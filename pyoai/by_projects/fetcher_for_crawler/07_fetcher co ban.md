# Buổi 7 — Xây dựng Fetcher cơ bản

Hôm nay chúng ta **ghép các thành phần đã học từ Buổi 1 → 6** thành một `Fetcher` hoàn chỉnh.

Mục tiêu:

```text
Crawler
   │
   ▼
 Fetcher
   │
   ├── ProxyProvider
   ├── UserAgentProvider
   ├── ProxyHealthChecker
   └── HttpClient
```

Fetcher sẽ thực hiện một request theo quy trình:

```text
1. Chọn Proxy
       ↓
2. Health Check Proxy
       ↓
3. Proxy sống?
       │
       ├── Không → chọn proxy khác
       │
       └── Có
            ↓
3. Chọn User-Agent
            ↓
4. Tạo request
            ↓
5. HttpClient GET
            ↓
6. Trả FetchResult
```

---

# 1. Trước hết: Fetcher không phải HttpClient

Đây là nguyên tắc rất quan trọng.

`HttpClient` biết:

```text
HTTP
GET
headers
proxy
timeout
connection
```

Còn `Fetcher` biết:

```text
chọn proxy
kiểm tra proxy
chọn User-Agent
retry/rotation sau này
điều phối request
```

Không làm kiểu này:

```python
class Fetcher:
    def __init__(self):
        self.client = httpx.Client()
        self.proxies = [...]
        self.user_agents = [...]
```

Đây là **God Object**.

---

# 2. Thiết kế `FetchRequest`

Fetcher cần đầu vào.

Ta tạo Value Object:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class FetchRequest:
    url: str
```

Sau này có thể mở rộng:

```python
@dataclass(frozen=True)
class FetchRequest:
    url: str
    headers: dict[str, str] | None = None
```

Nhưng hiện tại chưa cần quá nhiều thứ.

---

# 3. Thiết kế `FetchResult`

Fetcher không nên trả trực tiếp `httpx.Response`.

Ta tạo:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class FetchResult:
    url: str
    status_code: int
    headers: dict[str, str]
    content: bytes

    @property
    def text(self) -> str:
        return self.content.decode(
            "utf-8",
            errors="replace",
        )
```

Bây giờ Application chỉ biết:

```text
FetchResult
```

chứ không biết:

```text
httpx.Response
```

---

# 4. Quan hệ giữa `HttpResponse` và `FetchResult`

Ta đang có:

```text
HttpClient
     ↓
HttpResponse
     ↓
Fetcher
     ↓
FetchResult
```

Ví dụ:

```python
response = self._http_client.get(...)
```

sau đó:

```python
return FetchResult(
    url=response.url,
    status_code=response.status_code,
    headers=response.headers,
    content=response.content,
)
```

Điều này tạo ra boundary rất rõ:

```text
Infrastructure
     │
     │ HttpResponse
     ▼
   Fetcher
     │
     │ FetchResult
     ▼
Application
```

---

# 5. Thiết kế Fetcher

Ta bắt đầu với constructor:

```python
class Fetcher:
    def __init__(
        self,
        proxy_provider: ProxyProvider,
        user_agent_provider: UserAgentProvider,
        health_checker: ProxyHealthChecker,
        http_client: HttpClient,
    ):
        self._proxy_provider = proxy_provider
        self._user_agent_provider = user_agent_provider
        self._health_checker = health_checker
        self._http_client = http_client
```

Fetcher hoàn toàn không biết implementation cụ thể.

Không có:

```python
httpx.Client
```

Không có:

```python
ProxyPool(...)
```

Không có:

```python
UserAgentPool(...)
```

Đây chính là **Dependency Injection**.

---

# 6. Method `fetch()`

Phiên bản đầu tiên:

```python
class Fetcher:
    def __init__(
        self,
        proxy_provider: ProxyProvider,
        user_agent_provider: UserAgentProvider,
        health_checker: ProxyHealthChecker,
        http_client: HttpClient,
    ):
        self._proxy_provider = proxy_provider
        self._user_agent_provider = user_agent_provider
        self._health_checker = health_checker
        self._http_client = http_client

    def fetch(self, request: FetchRequest) -> FetchResult:

        proxy = self._proxy_provider.get_proxy()

        health = self._health_checker.check(proxy)

        if not health.reachable:
            proxy.mark_dead()
            raise RuntimeError("Proxy is dead")

        proxy.mark_alive()

        user_agent = self._user_agent_provider.get_user_agent()

        headers = {
            "User-Agent": user_agent,
        }

        response = self._http_client.get(
            request.url,
            headers=headers,
            proxy=proxy.url.value,
        )

        return FetchResult(
            url=response.url,
            status_code=response.status_code,
            headers=response.headers,
            content=response.content,
        )
```

Đây là Fetcher cơ bản.

---

# 7. Nhưng có một vấn đề

Nếu:

```text
Proxy A → DEAD
```

Fetcher hiện tại:

```text
A
↓
health check
↓
dead
↓
throw error
```

Trong khi chúng ta muốn:

```text
A
↓
dead
↓
B
↓
health check
↓
alive
↓
fetch
```

Đây chính là lý do Buổi 8 sẽ học **Proxy Rotation**.

Tuy nhiên, trước khi sang rotation, ta nên hiểu rõ lifecycle của **một request**.

---

# 8. Request Lifecycle

Một request:

```text
FetchRequest
     │
     ▼
ProxyProvider
     │
     ▼
Proxy
     │
     ▼
HealthChecker
     │
     ▼
ProxyHealthResult
     │
     ▼
UserAgentProvider
     │
     ▼
Headers
     │
     ▼
HttpClient
     │
     ▼
HttpResponse
     │
     ▼
FetchResult
```

Đây là flow trung tâm của Fetcher.

---

# 9. Tạo `FetchContext`

Ở Buổi 4 chúng ta đã có ý tưởng:

```python
@dataclass(frozen=True)
class FetchContext:
    proxy: Proxy
    user_agent: str
```

Bây giờ nó trở nên hữu ích.

```python
@dataclass(frozen=True)
class FetchContext:
    proxy: Proxy
    user_agent: str
```

Fetcher có thể tạo context:

```python
proxy = self._proxy_provider.get_proxy()

health = self._health_checker.check(proxy)

if not health.reachable:
    proxy.mark_dead()
    raise RuntimeError("Proxy is dead")

proxy.mark_alive()

user_agent = self._user_agent_provider.get_user_agent()

context = FetchContext(
    proxy=proxy,
    user_agent=user_agent,
)
```

Sau đó:

```python
headers = {
    "User-Agent": context.user_agent,
}
```

và:

```python
proxy = context.proxy.url.value
```

---

# 10. Tách `build_context()`

Fetcher bắt đầu hơi dài.

Ta có thể tách:

```python
def _build_context(self) -> FetchContext:

    proxy = self._proxy_provider.get_proxy()

    health = self._health_checker.check(proxy)

    if not health.reachable:
        proxy.mark_dead()
        raise RuntimeError("Proxy is dead")

    proxy.mark_alive()

    user_agent = self._user_agent_provider.get_user_agent()

    return FetchContext(
        proxy=proxy,
        user_agent=user_agent,
    )
```

Fetcher:

```python
def fetch(self, request: FetchRequest) -> FetchResult:

    context = self._build_context()

    headers = {
        "User-Agent": context.user_agent,
    }

    response = self._http_client.get(
        request.url,
        headers=headers,
        proxy=context.proxy.url.value,
    )

    return FetchResult(
        url=response.url,
        status_code=response.status_code,
        headers=response.headers,
        content=response.content,
    )
```

Dễ đọc hơn rất nhiều.

---

# 11. Tạo exception riêng

Không nên:

```python
raise RuntimeError("Proxy is dead")
```

Ta tạo exception thuộc Application/Domain:

```python
class FetchError(Exception):
    pass
```

và:

```python
class NoHealthyProxyError(FetchError):
    pass
```

Hiện tại:

```python
if not health.reachable:
    proxy.mark_dead()
    raise NoHealthyProxyError(f"Proxy is unavailable: {proxy.url.value}")
```

Sau này rotation sẽ không throw ngay mà tiếp tục thử proxy khác.

---

# 12. Không bắt lỗi quá rộng

Không nên:

```python
try:
    response = self._http_client.get(...)
except Exception:
    ...
```

Vì như vậy ta có thể vô tình nuốt:

```text
ProgrammingError
TypeError
AttributeError
DatabaseError
```

Chỉ xử lý các exception mà abstraction định nghĩa:

```python
try:
    response = self._http_client.get(...)
except FetchTimeoutError:
    ...
except FetchConnectionError:
    ...
```

Hoặc để `HttpClient` chuyển tất cả HTTPX-specific errors thành hierarchy:

```text
FetchError
├── FetchTimeoutError
├── FetchConnectionError
└── FetchNetworkError
```

Đây chính là **Anti-Corruption Layer** đã học ở Buổi 5.

---

# 13. Fake dependencies để test

Fetcher lúc này có 4 dependency.

Ta không cần Internet.

### Fake ProxyProvider

```python
class FakeProxyProvider(ProxyProvider):
    def __init__(self, proxy: Proxy):
        self.proxy = proxy

    def get_proxy(self) -> Proxy:
        return self.proxy
```

### Fake UA Provider

```python
class FakeUserAgentProvider(UserAgentProvider):
    def __init__(self, user_agent: str):
        self.user_agent = user_agent

    def get_user_agent(self) -> str:
        return self.user_agent
```

### Fake HealthChecker

```python
class FakeProxyHealthChecker(ProxyHealthChecker):
    def __init__(self, result: ProxyHealthResult):
        self.result = result

    def check(self, proxy: Proxy) -> ProxyHealthResult:
        return self.result
```

### Fake HttpClient

```python
class FakeHttpClient(HttpClient):
    def __init__(self, response: HttpResponse):
        self.response = response

    def get(
        self,
        url: str,
        *,
        headers=None,
        proxy=None,
    ) -> HttpResponse:

        return self.response
```

---

# 14. Test Fetcher

Ta tạo proxy:

```python
proxy = Proxy(url=ProxyUrl("http://127.0.0.1:8080"))
```

Fake response:

```python
response = HttpResponse(
    status_code=200,
    headers={
        "content-type": "text/html",
    },
    content=b"<h1>Hello</h1>",
    url="https://example.com",
)
```

Inject dependencies:

```python
fetcher = Fetcher(
    proxy_provider=FakeProxyProvider(proxy),
    user_agent_provider=FakeUserAgentProvider("Mozilla/5.0"),
    health_checker=FakeProxyHealthChecker(
        ProxyHealthResult(
            reachable=True,
            status_code=200,
        )
    ),
    http_client=FakeHttpClient(response),
)
```

Fetch:

```python
result = fetcher.fetch(FetchRequest(url="https://example.com"))
```

Assert:

```python
assert result.status_code == 200
assert result.text == "<h1>Hello</h1>"
```

---

# 15. Test proxy chết

```python
health_checker = FakeProxyHealthChecker(
    ProxyHealthResult(
        reachable=False,
    )
)
```

Sau đó:

```python
with pytest.raises(NoHealthyProxyError):
    fetcher.fetch(FetchRequest(url="https://example.com"))
```

Và kiểm tra:

```python
assert proxy.status == ProxyStatus.DEAD
```

---

# 16. Test User-Agent

Fake client nên ghi lại request:

```python
class FakeHttpClient(HttpClient):
    def __init__(self, response: HttpResponse):
        self.response = response
        self.last_url = None
        self.last_headers = None
        self.last_proxy = None

    def get(
        self,
        url: str,
        *,
        headers=None,
        proxy=None,
    ) -> HttpResponse:

        self.last_url = url
        self.last_headers = headers
        self.last_proxy = proxy

        return self.response
```

Test:

```python
assert client.last_headers["User-Agent"] == "Mozilla/5.0"
```

và:

```python
assert client.last_proxy == "http://127.0.0.1:8080"
```

Như vậy ta chứng minh được:

```text
ProxyProvider
       ↓
Fetcher
       ↓
HttpClient
```

đã truyền đúng dependency.

---

# 17. Test quan trọng nhất

Ta muốn kiểm tra toàn bộ flow:

```text
Proxy
  ↓
Health Check
  ↓
UA
  ↓
HTTP
```

Test:

```python
def test_fetcher_flow():

    proxy = Proxy(url=ProxyUrl("http://127.0.0.1:8080"))

    client = FakeHttpClient(
        HttpResponse(
            status_code=200,
            headers={},
            content=b"hello",
            url="https://example.com",
        )
    )

    fetcher = Fetcher(
        proxy_provider=FakeProxyProvider(proxy),
        user_agent_provider=FakeUserAgentProvider("Test-Agent"),
        health_checker=FakeProxyHealthChecker(
            ProxyHealthResult(
                reachable=True,
                status_code=200,
            )
        ),
        http_client=client,
    )

    result = fetcher.fetch(FetchRequest(url="https://example.com"))

    assert result.status_code == 200
    assert result.text == "hello"

    assert client.last_proxy == ("http://127.0.0.1:8080")

    assert client.last_headers["User-Agent"] == ("Test-Agent")
```

Đây là một **unit test thực sự có giá trị** vì không phụ thuộc:

* Internet
* website thật
* proxy thật
* HTTPX
* database

---

# 18. Architecture hiện tại

Sau Buổi 7:

```text
                    CRAWLER
                       │
                       ▼
                    FETCHER
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
  ProxyProvider   UAProvider   HealthChecker
          │            │            │
          ▼            ▼            ▼
      ProxyPool      UAPool      HealthResult
                       │
                       │
                       ▼
                  FetchContext
                       │
                       ▼
                   HttpClient
                       │
                       ▼
                  HttpxClient
                       │
                       ▼
                     httpx
```

---

# 19. Một vấn đề kiến trúc bắt đầu xuất hiện

Fetcher hiện tại:

```text
Proxy A
 ↓
dead
 ↓
throw
```

Nhưng yêu cầu crawler thực tế của chúng ta là:

```text
Proxy A → dead
Proxy B → dead
Proxy C → alive
```

Fetcher phải tự động:

```text
A
 ↓
health check
 ↓
dead
 ↓
B
 ↓
health check
 ↓
dead
 ↓
C
 ↓
health check
 ↓
alive
 ↓
GET
```

Đây chính là:

# **Buổi 8 — Proxy Rotation**

Ta sẽ thiết kế cẩn thận:

```text
ProxyPool
     ↓
candidate
     ↓
HealthChecker
     ↓
dead?
 ┌───┴────┐
 │        │
YES       NO
 │        │
 ▼        ▼
next     fetch
proxy
```

và đặc biệt xử lý trường hợp:

```text
A DEAD
B DEAD
C DEAD
```

mà **không được `while True` vô hạn**.

Ngoài ra, ở Buổi 8 ta sẽ bắt đầu tách rõ:

```text
Proxy selection
      ≠
Proxy health checking
      ≠
HTTP fetching
```

Đây là bước rất quan trọng để Fetcher sau này không biến thành một **God Object**.
