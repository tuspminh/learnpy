# Iterator Deep Dive — Buổi 21

# Performance: Iterator, Generator và Lazy Evaluation

Đây là buổi rất quan trọng vì từ đây chúng ta không chỉ hỏi:

> **"Code này có chạy đúng không?"**

mà bắt đầu hỏi:

> **"Code này sử dụng bao nhiêu RAM?"**
> **"Mất bao lâu?"**
> **"Chi phí tạo object là bao nhiêu?"**
> **"Iterator có thực sự nhanh hơn không?"**
> **"Khi nào nên đánh đổi CPU để lấy RAM?"**

Một hiểu lầm phổ biến là:

> **Generator luôn nhanh hơn List.**

❌ Không đúng.

Generator chủ yếu giúp **lazy evaluation và tiết kiệm memory**. Trong một số trường hợp nó còn có thể **chậm hơn List**.

---

# 1. Performance của Iterator gồm những gì?

Khi đánh giá Iterator, ta quan tâm ít nhất 5 thứ:

```text
Performance
│
├── CPU Time
├── Memory
├── Allocation
├── Throughput
└── Latency
```

---

## CPU Time

Thời gian CPU thực hiện computation.

Ví dụ:

```python
sum(x * x for x in range(1_000_000))
```

---

## Memory

Bao nhiêu RAM được sử dụng.

Đây thường là điểm mạnh nhất của Iterator.

---

## Allocation

Bao nhiêu object được tạo.

Ví dụ:

```python
[x * 2 for x in range(1_000_000)]
```

sẽ tạo một List lớn.

Generator:

```python
(x * 2 for x in range(1_000_000))
```

không tạo toàn bộ kết quả trước.

---

## Throughput

Bao nhiêu phần tử xử lý được trong một khoảng thời gian.

Ví dụ:

```text
100,000 items / second
```

---

## Latency

Thời gian để nhận **phần tử đầu tiên**.

Điểm này rất quan trọng trong streaming.

---

# 2. List vs Generator

Ví dụ:

```python
def list_version(n):

    return [
        x * x
        for x in range(n)
    ]
```

Generator:

```python
def generator_version(n):

    return (
        x * x
        for x in range(n)
    )
```

---

# 3. Đo CPU bằng `time.perf_counter()`

Python có:

```python
from time import perf_counter
```

Ví dụ:

```python
from time import perf_counter


start = perf_counter()

result = [
    x * x
    for x in range(1_000_000)
]

elapsed = perf_counter() - start

print(elapsed)
```

---

# 4. Đo Generator

```python
from time import perf_counter


start = perf_counter()

result = (
    x * x
    for x in range(1_000_000)
)

elapsed = perf_counter() - start

print(elapsed)
```

Bạn sẽ thấy một điều rất thú vị:

Generator có thể gần như tạo ra **ngay lập tức**.

Tại sao?

Vì computation chưa xảy ra.

---

# 5. Đây là một bẫy benchmark

Bạn không được so sánh:

```python
list(...)
```

với:

```python
generator expression
```

chỉ bằng thời gian tạo object.

Bởi vì:

```python
result = (
    x * x
    for x in range(1_000_000)
)
```

chưa thực sự tính `x*x`.

---

# 6. Phải consume Generator

Đúng hơn:

```python
start = perf_counter()

result = sum(
    x * x
    for x in range(1_000_000)
)

elapsed = perf_counter() - start
```

Bây giờ Generator mới thực sự thực hiện computation.

---

# 7. Benchmark List vs Generator

```python
from time import perf_counter


N = 1_000_000


start = perf_counter()

result = sum([
    x * x
    for x in range(N)
])

list_time = perf_counter() - start


start = perf_counter()

result = sum(
    x * x
    for x in range(N)
)

generator_time = perf_counter() - start


print("List:", list_time)
print("Generator:", generator_time)
```

Thông thường Generator có thể không nhanh hơn List.

Thậm chí:

```text
Generator
    ↓
yield / iterator protocol
    ↓
overhead
```

có thể khiến nó chậm hơn một chút.

---

# 8. Vậy Generator thắng ở đâu?

**Memory.**

Đây mới là lợi ích lớn.

---

# 9. Đo Memory bằng `tracemalloc`

Python có module:

```python
import tracemalloc
```

Ví dụ:

```python
import tracemalloc


tracemalloc.start()

data = [
    x * x
    for x in range(1_000_000)
]

current, peak = tracemalloc.get_traced_memory()

print("Current:", current)
print("Peak:", peak)

tracemalloc.stop()
```

---

# 10. Generator

```python
import tracemalloc


tracemalloc.start()

data = (
    x * x
    for x in range(1_000_000)
)

current, peak = tracemalloc.get_traced_memory()

print("Current:", current)
print("Peak:", peak)

tracemalloc.stop()
```

Generator không chứa toàn bộ:

```text
0
1
4
9
...
```

Nó chỉ giữ state cần thiết để tiếp tục computation.

---

# 11. Memory Model

List:

```text
List
│
├── item 1
├── item 2
├── item 3
├── ...
└── item 1,000,000
```

Generator:

```text
Generator
│
├── frame
├── local variables
└── current state
```

Đây là khác biệt cực kỳ quan trọng.

---

# 12. Generator không lưu toàn bộ kết quả

Ví dụ:

```python
def numbers():

    for i in range(1_000_000):
        yield i
```

Generator không có:

```text
[0,1,2,3,...]
```

trong RAM.

Nó chỉ biết:

> "Tôi đang ở đâu và lần tiếp theo phải làm gì?"

---

# 13. Iterator có overhead

Mỗi:

```python
next(iterator)
```

là một lần protocol call.

Ví dụ:

```python
for x in iterator:
    ...
```

có overhead so với việc thao tác trực tiếp trên một số cấu trúc dữ liệu tối ưu.

Vì vậy:

> Lazy không đồng nghĩa với zero-cost.

---

# 14. List có lợi thế CPU

List đã được materialize:

```text
Memory
│
├── item
├── item
├── item
└── ...
```

Khi lặp lại:

```python
for x in data:
    ...
```

Python chỉ đọc các phần tử đã tồn tại.

Generator phải:

```text
resume generator
      ↓
execute code
      ↓
yield
      ↓
resume
      ↓
execute
```

Do đó có thêm overhead.

---

# 15. Khi List nhanh hơn Generator

Ví dụ:

```python
data = [x * 2 for x in range(1_000_000)]
```

Sau đó dùng nhiều lần:

```python
sum(data)

max(data)

min(data)
```

Nếu dùng Generator:

```python
gen = (x * 2 for x in range(1_000_000))
```

Sau:

```python
sum(gen)
```

Generator đã hết.

Muốn:

```python
max(...)
```

phải tính lại.

---

# 16. Iterator là Single Pass

Đây là vấn đề performance rất quan trọng.

```python
gen = (x * 2 for x in range(10))
```

Sau:

```python
list(gen)
```

↓

Generator exhausted.

Không thể:

```python
list(gen)
```

lần nữa để lấy lại dữ liệu.

Nếu cần nhiều lần, List có thể tốt hơn.

---

# 17. Lazy giúp giảm Peak Memory

Đây là trường hợp Iterator cực kỳ mạnh.

Giả sử:

```text
10 triệu records
```

Nếu List:

```text
Database
    ↓
List 10 triệu records
    ↓
Processing
```

RAM có thể tăng rất lớn.

Lazy:

```text
Database
    ↓
Record 1
    ↓
Process
    ↓
Record 2
    ↓
Process
```

Peak memory thấp hơn rất nhiều.

---

# 18. Database Cursor

Ví dụ:

```python
cursor.execute(
    "SELECT * FROM chapters"
)

for row in cursor:
    process(row)
```

Không cần:

```python
rows = cursor.fetchall()
```

rồi mới xử lý.

---

## Cách 1

```python
rows = cursor.fetchall()

for row in rows:
    process(row)
```

```text
Database
    ↓
RAM
    ↓
Process
```

---

## Cách 2

```python
for row in cursor:
    process(row)
```

```text
Database
    ↓
row
    ↓
process
```

Cách thứ hai thường phù hợp hơn khi dữ liệu lớn.

---

# 19. File Processing

Không nên:

```python
with open("huge.log") as f:

    data = f.readlines()

for line in data:
    process(line)
```

Nếu file cực lớn.

Tốt hơn:

```python
with open("huge.log") as f:

    for line in f:
        process(line)
```

File object là Iterator.

---

# 20. Iterator Pipeline

Giả sử:

```python
data = range(10_000_000)
```

Pipeline:

```python
result = (
    x * 2
    for x in data
    if x % 2 == 0
)
```

Không tạo:

```text
10 triệu
↓
List
↓
List
↓
List
```

Mà:

```text
source
  ↓
filter
  ↓
transform
  ↓
consumer
```

---

# 21. Intermediate List là kẻ giết Memory

Ví dụ:

```python
result = [
    x * 2
    for x in data
    if x % 2 == 0
]
```

Nếu sau đó:

```python
result2 = [
    x + 1
    for x in result
]
```

Ta có:

```text
data
 ↓
result
 ↓
result2
```

Có thể đồng thời tồn tại nhiều cấu trúc lớn.

---

# 22. Lazy Pipeline

Thay bằng:

```python
result = (
    x * 2
    for x in data
    if x % 2 == 0
)

result2 = (
    x + 1
    for x in result
)
```

Pipeline:

```text
data
 ↓
filter
 ↓
map
 ↓
consumer
```

Chỉ một phần tử đi qua tại một thời điểm.

---

# 23. Latency: Iterator có lợi thế

Giả sử có:

```text
1,000,000 records
```

Eager:

```python
data = load_all()
```

Có thể phải đợi toàn bộ 1 triệu record.

Lazy:

```python
for item in stream():
    process(item)
```

Có thể bắt đầu xử lý ngay record đầu tiên.

---

# 24. Eager vs Lazy

### Eager

```text
Input
 ↓
Process ALL
 ↓
Output
```

Latency:

```text
cao
```

Memory:

```text
cao
```

---

### Lazy

```text
Input
 ↓
Process 1
 ↓
Output 1
 ↓
Process 2
 ↓
Output 2
```

Latency:

```text
thấp
```

Memory:

```text
thấp
```

Nhưng CPU overhead có thể cao hơn.

---

# 25. Throughput

Nếu mục tiêu là:

> xử lý tối đa số lượng record/giây

thì List/materialized data đôi khi có lợi.

Ví dụ:

```python
data = list(range(10_000_000))
```

Sau đó xử lý nhiều lần.

Trong trường hợp này, việc giữ dữ liệu trong RAM có thể đổi lấy throughput tốt hơn.

---

# 26. Một quy tắc thực tế

Không hỏi:

> Iterator hay List tốt hơn?

Mà hỏi:

> **Workload của tôi là gì?**

---

Nếu:

```text
Dữ liệu nhỏ
+
Truy cập nhiều lần
+
Random access
```

→ List.

Nếu:

```text
Dữ liệu lớn
+
One-pass
+
Streaming
```

→ Iterator.

---

# 27. Random Access

List:

```python
data[500000]
```

rất thuận tiện.

Iterator:

```python
iterator[500000]
```

❌ Không tồn tại.

Muốn tới phần tử 500,000:

```python
for _ in range(500000):
    next(iterator)
```

Chi phí O(n).

---

# 28. Complexity

Ví dụ:

```python
list_data[500_000]
```

thường:

```text
O(1)
```

Iterator:

```text
next() × 500,000
```

→ khoảng:

```text
O(n)
```

Đây là một trade-off lớn.

---

# 29. `itertools.islice()`

Nếu cần lấy phần tử thứ 500,000:

```python
from itertools import islice

value = next(
    islice(iterator, 500_000, None)
)
```

Nhưng bản chất vẫn phải đi qua các phần tử trước đó.

`islice()` không biến Iterator thành random-access structure.

---

# 30. Benchmark đúng cách với `timeit`

Thay vì:

```python
perf_counter()
```

cho những benchmark nhỏ, Python cung cấp:

```python
import timeit
```

Ví dụ:

```python
import timeit


code = """
sum(x * x for x in range(1000))
"""

print(
    timeit.timeit(
        code,
        number=10000
    )
)
```

---

# 31. `timeit` quan trọng vì sao?

Một lần chạy có thể bị ảnh hưởng bởi:

* OS scheduling
* CPU frequency
* Garbage Collector
* background process
* cache
* startup cost

`timeit` chạy nhiều lần để kết quả ổn định hơn.

---

# 32. Benchmark function

```python
import timeit


def list_version():

    return sum(
        [x * x for x in range(1000)]
    )


def generator_version():

    return sum(
        x * x
        for x in range(1000)
    )


print(
    timeit.timeit(
        list_version,
        number=10000
    )
)

print(
    timeit.timeit(
        generator_version,
        number=10000
    )
)
```

---

# 33. Không benchmark bằng cảm giác

Sai:

> "Generator chắc chắn nhanh hơn vì lazy."

Sai:

> "List chắc chắn nhanh hơn vì Python tối ưu List."

Đúng:

```text
Hypothesis
    ↓
Benchmark
    ↓
Measure
    ↓
Analyze
```

---

# 34. `sys.getsizeof()`

Có thể kiểm tra kích thước object:

```python
import sys

data = [1, 2, 3]

print(sys.getsizeof(data))
```

Generator:

```python
gen = (x for x in range(3))

print(sys.getsizeof(gen))
```

Nhưng cần cực kỳ cẩn thận:

> `sys.getsizeof()` không phản ánh toàn bộ memory mà một cấu trúc dữ liệu gián tiếp giữ.

Ví dụ List chứa references tới các object khác.

---

# 35. `tracemalloc`

Để phân tích allocation tốt hơn:

```python
import tracemalloc
```

Ví dụ:

```python
tracemalloc.start()

data = [
    x * x
    for x in range(100_000)
]

snapshot = tracemalloc.take_snapshot()

for stat in snapshot.statistics("lineno")[:5]:
    print(stat)
```

Đây là công cụ rất hữu ích khi debug memory.

---

# 36. Một benchmark thực tế

Hãy thử chương trình:

```python
import tracemalloc
import time


N = 1_000_000


def list_version():

    return sum(
        [x * x for x in range(N)]
    )


def generator_version():

    return sum(
        x * x
        for x in range(N)
    )
```

Ta có thể benchmark:

```text
             CPU        Memory
List         ?          cao
Generator    ?          thấp
```

**Không nên đoán số cụ thể.**

Hãy chạy trên chính máy của bạn vì kết quả phụ thuộc:

* CPU
* Python version
* OS
* workload
* memory
* garbage collector

---

# 37. Performance trong Crawler

Đây mới là phần quan trọng đối với dự án của bạn.

Giả sử crawler:

```text
10,000,000 chapters
```

Thiết kế:

```python
chapters = crawl_all()
```

Nếu:

```python
crawl_all()
```

trả:

```python
list[Chapter]
```

thì:

```text
10 triệu Chapter
        ↓
RAM
```

rất nguy hiểm.

---

Thiết kế:

```python
async def crawl_all():
    ...
    yield chapter
```

Consumer:

```python
async for chapter in crawl_all():

    await repository.save(chapter)
```

Memory:

```text
Chapter 1
   ↓
save
   ↓
release

Chapter 2
   ↓
save
   ↓
release
```

Đây là architecture phù hợp với streaming.

---

# 38. Nhưng có một vấn đề

Nếu:

```python
await repository.save(chapter)
```

chậm hơn crawler tạo chapter:

```text
Producer
   ↓
████████████
   
Consumer
   ↓
██
```

Producer có thể tạo dữ liệu nhanh hơn Consumer.

Đây gọi là:

> **Backpressure**

---

# 39. Backpressure

Ví dụ:

```text
Downloader
1000 item/s

Parser
800 item/s

Database
100 item/s
```

Nếu không kiểm soát:

```text
Queue
100
1000
10000
100000
...
```

RAM tăng.

---

# 40. Iterator + Queue

Một kiến trúc tốt:

```text
Producer
    ↓
Bounded Queue
    ↓
Consumers
```

Queue giới hạn:

```python
asyncio.Queue(maxsize=1000)
```

Khi queue đầy:

```python
await queue.put(item)
```

sẽ chờ.

Đây chính là một cơ chế backpressure.

---

# 41. Performance không chỉ là CPU

Một hệ thống tốt cần cân bằng:

```text
CPU
RAM
I/O
Latency
Throughput
Concurrency
Backpressure
```

Iterator chỉ giải quyết một phần bài toán.

---

# 42. Iterator Performance Model

Bạn có thể ghi nhớ:

```text
Iterator
   │
   ├── + Low memory
   ├── + Low latency
   ├── + Streaming
   ├── + Composable
   │
   ├── - Single pass
   ├── - No random access
   ├── - Possible protocol overhead
   └── - May recompute
```

---

# 43. Một ví dụ cực kỳ quan trọng

Giả sử:

```python
data = range(10_000_000)
```

Bạn chỉ cần:

```python
first = next(
    x for x in data
    if x > 1_000_000
)
```

Generator thắng rất rõ.

Vì nó dừng ngay khi tìm được:

```text
1,000,001
```

Không cần xử lý 10 triệu phần tử.

---

# 44. Lazy có thể giảm computation

Ví dụ:

```python
result = next(
    x * 2
    for x in range(10_000_000)
    if x > 1_000_000
)
```

Python chỉ tính tới khi tìm thấy phần tử phù hợp.

Đây không chỉ là memory optimization.

Đây còn là:

> **Computation avoidance**

---

# 45. `any()` và `all()`

Đây cũng là một ví dụ tuyệt vời.

```python
any(
    x > 100
    for x in data
)
```

Khi tìm được:

```text
x > 100
```

`any()` dừng ngay.

---

`all()` cũng tương tự.

```python
all(
    x > 0
    for x in data
)
```

Chỉ cần gặp:

```text
False
```

là dừng.

---

# 46. Short-circuit + Lazy

Đây là một pattern cực mạnh:

```text
Lazy Iterator
      +
Short Circuit
      ↓
Không xử lý dữ liệu không cần thiết
```

Ví dụ:

```python
next(
    x for x in data
    if condition(x)
)
```

---

# 47. Khi nào Iterator làm chương trình nhanh hơn?

Không phải vì:

> `next()` nhanh hơn List.

Mà vì Iterator có thể:

### 1. Không tính dữ liệu không cần thiết

```python
next(...)
```

### 2. Không tạo intermediate collections

```python
map → filter → generator
```

### 3. Streaming

Không cần đợi toàn bộ dữ liệu.

### 4. Giảm memory pressure

Ít memory có thể giúp tránh:

* swap
* allocation lớn
* GC pressure
* memory exhaustion

---

# 48. Khi nào Iterator làm chương trình chậm hơn?

Khi:

* Cần truy cập nhiều lần.
* Cần random access.
* Cần dữ liệu đã materialize.
* Pipeline quá nhiều tầng.
* Generator logic phức tạp.
* Computation phải thực hiện lại.
* Dataset nhỏ đến mức memory không phải vấn đề.

---

# 49. Quy tắc thực chiến

### Dùng List khi:

```text
Dataset nhỏ
+
Need reuse
+
Need indexing
+
Need len
+
Need sort
```

### Dùng Iterator khi:

```text
Dataset lớn
+
One pass
+
Streaming
+
Lazy
+
Potentially infinite
```

### Dùng Async Iterator khi:

```text
I/O bound
+
Streaming
+
Async API
+
Network
+
WebSocket
+
Crawler
```

---

# 50. Kiến trúc Performance cho Crawler

Một crawler production có thể:

```text
             URL Iterator
                  │
                  ▼
          Async Downloader
                  │
                  ▼
           Async Parser
                  │
                  ▼
          Bounded Queue
                  │
          ┌───────┴───────┐
          ▼       ▼       ▼
       Worker  Worker  Worker
          │       │       │
          └───────┬───────┘
                  ▼
              Database
```

Ở đây:

* Iterator → memory efficient
* Async → I/O concurrency
* Queue → backpressure
* Multiple workers → throughput
* Database batching → giảm I/O overhead

Đây là tư duy performance thực tế.

---

# 51. Bài tập thực hành

## Bài 1 — Benchmark

Viết benchmark so sánh:

```python
[x * 2 for x in range(N)]
```

với:

```python
(x * 2 for x in range(N))
```

Đo:

* thời gian tạo
* thời gian consume
* peak memory

Sử dụng:

```python
timeit
tracemalloc
```

---

# Bài 2 — Short Circuit

Tạo:

```python
numbers = range(10_000_000)
```

Tìm số đầu tiên chia hết cho:

```text
999983
```

So sánh:

```python
list(...)
```

với:

```python
next(...)
```

Xem lượng computation khác nhau thế nào.

---

# Bài 3 — File lớn

Tạo file có:

```text
1,000,000 dòng
```

So sánh:

```python
readlines()
```

với:

```python
for line in file:
```

Đo peak memory bằng `tracemalloc`.

---

# Bài 4 — Crawler Pipeline

Thiết kế:

```text
generate_urls()
        ↓
download()
        ↓
parse()
        ↓
save()
```

Yêu cầu:

* Không tạo List trung gian.
* Dùng Generator.
* Đo peak memory.
* Sau đó chuyển toàn bộ pipeline sang Async Generator.
* So sánh memory và throughput.

---

# Bài 5 — Backpressure

Mô phỏng:

```text
Producer = 1000 item/s
Consumer = 100 item/s
```

Dùng:

```python
asyncio.Queue(maxsize=100)
```

Quan sát:

* Queue tăng như thế nào.
* Producer bị block lúc nào.
* Memory thay đổi ra sao.

---

# Tổng kết Buổi 21

Sau buổi này, bạn nên bỏ suy nghĩ:

> **"Generator = nhanh hơn List."**

Thay bằng:

> **"Iterator là một trade-off giữa memory, CPU, latency và cách truy cập dữ liệu."**

Bảng tư duy quan trọng nhất:

| Tiêu chí            | List                      | Iterator/Generator |
| ------------------- | ------------------------- | ------------------ |
| Memory              | ❌ Cao                     | ✅ Thấp             |
| Lazy                | ❌                         | ✅                  |
| Streaming           | ❌                         | ✅                  |
| One-pass            | ❌                         | ✅                  |
| Random access       | ✅                         | ❌                  |
| Reuse               | ✅                         | ❌/cần tạo lại      |
| `len()`             | ✅                         | ❌                  |
| Latency phần tử đầu | Có thể cao                | ✅ Thấp             |
| CPU overhead        | Thường thấp hơn khi reuse | Có thể cao hơn     |
| Infinite data       | ❌                         | ✅                  |
| Pipeline            | Có intermediate data      | ✅ Rất tốt          |

**Tư duy cốt lõi:**

```text
Performance
    ↓
Không phải chỉ "nhanh hay chậm"
    ↓
CPU
RAM
Latency
Throughput
I/O
Concurrency
Backpressure
    ↓
Chọn đúng mô hình dữ liệu
```

Ở **Buổi 22 — Thiết kế thư viện sử dụng Iterator**, chúng ta sẽ chuyển từ việc *sử dụng Iterator* sang **thiết kế API/library chuyên nghiệp với Iterator**: `Iterable` vs `Iterator`, `Iterator[T]`, `Generator[T, SendT, ReturnT]`, API trả về iterator, custom collection, composable pipeline, typing và cách thiết kế một thư viện không phụ thuộc vào việc dữ liệu được materialize hay streaming.
