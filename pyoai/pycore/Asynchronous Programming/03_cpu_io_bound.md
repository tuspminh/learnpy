# Python Asynchronous Programming - Buổi 3

# CPU-bound và I/O-bound - Chọn đúng công cụ cho đúng bài toán

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ hiểu:
>
> * CPU-bound là gì.
> * I/O-bound là gì.
> * Vì sao `asyncio` không làm chương trình tính toán nhanh hơn.
> * Khi nào dùng Async, Thread hay Process.
> * Cách phân tích một bài toán trước khi lập trình.

---

# 1. Một câu hỏi rất quan trọng

Giả sử bạn có chương trình:

```python
for i in range(5_000_000_000):
    ...
```

Nếu thay bằng Async:

```python
async def work():
    for i in range(5_000_000_000):
        ...
```

Có nhanh hơn không?

Đáp án:

> **Không.**

Đây là điều mà rất nhiều lập trình viên mới học `asyncio` hiểu sai.

---

# 2. Chương trình tốn thời gian ở đâu?

Mọi chương trình đều tiêu tốn thời gian ở **hai loại hoạt động chính**:

```text
Chương trình

↓

CPU

↓

I/O
```

Hoặc nói cách khác:

```text
Tổng thời gian

=

Thời gian tính toán

+

Thời gian chờ
```

Ví dụ:

```text
Tính toán      2 giây

Chờ Internet   8 giây
```

Tổng:

```text
10 giây
```

---

# 3. CPU-bound là gì?

CPU-bound nghĩa là:

> Chương trình dành phần lớn thời gian để **tính toán trên CPU**.

Ví dụ:

* Nén file ZIP
* Mã hóa AES
* Render video
* Xử lý ảnh
* Machine Learning
* AI
* Tính số Fibonacci
* Nhân ma trận lớn
* Tính số nguyên tố

Ở đây:

CPU luôn bận.

---

## Ví dụ

```python
def calculate():
    total = 0

    for i in range(100_000_000):
        total += i

    return total
```

Timeline

```text
CPU

██████████████████████
```

Không có thời gian chờ.

CPU làm việc liên tục.

---

# 4. I/O-bound là gì?

I/O-bound nghĩa là:

> Chương trình dành phần lớn thời gian để **đợi dữ liệu từ bên ngoài**.

Ví dụ:

* HTTP Request
* Database
* Socket
* Web API
* Đọc file
* Ghi file
* Camera
* Bluetooth
* Microphone

Timeline

```text
CPU

██

Đợi

██████████

CPU

██

Đợi

██████████
```

CPU chỉ làm việc rất ít.

---

# 5. So sánh trực quan

## CPU-bound

```text
CPU

████████████████████████
```

CPU luôn bận.

---

## I/O-bound

```text
CPU

██

Waiting

████████

CPU

██

Waiting

████████
```

CPU rảnh rất nhiều.

---

# 6. Ví dụ CPU-bound

Tính Fibonacci bằng đệ quy:

```python
def fib(n):
    if n <= 1:
        return n

    return fib(n - 1) + fib(n - 2)

print(fib(40))
```

Điều gì xảy ra?

CPU phải thực hiện hàng trăm triệu phép tính.

Không có thời gian chờ I/O.

---

# 7. Ví dụ I/O-bound

```python
import requests

response = requests.get("https://example.com")
```

Quá trình:

```text
Python

↓

Gửi Request

↓

Đợi Internet

↓

Đợi Server

↓

Đợi Response

↓

Nhận dữ liệu
```

CPU gần như rảnh.

---

# 8. Một ví dụ đời sống

Giả sử bạn làm đầu bếp.

## CPU-bound

```text
Thái rau

↓

Băm thịt

↓

Nấu

↓

Chiên
```

Bạn làm việc liên tục.

Không có thời gian nghỉ.

---

## I/O-bound

```text
Cho bánh vào lò

↓

Đợi 20 phút

↓

Lấy bánh

↓

Cho bánh khác

↓

Đợi tiếp
```

Trong lúc chờ lò nướng,

bạn hoàn toàn có thể làm việc khác.

Đó chính là tư tưởng của Async.

---

# 9. Async giúp ở đâu?

Giả sử:

Download 5 file.

Mỗi file:

```text
1 giây gửi

5 giây chờ

1 giây lưu
```

Nếu Blocking

```text
File1

↓↓↓↓↓

File2

↓↓↓↓↓

File3

↓↓↓↓↓

...
```

Tổng:

```text
35 giây
```

---

Nếu Async

```text
Send 1

Send 2

Send 3

Send 4

Send 5

↓

Tất cả cùng chờ

↓

Lần lượt nhận kết quả
```

Có thể chỉ mất khoảng:

```text
7 giây
```

(Con số thực tế phụ thuộc vào máy chủ và mạng.)

---

# 10. Async không tăng tốc CPU

Ví dụ:

```python
def calculate():
    for i in range(10_000_000_000):
        ...
```

Đổi thành:

```python
async def calculate():
    for i in range(10_000_000_000):
        ...
```

Không khác.

Vì:

Không có chỗ nào để:

```python
await ...
```

Event Loop không có cơ hội chuyển sang công việc khác.

---

# 11. Khi nào Event Loop chuyển Task?

Event Loop chỉ chuyển sang coroutine khác khi gặp:

```python
await something()
```

Ví dụ

```python
async def download():
    await network()
```

Timeline

```text
Coroutine A

↓

await

↓

Pause

↓

Coroutine B
```

Nếu không có `await`:

```python
async def work():
    while True:
        ...
```

Event Loop:

```text
Coroutine A

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

Toàn bộ chương trình sẽ bị "đóng băng" vì coroutine này chiếm Event Loop.

---

# 12. Phân tích một bài toán

Giả sử:

Crawler 100 website.

Công việc gồm:

```text
Request

↓

Đợi Internet

↓

Đọc HTML

↓

Lưu Database
```

Đây là:

* HTTP → I/O
* Database → I/O

=> Async rất phù hợp.

---

Giả sử:

Resize 10.000 ảnh.

```text
Đọc ảnh

↓

Resize

↓

Lưu ảnh
```

Trong đó:

Resize chiếm gần hết thời gian.

Đây là:

CPU-bound.

Async không giúp nhiều.

---

# 13. Ví dụ hỗn hợp

Một ứng dụng AI:

```text
Download Model

↓

Đọc File

↓

Train AI

↓

Upload Result
```

Phân tích:

Download

↓

I/O

---

Read File

↓

I/O

---

Train

↓

CPU

---

Upload

↓

I/O

Đây là bài toán hỗn hợp. Bạn có thể kết hợp Async cho các bước I/O và Process cho bước huấn luyện.

---

# 14. Chọn công cụ đúng

| Bài toán            | Công cụ phù hợp                         |
| ------------------- | --------------------------------------- |
| Download nhiều file | Async                                   |
| Chat Server         | Async                                   |
| API Server          | Async                                   |
| WebSocket           | Async                                   |
| Database            | Async                                   |
| Đọc nhiều file      | Thread hoặc Async (nếu thư viện hỗ trợ) |
| Render Video        | Process                                 |
| AI                  | Process                                 |
| Machine Learning    | Process                                 |
| Tính toán lớn       | Process                                 |
| GUI + Download      | Async hoặc Thread                       |
| GUI + AI            | Process                                 |

---

# 15. Quy trình phân tích bài toán

Trước khi viết code, hãy tự hỏi:

```text
Chương trình chậm vì đâu?
        │
        ├── Chờ mạng?
        │       │
        │       └── Async
        │
        ├── Chờ Database?
        │       │
        │       └── Async
        │
        ├── Chờ File?
        │       │
        │       └── Async hoặc Thread
        │
        └── CPU tính toán?
                │
                └── Process
```

Đây là thói quen rất quan trọng của lập trình viên chuyên nghiệp.

---

# 16. Sai lầm phổ biến

### Sai lầm 1

> "Cứ dùng Async là nhanh."

❌ Sai.

Async chỉ giúp với **I/O-bound**.

---

### Sai lầm 2

> "Thread luôn nhanh hơn Async."

❌ Sai.

Với nhiều kết nối mạng đồng thời, Async thường sử dụng ít tài nguyên hơn và dễ mở rộng hơn.

---

### Sai lầm 3

> "CPU-bound cũng dùng Async."

❌ Sai.

Hãy dùng **Multiprocessing** hoặc thư viện tối ưu (NumPy, Cython, Rust...) khi phù hợp.

---

# 17. Tổng kết

## Ghi nhớ

### CPU-bound

* CPU luôn bận.
* Async không giúp tăng tốc.
* Dùng Process.

---

### I/O-bound

* CPU thường chờ.
* Async rất hiệu quả.
* Có thể dùng Thread nếu thư viện không hỗ trợ Async.

---

### Quy tắc vàng

```text
CPU-bound
        │
        └── Multiprocessing

I/O-bound
        │
        ├── Asyncio
        └── Thread (khi cần)
```

---

# Sơ đồ tư duy

```text
                 Chương trình
                      │
          ┌───────────┴───────────┐
          │                       │
      CPU-bound               I/O-bound
          │                       │
   CPU luôn bận            Chờ dữ liệu bên ngoài
          │                       │
    Render, AI, ML         HTTP, DB, File, Socket
          │                       │
   Multiprocessing      Asyncio / Thread
```

---

# Bài tập thực hành

### Bài 1

Phân loại các công việc sau là **CPU-bound** hay **I/O-bound**:

1. Tải 100 ảnh từ Internet.
2. Tính 10 triệu số Fibonacci.
3. Đọc 500 file log.
4. Gửi email cho 10.000 khách hàng.
5. Huấn luyện mô hình AI.
6. Truy vấn PostgreSQL.
7. Nén 5 GB dữ liệu.
8. Chat qua WebSocket.

---

### Bài 2

Viết chương trình mô phỏng một tác vụ CPU-bound:

```python
total = 0

for i in range(100_000_000):
    total += i

print(total)
```

Đo thời gian thực thi bằng `time.perf_counter()`.

---

### Bài 3

Viết chương trình mô phỏng một tác vụ I/O-bound:

```python
import time

for i in range(5):
    print(f"Lần {i + 1}")
    time.sleep(1)
```

Quan sát rằng phần lớn thời gian chương trình chỉ đang **chờ**, không phải tính toán.

---

## Chuẩn bị cho Buổi 4

Từ buổi sau, chúng ta sẽ bắt đầu bước vào **thế giới của `asyncio`**. Bạn sẽ học:

* `async def` thực sự tạo ra cái gì.
* Coroutine là gì và khác gì với hàm thông thường.
* Vì sao gọi một hàm `async` lại **không chạy ngay**.
* Cơ chế hoạt động của coroutine ở mức nền tảng.

Đây là bước chuyển từ lý thuyết về bất đồng bộ sang lập trình bất đồng bộ thực tế.
