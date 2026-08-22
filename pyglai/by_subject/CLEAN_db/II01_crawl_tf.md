Dưới đây là thiết kế và mã nguồn toàn diện cho ứng dụng tfcrawler được xây dựng bằng Python 3.13, tuân thủ nghiêm ngặt kiến trúc Clean Architecture, Domain-Driven Design (DDD) và các nguyên lý SOLID.

## Cấu trúc thư mục (Clean Architecture & DDD)
    
    
    tfcrawler/
    ├── pyproject.toml
    ├── tfcrawler/
    │   ├── __init__.py
    │   ├── cli.py                     # Giao diện CLI (Click) - Presentation Layer
    │   ├── domain/                    # Nghiệp vụ cốt lõi - Domain Layer (Enterprise Rules)
    │   │   ├── __init__.py
    │   │   └── models.py              # Entity, Value Object, Aggregate Root
    │   ├── use_cases/                 # Ca sử dụng - Application Layer (Application Rules)
    │   │   ├── __init__.py
    │   │   ├── scrape_listing.py
    │   │   └── scrape_novel.py
    │   └── infrastructure/            # Thư viện ngoại vi - Infrastructure Layer
    │       ├── __init__.py
    │       ├── database.py            # SQLite (Thuần SQL)
    │       └── scraper.py             # Selectolax & HTTP Client
    

* * *

## 1\. Thiết lập dự án (`pyproject.toml`)

Sử dụng cấu hình hiện đại với `uv` và Python 3.13.
    
    
    [project]
    name = "tfcrawler"
    version = "0.1.0"
    description = "Truyenfull Scraper với Clean Architecture và DDD"
    readme = "README.md"
    requires-python = ">=3.13"
    dependencies = [
        "click>=8.1.7",
        "selectolax>=0.3.21",
        "httpx>=0.27.0",
    ]
    
    [project.scripts]
    tfcrawler = "tfcrawler.cli:main"
    

* * *

## 2\. Lớp Domain (`tfcrawler/domain/models.py`)

Lớp chứa thực thể (Entities) độc lập, không phụ thuộc vào bất kỳ thư viện hay cơ sở dữ liệu nào.
    
    
    from dataclasses import dataclass, field
    from typing import List, Optional
    
    @dataclass
    class Chapter:
        """Value Object / Entity đại diện cho một chương truyện."""
        slug: str
        novel_slug: str
        chapter_no: int
        title: str
        content: Optional[str] = None
    
    @dataclass
    class Novel:
        """Aggregate Root đại diện cho một bộ truyện."""
        slug: str
        title: Optional[str] = None
        author: Optional[str] = None
        cover_url: Optional[str] = None
        description: Optional[str] = None
        is_full: bool = False
        chapters: List[Chapter] = field(default_factory=list)
    
        def add_chapter(self, chapter: Chapter):
            self.chapters.append(chapter)
    

* * *

## 3\. Lớp Cơ sở hạ tầng (Infrastructure Layer)

Chịu trách nhiệm tương tác phần cứng và thư viện bên thứ ba (SQLite thuần SQL, Selectolax).

## Kết nối Database (`tfcrawler/infrastructure/database.py`)
    
    
    import sqlite3
    from typing import List, Optional
    from tfcrawler.domain.models import Novel, Chapter
    
    class SQLiteRepository:
        """Tương tác DB sử dụng thuần SQL tuân thủ Interface Segregation."""
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
    
        def save_or_update_novel(self, novel: Novel):
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO novels (slug, title, author, cover_url, description, is_full)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(slug) DO UPDATE SET
                        title=coalesce(excluded.title, novels.title),
                        author=coalesce(excluded.author, novels.author),
                        cover_url=coalesce(excluded.cover_url, novels.cover_url),
                        description=coalesce(excluded.description, novels.description),
                        is_full=excluded.is_full
                """, (novel.slug, novel.title, novel.author, novel.cover_url, novel.description, int(novel.is_full)))
                conn.commit()
    
        def save_or_update_chapter(self, chapter: Chapter):
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO chapters (slug, novel_slug, chapter_no, title, content)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(slug) DO UPDATE SET
                        title=excluded.title,
                        content=coalesce(excluded.content, chapters.content)
                """, (chapter.slug, chapter.novel_slug, chapter.chapter_no, chapter.title, chapter.content))
                conn.commit()
    
        def get_incomplete_novels(self, limit: int) -> List[Novel]:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT slug, title, is_full FROM novels WHERE is_full = 0 LIMIT ?", (limit,))
                return [Novel(slug=row[0], title=row[1], is_full=bool(row[2])) for row in cursor.fetchall()]
    
        def get_existing_chapter_slugs(self, novel_slug: str) -> List[str]:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT slug FROM chapters WHERE novel_slug = ? AND content IS NOT NULL", (novel_slug,))
                return [row[0] for row in cursor.fetchall()]
    

## Bộ cào dữ liệu (`tfcrawler/infrastructure/scraper.py`)
    
    
    import httpx
    from selectolax.lexbor import LexborHTMLParser
    from typing import List, Tuple, Optional
    from tfcrawler.domain.models import Novel, Chapter
    
    class TruyenFullScraper:
        """Xử lý việc phân tích cú pháp HTML sử dụng Selectolax."""
        BASE_URL = "https://truyenfull.live"
    
        def __init__(self):
            self.client = httpx.Client(headers={"User-Agent": "Mozilla/5.0"}, follow_redirects=True)
    
        def fetch_html(self, url: str) -> Optional[LexborHTMLParser]:
            try:
                resp = self.client.get(url)
                if resp.status_code == 200:
                    return LexborHTMLParser(resp.text)
            except Exception as e:
                print(f"Lỗi tải URL {url}: {e}")
            return None
    
        def scrape_listing(self, listing_name: str) -> List[Novel]:
            novels = []
            page = 1
            while True:
                url = f"{self.BASE_URL}/{listing_name}/trang-{page}" if page > 1 else f"{self.BASE_URL}/{listing_name}"
                parser = self.fetch_html(url)
                if not parser:
                    break
                
                # Giả định cấu hình selector, thay đổi theo thực tế của trang
                elements = parser.css("div.list-truyen div.row")
                if not elements:
                    break
                    
                for el in elements:
                    a_tag = el.css_first("h3.truyen-title a")
                    if a_tag:
                        href = a_tag.attributes.get("href", "")
                        slug = href.strip("/").split("/")[-1]
                        title = a_tag.text().strip()
                        novels.append(Novel(slug=slug, title=title))
                
                # Kiểm tra xem có trang tiếp theo không
                if not parser.css_first("ul.pagination li.next"):
                    break
                page += 1
            return novels
    
        def scrape_novel_details(self, novel_slug: str) -> Tuple[Novel, List[Chapter]]:
            url = f"{self.BASE_URL}/{novel_slug}"
            parser = self.fetch_html(url)
            if not parser:
                return Novel(slug=novel_slug), []
    
            title = parser.css_first("h3.title").text().strip() if parser.css_first("h3.title") else ""
            author = parser.css_first("a[itemprop='author']").text().strip() if parser.css_first("a[itemprop='author']") else ""
            cover_url = parser.css_first("div.info-holder img").attributes.get("src", "") if parser.css_first("div.info-holder img") else ""
            desc = parser.css_first("div.desc-text").text().strip() if parser.css_first("div.desc-text") else ""
            is_full = parser.css_first("span.label-title.full") is not None
    
            novel = Novel(slug=novel_slug, title=title, author=author, cover_url=cover_url, description=desc, is_full=is_full)
            
            # Cào danh sách chương từ tất cả các trang của novel
            chapters = []
            page = 1
            while True:
                c_url = f"{self.BASE_URL}/{novel_slug}/trang-{page}" if page > 1 else url
                c_parser = self.fetch_html(c_url)
                if not c_parser:
                    break
                
                c_elements = c_parser.css("ul.list-chapter li a")
                if not c_elements:
                    break
    
                for idx, el in enumerate(c_elements, start=len(chapters) + 1):
                    c_href = el.attributes.get("href", "")
                    c_slug = c_href.strip("/").split("/")[-1]
                    c_title = el.text().strip()
                    chapters.append(Chapter(slug=c_slug, novel_slug=novel_slug, chapter_no=idx, title=c_title))
                    
                if not c_parser.css_first("ul.pagination li.next"):
                    break
                page += 1
    
            return novel, chapters
    
        def scrape_chapter_content(self, novel_slug: str, chapter_slug: str) -> Optional[str]:
            url = f"{self.BASE_URL}/{novel_slug}/{chapter_slug}"
            parser = self.fetch_html(url)
            if parser and parser.css_first("div.chapter-c"):
                return parser.css_first("div.chapter-c").html
            return None
    

* * *

## 4\. Lớp Ứng dụng (Use Cases Layer)

Nơi thực thi các kịch bản luồng công việc cụ thể của ứng dụng.

## Use Case 1: Cào Danh Sách Truyện (`tfcrawler/use_cases/scrape_listing.py`)
    
    
    from tfcrawler.infrastructure.database import SQLiteRepository
    from tfcrawler.infrastructure.scraper import TruyenFullScraper
    
    class ScrapeListingUseCase:
        def __init__(self, repo: SQLiteRepository, scraper: TruyenFullScraper):
            self.repo = repo
            self.scraper = scraper
    
        def execute(self, listing_name: str):
            print(f"Bắt đầu cào listing: {listing_name}")
            novels = self.scraper.scrape_listing(listing_name)
            for novel in novels:
                self.repo.save_or_update_novel(novel)
            print(f"Đã cập nhật thành công {len(novels)} truyện vào database.")
    

## Use Case 2: Cào Chi Tiết Truyện và Chương (`tfcrawler/use_cases/scrape_novel.py`)
    
    
    from typing import Optional
    from tfcrawler.infrastructure.database import SQLiteRepository
    from tfcrawler.infrastructure.scraper import TruyenFullScraper
    
    class ScrapeNovelUseCase:
        def __init__(self, repo: SQLiteRepository, scraper: TruyenFullScraper):
            self.repo = repo
            self.scraper = scraper
    
        def execute_single(self, novel_slug: str, num_chapters: Optional[int] = None):
            """Cào một truyện đơn lẻ."""
            novel, chapters = self.scraper.scrape_novel_details(novel_slug)
            self.repo.save_or_update_novel(novel)
            
            existing_slugs = self.repo.get_existing_chapter_slugs(novel_slug)
            chapters_to_scrape = [c for c in chapters if c.slug not in existing_slugs]
    
            if num_chapters and num_chapters > 0:
                chapters_to_scrape = chapters_to_scrape[:num_chapters]
    
            print(f"Đang cào {len(chapters_to_scrape)} chương cho truyện: {novel_slug}")
            for chapter in chapters_to_scrape:
                content = self.scraper.scrape_chapter_content(novel_slug, chapter.slug)
                if content:
                    chapter.content = content
                    self.repo.save_or_update_chapter(chapter)
    
        def execute_batch(self, num_novels: int, num_chapters_per_novel: int):
            """Lấy danh sách các truyện chưa hoàn thành trong DB để cào hàng loạt."""
            pending_novels = self.repo.get_incomplete_novels(limit=num_novels)
            print(f"Tìm thấy {len(pending_novels)} truyện cần cập nhật.")
            
            for novel in pending_novels:
                limit = None if num_chapters_per_novel == 0 else num_chapters_per_novel
                self.execute_single(novel.slug, num_chapters=limit)
    

* * *

## 5\. Giao diện CLI - Giao tiếp người dùng (`tfcrawler/cli.py`)

Sử dụng thư viện `Click` điều hướng các Command theo đúng yêu cầu đề bài.
    
    
    import click
    from tfcrawler.infrastructure.database import SQLiteRepository
    from tfcrawler.infrastructure.scraper import TruyenFullScraper
    from tfcrawler.use_cases.scrape_listing import ScrapeListingUseCase
    from tfcrawler.use_cases.scrape_novel import ScrapeNovelUseCase
    
    # Khởi tạo các Dependencies độc lập
    repo = SQLiteRepository()
    scraper = TruyenFullScraper()
    
    @click.group()
    def main():
        """Hệ thống cào dữ liệu truyenfull.live."""
        pass
    
    @main.group()
    def scape():
        """Nhóm lệnh cào dữ liệu từ các nguồn."""
        pass
    
    @scape.command(name="truyenfull")
    @click.argument("target")
    @click.argument("sub_target", required=False)
    @click.argument("extra_arg", required=False, type=int)
    def truyenfull(target, sub_target, extra_arg):
        """
        Điều phối lệnh linh hoạt dựa trên cấu trúc tham số đầu vào.
        
        1. tfcrawler scape truyenfull <listing-name>
        2. tfcrawler scape truyenfull <novel-slug> [<num-chapters>]
        3. tfcrawler scape truyenfull novel <num-novels> <num-chapters-per-novel>
        """
        # Kịch bản 3: tfcrawler scape truyenfull novel <num-novels> <num-chapters-per-novel>
        if target == "novel" and sub_target is not None and extra_arg is not None:
            use_case = ScrapeNovelUseCase(repo, scraper)
            use_case.execute_batch(num_novels=int(sub_target), num_chapters_per_novel=extra_arg)
            return
    
        # Kịch bản 1: tfcrawler scape truyenfull <listing-name>
        # Phân biệt nếu target không phải một cấu trúc số và không có sub_target đi kèm
        if sub_target is None:
            use_case = ScrapeListingUseCase(repo, scraper)
            use_case.execute(listing_name=target)
            return
    
        # Kịch bản 2: tfcrawler scape truyenfull <novel-slug> <num-chapters>
        if sub_target is not None:
            num_chapters = int(sub_target) if sub_target.isdigit() else None
            # Trường hợp nhập dạng: truyenfull novel-slug 10
            if num_chapters is not None:
                use_case = ScrapeNovelUseCase(repo, scraper)
                use_case.execute_single(novel_slug=target, num_chapters=num_chapters)
            # Trường hợp nhập dạng: truyenfull novel-slug (không truyền số lượng chương)
            else:
                use_case = ScrapeNovelUseCase(repo, scraper)
                use_case.execute_single(novel_slug=target, num_chapters=None)
            return
    
    if __name__ == "__main__":
        main()
    

* * *

## Cách vận hành và chạy kiểm thử bằng `uv`

  1. Cài đặt các thư viện cần thiết:
         
         uv pip install -e .
         

  2. Cào danh sách truyện từ 1 danh mục (ví dụ `truyen-hot`):
         
         tfcrawler scape truyenfull truyen-hot
         

  3. Cào một bộ truyện cụ thể (Mặc định cào hết hoặc giới hạn số chương):
         
         tfcrawler scape truyenfull doc-ton-tam-gioi
         tfcrawler scape truyenfull doc-ton-tam-gioi 10
         

  4. Cào cập nhật hàng loạt các truyện chưa full có sẵn trong DB:
         
         # Lấy ra 5 truyện chưa full, mỗi truyện cào thêm tối đa 20 chương mới
         tfcrawler scape truyenfull novel 5 20
         




Bạn có muốn tôi làm rõ hơn về phần cấu trúc Selector của `selectolax` theo đúng cấu trúc DOM thực tế hiện tại của website không?