Để chuyển đổi hệ thống sang chạy đồng bộ (Synchronous) và hỗ trợ đồng thời cả SQLite3 (sử dụng SQL thuần) và MongoDB theo đúng chuẩn DDD và SOLID, chúng ta sẽ định nghĩa lại lớp Repository. Toàn bộ logic nghiệp vụ (Domain) sẽ không bị ảnh hưởng, bạn chỉ cần thay đổi cấu hình loại Database muốn dùng tại file chạy chính.

Dưới đây là mã nguồn chi tiết:

* * *

## 🧱 Kiến Trúc Thư Mục Cập Nhật
    
    
    src/
    │
    ├── domain/
    │   ├── models.py            # Định nghĩa PageSource, Novel, Chapter
    │   └── services.py          # Đồng bộ hóa (Sync) Interface và Crawler Service
    │
    ├── infrastructure/
    │   ├── http_client.py       # Fetcher Client đồng bộ (Requests)
    │   ├── parsers.py           # Bộ parse HTML (BeautifulSoup)
    │   └── repositories/        # Thư mục chứa các triển khai Database độc lập
    │       ├── __init__.py
    │       ├── sqlite_repo.py   # Repository cho SQLite3 (SQL thuần)
    │       └── mongo_repo.py    # Repository cho MongoDB (Đồng bộ)
    │
    └── main.py                  # Lắp ghép hệ thống (Dependency Injection)
    

* * *

## 💻 Triển Khai Mã Nguồn Chi Tiết

## 1\. Lớp Domain (Đồng Bộ Hóa)

Định nghĩa Interface cho Client và Repository chạy theo dạng đồng bộ thông thường.
    
    
    # src/domain/services.py
    from abc import ABC, abstractmethod
    from src.domain.models import PageSource, Novel
    
    class HttpClientInterface(ABC):
        """Interface cho Fetcher Client đồng bộ (SOLID - I)"""
        @abstractmethod
        def fetch(self, url: str) -> PageSource:
            pass
    
    class NovelParserInterface(ABC):
        """Interface cho Bộ Parser HTML"""
        @abstractmethod
        def parse_novel(self, source: PageSource) -> Novel:
            pass
    
    class NovelRepositoryInterface(ABC):
        """Interface cho Repository - Quy định các hàm lưu trữ mà Domain cần (DDD)"""
        @abstractmethod
        def save(self, novel: Novel) -> None:
            pass
        
        @abstractmethod
        def get_by_url(self, url: str) -> Novel | None:
            pass
    
    class NovelCrawlerService:
        """Fetcher Crawler Service điều phối luồng xử lý đồng bộ (DDD - Domain Service)"""
        def __init__(
            self, 
            http_client: HttpClientInterface, 
            parser: NovelParserInterface,
            repository: NovelRepositoryInterface
        ):
            self._http_client = http_client
            self._parser = parser
            self._repository = repository
    
        def crawl_and_save(self, url: str) -> Novel:
            # Tránh cào trùng nếu truyện đã tồn tại trong DB
            existing_novel = self._repository.get_by_url(url)
            if existing_novel:
                return existing_novel
    
            # 1. Fetch dữ liệu thô đồng bộ
            page_source = self._http_client.fetch(url)
            
            # 2. Parse dữ liệu sang Domain Model
            novel = self._parser.parse_novel(page_source)
            
            # 3. Lưu vào DB thông qua Repository được cấu hình bên ngoài
            self._repository.save(novel)
            return novel
    

* * *

## 2\. Lớp Hạ Tầng - Triển Khai Các Repository (Infrastructure)

## 🔹 Triển khai SQLite3 (Dùng SQL Thuần)

Sử dụng thư viện mặc định `sqlite3` của Python và viết câu lệnh SQL tường minh, tạo 2 bảng quan hệ: `novels` (Truyện) và `chapters` (Chương).
    
    
    # src/infrastructure/repositories/sqlite_repo.py
    import sqlite3
    from src.domain.services import NovelRepositoryInterface
    from src.domain.models import Novel, Chapter
    
    class SqliteNovelRepository(NovelRepositoryInterface):
        """Triển khai Repository bằng SQLite3 sử dụng SQL thuần (SOLID - O/L)"""
        def __init__(self, db_path: str):
            self.db_path = db_path
            self._create_tables()
    
        def _get_connection(self):
            return sqlite3.connect(self.db_path)
    
        def _create_tables(self):
            """Khởi tạo cấu trúc bảng nếu chưa tồn tại"""
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS novels (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT UNIQUE,
                        author TEXT
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chapters (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        novel_id INTEGER,
                        title TEXT,
                        content TEXT,
                        url TEXT UNIQUE,
                        FOREIGN KEY (novel_id) REFERENCES novels(id)
                    )
                """)
                conn.commit()
    
        def save(self, novel: Novel) -> None:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # 1. Chèn hoặc bỏ qua nếu truyện đã tồn tại
                cursor.execute(
                    "INSERT OR IGNORE INTO novels (title, author) VALUES (?, ?)",
                    (novel.title, novel.author)
                )
                
                # Lấy id của novel vừa chèn hoặc đã có sẵn
                cursor.execute("SELECT id FROM novels WHERE title = ?", (novel.title,))
                novel_id = cursor.fetchone()[0]
    
                # 2. Chèn danh sách các chương thuộc truyện
                for ch in novel.chapters:
                    cursor.execute(
                        "INSERT OR IGNORE INTO chapters (novel_id, title, content, url) VALUES (?, ?, ?, ?)",
                        (novel_id, ch.title, ch.content, ch.url)
                    )
                conn.commit()
    
        def get_by_url(self, url: str) -> Novel | None:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Tìm xem URL chương này đã được cào chưa
                cursor.execute("""
                    SELECT n.title, n.author FROM novels n
                    JOIN chapters c ON n.id = c.novel_id
                    WHERE c.url = ?
                """, (url,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                    
                # Lấy toàn bộ chương thuộc truyện này để map ngược về Domain Model
                cursor.execute("""
                    SELECT c.title, c.content, c.url FROM chapters c
                    JOIN novels n ON n.id = c.novel_id
                    WHERE n.title = ?
                """, (row[0],))
                chapter_rows = cursor.fetchall()
                
                chapters = [Chapter(title=r[0], content=r[1], url=r[2]) for r in chapter_rows]
                return Novel(title=row[0], author=row[1], chapters=chapters)
    

## 🔹 Triển khai MongoDB (Đồng Bộ)

Sử dụng thư viện `pymongo` thông thường để lưu dữ liệu dạng Document lồng nhau (Embedded Document).
    
    
    # src/infrastructure/repositories/mongo_repo.py
    from pymongo import MongoClient
    from src.domain.services import NovelRepositoryInterface
    from src.domain.models import Novel, Chapter
    
    class MongoNovelRepository(NovelRepositoryInterface):
        """Triển khai Repository bằng MongoDB đồng bộ (SOLID - O/L)"""
        def __init__(self, connection_string: str, db_name: str):
            self._client = MongoClient(connection_string)
            self._db = self._client[db_name]
            self._collection = self._db["novels"]
    
        def save(self, novel: Novel) -> None:
            novel_data = {
                "title": novel.title,
                "author": novel.author,
                "chapters": [
                    {"title": ch.title, "content": ch.content, "url": ch.url} 
                    for ch in novel.chapters
                ]
            }
            # Thực hiện Upsert (Cập nhật nếu trùng tiêu đề, chưa có thì thêm mới)
            self._collection.update_one(
                {"title": novel.title}, 
                {"$set": novel_data}, 
                upsert=True
            )
    
        def get_by_url(self, url: str) -> Novel | None:
            doc = self._collection.find_one({"chapters.url": url})
            if not doc:
                return None
                
            chapters = [
                Chapter(title=ch["title"], content=ch["content"], url=ch["url"]) 
                for ch in doc.get("chapters", [])
            ]
            return Novel(title=doc["title"], author=doc["author"], chapters=chapters)
    

* * *

## 3\. Khởi Chạy Ứng Dụng (Lựa Chọn Cơ Sở Dữ Liệu Linh Hoạt)

Tại file khởi chạy, bạn có thể dễ dàng chuyển đổi qua lại giữa `SqliteNovelRepository` và `MongoNovelRepository` bằng cách thay đổi biến cấu hình mà không cần sửa bất kỳ dòng code logic nào khác.
    
    
    # src/main.py
    from src.infrastructure.http_client import RequestsHttpClient
    from src.infrastructure.parsers import TruyenFullParser
    
    # Import cả 2 loại Repository tùy chọn
    from src.infrastructure.repositories.sqlite_repo import SqliteNovelRepository
    from src.infrastructure.repositories.mongo_repo import MongoNovelRepository
    
    from src.domain.services import NovelCrawlerService
    
    # Cấu hình hệ thống linh hoạt
    DB_TYPE = "sqlite"  # Hoặc chuyển thành "mongo"
    
    def main():
        # 1. Khởi tạo Fetcher Client và Bộ Parser
        http_client = RequestsHttpClient(timeout=10)
        parser = TruyenFullParser()
        
        # 2. Khởi tạo Repository dựa theo cấu hình (Dependency Injection)
        if DB_TYPE == "sqlite":
            print("💾 Đang sử dụng cơ sở dữ liệu: SQLite3 (SQL Thuần)")
            repository = SqliteNovelRepository(db_path="novel_database.db")
        elif DB_TYPE == "mongo":
            print("🍃 Đang sử dụng cơ sở dữ liệu: MongoDB")
            repository = MongoNovelRepository(
                connection_string="mongodb://localhost:27017", 
                db_name="crawler_sync_db"
            )
        else:
            raise ValueError("Loại DB không được hỗ trợ!")
        
        # 3. Inject các thành phần hạ tầng vào lõi Domain Service
        crawler = NovelCrawlerService(
            http_client=http_client, 
            parser=parser, 
            repository=repository
        )
        
        # 4. Thực thi cào dữ liệu tuần tự (Đồng bộ)
        target_url = "https://example-truyen.com"
        try:
            novel = crawler.crawl_and_save(target_url)
            print(f"🎉 Xử lý thành công truyện: '{novel.title}'")
        except Exception as e:
            print(f"❌ Lỗi hệ thống: {e}")
    
    if __name__ == "__main__":
        main()
    

* * *

## 🔍 Điểm Sáng Về SOLID & DDD Sau Khi Nâng Cấp

  * Liskov Substitution (L): Cả `SqliteNovelRepository` và `MongoNovelRepository` đều kế thừa chính xác từ `NovelRepositoryInterface`. Bạn có thể hoán đổi vị trí của chúng cho nhau trong hàm `main.py` mà không làm đảo lộn hành vi ứng dụng hay gây lỗi biên dịch/runtime cho lớp gọi nó (`NovelCrawlerService`).
  * Độc Lập Công Nghệ (DDD Clean Architecture): Lớp Domain core hoàn toàn "sạch". Nó không hề biết sự tồn tại của các câu lệnh `SELECT/INSERT` SQL, cũng như không biết cấu trúc BSON của Mongo. Nó chỉ giao tiếp qua bản hợp đồng (Interface).



Nếu bạn muốn hoàn thiện thêm dự án này, vui lòng cho biết:

  * Bạn có cần xử lý Transaction (Atomicity) cho SQLite để đảm bảo khi cào lỗi giữa chừng thì không bị lưu dữ liệu rác không?
  * Bạn có muốn thêm cấu trúc Log hay quản lý Cấu hình (Environment Variables) cho các kết nối DB không?