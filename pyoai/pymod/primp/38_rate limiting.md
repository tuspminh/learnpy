# Buổi 38 — Rate Limiting

Đến đây crawler của chúng ta đã có:

```text
31 AsyncClient              ✅
32 async GET                ✅
33 Concurrent Requests      ✅
34 Semaphore                ✅
35 Timeout + Retry          ✅
36 Proxy Pool               ✅
37 Browser Profile Pool     ✅
38 Rate Limiting            ← hôm nay
39 Fetcher Architecture
40 Async Novel Fetcher
```

Điểm quan trọng nhất của Buổi 38:

> **Semaphore kiểm soát số request đang chạy. Rate Limiter kiểm soát tốc độ phát sinh request.**

Hai thứ này **không thay thế cho nhau**.

---

# 1. Vì sao cần Rate Limiting?

Giả sử:

```python
await asyncio.gather(
    *(fetch(url) for url in urls)
)
```

Có 1.000 URL.

Ta dùng:

```python
semaphore = asyncio.Semaphore(10)
```

Điều đó chỉ có nghĩa:

```text
tối đa 10 request đang active
```

Nhưng khi request hoàn thành rất nhanh:

```text
t=0.0   request 1
t=0.1   request 2
t=0.2   request 3
t=0.3   request 4
...
```

Crawler vẫn có thể tạo ra lượng request rất lớn trong một khoảng thời gian ngắn.

---

# 2. Semaphore và Rate Limiter

Hãy phân biệt thật rõ.

## Semaphore

```text
"Bao nhiêu request được chạy đồng thời?"
```

Ví dụ:

```python
asyncio.Semaphore(10)
```

→ tối đa 10 request đang chạy.

---

## Rate Limiter

```text
"Bao nhiêu request được phép bắt đầu trong một khoảng thời gian?"
```

Ví dụ:

```text
5 requests / second
```

thì tốc độ mục tiêu là:

```text
0.0s → request
0.2s → request
0.4s → request
0.6s → request
0.8s → request
```

---

# 3. Ví dụ dễ hình dung

Không có rate limiting:

```text
Request
Request
Request
Request
Request
Request
Request
Request
...
```

Có Semaphore:

```text
[10 requests active]
        ↓
wait
        ↓
[10 requests active]
```

Có Rate Limiter:

```text
request
  ↓
wait 200ms
  ↓
request
  ↓
wait 200ms
  ↓
request
```

Có cả hai:

```text
             ┌── concurrency limit
             ↓
Request → Semaphore → Rate Limiter → HTTP
```

---

# 4. Một Rate Limiter đơn giản

Ta bắt đầu bằng cách dễ hiểu nhất.

Mục tiêu:

```text
5 requests / second
```

Tương đương:

```text
1 request / 0.2 second
```

Công thức:

```text
interval = 1 / rate
```

Ví dụ:

```python
rate = 5

interval = 1 / rate

print(interval)
```

Kết quả:

```text
0.2
```

---

# 5. RateLimiter đầu tiên

```python
import asyncio


class RateLimiter:

    def __init__(
        self,
        requests_per_second: float,
    ):
        if requests_per_second <= 0:
            raise ValueError(
                "Rate must be greater than 0"
            )

        self.interval = (
            1 / requests_per_second
        )

        self._lock = asyncio.Lock()
        self._next_allowed = 0.0

    async def acquire(self):
        loop = asyncio.get_running_loop()

        async with self._lock:

            now = loop.time()

            wait_time = (
                self._next_allowed - now
            )

            if wait_time > 0:
                await asyncio.sleep(
                    wait_time
                )

            self._next_allowed = (
                loop.time()
                + self.interval
            )
```

Sử dụng:

```python
async def worker(
    limiter: RateLimiter,
    name: str,
):
    await limiter.acquire()

    print(
        name,
        asyncio.get_running_loop().time(),
    )
```

---

# 6. Tại sao cần Lock?

Đây là phần rất quan trọng.

Giả sử có:

```text
Task A
Task B
Task C
```

cùng gọi:

```python
await limiter.acquire()
```

Nếu không có Lock:

```text
A đọc time
B đọc time
C đọc time
```

cả ba có thể thấy cùng một thời điểm.

Sau đó:

```text
A → request
B → request
C → request
```

gần như đồng thời.

Như vậy Rate Limiter bị phá.

---

# 7. Lock bảo vệ state

Ta có:

```python
self._next_allowed
```

đây là mutable state.

Flow:

```text
Task A
   ↓
LOCK
   ↓
calculate wait
   ↓
update _next_allowed
   ↓
UNLOCK

Task B
   ↓
LOCK
   ↓
...
```

Nhờ đó các task xếp hàng.

---

# 8. Nhưng code trên có một vấn đề

Chúng ta đang:

```python
async with self._lock:
    await asyncio.sleep(wait_time)
```

Điều này nghĩa là Lock bị giữ trong lúc sleep.

Ví dụ:

```text
Task A
 ↓
LOCK
 ↓
sleep 200ms
 ↓
release

Task B
 ↓
LOCK
```

Với một RateLimiter đơn giản thì vẫn đúng, nhưng không tối ưu.

Ta có thể thiết kế tốt hơn.

---

# 9. Token spacing

Một cách đơn giản và hiệu quả cho crawler là **spacing**:

```text
5 req/s
```

thì mỗi request cách nhau:

```text
200 ms
```

Mô hình:

```text
|----200ms----|----200ms----|----200ms----|
     Req 1          Req 2          Req 3
```

Đây là kiểu **fixed interval / pacing**.

Nó rất dễ hiểu và phù hợp để học.

---

# 10. Rate Limiter hoàn chỉnh hơn

```python
import asyncio


class RateLimiter:

    def __init__(
        self,
        requests_per_second: float,
    ):
        if requests_per_second <= 0:
            raise ValueError(
                "requests_per_second "
                "must be > 0"
            )

        self.interval = (
            1.0 / requests_per_second
        )

        self._lock = asyncio.Lock()
        self._next_allowed = 0.0

    async def acquire(self):

        loop = asyncio.get_running_loop()

        async with self._lock:

            now = loop.time()

            if now < self._next_allowed:

                wait_time = (
                    self._next_allowed - now
                )

                self._next_allowed += (
                    self.interval
                )

            else:

                wait_time = 0.0

                self._next_allowed = (
                    now + self.interval
                )

        if wait_time > 0:
            await asyncio.sleep(
                wait_time
            )
```

Điểm quan trọng:

```text
Lock
 ↓
tính toán
 ↓
cập nhật state
 ↓
release
 ↓
sleep
```

Không giữ Lock trong lúc sleep.

---

# 11. Test RateLimiter

```python
import asyncio


async def worker(
    limiter: RateLimiter,
    worker_id: int,
):

    await limiter.acquire()

    now = (
        asyncio.get_running_loop().time()
    )

    print(
        f"Worker {worker_id} "
        f"started at {now:.3f}"
    )


async def main():

    limiter = RateLimiter(
        requests_per_second=5
    )

    start = (
        asyncio.get_running_loop().time()
    )

    await asyncio.gather(
        *(
            worker(limiter, i)
            for i in range(10)
        )
    )

    end = (
        asyncio.get_running_loop().time()
    )

    print(
        f"Elapsed: {end - start:.3f}s"
    )


if __name__ == "__main__":
    asyncio.run(main())
```

Với 5 req/s, các task sẽ được phân bố theo khoảng xấp xỉ:

```text
0.0
0.2
0.4
0.6
0.8
1.0
1.2
...
```

Độ chính xác thực tế phụ thuộc scheduler và hệ điều hành.

---

# 12. Rate Limiting đặt ở đâu?

Đây là câu hỏi architecture quan trọng.

Ta có:

```text
Application
    ↓
AsyncFetcher
    ↓
Semaphore
    ↓
RateLimiter
    ↓
HTTP Client
```

Tại sao?

Vì RateLimiter là concern của **outbound HTTP**.

Domain không nên biết:

```text
requests_per_second
asyncio.sleep
primp
proxy
```

---

# 13. Kết hợp Semaphore + RateLimiter

Đây là phần quan trọng nhất của bài.

```python
import asyncio


class AsyncFetcher:

    def __init__(
        self,
        client,
        concurrency: int,
        rate_limiter: RateLimiter,
    ):
        self.client = client

        self.semaphore = (
            asyncio.Semaphore(concurrency)
        )

        self.rate_limiter = rate_limiter

    async def get(self, url: str):

        async with self.semaphore:

            await self.rate_limiter.acquire()

            return await self.client.get(
                url,
                timeout=10,
            )
```

Flow:

```text
get(url)
   ↓
Semaphore
   ↓
RateLimiter
   ↓
AsyncClient
   ↓
HTTP
```

---

# 14. Có một quyết định architecture ở đây

Ta đặt:

```python
async with semaphore:
    await limiter.acquire()
    response = await client.get(...)
```

Như vậy semaphore slot được giữ trong lúc:

```text
RateLimiter waiting
```

Ví dụ:

```text
Semaphore = 10
Rate = 2 req/s
```

Task:

```text
Task A → semaphore → rate wait → HTTP
Task B → semaphore → rate wait
Task C → semaphore → rate wait
...
```

10 slot có thể bị chiếm bởi những task đang chờ rate limit.

Điều này **đúng về mặt giới hạn**, nhưng chưa tối ưu.

---

# 15. Đặt RateLimiter trước Semaphore

Ta có thể:

```python
async def get(self, url):

    await self.rate_limiter.acquire()

    async with self.semaphore:

        return await self.client.get(
            url,
            timeout=10,
        )
```

Flow:

```text
get
 ↓
RateLimiter
 ↓
Semaphore
 ↓
HTTP
```

Lúc này:

```text
RateLimiter
```

quyết định khi nào request được phép bắt đầu.

Sau đó:

```text
Semaphore
```

quyết định còn slot HTTP hay không.

---

# 16. Hai thứ có ý nghĩa khác nhau

### RateLimiter trước

```text
RateLimiter
    ↓
"Đã đến lúc được phép gửi chưa?"
    ↓
Semaphore
    ↓
"Có slot HTTP không?"
```

### Semaphore trước

```text
Semaphore
    ↓
"Có slot không?"
    ↓
RateLimiter
    ↓
"Đã đến lúc gửi chưa?"
```

Đối với crawler, tôi khuyên chúng ta conceptualize:

```text
RateLimiter → Semaphore → HTTP
```

để không giữ concurrency slot trong lúc chờ pacing.

---

# 17. AsyncFetcher

Ta có thể viết:

```python
class AsyncFetcher:

    def __init__(
        self,
        client,
        concurrency: int,
        rate_limiter: RateLimiter,
    ):
        self.client = client

        self.semaphore = (
            asyncio.Semaphore(concurrency)
        )

        self.rate_limiter = rate_limiter

    async def get(
        self,
        url: str,
    ):

        await self.rate_limiter.acquire()

        async with self.semaphore:

            return await self.client.get(
                url,
                timeout=10,
            )
```

---

# 18. Retry và Rate Limiting

Đây là chỗ rất dễ thiết kế sai.

Buổi 35:

```text
Request
 ↓
Retry
 ↓
Failure
 ↓
Backoff
 ↓
Retry
```

Bây giờ:

```text
RateLimiter
+
Retry
```

Câu hỏi:

> Retry có phải request mới và phải chịu Rate Limit không?

**Có.**

Nếu request ban đầu:

```text
GET chapter
```

thất bại:

```text
timeout
```

và retry:

```text
GET chapter
```

thì retry cũng là một HTTP attempt.

Do đó:

```text
RateLimiter
    ↓
Attempt 1
    ↓
failure
    ↓
backoff
    ↓
RateLimiter
    ↓
Attempt 2
```

---

# 19. Không nên

```text
RateLimiter
 ↓
Retry loop
 ├── attempt 1
 ├── attempt 2
 └── attempt 3
```

nếu mục tiêu là giới hạn **mọi HTTP attempt**.

Vì lúc đó 3 retry có thể phát sinh liên tiếp.

Tốt hơn:

```text
Retry attempt
     ↓
RateLimiter
     ↓
HTTP
```

---

# 20. Kiến trúc Retry + RateLimiter

```text
fetch()
  ↓
RetryPolicy
  ↓
Attempt
  ↓
RateLimiter
  ↓
Semaphore
  ↓
HTTP
```

Flow:

```text
Attempt 1
 ↓
RateLimiter
 ↓
Semaphore
 ↓
HTTP
 ↓
500
 ↓
backoff
 ↓
Attempt 2
 ↓
RateLimiter
 ↓
Semaphore
 ↓
HTTP
```

Điều này sẽ giúp chúng ta sau này xây Fetcher Architecture sạch hơn.

---

# 21. Rate Limiting theo host

Novel crawler có thể crawl nhiều website:

```text
truyenfull
nguonkhac
site-c
site-d
```

Không nhất thiết dùng:

```text
global rate = 2 req/s
```

cho tất cả.

Có thể:

```text
Host A → 2 req/s
Host B → 5 req/s
Host C → 1 req/s
```

Mô hình:

```text
RateLimiterRegistry
       │
       ├── truyenfull → 2/s
       ├── site-b     → 5/s
       └── site-c     → 1/s
```

Nhưng **chưa cần xây Registry hôm nay**.

---

# 22. Rate Limit toàn crawler

Ví dụ:

```text
Global:
10 requests/sec
```

thì tất cả request dùng chung:

```text
GlobalRateLimiter
```

```text
Crawler
   │
   ├── Worker A ─┐
   ├── Worker B  │
   ├── Worker C  ├── RateLimiter 10/s
   ├── Worker D  │
   └── Worker E ─┘
```

---

# 23. Rate Limit theo domain

Nếu crawler nhiều source:

```text
Crawler
 │
 ├── Source A → RateLimiter A
 │
 ├── Source B → RateLimiter B
 │
 └── Source C → RateLimiter C
```

Đây thường là architecture thực tế hơn.

Vì mỗi website có thể có:

```text
robots.txt
rate policy
server capacity
```

và crawler nên tuân thủ các yêu cầu/giới hạn truy cập áp dụng cho nguồn đó.

---

# 24. Rate Limiter không phải Retry

Đừng nhầm:

```text
RateLimiter
```

với:

```text
RetryPolicy
```

### RateLimiter

```text
Khi nào được phép gửi?
```

### RetryPolicy

```text
Có gửi lại sau failure không?
```

### Backoff

```text
Chờ bao lâu trước attempt tiếp theo?
```

### Semaphore

```text
Bao nhiêu request được active?
```

Ta có:

```text
             HTTP Control
                  │
       ┌──────────┼──────────┐
       ↓          ↓          ↓
 Semaphore   RateLimiter   Retry
       │          │          │
 concurrency    speed     failure policy
```

---

# 25. `Retry-After`

Ở Buổi 35 chúng ta đã nói về:

```text
429 Too Many Requests
```

Server có thể trả:

```http
Retry-After: 5
```

Điều đó nghĩa là server yêu cầu client chờ theo giá trị đó trước khi thử lại.

Do đó production RetryPolicy nên ưu tiên:

```text
Retry-After
```

khi hợp lệ, thay vì chỉ:

```text
exponential backoff
```

Flow:

```text
HTTP 429
   ↓
Retry-After: 5
   ↓
wait 5 sec
   ↓
RateLimiter
   ↓
retry
```

---

# 26. Rate Limiting và `Retry-After`

Hai cơ chế không mâu thuẫn:

```text
RateLimiter
    =
client-side pacing

Retry-After
    =
server-provided delay
```

Ví dụ:

```text
RateLimiter nói:
"Request tiếp theo sớm nhất 0.5s nữa."

Server nói:
"Retry sau 5s."

```

thì retry nên chờ theo policy phù hợp với `Retry-After`.

---

# 27. Token Bucket

Đến đây chúng ta đang dùng:

```text
Fixed Interval / Pacing
```

Nhưng rate limiting thực tế còn có:

```text
Token Bucket
Leaky Bucket
Sliding Window
Fixed Window
```

Một trong những mô hình phổ biến là:

```text
Token Bucket
```

Ví dụ:

```text
capacity = 5
rate = 2 tokens/sec
```

Bucket:

```text
┌─────────────┐
│ ● ● ● ● ●   │
└─────────────┘
```

Mỗi request lấy một token:

```text
request
   ↓
take token
   ↓
HTTP
```

Token tự được bổ sung theo thời gian.

---

# 28. Token Bucket khác Fixed Interval

Fixed interval:

```text
0.0 → request
0.5 → request
1.0 → request
1.5 → request
```

Token bucket có thể cho burst:

```text
● ● ● ● ●
↓ ↓ ↓ ↓ ↓
5 requests
```

sau đó phải chờ refill.

Điều này phù hợp với một số workload hơn.

Nhưng đối với bài học hiện tại:

> Chúng ta dùng **simple pacing limiter** trước.

Sau này nếu crawler cần burst control, ta mới chuyển sang token bucket.

---

# 29. RateLimiter Config

Giống các config trước, có thể dùng:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RateLimitConfig:

    requests_per_second: float = 2.0
```

Ví dụ:

```python
config = RateLimitConfig(
    requests_per_second=2
)
```

Sau đó:

```python
limiter = RateLimiter(
    config.requests_per_second
)
```

---

# 30. Hoàn chỉnh: Config + Limiter

```python
import asyncio
from dataclasses import dataclass


@dataclass(frozen=True)
class RateLimitConfig:
    requests_per_second: float = 2.0


class RateLimiter:

    def __init__(
        self,
        config: RateLimitConfig,
    ):
        if config.requests_per_second <= 0:
            raise ValueError(
                "requests_per_second "
                "must be > 0"
            )

        self.interval = (
            1.0
            / config.requests_per_second
        )

        self._lock = asyncio.Lock()
        self._next_allowed = 0.0

    async def acquire(self):

        loop = asyncio.get_running_loop()

        async with self._lock:

            now = loop.time()

            if now < self._next_allowed:

                wait_time = (
                    self._next_allowed - now
                )

                self._next_allowed += (
                    self.interval
                )

            else:

                wait_time = 0.0

                self._next_allowed = (
                    now + self.interval
                )

        if wait_time > 0:

            await asyncio.sleep(
                wait_time
            )
```

---

# 31. Test độc lập không cần Internet

```python
async def worker(
    limiter: RateLimiter,
    worker_id: int,
):

    await limiter.acquire()

    now = (
        asyncio.get_running_loop().time()
    )

    print(
        f"[{now:.3f}] "
        f"worker={worker_id}"
    )


async def main():

    config = RateLimitConfig(
        requests_per_second=2
    )

    limiter = RateLimiter(config)

    await asyncio.gather(
        *(
            worker(limiter, i)
            for i in range(6)
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
```

Ta kỳ vọng khoảng:

```text
worker 0 → t=0.0
worker 1 → t=0.5
worker 2 → t=1.0
worker 3 → t=1.5
worker 4 → t=2.0
worker 5 → t=2.5
```

Không cần chính xác tuyệt đối đến millisecond.

---

# 32. Tích hợp với `primp.AsyncClient`

Về mặt kiến trúc:

```python
import asyncio
import primp


class AsyncFetcher:

    def __init__(
        self,
        client: primp.AsyncClient,
        concurrency: int,
        rate_limiter: RateLimiter,
    ):
        self.client = client

        self.semaphore = (
            asyncio.Semaphore(concurrency)
        )

        self.rate_limiter = rate_limiter

    async def get(
        self,
        url: str,
    ):

        await self.rate_limiter.acquire()

        async with self.semaphore:

            return await self.client.get(
                url,
                timeout=10,
            )
```

Sử dụng:

```python
async def main():

    limiter = RateLimiter(
        RateLimitConfig(
            requests_per_second=2
        )
    )

    async with primp.AsyncClient(
        impersonate="chrome_146",
        impersonate_os="windows",
    ) as client:

        fetcher = AsyncFetcher(
            client=client,
            concurrency=5,
            rate_limiter=limiter,
        )

        urls = [
            "https://httpbin.org/get?page=1",
            "https://httpbin.org/get?page=2",
            "https://httpbin.org/get?page=3",
            "https://httpbin.org/get?page=4",
            "https://httpbin.org/get?page=5",
        ]

        responses = await asyncio.gather(
            *(
                fetcher.get(url)
                for url in urls
            )
        )

        for response in responses:

            print(
                response.status_code,
                response.url,
            )


if __name__ == "__main__":
    asyncio.run(main())
```

---

# 33. Một điểm cực kỳ quan trọng: Semaphore không tạo ra Rate Limit

Ví dụ:

```python
Semaphore(2)
```

với 100 request nhanh:

```text
Task 1 → 0.0
Task 2 → 0.0

Task 3 → 0.1
Task 4 → 0.1

Task 5 → 0.2
Task 6 → 0.2
```

Có thể vẫn có:

```text
10 request / second
```

hoặc hơn.

Semaphore chỉ giới hạn:

```text
active requests
```

không giới hạn:

```text
requests / second
```

---

# 34. Crawler hiện tại

Sau Buổi 38:

```text
                           AsyncFetcher
                                │
        ┌───────────────────────┼───────────────────────┐
        ↓                       ↓                       ↓
  RateLimiter             Semaphore              RetryPolicy
        │                       │                       │
     speed                 concurrency             failures
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                ↓
                         BrowserClient
                                ↓
                       primp.AsyncClient
                                ↓
                               HTTP
```

Và bên cạnh đó:

```text
ProxyPool
BrowserProfilePool
```

quản lý resource/identity.

---

# 35. Architecture đầy đủ sau Buổi 38

```text
                         Application
                              │
                              ↓
                     AsyncNovelFetcher
                              │
        ┌─────────────────────┼─────────────────────┐
        ↓                     ↓                     ↓
   RateLimiter            Semaphore            RetryPolicy
        │                     │                     │
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ↓
                        ProxyPool
                              │
                              ↓
                   BrowserProfilePool
                              │
                              ↓
                     BrowserClient
                              │
                              ↓
                    primp.AsyncClient
                              │
                              ↓
                             HTTP
```

Đây đã bắt đầu giống một **Fetcher infrastructure thật sự**, chứ không còn là một wrapper đơn giản quanh `primp`.

---

# 36. Nhưng đừng đưa mọi thứ vào `AsyncFetcher`

Một lỗi rất dễ mắc:

```python
class AsyncFetcher:

    def __init__(
        self,
        client,
        proxy_pool,
        profile_pool,
        retry_policy,
        rate_limiter,
        semaphore,
        logger,
        cache,
        parser,
        database,
        ...
    ):
        ...
```

Đây là dấu hiệu:

> `AsyncFetcher` đang trở thành God Object.

Ở Buổi 39 chúng ta sẽ xử lý chính vấn đề này.

---

# 37. Ranh giới trách nhiệm

Hiện tại:

| Component            | Trách nhiệm             |
| -------------------- | ----------------------- |
| `AsyncClient`        | HTTP transport          |
| `BrowserProfile`     | browser/network profile |
| `BrowserProfilePool` | chọn profile            |
| `ProxyPool`          | quản lý proxy           |
| `Semaphore`          | concurrency             |
| `RateLimiter`        | request pacing          |
| `RetryPolicy`        | retry decision          |
| `AsyncFetcher`       | orchestration           |

Đây chính là nền tảng để áp dụng SOLID.

---

# 38. Bài tập thực hành

## Bài 1 — 5 requests/second

Tạo:

```python
RateLimiter(5)
```

và 20 coroutine.

Đo thời gian giữa các request.

---

## Bài 2 — Semaphore + RateLimiter

Thiết lập:

```text
Semaphore = 3
Rate = 2 req/s
```

Tạo 10 task.

Quan sát:

```text
tốc độ ≈ 2 req/s
active HTTP ≤ 3
```

---

## Bài 3 — Retry

Giả lập:

```text
Attempt 1 → 500
Attempt 2 → 500
Attempt 3 → 200
```

Mỗi attempt phải đi qua:

```text
RateLimiter
```

Flow:

```text
Attempt 1
 ↓
RateLimiter
 ↓
HTTP
 ↓
500
 ↓
backoff

Attempt 2
 ↓
RateLimiter
 ↓
HTTP
 ↓
500
 ↓
backoff

Attempt 3
 ↓
RateLimiter
 ↓
HTTP
 ↓
200
```

---

# 39. Bài tập chính

Xây pipeline:

```text
URL
 ↓
RetryPolicy
 ↓
RateLimiter
 ↓
Semaphore
 ↓
ProxyPool
 ↓
BrowserProfilePool
 ↓
AsyncClient
```

Chưa cần tích hợp tất cả thành một class lớn.

Hãy giữ các component độc lập:

```text
RetryPolicy
RateLimiter
ProxyPool
BrowserProfilePool
```

để Buổi 39 chúng ta ghép chúng bằng architecture rõ ràng.

---

# 40. Tổng kết Buổi 38

Ba khái niệm phải nhớ tuyệt đối:

```text
Semaphore
    =
MAX CONCURRENT REQUESTS

RateLimiter
    =
REQUEST RATE

RetryPolicy
    =
RETRY BEHAVIOR
```

Ví dụ:

```text
Semaphore = 10
RateLimit = 2 req/s
MaxAttempts = 3
```

có nghĩa:

```text
                 ┌── tối đa 10 request active
                 │
                 ↓
Request ──────→ Semaphore
                 │
                 ↓
            RateLimiter
                 │
                 ↓
              HTTP
                 │
          ┌──────┴──────┐
          ↓             ↓
        success       failure
                          ↓
                     RetryPolicy
                          ↓
                       backoff
                          ↓
                    RateLimiter
                          ↓
                         HTTP
```

Và roadmap hiện tại:

```text
31. AsyncClient              ✅
32. async GET                ✅
33. Concurrent Requests      ✅
34. Semaphore                ✅
35. Timeout + Retry          ✅
36. Proxy Pool               ✅
37. Browser Profile Pool     ✅
38. Rate Limiting            ✅
39. Fetcher Architecture     ← tiếp theo
40. Async Novel Fetcher
```

**Buổi 39** sẽ là bước rất quan trọng: chúng ta sẽ ngừng ghép các component bằng một `AsyncFetcher` đơn giản và thiết kế **Fetcher Architecture theo DDD + SOLID**, gồm `Fetcher Interface`, `Request/Response`, `Retry`, `Proxy`, `Browser Profile`, `Rate Limiter`, error boundary và dependency injection — chuẩn bị trực tiếp cho **Buổi 40: Async Novel Fetcher**.
