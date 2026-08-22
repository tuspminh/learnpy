Thiết kế riêng cho 2 thành phần **Database Connection Manager** và **Data Mapper** tuân thủ nguyên lý **Clean Architecture** và **DDD**.

Trong Clean Architecture, hai lớp này nằm hoàn toàn ở tầng **Infrastructure**, đóng vai trò là "cầu nối" kỹ thuật giữa thế giới lưu trữ (Database Schema) và thế giới nghiệp vụ (Domain Entities).

---

### 1. Database Connection Manager (`infrastructure/database/connection.py`)

Thành phần này chịu trách nhiệm:

* Quản lý vòng đời kết nối SQLite (thread-safe, WAL mode).
* Cung cấp **Transaction Context Manager** để đảm bảo tính **ACID** cho các thao tác ghi.
* Tách biệt hoàn toàn việc khởi tạo và đóng kết nối khỏi nghiệp vụ.

```python
import sqlite3
from contextlib import contextmanager
from typing import Generator


class DatabaseConnectionFactory:
    """Factory khởi tạo và cấu hình tối ưu cho kết nối SQLite."""

    def __init__(self, db_path: str = "truyenfull.db"):
        self._db_path = db_path

    def create_connection(self) -> sqlite3.Connection:
        """Tạo kết nối đơn lẻ với các Pragma tối ưu hiệu năng và tính toàn vẹn."""
        conn = sqlite3.connect(
            self._db_path,
            timeout=30.0,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )
        # Cho phép truy cập cột bằng tên (row["title"])
        conn.row_factory = sqlite3.Row
        
        # Bật Ràng buộc Khóa ngoại (Foreign Keys)
        conn.execute("PRAGMA foreign_keys = ON;")
        # Chế độ WAL (Write-Ahead Logging) giúp tăng tốc độ ghi/đọc đồng thời
        conn.execute("PRAGMA journal_mode = WAL;")
        # Đồng bộ hóa dữ liệu an toàn
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn


class SQLiteUnitOfWork:
    """Transaction Manager giúp kiểm soát Commit / Rollback tự động (Unit of Work)."""

    def __init__(self, connection_factory: DatabaseConnectionFactory):
        self._factory = connection_factory

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Context Manager quản lý một Transaction an toàn."""
        conn = self._factory.create_connection()
        try:
            yield conn
            conn.commit()
        except Exception as err:
            conn.rollback()
            raise err
        finally:
            conn.close()

```

---

### 2. Data Mapper (`infrastructure/database/mappers.py`)

Áp dụng mẫu thiết kế **Data Mapper Pattern**. Lớp này hoàn toàn chịu trách nhiệm dịch chuyển dữ liệu 2 chiều:

1. **`to_domain`**: Chuyển SQLite Row (Raw Data) $\rightarrow$ Domain Entity / Aggregate Root.
2. **`to_persistence`**: Chuyển Domain Entity / Aggregate Root $\rightarrow$ Dictionary (SQL Payload).

Nhờ có Mapper, khi cấu hình bảng SQLite hay kiểu dữ liệu DB thay đổi, bạn chỉ cần sửa ở đây mà **không chạm vào bất kỳ dòng code Domain hay Application nào**.

```python
from datetime import datetime, timezone
import sqlite3
from typing import Any, Dict

from tfcrawler.domain.models import Chapter, ChapterIdentity, Novel, NovelStatus


class NovelDataMapper:
    """Mapper chuyển đổi dữ liệu hai chiều cho Aggregate Root Novel."""

    @staticmethod
    def to_domain(row: sqlite3.Row) -> Novel:
        """Chuyển đổi từ SQLite Row sang Domain Model Novel."""
        return Novel(
            slug=row["slug"],
            title=row["title"],
            author=row["author"],
            cover_url=row["cover_url"],
            description=row["description"],
            status=NovelStatus(row["status"]),
            total_chapters=row["total_chapters"],
            crawled_chapters=row["crawled_chapters"],
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    @staticmethod
    def to_persistence(novel: Novel) -> Dict[str, Any]:
        """Chuyển đổi từ Domain Model Novel sang Dictionary phục vụ SQL Params."""
        return {
            "slug": novel.slug,
            "title": novel.title,
            "author": novel.author,
            "cover_url": novel.cover_url,
            "description": novel.description,
            "status": novel.status.value,
            "total_chapters": novel.total_chapters,
            "crawled_chapters": novel.crawled_chapters,
            "updated_at": novel.updated_at.isoformat(),
        }


class ChapterDataMapper:
    """Mapper chuyển đổi dữ liệu hai chiều cho Entity Chapter."""

    @staticmethod
    def to_domain(row: sqlite3.Row) -> Chapter:
        """Chuyển đổi từ SQLite Row sang Domain Model Chapter."""
        return Chapter(
            identity=ChapterIdentity(
                novel_slug=row["novel_slug"],
                chapter_no=row["chapter_no"],
            ),
            slug=row["slug"],
            title=row["title"],
            content=row["content"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    @staticmethod
    def to_persistence(chapter: Chapter) -> Dict[str, Any]:
        """Chuyển đổi từ Domain Model Chapter sang Dictionary phục vụ SQL Params."""
        return {
            "novel_slug": chapter.novel_slug,
            "chapter_no": chapter.chapter_no,
            "slug": chapter.slug,
            "title": chapter.title,
            "content": chapter.content,
            "created_at": chapter.created_at.isoformat(),
        }

```

---

### 3. Ví dụ phối hợp Connection Manager + Mapper trong Repository

Dưới đây là cách hai thành phần trên kết hợp lại bên trong một Repository thuần SQL:

```python
from typing import Optional
from tfcrawler.domain.models import Novel
from tfcrawler.domain.repositories import NovelRepository
from tfcrawler.infrastructure.database.connection import DatabaseConnectionFactory
from tfcrawler.infrastructure.database.mappers import NovelDataMapper


class SQLiteNovelRepository(NovelRepository):
    def __init__(self, connection_factory: DatabaseConnectionFactory):
        self._factory = connection_factory

    def save(self, novel: Novel) -> None:
        """Lưu hoặc cập nhật Novel sử dụng Mapper và Connection Manager."""
        payload = NovelDataMapper.to_persistence(novel)
        sql = """
            INSERT INTO novels (
                slug, title, author, cover_url, description,
                status, total_chapters, crawled_chapters, updated_at
            ) VALUES (
                :slug, :title, :author, :cover_url, :description,
                :status, :total_chapters, :crawled_chapters, :updated_at
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
        # Sử dụng Connection Factory để tự động quản lý kết nối an toàn
        conn = self._factory.create_connection()
        with conn:
            conn.execute(sql, payload)
        conn.close()

    def get_by_slug(self, slug: str) -> Optional[Novel]:
        """Lấy thông tin và dùng Mapper dịch sang Domain Model."""
        sql = "SELECT * FROM novels WHERE slug = ?"
        conn = self._factory.create_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (slug,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # Dịch dữ liệu thô sang Domain Entity thông qua Data Mapper
        return NovelDataMapper.to_domain(row)

```

### Điểm mạnh của thiết kế này:

1. **Ranh giới rõ ràng**: `sqlite3.Row` hay cấu trúc SQLite không bao giờ "lọt" vào tầng Domain hay Application.
2. **Transaction An toàn**: Tự động dọn dẹp kết nối và Rollback khi gặp lỗi qua `SQLiteUnitOfWork`.
3. **Dễ Kiểm Thử (Testability)**: Bạn dễ dàng mock `DatabaseConnectionFactory` hoặc truyền vào đường dẫn DB `:memory:` khi chạy Unit Test.