# Buổi 20 — Mini Project: Story Crawler System

Hôm nay chúng ta bắt đầu **project thực tế** để tổng hợp toàn bộ SOLID.

Mục tiêu không phải viết crawler thật ngay, mà là xây **architecture đúng trước**, sau đó mới cắm HTTP, parser, SQLite, CLI và các source.

---

# 1. Mục tiêu project

Ta sẽ xây:

```text
Story Crawler System
```

Có khả năng:

```text
CLI
 ↓
Use Case
 ↓
Crawler Interface
 ↓
Crawler Plugin
 ├── Source A
 ├── Source B
 └── Source C

Use Case
 ↓
Repository Interface
 ↓
SQLite Repository
```

Sau này có thể mở rộng:

```text
Source D
Source E
PostgreSQL
REST API
PySide6
Web UI
```

mà không phải phá Domain/Application.

---

# 2. Architecture mục tiêu

```text
                         ┌───────────────┐
                         │      CLI      │
                         └───────┬───────┘
                                 │
                                 ↓
                         ┌───────────────┐
                         │   Use Case    │
                         │               │
                         │  CrawlStory   │
                         └───────┬───────┘
                                 │
                    ┌────────────┴────────────┐
                    ↓                         ↓
             Crawler Interface         Repository Interface
                    ↓                         ↓
          ┌─────────┴─────────┐               ↓
          ↓                   ↓             SQLite
      Source A             Source B
```

---

# 3. Nguyên tắc quan trọng

Chúng ta sẽ áp dụng:

```text
SRP
OCP
LSP
ISP
DIP
```

nhưng không cố nhét SOLID vào mọi chỗ.

Nguyên tắc:

> **Architecture phục vụ changeability, không phải phục vụ SOLID.**

---

# 4. Tạo project bằng `src` layout

Cấu trúc:

```text
story-crawler/
│
├── pyproject.toml
│
├── src/
│   └── story_crawler/
│       │
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── story.py
│       │   ├── chapter.py
│       │   ├── crawler.py
│       │   └── repository.py
│       │
│       ├── application/
│       │   ├── __init__.py
│       │   └── crawl_story.py
│       │
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   │
│       │   ├── crawler/
│       │   │   ├── __init__.py
│       │   │   ├── source_a.py
│       │   │   └── source_b.py
│       │   │
│       │   ├── http/
│       │   │   ├── __init__.py
│       │   │   └── requests_client.py
│       │   │
│       │   └── persistence/
│       │       ├── __init__.py
│       │       └── sqlite_repository.py
│       │
│       ├── presentation/
│       │   ├── __init__.py
│       │   └── cli.py
│       │
│       └── composition.py
│
└── tests/
```

Đây chính là architecture chúng ta vừa học ở Buổi 19.

---

# 5. Domain Layer

Domain là trung tâm.

Nó **không được biết**:

```text
requests
sqlite3
BeautifulSoup
Typer
PySide6
```

Domain chỉ biết business concepts.

---

# 6. `Story`

```python
# src/story_crawler/domain/story.py

from dataclasses import dataclass


@dataclass
class Story:
    title: str
    source: str
    url: str
```

Đây là Domain Entity đơn giản.

---

# 7. `Chapter`

```python
# src/story_crawler/domain/chapter.py

from dataclasses import dataclass


@dataclass
class Chapter:
    title: str
    url: str
    content: str
```

Sau này chúng ta có thể làm sâu hơn:

```text
Chapter
 ├── identity
 ├── number
 ├── title
 ├── content
 └── status
```

Nhưng hiện tại chưa cần.

---

# 8. Crawler Interface

Ta dùng `Protocol`.

```python
# src/story_crawler/domain/crawler.py

from typing import Protocol

from .story import Story


class StoryCrawler(Protocol):

    def can_handle(
        self,
        url: str,
    ) -> bool:
        ...

    def crawl(
        self,
        url: str,
    ) -> Story:
        ...
```

Đây là **Port** của Domain/Application.

---

# 9. Tại sao dùng Protocol?

Ta không cần:

```python
class SourceACrawler(StoryCrawler):
    ...
```

Chỉ cần object có đúng behavior:

```python
can_handle()
crawl()
```

là được.

Đây chính là:

```text
Duck Typing
+
Structural Typing
+
DIP
```

---

# 10. Repository Interface

Tạo:

```python
# src/story_crawler/domain/repository.py

from typing import Protocol

from .story import Story


class StoryRepository(Protocol):

    def save(
        self,
        story: Story,
    ) -> None:
        ...

    def get_by_url(
        self,
        url: str,
    ) -> Story | None:
        ...
```

Domain/Application chỉ biết abstraction này.

---

# 11. Crawler Registry

Registry có nhiệm vụ:

> Tìm crawler phù hợp với URL.

```python
# src/story_crawler/application/crawler_registry.py

from story_crawler.domain.crawler import StoryCrawler


class CrawlerRegistry:

    def __init__(
        self,
        crawlers: list[StoryCrawler],
    ):
        self._crawlers = crawlers

    def find(
        self,
        url: str,
    ) -> StoryCrawler:

        for crawler in self._crawlers:

            if crawler.can_handle(url):
                return crawler

        raise LookupError(
            f"No crawler found for: {url}"
        )
```

Tôi cố tình đặt Registry trong `application` thay vì Domain.

Vì Registry là cơ chế orchestration/selection, không phải business entity.

---

# 12. Use Case `CrawlStory`

```python
# src/story_crawler/application/crawl_story.py

from story_crawler.domain.repository import (
    StoryRepository,
)
from story_crawler.domain.story import Story

from .crawler_registry import CrawlerRegistry


class CrawlStory:

    def __init__(
        self,
        registry: CrawlerRegistry,
        repository: StoryRepository,
    ):
        self.registry = registry
        self.repository = repository

    def execute(
        self,
        url: str,
    ) -> Story:

        crawler = self.registry.find(url)

        story = crawler.crawl(url)

        self.repository.save(story)

        return story
```

Đây là phần quan trọng nhất của Application Layer.

---

# 13. Nhìn Use Case

```text
CrawlStory
│
├── tìm crawler
│
├── crawl
│
├── save
│
└── return Story
```

Nó không biết:

```text
requests
BeautifulSoup
sqlite3
SourceA
SourceB
```

Đây chính là **DIP**.

---

# 14. Source A

Bây giờ mới đi vào Infrastructure.

```python
# src/story_crawler/infrastructure/crawler/source_a.py

from urllib.parse import urlparse

from story_crawler.domain.story import Story


class SourceACrawler:

    def can_handle(
        self,
        url: str,
    ) -> bool:

        host = urlparse(url).netloc

        return host == "source-a.com"

    def crawl(
        self,
        url: str,
    ) -> Story:

        return Story(
            title="Demo Story A",
            source="source_a",
            url=url,
        )
```

Chưa HTTP thật.

Tại sao?

Vì:

> **Chúng ta đang xây architecture trước.**

---

# 15. Source B

```python
# src/story_crawler/infrastructure/crawler/source_b.py

from urllib.parse import urlparse

from story_crawler.domain.story import Story


class SourceBCrawler:

    def can_handle(
        self,
        url: str,
    ) -> bool:

        host = urlparse(url).netloc

        return host == "source-b.com"

    def crawl(
        self,
        url: str,
    ) -> Story:

        return Story(
            title="Demo Story B",
            source="source_b",
            url=url,
        )
```

---

# 16. Chúng ta vừa đạt OCP

Thêm Source C:

```python
class SourceCCrawler:

    def can_handle(self, url):
        ...

    def crawl(self, url):
        ...
```

Không cần sửa:

```text
CrawlStory
CrawlerRegistry
Story
StoryRepository
CLI
```

Đây là OCP.

---

# 17. SQLite Repository

Bây giờ Infrastructure implement Repository.

```python
# src/story_crawler/infrastructure/persistence/sqlite_repository.py

import sqlite3

from story_crawler.domain.story import Story


class SQLiteStoryRepository:

    def __init__(
        self,
        connection: sqlite3.Connection,
    ):
        self.connection = connection

    def save(
        self,
        story: Story,
    ) -> None:

        self.connection.execute(
            """
            INSERT INTO stories (
                title,
                source,
                url
            )
            VALUES (?, ?, ?)
            """,
            (
                story.title,
                story.source,
                story.url,
            ),
        )

        self.connection.commit()

    def get_by_url(
        self,
        url: str,
    ) -> Story | None:

        cursor = self.connection.execute(
            """
            SELECT title, source, url
            FROM stories
            WHERE url = ?
            """,
            (url,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return Story(
            title=row[0],
            source=row[1],
            url=row[2],
        )
```

---

# 18. Tạo database

Ta cần schema.

```sql
CREATE TABLE IF NOT EXISTS stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE
);
```

Điểm quan trọng:

```text
Domain
   ✗
sqlite3
```

nhưng:

```text
SQLiteRepository
   ↓
Domain Story
```

được.

---

# 19. HTTP Client

Tạo abstraction:

```python
# domain/http.py

from typing import Protocol


class HttpClient(Protocol):

    def get(
        self,
        url: str,
    ) -> str:
        ...
```

Nhưng tôi muốn bạn chú ý:

**Không nhất thiết HTTP phải thuộc Domain.**

Trong project lớn, ta có thể đặt `HttpClient` ở Application/Infrastructure ports tùy dependency structure.

Đừng biến Clean Architecture thành luật cứng nhắc về folder.

Quan trọng nhất vẫn là:

> Dependency direction.

---

# 20. Requests implementation

```python
# infrastructure/http/requests_client.py

import requests


class RequestsHttpClient:

    def get(
        self,
        url: str,
    ) -> str:

        response = requests.get(
            url,
            timeout=10,
        )

        response.raise_for_status()

        return response.text
```

---

# 21. Composition Root

Đây là nơi quan trọng nhất của project.

```python
# src/story_crawler/composition.py

import sqlite3

from story_crawler.application.crawl_story import (
    CrawlStory,
)
from story_crawler.application.crawler_registry import (
    CrawlerRegistry,
)
from story_crawler.infrastructure.crawler.source_a import (
    SourceACrawler,
)
from story_crawler.infrastructure.crawler.source_b import (
    SourceBCrawler,
)
from story_crawler.infrastructure.persistence.sqlite_repository import (
    SQLiteStoryRepository,
)


def build_application():

    connection = sqlite3.connect(
        "stories.db"
    )

    repository = SQLiteStoryRepository(
        connection
    )

    crawlers = [
        SourceACrawler(),
        SourceBCrawler(),
    ]

    registry = CrawlerRegistry(
        crawlers
    )

    return CrawlStory(
        registry=registry,
        repository=repository,
    )
```

---

# 22. Tại sao `composition.py` quan trọng?

Application cần:

```text
CrawlerRegistry
Repository
```

nhưng không biết implementation.

Composition Root quyết định:

```text
CrawlerRegistry
    ↓
SourceA
SourceB

Repository
    ↓
SQLite
```

Đây là:

> **Dependency Injection tại Composition Root.**

---

# 23. CLI

Ta có thể dùng `argparse` hoặc `Typer`.

Hôm nay dùng `argparse` để tập trung vào architecture.

```python
# src/story_crawler/presentation/cli.py

import argparse

from story_crawler.composition import (
    build_application,
)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "url",
    )

    args = parser.parse_args()

    use_case = build_application()

    story = use_case.execute(
        args.url
    )

    print(
        f"Title: {story.title}"
    )

    print(
        f"Source: {story.source}"
    )


if __name__ == "__main__":
    main()
```

---

# 24. Luồng chạy

Ví dụ:

```bash
python -m story_crawler.presentation.cli \
    https://source-a.com/story/123
```

Luồng:

```text
CLI
 │
 ↓
build_application()
 │
 ├── SQLiteRepository
 ├── SourceACrawler
 ├── SourceBCrawler
 └── CrawlerRegistry
 │
 ↓
CrawlStory
 │
 ↓
Registry.find(url)
 │
 ↓
SourceACrawler
 │
 ↓
Story
 │
 ↓
SQLiteRepository.save()
```

---

# 25. SOLID nằm ở đâu?

### SRP

```text
CLI
Use Case
Registry
Crawler
Repository
```

mỗi component có responsibility khác nhau.

### OCP

Thêm:

```text
Source C
```

không sửa Use Case.

### LSP

`SourceACrawler`, `SourceBCrawler` đều phải tuân:

```text
StoryCrawler contract
```

### ISP

Sau này tách:

```text
StoryCrawler
ChapterCrawler
Authenticator
Notifier
```

### DIP

```text
CrawlStory
   ↓
abstraction
   ↑
Infrastructure
```

---

# 26. Nhưng project này vẫn chưa hoàn chỉnh

Hiện tại:

```text
SourceA
  ↓
return "Demo Story A"
```

Chưa có:

```text
HTTP
HTML parser
Story parser
Chapter parser
Cleaning
Retry
Rate limit
Logging
Database migration
Testing
```

**Đừng thêm tất cả ngay.**

Architecture tốt được xây theo từng vertical slice.

---

# 27. Vertical Slice đầu tiên

Ta chọn:

```text
crawl story metadata
```

Luồng:

```text
URL
 ↓
Source A
 ↓
HTTP
 ↓
Parser
 ↓
Story
 ↓
Repository
```

Sau khi chạy được mới thêm:

```text
crawl chapters
```

rồi:

```text
crawl all chapters
```

rồi:

```text
resume
retry
parallel
```

---

# 28. Test trước khi thêm HTTP

Đây là điều tôi muốn bạn chú ý.

Ta có thể test toàn bộ Application ngay bây giờ.

```python
class FakeCrawler:

    def can_handle(self, url):
        return True

    def crawl(self, url):

        return Story(
            title="Test Story",
            source="fake",
            url=url,
        )
```

Fake repository:

```python
class FakeRepository:

    def __init__(self):
        self.items = []

    def save(self, story):
        self.items.append(story)

    def get_by_url(self, url):
        for story in self.items:
            if story.url == url:
                return story

        return None
```

---

# 29. Test Use Case

```python
def test_crawl_story():

    repository = FakeRepository()

    registry = CrawlerRegistry(
        [FakeCrawler()]
    )

    use_case = CrawlStory(
        registry,
        repository,
    )

    story = use_case.execute(
        "https://example.com/story/1"
    )

    assert story.title == "Test Story"

    assert (
        repository.items[0]
        == story
    )
```

Không cần:

```text
Internet
SQLite
requests
BeautifulSoup
```

Đây là architecture **testable by design**.

---

# 30. Một điểm rất quan trọng: Dependency Graph

Hãy nhìn dependency:

```text
presentation
      ↓
application
      ↓
domain
```

Infrastructure:

```text
infrastructure
      ↓
domain
```

Composition:

```text
composition
 ↓
mọi implementation
```

Không phải:

```text
domain
 ↓
infrastructure
```

---

# 31. Folder không quyết định Architecture

Ví dụ:

```text
domain/
application/
infrastructure/
```

không tự động biến project thành Clean Architecture.

Bạn có thể có folder đẹp:

```text
domain/
```

nhưng bên trong:

```python
import sqlite3
import requests
```

thì architecture vẫn sai.

**Dependency mới là thứ quyết định architecture.**

---

# 32. Một nguyên tắc vàng

> **Inner layer không được biết outer layer.**

Ví dụ:

```text
Domain
```

không biết:

```text
SQLite
HTTP
CLI
```

Application không biết:

```text
SourceA
SourceB
```

Infrastructure biết Domain.

Presentation biết Application.

---

# 33. Từ đây project sẽ phát triển như thế nào?

### Giai đoạn 1

```text
Story
Crawler
Repository
Use Case
SQLite
CLI
```

### Giai đoạn 2

```text
HTTP Client
Parser
Source A
Source B
```

### Giai đoạn 3

```text
Chapter
ChapterRepository
CrawlChapter
```

### Giai đoạn 4

```text
Crawler Plugin
Dynamic Registration
```

### Giai đoạn 5

```text
Retry
Rate Limit
Timeout
Logging
```

### Giai đoạn 6

```text
Async Crawler
Worker
Queue
```

Đây sẽ kết nối rất tự nhiên với những phần Python bạn đã học về `asyncio`, thread/process và queue.

---

# 34. Bài tập Buổi 20

Tôi muốn bạn **tự code**, không copy toàn bộ.

### Bài 1

Tạo:

```text
domain/story.py
```

với:

```python
@dataclass
class Story:
    title: str
    source: str
    url: str
```

---

### Bài 2

Tạo:

```text
domain/crawler.py
```

và định nghĩa:

```python
class StoryCrawler(Protocol):
    ...
```

---

### Bài 3

Tạo:

```text
application/crawler_registry.py
```

Implement:

```python
registry.find(url)
```

---

### Bài 4

Tạo:

```text
application/crawl_story.py
```

Implement:

```python
use_case.execute(url)
```

---

### Bài 5

Tạo:

```text
infrastructure/crawler/source_a.py
infrastructure/crawler/source_b.py
```

Hai crawler phải xử lý URL khác nhau.

---

### Bài 6

Tạo:

```text
FakeCrawler
FakeRepository
```

và viết test cho:

```python
CrawlStory.execute()
```

**Test này không được sử dụng Internet và SQLite.**

---

# 35. Challenge — quan trọng nhất

Sau khi hoàn thành, hãy thêm:

```text
SourceCCrawler
```

và kiểm tra:

> Bạn có phải sửa `CrawlStory` không?

Nếu câu trả lời là:

```text
Không.
```

thì bạn đã thực sự áp dụng OCP.

Sau đó thay:

```text
SQLiteStoryRepository
```

bằng:

```text
MemoryStoryRepository
```

mà không sửa Use Case.

Nếu làm được cả hai, bạn đã bắt đầu **thực sự tư duy theo SOLID**, thay vì chỉ học thuộc 5 chữ cái.

---

## Roadmap tiếp theo

Buổi 20 hôm nay mới dựng **skeleton architecture**. Bước tiếp theo nên đi theo thứ tự:

```text
Buổi 20
Architecture Skeleton
       ↓
Buổi 21
Domain Model Deep Dive
       ↓
Buổi 22
Crawler Port + Plugin
       ↓
Buổi 23
HTTP Client + Parser
       ↓
Buổi 24
SQLite Repository
       ↓
Buổi 25
CLI + Dependency Injection
       ↓
Buổi 26
Testing Architecture
       ↓
Buổi 27
Async Crawler
       ↓
Buổi 28
Queue + Worker
```

Điểm quan trọng nhất của project này là **không xây `CrawlerManager` mới dưới một cái tên khác**. Mỗi lần thêm chức năng, chúng ta sẽ kiểm tra **responsibility, dependency direction và blast radius** trước khi viết code.
