# SOLID Deep Dive — Buổi 8

# ISP Deep Dive — Role Interface, Capability Interface & Architecture

Buổi 7 chúng ta đã nắm được ý tưởng chính của ISP:

> **Client không nên bị buộc phụ thuộc vào những interface mà nó không sử dụng.**

Buổi 8 sẽ đi sâu vào **cách áp dụng ISP trong kiến trúc Python thực tế**, đặc biệt với:

* `Protocol`
* Dependency Injection
* Repository
* Service
* Clean Architecture
* Plugin Architecture
* Mock/Fake
* Adapter
* Facade
* Refactoring fat interface
* Crawler framework

---

# 1. ISP ở mức sâu hơn: Interface thuộc về Client

Một sai lầm rất phổ biến khi thiết kế interface:

```text
Implementation
      ↓
hãy tạo interface cho implementation
```

Ví dụ bạn có:

```python
class SqliteStoryRepository:

    def get(self, id):
        ...

    def save(self, story):
        ...

    def delete(self, id):
        ...

    def search(self, keyword):
        ...
```

Sau đó tạo:

```python
class StoryRepository(Protocol):

    def get(self, id):
        ...

    def save(self, story):
        ...

    def delete(self, id):
        ...

    def search(self, keyword):
        ...
```

Cách này nhìn có vẻ hợp lý.

Nhưng có một vấn đề:

> Interface đang phản ánh **implementation**, không phải **client**.

---

# 2. Hãy đảo ngược cách suy nghĩ

Thay vì:

```text
Repository
    ↓
Interface
    ↓
Client
```

hãy nghĩ:

```text
Client
    ↓
Client cần gì?
    ↓
Interface
    ↓
Implementation
```

Ví dụ:

```text
GetStoryUseCase
        ↓
cần get()
        ↓
StoryReader
        ↓
SqliteStoryRepository
```

Không cần:

```text
save()
delete()
search()
export()
```

---

# 3. Role Interface

Một interface nên đại diện cho:

> **Một role mà object đóng đối với client.**

Ví dụ:

```python
class StoryReader(Protocol):

    def get(self, story_id: int) -> Story | None:
        ...
```

Một repository có thể đóng nhiều role:

```text
SqliteStoryRepository
        │
        ├── StoryReader
        ├── StoryWriter
        └── StorySearcher
```

Đây là:

> **Role Interface**

---

# 4. Một object có thể có nhiều role

Ví dụ:

```python
class SqliteStoryRepository:

    def get(self, story_id):
        ...

    def save(self, story):
        ...

    def delete(self, story_id):
        ...

    def search(self, keyword):
        ...
```

Object này có thể được nhìn theo nhiều cách:

```text
             SqliteStoryRepository
              /        |        \
             /         |         \
            ↓          ↓          ↓
      StoryReader StoryWriter StorySearcher
```

Client A:

```python
class GetStoryUseCase:

    def __init__(self, reader: StoryReader):
        self.reader = reader
```

Client B:

```python
class CreateStoryUseCase:

    def __init__(self, writer: StoryWriter):
        self.writer = writer
```

Client C:

```python
class SearchStoryUseCase:

    def __init__(self, searcher: StorySearcher):
        self.searcher = searcher
```

Đây chính là ISP + DIP.

---

# 5. Role Interface khác Implementation Interface

### Implementation-oriented

```python
class SqliteRepositoryInterface:
    def get(...)
    def save(...)
    def delete(...)
    def search(...)
```

Nó nói:

> "SqliteRepository có những gì?"

### Client-oriented

```python
class StoryReader:
    def get(...)
```

Nó nói:

> "GetStoryUseCase cần gì?"

Hai cách này khác nhau về tư duy kiến trúc.

---

# 6. Capability Interface

Một khái niệm gần với Role Interface là:

> **Capability Interface**

Ví dụ:

```text
StoryReader
    ↓
có capability đọc story

StoryWriter
    ↓
có capability ghi story

StorySearcher
    ↓
có capability search
```

Đây là cách thiết kế rất phù hợp với Python.

---

# 7. Capability Composition

Một object có thể cung cấp nhiều capability:

```text
             StorySource
                  │
       ┌──────────┼──────────┐
       ↓          ↓          ↓
    Reader     Searcher    Lister
```

Không cần một interface khổng lồ:

```python
class StorySource:
    ...
```

---

# 8. `Protocol` là công cụ tuyệt vời cho ISP

Ví dụ:

```python
from typing import Protocol


class StoryReader(Protocol):

    def get_story(self, story_id: int) -> Story | None:
        ...
```

Một implementation:

```python
class SqliteStoryRepository:

    def get_story(self, story_id: int):
        ...
```

Không cần:

```python
class SqliteStoryRepository(StoryReader):
```

Structural typing cho phép:

```text
Có method phù hợp
       ↓
thỏa Protocol
```

---

# 9. Nhưng đừng nhầm Protocol với LSP

Ví dụ:

```python
class StoryReader(Protocol):

    def get_story(self, story_id: int) -> Story | None:
        ...
```

Implementation:

```python
class BrokenReader:

    def get_story(self, story_id):
        raise RuntimeError()
```

Shape:

```text
✔ method
✔ parameter
✔ return annotation
```

nhưng behavior:

```text
✘ contract
```

Do đó:

```text
ISP
    ↓
interface nhỏ

LSP
    ↓
implementation phải tuân contract
```

Hai principle bổ sung cho nhau.

---

# 10. ISP + Dependency Injection

Đây là một trong những lợi ích lớn nhất.

Không tốt:

```python
class GetStoryUseCase:

    def __init__(self, repository: StoryRepository):
        self.repository = repository
```

Nếu `StoryRepository` có:

```text
20 methods
```

thì use case đang phụ thuộc vào abstraction lớn.

Tốt:

```python
class GetStoryUseCase:

    def __init__(self, reader: StoryReader):
        self.reader = reader
```

Dependency graph:

```text
Before:

GetStoryUseCase
      ↓
HugeRepository
```

After:

```text
GetStoryUseCase
      ↓
StoryReader
```

---

# 11. ISP + Testability

Giả sử:

```python
class StoryReader(Protocol):

    def get_story(self, story_id):
        ...
```

Fake:

```python
class FakeStoryReader:

    def __init__(self, stories):
        self.stories = stories

    def get_story(self, story_id):
        return self.stories.get(story_id)
```

Test:

```python
def test_get_story():

    reader = FakeStoryReader({
        1: Story(id=1, title="Python")
    })

    use_case = GetStoryUseCase(reader)

    story = use_case.execute(1)

    assert story.title == "Python"
```

Fake cực kỳ đơn giản.

---

# 12. Nếu Interface quá lớn

Ví dụ:

```python
class Repository(Protocol):

    def get(self): ...
    def save(self): ...
    def delete(self): ...
    def search(self): ...
    def export(self): ...
    def backup(self): ...
    def migrate(self): ...
```

Fake phải làm:

```python
class FakeRepository:

    def get(self): ...
    def save(self): ...
    def delete(self): ...
    def search(self): ...
    def export(self): ...
    def backup(self): ...
    def migrate(self): ...
```

Dù test chỉ cần:

```text
get()
```

Đây là:

> **Interface pollution**

---

# 13. Interface Pollution

Một dependency bị "polluted" khi nó expose rất nhiều thứ mà client không cần.

Ví dụ:

```text
GetStoryUseCase
        ↓
Repository
        ├── get       ← cần
        ├── save      ← không cần
        ├── delete    ← không cần
        ├── search    ← không cần
        ├── export    ← không cần
        └── backup    ← không cần
```

ISP muốn:

```text
GetStoryUseCase
        ↓
StoryReader
        └── get
```

---

# 14. ISP + Clean Architecture

Đây là nơi ISP trở nên rất mạnh.

Ví dụ:

```text
┌─────────────────────────────┐
│       Presentation          │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│       Application           │
│                             │
│ GetStoryUseCase             │
│ SearchStoryUseCase          │
│ CreateStoryUseCase          │
└──────────────┬──────────────┘
               ↓
          Interfaces
               ↓
┌─────────────────────────────┐
│       Infrastructure        │
│                             │
│ SQLite                      │
│ PostgreSQL                  │
│ HTTP                        │
│ Redis                       │
└─────────────────────────────┘
```

Mỗi use case chỉ phụ thuộc interface nhỏ.

---

# 15. Ví dụ Clean Architecture

Domain:

```python
class Story:
    ...
```

Application:

```python
class StoryReader(Protocol):

    def get(self, story_id: int) -> Story | None:
        ...
```

Use case:

```python
class GetStoryUseCase:

    def __init__(self, reader: StoryReader):
        self.reader = reader

    def execute(self, story_id: int):
        return self.reader.get(story_id)
```

Infrastructure:

```python
class SqliteStoryRepository:

    def get(self, story_id: int):
        ...
```

Dependency:

```text
GetStoryUseCase
       ↓
StoryReader
       ↑
SqliteStoryRepository
```

Rất sạch.

---

# 16. ISP + Repository Pattern

Một repository thường bị thiết kế quá lớn:

```python
class StoryRepository(Protocol):

    def get(self): ...
    def save(self): ...
    def update(self): ...
    def delete(self): ...
    def search(self): ...
    def count(self): ...
```

Không phải lúc nào đây cũng là vấn đề.

Nếu toàn bộ application thực sự sử dụng tất cả:

```text
get
save
update
delete
search
count
```

thì interface vẫn cohesive.

ISP không phải:

> "Repository phải có interface nhỏ."

Mà:

> "Client không nên phụ thuộc vào những operation nó không cần."

---

# 17. Khi nào KHÔNG cần tách?

Ví dụ:

```python
class StoryReader(Protocol):

    def get_story(self, id):
        ...

    def get_chapter(self, id):
        ...

    def get_chapters(self, story_id):
        ...
```

Có thể giữ nguyên nếu tất cả đều là:

```text
Reading capability
```

Không cần tách thành:

```text
StoryGetter
ChapterGetter
ChapterLister
```

chỉ để giảm số method.

---

# 18. Over-Segregation

Đây là mặt trái của ISP.

Nếu bạn tách thành:

```text
IStoryGetter
IStorySaver
IStoryDeleter
IStorySearcher
IStoryCounter
IStoryExporter
```

thì dependency injection có thể biến thành:

```python
class StoryService:

    def __init__(
        self,
        getter,
        saver,
        deleter,
        searcher,
        counter,
        exporter,
    ):
        ...
```

Architecture trở nên:

```text
interface explosion
```

Đây cũng là design smell.

---

# 19. Quy tắc thực tế

Một interface nên được tách khi:

```text
Methods có lý do sử dụng khác nhau
```

hoặc:

```text
Clients sử dụng các nhóm method khác nhau
```

Không nên tách chỉ vì:

```text
Interface có 5 method
```

hay:

```text
Interface có 10 method
```

Số lượng method không phải tiêu chí chính.

---

# 20. Role Interface và ISP

Hãy xem:

```python
class StoryRepository:

    def get(self):
        ...

    def save(self):
        ...

    def delete(self):
        ...
```

Roles:

```text
Reader
Writer
Deleter
```

Nhưng:

```text
save + delete
```

có thể cùng thuộc:

```text
Writer
```

Ví dụ:

```python
class StoryWriter(Protocol):

    def save(self, story):
        ...

    def delete(self, story_id):
        ...
```

Đây là thiết kế dựa trên **role**, không dựa trên số lượng method.

---

# 21. Facade vs ISP

Hai khái niệm này rất dễ nhầm.

### Facade

Giấu một hệ thống phức tạp:

```text
Complex subsystem
      ↓
   Facade
      ↓
Simple API
```

### ISP

Giảm dependency của client:

```text
Client
  ↓
Small interface
```

Facade có thể có API nhỏ nhưng vẫn là một interface lớn đối với một client khác.

ISP tập trung vào:

> **Ai đang phụ thuộc vào interface?**

---

# 22. Ví dụ Facade

```python
class StoryFacade:

    def get_story(self):
        ...

    def search(self):
        ...

    def export(self):
        ...
```

Facade có thể rất hữu ích.

Không cần phải tách nó chỉ vì có nhiều method.

Nhưng nếu:

```text
GetStoryUseCase
```

chỉ cần:

```text
get_story()
```

thì use case không nhất thiết phải phụ thuộc vào toàn bộ `StoryFacade`.

Có thể tạo:

```python
class StoryReader(Protocol):

    def get_story(self, id):
        ...
```

Facade vẫn tồn tại.

---

# 23. Adapter vs ISP

Adapter:

```text
Old API
   ↓
Adapter
   ↓
Expected interface
```

Ví dụ:

```python
class LegacyStorage:

    def fetch_data(self, key):
        ...
```

Application muốn:

```python
class Reader(Protocol):

    def read(self, key):
        ...
```

Adapter:

```python
class LegacyStorageAdapter:

    def __init__(self, storage):
        self.storage = storage

    def read(self, key):
        return self.storage.fetch_data(key)
```

ISP xác định:

```text
Reader
```

là interface client cần.

Adapter thực hiện interface đó.

---

# 24. ISP + Adapter cực kỳ đẹp

Architecture:

```text
Application
    ↓
StoryReader
    ↑
    │
Adapter
    ↑
Legacy API
```

Application không biết:

```text
LegacyStorage
```

và cũng không bị ép dùng:

```text
fetch_data()
save_data()
delete_data()
backup_data()
```

---

# 25. ISP + Plugin Architecture

Đây là phần quan trọng với hệ thống crawler.

Không tạo:

```python
class CrawlerPlugin(Protocol):

    def crawl(self):
        ...

    def search(self):
        ...

    def login(self):
        ...

    def download_image(self):
        ...

    def parse_comments(self):
        ...

    def parse_author(self):
        ...
```

Thay vào đó:

```python
class StoryCrawler(Protocol):

    def crawl_story(self, url):
        ...
```

```python
class StorySearcher(Protocol):

    def search(self, keyword):
        ...
```

```python
class Authenticator(Protocol):

    def login(self):
        ...
```

```python
class ImageDownloader(Protocol):

    def download(self, url):
        ...
```

---

# 26. Một plugin có thể compose capability

Ví dụ:

```python
class SiteAPlugin:

    def crawl_story(self, url):
        ...

    def search(self, keyword):
        ...
```

Nó cung cấp:

```text
StoryCrawler
StorySearcher
```

SiteB:

```python
class SiteBPlugin:

    def crawl_story(self, url):
        ...
```

chỉ cung cấp:

```text
StoryCrawler
```

Application có thể kiểm tra capability một cách có chủ đích.

---

# 27. Nhưng tránh `hasattr()` khắp nơi

Không nên:

```python
if hasattr(plugin, "search"):
    plugin.search(...)
```

ở khắp application.

Tốt hơn là thiết kế registry/capability system:

```text
Plugin
   ↓
Capabilities
   ↓
Registry
```

Ví dụ:

```python
class PluginCapabilities:

    def __init__(
        self,
        crawler=None,
        searcher=None,
    ):
        self.crawler = crawler
        self.searcher = searcher
```

Hoặc đơn giản hơn, registry lưu những interface mà plugin cung cấp.

---

# 28. ISP + Event-driven architecture

Ví dụ event bus:

```python
class EventPublisher(Protocol):

    def publish(self, event):
        ...
```

Consumer không cần:

```text
subscribe
unsubscribe
publish
replay
clear
inspect
```

Nếu consumer chỉ publish:

```python
class OrderService:

    def __init__(self, publisher: EventPublisher):
        self.publisher = publisher
```

Dependency nhỏ.

---

# 29. ISP + Queue

Giả sử bạn xây queue server cho crawler.

Đừng inject một:

```python
class QueueManager:
    enqueue()
    dequeue()
    ack()
    retry()
    purge()
    stats()
    pause()
    resume()
```

vào worker nếu worker chỉ cần:

```python
class TaskConsumer(Protocol):

    def dequeue(self):
        ...

    def ack(self, task):
        ...
```

Producer:

```python
class TaskProducer(Protocol):

    def enqueue(self, task):
        ...
```

Monitor:

```python
class QueueMonitor(Protocol):

    def stats(self):
        ...
```

Rất phù hợp với ISP.

---

# 30. ISP + ThreadPool / ProcessPool

Ví dụ một service chỉ cần submit task:

```python
class TaskSubmitter(Protocol):

    def submit(self, fn, *args):
        ...
```

Không cần inject toàn bộ executor abstraction nếu client không dùng:

```text
shutdown
map
submit
future management
```

Một interface nhỏ giúp code dễ test hơn.

---

# 31. ISP + Python Standard Library

Một ví dụ rất tự nhiên:

```python
from typing import Protocol


class Writer(Protocol):

    def write(self, data: str) -> int:
        ...
```

Client:

```python
def write_report(writer: Writer):
    writer.write("Hello")
```

`writer` có thể là:

```text
TextIO
StringIO
File
Socket-like object
Fake
```

Client không cần biết toàn bộ API của `TextIO`.

Đây là tư duy duck typing + ISP.

---

# 32. ISP và Structural Typing

Python cho phép:

```python
class Writer(Protocol):

    def write(self, data: str) -> int:
        ...
```

Một class không liên quan:

```python
class Console:

    def write(self, data: str) -> int:
        print(data)
        return len(data)
```

vẫn có thể được sử dụng.

Không cần:

```python
class Console(Writer):
```

Điều này khuyến khích thiết kế interface theo:

```text
behavior
```

thay vì:

```text
inheritance hierarchy
```

---

# 33. Một nguyên tắc cực kỳ quan trọng

> **Interface nên nằm gần abstraction mà client sở hữu, không nhất thiết nằm gần implementation.**

Ví dụ:

```text
application/
    use_cases/
        get_story.py
        ports.py
```

Có thể:

```python
# application/ports.py

class StoryReader(Protocol):
    ...
```

Trong khi:

```text
infrastructure/
    sqlite/
        story_repository.py
```

implement nó.

---

# 34. Interface Ownership

Đây là tư duy quan trọng trong Clean Architecture.

Không nhất thiết:

```text
Infrastructure
    ↓
định nghĩa interface
    ↓
Application dùng
```

Thường tốt hơn:

```text
Application
    ↓
định nghĩa abstraction nó cần
    ↑
Infrastructure implement
```

Ví dụ:

```text
application
    ports.py
       ↓
StoryReader
       ↑
sqlite_repository.py
```

Điều này đồng thời hỗ trợ:

```text
ISP
+
DIP
+
Clean Architecture
```

---

# 35. Refactoring Fat Service

Giả sử:

```python
class StoryService:

    def get_story(self, id):
        ...

    def save_story(self, story):
        ...

    def delete_story(self, id):
        ...

    def search_story(self, keyword):
        ...

    def export_story(self, id):
        ...
```

Các client:

```text
GetStoryUseCase
    → get_story

CreateStoryUseCase
    → save_story

DeleteStoryUseCase
    → delete_story

SearchStoryUseCase
    → search_story

ExportStoryUseCase
    → export_story
```

Tạo role interfaces:

```python
class StoryReader(Protocol):

    def get_story(self, id):
        ...
```

```python
class StoryWriter(Protocol):

    def save_story(self, story):
        ...

    def delete_story(self, id):
        ...
```

```python
class StorySearcher(Protocol):

    def search_story(self, keyword):
        ...
```

```python
class StoryExporter(Protocol):

    def export_story(self, id):
        ...
```

---

# 36. Implementation vẫn có thể là một class

```python
class StoryService:

    def get_story(self, id):
        ...

    def save_story(self, story):
        ...

    def delete_story(self, id):
        ...

    def search_story(self, keyword):
        ...

    def export_story(self, id):
        ...
```

Không cần tách implementation thành 5 class.

Đây là điểm rất quan trọng:

```text
Interface segregation
        ≠
Class fragmentation
```

---

# 37. Architecture sau refactoring

```text
                         StoryService
                    ┌─────────┼─────────┐
                    │         │         │
                    ↓         ↓         ↓
               StoryReader Writer   Searcher
                    ↑         ↑         ↑
                    │         │         │
               GetUseCase CreateUseCase SearchUseCase
```

Implementation:

```text
StoryService
    ├── get_story()
    ├── save_story()
    ├── delete_story()
    ├── search_story()
    └── export_story()
```

Client nhìn thấy interface nhỏ.

Implementation vẫn có thể tập trung.

---

# 38. ISP và Testing Architecture

Một test:

```python
def test_get_story():
    reader = FakeReader(...)
```

Không cần:

```python
FakeRepository(
    database=...,
    cache=...,
    exporter=...,
    searcher=...,
)
```

Interface nhỏ giúp test:

```text
UseCase
   ↓
Tiny Fake
```

thay vì:

```text
UseCase
   ↓
Huge Mock
```

---

# 39. ISP và Mock vs Fake

Nếu interface nhỏ:

```python
class StoryReader(Protocol):

    def get(self, id):
        ...
```

thì Fake rất tự nhiên:

```python
class FakeStoryReader:

    def __init__(self, story):
        self.story = story

    def get(self, id):
        return self.story
```

Đôi khi còn tốt hơn `Mock`.

Vì fake thể hiện rõ behavior contract.

---

# 40. ISP Contract Test

Ta có:

```python
def story_reader_contract(reader):

    story = reader.get(1)

    assert story is not None
```

Sau đó:

```python
def test_sqlite_reader():
    story_reader_contract(
        SqliteStoryRepository(...)
    )
```

```python
def test_memory_reader():
    story_reader_contract(
        MemoryStoryRepository(...)
    )
```

Interface nhỏ giúp contract test tập trung hơn.

---

# 41. ISP và OCP

ISP cũng hỗ trợ OCP.

Ví dụ:

```text
StoryReader
   ↑
   ├── SQLite
   ├── PostgreSQL
   ├── Redis
   └── HTTP
```

Thêm implementation:

```text
MongoDB
```

không cần sửa client:

```text
GetStoryUseCase
```

Client chỉ biết:

```text
StoryReader
```

---

# 42. ISP + OCP + LSP

Ba principle kết hợp:

```text
ISP
 ↓
interface nhỏ
 ↓
OCP
 ↓
thêm implementation
 ↓
LSP
 ↓
implementation giữ contract
```

Ví dụ:

```text
StoryReader
   ↑
   ├── SQLiteReader
   ├── RedisReader
   └── HTTPReader
```

Tất cả:

```text
✔ implement capability
✔ giữ behavioral contract
```

---

# 43. ISP + DIP

Sau ISP:

```text
GetStoryUseCase
       ↓
StoryReader
```

DIP:

```text
Application
     ↓
Abstraction
     ↑
Infrastructure
```

Do đó hai principle thường xuất hiện cùng nhau.

---

# 44. Một công thức thiết kế rất hữu ích

Khi viết một class:

```python
class SomeUseCase:
```

hãy hỏi:

### Bước 1

Class này cần dependency nào?

### Bước 2

Dependency đó thực sự cần method nào?

### Bước 3

Những method đó thuộc capability nào?

### Bước 4

Tạo Protocol cho capability đó.

Ví dụ:

```text
Need:
    get_story()

Capability:
    StoryReader

Protocol:
    StoryReader
```

---

# 45. ISP trong hệ thống crawler của bạn

Một kiến trúc hợp lý có thể là:

```text
crawler/
│
├── ports/
│   ├── story_reader.py
│   ├── story_lister.py
│   ├── chapter_reader.py
│   ├── story_searcher.py
│   ├── image_downloader.py
│   └── authenticator.py
│
├── plugins/
│   ├── site_a/
│   ├── site_b/
│   └── site_c/
│
└── application/
    ├── crawl_story.py
    ├── search_story.py
    └── download_chapter.py
```

Application:

```text
CrawlStory
    ↓
StoryReader

SearchStory
    ↓
StorySearcher

DownloadChapter
    ↓
ChapterReader
```

Plugin:

```text
SiteA
 ├── StoryReader
 ├── StoryLister
 └── ChapterReader
```

SiteB:

```text
SiteB
 ├── StoryReader
 ├── StoryLister
 ├── ChapterReader
 └── StorySearcher
```

Đây là **capability-oriented plugin architecture**.

---

# 46. Một điều cần tránh

Đừng biến ISP thành:

```text
100 Protocol
```

cho một project nhỏ.

Ví dụ:

```text
StoryIdProvider
StoryTitleProvider
StoryChapterProvider
StoryMetadataProvider
StoryUrlProvider
...
```

Nếu chúng luôn đi cùng nhau, interface quá nhỏ sẽ tạo complexity.

Mục tiêu là:

```text
cohesion
+
low coupling
```

không phải:

```text
maximum fragmentation
```

---

# 47. Quy tắc vàng của ISP

Khi phân vân:

> **“Có nên tách interface này không?”**

hãy hỏi 4 câu:

### 1.

Có client nào chỉ dùng một phần interface không?

### 2.

Các implementation có bị ép implement capability không hỗ trợ không?

### 3.

Thay đổi một method có ảnh hưởng đến client không liên quan không?

### 4.

Fake/Mock có trở nên khó viết vì interface quá lớn không?

Nếu nhiều câu trả lời là **Có**:

→ xem xét ISP.

---

# 48. Bài tập Buổi 8 — Refactoring

Cho code:

```python
class Crawler(Protocol):

    def crawl_story(self, url):
        ...

    def crawl_chapters(self, story):
        ...

    def search(self, keyword):
        ...

    def login(self, username, password):
        ...

    def logout(self):
        ...

    def download_image(self, url):
        ...
```

Có:

```text
SiteA:
crawl_story
crawl_chapters

SiteB:
crawl_story
crawl_chapters
search

SiteC:
crawl_story
crawl_chapters
search
login
logout
download_image
```

### Yêu cầu

Thiết kế lại bằng:

```text
StoryCrawler
ChapterCrawler
StorySearcher
Authenticator
ImageDownloader
```

Sau đó giải thích:

* Client nào phụ thuộc interface nào?
* SiteA implement những interface nào?
* SiteB implement những interface nào?
* SiteC implement những interface nào?

---

# 49. Bài tập Buổi 8 — Repository Architecture

Thiết kế:

```text
StoryReader
StoryWriter
StorySearcher
```

Sau đó:

```python
class SqliteStoryRepository:
    ...
```

phải cung cấp cả ba capability.

Tạo:

```text
GetStoryUseCase
CreateStoryUseCase
SearchStoryUseCase
```

Mỗi use case chỉ được inject đúng interface nó cần.

Dependency graph phải có dạng:

```text
GetStoryUseCase
       ↓
StoryReader

CreateStoryUseCase
       ↓
StoryWriter

SearchStoryUseCase
       ↓
StorySearcher
```

---

# 50. Bài tập Buổi 8 — Testing

Viết:

```python
class FakeStoryReader:
    ...
```

và test:

```python
def test_get_story():
    ...
```

Không được tạo một:

```python
FakeStoryRepository
```

có hàng chục method.

Mục tiêu là chứng minh:

```text
ISP
 ↓
small interface
 ↓
small fake
 ↓
simple test
```

---

# 51. Bài tập nâng cao — Phát hiện Over-Segregation

Cho:

```python
class StoryReader(Protocol):

    def get_story(self, id):
        ...


class ChapterReader(Protocol):

    def get_chapter(self, id):
        ...


class MetadataReader(Protocol):

    def get_metadata(self, id):
        ...


class AuthorReader(Protocol):

    def get_author(self, id):
        ...
```

Use case:

```python
class ReadStoryUseCase:

    def __init__(
        self,
        story_reader,
        chapter_reader,
        metadata_reader,
        author_reader,
    ):
        ...
```

Câu hỏi:

> Đây có phải ISP tốt không?

Không được trả lời chỉ bằng:

> "Interface nhỏ nên tốt."

Hãy phân tích:

```text
cohesion
client needs
dependency count
change coupling
```

---

# 52. Tổng kết Buổi 8

ISP sâu hơn rất nhiều so với:

> “Chia interface lớn thành interface nhỏ.”

Bản chất của ISP là:

```text
                 Client
                    ↓
             What does it need?
                    ↓
              Role/Capability
                    ↓
              Small Protocol
                    ↓
             Implementation
```

Và một implementation có thể:

```text
               Implementation
              /       |       \
             ↓        ↓        ↓
         Reader    Writer   Searcher
```

Trong khi các client chỉ nhìn:

```text
Client A → Reader
Client B → Writer
Client C → Searcher
```

---

# 53. Toàn bộ SOLID đến hiện tại

```text
                    SOLID
                      │
       ┌──────────────┼───────────────┐
       ↓              ↓               ↓
      SRP            OCP             LSP
       │              │               │
       │              │               ↓
       │              │              ISP
       │              │               │
       └──────────────┴───────────────┤
                                      ↓
                                     DIP
```

Cụ thể:

```text
SRP
→ responsibility

OCP
→ extension

LSP
→ behavioral contract

ISP
→ client-specific interface

DIP
→ dependency direction
```

---

# 54. Roadmap

```text
✅ Buổi 1 — SOLID Foundation
✅ Buổi 2 — SRP
✅ Buổi 3 — SRP Deep Dive + Refactoring
✅ Buổi 4 — OCP
✅ Buổi 5 — LSP
✅ Buổi 6 — LSP Deep Dive
✅ Buổi 7 — ISP
✅ Buổi 8 — ISP Deep Dive

⬜ Buổi 9 — DIP
```

**Buổi 9 — DIP (Dependency Inversion Principle)** sẽ là phần rất quan trọng, vì chúng ta sẽ gom tất cả những gì đã học:

```text
SRP
 ↓
OCP
 ↓
LSP
 ↓
ISP
 ↓
DIP
 ↓
Clean Architecture
```

và đi sâu vào:

* High-level module vs Low-level module
* Dependency direction
* Abstraction
* Dependency Injection vs Dependency Inversion
* Constructor Injection
* Function Injection
* Protocol-based DI
* Composition Root
* Dependency graph
* Infrastructure boundary
* Repository + DIP
* Service + DIP
* Plugin + DIP
* Crawler architecture + DIP
* **Tự xây một architecture hoàn chỉnh bằng Python**.
