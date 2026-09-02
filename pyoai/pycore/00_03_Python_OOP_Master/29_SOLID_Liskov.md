# Python OOP Master — Buổi 29

## Liskov Substitution Principle — LSP

Hôm nay chúng ta học nguyên lý thứ 3 của **SOLID**:

> **L — Liskov Substitution Principle**

Đây là nguyên lý rất quan trọng vì nó trả lời câu hỏi:

> **“Khi tôi tạo subclass, tôi có thể thay object của class cha bằng object của class con mà chương trình vẫn hoạt động đúng không?”**

---

# 1. Mục tiêu

Sau buổi này bạn sẽ hiểu:

* LSP là gì
* Vì sao `is-a` chưa đủ để quyết định inheritance
* Behavioral compatibility là gì
* LSP liên quan thế nào đến contract
* Vì sao `Square` kế thừa `Rectangle` thường là ví dụ kinh điển của LSP violation
* LSP với `ABC`
* LSP với Repository
* LSP với Parser trong crawler
* Cách phát hiện và sửa LSP violation
* Quan hệ:

```text
OCP
 ↓
LSP
 ↓
ISP
 ↓
DIP
```

---

# 2. Định nghĩa LSP

Liskov Substitution Principle được Barbara Liskov đưa ra.

Cách hiểu thực tế:

> **Nếu `B` là subtype của `A`, thì mọi nơi đang yêu cầu `A` phải có thể nhận `B` mà không làm hỏng tính đúng đắn của chương trình.**

Ví dụ:

```python
class Animal:
    def eat(self):
        print("Eating")


class Dog(Animal):
    pass
```

Ta có:

```python
def feed(animal: Animal):
    animal.eat()
```

Có thể:

```python
dog = Dog()

feed(dog)
```

Không có vấn đề.

`Dog` thay thế được `Animal`.

---

# 3. LSP không đơn giản là `is-a`

Đây là điểm cực kỳ quan trọng.

Ví dụ:

```text
Dog is an Animal
Cat is an Animal
Bird is an Animal
```

Về mặt ngữ nghĩa:

```python
Dog(Animal)
```

có vẻ hợp lý.

Nhưng:

```text
is-a
```

chưa đảm bảo:

```text
behaviorally substitutable
```

Tức là:

```text
Dog is an Animal
```

chưa đủ.

Phải đảm bảo:

```text
Dog behaves like a valid Animal
```

theo contract mà `Animal` đưa ra.

---

# 4. Ví dụ kinh điển: Rectangle và Square

Ta thử thiết kế:

```python
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

Sau đó:

```python
class Square(Rectangle):

    def set_width(self, width):
        self.width = width
        self.height = width

    def set_height(self, height):
        self.width = height
        self.height = height
```

Nhìn qua có vẻ hợp lý:

```text
Square IS-A Rectangle
```

Nhưng vấn đề bắt đầu xuất hiện.

---

# 5. Một function yêu cầu Rectangle

```python
def resize_rectangle(rectangle: Rectangle):
    rectangle.set_width(10)
    rectangle.set_height(5)

    print(rectangle.area())
```

Với Rectangle:

```python
rectangle = Rectangle(2, 3)

resize_rectangle(rectangle)
```

Ta nhận được:

```text
50
```

Bởi vì:

```text
width = 10
height = 5

area = 10 * 5
     = 50
```

---

# 6. Nhưng với Square

```python
square = Square(2, 2)

resize_rectangle(square)
```

Sau:

```python
square.set_width(10)
```

ta có:

```text
width = 10
height = 10
```

Sau:

```python
square.set_height(5)
```

ta có:

```text
width = 5
height = 5
```

Area:

```text
25
```

Trong khi function đang làm việc với `Rectangle` và mong đợi:

```text
width = 10
height = 5
area = 50
```

Như vậy:

```text
Rectangle
    ↑
    |
Square
```

không còn thay thế được `Rectangle` trong mọi tình huống.

Đây là **LSP violation**.

---

# 7. Vấn đề thật sự nằm ở đâu?

Không phải Python.

Không phải inheritance syntax.

Không phải `super()`.

Vấn đề nằm ở **contract**.

`Rectangle` ngầm đưa ra contract:

```python
rectangle.set_width(10)
rectangle.set_height(5)
```

sẽ tạo:

```text
width = 10
height = 5
```

Nhưng `Square` phá contract đó:

```text
set_width()
```

đồng thời thay đổi `height`.

Do đó:

```text
Square
```

không còn hành xử theo contract của:

```text
Rectangle
```

---

# 8. Behavioral Contract

LSP thường được hiểu thông qua **contract**.

Một class cung cấp:

```text
Input
  ↓
Method
  ↓
Output
```

Subclass không được tùy tiện phá contract.

Có 3 ý quan trọng:

### 1. Preconditions

Điều kiện đầu vào.

Subclass không nên yêu cầu **nhiều điều kiện hơn** class cha.

Ví dụ base:

```python
def withdraw(amount):
    if amount > 0:
        ...
```

Subclass không nên đột nhiên yêu cầu:

```python
if amount > 100:
    ...
```

nếu contract của base cho phép `amount = 50`.

---

### 2. Postconditions

Điều kiện sau khi method chạy.

Subclass không nên làm giảm những đảm bảo mà base class đã cam kết.

Ví dụ:

```python
repository.save(entity)
```

Base contract:

```text
save thành công → entity tồn tại trong repository
```

Subclass không thể:

```python
def save(self, entity):
    print("Pretend saved")
```

nhưng thực tế không lưu gì.

---

### 3. Invariants

Invariant là điều kiện luôn phải được giữ đúng.

Ví dụ:

```text
BankAccount.balance >= 0
```

Nếu base class đảm bảo điều đó thì subclass không nên phá invariant.

---

# 9. Một ví dụ LSP violation rất thường gặp

```python
class Bird:

    def fly(self):
        print("Flying")
```

Sau đó:

```python
class Eagle(Bird):

    def fly(self):
        print("Eagle flying")
```

Ổn.

Nhưng:

```python
class Penguin(Bird):

    def fly(self):
        raise NotImplementedError
```

Ta có:

```python
def make_bird_fly(bird: Bird):
    bird.fly()
```

Với:

```python
eagle = Eagle()

make_bird_fly(eagle)
```

hoạt động.

Nhưng:

```python
penguin = Penguin()

make_bird_fly(penguin)
```

ném exception.

Như vậy:

```text
Penguin
```

không thể thay thế:

```text
Bird
```

theo contract của `Bird`.

---

# 10. Sửa bằng cách nào?

Đừng thiết kế:

```python
class Bird:
    def fly(self):
        ...
```

mà hãy tách abstraction.

Ví dụ:

```python
class Bird:
    def eat(self):
        print("Eating")
```

Sau đó:

```python
class FlyingBird(Bird):

    def fly(self):
        print("Flying")
```

Eagle:

```python
class Eagle(FlyingBird):

    def fly(self):
        print("Eagle flying")
```

Penguin:

```python
class Penguin(Bird):

    def eat(self):
        print("Penguin eating")
```

Bây giờ:

```text
Bird
├── FlyingBird
│   └── Eagle
│
└── Penguin
```

Hợp lý hơn.

---

# 11. LSP và Abstract Base Class

Bạn đã học `ABC`.

Ví dụ:

```python
from abc import ABC, abstractmethod


class Payment(ABC):

    @abstractmethod
    def pay(self, amount):
        pass
```

Các implementation:

```python
class CashPayment(Payment):

    def pay(self, amount):
        print(f"Cash: {amount}")


class CardPayment(Payment):

    def pay(self, amount):
        print(f"Card: {amount}")
```

Client:

```python
def checkout(payment: Payment, amount):
    payment.pay(amount)
```

Ta có:

```python
checkout(CashPayment(), 100)
checkout(CardPayment(), 100)
```

Nếu cả hai implementation tuân thủ contract:

```text
Payment
```

thì LSP được đảm bảo tốt.

---

# 12. Nhưng ABC không tự động đảm bảo LSP

Đây là lỗi tư duy rất phổ biến.

Ta viết:

```python
class Repository(ABC):

    @abstractmethod
    def save(self, entity):
        pass
```

Sau đó:

```python
class SQLiteRepository(Repository):

    def save(self, entity):
        print("Saved to SQLite")
```

và:

```python
class FakeRepository(Repository):

    def save(self, entity):
        raise NotImplementedError
```

Python vẫn cho phép:

```python
fake = FakeRepository()
```

Nếu contract yêu cầu:

```text
save()
```

phải lưu entity, thì `FakeRepository` này **vi phạm contract**.

Do đó:

```text
ABC
```

chỉ giúp xác định:

```text
method phải tồn tại
```

chứ không đảm bảo:

```text
behavior phải đúng
```

---

# 13. LSP trong Repository Pattern

Đây là phần đặc biệt quan trọng đối với project crawler của bạn.

Giả sử:

```python
from abc import ABC, abstractmethod


class StoryRepository(ABC):

    @abstractmethod
    def save(self, story):
        pass

    @abstractmethod
    def get(self, story_id):
        pass
```

Implementation:

```python
class SQLiteStoryRepository(StoryRepository):

    def save(self, story):
        ...

    def get(self, story_id):
        ...
```

Và:

```python
class MemoryStoryRepository(StoryRepository):

    def __init__(self):
        self.items = {}

    def save(self, story):
        self.items[story.id] = story

    def get(self, story_id):
        return self.items.get(story_id)
```

Client:

```python
class StoryService:

    def __init__(self, repository: StoryRepository):
        self.repository = repository

    def create(self, story):
        self.repository.save(story)
```

Ta có thể thay:

```python
service = StoryService(
    SQLiteStoryRepository()
)
```

bằng:

```python
service = StoryService(
    MemoryStoryRepository()
)
```

mà không cần sửa:

```python
StoryService
```

Đó là điều LSP mong muốn.

---

# 14. Repository violation

Giả sử:

```python
class FakeRepository(StoryRepository):

    def save(self, story):
        pass
```

Không lưu gì cả.

Trong test:

```python
repository = FakeRepository()

repository.save(story)

result = repository.get(story.id)
```

Có thể:

```text
None
```

Nếu contract của `StoryRepository` yêu cầu:

```text
save()
```

phải làm cho entity có thể được `get()` lại, thì FakeRepository này không còn tương thích.

Đây là một **LSP violation**.

---

# 15. LSP trong Crawler

Crawler của bạn có:

```text
Crawler
    ↓
Parser
```

Ta định nghĩa:

```python
from abc import ABC, abstractmethod


class StoryParser(ABC):

    @abstractmethod
    def parse(self, html):
        pass
```

Site A:

```python
class SiteAParser(StoryParser):

    def parse(self, html):
        return {
            "title": "Story A",
            "chapters": []
        }
```

Site B:

```python
class SiteBParser(StoryParser):

    def parse(self, html):
        return {
            "title": "Story B",
            "chapters": []
        }
```

Crawler:

```python
class Crawler:

    def __init__(self, parser: StoryParser):
        self.parser = parser

    def crawl(self, html):
        return self.parser.parse(html)
```

Ta có:

```python
crawler = Crawler(SiteAParser())
```

hoặc:

```python
crawler = Crawler(SiteBParser())
```

Crawler không cần biết parser cụ thể là gì.

---

# 16. Parser nào sẽ vi phạm LSP?

Ví dụ:

```python
class BrokenParser(StoryParser):

    def parse(self, html):
        raise RuntimeError("Not supported")
```

Nếu:

```python
Crawler
```

mong đợi:

```python
parser.parse(html)
```

luôn trả về:

```python
dict
```

thì:

```python
BrokenParser
```

không tuân thủ contract.

Một implementation khác:

```python
class BadParser(StoryParser):

    def parse(self, html):
        return "hello"
```

Cũng có vấn đề nếu contract yêu cầu:

```python
dict
```

---

# 17. Contract nên được xác định rõ

Thay vì:

```python
class StoryParser(ABC):

    @abstractmethod
    def parse(self, html):
        pass
```

ta có thể thiết kế rõ hơn:

```python
from dataclasses import dataclass


@dataclass
class ParsedStory:
    title: str
    chapters: list[str]
```

Parser:

```python
class StoryParser(ABC):

    @abstractmethod
    def parse(self, html: str) -> ParsedStory:
        pass
```

Site A:

```python
class SiteAParser(StoryParser):

    def parse(self, html: str) -> ParsedStory:
        return ParsedStory(
            title="Story A",
            chapters=["Chapter 1"]
        )
```

Site B:

```python
class SiteBParser(StoryParser):

    def parse(self, html: str) -> ParsedStory:
        return ParsedStory(
            title="Story B",
            chapters=["Chapter 1"]
        )
```

Contract rõ ràng hơn:

```text
Input:
    str

Output:
    ParsedStory
```

Điều này giúp giảm LSP violation.

---

# 18. LSP + OCP

Hai nguyên lý này liên quan rất chặt.

Ở Buổi 28:

```text
OCP
Open for extension
Closed for modification
```

Ta muốn:

```text
thêm implementation mới
        ↓
không sửa client
```

Nhưng điều đó chỉ thực sự an toàn nếu implementation mới tuân thủ LSP.

Ví dụ:

```text
PaymentService
      │
      ▼
 Payment
  ├── CashPayment
  ├── CardPayment
  ├── MoMoPayment
  └── PayPalPayment
```

OCP nói:

> Có thể thêm `MoMoPayment`.

LSP nói:

> `MoMoPayment` phải thực sự có thể thay thế `Payment`.

Nếu không:

```text
OCP
```

chỉ đúng trên giấy.

---

# 19. Một ví dụ rất thực tế

Giả sử:

```python
class FileStorage(ABC):

    @abstractmethod
    def save(self, filename, data):
        pass
```

Implementation:

```python
class LocalStorage(FileStorage):

    def save(self, filename, data):
        print(f"Save {filename}")
```

Cloud:

```python
class CloudStorage(FileStorage):

    def save(self, filename, data):
        print(f"Upload {filename}")
```

Client:

```python
class BackupService:

    def __init__(self, storage: FileStorage):
        self.storage = storage

    def backup(self, filename, data):
        self.storage.save(filename, data)
```

Có thể:

```python
BackupService(LocalStorage())
```

hoặc:

```python
BackupService(CloudStorage())
```

Nếu cả hai tuân thủ cùng contract:

```text
FileStorage
```

thì tốt.

---

# 20. Một dấu hiệu rất mạnh của LSP violation

Nếu bạn thấy:

```python
isinstance(...)
```

để xử lý subclass đặc biệt:

```python
def process(obj: Base):

    if isinstance(obj, SpecialChild):
        ...
```

hãy cảnh giác.

Ví dụ:

```python
def make_bird_fly(bird: Bird):

    if isinstance(bird, Penguin):
        return

    bird.fly()
```

Đây thường là dấu hiệu abstraction:

```text
Bird
```

đã thiết kế sai.

Client không nên phải biết:

```text
"À, nếu là Penguin thì xử lý riêng."
```

---

# 21. Một dấu hiệu khác

Subclass override:

```python
def method(self):
    raise NotImplementedError
```

Nếu base class đã public contract rằng method này có thể gọi được thì đây là dấu hiệu nguy hiểm.

Ví dụ:

```python
class Animal:

    def move(self):
        print("Moving")


class Fish(Animal):

    def move(self):
        raise NotImplementedError
```

Nếu tất cả `Animal` phải hỗ trợ:

```python
move()
```

thì abstraction có vấn đề.

---

# 22. LSP không có nghĩa subclass phải giống hệt

Điều này cũng rất quan trọng.

Ví dụ:

```python
class NotificationSender(ABC):

    @abstractmethod
    def send(self, message):
        pass
```

Email:

```python
class EmailSender(NotificationSender):

    def send(self, message):
        print("Sending email")
```

SMS:

```python
class SmsSender(NotificationSender):

    def send(self, message):
        print("Sending SMS")
```

Behavior bên trong khác nhau.

Điều đó **không vi phạm LSP**.

LSP không yêu cầu:

```text
implementation giống nhau
```

Nó yêu cầu:

```text
implementation tuân thủ cùng contract
```

---

# 23. LSP và Exception

Đây là phần rất quan trọng trong production code.

Giả sử:

```python
class Repository(ABC):

    @abstractmethod
    def get(self, id):
        pass
```

Contract:

```text
Không tìm thấy → return None
```

Implementation A:

```python
class SQLiteRepository(Repository):

    def get(self, id):
        return None
```

Implementation B:

```python
class MemoryRepository(Repository):

    def get(self, id):
        raise KeyError(id)
```

Nếu client viết:

```python
result = repository.get(10)

if result is None:
    print("Not found")
```

thì B phá contract.

Do đó LSP không chỉ liên quan đến:

```text
return value
```

mà còn liên quan đến:

```text
exception behavior
```

---

# 24. LSP và type

Ví dụ base:

```python
class Parser:

    def parse(self, html: str) -> dict:
        ...
```

Subclass:

```python
class BadParser(Parser):

    def parse(self, html: str) -> list:
        ...
```

Đây là dấu hiệu contract không tương thích.

Tốt hơn:

```python
class ParsedStory:
    ...
```

và mọi parser trả về:

```python
ParsedStory
```

---

# 25. LSP và Mutable State

Một nguồn violation khác là subclass thay đổi invariant.

Ví dụ:

```python
class Account:

    def __init__(self, balance):
        if balance < 0:
            raise ValueError

        self.balance = balance
```

Subclass:

```python
class SpecialAccount(Account):

    def __init__(self, balance):
        self.balance = -100
```

Nếu base contract:

```text
balance >= 0
```

thì subclass phá invariant.

---

# 26. Checklist phát hiện LSP violation

Khi tạo subclass, hãy hỏi:

### Câu 1

```text
Object subclass có thể đặt vào mọi nơi
base class được yêu cầu không?
```

### Câu 2

Subclass có yêu cầu input chặt hơn không?

```text
Base: nhận A, B, C

Child: chỉ nhận A
```

→ nguy hiểm.

### Câu 3

Subclass có trả về kết quả khác semantics không?

```text
Base → ParsedStory

Child → None
```

→ nguy hiểm.

### Câu 4

Subclass có thêm exception mà base không có không?

```text
Base → return None

Child → raise Exception
```

→ nguy hiểm.

### Câu 5

Subclass có phá invariant không?

### Câu 6

Client có phải kiểm tra:

```python
isinstance(obj, Child)
```

không?

Nếu có, cần xem lại abstraction.

---

# 27. LSP trong kiến trúc crawler của bạn

Một thiết kế tốt:

```text
                StoryParser
                    │
          ┌─────────┼─────────┐
          ↓         ↓         ↓
      SiteAParser SiteBParser SiteCParser
          │         │         │
          └─────────┼─────────┘
                    ↓
                 Crawler
```

Contract:

```python
class StoryParser(ABC):

    @abstractmethod
    def parse(self, html: str) -> ParsedStory:
        pass
```

Crawler:

```python
class Crawler:

    def __init__(self, parser: StoryParser):
        self.parser = parser

    def crawl(self, html: str) -> ParsedStory:
        return self.parser.parse(html)
```

Crawler không cần:

```python
if SiteA:
    ...

elif SiteB:
    ...

elif SiteC:
    ...
```

Đây chính là nền tảng cho:

```text
OCP
+
LSP
+
DI
+
Plugin Architecture
```

---

# 28. LSP + Testing

Một cách rất tốt để kiểm tra LSP là viết **contract test**.

Ví dụ:

```python
def repository_contract(repository):
    story = Story(
        id=1,
        title="Test"
    )

    repository.save(story)

    result = repository.get(1)

    assert result is not None
    assert result.id == 1
    assert result.title == "Test"
```

Sau đó chạy với SQLite:

```python
repository_contract(
    SQLiteStoryRepository()
)
```

và Memory:

```python
repository_contract(
    MemoryStoryRepository()
)
```

Nếu cả hai đều pass:

```text
SQLiteRepository
MemoryRepository
```

có khả năng cao đang tuân thủ cùng contract.

Đây là kỹ thuật rất hữu ích khi xây:

```text
Repository Pattern
```

---

# 29. Một kiến trúc tốt

Ta có:

```text
                 Repository
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
 SQLiteRepository MemoryRepository FakeRepository
```

Contract test:

```text
Repository Contract
       │
       ├── SQLite
       ├── Memory
       └── Fake
```

Mỗi implementation phải thỏa:

```text
same input semantics
same output semantics
same error semantics
same invariant
```

Đây là cách áp dụng LSP rất thực tế.

---

# 30. Inheritance hay Composition?

Một câu hỏi quan trọng sau khi học LSP:

> Nếu inheritance gây vấn đề thì làm gì?

Không nhất thiết phải cố sửa inheritance.

Có thể dùng:

```text
Composition
```

Ví dụ thay vì:

```python
class Penguin(Bird):
    ...
```

với một abstraction không phù hợp, ta có thể thiết kế behavior:

```python
class FlyBehavior:

    def fly(self):
        print("Flying")
```

và:

```python
class NoFlyBehavior:

    def fly(self):
        print("Cannot fly")
```

Sau đó:

```python
class Bird:

    def __init__(self, fly_behavior):
        self.fly_behavior = fly_behavior

    def fly(self):
        self.fly_behavior.fly()
```

Đây chính là hướng tư duy sẽ dẫn tới:

```text
Strategy Pattern
```

mà bạn sẽ học ở **Buổi 35**.

---

# 31. LSP và nguyên tắc “Favor Composition”

Ta có thể nhìn toàn bộ quá trình:

```text
Inheritance
    ↓
LSP violation
    ↓
Abstraction không đúng
    ↓
Tách interface
hoặc
Composition
    ↓
Strategy
```

Do đó LSP giúp bạn nhận ra:

> **Không phải quan hệ “is-a” nào cũng nên biểu diễn bằng inheritance.**

---

# 32. So sánh 3 tình huống

| Thiết kế                                                | LSP |
| ------------------------------------------------------- | --- |
| `Dog → Animal`, giữ contract                            | ✅   |
| `Square → Rectangle`, phá behavior                      | ❌   |
| `Penguin → Bird`, trong khi Bird bắt buộc `fly()`       | ❌   |
| `SiteAParser → StoryParser`, cùng contract              | ✅   |
| `SiteBParser → StoryParser`, trả kết quả khác semantics | ❌   |
| `MemoryRepository → Repository`, cùng contract          | ✅   |

---

# 33. LSP trong SOLID

Đến đây bạn đã có:

```text
S — Single Responsibility
    ↓
O — Open Closed
    ↓
L — Liskov Substitution
```

Có thể hiểu:

### SRP

Mỗi component có trách nhiệm rõ ràng.

```text
Crawler
Parser
Repository
Logger
```

### OCP

Có thể mở rộng:

```text
SiteAParser
SiteBParser
SiteCParser
```

### LSP

Những implementation đó phải thực sự thay thế được abstraction:

```text
StoryParser
```

Nếu không:

```text
OCP
```

sẽ trở nên nguy hiểm.

---

# 34. Quy tắc tư duy quan trọng

Khi viết:

```python
class Child(Parent):
    ...
```

đừng chỉ hỏi:

> “Child có phải Parent không?”

Hãy hỏi:

> **“Nếu một function nhận Parent, nó có thể nhận Child mà không cần biết Child là gì không?”**

Ví dụ:

```python
def process(parser: StoryParser):
    result = parser.parse(html)
```

Nếu function này chạy bình thường với:

```python
SiteAParser()
SiteBParser()
SiteCParser()
```

thì abstraction có chất lượng tốt.

---

# 35. Bài tập 1 — Rectangle/Square

Cho code:

```python
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


class Square(Rectangle):

    def set_width(self, width):
        self.width = width
        self.height = width

    def set_height(self, height):
        self.width = height
        self.height = height
```

Hãy giải thích:

```python
def calculate(rectangle):
    rectangle.set_width(10)
    rectangle.set_height(5)
    return rectangle.area()
```

Tại sao function này có thể cho kết quả khác nhau tùy object?

---

# 36. Bài tập 2 — Bird

Thiết kế lại:

```python
class Bird:
    def fly(self):
        pass
```

để:

```text
Eagle
Penguin
Ostrich
```

không vi phạm LSP.

Gợi ý:

```text
Bird
FlyingBird
```

---

# 37. Bài tập 3 — Repository

Thiết kế:

```python
class StoryRepository(ABC):
    ...
```

với:

```text
SQLiteStoryRepository
MemoryStoryRepository
FakeStoryRepository
```

Contract:

```text
save(story)
get(id)
delete(id)
```

Sau đó viết:

```python
def repository_contract(repository):
    ...
```

để kiểm tra cả 3 implementation.

Đây là bài tập **rất quan trọng** đối với project crawler của bạn.

---

# 38. Bài tập 4 — Parser

Thiết kế:

```text
StoryParser
    ├── SiteAParser
    ├── SiteBParser
    └── SiteCParser
```

Contract:

```python
parse(html: str) -> ParsedStory
```

Yêu cầu:

* Không `if site == ...` trong Crawler
* Parser nào cũng trả về `ParsedStory`
* Không parser nào phá contract
* Viết contract test

---

# 39. Bài tập 5 — Kiến trúc

Cho:

```text
Crawler
   ↓
Parser
   ↓
Repository
```

Thiết kế sao cho:

```text
Crawler
   ↓
StoryParser
   ├── SiteAParser
   ├── SiteBParser
   └── SiteCParser

Crawler
   ↓
StoryRepository
   ├── SQLiteRepository
   └── MemoryRepository
```

và chứng minh:

```text
Parser → LSP
Repository → LSP
```

đồng thời:

```text
Crawler → OCP
Crawler → DI
```

Đây là bài tập kết hợp **Buổi 24 → 29**.

---

# 40. Tổng kết Buổi 29

Điểm cốt lõi nhất:

```text
LSP
│
├── Subclass phải thay thế được Base class
│
├── Không phá contract
│
├── Không tăng precondition
│
├── Không giảm postcondition
│
├── Giữ invariant
│
├── Không thay đổi semantics
│
└── Không bắt client xử lý subclass đặc biệt
```

Và tư duy quan trọng nhất:

```text
"is-a"
   ≠
"behaviorally substitutable"
```

Một inheritance hierarchy tốt không chỉ cần:

```text
đúng về mặt ngữ nghĩa
```

mà còn phải:

```text
đúng về mặt hành vi
```

Đặc biệt trong kiến trúc crawler:

```text
              StoryParser
             /     |      \
            /      |       \
       SiteA    SiteB    SiteC
          \       |       /
           \      |      /
              Crawler
```

Nếu mọi parser tuân thủ cùng contract, bạn có được:

```text
OCP + LSP + DI + Plugin Architecture
```

Đây là nền tảng rất quan trọng trước khi sang **Buổi 30 — Interface Segregation Principle (ISP)**.
