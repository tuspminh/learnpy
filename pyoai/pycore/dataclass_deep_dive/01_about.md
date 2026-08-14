# Dataclass Deep Dive - Buổi 1

# Giới thiệu Dataclass và lý do ra đời

> Mục tiêu buổi học:
> 
> Sau buổi này bạn sẽ hiểu:
> 
> - Dataclass giải quyết vấn đề gì
> - Khi nào nên dùng
> - Dataclass thực chất là gì
> - Python tạo những gì phía sau
> - Khi nào KHÔNG nên dùng dataclass

---

# 1. Vấn đề trước khi có dataclass

Hãy xem một class đơn giản.

```text-x-trilium-auto
class Student:

    def __init__(self, id, name, age):
        self.id = id
        self.name = name
        self.age = age
```

Tạo object

```text-x-trilium-auto
s = Student(1, "An", 20)
```

Muốn in object

```text-x-trilium-auto
print(s)
```

Kết quả

```text-x-trilium-auto
<__main__.Student object at 0x000001A45D8F>
```

Không hữu ích.

Muốn đẹp hơn phải viết

```text-x-trilium-auto
class Student:

    def __init__(self, id, name, age):
        self.id = id
        self.name = name
        self.age = age

    def __repr__(self):
        return f"Student(id={self.id}, name={self.name}, age={self.age})"
```

---

## So sánh hai object

```text-x-trilium-auto
s1 = Student(1, "An", 20)
s2 = Student(1, "An", 20)

print(s1 == s2)
```

Kết quả

```text-x-trilium-auto
False
```

Tại sao?

Python mặc định so sánh địa chỉ bộ nhớ.

```text-x-trilium-auto
s1 ----------> Object A

s2 ----------> Object B
```

Mặc dù dữ liệu giống nhau nhưng là hai object khác nhau.

Muốn so sánh dữ liệu phải tự viết

```text-x-trilium-auto
def __eq__(self, other):
    return (
        self.id == other.id
        and self.name == other.name
        and self.age == other.age
    )
```

---

## Muốn sắp xếp

```text-x-trilium-auto
students.sort()
```

Python báo lỗi.

Phải tự viết

```text-x-trilium-auto
__lt__()

__le__()

__gt__()

__ge__()
```

---

## Muốn hash

Ví dụ

```text-x-trilium-auto
student_set = {s1}
```

hoặc

```text-x-trilium-auto
cache = {
    student: score
}
```

Lại phải viết

```text-x-trilium-auto
__hash__()
```

---

## Chỉ một model đơn giản

```text-x-trilium-auto
Student
```

đã phải viết rất nhiều code.

Trong thực tế

```text-x-trilium-auto
Book

Author

Novel

Category

Chapter

Publisher

Comment

Image
```

Mỗi class đều phải lặp lại những đoạn code giống nhau.

Đây gọi là **boilerplate code**.

---

# 2. Boilerplate là gì?

Boilerplate là:

> Những đoạn code lặp đi lặp lại nhưng không chứa logic nghiệp vụ.

Ví dụ

```text-x-trilium-auto
class User:

    def __init__(...):
        ...

    def __repr__(...):
        ...

    def __eq__(...):
        ...

    def __hash__(...):
        ...
```

90% code chỉ để hỗ trợ Python.

Không phải business logic.

---

# 3. Dataclass ra đời

Python 3.7

PEP 557

Mục tiêu:

> "Để biểu diễn dữ liệu."

Nghĩa là

Nếu object chủ yếu dùng để chứa dữ liệu

thì Python sẽ giúp bạn tạo:

- constructor
- repr
- compare
- hash
- ...

---

# 4. Dataclass là gì?

Đây là toàn bộ dataclass.

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass class Student:
    id: int
    name: str
    age: int
```

Chỉ vậy thôi.

---

Tạo object

```text-x-trilium-auto
s = Student(1, "An", 20)

print(s)
```

Kết quả

```text-x-trilium-auto
Student(id=1, name='An', age=20)
```

Không cần viết `__repr__`.

---

So sánh

```text-x-trilium-auto
a = Student(1, "An", 20)
b = Student(1, "An", 20)

print(a == b)
```

Kết quả

```text-x-trilium-auto
True
```

Không cần viết `__eq__`.

---

Khởi tạo

```text-x-trilium-auto
Student(1, "An", 20)
```

Không cần viết `__init__`.

---

# 5. Dataclass thực chất là gì?

Rất nhiều người nghĩ

```text-x-trilium-auto
Dataclass
↓

là kiểu dữ liệu mới
```

Sai.

Dataclass vẫn là

```text-x-trilium-auto
class
```

bình thường.

Decorator

```text-x-trilium-auto
@dataclass
```

chỉ làm một việc:

> Thêm các method vào class.

Ví dụ

```text-x-trilium-auto
@dataclass class Student:
    id: int
    name: str
```

Sau khi Python chạy

nó gần giống như

```text-x-trilium-auto
class Student:

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        ...

    def __eq__(self):
        ...
```

Decorator đã sửa class của bạn.

---

# 6. Dataclass không thay đổi kế thừa

Ví dụ

```text-x-trilium-auto
@dataclass class Animal:
    name: str
```

```text-x-trilium-auto
@dataclass class Dog(Animal):
    age: int
```

Hoàn toàn bình thường.

```text-x-trilium-auto
Animal

    ↑

Dog
```

Dataclass không phá OOP.

---

# 7. Dataclass chỉ dựa vào Type Hint

Ví dụ

```text-x-trilium-auto
@dataclass class Student:
    id: int
    name: str
```

Python nhìn thấy

```text-x-trilium-auto
id: int

name: str
```

và hiểu

```text-x-trilium-auto
Đây là field
```

Nếu viết

```text-x-trilium-auto
class Student:
    id = 0
```

thì đó chỉ là class variable, không được coi là field của dataclass.

---

# 8. Dataclass tạo những gì?

Mặc định

```text-x-trilium-auto
@dataclass
```

sẽ sinh ra:

| Method | Ý nghĩa |
| --- | --- |
| `__init__()` | Constructor |
| `__repr__()` | In đẹp |
| `__eq__()` | So sánh |
| `__match_args__()` | Hỗ trợ Pattern Matching (Python 3.10+) |

Tùy cấu hình, dataclass còn có thể tạo:

- `__hash__()`
- `__lt__()`
- `__le__()`
- `__gt__()`
- `__ge__()`

Chúng ta sẽ tìm hiểu chi tiết ở các buổi sau.

---

# 9. Dataclass không phải ORM

Nhiều người mới học thường nhầm:

```text-x-trilium-auto
Dataclass

=

Database Model
```

Sai.

Dataclass chỉ là object Python.

Ví dụ

```text-x-trilium-auto
@dataclass class Student:
    id: int
    name: str
```

Nó không:

- tạo bảng
- lưu SQLite
- lưu MySQL
- truy vấn dữ liệu

Đó là nhiệm vụ của ORM như SQLAlchemy hoặc Django ORM.

---

# 10. Khi nào nên dùng Dataclass?

Rất phù hợp cho:

- DTO (Data Transfer Object)
- API Response
- API Request
- Configuration
- Value Object
- Settings
- Cache
- Event
- Message
- Queue Item
- Parser Result
- Crawler Result

Ví dụ trong dự án crawler của bạn:

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass class Chapter:
    id: int
    title: str
    url: str
    index: int
```

Parser chỉ việc trả về:

```text-x-trilium-auto
chapter = Chapter(
    id=1,
    title="Chương 1",
    url="/chuong-1",
    index=1
)
```

Code rất rõ ràng.

---

# 11. Khi nào KHÔNG nên dùng?

Không nên dùng khi:

- class có nhiều logic nghiệp vụ hơn dữ liệu
- cần kiểm soát chặt việc khởi tạo
- cần nhiều thuộc tính tính toán động
- muốn quản lý trạng thái phức tạp

Ví dụ:

```text-x-trilium-auto
class BankAccount:

    def deposit(self):
        ...

    def withdraw(self):
        ...

    def transfer(self):
        ...

    def calculate_interest(self):
        ...
```

Đây là một **domain object** giàu hành vi (behavior-rich), không chỉ là một "túi dữ liệu". `@dataclass` không mang lại nhiều lợi ích trong trường hợp này.

---

# 12. So sánh Class thường và Dataclass

| Tiêu chí | Class thường | Dataclass |
| --- | --- | --- |
| Viết `__init__` | ✔   | ✘ (tự sinh) |
| Viết `__repr__` | ✔   | ✘   |
| Viết `__eq__` | ✔   | ✘   |
| Boilerplate | Nhiều | Ít  |
| Hiệu năng | Gần như tương đương | Gần như tương đương |
| Dùng cho dữ liệu | Được | Rất phù hợp |
| Dùng cho business logic | Rất phù hợp | Có thể, nhưng không phải lựa chọn tối ưu |

---

# Ví dụ tổng hợp

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass class Book:
    id: int
    title: str
    author: str
    pages: int


book1 = Book(1, "Python Deep Dive", "Alice", 500)
book2 = Book(1, "Python Deep Dive", "Alice", 500)

print(book1)
print(book1 == book2)
```

Kết quả:

```text-x-trilium-auto
Book(id=1, title='Python Deep Dive', author='Alice', pages=500)
True
```

Không cần tự viết `__init__`, `__repr__`, hay `__eq__`.

---

# Bài tập thực hành

## Bài 1

Viết class `Employee` theo cách truyền thống:

```text-x-trilium-auto
id
name
salary
```

Tự cài đặt:

- `__init__`
- `__repr__`
- `__eq__`

---

## Bài 2

Chuyển `Employee` sang `@dataclass`.

So sánh số dòng mã và kết quả chạy.

---

## Bài 3

Tạo các dataclass sau cho dự án crawler truyện:

- `Novel`
- `Author`
- `Category`
- `Chapter`

Mỗi lớp nên có tối thiểu 4 trường dữ liệu (ví dụ: `id`, `name`, `url`, `created_at` hoặc các trường phù hợp).

---

### Chuẩn bị cho Buổi 2

Ở buổi tiếp theo, chúng ta sẽ **mổ xẻ từng phương thức mà** `**@dataclass**` **tự sinh** (`__init__`, `__repr__`, `__eq__`, `__match_args__`...), xem Python tạo chúng như thế nào, quy tắc sinh ra ra sao và khi nào nên ghi đè (override) chúng. Đây là nền tảng để hiểu sâu cách `dataclass` hoạt động bên trong.