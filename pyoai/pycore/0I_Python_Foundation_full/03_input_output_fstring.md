# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 3: Input/Output Chuyên Sâu – Làm Chủ `print()`, `input()` và f-string

> **Mục tiêu buổi học**
> 
> Sau buổi học này, bạn sẽ:
> 
> - Hiểu sâu cách Python xuất dữ liệu ra màn hình.
> - Thành thạo mọi tham số của `print()`.
> - Thành thạo `input()`.
> - Thành thạo f-string (chuẩn hiện đại).
> - Biết định dạng số, chuỗi, ngày tháng.
> - Viết chương trình giao tiếp với người dùng chuyên nghiệp.
> - Biết các lỗi thường gặp.

---

# 1. Input và Output là gì?

Mọi chương trình đều có mô hình rất đơn giản:

```text-x-trilium-auto
        Người dùng
             │
          Input
             │
             ▼
      Chương trình Python
             │
          Output
             │
             ▼
        Kết quả
```

Ví dụ:

```text-x-trilium-auto
Nhập tên
↓

Garden

↓

Xin chào Garden
```

---

# 2. Hàm `print()`

Cú pháp:

```text-x-trilium-auto
print(*objects, sep=' ', end='\n', file=None, flush=False)
```

Đừng lo nếu bạn chưa hiểu hết. Chúng ta sẽ học từng tham số.

---

# 3. In một giá trị

```text-x-trilium-auto
print("Hello")
```

Kết quả

```text-x-trilium-auto
Hello
```

---

## In số

```text-x-trilium-auto
print(100)
```

```text-x-trilium-auto
100
```

---

## In số thực

```text-x-trilium-auto
print(3.14)
```

---

## In Boolean

```text-x-trilium-auto
print(True)
print(False)
```

---

# 4. In nhiều giá trị

```text-x-trilium-auto
print("Python", 2026, True)
```

Kết quả

```text-x-trilium-auto
Python 2026 True
```

Python tự động chèn khoảng trắng giữa các giá trị.

---

# 5. Tham số `sep`

Mặc định

```text-x-trilium-auto
print("A", "B", "C")
```

Kết quả

```text-x-trilium-auto
A B C
```

Vì:

```text-x-trilium-auto
sep=" "
```

---

Có thể thay đổi:

```text-x-trilium-auto
print("A", "B", "C", sep="-")
```

```text-x-trilium-auto
A-B-C
```

---

Ví dụ

```text-x-trilium-auto
print("2026", "07", "03", sep="/")
```

```text-x-trilium-auto
2026/07/03
```

---

Địa chỉ IP

```text-x-trilium-auto
print(192,168,1,1, sep=".")
```

```text-x-trilium-auto
192.168.1.1
```

---

Đường dẫn

```text-x-trilium-auto
print("home","garden","python", sep="/")
```

```text-x-trilium-auto
home/garden/python
```

---

# 6. Tham số `end`

Mặc định

```text-x-trilium-auto
print("Hello")
print("Python")
```

Kết quả

```text-x-trilium-auto
Hello
Python
```

Vì

```text-x-trilium-auto
end="\n"
```

---

Thay đổi

```text-x-trilium-auto
print("Hello", end=" ")
print("Python")
```

```text-x-trilium-auto
Hello Python
```

---

Ví dụ

```text-x-trilium-auto
print("Loading", end="...")
print("Done")
```

```text-x-trilium-auto
Loading...Done
```

---

# 7. Kết hợp `sep` và `end`

```text-x-trilium-auto
print(1,2,3, sep="-", end=" <END>\n")
```

```text-x-trilium-auto
1-2-3 <END>
```

---

# 8. Xuống dòng

```text-x-trilium-auto
print("Xin chào\nPython")
```

```text-x-trilium-auto
Xin chào
Python
```

---

# 9. Ký tự Escape

## `\n`

Xuống dòng

```text-x-trilium-auto
print("A\nB")
```

---

## `\t`

Tab

```text-x-trilium-auto
print("Tên\tTuổi")
```

```text-x-trilium-auto
Tên     Tuổi
```

---

## `\\`

In dấu `\`

```text-x-trilium-auto
print("C:\\Users\\Garden")
```

---

## `\"`

```text-x-trilium-auto
print("\"Python\"")
```

```text-x-trilium-auto
"Python"
```

---

# 10. Chuỗi nhiều dòng

```text-x-trilium-auto
print("""
Python
Java
C++
Rust
""")
```

---

# 11. Hàm `input()`

Cú pháp

```text-x-trilium-auto
input(prompt)
```

Ví dụ

```text-x-trilium-auto
name = input("Tên: ")
```

Người dùng nhập

```text-x-trilium-auto
Garden
```

Biến

```text-x-trilium-auto
name
```

sẽ có giá trị

```text-x-trilium-auto
Garden
```

---

# 12. Điều rất quan trọng

`input()` luôn trả về **chuỗi (**`**str**`**)**.

Ví dụ

```text-x-trilium-auto
age = input("Tuổi: ")

print(type(age))
```

Kết quả

```text-x-trilium-auto
<class 'str'>
```

---

Sai

```text-x-trilium-auto
age = input("Tuổi: ")

print(age + 1)
```

```text-x-trilium-auto
TypeError
```

Đúng

```text-x-trilium-auto
age = int(input("Tuổi: "))

print(age + 1)
```

---

# 13. Nhập nhiều dữ liệu

Ví dụ

```text-x-trilium-auto
first_name = input("Họ: ")
last_name = input("Tên: ")
```

---

# 14. Nhập nhiều giá trị trên một dòng

Ví dụ

Người dùng nhập

```text-x-trilium-auto
10 20
```

Code

```text-x-trilium-auto
a, b = input("Nhập hai số: ").split()

print(a)
print(b)
```

Kết quả

```text-x-trilium-auto
10

20
```

Muốn thành số

```text-x-trilium-auto
a, b = map(int, input().split())
```

Đây là cách lập trình viên Python thường dùng.

---

# 15. f-string

Đây là cách hiện đại nhất.

Ví dụ

```text-x-trilium-auto
name = "Garden"

print(f"Xin chào {name}")
```

```text-x-trilium-auto
Xin chào Garden
```

---

Nhiều biến

```text-x-trilium-auto
name = "Garden"
age = 20

print(f"{name} {age}")
```

---

Biểu thức

```text-x-trilium-auto
a = 10
b = 20

print(f"Tổng = {a+b}")
```

```text-x-trilium-auto
Tổng = 30
```

---

# 16. Định dạng số

Ví dụ

```text-x-trilium-auto
pi = 3.1415926535

print(f"{pi:.2f}")
```

```text-x-trilium-auto
3.14
```

---

3 số sau dấu phẩy

```text-x-trilium-auto
print(f"{pi:.3f}")
```

```text-x-trilium-auto
3.142
```

---

# 17. Phân tách hàng nghìn

```text-x-trilium-auto
money = 150000000

print(f"{money:,}")
```

```text-x-trilium-auto
150,000,000
```

---

# 18. Căn lề

Trái

```text-x-trilium-auto
print(f"|{'Python':<10}|")
```

```text-x-trilium-auto
|Python    |
```

---

Phải

```text-x-trilium-auto
print(f"|{'Python':>10}|")
```

```text-x-trilium-auto
|    Python|
```

---

Giữa

```text-x-trilium-auto
print(f"|{'Python':^10}|")
```

```text-x-trilium-auto
|  Python  |
```

---

# 19. Hiển thị phần trăm

```text-x-trilium-auto
score = 0.86

print(f"{score:.1%}")
```

```text-x-trilium-auto
86.0%
```

---

# 20. In bảng

```text-x-trilium-auto
name = "An"
age = 20
score = 9.5

print(f"{'Tên':<10}: {name}")
print(f"{'Tuổi':<10}: {age}")
print(f"{'Điểm':<10}: {score}")
```

Kết quả

```text-x-trilium-auto
Tên       : An
Tuổi      : 20
Điểm      : 9.5
```

---

# 21. Ví dụ thực tế

## Hóa đơn

```text-x-trilium-auto
product = input("Tên sản phẩm: ")
price = float(input("Giá: "))
quantity = int(input("Số lượng: "))

total = price * quantity

print()

print("====== HÓA ĐƠN ======")
print(f"Sản phẩm : {product}")
print(f"Giá      : {price:,.0f} VNĐ")
print(f"Số lượng : {quantity}")
print(f"Tổng tiền: {total:,.0f} VNĐ")
```

Ví dụ

```text-x-trilium-auto
Tên sản phẩm: Chuột Logitech
Giá: 350000
Số lượng: 2
```

Kết quả

```text-x-trilium-auto
====== HÓA ĐƠN ======

Sản phẩm : Chuột Logitech
Giá      : 350,000 VNĐ
Số lượng : 2
Tổng tiền: 700,000 VNĐ
```

---

# 22. Các lỗi phổ biến

## Lỗi 1

```text-x-trilium-auto
age = input()

print(age + 1)
```

Sai vì `age` là chuỗi.

---

## Lỗi 2

```text-x-trilium-auto
print("Tuổi: " + 20)
```

Sai.

Đúng

```text-x-trilium-auto
print("Tuổi:",20)
```

hoặc

```text-x-trilium-auto
print(f"Tuổi: {20}")
```

---

## Lỗi 3

```text-x-trilium-auto
name = input

print(name)
```

Quên dấu ngoặc `()`.

Đúng

```text-x-trilium-auto
name = input()
```

---

# 23. Bài tập thực hành

## Bài 1

Nhập:

- Họ tên
- Tuổi

In:

```text-x-trilium-auto
Xin chào <Tên>, bạn <Tuổi> tuổi.
```

---

## Bài 2

Nhập chiều dài và chiều rộng.

Tính diện tích hình chữ nhật.

---

## Bài 3

Nhập:

- Tên sản phẩm
- Giá
- Giảm giá %

In số tiền sau giảm.

---

## Bài 4

Nhập 3 số nguyên trên **một dòng**.

Ví dụ

```text-x-trilium-auto
10 20 30
```

In:

```text-x-trilium-auto
Tổng

Trung bình
```

---

## Bài 5

Nhập:

```text-x-trilium-auto
Ngày

Tháng

Năm
```

In:

```text-x-trilium-auto
03/07/2026
```

Sử dụng `sep="/"`.

---

## Bài 6

In bảng sau bằng f-string:

```text-x-trilium-auto
==============================
Tên        Tuổi      Điểm
An         20        8.5
Bình       21        9.0
Cường      19        7.8
==============================
```

Yêu cầu các cột thẳng hàng bằng cách dùng căn lề (`<`, `>`, `^`).

---

# Mini Project: Máy tính tính tiền quán cà phê ☕

Viết chương trình:

1. Nhập:
  - Tên khách hàng
  - Tên đồ uống
  - Giá
  - Số lượng
2. Tính:
  - Thành tiền
  - Thuế VAT 8%
  - Tổng thanh toán
3. In hóa đơn đẹp:

```text-x-trilium-auto
==============================
         HÓA ĐƠN
==============================
Khách hàng : Garden
Đồ uống    : Cà phê sữa
Giá        : 35,000 VNĐ
Số lượng   : 2
Thành tiền : 70,000 VNĐ
VAT (8%)   : 5,600 VNĐ
Tổng cộng  : 75,600 VNĐ
==============================
```

---

# Tổng kết buổi 3

Hôm nay bạn đã học được:

- ✅ Cách hoạt động của Input và Output.
- ✅ Sử dụng `print()` với các tham số `sep` và `end`.
- ✅ Các ký tự escape (`\n`, `\t`, `\\`, `\"`).
- ✅ Sử dụng `input()` và hiểu rằng luôn trả về `str`.
- ✅ Nhập nhiều giá trị bằng `split()` và `map()`.
- ✅ Thành thạo **f-string** để chèn biến và biểu thức.
- ✅ Định dạng số thập phân, phần trăm, phân tách hàng nghìn và căn lề.
- ✅ Xây dựng các chương trình tương tác với người dùng theo phong cách chuyên nghiệp.

### Chuẩn bị cho Buổi 4

Ở buổi tiếp theo, chúng ta sẽ học **toàn diện về toán tử trong Python**: toán tử số học, gán, so sánh, logic, membership (`in`, `not in`), identity (`is`, `is not`), thứ tự ưu tiên toán tử, toán tử ba ngôi (conditional expression), cùng nhiều ví dụ thực tế và bài tập để hình thành tư duy giải quyết bài toán bằng biểu thức Python.
