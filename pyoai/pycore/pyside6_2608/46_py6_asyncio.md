# Buổi 46 — PySide6 + `asyncio`

Đây là một trong những buổi quan trọng nhất của phần **Threading & Concurrency**.

Ở các buổi trước, ta có:

```text
Buổi 38 → QThread
Buổi 39 → Worker Object
Buổi 40 → Signal
Buổi 43 → QThreadPool
Buổi 44 → QRunnable
Buổi 45 → Concurrent Tasks
```

Hôm nay thêm:

```text
Python asyncio
```

Mục tiêu không chỉ là biết `asyncio`, mà phải hiểu:

> **Qt Event Loop và asyncio Event Loop khác nhau thế nào, và làm sao phối hợp chúng trong một ứng dụng PySide6.**

---

# 1. Bài toán

Giả sử app của chúng ta cần gọi HTTP:

```text
GUI
 │
 ├── GET URL 1
 ├── GET URL 2
 ├── GET URL 3
 └── GET URL 4
```

Nếu viết:

```python
response = requests.get(url)
```

trực tiếp trong GUI thread:

```text
GUI Thread
    │
    ▼
requests.get()
    │
    │ 2 giây
    ▼
GUI tiếp tục
```

GUI bị:

```text
FREEZE
```

---

# 2. Với QThreadPool

Ta có:

```text
GUI
 │
 ▼
QThreadPool
 │
 ├── HTTP 1
 ├── HTTP 2
 ├── HTTP 3
 └── HTTP 4
```

Đây là cách hoàn toàn hợp lý.

Nhưng Python có một mô hình khác:

```text
asyncio
```

Ta có thể viết:

```python
async def fetch(url):
    ...
```

và:

```python
await fetch(url)
```

---

# 3. asyncio hoạt động như thế nào?

Mental model:

```text
asyncio Event Loop
       │
       ├── Task A
       ├── Task B
       ├── Task C
       └── Task D
```

Các task chủ yếu là:

> **cooperative concurrency**

Ví dụ:

```python
async def task():
    await asyncio.sleep(2)
```

Khi task gặp:

```python
await
```

nó nhường quyền điều khiển cho event loop.

---

# 4. Qt cũng có Event Loop

PySide6:

```python
app = QApplication(sys.argv)

app.exec()
```

`app.exec()` chạy:

```text
Qt Event Loop
```

Mental model:

```text
QApplication
     │
     ▼
Qt Event Loop
     │
     ├── Mouse events
     ├── Keyboard events
     ├── Signals
     ├── Timers
     └── Paint events
```

Trong khi asyncio có:

```text
asyncio Event Loop
     │
     ├── Task A
     ├── Task B
     ├── Task C
     └── Socket events
```

---

# 5. Vấn đề lớn

Một thread không nên đồng thời chạy hai event loop độc lập:

```text
GUI Thread
 │
 ├── Qt Event Loop
 │
 └── asyncio Event Loop
```

Nếu thiết kế sai, chúng có thể tranh quyền điều khiển.

Ví dụ:

```python
app.exec()

asyncio.run(main())
```

Không phải cách phối hợp đúng cho một GUI app.

---

# 6. `asyncio.run()` là gì?

Ví dụ console app:

```python
import asyncio


async def main():
    await asyncio.sleep(1)
    print("Hello")


asyncio.run(main())
```

`asyncio.run()`:

```text
create event loop
       ↓
run coroutine
       ↓
close event loop
```

Nó phù hợp với:

```text
CLI
script
one-shot program
```

nhưng không nên đơn giản nhét:

```python
asyncio.run(...)
```

vào callback GUI cho mỗi lần click.

---

# 7. Sai lầm phổ biến

Ví dụ:

```python
def on_click(self):

    asyncio.run(
        download()
    )
```

Nếu `download()` mất 10 giây:

```text
GUI callback
     │
     ▼
asyncio.run()
     │
     ▼
BLOCK
     │
     ▼
GUI FREEZE
```

`asyncio` không tự động làm GUI responsive.

Đây là insight rất quan trọng:

> **`async` không đồng nghĩa với background thread.**

---

# 8. `asyncio` không tạo thread

Ví dụ:

```python
async def download():
    await asyncio.sleep(5)
```

Không có nghĩa:

```text
Thread 1
```

được tạo.

Thường vẫn là:

```text
1 thread
1 event loop
n async tasks
```

```text
Thread
  │
  ▼
asyncio loop
  ├── Task A
  ├── Task B
  └── Task C
```

---

# 9. Vậy PySide6 + asyncio có những mô hình nào?

Có 3 hướng chính:

### Pattern A

```text
Qt GUI Thread
     │
     ▼
QThread
     │
     ▼
asyncio Event Loop
```

### Pattern B

```text
Qt Event Loop
     +
asyncio Event Loop
```

được tích hợp bằng thư viện bridge.

### Pattern C

```text
Qt GUI
   │
   ▼
QThreadPool
   │
   ▼
asyncio.run(...)
```

Mỗi worker thread chạy một async operation/event loop riêng.

Trong giáo trình này, ta sẽ hiểu **A/C trước**, vì chúng giúp hiểu bản chất rất rõ.

---

# 10. Pattern A — asyncio trong QThread

Kiến trúc:

```text
                    GUI
                     │
                     ▼
                   QThread
                     │
                     ▼
              asyncio Event Loop
                     │
              ┌──────┼──────┐
              ▼      ▼      ▼
            Task A Task B Task C
```

GUI vẫn thuộc:

```text
Qt main thread
```

asyncio nằm trong:

```text
worker thread
```

---

# 11. Ví dụ Worker

```python
class AsyncWorker(QObject):

    finished = Signal(object)
    error = Signal(object)

    @Slot()
    def run(self):

        try:
            result = asyncio.run(
                self.main()
            )

            self.finished.emit(result)

        except Exception as e:
            self.error.emit(e)

    async def main(self):

        await asyncio.sleep(2)

        return "Done"
```

Sau đó worker chạy trong:

```python
QThread
```

---

# 12. Nhưng có một điểm quan trọng

Không nên mỗi lần chạy task lại:

```python
asyncio.run(...)
```

nếu bạn muốn một worker sống lâu và quản lý nhiều async task.

Tốt hơn:

```text
QThread
   │
   ▼
asyncio loop
   │
   ├── Task A
   ├── Task B
   ├── Task C
   └── Task D
```

Tức là event loop được giữ sống.

---

# 13. Tạo asyncio loop

```python
loop = asyncio.new_event_loop()
```

Sau đó:

```python
asyncio.set_event_loop(loop)
```

và:

```python
loop.run_forever()
```

Mental model:

```text
QThread
  │
  └── asyncio loop
          │
          └── run_forever()
```

---

# 14. Async Worker Thread

Một ý tưởng:

```python
class AsyncWorker(QObject):

    def start_loop(self):
        self.loop = asyncio.new_event_loop()

        asyncio.set_event_loop(
            self.loop
        )

        self.loop.run_forever()
```

Thread:

```python
thread = QThread()

worker = AsyncWorker()

worker.moveToThread(thread)

thread.started.connect(
    worker.start_loop
)

thread.start()
```

Khi thread start:

```text
QThread
   │
   ▼
worker.start_loop()
   │
   ▼
asyncio loop
   │
   ▼
run_forever()
```

---

# 15. Gửi coroutine vào loop

Đây là API rất quan trọng:

```python
asyncio.run_coroutine_threadsafe()
```

Ví dụ:

```python
future = asyncio.run_coroutine_threadsafe(
    fetch(url),
    worker.loop,
)
```

Nó cho phép:

```text
Qt GUI Thread
      │
      │ submit coroutine
      ▼
asyncio Thread
      │
      ▼
asyncio Event Loop
```

---

# 16. Mental Model

```text
             Main GUI Thread
                    │
                    │ submit
                    ▼
          run_coroutine_threadsafe()
                    │
                    ▼
          asyncio Worker Thread
                    │
                    ▼
             asyncio loop
              /     |     \
             /      |      \
         Task A   Task B   Task C
```

Đây là pattern rất mạnh.

---

# 17. Ví dụ HTTP

Giả sử dùng `httpx`:

```python
import httpx


async def fetch(url):

    async with httpx.AsyncClient() as client:

        response = await client.get(url)

        return response.text
```

Ta có:

```text
GUI
 │
 ▼
submit coroutine
 │
 ▼
asyncio loop
 │
 ├── fetch(url1)
 ├── fetch(url2)
 └── fetch(url3)
```

---

# 18. Concurrent HTTP

Đây mới là sức mạnh của asyncio.

```python
async def fetch_all(urls):

    tasks = [
        fetch(url)
        for url in urls
    ]

    return await asyncio.gather(
        *tasks
    )
```

Ví dụ:

```text
URL 1 → 2s
URL 2 → 3s
URL 3 → 1s
```

Tuần tự:

```text
2 + 3 + 1 = 6s
```

Concurrent:

```text
max(2, 3, 1) ≈ 3s
```

---

# 19. `asyncio.gather()`

```python
results = await asyncio.gather(
    fetch(url1),
    fetch(url2),
    fetch(url3),
)
```

Mental model:

```text
             gather()
                │
        ┌───────┼───────┐
        ▼       ▼       ▼
      Task A  Task B  Task C
        │       │       │
        └───────┼───────┘
                ▼
             results
```

---

# 20. Nhưng `gather()` không giới hạn concurrency

Nếu:

```python
urls = 10000
```

mà:

```python
await asyncio.gather(
    *(fetch(url) for url in urls)
)
```

có thể tạo rất nhiều coroutine/tasks.

Không phải lúc nào cũng tốt.

---

# 21. Semaphore

Dùng:

```python
semaphore = asyncio.Semaphore(10)
```

Sau đó:

```python
async def fetch(url):

    async with semaphore:

        ...
```

Mental model:

```text
100 URLs
   │
   ▼
Semaphore(10)
   │
   ├── 10 running
   └── 90 waiting
```

Tương tự:

```python
QThreadPool.setMaxThreadCount(10)
```

nhưng cơ chế khác nhau.

---

# 22. So sánh QThreadPool và asyncio

| QThreadPool               | asyncio                  |
| ------------------------- | ------------------------ |
| Thread-based              | Event-loop-based         |
| `QRunnable`               | coroutine                |
| Thread                    | Task                     |
| `pool.start()`            | `create_task()`          |
| Thread concurrency        | cooperative concurrency  |
| tốt cho blocking I/O      | tốt cho async I/O        |
| CPU Python không lý tưởng | CPU Python không phù hợp |

---

# 23. Khi nào dùng QThreadPool?

Ví dụ thư viện blocking:

```python
requests
PIL
sqlite3
subprocess
```

Nếu function:

```python
def process():
    ...
```

blocking:

```text
QThreadPool
```

rất phù hợp.

---

# 24. Khi nào dùng asyncio?

Nếu thư viện hỗ trợ async:

```python
httpx.AsyncClient
aiohttp
aiosqlite
```

thì:

```text
asyncio
```

có thể hiệu quả hơn cho nhiều I/O tasks.

---

# 25. Không nên trộn bừa

Ví dụ:

```text
QThreadPool
    ↓
asyncio
    ↓
QThread
    ↓
asyncio
```

Không.

Architecture nên rõ ràng:

```text
GUI
 │
 ▼
Async Service
 │
 ▼
asyncio
```

hoặc:

```text
GUI
 │
 ▼
Worker
 │
 ▼
blocking library
```

---

# 26. Async Service

Đây là cách rất phù hợp với Architecture mà ta học ở Phần III.

Ví dụ:

```text
presentation
      │
      ▼
application service
      │
      ▼
async infrastructure
      │
      ▼
httpx.AsyncClient
```

GUI không cần biết:

```text
httpx
asyncio
event loop
```

---

# 27. Ví dụ kiến trúc

```text
MainWindow
    │
    ▼
DownloadService
    │
    ▼
AsyncDownloadEngine
    │
    ▼
asyncio
    │
    ▼
httpx
```

Signal:

```text
AsyncDownloadEngine
      │
      ├── progress
      ├── result
      ├── error
      └── finished
```

---

# 28. Async + Signal

Một async worker không nên:

```python
label.setText(...)
```

Thay vào đó:

```python
progress.emit(...)
```

GUI:

```python
worker.progress.connect(
    self.on_progress
)
```

Vẫn giữ nguyên nguyên tắc:

> **Worker không biết GUI.**

---

# 29. Async Task Cancellation

Asyncio có:

```python
task.cancel()
```

Ví dụ:

```python
task = asyncio.create_task(
    download()
)

task.cancel()
```

Coroutine cần xử lý:

```python
try:
    ...
except asyncio.CancelledError:
    ...
```

---

# 30. Kết hợp với GUI Cancel

GUI:

```text
[ Cancel ]
```

↓

```python
engine.cancel(task_id)
```

↓

```text
asyncio Task
      │
      ▼
task.cancel()
```

↓

```text
CancelledError
```

↓

```text
cancelled.emit(task_id)
```

↓

```text
GUI
```

Đây là kiến trúc rất đẹp cho Download Manager.

---

# 31. Timeout

Asyncio hỗ trợ:

```python
asyncio.timeout()
```

Ví dụ:

```python
async def fetch(url):

    async with asyncio.timeout(10):

        return await client.get(url)
```

Nếu quá:

```text
10 seconds
```

task bị timeout.

---

# 32. Retry

Asyncio rất thuận tiện để xây retry:

```python
async def fetch_with_retry(url):

    for attempt in range(3):

        try:
            return await fetch(url)

        except Exception:

            if attempt == 2:
                raise

            await asyncio.sleep(1)
```

Architecture:

```text
fetch
 │
 ├── attempt 1
 │
 ├── attempt 2
 │
 └── attempt 3
```

---

# 33. Đây cực kỳ phù hợp với crawler

Ví dụ Story Reader:

```text
20 chapters
```

Async:

```text
CrawlerService
       │
       ▼
asyncio
       │
 ┌─────┼─────┐
 ▼     ▼     ▼
C1    C2    C3 ...
```

Giới hạn:

```python
Semaphore(5)
```

Tức:

```text
5 chapter concurrent
```

---

# 34. Nhưng database thì sao?

Bạn đã học `sqlite3`.

Nếu dùng:

```python
sqlite3
```

thì đây là blocking API.

Không nên:

```python
async def save():
    sqlite3.connect(...)
```

rồi giả định nó trở thành async.

Nếu muốn async SQLite:

```text
aiosqlite
```

hoặc đưa blocking DB operation sang:

```text
QThreadPool
```

---

# 35. Hai thế giới

Có thể hình dung:

```text
                PySide6 Application
                       │
             ┌─────────┴─────────┐
             │                   │
          Blocking              Async
             │                   │
             ▼                   ▼
        QThreadPool           asyncio
             │                   │
             ▼                   ▼
        requests              httpx
        sqlite3              aiosqlite
        PIL                   aiofiles
```

Đây là mental model rất quan trọng.

---

# 36. Sai lầm #1

```python
async def foo():
    time.sleep(5)
```

Sai.

`time.sleep()` blocking.

Nó block:

```text
asyncio event loop
```

Dùng:

```python
await asyncio.sleep(5)
```

---

# 37. Sai lầm #2

```python
async def foo():
    requests.get(url)
```

`requests` là blocking.

Nếu chạy trực tiếp trong async loop:

```text
asyncio
  │
  ▼
requests.get()
  │
  ▼
BLOCK EVENT LOOP
```

Không tốt.

---

# 38. Nếu bắt buộc dùng blocking API?

Có thể:

```python
result = await asyncio.to_thread(
    blocking_function
)
```

Ví dụ:

```python
async def fetch(url):

    return await asyncio.to_thread(
        requests.get,
        url,
    )
```

Mental model:

```text
asyncio
   │
   ▼
to_thread()
   │
   ▼
thread
   │
   ▼
blocking function
```

Đây là cầu nối rất hữu ích.

---

# 39. `asyncio.to_thread()`

Nó đặc biệt hữu ích khi:

```text
API hiện tại = synchronous
```

nhưng bạn đang ở:

```text
asyncio
```

Ví dụ:

```python
async def process_file(path):

    result = await asyncio.to_thread(
        process_file_sync,
        path,
    )

    return result
```

---

# 40. Ba tầng concurrency

Sau Buổi 46, bạn nên nhìn PySide6 như:

```text
                  GUI
                   │
          ┌────────┴────────┐
          │                 │
      Thread-based       Async-based
          │                 │
      QThreadPool         asyncio
          │                 │
      QRunnable          coroutine
```

Và nếu CPU-bound:

```text
                  CPU-heavy
                      │
                      ▼
              ProcessPoolExecutor
```

---

# 41. Decision Tree

Khi có một task:

### Câu 1

Task có blocking không?

```text
YES
 ↓
QThread / QThreadPool
```

### Câu 2

Task là async I/O?

```text
YES
 ↓
asyncio
```

### Câu 3

Task CPU-heavy?

```text
YES
 ↓
ProcessPoolExecutor
```

---

# 42. Bài tập 1 — Async Counter

Tạo:

```python
async def worker(name):
    for i in range(10):
        await asyncio.sleep(0.5)
        print(name, i)
```

Chạy:

```python
await asyncio.gather(
    worker("A"),
    worker("B"),
    worker("C"),
)
```

Quan sát:

```text
A 0
B 0
C 0
A 1
B 1
C 1
...
```

---

# 43. Bài tập 2 — PySide6 + asyncio

Tạo GUI:

```text
┌──────────────────────────┐
│ Async Demo               │
│                          │
│ [ Start ]                │
│                          │
│ Status: Idle             │
└──────────────────────────┘
```

Click:

```text
Start
```

↓

async task:

```text
0
1
2
...
10
```

GUI vẫn responsive.

---

# 44. Bài tập 3 — Concurrent HTTP

Cho:

```text
URL 1
URL 2
URL 3
URL 4
URL 5
```

Dùng:

```text
httpx.AsyncClient
asyncio.gather()
```

GUI hiển thị:

```text
URL 1 ✓
URL 2 ✓
URL 3 ✓
URL 4 ✓
URL 5 ✓
```

---

# 45. Bài tập 4 — Semaphore

Có:

```text
100 URLs
```

Nhưng chỉ cho:

```text
5 requests concurrent
```

Dùng:

```python
semaphore = asyncio.Semaphore(5)
```

---

# 46. Bài tập 5 — Cancel

GUI:

```text
[ Start ]
[ Cancel ]
```

Khi Start:

```text
20 async tasks
```

Khi Cancel:

```text
cancel all tasks
```

GUI:

```text
Cancelled
```

---

# 47. Bài tập 6 — Download Manager mini

Đây là bài quan trọng nhất trước Buổi 47.

Thiết kế:

```text
MainWindow
     │
     ▼
DownloadManager
     │
     ▼
AsyncDownloadEngine
     │
     ▼
asyncio
     │
     ▼
httpx
```

GUI:

```text
┌─────────────────────────────────────┐
│ URL                                 │
│ [____________________] [Download]   │
├─────────────────────────────────────┤
│ file1.zip     ████████ 80%          │
│ file2.zip     ██████   60%          │
│ file3.zip     ███      30%          │
├─────────────────────────────────────┤
│ Active: 3                           │
└─────────────────────────────────────┘
```

---

# 48. Kiến trúc mục tiêu

Sau khi hoàn thành bài này:

```text
                  MainWindow
                      │
                      │ signals
                      ▼
               DownloadManager
                      │
                      ▼
              AsyncDownloadEngine
                      │
                      ▼
                 asyncio
                      │
              ┌───────┼───────┐
              ▼       ▼       ▼
            Task A  Task B  Task C
              │       │       │
              └───────┼───────┘
                      ▼
                    httpx
```

Đây chính là kiến trúc chúng ta sẽ tiếp tục hoàn thiện ở:

> **Buổi 47 — PySide6 + HTTP**

Ở Buổi 47, ta sẽ đi sâu vào **HTTP client trong GUI**, đặc biệt là `httpx`, timeout, streaming download, progress theo byte, retry, cancellation và cách thiết kế `DownloadService` sao cho sau này có thể ghép thẳng vào **Download Manager ở Buổi 48**.
