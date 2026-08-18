# ThreadPoolExecutor Deep Dive — Buổi 2

## `submit()` và `Future` — hiểu cơ chế Future

Buổi 1 chúng ta đã có mental model:

```text
ThreadPoolExecutor
        │
        │ submit()
        ▼
      Future
        │
        ▼
     Worker
        │
        ▼
     Result
```

Hôm nay chúng ta đi sâu vào **`Future`**, vì đây là trung tâm của `ThreadPoolExecutor`.

---

# 1. `submit()` thực sự làm gì?

Ví dụ:

```python
from concurrent.futures import ThreadPoolExecutor
import time


def task(n):
    time.sleep(2)
    return n * 10


with ThreadPoolExecutor(max_workers=2) as executor:
    future = executor.submit(task, 5)

    print(future)
```

`submit()` có thể hình dung:

```text
executor.submit(task, 5)
          │
          ▼
   tạo một Future
          │
          ▼
   đưa task vào queue
          │
          ▼
      worker lấy task
          │
          ▼
       chạy task(5)
          │
          ▼
      Future = 50
```

Điểm quan trọng:

```python
future = executor.submit(task, 5)
```

**không phải**

```python
result = task(5)
```

mà là:

```python
future = "lời hứa rằng sau này sẽ có kết quả"
```

---

# 2. Future là một object

Bạn có thể kiểm tra:

```python
print(type(future))
```

Kết quả:

```text
<class 'concurrent.futures._base.Future'>
```

Vì vậy:

```python
future.result()
```

là method của object `Future`.

---

# 3. Future State Machine

Đây là phần quan trọng nhất của buổi hôm nay.

Một `Future` có vòng đời:

```text
                 submit()
                    │
                    ▼
                PENDING
                    │
                    ▼
                RUNNING
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
      FINISHED              CANCELLED
          │
     ┌────┴────┐
     ▼         ▼
 SUCCESS    EXCEPTION
```

Có thể hiểu:

```text
PENDING
   │
   │ worker bắt đầu
   ▼
RUNNING
   │
   ├──── success ────► FINISHED
   │
   └──── error ──────► FINISHED
```

Lưu ý:

**Exception không tạo một trạng thái Future riêng.**

Future vẫn hoàn thành, nhưng kết quả của nó là một exception.

---

# 4. `future.done()`

Kiểm tra task đã hoàn thành hay chưa:

```python
future.done()
```

Ví dụ:

```python
from concurrent.futures import ThreadPoolExecutor
import time


def task():
    time.sleep(3)
    return 100


with ThreadPoolExecutor(max_workers=1) as executor:

    future = executor.submit(task)

    print(future.done())

    time.sleep(4)

    print(future.done())
```

Kết quả:

```text
False
True
```

---

# 5. `done()` có nghĩa gì?

```python
future.done()
```

trả về:

```python
bool
```

Nếu:

```text
PENDING
RUNNING
```

thì:

```python
False
```

Nếu:

```text
FINISHED
CANCELLED
```

thì:

```python
True
```

Có thể nhớ:

> `done()` hỏi: "Future này đã kết thúc vòng đời chưa?"

---

# 6. `future.running()`

Kiểm tra task hiện tại có đang được worker thực thi hay không:

```python
future.running()
```

Ví dụ:

```python
from concurrent.futures import ThreadPoolExecutor
import time


def task():
    time.sleep(5)
    return 10


with ThreadPoolExecutor(max_workers=1) as executor:

    future = executor.submit(task)

    time.sleep(1)

    print("done:", future.done())
    print("running:", future.running())
```

Có thể nhận:

```text
done: False
running: True
```

Mental model:

```text
PENDING
   │
   │
running() = False
   │
   ▼
RUNNING
   │
   │
running() = True
   │
   ▼
FINISHED
   │
   │
done() = True
```

---

# 7. `future.cancel()`

Đây là phần dễ hiểu nhầm.

Bạn có thể thử:

```python
future.cancel()
```

Ví dụ:

```python
from concurrent.futures import ThreadPoolExecutor
import time


def task():
    time.sleep(5)
    return 100


with ThreadPoolExecutor(max_workers=1) as executor:

    future = executor.submit(task)

    print(future.cancel())
```

Nếu task chưa chạy:

```text
True
```

Nếu task đã chạy:

```text
False
```

---

# 8. Tại sao đang chạy thì không cancel được?

Giả sử:

```text
Future
   │
   ▼
PENDING
```

Ta có:

```python
future.cancel()
```

thì có thể:

```text
PENDING
   │
   ▼
CANCELLED
```

Nhưng:

```text
RUNNING
   │
   │ cancel()
   ▼
  ❌
```

ThreadPoolExecutor không thể đơn giản "giết" thread đang thực thi Python code.

Do đó:

```python
future.cancel()
```

chỉ thành công khi task **chưa bắt đầu chạy**.

---

# 9. Demo cancel

Muốn thấy rõ điều này, tạo:

```python
from concurrent.futures import ThreadPoolExecutor
import time


def task(name):
    print("start:", name)
    time.sleep(3)
    print("finish:", name)
    return name


with ThreadPoolExecutor(max_workers=1) as executor:

    future1 = executor.submit(task, "A")
    future2 = executor.submit(task, "B")

    print("cancel B:", future2.cancel())

    print("A:", future1.result())

    print("B cancelled:", future2.cancelled())
```

Có thể thấy:

```text
start: A
cancel B: True
finish: A
A: A
B cancelled: True
```

Tại sao?

Chúng ta chỉ có:

```text
Worker 1
   │
   ▼
 Task A
```

Task B đang chờ:

```text
Queue
   │
   └── Task B
```

nên B có thể bị cancel.

---

# 10. `future.cancelled()`

Sau khi cancel:

```python
future.cancelled()
```

sẽ trả:

```text
True
```

Ví dụ:

```python
if future.cancelled():
    print("Task was cancelled")
```

---

# 11. Ba method cần phân biệt

| Method        | Ý nghĩa                    |
| ------------- | -------------------------- |
| `done()`      | Future đã kết thúc chưa?   |
| `running()`   | Task đang chạy không?      |
| `cancelled()` | Future đã bị cancel không? |

Ví dụ:

```python
future.done()
future.running()
future.cancelled()
```

Một Future có thể:

```text
PENDING
done()      = False
running()   = False
cancelled() = False
```

hoặc:

```text
RUNNING
done()      = False
running()   = True
cancelled() = False
```

hoặc:

```text
CANCELLED
done()      = True
running()   = False
cancelled() = True
```

hoặc:

```text
FINISHED
done()      = True
running()   = False
cancelled() = False
```

---

# 12. `future.result()`

Đây là method chúng ta sử dụng rất nhiều.

```python
result = future.result()
```

Nếu task đã xong:

```text
Future
   │
   ▼
result = 100
```

Nếu task chưa xong:

```text
future.result()
      │
      ▼
   WAIT
      │
      ▼
task finished
      │
      ▼
   return result
```

Ví dụ:

```python
def task():
    time.sleep(3)
    return 42
```

thì:

```python
result = future.result()
```

có thể block khoảng 3 giây.

---

# 13. `result(timeout=...)`

Bạn có thể giới hạn thời gian chờ:

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


with ThreadPoolExecutor(max_workers=1) as executor:

    future = executor.submit(task)

    try:
        result = future.result(timeout=2)
        print(result)

    except TimeoutError:
        print("Task took too long")
```

Kết quả:

```text
Task took too long
```

Nhưng cực kỳ quan trọng:

> `timeout` của `result()` **không cancel task**.

Task vẫn đang chạy.

```text
Main Thread
    │
    ├── result(timeout=2)
    │
    └── TimeoutError
              │
              │
              ▼
         Worker vẫn chạy
              │
              ▼
          hoàn thành
```

---

# 14. Đây là một lỗi thiết kế phổ biến

Nhiều người nghĩ:

```python
future.result(timeout=2)
```

nghĩa là:

> "Nếu quá 2 giây thì dừng task."

**Sai.**

Nó chỉ có nghĩa:

> "Main thread chỉ chờ tối đa 2 giây để lấy kết quả."

---

# 15. `future.exception()`

Một method rất quan trọng:

```python
future.exception()
```

Nếu task thành công:

```python
future.exception()
```

trả:

```text
None
```

Nếu task xảy ra exception:

```python
future.exception()
```

trả về exception object.

Ví dụ:

```python
from concurrent.futures import ThreadPoolExecutor


def task():
    raise ValueError("Something went wrong")


with ThreadPoolExecutor(max_workers=1) as executor:

    future = executor.submit(task)

    print(future.exception())
```

Kết quả:

```text
Something went wrong
```

---

# 16. Exception không tự động xuất hiện ở main thread

Đây là điểm rất quan trọng.

Ví dụ:

```python
def task():
    raise ValueError("Boom!")
```

Nếu:

```python
future = executor.submit(task)
```

worker sẽ xảy ra:

```text
Worker Thread
     │
     ▼
 task()
     │
     ▼
ValueError
```

Nhưng main thread không nhất thiết lập tức crash.

Exception được giữ trong `Future`.

```text
Future
 ├── state = FINISHED
 └── exception = ValueError(...)
```

---

# 17. Exception xuất hiện khi gọi `result()`

```python
from concurrent.futures import ThreadPoolExecutor


def task():
    raise ValueError("Boom!")


with ThreadPoolExecutor(max_workers=1) as executor:

    future = executor.submit(task)

    try:
        result = future.result()

    except ValueError as e:
        print("ERROR:", e)
```

Đây là pattern rất quan trọng:

```text
worker
   │
   ▼
exception
   │
   ▼
Future
   │
   ▼
result()
   │
   ▼
raise exception
   │
   ▼
main thread
```

---

# 18. `exception()` vs `result()`

Hai cái khác nhau:

### `exception()`

```python
exc = future.exception()
```

chỉ kiểm tra exception.

### `result()`

```python
result = future.result()
```

lấy kết quả.

Nếu worker có exception:

```python
future.result()
```

sẽ **raise exception**.

Ví dụ:

```python
try:
    result = future.result()
except Exception as e:
    ...
```

---

# 19. Một pattern rất hữu ích

Ta có thể kiểm tra Future:

```python
if future.done():

    if future.cancelled():
        print("Cancelled")

    elif future.exception():
        print("Failed:", future.exception())

    else:
        print("Success:", future.result())
```

Mental model:

```text
              Future.done()
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
      cancelled?           exception?
          │                   │
         yes                 yes
          │                   │
      Cancelled             Failed
                             
                             
                    no
                     │
                     ▼
                   Success
```

---

# 20. Callback — bước đầu tiên

`Future` còn có:

```python
future.add_done_callback(...)
```

Ví dụ:

```python
from concurrent.futures import ThreadPoolExecutor
import time


def task(n):
    time.sleep(2)
    return n * 10


def callback(future):
    print("Task completed")
    print("Result:", future.result())


with ThreadPoolExecutor(max_workers=2) as executor:

    future = executor.submit(task, 10)

    future.add_done_callback(callback)

    print("Main thread continues...")
```

Mental model:

```text
submit()
   │
   ▼
Future
   │
   │ worker chạy
   ▼
finished
   │
   ▼
callback()
```

Callback sẽ được gọi khi Future hoàn thành.

---

# 21. Callback rất quan trọng trong hệ thống lớn

Ví dụ crawler:

```text
Crawler
   │
   ├── submit(url1)
   ├── submit(url2)
   ├── submit(url3)
   │
   ▼
 Future
   │
   ▼
 Downloader
   │
   ▼
 callback
   │
   ├── save result
   ├── update progress
   ├── log
   └── schedule next task
```

Đây sẽ trở thành nền tảng cho crawler worker của bạn.

---

# 22. Một vấn đề với callback

Callback nhận **Future**, không phải result:

```python
def callback(future):
    ...
```

Muốn lấy result:

```python
result = future.result()
```

Muốn lấy exception:

```python
exception = future.exception()
```

Do đó callback production thường nên xử lý cả hai:

```python
def callback(future):
    try:
        result = future.result()
        print("Success:", result)

    except Exception as e:
        print("Failed:", e)
```

---

# 23. Bài thực hành tổng hợp

Hãy chạy chương trình này:

```python
from concurrent.futures import ThreadPoolExecutor
import time
import random


def task(n):
    print(f"[START] {n}")

    time.sleep(random.uniform(1, 4))

    if n == 3:
        raise ValueError("Task 3 failed")

    print(f"[DONE] {n}")

    return n * 10


def callback(future):

    if future.cancelled():
        print("[CANCELLED]")

    elif future.exception():
        print("[ERROR]", future.exception())

    else:
        print("[RESULT]", future.result())


with ThreadPoolExecutor(max_workers=3) as executor:

    futures = []

    for i in range(1, 6):

        future = executor.submit(task, i)

        future.add_done_callback(callback)

        futures.append(future)

    print("All tasks submitted")

    for future in futures:
        print(
            "done=",
            future.done(),
            "running=",
            future.running(),
            "cancelled=",
            future.cancelled(),
        )
```

Quan sát:

```text
START
DONE
ERROR
RESULT
```

và đặc biệt quan sát thứ tự.

**Thứ tự submit không nhất thiết là thứ tự hoàn thành.**

---

# 24. Một insight cực kỳ quan trọng

Giả sử:

```python
future1 = executor.submit(task1)
future2 = executor.submit(task2)
future3 = executor.submit(task3)
```

Ta có:

```text
Submit order:

task1
task2
task3
```

Nhưng nếu:

```text
task1 = 5 giây
task2 = 1 giây
task3 = 3 giây
```

thì completion order có thể:

```text
task2
task3
task1
```

Đây là lý do bài tiếp theo rất quan trọng.

---

# 25. Tổng kết Buổi 2

Bạn cần nắm chắc các API:

```python
future.done()
future.running()
future.cancel()
future.cancelled()
future.result()
future.exception()
future.add_done_callback()
```

Và đặc biệt nhớ:

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

Nếu task chưa chạy:

```python
future.cancel()
```

có thể thành công.

Nếu task đã chạy:

```python
future.cancel()
```

thường thất bại.

Nếu task lỗi:

```python
future.exception()
```

cho biết exception.

Còn:

```python
future.result()
```

sẽ **raise lại exception**.

---

## Bài tập Buổi 2

Viết một chương trình:

```text
5 tasks
max_workers = 2
```

Mỗi task:

* ngủ từ 1–5 giây ngẫu nhiên
* task số 3 cố tình `raise ValueError`
* trả về `n * 100` nếu thành công

Yêu cầu:

1. Lưu tất cả `Future`.
2. In trạng thái `done/running/cancelled`.
3. Lấy kết quả bằng `result()`.
4. Bắt exception.
5. Thêm `callback`.
6. Thử `cancel()` task thứ 4.
7. Thử `result(timeout=1)`.

Sau khi hoàn thành bài này, **Buổi 3** chúng ta sẽ học `wait()` và `as_completed()` — đây là lúc bắt đầu chuyển từ kiểu **"submit tất cả rồi lấy result theo thứ tự"** sang **xử lý kết quả ngay khi từng worker hoàn thành**, cực kỳ quan trọng cho crawler/download worker.
