# Buổi 7 — Xây dựng Parser Engine (Kiến trúc Parser chuyên nghiệp)

Đây là buổi mà framework bắt đầu giống **Scrapy** hoặc các crawler framework chuyên nghiệp.

**Sau buổi này, Plugin sẽ không còn chứa XPath hay CSS Selector.**

Thay vì:

```python
class NovelBinPlugin:

    def get_book(self, url):

        response = self.client.get(url)

        selector = Selector(response.text)

        title = selector.css("h1::text").get()

        author = selector.xpath("//div[@class='author']/text()").get()

        ...
```

chúng ta sẽ tách thành:

```text
Plugin
    │
    ▼
Parser Engine
    │
    ▼
BookParser
    │
    ▼
Book Model
```

Đây là bước cực kỳ quan trọng để framework dễ bảo trì.

---

# Mục tiêu

Sau buổi này sẽ có kiến trúc:

```text
HTML

↓

Selector

↓

Parser

↓

Book

↓

Worker
```

Plugin chỉ còn làm:

```python
response = self.client.get(url)

book = self.book_parser.parse(response)
```

---

# 1. Kiến trúc Parser

```text
crawler/
│
├── parser/
│
├── engine.py
├── selector.py
├── exceptions.py
├── base.py
│
├── book.py
├── chapter.py
├── image.py
│
└── utils.py
```

Sau này mỗi plugin sẽ có parser riêng:

```text
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

---

# 2. Vai trò của Parser

Parser chỉ có một nhiệm vụ:

```text
HTML

↓

Model
```

Parser **không được**:

* gọi HTTP
* ghi SQLite
* log
* retry
* crawl trang tiếp theo

Đó là trách nhiệm của các tầng khác.

---

# 3. BaseParser

```python
from abc import ABC
from abc import abstractmethod

class BaseParser(ABC):

    @abstractmethod
    def parse(self, response):
        ...
```

Mọi parser đều kế thừa lớp này.

---

# 4. BookParser

Ví dụ:

```python
from parsel import Selector

class BookParser(BaseParser):

    def parse(self, response):

        selector = Selector(response.text)

        title = selector.css("h1::text").get()

        author = selector.css(".author::text").get()

        return Book(
            title=title,
            author=author
        )
```

Worker không biết XPath nằm ở đâu.

---

# 5. ChapterParser

```python
class ChapterParser(BaseParser):

    def parse(self, response):

        selector = Selector(response.text)

        title = selector.css("h1::text").get()

        content = selector.css("#chapter-content").get()

        return Chapter(
            title=title,
            content=content
        )
```

---

# 6. Selector Wrapper

Đừng để parser gọi trực tiếp `Selector`.

Tạo:

```python
class HtmlSelector:

    def __init__(self, html):

        self.selector = Selector(html)
```

API:

```python
selector.text(css)

selector.attr(css)

selector.xpath()

selector.css()
```

Ví dụ:

```python
title = selector.text("h1")
```

Thay vì:

```python
selector.css("h1::text").get()
```

Nếu sau này đổi từ `parsel` sang `BeautifulSoup` hoặc `lxml`, chỉ cần sửa `HtmlSelector`.

---

# 7. Helper Methods

Trong `HtmlSelector`:

```python
selector.text(css)
```

```python
selector.html(css)
```

```python
selector.attrs(css)
```

```python
selector.links(css)
```

```python
selector.exists(css)
```

Ví dụ:

```python
if selector.exists(".vip"):
    ...
```

---

# 8. ParseError

Tạo exception riêng:

```python
class ParseError(Exception):
    pass
```

Ví dụ:

```python
title = selector.text("h1")

if not title:

    raise ParseError(
        "Book title not found."
    )
```

Worker sẽ biết:

```text
Plugin OK

↓

Parser FAIL
```

Thay vì:

```text
AttributeError
```

---

# 9. Parser Engine

Thay vì plugin tạo parser trực tiếp:

```python
BookParser()
```

ta tạo:

```python
class ParserEngine:

    def __init__(self):

        self.parsers = {}
```

Đăng ký:

```python
engine.register(
    "book",
    BookParser()
)
```

Lấy parser:

```python
parser = engine.get("book")
```

Điều này cho phép plugin thay parser rất dễ.

---

# 10. Plugin sử dụng Parser

```python
class NovelPlugin:

    def __init__(

        self,

        client,

        parser_engine

    ):

        self.client = client

        self.parsers = parser_engine
```

Sử dụng:

```python
response = self.client.get(url)

book = self.parsers.get("book").parse(response)
```

Plugin cực kỳ gọn.

---

# 11. Parser Test bằng CLI

Đây là phần mạnh nhất.

Không cần Internet.

Lưu HTML:

```text
tests/

fixtures/

book.html
```

CLI:

```bash
crawler dev parser book tests/fixtures/book.html
```

Luồng:

```text
Đọc file

↓

BookParser

↓

Book

↓

In JSON
```

Output:

```json
{
  "title": "Đấu Phá Thương Khung",
  "author": "Thiên Tằm Thổ Đậu"
}
```

---

# 12. Test XPath

CLI:

```bash
crawler dev xpath \
    tests/fixtures/book.html \
    "//h1/text()"
```

Output:

```text
Đấu Phá Thương Khung
```

---

# 13. Test CSS

```bash
crawler dev css \
    tests/fixtures/book.html \
    ".book-title::text"
```

---

# 14. Snapshot Test

Đây là kỹ thuật rất hữu ích.

Lần đầu:

```bash
crawler dev parser snapshot \
    book.html
```

Sinh:

```text
tests/snapshots/

book.json
```

Sau này:

```bash
crawler dev parser compare \
    book.html
```

Nếu website thay đổi:

```text
FAIL

title changed

author changed
```

Bạn phát hiện ngay parser bị hỏng.

---

# 15. Unit Test

```python
def test_book_parser():

    html = Path(
        "tests/fixtures/book.html"
    ).read_text()

    response = HttpResponse(
        status_code=200,
        url="",
        text=html,
        headers={},
        elapsed=0
    )

    parser = BookParser()

    book = parser.parse(response)

    assert book.title == "Đấu Phá Thương Khung"
```

Không có:

* Internet
* requests
* Worker

---

# 16. CLI dành cho Parser

Tôi thường thiết kế như sau:

```text
crawler dev parser
│
├── book
├── chapter
├── image
├── list
├── snapshot
└── compare
```

Ví dụ:

```bash
crawler dev parser list
```

Output:

```text
book

chapter

image
```

---

# 17. Kiến trúc sau Buổi 7

```text
parser/
│
├── base.py
├── engine.py
├── selector.py
├── exceptions.py
│
├── book.py
├── chapter.py
├── image.py
└── utils.py
```

```text
plugins/

novelbin/

    parser/

        book.py

        chapter.py

        image.py
```

---

# Luồng hoạt động hoàn chỉnh

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

Mỗi tầng chỉ làm đúng một nhiệm vụ.

---

# Bài tập

1. Xây dựng `BaseParser`.
2. Xây dựng `HtmlSelector` bọc `parsel.Selector`.
3. Viết `BookParser` và `ChapterParser`.
4. Tạo `ParserEngine` với:

   * `register()`
   * `get()`
   * `unregister()`
5. Tạo `ParseError`.
6. Chuẩn bị HTML mẫu trong `tests/fixtures/`.
7. Thêm các lệnh CLI:

   * `crawler dev parser book <file>`
   * `crawler dev parser chapter <file>`
   * `crawler dev xpath <file> <expr>`
   * `crawler dev css <file> <expr>`
   * `crawler dev parser snapshot <file>`
   * `crawler dev parser compare <file>`
8. Viết unit test cho:

   * `HtmlSelector`
   * `BookParser`
   * `ChapterParser`
   * `ParserEngine`

---

# Góp ý để framework chuyên nghiệp hơn

Đến đây chúng ta đã có:

* Model
* Plugin
* Plugin Loader
* HTTP Client
* Parser Engine

Nhưng tôi muốn điều chỉnh roadmap một chút. Thay vì sang ngay **Crawler Plugin**, tôi khuyên nên thêm một buổi về **Pipeline & Crawl Context**, vì đây là lớp kết nối tất cả các thành phần đã xây dựng.

Roadmap tiếp theo sẽ là:

* **Buổi 8:** Pipeline + `CrawlContext` (quản lý toàn bộ dependency: `HttpClient`, `ParserEngine`, `Repository`, `Logger`, `Settings`).
* **Buổi 9:** Thiết kế `NovelCrawlerPlugin` hoàn chỉnh (plugin thật đầu tiên).
* **Buổi 10:** Book Discovery (crawl thông tin truyện).
* **Buổi 11:** Chapter List Discovery.
* **Buổi 12:** Chapter Content Crawl.

Cách đi này giúp mỗi tầng được hoàn thiện và kiểm thử bằng CLI trước khi ghép lại thành một crawler hoàn chỉnh. Khi bắt đầu viết plugin thật, bạn sẽ chủ yếu lắp ráp các thành phần đã có thay vì phải viết mọi thứ cùng lúc.
