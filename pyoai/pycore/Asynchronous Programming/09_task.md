# Python Asynchronous Programming - Buổi 9

# Task - Đơn vị thực thi của Event Loop

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ hiểu:
>
> * Task là gì.
> * Coroutine và Task khác nhau như thế nào.
> * Vì sao chỉ `await` chưa tạo ra chạy đồng thời.
> * `asyncio.create_task()` hoạt động ra sao.
> * Vòng đời của một Task.
> * Khi nào nên dùng Task.

> ⭐ Đây là một trong những buổi quan trọng nhất của cả khóa học. Từ đây trở đi, hầu hết chương trình `asyncio` thực tế đều sử dụng **Task**.

---

# 1. Ôn lại Coroutine

Chúng ta đã biết:

```python
async def download():
    print("Downloading...")
```

Khi gọi:

```python
coro = download()
```

Điều nhận được là:

```text
Coroutine Object
```

Không chạy.

Muốn chạy:

```python
await coro
```

hoặc

```python
asyncio.run(coro)
```

---

# 2. Vấn đề của `await`

Ví dụ:

```python
import asyncio

async def task1():
    print("Task 1 Start")
    await asyncio.sleep(2)
    print("Task 1 End")

async def task2():
    print("Task 2 Start")
    await asyncio.sleep(1)
    print("Task 2 End")

async def main():
    await task1()
    await task2()

asyncio.run(main())
```

Bạn nghĩ hai task chạy cùng lúc?

Không.

Timeline:

```text
Task1 Start

↓

sleep 2s

↓

Task1 End

↓

Task2 Start

↓

sleep 1s

↓

Task2 End
```

Tổng thời gian:

```text
3 giây
```

---

# 3. Vì sao?

Nhìn vào đoạn này:

```python
await task1()

await task2()
```

Ý nghĩa:

```text
Đợi task1 xong

↓

Mới chạy task2
```

Đây vẫn là thực thi tuần tự.

---

# 4. Muốn chạy đồng thời thì sao?

Ta cần:

```python
asyncio.create_task()
```

Đây là nơi **Task** xuất hiện.

---

# 5. Task là gì?

Định nghĩa:

> **Task là một Coroutine đã được đăng ký với Event Loop để được lập lịch thực thi.**

Hay nói đơn giản:

```text
Coroutine

↓

create_task()

↓

Task

↓

Event Loop quản lý
```

---

# 6. Ví dụ đầu tiên

```python
import asyncio

async def hello():
    print("Hello")

async def main():
    task = asyncio.create_task(hello())

    await task

asyncio.run(main())
```

Quá trình:

```text
hello()

↓

Coroutine

↓

create_task()

↓

Task

↓

Ready Queue

↓

Running
```

---

# 7. Task khác Coroutine như thế nào?

Đây là câu hỏi quan trọng nhất của buổi học.

## Coroutine

```python
coro = hello()
```

Chỉ tạo object.

Event Loop chưa biết đến nó.

---

## Task

```python
task = asyncio.create_task(hello())
```

Event Loop:

```text
Đã biết

↓

Đưa vào Ready Queue

↓

Sẽ tự chạy khi đến lượt
```

---

# 8. Hình dung trực quan

Coroutine giống như:

```text
Đơn xin việc
```

Bạn mới viết xong.

Chưa ai xử lý.

---

Task giống như:

```text
Đơn xin việc

↓

Nộp cho phòng nhân sự

↓

Đã được đưa vào danh sách xử lý
```

Event Loop chính là "phòng nhân sự".

---

# 9. Ví dụ chạy đồng thời

```python
import asyncio

async def task1():
    print("Task1 Start")
    await asyncio.sleep(2)
    print("Task1 End")

async def task2():
    print("Task2 Start")
    await asyncio.sleep(1)
    print("Task2 End")

async def main():

    t1 = asyncio.create_task(task1())

    t2 = asyncio.create_task(task2())

    await t1
    await t2

asyncio.run(main())
```

Timeline:

```text
0s

Task1 Start

Task2 Start

↓

Task2 ngủ

↓

Task1 ngủ

↓

1s

Task2 End

↓

2s

Task1 End
```

Tổng:

```text
2 giây
```

---

# 10. Điều gì xảy ra bên trong?

```python
t1 = asyncio.create_task(task1())
```

Python làm:

```text
task1()

↓

Coroutine

↓

Task

↓

Ready Queue
```

Ngay sau đó:

```python
t2 = asyncio.create_task(task2())
```

```text
task2()

↓

Coroutine

↓

Task

↓

Ready Queue
```

Ready Queue:

```text
Task1

Task2
```

Event Loop tự lập lịch cho cả hai.

---

# 11. `await task` có chặn Task khác không?

Ví dụ:

```python
t1 = asyncio.create_task(task1())
t2 = asyncio.create_task(task2())

await t1
```

Nhiều người nghĩ:

```text
Task2 đứng yên
```

Sai.

Trong lúc `main()` đang đợi `t1`, nếu `t2` đã sẵn sàng chạy thì Event Loop vẫn tiếp tục chạy `t2`.

`await t1` chỉ làm coroutine hiện tại (`main`) tạm dừng, không dừng cả Event Loop.

---

# 12. Task có trạng thái

Một Task thường trải qua các trạng thái:

```text
Created

↓

Scheduled

↓

Running

↓

Waiting

↓

Running

↓

Done
```

Giải thích:

### Created

Đã tạo.

---

### Scheduled

Đã đưa vào Ready Queue.

---

### Running

Đang chạy.

---

### Waiting

Gặp:

```python
await ...
```

---

### Done

Hoàn thành.

---

# 13. Task trả về kết quả

Ví dụ:

```python
import asyncio

async def add():
    return 100

async def main():

    task = asyncio.create_task(add())

    result = await task

    print(result)

asyncio.run(main())
```

Kết quả:

```text
100
```

Task cũng có thể trả về giá trị như coroutine.

---

# 14. Task có Exception

```python
async def work():
    raise ValueError("Error")
```

Nếu:

```python
task = asyncio.create_task(work())
```

Khi:

```python
await task
```

Exception sẽ được phát sinh tại điểm `await`, trừ khi bạn xử lý trước.

---

# 15. Task và Event Loop

```text
Coroutine

↓

Task

↓

Ready Queue

↓

Running

↓

await

↓

Timer Queue

↓

Ready Queue

↓

Running

↓

Done
```

Task chính là đơn vị mà Event Loop quản lý.

---

# 16. Sai lầm phổ biến

## Sai lầm 1

Nghĩ rằng:

```python
hello()
```

đã tạo Task.

Sai.

Chỉ tạo Coroutine.

---

## Sai lầm 2

Nghĩ rằng:

```python
await hello()
```

là Task.

Sai.

Đây chỉ là:

```text
Main Coroutine

↓

Đợi Coroutine khác
```

Không nhất thiết tạo Task riêng.

---

## Sai lầm 3

Nghĩ rằng:

Task = Thread.

Sai.

Task:

```text
Event Loop quản lý
```

Thread:

```text
OS quản lý
```

---

# 17. Coroutine vs Task

| Coroutine                    | Task                                              |
| ---------------------------- | ------------------------------------------------- |
| Chỉ là đối tượng coroutine   | Coroutine đã được Event Loop lập lịch             |
| Chưa tự chạy                 | Có thể được Event Loop chạy                       |
| Không có trạng thái lập lịch | Có trạng thái (`Pending`, `Running`, `Done`, ...) |
| Không nằm trong Ready Queue  | Có thể nằm trong Ready Queue                      |

---

# 18. Khi nào dùng Task?

Dùng Task khi:

✔ Download nhiều file.

✔ Gọi nhiều API.

✔ WebSocket.

✔ Chat Server.

✔ Background Job.

✔ GUI chạy nền.

✔ Thực hiện nhiều thao tác I/O đồng thời.

---

# 19. Khi nào không cần Task?

Ví dụ:

```python
async def get_name():
    return "Alice"

async def main():
    name = await get_name()
    print(name)
```

Ở đây chỉ có một luồng công việc đơn giản.

Không cần:

```python
asyncio.create_task()
```

---

# 20. Tổng kết

Điều quan trọng nhất của buổi học:

```text
Coroutine

↓

create_task()

↓

Task

↓

Event Loop

↓

Running
```

Hãy ghi nhớ:

> **Coroutine mô tả công việc. Task là công việc đã được Event Loop nhận và quản lý.**

---

# Sơ đồ tư duy

```text
async def
      │
      ▼
Coroutine Object
      │
create_task()
      ▼
     Task
      │
      ▼
Ready Queue
      │
      ▼
Running
      │
    await
      │
      ▼
Waiting
      │
      ▼
Running
      │
      ▼
Done
```

---

# Bài tập thực hành

## Bài 1

Viết hai coroutine:

```python
async def download():
    ...

async def upload():
    ...
```

Thực hiện:

* Chạy tuần tự bằng `await`.
* Sau đó chuyển sang `create_task()`.

Đo thời gian và so sánh.

---

## Bài 2

Viết ba Task:

* A ngủ 3 giây.
* B ngủ 1 giây.
* C ngủ 2 giây.

Dự đoán:

* Task nào kết thúc trước?
* Task nào kết thúc sau?

Giải thích bằng Timeline.

---

## Bài 3

Viết một coroutine:

```python
async def square(x):
    return x * x
```

Tạo Task cho `square(10)` và in kết quả.

---

## Bài 4 (Nâng cao)

Giải thích bằng lời:

Tại sao đoạn mã:

```python
await task1()
await task2()
```

không tạo ra sự chạy đồng thời, nhưng:

```python
t1 = asyncio.create_task(task1())
t2 = asyncio.create_task(task2())

await t1
await t2
```

lại cho phép cả hai tiến triển đồng thời trên cùng một Event Loop.

---

# Chuẩn bị cho Buổi 10

Ở buổi tiếp theo, chúng ta sẽ học **`asyncio.gather()`**, một trong những API được sử dụng nhiều nhất trong `asyncio`.

Bạn sẽ hiểu:

* `gather()` hoạt động như thế nào.
* Khác gì với `create_task()`.
* Chạy hàng chục hoặc hàng trăm coroutine cùng lúc.
* Thu thập kết quả theo đúng thứ tự.
* Xử lý exception trong `gather()`.
* Những lỗi thường gặp khi dùng `gather()`.

Đây là bước đầu tiên để xây dựng các chương trình tải dữ liệu, crawler và API client bất đồng bộ hiệu quả.
