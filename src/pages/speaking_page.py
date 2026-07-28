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
        title.setObjectName("pageTitle")
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

        placeholder = QLabel("🚧 功能开发中，敬请期待…")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setObjectName("placeholder")
        card_lay.addWidget(placeholder)

        parent_layout.addWidget(card)
