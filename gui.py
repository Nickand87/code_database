import csv
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QListWidget, QFormLayout, QFrame, QMessageBox,
                             QComboBox, QInputDialog, QApplication, QFileDialog, QTableWidget,
                             QTableWidgetItem, QHeaderView)
from PyQt5.QtGui import QFont, QIntValidator, QRegExpValidator, QColor
from PyQt5.QtCore import QRegExp, Qt
from special_classes import EnterLineEdit, CustomTitleBar


class ClickableLineEdit(QLineEdit):
    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        QApplication.clipboard().setText(self.text())


class ClientWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager

        # Initialize all instance attributes
        self.product_name_entry = None
        self.product_code_entry = None
        self.product_code_type_entry = None
        self.use_status_entry = None
        self.submit_button = None
        self.load_button = None
        self.delete_button = None
        self.clear_button = None
        self.product_code_table = None
        self.code_search_bar = None

        self.initializeUI()
        self.search_product_codes("")

    def initializeUI(self):
        """Initializes the main UI components of the window."""
        self.setWindowTitle("Game Code Management")
        self.setGeometry(100, 100, 800, 500)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        self.setupInputFields(main_layout)
        self.setupButtons(main_layout)
        self.setupUploadButton()
        self.setupProductCodeList(main_layout)

    def setupInputFields(self, layout):
        """Sets up input fields for client and contact information."""
        top_layout = QHBoxLayout()  # Horizontal layout to contain ProductInfo and ProductSelection frames

        # ProductInfo Frame
        product_info_frame = QFrame()
        product_info_frame.setFrameShape(QFrame.StyledPanel)
        product_info_layout = QFormLayout(product_info_frame)

        self.setupProductInfo(product_info_layout)
        top_layout.addWidget(product_info_frame)  # Add ProductInfo frame to top_layout

        # ProductSelection Frame
        product_selection_frame = QFrame()
        product_selection_frame.setFrameShape(QFrame.StyledPanel)
        self.product_selection_layout = QVBoxLayout(product_selection_frame)  # Set the product_selection_layout

        # Example widget in ProductSelection frame
        product_selection_label = QLabel("Product Selection")
        self.product_selection_layout.addWidget(product_selection_label)

        product_selection_frame.setFixedWidth(200)
        top_layout.addWidget(product_selection_frame)

        layout.addLayout(top_layout)

    def setupProductInfo(self, layout):
        """Sets up product information input fields."""
        font = QFont("Arial", 12)
        label_font = QFont("Arial", 10, QFont.Bold)

        product_title = QLabel("Game Code")
        product_title.setFont(label_font)
        layout.addRow(product_title)

        self.product_name_entry = EnterLineEdit()
        self.product_code_entry = EnterLineEdit()
        self.product_code_type_entry = QComboBox()
        self.use_status_entry = QComboBox()

        # Combobox options
        self.product_code_type_entry.addItems(["Unknown", "Full Product", "Expansion/Addon"])
        self.use_status_entry.addItems(["Unknown", "Available", "Used"])

        for label_text, widget in [
            ("Product Name:", self.product_name_entry),
            ("Product Code:", self.product_code_entry),
            ("Product Code Type:", self.product_code_type_entry),
            ("Status:", self.use_status_entry),
        ]:
            label = QLabel(label_text)
            label.setFont(label_font)
            widget.setFont(font)
            layout.addRow(label, widget)

    def setupUploadButton(self):
        """Sets up the upload button for CSV files."""
        upload_button = QPushButton("Upload CSV")
        upload_button.clicked.connect(self.openFileDialog)

        if self.product_selection_layout:
            self.product_selection_layout.addWidget(upload_button)  # Add to product_selection_layout

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
        self.submit_button.clicked.connect(self.submit_product_code)
        self.delete_button.clicked.connect(self.delete_product_code)
        self.load_button.clicked.connect(self.load_selected_game_code)

    def setupProductCodeList(self, layout):
        hbox = QHBoxLayout()

        self.code_search_bar = QLineEdit()
        self.code_search_bar.setPlaceholderText("Search product codes...")
        self.code_search_bar.textChanged.connect(self.search_product_codes)
        layout.addWidget(self.code_search_bar)

        # Use QTableWidget instead of QListWidget
        self.product_code_table = QTableWidget()
        self.product_code_table.setRowCount(0)
        self.product_code_table.setColumnCount(6)  # Adjust the number of columns as needed
        self.product_code_table.setHorizontalHeaderLabels(["ID", "Product Name", "Product Code", "", "Code Type", "Status"])
        self.product_code_table.setAlternatingRowColors(True)

        # Set selection behavior to select entire rows
        self.product_code_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.product_code_table.setSelectionMode(QTableWidget.SingleSelection)

        # Make table read-only (non-editable)
        self.product_code_table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.product_code_table.itemDoubleClicked.connect(self.load_product_code_data)
        self.product_code_table.itemDoubleClicked.connect(self.copy_product_code)

        # Set the horizontal stretch factor
        hbox.addWidget(self.product_code_table, 1)

        # Enable sorting and set default sorting criteria
        self.product_code_table.setSortingEnabled(True)
        self.product_code_table.sortByColumn(1, Qt.AscendingOrder)  # Sort by first column (ID) in ascending order by default

        # Set the horizontal header to stretch and adjust with the window
        header = self.product_code_table.horizontalHeader()
        #header.setSectionResizeMode(QHeaderView.Stretch)

        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Interactive)
        header.setSectionResizeMode(5, QHeaderView.Interactive)

        self.product_code_table.setColumnWidth(0, 50)
        self.product_code_table.setColumnWidth(1, 200)
        self.product_code_table.setColumnWidth(2, 150)
        self.product_code_table.setColumnWidth(4, 110)
        self.product_code_table.setColumnWidth(5, 110)

        layout.addLayout(hbox)

    def submit_product_code(self):
        """Submits or updates a game code in the database."""
        product_code = self.product_code_entry.text()
        product_code_data = {
            'product_name': self.product_name_entry.text(),
            'product_code': product_code,
            'code_type': self.product_code_type_entry.currentText(),
            'used_status': self.use_status_entry.currentText()
        }

        # Check if the product code already exists
        query = "SELECT * FROM product_codes WHERE product_code = ?"
        existing_game_code = self.db_manager.fetch_data('Codes.db', query, (product_code,))

        if existing_game_code:
            # Update existing record
            self.db_manager.write_data('Codes.db', 'product_codes', 'product_code', product_code_data)
            QMessageBox.information(self, "Updated", "Product code updated successfully.")
        else:
            # Insert new record
            self.db_manager.add_new_entry('Codes.db', 'product_codes', product_code_data)
            QMessageBox.information(self, "Added", "New product code added successfully.")

        # Reload the list box with current search criteria
        current_search_text = self.code_search_bar.text()
        self.search_product_codes(current_search_text)

    def delete_product_code(self):
        """Deletes the selected game code after confirmation."""
        selected_items = self.product_code_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Required", "Please select a product code to delete.")
            return

        # Assuming the first column of your table is the primary key for deletion
        primary_key = int(selected_items[0].text())  # Adjust the index if needed

        text, ok = QInputDialog.getText(self, "Confirm Delete", "Type 'delete' to confirm:")
        if ok and text.lower() == 'delete':
            if self.db_manager.delete_data('Codes.db', 'product_codes', f'id = {primary_key}'):
                self.search_product_codes(self.code_search_bar.text())  # Refresh the list
                QMessageBox.information(self, "Deleted", "Product code deleted successfully.")
            else:
                QMessageBox.critical(self, "Error", "Failed to delete product code.")
        else:
            QMessageBox.information(self, "Cancelled", "Delete operation cancelled.")

    def load_selected_game_code(self):
        """Load the currently selected game code data into the input fields."""
        item = self.product_code_table.currentItem()
        if not item:
            QMessageBox.warning(self, "Selection Required", "Please select a game code from the list.")
            return

        self.load_product_code_data(item)

    def search_product_codes(self, text):
        """Searches for product codes based on the provided text."""
        if not text.strip():
            query = """
                SELECT id, product_name, product_code, code_type, used_status 
                FROM product_codes 
                ORDER BY product_name
            """
            parameters = ()
        else:
            query = """
                SELECT id, product_name, product_code, code_type, used_status
                FROM product_codes
                WHERE product_code LIKE ? OR product_name LIKE ?
                ORDER BY product_name
            """
            search_text = f"%{text}%"
            parameters = (search_text, search_text)

        results = self.db_manager.fetch_data('Codes.db', query, parameters)
        self.populate_table(results)

    def populate_table(self, data):
        self.product_code_table.setSortingEnabled(False)
        self.product_code_table.setRowCount(0)
        grey_color = QColor(25, 35, 45)  # Light grey color

        for row_number, row_data in enumerate(data):
            self.product_code_table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                adjusted_column_number = column_number if column_number < 3 else column_number + 1
                self.product_code_table.setItem(row_number, adjusted_column_number, item)

                # Center-align data in specific columns (e.g., 0, 4, 5)
                if adjusted_column_number in [0, 2, 4, 5]:
                    item.setTextAlignment(Qt.AlignCenter)

                # Set the background color for the blank column
                if adjusted_column_number == 3:
                    item.setBackground(grey_color)

                # Inserting the blank cell with grey background
                if column_number == 2:
                    blank_item = QTableWidgetItem("")
                    blank_item.setBackground(grey_color)
                    self.product_code_table.setItem(row_number, column_number + 1, blank_item)

        self.product_code_table.setSortingEnabled(True)

    def load_product_code_data(self, item):
        row = item.row()
        primary_key = int(self.product_code_table.item(row, 0).text())
        query = """
            SELECT product_name, product_code, code_type, used_status
            FROM product_codes 
            WHERE id = ?
        """
        product_data = self.db_manager.fetch_data('Codes.db', query, (primary_key,))

        if product_data:
            self.clear_fields()
            product = product_data[0]
            self.product_name_entry.setText(product[0])
            self.product_code_entry.setText(product[1])

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
        self.product_name_entry.clear()
        self.product_code_entry.clear()
        self.product_code_type_entry.setCurrentIndex(0)  # Reset combo box to first item
        self.use_status_entry.setCurrentIndex(0)  # Reset combo box to first item

    def copy_product_code(self, item):
        """Copy the Product Code from the selected row in the table to the clipboard."""
        row = item.row()
        # Assuming the Product Code is in the third column (index 2)
        product_code_item = self.product_code_table.item(row, 2)
        if product_code_item:
            product_code = product_code_item.text()
            QApplication.clipboard().setText(product_code)

    def openFileDialog(self):
        """Opens a file dialog and processes the selected CSV file."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "",
                                                   "CSV Files (*.csv)", options=options)
        if file_name:
            self.processCSV(file_name)

    def processCSV(self, file_name):
        """Reads the CSV file, checks for existing product codes, and adds new products to the database."""
        with open(file_name, newline='', encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                if not self.checkIfProductCodeExists(row['Product Code']):
                    self.addNewProduct(row)

    def checkIfProductCodeExists(self, product_code):
        result = self.db_manager.fetch_data('Codes.db', "SELECT * FROM product_codes WHERE product_code = ?", (product_code,))
        return len(result) > 0

    def addNewProduct(self, product_data):
        self.db_manager.add_new_entry('Codes.db', 'product_codes', {
            'product_name': product_data['Product Name'],
            'product_code': product_data['Product Code'],
            'code_type': product_data['Product Code Type'],
            'used_status': product_data['Status']
        })

        current_search_text = self.code_search_bar.text()
        self.search_product_codes(current_search_text)
