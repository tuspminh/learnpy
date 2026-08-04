# Phần II — Model Layer

# Buổi 8 — Xây dựng StoryModel chuyên nghiệp

> Hôm nay chúng ta sẽ xây dựng **model đầu tiên** của framework.
>
> Không chỉ là một class chứa dữ liệu, mà là một model có metadata, validation, computed property và sẵn sàng làm việc với `StoryRepository`.

---

# Mục tiêu

Sau buổi này bạn sẽ xây dựng được:

* StoryModel hoàn chỉnh
* Metadata của Model
* Validation
* Computed Property
* Business Method
* Factory Method
* Chuẩn bị cho Repository

---

# 1. Story là Entity quan trọng nhất

Trong toàn bộ hệ thống

```text
Author
    │
    │1
    │
    ▼
 Story
    │
    │1
    │
    ▼
 Chapter
```

Mọi thứ đều xoay quanh Story.

---

# 2. StoryModel nằm ở đâu?

```text
framework/

    model/

        base_model.py

        story.py
```

---

# 3. Kế thừa BaseModel

```python
from framework.model.base_model import BaseModel


class Story(BaseModel):
    pass
```

Lúc này Story đã có:

* dirty tracking
* load()
* update()
* to_dict()
* from_dict()

mà không cần viết lại.

---

# 4. Metadata

Đây là phần rất quan trọng.

```python
class Story(BaseModel):
    __table__ = "story"

    __primary_key__ = "id"

    __fields__ = (
        "id",
        "source_id",
        "title",
        "slug",
        "author_id",
        "cover",
        "description",
        "status",
        "total_chapters",
        "last_chapter",
        "created_at",
        "updated_at",
    )
```

Sau này Repository sẽ đọc metadata này.

Ví dụ

```python
Story.__table__
```

↓

```text
story
```

---

# 5. Giá trị mặc định

Một Story mới nên có dữ liệu mặc định.

```python
DEFAULTS = {
    "status": "ongoing",
    "total_chapters": 0,
    "cover": "",
    "description": "",
    "last_chapter": "",
}
```

Trong constructor:

```python
def __init__(self, **kwargs):

    values = dict(self.DEFAULTS)

    values.update(kwargs)

    super().__init__(**values)
```

---

# 6. Validation

Story phải có title.

```python
def validate(self):

    if not self["title"]:
        raise ValueError("Title is required.")
```

---

Story phải có slug.

```python
if not self["slug"]:
    raise ValueError("Slug is required.")
```

---

Chapter không âm.

```python
if self["total_chapters"] < 0:
    raise ValueError("Invalid chapter count.")
```

---

# 7. Status

Ta thống nhất.

```text
ongoing

completed

paused

dropped
```

Không dùng

```text
Done

Finish

OK

...
```

Validation:

```python
STATUS = {"ongoing", "completed", "paused", "dropped"}
```

```python
if self["status"] not in self.STATUS:
    raise ValueError("Invalid status.")
```

---

# 8. Computed Property

Story đã hoàn thành?

Không cần lưu

```text
is_completed
```

vào database.

Ta tính.

```python
@property
def is_completed(self):

    return self["status"] == "completed"
```

---

# 9. Có cover?

```python
@property
def has_cover(self):

    return bool(self["cover"])
```

---

# 10. Có description?

```python
@property
def has_description(self):

    return bool(self["description"])
```

---

# 11. Display Title

Nhiều website

```text
one-piece
```

Ta muốn

```text
One Piece
```

```python
@property
def display_title(self):

    return self["title"].strip()
```

Sau này có thể xử lý Unicode.

---

# 12. Business Method

Ví dụ

Crawler thêm chapter.

```python
story.add_chapter()
```

↓

```python
def add_chapter(self):

    self["total_chapters"] += 1
```

---

Đổi trạng thái

```python
story.mark_completed()
```

↓

```python
def mark_completed(self):

    self["status"] = "completed"
```

---

Đổi mô tả

```python
def set_description(self, text):

    self["description"] = text.strip()
```

---

# 13. Factory Method

Ví dụ

Crawler vừa parse.

```python
data = {"title": "ABC", "slug": "abc"}
```

Ta muốn

```python
story = Story.from_crawler(data)
```

```python
@classmethod
def from_crawler(cls, data):

    return cls(title=data["title"], slug=data["slug"])
```

Sau này parse HTML rất tiện.

---

# 14. Clone

Đôi khi cần copy.

```python
story2 = story.clone()
```

↓

```python
def clone(self):

    return Story(**self.to_dict())
```

---

# 15. Serialize

Ví dụ

```python
story.to_dict()
```

↓

```python
{

"id":1,

"title":"ABC",

...
}
```

Sau này

JSON

API

Backup

đều dùng.

---

# 16. Deserialize

```python
Story.from_dict(...)
```

↓

Story object.

Không cần Repository biết constructor.

---

# 17. Kiểm thử

```python
story = Story(title="Đấu Phá", slug="dau-pha")
```

```python
print(story.is_completed)
```

↓

```text
False
```

---

```python
story.mark_completed()
```

↓

```python
print(story.is_completed)
```

↓

```text
True
```

---

# 18. Một số cải tiến nên áp dụng

Phiên bản hiện tại hoạt động tốt, nhưng để framework dễ bảo trì hơn, chúng ta nên bổ sung:

## Dùng Enum cho trạng thái

Thay vì:

```python
STATUS = {
    "ongoing",
    "completed",
    "paused",
    "dropped",
}
```

nên dùng:

```python
from enum import Enum


class StoryStatus(Enum):
    ONGOING = "ongoing"
    COMPLETED = "completed"
    PAUSED = "paused"
    DROPPED = "dropped"
```

Điều này tránh lỗi gõ sai chuỗi.

---

## Không hard-code tên trường

Thay vì:

```python
self["title"]
```

có thể khai báo:

```python
FIELD_TITLE = "title"
FIELD_STATUS = "status"
```

Hoặc dùng metadata `__fields__` để kiểm tra field hợp lệ trong `BaseModel`.

---

## Validation theo nhiều bước

Thay vì một `validate()` duy nhất, có thể chia nhỏ:

```python
def validate(self):
    self.validate_title()
    self.validate_slug()
    self.validate_status()
```

Mỗi hàm chỉ kiểm tra một trách nhiệm.

---

## Chuẩn bị cho quan hệ

Trong tương lai, `Story` có thể có:

```python
story.author

story.categories

story.chapters
```

Nhưng **không tải dữ liệu trong Model**. Những thuộc tính này sẽ được Repository hoặc Service gán khi cần (lazy/eager loading), tránh để Model phụ thuộc vào Database.

---

# Kiến trúc sau buổi 8

```text
BaseModel
      │
      ▼
Story
      │
      ├── Validation
      ├── Business Methods
      ├── Computed Properties
      ├── Metadata
      └── Serialization
```

---

# Bài tập

## Bài 1

Hoàn thiện `Story` với:

* `DEFAULTS`
* `validate()`
* `clone()`
* `from_crawler()`

---

## Bài 2

Viết các computed property:

* `is_completed`
* `has_cover`
* `has_description`
* `display_title`

---

## Bài 3

Viết các business method:

* `mark_completed()`
* `add_chapter()`
* `set_description()`

Sau mỗi thao tác, kiểm tra:

```python
print(story.is_dirty())

print(story.dirty_fields())
```

để quan sát cơ chế dirty tracking của `BaseModel`.

---

# Kết quả sau buổi 8

Đến thời điểm này, bạn đã có một `StoryModel` đủ mạnh để sử dụng trong dự án thực tế:

* Kế thừa toàn bộ khả năng của `BaseModel`.
* Có metadata để Repository tự động sinh SQL.
* Có validation nghiệp vụ.
* Có computed property thay vì lưu dữ liệu dư thừa.
* Có business method để thao tác với đối tượng.
* Có factory method phục vụ crawler.

## Chuẩn bị cho Buổi 9

Ở buổi tiếp theo, chúng ta sẽ xây dựng **ChapterModel**.

Khác với `Story`, `Chapter` có nhiều yêu cầu đặc biệt:

* Đảm bảo thứ tự chương (`chapter_no`).
* Hỗ trợ chương đặc biệt (ngoại truyện, chương 0, chương 10.5...).
* Quản lý URL gốc và nội dung.
* Chuẩn bị cho cơ chế cập nhật nội dung khi crawler chạy lại.

Đây sẽ là model đầu tiên có quan hệ trực tiếp với `Story` thông qua `story_id`, mở đầu cho việc xây dựng tầng Repository ở các buổi tiếp theo.
