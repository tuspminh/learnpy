# 🐍 Buổi 10 — `__getattr__()` Deep Dive

Hôm nay chúng ta hoàn thành phần **Attribute Access cơ bản**:

```text
Buổi 8  → Attribute Lookup
Buổi 9  → __getattribute__()
Buổi 10 → __getattr__()
Buổi 11 → Descriptor Foundation
```

Điểm quan trọng nhất của Buổi 10:

> `__getattribute__()` là **cửa vào của mọi attribute access**, còn `__getattr__()` là **cơ chế fallback khi lookup thất bại**.

---

# 1. `__getattr__()` là gì?

Ví dụ:

```python
class User:
    def __getattr__(self, name):
        return f"{name} không tồn tại"
```

```python
user = User()

print(user.name)
print(user.age)
```

Kết quả:

```text
name không tồn tại
age không tồn tại
```

Python không tìm thấy `name` và `age`, nên gọi:

```python
user.__getattr__("name")
user.__getattr__("age")
```

---

# 2. `__getattr__()` không được gọi cho mọi attribute

Đây là điểm khác biệt quan trọng với Buổi 9.

```python
class User:

    name = "Alice"

    def __getattr__(self, name):
        print("__getattr__:", name)
        return "fallback"
```

```python
user = User()

print(user.name)
```

Output:

```text
Alice
```

Không có:

```text
__getattr__: name
```

Vì `name` đã được tìm thấy.

---

# 3. Khi nào `__getattr__()` chạy?

Luồng:

```text
user.name
    │
    ▼
__getattribute__()
    │
    ▼
Normal attribute lookup
    │
    ├── FOUND ──────────► return
    │
    └── NOT FOUND
             │
             ▼
       __getattr__()
             │
             ▼
          return
```

Vì vậy:

```text
__getattribute__ = interception
__getattr__      = fallback
```

---

# 4. Ví dụ kết hợp cả hai

```python
class User:

    def __getattribute__(self, name):
        print("GETATTRIBUTE:", name)

        return object.__getattribute__(
            self,
            name
        )

    def __getattr__(self, name):
        print("GETATTR:", name)
        return "fallback"
```

Chạy:

```python
user = User()

print(user.name)
```

Conceptually:

```text
GETATTRIBUTE: name
GETATTR: name
fallback
```

Tức là:

```text
__getattribute__
       ↓
không tìm thấy
       ↓
__getattr__
```

---

# 5. `__getattr__()` không phải cơ chế lookup chính

Đây là misconception thường gặp:

```python
def __getattr__(self, name):
    ...
```

không có nghĩa:

> "Mỗi lần lấy attribute, Python gọi hàm này."

Không.

Nó chỉ là:

> "Nếu lookup bình thường không thành công, hãy thử hàm này."

---

# 6. `__getattr__()` phải trả về value hoặc raise `AttributeError`

Ví dụ:

```python
class User:

    def __getattr__(self, name):
        return 100
```

```python
user = User()

print(user.abc)
```

→ `100`.

Nhưng cũng có thể:

```python
class User:

    def __getattr__(self, name):
        raise AttributeError(name)
```

Khi đó:

```python
user.abc
```

vẫn kết thúc bằng:

```text
AttributeError
```

---

# 7. Dynamic Attributes

Đây là ứng dụng đầu tiên rất hữu ích.

```python
class Config:

    def __getattr__(self, name):
        return f"config:{name}"
```

```python
config = Config()

print(config.database)
print(config.redis)
print(config.timeout)
```

Output:

```text
config:database
config:redis
config:timeout
```

Object có thể cung cấp attribute **động**.

---

# 8. Dynamic Attribute từ dictionary

Ví dụ:

```python
class Config:

    def __init__(self, data):
        self._data = data

    def __getattr__(self, name):
        return self._data[name]
```

Sử dụng:

```python
config = Config({
    "host": "localhost",
    "port": 5432,
})
```

Ta có:

```python
print(config.host)
print(config.port)
```

Kết quả:

```text
localhost
5432
```

Architecture:

```text
config.host
     │
     ▼
__getattribute__("host")
     │
     ▼
không tìm thấy
     │
     ▼
__getattr__("host")
     │
     ▼
_data["host"]
```

---

# 9. Nhưng implementation trên có vấn đề

Ta viết:

```python
class Config:

    def __init__(self, data):
        self._data = data

    def __getattr__(self, name):
        return self._data[name]
```

Khi `name` không tồn tại:

```python
config.foo
```

thì:

```python
self._data
```

là một attribute access.

Thông thường không sao.

Nhưng khi kết hợp với `__getattribute__()` custom, proxy, lazy loading..., rất dễ tạo recursion.

Best practice:

> Những attribute nội bộ nên được truy cập cẩn thận bằng `object.__getattribute__()` khi cần.

---

# 10. `getattr()`

Một trong những lý do `__getattr__()` rất hữu ích là dynamic access.

Thay vì:

```python
config.host
```

ta có:

```python
name = "host"

getattr(config, name)
```

Conceptually:

```text
getattr(config, "host")
        ↓
attribute lookup
        ↓
__getattribute__
        ↓
không tìm thấy
        ↓
__getattr__
```

---

# 11. `getattr()` có default

Python hỗ trợ:

```python
getattr(
    object,
    name,
    default
)
```

Ví dụ:

```python
class User:
    name = "Alice"


user = User()

print(getattr(user, "name", "Unknown"))
print(getattr(user, "age", 0))
```

Kết quả:

```text
Alice
0
```

Nhưng cần hiểu một điểm quan trọng:

`getattr(obj, "x", default)` không đơn giản là đọc `__dict__`; nó vẫn thực hiện attribute lookup.

---

# 12. `hasattr()`

Ví dụ:

```python
class User:
    name = "Alice"


user = User()

print(hasattr(user, "name"))
print(hasattr(user, "age"))
```

Kết quả:

```text
True
False
```

Conceptually:

```text
hasattr(obj, "x")
       ↓
thử getattr
       ↓
AttributeError?
    │       │
   YES      NO
    │        │
 False      True
```

---

# 13. `__getattr__()` ảnh hưởng `hasattr()`

Ví dụ:

```python
class User:

    def __getattr__(self, name):
        return None
```

Bây giờ:

```python
user = User()

print(hasattr(user, "name"))
```

Kết quả:

```text
True
```

Tại sao?

Vì:

```text
user.name
   ↓
lookup thất bại
   ↓
__getattr__()
   ↓
return None
```

Không có `AttributeError`.

Do đó:

> `hasattr()` không có nghĩa là `"name" in obj.__dict__`.

---

# 14. Nếu `__getattr__()` raise `AttributeError`

```python
class User:

    def __getattr__(self, name):
        raise AttributeError(name)
```

```python
user = User()

print(hasattr(user, "name"))
```

→

```text
False
```

Đây là hành vi đúng khi attribute thực sự không tồn tại.

---

# 15. Dynamic Method

`__getattr__()` không chỉ tạo value.

Nó có thể tạo function/method động.

Ví dụ:

```python
class API:

    def __getattr__(self, name):

        def method(*args, **kwargs):
            return {
                "endpoint": name,
                "args": args,
                "kwargs": kwargs,
            }

        return method
```

Bây giờ:

```python
api = API()

print(api.users())
print(api.books())
print(api.chapters(page=2))
```

Có thể tạo:

```text
users
books
chapters
```

động mà không cần định nghĩa từng method.

---

# 16. Đây là pattern rất mạnh

Ta có:

```text
api.users()
api.books()
api.chapters()
api.stories()
```

nhưng class chỉ có:

```python
__getattr__()
```

Architecture:

```text
api.chapters
      │
      ▼
__getattr__("chapters")
      │
      ▼
create callable
      │
      ▼
api.chapters()
      │
      ▼
request / command
```

Các API client, proxy object và DSL có thể dùng ý tưởng này.

---

# 17. Lazy Loading bằng `__getattr__()`

Đây là ứng dụng rất hay.

Giả sử:

```python
class User:

    def __init__(self):
        self._profile = None

    def load_profile(self):
        print("Loading profile...")
        return {
            "name": "Alice"
        }

    def __getattr__(self, name):
        if name == "profile":
            profile = self.load_profile()

            self._profile = profile

            return profile

        raise AttributeError(name)
```

Sử dụng:

```python
user = User()

print(user.profile)
```

Output:

```text
Loading profile...
{'name': 'Alice'}
```

---

# 18. Nhưng ví dụ trên chưa cache đúng

Lần sau:

```python
print(user.profile)
```

vẫn có thể gọi `__getattr__()` nếu profile không được đặt đúng cách.

Ta có thể:

```python
class User:

    def __init__(self):
        self._profile = None

    def load_profile(self):
        print("Loading profile...")
        return {"name": "Alice"}

    def __getattr__(self, name):

        if name == "profile":

            profile = self._profile

            if profile is None:
                profile = self.load_profile()
                self._profile = profile

            return profile

        raise AttributeError(name)
```

Nhưng còn một cách đẹp hơn.

---

# 19. Cache bằng chính tên attribute

```python
class User:

    def load_profile(self):
        print("Loading profile...")
        return {
            "name": "Alice"
        }

    def __getattr__(self, name):

        if name == "profile":
            value = self.load_profile()

            object.__setattr__(
                self,
                "profile",
                value
            )

            return value

        raise AttributeError(name)
```

Lần đầu:

```python
user.profile
```

```text
__getattr__
    ↓
load
    ↓
set user.profile
    ↓
return
```

Lần sau:

```python
user.profile
```

đã tìm thấy:

```python
user.__dict__["profile"]
```

nên **không cần `__getattr__()` nữa**.

---

# 20. Đây là một pattern rất đẹp

```text
First access
────────────

user.profile
     ↓
normal lookup
     ↓
not found
     ↓
__getattr__
     ↓
load data
     ↓
cache as profile


Next access
───────────

user.profile
     ↓
normal lookup
     ↓
found
     ↓
return
```

Đây chính là **lazy initialization**.

---

# 21. Proxy với `__getattr__()`

Đây là một pattern cực kỳ phổ biến.

```python
class Proxy:

    def __init__(self, target):
        self._target = target

    def __getattr__(self, name):
        return getattr(
            self._target,
            name
        )
```

Ví dụ:

```python
class User:

    def hello(self):
        return "Hello"


user = User()
proxy = Proxy(user)

print(proxy.hello())
```

Luồng:

```text
proxy.hello()
     │
     ▼
normal lookup trên Proxy
     │
     ▼
hello không có
     │
     ▼
Proxy.__getattr__("hello")
     │
     ▼
target.hello
     │
     ▼
bound method
```

---

# 22. Tại sao Proxy thường dùng `__getattr__()`?

Vì Proxy chỉ muốn nói:

> "Nếu tôi không có attribute đó, hãy chuyển sang object thật."

Điều này tự nhiên hơn việc intercept mọi attribute bằng `__getattribute__()`.

Ví dụ:

```text
Proxy
├── _target       ← attribute của Proxy
└── mọi thứ khác  → target
```

`__getattr__()` rất phù hợp với mô hình này.

---

# 23. `__getattribute__()` vs `__getattr__()`

|                    | `__getattribute__()` | `__getattr__()`         |
| ------------------ | -------------------- | ----------------------- |
| Chạy               | Mọi lookup           | Chỉ khi lookup thất bại |
| Vai trò            | Interceptor          | Fallback                |
| Độ mạnh            | Rất mạnh             | Nhẹ hơn                 |
| Dễ recursion       | Cao                  | Thấp hơn                |
| Proxy              | Có thể               | Rất phù hợp             |
| Lazy loading       | Có thể               | Rất phù hợp             |
| Dynamic attributes | Có thể               | Rất phù hợp             |

Mental model:

```text
                    obj.x
                      │
                      ▼
             __getattribute__
                      │
                      ▼
                lookup bình thường
                      │
             ┌────────┴────────┐
             │                 │
           FOUND            NOT FOUND
             │                 │
             ▼                 ▼
          return         __getattr__
                               │
                        ┌──────┴──────┐
                        │             │
                     return        AttributeError
```

---

# 24. `__getattr__()` và `__dict__`

Đây là điểm rất đáng nhớ.

```python
class User:

    def __getattr__(self, name):
        return "dynamic"
```

```python
user = User()

print(user.__dict__)
```

Kết quả:

```python
{}
```

Nhưng:

```python
print(user.name)
```

→

```text
dynamic
```

Vậy:

```text
user.__dict__
```

không chứa:

```text
name
```

nhưng:

```text
user.name
```

vẫn tồn tại về mặt behavior.

---

# 25. `__getattr__()` tạo "virtual attributes"

Đây là cách tư duy rất hữu ích:

```text
Physical attributes
───────────────────
obj.__dict__
class.__dict__
descriptor


Virtual attributes
──────────────────
__getattr__()
```

Ví dụ:

```python
class User:

    def __getattr__(self, name):
        return f"virtual:{name}"
```

Object có vô hạn "virtual attributes":

```python
user.name
user.age
user.foo
user.bar
```

mặc dù không có chúng trong `__dict__`.

---

# 26. Cẩn thận với typo

Đây là nhược điểm.

```python
class Config:

    def __getattr__(self, name):
        return None
```

Bạn viết nhầm:

```python
config.databse
```

thay vì:

```python
config.database
```

Python không báo lỗi.

Nó trả:

```python
None
```

→ Bug khó phát hiện.

Vì vậy với configuration object, thường tốt hơn:

```python
def __getattr__(self, name):
    try:
        return self._data[name]
    except KeyError:
        raise AttributeError(name)
```

---

# 27. `__getattr__()` đúng cách

Ví dụ:

```python
class Config:

    def __init__(self, data):
        self._data = data

    def __getattr__(self, name):

        try:
            return self._data[name]

        except KeyError:
            raise AttributeError(
                f"{type(self).__name__!s} "
                f"has no attribute {name!r}"
            ) from None
```

Bây giờ:

```python
config = Config({
    "host": "localhost"
})

print(config.host)
```

→

```text
localhost
```

nhưng:

```python
print(config.port)
```

→ `AttributeError`.

---

# 28. Tại sao phải raise `AttributeError`?

Nhiều Python machinery dựa vào `AttributeError`.

Ví dụ:

```python
hasattr()
getattr()
```

và một số introspection tools.

Nếu attribute thực sự không tồn tại:

```python
raise AttributeError(name)
```

là behavior đúng.

Không nên:

```python
raise KeyError(name)
```

nếu interface bên ngoài đang mô phỏng attribute access.

---

# 29. `__getattr__()` và `getattr()`

Ví dụ:

```python
class User:

    def __getattr__(self, name):
        return f"missing:{name}"
```

Ta có:

```python
user = User()

print(user.foo)
```

và:

```python
print(getattr(user, "foo"))
```

đều có thể dẫn tới:

```text
missing:foo
```

Nhưng:

```python
user.__dict__.get("foo")
```

thì:

```text
None
```

vì `__dict__` chỉ là dictionary.

---

# 30. Đây là khác biệt cực kỳ quan trọng

```text
obj.attr
   ↓
attribute protocol
   ↓
__getattribute__
   ↓
descriptor / __dict__ / class / ...
   ↓
__getattr__
```

Trong khi:

```text
obj.__dict__.get("attr")
   ↓
dictionary lookup
   ↓
DONE
```

Nó không chạy:

```text
__getattr__
```

---

# 31. Crawler Framework — ứng dụng thực tế

Trong crawler của bạn, có thể có:

```python
response.status_code
response.headers
response.text
response.url
```

Nhưng bạn cũng có thể có một object dynamic:

```python
response.meta
```

hoặc:

```python
request.cookies
request.headers
request.query
```

`__getattr__()` có thể được dùng để:

```text
Request
   │
   ├── headers
   ├── cookies
   ├── params
   └── dynamic metadata
```

Tuy nhiên, trong framework production, **đừng lạm dụng dynamic attribute** vì IDE, static type checker và autocomplete sẽ khó hiểu object hơn.

---

# 32. Pattern: Dynamic API Client

Ví dụ:

```python
class API:

    def __init__(self, client):
        self._client = client

    def __getattr__(self, name):

        def endpoint(*args, **kwargs):
            return self._client.request(
                name,
                *args,
                **kwargs,
            )

        return endpoint
```

Có thể tạo interface kiểu:

```python
api.users()
api.stories()
api.chapters()
```

mà không cần định nghĩa từng method.

Đây là một trong những trường hợp `__getattr__()` thực sự hữu ích.

---

# 33. Pattern: Backward Compatibility

Giả sử API cũ:

```python
user.username
```

nhưng API mới đổi thành:

```python
user.name
```

Ta có thể tạm hỗ trợ:

```python
class User:

    def __init__(self, name):
        self.name = name

    def __getattr__(self, attr):

        if attr == "username":
            return self.name

        raise AttributeError(attr)
```

Khi đó:

```python
user.username
```

vẫn hoạt động.

Nhưng trong production nên kết hợp warning/deprecation rõ ràng thay vì giữ alias vô thời hạn.

---

# 34. `__getattr__()` không phải Descriptor

Đây là điểm chuẩn bị cho Buổi 11.

`__getattr__()`:

```text
object-level fallback
```

Descriptor:

```text
attribute-level behavior
```

Ví dụ:

```python
class User:

    name = StringField()
```

Descriptor chỉ kiểm soát:

```text
name
```

Còn:

```python
__getattr__()
```

xử lý các attribute **không được lookup thành công**.

---

# 35. Ba tầng cần nhớ

Sau 3 buổi:

```text
                    obj.attr
                       │
                       ▼
             ┌──────────────────┐
             │ __getattribute__  │
             └────────┬─────────┘
                      │
                      ▼
              Attribute Lookup
                      │
                      ▼
                Descriptor
                      │
                      ▼
               __dict__ / MRO
                      │
                 not found
                      │
                      ▼
                __getattr__
```

Đây là kiến trúc nền tảng của Python attribute system.

---

# 🧪 Bài tập thực hành

## Bài 1 — Fallback

Viết:

```python
class User:

    name = "Alice"

    def __getattr__(self, name):
        ...
```

Sao cho:

```python
user.name
```

→ `"Alice"`

nhưng:

```python
user.age
```

→ `"Unknown"`

---

## Bài 2 — Attribute từ dictionary

Xây:

```python
class Config:
    ...
```

Sao cho:

```python
config = Config({
    "host": "localhost",
    "port": 5432,
})
```

có thể:

```python
config.host
config.port
```

nhưng:

```python
config.database
```

phải raise `AttributeError`.

---

## Bài 3 — Dynamic method

Xây:

```python
class API:
    ...
```

sao cho:

```python
api.users()
api.stories()
api.chapters()
```

đều trả về:

```python
{
    "endpoint": "...",
}
```

Ví dụ:

```text
api.users()
→ {"endpoint": "users"}

api.chapters()
→ {"endpoint": "chapters"}
```

---

# 🧪 Bài 4 — Lazy Loading

Xây:

```python
class User:
    ...
```

sao cho:

```python
user = User()

print(user.profile)
print(user.profile)
```

chỉ in:

```text
Loading profile...
```

**một lần duy nhất**.

Gợi ý:

```python
object.__setattr__(
    self,
    "profile",
    value
)
```

---

# 🧪 Bài 5 — Proxy

Xây:

```python
class Proxy:
    ...
```

với:

```python
class User:

    def hello(self):
        return "Hello"
```

Sao cho:

```python
proxy = Proxy(User())

print(proxy.hello())
```

→

```text
Hello
```

Yêu cầu: sử dụng `__getattr__()`.

---

# 🎯 Tổng kết Part II đến thời điểm này

| Cơ chế             | Vai trò                     |
| ------------------ | --------------------------- |
| `obj.attr`         | Attribute access            |
| `__getattribute__` | Intercept mọi access        |
| `__getattr__`      | Fallback                    |
| `__dict__`         | Instance storage thường gặp |
| MRO                | Tìm class theo inheritance  |
| Descriptor         | Custom attribute behavior   |

Và một mental model cuối cùng:

```text
                    obj.attr
                       │
                       ▼
              __getattribute__()
                       │
                       ▼
              ┌────────────────┐
              │ Attribute      │
              │ Lookup         │
              └───────┬────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       Data      instance      class /
    descriptor   __dict__     non-data
          │           │           │
          └───────────┴───────────┘
                      │
                 not found
                      │
                      ▼
                __getattr__()
                      │
              ┌───────┴───────┐
              ▼               ▼
           return       AttributeError
```

---

# 🚀 Buổi 11 — Descriptor Foundation

Đây là buổi **rất quan trọng**.

Chúng ta sẽ bắt đầu tự xây:

```python
class Field:

    def __get__(self, instance, owner):
        ...

    def __set__(self, instance, value):
        ...
```

và hiểu tại sao:

```python
class User:
    name = Field()
```

lại có thể biến:

```python
user.name = "Alice"
```

thành:

```text
user.name = "Alice"
       ↓
Field.__set__()
       ↓
validation
       ↓
storage
```

Sau Buổi 11–16, bạn sẽ có thể **tự xây một mini descriptor framework**, khá sát với cách nhiều thư viện Python/ORM tận dụng cơ chế này.
