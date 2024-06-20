
import streamlit as st
import sqlite3
import pandas as pd

def get_connection():
    conn = sqlite3.connect('expenses.db')
    return conn

# Function to add a new category
def add_category(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO category (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

# Function to add a new subcategory
def add_subcategory(name, category_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO subcategory (name, category_id) VALUES (?, ?)", (name, category_id))
    conn.commit()
    conn.close()

# Function to add a new expense
def add_expense(expence_date,category_id, subcategory_id, description, amount,usr_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expense (date,category_id, subcategory_id, description, amount, usr_name) VALUES (?, ?, ?, ?, ?, ?)", 
                   (expence_date,category_id, subcategory_id, description, amount, usr_name))
    conn.commit()
    conn.close()

# Function to fetch all categories
def get_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM category")
    categories = cursor.fetchall()
    conn.close()
    return categories

# Function to fetch subcategories based on category_id
def get_subcategories(category_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM subcategory WHERE category_id = ?", (category_id,))
    subcategories = cursor.fetchall()
    conn.close()
    return subcategories


def fetch_expenses(user_name):
    conn = sqlite3.connect('expenses.db')
    query = """
        SELECT e.id, e.date, c.name AS category, s.name AS subcategory,e.amount,e.description,e.usr_name
        FROM expense e
        JOIN category c ON e.category_id = c.id
        JOIN subcategory s ON e.subcategory_id = s.id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df