# Buổi 30. Iterator trong Python (Python Intermediate)

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Hiểu Iterator là gì.
> * Phân biệt **Iterable** và **Iterator**.
> * Hiểu Iterator Protocol.
> * Thành thạo `iter()` và `next()`.
> * Tự xây dựng Iterator.
> * Hiểu `StopIteration`.
> * Hiểu cách `for` hoạt động bên trong.
> * Biết khi nào nên dùng Iterator.

> **Lưu ý**
>
> Bạn đã học một khóa **Iterator Deep Dive** rất chi tiết trước đây. Buổi này là phiên bản **Python Intermediate**, tập trung vào kiến thức nền tảng cần thiết để học **Generator (Buổi 31)** và **Context Manager (Buổi 34)**.

---

# 1. Iterator là gì?

Hãy tưởng tượng bạn có một hộp chứa 1 triệu quyển sách.

Bạn không thể cầm cùng lúc 1 triệu quyển.

Bạn sẽ lấy:

```
Quyển 1

↓

Quyển 2

↓

Quyển 3

↓

...
```

Đó chính là ý tưởng của Iterator.

Iterator **không trả toàn bộ dữ liệu cùng lúc**.

Nó trả từng phần tử một.

---

# 2. Iterable là gì?

Iterable là đối tượng **có thể lặp được**.

Ví dụ:

```python
numbers = [1, 2, 3]
```

Đây là Iterable.

Ta có thể:

```python
for x in numbers:
    print(x)
```

Các kiểu dữ liệu Iterable phổ biến:

```python
list
tuple
dict
set
str
range
file
```

---

# 3. Iterator là gì?

Iterator là đối tượng:

* nhớ vị trí hiện tại
* trả phần tử tiếp theo
* khi hết sẽ báo dừng

Ví dụ:

```python
numbers = iter([1, 2, 3])

print(next(numbers))
print(next(numbers))
print(next(numbers))
```

Output

```
1
2
3
```

Lần tiếp theo

```python
print(next(numbers))
```

↓

```
StopIteration
```

---

# 4. Iterable vs Iterator

```
Iterable

↓

iter()

↓

Iterator

↓

next()

↓

next()

↓

next()

↓

StopIteration
```

Đây là chu trình quan trọng nhất của Iterator.

---

# 5. Hàm `iter()`

```python
numbers = [10, 20, 30]

it = iter(numbers)

print(it)
```

Output

```python
<list_iterator object>
```

Không phải list.

Mà là

```
Iterator
```

---

# 6. Hàm `next()`

```python
numbers = iter([10, 20, 30])

print(next(numbers))
```

↓

```
10
```

Tiếp

```python
print(next(numbers))
```

↓

```
20
```

---

# 7. `for` hoạt động như thế nào?

Ta thường viết

```python
for x in [1, 2, 3]:
    print(x)
```

Python thực hiện gần tương đương:

```python
it = iter([1, 2, 3])

while True:
    try:
        x = next(it)
        print(x)
    except StopIteration:
        break
```

Đây là cơ chế cốt lõi của vòng lặp `for`.

---

# 8. `StopIteration`

Ví dụ

```python
it = iter([1])

print(next(it))

print(next(it))
```

↓

```
StopIteration
```

Đây **không phải lỗi lập trình**.

Nó là tín hiệu:

```
Không còn dữ liệu.
```

---

# 9. Iterator Protocol

Một Iterator phải có:

```python
__iter__()

__next__()
```

Đó gọi là

```
Iterator Protocol
```

---

# 10. Tự tạo Iterator

Ví dụ

```python
class Counter:
    def __init__(self):

        self.current = 1

    def __iter__(self):
        return self

    def __next__(self):

        if self.current > 5:
            raise StopIteration

        value = self.current

        self.current += 1

        return value
```

Sử dụng

```python
counter = Counter()

for i in counter:
    print(i)
```

Output

```
1
2
3
4
5
```

---

# 11. Giải thích

Trong class trên

```python
__iter__()
```

trả về

```
chính Iterator
```

Còn

```python
__next__()
```

trả về phần tử tiếp theo.

---

# 12. Iterator có trạng thái

Ví dụ

```python
it = iter([1, 2, 3])

print(next(it))
```

↓

```
1
```

Lần sau

```python
print(next(it))
```

↓

```
2
```

Iterator luôn nhớ vị trí hiện tại.

---

# 13. Không thể quay lại

```python
it = iter([1, 2, 3])

next(it)

next(it)
```

Bây giờ không thể quay về

```
1
```

Muốn đọc lại

```python
it = iter([1, 2, 3])
```

tạo Iterator mới.

---

# 14. File cũng là Iterator

```python
with open("data.txt") as f:
    print(next(f))

    print(next(f))
```

Python đọc từng dòng.

Không đọc toàn bộ file.

Đó là lý do đọc file rất tiết kiệm RAM.

---

# 15. Dict Iterator

```python
data = {"a": 1, "b": 2}

it = iter(data)

print(next(it))
```

↓

```
a
```

Iterator của `dict` mặc định duyệt qua các khóa.

---

# 16. `enumerate()`

```python
names = ["Alice", "Bob"]

for i, name in enumerate(names):
    print(i, name)
```

`enumerate()` trả về một Iterable, tạo các cặp `(index, value)`.

---

# 17. `zip()`

```python
names = ["Alice", "Bob"]
ages = [20, 21]

for name, age in zip(names, ages):
    print(name, age)
```

`zip()` cũng tạo ra một Iterator, giúp ghép nhiều Iterable.

---

# 18. `reversed()`

```python
nums = [1, 2, 3]

for x in reversed(nums):
    print(x)
```

Output

```
3
2
1
```

`reversed()` không tạo list mới mà trả về một Iterator.

---

# 19. `map()`

```python
nums = [1, 2, 3]

result = map(lambda x: x * 2, nums)

print(list(result))
```

Output

```
[2, 4, 6]
```

`map()` cũng trả về Iterator.

---

# 20. `filter()`

```python
nums = [1, 2, 3, 4]

result = filter(lambda x: x % 2 == 0, nums)

print(list(result))
```

Output

```
[2, 4]
```

---

# 21. Iterator chỉ dùng một lần

```python
it = iter([1, 2, 3])

print(list(it))

print(list(it))
```

Output

```
[1, 2, 3]
[]
```

Iterator đã bị "tiêu thụ" (consumed).

---

# 22. Khi nào nên dùng Iterator?

✔ File lớn

```python
for line in open("big.txt"):
    ...
```

---

✔ Crawler

```
URL

↓

URL

↓

URL
```

Không cần tải toàn bộ URL vào bộ nhớ trước.

---

✔ Log Parser

Đọc từng dòng log.

---

✔ Dữ liệu Streaming

Ví dụ:

```
Kafka

Socket

Queue
```

Dữ liệu đến liên tục và được xử lý từng phần.

---

# 23. Iterator và List

List

```
Toàn bộ dữ liệu

↓

RAM
```

Iterator

```
Từng phần tử

↓

RAM rất nhỏ
```

---

# 24. Ví dụ thực tế

Đọc file log:

```python
with open("app.log") as f:
    for line in f:
        if "ERROR" in line:
            print(line.strip())
```

Nếu `app.log` có dung lượng vài GB, chương trình vẫn hoạt động hiệu quả vì chỉ đọc từng dòng.

---

# 25. Những lỗi thường gặp

## Sai 1: Gọi `next()` quá số phần tử

```python
it = iter([1])

next(it)
next(it)
```

↓

```
StopIteration
```

Nếu tự dùng `next()`, nên xử lý:

```python
try:
    print(next(it))
except StopIteration:
    print("Hết dữ liệu")
```

Hoặc:

```python
print(next(it, None))
```

Tham số thứ hai là giá trị mặc định khi Iterator kết thúc.

---

## Sai 2: Nghĩ rằng Iterator có thể dùng lại

Sai

```python
it = iter([1, 2, 3])

list(it)

list(it)
```

↓

```
[]
```

---

## Sai 3: Sửa dữ liệu khi đang lặp

```python
numbers = [1, 2, 3]

for x in numbers:
    numbers.append(100)
```

Có thể gây vòng lặp không mong muốn hoặc hành vi khó dự đoán.

---

# 26. Best Practices

## ✔ Dùng `for`

Thay vì

```python
it = iter(data)

while True:
    try:
        print(next(it))
    except StopIteration:
        break
```

Hãy:

```python
for item in data:
    print(item)
```

Đơn giản và an toàn hơn.

---

## ✔ Chỉ dùng `next()` khi thật sự cần

Ví dụ:

* Parser
* Streaming
* Pipeline
* State Machine

---

## ✔ Không chuyển Iterator thành `list()` nếu dữ liệu lớn

Sai

```python
lines = list(open("huge.log"))
```

Đúng

```python
with open("huge.log") as f:
    for line in f:
        ...
```

---

## ✔ Hiểu rõ vòng đời của Iterator

Sau khi đã duyệt hết, Iterator không tự "quay lại". Nếu cần lặp lại, hãy tạo Iterator mới từ Iterable.

---

# 27. Mini Project - CSV Reader

Cấu trúc:

```text
csv_reader/

├── students.csv
└── main.py
```

`students.csv`

```csv
id,name,age
1,Alice,20
2,Bob,21
3,Charlie,22
```

Yêu cầu:

* Đọc từng dòng bằng `csv.reader()`.
* In ra từng bản ghi.
* Không đọc toàn bộ file vào bộ nhớ.
* Chỉ xử lý từng dòng một.

Đây là cách xử lý phù hợp với các file CSV rất lớn.

---

# Tổng kết

Sau buổi học này, bạn đã nắm được:

* Khái niệm **Iterable** và **Iterator**.
* `iter()` và `next()`.
* `StopIteration`.
* Iterator Protocol (`__iter__()` và `__next__()`).
* Cách `for` hoạt động bên trong.
* Các Iterator phổ biến như `map()`, `filter()`, `zip()`, `enumerate()`, `reversed()`.
* Ứng dụng Iterator trong xử lý file lớn, crawler và dữ liệu streaming.

# Bài tập thực hành

### Bài 1

Tạo một Iterator duyệt qua danh sách `[10, 20, 30, 40]` bằng `iter()` và `next()`.

### Bài 2

Viết lớp `EvenNumbers` sinh các số chẵn từ `2` đến `20` bằng cách triển khai `__iter__()` và `__next__()`.

### Bài 3

Đọc một file văn bản lớn, đếm số dòng chứa từ khóa `"ERROR"` mà không dùng `read()` hoặc `readlines()`.

### Bài 4

Sử dụng `zip()` để ghép hai danh sách:

```python
names = ["Alice", "Bob", "Charlie"]
scores = [85, 92, 78]
```

và in ra:

```text
Alice: 85
Bob: 92
Charlie: 78
```

### Bài 5

Sử dụng `map()` và `filter()` để:

* Nhân đôi các số trong danh sách.
* Lọc ra các số lớn hơn `10`.

### Bài 6 (Thử thách)

Xây dựng một lớp `PaginationIterator` nhận:

* danh sách dữ liệu,
* kích thước trang (`page_size`),

và mỗi lần gọi `next()` sẽ trả về **một trang dữ liệu** thay vì một phần tử.

Ví dụ:

```python
data = list(range(1, 11))
it = PaginationIterator(data, page_size=3)

print(next(it))  # [1, 2, 3]
print(next(it))  # [4, 5, 6]
print(next(it))  # [7, 8, 9]
print(next(it))  # [10]
```

---

# Chuẩn bị cho buổi sau

Ở **Buổi 31**, chúng ta sẽ học **Generator** – một chủ đề mở rộng trực tiếp từ Iterator, bao gồm:

* Từ khóa `yield`.
* Generator Function.
* Generator Expression.
* `yield from`.
* Gửi dữ liệu vào Generator (`send()`).
* Đóng Generator (`close()`).
* Ứng dụng trong xử lý dữ liệu lớn, pipeline và streaming.

Đây là một trong những tính năng mạnh và đặc trưng nhất của Python, giúp viết các chương trình vừa gọn gàng vừa tiết kiệm bộ nhớ.
