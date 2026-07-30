# Khóa học HTML bài bản dành cho Python Developer

# Buổi 3: Danh sách (Lists) trong HTML

## Mục tiêu

Sau buổi học này, bạn sẽ:

* Hiểu tại sao HTML có nhiều loại danh sách khác nhau.
* Thành thạo `ul`, `ol`, `li`.
* Biết sử dụng `dl`, `dt`, `dd`.
* Biết tạo danh sách nhiều cấp (Nested List).
* Biết ứng dụng danh sách trong menu, sidebar, mục lục và dữ liệu thực tế.
* Viết được HTML chuẩn Semantic.

---

# 1. Danh sách trong HTML là gì?

Rất nhiều nội dung trên web thực chất là **danh sách**.

Ví dụ:

```
Khóa học

- HTML
- CSS
- JavaScript
- Flask
```

Hoặc

```
Các bước cài Python

1. Download
2. Install
3. Verify
```

HTML cung cấp **3 loại danh sách**.

```
List

├── ul
├── ol
└── dl
```

---

# 2. Unordered List (`<ul>`)

Là danh sách **không có thứ tự**.

Ví dụ:

```html
<ul>
    <li>Python</li>
    <li>Flask</li>
    <li>Jinja2</li>
    <li>Sanic</li>
</ul>
```

Hiển thị

```
• Python
• Flask
• Jinja2
• Sanic
```

Trong đó

```
ul

↓

Danh sách
```

```
li

↓

Một phần tử
```

---

# 3. Có thể chứa bao nhiêu `<li>`?

Không giới hạn.

```html
<ul>

<li>1</li>

<li>2</li>

<li>3</li>

...

<li>100</li>

</ul>
```

---

# 4. Ordered List (`<ol>`)

Danh sách **có đánh số**.

```html
<ol>
    <li>Cài Python</li>
    <li>Cài VS Code</li>
    <li>Tạo Virtual Environment</li>
    <li>Viết Hello World</li>
</ol>
```

Hiển thị

```
1. Cài Python

2. Cài VS Code

3. Tạo Virtual Environment

4. Hello World
```

---

# 5. Khi nào dùng `ul`, khi nào dùng `ol`?

### Dùng `ul`

* Menu
* Danh mục
* Tính năng
* Tag
* Danh sách sản phẩm

Ví dụ

```html
<ul>
    <li>Trang chủ</li>
    <li>Sản phẩm</li>
    <li>Tin tức</li>
    <li>Liên hệ</li>
</ul>
```

---

### Dùng `ol`

* Quy trình
* Hướng dẫn
* Công thức
* Bước cài đặt

```html
<ol>

<li>Đăng nhập</li>

<li>Chọn sản phẩm</li>

<li>Thanh toán</li>

</ol>
```

---

# 6. Thuộc tính `type`

Có thể đổi kiểu đánh số.

```html
<ol type="A">
    <li>HTML</li>
    <li>CSS</li>
    <li>JS</li>
</ol>
```

Hiển thị

```
A.

B.

C.
```

---

Có thể dùng

```text
1

A

a

I

i
```

Ví dụ

```html
<ol type="I">
    <li>Introduction</li>
    <li>HTML</li>
    <li>CSS</li>
</ol>
```

Hiển thị

```
I

II

III
```

---

# 7. Thuộc tính `start`

```html
<ol start="5">
    <li>Python</li>
    <li>Flask</li>
</ol>
```

Hiển thị

```
5. Python

6. Flask
```

---

# 8. Thuộc tính `reversed`

```html
<ol reversed>
    <li>A</li>
    <li>B</li>
    <li>C</li>
</ol>
```

Hiển thị

```
3

2

1
```

---

# 9. Nested List (Danh sách lồng nhau)

Ví dụ

```html
<ul>

<li>Python

    <ul>

        <li>Flask</li>

        <li>Django</li>

    </ul>

</li>

<li>Java</li>

</ul>
```

Hiển thị

```
• Python

    • Flask

    • Django

• Java
```

---

# 10. Nested Ordered List

```html
<ol>

<li>Python

    <ol>

        <li>Flask</li>

        <li>Sanic</li>

    </ol>

</li>

<li>Go</li>

</ol>
```

---

# 11. Nhiều cấp

```html
<ul>

<li>Backend

    <ul>

        <li>Python

            <ul>

                <li>Flask</li>

                <li>FastAPI</li>

            </ul>

        </li>

    </ul>

</li>

</ul>
```

Hiển thị

```
Backend

    Python

        Flask

        FastAPI
```

---

# 12. Description List (`<dl>`)

Không phải danh sách thông thường.

Đây là danh sách:

```
Thuật ngữ

↓

Giải thích
```

---

Ví dụ

```html
<dl>

<dt>HTML</dt>

<dd>Ngôn ngữ đánh dấu.</dd>

<dt>CSS</dt>

<dd>Ngôn ngữ định dạng.</dd>

</dl>
```

Hiển thị

```
HTML

    Ngôn ngữ đánh dấu.

CSS

    Ngôn ngữ định dạng.
```

---

# 13. `dt`

Là tên.

```html
<dt>Python</dt>
```

---

# 14. `dd`

Là mô tả.

```html
<dd>Ngôn ngữ lập trình.</dd>
```

---

# 15. Ví dụ hoàn chỉnh

```html
<dl>

<dt>Flask</dt>

<dd>Framework Web.</dd>

<dt>Jinja2</dt>

<dd>Template Engine.</dd>

<dt>Parsel</dt>

<dd>HTML Parser.</dd>

</dl>
```

---

# 16. Ứng dụng thực tế: Menu website

```html
<nav>

<ul>

<li>Trang chủ</li>

<li>Sản phẩm</li>

<li>Tin tức</li>

<li>Liên hệ</li>

</ul>

</nav>
```

---

# 17. Sidebar khóa học

```html
<ul>

<li>HTML

    <ul>

        <li>Heading</li>

        <li>List</li>

        <li>Table</li>

    </ul>

</li>

<li>CSS</li>

<li>JavaScript</li>

</ul>
```

---

# 18. Mục lục sách

```html
<ol>

<li>HTML

    <ol>

        <li>Heading</li>

        <li>List</li>

        <li>Form</li>

    </ol>

</li>

<li>CSS</li>

<li>JavaScript</li>

</ol>
```

---

# 19. HTML cho Flask/Jinja2

Giả sử trong Flask:

```python
courses = ["Python", "HTML", "CSS", "Flask"]
```

Template Jinja2:

```html
<ul>

{% for course in courses %}

<li>{{ course }}</li>

{% endfor %}

</ul>
```

Render

```
• Python

• HTML

• CSS

• Flask
```

Đây là cách rất phổ biến để hiển thị dữ liệu từ Python lên giao diện.

---

# 20. Ví dụ thực tế hoàn chỉnh

```html
<!DOCTYPE html>
<html lang="vi">

<head>
    <meta charset="UTF-8">
    <title>Khóa học Python</title>
</head>

<body>

<h1>Lộ trình học Python</h1>

<h2>Các công nghệ Backend</h2>

<ul>

<li>Python</li>

<li>Flask</li>

<li>FastAPI</li>

<li>Sanic</li>

</ul>

<hr>

<h2>Các bước học</h2>

<ol>

<li>HTML</li>

<li>CSS</li>

<li>JavaScript</li>

<li>Flask</li>

</ol>

<hr>

<h2>Thuật ngữ</h2>

<dl>

<dt>HTML</dt>

<dd>Ngôn ngữ đánh dấu.</dd>

<dt>CSS</dt>

<dd>Ngôn ngữ định dạng.</dd>

<dt>Flask</dt>

<dd>Framework Web của Python.</dd>

</dl>

</body>

</html>
```

---

# 21. Những lỗi thường gặp

## ❌ Đặt `<li>` ngoài `<ul>` hoặc `<ol>`

Sai:

```html
<li>Python</li>
```

Đúng:

```html
<ul>
    <li>Python</li>
</ul>
```

---

## ❌ Lồng danh sách sai vị trí

Sai:

```html
<ul>
    <li>Python</li>
</ul>

<ul>
    <li>Flask</li>
</ul>
```

Nếu "Flask" là mục con của "Python", đúng phải là:

```html
<ul>
    <li>
        Python
        <ul>
            <li>Flask</li>
        </ul>
    </li>
</ul>
```

---

## ❌ Dùng `<br>` để giả lập danh sách

Sai:

```html
Python<br>
Flask<br>
FastAPI
```

Đúng:

```html
<ul>
    <li>Python</li>
    <li>Flask</li>
    <li>FastAPI</li>
</ul>
```

Danh sách đúng chuẩn giúp trình duyệt, công cụ tìm kiếm và trình đọc màn hình hiểu được cấu trúc nội dung.

---

# 22. Bài tập thực hành

## Bài 1

Tạo danh sách không thứ tự gồm:

* Python
* HTML
* CSS
* JavaScript
* Flask

---

## Bài 2

Tạo danh sách có thứ tự mô tả quy trình cài đặt Flask:

1. Cài Python
2. Tạo Virtual Environment
3. Cài Flask
4. Chạy ứng dụng đầu tiên

---

## Bài 3

Tạo danh sách lồng nhau theo cấu trúc:

```text
Backend
├── Python
│   ├── Flask
│   ├── FastAPI
│   └── Sanic
└── Go
```

---

## Bài 4

Tạo một Description List giải thích các thuật ngữ:

* HTML
* CSS
* JavaScript
* Flask
* Jinja2

Mỗi thuật ngữ có một phần mô tả ngắn.

---

## Bài 5 (Dành cho Python Developer)

Cho dữ liệu Python:

```python
books = ["Harry Potter", "Sherlock Holmes", "Tam Quốc Diễn Nghĩa", "Doraemon"]
```

Hãy viết template Jinja2 để hiển thị danh sách này thành một `<ul>`.

---

# Tổng kết

Trong buổi học này, bạn đã nắm được:

* Sự khác nhau giữa `ul`, `ol` và `dl`.
* Cách sử dụng `li`, `dt`, `dd`.
* Các thuộc tính `type`, `start`, `reversed` của danh sách có thứ tự.
* Kỹ thuật tạo danh sách nhiều cấp (Nested List).
* Ứng dụng danh sách trong menu, mục lục, sidebar và giao diện Flask/Jinja2.

Ở **Buổi 4**, chúng ta sẽ học về **Liên kết (Links)** với thẻ `<a>`, bao gồm liên kết tuyệt đối, tương đối, liên kết nội bộ trong trang, mở tab mới, tải tệp và các kỹ thuật điều hướng thường dùng trong ứng dụng web.
