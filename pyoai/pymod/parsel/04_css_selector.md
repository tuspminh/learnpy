# Khóa học Parsel

# Buổi 4 — CSS Selector Deep Dive

> Đây là một trong những buổi quan trọng nhất của khóa học.

Khoảng **80–90% crawler thực tế** chỉ cần CSS Selector là đủ. XPath thường chỉ dùng khi CSS không diễn tả được điều kiện cần tìm.

Sau buổi này, bạn sẽ có thể đọc và viết gần như mọi CSS Selector được sử dụng trong các dự án crawler.

---

# Mục tiêu

Bạn sẽ học:

* CSS Selector hoạt động như thế nào
* Các loại selector
* Kết hợp selector
* Pseudo Element của Parsel
* Selector theo attribute
* Selector theo nhiều class
* Selector lồng nhau
* Best Practices

---

# HTML dùng xuyên suốt bài

```html
<html>
<body>

<div class="library">

    <div class="book featured" id="python">

        <h2>Python</h2>

        <span class="price">100</span>

        <a href="/python">Read</a>

    </div>

    <div class="book">

        <h2>Java</h2>

        <span class="price">200</span>

        <a href="/java">Read</a>

    </div>

    <div class="book sale">

        <h2>Rust</h2>

        <span class="price">150</span>

        <a href="/rust">Read</a>

    </div>

</div>

</body>
</html>
```

```python
from parsel import Selector

sel = Selector(text=html)
```

---

# 1. Chọn theo tên thẻ

Ví dụ

```python
sel.css("div")
```

↓

```text
Tất cả thẻ div
```

---

```python
sel.css("h2")
```

↓

```text
Tất cả h2
```

---

# 2. Chọn theo class

CSS

```css
.book
```

Parsel

```python
sel.css(".book")
```

Kết quả

```text
Python

Java

Rust
```

---

# 3. Chọn theo id

CSS

```css
#python
```

Parsel

```python
sel.css("#python")
```

Kết quả

```text
<div id="python"...>
```

---

# 4. Chọn theo nhiều class

HTML

```html
<div class="book featured">
```

CSS

```css
.book.featured
```

Parsel

```python
sel.css(".book.featured")
```

Kết quả

```text
Python
```

Lưu ý

Không có dấu cách.

Sai

```css
.book .featured
```

Điều này có nghĩa là

```text
featured nằm bên trong book
```

Không phải

```text
book có class featured
```

---

# 5. Selector theo con

```css
.book h2
```

↓

```python
sel.css(".book h2")
```

Nghĩa là

```text
h2 bên trong book
```

---

# 6. Selector theo con trực tiếp (`>`)

Ví dụ

```css
.library > .book
```

Nghĩa là

```text
book là con trực tiếp của library
```

Không lấy cháu.

Ví dụ

```html
<div class="library">

    <div class="book">

    </div>

</div>
```

Được.

---

Nếu

```html
<div class="library">

    <section>

        <div class="book">

        </div>

    </section>

</div>
```

Không được.

---

# 7. Chọn nhiều selector

```css
h2, span
```

↓

```python
sel.css("h2, span")
```

Kết quả

```text
Tất cả h2

+

Tất cả span
```

---

# 8. Selector theo Attribute

Ví dụ

```html
<a href="/python">
```

Có thể

```python
sel.css("a[href]")
```

Nghĩa là

```text
mọi a có href
```

---

# 9. Attribute bằng giá trị

```python
sel.css('a[href="/python"]')
```

↓

```text
Read
```

---

# 10. Attribute bắt đầu bằng

```python
sel.css('a[href^="/"]')
```

Ký hiệu

```text
^=
```

nghĩa là

```text
bắt đầu bằng
```

Ví dụ

```text
/abc

/xyz
```

Đều khớp.

---

# 11. Attribute kết thúc bằng

```python
sel.css('img[src$=".jpg"]')
```

↓

```text
chỉ ảnh jpg
```

Ký hiệu

```text
$=
```

↓

```text
endswith
```

---

# 12. Attribute chứa chuỗi

```python
sel.css('a[href*="python"]')
```

Ký hiệu

```text
*=
```

↓

```text
contains
```

Ví dụ

```text
/python

/python/tutorial

abc/python
```

Đều khớp.

---

# 13. Pseudo-element `::text`

Đây là phần mở rộng của Parsel (không phải CSS chuẩn).

Ví dụ

```python
sel.css("h2::text")
```

↓

```python
["Python", "Java", "Rust"]
```

---

Nếu

```python
sel.css("h2")
```

Bạn nhận được

```text
SelectorList
```

Nếu

```python
sel.css("h2::text")
```

Bạn nhận được

```text
Text Node
```

---

# 14. `::attr()`

Ví dụ

```python
sel.css("a::attr(href)")
```

↓

```python
["/python", "/java", "/rust"]
```

---

# 15. Có thể kết hợp

```python
sel.css(".book a::attr(href)")
```

↓

```python
["/python", "/java", "/rust"]
```

---

# 16. Context

Đây là cách viết đẹp.

```python
books = sel.css(".book")

for book in books:
    title = book.css("h2::text").get()

    price = book.css(".price::text").get()
```

Thay vì

```python
sel.css(".book h2")
```

Việc giới hạn phạm vi tìm kiếm giúp parser dễ đọc và ít bị ảnh hưởng nếu cấu trúc HTML thay đổi.

---

# 17. Ví dụ thực tế

HTML

```html
<div class="article">

    <h1>News</h1>

    <a href="/news">Read</a>

    <span class="author">Tom</span>

</div>
```

Parser

```python
article = sel.css(".article")[0]

title = article.css("h1::text").get()

href = article.css("a::attr(href)").get()

author = article.css(".author::text").get()

print(title)

print(href)

print(author)
```

Kết quả

```text
News
/news
Tom
```

---

# 18. CSS Selector kết hợp

Ví dụ

```python
sel.css(".book.sale")
```

↓

```text
book

và

sale
```

---

```python
sel.css(".book .price")
```

↓

```text
price bên trong book
```

---

```python
sel.css(".book>a")
```

↓

```text
a là con trực tiếp
```

---

```python
sel.css(".book h2::text")
```

↓

```text
Text của h2
```

---

# 19. Một số selector hữu ích

| Selector            | Ý nghĩa                     |
| ------------------- | --------------------------- |
| `div`               | Tất cả `<div>`              |
| `.book`             | Class `book`                |
| `#python`           | ID `python`                 |
| `.book h2`          | `h2` nằm trong `.book`      |
| `.book > h2`        | `h2` là con trực tiếp       |
| `a[href]`           | Thẻ `a` có `href`           |
| `a[href^="/"]`      | `href` bắt đầu bằng `/`     |
| `a[href$=".pdf"]`   | `href` kết thúc bằng `.pdf` |
| `a[href*="python"]` | `href` chứa `"python"`      |
| `h2::text`          | Lấy text của `h2`           |
| `a::attr(href)`     | Lấy giá trị `href`          |

---

# 20. CSS và XPath tương đương

| CSS             | XPath                                |
| --------------- | ------------------------------------ |
| `.book`         | `//div[contains(@class,"book")]`     |
| `#python`       | `//*[@id="python"]`                  |
| `.book h2`      | `//div[contains(@class,"book")]//h2` |
| `.book > h2`    | `//div[contains(@class,"book")]/h2`  |
| `a[href]`       | `//a[@href]`                         |
| `a::attr(href)` | `//a/@href`                          |
| `h2::text`      | `//h2/text()`                        |

---

# 21. Hạn chế của CSS trong Parsel

CSS Selector rất mạnh, nhưng không làm được mọi thứ.

Ví dụ, bạn **không thể** chọn phần tử dựa trên nội dung text.

HTML:

```html
<h2>Python</h2>
<h2>Java</h2>
```

Không thể viết:

```css
h2[text()="Python"]
```

Trong trường hợp này, XPath phù hợp hơn:

```python
sel.xpath('//h2[text()="Python"]')
```

Đây là lý do Scrapy và Parsel hỗ trợ cả CSS lẫn XPath.

---

# 22. Best Practices

✅ Ưu tiên chọn theo class hoặc id thay vì phụ thuộc vào vị trí (`div > div > div`), vì cấu trúc HTML thường thay đổi.

✅ Khi đã lấy được một node cha (`book`, `article`, `product`), hãy truy vấn tương đối bên trong node đó.

✅ Sử dụng `::text` và `::attr()` ở bước cuối cùng khi cần lấy dữ liệu dạng chuỗi.

✅ Tránh selector quá dài:

```css
body > div:nth-child(2) > div > ul > li > span
```

Rất dễ hỏng khi website thay đổi giao diện.

---

# 23. Ví dụ hoàn chỉnh

```python
from parsel import Selector

html = """
<div class="library">

    <div class="book featured" id="python">
        <h2>Python</h2>
        <span class="price">100</span>
        <a href="/python">Read</a>
    </div>

    <div class="book">
        <h2>Java</h2>
        <span class="price">200</span>
        <a href="/java">Read</a>
    </div>

    <div class="book sale">
        <h2>Rust</h2>
        <span class="price">150</span>
        <a href="/rust">Read</a>
    </div>

</div>
"""

sel = Selector(text=html)

for book in sel.css(".book"):
    data = {
        "title": book.css("h2::text").get(),
        "price": int(book.css(".price::text").get()),
        "href": book.css("a::attr(href)").get(),
        "featured": "featured" in book.attrib.get("class", "").split(),
        "sale": "sale" in book.attrib.get("class", "").split(),
    }

    print(data)
```

Kết quả:

```python
{"title": "Python", "price": 100, "href": "/python", "featured": True, "sale": False}
{"title": "Java", "price": 200, "href": "/java", "featured": False, "sale": False}
{"title": "Rust", "price": 150, "href": "/rust", "featured": False, "sale": True}
```

---

# Bài tập

Cho HTML:

```html
<div class="catalog">

    <div class="product phone hot" data-id="101">
        <h3>iPhone 16</h3>
        <span class="price">2500</span>
        <img src="/images/iphone.jpg" alt="iPhone">
    </div>

    <div class="product laptop" data-id="102">
        <h3>ThinkPad X1</h3>
        <span class="price">3200</span>
        <img src="/images/thinkpad.png" alt="ThinkPad">
    </div>

    <div class="product phone" data-id="103">
        <h3>Pixel 10</h3>
        <span class="price">1800</span>
        <img src="/images/pixel.jpg" alt="Pixel">
    </div>

</div>
```

Hãy viết parser để:

1. Lấy tất cả `.product`.
2. Chỉ lấy sản phẩm có class `phone`.
3. Chỉ lấy sản phẩm có class `hot`.
4. Lấy `data-id` bằng `::attr(data-id)`.
5. Lấy `src` của các ảnh có đuôi `.jpg`.
6. Trả về:

```python
[
    {
        "id": "101",
        "name": "iPhone 16",
        "price": 2500,
        "image": "/images/iphone.jpg",
        "is_hot": True,
    },
    ...,
]
```

---

## Chuẩn bị cho Buổi 5

Ở **Buổi 5**, chúng ta sẽ học **XPath cơ bản**: cú pháp từ gốc, các trục (`/`, `//`, `.`), điều kiện (`[]`), truy cập thuộc tính (`@attr`), lấy text (`text()`), và cách chuyển đổi giữa CSS Selector và XPath để xử lý những trường hợp CSS không thể biểu diễn được. Đây là kỹ năng rất quan trọng khi crawl các website có cấu trúc HTML phức tạp.
