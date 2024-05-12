from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSignal
import xml.etree.ElementTree as ET
from styles import apply_style
import sys


class SettingsWindow(QMainWindow):
    settingsChanged = pyqtSignal()

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.db_path_entry = None
        self.style_entry = None
        self.save_button = None
        self.initializeUI()

    def initializeUI(self):
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 800, 500)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        self.setupDatabasePathSetting(layout)
        self.setupStyleSelectionSetting(layout)
        self.setupSaveButton(layout)
        self.load_settings()

    def setupDatabasePathSetting(self, layout):
        db_path_layout = QHBoxLayout()
        db_path_label = QLabel("Database Path:")
        self.db_path_entry = QLineEdit()
        db_path_layout.addWidget(db_path_label)
        db_path_layout.addWidget(self.db_path_entry)
        layout.addLayout(db_path_layout)

    def setupStyleSelectionSetting(self, layout):
        style_layout = QHBoxLayout()
        style_label = QLabel("Style Selection:")
        self.style_entry = QLineEdit()
        style_layout.addWidget(style_label)
        style_layout.addWidget(self.style_entry)
        layout.addLayout(style_layout)

    def setupSaveButton(self, layout):
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

    def load_settings(self):
        try:
            tree = ET.parse('settings.xml')
            root = tree.getroot()
            db_path = root.find('database/path').text
            style_selection = root.find('style/selection').text
            self.db_path_entry.setText(db_path)
            self.style_entry.setText(style_selection)
        except (FileNotFoundError, ET.ParseError, AttributeError):
            QMessageBox.warning(self, "Warning", "Failed to load settings. Using default values.")

    def save_settings(self):
        try:
            tree = ET.parse('settings.xml')
            root = tree.getroot()
            root.find('database/path').text = self.db_path_entry.text()
            style_selection = self.style_entry.text()
            root.find('style/selection').text = style_selection
            tree.write('settings.xml')
            apply_style(self, style_selection)
            QMessageBox.information(self, "Success", "Settings saved successfully.")
            self.settingsChanged.emit()
        except (FileNotFoundError, ET.ParseError, AttributeError):
            QMessageBox.critical(self, "Error", "Failed to save settings.")
