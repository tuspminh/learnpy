# Buổi 2. Biến và Kiểu dữ liệu trong JavaScript

**Chủ đề:** `var`, `let`, `const` • Kiểu dữ liệu nguyên thủy • Kiểu tham chiếu • Kiểm tra kiểu dữ liệu • So sánh với Python

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Hiểu cách JavaScript lưu trữ dữ liệu.
> * Phân biệt `var`, `let`, `const`.
> * Hiểu 7 kiểu dữ liệu nguyên thủy (Primitive Types).
> * Hiểu Object là kiểu tham chiếu (Reference Type).
> * Biết sử dụng `typeof`.
> * Tránh các lỗi phổ biến khi chuyển từ Python sang JavaScript.

---

# 1. Biến là gì?

Biến (Variable) là một vùng nhớ có tên để lưu trữ dữ liệu.

Ví dụ trong Python:

```python
name = "Alice"
age = 20
```

Trong JavaScript:

```javascript
let name = "Alice";
let age = 20;
```

Có thể hình dung:

```
RAM

+----------------------+
| name --> "Alice"     |
| age  --> 20          |
+----------------------+
```

---

# 2. Khai báo biến

JavaScript hiện nay có **3 cách khai báo biến**:

```javascript
var a = 10;
let b = 20;
const c = 30;
```

Nhưng trong lập trình hiện đại:

* Dùng `let`
* Dùng `const`
* Hạn chế hoặc tránh dùng `var`

---

# 3. `let`

Đây là cách khai báo biến phổ biến nhất.

```javascript
let age = 20;

console.log(age);
```

Kết quả:

```
20
```

Có thể thay đổi giá trị:

```javascript
let age = 20;

age = 21;

console.log(age);
```

Kết quả:

```
21
```

---

# 4. `const`

`const` nghĩa là **không thể gán lại (reassign)**.

```javascript
const PI = 3.14;

console.log(PI);
```

Sai:

```javascript
const PI = 3.14;

PI = 5;
```

Lỗi:

```
TypeError
```

> **Lưu ý:** `const` không có nghĩa là đối tượng bên trong bất biến. Nó chỉ ngăn việc gán lại biến sang giá trị khác.

Ví dụ:

```javascript
const person = {
    name: "An"
};

person.name = "Bình";

console.log(person.name);
```

Kết quả:

```
Bình
```

Đoạn mã trên **hợp lệ** vì ta không gán lại `person`, chỉ thay đổi thuộc tính của đối tượng.

---

# 5. `var`

Đây là cách cũ trước ES6.

```javascript
var name = "Tom";
```

Ngày nay ít dùng vì:

* Có hoisting khó hiểu.
* Không có block scope.
* Dễ gây lỗi.

Chúng ta sẽ phân tích chi tiết ở buổi về **Scope và Hoisting**.

---

# 6. Khi nào dùng `let`, khi nào dùng `const`?

Quy tắc đơn giản:

* Không thay đổi giá trị → `const`
* Có thay đổi giá trị → `let`

Ví dụ:

```javascript
const PI = 3.14159;

let score = 0;

score++;

console.log(score);
```

---

# 7. Kiểu dữ liệu trong JavaScript

Có hai nhóm lớn:

```
Data Types

├── Primitive
└── Object
```

---

# 8. Primitive Types

JavaScript có **7 kiểu dữ liệu nguyên thủy**:

| Kiểu      | Ví dụ       |
| --------- | ----------- |
| Number    | `10`        |
| String    | `"Hello"`   |
| Boolean   | `true`      |
| Undefined | `undefined` |
| Null      | `null`      |
| Symbol    | `Symbol()`  |
| BigInt    | `100n`      |

---

# 9. Number

Khác Python, JavaScript chỉ có một kiểu số thông thường là `Number`.

```javascript
let a = 10;
let b = 3.14;

console.log(a);
console.log(b);
```

Python:

```python
x = 10  # int
y = 3.14  # float
```

JavaScript:

```javascript
let x = 10;
let y = 3.14;
```

Cả hai đều là:

```
Number
```

---

# 10. String

```javascript
let name = "Alice";
```

Hoặc:

```javascript
let city = 'Hà Nội';
```

Hoặc dùng template literal:

```javascript
let language = `JavaScript`;
```

---

# 11. Boolean

```javascript
let isStudent = true;
let isLogin = false;
```

---

# 12. Undefined

Nếu khai báo nhưng chưa gán giá trị:

```javascript
let age;

console.log(age);
```

Kết quả:

```
undefined
```

---

# 13. Null

`null` biểu thị **không có giá trị** do lập trình viên chủ động gán.

```javascript
let user = null;
```

Khác với `undefined`.

| undefined       | null                  |
| --------------- | --------------------- |
| Chưa có giá trị | Cố ý không có giá trị |

---

# 14. Symbol

Dùng để tạo giá trị duy nhất.

```javascript
const id1 = Symbol();
const id2 = Symbol();

console.log(id1 === id2);
```

Kết quả:

```
false
```

Ngay cả khi mô tả giống nhau:

```javascript
const a = Symbol("id");
const b = Symbol("id");

console.log(a === b);
```

Vẫn:

```
false
```

---

# 15. BigInt

Dùng cho số nguyên rất lớn.

```javascript
const n = 123456789012345678901234567890n;
```

Lưu ý hậu tố `n`.

---

# 16. Object

Mọi thứ còn lại đều là Object.

Ví dụ:

```javascript
const person = {
    name: "An",
    age: 20
};
```

Array:

```javascript
const numbers = [1, 2, 3];
```

Date:

```javascript
const today = new Date();
```

Function:

```javascript
function hello() {}
```

Trong JavaScript, **function cũng là object**.

---

# 17. Kiểm tra kiểu dữ liệu

Dùng:

```javascript
typeof
```

Ví dụ:

```javascript
console.log(typeof 10);
console.log(typeof "Hello");
console.log(typeof true);
```

Kết quả:

```
number
string
boolean
```

---

Ví dụ khác:

```javascript
console.log(typeof undefined);
```

```
undefined
```

---

```javascript
console.log(typeof Symbol());
```

```
symbol
```

---

```javascript
console.log(typeof 100n);
```

```
bigint
```

---

# 18. Điều kỳ lạ của `null`

```javascript
console.log(typeof null);
```

Kết quả:

```
object
```

Đây là **một lỗi lịch sử (legacy bug)** của JavaScript và được giữ lại để đảm bảo tương thích ngược. Vì vậy, không nên dùng `typeof value === "object"` để kết luận rằng giá trị đó chắc chắn là một đối tượng.

---

# 19. So sánh với Python

Python:

```python
x = 10

print(type(x))
```

Kết quả:

```
<class 'int'>
```

JavaScript:

```javascript
let x = 10;

console.log(typeof x);
```

Kết quả:

```
number
```

---

# 20. Ví dụ hoàn chỉnh

```javascript
const name = "An";
let age = 20;
const isStudent = true;
let address;
const phone = null;
const id = Symbol("student");
const population = 9876543210123456789n;

console.log("Tên:", name);
console.log("Tuổi:", age);
console.log("Sinh viên:", isStudent);
console.log("Địa chỉ:", address);
console.log("Số điện thoại:", phone);
console.log("ID:", id);
console.log("Dân số:", population);

console.log("----------------");

console.log(typeof name);
console.log(typeof age);
console.log(typeof isStudent);
console.log(typeof address);
console.log(typeof phone);
console.log(typeof id);
console.log(typeof population);
```

Kết quả (rút gọn):

```
Tên: An
Tuổi: 20
Sinh viên: true
Địa chỉ: undefined
Số điện thoại: null
ID: Symbol(student)
Dân số: 9876543210123456789n
----------------
string
number
boolean
undefined
object
symbol
bigint
```

---

# 21. Best Practices

* Mặc định dùng `const`, chỉ dùng `let` khi cần thay đổi giá trị.
* Tránh `var` trong mã nguồn mới.
* Đặt tên biến có ý nghĩa (`userName`, `totalPrice`, `isLoggedIn`).
* Dùng `camelCase` cho tên biến theo chuẩn JavaScript.
* Dùng `typeof` để kiểm tra kiểu dữ liệu khi gỡ lỗi, nhưng nhớ ngoại lệ của `null`.

---

# 22. Những lỗi người học Python thường gặp

### Lỗi 1: Nghĩ rằng `const` giống hằng số tuyệt đối

Sai:

```javascript
const user = { name: "An" };
user = {};
```

Đúng:

```javascript
const user = { name: "An" };
user.name = "Bình";
```

---

### Lỗi 2: Cho rằng JavaScript có `int` và `float`

Sai:

```javascript
typeof 10;    // "int" ❌
```

Đúng:

```javascript
typeof 10;    // "number"
typeof 3.14;  // "number"
```

---

### Lỗi 3: Nhầm `null` và `undefined`

```javascript
let a;
let b = null;

console.log(a); // undefined
console.log(b); // null
```

---

### Lỗi 4: Tin rằng `typeof null` trả về `"null"`

```javascript
typeof null;
```

Kết quả:

```
"object"
```

Đây là hành vi lịch sử của JavaScript.

---

# 23. Bài tập thực hành

### Bài 1

Khai báo:

* tên
* tuổi
* nghề nghiệp

Sau đó in ra màn hình.

---

### Bài 2

Tạo một biến bằng `const` lưu tên trường học.

Thử gán giá trị mới và quan sát lỗi.

---

### Bài 3

Khai báo các biến có đủ 7 kiểu dữ liệu nguyên thủy:

* Number
* String
* Boolean
* Undefined
* Null
* Symbol
* BigInt

Dùng `typeof` để kiểm tra kiểu của từng biến.

---

### Bài 4

Tạo một object:

```javascript
const book = {
    title: "JavaScript Cơ Bản",
    pages: 300,
    published: true
};
```

* In ra các thuộc tính.
* Thay đổi `pages` thành `350`.
* Giải thích vì sao có thể thay đổi dù dùng `const`.

---

### Bài 5 (Thử thách)

Viết chương trình mô phỏng hồ sơ sinh viên:

* Họ tên
* Tuổi
* Mã sinh viên (`Symbol`)
* Điểm trung bình (`Number`)
* Đã tốt nghiệp (`Boolean`)
* Email (`null`)
* Địa chỉ (`undefined`)

In giá trị và kiểu dữ liệu của từng trường bằng `console.log()` và `typeof`.

---

# Tổng kết buổi 2

Bạn đã học được:

* Ba cách khai báo biến: `var`, `let`, `const`.
* Bảy kiểu dữ liệu nguyên thủy trong JavaScript.
* Khái niệm kiểu tham chiếu với `Object`.
* Cách sử dụng `typeof` và ngoại lệ `typeof null`.
* Sự khác biệt quan trọng giữa JavaScript và Python về hệ thống kiểu dữ liệu.

Ở **Buổi 3**, chúng ta sẽ học **toán tử trong JavaScript**, bao gồm toán tử số học, so sánh, logic, gán, toán tử ba ngôi (`?:`), **optional chaining (`?.`)**, **nullish coalescing (`??`)**, cùng những khác biệt tinh vi giữa `==` và `===`, một trong những chủ đề quan trọng nhất của JavaScript.
