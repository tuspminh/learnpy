# Buổi 4: Màu sắc trong CSS (Color)

> **Mục tiêu**
>
> Sau buổi học này, bạn sẽ:
>
> * Hiểu browser biểu diễn màu như thế nào.
> * Thành thạo tất cả cách khai báo màu trong CSS.
> * Biết khi nào nên dùng HEX, RGB, HSL.
> * Hiểu Alpha (độ trong suốt).
> * Biết các Best Practices khi thiết kế giao diện.
> * Xây dựng được một giao diện có phối màu đẹp.

---

# 1. Màu trong máy tính hoạt động như thế nào?

Màn hình máy tính không dùng sơn để tạo màu.

Mỗi điểm ảnh (Pixel) gồm 3 đèn LED nhỏ:

```text
      Pixel

┌──────────────┐
│              │
│   🔴 🟢 🔵    │
│              │
└──────────────┘
```

Ba màu cơ bản:

* 🔴 Red
* 🟢 Green
* 🔵 Blue

Đây gọi là mô hình màu **RGB (Red - Green - Blue)**.

---

# 2. Trộn màu RGB

Ví dụ

```text
Red   = 255
Green = 0
Blue  = 0
```

Kết quả

```text
Màu đỏ
```

---

Ví dụ

```text
255
255
0
```

Kết quả

```text
Vàng
```

---

Ví dụ

```text
0
255
255
```

Kết quả

```text
Xanh ngọc (Cyan)
```

---

Ví dụ

```text
255
255
255
```

```text
Trắng
```

---

Ví dụ

```text
0
0
0
```

```text
Đen
```

---

# 3. CSS hỗ trợ bao nhiêu cách khai báo màu?

Có 6 cách phổ biến:

| Cách        | Ví dụ               |
| ----------- | ------------------- |
| Tên màu     | `red`               |
| HEX         | `#ff0000`           |
| HEX rút gọn | `#f00`              |
| RGB         | `rgb(255,0,0)`      |
| RGBA        | `rgba(255,0,0,0.5)` |
| HSL / HSLA  | `hsl(0,100%,50%)`   |

---

# 4. Color Keywords

Đây là cách đơn giản nhất.

```css
h1{
    color:red;
}
```

Có rất nhiều tên màu:

```css
red
green
blue
black
white
gray
orange
purple
pink
brown
gold
navy
teal
tomato
crimson
coral
```

Ví dụ

```css
body{
    background:lightgray;
}

h1{
    color:navy;
}

p{
    color:crimson;
}
```

### Ưu điểm

* Dễ nhớ
* Dễ đọc

### Nhược điểm

* Không có nhiều lựa chọn
* Không đủ chính xác cho thiết kế chuyên nghiệp

---

# 5. HEX Color

Đây là cách được dùng nhiều nhất.

Ví dụ

```css
color:#ff0000;
```

Cấu trúc

```text
#RRGGBB
```

Ví dụ

```text
#FF0000
```

```text
FF
00
00
```

Nghĩa là

```text
Red = 255

Green = 0

Blue = 0
```

---

Ví dụ

```css
color:#00ff00;
```

```text
Xanh lá
```

---

Ví dụ

```css
color:#0000ff;
```

```text
Xanh dương
```

---

# 6. HEX rút gọn

Nếu mỗi cặp ký tự giống nhau:

```text
#ffffff
```

Có thể viết

```text
#fff
```

---

```text
#000000
```

↓

```text
#000
```

---

```text
#ff0000
```

↓

```text
#f00
```

---

# 7. RGB

Ví dụ

```css
color:rgb(255,0,0);
```

Ba giá trị

```text
Red

Green

Blue
```

Mỗi giá trị từ

```text
0

↓

255
```

Ví dụ

```css
background:rgb(100,180,255);
```

---

# 8. RGBA

RGBA thêm Alpha.

```css
rgba(255,0,0,0.5)
```

Trong đó

```text
255

0

0

0.5
```

Alpha

```text
0

↓

1
```

| Alpha | Ý nghĩa              |
| ----- | -------------------- |
| 0     | Trong suốt hoàn toàn |
| 0.25  | 25% hiển thị         |
| 0.5   | 50% hiển thị         |
| 0.75  | 75% hiển thị         |
| 1     | Hiển thị hoàn toàn   |

Ví dụ

```css
background:rgba(0,0,255,0.3);
```

---

# 9. HSL

HSL dễ điều chỉnh màu sắc hơn RGB.

```css
hsl(0,100%,50%)
```

Gồm

```text
Hue

Saturation

Lightness
```

---

## Hue

Là góc trên bánh xe màu.

```text
0°

Đỏ

120°

Xanh lá

240°

Xanh dương

360°

Đỏ
```

---

## Saturation

Độ bão hòa

```text
100%

↓

Rực rỡ

0%

↓

Xám
```

---

## Lightness

Độ sáng

```text
0%

↓

Đen

50%

↓

Màu gốc

100%

↓

Trắng
```

---

Ví dụ

```css
color:hsl(210,100%,50%);
```

---

# 10. HSLA

Giống HSL nhưng thêm Alpha.

```css
background:hsla(200,100%,50%,0.5);
```

---

# 11. opacity

Nhiều người nhầm với Alpha.

Ví dụ

```css
.card{
    opacity:0.5;
}
```

Điều gì xảy ra?

Không chỉ nền.

Mà

```text
Ảnh

↓

Mờ

Chữ

↓

Mờ

Button

↓

Mờ
```

Toàn bộ phần tử đều bị mờ.

---

Trong khi

```css
background:rgba(0,0,0,0.5);
```

Chỉ nền mờ.

Chữ vẫn rõ.

Đây là khác biệt cực kỳ quan trọng.

---

# 12. Ví dụ minh họa Alpha và Opacity

```html
<div class="box1">
    RGBA
</div>

<div class="box2">
    Opacity
</div>
```

```css
.box1{
    background:rgba(0,0,255,.3);
    color:black;
}

.box2{
    background:blue;
    opacity:.3;
    color:black;
}
```

Kết quả:

* `.box1`: nền xanh nhạt nhưng chữ vẫn rõ.
* `.box2`: cả nền và chữ đều mờ.

---

# 13. Thuộc tính color và background-color

Ví dụ

```css
body{
    background-color:#f4f4f4;
}
```

Đổi màu nền.

---

```css
h1{
    color:#1565c0;
}
```

Đổi màu chữ.

---

```css
button{
    background-color:#1976d2;
    color:white;
}
```

Đổi đồng thời màu nền và màu chữ.

---

# 14. Ví dụ hoàn chỉnh

## Cấu trúc

```text
lesson4/

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
    <title>Lesson 4 - Colors</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>

    <div class="container">

        <h1>CSS Colors</h1>

        <p>
            Học các hệ màu trong CSS.
        </p>

        <div class="card">
            Card với nền bán trong suốt.
        </div>

        <button>
            Đăng nhập
        </button>

    </div>

</body>
</html>
```

---

## style.css

```css
body{
    font-family:Arial,sans-serif;
    background:#f5f5f5;
    padding:40px;
}

.container{
    width:600px;
    margin:auto;
}

h1{
    color:#1565c0;
}

p{
    color:rgb(80,80,80);
}

.card{
    margin-top:20px;
    padding:20px;
    background:rgba(21,101,192,.15);
    border:1px solid #1565c0;
}

button{
    margin-top:20px;
    background:hsl(210,80%,45%);
    color:white;
    border:none;
    padding:12px 20px;
    cursor:pointer;
}

button:hover{
    background:hsl(210,80%,35%);
}
```

---

# 15. Bảng so sánh

| Kiểu màu | Ưu điểm                        | Nhược điểm                         |
| -------- | ------------------------------ | ---------------------------------- |
| Keyword  | Dễ nhớ                         | Ít màu                             |
| HEX      | Phổ biến, ngắn gọn             | Không trực quan khi cần điều chỉnh |
| RGB      | Dễ hiểu với lập trình          | Khó tinh chỉnh sắc độ              |
| RGBA     | Có độ trong suốt               | Cú pháp dài hơn                    |
| HSL      | Rất dễ thay đổi màu và độ sáng | Ít phổ biến hơn HEX                |
| HSLA     | Linh hoạt nhất khi cần Alpha   | Cú pháp dài                        |

---

# 16. Best Practices

### ✅ Dùng HEX cho màu chủ đạo

```css
:root{
    --primary:#1565c0;
}
```

---

### ✅ Dùng RGBA hoặc HSLA khi cần nền trong suốt

```css
background:rgba(0,0,0,.1);
```

---

### ✅ Hạn chế dùng `opacity` cho hộp chứa văn bản

Thay vì:

```css
.card{
    opacity:.5;
}
```

Hãy dùng:

```css
.card{
    background:rgba(0,0,0,.5);
}
```

---

### ✅ Tạo bảng màu thống nhất

```css
:root{
    --primary:#1565c0;
    --secondary:#1976d2;
    --success:#2e7d32;
    --warning:#f9a825;
    --danger:#d32f2f;
    --background:#f5f5f5;
    --text:#333333;
}
```

Việc này giúp toàn bộ dự án sử dụng màu sắc nhất quán và dễ thay đổi sau này.

---

# Tổng kết

Bạn đã học:

* Mô hình màu RGB.
* Color Keywords.
* HEX và HEX rút gọn.
* RGB và RGBA.
* HSL và HSLA.
* `opacity` và sự khác biệt với Alpha.
* `color` và `background-color`.
* Cách lựa chọn hệ màu phù hợp trong dự án thực tế.

---

# Bài tập thực hành

## Bài 1

Tạo một trang có:

* Tiêu đề màu `#1565c0`.
* Nền trang màu `#f5f5f5`.
* Một nút có nền `rgb(46,125,50)` và chữ màu trắng.

---

## Bài 2

Tạo hai thẻ `div`:

* Thẻ thứ nhất dùng `background: rgba(255,0,0,0.3);`
* Thẻ thứ hai dùng `background: red; opacity: 0.3;`

Quan sát và giải thích sự khác biệt về phần chữ bên trong.

---

## Bài 3

Viết một bảng màu bằng CSS Variables gồm:

* `--primary`
* `--secondary`
* `--success`
* `--warning`
* `--danger`
* `--background`
* `--text`

Sau đó áp dụng các biến này cho tiêu đề, đoạn văn và nút bấm.

---

## Mini Project

Thiết kế một **trang hồ sơ cá nhân (Profile Card)** gồm:

* Ảnh đại diện.
* Họ tên.
* Chức danh.
* Mô tả ngắn.
* Hai nút ("Liên hệ", "Xem dự án").

Yêu cầu:

* Sử dụng ít nhất **4 cách khai báo màu khác nhau** (HEX, RGB, RGBA, HSL hoặc Keyword).
* Tạo hiệu ứng nền bán trong suốt bằng `rgba()` hoặc `hsla()`.
* Không dùng `opacity` để làm mờ toàn bộ thẻ.

Ở **Buổi 5**, chúng ta sẽ học **CSS Units** (`px`, `%`, `em`, `rem`, `vw`, `vh`, `vmin`, `vmax`, `ch`, `ex`, ...) và hiểu khi nào nên dùng từng đơn vị để xây dựng giao diện linh hoạt, responsive và dễ mở rộng.
