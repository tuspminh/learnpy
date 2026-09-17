# Buổi 31 — `AsyncClient`

Hôm nay chúng ta bắt đầu **Phần IV — Async + Crawler**.

Sau Buổi 30, ta có:

```text
BrowserProfile
      ↓
BrowserClient
      ↓
primp.Client
      ↓
HTTP
```

Bây giờ chuyển sang:

```text
BrowserProfile
      ↓
AsyncBrowserClient
      ↓
primp.AsyncClient
      ↓
HTTP
```

`primp 2.0.1` hiện có `AsyncClient` chính thức và PyPI cung cấp ví dụ sử dụng `async with primp.AsyncClient(...)`. Thư viện yêu cầu Python >= 3.10. ([PyPI][1])

---

# 1. Async là gì?

Trước tiên cần phân biệt:

```text
Synchronous
```

với:

```text
Asynchronous
```

## Sync

```python
response1 = client.get(url1)
response2 = client.get(url2)
response3 = client.get(url3)
```

Luồng thực thi:

```text
request 1
   │
   ├────── waiting ──────┐
   │                     │
   ↓                     ↓
response 1          request 2
                         │
                         ├──── waiting ────┐
                         ↓                 │
                    response 2             │
                                           ↓
                                      request 3
```

Nếu server mất 3 giây:

```text
3 request × 3 giây
≈ 9 giây
```

---

# 2. Async

Async cho phép trong lúc request đang **chờ I/O**, event loop chuyển sang công việc khác.

```text
request 1
    │
    ├── waiting ──────────────┐
    │                         │
    │                     request 2
    │                         │
    │                         ├── waiting ───────┐
    │                         │                  │
    │                     request 3              │
    │                         │                  │
    └──────── response 1 ←────┘                  │
                                               response 2
```

Nếu ba request mỗi request mất khoảng 3 giây và chạy đồng thời:

```text
≈ 3 giây
```

thay vì:

```text
≈ 9 giây
```

**Nhưng đây chỉ là mô hình đơn giản.** Thực tế còn phụ thuộc connection, server, DNS, TCP/TLS, giới hạn concurrency, rate limit...

---

# 3. Async không phải Thread

Đây là điều rất quan trọng.

```text
Async
   ↓
Event Loop
   ↓
Cooperative concurrency
```

Không nhất thiết tạo:

```text
Thread 1
Thread 2
Thread 3
```

Với crawler I/O-bound:

```text
HTTP request
      ↓
waiting for network
      ↓
event loop làm việc khác
```

Async đặc biệt phù hợp với crawler vì phần lớn thời gian crawler:

```text
CPU        → thấp
Network    → chờ nhiều
```

---

# 4. `primp.AsyncClient`

API hiện tại:

```python
import primp

async with primp.AsyncClient(
    impersonate="chrome_146"
) as client:

    response = await client.get(url)
```

Đây là ví dụ async chính thức trên PyPI của `primp`. ([PyPI][1])

Điểm mới:

```text
await
```

và:

```text
async with
```

---

# 5. Chương trình Async đầu tiên

Tạo:

```text
lesson31/
└── 01_async_get.py
```

Code:

```python
import asyncio

import primp


async def main():
    async with primp.AsyncClient(
        impersonate="chrome_146",
        impersonate_os="windows",
    ) as client:

        response = await client.get(
            "https://httpbin.org/get"
        )

        print("Status:", response.status_code)
        print("URL:", response.url)
        print()
        print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
```

Chạy:

```bash
python 01_async_get.py
```

---

# 6. Phân tích từng dòng

## `async def`

```python
async def main():
```

Tạo một coroutine function.

Nó chưa chạy ngay khi gọi:

```python
main()
```

mà tạo coroutine object.

Để chạy:

```python
asyncio.run(main())
```

---

# 7. `asyncio.run()`

```python
asyncio.run(main())
```

Có thể hình dung:

```text
asyncio.run()
      │
      ↓
 Event Loop
      │
      ↓
   main()
      │
      ↓
 async operations
```

Trong chương trình CLI đơn giản, đây là cách phổ biến để khởi động async application.

---

# 8. `async with`

```python
async with primp.AsyncClient(...) as client:
```

Có nghĩa:

```text
Create AsyncClient
       ↓
Use AsyncClient
       ↓
Cleanup
```

Đây là lifecycle rất quan trọng.

Không nên nghĩ:

```python
client = primp.AsyncClient()
```

rồi bỏ mặc client suốt chương trình.

Dùng context manager giúp lifecycle rõ ràng.

PyPI hiện minh họa chính xác cách dùng này với `AsyncClient`. ([PyPI][1])

---

# 9. `await`

Dòng:

```python
response = await client.get(url)
```

có nghĩa:

> Chờ coroutine `get()` hoàn thành, nhưng trong thời gian chờ event loop có thể chạy coroutine khác.

Đây là khác biệt quan trọng với:

```python
response = client.get(url)
```

của sync client.

---

# 10. `await` không có nghĩa "chặn toàn bộ chương trình"

Ví dụ:

```python
async def download():
    response = await client.get(url)
```

Trong lúc:

```text
client.get()
```

đang chờ network:

```text
Event Loop
   │
   ├── download A → waiting
   │
   ├── download B → running
   │
   ├── download C → running
   │
   └── other task
```

Đây là nền tảng của concurrency.

---

# 11. `AsyncClient` cũng nên được reuse

Một sai lầm:

```python
async def fetch(url):
    async with primp.AsyncClient() as client:
        return await client.get(url)
```

Nếu gọi:

```python
await fetch(url1)
await fetch(url2)
await fetch(url3)
```

ta tạo nhiều client.

Không tốt.

Thay vào đó:

```text
Application
     │
     ↓
AsyncFetcher
     │
     ↓
one AsyncClient
     │
     ├── request 1
     ├── request 2
     ├── request 3
     └── request 4
```

Tài liệu Rust underlying của `primp` cũng mô tả `Client` có connection pool và khuyến nghị tạo một client rồi reuse để tránh overhead. ([Docs.rs][2])

---

# 12. Sai lầm thường gặp

Không nên:

```python
async def fetch(url):
    client = primp.AsyncClient()

    response = await client.get(url)

    return response
```

Vì:

```text
request
 ↓
new client
 ↓
request
 ↓
client bỏ đó
```

Thay vào đó:

```python
async def fetch_all():

    async with primp.AsyncClient() as client:

        response1 = await client.get(url1)
        response2 = await client.get(url2)
        response3 = await client.get(url3)
```

---

# 13. Async BrowserClient

Ở Buổi 30 chúng ta có:

```python
class BrowserClient:
    ...
```

Bây giờ xây:

```python
class AsyncBrowserClient:
    ...
```

Tạo:

```text
lesson31/
└── async_browser_client.py
```

```python
import primp

from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserProfile:
    impersonate: str
    os: str | None = None


class AsyncBrowserClient:

    def __init__(
        self,
        profile: BrowserProfile,
    ):
        self.profile = profile

        self.client = primp.AsyncClient(
            impersonate=profile.impersonate,
            impersonate_os=profile.os,
        )

    async def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict | None = None,
        timeout: float | None = None,
    ):
        return await self.client.get(
            url,
            headers=headers,
            params=params,
            timeout=timeout,
        )

    async def close(self):
        await self.client.aclose()
```

---

# 14. Nhưng có nên tự `close()` không?

Ở version hiện tại, cách rõ ràng nhất là dùng lifecycle:

```python
async with ...
```

Thay vì phụ thuộc vào việc nhớ:

```python
await client.close()
```

Ta có thể xây context manager cho `AsyncBrowserClient`.

---

# 15. AsyncBrowserClient hoàn chỉnh

```python
import primp

from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserProfile:
    impersonate: str
    os: str | None = None


class AsyncBrowserClient:

    def __init__(
        self,
        profile: BrowserProfile,
    ):
        self.profile = profile
        self.client = primp.AsyncClient(
            impersonate=profile.impersonate,
            impersonate_os=profile.os,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        await self.client.aclose()

    async def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict | None = None,
        timeout: float | None = None,
    ):
        return await self.client.get(
            url,
            headers=headers,
            params=params,
            timeout=timeout,
        )
```

Sau đó:

```python
async with AsyncBrowserClient(profile) as client:

    response = await client.get(url)
```

---

# 16. Nhưng hãy kiểm tra API hiện tại

Với thư viện thay đổi nhanh như `primp`, không nên tự suy đoán method lifecycle.

PyPI hiện có ví dụ:

```python
async with primp.AsyncClient(...) as client:
```

nên context-manager API là cách chúng ta ưu tiên trong khóa học. ([PyPI][1])

Phần `aclose()` nên xem là implementation detail cần xác nhận theo version đang cài, thay vì thiết kế architecture dựa trên một method chưa kiểm chứng.

---

# 17. Test AsyncBrowserClient

```python
import asyncio

from async_browser_client import (
    AsyncBrowserClient,
    BrowserProfile,
)


async def main():

    profile = BrowserProfile(
        impersonate="chrome_146",
        os="windows",
    )

    async with AsyncBrowserClient(profile) as client:

        response = await client.get(
            "https://httpbin.org/get"
        )

        print("Status:", response.status_code)
        print("URL:", response.url)
        print()
        print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
```

---

# 18. Async chưa tạo ra concurrency

Đây là điểm rất quan trọng.

Code:

```python
response1 = await client.get(url1)
response2 = await client.get(url2)
response3 = await client.get(url3)
```

vẫn chạy:

```text
url1
 ↓
wait
 ↓
response1

url2
 ↓
wait
 ↓
response2

url3
 ↓
wait
 ↓
response3
```

Đây là:

```text
async
```

nhưng **chưa phải concurrent requests**.

Concurrency sẽ là **Buổi 33**.

---

# 19. So sánh

## Sync

```python
response = client.get(url)
```

## Async

```python
response = await client.get(url)
```

Nhưng:

```python
await client.get(url1)
await client.get(url2)
await client.get(url3)
```

vẫn tuần tự.

Muốn:

```text
url1 ────────┐
url2 ────────┤
url3 ────────┤
             ↓
          concurrently
```

ta sẽ học:

```text
Buổi 33 — Concurrent Requests
```

---

# 20. `asyncio.gather()`

Chúng ta chỉ preview một chút.

```python
results = await asyncio.gather(
    client.get(url1),
    client.get(url2),
    client.get(url3),
)
```

Khi đó:

```text
              ┌── get(url1)
              │
gather() ─────┼── get(url2)
              │
              └── get(url3)
```

Đây chính là nội dung Buổi 33.

**Chưa cần dùng sâu hôm nay.**

---

# 21. Ví dụ Novel Crawler

Giả sử có:

```text
Novel
 ├── Chapter 1
 ├── Chapter 2
 ├── Chapter 3
 ├── Chapter 4
 └── Chapter 5
```

Sync:

```text
Chapter 1 → wait
Chapter 2 → wait
Chapter 3 → wait
Chapter 4 → wait
Chapter 5 → wait
```

Async:

```text
Task 1 ──────────────┐
Task 2 ──────────────┤
Task 3 ──────────────┤
Task 4 ──────────────┤
Task 5 ──────────────┘
```

Nhưng:

```text
Async
```

không có nghĩa:

```text
1000 requests cùng lúc
```

Đó là lý do sau này chúng ta cần:

```text
Semaphore
Rate Limiter
Retry
Proxy Pool
```

---

# 22. Connection Pool

Đây là lý do `AsyncClient` nên sống lâu.

```text
AsyncClient
     │
     ↓
Connection Pool
     │
 ┌───┼────┬────┐
 ↓   ↓    ↓    ↓
 C1  C2   C3   C4
```

Nhiều request có thể reuse connection phù hợp thay vì mỗi request phải bắt đầu toàn bộ:

```text
DNS
 ↓
TCP
 ↓
TLS
 ↓
HTTP
```

Tài liệu `primp` mô tả `Client` giữ connection pool nội bộ để tái sử dụng connection và giảm overhead. ([Docs.rs][2])

---

# 23. Async + Browser Impersonation

Đây là điểm rất thú vị của project.

Ta không mất browser impersonation khi chuyển async:

```text
Sync
─────────────────────
BrowserProfile
      ↓
primp.Client
      ↓
HTTP


Async
─────────────────────
BrowserProfile
      ↓
primp.AsyncClient
      ↓
HTTP
```

Vẫn giữ:

```text
Browser
Version
OS
TLS
HTTP/2
Headers
```

Chỉ thay:

```text
Client
```

bằng:

```text
AsyncClient
```

---

# 24. Kiến trúc sau Buổi 31

```text
                    Fetcher
                       │
              ┌────────┴────────┐
              │                 │
              ↓                 ↓
        Sync Fetcher       Async Fetcher
              │                 │
              ↓                 ↓
       BrowserClient     AsyncBrowserClient
              │                 │
              ↓                 ↓
        primp.Client      primp.AsyncClient
              │                 │
              └────────┬────────┘
                       ↓
                    Network
```

Đây là một kiến trúc rất đẹp:

```text
Application
     │
     ↓
Fetcher abstraction
     │
     ├── Sync implementation
     └── Async implementation
```

---

# 25. Đừng đưa `asyncio` vào Domain

Ví dụ không nên:

```python
class Chapter:

    async def crawl(self):
        ...
```

Domain Entity không nên biết:

```text
asyncio
primp
httpx
TCP
TLS
```

Thay vào đó:

```text
Domain
  ↓
Chapter


Application
  ↓
CrawlChapter


Infrastructure
  ↓
AsyncBrowserClient
  ↓
primp.AsyncClient
```

---

# 26. Async Use Case

Ví dụ:

```python
class CrawlChapter:

    def __init__(self, fetcher):
        self.fetcher = fetcher

    async def execute(self, url: str):

        response = await self.fetcher.get(url)

        return response.text
```

Ở đây Use Case biết:

```text
await fetcher.get()
```

nhưng không biết:

```text
primp.AsyncClient
```

Đây là abstraction đúng.

---

# 27. Fake Async Fetcher để test

Async architecture cũng cần test.

```python
class FakeAsyncFetcher:

    def __init__(self, content: str):
        self.content = content

    async def get(self, url: str):
        return FakeResponse(self.content)
```

Ví dụ:

```python
class FakeResponse:

    def __init__(self, text: str):
        self.text = text
        self.status_code = 200
```

Test:

```python
import asyncio


async def test():

    fetcher = FakeAsyncFetcher(
        "<html>Hello</html>"
    )

    response = await fetcher.get(
        "https://example.com"
    )

    assert response.status_code == 200
    assert response.text == "<html>Hello</html>"


asyncio.run(test())
```

Không cần Internet.

Đây là cách architecture giúp test dễ hơn.

---

# 28. Một điểm rất quan trọng: async không tự làm CPU nhanh hơn

Ví dụ:

```python
async def parse_big_document():
    for i in range(100_000_000):
        ...
```

Async không tự biến CPU-bound task thành nhanh hơn.

Async phù hợp nhất với:

```text
I/O-bound
```

Ví dụ:

```text
HTTP
Database async driver
Socket
File I/O
Network
```

Novel crawler:

```text
HTTP
   ↓
async
```

rất phù hợp.

Nhưng:

```text
HTML parsing cực nặng
OCR
image processing
CPU computation
```

có thể cần:

```text
ProcessPool
ThreadPool
native code
```

tùy workload.

---

# 29. Một crawler async cơ bản

Chúng ta có thể viết:

```python
import asyncio

import primp


async def fetch_chapter(
    client,
    url: str,
):
    response = await client.get(url)

    return {
        "url": str(response.url),
        "status": response.status_code,
        "text": response.text,
    }


async def main():

    urls = [
        "https://httpbin.org/get?page=1",
        "https://httpbin.org/get?page=2",
        "https://httpbin.org/get?page=3",
    ]

    async with primp.AsyncClient(
        impersonate="chrome_146",
        impersonate_os="windows",
    ) as client:

        for url in urls:

            result = await fetch_chapter(
                client,
                url,
            )

            print(
                result["status"],
                result["url"],
            )


if __name__ == "__main__":
    asyncio.run(main())
```

Chú ý:

**Đây vẫn là tuần tự.**

Chúng ta cố tình viết như vậy để hiểu lifecycle trước.

---

# 30. Lifecycle đúng của crawler

Một crawler async nên có lifecycle kiểu:

```text
Application start
       │
       ↓
Create AsyncClient
       │
       ↓
Create Fetcher
       │
       ↓
Discover chapters
       │
       ↓
Fetch chapters
       │
       ↓
Parse
       │
       ↓
Save
       │
       ↓
Shutdown
       │
       ↓
Close AsyncClient
```

Không phải:

```text
Chapter 1
   ↓
create client
   ↓
destroy client

Chapter 2
   ↓
create client
   ↓
destroy client
```

---

# 31. Tư duy quan trọng nhất của Buổi 31

Đừng nghĩ:

```text
AsyncClient = client nhanh hơn
```

Mà:

```text
AsyncClient
    ↓
non-blocking I/O
    ↓
event loop
    ↓
nhiều I/O operations có thể tiến hành đồng thời
```

Sau đó mới có:

```text
AsyncClient
    +
Concurrent Requests
    +
Semaphore
    +
Retry
    +
Rate Limiting
```

để trở thành crawler thực tế.

---

# 32. Bài tập thực hành

### Bài 1

Chạy:

```python
async with primp.AsyncClient(
    impersonate="chrome_146",
    impersonate_os="windows",
) as client:
```

và gọi:

```text
https://httpbin.org/get
```

---

### Bài 2

Gọi:

```text
https://tls.peet.ws/api/all
```

và kiểm tra browser impersonation vẫn hoạt động trong async.

---

### Bài 3

Tạo:

```text
AsyncBrowserClient
```

với:

```python
async def get(...)
```

---

### Bài 4

Viết:

```text
FakeAsyncFetcher
```

để test Use Case mà không cần Internet.

---

### Bài 5

Viết:

```python
async def fetch_one(client, url):
    ...
```

và chạy tuần tự:

```python
for url in urls:
    await fetch_one(client, url)
```

**Chưa dùng `gather()`**. Buổi 33 chúng ta sẽ biến chính đoạn code này thành concurrent crawler.

---

# 33. Kiến trúc cuối Buổi 31

```text
                    Novel Crawler
                         │
                         ↓
                    Application
                         │
                         ↓
                  Async Fetcher
                         │
                         ↓
               AsyncBrowserClient
                         │
                 ┌───────┴────────┐
                 ↓                ↓
          BrowserProfile     RequestOptions
                 │
                 ↓
        primp.AsyncClient
                 │
          ┌──────┼──────┐
          ↓      ↓      ↓
         TLS   HTTP/2 Headers
                 │
                 ↓
              Network
```

Và phần IV của chúng ta sẽ phát triển chính xác theo chuỗi:

```text
31. AsyncClient             ← HÔM NAY ✅
        ↓
32. async GET
        ↓
33. Concurrent Requests
        ↓
34. Semaphore
        ↓
35. Timeout + Retry
        ↓
36. Proxy Pool
        ↓
37. Browser Profile Pool
        ↓
38. Rate Limiting
        ↓
39. Fetcher Architecture
        ↓
40. Async Novel Fetcher
```

**Điểm cần nhớ:** hôm nay chúng ta mới xây nền async và lifecycle. `async` một mình chưa tạo concurrency; sang **Buổi 32**, chúng ta sẽ đi sâu vào `async GET`, `await`, response handling, timeout và cách chuyển `BrowserClient` của Buổi 30 thành `AsyncBrowserClient` hoàn chỉnh trước khi bắt đầu concurrent requests.

[1]: https://pypi.org/project/primp/2.0.1/?utm_source=chatgpt.com "primp · PyPI"
[2]: https://docs.rs/primp/latest/primp/struct.Client.html?utm_source=chatgpt.com "Client in primp - Rust"
