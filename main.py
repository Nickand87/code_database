import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QStackedWidget, QLabel, QSizeGrip, QStatusBar
from PyQt5.QtCore import Qt
from db_control import DatabaseManager
import xml.etree.ElementTree as ET
from styles import dark_style, light_style
from gui import ClientWindow
from temp_settings_gui import SettingsWindow
from special_classes import CustomTitleBar
import qdarkstyle


class MainWindow(QMainWindow):
    """Main window of the application."""
    def __init__(self, db_manager):
        super().__init__()
        self.setWindowTitle("Metrology Stuff")

        self.setWindowFlags(Qt.FramelessWindowHint)

        self.title_bar = CustomTitleBar(self)
        self.setMenuWidget(self.title_bar)

        self.setGeometry(100, 100, 800, 600)
        self.db_manager = db_manager
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI components."""
        main_layout = QHBoxLayout()

        # Sidebar setup
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_widget.setFixedWidth(100)  # Fixed width for the sidebar

        # Create a status bar
        self.status_bar = QStatusBar()
        #self.status_bar.setFixedHeight(30)
        self.setStatusBar(self.status_bar)

        # Initialize buttons and add them to the sidebar layout
        self.button1 = QPushButton("Clients")
        self.button1.setMinimumHeight(25)
        self.button1.clicked.connect(lambda: self.switch_page(0))
        sidebar_layout.addWidget(self.button1)

        # Add stretch to push subsequent widgets to the bottom
        sidebar_layout.addStretch(50)

        self.button2 = QPushButton("Settings")
        self.button2.setMinimumHeight(50)
        self.button2.clicked.connect(lambda: self.switch_page(1))
        sidebar_layout.addWidget(self.button2)

        sidebar_layout.addStretch()  # Add stretch to push all widgets up

        # Stacked widget for central area
        self.stacked_widget = QStackedWidget()

        # Example of adding pages to the stacked widget
        self.stacked_widget.addWidget(ClientWindow(self.db_manager))  # Assuming ClientWindow is a QWidget
        self.stacked_widget.addWidget(SettingsWindow(self.db_manager))  # Assuming SettingsWindow is a QWidget

        # Add sidebar and stacked widget to the main layout
        main_layout.addWidget(sidebar_widget)  # Sidebar
        main_layout.addWidget(self.stacked_widget)  # Stacked widget for pages

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def switch_page(self, page_index):
        """Switch between pages in the stacked widget."""
        self.stacked_widget.setCurrentIndex(page_index)


def read_style_setting():
    """Read the style setting from settings.xml."""
    try:
        tree = ET.parse('settings.xml')
        root = tree.getroot()
        return root.find('style/selection').text
    except Exception:
        return None  # Return None if the setting is not found


def apply_style(app, style_name):
    """Apply the selected style to the application."""
    if style_name == "dark":
        app.setStyleSheet(dark_style())
    elif style_name == "light":
        app.setStyleSheet(light_style())
    else:
        app.setStyleSheet("")  # Apply default style if the name is not recognized


def main():
    app = QApplication(sys.argv)

    style_setting = read_style_setting()
    apply_style(app, style_setting)

    db_manager = DatabaseManager()  # Database initialization now inside DatabaseManager

    mainWin = MainWindow(db_manager)
    mainWin.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
