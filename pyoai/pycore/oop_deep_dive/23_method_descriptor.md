# OOP Deep Dive — Buổi 23

# Method cũng là Descriptor

Đây là một buổi **rất quan trọng**.

Ở Buổi 5 chúng ta đã học:

* Function object
* Bound method
* Unbound method

Ở Buổi 21 chúng ta học:

* Descriptor
* `__get__`
* Data Descriptor
* Non-data Descriptor

Ở Buổi 22 chúng ta học:

* `property` thực chất là Descriptor.

Hôm nay chúng ta **nối cả ba kiến thức lại**:

```text
Function Object
      ↓
Function cũng là Descriptor
      ↓
function.__get__()
      ↓
Bound Method
      ↓
self được truyền tự động
```

Sau buổi này, câu:

```python
user.hello()
```

sẽ không còn là "Python tự động truyền `self`" một cách bí ẩn nữa.

---

# 1. Bắt đầu từ một class đơn giản

```python
class User:

    def hello(self):
        print("Hello")
```

Tạo object:

```python
user = User()
```

Ta gọi:

```python
user.hello()
```

Kết quả:

```text
Hello
```

Nhưng câu hỏi là:

> `hello` nằm ở đâu?

---

# 2. Kiểm tra `User.__dict__`

```python
print(User.__dict__)
```

Trong đó sẽ có đại loại:

```text
{
    ...
    'hello': <function User.hello at ...>,
    ...
}
```

Điểm quan trọng:

```python
User.__dict__["hello"]
```

là một **function object**.

---

# 3. Function nằm trên class

Ta có:

```text
User
 │
 └── __dict__
       │
       └── hello
             │
             ▼
        function object
```

Còn:

```python
user.__dict__
```

thường không có:

```python
"hello"
```

Ví dụ:

```python
user.__dict__
```

có thể là:

```python
{}
```

---

# 4. Nhưng `user.hello` lại tồn tại

Đây là điều thú vị.

```python
print(user.hello)
```

Bạn sẽ thấy dạng:

```text
<bound method User.hello of <User object ...>>
```

Trong khi:

```python
print(User.__dict__["hello"])
```

lại là:

```text
<function User.hello ...>
```

Vậy:

```python
User.__dict__["hello"]
```

và:

```python
user.hello
```

**không phải cùng một object**.

---

# 5. Function là Descriptor

Đây chính là bí mật.

Function object triển khai Descriptor Protocol.

Về mặt khái niệm, function có:

```python
__get__()
```

Do đó:

```python
user.hello
```

có thể hiểu về mặt cơ chế là:

```python
User.__dict__["hello"].__get__(
    user,
    User
)
```

---

# 6. Đây chính là Bound Method

Kết quả của:

```python
function.__get__(
    user,
    User
)
```

là một:

```text
bound method
```

Ví dụ:

```python
method = User.__dict__["hello"].__get__(
    user,
    User
)
```

Sau đó:

```python
method()
```

hoạt động.

---

# 7. `self` từ đâu ra?

Đây là câu hỏi quan trọng nhất.

Ta có:

```python
def hello(self):
    print("Hello")
```

Function yêu cầu một argument:

```python
self
```

Nhưng ta gọi:

```python
user.hello()
```

không truyền argument.

Tại sao không lỗi?

Bởi vì:

```python
user.hello
```

đã tạo ra **bound method**.

Bound method đã "bind" object:

```python
user
```

vào function.

Có thể hình dung:

```text
hello(self)
     │
     │ bind
     ▼
hello(user)
```

Do đó:

```python
user.hello()
```

thực chất tương đương về ý nghĩa với:

```python
User.hello(user)
```

---

# 8. So sánh trực tiếp

```python
class User:

    def hello(self):
        print(self)
```

Ta có:

```python
user = User()
```

### Cách 1

```python
user.hello()
```

### Cách 2

```python
User.hello(user)
```

Hai cách đều truyền `user` làm `self`.

---

# 9. `User.hello` khác `user.hello`

Đây là điểm cực kỳ quan trọng.

```python
User.hello
```

là:

```text
function
```

Còn:

```python
user.hello
```

là:

```text
bound method
```

---

# 10. Quan sát

```python
print(User.hello)
```

Có dạng:

```text
<function User.hello at ...>
```

Còn:

```python
print(user.hello)
```

có dạng:

```text
<bound method User.hello of <User ...>>
```

---

# 11. Function Descriptor hoạt động thế nào?

Có thể mô phỏng:

```python
class MyFunction:

    def __get__(self, instance, owner):

        if instance is None:
            return self

        return BoundMethod(
            self,
            instance
        )
```

Đây chưa phải implementation thật của Python, nhưng mô hình tư duy là chính xác.

---

# 12. Bound Method là gì?

Một bound method có thể hình dung gồm:

```text
┌──────────────────┐
│ Bound Method     │
├──────────────────┤
│ function         │ → hello
│ instance         │ → user
└──────────────────┘
```

Nó giữ:

```python
function
```

và:

```python
instance
```

---

# 13. Kiểm tra `__self__`

Ví dụ:

```python
class User:

    def hello(self):
        pass
```

```python
user = User()

method = user.hello
```

Ta có:

```python
print(method.__self__)
```

Kết quả:

```text
<User object ...>
```

Đó chính là:

```python
user
```

---

# 14. Kiểm tra `__func__`

```python
print(method.__func__)
```

Kết quả:

```text
<function User.hello ...>
```

Tức là bound method giữ:

```python
method.__self__
```

và:

```python
method.__func__
```

---

# 15. Sơ đồ rất quan trọng

```text
User.__dict__["hello"]
        │
        ▼
 Function Object
        │
        │ __get__(user, User)
        ▼
   Bound Method
      /     \
     /       \
    ▼         ▼
__func__    __self__
    │          │
    ▼          ▼
  hello       user
```

Khi gọi:

```python
user.hello()
```

Python dùng:

```text
__func__(__self__)
```

tức:

```python
hello(user)
```

---

# 16. `self` không phải keyword đặc biệt

Đây là một hiểu lầm phổ biến.

Python không yêu cầu tên:

```python
self
```

Bạn có thể viết:

```python
class User:

    def hello(this):
        print(this)
```

vẫn chạy:

```python
user.hello()
```

`self` chỉ là **quy ước đặt tên**.

Cơ chế thật nằm ở:

```text
Descriptor
+
Bound Method
```

---

# 17. Thử đổi tên

```python
class User:

    def hello(x):
        print(x)
```

```python
user = User()

user.hello()
```

Python vẫn bind:

```text
user
```

vào parameter đầu tiên.

---

# 18. Tự gọi `__get__`

Ta có thể truy cập function:

```python
func = User.__dict__["hello"]
```

Sau đó:

```python
bound = func.__get__(user, User)
```

Bây giờ:

```python
bound()
```

hoạt động.

---

# 19. Điều này cực kỳ quan trọng

Bạn có thể xem:

```python
user.hello
```

về mặt cơ chế gần như:

```python
User.__dict__["hello"].__get__(
    user,
    User
)
```

Đây chính là Descriptor Protocol đang hoạt động.

---

# 20. Class Access

Nếu:

```python
User.hello
```

thì:

```python
instance = None
```

Descriptor nhận:

```python
func.__get__(None, User)
```

Và function trả về chính function.

Do đó:

```python
User.hello
```

vẫn là function.

---

# 21. Vì vậy `instance=None` rất quan trọng

Ta có mô hình:

```text
User.hello
     │
     ▼
function.__get__(None, User)
     │
     ▼
function
```

Trong khi:

```text
user.hello
     │
     ▼
function.__get__(user, User)
     │
     ▼
bound method
```

---

# 22. Đây chính là pattern Descriptor

Bạn đã thấy pattern này ở Buổi 21:

```python
def __get__(self, instance, owner):

    if instance is None:
        return self

    ...
```

Function cũng có logic tương tự về mặt ý tưởng.

---

# 23. Tại sao method không nằm trong `user.__dict__`?

Vì không cần.

Python có thể lấy function từ class:

```python
User.__dict__["hello"]
```

rồi bind nó với:

```python
user
```

Mỗi lần truy cập:

```python
user.hello
```

Python có thể tạo ra bound method tương ứng.

---

# 24. Method là Non-data Descriptor

Function có:

```python
__get__()
```

nhưng không có:

```python
__set__()
```

Do đó function là:

> **Non-data Descriptor**

Điều này cực kỳ quan trọng.

---

# 25. Shadowing Method

Vì function là Non-data Descriptor, instance attribute có thể shadow nó.

Ví dụ:

```python
class User:

    def hello(self):
        return "method"
```

Sau đó:

```python
user = User()

user.hello = "attribute"
```

Bây giờ:

```python
print(user.hello)
```

Kết quả:

```text
attribute
```

---

# 26. Tại sao?

Lookup:

```text
user.hello
```

Python thấy:

```text
Data Descriptor?
```

Không.

Sau đó kiểm tra:

```python
user.__dict__
```

Có:

```python
"hello": "attribute"
```

→ lấy giá trị đó.

Function bị shadow.

---

# 27. Đây là sự khác biệt giữa `property` và method

### Property

```text
Data Descriptor
```

nên:

```text
property
>
instance.__dict__
```

### Method

```text
Non-data Descriptor
```

nên:

```text
instance.__dict__
>
method
```

Đây là một kiến thức rất sâu của Python OOP.

---

# 28. Xóa shadow

```python
del user.hello
```

Sau đó:

```python
user.hello()
```

lại hoạt động.

Vì instance không còn:

```python
"hello"
```

trong `__dict__`.

Python quay lại class:

```python
User.__dict__["hello"]
```

và bind method.

---

# 29. Bound Method không phải function

Ví dụ:

```python
user.hello
```

có:

```python
__self__
```

nhưng function:

```python
User.hello
```

không có bound instance.

Ta có:

```python
method.__self__ is user
```

↓

```text
True
```

---

# 30. `__func__`

```python
method = user.hello

print(method.__func__ is User.hello)
```

Kết quả:

```text
True
```

Điều này cho thấy:

```text
bound method
    =
function
+
instance
```

---

# 31. Method với nhiều arguments

```python
class Calculator:

    def add(self, a, b):
        return a + b
```

Khi:

```python
calc = Calculator()
```

thì:

```python
calc.add(10, 20)
```

về ý tưởng:

```python
Calculator.add(calc, 10, 20)
```

---

# 32. Descriptor không chỉ dùng cho method

Đây là điều cần mở rộng tư duy.

Python dùng Descriptor cho:

```text
method
property
classmethod
staticmethod
```

và nhiều cơ chế framework.

---

# 33. `classmethod`

Ví dụ:

```python
class User:

    @classmethod
    def create(cls):
        return cls()
```

Khi:

```python
User.create()
```

Python cũng đang sử dụng Descriptor.

`classmethod` object triển khai cơ chế `__get__()` để bind:

```text
class
```

thay vì instance.

---

# 34. `staticmethod`

Ví dụ:

```python
class Math:

    @staticmethod
    def add(a, b):
        return a + b
```

Khi:

```python
Math.add(1, 2)
```

không có instance được bind.

Đây cũng liên quan đến Descriptor.

---

# 35. So sánh

| Thành phần      | Descriptor? | Bind gì?          |
| --------------- | ----------: | ----------------- |
| instance method |           ✅ | instance          |
| `classmethod`   |           ✅ | class             |
| `staticmethod`  |           ✅ | không bind        |
| `property`      |           ✅ | instance → getter |

---

# 36. Đây là một trong những lý do Python rất linh hoạt

Cùng cú pháp:

```python
obj.attr
```

nhưng `attr` có thể là:

```text
instance attribute
class attribute
property
method
classmethod
staticmethod
custom descriptor
```

Python quyết định hành vi dựa trên **Descriptor Protocol + Attribute Lookup**.

---

# 37. Liên hệ Buổi 5

Ở Buổi 5 ta đã nói:

```text
Function Object
Bound Method
```

Bây giờ ta hiểu cơ chế phía dưới:

```text
Function Object
       ↓
Function là Descriptor
       ↓
__get__()
       ↓
Bound Method
       ↓
__self__ + __func__
```

Như vậy kiến thức cũ được giải thích bằng một cơ chế sâu hơn.

---

# 38. Tự xây dựng Bound Method đơn giản

Để hiểu bản chất, ta có thể mô phỏng.

```python
class BoundMethod:

    def __init__(self, func, instance):
        self.func = func
        self.instance = instance

    def __call__(self, *args, **kwargs):
        return self.func(
            self.instance,
            *args,
            **kwargs
        )
```

---

# 39. Descriptor tự tạo

```python
class MyMethod:

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):

        if instance is None:
            return self.func

        return BoundMethod(
            self.func,
            instance
        )
```

---

# 40. Sử dụng

```python
class User:

    def hello(self):
        print("Hello")

    hello = MyMethod(hello)
```

Bây giờ:

```python
user = User()

user.hello()
```

sẽ hoạt động thông qua Descriptor của chúng ta.

---

# 41. Luồng thực thi

```text
user.hello()
    │
    ▼
User.__dict__["hello"]
    │
    ▼
MyMethod
    │
    ▼
MyMethod.__get__(user, User)
    │
    ▼
BoundMethod
    │
    ▼
BoundMethod.__call__()
    │
    ▼
func(user)
```

Đây chính là bài học quan trọng nhất hôm nay.

---

# 42. Tại sao đây là kiến thức Framework?

Bởi vì framework có thể dùng Descriptor để thay đổi ý nghĩa của:

```python
obj.attribute
```

Ví dụ:

```python
user.name
```

có thể là:

```text
property
```

hoặc:

```text
ORM Field
```

hoặc:

```text
lazy loader
```

hoặc:

```text
computed field
```

Còn:

```python
user.save()
```

là:

```text
function descriptor
→ bound method
```

---

# 43. Liên hệ ORM

Ví dụ ORM:

```python
class User:

    name = StringField()
```

`StringField` có thể là Descriptor.

Còn:

```python
class User:

    def save(self):
        ...
```

`save` là function Descriptor.

Do đó một model ORM có thể chứa:

```text
User
 │
 ├── name
 │     ↓
 │   Field Descriptor
 │
 ├── age
 │     ↓
 │   Field Descriptor
 │
 └── save
       ↓
     Function Descriptor
```

Đây chính là nền tảng rất quan trọng để hiểu ORM ở Buổi 24.

---

# 44. Một thí nghiệm rất đáng làm

Chạy:

```python
class User:

    def hello(self):
        return "hello"


user = User()

print(User.__dict__["hello"])
print(User.hello)
print(user.hello)

print(type(User.__dict__["hello"]))
print(type(User.hello))
print(type(user.hello))
```

Bạn sẽ quan sát được:

```text
User.__dict__["hello"]
        ↓
function

User.hello
        ↓
function

user.hello
        ↓
method
```

---

# 45. Thí nghiệm `__self__`

```python
method = user.hello

print(method.__self__)
print(method.__func__)
```

Ta có:

```text
__self__
   ↓
user

__func__
   ↓
User.hello
```

---

# 46. Một insight rất quan trọng

Khi viết:

```python
user.hello()
```

đừng hình dung:

```text
Python tìm hello
↓
Python thấy function
↓
Python tự thêm self
```

Cách hiểu sâu hơn là:

```text
user.hello
    ↓
attribute lookup
    ↓
function descriptor
    ↓
function.__get__(user, User)
    ↓
bound method
    ↓
bound method()
    ↓
function(user)
```

Đây là cách tư duy đúng ở mức Python internals.

---

# 47. So sánh Property và Method

## Property

```python
user.name
```

```text
property
 ↓
__get__
 ↓
getter
```

## Method

```python
user.hello
```

```text
function
 ↓
__get__
 ↓
bound method
```

Hai cơ chế khác nhau nhưng đều dựa trên:

> **Descriptor Protocol**

---

# 48. Tổng hợp Descriptor từ Buổi 21 → 23

```text
                 Descriptor
                     │
          ┌──────────┼───────────┐
          │          │           │
          ▼          ▼           ▼
       property    method      custom
          │          │        descriptor
          ▼          ▼           │
       __get__    __get__        │
       __set__                  ...
          │
          ▼
      getter/setter
```

---

# 49. Bài tập

## Bài 1

Giải thích kết quả:

```python
class A:

    def hello(self):
        return "hello"


a = A()

print(A.hello)
print(a.hello)
```

Tại sao hai kết quả khác nhau?

---

## Bài 2

Giải thích:

```python
method = a.hello

print(method.__self__)
print(method.__func__)
```

`__self__` và `__func__` là gì?

---

## Bài 3

Không dùng `@property`, hãy tự xây:

```python
class MyProperty:
    ...
```

với:

```python
class User:

    def get_name(self):
        return self._name

    def set_name(self, value):
        self._name = value

    name = MyProperty(
        get_name,
        set_name
    )
```

Phải hỗ trợ:

```python
user.name
user.name = "Alice"
```

---

# 50. Bài tập Deep Dive — tự mô phỏng Method

Viết:

```python
class BoundMethod:
    ...
```

và:

```python
class MethodDescriptor:
    ...
```

sao cho:

```python
class User:

    def hello(self, name):
        return f"Hello {name}"

    hello = MethodDescriptor(hello)
```

có thể:

```python
user = User()

print(user.hello("Alice"))
```

cho kết quả:

```text
Hello Alice
```

---

# 51. Câu hỏi kiểm tra tư duy

Không cần code, hãy trả lời:

### Câu 1

Tại sao:

```python
User.__dict__["hello"]
```

là function nhưng:

```python
user.hello
```

là bound method?

### Câu 2

`self` được bind ở đâu?

### Câu 3

Tại sao function là **Non-data Descriptor**?

### Câu 4

Tại sao instance có thể shadow method?

```python
user.hello = "something"
```

### Câu 5

Tại sao property lại không dễ bị shadow như method?

Nếu trả lời được 5 câu này, bạn đã nắm khá chắc Descriptor.

---

# 52. Bức tranh lớn

Đến đây chúng ta đã đi được:

```text
Buổi 5
Function Object
     │
     ▼
Buổi 21
Descriptor Protocol
     │
     ├──────────────┐
     ▼              ▼
Buổi 22          Buổi 23
property         method
     │              │
     ▼              ▼
__get__          __get__
__set__          bound method
     │              │
     └──────┬───────┘
            ▼
      Attribute Access
```

Và đây chính là nền móng để bước sang:

# **Buổi 24 — ORM sử dụng Descriptor**

Chúng ta sẽ tự xây dựng một **Mini ORM** rất nhỏ:

```python
class User(Model):

    id = IntegerField()
    name = StringField()
    age = IntegerField()
```

rồi phân tích:

```python
user.name
```

→ Descriptor

```python
user.name = "Alice"
```

→ Descriptor

```python
User.name
```

→ Field metadata

và cuối cùng:

```text
Model
  ↓
Descriptor
  ↓
Field metadata
  ↓
Repository
  ↓
SQLite
```

Đó sẽ là nơi toàn bộ kiến thức **OOP + Descriptor + Repository + SQLite** mà bạn đang học bắt đầu kết nối thành một hệ thống thực tế.
    