import sqlite3
import pandas as pd
from typing import List, Dict

class DatabaseManager:
    """
    Handles all SQLite database connections and queries.
    Designed to be easily replaceable with SQLAlchemy if you upgrade to PostgreSQL later.
    """
    
    def __init__(self, db_path: str = "reddit_data.db"):
        self.db_path = db_path
        self._create_tables()

    def _get_connection(self):
        """Returns a new database connection."""
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        """Initializes the database schema."""
        query = """
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            subreddit TEXT,
            title TEXT,
            score INTEGER,
            num_comments INTEGER,
            created_utc REAL,
            url TEXT
        )
        """
        with self._get_connection() as conn:
            conn.execute(query)

    def insert_posts(self, posts: List[Dict]):
        """
        Inserts a list of post dictionaries into the database.
        Uses INSERT OR IGNORE to prevent duplicate entries if run multiple times.
        """
        query = """
        INSERT OR IGNORE INTO posts 
        (id, subreddit, title, score, num_comments, created_utc, url) 
        VALUES (:id, :subreddit, :title, :score, :num_comments, :created_utc, :url)
        """
        with self._get_connection() as conn:
            conn.executemany(query, posts)
            
    def get_all_posts_df(self) -> pd.DataFrame:
        """Retrieves all posts as a Pandas DataFrame for easy analysis."""
        with self._get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM posts", conn)
