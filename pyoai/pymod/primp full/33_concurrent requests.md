# Buổi 33 — Concurrent Requests với `asyncio.gather()`

Buổi 32 chúng ta đã có:

```text
AsyncClient
    ↓
await client.get()
    ↓
GET từng URL
```

Nhưng nếu có 1.000 chapter:

```text
chapter 1 → chờ xong
chapter 2 → chờ xong
chapter 3 → chờ xong
...
```

thì chưa tận dụng được sức mạnh của `asyncio`.

Hôm nay chúng ta chuyển sang:

```text
                    ┌── GET chapter 1
                    ├── GET chapter 2
                    ├── GET chapter 3
                    ├── GET chapter 4
AsyncClient ────────┼── GET chapter 5
                    └── ...
                           ↓
                       responses
```

Đây là nền móng trực tiếp cho **Async Novel Fetcher**.

---

# 1. Concurrent là gì?

Giả sử mỗi request mất khoảng 2 giây.

### Sequential

```python
for url in urls:
    await client.get(url)
```

Nếu có 5 request:

```text
Request 1 ───── 2s
Request 2 ───── 2s
Request 3 ───── 2s
Request 4 ───── 2s
Request 5 ───── 2s

≈ 10 giây
```

### Concurrent

```python
await asyncio.gather(
    client.get(url1),
    client.get(url2),
    client.get(url3),
    client.get(url4),
    client.get(url5),
)
```

Có thể hình dung:

```text
Request 1 ───────── 2s
Request 2 ───────── 2s
Request 3 ───────── 2s
Request 4 ───────── 2s
Request 5 ───────── 2s

≈ thời gian của request chậm nhất
```

Đây là lý do async rất phù hợp với crawler.

---

# 2. `asyncio.gather()`

Cú pháp cơ bản:

```python
results = await asyncio.gather(
    coroutine_1(),
    coroutine_2(),
    coroutine_3(),
)
```

Ví dụ:

```python
import asyncio


async def task(name: str, delay: float):
    print(f"{name}: start")

    await asyncio.sleep(delay)

    print(f"{name}: done")

    return name


async def main():

    results = await asyncio.gather(
        task("A", 2),
        task("B", 2),
        task("C", 2),
    )

    print(results)


if __name__ == "__main__":
    asyncio.run(main())
```

Kết quả có thể:

```text
A: start
B: start
C: start

A: done
B: done
C: done

['A', 'B', 'C']
```

Tổng thời gian khoảng:

```text
2 giây
```

thay vì:

```text
6 giây
```

---

# 3. Tại sao `asyncio.sleep()` chạy concurrent?

Điểm quan trọng nằm ở:

```python
await asyncio.sleep(delay)
```

Coroutine nói với event loop:

> Tôi đang chờ, hãy chạy coroutine khác.

Vì vậy:

```text
Task A
   ↓
await sleep
   ↓
yield

Task B
   ↓
await sleep
   ↓
yield

Task C
   ↓
await sleep
   ↓
yield
```

Event loop điều phối chúng.

---

# 4. So sánh trực tiếp

## Sequential

```python
async def main():

    await task("A", 2)
    await task("B", 2)
    await task("C", 2)
```

Flow:

```text
A ──────────┐
            ↓
            B ──────────┐
                        ↓
                        C ──────────
```

Khoảng:

```text
6 giây
```

---

## Concurrent

```python
async def main():

    await asyncio.gather(
        task("A", 2),
        task("B", 2),
        task("C", 2),
    )
```

Flow:

```text
A ─────────────
B ─────────────
C ─────────────
```

Khoảng:

```text
2 giây
```

---

# 5. Áp dụng vào `primp`

Bây giờ bỏ `sleep()` và dùng HTTP thật.

```python
import asyncio

import primp


async def fetch(
    client: primp.AsyncClient,
    url: str,
):
    response = await client.get(url)

    return response


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

        responses = await asyncio.gather(
            *(fetch(client, url) for url in urls)
        )

        for response in responses:
            print(
                response.status_code,
                response.url,
            )


if __name__ == "__main__":
    asyncio.run(main())
```

Điểm quan trọng:

```python
*(fetch(client, url) for url in urls)
```

tạo ra nhiều coroutine.

Sau đó:

```python
asyncio.gather(...)
```

chờ tất cả hoàn thành.

---

# 6. Viết đơn giản hơn

Ta hoàn toàn có thể viết:

```python
responses = await asyncio.gather(
    client.get(url1),
    client.get(url2),
    client.get(url3),
)
```

Ví dụ:

```python
import asyncio

import primp


async def main():

    async with primp.AsyncClient(
        impersonate="chrome_146",
        impersonate_os="windows",
    ) as client:

        responses = await asyncio.gather(
            client.get("https://httpbin.org/get?page=1"),
            client.get("https://httpbin.org/get?page=2"),
            client.get("https://httpbin.org/get?page=3"),
        )

        for response in responses:
            print(response.status_code)
            print(response.url)
            print()


if __name__ == "__main__":
    asyncio.run(main())
```

Đây là cách rất dễ hiểu khi số lượng request nhỏ.

---

# 7. Với danh sách URL

Crawler thực tế sẽ có:

```python
urls = [...]
```

Không thể viết thủ công 1.000 dòng.

Dùng:

```python
tasks = [
    client.get(url)
    for url in urls
]

responses = await asyncio.gather(*tasks)
```

Hoặc:

```python
responses = await asyncio.gather(
    *(client.get(url) for url in urls)
)
```

Hai cách đều có cùng ý tưởng.

---

# 8. `gather()` giữ thứ tự kết quả

Đây là điểm rất quan trọng.

Giả sử:

```python
urls = [
    "chapter-1",
    "chapter-2",
    "chapter-3",
]
```

Ta:

```python
responses = await asyncio.gather(
    client.get("chapter-1"),
    client.get("chapter-2"),
    client.get("chapter-3"),
)
```

Cho dù:

```text
chapter-3 hoàn thành trước
chapter-1 hoàn thành sau
chapter-2 hoàn thành giữa
```

`results` vẫn tương ứng:

```text
results[0] → chapter-1
results[1] → chapter-2
results[2] → chapter-3
```

Tức là:

```text
Input order
    ↓
gather()
    ↓
Output order
```

được giữ nguyên.

---

# 9. Nhưng execution order không được giữ

Đây là hai khái niệm khác nhau.

Input:

```text
1
2
3
```

Execution:

```text
2 ─────── done
3 ─────────── done
1 ─────────────── done
```

Nhưng kết quả:

```python
results[0] → 1
results[1] → 2
results[2] → 3
```

Vì vậy:

```text
Completion order ≠ Result order
```

---

# 10. Cực kỳ quan trọng với crawler

Giả sử:

```python
chapter_urls = [
    chapter_1,
    chapter_2,
    chapter_3,
]
```

Ta fetch concurrent:

```python
responses = await asyncio.gather(
    *(client.get(url) for url in chapter_urls)
)
```

Sau đó:

```python
for url, response in zip(
    chapter_urls,
    responses,
):
    print(url, response.url)
```

Ta vẫn map được:

```text
chapter_1 → response_1
chapter_2 → response_2
chapter_3 → response_3
```

---

# 11. Viết `fetch_one()`

Đây là cách tôi khuyến nghị cho kiến trúc crawler.

```python
async def fetch_one(
    client,
    url: str,
):
    response = await client.get(url)

    return response
```

Sau đó:

```python
responses = await asyncio.gather(
    *(fetch_one(client, url) for url in urls)
)
```

Tại sao nên có `fetch_one()`?

Vì sau này chúng ta sẽ thêm:

```text
fetch_one()
    ↓
timeout
    ↓
exception classification
    ↓
retry
    ↓
proxy
    ↓
logging
    ↓
metrics
```

Nhưng **không nên nhét tất cả vào hôm nay**.

---

# 12. Thêm index

Crawler đôi khi cần biết request thứ mấy.

```python
async def fetch_one(
    client,
    index: int,
    url: str,
):
    print(f"[{index}] GET {url}")

    response = await client.get(url)

    print(
        f"[{index}] DONE {response.status_code}"
    )

    return response
```

Sử dụng:

```python
tasks = [
    fetch_one(client, index, url)
    for index, url in enumerate(urls)
]

responses = await asyncio.gather(*tasks)
```

---

# 13. Ví dụ hoàn chỉnh cho Novel Crawler

Giả sử parser đã tìm được chapter URLs.

```python
import asyncio

import primp


async def fetch_one(
    client: primp.AsyncClient,
    index: int,
    url: str,
):
    print(f"[{index}] GET {url}")

    response = await client.get(
        url,
        timeout=10,
    )

    print(
        f"[{index}] DONE "
        f"{response.status_code}"
    )

    return response


async def fetch_chapters(
    client: primp.AsyncClient,
    urls: list[str],
):
    tasks = [
        fetch_one(client, index, url)
        for index, url in enumerate(urls, start=1)
    ]

    return await asyncio.gather(*tasks)


async def main():

    urls = [
        "https://httpbin.org/get?chapter=1",
        "https://httpbin.org/get?chapter=2",
        "https://httpbin.org/get?chapter=3",
        "https://httpbin.org/get?chapter=4",
        "https://httpbin.org/get?chapter=5",
    ]

    async with primp.AsyncClient(
        impersonate="chrome_146",
        impersonate_os="windows",
    ) as client:

        responses = await fetch_chapters(
            client,
            urls,
        )

        print()
        print("Total:", len(responses))

        for response in responses:
            print(
                response.status_code,
                response.url,
            )


if __name__ == "__main__":
    asyncio.run(main())
```

Đây đã là một **mini concurrent fetcher**.

---

# 14. Nhưng có một vấn đề rất lớn

Giả sử:

```python
urls = 100_000
```

Bạn làm:

```python
await asyncio.gather(
    *(client.get(url) for url in urls)
)
```

Về mặt ý tưởng:

```text
100,000 requests
       ↓
gather()
       ↓
100,000 coroutine
```

Đây **không phải thiết kế tốt** cho crawler production.

Có thể gây:

* quá nhiều task;
* quá nhiều connection;
* áp lực memory;
* quá tải server;
* dễ bị rate-limit;
* proxy pool bị khai thác quá nhanh;
* khó kiểm soát concurrency.

Đây chính là lý do **Buổi 34 — Semaphore** tồn tại.

---

# 15. `gather()` không phải concurrency limit

Đây là điểm phải nhớ:

```python
asyncio.gather(...)
```

nói:

> Chạy/chờ nhóm coroutine này.

Nó **không phải**:

> Chỉ cho phép tối đa 10 request cùng lúc.

Muốn:

```text
1000 URLs
     ↓
chỉ 10 request đồng thời
```

ta cần:

```python
asyncio.Semaphore(10)
```

Buổi 34 sẽ giải quyết chính xác vấn đề này.

---

# 16. Exception với `gather()`

Giả sử:

```python
async def task(n):
    if n == 2:
        raise RuntimeError("Failed")

    return n
```

và:

```python
results = await asyncio.gather(
    task(1),
    task(2),
    task(3),
)
```

Một task có thể phát sinh exception.

Với mặc định:

```python
return_exceptions=False
```

exception được propagate ra ngoài `gather()`.

Ví dụ:

```python
import asyncio


async def task(n: int):

    await asyncio.sleep(1)

    if n == 2:
        raise RuntimeError(
            "Task 2 failed"
        )

    return n


async def main():

    try:

        results = await asyncio.gather(
            task(1),
            task(2),
            task(3),
        )

        print(results)

    except Exception as exc:

        print(
            "Error:",
            type(exc).__name__,
            exc,
        )


if __name__ == "__main__":
    asyncio.run(main())
```

---

# 17. `return_exceptions=True`

Một lựa chọn khác:

```python
results = await asyncio.gather(
    task(1),
    task(2),
    task(3),
    return_exceptions=True,
)
```

Khi đó exception trở thành một phần của kết quả.

Ví dụ:

```text
[
    1,
    RuntimeError(...),
    3
]
```

Điều này rất hữu ích trong crawler.

Vì:

```text
Chapter 1 → success
Chapter 2 → failed
Chapter 3 → success
Chapter 4 → success
```

Ta không nhất thiết muốn toàn bộ batch thất bại chỉ vì Chapter 2 lỗi.

---

# 18. Crawler batch nên xử lý như thế nào?

Có thể:

```python
results = await asyncio.gather(
    *(fetch_one(client, url) for url in urls),
    return_exceptions=True,
)
```

Sau đó:

```python
for url, result in zip(urls, results):

    if isinstance(result, Exception):

        print(
            "FAILED:",
            url,
            type(result).__name__,
        )

        continue

    print(
        "SUCCESS:",
        url,
        result.status_code,
    )
```

Đây là nền móng cho:

```text
Error Classification
Retry Policy
```

sau này.

---

# 19. Không retry ngay ở đây

Đừng làm:

```python
async def fetch_one(...):

    try:
        ...
    except:
        for i in range(5):
            ...
```

Chúng ta đang học concurrency.

Kiến trúc cuối cùng sẽ tách:

```text
fetch_one
    ↓
HTTP error
    ↓
Error Classifier
    ↓
Retry Policy
    ↓
Retry
```

Buổi 35 mới xây phần đó.

---

# 20. Concurrent Fetcher với Browser Profile

Ta vẫn giữ Browser Profile từ Part III:

```python
import asyncio

import primp


async def main():

    async with primp.AsyncClient(
        impersonate="chrome_146",
        impersonate_os="windows",
    ) as client:

        urls = [
            "https://httpbin.org/get?page=1",
            "https://httpbin.org/get?page=2",
            "https://httpbin.org/get?page=3",
        ]

        responses = await asyncio.gather(
            *(client.get(url) for url in urls)
        )

        for response in responses:
            print(response.url)


if __name__ == "__main__":
    asyncio.run(main())
```

Tất cả request dùng cùng:

```text
Browser Profile
       ↓
AsyncClient
       ↓
connection/session state
```

Đây là điều phù hợp với mô hình crawler của chúng ta.

---

# 21. Đừng tạo Client cho mỗi request

Sai:

```python
async def fetch(url):

    async with primp.AsyncClient() as client:
        return await client.get(url)
```

rồi:

```python
await asyncio.gather(
    *(fetch(url) for url in urls)
)
```

Bạn đang tạo rất nhiều client.

Tốt hơn:

```python
async with primp.AsyncClient() as client:

    responses = await asyncio.gather(
        *(client.get(url) for url in urls)
    )
```

Tức là:

```text
                AsyncClient
                /    |    \
               /     |     \
            GET 1   GET 2   GET 3
```

thay vì:

```text
GET 1 → Client 1
GET 2 → Client 2
GET 3 → Client 3
```

---

# 22. Architecture sau Buổi 33

Hiện tại:

```text
                    Application
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
             ┌───────────┼───────────┐
             ↓           ↓           ↓
          GET #1      GET #2      GET #3
             │           │           │
             └───────────┼───────────┘
                         ↓
                     Responses
```

Đây là:

```text
Concurrent Requests
```

Nhưng còn thiếu:

```text
Concurrency Limit
```

---

# 23. Architecture mục tiêu

Sau khi hoàn thành Part IV:

```text
                     AsyncFetcher
                          │
                          ↓
                    Concurrency
                          │
                     Semaphore
                          │
                          ↓
                  Browser Profile
                          │
                          ↓
                  Proxy Strategy
                          │
                          ↓
                   Rate Limiter
                          │
                          ↓
                primp.AsyncClient
                          │
                ┌─────────┼─────────┐
                ↓         ↓         ↓
              GET       GET       GET
```

Từng lớp sẽ được học riêng.

---

# 24. Một nguyên tắc rất quan trọng

Đừng nhầm:

```text
Async
```

với:

```text
Concurrent
```

và cũng đừng nhầm:

```text
Concurrent
```

với:

```text
Unlimited
```

Ta có:

```text
async
  ↓
có khả năng nhường event loop

concurrent
  ↓
nhiều operation đang tiến hành đan xen

semaphore
  ↓
giới hạn bao nhiêu operation được phép cùng lúc
```

Do đó:

```text
Buổi 31
AsyncClient
    ↓
Buổi 32
async GET
    ↓
Buổi 33
Concurrent Requests
    ↓
Buổi 34
Semaphore
```

là một chuỗi kiến thức rất logic.

---

# 25. Bài tập thực hành

## Bài 1 — Chứng minh concurrent

Viết:

```python
async def worker(name, delay):
    ...
```

Chạy 5 worker:

```text
A → 2s
B → 1s
C → 3s
D → 1s
E → 2s
```

dùng:

```python
asyncio.gather()
```

Quan sát thứ tự hoàn thành.

---

## Bài 2 — 10 HTTP requests

Tạo:

```python
urls = [
    f"https://httpbin.org/get?page={i}"
    for i in range(1, 11)
]
```

Fetch bằng:

```python
await asyncio.gather(...)
```

In:

```text
page
status
url
```

---

## Bài 3 — Error handling

Cho một URL không hợp lệ:

```text
https://example.invalid
```

vào giữa danh sách.

Dùng:

```python
return_exceptions=True
```

Sau đó phân biệt:

```text
SUCCESS
FAILED
```

---

## Bài 4 — Mapping

Cho:

```python
urls = [
    "chapter-1",
    "chapter-2",
    "chapter-3",
]
```

Hãy đảm bảo output có dạng:

```text
chapter-1 → response-1
chapter-2 → response-2
chapter-3 → response-3
```

dù completion order khác nhau.

---

# 26. Bài tập quan trọng nhất

Hãy xây function:

```python
async def fetch_many(
    client,
    urls: list[str],
):
    ...
```

Yêu cầu:

```text
✓ dùng asyncio.gather()
✓ dùng một AsyncClient
✓ concurrent
✓ trả về kết quả theo đúng thứ tự urls
✓ exception của một URL không làm mất kết quả các URL khác
✓ chưa dùng Semaphore
✓ chưa retry
```

Khung:

```python
async def fetch_many(client, urls):

    results = await asyncio.gather(
        ...,
        return_exceptions=True,
    )

    return results
```

Đây chính là phiên bản đầu tiên của **batch fetcher**.

---

# 27. Tổng kết

Sau Buổi 33, mô hình trong đầu bạn nên là:

```text
                100 URLs
                   │
                   ↓
             asyncio.gather()
                   │
        ┌──────────┼──────────┐
        ↓          ↓          ↓
      GET 1      GET 2      GET 3
        ↓          ↓          ↓
      Resp       Resp       Resp
        └──────────┼──────────┘
                   ↓
                results
```

Nhưng:

```text
100 URLs
   ↓
100 requests cùng lúc
```

không phải lúc nào cũng đúng.

Vì vậy **Buổi 34 — Semaphore** sẽ giải quyết bài toán cực kỳ quan trọng:

```text
1000 URLs
     ↓
chỉ cho phép 10 requests
đang chạy đồng thời
     ↓
xong một request
     ↓
cho request tiếp theo vào
```

Mô hình:

```text
                1000 URLs
                    │
                    ↓
               Semaphore(10)
                    │
          ┌─────────┴─────────┐
          ↓                   ↓
      tối đa 10          chờ slot
      requests           tiếp theo
          │
          ↓
   primp.AsyncClient
```

Đây là bước bắt buộc trước khi chúng ta xây **Proxy Pool + Browser Profile Pool + Rate Limiting** cho Novel Crawler.
