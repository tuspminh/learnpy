# Python Asynchronous Programming - Buổi 5

# `await` - Trái tim của Asyncio

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ hiểu:
>
> * `await` thực sự làm gì.
> * Vì sao `await` không phải là "đợi" theo nghĩa thông thường.
> * `await` và `time.sleep()` khác nhau như thế nào.
> * Event Loop chuyển đổi Coroutine ra sao.
> * Vì sao `await` giúp một chương trình có thể xử lý hàng nghìn kết nối cùng lúc.

---

# 1. `await` là gì?

Đây là từ khóa quan trọng nhất của `asyncio`.

Nhiều người nghĩ:

> `await` = đợi.

Đúng nhưng **chưa đủ**.

Định nghĩa đầy đủ:

> **`await` tạm dừng Coroutine hiện tại và trả quyền điều khiển lại cho Event Loop để Event Loop có thể chạy Coroutine khác.**

Đây là điều quan trọng nhất của cả khóa học.

---

# 2. Ví dụ đầu tiên

```python
import asyncio

async def hello():
    print("A")
    await asyncio.sleep(2)
    print("B")

asyncio.run(hello())
```

Kết quả

```
A

(chờ 2 giây)

B
```

Có vẻ giống:

```python
import time

print("A")
time.sleep(2)
print("B")
```

Nhưng bên trong hoàn toàn khác.

---

# 3. `time.sleep()`

Giả sử:

```python
import time

print("A")
time.sleep(5)
print("B")
```

Timeline

```
Python

↓

A

↓

Sleep

↓

CPU chờ

↓

CPU chờ

↓

CPU chờ

↓

B
```

Trong lúc đó

Không làm được gì khác.

Đây là **Blocking**.

---

# 4. `await asyncio.sleep()`

```python
import asyncio

async def work():
    print("A")
    await asyncio.sleep(5)
    print("B")
```

Timeline

```
Coroutine

↓

A

↓

await

↓

Pause

↓

Event Loop

↓

Coroutine khác

↓

...

↓

Quay lại

↓

B
```

Khác biệt cực lớn:

Coroutine chỉ **tạm dừng**.

Toàn bộ chương trình **không bị dừng**.

---

# 5. Một ví dụ trực quan

Có hai Coroutine.

```python
import asyncio

async def task1():
    print("Task1 Start")
    await asyncio.sleep(3)
    print("Task1 End")

async def task2():
    print("Task2 Start")
    await asyncio.sleep(1)
    print("Task2 End")
```

Nếu Event Loop chạy cả hai:

Timeline

```
0s

Task1 Start

Task2 Start

↓

Task2 sleep

↓

Task1 sleep

↓

1s

Task2 End

↓

3s

Task1 End
```

Trong lúc Task1 ngủ,

Task2 vẫn chạy.

---

# 6. `await` không phải Sleep

Đây là hiểu lầm phổ biến.

`await` không phải là:

```
Dừng chương trình
```

Mà là:

```
Nhường quyền điều khiển
```

Nghĩa là:

```
Coroutine A

↓

await

↓

Event Loop

↓

Coroutine B

↓

Coroutine C

↓

Coroutine D

↓

Quay lại A
```

---

# 7. Ví dụ đời sống

Bạn đi nhà hàng.

## Blocking

```
Gọi món

↓

Đứng nhìn đầu bếp

↓

Đứng nhìn

↓

Đứng nhìn

↓

Có món
```

Bạn chẳng làm gì.

---

## Async

```
Gọi món

↓

Lấy số

↓

Đi uống nước

↓

Đọc báo

↓

Có chuông

↓

Lấy món
```

`await` giống như:

```
"Tôi chưa có việc gì làm,
hãy gọi người khác trước."
```

---

# 8. Event Loop làm gì?

Giả sử có:

```
Task A

Task B

Task C
```

Task A

```
A1

↓

await
```

Event Loop

```
↓

Task B
```

Task B

```
B1

↓

await
```

Event Loop

```
↓

Task C
```

Task C

```
C1

↓

await
```

Event Loop

```
↓

Quay lại Task A
```

Đó chính là **Scheduling**.

---

# 9. `await` chờ cái gì?

Có thể chờ:

* Coroutine
* Task
* Future
* Một số đối tượng "awaitable"

Ví dụ

```python
await another_coroutine()

await task

await future

await asyncio.sleep(1)
```

Không phải mọi đối tượng đều có thể `await`.

Ví dụ:

```python
await 123
```

Lỗi.

Hoặc:

```python
await "Hello"
```

Cũng lỗi.

---

# 10. await Coroutine

```python
import asyncio

async def hello():
    print("Hello")

async def main():
    await hello()

asyncio.run(main())
```

Timeline

```
main()

↓

await hello()

↓

hello()

↓

Return

↓

main()
```

---

# 11. await lồng nhau

```python
import asyncio

async def c():
    print("C")

async def b():
    print("B")
    await c()

async def a():
    print("A")
    await b()

asyncio.run(a())
```

Kết quả

```
A
B
C
```

Sơ đồ

```
a()

↓

await

↓

b()

↓

await

↓

c()
```

---

# 12. await không tạo Thread

Đây là điểm cực kỳ quan trọng.

Nhiều người nghĩ:

```
await

↓

Thread mới
```

Sai.

Thực tế

```
Process

↓

Main Thread

↓

Event Loop

↓

Coroutine
```

Chỉ có:

Một Thread.

---

# 13. Điều gì xảy ra khi gặp await?

Ví dụ

```python
await asyncio.sleep(2)
```

Python làm:

```
Coroutine

↓

Lưu trạng thái

↓

Pause

↓

Trả quyền

↓

Event Loop

↓

Chạy Coroutine khác

↓

2 giây

↓

Resume
```

Coroutine ghi nhớ chính xác vị trí đang thực thi để có thể tiếp tục sau này.

---

# 14. Nếu không có await?

Ví dụ

```python
async def work():

    while True:
        pass
```

Điều gì xảy ra?

```
Coroutine

↓

CPU

↓

CPU

↓

CPU

↓

CPU

↓

Không bao giờ nhường quyền
```

Event Loop bị "chiếm dụng".

Mọi Coroutine khác đều đứng yên.

---

# 15. await khác return

Đừng nhầm.

`return`

```
Hàm kết thúc
```

`await`

```
Coroutine tạm dừng
```

Ví dụ

```python
await something()
```

Sau khi hoàn thành,

Coroutine vẫn tiếp tục chạy.

---

# 16. Sai lầm phổ biến

## Sai lầm 1

```python
await time.sleep(1)
```

Sai.

`time.sleep()` không phải đối tượng có thể `await`.

Đúng:

```python
await asyncio.sleep(1)
```

---

## Sai lầm 2

```python
time.sleep(5)
```

đặt trong Coroutine.

Ví dụ

```python
async def work():
    time.sleep(5)
```

Điều này sẽ **chặn toàn bộ Event Loop** trong 5 giây.

Đây là một lỗi rất phổ biến khi mới học.

---

## Sai lầm 3

Nghĩ rằng:

```
await

=

Thread
```

Sai.

Không hề tạo Thread.

---

# 17. So sánh `time.sleep()` và `asyncio.sleep()`

| `time.sleep()`       | `await asyncio.sleep()`        |
| -------------------- | ------------------------------ |
| Blocking             | Non-blocking                   |
| Dừng Thread          | Chỉ tạm dừng Coroutine         |
| Chặn Event Loop      | Không chặn Event Loop          |
| Không chạy việc khác | Event Loop chạy Coroutine khác |

---

# 18. Mô hình hoạt động

```
Coroutine A

↓

await

↓

Pause

↓

Event Loop

↓

Coroutine B

↓

await

↓

Coroutine C

↓

Resume A

↓

Resume B

↓

Resume C
```

---

# 19. Tổng kết

Điều quan trọng nhất cần nhớ:

## `await` không phải là "đứng đợi"

Mà là:

> **"Tôi tạm dừng ở đây, Event Loop hãy chạy công việc khác trước."**

Đó chính là bí mật giúp Async xử lý hàng nghìn kết nối mà vẫn chỉ cần một Thread.

---

# Sơ đồ tư duy

```
                 await
                    │
                    ▼
         Tạm dừng Coroutine
                    │
                    ▼
        Trả quyền cho Event Loop
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   Coroutine B  Coroutine C  Coroutine D
        │
        ▼
  Quay lại Coroutine A
```

---

# Bài tập thực hành

## Bài 1

Chạy chương trình:

```python
import asyncio

async def hello():
    print("Start")
    await asyncio.sleep(2)
    print("End")

asyncio.run(hello())
```

Giải thích từng bước chương trình thực hiện.

---

## Bài 2

Thay:

```python
await asyncio.sleep(2)
```

bằng:

```python
import time
time.sleep(2)
```

Quan sát sự khác biệt và giải thích vì sao `time.sleep()` không phù hợp trong coroutine.

---

## Bài 3

Viết ba coroutine:

```python
async def a():
    ...

async def b():
    ...

async def c():
    ...
```

Trong đó:

* `a()` gọi `await b()`
* `b()` gọi `await c()`

Vẽ sơ đồ lời gọi hàm và giải thích luồng thực thi.

---

## Bài 4 (Tư duy)

Giả sử có 1.000 coroutine đều gọi:

```python
await asyncio.sleep(5)
```

Hãy trả lời:

1. Có tạo 1.000 Thread không?
2. CPU có bận trong 5 giây đó không?
3. Event Loop đang làm gì trong khoảng thời gian này?

Nếu trả lời được ba câu hỏi này, bạn đã nắm được bản chất của `await`.

---

# Chuẩn bị cho Buổi 6

Buổi tiếp theo là một trong những buổi quan trọng nhất của khóa học:

> **Event Loop Deep Dive**

Chúng ta sẽ không chỉ biết Event Loop là gì mà còn mô phỏng cách nó hoạt động từng bước:

* Event Loop là gì và được tạo khi nào.
* Hàng đợi (ready queue) hoạt động ra sao.
* Coroutine được lập lịch như thế nào.
* Khi gặp `await`, Event Loop lưu trạng thái ở đâu.
* Vì sao chỉ với một Thread, Event Loop vẫn có thể quản lý hàng chục nghìn coroutine.

Sau buổi này, bạn sẽ hiểu cơ chế cốt lõi của `asyncio`, không chỉ biết cách sử dụng.
