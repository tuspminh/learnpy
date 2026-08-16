# Iterator Deep Dive — Buổi 20

# Async Iterator

Hôm nay chúng ta chuyển từ **Iterator đồng bộ** sang **Iterator bất đồng bộ**.

Đây là bước rất quan trọng nếu bạn muốn làm:

* Async Crawler
* WebSocket
* Streaming API
* Streaming HTTP
* Async Database
* Queue Worker
* Event Stream
* AI Streaming

Đặc biệt với Python `asyncio`, bạn sẽ thường xuyên gặp:

```python
async for item in source:
    ...
```

Muốn hiểu `async for`, chúng ta phải hiểu **Async Iterator Protocol**.

---

# 1. Iterator và Async Iterator

Iterator thông thường:

```python
for item in iterator:
    ...
```

về bản chất tương đương:

```python
iterator = iter(source)

while True:
    try:
        item = next(iterator)
    except StopIteration:
        break

    ...
```

Async Iterator cũng tương tự, nhưng việc lấy phần tử kế tiếp có thể cần `await`.

```python
async for item in source:
    ...
```

về ý tưởng:

```python
iterator = source.__aiter__()

while True:
    try:
        item = await iterator.__anext__()
    except StopAsyncIteration:
        break

    ...
```

Đây chính là điểm cốt lõi của buổi học.

---

# 2. Async Iterator Protocol

Một Async Iterator cần hai phương thức:

```python
__aiter__()
__anext__()
```

Trong đó:

### `__aiter__()`

Trả về Async Iterator.

### `__anext__()`

Trả về một **Awaitable**.

Khi await hoàn thành:

```text
value
```

được trả về.

Khi hết dữ liệu:

```python
StopAsyncIteration
```

được raise.

---

# 3. Iterator vs Async Iterator

Iterator:

```python
class MyIterator:

    def __iter__(self):
        return self

    def __next__(self):
        ...
```

Async Iterator:

```python
class MyAsyncIterator:

    def __aiter__(self):
        return self

    async def __anext__(self):
        ...
```

Điểm khác biệt quan trọng:

```text
Iterator
    ↓
next()
    ↓
value
```

Trong khi:

```text
Async Iterator
    ↓
await __anext__()
    ↓
value
```

---

# 4. Async Iterator đầu tiên

```python
import asyncio


class Counter:

    def __init__(self, limit):
        self.current = 0
        self.limit = limit

    def __aiter__(self):
        return self

    async def __anext__(self):

        if self.current >= self.limit:
            raise StopAsyncIteration

        value = self.current

        self.current += 1

        return value
```

Sử dụng:

```python
async def main():

    async for number in Counter(5):
        print(number)


asyncio.run(main())
```

Kết quả:

```text
0
1
2
3
4
```

---

# 5. Thêm `await`

Async Iterator trở nên thực sự hữu ích khi mỗi phần tử cần thực hiện một thao tác bất đồng bộ.

Ví dụ mô phỏng API:

```python
import asyncio


class ApiIterator:

    def __init__(self, limit):
        self.current = 0
        self.limit = limit

    def __aiter__(self):
        return self

    async def __anext__(self):

        if self.current >= self.limit:
            raise StopAsyncIteration

        await asyncio.sleep(1)

        value = self.current

        self.current += 1

        return value
```

Sử dụng:

```python
async def main():

    async for value in ApiIterator(3):
        print(value)


asyncio.run(main())
```

Mỗi phần tử xuất hiện cách nhau khoảng 1 giây.

```text
0
   ↓ 1s
1
   ↓ 1s
2
```

---

# 6. Vì sao Async Iterator quan trọng?

Giả sử bạn crawl:

```text
URL 1
URL 2
URL 3
URL 4
```

Mỗi URL mất 1 giây để download.

Iterator đồng bộ:

```text
URL1 → 1s
       ↓
URL2 → 1s
       ↓
URL3 → 1s
       ↓
URL4 → 1s

≈ 4s
```

Async Iterator cho phép thao tác I/O không chặn event loop.

```text
URL1 ─────┐
URL2 ─────┤
URL3 ─────┤ → Event Loop
URL4 ─────┘
```

Async Iterator **không tự động làm mọi thứ chạy song song**; nó chỉ cho phép quá trình lấy dữ liệu và chờ I/O diễn ra bất đồng bộ. Muốn chạy nhiều request đồng thời, ta còn cần task/concurrency.

---

# 7. `async for` hoạt động thế nào?

Code:

```python
async for item in source:
    print(item)
```

Có thể hình dung thành:

```python
iterator = source.__aiter__()

while True:

    try:
        item = await iterator.__anext__()

    except StopAsyncIteration:
        break

    print(item)
```

Đây là kiến thức cực kỳ quan trọng.

Khi hiểu đoạn này, `async for` không còn là "cú pháp thần bí".

---

# 8. `StopAsyncIteration`

Iterator đồng bộ:

```python
StopIteration
```

Async Iterator:

```python
StopAsyncIteration
```

Ví dụ:

```python
class Counter:

    def __init__(self):
        self.value = 0

    def __aiter__(self):
        return self

    async def __anext__(self):

        if self.value >= 3:
            raise StopAsyncIteration

        value = self.value
        self.value += 1

        return value
```

Khi:

```python
await iterator.__anext__()
```

đến lần thứ tư:

```text
StopAsyncIteration
```

`async for` bắt exception này và kết thúc vòng lặp.

---

# 9. Async Generator

Trong thực tế, bạn **hiếm khi cần tự viết `__aiter__()` và `__anext__()`**.

Thay vào đó, Python cung cấp:

```python
async def
yield
```

Ví dụ:

```python
async def numbers():

    for i in range(5):

        await asyncio.sleep(1)

        yield i
```

Đây là:

> Async Generator.

Sử dụng:

```python
async def main():

    async for number in numbers():
        print(number)
```

Đây là cách viết đơn giản và tự nhiên hơn rất nhiều.

---

# 10. Async Generator là Async Iterator

```python
async def numbers():

    yield 1
    yield 2
    yield 3
```

```python
gen = numbers()
```

`gen` là Async Generator.

Nó hỗ trợ:

```python
__aiter__()
__anext__()
```

Do đó:

```python
async for x in gen:
    ...
```

hoạt động.

Quan hệ:

```text
Async Generator
       │
       ▼
Async Iterator
       │
       ▼
Async Iterable
```

---

# 11. Async Generator + I/O

Ví dụ mô phỏng API:

```python
import asyncio


async def fetch_pages():

    for page in range(1, 6):

        await asyncio.sleep(0.5)

        yield {
            "page": page,
            "url": f"https://example.com/page/{page}"
        }
```

Sử dụng:

```python
async def main():

    async for page in fetch_pages():

        print(page)


asyncio.run(main())
```

Kết quả:

```text
{'page': 1, ...}
{'page': 2, ...}
{'page': 3, ...}
{'page': 4, ...}
{'page': 5, ...}
```

---

# 12. Async Generator rất giống Generator thường

Generator:

```python
def numbers():

    for i in range(5):
        yield i
```

Async Generator:

```python
async def numbers():

    for i in range(5):

        await asyncio.sleep(1)

        yield i
```

Khác biệt:

```text
Generator
    ↓
next()

Async Generator
    ↓
await anext()
```

và:

```text
for
```

thành:

```text
async for
```

---

# 13. `anext()`

Python cung cấp:

```python
anext()
```

Ví dụ:

```python
async def numbers():

    yield 10
    yield 20
    yield 30
```

Ta có:

```python
async def main():

    gen = numbers()

    print(await anext(gen))
    print(await anext(gen))
    print(await anext(gen))
```

Kết quả:

```text
10
20
30
```

Đây chính là phiên bản bất đồng bộ của:

```python
next(iterator)
```

---

# 14. `aiter()`

Tương tự:

```python
iter()
```

Python có:

```python
aiter()
```

Ví dụ:

```python
iterator = aiter(numbers())
```

Sau đó:

```python
value = await anext(iterator)
```

---

# 15. Async Generator với API Pagination

Đây là ví dụ thực tế hơn.

Giả sử API có:

```text
/page/1
/page/2
/page/3
...
```

Ta thiết kế:

```python
async def fetch_all_pages(client):

    page = 1

    while True:

        response = await client.get(
            f"https://example.com/page/{page}"
        )

        data = await response.json()

        if not data["items"]:
            break

        yield from ...
```

Nhưng ở đây có một điểm quan trọng:

**Async Generator không thể dùng `yield from` như Generator đồng bộ.**

Không viết:

```python
yield from ...
```

trong `async def`.

Thay vào đó:

```python
async for item in source:
    yield item
```

---

# 16. Async `yield from` tương đương

Generator thường:

```python
def outer():

    yield from inner()
```

Async Generator:

```python
async def outer():

    async for item in inner():
        yield item
```

Đây là một điểm rất quan trọng.

---

# 17. Async Iterator cho Crawler

Bây giờ xây dựng một crawler đơn giản:

```python
import asyncio


class Crawler:

    def __init__(self, pages):
        self.pages = pages

    def __aiter__(self):
        return self._crawl()

    async def _crawl(self):

        for page in self.pages:

            await asyncio.sleep(0.2)

            yield {
                "url": page,
                "status": 200
            }
```

Sử dụng:

```python
async def main():

    crawler = Crawler([
        "https://example.com/1",
        "https://example.com/2",
        "https://example.com/3",
    ])

    async for result in crawler:
        print(result)


asyncio.run(main())
```

---

# 18. Async Pipeline

Đây là kiến trúc rất quan trọng.

```text
URL Generator
      ↓
Async Downloader
      ↓
Async Parser
      ↓
Async Validator
      ↓
Async Repository
```

Ví dụ:

```python
async def urls():

    for page in range(1, 6):
        yield f"https://example.com/{page}"
```

Downloader:

```python
async def download(urls):

    async for url in urls:

        await asyncio.sleep(0.2)

        yield f"<html>{url}</html>"
```

Parser:

```python
async def parse(htmls):

    async for html in htmls:

        yield {
            "html": html
        }
```

Pipeline:

```python
async def main():

    pages = urls()

    htmls = download(pages)

    items = parse(htmls)

    async for item in items:
        print(item)
```

---

# 19. Đây chính là Async Lazy Pipeline

Không có:

```python
list(...)
```

Không có:

```python
await gather_all_data()
```

Toàn bộ pipeline:

```text
lazy
+
async
+
streaming
```

Mỗi phần tử được xử lý khi cần.

---

# 20. Async Iterator + Queue

Trong crawler worker, một mô hình phổ biến là:

```text
Producer
    ↓
asyncio.Queue
    ↓
Consumer
```

Producer:

```python
async def producer(queue):

    for i in range(10):

        await queue.put(i)
```

Consumer:

```python
async def consumer(queue):

    while True:

        item = await queue.get()

        try:
            print("Processing:", item)

        finally:
            queue.task_done()
```

Đây là một bước tiến gần tới kiến trúc **crawl worker**.

---

# 21. Async Iterator và concurrency

Một lỗi rất phổ biến:

```python
async def crawl():

    async for url in urls():

        await download(url)
```

Đoạn này là async nhưng vẫn xử lý:

```text
URL1
 ↓
chờ
 ↓
URL2
 ↓
chờ
 ↓
URL3
```

Không có concurrency thực sự giữa các download.

---

Muốn xử lý nhiều URL đồng thời, cần tạo task.

Ví dụ ý tưởng:

```python
tasks = [
    asyncio.create_task(download(url))
    for url in urls
]
```

Sau đó:

```python
results = await asyncio.gather(*tasks)
```

Nhưng với dữ liệu lớn, cách tạo **hàng triệu task một lúc** lại là vấn đề.

Đó là lý do các kiến trúc worker + queue + semaphore + async iterator rất quan trọng.

---

# 22. Async Iterator + Semaphore

Ví dụ giới hạn 5 request đồng thời:

```python
import asyncio


semaphore = asyncio.Semaphore(5)


async def fetch(url):

    async with semaphore:

        print("Downloading", url)

        await asyncio.sleep(1)

        return url
```

Semaphore giúp giới hạn concurrency.

---

# 23. Async Generator có thể tạo stream vô hạn

```python
async def events():

    event_id = 0

    while True:

        await asyncio.sleep(1)

        yield {
            "id": event_id
        }

        event_id += 1
```

Đây là:

> Async Infinite Iterator.

Sử dụng:

```python
async for event in events():

    print(event)
```

Nhưng chương trình sẽ chạy mãi.

Cần dừng:

```python
count = 0

async for event in events():

    print(event)

    count += 1

    if count >= 10:
        break
```

---

# 24. Async Infinite Stream

Ta có thể hình dung:

```text
WebSocket
    ↓
Async Iterator
    ↓
Parser
    ↓
Filter
    ↓
Database
```

Dữ liệu có thể chạy liên tục:

```text
event 1
event 2
event 3
event 4
...
```

Đây là mô hình **stream processing**.

---

# 25. Xử lý lỗi

Async Iterator có thể gặp exception.

```python
async def data():

    for i in range(5):

        if i == 3:
            raise RuntimeError("Network error")

        yield i
```

Consumer:

```python
async def main():

    try:

        async for item in data():
            print(item)

    except RuntimeError as exc:

        print("Error:", exc)
```

---

# 26. Cleanup

Một vấn đề quan trọng khi làm Async Iterator là tài nguyên:

* HTTP connection
* File
* Socket
* Database connection

Async Generator có thể sử dụng:

```python
try:
    ...
finally:
    ...
```

Ví dụ:

```python
async def stream():

    resource = await open_resource()

    try:

        while True:

            item = await resource.read()

            if not item:
                break

            yield item

    finally:

        await resource.close()
```

Đây là pattern cực kỳ quan trọng trong code production.

---

# 27. Async Iterator và `aclose()`

Async Generator có:

```python
await generator.aclose()
```

Điều này cho phép đóng generator sớm và kích hoạt cleanup.

Ví dụ:

```python
async def stream():

    try:

        yield 1
        yield 2
        yield 3

    finally:

        print("Cleanup")
```

Nếu đóng generator:

```python
gen = stream()

print(await anext(gen))

await gen.aclose()
```

`finally` sẽ được thực hiện.

---

# 28. Async Iterator vs Async Generator

|                 | Async Iterator | Async Generator |
| --------------- | -------------- | --------------- |
| `__aiter__()`   | Tự viết        | Python tự tạo   |
| `__anext__()`   | Tự viết        | Python tự tạo   |
| `async for`     | ✅              | ✅               |
| `yield`         | Không bắt buộc | ✅               |
| Dễ viết         | Khó hơn        | Dễ hơn          |
| Custom protocol | Rất phù hợp    | Phù hợp         |
| Streaming       | ✅              | ✅               |

---

# 29. Khi nào dùng class Async Iterator?

Dùng class khi Iterator có **state phức tạp**.

Ví dụ:

```python
class DatabasePager:
    ...
```

Có thể giữ:

```text
connection
page
limit
offset
retry_count
cursor
```

---

# 30. Khi nào dùng Async Generator?

Khi logic đơn giản:

```python
async def read_pages():

    for page in pages:

        data = await fetch(page)

        yield data
```

Trong phần lớn trường hợp, Async Generator là lựa chọn dễ đọc hơn.

---

# 31. Ví dụ hoàn chỉnh: Async Pagination

Ta xây dựng một API giả lập.

```python
import asyncio


async def fetch_page(page: int):

    await asyncio.sleep(0.2)

    if page > 5:
        return []

    return [
        f"item-{page}-1",
        f"item-{page}-2",
        f"item-{page}-3",
    ]
```

Async Generator:

```python
async def fetch_items():

    page = 1

    while True:

        items = await fetch_page(page)

        if not items:
            break

        for item in items:
            yield item

        page += 1
```

Consumer:

```python
async def main():

    async for item in fetch_items():

        print("Received:", item)


asyncio.run(main())
```

Kết quả:

```text
Received: item-1-1
Received: item-1-2
Received: item-1-3
Received: item-2-1
...
```

Điểm quan trọng:

**Không cần tải toàn bộ 15 item vào một List trước khi bắt đầu xử lý.**

---

# 32. Async Iterator trong crawler thực tế

Kiến trúc có thể là:

```text
                    ┌──────────────┐
                    │ URL Source   │
                    └──────┬───────┘
                           │
                    Async Iterator
                           │
                           ▼
                    ┌──────────────┐
                    │ Downloader   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Parser       │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Validator    │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Repository   │
                    └──────────────┘
```

Mỗi tầng có thể là một Async Generator.

Đây chính là nền tảng để sau này xây dựng:

```text
crawl-worker
```

mà bạn đang hướng tới.

---

# 33. Một nguyên tắc kiến trúc quan trọng

Khi thiết kế thư viện, đừng khóa API vào:

```python
list[Chapter]
```

Nếu dữ liệu có thể lớn, hãy cân nhắc:

```python
AsyncIterator[Chapter]
```

Ví dụ:

```python
async def crawl_chapters() -> AsyncIterator[Chapter]:
    ...
```

Consumer:

```python
async for chapter in crawl_chapters():
    await repository.save(chapter)
```

Lợi ích:

* Không giữ toàn bộ chapter trong RAM.
* Có thể streaming.
* Có thể xử lý từng item.
* Có thể dừng sớm.
* Dễ kết hợp với queue.
* Phù hợp crawler lớn.

---

# 34. `AsyncIterable` và `AsyncIterator`

Trong type hint, cần phân biệt:

```python
AsyncIterable[T]
```

và:

```python
AsyncIterator[T]
```

`AsyncIterable` có thể truyền cho:

```python
aiter()
```

Còn `AsyncIterator` phải có:

```python
__aiter__()
__anext__()
```

Ví dụ:

```python
from collections.abc import AsyncIterator


async def numbers() -> AsyncIterator[int]:

    for i in range(10):
        yield i
```

Đây là cách type hint rất tốt cho Async Generator.

---

# 35. Mental Model

Sau buổi hôm nay, hãy ghi nhớ mô hình:

```text
Iterable
    │
    ├── Iterator
    │      │
    │      └── next()
    │
    └── AsyncIterable
           │
           └── AsyncIterator
                  │
                  └── await __anext__()
```

Generator:

```text
Generator
    ↓
Iterator
```

Async Generator:

```text
Async Generator
    ↓
Async Iterator
```

---

# Bài tập

## Bài 1 — Async Counter

Viết:

```python
async def counter(limit):
    ...
```

Yêu cầu:

* Sinh từ `0 → limit - 1`.
* Mỗi lần `yield` chờ `0.5` giây.
* Sử dụng:

```python
async for
```

để đọc dữ liệu.

---

## Bài 2 — Async Pagination

Tạo:

```python
async def fetch_page(page):
    ...
```

Giả lập API:

```text
page 1 → 3 item
page 2 → 3 item
page 3 → 3 item
page 4 → []
```

Sau đó xây dựng:

```python
async def fetch_all_items():
    ...
```

Hàm này phải trả về từng item bằng `yield`, không tạo một List chứa toàn bộ dữ liệu.

---

## Bài 3 — Async Infinite Event Stream

Viết:

```python
async def events():
    ...
```

Sinh event vô hạn:

```python
{
    "id": 1,
    "type": "CLICK"
}
```

Mỗi event cách nhau `0.2` giây.

Consumer chỉ nhận **20 event đầu tiên** rồi dừng.

---

## Bài 4 — Crawler Pipeline

Xây dựng pipeline:

```text
async_generate_urls()
        ↓
async_download()
        ↓
async_parse()
        ↓
async_save()
```

Mỗi tầng phải sử dụng:

```python
async for
```

và:

```python
async yield
```

**Lưu ý:** Python không có cú pháp `async yield`; cú pháp đúng là `yield` bên trong `async def`.

Mục tiêu cuối cùng:

```python
async for item in pipeline():
    ...
```

và toàn bộ pipeline phải hoạt động theo kiểu:

```text
Async
+
Lazy
+
Streaming
```

---

# Tổng kết Buổi 20

Bạn cần nắm chắc các thành phần sau:

```text
__aiter__()
__anext__()
StopAsyncIteration
async for
aiter()
anext()
async def + yield
Async Generator
AsyncIterable
AsyncIterator
```

Và đặc biệt hiểu được chuỗi:

```text
Generator
    ↓
Iterator
    ↓
Lazy Evaluation
```

được mở rộng thành:

```text
Async Generator
    ↓
Async Iterator
    ↓
Async Lazy Evaluation
    ↓
Streaming
```

Đây chính là nền tảng để bước sang **Buổi 21 — Performance**, nơi chúng ta sẽ đo thực tế **List vs Iterator vs Generator vs Async Iterator**, phân tích CPU, RAM, allocation, throughput, latency và tìm hiểu khi nào Iterator thực sự giúp chương trình nhanh hơn hoặc chỉ giúp tiết kiệm bộ nhớ.
