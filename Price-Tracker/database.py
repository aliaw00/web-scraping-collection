import sqlite3
from datetime import datetime
from config import DB_NAME

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            url TEXT,
            price REAL,
            checked_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_price(name, url, price):
    if price is None:
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO price_history (name, url, price, checked_at)
        VALUES (?, ?, ?, ?)
    """, (name, url, price, datetime.now().isoformat()))
    conn.commit()
    conn.close()
