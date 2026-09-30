"""CosyVoice3 TTS 生成器。

封装 CosyVoice3 的推理调用，支持：
- 懒加载模型（首次调用时初始化）
- 男/女说话人映射到不同的参考音频
- 同说话人连续行合并（减少推理调用次数）
- 长文本按句拆分（避免模型截断）
- 对话音频拼接（多条语音 + 静音间隔）
- 按题目生成 WAV 文件
"""

from __future__ import annotations

import logging
import re
import sys
from pathlib import Path
from typing import Callable

from utils.md_parser import ListeningDocument, Question, SpeechLine

logger = logging.getLogger(__name__)

# CosyVoice3 推理的 prompt 前缀（instruct 段，置于 <|endofprompt|> 之前）
PROMPT_INSTRUCT = "You are a helpful assistant."

# 默认参考音频转写（必须与 assets/voices/ 下对应 wav 的实际口播内容一字不差，
# 否则 zero-shot 音色克隆会串味到中文 / 把 prompt 转写念进输出 / 截断吞字）。
# 参考音频已裁短到 4-5 秒以降低 prompt 泄漏；换参考音频时务必同步更新这里。
DEFAULT_PROMPT_TEXT_MALE = (
    "Listening Test. In the listening test, you will be asked to demonstrate"
)
DEFAULT_PROMPT_TEXT_FEMALE = (
    "We're happy to see you all at this seminar this afternoon."
)


def _build_prompt_text(transcript: str, use_endofprompt: bool) -> str:
    """组装 zero-shot 的 prompt_text。

    CosyVoice3 需要 ``instruct<|endofprompt|>转写`` 格式；
    CosyVoice v1/v2 不用 <|endofprompt|>，prompt_text 就是裸转写。
    """
    if use_endofprompt:
        return f"{PROMPT_INSTRUCT}<|endofprompt|>{transcript}"
    return transcript


def _is_cosyvoice3(model_dir: str | Path) -> bool:
    """根据模型目录里的 yaml 判断是否为 CosyVoice3。"""
    return Path(model_dir, "cosyvoice3.yaml").exists()

# 对话轮次之间的静音时长（秒）
DIALOGUE_SILENCE_SEC = 0.5

# 题目之间的静音时长（秒）
QUESTION_GAP_SEC = 2.0

# 单次推理文本最大长度（超过则按句拆分）
MAX_TEXT_LEN = 100


class TTSGenerator:
    """CosyVoice3 TTS 生成器（懒加载）。"""

    def __init__(
        self,
        model_dir: str | Path,
        cosyvoice_repo_dir: str | Path | None = None,
        prompt_male_path: str | Path | None = None,
        prompt_female_path: str | Path | None = None,
        prompt_male_text: str | None = None,
        prompt_female_text: str | None = None,
        fp16: bool = True,
        flow_ode_steps: int | None = 6,
    ):
        self._model_dir = str(Path(model_dir).resolve())
        self._repo_dir = self._resolve_repo_dir(cosyvoice_repo_dir)
        self._cosyvoice = None
        self._sample_rate = 24000
        self._torch = None
        self._torchaudio = None
        self._fp16 = fp16
        # flow matching 的 ODE 步数（原默认 10）；越小越快，质量略降
        self._flow_ode_steps = flow_ode_steps
        # 已注册到 CosyVoice 缓存里的说话人集合（add_zero_shot_spk）
        self._registered_spk: set[str] = set()

        project_root = Path(__file__).resolve().parent.parent.parent
        default_voice_dir = project_root / "assets" / "voices"
        self._prompt_paths: dict[str, str] = {
            "M": str(prompt_male_path or default_voice_dir / "male_default.wav"),
            "F": str(prompt_female_path or default_voice_dir / "female_default.wav"),
        }
        # 每个说话人的 prompt_text 必须与其参考音频的口播内容一致
        # CosyVoice3 需要 <|endofprompt|> 前缀，v1/v2 只要裸转写
        use_eop = _is_cosyvoice3(self._model_dir)
        self._prompt_texts: dict[str, str] = {
            "M": _build_prompt_text(prompt_male_text or DEFAULT_PROMPT_TEXT_MALE, use_eop),
            "F": _build_prompt_text(prompt_female_text or DEFAULT_PROMPT_TEXT_FEMALE, use_eop),
        }

    @property
    def sample_rate(self) -> int:
        return self._sample_rate

    # ── 可用性检查 ────────────────────────────────────

    def is_available(self) -> bool:
        """检查 CosyVoice3 是否可导入（不加载模型）。"""
        try:
            repo_dir = self._repo_dir
            if not repo_dir or not Path(repo_dir).exists():
                return False
            matcha_path = str(Path(repo_dir) / "third_party" / "Matcha-TTS")
            paths_to_add = [repo_dir, matcha_path]
            original_path = sys.path[:]
            for p in paths_to_add:
                if p not in sys.path:
                    sys.path.insert(0, p)
            try:
                import cosyvoice.cli.cosyvoice  # noqa: F401
                return True
            except ImportError:
                return False
            finally:
                sys.path[:] = original_path
        except Exception:
            return False

    # ── 核心推理 ──────────────────────────────────────

    def _ensure_model(self):
        """确保模型已加载（首次调用时初始化）。"""
        if self._cosyvoice is not None:
            return

        repo_dir = self._repo_dir
        matcha_path = str(Path(repo_dir) / "third_party" / "Matcha-TTS")
        for p in [matcha_path, repo_dir]:
            if p not in sys.path:
                sys.path.insert(0, p)

        import torch
        import torchaudio
        from cosyvoice.cli.cosyvoice import AutoModel

        self._torch = torch
        self._torchaudio = torchaudio

        logger.info("正在加载 CosyVoice3 模型: %s (fp16=%s)", self._model_dir, self._fp16)
        self._cosyvoice = AutoModel(model_dir=self._model_dir, fp16=self._fp16)
        self._sample_rate = self._cosyvoice.sample_rate
        logger.info("CosyVoice3 模型加载完成，采样率: %d", self._sample_rate)

        # 降低 flow matching 的 ODE 步数以加速声码器（瓶颈在 flow，不在 LLM）
        if self._flow_ode_steps is not None:
            decoder = self._cosyvoice.model.flow.decoder
            orig_forward = decoder.forward

            def patched_forward(*args, **kwargs):
                kwargs["n_timesteps"] = self._flow_ode_steps
                return orig_forward(*args, **kwargs)

            decoder.forward = patched_forward
            logger.info("flow ODE 步数: %d", self._flow_ode_steps)

        # 预注册男/女说话人，把 prompt 的语音 token/feat/embedding 缓存起来，
        # 之后推理走 zero_shot_spk_id 路径，避免每次都重算 prompt 特征
        for spk in ("M", "F"):
            wav = self._prompt_paths.get(spk)
            ptext = self._prompt_texts.get(spk)
            if wav and Path(wav).exists() and ptext:
                try:
                    self._cosyvoice.add_zero_shot_spk(ptext, wav, spk)
                    self._registered_spk.add(spk)
                    logger.info("已缓存说话人 %s 的 prompt 特征", spk)
                except Exception:
                    logger.exception("注册说话人 %s 失败，将退回逐次提取", spk)

    def generate_speech(
        self,
        text: str,
        speaker: str,
        prompt_text: str | None = None,
    ) -> "torch.Tensor":
        """为单条文本生成语音。"""
        self._ensure_model()
        torch = self._torch

        prompt_wav = self._prompt_paths.get(speaker)
        if not prompt_wav or not Path(prompt_wav).exists():
            raise FileNotFoundError(
                f"说话人 '{speaker}' 的参考音频不存在: {prompt_wav}"
            )
        # 未显式指定 prompt_text 时，按说话人取与参考音频匹配的转写
        use_cached_spk = False
        if prompt_text is None:
            prompt_text = self._prompt_texts.get(speaker)
            if not prompt_text:
                raise ValueError(f"说话人 '{speaker}' 缺少 prompt_text")
            # 走预注册缓存路径，跳过逐次 prompt 特征提取
            use_cached_spk = speaker in self._registered_spk

        logger.debug("生成语音: [%s] %s", speaker, text[:50])

        spk_id = speaker if use_cached_spk else ""
        chunks = []
        for result in self._cosyvoice.inference_zero_shot(
            text, prompt_text, prompt_wav, zero_shot_spk_id=spk_id, stream=False
        ):
            chunks.append(result["tts_speech"])

        if not chunks:
            raise RuntimeError(f"CosyVoice3 推理返回空结果: {text[:50]}")

        if len(chunks) == 1:
            return chunks[0]
        return torch.cat(chunks, dim=1)

    def save_wav(self, waveform: "torch.Tensor", filepath: str | Path):
        """将波形张量保存为 WAV 文件。"""
        self._ensure_model()
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        self._torchaudio.save(str(filepath), waveform, self._sample_rate)
        logger.info("已保存: %s", filepath)

    # ── 静音生成 ──────────────────────────────────────

    def _generate_silence(self, duration_sec: float) -> "torch.Tensor":
        """生成静音张量。"""
        self._ensure_model()
        num_samples = int(self._sample_rate * duration_sec)
        return self._torch.zeros(1, num_samples)

    # ── 文本拆分 ──────────────────────────────────────

    @staticmethod
    def _split_text(text: str, max_len: int = MAX_TEXT_LEN) -> list[str]:
        """将长文本按句子边界拆分为适合 TTS 推理的小段。

        短文本（≤ max_len）直接返回；长文本先按句号/问号/感叹号
        拆分，再将相邻短句合并至不超过 max_len。
        """
        if len(text) <= max_len:
            return [text]

        # 按句子边界拆分，保留标点
        sentences = re.split(r"(?<=[.!?])\s+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # 将相邻短句合并，总长不超过 max_len
        chunks: list[str] = []
        current = ""
        for sent in sentences:
            if not current:
                current = sent
            elif len(current) + 1 + len(sent) <= max_len:
                current += " " + sent
            else:
                chunks.append(current)
                current = sent
        if current:
            chunks.append(current)

        return chunks if chunks else [text]

    # ── 单文件生成（所有题目对话拼为一个 WAV）─────────

    def generate_single_wav(
        self,
        doc: ListeningDocument,
        output_path: str | Path,
        pause_between_questions: float = 20.0,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> str:
        """将整份文档的所有题目对话拼接为一个完整 WAV 文件。

        每题结构：
        0. 念 "Question N."（女声旁白，报题号）
        1. 对话/独白正文（男女声交替，同说话人连续行合并）
        2. pause_between_questions 静音（最后一题不加）

        Parameters
        ----------
        doc : ListeningDocument
            文档数据。
        output_path : str | Path
            输出 WAV 文件路径。
        pause_between_questions : float
            题目之间的静音间隔秒数，默认 20。
        progress_callback : callable, optional
            进度回调 ``callback(current, total)``。

        Returns
        -------
        str
            生成的 WAV 文件路径。
        """
        self._ensure_model()
        torch = self._torch

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        total = len(doc.questions)
        all_wavs: list["torch.Tensor"] = []

        for i, question in enumerate(doc.questions):
            logger.info("生成题目 %d/%d ...", i + 1, total)

            # 0. 报题号（女声旁白）——对话前先念一句第几题
            all_wavs.append(self.generate_speech(f"Question {question.index}.", "F"))
            all_wavs.append(self._generate_silence(0.5))

            # 1. 对话/独白正文（同说话人连续行合并）
            all_wavs.append(self._generate_dialogue(question.dialogue_lines))

            # 2. 题目之间的静音（最后一题不加）
            if i < total - 1:
                all_wavs.append(self._generate_silence(pause_between_questions))

            if progress_callback:
                progress_callback(i + 1, total)

        full_wav = torch.cat(all_wavs, dim=1)
        self.save_wav(full_wav, output_path)

        return str(output_path)

    # ── 内部方法 ──────────────────────────────────────

    def _generate_dialogue(self, lines: list[SpeechLine]) -> "torch.Tensor":
        """为一组 SpeechLine 生成拼接音频。

        同说话人的连续行合并为一次推理调用以提升速度；
        说话人切换处插入静音间隔。
        """
        if not lines:
            return self._generate_silence(0.1)

        # 按说话人分组：连续同一说话人的行合并为一组
        groups: list[tuple[str, list[str]]] = []
        for line in lines:
            if groups and groups[-1][0] == line.speaker:
                groups[-1][1].append(line.text)
            else:
                groups.append((line.speaker, [line.text]))

        wavs: list["torch.Tensor"] = []
        for speaker, texts in groups:
            merged = " ".join(texts)
            chunks = self._split_text(merged)
            for chunk in chunks:
                wavs.append(self.generate_speech(chunk, speaker))

            # 说话人切换时插入静音
            wavs.append(self._generate_silence(DIALOGUE_SILENCE_SEC))

        # 去掉最后一组多余的静音
        if wavs:
            wavs.pop()

        if len(wavs) == 1:
            return wavs[0]
        return self._torch.cat(wavs, dim=1)

    @staticmethod
    def _resolve_repo_dir(repo_dir: str | Path | None) -> str:
        """解析 CosyVoice 仓库目录。"""
        if repo_dir:
            return str(Path(repo_dir).resolve())

        project_root = Path(__file__).resolve().parent.parent.parent
        candidates = [
            project_root / "third_party" / "CosyVoice",
            project_root / "CosyVoice",
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)

        return str(candidates[0])
