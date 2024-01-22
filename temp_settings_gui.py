from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import xml.etree.ElementTree as ET
import qdarkstyle
from styles import dark_style, light_style
import sys
from db_control import DatabaseManager


class SettingsWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager

        self.initializeUI()

    def initializeUI(self):
        """Initializes the main UI components of the settings window."""
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 800, 500)
        self.setStyleSheet(qdarkstyle.load_stylesheet())

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.setupDatabasePathSetting(layout)
        self.setupStyleSelectionSetting(layout)
        self.setupSaveButton(layout)
        self.load_settings()

    def setupDatabasePathSetting(self, layout):
        """Sets up the database path setting in the UI."""
        db_path_layout = QHBoxLayout()
        self.db_path_label = QLabel("Database Path:")
        self.db_path_entry = QLineEdit()
        db_path_layout.addWidget(self.db_path_label)
        db_path_layout.addWidget(self.db_path_entry)
        layout.addLayout(db_path_layout)

    def setupStyleSelectionSetting(self, layout):
        """Sets up the style selection setting in the UI."""
        style_layout = QHBoxLayout()
        self.style_label = QLabel("Style Selection:")
        self.style_entry = QLineEdit()
        style_layout.addWidget(self.style_label)
        style_layout.addWidget(self.style_entry)
        layout.addLayout(style_layout)

    def setupSaveButton(self, layout):
        """Sets up the save button in the UI."""
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

    def load_settings(self):
        """Load settings from the XML file and update the UI."""
        try:
            tree = ET.parse('settings.xml')
            root = tree.getroot()
            db_path = root.find('database/path').text
            style_selection = root.find('style/selection').text
            self.db_path_entry.setText(db_path)
            self.style_entry.setText(style_selection)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading settings: {str(e)}")

    def save_settings(self):
        """Save the settings to the XML file."""
        try:
            tree = ET.parse('settings.xml')
            root = tree.getroot()
            root.find('database/path').text = self.db_path_entry.text()
            style_selection = self.style_entry.text()
            root.find('style/selection').text = style_selection
            tree.write('settings.xml')

            self.apply_style(style_selection)  # Apply the selected style

            QMessageBox.information(self, "Success", "Settings saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving settings: {str(e)}")

    def apply_style(self, style_name):
        """Apply the selected style to the application."""
        if style_name == "dark":
            self.setStyleSheet(dark_style)
        elif style_name == "light":
            self.setStyleSheet(light_style)
        else:
            self.setStyleSheet("")  # Default style

# Example usage
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    db_manager = DatabaseManager()  # Replace with your actual database manager
    settings_window = SettingsWindow(db_manager)
    settings_window.show()
    sys.exit(app.exec_())
