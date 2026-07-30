"""
Data Tier (Tầng Dữ Liệu)

Tầng này chỉ làm việc với cơ sở dữ liệu qua SQL thuần, không chứa logic cào web.
"""

import sqlite3


class DBManager:
    def __init__(self, db_path="crawler.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Khởi tạo các bảng bằng SQL thuần"""
        query_stories = """
        CREATE TABLE IF NOT EXISTS stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            author TEXT,
            source TEXT
        );
        """
        query_chapters = """
        CREATE TABLE IF NOT EXISTS chapters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER,
            chapter_number REAL,
            title TEXT,
            content TEXT,
            FOREIGN KEY (story_id) REFERENCES stories (id)
        );
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query_stories)
            cursor.execute(query_chapters)
            conn.commit()

    def save_story(self, title, url, author, source):
        """Chèn hoặc bỏ qua nếu truyện đã tồn tại, trả về story_id"""
        query = "INSERT OR IGNORE INTO stories (title, url, author, source) VALUES (?, ?, ?, ?)"
        select_query = "SELECT id FROM stories WHERE url = ?"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (title, url, author, source))
            cursor.execute(select_query, (url,))
            row = cursor.fetchone()
            return row[0] if row else None

    def save_chapter(self, story_id, chapter_number, title, content):
        """Lưu chương truyện bằng SQL thuần"""
        query = "INSERT INTO chapters (story_id, chapter_number, title, content) VALUES (?, ?, ?, ?)"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (story_id, chapter_number, title, content))
            conn.commit()
