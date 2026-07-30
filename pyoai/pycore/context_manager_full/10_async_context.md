# Context Manager Deep Dive – Buổi 10

# Async Context Manager (`async with`, `__aenter__`, `__aexit__`)

> Đây là một trong những chủ đề quan trọng nhất nếu bạn muốn xây dựng:
> 
>   * Web crawler hiệu năng cao 
>   * API Server (FastAPI, aiohttp) 
>   * Async Database 
>   * Async HTTP Client 
>   * Async File Processing 
>   * Async Queue Worker 
> 


Đặc biệt, nó **liên quan trực tiếp** đến dự án **Story Crawler** mà bạn đang xây dựng.

* * *

# Mục tiêu

Sau buổi này bạn sẽ:

  * Hiểu Async Context Manager 
  * Hiểu `async with`
  * Hiểu `__aenter__`
  * Hiểu `__aexit__`
  * Biết cách hoạt động của `aiohttp`
  * Biết cách hoạt động của `aiosqlite`
  * Hiểu Connection Pool 
  * Biết Best Practices 



* * *

# 1\. Vì sao cần Async Context Manager?

Trong Python đồng bộ:
    
    
    with open("data.txt") as f:
        print(f.read())

Python gọi:
    
    
    __enter__()
    
    ↓
    
    code
    
    ↓
    
    __exit__()

* * *

Nhưng trong asyncio

Mọi thao tác có thể phải **chờ (await)**.

Ví dụ:
    
    
    Connect Database
    
    ↓
    
    Chờ
    
    ↓
    
    Connect HTTP
    
    ↓
    
    Chờ
    
    ↓
    
    Acquire Lock
    
    ↓
    
    Chờ

Không thể dùng
    
    
    __enter__()

được.

Python tạo thêm
    
    
    __aenter__()
    
    __aexit__()

* * *

# 2\. Cú pháp
    
    
    async with something:
        ...

Đây là phiên bản async của
    
    
    with something:

* * *

# 3\. Context Manager Async đầu tiên
    
    
    class AsyncDemo:
    
        async def __aenter__(self):
    
            print("Enter")
    
            return self
    
        async def __aexit__(
            self,
            exc_type,
            exc,
            tb
        ):
    
            print("Exit")

Sử dụng
    
    
    import asyncio
    
    
    async def main():
    
        async with AsyncDemo():
    
            print("Working")
    
    
    asyncio.run(main())

Output
    
    
    Enter
    
    Working
    
    Exit

* * *

# 4\. Python làm gì?
    
    
    async with obj as x:
        ...

tương đương gần như
    
    
    x = await obj.__aenter__()
    
    try:
    
        ...
    
    finally:
    
        await obj.__aexit__(...)

Đây là điểm khác biệt lớn nhất.

Mọi thứ đều có thể
    
    
    await

* * *

# 5\. Có thể chờ trong `__aenter__`

Ví dụ
    
    
    import asyncio
    
    
    class Demo:
    
        async def __aenter__(self):
    
            print("Connecting")
    
            await asyncio.sleep(1)
    
            print("Connected")
    
            return self
    
        async def __aexit__(self, *args):
    
            print("Disconnect")

Output
    
    
    Connecting
    
    (1 second)
    
    Connected
    
    ...
    
    Disconnect

Điều này không thể làm với `__enter__()`.

* * *

# 6\. Async HTTP

Ví dụ nổi tiếng nhất.
    
    
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
    
        ...

Bên trong
    
    
    __aenter__()
    
    ↓
    
    Open Session
    
    ↓
    
    HTTP Requests
    
    ↓
    
    __aexit__()
    
    ↓
    
    Close Session

* * *

# 7\. Async Request
    
    
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
    
        async with session.get(
            "https://example.com"
        ) as response:
    
            text = await response.text()
    
            print(text)

Quan sát

Có hai Context Manager
    
    
    Session
    
    ↓
    
    Response

* * *

Lifecycle
    
    
    Open Session
    
    ↓
    
    Send Request
    
    ↓
    
    Receive Response
    
    ↓
    
    Read
    
    ↓
    
    Close Response
    
    ↓
    
    Close Session

Đây là cách chuẩn khi dùng `aiohttp`.

* * *

# 8\. `aiosqlite`
    
    
    import aiosqlite
    
    async with aiosqlite.connect(
        "school.db"
    ) as db:
    
        await db.execute(
            "SELECT * FROM student"
        )

`aiosqlite.Connection` cũng là Async Context Manager.

* * *

# 9\. Async Lock
    
    
    import asyncio
    
    lock = asyncio.Lock()
    
    async with lock:
    
        print("Critical section")

Tương đương
    
    
    await lock.acquire()
    
    try:
    
        ...
    
    finally:
    
        lock.release()

* * *

# 10\. Async Semaphore
    
    
    sem = asyncio.Semaphore(5)
    
    async with sem:
    
        ...

Ý nghĩa
    
    
    Acquire
    
    ↓
    
    Run
    
    ↓
    
    Release

Rất quan trọng trong crawler.

Ví dụ
    
    
    1000 URLs
    
    ↓
    
    Semaphore(20)
    
    ↓
    
    Chỉ 20 request chạy đồng thời

* * *

# 11\. Story Crawler

Ví dụ
    
    
    async with Database() as db:
    
        async with HttpSession() as session:
    
            await crawl(session)

Lifecycle
    
    
    Connect DB
    
    ↓
    
    Open HTTP
    
    ↓
    
    Download
    
    ↓
    
    Save
    
    ↓
    
    Close HTTP
    
    ↓
    
    Close DB

* * *

# 12\. Async Transaction
    
    
    class Transaction:
    
        async def __aenter__(self):
    
            print("BEGIN")
    
            return self
    
        async def __aexit__(
            self,
            exc_type,
            exc,
            tb
        ):
    
            if exc_type:
    
                print("ROLLBACK")
    
            else:
    
                print("COMMIT")

* * *

# 13\. Async Timer
    
    
    import asyncio
    import time
    
    
    class Timer:
    
        async def __aenter__(self):
    
            self.start = time.perf_counter()
    
            return self
    
        async def __aexit__(self, *args):
    
            print(
                time.perf_counter() - self.start
            )
    
    
    async with Timer():
    
        await asyncio.sleep(2)

Output
    
    
    2.001

* * *

# 14\. Async Generator Context Manager

Giống hệt phiên bản sync.
    
    
    from contextlib import asynccontextmanager
    
    
    @asynccontextmanager
    async def timer():
    
        print("Start")
    
        try:
    
            yield
    
        finally:
    
            print("Stop")

Sử dụng
    
    
    async with timer():
    
        ...

* * *

# 15\. Async ExitStack

Python còn có
    
    
    from contextlib import AsyncExitStack

Ví dụ
    
    
    async with AsyncExitStack() as stack:
    
        session = await stack.enter_async_context(
            aiohttp.ClientSession()
        )
    
        db = await stack.enter_async_context(
            aiosqlite.connect("db.sqlite")
        )

Đây là phiên bản async của `ExitStack`.

* * *

# 16\. Connection Pool

Ví dụ
    
    
    100 requests
    
    ↓
    
    Pool
    
    ↓
    
    10 connections
    
    ↓
    
    Reuse

Thường
    
    
    async with pool.acquire() as conn:
    
        ...

Sau khi thoát

↓

Connection không bị đóng.

↓

Được trả lại Pool.

Đây là kỹ thuật được dùng trong:

  * asyncpg 
  * aiomysql 
  * aioredis 



* * *

# 17\. Nested Async Context
    
    
    async with Database():
    
        async with Http():
    
            async with Logger():
    
                ...

Hoặc
    
    
    async with (
        Database(),
        Http(),
        Logger(),
    ):
        ...

LIFO giống Context Manager đồng bộ.

* * *

# 18\. Best Practices

## Không dùng
    
    
    await connect()
    
    try:
    
        ...
    
    finally:
    
        await disconnect()

Nếu đối tượng đã hỗ trợ:
    
    
    async with ...

Hãy dùng `async with` để mã ngắn gọn và an toàn hơn.

* * *

## Session chỉ mở một lần

Sai
    
    
    for url in urls:
    
        async with ClientSession():

Mỗi lần lặp lại tạo một Session mới, rất tốn kém.

Đúng
    
    
    async with ClientSession() as session:
    
        for url in urls:
    
            ...

Một Session phục vụ nhiều request.

* * *

## Semaphore

Crawler
    
    
    10000 URLs
    
    ↓
    
    Semaphore
    
    ↓
    
    20 Workers

Không gửi hàng nghìn request cùng lúc.

* * *

# Ví dụ hoàn chỉnh
    
    
    import asyncio
    import aiohttp
    import time
    
    
    class Timer:
    
        async def __aenter__(self):
    
            self.start = time.perf_counter()
    
            return self
    
        async def __aexit__(self, *args):
    
            print(
                f"Elapsed: "
                f"{time.perf_counter()-self.start:.3f}s"
            )
    
    
    async def main():
    
        async with Timer():
    
            async with aiohttp.ClientSession() as session:
    
                async with session.get(
                    "https://example.com"
                ) as resp:
    
                    print(resp.status)
    
    
    asyncio.run(main())

Đây là phong cách mà bạn sẽ thấy trong rất nhiều dự án asyncio chuyên nghiệp.

* * *

# So sánh

Đồng bộ| Bất đồng bộ  
---|---  
`with`| `async with`  
`__enter__`| `__aenter__`  
`__exit__`| `__aexit__`  
`contextmanager`| `asynccontextmanager`  
`ExitStack`| `AsyncExitStack`  
  
* * *

# Áp dụng vào dự án Story Crawler

Trong dự án crawler của bạn, một kiến trúc bất đồng bộ có thể như sau:
    
    
    async with AsyncExitStack() as stack:
        session = await stack.enter_async_context(
            aiohttp.ClientSession()
        )
    
        db = await stack.enter_async_context(
            aiosqlite.connect("stories.db")
        )
    
        semaphore = asyncio.Semaphore(20)
    
        # Truyền session, db và semaphore cho các coroutine crawl

Ưu điểm:

  * Chỉ tạo **một** `ClientSession`. 
  * Chỉ mở **một** kết nối SQLite (hoặc một pool nếu dùng DB khác). 
  * Mọi tài nguyên đều được giải phóng đúng thứ tự khi kết thúc. 



* * *

# Bài tập

## Bài 1

Viết `AsyncTimer`.

Yêu cầu:

  * `__aenter__`
  * `__aexit__`
  * đo thời gian của: 


    
    
    await asyncio.sleep(2)

* * *

## Bài 2

Viết `AsyncLogger`.

Yêu cầu:
    
    
    START
    
    ↓
    
    await
    
    ↓
    
    END

Nếu có exception, ghi loại ngoại lệ trước khi để nó tiếp tục lan truyền.

* * *

## Bài 3

Viết `@asynccontextmanager`

Tên:
    
    
    connection()

Yêu cầu:
    
    
    CONNECT
    
    ↓
    
    yield
    
    ↓
    
    DISCONNECT

Đảm bảo `DISCONNECT` luôn được thực thi bằng `try...finally`.

* * *

## Bài 4 (Áp dụng cho Story Crawler)

Thiết kế hàm:
    
    
    async def crawl_source(source):
        ...

Yêu cầu:

  * Dùng `AsyncExitStack`. 
  * Mở: 
    * `aiohttp.ClientSession`
    * `AsyncLogger`
    * `AsyncTimer`
  * Giới hạn đồng thời bằng `asyncio.Semaphore`. 
  * Tải dữ liệu và lưu vào cơ sở dữ liệu (có thể mô phỏng bằng `await asyncio.sleep()` nếu chưa có phần lưu thực tế). 



* * *

# Tổng kết buổi 10

Đến đây, bạn đã làm chủ cả hai thế giới:

  * **Context Manager đồng bộ** (`with`, `__enter__`, `__exit__`). 
  * **Async Context Manager** (`async with`, `__aenter__`, `__aexit__`). 



Bạn cũng đã biết cách kết hợp chúng với:

  * `contextmanager`
  * `asynccontextmanager`
  * `ExitStack`
  * `AsyncExitStack`



Đây là nền tảng để xây dựng các ứng dụng Python hiện đại, đặc biệt là crawler, web service và các hệ thống I/O bất đồng bộ.

* * *

# Nhận xét về lộ trình

Đến buổi 10, bạn đã nắm được gần như **toàn bộ cơ chế cốt lõi** của Context Manager trong Python. Hai buổi cuối sẽ tập trung vào:

  * **Buổi 11:** Khảo sát các Context Manager quan trọng trong thư viện chuẩn và các thư viện phổ biến (`contextlib.suppress`, `nullcontext`, `closing`, `redirect_stdout`, `decimal.localcontext`, `tempfile`, ...), phân tích cách và khi nào nên dùng. 
  * **Buổi 12:** Xây dựng một **Resource Manager** hoàn chỉnh theo phong cách production, kết hợp những gì đã học (class-based, generator-based, `ExitStack`, async, transaction, logging...) để thiết kế một hệ thống quản lý tài nguyên có thể áp dụng trực tiếp vào các dự án như **Story Crawler** của bạn.

