# setup_db.py
import sqlite3
from werkzeug.security import generate_password_hash

def init_db():
    conn = sqlite3.connect('expenses.db')
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
    ''', ('admin', generate_password_hash('admin_password'), 1, 0))

    conn.commit()
    conn.close()


def insert_user(username, hashed_password, is_admin):
    with sqlite3.connect('expenses.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, password, is_admin, deleted)
            VALUES (?, ?, ?, ?)
        ''', (username, hashed_password, is_admin, 0))
        conn.commit()

def get_user(username):
    with sqlite3.connect('expenses.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM users WHERE username = ? AND deleted = 0
        ''', (username,))
        return cursor.fetchone()

def fetch_users(include_deleted=False):
    with sqlite3.connect('expenses.db') as conn:
        cursor = conn.cursor()
        if include_deleted:
            cursor.execute('SELECT username, password, is_admin, deleted FROM users')
        else:
            cursor.execute('SELECT username, password, is_admin, deleted FROM users WHERE deleted = 0')
        users = cursor.fetchall()
    return users

def update_user_password(username, new_password):
    hashed_password = generate_password_hash(new_password)
    with sqlite3.connect('expenses.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users
            SET password = ?
            WHERE username = ?
        ''', (hashed_password, username))
        conn.commit()

def soft_delete_user(username):
    with sqlite3.connect('expenses.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users
            SET deleted = 1
            WHERE username = ?
        ''', (username,))
        conn.commit()

# Function for hard delete of a user
def hard_delete_user(username):
    with sqlite3.connect('expenses.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM users
            WHERE username = ?
        ''', (username,))
        conn.commit()

