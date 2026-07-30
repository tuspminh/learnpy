# Buổi 4. String trong JavaScript (Chuỗi)

**Chủ đề:** Chuỗi • Escape Character • Template Literal • Unicode • String Methods • Immutable String • So sánh với Python

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Hiểu bản chất chuỗi trong JavaScript.
> * Biết cách tạo và thao tác với chuỗi.
> * Thành thạo các phương thức xử lý chuỗi quan trọng.
> * Hiểu sự khác nhau giữa JavaScript và Python khi làm việc với String.
> * Viết được các chương trình xử lý văn bản thực tế.

---

# 1. String là gì?

String (chuỗi) là một dãy ký tự.

Ví dụ:

```javascript
const name = "Nguyễn Văn A";
```

Chuỗi có thể chứa:

* Chữ cái
* Chữ số
* Khoảng trắng
* Emoji
* Ký tự Unicode

Ví dụ:

```javascript
const text = "Xin chào 👋";
```

---

# 2. Khai báo String

Có 3 cách.

## Dùng dấu "

```javascript
const name = "JavaScript";
```

---

## Dùng dấu '

```javascript
const city = 'Hồ Chí Minh';
```

---

## Dùng dấu ` (Template Literal)

```javascript
const language = `JavaScript`;
```

Template Literal là cách hiện đại và rất mạnh, chúng ta sẽ học kỹ ở phần sau.

---

# 3. Độ dài chuỗi

```javascript
const text = "Python";

console.log(text.length);
```

Kết quả:

```
6
```

So với Python:

```python
len(text)
```

JavaScript:

```javascript
text.length
```

Lưu ý: `length` là **thuộc tính**, không phải hàm.

---

# 4. Truy cập ký tự

```javascript
const text = "JavaScript";

console.log(text[0]);
console.log(text[1]);
console.log(text[2]);
```

Kết quả:

```
J
a
v
```

---

Có thể dùng:

```javascript
console.log(text.at(-1));
```

Kết quả:

```
t
```

`at()` hỗ trợ chỉ số âm, còn `text[-1]` sẽ trả về `undefined`.

---

# 5. String là Immutable

Giống Python.

Không thể sửa trực tiếp ký tự.

Sai:

```javascript
let text = "Java";

text[0] = "K";

console.log(text);
```

Kết quả:

```
Java
```

Không có gì thay đổi.

Muốn thay đổi:

```javascript
let text = "Java";

text = "Kava";

console.log(text);
```

---

# 6. Escape Character

Ví dụ:

```javascript
console.log("I'm learning JavaScript");
```

Đoạn trên hợp lệ vì chuỗi dùng dấu `"`.

Nếu dùng dấu `'`:

```javascript
console.log('I'm learning');
```

Sẽ lỗi.

Đúng:

```javascript
console.log('I\'m learning');
```

---

Các escape phổ biến:

| Escape | Ý nghĩa    |
| ------ | ---------- |
| `\n`   | Xuống dòng |
| `\t`   | Tab        |
| `\\`   | Dấu `\`    |
| `\"`   | Dấu `"`    |
| `\'`   | Dấu `'`    |

Ví dụ:

```javascript
console.log("Xin chào\nJavaScript");
```

Kết quả:

```
Xin chào
JavaScript
```

---

# 7. Template Literal

Đây là tính năng ES6 rất quan trọng.

Ví dụ:

```javascript
const name = "An";

console.log(`Xin chào ${name}`);
```

Kết quả:

```
Xin chào An
```

---

Có thể tính toán:

```javascript
const a = 10;
const b = 20;

console.log(`${a} + ${b} = ${a + b}`);
```

Kết quả:

```
10 + 20 = 30
```

---

So với Python:

Python:

```python
name = "An"

print(f"Xin chào {name}")
```

JavaScript:

```javascript
console.log(`Xin chào ${name}`);
```

---

# 8. Đổi chữ hoa chữ thường

```javascript
const text = "JavaScript";

console.log(text.toUpperCase());
console.log(text.toLowerCase());
```

Kết quả:

```
JAVASCRIPT
javascript
```

---

# 9. Xóa khoảng trắng

```javascript
const text = "   Hello   ";

console.log(text.trim());
```

Kết quả:

```
Hello
```

Có thêm:

```javascript
trimStart()

trimEnd()
```

---

# 10. Cắt chuỗi

## slice()

```javascript
const text = "JavaScript";

console.log(text.slice(0,4));
```

Kết quả:

```
Java
```

---

Có thể dùng số âm:

```javascript
console.log(text.slice(-6));
```

Kết quả:

```
Script
```

---

## substring()

```javascript
console.log(text.substring(0,4));
```

Kết quả:

```
Java
```

Khác biệt:

| slice            | substring                          |
| ---------------- | ---------------------------------- |
| Hỗ trợ số âm     | Không hỗ trợ số âm                 |
| Khuyến nghị dùng | Chỉ dùng khi cần tương thích mã cũ |

Trong mã hiện đại, ưu tiên `slice()`.

---

# 11. Tìm kiếm

```javascript
const text = "JavaScript";

console.log(text.includes("Script"));
```

```
true
```

---

```javascript
console.log(text.startsWith("Java"));
```

```
true
```

---

```javascript
console.log(text.endsWith("Script"));
```

```
true
```

---

# 12. indexOf()

```javascript
const text = "JavaScript";

console.log(text.indexOf("Script"));
```

```
4
```

Không tìm thấy:

```javascript
console.log(text.indexOf("Python"));
```

```
-1
```

---

# 13. replace()

```javascript
const text = "Hello Java";

console.log(text.replace("Java","JavaScript"));
```

```
Hello JavaScript
```

---

Thay tất cả:

```javascript
const text = "a,a,a";

console.log(text.replaceAll("a","b"));
```

```
b,b,b
```

---

# 14. split()

```javascript
const text = "Táo,Cam,Xoài";

const fruits = text.split(",");

console.log(fruits);
```

Kết quả:

```javascript
[ 'Táo', 'Cam', 'Xoài' ]
```

---

# 15. join()

Đây là phương thức của **Array**, thường dùng cùng `split()`.

```javascript
const words = ["Java","Script"];

console.log(words.join("-"));
```

```
Java-Script
```

---

# 16. repeat()

```javascript
console.log("*".repeat(10));
```

```
**********
```

---

# 17. padStart()

```javascript
console.log("7".padStart(3,"0"));
```

```
007
```

---

# 18. padEnd()

```javascript
console.log("JS".padEnd(6,"."));
```

```
JS....
```

---

# 19. Unicode

```javascript
console.log("Xin chào 😀");
```

JavaScript hỗ trợ Unicode.

Ví dụ:

```javascript
console.log("❤️");
```

---

# 20. Ví dụ hoàn chỉnh

```javascript
const fullName = "  Nguyễn Văn A  ";

console.log("Tên gốc:", fullName);

const name = fullName.trim();

console.log("Tên:", name);

console.log("Độ dài:", name.length);

console.log("Chữ hoa:", name.toUpperCase());

console.log("Chữ thường:", name.toLowerCase());

console.log("Có chữ Văn:", name.includes("Văn"));

console.log("3 ký tự đầu:", name.slice(0,3));

console.log("3 ký tự cuối:", name.slice(-3));

console.log(`Xin chào ${name}!`);
```

Kết quả (rút gọn):

```
Tên gốc:   Nguyễn Văn A
Tên: Nguyễn Văn A
Độ dài: 12
Chữ hoa: NGUYỄN VĂN A
...
```

---

# 21. So sánh với Python

| Python           | JavaScript           |
| ---------------- | -------------------- |
| `len(s)`         | `s.length`           |
| `s.upper()`      | `s.toUpperCase()`    |
| `s.lower()`      | `s.toLowerCase()`    |
| `s.strip()`      | `s.trim()`           |
| `s.startswith()` | `startsWith()`       |
| `s.endswith()`   | `endsWith()`         |
| `"x" in s`       | `includes()`         |
| `s.split()`      | `split()`            |
| `"".join(list)`  | `join()` (của Array) |
| f-string         | Template Literal     |

---

# 22. Best Practices

* Ưu tiên **Template Literal** thay vì nối chuỗi bằng `+`.
* Dùng `slice()` thay vì `substring()` trong mã mới.
* Luôn `trim()` dữ liệu người dùng nhập trước khi xử lý.
* Dùng `includes()` thay vì `indexOf() !== -1` khi chỉ cần kiểm tra có chứa hay không.
* Không cố sửa trực tiếp ký tự của chuỗi vì String là immutable.

---

# 23. Những lỗi người học Python thường gặp

### Lỗi 1: Gọi `length()` như hàm

Sai:

```javascript
text.length();
```

Đúng:

```javascript
text.length;
```

---

### Lỗi 2: Dùng `text[-1]`

```javascript
const text = "Hello";

console.log(text[-1]);
```

Kết quả:

```
undefined
```

Đúng:

```javascript
console.log(text.at(-1));
```

---

### Lỗi 3: Nghĩ `replace()` thay tất cả

```javascript
const text = "a a a";

console.log(text.replace("a","b"));
```

Kết quả:

```
b a a
```

Chỉ thay lần xuất hiện đầu tiên.

Muốn thay tất cả:

```javascript
console.log(text.replaceAll("a","b"));
```

---

### Lỗi 4: Sửa trực tiếp ký tự

Sai:

```javascript
let text = "Java";

text[0] = "K";
```

Chuỗi vẫn là `"Java"`.

---

# 24. Bài tập thực hành

## Bài 1

Khai báo:

```javascript
const fullName = "  Nguyễn Văn B  ";
```

* Xóa khoảng trắng đầu và cuối.
* In độ dài trước và sau khi `trim()`.

---

## Bài 2

Cho:

```javascript
const email = "student@example.com";
```

* Kiểm tra có chứa `"@"`.
* Kiểm tra có kết thúc bằng `".com"`.

---

## Bài 3

Cho:

```javascript
const sentence = "JavaScript,Python,Java";
```

* Tách thành mảng.
* Ghép lại bằng `" | "`.

---

## Bài 4

Cho:

```javascript
const phone = "987654321";
```

Hiển thị:

```
0987654321
```

Bằng `padStart()`.

---

## Bài 5 (Thử thách)

Viết chương trình xử lý danh sách học viên:

```javascript
const students = [
    "  Nguyễn Văn A ",
    " Trần Thị B",
    "Lê Văn C  "
];
```

Yêu cầu:

1. Xóa khoảng trắng ở đầu và cuối mỗi tên.
2. Chuyển tất cả thành chữ hoa.
3. In lời chào bằng Template Literal:

```text
Xin chào NGUYỄN VĂN A!
Xin chào TRẦN THỊ B!
Xin chào LÊ VĂN C!
```

---

# Tổng kết buổi 4

Bạn đã học được:

* Bản chất của `String` và tính **immutable**.
* Ba cách khai báo chuỗi và ưu điểm của **Template Literal**.
* Các phương thức xử lý chuỗi quan trọng như `trim()`, `slice()`, `includes()`, `replace()`, `split()`, `padStart()`,...
* Cách làm việc với Unicode và ký tự đặc biệt.
* Các khác biệt quan trọng giữa JavaScript và Python khi xử lý chuỗi.

**Buổi 5** sẽ chuyển sang **cấu trúc điều khiển**: `if`, `else`, `else if`, `switch`, biểu thức điều kiện phức tạp, kết hợp với các toán tử đã học để xây dựng các chương trình có luồng xử lý hoàn chỉnh.
