# ThreadPoolExecutor Deep Dive — Buổi 6

## GIL, CPU-bound vs I/O-bound và tại sao ThreadPoolExecutor không phải lúc nào cũng nhanh hơn

Buổi 5 chúng ta đã hiểu:

```text
ThreadPoolExecutor
        │
        ├── max_workers
        ├── worker thread
        ├── task queue
        └── worker reuse
```

Hôm nay đi vào phần quan trọng nhất để hiểu **bản chất của Python Thread**:

> **GIL là gì và nó ảnh hưởng thế nào đến ThreadPoolExecutor?**

---

# 1. Trước tiên: ThreadPoolExecutor không đồng nghĩa với parallel CPU

Đây là một trong những hiểu nhầm lớn nhất:

```python
with ThreadPoolExecutor(max_workers=10) as executor:
    ...
```

không có nghĩa:

```text
10 CPU cores
→
10 Python code chạy song song
```

Mà cần phân biệt:

```text
Concurrency
vs
Parallelism
```

---

# 2. Concurrency là gì?

Concurrency nghĩa là:

> Nhiều công việc cùng tiến triển trong cùng một khoảng thời gian.

Ví dụ:

```text
Thread A
   │
   ├── request
   ├── WAIT
   ├── response
   └── process

Thread B
   │
   ├── request
   ├── WAIT
   └── response
```

Trong lúc A đang:

```text
WAITING
```

B có thể làm việc.

---

# 3. Parallelism là gì?

Parallelism nghĩa là:

> Nhiều công việc thực sự chạy đồng thời trên nhiều CPU core.

Ví dụ máy có:

```text
CPU Core 1 → Task A
CPU Core 2 → Task B
CPU Core 3 → Task C
CPU Core 4 → Task D
```

Đây mới là parallel execution thực sự.

---

# 4. ThreadPoolExecutor chủ yếu giúp concurrency

Ví dụ HTTP:

```text
Thread 1 → HTTP request → WAIT
Thread 2 → HTTP request → WAIT
Thread 3 → HTTP request → WAIT
Thread 4 → HTTP request → WAIT
```

Trong thời gian chờ:

```text
network
```

CPU không cần thực hiện Python bytecode liên tục.

Do đó thread rất hiệu quả.

---

# 5. GIL là gì?

GIL = **Global Interpreter Lock**.

Trong CPython, GIL là một cơ chế đồng bộ hóa liên quan đến việc thực thi Python bytecode.

Ở mức đơn giản hóa:

```text
             CPython
                │
             Python
             threads
                │
                ▼
              GIL
                │
       ┌────────┼────────┐
       ▼        ▼        ▼
   Thread A  Thread B  Thread C
```

Tại một thời điểm, chỉ một thread có thể nắm GIL để thực thi Python bytecode trong interpreter theo mô hình GIL truyền thống.

**Lưu ý:** các phiên bản Python hiện đại cũng có hướng triển khai CPython **free-threaded**, nên không nên coi GIL là đặc tính bất biến của mọi bản Python. Nhưng khi học `ThreadPoolExecutor`, mô hình GIL truyền thống vẫn là nền tảng rất quan trọng.

---

# 6. Tại sao GIL tồn tại?

Đây là câu hỏi sâu.

CPython quản lý object bằng nhiều cơ chế nội bộ, nổi bật là:

```text
reference counting
+
garbage collection
+
runtime state
```

Ví dụ:

```python
a = []
b = a
```

Một object có:

```text
reference count
```

Khi thread thay đổi reference count đồng thời, cần đảm bảo các thao tác nội bộ không tạo ra trạng thái race nguy hiểm.

GIL từng giúp đơn giản hóa rất nhiều phần của CPython runtime.

---

# 7. Nhưng GIL không có nghĩa Thread vô dụng

Đây là điểm cực kỳ quan trọng.

Sai:

> Python có GIL nên không nên dùng thread.

Đúng:

> Thread rất hữu ích cho I/O-bound workload, nhưng không phải lựa chọn mặc định để tăng tốc CPU-bound Python bytecode.

---

# 8. I/O-bound là gì?

I/O-bound nghĩa là chương trình dành phần lớn thời gian chờ I/O.

Ví dụ:

```text
HTTP
Database
File
Socket
DNS
API
```

Ví dụ:

```python
def download(url):
    response = requests.get(url)
    return response.text
```

Thời gian:

```text
CPU
 │
 ├── tạo request
 │
 └── WAITING
       │
       │ network
       │
       ▼
    response
       │
       ▼
     CPU
```

Phần lớn thời gian:

```text
WAIT
```

---

# 9. CPU-bound là gì?

CPU-bound nghĩa là phần lớn thời gian dành cho tính toán.

Ví dụ:

```python
def calculate():
    total = 0

    for i in range(100_000_000):
        total += i

    return total
```

Ở đây:

```text
CPU
 │
 ├── calculate
 ├── calculate
 ├── calculate
 └── calculate
```

Không có thời gian chờ I/O đáng kể.

---

# 10. Thí nghiệm đầu tiên

Hãy thử:

```python
import time


def cpu_task():
    total = 0

    for i in range(50_000_000):
        total += i

    return total
```

Chạy một lần:

```python
start = time.perf_counter()

cpu_task()

elapsed = time.perf_counter() - start

print(elapsed)
```

Sau đó chạy hai lần tuần tự:

```python
start = time.perf_counter()

cpu_task()
cpu_task()

elapsed = time.perf_counter() - start

print(elapsed)
```

---

# 11. Sau đó dùng ThreadPoolExecutor

```python
from concurrent.futures import ThreadPoolExecutor
import time


def cpu_task():
    total = 0

    for i in range(50_000_000):
        total += i

    return total


start = time.perf_counter()

with ThreadPoolExecutor(max_workers=2) as executor:
    futures = [
        executor.submit(cpu_task)
        for _ in range(2)
    ]

    for future in futures:
        future.result()

elapsed = time.perf_counter() - start

print(elapsed)
```

Bạn có thể kỳ vọng:

```text
2 threads
```

không nhanh gấp 2 lần.

Thậm chí có thể:

```text
chậm hơn
```

so với chạy tuần tự.

---

# 12. Tại sao?

Hãy hình dung:

```text
CPU-bound Python code

Thread A ───────┐
                │
                ▼
               GIL
                ▲
                │
Thread B ───────┘
```

Hai thread cạnh tranh quyền thực thi Python bytecode.

Ngoài ra còn:

```text
context switching
+
thread scheduling
+
GIL coordination
```

→ overhead.

---

# 13. Context switching

Giả sử:

```text
Thread A
```

đang chạy.

Runtime chuyển sang:

```text
Thread B
```

rồi quay lại:

```text
Thread A
```

Quá trình này có cost.

Nếu workload rất nhỏ:

```text
task = 0.001s
```

thì overhead thread scheduling có thể đáng kể.

Do đó:

```text
parallelism ≠ free
```

---

# 14. Nhưng I/O lại khác

Ví dụ:

```python
def io_task():
    time.sleep(1)
```

Chạy:

```python
with ThreadPoolExecutor(max_workers=10) as executor:
    list(executor.map(io_task, range(10)))
```

Thời gian gần:

```text
~1 second
```

thay vì:

```text
~10 seconds
```

Tại sao?

```text
Thread 1 → sleep
Thread 2 → sleep
Thread 3 → sleep
...
```

Trong lúc một thread đang chờ, thread khác có thể tiến triển.

---

# 15. So sánh trực quan

### CPU-bound

```text
Task A ███████████████
Task B ███████████████
Task C ███████████████

       CPU
        │
        ▼
      GIL
```

Thread không tạo ra speedup CPU như bạn mong muốn.

---

### I/O-bound

```text
A █ WAIT █ WAIT █
B █ WAIT █ WAIT █
C █ WAIT █ WAIT █
D █ WAIT █ WAIT █
```

Trong lúc một task:

```text
WAIT
```

task khác có thể chạy.

---

# 16. Đây là lý do crawler dùng ThreadPoolExecutor

Crawler thường:

```text
request
  ↓
WAIT network
  ↓
response
  ↓
parse
```

Phần:

```text
WAIT network
```

thường lớn.

Ví dụ:

```text
Request = 100ms
Parse = 2ms
```

thì:

```text
98% thời gian
→ network waiting
```

ThreadPoolExecutor rất phù hợp.

---

# 17. Ví dụ crawler

```python
from concurrent.futures import ThreadPoolExecutor
import time


def crawl(url):
    print("START", url)

    # giả lập network
    time.sleep(1)

    print("DONE", url)

    return url


urls = [
    "url1",
    "url2",
    "url3",
    "url4",
    "url5",
]


with ThreadPoolExecutor(max_workers=5) as executor:

    results = list(
        executor.map(crawl, urls)
    )

print(results)
```

5 URL:

```text
~1 second
```

thay vì:

```text
~5 seconds
```

trong mô hình sleep này.

---

# 18. Một nuance rất quan trọng: GIL có thể được nhả

Không phải cứ ở trong thread là:

```text
GIL luôn bị giữ
```

Nhiều thao tác I/O trong Python/C extension có thể nhả GIL trong lúc chờ.

Ví dụ:

```text
socket I/O
file I/O
blocking system calls
```

Các thư viện native cũng có thể nhả GIL trong những đoạn thích hợp.

Đây là lý do:

```text
ThreadPoolExecutor
```

vẫn rất hữu ích.

---

# 19. C extension có thể thay đổi câu chuyện

Giả sử một thư viện thực hiện phần lớn computation bằng C/C++ và **nhả GIL** trong đoạn tính toán.

Khi đó:

```text
Thread A → native code
Thread B → native code
```

có thể thực sự tận dụng nhiều CPU core.

Do đó không nên áp dụng máy móc:

> "Python + thread = không chạy song song."

Phải hỏi:

> **Phần computation thực tế đang chạy ở đâu và có giữ GIL hay không?**

---

# 20. Ví dụ tư duy với NumPy

Ví dụ conceptual:

```python
import numpy as np
```

Một số operation của NumPy được thực hiện bằng native code và có thể xử lý song song/nhả GIL tùy operation và build.

Do đó:

```text
Python loop
```

và:

```text
NumPy native operation
```

không nên đánh đồng.

Đây là một trong những lý do benchmark thực tế quan trọng hơn lý thuyết đơn giản.

---

# 21. ThreadPoolExecutor vs ProcessPoolExecutor

Đây là cặp bạn phải thuộc.

|               | ThreadPoolExecutor | ProcessPoolExecutor          |
| ------------- | ------------------ | ---------------------------- |
| Đơn vị        | Thread             | Process                      |
| Shared memory | Có                 | Không trực tiếp              |
| I/O-bound     | ⭐⭐⭐⭐⭐              | ⭐⭐                           |
| CPU-bound     | ⭐                  | ⭐⭐⭐⭐⭐                        |
| GIL ảnh hưởng | Có                 | Process có interpreter riêng |
| Communication | dễ                 | serialization/pickle         |
| Memory        | thấp hơn           | cao hơn                      |
| Startup       | nhẹ hơn            | nặng hơn                     |

---

# 22. CPU-bound → ProcessPool

Ví dụ:

```python
from concurrent.futures import ProcessPoolExecutor


def cpu_task(n):
    total = 0

    for i in range(n):
        total += i

    return total


with ProcessPoolExecutor(max_workers=4) as executor:

    results = list(
        executor.map(
            cpu_task,
            [50_000_000] * 4
        )
    )
```

Mỗi process có:

```text
Process 1 → Python interpreter
Process 2 → Python interpreter
Process 3 → Python interpreter
Process 4 → Python interpreter
```

Không dùng chung một GIL theo kiểu thread trong cùng process.

---

# 23. Nhưng ProcessPool không phải "ThreadPool tốt hơn"

Nó có trade-off.

Process cần:

```text
process startup
+
IPC
+
serialization
+
pickle
+
memory
```

Ví dụ truyền object rất lớn:

```python
executor.submit(
    worker,
    huge_object
)
```

có thể rất tốn chi phí.

---

# 24. Quy tắc lựa chọn

Hãy ghi nhớ:

```text
Có network?
    ↓
ThreadPoolExecutor
```

```text
Có database I/O?
    ↓
ThreadPoolExecutor
```

```text
Đọc file?
    ↓
ThreadPoolExecutor
```

```text
API requests?
    ↓
ThreadPoolExecutor
```

Nhưng:

```text
Tính toán Python nặng?
    ↓
ProcessPoolExecutor
```

Đây là quy tắc ban đầu, sau đó mới benchmark.

---

# 25. Mixed workload

Thực tế thường không thuần:

```text
I/O
```

hoặc:

```text
CPU
```

Ví dụ crawler:

```text
HTTP request
    ↓
HTML
    ↓
BeautifulSoup
    ↓
extract
    ↓
save SQLite
```

Ta có:

```text
HTTP       → I/O-bound
BeautifulSoup → CPU + memory
SQLite     → I/O
```

Đây là:

```text
mixed workload
```

Không thể chỉ nhìn một đoạn rồi kết luận toàn hệ thống.

---

# 26. Kiến trúc pipeline

Một hệ thống crawler có thể chia:

```text
                URL Queue
                    │
                    ▼
           ThreadPoolExecutor
                    │
                    ▼
               HTTP Fetch
                    │
                    ▼
               HTML Queue
                    │
                    ▼
            Parser Workers
                    │
                    ▼
              Result Queue
                    │
                    ▼
             Database Writer
```

Đây là tư duy rất quan trọng.

Không nhất thiết:

```text
1 pool
```

cho tất cả.

Có thể:

```text
I/O pool
+
CPU pool
+
writer
```

---

# 27. Ví dụ pipeline

```text
Fetcher
   │
   │ I/O-bound
   ▼
ThreadPoolExecutor
   │
   ▼
HTML
   │
   │ CPU-bound
   ▼
ProcessPoolExecutor
   │
   ▼
Parsed data
   │
   │ I/O
   ▼
Database
```

Đây là architecture nâng cao mà sau này chúng ta có thể áp dụng cho crawler của bạn.

---

# 28. GIL không phải vấn đề của `sleep()`

Một số người làm demo:

```python
def task():
    time.sleep(1)
```

rồi kết luận:

> Thread chạy song song nên Python không có vấn đề GIL.

Không chính xác.

`time.sleep()` là **waiting**, không phải CPU-bound Python computation.

Demo này chủ yếu chứng minh:

```text
concurrency
```

không phải chứng minh:

```text
CPU parallelism
```

---

# 29. Demo đúng để phân biệt

Chúng ta có hai task.

### I/O-bound

```python
def io_task():
    time.sleep(1)
```

### CPU-bound

```python
def cpu_task():
    total = 0

    for i in range(50_000_000):
        total += i

    return total
```

Sau đó benchmark:

```text
sequential
vs
ThreadPoolExecutor
vs
ProcessPoolExecutor
```

Đây là thí nghiệm quan trọng nhất của Buổi 6.

---

# 30. Bài thực hành benchmark

Tạo:

```python
import time
from concurrent.futures import (
    ThreadPoolExecutor,
    ProcessPoolExecutor,
)
```

## Test A — sequential

```python
def cpu_task(n):
    total = 0

    for i in range(n):
        total += i

    return total
```

Chạy:

```python
start = time.perf_counter()

for _ in range(4):
    cpu_task(30_000_000)

print(time.perf_counter() - start)
```

---

# 31. Test B — ThreadPool

```python
start = time.perf_counter()

with ThreadPoolExecutor(max_workers=4) as executor:

    list(
        executor.map(
            cpu_task,
            [30_000_000] * 4
        )
    )

print(time.perf_counter() - start)
```

Ghi kết quả.

---

# 32. Test C — ProcessPool

```python
start = time.perf_counter()

with ProcessPoolExecutor(max_workers=4) as executor:

    list(
        executor.map(
            cpu_task,
            [30_000_000] * 4
        )
    )

print(time.perf_counter() - start)
```

So sánh.

Không cần kết quả giống hệt nhau trên mọi máy.

Điều quan trọng là quan sát:

```text
ThreadPool
vs
ProcessPool
```

với CPU-bound workload.

---

# 33. Bài thực hành thứ hai — I/O

```python
def io_task(_):
    time.sleep(1)
    return 1
```

So sánh:

```text
Sequential
ThreadPool(2)
ThreadPool(4)
ThreadPool(8)
```

Bạn sẽ thấy ThreadPool có lợi rõ ràng.

---

# 34. Bài tập suy luận

Cho workload:

### A

```text
Download 10.000 trang web
```

→ ?

### B

```text
Resize 10.000 ảnh bằng thư viện native
```

→ ?

### C

```text
Parse 10.000 file HTML bằng Python thuần
```

→ ?

### D

```text
Gọi REST API 1.000 lần
```

→ ?

### E

```text
Tính hash của 100.000 file
```

→ ?

Đừng chỉ trả lời bằng:

```text
Thread
```

hoặc:

```text
Process
```

Hãy suy nghĩ:

```text
I/O?
CPU?
native code?
GIL?
memory?
```

---

# 35. Một nuance rất mới: Free-threaded Python

Python hiện đại đang có hướng hỗ trợ **free-threaded CPython**, tức là có thể chạy interpreter không dựa trên GIL trong một số build/configuration.

Điều này có nghĩa kiến thức:

```text
"GIL tồn tại"
```

không nên được ghi nhớ như một chân lý vĩnh viễn của mọi CPython.

Nhưng kiến trúc ứng dụng vẫn phải dựa trên:

```text
benchmark
+
workload
+
thư viện sử dụng
+
runtime
```

thay vì giả định.

Đặc biệt, **ThreadPoolExecutor API không tự động biến CPU-bound code thành nhanh hơn** chỉ vì bạn tăng `max_workers`.

---

# 36. Mental model cuối buổi

Hãy ghi nhớ sơ đồ này:

```text
                    ThreadPoolExecutor
                           │
                           ▼
                     Worker Threads
                           │
              ┌────────────┴────────────┐
              │                         │
          I/O-bound                 CPU-bound
              │                         │
              ▼                         ▼
        ThreadPool tốt            ThreadPool thường
                                   không tối ưu
              │                         │
              ▼                         ▼
        network/file/API          ProcessPool
                                      │
                                      ▼
                               nhiều interpreter
```

Và:

```text
I/O-bound
    ↓
WAIT nhiều
    ↓
Thread rất hữu ích
```

Trong khi:

```text
CPU-bound Python
    ↓
compute nhiều
    ↓
GIL + scheduling overhead
    ↓
ThreadPool không phải lựa chọn mặc định
```

---

# 37. Checklist Buổi 6

Bạn phải giải thích được bằng lời của mình:

* [ ] Concurrency là gì?
* [ ] Parallelism là gì?
* [ ] I/O-bound là gì?
* [ ] CPU-bound là gì?
* [ ] GIL là gì?
* [ ] Vì sao ThreadPoolExecutor tốt cho HTTP?
* [ ] Vì sao ThreadPoolExecutor thường không giúp CPU-bound Python nhanh gấp N lần?
* [ ] Vì sao `ProcessPoolExecutor` phù hợp hơn cho CPU-bound?
* [ ] Tại sao C extension có thể thay đổi câu chuyện?
* [ ] Tại sao `sleep()` không phải ví dụ tốt để chứng minh CPU parallelism?
* [ ] Khi nào cần benchmark thay vì đoán?

---

## Bài tập chính Buổi 6

Tạo một file:

```text
lesson06_gil.py
```

và benchmark 3 mô hình:

```text
                 CPU-bound
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
 Sequential      ThreadPool   ProcessPool
```

và 3 mô hình:

```text
                  I/O-bound
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
 Sequential      ThreadPool(4)  ThreadPool(10)
```

Ghi lại:

```text
workload
workers
elapsed
speedup
```

Sau bài này, bạn sẽ không còn nhìn `ThreadPoolExecutor` đơn giản là **"chạy nhiều thread để nhanh hơn"**, mà bắt đầu nhìn nó theo đúng tư duy concurrent programming:

> **Tôi đang che giấu latency bằng concurrency, hay tôi thực sự cần CPU parallelism?**

**Buổi 7** chúng ta sẽ học một phần rất thực chiến: **Future lifecycle và trạng thái của Future** — `PENDING → RUNNING → FINISHED`, `cancel()`, `cancelled()`, `running()`, `done()`, `result()`, `exception()`, timeout và cách xây cơ chế **retry task** dựa trên Future.
