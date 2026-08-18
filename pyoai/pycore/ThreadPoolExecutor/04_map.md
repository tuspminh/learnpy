# ThreadPoolExecutor Deep Dive — Buổi 4

## `executor.map()` — khi nào dùng `map()`, khi nào dùng `submit()`

Buổi 3 chúng ta đã học:

```python
submit()
as_completed()
wait()
```

Hôm nay tập trung vào:

```python
executor.map()
```

Đây là API đơn giản hơn `submit()`, nhưng **rất dễ hiểu sai** về thứ tự kết quả và cách xử lý exception.

---

# 1. `map()` là gì?

Nếu Python thông thường:

```python
def square(x):
    return x * x


numbers = [1, 2, 3, 4, 5]

results = map(square, numbers)
```

thì:

```python
list(results)
```

cho:

```text
[1, 4, 9, 16, 25]
```

`ThreadPoolExecutor` cũng có:

```python
executor.map()
```

Ví dụ:

```python
from concurrent.futures import ThreadPoolExecutor


def square(x):
    return x * x


with ThreadPoolExecutor(max_workers=3) as executor:

    results = executor.map(square, [1, 2, 3, 4, 5])

    for result in results:
        print(result)
```

Kết quả:

```text
1
4
9
16
25
```

---

# 2. Mental model

Với:

```python
executor.map(square, numbers)
```

có thể hình dung:

```text
numbers
   │
   ├── 1 ──► Worker
   ├── 2 ──► Worker
   ├── 3 ──► Worker
   ├── 4 ──► Worker
   └── 5 ──► Worker
               │
               ▼
           results
```

Khác với `submit()`:

```python
future = executor.submit(...)
```

`map()` trực tiếp cung cấp cho bạn một iterator kết quả.

---

# 3. Điểm quan trọng nhất: `map()` giữ nguyên thứ tự input

Đây là khác biệt cực kỳ quan trọng.

Giả sử:

```text
Task 1 → 5 giây
Task 2 → 1 giây
Task 3 → 3 giây
```

Completion order:

```text
2
3
1
```

Nhưng:

```python
results = executor.map(task, [1, 2, 3])
```

vẫn cho:

```text
1
2
3
```

**theo thứ tự input.**

---

# 4. Demo

```python
from concurrent.futures import ThreadPoolExecutor
import time


def task(n):

    delays = {
        1: 5,
        2: 1,
        3: 3,
    }

    time.sleep(delays[n])

    print(f"finished {n}")

    return n * 10


with ThreadPoolExecutor(max_workers=3) as executor:

    results = executor.map(
        task,
        [1, 2, 3],
    )

    for result in results:
        print("RESULT:", result)
```

Có thể xảy ra:

```text
finished 2
finished 3
finished 1

RESULT: 10
RESULT: 20
RESULT: 30
```

Tức là:

```text
Completion order:
2 → 3 → 1

Result order:
1 → 2 → 3
```

---

# 5. Đây chính là điểm khác biệt với `as_completed()`

### `map()`

```python
for result in executor.map(task, items):
    ...
```

→ **input order**

### `as_completed()`

```python
for future in as_completed(futures):
    ...
```

→ **completion order**

Ví dụ:

```text
Input:
A B C

Thời gian:
A = 5s
B = 1s
C = 3s
```

### `map()`

```text
A
B
C
```

### `as_completed()`

```text
B
C
A
```

---

# 6. Vấn đề head-of-line blocking vẫn tồn tại

Đây là điều rất quan trọng.

Với:

```python
executor.map(...)
```

nếu task đầu tiên rất chậm:

```text
Task A → 10s
Task B → 1s
Task C → 1s
```

thì:

```python
for result in executor.map(...):
```

có thể phải chờ A.

Trong khi B và C đã hoàn thành.

```text
B ── 1s ──► DONE
C ── 1s ──► DONE
A ─────────────── 10s ──► DONE
                    │
                    ▼
                 result A
                    │
                    ▼
                 result B
                    │
                    ▼
                 result C
```

Do đó `map()` không phù hợp nếu bạn cần:

> "Task nào xong trước thì xử lý ngay."

Trong trường hợp đó:

```python
as_completed()
```

thường phù hợp hơn.

---

# 7. `submit()` cho bạn Future

Với:

```python
future = executor.submit(task, item)
```

bạn có:

```text
Future
├── done()
├── running()
├── cancelled()
├── exception()
├── result()
└── add_done_callback()
```

Còn:

```python
executor.map(...)
```

cho bạn:

```text
Iterator[Result]
```

Đây là khác biệt về abstraction.

---

# 8. So sánh API

|                         | `map()`             | `submit()`                  |
| ----------------------- | ------------------- | --------------------------- |
| Code                    | đơn giản            | nhiều code hơn              |
| Trả về                  | iterator kết quả    | Future                      |
| Thứ tự                  | input order         | tùy cách xử lý              |
| Completion order        | không               | có thể với `as_completed()` |
| Cancel từng task        | khó/không trực tiếp | có                          |
| Callback                | không trực tiếp     | có                          |
| Theo dõi trạng thái     | hạn chế             | đầy đủ                      |
| Xử lý từng task độc lập | hạn chế             | rất tốt                     |

---

# 9. `map()` phù hợp khi nào?

Rất phù hợp với bài toán:

```text
input → function → output
```

Ví dụ:

```python
urls = [...]
```

và:

```python
download(url)
```

hoặc:

```python
files = [...]
```

và:

```python
process_file(file)
```

hoặc:

```python
images = [...]
```

và:

```python
resize(image)
```

Bạn chỉ quan tâm:

```text
input
 ↓
worker
 ↓
output
```

và không cần quản lý từng Future.

---

# 10. Ví dụ xử lý file

```python
from concurrent.futures import ThreadPoolExecutor


def process_file(path):
    with open(path, "rb") as f:
        data = f.read()

    return path, len(data)


files = [
    "a.txt",
    "b.txt",
    "c.txt",
]


with ThreadPoolExecutor(max_workers=3) as executor:

    for path, size in executor.map(process_file, files):
        print(path, size)
```

Code rất gọn.

---

# 11. `map()` với nhiều argument

Giả sử:

```python
def add(a, b):
    return a + b
```

Ta có:

```python
a = [1, 2, 3]
b = [10, 20, 30]
```

Có thể:

```python
with ThreadPoolExecutor(max_workers=3) as executor:

    results = executor.map(add, a, b)

    print(list(results))
```

Kết quả:

```text
[11, 22, 33]
```

Mental model:

```text
add(1, 10)
add(2, 20)
add(3, 30)
```

---

# 12. `map()` giống `zip()`

Về ý tưởng:

```python
executor.map(add, a, b)
```

giống:

```python
for x, y in zip(a, b):
    add(x, y)
```

Nhưng phần thực thi được đưa vào thread pool.

---

# 13. Ví dụ thực tế với HTTP

```python
import requests
from concurrent.futures import ThreadPoolExecutor


def download(url):
    response = requests.get(url, timeout=10)

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

    for result in executor.map(download, urls):
        print(result)
```

Đây là code rất đẹp nếu:

* muốn xử lý toàn bộ URL;
* giữ kết quả theo thứ tự URL;
* không cần biết Future nào;
* không cần callback;
* không cần cancel từng URL.

---

# 14. Nhưng exception với `map()` có điểm cần chú ý

Ví dụ:

```python
def task(n):

    if n == 3:
        raise ValueError("Boom")

    return n * 10
```

Sau đó:

```python
with ThreadPoolExecutor(max_workers=3) as executor:

    results = executor.map(task, [1, 2, 3, 4, 5])

    for result in results:
        print(result)
```

Có thể:

```text
10
20
ValueError
```

Exception xuất hiện khi iterator `results` được tiêu thụ tới vị trí tương ứng.

---

# 15. Exception không có nghĩa tất cả task tự động dừng

Ví dụ:

```text
Task 1 → success
Task 2 → success
Task 3 → exception
Task 4 → running
Task 5 → running
```

Task 3 lỗi không có nghĩa:

```text
Task 4 → automatically cancelled
Task 5 → automatically cancelled
```

Vẫn cần hiểu lifecycle của executor và các task còn lại.

Nếu bạn cần kiểm soát chi tiết:

```python
submit()
```

thường tốt hơn.

---

# 16. `map()` vs `submit()` — tư duy thiết kế

Hãy tự hỏi:

### Câu hỏi 1

Tôi chỉ cần:

```text
input → output
```

thì:

```python
map()
```

thường rất đẹp.

---

### Câu hỏi 2

Tôi cần:

```text
task nào thành công?
task nào lỗi?
task nào đang chạy?
task nào cancel?
task nào hoàn thành trước?
```

thì:

```python
submit()
```

*

```python
Future
```

phù hợp hơn.

---

# 17. Một ví dụ rất rõ

## Cách 1 — `map()`

```python
with ThreadPoolExecutor(max_workers=5) as executor:

    for result in executor.map(download, urls):
        save(result)
```

Mental model:

```text
URLs
 ↓
map()
 ↓
results
 ↓
save
```

---

## Cách 2 — `submit()`

```python
with ThreadPoolExecutor(max_workers=5) as executor:

    future_to_url = {
        executor.submit(download, url): url
        for url in urls
    }

    for future in as_completed(future_to_url):

        url = future_to_url[future]

        try:
            result = future.result()

        except Exception as e:
            log_error(url, e)

        else:
            save(result)
```

Mental model:

```text
URL
 ↓
Future
 ↓
completion
 ↓
success / error
 ↓
save / retry / log
```

Cách thứ hai mạnh hơn rất nhiều.

---

# 18. Một insight quan trọng: `map()` là abstraction cao hơn

Có thể hình dung:

```text
             ThreadPoolExecutor
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
       submit()             map()
          │                   │
          ▼                   ▼
       Future              Iterator
          │
          ▼
   as_completed()
```

`submit()` cho bạn primitive cấp thấp hơn.

`map()` cung cấp abstraction đơn giản hơn cho bài toán:

```text
parallel map
```

---

# 19. `map()` không phải `multiprocessing.Pool.map`

Nếu bạn đã từng thấy:

```python
pool.map(...)
```

thì ý tưởng tương tự:

```text
map(function, iterable)
```

nhưng executor của `concurrent.futures` có thiết kế Future-based.

Điều này trở nên rất quan trọng khi chúng ta chuyển sang:

```text
ProcessPoolExecutor
```

---

# 20. `buffersize` — một điểm nâng cao cần biết

Ở Python hiện đại, `Executor.map()` có tham số:

```python
buffersize
```

Ví dụ:

```python
executor.map(
    worker,
    items,
    buffersize=10,
)
```

Ý tưởng của `buffersize` là kiểm soát lượng kết quả/task chưa được tiêu thụ trong quá trình map.

Điều này đặc biệt đáng quan tâm khi:

```text
items = hàng triệu phần tử
```

vì bạn không muốn toàn bộ pipeline tạo ra quá nhiều công việc chờ xử lý.

Ví dụ conceptual:

```text
1,000,000 items
       │
       ▼
   buffersize=10
       │
       ▼
   controlled flow
```

Đây sẽ liên quan trực tiếp đến **backpressure** mà chúng ta học ở phần nâng cao.

---

# 21. Một vấn đề quan trọng: `map()` không phải lúc nào cũng "lazy"

Đừng mặc định nghĩ:

```python
executor.map(...)
```

sẽ giống hoàn toàn:

```python
map(...)
```

của Python built-in về lazy evaluation.

Với `Executor.map()`, việc lấy input và submit task có các đặc điểm riêng của executor; ở Python hiện đại, `buffersize` cho phép kiểm soát việc này.

Do đó khi xử lý:

```text
10 items
```

và:

```text
10,000,000 items
```

cách dùng `map()` cần được thiết kế khác nhau.

---

# 22. `map()` và crawler

Giả sử:

```text
100 URLs
```

Nếu crawler đơn giản:

```python
with ThreadPoolExecutor(max_workers=10) as executor:

    for result in executor.map(crawl, urls):
        save(result)
```

rất ổn.

Nhưng crawler thực tế thường cần:

```text
retry
timeout
error classification
logging
progress
dynamic URLs
database
rate limiting
cancel
priority
```

Khi đó:

```python
submit()
```

sẽ phù hợp hơn.

---

# 23. `map()` và pipeline xử lý file

Ví dụ:

```text
1000 file
   │
   ▼
ThreadPool
   │
   ▼
parse
   │
   ▼
result
```

Nếu chỉ cần:

```python
for result in executor.map(parse, files):
    save(result)
```

thì rất gọn.

Không cần:

```python
Future
future_to_file
as_completed
try/except
```

nếu bài toán không cần chúng.

---

# 24. Quy tắc lựa chọn

Hãy ghi nhớ quy tắc này:

```text
Cần đơn giản?
    ↓
map()
```

```text
Cần kiểm soát từng task?
    ↓
submit()
```

```text
Cần xử lý theo completion order?
    ↓
submit() + as_completed()
```

```text
Cần chờ theo điều kiện?
    ↓
wait()
```

---

# 25. Bài tập 1 — `map()`

Tạo:

```python
def square(n):
    ...
```

Cho:

```python
numbers = range(1, 11)
```

Dùng:

```python
ThreadPoolExecutor(max_workers=3)
```

và:

```python
executor.map()
```

để tính bình phương.

Kết quả phải:

```text
1
4
9
16
...
100
```

---

# 26. Bài tập 2 — chứng minh thứ tự

Tạo:

```python
def task(n):
    ...
```

với:

```text
1 → 5s
2 → 1s
3 → 3s
```

Dùng:

```python
executor.map()
```

In:

```text
START
FINISH
RESULT
```

Quan sát:

```text
FINISH 2
FINISH 3
FINISH 1
```

nhưng:

```text
RESULT 1
RESULT 2
RESULT 3
```

Đây là bài tập quan trọng.

---

# 27. Bài tập 3 — so sánh `map()` và `as_completed()`

Dùng cùng một tập task:

```text
A → 5s
B → 1s
C → 3s
D → 2s
```

Chạy hai phiên bản.

### Version A

```python
executor.map()
```

### Version B

```python
submit()
+
as_completed()
```

So sánh:

```text
result order
completion order
```

---

# 28. Bài tập 4 — downloader

Tạo:

```python
urls = [
    ...
]
```

Viết:

```python
download(url)
```

giả lập request bằng:

```python
time.sleep(...)
```

Dùng:

```python
executor.map(download, urls)
```

Yêu cầu:

```text
URL → status → size
```

---

# 29. Bài tập 5 — quyết định kiến trúc

Cho từng bài toán, chọn:

```text
map()
submit()
submit() + as_completed()
wait()
```

### A

```text
Tính square cho 1 triệu số.
```

### B

```text
Download 100 URL và xử lý ngay URL nào hoàn thành.
```

### C

```text
Chờ tất cả 50 task hoàn thành rồi mới chuyển sang bước 2.
```

### D

```text
Download URL, nếu lỗi thì retry URL đó.
```

### E

```text
Chạy 20 task và cần phát hiện task đầu tiên bị lỗi.
```

Đáp án nên là:

```text
A → map()
B → submit() + as_completed()
C → wait(ALL_COMPLETED)
D → submit()
E → wait(FIRST_EXCEPTION)
```

---

# 30. Tổng kết Buổi 4

Ba API bây giờ cần được đặt cạnh nhau:

```text
                    Executor
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       submit()       map()       ...
          │
          ▼
       Future
          │
     ┌────┴─────┐
     ▼          ▼
as_completed   wait
```

### `map()`

```python
for result in executor.map(worker, items):
    ...
```

* đơn giản;
* giữ **input order**;
* phù hợp `input → output`;
* không thuận tiện khi cần quản lý từng task.

### `submit()`

```python
future = executor.submit(worker, item)
```

* có `Future`;
* kiểm soát từng task;
* cancel;
* callback;
* exception;
* timeout;
* kết hợp `as_completed()` / `wait()`.

### `as_completed()`

```python
for future in as_completed(futures):
    ...
```

→ **completion order**.

### `wait()`

```python
done, not_done = wait(...)
```

→ chờ theo điều kiện.

---

## Bài tập chính của Buổi 4

Hãy xây **mini downloader v2** với 20 URL giả lập.

Yêu cầu có **2 implementation**:

```text
Version 1
    executor.map()

Version 2
    executor.submit()
    +
    as_completed()
```

Sau đó trả lời 3 câu:

1. Tại sao `map()` trả kết quả theo input order dù task hoàn thành không theo thứ tự?
2. Tại sao crawler thực tế thường cần `submit() + as_completed()` hơn `map()`?
3. Nếu cần giới hạn số task đang chạy và liên tục bổ sung task mới khi task cũ hoàn thành, nên dùng pattern nào?

**Buổi 5** chúng ta sẽ đi sâu vào **`max_workers` và worker thread**: ThreadPool thực sự tạo thread như thế nào, thread được tái sử dụng ra sao, `max_workers` ảnh hưởng throughput thế nào, và đặc biệt là **cách chọn số worker cho HTTP/API/crawler/file I/O**.
