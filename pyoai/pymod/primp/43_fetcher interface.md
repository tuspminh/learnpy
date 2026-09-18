# Phần V — Novel Crawler

# Buổi 43 — Fetcher Interface

Ở hai buổi trước, chúng ta đã có:

```text
41. FetchRequest
        ↓
42. FetchResponse
```

Hôm nay chúng ta nối hai model đó bằng **Fetcher Interface**.

Mục tiêu kiến trúc:

```text
Application
     │
     ↓
   Fetcher
     │
     ├──────── PrimpFetcher
     │
     ├──────── HttpxFetcher
     │
     └──────── FakeFetcher
```

Application **không cần biết** Fetcher đang dùng `primp`, `httpx` hay fake.

---

# 1. Fetcher Interface là gì?

Ta muốn Application có thể viết:

```python
response = await fetcher.get(
    FetchRequest(url=url)
)
```

mà không quan tâm:

```text
primp?
httpx?
requests?
fake?
```

Đây chính là **Port** trong Hexagonal/Clean Architecture.

---

# 2. Interface trong Python

Python không bắt buộc phải dùng Java-style:

```python
interface Fetcher
```

Ta có thể dùng:

```python
from typing import Protocol
```

Ví dụ:

```python
from typing import Protocol


class Fetcher(Protocol):

    async def get(
        self,
        request: FetchRequest,
    ) -> FetchResponse:
        ...
```

Đây là **structural typing**.

---

# 3. Vì sao dùng `Protocol`?

Có hai cách phổ biến.

### Abstract Base Class

```python
from abc import ABC, abstractmethod


class Fetcher(ABC):

    @abstractmethod
    async def get(self, request):
        ...
```

Class implementation phải kế thừa:

```python
class PrimpFetcher(Fetcher):
    ...
```

---

### Protocol

```python
class Fetcher(Protocol):

    async def get(self, request):
        ...
```

Class không cần:

```python
class PrimpFetcher(Fetcher):
```

vẫn có thể satisfy contract nếu có method tương ứng.

Đây rất hợp với Dependency Inversion.

---

# 4. Structural Typing

Ví dụ:

```python
class FakeFetcher:

    async def get(
        self,
        request: FetchRequest,
    ) -> FetchResponse:

        return FetchResponse(
            status_code=200,
            url=request.url,
            headers={},
            content=b"fake",
        )
```

`FakeFetcher` không kế thừa:

```python
Fetcher
```

nhưng về mặt type:

```text
FakeFetcher
    ↓
có get(FetchRequest)
    ↓
trả FetchResponse
    ↓
thỏa Fetcher Protocol
```

Đây là structural typing.

---

# 5. Fetcher Port nằm ở Application

Cấu trúc:

```text
src/
└── crawler/
    └── application/
        └── ports/
            └── fetcher.py
```

Nội dung:

```python
from typing import Protocol

from crawler.application.models.request import (
    FetchRequest,
)

from crawler.application.models.response import (
    FetchResponse,
)


class Fetcher(Protocol):

    async def get(
        self,
        request: FetchRequest,
    ) -> FetchResponse:
        ...
```

---

# 6. Application Use Case

Ví dụ:

```python
class CrawlChapter:

    def __init__(
        self,
        fetcher: Fetcher,
    ):
        self.fetcher = fetcher

    async def execute(
        self,
        url: str,
    ) -> str:

        request = FetchRequest(
            url=url,
            timeout=15,
        )

        response = await self.fetcher.get(
            request
        )

        if not response.is_success:
            raise RuntimeError(
                f"HTTP {response.status_code}"
            )

        return response.text
```

Chú ý:

```python
self.fetcher
```

có type:

```python
Fetcher
```

không phải:

```python
PrimpFetcher
```

---

# 7. Dependency Inversion

Đây là DIP:

```text
Application
     ↓
Fetcher Protocol
     ↑
     │
Infrastructure
     │
 ┌───┴───────────────┐
 ↓                   ↓
PrimpFetcher     FakeFetcher
```

Không phải:

```text
Application
     ↓
PrimpFetcher
     ↓
primp
```

---

# 8. PrimpFetcher

Infrastructure implement contract:

```python
class PrimpFetcher:

    def __init__(
        self,
        transport,
        rate_limiter,
        semaphore,
        retry_executor,
    ):
        self.transport = transport
        self.rate_limiter = rate_limiter
        self.semaphore = semaphore
        self.retry_executor = retry_executor

    async def get(
        self,
        request: FetchRequest,
    ) -> FetchResponse:

        async def operation():

            await self.rate_limiter.acquire()

            async with self.semaphore:

                return await self.transport.send(
                    request
                )

        return await self.retry_executor.execute(
            operation
        )
```

Điểm quan trọng:

> `PrimpFetcher` không cần kế thừa `Fetcher`.

Nó chỉ cần implement đúng shape.

---

# 9. FakeFetcher

Đây là implementation cực kỳ hữu ích cho test:

```python
class FakeFetcher:

    def __init__(
        self,
        response: FetchResponse,
    ):
        self.response = response
        self.requests = []

    async def get(
        self,
        request: FetchRequest,
    ) -> FetchResponse:

        self.requests.append(request)

        return self.response
```

---

# 10. Test Use Case bằng FakeFetcher

```python
import asyncio


async def main():

    fake_fetcher = FakeFetcher(
        FetchResponse(
            status_code=200,
            url="https://example.com/chapter-1",
            headers={},
            content=b"""
                <html>
                    <body>
                        Hello Chapter
                    </body>
                </html>
            """,
        )
    )

    use_case = CrawlChapter(
        fetcher=fake_fetcher
    )

    html = await use_case.execute(
        "https://example.com/chapter-1"
    )

    print(html)


asyncio.run(main())
```

Không cần:

```text
Internet
primp
proxy
TLS
```

---

# 11. Đây là Dependency Injection

Ta truyền:

```python
CrawlChapter(
    fetcher=fake_fetcher
)
```

thay vì để:

```python
class CrawlChapter:

    def __init__(self):

        self.fetcher = PrimpFetcher(...)
```

Đây là:

> Constructor Injection.

---

# 12. Test Application không cần biết implementation

Ví dụ:

```python
fake = FakeFetcher(
    FetchResponse(
        status_code=200,
        url="https://example.com",
        headers={},
        content=b"hello",
    )
)

use_case = CrawlChapter(fake)

result = await use_case.execute(
    "https://example.com"
)

assert result == "hello"
```

Application test hoàn toàn không biết:

```text
primp
httpx
proxy
```

---

# 13. Type Checker sẽ hiểu Protocol

Ví dụ:

```python
class FakeFetcher:

    async def get(
        self,
        request: FetchRequest,
    ) -> FetchResponse:
        ...
```

Ta có thể:

```python
def create_use_case(
    fetcher: Fetcher,
) -> CrawlChapter:

    return CrawlChapter(
        fetcher=fetcher
    )
```

và:

```python
fake = FakeFetcher()

use_case = create_use_case(
    fake
)
```

Static type checker có thể kiểm tra structural compatibility.

---

# 14. Một Fetcher không cần biết Novel

Tên:

```python
Fetcher
```

không nên có:

```python
async def fetch_novel(...)
async def fetch_chapter(...)
async def fetch_listing(...)
```

Không nên:

```python
class Fetcher:

    async def fetch_novel(self):
        ...

    async def fetch_chapter(self):
        ...

    async def fetch_listing(self):
        ...
```

Fetcher chỉ làm một việc:

> Fetch resource từ URL.

---

# 15. Parser mới biết resource là gì

Ví dụ:

```text
Listing URL
    ↓
Fetcher
    ↓
HTML
    ↓
ListingParser
```

hoặc:

```text
Novel URL
    ↓
Fetcher
    ↓
HTML
    ↓
NovelParser
```

hoặc:

```text
Chapter URL
    ↓
Fetcher
    ↓
HTML
    ↓
ChapterParser
```

Fetcher không phân biệt.

---

# 16. Đây là SRP

Fetcher:

```text
Fetch HTTP resource
```

Parser:

```text
Parse HTML
```

Repository:

```text
Persist domain data
```

Use Case:

```text
Orchestrate business operation
```

Không có class nào làm tất cả.

---

# 17. Interface quá lớn là vấn đề

Không tạo:

```python
class Fetcher(Protocol):

    async def get(...):
        ...

    async def post(...):
        ...

    async def download_file(...):
        ...

    async def stream(...):
        ...

    async def upload(...):
        ...

    async def crawl_novel(...):
        ...

    async def crawl_chapter(...):
        ...
```

Đây là Interface Pollution.

Hiện tại Novel Crawler cần:

```python
get()
```

thì interface chỉ cần:

```python
class Fetcher(Protocol):

    async def get(
        self,
        request: FetchRequest,
    ) -> FetchResponse:
        ...
```

---

# 18. Interface Segregation Principle

ISP nói đơn giản:

> Client không nên bị ép phụ thuộc vào interface mà nó không sử dụng.

Nếu Application chỉ cần GET:

```python
Fetcher
```

chỉ cần GET.

Sau này nếu cần download:

```python
FileDownloader
```

có thể là Port khác.

```text
Fetcher
    ↓
GET HTML

FileDownloader
    ↓
Binary file
```

---

# 19. Có nên đặt tên `HttpFetcher`?

Không nên nếu đây là Application Port.

```text
HttpFetcher
```

nghe như implementation.

Port nên nói về **capability**:

```text
Fetcher
```

Infrastructure:

```text
PrimpFetcher
HttpxFetcher
```

---

# 20. Có thể có nhiều implementation

Sau này:

```text
                 Fetcher
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
 PrimpFetcher  HttpxFetcher FakeFetcher
```

Application:

```python
class CrawlChapter:

    def __init__(
        self,
        fetcher: Fetcher,
    ):
        ...
```

không thay đổi.

---

# 21. Ví dụ HttpxFetcher

Không cần triển khai đầy đủ ngay, chỉ để thấy sức mạnh của abstraction:

```python
class HttpxFetcher:

    def __init__(
        self,
        client,
    ):
        self.client = client

    async def get(
        self,
        request: FetchRequest,
    ) -> FetchResponse:

        response = await self.client.get(
            request.url,
            headers=request.headers,
            params=request.params,
            timeout=request.timeout,
        )

        return FetchResponse(
            status_code=response.status_code,
            url=str(response.url),
            headers=dict(response.headers),
            content=response.content,
        )
```

Application vẫn:

```python
response = await fetcher.get(
    request
)
```

---

# 22. Không cần Factory để chọn Fetcher

Đừng vội tạo:

```python
FetcherFactory
```

chỉ để:

```python
if engine == "primp":
    ...
elif engine == "httpx":
    ...
```

Composition Root có thể làm:

```python
fetcher = PrimpFetcher(...)
```

và inject:

```python
use_case = CrawlChapter(
    fetcher=fetcher
)
```

Đơn giản hơn.

---

# 23. Composition Root

Toàn bộ application được lắp:

```python
async def build_application():

    client = primp.AsyncClient(
        impersonate="chrome_146",
        impersonate_os="windows",
    )

    transport = PrimpTransport(
        client
    )

    rate_limiter = RateLimiter(2)

    semaphore = asyncio.Semaphore(10)

    retry_executor = RetryExecutor(
        RetryPolicy(
            max_attempts=3
        )
    )

    fetcher = PrimpFetcher(
        transport=transport,
        rate_limiter=rate_limiter,
        semaphore=semaphore,
        retry_executor=retry_executor,
    )

    crawl_chapter = CrawlChapter(
        fetcher=fetcher
    )

    return crawl_chapter
```

Đây là Dependency Injection hoàn chỉnh.

---

# 24. Một điều rất quan trọng: Interface không chứa implementation

Không làm:

```python
class Fetcher(Protocol):

    client: primp.AsyncClient

    proxy_pool: ProxyPool

    retry_policy: RetryPolicy
```

Sai.

Interface chỉ mô tả capability:

```python
class Fetcher(Protocol):

    async def get(
        self,
        request: FetchRequest,
    ) -> FetchResponse:
        ...
```

---

# 25. Retry không thuộc Fetcher Interface

Interface không cần:

```python
async def retry(...)
```

Application chỉ nói:

```text
Fetch resource
```

Retry là internal behavior của implementation.

```text
Fetcher
   ↓
PrimpFetcher
   ↓
RetryExecutor
```

---

# 26. Proxy cũng không thuộc Interface

Không:

```python
async def get(
    request,
    proxy
)
```

Nếu Application cần truyền proxy trực tiếp thì Application bắt đầu quản lý infrastructure.

Ta muốn:

```text
Application
     ↓
FetchRequest
     ↓
Fetcher
     ↓
ProxyStrategy
```

Proxy Strategy sẽ được học ở **Buổi 46**.

---

# 27. Browser Profile cũng vậy

Không:

```python
fetcher.get(
    request,
    browser="chrome_146"
)
```

Browser Profile là infrastructure strategy.

```text
Application
     ↓
Fetcher
     ↓
BrowserProfileStrategy
```

Buổi 47 sẽ xử lý phần này.

---

# 28. Fetcher Interface là "cửa vào"

Hãy hình dung:

```text
              APPLICATION
                   │
                   │
             ┌─────▼─────┐
             │  Fetcher  │
             │   PORT    │
             └─────┬─────┘
                   │
          ═══════════════════
             infrastructure
          ═══════════════════
             │            │
             ↓            ↓
       PrimpFetcher   FakeFetcher
             │
             ↓
          primp
```

Port là cửa.

Infrastructure là implementation phía bên kia cửa.

---

# 29. Unit Test Use Case

Đây là test rất quan trọng:

```python
import pytest


@pytest.mark.asyncio
async def test_crawl_chapter():

    fake_fetcher = FakeFetcher(
        FetchResponse(
            status_code=200,
            url="https://example.com/ch1",
            headers={},
            content=b"chapter html",
        )
    )

    use_case = CrawlChapter(
        fetcher=fake_fetcher
    )

    result = await use_case.execute(
        "https://example.com/ch1"
    )

    assert result == "chapter html"

    assert len(
        fake_fetcher.requests
    ) == 1

    assert (
        fake_fetcher.requests[0].url
        == "https://example.com/ch1"
    )
```

Test này kiểm tra:

```text
Use Case
    ↓
Fetcher Port
    ↓
Fake implementation
```

---

# 30. Test HTTP layer riêng

Trong khi đó:

```text
PrimpTransport
```

có test riêng.

```text
PrimpTransport
    ↓
primp
```

Như vậy:

```text
Application tests
```

không cần Internet.

Còn:

```text
Infrastructure integration tests
```

mới cần HTTP thật.

Đây là cách test rất sạch.

---

# 31. Ba tầng test

Ta có:

```text
                    Tests
                      │
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
     Domain      Application   Infrastructure
        │             │             │
        │             │             ↓
        │             │          primp
        │             │
        │             ↓
        │          FakeFetcher
        │
        ↓
     pure Python
```

Đây là một lợi ích lớn của Clean Architecture.

---

# 32. `Fetcher` có phải ABC không?

Không nhất thiết.

Trong project này tôi chọn:

```python
Protocol
```

vì:

1. Interface nhỏ.
2. Dependency Injection dễ.
3. Fake dễ viết.
4. Không bắt implementation phải kế thừa.
5. Phù hợp structural typing.

ABC vẫn hợp lý khi ta cần:

* shared implementation
* common state
* template method
* enforced inheritance

Nhưng Fetcher Port hiện tại không cần.

---

# 33. Một interface tốt

```python
class Fetcher(Protocol):

    async def get(
        self,
        request: FetchRequest,
    ) -> FetchResponse:
        ...
```

Có thể đọc nó như một câu:

> Bất kỳ object nào có khả năng `get(FetchRequest) -> FetchResponse` đều có thể đóng vai trò Fetcher.

Rất rõ ràng.

---

# 34. Full module

`application/ports/fetcher.py`:

```python
from typing import Protocol

from crawler.application.models.request import (
    FetchRequest,
)

from crawler.application.models.response import (
    FetchResponse,
)


class Fetcher(Protocol):

    async def get(
        self,
        request: FetchRequest,
    ) -> FetchResponse:
        """Fetch a resource."""
        ...
```

---

# 35. Project structure sau Buổi 43

```text
src/
└── crawler/
    │
    ├── domain/
    │   ├── novel.py
    │   ├── chapter.py
    │   └── crawl_task.py
    │
    ├── application/
    │   │
    │   ├── models/
    │   │   ├── request.py
    │   │   └── response.py
    │   │
    │   ├── ports/
    │   │   └── fetcher.py       ← Buổi 43
    │   │
    │   └── use_cases/
    │       └── crawl_chapter.py
    │
    └── infrastructure/
        └── http/
            ├── primp_fetcher.py
            ├── primp_transport.py
            ├── retry.py
            ├── rate_limit.py
            ├── proxy.py
            └── browser_profile.py
```

---

# 36. Toàn bộ dependency direction

Điều chúng ta muốn:

```text
┌──────────────────────┐
│       Domain         │
└──────────▲───────────┘
           │
           │
┌──────────┴───────────┐
│     Application      │
│                      │
│ FetchRequest         │
│ FetchResponse        │
│ Fetcher              │
│ CrawlChapter         │
└──────────▲───────────┘
           │
           │ implements
           │
┌──────────┴───────────┐
│   Infrastructure     │
│                      │
│ PrimpFetcher         │
│ PrimpTransport       │
│ Retry                │
│ Proxy                │
│ RateLimiter           │
└──────────────────────┘
```

Infrastructure phụ thuộc Application Port.

Application không phụ thuộc Infrastructure.

---

# 37. Điều này cho phép thay primp

Hiện tại:

```text
PrimpFetcher
    ↓
primp
```

Nếu sau này:

```text
primp
↓
httpx
```

ta có:

```text
HttpxFetcher
    ↓
httpx
```

Use Case:

```python
class CrawlChapter:

    def __init__(
        self,
        fetcher: Fetcher,
    ):
        self.fetcher = fetcher
```

**không đổi.**

---

# 38. Và đây chính là Liskov Substitution

Ở mức architectural:

```text
Fetcher
```

có thể được thay bởi:

```text
PrimpFetcher
FakeFetcher
HttpxFetcher
```

miễn implementation tuân thủ contract:

```text
FetchRequest
      ↓
FetchResponse
```

Application không cần biết implementation cụ thể.

---

# 39. Nhưng đừng hiểu LSP là "mọi class đều phải kế thừa"

Với `Protocol`:

```python
class FakeFetcher:
    ...
```

không cần:

```python
class FakeFetcher(Fetcher):
```

Điều quan trọng là **behavioral contract**, không phải inheritance.

---

# 40. Kết quả của Buổi 43

Chúng ta đã hoàn thiện contract:

```text
                 Fetcher Protocol
                       │
              ┌────────┴────────┐
              ↓                 ↓
       FetchRequest       FetchResponse
```

Application:

```python
response = await fetcher.get(
    FetchRequest(url=url)
)
```

không biết:

```text
primp
httpx
proxy
TLS
browser profile
retry
```

Infrastructure:

```text
PrimpFetcher
     ↓
PrimpTransport
     ↓
primp.AsyncClient
```

---

## Ba nguyên tắc cần nhớ

### 1. Port nói **cần gì**

```python
Fetcher
```

> Tôi cần khả năng fetch.

### 2. Adapter nói **làm bằng gì**

```python
PrimpFetcher
```

> Tôi thực hiện bằng primp.

### 3. Application không quyết định implementation

```text
Composition Root
       ↓
inject PrimpFetcher
       ↓
CrawlChapter
```

---

## Tiến độ Phần V

```text
41. Request Model              ✅
42. Response Model             ✅
43. Fetcher Interface          ✅
44. PrimpFetcher                  ← tiếp theo
45. Retry Policy
46. Proxy Strategy
47. Browser Profile Strategy
48. Error Classification
49. Observability / Logging
50. Production Fetcher
```

**Buổi 44 — `PrimpFetcher`** sẽ là lúc chúng ta lấy toàn bộ những thứ đã xây ở Phần IV (`AsyncClient`, `PrimpTransport`, `RetryExecutor`, `RateLimiter`, `Semaphore`) và đóng gói thành implementation chính thức của `Fetcher` Port.
