"""CosyVoice3 TTS 生成器。

封装 CosyVoice3 的推理调用，支持：
- 懒加载模型（首次调用时初始化）
- 男/女说话人映射到不同的参考音频
- 对话音频拼接（多条语音 + 静音间隔）
- 按题目生成 WAV 文件
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Callable

from utils.md_parser import ListeningDocument, Question, SpeechLine

logger = logging.getLogger(__name__)

# CosyVoice3 推理的默认 prompt 文本
DEFAULT_PROMPT_TEXT = "You are a helpful assistant.<|endofprompt|>希望你以后能够做的比我还好呦。"

# 对话轮次之间的静音时长（秒）
DIALOGUE_SILENCE_SEC = 0.5

# 题目之间的静音时长（秒）
QUESTION_GAP_SEC = 2.0


class TTSGenerator:
    """CosyVoice3 TTS 生成器（懒加载）。"""

    def __init__(
        self,
        model_dir: str | Path,
        cosyvoice_repo_dir: str | Path | None = None,
        prompt_male_path: str | Path | None = None,
        prompt_female_path: str | Path | None = None,
    ):
        self._model_dir = str(Path(model_dir).resolve())
        self._repo_dir = self._resolve_repo_dir(cosyvoice_repo_dir)
        self._cosyvoice = None
        self._sample_rate = 24000
        self._torch = None
        self._torchaudio = None

        project_root = Path(__file__).resolve().parent.parent.parent
        default_voice_dir = project_root / "assets" / "voices"
        self._prompt_paths: dict[str, str] = {
            "M": str(prompt_male_path or default_voice_dir / "male_default.wav"),
            "F": str(prompt_female_path or default_voice_dir / "female_default.wav"),
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

        logger.info("正在加载 CosyVoice3 模型: %s", self._model_dir)
        self._cosyvoice = AutoModel(model_dir=self._model_dir)
        self._sample_rate = self._cosyvoice.sample_rate
        logger.info("CosyVoice3 模型加载完成，采样率: %d", self._sample_rate)

    def generate_speech(
        self,
        text: str,
        speaker: str,
        prompt_text: str = DEFAULT_PROMPT_TEXT,
    ) -> "torch.Tensor":
        """为单条文本生成语音。"""
        self._ensure_model()
        torch = self._torch

        prompt_wav = self._prompt_paths.get(speaker)
        if not prompt_wav or not Path(prompt_wav).exists():
            raise FileNotFoundError(
                f"说话人 '{speaker}' 的参考音频不存在: {prompt_wav}"
            )

        logger.debug("生成语音: [%s] %s", speaker, text[:50])

        chunks = []
        for result in self._cosyvoice.inference_zero_shot(
            text, prompt_text, prompt_wav, stream=False
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

    # ── 单文件生成（所有题目对话拼为一个 WAV）─────────

    def generate_single_wav(
        self,
        doc: ListeningDocument,
        output_path: str | Path,
        pause_after_dialogue: float = 5.0,
        pause_after_question: float = 10.0,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> str:
        """将整份文档的所有题目对话拼接为一个完整 WAV 文件。

        每题结构：对话 → pause_after_dialogue 静音 → 念问题文本+选项
                 → pause_after_question 静音 → 下一题

        Parameters
        ----------
        doc : ListeningDocument
            文档数据。
        output_path : str | Path
            输出 WAV 文件路径。
        pause_after_dialogue : float
            对话结束后到念问题的间隔秒数，默认 5。
        pause_after_question : float
            念完问题后到下一题的间隔秒数，默认 10。
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

            # 1. 对话音频
            wav = self._generate_dialogue(question.dialogue_lines)
            all_wavs.append(wav)

            # 2. 对话后 → 念问题 的静音
            all_wavs.append(self._generate_silence(pause_after_dialogue))

            # 3. 念问题文本 + 选项（用默认女声）
            if question.question_text:
                q_wav = self.generate_speech(question.question_text, "F")
                all_wavs.append(q_wav)
            for opt in question.options:
                opt_wav = self.generate_speech(opt, "F")
                all_wavs.append(opt_wav)
                all_wavs.append(self._generate_silence(0.3))

            # 4. 念完问题后 → 下一题 的静音
            all_wavs.append(self._generate_silence(pause_after_question))

            if progress_callback:
                progress_callback(i + 1, total)

        # 去掉最后一个多余的尾部静音
        if all_wavs:
            all_wavs.pop()

        full_wav = torch.cat(all_wavs, dim=1)
        self.save_wav(full_wav, output_path)

        return str(output_path)

    # ── 内部方法 ──────────────────────────────────────

    def _generate_dialogue(self, lines: list[SpeechLine]) -> "torch.Tensor":
        """为一组 SpeechLine 生成拼接音频。"""
        if not lines:
            return self._generate_silence(0.1)

        wavs: list["torch.Tensor"] = []
        total_lines = len(lines)

        for i, line in enumerate(lines):
            wav = self.generate_speech(line.text, line.speaker)
            wavs.append(wav)

            if i < total_lines - 1:
                wavs.append(self._generate_silence(DIALOGUE_SILENCE_SEC))

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
