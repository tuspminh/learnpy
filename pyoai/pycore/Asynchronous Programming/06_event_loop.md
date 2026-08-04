# Python Asynchronous Programming - Buổi 6

# Event Loop Deep Dive (Phần 1) - Trái tim của `asyncio`

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ hiểu:
>
> * Event Loop là gì.
> * Vì sao `asyncio` cần Event Loop.
> * Event Loop hoạt động như thế nào.
> * Coroutine được Event Loop quản lý ra sao.
> * Ready Queue là gì.
> * Scheduler hoạt động như thế nào.

> **Đây là buổi quan trọng nhất từ đầu khóa học.** Nếu hiểu Event Loop, bạn sẽ hiểu gần như toàn bộ `asyncio`.

---

# 1. Vì sao cần Event Loop?

Giả sử bạn có 3 coroutine:

```python
async def download():
    ...

async def save():
    ...

async def upload():
    ...
```

Chúng đều được tạo ra.

Câu hỏi:

> **Ai quyết định coroutine nào chạy trước?**

Không phải Python interpreter.

Không phải CPU.

Không phải hệ điều hành (OS).

Mà là:

```text
Event Loop
```

---

# 2. Event Loop là gì?

Định nghĩa:

> **Event Loop là một bộ lập lịch (Scheduler) chạy liên tục, có nhiệm vụ quản lý, tạm dừng và tiếp tục các coroutine.**

Bạn có thể hình dung Event Loop như một **quản lý công việc**.

Ví dụ:

```text
Nhân viên A

Nhân viên B

Nhân viên C

↓

Quản lý

↓

Ai rảnh thì giao việc tiếp
```

Trong `asyncio`, Event Loop chính là người quản lý đó.

---

# 3. Event Loop chạy ở đâu?

Một hiểu lầm phổ biến:

> Event Loop là một Thread riêng.

❌ Sai.

Thực tế:

```text
Process
    │
    └── Main Thread
            │
            ├── Python Interpreter
            └── Event Loop
```

Event Loop **thường chạy ngay trong Main Thread**.

Nó không tự tạo Thread mới.

---

# 4. Event Loop làm việc gì?

Nó lặp liên tục:

```text
while True:

    Có coroutine sẵn sàng chạy?

        Có

            Chạy

        Không

            Chờ sự kiện mới
```

Tên gọi **Event Loop** xuất phát từ vòng lặp vô tận này.

---

# 5. `asyncio.run()` làm gì?

Khi viết:

```python
import asyncio

async def main():
    print("Hello")

asyncio.run(main())
```

Nhiều người nghĩ:

```text
main()

↓

Hello
```

Thực tế bên trong:

```text
Tạo Event Loop

↓

Đưa main() vào Event Loop

↓

Chạy Event Loop

↓

Coroutine kết thúc

↓

Đóng Event Loop
```

Đây là lý do `asyncio.run()` thường chỉ nên gọi **một lần** ở điểm bắt đầu chương trình.

---

# 6. Event Loop giống như một công nhân điều phối

Giả sử có:

```text
Task A

Task B

Task C
```

Event Loop sẽ làm:

```text
A chạy

↓

A gặp await

↓

Chuyển sang B

↓

B gặp await

↓

Chuyển sang C

↓

C gặp await

↓

Quay lại A

↓

...

Lặp lại
```

Đây chính là **Cooperative Multitasking** (đa nhiệm hợp tác): mỗi coroutine **tự nguyện nhường quyền** khi gặp `await`.

---

# 7. Ready Queue là gì?

Event Loop có một danh sách:

```text
Ready Queue
```

Đây là nơi chứa:

> Những coroutine **đã sẵn sàng chạy**.

Ví dụ:

```text
Ready Queue

↓

Task A

Task B

Task C
```

Event Loop lấy lần lượt:

```text
Lấy A

↓

Chạy

↓

Lấy B

↓

Chạy

↓

Lấy C

↓

Chạy
```

---

# 8. Khi gặp `await`

Giả sử:

```python
async def download():

    print("Start")

    await asyncio.sleep(5)

    print("End")
```

Điều gì xảy ra?

```text
download()

↓

In "Start"

↓

Gặp await

↓

Lưu trạng thái

↓

Ra khỏi CPU

↓

Event Loop chạy coroutine khác
```

Quan trọng:

Coroutine **không biến mất**.

Nó chỉ bị **Suspend** (tạm dừng).

---

# 9. Suspend nghĩa là gì?

Giả sử coroutine đang chạy:

```python
async def test():

    a = 10

    b = 20

    await something()

    print(a + b)
```

Khi gặp:

```python
await something()
```

Python sẽ lưu:

* vị trí đang thực thi
* giá trị `a`
* giá trị `b`
* ngăn xếp (stack) liên quan đến coroutine

Để sau này tiếp tục:

```python
print(a + b)
```

Mà không cần chạy lại từ đầu.

---

# 10. Resume

Sau khi I/O hoàn thành:

Ví dụ:

```text
Server trả lời

↓

Database xong

↓

File đọc xong
```

Event Loop nhận được thông báo:

```text
Task A sẵn sàng
```

Nó đưa Task A trở lại:

```text
Ready Queue
```

Rồi tiếp tục:

```text
print("End")
```

---

# 11. Ví dụ mô phỏng

Có hai coroutine:

```python
async def A():

    print("A1")

    await asyncio.sleep(3)

    print("A2")
```

```python
async def B():

    print("B1")

    await asyncio.sleep(1)

    print("B2")
```

Timeline:

```text
0s

A1

↓

A ngủ

↓

B1

↓

B ngủ

↓

1s

B2

↓

3s

A2
```

Event Loop luôn chọn coroutine **đã sẵn sàng** để chạy.

---

# 12. Event Loop không chạy song song

Nhiều người nghĩ:

```text
A

B

C
```

đang chạy cùng lúc.

Không.

Thực tế:

```text
A

↓

B

↓

C

↓

A

↓

B

↓

C
```

Chuyển đổi rất nhanh nên ta có cảm giác đồng thời.

---

# 13. Event Loop và CPU

Giả sử:

```python
while True:
    pass
```

Nếu đoạn này nằm trong coroutine:

```python
async def work():

    while True:
        pass
```

Điều gì xảy ra?

```text
Coroutine A

↓

CPU

↓

CPU

↓

CPU

↓

Không gặp await

↓

Event Loop bị kẹt
```

Toàn bộ chương trình bị treo.

Đây là lý do coroutine phải **nhường quyền** bằng `await`.

---

# 14. Event Loop không tự ý cướp CPU

Khác với Thread.

Thread:

```text
OS

↓

Ép Thread đổi ngữ cảnh
```

Async:

```text
Coroutine

↓

Tự nguyện await

↓

Nhường quyền
```

Đó gọi là:

**Cooperative Scheduling**.

---

# 15. Sơ đồ hoạt động hoàn chỉnh

```text
Coroutine A
      │
      ▼
    await
      │
      ▼
Lưu trạng thái
      │
      ▼
 Event Loop
      │
      ├────────► Coroutine B
      │
      ├────────► Coroutine C
      │
      └────────► Coroutine D
                  │
                  ▼
          I/O hoàn thành
                  │
                  ▼
        Đưa A vào Ready Queue
                  │
                  ▼
             Tiếp tục A
```

---

# 16. So sánh Thread Scheduler và Event Loop

| Thread                        | Asyncio                                |
| ----------------------------- | -------------------------------------- |
| Scheduler của OS              | Scheduler của Event Loop               |
| OS quyết định chuyển ngữ cảnh | Coroutine tự nhường quyền bằng `await` |
| Chuyển ngữ cảnh tốn kém hơn   | Chuyển coroutine nhẹ hơn               |
| Có thể chạy trên nhiều CPU    | Thường chỉ dùng một Thread             |

---

# 17. Những hiểu lầm phổ biến

### Sai lầm 1

> Event Loop = CPU

❌ Sai.

Event Loop chỉ là **bộ điều phối**, không phải CPU.

---

### Sai lầm 2

> Event Loop tạo Thread

❌ Sai.

Không tạo Thread.

---

### Sai lầm 3

> `await` tạo Thread

❌ Sai.

`await` chỉ:

```text
Pause

↓

Resume
```

---

### Sai lầm 4

> Coroutine chạy song song

❌ Sai.

Coroutine **luân phiên chạy** trên cùng một Event Loop (trừ khi bạn chủ động kết hợp với Thread hoặc Process).

---

# 18. Tổng kết

## Những điều quan trọng nhất

* Event Loop là **trái tim của `asyncio`**.
* Event Loop là một **Scheduler**.
* Event Loop thường chạy trên **Main Thread**.
* Coroutine chỉ chạy khi Event Loop điều phối.
* Gặp `await`:

  * Coroutine tạm dừng.
  * Trạng thái được lưu lại.
  * Event Loop chuyển sang coroutine khác.
* Khi I/O hoàn thành:

  * Coroutine được đưa trở lại Ready Queue.
  * Tiếp tục chạy từ đúng vị trí đã dừng.

---

# Sơ đồ tư duy

```text
                  asyncio.run()
                        │
                        ▼
                 Tạo Event Loop
                        │
                        ▼
                  Ready Queue
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
  Coroutine A     Coroutine B     Coroutine C
        │               │               │
      await           await           await
        │               │               │
        └───────┬───────┴───────┬───────┘
                ▼               ▼
             Event Loop (Scheduler)
                │
                ▼
        Resume khi I/O hoàn thành
```

---

# Bài tập thực hành

## Bài 1

Cho đoạn mã:

```python
import asyncio

async def work():
    print("Bắt đầu")
    await asyncio.sleep(2)
    print("Kết thúc")

asyncio.run(work())
```

Hãy mô tả từng bước Event Loop thực hiện từ lúc gọi `asyncio.run()` đến khi chương trình kết thúc.

---

## Bài 2

Giải thích bằng lời của bạn:

* Ready Queue là gì?
* Coroutine bị đưa ra khỏi Ready Queue khi nào?
* Coroutine quay lại Ready Queue khi nào?

---

## Bài 3

Vẽ sơ đồ Event Loop xử lý ba coroutine `A`, `B`, `C`, trong đó:

* `A` chờ 3 giây.
* `B` chờ 1 giây.
* `C` chờ 2 giây.

Hãy dự đoán thứ tự các coroutine được tiếp tục thực thi.

---

## Bài 4 (Nâng cao)

Giả sử một coroutine chứa:

```python
async def work():
    x = 10
    await asyncio.sleep(5)
    print(x)
```

Hãy giải thích:

* Giá trị `x` có bị mất trong 5 giây chờ không?
* Python lưu trạng thái coroutine ở đâu (mức khái niệm)?
* Vì sao khi tiếp tục, coroutine vẫn in được `10`?

---

# Chuẩn bị cho Buổi 7

Ở buổi tiếp theo, chúng ta sẽ bắt đầu **đọc mã nguồn thực tế** với:

# Event Loop Deep Dive (Phần 2)

Bạn sẽ học:

* `asyncio.run()` được triển khai theo các bước nào.
* `asyncio.get_running_loop()` và `asyncio.get_event_loop()` khác nhau ra sao.
* Event Loop có những hàng đợi (queues) nội bộ nào.
* I/O Selector (`epoll`, `kqueue`, `IOCP`) là gì và vì sao `asyncio` có thể xử lý hàng chục nghìn socket mà không cần hàng chục nghìn thread.

Đây sẽ là bước chuyển từ **hiểu cách sử dụng** sang **hiểu cơ chế bên trong của `asyncio`** ở mức gần với mã nguồn của Python.
