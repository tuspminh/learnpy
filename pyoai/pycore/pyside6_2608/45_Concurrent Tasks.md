# Buổi 45 — Concurrent Tasks

Ở Buổi 44, ta đã xây được:

```text
QRunnable
    +
WorkerSignals
    +
QThreadPool
```

Hôm nay chúng ta nâng cấp từ:

```text
1 Task
```

thành:

```text
N Task chạy concurrent
```

Đây là kiến thức rất quan trọng cho các ứng dụng PySide6 thực tế như:

* Download Manager
* Crawler Dashboard
* Batch Processor
* Image Processor
* File Scanner
* Story Crawler
* HTTP Client
* Import/Export dữ liệu

---

# 1. Concurrent ≠ Parallel

Trước tiên phải phân biệt:

```text
Concurrency
```

và:

```text
Parallelism
```

### Concurrency

Có nhiều công việc đang được quản lý cùng lúc:

```text
Task A ────────┐
Task B ────────┼── QThreadPool
Task C ────────┤
Task D ────────┘
```

### Parallelism

Nhiều task thực sự chạy trên nhiều CPU/thread cùng lúc:

```text
CPU 1 → Task A
CPU 2 → Task B
CPU 3 → Task C
CPU 4 → Task D
```

Với `QThreadPool`, chúng ta chủ yếu đang xây:

> **concurrent task execution bằng thread pool.**

---

# 2. Mental Model

Một task:

```text
GUI
 │
 ▼
QThreadPool
 │
 ▼
QRunnable
```

Nhiều task:

```text
                  QThreadPool
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
     Task A          Task B          Task C
        │              │              │
        ▼              ▼              ▼
     Worker          Worker          Worker
```

Nếu:

```python
pool.setMaxThreadCount(3)
```

thì tối đa khoảng:

```text
3 task
```

được thực thi đồng thời.

Các task còn lại chờ:

```text
Task 1 → RUNNING
Task 2 → RUNNING
Task 3 → RUNNING

Task 4 → QUEUED
Task 5 → QUEUED
Task 6 → QUEUED
```

---

# 3. Tạo nhiều task

Giả sử:

```python
def work(number):
    time.sleep(2)
    return number * number
```

Ta submit:

```python
for number in range(10):

    task = Task(
        work,
        number,
    )

    pool.start(task)
```

Pool quản lý:

```text
Task 0
Task 1
Task 2
Task 3
Task 4
Task 5
Task 6
Task 7
Task 8
Task 9
```

---

# 4. Giới hạn concurrency

Đây là API quan trọng:

```python
pool.setMaxThreadCount(4)
```

Ví dụ:

```python
pool = QThreadPool()

pool.setMaxThreadCount(4)
```

Mental model:

```text
10 tasks
     │
     ▼
QThreadPool
     │
     ├── Thread 1 → Task 1
     ├── Thread 2 → Task 2
     ├── Thread 3 → Task 3
     ├── Thread 4 → Task 4
     │
     └── Task 5..10 waiting
```

---

# 5. Vì sao không tạo 1000 thread?

Không nên:

```text
1000 tasks
    ↓
1000 threads
```

Thread có chi phí:

```text
memory
context switching
scheduling
OS resources
```

Thay vào đó:

```text
1000 tasks
    ↓
QThreadPool
    ↓
10 threads
```

Pool tái sử dụng worker threads.

---

# 6. `activeThreadCount()`

Có thể kiểm tra:

```python
pool.activeThreadCount()
```

Ví dụ:

```python
print(pool.activeThreadCount())
```

Cho biết số thread đang active.

---

# 7. `maxThreadCount()`

```python
print(pool.maxThreadCount())
```

Thiết lập:

```python
pool.setMaxThreadCount(4)
```

Kiểm tra:

```python
print(pool.maxThreadCount())
```

---

# 8. `start()` nhiều lần

Ví dụ:

```python
pool.start(Task(work, 1))
pool.start(Task(work, 2))
pool.start(Task(work, 3))
```

Không có nghĩa:

```text
Task 1 hoàn thành
↓
Task 2
↓
Task 3
```

Mà có thể:

```text
Task 1 ──────────┐
Task 2 ──────────┤ concurrent
Task 3 ──────────┘
```

---

# 9. Completion order ≠ Submission order

Đây là điểm cực kỳ quan trọng.

Ta submit:

```text
Task A
Task B
Task C
```

nhưng thời gian chạy:

```text
A = 5s
B = 1s
C = 3s
```

Có thể nhận:

```text
B finished
C finished
A finished
```

Không được giả định:

```text
A
B
C
```

---

# 10. Ví dụ

```python
def work(name, duration):
    time.sleep(duration)
    return name
```

Submit:

```python
Task(work, "A", 5)
Task(work, "B", 1)
Task(work, "C", 3)
```

Kết quả:

```text
B
C
A
```

Đây chính là bản chất concurrent execution.

---

# 11. GUI phải xử lý Completion bất kỳ thứ tự nào

Ví dụ:

```python
def on_result(result):
    self.list_widget.addItem(result)
```

Không nên giả định:

```text
Task 1
Task 2
Task 3
```

Nếu muốn giữ thứ tự ban đầu, phải gắn `task_id`.

---

# 12. Task ID

Thiết kế:

```python
class Task(QRunnable):

    def __init__(self, task_id, function, *args, **kwargs):
        ...
```

Ví dụ:

```python
task = Task(
    task_id=42,
    function=work,
    number=10,
)
```

Result có thể:

```python
{
    "task_id": 42,
    "result": 100,
}
```

---

# 13. Tạo `TaskResult`

Một thiết kế sạch:

```python
from dataclasses import dataclass


@dataclass
class TaskResult:
    task_id: int
    value: object
```

Signal:

```python
result = Signal(object)
```

Emit:

```python
self.signals.result.emit(
    TaskResult(
        task_id=self.task_id,
        value=result,
    )
)
```

GUI:

```python
def on_result(result):
    print(
        result.task_id,
        result.value,
    )
```

---

# 14. Concurrent Task Manager

Khi có nhiều task, GUI không nên tự quản lý tất cả.

Ta tạo:

```text
TaskManager
```

Architecture:

```text
MainWindow
     │
     ▼
TaskManager
     │
     ▼
QThreadPool
     │
 ┌───┼────┐
 ▼   ▼    ▼
T1  T2   T3
```

---

# 15. TaskManager cơ bản

```python
class TaskManager:

    def __init__(self, max_workers=4):
        self.pool = QThreadPool()
        self.pool.setMaxThreadCount(max_workers)

    def submit(self, task):
        self.pool.start(task)
```

Sử dụng:

```python
manager = TaskManager(max_workers=4)

manager.submit(
    Task(work, 1)
)
```

---

# 16. Quản lý danh sách task

Ta có thể lưu:

```python
self.tasks = {}
```

Ví dụ:

```python
self.tasks[task_id] = task
```

Mental model:

```text
TaskManager
 │
 ├── 1 → Task
 ├── 2 → Task
 ├── 3 → Task
 └── 4 → Task
```

Điều này rất hữu ích khi cần:

```text
status
cancel
progress
lookup
```

---

# 17. Task Status

Một task có thể có:

```text
PENDING
RUNNING
SUCCESS
FAILED
CANCELLED
```

Ví dụ:

```python
from enum import Enum, auto


class TaskStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()
    CANCELLED = auto()
```

Flow:

```text
PENDING
   │
   ▼
RUNNING
   │
   ├── SUCCESS
   │
   ├── FAILED
   │
   └── CANCELLED
```

---

# 18. Signals cho lifecycle

Ta có:

```python
class WorkerSignals(QObject):

    started = Signal()
    progress = Signal(int)
    result = Signal(object)
    error = Signal(object)
    finished = Signal()
```

Nhưng với nhiều task, có thể thêm:

```python
status_changed = Signal(object)
```

---

# 19. Batch Processing

Một use case rất thực tế:

```text
Folder
 │
 ├── image01.jpg
 ├── image02.jpg
 ├── image03.jpg
 ├── image04.jpg
 └── image05.jpg
```

Ta muốn:

```text
ImageProcessor
      │
      ▼
QThreadPool
      │
 ┌────┼────┐
 ▼    ▼    ▼
img1 img2 img3
```

---

# 20. Batch Progress

Giả sử:

```text
100 files
```

Mỗi task hoàn thành:

```text
1 file
```

Ta có:

```text
completed = 37
total = 100
```

Progress:

```python
percent = completed * 100 // total
```

GUI:

```python
progress_bar.setValue(percent)
```

---

# 21. Nhưng có race condition

Nếu nhiều thread cùng làm:

```python
self.completed += 1
```

có thể phát sinh race condition.

Ví dụ:

```text
Thread A đọc completed = 10
Thread B đọc completed = 10

A → 11
B → 11
```

Trong khi đáng lẽ:

```text
12
```

Đây là lý do cần synchronization.

---

# 22. Dùng `threading.Lock`

```python
from threading import Lock


class Counter:

    def __init__(self):
        self.value = 0
        self.lock = Lock()

    def increment(self):

        with self.lock:
            self.value += 1

            return self.value
```

Sau đó:

```python
completed = counter.increment()
```

---

# 23. Tuy nhiên GUI không nhất thiết phải tự increment

Một architecture tốt hơn:

```text
Task
 │
 ▼
finished signal
 │
 ▼
TaskManager
 │
 ▼
completed count
 │
 ▼
GUI
```

GUI không trực tiếp quản lý shared state giữa worker threads.

---

# 24. Batch Manager

Ví dụ:

```python
class BatchManager(QObject):

    progress = Signal(int)
    finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.total = 0
        self.completed = 0
```

Khi submit batch:

```python
self.total = len(tasks)
self.completed = 0
```

Khi task hoàn thành:

```python
self.completed += 1
```

Sau đó:

```python
percent = (
    self.completed * 100 // self.total
)
```

Emit:

```python
self.progress.emit(percent)
```

---

# 25. Nhưng nhớ thread safety

Nếu callback được xử lý trên GUI thread, việc cập nhật state ở GUI-side có thể đơn giản hơn.

Đây là một insight quan trọng:

> Đừng chia sẻ mutable state giữa worker threads nếu không cần thiết.

Thay vì:

```text
Thread 1 ─┐
Thread 2 ─┼── shared dict
Thread 3 ─┘
```

nên:

```text
Thread 1 ──signal──┐
Thread 2 ──signal──┼── Manager
Thread 3 ──signal──┘
```

---

# 26. Concurrent HTTP Downloads

Đây là use case cực kỳ gần với project của bạn.

Giả sử:

```text
URL 1
URL 2
URL 3
URL 4
URL 5
```

Ta tạo:

```text
DownloadTask
```

Mỗi task:

```python
download(url)
```

Pool:

```text
QThreadPool
 │
 ├── DownloadTask 1
 ├── DownloadTask 2
 ├── DownloadTask 3
 └── DownloadTask 4
```

---

# 27. Download Manager Architecture

```text
                    MainWindow
                        │
                        ▼
                 DownloadManager
                        │
                        ▼
                   QThreadPool
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
      DownloadTask  DownloadTask  DownloadTask
          │             │             │
          ▼             ▼             ▼
       HTTP          HTTP          HTTP
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                     Signals
                        │
                        ▼
                       GUI
```

Đây chính là nền tảng của **Buổi 48 — Download Manager**.

---

# 28. Không nên dùng quá nhiều thread cho HTTP

Ví dụ:

```python
pool.setMaxThreadCount(100)
```

không tự động có nghĩa là:

```text
100 downloads = tốt
```

Có thể gây:

```text
server overload
connection overhead
memory usage
rate limiting
```

Thường phải có concurrency limit hợp lý.

Ví dụ:

```python
pool.setMaxThreadCount(8)
```

hoặc:

```python
4
8
16
```

tùy workload.

---

# 29. CPU-bound vs I/O-bound

Đây là kiến thức bạn đã học ở ThreadPoolExecutor và ProcessPoolExecutor.

### I/O-bound

Ví dụ:

```text
HTTP
file
database
network
```

`QThreadPool` rất phù hợp.

### CPU-bound

Ví dụ:

```text
image processing
compression
large computation
```

Python GIL có thể hạn chế hiệu năng CPU-bound thuần Python.

Khi đó có thể cân nhắc:

```text
ProcessPoolExecutor
```

hoặc các thư viện native/giải phóng GIL.

---

# 30. So sánh

| Workload             | Công cụ             |
| -------------------- | ------------------- |
| GUI task             | QThreadPool         |
| HTTP                 | QThreadPool         |
| File I/O             | QThreadPool         |
| Database I/O         | QThreadPool         |
| CPU-heavy Python     | ProcessPoolExecutor |
| Async HTTP           | asyncio             |
| Qt event-driven task | QThread/QThreadPool |

Không có một công cụ phù hợp cho mọi trường hợp.

---

# 31. Fan-out / Fan-in

Đây là pattern rất quan trọng.

Ví dụ:

```text
             Request
                │
                ▼
              FAN-OUT
       ┌────────┼────────┐
       ▼        ▼        ▼
     Task A   Task B   Task C
       │        │        │
       └────────┼────────┘
                ▼
              FAN-IN
                │
                ▼
             Results
```

Ví dụ Story Reader:

```text
Crawler
 │
 ├── Source A
 ├── Source B
 ├── Source C
 └── Source D
       │
       ▼
    Aggregate
```

---

# 32. `waitForDone()`

`QThreadPool` có:

```python
pool.waitForDone()
```

Nó chờ các task hoàn thành.

Ví dụ:

```python
pool.start(task1)
pool.start(task2)

pool.waitForDone()
```

Nhưng:

> **Không nên gọi `waitForDone()` trên GUI thread cho task dài.**

Vì:

```text
GUI
 │
 ▼
waitForDone()
 │
 ▼
BLOCK
 │
 ▼
FREEZE
```

---

# 33. Sai lầm phổ biến

Sai:

```python
def on_click(self):

    for task in tasks:
        pool.start(task)

    pool.waitForDone()

    self.label.setText("Done")
```

GUI bị block.

Đúng:

```text
submit tasks
    ↓
GUI tiếp tục event loop
    ↓
task hoàn thành
    ↓
finished signal
    ↓
GUI cập nhật
```

---

# 34. Khi nào biết toàn bộ batch hoàn thành?

Không dùng:

```python
waitForDone()
```

trên GUI thread.

Ta dùng counter:

```python
completed += 1
```

khi mỗi task phát:

```python
finished
```

Nếu:

```python
completed == total
```

thì:

```python
batch_finished.emit()
```

---

# 35. `BatchManager`

Mental model:

```text
BatchManager
 │
 ├── total = 20
 ├── completed = 0
 │
 ├── Task 1 finished → 1
 ├── Task 2 finished → 2
 ├── Task 3 finished → 3
 │
 ...
 │
 └── Task 20 finished → 20
                         │
                         ▼
                   batch_finished
```

---

# 36. Có thể theo dõi từng task

Ví dụ UI:

```text
┌──────────────────────────────────┐
│ Downloads                        │
├──────────────────────────────────┤
│ file1.zip     ████████  80%      │
│ file2.zip     ██████████ 100%    │
│ file3.zip     ███       30%      │
│ file4.zip     waiting             │
└──────────────────────────────────┘
```

Mỗi task có:

```text
task_id
progress
status
result
error
```

GUI map:

```python
self.rows[task_id]
```

---

# 37. Task Registry

Ví dụ:

```python
self.tasks = {}
```

Khi tạo:

```python
self.tasks[task_id] = task
```

UI:

```text
tasks
 │
 ├── 101 → file1
 ├── 102 → file2
 ├── 103 → file3
 └── 104 → file4
```

Khi nhận:

```python
def on_progress(task_id, value):
    ...
```

GUI biết update row nào.

---

# 38. Signal nên chứa `task_id`

Thay vì:

```python
progress = Signal(int)
```

với concurrent task nên dùng:

```python
progress = Signal(int, int)
```

nghĩa:

```text
task_id
progress
```

Ví dụ:

```python
self.signals.progress.emit(
    self.task_id,
    75,
)
```

GUI:

```python
def on_progress(task_id, value):
    self.rows[task_id].setValue(value)
```

Đây là pattern cực kỳ hữu ích.

---

# 39. Thiết kế Signals cho Concurrent Task

Một phiên bản tốt:

```python
class WorkerSignals(QObject):

    started = Signal(int)

    progress = Signal(int, int)

    result = Signal(int, object)

    error = Signal(int, object)

    finished = Signal(int)
```

Trong đó:

```text
Signal(task_id, ...)
```

Giúp mọi event xác định task.

---

# 40. Task

```python
class Task(QRunnable):

    def __init__(self, task_id, function, *args, **kwargs):
        super().__init__()

        self.task_id = task_id
        self.function = function
        self.args = args
        self.kwargs = kwargs

        self.signals = WorkerSignals()

    def run(self):

        self.signals.started.emit(
            self.task_id
        )

        try:

            result = self.function(
                *self.args,
                **self.kwargs,
            )

            self.signals.result.emit(
                self.task_id,
                result,
            )

        except Exception as e:

            self.signals.error.emit(
                self.task_id,
                e,
            )

        finally:

            self.signals.finished.emit(
                self.task_id
            )
```

Đây là một abstraction rất đáng nhớ.

---

# 41. Concurrent Task Manager

```python
class TaskManager(QObject):

    def __init__(self, max_workers=4):
        super().__init__()

        self.pool = QThreadPool()
        self.pool.setMaxThreadCount(
            max_workers
        )

    def submit(self, task):
        self.pool.start(task)
```

GUI:

```python
manager.submit(task)
```

---

# 42. Nâng cấp TaskManager

Có thể để manager nhận:

```python
def submit(
    self,
    task_id,
    function,
    *args,
    **kwargs,
):
```

và tự tạo Task:

```python
def submit(
    self,
    task_id,
    function,
    *args,
    **kwargs,
):

    task = Task(
        task_id,
        function,
        *args,
        **kwargs,
    )

    self.pool.start(task)

    return task
```

Sử dụng:

```python
manager.submit(
    101,
    calculate,
    20,
)
```

---

# 43. Đây đã gần giống Executor

Ta đang xây:

```text
TaskManager
     │
     ▼
QThreadPool
```

API:

```python
manager.submit(...)
```

gần giống:

```python
executor.submit(...)
```

Nhưng Qt version có thêm:

```text
Signal
Progress
GUI integration
Task ID
```

---

# 44. Bài tập thực hành

## Bài 1 — 10 task

Tạo:

```text
Task 1
Task 2
...
Task 10
```

Mỗi task sleep random:

```python
random.uniform(1, 5)
```

Hiển thị:

```text
Task 1 finished
Task 4 finished
Task 2 finished
...
```

Quan sát completion order.

---

## Bài 2 — Task ID

Mỗi task có:

```text
task_id
```

Signal:

```text
result(task_id, result)
```

GUI hiển thị đúng task.

---

## Bài 3 — Concurrent limit

Thử:

```python
pool.setMaxThreadCount(1)
```

sau đó:

```python
2
4
8
```

Quan sát sự khác biệt.

---

## Bài 4 — Progress

Tạo 10 task.

Mỗi task:

```text
0 → 100
```

GUI có 10 progress bars.

```text
Task 1 ██████████
Task 2 █████
Task 3 ████████
...
```

---

## Bài 5 — Batch completion

Submit:

```text
20 tasks
```

GUI hiển thị:

```text
Completed: 0 / 20
```

Khi task xong:

```text
Completed: 1 / 20
Completed: 2 / 20
...
Completed: 20 / 20
```

Cuối cùng:

```text
All tasks completed!
```

---

# 45. Bài tập nâng cao — Crawler

Đây là bài rất phù hợp với project Story Reader của bạn.

Danh sách:

```text
chapter_001
chapter_002
chapter_003
...
chapter_020
```

Mỗi task:

```python
crawl_chapter(url)
```

Pool:

```text
max_workers = 4
```

GUI:

```text
Crawler
─────────────────────────────────
Chapter 1   ██████████ 100%
Chapter 2   ███████    70%
Chapter 3   ██████████ 100%
Chapter 4   ███        30%
Chapter 5   waiting
...
─────────────────────────────────
Completed: 3 / 20
```

Architecture:

```text
MainWindow
     │
     ▼
CrawlerManager
     │
     ▼
QThreadPool
     │
 ┌───┼────────┐
 ▼   ▼        ▼
C1  C2       C3 ...
 │   │        │
 └───┼────────┘
     ▼
 Signals
     │
     ▼
MainWindow
```

Đây chính là bước rất gần với **Crawler Dashboard** mà chúng ta sẽ xây ở project lớn.

---

# 46. Những điều không nên làm

### ❌ 1. Worker cập nhật widget

```python
self.label.setText(...)
```

Không.

---

### ❌ 2. Worker dùng chung mutable state tùy tiện

```python
shared_dict[key] = value
```

từ nhiều thread.

Cần synchronization hoặc thiết kế message/signal-based.

---

### ❌ 3. `waitForDone()` trên GUI thread

```python
pool.waitForDone()
```

với task dài → GUI freeze.

---

### ❌ 4. Tạo thread cho từng task

```text
1000 task
↓
1000 thread
```

Không.

Dùng pool.

---

### ❌ 5. Giả định thứ tự hoàn thành

```text
submit A
submit B
submit C

→ A B C
```

Không đảm bảo.

---

# 47. Mental Model quan trọng nhất của Buổi 45

Hãy nhớ:

```text
                TaskManager
                     │
                     ▼
                QThreadPool
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
     Task A        Task B        Task C
       │             │             │
       ▼             ▼             ▼
     Worker        Worker        Worker
       │             │             │
       └─────────────┼─────────────┘
                     │
                   Signal
                     │
                     ▼
                    GUI
```

Mỗi task nên có:

```text
Task ID
Status
Progress
Result
Error
Finished
```

---

# 48. Kết nối với những gì bạn đã học

Bạn đã học:

```text
Thread
   ↓
ThreadPoolExecutor
   ↓
ProcessPoolExecutor
   ↓
asyncio
   ↓
QThread
   ↓
QThreadPool
   ↓
QRunnable
   ↓
Concurrent Tasks
```

Điểm khác biệt quan trọng của PySide6 là:

```text
Concurrency
      +
Qt Event Loop
      +
Signal/Slot
      +
GUI Thread
```

Vì vậy tư duy đúng không phải:

> "Làm sao tạo nhiều thread?"

mà là:

> **"Làm sao tổ chức nhiều background tasks mà GUI vẫn responsive, task không biết GUI, kết quả/error/progress được truyền qua signal, và concurrency được kiểm soát?"**

Đó chính là nền tảng để sang **Buổi 46 — PySide6 + `asyncio`**, nơi chúng ta sẽ giải quyết một bài toán rất thú vị: **kết hợp Qt Event Loop với Python Asyncio Event Loop** mà không làm GUI freeze.
