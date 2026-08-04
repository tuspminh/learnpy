# Phần II — Model Layer

# Buổi 9 — Xây dựng ChapterModel chuyên nghiệp

> `Chapter` là model được truy cập nhiều nhất trong toàn bộ ứng dụng.
>
> Một ứng dụng đọc truyện có thể chỉ có vài chục nghìn `Story`, nhưng có thể có **hàng chục triệu `Chapter`**. Vì vậy, `ChapterModel` phải được thiết kế vừa chính xác vừa tối ưu.

---

# Mục tiêu

Sau buổi này bạn sẽ:

* Xây dựng `ChapterModel`
* Thiết kế metadata
* Validation cho chương
* Computed Property
* Business Method
* Chuẩn bị cho `ChapterRepository`

---

# 1. Chapter trong hệ thống

Quan hệ:

```text
Story
   │
   │ 1
   ▼
Chapter
```

Một truyện

↓

Nhiều chương

---

# 2. Vị trí

```text
framework/
│
└── model/
    │
    ├── base_model.py
    ├── story.py
    └── chapter.py
```

---

# 3. Metadata

```python
from framework.model.base_model import BaseModel


class Chapter(BaseModel):

    __table__ = "chapter"

    __primary_key__ = "id"

    __fields__ = (

        "id",

        "story_id",

        "source_id",

        "chapter_no",

        "title",

        "url",

        "content",

        "created_at",

        "updated_at",

    )
```

---

# 4. DEFAULTS

```python
DEFAULTS = {

    "title": "",

    "content": "",

    "url": "",

}
```

Constructor

```python
def __init__(self, **kwargs):

    values = dict(self.DEFAULTS)

    values.update(kwargs)

    super().__init__(**values)
```

---

# 5. Validation

## story_id

```python
if self["story_id"] is None:

    raise ValueError(

        "story_id is required."

    )
```

---

## title

```python
if not self["title"]:

    raise ValueError(

        "title is required."

    )
```

---

## url

```python
if not self["url"]:

    raise ValueError(

        "url is required."

    )
```

---

## chapter_no

```python
if self["chapter_no"] < 0:

    raise ValueError(

        "Invalid chapter number."

    )
```

---

# 6. Vì sao chapter_no dùng REAL?

Nhiều website có:

```text
Chương 10

↓

Chương 10.5

↓

Chương 11
```

Nếu dùng

```text
INTEGER
```

không lưu được

```text
10.5
```

SQLite

```text
REAL
```

là phù hợp.

---

# 7. Computed Property

## Có content?

```python
@property

def has_content(self):

    return bool(

        self["content"]

    )
```

---

## Content Length

```python
@property

def content_length(self):

    return len(

        self["content"]

    )
```

---

## Is Downloaded

```python
@property

def downloaded(self):

    return self.has_content
```

---

## Is Special Chapter

```python
@property

def is_special(self):

    return (

        int(self["chapter_no"])

        !=

        self["chapter_no"]

    )
```

Ví dụ

```text
10
```

↓

False

```text
10.5
```

↓

True

---

# 8. Business Method

## set_content()

```python
def set_content(

    self,

    text

):

    self["content"] = text.strip()
```

---

## clear_content()

```python
def clear_content(self):

    self["content"] = ""
```

---

## rename()

```python
def rename(

    self,

    title

):

    self["title"] = title.strip()
```

---

## move_to_story()

Ví dụ

Merge Database

```python
def move_to_story(

    self,

    story_id

):

    self["story_id"] = story_id
```

---

# 9. Factory

Crawler parse HTML

↓

```python
data = {

"title":"Chapter 15",

"url":"..."
}
```

↓

```python
@classmethod

def from_crawler(

    cls,

    data

):

    return cls(

        title=data["title"],

        url=data["url"],

        chapter_no=data["chapter_no"]

    )
```

---

# 10. Clone

```python
def clone(self):

    return Chapter(

        **self.to_dict()

    )
```

---

# 11. Preview

GUI

không cần đọc

100.000 ký tự

Ta thêm

```python
@property

def preview(self):

    return (

        self["content"][:200]

    )
```

---

# 12. Word Count

```python
@property

def word_count(self):

    return len(

        self["content"].split()

    )
```

---

# 13. Empty?

```python
@property

def is_empty(self):

    return (

        not self["content"]

    )
```

---

# 14. Kiểm thử

```python
chapter = Chapter(

title="Chapter 1",

chapter_no=1,

url="..."

)
```

↓

```python
print(

chapter.downloaded

)
```

↓

```text
False
```

---

```python
chapter.set_content(

"Hello Python"

)
```

↓

```python
print(

chapter.downloaded

)
```

↓

```text
True
```

---

```python
print(

chapter.word_count

)
```

↓

```text
2
```

---

# 15. Cải tiến thiết kế

Phiên bản hiện tại hoạt động tốt, nhưng để phục vụ crawler và reader lâu dài, chúng ta nên mở rộng.

---

## Bổ sung `crawl_status`

Không phải chương nào cũng đã được tải.

```python
from enum import Enum

class CrawlStatus(Enum):

    PENDING = "pending"

    SUCCESS = "success"

    FAILED = "failed"
```

Model có thể thêm trường:

```python
crawl_status
```

Điều này giúp crawler biết chương nào cần tải lại.

---

## Thêm checksum

Nhiều website chỉnh sửa nội dung.

Thêm:

```text
content_hash
```

Ví dụ SHA256.

Lần crawl sau:

```text
Hash cũ

↓

Hash mới

↓

Content thay đổi
```

↓

Cập nhật Database.

---

## Thêm encoding

Một số website:

```text
UTF-8

GBK

Shift-JIS
```

Có thể lưu:

```text
encoding
```

để hỗ trợ xử lý đặc biệt.

---

## Chuẩn bị cho Reader

Có thể thêm các trường:

```text
reading_time

character_count

line_count
```

được tính toán khi lưu nội dung.

---

# 16. Quan hệ với Story

Hiện tại chỉ có:

```python
story_id
```

Sau này Repository sẽ hỗ trợ:

```python
chapter.story
```

nhưng **Model không tự query Database**.

Ví dụ:

```python
chapter.story.title
```

sẽ do Repository gán sau khi tải dữ liệu.

Đây là cách giữ cho Model độc lập với tầng dữ liệu.

---

# Kiến trúc sau buổi 9

```text
BaseModel
      │
      ▼
Chapter
      │
      ├── Metadata
      ├── Validation
      ├── Business Methods
      ├── Computed Properties
      └── Factory
```

---

# Bài tập

## Bài 1

Hoàn thiện `ChapterModel` với:

* Metadata
* DEFAULTS
* Validation
* Factory
* Clone

---

## Bài 2

Viết các computed property:

* `downloaded`
* `has_content`
* `preview`
* `word_count`
* `content_length`
* `is_special`

---

## Bài 3

Viết các business method:

* `set_content()`
* `clear_content()`
* `rename()`
* `move_to_story()`

Kiểm tra sau mỗi thao tác:

```python
print(chapter.is_dirty())

print(chapter.dirty_fields())
```

để xác nhận cơ chế dirty tracking hoạt động đúng.

---

# Kết quả sau buổi 9

Bạn đã hoàn thành model quan trọng thứ hai của framework:

```text
BaseModel
    ├── Story
    └── Chapter
```

Đây là hai thực thể trung tâm của ứng dụng đọc truyện.

Đến thời điểm này:

* `Story` mô tả một bộ truyện.
* `Chapter` mô tả từng chương.
* Cả hai đều có metadata, validation, serialization và dirty tracking thống nhất.

---

# Chuẩn bị cho Buổi 10

Ở buổi tiếp theo, chúng ta sẽ xây dựng **AuthorModel** theo hướng **entity dùng chung**.

Khác với `Story` và `Chapter`, `Author` có nhiều điểm đặc biệt:

* Một tác giả có thể viết nhiều truyện (quan hệ 1-N).
* Có thể bổ sung các thông tin như tên khác (alias), tiểu sử, quốc gia.
* Hỗ trợ chuẩn hóa tên để tránh tạo nhiều bản ghi trùng lặp (ví dụ: `"Thiên Tằm Thổ Đậu"` và `" thiên tằm thổ đậu "`).

Buổi 10 cũng sẽ giới thiệu kỹ thuật **normalization** và **canonicalization** dữ liệu trước khi lưu vào cơ sở dữ liệu, rất hữu ích khi xây dựng crawler cho nhiều nguồn truyện.
