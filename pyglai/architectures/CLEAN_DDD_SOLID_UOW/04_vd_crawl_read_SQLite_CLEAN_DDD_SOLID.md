Để thiết kế một ứng dụng crawl truyện và đọc truyện sử dụng SQLite (SQL thuần) theo kiến trúc Clean Architecture + DDD + SOLID, chúng ta cần tách biệt hoàn toàn logic nghiệp vụ (Domain) ra khỏi chi tiết công nghệ (SQLite, Thư viện HTTP crawl).

Dưới đây là bản thiết kế chi tiết từ cấu trúc thư mục đến mã nguồn triển khai bằng Python thuần.

* * *

## 📂 Cấu trúc thư mục ứng dụng (Project Structure)
    
    
    src/
    ├── domain/                  # Lớp Nghiệp vụ cốt lõi (Chỉ dùng Python thuần)
    │   ├── models.py            # Story (Aggregate Root), Chapter (Entity)
    │   ├── repositories.py      # Interface cho StoryRepository, CrawlService
    │   └── exceptions.py        # Các ngoại lệ nghiệp vụ (ví dụ: ChapterNotFoundError)
    │
    ├── application/             # Lớp Điều hướng ứng dụng (Use Cases / DTOs)
    │   ├── dto.py               # Dữ liệu đầu vào/đầu ra (Data Transfer Objects)
    │   ├── unit_of_work.py      # Interface AbstractUnitOfWork
    │   └── use_cases.py         # CrawlStoryUseCase, ReadChapterUseCase
    │
    ├── infrastructure/          # Lớp Hạ tầng (Chi tiết công nghệ: SQLite, HTTP)
    │   ├── db/
    │   │   ├── connection.py    # Quản lý kết nối SQLite
    │   │   └── schema.sql       # File định nghĩa bảng SQL thuần
    │   ├── repositories/
    │   │   └── sqlite_repo.py   # Triển khai StoryRepository bằng SQL thuần
    │   ├── crawler/
    │   │   └── web_crawler.py   # Triển khai CrawlService bằng requests/BeautifulSoup
    │   └── unit_of_work.py      # Triển khai SQLiteUnitOfWork
    │
    └── presentation/            # Lớp Giao diện (CLI hoặc API)
        └── cli.py               # Giao diện dòng lệnh để Crawl và Đọc truyện
    

* * *

## 💻 Triển khai mã nguồn chi tiết

## 1\. Tầng Domain (Nghiệp vụ cốt lõi)

Áp dụng DDD để gom nhóm thực thể và Single Responsibility (S trong SOLID).
    
    
    # src/domain/models.py
    from dataclasses import dataclass, field
    from typing import List
    
    @dataclass
    class Chapter: # Entity
        chapter_id: str
        title: str
        content: str
        order_index: int
    
    @dataclass
    class Story: # Aggregate Root
        story_id: str
        title: str
        author: str
        url: str  # Nguồn crawl
        chapters: List[Chapter] = field(default_factory=list)
    
        def add_chapter(self, title: str, content: str) -> None:
            """Logic nghiệp vụ: Tự động tính toán số thứ tự chương"""
            next_order = len(self.chapters) + 1
            chapter_id = f"{self.story_id}-ch{next_order}"
            new_chapter = Chapter(
                chapter_id=chapter_id, 
                title=title, 
                content=content, 
                order_index=next_order
            )
            self.chapters.append(new_chapter)
    
    # src/domain/repositories.py
    from abc import ABC, abstractmethod
    from typing import Optional, List
    from src.domain.models import Story
    
    class StoryRepository(ABC): # Interface - Dependency Inversion (D)
        @abstractmethod
        def save(self, story: Story) -> None: pass
    
        @abstractmethod
        def get_by_id(self, story_id: str) -> Optional[Story]: pass
    
        @abstractmethod
        def list_all(self) -> List[Story]: pass
    
    class CrawlService(ABC): # Interface phục vụ việc Crawl từ bên ngoài
        @abstractmethod
        def fetch_story_details(self, url: str) -> Story: pass
    

## 2\. Tầng Application (Điều phối & Quản lý Giao dịch)

Định nghĩa Unit of Work và các Use Case độc lập.
    
    
    # src/application/unit_of_work.py
    from abc import ABC, abstractmethod
    from src.domain.repositories import StoryRepository
    
    class AbstractUnitOfWork(ABC):
        stories: StoryRepository
    
        def __enter__(self) -> "AbstractUnitOfWork": return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None: self.rollback()
            else: self.commit()
    
        @abstractmethod
        def commit(self): pass
        @abstractmethod
        def rollback(self): pass
    
    # src/application/use_cases.py
    from src.application.unit_of_work import AbstractUnitOfWork
    from src.domain.repositories import CrawlService
    from src.domain.models import Story
    
    class CrawlStoryUseCase:
        """Use Case: Crawl truyện từ một trang web và lưu vào máy"""
        def __init__(self, uow: AbstractUnitOfWork, crawler: CrawlService):
            self.uow = uow
            self.crawler = crawler
    
        def execute(self, url: str) -> str:
            # 1. Gọi dịch vụ crawl (bên ngoài) để lấy dữ liệu về Domain Model
            scraped_story: Story = self.crawler.fetch_story_details(url)
            
            # 2. Lưu vào Database thông qua Unit of Work đảm bảo an toàn giao dịch
            with self.uow:
                self.uow.stories.save(scraped_story)
                
            return scraped_story.story_id
    
    class ReadStoryUseCase:
        """Use Case: Đọc danh sách hoặc chi tiết truyện"""
        def __init__(self, uow: AbstractUnitOfWork):
            self.uow = uow
    
        def get_library(self):
            with self.uow:
                return self.uow.stories.list_all()
    
        def get_chapter(self, story_id: str, chapter_index: int):
            with self.uow:
                story = self.uow.stories.get_by_id(story_id)
                if not story or len(story.chapters) < chapter_index:
                    return None
                return story.chapters[chapter_index - 1]
    

## 3\. Tầng Infrastructure (Hiện thực hóa công nghệ: SQLite + SQL Thuần)

Đây là nơi viết các câu lệnh `INSERT`, `SELECT` bằng SQL thuần và triển khai UoW với SQLite Transaction.
    
    
    # src/infrastructure/repositories/sqlite_repo.py
    import sqlite3
    from typing import Optional, List
    from src.domain.models import Story, Chapter
    from src.domain.repositories import StoryRepository
    
    class SQLiteStoryRepository(StoryRepository):
        def __init__(self, connection: sqlite3.Connection):
            self.conn = connection
    
        def save(self, story: Story) -> None:
            cursor = self.conn.cursor()
            # SQL thuần chèn Story
            cursor.execute(
                "INSERT OR REPLACE INTO stories (id, title, author, url) VALUES (?, ?, ?, ?)",
                (story.story_id, story.title, story.author, story.url)
            )
            # SQL thuần chèn các Chapter thuộc Story đó (Tính toàn vẹn Aggregate trong DDD)
            for ch in story.chapters:
                cursor.execute(
                    "INSERT OR REPLACE INTO chapters (id, story_id, title, content, order_index) VALUES (?, ?, ?, ?, ?)",
                    (ch.chapter_id, story.story_id, ch.title, ch.content, ch.order_index)
                )
    
        def get_by_id(self, story_id: str) -> Optional[Story]:
            cursor = self.conn.cursor()
            cursor.execute("SELECT title, author, url FROM stories WHERE id = ?", (story_id,))
            story_row = cursor.fetchone()
            if not story_row: return None
    
            story = Story(story_id=story_id, title=story_row[0], author=story_row[1], url=story_row[2])
            
            # Tải kèm các Chapter lên (Eager Loading dữ liệu của Aggregate)
            cursor.execute("SELECT id, title, content, order_index FROM chapters WHERE story_id = ? ORDER BY order_index", (story_id,))
            for row in cursor.fetchall():
                story.chapters.append(Chapter(chapter_id=row[0], title=row[1], content=row[2], order_index=row[3]))
            return story
    
        def list_all(self) -> List[Story]:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, title, author, url FROM stories")
            return [Story(story_id=row[0], title=row[1], author=row[2], url=row[3]) for row in cursor.fetchall()]
    
    
    
    # src/infrastructure/unit_of_work.py
    import sqlite3
    from src.application.unit_of_work import AbstractUnitOfWork
    from src.infrastructure.repositories.sqlite_repo import SQLiteStoryRepository
    
    class SQLiteUnitOfWork(AbstractUnitOfWork):
        def __init__(self, db_path: str):
            self.db_path = db_path
    
        def __enter__(self):
            self.conn = sqlite3.connect(self.db_path)
            # Bật chế độ cô lập để quản lý Giao dịch thủ công (BEGIN TRANSACTION)
            self.conn.isolation_level = None 
            self.conn.execute("BEGIN")
            self.stories = SQLiteStoryRepository(self.conn)
            return super().__enter__()
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            super().__exit__(exc_type, exc_val, exc_tb)
            self.conn.close()
    
        def commit(self):
            self.conn.execute("COMMIT")
    
        def rollback(self):
            self.conn.execute("ROLLBACK")
    
    
    
    # src/infrastructure/crawler/web_crawler.py
    import uuid
    from src.domain.repositories import CrawlService
    from src.domain.models import Story
    
    class FakeWebCrawler(CrawlService):
        """Giả lập Crawler. Thực tế bạn sẽ dùng requests + BeautifulSoup ở đây"""
        def fetch_story_details(self, url: str) -> Story:
            story_id = str(uuid.uuid4())[:8]
            story = Story(story_id=story_id, title="Đắc Nhân Tâm", author="Dale Carnegie", url=url)
            # Giả lập cào được 2 chương
            story.add_chapter("Chương 1", "Nghệ thuật ứng xử căn bản...")
            story.add_chapter("Chương 2", "Sáu cách tạo thiện cảm...")
            return story
    

## 4\. Tầng Presentation (Khởi chạy ứng dụng)

Khởi tạo dữ liệu mẫu và chạy ứng dụng qua CLI.
    
    
    # src/infrastructure/db/schema.sql (Mô tả bảng SQL thuần)
    """
    CREATE TABLE IF NOT EXISTS stories (
        id TEXT PRIMARY KEY, title TEXT, author TEXT, url TEXT
    );
    CREATE TABLE IF NOT EXISTS chapters (
        id TEXT PRIMARY KEY, story_id TEXT, title TEXT, content TEXT, order_index INTEGER,
        FOREIGN KEY(story_id) REFERENCES stories(id)
    );
    """
    
    # src/presentation/cli.py
    import sqlite3
    from src.infrastructure.unit_of_work import SQLiteUnitOfWork
    from src.infrastructure.crawler.web_crawler import FakeWebCrawler
    from src.application.use_cases import CrawlStoryUseCase, ReadStoryUseCase
    
    def init_db(db_path: str):
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS stories (id TEXT PRIMARY KEY, title TEXT, author TEXT, url TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS chapters (id TEXT PRIMARY KEY, story_id TEXT, title TEXT, content TEXT, order_index INTEGER)")
        conn.close()
    
    if __name__ == "__main__":
        DB_PATH = "reading_app.db"
        init_db(DB_PATH)
    
        # 1. Khởi tạo các thành phần Hạ tầng (Infrastructure)
        uow = SQLiteUnitOfWork(DB_PATH)
        crawler = FakeWebCrawler()
    
        # 2. Tiêm vào Tầng Ứng dụng (Application Use Cases)
        crawl_use_case = CrawlStoryUseCase(uow, crawler)
        read_use_case = ReadStoryUseCase(uow)
    
        # 3. Chạy luồng ứng dụng
        print("--- 1. Tiến hành Crawl Truyện ---")
        story_id = crawl_use_case.execute("https://example-story.com")
        print(f"Đã crawl và lưu truyện thành công! ID: {story_id}\n")
    
        print("--- 2. Đọc truyện từ Database ---")
        chapters = read_use_case.get_chapter(story_id, chapter_index=1)
        if chapters:
            print(f"Đang đọc: {chapters.title}")
            print(f"Nội dung: {chapters.content}")
    

* * *

## 💡 Các nguyên lý được thỏa mãn như thế nào?

  1. Liskov Substitution & Dependency Inversion (L & D trong SOLID): Lớp `CrawlStoryUseCase` không quan tâm bạn dùng thư viện gì để crawl (`BeautifulSoup`, `Selenium`, hay `Scrapy`). Nó chỉ yêu cầu một đối tượng tuân thủ bản thiết kế `CrawlService`. Bạn có thể thay đổi lớp Crawler ở tầng Hạ tầng bất cứ lúc nào mà không cần sửa code của Use Case.
  2. Tính toàn vẹn Transaction (Unit of Work): Khi lưu một cuốn truyện, nếu quá trình lưu các chương (`chapters`) bị lỗi (ví dụ: mất kết nối SQLite giữa chừng), `SQLiteUnitOfWork` sẽ tự động kích hoạt câu lệnh `ROLLBACK`. Cuốn truyện đó sẽ không bị lưu dở dang vào DB.
  3. Mô hình DDD (Aggregate Root): `Story` là Aggregate Root quản lý các `Chapter`. Bạn không tạo ra Use Case hay Repository riêng để lưu lẻ tẻ từng Chapter. Mọi tương tác lưu trữ đều phải đi qua `StoryRepository`.



Để hoàn thiện ứng dụng này, hãy cho tôi biết:

  * Bạn có muốn chuyển phần `FakeWebCrawler` thành code cào dữ liệu thực tế bằng thư viện `BeautifulSoup` và `requests` không?
  * Bạn có cần thiết kế thêm tính năng quản lý tiến trình đọc (Bookmark) (Lưu lại chương cuối cùng người dùng đang đọc) theo mô hình này không?