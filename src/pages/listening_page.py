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


class ListeningPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        title = QLabel("🎧 听力练习")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        layout.addWidget(title)

        desc = QLabel("选择听力材料，播放音频，完成听写或选择练习")
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

        placeholder = QLabel("听力内容区域\n\n后续集成：音频播放、听写输入、进度追踪等")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setObjectName("placeholder")
        card_lay.addWidget(placeholder)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        play_btn = QPushButton("▶  播放音频")
        play_btn.setFixedSize(140, 40)
        play_btn.setObjectName("primaryButton")
        btn_row.addWidget(play_btn)
        btn_row.addStretch()
        card_lay.addLayout(btn_row)

        parent_layout.addWidget(card)
