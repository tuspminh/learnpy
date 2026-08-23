Để thiết kế cấu trúc công đoạn lưu DB và DB Connection Manager cho ứng dụng crawl truyện bằng Python, chúng ta sẽ áp dụng các nguyên tắc Clean Architecture và SOLID, kết hợp với các đặc tính thế mạnh của Python như `Context Manager` (để quản lý connection tự động), `abc` (Abstract Base Classes để làm Interface) và `Dataclasses` (để làm Domain Entities).

Dưới đây là kiến trúc và code triển khai chi tiết từng phần bằng Python.

* * *

## 1\. Kiến trúc thư mục (Directory Structure)
    
    
    src/
    │
    ├── domain/                      # 1. Lớp lõi (Domain Layer)
    │   ├── entities.py              # Các thực thể nghiệp vụ: Story, Chapter
    │   └── repositories.py          # Interfaces định nghĩa các hàm lưu trữ dữ liệu
    │
    ├── use_cases/                   # 2. Lớp nghiệp vụ (Use Case Layer)
    │   └── save_story_use_case.py   # Logic điều phối công đoạn xử lý và lưu truyện
    │
    └── infrastructure/              # 3. Lớp ngoại vi (Infrastructure Layer)
        ├── database/
        │   ├── connection_manager.py# DB Connection Manager (Quản lý kết nối)
        │   └── mysql_repositories.py# Cài đặt chi tiết câu lệnh SQL (MySQL/PostgreSQL)
        └── crawler/                 # Công cụ cào (BeautifulSoup, Scrapy...)
    

* * *

## 2\. Thiết kế DB Connection Manager (Pythonic & SOLID)

Trong Python, cách tốt nhất để quản lý kết nối (mở/đóng pool, giải phóng tài nguyên) là sử dụng Context Manager (`__enter__` và `__exit__`).

## Bước 2.1: Định nghĩa Interface cho DB Client (D - Dependency Inversion)
    
    
    # src/domain/repositories.py (Hoặc file interface riêng trong infrastructure)
    from abc import ABC, abstractmethod
    
    class IDbClient(ABC):
        @abstractmethod
        def connect(self) -> None:
            """Khởi tạo connection pool hoặc kết nối vật lý"""
            pass
    
        @abstractmethod
        def disconnect(self) -> None:
            """Đóng tất cả kết nối để tránh rò rỉ tài nguyên"""
            pass
    
        @abstractmethod
        def get_connection(self):
            """Lấy ra 1 connection instance từ Pool"""
            pass
    

## Bước 2.2: Triển khai Connection Manager sử dụng Connection Pool (MySQL mẫu)

Sử dụng thư viện `mysql-connector-python` hoặc `pymysql` kết hợp Threaded Connection Pool để tối ưu hiệu năng cho Crawler chạy đa luồng.
    
    
    # src/infrastructure/database/connection_manager.py
    import os
    from mysql.connector import pooling
    from src.domain.repositories import IDbClient
    
    class MySqlDbClient(IDbClient):
        def __init__(self):
            self._pool = None
    
        def connect(self) -> None:
            if not self._pool:
                # Khởi tạo Connection Pool tối ưu cho crawler
                self._pool = pooling.MySQLConnectionPool(
                    pool_name="crawler_pool",
                    pool_size=10,  # Số lượng connection đồng thời tối đa
                    host=os.getenv("DB_HOST", "localhost"),
                    user=os.getenv("DB_USER", "root"),
                    password=os.getenv("DB_PASSWORD", "password"),
                    database=os.getenv("DB_NAME", "comic_crawler")
                )
                print("🔌 MySQL Connection Pool đã được khởi tạo thành công.")
    
        def disconnect(self) -> None:
            # Trong thực tế, Pool của mysql-connector tự quản lý việc đóng các connection con
            self._pool = None
            print("🔌 MySQL Connection Pool đã được giải phóng.")
    
        def get_connection(self):
            if not self._pool:
                raise RuntimeError("Database chưa được kết nối! Hãy gọi .connect() trước.")
            return self._pool.get_connection()
    
    
    class DbContextManager:
        """Python Context Manager giúp tự động mượn và trả Connection về Pool"""
        def __init__(self, db_client: IDbClient):
            self.db_client = db_client
            self.connection = None
            self.cursor = None
    
        def __enter__(self):
            self.connection = self.db_client.get_connection()
            self.cursor = self.connection.cursor(dictionary=True) # Trả về dạng dict cho dễ map
            return self.connection, self.cursor
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.cursor:
                self.cursor.close()
            if self.connection:
                if exc_type is not None:
                    # Nếu xảy ra lỗi trong block 'with', tiến hành Rollback
                    self.connection.rollback()
                    print(f"❌ Xảy ra lỗi: {exc_val}. Đã Rollback dữ liệu.")
                else:
                    # Nếu thành công hoàn toàn, Commit dữ liệu
                    self.connection.commit()
                self.connection.close() # Trả connection lại cho Pool, không đóng hẳn vật lý
    

* * *

## 3\. Cấu trúc Công đoạn Lưu DB (Data Persistence Pipeline)

## Bước 3.1: Khai báo Entities và Repository Interfaces tại lớp Domain
    
    
    # src/domain/entities.py
    from dataclasses import dataclass, field
    from typing import Optional
    import uuid
    
    @dataclass
    class Story:
        title: str
        author: str
        slug: str
        id: str = field(default_factory=lambda: str(uuid.uuid4()))
        description: Optional[str] = None
    
    # src/domain/repositories.py (Tiếp tục file trên)
    from typing import Optional
    from src.domain.entities import Story
    
    class IStoryRepository(ABC):
        @abstractmethod
        def find_by_source_url(self, url: str) -> Optional[Story]:
            pass
    
        @abstractmethod
        def create(self, story: Story) -> Story:
            pass
    
        @abstractmethod
        def update(self, story: Story) -> None:
            pass
    

## Bước 3.2: Triển khai Repository chi tiết ở lớp Infrastructure

Tách biệt triệt để câu lệnh SQL (S - Single Responsibility). Sử dụng `DbContextManager` đã viết ở trên để thực thi.
    
    
    # src/infrastructure/database/mysql_repositories.py
    from typing import Optional
    from src.domain.entities import Story
    from src.domain.repositories import IStoryRepository, IDbClient
    from src.infrastructure.database.connection_manager import DbContextManager
    
    class MySqlStoryRepository(IStoryRepository):
        def __init__(self, db_client: IDbClient):
            self.db_client = db_client
    
        def find_by_source_url(self, url: str) -> Optional[Story]:
            query = """
                SELECT s.* FROM stories s 
                JOIN story_source_mappings m ON s.id = m.story_id 
                WHERE m.remote_url = %s LIMIT 1
            """
            # Sử dụng Context Manager để tự động quản lý đóng/mở/commit
            with DbContextManager(self.db_client) as (conn, cursor):
                cursor.execute(query, (url,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                # Map dữ liệu từ DB raw ngược về Domain Entity
                return Story(
                    id=row['id'],
                    title=row['title'],
                    author=row['author'],
                    slug=row['slug'],
                    description=row.get('description')
                )
    
        def create(self, story: Story) -> Story:
            query = "INSERT INTO stories (id, title, author, slug, description) VALUES (%s, %s, %s, %s, %s)"
            with DbContextManager(self.db_client) as (conn, cursor):
                cursor.execute(query, (story.id, story.title, story.author, story.slug, story.description))
            return story
    
        def update(self, story: Story) -> None:
            query = "UPDATE stories SET title = %s, author = %s, description = %s WHERE id = %s"
            with DbContextManager(self.db_client) as (conn, cursor):
                cursor.execute(query, (story.title, story.author, story.description, story.id))
    

## Bước 3.3: Lớp Use Case điều phối công đoạn lưu (Pipeline)

Lớp này nhận dữ liệu thô từ Crawler, làm sạch (Clean), kiểm tra trùng và lưu qua Interface.
    
    
    # src/use_cases/save_story_use_case.py
    from src.domain.entities import Story
    from src.domain.repositories import IStoryRepository
    
    class SaveCrawledStoryUseCase:
        # Dependency Injection qua __init__: chỉ nhận Interface, không phụ thuộc vào MySQL cụ thể
        def __init__(self, story_repo: IStoryRepository):
            self.story_repo = story_repo
    
        def execute(self, raw_data: dict) -> None:
            # Công đoạn 1: Clean & Validate dữ liệu thô từ Crawler
            clean_title = raw_data.get("title", "").strip()
            clean_author = raw_data.get("author", "Ẩn Danh").strip()
            clean_slug = clean_title.lower().replace(" ", "-") # Dummy tạo slug đơn giản
            source_url = raw_data.get("source_url")
    
            if not clean_title or not source_url:
                raise ValueError("Dữ liệu cào bị thiếu thông tin bắt buộc.")
    
            # Công đoạn 2: Kiểm tra trùng lặp thông qua Repository định danh nguồn
            existing_story = self.story_repo.find_by_source_url(source_url)
    
            if existing_story:
                # Công đoạn 3a: Nếu truyện đã tồn tại -> Cập nhật thông tin mới
                existing_story.title = clean_title
                existing_story.author = clean_author
                self.story_repo.update(existing_story)
                print(f"🔄 Đã cập nhật truyện có sẵn: {clean_title}")
            else:
                # Công đoạn 3b: Nếu là truyện mới -> Tạo mới entity và lưu DB
                new_story = Story(
                    title=clean_title,
                    author=clean_author,
                    slug=clean_slug,
                    description=raw_data.get("description")
                )
                self.story_repo.create(new_story)
                print(f"📥 Đã lưu mới truyện thành công: {clean_title}")
    

* * *

## 4\. Cách ráp nối và vận hành ứng dụng (Composition Root)

Tại file chạy chính của ứng dụng (`main.py`), ta khởi tạo các dependency và "tiêm" (inject) chúng vào nhau.
    
    
    # main.py
    import os
    from src.infrastructure.database.connection_manager import MySqlDbClient
    from src.infrastructure.database.mysql_repositories import MySqlStoryRepository
    from src.use_cases.save_story_use_case import SaveCrawledStoryUseCase
    
    def main():
        # 1. Khởi tạo DB Client và kết nối (Chỉ chạy 1 lần khi app start)
        db_client = MySqlDbClient()
        db_client.connect()
    
        try:
            # 2. Khởi tạo các Repository và truyền DB Client vào (Dependency Injection)
            story_repository = MySqlStoryRepository(db_client=db_client)
    
            # 3. Khởi tạo Use Case và truyền Repository vào
            save_story_use_case = SaveCrawledStoryUseCase(story_repo=story_repository)
    
            # Giả lập dữ liệu nhận được sau khi crawler bóc tách HTML thành công
            crawled_data = {
                "title": "  Đấu Phá Thương Khung  ",
                "author": "Thiên Tằm Thổ Đậu",
                "source_url": "https://truyenfull.vn",
                "description": "Một thế giới thuộc về Đấu Khí..."
            }
    
            # 4. Chạy công đoạn lưu dữ liệu vào DB
            save_story_use_case.execute(crawled_data)
    
        finally:
            # 5. Đóng toàn bộ Pool khi tắt ứng dụng
            db_client.disconnect()
    
    if __name__ == "__main__":
        main()
    

## 💡 Lợi ích mang lại từ kiến trúc Pythonic này:

  * Tính dễ kiểm thử (Testability): Bạn hoàn toàn có thể viết Unit Test cho `SaveCrawledStoryUseCase` bằng cách truyền vào một `MockStoryRepository` (chỉ lưu vào một mảng `[]` trong RAM) mà không cần phải bật server MySQL thật lên để test.
  * An toàn dữ liệu (Concurrency Safe): Sử dụng `DbContextManager` kết hợp Connection Pool giúp app crawler khi chạy đa luồng (`threading` hoặc `multiprocessing` trong Python) không bị xung đột kết nối hoặc tràn số lượng kết nối tối đa tới DB.



Để phát triển sâu hơn cho phần Core Engine, bạn có muốn tìm hiểu thêm về cách thiết kế cấu trúc lưu đồng thời cả Chương truyện (Chapter) lớn bằng Transaction an toàn, hoặc cách tích hợp SQLAlchemy ORM vào mô hình Clean Architecture này không?