from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QLineEdit,
)

from utils.audio_utils import AudioPlayer
from utils.md_parser import ListeningDocument, parse_listening_md
from utils.tts_worker import TTSWorker


class ListeningPage(QWidget):
    def __init__(self):
        super().__init__()
        self._doc: ListeningDocument | None = None
        self._md_path: str = ""
        self._wav_path: str = ""
        self._player = AudioPlayer()
        self._worker: TTSWorker | None = None
        self._answer_visible = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        title = QLabel("🎧 听力练习")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # ── 第一块：生成音频 ────────────────────────────
        gen_group = QGroupBox("生成音频")
        gen_group.setObjectName("sectionGroup")
        gen_lay = QVBoxLayout(gen_group)
        gen_lay.setSpacing(10)

        # 选择 MD
        md_row = QHBoxLayout()
        md_row.setSpacing(8)
        self._select_md_btn = QPushButton("📂 选择 MD")
        self._select_md_btn.setFixedSize(120, 32)
        self._select_md_btn.setObjectName("selectFileBtn")
        self._select_md_btn.clicked.connect(self._on_select_md)
        md_row.addWidget(self._select_md_btn)
        self._md_label = QLabel("未选择")
        self._md_label.setObjectName("descLabel")
        md_row.addWidget(self._md_label, stretch=1)
        gen_lay.addLayout(md_row)

        # 间隔设置
        pause_row = QHBoxLayout()
        pause_row.setSpacing(8)
        lbl1 = QLabel("对话后间隔:")
        lbl1.setObjectName("descLabel")
        pause_row.addWidget(lbl1)
        self._pause1_input = QLineEdit("5")
        self._pause1_input.setFixedWidth(50)
        self._pause1_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._pause1_input.setObjectName("pauseInput")
        pause_row.addWidget(self._pause1_input)
        lbl2 = QLabel("秒")
        lbl2.setObjectName("descLabel")
        pause_row.addWidget(lbl2)
        pause_row.addSpacing(12)
        lbl3 = QLabel("念题后间隔:")
        lbl3.setObjectName("descLabel")
        pause_row.addWidget(lbl3)
        self._pause2_input = QLineEdit("10")
        self._pause2_input.setFixedWidth(50)
        self._pause2_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._pause2_input.setObjectName("pauseInput")
        pause_row.addWidget(self._pause2_input)
        lbl4 = QLabel("秒")
        lbl4.setObjectName("descLabel")
        pause_row.addWidget(lbl4)
        pause_row.addStretch()
        gen_lay.addLayout(pause_row)

        # 生成按钮 + 进度
        gen_btn_row = QHBoxLayout()
        gen_btn_row.setSpacing(10)
        self._gen_btn = QPushButton("🔊 生成音频")
        self._gen_btn.setFixedSize(120, 36)
        self._gen_btn.setObjectName("primaryButton")
        self._gen_btn.setEnabled(False)
        self._gen_btn.clicked.connect(self._on_generate)
        gen_btn_row.addWidget(self._gen_btn)
        self._progress = QProgressBar()
        self._progress.setFixedHeight(20)
        self._progress.setObjectName("audioProgress")
        self._progress.setValue(0)
        self._progress.setTextVisible(False)
        gen_btn_row.addWidget(self._progress, stretch=1)
        self._progress_label = QLabel("0%")
        self._progress_label.setFixedWidth(40)
        self._progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._progress_label.setObjectName("progressPercent")
        gen_btn_row.addWidget(self._progress_label)
        gen_lay.addLayout(gen_btn_row)

        # 结果路径
        self._result_label = QLabel("")
        self._result_label.setObjectName("descLabel")
        self._result_label.setWordWrap(True)
        gen_lay.addWidget(self._result_label)

        layout.addWidget(gen_group)

        # ── 第二块：播放与答案 ──────────────────────────
        play_group = QGroupBox("播放与答案")
        play_group.setObjectName("sectionGroup")
        play_lay = QVBoxLayout(play_group)
        play_lay.setSpacing(10)

        # 选择 WAV
        wav_row = QHBoxLayout()
        wav_row.setSpacing(8)
        self._select_wav_btn = QPushButton("📂 选择音频")
        self._select_wav_btn.setFixedSize(120, 32)
        self._select_wav_btn.setObjectName("selectFileBtn")
        self._select_wav_btn.clicked.connect(self._on_select_wav)
        wav_row.addWidget(self._select_wav_btn)
        self._wav_label = QLabel("未选择")
        self._wav_label.setObjectName("descLabel")
        wav_row.addWidget(self._wav_label, stretch=1)
        play_lay.addLayout(wav_row)

        # 播放控制
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(10)
        self._play_btn = QPushButton("▶ 播放")
        self._play_btn.setFixedSize(90, 32)
        self._play_btn.setObjectName("primaryButton")
        self._play_btn.setEnabled(False)
        self._play_btn.clicked.connect(self._on_play)
        ctrl_row.addWidget(self._play_btn)
        self._pause_btn = QPushButton("⏸ 暂停")
        self._pause_btn.setFixedSize(90, 32)
        self._pause_btn.setObjectName("secondaryButton")
        self._pause_btn.setEnabled(False)
        self._pause_btn.clicked.connect(self._on_pause)
        ctrl_row.addWidget(self._pause_btn)
        self._stop_btn = QPushButton("⏹ 停止")
        self._stop_btn.setFixedSize(90, 32)
        self._stop_btn.setObjectName("secondaryButton")
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self._on_stop)
        ctrl_row.addWidget(self._stop_btn)
        ctrl_row.addStretch()
        play_lay.addLayout(ctrl_row)

        # 答案按钮
        self._answer_btn = QPushButton("显示答案")
        self._answer_btn.setFixedHeight(32)
        self._answer_btn.setObjectName("answerToggleBtn")
        self._answer_btn.clicked.connect(self._on_toggle_answer)
        self._answer_btn.hide()
        play_lay.addWidget(self._answer_btn)

        # 答案区域
        self._answer_scroll = QScrollArea()
        self._answer_scroll.setObjectName("answerScroll")
        self._answer_scroll.setWidgetResizable(True)
        self._answer_scroll.setFixedHeight(120)
        self._answer_inner = QWidget()
        self._answer_inner.setObjectName("answerInner")
        self._answer_layout = QVBoxLayout(self._answer_inner)
        self._answer_layout.setContentsMargins(8, 8, 8, 8)
        self._answer_layout.setSpacing(4)
        self._answer_layout.addStretch()
        self._answer_scroll.setWidget(self._answer_inner)
        self._answer_scroll.hide()
        play_lay.addWidget(self._answer_scroll)

        layout.addWidget(play_group)
        layout.addStretch()

    # ── 选择 MD ────────────────────────────────────────

    def _on_select_md(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择 MD 文件", str(Path.cwd()), "Markdown 文件 (*.md)"
        )
        if not path:
            return
        try:
            doc = parse_listening_md(path)
        except Exception as e:
            self._md_label.setText(f"解析失败: {e}")
            return
        if not doc.questions:
            self._md_label.setText("无题目内容")
            return

        self._doc = doc
        self._md_path = path
        self._md_label.setText(Path(path).name)
        self._gen_btn.setEnabled(True)
        self._result_label.setText("")
        self._answer_btn.show()

        # 自动查找同名 wav
        md_name = Path(path).stem
        output_dir = Path(__file__).resolve().parent.parent.parent / "output" / "listening"
        alt_wav = output_dir / f"{md_name}.wav"
        if alt_wav.exists():
            self._wav_path = str(alt_wav)
            self._wav_label.setText(f"{alt_wav.name}（已找到）")
            self._play_btn.setEnabled(True)

    # ── 生成音频 ──────────────────────────────────────

    def _on_generate(self):
        if not self._doc or not self._md_path:
            return

        md_name = Path(self._md_path).stem
        output_dir = Path(__file__).resolve().parent.parent.parent / "output" / "listening"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / f"{md_name}.wav")

        self._gen_btn.setEnabled(False)
        self._gen_btn.setText("⏳ 生成中…")
        self._select_md_btn.setEnabled(False)
        self._progress.setValue(0)
        self._progress_label.setText("0%")

        self._worker = TTSWorker(
            md_file_path=self._md_path,
            output_path=output_path,
            pause_after_dialogue=self._get_pause(self._pause1_input, 5),
            pause_after_question=self._get_pause(self._pause2_input, 10),
        )
        self._worker.progress.connect(self._on_gen_progress)
        self._worker.finished.connect(self._on_gen_finished)
        self._worker.start()

    def _on_gen_progress(self, current: int, total: int):
        if total > 0:
            self._progress.setMaximum(total)
            self._progress.setValue(current)
            pct = int(current / total * 100)
            self._progress_label.setText(f"{pct}%")

    def _on_gen_finished(self, success: bool, message: str):
        self._gen_btn.setEnabled(True)
        self._gen_btn.setText("🔊 生成音频")
        self._select_md_btn.setEnabled(True)

        if not success:
            self._result_label.setText(f"❌ {message}")
        else:
            wav_path = message.replace("音频已保存到: ", "").strip()
            self._wav_path = wav_path
            self._result_label.setText(f"✅ {wav_path}")
            self._wav_label.setText(Path(wav_path).name)
            self._play_btn.setEnabled(True)

    # ── 选择 WAV ───────────────────────────────────────

    def _on_select_wav(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择音频文件", str(Path.cwd()), "音频文件 (*.wav *.mp3)"
        )
        if not path:
            return
        self._wav_path = path
        self._wav_label.setText(Path(path).name)
        self._play_btn.setEnabled(True)

    # ── 播放控制 ──────────────────────────────────────

    def _on_play(self):
        if self._wav_path:
            self._player.play(self._wav_path)
            self._pause_btn.setEnabled(True)
            self._stop_btn.setEnabled(True)

    def _on_pause(self):
        self._player.stop()
        self._pause_btn.setEnabled(False)

    def _on_stop(self):
        self._player.stop()
        self._pause_btn.setEnabled(False)
        self._stop_btn.setEnabled(False)

    # ── 答案 ──────────────────────────────────────────

    def _clear_answers(self):
        while self._answer_layout.count():
            item = self._answer_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._answer_layout.addStretch()

    def _on_toggle_answer(self):
        if not self._doc:
            return

        self._answer_visible = not self._answer_visible
        self._clear_answers()

        if self._answer_visible:
            questions = self._doc.questions
            batch = 5
            for start in range(0, len(questions), batch):
                group = questions[start:start + batch]
                first = group[0].index
                last = group[-1].index
                answers = "  ".join(q.answer or "?" for q in group)
                lbl = QLabel(f"{first}-{last}:  {answers}")
                lbl.setObjectName("answerText")
                self._answer_layout.insertWidget(self._answer_layout.count() - 1, lbl)
            self._answer_scroll.show()
            self._answer_btn.setText("隐藏答案")
        else:
            self._answer_scroll.hide()
            self._answer_btn.setText("显示答案")

    # ── 辅助 ──────────────────────────────────────────

    @staticmethod
    def _get_pause(input_widget: QLineEdit, default: int) -> int:
        try:
            val = int(input_widget.text().strip())
            return val if 1 <= val <= 120 else default
        except (ValueError, AttributeError):
            return default
