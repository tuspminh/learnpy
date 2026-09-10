# Buổi 8 — Proxy Rotation

Ở Buổi 7, `Fetcher` mới xử lý được **một proxy**:

```text
Proxy A
   ↓
Health Check
   ↓
DEAD
   ↓
Error
```

Trong crawler thực tế, ta muốn:

```text
Proxy A
   ↓
DEAD
   ↓
Proxy B
   ↓
DEAD
   ↓
Proxy C
   ↓
ALIVE
   ↓
Fetch
```

Hôm nay chúng ta xây dựng **Proxy Rotation** nhưng vẫn giữ đúng DDD + SOLID.

---

# 1. Mục tiêu

Fetcher phải làm được:

```text
Fetch(url)
   │
   ▼
ProxyPool
   │
   ├── A → DEAD
   │
   ├── B → DEAD
   │
   └── C → ALIVE
             │
             ▼
        User-Agent
             │
             ▼
         HttpClient
             │
             ▼
            GET
```

Và đặc biệt:

```text
A DEAD
B DEAD
C DEAD
```

thì phải kết thúc rõ ràng:

```python
NoHealthyProxyError
```

**Không được `while True`.**

---

# 2. Vấn đề của `ProxyProvider` hiện tại

Ta đang có:

```python
class ProxyProvider(ABC):
    @abstractmethod
    def get_proxy(self) -> Proxy:
        raise NotImplementedError
```

Mỗi lần gọi:

```python
proxy = provider.get_proxy()
```

`ProxyPool` sẽ trả proxy tiếp theo.

Ví dụ:

```text
A → B → C → A → B → C
```

Điều này rất phù hợp với rotation.

---

# 3. ProxyPool phải có "finite iteration"

Sai:

```python
while True:
    proxy = pool.get_proxy()

    if health_checker.check(proxy):
        return proxy
```

Nếu toàn bộ proxy chết:

```text
A → B → C → A → B → C → ...
```

→ vòng lặp vô hạn.

Đây là bug rất nguy hiểm.

---

# 4. Giải pháp: giới hạn số lần thử

Nếu pool có:

```text
A
B
C
```

thì một request chỉ nên kiểm tra tối đa:

```text
3 proxy
```

Tức:

```python
for _ in range(proxy_count):
    ...
```

Sau khi kiểm tra hết:

```python
raise NoHealthyProxyError(...)
```

---

# 5. Thêm method `get_candidates()`

Thay vì để Fetcher gọi `get_proxy()` nhiều lần một cách mơ hồ, ta có thể mở rộng abstraction.

```python
class ProxyProvider(ABC):
    @abstractmethod
    def get_proxy(self) -> Proxy:
        raise NotImplementedError

    @abstractmethod
    def size(self) -> int:
        raise NotImplementedError
```

`ProxyPool`:

```python
class ProxyPool(ProxyProvider):
    def __init__(self, proxies: list[Proxy]):
        if not proxies:
            raise ValueError("Proxy pool cannot be empty")

        self._proxies = proxies
        self._index = 0

    def get_proxy(self) -> Proxy:
        total = len(self._proxies)

        for _ in range(total):
            proxy = self._proxies[self._index]

            self._index = (self._index + 1) % total

            if proxy.is_selectable:
                return proxy

        raise RuntimeError("No selectable proxy available")

    def size(self) -> int:
        return len(self._proxies)
```

---

# 6. Nhưng có cách tốt hơn

Ta không nhất thiết phải đưa `size()` vào abstraction.

Có thể để Pool cung cấp một batch candidate:

```python
class ProxyProvider(ABC):
    @abstractmethod
    def get_candidates(self) -> list[Proxy]:
        raise NotImplementedError
```

Nhưng cách này làm abstraction phụ thuộc vào việc caller muốn nhiều proxy.

Với thiết kế hiện tại, tôi khuyên **chưa thay đổi `ProxyProvider`**.

Ta giữ:

```python
get_proxy()
```

và thêm một cơ chế giới hạn retry ở Application.

---

# 7. Fetcher rotation

Ta viết:

```python
def _get_healthy_proxy(self) -> Proxy:

    attempts = 0
    max_attempts = self._proxy_provider.size()

    while attempts < max_attempts:
        proxy = self._proxy_provider.get_proxy()

        result = self._health_checker.check(proxy)

        if result.reachable:
            proxy.mark_alive()
            return proxy

        proxy.mark_dead()

        attempts += 1

    raise NoHealthyProxyError("No healthy proxy available")
```

Flow:

```text
attempt = 0
    ↓
get proxy
    ↓
health check
    ↓
alive? ── yes ──► return
    │
    no
    ↓
mark dead
    ↓
attempt++
    ↓
attempt < max?
    │
    ├── yes → proxy tiếp theo
    │
    └── no → NoHealthyProxyError
```

---

# 8. Tuy nhiên `size()` làm abstraction hơi xấu

Đây là một bài học kiến trúc quan trọng.

Fetcher thực sự cần:

> "Hãy đưa cho tôi proxy tiếp theo."

Fetcher **không nên quan tâm pool có bao nhiêu proxy**.

Ta có thể giải quyết bằng một abstraction mới:

```python
class ProxyRotator(ABC):
    @abstractmethod
    def next(self) -> Proxy:
        raise NotImplementedError
```

Nhưng vấn đề vẫn còn:

> Làm sao biết đã thử hết?

---

# 9. Thiết kế tốt hơn: Rotation Session

Ta tạo một object đại diện cho **một vòng rotation**.

```python
class ProxyRotation:
    def __init__(self, proxies: list[Proxy]):
        self._proxies = proxies
        self._index = 0

    def next(self) -> Proxy | None:

        if self._index >= len(self._proxies):
            return None

        proxy = self._proxies[self._index]
        self._index += 1

        return proxy
```

Ví dụ:

```python
rotation = ProxyRotation([proxy_a, proxy_b, proxy_c])
```

Sau đó:

```python
rotation.next()  # A
rotation.next()  # B
rotation.next()  # C
rotation.next()  # None
```

Không bao giờ infinite loop.

---

# 10. Nhưng ProxyPool hiện tại đã có rotation

Ta không muốn tạo quá nhiều abstraction.

Ở giai đoạn hiện tại, cách đơn giản và dễ hiểu nhất là:

```text
ProxyPool
   ↓
round-robin
   ↓
Fetcher giới hạn attempts
```

Đây là lựa chọn tốt cho phiên bản v1.

---

# 11. Refactor Fetcher

Ta thêm:

```python
class Fetcher:
    def __init__(
        self,
        proxy_provider: ProxyProvider,
        user_agent_provider: UserAgentProvider,
        health_checker: ProxyHealthChecker,
        http_client: HttpClient,
        max_proxy_attempts: int = 3,
    ):
        self._proxy_provider = proxy_provider
        self._user_agent_provider = user_agent_provider
        self._health_checker = health_checker
        self._http_client = http_client
        self._max_proxy_attempts = max_proxy_attempts
```

Nhưng có một vấn đề:

```text
max_proxy_attempts = 3
```

hard-code theo số lượng proxy không tốt.

---

# 12. ProxyProvider nên cung cấp rotation boundary

Ta có thể tạo method:

```python
class ProxyProvider(ABC):
    @abstractmethod
    def get_proxy(self) -> Proxy:
        raise NotImplementedError

    @abstractmethod
    def get_rotation_limit(self) -> int:
        raise NotImplementedError
```

`ProxyPool`:

```python
def get_rotation_limit(self) -> int:
    return len(self._proxies)
```

Fetcher:

```python
max_attempts = self._proxy_provider.get_rotation_limit()
```

Bây giờ Fetcher không biết cấu trúc nội bộ của pool.

---

# 13. `_get_healthy_proxy()`

Hoàn chỉnh:

```python
def _get_healthy_proxy(self) -> Proxy:

    max_attempts = self._proxy_provider.get_rotation_limit()

    for _ in range(max_attempts):
        proxy = self._proxy_provider.get_proxy()

        result = self._health_checker.check(proxy)

        if result.reachable:
            proxy.mark_alive()
            return proxy

        proxy.mark_dead()

    raise NoHealthyProxyError("No healthy proxy available")
```

Đây là rotation phiên bản đầu tiên.

---

# 14. `fetch()` trở nên sạch hơn

```python
def fetch(
    self,
    request: FetchRequest,
) -> FetchResult:

    proxy = self._get_healthy_proxy()

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

Ta đã có:

```text
fetch()
 ├── _get_healthy_proxy()
 ├── get_user_agent()
 ├── http_client.get()
 └── FetchResult
```

Khá dễ đọc.

---

# 15. Test rotation

Đây là test quan trọng.

Giả sử:

```text
A DEAD
B DEAD
C ALIVE
```

Ta cần kiểm tra Fetcher chọn C.

Fake HealthChecker có thể trả kết quả theo proxy:

```python
class FakeProxyHealthChecker(ProxyHealthChecker):
    def __init__(
        self,
        results: dict[str, ProxyHealthResult],
    ):
        self.results = results
        self.checked = []

    def check(
        self,
        proxy: Proxy,
    ) -> ProxyHealthResult:

        self.checked.append(proxy.url.value)

        return self.results[proxy.url.value]
```

---

# 16. Test

```python
proxy_a = Proxy(url=ProxyUrl("http://proxy-a:8080"))

proxy_b = Proxy(url=ProxyUrl("http://proxy-b:8080"))

proxy_c = Proxy(url=ProxyUrl("http://proxy-c:8080"))
```

Health:

```python
checker = FakeProxyHealthChecker(
    {
        "http://proxy-a:8080": ProxyHealthResult(reachable=False),
        "http://proxy-b:8080": ProxyHealthResult(reachable=False),
        "http://proxy-c:8080": ProxyHealthResult(
            reachable=True,
            status_code=200,
        ),
    }
)
```

Sau fetch:

```python
result = fetcher.fetch(FetchRequest(url="https://example.com"))
```

Kiểm tra:

```python
assert checker.checked == [
    "http://proxy-a:8080",
    "http://proxy-b:8080",
    "http://proxy-c:8080",
]
```

Proxy C phải được chọn.

---

# 17. Test tất cả proxy chết

```python
checker = FakeProxyHealthChecker(
    {
        "http://proxy-a:8080": ProxyHealthResult(reachable=False),
        "http://proxy-b:8080": ProxyHealthResult(reachable=False),
        "http://proxy-c:8080": ProxyHealthResult(reachable=False),
    }
)
```

Ta mong muốn:

```python
with pytest.raises(NoHealthyProxyError):
    fetcher.fetch(FetchRequest(url="https://example.com"))
```

Và quan trọng:

```python
assert checker.checked == [
    "http://proxy-a:8080",
    "http://proxy-b:8080",
    "http://proxy-c:8080",
]
```

**Chỉ thử đúng một vòng.**

---

# 18. Test không bị infinite loop

Đây là một test tư duy rất quan trọng.

Nếu có 3 proxy:

```text
A
B
C
```

thì health checker không được gọi:

```text
A B C A B C A B C ...
```

Ta assert:

```python
assert len(checker.checked) == 3
```

Nếu implementation vô tình dùng:

```python
while True:
```

test sẽ expose bug.

---

# 19. Một vấn đề khác: Proxy đã DEAD

`ProxyPool` hiện tại bỏ qua:

```python
if proxy.is_selectable:
```

Nếu `mark_dead()` làm:

```text
DEAD → không selectable
```

thì sau lần đầu:

```text
A DEAD
```

Pool sẽ bỏ A.

Điều này tốt cho runtime.

Ví dụ:

```text
Request 1

A → DEAD
B → DEAD
C → ALIVE
```

Request tiếp:

```text
B → ...
C → ...
```

A không còn được chọn.

---

# 20. Nhưng có một vấn đề production

Nếu A chết tạm thời:

```text
10:00 A DEAD
```

thì nó có thể bị loại **vĩnh viễn**.

Đây không phải thiết kế production hoàn chỉnh.

Sau này chúng ta sẽ thêm:

```text
DEAD
  ↓
cooldown
  ↓
UNKNOWN
  ↓
health check
```

hoặc:

```text
DEAD
  ↓
retry_after
  ↓
eligible again
```

Đó chính là lý do Buổi 17 về **Proxy State** sẽ quan trọng.

---

# 21. Rotation không đồng nghĩa Retry

Hai khái niệm này cần phân biệt ngay từ bây giờ.

### Proxy Rotation

```text
A
↓
B
↓
C
```

Là:

> đổi proxy.

### Retry

```text
A + request
↓
failure
↓
A + request
```

Là:

> thử lại request.

Sau này:

```text
Proxy Rotation
+
Retry
```

sẽ kết hợp thành:

```text
A + request
   ↓
failure
   ↓
B + request
   ↓
failure
   ↓
C + request
   ↓
success
```

Nhưng **Buổi 8 chưa làm Retry**.

---

# 22. Đừng làm thế này

Một thiết kế dễ mắc lỗi:

```python
for _ in range(10):
    proxy = pool.get_proxy()

    try:
        response = http_client.get(...)
    except Exception:
        continue
```

Nó trộn:

```text
Proxy selection
Health check
HTTP request
Retry
Exception handling
```

vào cùng một vòng lặp.

Sau này Fetcher sẽ trở thành:

```text
God Object
```

---

# 23. Thiết kế hiện tại

Ta giữ trách nhiệm:

```text
ProxyPool
    ↓
chọn proxy

HealthChecker
    ↓
kiểm tra proxy

Fetcher
    ↓
orchestrate

HttpClient
    ↓
HTTP transport
```

```text
                  Fetcher
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
     ProxyPool     Health     UA Pool
          │        Checker       │
          │          │           │
          └──────┬───┘           │
                 ▼               │
              Proxy              │
                 │               │
                 └───────┬───────┘
                         ▼
                    HttpClient
                         │
                         ▼
                       httpx
```

---

# 24. SOLID

Buổi này đặc biệt liên quan tới **SRP + OCP + DIP**.

### ProxyPool

Chỉ:

> chọn proxy.

### HealthChecker

Chỉ:

> kiểm tra proxy.

### Fetcher

Chỉ:

> orchestration.

### HttpClient

Chỉ:

> HTTP transport.

Không component nào cần biết toàn bộ hệ thống.

---

# 25. Kết quả sau Buổi 8

Fetcher hiện đã có khả năng:

```text
                 Fetch
                   │
                   ▼
              ProxyPool
                   │
              ┌────┴────┐
              ▼         ▼
           Proxy A   Proxy B ...
              │
              ▼
        Health Checker
              │
        ┌─────┴─────┐
        │           │
       DEAD       ALIVE
        │           │
        ▼           ▼
   next proxy     HTTP GET
        │
        ▼
      retry
```

Và chúng ta đã đặt được một **invariant rất quan trọng**:

> **Một request chỉ được thử tối đa một vòng qua ProxyPool; nếu không tìm được proxy khỏe thì throw `NoHealthyProxyError`.**

---

## Roadmap đến đây

```text
01 Architecture                 ✅
02 Proxy Domain Model            ✅
03 ProxyPool                     ✅
04 User-Agent Pool               ✅
05 HttpClient + httpx             ✅
06 Proxy Health Checker           ✅
07 Fetcher cơ bản                 ✅
08 Proxy Rotation                 ✅
09 User-Agent Rotation            ⬅️ tiếp theo
10 Retry
11 Error Handling
12 Fetch Policy
```

**Buổi 9 — User-Agent Rotation** sẽ hoàn thiện phần request fingerprint cơ bản:

```text
Proxy A + UA1
Proxy B + UA2
Proxy C + UA3
Proxy A + UA4
...
```

và chúng ta sẽ xem xét một vấn đề quan trọng: **Proxy rotation và UA rotation phải độc lập hay nên tạo thành một `RequestContext` cố định cho từng attempt?**
