# 🐍 Buổi 7 — Memory Debugging

Đây là **buổi cuối của Part I — Python Runtime & Memory**.

Sau 6 buổi, chúng ta đã đi từ:

```text
Object Model
     ↓
Memory Management
     ↓
Reference Counting
     ↓
Garbage Collector
     ↓
Shallow Copy
     ↓
Deep Copy
     ↓
🔥 Memory Debugging
```

Mục tiêu hôm nay:

> Khi Python process cứ tăng RAM, làm sao biết **object nào đang chiếm memory, memory được cấp phát ở đâu, và reference nào đang giữ object sống?**

---

# 1. Memory Leak trong Python là gì?

Một hiểu lầm phổ biến:

> Python có GC nên Python không có memory leak.

Sai.

Ví dụ:

```python
cache = []

def process():
    data = "x" * 1_000_000
    cache.append(data)
```

Gọi:

```python
for _ in range(100):
    process()
```

Ta có:

```text
Global cache
     │
     ├──► data
     ├──► data
     ├──► data
     ├──► ...
     └──► data
```

Các object vẫn **reachable**.

GC nhìn thấy:

```text
Root
 ↓
cache
 ↓
data
```

nên GC không thể xóa chúng.

---

# 2. Hai loại vấn đề cần phân biệt

## Loại 1 — Unreachable cycle

```text
A ◄──► B

không còn root
```

GC có thể xử lý.

## Loại 2 — Retained objects

```text
Global
  ↓
Cache
  ↓
A
  ↓
B
  ↓
C
```

Object vẫn reachable.

GC **không phải lỗi**.

Application đang giữ reference.

Vì vậy khi debug memory, câu hỏi quan trọng là:

> **Ai đang giữ reference?**

---

# 3. Công cụ quan trọng nhất: `tracemalloc`

Python có module:

```python
import tracemalloc
```

Đây là công cụ cực kỳ hữu ích để theo dõi memory allocations của Python.

Bắt đầu:

```python
tracemalloc.start()
```

Sau đó chạy code cần kiểm tra.

---

# 4. Ví dụ đầu tiên

```python
import tracemalloc

tracemalloc.start()

data = []

for i in range(100_000):
    data.append({
        "id": i,
        "value": "x" * 100,
    })

snapshot = tracemalloc.take_snapshot()

for stat in snapshot.statistics("lineno")[:10]:
    print(stat)
```

Bạn có thể thấy output dạng:

```text
example.py:8: size=...
example.py:7: size=...
...
```

Ý nghĩa:

> Memory đang được allocate nhiều ở dòng nào?

---

# 5. `tracemalloc` không phải GC

Hai công cụ có nhiệm vụ khác nhau.

```text
gc
 ↓
Object lifecycle
 ↓
Garbage collection
```

Trong khi:

```text
tracemalloc
 ↓
Memory allocation tracing
 ↓
Allocation statistics
```

Mental model:

```text
              MEMORY DEBUGGING
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
         gc                 tracemalloc
          │                     │
          ▼                     ▼
Object graph              Allocation site
References                Memory statistics
Cycles                    Snapshots
```

---

# 6. Snapshot

Một snapshot là ảnh chụp trạng thái allocation tại một thời điểm.

```python
snapshot = tracemalloc.take_snapshot()
```

Ví dụ:

```text
T0
 │
 ▼
snapshot1
 │
 │ application chạy
 ▼
snapshot2
```

Sau đó:

```python
snapshot2.compare_to(
    snapshot1,
    "lineno",
)
```

để xem memory thay đổi thế nào.

---

# 7. Đây mới là kỹ thuật rất mạnh

Ví dụ:

```python
import tracemalloc

tracemalloc.start()

snapshot1 = tracemalloc.take_snapshot()

data = []

for i in range(100_000):
    data.append({
        "id": i,
        "value": "x" * 100,
    })

snapshot2 = tracemalloc.take_snapshot()

stats = snapshot2.compare_to(
    snapshot1,
    "lineno",
)

for stat in stats[:10]:
    print(stat)
```

Bạn đang hỏi:

> So với thời điểm ban đầu, dòng code nào làm memory tăng nhiều nhất?

---

# 8. `lineno`

Khi:

```python
snapshot.statistics("lineno")
```

hoặc:

```python
snapshot2.compare_to(snapshot1, "lineno")
```

ta đang group theo source line.

Ví dụ:

```text
crawler.py:120
crawler.py:87
parser.py:45
```

Điều này cực kỳ hữu ích.

Thay vì:

> RAM tăng 500 MB.

Ta có:

> 350 MB được allocate từ `parser.py:45`.

---

# 9. Group theo file

Có thể dùng:

```python
snapshot.statistics("filename")
```

Ví dụ:

```python
for stat in snapshot.statistics("filename")[:10]:
    print(stat)
```

Cho phép nhìn:

```text
crawler.py
parser.py
cache.py
database.py
```

thay vì từng dòng.

---

# 10. Group theo traceback

Một cách mạnh hơn:

```python
snapshot.statistics("traceback")
```

Khi allocation đến từ call chain phức tạp:

```text
main()
  ↓
crawl()
  ↓
parse()
  ↓
build_model()
  ↓
allocation
```

traceback giúp tìm được context sâu hơn.

---

# 11. `display_top()`

Có thể tạo helper:

```python
def display_top(snapshot, limit=10):
    stats = snapshot.statistics("lineno")

    print(
        f"Top {limit} memory allocations"
    )

    for stat in stats[:limit]:
        print(stat)
```

Sử dụng:

```python
tracemalloc.start()

# code

snapshot = tracemalloc.take_snapshot()

display_top(snapshot)
```

Đây là pattern rất tiện khi debugging.

---

# 12. Tìm memory leak bằng Snapshot

Một quy trình thực tế:

```text
Start
  ↓
snapshot A
  ↓
run workload
  ↓
snapshot B
  ↓
compare
  ↓
identify suspicious allocation
  ↓
inspect references
  ↓
fix
  ↓
run again
```

---

# 13. Memory Leak Simulator

Hãy xây một ví dụ crawler.

```python
import tracemalloc


CACHE = []


def crawl(url):
    response = {
        "url": url,
        "html": "x" * 100_000,
    }

    CACHE.append(response)


tracemalloc.start()

snapshot1 = tracemalloc.take_snapshot()

for i in range(1_000):
    crawl(f"https://example.com/{i}")

snapshot2 = tracemalloc.take_snapshot()

stats = snapshot2.compare_to(
    snapshot1,
    "lineno",
)

for stat in stats[:10]:
    print(stat)
```

Memory sẽ tăng.

Tại sao?

```text
CACHE
 │
 ├── response 1
 ├── response 2
 ├── response 3
 ├── ...
 └── response 1000
```

---

# 14. `gc.collect()` có giải quyết được không?

Thử:

```python
import gc

gc.collect()
```

Sau đó snapshot lại.

Bạn sẽ thấy vấn đề vẫn tồn tại.

Bởi vì:

```text
CACHE
 ↓
response
```

vẫn còn reference.

GC không được phép xóa.

---

# 15. Fix

Thay:

```python
CACHE = []
```

bằng cache có giới hạn.

Ví dụ đơn giản:

```python
from collections import deque

CACHE = deque(maxlen=100)
```

Bây giờ:

```text
CACHE
 ├── response 901
 ├── response 902
 ├── ...
 └── response 1000
```

Các response cũ bị loại khỏi container.

Reference giảm.

Object có thể được reclaim.

---

# 16. Đây là một nguyên tắc production rất quan trọng

Không nên có:

```python
cache = {}
```

rồi vô thời hạn:

```python
cache[key] = huge_object
```

trừ khi có chiến lược eviction.

Production cache thường cần:

```text
TTL
LRU
size limit
max entries
eviction
weak references
manual cleanup
```

---

# 17. `gc.get_objects()`

Nếu muốn nghiên cứu object graph:

```python
import gc

objects = gc.get_objects()

print(len(objects))
```

Có thể lọc:

```python
strings = [
    obj
    for obj in gc.get_objects()
    if isinstance(obj, str)
]
```

Nhưng có caveat:

> `gc.get_objects()` không phải danh sách "mọi object đang tồn tại trong Python".

Nó liên quan đến các object được cyclic GC track.

Đây là distinction quan trọng.

---

# 18. Tìm object cụ thể

Ví dụ:

```python
class Response:
    pass
```

Tạo nhiều:

```python
responses = [
    Response()
    for _ in range(1000)
]
```

Có thể tìm các object loại này trong GC-tracked objects:

```python
import gc

responses = [
    obj
    for obj in gc.get_objects()
    if isinstance(obj, Response)
]

print(len(responses))
```

Rất hữu ích khi debug:

> Tại sao vẫn còn 10.000 `Response` objects?

---

# 19. `gc.get_referrers()`

Sau khi tìm object đáng ngờ:

```python
obj = responses[0]
```

có thể điều tra:

```python
refs = gc.get_referrers(obj)
```

Mental model:

```text
Who references this object?

        ?
        │
        ▼
      Object
```

Ví dụ:

```text
Global CACHE
     │
     ▼
   Response
```

`get_referrers()` có thể giúp tìm `CACHE`.

---

# 20. `gc.get_referents()`

Ngược lại:

```python
gc.get_referents(obj)
```

hỏi:

> Object này đang reference tới những object nào?

Ví dụ:

```text
Response
 ├──► URL
 ├──► Headers
 ├──► HTML
 └──► Metadata
```

`get_referents()` giúp đi **xuống graph**.

`get_referrers()` giúp đi **ngược lên graph**.

---

# 21. Reference Graph Debugging

Ta có:

```text
Global Registry
       │
       ▼
    Worker
       │
       ▼
    Crawler
       │
       ▼
   Response
       │
       ▼
      HTML
```

Nếu `HTML` quá lớn:

```text
HTML
 ↑
Response
 ↑
Crawler
 ↑
Worker
 ↑
Global Registry
```

Câu hỏi cần tìm:

> Tại sao `Global Registry` vẫn giữ Worker?

Đây mới là root cause.

---

# 22. Memory Leak Debugging không phải chỉ nhìn RAM

Ví dụ process:

```text
RAM:
100 MB
110 MB
120 MB
130 MB
140 MB
...
```

Không đủ để kết luận.

Có thể là:

```text
Python allocator giữ memory để reuse
```

hoặc:

```text
tracemalloc-visible Python allocations
```

hoặc:

```text
native memory ngoài phạm vi tracemalloc
```

Do đó cần phân biệt:

```text
RSS
Heap
Python allocations
Native allocations
Object retention
```

---

# 23. `sys.getsizeof()` cũng không phải công cụ leak detection

Ví dụ:

```python
import sys

data = {
    "users": [
        {"name": "A"},
        {"name": "B"},
    ]
}

print(sys.getsizeof(data))
```

Con số này không phải tổng memory của:

```text
data
 ├── list
 ├── dict
 ├── strings
 └── nested objects
```

`sys.getsizeof()` chủ yếu cho kích thước trực tiếp của object.

Không nên dùng:

```python
sys.getsizeof(root)
```

để kết luận:

> "Object graph này chiếm X MB."

---

# 24. `tracemalloc` cũng có giới hạn

`tracemalloc` rất tốt cho Python memory allocations, nhưng không phải công cụ để quan sát mọi loại native memory.

Ví dụ:

```text
Python
 │
 ├── Python objects
 │
 └── C extension
       │
       └── native memory
```

Một số allocation bên ngoài Python allocator có thể không được phản ánh đầy đủ như bạn mong đợi.

Nếu process RSS tăng nhưng `tracemalloc` không cho thấy nguyên nhân tương ứng, cần nghĩ đến:

```text
C extensions
native buffers
OS resources
external libraries
allocator behavior
```

---

# 25. Quy trình Debug Memory Production

Một workflow tốt:

```text
1. Xác nhận memory growth
          ↓
2. Reproduce workload
          ↓
3. tracemalloc.start()
          ↓
4. snapshot baseline
          ↓
5. run workload
          ↓
6. snapshot after
          ↓
7. compare_to()
          ↓
8. tìm allocation site
          ↓
9. tìm object đang giữ memory
          ↓
10. inspect referrers
          ↓
11. fix lifecycle/cache/reference
          ↓
12. benchmark lại
```

---

# 26. Một Memory Debugger nhỏ

Ta có thể viết:

```python
import tracemalloc


class MemoryDebugger:

    def __init__(self):
        self.before = None

    def start(self):
        tracemalloc.start()

    def snapshot_before(self):
        self.before = tracemalloc.take_snapshot()

    def compare(self):
        after = tracemalloc.take_snapshot()

        stats = after.compare_to(
            self.before,
            "lineno",
        )

        for stat in stats[:10]:
            print(stat)
```

Sử dụng:

```python
debugger = MemoryDebugger()

debugger.start()
debugger.snapshot_before()

# workload
data = []

for i in range(100_000):
    data.append("x" * 100)

debugger.compare()
```

Đây là bước đầu để xây **memory profiling infrastructure**.

---

# 27. Debug Memory của crawler

Trong crawler framework tương lai của chúng ta:

```text
Crawler
   │
   ├── Scheduler
   ├── Queue
   ├── Workers
   ├── Downloader
   ├── Parser
   ├── Cache
   └── Storage
```

Ta có thể đặt snapshot:

```text
Crawler Start
     │
     ▼
Snapshot A
     │
     ▼
1000 requests
     │
     ▼
Snapshot B
     │
     ▼
1000 requests
     │
     ▼
Snapshot C
```

Nếu:

```text
A → B : +50 MB
B → C : +50 MB
```

và workload tương đương nhau, đây là tín hiệu đáng điều tra.

---

# 28. Một bug crawler rất thực tế

Ví dụ:

```python
class Crawler:
    def __init__(self):
        self.responses = []

    def handle(self, response):
        self.responses.append(response)
```

Sau 1 triệu pages:

```text
Crawler
  │
  ▼
responses
  │
  ├── Response 1
  ├── Response 2
  ├── Response 3
  ├── ...
  └── Response 1,000,000
```

GC không giúp được.

Đây không phải:

```text
GC bug
```

mà là:

```text
lifecycle design bug
```

Có thể sửa thành:

```python
def handle(self, response):
    process(response)
```

hoặc:

```python
self.responses = deque(maxlen=1000)
```

hoặc lưu vào storage thay vì giữ toàn bộ response trong RAM.

---

# 29. Memory Ownership

Đây là khái niệm architecture rất quan trọng.

Mỗi object lớn nên có câu trả lời cho:

> **Ai sở hữu object này?**

Ví dụ:

```text
Response
   │
   ▼
Parser
```

Parser xử lý xong:

```text
Response
   ↓
extract data
   ↓
release response
```

Không nên vô tình:

```text
Global Registry
 ↓
Parser
 ↓
last_response
 ↓
huge HTML
```

---

# 30. Memory Retention

Trong Python, debugging memory thường là debugging:

```text
RETENTION
```

chứ không đơn giản là:

```text
ALLOCATION
```

Có hai câu hỏi:

### Allocation

> Memory được tạo ở đâu?

`tracemalloc`

### Retention

> Ai đang giữ object?

```text
gc
reference graph
get_referrers()
```

Kết hợp:

```text
tracemalloc
     +
gc
     +
object graph
```

mới mạnh.

---

# 31. Bộ ba Debugging

Hãy ghi nhớ:

```text
             MEMORY DEBUGGING
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
tracemalloc         gc       object graph
       │            │            │
       ▼            ▼            ▼
allocation       lifecycle    references
       │            │            │
       └────────────┼────────────┘
                    ▼
                root cause
```

---

# 32. Những sai lầm phổ biến

### ❌ Sai lầm 1

```python
gc.collect()
```

mỗi khi RAM tăng.

→ Không phải cách debug memory.

---

### ❌ Sai lầm 2

```python
sys.getsizeof(obj)
```

rồi kết luận toàn bộ graph chiếm bao nhiêu RAM.

→ Không chính xác.

---

### ❌ Sai lầm 3

Thấy cycle rồi kết luận:

> Memory leak.

→ Không nhất thiết.

---

### ❌ Sai lầm 4

Thấy process RSS không giảm rồi kết luận:

> Object chưa được GC.

→ Không nhất thiết.

Allocator có thể giữ memory để tái sử dụng.

---

### ❌ Sai lầm 5

Dùng `deepcopy()` cho object graph khổng lồ.

→ Có thể tự tạo thêm memory pressure.

---

# 33. Checklist Memory Debugging

Khi application tăng RAM:

```text
□ RAM có thực sự tăng liên tục không?
□ Workload có giống nhau không?
□ Có cache không giới hạn không?
□ Có global list/dict không?
□ Có registry giữ object không?
□ Có callback/closure giữ reference không?
□ Có queue không được drain không?
□ Có task/thread giữ object không?
□ Có cycle không?
□ Object có còn reachable không?
□ tracemalloc chỉ ra allocation nào?
□ referrers là gì?
□ RSS tăng nhưng Python allocations không tăng?
```

---

# 34. Part I hoàn thành 🎉

Bạn vừa hoàn thành toàn bộ:

```text
PART I — PYTHON RUNTIME & MEMORY

01  Python Object Model
02  Memory Management
03  Reference Counting
04  Garbage Collector
05  Shallow Copy
06  Deep Copy
07  Memory Debugging
```

Và mental model hiện tại là:

```text
                   Python Object
                        │
                        ▼
                  Object Graph
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
       Reference Counting       GC
              │                   │
              └─────────┬─────────┘
                        ▼
                 Object Lifetime
                        │
                        ▼
                    Copying
                  ┌─────┴─────┐
                  ▼           ▼
              Shallow       Deep
                  │           │
                  └─────┬─────┘
                        ▼
                 Memory Debugging
                  ┌─────┴──────┐
                  ▼            ▼
             tracemalloc       gc
                  │            │
                  ▼            ▼
             allocation    references
```

---

# 🚀 Phần II — Descriptor & Attribute System

Từ đây chúng ta chuyển sang một phần **rất quan trọng của Python internals**.

```text
Buổi 8  — Attribute Lookup
Buổi 9  — __getattribute__
Buổi 10 — __getattr__
Buổi 11 — Descriptor Foundation
Buổi 12 — Data Descriptor
Buổi 13 — Non-data Descriptor
Buổi 14 — property
Buổi 15 — Descriptor Practical
Buổi 16 — Descriptor Framework
```

Đặc biệt **Buổi 8 — Attribute Lookup** sẽ giải thích chính xác Python làm gì khi bạn viết:

```python
user.name
```

Python không đơn giản là:

```text
user
 ↓
__dict__
 ↓
name
```

Mà có một **thứ tự lookup rất cụ thể** liên quan tới:

```text
object
   ↓
type
   ↓
__getattribute__
   ↓
data descriptor
   ↓
instance __dict__
   ↓
non-data descriptor
   ↓
class attribute
   ↓
__getattr__
```

Đây chính là nền tảng để hiểu sâu:

* `property`
* method
* `classmethod`
* `staticmethod`
* ORM field
* validation framework
* dependency injection
* lazy loading
* framework internals

**Buổi 8 sẽ bắt đầu bằng việc tự mô phỏng Attribute Lookup bằng Python thuần**, trước khi đi vào Descriptor.
