# Buổi 37 — User-Agent / Browser Profile Pool

Ở Buổi 36 chúng ta đã xây:

```text
ProxyPool
    ↓
Proxy A
Proxy B
Proxy C
```

Hôm nay xây thêm **Browser Profile Pool**:

```text
BrowserProfilePool
    │
    ├── Chrome 146 + Windows
    ├── Chrome 147 + Windows
    ├── Firefox 146 + Windows
    └── Edge 146 + Windows
```

`primp 2.0.1` hiện hỗ trợ nhiều profile Chrome, Firefox, Safari, Edge, Opera và các OS profile như `windows`, `macos`, `linux`, `android`, `ios`, `random`. ([PyPI][1])

> Mục tiêu của Pool ở đây là quản lý các profile một cách có kiểm soát. Không nên hiểu việc xoay profile là bảo đảm tránh được anti-bot.

---

# 1. Nhắc lại BrowserProfile

Ở Buổi 30 chúng ta có:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserProfile:
    impersonate: str
    os: str | None = None
```

Ví dụ:

```python
chrome_windows = BrowserProfile(
    impersonate="chrome_146",
    os="windows",
)
```

Khi truyền vào:

```python
import primp


client = primp.AsyncClient(
    impersonate="chrome_146",
    impersonate_os="windows",
)
```

`primp` sẽ sử dụng profile tương ứng thay vì chỉ đơn giản thay đổi User-Agent. Official package mô tả browser impersonation bao gồm browser profiles cùng TLS/HTTP2 fingerprinting. ([PyPI][1])

---

# 2. Tại sao cần Browser Profile Pool?

Nếu chỉ có một profile:

```text
Crawler
   ↓
Chrome 146 + Windows
   ↓
mọi request
```

thì toàn bộ crawler dùng cùng một browser identity.

Khi cần quản lý nhiều client/session, ta có thể có:

```text
Browser Profile Pool
        │
        ├── Profile A
        ├── Profile B
        ├── Profile C
        └── Profile D
```

Ví dụ:

```text
A = Chrome 146 + Windows
B = Chrome 147 + Windows
C = Firefox 146 + Windows
D = Edge 146 + Windows
```

---

# 3. Nhưng đừng hiểu Pool là random mỗi request

Đây là nguyên tắc quan trọng nhất của bài.

Không nên:

```text
Request 1 → Chrome
Request 2 → Firefox
Request 3 → Safari
Request 4 → Edge
Request 5 → Chrome
```

một cách tùy tiện.

Bởi vì một client/session có thể gắn với:

```text
Browser Profile
+
Cookies
+
Connection state
+
Proxy
```

Do đó tốt hơn là:

```text
Profile
    ↓
Client/Session
    ↓
nhiều requests
```

thay vì:

```text
request
 ↓
random profile
 ↓
request
 ↓
random profile
```

---

# 4. Browser Profile Pool khác Proxy Pool

Hai pool có trách nhiệm khác nhau.

```text
ProxyPool
    ↓
Network path
    ↓
Proxy A/B/C
```

Trong khi:

```text
BrowserProfilePool
    ↓
Browser identity
    ↓
Chrome/Firefox/Edge...
```

Không gộp:

```python
class EverythingPool:
    proxy
    browser
    retry
    timeout
    cookies
```

Đó sẽ trở thành một God Object.

---

# 5. Profile Catalog

Trước tiên tạo catalog:

```python
PROFILES = [
    BrowserProfile(
        impersonate="chrome_146",
        os="windows",
    ),
    BrowserProfile(
        impersonate="chrome_147",
        os="windows",
    ),
    BrowserProfile(
        impersonate="firefox_146",
        os="windows",
    ),
    BrowserProfile(
        impersonate="edge_146",
        os="windows",
    ),
]
```

Các profile này tương ứng với các profile hiện được PyPI liệt kê cho `primp 2.0.1`. ([PyPI][1])

---

# 6. Round Robin Profile Pool

Giống Buổi 36:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserProfile:
    impersonate: str
    os: str | None = None


class BrowserProfilePool:

    def __init__(
        self,
        profiles: list[BrowserProfile],
    ):
        if not profiles:
            raise ValueError(
                "Browser profile pool cannot be empty"
            )

        self.profiles = profiles
        self.index = 0

    def next(self) -> BrowserProfile:

        profile = self.profiles[self.index]

        self.index = (
            self.index + 1
        ) % len(self.profiles)

        return profile
```

Test:

```python
pool = BrowserProfilePool([
    BrowserProfile("chrome_146", "windows"),
    BrowserProfile("chrome_147", "windows"),
    BrowserProfile("firefox_146", "windows"),
])


for _ in range(7):
    profile = pool.next()

    print(
        profile.impersonate,
        profile.os,
    )
```

Kết quả:

```text
chrome_146 windows
chrome_147 windows
firefox_146 windows
chrome_146 windows
chrome_147 windows
firefox_146 windows
chrome_146 windows
```

---

# 7. Vì sao Profile nên immutable?

Ta dùng:

```python
@dataclass(frozen=True)
class BrowserProfile:
```

vì profile là **configuration/value**.

Không muốn:

```python
profile.impersonate = "firefox_146"
```

sau khi client đã được tạo.

Mô hình:

```text
BrowserProfile
      ↓
AsyncClient
```

nên có tính ổn định.

---

# 8. Profile Pool + Async

Crawler của chúng ta chạy async:

```text
100 URLs
    ↓
gather()
    ↓
Semaphore(10)
```

Có thể có nhiều coroutine cùng gọi:

```python
profile = await pool.next()
```

Vì vậy ta có thể dùng `asyncio.Lock`, giống ProxyPool.

```python
import asyncio


class BrowserProfilePool:

    def __init__(
        self,
        profiles: list[BrowserProfile],
    ):
        if not profiles:
            raise ValueError(
                "Browser profile pool cannot be empty"
            )

        self.profiles = profiles
        self.index = 0
        self.lock = asyncio.Lock()

    async def next(self) -> BrowserProfile:

        async with self.lock:

            profile = self.profiles[self.index]

            self.index = (
                self.index + 1
            ) % len(self.profiles)

            return profile
```

Lock chỉ bảo vệ:

```text
index
selection
```

không bảo vệ HTTP request.

---

# 9. Sai lầm: lock cả HTTP request

Không làm:

```python
async with self.lock:

    profile = ...
    response = await client.get(url)
```

Nếu request mất 5 giây:

```text
Task A
 ↓
LOCK
 ↓
HTTP 5s
 ↓
release
```

Task B, C, D phải chờ.

Đúng:

```text
LOCK
 ↓
chọn profile
 ↓
RELEASE
 ↓
HTTP
```

---

# 10. Nhưng Pool chưa đủ

Ta có:

```text
Profile Pool
    ↓
Chrome 146
```

Nhưng profile phải được gắn với **client**.

Ví dụ:

```python
profile = BrowserProfile(
    impersonate="chrome_146",
    os="windows",
)

client = primp.AsyncClient(
    impersonate=profile.impersonate,
    impersonate_os=profile.os,
)
```

Ta không nên:

```text
Profile Pool
    ↓
profile
    ↓
mỗi request tạo AsyncClient
```

vì đã học ở Buổi 31:

```text
AsyncClient
=
long-lived resource
```

---

# 11. Mô hình tốt hơn: Profile + Client

Ta có:

```text
Profile A
    ↓
AsyncClient A

Profile B
    ↓
AsyncClient B

Profile C
    ↓
AsyncClient C
```

Có thể mô hình hóa:

```python
from dataclasses import dataclass


@dataclass
class BrowserClient:
    profile: BrowserProfile
    client: object
```

Sau này:

```text
BrowserClientPool
       │
       ├── BrowserClient A
       ├── BrowserClient B
       └── BrowserClient C
```

Đây thực tế gần với thứ crawler cần hơn là chỉ pool các string profile.

---

# 12. Tại sao?

Giả sử:

```text
Profile A
Chrome 146 + Windows
```

Client A có thể giữ:

```text
Client A
├── Profile
├── Cookies
└── Connection state
```

Trong khi:

```text
Profile B
Chrome 147 + Windows
```

có:

```text
Client B
├── Profile
├── Cookies
└── Connection state
```

Như vậy identity ổn định hơn:

```text
Task
 ↓
BrowserClient A
 ↓
Profile A
 ↓
HTTP
```

---

# 13. BrowserClientPool

Ta có thể thiết kế:

```python
@dataclass
class BrowserClient:

    profile: BrowserProfile
    client: object
```

Pool:

```python
class BrowserClientPool:

    def __init__(
        self,
        clients: list[BrowserClient],
    ):
        if not clients:
            raise ValueError(
                "Client pool cannot be empty"
            )

        self.clients = clients
        self.index = 0

    def next(self) -> BrowserClient:

        client = self.clients[self.index]

        self.index = (
            self.index + 1
        ) % len(self.clients)

        return client
```

Đây là một abstraction hữu ích hơn khi chúng ta đi vào crawler thực tế.

---

# 14. Tạo BrowserClient từ profile

```python
import primp


def create_browser_client(
    profile: BrowserProfile,
) -> BrowserClient:

    client = primp.AsyncClient(
        impersonate=profile.impersonate,
        impersonate_os=profile.os,
    )

    return BrowserClient(
        profile=profile,
        client=client,
    )
```

Sau đó:

```python
profiles = [
    BrowserProfile(
        "chrome_146",
        "windows",
    ),
    BrowserProfile(
        "chrome_147",
        "windows",
    ),
]

clients = [
    create_browser_client(profile)
    for profile in profiles
]
```

---

# 15. Nhưng có một điểm cần chú ý với AsyncClient

Ta đang tạo:

```python
primp.AsyncClient(...)
```

cho từng profile.

Điều này có nghĩa:

```text
2 profiles
→
2 clients
```

Nếu:

```text
20 profiles
→
20 clients
```

thì tài nguyên cũng tăng.

Vì vậy không nên tạo hàng trăm profile/client chỉ để "random".

Pool phải có kích thước hợp lý.

---

# 16. Profile Pool không phải concurrency pool

Đây là hai khái niệm khác nhau.

```text
Semaphore(10)
```

quyết định:

> Có tối đa bao nhiêu request đang chạy?

Còn:

```text
BrowserClientPool
```

quyết định:

> Request sử dụng browser client nào?

Ví dụ:

```text
10 concurrent requests
+
3 browser clients
```

hoàn toàn có thể tồn tại.

```text
                Semaphore(10)
                     │
       ┌─────────────┼─────────────┐
       ↓             ↓             ↓
   Client A      Client B      Client C
```

---

# 17. Profile Pool + Proxy Pool

Đây là lúc kiến trúc bắt đầu thú vị.

Ta có:

```text
BrowserProfilePool
        │
        ├── Chrome 146
        ├── Chrome 147
        └── Firefox 146

ProxyPool
        │
        ├── Proxy A
        ├── Proxy B
        └── Proxy C
```

Không nên tự động ghép random:

```text
Chrome 146 + Proxy C
Firefox 146 + Proxy A
...
```

mỗi request.

Thay vào đó, về sau chúng ta có thể xây **stable worker identity**:

```text
Worker 1
 ├── Browser Profile A
 └── Proxy A

Worker 2
 ├── Browser Profile B
 └── Proxy B

Worker 3
 ├── Browser Profile C
 └── Proxy C
```

Đây là mô hình rất phù hợp để phát triển crawler.

---

# 18. Worker Identity

Concept:

```text
Crawler Worker
    │
    ├── BrowserProfile
    ├── Proxy
    └── AsyncClient
```

Ví dụ:

```text
Worker A
Chrome 146 + Windows
Proxy A
Client A

Worker B
Chrome 147 + Windows
Proxy B
Client B

Worker C
Firefox 146 + Windows
Proxy C
Client C
```

Request:

```text
Chapter 1 → Worker A
Chapter 2 → Worker B
Chapter 3 → Worker C
Chapter 4 → Worker A
```

Đây là hướng thiết kế chúng ta sẽ tiến tới ở **Buổi 39 — Fetcher Architecture**.

---

# 19. Profile Health

Giống ProxyPool, profile cũng có thể có state:

```python
@dataclass
class ProfileState:

    profile: BrowserProfile
    failures: int = 0
    healthy: bool = True
```

Nhưng cần phân biệt:

```text
Proxy failure
```

với:

```text
Browser profile failure
```

Ví dụ:

```text
Timeout
```

chưa chắc profile sai.

Có thể là:

```text
network
proxy
server
```

Do đó **không nên mark profile unhealthy chỉ vì một HTTP request thất bại**.

---

# 20. Khi nào profile nên bị loại?

Đây là vấn đề Error Classification.

Ví dụ:

```text
DNS failure
    → có thể proxy

Connection failure
    → có thể proxy/network

HTTP 500
    → server

HTTP 404
    → resource

HTTP 403
    → cần phân tích context

Timeout
    → network/server/proxy
```

Không thể kết luận:

```text
request failed
→ browser profile hỏng
```

Vì vậy hôm nay chỉ xây **profile selection**, chưa xây profile health.

Phần này sẽ kết nối với:

```text
48. Error Classification
```

---

# 21. Random Profile có nên dùng?

`primp` hiện có profile:

```text
random
```

theo danh sách chính thức. ([PyPI][1])

Nhưng:

```python
primp.AsyncClient(
    impersonate="random"
)
```

không nên được hiểu là:

```text
mỗi request
→ random browser
```

Client được tạo với một configuration/profile.

Nếu muốn quản lý identity rõ ràng:

```text
Pool
 ↓
chọn profile
 ↓
tạo/giữ client
```

sẽ dễ kiểm soát hơn.

---

# 22. Không nên random User-Agent riêng

Sai:

```python
profile = BrowserProfile(
    impersonate="chrome_146",
    os="windows",
)

headers = {
    "User-Agent": "Firefox..."
}
```

Ta đã học ở Buổi 27:

```text
Browser Profile
    ↓
TLS
HTTP/2
Headers
```

Nếu tự thay User-Agent thành Firefox:

```text
UA       → Firefox
TLS      → Chrome
HTTP/2   → Chrome
```

thì profile trở nên không nhất quán.

`primp` cung cấp browser profiles chính vì nó mô phỏng nhiều đặc điểm mạng của browser, không chỉ UA. ([PyPI][1])

---

# 23. Browser Profile Pool hoàn chỉnh

Đây là phiên bản đủ tốt cho giai đoạn hiện tại:

```python
import asyncio
from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserProfile:
    impersonate: str
    os: str | None = None


class BrowserProfilePool:

    def __init__(
        self,
        profiles: list[BrowserProfile],
    ):
        if not profiles:
            raise ValueError(
                "Browser profile pool cannot be empty"
            )

        self.profiles = profiles
        self.index = 0
        self.lock = asyncio.Lock()

    async def next(self) -> BrowserProfile:

        async with self.lock:

            profile = self.profiles[self.index]

            self.index = (
                self.index + 1
            ) % len(self.profiles)

            return profile
```

Test:

```python
async def main():

    pool = BrowserProfilePool([
        BrowserProfile(
            "chrome_146",
            "windows",
        ),
        BrowserProfile(
            "chrome_147",
            "windows",
        ),
        BrowserProfile(
            "firefox_146",
            "windows",
        ),
    ])

    for _ in range(10):

        profile = await pool.next()

        print(
            f"{profile.impersonate}"
            f" + "
            f"{profile.os}"
        )


if __name__ == "__main__":
    asyncio.run(main())
```

---

# 24. Test concurrent selection

```python
async def worker(
    pool: BrowserProfilePool,
    worker_id: int,
):

    profile = await pool.next()

    print(
        f"Worker {worker_id}: "
        f"{profile.impersonate} "
        f"+ {profile.os}"
    )


async def main():

    pool = BrowserProfilePool([
        BrowserProfile(
            "chrome_146",
            "windows",
        ),
        BrowserProfile(
            "chrome_147",
            "windows",
        ),
        BrowserProfile(
            "firefox_146",
            "windows",
        ),
    ])

    await asyncio.gather(
        *(
            worker(pool, i)
            for i in range(12)
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
```

Điều cần kiểm tra không phải thứ tự output tuyệt đối, mà là pool vẫn chọn profile hợp lệ và state `index` không bị corrupt.

---

# 25. Kết hợp với Semaphore

Bây giờ:

```text
URLs
 ↓
gather()
 ↓
Semaphore(10)
 ↓
ProfilePool
 ↓
BrowserClient
 ↓
HTTP
```

Ví dụ:

```python
class AsyncFetcher:

    def __init__(
        self,
        profile_pool,
        semaphore,
    ):
        self.profile_pool = profile_pool
        self.semaphore = semaphore

    async def get(self, url):

        async with self.semaphore:

            profile = (
                await self.profile_pool.next()
            )

            print(
                "Using:",
                profile.impersonate,
                profile.os,
            )

            # HTTP implementation
```

Ở đây `Semaphore` giới hạn:

```text
concurrency
```

còn `ProfilePool` quản lý:

```text
browser identity selection
```

Hai trách nhiệm độc lập.

---

# 26. Kiến trúc hiện tại

Sau Buổi 36:

```text
AsyncFetcher
    │
    ├── Semaphore
    ├── ProxyPool
    └── RetryPolicy
```

Sau Buổi 37:

```text
AsyncFetcher
    │
    ├── Semaphore
    ├── ProxyPool
    ├── BrowserProfilePool
    └── RetryPolicy
```

Flow:

```text
                         URLs
                          │
                          ↓
                    asyncio.gather()
                          │
                          ↓
                    Semaphore(10)
                          │
              ┌───────────┴───────────┐
              ↓                       ↓
         ProxyPool             BrowserProfilePool
              │                       │
              ↓                       ↓
          Proxy A              Chrome 146
          Proxy B              Chrome 147
          Proxy C              Firefox 146
              │                       │
              └───────────┬───────────┘
                          ↓
                     HTTP Client
                          ↓
                   primp.AsyncClient
```

---

# 27. DDD/SOLID

Một điểm rất quan trọng:

### Domain

```text
Novel
Chapter
CrawlTask
```

không biết:

```text
primp
ProxyPool
BrowserProfilePool
AsyncClient
```

### Infrastructure

```text
PrimpAsyncClient
ProxyPool
BrowserProfilePool
```

chịu trách nhiệm HTTP/network.

### Application

```text
AsyncNovelFetcher
CrawlChapter
CrawlNovel
```

điều phối chúng.

Mô hình:

```text
Domain
   ↑
Application
   ↑
Infrastructure
```

hoặc nhìn theo dependency:

```text
Application
    ↓
interfaces / abstractions
    ↓
Infrastructure implementations
```

---

# 28. Một abstraction chưa nên tạo

Hiện tại **không cần**:

```text
IBrowserProfilePool
BrowserProfileFactory
BrowserProfileStrategy
BrowserProfileManager
BrowserProfileHealthService
BrowserProfileRegistry
```

Chỉ cần:

```text
BrowserProfile
BrowserProfilePool
```

là đủ.

Khi requirement thực sự xuất hiện mới tách abstraction.

Đây là nguyên tắc chúng ta đã giữ xuyên suốt project:

> **Abstraction vừa đủ, không abstraction vì abstraction.**

---

# 29. Bài tập thực hành

### Bài 1

Tạo:

```text
Chrome 146 + Windows
Chrome 147 + Windows
Firefox 146 + Windows
Edge 146 + Windows
```

và chạy pool 12 lần.

---

### Bài 2

Tạo:

```text
100 async tasks
```

mỗi task gọi:

```python
profile = await pool.next()
```

Kiểm tra pool hoạt động ổn định.

---

### Bài 3

Tạo:

```text
Semaphore(3)
+
BrowserProfilePool(3)
```

Quan sát:

```text
3 request active
```

nhưng profile được chọn luân phiên.

---

# 30. Bài tập chính — Browser Client Pool

Hãy xây:

```text
BrowserProfile
       ↓
BrowserClient
       ↓
BrowserClientPool
```

Mục tiêu:

```text
Profile A → Client A
Profile B → Client B
Profile C → Client C
```

sau đó:

```python
client = await pool.next()
```

và:

```python
response = await client.client.get(url)
```

Điểm quan trọng là **client phải được tạo một lần và tái sử dụng**, thay vì tạo `AsyncClient` mới cho mỗi request. Official `primp` cung cấp cả sync `Client` và async `AsyncClient`, với browser profile được cấu hình ngay khi client được khởi tạo. ([PyPI][1])

---

# 31. Bức tranh sau 37 buổi

Chúng ta hiện có:

```text
31  AsyncClient              ✅
32  async GET                ✅
33  Concurrent Requests      ✅
34  Semaphore                ✅
35  Timeout + Retry          ✅
36  Proxy Pool               ✅
37  Browser Profile Pool     ✅
38  Rate Limiting            ← tiếp theo
39  Fetcher Architecture
40  Async Novel Fetcher
```

Và architecture đang hình thành:

```text
                         AsyncNovelFetcher
                                │
          ┌─────────────────────┼─────────────────────┐
          ↓                     ↓                     ↓
     Semaphore              ProxyPool          ProfilePool
          │                     │                     │
          └─────────────────────┼─────────────────────┘
                                ↓
                       Browser Client Pool
                                ↓
                       primp.AsyncClient
                                ↓
                         Timeout / Retry
                                ↓
                              HTTP
```

**Buổi 38 — Rate Limiting** sẽ bổ sung một mảnh còn thiếu rất quan trọng:

```text
Semaphore
    =
bao nhiêu request chạy cùng lúc

Rate Limiter
    =
bao nhiêu request được phép phát sinh
trong một khoảng thời gian
```

Từ đó crawler sẽ có cả **concurrency control + traffic control**, trước khi chúng ta bước sang **Buổi 39 — Fetcher Architecture**.

[1]: https://pypi.org/project/primp/2.0.1/?utm_source=chatgpt.com "primp · PyPI"
