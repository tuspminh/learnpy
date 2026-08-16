Version:0.9 StartHTML:0000000105 EndHTML:0000029494 StartFragment:0000000141 EndFragment:0000029458 

Để hoàn thiện hệ thống và nâng cao độ an toàn về mặt dữ liệu (Type Safety) cho dự án sử dụng `sqlite3` thuần, việc bổ sung thêm tầng **Data Models** sử dụng `dataclasses` (đóng vai trò như `BaseModel`), **Enum** (quản lý trạng thái cố định) và **Mapper** (chuyển đổi qua lại giữa Row của SQLite và Object Python) là cực kỳ cần thiết.

Sự kết hợp này giúp code ở tầng Repositories và Main xử lý đối tượng Object tường minh (ví dụ: `task.status == TaskStatus.PENDING`), loại bỏ hoàn toàn việc "hardcode" chuỗi text hay truy cập key-value dạng dict dễ gõ sai.

Dưới đây là mã nguồn thiết kế chi tiết cho cấu trúc này:

* * *

**📄 models/enums.py**

Quản lý tập trung toàn bộ trạng thái cố định của hệ thống bằng Enum.

python
    
    
    from enum import Enum
    
    class TaskStatus(Enum):
        PENDING = "PENDING"
        RUNNING = "RUNNING"
        COMPLETED = "COMPLETED"
        FAILED = "FAILED"
    
    class NovelStatus(Enum):
        ONGOING = "Đang tiến hành"
        COMPLETED = "Hoàn thành"
        PAUSED = "Tạm ngưng"
        UNKNOWN = "Không rõ"
    

Hãy thận trọng khi sử dụng mã.

**📄 models/base.py**

Xây dựng lớp thực thể nền tảng bằng `dataclasses`, tích hợp sẵn phương thức kiểm tra và xuất dữ liệu sang Dictionary sạch.

python
    
    
    from dataclasses import dataclass, asdict
    from typing import Any
    
    @dataclass
    class BaseModel:
        def to_dict(self) -> dict[str, Any]:
            """Tự động chuyển đổi các thuộc tính của Object thành Dictionary."""
            data = asdict(self)
            # Chuyển đổi các thuộc tính dạng Enum thành giá trị string thô trước khi lưu DB
            for key, value in data.items():
                if isinstance(value, Enum):
                    data[key] = value.value
                elif isinstance(value, list):
                    # Hỗ trợ chuyển đổi danh sách Enum hoặc Object lồng nhau nếu có
                    data[key] = [v.value if isinstance(v, Enum) else v for v in value]
            return data
    

Hãy thận trọng khi sử dụng mã.

**📄 models/task.py**

python
    
    
    from dataclasses import dataclass
    from typing import Optional
    from .base import BaseModel
    from .enums import TaskStatus
    
    @dataclass
    class Task(BaseModel):
        target_url: str
        id: Optional[int] = None
        status: TaskStatus = TaskStatus.PENDING
        error_message: str = ""
        updated_at: Optional[str] = None
    

Hãy thận trọng khi sử dụng mã.

**📄 models/novel.py**

python
    
    
    from dataclasses import dataclass
    from typing import Optional
    from .base import BaseModel
    from .enums import NovelStatus
    
    @dataclass
    class Novel(BaseModel):
        website_id: int
        title: str
        slug: str
        id: Optional[int] = None
        author: str = "Không rõ"
        status: NovelStatus = NovelStatus.UNKNOWN
        genres: list[str] = os_field := None  # Sẽ lưu dạng chuỗi phân tách bằng dấu phẩy trong DB
        description: str = ""
        created_at: Optional[str] = None
    
        def __post_init__(self):
            # Đảm bảo genres luôn luôn là một list
            if self.genres is None:
                self.genres = []
            # Chuẩn hóa trạng thái nếu truyền vào dạng chuỗi
            if isinstance(self.status, str):
                try:
                    self.status = NovelStatus(self.status)
                except ValueError:
                    self.status = NovelStatus.UNKNOWN
    

Hãy thận trọng khi sử dụng mã.

**📄 models/chapter.py**

python
    
    
    from dataclasses import dataclass
    from typing import Optional
    from .base import BaseModel
    
    @dataclass
    class Chapter(BaseModel):
        novel_id: int
        title: str
        url: str
        id: Optional[int] = None
        order_index: int = 0
        content: str = ""
    

Hãy thận trọng khi sử dụng mã.

* * *

**📄 database/mapper.py**

Bộ chuyển đổi dữ liệu chuyên biệt (Data Mapper Pattern). Chịu trách nhiệm bóc tách các dòng dữ liệu thô `sqlite3.Row` để phục hồi (hydrate) thành các Python Object chuẩn xác.

python
    
    
    import sqlite3
    from typing import TypeVar, Type, Any
    from models.task import Task, TaskStatus
    from models.novel import Novel, NovelStatus
    from models.chapter import Chapter
    
    T = TypeVar("T")
    
    class DataMapper:
        @staticmethod
        def to_task(row: sqlite3.Row) -> Task:
            """Biến đổi một Row của bảng tasks thành Object Task."""
            return Task(
                id=row["id"],
                target_url=row["target_url"],
                status=TaskStatus(row["status"]),
                error_message=row["error_message"],
                updated_at=row["updated_at"]
            )
    
        @staticmethod
        def to_novel(row: sqlite3.Row) -> Novel:
            """Biến đổi một Row của bảng novels thành Object Novel."""
            # Chuyển chuỗi "Tiên hiệp, Kiếm hiệp" trong DB ngược thành list['Tiên hiệp', 'Kiếm hiệp']
            genres_list = [g.strip() for g in row["genres"].split(",") if g.strip()] if row["genres"] else []
            
            return Novel(
                id=row["id"],
                website_id=row["website_id"],
                title=row["title"],
                slug=row["slug"],
                author=row["author"],
                status=NovelStatus(row["status"]),
                genres=genres_list,
                description=row["description"],
                created_at=row["created_at"]
            )
    
        @staticmethod
        def to_chapter(row: sqlite3.Row) -> Chapter:
            """Biến đổi một Row của bảng chapters thành Object Chapter."""
            return Chapter(
                id=row["id"],
                novel_id=row["novel_id"],
                title=row["title"],
                url=row["url"],
                order_index=row["order_index"],
                content=row["content"]
            )
    

Hãy thận trọng khi sử dụng mã.

* * *

**🔄 Cập nhật tầng repositories/ sử dụng Object và Mapper**

Dưới đây là cách viết lại **TaskRepository** và **NovelRepository** để chúng giao tiếp hoàn toàn thông qua Object và sử dụng `DataMapper`.

**📄 repositories/task_repository.py (Cập nhật)**

python
    
    
    from typing import Optional
    from database.session import SQLiteSession
    from database.mapper import DataMapper
    from models.task import Task, TaskStatus
    from .base_repository import BaseRepository
    
    class TaskRepository(BaseRepository):
        def __init__(self):
            super().__init__("tasks")
    
        def get_next_pending_task(self, session: SQLiteSession) -> Optional[Task]:
            """Lấy tác vụ PENDING và trả về dưới dạng Object Task."""
            query = "SELECT * FROM tasks WHERE status = 'PENDING' ORDER BY id ASC LIMIT 1;"
            cursor = session.execute(query)
            row = cursor.fetchone()
            return DataMapper.to_task(row) if row else None
    
        def update_task(self, session: SQLiteSession, task: Task) -> None:
            """Cập nhật toàn bộ trạng thái của một Object Task xuống DB."""
            query = """
                UPDATE tasks 
                SET status = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?;
            """
            session.execute(query, (task.status.value, task.error_message, task.id))
    

Hãy thận trọng khi sử dụng mã.

**📄 repositories/novel_repository.py (Cập nhật)**

python
    
    
    from typing import Optional
    from database.session import SQLiteSession
    from database.mapper import DataMapper
    from models.novel import Novel
    from .base_repository import BaseRepository
    
    class NovelRepository(BaseRepository):
        def __init__(self):
            super().__init__("novels")
    
        def get_by_slug(self, session: SQLiteSession, slug: str) -> Optional[Novel]:
            """Tìm kiếm truyện theo slug và trả về Object Novel."""
            query = "SELECT * FROM novels WHERE slug = ?;"
            cursor = session.execute(query, (slug,))
            row = cursor.fetchone()
            return DataMapper.to_novel(row) if row else None
    
        def create_or_update_novel(self, session: SQLiteSession, novel: Novel) -> int:
            """Nhận vào một Object Novel, thực hiện Upsert và gán ngược ID lại cho Object."""
            genres_str = ", ".join(novel.genres)
            existing = self.get_by_slug(session, novel.slug)
            
            if existing:
                query = """
                    UPDATE novels 
                    SET title = ?, author = ?, status = ?, genres = ?, description = ?
                    WHERE id = ?;
                """
                session.execute(query, (
                    novel.title, novel.author, novel.status.value, 
                    genres_str, novel.description, existing.id
                ))
                novel.id = existing.id
                return existing.id
            else:
                query = """
                    INSERT INTO novels (website_id, title, slug, author, status, genres, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                """
                cursor = session.execute(query, (
                    novel.website_id, novel.title, novel.slug, novel.author, 
                    novel.status.value, genres_str, novel.description
                ))
                novel.id = cursor.lastrowid
                return cursor.lastrowid
    

Hãy thận trọng khi sử dụng mã.

* * *

**🚀 Trích đoạn áp dụng sạch đẹp trong main.py**

Khi triển khai thực tế trong file chạy chính, code của bạn sẽ cực kỳ tường minh nhờ cơ chế hướng đối tượng này:

python
    
    
    # Trích đoạn minh họa luồng xử lý trong vòng lặp main.py mới
    with SQLiteSession(self.engine) as session:
        # 1. Lấy Task Object từ repo
        task: Task = self.task_repo.get_next_pending_task(session)
        
        if task:
            # 2. Thay đổi trạng thái trực tiếp qua thuộc tính Object và Enum
            task.status = TaskStatus.RUNNING
            self.task_repo.update_task(session, task)
    
    # ... Thực hiện cào dữ liệu thô (raw_novel_data) từ Web ...
    
    try:
        # Khởi tạo Object Novel từ dữ liệu cào được một cách an toàn
        novel_obj = Novel(
            website_id=website_id,
            title=raw_novel_data["title"],
            slug=slug,
            author=raw_novel_data.get("author", "Không rõ"),
            genres=raw_novel_data.get("genres", []),
            description=raw_novel_data.get("description", "")
        )
    
        with SQLiteSession(self.engine) as session:
            # Ghi nhận xuống cơ sở dữ liệu bằng Object hoàn toàn
            self.novel_repo.create_or_update_novel(session, novel_obj)
            
            # Đánh dấu hoàn thành trên Object Task
            task.status = TaskStatus.COMPLETED
            self.task_repo.update_task(session, task)
            
    except Exception as e:
        with SQLiteSession(self.engine) as session:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            self.task_repo.update_task(session, task)
    

Hãy thận trọng khi sử dụng mã.

Kiến trúc framework crawler tự dựng bằng SQL thuần của bạn hiện tại đã đạt chuẩn **Enterprise-ready** (Sẵn sàng cho dự án lớn), bảo trì rất sướng vì mọi thứ được Module hóa độc lập.

Bạn có cần hỗ trợ thêm về phần viết **Unit Test** sử dụng dữ liệu giả lập (In-memory database `:memory:`) để kiểm tra tự động độ chính xác của tầng Repositories này không?

