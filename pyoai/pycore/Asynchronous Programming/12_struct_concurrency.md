# Python Asynchronous Programming - Buổi 12

# Structured Concurrency với `asyncio.TaskGroup` (Python 3.11+)

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ hiểu:
>
> * Structured Concurrency là gì.
> * Vì sao `TaskGroup` được bổ sung vào Python 3.11.
> * `TaskGroup` khác gì với `gather()`.
> * Cách sử dụng `async with asyncio.TaskGroup()`.
> * Cách xử lý lỗi trong `TaskGroup`.
> * `ExceptionGroup` là gì.
> * Khi nào nên dùng `TaskGroup`.

> ⭐ Đây là một trong những thay đổi lớn nhất của `asyncio` kể từ Python 3.11 và là cách được khuyến nghị để quản lý nhiều task có cùng vòng đời.

---

# 1. Vấn đề của `create_task()`

Ví dụ:

```python
import asyncio

async def worker(name):
    await asyncio.sleep(2)
    print(name)

async def main():
    asyncio.create_task(worker("A"))
    asyncio.create_task(worker("B"))

    print("Main End")

asyncio.run(main())
```

Điều gì xảy ra?

Có thể:

```text
Main End
```

rồi chương trình kết thúc.

Hai Task:

```text
A

B
```

chưa chắc đã chạy xong.

Vì:

```text
Main()

↓

Kết thúc

↓

Event Loop đóng
```

Các Task bị hủy.

---

# 2. Vấn đề lớn hơn

Giả sử:

```python
asyncio.create_task(download())

asyncio.create_task(upload())

asyncio.create_task(save_database())
```

Một Task bị lỗi.

Hai Task còn lại?

Ai chịu trách nhiệm hủy?

Ai cleanup?

Ai chờ tất cả kết thúc?

Nếu dùng `create_task()` đơn lẻ, bạn phải tự quản lý.

---

# 3. Structured Concurrency

Đây là một triết lý lập trình.

Ý tưởng:

> **Task phải sống bên trong một phạm vi (scope) rõ ràng.**

Ví dụ:

```text
Main

│

├── Task A

├── Task B

└── Task C
```

Khi:

```text
Main kết thúc
```

↓

Toàn bộ Task:

* hoàn thành
* hoặc bị hủy

Không để "Task mồ côi" (orphan task).

---

# 4. TaskGroup

Python 3.11 giới thiệu:

```python
asyncio.TaskGroup
```

Ví dụ:

```python
import asyncio

async def worker(name):

    await asyncio.sleep(2)

    print(name)

async def main():

    async with asyncio.TaskGroup() as tg:

        tg.create_task(worker("A"))

        tg.create_task(worker("B"))

    print("Done")

asyncio.run(main())
```

Kết quả:

```text
A

B

Done
```

`Done` chỉ được in sau khi tất cả Task trong nhóm đã hoàn thành.

---

# 5. `async with`

Đây là điểm khác biệt.

```python
async with asyncio.TaskGroup() as tg:
```

Có nghĩa:

```text
Vào Block

↓

Tạo Task

↓

Đợi tất cả Task

↓

Thoát Block
```

Không cần:

```python
await task
```

cho từng Task.

---

# 6. Timeline

```text
TaskGroup

↓

Task A

↓

Task B

↓

Task C

↓

Đợi tất cả

↓

Exit
```

Rất giống:

```python
with open(...)
```

nhưng dành cho Async.

---

# 7. `create_task()` trong TaskGroup

Lưu ý:

```python
tg.create_task(...)
```

khác:

```python
asyncio.create_task(...)
```

Task được tạo sẽ thuộc về TaskGroup.

---

# 8. Ví dụ thực tế

```python
import asyncio

async def download():
    await asyncio.sleep(2)
    print("Download")

async def upload():
    await asyncio.sleep(1)
    print("Upload")

async def process():
    await asyncio.sleep(3)
    print("Process")

async def main():

    async with asyncio.TaskGroup() as tg:

        tg.create_task(download())

        tg.create_task(upload())

        tg.create_task(process())

asyncio.run(main())
```

Timeline:

```text
0s

Download

Upload

Process

↓

1s

Upload Done

↓

2s

Download Done

↓

3s

Process Done

↓

Exit TaskGroup
```

---

# 9. Điều gì xảy ra nếu có lỗi?

Đây là ưu điểm lớn nhất.

Ví dụ:

```python
async def bad():

    await asyncio.sleep(1)

    raise RuntimeError("Boom")
```

Task khác:

```python
async def worker():

    await asyncio.sleep(10)
```

Nếu:

```text
bad()

↓

Boom
```

TaskGroup sẽ:

```text
Cancel

↓

Worker

↓

Cleanup

↓

Thoát
```

Không để Task chạy tiếp.

---

# 10. So sánh với `gather()`

`gather()`:

```text
Task A

Task B

Task C
```

Nếu một Task lỗi:

* có thể phát sinh exception.
* việc xử lý các Task còn lại phụ thuộc vào cách bạn sử dụng `gather()` và cấu hình của nó (`return_exceptions=True` hay không).

TaskGroup:

```text
Một Task lỗi

↓

Hủy toàn bộ Task còn lại

↓

Đợi Cleanup

↓

Thoát
```

Đây là lý do TaskGroup được gọi là **Structured Concurrency**.

---

# 11. ExceptionGroup

Nếu nhiều Task cùng lỗi.

Python không chỉ trả:

```text
ValueError
```

Mà:

```text
ExceptionGroup
```

Bên trong chứa:

```text
Task1

↓

ValueError

Task2

↓

RuntimeError

Task3

↓

TimeoutError
```

Một nhóm exception.

---

# 12. Ví dụ

```python
import asyncio

async def a():
    raise ValueError()

async def b():
    raise RuntimeError()

async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(a())
        tg.create_task(b())

try:
    asyncio.run(main())
except* Exception as eg:
    print(eg)
```

Đây là cú pháp mới của Python 3.11:

```python
except* Exception
```

để xử lý `ExceptionGroup`.

---

# 13. Cleanup

Ví dụ:

```python
async def worker():

    try:

        while True:

            await asyncio.sleep(1)

    except asyncio.CancelledError:

        print("Cleanup")

        raise
```

Nếu TaskGroup hủy:

```text
Cleanup
```

sẽ được gọi.

Điều này giúp đóng:

* Database
* File
* Socket
* WebSocket

an toàn.

---

# 14. Lấy kết quả từ TaskGroup

`TaskGroup.create_task()` trả về một đối tượng `Task`.

Bạn có thể giữ lại:

```python
import asyncio

async def square(x):
    return x * x

async def main():
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(square(2))
        t2 = tg.create_task(square(3))

    print(t1.result())
    print(t2.result())

asyncio.run(main())
```

Kết quả:

```text
4

9
```

Sau khi ra khỏi `TaskGroup`, các task đã hoàn thành nên có thể gọi `result()`.

---

# 15. Khi nào dùng TaskGroup?

Rất phù hợp:

* Gọi nhiều API.
* Download nhiều file.
* Upload nhiều file.
* Đồng bộ dữ liệu.
* Worker song song.
* Xử lý nhiều nguồn dữ liệu độc lập.

Miễn là:

```text
Các Task

↓

Có cùng vòng đời
```

---

# 16. Khi nào chưa phù hợp?

Ví dụ:

```text
Task A

↓

Tạo Task B

↓

Task B

↓

Tạo Task C
```

Quan hệ quá phức tạp.

Lúc này:

* TaskGroup vẫn dùng được ở nhiều trường hợp.
* Nhưng đôi khi cần kết hợp thêm các kỹ thuật khác như `Queue`, `Semaphore`, hoặc các TaskGroup lồng nhau.

---

# 17. So sánh

| Đặc điểm                        | `create_task()`  | `gather()`           | `TaskGroup`         |
| ------------------------------- | ---------------- | -------------------- | ------------------- |
| Chạy đồng thời                  | ✅                | ✅                    | ✅                   |
| Thu kết quả                     | Qua `await task` | ✅                    | Qua `Task.result()` |
| Tự quản lý Task                 | ❌                | Một phần             | ✅                   |
| Structured Concurrency          | ❌                | ❌                    | ✅                   |
| Tự hủy Task còn lại khi lỗi     | ❌                | Không mặc định       | ✅                   |
| Khuyến nghị cho mã Python 3.11+ | ⚠️               | ✅ (nhiều trường hợp) | ⭐ Có                |

---

# 18. Sai lầm phổ biến

## Sai lầm 1

Nghĩ:

```text
TaskGroup

=

gather()
```

Sai.

TaskGroup quản lý **vòng đời của Task**, không chỉ chạy đồng thời.

---

## Sai lầm 2

Quên:

```python
async with
```

TaskGroup chỉ hoạt động trong phạm vi (`scope`) của nó.

---

## Sai lầm 3

Không xử lý:

```python
CancelledError
```

Khi TaskGroup hủy Task.

---

# 19. Tổng kết

Điều quan trọng nhất:

```text
TaskGroup

↓

Task A

Task B

Task C

↓

Một Task lỗi

↓

Cancel tất cả

↓

Cleanup

↓

Exit
```

Hãy ghi nhớ:

> **TaskGroup không chỉ giúp chạy nhiều Task mà còn đảm bảo tất cả Task được quản lý như một đơn vị thống nhất.**

---

# Sơ đồ tư duy

```text
              TaskGroup

                   │

          async with Block

                   │

      ┌────────────┼────────────┐

      ▼            ▼            ▼

    Task A       Task B       Task C

      │            │            │

      └────────────┼────────────┘

                   ▼

          Chờ tất cả hoàn thành

                   ▼

          Hoặc hủy tất cả nếu có lỗi

                   ▼

                 Exit
```

---

# Bài tập thực hành

## Bài 1

Viết ba coroutine:

```python
download()
upload()
process()
```

Sử dụng:

```python
async with asyncio.TaskGroup()
```

để chạy đồng thời.

---

## Bài 2

Viết:

```python
square(x)
```

Tạo 5 Task trong TaskGroup.

Sau khi ra khỏi block:

In toàn bộ kết quả bằng:

```python
task.result()
```

---

## Bài 3

Viết:

```python
worker()
```

chạy:

```python
while True:
    await asyncio.sleep(1)
```

và:

```python
bad()
```

ném:

```python
RuntimeError()
```

Quan sát:

* worker có bị hủy không?
* `Cleanup` có được gọi không?

---

## Bài 4 (Nâng cao)

Thiết kế một chương trình mô phỏng hệ thống xử lý đơn hàng:

* Task 1: Kiểm tra tồn kho.
* Task 2: Tính phí vận chuyển.
* Task 3: Tính điểm thưởng khách hàng.

Yêu cầu:

* Chạy cả ba bằng `TaskGroup`.
* Nếu bất kỳ Task nào gặp lỗi (ví dụ kiểm tra tồn kho thất bại), toàn bộ nhóm phải dừng và các Task còn lại được hủy an toàn.

---

# Chuẩn bị cho Buổi 13

Ở buổi tiếp theo, chúng ta sẽ đi vào một chủ đề rất quan trọng trong các ứng dụng thực tế:

# **Timeout, Deadline và Cancellation nâng cao**

Bạn sẽ học:

* `asyncio.wait_for()`.
* `asyncio.timeout()` (Python 3.11+).
* Thiết lập thời gian chờ cho coroutine.
* Timeout lồng nhau.
* Sự khác nhau giữa `TimeoutError` và `CancelledError`.
* Thiết kế các hệ thống có khả năng tự hủy tác vụ khi quá thời gian.

Đây là nền tảng để xây dựng các ứng dụng mạng, API client, crawler và dịch vụ nền có khả năng xử lý các thao tác chậm hoặc bị treo một cách an toàn và hiệu quả.
