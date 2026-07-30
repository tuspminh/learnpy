# Khóa học Parsel

# Phần III — Làm việc với `Selector` nâng cao

# Buổi 12 — `Selector.root` Deep Dive

Đến nay chúng ta đã làm việc hoàn toàn với API của Parsel:

* `css()`
* `xpath()`
* `get()`
* `getall()`
* `re()`
* `attrib`

Thực tế, Parsel chỉ là một lớp bao (wrapper) rất mỏng quanh thư viện **lxml**.

Bên dưới mỗi `Selector` là một đối tượng:

```python
lxml.etree._Element
```

Đối tượng này được truy cập thông qua:

```python
selector.root
```

Đây là một trong những API mạnh nhất của Parsel.

Nếu biết dùng `root`, bạn gần như có toàn bộ sức mạnh của lxml.

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

* `Selector.root`
* `_Element`
* Quan hệ giữa Parsel và lxml
* Khi nào nên dùng `root`
* Khi nào KHÔNG nên dùng
* Các API quan trọng của lxml

---

# 1. `root` là gì?

Ví dụ

```python
from parsel import Selector

html = """
<div class="book">

    <h2>Python</h2>

</div>
"""

sel = Selector(text=html)

book = sel.css(".book")[0]
```

Nếu

```python
print(book.root)
```

Ví dụ kết quả

```text
<Element div at 0x7fa123456>
```

Đây chính là node HTML thật của lxml.

---

# 2. Kiểu dữ liệu

```python
print(type(book.root))
```

Ví dụ

```python
<class 'lxml.html.HtmlElement'>
```

hoặc

```python
<class 'lxml.etree._Element'>
```

Tùy cách Parser tạo DOM.

---

# 3. Kiến trúc

```text
HTML

     │

     ▼

lxml HTML Parser

     │

     ▼

_Element

     ▲

     │

Selector
```

Parsel chỉ "bọc" `_Element`.

---

# 4. Truy cập tag

HTML

```html
<div class="book">

<h2>Python</h2>

</div>
```

```python
book = sel.css(".book")[0]

print(book.root.tag)
```

↓

```text
div
```

---

```python
title = book.css("h2")[0]

print(title.root.tag)
```

↓

```text
h2
```

---

# 5. Truy cập text

HTML

```html
<h2>Python</h2>
```

```python
title = sel.css("h2")[0]

print(title.root.text)
```

↓

```text
Python
```

Không cần

```python
title.css("::text").get()
```

---

# 6. Truy cập attribute

```python
img = sel.css("img")[0]

print(img.root.attrib)
```

↓

```python
{"src": "cover.jpg", "alt": "Python"}
```

Đây chính là dictionary của lxml.

---

# 7. So sánh

Parsel

```python
img.attrib
```

↓

Dictionary

---

lxml

```python
img.root.attrib
```

↓

Cũng là Dictionary

---

# 8. Lấy Parent

HTML

```html
<div>

<h2>Python</h2>

</div>
```

```python
title = sel.css("h2")[0]

parent = title.root.getparent()

print(parent.tag)
```

↓

```text
div
```

Parsel không có API:

```python
title.parent()
```

Muốn lấy cha phải dùng `root`.

---

# 9. Lấy các node con

HTML

```html
<div>

<h2>Python</h2>

<p>Book</p>

</div>
```

```python
book = sel.css("div")[0]

for child in book.root:
    print(child.tag)
```

↓

```text
h2

p
```

---

# 10. Lấy sibling

HTML

```html
<h2>Python</h2>

<p>Book</p>

<span>100</span>
```

```python
title = sel.css("h2")[0]

next_node = title.root.getnext()

print(next_node.tag)
```

↓

```text
p
```

---

Node tiếp theo

```python
next_node.getnext()
```

↓

```text
span
```

---

# 11. Previous sibling

```python
span = sel.css("span")[0]

prev = span.root.getprevious()

print(prev.tag)
```

↓

```text
p
```

---

# 12. Duyệt cây DOM

```python
book = sel.css(".book")[0]

for node in book.root.iter():
    print(node.tag)
```

↓

```text
div

h2

p

img

span
```

Đây là DFS traversal của lxml.

---

# 13. Lấy toàn bộ text

HTML

```html
<div>

Hello

<b>Python</b>

World

</div>
```

```python
node = sel.css("div")[0]

print(node.root.text_content())
```

↓

```text
Hello Python World
```

So với

```python
node.css("::text").getall()
```

↓

```python
["Hello", "Python", "World"]
```

Khác nhau hoàn toàn.

---

# 14. XPath trực tiếp bằng lxml

```python
book.root.xpath(".//h2/text()")
```

↓

```python
["Python"]
```

Không cần Parsel.

---

# 15. CSS trực tiếp?

lxml không hỗ trợ CSS mặc định trên `_Element`.

Muốn CSS selector, bạn vẫn nên dùng:

```python
book.css("h2")
```

---

# 16. Chuyển ngược thành Selector

Nếu có `_Element`

```python
element = book.root
```

Có thể

```python
from parsel import Selector

new_selector = Selector(root=element)
```

↓

Lại có

```python
new_selector.css(...)
```

Đây là kỹ thuật hữu ích khi kết hợp API của lxml với Parsel.

---

# 17. Parser thực tế

```python
book = sel.css(".book")[0]

root = book.root

data = {
    "tag": root.tag,
    "children": len(root),
    "text": root.text_content(),
    "attrs": dict(root.attrib),
}

print(data)
```

Ví dụ kết quả

```python
{"tag": "div", "children": 3, "text": "Python Book 100", "attrs": {"class": "book"}}
```

---

# 18. Sai lầm phổ biến

## Sai lầm 1

```python
book.root.css("h2")
```

Sai.

`_Element`

không có

```python
css()
```

Đúng

```python
book.css("h2")
```

hoặc

```python
Selector(root=book.root).css("h2")
```

---

## Sai lầm 2

```python
book.root.get()
```

Sai.

`get()` là API của Parsel.

Không phải của lxml.

---

## Sai lầm 3

```python
book.root.getparent().css(...)
```

Sai.

Vì

```python
getparent()
```

trả về `_Element`.

Không phải `Selector`.

---

# 19. Khi nào nên dùng root?

✔ Cần lấy parent

✔ Cần lấy sibling

✔ Traverse DOM

✔ text_content()

✔ API đặc biệt của lxml

✔ Hiệu năng cao

---

# 20. Khi nào KHÔNG nên dùng?

Nếu chỉ cần

```python
.css()
```

```python
.xpath()
```

```python
.get()
```

```python
.getall()
```

thì cứ dùng Parsel.

Đơn giản hơn nhiều.

---

# 21. Best Practices

### Dùng Parsel làm API chính

```python
title = book.css("h2::text").get(default="")
```

---

### Chỉ dùng `root` khi Parsel không có API tương ứng

Ví dụ:

```python
parent = node.root.getparent()
```

---

### Nếu quay lại dùng CSS/XPath của Parsel

```python
from parsel import Selector

parent_selector = Selector(root=parent)

parent_selector.css("a")
```

---

### Không trộn lẫn `_Element` và `Selector`

Đặt tên rõ ràng:

```python
book_selector = sel.css(".book")[0]

book_element = book_selector.root
```

Điều này giúp tránh nhầm lẫn giữa API của Parsel và lxml.

---

# 22. Ví dụ hoàn chỉnh

```python
from parsel import Selector

html = """
<div class="book">
    <h2>Python</h2>
    <p>Programming Language</p>
    <img src="cover.jpg">
</div>
"""

sel = Selector(text=html)

book = sel.css(".book")[0]

root = book.root

print(root.tag)

print(root.attrib)

print(root.text_content())

for child in root:
    print(child.tag)
```

Kết quả

```text
div

{'class': 'book'}

Python Programming Language

h2

p

img
```

---

# 23. Quan hệ giữa Parsel và lxml

```text
              HTML

                │
                ▼
      lxml HTML Parser
                │
                ▼
        HtmlElement (_Element)
                ▲
                │
      Selector(root=element)
                │
        ┌───────┴────────┐
        │                │
     css()            xpath()
        │                │
        └───────┬────────┘
                ▼
           SelectorList
                │
     get() / getall() / re()
```

Đây là kiến trúc cốt lõi của Parsel.

---

# Bài tập

Cho HTML:

```html
<div class="library">

    <div class="book">

        <h2>Python</h2>

        <span>100</span>

    </div>

    <div class="book">

        <h2>Java</h2>

        <span>200</span>

    </div>

</div>
```

Hãy viết chương trình:

1. Lấy `Selector` của quyển sách đầu tiên.
2. In:

   * `root.tag`
   * `root.attrib`
3. Dùng `root.getparent()` để lấy node cha và in `tag`.
4. Dùng `root.iter()` để in toàn bộ tag bên trong quyển sách đầu tiên.
5. Dùng `Selector(root=...)` để chuyển node cha trở lại `Selector` rồi lấy tên của tất cả các sách bằng `.css("h2::text").getall()`.

---

# Tổng kết

`Selector.root` là **cánh cửa kết nối Parsel với lxml**. Trong phần lớn các crawler, bạn có thể chỉ cần API của Parsel. Tuy nhiên, khi cần điều hướng cây DOM (parent, sibling, traversal) hoặc tận dụng các tính năng chuyên sâu của lxml, `root` sẽ trở thành công cụ cực kỳ mạnh mẽ.

Đối với các dự án crawler lớn như crawler truyện, báo điện tử hay thương mại điện tử, việc kết hợp:

* **Parsel** để truy vấn CSS/XPath.
* **lxml** thông qua `root` để thao tác cây DOM.

là một kỹ thuật rất phổ biến.

---

## Lộ trình tiếp theo

Sau khi đã nắm vững toàn bộ API cơ bản và nâng cao của `Selector`, chúng ta sẽ chuyển sang phần quan trọng nhất của Parsel:

### **Phần IV – Kỹ thuật Parser chuyên nghiệp**

* **Buổi 13:** Parser lồng nhau (Nested Selector)
* **Buổi 14:** Parser danh sách (List Parsing)
* **Buổi 15:** Parser phân trang (Pagination)
* **Buổi 16:** Parser dữ liệu phức hợp (Nested Data Extraction)
* **Buổi 17:** Parser JavaScript và JSON nhúng
* **Buổi 18:** Thiết kế parser có khả năng chống thay đổi giao diện website
* **Buổi 19:** Kiểm thử (Testing) parser
* **Buổi 20:** Xây dựng parser hoàn chỉnh cho một website thực tế (ví dụ: trang truyện hoặc thương mại điện tử).
