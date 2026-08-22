Dưới đây là thiết kế chuyên sâu riêng cho phần **Domain Models** và **Repositories** theo chuẩn Clean Architecture & DDD (Domain-Driven Design), tách biệt hoàn toàn giữa **Domain Specification** (độc lập thư viện) và **Infrastructure Implementation** (SQLite thuần SQL).

---

### 1. Domain Layer (`domain/`)

Tập trung vào nghiệp vụ cốt lõi: Value Objects, Aggregate Root, Entities và Repository Interfaces.

#### **Value Objects & Aggregate Root** (`domain/models.py`)

```python
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional


class NovelStatus(str, Enum):
    ONGOING = "ongoing"
    COMPLETED = "completed"


@dataclass(frozen=True)
class ChapterIdentity:
    """Value Object xác định danh tính duy nhất của một Chapter."""
    novel_slug: str
    chapter_no: int


@dataclass
class Chapter:
    """Entity Chapter đại diện cho nội dung một chương."""
    identity: ChapterIdentity
    slug: str
    title: str
    content: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def novel_slug(self) -> str:
        return self.identity.novel_slug

    @property
    def chapter_no(self) -> int:
        return self.identity.chapter_no


@dataclass
class Novel:
    """Aggregate Root quản lý toàn bộ vòng đời và tiến trình cào của truyện."""
    slug: str
    title: str
    author: Optional[str] = None
    cover_url: Optional[str] = None
    description: Optional[str] = None
    status: NovelStatus = NovelStatus.ONGOING
    total_chapters: int = 0
    crawled_chapters: int = 0
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def update_progress(self, crawled_count: int) -> None:
        """Domain Method: Cập nhật tiến trình cào chương."""
        if crawled_count > self.crawled_chapters:
            self.crawled_chapters = crawled_count
            self.updated_at = datetime.now(timezone.utc)

    def mark_completed(self) -> None:
        """Domain Method: Đánh dấu truyện đã hoàn thành."""
        self.status = NovelStatus.COMPLETED
        self.updated_at = datetime.now(timezone.utc)

    @property
    def is_fully_crawled(self) -> bool:
        """Kiểm tra xem đã cào xong toàn bộ chương hiện có chưa."""
        return self.crawled_chapters >= self.total_chapters and self.total_chapters > 0

```

#### **Repository Interfaces** (`domain/repositories.py`)

Thao tác dữ liệu dưới dạng các tập hợp (Collections) domain objects, không lộ chi tiết truy vấn DB.

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from tfcrawler.domain.models import Novel, Chapter, ChapterIdentity


class NovelRepository(ABC):
    """Abstract Interface quản lý việc lưu trữ Aggregate Root Novel."""

    @abstractmethod
    def save(self, novel: Novel) -> None:
        """Thêm mới hoặc cập nhật thông tin Novel (Upsert)."""
        pass

    @abstractmethod
    def get_by_slug(self, slug: str) -> Optional[Novel]:
        """Lấy Novel theo Slug."""
        pass

    @abstractmethod
    def find_incomplete_novels(self, limit: int) -> List[Novel]:
        """Lấy danh sách các Novel chưa cào xong hoặc chưa hoàn thành (Ongoing)."""
        pass


class ChapterRepository(ABC):
    """Abstract Interface quản lý lưu trữ Entity Chapter."""

    @abstractmethod
    def save(self, chapter: Chapter) -> None:
        """Lưu hoặc cập nhật một Chapter."""
        pass

    @abstractmethod
    def get_by_identity(self, identity: ChapterIdentity) -> Optional[Chapter]:
        """Lấy thông tin Chapter theo Composite Key."""
        pass

    @abstractmethod
    def exists(self, identity: ChapterIdentity) -> bool:
        """Kiểm tra xem Chapter đã tồn tại trong DB chưa."""
        pass

    @abstractmethod
    def get_max_chapter_no(self, novel_slug: str) -> int:
        """Lấy thứ tự chương lớn nhất hiện có của một Novel."""
        pass

```

---

### 2. Infrastructure Layer (`infrastructure/`)

Hiện thực hóa Repositories bằng **SQLite thuần SQL** (dùng `sqlite3` trong thư viện chuẩn Python).

#### **Database Initializer** (`infrastructure/database.py`)

```python
import sqlite3

DDL_NOVELS = """
CREATE TABLE IF NOT EXISTS novels (
    slug TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    cover_url TEXT,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'ongoing',
    total_chapters INTEGER NOT NULL DEFAULT 0,
    crawled_chapters INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL
);
"""

DDL_CHAPTERS = """
CREATE TABLE IF NOT EXISTS chapters (
    novel_slug TEXT NOT NULL,
    chapter_no INTEGER NOT NULL,
    slug TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    created_at TEXT NOT NULL,
    PRIMARY KEY (novel_slug, chapter_no),
    FOREIGN KEY (novel_slug) REFERENCES novels(slug) ON DELETE CASCADE
);
"""

DDL_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_novels_status_progress 
ON novels(status, crawled_chapters, total_chapters);
"""


def init_sqlite_db(db_path: str = "truyenfull.db") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    with conn:
        conn.execute(DDL_NOVELS)
        conn.execute(DDL_CHAPTERS)
        conn.execute(DDL_INDEXES)
    return conn

```

#### **Concrete Repositories** (`infrastructure/sqlite_repository.py`)

```python
import sqlite3
from datetime import datetime, timezone
from typing import List, Optional

from tfcrawler.domain.models import Novel, NovelStatus, Chapter, ChapterIdentity
from tfcrawler.domain.repositories import NovelRepository, ChapterRepository


class SQLiteNovelRepository(NovelRepository):
    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection

    def save(self, novel: Novel) -> None:
        query = """
        INSERT INTO novels (
            slug, title, author, cover_url, description, 
            status, total_chapters, crawled_chapters, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(slug) DO UPDATE SET
            title = excluded.title,
            author = COALESCE(excluded.author, novels.author),
            cover_url = COALESCE(excluded.cover_url, novels.cover_url),
            description = COALESCE(excluded.description, novels.description),
            status = excluded.status,
            total_chapters = excluded.total_chapters,
            crawled_chapters = excluded.crawled_chapters,
            updated_at = excluded.updated_at;
        """
        with self._conn:
            self._conn.execute(query, (
                novel.slug,
                novel.title,
                novel.author,
                novel.cover_url,
                novel.description,
                novel.status.value,
                novel.total_chapters,
                novel.crawled_chapters,
                novel.updated_at.isoformat()
            ))

    def get_by_slug(self, slug: str) -> Optional[Novel]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM novels WHERE slug = ?", (slug,))
        row = cursor.fetchone()
        return self._map_row_to_novel(row) if row else None

    def find_incomplete_novels(self, limit: int) -> List[Novel]:
        query = """
        SELECT * FROM novels
        WHERE status = 'ongoing' OR crawled_chapters < total_chapters
        ORDER BY updated_at ASC
        LIMIT ?;
        """
        cursor = self._conn.cursor()
        cursor.execute(query, (limit,))
        return [self._map_row_to_novel(row) for row in cursor.fetchall()]

    @staticmethod
    def _map_row_to_novel(row: sqlite3.Row) -> Novel:
        return Novel(
            slug=row["slug"],
            title=row["title"],
            author=row["author"],
            cover_url=row["cover_url"],
            description=row["description"],
            status=NovelStatus(row["status"]),
            total_chapters=row["total_chapters"],
            crawled_chapters=row["crawled_chapters"],
            updated_at=datetime.fromisoformat(row["updated_at"])
        )


class SQLiteChapterRepository(ChapterRepository):
    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection

    def save(self, chapter: Chapter) -> None:
        query = """
        INSERT INTO chapters (
            novel_slug, chapter_no, slug, title, content, created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(novel_slug, chapter_no) DO UPDATE SET
            slug = excluded.slug,
            title = excluded.title,
            content = excluded.content;
        """
        with self._conn:
            self._conn.execute(query, (
                chapter.novel_slug,
                chapter.chapter_no,
                chapter.slug,
                chapter.title,
                chapter.content,
                chapter.created_at.isoformat()
            ))

    def get_by_identity(self, identity: ChapterIdentity) -> Optional[Chapter]:
        query = "SELECT * FROM chapters WHERE novel_slug = ? AND chapter_no = ?"
        cursor = self._conn.cursor()
        cursor.execute(query, (identity.novel_slug, identity.chapter_no))
        row = cursor.fetchone()
        return self._map_row_to_chapter(row) if row else None

    def exists(self, identity: ChapterIdentity) -> bool:
        query = "SELECT 1 FROM chapters WHERE novel_slug = ? AND chapter_no = ?"
        cursor = self._conn.cursor()
        cursor.execute(query, (identity.novel_slug, identity.chapter_no))
        return cursor.fetchone() is not None

    def get_max_chapter_no(self, novel_slug: str) -> int:
        query = "SELECT MAX(chapter_no) FROM chapters WHERE novel_slug = ?"
        cursor = self._conn.cursor()
        cursor.execute(query, (novel_slug,))
        result = cursor.fetchone()[0]
        return result if result is not None else 0

    @staticmethod
    def _map_row_to_chapter(row: sqlite3.Row) -> Chapter:
        return Chapter(
            identity=ChapterIdentity(
                novel_slug=row["novel_slug"],
                chapter_no=row["chapter_no"]
            ),
            slug=row["slug"],
            title=row["title"],
            content=row["content"],
            created_at=datetime.fromisoformat(row["created_at"])
        )

```

---

### Nguyên lý thiết kế đạt được

| Nguyên lý | Áp dụng trong thiết kế |
| --- | --- |
| **SRP** (Single Responsibility) | `Novel` quản lý trạng thái truyện; `SQLiteNovelRepository` chỉ đảm nhận lưu trữ SQL. |
| **DIP** (Dependency Inversion) | Các lớp Application/Use Cases phụ thuộc vào `NovelRepository` (Abstract), không dính trực tiếp vào SQLite. |
| **DDD Aggregate Root** | `Novel` đóng vai trò Aggregate Root duy nhất điều phối thông tin số lượng chương (`crawled_chapters`). |
| **Value Object Pattern** | `ChapterIdentity` đảm bảo tính toàn vẹn của Khóa chính tổng hợp (`novel_slug`, `chapter_no`). |