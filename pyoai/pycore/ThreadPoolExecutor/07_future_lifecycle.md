# ThreadPoolExecutor Deep Dive — Buổi 7

## Future Lifecycle — `PENDING → RUNNING → FINISHED`, Cancel, Timeout và Retry

Ở 6 buổi trước, chúng ta đã hiểu:

```text
ThreadPoolExecutor
        │
        ├── Worker
        ├── max_workers
        ├── Task Queue
        ├── map()
        ├── submit()
        ├── as_completed()
        ├── wait()
        └── GIL
```

Hôm nay chúng ta tập trung vào **`Future`**.

Đây là một trong những abstraction quan trọng nhất của `concurrent.futures`.

---

# 1. Future là gì?

Khi viết:

```python
future = executor.submit(task)
```

`task()` chưa nhất thiết đã hoàn thành.

`future` là một object đại diện cho:

> **Kết quả sẽ có trong tương lai của một task đang được executor quản lý.**

Mental model:

```text
submit()
   │
   ▼
 Future
   │
   ├── task đang chờ
   ├── task đang chạy
   ├── task hoàn thành
   └── task lỗi
```

---

# 2. Future không phải kết quả

Đây là lỗi rất phổ biến.

```python
future = executor.submit(add, 1, 2)
```

Không phải:

```python
future == 3
```

Mà:

```text
future
   │
   ▼
[ một lời hứa về kết quả ]
```

Muốn lấy kết quả:

```python
result = future.result()
```

---

# 3. Lifecycle của Future

Một Future có thể hình dung:

```text
             submit()
                │
                ▼
             PENDING
                │
                ▼
             RUNNING
             /     \
            /       \
           ▼         ▼
       FINISHED    CANCELLED
        /    \
       ▼      ▼
   SUCCESS   EXCEPTION
```

Cần nhớ:

```text
PENDING
   ↓
RUNNING
   ↓
FINISHED
```

hoặc:

```text
PENDING
   ↓
CANCELLED
```

---

# 4. `PENDING`

Ngay sau:

```python
future = executor.submit(task)
```

task có thể đang:

```text
PENDING
```

nghĩa là:

> Executor đã nhận task nhưng worker chưa bắt đầu chạy task đó.

Ví dụ:

```python
from concurrent.futures import ThreadPoolExecutor
import time


def task():
    time.sleep(3)


with ThreadPoolExecutor(max_workers=1) as executor:

    future1 = executor.submit(task)
    future2 = executor.submit(task)

    print(future1.running())
    print(future2.running())
```

Có thể:

```text
True
False
```

vì:

```text
Worker
  ↓
task 1 → RUNNING

Queue
  ↓
task 2 → PENDING
```

---

# 5. `running()`

Kiểm tra:

```python
future.running()
```

Ví dụ:

```python
if future.running():
    print("Task đang chạy")
```

Trả về:

```python
True
```

nếu worker đã bắt đầu thực hiện task.

---

# 6. `done()`

Kiểm tra:

```python
future.done()
```

Trả về `True` nếu Future đã hoàn tất.

Quan trọng:

```text
done()
```

bao gồm cả:

```text
SUCCESS
EXCEPTION
CANCELLED
```

Tức là:

```python
future.done()
```

không có nghĩa:

> task thành công.

Nó chỉ có nghĩa:

> task đã kết thúc lifecycle.

---

# 7. Ví dụ

```python
from concurrent.futures import ThreadPoolExecutor
import time


def task():
    time.sleep(2)
    return 100


with ThreadPoolExecutor(max_workers=1) as executor:

    future = executor.submit(task)

    print("running:", future.running())
    print("done:", future.done())

    time.sleep(3)

    print("running:", future.running())
    print("done:", future.done())
```

Ban đầu:

```text
running: True
done: False
```

Sau đó:

```text
running: False
done: True
```

---

# 8. `result()`

Đây là method quan trọng nhất:

```python
future.result()
```

Nếu task chưa xong:

```python
future.result()
```

sẽ **block** và chờ.

Ví dụ:

```python
future = executor.submit(task)

result = future.result()
```

Mental model:

```text
future.result()
      │
      ▼
task chưa xong?
      │
      ├── YES → WAIT
      │
      └── NO  → return result
```

---

# 9. `result(timeout=...)`

Có thể giới hạn thời gian chờ:

```python
future.result(timeout=2)
```

Ví dụ:

```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import time


def task():
    time.sleep(5)
    return 100


with ThreadPoolExecutor() as executor:

    future = executor.submit(task)

    try:
        result = future.result(timeout=2)
        print(result)

    except TimeoutError:
        print("Task chưa hoàn thành")
```

Sau 2 giây:

```text
TimeoutError
```

Nhưng cực kỳ quan trọng:

> **Timeout của `result()` không tự động dừng task.**

Task vẫn có thể tiếp tục chạy.

---

# 10. Đây là lỗi hiểu nhầm rất nguy hiểm

Bạn viết:

```python
future.result(timeout=2)
```

rồi nghĩ:

```text
2 seconds
↓
task bị kill
```

Không.

Thực tế:

```text
future.result(timeout=2)
        │
        ▼
caller ngừng chờ
        │
        ▼
task vẫn chạy
```

Ví dụ:

```text
Worker
  │
  ├────────────── Task ────────────────► DONE
  │
Caller
  │
  ├── result(timeout=2)
  │
  └── TimeoutError
```

---

# 11. `exception()`

Nếu task lỗi:

```python
future.exception()
```

có thể lấy exception.

Ví dụ:

```python
from concurrent.futures import ThreadPoolExecutor


def task():
    raise ValueError("Something went wrong")


with ThreadPoolExecutor() as executor:

    future = executor.submit(task)

    future.result()
```

sẽ raise:

```text
ValueError
```

Nhưng:

```python
future.exception()
```

sẽ trả về object exception:

```text
ValueError("Something went wrong")
```

---

# 12. `result()` và `exception()` khác nhau

### `result()`

```python
future.result()
```

→ trả kết quả hoặc **raise exception**.

### `exception()`

```python
future.exception()
```

→ trả exception object hoặc `None`.

Ví dụ:

```python
try:
    result = future.result()

except Exception as e:
    print("ERROR:", e)
```

thường phù hợp khi muốn xử lý lỗi.

---

# 13. `cancel()`

Đây là method rất quan trọng:

```python
future.cancel()
```

Nó cố gắng hủy task.

Nhưng chỉ hủy được task **chưa bắt đầu chạy**.

---

# 14. Ví dụ cancel thành công

```python
from concurrent.futures import ThreadPoolExecutor
import time


def task(n):
    print("RUN", n)
    time.sleep(3)


with ThreadPoolExecutor(max_workers=1) as executor:

    future1 = executor.submit(task, 1)
    future2 = executor.submit(task, 2)

    print(
        "cancel:",
        future2.cancel()
    )
```

Vì:

```text
max_workers = 1
```

nên:

```text
Worker
   │
   └── Task 1 RUNNING

Queue
   │
   └── Task 2 PENDING
```

Do đó:

```python
future2.cancel()
```

có thể thành công.

---

# 15. `cancel()` trả về Boolean

```python
success = future.cancel()
```

Có thể:

```text
True
```

hoặc:

```text
False
```

### `True`

Task đã được hủy.

### `False`

Task không thể hủy, thường vì đã chạy hoặc đã hoàn thành.

---

# 16. Không thể cancel task đang chạy

Ví dụ:

```python
future = executor.submit(task)

time.sleep(0.1)

print(
    future.cancel()
)
```

Nếu worker đã bắt đầu:

```text
RUNNING
```

thì:

```text
cancel() → False
```

---

# 17. `cancelled()`

Kiểm tra:

```python
future.cancelled()
```

Ví dụ:

```python
if future.cancelled():
    print("Task đã bị cancel")
```

Quan hệ:

```text
cancel()
   ↓
True
   ↓
cancelled() == True
```

---

# 18. State transition đầy đủ

Hãy nhớ sơ đồ:

```text
                    submit()
                       │
                       ▼
                    PENDING
                       │
               ┌───────┴────────┐
               │                │
            cancel()          worker
               │                │
               ▼                ▼
          CANCELLED          RUNNING
                                │
                         ┌──────┴──────┐
                         │             │
                      success       exception
                         │             │
                         ▼             ▼
                      FINISHED      FINISHED
```

---

# 19. `done()` trong tất cả trường hợp

Ví dụ:

```text
SUCCESS
   ↓
done() == True
```

```text
EXCEPTION
   ↓
done() == True
```

```text
CANCELLED
   ↓
done() == True
```

Vì vậy:

```python
future.done()
```

chỉ trả lời:

> "Future đã kết thúc chưa?"

Không trả lời:

> "Task có thành công không?"

---

# 20. `add_done_callback()`

Đây là một API rất hay.

Bạn có thể đăng ký callback:

```python
future.add_done_callback(callback)
```

Callback sẽ được gọi khi Future hoàn thành.

Ví dụ:

```python
from concurrent.futures import ThreadPoolExecutor
import time


def task():
    time.sleep(2)
    return 42


def on_done(future):
    print(
        "DONE:",
        future.result()
    )


with ThreadPoolExecutor() as executor:

    future = executor.submit(task)

    future.add_done_callback(on_done)
```

Sau khoảng 2 giây:

```text
DONE: 42
```

---

# 21. Callback chạy khi Future hoàn thành

Mental model:

```text
submit()
   │
   ▼
Future
   │
   ▼
RUNNING
   │
   ▼
FINISHED
   │
   ▼
callback(future)
```

Rất phù hợp cho:

```text
logging
metrics
notification
cleanup
```

---

# 22. Nhưng đừng làm callback quá nặng

Ví dụ không nên:

```python
def callback(future):
    huge_cpu_task()
```

Callback nên:

```text
nhẹ
nhanh
không block
```

Nếu callback thực hiện computation nặng, bạn có thể làm phức tạp việc quản lý worker.

---

# 23. Lấy kết quả an toàn trong callback

Không nên mặc định:

```python
def callback(future):
    print(future.result())
```

nếu task có thể lỗi.

Tốt hơn:

```python
def callback(future):

    try:
        result = future.result()

    except Exception as e:
        print("ERROR:", e)

    else:
        print("RESULT:", result)
```

---

# 24. Retry — bắt đầu xây cơ chế retry

Giả sử crawler:

```text
URL
 ↓
request
 ↓
timeout
```

Ta muốn:

```text
retry 3 times
```

Một cách đơn giản:

```python
def crawl(url):

    for attempt in range(3):

        try:
            return request(url)

        except Exception:
            if attempt == 2:
                raise
```

Đây là retry **bên trong task**.

---

# 25. Retry bằng Future

Một cách khác là quản lý ở bên ngoài:

```text
Future
  ↓
failed
  ↓
submit lại
  ↓
Future mới
```

Ví dụ:

```python
from concurrent.futures import ThreadPoolExecutor


def crawl(url):
    ...
```

Ta có:

```python
future = executor.submit(crawl, url)
```

Nếu:

```python
future.result()
```

raise:

```text
Exception
```

ta submit lại:

```python
executor.submit(crawl, url)
```

Đây là kiến trúc quan trọng cho crawler.

---

# 26. Nhưng retry phải cẩn thận

Không phải exception nào cũng nên retry.

Ví dụ:

```text
Timeout
ConnectionError
503
429
```

có thể retry.

Nhưng:

```text
404
invalid URL
parse bug
authentication failure
```

không nhất thiết retry.

Đây là lý do production crawler cần:

```text
Exception classification
```

---

# 27. Retry với exponential backoff

Không nên:

```text
retry
retry
retry
retry
```

ngay lập tức.

Nên:

```text
Attempt 1
   ↓
wait 1s

Attempt 2
   ↓
wait 2s

Attempt 3
   ↓
wait 4s
```

Công thức đơn giản:

```python
delay = 2 ** attempt
```

Ví dụ:

```text
attempt 0 → 1s
attempt 1 → 2s
attempt 2 → 4s
```

Sau này chúng ta sẽ xây retry framework hoàn chỉnh.

---

# 28. Timeout và cancel là hai thứ khác nhau

Đây là điểm cần thuộc.

### Timeout

```python
future.result(timeout=5)
```

nghĩa:

> Tôi chỉ chờ tối đa 5 giây.

Không có nghĩa:

> Task bị dừng sau 5 giây.

---

### Cancel

```python
future.cancel()
```

nghĩa:

> Cố gắng hủy task nếu nó chưa chạy.

---

# 29. Không có "kill running thread" an toàn

Python không cung cấp một API kiểu:

```python
future.kill()
```

để cưỡng chế giết một thread đang chạy.

Đây là lý do các task nên hỗ trợ:

```text
timeout
cooperative cancellation
```

thay vì trông chờ vào việc kill thread.

---

# 30. Cooperative cancellation

Ví dụ:

```python
import threading
import time


stop_event = threading.Event()


def worker():

    for i in range(100):

        if stop_event.is_set():
            print("STOP")
            return

        time.sleep(0.2)

        print(i)
```

Thread tự kiểm tra:

```python
stop_event.is_set()
```

và tự kết thúc.

Đây là:

> **cooperative cancellation**

Rất quan trọng trong concurrent programming.

---

# 31. ThreadPoolExecutor + Event

Ví dụ:

```python
from concurrent.futures import ThreadPoolExecutor
import threading
import time


stop_event = threading.Event()


def task(n):

    for i in range(20):

        if stop_event.is_set():
            print("Task", n, "stopped")
            return

        time.sleep(0.2)

    return n


with ThreadPoolExecutor(max_workers=3) as executor:

    futures = [
        executor.submit(task, i)
        for i in range(5)
    ]

    time.sleep(1)

    stop_event.set()

    for future in futures:
        future.result()
```

Đây là cách đúng hơn nếu cần yêu cầu các task đang chạy dừng một cách hợp tác.

---

# 32. `shutdown(cancel_futures=True)`

Executor cũng có:

```python
executor.shutdown(
    cancel_futures=True
)
```

Ý tưởng:

> Hủy những futures **chưa bắt đầu chạy**.

Không có nghĩa:

```text
running threads
→ bị kill
```

Các task đang chạy vẫn cần tự hoàn thành hoặc tự kiểm tra cancellation.

---

# 33. Một kiến trúc shutdown tốt

```text
Main thread
    │
    ▼
stop_event.set()
    │
    ├── Worker 1 → kiểm tra → stop
    ├── Worker 2 → kiểm tra → stop
    └── Worker 3 → kiểm tra → stop
```

và:

```python
executor.shutdown(
    wait=True,
    cancel_futures=True,
)
```

---

# 34. Một ví dụ Future lifecycle hoàn chỉnh

```python
from concurrent.futures import ThreadPoolExecutor
import time


def task(n):

    time.sleep(2)

    if n == 3:
        raise ValueError("Boom")

    return n * 10


with ThreadPoolExecutor(max_workers=2) as executor:

    future = executor.submit(task, 3)

    print("running:", future.running())
    print("done:", future.done())

    try:
        result = future.result(timeout=5)

    except Exception as e:
        print("error:", e)

    print("done:", future.done())
    print("cancelled:", future.cancelled())
    print("exception:", future.exception())
```

Bạn sẽ thấy:

```text
running: ...
done: False

error: Boom

done: True
cancelled: False
exception: Boom
```

---

# 35. Future state machine

Hãy học thuộc mô hình:

```text
                submit()
                   │
                   ▼
                PENDING
                   │
          ┌────────┴─────────┐
          │                  │
       cancel()            start
          │                  │
          ▼                  ▼
      CANCELLED           RUNNING
                              │
                       ┌──────┴──────┐
                       ▼             ▼
                    SUCCESS       ERROR
                       │             │
                       └──────┬──────┘
                              ▼
                           FINISHED
```

API tương ứng:

```text
PENDING
   → running()

RUNNING
   → running()

FINISHED
   → done()

CANCELLED
   → cancelled()
   → done()
```

---

# 36. Bài tập 1 — Future State Machine

Viết:

```python
def task():
    time.sleep(3)
    return 100
```

Sau đó in:

```python
future.running()
future.done()
future.cancelled()
```

ở các thời điểm:

```text
ngay sau submit
sau 1 giây
sau 4 giây
```

Quan sát lifecycle.

---

# 37. Bài tập 2 — Cancel

Dùng:

```python
max_workers=1
```

submit 5 task:

```text
Task 1
Task 2
Task 3
Task 4
Task 5
```

Sau đó thử:

```python
future.cancel()
```

với Task 3, 4, 5.

Kiểm tra:

```python
future.cancelled()
future.done()
```

Mục tiêu:

> Hiểu rõ task nào có thể cancel và task nào không.

---

# 38. Bài tập 3 — Timeout

Tạo:

```python
def task():
    time.sleep(10)
```

Sau đó:

```python
future.result(timeout=2)
```

Bắt:

```python
TimeoutError
```

Sau khi timeout:

```python
print(future.running())
print(future.done())
```

Quan sát.

Điều quan trọng cần nhận ra:

```text
TimeoutError
≠
task stopped
```

---

# 39. Bài tập 4 — Callback

Viết:

```python
def callback(future):
    ...
```

và:

```python
future.add_done_callback(callback)
```

Callback phải xử lý được cả:

```text
SUCCESS
ERROR
```

Ví dụ:

```text
SUCCESS → print(result)
ERROR   → print(exception)
```

---

# 40. Bài tập 5 — Retry

Viết một task giả lập:

```python
def crawl(url):
    ...
```

Trong đó:

```text
lần 1 → lỗi
lần 2 → lỗi
lần 3 → thành công
```

Xây:

```text
submit
 ↓
Future
 ↓
exception
 ↓
retry
 ↓
Future mới
 ↓
success
```

Giới hạn:

```text
max_retries = 3
```

---

# 41. Bài tập lớn — Mini Crawler v1

Đây là bài quan trọng nhất của Buổi 7.

Thiết kế:

```text
URLs
 │
 ▼
ThreadPoolExecutor
 │
 ▼
Future
 │
 ├── success → save
 │
 └── exception
        │
        ▼
      retry
        │
        ▼
      retry queue
```

Mỗi URL có:

```python
{
    "url": "...",
    "attempt": 0,
}
```

Luồng xử lý:

```text
URL
 ↓
submit()
 ↓
Future
 ↓
result()
 ├── SUCCESS → done
 │
 └── ERROR
      │
      ├── attempt < 3
      │      ↓
      │    retry
      │
      └── attempt >= 3
             ↓
           FAILED
```

Đây chính là nền móng cho **crawl-worker** mà bạn đang hướng tới.

---

# 42. Tổng kết Buổi 7

Bạn cần phân biệt thật chắc:

### `running()`

```python
future.running()
```

Task đang được worker thực thi.

### `done()`

```python
future.done()
```

Task đã kết thúc lifecycle.

### `cancelled()`

```python
future.cancelled()
```

Future đã bị cancel.

### `cancel()`

```python
future.cancel()
```

Cố gắng cancel task chưa chạy.

### `result()`

```python
future.result()
```

Chờ và lấy kết quả; exception sẽ được raise lại.

### `exception()`

```python
future.exception()
```

Lấy exception object nếu task lỗi.

### `add_done_callback()`

```python
future.add_done_callback(callback)
```

Chạy callback khi Future hoàn thành.

### Timeout

```python
future.result(timeout=5)
```

Chỉ giới hạn thời gian **caller chờ**, không kill running thread.

---

## Mental model quan trọng nhất

Đừng nghĩ:

```text
submit()
 ↓
result
```

Hãy nghĩ:

```text
submit()
   │
   ▼
 Future
   │
   ▼
PENDING
   │
   ▼
RUNNING
   │
   ├───────────────┐
   ▼               ▼
SUCCESS          EXCEPTION
   │               │
   └───────┬───────┘
           ▼
        FINISHED
```

Và nếu task chưa chạy:

```text
PENDING
   │
   ▼
cancel()
   │
   ▼
CANCELLED
```

**Buổi 8** chúng ta sẽ nâng cấp từ một `Future` lên **quản lý hàng trăm/hàng nghìn Future**: `as_completed()` sâu hơn, mapping `Future → task`, thu thập success/error, progress, retry và xây một **Task Manager** nhỏ — đây sẽ là bước chuyển từ học API sang thiết kế một hệ thống concurrent thực tế.
