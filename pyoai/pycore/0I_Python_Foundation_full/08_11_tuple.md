# Giai đoạn 1 – Python Foundation

# Buổi 11. Tuple (Bộ dữ liệu bất biến)

> Sau khi học **List**, bạn sẽ thấy `Tuple` có cú pháp gần như giống hệt. Tuy nhiên, đừng nghĩ Tuple là "List nhưng không sửa được". Trong Python, Tuple có **vai trò rất quan trọng** trong thiết kế API, trả về nhiều giá trị, làm khóa (`key`) của Dictionary và tối ưu hiệu năng.

---

# Mục tiêu

Sau buổi học này, bạn sẽ:

* Hiểu Tuple là gì.
* Phân biệt Tuple và List.
* Biết khi nào nên dùng Tuple.
* Hiểu Immutable.
* Truy cập phần tử.
* Slicing Tuple.
* Duyệt Tuple.
* Packing và Unpacking.
* Multiple Assignment.
* Hiểu vì sao Tuple thường xuất hiện trong code Python chuyên nghiệp.

---

# 1. Tuple là gì?

Tuple là một **collection có thứ tự (ordered)** giống List nhưng **không thể thay đổi (immutable)** sau khi được tạo.

Ví dụ:

```python
numbers = (10, 20, 30)
```

Kiểm tra kiểu dữ liệu:

```python
numbers = (10, 20, 30)

print(type(numbers))
```

Kết quả:

```text
<class 'tuple'>
```

---

# 2. Tạo Tuple

## Cách 1

```python
colors = ("red", "green", "blue")
```

---

## Cách 2

Có thể bỏ dấu ngoặc.

```python
colors = "red", "green", "blue"
```

Python vẫn hiểu đây là Tuple.

---

## Tuple rỗng

```python
empty = ()

print(type(empty))
```

```text
<class 'tuple'>
```

---

# 3. Tuple một phần tử

Đây là lỗi rất nhiều người mới học gặp phải.

Sai:

```python
number = 10

print(type(number))
```

Kết quả:

```text
<class 'int'>
```

Đúng:

```python
number = (10,)

print(type(number))
```

Kết quả:

```text
<class 'tuple'>
```

> **Lưu ý:** Dấu phẩy (`,`) mới là yếu tố quyết định tạo Tuple, không phải dấu ngoặc.

---

# 4. Truy cập phần tử

Giống List.

```python
colors = ("red", "green", "blue")

print(colors[0])
```

Kết quả:

```text
red
```

---

```python
print(colors[2])
```

```text
blue
```

---

# 5. Index âm

```python
print(colors[-1])
```

```text
blue
```

---

```python
print(colors[-2])
```

```text
green
```

---

# 6. Độ dài Tuple

```python
numbers = (10, 20, 30)

print(len(numbers))
```

Kết quả:

```text
3
```

---

# 7. Immutable

Tuple không thể thay đổi.

Ví dụ:

```python
numbers = (10, 20, 30)

numbers[0] = 100
```

Lỗi:

```text
TypeError:
'tuple' object does not support item assignment
```

---

Không thể:

* Thêm phần tử.
* Xóa phần tử.
* Sửa phần tử.

---

# 8. Duyệt Tuple

```python
numbers = (10, 20, 30)

for item in numbers:
    print(item)
```

Kết quả:

```text
10
20
30
```

---

Hoặc:

```python
for i in range(len(numbers)):
    print(i, numbers[i])
```

---

# 9. Slicing

```python
numbers = (10, 20, 30, 40, 50)

print(numbers[1:4])
```

```text
(20, 30, 40)
```

---

```python
print(numbers[::-1])
```

```text
(50, 40, 30, 20, 10)
```

---

# 10. Toán tử `+`

```python
a = (1, 2)

b = (3, 4)

print(a + b)
```

Kết quả:

```text
(1, 2, 3, 4)
```

---

# 11. Toán tử `*`

```python
print((1, 2) * 3)
```

Kết quả:

```text
(1, 2, 1, 2, 1, 2)
```

---

# 12. Toán tử `in`

```python
numbers = (10, 20, 30)

print(20 in numbers)
```

```text
True
```

---

```python
print(100 in numbers)
```

```text
False
```

---

# 13. Packing

Python tự gom nhiều giá trị thành Tuple.

```python
point = 10, 20

print(point)
```

Kết quả:

```text
(10, 20)
```

Đây gọi là **Tuple Packing**.

---

# 14. Unpacking

```python
point = (10, 20)

x, y = point

print(x)
print(y)
```

Kết quả:

```text
10
20
```

---

# 15. Multiple Assignment

```python
name, age, city = ("An", 20, "Hà Nội")

print(name)
print(age)
print(city)
```

Kết quả:

```text
An
20
Hà Nội
```

---

# 16. Hoán đổi biến

Trong nhiều ngôn ngữ:

```text
temp = a
a = b
b = temp
```

Python:

```python
a = 10
b = 20

a, b = b, a

print(a, b)
```

Kết quả:

```text
20 10
```

Đây là một trong những tính năng đặc trưng của Python.

---

# 17. Trả về nhiều giá trị từ hàm

```python
def get_user():
    return "An", 20


name, age = get_user()

print(name)
print(age)
```

Kết quả:

```text
An
20
```

Thực chất hàm trả về **một Tuple**.

---

# 18. Tuple lồng nhau

```python
matrix = ((1, 2), (3, 4))

print(matrix[1][0])
```

Kết quả:

```text
3
```

---

# 19. Tuple chứa List

Tuple là bất biến, nhưng phần tử bên trong có thể là đối tượng thay đổi được.

```python
data = ([1, 2], [3, 4])

data[0].append(99)

print(data)
```

Kết quả:

```text
([1, 2, 99], [3, 4])
```

Không thể:

```python
data[0] = [0]
```

Nhưng có thể thay đổi nội dung của List bên trong.

---

# 20. So sánh Tuple và List

| Tiêu chí                    | List              | Tuple                             |
| --------------------------- | ----------------- | --------------------------------- |
| Thay đổi được               | ✅                 | ❌                                 |
| Có thứ tự                   | ✅                 | ✅                                 |
| Truy cập bằng index         | ✅                 | ✅                                 |
| Hỗ trợ slicing              | ✅                 | ✅                                 |
| Dùng làm key của Dictionary | ❌                 | ✅ (nếu các phần tử cũng bất biến) |
| Hiệu năng                   | Chậm hơn một chút | Nhanh hơn một chút                |
| Bộ nhớ                      | Nhiều hơn         | Ít hơn                            |

---

# 21. Khi nào dùng Tuple?

Nên dùng Tuple khi dữ liệu:

* Không thay đổi sau khi tạo.
* Là hằng số.
* Là tọa độ `(x, y)`.
* Là giá trị trả về của hàm.
* Là khóa của Dictionary.
* Cần thể hiện rằng dữ liệu **không nên bị sửa đổi**.

Ví dụ:

```python
DAYS = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)
```

---

# 22. Ví dụ thực tế

## Tọa độ

```python
point = (120, 250)

x, y = point

print(f"Tọa độ: ({x}, {y})")
```

---

## Hàm trả về nhiều giá trị

```python
def calculate(a, b):
    return a + b, a - b, a * b


add, sub, mul = calculate(8, 4)

print(add)
print(sub)
print(mul)
```

Kết quả:

```text
12
4
32
```

---

# 23. Những lỗi thường gặp

## Quên dấu phẩy

Sai:

```python
value = 100
```

Đúng:

```python
value = (100,)
```

---

## Cố sửa Tuple

Sai:

```python
data = (1, 2, 3)

data[0] = 10
```

Lỗi:

```text
TypeError
```

---

## Unpacking sai số lượng

Sai:

```python
point = (10, 20)

x, y, z = point
```

Lỗi:

```text
ValueError:
not enough values to unpack
```

---

# 24. Bài tập thực hành

### Bài 1

Tạo Tuple gồm 5 số nguyên và:

* In phần tử đầu tiên.
* In phần tử cuối cùng.
* In độ dài của Tuple.

---

### Bài 2

Cho:

```python
point = (15, 30)
```

Unpack thành hai biến `x`, `y` và in ra.

---

### Bài 3

Viết hàm:

```python
def rectangle(width, height): ...
```

Hàm trả về:

* Diện tích.
* Chu vi.

Sử dụng Tuple để trả về nhiều giá trị.

---

### Bài 4

Cho Tuple:

```python
numbers = (5, 10, 15, 20, 25)
```

* In ba phần tử đầu.
* In ba phần tử cuối.
* In Tuple đảo ngược.

---

### Bài 5

Hoán đổi giá trị của hai biến bằng Tuple.

Ví dụ:

```python
a = 100
b = 200
```

Kết quả:

```text
a = 200
b = 100
```

---

# Tổng kết

Trong buổi học này, bạn đã học:

* Khái niệm và đặc điểm của `tuple`.
* Sự khác biệt giữa `tuple` và `list`.
* Tính **immutable** của Tuple.
* Truy cập phần tử, slicing và duyệt Tuple.
* Tuple Packing và Tuple Unpacking.
* Multiple Assignment và hoán đổi biến.
* Hàm trả về nhiều giá trị bằng Tuple.
* Các tình huống nên sử dụng Tuple trong lập trình thực tế.

## Chuẩn bị cho buổi 12

Ở **Buổi 12**, chúng ta sẽ học **Set (Tập hợp)**, tìm hiểu về:

* Tập hợp không có thứ tự.
* Loại bỏ phần tử trùng lặp.
* Các phép toán tập hợp (hợp, giao, hiệu, đối xứng).
* Ứng dụng của `set` trong việc tối ưu tìm kiếm và xử lý dữ liệu lớn. Đây là một kiểu dữ liệu rất mạnh mà nhiều lập trình viên mới thường bỏ qua.
