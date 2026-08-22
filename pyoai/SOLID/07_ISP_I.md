# SOLID Deep Dive — Buổi 7

# Interface Segregation Principle — ISP

Hôm nay chúng ta học chữ **I**:

> **Interface Segregation Principle**

Đây là principle liên kết rất chặt với **LSP** mà chúng ta vừa học.

Câu kinh điển:

> **Clients should not be forced to depend on interfaces they do not use.**

Hiểu đơn giản:

> **Đừng bắt một client phụ thuộc vào những method mà nó không cần.**

---

# 1. Vấn đề ISP giải quyết

Hãy bắt đầu bằng một interface quá lớn:

```python
from abc import ABC, abstractmethod


class Machine(ABC):

    @abstractmethod
    def print(self, document):
        ...

    @abstractmethod
    def scan(self, document):
        ...

    @abstractmethod
    def fax(self, document):
        ...
```

Một máy đa chức năng:

```python
class MultiFunctionPrinter(Machine):

    def print(self, document):
        ...

    def scan(self, document):
        ...

    def fax(self, document):
        ...
```

Không vấn đề.

Nhưng máy in đơn giản:

```python
class SimplePrinter(Machine):

    def print(self, document):
        ...

    def scan(self, document):
        raise NotImplementedError

    def fax(self, document):
        raise NotImplementedError
```

Đây là dấu hiệu rất rõ:

```text
Machine
 ├── print()
 ├── scan()
 └── fax()

SimplePrinter
 └── chỉ cần print()
```

`SimplePrinter` đang bị ép phụ thuộc vào:

```text
scan()
fax()
```

mà nó không cần.

→ **ISP violation.**

---

# 2. ISP không chỉ dành cho interface

Trong Python, từ "interface" không nhất thiết phải hiểu là:

```python
class Something(ABC):
```

ISP áp dụng cho:

* ABC
* Protocol
* abstract class
* API
* service
* module
* package
* dependency
* class public methods

Ví dụ:

```python
class UserService:

    def create_user(self):
        ...

    def delete_user(self):
        ...

    def send_email(self):
        ...

    def generate_report(self):
        ...

    def export_csv(self):
        ...
```

Nếu một client chỉ cần:

```python
create_user()
```

nhưng phải phụ thuộc cả `UserService`, abstraction có thể quá lớn.

---

# 3. “Interface” thực chất là gì?

Một cách hiểu sâu hơn:

> **Interface là tập hợp những capability mà một client có thể sử dụng.**

Ví dụ:

```text
Printer
    ↓
print()
```

là một capability.

```text
Scanner
    ↓
scan()
```

là một capability khác.

```text
Fax
    ↓
fax()
```

là capability khác nữa.

Thay vì:

```text
Machine
 ├── print
 ├── scan
 └── fax
```

ta có:

```text
Printable
    ↓
print()

Scannable
    ↓
scan()

Faxable
    ↓
fax()
```

---

# 4. ISP và “fat interface”

Một interface quá lớn thường được gọi là:

> **Fat Interface**

Ví dụ:

```python
class Repository(Protocol):

    def get(self, id):
        ...

    def save(self, entity):
        ...

    def delete(self, id):
        ...

    def search(self, query):
        ...

    def bulk_insert(self, entities):
        ...

    def export(self):
        ...

    def backup(self):
        ...
```

Có thể có client:

```python
class UserReader:

    def __init__(self, repository):
        self.repository = repository

    def get_user(self, user_id):
        return self.repository.get(user_id)
```

Client này thực chất chỉ cần:

```text
get()
```

Nhưng dependency type lại là:

```text
Repository
```

với hàng chục capability khác.

Đây là dấu hiệu cần xem xét ISP.

---

# 5. ISP không nói “mỗi interface chỉ có một method”

Đây là hiểu nhầm phổ biến.

ISP **không phải**:

> Một interface chỉ được có một method.

Ví dụ:

```python
class UserReader(Protocol):

    def get(self, id):
        ...

    def exists(self, id):
        ...
```

Hoàn toàn hợp lý nếu một nhóm client thực sự cần cả:

```text
get()
exists()
```

ISP hỏi:

> **Các method này có thuộc cùng một capability/cohesive contract không?**

chứ không hỏi:

> Có bao nhiêu method?

---

# 6. Cohesion

Đây là khái niệm quan trọng khi thiết kế interface.

Ví dụ:

```python
class UserReader(Protocol):

    def get(self, id):
        ...

    def exists(self, id):
        ...

    def list(self):
        ...
```

Ba method đều liên quan đến:

```text
User reading
```

→ cohesive.

Trong khi:

```python
class UserEverythingService:

    def get(self):
        ...

    def save(self):
        ...

    def delete(self):
        ...

    def send_email(self):
        ...

    def generate_pdf(self):
        ...

    def crawl_avatar(self):
        ...
```

→ cohesion thấp.

---

# 7. ISP và Client

ISP thực sự tập trung vào **client**.

Ví dụ:

```python
class ReportService:

    def __init__(self, exporter):
        self.exporter = exporter
```

Nếu `exporter` là:

```python
class Exporter(Protocol):

    def export_json(self):
        ...

    def export_csv(self):
        ...

    def export_xml(self):
        ...

    def export_pdf(self):
        ...
```

nhưng `ReportService` chỉ dùng:

```python
exporter.export_pdf()
```

thì client chỉ cần:

```python
class PdfExporter(Protocol):

    def export_pdf(self):
        ...
```

Từ:

```text
Exporter
```

thành:

```text
PdfExporter
```

---

# 8. ISP không nhất thiết yêu cầu thay đổi implementation

Điều này rất quan trọng.

Ví dụ:

```python
class ExportService:
    def export_pdf(self):
        ...

    def export_csv(self):
        ...
```

Một object vẫn có thể implement cả hai.

Ta chỉ thay đổi **abstraction mà client phụ thuộc vào**.

Ví dụ:

```python
class PdfExporter(Protocol):

    def export_pdf(self):
        ...


class CsvExporter(Protocol):

    def export_csv(self):
        ...
```

Implementation:

```python
class Exporter:

    def export_pdf(self):
        ...

    def export_csv(self):
        ...
```

Object này có thể thỏa cả hai Protocol.

---

# 9. Python `Protocol` rất phù hợp với ISP

Đây là một trong những điểm Python mạnh.

```python
from typing import Protocol


class Reader(Protocol):

    def read(self, path: str) -> str:
        ...
```

Writer:

```python
class Writer(Protocol):

    def write(self, path: str, data: str) -> None:
        ...
```

Một class:

```python
class FileManager:

    def read(self, path):
        ...

    def write(self, path, data):
        ...
```

có thể thỏa:

```text
Reader
Writer
```

mà không cần inheritance.

Client đọc:

```python
class DocumentLoader:

    def __init__(self, reader: Reader):
        self.reader = reader
```

Client ghi:

```python
class DocumentSaver:

    def __init__(self, writer: Writer):
        self.writer = writer
```

Dependency rất nhỏ.

---

# 10. ISP + LSP

Đây là mối liên hệ từ Buổi 6.

Interface lớn:

```text
Machine
 ├── print
 ├── scan
 └── fax
```

SimplePrinter:

```text
print ✔
scan ✘
fax ✘
```

Có hai vấn đề:

### ISP

`SimplePrinter` bị ép phụ thuộc capability không cần.

### LSP

`SimplePrinter` không thể thực sự thay `Machine`.

Do đó:

```text
ISP violation
       ↓
có thể dẫn đến
       ↓
LSP violation
```

---

# 11. Refactor bằng Interface Segregation

Thay:

```python
class Machine(Protocol):

    def print(self, document):
        ...

    def scan(self, document):
        ...

    def fax(self, document):
        ...
```

bằng:

```python
class Printer(Protocol):

    def print(self, document):
        ...


class Scanner(Protocol):

    def scan(self, document):
        ...


class Fax(Protocol):

    def fax(self, document):
        ...
```

Simple printer:

```python
class SimplePrinter:

    def print(self, document):
        print(document)
```

Multi-function:

```python
class MultiFunctionPrinter:

    def print(self, document):
        ...

    def scan(self, document):
        ...

    def fax(self, document):
        ...
```

Bây giờ:

```text
SimplePrinter
    ↓
Printer

MultiFunctionPrinter
    ↓
Printer
Scanner
Fax
```

Đẹp hơn rất nhiều.

---

# 12. ISP không phải “tách class càng nhiều càng tốt”

Đừng refactor kiểu:

```python
class UserGetter:
    def get(self):
        ...


class UserExistenceChecker:
    def exists(self):
        ...


class UserLister:
    def list(self):
        ...
```

rồi application có:

```python
class UserService:

    def __init__(
        self,
        getter,
        existence_checker,
        lister,
    ):
        ...
```

Nếu tất cả client luôn cần:

```text
get
exists
list
```

thì việc tách quá nhỏ làm architecture phức tạp không cần thiết.

Đây là:

> **Over-segregation**

ISP không nói:

> "Càng nhỏ càng tốt."

Nó nói:

> **Interface nên phù hợp với nhu cầu của client.**

---

# 13. Một heuristic tốt

Khi thiết kế interface, hỏi:

> **Ai là client của interface này?**

Sau đó:

```text
Client A
    ↓
needs methods 1, 2

Client B
    ↓
needs methods 3, 4

Client C
    ↓
needs methods 1, 2, 5
```

Nếu interface hiện tại:

```text
1,2,3,4,5
```

thì có thể cần segregation.

---

# 14. Ví dụ Repository

Giả sử:

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

Use case đọc:

```python
class GetStoryUseCase:

    def __init__(self, repository: StoryRepository):
        self.repository = repository
```

Nhưng nó chỉ dùng:

```python
repository.get(id)
```

Ta có thể tách:

```python
class StoryReader(Protocol):

    def get(self, id):
        ...
```

Write:

```python
class StoryWriter(Protocol):

    def save(self, story):
        ...

    def delete(self, id):
        ...
```

Search:

```python
class StorySearcher(Protocol):

    def search(self, keyword):
        ...
```

---

# 15. Application layer lúc này rất đẹp

```python
class GetStoryUseCase:

    def __init__(self, reader: StoryReader):
        self.reader = reader

    def execute(self, story_id):
        return self.reader.get(story_id)
```

Create:

```python
class CreateStoryUseCase:

    def __init__(self, writer: StoryWriter):
        self.writer = writer

    def execute(self, story):
        self.writer.save(story)
```

Search:

```python
class SearchStoryUseCase:

    def __init__(self, searcher: StorySearcher):
        self.searcher = searcher

    def execute(self, keyword):
        return self.searcher.search(keyword)
```

Mỗi use case chỉ biết capability nó cần.

Đây là ISP rất đẹp.

---

# 16. Nhưng SQLite Repository vẫn có thể là một class

Ta hoàn toàn có thể có:

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

Class này có nhiều method.

Không sao.

Bởi vì:

```text
Implementation
```

và:

```text
Client-facing interface
```

là hai vấn đề khác nhau.

Một implementation có thể implement nhiều interface nhỏ.

---

# 17. Đây là điểm cực kỳ quan trọng

Ta có:

```text
             SqliteStoryRepository
             /       |        \
            /        |         \
           ↓         ↓          ↓
      StoryReader StoryWriter StorySearcher
           ↑         ↑          ↑
           │         │          │
       UseCase A  UseCase B  UseCase C
```

`SqliteStoryRepository` vẫn là một class.

Nhưng application không cần phụ thuộc vào toàn bộ class.

Đây là một trong những lý do `Protocol` cực kỳ hữu ích trong Python.

---

# 18. ISP và Dependency Injection

ISP giúp Dependency Injection trở nên tốt hơn.

Không tốt:

```python
class StoryUseCase:

    def __init__(self, repository: HugeRepository):
        self.repository = repository
```

Client bị phụ thuộc vào:

```text
HugeRepository
```

Tốt hơn:

```python
class StoryUseCase:

    def __init__(self, reader: StoryReader):
        self.reader = reader
```

Dependency trở thành:

```text
HugeRepository
       ↓
StoryReader
```

nhỏ hơn.

---

# 19. ISP và DIP

Bạn có thể thấy chúng đang kết nối:

```text
ISP
 ↓
interface nhỏ
 ↓
DIP
 ↓
client phụ thuộc abstraction
```

Ví dụ:

```python
class GetStoryUseCase:

    def __init__(
        self,
        reader: StoryReader,
    ):
        self.reader = reader
```

Use case:

```text
không phụ thuộc SQLite
không phụ thuộc PostgreSQL
không phụ thuộc Redis
```

mà phụ thuộc:

```text
StoryReader
```

Đây chính là nền tảng cho Buổi 9 — **DIP**.

---

# 20. ISP và Mock Testing

Một lợi ích cực lớn của interface nhỏ:

```python
class StoryReader(Protocol):

    def get(self, id):
        ...
```

Test:

```python
class FakeStoryReader:

    def get(self, id):
        return Story(
            id=id,
            title="Test"
        )
```

Use case:

```python
reader = FakeStoryReader()

use_case = GetStoryUseCase(reader)
```

Mock rất đơn giản.

Nếu interface có:

```text
30 methods
```

fake implementation sẽ rất khó chịu.

ISP giúp:

```text
Small interface
     ↓
Small fake
     ↓
Easy testing
```

---

# 21. ISP và Mock Hell

Một dấu hiệu architecture có vấn đề:

```python
mock_repository.get.return_value = ...
mock_repository.save.return_value = ...
mock_repository.delete.return_value = ...
mock_repository.search.return_value = ...
mock_repository.export.return_value = ...
mock_repository.backup.return_value = ...
```

nhưng test chỉ cần:

```python
get()
```

Có thể abstraction đang quá lớn.

Sau ISP:

```python
reader = FakeStoryReader()
```

đơn giản hơn rất nhiều.

---

# 22. ISP trong Crawler Architecture

Đây là phần liên quan trực tiếp đến project crawler của bạn.

Không nên tạo một plugin interface khổng lồ:

```python
class CrawlerPlugin(Protocol):

    def can_handle(self, url):
        ...

    def get_story_list(self):
        ...

    def get_story(self):
        ...

    def get_chapter_list(self):
        ...

    def get_chapter(self):
        ...

    def search(self):
        ...

    def download_image(self):
        ...

    def login(self):
        ...

    def logout(self):
        ...
```

Website A có thể:

```text
✔ story
✔ chapter
✘ search
✘ login
✘ download_image
```

Nếu ép:

```python
class SiteAPlugin(CrawlerPlugin):
```

ta sẽ có:

```python
def search(self):
    raise NotImplementedError
```

Đây là smell.

---

# 23. Segregate Crawler Capabilities

Có thể thiết kế:

```python
class StoryLister(Protocol):

    def list_stories(self):
        ...
```

```python
class StoryReader(Protocol):

    def get_story(self, story_id):
        ...
```

```python
class ChapterReader(Protocol):

    def get_chapter(self, chapter_id):
        ...
```

```python
class StorySearcher(Protocol):

    def search(self, keyword):
        ...
```

```python
class ImageDownloader(Protocol):

    def download_image(self, url):
        ...
```

Một plugin chỉ implement capability nó hỗ trợ.

---

# 24. Plugin trở nên composable

Ví dụ:

```python
class SiteAPlugin:

    def list_stories(self):
        ...

    def get_story(self, story_id):
        ...

    def get_chapter(self, chapter_id):
        ...
```

Object này thỏa:

```text
StoryLister
StoryReader
ChapterReader
```

Nhưng không thỏa:

```text
StorySearcher
ImageDownloader
```

Không sao.

---

# 25. Application có thể yêu cầu đúng capability

Ví dụ:

```python
class SearchStoriesUseCase:

    def __init__(
        self,
        searcher: StorySearcher,
    ):
        self.searcher = searcher
```

Không phải:

```python
CrawlerPlugin
```

Search use case chỉ yêu cầu:

```text
StorySearcher
```

Đây chính là ISP.

---

# 26. Capability-based Design

Đây là cách tư duy rất mạnh:

Thay vì hỏi:

> “Object này thuộc loại nào?”

hãy hỏi:

> **“Object này có capability nào?”**

Ví dụ:

```text
SiteAPlugin
    │
    ├── ListStories
    ├── ReadStory
    └── ReadChapter
```

SiteB:

```text
SiteBPlugin
    │
    ├── ListStories
    ├── ReadStory
    ├── ReadChapter
    └── SearchStory
```

Đây là một design rất tự nhiên cho plugin architecture.

---

# 27. ISP và Duck Typing

Python có một lợi thế:

```python
class StoryReader(Protocol):

    def get_story(self, id):
        ...
```

Một object chỉ cần có:

```python
def get_story(self, id):
    ...
```

là đủ.

Không cần:

```python
class SiteAPlugin(StoryReader):
```

Điều này làm ISP cực kỳ tự nhiên.

---

# 28. ISP không có nghĩa client không thể dùng nhiều interface

Ví dụ:

```python
class CrawlUseCase:

    def __init__(
        self,
        reader: StoryReader,
        chapter_reader: ChapterReader,
    ):
        self.reader = reader
        self.chapter_reader = chapter_reader
```

Client cần hai capability.

Hoàn toàn hợp lệ.

ISP không yêu cầu:

```text
1 client
↓
1 interface
```

Mà là:

> **Client chỉ phụ thuộc vào những capability mà nó thực sự cần.**

---

# 29. ISP và Interface Composition

Có thể tạo interface lớn từ những interface nhỏ:

```python
class StoryReader(Protocol):

    def get_story(self, id):
        ...


class StorySearcher(Protocol):

    def search(self, keyword):
        ...


class FullStorySource(
    StoryReader,
    StorySearcher,
    Protocol,
):
    ...
```

Conceptually:

```text
StoryReader
      +
StorySearcher
      ↓
FullStorySource
```

Nhưng client vẫn có thể phụ thuộc vào interface nhỏ.

---

# 30. Khi nào interface nên được tách?

Hãy xem xét ISP khi:

### 1.

Implementation phải viết:

```python
raise NotImplementedError
```

### 2.

Implementation có nhiều:

```python
pass
```

cho methods không dùng.

### 3.

Client chỉ sử dụng 1–2 methods trong interface rất lớn.

### 4.

Một thay đổi trong interface ảnh hưởng đến rất nhiều client không liên quan.

### 5.

Mock/fake implementation trở nên khó viết.

### 6.

Các implementation hỗ trợ những capability khác nhau.

### 7.

Bạn bắt đầu phải dùng:

```python
hasattr(...)
```

hoặc:

```python
isinstance(...)
```

để kiểm tra capability.

---

# 31. ISP và Change Coupling

Đây là một cách nhìn sâu.

Giả sử:

```text
HugeInterface
      │
 ┌────┼─────┬──────┐
 ↓    ↓     ↓      ↓
 A    B     C      D
```

Nếu thêm method:

```text
new_method()
```

thì có thể tất cả:

```text
A
B
C
D
```

bị ảnh hưởng.

Mặc dù:

```text
A
```

không hề cần method mới.

Đây chính là **coupling do interface quá lớn**.

ISP giảm:

```text
Unnecessary coupling
```

---

# 32. ISP và Dependency Graph

Interface lớn:

```text
          HugeInterface
          /    |    \
         /     |     \
       A       B      C
```

Một thay đổi:

```text
HugeInterface
      ↓
A B C
```

đều bị tác động.

Interface nhỏ:

```text
Reader
 ↑
 A

Writer
 ↑
 B

Searcher
 ↑
 C
```

Thay đổi `Writer`:

```text
B
```

không ảnh hưởng:

```text
A
C
```

Đây là giá trị kiến trúc rất lớn của ISP.

---

# 33. ISP và Package Architecture

ISP không chỉ nằm trong class.

Ví dụ package:

```text
myapp.database
    ├── sqlite.py
    ├── postgres.py
    ├── redis.py
    ├── backup.py
    ├── migration.py
    └── admin.py
```

Nếu application chỉ cần:

```text
read stories
```

mà import:

```python
from myapp.database import Database
```

với một API khổng lồ, có thể tạo coupling không cần thiết.

Một architecture tốt có thể expose capability-oriented API:

```text
story_reader
story_writer
story_searcher
```

ISP có thể được áp dụng ở mức module/package.

---

# 34. ISP và API Design

REST API cũng có tư duy tương tự.

Không nhất thiết:

```text
/api/everything
```

với:

```text
GET
POST
PUT
DELETE
SEARCH
EXPORT
BACKUP
ADMIN
```

cho mọi consumer.

Consumer A chỉ cần:

```text
GET /stories
```

Consumer B:

```text
POST /stories
```

Consumer C:

```text
GET /stories/search
```

Tách capability giúp giảm coupling.

---

# 35. Sai lầm phổ biến #1

> “Interface càng nhỏ càng tốt.”

Sai.

Mục tiêu:

```text
Small
+
Cohesive
+
Client-focused
```

Không phải:

```text
Small at all costs
```

---

# 36. Sai lầm phổ biến #2

> “Mỗi class phải implement một interface.”

Sai.

Một implementation hoàn toàn có thể:

```text
implement
Reader
+
Writer
+
Searcher
```

ISP chỉ nói client không nên bị ép phụ thuộc vào tất cả.

---

# 37. Sai lầm phổ biến #3

> “Protocol càng ít method càng tốt.”

Sai.

Protocol:

```python
class StoryReader(Protocol):

    def get_story(self, id):
        ...

    def get_chapter(self, id):
        ...
```

có thể hoàn toàn hợp lý nếu cả hai thuộc cùng capability:

```text
Reading
```

---

# 38. Sai lầm phổ biến #4

> “Dùng ISP để tránh mọi inheritance.”

Không.

ISP không chống inheritance.

Nó chống:

```text
unnecessary dependency
```

Bạn vẫn có thể dùng:

```python
class FullRepository(
    StoryReader,
    StoryWriter,
):
    ...
```

---

# 39. Refactoring Recipe

Khi gặp interface lớn:

### Bước 1

Liệt kê tất cả methods.

```text
A
B
C
D
E
F
```

### Bước 2

Liệt kê client.

```text
Client X → A B
Client Y → C D
Client Z → A E
```

### Bước 3

Tìm nhóm capability.

```text
Reader → A B
Writer → C D
Exporter → E F
```

### Bước 4

Tạo Protocol nhỏ.

```python
class Reader(Protocol):
    ...
```

### Bước 5

Đổi dependency của client.

```python
ClientX(reader: Reader)
```

### Bước 6

Chạy test.

### Bước 7

Xóa abstraction cũ nếu không còn cần.

---

# 40. Case Study hoàn chỉnh — Story Application

Giả sử ban đầu:

```python
class StoryService(Protocol):

    def list_stories(self):
        ...

    def get_story(self, id):
        ...

    def get_chapter(self, id):
        ...

    def search(self, keyword):
        ...

    def save(self, story):
        ...

    def delete(self, id):
        ...

    def export(self, story):
        ...
```

Đây là một **fat interface**.

Tách:

```python
class StoryLister(Protocol):

    def list_stories(self):
        ...


class StoryReader(Protocol):

    def get_story(self, id):
        ...


class ChapterReader(Protocol):

    def get_chapter(self, id):
        ...


class StorySearcher(Protocol):

    def search(self, keyword):
        ...


class StoryWriter(Protocol):

    def save(self, story):
        ...

    def delete(self, id):
        ...


class StoryExporter(Protocol):

    def export(self, story):
        ...
```

---

# 41. Use Cases sau refactor

List:

```python
class ListStoriesUseCase:

    def __init__(self, reader: StoryLister):
        self.reader = reader
```

Get:

```python
class GetStoryUseCase:

    def __init__(self, reader: StoryReader):
        self.reader = reader
```

Search:

```python
class SearchStoryUseCase:

    def __init__(self, searcher: StorySearcher):
        self.searcher = searcher
```

Create:

```python
class CreateStoryUseCase:

    def __init__(self, writer: StoryWriter):
        self.writer = writer
```

Export:

```python
class ExportStoryUseCase:

    def __init__(self, exporter: StoryExporter):
        self.exporter = exporter
```

Mỗi use case có dependency rất rõ ràng.

---

# 42. Đây là kiến trúc mà bạn nên hướng tới

```text
                    Application
                        │
        ┌───────────────┼────────────────┐
        ↓               ↓                ↓
   StoryReader    StoryWriter      StorySearcher
        ↑               ↑                ↑
        └───────────────┼────────────────┘
                        │
              SqliteStoryRepository
```

Repository implementation có thể rất lớn.

Nhưng Application chỉ nhìn thấy:

```text
capabilities
```

chứ không nhìn thấy:

```text
implementation details
```

---

# 43. Bài tập Buổi 7 — Cơ bản

Cho:

```python
class Worker(Protocol):

    def run(self):
        ...

    def pause(self):
        ...

    def resume(self):
        ...

    def cancel(self):
        ...

    def get_logs(self):
        ...
```

Có client:

```python
class WorkerMonitor:

    def __init__(self, worker):
        self.worker = worker

    def show_logs(self):
        return self.worker.get_logs()
```

### Yêu cầu

1. Có ISP violation không?
2. `WorkerMonitor` thực sự cần capability nào?
3. Tạo interface phù hợp.
4. Refactor `WorkerMonitor`.

---

# 44. Bài tập Buổi 7 — Repository

Cho:

```python
class Repository(Protocol):

    def get(self, id):
        ...

    def save(self, entity):
        ...

    def delete(self, id):
        ...

    def search(self, keyword):
        ...
```

Có 3 use case:

```text
GetEntityUseCase
CreateEntityUseCase
SearchEntityUseCase
```

Hãy thiết kế lại thành:

```text
EntityReader
EntityWriter
EntitySearcher
```

sử dụng `Protocol`.

---

# 45. Bài tập Buổi 7 — Crawler Plugin

Thiết kế lại:

```python
class CrawlerPlugin(Protocol):

    def list_stories(self):
        ...

    def get_story(self):
        ...

    def get_chapter(self):
        ...

    def search(self):
        ...

    def login(self):
        ...

    def download_image(self):
        ...
```

Giả sử:

```text
SiteA:
list + story + chapter

SiteB:
list + story + chapter + search

SiteC:
list + story + chapter + search + login
```

Không được dùng:

```python
raise NotImplementedError
```

Hãy thiết kế lại bằng capability interfaces.

---

# 46. Bài tập nâng cao — Change Coupling

Cho:

```text
Interface I
├── method_a
├── method_b
├── method_c
├── method_d
└── method_e
```

Client:

```text
A → a,b
B → c
C → d,e
```

Nếu `method_e` thay đổi:

> Client nào thực sự nên bị ảnh hưởng?

Sau đó thiết kế lại interface sao cho:

```text
A
B
C
```

độc lập hơn.

---

# 47. Mental Model của ISP

Đừng nhớ ISP bằng:

> “Interface phải nhỏ.”

Hãy nhớ:

```text
                Client
                   │
                   ↓
             What does it need?
                   │
             ┌─────┴─────┐
             ↓           ↓
        Capability A  Capability B
             │           │
             ↓           ↓
        Small Protocol
```

Hoặc ngắn gọn:

> **Design interfaces from the client's point of view, not from the implementation's point of view.**

---

# 48. Quan hệ giữa SRP, OCP, LSP, ISP

Đến đây ta đã có một chuỗi rất đẹp:

```text
SRP
│
├── Một module có responsibility rõ ràng
│
↓
OCP
│
├── Variation có extension point
│
↓
LSP
│
├── Implementation phải giữ contract
│
↓
ISP
│
├── Client chỉ phụ thuộc capability cần thiết
│
↓
DIP
│
└── Client phụ thuộc abstraction thay vì concrete implementation
```

Đặc biệt:

```text
ISP
  ↓
Interface nhỏ
  ↓
LSP dễ tuân thủ hơn
  ↓
DIP dễ áp dụng hơn
```

---

# 49. Tiến độ khóa học

```text
✅ Buổi 1 — SOLID Foundation
✅ Buổi 2 — SRP
✅ Buổi 3 — SRP Deep Dive + Refactoring
✅ Buổi 4 — OCP
✅ Buổi 5 — LSP
✅ Buổi 6 — LSP Deep Dive
✅ Buổi 7 — ISP

⬜ Buổi 8 — ISP Deep Dive
⬜ Buổi 9 — DIP
```

**Buổi 8 — ISP Deep Dive** chúng ta sẽ đi sâu vào những phần quan trọng hơn:

* Interface Segregation trong `Protocol`
* ISP + Dependency Injection
* ISP + Mock/Fake
* ISP + Repository
* ISP + Clean Architecture
* ISP + Plugin Architecture
* ISP và package/module boundary
* Interface pollution
* Over-segregation
* Role Interface
* Capability Interface
* Facade vs ISP
* Adapter vs ISP
* Refactoring một **fat service** thành các role interfaces
* **Case study: `CrawlerPlugin` framework** từ kiến trúc hiện tại của bạn.
