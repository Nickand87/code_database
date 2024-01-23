import sqlite3
import os
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import QMessageBox
import sys


class DatabaseManager:
    """Handles database operations including initialization."""
    def __init__(self):
        self.db_folder = self.ensure_db_directory_exists()
        self.databases = self.load_database_names()
        self.connections = self.initialize_databases()

    def read_db_path_from_settings(self):
        """Read the database path from the XML settings file."""
        try:
            tree = ET.parse('settings.xml')
            root = tree.getroot()
            db_path = root.find('database/path').text
            return db_path
        except ET.ParseError:
            QMessageBox.critical(None, "Error", "Error parsing settings.xml.")
            sys.exit(1)
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error reading settings: {str(e)}")
            sys.exit(1)

    def load_database_names(self):
        """Load the names of all databases from settings or a predefined list."""
        # Example: reading from a predefined list
        return ['Clients.db', 'Codes.db']

    def ensure_db_directory_exists(self):
        """Ensure the directory for the databases exists."""
        db_directory = self.read_db_path_from_settings()
        if not os.path.exists(db_directory):
            os.makedirs(db_directory)
        return db_directory

    def initialize_databases(self):
        """Initialize multiple databases and return their connections."""
        connections = {}
        db_initialization_mapping = {
            'Clients.db': self.initialize_clients_db,
            'Codes.db': self.initialize_codes_db,
        }

        for db_name in self.databases:
            db_path = os.path.join(self.db_folder, db_name)
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # Call the specific initialization function for each database
                if db_name in db_initialization_mapping:
                    db_initialization_mapping[db_name](cursor)
                else:
                    print(f"No initialization function defined for {db_name}")

                connections[db_name] = conn
            except sqlite3.Error as e:
                print(f"Database Error with {db_name}: {str(e)}")
                QMessageBox.critical(None, "Database Error", f"{db_name}: {str(e)}")
                sys.exit(1)
        return connections

    def fetch_data(self, db_name, query, params=None):
        """Fetch data from the specified database using a SQL query."""
        if db_name in self.connections:
            conn = self.connections[db_name]
            try:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                return cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Error fetching data from {db_name}: {str(e)}")
                QMessageBox.critical(None, "Database Error", f"Error fetching data from {db_name}: {str(e)}")
                return []
        else:
            QMessageBox.critical(None, "Database Error", f"Database {db_name} not found.")
            return []

    def add_new_entry(self, db_name, table_name, data):
        """Adds a new entry to a specified table in a specified database."""
        if db_name not in self.connections:
            print(f"Database {db_name} not found.")
            return

        conn = self.connections[db_name]
        try:
            cursor = conn.cursor()

            # Constructing the INSERT query
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

            # Executing the query
            cursor.execute(query, list(data.values()))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding new entry to {db_name}: {str(e)}")
            conn.rollback()

    def write_data(self, db_name, table_name, key_field, data):
        """Write data to a specified table in a specified database."""
        if db_name not in self.connections:
            print(f"Database {db_name} not found.")
            return

        conn = self.connections[db_name]
        try:
            cursor = conn.cursor()

            # Check if a record with the key already exists
            select_query = f"SELECT * FROM {table_name} WHERE {key_field} = ?"
            cursor.execute(select_query, (data[key_field],))
            exists = cursor.fetchone()

            if exists:
                # Update existing record
                fields = ", ".join([f"{k} = ?" for k in data if k != key_field])
                values = [v for k, v in data.items() if k != key_field]
                update_query = f"UPDATE {table_name} SET {fields} WHERE {key_field} = ?"
                cursor.execute(update_query, values + [data[key_field]])
            else:
                # Insert new record
                placeholders = ", ".join(["?" for _ in data])
                fields = ", ".join(data.keys())
                values = list(data.values())
                insert_query = f"INSERT INTO {table_name} ({fields}) VALUES ({placeholders})"
                cursor.execute(insert_query, values)

            conn.commit()
        except sqlite3.Error as e:
            print(f"Error writing data to {db_name}: {str(e)}")
            conn.rollback()

    def delete_data(self, db_name, table_name, condition):
        """Deletes an entry from the specified table in the specified database based on a condition."""
        if db_name not in self.connections:
            print(f"Database {db_name} not found.")
            return False

        conn = self.connections[db_name]
        try:
            cursor = conn.cursor()

            # Constructing the DELETE query
            query = f"DELETE FROM {table_name} WHERE {condition}"

            # Executing the query
            cursor.execute(query)
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting entry from {db_name}: {str(e)}")
            conn.rollback()
            return False

    def initialize_clients_db(self, cursor):
        try:
            cursor.execute('''CREATE TABLE IF NOT EXISTS clients 
                               (id INTEGER PRIMARY KEY, client_id INTEGER, client_name TEXT, 
                                client_address1 TEXT, client_address2 TEXT, 
                                client_phone TEXT, client_emailfax TEXT)''')
        except sqlite3.Error as e:
            print(f"Database Error: {str(e)}")
            QMessageBox.critical(None, "Database Error", str(e))
            sys.exit(1)

    def initialize_codes_db(self, cursor):
        try:
            cursor.execute('''CREATE TABLE IF NOT EXISTS product_codes 
                               (id INTEGER PRIMARY KEY, product_name TEXT, product_code TEXT, 
                                code_type TEXT, used_status TEXT)''')
        except sqlite3.Error as e:
            print(f"Database Error: {str(e)}")
            QMessageBox.critical(None, "Database Error", str(e))
            sys.exit(1)
