Version:0.9 StartHTML:0000000105 EndHTML:0000021837 StartFragment:0000000141 EndFragment:0000021801 

Q:

Schema + Migration (code hoàn chỉnh)

GLAI:

Để hoàn thiện toàn bộ hệ thống lưu trữ bằng SQL thuần, chúng ta cần xây dựng một cơ chế quản lý cấu trúc bảng (**Schema**) kết hợp với bộ kiểm soát phiên bản (**Migration**) thủ công bằng `sqlite3`. Cơ chế này sử dụng một bảng đặc biệt có tên `schema_migrations` để ghi nhận các phiên bản script đã chạy, giúp bạn nâng cấp DB mà không làm mất dữ liệu cũ.

Dưới đây là mã nguồn hoàn chỉnh cho file `schema.py` và `migrations.py` đặt trong thư mục `database/`.

* * *

**📄 database/schema.py**

File này chứa định nghĩa cấu trúc bảng ban đầu (Version 1) và là nơi tập trung danh sách tất cả các bản cập nhật theo thời gian.

python
    
    
    # database/schema.py
    
    # Kịch bản khởi tạo hệ thống ban đầu (Version 1)
    INITIAL_SCHEMA_V1 = """
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
    
    # Mảng lưu trữ lộ trình phát triển của Database (Migration Path)
    # Mỗi phần tử là một Tuple gồm: (Mã_phiên_bản_int, Mô_tả_chuỗi, Câu_lệnh_SQL)
    # Khi bạn muốn thêm cột, tạo index mới... hãy thêm một phần tử vào mảng này.
    MIGRATIONS_REGISTRY = [
        (1, "Khởi tạo cấu trúc bảng nền tảng", INITIAL_SCHEMA_V1),
        
        # Ví dụ bản nâng cấp sau này (Version 2): Tạo Index để tăng tốc độ truy vấn Task và tìm truyện theo slug
        (2, "Tạo chỉ mục index tối ưu tốc độ tìm kiếm", """
            CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
            CREATE INDEX IF NOT EXISTS idx_novels_slug ON novels(slug);
        """),
        
        # Bạn có thể nối dài danh sách (Version 3, 4, 5...) tại đây trong tương lai mà không sợ lỗi code cũ
    ]
    

Hãy thận trọng khi sử dụng mã.

* * *

**📄 database/migrations.py**

Bộ điều phối Migration đảm nhận việc: Tự tạo bảng theo dõi phiên bản, đọc lịch sử đối chiếu, chạy tuần tự các bản cập nhật còn thiếu trong một Transaction an toàn.

python
    
    
    # database/migrations.py
    import logging
    from .engine import SQLiteEngine
    from .session import SQLiteSession
    from .schema import MIGRATIONS_REGISTRY
    
    logger = logging.getLogger(__name__)
    
    class MigrationManager:
        def __init__(self, engine: SQLiteEngine):
            self.engine = engine
    
        def _ensure_migration_table(self) -> None:
            """Đảm bảo bảng lưu lịch sử phiên bản hệ thống luôn tồn tại."""
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """
            # Chạy trực tiếp qua engine để khởi tạo hạ tầng quản lý ban đầu
            self.engine.execute_script(create_table_sql)
    
        def _get_applied_versions(self, session: SQLiteSession) -> set[int]:
            """Lấy danh sách các số phiên bản (Version ID) đã từng chạy trong quá khứ."""
            cursor = session.execute("SELECT version FROM schema_migrations ORDER BY version ASC;")
            return {row["version"] for row in cursor.fetchall()}
    
        def run_migrations(self) -> None:
            """Kiểm tra và áp dụng tuần tự các bản ghi SQL cập nhật cấu trúc database."""
            # 1. Khởi tạo bảng lưu vết phiên bản
            self._ensure_migration_table()
            
            # 2. Sử dụng SQLiteSession bọc toàn bộ chu kỳ nâng cấp vào một Transaction
            with SQLiteSession(self.engine) as session:
                applied_versions = self._get_applied_versions(session)
                
                # Sắp xếp danh sách đăng ký theo thứ tự tăng dần từ nhỏ đến lớn
                sorted_migrations = sorted(MIGRATIONS_REGISTRY, key=lambda x: x[0])
                
                migrated_count = 0
                for version, description, sql_script in sorted_migrations:
                    if version in applied_versions:
                        # Phiên bản này đã chạy rồi -> Bỏ qua
                        continue
                    
                    logger.info(f"[Migration] Đang áp dụng nâng cấp bản v{version}: {description}...")
                    
                    try:
                        # Thực thi kịch bản SQL thay đổi cấu trúc bảng
                        # Lưu ý: sqlite3 khuyên dùng executescript cho chuỗi nhiều câu lệnh, 
                        # chúng ta truy cập đối tượng connection vật lý trực tiếp từ session
                        if session.connection:
                            session.connection.executescript(sql_script)
                        
                        # Ghi nhận trạng thái hoàn thành vào bảng lịch sử
                        session.execute(
                            "INSERT INTO schema_migrations (version, description) VALUES (?, ?);",
                            (version, description)
                        )
                        migrated_count += 1
                        
                    except Exception as e:
                        # Cơ chế Context Manager của SQLiteSession sẽ tự động Rollback toàn bộ 
                        # nếu một câu lệnh trong vòng lặp này bị gãy.
                        logger.critical(f"[Migration] Thất bại nghiêm trọng tại bản v{version}! Chi tiết: {e}")
                        raise e
                        
                if migrated_count > 0:
                    logger.info(f"🎉 Đồng bộ Migration thành công! Đã nâng cấp {migrated_count} phiên bản cấu trúc.")
                else:
                    logger.info(" Database đã ở phiên bản mới nhất. Không cần cập nhật.")
    

Hãy thận trọng khi sử dụng mã.

* * *

**🔄 Cập nhật tích hợp vào Đầu não main.py**

Để hệ thống tự động kiểm tra và chạy Migration mỗi khi khởi động, bạn chỉ cần sửa hàm `setup_environment` trong file **main.py** (lượt chat trước) thành như sau:

python
    
    
    # Trích đoạn điều chỉnh trong file main.py
    
    from database.migrations import MigrationManager # Import thêm quản lý bộ nâng cấp
    
    class CrawlerCoordinator:
        def __init__(self, db_name: str = "crawler_production.db"):
            self.config = DatabaseConfig(db_name=db_name)
            self.engine = SQLiteEngine(self.config)
            
            # Đổi cơ chế gọi script tĩnh bằng bộ quản lý Migration thông minh
            self.migration_mgr = MigrationManager(self.engine)
            
            self.novel_repo = NovelRepository()
            self.chapter_repo = ChapterRepository()
            self.task_repo = TaskRepository()
            
            self.client = HTTPClient(delay_range=(1.5, 3.0), max_retries=3)
            self.scraper = TruyenFullSource(client=self.client)
    
        def setup_environment(self) -> None:
            """Kích hoạt Migration và sinh dữ liệu mồi ban đầu."""
            # Gọi chạy cập nhật / tạo cấu trúc bảng tự động
            self.migration_mgr.run_migrations()
            
            # Tạo dữ liệu mồi mẫu (Seed Data) nếu chưa có tác vụ
            with SQLiteSession(self.engine) as session:
                cursor = session.execute("SELECT COUNT(*) as total FROM tasks;")
                if cursor.fetchone()["total"] == 0:
                    logger.info("Database trống. Đang mồi tác vụ test vào bảng tasks...")
                    session.execute(
                        "INSERT INTO tasks (target_url, status) VALUES (?, ?);",
                        ("https://truyenfull.io", "PENDING")
                    )
    

Hãy thận trọng khi sử dụng mã.

Giờ đây, mỗi lần website đích thay đổi khiến bạn cần bổ sung thêm trường thông tin (ví dụ: cột `cover_image` vào bảng `novels`), bạn chỉ việc mở file `database/schema.py` ra và khai báo thêm phần tử `(3, "Bổ sung cột ảnh bìa truyện", "ALTER TABLE novels ADD COLUMN cover_image TEXT DEFAULT '';")` vào cuối mảng `MIGRATIONS_REGISTRY`. Hệ thống sẽ tự xử lý mượt mà khi chạy lại file `main.py`.

Hệ thống Core và Database của bạn hiện tại đã đạt độ hoàn thiện rất cao. Bạn có muốn tích hợp thêm bộ **Log File Writer** để ghi lại lịch sử lỗi cào truyện ra file text phục vụ việc kiểm tra sau này không?

