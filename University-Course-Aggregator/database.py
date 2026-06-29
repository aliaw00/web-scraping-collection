import sqlite3
import os
import datetime

class CourseDatabase:
    def __init__(self, db_name="courses.db"):
        self.db_name = db_name
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_name)

    def _init_db(self):
        """Initializes the courses database and table."""
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS courses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        provider TEXT NOT NULL,
                        course_id TEXT NOT NULL,
                        title TEXT NOT NULL,
                        description TEXT,
                        instructor TEXT,
                        schedule TEXT,
                        syllabus TEXT,
                        url TEXT,
                        scraped_at TEXT,
                        UNIQUE(provider, course_id)
                    )
                """)
        finally:
            conn.close()

    def upsert_course(self, provider, course_id, title, description, instructor, schedule, syllabus, url):
        """Inserts a new course or updates existing course information."""
        now = datetime.datetime.now().isoformat()
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO courses (provider, course_id, title, description, instructor, schedule, syllabus, url, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(provider, course_id) DO UPDATE SET
                        title=excluded.title,
                        description=excluded.description,
                        instructor=excluded.instructor,
                        schedule=excluded.schedule,
                        syllabus=excluded.syllabus,
                        url=excluded.url,
                        scraped_at=excluded.scraped_at
                """, (provider, course_id, title, description, instructor, schedule, syllabus, url, now))
        finally:
            conn.close()

    def get_courses(self, provider=None, search_query=None):
        """Retrieves courses filtered by provider and/or search query on title/description/syllabus."""
        query = "SELECT provider, course_id, title, description, instructor, schedule, syllabus, url, scraped_at FROM courses WHERE 1=1"
        params = []

        if provider:
            query += " AND provider = ?"
            params.append(provider)

        if search_query:
            query += " AND (title LIKE ? OR description LIKE ? OR syllabus LIKE ? OR course_id LIKE ?)"
            like_pattern = f"%{search_query}%"
            params.extend([like_pattern, like_pattern, like_pattern, like_pattern])

        conn = self._get_connection()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_all_providers(self):
        """Gets list of all distinct providers currently in the database."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT provider FROM courses")
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()

    def count_courses(self):
        """Returns the total number of courses in the database."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM courses")
            return cursor.fetchone()[0]
        finally:
            conn.close()
