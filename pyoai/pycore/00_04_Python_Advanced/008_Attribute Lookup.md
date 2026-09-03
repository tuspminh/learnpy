# 🐍 Buổi 8 — Attribute Lookup

Chúng ta bắt đầu **Part II — Descriptor & Attribute System**.

Đây là một trong những phần quan trọng nhất để hiểu Python internals.

Khi bạn viết:

```python
user.name
```

Python thực sự làm gì?

Không đơn giản là:

```text
user.__dict__["name"]
```

Mà có một **attribute lookup algorithm** với thứ tự ưu tiên rất cụ thể.

---

# 1. Mục tiêu Buổi 8

Sau buổi này bạn phải hiểu:

```text
user.name
   ↓
Python tìm "name" ở đâu?
   ↓
object.__getattribute__()
   ↓
class / MRO
   ↓
descriptor?
   ↓
instance __dict__?
   ↓
class attribute?
   ↓
__getattr__?
```

Đây là nền móng để hiểu:

```text
property
method
classmethod
staticmethod
ORM
lazy loading
dependency injection
framework
```

---

# 2. Ví dụ đơn giản nhất

```python
class User:
    name = "Class Name"


user = User()

user.age = 20
```

Ta có:

```text
User class
│
├── name = "Class Name"
│
└── __dict__

user instance
│
└── age = 20
```

Khi:

```python
print(user.age)
```

Python tìm `age`.

Khi:

```python
print(user.name)
```

Python phải tìm `name` ở class.

---

# 3. Instance Attribute

Ví dụ:

```python
class User:
    pass


user = User()

user.name = "Alice"
```

Thực tế:

```python
user.__dict__
```

cho:

```python
{
    "name": "Alice"
}
```

Vì vậy:

```python
user.name
```

có thể lấy từ:

```python
user.__dict__["name"]
```

---

# 4. Nhưng không phải attribute nào cũng nằm trong `__dict__`

Ví dụ:

```python
class User:
    role = "admin"
```

Sau:

```python
user = User()
```

Ta có:

```python
print(user.__dict__)
```

```text
{}
```

Nhưng:

```python
print(user.role)
```

vẫn hoạt động:

```text
admin
```

Tại sao?

Vì `role` nằm trong:

```python
User.__dict__
```

---

# 5. Hai namespace

Ta có:

```text
user
 │
 ▼
instance __dict__
```

và:

```text
User
 │
 ▼
class __dict__
```

Ví dụ:

```python
class User:
    role = "admin"


user = User()
user.name = "Alice"
```

Graph:

```text
user.__dict__
└── name → "Alice"


User.__dict__
└── role → "admin"
```

---

# 6. Python phải tìm ở đâu trước?

Đây mới là vấn đề.

Giả sử:

```python
class User:
    name = "Class"


user = User()
user.name = "Instance"
```

Bây giờ:

```python
print(user.name)
```

Kết quả:

```text
Instance
```

Instance attribute thắng class attribute.

Nhưng...

Điều này **không phải lúc nào cũng đúng**.

Đây chính là nơi Descriptor xuất hiện.

---

# 7. `__getattribute__`

Mỗi lần bạn viết:

```python
user.name
```

Python gọi cơ chế attribute access thông qua:

```python
object.__getattribute__(user, "name")
```

Bạn có thể thử:

```python
class User:
    pass


user = User()

user.name = "Alice"

print(
    object.__getattribute__(
        user,
        "name"
    )
)
```

Kết quả:

```text
Alice
```

---

# 8. Override `__getattribute__`

Ta có thể quan sát:

```python
class User:

    def __getattribute__(self, name):
        print("LOOKUP:", name)

        return object.__getattribute__(
            self,
            name
        )
```

Sau:

```python
user = User()

user.name = "Alice"

print(user.name)
```

Output tương tự:

```text
LOOKUP: name
Alice
```

Mỗi lần:

```python
user.x
```

đều đi qua:

```python
__getattribute__
```

---

# 9. Đừng làm lỗi recursion

Sai:

```python
class User:

    def __getattribute__(self, name):
        print(self.__dict__)
```

Tại sao?

Để lấy:

```python
self.__dict__
```

Python lại phải lookup:

```text
self.__dict__
      ↓
__getattribute__
      ↓
self.__dict__
      ↓
__getattribute__
      ↓
...
```

→ infinite recursion.

---

# 10. Cách đúng

Dùng:

```python
object.__getattribute__(
    self,
    "__dict__"
)
```

Ví dụ:

```python
class User:

    def __getattribute__(self, name):
        data = object.__getattribute__(
            self,
            "__dict__"
        )

        print(
            "LOOKUP:",
            name,
            data
        )

        return object.__getattribute__(
            self,
            name
        )
```

---

# 11. Lookup không chỉ là `__dict__`

Đây là mental model quan trọng:

```text
user.name
    ↓
__getattribute__
    ↓
Tìm "name"
    ↓
Class / MRO
    ↓
Descriptor?
    ↓
Instance dictionary?
    ↓
Class attribute?
    ↓
Không tìm thấy
    ↓
__getattr__
```

Nhưng thứ tự chính xác còn phụ thuộc vào việc class attribute có phải **data descriptor** hay không.

---

# 12. Data Descriptor xuất hiện

Đây là ví dụ:

```python
class Descriptor:

    def __get__(self, instance, owner):
        print("DESCRIPTOR GET")
        return "Descriptor value"

    def __set__(self, instance, value):
        print("DESCRIPTOR SET")
```

Sau:

```python
class User:
    name = Descriptor()
```

Ta có:

```text
User
│
└── name
      ↓
Descriptor object
```

Bây giờ:

```python
user = User()

user.name
```

sẽ gọi:

```python
Descriptor.__get__()
```

---

# 13. Data Descriptor vs Instance `__dict__`

Đây là ví dụ cực kỳ quan trọng:

```python
class Descriptor:

    def __get__(self, instance, owner):
        return "DESCRIPTOR"

    def __set__(self, instance, value):
        pass


class User:
    name = Descriptor()


user = User()

user.__dict__["name"] = "INSTANCE"

print(user.name)
```

Bạn có thể nghĩ:

```text
instance __dict__
    ↓
"name" = "INSTANCE"
```

nên kết quả phải là:

```text
INSTANCE
```

Nhưng không.

Kết quả:

```text
DESCRIPTOR
```

Tại sao?

**Data descriptor có độ ưu tiên cao hơn instance dictionary.**

---

# 14. Đây là thứ tự quan trọng

Khi Python lookup:

```python
user.name
```

một cách khái quát:

```text
1. Data Descriptor
2. Instance __dict__
3. Non-data Descriptor / Class Attribute
4. __getattr__
```

Đây là mental model cốt lõi.

---

# 15. Data Descriptor

Một object được xem là data descriptor khi type của nó cung cấp:

```python
__get__
```

và:

```python
__set__
```

hoặc:

```python
__delete__
```

Ví dụ:

```python
class Descriptor:

    def __get__(self, instance, owner):
        ...

    def __set__(self, instance, value):
        ...
```

---

# 16. Non-data Descriptor

Nếu chỉ có:

```python
__get__
```

thì đó là non-data descriptor.

Ví dụ:

```python
class Descriptor:

    def __get__(self, instance, owner):
        return "descriptor"
```

Không có:

```python
__set__
```

---

# 17. Non-data Descriptor vs Instance Attribute

Ví dụ:

```python
class Descriptor:

    def __get__(self, instance, owner):
        return "DESCRIPTOR"


class User:
    name = Descriptor()


user = User()

user.__dict__["name"] = "INSTANCE"

print(user.name)
```

Kết quả:

```text
INSTANCE
```

Vì:

```text
instance __dict__
```

có priority cao hơn **non-data descriptor**.

Đây là sự khác biệt cực kỳ quan trọng.

---

# 18. Tại sao method hoạt động như vậy?

Đây là phần rất thú vị.

Khi bạn viết:

```python
user.login()
```

Python nhìn thấy:

```python
User.login
```

Trong class:

```python
class User:

    def login(self):
        print("login")
```

Function object có cơ chế descriptor.

Vì vậy:

```python
user.login
```

không đơn giản là lấy function từ:

```python
User.__dict__
```

Nó được bind thành method.

---

# 19. Function là Descriptor

Ví dụ:

```python
class User:

    def hello(self):
        return "hello"
```

Kiểm tra:

```python
print(
    hasattr(
        User.__dict__["hello"],
        "__get__"
    )
)
```

Kết quả:

```text
True
```

Function implements descriptor protocol.

---

# 20. Method Binding

Ta có:

```text
User.__dict__["hello"]
        │
        ▼
Function descriptor
        │
        ▼
user.hello
        │
        ▼
bound method
        │
        ▼
hello(user)
```

Đó là lý do:

```python
user.hello()
```

tự động truyền:

```python
self = user
```

---

# 21. Tự mô phỏng Method Binding

Ví dụ:

```python
class User:

    def hello(self):
        return self


user = User()

method = User.__dict__["hello"].__get__(
    user,
    User
)

print(method())
```

Kết quả là:

```text
<__main__.User object ...>
```

Đây chính là descriptor mechanism.

---

# 22. `property` cũng là Descriptor

Ví dụ:

```python
class User:

    @property
    def name(self):
        return "Alice"
```

Khi:

```python
user.name
```

thực tế có descriptor:

```text
property
   ↓
__get__
   ↓
User.name()
```

Vì vậy:

```text
property
method
classmethod
staticmethod
```

đều liên quan rất chặt đến descriptor protocol.

---

# 23. MRO cũng tham gia

Giả sử:

```python
class Animal:
    name = "Animal"


class Dog(Animal):
    pass
```

Khi:

```python
dog = Dog()

print(dog.name)
```

Python cần tìm:

```text
Dog
 ↓
Animal
 ↓
object
```

Đây là:

```python
Dog.__mro__
```

---

# 24. Ví dụ MRO

```python
class A:
    x = "A"


class B(A):
    pass


class C(B):
    pass
```

```python
print(C.__mro__)
```

Conceptually:

```text
C
↓
B
↓
A
↓
object
```

Khi:

```python
c = C()

c.x
```

Python tìm `x` theo MRO.

---

# 25. Mô hình lookup hoàn chỉnh

Hãy hình dung:

```text
                 user.name
                     │
                     ▼
             __getattribute__
                     │
                     ▼
             Search class/MRO
                     │
             ┌───────┴────────┐
             │                │
             ▼                ▼
     Data descriptor?       No
             │                │
            YES               ▼
             │         instance __dict__
             ▼                │
        descriptor            │
          __get__             │
                              ▼
                       found?
                       ┌──────┴──────┐
                       │             │
                      YES            NO
                       │             │
                       ▼             ▼
                    return       class attr /
                                  non-data
                                      │
                                      ▼
                                  found?
                                      │
                                      ▼
                                  return
                                      │
                                     NO
                                      │
                                      ▼
                                 __getattr__
```

Đây là **mental model cực kỳ quan trọng**.

---

# 26. `__getattr__` nằm ở đâu?

Nếu `__getattribute__` không tìm thấy attribute:

```python
user.xyz
```

Python có thể gọi:

```python
__getattr__(user, "xyz")
```

Ví dụ:

```python
class User:

    def __getattr__(self, name):
        return f"{name} does not exist"
```

Bây giờ:

```python
user = User()

print(user.abc)
```

→

```text
abc does not exist
```

---

# 27. Phân biệt `__getattribute__` và `__getattr__`

### `__getattribute__`

Được gọi cho **mọi attribute access**.

```python
user.name
user.email
user.foo
```

### `__getattr__`

Chỉ được gọi khi lookup thông thường **không tìm thấy attribute**.

```text
user.foo
   ↓
__getattribute__
   ↓
not found
   ↓
__getattr__
```

Đây sẽ là nội dung riêng của:

> **Buổi 9 — `__getattribute__`**

và:

> **Buổi 10 — `__getattr__`**

---

# 28. Một thí nghiệm rất đáng chạy

```python
class Demo:

    x = "class"

    def __getattribute__(self, name):
        print("__getattribute__:", name)

        return object.__getattribute__(
            self,
            name
        )

    def __getattr__(self, name):
        print("__getattr__:", name)
        return "fallback"
```

Chạy:

```python
d = Demo()

print(d.x)
print(d.y)
```

Bạn sẽ thấy logic:

```text
__getattribute__: x
class

__getattribute__: y
__getattr__: y
fallback
```

Điều này chứng minh:

```text
__getattr__
```

không phải entry point đầu tiên.

---

# 29. Attribute Assignment cũng có Descriptor

Ta thường chỉ quan tâm:

```python
user.name
```

nhưng:

```python
user.name = "Alice"
```

cũng có cơ chế đặc biệt.

Nếu:

```python
class Descriptor:

    def __set__(self, instance, value):
        print("SET:", value)
```

thì:

```python
class User:
    name = Descriptor()
```

và:

```python
user.name = "Alice"
```

sẽ gọi:

```python
Descriptor.__set__()
```

thay vì đơn giản:

```python
user.__dict__["name"] = "Alice"
```

---

# 30. Đây là nền tảng của ORM

Hãy tưởng tượng:

```python
class User(Model):
    name = StringField()
    age = IntegerField()
```

Bạn viết:

```python
user.name = "Alice"
```

Framework có thể intercept:

```text
user.name = "Alice"
        ↓
StringField.__set__()
        ↓
validate
        ↓
normalize
        ↓
store
```

Và:

```python
user.name
```

có thể:

```text
user.name
    ↓
StringField.__get__()
    ↓
load value
```

Đây chính là cách Descriptor trở thành nền tảng của nhiều framework Python.

---

# 31. ORM Field

Conceptually:

```python
class StringField:

    def __get__(self, instance, owner):
        ...

    def __set__(self, instance, value):
        ...
```

Sau đó:

```python
class User:
    name = StringField()
```

Architecture:

```text
User
 │
 └── name
      │
      ▼
 StringField
      │
 ├── validation
 ├── conversion
 └── storage
```

Đây chính là thứ chúng ta sẽ tự xây trong các buổi Descriptor tiếp theo.

---

# 32. Attribute Lookup và `__dict__`

Một misconception:

> `obj.attribute` luôn tương đương `obj.__dict__["attribute"]`.

Không đúng.

Ví dụ:

```python
class User:
    role = "admin"
```

```python
user = User()
```

```python
user.__dict__
```

là:

```python
{}
```

nhưng:

```python
user.role
```

vẫn có giá trị.

Và với descriptor:

```python
user.name
```

thậm chí có thể **không đọc value từ instance dictionary theo cách thông thường**.

---

# 33. Attribute Lookup và `__slots__`

Sau này bạn sẽ học:

```python
class User:
    __slots__ = ("name",)
```

Khi đó instance có thể không có `__dict__`.

Nhưng:

```python
user.name
```

vẫn hoạt động.

Điều này càng chứng minh:

> Attribute access không đồng nghĩa với `instance.__dict__`.

`__slots__` thực tế dựa rất nhiều vào descriptor machinery.

---

# 34. Tại sao phải học kỹ phần này?

Vì rất nhiều thứ Python "thần kỳ" thực chất không thần kỳ.

Ví dụ:

```python
@property
```

là descriptor.

```python
obj.method
```

liên quan descriptor.

```python
classmethod
```

descriptor.

```python
staticmethod
```

descriptor.

ORM:

```python
user.name
```

descriptor.

Lazy loading:

```python
obj.data
```

descriptor.

Validation:

```python
obj.age = 10
```

descriptor.

Dependency injection:

```python
service.repository
```

có thể dùng descriptor.

---

# 35. Bài tập 1 — Class vs Instance

Dự đoán:

```python
class User:
    name = "Class"


user = User()

user.name = "Instance"

print(user.name)
print(User.name)
```

---

# 36. Bài tập 2 — Shadowing

```python
class User:
    name = "Class"


user = User()

print(user.name)

user.name = "Instance"

print(user.name)

del user.name

print(user.name)
```

Giải thích tại sao sau `del` giá trị lại quay về `"Class"`.

---

# 37. Bài tập 3 — Non-data Descriptor

```python
class Descriptor:

    def __get__(self, instance, owner):
        return "Descriptor"


class User:
    name = Descriptor()


user = User()

user.__dict__["name"] = "Instance"

print(user.name)
```

Dự đoán output.

---

# 38. Bài tập 4 — Data Descriptor

Thêm:

```python
def __set__(self, instance, value):
    pass
```

vào `Descriptor`.

Sau đó:

```python
user.__dict__["name"] = "Instance"

print(user.name)
```

Tại sao kết quả thay đổi?

---

# 39. Bài tập 5 — Method

Chạy:

```python
class User:

    def hello(self):
        return "hello"


user = User()

print(User.__dict__["hello"])
print(user.hello)
print(user.hello())
```

Sau đó kiểm tra:

```python
print(
    hasattr(
        User.__dict__["hello"],
        "__get__"
    )
)
```

Mục tiêu:

> Nhận ra rằng **function trong class là descriptor**.

---

# 40. Bài tập 6 — Tự trace lookup

Viết:

```python
class User:

    name = "Alice"

    def __getattribute__(self, name):
        print("LOOKUP:", name)
        return object.__getattribute__(
            self,
            name
        )
```

Sau đó thử:

```python
user = User()

user.name
user.__dict__
user.foo
```

và quan sát.

---

# 🎯 Tổng kết Buổi 8

Điều quan trọng nhất hôm nay không phải syntax mà là **thứ tự lookup**.

Hãy nhớ mental model:

```text
                    obj.attr
                       │
                       ▼
               __getattribute__
                       │
                       ▼
                   Class/MRO
                       │
                       ▼
              Data Descriptor?
                  │         │
                 YES        NO
                  │         │
                  ▼         ▼
             descriptor   instance
                __get__    __dict__
                              │
                              ▼
                           found?
                              │
                       ┌──────┴──────┐
                      YES            NO
                       │             │
                       ▼             ▼
                    return      class attribute
                                     │
                                     ▼
                                  found?
                                     │
                                  NO │
                                     ▼
                                __getattr__
```

Và 3 câu phải thuộc lòng:

> **Data descriptor thắng instance `__dict__`.**

> **Instance `__dict__` thắng non-data descriptor/class attribute.**

> **`__getattr__` chỉ là fallback sau khi lookup thông thường thất bại.**

---

## 🚀 Buổi 9 — `__getattribute__` Deep Dive

Buổi tiếp theo chúng ta sẽ **mổ xẻ chính `__getattribute__()`**:

```text
obj.attr
   ↓
__getattribute__()
   ↓
object.__getattribute__()
   ↓
descriptor
   ↓
instance dictionary
   ↓
class / MRO
```

Sau đó tự xây:

```python
class LoggedObject:
    ...
```

để log **mọi attribute access**, rồi dùng nó xây một **lazy-loading object** — nền tảng rất hữu ích cho ORM, framework và architecture.
