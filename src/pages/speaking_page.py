from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class SpeakingPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        title = QLabel("🎤 口语练习")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        layout.addWidget(title)

        desc = QLabel("跟读模仿、录音对比、发音评分")
        desc.setObjectName("descLabel")
        layout.addWidget(desc)

        layout.addSpacing(20)

        self._build_content_area(layout)

        layout.addStretch()

    def _build_content_area(self, parent_layout: QVBoxLayout):
        card = QWidget()
        card.setObjectName("contentCard")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(24, 20, 24, 20)
        card_lay.setSpacing(12)

        placeholder = QLabel("口语内容区域\n\n后续集成：录音采集、语音识别、发音评分等")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setObjectName("placeholder")
        card_lay.addWidget(placeholder)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        rec_btn = QPushButton("⏺  开始录音")
        rec_btn.setFixedSize(140, 40)
        rec_btn.setObjectName("primaryButton")
        btn_row.addWidget(rec_btn)
        btn_row.addStretch()
        card_lay.addLayout(btn_row)

        parent_layout.addWidget(card)
