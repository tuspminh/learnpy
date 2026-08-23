Để thiết kế phần **Database / Persistence Infrastructure** tuân thủ nghiêm ngặt **Clean Architecture** và **Domain-Driven Design (DDD)**, chúng ta cần phân tách rõ ràng giữa **Domain State (Entities/Value Objects)** và **Persistence State (Database Tables/Schema)**.

Trong DDD, Database chỉ là một **Detail** nằm ở lớp ngoài cùng (**Infrastructure**). Lớp Domain bên trong không được phép phụ thuộc vào bất kỳ khái niệm DB nào (như khóa ngoại, kiểu dữ liệu SQL, ORM, v.v.).

---

### 1. Nguyên tắc thiết kế Database trong Clean & DDD

1. **Persistence Ignorance**: Domain Model chỉ chứa logic nghiệp vụ và trạng thái thuần Python (`dataclass`), không chứa decorator/mapping của DB (như SQLAlchemy Base).
2. **Data Mapper Pattern**: Tạo lớp Mapper chuyển đổi (mapping) giữa **Domain Entity** $\leftrightarrow$ **Database Record (DTO/Row)**.
3. **Optimized Persistence Schema**: Thiết kế Bảng (Tables) chuẩn hóa, đánh Index tối ưu cho truy vấn đọc/ghi.
4. **Data Integrity (Thuần SQL)**: Sử dụng các ràng buộc SQLite (`FOREIGN KEY`, `UNIQUE`, `CHECK`, `COMPOSITE PRIMARY KEY`) để bảo vệ toàn vẹn dữ liệu ở tầng lưu trữ.

---

### 2. Thiết kế Cơ sở Dữ liệu Schema (SQLite)

Database hỗ trợ các luồng lưu trữ: **Listing**, **Novel** (thông tin + tiến trình cào), và **Chapter** (nội dung chương).

```sql
-- Thao tác khởi tạo schema (ddl.sql)

-- 1. Bảng Novels (Lưu trữ Aggregate Root Novel)
CREATE TABLE IF NOT EXISTS novels (
    slug TEXT PRIMARY KEY,                  -- Slug unique định danh Novel
    title TEXT NOT NULL,                    -- Tên truyện
    author TEXT,                            -- Tác giả
    cover_url TEXT,                         -- Ảnh bìa
    description TEXT,                       -- Mô tả truyện
    status TEXT NOT NULL DEFAULT 'ONGOING', -- Trạng thái: ONGOING, COMPLETED
    total_chapters INTEGER NOT NULL DEFAULT 0,   -- Tổng số chương phát hiện trên Web
    crawled_chapters INTEGER NOT NULL DEFAULT 0, -- Số chương đã cào thành công
    created_at TEXT NOT NULL,               -- Thời gian tạo bản ghi (ISO8601)
    updated_at TEXT NOT NULL,               -- Thời gian cập nhật gần nhất (ISO8601)
    
    CHECK (status IN ('ONGOING', 'COMPLETED')),
    CHECK (total_chapters >= 0),
    CHECK (crawled_chapters >= 0)
);

-- Index phục vụ Use Case: Cào danh sách novel chưa xong/chưa full
CREATE INDEX IF NOT EXISTS idx_novels_crawl_status 
ON novels(status, crawled_chapters, total_chapters, updated_at);


-- 2. Bảng Chapters (Lưu trữ Entity Chapter)
CREATE TABLE IF NOT EXISTS chapters (
    novel_slug TEXT NOT NULL,               -- Foreign key tham chiếu tới novels.slug
    chapter_no INTEGER NOT NULL,            -- Thứ tự chương trong truyện (1, 2, 3...)
    slug TEXT NOT NULL,                     -- Slug của chương (/novel-slug/chuong-2)
    title TEXT NOT NULL,                    -- Tiêu đề chương
    content TEXT,                           -- Nội dung chương (có thể NULL nếu cào lỗi/chưa lấy nội dung)
    created_at TEXT NOT NULL,               -- Thời gian cào/tạo bản ghi
    
    PRIMARY KEY (novel_slug, chapter_no),   -- Composite Primary Key đảm bảo không trùng số chương trong 1 truyện
    FOREIGN KEY (novel_slug) REFERENCES novels(slug) ON DELETE CASCADE
);

-- Index phục vụ tra cứu nhanh danh sách chương của 1 novel
CREATE INDEX IF NOT EXISTS idx_chapters_novel_slug 
ON chapters(novel_slug, chapter_no);

```

---

### 3. Triển khai Cấu trúc Tầng Persistence (Python)

#### `infrastructure/database/connection.py`

Quản lý kết nối Database và cấu hình SQLite Pragma.

```python
import sqlite3
from contextlib import contextmanager
from typing import Generator

class DatabaseConnectionFactory:
    """Factory khởi tạo và quản lý kết nối SQLite."""
    
    def __init__(self, db_path: str = "truyenfull.db"):
        self._db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            self._db_path,
            timeout=20.0,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        conn.row_factory = sqlite3.Row  # Cho phép truy cập cột theo tên
        # Bật Ràng buộc Khóa ngoại (Foreign Keys) cho SQLite
        conn.execute("PRAGMA foreign_keys = ON;")
        # Bật chế độ WAL để tăng hiệu năng ghi/đọc đồng thời
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager quản lý Transaction tự động Commit/Rollback."""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

```

---

#### `infrastructure/database/mappers.py`

Lớp Data Mapper chuyển đổi qua lại giữa **Database Row (DTO)** và **Domain Model**. Giúp bảo vệ Domain không bị ảnh hưởng khi Schema DB thay đổi.

```python
from datetime import datetime, timezone
import sqlite3
from tfcrawler.domain.models import Novel, Chapter, ChapterIdentity, NovelStatus

class NovelDataMapper:
    """Chuyển đổi dữ liệu giữa SQLite Row và Domain Model Novel."""
    
    @staticmethod
    def to_domain(row: sqlite3.Row) -> Novel:
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

    @staticmethod
    def to_persistence(novel: Novel) -> dict:
        return {
            "slug": novel.slug,
            "title": novel.title,
            "author": novel.author,
            "cover_url": novel.cover_url,
            "description": novel.description,
            "status": novel.status.value,
            "total_chapters": novel.total_chapters,
            "crawled_chapters": novel.crawled_chapters,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": novel.updated_at.isoformat()
        }


class ChapterDataMapper:
    """Chuyển đổi dữ liệu giữa SQLite Row và Domain Model Chapter."""

    @staticmethod
    def to_domain(row: sqlite3.Row) -> Chapter:
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

    @staticmethod
    def to_persistence(chapter: Chapter) -> dict:
        return {
            "novel_slug": chapter.novel_slug,
            "chapter_no": chapter.chapter_no,
            "slug": chapter.slug,
            "title": chapter.title,
            "content": chapter.content,
            "created_at": chapter.created_at.isoformat()
        }

```

---

#### `infrastructure/database/repositories.py`

Hiện thực hóa Repository Interfaces (ở lớp Domain) bằng SQL thuần.

```python
import sqlite3
from typing import List, Optional

from tfcrawler.domain.models import Novel, Chapter, ChapterIdentity
from tfcrawler.domain.repositories import NovelRepository, ChapterRepository
from tfcrawler.infrastructure.database.mappers import NovelDataMapper, ChapterDataMapper


class SQLiteNovelRepository(NovelRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def save(self, novel: Novel) -> None:
        """Upsert thông tin Novel vào Database bằng Thuần SQL."""
        data = NovelDataMapper.to_persistence(novel)
        sql = """
            INSERT INTO novels (
                slug, title, author, cover_url, description, 
                status, total_chapters, crawled_chapters, created_at, updated_at
            ) VALUES (
                :slug, :title, :author, :cover_url, :description, 
                :status, :total_chapters, :crawled_chapters, :created_at, :updated_at
            )
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
            self._conn.execute(sql, data)

    def get_by_slug(self, slug: str) -> Optional[Novel]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM novels WHERE slug = ?", (slug,))
        row = cursor.fetchone()
        return NovelDataMapper.to_domain(row) if row else None

    def find_incomplete_novels(self, limit: int) -> List[Novel]:
        """Lấy danh sách Novel chưa cào xong hoặc chưa full (status = ONGOING)."""
        sql = """
            SELECT * FROM novels
            WHERE status = 'ONGOING' OR crawled_chapters < total_chapters
            ORDER BY updated_at ASC
            LIMIT ?;
        """
        cursor = self._conn.cursor()
        cursor.execute(sql, (limit,))
        return [NovelDataMapper.to_domain(row) for row in cursor.fetchall()]


class SQLiteChapterRepository(ChapterRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def save(self, chapter: Chapter) -> None:
        """Upsert thông tin Chapter vào Database bằng Thuần SQL."""
        data = ChapterDataMapper.to_persistence(chapter)
        sql = """
            INSERT INTO chapters (
                novel_slug, chapter_no, slug, title, content, created_at
            ) VALUES (
                :novel_slug, :chapter_no, :slug, :title, :content, :created_at
            )
            ON CONFLICT(novel_slug, chapter_no) DO UPDATE SET
                slug = excluded.slug,
                title = excluded.title,
                content = excluded.content;
        """
        with self._conn:
            self._conn.execute(sql, data)

    def get_by_identity(self, identity: ChapterIdentity) -> Optional[Chapter]:
        sql = "SELECT * FROM chapters WHERE novel_slug = ? AND chapter_no = ?"
        cursor = self._conn.cursor()
        cursor.execute(sql, (identity.novel_slug, identity.chapter_no))
        row = cursor.fetchone()
        return ChapterDataMapper.to_domain(row) if row else None

    def exists(self, identity: ChapterIdentity) -> bool:
        sql = "SELECT 1 FROM chapters WHERE novel_slug = ? AND chapter_no = ?"
        cursor = self._conn.cursor()
        cursor.execute(sql, (identity.novel_slug, identity.chapter_no))
        return cursor.fetchone() is not None

    def get_max_chapter_no(self, novel_slug: str) -> int:
        sql = "SELECT COALESCE(MAX(chapter_no), 0) FROM chapters WHERE novel_slug = ?"
        cursor = self._conn.cursor()
        cursor.execute(sql, (novel_slug,))
        return cursor.fetchone()[0]

```

---

### 4. Bảng tóm tắt Kiến trúc Database theo Clean & DDD

| Khái niệm | Vị trí trong hệ thống | Vai trò & Đặc điểm |
| --- | --- | --- |
| **Domain Entity** | `domain/models.py` | Chứa dữ liệu & logic nghiệp vụ. Không phụ thuộc vào SQL. |
| **Repository Interface** | `domain/repositories.py` | Khai báo các hợp đồng (Contracts) thao tác dữ liệu theo góc nhìn Domain. |
| **Data Mapper** | `infrastructure/database/mappers.py` | Chuyển đổi hai chiều giữa SQL Rows và Domain Objects. Tách biệt DB Schema với Domain. |
| **Concrete Repository** | `infrastructure/database/repositories.py` | Thực thi truy vấn SQL thuần (`INSERT`, `UPDATE`, `SELECT`) và quản lý Transaction. |
| **Database Schema** | `infrastructure/database/schema.sql` | Quản lý cấu trúc Bảng, Ràng buộc dữ liệu (Check/FK) và Index trong SQLite. |