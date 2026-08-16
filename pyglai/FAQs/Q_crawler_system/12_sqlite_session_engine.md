Version:0.9 StartHTML:0000000105 EndHTML:0000075723 StartFragment:0000000141 EndFragment:0000075687 

### sqlitesession - sqlteengine

Để đáp ứng trọn vẹn mô hình kiến trúc 3 tầng (**Layered Architecture**) bọc trong thư mục `app/`, hai thành phần **SQLiteEngine** và **SQLiteSession** cần được thiết kế lại nhằm đóng vai trò như một bộ quản lý kết nối và điều phối giao dịch (Unit of Work) chuyên nghiệp.

  * **SQLiteEngine** đóng vai trò là Singleton/Factory quản lý cấu hình và khởi tạo Driver kết nối.

  * **SQLiteSession** đóng vai trò là một **Context Manager** quản lý Transaction, cung cấp phương thức `execute` và tự động `commit/rollback`.



Dưới đây là mã nguồn thiết kế chi tiết, tối ưu hiệu năng ghi của Crawler và đồng bộ tuyệt đối với tầng Service/Repository bạn đã xây dựng.

* * *

**📄 app/database/config.py**

Tập trung toàn bộ cấu hình hệ thống file và các câu lệnh `PRAGMA` tối ưu tốc độ I/O cho SQLite khi cào dữ liệu lớn.

python
    
    
    import os
    
    class DatabaseConfig:
        def __init__(self, db_name: str = "crawler.db", timeout: float = 30.0):
            # Định vị file database nằm tại thư mục gốc của dự án app/..
            self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../{db_name}"))
            self.timeout = timeout
            
            # Cấu hình tối ưu ghi siêu tốc cho SQLite (WAL mode giúp đọc/ghi song song)
            self.pragmas = {
                "foreign_keys": "ON",            # Bật ràng buộc khóa ngoại bắt buộc
                "journal_mode": "WAL",           # Write-Ahead Logging
                "synchronous": "NORMAL",         # Giảm số lần ghi đồng bộ trực tiếp xuống ổ đĩa vật lý
                "cache_size": -2000              # Sử dụng ~2MB bộ nhớ đệm cache
            }
    
        @property
        def connection_string(self) -> str:
            return self.db_path
    

Hãy thận trọng khi sử dụng mã.

* * *

**📄 app/database/driver.py**

Chịu trách nhiệm trực tiếp giao tiếp với thư viện hệ thống `sqlite3` và gán định dạng dữ liệu trả về dạng dòng-từ-điển (`sqlite3.Row`).

python
    
    
    import sqlite3
    from .config import DatabaseConfig
    
    class SQLiteDriver:
        def __init__(self, config: DatabaseConfig):
            self.config = config
            self._raw_conn: sqlite3.Connection | None = None
    
        def connect(self) -> sqlite3.Connection:
            """Khai mở kết nối vật lý và cấu hình môi trường SQLite."""
            self._raw_conn = sqlite3.connect(
                self.config.connection_string,
                timeout=self.config.timeout
            )
            # Giúp truy cập dữ liệu dạng từ điển: row["title"] thay vì row[0]
            self._raw_conn.row_factory = sqlite3.Row
            self._apply_pragmas()
            return self._raw_conn
    
        def _apply_pragmas(self) -> None:
            if not self._raw_conn:
                return
            cursor = self._raw_conn.cursor()
            for key, value in self.config.pragmas.items():
                cursor.execute(f"PRAGMA {key} = {value};")
    
        def disconnect(self) -> None:
            """Đóng kết nối vật lý một cách an toàn."""
            if self._raw_conn:
                self._raw_conn.close()
                self._raw_conn = None
    

Hãy thận trọng khi sử dụng mã.

* * *

**📄 app/database/engine.py**

Đóng vai trò trung tâm lưu giữ cấu hình. Tầng Service sẽ giữ duy nhất một instance của `SQLiteEngine` xuyên suốt vòng đời ứng dụng để sinh ra các Session khi cần làm việc.

python
    
    
    from .config import DatabaseConfig
    from .driver import SQLiteDriver
    
    class SQLiteEngine:
        def __init__(self, config: DatabaseConfig | None = None):
            self.config = config or DatabaseConfig()
    
        def create_driver(self) -> SQLiteDriver:
            """Sinh ra một đối tượng điều khiển kết nối Driver độc lập."""
            return SQLiteDriver(self.config)
    
        def execute_script(self, script_sql: str) -> None:
            """Hàm tiện ích chạy nhanh kịch bản SQL (ví dụ: Tạo bảng hoặc chạy Migration)."""
            driver = self.create_driver()
            raw_conn = driver.connect()
            try:
                raw_conn.executescript(script_sql)
                raw_conn.commit()
            finally:
                driver.disconnect()
    

Hãy thận trọng khi sử dụng mã.

* * *

**📄 app/database/session.py**

Quản lý chu kỳ sống của một Transaction (Unit of Work). Nó hoạt động như một lá chắn bảo vệ dữ liệu: **Cam kết ghi (commit)** nếu toàn bộ khối lệnh hoàn hảo, hoặc **Xóa bỏ trạng thái lỗi (rollback)** nếu có bất kỳ sự cố ngoại lệ nào xảy ra ở tầng Service/Repository.

python
    
    
    import sqlite3
    import logging
    from typing import Any
    from .engine import SQLiteEngine
    
    logger = logging.getLogger(__name__)
    
    class SQLiteSession:
        def __init__(self, engine: SQLiteEngine):
            self.engine = engine
            self.driver = self.engine.create_driver()
            self.connection: sqlite3.Connection | None = None
    
        def __enter__(self) -> "SQLiteSession":
            """Kích hoạt transaction khi bắt đầu khối lệnh 'with'."""
            self.connection = self.driver.connect()
            return self
    
        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
            """Quản lý đóng/ngắt tự động transaction khi thoát khối lệnh 'with'."""
            if self.connection:
                try:
                    if exc_type is not None:
                        # Phát hiện có lỗi xảy ra ở tầng trên -> Hoàn tác ngay lập tức
                        self.connection.rollback()
                        logger.error(f"[SQLiteSession] Phát hiện lỗi: {exc_val}. Đang thực hiện HỦY GIAO DỊCH (Rollback)...")
                    else:
                        # Mọi thứ chạy trơn tru mượt mà -> Lưu dữ liệu vĩnh viễn
                        self.connection.commit()
                finally:
                    # Ngắt kết nối vật lý trả lại tài nguyên cho hệ điều hành
                    self.driver.disconnect()
                    self.connection = None
            
            # Trả về False để Python tiếp tục ném lỗi lên tầng điều phối chính (main.py) xử lý/log lỗi
            return False  
    
        def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
            """Thực thi câu lệnh SQL truy vấn hoặc cập nhật đơn lẻ."""
            if not self.connection:
                raise RuntimeError("Lỗi hệ thống: Session chưa được kích hoạt. Hãy bọc lệnh trong cú pháp 'with'.")
            return self.connection.execute(sql, params)
    
        def executemany(self, sql: str, params_list: list[tuple]) -> sqlite3.Cursor:
            """Thực thi ghi dữ liệu hàng loạt tốc độ cao (Bulk Insert cho danh sách chương)."""
            if not self.connection:
                raise RuntimeError("Lỗi hệ thống: Session chưa được kích hoạt. Hãy bọc lệnh trong cú pháp 'with'.")
            return self.connection.executemany(sql, params_list)
    

Hãy thận trọng khi sử dụng mã.

* * *

**💡 Cách thức vận hành nhịp nhàng trong mô hình 3 tầng**

Để thấy rõ sức mạnh của thiết kế này, bạn hãy quan sát cách tầng **Service** (nơi nắm giữ luật nghiệp vụ) điều phối `SQLiteEngine` và `SQLiteSession` để giao dịch an toàn với **Repository** :

python
    
    
    # app/services/novel_service.py (Mẫu minh họa)
    from app.database.engine import SQLiteEngine
    from app.database.session import SQLiteSession
    from app.repository.novel_repository import NovelRepository
    from app.model.novel import Novel
    
    class NovelService:
        def __init__(self, engine: SQLiteEngine):
            self.engine = engine  # Nhận engine dùng chung
            self.novel_repo = NovelRepository()
    
        def save_crawled_novel_pipeline(self, novel_obj: Novel, chapters_data: list[dict]):
            """Bọc toàn bộ chuỗi hành động lưu Truyện + Lưu Chương vào một phiên làm việc duy nhất."""
            
            # Bắt đầu một Transaction an toàn
            with SQLiteSession(self.engine) as session:
                
                # Hành động 1: Ghi nhận thông tin truyện thông qua Repository nhận session
                novel_id = self.novel_repo.save(session, novel_obj)
                
                # Giả lập Hành động 2: Nếu có lỗi phát sinh ở đây (Ví dụ: dữ liệu chương lỗi cú pháp)
                if not chapters_data:
                    raise ValueError("Danh sách chương truyện trống! Hủy bỏ tác vụ ghi để tránh rác DB.")
                    
                # (Nếu không lỗi) -> Thực hiện ghi tiếp danh sách chương...
                # self.chapter_repo.bulk_insert(session, novel_id, chapters_data)
    
            # Kết thúc khối 'with': Tự động COMMIT xuống file crawler.db
    

Hãy thận trọng khi sử dụng mã.

Nếu bạn cần viết tiếp phần logic xử lý cho **app/services/task_service.py** để quản lý trạng thái các Task (`PENDING`, `RUNNING`, `COMPLETED`) dựa trên bộ Engine-Session mới này, hãy cho tôi biết nhé!

### task-service.py

Dưới đây là thiết kế trọn vẹn cho cấu trúc quản lý tác vụ (Task Management) theo mô hình 3 tầng, sử dụng bộ

`SQLiteEngine` và `SQLiteSession` vừa thiết kế để điều phối trạng thái hàng đợi cào truyện (`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`).

* * *

**📦 1. TẦNG DATA MODEL (app/model/task.py)**

Sử dụng `dataclasses` kết hợp với `Enum` để định nghĩa thực thể Task tường minh về kiểu dữ liệu.

python
    
    
    # app/model/task.py
    from dataclasses import dataclass, asdict
    from enum import Enum
    from typing import Optional, Any
    
    class TaskStatus(Enum):
        PENDING = "PENDING"
        RUNNING = "RUNNING"
        COMPLETED = "COMPLETED"
        FAILED = "FAILED"
    
    @dataclass
    class Task:
        target_url: str
        id: Optional[int] = None
        status: TaskStatus = TaskStatus.PENDING
        error_message: str = ""
        updated_at: Optional[str] = None
    
        def __post_init__(self):
            # Tự động chuẩn hóa trạng thái nếu truyền vào dạng chuỗi (String) từ DB Row
            if isinstance(self.status, str):
                try:
                    self.status = TaskStatus(self.status)
                except ValueError:
                    self.status = TaskStatus.PENDING
    
        def to_dict(self) -> dict[str, Any]:
            """Chuyển đổi thực thể Object thành Dictionary sạch."""
            data = asdict(self)
            data["status"] = self.status.value  # Ép giá trị Enum thành chuỗi thô
            return data
    

Hãy thận trọng khi sử dụng mã.

* * *

**📦 2. TẦNG DATA ACCESS / REPOSITORY (app/repository/task_repository.py)**

Chỉ tập trung xử lý câu lệnh SQL thuần để đọc/ghi trạng thái Task thông qua tham số `session`.

python
    
    
    # app/repository/task_repository.py
    import sqlite3
    from typing import Optional
    from app.database.session import SQLiteSession
    from app.model.task import Task, TaskStatus
    
    class TaskRepository:
        def get_next_pending(self, session: SQLiteSession) -> Optional[Task]:
            """Lấy tác vụ đầu tiên đang ở trạng thái PENDING (FIFO)."""
            query = "SELECT * FROM tasks WHERE status = 'PENDING' ORDER BY id ASC LIMIT 1;"
            cursor = session.execute(query)
            row = cursor.fetchone()
            return self._map_row_to_entity(row) if row else None
    
        def add_task(self, session: SQLiteSession, target_url: str) -> int:
            """Thêm một link truyện mới vào hàng đợi (bỏ qua nếu đã tồn tại link)."""
            query = "INSERT OR IGNORE INTO tasks (target_url, status) VALUES (?, 'PENDING');"
            cursor = session.execute(query, (target_url,))
            return cursor.lastrowid
    
        def update_status(self, session: SQLiteSession, task_id: int, status: TaskStatus, error_message: str = "") -> bool:
            """Cập nhật trạng thái và thông báo lỗi (nếu có) của một Task."""
            query = """
                UPDATE tasks 
                SET status = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?;
            """
            cursor = session.execute(query, (status.value, error_message, task_id))
            return cursor.rowcount > 0
    
        def _map_row_to_entity(self, row: sqlite3.Row) -> Task:
            """Hàm biến đổi cấu trúc bảng thô thành thực thể Python Object."""
            return Task(
                id=row["id"],
                target_url=row["target_url"],
                status=TaskStatus(row["status"]),
                error_message=row["error_message"],
                updated_at=row["updated_at"]
            )
    

Hãy thận trọng khi sử dụng mã.

* * *

**📦 3. TẦNG LOGIC NGHIỆP VỤ / SERVICE (app/services/task_service.py)**

Quản lý luồng logic bọc Transaction. Đảm bảo khi một luồng (thread) lấy Task, trạng thái của Task đó phải được chuyển sang `RUNNING` lập tức bên trong một Session để tránh các luồng song song nhặt trùng Task.

python
    
    
    # app/services/task_service.py
    import logging
    from typing import Optional
    from app.database.engine import SQLiteEngine
    from app.database.session import SQLiteSession
    from app.model.task import Task, TaskStatus
    from app.repository.task_repository import TaskRepository
    
    logger = logging.getLogger(__name__)
    
    class TaskService:
        def __init__(self, engine: SQLiteEngine):
            self.engine = engine
            self.task_repo = TaskRepository()
    
        def fetch_and_lock_next_task(self) -> Optional[Task]:
            """
            Lấy ra tác vụ kế tiếp và khóa nó lại bằng trạng thái RUNNING.
            Bọc trong một Giao dịch (Transaction) an toàn.
            """
            with SQLiteSession(self.engine) as session:
                task = self.task_repo.get_next_pending(session)
                
                if task:
                    # Cập nhật ngay lập tức sang trạng thái RUNNING trước khi trả về
                    self.task_repo.update_status(session, task.id, TaskStatus.RUNNING)
                    task.status = TaskStatus.RUNNING
                    logger.info(f"[TaskService] Đã khóa thành công Task ID [{task.id}] -> RUNNING")
                    return task
                    
                return None
    
        def mark_task_as_completed(self, task_id: int) -> None:
            """Đánh dấu tác vụ hoàn thành thành công."""
            with SQLiteSession(self.engine) as session:
                self.task_repo.update_status(session, task_id, TaskStatus.COMPLETED)
                logger.info(f"[TaskService] Đã cập nhật Task ID [{task_id}] -> COMPLETED")
    
        def mark_task_as_failed(self, task_id: int, error_reason: str) -> None:
            """Đánh dấu tác vụ thất bại kèm lý do lỗi để phục vụ debug."""
            with SQLiteSession(self.engine) as session:
                self.task_repo.update_status(session, task_id, TaskStatus.FAILED, error_message=error_reason)
                logger.error(f"[TaskService] Đã cập nhật Task ID [{task_id}] -> FAILED. Lý do: {error_reason}")
    
        def add_new_urls_to_queue(self, urls: list[str]) -> int:
            """Thêm danh sách link truyện mới cần cào vào hàng đợi."""
            added_count = 0
            with SQLiteSession(self.engine) as session:
                for url in urls:
                    if url.strip():
                        self.task_repo.add_task(session, url.strip())
                        added_count += 1
            logger.info(f"[TaskService] Đã đẩy thêm {added_count} liên kết vào hàng đợi.")
            return added_count
    

Hãy thận trọng khi sử dụng mã.

* * *

**🚀 Tích hợp sạch sẽ vào bộ điều phối main.py**

Khi có `TaskService` và `NovelService`, luồng xử lý chính của bạn sẽ không còn dính dáng tới câu lệnh SQL hay bọc cú pháp `with SQLiteSession` phức tạp nữa, code đọc như văn bản:

python
    
    
    # Trích đoạn minh họa luồng chạy điều phối trong main.py mới
    from app.database.engine import SQLiteEngine
    from app.services.task_service import TaskService
    from app.services.novel_service import NovelService
    
    class CrawlerCoordinator:
        def __init__(self):
            self.engine = SQLiteEngine()
            self.task_service = TaskService(self.engine)
            self.novel_service = NovelService(self.engine)
            # Khởi tạo plugin_manager, http_client...
    
        def start_loop(self):
            while True:
                # 1. Lấy và tự động khóa Task an toàn qua Service
                task = self.task_service.fetch_and_lock_next_task()
                
                if not task:
                    print("🎉 Sạch bóng hàng đợi! Hệ thống dừng.")
                    break
                    
                try:
                    # 2. Thực hiện cào dữ liệu từ plugin (giả lập kết quả trả về `raw_data`)
                    # website_id = 1, slug = "chu-tien"
                    raw_data = {"title": "Chu Tiên", "author": "Tiêu Đỉnh"} 
                    
                    # 3. Đẩy dữ liệu qua NovelService xử lý nghiệp vụ lưu trữ
                    self.novel_service.process_crawled_novel(website_id=1, slug="chu-tien", raw_data=raw_data)
                    
                    # 4. Đánh dấu hoàn thành Task
                    self.task_service.mark_task_as_completed(task.id)
                    
                except Exception as e:
                    # 5. Nếu có lỗi mạng/lỗi parse, đánh dấu Task thất bại kèm log lỗi
                    self.task_service.mark_task_as_failed(task.id, error_reason=str(e))
    

Hãy thận trọng khi sử dụng mã.

Bộ khung 3 tầng (`Model` -> `Repository` -> `Service`) bọc trong lõi `Engine/Session` tự xây dựng bằng SQL thuần của bạn hiện nay đã hoàn hảo, bảo mật và đồng bộ.

Bạn có muốn phát triển thêm bộ **API endpoints sử dụng FastAPI** đặt ở tầng trên cùng (`app/api/`) để làm giao diện Dashboard theo dõi trạng thái các Task này trực quan không?

### API endpoints sử dụng FastAPI

Để xây dựng giao diện Dashboard và cung cấp API theo dõi hệ thống crawler, chúng ta sẽ cài đặt thư viện **FastAPI** và **Uvicorn** ở tầng trên cùng (`app/api/`).

Tầng API sẽ gọi trực tiếp xuống tầng **Service** đã dựng để lấy dữ liệu, đảm bảo tuân thủ tuyệt đối kiến trúc 3 lớp, giữ cho mã nguồn tách biệt hoàn toàn giữa logic hiển thị và logic lưu trữ dữ liệu.

* * *

**📦 1. TẬNG API ENDPOINTS (app/api/routes.py)**

File này định nghĩa các đường dẫn công khai (endpoints) để kiểm tra trạng thái Crawler, danh sách truyện và thêm nhiệm vụ mới.

python
    
    
    # app/api/routes.py
    from fastapi import APIRouter, Depends, HTTPException, Query
    from pydantic import BaseModel, HttpUrl
    from typing import List, Dict, Any
    
    from app.database.engine import SQLiteEngine
    from app.services.task_service import TaskService
    from app.services.novel_service import NovelService
    
    router = APIRouter()
    
    # Khai báo cấu trúc dữ liệu đầu vào (Request Body) bằng Pydantic
    class TaskCreateRequest(BaseModel):
        urls: List[str]
    
    # Sử dụng Dependency Injection để khởi tạo Service dùng chung cho mỗi Request
    def get_task_service() -> TaskService:
        # Ở môi trường thực tế, instance engine nên được khởi tạo một lần ở file main/app chính
        from main import coordinator
        return TaskService(coordinator.engine)
    
    def get_novel_service() -> NovelService:
        from main import coordinator
        return NovelService(coordinator.engine)
    
    @router.get("/stats", summary="Lấy thống kê tổng quan hệ thống")
    def get_crawler_stats(task_service: TaskService = Depends(get_task_service)):
        """Trả về số lượng tác vụ theo từng trạng thái (PENDING, RUNNING, COMPLETED, FAILED)."""
        from app.database.session import SQLiteSession
        
        query = "SELECT status, COUNT(*) as count FROM tasks GROUP BY status;"
        stats = {"PENDING": 0, "RUNNING": 0, "COMPLETED": 0, "FAILED": 0}
        
        with SQLiteSession(task_service.engine) as session:
            cursor = session.execute(query)
            for row in cursor.fetchall():
                stats[row["status"]] = row["count"]
                
        return {"success": True, "data": stats}
    
    @router.post("/tasks", summary="Thêm link truyện vào hàng đợi cào")
    def add_tasks(payload: TaskCreateRequest, task_service: TaskService = Depends(get_task_service)):
        """Nhận danh sách URL truyện và đẩy vào bảng `tasks`."""
        if not payload.urls:
            raise HTTPException(status_code=400, detail="Danh sách liên kết không được để trống.")
            
        added_count = task_service.add_new_urls_to_queue(payload.urls)
        return {"success": True, "message": f"Đã thêm thành công {added_count} tác vụ vào hàng đợi."}
    
    @router.get("/tasks", summary="Lấy danh sách tác vụ trong hệ thống")
    def list_tasks(
        status: str = Query(None, description="Lọc theo trạng thái Task (PENDING, RUNNING...)"),
        limit: int = Query(10, ge=1, le=100),
        task_service: TaskService = Depends(get_task_service)
    ):
        from app.database.session import SQLiteSession
        
        query = "SELECT * FROM tasks"
        params = []
        if status:
            query += " WHERE status = ?"
            params.append(status.upper())
        query += " ORDER BY id DESC LIMIT ?;"
        params.append(limit)
        
        with SQLiteSession(task_service.engine) as session:
            cursor = session.execute(query, tuple(params))
            tasks = [dict(row) for row in cursor.fetchall()]
            
        return {"success": True, "data": tasks}
    
    @router.get("/novels", summary="Xem danh sách truyện đã cào thành công")
    def list_novels(limit: int = 20, novel_service: NovelService = Depends(get_novel_service)):
        from app.database.session import SQLiteSession
        
        with SQLiteSession(novel_service.engine) as session:
            # Gọi trực tiếp qua repository từ Service hoặc query nhanh dạng dict
            cursor = session.execute("SELECT id, title, slug, author, status, genres FROM novels ORDER BY id DESC LIMIT ?;", (limit,))
            novels = [dict(row) for row in cursor.fetchall()]
            
        return {"success": True, "data": novels}
    

Hãy thận trọng khi sử dụng mã.

* * *

**📦 2. KHỞI TẠO ĐẦU NÃO API SERVER (app/api/main_api.py)**

Cấu hình ứng dụng FastAPI, tích hợp Middleware chống lỗi chặn tên miền chéo (CORS) để giao diện Front-end (React/Vue) có thể gọi API bình thường.

python
    
    
    # app/api/main_api.py
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from app.api.routes import router as api_router
    
    def create_app() -> FastAPI:
        app = FastAPI(
            title="Crawler Management Dashboard API",
            description="Hệ thống API điều phối và theo dõi tiến độ cào truyện tự động",
            version="1.0.0"
        )
    
        # Cấu hình CORS an toàn cho phép Dashboard truy cập
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Trong thực tế sản phẩm nên chỉ định rõ Domain cụ thể
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
        # Đăng ký các tuyến đường API kèm tiền tố /api/v1
        app.include_router(api_router, prefix="/api/v1")
    
        @app.get("/", tags=["Trang chủ"])
        def root():
            return {
                "message": "Crawler API đang hoạt động bình thường.",
                "docs": "/docs"  # Đường dẫn tài liệu Swagger UI tự sinh của FastAPI
            }
    
        return app
    

Hãy thận trọng khi sử dụng mã.

* * *

**🔄 3. TÍCH HỢP CHẠY SONG SONG TRONG THƯ MỤC GỐC (main.py)**

Do Crawler chạy một **Vòng lặp vô hạn (Infinite Loop)** để cào truyện, còn FastAPI cũng cần một **Tiến trình vô hạn** để lắng nghe cổng mạng (Port 8000), bạn cần sử dụng thư viện `threading` của Python để chạy song song cả 2 nhiệm vụ này mà không làm nghẽn mã nguồn của nhau.

python
    
    
    # main.py (File gốc dự án được nâng cấp)
    import sys
    import time
    import logging
    import threading
    import uvicorn
    
    from app.database.config import DatabaseConfig
    from app.database.engine import SQLiteEngine
    from database.schema import CREATE_TABLES_SQL  # Schema từ migration của bạn
    from database.migrations import MigrationManager
    
    from app.services.task_service import TaskService
    from app.services.novel_service import NovelService
    from plugins.base.http_client import HTTPClient
    from plugins.plugin_manager import PluginManager
    
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger(__name__)
    
    class GlobalCoordinator:
        def __init__(self):
            self.engine = SQLiteEngine(DatabaseConfig(db_name="crawler_production.db"))
            self.task_service = TaskService(self.engine)
            self.novel_service = NovelService(self.engine)
            
            self.client = HTTPClient(delay_range=(2.0, 4.0))
            self.plugin_manager = PluginManager(client=self.client)
    
        def run_crawler_worker(self):
            """Tiến trình Worker chạy ngầm chuyên nhặt task ra cào dữ liệu."""
            # Chạy migration đồng bộ bảng trước
            MigrationManager(self.engine).run_migrations()
            self.plugin_manager.discover_and_load_plugins()
            
            logger.info("👷 Worker Crawler ngầm đã kích hoạt thành công.")
            while True:
                try:
                    task = self.task_service.fetch_and_lock_next_task()
                    if not task:
                        # Nếu hết việc, ngủ 5 giây rồi dậy quét hàng đợi tiếp thay vì tắt app
                        time.sleep(5.0)
                        continue
    
                    logger.info(f"[Worker] Đang xử lý: {task.target_url}")
                    
                    # Giả lập xác định plugin_id dựa vào URL (ví dụ URL chứa 'truyenfull')
                    plugin_id = "truyenfull" if "truyenfull" in task.target_url else "tangthuvien"
                    slug = task.target_url.strip("/").split("/")[-1]
                    
                    scraper = self.plugin_manager.get_source_instance(plugin_id)
                    raw_data = scraper.crawl_novel(slug)
                    
                    # Lưu vào DB
                    self.novel_service.process_crawled_novel(website_id=1, slug=slug, raw_data=raw_data)
                    self.task_service.mark_task_as_completed(task.id)
                    
                except Exception as e:
                    if 'task' in locals() and task:
                        self.task_service.mark_task_as_failed(task.id, error_reason=str(e))
                    logger.error(f"[Worker] Lỗi thực thi tác vụ: {e}")
                    time.sleep(3.0)
    
    # Khởi tạo thực thể Coordinator toàn cục để API routes có thể nạp chéo engine dữ liệu
    coordinator = GlobalCoordinator()
    
    if __name__ == "__main__":
        # 1. Kích hoạt luồng Worker Crawler chạy ngầm (Daemon thread để tự tắt khi tắt app chính)
        crawler_thread = threading.Thread(target=coordinator.run_crawler_worker, daemon=True)
        crawler_thread.start()
    
        # 2. Khởi chạy API Server FastAPI ở luồng chính (Main Thread)
        from app.api.main_api import create_app
        app = create_app()
        
        logger.info("🚀 Khởi chạy API HTTP Server tại địa chỉ http://127.0.0.1:8000")
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
    

Hãy thận trọng khi sử dụng mã.

* * *

**🛠️ Cách thức vận hành và Kiểm tra tính năng**

Cài đặt thư viện bổ sung qua terminal:

bash
    
    
    pip install fastapi uvicorn pydantic
    

Hãy thận trọng khi sử dụng mã.

Khởi chạy hệ thống bằng một câu lệnh duy nhất tại thư mục gốc:

bash
    
    
    python main.py
    

Hãy thận trọng khi sử dụng mã.

Lúc này, bạn hãy mở trình duyệt web lên và truy cập vào đường dẫn: **http://127.0.0**. Giao diện tài liệu tương tác **Swagger UI** của FastAPI sẽ hiển thị toàn bộ hệ thống API trực quan.

**Bạn có thể kiểm tra ngay lập tức:**

  1. Thực hiện gọi `GET /api/v1/stats` để xem biểu đồ số lượng Task hiện tại.
  2. Thực hiện gọi `POST /api/v1/tasks` truyền vào một danh sách các link truyện mới. Worker ngầm trong `main.py` sẽ lập tức phát hiện trạng thái `PENDING`, tự động nhặt và tiến hành cào lưu vào DB thời gian thực.



Hệ thống của bạn lúc này đã trở thành một hệ quản trị **Crawler Engine chuyên nghiệp hoàn chỉnh**. Bạn có cần hỗ trợ thiết kế thêm phần **Xác thực bảo mật (API Key / JWT Token Auth)** để chỉ những người có tài khoản mới được phép thêm link cào truyện vào hệ thống không?

