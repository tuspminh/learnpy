# Buổi 48 — Mini Project: Download Manager

Hôm nay chúng ta **ghép toàn bộ Phần IV — Threading & Concurrency** thành một ứng dụng thực tế.

Mục tiêu không phải chỉ làm một nút "Download", mà là xây một **Download Manager có architecture rõ ràng**:

```text
                    ┌─────────────────────┐
                    │     MainWindow      │
                    │     PySide6 GUI      │
                    └──────────┬──────────┘
                               │
                         Controller
                               │
                               ▼
                    ┌─────────────────────┐
                    │   DownloadService   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ AsyncDownloadEngine │
                    └──────────┬──────────┘
                               │
                         asyncio Task
                               │
                               ▼
                    ┌─────────────────────┐
                    │   httpx.AsyncClient │
                    └──────────┬──────────┘
                               │
                               ▼
                            Internet
```

---

# 1. Yêu cầu của project

GUI:

```text
┌─────────────────────────────────────────────────────────────┐
│ Download Manager                                            │
├─────────────────────────────────────────────────────────────┤
│ URL                                                         │
│ [ https://example.com/file.zip                 ] [Download] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ File       Status          Progress       Action             │
│ ─────────────────────────────────────────────────────────── │
│ A.zip      Downloading     ███████░░░ 70% [Cancel]          │
│ B.zip      Completed       ██████████ 100%                  │
│ C.zip      Pending         ░░░░░░░░░░ 0%   [Cancel]         │
│ D.zip      Failed          Error                             │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Active: 2     Completed: 1     Failed: 1                   │
└─────────────────────────────────────────────────────────────┘
```

Chức năng:

```text
✓ Download
✓ Streaming
✓ Progress
✓ Multiple downloads
✓ Concurrent limit
✓ Cancel
✓ Retry
✓ Timeout
✓ Error handling
✓ GUI không freeze
✓ Signal-based communication
```

---

# 2. Architecture

Chúng ta sẽ dùng:

```text
presentation/
    main_window.py
    download_model.py

application/
    download_controller.py
    download_service.py

domain/
    download.py

infrastructure/
    http/
        async_download_engine.py

main.py
```

Dependency direction:

```text
Presentation
     │
     ▼
Application
     │
     ▼
Domain

Infrastructure
     ▲
     │
Application
```

Điểm quan trọng:

> Domain không biết PySide6, asyncio hay httpx.

---

# 3. Domain Model

Đầu tiên:

```python
# domain/download.py

from dataclasses import dataclass
from enum import Enum, auto


class DownloadStatus(Enum):
    PENDING = auto()
    DOWNLOADING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass
class Download:
    id: int
    url: str
    path: str

    downloaded: int = 0
    total: int = 0

    status: DownloadStatus = DownloadStatus.PENDING

    error: str | None = None

    @property
    def progress(self) -> int:
        if self.total <= 0:
            return 0

        return int(
            self.downloaded * 100 / self.total
        )
```

Đây chính là Domain Model.

Không có:

```python
QObject
Signal
QWidget
httpx
asyncio
```

---

# 4. Tại sao `Download` không phải QObject?

Không cần:

```python
class Download(QObject):
    ...
```

Domain object chỉ chứa business state:

```text
Download
 ├── id
 ├── url
 ├── path
 ├── downloaded
 ├── total
 └── status
```

UI state sẽ nằm ở presentation.

Đây là một nguyên tắc rất quan trọng khi xây application lớn.

---

# 5. HTTP Engine

Bây giờ xây tầng infrastructure.

```python
# infrastructure/http/async_download_engine.py

import asyncio
from pathlib import Path

import httpx


class AsyncDownloadEngine:

    def __init__(
        self,
        max_connections: int = 10,
    ):
        limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=5,
        )

        timeout = httpx.Timeout(
            connect=10.0,
            read=30.0,
            write=30.0,
            pool=10.0,
        )

        self.client = httpx.AsyncClient(
            follow_redirects=True,
            limits=limits,
            timeout=timeout,
        )

    async def download(
        self,
        url: str,
        path: str,
        on_progress,
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

            Path(path).parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with open(path, "wb") as file:

                async for chunk in response.aiter_bytes(
                    chunk_size=64 * 1024
                ):
                    if not chunk:
                        continue

                    file.write(chunk)

                    downloaded += len(chunk)

                    on_progress(
                        downloaded,
                        total,
                    )

            return downloaded, total

    async def close(self):
        await self.client.aclose()
```

---

# 6. Tại sao `64 * 1024`?

Ta dùng:

```python
chunk_size=64 * 1024
```

tức:

```text
64 KB
```

Không nên mặc định tải cả file vào RAM.

Sai:

```python
response = await client.get(url)

data = response.content
```

Với file 2 GB:

```text
RAM
└── 2 GB
```

Streaming:

```text
Network
   │
   ▼
64 KB
   │
   ▼
Disk
```

RAM chỉ cần giữ một chunk nhỏ.

---

# 7. Progress Callback

Engine không biết PySide6.

Nó chỉ biết:

```python
on_progress(
    downloaded,
    total,
)
```

Ví dụ:

```text
downloaded = 50 MB
total      = 100 MB
```

Engine:

```python
on_progress(
    50_000_000,
    100_000_000,
)
```

Application layer sẽ chuyển thông tin này thành Signal.

---

# 8. Download Service

Service quản lý nhiều download.

```python
# application/download_service.py

import asyncio

from domain.download import (
    Download,
    DownloadStatus,
)
from infrastructure.http.async_download_engine import (
    AsyncDownloadEngine,
)


class DownloadService:

    def __init__(
        self,
        engine: AsyncDownloadEngine,
        max_concurrent: int = 3,
    ):
        self.engine = engine

        self.semaphore = asyncio.Semaphore(
            max_concurrent
        )

        self.tasks: dict[int, asyncio.Task] = {}

    async def start(
        self,
        download: Download,
        on_progress,
    ):

        async with self.semaphore:

            download.status = (
                DownloadStatus.DOWNLOADING
            )

            try:

                downloaded, total = (
                    await self.engine.download(
                        download.url,
                        download.path,
                        on_progress,
                    )
                )

                download.downloaded = downloaded
                download.total = total

                download.status = (
                    DownloadStatus.COMPLETED
                )

            except asyncio.CancelledError:

                download.status = (
                    DownloadStatus.CANCELLED
                )

                raise

            except Exception as exc:

                download.status = (
                    DownloadStatus.FAILED
                )

                download.error = str(exc)

                raise
```

---

# 9. Semaphore

Đây là phần rất quan trọng.

Ta đặt:

```python
asyncio.Semaphore(3)
```

Nếu có:

```text
20 downloads
```

thì:

```text
Download 1 ─┐
Download 2  │
Download 3  │ → RUNNING
────────────┘

Download 4
Download 5
Download 6
...
             → WAITING
```

Khi một download kết thúc:

```text
Download 1 → completed

Download 4 → running
```

Như vậy chúng ta không mở 20 connection cùng lúc.

---

# 10. Vì sao `QThreadPool` không được dùng ở đây?

Ta đã học:

```text
QThread
QThreadPool
QRunnable
```

Nhưng download của chúng ta sử dụng:

```text
httpx.AsyncClient
```

nên mô hình phù hợp là:

```text
QThread
   │
   ▼
asyncio event loop
   │
   ▼
httpx.AsyncClient
```

thay vì:

```text
QThreadPool
   │
   ├── requests.get()
   ├── requests.get()
   └── requests.get()
```

---

# 11. Asyncio Worker Thread

Đây là phần khó nhất của project.

Qt có event loop:

```text
Qt Event Loop
```

Trong khi asyncio có:

```text
asyncio Event Loop
```

Ta không muốn:

```text
Qt Main Thread
     │
     ├── Qt event loop
     └── asyncio.run()
```

bởi `asyncio.run()` là một event loop riêng và không nên được dùng như một vòng lặp blocking trong GUI.

Ta tạo:

```text
Main Thread
    │
    └── Qt Event Loop

Worker Thread
    │
    └── asyncio Event Loop
```

---

# 12. Async Worker

```python
# infrastructure/async_worker.py

import asyncio

from PySide6.QtCore import QObject, Signal


class AsyncWorker(QObject):

    progress = Signal(
        int,
        int,
        int,
    )

    completed = Signal(
        int,
    )

    failed = Signal(
        int,
        str,
    )

    cancelled = Signal(
        int,
    )

    def __init__(
        self,
        service,
    ):
        super().__init__()

        self.service = service

        self.loop = asyncio.new_event_loop()

        self.tasks = {}

    def run(self):
        asyncio.set_event_loop(
            self.loop
        )

        try:
            self.loop.run_forever()

        finally:
            self.loop.run_until_complete(
                self.service.engine.close()
            )

            self.loop.close()
```

---

# 13. Schedule Coroutine

Ta cần đưa coroutine vào event loop:

```python
asyncio.run_coroutine_threadsafe(
    coroutine,
    self.loop,
)
```

Ví dụ:

```python
future = asyncio.run_coroutine_threadsafe(
    self._download(...),
    self.loop,
)
```

Đây là cầu nối:

```text
Qt GUI
   │
   │ request
   ▼
Worker Thread
   │
   ▼
asyncio loop
   │
   ▼
coroutine
```

---

# 14. Worker hoàn chỉnh hơn

```python
class AsyncWorker(QObject):

    progress = Signal(int, int, int)
    completed = Signal(int)
    failed = Signal(int, str)
    cancelled = Signal(int)

    def __init__(self, service):
        super().__init__()

        self.service = service
        self.loop = asyncio.new_event_loop()

        self.tasks = {}

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def submit(
        self,
        download,
    ):
        future = asyncio.run_coroutine_threadsafe(
            self._run_download(download),
            self.loop,
        )

        self.tasks[download.id] = future

    async def _run_download(
        self,
        download,
    ):

        def on_progress(
            downloaded,
            total,
        ):
            self.progress.emit(
                download.id,
                downloaded,
                total,
            )

        try:

            await self.service.start(
                download,
                on_progress,
            )

            self.completed.emit(
                download.id
            )

        except asyncio.CancelledError:

            self.cancelled.emit(
                download.id
            )

        except Exception as exc:

            self.failed.emit(
                download.id,
                str(exc),
            )

        finally:

            self.tasks.pop(
                download.id,
                None,
            )

    def cancel(
        self,
        download_id,
    ):
        future = self.tasks.get(
            download_id
        )

        if future:
            future.cancel()
```

---

# 15. Worker Thread

PySide6:

```python
from PySide6.QtCore import QThread
```

Tạo:

```python
thread = QThread()
worker = AsyncWorker(service)

worker.moveToThread(thread)

thread.started.connect(
    worker.run
)

thread.start()
```

Kiến trúc:

```text
             Main Thread
          ┌───────────────┐
          │ MainWindow    │
          │ View          │
          └───────┬───────┘
                  │
               Signal
                  │
          ┌───────▼───────┐
          │ QThread       │
          │               │
          │ AsyncWorker   │
          │      │        │
          │ asyncio loop  │
          └───────┬───────┘
                  │
                  ▼
               httpx
```

---

# 16. Presentation Model

Ở GUI, chúng ta cần Model/View.

Đây là kiến thức từ **Phần II**.

Có thể dùng:

```text
QTableView
     │
     ▼
DownloadTableModel
```

Model hiển thị:

```text
File
Status
Progress
Downloaded
Total
```

---

# 17. Table Model

```python
from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    Qt,
)


class DownloadTableModel(
    QAbstractTableModel
):

    HEADERS = [
        "File",
        "Status",
        "Progress",
    ]

    def __init__(self):
        super().__init__()

        self.items = []

    def rowCount(
        self,
        parent=QModelIndex(),
    ):
        return len(self.items)

    def columnCount(
        self,
        parent=QModelIndex(),
    ):
        return len(self.HEADERS)

    def data(
        self,
        index,
        role=Qt.ItemDataRole.DisplayRole,
    ):

        if not index.isValid():
            return None

        download = self.items[
            index.row()
        ]

        if role == Qt.ItemDataRole.DisplayRole:

            if index.column() == 0:
                return download.path

            if index.column() == 1:
                return download.status.name

            if index.column() == 2:
                return f"{download.progress}%"

        return None

    def headerData(
        self,
        section,
        orientation,
        role,
    ):

        if (
            orientation
            == Qt.Orientation.Horizontal
            and role
            == Qt.ItemDataRole.DisplayRole
        ):
            return self.HEADERS[section]

        return None
```

---

# 18. MainWindow

GUI:

```python
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.url_edit = QLineEdit()
        self.download_button = QPushButton(
            "Download"
        )

        self.table = QTableView()

        self.model = DownloadTableModel()

        self.table.setModel(
            self.model
        )

        ...
```

---

# 19. Download button

Không làm:

```python
def download_clicked(self):
    requests.get(...)
```

Cũng không làm:

```python
def download_clicked(self):
    asyncio.run(...)
```

Mà:

```python
def download_clicked(self):

    url = self.url_edit.text().strip()

    if not url:
        return

    self.controller.download(
        url
    )
```

GUI chỉ gửi command.

---

# 20. Controller

```python
class DownloadController:

    def __init__(
        self,
        worker,
    ):
        self.worker = worker

        self.next_id = 1

        self.downloads = {}

    def download(
        self,
        url,
        path,
    ):

        download = Download(
            id=self.next_id,
            url=url,
            path=path,
        )

        self.next_id += 1

        self.downloads[
            download.id
        ] = download

        self.worker.submit(
            download
        )

        return download
```

---

# 21. Signal Progress

MainWindow:

```python
worker.progress.connect(
    self.on_progress
)
```

Slot:

```python
@Slot(int, int, int)
def on_progress(
    self,
    download_id,
    downloaded,
    total,
):

    download = (
        self.controller.downloads[
            download_id
        ]
    )

    download.downloaded = downloaded
    download.total = total

    self.model.refresh_download(
        download_id
    )
```

---

# 22. Refresh Model

Không cần:

```python
self.model.layoutChanged.emit()
```

mọi lần.

Tốt hơn:

```python
def refresh_download(
    self,
    download_id,
):

    for row, item in enumerate(
        self.items
    ):

        if item.id == download_id:

            index = self.index(
                row,
                0,
            )

            end = self.index(
                row,
                self.columnCount() - 1,
            )

            self.dataChanged.emit(
                index,
                end,
                [
                    Qt.ItemDataRole.DisplayRole
                ],
            )

            return
```

Đây chính là kiến thức:

```text
QModelIndex
Roles
dataChanged
```

từ Phần II.

---

# 23. Progress Bar thật

Nếu muốn progress bar đẹp:

```text
QTableView
    │
    ▼
Delegate
    │
    ▼
QProgressBar
```

Đây là nơi kiến thức:

```text
Buổi 20 — Delegate
```

được áp dụng.

Ví dụ:

```text
Progress
██████████░░░ 75%
```

thay vì:

```text
75%
```

---

# 24. Cancel

GUI:

```python
def cancel_download(
    self,
    download_id,
):
    self.worker.cancel(
        download_id
    )
```

Worker:

```python
def cancel(
    self,
    download_id,
):
    future = self.tasks.get(
        download_id
    )

    if future:
        future.cancel()
```

---

# 25. Cancellation Flow

```text
User clicks Cancel
       │
       ▼
MainWindow
       │
       ▼
Controller
       │
       ▼
Worker.cancel(id)
       │
       ▼
Future.cancel()
       │
       ▼
asyncio.CancelledError
       │
       ▼
DownloadStatus.CANCELLED
       │
       ▼
Signal
       │
       ▼
GUI
```

Đây là một flow rất quan trọng.

---

# 26. Error Flow

Nếu server trả:

```text
404
```

thì:

```python
response.raise_for_status()
```

ném:

```python
httpx.HTTPStatusError
```

Service:

```text
HTTPStatusError
       │
       ▼
FAILED
       │
       ▼
error signal
       │
       ▼
GUI
```

GUI:

```text
A.zip
Status: FAILED
Error: 404 Not Found
```

---

# 27. Retry

Không retry:

```text
404
403
401
```

Có thể retry:

```text
Timeout
ConnectionError
502
503
504
```

Một service có thể:

```python
async def retry_download(
    self,
    ...
):

    for attempt in range(3):

        try:
            return await ...

        except httpx.RequestError:

            if attempt == 2:
                raise

            await asyncio.sleep(
                2 ** attempt
            )
```

---

# 28. Một vấn đề quan trọng: file tạm

Không nên download trực tiếp:

```text
book.zip
```

Nếu download bị cancel:

```text
book.zip
```

có thể là file hỏng.

Tốt hơn:

```text
book.zip.part
```

Trong quá trình download:

```text
book.zip.part
```

Download thành công:

```text
book.zip.part
       │
       ▼
book.zip
```

Ví dụ:

```python
temp_path = path + ".part"
```

Sau khi hoàn thành:

```python
Path(temp_path).replace(path)
```

---

# 29. Atomic-ish completion

Flow:

```text
download
   │
   ▼
file.zip.part
   │
   │ complete
   ▼
file.zip
```

Điều này giúp ứng dụng biết:

```text
file.zip
    → completed file

file.zip.part
    → incomplete download
```

Đây là thiết kế rất đáng dùng trong Download Manager.

---

# 30. Application State

Mỗi download:

```text
PENDING
   │
   ▼
DOWNLOADING
   │
   ├─────────────┐
   ▼             ▼
COMPLETED      FAILED
   │
   │
   └── CANCELLED
```

GUI không nên tự suy đoán state từ progress.

Ví dụ:

```text
progress = 100
```

không nhất thiết:

```text
COMPLETED
```

vì request có thể chưa hoàn thành việc flush/rename file.

State phải do application layer quyết định.

---

# 31. Shutdown

Đây là phần nhiều tutorial bỏ qua.

Khi người dùng đóng app:

```text
MainWindow.close()
       │
       ▼
Cancel tasks
       │
       ▼
await AsyncClient.aclose()
       │
       ▼
stop asyncio loop
       │
       ▼
quit QThread
       │
       ▼
application exit
```

Không nên:

```text
GUI đóng
   ↓
thread vẫn chạy
   ↓
download vẫn chạy
```

---

# 32. Shutdown Worker

Có thể:

```python
def shutdown(self):

    for future in self.tasks.values():
        future.cancel()

    self.loop.call_soon_threadsafe(
        self.loop.stop
    )
```

Trong production cần cẩn thận hơn với thứ tự cleanup: cancel task → chờ coroutine kết thúc → đóng `AsyncClient` → stop loop → chờ thread kết thúc.

---

# 33. Project Structure hoàn chỉnh

Sau Buổi 48:

```text
download_manager/
│
├── main.py
│
├── domain/
│   ├── __init__.py
│   └── download.py
│
├── application/
│   ├── __init__.py
│   ├── download_service.py
│   └── download_controller.py
│
├── infrastructure/
│   ├── __init__.py
│   ├── async_worker.py
│   └── http/
│       ├── __init__.py
│       └── async_download_engine.py
│
└── presentation/
    ├── __init__.py
    ├── main_window.py
    ├── download_model.py
    └── delegates/
        └── progress_delegate.py
```

---

# 34. Dependency Graph

```text
                    main.py
                       │
                       ▼
                 MainWindow
                       │
                       ▼
              DownloadController
                       │
                       ▼
               DownloadService
                       │
                       ▼
             AsyncDownloadEngine
                       │
                       ▼
                     httpx
```

Domain:

```text
Download
```

được dùng ở:

```text
Controller
Service
Presentation Model
```

nhưng Domain không import ngược:

```python
from PySide6 ...
```

---

# 35. Đây là điểm kết thúc của Phần IV

Nhìn lại:

```text
Buổi 36
GUI Thread
   ↓
Buổi 37
GUI Freeze
   ↓
Buổi 38
QThread
   ↓
Buổi 39
Worker Object
   ↓
Buổi 40
Signals
   ↓
Buổi 41
Progress
   ↓
Buổi 42
Cancellation
   ↓
Buổi 43
QThreadPool
   ↓
Buổi 44
QRunnable
   ↓
Buổi 45
Concurrent Tasks
   ↓
Buổi 46
asyncio
   ↓
Buổi 47
HTTP
   ↓
Buổi 48
Download Manager
```

Bạn đã đi từ:

```python
button.clicked.connect(...)
```

đến:

```text
GUI
 │
 ├── Qt Event Loop
 │
 └── Worker Thread
         │
         └── asyncio Event Loop
                 │
                 ├── Task A
                 ├── Task B
                 └── Task C
                         │
                         ▼
                  httpx.AsyncClient
```

Đây là một bước chuyển rất lớn từ **PySide6 cơ bản → desktop application architecture**.

---

# Bài tập nâng cấp

Sau khi chạy được phiên bản cơ bản, hãy tự nâng cấp theo thứ tự:

### Level 1

```text
[Download]
[Cancel]
Progress
Status
```

### Level 2

```text
Concurrent limit = 3
Retry = 3
Timeout
```

### Level 3

```text
.part file
Filename detection
Content-Length
Speed
ETA
```

### Level 4

```text
Pause
Resume
```

### Level 5

```text
Download queue
Priority
Multiple files
Persistent state
```

### Level 6

Kết hợp kiến thức **Phần II + III + IV**:

```text
QTableView
     │
     ▼
QAbstractTableModel
     │
     ▼
DownloadController
     │
     ▼
DownloadService
     │
     ▼
asyncio
     │
     ▼
httpx
```

Đến đây, bạn đã có nền tảng rất tốt để bước sang **Phần V — SQLite + PySide6**, nơi chúng ta sẽ biến Download Manager/ứng dụng desktop thành một ứng dụng có **persistent state, Repository, Transaction, Search, Filter và Migration**.
