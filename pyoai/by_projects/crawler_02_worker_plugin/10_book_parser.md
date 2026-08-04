# Buổi 10 — Xây dựng Book Parser chuyên nghiệp

Đây là buổi đầu tiên chúng ta viết **parser thật** cho một website truyện.

Sau buổi này, parser sẽ có thể chuyển một trang HTML của truyện thành một đối tượng `Book` hoàn chỉnh.

> Mục tiêu của buổi này không phải là lấy được dữ liệu, mà là **xây dựng một parser có khả năng bảo trì nhiều năm**.

---

# Mục tiêu

Sau buổi này, luồng xử lý sẽ là:

```text
Book URL
    │
    ▼
RequestClient
    │
    ▼
HttpResponse
    │
    ▼
BookParser
    │
    ▼
Book
```

Plugin chỉ còn:

```python
response = context.http.get(url)

book = context.parsers.book.parse(response)
```

---

# Book cần parse những gì?

Một trang truyện thường chứa rất nhiều dữ liệu.

```text
Book

├── id
├── title
├── slug
├── author
├── description
├── cover
├── status
├── language
├── source
├── original_url
├── categories
├── tags
├── last_chapter
├── chapter_count
├── updated_at
└── metadata
```

Book Parser có nhiệm vụ tạo đầy đủ model này.

---

# Cấu trúc

```text
plugins/

    novelbin/

        parser/

            base.py

            book.py

            helpers.py

            mapping.py

            validators.py
```

Book Parser không nên chứa toàn bộ logic trong một file.

---

# Thiết kế

```python
class BookParser(
    BaseParser[Book]
):

    def parse(
        self,
        context: ParseContext
    ) -> Book:

        ...
```

Chúng ta sẽ dùng `ParseContext` thay vì truyền `HttpResponse`.

---

# ParseContext

```python
@dataclass(slots=True)
class ParseContext:

    response: HttpResponse

    selector: HtmlSelector

    base_url: str

    encoding: str

    plugin: str
```

Parser không cần tạo `HtmlSelector` nữa.

---

# Nguyên tắc

BookParser chỉ làm:

```text
HTML

↓

Book
```

Không được:

* download ảnh
* lưu database
* crawl chapter
* gọi API khác

---

# Chia parser thành nhiều hàm nhỏ

Sai:

```python
def parse(...):

    # 400 dòng
```

Đúng:

```python
class BookParser:

    def parse(self, context):

        return Book(

            title=self.parse_title(context),

            author=self.parse_author(context),

            cover=self.parse_cover(context),

            description=self.parse_description(context),

            categories=self.parse_categories(context),

            status=self.parse_status(context),
        )
```

Mỗi trường là một hàm riêng.

---

# Parse Title

```python
def parse_title(self, ctx):

    title = ctx.selector.text(
        "h1"
    )

    if not title:
        raise ParseError(
            "Missing title"
        )

    return title.strip()
```

---

# Parse Author

```python
def parse_author(self, ctx):

    return ctx.selector.text(
        ".author"
    )
```

Nếu website thay đổi selector, chỉ sửa hàm này.

---

# Parse Description

```python
def parse_description(self, ctx):

    html = ctx.selector.html(
        ".summary"
    )

    return clean_html(html)
```

Có thể:

* bỏ quảng cáo
* bỏ `<script>`
* chuẩn hóa `<br>`

---

# Parse Cover

```python
def parse_cover(self, ctx):

    return ctx.selector.attr(
        ".cover img",
        "src"
    )
```

Không download ảnh.

Chỉ lấy URL.

---

# Parse Category

```python
def parse_categories(self, ctx):

    return ctx.selector.texts(
        ".category a"
    )
```

↓

```text
Fantasy

Action

Comedy
```

---

# Parse Status

Website thường ghi:

```text
Completed
```

hoặc

```text
Ongoing
```

Ta chuyển sang Enum.

```python
class BookStatus(Enum):

    COMPLETED = "completed"

    ONGOING = "ongoing"
```

Mapping

```python
STATUS_MAP = {

    "Completed":
        BookStatus.COMPLETED,

    "Ongoing":
        BookStatus.ONGOING
}
```

---

# Parse Language

Tương tự

```text
English

Chinese

Vietnamese
```

↓

```python
Language.ENGLISH
```

---

# Parse Slug

Không lấy từ HTML.

Lấy từ URL.

```text
https://abc.com/book/solo-leveling
```

↓

```text
solo-leveling
```

---

# Parse Metadata

Metadata là dữ liệu phụ.

```python
metadata = {

    "views": "...",

    "rating": "...",

    "votes": "...",

    "publisher": "..."
}
```

Parser chỉ lưu.

Chưa xử lý.

---

# Validator

Sau khi parse

↓

Validate

```python
if not book.title:

    raise ParseError(...)
```

Có thể dùng

```python
BookValidator.validate(book)
```

---

# Normalize

Ví dụ

```text
"  Solo Leveling "
```

↓

```text
"Solo Leveling"
```

Hoặc

```text
"\nAction\n"
```

↓

```text
Action
```

---

# CLI kiểm thử

## Parse Book

```bash
crawler dev parser book \
    novelbin \
    tests/fixtures/book.html
```

Output

```json
{
    "title":"Solo Leveling",
    "author":"Chugong",
    "status":"ongoing"
}
```

---

## Kiểm tra từng trường

```bash
crawler dev parser field \
    title \
    tests/fixtures/book.html
```

↓

```text
Solo Leveling
```

---

```bash
crawler dev parser field \
    author \
    tests/fixtures/book.html
```

↓

```text
Chugong
```

---

## Hiển thị selector

```bash
crawler dev parser debug \
    title \
    tests/fixtures/book.html
```

↓

```text
CSS

h1

↓

Solo Leveling
```

Rất hữu ích khi sửa parser.

---

## Validate

```bash
crawler dev parser validate \
    tests/fixtures/book.html
```

↓

```text
Title

PASS

Author

PASS

Cover

PASS

Description

PASS
```

---

## Snapshot

```bash
crawler dev parser snapshot \
    tests/fixtures/book.html
```

↓

Sinh

```text
tests/

snapshots/

book.json
```

---

## Compare

```bash
crawler dev parser compare \
    tests/fixtures/book.html
```

↓

```text
PASS
```

Nếu website đổi

↓

```text
FAIL

title changed

cover missing
```

---

# Unit Test

```python
def test_title():

    parser = BookParser()

    book = parser.parse(ctx)

    assert book.title == \
        "Solo Leveling"
```

---

```python
def test_author():

    assert book.author == \
        "Chugong"
```

---

```python
def test_categories():

    assert len(
        book.categories
    ) == 3
```

---

# Cấu trúc sau Buổi 10

```text
plugins/

novelbin/

    parser/

        base.py

        book.py

        helpers.py

        mapping.py

        validators.py
```

Book Parser lúc này chỉ khoảng **150–250 dòng**, nhưng được chia thành nhiều phương thức nhỏ, rất dễ bảo trì.

---

# Bài tập

Xây dựng `BookParser` hoàn chỉnh với các phương thức:

* `parse_title()`
* `parse_author()`
* `parse_cover()`
* `parse_description()`
* `parse_categories()`
* `parse_tags()`
* `parse_status()`
* `parse_language()`
* `parse_slug()`
* `parse_metadata()`

Thêm:

* `BookValidator`
* `STATUS_MAP`
* `LANGUAGE_MAP`
* `clean_html()`
* `normalize_text()`

Viết CLI:

```bash
crawler dev parser book <plugin> <html_file>
crawler dev parser field <field> <html_file>
crawler dev parser debug <field> <html_file>
crawler dev parser validate <html_file>
crawler dev parser snapshot <html_file>
crawler dev parser compare <html_file>
```

Viết unit test cho từng phương thức parse riêng lẻ và một bài kiểm thử tổng hợp trên HTML fixture.

---

# Nâng cấp kiến trúc (khuyến nghị)

Đây là điểm tôi khuyên áp dụng ngay để parser có khả năng mở rộng lâu dài.

Thay vì viết:

```python
title = self.parse_title(ctx)
author = self.parse_author(ctx)
cover = self.parse_cover(ctx)
```

hãy xây dựng một **Field Parser**.

```text
BookParser
    │
    ├── TitleFieldParser
    ├── AuthorFieldParser
    ├── CoverFieldParser
    ├── StatusFieldParser
    ├── CategoryFieldParser
    └── DescriptionFieldParser
```

Mỗi `FieldParser` chỉ chịu trách nhiệm cho **một trường dữ liệu** và có thể đăng ký vào `BookParser` thông qua một registry:

```python
book_parser.register("title", TitleFieldParser())
book_parser.register("author", AuthorFieldParser())
```

Ưu điểm:

* Thay đổi cách lấy `title` không ảnh hưởng các trường khác.
* Có thể tái sử dụng `AuthorFieldParser` hoặc `StatusFieldParser` cho nhiều plugin.
* Dễ kiểm thử từng trường độc lập.
* Khi website thay đổi một selector, chỉ cần sửa đúng `FieldParser` tương ứng.

Đây là hướng thiết kế thường thấy trong các framework ETL và crawler quy mô lớn, nơi mỗi trường dữ liệu được xem như một "bộ chuyển đổi" độc lập thay vì một đoạn mã nằm lẫn trong một parser dài hàng trăm dòng.
