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
#primaryButton:disabled {
    background-color: #94a3b8;
    color: #e2e8f0;
}

/* Secondary Button */
#secondaryButton {
    background-color: #e2e8f0;
    color: #1e293b;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: bold;
}
#secondaryButton:hover {
    background-color: #cbd5e1;
}
#secondaryButton:disabled {
    background-color: #f1f5f9;
    color: #94a3b8;
}

/* Select File Button */
#selectFileBtn {
    background-color: #f1f5f9;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    font-size: 14px;
    font-weight: bold;
}
#selectFileBtn:hover {
    background-color: #e2e8f0;
    border-color: #94a3b8;
}

/* Answer Toggle Button */
#answerToggleBtn {
    background-color: transparent;
    color: #3b82f6;
    border: 1px solid #3b82f6;
    border-radius: 8px;
    font-size: 13px;
}
#answerToggleBtn:hover {
    background-color: #eff6ff;
}

/* Speaker Tag */
#speakerTag {
    color: #6366f1;
    font-weight: bold;
    font-size: 13px;
}

/* Speech Text */
#speechText {
    font-size: 14px;
}

/* Option Text */
#optionText {
    font-size: 14px;
}

/* Question Label */
#questionLabel {
    font-size: 14px;
}

/* Answer Text */
#answerText {
    font-size: 13px;
}

/* Answer Scroll Area */
#answerScroll {
    border: none;
}

/* Audio Progress Bar */
#audioProgress {
    border-radius: 4px;
}
#audioProgress::chunk {
    background-color: #3b82f6;
    border-radius: 4px;
}

/* Progress Percent Label */
#progressPercent {
    font-size: 12px;
    font-weight: bold;
}

/* Pause Input */
#pauseInput {
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 13px;
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

/* Section GroupBox */
#sectionGroup {
    font-size: 15px;
    font-weight: bold;
    border-radius: 8px;
    padding: 16px 12px 12px 12px;
    margin-top: 12px;
}
#sectionGroup::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
}
"""

LIGHT_STYLESHEET = _BASE + """
QMainWindow { background-color: #ffffff; }

/* Sidebar */
#sidebar { background-color: #1e293b; }
#sidebarTitle { color: #ffffff; }
#sidebarSubtitle { color: #cbd5e1; font-size: 13px; }
#navButton { color: #ffffff; }
#navButton:hover { background-color: #334155; color: #ffffff; }
#themeToggleBtn { background-color: transparent; color: #f8fafc; }
#themeToggleBtn:hover { background-color: #334155; }

/* Main Content */
#pageTitle { color: #1e293b; }
#descLabel { color: #475569; font-size: 14px; }
#contentCard { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; }
#scrollViewport { background-color: #ffffff; }
#placeholder { color: #64748b; font-size: 15px; min-height: 180px; }

/* Listening Page */
#questionLabel { color: #1e293b; }
#speakerTag { color: #6366f1; }
#speechText { color: #334155; }
#optionText { color: #334155; }
#answerText { color: #1e293b; }
#answerScroll { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; }
#answerInner { background-color: #f8fafc; }
#answerSection { border-top: 1px dashed #cbd5e1; }
#selectFileBtn { background-color: #f1f5f9; color: #1e293b; border: 1px solid #cbd5e1; }
#selectFileBtn:hover { background-color: #e2e8f0; border-color: #94a3b8; }
#answerToggleBtn { color: #3b82f6; border: 1px solid #3b82f6; }
#answerToggleBtn:hover { background-color: #eff6ff; }
#secondaryButton { background-color: #e2e8f0; color: #1e293b; }
#secondaryButton:hover { background-color: #cbd5e1; }
#secondaryButton:disabled { background-color: #f1f5f9; color: #94a3b8; }
#audioProgress { background-color: #e2e8f0; border: 1px solid #cbd5e1; }
#audioProgress::chunk { background-color: #3b82f6; }
#progressPercent { color: #475569; }
#pauseInput { background-color: #f8fafc; color: #1e293b; border: 1px solid #94a3b8; }
#sectionGroup { border: 1px solid #e2e8f0; }
#sectionGroup::title { color: #1e293b; }


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
#pageTitle { color: #f1f5f9; }
#descLabel { color: #94a3b8; font-size: 14px; }
#contentCard { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; }
#scrollViewport { background-color: #1e293b; }
#placeholder { color: #64748b; font-size: 15px; min-height: 180px; }

/* Listening Page */
#questionLabel { color: #f1f5f9; }
#speakerTag { color: #a5b4fc; }
#speechText { color: #e2e8f0; }
#optionText { color: #e2e8f0; }
#answerText { color: #94a3b8; }
#answerScroll { background-color: #1e293b; border: 1px solid #334155; border-radius: 6px; }
#answerInner { background-color: #1e293b; }
#answerSection { border-top: 1px dashed #475569; }
#selectFileBtn { background-color: #334155; color: #e2e8f0; border: 1px solid #475569; }
#selectFileBtn:hover { background-color: #475569; border-color: #64748b; }
#answerToggleBtn { color: #60a5fa; border: 1px solid #60a5fa; }
#answerToggleBtn:hover { background-color: #1e3a5f; }
#secondaryButton { background-color: #334155; color: #e2e8f0; }
#secondaryButton:hover { background-color: #475569; }
#secondaryButton:disabled { background-color: #1e293b; color: #475569; }
#audioProgress { background-color: #334155; border: 1px solid #475569; }
#audioProgress::chunk { background-color: #3b82f6; }
#progressPercent { color: #94a3b8; }
#pauseInput { background-color: #0f172a; color: #e2e8f0; border: 1px solid #475569; }


/* Settings Dialog - Dark */
#settingsDialog { background-color: #1e293b; }
#settingsDialog QLabel { color: #e2e8f0; }
#settingsInput { background-color: #0f172a; color: #f1f5f9; border: 1px solid #334155; }
#settingsHint { color: #64748b; font-size: 12px; }
#settingsCancelBtn { background-color: #334155; color: #e2e8f0; border: none; border-radius: 8px; font-size: 14px; }
#settingsCancelBtn:hover { background-color: #475569; }
"""
