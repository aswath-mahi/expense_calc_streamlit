import os
import sqlite3
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExpenseManagerSQLite:
    def __init__(self, db_path='expenses.db'):
        self.db_path = db_path

    def add_category(self, name):
        if not name:
            logger.error("Category name cannot be empty.")
            return False
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO category (name) VALUES (?)", (name,))
            conn.commit()
            logger.info(f"Category '{name}' added successfully.")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error adding category '{name}': {e}")
            return False
        finally:
            conn.close()

    def add_subcategory(self, name, category_id):
        if not name or not category_id:
            logger.error("Subcategory name and category ID cannot be empty.")
            return False
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO subcategory (name, category_id) VALUES (?, ?)", (name, category_id))
            conn.commit()
            logger.info(f"Subcategory '{name}' added successfully under category ID {category_id}.")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error adding subcategory '{name}': {e}")
            return False
        finally:
            conn.close()

    def add_expense(self, expense_date, category_id, subcategory_id, description, amount, usr_name):
        if not expense_date or not category_id or not subcategory_id or not amount or not usr_name:
            logger.error("Expense data fields cannot be empty.")
            return False
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO expense (date, category_id, subcategory_id, description, amount, usr_name)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (expense_date, category_id, subcategory_id, description, amount, usr_name))
            conn.commit()
            logger.info(f"Expense of amount {amount} added successfully.")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error adding expense: {e}")
            return False
        finally:
            conn.close()

    def get_categories(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM category")
            categories = cursor.fetchall()
            return categories
        except sqlite3.Error as e:
            logger.error(f"Error fetching categories: {e}")
            return []
        finally:
            conn.close()

    def get_subcategories(self, category_id):
        if not category_id:
            logger.error("Category ID cannot be empty.")
            return []
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM subcategory WHERE category_id = ?", (category_id,))
            subcategories = cursor.fetchall()
            return subcategories
        except sqlite3.Error as e:
            logger.error(f"Error fetching subcategories for category ID {category_id}: {e}")
            return []
        finally:
            conn.close()

    def fetch_expenses(self, usr_name=None):
        try:
            conn = sqlite3.connect(self.db_path)
            query = """
                SELECT e.id, e.date, c.name AS category, s.name AS subcategory, e.amount, e.description, e.usr_name
                FROM expense e
                JOIN category c ON e.category_id = c.id
                JOIN subcategory s ON e.subcategory_id = s.id
            """
            if usr_name:
                query += " WHERE e.usr_name = ?"
                df = pd.read_sql_query(query, conn, params=(usr_name,))
            else:
                df = pd.read_sql_query(query, conn)
            return df
        except sqlite3.Error as e:
            logger.error(f"Error fetching expenses: {e}")
            return pd.DataFrame()
        finally:
            conn.close()

db_path = os.getenv('DB_PATH', 'expenses.db')
utils_ = ExpenseManagerSQLite(db_path=db_path)
