# Buổi 1. Giới thiệu JavaScript từ gốc

**Chủ đề:** JavaScript là gì? • ECMAScript • JavaScript Engine • Runtime • Browser vs Node.js • Cài đặt môi trường • Chương trình đầu tiên

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Hiểu JavaScript thực chất là gì.
> * Phân biệt JavaScript, ECMAScript và V8.
> * Hiểu JavaScript chạy như thế nào.
> * Phân biệt Browser và Node.js.
> * Cài đặt môi trường phát triển.
> * Viết chương trình JavaScript đầu tiên.
> * So sánh tư duy JavaScript với Python.

---

# 1. JavaScript là gì?

JavaScript (JS) là một **ngôn ngữ lập trình đa mục đích (General-purpose Programming Language)**.

Ban đầu JavaScript chỉ dùng để làm cho website trở nên tương tác hơn.

Ví dụ:

Website chỉ có HTML:

```html
<h1>Xin chào</h1>
```

Website có JavaScript:

* Bấm nút
* Hiện popup
* Đăng nhập
* Chat
* Animation
* Game
* Kéo thả
* Upload file

Ngày nay JavaScript còn dùng để viết:

* Website Frontend
* Backend
* Desktop App
* Mobile App
* IoT
* AI
* Game

---

# 2. JavaScript dùng ở đâu?

## Frontend

Ví dụ:

```
HTML
CSS
JavaScript
```

HTML

↓

Tạo cấu trúc

CSS

↓

Làm đẹp

JavaScript

↓

Điều khiển

Ví dụ:

```
Người dùng bấm nút

↓

JavaScript

↓

Gửi dữ liệu

↓

Server Python

↓

Trả JSON

↓

Hiển thị kết quả
```

---

## Backend

Có thể dùng:

```
NodeJS
```

Ví dụ:

```
Client

↓

NodeJS

↓

Database
```

---

## Desktop

Ví dụ:

```
Electron
```

VS Code được xây dựng bằng Electron, sử dụng JavaScript/TypeScript cho phần lớn giao diện.

---

## Mobile

Ví dụ:

```
React Native
```

---

# 3. JavaScript khác Python thế nào?

| Python               | JavaScript        |
| -------------------- | ----------------- |
| Guido tạo            | Brendan Eich tạo  |
| 1991                 | 1995              |
| Đọc dễ               | Linh hoạt         |
| Indentation          | `{}`              |
| Backend mạnh         | Frontend mạnh     |
| Django/Flask/FastAPI | React/Vue/Angular |

Ví dụ Python:

```python
print("Hello")
```

JavaScript:

```javascript
console.log("Hello");
```

---

# 4. ECMAScript là gì?

Đây là phần mà rất nhiều người mới học nhầm.

JavaScript ≠ ECMAScript.

Quan hệ đúng là:

```
ECMAScript

↓

Đặc tả (Specification)

↓

JavaScript

↓

Ngôn ngữ thực tế
```

ECMAScript giống như:

> "Luật"

JavaScript Engine giống như:

> "Người thực hiện luật"

Ví dụ:

```
ECMAScript nói:

Có vòng lặp for

↓

V8

↓

Thực thi vòng lặp
```

---

# 5. ECMAScript Version

Ví dụ:

```
ES5

↓

ES6 (2015)

↓

ES2016

↓

ES2017

↓

...

↓

ES2026
```

ES6 là phiên bản mang đến nhiều tính năng hiện đại như:

* `let`
* `const`
* Arrow Function
* Class
* Module
* Template String
* Promise (được chuẩn hóa và sử dụng rộng rãi)

Ngày nay hầu hết dự án đều sử dụng cú pháp ES6+.

---

# 6. JavaScript Engine là gì?

JavaScript không tự chạy.

Nó cần:

```
Engine
```

Ví dụ:

```
Code

↓

Engine

↓

Machine Code

↓

CPU
```

---

## Engine nổi tiếng

### V8

Google

Chrome

NodeJS

---

### SpiderMonkey

Firefox

---

### JavaScriptCore

Safari

---

# 7. JavaScript Runtime

Engine **không đủ**.

Ví dụ:

```javascript
setTimeout(...)
```

Engine không biết:

```
Timer
```

Ai biết?

Runtime.

Runtime cung cấp:

* Timer
* File
* Network
* DOM (trong trình duyệt)
* Các API khác

---

# 8. Browser Runtime

Ví dụ:

```
Chrome

↓

V8

+

DOM

+

Fetch

+

Window

+

Document
```

Ví dụ:

```javascript
document.title
```

Được.

---

```javascript
window.location
```

Được.

---

# 9. Node Runtime

Node cũng dùng V8.

Nhưng không có DOM.

Có:

```
Filesystem

Network

Process

OS

Buffer
```

Ví dụ:

```javascript
const fs = require("fs");
```

Đọc file.

---

Nhưng:

```javascript
document.querySelector(...)
```

Sai.

Vì:

```
Node

↓

Không có document
```

---

# 10. Browser vs Node

| Browser                | Node                  |
| ---------------------- | --------------------- |
| Có DOM                 | Không có DOM          |
| Có window              | Không có window       |
| Có document            | Không có document     |
| Có alert               | Không có alert        |
| Có HTML                | Không có HTML         |
| Có File System hạn chế | Có File System đầy đủ |

---

# 11. JavaScript chạy như thế nào?

```
Bạn viết code

↓

Engine đọc

↓

Parser

↓

AST

↓

Compiler

↓

Machine Code

↓

CPU
```

Đây là quá trình được tối ưu rất nhiều trong các engine hiện đại như V8.

---

# 12. Cài NodeJS

Tải từ trang chính thức của Node.js và cài đặt.

Kiểm tra:

```bash
node -v
```

Ví dụ:

```
v24.x.x
```

Kiểm tra npm:

```bash
npm -v
```

---

# 13. VS Code

Tạo thư mục:

```
javascript-learning
```

Tạo file:

```
hello.js
```

---

# 14. Chương trình đầu tiên

```javascript
console.log("Hello JavaScript!");
```

Chạy:

```bash
node hello.js
```

Kết quả:

```
Hello JavaScript!
```

---

# 15. `console.log()`

Trong Python:

```python
print("Hello")
```

JavaScript:

```javascript
console.log("Hello");
```

Nó ghi dữ liệu ra Console.

Ví dụ:

```javascript
console.log("Xin chào");
console.log(100);
console.log(true);
```

Kết quả:

```
Xin chào
100
true
```

---

# 16. Nhiều kiểu dữ liệu

```javascript
console.log("Tên");
console.log(20);
console.log(false);
console.log(null);
```

Kết quả:

```
Tên
20
false
null
```

---

# 17. Viết nhiều dòng

```javascript
console.log("Một");
console.log("Hai");
console.log("Ba");
```

---

# 18. Comment

Một dòng:

```javascript
// Đây là comment

console.log("Hello");
```

Nhiều dòng:

```javascript
/*
Đây là
comment
nhiều dòng
*/

console.log("Hello");
```

---

# 19. Ví dụ hoàn chỉnh

```javascript
// hello.js

console.log("=================");
console.log("KHÓA HỌC JAVASCRIPT");
console.log("=================");

console.log("Xin chào!");
console.log("Đây là chương trình JavaScript đầu tiên.");

console.log("JavaScript chạy trên:");
console.log("- Browser");
console.log("- Node.js");

console.log("Kết thúc chương trình.");
```

Kết quả:

```
=================
KHÓA HỌC JAVASCRIPT
=================
Xin chào!
Đây là chương trình JavaScript đầu tiên.
JavaScript chạy trên:
- Browser
- Node.js
Kết thúc chương trình.
```

---

# 20. Best Practices

* Đặt tên file bằng chữ thường và dùng dấu gạch nối (`hello-world.js`, `user-service.js`).
* Mỗi file chỉ nên đảm nhiệm một mục đích rõ ràng.
* Luôn sử dụng `console.log()` để kiểm tra dữ liệu trong giai đoạn học và gỡ lỗi.
* Sử dụng trình soạn thảo có hỗ trợ JavaScript như VS Code.
* Khi chạy bằng Node.js, hãy lưu ý rằng các API của trình duyệt như `document`, `window` không tồn tại.

---

# 21. Những lỗi người học Python thường gặp

❌ Quên rằng JavaScript trong trình duyệt và Node.js có các API khác nhau.

```javascript
document.title
```

Chạy được trên trình duyệt nhưng sẽ lỗi trong Node.js.

---

❌ Nhầm `print()` của Python với JavaScript.

Sai:

```javascript
print("Hello");
```

Đúng:

```javascript
console.log("Hello");
```

---

❌ Cho rằng JavaScript chỉ dùng cho frontend.

Ngày nay JavaScript được dùng rộng rãi ở frontend, backend, desktop, mobile và nhiều lĩnh vực khác.

---

# 22. Bài tập thực hành

### Bài 1

Tạo file `hello.js` và in ra:

```
Xin chào JavaScript!
```

---

### Bài 2

In ra họ tên, tuổi và nghề nghiệp (mỗi thông tin trên một dòng).

Ví dụ:

```
Nguyễn Văn A
25
Lập trình viên
```

---

### Bài 3

Viết chương trình hiển thị:

```
=====================
    HỒ SƠ CÁ NHÂN
=====================
Tên:
Tuổi:
Địa chỉ:
Email:
=====================
```

---

### Bài 4

Thêm comment một dòng và nhiều dòng vào chương trình của bạn.

---

### Bài 5 (Thử thách)

Tạo file `about-javascript.js` và in ra tối thiểu **10 dòng** mô tả ngắn về JavaScript (ví dụ: JavaScript dùng để làm gì, chạy ở đâu, có thể kết hợp với Python như thế nào, v.v.).

---

## Tổng kết buổi 1

Bạn đã nắm được các khái niệm nền tảng:

* JavaScript là gì và phạm vi ứng dụng.
* Mối quan hệ giữa **ECMAScript**, **JavaScript** và **JavaScript Engine**.
* Vai trò của **Runtime** trong Browser và Node.js.
* Sự khác biệt giữa Browser và Node.js.
* Cách cài đặt môi trường và chạy chương trình JavaScript đầu tiên.
* Sử dụng `console.log()` và comment trong JavaScript.

Ở **Buổi 2**, chúng ta sẽ đi sâu vào **biến (`var`, `let`, `const`), kiểu dữ liệu nguyên thủy, kiểu tham chiếu và hệ thống kiểu của JavaScript**, đồng thời so sánh chi tiết với Python để hiểu các khác biệt quan trọng ngay từ đầu.
