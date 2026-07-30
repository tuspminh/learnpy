# Khóa học Parsel

# Buổi 6 — XPath nâng cao (Advanced XPath)

Đây là một trong những buổi quan trọng nhất của khóa học.

Sau buổi này, bạn sẽ có thể parser được hầu hết các website thực tế mà CSS Selector không thể xử lý.

---

# Mục tiêu

Sau buổi này bạn sẽ thành thạo:

* `contains()`
* `starts-with()`
* `normalize-space()`
* `string()`
* `last()`
* `position()`
* `and`
* `or`
* `not()`
* XPath Axes
* Các kỹ thuật parser thực tế

---

# HTML dùng xuyên suốt

```html
<html>
<body>

<div class="library">

    <div class="book featured" data-id="101">

        <h2> Python </h2>

        <span class="price">100</span>

        <span class="author">Alice</span>

        <a href="/python">Read</a>

    </div>

    <div class="book sale" data-id="102">

        <h2>Java</h2>

        <span class="price">200</span>

        <span class="author">Bob</span>

        <a href="/java">Read</a>

    </div>

    <div class="book" data-id="103">

        <h2>Rust</h2>

        <span class="price">150</span>

        <span class="author">Tom</span>

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

# 1. contains()

Đây là hàm được dùng nhiều nhất.

Ví dụ

```python
sel.xpath('//div[contains(@class,"book")]')
```

↓

```
book

book featured

book sale
```

---

Có thể tìm theo text

```python
sel.xpath('//h2[contains(text(),"Py")]')
```

↓

```
Python
```

---

# 2. starts-with()

Ví dụ

```python
sel.xpath('//a[starts-with(@href,"/py")]')
```

↓

```
/python
```

---

Một ví dụ khác

```html
<a href="https://example.com">
```

```python
sel.xpath('//a[starts-with(@href,"https")]')
```

↓

```
mọi link https
```

---

# 3. normalize-space()

Website thường có

```html
<h2>

     Python

</h2>
```

Nếu dùng

```python
sel.xpath("//h2/text()").get()
```

ta nhận

```
"\n   Python\n"
```

Dùng

```python
sel.xpath("normalize-space(//h2)")
```

↓

```
Python
```

---

Hoặc

```python
book.xpath("normalize-space(.//h2)")
```

↓

```
Python
```

---

# 4. string()

Giả sử

```html
<div>

Hello

<span>World</span>

</div>
```

Muốn lấy toàn bộ text

```python
sel.xpath("string(//div)")
```

↓

```
Hello World
```

---

# 5. last()

Lấy phần tử cuối

```python
sel.xpath('//div[contains(@class,"book")][last()]')
```

↓

```
Rust
```

---

# 6. position()

Lấy từ phần tử thứ hai trở đi

```python
sel.xpath('//div[contains(@class,"book")][position()>1]')
```

↓

```
Java

Rust
```

---

Lấy hai phần tử đầu

```python
sel.xpath('//div[contains(@class,"book")][position()<3]')
```

↓

```
Python

Java
```

---

# 7. and

Ví dụ

```python
sel.xpath('//div[contains(@class,"book") and contains(@class,"featured")]')
```

↓

```
Python
```

---

# 8. or

```python
sel.xpath('//div[contains(@class,"featured") or contains(@class,"sale")]')
```

↓

```
Python

Java
```

---

# 9. not()

Lấy mọi book không sale

```python
sel.xpath('//div[contains(@class,"book") and not(contains(@class,"sale"))]')
```

↓

```
Python

Rust
```

---

# 10. Axes

Đây là sức mạnh lớn nhất của XPath.

```
parent

child

ancestor

descendant

following-sibling

preceding-sibling
```

---

# 11. parent

HTML

```html
<div class="book">

    <h2>Python</h2>

</div>
```

Parser

```python
sel.xpath("//h2/parent::div")
```

↓

```
div.book
```

---

# 12. child

```python
sel.xpath("//div/child::h2")
```

↓

```
mọi h2 là con trực tiếp
```

---

# 13. descendant

```python
sel.xpath("//div/descendant::span")
```

↓

```
mọi span bên trong div
```

Giống

```python
//div//span
```

---

# 14. ancestor

Ví dụ

```python
sel.xpath("//h2/ancestor::div")
```

↓

```
mọi div cha
```

Hoặc

```python
sel.xpath("//h2/ancestor::*")
```

↓

```
mọi node cha
```

---

# 15. following-sibling

HTML

```html
<h2>Python</h2>

<span>100</span>
```

Parser

```python
sel.xpath("//h2/following-sibling::span")
```

↓

```
100
```

---

# 16. preceding-sibling

HTML

```html
<span>100</span>

<a>Read</a>
```

Parser

```python
sel.xpath("//a/preceding-sibling::span")
```

↓

```
100
```

---

# 17. Kết hợp nhiều điều kiện

```python
sel.xpath("""
//div[
contains(@class,"book")
and
@data-id="101"
]
""")
```

↓

```
Python
```

---

# 18. Parser thực tế

```python
books = sel.xpath('//div[contains(@class,"book")]')

for book in books:
    data = {
        "id": book.xpath("./@data-id").get(),
        "title": book.xpath("normalize-space(.//h2)").get(),
        "price": int(book.xpath(".//span[@class='price']/text()").get()),
        "author": book.xpath(".//span[@class='author']/text()").get(),
        "href": book.xpath(".//a/@href").get(),
        "featured": bool(book.xpath('contains(@class,"featured")').get()),
    }

    print(data)
```

Kết quả

```python
{"101", "Python", 100, "Alice", "/python", True}
```

---

# 19. Một lưu ý quan trọng về `contains(@class, ...)`

Rất nhiều hướng dẫn trên Internet viết:

```xpath
contains(@class, "book")
```

Điều này **có thể sai**.

Ví dụ

```html
<div class="ebook">
```

thì

```xpath
contains(@class,"book")
```

vẫn trả về **True** vì `"ebook"` chứa chuỗi `"book"`.

Cách an toàn hơn là:

```xpath
contains(concat(" ", normalize-space(@class), " "), " book ")
```

Ví dụ:

```python
sel.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " book ")]')
```

Đây là kỹ thuật được dùng trong nhiều dự án XPath chuyên nghiệp để kiểm tra chính xác một class.

---

# 20. Một số hàm XPath hữu ích khác

## `count()`

Đếm số node:

```python
sel.xpath("count(//div)").get()
```

Kết quả:

```
4
```

---

## `name()`

Lấy tên thẻ:

```python
sel.xpath("name(//h2)").get()
```

↓

```
h2
```

---

## `boolean()`

Kiểm tra có tồn tại node hay không:

```python
sel.xpath("boolean(//div[@id='python'])").get()
```

↓

```
1
```

Nếu không tồn tại:

```
0
```

---

# 21. CSS hay XPath?

| Nhu cầu           | CSS   | XPath |
| ----------------- | ----- | ----- |
| Chọn theo class   | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐  |
| Chọn theo id      | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐  |
| Chọn theo text    | ❌     | ⭐⭐⭐⭐⭐ |
| Chọn theo vị trí  | ⭐⭐    | ⭐⭐⭐⭐⭐ |
| Di chuyển lên cha | ❌     | ⭐⭐⭐⭐⭐ |
| Sibling           | ❌     | ⭐⭐⭐⭐⭐ |
| Hàm xử lý chuỗi   | ❌     | ⭐⭐⭐⭐⭐ |
| Logic and/or      | ⭐⭐    | ⭐⭐⭐⭐⭐ |

---

# 22. Best Practices

### Luôn dùng Relative XPath trong vòng lặp

Đúng:

```python
for book in books:
    title = book.xpath(".//h2/text()").get()
```

Sai:

```python
for book in books:
    title = book.xpath("//h2/text()").get()
```

---

### Dùng `normalize-space()` khi lấy text

Thay vì

```python
book.xpath(".//h2/text()").get()
```

hãy dùng

```python
book.xpath("normalize-space(.//h2)").get()
```

---

### Kiểm tra class an toàn

Thay vì

```xpath
contains(@class,"book")
```

hãy dùng

```xpath
contains(concat(" ", normalize-space(@class), " "), " book ")
```

---

### Chỉ chuyển sang `str` ở cuối

Đúng:

```python
book.xpath(".//a/@href").get()
```

Không nên gọi `.get()` quá sớm rồi mới tiếp tục xử lý XPath.

---

# 23. Ví dụ hoàn chỉnh

```python
from parsel import Selector

html = """
<div class="library">

    <div class="book featured" data-id="101">
        <h2>
            Python
        </h2>
        <span class="price">100</span>
        <span class="author">Alice</span>
        <a href="/python">Read</a>
    </div>

    <div class="book sale" data-id="102">
        <h2>Java</h2>
        <span class="price">200</span>
        <span class="author">Bob</span>
        <a href="/java">Read</a>
    </div>

</div>
"""

sel = Selector(text=html)

for book in sel.xpath(
    '//div[contains(concat(" ", normalize-space(@class), " "), " book ")]'
):
    data = {
        "id": book.xpath("./@data-id").get(),
        "title": book.xpath("normalize-space(.//h2)").get(),
        "price": int(book.xpath(".//span[@class='price']/text()").get()),
        "author": book.xpath(".//span[@class='author']/text()").get(),
        "href": book.xpath(".//a/@href").get(),
        "is_featured": "featured" in book.attrib.get("class", "").split(),
    }

    print(data)
```

Kết quả:

```python
{
    "id": "101",
    "title": "Python",
    "price": 100,
    "author": "Alice",
    "href": "/python",
    "is_featured": True,
}

{
    "id": "102",
    "title": "Java",
    "price": 200,
    "author": "Bob",
    "href": "/java",
    "is_featured": False,
}
```

---

# Bài tập

Cho HTML:

```html
<div class="products">

    <div class="product hot" data-id="201">
        <h3>iPhone 16</h3>
        <span class="brand">Apple</span>
        <span class="price">2500</span>
    </div>

    <div class="product" data-id="202">
        <h3>Galaxy S26</h3>
        <span class="brand">Samsung</span>
        <span class="price">2200</span>
    </div>

    <div class="product sale" data-id="203">
        <h3>Pixel 10</h3>
        <span class="brand">Google</span>
        <span class="price">1800</span>
    </div>

</div>
```

Hãy viết các truy vấn XPath để:

1. Lấy tất cả sản phẩm bằng cách kiểm tra class an toàn (`concat + normalize-space`).
2. Lấy sản phẩm có `data-id="202"`.
3. Lấy sản phẩm đầu tiên, cuối cùng và hai sản phẩm đầu.
4. Lấy sản phẩm có class `hot` hoặc `sale`.
5. Lấy mọi sản phẩm **không** có class `sale`.
6. Từ mỗi sản phẩm, dùng Relative XPath để tạo:

```python
[
    {
        "id": "201",
        "name": "iPhone 16",
        "brand": "Apple",
        "price": 2500,
        "is_hot": True,
        "is_sale": False,
    },
    ...,
]
```

---

## Lộ trình tiếp theo

Từ buổi sau, chúng ta chuyển sang **Phần II – Trích xuất dữ liệu**, tập trung vào các API mà bạn sẽ dùng hàng ngày trong Parsel:

* **Buổi 7:** `get()` và `get(default=...)`
* **Buổi 8:** `getall()`
* **Buổi 9:** `re()` và Regex trong Parsel
* **Buổi 10:** `re_first()`
* **Buổi 11:** `attrib`
* **Buổi 12:** `namespaces` (làm việc với XML và RSS Feed)

Đến cuối Phần II, bạn sẽ nắm vững toàn bộ các phương thức trích xuất dữ liệu quan trọng của `parsel.Selector` và `SelectorList`, đủ để xây dựng parser cho hầu hết các website thực tế.
