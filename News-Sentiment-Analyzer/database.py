import sqlite3
import pandas as pd
from typing import List, Dict
from config import DB_NAME

def init_db():
    """Initializes the articles database and sets up the schema."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            url TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            summary TEXT,
            source TEXT NOT NULL,
            published_at TEXT,
            sentiment_score REAL,
            sentiment_label TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_articles(articles: List[Dict]):
    """
    Inserts news articles with sentiment analysis scores.
    Uses INSERT OR IGNORE to prevent duplicate entries based on the URL.
    """
    if not articles:
        return

    query = """
    INSERT OR IGNORE INTO articles 
    (url, title, summary, source, published_at, sentiment_score, sentiment_label)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    
    conn = sqlite3.connect(DB_NAME)
    try:
        # Map list of dictionaries into tuple parameters
        records = [
            (
                a["url"],
                a["title"],
                a.get("summary", ""),
                a["source"],
                a.get("published_at", ""),
                a["sentiment_score"],
                a["sentiment_label"]
            )
            for a in articles
        ]
        conn.executemany(query, records)
        conn.commit()
    finally:
        conn.close()

def get_articles_df() -> pd.DataFrame:
    """Retrieves all stored articles into a pandas DataFrame."""
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query("SELECT * FROM articles", conn)
        return df
    finally:
        conn.close()
