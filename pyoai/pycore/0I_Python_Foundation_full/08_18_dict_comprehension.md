# Giai đoạn 1 – Python Foundation

# Buổi 18. Dict Comprehension

> **Dict Comprehension** là phiên bản mở rộng của List Comprehension, giúp tạo **Dictionary** một cách ngắn gọn, rõ ràng và hiệu quả. Trong các dự án Python thực tế, Dict Comprehension được dùng rất nhiều khi xử lý dữ liệu, xây dựng bảng ánh xạ (mapping), cấu hình (configuration), thống kê và chuyển đổi dữ liệu.

---

# Mục tiêu

Sau buổi học này, bạn sẽ:

* Hiểu Dict Comprehension là gì.
* Biết cú pháp chuẩn.
* Chuyển từ vòng lặp `for` sang Dict Comprehension.
* Kết hợp với điều kiện `if`.
* Thực hiện chuyển đổi `key` và `value`.
* Kết hợp với các hàm như `zip()`, `enumerate()`.
* Hiểu các trường hợp nên và không nên sử dụng.
* Áp dụng vào các bài toán thực tế.

---

# 1. Dict Comprehension là gì?

Dict Comprehension là cách tạo **Dictionary** bằng một biểu thức duy nhất.

Ví dụ thông thường:

```python
numbers = {}

for i in range(5):
    numbers[i] = i * i

print(numbers)
```

Kết quả:

```text
{0: 0, 1: 1, 2: 4, 3: 9, 4: 16}
```

Có thể viết ngắn gọn:

```python
numbers = {i: i * i for i in range(5)}

print(numbers)
```

---

# 2. Cú pháp

```python
{key: value for item in iterable}
```

Ví dụ:

```python
squares = {x: x**2 for x in range(6)}

print(squares)
```

Kết quả:

```text
{
    0:0,
    1:1,
    2:4,
    3:9,
    4:16,
    5:25
}
```

---

# 3. Chuyển từ `for` sang Dict Comprehension

Thông thường:

```python
prices = {}

for item in ["Apple", "Banana", "Orange"]:
    prices[item] = 100
```

Dict Comprehension:

```python
prices = {item: 100 for item in ["Apple", "Banana", "Orange"]}

print(prices)
```

Kết quả:

```text
{
    'Apple':100,
    'Banana':100,
    'Orange':100
}
```

---

# 4. Kết hợp với `if`

Lấy bình phương của số chẵn.

```python
result = {x: x * x for x in range(10) if x % 2 == 0}

print(result)
```

Kết quả:

```text
{
    0:0,
    2:4,
    4:16,
    6:36,
    8:64
}
```

---

# 5. Điều kiện trong Value

```python
grades = {score: ("Đậu" if score >= 5 else "Rớt") for score in range(11)}

print(grades)
```

Kết quả:

```text
{
0:'Rớt',
1:'Rớt',
...
5:'Đậu',
...
10:'Đậu'
}
```

Lưu ý:

* `if` sau `for` → lọc dữ liệu.
* `if...else` trước `for` → quyết định giá trị.

---

# 6. Đảo ngược Key và Value

Cho:

```python
country_codes = {"VN": "Việt Nam", "JP": "Nhật Bản", "US": "Hoa Kỳ"}
```

Đảo ngược:

```python
reverse = {value: key for key, value in country_codes.items()}

print(reverse)
```

Kết quả:

```text
{
'Việt Nam':'VN',
'Nhật Bản':'JP',
'Hoa Kỳ':'US'
}
```

> **Lưu ý:** Nếu giá trị (`value`) bị trùng, các khóa trước sẽ bị ghi đè.

---

# 7. Dùng với `enumerate()`

```python
students = ["An", "Lan", "Hoa"]

mapping = {index: name for index, name in enumerate(students)}

print(mapping)
```

Kết quả:

```text
{
0:'An',
1:'Lan',
2:'Hoa'
}
```

---

# 8. Dùng với `zip()`

```python
names = ["An", "Lan", "Hoa"]

scores = [8, 9, 7]

result = {name: score for name, score in zip(names, scores)}

print(result)
```

Kết quả:

```text
{
'An':8,
'Lan':9,
'Hoa':7
}
```

---

# 9. Duyệt Dictionary

Cho:

```python
student = {"name": "An", "age": 20, "city": "Huế"}
```

Tạo Dictionary mới:

```python
upper_keys = {key.upper(): value for key, value in student.items()}

print(upper_keys)
```

Kết quả:

```text
{
'NAME':'An',
'AGE':20,
'CITY':'Huế'
}
```

---

# 10. Biến đổi Value

```python
prices = {"Apple": 100, "Orange": 200}

new_prices = {product: price * 1.1 for product, price in prices.items()}

print(new_prices)
```

Kết quả:

```text
{
'Apple':110.0,
'Orange':220.0
}
```

---

# 11. Lọc Dictionary

```python
students = {"An": 8, "Lan": 4, "Hoa": 9}

passed = {name: score for name, score in students.items() if score >= 5}

print(passed)
```

Kết quả:

```text
{
'An':8,
'Hoa':9
}
```

---

# 12. Dictionary lồng nhau

```python
matrix = {row: {col: row * col for col in range(3)} for row in range(3)}

print(matrix)
```

Kết quả:

```text
{
0:{0:0,1:0,2:0},
1:{0:0,1:1,2:2},
2:{0:0,1:2,2:4}
}
```

---

# 13. Dict Comprehension và Scope

```python
mapping = {x: x * x for x in range(5)}

print(x)
```

Kết quả:

```text
NameError
```

Giống List Comprehension, biến `x` không tồn tại bên ngoài.

---

# 14. Khi nào nên dùng?

Nên dùng khi:

* Tạo Dictionary mới.
* Chuyển đổi cấu trúc dữ liệu.
* Xây dựng bảng tra cứu (lookup table).
* Lọc dữ liệu.
* Ánh xạ (`mapping`) giữa hai tập dữ liệu.

---

# 15. Khi nào KHÔNG nên dùng?

Không nên:

```python
result = {
    user.id: calculate_salary(user, get_tax(user), get_bonus(user), get_allowance(user))
    for user in employees
}
```

Khó đọc.

Nên:

```python
result = {}

for user in employees:
    salary = calculate_salary(user, get_tax(user), get_bonus(user), get_allowance(user))

    result[user.id] = salary
```

---

# 16. So sánh Dict Comprehension và `dict()`

```python
pairs = [("A", 1), ("B", 2)]
```

Có thể:

```python
result = dict(pairs)
```

Hoặc:

```python
result = {key: value for key, value in pairs}
```

Nếu chỉ chuyển đổi trực tiếp, `dict()` đơn giản hơn.

Nếu cần biến đổi hoặc lọc dữ liệu, Dict Comprehension linh hoạt hơn.

---

# 17. Ví dụ thực tế

## Ví dụ 1: Đếm độ dài chuỗi

```python
words = ["python", "java", "golang"]

lengths = {word: len(word) for word in words}

print(lengths)
```

Kết quả:

```text
{
'python':6,
'java':4,
'golang':7
}
```

---

## Ví dụ 2: Chuyển điểm thành xếp loại

```python
scores = {"An": 8, "Lan": 4, "Hoa": 10}

grades = {name: ("Pass" if score >= 5 else "Fail") for name, score in scores.items()}

print(grades)
```

Kết quả:

```text
{
'An':'Pass',
'Lan':'Fail',
'Hoa':'Pass'
}
```

---

## Ví dụ 3: Tạo bảng ASCII

```python
ascii_table = {chr(code): code for code in range(65, 71)}

print(ascii_table)
```

Kết quả:

```text
{
'A':65,
'B':66,
'C':67,
'D':68,
'E':69,
'F':70
}
```

---

# 18. Những lỗi thường gặp

## Lỗi 1: Thiếu dấu `:`

Sai:

```python
{x for x in range(5)}
```

Đây là **Set Comprehension**, không phải Dict Comprehension.

Đúng:

```python
{x: x for x in range(5)}
```

---

## Lỗi 2: Quên `.items()`

Sai:

```python
student = {"An": 8}

{k: v for k, v in student}
```

Lỗi:

```text
ValueError
```

Đúng:

```python
{k: v for k, v in student.items()}
```

---

## Lỗi 3: Key bị trùng

```python
result = {len(word): word for word in ["A", "B", "CC"]}
```

Kết quả:

```text
{
1:'B',
2:'CC'
}
```

`'A'` bị ghi đè bởi `'B'` vì cùng khóa `1`.

---

# 19. So sánh các Comprehension

| Kiểu                | Kết quả    |
| ------------------- | ---------- |
| `[x for x in data]` | List       |
| `{x for x in data}` | Set        |
| `{k: v for ...}`    | Dictionary |
| `(x for x in data)` | Generator  |

Đây là bốn dạng **Comprehension / Expression** quan trọng trong Python.

---

# 20. Bài tập thực hành

## Bài 1

Tạo Dictionary:

```text
{
1:1,
2:4,
3:9,
4:16,
5:25
}
```

bằng Dict Comprehension.

---

## Bài 2

Cho:

```python
words = ["python", "java", "c++"]
```

Tạo Dictionary:

```text
{
'python':6,
'java':4,
'c++':3
}
```

---

## Bài 3

Cho:

```python
students = {"An": 8, "Lan": 4, "Hoa": 10}
```

Lọc ra các học sinh có điểm từ 8 trở lên.

---

## Bài 4

Cho:

```python
countries = {"VN": "Việt Nam", "JP": "Nhật Bản", "US": "Hoa Kỳ"}
```

Đảo ngược `key` và `value`.

---

## Bài 5

Cho:

```python
names = ["An", "Lan", "Hoa"]

scores = [8, 9, 10]
```

Dùng `zip()` và Dict Comprehension để tạo:

```text
{
'An':8,
'Lan':9,
'Hoa':10
}
```

---

# 21. Tổng kết

Trong buổi học này, bạn đã học:

* Khái niệm **Dict Comprehension**.
* Cú pháp chuẩn và cách chuyển từ vòng lặp `for`.
* Kết hợp với `if` và `if...else`.
* Sử dụng với `zip()`, `enumerate()`, `.items()`.
* Đảo ngược `key` và `value`.
* Các lỗi phổ biến và cách tránh.
* So sánh giữa Dict Comprehension với `dict()` và các dạng Comprehension khác.

Đến đây, bạn đã hoàn thành nhóm kiến thức về **Comprehension** trong Python:

* ✅ List Comprehension
* ✅ Dict Comprehension

Ở giai đoạn Intermediate, bạn sẽ tiếp tục học **Set Comprehension** và đặc biệt là **Generator Expression**, nền tảng cho lập trình hiệu năng cao.

---

# Chuẩn bị cho Buổi 19

Ở **Buổi 19**, chúng ta sẽ học **Exception (Xử lý ngoại lệ)** – một trong những kỹ năng quan trọng nhất của lập trình viên Python chuyên nghiệp.

Các nội dung sẽ bao gồm:

* Khái niệm Exception.
* `try`, `except`, `else`, `finally`.
* Bắt nhiều loại ngoại lệ.
* Tự tạo ngoại lệ với `raise`.
* Định nghĩa ngoại lệ tùy chỉnh (Custom Exception).
* Best Practices khi xử lý lỗi.
* Ứng dụng Exception trong các chương trình thực tế.

Đây là bước cuối cùng về ngôn ngữ Python trước khi bước vào **Buổi 20 – Mini Project**, nơi bạn sẽ tổng hợp toàn bộ kiến thức của Giai đoạn 1 để xây dựng một ứng dụng Python hoàn chỉnh.
