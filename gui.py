import csv
import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFormLayout, QFrame, QMessageBox, QComboBox, QInputDialog,
    QApplication, QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from special_classes import EnterLineEdit


class ProductInfoSection(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = None
        self.product_name_entry = None
        self.product_code_entry = None
        self.product_code_type_entry = None
        self.use_status_entry = None
        self.initializeUI()

    def initializeUI(self):
        self.layout = QFormLayout()
        self.setupProductInfo()
        self.setLayout(self.layout)

    def setupProductInfo(self):
        font = QFont("Arial", 12)
        label_font = QFont("Arial", 10, QFont.Bold)

        product_title = QLabel("Game Code")
        product_title.setFont(label_font)
        self.layout.addRow(product_title)

        self.product_name_entry = EnterLineEdit()
        self.product_code_entry = EnterLineEdit()
        self.product_code_type_entry = QComboBox()
        self.use_status_entry = QComboBox()

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
            self.layout.addRow(label, widget)

    def getProductCode(self):
        return self.product_code_entry.text()

    def getProductCodeData(self):
        return {
            'product_name': self.product_name_entry.text(),
            'product_code': self.product_code_entry.text(),
            'code_type': self.product_code_type_entry.currentText(),
            'used_status': self.use_status_entry.currentText()
        }

    def clearFields(self):
        self.product_name_entry.clear()
        self.product_code_entry.clear()
        self.product_code_type_entry.setCurrentIndex(0)
        self.use_status_entry.setCurrentIndex(0)

    def populateFields(self, product):
        self.product_name_entry.setText(product[0])
        self.product_code_entry.setText(product[1])
        self.set_product_code_type_index(product[2])
        self.set_use_status_index(product[3])

    def set_product_code_type_index(self, code_type):
        index = self.product_code_type_entry.findText(code_type)
        if index >= 0:
            self.product_code_type_entry.setCurrentIndex(index)

    def set_use_status_index(self, use_status):
        index = self.use_status_entry.findText(use_status)
        if index >= 0:
            self.use_status_entry.setCurrentIndex(index)


class ProductSelectionSection(QWidget):
    def __init__(self, db_manager, product_code_list_section):
        super().__init__()
        self.db_manager = db_manager
        self.product_code_list_section = product_code_list_section
        self.layout = None
        self.code_type_refine_combo = None
        self.status_refine_combo = None
        self.initializeUI()

    def initializeUI(self):
        self.layout = QVBoxLayout()
        self.setupRefineDropdowns()
        self.setupUploadButton()
        self.setLayout(self.layout)

    def setupRefineDropdowns(self):
        product_selection_label = QLabel("Product Selection")
        self.layout.addWidget(product_selection_label)

        self.code_type_refine_combo = QComboBox()
        self.code_type_refine_combo.addItems(["Default", "Unknown", "Full Product", "Expansion/Addon"])
        self.layout.addWidget(QLabel("Code Type Refine"))
        self.layout.addWidget(self.code_type_refine_combo)

        self.status_refine_combo = QComboBox()
        self.status_refine_combo.addItems(["Default", "Unknown", "Available", "Used"])
        self.layout.addWidget(QLabel("Status Refine"))
        self.layout.addWidget(self.status_refine_combo)

    def setupUploadButton(self):
        upload_button = QPushButton("Upload CSV")
        upload_button.clicked.connect(self.openFileDialog)
        self.layout.addWidget(upload_button)

    def openFileDialog(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open CSV File", "", "CSV Files (*.csv)", options=options)
        if file_name:
            logging.info(f"CSV file selected: {file_name}")
            self.processCSV(file_name)

    def processCSV(self, file_name):
        with open(file_name, 'r', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)  # Skip the header row
            row_count = 0
            for row in csvreader:
                row_count += 1
                logging.info(f"Processing row {row_count}: {row}")
                product_data = {
                    'Product Name': row[0],
                    'Product Code': row[1],
                    'Product Code Type': row[2],
                    'Status': row[3]
                }
                if not self.checkIfProductCodeExists(product_data['Product Code']):
                    logging.info(f"Adding new product: {product_data}")
                    self.addNewProduct(product_data)
                else:
                    logging.info(f"Product code already exists: {product_data['Product Code']}")
            logging.info(f"Total rows processed: {row_count}")

    def checkIfProductCodeExists(self, product_code):
        query = "SELECT * FROM product_codes WHERE product_code = ?"
        parameters = (product_code,)
        logging.info(f"Checking if product code exists: {product_code}")
        logging.info(f"Query: {query}")
        logging.info(f"Parameters: {parameters}")
        result = self.db_manager.fetch_data('Codes.db', query, parameters)
        logging.info(f"Query result: {result}")
        return len(result) > 0

    def addNewProduct(self, product_data):
        try:
            # Check if any required fields are missing
            required_fields = ['Product Name', 'Product Code', 'Product Code Type', 'Status']
            missing_fields = [field for field in required_fields if field not in product_data or not product_data[field]]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

            # Add the new product to the database
            success = self.db_manager.add_new_entry(
                'Codes.db', 'product_codes', {
                    'product_name': product_data['Product Name'],
                    'product_code': product_data['Product Code'],
                    'code_type': product_data['Product Code Type'],
                    'used_status': product_data['Status']
                })

            if success:
                logging.info(f"New product added successfully: {product_data}")
                self.product_code_list_section.searchProductCodes("")
            else:
                raise Exception("Failed to add new product")

        except (ValueError, KeyError, Exception) as e:
            logging.error(f"Error adding new product: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to add new product: {str(e)}")

    def getCodeTypeFilter(self):
        return self.code_type_refine_combo.currentText()

    def getStatusFilter(self):
        return self.status_refine_combo.currentText()


class ProductCodeListSection(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.layout = None
        self.code_search_bar = None
        self.product_code_table = None
        self.initializeUI()

    def initializeUI(self):
        self.layout = QVBoxLayout()
        self.setupProductCodeList()
        self.setLayout(self.layout)

    def setupProductCodeList(self):
        self.code_search_bar = QLineEdit()
        self.code_search_bar.setPlaceholderText("Search product codes...")
        self.layout.addWidget(self.code_search_bar)

        self.product_code_table = QTableWidget()
        self.product_code_table.setRowCount(0)
        self.product_code_table.setColumnCount(6)
        self.product_code_table.setHorizontalHeaderLabels(["ID", "Product Name", "Product Code", "", "Code Type", "Status"])
        self.product_code_table.setAlternatingRowColors(True)
        self.product_code_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.product_code_table.setSelectionMode(QTableWidget.SingleSelection)
        self.product_code_table.setEditTriggers(QTableWidget.NoEditTriggers)

        header = self.product_code_table.horizontalHeader()
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

        self.layout.addWidget(self.product_code_table)

    def searchProductCodes(self, text, code_type_filter, status_filter):
        query = """
            SELECT id, product_name, product_code, code_type, used_status
            FROM product_codes
            WHERE (product_code LIKE ? OR product_name LIKE ?)
        """
        search_text = f"%{text}%"
        parameters = [search_text, search_text]

        if code_type_filter != "Default":
            query += " AND code_type = ?"
            parameters.append(code_type_filter)

        if status_filter != "Default":
            query += " AND used_status = ?"
            parameters.append(status_filter)

        query += " ORDER BY product_name"
        results = self.db_manager.fetch_data('Codes.db', query, tuple(parameters))
        self.populateTable(results)

    def populateTable(self, data):
        self.product_code_table.setSortingEnabled(False)
        self.product_code_table.setRowCount(0)

        for row_number, row_data in enumerate(data):
            self.product_code_table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                adjusted_column_number = column_number if column_number < 3 else column_number + 1
                self.product_code_table.setItem(row_number, adjusted_column_number, item)

                if adjusted_column_number in [0, 2, 4, 5]:
                    item.setTextAlignment(Qt.AlignCenter)

                if column_number == 3:
                    blank_item = QTableWidgetItem("")
                    self.product_code_table.setItem(row_number, column_number, blank_item)

        self.product_code_table.setSortingEnabled(True)

    def getSelectedProductCode(self):
        selected_items = self.product_code_table.selectedItems()
        if selected_items:
            return int(selected_items[0].text())
        return None

    def getSelectedProductCodeData(self):
        row = self.product_code_table.currentRow()
        if row >= 0:
            product_id = int(self.product_code_table.item(row, 0).text())
            query = """
                SELECT product_name, product_code, code_type, used_status
                FROM product_codes 
                WHERE id = ?
            """
            product_data = self.db_manager.fetch_data('Codes.db', query, (product_id,))
            if product_data:
                return product_data[0]
        return None


class ButtonSection(QWidget):
    def __init__(self, product_info_section, product_code_list_section, product_selection_section, db_manager):
        super().__init__()
        self.product_info_section = product_info_section
        self.product_code_list_section = product_code_list_section
        self.product_selection_section = product_selection_section
        self.db_manager = db_manager
        self.layout = None
        self.submit_button = None
        self.load_button = None
        self.delete_button = None
        self.clear_button = None
        self.initializeUI()

    def initializeUI(self):
        self.layout = QHBoxLayout()
        self.setupButtons()
        self.setLayout(self.layout)

    def setupButtons(self):
        font = QFont("Arial", 12)
        self.submit_button = QPushButton("Submit Code")
        self.load_button = QPushButton("Load Code")
        self.delete_button = QPushButton("Delete Code")
        self.clear_button = QPushButton("Clear Fields")

        self.submit_button.setFont(font)
        self.load_button.setFont(font)
        self.delete_button.setFont(font)
        self.clear_button.setFont(font)

        self.layout.addWidget(self.submit_button)
        self.layout.addWidget(self.load_button)
        self.layout.addWidget(self.delete_button)
        self.layout.addWidget(self.clear_button)

        self.clear_button.clicked.connect(self.clearFields)
        self.submit_button.clicked.connect(self.submitProductCode)
        self.delete_button.clicked.connect(self.deleteProductCode)
        self.load_button.clicked.connect(self.loadSelectedGameCode)

    def clearFields(self):
        logging.info("Clearing input fields")
        self.product_info_section.clearFields()

    def submitProductCode(self):
        product_code_data = self.product_info_section.getProductCodeData()
        product_code = product_code_data['product_code']

        logging.info(f"Submitting product code: {product_code}")

        existing_game_code = self.db_manager.fetch_data(
            'Codes.db', "SELECT * FROM product_codes WHERE product_code = ?", (product_code,))

        if existing_game_code:
            condition = f"product_code = '{product_code}'"
            success = self.db_manager.update_entry('Codes.db', 'product_codes', product_code_data, condition)
            if success:
                logging.info(f"Product code updated successfully: {product_code}")
                QMessageBox.information(self, "Updated", "Product code updated successfully.")
            else:
                logging.error(f"Failed to update product code: {product_code}")
                QMessageBox.critical(self, "Error", "Failed to update product code.")
        else:
            success = self.db_manager.add_new_entry('Codes.db', 'product_codes', product_code_data)
            if success:
                logging.info(f"New product code added successfully: {product_code}")
                QMessageBox.information(self, "Added", "New product code added successfully.")
            else:
                logging.error(f"Failed to add new product code: {product_code}")
                QMessageBox.critical(self, "Error", "Failed to add new product code.")

        code_type_filter = self.product_selection_section.getCodeTypeFilter()
        status_filter = self.product_selection_section.getStatusFilter()
        self.product_code_list_section.searchProductCodes("", code_type_filter, status_filter)

    def deleteProductCode(self):
        primary_key = self.product_code_list_section.getSelectedProductCode()
        if primary_key is None:
            logging.warning("No product code selected for deletion")
            QMessageBox.warning(self, "Selection Required", "Please select a product code to delete.")
            return

        if self.confirmDelete():
            logging.info(f"Deleting product code with ID: {primary_key}")
            self.performDeletion(primary_key)
        else:
            logging.info("Delete operation cancelled")
            QMessageBox.information(self, "Cancelled", "Delete operation cancelled.")

    def confirmDelete(self):
        text, ok = QInputDialog.getText(self, "Confirm Delete", "Type 'delete' to confirm:")
        return ok and text.lower() == 'delete'

    def performDeletion(self, primary_key):
        condition = f"id = {primary_key}"
        success = self.db_manager.delete_entry('Codes.db', 'product_codes', condition)
        if success:
            logging.info(f"Product code deleted successfully: {primary_key}")
            code_type_filter = self.product_selection_section.getCodeTypeFilter()
            status_filter = self.product_selection_section.getStatusFilter()
            self.product_code_list_section.searchProductCodes("", code_type_filter, status_filter)
            QMessageBox.information(self, "Deleted", "Product code deleted successfully.")
        else:
            logging.error(f"Failed to delete product code: {primary_key}")
            QMessageBox.critical(self, "Error", "Failed to delete product code.")

    def loadSelectedGameCode(self):
        product_code_data = self.product_code_list_section.getSelectedProductCodeData()
        if product_code_data:
            logging.info(f"Loading selected game code: {product_code_data}")
            self.product_info_section.populateFields(product_code_data)
        else:
            logging.warning("No game code selected for loading")
            QMessageBox.warning(self, "Selection Required", "Please select a game code from the list.")


class ClientWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.product_info_section = None
        self.product_code_list_section = None
        self.product_selection_section = None
        self.button_section = None
        self.initializeUI()

    def initializeUI(self):
        self.setWindowTitle("Game Code Management")
        self.setGeometry(100, 100, 800, 500)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.product_info_section = ProductInfoSection()
        self.product_code_list_section = ProductCodeListSection(self.db_manager)
        self.product_selection_section = ProductSelectionSection(self.db_manager, self.product_code_list_section)
        self.button_section = ButtonSection(self.product_info_section, self.product_code_list_section, self.product_selection_section, self.db_manager)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.product_info_section)
        top_layout.addWidget(self.product_selection_section)

        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.button_section)
        main_layout.addWidget(self.product_code_list_section)

        self.product_selection_section.code_type_refine_combo.currentTextChanged.connect(self.refineSearch)
        self.product_selection_section.status_refine_combo.currentTextChanged.connect(self.refineSearch)

        self.product_code_list_section.code_search_bar.textChanged.connect(self.searchProductCodes)
        self.product_code_list_section.product_code_table.itemDoubleClicked.connect(self.loadProductCodeData)
        self.product_code_list_section.product_code_table.itemDoubleClicked.connect(self.copyProductCode)

        self.searchProductCodes()

    def searchProductCodes(self):
        search_text = self.product_code_list_section.code_search_bar.text()
        code_type_filter = self.product_selection_section.getCodeTypeFilter()
        status_filter = self.product_selection_section.getStatusFilter()
        self.product_code_list_section.searchProductCodes(search_text, code_type_filter, status_filter)

    def loadProductCodeData(self, item):
        product_code_data = self.product_code_list_section.getSelectedProductCodeData()
        if product_code_data:
            self.product_info_section.populateFields(product_code_data)

    def copyProductCode(self, item):
        row = item.row()
        product_code_item = self.product_code_list_section.product_code_table.item(row, 2)
        if product_code_item:
            product_code = product_code_item.text()
            QApplication.clipboard().setText(product_code)

    def refineSearch(self):
        search_text = self.product_code_list_section.code_search_bar.text()
        code_type_filter = self.product_selection_section.getCodeTypeFilter()
        status_filter = self.product_selection_section.getStatusFilter()
        self.product_code_list_section.searchProductCodes(search_text, code_type_filter, status_filter)
