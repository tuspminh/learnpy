# ThreadPoolExecutor Deep Dive — Buổi 3

## `wait()` và `as_completed()` — xử lý Future theo trạng thái hoàn thành

Ở Buổi 2, chúng ta đã hiểu:

```text
submit()
   ↓
Future
   ↓
PENDING
   ↓
RUNNING
   ↓
FINISHED
```

Hôm nay chúng ta giải quyết một vấn đề rất thực tế:

> **Có 100 task chạy đồng thời. Làm sao xử lý kết quả ngay khi từng task hoàn thành, thay vì phải chờ theo thứ tự submit?**

Hai công cụ quan trọng:

```python
wait()
as_completed()
```

---

# 1. Vấn đề của cách `future.result()` theo thứ tự

Ví dụ:

```python
from concurrent.futures import ThreadPoolExecutor
import time


def task(n):
    delay = {
        1: 5,
        2: 1,
        3: 3,
    }[n]

    time.sleep(delay)

    return n


with ThreadPoolExecutor(max_workers=3) as executor:

    futures = [
        executor.submit(task, 1),
        executor.submit(task, 2),
        executor.submit(task, 3),
    ]

    for future in futures:
        print(future.result())
```

Thời gian:

```text
task 1 → 5 giây
task 2 → 1 giây
task 3 → 3 giây
```

Thứ tự hoàn thành thực tế:

```text
1s → task 2
3s → task 3
5s → task 1
```

Nhưng code lại:

```python
for future in futures:
    future.result()
```

nên:

```text
Main thread
    │
    ▼
future task 1
    │
    │ WAIT 5s
    ▼
result 1

future task 2
    │
    ▼
result 2

future task 3
```

Trong khi task 2 đã xong từ giây thứ 1.

Đây gọi là **head-of-line blocking**.

---

# 2. `as_completed()` giải quyết vấn đề này

Thay:

```python
for future in futures:
    result = future.result()
```

bằng:

```python
from concurrent.futures import as_completed

for future in as_completed(futures):
    result = future.result()
```

Bây giờ:

```text
task 2 ── 1s ──► result 2
task 3 ── 3s ──► result 3
task 1 ── 5s ──► result 1
```

Kết quả:

```text
2
3
1
```

Đây là một pattern cực kỳ quan trọng.

---

# 3. `as_completed()` là gì?

Cú pháp:

```python
as_completed(fs)
```

Trong đó:

```python
fs
```

là một iterable chứa các `Future`.

Ví dụ:

```python
futures = [
    future1,
    future2,
    future3,
]
```

Sau đó:

```python
for future in as_completed(futures):
    ...
```

`as_completed()` trả về các Future **theo thứ tự chúng hoàn thành**.

Không phải thứ tự submit.

---

# 4. Ví dụ đầy đủ

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


def task(n):
    delay = 6 - n

    print(f"START {n}")

    time.sleep(delay)

    print(f"DONE {n}")

    return n * 10


with ThreadPoolExecutor(max_workers=3) as executor:

    futures = [
        executor.submit(task, i)
        for i in range(1, 4)
    ]

    for future in as_completed(futures):

        result = future.result()

        print("RESULT:", result)
```

Các task:

```text
task 1 → 5s
task 2 → 4s
task 3 → 3s
```

Kết quả:

```text
DONE 3
RESULT: 30

DONE 2
RESULT: 20

DONE 1
RESULT: 10
```

---

# 5. Tại sao `as_completed()` rất hữu ích?

Giả sử crawler có:

```text
1000 URL
```

Bạn submit:

```text
URL 1
URL 2
URL 3
...
URL 1000
```

Một URL:

```text
2 giây
```

URL khác:

```text
0.1 giây
```

Nếu chờ theo thứ tự:

```python
for future in futures:
    future.result()
```

thì một URL chậm đầu danh sách có thể làm trì hoãn việc xử lý các kết quả đã hoàn thành.

Với:

```python
for future in as_completed(futures):
```

ta xử lý:

```text
URL nào xong trước
        ↓
xử lý ngay
        ↓
URL tiếp theo
```

Đây chính là pattern phù hợp với:

* web crawler
* downloader
* API client
* batch HTTP request
* parallel file processing

---

# 6. Nhưng `as_completed()` trả về Future, không phải result

Đây là điểm cần nhớ.

```python
for future in as_completed(futures):
```

`future` vẫn là:

```python
Future
```

Muốn lấy kết quả:

```python
result = future.result()
```

Do đó:

```python
for future in as_completed(futures):
    print(future.result())
```

---

# 7. Xử lý exception với `as_completed()`

Giả sử:

```python
def task(n):

    if n == 3:
        raise ValueError("Task failed")

    return n * 10
```

Ta phải viết:

```python
for future in as_completed(futures):

    try:
        result = future.result()
        print("SUCCESS:", result)

    except Exception as e:
        print("ERROR:", e)
```

Mental model:

```text
Worker
   │
   ├── success ───────► Future
   │                       │
   │                       ▼
   │                 future.result()
   │
   └── exception ─────► Future
                           │
                           ▼
                    future.result()
                           │
                           ▼
                    raise exception
```

---

# 8. Một pattern production tốt

Thường ta sẽ viết:

```python
for future in as_completed(futures):

    try:
        result = future.result()

    except Exception as e:
        print("Task failed:", e)

    else:
        print("Task success:", result)
```

Tách rõ:

```text
try
  ↓
lấy result

except
  ↓
task failed

else
  ↓
task success
```

---

# 9. Mapping Future → input

Đây là một kỹ thuật **cực kỳ quan trọng**.

Giả sử crawler:

```python
urls = [
    "url1",
    "url2",
    "url3",
]
```

Ta submit:

```python
future = executor.submit(download, url)
```

Sau đó:

```python
as_completed(futures)
```

nhưng ta cần biết:

> Future này thuộc URL nào?

Giải pháp:

```python
future_to_url = {}

for url in urls:

    future = executor.submit(download, url)

    future_to_url[future] = url
```

Sau đó:

```python
for future in as_completed(future_to_url):

    url = future_to_url[future]

    try:
        result = future.result()

    except Exception as e:
        print(url, "FAILED:", e)

    else:
        print(url, "SUCCESS:", result)
```

---

# 10. Đây là pattern bạn nên thuộc lòng

```python
future_to_item = {}

for item in items:

    future = executor.submit(worker, item)

    future_to_item[future] = item


for future in as_completed(future_to_item):

    item = future_to_item[future]

    try:
        result = future.result()

    except Exception as e:
        print(item, "FAILED:", e)

    else:
        print(item, "SUCCESS:", result)
```

Đây là một trong những pattern nền tảng của concurrent programming bằng `concurrent.futures`.

---

# 11. Ví dụ crawler

Ví dụ:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random


def crawl(url):
    delay = random.uniform(1, 4)

    time.sleep(delay)

    if "bad" in url:
        raise RuntimeError("Cannot crawl")

    return f"Content of {url}"


urls = [
    "https://site.com/a",
    "https://site.com/b",
    "https://site.com/bad",
    "https://site.com/d",
]


with ThreadPoolExecutor(max_workers=3) as executor:

    future_to_url = {
        executor.submit(crawl, url): url
        for url in urls
    }

    for future in as_completed(future_to_url):

        url = future_to_url[future]

        try:
            content = future.result()

        except Exception as e:
            print(f"[ERROR] {url}: {e}")

        else:
            print(f"[SUCCESS] {url}")
```

Đây chính là nền tảng cho crawler worker.

---

# 12. `as_completed()` có `timeout`

Có thể:

```python
as_completed(
    futures,
    timeout=10,
)
```

Ví dụ:

```python
from concurrent.futures import as_completed, TimeoutError


try:

    for future in as_completed(
        futures,
        timeout=10,
    ):
        print(future.result())

except TimeoutError:
    print("Not all tasks completed")
```

Điểm rất quan trọng:

```python
timeout=10
```

là timeout cho **toàn bộ quá trình chờ iterator**, không phải timeout riêng cho từng task.

---

# 13. `wait()` là gì?

Bây giờ đến công cụ thứ hai:

```python
from concurrent.futures import wait
```

Cú pháp:

```python
done, not_done = wait(futures)
```

Nó trả về hai tập hợp:

```text
done
not_done
```

Ví dụ:

```python
done, not_done = wait(futures)
```

Mental model:

```text
                futures
                   │
                   ▼
                 wait()
                   │
          ┌────────┴────────┐
          ▼                 ▼
        done             not_done
```

---

# 14. Ví dụ `wait()`

```python
from concurrent.futures import ThreadPoolExecutor, wait
import time


def task(n):
    time.sleep(n)
    return n


with ThreadPoolExecutor(max_workers=3) as executor:

    futures = [
        executor.submit(task, 1),
        executor.submit(task, 2),
        executor.submit(task, 3),
    ]

    done, not_done = wait(futures)

    print("DONE:", len(done))
    print("NOT DONE:", len(not_done))
```

Không truyền timeout:

```python
wait(futures)
```

sẽ chờ cho **tất cả Future hoàn thành**.

---

# 15. `wait()` khác `as_completed()` thế nào?

Đây là điểm cần phân biệt rõ.

### `wait()`

Cho bạn:

```text
done
not_done
```

Ví dụ:

```python
done, not_done = wait(futures)
```

Nó thích hợp khi bạn muốn:

> "Đợi một điều kiện nào đó xảy ra."

---

### `as_completed()`

Cho bạn từng Future:

```python
for future in as_completed(futures):
```

Nó thích hợp khi bạn muốn:

> "Task nào xong thì xử lý ngay task đó."

---

# 16. `wait()` với timeout

Ví dụ:

```python
done, not_done = wait(
    futures,
    timeout=2,
)
```

Sau 2 giây:

```text
done
```

chứa task đã hoàn thành.

```text
not_done
```

chứa task chưa hoàn thành.

Ví dụ:

```text
Task A → 1s
Task B → 2s
Task C → 5s
```

Sau:

```python
wait(..., timeout=2)
```

có thể:

```text
done:
    A
    B

not_done:
    C
```

---

# 17. `wait()` không cancel task

Giống `result(timeout=...)`.

```python
done, not_done = wait(
    futures,
    timeout=2,
)
```

không có nghĩa:

```text
task chưa xong → cancel
```

Nó chỉ có nghĩa:

```text
Main thread
     │
     ▼
   wait()
     │
     │ tối đa 2s
     ▼
trả về done / not_done
```

Worker vẫn tiếp tục chạy.

---

# 18. `return_when`

Đây là phần quan trọng nhất của `wait()`.

Cú pháp:

```python
wait(
    futures,
    return_when=...
)
```

Có ba giá trị quan trọng:

```python
FIRST_COMPLETED
FIRST_EXCEPTION
ALL_COMPLETED
```

---

# 19. `ALL_COMPLETED`

Mặc định:

```python
wait(
    futures,
    return_when=ALL_COMPLETED,
)
```

nghĩa là:

> Chờ tất cả Future hoàn thành.

Tương đương ý tưởng:

```text
A ───────► done
B ───────────► done
C ───────────────► done
                    │
                    ▼
                  return
```

---

# 20. `FIRST_COMPLETED`

Ví dụ:

```python
from concurrent.futures import wait, FIRST_COMPLETED
```

Sau đó:

```python
done, not_done = wait(
    futures,
    return_when=FIRST_COMPLETED,
)
```

Nghĩa là:

> Return ngay khi **ít nhất một Future hoàn thành**.

Ví dụ:

```text
A ────────────── 5s
B ── 1s
C ─────── 3s
```

thì:

```text
1s
│
▼
B finished
│
▼
wait() returns
```

Kết quả:

```text
done = {B}
not_done = {A, C}
```

---

# 21. `FIRST_EXCEPTION`

```python
from concurrent.futures import FIRST_EXCEPTION
```

Sau đó:

```python
done, not_done = wait(
    futures,
    return_when=FIRST_EXCEPTION,
)
```

Nghĩa là:

> Return khi có Future đầu tiên phát sinh exception.

Ví dụ:

```text
A ───── success
B ── exception
C ───────── success
```

Khi B lỗi:

```text
wait()
  │
  ▼
return
```

Nhưng cần lưu ý:

> `FIRST_EXCEPTION` không tự động cancel các task còn lại.

---

# 22. So sánh trực tiếp

| Công cụ           | Mục đích                         |
| ----------------- | -------------------------------- |
| `future.result()` | Lấy kết quả một Future           |
| `as_completed()`  | Xử lý từng Future khi hoàn thành |
| `wait()`          | Chờ theo điều kiện               |
| `FIRST_COMPLETED` | Chờ task đầu tiên xong           |
| `FIRST_EXCEPTION` | Chờ exception đầu tiên           |
| `ALL_COMPLETED`   | Chờ tất cả                       |

---

# 23. Pattern `as_completed()` cho crawler

Đây là pattern tôi muốn bạn đặc biệt ghi nhớ:

```python
with ThreadPoolExecutor(max_workers=10) as executor:

    future_to_url = {
        executor.submit(crawl, url): url
        for url in urls
    }

    for future in as_completed(future_to_url):

        url = future_to_url[future]

        try:
            result = future.result()

        except Exception as e:
            print(f"[ERROR] {url}: {e}")

        else:
            print(f"[OK] {url}")
```

Đây gần như là:

```text
Crawler
   │
   ├── URL
   ├── URL
   ├── URL
   └── URL
        │
        ▼
 ThreadPoolExecutor
        │
        ▼
     Workers
        │
        ▼
     Futures
        │
        ▼
 as_completed()
        │
   ┌────┴────┐
   ▼         ▼
SUCCESS    ERROR
```

---

# 24. Một pattern khác: `wait(FIRST_COMPLETED)`

Pattern này hữu ích khi bạn muốn quản lý số lượng task đang chạy.

Ví dụ ý tưởng:

```text
10 worker đang chạy

      ↓

một task hoàn thành

      ↓

wait(FIRST_COMPLETED)

      ↓

lấy task hoàn thành

      ↓

submit task mới
```

Đây là nền tảng để xây:

* bounded concurrency
* producer/consumer
* dynamic task scheduling
* crawler scheduler

Chúng ta sẽ đi sâu hơn ở phần Pattern.

---

# 25. Một ví dụ thực tế hơn

Giả sử cần tải:

```python
urls = [...]
```

Nhưng ta muốn:

```text
tối đa 3 request đồng thời
```

Ban đầu:

```text
Worker 1 → URL 1
Worker 2 → URL 2
Worker 3 → URL 3
```

Khi URL 2 xong:

```text
Worker 2 → URL 5
```

Trong khi:

```text
Worker 1 → URL 1
Worker 3 → URL 3
```

Đây là mô hình:

```text
┌──────────────────────────────┐
│       3 active workers       │
└──────────────────────────────┘
       │       │       │
       ▼       ▼       ▼
      URL1    URL3    URL2
                       │
                       ▼
                     DONE
                       │
                       ▼
                      URL4
```

`as_completed()` và `wait(FIRST_COMPLETED)` là hai công cụ quan trọng để xây logic kiểu này.

---

# 26. Sai lầm phổ biến #1

Sai:

```python
for future in futures:
    result = future.result()
```

nếu mục tiêu là:

> xử lý ngay task hoàn thành.

Đúng hơn:

```python
for future in as_completed(futures):
    result = future.result()
```

---

# 27. Sai lầm phổ biến #2

Sai khi nghĩ:

```python
wait(
    futures,
    timeout=5,
)
```

sẽ dừng task sau 5 giây.

Không.

Nó chỉ dừng **việc chờ của thread gọi `wait()`**.

---

# 28. Sai lầm phổ biến #3

Sai khi nghĩ:

```python
FIRST_COMPLETED
```

sẽ cancel các task còn lại.

Không.

Ví dụ:

```text
A → done
B → running
C → running
```

`wait(FIRST_COMPLETED)` return:

```text
done = A
not_done = B, C
```

B và C vẫn chạy.

Nếu muốn cancel:

```python
for future in not_done:
    future.cancel()
```

Nhưng chỉ những Future chưa bắt đầu chạy mới có thể cancel thành công.

---

# 29. Bài thực hành 1 — Completion Order

Viết:

```python
def task(n):
    ...
```

với thời gian:

```text
task 1 → 5s
task 2 → 1s
task 3 → 4s
task 4 → 2s
task 5 → 3s
```

Chạy bằng:

```python
ThreadPoolExecutor(max_workers=5)
```

Sau đó dùng:

```python
as_completed()
```

In:

```text
Task 2 completed
Task 4 completed
Task 5 completed
Task 3 completed
Task 1 completed
```

Bạn phải thấy thứ tự **completion order**, không phải submit order.

---

# 30. Bài thực hành 2 — Mapping

Tạo:

```python
urls = [
    "url-1",
    "url-2",
    "url-3",
    "url-4",
    "url-5",
]
```

Tạo:

```python
future_to_url
```

và dùng:

```python
as_completed()
```

để in:

```text
[OK] url-3
[OK] url-1
[ERROR] url-5
...
```

---

# 31. Bài thực hành 3 — `wait()`

Tạo 5 task có thời gian:

```text
1s
2s
3s
4s
5s
```

Chạy:

```python
done, not_done = wait(
    futures,
    timeout=2,
)
```

Quan sát:

```python
len(done)
len(not_done)
```

Sau đó thử:

```python
FIRST_COMPLETED
```

và:

```python
ALL_COMPLETED
```

So sánh.

---

# 32. Bài thực hành 4 — `FIRST_EXCEPTION`

Tạo 5 task:

```text
Task 1 → success
Task 2 → success
Task 3 → exception
Task 4 → success
Task 5 → success
```

Chạy:

```python
done, not_done = wait(
    futures,
    return_when=FIRST_EXCEPTION,
)
```

Quan sát:

```python
done
not_done
```

Sau đó kiểm tra từng Future:

```python
for future in done:
    print(
        future.done(),
        future.exception(),
    )
```

---

# 33. Bài tập quan trọng nhất

Xây một mini downloader giả lập:

```text
10 URLs
max_workers = 3
```

Mỗi URL:

```python
time.sleep(random.uniform(1, 5))
```

Một số URL ngẫu nhiên thất bại.

Yêu cầu:

```text
[START] url
[SUCCESS] url
[FAILED] url
```

và khi một URL hoàn thành:

```text
completed = 1/10
completed = 2/10
completed = 3/10
...
```

Gợi ý kiến trúc:

```python
future_to_url = {
    executor.submit(download, url): url
    for url in urls
}

for future in as_completed(future_to_url):
    ...
```

Đây là bài rất đáng làm vì nó gần với **crawler worker thực tế**.

---

# Tổng kết Buổi 3

Hôm nay cần phân biệt thật chắc:

```text
future.result()
      │
      └── lấy kết quả một Future


as_completed(futures)
      │
      └── lấy Future theo completion order


wait(futures)
      │
      └── chờ theo condition
```

Và:

```text
wait(..., ALL_COMPLETED)
        ↓
chờ tất cả

wait(..., FIRST_COMPLETED)
        ↓
task đầu tiên hoàn thành

wait(..., FIRST_EXCEPTION)
        ↓
exception đầu tiên
```

Đặc biệt, hãy ghi nhớ pattern:

```python
future_to_item = {
    executor.submit(worker, item): item
    for item in items
}

for future in as_completed(future_to_item):

    item = future_to_item[future]

    try:
        result = future.result()
    except Exception as e:
        ...
    else:
        ...
```

**Buổi 4** chúng ta sẽ đi vào phần rất quan trọng: **`Executor.map()`**, so sánh sâu `map()` vs `submit()` vs `as_completed()`, thứ tự kết quả, lazy/eager behavior và khi nào `map()` phù hợp — đặc biệt trong xử lý hàng nghìn task.
