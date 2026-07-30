# OOP Deep Dive – Buổi 21

# Magic Methods Deep Dive II – Xây dựng Container Pythonic (`__getitem__`, `__setitem__`, `__hash__`, `__eq__`, ...)

> Sau buổi 20, class của bạn đã có thể:
> 
> - in đẹp
> - lặp (`for`)
> - kiểm tra `in`
> - dùng `len()`
> 
> Hôm nay chúng ta sẽ tiến thêm một bước:
> 
> **Biến class của bạn thành một kiểu dữ liệu (container) giống như** `**list**`**,** `**dict**` **và** `**tuple**`**.**

Đây là nhóm magic methods được sử dụng rất nhiều trong:

- Pandas
- NumPy
- PyTorch
- SQLAlchemy
- Django ORM
- pathlib
- requests

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

- `__getitem__()`
- `__setitem__()`
- `__delitem__()`
- `__missing__()`
- `__reversed__()`
- `__index__()`
- `__eq__()`
- `__hash__()`
- Quan hệ giữa `==`, `is`, `hash()`

---

# 1. `__getitem__()`

Bạn đã làm việc với:

```text-x-trilium-auto
numbers = [10,20,30]

print(numbers[1])
```

Python thực chất gọi

```text-x-trilium-auto
numbers.__getitem__(1)
```

---

Ta cũng có thể làm điều này.

```text-x-trilium-auto
class Library:

    def __init__(self):

        self.books = [
            "Python",
            "Django",
            "Flask"
        ]

    def __getitem__(self,index):

        return self.books[index]
```

---

```text-x-trilium-auto
lib = Library()

print(lib[0])
```

↓

```text-x-trilium-auto
Python
```

---

# 2. Slice

Điều thú vị:

```text-x-trilium-auto
lib[0:2]
```

Python vẫn gọi:

```text-x-trilium-auto
__getitem__()
```

Nhưng lần này:

```text-x-trilium-auto
index
```

là

```text-x-trilium-auto
slice(0,2,None)
```

---

Ví dụ

```text-x-trilium-auto
def __getitem__(self,index):

    print(index)

    return self.books[index]
```

Kết quả

```text-x-trilium-auto
slice(0,2,None)
```

---

# 3. Hỗ trợ slice riêng

```text-x-trilium-auto
def __getitem__(self,index):

    if isinstance(index,slice):

        print("Slice")

    else:

        print("Index")

    return self.books[index]
```

---

# 4. `__setitem__()`

Ví dụ

```text-x-trilium-auto
numbers[0]=100
```

↓

Python gọi

```text-x-trilium-auto
numbers.__setitem__(0,100)
```

---

Ta tự viết

```text-x-trilium-auto
class Library:

    def __setitem__(

        self,

        index,

        value

    ):

        self.books[index]=value
```

---

```text-x-trilium-auto
lib[1]="FastAPI"
```

↓

Danh sách thay đổi.

---

# 5. `__delitem__()`

Ví dụ

```text-x-trilium-auto
del lib[1]
```

↓

Python gọi

```text-x-trilium-auto
__delitem__()
```

---

```text-x-trilium-auto
def __delitem__(

    self,

    index

):

    del self.books[index]
```

---

# 6. `__missing__()`

Đây là method khá đặc biệt.

Chỉ hoạt động với **dict subclass**.

Ví dụ

```text-x-trilium-auto
class MyDict(dict):

    def __missing__(self,key):

        return "Not Found"
```

---

```text-x-trilium-auto
d=MyDict()

print(d["abc"])
```

↓

```text-x-trilium-auto
Not Found
```

Thay vì

```text-x-trilium-auto
KeyError
```

---

# 7. Ứng dụng

Ví dụ

```text-x-trilium-auto
config["timeout"]
```

Nếu không tồn tại

↓

Trả về mặc định.

---

# 8. `__reversed__()`

Ví dụ

```text-x-trilium-auto
reversed(obj)
```

↓

Python gọi

```text-x-trilium-auto
__reversed__()
```

---

```text-x-trilium-auto
class Playlist:

    def __reversed__(self):

        return reversed(self.songs)
```

---

```text-x-trilium-auto
for song in reversed(playlist):
```

↓

Hoạt động.

---

# 9. `__index__()`

Đây là magic method ít gặp nhưng rất hữu ích.

Ví dụ

```text-x-trilium-auto
class Number:

    def __index__(self):

        return 5
```

---

```text-x-trilium-auto
n=Number()

print(bin(n))
```

↓

```text-x-trilium-auto
0b101
```

Python gọi

```text-x-trilium-auto
__index__()
```

---

Ứng dụng:

Các object đại diện cho số nguyên có thể dùng trong:

- `bin()`
- `hex()`
- `oct()`
- slicing

Ví dụ

```text-x-trilium-auto
numbers[:Number()]
```

---

# 10. `==`

Ví dụ

```text-x-trilium-auto
class User:

    def __init__(

        self,

        name

    ):

        self.name=name
```

---

```text-x-trilium-auto
u1=User("Alice")

u2=User("Alice")
```

↓

```text-x-trilium-auto
u1==u2
```

↓

```text-x-trilium-auto
False
```

Mặc định:

So sánh identity.

---

# 11. `__eq__()`

```text-x-trilium-auto
class User:

    def __eq__(

        self,

        other

    ):

        return self.name==other.name
```

---

```text-x-trilium-auto
u1==u2
```

↓

```text-x-trilium-auto
True
```

---

# 12. So sánh

```text-x-trilium-auto
is

↓

Identity
```

---

```text-x-trilium-auto
==

↓

Value
```

Ví dụ

```text-x-trilium-auto
a=[]

b=[]
```

↓

```text-x-trilium-auto
a is b
```

↓

False

---

```text-x-trilium-auto
a==b
```

↓

True

---

# 13. `__hash__()`

Hash dùng trong:

- dict
- set

Ví dụ

```text-x-trilium-auto
hash("Python")
```

↓

Một số nguyên.

---

Ta tự viết

```text-x-trilium-auto
class User:

    def __hash__(self):

        return hash(self.name)
```

---

# 14. Quan hệ `__eq__` và `__hash__`

Đây là quy tắc cực kỳ quan trọng.

Nếu

```text-x-trilium-auto
a==b
```

↓

Thì

```text-x-trilium-auto
hash(a)
```

phải bằng

```text-x-trilium-auto
hash(b)
```

---

Ví dụ

```text-x-trilium-auto
class User:

    def __eq__(

        self,

        other

    ):

        return self.name==other.name

    def __hash__(self):

        return hash(self.name)
```

---

# 15. Hashable

Một object hashable:

- immutable (khuyến nghị mạnh)
- hash không đổi

Ví dụ

```text-x-trilium-auto
tuple
str
frozenset
```

Hashable.

---

```text-x-trilium-auto
list
dict
set
```

Không hashable.

---

# 16. Set

```text-x-trilium-auto
users={
    User("Alice"),
    User("Alice")
}
```

Nếu

`__eq__`

và

`__hash__`

đúng

↓

Set chỉ có một phần tử.

---

# 17. Dictionary Key

```text-x-trilium-auto
d={
    User("Alice"):100
}
```

Hoạt động nhờ:

```text-x-trilium-auto
__hash__()
```

---

# 18. Sai lầm phổ biến

Sai

```text-x-trilium-auto
__eq__()
```

Nhưng không có

```text-x-trilium-auto
__hash__()
```

↓

Object không còn hashable (Python thường đặt `__hash__ = None` khi bạn ghi đè `__eq__` mà không định nghĩa lại `__hash__`).

---

# 19. Container hoàn chỉnh

```text-x-trilium-auto
class Library:

    def __getitem__(...):

    def __setitem__(...):

    def __delitem__(...):

    def __len__(...):

    def __iter__(...)
```

Bây giờ

Library

gần giống:

```text-x-trilium-auto
list
```

---

# 20. Áp dụng vào hệ thống crawler

Ví dụ

```text-x-trilium-auto
class NovelCollection
```

Hỗ trợ

```text-x-trilium-auto
collection[0]

collection[2:10]

len(collection)

for novel in collection

del collection[3]
```

Giống hệt list.

---

# 21. Job Queue

```text-x-trilium-auto
queue[0]
```

↓

Job đầu tiên.

---

```text-x-trilium-auto
queue[-1]
```

↓

Job cuối.

---

```text-x-trilium-auto
queue[2:5]
```

↓

Các job.

---

# 22. Cache

```text-x-trilium-auto
cache[url]
```

↓

Novel.

Nếu không có

↓

```text-x-trilium-auto
__missing__()
```

↓

Load từ SQLite.

↓

Lưu cache.

↓

Trả về.

Đây là một kỹ thuật rất hay khi xây dựng cache dựa trên `dict`.

---

# 23. ORM

Ví dụ

```text-x-trilium-auto
book["title"]
```

↓

`__getitem__`

↓

Lấy field.

Một số ORM hoặc thư viện dữ liệu hỗ trợ cú pháp này bên cạnh `book.title`.

---

# 24. Tổng kết

```text-x-trilium-auto
                 Container API

                        │

      ┌─────────────────┼─────────────────┐

      ▼                 ▼                 ▼

 __getitem__      __setitem__      __delitem__

      │

      ▼

 Slice / Index

      │

      ▼

 __eq__

 __hash__

      │

      ▼

 dict / set
```

---

# Điều quan trọng nhất cần nhớ

Một class Pythonic không cần tạo các method như:

```text-x-trilium-auto
library.get(0)

library.remove(1)

library.set(0,obj)
```

Hãy để người dùng sử dụng cú pháp tự nhiên của Python:

```text-x-trilium-auto
library[0]

library[1]=book

del library[2]
```

Đó chính là sức mạnh của Data Model.

---

# Bài tập thực hành

## Bài 1

Viết lớp `Playlist` hỗ trợ:

```text-x-trilium-auto
playlist[0]
playlist[1] = "Song A" del playlist[2]
playlist[1:3]
```

---

## Bài 2

Viết `ConfigDict(dict)`:

- Override `__missing__()`.
- Khi key không tồn tại:

```text-x-trilium-auto
config["timeout"]
```

trả về:

```text-x-trilium-auto
30
```

---

## Bài 3

Viết lớp `User`:

- Có `id` và `name`.
- Hai `User` bằng nhau nếu cùng `id`.
- Triển khai đúng `__eq__()` và `__hash__()`.

Kiểm tra:

```text-x-trilium-auto
users = {
    User(1, "Alice"),
    User(1, "Alice")
}
```

Giải thích vì sao set chỉ còn một phần tử.

---

## Bài 4 (Áp dụng dự án crawler)

Thiết kế lớp:

```text-x-trilium-auto
class NovelRepository:
    ...
```

Hỗ trợ:

- `repo[id]` → lấy truyện theo ID.
- `repo[url]` → lấy truyện theo URL.
- `repo[id] = novel` → cập nhật.
- `del repo[id]` → xóa.
- `len(repo)` → số lượng truyện.
- `for novel in repo` → duyệt tất cả truyện.

Hãy suy nghĩ cách triển khai sao cho vẫn tận dụng SQLite bên dưới nhưng cung cấp một API Pythonic cho người sử dụng.

---

# Chuẩn bị cho Buổi 22

Buổi tiếp theo chúng ta sẽ học nhóm **Magic Methods về toán tử (Operator Overloading)**:

- `__add__()`
- `__sub__()`
- `__mul__()`
- `__truediv__()`
- `__floordiv__()`
- `__mod__()`
- `__pow__()`
- `__matmul__()`
- `__iadd__()` (`+=`)
- `__radd__()` (reverse operator)

Đây là nhóm magic methods được sử dụng nhiều trong:

- NumPy
- Pandas
- PyTorch
- TensorFlow
- SQLAlchemy Expression API

Sau buổi đó, bạn sẽ hiểu cách các thư viện này cho phép viết những biểu thức tự nhiên như:

```text-x-trilium-auto
vector1 + vector2 
matrix_a @ matrix_b 
query1 & query2 
query | other_query
```

mà vẫn thực hiện những logic rất phức tạp phía sau.