# 🐍 Giai đoạn IV — Python Advanced

## Buổi 1 — Python Object Model

Ở các giai đoạn trước, bạn đã học OOP theo góc nhìn **lập trình viên**:

```text
class
object
attribute
method
inheritance
polymorphism
```

Từ hôm nay chúng ta chuyển sang góc nhìn sâu hơn:

> **Python thực sự nhìn nhận class và object như thế nào?**

Đây là nền móng để sau này học **Memory Management → Descriptor → Metaclass → Reflection → Bytecode**.

---

# 1. Mọi thứ trong Python đều là Object

Đây là một trong những ý tưởng quan trọng nhất của Python.

```python
x = 10
```

`10` là object.

```python
name = "Alice"
```

`"Alice"` là object.

```python
numbers = [1, 2, 3]
```

`numbers` trỏ tới một object `list`.

Nhưng chưa hết.

```python
def hello():
    pass
```

`hello` cũng là object.

Class cũng là object:

```python
class User:
    pass
```

`User` cũng là object.

Thậm chí:

```python
int
str
list
User
```

đều là object.

Có thể hình dung:

```text
Python
  │
  └── Object
       ├── int object
       ├── str object
       ├── list object
       ├── function object
       ├── class object
       └── ...
```

---

# 2. Variable không chứa object

Đây là điểm rất quan trọng.

Khi viết:

```python
x = 10
```

Không nên hình dung:

```text
x
│
└── 10
```

mà nên hình dung:

```text
x ─────────► 10
             object
```

`x` là **name**.

`10` là **object**.

Name tham chiếu tới object.

Ví dụ:

```python
x = 10
y = x
```

Ta có:

```text
        ┌───────────┐
x ─────►│           │
        │  int(10)  │
y ─────►│           │
        └───────────┘
```

Hai name cùng tham chiếu tới một object.

Kiểm tra:

```python
x = 10
y = x

print(x is y)
```

Kết quả:

```text
True
```

---

# 3. `id()` — Identity của object

Python cung cấp:

```python
id()
```

Ví dụ:

```python
x = 10

print(id(x))
```

`id(x)` cho biết **identity** của object mà `x` đang tham chiếu.

Ví dụ:

```text
x
│
▼
┌──────────────┐
│ int object   │
│ value = 10   │
│ id = 123456  │
└──────────────┘
```

Bạn có thể kiểm tra:

```python
x = 10
y = x

print(id(x))
print(id(y))
```

Hai giá trị sẽ giống nhau trong trường hợp này.

---

# 4. Identity ≠ Value

Đây là khái niệm cần phân biệt.

Một object có ba khía cạnh quan trọng:

```text
Object
├── Identity
├── Type
└── Value
```

### Identity

Object **là object nào?**

```python
id(obj)
```

### Type

Object thuộc kiểu gì?

```python
type(obj)
```

### Value

Object chứa giá trị gì?

Ví dụ:

```python
x = 100
```

Ta có:

```text
Identity → một object cụ thể
Type     → int
Value    → 100
```

---

# 5. `type()`

```python
x = 100

print(type(x))
```

Kết quả:

```text
<class 'int'>
```

Điều thú vị là:

```python
type(x)
```

cũng trả về **một object**.

Cụ thể:

```text
x
│
▼
int object
│
└── type → int

int
│
▼
class object
```

---

# 6. `isinstance()`

Bạn đã học:

```python
isinstance(x, int)
```

Ví dụ:

```python
x = 100

print(isinstance(x, int))
```

```text
True
```

Nhưng hãy nhìn sâu hơn.

```python
class User:
    pass

user = User()

print(type(user))
print(isinstance(user, User))
```

Kết quả:

```text
<class '__main__.User'>
True
```

---

# 7. Class cũng là Object

Đây là bước chuyển quan trọng.

```python
class User:
    pass
```

Thông thường ta nghĩ:

```text
User = class
```

Nhưng chính xác hơn:

```text
User
 ↓
class object
```

Có thể làm:

```python
class User:
    pass

print(type(User))
```

Kết quả:

```text
<class 'type'>
```

Điều này dẫn tới một câu hỏi rất quan trọng:

> Nếu `User` là object, vậy object `User` thuộc type nào?

Câu trả lời:

```text
User
 ↓
type
```

---

# 8. `type` là gì?

```python
class User:
    pass

print(type(User))
```

```text
<class 'type'>
```

Tức là:

```text
User
   │
   │ instance of
   ▼
 type
```

Nói cách khác:

> **Class trong Python là instance của một metaclass.**

Trong trường hợp thông thường, metaclass đó là:

```python
type
```

---

# 9. Object → Class → Metaclass

Đây là mô hình chúng ta sẽ sử dụng xuyên suốt phần Advanced.

Ví dụ:

```python
class User:
    pass

user = User()
```

Ta có:

```text
user
 │
 │ instance of
 ▼
User
 │
 │ instance of
 ▼
type
```

Hay:

```text
user ─────► User ─────► type
 object      class      metaclass
```

Đây chính là nền tảng của **Metaclass** mà chúng ta sẽ học ở Phần IV.

---

# 10. `__class__`

Python cho phép xem class của object:

```python
x = 10

print(x.__class__)
```

Kết quả:

```text
<class 'int'>
```

Tương đương:

```python
type(x)
```

Thông thường:

```python
x.__class__ is type(x)
```

là:

```text
True
```

---

# 11. Class cũng có `__class__`

Ví dụ:

```python
class User:
    pass

print(User.__class__)
```

Kết quả:

```text
<class 'type'>
```

Ta có:

```text
user.__class__  → User
User.__class__  → type
```

Đây là một trong những câu lệnh rất đáng nhớ:

```python
obj.__class__
```

---

# 12. `__dict__`

Object Python thường có namespace.

Ví dụ:

```python
class User:
    name = "Alice"
```

Ta có:

```python
print(User.__dict__)
```

Bạn sẽ thấy một mapping chứa các thành phần của class:

```text
{
    '__module__': ...,
    'name': 'Alice',
    '__dict__': ...,
    '__weakref__': ...,
    '__doc__': ...
}
```

`__dict__` của class cho chúng ta thấy:

> Class đang chứa những attribute nào?

---

# 13. Instance `__dict__`

Ví dụ:

```python
class User:
    pass

user = User()

user.name = "Alice"
user.age = 20
```

Bây giờ:

```python
print(user.__dict__)
```

Kết quả:

```python
{
    "name": "Alice",
    "age": 20
}
```

Ta có:

```text
User
 │
 └── class namespace
       │
       ├── ...
       └──

user
 │
 └── instance namespace
       │
       ├── name = "Alice"
       └── age = 20
```

---

# 14. Class attribute vs Instance attribute

Ví dụ:

```python
class User:
    species = "Human"

user = User()

user.name = "Alice"
```

Ta có:

```text
User
├── species = "Human"
│
└── ...

user
└── name = "Alice"
```

Kiểm tra:

```python
print(User.__dict__)
print(user.__dict__)
```

`species` thuộc class.

`name` thuộc instance.

---

# 15. Attribute Lookup

Khi bạn viết:

```python
user.name
```

Python phải tìm `name`.

Một cách đơn giản hóa:

```text
user.name
   │
   ▼
instance/class attribute lookup
   │
   ├── instance
   │
   ├── descriptor
   │
   └── class / MRO
```

Phần này sẽ cực kỳ quan trọng khi chúng ta học:

> **Descriptor**

và sau này:

> `__getattribute__`

---

# 16. MRO

Ví dụ:

```python
class Animal:
    pass

class Dog(Animal):
    pass
```

Kiểm tra:

```python
print(Dog.__mro__)
```

Kết quả dạng:

```text
(
    <class '__main__.Dog'>,
    <class '__main__.Animal'>,
    <class 'object'>
)
```

Python tìm attribute/method theo **MRO — Method Resolution Order**.

```text
Dog
 ↓
Animal
 ↓
object
```

---

# 17. `object`

Một câu hỏi quan trọng:

> `object` là gì?

```python
print(type(object))
```

Kết quả:

```text
<class 'type'>
```

Và:

```python
print(object.__class__)
```

cũng là:

```text
<class 'type'>
```

Trong Python 3, class thông thường cuối cùng đều có:

```text
object
```

trong inheritance hierarchy.

Ví dụ:

```python
class User:
    pass
```

thực chất có thể hiểu như:

```python
class User(object):
    pass
```

---

# 18. Mô hình tổng quát

Đây là sơ đồ bạn nên ghi nhớ:

```text
                 ┌─────────────┐
                 │    type     │
                 └──────┬──────┘
                        │
                  instance of
                        │
                        ▼
                 ┌─────────────┐
                 │    User     │
                 └──────┬──────┘
                        │
                  instance of
                        │
                        ▼
                 ┌─────────────┐
                 │    user     │
                 └─────────────┘
```

Trong đó:

```text
user
 ↓
User
 ↓
type
```

Nhưng inheritance lại là:

```text
User
 ↓ inherits
object
```

Đây là **hai quan hệ khác nhau**:

```text
instance relationship

user ─────► User
User ─────► type
```

và:

```text
inheritance relationship

User ─────► object
```

Đừng nhầm hai loại quan hệ này.

---

# 19. Một ví dụ tổng hợp

Hãy chạy:

```python
class User:
    species = "Human"

    def __init__(self, name):
        self.name = name


user = User("Alice")

print("user:", user)
print("type(user):", type(user))
print("user.__class__:", user.__class__)

print("User:", User)
print("type(User):", type(User))
print("User.__class__:", User.__class__)

print("user.__dict__:", user.__dict__)
print("User.__dict__:", User.__dict__)

print("User.__mro__:", User.__mro__)
```

Hãy đặc biệt quan sát:

```text
type(user)
```

và:

```text
type(User)
```

---

# 20. Mô hình tư duy mới

Từ hôm nay, thay vì nghĩ:

```python
x = 10
```

là:

> x chứa 10

hãy nghĩ:

```text
x ───────► object
             │
             ├── identity
             ├── type
             └── value
```

Và:

```python
user = User()
```

là:

```text
user
 │
 ▼
┌───────────────┐
│ User instance │
│               │
│ __dict__      │
└───────┬───────┘
        │
        │ __class__
        ▼
┌───────────────┐
│ User          │
│ class object  │
└───────┬───────┘
        │
        │ __class__
        ▼
┌───────────────┐
│ type          │
└───────────────┘
```

---

# 🧠 21. Những điều cần nhớ sau Buổi 1

### ① Python variable là name

```python
x = object()
```

Không phải `x` chứa object; `x` **tham chiếu tới object**.

### ② Object có

```text
Identity
Type
Value
```

### ③ `type()`

Cho biết type của object.

### ④ `id()`

Cho biết identity của object.

### ⑤ `__class__`

Cho biết class/type của object.

### ⑥ Class cũng là object

```python
class User:
    pass

type(User)
# <class 'type'>
```

### ⑦ Class thông thường là instance của `type`

```text
User → type
```

### ⑧ Instance là instance của class

```text
user → User
```

### ⑨ Inheritance khác instance relationship

```text
user ──instance──► User ──instance──► type

User ──inherit──► object
```

---

# 🧪 Bài tập Buổi 1

Không cần làm tất cả ngay; hãy tự chạy từng câu và **dự đoán kết quả trước**.

### Bài 1

```python
x = 100
y = x

print(x is y)
print(id(x))
print(id(y))
print(type(x))
```

---

### Bài 2

```python
class Person:
    pass

p = Person()

print(type(p))
print(type(Person))
print(p.__class__)
print(Person.__class__)
```

Hãy giải thích quan hệ:

```text
p
Person
type
object
```

---

### Bài 3

```python
class User:
    role = "admin"

user = User()
user.name = "Alice"

print(user.__dict__)
print(User.__dict__)
```

Câu hỏi:

**Tại sao `name` nằm trong `user.__dict__` nhưng `role` lại nằm trong `User.__dict__`?**

---

### Bài 4 — Quan trọng

Không được chạy trước, hãy dự đoán:

```python
class A:
    pass

a = A()

print(type(a))
print(type(A))
print(type(type))
print(type(object))
print(A.__class__)
print(object.__class__)
```

Sau đó mới chạy để kiểm chứng.

---

### Bài 5 — Suy luận

Giải thích bằng sơ đồ:

```python
class Animal:
    pass

class Dog(Animal):
    pass

dog = Dog()
```

Hãy vẽ:

```text
dog
 ↓
 ?
 ↓
 ?
```

và inheritance:

```text
Dog
 ↓
 ?
```

---

## 🎯 Preview Buổi 2

Buổi tiếp theo chúng ta sẽ đi sâu vào:

# **Memory Management — Python lưu Object trong bộ nhớ như thế nào?**

Từ:

```text
name
 ↓
object
 ↓
memory
```

chúng ta sẽ bắt đầu khám phá:

```text
Python Memory Manager
        ↓
CPython
        ↓
Heap
        ↓
Object Header
        ↓
Reference Count
        ↓
Allocator
        ↓
pymalloc
```

Đây sẽ là nền tảng trực tiếp cho **Buổi 3 — Reference Counting** và **Buổi 4 — Garbage Collector**.
