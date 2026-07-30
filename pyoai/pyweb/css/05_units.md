# Buổi 5: CSS Units (Đơn vị đo trong CSS)

> **Mục tiêu**
>
> Sau buổi học này, bạn sẽ:
>
> * Hiểu sự khác nhau giữa đơn vị **tuyệt đối** và **tương đối**.
> * Thành thạo `px`, `%`, `em`, `rem`, `vw`, `vh`, `vmin`, `vmax`, `ch`, `ex`.
> * Biết khi nào nên dùng từng đơn vị.
> * Biết cách xây dựng giao diện Responsive.
> * Tránh các lỗi phổ biến khi dùng `em` và `%`.

---

# 1. CSS Unit là gì?

CSS Unit (đơn vị đo) dùng để xác định kích thước của các thuộc tính như:

```css
width
height
margin
padding
font-size
border-radius
gap
top
left
...
```

Ví dụ

```css
width:300px;

font-size:18px;

padding:20px;
```

---

# 2. Hai nhóm đơn vị

CSS chia thành hai nhóm lớn.

```
Units

├── Absolute Units
│      │
│      ├── px
│      ├── cm
│      ├── mm
│      ├── in
│      └── pt
│
└── Relative Units
       │
       ├── %
       ├── em
       ├── rem
       ├── vw
       ├── vh
       ├── vmin
       ├── vmax
       ├── ch
       └── ex
```

Trong lập trình web hiện đại:

* Dùng nhiều: `px`, `%`, `rem`, `vw`, `vh`
* Dùng khá nhiều: `em`
* Dùng ít hơn: `ch`, `vmin`, `vmax`, `ex`
* Hầu như không dùng: `cm`, `mm`, `in`

---

# 3. px (Pixel)

Đây là đơn vị phổ biến nhất.

```css
h1{
    font-size:40px;
}
```

Nghĩa là

```
Chiều cao chữ

≈ 40 pixel
```

Ví dụ

```css
.card{

width:400px;

height:300px;

}
```

## Ưu điểm

* Dễ hiểu
* Dễ kiểm soát
* Chính xác

## Nhược điểm

* Không linh hoạt bằng `rem`
* Ít thích nghi với thay đổi kích thước chữ gốc

---

# 4. %

Đơn vị phần trăm luôn phụ thuộc vào phần tử cha.

Ví dụ

```html
<div class="parent">

<div class="child">

</div>

</div>
```

CSS

```css
.parent{

width:600px;

}

.child{

width:50%;

}
```

Browser tính

```
600px

↓

50%

↓

300px
```

Nếu cha đổi thành

```css
width:800px;
```

thì con sẽ thành

```
400px
```

Đây là lý do `%` rất hữu ích trong bố cục linh hoạt.

---

# 5. em

Đây là đơn vị khiến rất nhiều người mới học bị nhầm.

`1em` = **font-size của phần tử cha** (đối với `font-size`) hoặc **font-size của chính phần tử** (đối với đa số thuộc tính khác như `padding`, `margin`).

Ví dụ

```css
.parent{

font-size:20px;

}

.child{

font-size:2em;

}
```

Browser tính

```
2 × 20

=

40px
```

---

Ví dụ lồng nhau

```html
<div class="a">

<div class="b">

<div class="c">

Hello

</div>

</div>

</div>
```

```css
.a{

font-size:20px;

}

.b{

font-size:2em;

}

.c{

font-size:2em;

}
```

Kết quả

```
.a

20px

↓

.b

40px

↓

.c

80px
```

Đây gọi là **hiệu ứng nhân (compounding)**.

---

# 6. rem

Đây là đơn vị được khuyến nghị sử dụng cho kích thước chữ.

`rem` = **Root em**

Nó luôn dựa trên font-size của phần tử `<html>`.

Ví dụ

```css
html{

font-size:16px;

}
```

```css
h1{

font-size:2rem;

}
```

Browser

```
2 × 16

=

32px
```

Điểm quan trọng:

Dù lồng nhiều tầng

```
div

↓

div

↓

div

↓

div
```

thì

```css
2rem
```

vẫn luôn là

```
32px
```

---

# 7. So sánh em và rem

| Thuộc tính                | em                        | rem         |
| ------------------------- | ------------------------- | ----------- |
| Dựa vào                   | Cha (đối với `font-size`) | `<html>`    |
| Có nhân nhiều tầng        | Có                        | Không       |
| Ổn định                   | Không bằng rem            | Rất ổn định |
| Khuyến nghị cho font-size | Không nhiều               | ✔           |

---

# 8. vw (Viewport Width)

Viewport = vùng hiển thị của trình duyệt.

Ví dụ

```css
width:50vw;
```

Nếu màn hình rộng

```
1200px
```

thì

```
50%

↓

600px
```

---

Ví dụ

```css
.hero{

width:100vw;

}
```

Luôn rộng bằng cửa sổ trình duyệt.

---

# 9. vh (Viewport Height)

```css
height:100vh;
```

Nếu trình duyệt cao

```
900px
```

thì

```
height

=

900px
```

Thường dùng

```css
.hero{

height:100vh;

}
```

để tạo màn hình chào (Hero Section) chiếm toàn bộ chiều cao.

---

# 10. vmin và vmax

Giả sử

```
Màn hình

1200 × 800
```

```
vmin

↓

800
```

```
1vmin

=

8px
```

---

```
vmax

↓

1200
```

```
1vmax

=

12px
```

Ứng dụng:

* Hiệu ứng toàn màn hình.
* Logo co giãn theo màn hình.
* Typography linh hoạt.

---

# 11. ch

`ch` ≈ chiều rộng của ký tự **0** trong font hiện tại.

Ví dụ

```css
input{

width:30ch;

}
```

Có nghĩa

```
Đủ khoảng

30 ký tự
```

Rất hữu ích với:

* Input nhập mã.
* OTP.
* Mã giảm giá.
* Serial.
* Console.

---

# 12. ex

`1ex`

≈ chiều cao chữ thường **x**.

Đơn vị này hiếm dùng trong thực tế.

---

# 13. Ví dụ hoàn chỉnh

## Cấu trúc

```
lesson5/

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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lesson 5 - CSS Units</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>

<div class="container">

<h1>CSS Units</h1>

<p>
Đây là bài học về các đơn vị đo trong CSS.
</p>

<div class="card">

Nội dung card

</div>

<input
type="text"
placeholder="Nhập tên">

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
    font-family:Arial,sans-serif;
    background:#f5f5f5;
}

.container{

width:80%;

margin:auto;

padding:2rem;

}

h1{

font-size:2.5rem;

}

p{

font-size:1rem;

line-height:1.8;

}

.card{

width:60%;

padding:1.5em;

background:#fff;

border-radius:10px;

margin-top:20px;

}

input{

margin-top:20px;

width:30ch;

padding:.8rem;

}
```

---

# 14. Khi nào dùng đơn vị nào?

| Mục đích                                | Đơn vị khuyến nghị |
| --------------------------------------- | ------------------ |
| Font chữ                                | `rem`              |
| Khoảng cách (margin, padding)           | `rem`, `em`        |
| Chiều rộng linh hoạt                    | `%`                |
| Hero toàn màn hình                      | `vh`, `vw`         |
| Input theo số ký tự                     | `ch`               |
| Icon hoặc thành phần cần tỷ lệ theo chữ | `em`               |
| Kích thước cố định                      | `px`               |

---

# 15. Những lỗi phổ biến

## Sai 1

Dùng toàn bộ bằng px

```css
font-size:16px;

margin:20px;

padding:20px;
```

Website sẽ khó mở rộng khi người dùng thay đổi cỡ chữ mặc định.

---

## Sai 2

Lạm dụng em

```css
.parent{

font-size:2em;

}

.child{

font-size:2em;

}

.grandchild{

font-size:2em;
}
```

Kết quả

```
16

↓

32

↓

64

↓

128
```

Chữ phóng to ngoài ý muốn.

---

## Sai 3

Dùng 100vw cho mọi phần tử

```css
width:100vw;
```

Có thể gây thanh cuộn ngang vì `100vw` tính cả chiều rộng của thanh cuộn (scrollbar) trên một số trình duyệt. Trong nhiều trường hợp, `width: 100%` sẽ phù hợp hơn.

---

# 16. Best Practices

Trong các dự án **Flask**, **Django** hoặc **FastAPI**:

* ✔ Font chữ: `rem`
* ✔ Margin và Padding: `rem`
* ✔ Chiều rộng bố cục: `%` hoặc `max-width`
* ✔ Hero Section: `100vh`
* ✔ Ảnh: `max-width:100%`
* ✔ Không lạm dụng `px` cho mọi thứ.
* ✔ Chỉ dùng `em` khi muốn một thành phần tỷ lệ theo kích thước chữ của nó (ví dụ icon cạnh văn bản).

---

# Tổng kết

Hôm nay bạn đã học:

* Absolute Units và Relative Units.
* `px`, `%`, `em`, `rem`.
* `vw`, `vh`, `vmin`, `vmax`.
* `ch`, `ex`.
* Sự khác nhau giữa `em` và `rem`.
* Cách chọn đơn vị phù hợp trong dự án thực tế.

---

# Bài tập thực hành

## Bài 1

Tạo một trang có:

* Tiêu đề `font-size: 2.5rem`.
* Đoạn văn `font-size: 1rem`.
* Một thẻ `div` có `width: 70%`.
* Một nút có `padding: 1rem 2rem`.

---

## Bài 2

Tạo hai thẻ:

* `.parent` có `font-size: 20px`.
* `.child` dùng `font-size: 2em`.
* Một phần tử khác dùng `font-size: 2rem`.

So sánh kết quả và giải thích vì sao hai kích thước có thể khác nhau nếu thay đổi `font-size` của phần tử cha.

---

## Bài 3

Tạo một **Hero Section**:

* Chiều rộng `100vw`.
* Chiều cao `100vh`.
* Tiêu đề `font-size: 4rem`.
* Nút có `padding` bằng `rem`.

Thử thay đổi kích thước cửa sổ trình duyệt và quan sát sự khác biệt giữa các đơn vị `%`, `vw`, `vh` và `rem`.

---

## Mini Project

Thiết kế một **Landing Page** đơn giản gồm:

* Thanh điều hướng (Navigation).
* Hero Section.
* Khu vực giới thiệu.
* Nút "Bắt đầu".

Yêu cầu:

* Sử dụng `rem` cho toàn bộ typography.
* Dùng `%` hoặc `max-width` cho bố cục.
* Dùng `100vh` cho Hero Section.
* Dùng `ch` cho ô tìm kiếm hoặc ô nhập liệu.
* Hạn chế tối đa việc dùng `px`, chỉ dùng khi thực sự cần (ví dụ: viền `1px`).

Ở **Buổi 6**, chúng ta sẽ bắt đầu phần **Typography**, tìm hiểu chi tiết về `font-family`, `font-size`, `font-weight` và `font-style`, đồng thời học cách xây dựng hệ thống chữ nhất quán cho một website chuyên nghiệp.
