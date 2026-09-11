# Buổi 4 — ParseResult, Validation và ParserError

Hôm nay chúng ta giải quyết một vấn đề rất thực tế:

> **Website thay đổi HTML hoặc HTML bị thiếu dữ liệu thì Parser phải phản ứng thế nào?**

Không nên để parser văng ra những lỗi kiểu:

```text
AttributeError: 'NoneType' object has no attribute 'text'
IndexError: list index out of range
ValueError: invalid literal for int()
```

Thay vào đó, parser phải tạo ra **lỗi nghiệp vụ có ngữ nghĩa**:

```text
ParserError
├── InvalidPageSourceError
├── MissingFieldError
├── InvalidUrlError
├── InvalidChapterNumberError
└── ParserNotSupportedError
```

Và đặc biệt:

```text
Parser lỗi
    ≠
Fetcher lỗi
```

Fetcher không được biến thành Parser, và Parser cũng không xử lý HTTP.

---

# 1. Trước hết: phân biệt 3 loại lỗi

Trong crawler của chúng ta:

```text
HTTPX
  │
  ├── NetworkError
  ├── Timeout
  ├── ProxyError
  └── HTTPError
```

đây là **Fetcher concern**.

Parser:

```text
page_source
    │
    ├── HTML hỏng
    ├── selector không tồn tại
    ├── thiếu title
    ├── URL không hợp lệ
    └── chapter number không hợp lệ
```

đây là **Parser concern**.

Application:

```text
ParserError
    ↓
retry?
skip?
log?
mark failed?
```

đây là **Application concern**.

---

# 2. Tại sao không trả `None` cho mọi thứ?

Ví dụ:

```python
title = None
```

Nếu website thay đổi:

```html
<h1 class="new-title">
```

nhưng parser vẫn tìm:

```python
.title
```

thì:

```python
title = None
```

sẽ khiến crawler tiếp tục chạy.

Sau đó database có thể chứa:

```text
title = NULL
author = NULL
url = ...
```

Rất khó phát hiện.

Với những field **bắt buộc**, tốt hơn là:

```text
MissingFieldError
```

để hệ thống biết:

> Parser đã không còn phù hợp với HTML hiện tại.

---

# 3. Required và Optional Field

Đây là quyết định quan trọng.

## Listing

```text
title       REQUIRED
author      REQUIRED
url         REQUIRED
```

Nếu thiếu:

```text
ParserError
```

---

## Novel

```text
title         REQUIRED
author        REQUIRED
url           REQUIRED

cover         OPTIONAL
description   OPTIONAL
status        OPTIONAL
```

---

## Chapter

```text
title          REQUIRED
chapter_no     có thể OPTIONAL
content        REQUIRED
url            REQUIRED
```

Ví dụ một website không ghi:

```text
Chapter 123
```

mà chỉ:

```text
Đường về nhà
```

thì `chapter_no` có thể là:

```python
None
```

Không nên coi đây luôn là lỗi parser.

---

# 4. Thiết kế `ParserError`

Tạo:

```text
domain/
└── parser_error.py
```

Code:

```python
class ParserError(Exception):
    """Base exception for parser errors."""
```

Tất cả lỗi parser sẽ kế thừa nó.

---

# 5. `InvalidPageSourceError`

```python
class InvalidPageSourceError(ParserError):
    """Raised when page source is invalid."""
```

Ví dụ:

```python
if not page_source:
    raise InvalidPageSourceError(
        "Page source is empty"
    )
```

---

# 6. `MissingFieldError`

```python
class MissingFieldError(ParserError):
    """Raised when a required field cannot be extracted."""

    def __init__(
        self,
        field: str,
        selector: str | None = None,
    ):
        self.field = field
        self.selector = selector

        message = f"Required field '{field}' is missing"

        if selector:
            message += f" (selector={selector!r})"

        super().__init__(message)
```

Ví dụ:

```python
raise MissingFieldError(
    field="title",
    selector=".story-title",
)
```

Lỗi:

```text
Required field 'title' is missing (selector='.story-title')
```

Cực kỳ hữu ích khi debug website.

---

# 7. `InvalidUrlError`

```python
class InvalidUrlError(ParserError):
    """Raised when extracted URL is invalid."""

    def __init__(self, url: str):
        self.url = url

        super().__init__(
            f"Invalid URL: {url!r}"
        )
```

Sau này chúng ta sẽ có URL Value Object tốt hơn, nhưng hiện tại chưa cần vội.

---

# 8. `InvalidChapterNumberError`

```python
class InvalidChapterNumberError(ParserError):
    """Raised when chapter number cannot be parsed."""

    def __init__(self, value: str):
        self.value = value

        super().__init__(
            f"Invalid chapter number: {value!r}"
        )
```

Ví dụ:

```python
"Chương abc"
```

không thể parse thành số.

---

# 9. `ParserNotSupportedError`

Sau này Parser Registry sẽ cần lỗi này:

```python
class ParserNotSupportedError(ParserError):
    """Raised when no parser supports the URL."""

    def __init__(self, url: str):
        self.url = url

        super().__init__(
            f"No parser supports URL: {url!r}"
        )
```

---

# 10. File hoàn chỉnh

`domain/parser_error.py`:

```python
class ParserError(Exception):
    """Base exception for parser errors."""


class InvalidPageSourceError(ParserError):
    """Raised when page source is invalid."""


class MissingFieldError(ParserError):
    """Raised when a required field cannot be extracted."""

    def __init__(
        self,
        field: str,
        selector: str | None = None,
    ):
        self.field = field
        self.selector = selector

        message = f"Required field '{field}' is missing"

        if selector:
            message += f" (selector={selector!r})"

        super().__init__(message)


class InvalidUrlError(ParserError):
    """Raised when extracted URL is invalid."""

    def __init__(self, url: str):
        self.url = url

        super().__init__(
            f"Invalid URL: {url!r}"
        )


class InvalidChapterNumberError(ParserError):
    """Raised when chapter number cannot be parsed."""

    def __init__(self, value: str):
        self.value = value

        super().__init__(
            f"Invalid chapter number: {value!r}"
        )


class ParserNotSupportedError(ParserError):
    """Raised when no parser supports the URL."""

    def __init__(self, url: str):
        self.url = url

        super().__init__(
            f"No parser supports URL: {url!r}"
        )
```

---

# 11. Validation page source

Ta không nên để:

```python
HTMLParser("")
```

được gọi lung tung.

Tạo helper:

```python
def validate_page_source(
    page_source: str,
) -> None:

    if not isinstance(page_source, str):
        raise InvalidPageSourceError(
            "Page source must be a string"
        )

    if not page_source.strip():
        raise InvalidPageSourceError(
            "Page source is empty"
        )
```

---

# 12. Đặt helper ở đâu?

Tạm thời:

```text
infrastructure/
└── parser/
    ├── base.py
    ├── selectolax_document.py
    └── validation.py
```

`validation.py`:

```python
from crawler.domain.parser_error import (
    InvalidPageSourceError,
)


def validate_page_source(
    page_source: str,
) -> None:

    if not isinstance(page_source, str):
        raise InvalidPageSourceError(
            "Page source must be a string"
        )

    if not page_source.strip():
        raise InvalidPageSourceError(
            "Page source is empty"
        )
```

---

# 13. Cải thiện `SelectolaxDocument`

Buổi 2 ta có:

```python
class SelectolaxDocument:

    def __init__(self, page_source: str):
        self._tree = HTMLParser(page_source)
```

Bây giờ:

```python
from selectolax.parser import HTMLParser

from .validation import validate_page_source


class SelectolaxDocument:

    def __init__(self, page_source: str):
        validate_page_source(page_source)

        self._tree = HTMLParser(page_source)

    def first(self, selector: str):
        return self._tree.css_first(selector)

    def all(self, selector: str):
        return self._tree.css(selector)

    def text(self, selector: str) -> str | None:
        node = self.first(selector)

        if node is None:
            return None

        value = node.text().strip()

        return value or None

    def attribute(
        self,
        selector: str,
        name: str,
    ) -> str | None:

        node = self.first(selector)

        if node is None:
            return None

        value = node.attributes.get(name)

        if value is None:
            return None

        value = value.strip()

        return value or None
```

---

# 14. Nhưng `text()` không nên raise error

Ví dụ:

```python
title = document.text(".title")
```

Nếu `.title` không tồn tại, ta trả:

```python
None
```

Tại sao?

Vì `SelectolaxDocument` chỉ là **DOM adapter**.

Nó không biết:

```text
title là REQUIRED
author là REQUIRED
description là OPTIONAL
```

Chỉ parser biết điều đó.

Đây là separation of responsibility rất quan trọng.

---

# 15. Parser mới quyết định Required

Ví dụ:

```python
title = document.text(".title")

if title is None:
    raise MissingFieldError(
        field="title",
        selector=".title",
    )
```

Trong khi:

```python
description = document.text(".description")
```

có thể chấp nhận:

```python
description is None
```

---

# 16. Tạo helper `required_text`

Để tránh lặp code:

```python
title = document.text(".title")

if title is None:
    raise MissingFieldError(...)

author = document.text(".author")

if author is None:
    raise MissingFieldError(...)
```

Ta tạo:

```python
from crawler.domain.parser_error import (
    MissingFieldError,
)


def required_text(
    document,
    selector: str,
    field: str,
) -> str:

    value = document.text(selector)

    if value is None:
        raise MissingFieldError(
            field=field,
            selector=selector,
        )

    return value
```

---

# 17. `required_attribute`

Tương tự URL:

```python
def required_attribute(
    document,
    selector: str,
    attribute: str,
    field: str,
) -> str:

    value = document.attribute(
        selector,
        attribute,
    )

    if value is None:
        raise MissingFieldError(
            field=field,
            selector=selector,
        )

    return value
```

Sau này parser sẽ rất sạch.

---

# 18. Ví dụ parser giả

```python
class DummyListingParser:

    def parse_listing(
        self,
        page_source: str,
        url: str,
    ):
        document = SelectolaxDocument(page_source)

        title = required_text(
            document,
            ".title",
            "title",
        )

        author = required_text(
            document,
            ".author",
            "author",
        )

        story_url = required_attribute(
            document,
            "a",
            "href",
            "url",
        )

        ...
```

Nếu HTML:

```html
<h2 class="title">Truyện A</h2>
```

nhưng không có:

```html
<span class="author">
```

thì parser báo:

```text
MissingFieldError:
Required field 'author' is missing
```

thay vì:

```text
AttributeError
```

---

# 19. ParseResult: thành công hay lỗi?

Có một câu hỏi quan trọng:

> Có nên để `ParseResult` chứa cả success và error không?

Ví dụ:

```python
ParseResult(
    success=False,
    error=...
)
```

**Hiện tại tôi không khuyến nghị.**

Với Python application của chúng ta, cách đơn giản và rõ ràng hơn:

```text
success
   ↓
return Domain Result

failure
   ↓
raise ParserError
```

Ví dụ:

```python
try:
    result = parser.parse_listing(
        page_source,
        url,
    )

except ParserError as exc:
    ...
```

---

# 20. Tại sao không dùng `ParseResult[T]` ngay?

Ta hoàn toàn có thể thiết kế:

```python
ParseResult[T]
```

nhưng lúc này sẽ xuất hiện:

```text
Result
Either
Success
Failure
Optional
Exception
```

quá nhiều abstraction.

Mục tiêu của framework hiện tại là:

```text
Fetcher
Parser
Application
Repository
```

nên ta ưu tiên code rõ ràng.

Khi crawler lớn hơn, nếu cần functional error handling, chúng ta có thể thêm `Result`.

---

# 21. ParserError không xử lý trong Parser

Một lỗi thường gặp:

```python
class ListingParser:

    def parse_listing(...):

        try:
            ...
        except Exception:
            return []
```

**Không làm.**

Đây là anti-pattern.

Nếu website thay đổi:

```text
Parser
 ↓
Exception
 ↓
[]
```

crawler sẽ tưởng:

> Listing này không có truyện.

Trong khi thực tế:

> Parser đã hỏng.

---

# 22. Không được nuốt exception

Sai:

```python
try:
    title = ...
except Exception:
    title = ""
```

Sai:

```python
try:
    ...
except Exception:
    return ListingPage(
        items=[],
        next_url=None,
    )
```

Sai:

```python
except Exception:
    pass
```

Đúng:

```python
raise MissingFieldError(
    field="title",
    selector=".title",
)
```

---

# 23. Nhưng Application mới quyết định làm gì

Ví dụ:

```python
try:
    result = parser.parse_listing(
        page_source,
        url,
    )

except ParserError as exc:
    logger.error(
        "Parser failed: %s",
        exc,
    )

    mark_page_failed(url)
```

Parser không biết:

```text
retry
database
queue
logging policy
```

Parser chỉ:

```text
phát hiện lỗi
     ↓
raise ParserError
```

---

# 24. Flow hoàn chỉnh

```text
HTTPX Fetcher
      │
      │ page_source
      ▼
SelectolaxDocument
      │
      ▼
Site Parser
      │
      ├──── SUCCESS ────► Domain Model
      │
      │
      └──── FAILURE
               │
               ▼
          ParserError
               │
               ▼
          Application
               │
          ┌────┴─────┐
          ▼          ▼
        Retry       Failed
```

---

# 25. Phân loại lỗi sau này

Ta sẽ có architecture:

```text
Exception
│
├── FetchError
│   ├── NetworkError
│   ├── TimeoutError
│   ├── ProxyError
│   └── HTTPError
│
└── ParserError
    ├── InvalidPageSourceError
    ├── MissingFieldError
    ├── InvalidUrlError
    ├── InvalidChapterNumberError
    └── ParserNotSupportedError
```

Điều này rất hữu ích cho crawler.

Ví dụ:

```python
except TimeoutError:
    retry()
```

nhưng:

```python
except MissingFieldError:
    mark_parser_broken()
```

Hai lỗi có **chiến lược xử lý hoàn toàn khác nhau**.

---

# 26. Một ví dụ thực tế

Giả sử crawler nhận:

```text
GET /truyen-a
```

Fetcher thành công:

```text
HTTP 200
```

HTML:

```html
<h1 class="book-name">
    Truyện A
</h1>
```

Parser cũ tìm:

```python
".title"
```

Kết quả:

```python
None
```

Parser:

```python
raise MissingFieldError(
    field="title",
    selector=".title",
)
```

Application nhận:

```text
ParserError
```

ghi:

```text
Parser failed:
Required field 'title' is missing
(selector='.title')
```

Đây chính là tín hiệu cho chúng ta:

> Website đã thay đổi HTML.

---

# 27. Test

Tạo:

```text
tests/
└── parser/
    └── test_validation.py
```

Test page source:

```python
import pytest

from crawler.infrastructure.parser.validation import (
    validate_page_source,
)

from crawler.domain.parser_error import (
    InvalidPageSourceError,
)


def test_empty_page_source():
    with pytest.raises(InvalidPageSourceError):
        validate_page_source("")


def test_whitespace_page_source():
    with pytest.raises(InvalidPageSourceError):
        validate_page_source("   ")


def test_valid_page_source():
    validate_page_source(
        "<html><body>Hello</body></html>"
    )
```

---

# 28. Test `MissingFieldError`

```python
from crawler.domain.parser_error import (
    MissingFieldError,
)


def test_missing_field_error():
    error = MissingFieldError(
        field="title",
        selector=".title",
    )

    assert error.field == "title"
    assert error.selector == ".title"
    assert "title" in str(error)
    assert ".title" in str(error)
```

---

# 29. Test `required_text`

```python
import pytest

from crawler.infrastructure.parser.selectolax_document import (
    SelectolaxDocument,
)

from crawler.infrastructure.parser.validation import (
    required_text,
)

from crawler.domain.parser_error import (
    MissingFieldError,
)


def test_required_text():
    html = """
    <h1 class="title">
        Truyện A
    </h1>
    """

    document = SelectolaxDocument(html)

    result = required_text(
        document,
        ".title",
        "title",
    )

    assert result == "Truyện A"


def test_required_text_missing():
    html = """
    <h1 class="name">
        Truyện A
    </h1>
    """

    document = SelectolaxDocument(html)

    with pytest.raises(MissingFieldError):
        required_text(
            document,
            ".title",
            "title",
        )
```

---

# 30. Cấu trúc sau Buổi 4

```text
src/
└── crawler/
    │
    ├── domain/
    │   ├── novel.py
    │   ├── chapter.py
    │   ├── parser_result.py
    │   └── parser_error.py
    │
    └── infrastructure/
        └── parser/
            ├── base.py
            ├── selectolax_document.py
            └── validation.py
```

---

# 31. Quan hệ giữa các file

```text
                    domain
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
    Domain Models           ParserError
          ▲                       ▲
          │                       │
          │                       │
    infrastructure/parser
          │
    ┌─────┴───────────────────┐
    │                         │
    ▼                         ▼
SelectolaxDocument       validation
    │                         │
    └──────────┬──────────────┘
               │
               ▼
         Concrete Parser
```

Điểm đáng chú ý:

```text
SelectolaxDocument → infrastructure
ParserError        → domain
```

Parser cụ thể có thể dùng cả hai.

---

# 32. Một nguyên tắc rất quan trọng cho các buổi sau

Chúng ta sẽ phân biệt:

### DOM extraction

```python
document.text(".title")
```

→ có thể trả `None`.

### Required domain extraction

```python
required_text(
    document,
    ".title",
    "title",
)
```

→ thiếu thì `ParserError`.

### Optional domain extraction

```python
description = document.text(".description")
```

→ thiếu vẫn hợp lệ.

Như vậy Parser biết chính xác **field nào bắt buộc, field nào tùy chọn**.

---

# Bài tập Buổi 4

Tự hoàn thành 3 phần:

### 1. `parser_error.py`

Tạo:

```text
ParserError
InvalidPageSourceError
MissingFieldError
InvalidUrlError
InvalidChapterNumberError
ParserNotSupportedError
```

### 2. `validation.py`

Tạo:

```python
validate_page_source()

required_text()

required_attribute()
```

### 3. Test

Test ít nhất:

```text
empty page source
missing title
missing author
missing href
valid required field
optional field không tồn tại
```

---

## Sau Buổi 4, kiến trúc đã khá chắc

```text
             HTTPX
               │
               │ str
               ▼
      ┌──────────────────┐
      │ Selectolax       │
      │ Document Adapter │
      └────────┬─────────┘
               │
               ▼
      ┌──────────────────┐
      │ Concrete Parser  │
      └────────┬─────────┘
               │
       ┌───────┴────────┐
       │                │
    SUCCESS           FAILURE
       │                │
       ▼                ▼
 Domain Model       ParserError
       │                │
       └───────┬────────┘
               ▼
          Application
```

**Buổi 5** chúng ta sẽ quay lại Domain và xây **`Novel` / `NovelSummary` / `ChapterSummary` thật bài bản**, bao gồm invariant, URL, optional field và tại sao **Listing Model không nên dùng trực tiếp `Novel`**. Sau đó từ Buổi 6 mới bắt đầu đi vào parser thực tế.
