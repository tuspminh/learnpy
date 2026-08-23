Để đưa phần Database tuân thủ nghiêm ngặt Kiến trúc Clean, DDD và nguyên lý SOLID, chúng ta cần giải quyết hai vấn đề lớn của code cũ:

  1. Vi phạm Dependency Inversion (D trong SOLID): Lớp Use Case đang phụ thuộc trực tiếp vào class cụ thể `SQLiteRepository` ở tầng Infrastructure.
  2. Thiếu tính trừu tượng (DDD): Repository phải là một Interface (Port) nằm ở tầng Domain hoặc Application, còn SQLite chỉ là một Adapter thực thi (Implementation) nằm ở tầng Infrastructure.



Dưới đây là thiết kế lại toàn bộ phần Database và cách kết nối nó vào hệ thống.

* * *

## 1\. Tầng Domain: Định nghĩa Repository Interface (Port)

Theo DDD và Clean Architecture, Interface của Repository thuộc về tầng Domain (hoặc Application). Tầng này không quan tâm bạn dùng SQLite, MySQL hay MongoDB.

Thêm file `tfcrawler/domain/repositories.py`:
    
    
    from abc import ABC, abstractmethod
    from typing import List, Optional
    from tfcrawler.domain.models import Novel, Chapter
    
    class NovelRepository(ABC):
        """Interface định nghĩa các hành vi thao tác với thực thể Novel (DDD Repository)."""
    
        @abstractmethod
        def save(self, novel: Novel) -> None:
            """Lưu mới hoặc cập nhật thông tin Novel."""
            pass
    
        @abstractmethod
        def get_incomplete_novels(self, limit: int) -> List[Novel]:
            """Lấy danh sách các truyện chưa hoàn thành."""
            pass
    
    class ChapterRepository(ABC):
        """Interface định nghĩa các hành vi thao tác với thực thể Chapter."""
    
        @abstractmethod
        def save(self, chapter: Chapter) -> None:
            """Lưu mới hoặc cập nhật thông tin Chapter."""
            pass
    
        @abstractmethod
        def get_existing_slugs(self, novel_slug: str) -> List[str]:
            """Lấy danh sách các slug chương đã được cào nội dung."""
            pass
    

_Lưu ý: Tách riêng`NovelRepository` và `ChapterRepository` tuân thủ nghiêm ngặt nguyên lý Interface Segregation (I trong SOLID)._

* * *

## 2\. Tầng Infrastructure: Thực thi bằng SQLite (Adapter)

Tầng này chứa mã nguồn cấu hình SQL thuần, thực thi các Interface đã định nghĩa ở trên.

Sửa lại file `tfcrawler/infrastructure/database.py`:
    
    
    import sqlite3
    from typing import List
    from tfcrawler.domain.models import Novel, Chapter
    from tfcrawler.domain.repositories import NovelRepository, ChapterRepository
    
    class SQLiteDatabase:
        """Quản lý kết nối và khởi tạo Database (Single Responsibility)."""
        def __init__(self, db_path: str = "truyenfull.db"):
            self.db_path = db_path
            self._init_db()
    
        def _init_db(self):
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS novels (
                        slug TEXT PRIMARY KEY,
                        title TEXT,
                        author TEXT,
                        cover_url TEXT,
                        description TEXT,
                        is_full INTEGER DEFAULT 0
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chapters (
                        slug TEXT PRIMARY KEY,
                        novel_slug TEXT,
                        chapter_no INTEGER,
                        title TEXT,
                        content TEXT,
                        FOREIGN KEY(novel_slug) REFERENCES novels(slug)
                    )
                """)
                conn.commit()
    
        def get_connection(self):
            return sqlite3.connect(self.db_path)
    
    
    class SQLiteNovelRepository(NovelRepository):
        """Thực thi NovelRepository bằng SQLite thuần SQL."""
        def __init__(self, db: SQLiteDatabase):
            self.db = db
    
        def save(self, novel: Novel) -> None:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO novels (slug, title, author, cover_url, description, is_full)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(slug) DO UPDATE SET
                        title = coalesce(excluded.title, novels.title),
                        author = coalesce(excluded.author, novels.author),
                        cover_url = coalesce(excluded.cover_url, novels.cover_url),
                        description = coalesce(excluded.description, novels.description),
                        is_full = excluded.is_full
                """, (novel.slug, novel.title, novel.author, novel.cover_url, novel.description, int(novel.is_full)))
                conn.commit()
    
        def get_incomplete_novels(self, limit: int) -> List[Novel]:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT slug, title, is_full FROM novels WHERE is_full = 0 LIMIT ?", (limit,))
                return [Novel(slug=row[0], title=row[1], is_full=bool(row[2])) for row in cursor.fetchall()]
    
    
    class SQLiteChapterRepository(ChapterRepository):
        """Thực thi ChapterRepository bằng SQLite thuần SQL."""
        def __init__(self, db: SQLiteDatabase):
            self.db = db
    
        def save(self, chapter: Chapter) -> None:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO chapters (slug, novel_slug, chapter_no, title, content)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(slug) DO UPDATE SET
                        title = excluded.title,
                        content = coalesce(excluded.content, chapters.content)
                """, (chapter.slug, chapter.novel_slug, chapter.chapter_no, chapter.title, chapter.content))
                conn.commit()
    
        def get_existing_slugs(self, novel_slug: str) -> List[str]:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT slug FROM chapters WHERE novel_slug = ? AND content IS NOT NULL", (novel_slug,))
                return [row[0] for row in cursor.fetchall()]
    

* * *

## 3\. Tầng Application: Cập nhật Use Cases (Dependency Inversion)

Bây giờ, các Use Case sẽ nhận vào `NovelRepository` và `ChapterRepository` (dạng trừu tượng - Abstraction). Chúng không cần biết cơ sở dữ liệu phía sau là gì.

## Tác vụ cào Listing (`tfcrawler/use_cases/scrape_listing.py`)
    
    
    from tfcrawler.domain.repositories import NovelRepository
    from tfcrawler.infrastructure.scraper import TruyenFullScraper
    
    class ScrapeListingUseCase:
        # Phụ thuộc vào Interface (Lớp trừu tượng), không phụ thuộc vào SQLite cụ thể
        def __init__(self, novel_repo: NovelRepository, scraper: TruyenFullScraper):
            self.novel_repo = novel_repo
            self.scraper = scraper
    
        def execute(self, listing_name: str):
            print(f"Bắt đầu cào listing: {listing_name}")
            novels = self.scraper.scrape_listing(listing_name)
            for novel in novels:
                self.novel_repo.save(novel)
            print(f"Đã cập nhật thành công {len(novels)} truyện.")
    

## Tác vụ cào Truyện (`tfcrawler/use_cases/scrape_novel.py`)
    
    
    from typing import Optional
    from tfcrawler.domain.repositories import NovelRepository, ChapterRepository
    from tfcrawler.infrastructure.scraper import TruyenFullScraper
    
    class ScrapeNovelUseCase:
        def __init__(self, novel_repo: NovelRepository, chapter_repo: ChapterRepository, scraper: TruyenFullScraper):
            self.novel_repo = novel_repo
            self.chapter_repo = chapter_repo
            self.scraper = scraper
    
        def execute_single(self, novel_slug: str, num_chapters: Optional[int] = None):
            novel, chapters = self.scraper.scrape_novel_details(novel_slug)
            self.novel_repo.save(novel)
            
            existing_slugs = self.chapter_repo.get_existing_slugs(novel_slug)
            chapters_to_scrape = [c for c in chapters if c.slug not in existing_slugs]
    
            if num_chapters and num_chapters > 0:
                chapters_to_scrape = chapters_to_scrape[:num_chapters]
    
            print(f"Đang cào {len(chapters_to_scrape)} chương cho truyện: {novel_slug}")
            for chapter in chapters_to_scrape:
                content = self.scraper.scrape_chapter_content(novel_slug, chapter.slug)
                if content:
                    chapter.content = content
                    self.chapter_repo.save(chapter)
    
        def execute_batch(self, num_novels: int, num_chapters_per_novel: int):
            pending_novels = self.novel_repo.get_incomplete_novels(limit=num_novels)
            print(f"Tìm thấy {len(pending_novels)} truyện cần cập nhật.")
            
            for novel in pending_novels:
                limit = None if num_chapters_per_novel == 0 else num_chapters_per_novel
                self.execute_single(novel.slug, num_chapters=limit)
    

* * *

## 4\. Tầng Presentation: Khởi tạo và Tiêm phụ thuộc (Dependency Injection)

Tại file `cli.py`, chúng ta đóng vai trò là nhà cấu hình hệ thống (Composer), khởi tạo các thực thể cụ thể ở tầng `Infrastructure` rồi "tiêm" (inject) chúng vào tầng `Application`.

Sửa lại file `tfcrawler/cli.py`:
    
    
    import click
    from tfcrawler.infrastructure.database import SQLiteDatabase, SQLiteNovelRepository, SQLiteChapterRepository
    from tfcrawler.infrastructure.scraper import TruyenFullScraper
    from tfcrawler.use_cases.scrape_listing import ScrapeListingUseCase
    from tfcrawler.use_cases.scrape_novel import ScrapeNovelUseCase
    
    # 1. Khởi tạo tầng hạ tầng hạ cấp (Low-level infrastructure)
    db_instance = SQLiteDatabase()
    scraper_instance = TruyenFullScraper()
    
    # 2. Khởi tạo các Adapters tương ứng với Interface của Domain
    novel_repo = SQLiteNovelRepository(db_instance)
    chapter_repo = SQLiteChapterRepository(db_instance)
    
    @click.group()
    def main():
        """Hệ thống cào dữ liệu truyenfull.live tuân thủ SOLID."""
        pass
    
    @main.group()
    def scape():
        pass
    
    @scape.command(name="truyenfull")
    @click.argument("target")
    @click.argument("sub_target", required=False)
    @click.argument("extra_arg", required=False, type=int)
    def truyenfull(target, sub_target, extra_arg):
        # Kịch bản 3: Cào hàng loạt truyện chưa hoàn thành từ DB
        if target == "novel" and sub_target is not None and extra_arg is not None:
            use_case = ScrapeNovelUseCase(novel_repo, chapter_repo, scraper_instance)
            use_case.execute_batch(num_novels=int(sub_target), num_chapters_per_novel=extra_arg)
            return
    
        # Kịch bản 1: Cào từ listing (Ví dụ: /truyen-hot)
        if sub_target is None:
            use_case = ScrapeListingUseCase(novel_repo, scraper_instance)
            use_case.execute(listing_name=target)
            return
    
        # Kịch bản 2: Cào một truyện cụ thể theo novel-slug
        if sub_target is not None:
            num_chapters = int(sub_target) if sub_target.isdigit() else None
            use_case = ScrapeNovelUseCase(novel_repo, chapter_repo, scraper_instance)
            use_case.execute_single(novel_slug=target, num_chapters=num_chapters)
            return
    
    if __name__ == "__main__":
        main()
    

* * *

## Điểm cải tiến SOLID & Clean Architecture cốt lõi ở đây:

  * Single Responsibility (S): Lớp `SQLiteDatabase` chỉ lo kết nối và tạo bảng. Các lớp `Repository` chỉ lo ánh xạ câu lệnh SQL. Lớp `UseCase` chỉ lo logic nghiệp vụ cào và lưu.
  * Open/Closed (O): Nếu ngày mai bạn muốn chuyển từ SQLite sang Postgres hoặc lưu file JSON, bạn không cần sửa một dòng code nào trong tầng `domain/` hay `use_cases/`. Bạn chỉ cần viết một class mới thực thi `NovelRepository` ở tầng `infrastructure/`.
  * Dependency Inversion (D): Luồng kiểm soát (Control Flow) đi từ CLI -> UseCase -> Repository. Nhưng luồng phụ thuộc (Dependency Flow) thì đảo ngược: Tầng Infrastructure phụ thuộc ngược vào Domain (thông qua việc `implements` các Interface).



Bạn có muốn tôi viết thêm Unit Test bằng `unittest` hoặc `pytest` để chứng minh cấu trúc này cực kỳ dễ test nhờ việc Mocking các Repository không?