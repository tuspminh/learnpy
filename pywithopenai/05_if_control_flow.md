# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 5: Làm chủ Cấu trúc Điều kiện (`if`, `elif`, `else`)

> **Mục tiêu buổi học**
> 
> Sau buổi học này, bạn sẽ:
> 
> - Hiểu cách chương trình đưa ra quyết định.
> - Thành thạo `if`, `elif`, `else`.
> - Hiểu giá trị Truthy/Falsy trong điều kiện.
> - Biết kết hợp nhiều điều kiện.
> - Viết điều kiện theo phong cách Pythonic.
> - Tránh các lỗi phổ biến.
> - Xây dựng được các chương trình thực tế.

---

# 1. Điều kiện là gì?

Trong cuộc sống, chúng ta liên tục đưa ra quyết định dựa trên điều kiện.

Ví dụ:

```text-x-trilium-auto
Nếu trời mưa
    → Mang ô.

Nếu hết tiền
    → Không mua đồ.

Nếu điểm >= 8
    → Học sinh giỏi.
```

Máy tính cũng hoạt động tương tự.

```text-x-trilium-auto
Điều kiện

↓

Đúng (True)

↓

Thực hiện khối lệnh A

Hoặc

Sai (False)

↓

Thực hiện khối lệnh B
```

---

# 2. Câu lệnh `if`

Cú pháp

```text-x-trilium-auto
if điều_kiện:
    khối_lệnh
```

Ví dụ

```text-x-trilium-auto
age = 20

if age >= 18:
    print("Bạn đã đủ tuổi.")
```

Kết quả

```text-x-trilium-auto
Bạn đã đủ tuổi.
```

---

Điều gì xảy ra?

```text-x-trilium-auto
age = 20

↓

20 >= 18

↓

True

↓

Thực hiện print()
```

---

# 3. Thụt lề (Indentation)

Đây là điểm rất quan trọng.

Python **không dùng** `**{}**` như C, Java.

Python dùng **thụt lề**.

Đúng

```text-x-trilium-auto
age = 20

if age >= 18:
    print("Đủ tuổi")
```

Sai

```text-x-trilium-auto
age = 20

if age >= 18:
print("Đủ tuổi")
```

Kết quả

```text-x-trilium-auto
IndentationError
```

---

## Quy tắc

PEP 8 khuyến nghị:

**4 khoảng trắng** cho mỗi mức thụt lề.

Không nên trộn **Tab** và **Space** trong cùng một tệp.

---

# 4. `if...else`

Ví dụ

```text-x-trilium-auto
age = 16

if age >= 18:
    print("Được xem phim.")
else:
    print("Chưa đủ tuổi.")
```

Kết quả

```text-x-trilium-auto
Chưa đủ tuổi.
```

---

Luồng hoạt động

```text-x-trilium-auto
          age >= 18 ?

           /      \

        True      False

         │          │

     Được xem   Chưa đủ tuổi
```

---

# 5. `if...elif...else`

Ví dụ

```text-x-trilium-auto
score = 8

if score >= 9:
    print("Xuất sắc")
elif score >= 8:
    print("Giỏi")
elif score >= 6.5:
    print("Khá")
elif score >= 5:
    print("Trung bình")
else:
    print("Yếu")
```

Kết quả

```text-x-trilium-auto
Giỏi
```

---

Lưu ý:

Python kiểm tra **từ trên xuống dưới**.

Khi gặp điều kiện đúng đầu tiên, các điều kiện phía sau sẽ không được kiểm tra nữa.

---

# 6. Ví dụ sai phổ biến

Sai

```text-x-trilium-auto
score = 9

if score >= 5:
    print("Đậu")
elif score >= 8:
    print("Giỏi")
```

Kết quả

```text-x-trilium-auto
Đậu
```

Vì:

```text-x-trilium-auto
9 >= 5

↓

True

↓

Dừng luôn
```

Đúng

```text-x-trilium-auto
if score >= 8:
    print("Giỏi")
elif score >= 5:
    print("Đậu")
```

---

# 7. Điều kiện lồng nhau (Nested if)

Ví dụ

```text-x-trilium-auto
age = 20
has_ticket = True

if age >= 18:
    if has_ticket:
        print("Được vào rạp.")
    else:
        print("Mua vé trước.")
else:
    print("Chưa đủ tuổi.")
```

---

Sơ đồ

```text-x-trilium-auto
age >=18 ?

│

├── Không

│      ↓

│   Kết thúc

│

└── Có

      │

      has_ticket ?

      │

 ├── Có

 │

 │  Được vào

 │

 └── Không

    Mua vé
```

---

# 8. Kết hợp điều kiện

## `and`

```text-x-trilium-auto
age = 20
has_ticket = True

if age >= 18 and has_ticket:
    print("Được vào.")
```

---

## `or`

```text-x-trilium-auto
is_admin = False
is_teacher = True

if is_admin or is_teacher:
    print("Có quyền truy cập.")
```

---

## `not`

```text-x-trilium-auto
is_login = False

if not is_login:
    print("Hãy đăng nhập.")
```

---

# 9. Truthy và Falsy

Không nhất thiết phải viết:

```text-x-trilium-auto
if is_login == True:
```

Chỉ cần:

```text-x-trilium-auto
if is_login:
```

---

Ví dụ

```text-x-trilium-auto
name = "Garden"

if name:
    print("Có tên.")
```

---

Chuỗi rỗng

```text-x-trilium-auto
name = ""

if name:
    print("Có dữ liệu")
else:
    print("Rỗng")
```

Kết quả

```text-x-trilium-auto
Rỗng
```

---

Danh sách

```text-x-trilium-auto
numbers = []

if numbers:
    print("Có phần tử")
else:
    print("Danh sách rỗng")
```

---

Đây là cách viết Pythonic.

---

# 10. So sánh chuỗi

```text-x-trilium-auto
password = "python123"

user_input = input("Mật khẩu: ")

if user_input == password:
    print("Đăng nhập thành công.")
else:
    print("Sai mật khẩu.")
```

---

# 11. Toán tử ba ngôi

Thông thường

```text-x-trilium-auto
if age >= 18:
    status = "Người lớn"
else:
    status = "Trẻ em"
```

Viết gọn

```text-x-trilium-auto
status = "Người lớn" if age >= 18 else "Trẻ em"
```

---

# 12. Guard Clause (phong cách chuyên nghiệp)

Thay vì

```text-x-trilium-auto
if user is not None:
    print("Xin chào")
```

Có thể viết:

```text-x-trilium-auto
if user is None:
    print("Không có người dùng.")
    exit()

print("Xin chào")
```

Đây gọi là **Guard Clause**.

Ưu điểm:

- Code ít lồng nhau.
- Dễ đọc.
- Dễ bảo trì.

---

# 13. Ví dụ thực tế 1 - Kiểm tra tuổi

```text-x-trilium-auto
age = int(input("Tuổi: "))

if age < 0:
    print("Tuổi không hợp lệ.")
elif age < 13:
    print("Trẻ em")
elif age < 18:
    print("Thiếu niên")
elif age < 60:
    print("Người lớn")
else:
    print("Người cao tuổi")
```

---

# 14. Ví dụ thực tế 2 - ATM

```text-x-trilium-auto
balance = 500000

money = int(input("Số tiền cần rút: "))

if money <= balance:
    balance -= money
    print("Rút thành công.")
    print(f"Số dư: {balance:,} VNĐ")
else:
    print("Không đủ số dư.")
```

---

# 15. Ví dụ thực tế 3 - Đăng nhập

```text-x-trilium-auto
USERNAME = "admin"
PASSWORD = "123456"

username = input("Tên đăng nhập: ")
password = input("Mật khẩu: ")

if username == USERNAME and password == PASSWORD:
    print("Đăng nhập thành công.")
else:
    print("Sai thông tin.")
```

---

# 16. Những lỗi phổ biến

## Lỗi 1: Quên dấu `:`

Sai

```text-x-trilium-auto
if age >= 18
    print("OK")
```

Đúng

```text-x-trilium-auto
if age >= 18:
    print("OK")
```

---

## Lỗi 2: Sai thụt lề

Sai

```text-x-trilium-auto
if age >= 18:
print("OK")
```

---

## Lỗi 3: Dùng `=` thay vì `==`

Sai

```text-x-trilium-auto
if age = 18:
```

Đúng

```text-x-trilium-auto
if age == 18:
```

---

## Lỗi 4: Điều kiện dư thừa

Không nên

```text-x-trilium-auto
if is_login == True:
```

Nên

```text-x-trilium-auto
if is_login:
```

---

# 17. Pythonic

Không nên

```text-x-trilium-auto
if len(numbers) > 0:
    print("Có dữ liệu")
```

Nên

```text-x-trilium-auto
if numbers:
    print("Có dữ liệu")
```

---

Không nên

```text-x-trilium-auto
if len(text) == 0:
```

Nên

```text-x-trilium-auto
if not text:
```

---

# 18. Bài tập thực hành

## Bài 1

Nhập tuổi.

In:

- Trẻ em
- Thiếu niên
- Người lớn
- Người cao tuổi

---

## Bài 2

Nhập điểm.

In:

- Xuất sắc
- Giỏi
- Khá
- Trung bình
- Yếu

---

## Bài 3

Nhập username và password.

Nếu đúng

```text-x-trilium-auto
Đăng nhập thành công.
```

Ngược lại

```text-x-trilium-auto
Sai tài khoản hoặc mật khẩu.
```

---

## Bài 4

Nhập số.

Kiểm tra:

- Dương
- Âm
- Bằng 0

---

## Bài 5

Nhập năm sinh.

Tính tuổi.

Nếu dưới 18

```text-x-trilium-auto
Chưa đủ tuổi.
```

Nếu từ 18 trở lên

```text-x-trilium-auto
Đủ tuổi.
```

---

## Bài 6

Nhập:

- Số dư tài khoản
- Số tiền muốn rút

Kiểm tra có đủ tiền hay không.

---

## Bài 7

Nhập mật khẩu.

Nếu độ dài nhỏ hơn 8 ký tự:

```text-x-trilium-auto
Mật khẩu quá ngắn.
```

Ngược lại:

```text-x-trilium-auto
Mật khẩu hợp lệ.
```

*Gợi ý:* Dùng `len()` để lấy độ dài chuỗi.

---

# Mini Project: Hệ thống tính học lực

Viết chương trình:

Nhập:

- Họ tên
- Điểm Toán
- Điểm Văn
- Điểm Anh

Tính:

```text-x-trilium-auto
Điểm trung bình
```

Phân loại:

| Điểm TB | Học lực |
| --- | --- |
| ≥ 9 | Xuất sắc |
| ≥ 8 | Giỏi |
| ≥ 6.5 | Khá |
| ≥ 5 | Trung bình |
| < 5 | Yếu |

In kết quả:

```text-x-trilium-auto
=============================
      KẾT QUẢ HỌC TẬP
=============================

Họ tên      : Nguyễn Văn A

Điểm TB     : 8.33

Học lực     : Giỏi

=============================
```

---

# Tóm tắt buổi 5

Hôm nay bạn đã học được:

- ✅ Câu lệnh `if`.
- ✅ `if...else`.
- ✅ `if...elif...else`.
- ✅ Điều kiện lồng nhau (Nested `if`).
- ✅ Kết hợp điều kiện với `and`, `or`, `not`.
- ✅ Truthy/Falsy và cách viết Pythonic.
- ✅ So sánh chuỗi.
- ✅ Toán tử điều kiện (conditional expression).
- ✅ Guard Clause để giảm lồng nhau.
- ✅ Các lỗi phổ biến và cách tránh.

---

# Góc lập trình viên chuyên nghiệp

Trong các dự án thực tế, phần lớn logic nghiệp vụ đều được xây dựng từ các câu lệnh điều kiện. Ví dụ:

- Kiểm tra đăng nhập và phân quyền người dùng.
- Xác thực dữ liệu trước khi lưu vào cơ sở dữ liệu.
- Tính giảm giá, thuế và khuyến mãi trong hệ thống bán hàng.
- Điều khiển luồng xử lý của chatbot hoặc ứng dụng AI.
- Kiểm tra trạng thái đơn hàng, thanh toán và vận chuyển.

Vì vậy, việc nắm vững `if`, `elif` và `else` sẽ là nền tảng quan trọng cho mọi lĩnh vực lập trình Python sau này.

## Chuẩn bị cho Buổi 6

Ở buổi tiếp theo, chúng ta sẽ học `**match...case**` **(Structural Pattern Matching)** – một tính năng hiện đại từ Python 3.10+, giúp thay thế nhiều chuỗi `if...elif...else` phức tạp bằng mã nguồn ngắn gọn, rõ ràng và mạnh mẽ hơn. Chúng ta sẽ đi từ cú pháp cơ bản đến pattern matching nâng cao với nhiều ví dụ thực tế.
