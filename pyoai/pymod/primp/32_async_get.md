# Buổi 32 — `async GET`

Ở Buổi 31, chúng ta đã biết:

```text
primp.Client
      ↓
sync GET

primp.AsyncClient
      ↓
async GET
```

Hôm nay đi sâu vào **cách viết async GET đúng**, đặc biệt trong bối cảnh Novel Crawler.

Mục tiêu cuối buổi:

```text
AsyncBrowserClient
        ↓
async get()
        ↓
await client.get()
        ↓
Response
        ↓
text / json / headers / status
```

---

# 1. GET sync và async

Sync:

```python
response = client.get(url)
```

Async:

```python
response = await client.get(url)
```

Sự khác biệt quan trọng nhất là:

```python
await
```

`primp` hiện cung cấp `AsyncClient`, và tài liệu chính thức minh họa việc gọi:

```python
async with primp.AsyncClient(...) as client:
    response = await client.get(...)
```

---

# 2. Chương trình đầu tiên

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
python main.py
```

---

# 3. `async def`

```python
async def main():
```

Đây là coroutine function.

Ví dụ:

```python
async def hello():
    print("Hello")
```

Khi gọi:

```python
hello()
```

không có nghĩa là function đã thực sự chạy như function sync thông thường. Nó tạo coroutine.

Muốn thực thi:

```python
asyncio.run(hello())
```

---

# 4. `await client.get()`

Đây là dòng quan trọng nhất:

```python
response = await client.get(url)
```

Có thể đọc như:

> Thực hiện HTTP GET bất đồng bộ và chờ kết quả.

Trong thời gian operation đang chờ I/O, event loop có thể chuyển sang coroutine khác.

```text
Coroutine A
    │
    ├── HTTP GET
    │
    └── waiting
          │
          ↓
     Event Loop
          │
          ├── Coroutine B
          ├── Coroutine C
          └── Coroutine D
```

Nhưng nhớ:

> **Có `async/await` chưa có nghĩa là bạn đã chạy nhiều request đồng thời.**

Điều này sẽ được giải quyết ở Buổi 33.

---

# 5. Response vẫn là Response

Sau:

```python
response = await client.get(url)
```

ta vẫn có các thông tin quen thuộc:

```python
response.status_code
response.url
response.headers
response.text
response.content
```

Ví dụ:

```python
print(response.status_code)
print(response.url)
print(response.headers)
print(response.text)
```

Do đó chuyển từ sync sang async **không có nghĩa phải học lại HTTP Response từ đầu**.

---

# 6. Async GET với Query Parameters

Tương tự sync:

```python
response = await client.get(
    "https://httpbin.org/get",
    params={
        "page": 2,
        "limit": 20,
    },
)
```

Complete:

```python
import asyncio

import primp


async def main():

    async with primp.AsyncClient(
        impersonate="chrome_146",
        impersonate_os="windows",
    ) as client:

        response = await client.get(
            "https://httpbin.org/get",
            params={
                "page": 2,
                "limit": 20,
            },
        )

        print("Status:", response.status_code)
        print("URL:", response.url)
        print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
```

URL cuối sẽ có dạng tương đương:

```text
https://httpbin.org/get?page=2&limit=20
```

---

# 7. Async GET với Headers

```python
response = await client.get(
    url,
    headers={
        "Accept": "text/html",
        "Accept-Language": "vi-VN,vi;q=0.9",
    },
)
```

Trong Novel Crawler:

```python
response = await client.get(
    chapter_url,
    headers={
        "Referer": novel_url,
    },
)
```

Đây là một ví dụ rất thực tế.

---

# 8. Kết hợp `params` + `headers`

```python
response = await client.get(
    "https://httpbin.org/get",

    params={
        "page": 2,
    },

    headers={
        "Accept": "text/html",
        "Accept-Language": "vi-VN,vi;q=0.9",
    },

    timeout=10,
)
```

Về mặt architecture:

```text
Request
 ├── URL
 ├── params
 ├── headers
 └── timeout
        ↓
   AsyncBrowserClient
        ↓
   primp.AsyncClient
```

---

# 9. Xây lại `AsyncBrowserClient`

Ở Buổi 31 chúng ta có phiên bản cơ bản.

Bây giờ làm sạch hơn:

```python
from dataclasses import dataclass

import primp


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
```

---

# 10. Sử dụng `AsyncBrowserClient`

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

    client = AsyncBrowserClient(profile)

    response = await client.get(
        "https://httpbin.org/get",
        params={
            "page": 2,
        },
    )

    print(response.status_code)
    print(response.url)
    print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
```

Nhưng code này còn một vấn đề:

**Lifecycle.**

---

# 11. Lifecycle của AsyncClient

Tốt hơn là:

```python
async with AsyncBrowserClient(profile) as client:
    ...
```

Ta xây context manager:

```python
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
async def main():

    profile = BrowserProfile(
        impersonate="chrome_146",
        os="windows",
    )

    async with AsyncBrowserClient(profile) as client:

        response = await client.get(
            "https://httpbin.org/get"
        )

        print(response.text)
```

---

# 12. Vì sao lifecycle quan trọng?

Hãy hình dung crawler:

```text
Crawler start
     ↓
Create AsyncClient
     ↓
Chapter 1
     ↓
Chapter 2
     ↓
Chapter 3
     ↓
Chapter 4
     ↓
Chapter 5
     ↓
Crawler shutdown
     ↓
Close AsyncClient
```

Không phải:

```text
Chapter 1 → create client → close
Chapter 2 → create client → close
Chapter 3 → create client → close
```

Client dài hạn giúp tận dụng connection/session state phù hợp.

---

# 13. Async GET không nên chứa business logic

Không nên:

```python
async def get_chapter(url):

    response = await client.get(url)

    title = ...
    author = ...
    content = ...

    save_to_database(...)

    return ...
```

Đây là quá nhiều responsibility.

Tách:

```text
Fetcher
   ↓
HTTP Response

Parser
   ↓
Chapter

Repository
   ↓
Database
```

---

# 14. Kiến trúc Novel Crawler

```text
                Application
                    │
                    ↓
              CrawlChapter
                    │
                    ↓
               AsyncFetcher
                    │
                    ↓
          AsyncBrowserClient
                    │
                    ↓
          primp.AsyncClient
                    │
                    ↓
                  HTTP
                    │
                    ↓
                Response
                    │
                    ↓
                 Parser
                    │
                    ↓
                Chapter
                    │
                    ↓
              Repository
```

Async chỉ nằm chủ yếu ở **I/O boundary**.

---

# 15. Fetcher interface

Ta có thể định nghĩa Protocol:

```python
from typing import Protocol


class AsyncFetcher(Protocol):

    async def get(
        self,
        url: str,
    ):
        ...
```

Sau đó:

```text
AsyncFetcher
     ↑
     │
AsyncBrowserClient
```

Application chỉ cần biết:

```python
response = await fetcher.get(url)
```

Không cần biết:

```python
primp.AsyncClient
```

---

# 16. Async GET + Parser

Đây là flow thực tế:

```python
async def crawl_chapter(
    fetcher,
    parser,
    url,
):
    response = await fetcher.get(url)

    chapter = parser.parse(
        response.text
    )

    return chapter
```

Điểm rất đẹp:

```text
await
```

chỉ xuất hiện ở network boundary.

Parser vẫn có thể là:

```python
chapter = parser.parse(html)
```

hoàn toàn synchronous.

---

# 17. Tại sao Parser không cần async?

`selectolax` xử lý HTML trong memory:

```text
HTML string
    ↓
selectolax
    ↓
DOM
    ↓
Chapter
```

Đây không phải network I/O.

Do đó không cần:

```python
await parser.parse(...)
```

trừ khi parser thực sự có asynchronous I/O riêng.

Thông thường:

```text
Fetcher       → async
Parser        → sync
Repository    → tùy database implementation
```

là thiết kế hợp lý.

---

# 18. Async GET + yarl

Bạn đã học `yarl`, nên có thể kết hợp:

```python
from yarl import URL


chapter_url = URL(
    "https://example.com/truyen/abc"
)

chapter_url = chapter_url.with_query(
    page=2
)

response = await client.get(
    str(chapter_url)
)
```

Architecture:

```text
yarl
 ↓
URL construction
 ↓
AsyncFetcher
 ↓
primp
 ↓
HTTP
```

Không để `primp` chịu trách nhiệm xây URL business logic.

---

# 19. Xử lý lỗi

Async cũng cần `try/except`.

```python
import asyncio
import primp


async def main():

    async with primp.AsyncClient() as client:

        try:

            response = await client.get(
                "https://example.invalid"
            )

            print(response.status_code)

        except Exception as exc:

            print(
                "Request failed:",
                type(exc).__name__,
            )


if __name__ == "__main__":
    asyncio.run(main())
```

Ở giai đoạn hiện tại chưa cần xây retry.

Retry sẽ là:

```text
Buổi 35 — Timeout + Retry
```

---

# 20. Timeout

Có thể truyền timeout:

```python
response = await client.get(
    url,
    timeout=5,
)
```

Flow:

```text
Async GET
    │
    ├── response
    │
    └── timeout
          ↓
       exception
```

Đừng viết:

```python
except Exception:
    retry()
```

ngay bây giờ.

Vì:

```text
Timeout
DNS error
Connection error
SSL error
404
500
```

không nhất thiết có cùng retry policy.

Buổi 35 chúng ta sẽ phân loại chúng.

---

# 21. Một lỗi async rất phổ biến

Sai:

```python
response = client.get(url)
```

Nếu `client.get()` là async method thì bạn nhận được coroutine, không phải response.

Đúng:

```python
response = await client.get(url)
```

Có thể kiểm tra:

```python
print(type(response))
```

Sau `await`, mới xử lý:

```python
response.status_code
response.text
```

---

# 22. Một lỗi khác

Không nên:

```python
await asyncio.run(main())
```

Bởi vì:

```python
asyncio.run()
```

là cách khởi động event loop từ synchronous entry point.

Đúng:

```python
if __name__ == "__main__":
    asyncio.run(main())
```

Bên trong async code:

```python
await something()
```

---

# 23. `time.sleep()` trong async code

Đây là lỗi cực kỳ quan trọng.

Không nên:

```python
async def fetch():
    time.sleep(5)
    response = await client.get(url)
```

`time.sleep()` block event loop.

Nếu cần sleep async:

```python
await asyncio.sleep(5)
```

So sánh:

```text
time.sleep()
    ↓
BLOCK EVENT LOOP
```

trong khi:

```text
await asyncio.sleep()
    ↓
yield control
    ↓
event loop làm việc khác
```

Rate limiting sau này phải đặc biệt chú ý điều này.

---

# 24. Async GET tuần tự

Ví dụ:

```python
async def main():

    async with primp.AsyncClient() as client:

        for url in urls:

            response = await client.get(url)

            print(response.status_code)
```

Flow:

```text
GET 1
 ↓
wait
 ↓
response 1
 ↓
GET 2
 ↓
wait
 ↓
response 2
 ↓
GET 3
```

Đây vẫn là **sequential I/O**.

---

# 25. Async GET concurrent

Preview:

```python
tasks = [
    client.get(url1),
    client.get(url2),
    client.get(url3),
]

responses = await asyncio.gather(*tasks)
```

Flow:

```text
             ┌── GET 1
             │
gather() ────┼── GET 2
             │
             └── GET 3
                    ↓
               responses
```

Đây mới là nền tảng crawler tốc độ cao.

**Buổi 33 chúng ta sẽ học rất kỹ phần này.**

---

# 26. Ví dụ thực tế với chapter URLs

Giả sử parser đã tìm được:

```python
chapter_urls = [
    "https://example.com/chapter-1",
    "https://example.com/chapter-2",
    "https://example.com/chapter-3",
]
```

Buổi 32:

```python
async def fetch_chapters(
    client,
    chapter_urls,
):

    results = []

    for url in chapter_urls:

        response = await client.get(url)

        results.append(response)

    return results
```

Đây là:

```text
async
+
reuse client
+
sequential
```

Buổi 33 sẽ chuyển thành:

```text
async
+
reuse client
+
concurrent
```

---

# 27. Bài tập thực hành

## Bài 1 — GET cơ bản

```python
async with primp.AsyncClient(
    impersonate="chrome_146",
    impersonate_os="windows",
) as client:

    response = await client.get(
        "https://httpbin.org/get"
    )

    print(response.status_code)
    print(response.text)
```

---

## Bài 2 — Query

Gọi:

```text
https://httpbin.org/get
```

với:

```python
params={
    "page": 5,
    "limit": 20,
}
```

Kiểm tra:

```python
print(response.url)
```

---

## Bài 3 — Headers

Gọi:

```text
https://httpbin.org/headers
```

với:

```python
headers={
    "Accept-Language": "vi-VN,vi;q=0.9"
}
```

---

## Bài 4 — Referer

Giả lập:

```text
Novel page
     ↓
Chapter page
```

```python
response = await client.get(
    chapter_url,
    headers={
        "Referer": novel_url,
    },
)
```

---

## Bài 5 — AsyncBrowserClient

Tự viết:

```text
BrowserProfile
AsyncBrowserClient
```

sao cho chạy được:

```python
async with AsyncBrowserClient(profile) as client:

    response = await client.get(url)

    print(response.text)
```

---

# 28. Bài tập quan trọng nhất

Viết function:

```python
async def fetch_one(
    client,
    url: str,
):
    ...
```

Yêu cầu:

* nhận `AsyncClient`
* GET URL
* trả về response
* không parse HTML
* không lưu database
* không retry
* không tạo client mới

Sau đó:

```python
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

            response = await fetch_one(
                client,
                url,
            )

            print(
                response.status_code,
                response.url,
            )
```

Đây chính là nền móng cho Buổi 33.

---

# 29. Tổng kết Buổi 32

Bạn cần nắm chắc 7 điểm:

```text
1. async def
       ↓
   coroutine

2. await client.get()
       ↓
   async HTTP GET

3. AsyncClient
       ↓
   nên reuse

4. async with
       ↓
   lifecycle

5. async ≠ concurrent

6. time.sleep()
       ↓
   không dùng trong async code

7. HTTP async
       ↓
   Parser vẫn có thể sync
```

Kiến trúc hiện tại:

```text
                    Application
                         │
                         ↓
                  Async Fetcher
                         │
                         ↓
               AsyncBrowserClient
                         │
                         ↓
                primp.AsyncClient
                         │
                         ↓
                       HTTP
                         │
                         ↓
                    Response
                         │
                         ↓
                  Parser (sync)
                         │
                         ↓
                      Domain
```

Và bước tiếp theo là:

```text
31. AsyncClient             ✅
32. async GET               ✅
33. Concurrent Requests     ← tiếp theo
34. Semaphore
35. Timeout + Retry
36. Proxy Pool
37. Browser Profile Pool
38. Rate Limiting
39. Fetcher Architecture
40. Async Novel Fetcher
```

**Buổi 33 sẽ là bước ngoặt:** từ một async GET chạy tuần tự, chúng ta sẽ xây `asyncio.gather()` để fetch **nhiều chapter đồng thời**, sau đó Buổi 34 dùng `Semaphore` để kiểm soát số request đồng thời.
