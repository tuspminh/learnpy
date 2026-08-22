Dưới đây là kiến trúc dự án **`tfcrawler`** được thiết kế chuẩn theo **Clean Architecture**, **Domain-Driven Design (DDD)** và các nguyên lý **SOLID**, đáp ứng đầy đủ yêu cầu của bạn.

---

### **1. Cấu trúc thư mục (Project Layout)**

Dự án tuân theo mô hình 4 lớp chuẩn của Clean Architecture / DDD:

```text
tfcrawler/
├── pyproject.toml
├── README.md
└── tfcrawler/
    ├── __init__.py
    ├── domain/                 # 1. Domain Layer (Entities, Value Objects, Domain Interfaces)
    │   ├── __init__.py
    │   ├── models.py           # Novel, Chapter, Listing Entities
    │   └── repositories.py     # Interfaces (Abstractions) cho Repositories
    ├── application/            # 2. Application Layer (Use Cases, DTOs)
    │   ├── __init__.py
    │   ├── crawler_service.py  # Interface cho HTML Scraper
    │   └── use_cases.py        # Logic nghiệp vụ (Scrape Listing, Scrape Novel, Update Pending)
    ├── infrastructure/         # 3. Infrastructure Layer (SQLite, Selectolax Scraper)
    │   ├── __init__.py
    │   ├── database.py         # Khởi tạo SQLite DB & SQLite DDL
    │   ├── sqlite_repository.py# Concrete implementation của Repositories (Thuần SQL)
    │   └── selectolax_scraper.py# Concrete implementation của Scraper
    └── cli/                    # 4. Presentation / User Interface Layer (Click CLI)
        ├── __init__.py
        └── main.py             # CLI Entry point với Click

```

---

### **2. Chi tiết Cài đặt Source Code**

#### **`pyproject.toml`** (Dùng `uv` & Python 3.13)

```toml
[project]
name = "tfcrawler"
version = "0.1.0"
description = "Truyenfull Web Scraper with Clean Architecture, DDD, Python 3.13"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "click>=8.1.7",
    "httpx>=0.27.0",
    "selectolax>=0.3.21",
]

[project.scripts]
tfcrawler = "tfcrawler.cli.main:cli"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

```

---

#### **Domain Layer** (`tfcrawler/domain/models.py` & `repositories.py`)

Thực thể cốt lõi (Entities & Aggregates) độc lập hoàn toàn với framework và thư viện ngoài.

```python
# tfcrawler/domain/models.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Chapter:
    slug: str
    novel_slug: str
    chapter_no: int
    title: str
    content: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Novel:
    slug: str
    title: str
    author: Optional[str] = None
    cover_url: Optional[str] = None
    description: Optional[str] = None
    is_full: bool = False
    total_chapters: int = 0
    crawled_chapters: int = 0
    updated_at: datetime = field(default_factory=datetime.now)

```

```python
# tfcrawler/domain/repositories.py
from abc import ABC, abstractmethod
from typing import List, Optional
from tfcrawler.domain.models import Novel, Chapter


class NovelRepository(ABC):
    @abstractmethod
    def save_or_update(self, novel: Novel) -> None:
        pass

    @abstractmethod
    def get_by_slug(self, slug: str) -> Optional[Novel]:
        pass

    @abstractmethod
    def get_pending_or_incomplete_novels(self, limit: int) -> List[Novel]:
        pass

    @abstractmethod
    def update_progress(self, slug: str, crawled_chapters: int, is_full: bool) -> None:
        pass


class ChapterRepository(ABC):
    @abstractmethod
    def save(self, chapter: Chapter) -> None:
        pass

    @abstractmethod
    def exists(self, novel_slug: str, chapter_no: int) -> bool:
        pass

```

---

#### **Application Layer** (`tfcrawler/application/`)

Chứa các abstractions về scraper và các **Use Case** điều phối dữ liệu giữa Scraper và Repositories.

```python
# tfcrawler/application/crawler_service.py
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from tfcrawler.domain.models import Novel, Chapter


class NovelScraper(ABC):
    @abstractmethod
    def fetch_listing(self, listing_name: str, max_pages: int = 1) -> List[Novel]:
        """Cào danh sách novel từ listing (ví dụ: danh-sach/truyen-moi)"""
        pass

    @abstractmethod
    def fetch_novel_info(self, novel_slug: str) -> Tuple[Novel, List[str]]:
        """Cào thông tin novel và danh sách slug của toàn bộ chapter"""
        pass

    @abstractmethod
    def fetch_chapter_content(self, novel_slug: str, chapter_slug: str, chapter_no: int) -> Chapter:
        """Cào nội dung chi tiết của 1 chương"""
        pass

```

```python
# tfcrawler/application/use_cases.py
from typing import List
from tfcrawler.domain.repositories import NovelRepository, ChapterRepository
from tfcrawler.application.crawler_service import NovelScraper


class ScrapeListingUseCase:
    def __init__(self, scraper: NovelScraper, novel_repo: NovelRepository):
        self.scraper = scraper
        self.novel_repo = novel_repo

    def execute(self, listing_name: str, max_pages: int = 1) -> int:
        novels = self.scraper.fetch_listing(listing_name, max_pages=max_pages)
        for novel in novels:
            self.novel_repo.save_or_update(novel)
        return len(novels)


class ScrapeNovelUseCase:
    def __init__(
        self,
        scraper: NovelScraper,
        novel_repo: NovelRepository,
        chapter_repo: ChapterRepository,
    ):
        self.scraper = scraper
        self.novel_repo = novel_repo
        self.chapter_repo = chapter_repo

    def execute(self, novel_slug: str, num_chapters: int = 0) -> int:
        novel, chapter_slugs = self.scraper.fetch_novel_info(novel_slug)
        existing_novel = self.novel_repo.get_by_slug(novel_slug)

        if existing_novel:
            novel.crawled_chapters = existing_novel.crawled_chapters

        self.novel_repo.save_or_update(novel)

        target_slugs = chapter_slugs
        if num_chapters > 0:
            target_slugs = chapter_slugs[:num_chapters]

        count = 0
        for idx, ch_slug in enumerate(target_slugs, start=1):
            if self.chapter_repo.exists(novel_slug, idx):
                continue

            chapter = self.scraper.fetch_chapter_content(novel_slug, ch_slug, idx)
            self.chapter_repo.save(chapter)
            count += 1
            self.novel_repo.update_progress(novel_slug, crawled_chapters=idx, is_full=novel.is_full)

        return count


class ScrapeBatchNovelsUseCase:
    def __init__(self, scrape_novel_uc: ScrapeNovelUseCase, novel_repo: NovelRepository):
        self.scrape_novel_uc = scrape_novel_uc
        self.novel_repo = novel_repo

    def execute(self, num_novels: int, num_chapters_per_novel: int) -> None:
        pending_novels = self.novel_repo.get_pending_or_incomplete_novels(limit=num_novels)
        for novel in pending_novels:
            self.scrape_novel_uc.execute(novel.slug, num_chapters=num_chapters_per_novel)

```

---

#### **Infrastructure Layer** (`tfcrawler/infrastructure/`)

Sử dụng **Selectolax** cho việc parsing HTML và **SQLite (Thuần SQL - `sqlite3`)** cho việc lưu trữ.

```python
# tfcrawler/infrastructure/database.py
import sqlite3

def init_db(db_path: str = "truyenfull.db") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS novels (
                slug TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT,
                cover_url TEXT,
                description TEXT,
                is_full INTEGER DEFAULT 0,
                total_chapters INTEGER DEFAULT 0,
                crawled_chapters INTEGER DEFAULT 0,
                updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS chapters (
                novel_slug TEXT,
                chapter_no INTEGER,
                slug TEXT,
                title TEXT NOT NULL,
                content TEXT,
                created_at TEXT,
                PRIMARY KEY (novel_slug, chapter_no),
                FOREIGN KEY (novel_slug) REFERENCES novels(slug)
            );
        """)
    return conn

```

```python
# tfcrawler/infrastructure/sqlite_repository.py
import sqlite3
from typing import List, Optional
from tfcrawler.domain.models import Novel, Chapter
from tfcrawler.domain.repositories import NovelRepository, ChapterRepository


class SQLiteNovelRepository(NovelRepository):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save_or_update(self, novel: Novel) -> None:
        sql = """
            INSERT INTO novels (slug, title, author, cover_url, description, is_full, total_chapters, crawled_chapters, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(slug) DO UPDATE SET
                title = excluded.title,
                author = COALESCE(excluded.author, novels.author),
                cover_url = COALESCE(excluded.cover_url, novels.cover_url),
                description = COALESCE(excluded.description, novels.description),
                is_full = excluded.is_full,
                total_chapters = excluded.total_chapters,
                updated_at = excluded.updated_at;
        """
        with self.conn:
            self.conn.execute(sql, (
                novel.slug, novel.title, novel.author, novel.cover_url,
                novel.description, int(novel.is_full), novel.total_chapters,
                novel.crawled_chapters, novel.updated_at.isoformat()
            ))

    def get_by_slug(self, slug: str) -> Optional[Novel]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM novels WHERE slug = ?", (slug,))
        row = cursor.fetchone()
        if not row:
            return None
        return Novel(
            slug=row["slug"], title=row["title"], author=row["author"],
            cover_url=row["cover_url"], description=row["description"],
            is_full=bool(row["is_full"]), total_chapters=row["total_chapters"],
            crawled_chapters=row["crawled_chapters"]
        )

    def get_pending_or_incomplete_novels(self, limit: int) -> List[Novel]:
        cursor = self.conn.cursor()
        sql = """
            SELECT * FROM novels 
            WHERE is_full = 0 OR crawled_chapters < total_chapters 
            LIMIT ?
        """
        cursor.execute(sql, (limit,))
        rows = cursor.fetchall()
        return [Novel(
            slug=r["slug"], title=r["title"], author=r["author"],
            cover_url=r["cover_url"], description=r["description"],
            is_full=bool(r["is_full"]), total_chapters=r["total_chapters"],
            crawled_chapters=r["crawled_chapters"]
        ) for r in rows]

    def update_progress(self, slug: str, crawled_chapters: int, is_full: bool) -> None:
        with self.conn:
            self.conn.execute(
                "UPDATE novels SET crawled_chapters = ?, is_full = ? WHERE slug = ?",
                (crawled_chapters, int(is_full), slug)
            )


class SQLiteChapterRepository(ChapterRepository):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, chapter: Chapter) -> None:
        sql = """
            INSERT INTO chapters (novel_slug, chapter_no, slug, title, content, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(novel_slug, chapter_no) DO UPDATE SET
                title = excluded.title,
                content = excluded.content;
        """
        with self.conn:
            self.conn.execute(sql, (
                chapter.novel_slug, chapter.chapter_no, chapter.slug,
                chapter.title, chapter.content, chapter.created_at.isoformat()
            ))

    def exists(self, novel_slug: str, chapter_no: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT 1 FROM chapters WHERE novel_slug = ? AND chapter_no = ?",
            (novel_slug, chapter_no)
        )
        return cursor.fetchone() is not None

```

```python
# tfcrawler/infrastructure/selectolax_scraper.py
import httpx
from selectolax.parser import HTMLParser
from typing import List, Tuple
from tfcrawler.domain.models import Novel, Chapter
from tfcrawler.application.crawler_service import NovelScraper


class SelectolaxTruyenFullScraper(NovelScraper):
    BASE_URL = "https://truyenfull.live"

    def __init__(self):
        self.client = httpx.Client(
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            follow_redirects=True,
            timeout=10.0
        )

    def fetch_listing(self, listing_name: str, max_pages: int = 1) -> List[Novel]:
        novels = []
        url = f"{self.BASE_URL}/{listing_name}"
        resp = self.client.get(url)
        if resp.status_code != 200:
            return novels

        tree = HTMLParser(resp.text)
        for node in tree.css(".list-truyen .row"):
            title_elem = node.css_first(".truyen-title a")
            if not title_elem:
                continue
            
            href = title_elem.attributes.get("href", "").strip("/")
            slug = href.split("/")[-1]
            title = title_elem.text(strip=True)
            
            author_elem = node.css_first(".author")
            author = author_elem.text(strip=True) if author_elem else None

            novels.append(Novel(slug=slug, title=title, author=author))
        return novels

    def fetch_novel_info(self, novel_slug: str) -> Tuple[Novel, List[str]]:
        url = f"{self.BASE_URL}/{novel_slug}"
        resp = self.client.get(url)
        tree = HTMLParser(resp.text)

        title = tree.css_first("h3.title").text(strip=True) if tree.css_first("h3.title") else novel_slug
        author = tree.css_first("a[itemprop='author']").text(strip=True) if tree.css_first("a[itemprop='author']") else None
        
        cover_node = tree.css_first(".info-holder .book img")
        cover_url = cover_node.attributes.get("src") if cover_node else None

        desc_node = tree.css_first(".desc-text")
        description = desc_node.text(strip=True) if desc_node else None

        is_full = bool(tree.css_first(".full-label"))

        # Lấy danh sách chapter slugs
        chapter_slugs = []
        for a_tag in tree.css("#list-chapter .list-chapter a"):
            ch_href = a_tag.attributes.get("href", "").strip("/")
            ch_slug = ch_href.split("/")[-1]
            chapter_slugs.append(ch_slug)

        novel = Novel(
            slug=novel_slug,
            title=title,
            author=author,
            cover_url=cover_url,
            description=description,
            is_full=is_full,
            total_chapters=len(chapter_slugs)
        )
        return novel, chapter_slugs

    def fetch_chapter_content(self, novel_slug: str, chapter_slug: str, chapter_no: int) -> Chapter:
        url = f"{self.BASE_URL}/{novel_slug}/{chapter_slug}"
        resp = self.client.get(url)
        tree = HTMLParser(resp.text)

        title_elem = tree.css_first(".chapter-title")
        title = title_elem.text(strip=True) if title_elem else f"Chương {chapter_no}"

        content_elem = tree.css_first("#chapter-c")
        content = content_elem.html if content_elem else ""

        return Chapter(
            slug=chapter_slug,
            novel_slug=novel_slug,
            chapter_no=chapter_no,
            title=title,
            content=content
        )

```

---

#### **Presentation / CLI Layer** (`tfcrawler/cli/main.py`)

Giao diện dòng lệnh bằng **Click**, đóng vai trò Dependency Injection Container để lắp ráp các lớp lại với nhau.

```python
# tfcrawler/cli/main.py
import click
from tfcrawler.infrastructure.database import init_db
from tfcrawler.infrastructure.sqlite_repository import SQLiteNovelRepository, SQLiteChapterRepository
from tfcrawler.infrastructure.selectolax_scraper import SelectolaxTruyenFullScraper
from tfcrawler.application.use_cases import (
    ScrapeListingUseCase,
    ScrapeNovelUseCase,
    ScrapeBatchNovelsUseCase,
)


@click.group()
def cli():
    """TFCrawler - CLI Tool cào truyện từ TruyenFull"""
    pass


@cli.group()
def scape():
    """Nhóm lệnh cào dữ liệu"""
    pass


@scape.command("truyenfull")
@click.argument("target")
@click.argument("arg1", required=False, type=int, default=0)
@click.argument("arg2", required=False, type=int, default=0)
def truyenfull(target: str, arg1: int, arg2: int):
    """Lệnh chính cào theo listing, novel-slug, hoặc batch novel.
    
    Ví dụ sử dụng:
    1. tfcrawler scape truyenfull listing-name
    2. tfcrawler scape truyenfull novel-slug [num-chapters]
    3. tfcrawler scape truyenfull novel <num-novels> <num-chapters-per-novel>
    """
    conn = init_db()
    novel_repo = SQLiteNovelRepository(conn)
    chapter_repo = SQLiteChapterRepository(conn)
    scraper = SelectolaxTruyenFullScraper()

    if target == "novel":
        # Case 3: Batch Novels -> tfcrawler scape truyenfull novel num_novels num_chapters_per_novel
        num_novels = arg1 if arg1 > 0 else 10
        num_chapters = arg2
        
        click.echo(f"🔄 Đang tiến hành cào batch {num_novels} truyện...")
        scrape_novel_uc = ScrapeNovelUseCase(scraper, novel_repo, chapter_repo)
        batch_uc = ScrapeBatchNovelsUseCase(scrape_novel_uc, novel_repo)
        batch_uc.execute(num_novels=num_novels, num_chapters_per_novel=num_chapters)
        click.echo("✅ Hoàn tất cào batch!")

    elif target.startswith("danh-sach") or "/" in target or "hot" in target or "moi" in target:
        # Case 1: Listing -> tfcrawler scape truyenfull listing-name
        click.echo(f"🔄 Đang cào danh sách: {target}...")
        use_case = ScrapeListingUseCase(scraper, novel_repo)
        count = use_case.execute(listing_name=target)
        click.echo(f"✅ Đã lưu/cập nhật {count} truyện vào SQLite.")

    else:
        # Case 2: Single Novel Slug -> tfcrawler scape truyenfull novel-slug [num-chapters]
        num_chapters = arg1
        click.echo(f"🔄 Đang cào truyện {target} (Chương: {'Tất cả' if num_chapters == 0 else num_chapters})...")
        use_case = ScrapeNovelUseCase(scraper, novel_repo, chapter_repo)
        crawled = use_case.execute(novel_slug=target, num_chapters=num_chapters)
        click.echo(f"✅ Đã cào xong {crawled} chương mới!")


if __name__ == "__main__":
    cli()

```

---

### **3. Hướng dẫn chạy chương trình với `uv**`

1. **Khởi tạo dự án & Cài đặt:**
```bash
uv sync

```


2. **Chạy các câu lệnh cào:**
* **Cào Listing:**
```bash
uv run tfcrawler scape truyenfull ds-truyen-moi

```


* **Cào 1 Novel (Tất cả hoặc chỉ định số chương):**
```bash
# Cào toàn bộ chương
uv run tfcrawler scape truyenfull vo-thuong-sieu-viet

# Cào 10 chương đầu
uv run tfcrawler scape truyenfull vo-thuong-sieu-viet 10

```


* **Cào Batch các Novel chưa hoàn thành:**
```bash
# Cào 5 truyện chưa xong, mỗi truyện cào 20 chương
uv run tfcrawler scape truyenfull novel 5 20

# Cào 5 truyện chưa xong, cào hết chương (truyền 0)
uv run tfcrawler scape truyenfull novel 5 0

```