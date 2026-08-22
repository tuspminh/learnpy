# SOLID Deep Dive — Buổi 6

# LSP Deep Dive — Behavioral Contract trong Python

Buổi 5 chúng ta đã hiểu:

> **LSP = subtype phải có thể thay thế cho abstraction mà không phá vỡ contract của client.**

Buổi 6 sẽ đi sâu hơn vào **những violation khó nhìn thấy**. Đây là phần rất quan trọng nếu bạn muốn thiết kế **Repository, Service, Plugin, Worker, Crawler** bằng Python.

---

# 1. LSP thực sự nằm ở đâu?

Một cách nhìn đơn giản:

```text
                 Abstraction
                      │
             ┌────────┴────────┐
             │                 │
       Implementation A   Implementation B
             │                 │
             └────────┬────────┘
                      ↓
                 Same Contract
                      ↓
                 Same Client
```

Ví dụ:

```python
def process(repo: StoryRepository):
    story = repo.get(10)

    if story is not None:
        print(story.title)
```

`process()` không quan tâm:

```text
SQLite
Memory
PostgreSQL
Redis
Mock
```

Miễn là tất cả đều tuân thủ:

```text
get(id)
    ↓
Story | None
```

---

# 2. LSP nằm ở “client expectation”

Đây là insight quan trọng nhất của buổi này.

Không thể đánh giá LSP chỉ bằng:

```python
class Child(Parent):
    ...
```

Ta phải nhìn **client**.

Ví dụ:

```python
def checkout(payment):
    payment.pay(100)
```

Client đang giả định:

```text
payment có pay()
pay(100) có thể thực hiện
```

Nếu:

```python
class BrokenPayment:

    def pay(self, amount):
        raise NotImplementedError
```

thì implementation này không thể thay thế payment mà client mong đợi.

---

# 3. LSP violation không nhất thiết gây lỗi ngay

Đây là điểm rất dễ bỏ qua.

Ví dụ:

```python
class Repository(Protocol):

    def get(self, id: int) -> Story | None:
        ...
```

Implementation:

```python
class MemoryRepository:

    def get(self, id):
        ...
```

Code chạy bình thường.

Nhưng behavior:

```text
SQLite:
missing → None

Memory:
missing → KeyError
```

Không có syntax error.

Không có type error.

Nhưng:

```text
Contract khác nhau
        ↓
Client behavior khác nhau
        ↓
LSP violation
```

Đây là lý do LSP thường khó phát hiện hơn SRP/OCP.

---

# 4. Contract gồm nhiều thứ hơn return type

Khi thiết kế abstraction, contract có thể bao gồm:

```text
Input
Output
Exception
Side effect
State
Ordering
Timing
Idempotency
Invariant
```

Ví dụ:

```python
class StoryRepository(Protocol):

    def save(self, story: Story) -> None:
        ...
```

Không chỉ có:

```text
return None
```

Mà còn có thể ngầm hiểu:

```text
save(story)
    ↓
story được lưu
    ↓
lần get tiếp theo có thể lấy được
```

Nếu implementation chỉ:

```python
def save(self, story):
    pass
```

thì return type đúng nhưng behavior sai.

---

# 5. Return Type — chưa đủ

Ví dụ:

```python
class Cache(Protocol):

    def get(self, key: str) -> str | None:
        ...
```

Implementation A:

```python
class MemoryCache:

    def get(self, key):
        return self.data.get(key)
```

Implementation B:

```python
class RedisCache:

    def get(self, key):
        return self.client.get(key)
```

Nếu Redis client trả:

```python
bytes | None
```

thì:

```text
Protocol:
str | None

Redis:
bytes | None
```

Mặc dù method tồn tại, contract đã khác.

Client:

```python
value = cache.get("name")

print(value.upper())
```

có thể hoạt động với `str` nhưng không còn đúng theo expectation ban đầu.

---

# 6. Exception Contract

Đây là một trong những nguồn LSP violation phổ biến nhất.

Giả sử:

```python
class StoryRepository(Protocol):

    def get(self, id: int) -> Story | None:
        ...
```

Contract:

```text
Không tìm thấy:
    → None

Database error:
    → RepositoryError
```

Client:

```python
def get_story(repo, id):

    try:
        return repo.get(id)

    except RepositoryError:
        return None
```

Implementation A:

```python
class SqliteRepository:

    def get(self, id):
        ...
        # raises RepositoryError
```

Implementation B:

```python
class MemoryRepository:

    def get(self, id):
        ...
        raise KeyError(id)
```

Client không xử lý `KeyError`.

Kết quả:

```text
SQLiteRepository
    ↓
đúng contract

MemoryRepository
    ↓
sai contract
```

→ LSP violation.

---

# 7. Exception là một phần API

Khi thiết kế interface:

```python
class Downloader(Protocol):

    def download(self, url: str) -> bytes:
        ...
```

đừng chỉ nghĩ:

```text
Input → Output
```

Hãy nghĩ:

```text
Input
 ↓
Output
 ↓
Failure modes
```

Ví dụ contract:

```text
download(url)

Success:
    → bytes

Invalid URL:
    → InvalidUrlError

Network failure:
    → DownloadError
```

Mọi implementation phải tôn trọng abstraction này.

---

# 8. Không nên expose implementation-specific exception

Ví dụ:

```python
class SqliteRepository:

    def get(self, id):
        raise sqlite3.OperationalError(...)
```

Nếu abstraction là:

```text
StoryRepository
```

thì client domain/application không nên phải biết:

```python
sqlite3.OperationalError
```

Tốt hơn:

```python
class RepositoryError(Exception):
    pass
```

và:

```python
class SqliteRepository:

    def get(self, id):

        try:
            ...
        except sqlite3.Error as exc:
            raise RepositoryError() from exc
```

Bây giờ abstraction có contract ổn định:

```text
Infrastructure exception
        ↓
RepositoryError
        ↓
Application
```

Điều này hỗ trợ LSP rất tốt.

---

# 9. Strengthening Preconditions

Đây là một khái niệm quan trọng.

Base:

```python
class Downloader(Protocol):

    def download(self, url: str) -> bytes:
        ...
```

Giả sử client có quyền gọi:

```python
download("https://example.com")
```

Subtype:

```python
class SpecialDownloader:

    def download(self, url: str) -> bytes:

        if not url.endswith(".html"):
            raise ValueError()

        ...
```

Subtype đã yêu cầu:

```text
Base:
mọi URL hợp lệ

Subtype:
chỉ .html
```

Subtype làm **precondition mạnh hơn**.

→ LSP violation.

---

# 10. Weakening Preconditions

Ngược lại, subtype có thể chấp nhận **nhiều hơn**.

Base:

```text
chỉ chấp nhận URL HTTPS
```

Subtype:

```text
chấp nhận HTTPS + HTTP
```

Điều này thường không phá LSP.

Ta có:

```text
Base:
    HTTPS

Subtype:
    HTTPS
    HTTP
```

Subtype không yêu cầu client phải làm thêm điều gì.

Do đó:

> **Subtype có thể nới rộng input requirements.**

---

# 11. Postcondition

Base:

```python
class Repository(Protocol):

    def save(self, story: Story) -> None:
        ...
```

Giả sử:

```text
Sau save():
    story tồn tại trong repository
```

Subtype:

```python
class FakeRepository:

    def save(self, story):
        print("saved")
```

Không thực sự lưu.

Return:

```text
None
```

vẫn đúng.

Nhưng postcondition:

```text
story được lưu
```

bị phá.

→ LSP violation.

---

# 12. Strengthening Postcondition

Subtype có thể đảm bảo **nhiều hơn** base mà không phá LSP.

Base:

```text
save()
    ↓
story được lưu
```

Subtype:

```text
save()
    ↓
story được lưu
+
audit log được ghi
+
cache được update
```

Thông thường:

```text
Base contract
    ⊂
Subtype guarantees
```

vẫn substitutable.

---

# 13. Invariant

Invariant là điều kiện phải luôn đúng.

Ví dụ:

```python
class BankAccount:
    balance >= 0
```

Subtype:

```python
class OverdraftAccount(BankAccount):
    balance >= -1000
```

Bây giờ subtype cho phép:

```text
balance = -500
```

Nếu base client giả định:

```python
assert account.balance >= 0
```

thì client có thể fail.

Cần xem lại abstraction.

---

# 14. Mutable State và LSP

Mutable object rất dễ tạo LSP violation.

Ví dụ:

```python
class User:

    def change_name(self, name):
        self.name = name
```

Subtype:

```python
class ImmutableUser(User):

    def change_name(self, name):
        raise RuntimeError()
```

Client:

```python
def rename(user: User):
    user.change_name("Alice")
```

Với `User`:

```text
OK
```

Với `ImmutableUser`:

```text
RuntimeError
```

Subtype không còn thay thế được base.

---

# 15. Read-only subtype

Đây là một pattern hay gặp:

```text
Repository
    ↓
ReadOnlyRepository
```

Nếu `Repository` có:

```python
get()
save()
delete()
```

thì:

```python
class ReadOnlyRepository(Repository):
    ...
```

rất dễ vi phạm LSP.

Bởi vì client của `Repository` có quyền:

```python
repo.save(...)
```

nhưng ReadOnlyRepository không thể thực hiện.

Giải pháp thường tốt hơn:

```text
ReadableRepository
        ↑
        │
ReadWriteRepository
```

Ví dụ:

```python
class StoryReader(Protocol):

    def get(self, id: int) -> Story | None:
        ...
```

```python
class StoryRepository(StoryReader, Protocol):

    def save(self, story: Story) -> None:
        ...

    def delete(self, id: int) -> None:
        ...
```

Bây giờ:

```text
StoryReader
    ↓
chỉ đọc

StoryRepository
    ↓
đọc + ghi
```

Đây là thiết kế tốt hơn.

---

# 16. LSP và ISP bắt đầu giao nhau

Đây là lý do sau LSP chúng ta học ISP.

Nếu bạn thường xuyên viết:

```python
class BaseService:
    method_a()
    method_b()
    method_c()
    method_d()
```

rồi subtype:

```python
class SpecialService(BaseService):

    def method_c(self):
        raise NotImplementedError
```

thì có thể có hai vấn đề:

```text
LSP
+
ISP
```

LSP:

```text
SpecialService không thể thay BaseService
```

ISP:

```text
BaseService quá lớn
```

---

# 17. Covariance

Bây giờ đến phần typing sâu hơn.

Giả sử:

```python
class Animal:
    ...


class Dog(Animal):
    ...
```

Một function:

```python
def get_animal() -> Animal:
    ...
```

Subtype có thể trả về:

```python
Dog
```

Điều này thường an toàn:

```text
Animal
   ↑
  Dog
```

Client cần Animal:

```python
animal = get_animal()
```

Dog vẫn là Animal.

Đây là:

> **Covariant return type**

---

# 18. Ví dụ covariance

```python
class Animal:
    pass


class Dog(Animal):
    pass


class AnimalFactory:

    def create(self) -> Animal:
        ...


class DogFactory(AnimalFactory):

    def create(self) -> Dog:
        ...
```

Subtype trả về kiểu **cụ thể hơn**.

```text
Base:
Animal

Subtype:
Dog
```

An toàn vì:

```text
Dog IS-A Animal
```

---

# 19. Contravariance

Phần này khó hơn.

Nếu một function **nhận input**, subtype thường phải có khả năng xử lý input **ít nhất rộng bằng** base.

Ví dụ:

```python
class Animal:
    pass


class Dog(Animal):
    pass
```

Base processor:

```python
class AnimalProcessor:

    def process(self, animal: Animal):
        ...
```

Subtype nếu chỉ nhận:

```python
class DogProcessor:

    def process(self, dog: Dog):
        ...
```

thì có vấn đề.

Client có thể làm:

```python
processor.process(Cat())
```

nếu `processor` được xem là `AnimalProcessor`.

Nhưng `DogProcessor` không xử lý được Cat.

→ LSP violation.

---

# 20. Quy tắc dễ nhớ

Đối với subtype:

```text
Return type
    ↓
có thể cụ thể hơn

Parameter type
    ↓
không nên hẹp hơn
```

Mental model:

```text
INPUT
→ chấp nhận rộng

OUTPUT
→ trả về cụ thể
```

Đây là cách trực giác để nhớ:

```text
Covariance
Contravariance
```

---

# 21. `Protocol` và LSP

Python rất phù hợp để biểu diễn abstraction bằng `Protocol`.

Ví dụ:

```python
from typing import Protocol


class StoryRepository(Protocol):

    def get(self, id: int) -> Story | None:
        ...

    def save(self, story: Story) -> None:
        ...
```

Implementation:

```python
class SqliteStoryRepository:

    def get(self, id: int) -> Story | None:
        ...

    def save(self, story: Story) -> None:
        ...
```

Không cần inheritance.

Nhưng vẫn phải đảm bảo:

```text
Structural compatibility
+
Behavioral compatibility
```

`Protocol` giúp kiểm tra phần **shape/type**.

LSP yêu cầu thêm:

```text
behavior
```

---

# 22. `Protocol` không đảm bảo LSP

Đây là một điểm cực kỳ quan trọng.

Code:

```python
class Repository(Protocol):

    def get(self, id: int) -> Story | None:
        ...
```

Implementation:

```python
class BrokenRepository:

    def get(self, id: int) -> Story | None:
        raise RuntimeError()
```

Type checker có thể thấy:

```text
signature OK
```

nhưng behavior:

```text
contract broken
```

Vì vậy:

> **Type compatibility ≠ behavioral substitutability.**

---

# 23. ABC cũng không đảm bảo LSP

Tương tự:

```python
from abc import ABC, abstractmethod


class Repository(ABC):

    @abstractmethod
    def get(self, id):
        ...
```

Subtype:

```python
class BrokenRepository(Repository):

    def get(self, id):
        raise RuntimeError()
```

Python cho phép.

ABC chỉ đảm bảo:

```text
method exists
```

Không đảm bảo:

```text
method behaves correctly
```

---

# 24. `NotImplementedError` — một smell

Nếu bạn thấy:

```python
class BaseRepository:

    def save(self):
        raise NotImplementedError
```

và rất nhiều subclass:

```python
class ReadOnlyRepository(BaseRepository):

    def save(self):
        raise NotImplementedError
```

hãy dừng lại.

Đừng chỉ nghĩ:

> “Subclass chưa implement.”

Hãy hỏi:

> **Tại sao subtype không thể thực hiện contract của base?**

Nếu câu trả lời là:

> “Vì nó không có capability đó.”

thì abstraction có thể sai.

---

# 25. Composition vs Inheritance

Một trong những cách tránh LSP violation mạnh nhất:

> **Prefer composition over inheritance khi behavior không thực sự substitutable.**

Ví dụ không tốt:

```python
class ReadOnlyRepository(Repository):
    ...
```

Có thể chuyển thành:

```python
class StoryReader:
    ...
```

và:

```python
class StoryRepository(StoryReader):
    ...
```

Hoặc composition:

```python
class StoryService:

    def __init__(self, reader):
        self.reader = reader
```

Không ép một object có capability mà nó không có.

---

# 26. Một ví dụ architecture thực tế

Giả sử application crawler của bạn có:

```text
StorySource
```

Bạn muốn:

```text
Source
├── list_stories()
├── get_story()
├── get_chapter()
├── search()
└── download()
```

Sau đó một website không hỗ trợ search:

```python
class SiteA(Source):

    def search(self, keyword):
        raise NotImplementedError
```

Có vấn đề.

Client:

```python
def search_stories(source: Source):
    return source.search("python")
```

không thể dùng SiteA.

Đừng ép:

```text
SiteA IS-A FullSource
```

Hãy tách capability:

```text
StoryLister
StoryReader
ChapterReader
Searcher
Downloader
```

Đây là bước chuyển tự nhiên từ:

```text
LSP
```

sang:

```text
ISP
```

---

# 27. Test LSP bằng contract tests

Đây là kỹ thuật rất hữu ích trong Python.

Ta có contract:

```python
def repository_contract(repo):
    repo.save(story)

    result = repo.get(story.id)

    assert result == story
```

Sau đó test:

```python
def test_sqlite_repository():
    repository_contract(SqliteStoryRepository(...))
```

và:

```python
def test_memory_repository():
    repository_contract(MemoryStoryRepository(...))
```

Nếu cả hai pass:

```text
Same contract
```

Đây là cách rất thực tế để kiểm tra LSP.

---

# 28. Contract Test nâng cao

Ví dụ:

```python
def repository_contract(repo):

    missing = repo.get(999999)

    assert missing is None

    repo.save(story)

    result = repo.get(story.id)

    assert result == story
```

Nếu:

```text
SQLite → pass
Memory → pass
Redis → fail
```

thì implementation Redis không tuân thủ contract.

Không cần biết implementation bên trong như thế nào.

---

# 29. Đây là cách rất hay cho plugin architecture

Crawler framework:

```python
def crawler_plugin_contract(plugin):

    assert plugin.can_handle(TEST_URL)

    story = plugin.crawl(TEST_URL)

    assert story.title
    assert story.chapters
```

Mỗi plugin:

```text
SiteA
SiteB
SiteC
SiteD
```

phải pass cùng contract.

Đây là:

> **LSP + Contract Testing**

rất mạnh trong hệ thống plugin.

---

# 30. Checklist phát hiện LSP violation

Khi review code, hãy tìm:

### Smell 1

```python
raise NotImplementedError
```

### Smell 2

```python
if isinstance(...)
```

### Smell 3

```python
if type(...) == ...
```

### Smell 4

Subtype yêu cầu input đặc biệt hơn.

### Smell 5

Subtype throw exception mà base không dự kiến.

### Smell 6

Subtype trả về semantics khác.

### Smell 7

Subtype không duy trì invariant.

### Smell 8

Client phải biết subtype cụ thể.

### Smell 9

Một subclass override method thành:

```python
pass
```

### Smell 10

Một implementation có behavior khác nhau đáng kể dù cùng interface.

Không phải smell nào cũng chắc chắn là LSP violation.

Nhưng tất cả đều đáng điều tra.

---

# 31. Một quy trình refactoring LSP

Khi gặp violation:

```text
1. Xác định client
        ↓
2. Xác định expectation
        ↓
3. Viết contract
        ↓
4. Xác định implementation nào phá contract
        ↓
5. Kiểm tra abstraction
        ↓
6. Tách interface nếu cần
        ↓
7. Composition nếu cần
        ↓
8. Viết contract tests
```

Đừng bắt đầu bằng:

```text
“Xóa inheritance đi.”
```

Hãy bắt đầu bằng:

> **Client thực sự cần capability nào?**

---

# 32. Case Study — Payment

Giả sử:

```python
class Payment(Protocol):

    def pay(self, amount: float) -> None:
        ...
```

Implementation:

```python
class CreditCardPayment:

    def pay(self, amount):
        ...
```

```python
class CashPayment:

    def pay(self, amount):
        ...
```

```python
class FreePayment:

    def pay(self, amount):
        if amount != 0:
            raise ValueError()
```

Câu hỏi:

> `FreePayment` có vi phạm LSP không?

Câu trả lời:

**Chưa chắc.**

Ta phải biết contract của `Payment`.

Nếu contract là:

```text
pay(amount)
→ amount phải >= 0
```

thì FreePayment có thể vi phạm vì nó yêu cầu:

```text
amount == 0
```

Nếu contract là:

```text
Payment implementation được phép từ chối amount không hỗ trợ
```

thì có thể không vi phạm.

Đây chính là lý do:

> **LSP không thể đánh giá chỉ từ class structure.**

Phải biết **contract**.

---

# 33. Case Study — Notification

```python
class Notifier(Protocol):

    def send(self, message: str) -> None:
        ...
```

Email:

```python
class EmailNotifier:

    def send(self, message):
        ...
```

Telegram:

```python
class TelegramNotifier:

    def send(self, message):
        ...
```

Broken:

```python
class SilentNotifier:

    def send(self, message):
        pass
```

Nếu contract là:

```text
send()
→ message phải được gửi
```

thì `SilentNotifier` vi phạm LSP.

Nếu `SilentNotifier` được định nghĩa là:

```text
Null Object
```

và contract explicitly nói:

```text
send() may intentionally do nothing
```

thì lại không vi phạm.

Một lần nữa:

```text
Contract
    ↓
determines LSP
```

---

# 34. Null Object Pattern

Đây là một ứng dụng thú vị của LSP.

Thay vì:

```python
if notifier:
    notifier.send(message)
```

ta có:

```python
class NullNotifier:

    def send(self, message):
        pass
```

Nếu `Notifier` contract cho phép:

```text
send()
    ↓
no-op implementation
```

thì:

```python
service = NotificationService(
    NullNotifier()
)
```

vẫn hợp lệ.

Null Object chỉ tốt khi nó **thực sự tuân thủ abstraction contract**.

---

# 35. Mental Model cuối buổi

Đừng nhớ LSP bằng câu:

> “Subclass phải có thể thay thế superclass.”

Hãy nhớ sâu hơn:

```text
                  Client
                    │
                    ↓
                Contract
                    │
          ┌─────────┴─────────┐
          ↓                   ↓
   Implementation A    Implementation B
          │                   │
          └─────────┬─────────┘
                    ↓
             Same expectation
```

Và:

```text
Input
 ↓
Precondition
 ↓
Operation
 ↓
Postcondition
 ↓
Output
```

Subtype phải giữ được contract đó.

---

# 36. Bài tập Buổi 6

## Bài 1 — Repository Contract

Thiết kế:

```python
class StoryRepository(Protocol):
    ...
```

Contract:

```text
get(id):
    found     → Story
    not found → None

save(story):
    story phải được lưu

delete(id):
    nếu không tồn tại → None
```

Viết:

```text
SqliteStoryRepository
MemoryStoryRepository
```

và một bộ **contract tests** dùng chung cho cả hai.

---

## Bài 2 — Tìm LSP violation

```python
class FileStorage(Protocol):

    def read(self, path: str) -> bytes:
        ...

    def write(self, path: str, data: bytes) -> None:
        ...
```

Implementation:

```python
class ReadOnlyStorage:

    def read(self, path):
        ...

    def write(self, path, data):
        raise PermissionError()
```

Hãy trả lời:

1. Có LSP violation không?
2. Client nào bị ảnh hưởng?
3. Contract nào bị phá?
4. Thiết kế abstraction lại như thế nào?

---

## Bài 3 — Crawler Plugin

Thiết kế contract:

```python
class CrawlerPlugin(Protocol):
    ...
```

Yêu cầu:

```text
can_handle(url) == True
        ↓
crawl(url)
        ↓
Story hợp lệ
```

Viết:

```text
SiteAPlugin
SiteBPlugin
BrokenPlugin
```

Sau đó viết:

```python
def crawler_plugin_contract(plugin):
    ...
```

để phát hiện `BrokenPlugin`.

---

## Bài 4 — Covariance / Contravariance

Giải thích tại sao:

```python
class Dog(Animal):
    pass
```

thì:

```python
def create() -> Dog:
    ...
```

có thể thay:

```python
def create() -> Animal:
    ...
```

nhưng một processor:

```python
def process(dog: Dog):
    ...
```

không nhất thiết có thể thay:

```python
def process(animal: Animal):
    ...
```

---

# 37. Tiến độ SOLID

```text
✅ Buổi 1 — SOLID Foundation

✅ Buổi 2 — SRP

✅ Buổi 3 — SRP Deep Dive + Refactoring

✅ Buổi 4 — OCP

✅ Buổi 5 — LSP

✅ Buổi 6 — LSP Deep Dive

⬜ Buổi 7 — ISP

⬜ Buổi 8 — ISP Deep Dive

⬜ Buổi 9 — DIP
```

**Buổi 7 — ISP (Interface Segregation Principle)** sẽ nối trực tiếp từ vấn đề cuối buổi hôm nay:

```text
Interface quá lớn
       ↓
Subclass không thể implement đầy đủ
       ↓
NotImplementedError
       ↓
LSP violation
       ↓
Tách interface
       ↓
ISP
```

Đây là lúc chúng ta chuyển từ câu hỏi **“Subtype có thực sự thay thế được abstraction không?”** sang câu hỏi **“Abstraction này có đang ép client phụ thuộc vào những thứ nó không cần không?”**
