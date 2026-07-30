# Khóa học Parsel

# Phần II — Trích xuất dữ liệu

# Buổi 10 — `re_first()` Deep Dive

Đến thời điểm này, chúng ta đã học:

* `get()`
* `getall()`
* `re()`

Có một vấn đề rất thường gặp với `re()`:

```python
price = book.css(".price::text").re(r"\d+")

print(price)
```

Kết quả:

```python
["150"]
```

Muốn lấy số:

```python
price = int(price[0])
```

Hoặc

```python
price = int(price[0]) if price else 0
```

Việc này lặp đi lặp lại rất nhiều.

Parsel cung cấp một API tiện hơn:

```python
.re_first()
```

Đây là phương thức được dùng rất nhiều trong các project Scrapy lớn.

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

* `re_first()`
* Sự khác nhau giữa `re()` và `re_first()`
* `default=`
* Capture Group
* Regex thực tế
* Best Practices

---

# 1. `re_first()` là gì?

`re_first()` thực hiện:

> Áp dụng Regex và chỉ trả về kết quả đầu tiên.

Ví dụ

HTML

```html
<span>

Price: 150 USD

</span>
```

Parser

```python
sel.css("span::text").re_first(r"\d+")
```

↓

```python
"150"
```

Không phải

```python
["150"]
```

---

# 2. So sánh

`re()`

```python
sel.css("span::text").re(r"\d+")
```

↓

```python
["150"]
```

---

`re_first()`

```python
sel.css("span::text").re_first(r"\d+")
```

↓

```python
"150"
```

---

# 3. HTML mẫu

```html
<div class="book">

<h2>Python</h2>

<span class="price">

Price: 150 USD

</span>

</div>
```

```python
book = sel.css(".book")[0]
```

---

# 4. Ví dụ đầu tiên

```python
price = book.css(".price::text").re_first(r"\d+")

print(price)
```

↓

```python
"150"
```

---

# 5. Kiểu dữ liệu

```python
price = book.css(".price::text").re_first(r"\d+")

print(type(price))
```

↓

```python
<class 'str'>
```

Không phải

```python
list
```

---

# 6. Không có kết quả

```python
book.css("h2::text").re_first(r"\d+")
```

↓

```python
None
```

Khác với

```python
.re()
```

↓

```python
[]
```

---

# 7. `default=`

Giống `get()`.

Ví dụ

```python
price = book.css(".price::text").re_first(r"\d+", default="0")
```

Nếu không có

↓

```python
"0"
```

Không phải

```python
None
```

---

# 8. Ví dụ

HTML

```html
<span>

Không có giá

</span>
```

Parser

```python
price = sel.css("span::text").re_first(r"\d+", default="0")

print(price)
```

↓

```python
"0"
```

---

# 9. Capture Group

HTML

```html
<span>

Price: 150 USD

</span>
```

Regex

```python
r"Price:\s*(\d+)"
```

```python
book.css(".price::text").re_first(r"Price:\s*(\d+)")
```

↓

```python
"150"
```

---

# 10. Không có Capture Group

```python
book.css(".price::text").re_first(r"Price:\s*\d+")
```

↓

```python
"Price: 150"
```

---

# 11. Nhiều kết quả

HTML

```html
<span>

100

200

300

</span>
```

```python
sel.css("span::text").re_first(r"\d+")
```

↓

```python
"100"
```

Chỉ lấy kết quả đầu tiên.

---

# 12. Parser giá tiền

HTML

```html
<span>

Giá: 1.250.000₫

</span>
```

```python
price = sel.css("span::text").re_first(r"[\d\.]+", default="0")

price = int(price.replace(".", ""))
```

↓

```python
1250000
```

---

# 13. Parser JavaScript

HTML

```html
<script>

var storyId = 789;

</script>
```

```python
story_id = sel.css("script::text").re_first(r"storyId\s*=\s*(\d+)", default="0")

story_id = int(story_id)
```

↓

```python
789
```

---

# 14. Parser URL

HTML

```html
<a href="/chapter/12345">
```

```python
chapter = sel.css("a::attr(href)").re_first(r"\d+", default="0")
```

↓

```python
"12345"
```

---

# 15. Regex trên SelectorList

HTML

```html
<li>100</li>

<li>200</li>

<li>300</li>
```

```python
sel.css("li::text").re_first(r"\d+")
```

↓

```python
"100"
```

---

# 16. So sánh

| API          | Trả về            |
| ------------ | ----------------- |
| `re()`       | `list[str]`       |
| `re_first()` | `str` hoặc `None` |

---

# 17. Parser thực tế

```python
book = sel.css(".book")[0]

price = int(book.css(".price::text").re_first(r"\d+", default="0"))

rating = float(book.css(".rating::text").re_first(r"\d+\.\d+", default="0"))

print(price)

print(rating)
```

---

# 18. Sai lầm phổ biến

## Sai lầm 1

```python
price = book.css(".price::text").re_first(r"\d+")

price[0]
```

Sai.

Vì

```python
price
```

đã là

```python
"150"
```

Không phải

```python
["150"]
```

---

## Sai lầm 2

```python
int(book.css(".price::text").re_first(r"\d+"))
```

Nếu không có giá.

↓

```python
None
```

↓

```python
TypeError
```

Đúng

```python
int(book.css(".price::text").re_first(r"\d+", default="0"))
```

---

## Sai lầm 3

Dùng `re()` rồi lấy phần tử đầu.

```python
price = book.css(".price::text").re(r"\d+")

price = price[0]
```

Có thể viết ngắn hơn

```python
price = book.css(".price::text").re_first(r"\d+")
```

---

# 19. Khi nào dùng `re_first()`?

Rất phù hợp với:

* Giá
* Rating
* ID
* Version
* Chapter ID
* Story ID
* User ID
* Email đầu tiên
* Số điện thoại đầu tiên

---

Không nên dùng với:

* Danh sách tag
* Danh sách email
* Danh sách URL
* Danh sách chương

Lúc này dùng `re()`.

---

# 20. Kết hợp CSS → Regex

Đây là phong cách chuyên nghiệp.

```text
CSS
    ↓
Text
    ↓
Regex
    ↓
int
```

Ví dụ

```python
views = int(book.css(".views::text").re_first(r"[\d,]+", default="0").replace(",", ""))
```

---

# 21. Kết hợp XPath → Regex

```python
views = int(book.xpath(".//span/text()").re_first(r"\d+", default="0"))
```

---

# 22. Parser thực tế

HTML

```html
<div class="book">

<h2>Python</h2>

<span>

Views: 1,234

</span>

<p>

Rating: 4.8

</p>

<script>

var id=88;

</script>

</div>
```

Parser

```python
book = sel.css(".book")[0]

data = {
    "title": book.css("h2::text").get(default=""),
    "views": int(
        book.css("span::text").re_first(r"[\d,]+", default="0").replace(",", "")
    ),
    "rating": float(book.css("p::text").re_first(r"\d+\.\d+", default="0")),
    "id": int(book.css("script::text").re_first(r"id=(\d+)", default="0")),
}

print(data)
```

↓

```python
{"title": "Python", "views": 1234, "rating": 4.8, "id": 88}
```

---

# 23. `re()` hay `re_first()`?

| Nhu cầu       | API          |
| ------------- | ------------ |
| Một giá trị   | `re_first()` |
| Nhiều giá trị | `re()`       |
| Có `default=` | `re_first()` |
| Luôn trả list | `re()`       |

---

# 24. Best Practices

## Luôn dùng `default`

```python
price = int(book.css(".price::text").re_first(r"\d+", default="0"))
```

---

## Chỉ Regex sau khi chọn đúng node

Đúng

```python
book.css(".price::text").re_first(...)
```

Không nên

```python
sel.re_first(...)
```

vì regex sẽ quét toàn bộ tài liệu.

---

## Chuyển kiểu dữ liệu sau Regex

Đúng

```python
price = int(price_text)
```

Không cố gắng để Regex trả về kiểu số.

---

## Đặt Pattern thành hằng số

```python
PRICE_PATTERN = r"[\d\.]+"
VIEW_PATTERN = r"[\d,]+"
ID_PATTERN = r"id=(\d+)"
```

Giúp mã dễ bảo trì và tái sử dụng.

---

# 25. Ví dụ hoàn chỉnh

```python
from parsel import Selector

html = """
<div class="novel">

<h2>Đấu Phá Thương Khung</h2>

<span class="views">

Lượt xem: 2,345,678

</span>

<span class="chapters">

1988 chương

</span>

<script>

var storyId = 999;

</script>

</div>
"""

sel = Selector(text=html)

novel = sel.css(".novel")[0]

data = {
    "title": novel.css("h2::text").get(default="").strip(),
    "views": int(
        novel.css(".views::text").re_first(r"[\d,]+", default="0").replace(",", "")
    ),
    "chapters": int(novel.css(".chapters::text").re_first(r"\d+", default="0")),
    "story_id": int(
        novel.css("script::text").re_first(r"storyId\s*=\s*(\d+)", default="0")
    ),
}

print(data)
```

Kết quả

```python
{"title": "Đấu Phá Thương Khung", "views": 2345678, "chapters": 1988, "story_id": 999}
```

---

# 26. `re()` và `re_first()` hoạt động như thế nào?

Hiểu được cơ chế bên trong sẽ giúp bạn chọn đúng API.

Giả sử:

```python
selector = book.css(".price::text")
```

Nội dung:

```text
Price: 150 USD
```

### `re()`

```python
selector.re(r"\d+")
```

Bên trong Parsel có thể hình dung tương tự:

```python
import re

text = "Price: 150 USD"

result = re.findall(r"\d+", text)

print(result)
```

Kết quả:

```python
["150"]
```

---

### `re_first()`

Có thể hình dung:

```python
matches = re.findall(r"\d+", text)

result = matches[0] if matches else None
```

Nếu bạn truyền `default=`:

```python
result = matches[0] if matches else default
```

Đó là lý do `re_first()` vừa ngắn gọn vừa an toàn hơn so với việc tự viết:

```python
matches = selector.re(pattern)

value = matches[0] if matches else "0"
```

---

# Bài tập

Cho HTML:

```html
<div class="movie">

<h2>Interstellar</h2>

<span class="duration">
169 phút
</span>

<span class="score">
IMDb: 8.7/10
</span>

<script>
var movieId = 2026;
</script>

</div>
```

Hãy tạo parser trả về:

```python
{
    "title": "Interstellar",
    "duration": 169,
    "score": 8.7,
    "movie_id": 2026,
}
```

Yêu cầu:

1. Dùng `get()` để lấy tiêu đề.
2. Dùng `re_first()` để lấy:

   * thời lượng,
   * điểm IMDb,
   * `movieId`.
3. Luôn sử dụng `default=` để parser không bị lỗi.
4. Chuyển dữ liệu sang đúng kiểu `int` hoặc `float`.

---

# Tổng kết

`re_first()` là phiên bản "một giá trị" của `re()`. Trong thực tế:

* **`re()`** dùng khi bạn cần **tất cả** kết quả khớp.
* **`re_first()`** dùng khi bạn chỉ cần **một** kết quả và muốn có thể chỉ định `default`.

Trong các dự án crawler lớn (Scrapy, Parsel), `re_first()` thường được dùng nhiều hơn `re()` vì hầu hết các trường như **ID, giá, lượt xem, số chương, điểm đánh giá** đều chỉ có một giá trị.

## Buổi tiếp theo

Ở **Buổi 11**, chúng ta sẽ học **`Selector.attrib`** và **`Selector.root`**:

* `attrib` để truy cập trực tiếp toàn bộ thuộc tính của một node dưới dạng `dict`.
* So sánh `attrib` với `::attr()` và `@attribute`.
* Khi nào nên dùng `attrib`, khi nào không nên.
* `root` để truy cập đối tượng `lxml.etree.Element` bên dưới `Selector`, mở ra khả năng kết hợp Parsel với toàn bộ hệ sinh thái `lxml` cho các bài toán parser nâng cao.
