# Python OOP Master — Buổi 30

## Interface Segregation Principle — ISP

Hôm nay chúng ta học nguyên lý thứ 4 của SOLID:

> **I — Interface Segregation Principle**

Nếu **LSP** hỏi:

> “Subclass có thể thay thế class/interface cha không?”

thì **ISP** hỏi:

> **“Interface này có đang bắt client phụ thuộc vào những thứ nó không cần không?”**

Đây là nguyên lý cực kỳ quan trọng khi thiết kế:

* Repository
* Crawler
* Parser
* Storage
* Notification
* Service
* Plugin Architecture
* Clean Architecture

---

# 1. Mục tiêu

Sau buổi này bạn sẽ hiểu:

* ISP là gì
* Vì sao interface quá lớn là vấn đề
* “Fat Interface” là gì
* Client không nên phụ thuộc vào method mình không sử dụng
* Cách tách interface
* ISP với `ABC`
* ISP với Python Duck Typing
* ISP + DI
* ISP + Repository
* ISP + Crawler
* ISP + LSP
* Khi nào **không nên** tách interface quá nhỏ

---

# 2. ISP là gì?

Robert C. Martin định nghĩa:

> **Clients should not be forced to depend on interfaces they do not use.**

Hiểu đơn giản:

> **Không ép một class phải phụ thuộc vào những method mà nó không cần.**

Ví dụ xấu:

```python
class Worker:
    def work(self):
        pass

    def eat(self):
        pass
```

Nếu có:

```python
class Robot(Worker):

    def work(self):
        print("Robot working")

    def eat(self):
        raise NotImplementedError
```

thì có vấn đề.

Robot bị ép phải implement:

```python
eat()
```

mặc dù Robot không cần ăn.

Đây là dấu hiệu của **ISP violation**.

---

# 3. Fat Interface

Một interface quá lớn thường được gọi là:

```text
Fat Interface
```

Ví dụ:

```python
from abc import ABC, abstractmethod


class Machine(ABC):

    @abstractmethod
    def print(self, document):
        pass

    @abstractmethod
    def scan(self, document):
        pass

    @abstractmethod
    def fax(self, document):
        pass

    @abstractmethod
    def copy(self, document):
        pass
```

Ta có:

```python
class SimplePrinter(Machine):

    def print(self, document):
        print("Printing")

    def scan(self, document):
        raise NotImplementedError

    def fax(self, document):
        raise NotImplementedError

    def copy(self, document):
        raise NotImplementedError
```

Rõ ràng:

```text
SimplePrinter
```

chỉ cần:

```text
print()
```

nhưng bị ép phụ thuộc vào:

```text
scan()
fax()
copy()
```

Đây chính là vấn đề ISP.

---

# 4. Tách interface

Thay vì:

```text
Machine
 ├── print
 ├── scan
 ├── fax
 └── copy
```

ta tách:

```text
Printer
 └── print

Scanner
 └── scan

Fax
 └── fax

Copier
 └── copy
```

Code:

```python
from abc import ABC, abstractmethod


class Printer(ABC):

    @abstractmethod
    def print(self, document):
        pass


class Scanner(ABC):

    @abstractmethod
    def scan(self, document):
        pass


class Fax(ABC):

    @abstractmethod
    def fax(self, document):
        pass
```

Simple printer:

```python
class SimplePrinter(Printer):

    def print(self, document):
        print("Printing")
```

Không còn:

```python
raise NotImplementedError
```

cho những behavior không liên quan.

---

# 5. Multi-function Printer

Một máy in đa chức năng có thể implement nhiều interface:

```python
class MultiFunctionPrinter(Printer, Scanner, Fax):

    def print(self, document):
        print("Printing")

    def scan(self, document):
        print("Scanning")

    def fax(self, document):
        print("Faxing")
```

Bây giờ:

```text
Printer
       \
Scanner ---> MultiFunctionPrinter
       /
Fax
```

Mỗi client chỉ phụ thuộc interface cần thiết.

---

# 6. Đây mới là điểm quan trọng

Giả sử:

```python
def print_document(printer: Printer, document):
    printer.print(document)
```

Function này chỉ cần:

```text
Printer
```

Nó không cần biết:

```text
Scanner
Fax
Copier
```

Đây chính là ISP.

Client:

```text
print_document()
```

chỉ phụ thuộc vào:

```text
Printer
```

thay vì:

```text
Machine
```

---

# 7. ISP không có nghĩa là “mỗi class một interface”

Đừng hiểu ISP thành:

> “Mỗi method phải có một interface.”

Ví dụ này quá mức:

```python
class CanCreate:
    ...

class CanRead:
    ...

class CanUpdate:
    ...

class CanDelete:
    ...
```

Có thể đúng trong một số kiến trúc.

Nhưng nếu hệ thống của bạn luôn sử dụng:

```text
CRUD
```

cùng nhau thì việc tách quá nhỏ có thể làm architecture trở nên phức tạp không cần thiết.

Mục tiêu của ISP là:

```text
Interface
    ↓
cohesive responsibilities
```

chứ không phải:

```text
1 method = 1 interface
```

---

# 8. ISP và Cohesion

Interface tốt thường có **cohesion cao**.

Ví dụ:

```python
class StoryReader(ABC):

    @abstractmethod
    def get_story(self, story_id):
        pass

    @abstractmethod
    def get_chapters(self, story_id):
        pass
```

Hai method liên quan trực tiếp đến:

```text
Reading
```

Đây là interface khá cohesive.

---

# 9. Interface xấu

Ví dụ:

```python
class StorySystem(ABC):

    @abstractmethod
    def crawl(self):
        pass

    @abstractmethod
    def parse(self):
        pass

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def render_ui(self):
        pass

    @abstractmethod
    def send_notification(self):
        pass
```

Đây là một interface có quá nhiều trách nhiệm.

Nó trộn:

```text
Crawler
Parser
Repository
UI
Notification
```

Đây vừa có vấn đề ISP vừa có thể vi phạm SRP.

---

# 10. Tách theo client

Một cách rất tốt để áp dụng ISP:

> **Tách interface dựa trên nhu cầu của client.**

Ví dụ:

```text
Crawler
   ↓
Parser

ReadingPage
   ↓
StoryReader

Dashboard
   ↓
CrawlerStatusReader

Admin
   ↓
CrawlerController
```

Không nhất thiết tất cả phải phụ thuộc vào:

```text
StorySystem
```

---

# 11. ISP trong Repository

Đây là phần đặc biệt quan trọng đối với project của bạn.

Giả sử:

```python
class StoryRepository(ABC):

    @abstractmethod
    def create(self, story):
        pass

    @abstractmethod
    def get(self, story_id):
        pass

    @abstractmethod
    def update(self, story):
        pass

    @abstractmethod
    def delete(self, story_id):
        pass

    @abstractmethod
    def search(self, keyword):
        pass

    @abstractmethod
    def count(self):
        pass
```

Có thể ban đầu trông rất ổn.

Nhưng hãy xem các client.

---

# 12. ReadingPage

Reading page chỉ cần:

```text
get story
get chapters
```

Nó không cần:

```text
create
update
delete
```

Nếu ép:

```python
class ReadingService:

    def __init__(self, repository: StoryRepository):
        self.repository = repository
```

thì `ReadingService` đang phụ thuộc vào một interface lớn hơn nhu cầu.

---

# 13. Tách Repository Interface

Ta có:

```python
from abc import ABC, abstractmethod


class StoryReader(ABC):

    @abstractmethod
    def get(self, story_id):
        pass


class StoryWriter(ABC):

    @abstractmethod
    def create(self, story):
        pass

    @abstractmethod
    def update(self, story):
        pass


class StoryDeleter(ABC):

    @abstractmethod
    def delete(self, story_id):
        pass
```

Bây giờ:

```text
StoryReader
StoryWriter
StoryDeleter
```

là những interface nhỏ và có mục đích rõ ràng.

---

# 14. Reading Service

Reading Service:

```python
class ReadingService:

    def __init__(self, reader: StoryReader):
        self.reader = reader

    def read_story(self, story_id):
        return self.reader.get(story_id)
```

Nó chỉ phụ thuộc:

```text
StoryReader
```

Không phụ thuộc:

```text
StoryWriter
StoryDeleter
```

Đây chính là ISP + DI.

---

# 15. SQLite Repository

Một implementation có thể implement nhiều interface:

```python
class SQLiteStoryRepository(
    StoryReader,
    StoryWriter,
    StoryDeleter,
):

    def get(self, story_id):
        ...

    def create(self, story):
        ...

    def update(self, story):
        ...

    def delete(self, story_id):
        ...
```

Không có vấn đề gì.

Một object có thể cung cấp nhiều capability.

```text
                SQLiteStoryRepository
                 /       |        \
                /        |         \
               ↓         ↓          ↓
        StoryReader  StoryWriter  StoryDeleter
```

Nhưng client chỉ nhận capability mà nó cần.

---

# 16. Đây là một pattern rất mạnh

Ví dụ:

```python
repository = SQLiteStoryRepository()
```

Ta có thể truyền:

```python
ReadingService(repository)
```

vì:

```text
SQLiteStoryRepository
        ↓
    StoryReader
```

Hoặc:

```python
AdminService(repository)
```

vì:

```text
SQLiteStoryRepository
        ↓
    StoryWriter
```

Object thật:

```text
SQLiteStoryRepository
```

có nhiều khả năng.

Nhưng mỗi client chỉ nhìn thấy interface nhỏ tương ứng.

---

# 17. ISP + Dependency Injection

Ta có:

```python
class ReadingService:

    def __init__(self, reader: StoryReader):
        self.reader = reader
```

và:

```python
class AdminService:

    def __init__(self, writer: StoryWriter):
        self.writer = writer
```

Composition Root:

```python
repository = SQLiteStoryRepository()

reading_service = ReadingService(repository)

admin_service = AdminService(repository)
```

Một implementation:

```text
SQLiteStoryRepository
```

được inject vào nhiều client.

Nhưng:

```text
ReadingService
```

chỉ biết:

```text
StoryReader
```

và:

```text
AdminService
```

chỉ biết:

```text
StoryWriter
```

Đây là thiết kế rất sạch.

---

# 18. ISP trong Crawler

Project crawler của bạn có thể có interface:

```text
Crawler
```

nhưng đừng gom tất cả behavior vào một interface.

Ví dụ xấu:

```python
class Crawler(ABC):

    @abstractmethod
    def crawl(self):
        pass

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def resume(self):
        pass

    @abstractmethod
    def cancel(self):
        pass

    @abstractmethod
    def get_status(self):
        pass

    @abstractmethod
    def retry_failed(self):
        pass
```

Một object crawler nhỏ có thể chỉ thực sự cần:

```text
crawl()
```

---

# 19. Tách crawler capabilities

Có thể thiết kế:

```python
class CrawlerRunner(ABC):

    @abstractmethod
    def crawl(self):
        pass


class CrawlerController(ABC):

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def resume(self):
        pass

    @abstractmethod
    def cancel(self):
        pass


class CrawlerMonitor(ABC):

    @abstractmethod
    def get_status(self):
        pass
```

Kiến trúc:

```text
                 Crawler
                    │
        ┌───────────┼────────────┐
        ↓           ↓            ↓
CrawlerRunner  CrawlerController CrawlerMonitor
```

---

# 20. Dashboard

Dashboard chỉ cần:

```python
class Dashboard:

    def __init__(self, monitor: CrawlerMonitor):
        self.monitor = monitor

    def refresh(self):
        status = self.monitor.get_status()
        print(status)
```

Dashboard không cần:

```text
crawl()
```

không cần:

```text
pause()
resume()
```

nếu nó chỉ hiển thị trạng thái.

---

# 21. Control Panel

Ngược lại:

```python
class CrawlerControlPanel:

    def __init__(self, controller: CrawlerController):
        self.controller = controller

    def pause(self):
        self.controller.pause()

    def resume(self):
        self.controller.resume()
```

Control Panel chỉ phụ thuộc:

```text
CrawlerController
```

Đây là ISP rất rõ ràng.

---

# 22. ISP + PySide6

Điều này đặc biệt hữu ích với ứng dụng PySide6 của bạn.

Ví dụ Dashboard:

```text
Dashboard
   ↓
CrawlerMonitor
```

Reading Page:

```text
ReadingPage
   ↓
StoryReader
```

Crawler Control:

```text
CrawlerControl
   ↓
CrawlerController
```

Không nên để tất cả UI phụ thuộc vào một:

```text
ApplicationService
```

khổng lồ.

---

# 23. Fat Service

Một vấn đề tương tự cũng xảy ra với Service.

Ví dụ:

```python
class StoryService:

    def create_story(self):
        ...

    def update_story(self):
        ...

    def delete_story(self):
        ...

    def read_story(self):
        ...

    def search_story(self):
        ...

    def crawl_story(self):
        ...

    def export_story(self):
        ...

    def send_notification(self):
        ...
```

Đây là dấu hiệu:

```text
Fat Service
```

Không chỉ ISP mà SRP cũng có thể bị vi phạm.

---

# 24. Interface theo use case

Trong Clean Architecture/DDD, ta có thể thiết kế interface theo nhu cầu application layer:

```text
application/
│
├── commands/
│   ├── create_story.py
│   ├── update_story.py
│   └── delete_story.py
│
└── queries/
    ├── get_story.py
    └── search_story.py
```

Read side:

```text
StoryReader
```

Write side:

```text
StoryWriter
```

Điều này rất phù hợp với:

```text
CQRS
```

mà bạn đã học.

---

# 25. ISP + CQRS

Có thể hình dung:

```text
              Application
                   │
          ┌────────┴────────┐
          ↓                 ↓
        Query             Command
          │                 │
          ↓                 ↓
    StoryReader        StoryWriter
          │                 │
          ↓                 ↓
      Read Model        Write Model
```

Query không cần:

```text
create()
update()
delete()
```

Command không cần:

```text
search()
```

Đây là ISP kết hợp rất tự nhiên với CQRS.

---

# 26. ISP và Duck Typing

Python không bắt buộc bạn phải dùng `ABC`.

Ví dụ:

```python
class Printer:

    def print(self, document):
        print(document)
```

Client:

```python
def print_document(printer, document):
    printer.print(document)
```

Bất kỳ object nào có:

```python
.print()
```

đều có thể dùng.

Đây là Duck Typing.

---

# 27. Protocol — cách Python hiện đại

Với type checking, ta có thể dùng:

```python
from typing import Protocol


class StoryReader(Protocol):

    def get(self, story_id: int):
        ...
```

Implementation không cần kế thừa:

```python
class SQLiteStoryRepository:

    def get(self, story_id: int):
        ...
```

Python vẫn có thể xem nó phù hợp với protocol về mặt cấu trúc.

Đây là:

```text
Structural Typing
```

rất phù hợp với tinh thần ISP.

---

# 28. ABC vs Protocol

|                     | ABC                 | Protocol       |
| ------------------- | ------------------- | -------------- |
| Kế thừa             | Thường có           | Không bắt buộc |
| Runtime abstraction | Mạnh                | Nhẹ            |
| Duck typing         | Không tự nhiên bằng | Rất phù hợp    |
| Explicit contract   | Rõ                  | Rõ qua type    |
| Plugin architecture | Tốt                 | Rất tốt        |
| Python hiện đại     | Tốt                 | Rất hữu ích    |

Ví dụ với crawler:

```python
class StoryParser(Protocol):

    def parse(self, html: str) -> ParsedStory:
        ...
```

Parser:

```python
class SiteAParser:

    def parse(self, html: str) -> ParsedStory:
        ...
```

Không cần:

```python
class SiteAParser(StoryParser):
```

vẫn phù hợp về mặt structural typing.

---

# 29. ISP + LSP

Hai nguyên lý này có mối quan hệ rất thú vị.

### ISP

Tách:

```text
Fat Interface
```

thành:

```text
Small Interfaces
```

### LSP

Đảm bảo implementation:

```text
tuân thủ contract
```

Ví dụ:

```text
StoryRepository
      ↓
StoryReader
StoryWriter
StoryDeleter
```

Sau khi tách interface bằng ISP, từng implementation vẫn phải tuân thủ LSP.

---

# 30. ISP + OCP

Buổi 28:

```text
OCP
```

muốn:

```text
extension
```

không làm thay đổi client.

ISP giúp tạo những abstraction nhỏ:

```text
Parser
Storage
Notification
```

Sau đó ta có thể thêm:

```text
SiteCParser
RedisStorage
TelegramNotification
```

mà client chỉ phụ thuộc capability cần thiết.

---

# 31. ISP + SRP

Hai nguyên lý này cũng liên quan.

### SRP

Class/module không nên có quá nhiều trách nhiệm.

### ISP

Interface không nên có quá nhiều trách nhiệm đối với một client.

Ví dụ:

```text
StorySystem
```

vừa:

```text
crawl
parse
save
read
notify
```

có thể vi phạm:

```text
SRP
+
ISP
```

Refactor:

```text
Crawler
Parser
Repository
Reader
Notifier
```

---

# 32. Một kiến trúc tổng hợp

Đối với story crawler/reader của bạn, ta có thể hướng tới:

```text
                         Application
                              │
             ┌────────────────┼────────────────┐
             ↓                ↓                ↓
          Crawler          Reader           Dashboard
             │                │                │
             ↓                ↓                ↓
       CrawlerRunner      StoryReader     CrawlerMonitor
             │                │                │
             ↓                ↓                ↓
          Parser          Read Model       Crawler State
             │
      ┌──────┼──────┐
      ↓      ↓      ↓
   SiteA   SiteB   SiteC
```

Repository:

```text
                Repository
                     │
          ┌──────────┴──────────┐
          ↓                     ↓
    StoryReader            StoryWriter
          │                     │
          └──────────┬──────────┘
                     ↓
          SQLiteStoryRepository
```

Đây là kiến trúc bắt đầu rất gần với:

```text
Clean Architecture
+
DDD
+
CQRS
+
SOLID
```

---

# 33. Khi nào interface quá lớn?

Một interface có thể đang quá lớn nếu:

### Dấu hiệu 1

Implementation thường xuyên có:

```python
raise NotImplementedError
```

---

### Dấu hiệu 2

Subclass có rất nhiều:

```python
pass
```

---

### Dấu hiệu 3

Client chỉ dùng:

```text
1–2 methods
```

trong một interface có:

```text
10–20 methods
```

---

### Dấu hiệu 4

Một thay đổi trong interface ảnh hưởng đến rất nhiều implementation không liên quan.

---

### Dấu hiệu 5

Client phải nhận dependency lớn:

```python
class UI:

    def __init__(self, giant_service):
        ...
```

trong khi UI chỉ dùng một method.

---

# 34. Nhưng đừng tách interface quá sớm

Ví dụ:

```python
class UserRepository:
    def create(...)
    def get(...)
    def update(...)
    def delete(...)
```

Nếu toàn bộ application thực sự dùng CRUD thì interface này hoàn toàn có thể hợp lý.

Đừng biến nó thành:

```text
UserCreator
UserReader
UserUpdater
UserDeleter
```

chỉ vì muốn “SOLID tuyệt đối”.

SOLID là:

```text
design principle
```

không phải:

```text
law
```

---

# 35. Nguyên tắc thực tế

Hãy bắt đầu:

```text
Interface
```

sau đó quan sát:

```text
Client A
Client B
Client C
```

Nếu:

```text
Client A → method 1, 2
Client B → method 3, 4
Client C → method 5
```

thì có thể interface đang quá lớn.

Tách thành:

```text
Interface A → 1, 2
Interface B → 3, 4
Interface C → 5
```

---

# 36. Ví dụ hoàn chỉnh

Ta xây hệ thống storage.

### Interface

```python
from abc import ABC, abstractmethod


class Reader(ABC):

    @abstractmethod
    def read(self, key):
        pass


class Writer(ABC):

    @abstractmethod
    def write(self, key, value):
        pass


class Deleter(ABC):

    @abstractmethod
    def delete(self, key):
        pass
```

Implementation:

```python
class MemoryStorage(Reader, Writer, Deleter):

    def __init__(self):
        self.data = {}

    def read(self, key):
        return self.data.get(key)

    def write(self, key, value):
        self.data[key] = value

    def delete(self, key):
        self.data.pop(key, None)
```

---

# 37. Các client

Reader:

```python
class ReadService:

    def __init__(self, reader: Reader):
        self.reader = reader

    def get(self, key):
        return self.reader.read(key)
```

Writer:

```python
class WriteService:

    def __init__(self, writer: Writer):
        self.writer = writer

    def save(self, key, value):
        self.writer.write(key, value)
```

Delete:

```python
class DeleteService:

    def __init__(self, deleter: Deleter):
        self.deleter = deleter

    def remove(self, key):
        self.deleter.delete(key)
```

Composition Root:

```python
storage = MemoryStorage()

reader = ReadService(storage)
writer = WriteService(storage)
deleter = DeleteService(storage)
```

Một object:

```text
MemoryStorage
```

cung cấp:

```text
Reader
Writer
Deleter
```

nhưng mỗi service chỉ phụ thuộc vào interface cần thiết.

Đây là **ISP + DI** rất rõ ràng.

---

# 38. Bài tập 1 — Printer

Cho:

```python
class Machine(ABC):

    @abstractmethod
    def print(self):
        pass

    @abstractmethod
    def scan(self):
        pass

    @abstractmethod
    def fax(self):
        pass
```

Hãy refactor theo ISP.

Mục tiêu:

```text
Printer
Scanner
Fax
```

và:

```text
SimplePrinter
```

chỉ cần implement:

```text
Printer
```

---

# 39. Bài tập 2 — StoryRepository

Thiết kế:

```text
StoryReader
StoryWriter
StoryDeleter
StorySearcher
```

Sau đó:

```text
ReadingService
```

chỉ phụ thuộc:

```text
StoryReader
```

và:

```text
AdminService
```

chỉ phụ thuộc:

```text
StoryWriter
StoryDeleter
```

---

# 40. Bài tập 3 — Crawler Dashboard

Thiết kế:

```text
CrawlerRunner
CrawlerController
CrawlerMonitor
```

Với:

```text
CrawlerRunner
    crawl()

CrawlerController
    pause()
    resume()
    cancel()

CrawlerMonitor
    get_status()
    get_progress()
```

Sau đó:

```text
Dashboard
```

chỉ được phép phụ thuộc:

```text
CrawlerMonitor
```

Còn:

```text
ControlPanel
```

chỉ phụ thuộc:

```text
CrawlerController
```

---

# 41. Bài tập 4 — Protocol

Viết lại:

```python
class StoryReader(ABC):
    ...
```

thành:

```python
class StoryReader(Protocol):
    ...
```

Sau đó tạo:

```text
SQLiteStoryRepository
MemoryStoryRepository
FakeStoryRepository
```

mà không cần kế thừa `StoryReader`.

---

# 42. Bài tập 5 — Architecture Challenge

Thiết kế:

```text
                   Application
                        │
          ┌─────────────┼─────────────┐
          ↓             ↓             ↓
       Crawler       Reader       Dashboard
          ↓             ↓             ↓
       Parser      StoryReader   CrawlerMonitor
          ↓
    ┌─────┼─────┐
    ↓     ↓     ↓
 SiteA SiteB SiteC
```

Yêu cầu:

* Không có Fat Interface
* Không có God Service
* Dùng DI
* Parser tuân thủ LSP
* Interface tuân thủ ISP
* Crawler tuân thủ OCP
* Dễ thay SQLite bằng Memory Repository

Đây là bài tập rất tốt để kết nối:

```text
Buổi 24  Composition
   ↓
Buổi 25  Aggregation
   ↓
Buổi 26  Dependency Injection
   ↓
Buổi 27  SRP
   ↓
Buổi 28  OCP
   ↓
Buổi 29  LSP
   ↓
Buổi 30  ISP
```

---

# 43. Tóm tắt Buổi 30

ISP có thể ghi nhớ bằng một câu:

> **Một client chỉ nên phụ thuộc vào những interface chứa đúng những gì nó cần.**

Không nên:

```text
Client
   ↓
Fat Interface
   ↓
10 methods
   ↓
Client dùng 2 methods
```

Nên:

```text
Client
   ↓
Small Interface
   ↓
2 methods
```

Trong project crawler:

```text
Crawler
   ↓
CrawlerRunner

Dashboard
   ↓
CrawlerMonitor

ControlPanel
   ↓
CrawlerController

ReadingPage
   ↓
StoryReader
```

Và kiến trúc SOLID hiện tại của chúng ta:

```text
SRP
 ↓
Một component một nhóm trách nhiệm
 ↓
OCP
 ↓
Có thể mở rộng bằng implementation mới
 ↓
LSP
 ↓
Implementation phải thay thế được abstraction
 ↓
ISP
 ↓
Abstraction không được ép client phụ thuộc thứ không cần
```

**Buổi tiếp theo — Buổi 31: Dependency Inversion Principle (DIP)** sẽ là mảnh ghép cuối của SOLID. Khi kết hợp **DIP + DI + ISP + LSP**, chúng ta sẽ bắt đầu thiết kế được kiến trúc giống các hệ thống Python production thực tế.
