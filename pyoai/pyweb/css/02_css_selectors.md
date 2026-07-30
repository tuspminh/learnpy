# Buổi 2: CSS Selectors từ cơ bản đến nâng cao

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Hiểu Selector là gì.
> * Biết cách browser tìm phần tử bằng Selector.
> * Thành thạo tất cả selector cơ bản.
> * Thành thạo selector kết hợp.
> * Biết selector nào nên dùng trong dự án Flask/Jinja2.
> * Đọc được CSS của Bootstrap, Tailwind, AdminLTE...

---

# 1. Selector là gì?

Selector dùng để **chọn phần tử HTML** mà CSS sẽ áp dụng.

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

Selector là

```css
p
```

Browser hiểu là

> Hãy tìm tất cả thẻ `<p>`.

Kết quả

```
✓ <p>Python</p>

✓ <p>CSS</p>
```

---

# 2. Browser xử lý Selector như thế nào?

Ví dụ

```css
div p{
    color:red;
}
```

Browser sẽ

```
DOM Tree

html
 │
 body
 │
 div
 │
 p
```

Sau đó tìm

```
div

↓

bên trong div

↓

tìm p

↓

đổi màu đỏ
```

Trong trang HTML lớn có hàng chục nghìn phần tử, selector càng phức tạp thì browser càng phải thực hiện nhiều bước hơn. Với website thông thường, bạn ưu tiên **selector rõ ràng, dễ đọc** thay vì tối ưu quá sớm.

---

# 3. Universal Selector (*)

Dấu *

```css
*{
    color:red;
}
```

Nghĩa là

```
Chọn MỌI phần tử.
```

Ví dụ

```html
<h1>Hello</h1>

<p>Python</p>

<button>OK</button>
```

Kết quả

```
Hello      đỏ

Python     đỏ

OK          đỏ
```

### Ứng dụng

Reset CSS

```css
*{
    margin:0;
    padding:0;
}
```

Đây là cách rất phổ biến để loại bỏ khoảng cách mặc định mà trình duyệt thêm vào các phần tử.

---

# 4. Element Selector

Chọn theo tên thẻ.

Ví dụ

```css
p{
    color:blue;
}
```

HTML

```html
<h1>Hello</h1>

<p>A</p>

<p>B</p>
```

Kết quả

```
Hello

A màu xanh

B màu xanh
```

---

# 5. Class Selector

Class bắt đầu bằng dấu chấm

```css
.title{
    color:red;
}
```

HTML

```html
<h1 class="title">
Hello
</h1>
```

Có thể dùng nhiều lần

```html
<h1 class="title">One</h1>

<h2 class="title">Two</h2>

<p class="title">Three</p>
```

Tất cả đều đỏ.

## Đây là selector được dùng nhiều nhất trong thực tế.

---

# 6. ID Selector

Bắt đầu bằng #

```css
#header{
    background:blue;
}
```

HTML

```html
<div id="header">
Header
</div>
```

ID nên **duy nhất** trong một trang.

Không nên

```html
<div id="header"></div>

<div id="header"></div>
```

Điều này vi phạm chuẩn HTML và dễ gây lỗi khi dùng JavaScript hoặc CSS.

---

# 7. Class vs ID

Ví dụ

```html
<div id="menu">

</div>

<div class="menu">

</div>
```

Khác nhau

| Class          | ID          |
| -------------- | ----------- |
| Dùng nhiều lần | Chỉ một lần |
| .              | #           |
| Khuyên dùng    | Ít dùng hơn |

Trong các dự án hiện đại, CSS chủ yếu được viết theo **class**, còn **id** thường dành cho JavaScript hoặc liên kết (`#section-1`).

---

# 8. Multiple Selector

Có thể chọn nhiều selector

```css
h1,p,button{

    color:red;

}
```

HTML

```html
<h1>Hello</h1>

<p>Python</p>

<button>OK</button>
```

Tất cả đều đỏ.

---

# 9. Descendant Selector (dấu cách)

Đây là selector cực kỳ quan trọng.

```css
div p{

}
```

Nghĩa là

```
Chọn p nằm bên trong div
```

Ví dụ

```html
<div>

<p>A</p>

</div>

<p>B</p>
```

CSS

```css
div p{

color:red;

}
```

Kết quả

```
A đỏ

B bình thường
```

Browser hiểu

```
div

↓

tìm p bên trong
```

---

# 10. Child Selector (>)

Ví dụ

```css
div>p{

}
```

Khác với dấu cách.

HTML

```html
<div>

<p>A</p>

<section>

<p>B</p>

</section>

</div>
```

Nếu dùng

```css
div>p{

color:red;

}
```

Kết quả

```
A đỏ

B không đỏ
```

Vì

```
A

là con trực tiếp

div

↓

B

không phải con trực tiếp
```

---

# 11. Adjacent Sibling (+)

Ví dụ

```css
h1+p{

color:red;

}
```

HTML

```html
<h1>

Hello

</h1>

<p>

A

</p>

<p>

B

</p>
```

Chỉ

```
A đỏ
```

B không đỏ.

Vì

```
h1

↓

p đầu tiên
```

---

# 12. General Sibling (~)

Ví dụ

```css
h1~p{

color:blue;

}
```

HTML

```html
<h1>Hello</h1>

<p>A</p>

<p>B</p>

<p>C</p>
```

Kết quả

```
A xanh

B xanh

C xanh
```

Tất cả các thẻ `<p>` cùng cấp và đứng sau `<h1>` đều được chọn.

---

# 13. Attribute Selector

Đây là selector cực kỳ hữu ích khi làm việc với form.

HTML

```html
<input type="text">

<input type="password">

<input type="email">
```

CSS

```css
input[type="password"]{

border:2px solid red;

}
```

Chỉ ô password đổi viền.

---

Có thể dùng

```css
input[type="text"]
```

```css
a[target="_blank"]
```

```css
img[alt]
```

---

# 14. Một số Attribute Selector nâng cao

Bắt đầu bằng

```css
a[href^="https"]
```

Ví dụ

```html
<a href="https://example.com">HTTPS</a>
<a href="http://example.com">HTTP</a>
```

Chỉ liên kết HTTPS được chọn.

---

Kết thúc bằng

```css
img[src$=".png"]
```

Chỉ chọn ảnh có đuôi `.png`.

---

Chứa chuỗi

```css
a[href*="github"]
```

Chọn mọi liên kết có chứa `"github"` trong thuộc tính `href`.

---

# 15. Ví dụ hoàn chỉnh

## Cấu trúc dự án

```
lesson2/

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
    <title>Lesson 2 - CSS Selectors</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>

    <h1 class="title">Học CSS Selector</h1>

    <p>Đây là đoạn văn đầu tiên.</p>

    <div class="card">
        <p>Đoạn văn nằm trong card.</p>

        <section>
            <p>Đoạn văn trong section.</p>
        </section>
    </div>

    <input type="text" placeholder="Tên">

    <input type="password" placeholder="Mật khẩu">

    <button class="btn">
        Đăng nhập
    </button>

</body>
</html>
```

---

## style.css

```css
/* Reset */
*{
    margin:0;
    padding:0;
    box-sizing:border-box;
}

body{
    font-family:Arial,sans-serif;
    margin:40px;
}

/* Class selector */
.title{
    color:#1565c0;
    margin-bottom:20px;
}

/* Element selector */
p{
    margin:10px 0;
}

/* Descendant selector */
.card p{
    color:green;
}

/* Child selector */
.card>p{
    font-weight:bold;
}

/* Attribute selector */
input[type="password"]{
    border:2px solid crimson;
}

/* Button */
.btn{
    margin-top:20px;
    padding:10px 20px;
    background:#1565c0;
    color:white;
    border:none;
}
```

Khi mở trang:

* Tiêu đề có màu xanh.
* Mọi đoạn văn có khoảng cách trên dưới.
* Các đoạn văn trong `.card` có màu xanh lá.
* Chỉ đoạn văn là **con trực tiếp** của `.card` được in đậm.
* Ô nhập mật khẩu có viền đỏ.
* Nút "Đăng nhập" có nền xanh.

---

# 16. Best Practices

Trong các dự án **Flask + Jinja2** hoặc **Django**, hãy ưu tiên:

* Dùng **class** để định kiểu giao diện.
* Chỉ dùng **id** khi cần định danh duy nhất hoặc thao tác với JavaScript.
* Tránh viết selector quá dài như:

```css
body div main section article .content p span a{
    color:red;
}
```

Thay vào đó, hãy đặt class rõ ràng:

```css
.article-link{
    color:red;
}
```

Điều này giúp mã CSS dễ đọc, dễ bảo trì và ít phụ thuộc vào cấu trúc HTML.

---

# Bài tập thực hành

1. Tạo một trang HTML gồm:

   * Một tiêu đề.
   * Hai thẻ `div`, mỗi thẻ chứa hai đoạn văn.
   * Ba ô nhập liệu (`text`, `email`, `password`).
   * Hai nút bấm.

2. Viết CSS để:

   * Tô màu tiêu đề bằng class.
   * Đổi màu tất cả đoạn văn trong `div`.
   * In đậm chỉ các đoạn văn là **con trực tiếp** của `div`.
   * Đặt viền màu xanh cho `input[type="email"]`.
   * Đặt viền màu đỏ cho `input[type="password"]`.

3. Thử thay `div p` bằng `div > p` và quan sát sự khác biệt về các phần tử được chọn.

Ở **Buổi 3**, chúng ta sẽ học **Specificity (độ ưu tiên của CSS)**, hiểu chính xác vì sao hai quy tắc CSS xung đột, cách trình duyệt quyết định quy tắc nào thắng, và khi nào nên (hoặc không nên) dùng `!important`. Đây là nền tảng để gỡ lỗi CSS trong các dự án thực tế.
