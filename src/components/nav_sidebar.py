from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from styles import theme


class NavButton(QPushButton):
    def __init__(self, text: str, index: int):
        super().__init__(text)
        self.index = index
        self.setCheckable(True)
        self.setFixedHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("navButton")


class NavSidebar(QWidget):
    page_changed = Signal(int)
    settings_requested = Signal()

    PAGES = [
        ("🎧  听力练习", 0),
        ("🎤  口语练习", 1),
    ]

    def __init__(self):
        super().__init__()
        self.setFixedWidth(200)
        self.setObjectName("sidebar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(8)

        title = QLabel("EPT")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("sidebarTitle")
        layout.addWidget(title)

        subtitle = QLabel("英语练习工具")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setObjectName("sidebarSubtitle")
        layout.addWidget(subtitle)

        layout.addSpacing(24)

        self.buttons: list[NavButton] = []
        for label, idx in self.PAGES:
            btn = NavButton(label, idx)
            btn.clicked.connect(lambda checked, i=idx: self._on_click(i))
            self.buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(4)

        settings_btn = QPushButton("⚙  设置")
        settings_btn.setObjectName("navButton")
        settings_btn.setFixedHeight(36)
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.clicked.connect(self.settings_requested.emit)
        bottom_row.addWidget(settings_btn)

        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setObjectName("themeToggleBtn")
        self.theme_btn.setFixedSize(36, 36)
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.clicked.connect(self._toggle_theme)
        bottom_row.addWidget(self.theme_btn)

        layout.addLayout(bottom_row)

        self.buttons[0].setChecked(True)

    def _toggle_theme(self):
        theme.toggle()
        self.theme_btn.setText("☀️" if theme.is_dark else "🌙")

    def _on_click(self, index: int):
        for btn in self.buttons:
            btn.setChecked(btn.index == index)
        self.page_changed.emit(index)
