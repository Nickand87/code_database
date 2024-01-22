
# PyQt5 imports
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QListWidget, QFormLayout,
                             QFrame, QMessageBox, QComboBox, QInputDialog, QApplication)
from PyQt5.QtGui import QFont, QIntValidator, QRegExpValidator
from PyQt5.QtCore import QRegExp

# Local application imports
from special_classes import EnterLineEdit


class ClickableLineEdit(QLineEdit):
    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        QApplication.clipboard().setText(self.text())


class ClientWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager

        # Initialize all instance attributes
        self.game_name_entry = None
        self.game_product_code_entry = None
        self.product_code_type_entry = None
        self.use_status_entry = None
        self.submit_button = None
        self.load_button = None
        self.delete_button = None
        self.clear_button = None
        self.game_code_list = None
        self.code_search_bar = None

        self.initializeUI()
        self.search_game_codes("")

    def initializeUI(self):
        """Initializes the main UI components of the window."""
        self.setWindowTitle("Game Code Management")
        self.setGeometry(100, 100, 800, 500)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        self.setupInputFields(main_layout)
        self.setupButtons(main_layout)
        self.setupGameCodeList(main_layout)

    def setupInputFields(self, layout):
        """Sets up input fields for client and contact information."""
        input_layout = QHBoxLayout()
        layout.addLayout(input_layout)

        self.setupProductInfo(input_layout)

    def setupProductInfo(self, layout):
        """Sets up client information input fields."""
        product_frame = QFrame()
        product_frame.setFrameShape(QFrame.StyledPanel)
        product_layout = QFormLayout(product_frame)
        layout.addWidget(product_frame)

        font = QFont("Arial", 12)
        label_font = QFont("Arial", 10, QFont.Bold)

        product_title = QLabel("Game Code")
        product_title.setFont(label_font)
        product_layout.addRow(product_title)

        self.game_name_entry = EnterLineEdit()
        self.game_product_code_entry = EnterLineEdit()
        self.product_code_type_entry = QComboBox()
        self.use_status_entry = QComboBox()

        # Combobox options
        self.product_code_type_entry.addItems(["Full Product", "Expansion/Addon"])
        self.use_status_entry.addItems((["Available", "Used"]))

        for label_text, widget in [
            ("Product Name:", self.game_name_entry),
            ("Product Code:", self.game_product_code_entry),
            ("Product Code Type:", self.product_code_type_entry),
            ("Status:", self.use_status_entry),
        ]:
            label = QLabel(label_text)
            label.setFont(label_font)
            widget.setFont(font)
            product_layout.addRow(label, widget)

    def setupButtons(self, layout):
        """Sets up buttons in the UI."""
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        font = QFont("Arial", 12)

        self.submit_button = QPushButton("Submit Code")
        self.load_button = QPushButton("Load Code")
        self.delete_button = QPushButton("Delete Code")
        self.clear_button = QPushButton("Clear Fields")

        self.submit_button.setFont(font)
        self.load_button.setFont(font)
        self.delete_button.setFont(font)
        self.clear_button.setFont(font)

        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)

        self.clear_button.clicked.connect(self.clear_fields)
        self.submit_button.clicked.connect(self.submit_game_code)
        self.delete_button.clicked.connect(self.delete_game_code)
        self.load_button.clicked.connect(self.load_selected_game_code)

    def setupGameCodeList(self, layout):
        """Sets up the client list UI component."""
        hbox = QHBoxLayout()

        self.code_search_bar = QLineEdit()
        self.code_search_bar.setPlaceholderText("Search game codes...")
        self.code_search_bar.textChanged.connect(self.search_game_codes)
        layout.addWidget(self.code_search_bar)

        self.game_code_list = QListWidget()
        self.game_code_list.setAlternatingRowColors(True)
        self.game_code_list.itemDoubleClicked.connect(self.load_game_code_data)
        self.game_code_list.itemDoubleClicked.connect(self.copy_product_code)
        hbox.addWidget(self.game_code_list)

        layout.addLayout(hbox)

    def submit_game_code(self):
        """Submits or updates a game code in the database."""
        product_code = self.game_product_code_entry.text()
        game_code_data = {
            'game_name': self.game_name_entry.text(),
            'product_code': product_code,
            'code_type': self.product_code_type_entry.currentText(),
            'used_status': self.use_status_entry.currentText()
        }

        # Check if the product code already exists
        query = "SELECT * FROM game_codes WHERE product_code = ?"
        existing_game_code = self.db_manager.fetch_data('Codes.db', query, (product_code,))

        if existing_game_code:
            # Update existing record
            self.db_manager.write_data('Codes.db', 'game_codes', 'product_code', game_code_data)
            QMessageBox.information(self, "Updated", "Game code updated successfully.")
        else:
            # Insert new record
            self.db_manager.add_new_entry('Codes.db', 'game_codes', game_code_data)
            QMessageBox.information(self, "Added", "New game code added successfully.")

        # Reload the list box with current search criteria
        current_search_text = self.code_search_bar.text()
        self.search_game_codes(current_search_text)

    def delete_game_code(self):
        """Deletes the selected game code after confirmation."""
        item = self.game_code_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Selection Required", "Please select a game code to delete.")
            return

        text, ok = QInputDialog.getText(self, "Confirm Delete", "Type 'delete' to confirm:")
        if ok and text == "delete":
            primary_key = int(item.text().split(':')[0].strip())
            if self.db_manager.delete_data('Codes.db', 'game_codes', f'id = {primary_key}'):
                self.search_game_codes(self.code_search_bar.text())  # Refresh the list
                QMessageBox.information(self, "Deleted", "Game code deleted successfully.")
            else:
                QMessageBox.critical(self, "Error", "Failed to delete game code.")
        else:
            QMessageBox.information(self, "Cancelled", "Delete operation cancelled.")

    def load_selected_game_code(self):
        """Load the currently selected game code data into the input fields."""
        item = self.game_code_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Selection Required", "Please select a game code from the list.")
            return

        self.load_game_code_data(item)

    def search_game_codes(self, text):
        """Searches for clients based on the provided text."""
        if not text.strip():
            query = """
                SELECT id, game_name, product_code, code_type, used_status 
                FROM game_codes 
                ORDER BY game_name
            """
            parameters = ()
        else:
            query = """
                SELECT id, game_name, product_code, code_type, used_status
                FROM game_codes
                WHERE product_code LIKE ? OR game_name LIKE ?
                ORDER BY game_name
            """
            search_text = f"%{text}%"
            parameters = (search_text, search_text)

        results = self.db_manager.fetch_data('Codes.db', query, parameters)
        self.game_code_list.clear()
        for product_code in results:
            self.game_code_list.addItem(f"{product_code[0]}: {product_code[1]}: {product_code[2]}: {product_code[3]}")

    def load_game_code_data(self, item):
        """Loads game code data from the database based on the selected item's primary key."""
        # Extract the primary key (id) from the selected item
        primary_key = int(item.text().split(':')[0].strip())
        query = """
            SELECT game_name, product_code, code_type, used_status
            FROM game_codes 
            WHERE id = ?
        """
        product_data = self.db_manager.fetch_data('Codes.db', query, (primary_key,))

        if product_data:
            self.clear_fields()
            product = product_data[0]
            self.game_name_entry.setText(product[0])
            self.game_product_code_entry.setText(product[1])

            # Set the current index for product_code_type_entry combo box
            product_code_type_index = self.product_code_type_entry.findText(product[2])
            if product_code_type_index >= 0:
                self.product_code_type_entry.setCurrentIndex(product_code_type_index)

            # Set the current index for use_status_entry combo box
            use_status_index = self.use_status_entry.findText(product[3])
            if use_status_index >= 0:
                self.use_status_entry.setCurrentIndex(use_status_index)

    def clear_fields(self):
        """Clears all input fields in the window."""
        self.game_name_entry.clear()
        self.game_product_code_entry.clear()
        self.product_code_type_entry.setCurrentIndex(0)  # Reset combo box to first item
        self.use_status_entry.setCurrentIndex(0)  # Reset combo box to first item

    def copy_product_code(self, item):
        """Copy the Product Code from the selected item in the listbox to the clipboard."""
        product_code = item.text().split(':')[2].strip()  # Adjust index if needed
        QApplication.clipboard().setText(product_code)
