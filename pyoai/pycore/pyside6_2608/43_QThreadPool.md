# Buổi 43 — `QThreadPool`

Từ Buổi 36 → 42, chúng ta học mô hình:

```text
GUI
 │
 ▼
QThread
 │
 ▼
Worker
 │
 ▼
Task
```

Mô hình này rất tốt khi có **một task dài**.

Nhưng nếu ứng dụng có:

```text
Download 1
Download 2
Download 3
Download 4
...
Download 100
```

thì tạo:

```text
QThread × 100
```

là không tốt.

Qt cung cấp:

```python
QThreadPool
```

để giải quyết bài toán này.

---

# 1. Mental Model

`QThreadPool` là một **pool các thread có thể tái sử dụng**.

Thay vì:

```text
Task 1 → Thread 1
Task 2 → Thread 2
Task 3 → Thread 3
Task 4 → Thread 4
```

ta có:

```text
                 QThreadPool
              ┌──────┼──────┐
              ▼      ▼      ▼
           Thread  Thread  Thread
              │      │      │
              ▼      ▼      ▼
            Task    Task    Task
```

Khi task hoàn thành:

```text
Thread
   │
   ▼
trả về Pool
```

Thread có thể được sử dụng cho task khác.

---

# 2. Tại sao cần Thread Pool?

Giả sử:

```text
100 tasks
```

Nếu mỗi task tạo một thread:

```text
100 tasks
    ↓
100 threads
```

Có thể dẫn tới:

* nhiều context switching
* memory overhead
* khó quản lý lifecycle
* scheduling phức tạp
* performance không tốt

Thread pool giới hạn số thread:

```text
100 tasks
    ↓
QThreadPool
    ↓
8 threads
```

Ví dụ:

```text
Task 1 ──► Thread 1
Task 2 ──► Thread 2
Task 3 ──► Thread 3
...
Task 8 ──► Thread 8

Task 9 ──► queue
Task 10 ─► queue
...
```

Khi Thread 1 hoàn thành:

```text
Thread 1
   ↓
Task 9
```

---

# 3. API chính

Import:

```python
from PySide6.QtCore import QThreadPool
```

Tạo:

```python
pool = QThreadPool()
```

Hoặc lấy global pool:

```python
pool = QThreadPool.globalInstance()
```

---

# 4. `globalInstance()`

Qt có một thread pool dùng chung:

```python
pool = QThreadPool.globalInstance()
```

Mental model:

```text
Application
     │
     ▼
Global QThreadPool
     │
 ┌───┼────┬────┐
 ▼   ▼    ▼    ▼
 T1  T2   T3   T4
```

Đối với các task đơn giản, đây là cách rất tiện.

---

# 5. Submit Task

`QThreadPool` không trực tiếp nhận function:

```python
pool.start(my_function)
```

Thay vào đó, ta dùng:

```python
QRunnable
```

Đây chính là lý do:

> **Buổi 43 — QThreadPool**

đi ngay trước:

> **Buổi 44 — QRunnable**

---

# 6. Quan hệ giữa `QThreadPool` và `QRunnable`

Mental model:

```text
QRunnable
    │
    │ start()
    ▼
QThreadPool
    │
    ▼
Thread
    │
    ▼
QRunnable.run()
```

`QRunnable` đại diện cho **một task có thể chạy**.

`QThreadPool` quản lý **các thread thực thi task**.

---

# 7. Ví dụ đầu tiên

```python
from PySide6.QtCore import QRunnable, QThreadPool
```

Tạo task:

```python
class Task(QRunnable):

    def run(self):
        print("Hello from worker thread")
```

Submit:

```python
pool = QThreadPool.globalInstance()

pool.start(Task())
```

Flow:

```text
Task()
   │
   ▼
pool.start()
   │
   ▼
QThreadPool
   │
   ▼
available thread
   │
   ▼
Task.run()
```

---

# 8. Một điểm quan trọng

Với:

```python
QThread + Worker(QObject)
```

ta có:

```text
QObject
   +
QThread
```

Còn với:

```python
QThreadPool
```

ta thường có:

```text
QRunnable
   +
QThreadPool
```

Hai architecture khác nhau.

---

# 9. Khi nào dùng `QThread`?

Ví dụ:

```text
Crawler service
Download service
Database worker
Long-running process
```

cần:

* lifecycle rõ ràng
* signals nhiều
* cancel/pause/resume
* event loop của worker
* communication hai chiều

thì:

```text
QThread + QObject Worker
```

rất phù hợp.

---

# 10. Khi nào dùng `QThreadPool`?

Ví dụ:

```text
resize image 1
resize image 2
resize image 3
resize image 4
```

hoặc:

```text
download metadata A
download metadata B
download metadata C
```

hoặc:

```text
process file 1
process file 2
process file 3
```

thì:

```text
QThreadPool + QRunnable
```

rất phù hợp.

---

# 11. Thread Pool giới hạn concurrency

Kiểm tra:

```python
pool.maxThreadCount()
```

Ví dụ:

```python
print(pool.maxThreadCount())
```

Có thể trả về số thread pool cho phép chạy đồng thời.

Mental model:

```text
maxThreadCount = 8
```

thì:

```text
Task 1 → running
Task 2 → running
...
Task 8 → running

Task 9 → waiting
Task 10 → waiting
```

---

# 12. `setMaxThreadCount()`

Có thể:

```python
pool.setMaxThreadCount(4)
```

Khi đó:

```text
QThreadPool
 ├── T1
 ├── T2
 ├── T3
 └── T4
```

Tối đa 4 task chạy đồng thời.

---

# 13. Queue của Thread Pool

Giả sử:

```python
pool.setMaxThreadCount(2)
```

Submit:

```text
Task A
Task B
Task C
Task D
Task E
```

Pool:

```text
Running:

Thread 1 → A
Thread 2 → B

Waiting:

C
D
E
```

Khi A xong:

```text
Thread 1 → C
```

Khi B xong:

```text
Thread 2 → D
```

---

# 14. Thread được tái sử dụng

Điểm quan trọng:

```text
Task A
   ↓
Thread 1
   ↓
finished
   ↓
Thread 1 returned to pool
   ↓
Task C
```

Không nhất thiết phải:

```text
Task A → create Thread
Task A → destroy Thread
Task C → create Thread
```

---

# 15. So sánh hai mô hình

| `QThread + Worker`          | `QThreadPool + QRunnable`           |
| --------------------------- | ----------------------------------- |
| Worker là `QObject`         | Task là `QRunnable`                 |
| Thread lifecycle rõ         | Pool quản lý thread                 |
| Phù hợp long-running worker | Phù hợp short/medium tasks          |
| Signal/Slot mạnh            | Cần thiết kế signals riêng          |
| Có event loop worker        | Không nên dựa vào worker event loop |
| Cancel phức tạp hơn         | Task-oriented                       |
| Một worker/task thường trực | Nhiều task                          |

---

# 16. Một lỗi phổ biến

Đừng nghĩ:

```text
QThreadPool = QThread nhưng tự động
```

Không hẳn.

`QThreadPool` thiên về:

```text
Task scheduling
+
Thread reuse
+
Concurrency limiting
```

Trong khi `QThread` thiên về:

```text
Thread lifecycle
+
QObject affinity
+
Event loop
```

---

# 17. Ví dụ nhiều task

```python
from PySide6.QtCore import QRunnable, QThreadPool
import time


class Task(QRunnable):

    def __init__(self, number):
        super().__init__()
        self.number = number

    def run(self):
        print(f"Task {self.number} started")

        time.sleep(1)

        print(f"Task {self.number} finished")
```

Submit:

```python
pool = QThreadPool.globalInstance()

for i in range(10):
    pool.start(Task(i))
```

Nếu pool có:

```text
4 threads
```

thì khoảng:

```text
Task 0 ─┐
Task 1 ─┤
Task 2 ─┼─ running
Task 3 ─┘

Task 4 ─┐
Task 5  │ waiting
...
```

---

# 18. `waitForDone()`

API:

```python
pool.waitForDone()
```

Có nghĩa:

> Chờ tất cả task trong pool hoàn thành.

Ví dụ:

```python
pool.start(Task(1))
pool.start(Task(2))

pool.waitForDone()

print("All done")
```

Nhưng **không nên gọi trong GUI thread** nếu task có thể chạy lâu.

Sai:

```text
GUI Thread
   │
   ▼
waitForDone()
   │
   ▼
GUI bị block
```

Kết quả:

```text
❌ UI freeze
```

---

# 19. GUI vẫn phải responsive

Đúng:

```text
GUI Thread
   │
   ├── start tasks
   │
   └── event loop continues
             │
             ▼
        QThreadPool
             │
        ┌────┼────┐
        ▼    ▼    ▼
       T1   T2   T3
```

---

# 20. Vì sao `QRunnable` không có Signal như `QObject`?

`QRunnable` không phải `QObject`.

Vì vậy không thể đơn giản:

```python
class Task(QRunnable):

    progress = Signal(int)
```

theo cách thông thường.

Ta cần một object signal riêng.

Đây là nội dung cực kỳ quan trọng của **Buổi 44**.

Ví dụ:

```python
class WorkerSignals(QObject):

    finished = Signal()
    error = Signal(str)
    result = Signal(object)
```

Sau đó:

```python
class Task(QRunnable):

    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()
```

---

# 21. Nhưng hôm nay chỉ cần hiểu architecture

```text
QRunnable
    │
    ├── run()
    │
    └── signals
           │
           ├── result
           ├── error
           └── finished
```

Chi tiết implementation sẽ học ở Buổi 44.

---

# 22. `QThreadPool` + PySide6 GUI

Ví dụ:

```text
GUI
 │
 │ start
 ▼
QThreadPool
 │
 ├── Task A
 ├── Task B
 ├── Task C
 └── Task D
 │
 ▼
Signals
 │
 ▼
GUI
```

Đây là architecture cực kỳ hữu ích.

---

# 23. Ví dụ Image Processing

Giả sử có:

```text
100 images
```

Không nên:

```text
100 QThreads
```

Có thể:

```text
QThreadPool
maxThreadCount = 8
```

Sau đó:

```text
Image 1 → Task
Image 2 → Task
...
Image 100 → Task
```

Pool:

```text
T1 → image 1
T2 → image 2
T3 → image 3
...
T8 → image 8

waiting:
image 9
image 10
...
```

---

# 24. Ví dụ Story Reader

Đây là nơi kiến thức rất phù hợp với project của bạn.

Giả sử cần crawl metadata:

```text
Story A
Story B
Story C
Story D
Story E
```

Có thể:

```text
QThreadPool
    │
    ├── CrawlTask(A)
    ├── CrawlTask(B)
    ├── CrawlTask(C)
    ├── CrawlTask(D)
    └── CrawlTask(E)
```

Ví dụ:

```text
maxThreadCount = 4
```

thì:

```text
A ──► Thread 1
B ──► Thread 2
C ──► Thread 3
D ──► Thread 4

E ──► queue
```

---

# 25. Nhưng đừng vội dùng ThreadPool cho mọi thứ

Ví dụ crawler có:

```text
Pause
Resume
Cancel
Progress
Retry
Rate limiting
HTTP session
Database transaction
```

thì một Worker dài sống xuyên suốt có thể phù hợp hơn:

```text
QThread
  +
Worker(QObject)
```

Còn nếu:

```text
100 independent tasks
```

thì:

```text
QThreadPool
```

rất hợp lý.

---

# 26. Thread Pool và I/O

ThreadPool rất phù hợp với nhiều I/O task:

```text
download metadata
read files
process network response
```

Ví dụ:

```text
100 URLs
   ↓
QThreadPool
   ↓
8 concurrent requests
```

Nhưng cần chú ý:

* server rate limit
* connection pool
* timeout
* retry
* cancellation

Không phải:

```text
1000 URLs
→ 1000 concurrent requests
```

---

# 27. Thread Pool và CPU

Nếu task là CPU-bound:

```text
image processing
compression
parsing lớn
hashing
```

thì `QThreadPool` vẫn tạo thread concurrency, nhưng Python GIL có thể ảnh hưởng nếu phần lớn công việc thực hiện bằng Python bytecode.

Khi đó cần cân nhắc:

```text
QThreadPool
```

vs:

```text
ProcessPoolExecutor
```

mà bạn đã học trước đây.

---

# 28. So sánh với `ThreadPoolExecutor`

Bạn đã học `ThreadPoolExecutor`, nên đây là điểm rất đáng chú ý.

### Python

```python
executor.submit(task)
```

### Qt

```python
pool.start(runnable)
```

Mental model giống nhau:

```text
Task
 ↓
Pool
 ↓
Worker Thread
```

Nhưng Qt tích hợp tự nhiên với:

```text
QObject
Signal
Slot
Qt Event Loop
GUI
```

---

# 29. So sánh

| `ThreadPoolExecutor`    | `QThreadPool`         |
| ----------------------- | --------------------- |
| Python standard library | Qt                    |
| `Future`                | `QRunnable`           |
| `submit()`              | `start()`             |
| `Future.result()`       | Signals/custom result |
| `Future.exception()`    | Signal error          |
| Python concurrency      | Qt concurrency        |
| Không phụ thuộc GUI     | Tích hợp Qt           |

---

# 30. Một điểm khác biệt lớn

Với `ThreadPoolExecutor`:

```python
future = executor.submit(task)

result = future.result()
```

Bạn có abstraction:

```text
Future
```

Với `QThreadPool`:

```text
QRunnable
```

không tự cung cấp Future tương đương.

Bạn thường thiết kế:

```text
QRunnable
   │
   ▼
Signals
   │
   ├── result
   ├── error
   └── finished
```

---

# 31. `QThreadPool` không thay thế `asyncio`

Cũng cần phân biệt:

```text
QThreadPool
```

và:

```text
asyncio
```

### QThreadPool

```text
OS threads
```

### asyncio

```text
event loop
+
coroutines
```

Nếu có:

```text
1000 network operations
```

thì asyncio có thể rất hiệu quả.

Nếu có:

```text
blocking library
```

thì thread pool thường phù hợp hơn.

Buổi 46 chúng ta sẽ kết hợp PySide6 với asyncio.

---

# 32. Thread Pool Lifecycle

Có thể tạo:

```python
pool = QThreadPool()
```

Sau đó:

```python
pool.start(task1)
pool.start(task2)
pool.start(task3)
```

Khi task hoàn thành:

```text
Task
 ↓
finished
 ↓
QRunnable released
```

Pool tiếp tục sống.

---

# 33. `expiryTimeout`

QThreadPool có cơ chế thread idle timeout.

Bạn có thể xem:

```python
pool.expiryTimeout()
```

và thiết lập:

```python
pool.setExpiryTimeout(30000)
```

Ý tưởng:

```text
Task finished
     ↓
Thread idle
     ↓
idle timeout
     ↓
thread may be released
```

Điều này giúp pool quản lý resource.

---

# 34. `activeThreadCount()`

Có thể kiểm tra:

```python
pool.activeThreadCount()
```

Ví dụ:

```text
max = 8
active = 5
```

nghĩa là hiện có khoảng 5 thread đang hoạt động.

Rất hữu ích cho dashboard.

Ví dụ:

```text
Workers: 5 / 8
```

---

# 35. `clear()`

Có:

```python
pool.clear()
```

Dùng để loại bỏ các runnable đang **chờ chạy**.

Điểm quan trọng:

> `clear()` không phải là "kill những task đang chạy".

Mental model:

```text
Running:
A B C D

Waiting:
E F G H

clear()
 ↓

Running:
A B C D

Waiting:
empty
```

---

# 36. Đây là một distinction quan trọng

```text
clear()
```

khác:

```text
cancel running task
```

Đối với task đang chạy:

```text
QRunnable.run()
```

vẫn phải tự hỗ trợ cancellation.

---

# 37. Cancellation với ThreadPool

Ta vẫn quay lại bài học Buổi 42:

```text
cooperative cancellation
```

Ví dụ task:

```python
if self.token.is_cancelled():
    return
```

Không nên:

```text
kill thread
```

Thread pool càng không phải nơi để "giết thread" tùy ý.

---

# 38. Priority

QThreadPool hỗ trợ priority khi start runnable.

Ví dụ khái niệm:

```python
pool.start(task, priority)
```

Có thể dùng priority để scheduler ưu tiên một số task.

Nhưng:

> Không nên lạm dụng priority để thay thế một task scheduler/domain scheduler rõ ràng.

---

# 39. Architecture cho Download Manager

Sau này ở Buổi 48 ta có thể có:

```text
                 Download Manager
                         │
                         ▼
                    QThreadPool
              ┌──────────┼──────────┐
              ▼          ▼          ▼
          Download A Download B Download C
              │          │          │
              ▼          ▼          ▼
           Signals    Signals    Signals
              │          │          │
              └──────────┼──────────┘
                         ▼
                        GUI
```

GUI:

```text
Download A  ███████░░ 70%
Download B  ███░░░░░░ 30%
Download C  █████████ 100%
```

---

# 40. Architecture cho Crawler Dashboard

Ví dụ:

```text
Crawler Dashboard
        │
        ▼
   QThreadPool
        │
 ┌──────┼───────┐
 ▼      ▼       ▼
Task A Task B  Task C
 │      │       │
 ▼      ▼       ▼
Story  Story   Story
```

Mỗi task:

```text
progress
result
error
finished
```

GUI:

```text
Task A  80%
Task B  40%
Task C 100%
```

Đây là bước tiến rất lớn so với:

```text
1 QThread
1 Worker
1 Task
```

---

# 41. Bài tập 1 — Hello ThreadPool

Tạo:

```python
class Task(QRunnable):

    def run(self):
        print("Hello")
```

Sau đó:

```python
pool = QThreadPool.globalInstance()

pool.start(Task())
```

---

# 42. Bài tập 2 — 20 Tasks

Tạo:

```text
Task 1
Task 2
...
Task 20
```

Mỗi task:

```python
time.sleep(1)
```

In:

```text
started
finished
```

Quan sát concurrency.

---

# 43. Bài tập 3 — Giới hạn 3 thread

```python
pool.setMaxThreadCount(3)
```

Submit:

```text
20 tasks
```

Quan sát:

```text
Task 1 ─┐
Task 2 ─┼─ running
Task 3 ─┘

Task 4+
waiting
```

---

# 44. Bài tập 4 — Active Threads

Hiển thị:

```python
pool.activeThreadCount()
```

GUI:

```text
Active workers: 3
```

---

# 45. Bài tập 5 — File Processing

Có:

```text
100 files
```

Mỗi file là một `QRunnable`.

Pool:

```text
maxThreadCount = 4
```

Xử lý đồng thời tối đa 4 file.

---

# 46. Bài tập 6 — Story Metadata

Tạo:

```text
Story A
Story B
Story C
Story D
Story E
```

Mỗi story:

```text
sleep(1)
```

Chạy qua:

```text
QThreadPool
```

Quan sát task scheduling.

---

# 47. Bài tập 7 — Clear Queue

Submit:

```text
100 tasks
```

sau đó:

```python
pool.clear()
```

Quan sát:

```text
Running tasks
```

và:

```text
Waiting tasks
```

Để hiểu `clear()` không phải cancellation.

---

# 48. Bài tập 8 — So sánh

Viết hai phiên bản:

### Version A

```text
100 tasks
100 QThread
```

### Version B

```text
100 tasks
QThreadPool
max = 8
```

So sánh:

```text
code
resource
lifecycle
concurrency
```

---

# 49. Bài tập 9 — ThreadPool + GUI

UI:

```text
┌────────────────────────────┐
│ Tasks: 20                  │
│                            │
│ Active workers: 4          │
│                            │
│ [Start]                    │
└────────────────────────────┘
```

Submit 20 tasks.

GUI không được freeze.

---

# 50. Bài tập 10 — Chuẩn bị cho Buổi 44

Tạo:

```text
Task
Signals
QThreadPool
GUI
```

Architecture:

```text
QRunnable
   │
   ├── run()
   │
   └── signals
          │
          ├── started
          ├── progress
          ├── result
          ├── error
          └── finished
```

Ở Buổi 44 chúng ta sẽ biến architecture này thành code hoàn chỉnh.

---

# 51. Checklist Buổi 43

Bạn cần hiểu:

### `QThreadPool`

```text
quản lý pool của threads
```

### `QRunnable`

```text
đại diện cho task
```

### `maxThreadCount`

```text
giới hạn concurrency
```

### `activeThreadCount`

```text
số thread đang active
```

### `clear()`

```text
xóa task đang chờ
```

### `waitForDone()`

```text
chờ tất cả task hoàn thành
```

### Thread reuse

```text
Thread
 ↓
Task
 ↓
Pool
 ↓
Task khác
```

---

# 52. Mental Model quan trọng nhất

Hãy chuyển mental model từ:

```text
                  QThread
                     │
                     ▼
                   Worker
                     │
                     ▼
                    Task
```

sang:

```text
                     QThreadPool
                          │
             ┌────────────┼────────────┐
             │            │            │
             ▼            ▼            ▼
          Thread 1     Thread 2     Thread 3
             │            │            │
             ▼            ▼            ▼
           Task A       Task B       Task C

             Task D ───────────────► Queue
             Task E ───────────────► Queue
             Task F ───────────────► Queue
```

Công thức:

```text
QRunnable
    +
QThreadPool
    =
Task-based concurrency
```

Và so với kiến thức bạn đã học:

```text
QThread + Worker
    → long-running worker / lifecycle / event-driven

QThreadPool + QRunnable
    → nhiều task độc lập / bounded concurrency
```

**Buổi 44 — `QRunnable`** sẽ đi sâu vào phần còn thiếu: **làm thế nào `QRunnable` giao tiếp với GUI bằng Signal, trả `result`, báo `error`, `finished`, `progress`, và thiết kế một `WorkerSignals` chuẩn**. Đây cũng là lúc chúng ta xây một `TaskRunner` có thể tái sử dụng cho các project PySide6 sau này.
