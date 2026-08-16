Version:0.9 StartHTML:0000000105 EndHTML:0000043620 StartFragment:0000000141 EndFragment:0000043584 

Q:
    
    
    database/
    ├── config.py # DatabaseConfig
    ├── connection.py # SQLiteConnection
    ├── session.py # SQLiteSession
    └── engine.py # SQLiteEngine

GLAI:

## **Engine-Connection-Session**

Để thiết kế cấu trúc thư mục `database/` theo mô hình **Engine-Connection-Session** (tương tự kiến trúc của SQLAlchemy nhưng xây dựng thủ công trên nền `sqlite3` thuần), chúng ta cần tách biệt rõ ràng trách nhiệm: `Engine` giữ cấu hình/quản lý pool, `Connection` xử lý kết nối vật lý, và `Session` đóng vai trò quản lý transaction (Unit of Work).

Dưới đây là mã nguồn chi tiết, đồng bộ và phân tách mô-đun chuẩn xác theo sơ đồ của bạn.

* * *

**📄 database/config.py**

Nơi định nghĩa cấu hình Database, các chế độ tối ưu cho SQLite (`journal_mode`, `synchronous`) giúp tăng tốc độ ghi dữ liệu của crawler.

python
    
    
    import os
    
    class DatabaseConfig:
        def __init__(self, db_name: str = "crawler.db", timeout: float = 30.0):
            # Định vị file database nằm tại thư mục gốc của dự án
            self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../{db_name}"))
            self.timeout = timeout
            
            # Các thiết lập PRAGMA tối ưu hiệu năng ghi cho SQLite
            self.pragmas = {
                "foreign_keys": "ON",            # Bật ràng buộc khóa ngoại
                "journal_mode": "WAL",           # Write-Ahead Logging: Giúp đọc/ghi song song cực nhanh
                "synchronous": "NORMAL",         # Giảm bớt việc ghi đồng bộ xuống đĩa để tăng tốc
                "cache_size": -2000              # Sử dụng khoảng 2MB bộ nhớ đệm cache
            }
    
        @property
        def connection_string(self) -> str:
            return self.db_path
    

Hãy thận trọng khi sử dụng mã.

**📄 database/connection.py**

Lớp bọc đối tượng kết nối thô của `sqlite3`, chịu trách nhiệm cấu hình cấu trúc dữ liệu trả về và áp dụng các thông số tối ưu hệ thống.

python
    
    
    import sqlite3
    from .config import DatabaseConfig
    
    class SQLiteConnection:
        def __init__(self, config: DatabaseConfig):
            self.config = config
            self._raw_conn: sqlite3.Connection | None = None
    
        def open(self) -> sqlite3.Connection:
            """Khởi tạo và thiết lập cấu hình kết nối vật lý."""
            self._raw_conn = sqlite3.connect(
                self.config.connection_string,
                timeout=self.config.timeout
            )
            # Giúp truy cập dữ liệu dạng Dictionary: row["col_name"] thay vì row[0]
            self._raw_conn.row_factory = sqlite3.Row
            
            # Áp dụng các cấu hình tối ưu hiệu năng
            self._apply_pragmas()
            return self._raw_conn
    
        def _apply_pragmas(self) -> None:
            if not self._raw_conn:
                return
            cursor = self._raw_conn.cursor()
            for key, value in self.config.pragmas.items():
                cursor.execute(f"PRAGMA {key} = {value};")
    
        def close(self) -> None:
            """Đóng kết nối một cách an toàn."""
            if self._raw_conn:
                self._raw_conn.close()
                self._raw_conn = None
    

Hãy thận trọng khi sử dụng mã.

**📄 database/engine.py**

Điểm quản lý trung tâm (Factory). Nhận vào cấu hình và chịu trách nhiệm cấp phát các đối tượng kết nối (`SQLiteConnection`), đồng thời cung cấp hàm khởi chạy nhanh script tạo bảng ban đầu.

python
    
    
    from .config import DatabaseConfig
    from .connection import SQLiteConnection
    
    class SQLiteEngine:
        def __init__(self, config: DatabaseConfig | None = None):
            self.config = config or DatabaseConfig()
    
        def connect(self) -> SQLiteConnection:
            """Tạo ra một đối tượng quản lý kết nối mới."""
            return SQLiteConnection(self.config)
    
        def execute_script(self, script_sql: str) -> None:
            """Chạy nhanh một kịch bản SQL (Ví dụ: Khởi tạo schema tạo bảng)."""
            db_conn = self.connect()
            raw_conn = db_conn.open()
            try:
                raw_conn.executescript(script_sql)
                raw_conn.commit()
            finally:
                db_conn.close()
    

Hãy thận trọng khi sử dụng mã.

**📄 database/session.py**

Thành phần cốt lõi quản lý chu trình giao dịch (Transaction). Sử dụng Context Manager (`with`) để tự động `commit()` khi khối lệnh chạy thành công hoặc `rollback()` nếu phát sinh lỗi bất ngờ.
    
    
    import sqlite3
    from typing import Any
    from .engine import SQLiteEngine
    
    class SQLiteSession:
        def __init__(self, engine: SQLiteEngine):
            self.engine = engine
            self.db_conn = self.engine.connect()
            self.connection: sqlite3.Connection | None = None
    
        def __enter__(self) -> "SQLiteSession":
            """Khai mở phiên làm việc (Session) và bắt đầu một Transaction."""
            self.connection = self.db_conn.open()
            return self
    
        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
            """Kết thúc phiên làm việc: Tự động commit nếu êm xuôi, rollback nếu lỗi."""
            if self.connection:
                try:
                    if exc_type is not None:
                        # Có lỗi xảy ra trong khối lệnh `with` -> Hoàn tác dữ liệu
                        self.connection.rollback()
                        print(f"[Database Session] Lỗi hệ thống: {exc_val}. Đang thực hiện Rollback...")
                    else:
                        # Mọi thứ chạy mượt mà -> Lưu dữ liệu vĩnh viễn vào ổ đĩa
                        self.connection.commit()
                finally:
                    self.db_conn.close()
                    self.connection = None
            return False  # Trả về False để Python tiếp tục ném lỗi ra ngoài nếu có
    
        def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
            """Phương thức tiện ích để thực thi câu lệnh truy vấn đơn lẻ."""
            if not self.connection:
                raise RuntimeError("Session chưa được mở. Vui lòng sử dụng cấu trúc cú pháp 'with'.")
            return self.connection.execute(sql, params)
    
        def executemany(self, sql: str, params_list: list[tuple]) -> sqlite3.Cursor:
            """Phương thức tiện ích để thực thi ghi dữ liệu số lượng lớn (Bulk Insert)."""
            if not self.connection:
                raise RuntimeError("Session chưa được mở. Vui lòng sử dụng cấu trúc cú pháp 'with'.")
            return self.connection.executemany(sql, params_list)
    

* * *

**🚀 Hướng dẫn tích hợp và chạy thử nghiệm hệ thống**

Dưới đây là ví dụ minh họa cách kết hợp bộ khung cơ sở dữ liệu mới này để thực thi câu lệnh SQL một cách an toàn và chuyên nghiệp:

python
    
    
    # db_demo_test.py
    from database.config import DatabaseConfig
    from database.engine import SQLiteEngine
    from database.session import SQLiteSession
    
    # Kịch bản khởi tạo bảng (Schema)
    INIT_SQL = """
    CREATE TABLE IF NOT EXISTS mock_novels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL
    );
    """
    
    def main():
        # 1. Khởi tạo cấu hình và Engine
        config = DatabaseConfig(db_name="crawler_factory.db")
        engine = SQLiteEngine(config)
    
        # 2. Khởi tạo bảng dữ liệu ban đầu
        print("[+] Đang tạo bảng bằng Engine...")
        engine.execute_script(INIT_SQL)
    
        # 3. Sử dụng Session để thực hiện thêm/sửa/xóa dữ liệu bọc trong Transaction an toàn
        print("[+] Mở Session để ghi dữ liệu thử nghiệm...")
        try:
            with SQLiteSession(engine) as session:
                # Chèn dữ liệu đơn lẻ
                session.execute(
                    "INSERT OR IGNORE INTO mock_novels (title, slug) VALUES (?, ?)", 
                    ("Tiên Nghịch", "tien-nghich")
                )
                
                # Ghi hàng loạt (Bulk Insert) tối ưu hiệu năng
                data_list = [
                    ("Phàm Nhân Tu Tiên", "pham-nhan-tu-tien"),
                    ("Cầu Ma", "cau-ma")
                ]
                session.executemany(
                    "INSERT OR IGNORE INTO mock_novels (title, slug) VALUES (?, ?)", 
                    data_list
                )
                
            print("🎉 Lưu dữ liệu (Commit) thành công!")
            
        except Exception as e:
            print(f"❌ Phiên làm việc thất bại: {e}")
    
        # 4. Mở một phiên khác để đọc kiểm tra dữ liệu
        with SQLiteSession(engine) as session:
            cursor = session.execute("SELECT * FROM mock_novels")
            rows = cursor.fetchall()
            
            print("\n--- Danh sách truyện hiện có trong Database ---")
            for row in rows:
                print(f"ID: {row['id']} | Tên: {row['title']} | Slug: {row['slug']}")
    
    if __name__ == "__main__":
        main()
    

Hãy thận trọng khi sử dụng mã.

Kế thừa cấu trúc này, bạn có muốn tôi cập nhật lại các file trong thư mục **repositories/** (như `novel_repository.py`, `chapter_repository.py`) để chúng nhận vào tham số `session: SQLiteSession` thay vì `conn: sqlite3.Connection` không?

## cập nhât repo để nhận SQLiteSession

Dưới đây là mã nguồn được cập nhật toàn diện cho tầng **Repositories**. Lần này, các hàm sẽ nhận trực tiếp đối tượng `session: SQLiteSession` thay vì `conn: sqlite3.Connection`.

Mọi thao tác gọi đến cơ sở dữ liệu sẽ thông qua các phương thức `session.execute()` hoặc `session.executemany()` nhằm tuân thủ thiết kế bọc Transaction an toàn mà bạn vừa xây dựng.

* * *

**📄 repositories/base_repository.py**

Lớp cha thiết lập các truy vấn nền tảng dùng chung (CRUD) dựa trên `SQLiteSession`.

python
    
    
    from typing import Any, Optional
    import sqlite3
    from database.session import SQLiteSession
    
    class BaseRepository:
        def __init__(self, table_name: str):
            self.table_name = table_name
    
        def get_by_id(self, session: SQLiteSession, id: Any) -> Optional[sqlite3.Row]:
            query = f"SELECT * FROM {self.table_name} WHERE id = ?;"
            cursor = session.execute(query, (id,))
            return cursor.fetchone()
    
        def get_all(self, session: SQLiteSession, limit: int = 100) -> list[sqlite3.Row]:
            query = f"SELECT * FROM {self.table_name} LIMIT ?;"
            cursor = session.execute(query, (limit,))
            return cursor.fetchall()
    
        def delete(self, session: SQLiteSession, id: Any) -> bool:
            query = f"DELETE FROM {self.table_name} WHERE id = ?;"
            cursor = session.execute(query, (id,))
            # Đối tượng connection vật lý nằm trong session được dùng để đếm số dòng bị ảnh hưởng
            return cursor.rowcount > 0
    

Hãy thận trọng khi sử dụng mã.

**📄 repositories/novel_repository.py**

Xử lý logic thêm mới và cập nhật đồng bộ (Upsert) dữ liệu thông tin truyện qua `SQLiteSession`.

python
    
    
    from typing import Optional
    import sqlite3
    from database.session import SQLiteSession
    from .base_repository import BaseRepository
    
    class NovelRepository(BaseRepository):
        def __init__(self):
            super().__init__("novels")
    
        def get_by_slug(self, session: SQLiteSession, slug: str) -> Optional[sqlite3.Row]:
            query = "SELECT * FROM novels WHERE slug = ?;"
            cursor = session.execute(query, (slug,))
            return cursor.fetchone()
    
        def create_or_update(self, session: SQLiteSession, website_id: int, novel_data: dict) -> int:
            """Cập nhật thông tin truyện nếu trùng slug, ngược lại tạo mới. Trả về ID của truyện."""
            genres_str = ", ".join(novel_data.get("genres", []))
            existing = self.get_by_slug(session, novel_data["slug"])
            
            if existing:
                query = """
                    UPDATE novels 
                    SET title = ?, author = ?, status = ?, genres = ?, description = ?
                    WHERE id = ?;
                """
                session.execute(query, (
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
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                """
                cursor = session.execute(query, (
                    website_id,
                    novel_data["title"],
                    novel_data["slug"],
                    novel_data.get("author", "Không rõ"),
                    novel_data.get("status", "Đang tiến hành"),
                    genres_str,
                    novel_data.get("description", "")
                ))
                return cursor.lastrowid
    

Hãy thận trọng khi sử dụng mã.

**📄 repositories/chapter_repository.py**

Tối ưu hóa tác vụ chèn hàng loạt nội dung chương (Bulk Insert) bằng cách tích hợp tính năng `executemany` của `SQLiteSession`.

python
    
    
    from database.session import SQLiteSession
    from .base_repository import BaseRepository
    
    class ChapterRepository(BaseRepository):
        def __init__(self):
            super().__init__("chapters")
    
        def bulk_insert_chapters(self, session: SQLiteSession, novel_id: int, chapters_data: list[dict]) -> None:
            """Sử dụng cơ chế INSERT OR IGNORE để đẩy nhanh hàng loạt chương truyện."""
            query = """
                INSERT OR IGNORE INTO chapters (novel_id, title, url, order_index, content)
                VALUES (?, ?, ?, ?, ?);
            """
            
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
                session.executemany(query, records_to_insert)
    

Hãy thận trọng khi sử dụng mã.

**📄 repositories/task_repository.py**

Hỗ trợ quản lý hàng đợi tác vụ cào dữ liệu cho crawler.

python
    
    
    from typing import Optional
    import sqlite3
    from database.session import SQLiteSession
    from .base_repository import BaseRepository
    
    class TaskRepository(BaseRepository):
        def __init__(self):
            super().__init__("tasks")
    
        def get_next_pending_task(self, session: SQLiteSession) -> Optional[sqlite3.Row]:
            """Lấy ra một tác vụ đang ở trạng thái chờ (PENDING) để xử lý."""
            query = "SELECT * FROM tasks WHERE status = 'PENDING' ORDER BY id ASC LIMIT 1;"
            cursor = session.execute(query)
            return cursor.fetchone()
    
        def update_task_status(self, session: SQLiteSession, task_id: int, status: str, error_message: str = "") -> None:
            """Cập nhật trạng thái tác vụ (RUNNING, COMPLETED, FAILED)."""
            query = """
                UPDATE tasks 
                SET status = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?;
            """
            session.execute(query, (status, error_message, task_id))
    

Hãy thận trọng khi sử dụng mã.

* * *

**🚀 Hướng dẫn tích hợp toàn bộ luồng hoạt động mới**

Dưới đây là file `run_pipeline.py` hoàn chỉnh tại thư mục gốc, minh chứng cách kết hợp nhịp nhàng giữa **Engine** , **Session** , **Source Scraper** và các **Repositories** mới cập nhật:

python
    
    
    # run_pipeline.py
    from database.config import DatabaseConfig
    from database.engine import SQLiteEngine
    from database.session import SQLiteSession
    from database.schema import CREATE_TABLES_SQL  # Import chuỗi lệnh SQL tạo bảng ở các bước trước
    
    from repositories.novel_repository import NovelRepository
    from repositories.chapter_repository import ChapterRepository
    
    from plugins.base.http_client import HTTPClient
    from plugins.truyenfull.source import TruyenFullSource
    
    def main():
        # 1. Khởi tạo Engine cấu trúc dữ liệu cơ sở
        config = DatabaseConfig(db_name="crawler_production.db")
        engine = SQLiteEngine(config)
        
        print("[+] Khởi tạo cấu trúc bảng dữ liệu...")
        engine.execute_script(CREATE_TABLES_SQL)
    
        # 2. Khởi tạo Client và Bộ thu thập truyện
        client = HTTPClient(delay_range=(1.0, 2.0))
        scraper = TruyenFullSource(client=client)
        slug_target = "truyen-chu-tien"
    
        try:
            # Tải thông tin từ website
            raw_data = scraper.crawl_novel(slug_target)
            raw_data["slug"] = slug_target
    
            # 3. Mở một chu kỳ Session bọc Transaction an toàn để ghi nhận dữ liệu bằng Repositories
            print("[+] Khai mở cơ chế SQLiteSession. Tiến hành đồng bộ...")
            with SQLiteSession(engine) as session:
                
                # Xử lý nhanh ghi nhận thông tin nguồn Website
                cursor = session.execute("SELECT id FROM websites WHERE base_url = ?;", ("https://truyenfull.io",))
                row = cursor.fetchone()
                if row:
                    website_id = row["id"]
                else:
                    cursor = session.execute(
                        "INSERT INTO websites (name, base_url) VALUES (?, ?);", 
                        ("TruyenFull", "https://truyenfull.io")
                    )
                    website_id = cursor.lastrowid
    
                # Thực thi thông qua NovelRepository nhận tham số session
                novel_repo = NovelRepository()
                novel_id = novel_repo.create_or_update(session, website_id=website_id, novel_data=raw_data)
                
                # Thực thi thông qua ChapterRepository nhận tham số session
                chapter_repo = ChapterRepository()
                chapter_repo.bulk_insert_chapters(
                    session=session, 
                    novel_id=novel_id, 
                    chapters_data=raw_data["chapters_content"]
                )
                
            print("\n🎉 HOÀN THÀNH: Giao dịch kết thúc mỹ mãn, dữ liệu đã được tự động Commit an toàn!")
    
        except Exception as e:
            print(f"❌ Chu trình thất bại: {e}")
        finally:
            client.close()
    
    if __name__ == "__main__":
        main()
    

Hãy thận trọng khi sử dụng mã.

Kế hoạch tiếp theo, bạn có muốn thiết kế file **main.py** đầu não để triển khai cơ chế **vòng lặp liên tục quét hàng đợi tác vụ (tasks)** , tự động nhặt link truyện `PENDING` ra cào cho đến khi sạch hàng đợi không?

