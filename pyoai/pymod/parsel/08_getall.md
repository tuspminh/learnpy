# Khóa học Parsel

# Phần II — Trích xuất dữ liệu

# Buổi 8 — `getall()` Deep Dive

Trong buổi trước chúng ta học:

```python
.get()
```

để lấy **một** kết quả.

Hôm nay sẽ học:

```python
.getall()
```

để lấy **toàn bộ** kết quả.

Đây là API quan trọng thứ hai sau `get()`.

Trong thực tế, `getall()` được dùng để lấy:

* danh sách ảnh
* danh sách tag
* danh sách thể loại
* danh sách chương
* danh sách link
* danh sách tác giả
* danh sách bình luận
* danh sách tập phim
* ...

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

* `getall()` hoạt động thế nào
* `SelectorList.getall()`
* Khi nào dùng
* Khi nào KHÔNG dùng
* `get()` vs `getall()`
* Parser thực tế
* Best Practices

---

# HTML dùng xuyên suốt

```html
<div class="book">

    <h2>Python Deep Dive</h2>

    <ul class="tags">

        <li>Python</li>

        <li>Programming</li>

        <li>Backend</li>

    </ul>

    <div class="images">

        <img src="1.jpg">

        <img src="2.jpg">

        <img src="3.jpg">

    </div>

</div>
```

```python
from parsel import Selector

sel = Selector(text=html)
```

---

# 1. `getall()` là gì?

Nếu

```python
sel.css("li::text")
```

↓

```
SelectorList
```

thì

```python
sel.css("li::text").getall()
```

↓

```python
["Python", "Programming", "Backend"]
```

Nó trả về **list[str]**.

---

# 2. Kiểu dữ liệu

```python
tags = sel.css("li::text").getall()

print(type(tags))
```

↓

```python
<class 'list'>
```

Không còn là

```
SelectorList
```

Mà là list Python thông thường.

---

# 3. So sánh

```python
sel.css("li::text")
```

↓

```
SelectorList
```

---

```python
sel.css("li::text").get()
```

↓

```python
"Python"
```

---

```python
sel.css("li::text").getall()
```

↓

```python
["Python", "Programming", "Backend"]
```

---

# 4. Ví dụ trực quan

```
SelectorList

├── Python

├── Programming

└── Backend
```

`get()`

↓

```
Python
```

---

`getall()`

↓

```
[
Python,
Programming,
Backend
]
```

---

# 5. Lấy nhiều href

HTML

```html
<a href="/python"></a>

<a href="/java"></a>

<a href="/rust"></a>
```

```python
links = sel.css("a::attr(href)").getall()

print(links)
```

↓

```python
["/python", "/java", "/rust"]
```

---

# 6. Lấy nhiều ảnh

```html
<img src="1.jpg">

<img src="2.jpg">

<img src="3.jpg">
```

```python
images = sel.css("img::attr(src)").getall()
```

↓

```python
["1.jpg", "2.jpg", "3.jpg"]
```

---

# 7. Lấy nhiều text

```html
<li>One</li>

<li>Two</li>

<li>Three</li>
```

```python
items = sel.css("li::text").getall()
```

↓

```python
["One", "Two", "Three"]
```

---

# 8. Nếu không có kết quả

```python
result = sel.css(".author::text").getall()

print(result)
```

↓

```python
[]
```

Không phải

```python
None
```

Đây là điểm khác với `get()`.

---

# 9. So sánh

`get()`

```python
None
```

---

`getall()`

```python
[]
```

---

# 10. Vì sao điều này tốt?

Bạn có thể

```python
for tag in tags:
```

Nếu

```python
tags = []
```

thì vòng lặp không chạy.

Không bị lỗi.

---

Trong khi

```python
tags = None
```

↓

```python
for tag in None:
```

↓

```
TypeError
```

---

# 11. Parser thực tế

```python
book = sel.css(".book")[0]

data = {
    "title": book.css("h2::text").get(),
    "tags": book.css("li::text").getall(),
    "images": book.css("img::attr(src)").getall(),
}

print(data)
```

↓

```python
{
    "title": "Python Deep Dive",
    "tags": ["Python", "Programming", "Backend"],
    "images": ["1.jpg", "2.jpg", "3.jpg"],
}
```

---

# 12. `getall()` không có `default`

Đây là điều nhiều người thắc mắc.

Sai

```python
sel.css("li").getall(default=[])
```

Không tồn tại.

Vì

```python
getall()
```

luôn trả

```python
[]
```

nếu không có dữ liệu.

Không cần `default`.

---

# 13. Kết hợp list comprehension

Ví dụ

```python
tags = [tag.strip() for tag in sel.css("li::text").getall()]
```

↓

```python
["Python", "Programming", "Backend"]
```

---

# 14. Loại bỏ chuỗi rỗng

HTML

```html
<li>

Python

</li>

<li>

</li>

<li>

Java

</li>
```

```python
tags = [x.strip() for x in sel.css("li::text").getall() if x.strip()]
```

↓

```python
["Python", "Java"]
```

---

# 15. Chuyển kiểu dữ liệu

```html
<span>100</span>

<span>200</span>

<span>300</span>
```

```python
prices = [int(x) for x in sel.css("span::text").getall()]
```

↓

```python
[100, 200, 300]
```

---

# 16. XPath

Hoàn toàn giống CSS.

```python
authors = book.xpath(".//span/text()").getall()
```

↓

```python
["Alice", "Bob", "Tom"]
```

---

# 17. `getall()` với Selector

Lưu ý.

Nếu

```python
books = sel.css(".book")
```

thì

```python
books.getall()
```

↓

```python
["<div>...</div>", "<div>...</div>", "<div>...</div>"]
```

Đây là HTML.

Không phải text.

---

# 18. Khi nào dùng `get()`?

Ví dụ

```python
title
```

↓

Một giá trị.

```python
book.css("h2::text").get()
```

---

```python
price
```

↓

Một giá trị.

```python
book.css(".price::text").get()
```

---

# 19. Khi nào dùng `getall()`?

Ví dụ

```python
tags
```

↓

Nhiều giá trị.

---

```python
categories
```

↓

Nhiều giá trị.

---

```python
authors
```

↓

Nhiều giá trị.

---

```python
images
```

↓

Nhiều giá trị.

---

```python
chapters
```

↓

Nhiều giá trị.

---

```python
comments
```

↓

Nhiều giá trị.

---

# 20. Sai lầm phổ biến

## Sai lầm 1

```python
title = book.css("h2::text").getall()
```

↓

```python
["Python"]
```

Sau đó

```python
title.upper()
```

↓

```
AttributeError
```

Vì

```python
title
```

là list.

---

## Sai lầm 2

```python
tags = book.css("li::text").get()

for tag in tags:
```

↓

```
P
y
t
h
o
n
```

Vì

```python
tags
```

là string.

Không phải list.

Đúng

```python
tags = book.css("li::text").getall()
```

---

## Sai lầm 3

```python
len(book.css("li::text").get())
```

Nếu

```python
Python
```

↓

```
6
```

Bạn đang đếm số ký tự.

Không phải số tag.

Đúng

```python
len(book.css("li::text").getall())
```

↓

```
3
```

---

# 21. Parser crawler truyện

HTML

```html
<ul class="genres">

<li>Tiên Hiệp</li>

<li>Huyền Huyễn</li>

<li>Hệ Thống</li>

</ul>
```

Parser

```python
genres = [x.strip() for x in book.css(".genres li::text").getall()]
```

↓

```python
["Tiên Hiệp", "Huyền Huyễn", "Hệ Thống"]
```

---

# 22. Parser nhiều ảnh

```python
images = [src for src in book.css(".gallery img::attr(src)").getall()]
```

↓

```python
["a.jpg", "b.jpg", "c.jpg"]
```

---

# 23. Parser nhiều chương

```python
chapters = []

for a in sel.css(".chapter a"):
    chapters.append(
        {"title": a.css("::text").get(), "href": a.css("::attr(href)").get()}
    )
```

↓

```python
[{"title": "Chapter 1", "href": "..."}, ...]
```

---

# 24. Hiệu năng

`getall()` chỉ chuyển đổi các phần tử trong `SelectorList` thành danh sách chuỗi một lần.

Nếu bạn cần xử lý tất cả kết quả, hãy gọi `getall()` **một lần** rồi làm việc trên list:

```python
texts = sel.css("li::text").getall()

cleaned = [t.strip() for t in texts]
```

Thay vì lặp nhiều lần và gọi lại cùng một selector.

---

# 25. So sánh `get()` và `getall()`

| Tiêu chí         | `get()`           | `getall()`  |
| ---------------- | ----------------- | ----------- |
| Kiểu trả về      | `str` hoặc `None` | `list[str]` |
| Không có dữ liệu | `None`            | `[]`        |
| Có `default=`    | ✔                 | ✘           |
| Một giá trị      | ✔                 | ✘           |
| Nhiều giá trị    | ✘                 | ✔           |

---

# 26. Best Practices

### Dùng `get()` cho

* tiêu đề
* giá
* URL chi tiết
* tên tác giả
* ngày đăng

---

### Dùng `getall()` cho

* ảnh
* tags
* thể loại
* chương
* liên kết
* bình luận
* danh sách tập

---

### Làm sạch dữ liệu ngay sau `getall()`

```python
tags = [t.strip() for t in book.css(".tags li::text").getall() if t.strip()]
```

---

### Chuyển kiểu dữ liệu sau khi lấy danh sách

```python
scores = [float(s) for s in sel.css(".score::text").getall()]
```

---

### Không dùng `getall()` nếu bạn chỉ cần một giá trị

Thay vì:

```python
title = book.css("h2::text").getall()[0]
```

Hãy viết:

```python
title = book.css("h2::text").get()
```

Ngắn gọn hơn, an toàn hơn và thể hiện rõ ý định của mã nguồn.

---

# 27. Ví dụ hoàn chỉnh

```python
from parsel import Selector

html = """
<div class="book">
    <h2>Python Deep Dive</h2>

    <ul class="tags">
        <li> Python </li>
        <li> Programming </li>
        <li> Backend </li>
    </ul>

    <div class="gallery">
        <img src="1.jpg">
        <img src="2.jpg">
        <img src="3.jpg">
    </div>
</div>
"""

sel = Selector(text=html)

book = sel.css(".book")[0]

data = {
    "title": book.css("h2::text").get(default="").strip(),
    "tags": [t.strip() for t in book.css(".tags li::text").getall() if t.strip()],
    "images": book.css(".gallery img::attr(src)").getall(),
}

print(data)
```

Kết quả:

```python
{
    "title": "Python Deep Dive",
    "tags": ["Python", "Programming", "Backend"],
    "images": ["1.jpg", "2.jpg", "3.jpg"],
}
```

---

# Bài tập

Cho HTML:

```html
<div class="movie">

    <h2>Interstellar</h2>

    <ul class="actors">
        <li>Matthew McConaughey</li>
        <li>Anne Hathaway</li>
        <li>Jessica Chastain</li>
    </ul>

    <div class="screenshots">
        <img src="1.jpg">
        <img src="2.jpg">
        <img src="3.jpg">
    </div>

</div>
```

Hãy viết parser để tạo:

```python
{
    "title": "Interstellar",
    "actors": [
        "Matthew McConaughey",
        "Anne Hathaway",
        "Jessica Chastain",
    ],
    "screenshots": [
        "1.jpg",
        "2.jpg",
        "3.jpg",
    ],
}
```

Yêu cầu:

1. Dùng `get()` cho `title`.
2. Dùng `getall()` cho `actors`.
3. Dùng `getall()` cho `screenshots`.
4. Loại bỏ khoảng trắng thừa trong danh sách diễn viên.
5. Nếu không có diễn viên hoặc ảnh, kết quả vẫn phải là danh sách rỗng `[]`.

---

## Tổng kết

Quy tắc ghi nhớ đơn giản:

* **Một giá trị** → `get()`
* **Nhiều giá trị** → `getall()`

Trong các parser chuyên nghiệp, bạn sẽ thấy hai phương thức này xuất hiện ở hầu hết mọi hàm trích xuất dữ liệu.

Ở **Buổi 9**, chúng ta sẽ học **`re()`**: cách kết hợp biểu thức chính quy (Regular Expressions) với Parsel để trích xuất dữ liệu từ text hoặc HTML khi CSS và XPath không đủ linh hoạt, chẳng hạn như lấy mã sản phẩm, giá tiền, số chương, URL động hoặc dữ liệu nhúng trong JavaScript.
