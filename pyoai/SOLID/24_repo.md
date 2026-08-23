# Buổi 24 — SQLite Repository Deep Dive

Hôm nay chúng ta xây **Persistence Layer** thật cho Story Crawler.

Mục tiêu không chỉ là viết:

```python
sqlite3.connect(...)
```

mà hiểu sâu:

```text
Domain
   ↑
Repository Interface
   ↑
SQLite Repository
   ↑
SQLite
```

và đặc biệt hiểu **Repository Pattern thực sự dùng để làm gì**.

---

# 1. Kiến trúc sau Buổi 24

```text
                         Presentation
                              │
                              ▼
                         Application
                              │
                              ▼
                    StoryRepository
                         Protocol
                              ▲
                              │
                    SQLiteStoryRepository
                              │
                              ▼
                           SQLite
```

Điểm quan trọng:

> `CrawlStory` không biết SQLite tồn tại.

---

# 2. Repository là gì?

Repository là abstraction cho phép Application nói:

> "Tôi muốn lưu/lấy Story."

Application không cần quan tâm:

```text
SQLite
PostgreSQL
MongoDB
Memory
Remote API
```

Ví dụ:

```python
repository.save(story)
```

Application chỉ quan tâm **what**.

Infrastructure quyết định **how**.

---

# 3. Repository Interface

Ta đã có:

```python
from typing import Protocol

from .story import Story
from .value_objects import Url


class StoryRepository(Protocol):

    def save(self, story: Story) -> None:
        ...

    def get_by_url(
        self,
        url: Url,
    ) -> Story | None:
        ...
```

Nhưng với project thực tế, chúng ta sẽ mở rộng.

---

# 4. Repository Contract

Ta muốn:

```text
save()
get_by_url()
exists()
delete()
```

Có thể:

```python
class StoryRepository(Protocol):

    def save(
        self,
        story: Story,
    ) -> None:
        ...

    def get_by_url(
        self,
        url: Url,
    ) -> Story | None:
        ...

    def exists(
        self,
        url: Url,
    ) -> bool:
        ...

    def delete(
        self,
        url: Url,
    ) -> None:
        ...
```

Nhưng đừng vội thêm 20 method.

> Interface chỉ nên chứa những capability mà client thực sự cần.

Đây chính là **ISP**.

---

# 5. Database Schema

Ta tạo:

```sql
CREATE TABLE IF NOT EXISTS stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE
);
```

Database có:

```text
id
title
source
url
```

Domain có:

```text
Story
├── title
├── Source
└── Url
```

Hai representation khác nhau.

---

# 6. Mapping

Đây là boundary:

```text
Domain Story
     │
     ▼
 Mapper
     │
     ▼
SQLite Row
```

Ví dụ:

```python
def story_to_row(story: Story):
    return (
        story.title,
        story.source.name,
        story.url.value,
    )
```

Và ngược lại:

```python
def row_to_story(row):
    return Story(
        title=row["title"],
        source=Source(row["source"]),
        url=Url(row["url"]),
    )
```

---

# 7. Đừng để Mapping nằm trong Domain

Sai:

```python
@dataclass
class Story:

    ...

    def to_sqlite_row(self):
        ...
```

Vì lúc này:

```text
Domain
 ↓
SQLite
```

Domain biết Infrastructure.

Không tốt.

---

# 8. SQLite Repository

```python
import sqlite3

from story_crawler.domain.repository import StoryRepository
from story_crawler.domain.story import Story
from story_crawler.domain.value_objects import (
    Source,
    Url,
)


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
                story.source.name,
                story.url.value,
            ),
        )

        self.connection.commit()
```

---

# 9. `get_by_url()`

```python
def get_by_url(
    self,
    url: Url,
) -> Story | None:

    cursor = self.connection.execute(
        """
        SELECT title, source, url
        FROM stories
        WHERE url = ?
        """,
        (url.value,),
    )

    row = cursor.fetchone()

    if row is None:
        return None

    return Story(
        title=row["title"],
        source=Source(row["source"]),
        url=Url(row["url"]),
    )
```

Nhớ cấu hình:

```python
connection.row_factory = sqlite3.Row
```

---

# 10. Tạo Connection Factory

Không nên để:

```python
SQLiteStoryRepository(
    sqlite3.connect(...)
)
```

rải khắp code.

Tạo:

```python
def create_connection(
    database: str,
) -> sqlite3.Connection:

    connection = sqlite3.connect(
        database
    )

    connection.row_factory = (
        sqlite3.Row
    )

    return connection
```

Composition Root:

```python
connection = create_connection(
    "stories.db"
)

repository = SQLiteStoryRepository(
    connection
)
```

---

# 11. Database Initialization

Tách:

```text
database/
├── connection.py
└── schema.py
```

`schema.py`:

```python
SCHEMA = """
CREATE TABLE IF NOT EXISTS stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE
);
"""
```

Initializer:

```python
def initialize_database(connection):

    connection.executescript(
        SCHEMA
    )

    connection.commit()
```

---

# 12. Vì sao tách Database Initialization?

Đây là một responsibility khác:

```text
SQLiteStoryRepository
→ persistence behavior

DatabaseInitializer
→ database setup
```

Không nên:

```python
class SQLiteStoryRepository:

    def __init__(self):
        create_table()
```

vì constructor sẽ có side effect.

---

# 13. Repository Constructor

Một repository tốt:

```python
repository = SQLiteStoryRepository(
    connection
)
```

Không:

```python
repository = SQLiteStoryRepository(
    "stories.db"
)
```

rồi bên trong:

```python
sqlite3.connect(...)
```

Tại sao?

Vì Dependency Injection.

```text
Composition Root
      │
      ▼
Connection
      │
      ▼
Repository
```

---

# 14. Test Repository

Repository cần test với SQLite thật.

Nhưng:

> Không dùng database production.

Ta dùng:

```python
connection = sqlite3.connect(
    ":memory:"
)
```

SQLite tạo database trong RAM.

---

# 15. Repository Test

```python
def test_save_and_get_story():

    connection = sqlite3.connect(
        ":memory:"
    )

    connection.row_factory = sqlite3.Row

    initialize_database(
        connection
    )

    repository = SQLiteStoryRepository(
        connection
    )

    story = Story(
        title="Test Story",
        source=Source("source_a"),
        url=Url(
            "https://source-a.com/story/1"
        ),
    )

    repository.save(story)

    result = repository.get_by_url(
        story.url
    )

    assert result == story
```

Đây là **integration test**.

---

# 16. Unit Test vs Integration Test

### Unit Test

```text
CrawlStory
FakeRepository
FakeCrawler
```

Không SQLite.

Nhanh.

### Integration Test

```text
SQLiteStoryRepository
SQLite
```

Kiểm tra:

```text
SQL
mapping
schema
constraint
transaction
```

Hai loại test đều cần.

---

# 17. Tại sao không Mock SQLite?

Không nên:

```python
connection = Mock()
```

rồi test SQL.

Bạn sẽ test:

> "Mock của tôi trả đúng dữ liệu"

chứ không test:

> "SQL của tôi có đúng không?"

Repository là nơi SQL thật sự quan trọng.

Do đó:

```text
SQLite Repository
→ SQLite in-memory
```

thường tốt hơn mock.

---

# 18. `exists()`

Ta có thể:

```python
def exists(
    self,
    url: Url,
) -> bool:

    cursor = self.connection.execute(
        """
        SELECT 1
        FROM stories
        WHERE url = ?
        LIMIT 1
        """,
        (url.value,),
    )

    return cursor.fetchone() is not None
```

---

# 19. `delete()`

```python
def delete(
    self,
    url: Url,
) -> None:

    self.connection.execute(
        """
        DELETE FROM stories
        WHERE url = ?
        """,
        (url.value,),
    )

    self.connection.commit()
```

Nhưng có một câu hỏi:

> `delete()` có thực sự là domain operation không?

Đây là câu hỏi quan trọng.

Không phải repository method nào cũng nên tồn tại chỉ vì CRUD có nó.

---

# 20. Repository không nhất thiết CRUD

Một Repository tốt có thể là:

```python
story_repository.find_by_url(url)
```

hoặc:

```python
story_repository.find_pending_stories()
```

thay vì:

```text
insert()
update()
delete()
```

DDD Repository nên phản ánh **domain/application needs**, không nhất thiết mirror database.

---

# 21. Ví dụ rất thực tế

Crawler cần:

> "Tìm Story chưa crawl."

Thay vì:

```python
repository.select(
    where="status = pending"
)
```

Ta có:

```python
repository.find_pending()
```

Application hiểu nghiệp vụ.

Infrastructure quyết định SQL:

```sql
SELECT ...
FROM stories
WHERE status = 'pending'
```

---

# 22. Repository không phải DAO?

Hai khái niệm thường bị nhầm.

### DAO

Thường tập trung vào persistence:

```text
insert
select
update
delete
```

### Repository

Thường thể hiện domain/application abstraction:

```text
get_story
find_pending
save_story
```

Trong Python project nhỏ, ranh giới có thể mờ.

Nhưng khi học Clean Architecture/DDD, nên hiểu distinction này.

---

# 23. Transaction

Đây là phần rất quan trọng.

Giả sử:

```text
save Story
save Chapter 1
save Chapter 2
save Chapter 3
```

Nếu:

```text
Chapter 3
```

lỗi thì chuyện gì xảy ra?

Không muốn:

```text
Story     ✓
Chapter1  ✓
Chapter2  ✓
Chapter3  ✗
```

Nếu business operation yêu cầu atomicity:

```text
Story + Chapters
```

phải cùng transaction.

---

# 24. Transaction boundary

Đây là lý do chúng ta sắp cần:

> **Unit of Work**

Thay vì:

```python
repository.save(story)
repository.save_chapter(chapter1)
repository.save_chapter(chapter2)
```

mỗi method tự:

```python
commit()
```

thì khó kiểm soát transaction.

---

# 25. Một vấn đề trong Repository hiện tại

Chúng ta đang:

```python
def save(...):
    ...
    connection.commit()
```

Điều này đơn giản.

Nhưng với operation phức tạp:

```text
save story
save chapters
update crawler state
```

thì mỗi repository tự commit là không tốt.

---

# 26. Tạm thời chưa cần Unit of Work

Ở Buổi 24, project chỉ có:

```text
Story
```

nên:

```python
save()
→ commit()
```

chấp nhận được.

Nhưng khi thêm:

```text
Chapter
CrawlerJob
CrawlState
```

ta sẽ thiết kế:

```text
UnitOfWork
```

ở một buổi sau.

Đừng over-engineer quá sớm.

---

# 27. Upsert

Crawler rất hay crawl lại.

Ta có:

```text
URL UNIQUE
```

Nếu:

```python
repository.save(story)
```

hai lần:

```text
INSERT
INSERT
```

lần thứ hai sẽ lỗi.

Có thể cần:

```sql
INSERT INTO stories (...)
VALUES (...)
ON CONFLICT(url)
DO UPDATE SET
    title = excluded.title,
    source = excluded.source;
```

---

# 28. Nhưng Upsert có phải Domain Rule?

Không.

```text
UPSERT
```

là persistence strategy.

Domain chỉ nói:

> Story có URL này.

SQLite quyết định:

> Tôi sẽ dùng `ON CONFLICT`.

---

# 29. Canonical URL

Buổi 21 ta đã nói:

```text
https://source-a.com/story/1
https://source-a.com/story/1/
```

có thể là cùng Story.

Repository không nên tự quyết định business identity.

Tốt hơn:

```text
Domain
 ↓
Canonical Url
 ↓
Repository
```

Như vậy:

```python
Url(
    "https://source-a.com/story/1/"
)
```

có thể normalize ngay khi tạo Value Object.

---

# 30. Mapping hoàn chỉnh

Ta có thể tách mapper:

```text
infrastructure/persistence/
├── sqlite_repository.py
└── mappers.py
```

`mappers.py`:

```python
def story_to_row(
    story: Story,
) -> tuple[str, str, str]:

    return (
        story.title,
        story.source.name,
        story.url.value,
    )
```

và:

```python
def row_to_story(
    row,
) -> Story:

    return Story(
        title=row["title"],
        source=Source(
            row["source"]
        ),
        url=Url(
            row["url"]
        ),
    )
```

---

# 31. Có nhất thiết phải có Mapper class?

Không.

Đừng viết:

```python
class StoryMapperFactoryBuilder:
    ...
```

chỉ để map 3 fields.

Python rất phù hợp với:

```python
def story_to_row(...):
    ...
```

Đây là một ví dụ SOLID quan trọng:

> **SOLID không có nghĩa là tạo thật nhiều class.**

---

# 32. Repository hoàn chỉnh

Phiên bản hiện tại:

```python
class SQLiteStoryRepository:

    def __init__(
        self,
        connection,
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
            ON CONFLICT(url)
            DO UPDATE SET
                title = excluded.title,
                source = excluded.source
            """,
            (
                story.title,
                story.source.name,
                story.url.value,
            ),
        )

        self.connection.commit()

    def get_by_url(
        self,
        url: Url,
    ) -> Story | None:

        cursor = self.connection.execute(
            """
            SELECT
                title,
                source,
                url
            FROM stories
            WHERE url = ?
            """,
            (url.value,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return Story(
            title=row["title"],
            source=Source(
                row["source"]
            ),
            url=Url(
                row["url"]
            ),
        )
```

Đây đã là một Infrastructure component khá sạch.

---

# 33. Dependency Direction

Nhìn toàn bộ:

```text
                    Domain
                      ▲
                      │
               Repository Port
                      ▲
                      │
              SQLite Repository
                      │
                      ▼
                   SQLite
```

Application:

```text
Application
    │
    ▼
Repository Protocol
```

Infrastructure:

```text
SQLiteRepository
    │
    ▼
Repository Protocol
```

Đây chính là **Dependency Inversion**.

---

# 34. Nếu đổi SQLite → PostgreSQL?

Tạo:

```python
class PostgresStoryRepository:
    ...
```

Implement cùng contract.

Application:

```python
class CrawlStory:

    def __init__(
        self,
        repository: StoryRepository,
    ):
        ...
```

không đổi.

Composition Root đổi:

```python
repository = PostgresStoryRepository(...)
```

Đây là:

```text
DIP
+
OCP
+
LSP
```

hoạt động cùng nhau.

---

# 35. Nếu đổi SQLite → Fake?

Trong unit test:

```python
use_case = CrawlStory(
    registry=fake_registry,
    repository=FakeRepository(),
)
```

Không SQLite.

Đây là lý do abstraction có giá trị.

---

# 36. Một điều không nên làm

Đừng tạo:

```python
class DatabaseManager:
    def save_story(...)
    def get_story(...)
    def save_chapter(...)
    def save_user(...)
    def send_notification(...)
    def crawl(...)
```

Rồi inject:

```python
DatabaseManager
```

vào mọi nơi.

Đó là **God Object**.

Thay vào đó:

```text
StoryRepository
ChapterRepository
UserRepository
```

và các service riêng.

---

# 37. Repository Interface cũng cần ISP

Nếu `CrawlStory` chỉ cần:

```python
save()
```

thì interface:

```python
class StoryWriter(Protocol):

    def save(self, story):
        ...
```

có thể tốt hơn:

```python
class StoryRepository(Protocol):

    def save(...)
    def delete(...)
    def get_by_url(...)
    def find_pending(...)
    def search(...)
    def count(...)
    def ...
```

Đây chính là **ISP**.

Interface nên phục vụ **client**, không phục vụ implementation.

---

# 38. Bài tập thực hành

## Bài 1

Tạo:

```text
infrastructure/persistence/
├── connection.py
├── schema.py
├── mappers.py
└── sqlite_story_repository.py
```

---

## Bài 2

Implement:

```python
save()
get_by_url()
exists()
```

---

## Bài 3

Viết test bằng:

```python
sqlite3.connect(":memory:")
```

Test:

```text
save
 ↓
get_by_url
 ↓
Story
```

---

## Bài 4

Test `exists()`:

```python
assert repository.exists(
    story.url
)

assert not repository.exists(
    Url("https://example.com/no")
)
```

---

## Bài 5 — Upsert

Lưu:

```text
Story A
title = "Old"
```

sau đó lưu:

```text
Story A
title = "New"
```

Kiểm tra database chỉ có **một record** và title là:

```text
New
```

---

# 39. Challenge Architecture

Tạo:

```python
class FakeStoryRepository:
    ...
```

Sau đó chạy:

```text
CrawlStory
    ↓
SourceACrawler
    ↓
Story
    ↓
FakeRepository
```

Không:

```text
SQLite
```

Sau đó thay:

```text
FakeRepository
```

bằng:

```text
SQLiteStoryRepository
```

mà **không sửa `CrawlStory`**.

Nếu làm được:

```text
Application
    ↓
Repository Protocol
    ↑
 ┌──┴──────────────┐
Fake             SQLite
```

thì bạn đã nắm được bản chất của **DIP + Repository Pattern**.

---

# 40. Architecture sau Buổi 24

```text
                    ┌─────────────┐
                    │     CLI     │
                    └──────┬──────┘
                           ↓
                    ┌─────────────┐
                    │  CrawlStory │
                    └──────┬──────┘
                           ↓
              ┌────────────┴────────────┐
              ↓                         ↓
       CrawlerRegistry          StoryRepository
              ↓                         ↑
        ┌─────┴─────┐                   │
        ↓           ↓                   │
     Source A    Source B               │
        │                               │
        ↓                               │
   HttpClient                           │
        │                               │
        ↓                               │
   StoryParser                           │
                                        │
                                        │
                              SQLiteStoryRepository
                                        │
                                        ↓
                                     SQLite
```

---

# 41. Một insight rất quan trọng

Bạn có thể nhìn toàn bộ hệ thống thành **3 loại dependency**:

### Business dependency

```text
CrawlStory
    ↓
StoryCrawler
StoryRepository
```

### Technical dependency

```text
Requests
BeautifulSoup
SQLite
```

### Composition dependency

```text
composition.py
```

Composition Root là nơi **ghép business abstraction với technical implementation**.

Đây chính là một trong những tư duy quan trọng nhất của Clean Architecture.

---

## Buổi 25 — CLI + Dependency Injection

Buổi tiếp theo chúng ta sẽ hoàn thiện tầng ngoài:

```text
CLI
 ↓
Composition Root
 ↓
Application
 ↓
Domain
```

và đi sâu vào một câu hỏi rất quan trọng:

> **Tại sao CLI không nên tự tạo `SQLiteRepository`, `SourceACrawler`, `RequestsHttpClient`?**

Sau đó chúng ta sẽ thiết kế:

```text
main()
   ↓
build_application()
   ↓
Dependency Injection
   ↓
Use Case
```

và cuối buổi có một CLI hoàn chỉnh:

```bash
story-crawler crawl URL
story-crawler story URL
story-crawler list
```

để toàn bộ architecture bắt đầu trở thành một **ứng dụng thực sự**, thay vì chỉ là các class rời rạc.
