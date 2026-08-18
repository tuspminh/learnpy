Được. Tôi sẽ dạy **`ThreadPoolExecutor` từ nền tảng → hiểu cơ chế → pattern thực tế → production**, theo kiểu Deep Dive giống các khóa Python trước của bạn.

# ThreadPoolExecutor Deep Dive — Roadmap

## Phần I — Foundation

1. Thread là gì?
2. `concurrent.futures` là gì?
3. `ThreadPoolExecutor` là gì?
4. `submit()` và `Future`
5. `result()`
6. `done()`, `running()`, `cancelled()`
7. `wait()`
8. `as_completed()`
9. `map()`
10. `shutdown()`

## Phần II — ThreadPoolExecutor Deep Dive

11. Worker thread và task queue
12. `max_workers`
13. Thread lifecycle
14. Future state machine
15. Exception trong worker
16. Timeout
17. Cancel task
18. `wait()` với `FIRST_COMPLETED`
19. `wait()` với `FIRST_EXCEPTION`
20. `as_completed()` nâng cao

## Phần III — Patterns

21. Fan-out / Fan-in
22. Producer → Worker → Collector
23. Parallel I/O
24. Batch processing
25. Retry task
26. Rate limiting
27. Progress tracking
28. Bounded concurrency
29. Backpressure
30. Thread-safe result collection

## Phần IV — Thread Safety

31. Race condition
32. GIL và ThreadPoolExecutor
33. Shared state
34. Lock
35. RLock
36. Condition
37. Semaphore
38. Event
39. Queue
40. Deadlock

## Phần V — Production

41. Error handling
42. Retry architecture
43. Graceful shutdown
44. Cancellation
45. Logging
46. Timeout strategy
47. Monitoring
48. Structured result
49. Worker architecture
50. Mini Project: **Concurrent Downloader**

Sau đó chúng ta có thể xây tiếp:

**ThreadPoolExecutor → Crawl Worker → Queue Server → Crawler Plugin**

rất phù hợp với hệ thống crawler mà bạn đang xây dựng.

---

# Buổi 1 — ThreadPoolExecutor là gì?

## 1. Bài toán

Giả sử chúng ta có 5 công việc:

```python
import time


def task(n):
    print(f"Start {n}")
    time.sleep(2)
    print(f"Done {n}")
    return n * 2
```

Nếu chạy tuần tự:

```python
for i in range(5):
    task(i)
```

thời gian xấp xỉ:

```text
2 + 2 + 2 + 2 + 2
= 10 giây
```

Nhưng các task này độc lập với nhau.

Ta có thể cho nhiều thread xử lý đồng thời.

```text
                 ┌── task(0)
                 │
Main Thread ─────┼── task(1)
                 │
                 ├── task(2)
                 │
                 ├── task(3)
                 │
                 └── task(4)
```

Nếu có 5 worker:

```text
~2 giây
```

thay vì:

```text
~10 giây
```

Đây chính là một trong những use case quan trọng của `ThreadPoolExecutor`.

---

# 2. `ThreadPoolExecutor` nằm ở đâu?

Python có module:

```python
concurrent.futures
```

Trong đó có hai executor chính:

```python
ThreadPoolExecutor
ProcessPoolExecutor
```

Import:

```python
from concurrent.futures import ThreadPoolExecutor
```

Ý tưởng:

```text
Executor
   │
   ├── quản lý worker
   │
   ├── nhận task
   │
   ├── đưa task vào queue
   │
   └── trả về Future
```

---

# 3. Ví dụ đầu tiên

```python
from concurrent.futures import ThreadPoolExecutor
import time


def task(n):
    print(f"Start {n}")

    time.sleep(2)

    print(f"Done {n}")

    return n * 2


with ThreadPoolExecutor(max_workers=5) as executor:

    futures = []

    for i in range(5):
        future = executor.submit(task, i)
        futures.append(future)

    for future in futures:
        print(future.result())
```

Có thể nhận được:

```text
Start 0
Start 1
Start 2
Start 3
Start 4

Done 0
Done 1
Done 2
Done 3
Done 4

0
2
4
6
8
```

Điểm quan trọng nhất của bài hôm nay:

```python
executor.submit(...)
```

**không trả về kết quả của task.**

Nó trả về một object:

```python
Future
```

---

# 4. `Future` là gì?

Đây là khái niệm cực kỳ quan trọng.

Khi viết:

```python
future = executor.submit(task, 10)
```

không có nghĩa:

```python
result = task(10)
```

Mà là:

```text
submit task
     │
     ▼
┌─────────────┐
│   Future    │
│             │
│  pending    │
└─────────────┘
     │
     │ worker xử lý
     ▼
┌─────────────┐
│   Future    │
│             │
│  finished   │
│  result=20  │
└─────────────┘
```

`Future` là một **đại diện cho kết quả trong tương lai**.

---

# 5. `submit()` không block

Ví dụ:

```python
import time
from concurrent.futures import ThreadPoolExecutor


def task(n):
    time.sleep(3)
    return n


with ThreadPoolExecutor(max_workers=3) as executor:

    start = time.time()

    future1 = executor.submit(task, 1)
    future2 = executor.submit(task, 2)
    future3 = executor.submit(task, 3)

    print("Tasks submitted")

    print(time.time() - start)
```

Bạn sẽ thấy:

```text
Tasks submitted
~0.00
```

`submit()` gần như trả về ngay.

Trong khi task vẫn đang chạy:

```text
Main Thread
     │
     ├── submit(task1) ──────► Future
     │
     ├── submit(task2) ──────► Future
     │
     ├── submit(task3) ──────► Future
     │
     ▼
  tiếp tục chạy
```

---

# 6. `result()` mới là chỗ block

Ví dụ:

```python
future = executor.submit(task, 10)

print("Before result")

result = future.result()

print("After result")
```

Nếu task mất 3 giây:

```text
Before result
     │
     │
     │ 3 seconds
     ▼
After result
```

`result()` sẽ chờ task hoàn thành.

---

# 7. Một điểm rất dễ hiểu nhầm

Code:

```python
future1 = executor.submit(task, 1)
future2 = executor.submit(task, 2)
future3 = executor.submit(task, 3)

result1 = future1.result()
result2 = future2.result()
result3 = future3.result()
```

**không có nghĩa là task chạy tuần tự.**

Ba task đã được submit trước:

```text
submit task1 ──┐
submit task2 ──┼──► Worker pool
submit task3 ──┘
```

Sau đó main thread mới lấy kết quả.

---

# 8. `max_workers`

Ví dụ:

```python
ThreadPoolExecutor(max_workers=3)
```

nghĩa là pool có tối đa:

```text
3 worker threads
```

Nếu submit:

```python
10 tasks
```

thì không phải 10 thread được tạo.

Mà:

```text
Worker 1 ── task 1
Worker 2 ── task 2
Worker 3 ── task 3

           ↓

Worker 1 ── task 4
Worker 2 ── task 5
Worker 3 ── task 6

           ↓

...
```

Có thể hình dung:

```text
                 ThreadPool
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
     Worker 1     Worker 2     Worker 3
        │            │            │
        ▼            ▼            ▼
      Task         Task         Task
```

---

# 9. Tại sao gọi là Pool?

Vì thread được **tái sử dụng**.

Không phải:

```text
Task 1 → tạo thread
Task 1 → destroy thread

Task 2 → tạo thread
Task 2 → destroy thread
```

Mà:

```text
Worker Thread
     │
     ├── Task 1
     ├── Task 4
     ├── Task 7
     ├── Task 10
     └── ...
```

Đây là một trong những lý do thread pool hiệu quả hơn việc tự tạo thread cho từng task.

---

# 10. Vì sao dùng `with`?

Ta thường viết:

```python
with ThreadPoolExecutor(max_workers=5) as executor:
    ...
```

thay vì:

```python
executor = ThreadPoolExecutor(max_workers=5)

...

executor.shutdown()
```

`with` đảm bảo executor được shutdown đúng cách.

Tương đương về ý tưởng:

```python
executor = ThreadPoolExecutor(max_workers=5)

try:
    ...
finally:
    executor.shutdown()
```

---

# 11. Ví dụ thực tế: tải nhiều URL

Đây là use case rất phù hợp với ThreadPoolExecutor.

```python
from concurrent.futures import ThreadPoolExecutor
import requests


def download(url):
    response = requests.get(url)

    return {
        "url": url,
        "status": response.status_code,
        "size": len(response.content),
    }


urls = [
    "https://example.com",
    "https://example.org",
    "https://example.net",
]


with ThreadPoolExecutor(max_workers=3) as executor:

    futures = [
        executor.submit(download, url)
        for url in urls
    ]

    for future in futures:
        result = future.result()
        print(result)
```

Đây chính là pattern rất quan trọng cho các ứng dụng:

```text
Crawler
Downloader
HTTP client
File processing
API requests
Database I/O
Image downloading
TTS generation
```

---

# 12. ThreadPoolExecutor phù hợp với loại task nào?

Điểm này cực kỳ quan trọng.

### Rất phù hợp

**I/O-bound**

Ví dụ:

```text
HTTP request
Download file
Upload file
Read file
Database query
API call
Web scraping
```

Ví dụ:

```python
requests.get(...)
```

hoặc:

```python
response = api_client.fetch(...)
```

Trong lúc thread chờ I/O:

```text
Thread
  │
  ├── gửi request
  │
  ├── WAIT
  │
  ├── WAIT
  │
  └── nhận response
```

Thread có thể giúp tăng throughput.

---

# 13. Không nên mặc định dùng ThreadPoolExecutor cho CPU-bound

Ví dụ:

```python
def calculate():
    for i in range(100_000_000):
        ...
```

Đây là CPU-bound.

Trong trường hợp này, thường cần xem xét:

```python
ProcessPoolExecutor
```

thay vì:

```python
ThreadPoolExecutor
```

vì Python có **GIL** đối với CPython.

Nhưng chúng ta sẽ học rất kỹ GIL ở phần sau.

---

# 14. Mental Model quan trọng nhất

Hãy nhớ mô hình này:

```text
                  ThreadPoolExecutor
                         │
                         │ submit()
                         ▼
                   ┌───────────┐
                   │ Task Queue│
                   └─────┬─────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
           Worker 1   Worker 2   Worker 3
              │          │          │
              ▼          ▼          ▼
            Task A     Task B     Task C
              │          │          │
              └──────────┼──────────┘
                         ▼
                      Future
                         │
                         ▼
                    result()
```

Nếu hiểu được sơ đồ này thì những bài sau sẽ dễ hơn rất nhiều.

---

# 15. Bài tập Buổi 1

### Bài 1

Viết chương trình chạy 5 task tuần tự:

```python
task(1)
task(2)
task(3)
task(4)
task(5)
```

Mỗi task:

```python
time.sleep(2)
```

Đo thời gian bằng:

```python
time.perf_counter()
```

---

### Bài 2

Chuyển chương trình trên sang:

```python
ThreadPoolExecutor(max_workers=5)
```

So sánh thời gian.

---

### Bài 3

Thử:

```python
max_workers=1
max_workers=2
max_workers=3
max_workers=5
```

Quan sát thời gian.

---

### Bài 4 — Quan trọng

Viết:

```python
def task(n):
    print(f"start {n}")
    time.sleep(2)
    print(f"finish {n}")
    return n * 10
```

Sau đó:

```python
future = executor.submit(task, 5)
```

Hãy kiểm tra:

```python
print(type(future))
print(future)
```

Sau đó:

```python
print(future.done())
```

và:

```python
print(future.result())
print(future.done())
```

Mục tiêu là tự quan sát vòng đời:

```text
Future
  ↓
PENDING
  ↓
RUNNING
  ↓
FINISHED
  ↓
result
```

---

## Kiến thức cần nắm chắc sau Buổi 1

Bạn cần phân biệt rõ:

```text
Thread
    ↓
Worker
    ↓
ThreadPool
    ↓
Executor
    ↓
submit()
    ↓
Future
    ↓
result()
```

Đặc biệt:

> **`submit()` gửi công việc và trả về `Future`; `Future.result()` lấy kết quả và có thể block cho tới khi công việc hoàn thành.**

**Buổi 2** chúng ta sẽ đi sâu vào **`submit()` + `Future`**, đặc biệt là `done()`, `running()`, `cancelled()`, `exception()`, `result(timeout=...)` và **Future state machine**.
