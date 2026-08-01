# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 43: Pytest (Phần 15) – Async Testing với asyncio, pytest-asyncio, AsyncMock, WebSocket và hệ thống bất đồng bộ

> **Async programming là tiêu chuẩn của Python Backend hiện đại.**
>
> Nếu bạn sử dụng:
>
> * FastAPI
> * httpx
> * aiohttp
> * websockets
> * aiosqlite
> * asyncio
> * redis.asyncio
> * SQLAlchemy Async
>
> thì bạn **bắt buộc** phải biết cách kiểm thử mã bất đồng bộ.

Buổi này là một trong những buổi quan trọng nhất của toàn bộ phần Pytest.

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ:

* Hiểu cơ chế Async Testing.
* Thành thạo `pytest-asyncio`.
* Viết Unit Test cho coroutine.
* Viết Async Fixture.
* Mock Async Function bằng `AsyncMock`.
* Test `asyncio.Queue`.
* Test `asyncio.Task`.
* Test Timeout.
* Test Cancellation.
* Test WebSocket.
* Test FastAPI Async.
* Thiết kế Test cho Crawler bất đồng bộ.

---

# Roadmap

```text
Buổi 29–42
✓ Unit Testing
✓ Integration
✓ E2E
✓ Performance
✓ Security

Buổi 43
✓ Async Testing

Buổi 44
✓ Viết Plugin cho Pytest

Buổi 45
✓ Xây dựng Test Framework riêng
```

---

# Phần I

# Vì sao Async Test khác Unit Test?

Hàm bình thường:

```python
def add(a, b):
    return a + b
```

Test:

```python
def test_add():
    assert add(2, 3) == 5
```

---

Coroutine:

```python
async def add(a, b):
    return a + b
```

Không thể:

```python
assert add(2, 3) == 5
```

Vì:

```text
add()

↓

Coroutine Object
```

Muốn chạy:

```text
await add()
```

---

# Phần II

# pytest-asyncio

Cài đặt:

```bash
pip install pytest-asyncio
```

---

Ví dụ:

```python
async def add(a, b):

    return a + b
```

Test:

```python
import pytest


@pytest.mark.asyncio
async def test_add():

    result = await add(2, 3)

    assert result == 5
```

Pytest sẽ tự tạo Event Loop để chạy test.

---

# Phần III

# Async Fixture

Fixture cũng có thể là coroutine.

Ví dụ:

```python
import pytest_asyncio


@pytest_asyncio.fixture
async def database():

    db = await connect()

    yield db

    await db.close()
```

---

Test:

```python
@pytest.mark.asyncio
async def test_query(database):

    rows = await database.fetch()

    assert rows
```

---

Đây là cách chuẩn khi dùng:

* aiosqlite
* asyncpg
* redis.asyncio
* SQLAlchemy Async

---

# Phần IV

# AsyncMock

Python cung cấp:

```python
from unittest.mock import AsyncMock
```

Ví dụ:

```python
api = AsyncMock()

api.fetch.return_value = {"name": "Alice"}
```

---

Test:

```python
@pytest.mark.asyncio
async def test_fetch():

    result = await api.fetch()

    assert result["name"] == "Alice"
```

---

Kiểm tra:

```python
api.fetch.assert_awaited_once()
```

Khác với:

```python
assert_called_once()
```

---

# Phần V

# Mock Async Repository

Repository:

```python
class UserRepository:
    async def save(self, user): ...
```

---

Test:

```python
repo = AsyncMock()

repo.save.return_value = True
```

---

Service:

```python
await service.register()
```

---

Kiểm tra:

```python
repo.save.assert_awaited_once()
```

---

# Phần VI

# asyncio.Queue

Ví dụ Producer:

```python
await queue.put("chapter")
```

Consumer:

```python
item = await queue.get()
```

---

Test:

```python
@pytest.mark.asyncio
async def test_queue():

    q = asyncio.Queue()

    await q.put("python")

    result = await q.get()

    assert result == "python"
```

---

Ứng dụng:

Crawler.

```text
Downloader

↓

Queue

↓

Parser

↓

Repository
```

---

# Phần VII

# Test asyncio.Task

Ví dụ:

```python
task = asyncio.create_task(download())
```

---

Test:

```python
result = await task

assert result == "done"
```

---

Có thể kiểm tra:

```python
task.done()
```

hoặc:

```python
task.cancelled()
```

---

# Phần VIII

# Timeout Testing

Ví dụ:

```python
await asyncio.wait_for(download(), timeout=1)
```

---

Test:

```python
import asyncio

import pytest


@pytest.mark.asyncio
async def test_timeout():

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_task(), timeout=0.1)
```

---

Rất quan trọng đối với:

* HTTP.
* Redis.
* API.

---

# Phần IX

# Cancellation Testing

Task:

```python
task = asyncio.create_task(download())
```

---

Hủy:

```python
task.cancel()
```

---

Test:

```python
with pytest.raises(asyncio.CancelledError):
    await task
```

---

Ứng dụng:

Người dùng bấm:

```text
Stop Crawl
```

Task phải dừng đúng cách.

---

# Phần X

# Test Async HTTP

Ví dụ:

```python
import httpx
```

---

Client:

```python
async with httpx.AsyncClient() as client:
    response = await client.get(url)
```

---

Test:

Có thể mock:

```python
AsyncMock()
```

hoặc dùng thư viện chuyên dụng như `respx` để giả lập HTTP.

---

# Phần XI

# Test FastAPI Async

FastAPI:

```python
@app.get("/users")
async def users(): ...
```

---

Test:

```python
from httpx import AsyncClient

import pytest


@pytest.mark.asyncio
async def test_users(app):

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/users")

        assert response.status_code == 200
```

---

Đây là cách test chuẩn cho FastAPI.

---

# Phần XII

# Test WebSocket

Ví dụ:

```text
Client

↓

WebSocket

↓

Server
```

---

Test:

```python
async with websocket() as ws:
    await ws.send("hello")

    msg = await ws.receive()
```

---

Kiểm tra:

```python
assert msg == "hello"
```

---

Ứng dụng:

* Chat.
* Notification.
* Dashboard.

---

# Phần XIII

# Async Database Testing

Ví dụ:

```python
async with aiosqlite.connect(":memory:") as db:
    ...
```

---

Fixture:

```python
@pytest_asyncio.fixture
async def db(): ...
```

---

Test:

```python
await repo.save()
```

---

Integration Test:

```text
Repository

+

SQLite Async
```

---

# Phần XIV

# Test dự án Story Crawler

Kiến trúc:

```text
Downloader

↓

asyncio.Queue

↓

Parser

↓

Repository

↓

Redis
```

---

Unit:

Mock:

* Downloader.
* Redis.

---

Integration:

Test:

```text
Repository

+

SQLite
```

---

Async:

```text
Queue

↓

Producer

↓

Consumer
```

---

Benchmark:

```text
100 concurrent downloads
```

---

# Phần XV

# Sai lầm phổ biến

## 1. Quên await

Sai:

```python
result = download()
```

Đúng:

```python
result = await download()
```

---

## 2. Dùng Mock thay AsyncMock

Sai:

```python
repo = Mock()
```

Nếu phương thức là async thì nên dùng:

```python
repo = AsyncMock()
```

---

## 3. Không kiểm tra timeout

HTTP.

Database.

Redis.

MQ.

Đều nên có test timeout.

---

## 4. Không test cancellation

Ứng dụng:

Crawler.

Downloader.

Worker.

Đều phải test khả năng hủy tác vụ.

---

# Phần XVI

# Mini Project

Thiết kế test cho:

```text
Async Story Crawler

↓

httpx.AsyncClient

↓

asyncio.Queue

↓

Parser

↓

Repository

↓

Redis
```

Các test cần có:

* Downloader.
* Queue.
* Parser.
* Repository.
* Timeout.
* Cancellation.
* Retry.
* Redis.
* Integration.
* Benchmark.

---

# Bài tập

### Bài 1

Viết test:

```python
async def add(a,b)
```

---

### Bài 2

Tạo:

```python
AsyncMock
```

cho Repository.

---

### Bài 3

Test:

```python
asyncio.Queue
```

---

### Bài 4

Test:

```python
asyncio.wait_for()
```

---

### Bài 5

Thiết kế Async Test Suite cho dự án Story Crawler.

---

# Tổng kết Buổi 43

Bạn đã học:

* ✅ `pytest-asyncio`.
* ✅ Async Test.
* ✅ Async Fixture.
* ✅ `AsyncMock`.
* ✅ `asyncio.Queue`.
* ✅ `asyncio.Task`.
* ✅ Timeout Testing.
* ✅ Cancellation Testing.
* ✅ Async HTTP Testing.
* ✅ FastAPI Async Testing.
* ✅ WebSocket Testing.
* ✅ Async Database Testing.

---

# Góc nhìn Senior Python Developer

Trong các ứng dụng Python hiện đại:

* `asyncio` không còn là kiến thức nâng cao mà là **kỹ năng nền tảng**.
* Viết được mã `async` mới chỉ là bước đầu; **kiểm thử được mã `async`** mới giúp hệ thống ổn định khi chạy với hàng nghìn tác vụ đồng thời.

Một chiến lược kiểm thử tốt cho ứng dụng bất đồng bộ thường bao gồm:

```text
Unit Test
    │
Mock Async Dependencies
    │
Integration Test (Database/Redis/HTTP)
    │
Concurrency Test
    │
Timeout & Cancellation Test
    │
Performance Benchmark
```

Đó là nền tảng để xây dựng các hệ thống như crawler, API hiệu năng cao, xử lý nền và các dịch vụ thời gian thực.

---

# Chuẩn bị Buổi 44

**Pytest (Phần 16) – Phát triển Plugin cho Pytest và mở rộng hệ thống kiểm thử**

Chúng ta sẽ học:

* Kiến trúc plugin của Pytest.
* Hook System (`pytest_*` hooks).
* Tự tạo marker.
* Thêm command-line options.
* Thu thập và thay đổi test trong quá trình chạy.
* Sinh báo cáo tùy chỉnh.
* Chia sẻ plugin giữa nhiều dự án.
* Xây dựng một plugin hoàn chỉnh phục vụ dự án Python thực tế.

Đây là bước chuyển từ **người sử dụng Pytest** sang **người mở rộng và tùy biến Pytest**.
