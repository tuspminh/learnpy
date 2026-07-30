# Khóa học HTML bài bản dành cho Python Developer

# Buổi 2: Text & Heading - Các thẻ văn bản trong HTML

## Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu cách HTML biểu diễn văn bản.
* Biết sử dụng đúng các thẻ Heading.
* Biết khi nào dùng `<strong>` thay vì `<b>`.
* Biết khi nào dùng `<em>` thay vì `<i>`.
* Hiểu Semantic HTML.
* Viết được một bài viết HTML hoàn chỉnh.

---

# 1. Văn bản trong HTML

Một trang web chủ yếu là văn bản.

Ví dụ:

```
Tên sản phẩm

Giá bán

Mô tả

Liên hệ
```

HTML có rất nhiều thẻ để biểu diễn các loại văn bản khác nhau.

Ví dụ:

```html
<h1>Python Tutorial</h1>

<p>Đây là khóa học Python.</p>

<strong>Quan trọng</strong>

<em>Ghi chú</em>
```

---

# 2. Heading

Heading là tiêu đề.

HTML có:

```
h1
h2
h3
h4
h5
h6
```

Trong đó

```
h1

↓

Lớn nhất
```

```
h6

↓

Nhỏ nhất
```

---

## Ví dụ

```html
<h1>Python</h1>

<h2>Flask</h2>

<h3>Jinja2</h3>

<h4>HTML</h4>

<h5>CSS</h5>

<h6>JavaScript</h6>
```

Hiển thị

```
Python

    Flask

        Jinja2

            HTML

                CSS

                    JavaScript
```

---

# 3. Ý nghĩa của Heading

Heading **không chỉ để phóng to chữ**.

Sai:

```html
<h1>Trang chủ</h1>

<h1>Sản phẩm</h1>

<h1>Liên hệ</h1>

<h1>Tin tức</h1>
```

Đây là cấu trúc không hợp lý.

Đúng:

```html
<h1>Khóa học Python</h1>

<h2>Giới thiệu</h2>

<h2>Nội dung</h2>

<h2>Giảng viên</h2>

<h2>Đăng ký</h2>
```

---

# 4. Quy tắc Heading

Giống như một cuốn sách.

```
Cuốn sách

↓

Chương

↓

Mục

↓

Tiểu mục
```

HTML cũng vậy.

```
h1

↓

h2

↓

h3

↓

h4
```

Ví dụ

```html
<h1>Python</h1>

<h2>Flask</h2>

<h3>Routing</h3>

<h3>Template</h3>

<h2>Django</h2>

<h3>Model</h3>
```

---

# 5. Paragraph

Đoạn văn.

Ví dụ

```html
<p>
Python là ngôn ngữ lập trình phổ biến.
</p>

<p>
Flask là framework web.
</p>
```

Kết quả

```
Python là ngôn ngữ lập trình phổ biến.

Flask là framework web.
```

Mỗi `<p>` là một đoạn riêng.

---

# 6. `<br>`

Xuống dòng.

Ví dụ

```html
<p>
Xin chào<br>
Tôi là Nam<br>
Tôi học Python
</p>
```

Hiển thị

```
Xin chào
Tôi là Nam
Tôi học Python
```

---

# 7. `<hr>`

Đường kẻ ngang.

Ví dụ

```html
<p>Phần 1</p>

<hr>

<p>Phần 2</p>
```

Hiển thị

```
Phần 1

-------------------------

Phần 2
```

---

# 8. `<strong>`

Đánh dấu nội dung quan trọng.

Ví dụ

```html
<p>

<strong>Cảnh báo:</strong>

Không chia sẻ mật khẩu.

</p>
```

Hiển thị

**Cảnh báo:** Không chia sẻ mật khẩu.

---

# 9. `<b>`

In đậm.

Ví dụ

```html
<b>Python</b>
```

Hiển thị

**Python**

---

## Khác nhau

Sai lầm của nhiều người:

```
strong

=

b
```

Không đúng.

`<strong>`

```
Có ý nghĩa

Semantic
```

`<b>`

```
Chỉ in đậm

Không mang ý nghĩa
```

---

Ví dụ

```html
<p>

<strong>Cảnh báo</strong>

</p>
```

Google hiểu

```
Đây là thông tin quan trọng
```

Nếu

```html
<b>Cảnh báo</b>
```

Google chỉ hiểu

```
Đây là chữ đậm
```

---

# 10. `<em>`

Nhấn mạnh.

Ví dụ

```html
<p>

Bạn nên học

<em>HTML</em>

trước CSS.

</p>
```

Hiển thị

Bạn nên học *HTML* trước CSS.

---

# 11. `<i>`

In nghiêng.

Ví dụ

```html
<i>Python</i>
```

Hiển thị

*Python*

---

## Khác nhau

```
em

↓

Nhấn mạnh

Semantic
```

```
i

↓

Chỉ in nghiêng
```

---

# 12. `<mark>`

Tô vàng.

Ví dụ

```html
<p>

HTML rất

<mark>quan trọng</mark>

đối với Web.

</p>
```

Hiển thị

HTML rất ==quan trọng== đối với Web.

---

# 13. `<small>`

Chữ nhỏ.

Ví dụ

```html
<p>

Giá:

500.000₫

<small>Đã bao gồm VAT</small>

</p>
```

---

# 14. `<sup>`

Chỉ số trên.

Ví dụ

```html
x<sup>2</sup>
```

Hiển thị

```
x²
```

---

# 15. `<sub>`

Chỉ số dưới.

Ví dụ

```html
H<sub>2</sub>O
```

Hiển thị

```
H₂O
```

---

# 16. Ví dụ tổng hợp

```html
<!DOCTYPE html>
<html lang="vi">

<head>
    <meta charset="UTF-8">
    <title>Bài học HTML</title>
</head>

<body>

<h1>Học HTML</h1>

<p>

HTML là nền tảng của Web.

</p>

<h2>Vì sao nên học?</h2>

<p>

<strong>HTML</strong>

là bước đầu tiên để học

<em>Flask</em>

và

<em>Jinja2</em>.

</p>

<hr>

<p>

Công thức:

x<sup>2</sup>

+

y<sup>2</sup>

</p>

<p>

Nước:

H<sub>2</sub>O

</p>

<p>

<mark>Quan trọng</mark>

Không bỏ qua HTML.

</p>

<p>

<small>

© 2026 Python Course

</small>

</p>

</body>

</html>
```

---

# 17. Cấu trúc Heading chuẩn cho bài viết

```html
<h1>Học Flask từ cơ bản</h1>

<p>Giới thiệu khóa học.</p>

<h2>Flask là gì?</h2>

<p>...</p>

<h2>Cài đặt Flask</h2>

<p>...</p>

<h3>Tạo Virtual Environment</h3>

<p>...</p>

<h3>Cài Flask</h3>

<p>...</p>

<h2>Ví dụ đầu tiên</h2>

<p>...</p>
```

Đây là cấu trúc mà các công cụ tìm kiếm và trình đọc màn hình dễ hiểu.

---

# 18. Những lỗi người mới thường mắc

❌ Dùng Heading chỉ để tăng kích thước chữ:

```html
<h3>Màu đỏ</h3>
```

Muốn chữ to hay nhỏ hãy dùng CSS, không dùng Heading sai mục đích.

---

❌ Dùng nhiều `<br>` để tạo khoảng cách:

```html
<p>Dòng 1</p>
<br>
<br>
<br>
<p>Dòng 2</p>
```

Khoảng cách giữa các phần nên được xử lý bằng CSS (`margin`, `padding`).

---

❌ Dùng `<b>` thay cho `<strong>` khi muốn nhấn mạnh ý nghĩa:

```html
<b>Lưu ý:</b>
```

Nên dùng:

```html
<strong>Lưu ý:</strong>
```

---

❌ Bỏ qua cấu trúc Heading:

```html
<h1>Trang chủ</h1>
<h4>Sản phẩm</h4>
```

Nên đi tuần tự:

```html
<h1>Trang chủ</h1>
<h2>Sản phẩm</h2>
```

---

# 19. HTML và Jinja2

Trong Flask, bạn sẽ thường kết hợp các thẻ văn bản với cú pháp Jinja2:

```html
<h1>{{ title }}</h1>

<p>Xin chào {{ username }}</p>

<p>

<strong>Email:</strong>

{{ email }}

</p>
```

Khi render:

```python
return render_template(
    "index.html", title="Trang chủ", username="Garden Dau", email="garden@example.com"
)
```

Kết quả:

```text
Trang chủ

Xin chào Garden Dau

Email: garden@example.com
```

---

# Bài tập thực hành

## Bài 1

Tạo trang giới thiệu bản thân gồm:

* Một tiêu đề (`<h1>`)
* Hai tiêu đề phụ (`<h2>`)
* Ba đoạn văn (`<p>`)

---

## Bài 2

Viết một bài giới thiệu về Python, trong đó sử dụng:

* `<strong>`
* `<em>`
* `<mark>`

ít nhất một lần mỗi thẻ.

---

## Bài 3

Viết các công thức sau bằng HTML:

* x³ + y²
* CO₂
* H₂SO₄
* a² + b² = c²

Sử dụng đúng `<sup>` và `<sub>`.

---

## Bài 4

Tạo một bài viết ngắn với cấu trúc:

```text
H1

├── H2
│   ├── H3
│   └── H3
└── H2
    └── H3
```

Mỗi mục có ít nhất một đoạn văn mô tả.

---

## Tóm tắt buổi học

Bạn đã học:

* Cách sử dụng các thẻ văn bản cơ bản: `h1`–`h6`, `p`, `br`, `hr`.
* Sự khác nhau giữa `<strong>` và `<b>`, giữa `<em>` và `<i>`.
* Các thẻ `mark`, `small`, `sup`, `sub`.
* Cách xây dựng cấu trúc Heading đúng chuẩn Semantic HTML.
* Cách kết hợp các thẻ văn bản với Jinja2 trong ứng dụng Flask.

Ở **Buổi 3**, chúng ta sẽ học **Danh sách (Lists)**, bao gồm `ul`, `ol`, `li`, `dl`, `dt`, `dd`, cùng các kỹ thuật lồng danh sách và ứng dụng trong menu điều hướng, mục lục và trình bày dữ liệu.
