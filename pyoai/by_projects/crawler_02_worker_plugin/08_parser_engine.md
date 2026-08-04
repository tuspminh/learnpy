# Buổi 8 — Xây dựng Parser Engine

Đây là buổi học quan trọng nhất của **Crawler Framework**.

Sau buổi này, framework sẽ đạt được một nguyên tắc rất quan trọng:

> **Plugin không chứa XPath/CSS Selector.**

Plugin chỉ điều phối.

Parser mới là nơi hiểu HTML.

Đây là cách mà các crawler framework lớn đều hướng tới.

---

# Mục tiêu

Sau buổi này kiến trúc sẽ là:

```text
                 Worker
                    │
                    ▼
                 Plugin
                    │
                    ▼
             Request Client
                    │
                    ▼
              HttpResponse
                    │
                    ▼
              Parser Engine
                    │
          ┌─────────┴─────────┐
          │                   │
      BookParser        ChapterParser
          │                   │
          ▼                   ▼
       Book Model      Chapter Model
```

Plugin chỉ làm:

```python
response = context.http.get(url)

book = context.parsers.book.parse(response)
```

Không có:

* XPath
* CSS
* Regex

---

# Mục tiêu của Parser Engine

Parser chỉ có **một nhiệm vụ**

```text
HTML

↓

Model
```

Không được:

* gọi HTTP
* ghi SQLite
* retry
* logging
* sleep
* crawl trang khác

Parser phải là **Pure Function**.

```text
HTML

↓

Book
```

---

# Kiến trúc

```
crawler/

parser/

    __init__.py

    engine.py

    registry.py

    selector.py

    base.py

    exceptions.py

    helpers.py

    book.py

    chapter.py

    image.py

    search.py
```

---

# Kiến trúc Plugin

```
plugins/

novelbin/

    parser/

        book.py

        chapter.py

        image.py

truyenfull/

    parser/

        book.py

        chapter.py
```

Parser của website nào nằm trong plugin đó.

---

# 1. BaseParser

```python
from abc import ABC
from abc import abstractmethod

class BaseParser(ABC):

    @abstractmethod
    def parse(self, response):
        ...
```

---

Có thể thêm generic để type-safe hơn:

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class BaseParser(
    ABC,
    Generic[T]
):

    @abstractmethod
    def parse(
        self,
        response
    ) -> T:
        ...
```

Ví dụ

```python
class BookParser(
    BaseParser[Book]
):
    ...
```

IDE sẽ hiểu parser trả về Book.

---

# 2. HtmlSelector Wrapper

Không dùng trực tiếp

```python
Selector(html)
```

Tạo wrapper.

```python
from parsel import Selector

class HtmlSelector:

    def __init__(self, html):

        self.selector = Selector(html)
```

---

API

```python
selector.text(css)

selector.html(css)

selector.attr(css)

selector.exists(css)

selector.css(css)

selector.xpath(xpath)
```

---

Ví dụ

```python
title = selector.text("h1")
```

Thay vì

```python
selector.css(
    "h1::text"
).get()
```

---

# 3. Vì sao phải Wrapper?

Giả sử sau này đổi

```
parsel

↓

BeautifulSoup
```

Plugin

↓

Parser

↓

không cần sửa.

Chỉ sửa

```
HtmlSelector
```

---

# 4. BookParser

```python
class BookParser(
    BaseParser[Book]
):

    def parse(self, response):

        selector = HtmlSelector(
            response.text
        )

        return Book(

            title=selector.text(
                "h1"
            ),

            author=selector.text(
                ".author"
            )
        )
```

---

# 5. ChapterParser

```python
class ChapterParser(
    BaseParser[Chapter]
):

    def parse(
        self,
        response
    ):

        selector = HtmlSelector(
            response.text
        )

        return Chapter(

            title=selector.text(
                "h1"
            ),

            content=selector.html(
                "#chapter-content"
            )
        )
```

---

# 6. Selector Helper

HtmlSelector nên có:

```python
selector.text()

selector.texts()

selector.html()

selector.htmls()

selector.attr()

selector.attrs()

selector.exists()

selector.css()

selector.xpath()
```

Ví dụ

```python
selector.texts(
    ".tag"
)
```

↓

```
["Action","Fantasy"]
```

---

# 7. ParseError

Không nên

```python
AttributeError
```

hay

```python
IndexError
```

Ta tạo

```python
class ParseError(
    Exception
):
    pass
```

Ví dụ

```python
title = selector.text(
    "h1"
)

if title is None:

    raise ParseError(
        "Book title missing."
    )
```

Worker sẽ biết

```
Parser lỗi
```

không phải

```
HTTP lỗi
```

---

# 8. Parser Registry

Ta cần Registry giống Plugin.

```python
class ParserRegistry:

    def __init__(self):

        self.parsers = {}
```

---

Đăng ký

```python
registry.register(

    "book",

    BookParser()
)
```

---

Lấy

```python
registry.get(
    "book"
)
```

---

# 9. Parser Engine

Engine sẽ quản lý Registry.

```python
class ParserEngine:

    def __init__(self):

        self.registry = ParserRegistry()
```

API

```python
engine.register()

engine.unregister()

engine.get()

engine.names()
```

---

# 10. Plugin sử dụng Parser

Plugin cực kỳ đơn giản.

```python
response = context.http.get(url)

book = context.parsers.get(
    "book"
).parse(response)
```

Plugin không biết XPath.

---

# 11. HTML Fixture

Đây là điều rất nhiều người quên.

Tạo

```
tests/

fixtures/

book.html

chapter.html

search.html
```

Đây là HTML thật tải từ website.

Parser sẽ test trên file này.

Không cần Internet.

---

# 12. CLI Parser

Đây là phần mạnh nhất.

## Parse Book

```bash
crawler dev parser book \
    tests/fixtures/book.html
```

↓

```
BookParser

↓

Book
```

Output

```json
{
    "title":"Đấu Phá Thương Khung",

    "author":"Thiên Tằm Thổ Đậu"
}
```

---

## Parse Chapter

```bash
crawler dev parser chapter \
    tests/fixtures/chapter.html
```

---

## XPath Test

```bash
crawler dev xpath \
    tests/fixtures/book.html \
    "//h1/text()"
```

↓

```
Đấu Phá Thương Khung
```

---

## CSS Test

```bash
crawler dev css \
    tests/fixtures/book.html \
    ".book-title::text"
```

↓

```
Đấu Phá Thương Khương
```

---

## Pretty HTML

```bash
crawler dev parser pretty \
    tests/fixtures/book.html
```

↓

Format HTML.

Rất hữu ích khi debug.

---

## Validate HTML

```bash
crawler dev parser validate \
    tests/fixtures/book.html
```

↓

```
Title

✓

Author

✓

Cover

✓

Description

✗ Missing
```

---

# 13. Snapshot Test

Lần đầu

```bash
crawler dev parser snapshot \
    tests/fixtures/book.html
```

Sinh

```
tests/

snapshots/

book.json
```

---

Sau này

```bash
crawler dev parser compare \
    tests/fixtures/book.html
```

↓

```
PASS
```

Nếu website đổi

↓

```
FAIL

Author changed

Description missing
```

Bạn biết parser phải sửa.

---

# 14. Unit Test

```python
def test_book():

    html = Path(
        "tests/fixtures/book.html"
    ).read_text()

    response = HttpResponse(

        status_code=200,

        url="",

        text=html,

        headers={},

        elapsed=0,

        encoding="utf8",

        content=b""
    )

    parser = BookParser()

    book = parser.parse(
        response
    )

    assert book.title == \
        "Đấu Phá Thương Khung"
```

---

Kiểm tra Registry

```python
def test_registry():

    registry = ParserRegistry()

    registry.register(

        "book",

        BookParser()
    )

    assert registry.get(
        "book"
    )
```

---

# 15. Kiến trúc sau Buổi 8

```
parser/

    base.py

    engine.py

    registry.py

    selector.py

    helpers.py

    exceptions.py

    book.py

    chapter.py

    image.py
```

---

Luồng hoạt động

```text
Worker

↓

Plugin

↓

HttpClient

↓

HttpResponse

↓

ParserEngine

↓

BookParser

↓

Book Model

↓

Repository
```

Mỗi tầng chỉ có **một trách nhiệm**.

---

# Bài tập

Xây dựng đầy đủ:

* `BaseParser`
* `HtmlSelector`
* `ParserRegistry`
* `ParserEngine`
* `BookParser`
* `ChapterParser`
* `ParseError`

Viết CLI:

```bash
crawler dev parser book FILE

crawler dev parser chapter FILE

crawler dev xpath FILE EXPR

crawler dev css FILE EXPR

crawler dev parser validate FILE

crawler dev parser snapshot FILE

crawler dev parser compare FILE
```

Viết unit test cho:

* `HtmlSelector`
* `BookParser`
* `ChapterParser`
* `ParserRegistry`
* `ParserEngine`

---

# Cải tiến kiến trúc (quan trọng)

Đây là điểm tôi muốn nâng cấp so với roadmap ban đầu.

Thay vì mỗi parser tự tạo `HtmlSelector`, hãy đưa thêm một lớp **ParseContext** để chia sẻ các tiện ích trong quá trình phân tích.

```text
HttpResponse
      │
      ▼
 ParseContext
      │
      ├── HtmlSelector
      ├── Base URL
      ├── Encoding
      ├── Logger
      ├── Helper Functions
      └── Parser Options
      │
      ▼
   BookParser
```

Khi đó chữ ký của parser sẽ là:

```python
book = parser.parse(parse_context)
```

Lợi ích:

* Không phải tạo `HtmlSelector` ở mọi parser.
* Có thể lưu cache kết quả XPath/CSS.
* Có thể cung cấp các hàm chuẩn như `absolute_url()`, `normalize_whitespace()`, `clean_html()`, `extract_text()`.
* Dễ mở rộng khi sau này cần hỗ trợ JSON API hoặc XML mà không phải thay đổi giao diện của parser.

Đây là thiết kế mà nhiều framework crawler lớn áp dụng: **Context → Parser → Model**, thay vì truyền trực tiếp chuỗi HTML vào từng parser. Điều này sẽ giúp các buổi tiếp theo (Crawler Pipeline, Worker và Scheduler) ghép nối với nhau một cách tự nhiên và dễ mở rộng.
