Rất đúng. Thực ra tôi đã **đi lệch roadmap** sang hướng xây dựng Worker/Pipeline sớm. Nếu mục tiêu là **xây dựng framework crawler theo plugin**, thì sau khi hoàn thành:

* ✅ Buổi 1: Architecture
* ✅ Buổi 2: Project Structure
* ✅ Buổi 3: Core Model
* ✅ Buổi 4: Plugin Interface
* ✅ Buổi 5: Plugin Loader
* ✅ Buổi 6: Crawl Context
* ✅ Buổi 7: Request Client
* ✅ Buổi 8: Parser Engine

thì **Giai đoạn 2** phải tập trung hoàn toàn vào **xây dựng một plugin crawler hoàn chỉnh**.

Đây là thứ tự hợp lý hơn:

```
Giai đoạn 2 — Crawler Plugin

Buổi 9.  Thiết kế Novel Plugin
Buổi 10. Book Parser
Buổi 11. Chapter Parser
Buổi 12. Content Parser
Buổi 13. Image Parser
Buổi 14. Metadata Parser
Buổi 15. Plugin Versioning
```

Đây cũng là cách Scrapy phát triển spider.

---

# Buổi 9 — Thiết kế Novel Plugin

Đây là buổi học quan trọng nhất của toàn bộ **Giai đoạn 2**.

Sau buổi này, chúng ta sẽ có **plugin đầu tiên** có thể crawl một website truyện.

Điều quan trọng là:

> **Plugin không phải Parser.**

Plugin chỉ là **Orchestrator (điều phối)**.

---

# Mục tiêu

Sau buổi này plugin sẽ có kiến trúc:

```text
                  NovelPlugin
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
 HttpClient     ParserEngine     CrawlContext
        │              │
        ▼              ▼
  HttpResponse      BookParser
                    ChapterParser
                    ContentParser
```

Plugin không parse HTML.

Plugin không save SQLite.

Plugin không download ảnh.

Plugin chỉ điều phối.

---

# Trách nhiệm của Plugin

Plugin chỉ làm 4 việc:

```
1. Xây URL

↓

2. Gửi Request

↓

3. Chọn Parser

↓

4. Trả Model
```

Ví dụ:

```python
book = plugin.get_book(url)

chapters = plugin.get_chapters(url)

chapter = plugin.get_chapter(url)
```

---

# Cấu trúc Plugin

```
plugins/

novelbin/

    __init__.py

    plugin.py

    manifest.py

    config.py

    parser/

        book.py

        chapter.py

        content.py

        image.py

        metadata.py
```

Plugin chỉ có một file điều phối.

---

# Interface

Buổi 4 chúng ta có:

```python
class CrawlerPlugin(ABC):

    def get_book(...):

    def get_chapters(...):

    def get_chapter(...)
```

Bây giờ sẽ implement.

---

# Thiết kế Plugin

```python
class NovelPlugin(CrawlerPlugin):

    def __init__(

        self,

        context

    ):

        self.context = context
```

Plugin không tạo:

* HttpClient
* Parser
* Repository

Tất cả lấy từ Context.

---

# Khởi tạo Parser

```python
class NovelPlugin:

    @property
    def book_parser(self):

        return self.context.parsers.get(
            "book"
        )
```

Tương tự:

```python
chapter_parser
```

```python
content_parser
```

```python
image_parser
```

---

# get_book()

Flow

```
URL

↓

HTTP

↓

BookParser

↓

Book
```

Code

```python
def get_book(

    self,

    url

):

    response = self.context.http.get(
        url
    )

    return self.book_parser.parse(
        response
    )
```

Plugin cực kỳ ngắn.

---

# get_chapters()

```
URL

↓

HTTP

↓

ChapterParser

↓

list[Chapter]
```

```python
def get_chapters(

    self,

    url

):

    response = self.context.http.get(
        url
    )

    return self.chapter_parser.parse(
        response
    )
```

---

# get_content()

```
Chapter URL

↓

HTTP

↓

ContentParser

↓

Chapter.content
```

```python
def get_content(

    self,

    url

):
    ...
```

---

# Không được làm điều này

Sai

```python
class NovelPlugin:

    def get_book(...):

        selector = Selector(...)
```

Sai.

Parser mới được dùng Selector.

---

Sai

```python
BookRepository.save(...)
```

Plugin không được save.

---

Sai

```python
requests.get(...)
```

Plugin chỉ dùng

```python
context.http
```

---

# URL Builder

Một website thường có nhiều URL.

Ví dụ

```
Book

/book/123
```

```
Chapter

/book/123/chapter-1
```

```
Search

/search?q=abc
```

Ta tách riêng:

```python
class UrlBuilder:

    def book(...)

    def chapter(...)

    def search(...)
```

Plugin:

```python
url = self.url_builder.book(
    book_id
)
```

Không hardcode.

---

# Plugin Workflow

```
Book URL

↓

RequestClient

↓

Response

↓

BookParser

↓

Book
```

```
Book URL

↓

RequestClient

↓

ChapterParser

↓

list[Chapter]
```

```
Chapter URL

↓

RequestClient

↓

ContentParser

↓

Chapter
```

---

# Error Mapping

Plugin không nên ném:

```
TimeoutError

AttributeError

ConnectionError
```

Ta tạo exception:

```
PluginError

↓

RequestError

↓

ParseError
```

Worker sẽ dễ xử lý.

---

# CLI Test

Đây là phần tôi luôn làm đầu tiên.

## Test Book

```bash
crawler dev plugin book \
    novelbin \
    https://abc.com/book/1
```

↓

```
Book

Title

Author

Status
```

---

## Test Chapter List

```bash
crawler dev plugin chapters \
    novelbin \
    https://abc.com/book/1
```

↓

```
120 chapter
```

---

## Test Content

```bash
crawler dev plugin content \
    novelbin \
    https://...
```

↓

```
Chapter 1

Lorem ipsum...
```

---

## Test toàn Plugin

```bash
crawler dev plugin doctor \
    novelbin
```

↓

```
Metadata

PASS

Book

PASS

Chapter

PASS

Content

PASS
```

---

# Unit Test

```python
def test_get_book():

    plugin = NovelPlugin(
        mock_context
    )

    book = plugin.get_book(
        url
    )

    assert book.title
```

---

```python
def test_get_chapters():

    chapters = plugin.get_chapters(
        url
    )

    assert len(chapters) > 0
```

---

# Kiến trúc sau Buổi 9

```
plugins/

novelbin/

    plugin.py

    manifest.py

    config.py

    parser/

        book.py

        chapter.py

        content.py

        image.py

        metadata.py

    url_builder.py
```

Plugin bây giờ chỉ còn khoảng **100–200 dòng**, rất dễ đọc và dễ bảo trì.

---

# Bài tập

Xây dựng `NovelPlugin` với các phương thức:

* `get_book(url)`
* `get_chapters(url)`
* `get_content(url)`
* `get_images(url)`
* `get_metadata(url)`

Tạo `UrlBuilder` để sinh URL thay vì nối chuỗi trực tiếp.

Viết CLI:

```bash
crawler dev plugin book <plugin> <url>
crawler dev plugin chapters <plugin> <url>
crawler dev plugin content <plugin> <url>
crawler dev plugin images <plugin> <url>
crawler dev plugin metadata <plugin> <url>
crawler dev plugin doctor <plugin>
```

Viết unit test bằng `MockHttpClient` và HTML fixture, đảm bảo plugin có thể được kiểm thử hoàn toàn offline.

---

## Chuẩn bị cho Buổi 10

Ở **Buổi 10**, chúng ta sẽ đi sâu vào **Book Parser**, không chỉ lấy `title` và `author` mà còn xây dựng một parser chuyên nghiệp có khả năng:

* Trích xuất đầy đủ thông tin `Book`.
* Chuẩn hóa dữ liệu (normalize).
* Xử lý thiếu trường bắt buộc.
* Hỗ trợ nhiều layout HTML.
* Kiểm thử bằng snapshot và HTML fixture.
* Đảm bảo parser hoạt động ổn định ngay cả khi website có những thay đổi nhỏ về giao diện.
