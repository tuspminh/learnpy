# Python OOP Master — Buổi 35

# Strategy Pattern

Hôm nay chúng ta học một Pattern rất quan trọng:

> **Strategy Pattern — đóng gói một nhóm thuật toán/behavior có thể thay thế cho nhau và cho phép chọn strategy tại runtime.**

Đây là Pattern cực kỳ phù hợp với project crawler của bạn, đặc biệt cho:

```text
Retry
Parser
Storage
Request policy
Rate limiting
Sorting
Notification
```

---

# 1. Mục tiêu

Sau buổi này bạn sẽ hiểu:

* Strategy Pattern là gì?
* Tại sao cần Strategy?
* Strategy giải quyết `if/elif` như thế nào?
* Strategy + Polymorphism
* Strategy + Composition
* Strategy + Dependency Injection
* Strategy + OCP
* Strategy với ABC
* Strategy với Duck Typing / Protocol
* Chọn Strategy runtime
* Strategy cho Retry
* Strategy cho Crawler
* Strategy vs Factory
* Strategy vs State
* Khi nào không nên dùng Strategy

---

# 2. Strategy Pattern là gì?

Strategy Pattern cho phép chúng ta:

> **Định nghĩa nhiều thuật toán khác nhau cho cùng một nhiệm vụ, đóng gói chúng thành các object riêng biệt và thay đổi thuật toán mà không sửa client.**

Ví dụ:

```text
Payment
├── CreditCard
├── PayPal
└── MoMo
```

hoặc crawler:

```text
RetryStrategy
├── NoRetry
├── FixedRetry
└── ExponentialBackoff
```

Client chỉ biết:

```text
RetryStrategy
```

không cần biết implementation cụ thể.

---

# 3. Ví dụ đơn giản nhất

Giả sử có chương trình tính giá vận chuyển.

Có:

```text
Standard Shipping
Express Shipping
Free Shipping
```

Cách đầu tiên rất dễ viết:

```python
class Shipping:

    def calculate(self, method, weight):

        if method == "standard":
            return weight * 10

        elif method == "express":
            return weight * 30

        elif method == "free":
            return 0

        raise ValueError("Unknown method")
```

Ban đầu không vấn đề.

Nhưng sau này:

```text
standard
express
free
same_day
international
drone
pickup
...
```

`if/elif` ngày càng lớn.

---

# 4. Strategy giải quyết thế nào?

Tách từng thuật toán:

```python
class StandardShipping:

    def calculate(self, weight):
        return weight * 10
```

```python
class ExpressShipping:

    def calculate(self, weight):
        return weight * 30
```

```python
class FreeShipping:

    def calculate(self, weight):
        return 0
```

Sau đó:

```python
class ShippingService:

    def __init__(self, strategy):
        self.strategy = strategy

    def calculate(self, weight):
        return self.strategy.calculate(weight)
```

Sử dụng:

```python
service = ShippingService(
    StandardShipping()
)

print(service.calculate(5))
```

---

# 5. Kiến trúc

```text
              ShippingService
                     │
                     ↓
              ShippingStrategy
                 ↑    ↑    ↑
                 │    │    │
             Standard Express Free
```

`ShippingService` không biết:

```text
StandardShipping
ExpressShipping
FreeShipping
```

nó chỉ cần biết:

```text
ShippingStrategy
```

---

# 6. Strategy chính là Polymorphism

Ta có:

```python
class ShippingStrategy:
    def calculate(self, weight):
        ...
```

Các implementation:

```python
class StandardShipping:
    def calculate(self, weight):
        return weight * 10


class ExpressShipping:
    def calculate(self, weight):
        return weight * 30
```

Client:

```python
class ShippingService:

    def __init__(self, strategy):
        self.strategy = strategy

    def calculate(self, weight):
        return self.strategy.calculate(weight)
```

Ta có thể thay:

```python
ShippingService(StandardShipping())
```

bằng:

```python
ShippingService(ExpressShipping())
```

mà `ShippingService` không thay đổi.

Đây chính là:

```text
Strategy
    +
Polymorphism
```

---

# 7. Strategy với ABC

Ta có thể định nghĩa contract rõ ràng:

```python
from abc import ABC, abstractmethod


class ShippingStrategy(ABC):

    @abstractmethod
    def calculate(self, weight):
        pass
```

Concrete strategies:

```python
class StandardShipping(ShippingStrategy):

    def calculate(self, weight):
        return weight * 10
```

```python
class ExpressShipping(ShippingStrategy):

    def calculate(self, weight):
        return weight * 30
```

```python
class FreeShipping(ShippingStrategy):

    def calculate(self, weight):
        return 0
```

Context:

```python
class ShippingService:

    def __init__(
        self,
        strategy: ShippingStrategy,
    ):
        self.strategy = strategy

    def calculate(self, weight):
        return self.strategy.calculate(weight)
```

---

# 8. Đây chính là Composition

Hãy nhìn:

```python
class ShippingService:

    def __init__(self, strategy):
        self.strategy = strategy
```

`ShippingService` **chứa** Strategy.

Đây là:

```text
ShippingService
      │
      └── HAS-A → Strategy
```

Không phải:

```text
ShippingService
      ↑
    extends
```

Strategy rất thường được implement bằng:

> **Composition over Inheritance**

---

# 9. Strategy + Dependency Injection

Ta inject strategy:

```python
strategy = ExpressShipping()

service = ShippingService(
    strategy
)
```

Hoặc:

```python
service = ShippingService(
    StandardShipping()
)
```

Dependency:

```text
Composition Root
       │
       ↓
 Strategy
       │
       ↓
ShippingService
```

Điều này hoàn toàn phù hợp với Buổi 26:

> Dependency Injection.

---

# 10. Strategy + OCP

Giả sử ban đầu:

```text
Standard
Express
```

Sau đó thêm:

```python
class DroneShipping(ShippingStrategy):

    def calculate(self, weight):
        return weight * 50
```

Không cần sửa:

```python
ShippingService
```

Chỉ cần:

```python
service = ShippingService(
    DroneShipping()
)
```

Đây chính là:

> **Open for extension, closed for modification.**

Strategy là một cách rất tự nhiên để thực hiện OCP.

---

# 11. Strategy trong Crawler

Đây mới là phần quan trọng.

Crawler của bạn có thể có nhiều **retry policy**.

Ví dụ:

```text
No Retry
Fixed Retry
Exponential Backoff
```

Nếu viết:

```python
class Crawler:

    def request(self, url, retry_type):

        if retry_type == "none":
            ...

        elif retry_type == "fixed":
            ...

        elif retry_type == "exponential":
            ...
```

thì Crawler sẽ ngày càng phình to.

Ta dùng Strategy.

---

# 12. Retry Strategy

Interface:

```python
from abc import ABC, abstractmethod


class RetryStrategy(ABC):

    @abstractmethod
    def get_delay(self, attempt):
        pass
```

No retry:

```python
class NoRetry(RetryStrategy):

    def get_delay(self, attempt):
        return None
```

Fixed:

```python
class FixedRetry(RetryStrategy):

    def __init__(self, delay):
        self.delay = delay

    def get_delay(self, attempt):
        return self.delay
```

Exponential:

```python
class ExponentialBackoff(RetryStrategy):

    def __init__(self, base_delay):
        self.base_delay = base_delay

    def get_delay(self, attempt):
        return self.base_delay * (2 ** attempt)
```

---

# 13. Crawler sử dụng Strategy

```python
class Crawler:

    def __init__(self, retry_strategy):
        self.retry_strategy = retry_strategy

    def get_retry_delay(self, attempt):
        return self.retry_strategy.get_delay(
            attempt
        )
```

Sử dụng:

```python
crawler = Crawler(
    retry_strategy=FixedRetry(2)
)
```

hoặc:

```python
crawler = Crawler(
    retry_strategy=ExponentialBackoff(1)
)
```

Crawler không cần biết cách tính delay.

---

# 14. Exponential Backoff

Ví dụ:

```python
strategy = ExponentialBackoff(
    base_delay=1
)
```

Các lần retry:

```text
attempt 0 → 1
attempt 1 → 2
attempt 2 → 4
attempt 3 → 8
attempt 4 → 16
```

Công thức:

```text
delay = base_delay × 2^attempt
```

Strategy chứa thuật toán.

Crawler chỉ gọi:

```python
delay = strategy.get_delay(attempt)
```

Đây là một ví dụ rất đẹp của Strategy Pattern.

---

# 15. Strategy hoàn chỉnh hơn

Ta có thể thiết kế:

```python
import time


class RetryStrategy(ABC):

    @abstractmethod
    def get_delay(self, attempt):
        pass
```

Fixed:

```python
class FixedRetry(RetryStrategy):

    def __init__(self, delay):
        self.delay = delay

    def get_delay(self, attempt):
        return self.delay
```

Exponential:

```python
class ExponentialBackoff(RetryStrategy):

    def __init__(
        self,
        base_delay=1,
        max_delay=30,
    ):
        self.base_delay = base_delay
        self.max_delay = max_delay

    def get_delay(self, attempt):

        delay = self.base_delay * (
            2 ** attempt
        )

        return min(delay, self.max_delay)
```

Crawler:

```python
class Crawler:

    def __init__(self, retry_strategy):
        self.retry_strategy = retry_strategy

    def retry(self, attempt):

        delay = self.retry_strategy.get_delay(
            attempt
        )

        if delay is None:
            return

        time.sleep(delay)
```

---

# 16. Strategy không nhất thiết phải là ABC

Python rất thích Duck Typing.

Ta có thể viết:

```python
class FixedRetry:

    def get_delay(self, attempt):
        return 2
```

và:

```python
class ExponentialBackoff:

    def get_delay(self, attempt):
        return 2 ** attempt
```

Crawler:

```python
class Crawler:

    def __init__(self, retry_strategy):
        self.retry_strategy = retry_strategy
```

Không cần inheritance.

Miễn object có:

```python
get_delay()
```

là được.

---

# 17. Strategy với Protocol

Nếu muốn có static typing:

```python
from typing import Protocol


class RetryStrategy(Protocol):

    def get_delay(self, attempt: int) -> float | None:
        ...
```

Implementation:

```python
class FixedRetry:

    def __init__(self, delay: float):
        self.delay = delay

    def get_delay(
        self,
        attempt: int,
    ) -> float:
        return self.delay
```

Crawler:

```python
class Crawler:

    def __init__(
        self,
        retry_strategy: RetryStrategy,
    ):
        self.retry_strategy = retry_strategy
```

Đây là một cách rất **Pythonic**.

---

# 18. Strategy runtime

Một ưu điểm quan trọng:

> Có thể thay đổi Strategy trong runtime.

Ví dụ:

```python
crawler = Crawler(
    FixedRetry(2)
)
```

Sau đó:

```python
crawler.retry_strategy = (
    ExponentialBackoff(1)
)
```

Bây giờ behavior đã thay đổi.

Crawler không cần sửa code.

---

# 19. Có thể có `set_strategy()`

```python
class Crawler:

    def __init__(self, strategy):
        self.strategy = strategy

    def set_strategy(self, strategy):
        self.strategy = strategy

    def crawl(self, url):
        ...
```

Sử dụng:

```python
crawler.set_strategy(
    ExponentialBackoff(1)
)
```

Tuy nhiên nếu strategy là dependency bắt buộc, thường nên inject qua constructor.

---

# 20. Strategy cho Parser

Ta có thể dùng Strategy cho nhiều loại parsing behavior:

```text
ParserStrategy
├── BeautifulSoupParser
├── SelectolaxParser
└── RegexParser
```

Ví dụ:

```python
class ParserStrategy(Protocol):

    def parse(self, html):
        ...
```

Implement:

```python
class SelectolaxParser:

    def parse(self, html):
        ...
```

```python
class BeautifulSoupParser:

    def parse(self, html):
        ...
```

Crawler:

```python
class Crawler:

    def __init__(self, parser):
        self.parser = parser

    def crawl(self, html):
        return self.parser.parse(html)
```

---

# 21. Nhưng Parser Factory thì sao?

Đây là câu hỏi rất quan trọng.

Ta đã học:

```text
Factory
```

và hôm nay:

```text
Strategy
```

Hai cái có thể nhìn rất giống nhau.

### Factory

```python
parser = ParserFactory.create(
    "site_a"
)
```

Factory quyết định:

> **Tạo object nào?**

### Strategy

```python
crawler = Crawler(
    parser_strategy
)
```

Strategy quyết định:

> **Behavior/algorithm nào được sử dụng?**

---

# 22. Factory + Strategy

Chúng hoàn toàn có thể kết hợp:

```text
CLI
 │
 │ --retry exponential
 ↓
Factory
 │
 ↓
ExponentialBackoff
 │
 ↓
Crawler
```

Ví dụ:

```python
strategy = RetryStrategyFactory.create(
    "exponential"
)

crawler = Crawler(
    retry_strategy=strategy
)
```

Ở đây:

```text
Factory
   ↓
chọn Strategy
   ↓
Crawler
```

Đây là kiến trúc rất phổ biến.

---

# 23. Strategy cho Storage

Crawler có thể lưu dữ liệu theo nhiều cách:

```text
SQLite
JSON
Memory
PostgreSQL
```

Ta có:

```python
class StorageStrategy(Protocol):

    def save(self, story):
        ...
```

SQLite:

```python
class SQLiteStorage:

    def save(self, story):
        print("Save to SQLite")
```

JSON:

```python
class JSONStorage:

    def save(self, story):
        print("Save to JSON")
```

Memory:

```python
class MemoryStorage:

    def save(self, story):
        print("Save to memory")
```

Crawler:

```python
class Crawler:

    def __init__(self, storage):
        self.storage = storage

    def process(self, story):
        self.storage.save(story)
```

---

# 24. Strategy cho Rate Limiting

Crawler cũng có thể có:

```text
RateLimitStrategy
├── NoLimit
├── FixedDelay
├── TokenBucket
└── Adaptive
```

Ví dụ:

```python
class RateLimitStrategy(Protocol):

    def wait(self):
        ...
```

Crawler:

```python
class Crawler:

    def __init__(self, rate_limiter):
        self.rate_limiter = rate_limiter

    def request(self, url):

        self.rate_limiter.wait()

        return self.client.get(url)
```

Crawler không cần biết thuật toán rate limit.

---

# 25. Strategy cho concurrency

Bạn thậm chí có thể thiết kế:

```text
ConcurrencyStrategy
├── Sequential
├── ThreadPool
├── Asyncio
└── ProcessPool
```

Ví dụ:

```python
class SequentialStrategy:

    def run(self, tasks):
        return [
            task()
            for task in tasks
        ]
```

Thread:

```python
class ThreadPoolStrategy:

    def __init__(self, max_workers):
        self.max_workers = max_workers

    def run(self, tasks):
        ...
```

Async:

```python
class AsyncStrategy:

    async def run(self, tasks):
        ...
```

Đây là một ý tưởng architecture rất mạnh.

---

# 26. Nhưng đừng biến mọi thứ thành Strategy

Ví dụ:

```python
class AddStrategy:
    def execute(self, a, b):
        return a + b
```

nếu application chỉ có:

```python
a + b
```

thì Strategy là thừa.

Bạn sẽ tạo:

```text
Interface
Implementation
Context
DI
Factory
```

chỉ để cộng hai số.

Không cần.

---

# 27. Khi nào Strategy phù hợp?

Hãy nhớ:

```text
Có nhiều thuật toán
       ↓
cùng một mục đích
       ↓
có thể thay thế nhau
       ↓
behavior có thể thay đổi
```

Ví dụ:

```text
Retry
Storage
Parser
Payment
Compression
Serialization
Sorting
Notification
Rate Limiting
```

---

# 28. Dấu hiệu nên Refactor thành Strategy

Một dấu hiệu rất mạnh:

```python
if method == "A":
    ...


elif method == "B":
    ...


elif method == "C":
    ...
```

và mỗi nhánh chứa **một thuật toán tương đối độc lập**.

Khi đó hãy suy nghĩ:

```text
if/elif
   ↓
Strategy
```

Nhưng không phải mọi `if` đều cần Strategy.

---

# 29. Strategy vs Inheritance

Một thiết kế xấu:

```python
class Crawler:
    ...


class RetryCrawler(Crawler):
    ...


class ExponentialRetryCrawler(Crawler):
    ...


class FixedRetryCrawler(Crawler):
    ...
```

Ta đang tạo:

```text
Crawler
 ├── RetryCrawler
 ├── FixedRetryCrawler
 └── ExponentialRetryCrawler
```

Retry thực chất không phải một loại Crawler.

Nó là **behavior của Crawler**.

Vì vậy Composition tốt hơn:

```text
Crawler
   │
   └── RetryStrategy
```

---

# 30. Đây là ví dụ rất điển hình của Composition over Inheritance

Không tốt:

```text
ExponentialRetryCrawler
        ↓
      Crawler
```

Tốt:

```text
Crawler
   │
   └── ExponentialBackoff
```

Quan hệ:

```text
Crawler HAS-A RetryStrategy
```

không phải:

```text
ExponentialRetryCrawler IS-A Crawler
```

---

# 31. Strategy và SOLID

Strategy gần như là một ví dụ tổng hợp của SOLID.

### SRP

Mỗi Strategy chứa một thuật toán.

```text
FixedRetry
    ↓
fixed retry logic
```

### OCP

Thêm:

```python
class JitterRetry:
    ...
```

không sửa Crawler.

### LSP

Các Strategy phải có behavior tương thích với contract.

### ISP

Strategy interface nhỏ:

```python
get_delay()
```

### DIP

Crawler phụ thuộc:

```text
RetryStrategy
```

thay vì:

```text
FixedRetry
ExponentialBackoff
```

---

# 32. Strategy + DI + DIP

Đây là kiến trúc cốt lõi:

```text
                  Crawler
                     │
                     ↓
               RetryStrategy
                  ↑       ↑
                  │       │
             FixedRetry  Exponential
```

Composition Root:

```python
strategy = ExponentialBackoff(
    base_delay=1
)

crawler = Crawler(
    retry_strategy=strategy
)
```

Dependency direction:

```text
Crawler
   ↓
RetryStrategy
   ↑
Concrete Strategy
```

Đúng tinh thần DIP.

---

# 33. Testing Strategy cực kỳ dễ

Ví dụ:

```python
class FakeRetry:

    def get_delay(self, attempt):
        return 0
```

Test:

```python
crawler = Crawler(
    retry_strategy=FakeRetry()
)
```

Không cần:

```text
sleep
network
HTTP server
```

Strategy có thể được thay bằng fake.

Đây là một lợi ích cực lớn của Composition + DI.

---

# 34. Strategy có state

Strategy không nhất thiết stateless.

Ví dụ:

```python
class FixedRetry:

    def __init__(self, delay):
        self.delay = delay
```

Strategy chứa configuration.

Hoặc:

```python
class RateLimiter:

    def __init__(self, requests_per_second):
        self.requests_per_second = (
            requests_per_second
        )
```

Điều này rất tự nhiên.

---

# 35. Strategy vs State

Hai Pattern này thường bị nhầm.

### Strategy

Mục tiêu:

> **Chọn thuật toán/behavior để thực hiện một nhiệm vụ.**

Ví dụ:

```text
RetryStrategy
├── Fixed
└── Exponential
```

### State

Mục tiêu:

> **Behavior thay đổi theo trạng thái hiện tại của object.**

Ví dụ:

```text
Crawler
├── RunningState
├── PausedState
├── FailedState
└── CompletedState
```

So sánh:

| Strategy                           | State                         |
| ---------------------------------- | ----------------------------- |
| Chọn thuật toán                    | Chọn behavior theo state      |
| Thường do client/config quyết định | Thường object tự chuyển state |
| FixedRetry                         | PausedState                   |
| CompressionStrategy                | LoggedOutState                |

---

# 36. Strategy vs Factory

Nhớ bằng hai câu:

```text
Factory:
"Tạo cái gì?"

Strategy:
"Làm bằng cách nào?"
```

Ví dụ:

```python
parser = ParserFactory.create("site_a")
```

→ Factory.

```python
crawler = Crawler(
    retry_strategy=ExponentialBackoff(1)
)
```

→ Strategy.

---

# 37. Một kiến trúc Crawler hoàn chỉnh

Bây giờ chúng ta có thể xây:

```text
                         Crawler
                            │
          ┌─────────────────┼─────────────────┐
          ↓                 ↓                 ↓
     HttpClient       ParserStrategy    RetryStrategy
          ↑                 ↑                 ↑
        HTTPX            SiteA/SiteB     Fixed/Exponential
                            │
                            ↓
                       StoryRepository
```

Trong đó:

```text
HttpClient
    → dependency

Parser
    → Strategy

Retry
    → Strategy

Repository
    → abstraction
```

Composition Root:

```python
client = HttpxClient()

parser = SiteAParser()

retry = ExponentialBackoff(
    base_delay=1,
    max_delay=30,
)

repository = SQLiteStoryRepository(
    db
)

crawler = Crawler(
    client=client,
    parser=parser,
    retry_strategy=retry,
    repository=repository,
)
```

Đây là architecture rất gần với project thực tế của bạn.

---

# 38. Strategy Registry

Có thể kết hợp Factory:

```python
class RetryStrategyFactory:

    _strategies = {
        "none": NoRetry,
        "fixed": FixedRetry,
        "exponential": ExponentialBackoff,
    }

    @classmethod
    def create(cls, name, **kwargs):

        try:
            strategy_class = cls._strategies[name]
        except KeyError:
            raise ValueError(
                f"Unknown strategy: {name}"
            )

        return strategy_class(**kwargs)
```

CLI:

```text
mycrawler crawl \
    --retry exponential \
    --workers 20
```

Application:

```python
retry = RetryStrategyFactory.create(
    "exponential",
    base_delay=1,
)
```

Sau đó:

```python
crawler = Crawler(
    retry_strategy=retry
)
```

Flow:

```text
CLI
 ↓
Factory
 ↓
Strategy
 ↓
DI
 ↓
Crawler
```

---

# 39. Đây là lúc các Pattern bắt đầu kết hợp

Chúng ta đã học:

```text
Singleton
Factory
Builder
Strategy
```

Chúng không phải những thứ độc lập.

Ví dụ:

```text
Factory
   ↓
tạo Strategy

Builder
   ↓
xây Config

DI
   ↓
inject vào Crawler

Strategy
   ↓
thay đổi algorithm
```

Một application thực tế có thể dùng nhiều pattern cùng nhau.

---

# 40. Bài tập 1 — Payment Strategy

Tạo:

```text
PaymentStrategy
├── CreditCardPayment
├── PayPalPayment
└── MoMoPayment
```

Interface:

```python
class PaymentStrategy:
    def pay(self, amount):
        ...
```

Context:

```python
class PaymentService:

    def __init__(self, strategy):
        self.strategy = strategy

    def pay(self, amount):
        return self.strategy.pay(amount)
```

Sử dụng:

```python
service = PaymentService(
    MoMoPayment()
)

service.pay(100_000)
```

---

# 41. Bài tập 2 — Retry Strategy

Tạo:

```text
RetryStrategy
├── NoRetry
├── FixedRetry
└── ExponentialBackoff
```

API:

```python
strategy.get_delay(attempt)
```

Test:

```python
assert FixedRetry(2).get_delay(1) == 2
```

và:

```python
assert ExponentialBackoff(1).get_delay(3) == 8
```

---

# 42. Bài tập 3 — Storage Strategy

Tạo:

```text
StorageStrategy
├── SQLiteStorage
├── JSONStorage
└── MemoryStorage
```

API:

```python
storage.save(story)
```

Context:

```python
class StoryService:

    def __init__(self, storage):
        self.storage = storage

    def save(self, story):
        self.storage.save(story)
```

---

# 43. Bài tập nâng cao ⭐

Thiết kế:

```text
Crawler
```

với:

```text
RetryStrategy
ParserStrategy
StorageStrategy
```

Constructor:

```python
crawler = Crawler(
    client=client,
    parser=parser,
    retry_strategy=retry,
    storage=storage,
)
```

Không được để Crawler:

```python
if parser_type == ...
```

hoặc:

```python
if retry_type == ...
```

hoặc:

```python
if storage_type == ...
```

Crawler chỉ sử dụng abstraction.

---

# 44. Bài tập kiến trúc ⭐⭐⭐

Thiết kế CLI:

```text
crawler crawl \
    --site site_a \
    --retry exponential \
    --storage sqlite
```

Architecture:

```text
CLI
 │
 ├───────────────┐
 ↓               ↓
ParserFactory  RetryFactory
 ↓               ↓
SiteAParser    ExponentialBackoff
 │               │
 └───────┬───────┘
         ↓
      Crawler
         │
         ↓
 StorageStrategy
         │
         ↓
      SQLite
```

Yêu cầu:

* Factory tạo Strategy
* Strategy chứa behavior
* Crawler không có `if/elif` cho từng implementation
* Dependency được inject
* Có thể thay Strategy trong test
* Infrastructure không chui vào domain

Đây là bài tập tổng hợp rất tốt cho toàn bộ phần SOLID + Design Pattern hiện tại.

---

# 45. Tổng kết Buổi 35

Strategy Pattern:

> **Đóng gói các thuật toán/behavior có thể thay thế nhau và cho phép chọn chúng độc lập với context.**

Công thức tư duy:

```text
Nhiều thuật toán
      ↓
cùng mục đích
      ↓
có thể thay thế
      ↓
Strategy
```

Ví dụ:

```text
Retry
├── Fixed
├── Exponential
└── NoRetry
```

---

# 46. Ba Pattern cần phân biệt

### Singleton

```text
Có bao nhiêu object?
```

### Factory

```text
Tạo object nào?
```

### Strategy

```text
Thực hiện behavior bằng cách nào?
```

Có thể nhớ:

```text
Singleton → HOW MANY?
Factory   → WHICH OBJECT?
Strategy  → WHICH ALGORITHM?
```

---

# 47. Design Pattern roadmap

Đã hoàn thành:

```text
Buổi 32 — Singleton    ✅
Buổi 33 — Factory      ✅
Buổi 34 — Builder      ✅
Buổi 35 — Strategy     ✅
```

Tiếp theo:

# **Buổi 36 — Observer Pattern**

Chúng ta sẽ áp dụng Observer trực tiếp vào **Crawler Dashboard + PySide6**:

```text
                    Crawler
                       │
                    Event
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
      Dashboard     Logger      ProgressBar
          ↓
       PySide6 UI
```

Đây sẽ là cầu nối rất quan trọng giữa **Design Pattern → Event-Driven Architecture → PySide6 Signals/Slots**, đúng với kiến trúc crawler dashboard mà bạn đang xây.
