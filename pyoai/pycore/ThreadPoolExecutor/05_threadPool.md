# ThreadPoolExecutor Deep Dive — Buổi 5

## `max_workers` và Worker Thread — ThreadPool thực sự hoạt động thế nào?

Sau 4 buổi, chúng ta đã đi từ:

```text
submit()
Future
wait()
as_completed()
map()
```

Hôm nay đi xuống **một tầng thấp hơn**:

> Khi gọi `ThreadPoolExecutor(max_workers=5)`, Python thực sự làm gì?

Và câu hỏi quan trọng hơn:

> **Nên chọn `max_workers` bằng bao nhiêu?**

---

# 1. `max_workers` là gì?

Khi viết:

```python
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(
    max_workers=5
)
```

ta đang nói:

> ThreadPool được phép sử dụng tối đa 5 worker thread đồng thời.

Ví dụ có 20 task:

```text
20 tasks
   │
   ▼
ThreadPool
   │
   ├── Worker 1
   ├── Worker 2
   ├── Worker 3
   ├── Worker 4
   └── Worker 5
```

Chỉ tối đa 5 task chạy cùng lúc.

```text
Task 1 ──► Worker 1
Task 2 ──► Worker 2
Task 3 ──► Worker 3
Task 4 ──► Worker 4
Task 5 ──► Worker 5

Task 6 ──► WAIT
Task 7 ──► WAIT
...
```

---

# 2. `max_workers` không phải số task

Đây là lỗi hiểu nhầm phổ biến.

```python
ThreadPoolExecutor(max_workers=5)
```

không có nghĩa:

```text
chỉ chạy 5 task
```

Mà nghĩa là:

```text
tối đa 5 worker chạy task đồng thời
```

Bạn hoàn toàn có thể:

```python
for i in range(10000):
    executor.submit(task, i)
```

với:

```python
max_workers=5
```

Khi đó:

```text
10000 tasks
    │
    ▼
  queue
    │
    ├── Worker 1
    ├── Worker 2
    ├── Worker 3
    ├── Worker 4
    └── Worker 5
```

---

# 3. ThreadPool không tạo 10.000 thread

Ví dụ:

```python
with ThreadPoolExecutor(max_workers=5) as executor:

    for i in range(10000):
        executor.submit(task, i)
```

Không phải:

```text
10,000 tasks
     ↓
10,000 threads
```

Mà:

```text
10,000 tasks
     ↓
task queue
     ↓
5 worker threads
```

Đây chính là ý nghĩa của **pool**.

---

# 4. Worker thread được tái sử dụng

Giả sử:

```python
max_workers=3
```

Có:

```text
Worker 1
Worker 2
Worker 3
```

Task:

```text
A
B
C
D
E
F
```

Có thể diễn ra:

```text
Worker 1 → A → D
Worker 2 → B → E
Worker 3 → C → F
```

Không phải:

```text
A → tạo Thread A → destroy
B → tạo Thread B → destroy
C → tạo Thread C → destroy
```

Mà worker sống trong pool và lấy task tiếp theo.

---

# 5. Vì sao phải dùng ThreadPool?

Tạo thread có overhead.

Nếu tự làm:

```python
import threading

thread = threading.Thread(...)
thread.start()
```

với hàng nghìn task, bạn có thể tạo ra rất nhiều thread.

Điều này dẫn đến:

```text
memory
context switching
thread scheduling
resource usage
```

ThreadPool giải quyết bằng cách:

```text
ít thread
+
nhiều task
+
tái sử dụng worker
```

---

# 6. Worker lifecycle

Mental model:

```text
ThreadPoolExecutor
        │
        ▼
    Worker Thread
        │
        ▼
    chờ task
        │
        ▼
    nhận task
        │
        ▼
    chạy task
        │
        ▼
    hoàn thành
        │
        ▼
    quay lại chờ task
```

Tức là:

```text
WAIT
 ↓
TASK
 ↓
WAIT
 ↓
TASK
 ↓
WAIT
```

Worker không chết sau mỗi task.

---

# 7. Một worker có thể xử lý nhiều task

Ví dụ:

```python
def task(n):
    print(
        n,
        threading.current_thread().name
    )
```

Chạy:

```python
from concurrent.futures import ThreadPoolExecutor
import threading


def task(n):
    print(
        n,
        threading.current_thread().name
    )


with ThreadPoolExecutor(max_workers=3) as executor:

    for i in range(10):
        executor.submit(task, i)
```

Bạn có thể thấy:

```text
0 ThreadPoolExecutor-0_0
1 ThreadPoolExecutor-0_1
2 ThreadPoolExecutor-0_2
3 ThreadPoolExecutor-0_0
4 ThreadPoolExecutor-0_1
5 ThreadPoolExecutor-0_2
...
```

Điều này cho thấy worker được tái sử dụng.

---

# 8. ThreadPool tạo thread khi cần

Một chi tiết quan trọng:

```python
ThreadPoolExecutor(max_workers=10)
```

không nhất thiết có nghĩa:

> ngay lập tức tạo đủ 10 thread.

Executor có thể tạo worker khi có công việc cần xử lý, tới giới hạn `max_workers`.

Ví dụ:

```python
executor = ThreadPoolExecutor(max_workers=10)
```

nhưng chỉ submit:

```python
executor.submit(task)
```

thì không cần thiết phải có 10 worker đang hoạt động.

Mental model:

```text
max_workers=10

submit task 1
    ↓
có worker

submit task 2
    ↓
thêm worker nếu cần

...

tối đa
10 workers
```

---

# 9. Task queue

Đây là một khái niệm cực kỳ quan trọng.

Khi:

```python
executor.submit(task, 1)
```

task được đưa vào một hàng đợi nội bộ.

Có thể hình dung:

```text
                 Executor
                     │
                     ▼
               ┌───────────┐
               │ Task Queue│
               ├───────────┤
               │ Task 4    │
               │ Task 5    │
               │ Task 6    │
               │ Task 7    │
               └─────┬─────┘
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Worker 1   Worker 2   Worker 3
```

Worker lấy task từ queue.

---

# 10. Điều gì xảy ra khi task nhiều hơn worker?

Ví dụ:

```python
max_workers=3
```

submit:

```text
10 tasks
```

Ta có:

```text
Running:

Task 1 → Worker 1
Task 2 → Worker 2
Task 3 → Worker 3
```

Các task còn lại:

```text
Queue:

Task 4
Task 5
Task 6
Task 7
Task 8
Task 9
Task 10
```

Khi Worker 2 xong:

```text
Worker 2
   │
   ├── Task 2 DONE
   │
   ▼
Task 4
```

Sau đó:

```text
Worker 2 → Task 4
```

---

# 11. Vì vậy `max_workers` chính là concurrency limit

Ví dụ:

```python
ThreadPoolExecutor(max_workers=20)
```

có thể hiểu:

```text
max 20 task đang chạy đồng thời
```

Đây rất quan trọng với crawler.

Nếu bạn có:

```text
1000 URL
```

nhưng:

```text
max_workers=10
```

thì:

```text
1000 URLs
     ↓
10 active requests
     ↓
990 waiting
```

---

# 12. Nhưng `max_workers` càng lớn không phải càng nhanh

Đây là bài học rất quan trọng.

Bạn có thể nghĩ:

```text
1 worker   → chậm
10 workers → nhanh
100 workers → rất nhanh
1000 workers → cực nhanh
```

Không đúng.

Thường có:

```text
concurrency
    │
    │          ┌───────
    │        /
    │      /
    │    /
    │  /
    │ /
    └──────────────────
          workers
```

Tới một điểm:

```text
thêm worker
    ↓
không tăng throughput đáng kể
```

thậm chí:

```text
thêm worker
    ↓
performance giảm
```

---

# 13. Tại sao quá nhiều thread lại chậm?

Có nhiều nguyên nhân.

### 1. Context switching

CPU phải chuyển giữa nhiều thread.

```text
Thread A
   ↓
Thread B
   ↓
Thread C
   ↓
Thread D
   ↓
...
```

Quá nhiều thread → overhead tăng.

---

### 2. Memory

Mỗi thread có stack và metadata.

Nhiều thread:

```text
100 threads
200 threads
1000 threads
```

→ resource tăng.

---

### 3. External bottleneck

Ví dụ server chỉ cho:

```text
20 request/s
```

Bạn tạo:

```text
200 workers
```

không biến server thành:

```text
200 request/s
```

Bạn chỉ tạo thêm contention.

---

### 4. Connection pool

HTTP client có connection pool giới hạn.

Ví dụ:

```text
ThreadPool
100 workers
      ↓
HTTP connection pool
10 connections
```

100 thread không đồng nghĩa 100 request hiệu quả.

---

# 14. ThreadPoolExecutor đặc biệt phù hợp I/O-bound

Ví dụ:

```text
HTTP request
   ↓
WAIT
   ↓
response
```

Trong lúc chờ:

```text
Thread
   │
   └── WAITING
```

CPU có thể làm công việc khác.

Do đó có thể dùng:

```text
10
20
50
```

worker tùy workload.

Nhưng phải benchmark.

---

# 15. Ví dụ benchmark đơn giản

```python
import time
from concurrent.futures import ThreadPoolExecutor


def task(_):
    time.sleep(1)


for workers in [1, 2, 4, 8, 16]:

    start = time.perf_counter()

    with ThreadPoolExecutor(
        max_workers=workers
    ) as executor:

        list(executor.map(task, range(20)))

    elapsed = time.perf_counter() - start

    print(
        workers,
        elapsed
    )
```

Kỳ vọng gần đúng:

```text
workers    time
----------------
1          20s
2          10s
4           5s
8           3s
16          2s
```

Không nhất thiết chính xác vì còn overhead và scheduler.

---

# 16. Với I/O-bound, số worker có thể lớn hơn CPU core

Đây là điểm rất quan trọng.

Nếu máy có:

```text
8 CPU cores
```

không có nghĩa:

```text
max_workers = 8
```

đối với I/O-bound.

Ví dụ:

```text
HTTP requests
```

có thể thử:

```text
16
32
64
```

và benchmark.

Vì phần lớn thời gian worker đang:

```text
WAITING
```

chứ không sử dụng CPU liên tục.

---

# 17. Nhưng CPU-bound thì khác

Giả sử:

```python
def cpu_task(n):
    total = 0

    for i in range(50_000_000):
        total += i

    return total
```

Đây là:

```text
CPU-bound
```

ThreadPoolExecutor không phải lựa chọn mặc định tốt trong CPython cho loại workload này.

Tăng:

```text
1
2
4
8
16
```

thread có thể không mang lại speedup tuyến tính.

Lúc này cần xem xét:

```python
ProcessPoolExecutor
```

hoặc các thư viện native giải phóng GIL.

---

# 18. GIL — chỉ cần hiểu sơ bộ hôm nay

GIL = **Global Interpreter Lock** trong CPython.

Ở mức đơn giản:

```text
CPU-bound Python code
        ↓
GIL
        ↓
multiple threads
```

không thể kỳ vọng nhiều thread Python bytecode chạy CPU song song như nhiều process.

Nhưng:

```text
I/O
 ↓
thread waits
```

là một trường hợp ThreadPoolExecutor rất hữu ích.

Buổi sau chúng ta sẽ đi sâu riêng vào GIL.

---

# 19. `max_workers` cho crawler

Đây là phần rất phù hợp với dự án của bạn.

Giả sử crawler:

```text
1000 URLs
```

Một request trung bình:

```text
500 ms
```

Nếu:

```text
workers = 1
```

throughput lý tưởng:

```text
~2 request/s
```

Nếu:

```text
workers = 10
```

có thể lý tưởng:

```text
~20 request/s
```

Nhưng thực tế còn phụ thuộc:

```text
network
server
DNS
connection
rate limit
response size
CPU
database
```

---

# 20. Đừng nhầm `max_workers` với rate limit

Ví dụ:

```python
ThreadPoolExecutor(max_workers=20)
```

không có nghĩa:

```text
20 requests / second
```

Nó nghĩa:

```text
tối đa 20 task đồng thời
```

Hai khái niệm khác nhau:

### Concurrency

```text
bao nhiêu task đang chạy cùng lúc?
```

### Rate

```text
bao nhiêu task được bắt đầu mỗi giây?
```

Ví dụ:

```text
20 concurrent workers
+
5 requests/second
```

hoàn toàn có thể tồn tại cùng nhau.

Sau này ta sẽ học:

```text
Semaphore
Rate Limiter
Token Bucket
```

---

# 21. `max_workers` và server

Giả sử server có giới hạn:

```text
10 concurrent connections
```

Bạn dùng:

```python
max_workers=100
```

có thể gây:

```text
429 Too Many Requests
503
connection refused
timeouts
```

Do đó crawler production cần:

```text
ThreadPool
   +
Rate Limiter
   +
Retry
   +
Timeout
```

Không chỉ đơn giản:

```python
max_workers=100
```

---

# 22. Thread name

Trong debugging, nên đặt tên worker:

```python
ThreadPoolExecutor(
    max_workers=5,
    thread_name_prefix="crawler"
)
```

Ví dụ:

```python
from concurrent.futures import ThreadPoolExecutor
import threading


def task(n):
    print(
        n,
        threading.current_thread().name
    )


with ThreadPoolExecutor(
    max_workers=3,
    thread_name_prefix="crawler",
) as executor:

    list(
        executor.map(
            task,
            range(10)
        )
    )
```

Bạn có thể thấy:

```text
crawler_0
crawler_1
crawler_2
```

Điều này rất hữu ích khi logging.

---

# 23. Production logging

Ví dụ:

```python
import logging
import threading


logger = logging.getLogger(__name__)


def task(url):

    logger.info(
        "Start %s [%s]",
        url,
        threading.current_thread().name,
    )
```

Log:

```text
Start url1 [crawler_0]
Start url2 [crawler_1]
Start url3 [crawler_2]
```

Khi có lỗi production, thông tin thread giúp debug dễ hơn.

---

# 24. Một thí nghiệm rất đáng làm

Chạy:

```python
from concurrent.futures import ThreadPoolExecutor
import threading
import time


def task(n):

    name = threading.current_thread().name

    print(
        f"START {n} - {name}"
    )

    time.sleep(1)

    print(
        f"END {n} - {name}"
    )


with ThreadPoolExecutor(
    max_workers=3,
    thread_name_prefix="worker",
) as executor:

    futures = [
        executor.submit(task, i)
        for i in range(10)
    ]

    for future in futures:
        future.result()
```

Bạn hãy quan sát:

```text
worker_0
worker_1
worker_2
```

được tái sử dụng cho nhiều task.

Đây chính là **Thread Pool**.

---

# 25. Worker không nhất thiết được tạo ngay khi Executor được tạo

Ví dụ:

```python
executor = ThreadPoolExecutor(
    max_workers=10
)
```

lúc này chưa có nghĩa là:

```text
10 worker đang chạy
```

Sau khi:

```python
executor.submit(task)
```

executor mới cần worker để thực hiện task.

Điều này giúp pool không tạo resource dư thừa ngay từ đầu.

---

# 26. Khi shutdown xảy ra

Khi:

```python
with ThreadPoolExecutor(...) as executor:
    ...
```

thoát khỏi `with`, executor sẽ shutdown.

Mental model:

```text
submit tasks
     ↓
workers xử lý
     ↓
tasks hoàn thành
     ↓
shutdown
     ↓
workers kết thúc
```

Ta sẽ học sâu `shutdown()` ở phần sau.

---

# 27. Một lỗi thiết kế nguy hiểm

Không nên mặc định:

```python
max_workers=1000
```

chỉ vì:

> "Tôi muốn crawl thật nhanh."

Cần xem:

```text
Target server
     ↓
network
     ↓
connection pool
     ↓
CPU
     ↓
RAM
     ↓
database
     ↓
rate limit
```

Ví dụ crawler:

```text
1000 workers
     ↓
1000 requests
     ↓
server 429
     ↓
retry
     ↓
2000 requests
     ↓
server càng quá tải
```

Đây là **positive feedback loop rất xấu**.

---

# 28. Quy trình chọn `max_workers`

Trong production, tôi khuyên:

### Bước 1

Xác định workload:

```text
I/O-bound?
CPU-bound?
mixed?
```

### Bước 2

Đo latency:

```text
request = 100ms?
request = 1s?
request = 10s?
```

### Bước 3

Xem giới hạn bên ngoài:

```text
API rate limit
server concurrency
connection pool
```

### Bước 4

Benchmark:

```text
5
10
20
30
50
```

### Bước 5

Chọn điểm throughput tốt mà không gây overload.

---

# 29. Công thức tư duy đơn giản

Với I/O-bound:

```text
throughput ≈ concurrency / latency
```

Ví dụ:

```text
latency = 1 second
concurrency = 10
```

thì throughput lý tưởng xấp xỉ:

```text
10 requests/sec
```

Nếu:

```text
latency = 0.5 sec
concurrency = 10
```

thì lý tưởng:

```text
20 requests/sec
```

Nhưng đây chỉ là mô hình lý thuyết.

Thực tế còn:

```text
network
server
connection
scheduler
CPU
```

---

# 30. Một ví dụ crawler architecture

Với hệ thống crawler của bạn, có thể hình dung:

```text
                  Scheduler
                      │
                      ▼
                URL Queue
                      │
                      ▼
              ThreadPoolExecutor
                      │
             max_workers = N
                      │
       ┌──────────────┼──────────────┐
       ▼              ▼              ▼
   Worker 1       Worker 2       Worker N
       │              │              │
       ▼              ▼              ▼
     HTTP           HTTP           HTTP
       │              │              │
       └──────────────┼──────────────┘
                      ▼
                   Result
                      │
             ┌────────┴────────┐
             ▼                 ▼
          Success             Error
             │                 │
             ▼                 ▼
           Parser            Retry
```

Sau này ta sẽ biến nó thành architecture thật.

---

# 31. Bài tập 1 — Worker reuse

Viết chương trình:

```python
max_workers=3
```

submit:

```text
10 tasks
```

Mỗi task in:

```text
task id
thread name
```

Ví dụ:

```text
task=0 thread=worker_0
task=1 thread=worker_1
task=2 thread=worker_2
task=3 thread=worker_0
...
```

Mục tiêu:

> Chứng minh rằng worker được tái sử dụng.

---

# 32. Bài tập 2 — Benchmark

Chạy:

```text
max_workers:
1
2
4
8
16
32
```

với:

```python
def task(_):
    time.sleep(0.5)
```

và:

```text
100 tasks
```

Đo:

```python
time.perf_counter()
```

Tạo bảng:

```text
workers | elapsed | throughput
--------|---------|-----------
1       | ...     | ...
2       | ...     | ...
4       | ...     | ...
8       | ...     | ...
16      | ...     | ...
32      | ...     | ...
```

Bạn sẽ thấy rất rõ quan hệ:

```text
concurrency
     ↓
throughput
```

---

# 33. Bài tập 3 — Crawler benchmark

Giả lập:

```python
def crawl(url):
    time.sleep(1)
    return url
```

100 URL.

Thử:

```text
workers = 1
5
10
20
50
```

Tính:

```text
elapsed
throughput = total_tasks / elapsed
```

Sau đó trả lời:

> Từ mức worker nào trở đi tốc độ tăng không còn tương ứng?

---

# 34. Bài tập 4 — Thread name

Sử dụng:

```python
thread_name_prefix="crawler"
```

và logging:

```text
2026-08-18 22:10:00 [crawler_0] START url1
2026-08-18 22:10:00 [crawler_1] START url2
```

Mục tiêu là bắt đầu hình thành tư duy **production logging**.

---

# 35. Tổng kết Buổi 5

Bạn cần nắm chắc:

### `max_workers`

```python
ThreadPoolExecutor(
    max_workers=N
)
```

→ số worker thread tối đa có thể chạy đồng thời.

### Worker

```text
worker
  ↓
task
  ↓
done
  ↓
lấy task tiếp theo
```

→ worker được tái sử dụng.

### Task queue

```text
nhiều tasks
    ↓
queue
    ↓
ít workers
```

### Không phải càng nhiều worker càng tốt

```text
workers ↑
   ↓
throughput ↑
   ↓
saturation
   ↓
overhead / bottleneck
   ↓
performance ↓
```

### I/O-bound

ThreadPoolExecutor rất phù hợp.

### CPU-bound

Trong CPython, cần cân nhắc `ProcessPoolExecutor` hoặc các giải pháp khác.

### Crawler

Đừng chỉ nghĩ:

```text
max_workers
```

mà phải nghĩ cả:

```text
max_workers
+
rate limit
+
connection pool
+
timeout
+
retry
+
server capacity
```

---

## Bài tập chính Buổi 5

Hãy xây một benchmark nhỏ:

```text
100 URL
```

Mỗi URL:

```text
sleep 0.5–2s
```

Chạy:

```text
workers = 1
2
4
8
16
32
64
```

Ghi lại:

```text
workers
elapsed
throughput
```

Sau đó dùng kết quả để trả lời:

> **Với workload I/O-bound này, `max_workers` tối ưu của máy bạn nằm khoảng nào, và tại sao?**

**Buổi 6** chúng ta sẽ đi sâu vào một chủ đề cực kỳ quan trọng: **GIL + ThreadPoolExecutor** — tại sao thread rất tốt cho I/O nhưng thường không giúp tăng tốc CPU-bound Python code, GIL thực sự làm gì, và tại sao một số thư viện C/extension lại có thể thay đổi kết luận này.
