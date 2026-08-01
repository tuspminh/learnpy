# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 4: Làm chủ Toán tử (Operators) trong Python

> **Mục tiêu buổi học**
> 
> Sau buổi học này, bạn sẽ:
> 
> - Hiểu bản chất của toán tử trong Python.
> - Thành thạo toàn bộ các loại toán tử.
> - Biết thứ tự ưu tiên của toán tử.
> - Hiểu sự khác nhau giữa `==` và `is`.
> - Hiểu `in`, `not in`.
> - Thành thạo các toán tử gán mở rộng.
> - Biết viết biểu thức Python chuyên nghiệp.
> - Áp dụng vào các bài toán thực tế.

---

# 1. Toán tử là gì?

Toán tử (Operator) là ký hiệu dùng để **thực hiện một phép toán trên một hoặc nhiều toán hạng (operand)**.

Ví dụ:

```text-x-trilium-auto
a = 10
b = 20

c = a + b
```

Trong đó:

```text-x-trilium-auto
a + b

a  -> toán hạng

+  -> toán tử

b  -> toán hạng
```

---

# 2. Các nhóm toán tử trong Python

Python có 7 nhóm toán tử chính:

| Nhóm | Ví dụ |
| --- | --- |
| Toán tử số học | `+ - * / // % **` |
| Toán tử gán | `= += -= *= /= ...` |
| Toán tử so sánh | `== != > < >= <=` |
| Toán tử logic | `and or not` |
| Toán tử thành viên | `in`, `not in` |
| Toán tử định danh | `is`, `is not` |
| Toán tử điều kiện | `x if condition else y` |

---

# 3. Toán tử số học

## Phép cộng

```text-x-trilium-auto
a = 10
b = 5

print(a + b)
```

Kết quả:

```text-x-trilium-auto
15
```

---

## Phép trừ

```text-x-trilium-auto
print(10 - 3)
```

```text-x-trilium-auto
7
```

---

## Phép nhân

```text-x-trilium-auto
print(5 * 4)
```

```text-x-trilium-auto
20
```

---

## Phép chia

```text-x-trilium-auto
print(10 / 4)
```

Kết quả:

```text-x-trilium-auto
2.5
```

Lưu ý:

`/` luôn trả về `float`.

---

## Chia lấy phần nguyên

```text-x-trilium-auto
print(10 // 4)
```

```text-x-trilium-auto
2
```

---

## Chia lấy dư

```text-x-trilium-auto
print(10 % 4)
```

```text-x-trilium-auto
2
```

Ứng dụng:

Kiểm tra số chẵn:

```text-x-trilium-auto
number = 20

print(number % 2 == 0)
```

```text-x-trilium-auto
True
```

---

## Lũy thừa

```text-x-trilium-auto
print(2 ** 5)
```

```text-x-trilium-auto
32
```

---

# 4. Ví dụ thực tế

Giả sử một cửa hàng bán:

```text-x-trilium-auto
price = 35000
quantity = 3

total = price * quantity

print(total)
```

```text-x-trilium-auto
105000
```

---

# 5. Toán tử gán

## Gán thông thường

```text-x-trilium-auto
x = 10
```

---

## Cộng rồi gán

```text-x-trilium-auto
x = 10

x += 5

print(x)
```

```text-x-trilium-auto
15
```

---

## Trừ rồi gán

```text-x-trilium-auto
x = 20

x -= 8
```

---

## Nhân rồi gán

```text-x-trilium-auto
x *= 3
```

---

## Chia rồi gán

```text-x-trilium-auto
x /= 2
```

---

## Chia nguyên rồi gán

```text-x-trilium-auto
x //= 2
```

---

## Chia dư rồi gán

```text-x-trilium-auto
x %= 3
```

---

## Lũy thừa rồi gán

```text-x-trilium-auto
x **= 2
```

---

# 6. Toán tử so sánh

```text-x-trilium-auto
10 == 10
```

```text-x-trilium-auto
True
```

---

```text-x-trilium-auto
10 != 20
```

```text-x-trilium-auto
True
```

---

```text-x-trilium-auto
5 > 3
```

```text-x-trilium-auto
True
```

---

```text-x-trilium-auto
5 < 3
```

```text-x-trilium-auto
False
```

---

```text-x-trilium-auto
5 >= 5
```

```text-x-trilium-auto
True
```

---

```text-x-trilium-auto
5 <= 10
```

```text-x-trilium-auto
True
```

---

# 7. Ứng dụng

```text-x-trilium-auto
age = 18

print(age >= 18)
```

```text-x-trilium-auto
True
```

---

# 8. Toán tử logic

Có ba toán tử:

```text-x-trilium-auto
and

or

not
```

---

## AND

```text-x-trilium-auto
True and True
```

```text-x-trilium-auto
True
```

```text-x-trilium-auto
True and False
```

```text-x-trilium-auto
False
```

Ví dụ:

```text-x-trilium-auto
age = 20
has_ticket = True

print(age >= 18 and has_ticket)
```

```text-x-trilium-auto
True
```

Chỉ khi **tất cả điều kiện đúng** thì kết quả mới đúng.

---

## OR

```text-x-trilium-auto
False or True
```

```text-x-trilium-auto
True
```

Ví dụ:

```text-x-trilium-auto
is_admin = False
is_teacher = True

print(is_admin or is_teacher)
```

```text-x-trilium-auto
True
```

Chỉ cần **một điều kiện đúng**.

---

## NOT

```text-x-trilium-auto
not True
```

```text-x-trilium-auto
False
```

Ví dụ:

```text-x-trilium-auto
is_login = False

print(not is_login)
```

```text-x-trilium-auto
True
```

---

# 9. Short-Circuit Evaluation

Python **không luôn đánh giá toàn bộ biểu thức**.

Ví dụ:

```text-x-trilium-auto
False and print("Hello")
```

Kết quả:

Không in gì cả.

Vì `False and ...` chắc chắn là `False`, nên Python không cần đánh giá phần còn lại.

Tương tự:

```text-x-trilium-auto
True or print("Hello")
```

Cũng không in gì.

Đây gọi là **Short-Circuit Evaluation**, giúp chương trình chạy nhanh hơn và tránh một số lỗi.

---

# 10. Toán tử thành viên

## `in`

```text-x-trilium-auto
"Py" in "Python"
```

```text-x-trilium-auto
True
```

---

```text-x-trilium-auto
3 in [1, 2, 3]
```

```text-x-trilium-auto
True
```

---

```text-x-trilium-auto
10 in [1, 2, 3]
```

```text-x-trilium-auto
False
```

---

## `not in`

```text-x-trilium-auto
5 not in [1, 2, 3]
```

```text-x-trilium-auto
True
```

---

# 11. Ví dụ thực tế

Kiểm tra email:

```text-x-trilium-auto
email = input("Email: ")

print("@" in email)
```

Nếu kết quả là `False`, địa chỉ email chắc chắn không hợp lệ.

---

# 12. Toán tử định danh

Đây là phần rất nhiều người mới học nhầm.

## `==`

So sánh **giá trị**.

```text-x-trilium-auto
a = [1, 2, 3]
b = [1, 2, 3]

print(a == b)
```

```text-x-trilium-auto
True
```

Vì hai danh sách có cùng giá trị.

---

## `is`

So sánh **hai biến có cùng tham chiếu đến một object hay không**.

```text-x-trilium-auto
print(a is b)
```

```text-x-trilium-auto
False
```

Hai danh sách giống nhau nhưng là hai object khác nhau.

---

Ví dụ:

```text-x-trilium-auto
a = [1, 2]
b = a

print(a is b)
```

```text-x-trilium-auto
True
```

Vì `a` và `b` cùng tham chiếu tới một object.

---

> **Quy tắc quan trọng**
> 
> - Dùng `==` để so sánh giá trị.
> - Dùng `is` để kiểm tra cùng một object (ví dụ với `None`).

Ví dụ đúng:

```text-x-trilium-auto
result = None

if result is None:
    print("Chưa có kết quả")
```

Không nên viết:

```text-x-trilium-auto
if result == None:
    ...
```

---

# 13. Toán tử điều kiện (Conditional Expression)

Viết ngắn gọn:

```text-x-trilium-auto
age = 20

status = "Người lớn" if age >= 18 else "Trẻ em"

print(status)
```

Kết quả:

```text-x-trilium-auto
Người lớn
```

Đây còn gọi là **ternary operator** trong nhiều ngôn ngữ.

---

# 14. Thứ tự ưu tiên toán tử

Ví dụ:

```text-x-trilium-auto
print(2 + 3 * 4)
```

Kết quả:

```text-x-trilium-auto
14
```

Không phải:

```text-x-trilium-auto
20
```

Vì phép nhân thực hiện trước.

---

Nếu muốn cộng trước:

```text-x-trilium-auto
print((2 + 3) * 4)
```

```text-x-trilium-auto
20
```

---

Thứ tự ưu tiên (từ cao xuống thấp):

1. `()`
2. `**`
3. `* / // %`
4. `+ -`
5. So sánh (`==`, `<`, `>`, ...)
6. `not`
7. `and`
8. `or`

Khi biểu thức phức tạp, hãy dùng dấu ngoặc để mã nguồn dễ đọc hơn.

---

# 15. Ví dụ thực tế

Tính tiền sau giảm giá:

```text-x-trilium-auto
price = 500000
discount = 15

final_price = price * (100 - discount) / 100

print(f"Giá sau giảm: {final_price:,.0f} VNĐ")
```

Kết quả:

```text-x-trilium-auto
Giá sau giảm: 425,000 VNĐ
```

---

# 16. Các lỗi thường gặp

## Lỗi 1: Nhầm `=` và `==`

Sai:

```text-x-trilium-auto
if age = 18:
    print("Đủ tuổi")
```

Đúng:

```text-x-trilium-auto
if age == 18:
    print("Đủ tuổi")
```

`=` là gán, `==` là so sánh.

---

## Lỗi 2: Dùng `is` để so sánh số hoặc chuỗi

Không nên:

```text-x-trilium-auto
a = 1000
b = 1000

print(a is b)
```

Kết quả có thể khác nhau tùy cách Python quản lý bộ nhớ.

Nên dùng:

```text-x-trilium-auto
print(a == b)
```

---

## Lỗi 3: Quên ép kiểu

```text-x-trilium-auto
age = input("Tuổi: ")

print(age >= 18)
```

Sai vì `age` là `str`.

Đúng:

```text-x-trilium-auto
age = int(input("Tuổi: "))

print(age >= 18)
```

---

# 17. Bài tập thực hành

### Bài 1

Nhập hai số nguyên và in:

- Tổng
- Hiệu
- Tích
- Thương
- Chia lấy dư
- Lũy thừa (`a` mũ `b`)

---

### Bài 2

Nhập một số nguyên.

Kiểm tra số đó là **chẵn hay lẻ**.

---

### Bài 3

Nhập điểm trung bình.

In:

- "Đạt" nếu điểm từ 5 trở lên.
- "Chưa đạt" nếu nhỏ hơn 5.

*Gợi ý:* Dùng toán tử điều kiện.

---

### Bài 4

Nhập email.

Kiểm tra xem email có chứa ký tự `@` hay không bằng toán tử `in`.

---

### Bài 5

Nhập giá sản phẩm và phần trăm giảm giá.

Tính giá sau giảm.

---

### Bài 6

Cho:

```text-x-trilium-auto
numbers = [10, 20, 30, 40, 50]
```

Kiểm tra:

- `20 in numbers`
- `100 in numbers`
- `40 not in numbers`

Giải thích kết quả.

---

### Bài 7

Tạo hai danh sách có cùng nội dung:

```text-x-trilium-auto
a = [1, 2, 3]
b = [1, 2, 3]
```

In kết quả của:

```text-x-trilium-auto
print(a == b)
print(a is b)
```

Sau đó gán:

```text-x-trilium-auto
b = a
```

Và in lại hai biểu thức trên. Giải thích sự khác nhau.

---

# Mini Project: Máy tính tính lương nhân viên

Viết chương trình:

1. Nhập:
  - Tên nhân viên
  - Lương theo giờ
  - Số giờ làm việc
  - Thưởng
  - Thuế (%)
2. Tính:
  - Lương cơ bản = Lương theo giờ × Số giờ
  - Tổng thu nhập = Lương cơ bản + Thưởng
  - Thuế phải nộp
  - Lương thực nhận
3. In kết quả theo định dạng đẹp:

```text-x-trilium-auto
=================================
        BẢNG LƯƠNG
=================================
Nhân viên      : Nguyễn Văn A
Lương cơ bản   : 16,000,000 VNĐ
Thưởng         : 2,000,000 VNĐ
Tổng thu nhập  : 18,000,000 VNĐ
Thuế (10%)     : 1,800,000 VNĐ
Thực nhận      : 16,200,000 VNĐ
=================================
```

---

# Tổng kết buổi 4

Trong buổi học này, bạn đã nắm được:

- ✅ Toán tử số học.
- ✅ Toán tử gán và gán mở rộng.
- ✅ Toán tử so sánh.
- ✅ Toán tử logic (`and`, `or`, `not`) và **Short-Circuit Evaluation**.
- ✅ Toán tử thành viên (`in`, `not in`).
- ✅ Toán tử định danh (`is`, `is not`) và sự khác biệt với `==`.
- ✅ Toán tử điều kiện (conditional expression).
- ✅ Thứ tự ưu tiên của toán tử.
- ✅ Các lỗi phổ biến và cách tránh.

## Chuẩn bị cho Buổi 5

Ở buổi tiếp theo, chúng ta sẽ học **cấu trúc điều khiển** `**if**`**,** `**elif**`**,** `**else**` từ cơ bản đến nâng cao, bao gồm điều kiện lồng nhau (nested `if`), kết hợp nhiều điều kiện, guard clause, cách viết điều kiện theo phong cách Pythonic và nhiều ví dụ thực tế như hệ thống đăng nhập, tính thuế, phân loại học lực và xử lý nghiệp vụ trong ứng dụng.
