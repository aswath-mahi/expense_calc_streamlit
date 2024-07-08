import sqlite3
from werkzeug.security import generate_password_hash

class SQLiteDatabaseManager:
    def __init__(self, db_name='expenses.db'):
        self.db_name = db_name

    def init_db(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Create table for categories
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS category (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )
                ''')
                
                # Create table for subcategories
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS subcategory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category_id INTEGER,
                    FOREIGN KEY (category_id) REFERENCES category (id)
                )
                ''')

                # Create table for expenses
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS expense (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    category_id INTEGER,
                    subcategory_id INTEGER,
                    description TEXT,
                    amount REAL,
                    usr_name TEXT,
                    FOREIGN KEY (category_id) REFERENCES category (id),
                    FOREIGN KEY (subcategory_id) REFERENCES subcategory (id)
                )
                ''')

                # Create table for users
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    password TEXT,
                    is_admin INTEGER,
                    deleted INTEGER DEFAULT 0
                )
                ''')
                
                # Create a default admin user
                cursor.execute('''
                INSERT OR IGNORE INTO users (username, password, is_admin, deleted)
                VALUES (?, ?, ?, ?)
                ''', ('admin', generate_password_hash('Sh@1420I'), 1, 0))
                
                conn.commit()
                print("Database initialized successfully.")
        except Exception as e:
            print(f"Error initializing database: {e}")

    def insert_user(self, username, hashed_password, is_admin):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO users (username, password, is_admin, deleted)
                VALUES (?, ?, ?, ?)
                ''', (username, hashed_password, is_admin, 0))
                conn.commit()
                print(f"User {username} inserted successfully.")
        except Exception as e:
            print(f"Error inserting user {username}: {e}")

    def get_user(self, username):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                SELECT * FROM users WHERE username = ? AND deleted = 0
                ''', (username,))
                user = cursor.fetchone()
                if user:
                    print(f"User {username} found.")
                else:
                    print(f"User {username} not found.")
                return user
        except Exception as e:
            print(f"Error retrieving user {username}: {e}")

    def fetch_users(self, include_deleted=False):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                if include_deleted:
                    cursor.execute('SELECT username, password, is_admin, deleted FROM users')
                else:
                    cursor.execute('SELECT username, password, is_admin, deleted FROM users WHERE deleted = 0')
                users = cursor.fetchall()
                print(f"Fetched {len(users)} users.")
                return users
        except Exception as e:
            print(f"Error fetching users: {e}")

    def update_user_password(self, username, new_password):
        try:
            hashed_password = generate_password_hash(new_password)
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                UPDATE users
                SET password = ?
                WHERE username = ?
                ''', (hashed_password, username))
                conn.commit()
                if cursor.rowcount > 0:
                    print(f"Password for user {username} updated successfully.")
                else:
                    print(f"No user {username} found to update.")
        except Exception as e:
            print(f"Error updating password for user {username}: {e}")

    def soft_delete_user(self, username):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                UPDATE users
                SET deleted = 1
                WHERE username = ?
                ''', (username,))
                conn.commit()
                if cursor.rowcount > 0:
                    print(f"User {username} soft-deleted successfully.")
                else:
                    print(f"No user {username} found to delete.")
        except Exception as e:
            print(f"Error soft-deleting user {username}: {e}")

    def hard_delete_user(self, username):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                DELETE FROM users
                WHERE username = ?
                ''', (username,))
                conn.commit()
                if cursor.rowcount > 0:
                    print(f"User {username} hard-deleted successfully.")
                else:
                    print(f"No user {username} found to delete.")
        except Exception as e:
            print(f"Error hard-deleting user {username}: {e}")


# Example usage:
db_manager = SQLiteDatabaseManager()
