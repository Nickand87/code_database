import sqlite3
import os
import logging
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import QMessageBox
import sys


class DatabaseManager:
    def __init__(self):
        self.db_folder = self.ensure_db_directory_exists()
        self.databases = self.load_database_names()
        self.connections = self.initialize_databases()

    def read_db_path_from_settings(self):
        try:
            tree = ET.parse('settings.xml')
            root = tree.getroot()
            return root.find('database/path').text
        except (ET.ParseError, AttributeError):
            QMessageBox.critical(None, "Error", "Error parsing settings.xml or missing database path.")
            sys.exit(1)

    def load_database_names(self):
        return ['Clients.db', 'Codes.db']

    def ensure_db_directory_exists(self):
        db_directory = self.read_db_path_from_settings()
        os.makedirs(db_directory, exist_ok=True)
        return db_directory

    def initialize_databases(self):
        connections = {}
        for db_name in self.databases:
            db_path = os.path.join(self.db_folder, db_name)
            try:
                conn = sqlite3.connect(db_path)
                self.initialize_tables(conn, db_name)
                connections[db_name] = conn
            except sqlite3.Error as e:
                QMessageBox.critical(None, f"Database Error ({db_name})", str(e))
                sys.exit(1)
        return connections

    def initialize_tables(self, conn, db_name):
        cursor = conn.cursor()
        if db_name == 'Clients.db':
            cursor.execute('''CREATE TABLE IF NOT EXISTS clients
                              (id INTEGER PRIMARY KEY, client_id INTEGER, client_name TEXT,
                               client_address1 TEXT, client_address2 TEXT,
                               client_phone TEXT, client_emailfax TEXT)''')
        elif db_name == 'Codes.db':
            cursor.execute('''CREATE TABLE IF NOT EXISTS product_codes
                              (id INTEGER PRIMARY KEY, product_name TEXT, product_code TEXT,
                               code_type TEXT, used_status TEXT)''')

    def fetch_data(self, db_name, query, params=None):
        if db_name in self.connections:
            conn = self.connections[db_name]
            try:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                return cursor.fetchall()
            except sqlite3.Error as e:
                QMessageBox.critical(None, f"Database Error ({db_name})", f"Error fetching data: {str(e)}")
        else:
            QMessageBox.critical(None, "Database Error", f"Database {db_name} not found.")
        return []

    def execute_query(self, db_name, query, params=None):
        if db_name in self.connections:
            conn = self.connections[db_name]
            try:
                cursor = conn.cursor()
                logging.info(f"Executing query: {query}")
                logging.info(f"Parameters: {params}")
                cursor.execute(query, params or ())
                conn.commit()
                return True
            except sqlite3.Error as e:
                logging.error(f"Error executing query: {str(e)}")
                QMessageBox.critical(None, f"Database Error ({db_name})", f"Error executing query: {str(e)}")
                conn.rollback()
        else:
            logging.error(f"Database {db_name} not found.")
            QMessageBox.critical(None, "Database Error", f"Database {db_name} not found.")
        return False

    def add_new_entry(self, db_name, table_name, data):
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        return self.execute_query(db_name, query, list(data.values()))

    def update_entry(self, db_name, table_name, data, condition):
        set_clause = ', '.join([f"{column} = ?" for column in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
        return self.execute_query(db_name, query, list(data.values()))

    def delete_entry(self, db_name, table_name, condition):
        query = f"DELETE FROM {table_name} WHERE {condition}"
        return self.execute_query(db_name, query)
