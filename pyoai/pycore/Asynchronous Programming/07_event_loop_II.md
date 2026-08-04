# Python Asynchronous Programming - Buổi 7

# Event Loop Deep Dive (Phần 2) - Bên trong `asyncio.run()` và Event Loop

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ hiểu:
>
> * `asyncio.run()` thực sự làm gì.
> * Event Loop được tạo và hủy như thế nào.
> * `get_running_loop()` và `get_event_loop()` khác nhau ra sao.
> * Ready Queue, Timer Queue, I/O Queue là gì.
> * Vì sao Event Loop có thể quản lý hàng chục nghìn socket.

> **Lưu ý:** Đây là buổi đi sâu vào nội bộ của `asyncio`. Chúng ta sẽ mô tả theo cách dễ hiểu; một số chi tiết triển khai có thể khác nhau giữa các phiên bản Python hoặc hệ điều hành, nhưng các khái niệm cốt lõi là giống nhau.

---

# 1. Điều gì xảy ra khi gọi `asyncio.run()`?

Bạn thường viết:

```python
import asyncio

async def main():
    print("Hello")

asyncio.run(main())
```

Trông rất đơn giản.

Nhưng bên trong, Python thực hiện nhiều bước.

Có thể hình dung như sau:

```text
Tạo Event Loop

↓

Đặt Event Loop hiện tại

↓

Tạo Task cho main()

↓

Chạy Event Loop

↓

Đợi main() kết thúc

↓

Hủy các Task còn lại (nếu có)

↓

Đóng Event Loop
```

`asyncio.run()` giúp bạn không phải tự làm các bước này.

---

# 2. Mô phỏng `asyncio.run()`

Nếu tự viết (đơn giản hóa), ý tưởng sẽ gần như:

```python
loop = asyncio.new_event_loop()

asyncio.set_event_loop(loop)

loop.run_until_complete(main())

loop.close()
```

Đây **không phải** mã nguồn thật của Python, nhưng giúp bạn hiểu quy trình.

---

# 3. Tại sao phải tạo Event Loop?

Coroutine chỉ là:

```text
Coroutine Object
```

Nó không tự chạy.

Cần có:

```text
Coroutine

↓

Event Loop

↓

Running
```

Nếu không có Event Loop:

```python
hello()
```

chỉ tạo coroutine.

Không thực thi.

---

# 4. Event Loop có chạy mãi không?

Có hai trường hợp.

### Trường hợp 1

Trong chương trình:

```python
asyncio.run(main())
```

Event Loop:

```text
Tạo

↓

Chạy

↓

main() xong

↓

Đóng
```

---

### Trường hợp 2

Web Server

Ví dụ:

* FastAPI
* aiohttp
* WebSocket Server

Event Loop:

```text
Khởi động

↓

while True

↓

Đợi Request

↓

Xử lý

↓

Đợi tiếp
```

Có thể chạy nhiều giờ hoặc nhiều ngày.

---

# 5. `get_running_loop()`

Ví dụ:

```python
import asyncio

async def main():
    loop = asyncio.get_running_loop()
    print(loop)

asyncio.run(main())
```

Kết quả:

```text
<_UnixSelectorEventLoop ...>
```

(Trên Windows có thể là kiểu Event Loop khác.)

Ý nghĩa:

Lấy Event Loop **đang chạy**.

---

# 6. `get_event_loop()`

Đây là API cũ hơn.

Ngày trước thường viết:

```python
loop = asyncio.get_event_loop()
```

Hiện nay:

Python khuyến khích:

```python
asyncio.get_running_loop()
```

vì rõ ràng hơn trong coroutine.

> Trong các phiên bản Python mới, hành vi của `get_event_loop()` đã thay đổi và không còn là lựa chọn mặc định trong coroutine.

---

# 7. Event Loop bên trong có gì?

Bạn có thể hình dung:

```text
Event Loop
│
├── Ready Queue
│
├── Timer Queue
│
├── I/O Selector
│
└── Scheduler
```

Đây là bốn thành phần rất quan trọng.

---

# 8. Ready Queue

Đã học ở buổi trước.

Đây là nơi chứa:

```text
Task A

Task B

Task C
```

đã sẵn sàng chạy.

---

# 9. Timer Queue

Giả sử:

```python
await asyncio.sleep(5)
```

Coroutine có chạy ngay không?

Không.

Nó được đưa vào:

```text
Timer Queue
```

Kèm theo:

```text
Thời điểm đánh thức

↓

5 giây sau
```

Event Loop liên tục kiểm tra:

```text
Đã đến giờ chưa?
```

Nếu:

```text
Có
```

↓

Đưa trở lại Ready Queue.

---

# 10. Ví dụ

Có:

```python
await asyncio.sleep(3)
```

Timeline:

```text
0s

Ready Queue

↓

Running

↓

sleep(3)

↓

Timer Queue

↓

3 giây

↓

Ready Queue

↓

Running
```

---

# 11. I/O Queue

Giả sử:

```python
await socket.recv()
```

Socket chưa có dữ liệu.

Event Loop:

```text
Running

↓

Đợi dữ liệu

↓

Đưa sang I/O Queue
```

Không lãng phí CPU.

---

# 12. Khi dữ liệu đến

Ví dụ:

Server gửi dữ liệu.

OS thông báo:

```text
Socket Ready
```

Event Loop:

```text
I/O Queue

↓

Ready Queue

↓

Running
```

Coroutine tiếp tục chạy.

---

# 13. Scheduler

Scheduler là "bộ não" của Event Loop.

Nó quyết định:

```text
Task nào chạy trước

Task nào chạy sau

Task nào được Resume
```

Thông thường:

Scheduler chọn các Task đã sẵn sàng.

---

# 14. Một vòng lặp hoàn chỉnh

Có thể hình dung Event Loop như:

```text
while True:

    kiểm tra Timer

    kiểm tra Socket

    kiểm tra File

    lấy Task từ Ready Queue

    chạy Task

    gặp await

    đưa Task sang Queue phù hợp
```

Đó chính là lý do gọi là:

```text
Event Loop
```

---

# 15. Vì sao Async quản lý được 10.000 socket?

Đây là điều kỳ diệu nhất.

Không phải:

```text
10.000 Socket

↓

10.000 Thread
```

Mà là:

```text
10.000 Socket

↓

OS theo dõi

↓

Event Loop

↓

Coroutine
```

Thread:

```text
Socket A

↓

Thread A
```

Socket B

↓

Thread B

...

Tốn rất nhiều RAM.

---

Async:

```text
Socket A

↓

Coroutine A

Socket B

↓

Coroutine B

Socket C

↓

Coroutine C

↓

Một Event Loop
```

Rất nhẹ.

---

# 16. Event Loop giao tiếp với OS như thế nào?

Đây là nơi Event Loop trở nên rất mạnh.

Nó không liên tục hỏi:

```text
Có dữ liệu chưa?

Có dữ liệu chưa?

Có dữ liệu chưa?
```

(thao tác này gọi là polling kiểu bận, rất tốn CPU)

Thay vào đó, nó sử dụng cơ chế thông báo của hệ điều hành.

Ví dụ:

Linux

```text
epoll
```

macOS / BSD

```text
kqueue
```

Windows

```text
IOCP
```

Ý tưởng:

```text
OS

↓

Khi socket có dữ liệu

↓

Thông báo Event Loop

↓

Event Loop Resume Coroutine
```

Đây là cơ chế **event-driven**.

---

# 17. Minh họa

Giả sử:

1000 client.

```text
Client

↓

Server

↓

Socket

↓

OS

↓

Event Loop

↓

Coroutine
```

Nếu:

Client số 500 gửi dữ liệu.

OS báo:

```text
Socket #500 Ready
```

Event Loop chỉ đánh thức:

```text
Coroutine #500
```

999 coroutine còn lại vẫn ngủ.

Đó là lý do Async cực kỳ hiệu quả.

---

# 18. Toàn bộ sơ đồ

```text
                asyncio.run()

                      │

          Tạo Event Loop

                      │

        ┌─────────────┼─────────────┐

        ▼             ▼             ▼

 Ready Queue     Timer Queue     I/O Queue

        │             │             │

        └─────────────┼─────────────┘

                      ▼

                 Scheduler

                      ▼

                 Coroutine

                      ▼

                    await

                      ▼

              Quay lại Queue
```

---

# 19. Những hiểu lầm phổ biến

### Sai lầm 1

> `asyncio.sleep()` vẫn chiếm CPU.

❌ Sai.

Trong thời gian ngủ, coroutine nằm trong **Timer Queue**.

---

### Sai lầm 2

> Event Loop liên tục kiểm tra mọi socket.

❌ Không theo kiểu "hỏi liên tục". Nó chủ yếu dựa vào cơ chế thông báo của hệ điều hành (`epoll`, `kqueue`, `IOCP`).

---

### Sai lầm 3

> Có 10.000 coroutine thì CPU chạy 10.000 việc cùng lúc.

❌ Sai.

CPU vẫn chỉ chạy **một coroutine tại một thời điểm trên một Event Loop**.

---

# 20. Tổng kết

Bạn cần nhớ sơ đồ sau:

```text
Coroutine

↓

await

↓

Queue phù hợp

↓

Event Loop

↓

Scheduler

↓

Ready Queue

↓

Running

↓

await

↓

...
```

Đây là chu trình sống của mọi coroutine trong `asyncio`.

---

# Sơ đồ tư duy

```text
                Event Loop
                     │
     ┌───────────────┼───────────────┐
     │               │               │
Ready Queue     Timer Queue     I/O Queue
     │               │               │
     └───────────────┼───────────────┘
                     ▼
                Scheduler
                     ▼
                 Coroutine
                     ▼
                   await
                     ▼
              Chuyển Queue
```

---

# Bài tập thực hành

## Bài 1

Giải thích bằng lời:

Vì sao:

```python
await asyncio.sleep(5)
```

không làm chương trình bị treo?

---

## Bài 2

Cho ba coroutine:

* A: `await asyncio.sleep(5)`
* B: `await asyncio.sleep(1)`
* C: `await asyncio.sleep(3)`

Hãy vẽ:

* Ready Queue
* Timer Queue

ở từng thời điểm.

---

## Bài 3

Giải thích:

Tại sao Async Server có thể phục vụ 20.000 client mà không cần tạo 20.000 thread?

---

## Bài 4 (Tư duy)

Nếu hệ điều hành **không có** `epoll`, `kqueue` hay `IOCP`, Event Loop sẽ phải kiểm tra socket theo cách nào? Theo bạn, điều đó sẽ ảnh hưởng thế nào đến hiệu năng?

---

# Chuẩn bị cho Buổi 8

Từ buổi sau, chúng ta sẽ chuyển từ **lý thuyết về Event Loop** sang **thực hành lập trình bất đồng bộ** với:

# Coroutine nâng cao

Bạn sẽ học:

* Coroutine chaining.
* Gọi lồng nhiều coroutine.
* Giá trị trả về của coroutine.
* `await` nhiều tầng.
* Luồng thực thi khi nhiều coroutine gọi lẫn nhau.
* Stack của coroutine và cách Event Loop quay lại đúng vị trí sau mỗi lần `await`.

Sau buổi 8, bạn sẽ có đủ nền tảng để bước sang **Task**, **`asyncio.create_task()`**, **`gather()`** và xây dựng các chương trình bất đồng bộ thực tế.
