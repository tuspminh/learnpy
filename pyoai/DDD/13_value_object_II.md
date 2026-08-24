# DDD Deep Dive — Buổi 13

# Value Object nâng cao

Ở Buổi 12, chúng ta đã hiểu:

```text
Value Object
├── Không có identity
├── Equality theo value
├── Immutable
├── Validation
└── Semantic Type
```

Hôm nay chúng ta đi sâu hơn vào cách **thiết kế Value Object thực sự tốt trong Python**:

```text
Buổi 13
├── Composite Value Object
├── Normalization
├── Canonical Representation
├── Factory
├── Invalid State
└── Python Implementation
```

---

# 1. Composite Value Object là gì?

Value Object không nhất thiết chỉ chứa **một primitive**.

Ví dụ:

```python
Money(
    amount=100,
    currency="USD",
)
```

Đây là một Value Object có **nhiều thành phần**:

```text
Money
├── amount
└── currency
```

Ta gọi đây là:

> **Composite Value Object**

---

# 2. Ví dụ `Money`

Nếu dùng primitive:

```python
amount: float
currency: str
```

thì có thể xảy ra:

```python
amount = -100
currency = "ABC"
```

Python không phản đối.

Nhưng Domain có thể yêu cầu:

```text
amount >= 0
currency phải hợp lệ
```

Do đó:

```python
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str
```

---

# 3. Composite Value Object trong hệ thống đọc truyện

Ví dụ `Source` có:

```text
scheme
host
path
```

Thay vì:

```python
scheme: str
host: str
path: str
```

ta có thể model:

```text
SourceUrl
├── scheme
├── host
└── path
```

Nhưng ở cấp Domain:

```python
SourceUrl("https://example.com/story/one-piece")
```

vẫn chỉ là **một giá trị**.

---

# 4. Một ví dụ khác: `DateRange`

```python
DateRange(
    start=date(...),
    end=date(...),
)
```

Đây là Value Object vì:

```text
DateRange(A, B)
```

được xác định bởi:

```text start + end
```

không cần identity.

---

# 5. Composite Value Object có invariant riêng

Ví dụ:

```python
@dataclass(frozen=True)
class DateRange:
    start: date
    end: date

    def __post_init__(self):
        if self.end < self.start:
            raise ValueError(
                "End date cannot be before start date"
            )
```

Invariant:

```text
start <= end
```

---

# 6. Điều quan trọng

Value Object không chỉ là:

```text
wrapper around primitive
```

Nó có thể là:

```text
Value Object
    ↓
nhiều values
    ↓
business meaning
    ↓
invariant
    ↓
behavior
```

---

# 7. Composite Value Object vs Entity

Ví dụ:

```text
Address
├── street
├── city
└── postal_code
```

có thể là Value Object.

Hai Address:

```text
Address(
    "123 ABC",
    "HCM",
    "700000"
)

Address(
    "123 ABC",
    "HCM",
    "700000"
)
```

được xem là bằng nhau nếu toàn bộ value giống nhau.

Không cần:

```text
AddressId
```

---

# 8. Normalization là gì?

Normalization nghĩa là:

> Chuyển nhiều cách biểu diễn của cùng một giá trị về một dạng chuẩn.

Ví dụ:

```text
" One Piece "
"One Piece"
"  One Piece  "
```

có thể normalize thành:

```text
"One Piece"
```

---

# 9. Normalization của `StoryTitle`

```python
@dataclass(frozen=True)
class StoryTitle:
    value: str

    def __post_init__(self):
        value = self.value.strip()

        if not value:
            raise ValueError("Title cannot be empty")

        object.__setattr__(self, "value", value)
```

Bây giờ:

```python
a = StoryTitle(" One Piece ")
b = StoryTitle("One Piece")
```

ta có:

```python
a == b
```

→ `True`.

---

# 10. Normalization không phải Validation

Đây là hai khái niệm khác nhau.

### Validation

Hỏi:

> Value này có hợp lệ không?

Ví dụ:

```text
""
```

→ invalid.

### Normalization

Hỏi:

> Value này có thể được chuyển thành representation chuẩn nào?

Ví dụ:

```text
"   One Piece   "
```

→

```text
"One Piece"
```

---

# 11. Thứ tự rất quan trọng

Thông thường:

```text
Raw Input
   ↓
Normalize
   ↓
Validate
   ↓
Canonical Value
```

Ví dụ:

```python
value = self.value.strip()

if not value:
    raise ValueError(...)
```

Không nên validation trước khi normalization nếu normalization có thể biến input thành dạng hợp lệ.

---

# 12. Canonical Representation

Canonical representation là:

> **Một cách biểu diễn chuẩn duy nhất cho một giá trị Domain.**

Ví dụ:

```text
" one piece "
"One Piece"
```

có thể canonicalize thành:

```text
"One Piece"
```

---

# 13. Vì sao canonical representation quan trọng?

Giả sử:

```python
a = StoryTitle("One Piece")
b = StoryTitle(" One Piece ")
```

Nếu không normalize:

```text
a != b
```

Mặc dù business có thể coi chúng là cùng một title.

Canonical representation giúp:

```text
Equivalent input
       ↓
Canonical value
       ↓
Equality đơn giản
```

---

# 14. Ví dụ URL

Giả sử:

```text
HTTPS://EXAMPLE.COM/story
https://example.com/story
```

Domain có thể muốn coi chúng tương đương.

Ta có thể canonicalize:

```text
https://example.com/story
```

Nhưng cần rất cẩn thận:

> **Không được normalization vượt quá business semantics.**

Không phải mọi URL khác nhau đều tương đương.

---

# 15. Đừng normalize mù quáng

Ví dụ:

```python
value.lower()
```

với mọi string là nguy hiểm.

Với title:

```text
"One Piece"
```

chuyển thành:

```text
"one piece"
```

có thể làm mất formatting mà Domain muốn giữ.

Do đó normalization phải xuất phát từ:

```text
Business meaning
```

chứ không phải:

```text
"Code cho đẹp"
```

---

# 16. Canonicalization của `SourceUrl`

Có thể tạo:

```python
from urllib.parse import urlparse, urlunparse


@dataclass(frozen=True)
class SourceUrl:
    value: str

    def __post_init__(self):
        value = self._normalize(self.value)
        self._validate(value)

        object.__setattr__(self, "value", value)

    @staticmethod
    def _normalize(value: str) -> str:
        return value.strip()
```

Đây là cấu trúc tốt hơn vì:

```text
__post_init__
├── normalize
└── validate
```

---

# 17. Tách normalization và validation

Một implementation rõ ràng:

```python
@dataclass(frozen=True)
class StoryTitle:
    value: str

    def __post_init__(self):
        value = self.normalize(self.value)
        self.validate(value)

        object.__setattr__(self, "value", value)

    @staticmethod
    def normalize(value: str) -> str:
        return value.strip()

    @staticmethod
    def validate(value: str) -> None:
        if not value:
            raise ValueError("Title cannot be empty")

        if len(value) > 200:
            raise ValueError(
                "Title cannot exceed 200 characters"
            )
```

Cấu trúc này rất dễ test.

---

# 18. Factory là gì?

Factory là nơi chịu trách nhiệm:

> **Tạo ra một Domain Object hợp lệ.**

Ví dụ:

```python
StoryTitle.create(" One Piece ")
```

thay vì:

```python
StoryTitle(" One Piece ")
```

---

# 19. Factory method

Python hỗ trợ rất tốt:

```python
@classmethod
def create(cls, value: str):
    ...
```

Ví dụ:

```python
@dataclass(frozen=True)
class StoryTitle:
    value: str

    @classmethod
    def create(cls, value: str) -> "StoryTitle":
        value = value.strip()

        if not value:
            raise ValueError(
                "Title cannot be empty"
            )

        return cls(value)
```

---

# 20. Tại sao cần Factory nếu constructor đã đủ?

Không phải lúc nào cũng cần.

Nếu:

```python
StoryTitle("One Piece")
```

đã rõ ràng và đảm bảo invariant thì constructor là đủ.

Factory trở nên hữu ích khi:

```text
có nhiều cách tạo object
```

hoặc:

```text
creation logic phức tạp
```

---

# 21. Ví dụ nhiều factory

```python
class SourceUrl:
    ...

    @classmethod
    def from_string(cls, value: str):
        ...

    @classmethod
    def from_parts(
        cls,
        scheme: str,
        host: str,
        path: str,
    ):
        ...
```

Hai cách:

```python
SourceUrl.from_string(...)
```

và:

```python
SourceUrl.from_parts(...)
```

đều tạo ra:

```text
SourceUrl
```

---

# 22. Factory không nhất thiết là Factory Pattern lớn

Trong DDD, khi nói:

```python
StoryTitle.create(...)
```

không nhất thiết phải tạo:

```text
StoryTitleFactory
```

riêng.

Có thể chỉ cần:

```python
@classmethod
def create(...)
```

Đây là:

> **Factory Method**

và thường là đủ.

---

# 23. Khi nào nên dùng Factory riêng?

Ví dụ creation cần:

```text
nhiều dependencies
external service
configuration
complex algorithm
```

thì có thể tạo:

```text
StoryFactory
```

Ví dụ:

```python
story = story_factory.create(...)
```

Nhưng đừng tạo Factory chỉ vì:

> "DDD nói phải có Factory."

---

# 24. Invalid State

Một nguyên tắc cực kỳ quan trọng:

> **Value Object không được tồn tại ở trạng thái invalid.**

Sai:

```python
title = StoryTitle("")
```

rồi:

```python
if not title.value:
    ...
```

Mỗi nơi lại phải kiểm tra.

---

# 25. Thiết kế tốt

```python
title = StoryTitle("")
```

→ ngay lập tức:

```text
ValueError
```

Sau khi có:

```python
title: StoryTitle
```

ta có thể tin:

```text
title hợp lệ
```

Đây là:

> **Make illegal states unrepresentable.**

---

# 26. Ví dụ sai

```python
@dataclass
class StoryTitle:
    value: str
```

Sau đó:

```python
title = StoryTitle("")
```

Object vẫn tồn tại.

Đây là:

```text
Invalid state
```

được phép tồn tại.

---

# 27. Ví dụ tốt

```python
@dataclass(frozen=True)
class StoryTitle:
    value: str

    def __post_init__(self):
        value = self.value.strip()

        if not value:
            raise ValueError(
                "Story title cannot be empty"
            )

        object.__setattr__(
            self,
            "value",
            value,
        )
```

Bây giờ:

```python
StoryTitle("")
```

không tạo được object.

---

# 28. Boundary của Value Object

Một câu hỏi rất hay:

> Validation nên nằm ở đâu?

Ví dụ:

```text
UI
Application
Domain
Database
```

Có thể validation ở nhiều layer.

Nhưng **business invariant của Value Object phải được bảo vệ ở Domain**.

Ví dụ UI:

```python
if not title:
    show_error()
```

rất tốt cho UX.

Nhưng Domain vẫn phải:

```python
StoryTitle(title)
```

và tự validate.

---

# 29. Defense in depth

Ta có thể có:

```text
UI
 ↓
basic validation
 ↓
Application
 ↓
Domain
 ↓
Value Object validation
 ↓
Infrastructure
 ↓
Database constraints
```

Nhưng:

> Database validation không thay thế Domain validation.

---

# 30. Composite Value Object nâng cao

Ví dụ `SourceUrl`:

```python
@dataclass(frozen=True)
class SourceUrl:
    scheme: str
    host: str
    path: str
```

Invariant:

```text
scheme ∈ {"http", "https"}
host != ""
path bắt đầu bằng "/"
```

Đây là một Composite Value Object thực sự.

---

# 31. Canonical representation của Composite Value Object

Ta có:

```python
url = SourceUrl(
    scheme="https",
    host="example.com",
    path="/story",
)
```

Có thể expose:

```python
@property
def value(self) -> str:
    return f"{self.scheme}://{self.host}{self.path}"
```

Kết quả:

```text
https://example.com/story
```

---

# 32. Nhưng có nên lưu cả `value` và parts?

Thường không nên lưu duplicate state:

```python
@dataclass
class SourceUrl:
    value: str
    scheme: str
    host: str
```

Có nguy cơ:

```text
value không khớp scheme/host
```

Ví dụ:

```text
value = https://example.com
scheme = http
```

Đây là invalid state.

---

# 33. Một nguồn sự thật duy nhất

Thiết kế tốt:

```text
SourceUrl
├── scheme
├── host
└── path
```

và:

```python
@property
def value(self):
    ...
```

`value` được **derive** từ state.

Hoặc ngược lại:

```text
SourceUrl
└── canonical string
```

và parse khi cần.

Nhưng tránh lưu duplicate representation nếu không cần.

---

# 34. Example Composite Value Object

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class SourceUrl:
    scheme: str
    host: str
    path: str = "/"

    def __post_init__(self):
        scheme = self.scheme.lower().strip()
        host = self.host.lower().strip()
        path = self.path.strip()

        if scheme not in {"http", "https"}:
            raise ValueError("Invalid scheme")

        if not host:
            raise ValueError("Host cannot be empty")

        if not path.startswith("/"):
            path = "/" + path

        object.__setattr__(self, "scheme", scheme)
        object.__setattr__(self, "host", host)
        object.__setattr__(self, "path", path)

    @property
    def value(self) -> str:
        return f"{self.scheme}://{self.host}{self.path}"
```

---

# 35. Canonicalization

```python
a = SourceUrl(
    scheme="HTTPS",
    host="EXAMPLE.COM",
    path="story",
)
```

Canonical state:

```text
scheme = https
host   = example.com
path   = /story
```

và:

```python
a.value
```

→

```text
https://example.com/story
```

---

# 36. Equality

Vì:

```python
@dataclass(frozen=True)
```

equality dựa trên:

```text
scheme
host
path
```

Ví dụ:

```python
a = SourceUrl(
    "HTTPS",
    "EXAMPLE.COM",
    "story",
)

b = SourceUrl(
    "https",
    "example.com",
    "/story",
)
```

Sau normalization:

```python
a == b
```

→ `True`.

---

# 37. Đây chính là sức mạnh của Value Object

Input:

```text
HTTPS://EXAMPLE.COM/story
https://example.com/story
https://EXAMPLE.COM/story
```

↓

```text
Normalization
```

↓

```text
Canonical Representation
```

↓

```text
Equality by Value
```

---

# 38. Value Object và domain language

Thay vì:

```python
def crawl(url: str):
    ...
```

ta có:

```python
def crawl(url: SourceUrl):
    ...
```

Code nói rõ:

> Crawler nhận một **SourceUrl hợp lệ**, không phải một chuỗi tùy ý.

Đây chính là sức mạnh của DDD.

---

# 39. Một Value Object không nhất thiết phải có class riêng

Đây là điểm cân bằng.

Nếu:

```python
description: str
```

không có:

* validation
* behavior
* business meaning đặc biệt

thì giữ `str` có thể tốt hơn.

Không nên tạo:

```python
DescriptionText
StoryDescriptionText
NovelDescriptionValue
```

chỉ để code "trông giống DDD".

---

# 40. Rule thực tế

Hãy tạo Value Object khi primitive có ít nhất một trong các đặc điểm:

```text
1. Business meaning rõ ràng
2. Validation riêng
3. Normalization riêng
4. Behavior riêng
5. Equality semantics riêng
6. Được sử dụng ở nhiều nơi
```

Ví dụ:

```text
EmailAddress
Money
Currency
PhoneNumber
StoryTitle
ChapterNumber
SourceUrl
```

rất phù hợp.

---

# 41. Value Object và `Optional`

Nếu domain cho phép:

```text
title có thể null
```

đừng tạo:

```python
StoryTitle(None)
```

nếu `None` không phải value hợp lệ.

Thay vào đó:

```python
title: StoryTitle | None
```

Điều này phân biệt:

```text
Không có title
```

với:

```text
Có title nhưng invalid
```

---

# 42. Value Object không nên nuốt lỗi

Sai:

```python
try:
    ...
except ValueError:
    return None
```

Điều này làm:

```text
invalid input
```

trở thành:

```text
không rõ chuyện gì xảy ra
```

Domain nên fail rõ ràng:

```python
raise InvalidStoryTitle(...)
```

Sau này chúng ta sẽ thiết kế **Domain Exception** tốt hơn.

---

# 43. Custom Exception

Thay vì:

```python
raise ValueError(...)
```

có thể:

```python
class InvalidStoryTitle(ValueError):
    pass
```

sau đó:

```python
raise InvalidStoryTitle(
    "Story title cannot be empty"
)
```

Điều này làm exception có semantic rõ hơn.

---

# 44. Full `StoryTitle` implementation

```python
from dataclasses import dataclass


class InvalidStoryTitle(ValueError):
    pass


@dataclass(frozen=True)
class StoryTitle:
    value: str

    def __post_init__(self):
        value = self.normalize(self.value)
        self.validate(value)

        object.__setattr__(
            self,
            "value",
            value,
        )

    @staticmethod
    def normalize(value: str) -> str:
        return value.strip()

    @staticmethod
    def validate(value: str) -> None:
        if not value:
            raise InvalidStoryTitle(
                "Story title cannot be empty"
            )

        if len(value) > 200:
            raise InvalidStoryTitle(
                "Story title is too long"
            )

    def __str__(self) -> str:
        return self.value
```

---

# 45. Full `ChapterNumber`

```python
from dataclasses import dataclass


class InvalidChapterNumber(ValueError):
    pass


@dataclass(frozen=True)
class ChapterNumber:
    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise InvalidChapterNumber(
                "Chapter number must be positive"
            )

    def next(self) -> "ChapterNumber":
        return ChapterNumber(self.value + 1)

    def previous(self) -> "ChapterNumber":
        if self.value == 1:
            raise InvalidChapterNumber(
                "Chapter number cannot be less than 1"
            )

        return ChapterNumber(self.value - 1)
```

---

# 46. Một điểm rất quan trọng: Value Object có thể tạo object mới

Vì immutable:

```python
number = ChapterNumber(10)
```

Không làm:

```python
number.value += 1
```

Thay vào đó:

```python
new_number = number.next()
```

Ta có:

```text
number
  ↓
ChapterNumber(10)

new_number
  ↓
ChapterNumber(11)
```

Object cũ không thay đổi.

---

# 47. Value Object có thể dùng trong Entity

```python
@dataclass(eq=False)
class Story:
    id: StoryId
    title: StoryTitle
```

Rename:

```python
def rename(self, title: StoryTitle):
    self.title = title
```

hoặc:

```python
def rename(self, title: str):
    self.title = StoryTitle(title)
```

Cách thứ hai tiện ở boundary, nhưng cách thứ nhất giữ Domain API "typed" hơn.

---

# 48. Một nguyên tắc thiết kế rất hay

Ở **Domain boundary**:

```text
Primitive
   ↓
Value Object
```

Sau khi vào Domain:

```text
Value Object
   ↓
Business logic
```

Ở boundary ra ngoài:

```text
Value Object
   ↓
Primitive / DTO
```

Ví dụ:

```text
HTTP JSON
    ↓
str
    ↓
StoryTitle
    ↓
Entity
    ↓
StoryResponse
    ↓
str
    ↓
JSON
```

---

# 49. Tổng kết Buổi 13

Bạn cần nắm chắc 6 ý.

### ① Composite Value Object

Value Object có thể chứa nhiều value:

```text
Money
├── amount
└── currency
```

---

### ② Normalization

```text
Raw Input
   ↓
Normalize
```

Ví dụ:

```text
"  One Piece  "
       ↓
"One Piece"
```

---

### ③ Canonical Representation

Một value hợp lệ nên có representation chuẩn để equality đáng tin cậy.

---

### ④ Factory

Dùng khi creation có logic:

```python
StoryTitle.create(...)
SourceUrl.from_string(...)
```

Nhưng không tạo Factory chỉ vì "DDD".

---

### ⑤ Invalid State

Value Object không nên cho phép:

```text
invalid object
```

tồn tại.

Thay vào đó:

```text
Input
 ↓
Normalize
 ↓
Validate
 ↓
Valid Value Object
```

---

### ⑥ Value Object là semantic type

Thay vì:

```python
title: str
chapter: int
url: str
```

ta có:

```python
title: StoryTitle
chapter: ChapterNumber
url: SourceUrl
```

Code trở nên **giàu ngữ nghĩa Domain hơn**.

---

# 50. Bài tập Buổi 13

Hãy tự implement 3 Value Object sau:

### `StoryTitle`

```text
├── immutable
├── trim
├── không rỗng
├── max 200 chars
└── equality theo value
```

### `ChapterNumber`

```text
├── immutable
├── > 0
├── next()
└── previous()
```

### `SourceUrl`

```text
├── immutable
├── http/https
├── host bắt buộc
├── normalize scheme
├── normalize host
└── canonical value
```

Sau đó viết test cho:

```text
1. valid input
2. invalid input
3. normalization
4. equality
5. immutability
6. canonical representation
7. behavior
```

---

## Bài tập nâng cao

Thiết kế:

```text
SourceUrl
├── scheme
├── host
├── path
└── query
```

với invariant:

```text
scheme ∈ {http, https}
host != ""
path bắt đầu bằng "/"
```

và:

```python
url.value
```

luôn trả về **canonical URL**.

Đây là bài tập rất tốt trước khi chúng ta chuyển sang **Buổi 14 — Entity + Value Object**, nơi sẽ ghép toàn bộ kiến thức thành một Domain Model hoàn chỉnh:

```text
Story
├── StoryId
├── StoryTitle
├── SourceId
└── Status

Chapter
├── ChapterId
├── ChapterNumber
├── ChapterTitle
└── ChapterContent
```
