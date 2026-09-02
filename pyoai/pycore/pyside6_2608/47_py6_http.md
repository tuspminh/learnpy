# Buổi 47 — PySide6 + HTTP

Hôm nay chúng ta ghép 3 thứ đã học:

```text
PySide6
   +
asyncio
   +
HTTP
```

Mục tiêu cuối buổi:

```text
MainWindow
    │
    ▼
DownloadService
    │
    ▼
asyncio
    │
    ▼
httpx.AsyncClient
    │
    ▼
Internet
```

Đây là bước chuẩn bị trực tiếp cho **Buổi 48 — Mini Project: Download Manager**.

---

# 1. Bài toán thực tế

Ta muốn GUI có:

```text
┌─────────────────────────────────────────┐
│ URL                                     │
│ [ https://example.com/file.zip ] [GET] │
│                                         │
│ Status: Downloading...                  │
│ ████████████████░░░░░  75%              │
└─────────────────────────────────────────┘
```

Trong quá trình download:

* GUI không freeze
* có progress
* có timeout
* có error handling
* có cancellation
* có retry
* có thể chạy nhiều download đồng thời

---

# 2. Vì sao không dùng `requests` trực tiếp?

Sai:

```python
def download(url):
    response = requests.get(url)
```

Nếu gọi từ GUI thread:

```text
GUI Thread
    │
    ▼
requests.get()
    │
    │
    │ 10 seconds
    │
    ▼
GUI
```

Trong 10 giây:

```text
❌ không repaint
❌ không click
❌ không scroll
❌ không phản hồi
```

---

# 3. Dùng `httpx.AsyncClient`

Ta có:

```python
import httpx
```

Async request:

```python
async with httpx.AsyncClient() as client:
    response = await client.get(url)
```

Mental model:

```text
asyncio
   │
   ▼
httpx.AsyncClient
   │
   ▼
await network I/O
   │
   ▼
asyncio làm việc khác
```

---

# 4. HTTP Client nên được tái sử dụng

Không nên:

```python
async def fetch(url):

    async with httpx.AsyncClient() as client:
        ...
```

cho hàng nghìn request nếu bạn muốn một client sống lâu.

Tốt hơn:

```text
DownloadService
      │
      ▼
AsyncClient
      │
 ┌────┼────┐
 ▼    ▼    ▼
Req1 Req2 Req3
```

Lợi ích:

* connection pooling
* keep-alive
* giảm overhead
* quản lý connection tập trung

---

# 5. `DownloadService`

Bắt đầu từ abstraction:

```python
class DownloadService:

    async def fetch(self, url: str) -> bytes:
        ...
```

GUI không cần biết:

```text
httpx
socket
TCP
HTTP
```

GUI chỉ biết:

```python
result = await service.fetch(url)
```

---

# 6. Nhưng DownloadService không nên điều khiển GUI

Không làm:

```python
class DownloadService:

    async def fetch(self, url):
        self.progress_bar.setValue(...)
```

Sai architecture.

Service chỉ phát:

```text
result
progress
error
```

GUI nhận và hiển thị.

---

# 7. HTTP Status Code

Response:

```python
response.status_code
```

Ví dụ:

```text
200 → OK
404 → Not Found
403 → Forbidden
500 → Server Error
```

Có thể:

```python
response.raise_for_status()
```

Nếu status không thành công:

```text
httpx.HTTPStatusError
```

---

# 8. Timeout

HTTP request không nên chạy vô hạn.

Ví dụ:

```python
timeout = httpx.Timeout(10.0)
```

Sau đó:

```python
async with httpx.AsyncClient(
    timeout=timeout
) as client:
    ...
```

Có thể phân biệt:

```python
httpx.Timeout(
    connect=5.0,
    read=10.0,
    write=10.0,
    pool=5.0,
)
```

Mental model:

```text
connect timeout
      ↓
TCP connection

read timeout
      ↓
đọc response

write timeout
      ↓
gửi request

pool timeout
      ↓
chờ connection
```

---

# 9. Exception quan trọng

HTTP client có thể gặp:

```text
httpx.ConnectError
httpx.TimeoutException
httpx.HTTPStatusError
httpx.RequestError
```

Ví dụ:

```python
try:

    response = await client.get(url)

    response.raise_for_status()

except httpx.TimeoutException:
    ...

except httpx.HTTPStatusError:
    ...

except httpx.RequestError:
    ...
```

---

# 10. Không nên bắt `Exception` quá sớm

Tránh:

```python
try:
    ...
except Exception:
    print("Error")
```

vì bạn mất thông tin loại lỗi.

Tốt hơn:

```python
except httpx.TimeoutException:
    ...
```

và:

```python
except httpx.HTTPStatusError:
    ...
```

---

# 11. Download file lớn

Đây là điểm rất quan trọng.

Không nên:

```python
data = await client.get(url)
content = data.content
```

với file:

```text
1 GB
```

vì bạn có thể đưa toàn bộ dữ liệu vào RAM.

Thay vào đó:

```text
HTTP
 │
 ▼
stream
 │
 ├── chunk
 ├── chunk
 ├── chunk
 └── chunk
       │
       ▼
      file
```

---

# 12. HTTP Streaming

Với HTTPX:

```python
async with client.stream(
    "GET",
    url,
) as response:

    response.raise_for_status()

    async for chunk in response.aiter_bytes():
        ...
```

Đây là pattern cốt lõi của Download Manager.

---

# 13. Ghi chunk xuống file

Ví dụ:

```python
async with client.stream(
    "GET",
    url,
) as response:

    response.raise_for_status()

    with open(path, "wb") as file:

        async for chunk in response.aiter_bytes():

            file.write(chunk)
```

Nhưng có một vấn đề:

```python
file.write()
```

là synchronous I/O.

Với file lớn, ta có thể cân nhắc:

```python
await asyncio.to_thread(
    file.write,
    chunk,
)
```

Tuy nhiên không phải lúc nào cũng cần. File I/O local thường khá nhanh; việc đẩy từng chunk qua thread cũng có overhead.

---

# 14. Content-Length

Server có thể trả:

```text
Content-Length: 104857600
```

Ta lấy:

```python
total = response.headers.get(
    "Content-Length"
)
```

Ví dụ:

```python
total = int(
    response.headers.get(
        "Content-Length",
        0,
    )
)
```

---

# 15. Tính progress

Mỗi chunk:

```python
downloaded += len(chunk)
```

Sau đó:

```python
percent = (
    downloaded * 100 // total
)
```

GUI:

```text
Downloaded: 75 MB
Total:      100 MB

Progress: 75%
```

---

# 16. Progress theo bytes tốt hơn

Không nên chỉ:

```text
10%
20%
30%
```

Ta có:

```text
downloaded
total
```

Ví dụ:

```python
progress.emit(
    downloaded,
    total,
)
```

GUI tự tính:

```python
percent = downloaded * 100 // total
```

Điều này linh hoạt hơn.

---

# 17. Signal

Ta thiết kế:

```python
class DownloadSignals(QObject):

    progress = Signal(int, int)
    finished = Signal(str)
    error = Signal(object)
```

Trong đó:

```text
progress(downloaded, total)
```

---

# 18. Nhưng concurrent download cần `download_id`

Giả sử:

```text
file A
file B
file C
```

Nếu chỉ:

```python
progress = Signal(int, int)
```

GUI không biết progress thuộc file nào.

Vì vậy:

```python
progress = Signal(
    int,  # download_id
    int,  # downloaded
    int,  # total
)
```

Ví dụ:

```python
self.signals.progress.emit(
    101,
    downloaded,
    total,
)
```

---

# 19. Download ID

Mental model:

```text
DownloadManager
 │
 ├── 101 → fileA.zip
 ├── 102 → fileB.zip
 └── 103 → fileC.zip
```

Signal:

```text
progress(
    102,
    50MB,
    100MB
)
```

GUI biết:

```text
Download 102
    ↓
update row 102
```

---

# 20. Download Engine

Ta có thể thiết kế:

```python
class DownloadEngine:

    async def download(
        self,
        download_id: int,
        url: str,
        path: str,
    ):
        ...
```

Nó không biết GUI.

---

# 21. Async Download Engine

Khung:

```python
class DownloadEngine:

    def __init__(self):
        self.client = httpx.AsyncClient()

    async def download(
        self,
        download_id,
        url,
        path,
    ):

        async with self.client.stream(
            "GET",
            url,
        ) as response:

            response.raise_for_status()

            total = int(
                response.headers.get(
                    "Content-Length",
                    0,
                )
            )

            downloaded = 0

            with open(path, "wb") as file:

                async for chunk in response.aiter_bytes():

                    file.write(chunk)

                    downloaded += len(chunk)
```

---

# 22. Thêm progress callback

Một cách đơn giản:

```python
async def download(
    self,
    download_id,
    url,
    path,
    on_progress,
):
```

Sau mỗi chunk:

```python
on_progress(
    download_id,
    downloaded,
    total,
)
```

Nhưng trong kiến trúc PySide6, ta thích:

```text
Signal
```

hơn callback GUI trực tiếp.

---

# 23. Service + Signal

Ví dụ:

```python
class DownloadService(QObject):

    progress = Signal(int, int, int)
    finished = Signal(int, str)
    error = Signal(int, object)
```

Trong coroutine:

```python
self.progress.emit(
    download_id,
    downloaded,
    total,
)
```

---

# 24. Một điểm rất quan trọng

`Signal.emit()` từ worker thread có thể được Qt chuyển đến GUI thread khi kết nối theo cơ chế queued connection.

Mental model:

```text
async worker
     │
     │ emit
     ▼
Qt Signal
     │
     ▼
GUI event loop
     │
     ▼
slot
```

Do đó:

```python
@Slot(int, int, int)
def on_progress(
    self,
    download_id,
    downloaded,
    total,
):
    ...
```

có thể cập nhật UI tại GUI side.

---

# 25. Cancellation

Người dùng nhấn:

```text
[ Cancel ]
```

Ta cần:

```text
GUI
 │
 ▼
DownloadManager.cancel(id)
 │
 ▼
asyncio.Task.cancel()
```

---

# 26. Lưu các task

```python
self.tasks = {}
```

Khi bắt đầu:

```python
task = asyncio.create_task(
    self.download(...)
)

self.tasks[download_id] = task
```

Sau đó:

```python
task.cancel()
```

---

# 27. Xử lý cancellation

Trong coroutine:

```python
try:

    ...

except asyncio.CancelledError:

    raise
```

Thông thường nên để cancellation tiếp tục lan truyền, thay vì nuốt exception.

Cuối cùng:

```python
finally:
    self.tasks.pop(
        download_id,
        None,
    )
```

---

# 28. Retry

Network có thể lỗi tạm thời.

Ví dụ:

```text
attempt 1 → timeout
attempt 2 → timeout
attempt 3 → success
```

Ta viết:

```python
for attempt in range(3):

    try:
        return await download()

    except httpx.RequestError:

        if attempt == 2:
            raise

        await asyncio.sleep(1)
```

---

# 29. Exponential Backoff

Tốt hơn:

```python
delay = 2 ** attempt
```

Kết quả:

```text
attempt 1 → 1s
attempt 2 → 2s
attempt 3 → 4s
```

Có thể thêm jitter trong hệ thống thực tế để tránh nhiều client retry cùng lúc.

---

# 30. Retry không phải lỗi nào cũng retry

Ví dụ:

```text
500 → có thể retry
502 → có thể retry
503 → có thể retry
```

Nhưng:

```text
400
401
403
404
```

thường không nên retry mù quáng.

Đặc biệt:

```text
404 Not Found
```

retry không làm file xuất hiện.

---

# 31. Concurrent Downloads

Ta có:

```python
async def download_many(urls):
    tasks = [
        download(url)
        for url in urls
    ]

    return await asyncio.gather(
        *tasks
    )
```

Nhưng phải giới hạn concurrency.

---

# 32. Semaphore

Ví dụ:

```python
self.semaphore = asyncio.Semaphore(4)
```

Trong download:

```python
async with self.semaphore:
    await self.download(...)
```

Kết quả:

```text
100 downloads
       │
       ▼
Semaphore(4)
       │
 ┌─────┼─────┐
 ▼     ▼     ▼
 D1    D2    D3 ...
```

Chỉ 4 download được phép chạy trong vùng giới hạn.

---

# 33. Connection Pool

`httpx.AsyncClient` cũng có connection pool.

Có thể cấu hình:

```python
limits = httpx.Limits(
    max_connections=10,
    max_keepalive_connections=5,
)
```

Sau đó:

```python
client = httpx.AsyncClient(
    limits=limits
)
```

Ta có hai lớp kiểm soát:

```text
Application
    │
    ▼
Semaphore
    │
    ▼
HTTPX connection pool
```

---

# 34. User-Agent

Một HTTP client thực tế thường gửi:

```python
headers = {
    "User-Agent": "MyDownloader/1.0"
}
```

Ví dụ:

```python
client = httpx.AsyncClient(
    headers=headers
)
```

Không nên giả mạo danh tính trình duyệt một cách tùy tiện; hãy dùng User-Agent mô tả ứng dụng của mình khi phù hợp.

---

# 35. Redirect

HTTP có:

```text
301
302
307
308
```

HTTPX có thể cấu hình redirect:

```python
client = httpx.AsyncClient(
    follow_redirects=True
)
```

Đây thường là điều bạn muốn khi download file từ URL chuyển hướng.

---

# 36. Response Headers

Một download manager thực tế có thể quan tâm:

```text
Content-Length
Content-Type
Content-Disposition
ETag
Last-Modified
Accept-Ranges
```

Ví dụ:

```python
content_type = response.headers.get(
    "Content-Type"
)
```

---

# 37. Filename

URL:

```text
https://example.com/files/book.zip
```

Có thể lấy:

```text
book.zip
```

nhưng URL không phải lúc nào cũng chứa filename.

Server có thể gửi:

```text
Content-Disposition
```

Ví dụ:

```text
attachment; filename="book.zip"
```

Một Download Manager tốt cần có chiến lược:

```text
Content-Disposition
       ↓
URL filename
       ↓
generated filename
```

---

# 38. Async HTTP + PySide6 Architecture

Đây là kiến trúc ta muốn đạt:

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
                  asyncio Tasks
                        │
                        ▼
                httpx.AsyncClient
                        │
                        ▼
                     HTTP
```

GUI không biết:

```text
httpx implementation
socket
asyncio internals
```

---

# 39. Nhưng asyncio chạy ở đâu?

Có hai lựa chọn kiến trúc.

### Cách 1

Asyncio loop nằm trong `QThread`.

```text
Qt Main Thread
     │
     ▼
    GUI

QThread
     │
     ▼
asyncio loop
     │
     ▼
httpx
```

### Cách 2

Tích hợp Qt event loop với asyncio bằng một bridge/event-loop integration.

Đối với giáo trình hiện tại, **Cách 1 giúp hiểu rõ boundary giữa GUI và async engine**.

---

# 40. Boundary

Hãy nhớ boundary:

```text
┌──────────────────────────────┐
│          GUI THREAD          │
│                              │
│ MainWindow                   │
│ QListView                    │
│ ProgressBar                  │
└──────────────┬───────────────┘
               │
             Signal
               │
┌──────────────▼───────────────┐
│       ASYNC WORKER           │
│                              │
│ asyncio Event Loop           │
│ DownloadManager              │
│ httpx.AsyncClient            │
└──────────────────────────────┘
```

Đây là một kiến trúc rất sạch.

---

# 41. Không để HTTP client tạo trong GUI rồi dùng tùy tiện

Không nên thiết kế:

```python
class MainWindow:
    client = httpx.AsyncClient()
```

rồi các thread/loop khác nhau cùng sử dụng nó.

Async client nên có lifecycle rõ ràng và được sử dụng trong đúng async context/loop mà nó thuộc về.

---

# 42. Lifecycle

Download service:

```text
create
  │
  ▼
start async loop
  │
  ▼
create AsyncClient
  │
  ▼
download tasks
  │
  ▼
cancel tasks
  │
  ▼
close AsyncClient
  │
  ▼
stop loop
```

Đây là lifecycle chuẩn cần nghĩ tới khi thiết kế production app.

---

# 43. `AsyncClient` phải được đóng

Nếu tạo:

```python
client = httpx.AsyncClient()
```

thì cuối cùng:

```python
await client.aclose()
```

Hoặc:

```python
async with httpx.AsyncClient() as client:
    ...
```

Với service sống lâu, thường dùng lifecycle:

```text
service.start()
service.close()
```

---

# 44. Error flow

Một request có thể:

```text
HTTP
 │
 ├── Success
 │
 ├── Timeout
 │
 ├── Connection Error
 │
 ├── HTTP Error
 │
 └── Cancelled
```

Không nên gom tất cả thành:

```text
"Download failed"
```

GUI nên có thông tin đủ để hiển thị:

```text
file.zip
Status: Failed
Reason: Timeout
```

---

# 45. Download State

Kết hợp với Buổi 32 — Application State, ta có:

```python
class DownloadStatus(Enum):

    PENDING = ...
    DOWNLOADING = ...
    COMPLETED = ...
    FAILED = ...
    CANCELLED = ...
```

Một download:

```text
PENDING
   │
   ▼
DOWNLOADING
   │
   ├── COMPLETED
   ├── FAILED
   └── CANCELLED
```

---

# 46. Download Model

Có thể tạo:

```python
@dataclass
class Download:

    id: int
    url: str
    path: str

    downloaded: int = 0
    total: int = 0

    status: DownloadStatus = (
        DownloadStatus.PENDING
    )
```

Bây giờ:

```text
Domain Model
     │
     ▼
Download
```

không phụ thuộc PySide6.

Đây chính là kiến thức từ **UI Architecture** chúng ta vừa học.

---

# 47. Application Architecture

Toàn bộ những gì đã học đang kết nối:

```text
presentation
     │
     ▼
application
     │
     ▼
domain
     │
     ▼
infrastructure
```

Ví dụ:

```text
MainWindow
    │
    ▼
DownloadController
    │
    ▼
DownloadService
    │
    ▼
DownloadEngine
    │
    ▼
httpx
```

---

# 48. Controller làm gì?

Buổi 28 chúng ta đã học Controller.

Khi user click:

```text
[Download]
```

GUI:

```python
self.controller.download(
    url
)
```

Controller:

```text
validate
   ↓
create Download
   ↓
service.start()
   ↓
update state
```

GUI không tự gọi `httpx`.

---

# 49. Mini Example Flow

User:

```text
Download
```

↓

```text
MainWindow
```

↓

```text
Controller
```

↓

```text
DownloadService
```

↓

```text
AsyncDownloadEngine
```

↓

```text
asyncio Task
```

↓

```text
httpx
```

↓

```text
Server
```

Response:

```text
Server
  ↓
httpx
  ↓
asyncio
  ↓
Signal
  ↓
Controller / State
  ↓
View
```

---

# 50. Đây là kiến trúc quan trọng

Đừng xây:

```text
MainWindow
    │
    ├── asyncio
    ├── httpx
    ├── file.write
    ├── retry
    ├── progress
    └── error handling
```

Sau vài nghìn dòng code sẽ thành:

```text
MainWindow.py
    3000 lines
```

Thay vào đó:

```text
presentation/
    main_window.py

application/
    download_controller.py
    download_service.py

domain/
    download.py

infrastructure/
    http/
        download_engine.py
```

---

# 51. Bài tập 1 — HTTP GET

Tạo PySide6 app:

```text
┌─────────────────────────────────┐
│ URL                             │
│ [____________________] [GET]   │
│                                 │
│ Status                          │
│                                 │
│ Response length:                │
└─────────────────────────────────┘
```

Click `GET`:

```python
await client.get(url)
```

Hiển thị:

```text
Status: 200
Length: 12345 bytes
```

---

# 52. Bài tập 2 — Timeout

Cho phép:

```text
Timeout: [ 10 ]
```

Test:

```text
timeout
connection error
successful request
```

GUI phải phân biệt:

```text
Timeout
Connection Error
HTTP Error
Success
```

---

# 53. Bài tập 3 — Streaming

Download một file lớn.

Không dùng:

```python
response.content
```

Mà:

```python
async with client.stream(...):
```

và:

```python
async for chunk in response.aiter_bytes():
```

---

# 54. Bài tập 4 — Progress

GUI:

```text
file.zip

████████████░░░░░░ 65%

65 MB / 100 MB
```

Signal:

```python
progress.emit(
    download_id,
    downloaded,
    total,
)
```

---

# 55. Bài tập 5 — Concurrent Download

Cho 5 URL:

```text
A
B
C
D
E
```

Cho phép tối đa:

```text
3 concurrent downloads
```

Dùng:

```python
asyncio.Semaphore(3)
```

---

# 56. Bài tập 6 — Cancellation

GUI:

```text
file.zip
████████░░░░ 40%

[Cancel]
```

Click:

```text
Cancel
```

↓

```python
task.cancel()
```

↓

```text
Cancelled
```

---

# 57. Bài tập 7 — Retry

Cho:

```text
Max retry: 3
```

Flow:

```text
Attempt 1
   ↓
Timeout
   ↓
wait 1s
   ↓
Attempt 2
   ↓
Timeout
   ↓
wait 2s
   ↓
Attempt 3
```

---

# 58. Bài tập 8 — Download Manager

Bắt đầu thiết kế project Buổi 48:

```text
┌────────────────────────────────────────────┐
│ Download Manager                           │
├────────────────────────────────────────────┤
│ URL                                        │
│ [____________________________] [Download]  │
├────────────────────────────────────────────┤
│ File       Status       Progress           │
│                                            │
│ A.zip      Downloading  ███████░ 70%       │
│ B.zip      Completed    ██████████ 100%     │
│ C.zip      Pending      ░░░░░░░░░ 0%        │
│ D.zip      Failed      Error               │
├────────────────────────────────────────────┤
│ Active: 1   Completed: 1   Failed: 1       │
└────────────────────────────────────────────┘
```

---

# 59. Checklist Buổi 47

Sau buổi này bạn cần hiểu được:

```text
✓ httpx.AsyncClient
✓ async HTTP request
✓ HTTP timeout
✓ HTTP status
✓ exception handling
✓ streaming response
✓ aiter_bytes()
✓ Content-Length
✓ progress theo bytes
✓ concurrent downloads
✓ Semaphore
✓ cancellation
✓ retry
✓ backoff
✓ connection pool
✓ AsyncClient lifecycle
✓ Signal → GUI
```

Và quan trọng nhất:

```text
GUI
 │
 │ Signal
 ▼
Application
 │
 ▼
Async Service
 │
 ▼
asyncio
 │
 ▼
httpx
 │
 ▼
HTTP
```

---

# 60. Mental Model cuối buổi

Toàn bộ **Phần IV** hiện tại có thể nhìn như sau:

```text
                       PySide6 GUI
                            │
                            ▼
                    Application Layer
                            │
             ┌──────────────┴──────────────┐
             │                             │
       Thread-based                   Async-based
             │                             │
             ▼                             ▼
        QThreadPool                    asyncio
             │                             │
         QRunnable                    coroutine
             │                             │
             ▼                             ▼
      blocking I/O                   httpx async
             │                             │
             └──────────────┬──────────────┘
                            ▼
                         Signals
                            │
                            ▼
                           GUI
```

Và **Buổi 48** sẽ là lúc ghép tất cả thành một ứng dụng hoàn chỉnh:

```text
                    Download Manager
                           │
              ┌────────────┴────────────┐
              │                         │
          MainWindow              Download Model
              │                         │
              ▼                         │
        Controller                      │
              │                         │
              ▼                         │
       DownloadService ◄────────────────┘
              │
              ▼
      AsyncDownloadEngine
              │
              ▼
           asyncio
              │
              ▼
       httpx.AsyncClient
              │
              ▼
           Internet
```

**Buổi 48 — Download Manager** sẽ tập trung vào việc ghép `QTableView/Model`, `Signal`, `asyncio`, `httpx`, progress từng file, concurrent limit, cancel, retry và trạng thái `Pending/Downloading/Completed/Failed/Cancelled` thành một project có kiến trúc tương đối production-style.
