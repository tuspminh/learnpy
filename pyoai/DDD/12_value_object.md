# DDD Deep Dive — Buổi 12

# Value Object

Hôm nay chúng ta học một trong những khái niệm **quan trọng nhất của Tactical DDD**:

> **Value Object — Object được xác định bởi giá trị của nó, không phải identity.**

Nếu Buổi 11 chúng ta học:

```text
Entity
    ↓
"Đây là object nào?"
```

thì hôm nay:

```text
Value Object
    ↓
"Giá trị của nó là gì?"
```

---

# 1. Value Object là gì?

Value Object là một object:

* không có identity riêng trong domain
* được xác định hoàn toàn bởi value
* thường immutable
* có validation
* có behavior liên quan đến value
* có equality dựa trên value

Ví dụ hệ thống đọc truyện:

```text
StoryTitle
ChapterNumber
SourceUrl
```

---

# 2. Entity vs Value Object

So sánh:

```text
Entity
──────────────
Story #100
Story #200
```

Hai Story có thể có:

```text
title = "One Piece"
```

nhưng vẫn khác nhau vì identity khác.

---

Value Object:

```text
StoryTitle("One Piece")
StoryTitle("One Piece")
```

hai object này có cùng value.

Do đó:

```python
title_a == title_b
```

là:

```text
True
```

---

# 3. Identity vs Value

Đây là nền tảng.

## Entity

```text
Story(
    id=1,
    title="One Piece"
)
```

Identity:

```text
1
```

---

## Value Object

```text
StoryTitle("One Piece")
```

Không cần:

```text
StoryTitleId = 123
```

Bởi vì:

```text
"One Piece"
```

**chính là identity theo nghĩa value của object.**

---

# 4. Một ví dụ rất rõ

Giả sử:

```python
title_a = StoryTitle("One Piece")
title_b = StoryTitle("One Piece")
```

Có thể chúng nằm ở:

```text
memory address khác nhau
```

nhưng Domain nói:

```text
title_a == title_b
```

vì:

```text
value giống nhau
```

---

# 5. Value Object không quan tâm object nằm ở đâu

Ví dụ:

```python
title_a = StoryTitle("One Piece")
title_b = StoryTitle("One Piece")
```

Python:

```text
id(title_a) != id(title_b)
```

nhưng:

```text
title_a == title_b
```

Đây là:

```text
Object identity
    ≠
Domain identity
```

Value Object không cần domain identity.

---

# 6. Tại sao không dùng `str`?

Bạn có thể viết:

```python
class Story:
    title: str
```

Nhưng:

```python
story.title = ""
```

hoàn toàn hợp lệ về mặt Python.

Trong Domain:

```text
StoryTitle
```

có thể có rule:

```text
không rỗng
không quá 200 ký tự
trim whitespace
```

Khi đó `str` quá yếu để biểu diễn domain concept.

---

# 7. Primitive Obsession

Đây là vấn đề rất quan trọng trong DDD.

Ví dụ:

```python
def create_story(
    title: str,
    url: str,
    chapter_number: int,
):
    ...
```

Tất cả đều là primitive:

```text
str
str
int
```

Nhưng semantic hoàn toàn khác nhau:

```text
title
url
chapter_number
```

---

# 8. Primitive không thể hiện business meaning

Ví dụ:

```python
chapter_number = -10
```

Python hoàn toàn chấp nhận.

Nhưng Domain có thể nói:

```text
Chapter number phải > 0
```

Tương tự:

```python
url = "hello"
```

Python vẫn chấp nhận.

Nhưng Domain:

```text
SourceUrl phải là URL hợp lệ.
```

Value Object giải quyết vấn đề này.

---

# 9. `StoryTitle`

Ta tạo:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class StoryTitle:
    value: str
```

`frozen=True` khiến object immutable.

---

# 10. Validation

Nhưng code trên chưa đủ.

Ta cần:

```python
@dataclass(frozen=True)
class StoryTitle:
    value: str

    def __post_init__(self):
        value = self.value.strip()

        if not value:
            raise ValueError("Story title cannot be empty")

        if len(value) > 200:
            raise ValueError(
                "Story title cannot exceed 200 characters"
            )

        object.__setattr__(self, "value", value)
```

---

# 11. Tại sao dùng `object.__setattr__`?

Vì:

```python
@dataclass(frozen=True)
```

không cho:

```python
self.value = value
```

nên trong quá trình khởi tạo, nếu cần normalize:

```python
object.__setattr__(
    self,
    "value",
    value,
)
```

Sau khi khởi tạo:

```python
title.value = "Naruto"
```

sẽ bị từ chối.

---

# 12. Immutable là gì?

Immutable nghĩa là:

> Sau khi object được tạo, value không thể thay đổi.

Ví dụ:

```python
title = StoryTitle("One Piece")
```

Sau đó không được:

```python
title.value = "Naruto"
```

Thay vào đó tạo object mới:

```python
title = StoryTitle("Naruto")
```

---

# 13. Tại sao Value Object nên immutable?

Bởi vì nó đại diện cho một **giá trị**.

Ví dụ:

```text
Money(100, "USD")
```

Nếu object đang đại diện:

```text
100 USD
```

rồi đột nhiên bên trong nó biến thành:

```text
500 USD
```

thì các object đang tham chiếu tới nó rất khó đoán.

Immutable làm behavior dễ hiểu hơn.

---

# 14. Value Object có equality theo value

Với:

```python
@dataclass(frozen=True)
class StoryTitle:
    value: str
```

Python tự tạo equality:

```python
a = StoryTitle("One Piece")
b = StoryTitle("One Piece")
```

kết quả:

```python
a == b
```

là:

```text
True
```

---

# 15. Đây chính là điểm khác Entity

Entity:

```text
Story(id=1, title="One Piece")
Story(id=2, title="One Piece")
```

khác nhau.

Value Object:

```text
StoryTitle("One Piece")
StoryTitle("One Piece")
```

giống nhau.

---

# 16. `ChapterNumber`

Bây giờ chúng ta tạo Value Object thứ hai:

```python
@dataclass(frozen=True)
class ChapterNumber:
    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError(
                "Chapter number must be positive"
            )
```

Sử dụng:

```python
number = ChapterNumber(10)
```

---

# 17. Không thể tạo invalid state

```python
ChapterNumber(-1)
```

→ lỗi.

```python
ChapterNumber(0)
```

→ lỗi.

Như vậy mọi object hợp lệ đều đảm bảo:

```text
ChapterNumber.value > 0
```

Đây là một ý tưởng cực kỳ quan trọng:

> **Value Object bảo vệ invariant của chính value mà nó đại diện.**

---

# 18. Semantic Type

So sánh:

```python
chapter_number: int
```

với:

```python
chapter_number: ChapterNumber
```

Cái thứ hai nói rõ hơn rất nhiều:

```text
ChapterNumber
```

không phải:

```text
PageNumber
```

không phải:

```text
UserId
```

không phải:

```text
Price
```

Mặc dù tất cả có thể là `int`.

---

# 19. Đây là "semantic type"

Ví dụ:

```python
user_id: UserId
story_id: StoryId
chapter_number: ChapterNumber
page_number: PageNumber
```

thay vì:

```python
user_id: int
story_id: int
chapter_number: int
page_number: int
```

Python type system lúc này giúp code diễn đạt Domain tốt hơn.

---

# 20. `SourceUrl`

Đây là Value Object rất phù hợp.

Thay vì:

```python
source_url: str
```

ta có:

```python
@dataclass(frozen=True)
class SourceUrl:
    value: str
```

và validate.

---

# 21. Validation URL

Có thể bắt đầu đơn giản:

```python
from urllib.parse import urlparse


@dataclass(frozen=True)
class SourceUrl:
    value: str

    def __post_init__(self):
        value = self.value.strip()

        parsed = urlparse(value)

        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Invalid URL scheme")

        if not parsed.netloc:
            raise ValueError("Invalid URL")

        object.__setattr__(self, "value", value)
```

---

# 22. Bây giờ Domain model trở nên rõ hơn

Thay vì:

```python
@dataclass
class Story:
    id: int
    title: str
    source_url: str
```

ta có:

```python
@dataclass
class Story:
    id: StoryId
    title: StoryTitle
    source_url: SourceUrl
```

Nhìn type là hiểu Domain.

---

# 23. Value Object có behavior

Đừng nghĩ Value Object chỉ là:

```text
wrapper quanh primitive
```

Nó có thể có behavior.

Ví dụ `ChapterNumber`:

```python
@dataclass(frozen=True)
class ChapterNumber:
    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError()

    def next(self) -> "ChapterNumber":
        return ChapterNumber(self.value + 1)
```

---

# 24. Hoặc comparison

```python
@dataclass(frozen=True)
class ChapterNumber:
    value: int

    def is_after(self, other: "ChapterNumber") -> bool:
        return self.value > other.value
```

Sử dụng:

```python
a = ChapterNumber(10)
b = ChapterNumber(5)

a.is_after(b)
```

→ `True`.

Behavior này thuộc về `ChapterNumber`, không cần đẩy ra ngoài.

---

# 25. Value Object và normalization

Ví dụ:

```python
StoryTitle("   One Piece   ")
```

Có thể normalize thành:

```text
"One Piece"
```

Ngay trong constructor:

```python
value = self.value.strip()
```

Như vậy:

```python
a = StoryTitle("One Piece")
b = StoryTitle("  One Piece  ")
```

có thể trở thành:

```python
a == b
```

→ `True`.

---

# 26. Canonical representation

Một Value Object tốt có thể có:

> **canonical representation**

Ví dụ URL:

```text
HTTPS://EXAMPLE.COM/
```

có thể normalize thành một representation chuẩn tùy domain.

Ví dụ đơn giản:

```text
https://example.com/
```

Mục tiêu:

```text
nhiều input
   ↓
normalize
   ↓
một representation chuẩn
```

Điều này sẽ đặc biệt quan trọng ở Buổi 13.

---

# 27. Value Object không có lifecycle

Entity:

```text
Story #1
draft
 ↓
published
 ↓
archived
```

Value Object:

```text
StoryTitle("One Piece")
```

Không có lifecycle kiểu:

```text
StoryTitle #1
 ↓
StoryTitle #2
```

Nếu title thay đổi:

```python
story.rename("Naruto")
```

ta tạo một value mới:

```text
StoryTitle("Naruto")
```

---

# 28. Entity chứa Value Object

Đây là kiến trúc chúng ta muốn:

```text
Story
│
├── StoryId
├── StoryTitle
├── SourceId
└── Status
```

Entity:

```python
@dataclass
class Story:
    id: StoryId
    title: StoryTitle
    source_id: SourceId
    status: StoryStatus
```

Value Objects:

```text
StoryId
StoryTitle
SourceId
StoryStatus
```

---

# 29. Tại sao `status` cũng có thể là Value Object?

Nếu:

```python
status: str
```

thì:

```python
story.status = "abc"
```

vẫn được.

Tốt hơn:

```python
class StoryStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    COMPLETED = "completed"
    ARCHIVED = "archived"
```

Enum có thể đóng vai trò semantic type.

Tùy domain, status có thể được model bằng Enum hoặc Value Object.

---

# 30. Value Object và Enum không hoàn toàn giống nhau

Enum phù hợp khi:

```text
tập giá trị hữu hạn
```

Ví dụ:

```text
DRAFT
PUBLISHED
COMPLETED
ARCHIVED
```

Value Object phù hợp khi:

```text
value có validation
behavior
normalization
```

Ví dụ:

```text
StoryTitle
SourceUrl
Money
EmailAddress
ChapterNumber
```

---

# 31. Value Object nên nằm ở đâu?

Ví dụ:

```text
catalog/
└── domain/
    └── value_objects/
        ├── story_id.py
        ├── story_title.py
        ├── source_id.py
        ├── source_url.py
        └── chapter_number.py
```

Đây là nơi hợp lý.

Không đặt:

```text
infrastructure/
└── value_objects/
```

nếu đó là Domain concept.

---

# 32. Không để Value Object phụ thuộc Infrastructure

Không nên:

```python
from sqlalchemy import String
```

trong:

```text
StoryTitle
```

Không nên:

```python
import requests
```

trong:

```text
SourceUrl
```

Domain phải độc lập.

---

# 33. Value Object và serialization

Giả sử:

```python
title = StoryTitle("One Piece")
```

Khi API cần JSON:

```python
{
    "title": title.value
}
```

hoặc dùng mapper:

```python
def to_response(story: Story) -> StoryResponse:
    return StoryResponse(
        id=story.id.value,
        title=story.title.value,
    )
```

Domain không cần biết JSON.

---

# 34. Value Object và Database

Database:

```text
story_id INTEGER
title TEXT
chapter_number INTEGER
source_url TEXT
```

Domain:

```text
StoryId
StoryTitle
ChapterNumber
SourceUrl
```

Infrastructure mapping:

```text
INTEGER ↔ StoryId
TEXT    ↔ StoryTitle
INTEGER ↔ ChapterNumber
TEXT    ↔ SourceUrl
```

Đây chính là lý do chúng ta đã học:

> Entity ≠ Database Row.

Và hôm nay:

> Value Object ≠ Primitive.

---

# 35. Một ví dụ hoàn chỉnh

```python
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class StoryTitle:
    value: str

    def __post_init__(self):
        value = self.value.strip()

        if not value:
            raise ValueError("Title cannot be empty")

        if len(value) > 200:
            raise ValueError(
                "Title cannot exceed 200 characters"
            )

        object.__setattr__(self, "value", value)


@dataclass(frozen=True)
class ChapterNumber:
    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError(
                "Chapter number must be positive"
            )


@dataclass(frozen=True)
class SourceUrl:
    value: str

    def __post_init__(self):
        value = self.value.strip()
        parsed = urlparse(value)

        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Invalid URL scheme")

        if not parsed.netloc:
            raise ValueError("Invalid URL")

        object.__setattr__(self, "value", value)
```

---

# 36. Test Value Object

Đây là nơi Value Object cực kỳ dễ test.

## StoryTitle

```python
def test_story_title():
    title = StoryTitle("  One Piece  ")

    assert title.value == "One Piece"
```

---

## Equality

```python
def test_story_title_equality():
    a = StoryTitle("One Piece")
    b = StoryTitle("One Piece")

    assert a == b
```

---

## Invalid

```python
def test_empty_title():
    with pytest.raises(ValueError):
        StoryTitle("")
```

---

# 37. Immutability test

```python
def test_story_title_is_immutable():
    title = StoryTitle("One Piece")

    with pytest.raises(FrozenInstanceError):
        title.value = "Naruto"
```

Đây là behavior quan trọng của Value Object.

---

# 38. Một lỗi thiết kế phổ biến

Đừng làm:

```python
@dataclass(frozen=True)
class StoryTitle:
    value: str
```

rồi mọi nơi đều:

```python
StoryTitle(...)
```

nhưng không validation.

Khi đó bạn chỉ tạo:

```text
wrapper quanh string
```

chứ chưa thực sự model domain.

Value Object nên có:

```text
Value
+
Constraint
+
Meaning
+
Behavior (khi cần)
```

---

# 39. Một lỗi khác: Value Object quá thông minh

Ngược lại, không nên biến:

```text
StoryTitle
```

thành một "God Object":

```python
class StoryTitle:
    def validate(...)
    def save(...)
    def send_email(...)
    def fetch_story(...)
    def notify(...)
```

Value Object chỉ nên chứa behavior liên quan trực tiếp tới chính value đó.

---

# 40. Value Object và primitive conversion

Đôi khi cần:

```python
str(title)
```

Ta có thể:

```python
def __str__(self) -> str:
    return self.value
```

Ví dụ:

```python
title = StoryTitle("One Piece")

print(title)
```

→

```text
One Piece
```

---

# 41. `repr`

Dataclass đã hỗ trợ:

```python
StoryTitle(value='One Piece')
```

rất hữu ích khi debug.

---

# 42. Value Object có nên dùng inheritance?

Thông thường:

```text
Không cần.
```

Không nên tạo:

```text
BaseValueObject
     ↓
StoryTitle
ChapterNumber
SourceUrl
```

chỉ để chứng minh rằng mình đang dùng DDD.

Python có `dataclass(frozen=True)` rất phù hợp cho nhiều Value Object.

---

# 43. Value Object và Type Safety

Ví dụ:

```python
def load_chapter(
    story_id: StoryId,
    chapter_number: ChapterNumber,
):
    ...
```

Nhìn signature đã hiểu domain.

Trong khi:

```python
def load_chapter(
    story_id: int,
    chapter_number: int,
):
    ...
```

không biết:

```text
int nào là gì?
```

Semantic types làm code **tự mô tả**.

---

# 44. Một ví dụ bug kinh điển

```python
def load_chapter(
    story_id: int,
    chapter_number: int,
):
    ...
```

Ai đó có thể gọi:

```python
load_chapter(
    story_id=10,
    chapter_number=100,
)
```

vẫn hợp lệ.

Nhưng nếu nhầm:

```python
load_chapter(
    story_id=100,
    chapter_number=10,
)
```

Python không biết.

Với semantic types:

```python
def load_chapter(
    story_id: StoryId,
    chapter_number: ChapterNumber,
):
```

ý nghĩa rõ ràng hơn nhiều.

---

# 45. Value Object và "Make Illegal States Unrepresentable"

Đây là một tư tưởng rất mạnh.

Thay vì:

```python
chapter_number: int
```

cho phép:

```text
-10
0
1
2
3
```

Ta dùng:

```python
ChapterNumber
```

chỉ cho phép:

```text
1
2
3
...
```

Tức là:

> **Thiết kế type để trạng thái invalid khó hoặc không thể biểu diễn.**

---

# 46. Entity + Value Object

Bây giờ ghép hai buổi:

```text
Entity
│
│ identity
│
└── Story
     │
     ├── StoryId
     ├── StoryTitle
     ├── SourceId
     └── Status
```

Trong đó:

```text
Story
```

là Entity.

```text
StoryId
StoryTitle
SourceId
```

là Value Objects.

---

# 47. Mental Model

Hãy ghi nhớ:

```text
Entity
──────────────────────
Who is this?
↓
Identity
↓
Lifecycle
↓
Mutable state
↓
Behavior
```

Value Object:

```text
Value Object
──────────────────────
What is this value?
↓
Value
↓
Immutable
↓
Validation
↓
Equality by value
```

---

# 48. So sánh tổng hợp

| Đặc điểm          | Entity        | Value Object     |
| ----------------- | ------------- | ---------------- |
| Identity          | Có            | Không            |
| Equality          | Identity      | Value            |
| Mutable           | Thường có thể | Thường immutable |
| Lifecycle         | Có            | Không            |
| Business behavior | Có            | Có thể có        |
| Validation        | Có            | Có               |
| Ví dụ             | Story         | StoryTitle       |
| Ví dụ             | Chapter       | ChapterNumber    |
| Ví dụ             | User          | SourceUrl        |

---

# 49. Trong hệ thống đọc truyện

Ta có thể thiết kế:

```text
Story
├── StoryId
├── StoryTitle
├── SourceId
└── StoryStatus
```

và:

```text
Chapter
├── ChapterId
├── ChapterNumber
├── ChapterTitle
└── ChapterContent
```

Chú ý:

```text
ChapterTitle
ChapterContent
```

có thể trở thành Value Object nếu domain có rule riêng.

Không phải mọi `str` đều bắt buộc phải biến thành Value Object.

---

# 50. Quy tắc thực tế

Không nên:

```text
str → Value Object
int → Value Object
```

một cách máy móc.

Hãy hỏi:

> Primitive này có **business meaning hoặc business constraint** riêng không?

Nếu có:

```text
→ Value Object
```

Nếu không:

```text
→ primitive có thể đủ.
```

---

# 51. Ví dụ quyết định

### `StoryTitle`

```text
Có meaning
Có validation
Có normalization
→ Value Object
```

### `ChapterNumber`

```text
Có meaning
Có constraint > 0
→ Value Object
```

### `SourceUrl`

```text
Có meaning
Có validation
→ Value Object
```

### `description`

Nếu chỉ:

```text
free-form text
```

và không có rule:

```text
→ str có thể đủ.
```

---

# 52. Bài tập Buổi 12

## Bài 1 — Tạo `StoryTitle`

Yêu cầu:

```text
StoryTitle
├── immutable
├── trim whitespace
├── không rỗng
├── tối đa 200 ký tự
└── equality theo value
```

---

## Bài 2 — Tạo `ChapterNumber`

Yêu cầu:

```text
ChapterNumber
├── immutable
├── integer
├── > 0
└── có method next()
```

Ví dụ:

```python
number = ChapterNumber(10)

next_number = number.next()

assert next_number.value == 11
assert number.value == 10
```

---

## Bài 3 — Tạo `SourceUrl`

Yêu cầu:

```text
SourceUrl
├── immutable
├── strip whitespace
├── chỉ http/https
└── phải có host
```

---

# 53. Bài tập quan trọng nhất

Refactor Entity của Buổi 11:

Từ:

```python
@dataclass
class Story:
    id: int
    title: str
    source_id: int
    status: str
```

thành:

```text
Story
├── StoryId
├── StoryTitle
├── SourceId
└── StoryStatus
```

Mục tiêu:

```text
Primitive
   ↓
Semantic Type
   ↓
Domain Model
```

---

# 54. Chuỗi kiến thức cần nhớ

Buổi 11:

```text
Entity
    ↓
Identity
```

Buổi 12:

```text
Value Object
    ↓
Value
    ↓
Immutable
    ↓
Validation
```

Buổi 13 chúng ta sẽ đi sâu hơn:

```text
Composite Value Object
Normalization
Canonical Representation
Factory
Invalid State
Python implementation
```

Đặc biệt, chúng ta sẽ giải quyết câu hỏi rất quan trọng:

> **Khi nào một Value Object nên được tạo từ nhiều field, và làm sao đảm bảo mọi instance luôn ở trạng thái canonical và hợp lệ?**
