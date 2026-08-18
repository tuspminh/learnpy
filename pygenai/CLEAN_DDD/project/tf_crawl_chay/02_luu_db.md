Để chuyển đổi sang **SQLite3**, chúng ta sẽ thực hiện 2 bước chính theo đúng nguyên lý Clean Architecture:

1. **Tạo bảng DB & Adapter mới** trong tầng `infrastructure/storage.py` (thay thế cho JSON File Adapter).
2. **Cập nhật Dependency Injection** trong `main.py` để sử dụng Adapter mới mà **không cần chỉnh sửa bất kỳ dòng code nào** trong tầng `domain` hay `application`.

---

### 1. Thêm SQLite Adapter (`infrastructure/storage.py`)

Thêm lớp `SqliteNovelRepositoryAdapter` cài đặt giao diện `NovelRepositoryPort`:

```python
import sqlite3
import os
from domain.ports import NovelRepositoryPort
from domain.entities import Novel, Chapter
from domain.value_objects import Slug

class SqliteNovelRepositoryAdapter(NovelRepositoryPort):
    def __init__(self, db_path: str = "truyenfull.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self):
        """Khởi tạo cấu trúc bảng SQLite"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Bảng lưu thông tin Novel
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS novels (
                    slug TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    author TEXT,
                    description TEXT,
                    cover_url TEXT
                )
            """)
            
            # Bảng lưu thông tin Chapter
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chapters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    novel_slug TEXT NOT NULL,
                    chapter_number INTEGER NOT NULL,
                    title TEXT,
                    content TEXT,
                    FOREIGN KEY (novel_slug) REFERENCES novels(slug) ON DELETE CASCADE,
                    UNIQUE(novel_slug, chapter_number)
                )
            """)
            conn.commit()

    def save_novel(self, novel: Novel) -> None:
        """Lưu hoặc cập nhật thông tin Novel"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO novels (slug, title, author, description, cover_url)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(slug) DO UPDATE SET
                    title = excluded.title,
                    author = excluded.author,
                    description = excluded.description,
                    cover_url = excluded.cover_url
            """, (
                novel.slug.value,
                novel.title,
                novel.author,
                novel.description,
                novel.cover_url.value
            ))
            conn.commit()

    def save_chapter(self, novel_slug: Slug, chapter: Chapter) -> None:
        """Lưu hoặc cập nhật thông tin Chapter"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chapters (novel_slug, chapter_number, title, content)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(novel_slug, chapter_number) DO UPDATE SET
                    title = excluded.title,
                    content = excluded.content
            """, (
                novel_slug.value,
                chapter.number.value,
                chapter.title,
                chapter.content
            ))
            conn.commit()

```

---

### 2. Cập nhật Entrypoint (`main.py`)

Chỉ cần đổi `repository` thành `SqliteNovelRepositoryAdapter`:

```python
from infrastructure.http_fetcher import RequestsFetcherAdapter
from infrastructure.parsers import BeautifulSoupTruyenFullParserAdapter
from infrastructure.storage import SqliteNovelRepositoryAdapter  # Import Adapter mới
from application.use_cases import CrawlNovelUseCase, CrawlListingUseCase

def main():
    BASE_URL = "https://truyenfull.live"

    # Dependency Injection Setup
    fetcher = RequestsFetcherAdapter()
    parser = BeautifulSoupTruyenFullParserAdapter()
    
    # Thay thế JSON Adapter bằng SQLite Adapter
    repository = SqliteNovelRepositoryAdapter(db_path="truyenfull.db")

    # Inject Use Cases (Giữ nguyên không đổi)
    crawl_novel_uc = CrawlNovelUseCase(
        base_url=BASE_URL,
        fetcher=fetcher,
        parser=parser,
        repository=repository
    )
    
    crawl_listing_uc = CrawlListingUseCase(
        base_url=BASE_URL,
        fetcher=fetcher,
        parser=parser,
        crawl_novel_uc=crawl_novel_uc
    )

    # Thực thi crawl
    print("Starting novel crawl into SQLite...")
    crawl_novel_uc.execute("dau-la-dai-luc")

if __name__ == "__main__":
    main()

```

---

### Cấu trúc cơ sở dữ liệu được tạo tự động:

* **Bảng `novels**`:
* `slug` (TEXT PRIMARY KEY)
* `title` (TEXT)
* `author` (TEXT)
* `description` (TEXT)
* `cover_url` (TEXT)


* **Bảng `chapters**`:
* `id` (INTEGER PRIMARY KEY)
* `novel_slug` (TEXT, Khóa ngoại tham chiếu `novels.slug`)
* `chapter_number` (INTEGER)
* `title` (TEXT)
* `content` (TEXT)
* Ràng buộc duy nhất `UNIQUE(novel_slug, chapter_number)` đảm bảo không bị trùng lặp chương khi crawl lại.