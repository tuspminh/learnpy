# Khóa học Parsel

# Buổi 5 — XPath cơ bản (Foundation)

Trong thực tế, nếu CSS Selector giải quyết được khoảng **80–90%** nhu cầu thì **XPath** sẽ xử lý gần như toàn bộ các trường hợp còn lại.

XPath mạnh hơn CSS ở chỗ:

* Chọn theo nội dung text
* Chọn theo vị trí
* Di chuyển lên node cha
* Điều kiện phức tạp
* Logic AND/OR
* Hàm xử lý chuỗi

Đây là lý do gần như mọi crawler chuyên nghiệp đều biết cả CSS và XPath.

---

# Mục tiêu

Sau buổi này bạn sẽ biết:

* XPath là gì
* Cấu trúc cú pháp
* `/`, `//`, `.`
* `text()`
* `@attribute`
* Điều kiện `[]`
* Vị trí `[1]`, `[last()]`
* Relative XPath

---

# HTML sử dụng

```html
<html>
<body>

<div class="library">

    <div class="book" id="python">

        <h2>Python</h2>

        <span class="price">100</span>

        <a href="/python">Read</a>

    </div>

    <div class="book">

        <h2>Java</h2>

        <span class="price">200</span>

        <a href="/java">Read</a>

    </div>

    <div class="book">

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

# 1. XPath là gì?

XPath là ngôn ngữ dùng để **định vị node trong cây XML/HTML**.

Hãy tưởng tượng DOM:

```
html

└── body

      └── div.library

             ├── div.book

             │      ├── h2

             │      ├── span

             │      └── a

             ├── div.book

             └── div.book
```

XPath giống như một con đường đi trong cây này.

---

# 2. Chọn theo tên thẻ

```python
sel.xpath("//h2")
```

↓

```
Tất cả h2
```

---

```python
sel.xpath("//div")
```

↓

```
Tất cả div
```

---

# 3. Dấu `//`

Đây là ký hiệu được dùng nhiều nhất.

```
//
```

nghĩa là

> tìm ở mọi cấp.

Ví dụ

```python
sel.xpath("//span")
```

↓

```
mọi span
```

không cần biết nằm sâu bao nhiêu.

---

# 4. Dấu `/`

```
/
```

nghĩa là

> con trực tiếp.

Ví dụ

```
html

└── body

      └── div
```

XPath

```python
/html/body/div
```

Chỉ lấy div là con trực tiếp.

---

# 5. So sánh

```
/body/div
```

↓

```
div là con
```

---

```
/body//div
```

↓

```
mọi div bên trong body
```

---

# 6. Chọn theo attribute

Ví dụ

```html
<div id="python">
```

XPath

```python
sel.xpath('//*[@id="python"]')
```

Giải thích

```
*

↓

mọi tag
```

```
[@id="python"]

↓

attribute id
```

---

# 7. Chọn theo class

```python
sel.xpath('//*[@class="book"]')
```

Lưu ý:

Điều này chỉ đúng nếu class đúng bằng

```
book
```

Nếu HTML

```html
<div class="book featured">
```

thì không khớp.

---

# 8. contains()

Đây là cách phổ biến.

```python
sel.xpath('//div[contains(@class,"book")]')
```

↓

```
book

book featured

book sale
```

Đều được.

---

# 9. Lấy text

Ví dụ

```python
sel.xpath("//h2/text()")
```

↓

```python
["Python", "Java", "Rust"]
```

---

Nếu

```python
sel.xpath("//h2")
```

thì nhận

```
SelectorList
```

Nếu

```python
sel.xpath("//h2/text()")
```

thì nhận

```
Text Node
```

---

# 10. Lấy attribute

Ví dụ

```python
sel.xpath("//a/@href")
```

↓

```python
["/python", "/java", "/rust"]
```

---

# 11. Điều kiện `[]`

Ví dụ

```python
sel.xpath('//div[@id="python"]')
```

↓

```
chỉ div có id python
```

---

Có thể

```python
sel.xpath('//a[@href="/java"]')
```

↓

```
chỉ link java
```

---

# 12. Vị trí

Lấy quyển đầu

```python
sel.xpath("//div[@class='book'][1]")
```

---

Quyển cuối

```python
sel.xpath("//div[@class='book'][last()]")
```

---

Quyển thứ hai

```python
sel.xpath("//div[@class='book'][2]")
```

⚠ Lưu ý: **XPath đánh số từ 1**, không phải từ 0.

---

# 13. Relative XPath

Giả sử

```python
books = sel.css(".book")
```

Lặp

```python
for book in books:
```

Muốn lấy tiêu đề

Đúng

```python
book.xpath(".//h2/text()")
```

Sai

```python
book.xpath("//h2/text()")
```

---

# 14. Dấu `.`

```
.
```

nghĩa là

```
node hiện tại
```

Ví dụ

```python
book.xpath(".//span/text()")
```

↓

```
span bên trong book
```

---

# 15. So sánh

```
book.xpath("//span")
```

↓

```
toàn document
```

---

```
book.xpath(".//span")
```

↓

```
chỉ trong book
```

---

# 16. Ví dụ hoàn chỉnh

```python
for book in sel.xpath('//div[contains(@class,"book")]'):
    title = book.xpath(".//h2/text()").get()

    price = book.xpath(".//span/text()").get()

    href = book.xpath(".//a/@href").get()

    print(title, price, href)
```

Kết quả

```
Python 100 /python

Java 200 /java

Rust 150 /rust
```

---

# 17. CSS ↔ XPath

| CSS             | XPath                                |
| --------------- | ------------------------------------ |
| `.book`         | `//div[contains(@class,"book")]`     |
| `#python`       | `//*[@id="python"]`                  |
| `h2`            | `//h2`                               |
| `h2::text`      | `//h2/text()`                        |
| `a::attr(href)` | `//a/@href`                          |
| `.book h2`      | `//div[contains(@class,"book")]//h2` |
| `.book > h2`    | `//div[contains(@class,"book")]/h2`  |

---

# 18. Những lỗi phổ biến

## Lỗi 1: So sánh class bằng `=`

```python
sel.xpath('//div[@class="book"]')
```

Nếu HTML:

```html
<div class="book featured">
```

→ Không khớp.

Đúng:

```python
sel.xpath('//div[contains(@class,"book")]')
```

---

## Lỗi 2: Quên dấu `.`

```python
for book in books:
    book.xpath("//a/@href")
```

Kết quả

```
Mọi href trong tài liệu
```

Đúng

```python
book.xpath(".//a/@href")
```

---

## Lỗi 3: Nhầm chỉ số

Sai

```python
sel.xpath("//div[0]")
```

XPath không có chỉ số 0.

Đúng

```python
sel.xpath("//div[1]")
```

---

# 19. Ví dụ thực tế

HTML

```html
<div class="product">
    <h3>ThinkPad X1</h3>
    <span class="price">3200</span>
    <img src="/img/x1.jpg">
</div>
```

Parser

```python
product = sel.xpath('//div[contains(@class,"product")]')[0]

data = {
    "name": product.xpath(".//h3/text()").get(),
    "price": int(product.xpath(".//span/text()").get()),
    "image": product.xpath(".//img/@src").get(),
}

print(data)
```

Kết quả

```python
{
    "name": "ThinkPad X1",
    "price": 3200,
    "image": "/img/x1.jpg",
}
```

---

# 20. Best Practices

✅ Dùng CSS khi selector đơn giản và dễ đọc.

✅ Dùng XPath khi cần:

* chọn theo text
* chọn theo vị trí
* điều kiện phức tạp
* di chuyển trong cây DOM

✅ Trong vòng lặp, luôn dùng Relative XPath (`.//`).

✅ Với class, ưu tiên `contains(@class, "...")` thay vì `@class="..."` nếu website có nhiều class trên cùng một phần tử.

---

# 21. CSS hay XPath?

| Tiêu chí                | CSS   | XPath |
| ----------------------- | ----- | ----- |
| Dễ đọc                  | ⭐⭐⭐⭐⭐ | ⭐⭐⭐   |
| Nhanh để viết           | ⭐⭐⭐⭐⭐ | ⭐⭐⭐   |
| Chọn theo class/id      | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐  |
| Chọn theo text          | ❌     | ⭐⭐⭐⭐⭐ |
| Chọn theo vị trí        | ⭐⭐    | ⭐⭐⭐⭐⭐ |
| Điều hướng lên node cha | ❌     | ⭐⭐⭐⭐⭐ |
| Điều kiện logic         | ⭐⭐    | ⭐⭐⭐⭐⭐ |

Trong các dự án crawler lớn, nhiều lập trình viên sử dụng CSS cho các truy vấn đơn giản và chuyển sang XPath khi cần biểu thức mạnh hơn.

---

# Bài tập

Cho HTML:

```html
<div class="catalog">

    <div class="product featured" data-id="101">
        <h3>iPhone 16</h3>
        <span class="price">2500</span>
        <a href="/iphone16">Chi tiết</a>
    </div>

    <div class="product" data-id="102">
        <h3>Galaxy S26</h3>
        <span class="price">2200</span>
        <a href="/galaxys26">Chi tiết</a>
    </div>

    <div class="product sale" data-id="103">
        <h3>Pixel 10</h3>
        <span class="price">1800</span>
        <a href="/pixel10">Chi tiết</a>
    </div>

</div>
```

Hãy viết các truy vấn XPath để:

1. Lấy tất cả sản phẩm.
2. Lấy tên của tất cả sản phẩm.
3. Lấy tất cả `href`.
4. Lấy sản phẩm đầu tiên và cuối cùng.
5. Chỉ lấy sản phẩm có class `featured`.
6. Duyệt từng sản phẩm bằng Relative XPath và tạo:

```python
[
    {
        "id": "101",
        "name": "iPhone 16",
        "price": 2500,
        "href": "/iphone16",
    },
    ...,
]
```

---

## Chuẩn bị cho Buổi 6

Ở **Buổi 6**, chúng ta sẽ học **XPath nâng cao**: các hàm `contains()`, `starts-with()`, `normalize-space()`, toán tử `and`/`or`, các trục (Axes) như `parent`, `ancestor`, `following-sibling`, `preceding-sibling`, cùng các kỹ thuật xử lý HTML phức tạp thường gặp trong các website thương mại điện tử, diễn đàn và trang tin tức. Đây là phần giúp bạn khai thác tối đa sức mạnh của XPath trong Parsel.
