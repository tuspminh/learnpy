# Dataclass Deep Dive - Buổi 2

# Generated Methods Deep Dive

> Sau buổi này bạn sẽ hiểu chính xác `@dataclass` sinh ra những method nào, sinh theo quy tắc gì, khi nào không sinh, và cách override chúng.

---

# Mục tiêu

Cuối buổi học bạn sẽ trả lời được:

- `@dataclass` thực sự tạo những method nào?
- Thứ tự tạo method ra sao?
- Khi nào Python không tạo?
- Có thể override được không?
- Tại sao `==` hoạt động?
- Tại sao `print(obj)` đẹp?
- `__match_args__` dùng để làm gì?

---

# 1. Nhắc lại

Dataclass

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass class Student:
    id: int
    name: str
    age: int
```

Đây chỉ là:

```text-x-trilium-auto
@dataclass
```

Một decorator.

Decorator sẽ sửa lại class.

Sau khi Python chạy gần giống:

```text-x-trilium-auto
class Student:

    def __init__(self, id, name, age):
        self.id = id
        self.name = name
        self.age = age

    def __repr__(self):
        ...

    def __eq__(self):
        ...
```

Nó **không tạo class mới**, mà **trả về chính class đã được bổ sung các phương thức**.

---

# 2. Dataclass sinh những method nào?

Mặc định

```text-x-trilium-auto
@dataclass
```

sinh:

| Method | Mặc định |
| --- | --- |
| `__init__` | ✔   |
| `__repr__` | ✔   |
| `__eq__` | ✔   |
| `__match_args__` | ✔ (Python 3.10+) |

Nếu bật thêm:

```text-x-trilium-auto
@dataclass(order=True)
```

thì sinh thêm

```text-x-trilium-auto
__lt__
__le__
__gt__
__ge__
```

Nếu

```text-x-trilium-auto
frozen=True
```

có thể sinh

```text-x-trilium-auto
__hash__
```

---

# 3. **init**()

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass class Student:
    id: int
    name: str
    age: int
```

Python sinh gần giống

```text-x-trilium-auto
def __init__(self, id, name, age):
    self.id = id
    self.name = name
    self.age = age
```

Bạn có thể kiểm tra:

```text-x-trilium-auto
s = Student(1, "An", 20)

print(s.id)
print(s.name)
print(s.age)
```

Kết quả

```text-x-trilium-auto
1
An
20
```

---

# 4. Nếu tự viết **init**?

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass class Student:

    id: int
    name: str

    def __init__(self, id, name):
        print("Custom init")
        self.id = id
        self.name = name
```

Chạy

```text-x-trilium-auto
Student(1, "An")
```

Kết quả

```text-x-trilium-auto
Custom init
```

Dataclass **không ghi đè** `__init__` mà bạn đã định nghĩa.

Quy tắc:

> Nếu method đã tồn tại, dataclass tôn trọng method đó.

---

# 5. **repr**()

Không có dataclass

```text-x-trilium-auto
class Student:
    ...
```

In

```text-x-trilium-auto
print(student)
```

Kết quả

```text-x-trilium-auto
<__main__.Student object at 0x...>
```

Có dataclass

```text-x-trilium-auto
@dataclass class Student:
    id: int
    name: str
```

In

```text-x-trilium-auto
print(student)
```

Kết quả

```text-x-trilium-auto
Student(id=1, name='An')
```

Python sinh gần giống

```text-x-trilium-auto
def __repr__(self):
    return f"Student(id={self.id}, name={self.name})"
```

---

# 6. Override **repr**()

```text-x-trilium-auto
@dataclass class Student:
    id: int
    name: str

    def __repr__(self):
        return f"<Student {self.name}>"
```

Kết quả

```text-x-trilium-auto
<Student An>
```

Dataclass không sinh nữa.

---

# 7. **eq**()

Đây là phần cực kỳ quan trọng.

Ví dụ

```text-x-trilium-auto
a = Student(1, "An")
b = Student(1, "An")
```

Không có dataclass

```text-x-trilium-auto
print(a == b)
```

Kết quả

```text-x-trilium-auto
False
```

Có dataclass

```text-x-trilium-auto
True
```

---

Python sinh gần giống

```text-x-trilium-auto
def __eq__(self, other):

    if other.__class__ is self.__class__:

        return (
            self.id == other.id
            and
            self.name == other.name
        )

    return NotImplemented
```

Nó so sánh **từng field theo thứ tự khai báo**.

---

# 8. Thứ tự field rất quan trọng

Ví dụ

```text-x-trilium-auto
@dataclass class Student:
    id: int
    name: str
    age: int
```

Python sinh

```text-x-trilium-auto
self.id == other.id

and

self.name == other.name

and

self.age == other.age
```

Không bỏ sót field nào (trừ khi bạn cấu hình khác ở `field(compare=False)` trong buổi sau).

---

# 9. Khác class thì sao?

```text-x-trilium-auto
@dataclass class Animal:
    name: str


@dataclass class Dog:
    name: str
```

```text-x-trilium-auto
Animal("Tom") == Dog("Tom")
```

Kết quả

```text-x-trilium-auto
False
```

Không phải vì dữ liệu khác.

Mà vì

```text-x-trilium-auto
Animal != Dog
```

Dataclass yêu cầu cùng kiểu đối tượng.

---

# 10. **match_args**()

Đây là method mới từ Python 3.10.

Ví dụ

```text-x-trilium-auto
@dataclass class Student:
    id: int
    name: str
```

Python sinh

```text-x-trilium-auto
Student.__match_args__
```

In ra

```text-x-trilium-auto
print(Student.__match_args__)
```

Kết quả

```text-x-trilium-auto
('id', 'name')
```

---

Nó phục vụ Pattern Matching.

```text-x-trilium-auto
student = Student(1, "An")

match student:

    case Student(id, name):
        print(id)
        print(name)
```

Kết quả

```text-x-trilium-auto
1
An
```

Không cần truy cập thuộc tính bằng tên.

---

# 11. Có thể tắt Generated Method

Ví dụ

```text-x-trilium-auto
@dataclass(repr=False)
class Student:
    id: int
```

Không sinh

```text-x-trilium-auto
__repr__
```

---

```text-x-trilium-auto
@dataclass(eq=False)
```

Không sinh

```text-x-trilium-auto
__eq__
```

---

```text-x-trilium-auto
@dataclass(init=False)
```

Không sinh

```text-x-trilium-auto
__init__
```

Lúc này

```text-x-trilium-auto
Student()
```

sẽ lỗi vì bạn chưa có constructor.

---

# 12. Thứ tự sinh method

Dataclass xử lý theo trình tự:

```text-x-trilium-auto
Đọc annotations
        ↓
Tạo field
        ↓
Sinh __init__
        ↓
Sinh __repr__
        ↓
Sinh __eq__
        ↓
Sinh order methods (nếu order=True)
        ↓
Sinh hash (nếu cần)
        ↓
Sinh __match_args__
```

Việc hiểu trình tự này sẽ giúp bạn lý giải các hành vi khi kết hợp `field()`, `InitVar`, `frozen`, `slots`...

---

# 13. inspect

Ta có thể dùng `inspect` để xem chữ ký (signature) của constructor.

```text-x-trilium-auto
from dataclasses import dataclass import inspect


@dataclass class Student:
    id: int
    name: str
    age: int


print(inspect.signature(Student))
```

Kết quả

```text-x-trilium-auto
(id: int, name: str, age: int)
```

Không cần viết constructor.

---

# 14. vars()

```text-x-trilium-auto
s = Student(1, "An", 20)

print(vars(s))
```

Kết quả

```text-x-trilium-auto
{
    'id': 1,
    'name': 'An',
    'age': 20
}
```

Dataclass vẫn là object Python bình thường có `__dict__` (trừ khi dùng `slots=True`, sẽ học ở Buổi 7).

---

# 15. Ví dụ thực tế trong dự án crawler

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass class Chapter:
    id: int
    title: str
    url: str
    index: int


c1 = Chapter(1, "Chương 1", "/chuong-1", 1)
c2 = Chapter(1, "Chương 1", "/chuong-1", 1)

print(c1)
print(c1 == c2)
```

Kết quả

```text-x-trilium-auto
Chapter(id=1, title='Chương 1', url='/chuong-1', index=1)
True
```

Điều này rất hữu ích khi parser tạo ra các đối tượng và bạn muốn so sánh chúng theo nội dung thay vì địa chỉ bộ nhớ.

---

# Tổng kết Buổi 2

| Method | Mục đích | Tự sinh mặc định |
| --- | --- | --- |
| `__init__` | Khởi tạo object | ✔   |
| `__repr__` | Hiển thị khi `print()` | ✔   |
| `__eq__` | So sánh giá trị | ✔   |
| `__match_args__` | Hỗ trợ `match/case` | ✔   |
| `__hash__` | Dùng làm key của `dict`/`set` | Có điều kiện |
| `__lt__`, `__le__`, `__gt__`, `__ge__` | So sánh thứ tự | Chỉ khi `order=True` |

---

# Bài tập thực hành

### Bài 1

Tạo dataclass `Book` với các trường:

- `id`
- `title`
- `author`

Thực hiện:

- In đối tượng.
- So sánh hai đối tượng có cùng dữ liệu.
- In `Book.__match_args__`.
- Dùng `inspect.signature(Book)` để xem constructor được sinh.

---

### Bài 2

Tạo dataclass `Novel` và tự override `__repr__()` theo định dạng:

```text-x-trilium-auto
<Novel: Tiên Nghịch>
```

Kiểm tra rằng dataclass sử dụng phiên bản `__repr__` của bạn thay vì phiên bản tự sinh.

---

### Bài 3

Tạo hai dataclass:

```text-x-trilium-auto
@dataclass class Author:
    name: str


@dataclass class Translator:
    name: str
```

So sánh:

```text-x-trilium-auto
Author("Nguyễn Nhật Ánh") == Translator("Nguyễn Nhật Ánh")
```

Giải thích vì sao kết quả là `False` dù dữ liệu giống nhau.

---

## Chuẩn bị cho Buổi 3

Buổi tiếp theo chúng ta sẽ đi sâu vào **Type Hint trong Dataclass**: vì sao `id: int` khác `id = 0`, cách dataclass đọc `__annotations__`, và sử dụng các kiểu như `Optional`, `Union`, `Generic`, `Self`, `Annotated` để xây dựng các mô hình dữ liệu mạnh mẽ, an toàn và dễ bảo trì.