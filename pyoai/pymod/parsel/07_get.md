# Khóa học Parsel

# Phần II — Trích xuất dữ liệu

# Buổi 7 — `get()` Deep Dive

Đây là phương thức được sử dụng nhiều nhất trong Parsel.

Trong một parser thực tế, bạn sẽ gọi `get()` hàng trăm hoặc hàng nghìn lần.

Nếu không hiểu rõ `get()`, bạn rất dễ gặp các lỗi như:

* `AttributeError`
* `TypeError`
* `NoneType has no attribute...`
* Parser bị crash khi website thay đổi

Buổi này sẽ đi sâu toàn bộ về `get()`.

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

* `get()` hoạt động như thế nào
* `Selector.get()`
* `SelectorList.get()`
* `default=`
* Khi nào trả về `None`
* Khi nào trả về HTML
* Khi nào trả về text
* Các lỗi phổ biến
* Best Practices

---

# 1. `get()` là gì?

`get()` có nhiệm vụ:

> **Lấy giá trị đầu tiên từ kết quả Selector.**

Ví dụ

```html
<h2>Python</h2>

<h2>Java</h2>

<h2>Rust</h2>
```

```python
titles = sel.css("h2::text")

print(type(titles))
```

```
SelectorList
```

Nếu

```python
titles.get()
```

↓

```
Python
```

Chỉ lấy phần tử đầu tiên.

---

# 2. `SelectorList.get()`

Ví dụ

```python
titles = sel.css("h2::text")
```

Cấu trúc

```
SelectorList

├── Python

├── Java

└── Rust
```

`get()`

↓

```
Python
```

---

# 3. `Selector.get()`

Giả sử

```python
book = sel.css(".book")[0]
```

Kiểu

```python
print(type(book))
```

↓

```
Selector
```

Nếu

```python
book.get()
```

Kết quả

```html
<div class="book">

...

</div>
```

Lưu ý

Đây **không phải text**.

Đây là HTML của node.

---

# 4. So sánh

```python
sel.css(".book").get()
```

↓

HTML của book đầu tiên.

---

```python
sel.css(".book::text").get()
```

↓

Text đầu tiên.

---

```python
sel.css("a::attr(href)").get()
```

↓

href đầu tiên.

---

# 5. Ví dụ trực quan

HTML

```html
<div class="book">

<h2>Python</h2>

</div>
```

```python
book = sel.css(".book")[0]
```

`book.get()`

↓

```html
<div class="book">

<h2>Python</h2>

</div>
```

---

Nếu

```python
book.css("h2::text").get()
```

↓

```
Python
```

---

# 6. Khi không tìm thấy

Ví dụ

```python
title = sel.css("h5::text").get()
```

Không có

```html
<h5>
```

Kết quả

```python
None
```

Đây là nguyên nhân của rất nhiều lỗi.

---

# 7. Vì sao parser crash?

Ví dụ

```python
price = sel.css(".price::text").get()

print(price.strip())
```

Nếu website bỏ giá.

↓

```python
price = None
```

Thì

```python
None.strip()
```

↓

```
AttributeError
```

---

# 8. `default=`

Giải pháp

```python
price = sel.css(".price::text").get(default="")
```

Nếu không có

↓

```
""
```

Không còn

```
None
```

---

Ví dụ

```python
price = sel.css(".price::text").get(default="0")
```

↓

```
0
```

---

# 9. Minh họa

Không dùng default

```python
name = sel.css("h3::text").get()
```

↓

```
None
```

---

Có default

```python
name = sel.css("h3::text").get(default="Unknown")
```

↓

```
Unknown
```

---

# 10. `default` không ghi đè

Ví dụ

```python
title = sel.css("h2::text").get(default="ABC")
```

HTML

```html
<h2>Python</h2>
```

Kết quả

```
Python
```

Không phải

```
ABC
```

`default` chỉ dùng khi **không có kết quả**.

---

# 11. Ví dụ hoàn chỉnh

```python
from parsel import Selector

html = """
<div class="book">

<h2>Python</h2>

</div>
"""

sel = Selector(text=html)

print(sel.css("h2::text").get())

print(sel.css("span::text").get())

print(sel.css("span::text").get(default="Không có"))
```

Kết quả

```
Python

None

Không có
```

---

# 12. `get()` sau CSS

```python
title = book.css("h2::text").get()
```

Đây là cách dùng phổ biến nhất.

---

# 13. `get()` sau XPath

```python
title = book.xpath(".//h2/text()").get()
```

Hoàn toàn giống CSS.

---

# 14. `get()` không chuyển kiểu dữ liệu

Ví dụ

HTML

```html
<span>100</span>
```

```python
price = book.css("span::text").get()

print(type(price))
```

↓

```
str
```

Không phải

```
int
```

Muốn số

```python
price = int(book.css("span::text").get())
```

---

# 15. Parser thực tế

```python
data = {
    "title": book.css("h2::text").get(default=""),
    "price": int(book.css(".price::text").get(default="0")),
    "author": book.css(".author::text").get(default="Unknown"),
    "href": book.css("a::attr(href)").get(default=""),
}
```

Parser sẽ an toàn hơn khi website thiếu dữ liệu.

---

# 16. Sai lầm phổ biến

## Sai lầm 1

```python
book = sel.css(".book").get()

book.css("h2")
```

Sai.

Vì

```python
book
```

đã là

```
str
```

Không còn là `Selector`.

Đúng

```python
book = sel.css(".book")[0]
```

---

## Sai lầm 2

```python
int(sel.css(".price::text").get())
```

Nếu

```
None
```

↓

```
TypeError
```

Đúng

```python
int(sel.css(".price::text").get(default="0"))
```

---

## Sai lầm 3

```python
sel.css(".title::text").get().strip()
```

Nếu không có title.

↓

```
None.strip()
```

Sai.

Đúng

```python
sel.css(".title::text").get(default="").strip()
```

---

# 17. `default` với kiểu dữ liệu

Ví dụ

```python
count = int(sel.css(".count::text").get(default="0"))
```

Không nên

```python
default = 0
```

vì `get()` luôn trả về chuỗi hoặc `None`.

Đúng:

```python
default = "0"
```

rồi chuyển sang `int`.

---

# 18. Chuỗi xử lý an toàn

```python
title = book.css("h2::text").get(default="").strip()
```

```python
author = book.css(".author::text").get(default="Unknown").strip()
```

Đây là phong cách rất phổ biến trong Scrapy.

---

# 19. Ví dụ parser hoàn chỉnh

```python
from parsel import Selector

html = """
<div class="book">

    <h2>
        Python
    </h2>

    <span class="price">100</span>

    <span class="author">
        Alice
    </span>

</div>
"""

sel = Selector(text=html)

book = sel.css(".book")[0]

data = {
    "title": book.css("h2::text").get(default="").strip(),
    "price": int(book.css(".price::text").get(default="0")),
    "author": book.css(".author::text").get(default="").strip(),
}

print(data)
```

Kết quả

```python
{"title": "Python", "price": 100, "author": "Alice"}
```

---

# 20. `get()` với `normalize-space()`

Thay vì:

```python
title = book.xpath(".//h2/text()").get(default="").strip()
```

Có thể để XPath xử lý khoảng trắng:

```python
title = book.xpath("normalize-space(.//h2)").get(default="")
```

Ưu điểm:

* Không cần `.strip()`.
* Xử lý luôn khoảng trắng thừa ở đầu, cuối và giữa các dòng.

---

# 21. So sánh `get()` và `getall()`

| Phương thức      | Kết quả                  |      |
| ---------------- | ------------------------ | ---- |
| `get()`          | Phần tử đầu tiên         |      |
| `getall()`       | Danh sách tất cả phần tử |      |
| Không có kết quả | `None` hoặc `default`    | `[]` |

Ví dụ:

```html
<h2>Python</h2>
<h2>Java</h2>
<h2>Rust</h2>
```

```python
sel.css("h2::text").get()
```

↓

```python
"Python"
```

---

```python
sel.css("h2::text").getall()
```

↓

```python
["Python", "Java", "Rust"]
```

---

# 22. Best Practices

### Luôn dùng `default`

```python
title = book.css("h2::text").get(default="")
```

---

### Chỉ gọi `get()` khi chắc chắn chỉ cần một giá trị

Ví dụ:

* Tiêu đề
* Giá
* Tác giả
* URL chi tiết

Nếu là danh sách:

* Tag
* Thể loại
* Hình ảnh

→ Dùng `getall()`.

---

### Chuyển kiểu sau khi `get()`

```python
price = int(book.css(".price::text").get(default="0"))
```

Không nên:

```python
int(book.css(".price::text"))
```

---

### Không gọi `get()` quá sớm

Đúng:

```python
book = sel.css(".book")[0]
title = book.css("h2::text").get()
```

Sai:

```python
book = sel.css(".book").get()
```

vì bạn sẽ mất khả năng tiếp tục truy vấn trên node đó.

---

# Bài tập

Cho HTML:

```html
<div class="movie">

    <h2>Inception</h2>

    <span class="year">2010</span>

    <span class="rating">8.8</span>

</div>

<div class="movie">

    <h2>Interstellar</h2>

    <span class="year">2014</span>

</div>
```

Hãy viết parser để tạo:

```python
[
    {
        "title": "Inception",
        "year": 2010,
        "rating": 8.8,
    },
    {
        "title": "Interstellar",
        "year": 2014,
        "rating": 0.0,
    },
]
```

Yêu cầu:

1. Sử dụng `get(default=...)` cho mọi trường.
2. Chuyển `year` sang `int`.
3. Chuyển `rating` sang `float`.
4. Không để parser bị lỗi nếu thiếu `<span class="rating">`.

---

# Tổng kết

`get()` là phương thức **lấy một giá trị duy nhất** và là API được dùng nhiều nhất trong Parsel. Khi kết hợp với `default=...`, chuyển kiểu dữ liệu đúng lúc và giữ `Selector` đến bước cuối cùng, bạn sẽ có các parser ổn định ngay cả khi HTML của website thay đổi hoặc thiếu dữ liệu.

Ở **Buổi 8**, chúng ta sẽ học **`getall()`**: cách lấy toàn bộ kết quả, xử lý danh sách dữ liệu (tags, ảnh, chương truyện, liên kết...), hiệu năng, và các mẫu thiết kế parser chuyên nghiệp cho dữ liệu nhiều giá trị.
