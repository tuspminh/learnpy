# Buổi 1: CSS là gì? Cách hoạt động của CSS

> Mục tiêu buổi học:
>
> Sau buổi này, bạn sẽ hiểu:
>
> * CSS là gì và tại sao cần CSS.
> * Trình duyệt render một trang web như thế nào.
> * CSS Rule gồm những thành phần nào.
> * Selector, Property, Value.
> * Inline, Internal, External CSS.
> * Cascade (quy tắc ghi đè).
> * Viết được trang HTML có CSS hoàn chỉnh.

---

# 1. CSS là gì?

CSS (Cascading Style Sheets) là ngôn ngữ dùng để mô tả cách hiển thị của tài liệu HTML.

Nếu HTML là **bộ xương**, thì CSS chính là **quần áo, màu sắc và cách trang trí**.

Ví dụ

Không có CSS

```
Hello World

Đây là đoạn văn.
```

Có CSS

```
Hello World
(màu xanh, cỡ 40px)

Đây là đoạn văn
(font đẹp, căn giữa, nền xám...)
```

CSS không thay đổi nội dung.

CSS chỉ thay đổi cách hiển thị.

---

# 2. HTML và CSS phối hợp như thế nào?

Giả sử có file

```
index.html
```

```html
<h1>Hello CSS</h1>
```

Trình duyệt sẽ hiển thị

```
Hello CSS
```

Nếu thêm CSS

```css
h1{
    color:red;
}
```

thì sẽ hiển thị

```
Hello CSS (màu đỏ)
```

HTML vẫn giữ nguyên.

Chỉ cách hiển thị thay đổi.

---

# 3. Browser Rendering

Đây là kiến thức rất quan trọng.

Mỗi lần mở website:

```
https://example.com
```

Browser sẽ làm các bước sau.

```
        Người dùng
             │
             ▼
      Gõ URL vào Browser
             │
             ▼
      Gửi HTTP Request
             │
             ▼
        Server trả HTML
             │
             ▼
      Browser đọc HTML
             │
             ▼
      Phát hiện file CSS
             │
             ▼
      Download CSS
             │
             ▼
      Parse CSS
             │
             ▼
      Ghép HTML + CSS
             │
             ▼
      Render giao diện
```

Đó gọi là

```
Rendering Pipeline
```

---

# 4. Browser tạo DOM

Ví dụ

```html
<html>

<body>

<h1>Hello</h1>

<p>CSS</p>

</body>

</html>
```

Browser sẽ tạo cây

```
html
 │
 └── body
      │
      ├── h1
      │     │
      │     └── Hello
      │
      └── p
            │
            └── CSS
```

Đây gọi là

```
DOM Tree
```

DOM = Document Object Model

---

# 5. Browser tạo CSSOM

CSS

```css
h1{
    color:red;
}

p{
    color:blue;
}
```

Browser tạo

```
CSSOM

h1
 └── color:red

p
 └── color:blue
```

---

# 6. DOM + CSSOM = Render Tree

```
DOM
 │
 │
 ├────────────┐
 │            │
 ▼            ▼
CSSOM      DOM Tree

      │
      ▼

 Render Tree
```

Render Tree mới là thứ được dùng để vẽ lên màn hình.

---

# 7. CSS Rule

Ví dụ

```css
h1{

    color:red;

}
```

Một Rule gồm

```
Selector

h1

Declaration

color:red;
```

Trong Declaration lại gồm

```
Property

color

Value

red
```

Hình minh họa

```
h1{

    color:red;

    font-size:40px;

}
```

```
Selector

h1

↓

Property
color

↓

Value
red

Property
font-size

↓

Value
40px
```

---

# 8. Selector

Selector nghĩa là

```
Chọn phần tử
```

Ví dụ

HTML

```html
<h1>Hello</h1>

<p>Python</p>

<p>CSS</p>
```

CSS

```css
p{

    color:blue;

}
```

Selector

```
p
```

sẽ chọn

```
<p>Python</p>

<p>CSS</p>
```

---

# 9. Property

Property là thuộc tính.

Ví dụ

```css
color
```

```
font-size
```

```
background
```

```
width
```

```
height
```

...

---

# 10. Value

Property luôn đi cùng Value.

Ví dụ

```css
color:red;
```

Property

```
color
```

Value

```
red
```

Ví dụ

```css
font-size:20px;
```

Property

```
font-size
```

Value

```
20px
```

---

# 11. Comment

```css
/*

Đây là comment

*/
```

Ví dụ

```css
/* Header */

h1{

    color:red;

}
```

Comment không ảnh hưởng tới giao diện, nhưng rất hữu ích để ghi chú hoặc chia nhóm mã CSS.

---

# 12. Ba cách sử dụng CSS

## Cách 1. Inline CSS

```html
<h1 style="color:red;">
    Hello
</h1>
```

Ưu điểm

* Nhanh
* Dễ thử nghiệm

Nhược điểm

* Khó bảo trì
* Không tái sử dụng
* Không nên dùng trong dự án lớn

---

## Cách 2. Internal CSS

```html
<!DOCTYPE html>

<html>

<head>

<style>

h1{

    color:red;

}

</style>

</head>

<body>

<h1>Hello</h1>

</body>

</html>
```

CSS được viết ngay trong thẻ `<style>`.

---

## Cách 3. External CSS (Khuyến nghị)

index.html

```html
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>CSS External</title>

    <link rel="stylesheet" href="style.css">
</head>

<body>

<h1>Hello CSS</h1>

<p>Python Developer</p>

</body>

</html>
```

style.css

```css
h1{
    color: crimson;
}

p{
    color: steelblue;
}
```

Đây là cách sử dụng phổ biến trong các dự án thực tế vì giúp tách biệt nội dung (HTML) và giao diện (CSS), dễ tái sử dụng và bảo trì.

---

# 13. Cascade (Quy tắc ghi đè)

"C" trong CSS là **Cascading**.

Nếu nhiều quy tắc cùng áp dụng cho một phần tử, trình duyệt sẽ quyết định quy tắc nào được ưu tiên.

Ví dụ:

```html
<!DOCTYPE html>
<html>
<head>
<style>

h1{
    color:blue;
}

h1{
    color:red;
}

</style>
</head>

<body>

<h1>Hello CSS</h1>

</body>

</html>
```

Kết quả:

```
Hello CSS
```

sẽ có màu **đỏ**.

Vì hai selector có cùng độ ưu tiên nên quy tắc xuất hiện **sau** sẽ ghi đè quy tắc trước.

> Các quy tắc ưu tiên phức tạp hơn (Specificity, `!important`, kế thừa...) sẽ được học chi tiết ở các buổi tiếp theo.

---

# 14. Ví dụ hoàn chỉnh

## Cấu trúc thư mục

```
lesson1/

│── index.html
│── style.css
```

### index.html

```html
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Buổi 1 - CSS</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>

    <h1>Chào mừng đến với CSS</h1>

    <p>
        Đây là ví dụ đầu tiên về CSS.
    </p>

    <button>Bấm vào đây</button>

</body>
</html>
```

### style.css

```css
/* Thiết lập chung cho toàn trang */
body{
    font-family: Arial, Helvetica, sans-serif;
    background:#f5f5f5;
    margin:40px;
}

/* Tiêu đề */
h1{
    color:#1565c0;
}

/* Đoạn văn */
p{
    color:#555;
    font-size:18px;
}

/* Nút bấm */
button{
    background:#1565c0;
    color:white;
    border:none;
    padding:10px 20px;
    font-size:16px;
    cursor:pointer;
}

/* Hiệu ứng khi rê chuột */
button:hover{
    background:#0d47a1;
}
```

Khi mở `index.html`, bạn sẽ thấy một trang web đơn giản với nền xám nhạt, tiêu đề màu xanh, đoạn văn dễ đọc và nút bấm có hiệu ứng đổi màu khi đưa chuột vào.

---

# 15. Những lỗi phổ biến

1. **Quên liên kết file CSS**

```html
<link rel="stylesheet" href="style.css">
```

2. **Sai tên hoặc đường dẫn file**

Ví dụ:

```
style.css
```

nhưng lại ghi:

```html
<link rel="stylesheet" href="styles.css">
```

3. **Quên dấu `;` giữa các thuộc tính**

```css
/* Sai */
h1{
    color:red
    font-size:40px;
}

/* Đúng */
h1{
    color:red;
    font-size:40px;
}
```

4. **Quên đóng ngoặc nhọn**

```css
/* Sai */
h1{
    color:red;

/* Đúng */
h1{
    color:red;
}
```

---

# Tổng kết buổi 1

Bạn đã nắm được:

* CSS là gì và vai trò của CSS.
* Quy trình render của trình duyệt: **HTML → DOM**, **CSS → CSSOM**, sau đó kết hợp thành **Render Tree** để hiển thị giao diện.
* Cấu trúc của một CSS Rule gồm **Selector**, **Property** và **Value**.
* Ba cách áp dụng CSS: **Inline**, **Internal** và **External** (khuyến nghị dùng trong dự án).
* Khái niệm **Cascade** và quy tắc ghi đè cơ bản.
* Cách tạo một dự án HTML + CSS đơn giản và chạy trực tiếp trên trình duyệt.

---

# Bài tập thực hành

1. Tạo một trang `index.html` có:

   * Tiêu đề (`h1`).
   * Hai đoạn văn (`p`).
   * Một nút (`button`).

2. Viết file `style.css` để:

   * Đổi màu tiêu đề.
   * Đặt nền trang thành màu sáng.
   * Thay đổi kích thước chữ của đoạn văn.
   * Thiết kế nút có màu nền, chữ trắng và hiệu ứng đổi màu khi rê chuột.

3. Thử áp dụng cùng một thuộc tính `color` cho `h1` bằng cả Inline, Internal và External CSS, sau đó quan sát quy tắc Cascade để xem kiểu nào được ưu tiên.

Ở **Buổi 2**, chúng ta sẽ học **CSS Selectors** một cách hệ thống, từ các selector cơ bản đến các tổ hợp mạnh mẽ như **Descendant**, **Child**, **Sibling** và **Attribute Selector**, giúp bạn chọn đúng phần tử trong những trang HTML phức tạp.
