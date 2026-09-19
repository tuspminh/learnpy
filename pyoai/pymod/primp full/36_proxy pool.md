# Buổi 36 — Proxy Pool

Ở Buổi 14 chúng ta mới có **một proxy**:

```text
ProxyConfig
    ↓
primp.AsyncClient
    ↓
HTTP
```

Đến Buổi 35, crawler đã có:

```text
AsyncClient
    ↓
Concurrent Requests
    ↓
Semaphore
    ↓
Timeout
    ↓
Retry
```

Bây giờ ta đưa nhiều proxy vào:

```text
                    Proxy Pool
                 ┌─────┼─────┐
                 ↓     ↓     ↓
              Proxy A B     C
                 │     │     │
                 └─────┼─────┘
                       ↓
                 HTTP Fetcher
```

Mục tiêu hôm nay:

```text
ProxyConfig
ProxyPool
Proxy selection
Round-robin
Proxy failure
Proxy health
Async Fetcher + Proxy Pool
```

> Lưu ý: proxy rotation nên được dùng để quản lý tải, độ sẵn sàng và phân bổ traffic hợp lệ; không nên xem nó như cơ chế bảo đảm vượt qua anti-bot hay giới hạn truy cập.

---

# 1. Vì sao cần Proxy Pool?

Một crawler có thể chỉ dùng:

```text
Proxy A
```

nhưng proxy có thể:

```text
timeout
connection failed
bị ngắt
hết quota
không còn hoạt động
```

Nếu chỉ có một proxy:

```text
Crawler
   ↓
Proxy A
   ↓
FAILED
   ↓
crawler bị ảnh hưởng
```

Với pool:

```text
Crawler
   ↓
Proxy Pool
   │
   ├── Proxy A
   ├── Proxy B
   ├── Proxy C
   └── Proxy D
```

Khi một proxy gặp lỗi, pool có thể chọn proxy khác theo policy.

---

# 2. Proxy Pool không phải Proxy Config

Ta đã có:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ProxyConfig:
    url: str
    username: str | None = None
    password: str | None = None
```

Đây là **một proxy**.

Còn:

```text
ProxyPool
```

là nơi quản lý:

```text
Proxy A
Proxy B
Proxy C
Proxy D
```

Do đó:

```text
ProxyConfig
    =
một proxy

ProxyPool
    =
nhiều proxy + selection policy
```

---

# 3. Thiết kế đơn giản nhất

Bắt đầu:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ProxyConfig:
    url: str
```

Pool:

```python
class ProxyPool:

    def __init__(
        self,
        proxies: list[ProxyConfig],
    ):
        self.proxies = proxies
```

Sử dụng:

```python
pool = ProxyPool([
    ProxyConfig("http://proxy-a:8080"),
    ProxyConfig("http://proxy-b:8080"),
    ProxyConfig("http://proxy-c:8080"),
])
```

---

# 4. Proxy selection

Pool phải trả lời câu hỏi:

> Request tiếp theo dùng proxy nào?

Đây là **Proxy Selection Strategy**.

Strategy đơn giản nhất:

```text
Round Robin
```

Ví dụ:

```text
Request 1 → A
Request 2 → B
Request 3 → C
Request 4 → A
Request 5 → B
Request 6 → C
```

---

# 5. Round Robin

Code:

```python
class ProxyPool:

    def __init__(
        self,
        proxies: list[ProxyConfig],
    ):
        if not proxies:
            raise ValueError(
                "Proxy pool cannot be empty"
            )

        self.proxies = proxies
        self.index = 0

    def next(self) -> ProxyConfig:

        proxy = self.proxies[self.index]

        self.index = (
            self.index + 1
        ) % len(self.proxies)

        return proxy
```

Test:

```python
proxies = [
    ProxyConfig("proxy-a"),
    ProxyConfig("proxy-b"),
    ProxyConfig("proxy-c"),
]

pool = ProxyPool(proxies)

for _ in range(8):
    print(pool.next().url)
```

Kết quả:

```text
proxy-a
proxy-b
proxy-c
proxy-a
proxy-b
proxy-c
proxy-a
proxy-b
```

---

# 6. Vì sao Round Robin hữu ích?

Nó rất đơn giản:

```text
Request
   ↓
A
   ↓
Request
   ↓
B
   ↓
Request
   ↓
C
```

Không cần biết quá nhiều về proxy.

Nhưng có một nhược điểm:

```text
Proxy A → khỏe
Proxy B → chết
Proxy C → khỏe
```

Round Robin vẫn chọn:

```text
A → B → C → A → B → C
```

Tức là:

> Pool chưa biết proxy B đang chết.

Do đó cần **health state**.

---

# 7. Proxy State

Ta có thể mô hình hóa:

```text
Proxy A → healthy
Proxy B → unhealthy
Proxy C → healthy
```

Một class:

```python
from dataclasses import dataclass


@dataclass
class ProxyState:
    proxy: ProxyConfig
    failures: int = 0
    healthy: bool = True
```

Pool:

```python
class ProxyPool:

    def __init__(
        self,
        proxies: list[ProxyConfig],
    ):
        self.states = [
            ProxyState(proxy)
            for proxy in proxies
        ]
```

---

# 8. `mark_failure()`

Khi request qua proxy thất bại:

```python
def mark_failure(
    self,
    proxy: ProxyConfig,
):
    ...
```

Ta cần tìm state tương ứng:

```python
class ProxyPool:

    def __init__(
        self,
        proxies: list[ProxyConfig],
    ):
        self.states = [
            ProxyState(proxy)
            for proxy in proxies
        ]

    def mark_failure(
        self,
        proxy: ProxyConfig,
    ):
        for state in self.states:

            if state.proxy == proxy:

                state.failures += 1

                if state.failures >= 3:
                    state.healthy = False

                return
```

Ví dụ:

```text
Proxy B
 ↓
failure #1
 ↓
failure #2
 ↓
failure #3
 ↓
unhealthy
```

---

# 9. `mark_success()`

Khi request thành công:

```python
def mark_success(
    self,
    proxy: ProxyConfig,
):
    ...
```

Có thể reset:

```python
def mark_success(
    self,
    proxy: ProxyConfig,
):
    for state in self.states:

        if state.proxy == proxy:

            state.failures = 0
            state.healthy = True

            return
```

Flow:

```text
Proxy B
 ↓
failure
 ↓
failure
 ↓
success
 ↓
failure count = 0
```

---

# 10. Chọn proxy khỏe

```python
def next(self) -> ProxyConfig:

    healthy = [
        state.proxy
        for state in self.states
        if state.healthy
    ]

    if not healthy:
        raise RuntimeError(
            "No healthy proxies"
        )

    proxy = healthy[
        self.index % len(healthy)
    ]

    self.index += 1

    return proxy
```

Bây giờ:

```text
A healthy
B unhealthy
C healthy
```

Pool chỉ chọn:

```text
A → C → A → C
```

---

# 11. Nhưng có một vấn đề async

Ở crawler của chúng ta:

```text
Task 1
Task 2
Task 3
Task 4
...
```

cùng truy cập:

```python
pool.next()
```

Nếu pool có mutable state:

```python
self.index
```

thì cần cẩn thận với concurrent access.

Trong Python async, code không tự động chạy song song trên nhiều thread chỉ vì dùng coroutine, nhưng việc thiết kế stateful async component vẫn cần rõ ràng.

Một cách đơn giản là dùng `asyncio.Lock`.

---

# 12. Async Proxy Pool

```python
import asyncio


class ProxyPool:

    def __init__(
        self,
        proxies: list[ProxyConfig],
    ):
        if not proxies:
            raise ValueError(
                "Proxy pool cannot be empty"
            )

        self.states = [
            ProxyState(proxy)
            for proxy in proxies
        ]

        self.index = 0
        self.lock = asyncio.Lock()

    async def next(self) -> ProxyConfig:

        async with self.lock:

            healthy = [
                state.proxy
                for state in self.states
                if state.healthy
            ]

            if not healthy:
                raise RuntimeError(
                    "No healthy proxies"
                )

            proxy = healthy[
                self.index % len(healthy)
            ]

            self.index += 1

            return proxy
```

---

# 13. Tại sao Lock chỉ bao quanh selection?

Không nên:

```python
async with self.lock:

    response = await client.get(...)
```

vì HTTP request có thể mất vài giây.

Nếu làm vậy:

```text
Task A
 ↓
lock
 ↓
HTTP 5 seconds
 ↓
release

Task B
 ↓
wait 5 seconds
```

Pool trở thành bottleneck.

Ta chỉ lock phần:

```text
state mutation
+
proxy selection
```

chứ không lock network operation.

---

# 14. Proxy + `primp.AsyncClient`

Đây là chỗ có một vấn đề thiết kế quan trọng.

Một proxy có thể là **client-level configuration**. Vì vậy ta không nên tùy tiện giả định rằng:

```python
client.get(
    url,
    proxy=proxy.url,
)
```

là API Python `primp` hiện tại nếu chưa xác minh phiên bản cụ thể.

Thay vào đó, với `primp`, cần cấu hình proxy theo API phiên bản đang dùng và giữ proxy/client relationship rõ ràng.

Về architecture:

```text
ProxyPool
    ↓
ProxyConfig
    ↓
Primp Client configuration
    ↓
HTTP
```

Không nên nhét proxy thành một phần của Domain.

---

# 15. Một mô hình client-per-proxy

Nếu proxy là client-level configuration, ta có thể xây:

```text
Proxy A → AsyncClient A
Proxy B → AsyncClient B
Proxy C → AsyncClient C
```

và pool quản lý cả cặp:

```text
ProxyClient
```

Ví dụ concept:

```python
from dataclasses import dataclass


@dataclass
class ProxyClient:
    proxy: ProxyConfig
    client: object
```

Pool:

```text
ProxyPool
   │
   ├── ProxyClient A
   ├── ProxyClient B
   └── ProxyClient C
```

Điều này có ưu điểm:

```text
Proxy identity
+
Client/session state
```

được giữ ổn định.

---

# 16. Tại sao không đổi proxy ngẫu nhiên mỗi request?

Ví dụ:

```text
Chapter 1 → Proxy A
Chapter 2 → Proxy C
Chapter 3 → Proxy B
Chapter 4 → Proxy A
```

Không phải lúc nào cũng tốt.

Client/session có thể chứa:

```text
Cookies
Connection state
Browser profile
Proxy identity
```

Nếu thay đổi lung tung:

```text
same session
+
different IP/proxy
```

có thể tạo ra state không nhất quán.

Vì vậy:

> **Proxy rotation phải được thiết kế cùng Session/Client lifecycle.**

Đây là lý do Buổi 16 và Buổi 20 về Client Lifecycle rất quan trọng.

---

# 17. Proxy Pool không nhất thiết random

Có nhiều strategy:

```text
Round Robin
Random
Least Failures
Least Recently Used
Weighted
Healthy-only
```

Hôm nay ta chỉ triển khai:

```text
Round Robin + Health
```

Đừng xây tất cả ngay.

---

# 18. Proxy Health

Một proxy có thể:

```text
healthy
degraded
unhealthy
```

Nhưng ở mức đầu tiên chỉ cần:

```text
healthy = True / False
```

Ví dụ:

```python
@dataclass
class ProxyState:
    proxy: ProxyConfig
    failures: int = 0
    healthy: bool = True
```

---

# 19. Failure Threshold

Ví dụ:

```python
failure_threshold = 3
```

Flow:

```text
Proxy A

failure 1
   ↓
still healthy

failure 2
   ↓
still healthy

failure 3
   ↓
unhealthy
```

Không nên:

```text
1 failure → blacklist forever
```

vì network failure có thể chỉ là tạm thời.

---

# 20. Recovery

Một proxy unhealthy không nhất thiết chết vĩnh viễn.

Có thể:

```text
unhealthy
   ↓
cooldown
   ↓
health check
   ↓
healthy
```

Ví dụ:

```text
Proxy B
  ↓
3 failures
  ↓
unhealthy
  ↓
60 seconds
  ↓
health check
  ↓
success
  ↓
healthy
```

Đây là một dạng **Circuit Breaker-like behavior**.

Chúng ta chưa cần xây đầy đủ hôm nay.

---

# 21. Proxy Health Check

Về mặt kiến trúc:

```text
ProxyPool
    ↓
HealthChecker
    ↓
test request
    ↓
success/failure
```

Không nên để:

```text
ProxyPool
```

tự chứa toàn bộ HTTP logic.

Sau này có thể:

```text
ProxyPool
ProxyHealthChecker
ProxySelectionStrategy
```

nhưng hiện tại chưa cần tạo quá nhiều abstraction.

---

# 22. Kết hợp Retry + Proxy Pool

Đây là phần rất quan trọng.

Giả sử:

```text
Proxy A
   ↓
GET
   ↓
timeout
```

Có hai policy khả dĩ:

### Strategy 1

Retry cùng proxy:

```text
A → fail
A → retry
A → retry
```

### Strategy 2

Đổi proxy:

```text
A → fail
B → retry
C → retry
```

Hai chiến lược có ý nghĩa khác nhau.

---

# 23. Không nên đổi proxy cho mọi lỗi

Ví dụ:

```text
404
```

thì:

```text
Proxy A
 ↓
404
```

đổi sang:

```text
Proxy B
 ↓
404
```

không giải quyết được vấn đề.

Có thể resource thực sự không tồn tại.

Trong khi:

```text
timeout
connection failure
proxy connection failure
```

có thể liên quan đến proxy/network.

Do đó:

```text
Error Classification
       ↓
Proxy failure?
       ↓
rotate?
```

Đây là lý do roadmap sau này có:

```text
48. Error Classification
```

---

# 24. Flow tốt hơn

```text
Request
   ↓
Proxy A
   ↓
Failure
   ↓
Classify Error
   │
   ├── 404 → stop
   │
   ├── server 500 → Retry Policy
   │
   └── proxy/network failure
             ↓
          mark A failed
             ↓
          choose B
             ↓
           retry
```

Đây là architecture mà chúng ta sẽ hoàn thiện dần.

---

# 25. Kết hợp Semaphore

Hiện tại ta có:

```text
Semaphore(10)
```

và:

```text
Proxy Pool
```

Flow:

```text
                    1000 URLs
                        ↓
                     gather
                        ↓
                 Semaphore(10)
                        ↓
              ┌─────────┼─────────┐
              ↓         ↓         ↓
           Task A    Task B    Task C
              ↓         ↓         ↓
           Proxy A   Proxy B   Proxy C
              ↓         ↓         ↓
             HTTP      HTTP      HTTP
```

Mỗi task lấy một proxy.

---

# 26. Ví dụ ProxyPool độc lập

Trước khi tích hợp `primp`, hãy test pool.

```python
import asyncio
from dataclasses import dataclass


@dataclass(frozen=True)
class ProxyConfig:
    url: str


@dataclass
class ProxyState:
    proxy: ProxyConfig
    failures: int = 0
    healthy: bool = True


class ProxyPool:

    def __init__(
        self,
        proxies: list[ProxyConfig],
        failure_threshold: int = 3,
    ):
        if not proxies:
            raise ValueError(
                "Proxy pool cannot be empty"
            )

        self.states = [
            ProxyState(proxy)
            for proxy in proxies
        ]

        self.failure_threshold = (
            failure_threshold
        )

        self.index = 0
        self.lock = asyncio.Lock()

    async def next(self) -> ProxyConfig:

        async with self.lock:

            healthy = [
                state.proxy
                for state in self.states
                if state.healthy
            ]

            if not healthy:
                raise RuntimeError(
                    "No healthy proxies"
                )

            proxy = healthy[
                self.index % len(healthy)
            ]

            self.index += 1

            return proxy

    async def mark_failure(
        self,
        proxy: ProxyConfig,
    ):

        async with self.lock:

            for state in self.states:

                if state.proxy == proxy:

                    state.failures += 1

                    if (
                        state.failures
                        >= self.failure_threshold
                    ):
                        state.healthy = False

                    return

    async def mark_success(
        self,
        proxy: ProxyConfig,
    ):

        async with self.lock:

            for state in self.states:

                if state.proxy == proxy:

                    state.failures = 0
                    state.healthy = True

                    return
```

---

# 27. Test Pool

```python
async def main():

    pool = ProxyPool(
        [
            ProxyConfig("proxy-A"),
            ProxyConfig("proxy-B"),
            ProxyConfig("proxy-C"),
        ]
    )

    for _ in range(6):

        proxy = await pool.next()

        print(
            "Selected:",
            proxy.url,
        )


if __name__ == "__main__":
    asyncio.run(main())
```

Kết quả:

```text
Selected: proxy-A
Selected: proxy-B
Selected: proxy-C
Selected: proxy-A
Selected: proxy-B
Selected: proxy-C
```

---

# 28. Test unhealthy proxy

```python
async def main():

    proxy_a = ProxyConfig("proxy-A")
    proxy_b = ProxyConfig("proxy-B")
    proxy_c = ProxyConfig("proxy-C")

    pool = ProxyPool(
        [
            proxy_a,
            proxy_b,
            proxy_c,
        ],
        failure_threshold=2,
    )

    await pool.mark_failure(proxy_b)
    await pool.mark_failure(proxy_b)

    for _ in range(6):

        proxy = await pool.next()

        print(proxy.url)


if __name__ == "__main__":
    asyncio.run(main())
```

Ta sẽ chỉ còn:

```text
proxy-A
proxy-C
proxy-A
proxy-C
...
```

Proxy B đã bị loại khỏi healthy pool.

---

# 29. Tích hợp vào Fetcher

Về mặt concept:

```python
class AsyncFetcher:

    def __init__(
        self,
        client,
        proxy_pool,
        semaphore,
    ):
        self.client = client
        self.proxy_pool = proxy_pool
        self.semaphore = semaphore
```

Request:

```python
async def get(self, url):

    async with self.semaphore:

        proxy = await self.proxy_pool.next()

        try:

            response = await self.client.get(
                url,
                ...
            )

            await self.proxy_pool.mark_success(
                proxy
            )

            return response

        except Exception:

            await self.proxy_pool.mark_failure(
                proxy
            )

            raise
```

**Phần `...` về cách truyền proxy cụ thể vào `primp` cần bám đúng API version bạn đang cài**, thay vì tự đoán keyword. Đây là chỗ nên kiểm tra tài liệu/source của `primp` trước khi biến concept thành production adapter.

---

# 30. Một vấn đề khác: proxy và Browser Profile

Chúng ta đã học:

```text
Browser Profile
    ↓
Chrome + Windows
    ↓
TLS
HTTP/2
Headers
```

và hôm nay:

```text
Proxy
    ↓
IP/network path
```

Do đó một request thực tế có identity:

```text
Browser Profile
+
OS
+
Proxy
+
Cookies/session
+
Request behavior
```

Không nên random từng thành phần độc lập.

Ví dụ không nên thiết kế:

```text
Request 1
Chrome + Windows + Proxy A

Request 2
Firefox + Linux + Proxy B

Request 3
Chrome + macOS + Proxy C
```

chỉ vì muốn "random".

---

# 31. Tốt hơn: Proxy + Browser Profile như một Persona

Về sau có thể có:

```text
BrowserPersona
    │
    ├── BrowserProfile
    └── Proxy
```

Ví dụ:

```text
Persona A
 ├── Chrome 146
 ├── Windows
 └── Proxy A

Persona B
 ├── Firefox 146
 ├── Windows
 └── Proxy B
```

Nhưng **chưa xây class này ở Buổi 36**.

Chúng ta sẽ học Browser Profile Pool ở Buổi 37 trước.

---

# 32. Proxy Pool và DDD/SOLID

Đừng để:

```text
Novel
Chapter
CrawlTask
```

biết:

```text
ProxyPool
primp
AsyncClient
```

Đúng:

```text
Application
    ↓
AsyncFetcher
    ↓
ProxyPool
    ↓
Primp Adapter
```

Domain:

```text
Novel
Chapter
CrawlTask
```

hoàn toàn độc lập.

---

# 33. Cấu trúc thư mục đề xuất

Đến đây project có thể bắt đầu hình thành:

```text
src/
└── crawler/
    ├── application/
    │   └── ...
    │
    ├── domain/
    │   ├── novel.py
    │   └── chapter.py
    │
    └── infrastructure/
        └── http/
            ├── browser_profile.py
            ├── proxy.py
            ├── proxy_pool.py
            ├── async_client.py
            └── fetcher.py
```

Tạm thời chưa cần:

```text
proxy_strategy.py
proxy_health_service.py
proxy_manager.py
proxy_factory.py
```

cho đến khi requirements thực sự cần.

---

# 34. Luồng hoàn chỉnh hiện tại

```text
                        URLs
                         │
                         ↓
                  asyncio.gather()
                         │
                         ↓
                  Semaphore(10)
                         │
             ┌───────────┼───────────┐
             ↓           ↓           ↓
           Task 1      Task 2      Task 3
             │           │           │
             ↓           ↓           ↓
         ProxyPool   ProxyPool   ProxyPool
             │           │           │
             ↓           ↓           ↓
           Proxy A    Proxy B    Proxy C
             │           │           │
             └───────────┼───────────┘
                         ↓
                  Browser Profile
                         ↓
                  primp.AsyncClient
                         ↓
                       HTTP
                         ↓
                    Timeout
                         ↓
                   Retry Policy
```

Đây chính là skeleton của Async Novel Fetcher.

---

# 35. Nhưng Proxy Pool hiện tại còn thiếu

Ta mới có:

```text
✓ danh sách proxy
✓ round robin
✓ healthy/unhealthy
✓ failure threshold
```

Chưa có:

```text
✗ proxy health check
✗ cooldown
✗ proxy recovery
✗ weighted selection
✗ latency tracking
✗ success rate
✗ integration hoàn chỉnh với primp
```

Không cần làm tất cả ngay.

Roadmap sẽ xử lý từng phần.

---

# 36. Bài tập thực hành

### Bài 1 — Round Robin

Tạo 3 proxy:

```text
A
B
C
```

gọi `next()` 10 lần.

Kết quả phải tuần hoàn:

```text
A B C A B C A B C A
```

---

### Bài 2 — Failure Threshold

Đặt:

```python
failure_threshold=3
```

Cho Proxy B:

```text
failure
failure
failure
```

Sau đó kiểm tra:

```text
Proxy B → unhealthy
```

---

### Bài 3 — Recovery

Sau:

```text
Proxy B → unhealthy
```

gọi:

```python
await pool.mark_success(proxy_b)
```

và kiểm tra:

```text
Proxy B → healthy
```

---

### Bài 4 — Concurrent Selection

Tạo:

```text
100 tasks
+
ProxyPool
```

Mỗi task:

```python
proxy = await pool.next()
```

Kiểm tra rằng selection không làm hỏng state `index`.

---

# 37. Bài tập chính — Async Proxy Fetcher

Xây:

```text
AsyncFetcher
    │
    ├── Semaphore
    ├── ProxyPool
    └── AsyncClient
```

Flow:

```text
get(url)
   ↓
Semaphore
   ↓
ProxyPool.next()
   ↓
request
   ↓
success → mark_success()
   ↓
failure → mark_failure()
```

Chưa cần:

```text
Retry
Rate Limit
Browser Profile Pool
```

vì những phần đó sẽ được ghép dần.

---

# 38. Một nguyên tắc rất quan trọng

Đừng nghĩ:

```text
Proxy Pool
=
đổi IP liên tục
```

Mô hình chính xác hơn:

```text
Proxy Pool
=
quản lý một tập proxy
+
chọn proxy
+
theo dõi trạng thái
+
loại proxy lỗi
+
có khả năng phục hồi
```

Đây là một **resource management component**, không đơn thuần là randomizer.

---

# 39. Tổng kết Buổi 36

Đến đây:

```text
31. AsyncClient             ✅
32. async GET               ✅
33. Concurrent Requests     ✅
34. Semaphore               ✅
35. Timeout + Retry         ✅
36. Proxy Pool              ✅
37. Browser Profile Pool    ← tiếp theo
38. Rate Limiting
39. Fetcher Architecture
40. Async Novel Fetcher
```

Kiến trúc hiện tại:

```text
                    AsyncNovelFetcher
                           │
             ┌─────────────┼─────────────┐
             ↓             ↓             ↓
        Semaphore       ProxyPool     RetryPolicy
             │             │             │
             └─────────────┼─────────────┘
                           ↓
                    BrowserClient
                           ↓
                  primp.AsyncClient
                           ↓
                          HTTP
```

Và điều quan trọng nhất hôm nay:

```text
ProxyConfig
    =
một proxy

ProxyPool
    =
nhiều proxy
+
selection
+
health state

Semaphore
    =
giới hạn concurrency

RetryPolicy
    =
quyết định retry

BrowserProfile
    =
browser/network identity
```

Bước tiếp theo **Buổi 37 — User-Agent / Browser Profile Pool** sẽ nối trực tiếp với Buổi 23–30: thay vì chỉ có một `chrome_146 + windows`, chúng ta sẽ quản lý **nhiều browser profiles**, chọn profile ổn định cho từng client/session và tránh việc random browser/OS một cách thiếu nhất quán.
