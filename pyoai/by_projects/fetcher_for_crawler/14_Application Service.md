# 📘 Buổi 14 — Application Service

Tiếp tục đúng roadmap Fetcher:

```text
01 Architecture
02 Proxy Domain
03 ProxyPool
04 User-Agent Pool
05 HttpClient
06 Proxy Health Checker
07 Basic Fetcher
08 Proxy Rotation
09 User-Agent Rotation
10 Retry
11 Error Handling
12 Fetch Policy
13 Domain Service
👉 14 Application Service
15 Dependency Injection
16 Repository cho Proxy
17 Proxy State
18 Circuit Breaker
19 Rate Limiting
20 Fetch Orchestration
```

Hôm nay chúng ta giải quyết một câu hỏi rất quan trọng:

> **`Fetcher` và `Application Service` khác nhau ở đâu?**

---

# 1. Vấn đề hiện tại

Sau Buổi 13, kiến trúc của chúng ta đã có:

```text
Crawler
   ↓
Fetcher
   ↓
HealthyProxySelector
   ↓
ProxyHealthService
   ↓
HttpClient
```

Nhưng khi ứng dụng thật bắt đầu có nhiều use case:

```text
crawl chapter
crawl book
retry failed chapter
recrawl
download image
check proxy
fetch metadata
```

thì không nên để:

```text
Crawler
   ↓
Fetcher
```

trực tiếp xử lý toàn bộ workflow.

Ta cần một lớp:

```text
Application Service
```

---

# 2. Application Service là gì?

Có thể hiểu đơn giản:

> **Application Service đại diện cho một use case của hệ thống và điều phối các thành phần để hoàn thành use case đó.**

Nó không chứa business rule chi tiết của Domain.

Ví dụ:

```text
FetchChapter
```

có workflow:

```text
1. nhận URL
2. tạo FetchRequest
3. gọi Fetcher
4. nhận FetchResult
5. xử lý kết quả
6. trả về Application Result
```

Đây là Application logic.

---

# 3. Fetcher vs Application Service

Đây là phần quan trọng nhất hôm nay.

## Fetcher

Fetcher trả lời:

> **"Làm thế nào để thực hiện một HTTP fetch đáng tin cậy?"**

Nó biết:

```text
Proxy
User-Agent
Health Check
Retry
Error Classification
Fetch Policy
HttpClient
```

---

## Application Service

Application Service trả lời:

> **"Use case của ứng dụng này cần làm gì với Fetcher?"**

Ví dụ:

```text
FetchChapterUseCase
    ↓
Fetcher
    ↓
FetchResult
    ↓
ChapterCrawler
```

---

# 4. Ví dụ

Giả sử crawler cần tải:

```text
https://example.com/chapter-100
```

Application Service:

```text
id="j2s7qv"
FetchChapterService
        │
        ▼
FetchRequest
        │
        ▼
Fetcher
        │
        ├── Proxy
        ├── UA
        ├── Retry
        └── HTTP
        │
        ▼
FetchResult
        │
        ▼
Application Service
```

Fetcher **không cần biết**:

```text
đây là chapter
đây là book
đây là metadata
```

Nó chỉ biết:

```text
"fetch URL này"
```

---

# 5. Thiết kế Application Service

Tạo:

```text
application/
└── services/
    └── fetch_service.py
```

Interface:

```python id="k2e5is"
from abc import ABC, abstractmethod


class FetchApplicationService(ABC):
    @abstractmethod
    def fetch(self, url: str) -> FetchResult:
        raise NotImplementedError
```

Nhưng trong thực tế chúng ta có thể không cần ABC ở đây.

Application Service thường là **use-case implementation**, còn interface chỉ cần khi thực sự có nhu cầu thay thế.

Do đó version đơn giản:

```python id="x6e5iw"
class FetchApplicationService:
    def __init__(self, fetcher: Fetcher):
        self._fetcher = fetcher

    def fetch(self, url: str) -> FetchResult:
        request = FetchRequest(url=url)
        return self._fetcher.fetch(request)
```

---

# 6. Có vẻ quá đơn giản?

Đúng.

Hiện tại:

```text
Application Service
     ↓
Fetcher
```

chỉ có:

```python
request = FetchRequest(url)
return fetcher.fetch(request)
```

Có thể bạn sẽ hỏi:

> "Vậy tại sao cần nó?"

Bởi vì Application Service sẽ trở nên quan trọng khi use case có thêm workflow.

Ví dụ:

```text
Fetch Chapter
      ↓
Fetcher
      ↓
FetchResult
      ↓
Parse Chapter
      ↓
Save Chapter
      ↓
Publish Domain Event
```

Lúc đó:

```text
Application Service
```

là nơi điều phối.

---

# 7. Fetcher không nên save Database

Ví dụ này không nên:

```python id="d9m1ke"
class Fetcher:
    def fetch(self, request):
        response = ...
        chapter_repository.save(...)
```

Vì Fetcher sẽ bị phụ thuộc:

```text
Fetcher
 ├── HTTP
 ├── Proxy
 ├── Parser
 └── Database
```

Đây là violation SRP.

Fetcher chỉ nên:

```text
URL
 ↓
HTTP
 ↓
FetchResult
```

---

# 8. Application Service có thể điều phối nhiều component

Ví dụ:

```python id="n9z2ei"
class FetchChapterService:
    def __init__(
        self,
        fetcher: Fetcher,
        chapter_parser: ChapterParser,
        chapter_repository: ChapterRepository,
    ):
        self._fetcher = fetcher
        self._chapter_parser = chapter_parser
        self._chapter_repository = chapter_repository

    def execute(self, url: str):
        request = FetchRequest(url=url)

        result = self._fetcher.fetch(request)

        chapter = self._chapter_parser.parse(result.text)

        self._chapter_repository.save(chapter)

        return chapter
```

Đây chính là Application Service.

---

# 9. Nhưng hãy cẩn thận

Application Service **không nên chứa business rules**.

Ví dụ:

```python id="5p8g0a"
if chapter.number <= 0:
    raise ValueError(...)
```

Nếu đây là invariant của `Chapter`, thì nên để:

```text
Chapter Entity
```

xử lý.

Application Service chỉ:

```text
gọi
→ truyền dữ liệu
→ điều phối
```

---

# 10. Domain vs Application

Hãy nhìn ví dụ:

### Domain rule

```text id="0mjf3j"
Proxy DEAD không được sử dụng
```

→ Domain.

---

### Domain rule

```text id="n7s8nq"
Chapter number phải > 0
```

→ Chapter Entity.

---

### Application workflow

```text id="7n7kz0"
fetch
↓
parse
↓
save
```

→ Application Service.

---

### Infrastructure

```text id="b8rjxx"
httpx.Client
sqlite3.Connection
Redis
```

→ Infrastructure.

---

# 11. Use Case cụ thể hơn

Thay vì:

```python id="z8z0wy"
service.fetch(url)
```

ta có thể tạo Request DTO.

```python id="s4m8d9"
@dataclass(frozen=True)
class FetchUrlCommand:
    url: str
```

Service:

```python id="yqj5cv"
class FetchUrlService:
    def __init__(self, fetcher: Fetcher):
        self._fetcher = fetcher

    def execute(
        self,
        command: FetchUrlCommand,
    ) -> FetchResult:

        request = FetchRequest(url=command.url)

        return self._fetcher.fetch(request)
```

Flow:

```text
CLI
 ↓
FetchUrlCommand
 ↓
Application Service
 ↓
FetchRequest
 ↓
Fetcher
```

---

# 12. Command vs Request

Hai object này có thể trông giống nhau:

```text
FetchUrlCommand
FetchRequest
```

Nhưng vai trò khác nhau.

### Command

Application layer:

> "Tôi muốn thực hiện use case này."

```python id="1f4ocf"
FetchUrlCommand(url="...")
```

---

### Request

Fetcher layer:

> "Đây là dữ liệu cần để thực hiện fetch."

```python id="odv0f0"
FetchRequest(url="...")
```

Trong project nhỏ có thể gộp.

Nhưng trong architecture lớn, tách ra giúp boundary rõ hơn.

---

# 13. Application Result

Tương tự, Application Service có thể không trả trực tiếp:

```python id="q4r8h1"
FetchResult
```

mà tạo:

```python id="8xk8az"
@dataclass(frozen=True)
class FetchUrlResult:
    url: str
    status_code: int
    content: bytes
```

Tuy nhiên hiện tại:

```text FetchResult
```

đã khá phù hợp.

**Chưa cần tạo thêm abstraction chỉ để cho đẹp.**

Đây là nguyên tắc quan trọng:

> DDD tốt không phải là tạo thật nhiều class.

---

# 14. Application Service với Error

Application Service không nên tự xử lý:

```text
Timeout
Connection
500
429
```

vì Fetcher + FetchPolicy đã chịu trách nhiệm.

Ví dụ:

```python id="25o4m3"
class FetchUrlService:
    def __init__(self, fetcher: Fetcher):
        self._fetcher = fetcher

    def execute(
        self,
        command: FetchUrlCommand,
    ) -> FetchResult:

        request = FetchRequest(url=command.url)

        return self._fetcher.fetch(request)
```

Nếu Fetcher không thể fetch:

```text
Fetcher
 ↓
FetchError
 ↓
Application Service
```

Application Service có thể:

```text
log
convert to use-case error
notify caller
```

nhưng **không nên tự thực hiện retry**.

---

# 15. Exception boundary

Đây là một kiến trúc rất tốt:

```text id="j7q0lf"
Infrastructure
     │
     │ httpx exception
     ▼
HttpxClient
     │
     │ FetchError
     ▼
Fetcher
     │
     │ FetchError
     ▼
Application Service
     │
     │ Application-level result/error
     ▼
CLI / GUI
```

Ví dụ GUI không cần biết:

```python id="y7c2e3"
httpx.ConnectTimeout
```

Nó chỉ cần biết:

```text
FetchTimeoutError
```

hoặc application-level error.

---

# 16. Application Service cho CLI

Ví dụ CLI:

```text id="3w3sba"
crawl fetch URL
```

Không nên:

```python id="8h8x5q"
client = httpx.Client(...)
proxy = ...
retry = ...
```

trong CLI.

Đúng:

```python id="c3b9zw"
service = FetchUrlService(fetcher)

result = service.execute(FetchUrlCommand(url))
```

CLI chỉ là **delivery mechanism**.

---

# 17. GUI cũng dùng cùng Service

Sau này PySide6:

```text id="0ivm9g"
PySide6
   ↓
FetchUrlCommand
   ↓
FetchUrlService
   ↓
Fetcher
   ↓
HttpClient
```

CLI:

```text id="6zsvwt"
CLI
 ↓
FetchUrlCommand
 ↓
FetchUrlService
 ↓
Fetcher
```

Hai UI khác nhau nhưng dùng chung Application layer.

Đây chính là lợi ích cực lớn.

---

# 18. Crawler cũng dùng Application Service

Trong project truyện:

```text id="d8t5r7"
Crawler
   ↓
FetchChapterService
   ↓
Fetcher
   ↓
HTTP
```

Sau đó:

```text id="j9o9re"
FetchResult
   ↓
ChapterParser
   ↓
Chapter
   ↓
ChapterRepository
```

Application Service có thể điều phối cả pipeline.

---

# 19. Ví dụ `FetchChapterService`

Bây giờ xây một use case thực tế hơn.

```python id="xg2g6m"
class FetchChapterService:
    def __init__(
        self,
        fetcher: Fetcher,
        parser: ChapterParser,
        repository: ChapterRepository,
    ):
        self._fetcher = fetcher
        self._parser = parser
        self._repository = repository

    def execute(
        self,
        url: str,
    ) -> Chapter:

        request = FetchRequest(url=url)

        result = self._fetcher.fetch(request)

        chapter = self._parser.parse(result.text)

        self._repository.save(chapter)

        return chapter
```

Flow:

```text id="o2xx2b"
URL
 ↓
FetchChapterService
 ↓
Fetcher
 ↓
FetchResult
 ↓
ChapterParser
 ↓
Chapter
 ↓
ChapterRepository
```

---

# 20. Đây mới là chỗ DDD bắt đầu phát huy

Fetcher chỉ biết:

```text id="q9a5q8"
HTTP resource
```

Chapter Service biết:

```text id="kqcb8s"
Chapter use case
```

Chapter Parser biết:

```text id="8n0jch"
HTML → Chapter
```

Chapter Entity biết:

```text id="4d2m7x"
Chapter invariants
```

Repository biết:

```text id="j9g9lh"
Chapter → database
```

Mỗi layer có trách nhiệm riêng.

---

# 21. Application Service không nên chứa SQL

Sai:

```python id="3j0hkm"
class FetchChapterService:
    def execute(self, url):
        ...
        cursor.execute("INSERT INTO chapters ...")
```

SQL thuộc:

```text id="jbxg2w"
Infrastructure Repository
```

Application chỉ:

```python id="yd4l7q"
repository.save(chapter)
```

---

# 22. Application Service không nên biết SQLite

Không nên:

```python id="7atxbs"
import sqlite3
```

trong Application.

Đúng:

```text id="q73mml"
Application
    ↓
ChapterRepository interface
    ↓
SQLiteChapterRepository
```

Đây chính là DIP.

---

# 23. Application Service không nên biết HTTPX

Không:

```python id="1l6k2m"
import httpx
```

Đúng:

```text id="i5m1qi"
Application
    ↓
Fetcher
    ↓
HttpClient
    ↓
HttpxClient
```

---

# 24. Dependency graph

Kiến trúc hiện tại:

```text id="u1x9dn"
                       CLI
                        │
                        ▼
              FetchUrlApplicationService
                        │
                        ▼
                      Fetcher
                        │
         ┌──────────────┼───────────────┐
         │              │               │
         ▼              ▼               ▼
 HealthyProxy      UserAgent       FetchPolicy
   Selector         Provider
         │
         ▼
 ProxyHealthService
         │
         ▼
 ProxyHealthChecker
         │
         ▼
      HttpClient
         │
         ▼
      HttpxClient
```

---

# 25. Với Chapter crawler

Sau này:

```text id="1o4v95"
                   CrawlChapterService
                          │
             ┌────────────┼─────────────┐
             │            │             │
             ▼            ▼             ▼
          Fetcher      Parser       Repository
             │            │             │
             ▼            ▼             ▼
         HTTP HTML     Chapter      SQLite
```

Đây là Application orchestration.

---

# 26. Một Application Service nên làm gì?

Một Application Service thường có thể:

```text id="qv5m5w"
✓ nhận command
✓ validate application input
✓ gọi domain service
✓ gọi repository
✓ gọi external service qua abstraction
✓ điều phối transaction
✓ publish event
✓ trả result
```

Không nên:

```text id="1f1y9s"
✗ SQL trực tiếp
✗ HTTPX trực tiếp
✗ business invariant của Entity
✗ retry algorithm
✗ proxy rotation algorithm
```

---

# 27. Application Service và Transaction

Điểm này sẽ rất quan trọng với project của bạn.

Ví dụ:

```text id="azj42v"
Fetch Chapter
      ↓
Parse Chapter
      ↓
Save Chapter
      ↓
Save Images
      ↓
Save Metadata
```

Nếu cần transaction:

```text id="bq3m1h"
Application Service
        ↓
UnitOfWork
        ↓
Repository
```

Sau này chúng ta có thể có:

```python id="w6d0vf"
with uow:
    chapter = ...
    uow.chapters.save(chapter)
    uow.images.save(...)
```

Đây là lý do Application Service là nơi rất tự nhiên để điều phối UoW.

---

# 28. Nhưng chưa đưa UoW vào hôm nay

Bạn đã học UoW/SQLite riêng rồi, nhưng roadmap Fetcher hiện tại chưa tới:

```text
16 Repository
17 Proxy State
```

vì vậy hôm nay **không ghép UoW vào Fetcher**.

Ta giữ boundary:

```text
Fetcher
```

chỉ tập trung vào fetching.

Đây là cách tránh roadmap bị lan man.

---

# 29. Test Application Service

Vì Application Service nhận `Fetcher` qua constructor:

```python id="w2b3rf"
class FetchUrlService:
    def __init__(self, fetcher):
        self._fetcher = fetcher
```

ta có thể dùng Fake.

```python id="a6wqv0"
class FakeFetcher:
    def __init__(self, result):
        self.result = result
        self.last_request = None

    def fetch(self, request):
        self.last_request = request
        return self.result
```

---

# 30. Test

```python id="c5n2w5"
def test_fetch_service_creates_request():
    result = FetchResult(
        url="https://example.com",
        status_code=200,
        headers={},
        content=b"hello",
    )

    fetcher = FakeFetcher(result)

    service = FetchUrlService(fetcher)

    actual = service.execute(FetchUrlCommand(url="https://example.com"))

    assert actual is result

    assert fetcher.last_request.url == ("https://example.com")
```

Không cần:

```text
httpx
network
proxy
Internet
```

Test chạy cực nhanh.

Đây chính là lợi ích của DI.

---

# 31. Test Error Propagation

Nếu Fetcher lỗi:

```python id="0i4k6v"
class FakeFetcher:
    def fetch(self, request):
        raise FetchTimeoutError(
            "timeout",
            url=request.url,
        )
```

Service:

```python id="6y0h2s"
service.execute(...)
```

sẽ propagate:

```text
FetchTimeoutError
```

Nếu Application Service chưa có lý do để chuyển đổi lỗi, **đừng chuyển đổi chỉ cho đẹp**.

---

# 32. Khi nào cần Application Exception?

Sau này GUI có thể không muốn nhận:

```text
FetchTimeoutError
```

mà muốn:

```text
ChapterFetchFailed
```

Khi đó:

```text id="v6l1pj"
Fetcher
 ↓
FetchTimeoutError
 ↓
FetchChapterService
 ↓
ChapterFetchFailed
 ↓
GUI
```

Nhưng chỉ làm khi boundary thực sự cần.

---

# 33. Application Service vs Domain Service

Đây là bảng cần nhớ:

|                      | Domain Service                     | Application Service    |
| -------------------- | ---------------------------------- | ---------------------- |
| Mục đích             | Domain logic                       | Use case orchestration |
| Business rule        | ✅                                  | Không nên              |
| Gọi Entity           | ✅                                  | ✅                      |
| Gọi Repository       | Thường qua abstraction/domain port | ✅                      |
| Gọi external service | Qua abstraction                    | ✅                      |
| HTTPX                | ❌                                  | ❌                      |
| SQLite               | ❌                                  | ❌                      |
| Điều phối workflow   | ❌/ít                               | ✅                      |
| Transaction/UoW      | Không trực tiếp                    | ✅                      |

---

# 34. Ví dụ so sánh

### Domain Service

```python id="mcvb0q"
class ProxyHealthService:
    def verify(self, proxy):
        result = self._checker.check(proxy)

        if result.reachable:
            proxy.mark_alive()
            return True

        proxy.mark_dead()
        return False
```

Nó chứa domain behavior:

```text
health result
→ proxy state
```

---

### Application Service

```python id="kk7vii"
class FetchChapterService:
    def execute(self, url):

        result = self._fetcher.fetch(FetchRequest(url))

        chapter = self._parser.parse(result.text)

        self._repository.save(chapter)

        return chapter
```

Nó chứa workflow:

```text
fetch
→ parse
→ save
```

---

# 35. Kiến trúc Fetcher hoàn chỉnh hơn

```text id="3t9i8j"
                        ┌─────────────┐
                        │     CLI     │
                        └──────┬──────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │ Application Service│
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │      Fetcher       │
                    └─────────┬──────────┘
                              │
           ┌──────────────────┼──────────────────┐
           │                  │                  │
           ▼                  ▼                  ▼
   HealthyProxy         UserAgent          FetchPolicy
      Selector            Provider
           │
           ▼
   ProxyHealthService
           │
           ▼
   ProxyHealthChecker
           │
           ▼
       HttpClient
           │
           ▼
       HttpxClient
```

---

# 36. Quan trọng: Fetcher vẫn không phải Application Service

Một cách nhìn rất dễ nhớ:

```text id="u6yubg"
Application Service
=
"WHAT use case?"

Fetcher
=
"HOW fetch reliably?"
```

Ví dụ:

```text
FetchChapterService
=
"Fetch một chapter và lưu nó"

Fetcher
=
"Thực hiện HTTP fetch với proxy,
UA, health check, retry, policy"
```

---

# 37. Đặt tên theo use case

Trong project lớn, tôi khuyên tránh một class khổng lồ:

```python id="x8xw9q"
class ApplicationService: ...
```

Thay vào đó:

```text id="zqf7n7"
application/
└── services/
    ├── fetch_url.py
    ├── fetch_chapter.py
    ├── crawl_book.py
    └── retry_chapter.py
```

Mỗi class đại diện cho một use case.

Ví dụ:

```python id="yqy6mt"
class FetchChapterService: ...
```

rất dễ hiểu.

---

# 38. Bài tập Buổi 14

### Bài 1

Tạo:

```text id="ay8qif"
application/services/fetch_url.py
```

với:

```python id="gq7mto"
FetchUrlCommand
FetchUrlService
```

---

### Bài 2

Inject:

```text id="3m0f91"
Fetcher
```

qua constructor.

Không tạo:

```python id="gghm03"
Fetcher(...)
```

bên trong Service.

---

### Bài 3

Viết:

```text id="2r3rmy"
FakeFetcher
```

và test:

```text
Command
 ↓
Service
 ↓
FetchRequest
 ↓
FakeFetcher
 ↓
FetchResult
```

---

### Bài 4

Tạo sơ đồ:

```text
CLI
 ↓
FetchUrlService
 ↓
Fetcher
 ↓
HealthyProxySelector
 ↓
ProxyHealthService
 ↓
HttpClient
```

và đánh dấu:

```text
Domain
Application
Infrastructure
```

---

# 🧠 Tóm tắt Buổi 14

Bạn cần nắm chắc 4 tầng:

```text id="1h7qbg"
Domain
│
├── Proxy
├── ProxyUrl
├── ProxyHealthService
└── HealthyProxySelector


Application
│
├── Fetcher
├── ErrorClassifier
├── FetchPolicy
└── FetchUrlService


Infrastructure
│
└── HttpxClient


Delivery
│
├── CLI
└── PySide6
```

Và nhớ:

```text id="4qj4cs"
Domain Service
→ business/domain logic

Application Service
→ use-case orchestration

Fetcher
→ reliable HTTP-fetch mechanism

Infrastructure
→ technical implementation
```

---

## 🔜 Buổi 15 — Dependency Injection

Đây là bước tiếp theo rất tự nhiên.

Chúng ta sẽ không chỉ nói:

```python
class Fetcher:
    def __init__(...):
        ...
```

mà sẽ xây **Composition Root** hoàn chỉnh:

```text
main.py
   │
   ├── tạo ProxyPool
   ├── tạo UserAgentPool
   ├── tạo HttpxClient
   ├── tạo HealthChecker
   ├── tạo HealthService
   ├── tạo ProxySelector
   ├── tạo ErrorClassifier
   ├── tạo FetchPolicy
   ├── tạo Fetcher
   └── tạo ApplicationService
```

sau đó:

```text
CLI
 ↓
Application Service
 ↓
Fetcher
```

**không class nào tự `new` dependency bên trong**.

Đây sẽ là Buổi 15 — **Dependency Injection + Composition Root**, nền tảng để sau này chúng ta thay `HttpxClient` bằng `FakeHttpClient`, thay `ProxyPool` bằng `SQLiteProxyRepository`, và viết test toàn hệ thống mà không cần Internet.
