# Buổi 6: Encapsulation trong Python – Public, Protected, Private và Name Mangling

Đây là buổi mà rất nhiều người mới học Python hiểu sai.

Nếu bạn từng học Java hoặc C++, bạn sẽ quen với:

- `public`
- `private`
- `protected`

Nhưng trong Python **không tồn tại các từ khóa này**. Python chọn một triết lý khác: **"We are all consenting adults here."** (Tạm dịch: "Chúng ta đều là những người có trách nhiệm.")

Điều đó có nghĩa là Python **không cố ngăn bạn truy cập dữ liệu**, mà chỉ **đưa ra quy ước và công cụ để hạn chế việc sử dụng sai**.

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ hiểu:

- Encapsulation (đóng gói) là gì.
- Public attribute.
- Protected attribute.
- Private attribute.
- Name Mangling hoạt động như thế nào.
- Tại sao Python không có private "thật".
- Khi nào nên dùng `_name` và `__name`.
- Những sai lầm phổ biến.

---

# 1. Encapsulation là gì?

Encapsulation là việc:

- Gom dữ liệu (data) và hành vi (method) vào cùng một class.
- Che giấu các chi tiết cài đặt bên trong.
- Chỉ cung cấp giao diện cần thiết cho người dùng class.

Ví dụ:

```text-x-trilium-auto
class BankAccount:

    def __init__(self, balance):
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
```

Người dùng chỉ cần:

```text-x-trilium-auto
account.deposit(100)
```

Không cần biết bên trong cập nhật `balance` như thế nào.

---

# 2. Public Attribute

Đây là loại mặc định.

Ví dụ:

```text-x-trilium-auto
class Student:

    def __init__(self):
        self.name = "An"
```

Có thể truy cập ở mọi nơi:

```text-x-trilium-auto
s = Student()

print(s.name)

s.name = "Bình"
```

Không có giới hạn.

Sơ đồ:

```text-x-trilium-auto
Student

name

↓

Mọi nơi đều truy cập được
```

---

# 3. Protected Attribute (Theo quy ước)

Python không có protected thật.

Quy ước:

```text-x-trilium-auto
class Student:

    def __init__(self):
        self._score = 100
```

Dấu `_` chỉ mang ý nghĩa:

> "Đây là thành phần nội bộ, đừng dùng nếu không cần."

Vẫn truy cập được:

```text-x-trilium-auto
s = Student()

print(s._score)
```

Không có lỗi.

---

# 4. Protected dùng để làm gì?

Ví dụ:

```text-x-trilium-auto
class Animal:

    def __init__(self):
        self._energy = 100
```

Lớp con:

```text-x-trilium-auto
class Dog(Animal):

    def run(self):
        self._energy -= 10
```

`_energy` được xem là dành cho class và các lớp kế thừa, không phải cho mã bên ngoài.

---

# 5. Private Attribute

Nếu muốn hạn chế mạnh hơn:

```text-x-trilium-auto
class Student:

    def __init__(self):
        self.__score = 100
```

Thử:

```text-x-trilium-auto
s = Student()

print(s.__score)
```

Kết quả:

```text-x-trilium-auto
AttributeError
```

Nhiều người nghĩ:

> "Python đã mã hóa dữ liệu."

Không đúng.

---

# 6. Name Mangling

Python không xóa thuộc tính.

Nó đổi tên.

Ví dụ:

```text-x-trilium-auto
class Student:

    def __init__(self):
        self.__score = 100
```

Thực tế trong bộ nhớ:

```text-x-trilium-auto
Student

_score

↓

Không

↓

_Student__score
```

Python đã đổi tên thành:

```text-x-trilium-auto
_Student__score
```

Đây gọi là **Name Mangling**.

---

# 7. Kiểm tra bằng `__dict__`

```text-x-trilium-auto
class Student:

    def __init__(self):
        self.__score = 100

s = Student()

print(s.__dict__)
```

Kết quả:

```text-x-trilium-auto
{
    '_Student__score': 100
}
```

Rõ ràng:

`__score`

đã trở thành

`_Student__score`

---

# 8. Có thể truy cập không?

Có.

```text-x-trilium-auto
print(s._Student__score)
```

Kết quả:

```text-x-trilium-auto
100
```

Điều này chứng minh:

Python không có private tuyệt đối.

Chỉ đổi tên.

---

# 9. Tại sao phải Name Mangling?

Xem ví dụ:

```text-x-trilium-auto
class Animal:

    def __init__(self):
        self.__age = 10
```

Lớp con:

```text-x-trilium-auto
class Dog(Animal):

    def __init__(self):
        super().__init__()
        self.__age = 2
```

Nếu không có Name Mangling:

```text-x-trilium-auto
Animal.age

↓

Dog.age

↓

Ghi đè
```

Rất nguy hiểm.

---

Thực tế:

```text-x-trilium-auto
Animal

_Animal__age
```

và

```text-x-trilium-auto
Dog

_Dog__age
```

Hai thuộc tính hoàn toàn khác nhau.

---

# 10. Ví dụ

```text-x-trilium-auto
class Animal:

    def __init__(self):
        self.__age = 10


class Dog(Animal):

    def __init__(self):
        super().__init__()
        self.__age = 2


d = Dog()

print(d.__dict__)
```

Kết quả:

```text-x-trilium-auto
{
 '_Animal__age':10,
 '_Dog__age':2
}
```

Đây chính là mục đích thật sự của Name Mangling.

---

# 11. So sánh `_` và `__`

## Một dấu gạch dưới

```text-x-trilium-auto
_value
```

Ý nghĩa:

```text-x-trilium-auto
Protected (quy ước)

↓

Đừng dùng từ bên ngoài
```

---

## Hai dấu gạch dưới

```text-x-trilium-auto
__value
```

Ý nghĩa:

```text-x-trilium-auto
Name Mangling

↓

Tránh xung đột tên

↓

Hạn chế truy cập
```

---

# 12. Không nên lạm dụng `__`

Nhiều người viết:

```text-x-trilium-auto
class User:

    def __init__(self):
        self.__name = ""
        self.__age = 0
        self.__email = ""
```

Đây thường là không cần thiết.

Python khuyến khích:

```text-x-trilium-auto
self.name
```

hoặc

```text-x-trilium-auto
self._name
```

Chỉ dùng `__` khi thật sự cần tránh xung đột tên hoặc muốn ẩn chi tiết cài đặt.

---

# 13. Ví dụ thực tế: Repository

Trong dự án crawler của bạn:

```text-x-trilium-auto
class BookRepository:

    def __init__(self, db):
        self._db = db
```

Không cần:

```text-x-trilium-auto
self.__db
```

Vì repository và các lớp liên quan vẫn có thể cần truy cập `_db`.

---

# 14. Ví dụ thực tế: HTTP Client

```text-x-trilium-auto
class HttpClient:

    def __init__(self):
        self._session = None
```

`_session` là chi tiết nội bộ, nhưng các lớp kế thừa hoặc code trong cùng module vẫn có thể sử dụng nếu cần.

---

# 15. Ví dụ cần `__`

```text-x-trilium-auto
class Cache:

    def __init__(self):
        self.__lock = object()
```

Bạn không muốn lớp kế thừa vô tình tạo một thuộc tính cùng tên `__lock`.

---

# 16. Sai lầm phổ biến

## Sai lầm 1

Nghĩ rằng:

```text-x-trilium-auto
self.__x
```

là bảo mật.

Sai.

Có thể truy cập:

```text-x-trilium-auto
obj._ClassName__x
```

---

## Sai lầm 2

Lạm dụng `__`

Ví dụ:

```text-x-trilium-auto
self.__name
self.__age
self.__salary
self.__phone
```

Không cần thiết.

---

## Sai lầm 3

Viết:

```text-x-trilium-auto
self._x
```

rồi mong Python cấm truy cập.

Không.

Đây chỉ là quy ước.

---

# 17. Quy tắc nên dùng

| Loại | Khi dùng |
| --- | --- |
| `name` | Thuộc tính công khai |
| `_name` | Nội bộ của class (quy ước) |
| `__name` | Tránh xung đột tên, chi tiết rất nội bộ |

---

# 18. Tổng kết

| Ký hiệu | Ý nghĩa | Có truy cập được không? |
| --- | --- | --- |
| `name` | Public | Có  |
| `_name` | Protected (quy ước) | Có  |
| `__name` | Name Mangling | Có, nếu biết tên đã bị đổi |

---

# Bài tập thực hành

## Bài 1

Viết lớp:

```text-x-trilium-auto
class Employee:
```

Có:

- `name` (public)
- `_salary` (protected)
- `__password` (private)

Tạo object và:

- In `name`
- In `_salary`
- Thử in `__password`
- In `__dict__`
- Truy cập `_Employee__password`

Giải thích kết quả.

---

## Bài 2

Tạo hai lớp:

```text-x-trilium-auto
class Animal
```

và

```text-x-trilium-auto
class Dog(Animal)
```

Cả hai đều có:

```text-x-trilium-auto
__age
```

In `__dict__` của `Dog` và giải thích vì sao có hai khóa khác nhau.

---

## Bài 3

Thiết kế lớp:

```text-x-trilium-auto
class DatabaseConnection:
```

- `_connection`
- `_cursor`
- `__secret_key`

Giải thích vì sao hai thuộc tính đầu dùng `_`, còn thuộc tính cuối dùng `__`.

---

## Bài 4 (Thực tế)

Trong dự án hệ thống crawler truyện, hãy thiết kế một lớp `HttpClient` với:

- `_session`: phiên làm việc HTTP dùng chung trong nội bộ lớp.
- `_headers`: tiêu đề mặc định.
- `__request_count`: bộ đếm số lần gửi request.

Viết thêm phương thức `get(url)` để tăng `__request_count` mỗi lần gọi và một phương thức `request_count()` để đọc giá trị này. Điều này giúp bạn luyện tập cách kết hợp public method với thuộc tính nội bộ.

---

## Chuẩn bị cho Buổi 7

Ở buổi tiếp theo, chúng ta sẽ học về **Property và Descriptor cơ bản**, bao gồm:

- Vì sao Python khuyến khích dùng `@property`.
- Biến một method thành thuộc tính như thế nào.
- `getter`, `setter`, `deleter`.
- Kiểm soát việc đọc và ghi dữ liệu.
- Tại sao `property` thực chất là một **descriptor**.

Đây là nền tảng để hiểu cách hoạt động của nhiều thư viện lớn như ORM, PySide6, `dataclasses` và các framework Python hiện đại.