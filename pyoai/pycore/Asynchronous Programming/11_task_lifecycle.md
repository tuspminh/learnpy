# Python Asynchronous Programming - Buổi 11

# Task Lifecycle & Task Management - Quản lý vòng đời của `asyncio.Task`

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ hiểu:
>
> * Vòng đời (Lifecycle) của một `Task`.
> * Các trạng thái của `Task`.
> * Các phương thức: `done()`, `result()`, `exception()`, `cancel()`, `cancelled()`.
> * Cách hủy (`cancel`) một Task đúng cách.
> * Cách xử lý `CancelledError`.
> * Những lỗi phổ biến khi quản lý Task.

> ⭐ Đây là kiến thức rất quan trọng khi xây dựng các ứng dụng chạy lâu như **FastAPI**, **Discord Bot**, **Telegram Bot**, **WebSocket Server**, **Background Worker**...

---

# 1. Task có vòng đời

Một Task không chỉ đơn giản là "được tạo rồi chạy".

Nó trải qua nhiều trạng thái.

```text
            create_task()
                  │
                  ▼
             PENDING
                  │
                  ▼
             RUNNING
          ┌───────┴────────┐
          ▼                ▼
      COMPLETED        CANCELLED
          │                │
          ▼                ▼
       RESULT         CancelledError
```

---

# 2. Tạo một Task

```python
import asyncio

async def work():
    await asyncio.sleep(2)
    return "Done"

async def main():
    task = asyncio.create_task(work())
    print(task)

    result = await task
    print(result)

asyncio.run(main())
```

Ví dụ đầu ra:

```text
<Task pending ...>

Done
```

Ngay sau khi tạo:

```python
task = asyncio.create_task(...)
```

Task thường ở trạng thái:

```text
PENDING
```

---

# 3. Trạng thái PENDING

Có nghĩa là:

* Task đã được tạo.
* Event Loop đã biết về Task.
* Có thể chưa được chạy hoặc chưa hoàn thành.

Ví dụ:

```python
task = asyncio.create_task(work())

print(task.done())
```

Kết quả:

```text
False
```

---

# 4. `done()`

Kiểm tra Task đã kết thúc chưa.

```python
import asyncio

async def work():
    await asyncio.sleep(1)

async def main():

    task = asyncio.create_task(work())

    print(task.done())

    await task

    print(task.done())

asyncio.run(main())
```

Kết quả:

```text
False

True
```

---

# 5. `result()`

Lấy kết quả trả về của Task.

```python
import asyncio

async def square():

    return 25

async def main():

    task = asyncio.create_task(square())

    await task

    print(task.result())

asyncio.run(main())
```

Kết quả:

```text
25
```

---

# 6. Sai lầm với `result()`

Nếu gọi quá sớm:

```python
task = asyncio.create_task(work())

print(task.result())
```

Lỗi:

```text
InvalidStateError
```

Vì Task:

```text
Chưa xong
```

Muốn dùng `result()`:

* `await task`
* hoặc `task.done() == True`

---

# 7. `exception()`

Nếu Task bị lỗi.

```python
import asyncio

async def work():
    raise ValueError("Something wrong")

async def main():

    task = asyncio.create_task(work())

    try:
        await task
    except ValueError:
        pass

    print(task.exception())

asyncio.run(main())
```

Kết quả:

```text
Something wrong
```

---

# 8. `cancel()`

Đây là API rất quan trọng.

```python
task.cancel()
```

Ý nghĩa:

> Yêu cầu Event Loop hủy Task.

Lưu ý:

Không phải:

```text
Kill ngay lập tức
```

Mà là:

```text
Đánh dấu cần hủy

↓

Coroutine sẽ nhận CancelledError
```

---

# 9. Ví dụ `cancel()`

```python
import asyncio

async def work():

    while True:
        print("Working...")
        await asyncio.sleep(1)

async def main():

    task = asyncio.create_task(work())

    await asyncio.sleep(3)

    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        print("Task cancelled")

asyncio.run(main())
```

Kết quả:

```text
Working...

Working...

Working...

Task cancelled
```

---

# 10. Điều gì xảy ra khi Cancel?

Timeline:

```text
Task

↓

Running

↓

await sleep()

↓

cancel()

↓

CancelledError

↓

Coroutine kết thúc
```

---

# 11. `CancelledError`

Đây là Exception đặc biệt.

Ví dụ:

```python
import asyncio

async def work():

    try:

        while True:
            await asyncio.sleep(1)

    except asyncio.CancelledError:

        print("Cleaning...")

        raise
```

Khi bị hủy:

```text
Cleaning...
```

Đây là nơi thích hợp để:

* đóng file
* đóng database connection
* đóng websocket
* giải phóng tài nguyên

Sau khi dọn dẹp, nên `raise` lại để Task thực sự kết thúc ở trạng thái bị hủy.

---

# 12. `cancelled()`

Kiểm tra Task có bị hủy không.

```python
print(task.cancelled())
```

Ví dụ:

```text
False
```

Sau khi hủy thành công:

```text
True
```

Lưu ý: `cancelled()` chỉ trả về `True` khi Task đã thực sự kết thúc do bị hủy.

---

# 13. Timeline đầy đủ

```text
create_task()

↓

Pending

↓

Running

↓

await

↓

Running

↓

cancel()

↓

CancelledError

↓

Done
```

---

# 14. `done()` và `cancelled()`

Nhiều người nhầm.

Task bị hủy:

```text
Done

=

True
```

Đồng thời:

```text
Cancelled

=

True
```

Vì:

Task đã kết thúc.

---

# 15. Nếu không bắt `CancelledError`

Ví dụ:

```python
async def work():

    while True:

        await asyncio.sleep(1)
```

Nếu:

```python
task.cancel()
```

Task vẫn kết thúc.

Chỉ là:

Không có cơ hội:

```text
Cleanup
```

Do đó, với các Task quản lý tài nguyên, hãy bắt `CancelledError` để dọn dẹp trước khi kết thúc.

---

# 16. Hủy nhiều Task

```python
tasks = [

    asyncio.create_task(work1()),

    asyncio.create_task(work2()),

    asyncio.create_task(work3())

]
```

Hủy:

```python
for task in tasks:
    task.cancel()
```

Sau đó:

```python
await asyncio.gather(
    *tasks,
    return_exceptions=True
)
```

Đây là mẫu rất phổ biến khi tắt ứng dụng.

---

# 17. Kiểm tra trạng thái

```python
print(task.done())

print(task.cancelled())

print(task.exception())

print(task.result())
```

Đây là bốn API quan trọng nhất để theo dõi một Task.

---

# 18. Sai lầm phổ biến

## Sai lầm 1

```python
task.cancel()
```

↓

Nghĩ:

```text
Task chết ngay
```

Sai.

Task chỉ bị hủy khi nó có cơ hội xử lý yêu cầu hủy (thường tại một điểm `await`).

---

## Sai lầm 2

```python
print(task.result())
```

trước khi:

```text
Done
```

↓

Lỗi.

---

## Sai lầm 3

Không xử lý:

```text
CancelledError
```

↓

Không cleanup.

---

## Sai lầm 4

Không `await` Task sau khi `cancel()`.

Ví dụ:

```python
task.cancel()
```

rồi kết thúc chương trình.

Có thể:

* coroutine chưa cleanup
* exception chưa được xử lý đầy đủ

Thực tế nên:

```python
task.cancel()

try:
    await task
except asyncio.CancelledError:
    pass
```

---

# 19. Ví dụ thực tế

Background Worker:

```text
Server

↓

Background Sync

↓

Đọc Queue

↓

Gửi Email

↓

Task
```

Khi Server tắt:

```text
cancel()

↓

Cleanup

↓

Đóng DB

↓

Đóng Redis

↓

Finish
```

Đây là lý do `cancel()` rất quan trọng trong các ứng dụng chạy lâu.

---

# 20. Tổng kết

Một Task thường trải qua:

```text
Created

↓

Pending

↓

Running

↓

Waiting

↓

Running

↓

Done
```

Hoặc:

```text
Running

↓

cancel()

↓

CancelledError

↓

Done
```

Các API cần nhớ:

| API           | Ý nghĩa                                   |
| ------------- | ----------------------------------------- |
| `done()`      | Task đã kết thúc chưa                     |
| `result()`    | Lấy kết quả sau khi hoàn thành            |
| `exception()` | Lấy exception nếu Task lỗi                |
| `cancel()`    | Yêu cầu hủy Task                          |
| `cancelled()` | Kiểm tra Task có kết thúc do bị hủy không |

---

# Sơ đồ tư duy

```text
              Task

                │

          create_task()

                │

             Pending

                │

             Running

      ┌─────────┴─────────┐

      ▼                   ▼

   Completed          cancel()

      │                   │

      ▼                   ▼

  result()         CancelledError

      │                   │

      └─────────┬─────────┘

                ▼

               Done
```

---

# Bài tập thực hành

## Bài 1

Viết một coroutine:

```python
async def worker():
```

* chạy 10 giây (`asyncio.sleep(10)`)
* sau 2 giây hãy gọi `cancel()`
* bắt `CancelledError`
* in:

```text
Cleaning resources...
```

---

## Bài 2

Viết một Task trả về:

```python
return 999
```

Sau khi hoàn thành:

* kiểm tra `done()`
* in `result()`

---

## Bài 3

Viết một Task:

```python
raise RuntimeError("Network Error")
```

Sau khi kết thúc:

* dùng `exception()`
* in exception

---

## Bài 4 (Nâng cao)

Viết chương trình tạo **5 Task** chạy vòng lặp vô hạn:

```python
while True:
    await asyncio.sleep(1)
```

Sau 5 giây:

* hủy toàn bộ Task.
* đảm bảo mỗi Task đều in:

```text
Cleanup...
```

* sau đó chương trình kết thúc gọn gàng, không còn Task chạy nền.

---

# Chuẩn bị cho Buổi 12

Buổi tiếp theo chúng ta sẽ học một chủ đề rất quan trọng trong Python hiện đại:

# **Structured Concurrency với `asyncio.TaskGroup` (Python 3.11+)**

Bạn sẽ học:

* Vì sao `TaskGroup` ra đời.
* `TaskGroup` khác `gather()` như thế nào.
* Quản lý nhóm Task an toàn.
* Cơ chế tự động hủy các Task còn lại khi có lỗi.
* `ExceptionGroup` và xử lý nhiều ngoại lệ cùng lúc.
* Thực hành xây dựng các tác vụ đồng thời theo phong cách hiện đại.

Đây là hướng lập trình được khuyến nghị cho các dự án Python mới từ phiên bản **3.11 trở lên** và đang dần thay thế nhiều trường hợp sử dụng `asyncio.gather()`.
