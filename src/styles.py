from PySide6.QtCore import Signal, QObject


class ThemeManager(QObject):
    theme_changed = Signal(bool)

    def __init__(self):
        super().__init__()
        self._dark = False

    @property
    def is_dark(self) -> bool:
        return self._dark

    def toggle(self):
        self._dark = not self._dark
        self.theme_changed.emit(self._dark)

    def stylesheet(self) -> str:
        return DARK_STYLESHEET if self._dark else LIGHT_STYLESHEET


theme = ThemeManager()

_BASE = """
QWidget {
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    font-size: 14px;
}

/* Nav Buttons common */
#navButton {
    background-color: transparent;
    border: none;
    border-radius: 8px;
    text-align: left;
    padding-left: 16px;
    font-size: 15px;
}
#navButton:checked {
    background-color: #3b82f6;
    color: #ffffff;
    font-weight: bold;
}

/* Primary Button */
#primaryButton {
    background-color: #3b82f6;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: bold;
}
#primaryButton:hover {
    background-color: #2563eb;
}
#primaryButton:pressed {
    background-color: #1d4ed8;
}

/* Settings Input common */
#settingsInput {
    border-radius: 6px;
    padding: 8px 12px;
    min-width: 260px;
    selection-background-color: #3b82f6;
}
#settingsInput:focus {
    border-color: #3b82f6;
}

/* Theme toggle button */
#themeToggleBtn {
    border: none;
    border-radius: 6px;
    font-size: 18px;
    padding: 4px;
}
"""

LIGHT_STYLESHEET = _BASE + """
QMainWindow { background-color: #ffffff; }

/* Sidebar */
#sidebar { background-color: #1e293b; }
#sidebarTitle { color: #f8fafc; }
#sidebarSubtitle { color: #94a3b8; font-size: 13px; }
#navButton { color: #cbd5e1; }
#navButton:hover { background-color: #334155; color: #f1f5f9; }
#themeToggleBtn { background-color: transparent; color: #f8fafc; }
#themeToggleBtn:hover { background-color: #334155; }

/* Main Content */
#descLabel { color: #64748b; font-size: 14px; }
#contentCard { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; }
#placeholder { color: #94a3b8; font-size: 15px; min-height: 180px; }

/* Settings Dialog - Light */
#settingsDialog { background-color: #ffffff; }
#settingsDialog QLabel { color: #1e293b; }
#settingsInput { background-color: #ffffff; color: #1e293b; border: 1px solid #d1d5db; }
#settingsHint { color: #9ca3af; font-size: 12px; }
#settingsCancelBtn { background-color: #f3f4f6; color: #374151; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; }
#settingsCancelBtn:hover { background-color: #e5e7eb; }
"""

DARK_STYLESHEET = _BASE + """
QMainWindow { background-color: #0f172a; }

/* Sidebar */
#sidebar { background-color: #0f172a; }
#sidebarTitle { color: #f8fafc; }
#sidebarSubtitle { color: #64748b; font-size: 13px; }
#navButton { color: #94a3b8; }
#navButton:hover { background-color: #1e293b; color: #e2e8f0; }
#themeToggleBtn { background-color: transparent; color: #f8fafc; }
#themeToggleBtn:hover { background-color: #1e293b; }

/* Main Content */
#descLabel { color: #94a3b8; font-size: 14px; }
#contentCard { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; }
#placeholder { color: #64748b; font-size: 15px; min-height: 180px; }

/* Settings Dialog - Dark */
#settingsDialog { background-color: #1e293b; }
#settingsDialog QLabel { color: #e2e8f0; }
#settingsInput { background-color: #0f172a; color: #f1f5f9; border: 1px solid #334155; }
#settingsHint { color: #64748b; font-size: 12px; }
#settingsCancelBtn { background-color: #334155; color: #e2e8f0; border: none; border-radius: 8px; font-size: 14px; }
#settingsCancelBtn:hover { background-color: #475569; }
"""
