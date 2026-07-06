# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 14: Làm chủ Iterator, Iterable, Generator và `yield` (Nền tảng của Python hiện đại)

> **Mục tiêu buổi học**
> 
> Sau buổi học này, bạn sẽ:
> 
> - Hiểu cách vòng lặp `for` hoạt động bên trong.
> - Phân biệt rõ **Iterable**, **Iterator** và **Generator**.
> - Thành thạo hàm `iter()` và `next()`.
> - Hiểu sâu từ khóa `yield`.
> - Biết khi nào nên dùng Generator thay vì List.
> - Xử lý dữ liệu lớn tiết kiệm bộ nhớ.
> - Hiểu nền tảng của `async for`, Pandas, Scrapy, FastAPI và các hệ thống xử lý dữ liệu hiện đại.

---

# 1. Mở đầu

Bạn đã sử dụng `for` rất nhiều:

```text-x-trilium-auto
for i in range(5):
    print(i)
```

Hay:

```text-x-trilium-auto
names = ["An", "Bình", "Lan"]

for name in names:
    print(name)
```

Nhưng bạn có biết:

> **Python thực hiện điều này như thế nào?**

Câu trả lời nằm ở **Iterable** và **Iterator**.

---

# 2. Iterable là gì?

Một **Iterable** là:

> Một đối tượng có thể được duyệt qua bằng vòng lặp `for`.

Ví dụ:

```text-x-trilium-auto
numbers = [1, 2, 3]
```

Là Iterable.

Các đối tượng sau đều là Iterable:

```text-x-trilium-auto
list
tuple
dict
set
str
range
file
generator
```

Ví dụ:

```text-x-trilium-auto
text = "Python"

for char in text:
    print(char)
```

Kết quả:

```text-x-trilium-auto
P
y
t
h
o
n
```

---

# 3. Iterator là gì?

Iterator là đối tượng:

- Ghi nhớ vị trí hiện tại.
- Biết phần tử tiếp theo là gì.

Ví dụ:

```text-x-trilium-auto
numbers = [10, 20, 30]
```

Tạo Iterator:

```text-x-trilium-auto
it = iter(numbers)
```

Lấy từng phần tử:

```text-x-trilium-auto
print(next(it))
print(next(it))
print(next(it))
```

Kết quả:

```text-x-trilium-auto
10
20
30
```

---

Nếu gọi thêm:

```text-x-trilium-auto
next(it)
```

Lỗi:

```text-x-trilium-auto
StopIteration
```

---

# 4. Hình dung Iterator

Danh sách:

```text-x-trilium-auto
10 → 20 → 30
```

Iterator:

```text-x-trilium-auto
^
```

Sau:

```text-x-trilium-auto
next(it)
```

```text-x-trilium-auto
10 → 20 → 30
     ^
```

Iterator luôn ghi nhớ vị trí.

---

# 5. `for` hoạt động như thế nào?

Đoạn:

```text-x-trilium-auto
for x in numbers:
    print(x)
```

Thực chất gần giống:

```text-x-trilium-auto
it = iter(numbers)

while True:
    try:
        x = next(it)
        print(x)
    except StopIteration:
        break
```

Đây chính là cơ chế bên trong của `for`.

---

# 6. Kiểm tra một đối tượng có phải Iterable không

```text-x-trilium-auto
from collections.abc import Iterable

print(isinstance([1,2,3], Iterable))
```

Kết quả:

```text-x-trilium-auto
True
```

---

Kiểm tra Iterator:

```text-x-trilium-auto
from collections.abc import Iterator

it = iter([1,2,3])

print(isinstance(it, Iterator))
```

---

# 7. Iterable và Iterator khác nhau thế nào?

Ví dụ:

```text-x-trilium-auto
numbers = [1,2,3]
```

Đây là:

```text-x-trilium-auto
Iterable
```

Nhưng:

```text-x-trilium-auto
next(numbers)
```

Lỗi.

Vì list không phải Iterator.

Phải:

```text-x-trilium-auto
it = iter(numbers)
```

Sau đó:

```text-x-trilium-auto
next(it)
```

---

# 8. Generator là gì?

Generator là:

> Một Iterator được tạo dễ dàng bằng `yield`.

Ví dụ:

```text-x-trilium-auto
def numbers():

    yield 1

    yield 2

    yield 3
```

Tạo Generator:

```text-x-trilium-auto
g = numbers()
```

Lấy giá trị:

```text-x-trilium-auto
print(next(g))
```

Kết quả:

```text-x-trilium-auto
1
```

Tiếp:

```text-x-trilium-auto
print(next(g))
```

```text-x-trilium-auto
2
```

---

# 9. `yield` khác `return`

`return`

```text-x-trilium-auto
def hello():
    return 10
```

Khi gặp:

```text-x-trilium-auto
return
```

Hàm kết thúc ngay.

---

`yield`

```text-x-trilium-auto
def hello():

    yield 10

    yield 20
```

Hàm **tạm dừng**.

Lần sau gọi `next()` sẽ tiếp tục từ vị trí trước đó.

---

# 10. Hình dung `yield`

```text-x-trilium-auto
def demo():

    print("A")

    yield 1

    print("B")

    yield 2

    print("C")
```

Thực hiện:

```text-x-trilium-auto
g = demo()
```

Lần 1:

```text-x-trilium-auto
next(g)
```

In:

```text-x-trilium-auto
A
```

Trả:

```text-x-trilium-auto
1
```

---

Lần 2:

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

Lần 3:

```text-x-trilium-auto
C
```

Sau đó:

```text-x-trilium-auto
StopIteration
```

---

# 11. Generator tiết kiệm bộ nhớ

Không nên:

```text-x-trilium-auto
numbers = []

for i in range(10000000):
    numbers.append(i)
```

Tốn rất nhiều RAM.

Generator:

```text-x-trilium-auto
def generate():

    for i in range(10000000):

        yield i
```

Không lưu toàn bộ.

Chỉ tạo khi cần.

Đây gọi là:

> **Lazy Evaluation (Đánh giá lười).**

---

# 12. So sánh List và Generator

List:

```text-x-trilium-auto
[x*x for x in range(5)]
```

Kết quả:

```text-x-trilium-auto
[0,1,4,9,16]
```

---

Generator:

```text-x-trilium-auto
(x*x for x in range(5))
```

Kết quả:

```text-x-trilium-auto
<generator object ...>
```

Muốn xem:

```text-x-trilium-auto
list(generator)
```

---

# 13. Generator Expression

Giống List Comprehension.

List:

```text-x-trilium-auto
numbers = [x*x for x in range(10)]
```

Generator:

```text-x-trilium-auto
numbers = (x*x for x in range(10))
```

Khác biệt:

- List tạo ngay.
- Generator tạo khi cần.

---

# 14. Đọc file lớn

Sai:

```text-x-trilium-auto
with open("log.txt") as f:

    data = f.readlines()
```

Nếu file 10GB:

RAM sẽ rất lớn.

Đúng:

```text-x-trilium-auto
with open("log.txt") as f:

    for line in f:
        print(line)
```

Python đọc từng dòng.

Đây là Iterator.

---

# 15. Tự viết Generator

```text-x-trilium-auto
def countdown(n):

    while n > 0:

        yield n

        n -= 1
```

Sử dụng:

```text-x-trilium-auto
for i in countdown(5):
    print(i)
```

Kết quả:

```text-x-trilium-auto
5
4
3
2
1
```

---

# 16. Generator vô hạn

```text-x-trilium-auto
def forever():

    i = 0

    while True:

        yield i

        i += 1
```

Có thể:

```text-x-trilium-auto
g = forever()

for _ in range(10):

    print(next(g))
```

Đây là cách nhiều hệ thống streaming hoạt động.

---

# 17. Ứng dụng thực tế

### Đọc log

```text-x-trilium-auto
for line in logfile:
```

---

### Web Scraping

Scrapy dùng Generator rất nhiều.

---

### AI

Sinh dữ liệu từng batch.

---

### Video

Đọc từng frame.

---

### ChatGPT Streaming

Không gửi cả câu trả lời.

Mà gửi:

```text-x-trilium-auto
Token

↓

Token

↓

Token
```

Generator là nền tảng của cơ chế này.

---

# 18. Những lỗi phổ biến

## Lỗi 1

Generator chỉ chạy một lần.

```text-x-trilium-auto
g = numbers()

list(g)

list(g)
```

Lần hai:

```text-x-trilium-auto
[]
```

Vì Generator đã hết dữ liệu.

Muốn dùng lại:

```text-x-trilium-auto
g = numbers()
```

---

## Lỗi 2

Nhầm Generator với List.

Sai:

```text-x-trilium-auto
len(generator)
```

Generator không có độ dài cố định.

---

## Lỗi 3

Quên `yield`.

Sai:

```text-x-trilium-auto
def gen():

    return 1
```

Không phải Generator.

---

# 19. Ví dụ thực tế

## Sinh ID

```text-x-trilium-auto
def id_generator():

    i = 1

    while True:

        yield f"EMP{i:05}"

        i += 1
```

---

## Đọc cảm biến

```text-x-trilium-auto
def sensor():

    while True:

        value = read_sensor()

        yield value
```

---

## Sinh mật khẩu

```text-x-trilium-auto
def passwords():

    ...
```

Mỗi lần:

```text-x-trilium-auto
yield
```

một mật khẩu.

---

# 20. Bài tập thực hành

## Bài 1

Viết Generator:

```text-x-trilium-auto
count_up(10)
```

Sinh:

```text-x-trilium-auto
1

2

...

10
```

---

## Bài 2

Viết Generator:

```text-x-trilium-auto
even_numbers()
```

Sinh số chẵn vô hạn.

---

## Bài 3

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

## Bài 4

Viết Generator:

```text-x-trilium-auto
fibonacci()
```

Sinh dãy Fibonacci vô hạn.

---

## Bài 5

So sánh:

- List
- Generator

về:

- RAM
- Tốc độ
- Khả năng tái sử dụng

Hãy thử dùng `sys.getsizeof()` để đo bộ nhớ mà mỗi kiểu đối tượng sử dụng.

---

## Bài 6

Đọc file lớn bằng Generator và đếm số dòng chứa từ khóa `"ERROR"` mà không dùng `readlines()`.

---

# Mini Project: Hệ thống đọc log thời gian thực

Viết chương trình:

```text-x-trilium-auto
def read_log(filename):
    ...
```

Yêu cầu:

- Đọc từng dòng bằng Generator.
- Chỉ xử lý một dòng tại một thời điểm.
- Nếu dòng chứa `"ERROR"` thì in ra màn hình.
- Có thể mở rộng để theo dõi tệp log đang được ghi liên tục (tương tự lệnh `tail -f` trên Linux).

---

# Tổng kết buổi 14

Hôm nay bạn đã học:

- ✅ Iterable.
- ✅ Iterator.
- ✅ `iter()`.
- ✅ `next()`.
- ✅ `StopIteration`.
- ✅ Generator.
- ✅ `yield`.
- ✅ Generator Expression.
- ✅ Lazy Evaluation.
- ✅ So sánh Generator và List.
- ✅ Các ứng dụng thực tế trong xử lý dữ liệu lớn.

---

# Góc lập trình viên chuyên nghiệp

**Iterator** và **Generator** là nền tảng của rất nhiều công nghệ hiện đại:

- **Pandas** đọc dữ liệu theo từng khối (`chunksize`).
- **Scrapy** xử lý dữ liệu web theo luồng.
- **FastAPI** có `StreamingResponse` để trả dữ liệu dần dần.
- **asyncio** và `async for` mở rộng ý tưởng của Iterator sang môi trường bất đồng bộ.
- Các mô hình AI hiện đại (bao gồm các chatbot) thường **stream** kết quả theo từng token thay vì đợi tạo xong toàn bộ phản hồi.

Nếu hiểu rõ cơ chế này, bạn sẽ biết cách xây dựng các chương trình vừa **tiết kiệm bộ nhớ**, vừa **xử lý dữ liệu lớn hiệu quả**.

---

# Chuẩn bị cho Buổi 15

Ở **Buổi 15**, chúng ta sẽ học **Generator nâng cao và Coroutine**:

- Cơ chế hoạt động bên trong của `yield`.
- `yield from`.
- Gửi dữ liệu vào Generator bằng `send()`.
- Đóng Generator với `close()`.
- Xử lý ngoại lệ bằng `throw()`.
- Mô hình Coroutine cổ điển.
- Mối liên hệ giữa Generator và `async`/`await`.

Đây là bước đệm quan trọng trước khi đi vào **lập trình bất đồng bộ (**`**asyncio**`**)**, một trong những kỹ năng quan trọng nhất của Python hiện đại.
