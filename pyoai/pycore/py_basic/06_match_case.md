# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 6: Làm chủ `match...case` (Structural Pattern Matching)

> **Mục tiêu buổi học**
> 
> Sau buổi học này, bạn sẽ:
> 
> - Hiểu `match...case` là gì.
> - Biết khi nào nên dùng `match`, khi nào nên dùng `if`.
> - Thành thạo toàn bộ cú pháp `match...case`.
> - Biết Pattern Matching hoạt động như thế nào.
> - Biết sử dụng Guard (`if`) trong `case`.
> - Biết bắt nhiều giá trị cùng lúc.
> - Biết Match Sequence.
> - Biết Match Dictionary.
> - Biết Match Object.
> - Xây dựng được chương trình thực tế.

> **Lưu ý**
> 
> `match...case` chỉ có từ **Python 3.10** trở lên.

---

# 1. Vì sao cần `match...case`?

Giả sử ta viết menu:

```text-x-trilium-auto
menu = int(input("Chọn menu: "))

if menu == 1:
    print("Đăng nhập")

elif menu == 2:
    print("Đăng ký")

elif menu == 3:
    print("Đổi mật khẩu")

elif menu == 4:
    print("Thoát")

else:
    print("Không hợp lệ")
```

Chương trình chạy tốt.

Nhưng nếu có:

- 20 menu
- 50 menu
- 100 menu

thì sẽ rất dài.

Python 3.10 giới thiệu:

```text-x-trilium-auto
match
```

để giải quyết vấn đề này.

---

# 2. Cú pháp

```text-x-trilium-auto
match biểu_thức:

    case giá_trị_1:
        ...

    case giá_trị_2:
        ...

    case _:
        ...
```

Trong đó

```text-x-trilium-auto
_

↓

default
```

tương tự:

```text-x-trilium-auto
else
```

---

# 3. Ví dụ đầu tiên

```text-x-trilium-auto
menu = 2

match menu:

    case 1:
        print("Đăng nhập")

    case 2:
        print("Đăng ký")

    case 3:
        print("Thoát")

    case _:
        print("Không hợp lệ")
```

Kết quả

```text-x-trilium-auto
Đăng ký
```

---

# 4. Luồng hoạt động

```text-x-trilium-auto
match menu

│

├── case 1

├── case 2

├── case 3

└── case _
```

Python sẽ kiểm tra từ trên xuống.

Khi gặp case đúng

↓

Dừng.

Không kiểm tra tiếp.

---

# 5. Không cần `break`

Khác với C, Java.

Ví dụ C

```text-x-trilium-auto
switch(x){

case 1:
...

break;

case 2:
...

break;

}
```

Python

```text-x-trilium-auto
match x:

    case 1:
        ...

    case 2:
        ...
```

Không cần

```text-x-trilium-auto
break
```

---

# 6. Match chuỗi

```text-x-trilium-auto
command = input("Lệnh: ")

match command:

    case "start":
        print("Khởi động")

    case "stop":
        print("Dừng")

    case "restart":
        print("Khởi động lại")

    case _:
        print("Không biết lệnh")
```

---

# 7. Match nhiều giá trị

Có thể dùng:

```text-x-trilium-auto
|
```

Ví dụ

```text-x-trilium-auto
grade = "A"

match grade:

    case "A" | "A+":
        print("Xuất sắc")

    case "B" | "B+":
        print("Giỏi")

    case _:
        print("Khác")
```

---

# 8. Match số

```text-x-trilium-auto
day = 6

match day:

    case 1:
        print("Thứ Hai")

    case 2:
        print("Thứ Ba")

    case 3:
        print("Thứ Tư")

    case 4:
        print("Thứ Năm")

    case 5:
        print("Thứ Sáu")

    case 6:
        print("Thứ Bảy")

    case 7:
        print("Chủ Nhật")

    case _:
        print("Không hợp lệ")
```

---

# 9. Guard

Có thể thêm điều kiện.

Ví dụ

```text-x-trilium-auto
age = 20

match age:

    case x if x >= 18:
        print("Người lớn")

    case _:
        print("Trẻ em")
```

Ở đây

```text-x-trilium-auto
case x
```

lưu giá trị vào

```text-x-trilium-auto
x
```

sau đó

```text-x-trilium-auto
if x >=18
```

---

# 10. Match Sequence

Ví dụ

```text-x-trilium-auto
point = (10, 20)

match point:

    case (0, 0):
        print("Gốc tọa độ")

    case (0, y):
        print("Trục Y")

    case (x, 0):
        print("Trục X")

    case (x, y):
        print(x, y)
```

Nếu

```text-x-trilium-auto
point=(5,8)
```

Kết quả

```text-x-trilium-auto
5 8
```

---

# 11. Match List

```text-x-trilium-auto
numbers = [1, 2]

match numbers:

    case [1, 2]:
        print("Đúng")

    case [x, y]:
        print(x, y)

    case _:
        print("Khác")
```

---

Ví dụ

```text-x-trilium-auto
numbers=[100,200]
```

Kết quả

```text-x-trilium-auto
100 200
```

---

# 12. Match nhiều phần tử

```text-x-trilium-auto
numbers = [1, 2, 3, 4, 5]

match numbers:

    case [first, *middle, last]:

        print(first)

        print(middle)

        print(last)
```

Kết quả

```text-x-trilium-auto
1

[2,3,4]

5
```

Đây là tính năng cực mạnh.

---

# 13. Match Dictionary

Ví dụ

```text-x-trilium-auto
student = {

    "name": "An",

    "age": 20

}

match student:

    case {"name": name}:

        print(name)
```

Kết quả

```text-x-trilium-auto
An
```

---

Có thể

```text-x-trilium-auto
case {

"name":name,

"age":age

}
```

---

# 14. Match Object

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass
class Point:

    x: int

    y: int


point = Point(5, 8)

match point:

    case Point(0, 0):

        print("Origin")

    case Point(x, y):

        print(x, y)
```

Kết quả

```text-x-trilium-auto
5 8
```

---

# 15. Match Enum

```text-x-trilium-auto
from enum import Enum

class Status(Enum):

    READY = 1

    RUNNING = 2

    STOP = 3
```

```text-x-trilium-auto
status = Status.READY

match status:

    case Status.READY:
        print("Ready")

    case Status.RUNNING:
        print("Running")

    case Status.STOP:
        print("Stop")
```

---

# 16. Khi nào dùng `match`?

Nên dùng

- Menu
- Command
- API Action
- HTTP Method
- CLI
- State Machine
- Event
- Parser

Ví dụ

```text-x-trilium-auto
match method:

    case "GET":
        ...

    case "POST":
        ...

    case "PUT":
        ...

    case "DELETE":
        ...
```

---

# 17. Khi nào KHÔNG nên dùng?

Ví dụ

```text-x-trilium-auto
if age >=18:

...
```

Không nên đổi thành

```text-x-trilium-auto
match age
```

Điều này làm code khó đọc hơn.

---

# 18. `match` hay `if`?

| `if` | `match` |
| --- | --- |
| Điều kiện phức tạp | ⭐   |
| So sánh khoảng giá trị | ⭐   |
| Logic `and`, `or` | ⭐   |
| Menu |     |
| Command |     |
| Parser |     |
| Pattern Matching |     |

**Nguyên tắc:** Nếu bạn cần kiểm tra **nhiều giá trị cụ thể** hoặc **phân rã cấu trúc dữ liệu**, `match` thường rõ ràng hơn. Nếu cần biểu thức logic phức tạp (`and`, `or`, `<`, `>`, ...), `if` thường là lựa chọn phù hợp hơn.

---

# 19. Những lỗi thường gặp

## Lỗi 1

Quên `_`

```text-x-trilium-auto
match menu:

    case 1:
        ...

    case 2:
        ...
```

Nên luôn có

```text-x-trilium-auto
case _:
```

để xử lý các trường hợp còn lại.

---

## Lỗi 2

Lạm dụng `match`

Ví dụ

```text-x-trilium-auto
age = 20

match age:

    case x if x >=18:
        ...
```

Trong trường hợp này

```text-x-trilium-auto
if age>=18
```

đẹp hơn nhiều.

---

## Lỗi 3

Nhầm `|` với `or`

Đúng

```text-x-trilium-auto
case 1 | 2:
```

Sai

```text-x-trilium-auto
case 1 or 2:
```

---

# 20. Ví dụ thực tế: CLI Calculator

```text-x-trilium-auto
operator = input("+, -, *, / : ")

a = float(input("a = "))
b = float(input("b = "))

match operator:

    case "+":
        print(a + b)

    case "-":
        print(a - b)

    case "*":
        print(a * b)

    case "/":
        if b == 0:
            print("Không thể chia cho 0.")
        else:
            print(a / b)

    case _:
        print("Toán tử không hợp lệ.")
```

---

# 21. Bài tập thực hành

## Bài 1

Viết chương trình nhập số từ 1 đến 7.

In tên ngày trong tuần bằng `match`.

---

## Bài 2

Nhập tháng.

In số ngày của tháng bằng cách sử dụng:

```text-x-trilium-auto
case 1 | 3 | 5 | 7 | 8 | 10 | 12:
```

---

## Bài 3

Nhập lệnh:

```text-x-trilium-auto
start

stop

pause

restart
```

Dùng `match` xử lý.

---

## Bài 4

Nhập phương thức HTTP:

```text-x-trilium-auto
GET

POST

PUT

DELETE
```

In ý nghĩa của từng phương thức.

---

## Bài 5

Cho

```text-x-trilium-auto
point = (0, 8)
```

Dùng `match` xác định:

- Gốc tọa độ
- Trục X
- Trục Y
- Điểm bất kỳ

---

## Bài 6

Cho

```text-x-trilium-auto
numbers = [10,20,30,40]
```

Dùng

```text-x-trilium-auto
[first,*middle,last]
```

In

```text-x-trilium-auto
10

[20,30]

40
```

---

## Bài 7

Viết menu:

```text-x-trilium-auto
1 Đăng nhập

2 Đăng ký

3 Đổi mật khẩu

4 Thoát
```

Sử dụng `match`.

---

# Mini Project: Máy ATM

Viết chương trình ATM có menu:

```text-x-trilium-auto
===================

1 Kiểm tra số dư

2 Nạp tiền

3 Rút tiền

4 Chuyển khoản

5 Thoát

===================
```

Yêu cầu:

- Dùng `match...case` để xử lý menu.
- Kiểm tra số dư khi rút tiền.
- Không cho rút quá số dư.
- Sau mỗi thao tác, in lại số dư hiện tại.

---

# Tóm tắt buổi 6

Bạn đã học được:

- ✅ `match...case` là gì.
- ✅ So sánh với `if...elif...else`.
- ✅ `case _` để xử lý mặc định.
- ✅ Match nhiều giá trị bằng `|`.
- ✅ Guard (`case x if ...`).
- ✅ Pattern Matching với tuple, list, dictionary và object.
- ✅ Ứng dụng `match` trong menu, CLI, HTTP API và parser.
- ✅ Các lỗi phổ biến và cách tránh.

---

# Góc lập trình viên chuyên nghiệp

`match...case` là một trong những tính năng mạnh nhất được bổ sung từ Python 3.10. Tuy nhiên, **đừng cố sử dụng nó ở mọi nơi**. Một lập trình viên giỏi không phải là người dùng nhiều tính năng nhất, mà là người **chọn đúng công cụ cho đúng bài toán**.

- Dùng `if` cho điều kiện logic và so sánh.
- Dùng `match` khi phân loại theo nhiều giá trị cố định hoặc cần phân rã cấu trúc dữ liệu.

Việc lựa chọn đúng sẽ giúp mã nguồn ngắn gọn, dễ đọc và dễ bảo trì.

## Chuẩn bị cho Buổi 7

Ở buổi tiếp theo, chúng ta sẽ bắt đầu một trong những chủ đề quan trọng nhất của lập trình: **vòng lặp** `**while**`. Bạn sẽ học từ cách hoạt động, điều kiện dừng, `break`, `continue`, `else` trong vòng lặp, đến các kỹ thuật tránh vòng lặp vô hạn và xây dựng các chương trình tương tác như menu lặp, trò chơi đoán số và hệ thống đăng nhập nhiều lần.
