Dưới đây là thiết kế tiếp cho tầng Application Service để điều phối tiến trình crawl và cách tối ưu SQLite thuần SQL khi chạy multi-threading (đa luồng) để không bị khóa database (`database is locked`).

* * *

## 4\. Tầng Application Service (`application/crawler_service.py`)

Tầng này không chứa logic nghiệp vụ của truyện, nó đóng vai trò điều phối: Gọi `Crawler` để lấy dữ liệu từ web → Đổ vào `Domain Model` để kiểm tra → Gọi `Repository` để lưu vào SQLite.
    
    
    from domain.model import Comic, ComicId, Chapter, ChapterId
    from domain.repository import ComicRepository, ChapterRepository
    import requests # Hoặc httpx, BeautifulSoup tùy bạn dùng
    
    class CrawlerApplicationService:
        def __init__(self, comic_repo: ComicRepository, chapter_repo: ChapterRepository):
            self.comic_repo = comic_repo
            self.chapter_repo = chapter_repo
    
        def crawl_new_comic(self, comic_slug: str, title: str, source_url: str) -> ComicId:
            """Khởi tạo một truyện mới trong hệ thống trước khi crawl chương"""
            comic_id = ComicId(comic_slug)
            
            # Kiểm tra nếu truyện đã tồn tại trong DB chưa
            existing_comic = self.comic_repo.get_by_id(comic_id)
            if existing_comic:
                return comic_id
    
            # Tạo Domain Entity mới và lưu
            new_comic = Comic(id=comic_id, title=title, source_url=source_url)
            self.comic_repo.save(new_comic)
            return comic_id
    
        def crawl_and_save_chapter(self, comic_id: ComicId, chapter_num: int, url: str):
            """Giả lập việc cào một chương cụ thể và lưu vào DB"""
            # Giả lập payload cào được từ BeautifulSoup/Requests
            # response = requests.get(url) ...
            fetched_title = f"Chương {chapter_num}: Tiết tử"
            fetched_content = "Nội dung chữ của truyện đã cào được ở đây..."
            
            chapter_slug = f"{comic_id.value}-chuong-{chapter_num}"
            chapter_id = ChapterId(chapter_slug)
    
            # Tạo Domain Entity để xử lý logic (nếu có)
            chapter = Chapter(
                id=chapter_id,
                comic_id=comic_id,
                number=chapter_num,
                title=fetched_title,
                content=fetched_content
            )
            
            # Thẩm định nghiệp vụ thông qua Domain trước khi lưu
            chapter.update_content(fetched_content) 
    
            # Lưu xuống DB qua Repository
            self.chapter_repo.save(chapter)
    

* * *

## 5\. Tối ưu SQL cho Đa luồng (Multi-threading Crawling)

Khi crawl truyện, bạn thường cào nhiều chương cùng lúc bằng `ThreadPoolExecutor`. SQLite mặc định sẽ bị lỗi `sqlite3.OperationalError: database is locked` nếu có nhiều luồng cùng ghi dữ liệu.

Để giải quyết triệt để bằng thuần SQL, hãy áp dụng 3 kỹ thuật sau trong file `infrastructure/database.py`:

## Kỹ thuật 1: Bật chế độ WAL (Write-Ahead Logging)

Chế độ này cho phép nhiều luồng Đọc thoải mái ngay cả khi có 1 luồng đang Ghi, tăng tốc độ ghi file lên gấp nhiều lần.

## Kỹ thuật 2: Tăng `timeout` khi kết nối

Nếu luồng A đang ghi, luồng B sẽ đợi (block) thay vì báo lỗi ngay lập tức.

## Kỹ thuật 3: Sử dụng `INSERT OR IGNORE` hoặc `UPSERT`

Tránh việc phải `SELECT` lên kiểm tra xem chương đó đã crawl chưa rồi mới `INSERT` (mất 2 truy vấn). Ta dùng thẳng lệnh SQL tối ưu để DB tự xử lý.

Cập nhật lại file `infrastructure/sqlite_repository.py` tối ưu cho đa luồng:
    
    
    import sqlite3
    from domain.model import Chapter
    from domain.repository import ChapterRepository
    
    class SQLiteChapterRepository(ChapterRepository):
        def __init__(self, db_path: str):
            self.db_path = db_path
    
        def _get_connection(self):
            """Khởi tạo kết nối an toàn cho đa luồng"""
            # timeout=30: Đợi tối đa 30 giây nếu DB đang bị khóa bởi luồng khác
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            
            # Bật chế độ WAL (Chỉ cần chạy 1 lần lúc kết nối)
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;") 
            return conn
    
        def save(self, chapter: Chapter) -> None:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Thuần SQL: Sử dụng UPSERT (Dành cho SQLite 3.24+)
            # Nếu trùng ID (đã crawl rồi) -> Chỉ cập nhật nội dung mới, không ghi đè ngày tạo
            sql = """
                INSERT INTO chapters (id, comic_id, number, title, content, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    content = excluded.content,
                    title = excluded.title
            """
            
            cursor.execute(sql, (
                chapter.id.value, 
                chapter.comic_id.value, 
                chapter.number, 
                chapter.title, 
                chapter.content, 
                chapter.created_at.isoformat()
            ))
            conn.commit()
            conn.close()
    

* * *

## 6\. Khởi chạy ứng dụng đa luồng (`main.py`)

Mã nguồn kết hợp tất cả các phần trên chạy thử nghiệm với `concurrent.futures`.
    
    
    from concurrent.futures import ThreadPoolExecutor
    from infrastructure.database import init_db
    from infrastructure.sqlite_repository import SQLiteComicRepository, SQLiteChapterRepository
    from application.crawler_service import CrawlerApplicationService
    from domain.model import ComicId
    
    DB_PATH = "comics.db"
    
    def main():
        # 1. Khởi tạo DB vật lý
        init_db(DB_PATH)
    
        # 2. Khởi tạo các thành phần theo Dependency Injection
        comic_repo = SQLiteComicRepository(DB_PATH)
        chapter_repo = SQLiteChapterRepository(DB_PATH)
        crawler_service = CrawlerApplicationService(comic_repo, chapter_repo)
    
        # 3. Tạo một truyện mới
        comic_slug = "linh-vuc"
        comic_id = crawler_service.crawl_new_comic(
            comic_slug=comic_slug,
            title="Linh Vực",
            source_url="https://truyenfull.vn"
        )
    
        # 4. Giả lập crawl 20 chương song song bằng Multi-threading
        print("Bắt đầu crawl truyện đa luồng...")
        chapters_to_crawl = list(range(1, 21)) # Chương 1 đến 20
    
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Sử dụng lambda hoặc hàm bọc để truyền tham số cố định
            executor.map(
                lambda num: crawler_service.crawl_and_save_chapter(
                    comic_id=comic_id,
                    chapter_num=num,
                    url=f"https://truyenfull.vnchuong-{num}/"
                ), 
                chapters_to_crawl
            )
    
        print("Crawl hoàn tất! Dữ liệu đã lưu an toàn vào SQLite.")
    
    if __name__ == "__main__":
        main()
    

Để tiếp tục hoàn thiện, bạn có muốn tích hợp thêm:

  * Bộ quản lý trạng thái crawl (Crawl State / Progress) để lưu lại tiến độ, giúp app nếu bị sập giữa chừng thì khi bật lại sẽ crawl tiếp tục chứ không cào lại từ đầu?
  * Cơ chế Retry bằng SQL khi gặp lỗi mạng (HTTP 503, 429)?