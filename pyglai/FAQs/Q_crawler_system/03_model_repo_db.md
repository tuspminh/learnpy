Version:0.9 StartHTML:0000000105 EndHTML:0000079020 StartFragment:0000000141 EndFragment:0000078984 

Q:
    
    
    ├── database/
    │   ├── database.py
    │   ├── migrations.py
    │   └── schema.py
    ├── models/
    │ ├── novel.py
    │ ├── chapter.py
    │ ├── task.py
    │ ├── website.py
    │ └── ...
    ├── repositories/
    │ ├── base_repository.py
    │ ├── novel_repository.py
    │ ├── chapter_repository.py
    │ ├── task_repository.py
    │ └── ..database/ 
    │ ├── __init__.py 
    │ ├── database.py 
    │ ├── connection.py 
    │ ├── migrations.py
    │ ├── schema.py 
    │ ├── transaction.py 
    │ └── version.py

## GLAI: SQLALchemy

Để tích hợp hệ thống lưu trữ dữ liệu bền vững (Persistence Layer) cho Crawler theo chuẩn kiến trúc **Repository Pattern** , chúng ta sẽ sử dụng **SQLite** kết hợp thư viện **SQLAlchemy** (phiên bản 2.0 trở lên). Việc tách biệt rõ ràng giữa Database Connection, DB Schema, Data Model và Repositories giúp hệ thống của bạn mở rộng cực kỳ dễ dàng (ví dụ: chuyển đổi từ SQLite sang MySQL hay PostgreSQL sau này chỉ mất 1 dòng code cấu hình).

Dưới đây là mã nguồn tối ưu, đồng bộ và đầy đủ cho kiến trúc thư mục bạn yêu cầu.

* * *

**📦 1. TẦNG DATABASE (Cấu hình, Kết nối & Giao dịch)**

**📄 database/connection.py**

Nơi chịu trách nhiệm quản lý Connection Pool và tạo Engine kết nối Database.

python
    
    
    import os
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Đường dẫn lưu file SQLite tại thư mục gốc dự án
    DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../crawler.db"))
    DATABASE_URL = f"sqlite:///{DB_PATH}"
    
    # Tạo Engine (Bật tính năng check_same_thread=False để dùng được đa luồng cho SQLite)
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},
        pool_pre_ping=True
    )
    
    # Cấu hình Factory để sinh Session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    

Hãy thận trọng khi sử dụng mã.

**📄 database/transaction.py**

Quản lý vòng đời của Session dựa trên lập trình ngữ cảnh (Context Manager) để tự động `commit` khi thành công hoặc `rollback` khi gặp lỗi.

python
    
    
    from contextlib import contextmanager
    from typing import Generator
    from sqlalchemy.orm import Session
    from .connection import SessionLocal
    
    @contextmanager
    def transaction_scope() -> Generator[Session, None, None]:
        """Cung cấp một Session làm việc an toàn cho các tác vụ thay đổi dữ liệu."""
        session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    

Hãy thận trọng khi sử dụng mã.

**📄 database/schema.py**

Định nghĩa Base Class cho SQLAlchemy để các Models kế thừa cấu hình bảng.

python
    
    
    from sqlalchemy.orm import DeclarativeBase
    
    class Base(DeclarativeBase):
        """Lớp nền tảng ánh xạ Object - Relational (ORM)"""
        pass
    

Hãy thận trọng khi sử dụng mã.

**📄 database/database.py**

Điểm gom cấu hình và cung cấp API tạo bảng nhanh gọn.

python
    
    
    from .connection import engine
    from .schema import Base
    
    def init_db() -> None:
        """Tạo toàn bộ cấu trúc bảng nếu chưa tồn tại trong Database."""
        # Nạp toàn bộ models vào context trước khi tạo bảng
        import models.website
        import models.novel
        import models.chapter
        import models.task
        
        Base.metadata.create_all(bind=engine)
    

Hãy thận trọng khi sử dụng mã.

* * *

**📦 2. TẦNG MODELS (Định nghĩa thực thể & mối quan hệ)**

**📄 models/website.py**

python
    
    
    from sqlalchemy import String
    from sqlalchemy.orm import Mapped, mapped_column, relationship
    from database.schema import Base
    
    class Website(Base):
        __tablename__ = "websites"
    
        id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
        name: Mapped[str] = mapped_column(String(100), nullable=False)
        base_url: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    
        # Quan hệ 1 - Nhiều: Một website chứa nhiều truyện
        novels = relationship("Novel", back_populates="website", cascade="all, delete-orphan")
    

Hãy thận trọng khi sử dụng mã.

**📄 models/novel.py**

python
    
    
    from datetime import datetime
    from sqlalchemy import String, ForeignKey, DateTime
    from sqlalchemy.orm import Mapped, mapped_column, relationship
    from database.schema import Base
    
    class Novel(Base):
        __tablename__ = "novels"
    
        id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
        website_id: Mapped[int] = mapped_column(ForeignKey("websites.id"), nullable=False)
        title: Mapped[str] = mapped_column(String(255), nullable=False)
        slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
        author: Mapped[str] = mapped_column(String(100), default="Không rõ")
        status: Mapped[str] = mapped_column(String(50), default="Đang tiến hành")
        genres: Mapped[str] = mapped_column(String(255), default="")  # Lưu dạng chuỗi ngăn cách bởi dấu phẩy
        description: Mapped[str] = mapped_column(String, default="")
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
        # Các mối quan hệ liên kết bảng
        website = relationship("Website", back_populates="novels")
        chapters = relationship("Chapter", back_populates="novel", cascade="all, delete-orphan")
    

Hãy thận trọng khi sử dụng mã.

**📄 models/chapter.py**

python
    
    
    from sqlalchemy import String, ForeignKey, Integer
    from sqlalchemy.orm import Mapped, mapped_column, relationship
    from database.schema import Base
    
    class Chapter(Base):
        __tablename__ = "chapters"
    
        id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
        novel_id: Mapped[int] = mapped_column(ForeignKey("novels.id"), nullable=False)
        title: Mapped[str] = mapped_column(String(255), nullable=False)
        url: Mapped[str] = mapped_column(String(500), nullable=False)
        order_index: Mapped[int] = mapped_column(Integer, default=0)  # Thứ tự chương
        content: Mapped[str] = mapped_column(String, default="")       # Nội dung text chữ của truyện
    
        novel = relationship("Novel", back_populates="chapters")
    

Hãy thận trọng khi sử dụng mã.

**📄 models/task.py**

Phục vụ quản lý trạng thái tải: đang chờ, đang tải, lỗi, hoặc thành công.

python
    
    
    from datetime import datetime
    from sqlalchemy import String, DateTime
    from sqlalchemy.orm import Mapped, mapped_column
    from database.schema import Base
    
    class Task(Base):
        __tablename__ = "tasks"
    
        id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
        target_url: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
        status: Mapped[str] = mapped_column(String(50), default="PENDING")  # PENDING, RUNNING, COMPLETED, FAILED
        error_message: Mapped[str] = mapped_column(String, default="")
        updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    

Hãy thận trọng khi sử dụng mã.

* * *

**📦 3. TẦNG REPOSITORIES (Thực thi truy vấn dữ liệu)**

**📄 repositories/base_repository.py**

Lớp cha trừu tượng xử lý các hàm CRUD cơ bản (Thêm, sửa, xóa, tìm kiếm theo ID) cho mọi Model.

python
    
    
    from typing import TypeVar, Generic, Type, Any
    from sqlalchemy.orm import Session
    from database.schema import Base
    
    ModelType = TypeVar("ModelType", bound=Base)
    
    class BaseRepository(Generic[ModelType]):
        def __init__(self, model_class: Type[ModelType]):
            self.model_class = model_class
    
        def get_by_id(self, db: Session, id: Any) -> ModelType | None:
            return db.query(self.model_class).filter(self.model_class.id == id).first()
    
        def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> list[ModelType]:
            return db.query(self.model_class).offset(skip).limit(limit).all()
    
        def create(self, db: Session, obj: ModelType) -> ModelType:
            db.add(obj)
            db.flush()  # Sinh ID tự động cho object trước khi commit thực sự
            return obj
    
        def delete(self, db: Session, id: Any) -> bool:
            obj = self.get_by_id(db, id)
            if obj:
                db.delete(obj)
                return True
            return False
    

Hãy thận trọng khi sử dụng mã.

**📄 repositories/novel_repository.py**

Xử lý các logic chuyên sâu đặc thù riêng cho bảng truyện.

python
    
    
    from sqlalchemy.orm import Session
    from models.novel import Novel
    from .base_repository import BaseRepository
    
    class NovelRepository(BaseRepository[Novel]):
        def __init__(self):
            super().__init__(Novel)
    
        def get_by_slug(self, db: Session, slug: str) -> Novel | None:
            return db.query(Novel).filter(Novel.slug == slug).first()
    
        def create_or_update(self, db: Session, website_id: int, novel_data: dict) -> Novel:
            """Cập nhật thông tin truyện nếu đã tồn tại, ngược lại thì tạo mới."""
            existing_novel = self.get_by_slug(db, novel_data["slug"])
            
            genres_str = ", ".join(novel_data.get("genres", []))
            
            if existing_novel:
                existing_novel.title = novel_data.get("title", existing_novel.title)
                existing_novel.author = novel_data.get("author", existing_novel.author)
                existing_novel.status = novel_data.get("status", existing_novel.status)
                existing_novel.genres = genres_str
                existing_novel.description = novel_data.get("description", existing_novel.description)
                return existing_novel
            else:
                new_novel = Novel(
                    website_id=website_id,
                    title=novel_data["title"],
                    slug=novel_data["slug"],
                    author=novel_data.get("author", "Không rõ"),
                    status=novel_data.get("status", "Đang tiến hành"),
                    genres=genres_str,
                    description=novel_data.get("description", "")
                )
                return self.create(db, new_novel)
    

Hãy thận trọng khi sử dụng mã.

**📄 repositories/chapter_repository.py**

python
    
    
    from sqlalchemy.orm import Session
    from models.chapter import Chapter
    from .base_repository import BaseRepository
    
    class ChapterRepository(BaseRepository[Chapter]):
        def __init__(self):
            super().__init__(Chapter)
    
        def is_chapter_exists(self, db: Session, novel_id: int, url: str) -> bool:
            return db.query(Chapter).filter(Chapter.novel_id == novel_id, Chapter.url == url).count() > 0
    
        def bulk_insert_chapters(self, db: Session, novel_id: int, chapters_data: list[dict]) -> None:
            """Lưu hàng loạt nội dung chương một cách tối ưu."""
            chapters_to_insert = []
            for idx, ch in enumerate(chapters_data):
                if not self.is_chapter_exists(db, novel_id, ch["url"]):
                    chapters_to_insert.append(
                        Chapter(
                            novel_id=novel_id,
                            title=ch["title"],
                            url=ch["url"],
                            order_index=idx + 1,
                            content=ch.get("content", "")
                        )
                    )
            if chapters_to_insert:
                db.bulk_save_objects(chapters_to_insert)
    

Hãy thận trọng khi sử dụng mã.

* * *

**🚀 4. KẾT NỐI TOÀN BỘ HỆ THỐNG VÀ CHẠY THỬ NGHIỆM**

Dưới đây là một file `main_persistence_test.py` tích hợp cả HTTP Client, Parser ở lượt chat trước để nạp thẳng dữ liệu cào được từ **TruyenFull** trực tiếp vào **SQLite**.

python
    
    
    # main_persistence_test.py
    from database.database import init_db
    from database.transaction import transaction_scope
    from models.website import Website
    from repositories.novel_repository import NovelRepository
    from repositories.chapter_repository import ChapterRepository
    from plugins.base.http_client import HTTPClient
    from plugins.truyenfull.source import TruyenFullSource
    
    def run_crawler_pipeline():
        # Bước 1: Khởi tạo cấu trúc bảng Database
        print("[1] Đang cấu hình và đồng bộ database...")
        init_db()
    
        # Bước 2: Chuẩn bị nguồn cào
        client = HTTPClient(delay_range=(1.0, 2.0))
        scraper = TruyenFullSource(client=client)
        
        slug_truyen = "truyen-chu-tien"
    
        try:
            # Bước 3: Cào dữ liệu thô từ trang Web
            print(f"[2] Bắt đầu cào dữ liệu từ web cho truyện: {slug_truyen}")
            raw_data = scraper.crawl_novel(slug_truyen)
            raw_data["slug"] = slug_truyen
    
            # Bước 4: Lưu trữ an toàn dữ liệu thông qua Transaction & Repository
            print("[3] Kết nối Database thành công. Tiến hành lưu trữ...")
            with transaction_scope() as db_session:
                
                # 4.1 Khởi tạo/Lấy bản ghi Website gốc
                existing_site = db_session.query(Website).filter(Website.base_url == "https://truyenfull.io").first()
                if not existing_site:
                    existing_site = Website(name="TruyenFull", base_url="https://truyenfull.io")
                    db_session.add(existing_site)
                    db_session.flush() # Để lấy existing_site.id
                
                # 4.2 Thêm mới hoặc cập nhật thông tin truyện
                novel_repo = NovelRepository()
                novel_record = novel_repo.create_or_update(db_session, website_id=existing_site.id, novel_data=raw_data)
                
                # 4.3 Thêm mới hàng loạt nội dung chương truyện vào Database
                chapter_repo = ChapterRepository()
                chapter_repo.bulk_insert_chapters(
                    db=db_session, 
                    novel_id=novel_record.id, 
                    chapters_data=raw_data["chapters_content"]
                )
                
            print("\n🎉 HỆ THỐNG PIPELINE HOÀN TẤT THÀNH CÔNG!")
            print(f"-> Truyện '{novel_record.title}' và các chương chi tiết đã được nạp an toàn vào DB.")
    
        except Exception as e:
            print(f"❌ Xảy ra lỗi trong quá trình thực thi: {e}")
        finally:
            client.close()
    
    if __name__ == "__main__":
        run_crawler_pipeline()
    

Hãy thận trọng khi sử dụng mã.

Để tiếp tục hoàn thiện, bạn có muốn cấu hình hệ thống **Đa luồng (Multi-threading)** kết hợp với bảng `Task` để cào cùng lúc nhiều bộ truyện khác nhau không?

## GLAI: SQL + SQLite3 thuần

Việc chuyển sang dùng thư viện thuần `sqlite3` và viết câu lệnh SQL trực tiếp (Raw SQL) rất phù hợp cho crawler: giúp tăng tốc độ ghi dữ liệu, giảm độ trễ và kiểm soát tuyệt đối hiệu năng mà không phụ thuộc vào lớp trừu tượng phức tạp của ORM.

Dưới đây là toàn bộ mã nguồn của hệ thống được viết lại hoàn toàn bằng **Raw SQL** , giữ nguyên kiến trúc Repository Pattern nhưng sử dụng thư viện `sqlite3` có sẵn của Python.

* * *

**📦 1. TẦNG DATABASE (Kết nối & Giao dịch thuần)**

**📄 database/connection.py**

python
    
    
    import os
    import sqlite3
    
    DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../crawler.db"))
    
    def get_db_connection() -> sqlite3.Connection:
        """Tạo kết nối tới SQLite, cấu hình trả về kết quả dạng Dictionary."""
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        # Giúp truy cập dữ liệu theo tên cột: row['title'] thay vì row[0]
        conn.row_factory = sqlite3.Row
        # Bật tính năng khóa ngoại (Foreign Key) - Mặc định SQLite tắt tính năng này
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    

Hãy thận trọng khi sử dụng mã.

**📄 database/transaction.py**

python
    
    
    from contextlib import contextmanager
    from typing import Generator
    import sqlite3
    from .connection import get_db_connection
    
    @contextmanager
    def transaction_scope() -> Generator[sqlite3.Connection, None, None]:
        """Quản lý Context Manager tự động Commit khi thành công và Rollback khi lỗi."""
        conn = get_db_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    

Hãy thận trọng khi sử dụng mã.

**📄 database/schema.py**

Định nghĩa sẵn các chuỗi lệnh SQL khởi tạo cấu trúc bảng.

python
    
    
    CREATE_TABLES_SQL = """
    CREATE TABLE IF NOT EXISTS websites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        base_url TEXT UNIQUE NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS novels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        website_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        author TEXT DEFAULT 'Không rõ',
        status TEXT DEFAULT 'Đang tiến hành',
        genres TEXT DEFAULT '',
        description TEXT DEFAULT '',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE
    );
    
    CREATE TABLE IF NOT EXISTS chapters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        novel_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        order_index INTEGER DEFAULT 0,
        content TEXT DEFAULT '',
        UNIQUE(novel_id, url),
        FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE
    );
    
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target_url TEXT UNIQUE NOT NULL,
        status TEXT DEFAULT 'PENDING',
        error_message TEXT DEFAULT '',
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """
    

Hãy thận trọng khi sử dụng mã.

**📄 database/database.py**

python
    
    
    from .connection import get_db_connection
    from .schema import CREATE_TABLES_SQL
    
    def init_db() -> None:
        """Khởi tạo toàn bộ cấu trúc cơ sở dữ liệu bằng SQL thuần."""
        conn = get_db_connection()
        try:
            # execute_script cho phép chạy chuỗi nhiều câu lệnh SQL cùng lúc
            conn.executescript(CREATE_TABLES_SQL)
            conn.commit()
        finally:
            conn.close()
    

Hãy thận trọng khi sử dụng mã.

* * *

**📦 2. TẦNG MODELS (Dạng Data Class / Dictionaries sạch)**

Vì không sử dụng ORM, tầng này không chứa logic ánh xạ bảng. Bạn chỉ cần định nghĩa cấu trúc dữ liệu thuần để gán kiểu dữ liệu (Type hinting) cho sáng sủa.

**📄 models/novel.py**

python
    
    
    from typing import TypedDict, Optional
    
    class NovelDict(TypedDict):
        id: Optional[int]
        website_id: int
        title: str
        slug: str
        author: str
        status: str
        genres: str
        description: str
        created_at: Optional[str]
    

Hãy thận trọng khi sử dụng mã.

* * *

**📦 3. TẦNG REPOSITORIES (Thực thi SQL thuần bằng Con trỏ - Cursor)**

**📄 repositories/base_repository.py**

Xử lý các câu lệnh SQL cơ bản chung cho các bảng.

python
    
    
    from typing import Any, Optional
    import sqlite3
    
    class BaseRepository:
        def __init__(self, table_name: str):
            self.table_name = table_name
    
        def get_by_id(self, conn: sqlite3.Connection, id: Any) -> Optional[sqlite3.Row]:
            query = f"SELECT * FROM {self.table_name} WHERE id = ?"
            cursor = conn.execute(query, (id,))
            return cursor.fetchone()
    
        def get_all(self, conn: sqlite3.Connection, limit: int = 100) -> list[sqlite3.Row]:
            query = f"SELECT * FROM {self.table_name} LIMIT ?"
            cursor = conn.execute(query, (limit,))
            return cursor.fetchall()
    
        def delete(self, conn: sqlite3.Connection, id: Any) -> bool:
            query = f"DELETE FROM {self.table_name} WHERE id = ?"
            cursor = conn.execute(query, (id,))
            return cursor.rowcount > 0
    

Hãy thận trọng khi sử dụng mã.

**📄 repositories/novel_repository.py**

python
    
    
    import sqlite3
    from typing import Optional
    from .base_repository import BaseRepository
    
    class NovelRepository(BaseRepository):
        def __init__(self):
            super().__init__("novels")
    
        def get_by_slug(self, conn: sqlite3.Connection, slug: str) -> Optional[sqlite3.Row]:
            query = "SELECT * FROM novels WHERE slug = ?"
            cursor = conn.execute(query, (slug,))
            return cursor.fetchone()
    
        def create_or_update(self, conn: sqlite3.Connection, website_id: int, novel_data: dict) -> int:
            """Thêm mới truyện, nếu trùng slug thì tự động cập nhật (Upsert) và trả về ID."""
            genres_str = ", ".join(novel_data.get("genres", []))
            
            # Kiểm tra sự tồn tại trước bằng SQL
            existing = self.get_by_slug(conn, novel_data["slug"])
            
            if existing:
                query = """
                    UPDATE novels 
                    SET title = ?, author = ?, status = ?, genres = ?, description = ?
                    WHERE id = ?
                """
                conn.execute(query, (
                    novel_data["title"],
                    novel_data.get("author", "Không rõ"),
                    novel_data.get("status", "Đang tiến hành"),
                    genres_str,
                    novel_data.get("description", ""),
                    existing["id"]
                ))
                return existing["id"]
            else:
                query = """
                    INSERT INTO novels (website_id, title, slug, author, status, genres, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                cursor = conn.execute(query, (
                    website_id,
                    novel_data["title"],
                    novel_data["slug"],
                    novel_data.get("author", "Không rõ"),
                    novel_data.get("status", "Đang tiến hành"),
                    genres_str,
                    novel_data.get("description", "")
                ))
                return cursor.lastrowid  # Lấy ID tự sinh của dòng vừa chèn vào
    

Hãy thận trọng khi sử dụng mã.

**📄 repositories/chapter_repository.py**

Tận dụng tính năng `executemany` của `sqlite3` để ghi hàng loạt chương siêu tốc.

python
    
    
    import sqlite3
    from .base_repository import BaseRepository
    
    class ChapterRepository(BaseRepository):
        def __init__(self):
            super().__init__("chapters")
    
        def bulk_insert_chapters(self, conn: sqlite3.Connection, novel_id: int, chapters_data: list[dict]) -> None:
            """Sử dụng SQL INSERT OR IGNORE và executemany để đẩy danh sách dữ liệu cực nhanh."""
            query = """
                INSERT OR IGNORE INTO chapters (novel_id, title, url, order_index, content)
                VALUES (?, ?, ?, ?, ?)
            """
            
            # Chuẩn bị danh sách Tuple dữ liệu tương ứng các dấu chấm hỏi (?)
            records_to_insert = []
            for idx, ch in enumerate(chapters_data):
                records_to_insert.append((
                    novel_id,
                    ch["title"],
                    ch["url"],
                    idx + 1,
                    ch.get("content", "")
                ))
                
            if records_to_insert:
                # Ghi đồng loạt xuống ổ đĩa chỉ bằng 1 câu lệnh tối ưu
                conn.executemany(query, records_to_insert)
    

Hãy thận trọng khi sử dụng mã.

* * *

**🚀 4. LUỒNG CHẠY THỬ NGHIỆM TÍNH NĂNG (Pipeline)**

File test tích hợp pipeline cào dữ liệu và ghi trực tiếp bằng SQL thuần:

python
    
    
    # pipeline_test.py
    from database.database import init_db
    from database.transaction import transaction_scope
    from repositories.novel_repository import NovelRepository
    from repositories.chapter_repository import ChapterRepository
    from plugins.base.http_client import HTTPClient
    from plugins.truyenfull.source import TruyenFullSource
    
    def main():
        print("[+] Khởi tạo cấu trúc bảng SQLite3...")
        init_db()
    
        client = HTTPClient(delay_range=(1.0, 1.5))
        scraper = TruyenFullSource(client=client)
        slug_truyen = "truyen-chu-tien"
    
        try:
            # 1. Cào dữ liệu
            raw_data = scraper.crawl_novel(slug_truyen)
            raw_data["slug"] = slug_truyen
    
            # 2. Sử dụng Transaction bọc kết nối sqlite3 thuần
            with transaction_scope() as conn:
                
                # Kiểm tra hoặc chèn Website
                cursor = conn.execute("SELECT id FROM websites WHERE base_url = ?", ("https://truyenfull.io",))
                row = cursor.fetchone()
                if row:
                    website_id = row["id"]
                else:
                    cursor = conn.execute(
                        "INSERT INTO websites (name, base_url) VALUES (?, ?)", 
                        ("TruyenFull", "https://truyenfull.io")
                    )
                    website_id = cursor.lastrowid
    
                # Ghi thông tin truyện bằng Raw SQL
                novel_repo = NovelRepository()
                novel_id = novel_repo.create_or_update(conn, website_id=website_id, novel_data=raw_data)
                
                # Ghi hàng loạt chương bằng executemany siêu tốc
                chapter_repo = ChapterRepository()
                chapter_repo.bulk_insert_chapters(
                    conn=conn, 
                    novel_id=novel_id, 
                    chapters_data=raw_data["chapters_content"]
                )
                
            print("\n🎉 THÀNH CÔNG: Dữ liệu đã lưu bằng SQL thuần vào file 'crawler.db'!")
    
        except Exception as e:
            print(f"❌ Thất bại: {e}")
        finally:
            client.close()
    
    if __name__ == "__main__":
        main()
    

Hãy thận trọng khi sử dụng mã.

Bạn có muốn hoàn thiện nốt phần **Task Manager** bằng SQL thuần (sử dụng câu lệnh `UPDATE tasks SET status = 'COMPLETED' WHERE ...`) để quản lý tiến độ cào hàng loạt link truyện không?

