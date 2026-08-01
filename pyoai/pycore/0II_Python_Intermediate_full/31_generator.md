# Buổi 31. Generator trong Python (Python Intermediate)

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Hiểu Generator là gì và vì sao nó quan trọng.
> * Phân biệt Generator và Iterator.
> * Thành thạo `yield`.
> * Viết Generator Function.
> * Sử dụng Generator Expression.
> * Hiểu `yield from`.
> * Biết `send()`, `close()`, `throw()`.
> * Ứng dụng Generator trong xử lý dữ liệu lớn, pipeline và streaming.

> **Lưu ý**
>
> Bạn đã học một khóa **Generator Deep Dive** trước đây. Buổi này tập trung vào mức **Python Intermediate**, giúp bạn sử dụng Generator thành thạo trong các chương trình Python thông thường.

---

# 1. Generator là gì?

Generator là **một loại Iterator đặc biệt** được tạo bằng từ khóa `yield`.

Thay vì trả về toàn bộ dữ liệu cùng lúc như `return`, Generator **tạo từng giá trị một khi cần**.

Ví dụ:

```python
def numbers():
    yield 1
    yield 2
    yield 3
```

Sử dụng:

```python
g = numbers()

print(next(g))
print(next(g))
print(next(g))
```

Kết quả:

```text
1
2
3
```

---

# 2. `return` vs `yield`

Ví dụ với `return`:

```python
def func():
    return 1
    return 2
```

Kết quả:

```text
1
```

Hàm kết thúc ngay sau `return`.

---

Ví dụ với `yield`:

```python
def func():
    yield 1
    yield 2
```

Kết quả:

```text
1
2
```

Hàm **tạm dừng** sau mỗi `yield` và tiếp tục từ đúng vị trí đó ở lần gọi `next()` tiếp theo.

---

# 3. Generator Function

Một hàm chứa `yield` sẽ trở thành Generator Function.

```python
def countdown():
    yield 3
    yield 2
    yield 1
```

```python
g = countdown()

for x in g:
    print(x)
```

Output:

```text
3
2
1
```

---

# 4. Kiểm tra kiểu dữ liệu

```python
def numbers():
    yield 1


g = numbers()

print(type(g))
```

Output:

```text
<class 'generator'>
```

Generator là một Iterator.

---

# 5. Generator là Iterator

Có thể dùng:

```python
next(g)
```

Hoặc:

```python
for x in g:
    print(x)
```

Hoặc:

```python
list(g)
```

---

# 6. Generator chỉ chạy khi cần

```python
def hello():
    print("Start")
    yield 1
    print("Continue")
    yield 2
```

```python
g = hello()

print(next(g))
print(next(g))
```

Output:

```text
Start
1
Continue
2
```

Generator **không chạy khi được tạo**, mà chỉ chạy khi có yêu cầu lấy giá trị (`next()` hoặc `for`).

---

# 7. Trạng thái của Generator

```python
def demo():
    print("A")
    yield 1

    print("B")
    yield 2

    print("C")
```

Generator ghi nhớ:

* biến cục bộ,
* vị trí thực thi,
* ngăn xếp lời gọi.

Điều này làm Generator mạnh hơn nhiều so với một hàm thông thường.

---

# 8. Generator vs List

List:

```python
numbers = [x for x in range(1_000_000)]
```

Sinh toàn bộ dữ liệu.

---

Generator:

```python
numbers = (x for x in range(1_000_000))
```

Sinh từng phần tử.

RAM sử dụng rất nhỏ.

---

# 9. Generator Expression

Giống List Comprehension.

List:

```python
nums = [x * 2 for x in range(5)]
```

Generator:

```python
nums = (x * 2 for x in range(5))
```

Sử dụng:

```python
for x in nums:
    print(x)
```

---

# 10. So sánh bộ nhớ

```python
nums = [x for x in range(10_000_000)]
```

Có thể tiêu tốn hàng trăm MB RAM.

---

```python
nums = (x for x in range(10_000_000))
```

RAM gần như không đổi.

Đây là một trong những lý do Generator được dùng nhiều trong xử lý dữ liệu lớn.

---

# 11. `yield from`

Ví dụ:

```python
def numbers():
    yield from [1, 2, 3]
```

Tương đương:

```python
def numbers():
    for x in [1, 2, 3]:
        yield x
```

---

Ví dụ khác:

```python
def letters():
    yield from "ABC"
```

Output:

```text
A
B
C
```

---

# 12. `send()`

Generator có thể nhận dữ liệu.

```python
def echo():
    while True:
        value = yield
        print(value)
```

```python
g = echo()

next(g)

g.send("Hello")

g.send("Python")
```

Output:

```text
Hello
Python
```

`next(g)` đầu tiên dùng để đưa Generator tới `yield` đầu tiên.

---

# 13. `close()`

```python
def numbers():
    yield 1
    yield 2
```

```python
g = numbers()

g.close()
```

Sau đó:

```python
next(g)
```

↓

```text
StopIteration
```

---

# 14. `throw()`

Có thể ném ngoại lệ vào Generator.

```python
def demo():
    try:
        yield 1
    except ValueError:
        print("ValueError")
```

```python
g = demo()

next(g)

g.throw(ValueError)
```

Output:

```text
ValueError
```

---

# 15. Generator Pipeline

Ví dụ:

```python
def read():
    for i in range(5):
        yield i


def square(data):
    for x in data:
        yield x * x
```

```python
for value in square(read()):
    print(value)
```

Output:

```text
0
1
4
9
16
```

Pipeline giúp xử lý dữ liệu theo từng bước mà không cần tạo danh sách trung gian.

---

# 16. Đọc file lớn

Sai:

```python
with open("huge.log") as f:
    lines = f.readlines()
```

Đọc toàn bộ file vào RAM.

---

Đúng:

```python
def read_lines(filename):
    with open(filename) as f:
        for line in f:
            yield line
```

---

# 17. Lọc dữ liệu

```python
def errors(lines):
    for line in lines:
        if "ERROR" in line:
            yield line
```

Sử dụng:

```python
for line in errors(read_lines("app.log")):
    print(line)
```

---

# 18. Generator trong Crawler

```python
def crawl_pages():
    page = 1

    while True:
        yield page
        page += 1
```

Mỗi lần lấy:

```python
next(generator)
```

↓

Trang tiếp theo.

---

# 19. Generator trong CSV

```python
import csv


def students():
    with open("students.csv") as f:
        reader = csv.DictReader(f)

        for row in reader:
            yield row
```

Không cần đọc toàn bộ file CSV.

---

# 20. Generator trong API

Ví dụ phân trang:

```python
def api_pages():
    page = 1

    while True:
        data = fetch(page)

        if not data:
            break

        yield data

        page += 1
```

---

# 21. Generator và `StopIteration`

Generator tự động phát sinh `StopIteration` khi:

* chạy hết hàm,
* hoặc gặp `return`.

Ví dụ:

```python
def demo():
    yield 1
    return
```

Sau khi lấy `1`, Generator kết thúc.

---

# 22. Những lỗi thường gặp

## Sai 1: Quên `yield`

```python
def numbers():
    return [1, 2, 3]
```

Đây là hàm bình thường, không phải Generator.

---

## Sai 2: Dùng lại Generator

```python
g = numbers()

list(g)
list(g)
```

Output:

```text
[]
```

Generator đã bị tiêu thụ.

---

## Sai 3: Chuyển Generator thành List khi không cần

```python
data = list(big_generator())
```

Nếu dữ liệu rất lớn sẽ làm mất lợi thế về bộ nhớ.

---

# 23. Best Practices

## ✔ Dùng Generator cho dữ liệu lớn

Ví dụ:

* File lớn.
* CSV lớn.
* JSON lớn.
* Streaming.

---

## ✔ Dùng Pipeline

Ví dụ:

```text
Đọc file
    ↓
Lọc
    ↓
Chuyển đổi
    ↓
Ghi kết quả
```

Mỗi bước là một Generator.

---

## ✔ Dùng Generator Expression

Thay vì:

```python
squares = [x * x for x in range(1000)]
```

Nếu chỉ duyệt một lần:

```python
squares = (x * x for x in range(1000))
```

---

## ✔ Không lạm dụng `send()` và `throw()`

Hai phương thức này rất mạnh nhưng làm mã khó đọc hơn. Trong đa số ứng dụng, `yield` và `yield from` đã đủ.

---

# 24. Mini Project - Log Processing Pipeline

Cấu trúc:

```text
log_pipeline/

├── app.log
└── main.py
```

`app.log`

```text
INFO Start
ERROR Database
INFO Login
WARNING Disk
ERROR Timeout
```

Pipeline:

```text
Đọc file
      ↓
Lọc ERROR
      ↓
Chuyển thành chữ thường
      ↓
In kết quả
```

Ví dụ:

```text
error database
error timeout
```

Mỗi bước được triển khai bằng một Generator riêng.

---

# Tổng kết

Sau buổi học này, bạn đã nắm được:

* Generator là gì.
* `yield` và Generator Function.
* Generator Expression.
* `yield from`.
* `send()`, `close()`, `throw()`.
* Sự khác nhau giữa Generator và List.
* Xây dựng Pipeline bằng Generator.
* Ứng dụng trong xử lý file, crawler, API và dữ liệu lớn.

---

# So sánh Iterator và Generator

| Tiêu chí           | Iterator                          | Generator                    |
| ------------------ | --------------------------------- | ---------------------------- |
| Cách tạo           | Viết `__iter__()` và `__next__()` | Dùng `yield`                 |
| Độ dài mã          | Dài hơn                           | Ngắn gọn                     |
| Ghi nhớ trạng thái | Tự quản lý                        | Python tự quản lý            |
| Dễ viết            | Trung bình                        | Rất dễ                       |
| Hiệu năng          | Tốt                               | Tốt                          |
| Tiết kiệm bộ nhớ   | Có                                | Có                           |
| Khuyến nghị        | Khi cần kiểm soát chi tiết        | Trong hầu hết các trường hợp |

---

# Bài tập thực hành

### Bài 1

Viết Generator sinh các số từ `1` đến `10`.

### Bài 2

Viết Generator sinh các số Fibonacci đầu tiên.

Ví dụ:

```text
1 1 2 3 5 8 13 ...
```

### Bài 3

Viết Generator đọc từng dòng của một file văn bản và chỉ trả về các dòng chứa từ `"ERROR"`.

### Bài 4

Viết Generator Pipeline:

```text
range(1, 21)
    ↓
lọc số chẵn
    ↓
bình phương
    ↓
in kết quả
```

Mỗi bước là một Generator riêng.

### Bài 5

Viết Generator Expression tạo các lập phương (`x ** 3`) của các số từ `1` đến `100`, sau đó tính tổng mà không tạo danh sách trung gian.

### Bài 6 (Thử thách)

Xây dựng một **Lazy CSV Processor**:

* Đọc file CSV bằng `csv.DictReader`.
* Trả về từng bản ghi dưới dạng Generator.
* Lọc những sinh viên có điểm trung bình ≥ 8.
* Chuyển tên sinh viên thành chữ hoa.
* Ghi kết quả ra file CSV mới.

Toàn bộ quá trình phải xử lý theo kiểu **streaming**, không được đọc toàn bộ dữ liệu vào bộ nhớ.

---

# Chuẩn bị cho buổi sau

Ở **Buổi 32**, chúng ta sẽ học **Decorator** trong Python Intermediate, bao gồm:

* Hàm là đối tượng hạng nhất (First-class Functions).
* Hàm lồng nhau (Nested Functions).
* Khái niệm Decorator.
* Cú pháp `@decorator`.
* Truyền tham số với `*args`, `**kwargs`.
* Bảo toàn metadata bằng `functools.wraps`.
* Các Decorator hữu ích như `@staticmethod`, `@classmethod`, `@property` và một số ứng dụng thực tế như logging, đo thời gian thực thi và kiểm tra quyền truy cập.
