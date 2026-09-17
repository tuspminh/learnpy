Dưới đây là kiến trúc NovelRepository sử dụng thư viện `sqlite3` thuần SQL trong Python, được thiết kế theo đúng nguyên lý DDD (Domain-Driven Design).

Trong DDD, Repository chịu trách nhiệm lưu trữ và tái tạo (rehydrate) các Domain Entities (`Novel`, `Chapter`) với cơ sở dữ liệu mà không làm lộ các kết nối cơ sở dữ liệu ra tầng nghiệp vụ.

* * *

## 1\. Tầng Domain: Định nghĩa Interface (`domain/repositories.py`)

Tầng nghiệp vụ định nghĩa các quy ước (Contracts) mà cơ sở dữ liệu bắt buộc phải tuân theo.
    
    
    from abc import ABC, abstractmethod
    from domain.entities import Novel, Chapter
    from typing import Optional, List
    
    class INovelRepository(ABC):
        """Interface quy định các thao tác lưu trữ truyện theo chuẩn DDD"""
        
        @abstractmethod
        def save_novel_meta(self, novel: Novel) -> None:
            """Lưu hoặc cập nhật thông tin tổng quan của truyện (Meta data)"""
            pass
    
        @abstractmethod
        def save_chapter(self, novel_url: str, chapter: Chapter) -> None:
            """Lưu hoặc cập nhật nội dung của một chương cụ thể"""
            pass
    
        @abstractmethod
        def find_by_url(self, source_url: str) -> Optional[Novel]:
            """Tìm kiếm và tái tạo lại một Object Novel hoàn chỉnh từ DB"""
            pass
    
        @abstractmethod
        def is_chapter_exists(self, novel_url: str, chapter_number: float) -> bool:
            """Kiểm tra chương này đã được cào và lưu trữ chưa (Tránh cào trùng)"""
            pass
    

* * *

## 2\. Tầng Infrastructure: Triển khai với SQLite Thuần (`infrastructure/repositories/sqlite_repository.py`)

Lớp này thực thi interface trên bằng cách viết các câu lệnh SQL thuần túy (`INSERT`, `SELECT`, `UPDATE`).
    
    
    import sqlite3
    from typing import Optional, List
    from domain.entities import Novel, Chapter
    from domain.repositories import INovelRepository
    
    class SQLiteNovelRepository(INovelRepository):
        """Triển khai kết nối cơ sở dữ liệu SQLite bằng SQL thuần"""
    
        def __init__(self, db_path: str = "novel_crawler.db"):
            self.db_path = db_path
            self._create_tables()
    
        def _get_connection(self) -> sqlite3.Connection:
            """Khởi tạo kết nối. Thiết lập row_factory để lấy dữ liệu dạng Dictionary"""
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
    
        def _create_tables(self) -> None:
            """Khởi tạo cấu trúc bảng SQL thuần (Dữ liệu quan hệ)"""
            create_novels_table = """
            CREATE TABLE IF NOT EXISTS novels (
                source_url TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT,
                description TEXT
            );
            """
            create_chapters_table = """
            CREATE TABLE IF NOT EXISTS chapters (
                id TEXT PRIMARY KEY, -- Ghép từ source_url và chapter_number
                novel_url TEXT,
                chapter_number REAL NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                FOREIGN KEY (novel_url) REFERENCES novels (source_url) ON DELETE CASCADE
            );
            """
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(create_novels_table)
                cursor.execute(create_chapters_table)
                # Tạo Index để tối ưu tốc độ tìm kiếm chương
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_chapters_novel ON chapters(novel_url);")
                conn.commit()
    
        def save_novel_meta(self, novel: Novel) -> None:
            query = """
            INSERT INTO novels (source_url, title, author, description)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(source_url) DO UPDATE SET
                title = excluded.title,
                author = excluded.author,
                description = excluded.description;
            """
            with self._get_connection() as conn:
                conn.execute(query, (novel.source_url, novel.title, novel.author, novel.description))
                conn.commit()
    
        def save_chapter(self, novel_url: str, chapter: Chapter) -> None:
            # Sử dụng id tổng hợp (Composite Key) để tránh trùng lặp bản ghi
            chapter_id = f"{novel_url}_{chapter.number}"
            query = """
            INSERT INTO chapters (id, novel_url, chapter_number, title, content)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                content = excluded.content;
            """
            with self._get_connection() as conn:
                conn.execute(query, (chapter_id, novel_url, chapter.number, chapter.title, chapter.content))
                conn.commit()
    
        def is_chapter_exists(self, novel_url: str, chapter_number: float) -> bool:
            chapter_id = f"{novel_url}_{chapter_number}"
            query = "SELECT 1 FROM chapters WHERE id = ? LIMIT 1;"
            with self._get_connection() as conn:
                cursor = conn.execute(query, (chapter_id,))
                return cursor.fetchone() is not None
    
        def find_by_url(self, source_url: str) -> Optional[Novel]:
            """Tái cấu trúc (Rehydrate) từ dòng dữ liệu SQL thuần thành Domain Object"""
            novel_query = "SELECT * FROM novels WHERE source_url = ?;"
            chapters_query = "SELECT * FROM chapters WHERE novel_url = ? ORDER BY chapter_number ASC;"
    
            with self._get_connection() as conn:
                # 1. Lấy thông tin truyện
                novel_row = conn.execute(novel_query, (source_url,)).fetchone()
                if not novel_row:
                    return None
    
                # Khởi tạo lại Entity Novel từ dữ liệu thô trong DB
                novel = Novel(
                    title=novel_row['title'],
                    author=novel_row['author'],
                    description=novel_row['description'],
                    source_url=novel_row['source_url']
                )
    
                # 2. Lấy danh sách chương thuộc về truyện đó
                chapter_rows = conn.execute(chapters_query, (source_url,)).fetchall()
                for row in chapter_rows:
                    chapter = Chapter(
                        number=row['chapter_number'],
                        title=row['title'],
                        content=row['content']
                    )
                    novel.add_chapter(chapter)
    
                return novel
    

* * *

## 3\. Cách tích hợp vào luồng điều phối của Crawler

Khi chạy ứng dụng, bạn chỉ cần nạp (inject) Repository này vào `MultiThreadedNovelCrawler` đã dựng ở bước trước:
    
    
    if __name__ == "__main__":
        from infrastructure.fetchers.http_fetcher import CloudflareBypassFetcher
        from application.services.novel_crawler import MultiThreadedNovelCrawler
        
        # 1. Khởi tạo hạ tầng (Infrastructure Layers)
        repo = SQLiteNovelRepository(db_path="my_novels.db")
        fetcher = CloudflareBypassFetcher()
        
        # 2. Khởi tạo lõi điều phối (Application Layer)
        crawler_engine = MultiThreadedNovelCrawler(fetcher=fetcher, repository=repo)
        
        # 3. Kích hoạt tiến trình cào
        url = "https://truyenfull.io"
        crawler_engine.crawl_full_novel(url)
    

Để hoàn thiện toàn bộ hệ thống crawl truyện chữ này, bạn có cần hỗ trợ thiết kế tiếp phần nào dưới đây không:

  * Triển khai cơ chế Resume Crawl (Nếu đang cào 1000 chương mà bị ngắt mạng, khi chạy lại hệ thống sẽ tự động bỏ qua các chương đã có trong SQLite và cào tiếp)?
  * Xây dựng thêm một Export Service để kết xuất dữ liệu từ SQLite ra file EPUB hoặc TXT để đọc offline?