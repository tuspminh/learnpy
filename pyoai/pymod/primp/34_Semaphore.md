# Buổi 34 — `asyncio.Semaphore`

Ở Buổi 33, chúng ta đã có:

```text
asyncio.gather()
        ↓
Concurrent Requests
```

Nhưng có một vấn đề:

```text
10.000 URLs
     ↓
10.000 coroutine
     ↓
gather()
```

Ta không muốn crawler **bắn toàn bộ request cùng lúc**.

Buổi 34 giải quyết chính xác bài toán đó:

```text
10.000 URLs
     ↓
Semaphore(10)
     ↓
chỉ tối đa 10 request
đang chạy đồng thời
```

`asyncio.Semaphore` duy trì một counter; `acquire()` giảm counter, `release()` tăng lại, và khi counter bằng 0 task mới phải chờ. Python khuyến nghị dùng Semaphore với `async with`. ([Python documentation][1])

`primp 2.0.1` hiện cung cấp `AsyncClient`, nên chúng ta vẫn giữ đúng kiến trúc đã học. ([PyPI][2])

---

# 1. Vấn đề của `gather()`

Buổi 33:

```python
responses = await asyncio.gather(
    *(client.get(url) for url in urls)
)
```

Nếu:

```python
urls = 100
```

thì có thể hình dung:

```text
100 URLs
   │
   ├── Request 1
   ├── Request 2
   ├── Request 3
   ├── ...
   └── Request 100
```

`gather()` chạy awaitables concurrently và trả kết quả theo thứ tự input. ([Python documentation][3])

Nhưng `gather()` **không phải concurrency limiter**.

Nó không nói:

```text
"chỉ cho phép 10 request"
```

Đó là nhiệm vụ của `Semaphore`.

---

# 2. Semaphore là gì?

Hãy tưởng tượng một phòng có:

```text
10 chiếc vé
```

Mỗi task muốn vào phòng phải lấy một vé.

```text
Semaphore(10)
```

Ban đầu:

```text
10 slots
```

Task 1 lấy:

```text
9 slots
```

Task 2:

```text
8 slots
```

...

Task 10:

```text
0 slots
```

Task 11:

```text
WAIT
```

Khi Task 1 hoàn thành:

```text
release()
```

thì:

```text
1 slot
```

được trả lại cho task đang chờ.

---

# 3. Ví dụ không dùng HTTP

Trước tiên hiểu Semaphore độc lập.

```python
import asyncio


async def worker(
    semaphore: asyncio.Semaphore,
    name: str,
):
    async with semaphore:

        print(f"{name}: START")

        await asyncio.sleep(2)

        print(f"{name}: END")


async def main():

    semaphore = asyncio.Semaphore(2)

    await asyncio.gather(
        worker(semaphore, "A"),
        worker(semaphore, "B"),
        worker(semaphore, "C"),
        worker(semaphore, "D"),
        worker(semaphore, "E"),
    )


if __name__ == "__main__":
    asyncio.run(main())
```

Ta đặt:

```python
asyncio.Semaphore(2)
```

nghĩa là:

> Tối đa 2 worker được chạy phần nằm trong `async with` cùng lúc.

---

# 4. Quan sát execution

Có thể thấy:

```text
A: START
B: START

A: END
B: END

C: START
D: START

C: END
D: END

E: START

E: END
```

Mặc dù chúng ta tạo:

```text
A B C D E
```

cùng lúc bằng `gather()`.

Nhưng Semaphore biến:

```text
5 concurrent tasks
```

thành:

```text
maximum 2 active workers
```

---

# 5. Cú pháp quan trọng nhất

Bạn cần nhớ:

```python
async with semaphore:
    ...
```

Nó tương đương về ý tưởng với:

```python
await semaphore.acquire()

try:
    ...
finally:
    semaphore.release()
```

Python documentation cũng khuyến nghị dạng `async with` vì việc `release()` được đảm bảo khi thoát khỏi context. ([Python documentation][1])

---

# 6. Tại sao phải `async with`?

Ví dụ:

```python
async with semaphore:

    response = await client.get(url)
```

Flow:

```text
Task
 ↓
acquire semaphore
 ↓
có slot?
 ├── YES → GET
 │          ↓
 │       response
 │          ↓
 │       release
 │
 └── NO
      ↓
     WAIT
      ↓
   có slot
      ↓
     GET
```

Đây chính là thứ chúng ta cần cho crawler.

---

# 7. Async HTTP + Semaphore

Bây giờ đưa `primp` vào.

```python
import asyncio

import primp


async def fetch_one(
    client: primp.AsyncClient,
    semaphore: asyncio.Semaphore,
    url: str,
):
    async with semaphore:

        print("GET:", url)

        response = await client.get(
            url,
            timeout=10,
        )

        print(
            "DONE:",
            response.status_code,
            url,
        )

        return response


async def main():

    urls = [
        f"https://httpbin.org/get?page={i}"
        for i in range(1, 11)
    ]

    semaphore = asyncio.Semaphore(3)

    async with primp.AsyncClient(
        impersonate="chrome_146",
        impersonate_os="windows",
    ) as client:

        responses = await asyncio.gather(
            *(
                fetch_one(
                    client,
                    semaphore,
                    url,
                )
                for url in urls
            )
        )

        print()
        print("Completed:", len(responses))


if __name__ == "__main__":
    asyncio.run(main())
```

---

# 8. Điều gì đang xảy ra?

Chúng ta có:

```text
10 URLs
```

nhưng:

```python
semaphore = asyncio.Semaphore(3)
```

nên:

```text
                    Semaphore(3)
                         │
              ┌──────────┼──────────┐
              ↓          ↓          ↓
            GET 1      GET 2      GET 3
              │          │          │
              └──────────┼──────────┘
                         ↓
                      slot free
                         ↓
                       GET 4
```

Không bao giờ có hơn 3 request đi qua vùng:

```python
async with semaphore:
```

cùng lúc.

---

# 9. Một điểm rất quan trọng: đặt Semaphore ở đâu?

Đúng:

```python
async def fetch_one(...):

    async with semaphore:

        response = await client.get(url)

    return response
```

Semaphore bao quanh **HTTP operation**.

Không nên:

```python
async with semaphore:

    parse_html()

    save_database()

    response = await client.get(url)
```

vì như vậy bạn đang giữ slot trong cả:

```text
HTTP
+
Parsing
+
Database
```

Trong khi mục tiêu của semaphore ở đây là giới hạn concurrency của HTTP fetch.

---

# 10. Phạm vi của Semaphore

Ta muốn:

```text
Semaphore
    ↓
HTTP requests
```

chứ không phải:

```text
Semaphore
    ↓
toàn bộ application
```

Do đó:

```python
class AsyncFetcher:
    def __init__(self, concurrency: int):
        self.semaphore = asyncio.Semaphore(concurrency)
```

là hướng thiết kế hợp lý.

---

# 11. Xây `AsyncFetcher`

Bây giờ bắt đầu tiến gần architecture thực tế.

```python
import asyncio

import primp


class AsyncFetcher:

    def __init__(
        self,
        client: primp.AsyncClient,
        concurrency: int = 10,
    ):
        self.client = client
        self.semaphore = asyncio.Semaphore(
            concurrency
        )

    async def get(
        self,
        url: str,
    ):
        async with self.semaphore:

            return await self.client.get(
                url,
                timeout=10,
            )
```

Sử dụng:

```python
async def main():

    async with primp.AsyncClient(
        impersonate="chrome_146",
        impersonate_os="windows",
    ) as client:

        fetcher = AsyncFetcher(
            client,
            concurrency=3,
        )

        response = await fetcher.get(
            "https://httpbin.org/get"
        )

        print(response.status_code)
```

---

# 12. `AsyncFetcher` với nhiều URLs

```python
import asyncio

import primp


class AsyncFetcher:

    def __init__(
        self,
        client: primp.AsyncClient,
        concurrency: int = 10,
    ):
        self.client = client
        self.semaphore = asyncio.Semaphore(
            concurrency
        )

    async def get(
        self,
        url: str,
    ):
        async with self.semaphore:

            return await self.client.get(
                url,
                timeout=10,
            )

    async def get_many(
        self,
        urls: list[str],
    ):
        return await asyncio.gather(
            *(self.get(url) for url in urls)
        )


async def main():

    urls = [
        f"https://httpbin.org/get?page={i}"
        for i in range(1, 11)
    ]

    async with primp.AsyncClient(
        impersonate="chrome_146",
        impersonate_os="windows",
    ) as client:

        fetcher = AsyncFetcher(
            client,
            concurrency=3,
        )

        responses = await fetcher.get_many(
            urls
        )

        for response in responses:
            print(
                response.status_code,
                response.url,
            )


if __name__ == "__main__":
    asyncio.run(main())
```

Đây là cấu trúc rất đáng nhớ:

```text
get_many()
    ↓
gather()
    ↓
get()
    ↓
Semaphore
    ↓
AsyncClient
    ↓
HTTP
```

---

# 13. `gather()` + `Semaphore`

Đây là hai thứ **không cạnh tranh nhau**.

Chúng giải quyết hai vấn đề khác nhau:

### `gather()`

```text
Làm nhiều coroutine concurrently
```

### `Semaphore`

```text
Giới hạn bao nhiêu coroutine
được vào vùng critical section cùng lúc
```

Kết hợp:

```text
                 gather()
                    ↓
             100 coroutine
                    ↓
             Semaphore(10)
                    ↓
          ┌─────────┴─────────┐
          ↓                   ↓
       tối đa 10           90 đang chờ
       HTTP request
```

Đây là pattern rất phổ biến trong async crawler.

---

# 14. Vì sao không chỉ dùng `Semaphore(1)`?

Nếu:

```python
semaphore = asyncio.Semaphore(1)
```

thì:

```text
GET 1
 ↓
GET 2
 ↓
GET 3
 ↓
GET 4
```

gần như trở thành sequential.

Tức:

```text
Semaphore(1)
    ↓
không concurrency
```

Còn:

```text
Semaphore(10)
    ↓
10 concurrent requests
```

---

# 15. Chọn concurrency bao nhiêu?

Không có con số universal.

Ví dụ:

```text
1
3
5
10
20
50
```

đều có thể hợp lý tùy:

* website;
* latency;
* server capacity;
* network;
* proxy;
* crawler workload;
* rate limit;
* số connection;
* yêu cầu của website.

Không nên mặc định:

```text
"100 là nhanh hơn 10"
```

Vì có thể xảy ra:

```text
concurrency tăng
      ↓
server throttling
      ↓
timeout tăng
      ↓
error tăng
      ↓
throughput thực tế giảm
```

---

# 16. Semaphore không phải Rate Limiter

Đây là điểm **cực kỳ quan trọng**.

Giả sử:

```python
Semaphore(10)
```

nó có nghĩa:

> Tối đa 10 request đang active cùng lúc.

Nó **không có nghĩa**:

> Chỉ được gửi 10 request mỗi giây.

Hai khái niệm khác nhau.

### Concurrency

```text
10 request đang chạy
```

### Rate

```text
10 request / second
```

Ví dụ:

```text
Concurrency = 10
Rate = 2 req/s
```

hoàn toàn có thể tồn tại cùng nhau.

Rate Limiting sẽ học ở **Buổi 38**.

---

# 17. Semaphore cũng không phải Connection Pool

Một `Semaphore(10)` không có nghĩa:

```text
10 TCP connections
```

Nó chỉ kiểm soát:

```text
10 coroutine
```

được phép vào vùng code bảo vệ bởi semaphore.

Việc quản lý connection thuộc HTTP client/transport.

Trong kiến trúc của chúng ta:

```text
Semaphore
    ↓
Application/Fetcher concurrency policy

primp.AsyncClient
    ↓
HTTP client / connection handling
```

Không trộn hai trách nhiệm này.

---

# 18. Kiểm chứng concurrency

Ta có thể tạo counter:

```python
import asyncio


active = 0
maximum = 0


async def worker(
    semaphore: asyncio.Semaphore,
    name: str,
):
    global active, maximum

    async with semaphore:

        active += 1
        maximum = max(maximum, active)

        print(
            f"{name}: active={active}"
        )

        await asyncio.sleep(1)

        active -= 1


async def main():

    semaphore = asyncio.Semaphore(3)

    await asyncio.gather(
        *(
            worker(
                semaphore,
                f"task-{i}",
            )
            for i in range(10)
        )
    )

    print(
        "Maximum concurrency:",
        maximum,
    )


if __name__ == "__main__":
    asyncio.run(main())
```

Kết quả cuối phải cho thấy:

```text
Maximum concurrency: 3
```

Đây là một bài test rất tốt để hiểu Semaphore.

---

# 19. Cách viết tốt hơn, tránh `global`

Trong code production, không nên dùng global counter.

Ta có thể tạo class:

```python
import asyncio


class ConcurrencyTracker:

    def __init__(self):
        self.active = 0
        self.maximum = 0

    def started(self):
        self.active += 1

        self.maximum = max(
            self.maximum,
            self.active,
        )

    def finished(self):
        self.active -= 1
```

Worker:

```python
async def worker(
    semaphore,
    tracker,
    name,
):
    async with semaphore:

        tracker.started()

        try:
            print(
                name,
                tracker.active,
            )

            await asyncio.sleep(1)

        finally:
            tracker.finished()
```

Ở đây chúng ta cũng học được một pattern quan trọng:

```python
try:
    ...
finally:
    ...
```

để đảm bảo cleanup.

---

# 20. Tại sao `async with semaphore` an toàn hơn manual `acquire()`?

Nếu bạn viết:

```python
await semaphore.acquire()

response = await client.get(url)

semaphore.release()
```

và request phát sinh exception:

```text
acquire
 ↓
GET
 ↓
Exception
 ↓
release không chạy
```

Semaphore có thể bị giữ slot.

Đó là lý do tốt hơn:

```python
async with semaphore:

    response = await client.get(url)
```

Python documentation mô tả `async with` là cách preferred để sử dụng Semaphore. ([Python documentation][1])

---

# 21. Nếu request lỗi thì sao?

Ví dụ:

```python
async def get(self, url):

    async with self.semaphore:

        return await self.client.get(url)
```

Nếu:

```python
await self.client.get(url)
```

ném exception:

```text
GET
 ↓
Exception
 ↓
thoát async with
 ↓
Semaphore release
```

Đó là một ưu điểm rất quan trọng.

Sau đó exception có thể được xử lý ở tầng trên.

---

# 22. Kết hợp `return_exceptions=True`

Trong crawler:

```python
async def get_many(
    self,
    urls: list[str],
):
    return await asyncio.gather(
        *(self.get(url) for url in urls),
        return_exceptions=True,
    )
```

Sau đó:

```python
results = await fetcher.get_many(urls)

for url, result in zip(urls, results):

    if isinstance(result, Exception):

        print(
            "FAILED:",
            url,
            type(result).__name__,
        )

    else:

        print(
            "OK:",
            url,
            result.status_code,
        )
```

`gather(..., return_exceptions=True)` đưa exception vào danh sách kết quả thay vì lập tức propagate nó. ([Python documentation][3])

Điều này đặc biệt hữu ích khi crawl hàng nghìn chapter.

---

# 23. Nhưng đừng nuốt exception

Không nên:

```python
except Exception:
    return None
```

rồi bỏ qua.

Vì sau này chúng ta cần biết:

```text
Timeout
ConnectionError
SSL Error
HTTP 500
HTTP 429
HTTP 404
```

để áp dụng policy khác nhau.

Đó là lý do roadmap có:

```text
35. Timeout + Retry
48. Error Classification
```

---

# 24. Semaphore trong Novel Crawler

Hãy hình dung:

```text
Novel
 ├── Chapter 1
 ├── Chapter 2
 ├── Chapter 3
 ├── ...
 └── Chapter 500
```

Parser tạo:

```python
chapter_urls = [...]
```

Application:

```python
responses = await fetcher.get_many(
    chapter_urls
)
```

Fetcher:

```text
get_many()
    ↓
gather()
    ↓
get()
    ↓
Semaphore(10)
    ↓
primp.AsyncClient
```

Kết quả:

```text
500 chapters
      ↓
max 10 HTTP requests
      ↓
responses
      ↓
Parser
```

---

# 25. Kiến trúc hiện tại

Sau Buổi 34:

```text
                    Application
                         │
                         ↓
                  AsyncNovelFetcher
                         │
                         ↓
                    get_many()
                         │
                         ↓
                  asyncio.gather()
                         │
             ┌───────────┼───────────┐
             ↓           ↓           ↓
           get()       get()       get()
             │           │           │
             └───────────┼───────────┘
                         ↓
                  asyncio.Semaphore
                         │
                  max concurrency
                         │
                         ↓
                primp.AsyncClient
                         │
                         ↓
                        HTTP
```

---

# 26. Tách `ConcurrencyConfig`

Khi project lớn hơn, không nên hard-code:

```python
asyncio.Semaphore(10)
```

ở nhiều nơi.

Có thể:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ConcurrencyConfig:
    max_concurrency: int = 10
```

Sau đó:

```python
class AsyncFetcher:

    def __init__(
        self,
        client,
        config: ConcurrencyConfig,
    ):
        self.client = client

        self.semaphore = asyncio.Semaphore(
            config.max_concurrency
        )
```

Configuration:

```python
config = ConcurrencyConfig(
    max_concurrency=10
)
```

---

# 27. Nhưng đừng abstraction quá sớm

Không cần ngay lập tức tạo:

```text
ConcurrencyManager
ConcurrencyPolicy
ConcurrencyStrategy
ConcurrencyFactory
ConcurrencyProvider
ConcurrencyRegistry
```

😄

Hiện tại chỉ cần:

```text
ConcurrencyConfig
        ↓
Semaphore
        ↓
AsyncFetcher
```

là đủ.

Đây phù hợp với nguyên tắc chúng ta đã dùng xuyên suốt project:

> **Abstraction khi có responsibility thực sự, không tạo class chỉ vì SOLID.**

---

# 28. Một thiết kế hoàn chỉnh hơn

Đây là phiên bản tôi khuyên bạn giữ lại làm nền cho các buổi sau:

```python
import asyncio
from dataclasses import dataclass

import primp


@dataclass(frozen=True)
class ConcurrencyConfig:
    max_concurrency: int = 10


class AsyncFetcher:

    def __init__(
        self,
        client: primp.AsyncClient,
        config: ConcurrencyConfig,
    ):
        self.client = client

        self.semaphore = asyncio.Semaphore(
            config.max_concurrency
        )

    async def get(
        self,
        url: str,
    ):
        async with self.semaphore:

            return await self.client.get(
                url,
                timeout=10,
            )

    async def get_many(
        self,
        urls: list[str],
    ):
        return await asyncio.gather(
            *(self.get(url) for url in urls),
            return_exceptions=True,
        )


async def main():

    config = ConcurrencyConfig(
        max_concurrency=3
    )

    urls = [
        f"https://httpbin.org/get?page={i}"
        for i in range(1, 11)
    ]

    async with primp.AsyncClient(
        impersonate="chrome_146",
        impersonate_os="windows",
    ) as client:

        fetcher = AsyncFetcher(
            client,
            config,
        )

        results = await fetcher.get_many(
            urls
        )

        for url, result in zip(
            urls,
            results,
        ):

            if isinstance(result, Exception):

                print(
                    "FAILED:",
                    url,
                    type(result).__name__,
                )

            else:

                print(
                    "OK:",
                    result.status_code,
                    result.url,
                )


if __name__ == "__main__":
    asyncio.run(main())
```

Đây là code bạn có thể dùng làm **checkpoint sau Buổi 34**.

---

# 29. Một vấn đề mới xuất hiện

Bây giờ chúng ta đã có:

```text
gather()
+
Semaphore
```

Nhưng vẫn còn một vấn đề:

```text
Request
   ↓
timeout?
   ↓
failed?
   ↓
retry?
```

Ví dụ:

```text
Chapter 101
    ↓
timeout
    ↓
Retry #1
    ↓
timeout
    ↓
Retry #2
    ↓
success
```

Nhưng:

```text
404
```

thì có nên retry không?

Có thể không.

```text
429
```

thì cần xử lý khác.

```text
500
```

lại khác.

Đây là lý do **Buổi 35 — Timeout + Retry** sẽ không chỉ là:

```python
for _ in range(3):
    try:
        ...
```

mà chúng ta sẽ bắt đầu xây **Retry Policy** đúng kiến trúc.

---

# 30. Phân biệt 4 khái niệm

Sau Buổi 34, bạn cần phân biệt thật chắc:

| Khái niệm    | Ý nghĩa                              |
| ------------ | ------------------------------------ |
| `async`      | Code có thể hoạt động với event loop |
| `gather()`   | Chạy nhiều awaitable concurrently    |
| `Semaphore`  | Giới hạn số operation đồng thời      |
| Rate Limiter | Giới hạn tốc độ request              |

Ví dụ:

```text
500 URLs
   ↓
gather()
   ↓
500 tasks
   ↓
Semaphore(10)
   ↓
10 HTTP requests active
   ↓
Rate Limiter
   ↓
ví dụ kiểm soát tốc độ gửi request
```

**Semaphore không thay thế Rate Limiter.**

---

# 31. Bài tập thực hành

### Bài 1

Tạo:

```python
semaphore = asyncio.Semaphore(3)
```

và 10 worker.

Chứng minh:

```text
maximum concurrent = 3
```

---

### Bài 2

Viết:

```python
async def fetch_many(
    client,
    urls,
    max_concurrency=5,
):
    ...
```

Yêu cầu:

```text
✓ AsyncClient dùng chung
✓ asyncio.gather()
✓ Semaphore
✓ tối đa 5 request
✓ kết quả giữ đúng thứ tự URL
✓ không retry
```

---

### Bài 3 — quan trọng

Thử:

```text
max_concurrency = 1
max_concurrency = 2
max_concurrency = 5
max_concurrency = 10
```

và quan sát:

```text
thời gian
+
maximum active requests
```

---

### Bài 4 — Novel Crawler

Giả sử parser trả:

```python
chapter_urls = [
    ".../chuong-1",
    ".../chuong-2",
    ...
]
```

Xây:

```text
AsyncNovelFetcher
        ↓
get_many()
        ↓
Semaphore(10)
        ↓
primp.AsyncClient
```

**Không đưa Parser vào Fetcher.**

---

# 32. Tổng kết Buổi 34

Ta đã đi từ:

```text
Buổi 31
AsyncClient
```

→

```text
Buổi 32
async GET
```

→

```text
Buổi 33
gather()
```

→

```text
Buổi 34
Semaphore
```

Architecture:

```text
                  AsyncNovelFetcher
                         │
                         ↓
                  asyncio.gather()
                         │
             ┌───────────┼───────────┐
             ↓           ↓           ↓
           task        task        task
             │           │           │
             └───────────┼───────────┘
                         ↓
                asyncio.Semaphore(10)
                         │
                    max 10 active
                         │
                         ↓
                primp.AsyncClient
                         │
                         ↓
                       HTTP
```

Và roadmap tiếp tục rất tự nhiên:

```text
31. AsyncClient             ✅
32. async GET               ✅
33. Concurrent Requests     ✅
34. Semaphore               ✅
35. Timeout + Retry         ← tiếp theo
36. Proxy Pool
37. User-Agent / Browser Profile Pool
38. Rate Limiting
39. Fetcher Architecture
40. Async Novel Fetcher
```

Điểm quan trọng nhất của Buổi 34 là:

> **`gather()` tạo concurrency; `Semaphore` kiểm soát concurrency.**

Đó là nền tảng để sau này chúng ta xây crawler có hàng nghìn chapter nhưng vẫn kiểm soát được tải lên website.

[1]: https://docs.python.org/3.12/library/asyncio-sync.html?utm_source=chatgpt.com "Synchronization Primitives — Python 3.12.14 documentation"
[2]: https://pypi.org/project/primp/2.0.1/?utm_source=chatgpt.com "primp · PyPI"
[3]: https://docs.python.org/3/library/asyncio-task.html?utm_source=chatgpt.com "Coroutines and tasks — Python 3.14.7 documentation"
