"""TTS 后台工作线程。

在 QThread 中运行 CosyVoice3 推理，避免阻塞 UI。
生成单个完整 WAV 文件。
"""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from utils.md_parser import parse_listening_md
from utils.tts_generator import TTSGenerator

logger = logging.getLogger(__name__)


class TTSWorker(QThread):
    """在后台线程中执行 MD 解析 + TTS 生成（单个 WAV 文件）。

    Signals
    -------
    progress : Signal(int, int)
        进度更新 ``(current, total)``。
    finished : Signal(bool, str)
        完成信号 ``(success, message_or_error)``。
    wav_ready : Signal(str)
        WAV 文件生成完成，传出文件路径。
    """

    progress = Signal(int, int)
    finished = Signal(bool, str)
    wav_ready = Signal(str)

    def __init__(
        self,
        md_file_path: str,
        output_path: str,
        pause_between_questions: float = 20.0,
        model_dir: str | None = None,
        cosyvoice_repo_dir: str | None = None,
        prompt_male_path: str | None = None,
        prompt_female_path: str | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self._md_file_path = md_file_path
        self._output_path = output_path
        self._pause_between_questions = pause_between_questions
        self._model_dir = model_dir
        self._cosyvoice_repo_dir = cosyvoice_repo_dir
        self._prompt_male_path = prompt_male_path
        self._prompt_female_path = prompt_female_path

    def run(self):
        try:
            # 1. 解析 MD 文件
            logger.info("解析 MD 文件: %s", self._md_file_path)
            doc = parse_listening_md(self._md_file_path)

            if not doc.questions:
                self.finished.emit(False, "MD 文件中没有找到题目内容")
                return

            logger.info(
                "解析完成: %s, %d 道题目", doc.title, len(doc.questions)
            )

            # 2. 创建 TTS 生成器
            project_root = Path(__file__).resolve().parent.parent.parent
            model_dir = self._model_dir or str(
                project_root / "models" / "CosyVoice-300M"
            )

            tts = TTSGenerator(
                model_dir=model_dir,
                cosyvoice_repo_dir=self._cosyvoice_repo_dir,
                prompt_male_path=self._prompt_male_path,
                prompt_female_path=self._prompt_female_path,
            )

            # 3. 生成单个 WAV 文件
            def on_progress(current: int, total: int):
                self.progress.emit(current, total)

            wav_path = tts.generate_single_wav(
                doc,
                self._output_path,
                pause_between_questions=self._pause_between_questions,
                progress_callback=on_progress,
            )

            self.wav_ready.emit(wav_path)
            self.finished.emit(True, f"音频已保存到: {wav_path}")

        except FileNotFoundError as e:
            logger.error("文件未找到: %s", e)
            self.finished.emit(False, f"文件未找到: {e}")
        except ImportError as e:
            logger.error("CosyVoice3 导入失败: %s", e)
            self.finished.emit(
                False,
                f"CosyVoice3 未安装或导入失败: {e}\n"
                "请运行 scripts/setup_tts.py 安装依赖。",
            )
        except Exception as e:
            logger.exception("TTS 生成失败")
            self.finished.emit(False, f"生成失败: {e}")
