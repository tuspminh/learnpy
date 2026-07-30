# Khóa học Parsel

# Phần III — Làm việc với `Selector` nâng cao

# Buổi 11 — `Selector.attrib` Deep Dive

Trong các buổi trước, chúng ta thường lấy thuộc tính bằng:

```python
book.css("a::attr(href)").get()
```

hoặc

```python
book.xpath(".//@href").get()
```

Đây là cách phổ biến nhất.

Tuy nhiên, đôi khi bạn muốn lấy **toàn bộ thuộc tính của một node** cùng một lúc.

Ví dụ:

```html
<a href="/book/1"
   class="item"
   data-id="100"
   title="Python">
```

Thay vì viết:

```python
href = a.css("::attr(href)").get()
title = a.css("::attr(title)").get()
cls = a.css("::attr(class)").get()
```

Parsel cho phép:

```python
a.attrib
```

↓

```python
{"href": "/book/1", "class": "item", "data-id": "100", "title": "Python"}
```

Đây là API rất hữu ích khi viết crawler lớn.

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

* `Selector.attrib`
* `SelectorList.attrib`
* So sánh với `::attr()`
* Lấy toàn bộ thuộc tính
* Thuộc tính tùy chỉnh (`data-*`)
* Best Practices

---

# 1. `attrib` là gì?

`attrib` là một **property** của `Selector`.

Nó trả về:

```python
dict[str, str]
```

chứa toàn bộ attribute của node.

Ví dụ:

HTML

```html
<img src="cover.jpg"
     alt="Python"
     width="200">
```

Parser

```python
img = sel.css("img")[0]

print(img.attrib)
```

↓

```python
{"src": "cover.jpg", "alt": "Python", "width": "200"}
```

---

# 2. Kiểu dữ liệu

```python
attrs = img.attrib

print(type(attrs))
```

↓

```python
<class 'dict'>
```

---

# 3. Truy cập thuộc tính

```python
attrs = img.attrib

print(attrs["src"])
```

↓

```python
cover.jpg
```

---

```python
print(attrs["alt"])
```

↓

```python
Python
```

---

# 4. HTML mẫu

```html
<div class="book"
     data-id="15"
     data-category="Programming">

    <a href="/python"
       title="Python Book">

        Python

    </a>

</div>
```

---

# 5. Lấy thuộc tính của `<a>`

```python
a = sel.css("a")[0]

print(a.attrib)
```

↓

```python
{"href": "/python", "title": "Python Book"}
```

---

# 6. Truy cập từng thuộc tính

```python
a.attrib["href"]
```

↓

```python
"/python"
```

---

```python
a.attrib["title"]
```

↓

```python
"Python Book"
```

---

# 7. Lấy thuộc tính tùy chỉnh

```python
book = sel.css(".book")[0]

print(book.attrib)
```

↓

```python
{"class": "book", "data-id": "15", "data-category": "Programming"}
```

---

```python
book.attrib["data-id"]
```

↓

```python
15
```

(giá trị vẫn là **chuỗi** `"15"`)

---

# 8. `attrib.get()`

Giống Dictionary.

Không nên

```python
book.attrib["author"]
```

Nếu không tồn tại

↓

```python
KeyError
```

Đúng

```python
book.attrib.get("author")
```

↓

```python
None
```

---

Có default

```python
book.attrib.get("author", "Unknown")
```

↓

```python
Unknown
```

---

# 9. So sánh với `::attr()`

Ví dụ

```python
a.css("::attr(href)").get()
```

↓

```python
"/python"
```

---

```python
a.attrib["href"]
```

↓

```python
"/python"
```

Kết quả giống nhau.

---

# 10. Khác nhau

`::attr()`

```python
a.css("::attr(href)").get()
```

Ưu điểm

* Có thể kết hợp selector
* Có `default=`
* Làm việc với `SelectorList`

---

`attrib`

```python
a.attrib["href"]
```

Ưu điểm

* Nhanh
* Ngắn
* Có toàn bộ attribute

---

# 11. Khi nào dùng `attrib`?

Nếu đã có `Selector`

```python
a = book.css("a")[0]
```

thì

```python
href = a.attrib["href"]
```

là lựa chọn rất tốt.

---

# 12. Khi nào KHÔNG dùng?

Nếu chưa chọn node.

Sai

```python
sel.attrib
```

`sel` là toàn bộ document.

Không có ý nghĩa.

Hãy:

```python
book = sel.css(".book")[0]
```

sau đó

```python
book.attrib
```

---

# 13. Thuộc tính Boolean

HTML

```html
<input
type="checkbox"
checked>
```

Parser

```python
checkbox = sel.css("input")[0]

print(checkbox.attrib)
```

↓

```python
{"type": "checkbox", "checked": "checked"}
```

Trong HTML, thuộc tính boolean thường có giá trị chính là tên của nó.

---

# 14. Parser thực tế

HTML

```html
<img
src="cover.jpg"

alt="Python"

loading="lazy"

width="300"

height="500">
```

Parser

```python
img = sel.css("img")[0]

data = {
    "src": img.attrib.get("src"),
    "alt": img.attrib.get("alt"),
    "loading": img.attrib.get("loading"),
    "width": int(img.attrib.get("width", "0")),
    "height": int(img.attrib.get("height", "0")),
}

print(data)
```

↓

```python
{"src": "cover.jpg", "alt": "Python", "loading": "lazy", "width": 300, "height": 500}
```

---

# 15. `attrib` với `data-*`

HTML

```html
<div

data-id="123"

data-type="vip"

data-price="100000"

>
```

Parser

```python
node = sel.css("div")[0]

print(node.attrib)
```

↓

```python
{"data-id": "123", "data-type": "vip", "data-price": "100000"}
```

---

```python
price = int(node.attrib.get("data-price", "0"))
```

↓

```python
100000
```

---

# 16. Lặp qua toàn bộ thuộc tính

```python
for name, value in a.attrib.items():
    print(name, value)
```

↓

```text
href /python

title Python Book
```

---

# 17. Sao chép thuộc tính

Nếu cần chỉnh sửa mà không ảnh hưởng dữ liệu gốc:

```python
attrs = dict(a.attrib)

attrs["href"] = "/new"

print(attrs)
```

Lưu ý: việc thay đổi `attrs` không thay đổi HTML gốc.

---

# 18. Sai lầm phổ biến

## Sai lầm 1

```python
href = a.attrib["href"]
```

Nếu thiếu `href`

↓

```python
KeyError
```

Đúng

```python
href = a.attrib.get("href", "")
```

---

## Sai lầm 2

```python
price = a.attrib["data-price"] + 100
```

Sai.

Vì

```python
a.attrib["data-price"]
```

là

```python
"100"
```

Không phải

```python
100
```

Đúng

```python
price = int(a.attrib.get("data-price", "0"))
```

---

## Sai lầm 3

```python
attrs = book.attrib

attrs["new"] = "abc"
```

Điều này **không thêm thuộc tính vào HTML**.

Nó chỉ thay đổi dictionary bạn đang thao tác.

Parsel không phải thư viện chỉnh sửa HTML.

---

# 19. So sánh `attrib` và `css("::attr()")`

| Tiêu chí                 | `attrib`          | `::attr()`             |
| ------------------------ | ----------------- | ---------------------- |
| Lấy 1 thuộc tính         | ✔                 | ✔                      |
| Lấy tất cả thuộc tính    | ✔                 | ✘                      |
| Dùng trên `SelectorList` | ✘                 | ✔                      |
| `default=`               | Dùng `dict.get()` | Dùng `.get(default=)`  |
| Kiểu trả về              | `dict`            | `SelectorList` → `str` |

---

# 20. Ví dụ hoàn chỉnh

```python
from parsel import Selector

html = """
<div class="book" data-id="100">
    <a href="/python"
       title="Python Book">
       Python
    </a>

    <img src="cover.jpg"
         alt="Cover"
         width="300">
</div>
"""

sel = Selector(text=html)

book = sel.css(".book")[0]
a = book.css("a")[0]
img = book.css("img")[0]

data = {
    "book_id": int(book.attrib.get("data-id", "0")),
    "href": a.attrib.get("href", ""),
    "title": a.attrib.get("title", ""),
    "image": img.attrib.get("src", ""),
    "width": int(img.attrib.get("width", "0")),
}

print(data)
```

Kết quả:

```python
{
    "book_id": 100,
    "href": "/python",
    "title": "Python Book",
    "image": "cover.jpg",
    "width": 300,
}
```

---

# 21. So sánh hiệu năng

Giả sử bạn cần lấy 5 thuộc tính:

### Cách 1

```python
href = a.css("::attr(href)").get()
title = a.css("::attr(title)").get()
target = a.css("::attr(target)").get()
rel = a.css("::attr(rel)").get()
cls = a.css("::attr(class)").get()
```

Mỗi lần gọi `css()` đều phải thực hiện truy vấn selector.

---

### Cách 2

```python
attrs = a.attrib

href = attrs.get("href")
title = attrs.get("title")
target = attrs.get("target")
rel = attrs.get("rel")
cls = attrs.get("class")
```

Chỉ truy cập dictionary đã có sẵn.

Nếu cần nhiều thuộc tính trên cùng một node, cách này thường rõ ràng và hiệu quả hơn.

---

# 22. Best Practices

✅ Sau khi đã có `Selector`, ưu tiên dùng:

```python
attrs = node.attrib
```

---

✅ Luôn dùng:

```python
attrs.get("href", "")
```

thay vì:

```python
attrs["href"]
```

---

✅ Chuyển kiểu dữ liệu ngay sau khi lấy:

```python
book_id = int(attrs.get("data-id", "0"))
```

---

✅ Dùng `attrib` khi cần nhiều thuộc tính từ cùng một phần tử.

---

# Bài tập

Cho HTML:

```html
<div class="movie"
     data-id="101"
     data-rating="8.7">

    <img
        src="poster.jpg"
        alt="Poster"
        width="400"
        height="600">

    <a
        href="/movie/interstellar"
        title="Interstellar">
        Xem
    </a>

</div>
```

Hãy tạo parser trả về:

```python
{
    "movie_id": 101,
    "rating": 8.7,
    "poster": {
        "src": "poster.jpg",
        "alt": "Poster",
        "width": 400,
        "height": 600,
    },
    "link": {
        "href": "/movie/interstellar",
        "title": "Interstellar",
    },
}
```

Yêu cầu:

1. Sử dụng `attrib` để lấy tất cả thuộc tính cần thiết.
2. Dùng `dict.get()` thay vì truy cập trực tiếp bằng `[]`.
3. Chuyển `movie_id`, `width`, `height` sang `int`.
4. Chuyển `rating` sang `float`.

---

# Tổng kết

`Selector.attrib` là cách **nhanh, gọn và trực tiếp** để truy cập toàn bộ thuộc tính của một node dưới dạng `dict`. Đây là lựa chọn lý tưởng khi bạn đã có `Selector` và cần đọc nhiều thuộc tính từ cùng một phần tử.

Trong các crawler chuyên nghiệp, bạn sẽ thường thấy mẫu:

```python
node = sel.css(".item")[0]
attrs = node.attrib

item = {
    "id": int(attrs.get("data-id", "0")),
    "href": attrs.get("href", ""),
    "title": attrs.get("title", ""),
}
```

đơn giản, dễ đọc và dễ bảo trì.

## Buổi tiếp theo

Ở **Buổi 12**, chúng ta sẽ học **`Selector.root`** — cách truy cập trực tiếp đối tượng `lxml.etree.Element` nằm bên dưới `Selector`, mở ra khả năng sử dụng toàn bộ API mạnh mẽ của **lxml** (duyệt cây DOM, thao tác node, lấy sibling, parent, namespace, v.v.) cùng với Parsel.
