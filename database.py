import sqlite3

def connect_db():
    # This creates (or opens) the library.db file
    return sqlite3.connect("library.db", check_same_thread=False)

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    
    # 1. Users Table: Stores Name, Email, and Password
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        name TEXT, 
                        email TEXT UNIQUE, 
                        password TEXT)''')
    
    # 2. Books Table: Stores all resource details including Stock
    cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        author TEXT,
                        category TEXT,
                        stock INTEGER,
                        price REAL,
                        preview_path TEXT,
                        full_path TEXT)''')
    conn.commit()
    conn.close()

# --- USER FUNCTIONS ---

def add_user(name, email, password):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", 
                       (name, email, password))
        conn.commit()
    except sqlite3.IntegrityError:
        pass # Email already exists
    conn.close()

def verify_login(email, password):
    conn = connect_db()
    cursor = conn.cursor()
    # We select name and email to pass back to app.py session state
    cursor.execute("SELECT name, email FROM users WHERE email=? AND password=?", 
                   (email, password))
    user = cursor.fetchone()
    conn.close()
    return user

# --- BOOK FUNCTIONS ---

def add_book(title, author, category, stock, price, preview_path, full_path):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO books (title, author, category, stock, price, preview_path, full_path) 
                      VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                   (title, author, category, stock, price, preview_path, full_path))
    conn.commit()
    conn.close()

def get_all_books():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    conn.close()
    return books

def get_books_by_category(category):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE category=?", (category,))
    books = cursor.fetchall()
    conn.close()
    return books
