# OOP Deep Dive – Buổi 18

# Metaclass Deep Dive II – `__prepare__()`, `__new__()`, `__init__()` và xây dựng Plugin Framework

> **Đây là một trong những buổi "đỉnh cao" của OOP Python.**

Đến đây chúng ta đã học:

- Descriptor
- ABC
- Protocol
- Metaclass cơ bản

Hôm nay chúng ta sẽ kết hợp tất cả để hiểu **Python tạo một class như thế nào** và xây dựng một **Plugin Framework** giống như Django, SQLAlchemy hoặc pytest.

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

- Vòng đời tạo Class
- `__prepare__()`
- `__new__()` của Metaclass
- `__init__()` của Metaclass
- Sự khác nhau giữa ba hàm trên
- Plugin Registry
- Auto Registration
- Validation khi tạo class

---

# 1. Python tạo class như thế nào?

Giả sử

```text-x-trilium-auto
class Book(BaseModel):
    title = StringField()
    author = StringField()

    def save(self):
        ...
```

Python **không tạo class ngay lập tức**.

Nó trải qua nhiều bước.

---

# 2. Toàn bộ vòng đời

```text-x-trilium-auto
Đọc class

↓

Gọi __prepare__()

↓

Tạo namespace

↓

Thực thi code trong class

↓

Thu thập namespace

↓

Gọi __new__()

↓

Sinh class object

↓

Gọi __init__()

↓

Class sẵn sàng
```

Đây là quy trình thật của CPython.

---

# 3. `__prepare__()`

Đây là bước đầu tiên.

```text-x-trilium-auto
class MyMeta(type):

    @classmethod
    def __prepare__(

        cls,

        name,

        bases
    ):

        print("__prepare__")

        return {}
```

Python sẽ gọi trước khi thực thi thân class.

---

# 4. Namespace là gì?

Giả sử

```text-x-trilium-auto
class Book:

    title = "Python"

    pages = 500

    def hello(self):
        pass
```

Trong lúc class đang được tạo,

Python thực chất đang xây dựng một dictionary.

```text-x-trilium-auto
{
    "title": "Python",
    "pages": 500,
    "hello": hello
}
```

Dictionary này gọi là:

> Namespace.

---

# 5. Ví dụ

```text-x-trilium-auto
class MyMeta(type):

    @classmethod
    def __prepare__(

        cls,

        name,

        bases

    ):

        print("prepare")

        return {}
```

---

```text-x-trilium-auto
class Demo(

    metaclass=MyMeta
):

    x = 1

    y = 2
```

Kết quả

```text-x-trilium-auto
prepare
```

---

# 6. Tại sao cần `__prepare__()`?

Bạn có thể trả về:

- dict
- OrderedDict
- defaultdict
- hoặc một object mapping tự tạo

Ví dụ

```text-x-trilium-auto
from collections import OrderedDict
```

```text-x-trilium-auto
return OrderedDict()
```

Ngày nay `dict` của Python đã giữ thứ tự chèn (từ Python 3.7), nhưng `__prepare__()` vẫn hữu ích nếu bạn muốn dùng một kiểu mapping đặc biệt.

---

# 7. `__new__()`

Sau khi namespace hoàn thành.

Python gọi:

```text-x-trilium-auto
def __new__(

    cls,

    name,

    bases,

    attrs

):
```

`attrs`

chính là namespace.

Ví dụ

```text-x-trilium-auto
print(attrs)
```

↓

```text-x-trilium-auto
{
    "__module__":...,

    "__qualname__":...,

    "title":"Python",

    "save":...
}
```

---

# 8. Thêm attribute

```text-x-trilium-auto
class MyMeta(type):

    def __new__(

        cls,

        name,

        bases,

        attrs

    ):

        attrs["version"] = "1.0"

        return super().__new__(

            cls,

            name,

            bases,

            attrs

        )
```

---

```text-x-trilium-auto
class Book(

    metaclass=MyMeta

):
    pass
```

↓

```text-x-trilium-auto
Book.version
```

↓

```text-x-trilium-auto
1.0
```

---

# 9. `__init__()`

Sau khi class được tạo.

Python gọi:

```text-x-trilium-auto
def __init__(

    cls,

    name,

    bases,

    attrs

):
```

Lúc này:

Class đã tồn tại.

Bạn không tạo class nữa.

Chỉ cấu hình thêm.

---

# 10. So sánh

## `__prepare__()`

```text-x-trilium-auto
Chuẩn bị namespace
```

---

## `__new__()`

```text-x-trilium-auto
Tạo class object
```

---

## `__init__()`

```text-x-trilium-auto
Khởi tạo class object
```

---

# 11. Minh họa

```text-x-trilium-auto
            __prepare__

                  │

        tạo namespace

                  │

                  ▼

             __new__

                  │

          tạo class object

                  │

                  ▼

             __init__

                  │

        cấu hình class
```

---

# 12. Plugin Registry

Giả sử

```text-x-trilium-auto
PLUGIN_REGISTRY = {}
```

Ta muốn:

```text-x-trilium-auto
class TruyenFull(BaseSource):
```

↓

Tự động thêm vào registry.

---

# 13. Metaclass

```text-x-trilium-auto
PLUGIN_REGISTRY = {}


class SourceMeta(type):

    def __init__(

        cls,

        name,

        bases,

        attrs

    ):

        if name != "BaseSource":

            PLUGIN_REGISTRY[name] = cls

        super().__init__(

            name,

            bases,

            attrs

        )
```

---

# 14. Sử dụng

```text-x-trilium-auto
class BaseSource(

    metaclass=SourceMeta
):
    pass
```

---

```text-x-trilium-auto
class TruyenFull(

    BaseSource
):
    pass
```

---

```text-x-trilium-auto
class TangThuVien(

    BaseSource
):
    pass
```

---

Kết quả

```text-x-trilium-auto
print(PLUGIN_REGISTRY)
```

↓

```text-x-trilium-auto
{
    "TruyenFull":TruyenFull,

    "TangThuVien":TangThuVien
}
```

Không cần:

```text-x-trilium-auto
register(...)
```

---

# 15. Validation

Metaclass có thể kiểm tra.

Ví dụ

```text-x-trilium-auto
class SourceMeta(type):

    def __new__(

        cls,

        name,

        bases,

        attrs

    ):

        if "fetch" not in attrs:

            raise TypeError(

                "Missing fetch()"

            )

        return super().__new__(

            cls,

            name,

            bases,

            attrs
        )
```

---

Nếu plugin thiếu:

```text-x-trilium-auto
fetch()
```

↓

Lỗi ngay khi import.

Không đợi runtime.

---

# 16. Thu thập Descriptor

Giả sử

```text-x-trilium-auto
class Book:

    title = StringField()

    author = StringField()
```

Metaclass

có thể tìm:

```text-x-trilium-auto
for key,value in attrs.items():
```

↓

Nếu

```text-x-trilium-auto
isinstance(

    value,

    Field
)
```

↓

Lưu metadata.

Đây chính là cách Django ORM hoạt động ở mức khái niệm.

---

# 17. Tạo `_fields`

```text-x-trilium-auto
attrs["_fields"] = {}
```

---

```text-x-trilium-auto
for key,value in attrs.items():

    if isinstance(

        value,

        Field

    ):

        attrs["_fields"][key] = value
```

Sau này

```text-x-trilium-auto
Book._fields
```

↓

```text-x-trilium-auto
{
    "title":...,

    "author":...
}
```

---

# 18. Mini ORM

Model

```text-x-trilium-auto
class Novel(Model):

    title = StringField()

    url = UrlField()

    views = IntegerField()
```

Metaclass

↓

Tự tạo

```text-x-trilium-auto
_fields
```

Sau này

```text-x-trilium-auto
Novel._fields
```

↓

Phục vụ:

- SQL
- Validation
- Serialization

---

# 19. Tự sinh SQL

Giả sử

```text-x-trilium-auto
Novel._fields
```

↓

```text-x-trilium-auto
title

url

views
```

Metaclass có thể sinh

```text-x-trilium-auto
CREATE TABLE novel (

title TEXT,

url TEXT,

views INTEGER

)
```

Đây là ý tưởng nền tảng của ORM.

---

# 20. Auto Plugin

Giả sử

```text-x-trilium-auto
plugins/
```

có

```text-x-trilium-auto
truyenfull.py

metruyen.py

novelbin.py
```

Mỗi file

↓

Import

↓

Metaclass chạy

↓

Registry đầy đủ.

Plugin Manager chỉ cần:

```text-x-trilium-auto
PLUGIN_REGISTRY
```

---

# 21. Kết hợp với ABC

```text-x-trilium-auto
class BaseSource(

    ABC,

    metaclass=SourceMeta
)
```

Có thể:

- ép implement
- tự đăng ký plugin

Một lưu ý quan trọng: nếu kết hợp `ABC` với metaclass riêng, metaclass của bạn thường cần kế thừa từ `ABCMeta` thay vì `type` để tránh xung đột metaclass.

Ví dụ:

```text-x-trilium-auto
from abc import ABCMeta

class SourceMeta(ABCMeta):
    ...
```

---

# 22. Kết hợp với Descriptor

```text-x-trilium-auto
class Novel(Model):

    title = StringField()

    url = UrlField()
```

Descriptor

↓

Validation.

Metaclass

↓

Thu thập field.

Hai cơ chế phối hợp với nhau.

---

# 23. Áp dụng vào dự án crawler

Kiến trúc đề xuất:

```text-x-trilium-auto
                    SourceMeta
                         │
        Auto register + Validation
                         │
                         ▼
                    BaseSource (ABC)
                         ▲
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
  TruyenFull       TangThuVien      NovelBin
```

`CrawlerService`

không cần biết:

- có bao nhiêu source.
- source ở đâu.

Chỉ cần:

```text-x-trilium-auto
PLUGIN_REGISTRY
```

---

# 24. Vòng đời Plugin

```text-x-trilium-auto
Import plugin

↓

Metaclass

↓

Validate

↓

Register

↓

Ready
```

Không cần:

```text-x-trilium-auto
register()

init()

setup()
```

---

# 25. Tổng kết

```text-x-trilium-auto
              Metaclass

                    │

     ┌──────────────┼──────────────┐

     ▼              ▼              ▼

__prepare__     __new__      __init__

     │              │              │

 Namespace      Create       Configure

     │

     ▼

Descriptor / Plugin / ORM
```

---

# Điều quan trọng nhất cần nhớ

Metaclass **không phải để tạo object**.

Metaclass dùng để:

- tạo class.
- sửa class.
- kiểm tra class.
- đăng ký class.
- thu thập metadata.

Đây là nền tảng của:

- Django ORM
- SQLAlchemy
- Enum
- Plugin Framework
- Serializer Framework

---

# Bài tập thực hành

## Bài 1

Viết `MyMeta`:

- In tên class trong `__prepare__()`.
- In namespace trong `__new__()`.
- In thông báo trong `__init__()`.

Quan sát thứ tự thực thi.

---

## Bài 2

Tạo:

```text-x-trilium-auto
MODEL_REGISTRY = {}
```

Viết metaclass:

```text-x-trilium-auto
ModelMeta
```

Tự động thêm mọi model vào registry.

---

## Bài 3

Viết metaclass kiểm tra:

Nếu class có tên kết thúc bằng:

```text-x-trilium-auto
Repository
```

thì bắt buộc phải có:

```text-x-trilium-auto
save()
```

Nếu thiếu

↓

Raise `TypeError`.

---

## Bài 4 (Áp dụng dự án crawler)

Thiết kế hoàn chỉnh:

- `SourceMeta` (kế thừa `ABCMeta`).
- `BaseSource`.
- `Field` (Descriptor).
- `ModelMeta`.
- `Novel` model.
- `CrawlerService`.

Yêu cầu:

- Source tự đăng ký.
- Model tự thu thập Field.
- Validation diễn ra trong Descriptor.
- `CrawlerService` chỉ làm việc với registry và contract của `BaseSource`.

Đây chính là kiến trúc thu nhỏ của một framework Python hiện đại.

---

# Chuẩn bị cho Buổi 19

Từ buổi sau, chúng ta sẽ rời khỏi thế giới **tạo class**, để đi vào **quản lý vòng đời object** với các "magic methods" nâng cao:

- `__new__()` của object.
- `__init__()`.
- `__del__()`.
- Immutable object.
- Singleton Pattern.
- Flyweight Pattern.
- Object Pool.

Đây là những kỹ thuật được sử dụng trong các hệ thống hiệu năng cao, cache và framework Python chuyên nghiệp.