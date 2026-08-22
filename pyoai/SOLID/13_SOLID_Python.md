# Buổi 13 — SOLID + Python

Hôm nay chúng ta chuyển từ **SOLID ở mức OOP/class** sang cách tư duy SOLID **đúng với Python**.

Điểm quan trọng nhất:

> **SOLID không yêu cầu Python phải trở thành Java.**

Python có những cơ chế rất mạnh như:

```text
Duck Typing
Protocol
First-class Function
Higher-order Function
Composition
Dataclass
typing
```

Những cơ chế này cho phép chúng ta áp dụng SOLID theo cách **Pythonic hơn**, ít inheritance hơn và thường ít boilerplate hơn.

---

# 1. SOLID trong Python khác gì?

Trong một ngôn ngữ thiên về class/inheritance, người ta dễ thiết kế:

```text
Interface
   ↑
Abstract Class
   ↑
Concrete Class
```

Python thường có thể đơn giản hơn:

```text
Contract
   ↑
Object có đủ behavior
```

Ví dụ:

```python
class EmailSender:

    def send(self, message: str) -> None:
        print(f"Email: {message}")
```

Ta không nhất thiết cần:

```python
class EmailSender(EmailSenderInterface):
    ...
```

Nếu object có method cần thiết, Python có thể sử dụng nó.

Đó là **Duck Typing**.

---

# 2. Duck Typing

Triết lý:

> "Nếu nó đi như vịt và kêu như vịt, hãy coi nó như vịt."

Ví dụ:

```python
class FileLogger:

    def write(self, message: str):
        print(f"FILE: {message}")
```

```python
class ConsoleLogger:

    def write(self, message: str):
        print(f"CONSOLE: {message}")
```

Một function:

```python
def log(logger, message: str):
    logger.write(message)
```

Không cần:

```python
LoggerBase
LoggerInterface
ABC
```

Sử dụng:

```python
log(
    FileLogger(),
    "Hello",
)

log(
    ConsoleLogger(),
    "Hello",
)
```

---

# 3. Đây có phải DIP không?

Có thể.

Dependency của:

```python
def log(logger, message):
```

không phải:

```text
FileLogger
```

mà là capability:

```text
logger.write()
```

Ta đang phụ thuộc vào behavior.

Đây là một cách rất Pythonic để thực hiện abstraction.

---

# 4. Nhưng Duck Typing có vấn đề

IDE/type checker không biết chắc:

```python
logger.write(...)
```

có tồn tại hay không.

Ví dụ:

```python
class BrokenLogger:

    def save(self, message):
        ...
```

Nếu:

```python
log(
    BrokenLogger(),
    "hello",
)
```

sẽ lỗi runtime.

Đây là lúc `Protocol` rất hữu ích.

---

# 5. Protocol

```python
from typing import Protocol


class Logger(Protocol):

    def write(self, message: str) -> None:
        ...
```

Function:

```python
def log(
    logger: Logger,
    message: str,
):
    logger.write(message)
```

Implementation:

```python
class ConsoleLogger:

    def write(self, message: str) -> None:
        print(message)
```

Không cần inheritance.

```python
logger = ConsoleLogger()

log(logger, "Hello")
```

`ConsoleLogger` tương thích với `Logger` vì nó có đúng behavior.

---

# 6. Protocol = Structural Typing

Đây là điểm rất quan trọng.

ABC thường sử dụng:

```text
nominal typing
```

tức là:

```python
class ConsoleLogger(Logger):
    ...
```

Trong khi Protocol dùng:

```text
structural typing
```

Chỉ cần structure phù hợp.

```text
Logger Protocol
    │
    └── write(message)

ConsoleLogger
    │
    └── write(message)
```

Python có thể coi chúng compatible.

---

# 7. Protocol + OCP

Ví dụ:

```python
class PaymentGateway(Protocol):

    def charge(self, amount: int) -> None:
        ...
```

Stripe:

```python
class StripePayment:

    def charge(self, amount: int) -> None:
        ...
```

Momo:

```python
class MomoPayment:

    def charge(self, amount: int) -> None:
        ...
```

Service:

```python
class PaymentService:

    def __init__(
        self,
        gateway: PaymentGateway,
    ):
        self.gateway = gateway

    def pay(self, amount: int):
        self.gateway.charge(amount)
```

Thêm:

```python
class PayPalPayment:

    def charge(self, amount: int) -> None:
        ...
```

Không cần sửa `PaymentService`.

Ta có:

```text
Protocol
   ↑
   ├── Stripe
   ├── Momo
   └── PayPal
```

---

# 8. Protocol + ISP

Đây là nơi Protocol rất mạnh.

Thay vì:

```python
class Crawler(Protocol):

    def crawl(self): ...
    def parse(self): ...
    def download(self): ...
    def login(self): ...
    def upload(self): ...
    def notify(self): ...
```

Ta tách:

```python
class Crawler(Protocol):

    def crawl(self): ...
```

```python
class Parser(Protocol):

    def parse(self, html): ...
```

```python
class Downloader(Protocol):

    def download(self, url): ...
```

Đây chính là:

```text
ISP
+
Protocol
```

---

# 9. Protocol + DIP

Application:

```python
class CrawlUseCase:

    def __init__(
        self,
        crawler: Crawler,
    ):
        self.crawler = crawler
```

Infrastructure:

```python
class SiteACrawler:

    def crawl(self):
        ...
```

Application không cần:

```python
from infrastructure.site_a import SiteACrawler
```

Nó chỉ biết:

```text
Crawler Protocol
```

Đây là DIP rất tự nhiên trong Python.

---

# 10. ABC

Python vẫn có `ABC`.

```python
from abc import ABC, abstractmethod


class PaymentGateway(ABC):

    @abstractmethod
    def charge(self, amount: int) -> None:
        ...
```

Implementation:

```python
class StripePayment(PaymentGateway):

    def charge(self, amount: int) -> None:
        print("Stripe")
```

---

# 11. Protocol vs ABC

|                         | Protocol | ABC       |
| ----------------------- | -------- | --------- |
| Structural typing       | ✅        | ❌         |
| Inheritance bắt buộc    | ❌        | thường có |
| Runtime abstraction     | hạn chế  | mạnh      |
| Duck typing             | ⭐⭐⭐⭐⭐    | ⭐⭐        |
| Pythonic flexibility    | ⭐⭐⭐⭐⭐    | ⭐⭐⭐       |
| Shared implementation   | hạn chế  | ✅         |
| Framework/base behavior | ⭐⭐       | ⭐⭐⭐⭐⭐     |

Một quy tắc thực tế:

> Nếu bạn chỉ cần **contract** → cân nhắc `Protocol`.

> Nếu bạn cần **shared behavior + lifecycle + inheritance** → `ABC` có thể phù hợp hơn.

---

# 12. Đừng dùng ABC chỉ vì SOLID

Ví dụ:

```python
class UserRepository(ABC):

    @abstractmethod
    def save(self):
        ...
```

Nếu mục tiêu duy nhất là:

```text
UserRepository là contract
```

thì:

```python
class UserRepository(Protocol):

    def save(self, user) -> None:
        ...
```

có thể đơn giản hơn.

---

# 13. First-class Function

Đây là một điểm rất Pythonic.

Trong Python:

```python
def add(a, b):
    return a + b
```

function là object.

Có thể:

```python
operation = add
```

và:

```python
operation(1, 2)
```

Có thể truyền function:

```python
def execute(operation, a, b):
    return operation(a, b)
```

```python
execute(add, 10, 20)
```

---

# 14. Function cũng có thể thay Strategy

Đây là một insight rất quan trọng.

Ta thường học Strategy như:

```text
Strategy
   ↑
 ┌─┴────────┐
Add       Multiply
```

Nhưng Python có thể viết:

```python
def add(a, b):
    return a + b


def multiply(a, b):
    return a * b
```

Sau đó:

```python
def calculate(
    operation,
    a,
    b,
):
    return operation(a, b)
```

Sử dụng:

```python
calculate(add, 2, 3)

calculate(multiply, 2, 3)
```

Không cần class.

---

# 15. Strategy bằng function

Đây là một trong những cách áp dụng OCP rất Pythonic.

```python
from collections.abc import Callable


Operation = Callable[[int, int], int]


def calculate(
    operation: Operation,
    a: int,
    b: int,
) -> int:
    return operation(a, b)
```

Implementation:

```python
def add(a: int, b: int) -> int:
    return a + b
```

```python
def multiply(a: int, b: int) -> int:
    return a * b
```

Sử dụng:

```python
calculate(add, 2, 3)

calculate(multiply, 2, 3)
```

Đây vẫn là Strategy.

Chỉ là:

> **Strategy được biểu diễn bằng function thay vì class.**

---

# 16. Higher-order Function

Function được gọi là higher-order function khi nó:

* nhận function làm argument
* hoặc trả về function

Ví dụ:

```python
def apply(
    operation,
    value,
):
    return operation(value)
```

Function:

```python
def double(x):
    return x * 2
```

Sử dụng:

```python
apply(double, 10)
```

---

# 17. Function Factory

Function cũng có thể tạo function:

```python
def make_multiplier(n):

    def multiply(x):
        return x * n

    return multiply
```

Sau đó:

```python
double = make_multiplier(2)

triple = make_multiplier(3)
```

```python
double(10)
# 20

triple(10)
# 30
```

Đây chính là một dạng:

```text
Factory
```

nhưng factory tạo **function**.

---

# 18. SOLID không yêu cầu Class

Đây là một insight rất quan trọng.

Ví dụ SRP:

```python
def parse_story(html):
    ...


def validate_story(story):
    ...


def save_story(story):
    ...
```

Mỗi function có responsibility rõ ràng.

Không cần:

```text
StoryParser
StoryValidator
StorySaver
```

trong mọi trường hợp.

---

# 19. SRP + Function

Code:

```python
def process_story(html):

    soup = BeautifulSoup(html)

    story = parse(soup)

    validate(story)

    save(story)
```

Có thể tách:

```text
parse
validate
save
```

Nhưng `process_story()` vẫn là một orchestration function.

Đây có thể là thiết kế rất tốt.

---

# 20. Composition

Python thường thích:

> **Composition over inheritance**

Ví dụ:

```python
class Crawler:

    def __init__(
        self,
        downloader,
        parser,
        repository,
    ):
        self.downloader = downloader
        self.parser = parser
        self.repository = repository
```

Crawler được tạo từ:

```text
Downloader
Parser
Repository
```

Không cần:

```text
BaseCrawler
   ↑
SiteCrawler
   ↑
AdvancedSiteCrawler
   ↑
...
```

---

# 21. Composition + DIP

```python
class CrawlUseCase:

    def __init__(
        self,
        downloader,
        parser,
        repository,
    ):
        self.downloader = downloader
        self.parser = parser
        self.repository = repository
```

Dependencies được inject.

```text
CrawlUseCase
 ├── Downloader
 ├── Parser
 └── Repository
```

Đây là DIP + Composition.

---

# 22. Composition + SRP

Mỗi object:

```text
Downloader → download
Parser     → parse
Repository → persistence
```

Use case:

```text
CrawlUseCase → orchestration
```

Không object nào cần biết quá nhiều.

---

# 23. Dataclass

`dataclass` không phải SOLID principle.

Nó là một công cụ Python rất hữu ích để biểu diễn:

```text
data
state
configuration
Value Object
DTO
```

Ví dụ:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class UserId:

    value: int
```

Đây có thể là Value Object.

---

# 24. Dataclass + SRP

Ví dụ:

```python
@dataclass
class User:

    id: int
    name: str
    email: str
```

Object này chủ yếu biểu diễn state.

Đừng ép nó làm:

```text
database
HTTP
email
logging
```

Chúng ta giữ responsibility rõ ràng.

---

# 25. Dataclass + Immutability

```python
@dataclass(frozen=True)
class Money:

    amount: int
    currency: str
```

Không thể:

```python
money.amount = 100
```

Value Object thường hưởng lợi từ immutable design.

Điều này đặc biệt hữu ích khi kết hợp:

```text
DDD
+
SOLID
+
dataclass
```

---

# 26. typing

Python typing giúp làm rõ abstraction.

Ví dụ:

```python
from typing import Protocol


class UserRepository(Protocol):

    def get_by_id(
        self,
        user_id: int,
    ) -> "User | None":
        ...
```

Không chỉ để IDE.

Typing giúp developer hiểu:

```text
UserService cần capability gì?
```

---

# 27. `Callable`

Nếu dependency là function:

```python
from collections.abc import Callable
```

Ví dụ:

```python
Formatter = Callable[[str], str]
```

Function:

```python
def uppercase(value: str) -> str:
    return value.upper()
```

Service:

```python
class TextService:

    def __init__(
        self,
        formatter: Formatter,
    ):
        self.formatter = formatter
```

Đây là DIP bằng function.

---

# 28. Protocol vs Callable

Nếu dependency chỉ là:

```text
một function
```

thì:

```python
Callable
```

thường đủ.

Ví dụ:

```python
Formatter = Callable[[str], str]
```

Nếu dependency có nhiều operations:

```text
get()
save()
delete()
```

thì:

```python
Protocol
```

thường phù hợp hơn.

---

# 29. Function Dependency Injection

Đây là một kỹ thuật rất Pythonic.

```python
def send_email(to, message):
    ...


class UserService:

    def __init__(
        self,
        send_notification,
    ):
        self.send_notification = send_notification
```

Test:

```python
def fake_notification(to, message):
    ...
```

Inject:

```python
service = UserService(
    fake_notification
)
```

Không cần:

```text
NotificationService
NotificationInterface
NotificationFactory
```

nếu vấn đề đơn giản.

---

# 30. Một nguyên tắc cực kỳ quan trọng

> **Abstraction càng đơn giản càng tốt.**

Nếu cần:

```text
function
```

hãy dùng function.

Nếu cần:

```text
object + vài methods
```

hãy cân nhắc Protocol.

Nếu cần:

```text
shared implementation + lifecycle
```

hãy cân nhắc ABC.

Không nên:

```text
function
   ↓
ABC
   ↓
3 abstract classes
   ↓
Factory
   ↓
Container
```

chỉ để gọi:

```python
send_email()
```

---

# 31. Pythonic SOLID

Ta có thể hình dung:

```text
                  SOLID
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
     Function    Protocol     ABC
        │           │           │
        ↓           ↓           ↓
    simple       contract     shared
    behavior     boundary     behavior
```

Và:

```text
Composition
    ↓
Dependency Injection
    ↓
Protocol / Callable
    ↓
Polymorphism
```

---

# 32. Ví dụ hoàn chỉnh

Ta xây một `StoryProcessor`.

Requirement:

```text
HTML
 ↓
Parser
 ↓
Validator
 ↓
Repository
```

---

## Parser

```python
from typing import Protocol


class StoryParser(Protocol):

    def parse(self, html: str):
        ...
```

---

## Validator

```python
class StoryValidator(Protocol):

    def validate(self, story) -> None:
        ...
```

---

## Repository

```python
class StoryRepository(Protocol):

    def save(self, story) -> None:
        ...
```

---

## Use Case

```python
class ProcessStory:

    def __init__(
        self,
        parser: StoryParser,
        validator: StoryValidator,
        repository: StoryRepository,
    ):
        self.parser = parser
        self.validator = validator
        self.repository = repository

    def execute(self, html: str):

        story = self.parser.parse(html)

        self.validator.validate(story)

        self.repository.save(story)

        return story
```

Đây là:

```text
SRP
OCP
ISP
DIP
```

được thể hiện bằng:

```text
Protocol
Composition
Dependency Injection
```

---

# 33. Nhưng Python còn có thể đơn giản hơn

Nếu parser chỉ là một function:

```python
def parse_story(html: str):
    ...
```

thì:

```python
from collections.abc import Callable


Parser = Callable[[str], object]
```

Use case:

```python
class ProcessStory:

    def __init__(
        self,
        parser: Parser,
        validator,
        repository,
    ):
        ...
```

Không nhất thiết phải tạo:

```python
class BeautifulSoupParser:
    ...
```

---

# 34. Khi nào nên dùng class?

Dùng class khi có:

```text
state
+
behavior
```

hoặc:

```text
nhiều related operations
```

Ví dụ:

```python
class SQLiteStoryRepository:

    def __init__(self, connection):
        self.connection = connection

    def save(self, story):
        ...

    def get_by_id(self, story_id):
        ...

    def delete(self, story_id):
        ...
```

Ở đây class hợp lý.

---

# 35. Khi nào function tốt hơn?

Ví dụ:

```python
def normalize_title(title: str) -> str:
    return " ".join(title.split())
```

Đừng tạo:

```python
class TitleNormalizer:
    def normalize(self, title):
        ...
```

chỉ vì:

> "SOLID yêu cầu abstraction."

Không.

Function đã đủ tốt.

---

# 36. SOLID + Python: Composition over Inheritance

Thay vì:

```text
BaseCrawler
    ↑
SiteCrawler
    ↑
SpecialSiteCrawler
```

có thể:

```text
Crawler
 ├── downloader
 ├── parser
 ├── validator
 └── repository
```

Mỗi dependency có thể thay thế độc lập.

Đây là:

```text
Composition
+
DIP
+
ISP
+
OCP
```

---

# 37. Đây là điểm khác biệt lớn với Java-style SOLID

Python cho phép:

```python
def process(strategy):
    ...
```

thay vì:

```text
IStrategy
AbstractStrategy
ConcreteStrategy
StrategyFactory
```

Python cho phép:

```python
Protocol
```

thay vì bắt buộc inheritance.

Python cho phép:

```python
Callable
```

thay vì class cho behavior đơn giản.

Python cho phép:

```python
duck typing
```

thay vì interface cho mọi thứ.

---

# 38. Nhưng đừng hiểu sai

Pythonic ≠ không cần abstraction.

Một hệ thống lớn như:

```text
Crawler
Database
Queue
HTTP
Plugin
```

vẫn cần abstraction.

Ví dụ:

```text
Crawler
    ↓
Crawler Protocol

UseCase
    ↓
Repository Protocol

UseCase
    ↓
HttpClient Protocol
```

Abstraction rất có giá trị ở **boundary**.

---

# 39. Quy tắc chọn abstraction

Tôi khuyên bạn dùng decision tree này:

```text
Dependency chỉ là một operation?
        │
       YES
        ↓
     Callable
        │
       NO
        ↓
Có nhiều operations?
        │
       YES
        ↓
    Protocol
        │
        ↓
Cần shared implementation?
        │
       YES
        ↓
       ABC
```

Không phải luật tuyệt đối, nhưng rất hữu ích.

---

# 40. Python SOLID Checklist

Khi viết code mới, hỏi:

### SRP

```text
Function/class này có một responsibility rõ không?
```

### OCP

```text
Variation có thể inject/compose không?
```

### LSP

```text
Implementation có thực sự thay thế contract không?
```

### ISP

```text
Protocol có nhỏ không?
```

### DIP

```text
Business code có import infrastructure không?
```

### Python

```text
Có cần class không?
Có thể dùng function không?
Có thể dùng Protocol không?
Có thể composition thay inheritance không?
```

---

# 41. Bài tập 1 — Strategy bằng Function

Viết:

```python
def calculate(operation, a, b):
    ...
```

Hỗ trợ:

```text
add
subtract
multiply
divide
```

Không được dùng class.

Sau đó thêm:

```text
power
```

mà không sửa `calculate()`.

---

# 42. Bài tập 2 — Protocol

Thiết kế:

```text
FileStorage
```

với:

```text
save()
load()
delete()
```

Implementation:

```text
LocalFileStorage
MemoryFileStorage
```

Dùng `Protocol`.

---

# 43. Bài tập 3 — Callable DI

Thiết kế:

```python
class TextProcessor:
    ...
```

Dependency:

```text
normalizer: Callable
```

Cho phép:

```python
lowercase
uppercase
titlecase
```

mà không sửa `TextProcessor`.

---

# 44. Bài tập 4 — Composition

Thiết kế:

```text
StoryService
```

nhận:

```text
Parser
Validator
Repository
```

Không được inheritance.

---

# 45. Bài tập 5 — Refactoring

Code ban đầu:

```python
class StoryManager:

    def process(self, html):

        soup = BeautifulSoup(html)

        title = soup.find("h1").text

        if not title:
            raise ValueError()

        conn = sqlite3.connect("story.db")

        conn.execute(
            "INSERT INTO stories(title) VALUES (?)",
            (title,),
        )

        conn.commit()
```

Hãy refactor thành:

```text
StoryService
     ↓
Parser
     ↓
Validator
     ↓
Repository
```

và dùng:

```text
Protocol
dataclass
Dependency Injection
Composition
```

---

# 46. Bài tập lớn — Pythonic SOLID

Thiết kế:

```text
Story Processing Framework
```

Architecture:

```text
             ProcessStory
                  │
       ┌──────────┼──────────┐
       ↓          ↓          ↓
    Parser     Validator   Repository
       ↑          ↑          ↑
    Protocol   Protocol    Protocol
```

Domain model:

```python
@dataclass(frozen=True)
class Story:
    id: int
    title: str
```

Infrastructure:

```text
BeautifulSoupParser
SQLiteStoryRepository
```

Testing:

```text
FakeParser
FakeRepository
FakeValidator
```

Không inheritance nếu không cần.

---

# 47. Insight quan trọng nhất của Buổi 13

Sau khi học SOLID + Python, hãy bỏ tư duy:

```text
SOLID
 ↓
interface
 ↓
abstract class
 ↓
inheritance
```

và thay bằng:

```text
SOLID
 ↓
boundary
 ↓
contract
 ↓
composition
 ↓
dependency injection
 ↓
Protocol / Callable / Function
```

Đây là cách áp dụng SOLID **Pythonic** hơn.

---

# 48. Mental Model cuối buổi

```text
                  PYTHON
                    │
       ┌────────────┼────────────┐
       ↓            ↓            ↓
    Function      Protocol       ABC
       │            │            │
       ↓            ↓            ↓
  simple behavior  contract   shared behavior
       │            │            │
       └────────────┼────────────┘
                    ↓
               Composition
                    ↓
             Dependency Injection
                    ↓
                  SOLID
```

Và một câu tôi muốn bạn nhớ:

> **Trong Python, abstraction không nhất thiết phải là class.**

Có thể là:

```python
function
```

hoặc:

```python
Callable
```

hoặc:

```python
Protocol
```

hoặc:

```python
ABC
```

hoặc thậm chí đơn giản là:

```text
duck typing
```

Tùy boundary và mức độ phức tạp của hệ thống.

---

## Roadmap

```text
PHẦN V — SOLID kết hợp

✅ Buổi 12 — SOLID + Design Patterns
✅ Buổi 13 — SOLID + Python
⬜ Buổi 14 — SOLID + Testing
⬜ Buổi 15 — SOLID + DDD

PHẦN VI — SOLID trong Clean Architecture

⬜ Buổi 16 — Clean Architecture
⬜ Buổi 17 — CLI → Application → Domain → Repository → SQLite
⬜ Buổi 18 — Crawler → Use Case → Crawler Interface → Plugin
⬜ Buổi 19 — Refactoring CrawlerManager
```

**Buổi 14 sẽ rất thực chiến:** chúng ta sẽ dùng `Unit Test`, `Mock`, `Stub`, `Fake`, Dependency Injection để chứng minh một điều quan trọng: **một architecture tốt không chỉ dễ đọc — nó phải dễ test**.
