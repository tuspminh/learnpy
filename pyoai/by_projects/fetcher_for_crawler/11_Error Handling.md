# 📘 Buổi 11 — Error Handling cho Fetcher

Hôm nay chúng ta tiếp tục **đúng roadmap Fetcher**:

```text
Buổi 10 — Retry
        ↓
👉 Buổi 11 — Error Handling
        ↓
Buổi 12 — Fetch Policy
        ↓
Buổi 13 — Domain Service
```

Mục tiêu của buổi này là xây dựng một hệ thống lỗi **có phân loại**, để Fetcher biết:

* lỗi nào do network?
* lỗi nào do proxy?
* lỗi nào do server?
* lỗi nào do target website?
* lỗi nào được retry?
* lỗi nào phải đổi proxy?
* lỗi nào phải dừng ngay?

---

# 1. Vấn đề của cách xử lý lỗi đơn giản

Ví dụ chúng ta có:

```python
try:
    response = client.get(url)
except Exception:
    retry()
```

Cách này **rất nguy hiểm**.

Vì:

```text
Timeout
ConnectionError
403
404
429
500
Proxy chết
URL sai
Programming Bug
```

đều có thể bị gom thành:

```text
Exception
```

Fetcher không thể biết nên làm gì.

Ví dụ:

```text
404
```

Không nên retry vô hạn.

Trong khi:

```text
500
```

có thể retry.

Còn:

```text
Proxy connection timeout
```

có thể cần:

```text
đánh dấu proxy DEAD
→ đổi proxy
→ retry request
```

Vì vậy chúng ta cần **Error Classification**.

---

# 2. Kiến trúc Error Handling

Kiến trúc hôm nay:

```text
                 ┌─────────────────────┐
                 │      httpx          │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │    HttpxClient      │
                 │ Infrastructure      │
                 └──────────┬──────────┘
                            │
                    map exceptions
                            │
                            ▼
                 ┌─────────────────────┐
                 │    FetchError       │
                 │ Application Error   │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │  ErrorClassifier    │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │   ErrorKind         │
                 │   retryable         │
                 │   proxy_related     │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │    FetchPolicy      │
                 │      Buổi 12        │
                 └─────────────────────┘
```

Điểm quan trọng:

> `httpx` chỉ xuất hiện ở Infrastructure.

Domain/Application **không biết `httpx.ConnectError` là gì**.

---

# 3. Exception Hierarchy

Chúng ta bắt đầu bằng exception hierarchy.

```text
FetchError
│
├── FetchTimeoutError
│
├── FetchConnectionError
│
├── FetchNetworkError
│
├── FetchHttpError
│   │
│   ├── TooManyRequestsError
│   │
│   ├── ClientError
│   │
│   └── ServerError
│
└── NoHealthyProxyError
```

---

# 4. Base `FetchError`

Tạo:

```text
fetcher/
└── domain/
    └── errors.py
```

Code:

```python
class FetchError(Exception):
    """Base exception for all fetch-related errors."""

    def __init__(
        self,
        message: str,
        *,
        url: str | None = None,
    ):
        super().__init__(message)
        self.url = url
```

Ví dụ:

```python
raise FetchError(
    "Fetch failed",
    url="https://example.com",
)
```

---

# 5. Timeout Error

```python
class FetchTimeoutError(FetchError):
    """Request timed out."""
```

Sử dụng:

```python
raise FetchTimeoutError(
    "Request timed out",
    url=url,
)
```

---

# 6. Connection Error

```python
class FetchConnectionError(FetchError):
    """Connection could not be established."""
```

Ví dụ:

```text
Proxy không kết nối được
DNS failure
TCP connection failure
```

---

# 7. Network Error

```python
class FetchNetworkError(FetchError):
    """General network error."""
```

---

# 8. HTTP Error

Bây giờ đến HTTP error.

```python
class FetchHttpError(FetchError):
    """HTTP-level error."""

    def __init__(
        self,
        message: str,
        *,
        url: str,
        status_code: int,
    ):
        super().__init__(
            message,
            url=url,
        )
        self.status_code = status_code
```

Ví dụ:

```python
raise FetchHttpError(
    "HTTP error",
    url=url,
    status_code=500,
)
```

---

# 9. Các HTTP Error cụ thể

## 9.1 429

```python
class TooManyRequestsError(FetchHttpError):
    """HTTP 429."""
```

---

## 9.2 Client Error

```python
class ClientError(FetchHttpError):
    """HTTP 4xx error."""
```

Ví dụ:

```text
400
401
403
404
```

---

## 9.3 Server Error

```python
class ServerError(FetchHttpError):
    """HTTP 5xx error."""
```

Ví dụ:

```text
500
502
503
504
```

---

# 10. No Healthy Proxy

Đây là lỗi đặc biệt.

```python
class NoHealthyProxyError(FetchError):
    """No healthy proxy is available."""
```

Ví dụ:

```text
Proxy A DEAD
Proxy B DEAD
Proxy C DEAD
```

thì:

```python
raise NoHealthyProxyError("No healthy proxy available")
```

---

# 11. Full `errors.py`

Đây là version hoàn chỉnh đầu tiên:

```python
class FetchError(Exception):
    """Base exception for all fetch-related errors."""

    def __init__(
        self,
        message: str,
        *,
        url: str | None = None,
    ):
        super().__init__(message)
        self.url = url


class FetchTimeoutError(FetchError):
    """Request timed out."""


class FetchConnectionError(FetchError):
    """Connection could not be established."""


class FetchNetworkError(FetchError):
    """General network error."""


class FetchHttpError(FetchError):
    """HTTP-level error."""

    def __init__(
        self,
        message: str,
        *,
        url: str,
        status_code: int,
    ):
        super().__init__(
            message,
            url=url,
        )
        self.status_code = status_code


class TooManyRequestsError(FetchHttpError):
    """HTTP 429."""


class ClientError(FetchHttpError):
    """HTTP 4xx error."""


class ServerError(FetchHttpError):
    """HTTP 5xx error."""


class NoHealthyProxyError(FetchError):
    """No healthy proxy is available."""
```

---

# 12. Error Classification

Bây giờ có một vấn đề khác.

Có exception chưa đủ.

Fetcher cần biết:

```text
Lỗi này có retry không?
Lỗi này có liên quan proxy không?
Lỗi này thuộc target/server?
```

Chúng ta tạo:

```python
from enum import Enum, auto
```

và:

```python
class ErrorKind(Enum):
    TIMEOUT = auto()
    CONNECTION = auto()
    NETWORK = auto()

    RATE_LIMIT = auto()

    HTTP_CLIENT = auto()
    HTTP_SERVER = auto()

    PROXY = auto()

    FATAL = auto()
```

---

# 13. ErrorInfo

Thay vì chỉ trả về `ErrorKind`, ta có thể trả về một object.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class FetchErrorInfo:
    kind: ErrorKind

    retryable: bool

    proxy_related: bool

    status_code: int | None = None
```

Ví dụ:

```python
FetchErrorInfo(
    kind=ErrorKind.TIMEOUT,
    retryable=True,
    proxy_related=True,
)
```

Fetcher có thể hiểu:

```text
TIMEOUT
↓
retryable = True
↓
proxy_related = True
↓
đổi proxy
```

---

# 14. ErrorClassifier

Tạo abstraction:

```python
from abc import ABC, abstractmethod


class ErrorClassifier(ABC):
    @abstractmethod
    def classify(
        self,
        error: Exception,
    ) -> FetchErrorInfo:
        raise NotImplementedError
```

Đây là DIP.

Fetcher không cần biết implementation cụ thể.

---

# 15. DefaultErrorClassifier

```python
class DefaultErrorClassifier(ErrorClassifier):
    def classify(
        self,
        error: Exception,
    ) -> FetchErrorInfo:

        if isinstance(error, FetchTimeoutError):
            return FetchErrorInfo(
                kind=ErrorKind.TIMEOUT,
                retryable=True,
                proxy_related=True,
            )

        if isinstance(error, FetchConnectionError):
            return FetchErrorInfo(
                kind=ErrorKind.CONNECTION,
                retryable=True,
                proxy_related=True,
            )

        if isinstance(error, FetchNetworkError):
            return FetchErrorInfo(
                kind=ErrorKind.NETWORK,
                retryable=True,
                proxy_related=True,
            )

        if isinstance(error, TooManyRequestsError):
            return FetchErrorInfo(
                kind=ErrorKind.RATE_LIMIT,
                retryable=True,
                proxy_related=False,
                status_code=429,
            )

        if isinstance(error, ServerError):
            return FetchErrorInfo(
                kind=ErrorKind.HTTP_SERVER,
                retryable=True,
                proxy_related=False,
                status_code=error.status_code,
            )

        if isinstance(error, ClientError):
            return FetchErrorInfo(
                kind=ErrorKind.HTTP_CLIENT,
                retryable=False,
                proxy_related=False,
                status_code=error.status_code,
            )

        return FetchErrorInfo(
            kind=ErrorKind.FATAL,
            retryable=False,
            proxy_related=False,
        )
```

---

# 16. Bảng phân loại

Sau khi có classifier:

| Error           | Retry |  Proxy liên quan |
| --------------- | ----: | ---------------: |
| Timeout         |     ✅ |           Có thể |
| Connection      |     ✅ |               Có |
| Network         |     ✅ |           Có thể |
| 429             |     ✅ | Không nhất thiết |
| 500             |     ✅ |            Không |
| 502             |     ✅ |           Có thể |
| 503             |     ✅ |            Không |
| 404             |     ❌ |            Không |
| 403             |     ❌ | Không nhất thiết |
| 401             |     ❌ |            Không |
| Programming bug |     ❌ |            Không |

Điểm rất quan trọng:

> Không phải mọi lỗi network đều chắc chắn do proxy.

Ví dụ:

```text
Proxy ALIVE
        ↓
GET example.com
        ↓
500
```

`500` thường là lỗi của server target.

Không nên lập tức:

```python
proxy.mark_dead()
```

---

# 17. Phân biệt Proxy Failure và Target Failure

Đây là phần cực kỳ quan trọng đối với crawler của chúng ta.

### Trường hợp A

```text
Proxy
 ↓
X connection
```

Ví dụ:

```text
ConnectTimeout
ConnectError
```

Khả năng cao:

```text
Proxy có vấn đề
```

→ có thể đánh dấu proxy DEAD.

---

### Trường hợp B

```text
Proxy
 ↓
Target
 ↓
403
```

Proxy vẫn hoạt động.

```text
Proxy = ALIVE
Target = từ chối
```

Không nên đánh dấu proxy DEAD.

---

### Trường hợp C

```text
Proxy
 ↓
Target
 ↓
500
```

Có thể là:

```text
Target server lỗi
```

Không nên đánh dấu proxy DEAD chỉ vì 500.

---

### Trường hợp D

```text
Proxy
 ↓
Target
 ↓
429
```

Đây là:

```text
Rate limit
```

Có thể:

```text
backoff
↓
đợi
↓
retry
```

hoặc chính sách có thể chọn proxy khác.

Buổi 12 chúng ta sẽ quyết định việc này bằng `FetchPolicy`.

---

# 18. HTTPX Anti-Corruption Layer

Đây là nơi rất quan trọng trong DDD.

Không được để:

```python
FetchError
```

phụ thuộc vào:

```python
httpx.ConnectError
```

Sai:

```python
class FetchError(httpx.ConnectError): ...
```

Hoặc:

```python
def fetch() -> httpx.Response:
```

Application layer sẽ bị phụ thuộc `httpx`.

---

# 19. HttpxClient mapping

Infrastructure:

```python
import httpx
```

Sau đó:

```python
class HttpxClient(HttpClient):
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
                "Request timed out",
                url=url,
            ) from exc

        except httpx.ConnectError as exc:
            raise FetchConnectionError(
                "Connection failed",
                url=url,
            ) from exc

        except httpx.NetworkError as exc:
            raise FetchNetworkError(
                "Network error",
                url=url,
            ) from exc

        return HttpResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            content=response.content,
            url=str(response.url),
        )
```

Như vậy:

```text
httpx
 ↓
HttpxClient
 ↓
FetchTimeoutError
 ↓
Application
```

Application không cần biết `httpx` tồn tại.

---

# 20. Một điểm rất quan trọng: HTTP status

Hiện tại chúng ta **chưa cần** làm:

```python
response.raise_for_status()
```

trong `HttpxClient`.

Tại sao?

Vì:

```text
HTTP 200
HTTP 403
HTTP 404
HTTP 429
HTTP 500
```

đều là **response hợp lệ về mặt transport**.

`HttpClient` nên trả:

```python
HttpResponse
```

Application/FetchPolicy mới quyết định:

```text
200 → success

403 → fatal

404 → not found

429 → retry/backoff

500 → retry

503 → retry
```

Kiến trúc:

```text
HttpxClient
     │
     ▼
HttpResponse
     │
     ▼
Application
     │
     ▼
ErrorClassifier / FetchPolicy
```

Đây là separation of concerns tốt hơn.

---

# 21. Classify HTTP status

Ta có thể tạo helper:

```python
def classify_status(
    status_code: int,
) -> FetchErrorInfo | None:

    if status_code == 429:
        return FetchErrorInfo(
            kind=ErrorKind.RATE_LIMIT,
            retryable=True,
            proxy_related=False,
            status_code=429,
        )

    if 500 <= status_code <= 599:
        return FetchErrorInfo(
            kind=ErrorKind.HTTP_SERVER,
            retryable=True,
            proxy_related=False,
            status_code=status_code,
        )

    if 400 <= status_code <= 499:
        return FetchErrorInfo(
            kind=ErrorKind.HTTP_CLIENT,
            retryable=False,
            proxy_related=False,
            status_code=status_code,
        )

    return None
```

Sau này `FetchPolicy` sẽ dùng logic này.

---

# 22. Không catch `Exception` một cách bừa bãi

Không nên:

```python
try:
    ...
except Exception:
    retry()
```

Vì nó có thể nuốt:

```text
AttributeError
TypeError
KeyError
Programming bug
Database error
MemoryError
```

Ví dụ bạn viết nhầm:

```python
proxy.url.valeu
```

thay vì:

```python
proxy.url.value
```

Nếu:

```python
except Exception:
    retry()
```

Fetcher có thể retry lỗi code của chính bạn.

Rất khó debug.

---

# 23. Cách tốt hơn

Chỉ catch các lỗi mà ta thực sự xử lý được:

```python
try:
    response = self._http_client.get(...)
except (
    FetchTimeoutError,
    FetchConnectionError,
    FetchNetworkError,
) as exc:
    ...
```

Hoặc:

```python
except FetchError as exc:
    ...
```

nếu Application thực sự xử lý toàn bộ `FetchError`.

---

# 24. Error Handling Flow

Fetcher sau Buổi 11 sẽ có flow:

```text
                 Fetch Request
                       │
                       ▼
                 Select Proxy
                       │
                       ▼
                 Health Check
                       │
                       ▼
                 Select User-Agent
                       │
                       ▼
                  HTTP Request
                       │
             ┌─────────┴──────────┐
             │                    │
           success              error
             │                    │
             ▼                    ▼
        FetchResult         ErrorClassifier
                                  │
                                  ▼
                            FetchErrorInfo
                                  │
                                  ▼
                             FetchPolicy
                            (Buổi 12)
```

---

# 25. Test ErrorClassifier

Đây là phần chúng ta nên test ngay.

## Test timeout

```python
def test_timeout_is_retryable():
    classifier = DefaultErrorClassifier()

    error = FetchTimeoutError(
        "timeout",
        url="https://example.com",
    )

    info = classifier.classify(error)

    assert info.kind == ErrorKind.TIMEOUT
    assert info.retryable is True
    assert info.proxy_related is True
```

---

## Test 404

```python
def test_404_is_not_retryable():
    classifier = DefaultErrorClassifier()

    error = ClientError(
        "Not found",
        url="https://example.com",
        status_code=404,
    )

    info = classifier.classify(error)

    assert info.kind == ErrorKind.HTTP_CLIENT
    assert info.retryable is False
    assert info.proxy_related is False
```

---

## Test 500

```python
def test_500_is_retryable():
    classifier = DefaultErrorClassifier()

    error = ServerError(
        "Server error",
        url="https://example.com",
        status_code=500,
    )

    info = classifier.classify(error)

    assert info.kind == ErrorKind.HTTP_SERVER
    assert info.retryable is True
    assert info.proxy_related is False
```

---

## Test 429

```python
def test_429_is_retryable():
    classifier = DefaultErrorClassifier()

    error = TooManyRequestsError(
        "Rate limited",
        url="https://example.com",
        status_code=429,
    )

    info = classifier.classify(error)

    assert info.kind == ErrorKind.RATE_LIMIT
    assert info.retryable is True
    assert info.proxy_related is False
```

---

# 26. Test Unknown Exception

Đây là test rất quan trọng.

```python
def test_unknown_exception_is_fatal():
    classifier = DefaultErrorClassifier()

    error = ValueError("bug")

    info = classifier.classify(error)

    assert info.kind == ErrorKind.FATAL
    assert info.retryable is False
    assert info.proxy_related is False
```

Điều này giúp chúng ta tránh:

```text
bug trong code
    ↓
retry
    ↓
retry
    ↓
retry
```

---

# 27. Cấu trúc project sau Buổi 11

Hiện tại có thể tổ chức:

```text
fetcher/
│
├── domain/
│   ├── models/
│   │   ├── proxy.py
│   │   └── fetch.py
│   │
│   ├── errors.py
│   │
│   └── enums.py
│
├── application/
│   ├── fetcher.py
│   ├── retry.py
│   ├── error_classifier.py
│   └── ...
│
├── infrastructure/
│   └── http/
│       └── httpx_client.py
│
└── tests/
    ├── test_proxy.py
    ├── test_proxy_pool.py
    ├── test_user_agent.py
    ├── test_retry.py
    └── test_error_classifier.py
```

---

# 28. DDD + SOLID nhìn như thế nào?

### Domain

```text
Proxy
ProxyUrl
ProxyStatus
FetchError
ErrorKind
```

Không biết:

```text
httpx
requests
aiohttp
```

---

### Application

```text
Fetcher
RetryPolicy
ErrorClassifier
FetchPolicy
```

chỉ biết abstraction.

---

### Infrastructure

```text
HttpxClient
```

biết:

```python
import httpx
```

---

# 29. Dependency Direction

Đây là nguyên tắc quan trọng:

```text
Infrastructure
      │
      │ implements
      ▼
Application abstractions
      │
      ▼
Domain
```

Không được:

```text
Domain
  ↓
httpx
```

Sai kiến trúc.

Đúng:

```text
        Domain
          ▲
          │
    Application
          ▲
          │
   Infrastructure
```

Infrastructure phụ thuộc vào abstraction phía trong.

---

# 30. Một quyết định kiến trúc rất quan trọng

Ở Buổi 11, chúng ta **không để ErrorClassifier tự retry**.

Sai:

```python
classifier.classify()
    ↓
retry()
```

Classifier chỉ trả lời:

```text
"Lỗi này là gì?"
```

Nó không quyết định hành động.

Ví dụ:

```python
info = classifier.classify(error)
```

Kết quả:

```text
kind = TIMEOUT
retryable = True
proxy_related = True
```

Sau đó:

```text
FetchPolicy
```

mới quyết định:

```text
retry?
đổi proxy?
backoff?
dừng?
```

Đây chính là lý do chúng ta có **Buổi 12 — Fetch Policy**.

---

# 31. Tư duy kiến trúc cần nhớ

Fetcher của chúng ta đang dần hình thành:

```text
                    Fetcher
                       │
       ┌───────────────┼────────────────┐
       │               │                │
       ▼               ▼                ▼
 ProxyProvider    UAProvider      HealthChecker
       │
       ▼
     Proxy

                       │
                       ▼
                  HttpClient
                       │
                       ▼
                   Response
                       │
                       ▼
               ErrorClassifier
                       │
                       ▼
                 ErrorInfo
                       │
                       ▼
                 FetchPolicy
```

Mỗi component có **một trách nhiệm rõ ràng**.

---

# 32. Những gì đã hoàn thành

Sau Buổi 11:

```text
✅ Proxy Domain Model
✅ ProxyPool
✅ User-Agent Pool
✅ HttpClient abstraction
✅ httpx sync adapter
✅ Proxy Health Checker
✅ Basic Fetcher
✅ Proxy Rotation
✅ User-Agent Rotation
✅ Retry
✅ Retry Delay
✅ Exception Hierarchy
✅ Error Classification
```

Còn thiếu:

```text
⬜ Fetch Policy
⬜ Domain Service
⬜ Application Service
⬜ Dependency Injection
⬜ Proxy Repository
⬜ Proxy State nâng cao
⬜ Circuit Breaker
⬜ Rate Limiting
⬜ Fetch Orchestration
⬜ Testing toàn hệ thống
```

---

# 🎯 Bài tập Buổi 11

Hãy tự implement 5 phần sau:

### Bài 1

Tạo:

```text
errors.py
```

với hierarchy:

```text
FetchError
├── FetchTimeoutError
├── FetchConnectionError
├── FetchNetworkError
├── FetchHttpError
│   ├── TooManyRequestsError
│   ├── ClientError
│   └── ServerError
└── NoHealthyProxyError
```

### Bài 2

Tạo:

```python
ErrorKind
```

với:

```text
TIMEOUT
CONNECTION
NETWORK
RATE_LIMIT
HTTP_CLIENT
HTTP_SERVER
PROXY
FATAL
```

### Bài 3

Implement:

```python
FetchErrorInfo
```

### Bài 4

Implement:

```python
DefaultErrorClassifier
```

và test:

```text
Timeout → retry
Connection → retry
429 → retry
500 → retry
404 → no retry
403 → no retry
unknown exception → fatal
```

### Bài 5 — quan trọng nhất

Tự trả lời:

> Nếu proxy A health check thành công, nhưng request đến website truyện trả về `403`, có nên `proxy.mark_dead()` không?

**Đáp án:** Không nên mặc định làm vậy.

```text
Health Check
     ↓
Proxy hoạt động
     ↓
Target trả 403
     ↓
Target từ chối request
     ↓
Proxy vẫn có thể ALIVE
```

Đây là một trong những nguyên tắc quan trọng nhất khi xây crawler có proxy.

---

## 🔜 Buổi 12 — Fetch Policy

Buổi tiếp theo chúng ta sẽ ghép toàn bộ những thứ đã học thành **chính sách quyết định của Fetcher**:

```text
Error
  ↓
ErrorClassifier
  ↓
FetchErrorInfo
  ↓
FetchPolicy
  ├── Retry?
  ├── Rotate Proxy?
  ├── Mark Proxy DEAD?
  ├── Backoff?
  └── Stop?
```

Và lúc đó chúng ta sẽ xử lý được các tình huống thực tế như:

```text
Proxy A → timeout
       ↓
mark DEAD
       ↓
Proxy B
       ↓
500
       ↓
retry same proxy
       ↓
503
       ↓
backoff
       ↓
retry
       ↓
200
```

Đây sẽ là bước quan trọng để Fetcher chuyển từ **“chạy được”** sang **“có policy rõ ràng và có thể mở rộng”**.
