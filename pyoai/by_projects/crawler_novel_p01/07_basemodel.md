# Phần II — Model Layer

# Buổi 7 — Thiết kế BaseModel

> Đây là buổi quan trọng nhất của toàn bộ tầng Model.
>
> Nếu `BaseModel` được thiết kế tốt, sau này `Story`, `Chapter`, `Author`, `Category`... chỉ còn vài dòng code.

---

# Mục tiêu

Sau buổi này bạn sẽ:

* Hiểu Model thực sự là gì
* Phân biệt Model và Repository
* Xây dựng BaseModel theo hướng framework
* Có khả năng serialize / deserialize
* Theo dõi trạng thái object (dirty tracking)
* Chuẩn bị cho BaseRepository

---

# 1. Model là gì?

Nhiều người nghĩ Model là:

```python
class Story:

    def __init__(...):
        ...
```

Không.

Trong framework, Model là đại diện của **một bản ghi (row)** trong database.

Ví dụ

```text
story table

+----+------------------+-----------+
| id | title            | author_id |
+----+------------------+-----------+
| 1  | Đấu Phá...       | 5         |
+----+------------------+-----------+
```

↓

Python

```python
Story(id=1, title="Đấu Phá...", author_id=5)
```

Một object

↓

Một row.

---

# 2. Điều Model KHÔNG được làm

Model không được:

❌ mở sqlite

❌ execute SQL

❌ commit

❌ rollback

❌ query

Sai:

```python
class Story:
    def save(self): ...
```

Hoặc

```python
story.delete()
```

Đó là Active Record.

Framework của chúng ta dùng

```text
Repository Pattern
```

nên Model phải là

```text
Data Object
```

---

# 3. Trách nhiệm của Model

Model chỉ có nhiệm vụ:

✓ chứa dữ liệu

✓ validate

✓ serialize

✓ deserialize

✓ dirty tracking

✓ metadata

Không làm gì khác.

---

# 4. Kiến trúc

```text
SQLite

↓

Repository

↓

Dictionary

↓

BaseModel

↓

Story
```

Repository nhận dữ liệu

↓

chuyển thành Model.

---

# 5. Thiết kế BaseModel

Tạo

```text
framework/

    model/

        base_model.py
```

---

# 6. Constructor

```python
class BaseModel:
    def __init__(self, **kwargs):

        self._data = {}

        self._original = {}

        self._dirty = set()

        self.load(kwargs)
```

Có ba thành phần:

```text
_data

dữ liệu hiện tại
```

```text
_original

dữ liệu lúc load
```

```text
_dirty

những field đã đổi
```

---

# 7. load()

```python
def load(self, values):

    self._data.update(values)

    self._original = dict(values)

    self._dirty.clear()
```

Ví dụ

```python
story.load({"title": "ABC", "author_id": 5})
```

---

# 8. get()

```python
def get(self, key, default=None):

    return self._data.get(key, default)
```

Ví dụ

```python
story.get("title")
```

↓

```text
ABC
```

---

# 9. set()

```python
def set(self, key, value):

    old = self._data.get(key)

    self._data[key] = value

    if old != value:
        self._dirty.add(key)
```

Ví dụ

```python
story.set("title", "One Piece")
```

Dirty

```text
title
```

---

# 10. Dirty Tracking

Ban đầu

```python
Story(title="ABC")
```

Dirty

↓

rỗng

Sau

```python
story.set("title", "XYZ")
```

Dirty

↓

```text
title
```

Repository sẽ biết

field nào đổi.

---

# 11. is_dirty()

```python
def is_dirty(self):

    return bool(self._dirty)
```

Ví dụ

```python
story.is_dirty()
```

↓

```text
True
```

---

# 12. dirty_fields()

```python
def dirty_fields(self):

    return sorted(self._dirty)
```

Ví dụ

```python
["title", "author_id"]
```

---

# 13. reset_dirty()

Sau khi save

Repository sẽ gọi

```python
def reset_dirty(self):

    self._original = dict(self._data)

    self._dirty.clear()
```

Object trở lại

Clean.

---

# 14. to_dict()

Đây là hàm Repository sẽ dùng.

```python
def to_dict(self):

    return dict(self._data)
```

Ví dụ

```python
{"id": 1, "title": "ABC"}
```

---

# 15. from_dict()

```python
@classmethod
def from_dict(cls, values):

    return cls(**values)
```

Ví dụ

```python
row = {"id": 1, "title": "Python"}

story = Story.from_dict(row)
```

---

# 16. update()

```python
def update(self, values):

    for key, value in values.items():
        self.set(key, value)
```

Ví dụ

```python
story.update({"title": "XYZ", "author_id": 7})
```

---

# 17. **getitem**

Để dùng

```python
story["title"]
```

```python
def __getitem__(self, key):

    return self._data[key]
```

---

# 18. **setitem**

```python
story["title"] = "ABC"
```

↓

```python
def __setitem__(self, key, value):

    self.set(key, value)
```

---

# 19. **repr**

```python
def __repr__(self):

    return f"{self.__class__.__name__}({self._data})"
```

Kết quả

```text
Story({

'id':1,

'title':'ABC'

})
```

Debug rất dễ.

---

# 20. Thiết kế chuyên nghiệp hơn

Phiên bản trên hoạt động tốt, nhưng để framework đủ mạnh, chúng ta nên bổ sung thêm các khái niệm sau.

## Metadata của Model

Mỗi Model nên khai báo:

```python
class Story(BaseModel):
    __table__ = "story"

    __primary_key__ = "id"

    __fields__ = (
        "id",
        "title",
        "author_id",
        "cover",
    )
```

Repository sẽ không cần hard-code tên bảng nữa.

---

## Field Validation

BaseModel nên có:

```python
def validate(self):
    pass
```

Mặc định không làm gì.

Các model con sẽ override:

```python
class Story(BaseModel):
    def validate(self):

        if not self["title"]:
            raise ValueError("title is required")
```

Repository sẽ gọi:

```python
story.validate()
```

trước khi lưu.

---

## Theo dõi trạng thái Model

Ngoài dirty field, mỗi object có thể có trạng thái:

```text
NEW

LOADED

MODIFIED

DELETED
```

Điều này sẽ rất hữu ích khi xây dựng **Unit of Work** sau này.

---

# Ví dụ hoàn chỉnh

```python
story = Story.from_dict({"id": 1, "title": "Đấu Phá"})

print(story.is_dirty())

story["title"] = "One Piece"

print(story.dirty_fields())

print(story.to_dict())
```

Kết quả

```text
False

['title']

{

'id':1,

'title':'One Piece'

}
```

---

# Kiến trúc sau buổi 7

```text
SQLite

↓

Repository

↓

dict

↓

BaseModel

↓

Story

↓

Application
```

Model hoàn toàn không biết SQLite tồn tại.

---

# Bài tập

## Bài 1

Viết đầy đủ `BaseModel` gồm:

* `load()`
* `get()`
* `set()`
* `update()`
* `to_dict()`
* `from_dict()`
* `is_dirty()`
* `dirty_fields()`
* `reset_dirty()`

---

## Bài 2

Thêm các magic method:

* `__getitem__`
* `__setitem__`
* `__repr__`

---

## Bài 3

Tạo model thử nghiệm:

```python
class DemoModel(BaseModel):
    __table__ = "demo"

    __primary_key__ = "id"
```

và kiểm tra:

```python
demo["name"] = "Python"

print(demo.is_dirty())

print(demo.to_dict())
```

---

# Kết quả sau buổi 7

Bạn đã xây dựng được nền móng của tầng Model:

```text
BaseModel
    │
    ├── Data Storage
    ├── Dirty Tracking
    ├── Serialization
    ├── Validation Hook
    └── Metadata
```

Đây sẽ là lớp cha cho tất cả các model trong framework.

---

# Chuẩn bị cho Buổi 8

Ở buổi tiếp theo, chúng ta sẽ xây dựng **StoryModel** một cách hoàn chỉnh:

* Kế thừa `BaseModel`.
* Khai báo metadata (`__table__`, `__fields__`, `__primary_key__`).
* Thêm validation nghiệp vụ (ví dụ: tiêu đề không được rỗng).
* Thêm các thuộc tính tính toán (computed properties), chẳng hạn `is_completed`, `chapter_count`.
* Chuẩn bị để kết nối trực tiếp với `StoryRepository` ở các buổi tiếp theo.

Từ buổi 8 trở đi, chúng ta sẽ bắt đầu tạo các model thực tế của ứng dụng đọc và cào truyện.
