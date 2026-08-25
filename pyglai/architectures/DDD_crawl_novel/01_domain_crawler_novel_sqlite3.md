Thiết kế Domain Model theo Domain-Driven Design (DDD) cho ứng dụng crawl truyện bằng Python và SQLite3 (dùng thuần SQL, không ORM).

## Kiến trúc thư mục (Layered Architecture)

Chia project thành 3 tầng chính để tách biệt logic domain với database và crawler:
    
    
    comic_crawler/
    │
    ├── domain/                  # Tầng Domain (Core Business Logic)
    │   ├── model.py             # Entities và Value Objects
    │   └── repository.py        # Abstract Repository (Interface)
    │
    ├── infrastructure/          # Tầng hạ tầng (SQLite thuần SQL)
    │   ├── database.py          # Khởi tạo kết nối & tạo bảng
    │   └── sqlite_repository.py # Implement các repository bằng SQL
    │
    └── main.py                  # Entry point chạy app
    

* * *

## 1\. Tầng Domain (`domain/model.py`)

Định nghĩa các Entity (có định danh/ID) và Value Object (bất biến, không có định danh) thuần Python, độc lập hoàn toàn với SQLite.
    
    
    from dataclasses import dataclass
    from datetime import datetime
    from typing import List, Optional
    
    # --- Value Objects ---
    @dataclass(frozen=True)
    class ChapterId:
        value: str  # Ví dụ: "uyen-uong-dai-luc-chuong-1"
    
    @dataclass(frozen=True)
    class ComicId:
        value: str  # Ví dụ: "uyen-uong-dai-luc"
    
    # --- Entities ---
    class Chapter:
        def __init__(self, id: ChapterId, comic_id: ComicId, number: int, title: str, content: str, created_at: datetime = None):
            self.id = id
            self.comic_id = comic_id
            self.number = number
            self.title = title
            self.content = content
            self.created_at = created_at or datetime.now()
    
        def update_content(self, new_content: str):
            if not new_content.strip():
                raise ValueError("Nội dung chương không được để trống")
            self.content = new_content
    
    class Comic:
        def __init__(self, id: ComicId, title: str, source_url: str, chapters: List[Chapter] = None):
            self.id = id
            self.title = title
            self.source_url = source_url
            self.chapters = chapters or []
    
        def add_chapter(self, chapter: Chapter):
            if any(c.id == chapter.id for c in self.chapters):
                return  # Tránh trùng lặp trong memory
            self.chapters.append(chapter)
    

* * *

## 2\. Định nghĩa Repository Interface (`domain/repository.py`)

Giao diện lưu trữ (Repository Pattern) giúp Domain không phụ thuộc vào SQLite.
    
    
    from abc import ABC, abstractmethod
    from typing import Optional, List
    from .model import Comic, ComicId, Chapter, ChapterId
    
    class ComicRepository(ABC):
        @abstractmethod
        def save(self, comic: Comic) -> None:
            pass
    
        @abstractmethod
        def get_by_id(self, comic_id: ComicId) -> Optional[Comic]:
            pass
    
    class ChapterRepository(ABC):
        @abstractmethod
        def save(self, chapter: Chapter) -> None:
            pass
    
        @abstractmethod
        def get_by_id(self, chapter_id: ChapterId) -> Optional[Chapter]:
            pass
    
        @abstractmethod
        def list_by_comic(self, comic_id: ComicId) -> List[Chapter]:
            pass
    

* * *

## 3\. Tầng Infrastructure - SQLite Thuần SQL (`infrastructure/sqlite_repository.py`)

Thực thi các interface bằng `sqlite3` thuần túy, dùng câu lệnh SQL truyền thống.

## Khởi tạo Database (`infrastructure/database.py`)
    
    
    import sqlite3
    
    def init_db(db_path: str = "comics.db"):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comics (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                source_url TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chapters (
                id TEXT PRIMARY KEY,
                comic_id TEXT NOT NULL,
                number INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (comic_id) REFERENCES comics(id)
            )
        """)
        conn.commit()
        conn.close()
    

## Implement Repository (`infrastructure/sqlite_repository.py`)
    
    
    import sqlite3
    from typing import Optional, List
    from domain.model import Comic, ComicId, Chapter, ChapterId
    from domain.repository import ComicRepository, ChapterRepository
    
    class SQLiteComicRepository(ComicRepository):
        def __init__(self, db_path: str):
            self.db_path = db_path
    
        def save(self, comic: Comic) -> None:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO comics (id, title, source_url) VALUES (?, ?, ?)",
                (comic.id.value, comic.title, comic.source_url)
            )
            conn.commit()
            conn.close()
    
        def get_by_id(self, comic_id: ComicId) -> Optional[Comic]:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, source_url FROM comics WHERE id = ?", (comic_id.value,))
            row = cursor.fetchone()
            conn.close()
            if not row:
                return None
            return Comic(id=ComicId(row[0]), title=row[1], source_url=row[2])
    
    class SQLiteChapterRepository(ChapterRepository):
        def __init__(self, db_path: str):
            self.db_path = db_path
    
        def save(self, chapter: Chapter) -> None:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO chapters (id, comic_id, number, title, content, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (chapter.id.value, chapter.comic_id.value, chapter.number, chapter.title, chapter.content, chapter.created_at.isoformat())
            )
            conn.commit()
            conn.close()
    
        def get_by_id(self, chapter_id: ChapterId) -> Optional[Chapter]:
            # Tương tự, viết lệnh SELECT theo chapter_id
            pass
    
        def list_by_comic(self, comic_id: ComicId) -> List[Chapter]:
            # Lấy danh sách chương theo comic_id
            return []
    

Nếu bạn muốn, tôi có thể hướng dẫn viết tiếp:

  * Tầng Application Service (điều phối tiến trình crawl từ web vào Repository)
  * Cách dùng lệnh SQL tối ưu để chống trùng lặp khi crawl nhiều luồng (Multi-threading)