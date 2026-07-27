from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from utils.settings import Settings


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setFixedSize(480, 320)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setObjectName("settingsDialog")

        settings = Settings()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(16)

        title = QLabel("⚙  大模型配置")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.api_url_input = QLineEdit(settings.api_url)
        self.api_url_input.setPlaceholderText("https://api.openai.com/v1")
        self.api_url_input.setObjectName("settingsInput")
        form.addRow("API 网址：", self.api_url_input)

        self.api_key_input = QLineEdit(settings.api_key)
        self.api_key_input.setPlaceholderText("sk-...")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setObjectName("settingsInput")
        form.addRow("API Key：", self.api_key_input)

        self.model_input = QLineEdit(settings.model_name)
        self.model_input.setPlaceholderText("gpt-4o")
        self.model_input.setObjectName("settingsInput")
        form.addRow("模型名称：", self.model_input)

        layout.addLayout(form)

        hint = QLabel("配置保存在 ~/.ept/settings.json")
        hint.setObjectName("settingsHint")
        layout.addWidget(hint)

        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(90, 36)
        cancel_btn.setObjectName("settingsCancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("保存")
        save_btn.setFixedSize(90, 36)
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)

    def _save(self):
        Settings().update(
            api_key=self.api_key_input.text().strip(),
            api_url=self.api_url_input.text().strip(),
            model_name=self.model_input.text().strip(),
        )
        self.accept()
