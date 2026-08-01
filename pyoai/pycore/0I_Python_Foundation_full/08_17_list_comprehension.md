# Giai đoạn 1 – Python Foundation

# Buổi 17. List Comprehension

> **List Comprehension** là một trong những cú pháp nổi tiếng nhất của Python. Nó giúp tạo danh sách (List) một cách **ngắn gọn, rõ ràng và thường nhanh hơn** so với cách dùng vòng lặp thông thường. Trong các dự án Python chuyên nghiệp, bạn sẽ gặp List Comprehension rất thường xuyên.

> Sau khi thành thạo bài này, bạn sẽ dễ dàng học **Dict Comprehension**, **Set Comprehension**, **Generator Expression** và xử lý dữ liệu với Pandas.

---

# Mục tiêu

Sau buổi học này, bạn sẽ:

* Hiểu List Comprehension là gì.
* Biết chuyển từ `for` sang List Comprehension.
* Kết hợp với `if`.
* Sử dụng `if...else`.
* Viết List Comprehension lồng nhau.
* Hiểu phạm vi biến trong List Comprehension.
* So sánh hiệu năng với vòng lặp thông thường.
* Biết khi nào nên và không nên sử dụng.

---

# 1. List Comprehension là gì?

List Comprehension là cú pháp tạo List bằng một biểu thức duy nhất.

Thay vì:

```python
numbers = []

for i in range(5):
    numbers.append(i)

print(numbers)
```

Có thể viết:

```python
numbers = [i for i in range(5)]

print(numbers)
```

Kết quả:

```text
[0, 1, 2, 3, 4]
```

---

# 2. Cú pháp

```python
[expression for item in iterable]
```

Ví dụ:

```python
squares = [x * x for x in range(6)]

print(squares)
```

Kết quả:

```text
[0, 1, 4, 9, 16, 25]
```

---

# 3. Chuyển từ vòng lặp sang List Comprehension

### Cách thông thường

```python
result = []

for i in range(1, 6):
    result.append(i * 10)

print(result)
```

### List Comprehension

```python
result = [i * 10 for i in range(1, 6)]

print(result)
```

Kết quả:

```text
[10, 20, 30, 40, 50]
```

---

# 4. Duyệt List

```python
names = ["An", "Lan", "Hoa"]

upper_names = [name.upper() for name in names]

print(upper_names)
```

Kết quả:

```text
['AN', 'LAN', 'HOA']
```

---

# 5. Kết hợp với `if`

Lấy các số chẵn:

```python
numbers = [1, 2, 3, 4, 5, 6]

evens = [n for n in numbers if n % 2 == 0]

print(evens)
```

Kết quả:

```text
[2, 4, 6]
```

---

Lấy số lớn hơn 10:

```python
numbers = [5, 12, 8, 20, 15]

result = [n for n in numbers if n > 10]

print(result)
```

Kết quả:

```text
[12, 20, 15]
```

---

# 6. `if...else` trong List Comprehension

Cú pháp:

```python
[expression_if if condition else expression_else for item in iterable]
```

Ví dụ:

```python
numbers = [1, 2, 3, 4, 5]

result = ["Chẵn" if n % 2 == 0 else "Lẻ" for n in numbers]

print(result)
```

Kết quả:

```text
['Lẻ', 'Chẵn', 'Lẻ', 'Chẵn', 'Lẻ']
```

> **Lưu ý:** `if` dùng để **lọc** sẽ đặt sau `for`, còn `if...else` dùng để **chọn giá trị** sẽ đặt trước `for`.

---

# 7. List Comprehension với String

```python
text = "Python"

letters = [char for char in text]

print(letters)
```

Kết quả:

```text
['P', 'y', 't', 'h', 'o', 'n']
```

---

Đổi sang chữ thường:

```python
text = "PYTHON"

result = [char.lower() for char in text]

print(result)
```

Kết quả:

```text
['p', 'y', 't', 'h', 'o', 'n']
```

---

# 8. Dùng với `enumerate()`

```python
names = ["An", "Lan", "Hoa"]

result = [f"{index}: {name}" for index, name in enumerate(names)]

print(result)
```

Kết quả:

```text
['0: An', '1: Lan', '2: Hoa']
```

---

# 9. List Comprehension lồng nhau

Tạo bảng cửu chương:

```python
table = [[i * j for j in range(1, 6)] for i in range(1, 4)]

print(table)
```

Kết quả:

```text
[
    [1, 2, 3, 4, 5],
    [2, 4, 6, 8, 10],
    [3, 6, 9, 12, 15]
]
```

---

# 10. Hai vòng lặp

```python
pairs = [(x, y) for x in range(3) for y in range(2)]

print(pairs)
```

Kết quả:

```text
[
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 1),
    (2, 0),
    (2, 1)
]
```

Tương đương:

```python
pairs = []

for x in range(3):
    for y in range(2):
        pairs.append((x, y))
```

---

# 11. Làm phẳng (Flatten) List lồng nhau

```python
matrix = [[1, 2], [3, 4], [5, 6]]

flat = [item for row in matrix for item in row]

print(flat)
```

Kết quả:

```text
[1, 2, 3, 4, 5, 6]
```

---

# 12. Gọi hàm trong List Comprehension

```python
def square(x):
    return x * x


numbers = [1, 2, 3, 4]

result = [square(n) for n in numbers]

print(result)
```

Kết quả:

```text
[1, 4, 9, 16]
```

---

# 13. List Comprehension và Scope

```python
numbers = [x for x in range(5)]

print(x)
```

Trong Python 3:

```text
NameError
```

Biến `x` **không bị rò rỉ** ra ngoài List Comprehension.

Đây là điểm khác với Python 2.

---

# 14. So sánh với `map()`

```python
numbers = [1, 2, 3]

result = [x * 2 for x in numbers]
```

Tương đương:

```python
result = list(map(lambda x: x * 2, numbers))
```

Trong nhiều trường hợp, List Comprehension dễ đọc hơn.

---

# 15. Hiệu năng

Thông thường:

```text
List Comprehension
        ↓
Nhanh hơn một chút
        ↓
For + append()
```

Lý do:

* Được tối ưu trong CPython.
* Giảm số lần gọi phương thức `append()`.

Tuy nhiên, chênh lệch thường không lớn. Hãy ưu tiên **độ dễ đọc** trước khi tối ưu.

---

# 16. Khi nào nên dùng?

Nên dùng khi:

* Tạo List mới.
* Chuyển đổi dữ liệu.
* Lọc dữ liệu.
* Logic đơn giản.

Ví dụ:

```python
prices = [100, 200, 300]

vat_prices = [price * 1.1 for price in prices]
```

---

# 17. Khi nào KHÔNG nên dùng?

Không nên:

```python
result = [
    calculate_discount(user, get_tax(user), get_coupon(user), get_shipping(user))
    for user in users
]
```

Quá dài và khó đọc.

Nên:

```python
result = []

for user in users:
    discount = calculate_discount(
        user, get_tax(user), get_coupon(user), get_shipping(user)
    )
    result.append(discount)
```

Nguyên tắc:

> Nếu List Comprehension dài hơn khoảng 2–3 dòng hoặc chứa logic phức tạp, hãy dùng `for` thông thường.

---

# 18. Ví dụ thực tế

## Chuyển tên thành chữ hoa

```python
students = ["An", "Lan", "Hoa"]

result = [name.upper() for name in students]

print(result)
```

---

## Lọc file Python

```python
files = ["main.py", "README.md", "app.py", "data.json"]

python_files = [file for file in files if file.endswith(".py")]

print(python_files)
```

Kết quả:

```text
['main.py', 'app.py']
```

---

## Bình phương các số chẵn

```python
numbers = range(10)

result = [n**2 for n in numbers if n % 2 == 0]

print(result)
```

Kết quả:

```text
[0, 4, 16, 36, 64]
```

---

# 19. Những lỗi thường gặp

## Lỗi 1: Nhầm vị trí của `if`

Sai:

```python
numbers = [
    if x % 2 == 0
    x
    for x in range(10)
]
```

Đúng:

```python
numbers = [x for x in range(10) if x % 2 == 0]
```

---

## Lỗi 2: Nhầm giữa `if` lọc và `if...else`

Lọc:

```python
[x for x in numbers if x > 0]
```

Chọn giá trị:

```python
["Dương" if x > 0 else "Âm" for x in numbers]
```

---

## Lỗi 3: Lồng quá nhiều vòng lặp

Sai:

```python
result = [... for a in ... for b in ... for c in ... if ...]
```

Khó đọc và khó bảo trì.

---

# 20. So sánh `for` và List Comprehension

| Tiêu chí                  | `for` | List Comprehension |
| ------------------------- | ----- | ------------------ |
| Dễ đọc với logic đơn giản | ⭐⭐⭐   | ⭐⭐⭐⭐⭐              |
| Logic phức tạp            | ⭐⭐⭐⭐⭐ | ⭐⭐                 |
| Tạo List mới              | ⭐⭐⭐   | ⭐⭐⭐⭐⭐              |
| Hiệu năng                 | Tốt   | Tốt hơn một chút   |
| Dễ debug                  | ⭐⭐⭐⭐⭐ | ⭐⭐                 |

---

# 21. Bài tập thực hành

## Bài 1

Tạo List:

```python
[1, 4, 9, 16, 25]
```

bằng List Comprehension.

---

## Bài 2

Cho:

```python
numbers = list(range(20))
```

Tạo List chỉ chứa số lẻ.

---

## Bài 3

Cho:

```python
words = ["python", "java", "golang"]
```

Tạo List:

```text
['PYTHON', 'JAVA', 'GOLANG']
```

---

## Bài 4

Cho:

```python
matrix = [[1, 2], [3, 4], [5, 6]]
```

Làm phẳng thành:

```text
[1, 2, 3, 4, 5, 6]
```

---

## Bài 5

Cho:

```python
students = [
    {"name": "An", "score": 8},
    {"name": "Lan", "score": 4},
    {"name": "Hoa", "score": 9},
]
```

Dùng List Comprehension để lấy danh sách tên của các học sinh có điểm từ **8 trở lên**.

Kết quả mong muốn:

```text
['An', 'Hoa']
```

---

# 22. Tổng kết

Trong buổi học này, bạn đã học:

* Khái niệm và cú pháp của **List Comprehension**.
* Chuyển đổi từ vòng lặp `for` sang List Comprehension.
* Sử dụng `if` để lọc và `if...else` để biến đổi dữ liệu.
* List Comprehension lồng nhau và kỹ thuật làm phẳng danh sách.
* Phạm vi biến (scope) trong List Comprehension.
* So sánh với `map()` và vòng lặp thông thường.
* Các nguyên tắc sử dụng trong dự án thực tế.

---

# Chuẩn bị cho Buổi 18

Ở **Buổi 18**, chúng ta sẽ học **Dict Comprehension**, bao gồm:

* Cú pháp tạo `dict` bằng Comprehension.
* Chuyển đổi từ `for` sang Dict Comprehension.
* Kết hợp với điều kiện `if`.
* Đảo ngược `key` và `value`.
* Xử lý dữ liệu thực tế như đếm tần suất, chuyển đổi cấu trúc dữ liệu.
* So sánh `Dict Comprehension` với `List Comprehension` và `dict()` thông thường.

Đây là bước cuối để bạn làm chủ nhóm **Comprehension** trong Python trước khi chuyển sang xử lý ngoại lệ (`Exception`) và dự án tổng hợp ở cuối giai đoạn Foundation.
