# Dataclass Deep Dive - Buổi 7

# `slots=True` Deep Dive (Memory Optimization)

> Đây là một trong những tính năng được đánh giá cao nhất của Python 3.10+.

Nếu dự án của bạn chỉ tạo vài chục object thì gần như không có khác biệt.

Nhưng nếu dự án tạo:

- 100.000 Chapter
- 500.000 Novel
- 3 triệu Comment
- 10 triệu CrawlTask

thì `slots=True` có thể giúp giảm hàng chục đến hàng trăm MB RAM.

Trong hệ thống crawler truyện mà bạn đang xây dựng, đây là một kiến thức rất thực tế.

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

- `__dict__` là gì?
- Python lưu thuộc tính như thế nào?
- `__slots__`
- `slots=True`
- Memory layout
- Benchmark
- Khi nào nên dùng
- Khi nào không nên dùng

---

# 1. Mọi object Python lưu dữ liệu ở đâu?

Ví dụ

```text-x-trilium-auto
class Student:

    def __init__(self):
        self.id = 1
        self.name = "An"
```

Tạo object

```text-x-trilium-auto
s = Student()
```

Thử

```text-x-trilium-auto
print(s.__dict__)
```

Kết quả

```text-x-trilium-auto
{
    "id": 1,
    "name": "An"
}
```

---

## **dict** là gì?

Đây là Dictionary chứa toàn bộ attribute.

```text-x-trilium-auto
Student Object

+--------------------+

__dict__

↓

{

"id":1,

"name":"An"

}

+--------------------+
```

Mỗi lần

```text-x-trilium-auto
s.name
```

Python thực chất làm

```text-x-trilium-auto
s.__dict__["name"]
```

(đã được tối ưu bên trong CPython nhưng ý tưởng là như vậy).

---

# 2. Vì sao **dict** tốn RAM?

Dictionary rất linh hoạt.

Có thể thêm thuộc tính bất kỳ.

```text-x-trilium-auto
s.age = 20

s.email = "abc"

s.phone = "123"
```

Đều hợp lệ.

```text-x-trilium-auto
print(s.__dict__)
```

```text-x-trilium-auto
{
    'id': 1,
    'name': 'An',
    'age': 20,
    'email': 'abc',
    'phone': '123'
}
```

Python phải dành bộ nhớ cho Dictionary.

---

# 3. Hàng triệu object

Ví dụ

```text-x-trilium-auto
1 object

↓

__dict__

↓

Dictionary
```

1000000 object

↓

1000000 Dictionary

↓

Rất tốn RAM.

---

# 4. **slots**

Python có cơ chế

```text-x-trilium-auto
__slots__
```

Ví dụ

```text-x-trilium-auto
class Student:

    __slots__ = (
        "id",
        "name"
    )

    def __init__(self,id,name):
        self.id=id
        self.name=name
```

Lúc này

```text-x-trilium-auto
print(hasattr(s,"__dict__"))
```

Kết quả

```text-x-trilium-auto
False
```

Không còn Dictionary.

---

# 5. Dataclass hỗ trợ slots

Python 3.10

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass(slots=True)
class Student:

    id:int

    name:str
```

Dataclass tự sinh

```text-x-trilium-auto
__slots__
```

Bạn không cần viết tay.

---

# 6. Kiểm tra

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass(slots=True)
class Student:

    id:int

    name:str
```

```text-x-trilium-auto
s=Student(1,"An")
```

```text-x-trilium-auto
print(hasattr(s,"__dict__"))
```

Kết quả

```text-x-trilium-auto
False
```

---

# 7. Không thể thêm thuộc tính mới

Class bình thường

```text-x-trilium-auto
s.age=20
```

Được.

Slots

```text-x-trilium-auto
s.age=20
```

Kết quả

```text-x-trilium-auto
AttributeError
```

Vì

```text-x-trilium-auto
age
```

không nằm trong

```text-x-trilium-auto
__slots__
```

---

# 8. Minh họa bộ nhớ

Không Slots

```text-x-trilium-auto
Student

↓

__dict__

↓

{
id

name

email

phone

...
}
```

Slots

```text-x-trilium-auto
Student

↓

id

name
```

Không còn Dictionary.

---

# 9. Benchmark RAM

Ví dụ benchmark đơn giản:

```text-x-trilium-auto
from dataclasses import dataclass import sys

@dataclass class A:
    x:int
    y:int


@dataclass(slots=True)
class B:
    x:int
    y:int


a=A(1,2)
b=B(1,2)

print(sys.getsizeof(a))
print(sys.getsizeof(b))
```

Bạn sẽ thấy object dùng `slots` thường nhỏ hơn, nhưng lưu ý:

> `sys.getsizeof()` **không tính kích thước của** `**__dict__**` **và các đối tượng mà nó tham chiếu**.

Muốn đo chính xác tổng bộ nhớ, cần dùng thư viện như `pympler` hoặc `tracemalloc`.

---

# 10. Benchmark tốc độ

Truy cập

```text-x-trilium-auto
obj.name
```

Slots

↓

nhanh hơn một chút.

Lý do

Không cần tra Dictionary.

Mức cải thiện thường nhỏ (vài phần trăm), nhưng với hàng triệu lần truy cập có thể đáng kể.

---

# 11. fields()

Không ảnh hưởng.

```text-x-trilium-auto
from dataclasses import fields

print(fields(Student))
```

Hoạt động bình thường.

---

# 12. asdict()

```text-x-trilium-auto
from dataclasses import asdict

print(asdict(s))
```

Kết quả

```text-x-trilium-auto
{
'id':1,

'name':'An'
}
```

Slots không ảnh hưởng.

---

# 13. Frozen + Slots

Có thể kết hợp

```text-x-trilium-auto
@dataclass(

slots=True,

frozen=True

)
```

Đây là một trong những cấu hình phổ biến nhất.

Ví dụ

```text-x-trilium-auto
@dataclass(
    slots=True,
    frozen=True
)
class ChapterID:

    source:str

    id:str
```

Object

- nhỏ
- immutable
- hashable (trong điều kiện phù hợp)

---

# 14. Kế thừa

Ví dụ

```text-x-trilium-auto
@dataclass(slots=True)
class Animal:

    name:str
```

```text-x-trilium-auto
@dataclass(slots=True)
class Dog(Animal):

    age:int
```

Được.

Dataclass sẽ hợp nhất `__slots__` của lớp cha và lớp con.

---

# 15. Không nên tự viết **slots**

Sai

```text-x-trilium-auto
@dataclass(slots=True)
class Student:

    __slots__=("id",)

    id:int
```

Python báo lỗi.

Vì

`slots=True`

đã tự sinh rồi.

---

# 16. dir()

```text-x-trilium-auto
print(dir(s))
```

Bạn sẽ thấy

```text-x-trilium-auto
__slots__
```

xuất hiện.

---

# 17. Ứng dụng Crawler

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass(slots=True)
class Chapter:

    id:int

    title:str

    url:str

    html:str
```

Giả sử

```text-x-trilium-auto
200000 Chapter
```

Slots

↓

giảm đáng kể RAM.

Đặc biệt nếu mỗi `Chapter` chỉ chứa vài thuộc tính cố định.

---

# 18. Khi nào nên dùng?

Nên

✔ DTO

✔ Event

✔ Config

✔ Parser Result

✔ Queue Item

✔ API Response

✔ Chapter

✔ Novel

✔ Author

✔ Category

✔ Metadata

Đây đều là các mô hình dữ liệu có cấu trúc ổn định.

---

# 19. Khi nào không nên?

Ví dụ

Plugin

```text-x-trilium-auto
obj.xxx=...

obj.yyy=...

obj.zzz=...
```

Luôn thêm attribute động.

Không dùng Slots.

---

ORM cũ

Một số ORM hoặc framework cũ thêm thuộc tính động vào object.

Nếu dùng `slots=True` có thể gây lỗi.

---

Monkey Patch

```text-x-trilium-auto
obj.debug=True
```

Không làm được.

---

# 20. Slots và Pickle

Hiện nay (Python 3.11+), dataclass với `slots=True` vẫn có thể được `pickle` bình thường trong hầu hết các trường hợp.

```text-x-trilium-auto
import pickle

data = pickle.dumps(s)
obj = pickle.loads(data)
```

Hoạt động bình thường.

---

# 21. Slots và Weak Reference

Một điểm cần lưu ý.

Class có `__slots__` **không hỗ trợ weak reference mặc định**.

Ví dụ

```text-x-trilium-auto
import weakref

weakref.ref(obj)
```

Có thể báo lỗi.

Nếu cần hỗ trợ, từ Python 3.11 có thể dùng:

```text-x-trilium-auto
@dataclass(
    slots=True,
    weakref_slot=True
)
class Student:
    id: int
```

Dataclass sẽ thêm `__weakref__` vào `__slots__`.

---

# 22. So sánh

| Tính năng | Class thường | slots=True |
| --- | --- | --- |
| Có `__dict__` | ✔   | ✘   |
| Thêm attribute mới | ✔   | ✘   |
| Tiết kiệm RAM | ✘   | ✔   |
| Truy cập attribute | Bình thường | Nhanh hơn một chút |
| Linh hoạt | Cao | Thấp |

---

# 23. Kiến trúc trong dự án crawler

Mình khuyến nghị:

```text-x-trilium-auto
models/

    chapter.py
        slots=True

    author.py
        slots=True

    category.py
        slots=True

    image.py
        slots=True

    novel.py
        slots=True
```

Trong khi

```text-x-trilium-auto
services/

repositories/

plugins/
```

thì **không nên** dùng `slots=True` vì các lớp này thường chứa nhiều hành vi hơn dữ liệu và đôi khi cần mở rộng linh hoạt.

---

# 24. Best Practice

Đối với hệ thống crawler của bạn, một cấu hình rất hợp lý là:

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass(
    slots=True,
    frozen=True
)
class NovelID:

    source: str

    novel_id: str
```

Hoặc

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass(
    slots=True
)
class Chapter:

    id: int
    title: str
    url: str
    index: int
```

Những đối tượng này:

- được tạo rất nhiều,
- có cấu trúc cố định,
- không cần thêm thuộc tính động,

nên `slots=True` mang lại lợi ích rõ rệt.

---

# Tổng kết

| Tùy chọn | Ý nghĩa |
| --- | --- |
| `slots=True` | Tự sinh `__slots__` |
| `__dict__` | Bị loại bỏ |
| RAM | Giảm đáng kể khi có nhiều object |
| Tốc độ | Truy cập thuộc tính nhanh hơn một chút |
| Attribute mới | Không thể thêm động |
| Kết hợp tốt | `frozen=True` |

---

# Bài tập thực hành

## Bài 1

Tạo hai lớp:

```text-x-trilium-auto
@dataclass class User:
    id: int
    name: str
```

và

```text-x-trilium-auto
@dataclass(slots=True)
class UserSlots:
    id: int
    name: str
```

Kiểm tra:

```text-x-trilium-auto
hasattr(obj, "__dict__")
```

và thử thêm:

```text-x-trilium-auto
obj.email = "abc@example.com"
```

Quan sát sự khác biệt.

---

## Bài 2

Thiết kế:

```text-x-trilium-auto
@dataclass(
    slots=True,
    frozen=True
)
class ChapterID:
    source: str
    chapter_id: str
```

Kiểm tra:

- Có sửa được field không?
- Có dùng làm key của `dict` được không?

---

## Bài 3 (Áp dụng dự án crawler)

Thiết kế các dataclass sau với `slots=True`:

- `Author`
- `Category`
- `Image`
- `Chapter`
- `NovelSummary`

Viết một đoạn mã tạo danh sách gồm **100.000** `Chapter` và dùng `tracemalloc` để quan sát mức sử dụng bộ nhớ trong quá trình tạo đối tượng. Sau đó, lặp lại với phiên bản không dùng `slots=True` để tự đánh giá sự khác biệt.

---

# Chuẩn bị cho Buổi 8

Buổi tiếp theo chúng ta sẽ học **Keyword-only Fields (**`**kw_only=True**`**) Deep Dive**.

Đây là một tính năng mới từ Python 3.10 giúp:

- Thiết kế API rõ ràng hơn.
- Tránh truyền nhầm tham số khi constructor có nhiều đối số.
- Tạo các dataclass dễ mở rộng mà vẫn giữ khả năng tương thích ngược (backward compatibility).
- Thiết kế các lớp cấu hình (`Config`), tham số crawler (`CrawlerOptions`) và request object chuyên nghiệp hơn.

Đây là một tính năng rất hữu ích trong các thư viện và framework hiện đại.