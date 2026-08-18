Hệ thống đọc, viết và crawl truyện đòi hỏi tách biệt rõ ràng giữa logic nghiệp vụ phức tạp và các tác vụ hạ tầng nặng như cào dữ liệu hay render giao diện.

## 1. Phân chia Bounded Contexts (DDD Context Mapping)

Hệ thống được chia thành 3 **Bounded Context** độc lập để tránh lẫn lộn nghiệp vụ:

| Bounded Context | Trách nhiệm chính | Core Aggregates / Entities |
| --- | --- | --- |
| **Authoring Context** (Viết truyện) | Tác giả sáng tác, quản lý bản nháp, xuất bản chương, duyệt bản quyền. | `Story` (Aggregate Root), `Chapter`, `Author` |
| **Reading Context** (Đọc truyện) | Độc giả tìm kiếm, đọc nội dung, lưu lịch sử đọc, đánh dấu trang (bookmark). | `Reader`, `ReadingHistory`, `Bookmark`, `CatalogStory` |
| **Ingestion Context** (Crawl truyện) | Lấy dữ liệu tự động từ các nguồn ngoài, chuẩn hóa dữ liệu về hệ thống. | `CrawlTarget` (Aggregate Root), `RawChapter`, `SourceConfig` |

---

## 2. Mô hình hóa Domain (Tactical DDD)

### Aggregates & Value Objects (`domain/`)

```python
# domain/authoring/entities.py
from dataclasses import dataclass, field
from enum import Enum
from typing import List
import uuid

class StoryStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    COMPLETED = "completed"

@dataclass(frozen=True)
class ChapterContent:
    """Value Object: Nội dung chương là bất biến khi truyền tải"""
    body: str
    word_count: int

    def __post_init__(self):
        if not self.body.strip():
            raise ValueError("Nội dung chương không được để trống")

class Story:
    """Aggregate Root quản lý vòng đời bộ truyện"""
    def __init__(self, title: str, author_id: str):
        self.id = str(uuid.uuid4())
        self.title = title
        self.author_id = author_id
        self.status = StoryStatus.DRAFT
        self.chapters: List['Chapter'] = []

    def add_chapter(self, title: str, content: ChapterContent) -> 'Chapter':
        order_number = len(self.chapters) + 1
        chapter = Chapter(
            story_id=self.id, 
            order_number=order_number, 
            title=title, 
            content=content
        )
        self.chapters.append(chapter)
        return chapter

class Chapter:
    """Entity thuộc Aggregate Story"""
    def __init__(self, story_id: str, order_number: int, title: str, content: ChapterContent):
        self.id = str(uuid.uuid4())
        self.story_id = story_id
        self.order_number = order_number
        self.title = title
        self.content = content

```

---

## 3. Cấu trúc thư mục chuẩn Clean Architecture

```text
src/
├── domain/                       # Core Business Logic (Zero dependencies)
│   ├── authoring/                # Entities, Value Objects, Domain Events
│   ├── reading/                  # Reading models, Bookmarks
│   └── ingestion/                # Crawl rules, Source definitions
│
├── application/                  # Use Cases & Interfaces
│   ├── authoring/                # UseCase: CreateStory, PublishChapter
│   ├── reading/                  # UseCase: GetChapterContent, RecordHistory
│   ├── ingestion/                # UseCase: RunCrawlJob, SyncExternalStory
│   └── interfaces/               # Abstract Repositories, Scraper Interfaces
│
├── infrastructure/               # External Implementations
│   ├── persistence/              # SQLAlchemy / MongoDB Repositories
│   ├── scrapers/                 # Playwright / BeautifulSoup Crawlers
│   ├── storage/                  # S3 / Local storage cho ảnh truyện
│   └── messaging/                # Celery / Redis Event Bus
│
└── presentation/                 # Driving Adapters
    ├── api/                      # FastAPI Endpoints (Web app, Mobile API)
    └── workers/                  # Celery Task Execution for Scrapers

```

---

## 4. Tách biệt Crawler qua Dependency Inversion

Động cơ crawl dữ liệu ở tầng **Infrastructure** sẽ cài đặt Interface từ tầng **Application**, giúp bạn dễ dàng thay thế công nghệ cào (Playwright, Scrapy, HTTPX) mà không ảnh hưởng đến logic đọc/viết.

### Application Layer (`application/interfaces/scraper.py`)

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class ScrapedChapterDTO:
    title: str
    content_raw: str
    chapter_number: int

class ExternalStoryScraper(ABC):
    @abstractmethod
    async def fetch_chapter(self, source_url: str) -> ScrapedChapterDTO:
        pass

```

### Application Use Case (`application/ingestion/use_cases.py`)

```python
from application.interfaces.scraper import ExternalStoryScraper
from domain.authoring.entities import Story, ChapterContent
from application.interfaces.repositories import StoryRepository

class IngestChapterUseCase:
    """Chuyển đổi dữ liệu thô từ Crawler thành Domain Model chuẩn"""
    def __init__(self, scraper: ExternalStoryScraper, story_repo: StoryRepository):
        self.scraper = scraper
        self.story_repo = story_repo

    async def execute(self, story_id: str, source_url: str):
        story = await self.story_repo.get_by_id(story_id)
        
        # Lấy dữ liệu thô qua Interface (không phụ thuộc vào thư viện scraper cụ thể)
        scraped_data = await self.scraper.fetch_chapter(source_url)
        
        # Đưa vào Domain Entity
        content = ChapterContent(
            body=scraped_data.content_raw, 
            word_count=len(scraped_data.content_raw.split())
        )
        story.add_chapter(title=scraped_data.title, content=content)
        
        await self.story_repo.save(story)

```

---

## 5. Giao tiếp giữa các Context bằng Domain Events

Khi **Ingestion Context** cào thành công một chương mới, thay vì trực tiếp gọi sang Reading Context, nó phát ra một `ChapterIngestedEvent`.

* **Reading Context** lắng nghe sự kiện này để cập nhật danh mục và gửi thông báo cho độc giả đang theo dõi.
* **Storage Engine** tự động tải các hình ảnh đính kèm (nếu là comic/manga) lên S3.