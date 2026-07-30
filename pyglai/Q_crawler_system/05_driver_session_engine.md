Version:0.9 StartHTML:0000000105 EndHTML:0000039505 StartFragment:0000000141 EndFragment:0000039469 

Q:

đổi cấu trúc một chút 
    
    
    database/ 
    	config.py 
    	driver.py 
    	session.py 
    	engine.py

GLAI:

### driver-session-engine

Để điều chỉnh cấu trúc thư mục `database/` theo sơ đồ mới, chúng ta sẽ đưa file `connection.py` cũ thành **driver.py**.

Trong kiến trúc cơ sở dữ liệu cấp thấp, **driver.py** đóng vai trò quản lý tầng kết nối trực tiếp đến phần cứng/hệ thống file (thư viện `sqlite3`), đóng gói các tùy chỉnh và xử lý các hàm thiết lập nền tảng một cách độc lập.

Dưới đây là mã nguồn chi tiết, đồng bộ và phân tách mô-đun chính xác theo cấu trúc mới:

* * *

**📄 database/config.py**

Nơi tập trung các hằng số cấu hình, đường dẫn tệp tin và các câu lệnh tối ưu hiệu năng (PRAGMA).

python
    
    
    import os
    
    class DatabaseConfig:
        def __init__(self, db_name: str = "crawler.db", timeout: float = 30.0):
            # Định vị file database nằm tại thư mục gốc của dự án
            self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../{db_name}"))
            self.timeout = timeout
            
            # Các thiết lập PRAGMA tối ưu hiệu năng đọc/ghi (I/O) cho SQLite
            self.pragmas = {
                "foreign_keys": "ON",            # Bật ràng buộc khóa ngoại
                "journal_mode": "WAL",           # Write-Ahead Logging: Cho phép đọc/ghi song song
                "synchronous": "NORMAL",         # Tối ưu hóa bộ đệm, giảm số lần ghi trực tiếp xuống ổ đĩa
                "cache_size": -2000              # Cấp phát khoảng 2MB bộ nhớ đệm (Cache)
            }
    
        @property
        def connection_string(self) -> str:
            return self.db_path
    

Hãy thận trọng khi sử dụng mã.

**📄 database/driver.py**

Thay thế cho `connection.py`. Đây là Driver điều khiển kết nối vật lý, trực tiếp tương tác với thư viện mã nguồn `sqlite3` của Python và gán định dạng dữ liệu trả về.

python
    
    
    import sqlite3
    from .config import DatabaseConfig
    
    class SQLiteDriver:
        def __init__(self, config: DatabaseConfig):
            self.config = config
            self._raw_conn: sqlite3.Connection | None = None
    
        def connect(self) -> sqlite3.Connection:
            """Khai mở kết nối vật lý tới tệp tin SQLite."""
            self._raw_conn = sqlite3.connect(
                self.config.connection_string,
                timeout=self.config.timeout
            )
            # Ép cấu trúc kết quả trả về dạng Dictionary (row["column_name"])
            self._raw_conn.row_factory = sqlite3.Row
            
            # Thực thi các Pragma tối ưu hóa hệ thống file
            self._apply_pragmas()
            return self._raw_conn
    
        def _apply_pragmas(self) -> None:
            if not self._raw_conn:
                return
            cursor = self._raw_conn.cursor()
            for key, value in self.config.pragmas.items():
                cursor.execute(f"PRAGMA {key} = {value};")
    
        def disconnect(self) -> None:
            """Ngắt kết nối và giải phóng tài nguyên an toàn."""
            if self._raw_conn:
                self._raw_conn.close()
                self._raw_conn = None
    

Hãy thận trọng khi sử dụng mã.

**📄 database/engine.py**

Bộ máy trung tâm (Factory) nhận cấu hình, chịu trách nhiệm khởi tạo Driver kết nối, đồng thời cung cấp phương thức chạy nhanh các đoạn mã cấu trúc (Schema Script).

python
    
    
    from .config import DatabaseConfig
    from .driver import SQLiteDriver
    
    class SQLiteEngine:
        def __init__(self, config: DatabaseConfig | None = None):
            self.config = config or DatabaseConfig()
    
        def create_driver(self) -> SQLiteDriver:
            """Sinh ra một đối tượng Driver điều khiển kết nối độc lập."""
            return SQLiteDriver(self.config)
    
        def execute_script(self, script_sql: str) -> None:
            """Thực thi nhanh một nhóm câu lệnh SQL (Ví dụ: Tạo bảng dữ liệu ban đầu)."""
            driver = self.create_driver()
            raw_conn = driver.connect()
            try:
                raw_conn.executescript(script_sql)
                raw_conn.commit()
            finally:
                driver.disconnect()
    

Hãy thận trọng khi sử dụng mã.

**📄 database/session.py**

Quản lý vòng đời của một phiên làm việc (Unit of Work). Sử dụng cơ chế Context Manager (`with`) để tự động hóa hoàn toàn việc `commit` dữ liệu hoặc `rollback` khi phát sinh ngoại lệ đột xuất.

python
    
    
    import sqlite3
    from typing import Any
    from .engine import SQLiteEngine
    
    class SQLiteSession:
        def __init__(self, engine: SQLiteEngine):
            self.engine = engine
            self.driver = self.engine.create_driver()
            self.connection: sqlite3.Connection | None = None
    
        def __enter__(self) -> "SQLiteSession":
            """Mở phiên làm việc và kích hoạt Transaction."""
            self.connection = self.driver.connect()
            return self
    
        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
            """Đóng phiên: Tự động commit nếu thành công, rollback nếu lỗi."""
            if self.connection:
                try:
                    if exc_type is not None:
                        # Gặp lỗi phát sinh trong khối lệnh `with` -> Hoàn tác dữ liệu
                        self.connection.rollback()
                        print(f"[Session] Lỗi: {exc_val}. Đang thực thi Rollback...")
                    else:
                        # Khối lệnh mượt mà -> Lưu vĩnh viễn dữ liệu xuống đĩa
                        self.connection.commit()
                finally:
                    self.driver.disconnect()
                    self.connection = None
            return False  # Trả về False để Python tiếp tục ném lỗi ra ngoài (nếu có) để log debug
    
        def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
            """Hàm tiện ích thực thi câu lệnh truy vấn đơn lẻ."""
            if not self.connection:
                raise RuntimeError("Session chưa được mở. Vui lòng sử dụng cú pháp 'with'.")
            return self.connection.execute(sql, params)
    
        def executemany(self, sql: str, params_list: list[tuple]) -> sqlite3.Cursor:
            """Hàm tiện ích thực thi ghi dữ liệu số lượng lớn (Bulk Insert)."""
            if not self.connection:
                raise RuntimeError("Session chưa được mở. Vui lòng sử dụng cú pháp 'with'.")
            return self.connection.executemany(sql, params_list)
    

Hãy thận trọng khi sử dụng mã.

* * *

**🚀 Kiểm tra tính đúng đắn của luồng kiến trúc mới**

Bạn có thể chạy tệp tin thử nghiệm sau để kiểm tra xem cấu trúc Engine -> Driver -> Session mới đã hoạt động ăn khớp với nhau chưa:

python
    
    
    # test_new_structure.py
    from database.config import DatabaseConfig
    from database.engine import SQLiteEngine
    from database.session import SQLiteSession
    
    # Script tạo bảng giả lập
    MOCK_SCHEMA = """
    CREATE TABLE IF NOT EXISTS system_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    def main():
        # 1. Thiết lập cấu hình và Engine
        config = DatabaseConfig(db_name="crawler_new_driver.db")
        engine = SQLiteEngine(config)
    
        # 2. Khởi tạo bảng dữ liệu thông qua Engine
        print("[+] Đang khởi tạo bảng dữ liệu bằng Engine và Driver...")
        engine.execute_script(MOCK_SCHEMA)
    
        # 3. Sử dụng Session để thực thi ghi dữ liệu
        print("[+] Mở SQLiteSession bọc Transaction...")
        try:
            with SQLiteSession(engine) as session:
                # Ghi bản ghi đơn lẻ
                session.execute(
                    "INSERT INTO system_logs (message) VALUES (?);", 
                    ("Khởi động hệ thống crawler thành công.",)
                )
                # Ghi hàng loạt bản ghi
                bulk_logs = [
                    ("Đang kiểm tra kết nối proxy...",),
                    ("Bắt đầu quét danh sách hàng đợi tasks...",)
                ]
                session.executemany("INSERT INTO system_logs (message) VALUES (?);", bulk_logs)
                
            print("🎉 Giao dịch thành công (Tự động Commit)!")
        except Exception as e:
            print(f"❌ Giao dịch thất bại: {e}")
    
        # 4. Kiểm tra lại dữ liệu đã ghi
        with SQLiteSession(engine) as session:
            cursor = session.execute("SELECT * FROM system_logs;")
            rows = cursor.fetchall()
            print("\n--- Dữ liệu Logs đọc được từ Database ---")
            for row in rows:
                print(f"[{row['created_at']}] ID: {row['id']} | {row['message']}")
    
    if __name__ == "__main__":
        main()
    

Hãy thận trọng khi sử dụng mã.

Cấu trúc thành phần lưu trữ (Database layer) hiện tại đã rất gọn gàng và chuẩn chỉ. Bạn có muốn tôi giúp **viết file điều phối chạy chính (main.py)** để kết hợp toàn bộ từ `HTTPClient`, `TruyenFullSource`, các `Repositories` và hệ thống `Database` mới này vào một vòng lặp xử lý không?

### thử nghiệm:

Dưới đây là mã nguồn file đầu não **main.py** đặt tại thư mục gốc của dự án.

File này đóng vai trò là **Core Coordinator (Bộ điều phối chính)** : thiết lập vòng lặp quét bảng `tasks` liên tục, tự động nhặt các link truyện ở trạng thái `PENDING`, kích hoạt `HTTPClient` phối hợp cùng module `truyenfull` để cào, và dùng `SQLiteSession` cùng các `Repositories` để lưu trữ dữ liệu bền vững.

* * *

**📄 main.py**

python
    
    
    import sys
    import time
    import logging
    from database.config import DatabaseConfig
    from database.engine import SQLiteEngine
    from database.session import SQLiteSession
    from database.schema import CREATE_TABLES_SQL  # Chuỗi câu lệnh SQL tạo bảng đã dựng
    
    from repositories.novel_repository import NovelRepository
    from repositories.chapter_repository import ChapterRepository
    from repositories.task_repository import TaskRepository
    
    from plugins.base.http_client import HTTPClient
    from plugins.truyenfull.source import TruyenFullSource
    
    # Cấu hình hệ thống Log để tiện theo dõi tiến độ cào
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    logger = logging.getLogger(__name__)
    
    class CrawlerCoordinator:
        def __init__(self, db_name: str = "crawler_production.db"):
            # 1. Khởi tạo hạ tầng Database tầng thấp
            self.config = DatabaseConfig(db_name=db_name)
            self.engine = SQLiteEngine(self.config)
            
            # 2. Khởi tạo tầng truy vấn dữ liệu (Repositories)
            self.novel_repo = NovelRepository()
            self.chapter_repo = ChapterRepository()
            self.task_repo = TaskRepository()
            
            # 3. Khởi tạo mạng lưới (HTTP Client & Scraper Source)
            # Thiết lập delay an toàn từ 1.5 đến 3 giây để tránh bị chặn IP
            self.client = HTTPClient(delay_range=(1.5, 3.0), max_retries=3)
            self.scraper = TruyenFullSource(client=self.client)
    
        def setup_environment(self) -> None:
            """Tạo bảng dữ liệu và mồi sẵn dữ liệu mẫu ban đầu nếu DB trống."""
            logger.info("Đang kiểm tra và đồng bộ cấu trúc bảng SQLite3...")
            self.engine.execute_script(CREATE_TABLES_SQL)
            
            # Tạo sẵn dữ liệu mồi (Seed Data) để test vòng lặp nếu chưa có task nào
            with SQLiteSession(self.engine) as session:
                cursor = session.execute("SELECT COUNT(*) as total FROM tasks;")
                if cursor.fetchone()["total"] == 0:
                    logger.info("Database trống. Đang mồi tác vụ test vào bảng tasks...")
                    # Thử nghiệm thêm 2 truyện vào hàng đợi
                    session.execute(
                        "INSERT INTO tasks (target_url, status) VALUES (?, ?);",
                        ("https://truyenfull.io", "PENDING")
                    )
                    session.execute(
                        "INSERT INTO tasks (target_url, status) VALUES (?, ?);",
                        ("https://truyenfull.io", "PENDING")
                    )
                    
                # Đảm bảo có thông tin Website của TruyenFull
                cursor = session.execute("SELECT id FROM websites WHERE base_url = ?;", ("https://truyenfull.io",))
                if not cursor.fetchone():
                    session.execute(
                        "INSERT INTO websites (name, base_url) VALUES (?, ?);",
                        ("TruyenFull", "https://truyenfull.io")
                    )
    
        def run(self) -> None:
            """Vòng lặp cốt lõi quét hàng đợi tasks liên tục cho đến khi sạch bóng tác vụ."""
            self.setup_environment()
            logger.info("=== HỆ THỐNG CRAWLER ĐÃ SẴN SÀNG VÀ KÍCH HOẠT VÒNG LẶP ===")
    
            while True:
                # Bước 1: Mở một session ngắn để nhặt tác vụ PENDING
                task = None
                with SQLiteSession(self.engine) as session:
                    task = self.task_repo.get_next_pending_task(session)
                    
                    # Nếu tìm thấy task, chuyển ngay trạng thái sang RUNNING bên trong transaction
                    if task:
                        self.task_repo.update_task_status(session, task["id"], "RUNNING")
                
                # Bước 2: Nếu không còn tác vụ nào, thoát vòng lặp kết thúc chương trình
                if not task:
                    logger.info("🎉 Tất cả tác vụ trong hàng đợi đã được xử lý xong. Hệ thống dừng.")
                    break
    
                target_url = task["target_url"]
                task_id = task["id"]
                logger.info(f"🚀 Nhận tác vụ ID [{task_id}]: Đang xử lý nguồn {target_url}")
    
                try:
                    # Bước 3: Gọi module TruyenFullSource xử lý logic mạng và bóc tách HTML
                    # Tách lấy slug từ URL để truyền vào hàm crawl_novel
                    slug = target_url.strip("/").split("/")[-1]
                    raw_novel_data = self.scraper.crawl_novel(slug)
                    raw_novel_data["slug"] = slug
    
                    # Bước 4: Mở một SQLiteSession bọc Transaction để đẩy toàn bộ kết quả vào DB
                    with SQLiteSession(self.engine) as session:
                        # Lấy ID của Website TruyenFull để làm khóa ngoại
                        cursor = session.execute("SELECT id FROM websites WHERE base_url = ?;", ("https://truyenfull.io",))
                        website_id = cursor.fetchone()["id"]
    
                        # Ghi thông tin truyện (Upsert)
                        novel_id = self.novel_repo.create_or_update(session, website_id=website_id, novel_data=raw_novel_data)
                        
                        # Ghi hàng loạt chương truyện thu thập được bằng executemany siêu tốc
                        self.chapter_repo.bulk_insert_chapters(
                            session=session,
                            novel_id=novel_id,
                            chapters_data=raw_novel_data["chapters_content"]
                        )
                        
                        # Đánh dấu tác vụ COMPLETED hoàn thành mỹ mãn
                        self.task_repo.update_task_status(session, task_id, "COMPLETED")
                    
                    logger.info(f"✅ Tác vụ ID [{task_id}] hoàn thành xuất sắc. Đã lưu truyện '{raw_novel_data['title']}'.")
    
                except Exception as e:
                    # Bước 5: Nếu có bất kỳ lỗi mạng, lỗi parse HTML hoặc lỗi ghi đĩa, cập nhật FAILED
                    logger.error(f"❌ Tác vụ ID [{task_id}] thất bại do lỗi: {e}")
                    with SQLiteSession(self.engine) as session:
                        self.task_repo.update_task_status(session, task_id, "FAILED", error_message=str(e))
                
                # Nghỉ ngắn giữa các Task lớn để bảo vệ hệ thống và giả lập hành vi người dùng
                time.sleep(2.0)
    
        def close(self) -> None:
            """Giải phóng và đóng các kết nối mạng khi tắt máy."""
            logger.info("Đang đóng các phiên kết nối HTTP Client...")
            self.client.close()
    
    if __name__ == "__main__":
        coordinator = CrawlerCoordinator()
        try:
            coordinator.run()
        except KeyboardInterrupt:
            logger.warning("\n⚠️ Nhận lệnh ngắt từ bàn phím (Ctrl+C). Đang dừng hệ thống an toàn...")
        finally:
            coordinator.close()
            logger.info("Hệ thống tắt hoàn toàn. Tạm biệt!")
    

Hãy thận trọng khi sử dụng mã.

* * *

**🛠️ Cách thức vận hành toàn bộ dự án của bạn**

Lúc này, cấu trúc toàn bộ mã nguồn của bạn đã liên kết với nhau một cách hoàn hảo. Để khởi động toàn bộ dây chuyền cào truyện tự động, bạn chỉ cần mở Terminal tại thư mục gốc của dự án và gõ lệnh duy nhất:

bash
    
    
    python main.py
    

Hãy thận trọng khi sử dụng mã.

**Hệ thống sẽ tự động thực hiện luồng:**

  1. Tạo tệp `crawler_production.db` và nạp cấu trúc bảng qua `Engine` và `Driver`.
  2. Tự động bơm 2 link truyện mẫu vào bảng `tasks`.
  3. Bắt đầu lấy link `truyen-chu-tien`, giả lập trình duyệt bằng `HTTPClient`, bypass giãn cách bằng `RateLimiter`, cào nội dung qua `TruyenFullParser`.
  4. Mở `SQLiteSession` ghi dữ liệu an toàn vào đĩa và tự động Commit.
  5. Tiếp tục chuyển sang link `pham-nhan-tu-tien` cho đến khi sạch hàng đợi.



Để hệ thống trở nên mạnh mẽ hơn nữa, bạn có muốn tích hợp thêm bộ **argparse** vào file `main.py` để có thể truyền link truyện trực tiếp từ terminal (ví dụ: `python main.py --add-task https://...`) không?

