# OOP Deep Dive — Buổi 27

# Metaclass — Class dùng để tạo Class

Hôm nay chúng ta bước vào phần quan trọng nhất của **Metaclass**.

Roadmap:

```text
Buổi 25 — type()
Buổi 26 — Dynamic Class Creation
👉 Buổi 27 — Metaclass
Buổi 28 — __new__ của Metaclass
Buổi 29 — __prepare__ / __init_subclass__
Buổi 30 — Ứng dụng Metaclass
```

Mục tiêu hôm nay là hiểu thật chắc:

> **Metaclass là gì, tại sao `type` là metaclass mặc định, và `metaclass=...` thực sự làm gì.**

---

# 1. Nhắc lại object model

Ta đã có:

```python
class User:
    pass

user = User()
```

Quan hệ:

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

Và:

```python
type(user) is User
type(User) is type
```

---

# 2. Nhưng `type` là gì?

`type` cũng là một class.

```python
print(type(type))
```

Kết quả:

```text
<class 'type'>
```

Điều này dẫn tới:

```text
type
 ↑
type
```

Có vẻ vòng tròn.

Python cho phép điều này vì `type` là một **metaclass đặc biệt**.

---

# 3. Định nghĩa đơn giản nhất

Có thể hiểu:

> **Metaclass là class dùng để tạo và điều khiển class object.**

Class thông thường:

```text
Class
  ↓ tạo
Instance
```

Metaclass:

```text
Metaclass
    ↓ tạo
Class
```

Ví dụ:

```text
type
 ↓
User
 ↓
user
```

---

# 4. So sánh

## Class

```python
class User:
    pass
```

Tạo:

```python
user = User()
```

```text
User
 ↓
user
```

## Metaclass

```python
class User(metaclass=MyMeta):
    pass
```

`MyMeta` tham gia vào quá trình tạo:

```text
MyMeta
   ↓
 User
```

Sau đó:

```text
User
 ↓
user
```

---

# 5. Metaclass không phải "class cha"

Đây là lỗi rất phổ biến.

```python
class User(metaclass=MyMeta):
    pass
```

Không có nghĩa:

```text
User
 ↑
MyMeta
```

theo inheritance.

Nó có nghĩa:

```text
MyMeta
   ↓ creates
User
```

Quan hệ này là:

```python
type(User) is MyMeta
```

chứ không phải:

```python
issubclass(User, MyMeta)
```

---

# 6. Ví dụ đầu tiên

```python
class MyMeta(type):
    pass
```

Sau đó:

```python
class User(metaclass=MyMeta):
    pass
```

Kiểm tra:

```python
print(type(User))
```

Kết quả:

```text
<class '__main__.MyMeta'>
```

---

# 7. Đây là điểm cốt lõi

Thông thường:

```python
class User:
    pass
```

Python dùng:

```text
type
```

làm metaclass.

Nhưng:

```python
class User(metaclass=MyMeta):
    pass
```

Python dùng:

```text
MyMeta
```

làm metaclass.

---

# 8. `metaclass=` là gì?

Cú pháp:

```python
class User(metaclass=MyMeta):
    pass
```

nói với Python:

> Khi tạo class `User`, hãy sử dụng `MyMeta` làm metaclass.

---

# 9. Thử nghiệm

```python
class MyMeta(type):

    def __new__(
        mcls,
        name,
        bases,
        namespace,
    ):
        print("Creating:", name)

        return super().__new__(
            mcls,
            name,
            bases,
            namespace,
        )
```

Sau đó:

```python
class User(metaclass=MyMeta):
    pass
```

Kết quả:

```text
Creating: User
```

---

# 10. Điều gì xảy ra?

Khi Python gặp:

```python
class User(metaclass=MyMeta):
    pass
```

nó không đơn giản chỉ tạo class rồi mới gọi `MyMeta`.

Thay vào đó, quá trình class creation sử dụng metaclass.

Ở mức khái niệm:

```text
class User
    ↓
xác định metaclass
    ↓
MyMeta
    ↓
MyMeta(...)
    ↓
User class object
```

---

# 11. Metaclass cũng là class

Ta viết:

```python
class MyMeta(type):
    pass
```

Nghĩa là:

```text
MyMeta
    ↑
   type
```

Tức:

```python
issubclass(MyMeta, type)
```

→

```text
True
```

Và:

```python
type(MyMeta)
```

→

```text
type
```

---

# 12. Sơ đồ ba tầng

Đây là sơ đồ cần nhớ:

```text
              type
                │
                │ metaclass
                ▼
             MyMeta
                │
                │ metaclass
                ▼
              User
                │
                │ instance
                ▼
              user
```

Nhưng chính xác hơn:

```text
MyMeta
  └── instance of type

User
  └── instance of MyMeta

user
  └── instance of User
```

---

# 13. Kiểm tra từng tầng

```python
class MyMeta(type):
    pass


class User(metaclass=MyMeta):
    pass


user = User()

print(type(user))
print(type(User))
print(type(MyMeta))
```

Kết quả:

```text
<class '__main__.User'>
<class '__main__.MyMeta'>
<class 'type'>
```

---

# 14. Đây là một chuỗi rất quan trọng

```text
user
 ↓ type()
User
 ↓ type()
MyMeta
 ↓ type()
type
```

Có thể hình dung:

```python
type(user)  # User
type(User)  # MyMeta
type(MyMeta)  # type
```

---

# 15. Metaclass hoạt động ở đâu?

Điểm quan trọng:

> Metaclass hoạt động **khi class được tạo**.

Ví dụ:

```python
class User(metaclass=MyMeta):
    pass
```

`MyMeta` có cơ hội:

```text
kiểm tra class
sửa class
thêm attribute
xóa attribute
validate class
register class
tạo descriptor
tạo metadata
```

---

# 16. Ví dụ: tự động thêm attribute

```python
class MyMeta(type):

    def __new__(
        mcls,
        name,
        bases,
        namespace,
    ):

        namespace["framework"] = "MyFramework"

        return super().__new__(
            mcls,
            name,
            bases,
            namespace,
        )
```

Sau đó:

```python
class User(metaclass=MyMeta):
    pass
```

Ta có:

```python
print(User.framework)
```

→

```text
MyFramework
```

---

# 17. Metaclass đã thay đổi class

Source code:

```python
class User(metaclass=MyMeta):
    pass
```

không viết:

```python
framework = "MyFramework"
```

nhưng sau khi class được tạo:

```python
User.framework
```

vẫn tồn tại.

Đây chính là sức mạnh của metaclass.

---

# 18. Tự động đăng ký class

Đây là một ứng dụng rất thực tế.

Ta tạo registry:

```python
registry = {}
```

Metaclass:

```python
class RegistryMeta(type):

    def __new__(
        mcls,
        name,
        bases,
        namespace,
    ):

        cls = super().__new__(
            mcls,
            name,
            bases,
            namespace,
        )

        registry[name] = cls

        return cls
```

---

# 19. Tạo class

```python
class User(metaclass=RegistryMeta):
    pass


class Book(metaclass=RegistryMeta):
    pass
```

Bây giờ:

```python
print(registry)
```

có thể chứa:

```text
{
    "User": <class User>,
    "Book": <class Book>
}
```

---

# 20. Đây là Plugin Registry

Tưởng tượng:

```python
class NovelPlugin(metaclass=PluginMeta):
    pass


class MangaPlugin(metaclass=PluginMeta):
    pass
```

Metaclass tự động:

```text
NovelPlugin → registry
MangaPlugin → registry
```

Framework sau đó có thể:

```python
plugin = registry["NovelPlugin"]
```

Đây chính là một ứng dụng rất gần với **Plugin Architecture**.

---

# 21. Metaclass và ORM

Ta có:

```python
class ModelMeta(type):
    ...
```

Sau đó:

```python
class User(metaclass=ModelMeta):

    id = IntegerField()
    name = StringField()
```

Metaclass có thể phát hiện:

```text
id
name
```

và xây dựng:

```text
User._fields
```

---

# 22. Đây là nơi Buổi 24 quay lại

Buổi 24:

```python
class User(Model):
    id = IntegerField()
    name = StringField()
```

Ta muốn framework tự động biết:

```text
id
name
```

Metaclass có thể làm:

```python
class ModelMeta(type):

    def __new__(
        mcls,
        name,
        bases,
        namespace,
    ):

        fields = {}

        for key, value in namespace.items():

            if isinstance(value, Field):
                fields[key] = value

        namespace["_fields"] = fields

        return super().__new__(
            mcls,
            name,
            bases,
            namespace,
        )
```

---

# 23. Model

```python
class Model(metaclass=ModelMeta):
    pass
```

Sau đó:

```python
class User(Model):

    id = IntegerField()
    name = StringField()
```

Metaclass sẽ nhìn thấy:

```text
namespace
├── id
└── name
```

và tạo:

```python
User._fields
```

---

# 24. Tư duy quan trọng

Descriptor xử lý:

```text
user.name
```

Metaclass xử lý:

```text
class User:
    name = StringField()
```

Tức:

```text
              ORM
               │
       ┌───────┴────────┐
       ▼                ▼
 Descriptor          Metaclass
       │                │
       ▼                ▼
instance access    class creation
```

---

# 25. Metaclass không thay thế Descriptor

Đây là điểm rất quan trọng.

Metaclass:

```text
class creation
```

Descriptor:

```text
attribute access
```

Ví dụ:

```python
user.name = "Alice"
```

thường liên quan đến Descriptor.

Còn:

```python
class User:
    name = StringField()
```

có thể được Metaclass phân tích khi class được tạo.

---

# 26. Metaclass kế thừa từ `type`

Thông thường:

```python
class MyMeta(type):
    pass
```

Tại sao?

Vì `type` là metaclass mặc định.

Ta mở rộng behavior của `type`.

Ví dụ:

```text
type
 ↑
MyMeta
```

`MyMeta` kế thừa cơ chế tạo class từ `type`.

---

# 27. Metaclass `__new__`

Ta thường viết:

```python
class MyMeta(type):

    def __new__(
        mcls,
        name,
        bases,
        namespace,
    ):
        ...
```

Ba tham số quen thuộc:

```text
name
bases
namespace
```

Chính là những gì chúng ta đã học ở Buổi 26.

---

# 28. Nhớ lại `type()`

Ta có:

```python
User = type(
    "User",
    (Model,),
    {
        "name": StringField()
    }
)
```

Metaclass cũng nhận về cơ bản:

```text
name
bases
namespace
```

Vì vậy:

> Buổi 26 là nền tảng trực tiếp của Buổi 27.

---

# 29. Metaclass `__new__` làm gì?

Ví dụ:

```python
class MyMeta(type):

    def __new__(
        mcls,
        name,
        bases,
        namespace,
    ):

        print("NAME:", name)
        print("BASES:", bases)
        print("NAMESPACE:", namespace)

        return super().__new__(
            mcls,
            name,
            bases,
            namespace,
        )
```

Sau đó:

```python
class User(metaclass=MyMeta):

    age = 20

    def hello(self):
        pass
```

Bạn sẽ thấy metaclass nhận được:

```text
NAME
BASES
NAMESPACE
```

---

# 30. Namespace rất quan trọng

Ví dụ:

```python
class User(metaclass=MyMeta):

    name = "Alice"
    age = 25

    def hello(self):
        pass
```

Metaclass nhận namespace chứa đại khái:

```text
__module__
__qualname__
name
age
hello
```

Do đó metaclass có thể:

```text
inspect
validate
modify
register
```

class trước khi class object được tạo hoàn chỉnh.

---

# 31. Ví dụ Validation

Giả sử framework yêu cầu mọi Model phải có:

```python
id
```

Ta có:

```python
class ModelMeta(type):

    def __new__(
        mcls,
        name,
        bases,
        namespace,
    ):

        if name != "Model":
            if "id" not in namespace:
                raise TypeError(
                    f"{name} must define id"
                )

        return super().__new__(
            mcls,
            name,
            bases,
            namespace,
        )
```

---

# 32. Class hợp lệ

```python
class Model(metaclass=ModelMeta):
    pass


class User(Model):

    id = 1
```

OK.

---

# 33. Class không hợp lệ

```python
class Product(Model):

    name = "Book"
```

Có thể bị:

```text
TypeError:
Product must define id
```

Điều này xảy ra **ngay khi class được định nghĩa**.

---

# 34. Đây là điểm cực mạnh

Không cần chờ:

```python
product = Product()
```

mới phát hiện lỗi.

Framework có thể phát hiện lỗi ngay:

```python
class Product(...):
```

Trong lúc class creation.

---

# 35. Metaclass như một "class validator"

Có thể hình dung:

```text
class declaration
       ↓
    Metaclass
       ↓
   validation
       ↓
   class object
```

Nếu invalid:

```text
class declaration
       ↓
    Metaclass
       ↓
     ERROR
```

Class không được tạo.

---

# 36. Metaclass như compiler hook

Một cách tư duy nâng cao:

> Metaclass cho phép framework can thiệp vào quá trình xây dựng class.

Không phải compiler hook theo nghĩa chính thức, nhưng về mặt tư duy rất hữu ích.

Ví dụ:

```text
Python source
     ↓
class body
     ↓
metaclass
     ↓
class object
```

---

# 37. Metaclass có thể tự động thêm method

Ví dụ:

```python
class AutoReprMeta(type):

    def __new__(
        mcls,
        name,
        bases,
        namespace,
    ):

        if "__repr__" not in namespace:

            def __repr__(self):
                return (
                    f"<{type(self).__name__}>"
                )

            namespace["__repr__"] = __repr__

        return super().__new__(
            mcls,
            name,
            bases,
            namespace,
        )
```

---

# 38. Sử dụng

```python
class User(metaclass=AutoReprMeta):
    pass
```

Sau đó:

```python
user = User()

print(user)
```

có thể ra:

```text
<User>
```

Mặc dù `User` không tự viết `__repr__`.

---

# 39. Metaclass có thể sửa class name

Ví dụ:

```python
class Meta(type):

    def __new__(
        mcls,
        name,
        bases,
        namespace,
    ):

        print(
            "Creating:",
            name
        )

        return super().__new__(
            mcls,
            name,
            bases,
            namespace,
        )
```

Khi:

```python
class User(metaclass=Meta):
    pass
```

ta có:

```text
Creating: User
```

---

# 40. Nhưng đừng lạm dụng

Metaclass cực mạnh nhưng cũng rất dễ làm code khó hiểu.

Không nên dùng metaclass chỉ để:

```text
thêm một attribute đơn giản
```

Trong nhiều trường hợp có thể dùng:

* decorator
* class decorator
* `__init_subclass__`
* descriptor
* inheritance
* composition

đơn giản hơn.

---

# 41. Metaclass vs Class Decorator

Ví dụ:

```python
@register
class User:
    pass
```

có thể thay cho một số trường hợp:

```python
class User(metaclass=RegistryMeta):
    pass
```

Class decorator:

```text
class đã được tạo
      ↓
decorator
```

Metaclass:

```text
class đang được tạo
      ↓
metaclass
      ↓
class object
```

Đây là khác biệt quan trọng.

---

# 42. Metaclass vs `__init_subclass__`

Ví dụ:

```python
class Base:

    def __init_subclass__(cls):
        ...
```

Khi:

```python
class User(Base):
    pass
```

`__init_subclass__` được gọi khi subclass được tạo.

Nó thường đơn giản hơn metaclass.

Chúng ta sẽ học kỹ ở **Buổi 29**.

---

# 43. Khi nào dùng Metaclass?

Một số trường hợp phù hợp:

### ORM

```text
Model schema
```

### Plugin registry

```text
Plugin discovery
```

### Framework

```text
Declarative API
```

### Validation framework

```text
Class structure validation
```

### Serialization

```text
Schema registration
```

### DSL

```text
Declarative class syntax
```

---

# 44. Ví dụ Plugin Architecture

Ta có:

```python
plugins = {}
```

Metaclass:

```python
class PluginMeta(type):

    def __new__(
        mcls,
        name,
        bases,
        namespace,
    ):

        cls = super().__new__(
            mcls,
            name,
            bases,
            namespace,
        )

        if name != "Plugin":
            plugins[name] = cls

        return cls
```

---

# 45. Plugin Base

```python
class Plugin(metaclass=PluginMeta):
    pass
```

Sau đó:

```python
class NovelPlugin(Plugin):
    pass


class MangaPlugin(Plugin):
    pass
```

Framework tự động có:

```python
plugins
```

chứa:

```text
NovelPlugin
MangaPlugin
```

---

# 46. Đây rất gần với framework thực tế

Thay vì:

```python
register_plugin(NovelPlugin)
register_plugin(MangaPlugin)
```

developer chỉ cần:

```python
class NovelPlugin(Plugin):
    ...
```

Metaclass tự đăng ký.

Đây được gọi là **declarative API**:

> Bạn chỉ khai báo class, framework tự làm phần còn lại.

---

# 47. ORM cũng có declarative API

Ví dụ:

```python
class User(Model):

    id = IntegerField()
    name = StringField()
```

Developer không cần:

```python
register_field(User, "id", IntegerField())
register_field(User, "name", StringField())
```

Framework tự làm.

Đằng sau có thể là:

```text
Metaclass
+
Descriptor
```

---

# 48. Một ví dụ Mini ORM

```python
class Field:
    pass


class ModelMeta(type):

    def __new__(
        mcls,
        name,
        bases,
        namespace,
    ):

        fields = {}

        for key, value in namespace.items():

            if isinstance(value, Field):
                fields[key] = value

        namespace["_fields"] = fields

        return super().__new__(
            mcls,
            name,
            bases,
            namespace,
        )
```

Sau đó:

```python
class Model(metaclass=ModelMeta):
    pass
```

và:

```python
class User(Model):

    id = Field()
    name = Field()
```

---

# 49. Kiểm tra

```python
print(User._fields)
```

Có:

```text
{
    "id": ...,
    "name": ...
}
```

Không cần viết:

```python
User._fields = ...
```

Framework tự tạo.

---

# 50. Metaclass + Descriptor

Đây là kiến trúc mà bạn cần nhớ:

```text
class User(Model):

    name = StringField()
```

### Khi class được tạo:

```text
Metaclass
    ↓
inspect namespace
    ↓
collect StringField
    ↓
build metadata
    ↓
User class
```

### Khi instance được sử dụng:

```text
user.name
    ↓
Descriptor
    ↓
value
```

Hai cơ chế làm hai công việc khác nhau.

---

# 51. Một lỗi phổ biến

Người mới thường nghĩ:

```text
Metaclass = advanced inheritance
```

Không đúng.

Metaclass không chủ yếu dùng để kế thừa behavior cho instance.

Nó chủ yếu kiểm soát:

> **class creation**

---

# 52. Một lỗi khác

Người mới thấy:

```python
class MyMeta(type):
```

rồi nghĩ:

```text
MyMeta tạo instance của User
```

Không.

```text
MyMeta
   ↓
tạo User class object
```

Sau đó:

```text
User
   ↓
tạo user instance
```

---

# 53. Mô hình chính xác

```text
                type
                 │
                 │ creates
                 ▼
               MyMeta
                 │
                 │ creates
                 ▼
                User
                 │
                 │ creates
                 ▼
                user
```

Nhưng lưu ý:

```python
type(MyMeta) is type
type(User) is MyMeta
type(user) is User
```

---

# 54. Câu hỏi kiểm tra tư duy

Cho:

```python
class Meta(type):
    pass


class User(metaclass=Meta):
    pass


user = User()
```

Hãy tự trả lời:

### `type(user)`?

```text
User
```

### `type(User)`?

```text
Meta
```

### `type(Meta)`?

```text
type
```

### `issubclass(Meta, type)`?

```text
True
```

### `issubclass(User, Meta)`?

```text
False
```

Đây là bài test rất tốt để xem bạn đã hiểu metaclass hay chưa.

---

# 55. Một cách hình dung cực dễ nhớ

Hãy coi:

```text
Instance Factory
```

là class.

Ví dụ:

```text
User
 ↓
user
```

Còn:

```text
Class Factory
```

là metaclass.

```text
Meta
 ↓
User
```

Do đó:

```text
Factory
   ↓
Instance

MetaFactory
   ↓
Class
```

---

# 56. Metaclass chính là "Class Factory cấp cao"

Ta đã học Buổi 26:

```python
type(
    "User",
    (),
    {}
)
```

Đây là tạo class trực tiếp.

Metaclass cho phép framework nói:

```text
"Mỗi khi developer khai báo một class,
hãy cho tôi can thiệp vào quá trình tạo class đó."
```

---

# 57. Điều này giải thích tại sao `type` quan trọng

`type` vừa:

```python
type(obj)
```

để kiểm tra type,

vừa:

```python
type(name, bases, namespace)
```

để tạo class.

Và `type` là:

> **Metaclass mặc định của class trong Python.**

---

# 58. Bài tập thực hành

## Bài 1 — Meta đơn giản

Viết:

```python
class MyMeta(type):
    ...
```

sao cho khi tạo:

```python
class User(metaclass=MyMeta):
    pass
```

in:

```text
Creating User
```

---

## Bài 2 — Auto attribute

Metaclass tự động thêm:

```python
framework = "MyFramework"
```

để:

```python
User.framework
```

hoạt động.

---

## Bài 3 — Validation

Tất cả class kế thừa `Model` bắt buộc có:

```python
id
```

Ví dụ hợp lệ:

```python
class User(Model):
    id = IntegerField()
```

Ví dụ không hợp lệ:

```python
class Book(Model):
    title = StringField()
```

---

## Bài 4 — Registry

Tạo:

```python
PluginMeta
```

sao cho:

```python
class NovelPlugin(Plugin):
    pass

class MangaPlugin(Plugin):
    pass
```

tự động được đăng ký.

---

## Bài 5 — Mini ORM

Tạo:

```python
class ModelMeta(type):
    ...
```

sao cho:

```python
class User(Model):

    id = IntegerField()
    name = StringField()
```

tự động có:

```python
User._fields
```

với:

```text
id
name
```

---

# 59. Bài Deep Dive quan trọng nhất

Hãy giải thích chính xác đoạn:

```python
class ModelMeta(type):

    def __new__(
        mcls,
        name,
        bases,
        namespace,
    ):

        namespace["_framework"] = "ORM"

        return super().__new__(
            mcls,
            name,
            bases,
            namespace,
        )


class User(metaclass=ModelMeta):
    pass
```

Theo chuỗi:

```text
class User
    ↓
xác định metaclass
    ↓
ModelMeta
    ↓
ModelMeta.__new__()
    ↓
namespace được sửa
    ↓
type.__new__()
    ↓
User class object
    ↓
User._framework
```

Nếu bạn hiểu được chuỗi này, bạn đã thực sự bắt đầu hiểu Metaclass.

---

# 60. Tổng kết Buổi 27

Hôm nay hãy ghi nhớ 10 ý:

```text
1. Class cũng là object.

2. type là metaclass mặc định.

3. Metaclass là class dùng để tạo class.

4. metaclass=MyMeta cho phép chỉ định
   metaclass của class.

5. MyMeta thường kế thừa type.

6. Metaclass can thiệp vào class creation.

7. Metaclass nhận name, bases, namespace.

8. Metaclass có thể validate class.

9. Metaclass có thể modify class.

10. Metaclass có thể xây registry,
    ORM metadata, plugin system...
```

Mô hình cuối cùng:

```text
                    type
                     │
                     │ creates
                     ▼
                   Meta
                     │
                     │ creates
                     ▼
                   User
                     │
                     │ creates
                     ▼
                   user
```

Và kết nối với các bài trước:

```text
Descriptor
    ↓
attribute access

type()
    ↓
dynamic class creation

Metaclass
    ↓
control class creation
```

---

# Buổi 28 — `__new__` của Metaclass

Bài tiếp theo chúng ta sẽ **mổ xẻ cực sâu**:

```python
class ModelMeta(type):

    def __new__(
        mcls,
        name,
        bases,
        namespace,
    ):
        ...
```

Đặc biệt phân biệt:

```text
object.__new__()
        ↓
tạo instance

Class.__new__()
        ↓
tạo instance của class

Metaclass.__new__()
        ↓
tạo class object
```

và giải mã chính xác:

```python
super().__new__(
    mcls,
    name,
    bases,
    namespace,
)
```

đang làm gì.
