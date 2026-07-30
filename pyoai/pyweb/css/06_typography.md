# Buổi 6: Typography (Phần 1) – `font-family`, `font-size`, `font-weight`, `font-style`

> **Mục tiêu**
>
> Sau buổi học này, bạn sẽ:
>
> * Hiểu typography là gì và vì sao nó quan trọng.
> * Thành thạo `font-family`.
> * Hiểu cơ chế Font Stack.
> * Thành thạo `font-size`.
> * Hiểu `font-weight`.
> * Hiểu `font-style`.
> * Biết cách xây dựng hệ thống font cho website Flask/Django/FastAPI.

---

# 1. Typography là gì?

Typography là nghệ thuật trình bày văn bản sao cho:

* Dễ đọc
* Đẹp
* Có thứ bậc
* Chuyên nghiệp

Ví dụ hai trang web có cùng nội dung nhưng khác typography:

```text
Website A

HELLO WORLD

Đây là website...
```

↓

```text
Khó đọc
```

---

```text
Website B

Hello World

Đây là website...
```

↓

```text
Rõ ràng

Khoảng cách hợp lý

Font đẹp
```

Người dùng thường đánh giá chất lượng một website chỉ trong vài giây đầu tiên, và typography là một trong những yếu tố tạo ấn tượng mạnh nhất.

---

# 2. Thuộc tính `font-family`

Đây là thuộc tính xác định kiểu chữ.

Ví dụ

```css
h1{
    font-family:Arial;
}
```

---

Có thể dùng nhiều font

```css
font-family:Arial, Helvetica, sans-serif;
```

Browser sẽ:

```text
Arial

↓

Có?

↓

Có

↓

Dùng Arial

↓

Không

↓

Helvetica

↓

Không

↓

sans-serif
```

Đây gọi là **Font Stack**.

---

# 3. Font Stack

Một Font Stack luôn nên có font dự phòng.

Ví dụ

```css
body{

font-family:

Arial,

Helvetica,

sans-serif;

}
```

Ý nghĩa

```text
Arial

↓

không có

↓

Helvetica

↓

không có

↓

sans-serif
```

---

Ví dụ khác

```css
font-family:

"Segoe UI",

Tahoma,

Geneva,

Verdana,

sans-serif;
```

Đây là một Font Stack phổ biến trên Windows.

---

# 4. Generic Font Family

Cuối Font Stack thường là một **Generic Family**.

Có 5 nhóm chính.

---

## Serif

Có chân.

Ví dụ

```text
Times New Roman

Georgia
```

Hình dung

```text
T

có chân
```

Thường dùng cho:

* Báo
* Sách
* Tài liệu

---

## Sans-serif

Không chân.

Ví dụ

```text
Arial

Helvetica

Roboto
```

Hiện đại hơn.

Được dùng rất nhiều trên website.

---

## Monospace

Mọi ký tự rộng bằng nhau.

Ví dụ

```text
i

████

W

████
```

Font

```text
Courier New

Consolas

Fira Code
```

Rất phù hợp cho:

* Code
* Terminal
* Console

Ví dụ

```css
code{

font-family:Consolas,monospace;

}
```

---

## Cursive

Giống chữ viết tay.

Ví dụ

```text
Hello
```

Dùng cho:

* Thiệp
* Logo
* Tiêu đề nghệ thuật

Không nên dùng cho đoạn văn dài.

---

## Fantasy

Font trang trí.

Ví dụ

```text
GAME

MOVIE

POSTER
```

Ít dùng trong website doanh nghiệp.

---

# 5. `font-size`

Điều khiển kích thước chữ.

Ví dụ

```css
p{

font-size:16px;

}
```

---

Khuyến nghị hiện nay

```css
html{

font-size:16px;

}
```

Sau đó

```css
h1{

font-size:2.5rem;

}
```

```css
h2{

font-size:2rem;

}
```

```css
p{

font-size:1rem;

}
```

---

# 6. Vì sao dùng `rem`?

Nếu sau này muốn tăng toàn bộ website

Chỉ cần

```css
html{

font-size:18px;

}
```

Mọi chữ sẽ tự tăng.

Đây là lý do hầu hết framework hiện đại ưu tiên `rem`.

---

# 7. `font-weight`

Điều khiển độ đậm.

Có thể dùng chữ

```css
font-weight:normal;

font-weight:bold;
```

Hoặc số.

```css
100

200

300

400

500

600

700

800

900
```

---

Bảng tham khảo

| Giá trị | Ý nghĩa     |
| ------- | ----------- |
| 100     | Thin        |
| 200     | Extra Light |
| 300     | Light       |
| 400     | Normal      |
| 500     | Medium      |
| 600     | Semi Bold   |
| 700     | Bold        |
| 800     | Extra Bold  |
| 900     | Black       |

---

Ví dụ

```css
h1{

font-weight:700;
}
```

---

# 8. Không phải font nào cũng hỗ trợ mọi trọng lượng

Ví dụ

```css
font-weight:950;
```

Nếu font chỉ có

```text
400

700
```

Browser sẽ chọn giá trị gần nhất.

Điều này đặc biệt quan trọng khi dùng font tùy chỉnh hoặc Google Fonts: bạn cần tải đúng các trọng lượng sẽ sử dụng.

---

# 9. `font-style`

Điều khiển kiểu chữ.

```css
font-style:normal;
```

---

```css
font-style:italic;
```

---

```css
font-style:oblique;
```

---

Ví dụ

```css
.quote{

font-style:italic;

}
```

---

Kết quả

```text
Đây là câu trích dẫn.
```

nghiêng.

---

# 10. Italic và Oblique khác nhau thế nào?

Nhiều người tưởng giống nhau.

Không hoàn toàn.

### Italic

Font được thiết kế riêng.

```text
Hello
```

↓

Phiên bản nghiêng do nhà thiết kế font tạo.

---

### Oblique

Browser chỉ nghiêng font bình thường.

```text
Hello
```

↓

Xoay nghiêng.

---

Đa số website dùng

```css
italic
```

---

# 11. Ví dụ hoàn chỉnh

## Cấu trúc

```text
lesson6/

│── index.html

│── style.css
```

---

## index.html

```html
<!DOCTYPE html>
<html lang="vi">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>Lesson 6</title>

<link
rel="stylesheet"
href="style.css">

</head>

<body>

<div class="container">

<h1>

Học Typography

</h1>

<h2>

CSS Font

</h2>

<p>

Typography giúp website chuyên nghiệp hơn.

</p>

<p class="quote">

"Learning never stops."

</p>

<code>

print("Hello CSS")

</code>

</div>

</body>

</html>
```

---

## style.css

```css
html{
    font-size:16px;
}

body{

    background:#f5f5f5;

    font-family:
        "Segoe UI",
        Arial,
        sans-serif;

    color:#333;
}

.container{

    width:80%;

    margin:auto;

    padding:2rem;

}

h1{

    font-size:2.5rem;

    font-weight:700;

}

h2{

    font-size:2rem;

    font-weight:600;

}

p{

    font-size:1rem;

    line-height:1.8;

}

.quote{

    font-style:italic;

    color:#666;

}

code{

    display:block;

    margin-top:20px;

    padding:1rem;

    background:#222;

    color:#00ff90;

    font-family:
        Consolas,
        monospace;

}
```

---

# 12. Hệ thống Typography chuyên nghiệp

Ví dụ

```css
html{

font-size:16px;

}

body{

font-size:1rem;

}

h1{

font-size:2.5rem;

}

h2{

font-size:2rem;

}

h3{

font-size:1.75rem;

}

h4{

font-size:1.5rem;

}

small{

font-size:.875rem;
}
```

Đây là cách tổ chức thường thấy trong các Design System, giúp giao diện có tính nhất quán.

---

# 13. Những lỗi phổ biến

## Sai 1

```css
font-family:Arial;
```

Không có font dự phòng.

Nên

```css
font-family:

Arial,

Helvetica,

sans-serif;
```

---

## Sai 2

Toàn bộ dùng px.

```css
font-size:18px;
```

Nên dùng

```css
font-size:1rem;
```

để dễ mở rộng và hỗ trợ người dùng thay đổi kích thước chữ.

---

## Sai 3

Dùng quá nhiều font.

```text
Arial

Roboto

Verdana

Georgia

Tahoma

Courier
```

Một website nên dùng **1–2 font chính**, tối đa **3** trong hầu hết trường hợp.

---

## Sai 4

Đặt `font-weight:900` cho mọi tiêu đề.

Chữ sẽ nặng nề và khó đọc.

Thông thường:

```text
Heading

↓

600–700

Paragraph

↓

400
```

---

# 14. Best Practices

Trong dự án Flask/Django/FastAPI:

✔ Body

```css
font-family:

"Segoe UI",

Arial,

sans-serif;
```

---

✔ Code

```css
font-family:

Consolas,

monospace;
```

---

✔ Font-size

```css
rem
```

---

✔ Font-weight

```text
400

600

700
```

Ba mức này thường đã đủ cho hầu hết giao diện.

---

# Tổng kết

Bạn đã học:

* Typography là gì.
* `font-family`.
* Font Stack.
* Generic Font Families.
* `font-size`.
* `font-weight`.
* `font-style`.
* Xây dựng hệ thống typography chuyên nghiệp.

---

# Bài tập thực hành

## Bài 1

Tạo một trang gồm:

* `h1`
* `h2`
* `h3`
* `p`
* `code`

Thiết lập:

* `body` dùng Font Stack `"Segoe UI", Arial, sans-serif`.
* `code` dùng `Consolas, monospace`.
* Kích thước chữ sử dụng `rem`.

---

## Bài 2

Tạo ba đoạn văn:

* Đoạn 1: `font-weight:300`
* Đoạn 2: `font-weight:500`
* Đoạn 3: `font-weight:700`

Quan sát sự khác biệt và kiểm tra xem font bạn đang dùng có hỗ trợ đầy đủ các trọng lượng này không.

---

## Bài 3

Tạo một khối trích dẫn (`blockquote` hoặc `div`) với:

* `font-style: italic`
* `font-size: 1.2rem`
* `font-weight: 400`

Thêm nền sáng và khoảng đệm để tạo cảm giác như một câu trích dẫn trong bài viết.

---

## Mini Project

Thiết kế một **trang Blog Article** gồm:

* Tiêu đề bài viết.
* Tên tác giả.
* Ngày đăng.
* Nội dung gồm nhiều đoạn văn.
* Một đoạn mã nguồn (`<code>` hoặc `<pre>`).
* Một câu trích dẫn.

Yêu cầu:

* Chỉ sử dụng **2 Font Family** (một cho nội dung, một cho mã nguồn).
* Dùng `rem` cho toàn bộ typography.
* Sử dụng `font-weight` để tạo rõ thứ bậc giữa tiêu đề, phụ đề và nội dung.
* Sử dụng `italic` cho phần trích dẫn.

Ở **Buổi 7**, chúng ta sẽ tiếp tục phần Typography với các thuộc tính quan trọng như **`line-height`**, **`letter-spacing`**, **`word-spacing`**, **`text-align`**, **`text-indent`**, **`text-transform`**, **`text-decoration`** và **`text-shadow`**, đồng thời học cách tạo các đoạn văn dễ đọc và chuyên nghiệp như trên các website lớn.
