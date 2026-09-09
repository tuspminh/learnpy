# Buổi 5 — `HttpClient` Abstraction + `httpx.Client` Sync

Hôm nay ta đưa **`httpx` vào Infrastructure** lần đầu tiên.

Mục tiêu:

```text
Application
    │
    ▼
 HttpClient          ← abstraction
    ▲
    │
 HttpxClient         ← Infrastructure
    │
    ▼
   httpx
```

**Quy tắc kiến trúc:** `domain/` và `application/` tuyệt đối không import `httpx`.

---

# 1. Tại sao không gọi `httpx.get()` trực tiếp?

Cách đơn giản:

```python
import httpx


def fetch(url: str):
    return httpx.get(url)
```

nhưng Application bây giờ phụ thuộc trực tiếp vào thư viện:

```text
Application
     │
     ▼
   httpx
```

Nếu sau này đổi:

```text
httpx → requests
```

hoặc:

```text
httpx sync → httpx async
```

ta phải sửa Application.

Kiến trúc mong muốn:

```text
Application
     │
     ▼
 HttpClient
     ▲
     │
 HttpxClient
     │
     ▼
   httpx
```

---

# 2. `HttpClient` là Port

Tạo:

```text
domain/
└── fetch/
    └── interfaces.py
```

Ta đã có:

```python
from abc import ABC, abstractmethod


class HttpClient(ABC):

    @abstractmethod
    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        proxy: str | None = None,
    ):
        raise NotImplementedError
```

Nhưng interface này vẫn còn một vấn đề:

```python
proxy: str | None
```

và return type chưa rõ.

Ta sẽ thiết kế tốt hơn.

---

# 3. HTTP Response không nên là `httpx.Response`

Không nên:

```python
class HttpClient(ABC):

    @abstractmethod
    def get(...) -> httpx.Response:
        ...
```

vì như vậy:

```text
Domain
   ↓
httpx.Response
```

lại bị leak dependency.

Ta tạo một Domain/Application response model riêng.

---

# 4. `HttpResponse`

Tạo:

```text
domain/fetch/entities.py
```

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class HttpResponse:

    status_code: int
    headers: dict[str, str]
    content: bytes
    url: str

    @property
    def text(self) -> str:
        return self.content.decode(
            "utf-8",
            errors="replace",
        )
```

Bây giờ Application nhận:

```text
HttpResponse
```

chứ không nhận:

```text
httpx.Response
```

---

# 5. Tại sao dùng `bytes`?

Crawler truyện chữ chủ yếu lấy HTML.

Ta có thể muốn:

```python
response.text
```

nhưng lưu `bytes` làm raw content sẽ linh hoạt hơn:

```text
HTTP
  ↓
bytes
  ↓
decode
  ↓
text
  ↓
parser
```

Sau này có thể gặp:

```text
UTF-8
Windows-1252
GBK
...
```

và ta có thể cải thiện cơ chế decode mà không thay đổi HTTP client interface.

---

# 6. `HttpClient` hoàn chỉnh

```python
from abc import ABC, abstractmethod

from .entities import HttpResponse


class HttpClient(ABC):

    @abstractmethod
    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        proxy: str | None = None,
    ) -> HttpResponse:
        raise NotImplementedError
```

Đây là **Port**.

---

# 7. Infrastructure: `HttpxClient`

Cấu trúc:

```text
infrastructure/
└── http/
    └── httpx_client.py
```

```python
import httpx

from domain.fetch.entities import HttpResponse
from domain.fetch.interfaces import HttpClient


class HttpxClient(HttpClient):

    def __init__(
        self,
        timeout: float = 10.0,
    ):
        self._timeout = timeout

    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        proxy: str | None = None,
    ) -> HttpResponse:

        with httpx.Client(
            timeout=self._timeout,
            proxy=proxy,
        ) as client:

            response = client.get(
                url,
                headers=headers,
            )

        return HttpResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            content=response.content,
            url=str(response.url),
        )
```

Bây giờ:

```text
httpx
```

chỉ xuất hiện ở:

```text
infrastructure/http/httpx_client.py
```

---

# 8. Nhưng có một vấn đề lớn

Ta đang:

```python
with httpx.Client(...) as client:
```

mỗi lần gọi:

```python
get()
```

lại tạo Client mới.

Ví dụ crawler:

```text
1000 chapters
     ↓
1000 lần tạo Client
```

Không tốt.

---

# 9. Vì sao nên dùng `httpx.Client` lâu sống?

`httpx.Client` hỗ trợ connection pooling.

Thay vì:

```text
request
 ↓
create connection
 ↓
request
 ↓
close
```

ta muốn:

```text
HttpxClient
     │
     ▼
httpx.Client
     │
     ├── request 1
     ├── request 2
     ├── request 3
     ├── request 4
     └── ...
```

Điều này đặc biệt hữu ích cho crawler.

---

# 10. Refactor `HttpxClient`

```python
import httpx

from domain.fetch.entities import HttpResponse
from domain.fetch.interfaces import HttpClient


class HttpxClient(HttpClient):

    def __init__(
        self,
        timeout: float = 10.0,
    ):
        self._client = httpx.Client(
            timeout=timeout,
        )

    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        proxy: str | None = None,
    ) -> HttpResponse:

        response = self._client.get(
            url,
            headers=headers,
            proxy=proxy,
        )

        return HttpResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            content=response.content,
            url=str(response.url),
        )

    def close(self):
        self._client.close()
```

---

# 11. Nhưng proxy có thể thay đổi

Đây là điểm quan trọng.

Ta có:

```text
request 1 → proxy A
request 2 → proxy B
request 3 → proxy C
```

Không thể thiết kế:

```python
self._client = httpx.Client(
    proxy=proxy_a
)
```

rồi giữ Client đó mãi.

Vì proxy là **per-request**.

Ta cần:

```python
response = self._client.get(
    url,
    proxy=proxy,
)
```

nếu phiên bản `httpx` đang dùng hỗ trợ request-level proxy configuration theo API tương ứng.

Tuy nhiên, tùy phiên bản HTTPX, API proxy có thể khác nhau. Ta sẽ khóa dependency/version trong project và kiểm tra API cụ thể khi triển khai thực tế.

Điểm kiến trúc quan trọng vẫn là:

```text
HttpxClient
    ↓
quản lý chi tiết HTTPX

Fetcher
    ↓
không biết HTTPX
```

---

# 12. Timeout

Crawler không được:

```python
httpx.get(url)
```

mà không có timeout.

Ta muốn:

```text
connect timeout
read timeout
write timeout
pool timeout
```

HTTPX cho phép dùng `httpx.Timeout`.

Infrastructure có thể cấu hình:

```python
timeout = httpx.Timeout(
    connect=5.0,
    read=15.0,
    write=10.0,
    pool=5.0,
)
```

Sau đó:

```python
self._client = httpx.Client(
    timeout=timeout,
)
```

---

# 13. Tạo config riêng

Không nên hard-code:

```python
timeout=10
```

trong class.

Ta có thể tạo:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class HttpClientConfig:

    connect_timeout: float = 5.0
    read_timeout: float = 15.0
    write_timeout: float = 10.0
    pool_timeout: float = 5.0
```

Sau đó Infrastructure:

```python
timeout = httpx.Timeout(
    connect=config.connect_timeout,
    read=config.read_timeout,
    write=config.write_timeout,
    pool=config.pool_timeout,
)
```

Đây là bước đầu để sau này đưa configuration vào:

```text
.env
config.yaml
environment
CLI
```

---

# 14. Headers

Fetcher sẽ truyền:

```python
headers = {
    "User-Agent": user_agent,
}
```

vào:

```python
http_client.get(
    url,
    headers=headers,
)
```

`HttpxClient` chỉ transport.

Nó không quyết định User-Agent.

Đây là **SRP**.

---

# 15. Proxy

Tương tự:

```python
http_client.get(
    url,
    proxy=proxy.url.value,
)
```

`HttpxClient` không quyết định:

```text
proxy nào?
```

Nó chỉ biết:

```text
proxy URL nào được truyền vào?
```

Quyết định proxy thuộc:

```text
ProxyProvider / ProxyPool
```

---

# 16. Exception

Đây là phần cực kỳ quan trọng.

HTTPX có nhiều exception:

```text
HTTPError
├── RequestError
│   ├── TransportError
│   ├── TimeoutException
│   └── NetworkError
└── HTTPStatusError
```

Application không nên biết:

```python
except httpx.ConnectTimeout:
```

vì lại phụ thuộc HTTPX.

Ta tạo exception của hệ thống:

```text
domain/fetch/exceptions.py
```

```python
class FetchError(Exception):
    """Base fetch exception."""


class FetchTimeoutError(FetchError):
    pass


class FetchConnectionError(FetchError):
    pass


class FetchNetworkError(FetchError):
    pass
```

Sau này có thể thêm:

```text
FetchProxyError
FetchHttpError
FetchInvalidUrl
```

---

# 17. Mapping exception

Trong `HttpxClient`:

```python
try:
    response = self._client.get(
        url,
        headers=headers,
        proxy=proxy,
    )

except httpx.TimeoutException as exc:
    raise FetchTimeoutError(
        str(exc)
    ) from exc

except httpx.ConnectError as exc:
    raise FetchConnectionError(
        str(exc)
    ) from exc

except httpx.NetworkError as exc:
    raise FetchNetworkError(
        str(exc)
    ) from exc
```

Application chỉ cần:

```python
try:
    response = http_client.get(...)
except FetchTimeoutError:
    ...
```

Không cần import HTTPX.

---

# 18. Đây chính là Anti-Corruption Layer

Ta đang làm:

```text
                 Infrastructure
                       │
                 ┌─────▼─────┐
                 │   httpx   │
                 └─────┬─────┘
                       │
                 mapping errors
                       │
                       ▼
                 FetchError
                       │
                       ▼
                  Application
```

HTTPX-specific concepts bị chặn ở Infrastructure.

Đây là tư duy rất quan trọng khi xây architecture.

---

# 19. `HttpxClient` phiên bản tốt hơn

Tạm thời:

```python
import httpx

from domain.fetch.entities import HttpResponse
from domain.fetch.exceptions import (
    FetchConnectionError,
    FetchNetworkError,
    FetchTimeoutError,
)
from domain.fetch.interfaces import HttpClient


class HttpxClient(HttpClient):

    def __init__(
        self,
        timeout: httpx.Timeout | None = None,
    ):
        self._client = httpx.Client(
            timeout=timeout,
        )

    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        proxy: str | None = None,
    ) -> HttpResponse:

        try:

            response = self._client.get(
                url,
                headers=headers,
                proxy=proxy,
            )

        except httpx.TimeoutException as exc:
            raise FetchTimeoutError(
                str(exc)
            ) from exc

        except httpx.ConnectError as exc:
            raise FetchConnectionError(
                str(exc)
            ) from exc

        except httpx.NetworkError as exc:
            raise FetchNetworkError(
                str(exc)
            ) from exc

        return HttpResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            content=response.content,
            url=str(response.url),
        )

    def close(self):
        self._client.close()
```

---

# 20. Có nên gọi `raise_for_status()`?

Chưa.

Nếu:

```text
404
403
429
500
```

thì crawler có thể cần biết chính xác status.

Ta giữ:

```python
response.status_code
```

để Application quyết định.

Ví dụ:

```python
if response.status_code == 404:
    ...
```

hoặc:

```python
if response.status_code == 429:
    ...
```

Sau này ta sẽ tạo:

```text
HttpStatusPolicy
```

hoặc `FetchPolicy`.

---

# 21. Test mà không cần Internet

Đây là lợi ích của abstraction.

Ta có:

```python
class FakeHttpClient(HttpClient):

    def __init__(self):
        self.calls = []

    def get(
        self,
        url,
        *,
        headers=None,
        proxy=None,
    ):
        self.calls.append({
            "url": url,
            "headers": headers,
            "proxy": proxy,
        })

        return HttpResponse(
            status_code=200,
            headers={
                "content-type": "text/html"
            },
            content=b"<html>Hello</html>",
            url=url,
        )
```

---

# 22. Test

```python
def test_fetcher_uses_proxy_and_user_agent():

    http_client = FakeHttpClient()

    proxy = Proxy(
        ProxyUrl("http://proxy-a:8080")
    )

    proxy_provider = FakeProxyProvider(proxy)

    ua_provider = FakeUserAgentProvider(
        "UA-1"
    )

    fetcher = Fetcher(
        proxy_provider=proxy_provider,
        user_agent_provider=ua_provider,
        http_client=http_client,
    )

    response = fetcher.fetch(
        "https://example.com"
    )

    assert response.status_code == 200

    assert http_client.calls[0]["proxy"] == (
        "http://proxy-a:8080"
    )

    assert http_client.calls[0]["headers"][
        "User-Agent"
    ] == "UA-1"
```

Không Internet.

Không proxy thật.

Không HTTPX.

---

# 23. Kiến trúc hiện tại

Sau Buổi 5:

```text
                         APPLICATION
                              │
                              ▼
                           Fetcher
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
       ProxyProvider    UAProvider        HttpClient
             │                │                ▲
             ▼                ▼                │
        ProxyPool          UAPool              │
                                              │
                                      ┌───────┴───────┐
                                      │   HttpxClient │
                                      └───────┬───────┘
                                              │
                                              ▼
                                             httpx
```

---

# 24. Boundary cực kỳ rõ

### Domain

```text
Proxy
ProxyUrl
ProxyStatus
FetchError
HttpResponse
HttpClient interface
ProxyProvider interface
UserAgentProvider interface
```

### Application

```text
Fetcher
```

### Infrastructure

```text
ProxyPool
UserAgentPool
HttpxClient
```

---

# 25. Một điều ta chưa làm

Hiện tại Fetcher có thể:

```text
ProxyPool
   ↓
Proxy A
   ↓
HttpClient
   ↓
GET
```

nhưng **chưa kiểm tra Proxy A còn sống trước khi GET chapter**.

Đây là requirement ban đầu của bạn.

Ta sẽ không nhét logic này vào `HttpxClient`.

Ta sẽ tạo riêng:

```text
ProxyHealthChecker
```

với:

```text
ProxyHealthChecker
        ▲
        │
HttpxProxyHealthChecker
        │
        ▼
      httpx
```

Flow sẽ thành:

```text
Fetcher
   │
   ▼
ProxyProvider
   │
   ▼
Proxy A
   │
   ▼
HealthChecker
   │
   ├── DEAD ──→ ProxyPool → Proxy B
   │
   └── ALIVE
         │
         ▼
      HttpClient
         │
         ▼
       GET URL
```

Đây là **Buổi 6 — Proxy Health Checker với `httpx sync`**.

Ta sẽ đặc biệt thiết kế để **health-check không làm bẩn `HttpClient`**, đồng thời xử lý timeout, connection error, HTTP status và cập nhật `Proxy.mark_alive()` / `mark_dead()`.
