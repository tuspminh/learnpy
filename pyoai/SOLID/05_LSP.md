# SOLID Deep Dive — Buổi 5

# Liskov Substitution Principle — LSP

Hôm nay chúng ta học chữ **L**:

> **Liskov Substitution Principle**

Đây là principle khó hơn SRP và OCP rất nhiều, vì LSP không chỉ nói về **cấu trúc class**, mà nói về **behavior và contract**.

Nếu SRP hỏi:

> Class này có trách nhiệm gì?

OCP hỏi:

> Tôi có thể mở rộng behavior mà không sửa core không?

thì LSP hỏi:

> **Nếu B là subtype của A, tôi có thể dùng B ở mọi nơi đang cần A mà chương trình vẫn đúng không?**

---

# 1. Định nghĩa

Barbara Liskov đưa ra ý tưởng về **behavioral subtyping**.

Hiểu thực tế:

> **Subtype phải có thể thay thế cho base type mà không phá vỡ những giả định của client.**

Ví dụ:

```python
class Bird:
    def fly(self):
        ...


class Eagle(Bird):
    def fly(self):
        ...


def make_fly(bird: Bird):
    bird.fly()
```

`Eagle` có thể thay thế `Bird`:

```python
make_fly(Eagle())
```

Không vấn đề.

Nhưng:

```python
class Penguin(Bird):

    def fly(self):
        raise NotImplementedError
```

thì:

```python
make_fly(Penguin())
```

bị lỗi.

Đây là **LSP violation**.

---

# 2. “IS-A” chưa đủ

Đây là lỗi tư duy rất phổ biến khi học OOP.

Ta thường nghĩ:

```text
Penguin IS-A Bird
```

→ inheritance:

```python
class Penguin(Bird):
    ...
```

Về mặt thế giới thực:

```text
Penguin là Bird
```

đúng.

Nhưng về mặt phần mềm:

```text
Penguin
```

có thực sự thỏa **contract của Bird** không?

Nếu `Bird` contract nói:

```python
bird.fly()
```

luôn có thể gọi được,

thì Penguin không thỏa contract.

Vì vậy:

> **Inheritance relationship không tự động tạo ra valid subtype relationship.**

---

# 3. Behavioral Subtyping

Đây là keyword quan trọng nhất của LSP:

> **Behavioral Subtyping**

Không chỉ:

```text
class B(A)
```

mà phải:

```text
B behaves correctly wherever A is expected
```

Ví dụ:

```python
def process_payment(payment: Payment):
    payment.pay(100)
```

Nếu:

```python
class BrokenPayment(Payment):

    def pay(self, amount):
        raise RuntimeError("Cannot pay")
```

thì `BrokenPayment` có thể vi phạm contract của `Payment`.

---

# 4. Contract

Để hiểu LSP, ta cần hiểu:

> **Contract**

Một method có thể có:

```text
Precondition
Postcondition
Invariant
```

---

# 5. Precondition

Precondition = điều kiện client phải thỏa **trước khi gọi**.

Ví dụ:

```python
class BankAccount:

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError()

        ...
```

Contract:

```text
amount > 0
```

Client có thể giả định:

```python
account.withdraw(100)
```

hợp lệ.

---

# 6. Postcondition

Postcondition = điều kiện phải đúng **sau khi method chạy thành công**.

Ví dụ:

```python
class BankAccount:

    def deposit(self, amount):
        ...
```

Nếu contract nói:

```text
balance_after
=
balance_before + amount
```

thì implementation phải đảm bảo điều đó.

---

# 7. Invariant

Invariant = điều kiện luôn phải đúng đối với object.

Ví dụ:

```python
class BankAccount:
    balance >= 0
```

có thể là invariant.

Nếu subtype phá vỡ invariant:

```python
class SpecialAccount(BankAccount):
    ...
```

thì có thể vi phạm LSP.

---

# 8. Quy tắc quan trọng của LSP

Có một cách diễn đạt kinh điển:

### Subtype không nên yêu cầu mạnh hơn

Subtype không nên **strengthen preconditions**.

### Subtype không nên đảm bảo yếu hơn

Subtype không nên **weaken postconditions**.

### Subtype phải giữ invariant

Hãy nhớ:

```text id="n18cz3"
Precondition
Subtype không được mạnh hơn

Postcondition
Subtype không được yếu hơn

Invariant
Subtype phải giữ được
```

---

# 9. Ví dụ Precondition

Base:

```python
class FileStorage:

    def save(self, data: bytes):
        ...
```

Giả sử contract:

```text
save() nhận mọi bytes hợp lệ
```

Subtype:

```python
class PdfStorage(FileStorage):

    def save(self, data: bytes):
        if not data.startswith(b"%PDF"):
            raise ValueError("Only PDF")
```

Subtype đã thêm precondition:

```text
Base:
mọi bytes

Subtype:
chỉ PDF
```

Client từng dùng:

```python
storage.save(any_bytes)
```

giờ có thể crash.

Đây là LSP violation.

---

# 10. Ví dụ Postcondition

Base:

```python
class Cache:

    def put(self, key, value):
        ...
```

Giả sử contract:

```text
Sau put(), get(key) trả về value
```

Subtype:

```python
class UnreliableCache(Cache):

    def put(self, key, value):
        # đôi khi không lưu
        pass
```

Client:

```python
cache.put("name", "Alice")

assert cache.get("name") == "Alice"
```

có thể fail.

Subtype không giữ postcondition.

---

# 11. Rectangle / Square Problem

Một ví dụ kinh điển.

Ta có:

```python
class Rectangle:

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height
```

Square:

```python
class Square(Rectangle):

    def set_width(self, width):
        self.width = width
        self.height = width

    def set_height(self, height):
        self.width = height
        self.height = height
```

Về toán học:

```text
Square IS-A Rectangle
```

Nhưng:

```python
def resize(rectangle):
    rectangle.set_width(10)
    rectangle.set_height(20)

    return rectangle.width * rectangle.height
```

Với Rectangle:

```text
10 × 20 = 200
```

Với Square:

```text
20 × 20 = 400
```

Behavior thay đổi.

Client không thể sử dụng Square như Rectangle.

Đây là LSP violation.

---

# 12. Bài học từ Rectangle/Square

LSP dạy chúng ta:

> **Mô hình domain “A là B” chưa chắc tương đương với subtype relationship trong code.**

Inheritance không chỉ biểu diễn:

```text
classification
```

mà còn biểu diễn:

```text
behavioral contract
```

Đây là điểm cực kỳ quan trọng.

---

# 13. Composition có thể tốt hơn inheritance

Thay vì:

```python
class Square(Rectangle):
    ...
```

ta có thể thiết kế:

```python
class Shape:
    def area(self):
        ...
```

Rectangle:

```python
class Rectangle(Shape):

    def area(self):
        return self.width * self.height
```

Square:

```python
class Square(Shape):

    def area(self):
        return self.side ** 2
```

Cả hai cùng thỏa:

```text
Shape
  ↓
area()
```

Không cần giả định:

```text
Square is mutable Rectangle
```

Đây là một giải pháp rất mạnh:

> **Abstraction nên thể hiện behavior mà client cần, không phải toàn bộ cấu trúc inheritance.**

---

# 14. LSP và Interface nhỏ

Ví dụ:

```python
class Animal:

    def eat(self):
        ...

    def fly(self):
        ...

    def swim(self):
        ...
```

Sau đó:

```python
class Dog(Animal):
    def fly(self):
        raise NotImplementedError
```

Đây không chỉ là vấn đề LSP.

Nó còn gợi ý:

```text
ISP
```

vì interface:

```text
Animal
```

đã quá rộng.

Có thể tách:

```python
class Eater:
    def eat(self):
        ...


class Flyer:
    def fly(self):
        ...


class Swimmer:
    def swim(self):
        ...
```

Bây giờ:

```text
Dog
 ↓
Eater

Duck
 ↓
Eater
Flyer
Swimmer
```

Đây là nơi **LSP và ISP bắt đầu liên quan nhau**.

---

# 15. LSP không chỉ liên quan inheritance

Đây là một insight rất quan trọng.

Ví dụ:

```python
class Repository(Protocol):

    def get(self, id: int):
        ...
```

Implementation:

```python
class SqliteRepository:

    def get(self, id):
        ...
```

và:

```python
class MemoryRepository:

    def get(self, id):
        ...
```

Không cần:

```python
class MemoryRepository(Repository)
```

nhưng cả hai phải tuân thủ:

```text
Repository contract
```

Nếu:

```python
SqliteRepository.get(1)
```

trả về object,

nhưng:

```python
MemoryRepository.get(1)
```

luôn raise exception khi không tìm thấy,

trong khi client không mong đợi exception, thì vẫn có thể có LSP violation.

Do đó:

> **LSP nói về substitutability, không đơn thuần là inheritance.**

---

# 16. Python và Duck Typing

Python đặc biệt thú vị.

Ta có:

```python
def send_message(sender):
    sender.send("hello")
```

Không cần:

```python
class Sender(ABC)
```

Bất kỳ object nào có:

```python
send()
```

đều có thể được dùng.

Nhưng vẫn tồn tại một contract ngầm:

```text id="v2p2zq"
sender.send(message)
```

phải có behavior mà client mong đợi.

Vì vậy Duck Typing **không loại bỏ LSP**.

Ngược lại:

> **Duck typing khiến behavioral contract càng quan trọng.**

---

# 17. Exception và LSP

Một vấn đề rất hay gặp.

Base:

```python
class Downloader:

    def download(self, url):
        ...
```

Client:

```python
try:
    downloader.download(url)
except DownloadError:
    ...
```

Subtype:

```python
class SpecialDownloader(Downloader):

    def download(self, url):
        raise SomeCompletelyDifferentError()
```

Client có thể không xử lý được.

Subtype đã thay đổi error contract.

Đây có thể là LSP violation.

---

# 18. Return Type

Base:

```python
class Repository:

    def get(self, id) -> User:
        ...
```

Subtype:

```python
class CachedRepository(Repository):

    def get(self, id) -> None:
        ...
```

Nếu client mong:

```python
user = repository.get(1)
print(user.name)
```

thì subtype phá contract.

Trong typing hiện đại, type checker có thể giúp phát hiện một số vấn đề như vậy.

---

# 19. Mutable State

Một nguồn LSP violation khác là mutable state.

Ví dụ:

```python
class Account:

    def withdraw(self, amount):
        ...
```

Base cho phép:

```text
withdraw(100)
```

Subtype:

```python
class FrozenAccount(Account):

    def withdraw(self, amount):
        raise RuntimeError()
```

Nếu client đã có contract:

```text
Account có thể withdraw
```

thì `FrozenAccount` không còn thay thế được.

Nếu thực sự cần frozen account, có thể abstraction đúng hơn là:

```text
ReadableAccount
WritableAccount
```

---

# 20. LSP và “NotImplementedError”

Một smell rất mạnh:

```python
class BaseStorage:

    def save(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def upload(self):
        raise NotImplementedError
```

Sau đó:

```python
class ReadOnlyStorage(BaseStorage):

    def save(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError
```

Đây là dấu hiệu abstraction có vấn đề.

Bạn đang nói:

```text
ReadOnlyStorage
IS-A
BaseStorage
```

nhưng lại không thể sử dụng nó như BaseStorage.

Có khả năng cần:

```text id="r8xxgc"
ReadableStorage
WritableStorage
DeletableStorage
```

Đây sẽ dẫn chúng ta tới ISP.

---

# 21. LSP + OCP

Hai principle này liên kết rất chặt.

OCP nói:

```text
Thêm subtype/implementation
→ không sửa core
```

Nhưng nếu subtype mới:

```text
phá contract
```

thì OCP chẳng còn ý nghĩa.

Ví dụ:

```text id="3jpm1j"
Payment
  ↑
  ├── CardPayment
  ├── BankPayment
  └── BrokenPayment
```

Core:

```python id="xk7f2g"
def checkout(payment: Payment):
    payment.pay(100)
```

Nếu `BrokenPayment` không thực hiện đúng contract:

```text id="qv1b7e"
OCP ✔
LSP ✘
```

Do đó:

> **Extension point chỉ an toàn khi implementation tuân thủ contract.**

---

# 22. LSP + Repository

Đây là ví dụ rất thực tế với kiến trúc bạn đang xây dựng.

Ta có:

```python id="h3t5sc"
from typing import Protocol


class StoryRepository(Protocol):

    def save(self, story: Story) -> None:
        ...

    def get(self, story_id: int) -> Story | None:
        ...
```

SQLite:

```python id="m0q0go"
class SqliteStoryRepository:

    def save(self, story):
        ...

    def get(self, story_id):
        ...
```

Memory:

```python id="qk8fdo"
class InMemoryStoryRepository:

    def save(self, story):
        ...

    def get(self, story_id):
        ...
```

Use case:

```python id="5ydxgm"
class GetStoryUseCase:

    def __init__(self, repository):
        self.repository = repository

    def execute(self, story_id):
        return self.repository.get(story_id)
```

Nếu cả hai repository đều tuân thủ:

```text id="j9e3bc"
get(existing_id)
→ Story

get(non_existing_id)
→ None
```

thì chúng có thể thay thế nhau.

Đây là LSP.

---

# 23. Một ví dụ vi phạm tinh vi hơn

SQLite:

```python id="9r0q6r"
class SqliteStoryRepository:

    def get(self, story_id):
        return story_or_none
```

Memory:

```python id="j7q7u2"
class MemoryStoryRepository:

    def get(self, story_id):
        if story_id not in self.data:
            raise KeyError(story_id)

        return self.data[story_id]
```

Cả hai đều có:

```python
get()
```

Type checker có thể không phản đối.

Nhưng behavior khác:

```text id="7pfrc4"
SQLite
missing → None

Memory
missing → KeyError
```

Nếu client contract là:

```text id="cqzj2j"
missing → None
```

thì `MemoryStoryRepository` vi phạm LSP.

Đây chính là **behavioral contract**.

---

# 24. Cách thiết kế contract tốt

Nếu muốn LSP rõ ràng, hãy xác định:

```text id="3l40s6"
Input
Output
Errors
State changes
Invariants
```

Ví dụ:

```text
StoryRepository.get()

Input:
    story_id > 0

Output:
    Story | None

Errors:
    DatabaseError nếu database failure

Behavior:
    không xóa dữ liệu
```

Subtype phải tôn trọng contract đó.

---

# 25. LSP trong crawler plugin

Đây là phần rất quan trọng cho architecture crawler.

Ta có:

```python id="f7ey5b"
class CrawlerPlugin(Protocol):

    def can_handle(self, url: str) -> bool:
        ...

    def crawl(self, url: str) -> Story:
        ...
```

Core:

```python id="vqm1l2"
def run_plugin(
    plugin: CrawlerPlugin,
    url: str,
):
    if plugin.can_handle(url):
        return plugin.crawl(url)
```

Nếu `SiteAPlugin`:

```python id="70lqwc"
def crawl(self, url):
    return Story(...)
```

và `SiteBPlugin`:

```python id="r9d5cs"
def crawl(self, url):
    raise NotImplementedError
```

thì SiteB không phải một valid plugin.

Nếu:

```text id="b8l6la"
can_handle(url) == True
```

thì client có quyền mong đợi:

```text id="08hs2q"
crawl(url)
```

hoạt động đúng contract.

---

# 26. LSP và `can_handle`

Cẩn thận với contract:

```python id="y0t3gs"
plugin.can_handle(url)
```

Nếu trả:

```text
True
```

thì plugin phải đảm bảo:

```python id="nj9qv4"
plugin.crawl(url)
```

có thể xử lý URL đó.

Nếu:

```python id="cm4k9g"
can_handle() → True
crawl() → UnsupportedUrlError
```

thì có thể có contract inconsistency.

Một contract tốt có thể là:

```text id="xg6uxm"
can_handle(url) == True
        ↓
plugin có trách nhiệm xử lý url
```

Đây là LSP ở mức architecture.

---

# 27. LSP và Design by Contract

Bạn có thể hình dung:

```text id="k2d0cl"
            Contract
               │
       ┌───────┼────────┐
       ↓       ↓        ↓
Precondition Postcondition Invariant
       │       │        │
       └───────┼────────┘
               ↓
             LSP
```

Subtype phải tôn trọng contract.

Đây là cách hiểu sâu hơn rất nhiều so với:

> “LSP là subclass phải thay thế superclass.”

---

# 28. Một heuristic rất mạnh

Khi bạn định viết:

```python
class Child(Parent):
    ...
```

hãy hỏi:

### 1.

Client đang kỳ vọng điều gì từ `Parent`?

### 2.

`Child` có đáp ứng toàn bộ expectation đó không?

### 3.

`Child` có thêm precondition không?

### 4.

`Child` có làm yếu postcondition không?

### 5.

`Child` có thay đổi exception behavior không?

### 6.

`Child` có phá invariant không?

### 7.

Client có phải kiểm tra:

```python
if isinstance(child, SomeSpecialType):
```

không?

Nếu câu trả lời cuối là **có**, đó là một smell rất mạnh.

---

# 29. `isinstance()` và LSP

Ví dụ:

```python id="jnd0v1"
def process(storage):
    if isinstance(storage, ReadOnlyStorage):
        ...
    else:
        storage.save(...)
```

Nếu client phải biết subtype cụ thể để xử lý đúng:

```text id="8k8m3k"
Abstraction
    ↓
không đủ tốt
```

Có khả năng:

```text id="8e7p3g"
LSP violation
```

hoặc abstraction design đang có vấn đề.

Một abstraction tốt giúp client viết:

```python id="kq0zqn"
storage.save(...)
```

mà không cần biết implementation cụ thể.

---

# 30. LSP không nói “subclass phải giống hệt”

Điều này cũng quan trọng.

Subtype hoàn toàn có thể:

* tối ưu hơn
* nhanh hơn
* thêm behavior
* dùng algorithm khác
* lưu dữ liệu khác
* có implementation hoàn toàn khác

Miễn là:

```text id="9h6p8k"
Public contract
        ↓
được giữ nguyên
```

Ví dụ:

```text id="i7g3yw"
Repository
   ↑
   ├── SQLite
   ├── PostgreSQL
   ├── Redis
   └── Memory
```

implementation khác nhau hoàn toàn.

Nhưng client vẫn có thể dùng chúng theo cùng contract.

Đó chính là mục tiêu.

---

# 31. Bài tập 1 — Rectangle

Cho:

```python id="2z9gcd"
class Rectangle:

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

    def area(self):
        return self.width * self.height
```

và:

```python id="q8g8qb"
class Square(Rectangle):

    def set_width(self, width):
        self.width = width
        self.height = width

    def set_height(self, height):
        self.width = height
        self.height = height
```

Hãy giải thích chính xác:

1. Vì sao `Square` vi phạm LSP?
2. Contract của `Rectangle` là gì?
3. Precondition có thay đổi không?
4. Postcondition có thay đổi không?
5. Invariant nào bị ảnh hưởng?
6. Thiết kế lại abstraction.

---

# 32. Bài tập 2 — Repository

Cho:

```python id="x1f8qb"
class StoryRepository(Protocol):

    def get(self, id: int) -> Story | None:
        ...
```

Implementation A:

```python id="7hmg9b"
class SqliteStoryRepository:

    def get(self, id):
        ...
```

Implementation B:

```python id="skkz0n"
class MemoryStoryRepository:

    def get(self, id):
        if id not in self.data:
            raise KeyError(id)

        return self.data[id]
```

Hãy xác định:

```text id="efb4nw"
Có LSP violation không?
Nếu có, chính xác contract nào bị phá?
```

---

# 33. Bài tập 3 — Crawler Plugin

Thiết kế:

```python id="n5i7o8"
class CrawlerPlugin(Protocol):

    def can_handle(self, url: str) -> bool:
        ...

    def crawl(self, url: str) -> Story:
        ...
```

Tạo:

```text id="b84jkj"
SiteAPlugin
SiteBPlugin
```

với contract:

```text id="f2v2qb"
can_handle(url) == True
        ↓
crawl(url) phải xử lý được URL
        ↓
trả Story hợp lệ
```

Sau đó cố tình tạo một plugin vi phạm LSP và giải thích vì sao.

---

# 34. Tổng kết Buổi 5

Ba tầng tư duy:

```text id="x4u8y0"
Inheritance
    ↓
Subtype
    ↓
Behavioral Subtype
```

Không dừng ở:

```text id="wjy8a9"
B extends A
```

mà phải:

```text id="k7m4y4"
B có thể thay A
        ↓
client vẫn đúng
        ↓
contract vẫn được giữ
```

Mental model:

```text id="2af7xl"
              LSP
               │
               ↓
          Substitutability
               │
               ↓
            Contract
        ┌──────┼──────┐
        ↓      ↓      ↓
   Precondition Postcondition Invariant
```

Và một câu cần nhớ:

> **LSP không hỏi “B có phải là A không?”; LSP hỏi “B có thể thực sự đóng vai A mà client không cần biết sự khác biệt không?”**

---

### Tiến độ khóa học

```text
✅ Buổi 1 — SOLID Foundation
✅ Buổi 2 — SRP
✅ Buổi 3 — SRP Deep Dive + Refactoring
✅ Buổi 4 — OCP
✅ Buổi 5 — LSP
⬜ Buổi 6 — LSP Deep Dive
⬜ Buổi 7 — ISP
⬜ Buổi 8 — ISP Deep Dive
⬜ Buổi 9 — DIP
...
```

**Buổi 6** sẽ đi sâu vào những trường hợp LSP khó hơn: **exception contract, mutable state, covariance/contravariance, `Protocol`, `ABC`, `NotImplementedError`, inheritance vs composition**, và đặc biệt là cách phát hiện LSP violation trong một codebase Python thực tế.
