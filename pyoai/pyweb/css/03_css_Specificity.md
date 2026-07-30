# Buổi 3: CSS Specificity (Độ ưu tiên của CSS)

> **Mục tiêu**
>
> Sau buổi học này, bạn sẽ hiểu:
>
> * Specificity là gì.
> * Browser quyết định áp dụng CSS theo thứ tự nào.
> * Cascade hoạt động ra sao.
> * Khi nào CSS bị ghi đè.
> * Cách tính điểm Specificity.
> * Khi nào nên và không nên dùng `!important`.
> * Cách viết CSS dễ bảo trì trong các dự án Flask/Jinja2.

---

# 1. Vì sao cần Specificity?

Giả sử có CSS:

```css
p{
    color: blue;
}

.text{
    color: red;
}
```

HTML

```html
<p class="text">
    Hello CSS
</p>
```

Đoạn văn sẽ có màu gì?

Có hai đáp án:

```
Xanh

hoặc

Đỏ
```

Browser cần một quy tắc để quyết định.

Quy tắc đó chính là **Specificity**.

---

# 2. Browser quyết định CSS theo thứ tự nào?

Đây là quy trình thực tế mà trình duyệt áp dụng:

```
Có !important?

↓

Có

↓

!important thắng

↓

Không

↓

So sánh Specificity

↓

Nếu bằng nhau

↓

Rule viết sau thắng
```

Đây là điều bạn nên ghi nhớ vì nó giải thích hầu hết các xung đột CSS.

---

# 3. Bốn mức ưu tiên cơ bản

Từ thấp đến cao:

```
Element

↓

Class

↓

ID

↓

Inline Style
```

Ví dụ:

```css
p{
    color:blue;
}

.text{
    color:red;
}

#title{
    color:green;
}
```

HTML

```html
<p
id="title"
class="text">

Hello

</p>
```

Kết quả

```
Màu xanh lá
```

Vì **ID** ưu tiên hơn **Class** và **Element**.

---

# 4. Cách tính điểm Specificity

Một cách đơn giản là xem Specificity như một bộ 4 số:

```
Inline

↓

ID

↓

Class

↓

Element
```

Ví dụ:

```
(1,0,0,0)

↓

Inline Style
```

```
(0,1,0,0)

↓

1 ID
```

```
(0,0,1,0)

↓

1 Class
```

```
(0,0,0,1)

↓

1 Element
```

Trình duyệt sẽ so sánh từ trái sang phải.

---

# 5. Ví dụ tính điểm

## Ví dụ 1

```css
p{
}
```

Điểm

```
0,0,0,1
```

---

## Ví dụ 2

```css
.text{
}
```

Điểm

```
0,0,1,0
```

---

## Ví dụ 3

```css
#header{
}
```

Điểm

```
0,1,0,0
```

---

## Ví dụ 4

```css
<p style="color:red;">
```

Điểm

```
1,0,0,0
```

Inline gần như luôn thắng các quy tắc thông thường.

---

# 6. Nhiều Selector cộng điểm

Ví dụ

```css
div p{
}
```

Có

```
div

+

p
```

Điểm

```
0,0,0,2
```

---

Ví dụ

```css
.card p{
}
```

Có

```
.card

+

p
```

Điểm

```
0,0,1,1
```

---

Ví dụ

```css
#main .card p{
}
```

Điểm

```
#main

+

.card

+

p
```

Điểm

```
0,1,1,1
```

---

# 7. So sánh điểm

Ví dụ

```css
p{
    color:blue;
}

.card p{
    color:red;
}
```

Điểm

```
p

↓

0,0,0,1

.card p

↓

0,0,1,1
```

`.card p` thắng.

---

Ví dụ

```css
.card{
}

#card{
}
```

Điểm

```
.card

↓

0,0,1,0

#card

↓

0,1,0,0
```

ID thắng.

---

# 8. Nếu điểm bằng nhau

Ví dụ

```css
p{

color:blue;

}

p{

color:red;

}
```

Điểm đều là

```
0,0,0,1
```

Rule viết sau thắng.

Kết quả

```
Đỏ
```

---

# 9. Inline Style

Ví dụ

```html
<p
style="color:red;"
class="text">

Hello

</p>
```

CSS

```css
.text{

color:blue;

}
```

Inline thắng.

Kết quả

```
Đỏ
```

---

# 10. !important

Ví dụ

```css
p{

color:blue !important;

}
```

HTML

```html
<p
style="color:red;">

Hello

</p>
```

Kết quả

```
Xanh
```

`!important` có thể ghi đè cả Inline Style thông thường.

---

# 11. Khi nào KHÔNG nên dùng !important

Sai

```css
.btn{

color:red !important;

}
```

```css
.card{

padding:20px !important;

}
```

```css
body{

background:black !important;

}
```

Sau vài tháng, dự án sẽ rất khó bảo trì vì mọi người phải tiếp tục dùng `!important` để ghi đè lẫn nhau.

---

# 12. Khi nào NÊN dùng !important

Một số trường hợp hợp lý:

* Ghi đè CSS của thư viện bên thứ ba khi không thể sửa nguồn.
* Các lớp tiện ích (utility classes) được thiết kế có chủ đích.
* Một số quy tắc phục vụ trợ năng (accessibility).

Ví dụ:

```css
.hidden{
    display:none !important;
}
```

---

# 13. Ví dụ hoàn chỉnh

## Cấu trúc

```
lesson3/

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
    <title>Lesson 3</title>

    <link rel="stylesheet" href="style.css">
</head>
<body>

<h1 id="title" class="main-title">
    CSS Specificity
</h1>

<p class="text">
    Hello Python
</p>

<p
class="text"
style="color:orange;">
    Inline Style
</p>

</body>
</html>
```

---

## style.css

```css
/* Element */
h1{
    color:blue;
}

/* Class */
.main-title{
    color:green;
}

/* ID */
#title{
    color:red;
}

/* Element */
p{
    color:black;
}

/* Class */
.text{
    color:steelblue;
}

/* Chỉ đoạn văn có inline style vẫn giữ màu cam */
```

Kết quả:

* Tiêu đề có màu **đỏ** (ID thắng).
* Đoạn văn đầu có màu **xanh thép** (class thắng element).
* Đoạn văn thứ hai có màu **cam** (inline thắng class).

---

# 14. Debug CSS bằng DevTools

Khi CSS không hoạt động như mong muốn:

1. Mở trình duyệt.
2. Nhấn **F12** (hoặc **Inspect**).
3. Chọn phần tử cần kiểm tra.
4. Xem tab **Styles**.

Bạn sẽ thấy:

* Quy tắc nào đang được áp dụng.
* Quy tắc nào bị gạch ngang (đã bị ghi đè).
* Quy tắc đến từ file CSS nào và dòng nào.

Đây là kỹ năng quan trọng khi phát triển web.

---

# 15. Best Practices

### ✅ Ưu tiên Class

```css
.button-primary{
    background:#1565c0;
}
```

---

### ❌ Hạn chế dùng ID để tạo kiểu

```css
#submitButton{
    background:red;
}
```

ID có Specificity cao, khiến việc ghi đè sau này khó khăn hơn.

---

### ✅ Tránh Selector quá dài

Không nên:

```css
body main .container .content article .card p{
    color:red;
}
```

Nên:

```css
.article-text{
    color:red;
}
```

---

### ✅ Hạn chế `!important`

Nếu phải dùng nhiều `!important`, hãy xem lại cách tổ chức selector hoặc cấu trúc CSS của dự án.

---

# 16. Tóm tắt

| Selector     | Điểm Specificity |
| ------------ | ---------------: |
| Inline Style |          1,0,0,0 |
| `#id`        |          0,1,0,0 |
| `.class`     |          0,0,1,0 |
| `p`          |          0,0,0,1 |
| `*`          |          0,0,0,0 |

Quy tắc ưu tiên:

1. `!important`
2. Inline Style
3. ID
4. Class, pseudo-class, attribute selector
5. Element, pseudo-element
6. Nếu vẫn bằng nhau → quy tắc xuất hiện **sau** sẽ thắng.

---

# Bài tập thực hành

## Bài 1

Viết HTML:

```html
<h1 id="logo" class="title">
    My Website
</h1>
```

Viết CSS với ba quy tắc:

```css
h1 { color: blue; }
.title { color: green; }
#logo { color: red; }
```

Dự đoán màu hiển thị, sau đó chạy thử để kiểm chứng.

---

## Bài 2

Thêm:

```html
style="color:purple;"
```

vào thẻ `<h1>` và quan sát điều gì thay đổi.

---

## Bài 3

Thêm:

```css
h1{
    color:black !important;
}
```

và so sánh kết quả với trường hợp chỉ dùng Inline Style.

---

## Mini Project

Tạo một trang hồ sơ cá nhân gồm:

* Tiêu đề (`h1`)
* Ảnh đại diện (`img`)
* Đoạn giới thiệu (`p`)
* Hai nút (`button`)

Viết nhiều quy tắc CSS (Element, Class, ID và Inline) cùng áp dụng lên một số phần tử, sau đó:

1. Dự đoán quy tắc nào sẽ được áp dụng.
2. Kiểm tra bằng trình duyệt và DevTools.
3. Ghi lại điểm Specificity của từng selector.

Đây là bài tập rất hiệu quả để làm quen với cách trình duyệt xử lý CSS trong các dự án thực tế.

Ở **Buổi 4**, chúng ta sẽ học **Color trong CSS** một cách toàn diện: các hệ màu **Keyword**, **HEX**, **RGB**, **RGBA**, **HSL**, **HSLA**, cách sử dụng `opacity`, nguyên lý pha màu, độ trong suốt và các thực hành giúp xây dựng giao diện đẹp, dễ đọc và nhất quán.
