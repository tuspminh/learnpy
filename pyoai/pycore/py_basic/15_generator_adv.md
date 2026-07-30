# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 15: Generator Nâng cao, `yield from`, Coroutine và nền tảng của `async`/`await`

> **Mục tiêu buổi học**
> 
> Sau buổi học này, bạn sẽ:
> 
> - Hiểu cơ chế hoạt động bên trong của Generator.
> - Thành thạo `yield from`.
> - Biết cách gửi dữ liệu vào Generator bằng `send()`.
> - Hiểu `close()` và `throw()`.
> - Hiểu Coroutine cổ điển trong Python.
> - Hiểu mối liên hệ giữa Generator và `async`/`await`.
> - Biết các ứng dụng thực tế trong xử lý dữ liệu, streaming và bất đồng bộ.

---

# 1. Ôn tập Generator

Buổi trước:

```text-x-trilium-auto
def numbers():
    yield 1
    yield 2
    yield 3
```

Sử dụng:

```text-x-trilium-auto
g = numbers()

print(next(g))
print(next(g))
print(next(g))
```

Kết quả:

```text-x-trilium-auto
1
2
3
```

Khi gặp:

```text-x-trilium-auto
yield
```

Python:

- Tạm dừng hàm.
- Ghi nhớ toàn bộ trạng thái.
- Tiếp tục từ đúng vị trí đó khi gọi `next()`.

---

# 2. Bên trong Generator

Ví dụ:

```text-x-trilium-auto
def demo():

    print("A")

    yield 1

    print("B")

    yield 2

    print("C")
```

Khởi tạo:

```text-x-trilium-auto
g = demo()
```

Lưu ý:

> Chưa có dòng nào được chạy.

Generator chỉ được tạo.

---

Gọi:

```text-x-trilium-auto
next(g)
```

In:

```text-x-trilium-auto
A
```

Trả về:

```text-x-trilium-auto
1
```

---

Gọi tiếp:

```text-x-trilium-auto
next(g)
```

In:

```text-x-trilium-auto
B
```

Trả:

```text-x-trilium-auto
2
```

---

Gọi tiếp:

```text-x-trilium-auto
next(g)
```

In:

```text-x-trilium-auto
C
```

Sau đó:

```text-x-trilium-auto
StopIteration
```

---

# 3. Generator ghi nhớ trạng thái

Ví dụ:

```text-x-trilium-auto
def counter():

    i = 1

    while True:

        yield i

        i += 1
```

Sử dụng:

```text-x-trilium-auto
g = counter()

print(next(g))
print(next(g))
print(next(g))
```

Kết quả:

```text-x-trilium-auto
1
2
3
```

Generator nhớ rằng:

```text-x-trilium-auto
i
```

đang bằng bao nhiêu.

Đây chính là **stateful object** (đối tượng có trạng thái).

---

# 4. `yield from`

Giả sử:

```text-x-trilium-auto
def numbers():

    yield 1

    yield 2

    yield 3
```

Muốn trả từng phần tử:

Thông thường:

```text-x-trilium-auto
def all_numbers():

    for x in numbers():

        yield x
```

Python cho phép viết ngắn hơn:

```text-x-trilium-auto
def all_numbers():

    yield from numbers()
```

Kết quả hoàn toàn giống nhau.

---

# 5. Ví dụ `yield from`

```text-x-trilium-auto
def letters():

    yield "A"

    yield "B"

def numbers():

    yield 1

    yield 2

def all_items():

    yield from letters()

    yield from numbers()
```

Kết quả:

```text-x-trilium-auto
for item in all_items():
    print(item)
```

```text-x-trilium-auto
A
B
1
2
```

---

# 6. Ứng dụng của `yield from`

Đọc nhiều file:

```text-x-trilium-auto
def read_all():

    yield from read_file1()

    yield from read_file2()

    yield from read_file3()
```

Streaming dữ liệu:

```text-x-trilium-auto
yield from socket_stream()
```

Đây là kỹ thuật được dùng rất nhiều trong các pipeline xử lý dữ liệu.

---

# 7. `send()`

Đây là tính năng rất đặc biệt.

Không chỉ lấy dữ liệu.

Mà còn gửi dữ liệu **vào Generator**.

Ví dụ:

```text-x-trilium-auto
def echo():

    while True:

        message = yield

        print(message)
```

Khởi tạo:

```text-x-trilium-auto
g = echo()
```

Khởi động Generator:

```text-x-trilium-auto
next(g)
```

Sau đó:

```text-x-trilium-auto
g.send("Hello")
```

Kết quả:

```text-x-trilium-auto
Hello
```

Tiếp:

```text-x-trilium-auto
g.send("Python")
```

```text-x-trilium-auto
Python
```

---

# 8. Vì sao cần `next()` trước?

Generator chưa chạy đến dòng:

```text-x-trilium-auto
message = yield
```

Nếu gọi:

```text-x-trilium-auto
g.send("Hello")
```

ngay lập tức sẽ lỗi:

```text-x-trilium-auto
TypeError
```

Muốn bắt đầu Generator cần:

```text-x-trilium-auto
next(g)
```

Hoặc:

```text-x-trilium-auto
g.send(None)
```

---

# 9. `yield` cũng là biểu thức

Ít người biết điều này.

Ví dụ:

```text-x-trilium-auto
value = yield
```

Python sẽ:

- Tạm dừng.
- Chờ dữ liệu.
- Giá trị của:

```text-x-trilium-auto
yield
```

chính là dữ liệu nhận từ:

```text-x-trilium-auto
send()
```

Đây là nền tảng của Coroutine.

---

# 10. Coroutine là gì?

Coroutine là:

> Một hàm có thể **nhận dữ liệu**, **tạm dừng** và **tiếp tục** nhiều lần.

Ví dụ:

```text-x-trilium-auto
def accumulator():

    total = 0

    while True:

        value = yield total

        total += value
```

Sử dụng:

```text-x-trilium-auto
g = accumulator()

print(next(g))
print(g.send(10))
print(g.send(20))
print(g.send(5))
```

Kết quả:

```text-x-trilium-auto
0
10
30
35
```

Đây là Coroutine cổ điển của Python.

---

# 11. `close()`

Có thể đóng Generator.

Ví dụ:

```text-x-trilium-auto
g.close()
```

Sau đó:

```text-x-trilium-auto
next(g)
```

Lỗi:

```text-x-trilium-auto
StopIteration
```

---

Ví dụ:

```text-x-trilium-auto
def demo():

    try:

        while True:

            yield

    finally:

        print("Đã đóng Generator")
```

---

# 12. `throw()`

Có thể ném Exception vào Generator.

Ví dụ:

```text-x-trilium-auto
g.throw(ValueError("Sai dữ liệu"))
```

Trong Generator:

```text-x-trilium-auto
try:
    ...
except ValueError:
    ...
```

Ứng dụng:

- Debug.
- Dừng pipeline.
- Xử lý lỗi trong streaming.

---

# 13. Generator Pipeline

Ví dụ:

```text-x-trilium-auto
def read():

    ...

def clean():

    ...

def save():

    ...
```

Pipeline:

```text-x-trilium-auto
yield from read()

↓

yield from clean()

↓

yield from save()
```

Đây là mô hình rất phổ biến trong xử lý dữ liệu lớn (ETL).

---

# 14. Mối liên hệ với `async`

Ngày nay:

```text-x-trilium-auto
async def hello():
```

thay thế phần lớn Coroutine kiểu cũ.

Tuy nhiên:

Python xây dựng:

```text-x-trilium-auto
async

↓

Generator

↓

yield
```

Hiểu Generator sẽ giúp bạn hiểu `asyncio` dễ dàng hơn rất nhiều.

---

# 15. Generator vs Coroutine

Generator:

```text-x-trilium-auto
yield dữ liệu
```

Coroutine:

```text-x-trilium-auto
yield

↓

nhận dữ liệu
```

Generator:

```text-x-trilium-auto
next()
```

Coroutine:

```text-x-trilium-auto
send()
```

---

# 16. Ví dụ thực tế

## Logger

```text-x-trilium-auto
def logger():

    while True:

        message = yield

        print(message)
```

---

## Chat Server

```text-x-trilium-auto
client.send()

↓

Coroutine
```

---

## Streaming

```text-x-trilium-auto
Video

↓

Frame

↓

Frame

↓

Frame
```

Generator giúp không cần tải toàn bộ video vào bộ nhớ.

---

# 17. Những lỗi phổ biến

## Lỗi 1

Quên:

```text-x-trilium-auto
next(generator)
```

trước:

```text-x-trilium-auto
send()
```

---

## Lỗi 2

Generator đã đóng.

```text-x-trilium-auto
close()
```

Không thể:

```text-x-trilium-auto
next()
```

---

## Lỗi 3

Không xử lý:

```text-x-trilium-auto
StopIteration
```

Khi dùng `next()` trực tiếp, hãy chuẩn bị xử lý ngoại lệ hoặc dùng `for` nếu không cần điều khiển thủ công.

---

# 18. Ví dụ thực tế

## Sinh ID

```text-x-trilium-auto
def ids():

    i = 1

    while True:

        yield f"USER{i:04}"

        i += 1
```

---

## Đọc Log

```text-x-trilium-auto
def logs():

    while True:

        yield read_line()
```

---

## Stream API

```text-x-trilium-auto
yield json_data
```

Đây là nguyên lý của nhiều API streaming hiện đại.

---

# 19. Bài tập thực hành

## Bài 1

Viết Generator:

```text-x-trilium-auto
alphabet()
```

Sinh:

```text-x-trilium-auto
A

B

...

Z
```

---

## Bài 2

Viết Generator:

```text-x-trilium-auto
odd_numbers()
```

Sinh số lẻ vô hạn.

---

## Bài 3

Viết:

```text-x-trilium-auto
yield from
```

để nối ba Generator lại với nhau.

---

## Bài 4

Viết Coroutine:

```text-x-trilium-auto
counter()
```

Nhận số bằng:

```text-x-trilium-auto
send()
```

và cộng dồn.

---

## Bài 5

Viết Generator:

```text-x-trilium-auto
read_csv()
```

Đọc từng dòng từ một file CSV lớn và `yield` từng bản ghi sau khi tách cột.

---

## Bài 6

Thử:

```text-x-trilium-auto
close()

throw()
```

và quan sát sự khác biệt trong hành vi của Generator.

---

# Mini Project: Pipeline xử lý dữ liệu

Xây dựng một pipeline gồm 4 Generator:

```text-x-trilium-auto
Đọc dữ liệu
      │
      ▼
Lọc dữ liệu
      │
      ▼
Chuyển đổi dữ liệu
      │
      ▼
Lưu dữ liệu
```

Yêu cầu:

1. Tạo Generator `read_data()` sinh từng dòng dữ liệu.
2. Tạo Generator `filter_data()` chỉ giữ lại các bản ghi hợp lệ.
3. Tạo Generator `transform_data()` chuyển đổi dữ liệu (ví dụ: chuẩn hóa chuỗi, tính toán trường mới).
4. Dùng `yield from` để kết nối các bước.
5. Chương trình chỉ xử lý **từng bản ghi một**, không nạp toàn bộ dữ liệu vào bộ nhớ.

---

# Tổng kết buổi 15

Bạn đã học:

- ✅ Cơ chế hoạt động bên trong của Generator.
- ✅ `yield from`.
- ✅ `send()`.
- ✅ `close()`.
- ✅ `throw()`.
- ✅ Coroutine cổ điển.
- ✅ Generator Pipeline.
- ✅ Mối liên hệ giữa Generator và `async`/`await`.
- ✅ Ứng dụng trong streaming và xử lý dữ liệu.

---

# Góc lập trình viên chuyên nghiệp

Các hệ thống hiện đại như:

- **FastAPI** (StreamingResponse).
- **aiohttp** (stream dữ liệu qua mạng).
- **Pandas** (đọc dữ liệu theo từng khối).
- **Scrapy** (pipeline xử lý dữ liệu).
- **Các mô hình AI** (trả kết quả từng token).

đều dựa trên tư tưởng **xử lý dữ liệu theo dòng (streaming)** thay vì tải toàn bộ dữ liệu vào bộ nhớ.

Generator và Coroutine chính là nền tảng giúp Python xây dựng những hệ thống này một cách hiệu quả.

---

# Chuẩn bị cho Buổi 16

Ở **Buổi 16**, chúng ta sẽ bước sang một cột mốc rất quan trọng:

# **Lập trình hướng đối tượng (Object-Oriented Programming - OOP) - Phần 1**

Chúng ta sẽ học:

- OOP là gì và vì sao cần OOP.
- Class và Object.
- Thuộc tính (Attributes).
- Phương thức (Methods).
- `self`.
- Hàm khởi tạo `__init__`.
- Khởi tạo và quản lý đối tượng.
- Thiết kế các lớp theo tư duy hướng đối tượng.

Đây là nền tảng để xây dựng các ứng dụng lớn như web, desktop, game, AI và hệ thống doanh nghiệp bằng Python. Từ buổi này trở đi, chúng ta sẽ chuyển dần từ **viết các đoạn mã** sang **thiết kế phần mềm** theo phong cách chuyên nghiệp.
