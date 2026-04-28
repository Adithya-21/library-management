import sqlite3

def connect():
    return sqlite3.connect("library.db", check_same_thread=False)

def create_tables():
    conn = connect()
    cur = conn.cursor()
    # Schema includes Price, Preview, and Full Book path
    cur.execute("""CREATE TABLE IF NOT EXISTS Books(
        book_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        title TEXT, author TEXT, category TEXT, quantity INTEGER,
        price REAL DEFAULT 0.0, 
        preview_url TEXT, 
        full_book_path TEXT,
        UNIQUE(title, author))""")
    
    cur.execute("""CREATE TABLE IF NOT EXISTS Users(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT, email TEXT, password TEXT)""")
    conn.commit()
    conn.close()

def add_user(name, email, password):
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO Users(name, email, password) VALUES (?, ?, ?)", (name, email, password))
    conn.commit()
    conn.close()

def verify_login(email, password):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Users WHERE email=? AND password=?", (email, password))
    user = cur.fetchone()
    conn.close()
    return user

def add_book(title, author, category, qty, price, preview_url, full_path):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""INSERT OR IGNORE INTO Books(title, author, category, quantity, price, preview_url, full_book_path) 
                   VALUES (?,?,?,?,?,?,?)""", (title, author, category, qty, price, preview_url, full_path))
    conn.commit()
    conn.close()

def get_all_books():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Books")
    data = cur.fetchall()
    conn.close()
    return data

def get_books_by_category(category):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Books WHERE category=?", (category,))
    data = cur.fetchall()
    conn.close()
    return data