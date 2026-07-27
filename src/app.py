from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from components.nav_sidebar import NavSidebar
from pages.listening_page import ListeningPage
from pages.speaking_page import SpeakingPage
from styles import STYLESHEET


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("English Practice Tool")
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = NavSidebar()
        self.stack = QStackedWidget()

        self.listening_page = ListeningPage()
        self.speaking_page = SpeakingPage()

        self.stack.addWidget(self.listening_page)
        self.stack.addWidget(self.speaking_page)

        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack, stretch=1)

        self.sidebar.page_changed.connect(self._switch_page)

        self.setStyleSheet(STYLESHEET)

    def _switch_page(self, index: int):
        self.stack.setCurrentIndex(index)
