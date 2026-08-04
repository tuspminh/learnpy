# Giai đoạn 1 – Python Foundation

# Buổi 16. Lambda Function (Hàm vô danh)

> `lambda` là một tính năng quan trọng của Python, thường được sử dụng trong **lập trình hàm (Functional Programming)**. Bạn sẽ gặp `lambda` rất nhiều khi làm việc với `sorted()`, `map()`, `filter()`, `reduce()`, Pandas, PyQt/PySide, Flask, Django và nhiều thư viện khác.

> **Lưu ý:** `lambda` không thay thế hoàn toàn `def`. Trong Python chuyên nghiệp, `lambda` chỉ nên dùng cho các hàm ngắn gọn, đơn giản.

---

# Mục tiêu

Sau buổi học này, bạn sẽ:

* Hiểu `lambda` là gì.
* Biết cú pháp của `lambda`.
* So sánh `lambda` với `def`.
* Sử dụng `lambda` với `sorted()`, `map()`, `filter()`.
* Hiểu cách `lambda` hoạt động như một object.
* Biết khi nào nên và không nên dùng `lambda`.
* Áp dụng `lambda` vào các bài toán thực tế.

---

# 1. Lambda là gì?

`lambda` là **hàm vô danh (anonymous function)**.

Thông thường, khi tạo một hàm:

```python
def add(a, b):
    return a + b
```

Có thể viết ngắn gọn:

```python
add = lambda a, b: a + b
```

Hai cách trên có chức năng giống nhau.

---

# 2. Cú pháp

```python
lambda parameters: expression
```

Trong đó:

* `lambda` : từ khóa.
* `parameters` : tham số.
* `expression` : biểu thức trả về.

Ví dụ:

```python
square = lambda x: x * x

print(square(5))
```

Kết quả:

```text
25
```

---

# 3. So sánh với `def`

### Dùng `def`

```python
def multiply(a, b):
    return a * b


print(multiply(3, 4))
```

### Dùng `lambda`

```python
multiply = lambda a, b: a * b

print(multiply(3, 4))
```

Kết quả:

```text
12
```

---

# 4. Lambda luôn trả về giá trị

Ví dụ:

```python
double = lambda x: x * 2

print(double(8))
```

Kết quả:

```text
16
```

Bạn không cần viết `return`.

Python tự trả về kết quả của biểu thức.

---

# 5. Lambda không có tên

Ví dụ:

```python
lambda x: x + 1
```

Đây là một hàm nhưng chưa được gán cho biến nào.

Có thể gán:

```python
increase = lambda x: x + 1

print(increase(9))
```

Kết quả:

```text
10
```

---

# 6. Lambda nhiều tham số

```python
area = lambda width, height: width * height

print(area(10, 5))
```

Kết quả:

```text
50
```

---

# 7. Lambda không có tham số

```python
hello = lambda: "Hello Python"

print(hello())
```

Kết quả:

```text
Hello Python
```

---

# 8. Lambda có điều kiện

Có thể dùng toán tử ba ngôi.

```python
is_even = lambda x: "Chẵn" if x % 2 == 0 else "Lẻ"

print(is_even(8))
print(is_even(5))
```

Kết quả:

```text
Chẵn
Lẻ
```

---

# 9. Lambda là Object

```python
add = lambda a, b: a + b

print(type(add))
```

Kết quả:

```text
<class 'function'>
```

Điều này cho thấy `lambda` cũng là một đối tượng hàm (`function object`).

---

# 10. Truyền Lambda vào hàm

Ví dụ:

```python
def calculate(func, x):
    return func(x)


result = calculate(lambda x: x * 3, 10)

print(result)
```

Kết quả:

```text
30
```

Đây là nền tảng của callback.

---

# 11. Lambda với `sorted()`

Ví dụ:

```python
students = [("Lan", 20), ("An", 18), ("Hoa", 22)]

students.sort(key=lambda student: student[1])

print(students)
```

Kết quả:

```text
[
 ('An', 18),
 ('Lan', 20),
 ('Hoa', 22)
]
```

`lambda student: student[1]` nghĩa là sắp xếp theo tuổi.

---

# 12. Sắp xếp Dictionary

```python
students = [
    {"name": "Lan", "score": 8},
    {"name": "An", "score": 10},
    {"name": "Hoa", "score": 7},
]

students.sort(key=lambda item: item["score"])

print(students)
```

Kết quả:

```text
[
 {'name': 'Hoa', 'score': 7},
 {'name': 'Lan', 'score': 8},
 {'name': 'An', 'score': 10}
]
```

---

# 13. `sorted()`

Không làm thay đổi dữ liệu gốc.

```python
numbers = [5, 3, 1, 4, 2]

result = sorted(numbers)

print(result)
print(numbers)
```

Kết quả:

```text
[1, 2, 3, 4, 5]
[5, 3, 1, 4, 2]
```

---

# 14. Lambda với `map()`

`map()` áp dụng một hàm lên từng phần tử.

```python
numbers = [1, 2, 3, 4]

result = map(lambda x: x * 2, numbers)

print(list(result))
```

Kết quả:

```text
[2, 4, 6, 8]
```

---

# 15. Lambda với `filter()`

Lọc dữ liệu.

```python
numbers = [1, 2, 3, 4, 5, 6]

result = filter(lambda x: x % 2 == 0, numbers)

print(list(result))
```

Kết quả:

```text
[2, 4, 6]
```

---

# 16. Lambda với `max()`

```python
students = [
    {"name": "An", "score": 8},
    {"name": "Lan", "score": 10},
    {"name": "Hoa", "score": 9},
]

best = max(students, key=lambda s: s["score"])

print(best)
```

Kết quả:

```text
{'name': 'Lan', 'score': 10}
```

---

# 17. Lambda với `min()`

```python
youngest = min(
    [
        {"name": "Lan", "age": 22},
        {"name": "An", "age": 18},
        {"name": "Hoa", "age": 25},
    ],
    key=lambda person: person["age"],
)

print(youngest)
```

Kết quả:

```text
{'name': 'An', 'age': 18}
```

---

# 18. Khi nào nên dùng Lambda?

Nên dùng khi:

* Hàm rất ngắn.
* Chỉ dùng một lần.
* Làm callback.
* Dùng với `sorted()`, `map()`, `filter()`, `max()`, `min()`.

Ví dụ:

```python
numbers = [5, 3, 1]

print(sorted(numbers, key=lambda x: -x))
```

---

# 19. Khi nào KHÔNG nên dùng Lambda?

Không nên:

```python
calculate = lambda price, tax, discount: ((price * tax) - discount + 100) * 5 / 7
```

Rất khó đọc.

Nên:

```python
def calculate(price, tax, discount):
    subtotal = price * tax
    result = (subtotal - discount + 100) * 5 / 7
    return result
```

Nguyên tắc:

> Nếu biểu thức dài hơn một dòng hoặc cần nhiều bước xử lý, hãy dùng `def`.

---

# 20. Lambda và Closure

Lambda có thể truy cập biến bên ngoài.

```python
tax = 0.1

calculate = lambda price: price + price * tax

print(calculate(100))
```

Kết quả:

```text
110.0
```

Đây là một dạng **closure đơn giản**, sẽ học kỹ hơn ở giai đoạn Intermediate.

---

# 21. So sánh `lambda` và `def`

| Tiêu chí     | `lambda`                 | `def`          |
| ------------ | ------------------------ | -------------- |
| Có tên       | Không (trừ khi gán biến) | Có             |
| Nhiều dòng   | ❌                        | ✅              |
| Có `return`  | Tự động                  | Viết rõ        |
| Có docstring | ❌                        | ✅              |
| Dễ đọc       | Hàm ngắn                 | Mọi trường hợp |
| Thích hợp    | Callback, hàm ngắn       | Logic phức tạp |

---

# 22. Những lỗi thường gặp

## Lỗi 1: Viết nhiều câu lệnh

Sai:

```python
lambda x:
    y = x * 2
    return y
```

`lambda` chỉ chứa **một biểu thức**, không chứa nhiều câu lệnh.

---

## Lỗi 2: Lạm dụng `lambda`

Sai:

```python
result = lambda a, b, c, d: (a + b + c + d) / 4 if a > 0 else 0
```

Khó đọc.

Nên dùng `def`.

---

## Lỗi 3: Quên chuyển `map()` và `filter()` thành danh sách

```python
numbers = [1, 2, 3]

result = map(lambda x: x * 2, numbers)

print(result)
```

Kết quả:

```text
<map object at 0x...>
```

Đúng:

```python
print(list(result))
```

---

# 23. Ví dụ thực tế

## Sắp xếp sản phẩm theo giá

```python
products = [
    {"name": "Laptop", "price": 25000},
    {"name": "Mouse", "price": 500},
    {"name": "Keyboard", "price": 1200},
]

products.sort(key=lambda p: p["price"])

for product in products:
    print(product)
```

---

## Lọc sinh viên đạt

```python
students = [
    {"name": "An", "score": 8},
    {"name": "Lan", "score": 4},
    {"name": "Hoa", "score": 9},
]

passed = list(filter(lambda student: student["score"] >= 5, students))

print(passed)
```

---

## Tăng lương 10%

```python
salaries = [1000, 1200, 1500]

new_salaries = list(map(lambda salary: salary * 1.1, salaries))

print(new_salaries)
```

Kết quả:

```text
[1100.0, 1320.0, 1650.0]
```

---

# 24. Bài tập thực hành

## Bài 1

Viết `lambda` tính bình phương.

Ví dụ:

```python
square = lambda x: ...
```

---

## Bài 2

Viết `lambda` kiểm tra số chẵn.

Trả về `True` hoặc `False`.

---

## Bài 3

Cho:

```python
students = [
    {"name": "An", "score": 7},
    {"name": "Lan", "score": 9},
    {"name": "Hoa", "score": 8},
]
```

Sắp xếp theo điểm giảm dần bằng `sorted()` và `lambda`.

---

## Bài 4

Cho:

```python
numbers = [1, 2, 3, 4, 5]
```

Dùng `map()` và `lambda` để tạo danh sách bình phương.

---

## Bài 5

Cho:

```python
numbers = list(range(1, 21))
```

Dùng `filter()` và `lambda` để lấy các số chia hết cho 3.

---

# Tổng kết

Trong buổi học này, bạn đã học:

* Khái niệm `lambda`.
* Cú pháp và cách hoạt động.
* So sánh `lambda` với `def`.
* Sử dụng `lambda` với `sorted()`, `map()`, `filter()`, `max()`, `min()`.
* Khi nào nên và không nên dùng `lambda`.
* Các lỗi thường gặp và ví dụ thực tế.

---

# Chuẩn bị cho Buổi 17

Ở **Buổi 17**, chúng ta sẽ học **List Comprehension** – một trong những cú pháp "đặc trưng" của Python giúp viết mã ngắn gọn, dễ đọc và hiệu quả hơn.

Các nội dung sẽ bao gồm:

* Cú pháp cơ bản của List Comprehension.
* Chuyển đổi từ vòng lặp `for` sang List Comprehension.
* Kết hợp với điều kiện `if`.
* List Comprehension lồng nhau (Nested).
* So sánh hiệu năng với vòng lặp thông thường.
* Những trường hợp nên và không nên sử dụng trong các dự án Python chuyên nghiệp.
