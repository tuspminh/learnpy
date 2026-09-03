# 🐍 Buổi 9 — `__getattribute__()` Deep Dive

Hôm nay chúng ta đi sâu vào **trung tâm của Attribute Lookup**.

Nếu Buổi 8 trả lời:

> Python tìm `obj.attr` ở đâu?

thì Buổi 9 trả lời:

> **`__getattribute__()` thực sự kiểm soát việc đó như thế nào?**

---

# 1. `__getattribute__()` là gì?

Mỗi khi bạn viết:

```python
user.name
```

Python thực hiện attribute access thông qua:

```python
user.__getattribute__("name")
```

Ở mức khái niệm:

```text
user.name
   │
   ▼
__getattribute__(user, "name")
   │
   ▼
attribute lookup machinery
```

`__getattribute__()` đặc biệt ở chỗ:

> Nó được gọi cho **mọi attribute access**.

---

# 2. Ví dụ cơ bản

```python
class User:

    def __getattribute__(self, name):
        print("GET:", name)

        return object.__getattribute__(self, name)
```

Sử dụng:

```python
user = User()

user.name
```

Output:

```text
GET: name
```

Nhưng `name` không tồn tại nên cuối cùng sẽ có:

```text
AttributeError
```

---

# 3. Tại sao gọi `object.__getattribute__()`?

Đây là điểm cực kỳ quan trọng.

Ta override:

```python
class User:

    def __getattribute__(self, name):
        ...
```

Nhưng chúng ta vẫn cần Python thực hiện lookup chuẩn.

Vì vậy:

```python
return object.__getattribute__(self, name)
```

có nghĩa:

> "Sau khi tôi can thiệp, hãy giao việc lookup thực sự cho implementation mặc định."

Mental model:

```text
user.name
    │
    ▼
User.__getattribute__()
    │
    ├── logging
    ├── permission
    ├── debugging
    └── ...
    │
    ▼
object.__getattribute__()
    │
    ▼
normal attribute lookup
```

---

# 4. Sai lầm kinh điển: recursion

Đừng viết:

```python
class User:

    def __getattribute__(self, name):
        print(self.__dict__)
```

Tại sao?

Bạn đang xử lý:

```python
self.__dict__
```

Nhưng chính việc đó lại là một attribute lookup.

```text
self.__dict__
     ↓
__getattribute__()
     ↓
self.__dict__
     ↓
__getattribute__()
     ↓
...
```

→ `RecursionError`.

---

# 5. Cách tránh recursion

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

        print("GET:", name)
        print("DICT:", data)

        return object.__getattribute__(
            self,
            name
        )
```

---

# 6. `__getattribute__()` bắt mọi attribute

Ví dụ:

```python
class User:

    role = "admin"

    def hello(self):
        return "hello"

    def __getattribute__(self, name):
        print("LOOKUP:", name)

        return object.__getattribute__(
            self,
            name
        )
```

Chạy:

```python
user = User()

user.role
user.hello
user.__dict__
```

Bạn sẽ thấy:

```text
LOOKUP: role
LOOKUP: hello
LOOKUP: __dict__
```

---

# 7. Method cũng đi qua `__getattribute__`

Điều này rất đáng chú ý.

```python
user.hello()
```

không chỉ là:

```text
gọi hello()
```

Mà trước tiên:

```text
user.hello
    ↓
__getattribute__("hello")
    ↓
descriptor lookup
    ↓
bound method
    ↓
()
```

Sau đó mới gọi method.

---

# 8. Vì sao method tự nhận `self`?

Xét:

```python
class User:

    def hello(self):
        return "Hello"
```

Trong:

```python
User.__dict__
```

`hello` là function.

Nhưng:

```python
user.hello
```

trả về **bound method**.

Conceptually:

```text
User.__dict__["hello"]
        │
        ▼
    function
        │
        │ __get__
        ▼
user.hello
        │
        ▼
bound method
        │
        ▼
hello(user)
```

Đây là descriptor machinery.

Descriptor sẽ học kỹ ở Buổi 11.

---

# 9. `__getattribute__()` có thể thay đổi behavior

Ví dụ logging:

```python
class LoggedObject:

    def __getattribute__(self, name):
        print(f"Accessing: {name}")

        return object.__getattribute__(
            self,
            name
        )
```

Sử dụng:

```python
class User(LoggedObject):

    name = "Alice"
    age = 20
```

```python
user = User()

print(user.name)
print(user.age)
```

Output:

```text
Accessing: name
Alice

Accessing: age
20
```

---

# 10. Logging thực tế hơn

Ta có thể log trước và sau:

```python
class LoggedObject:

    def __getattribute__(self, name):
        print(f"[GET] {name}")

        value = object.__getattribute__(
            self,
            name
        )

        print(f"[VALUE] {value}")

        return value
```

Ví dụ:

```python
class User(LoggedObject):

    name = "Alice"
```

```python
user = User()

print(user.name)
```

Conceptually:

```text
[GET] name
[VALUE] Alice
Alice
```

---

# 11. Nhưng có một vấn đề

Nếu `value` là object lớn:

```python
print(f"[VALUE] {value}")
```

có thể gây side effect hoặc recursion.

Ví dụ một object có `__repr__()` phức tạp.

Vì vậy instrumentation trong framework cần rất cẩn thận.

---

# 12. `__getattribute__()` có thể chặn attribute

Ví dụ security:

```python
class SecureUser:

    password = "secret"

    def __getattribute__(self, name):

        if name == "password":
            raise AttributeError(
                "password is private"
            )

        return object.__getattribute__(
            self,
            name
        )
```

Bây giờ:

```python
user = SecureUser()

print(user.password)
```

→ `AttributeError`.

---

# 13. Nhưng đây chưa phải security thực sự

Không nên nghĩ:

```python
__getattribute__
```

là một hệ thống security mạnh.

Python thiên về:

> "we are all consenting adults"

Nó phù hợp để:

* enforce convention
* validation
* instrumentation
* lazy loading
* proxy
* framework behavior

hơn là security boundary tuyệt đối.

---

# 14. Proxy Object

Đây là ứng dụng rất quan trọng.

Giả sử:

```python
class User:

    def hello(self):
        return "hello"
```

Ta muốn một proxy đứng trước:

```text
Application
     │
     ▼
   Proxy
     │
     ▼
    User
```

Có thể làm:

```python
class Proxy:

    def __init__(self, target):
        self._target = target

    def __getattribute__(self, name):
        if name == "_target":
            return object.__getattribute__(
                self,
                name
            )

        target = object.__getattribute__(
            self,
            "_target"
        )

        return getattr(target, name)
```

---

# 15. Proxy hoạt động như thế nào?

```python
user = User()

proxy = Proxy(user)

proxy.hello()
```

Luồng:

```text
proxy.hello()
      │
      ▼
Proxy.__getattribute__("hello")
      │
      ▼
target
      │
      ▼
target.hello
      │
      ▼
bound method
      │
      ▼
()
```

Đây là nền tảng của rất nhiều:

* proxy
* lazy object
* ORM
* remote object
* caching
* authorization layer

---

# 16. Lazy Loading

Một ứng dụng rất quan trọng.

Giả sử:

```python
class User:
    def __init__(self, user_id):
        self.user_id = user_id
```

Ta không muốn load profile ngay:

```text
User created
    ↓
profile chưa load
```

Chỉ khi:

```python
user.profile
```

thì mới load database.

Conceptually:

```text
user.profile
     │
     ▼
__getattribute__
     │
     ▼
profile chưa có?
     │
    YES
     │
     ▼
load từ DB
     │
     ▼
cache profile
     │
     ▼
return profile
```

---

# 17. Ví dụ Lazy Object

```python
class LazyUser:

    def __init__(self, user_id):
        self.user_id = user_id
        self._profile = None

    def _load_profile(self):
        print("Loading profile...")
        return {
            "name": "Alice",
            "age": 30,
        }

    def __getattribute__(self, name):

        if name == "profile":

            profile = object.__getattribute__(
                self,
                "_profile"
            )

            if profile is None:
                profile = object.__getattribute__(
                    self,
                    "_load_profile"
                )()

                object.__setattr__(
                    self,
                    "_profile",
                    profile
                )

            return profile

        return object.__getattribute__(
            self,
            name
        )
```

Sử dụng:

```python
user = LazyUser(1)
```

Chưa load database.

Khi:

```python
print(user.profile)
```

mới:

```text
Loading profile...
```

Lần sau:

```python
print(user.profile)
```

đã có cache.

---

# 18. Nhưng Descriptor thường phù hợp hơn

Đây là điểm kiến trúc rất quan trọng.

Bạn **có thể** dùng:

```python
__getattribute__()
```

để làm lazy loading.

Nhưng nếu chỉ muốn kiểm soát một vài attribute:

```text
user.name
user.age
user.profile
user.settings
```

thì override toàn bộ `__getattribute__()` thường quá mạnh.

Descriptor thường sạch hơn:

```python
class User:

    profile = LazyField()
```

Khi đó:

```text
User
 │
 └── profile
       ↓
   LazyField
```

Chúng ta sẽ xây chính hệ thống này ở các buổi:

```text
11 Descriptor Foundation
12 Data Descriptor
13 Non-data Descriptor
14 property
15 Descriptor Practical
16 Descriptor Framework
```

---

# 19. `object.__getattribute__()` vs `getattr()`

Ba cách:

```python
user.name
```

```python
getattr(user, "name")
```

```python
object.__getattribute__(user, "name")
```

không hoàn toàn giống nhau về mục đích.

### `user.name`

Syntax attribute access.

### `getattr()`

Dynamic attribute access:

```python
name = "username"

value = getattr(
    user,
    name
)
```

Nó cũng đi qua attribute lookup machinery.

### `object.__getattribute__()`

Gọi trực tiếp implementation mặc định của `object`.

Thường dùng khi override:

```python
def __getattribute__(self, name):
    return object.__getattribute__(
        self,
        name
    )
```

---

# 20. `getattr()` có thể kích hoạt `__getattr__`

Ví dụ:

```python
class User:

    def __getattr__(self, name):
        return "fallback"
```

```python
user = User()

print(getattr(user, "abc"))
```

→

```text
fallback
```

Trong khi `object.__getattribute__()` chỉ thực hiện lookup cơ bản và nếu không tìm thấy thì raise `AttributeError`.

---

# 21. `hasattr()`

Ta có:

```python
hasattr(user, "name")
```

Conceptually:

```text
hasattr
   ↓
getattr
   ↓
attribute lookup
   ↓
AttributeError?
   ├── YES → False
   └── NO  → True
```

Do đó:

```python
hasattr()
```

có thể kích hoạt:

* `__getattribute__`
* descriptor `__get__`
* `__getattr__`

Đây là lý do không nên coi `hasattr()` chỉ là một phép kiểm tra dictionary đơn giản.

---

# 22. `__getattribute__()` và MRO

Nếu:

```python
class A:
    x = "A"


class B(A):

    def __getattribute__(self, name):
        print("B lookup:", name)

        return super().__getattribute__(name)
```

và:

```python
b = B()

print(b.x)
```

thì:

```text
b.x
 ↓
B.__getattribute__
 ↓
super().__getattribute__
 ↓
object.__getattribute__
 ↓
MRO
 ↓
B
 ↓
A
 ↓
object
 ↓
x
```

---

# 23. `super().__getattribute__()` hay `object.__getattribute__()`?

Bạn thường thấy:

```python
return super().__getattribute__(name)
```

hoặc:

```python
return object.__getattribute__(self, name)
```

Cả hai có thể đúng trong những thiết kế phù hợp, nhưng chúng có semantics khác nhau trong inheritance.

Ví dụ class trực tiếp kế thừa `object`:

```python
class User:

    def __getattribute__(self, name):
        return object.__getattribute__(
            self,
            name
        )
```

rất rõ ràng.

Trong framework có inheritance phức tạp, `super()` có thể giúp tôn trọng cooperative inheritance.

---

# 24. Một Logger hoàn chỉnh hơn

```python
class LoggedObject:

    def __getattribute__(self, name):

        print(
            f"[GET] "
            f"{type(self).__name__}.{name}"
        )

        return super().__getattribute__(
            name
        )
```

Ví dụ:

```python
class User(LoggedObject):

    name = "Alice"

    def hello(self):
        return "Hello"
```

```python
user = User()

print(user.name)
print(user.hello())
```

---

# 25. Một lưu ý về `type(self)`

Trong:

```python
__getattribute__
```

viết:

```python
type(self)
```

cũng là một operation có thể liên quan đến attribute/type machinery ở mức runtime.

Trong debugging cực thấp, nếu muốn tránh những tương tác không cần thiết, có thể giữ implementation đơn giản và gọi trực tiếp:

```python
object.__getattribute__
```

Đừng over-engineer `__getattribute__`.

---

# 26. Pattern quan trọng nhất

Khi override `__getattribute__`, hãy nhớ pattern:

```python
class MyObject:

    def __getattribute__(self, name):

        # custom behavior
        ...

        # normal lookup
        return object.__getattribute__(
            self,
            name
        )
```

Hoặc cooperative:

```python
class MyObject:

    def __getattribute__(self, name):

        # custom behavior
        ...

        return super().__getattribute__(
            name
        )
```

---

# 27. Những thứ có thể xây bằng `__getattribute__`

```text
__getattribute__
       │
       ├── Logging
       │
       ├── Debugging
       │
       ├── Proxy
       │
       ├── Lazy Loading
       │
       ├── Caching
       │
       ├── Authorization
       │
       ├── Deprecation warning
       │
       ├── Metrics
       │
       └── Dynamic behavior
```

Nhưng:

> **Không nên override `__getattribute__()` chỉ vì muốn giải quyết một vấn đề nhỏ.**

Nó là một hook rất mạnh.

---

# 28. So sánh ba cơ chế

| Cơ chế             | Khi nào chạy?        | Mục đích          |
| ------------------ | -------------------- | ----------------- |
| `__getattribute__` | Mọi attribute access | Intercept toàn bộ |
| `__getattr__`      | Lookup thất bại      | Fallback          |
| Descriptor         | Attribute cụ thể     | Custom behavior   |

Mental model:

```text
                    Attribute Access
                          │
                          ▼
                 __getattribute__
                          │
                          ▼
                     Descriptor
                          │
                          ▼
                   Normal Lookup
                          │
                          ▼
                    Not Found
                          │
                          ▼
                     __getattr__
```

---

# 29. Bài tập thực hành

## Bài 1 — Logger

Viết:

```python
class LoggedObject:
    ...
```

sao cho:

```python
class User(LoggedObject):
    name = "Alice"
    age = 20
```

khi:

```python
user.name
user.age
```

sẽ log:

```text
GET name
GET age
```

---

## Bài 2 — Block private attribute

Viết:

```python
class User:

    _password = "123456"
```

Override `__getattribute__()` sao cho:

```python
user.name
```

được phép nhưng:

```python
user._password
```

ném:

```python
AttributeError
```

---

## Bài 3 — Đếm số lần access

Xây:

```python
class AccessCounter:
    ...
```

Ví dụ:

```python
user.name
user.name
user.age
user.name
```

kết quả conceptually:

```python
{
    "name": 3,
    "age": 1,
}
```

**Lưu ý:** phải tránh recursion khi truy cập dictionary lưu counter.

---

## Bài 4 — Lazy Loading

Xây:

```python
class LazyUser:
    ...
```

Sao cho:

```python
user = LazyUser()

print("created")

print(user.profile)
print(user.profile)
```

Output:

```text
created
Loading profile...
{'name': 'Alice'}
{'name': 'Alice'}
```

`Loading profile...` chỉ xuất hiện **một lần**.

---

# 🧠 Mental Model Buổi 9

Đừng nhớ `__getattribute__()` như một syntax trick.

Hãy nhớ nó như **cổng vào của attribute access**:

```text
                user.name
                    │
                    ▼
          ┌──────────────────┐
          │ __getattribute__  │
          └────────┬─────────┘
                   │
                   ▼
        object.__getattribute__
                   │
                   ▼
             Class / MRO
                   │
                   ▼
              Descriptor
                   │
                   ▼
          Instance __dict__
                   │
                   ▼
             Class attr
                   │
                   ▼
              not found
                   │
                   ▼
             __getattr__
```

### Ba câu cần nhớ

**1.**

```python
obj.attr
```

đi qua:

```python
__getattribute__()
```

**2.**

Trong `__getattribute__()`, thường phải dùng:

```python
object.__getattribute__(
    self,
    name
)
```

để tránh recursion và giữ lookup mặc định.

**3.**

`__getattribute__` là **global interception point của attribute access**, còn Descriptor cho phép kiểm soát **từng attribute cụ thể**.

---

# 🚀 Buổi 10 — `__getattr__()`

Buổi tiếp theo chúng ta sẽ phân biệt thật sâu:

```python
__getattribute__()
        vs
__getattr__()
```

và xây các pattern:

```text
Fallback Attribute
Dynamic Attribute
Lazy Attribute
Proxy
Default Value
Remote Attribute
```

Đặc biệt sẽ giải thích vì sao:

```python
getattr(obj, "x")
```

có thể kích hoạt `__getattr__()`, còn:

```python
obj.__dict__.get("x")
```

thì không.
