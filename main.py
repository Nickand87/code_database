import sys
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QStackedWidget, QStatusBar
from PyQt5.QtCore import Qt
from db_control import DatabaseManager
import xml.etree.ElementTree as ET
from styles import apply_style, get_dark_style, get_light_style
from gui import ClientWindow
from settings_gui import SettingsWindow
from special_classes import CustomTitleBar


class MainWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.setWindowTitle("Fools")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.title_bar = CustomTitleBar(self)
        self.setMenuWidget(self.title_bar)
        self.setGeometry(100, 100, 900, 600)
        self.db_manager = db_manager
        self.settings_window = None
        self.apply_style_settings()
        self.setup_ui()

    def apply_style_settings(self):
        style_setting = self.read_style_setting()
        apply_style(self, style_setting)

    def read_style_setting(self):
        try:
            tree = ET.parse('settings.xml')
            root = tree.getroot()
            return root.find('style/selection').text
        except Exception:
            return None

    def setup_ui(self):
        main_layout = QHBoxLayout()

        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_widget.setFixedWidth(100)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.button1 = QPushButton("Product Codes")
        self.button1.setMinimumHeight(25)
        self.button1.clicked.connect(lambda: self.switch_page(0))
        sidebar_layout.addWidget(self.button1)

        sidebar_layout.addStretch(50)

        self.button2 = QPushButton("Settings")
        self.button2.setMinimumHeight(50)
        self.button2.clicked.connect(lambda: self.switch_page(1))
        sidebar_layout.addWidget(self.button2)

        sidebar_layout.addStretch()

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(ClientWindow(self.db_manager))
        self.settings_window = SettingsWindow(self.db_manager)
        self.settings_window.settingsChanged.connect(self.reinitialize_app)
        self.stacked_widget.addWidget(self.settings_window)

        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(self.stacked_widget)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def reinitialize_app(self):
        current_page_index = self.stacked_widget.currentIndex()
        self.close()
        new_main_window = MainWindow(self.db_manager)
        if current_page_index == 1:
            new_main_window.switch_page(1)
        new_main_window.show()

    def switch_page(self, page_index):
        if page_index == 1:
            self.stacked_widget.setCurrentWidget(self.settings_window)
        else:
            self.stacked_widget.setCurrentIndex(page_index)


def main():
    # Configure logging
    logging.basicConfig(filename='log.txt', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    app = QApplication(sys.argv)
    db_manager = DatabaseManager()
    mainWin = MainWindow(db_manager)
    mainWin.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()