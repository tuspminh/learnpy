Để xây dựng cơ chế Crawl State / Progress Tracking (Quản lý Tiến độ) theo đúng tinh thần Domain-Driven Design (DDD), chúng ta sẽ thiết kế một Aggregate Root mới có tên là `CrawlJob` (hoặc `CrawlProgress`).

Thực thể này chịu trách nhiệm quản lý trạng thái, danh sách các chương cần cào, chương nào thành công, chương nào thất bại, và lý do lỗi. Khi ứng dụng bị sập, hệ thống chỉ cần tải `CrawlJob` từ SQLite lên và tiếp tục xử lý các chương chưa hoàn thành.

* * *

## 1\. Thiết kế Tầng Domain (`domain/crawl_job.py`)

Tách biệt trạng thái của một tác vụ cào bằng các Value Objects (`JobId`, `ChapterStatus`) và một Aggregate Root (`CrawlJob`).
    
    
    from dataclasses import dataclass
    from enum import Enum
    from typing import List, Dict, Optional
    from datetime import datetime
    
    class JobStatus(Enum):
        PENDING = "PENDING"
        RUNNING = "RUNNING"
        COMPLETED = "COMPLETED"
        FAILED = "FAILED"
    
    class ChapterStatus(Enum):
        QUEUE = "QUEUE"
        SUCCESS = "SUCCESS"
        FAILED = "FAILED"
    
    @dataclass(frozen=True)
    class JobId:
        value: str  # Định danh duy nhất, ví dụ: "job-linh-vuc-2026-08-25"
    
    @dataclass
    class ChapterTask:
        """Value Object đại diện cho nhiệm vụ cào của một chương cụ thể"""
        chapter_num: int
        url: str
        status: ChapterStatus
        error_message: Optional[str] = None
        updated_at: datetime = datetime.now()
    
    class CrawlJob:
        def __init__(
            self, 
            id: JobId, 
            comic_slug: str, 
            status: JobStatus, 
            tasks: List[ChapterTask],
            created_at: datetime = None
        ):
            self.id = id
            self.comic_slug = comic_slug
            self.status = status
            self.tasks = tasks or []
            self.created_at = created_at or datetime.now()
    
        def start(self):
            """Domain Logic: Đổi trạng thái sang đang chạy"""
            if self.status == JobStatus.COMPLETED:
                raise ValueError("Tác vụ này đã hoàn thành, không thể chạy lại!")
            self.status = JobStatus.RUNNING
    
        def update_chapter_success(self, chapter_num: int):
            """Domain Logic: Đánh dấu chương cào thành công"""
            for task in self.tasks:
                if task.chapter_num == chapter_num:
                    task.status = ChapterStatus.SUCCESS
                    task.error_message = None
                    task.updated_at = datetime.now()
                    break
            self._check_completion()
    
        def update_chapter_failed(self, chapter_num: int, reason: str):
            """Domain Logic: Ghi nhận chương cào thất bại"""
            for task in self.tasks:
                if task.chapter_num == chapter_num:
                    task.status = ChapterStatus.FAILED
                    task.error_message = reason
                    task.updated_at = datetime.now()
                    break
            self.status = JobStatus.FAILED  # Job bị đánh dấu lỗi nhưng vẫn có thể chạy tiếp
    
        def get_pending_tasks(self) -> List[ChapterTask]:
            """Lấy danh sách các chương chưa cào hoặc cào lỗi để chạy tiếp"""
            return [t for t in self.tasks if t.status in (ChapterStatus.QUEUE, ChapterStatus.FAILED)]
    
        def _check_completion(self):
            """Tự động kiểm tra xem toàn bộ các chương đã xong chưa"""
            if all(t.status == ChapterStatus.SUCCESS for t in self.tasks):
                self.status = JobStatus.COMPLETED
    

* * *

## 2\. Định nghĩa Interface Repository (`domain/job_repository.py`)
    
    
    from abc import ABC, abstractmethod
    from typing import Optional
    from .crawl_job import CrawlJob, JobId
    
    class CrawlJobRepository(ABC):
        @abstractmethod
        def save(self, job: CrawlJob) -> None:
            """Lưu hoặc cập nhật trạng thái của toàn bộ Job"""
            pass
    
        @abstractmethod
        def get_by_id(self, job_id: JobId) -> Optional[CrawlJob]:
            """Tải Job kèm theo toàn bộ tiến độ chương từ DB lên RAM"""
            pass
    
        @abstractmethod
        def update_task_status(self, job_id: JobId, chapter_num: int, status: str, error: Optional[str]) -> None:
            """Tối ưu: Chỉ cập nhật trạng thái của đúng 1 chương đơn lẻ khi đang crawl đa luồng"""
            pass
    

* * *

## 3\. Tầng Infrastructure - SQLite Thuần SQL

Chúng ta cần 2 bảng: `crawl_jobs` lưu thông tin chung và `crawl_job_tasks` lưu chi tiết tiến độ từng chương.

## Khởi tạo bảng (`infrastructure/database.py`)
    
    
    def init_job_db(cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crawl_jobs (
                id TEXT PRIMARY KEY,
                comic_slug TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crawl_job_tasks (
                job_id TEXT NOT NULL,
                chapter_num INTEGER NOT NULL,
                url TEXT NOT NULL,
                status TEXT NOT NULL,
                error_message TEXT,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (job_id, chapter_num),
                FOREIGN KEY (job_id) REFERENCES crawl_jobs(id) ON DELETE CASCADE
            )
        """)
    

## Triển khai Repository (`infrastructure/sqlite_job_repository.py`)
    
    
    import sqlite3
    from typing import Optional, List
    from domain.crawl_job import CrawlJob, JobId, ChapterTask, JobStatus, ChapterStatus
    from domain.job_repository import CrawlJobRepository
    
    class SQLiteCrawlJobRepository(CrawlJobRepository):
        def __init__(self, db_path: str):
            self.db_path = db_path
    
        def _get_connection(self):
            conn = sqlite3.connect(self.db_path, timeout=30.0, isolation_level=None)
            conn.execute("PRAGMA journal_mode=WAL;")
            return conn
    
        def save(self, job: CrawlJob) -> None:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("BEGIN TRANSACTION;")
                # 1. Lưu thông tin Job gốc (UPSERT)
                cursor.execute("""
                    INSERT INTO crawl_jobs (id, comic_slug, status, created_at) VALUES (?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET status = excluded.status
                """, (job.id.value, job.comic_slug, job.status.value, job.created_at.isoformat()))
    
                # 2. Lưu hàng loạt danh sách nhiệm vụ chương (Batch INSERT OR IGNORE)
                # Dùng IGNORE để nếu nạp lại Job cũ, cấu trúc danh sách chương không bị ghi đè mất tiến độ cũ
                task_data = [
                    (job.id.value, t.chapter_num, t.url, t.status.value, t.error_message, t.updated_at.isoformat())
                    for t in job.tasks
                ]
                cursor.executemany("""
                    INSERT OR IGNORE INTO crawl_job_tasks (job_id, chapter_num, url, status, error_message, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, task_data)
                cursor.execute("COMMIT;")
            except Exception as e:
                cursor.execute("ROLLBACK;")
                raise e
            finally:
                conn.close()
    
        def update_task_status(self, job_id: JobId, chapter_num: int, status: str, error: Optional[str]) -> None:
            """Cập nhật nhanh tiến độ của 1 chương (Rất quan trọng khi chạy đa luồng)"""
            conn = self._get_connection()
            cursor = conn.cursor()
            from datetime import datetime
            cursor.execute("""
                UPDATE crawl_job_tasks 
                SET status = ?, error_message = ?, updated_at = ?
                WHERE job_id = ? AND chapter_num = ?
            """, (status, error, datetime.now().isoformat(), job_id.value, chapter_num))
            conn.close()
    
        def get_by_id(self, job_id: JobId) -> Optional[CrawlJob]:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Lấy thông tin Job
            cursor.execute("SELECT comic_slug, status, created_at FROM crawl_jobs WHERE id = ?", (job_id.value,))
            job_row = cursor.fetchone()
            if not job_row:
                conn.close()
                return None
            
            # Lấy danh sách Task liên quan
            cursor.execute("SELECT chapter_num, url, status, error_message, updated_at FROM crawl_job_tasks WHERE job_id = ?", (job_id.value,))
            task_rows = cursor.fetchall()
            conn.close()
    
            tasks = [
                ChapterTask(
                    chapter_num=row[0], url=row[1], 
                    status=ChapterStatus(row[2]), error_message=row[3],
                    updated_at=datetime.fromisoformat(row[4])
                ) for row in task_rows
            ]
            return CrawlJob(id=job_id, comic_slug=job_row[0], status=JobStatus(job_row[1]), tasks=tasks, created_at=datetime.fromisoformat(job_row[2]))
    

* * *

## 4\. Tập trung điều phối tại Tầng Application Service

Service này sẽ chịu trách nhiệm bọc luồng xử lý: Kiểm tra Job cũ → Lấy các chương chưa cào → Cào đa luồng → Cập nhật trực tiếp tiến độ vào SQLite.
    
    
    from concurrent.futures import ThreadPoolExecutor
    from domain.crawl_job import CrawlJob, JobId, ChapterTask, JobStatus
    from domain.job_repository import CrawlJobRepository
    from domain.repository import ChapterRepository # Repo lưu truyện từ các phần trước
    
    class ResilientCrawlerService:
        def __init__(self, job_repo: CrawlJobRepository, chapter_repo: ChapterRepository):
            self.job_repo = job_repo
            self.chapter_repo = chapter_repo
    
        def execute_job(self, job_id: JobId, comic_slug: str, all_chapter_urls: List[str]):
            """Khởi chạy tác vụ cào truyện có khả năng tự phục hồi khi sập"""
            
            # 1. Thử tải Job cũ lên xem trước đó đã cào dở chưa
            job = self.job_repo.get_by_id(job_id)
            
            if not job:
                print(f"🎯 Tạo mới tác vụ cào truyện cho {comic_slug}")
                # Nếu chưa có, tạo mới danh sách Task với trạng thái ban đầu là QUEUE
                tasks = [
                    ChapterTask(chapter_num=i+1, url=url, status=ChapterStatus.QUEUE)
                    for i, url in enumerate(all_chapter_urls)
                ]
                job = CrawlJob(id=job_id, comic_slug=comic_slug, status=JobStatus.PENDING, tasks=tasks)
                self.job_repo.save(job)
    
            # 2. Đổi trạng thái sang RUNNING
            job.start()
            self.job_repo.save(job)
    
            # 3. Lấy ra các chương CHƯA cào được (Lọc bỏ các chương đã SUCCESS)
            pending_tasks = job.get_pending_tasks()
            if not pending_tasks:
                print("🎉 Tất cả các chương đã được cào thành công từ trước!")
                return
    
            print(f"🚀 Phát hiện {len(pending_tasks)} chương chưa hoàn thành. Bắt đầu cào...")
    
            # 4. Thực thi cào đa luồng bằng ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=5) as executor:
                executor.map(lambda task: self._crawl_single_task(job.id, job.comic_slug, task), pending_tasks)
    
            # 5. Kiểm tra lại trạng thái cuối cùng và đóng Job
            final_job_state = self.job_repo.get_by_id(job_id)
            final_job_state._check_completion()
            self.job_repo.save(final_job_state)
            print(f"🏁 Trạng thái kết thúc tác vụ: {final_job_state.status.value}")
    
        def _crawl_single_task(self, job_id: JobId, comic_slug: str, task: ChapterTask):
            """Hàm xử lý cào một chương đơn lẻ"""
            try:
                # Giả lập logic cào HTTP (Ví dụ dùng requests/BeautifulSoup)
                # response = requests.get(task.url) ...
                
                # Giả lập lỗi ngẫu nhiên (ví dụ lỗi mạng, timeout ở chương số 5)
                if task.chapter_num == 5:
                    raise RuntimeError("HTTP Error 504: Gateway Timeout")
    
                # Tạo Entity Chapter và lưu vào kho truyện chính (Áp dụng các phần trước)
                # self.chapter_repo.save(new_chapter)
                
                # Cập nhật tiến độ thành công vào SQLite ngay lập tức
                self.job_repo.update_task_status(job_id, task.chapter_num, ChapterStatus.SUCCESS.value, None)
                print(f"✅ Đã cào xong Chương {task.chapter_num}")
    
            except Exception as e:
                # Ghi nhận lỗi chi tiết vào DB để quản trị viên kiểm tra lỗi XPath/Network
                self.job_repo.update_task_status(job_id, task.chapter_num, ChapterStatus.FAILED.value, str(e))
                print(f"❌ Lỗi ở Chương {task.chapter_num}: {e}")
    

* * *

## Kịch bản chạy thử nghiệm kiểm chứng khả năng phục hồi

Hãy xem điều gì xảy ra nếu bạn chạy mã nguồn này trong `main.py`:
    
    
    # Giả lập danh sách 10 chương truyện cần cào
    urls = [f"https://truyen.vn{i}" for i in range(1, 11)]
    job_id = JobId("job-on-piece-tuan-35")
    
    service = ResilientCrawlerService(sqlite_job_repo, sqlite_chapter_repo)
    
    # --- CHẠY LẦN 1: Giả lập bị sập do lỗi mạng ở chương 5 ---
    service.execute_job(job_id, "one-piece", urls)
    # Kết quả trong DB: Chương 1,2,3,4,6,7,8,9,10 có trạng thái 'SUCCESS'. Chương 5 có trạng thái 'FAILED'.
    
    # --- CHẠY LẦN 2: Người dùng bật lại app sau khi sửa mạng ---
    print("\n--- Khởi động lại hệ thống sau sự cố ---")
    service.execute_job(job_id, "one-piece", urls)
    # Kết quả: Hệ thống in ra: "Phát hiện 1 chương chưa hoàn thành. Bắt đầu cào..."
    # Nó chỉ cào DUY NHẤT chương 5, bỏ qua hoàn toàn 9 chương đã thành công trước đó.
    

## Tổng kết sức mạnh hệ thống khi kết hợp toàn bộ kỹ thuật DDD + SQL:

  1. Kiểm soát trạng thái cực kỳ chặt chẽ: Nhờ mô hình hóa qua Domain Object, trạng thái tiến độ luôn chính xác và an toàn.
  2. Không lo tốn tài nguyên cào lại: Dữ liệu lớn tới hàng vạn chương hoàn toàn có thể yên tâm. Bạn có thể tắt bật script bất cứ lúc nào, SQLite đóng vai trò như một bộ nhớ lưu vết bền vững.
  3. Minh bạch lỗi: Cột `error_message` thuần SQL lưu lại vết lỗi chi tiết (như lỗi IP bị block, lỗi thay đổi giao diện), giúp bạn sửa lỗi nhanh chóng.



Đến đây hệ thống đã có đầy đủ: Domain core, SQLite thuần SQL tối ưu đa luồng, Kỹ thuật Bulk Insert / Upsert, Domain Event phát tín hiệu tự động, Selector động bằng JSON, và Progress Tracking chống sập.

Bạn có cần tôi hỗ trợ cấu trúc hoặc làm rõ thêm về phần nào trong toàn bộ kiến trúc này nữa không?