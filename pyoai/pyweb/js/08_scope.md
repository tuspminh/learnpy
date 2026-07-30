# Buổi 8. Scope, Lexical Scope và Hoisting trong JavaScript

**Chủ đề:** Global Scope • Function Scope • Block Scope • Lexical Scope • Scope Chain • Hoisting • Temporal Dead Zone (TDZ) • `var`, `let`, `const` • Closures (giới thiệu)

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Hiểu chính xác biến "sống" ở đâu trong chương trình.
> * Hiểu tại sao `var` gây nhiều lỗi.
> * Hiểu Hoisting và Temporal Dead Zone.
> * Hiểu Lexical Scope – nền tảng của Closure.
> * Biết cách viết mã tránh lỗi về phạm vi biến.

---

# 1. Scope là gì?

**Scope (phạm vi)** là vùng trong chương trình mà một biến có thể được truy cập.

Ví dụ:

```javascript
const name = "An";

console.log(name);
```

Ở đây:

```text
Global Scope

┌───────────────────────┐
│ const name = "An"     │
│                       │
│ console.log(name)     │
└───────────────────────┘
```

Biến `name` có thể được sử dụng ở mọi nơi trong phạm vi toàn cục.

---

# 2. Có những loại Scope nào?

JavaScript hiện đại có ba loại chính:

```text
Scope

├── Global Scope
├── Function Scope
└── Block Scope
```

---

# 3. Global Scope

Biến khai báo ngoài mọi hàm hoặc block.

```javascript
const language = "JavaScript";

function hello() {
    console.log(language);
}

hello();
```

Kết quả:

```text
JavaScript
```

Có thể hình dung:

```text
Global

┌──────────────────────────────┐
│ language                     │
│                              │
│ function hello()             │
│                              │
└──────────────────────────────┘
```

---

# 4. Function Scope

Biến khai báo trong hàm chỉ dùng được trong hàm đó.

```javascript
function test() {

    const age = 20;

    console.log(age);

}

test();

console.log(age);
```

Kết quả:

```text
20
ReferenceError
```

Sơ đồ:

```text
Global

┌──────────────────────┐
│                      │
│ test()               │
│   age                │
│                      │
└──────────────────────┘
```

---

# 5. Block Scope

Khối lệnh:

```javascript
{

}
```

Ví dụ:

```javascript
{

    const city = "Hà Nội";

    console.log(city);

}

console.log(city);
```

Kết quả:

```text
Hà Nội
ReferenceError
```

---

`let` và `const` có Block Scope.

```javascript
if (true) {

    let x = 10;

}

console.log(x);
```

Kết quả:

```text
ReferenceError
```

---

# 6. `var` không có Block Scope

```javascript
if (true) {

    var score = 100;

}

console.log(score);
```

Kết quả:

```text
100
```

Đây là lý do hiện nay người ta hạn chế dùng `var`.

---

So sánh:

```javascript
if (true) {

    let a = 1;
    const b = 2;
    var c = 3;

}

console.log(a);
console.log(b);
console.log(c);
```

Kết quả:

```text
ReferenceError
ReferenceError
3
```

---

# 7. Lexical Scope

Đây là một trong những khái niệm quan trọng nhất của JavaScript.

**Lexical Scope** nghĩa là:

> Hàm có thể truy cập các biến được khai báo trong phạm vi mà nó được định nghĩa.

Ví dụ:

```javascript
const language = "JavaScript";

function outer() {

    const framework = "React";

    function inner() {

        console.log(language);
        console.log(framework);

    }

    inner();

}

outer();
```

Kết quả:

```text
JavaScript
React
```

---

Sơ đồ:

```text
Global

language

↓

outer()

framework

↓

inner()
```

`inner()` có thể nhìn thấy:

* framework
* language

---

# 8. Scope Chain

Nếu biến không tồn tại ở Scope hiện tại:

↓

JavaScript tìm ở Scope cha.

↓

Nếu không thấy

↓

Tiếp tục tìm.

↓

Đến Global.

↓

Không có

↓

ReferenceError

Ví dụ:

```javascript
const x = 100;

function a() {

    function b() {

        console.log(x);

    }

    b();

}

a();
```

---

# 9. Hoisting là gì?

JavaScript thực hiện chương trình theo hai giai đoạn:

```text
1. Creation Phase

↓

2. Execution Phase
```

Trong giai đoạn đầu, JavaScript thu thập các khai báo.

Hiện tượng này gọi là:

```text
Hoisting
```

---

# 10. Hoisting với Function Declaration

```javascript
hello();

function hello() {
    console.log("Hello");
}
```

Kết quả:

```text
Hello
```

Vì Function Declaration được hoisting hoàn toàn.

---

# 11. Hoisting với `var`

```javascript
console.log(age);

var age = 20;
```

Kết quả:

```text
undefined
```

JavaScript hiểu gần giống:

```javascript
var age;

console.log(age);

age = 20;
```

---

# 12. Hoisting với `let`

```javascript
console.log(age);

let age = 20;
```

Kết quả:

```text
ReferenceError
```

Không phải vì `let` không hoisting.

Thực tế:

* `let` **có hoisting**.
* Nhưng biến nằm trong **Temporal Dead Zone**.

---

# 13. Temporal Dead Zone (TDZ)

TDZ là khoảng thời gian:

```text
Biến được tạo

↓

Chưa khởi tạo

↓

Không được truy cập
```

Ví dụ:

```javascript
console.log(name);

let name = "An";
```

Trong TDZ:

```text
ReferenceError
```

---

Sơ đồ:

```text
Creation Phase

↓

name tồn tại

↓

TDZ

↓

let name = "An"

↓

Có thể dùng
```

---

# 14. `const` cũng có TDZ

```javascript
console.log(PI);

const PI = 3.14;
```

Kết quả:

```text
ReferenceError
```

---

# 15. Function Expression

```javascript
hello();

const hello = function() {
    console.log("Hello");
};
```

Kết quả:

```text
ReferenceError
```

Lý do:

* `hello` là biến `const`.
* Biến đang ở TDZ.

---

# 16. So sánh Hoisting

| Khai báo             | Hoisting          | Truy cập trước khai báo                   |
| -------------------- | ----------------- | ----------------------------------------- |
| Function Declaration | Có                | ✅ Được                                    |
| `var`                | Có                | `undefined`                               |
| `let`                | Có                | `ReferenceError`                          |
| `const`              | Có                | `ReferenceError`                          |
| Function Expression  | Theo biến chứa nó | Thường `ReferenceError` với `let`/`const` |

---

# 17. Ví dụ thực tế

```javascript
const TAX = 0.1;

function calculate(price) {

    const total = price + price * TAX;

    return total;

}

console.log(calculate(100000));
```

Quá trình tìm biến:

```text
calculate()

↓

Tìm TAX

↓

Không có

↓

Global

↓

Tìm thấy
```

---

# 18. Giới thiệu Closure

Closure sẽ học chi tiết ở **Buổi 22**, nhưng cần biết nền tảng.

```javascript
function outer() {

    let count = 0;

    function inner() {

        count++;

        console.log(count);

    }

    return inner;

}

const counter = outer();

counter();
counter();
counter();
```

Kết quả:

```text
1
2
3
```

Tại sao `count` vẫn còn tồn tại sau khi `outer()` kết thúc?

→ Vì **Closure**.

Closure hoạt động dựa trên **Lexical Scope**.

---

# 19. So sánh với Python

Python:

```python
x = 10


def test():
    print(x)
```

JavaScript:

```javascript
const x = 10;

function test() {
    console.log(x);
}
```

Đều hoạt động theo **Lexical Scope**.

Tuy nhiên:

Python **không có Hoisting**.

---

# 20. Best Practices

## Luôn dùng `const`

```javascript
const PI = 3.14;
```

---

Nếu cần thay đổi:

```javascript
let score = 0;
```

---

Không dùng:

```javascript
var score = 0;
```

Trừ khi bảo trì mã cũ.

---

## Khai báo trước khi sử dụng

Đừng dựa vào Hoisting.

Không nên:

```javascript
hello();

function hello() {}
```

Nên:

```javascript
function hello() {}

hello();
```

Mặc dù cả hai đều chạy được, cách thứ hai rõ ràng và nhất quán hơn.

---

## Giảm Global Scope

Không nên:

```javascript
const a = ...
const b = ...
const c = ...
const d = ...
```

Nên đặt biến trong phạm vi nhỏ nhất có thể.

---

# 21. Những lỗi người học Python thường gặp

## Lỗi 1: Nghĩ `var` giống `let`

```javascript
if (true) {

    var x = 10;

}

console.log(x);
```

Kết quả:

```text
10
```

---

## Lỗi 2: Nghĩ `let` không Hoisting

Sai.

`let` vẫn được hoisting.

Nhưng:

```text
Temporal Dead Zone
```

làm cho không thể truy cập trước khi khởi tạo.

---

## Lỗi 3: Gọi Function Expression trước khi khai báo

```javascript
hello();

const hello = function() {};
```

Lỗi.

---

## Lỗi 4: Khai báo quá nhiều biến Global

Ví dụ:

```javascript
const user = ...
const product = ...
const cart = ...
const order = ...
```

Trong dự án lớn, điều này làm tăng nguy cơ xung đột tên và khó bảo trì.

---

# 22. Bài tập thực hành

## Bài 1

Viết chương trình chứng minh sự khác nhau giữa:

* `var`
* `let`
* `const`

khi khai báo trong `if`.

---

## Bài 2

Thử chạy:

```javascript
console.log(a);

var a = 10;
```

Sau đó thay `var` bằng:

```javascript
let
```

và

```javascript
const
```

Quan sát sự khác biệt.

---

## Bài 3

Viết hai ví dụ:

* Function Declaration.
* Function Expression.

Gọi hàm trước khi khai báo và giải thích kết quả.

---

## Bài 4

Viết ba hàm lồng nhau:

```javascript
outer()

↓

middle()

↓

inner()
```

Mỗi cấp khai báo một biến riêng.

Trong `inner()`, in ra tất cả các biến để quan sát **Scope Chain**.

---

## Bài 5 (Thử thách)

Viết hàm:

```javascript
function createCounter() {

}
```

Yêu cầu:

* Bên trong có biến `count`.
* Trả về một hàm tăng `count`.
* Mỗi lần gọi hàm trả về sẽ in:

```text
1
2
3
4
...
```

> Đây là ví dụ đầu tiên về **Closure**. Chúng ta mới chỉ quan sát hiện tượng; cơ chế hoạt động sẽ được phân tích chi tiết ở **Buổi 22**.

---

# Tổng kết buổi 8

Bạn đã nắm được những kiến thức nền tảng quan trọng của JavaScript:

* **Global Scope**, **Function Scope** và **Block Scope**.
* **Lexical Scope** và **Scope Chain**, nền tảng của Closure.
* Cơ chế **Hoisting** trong giai đoạn tạo thực thi.
* **Temporal Dead Zone (TDZ)** và lý do `let`/`const` an toàn hơn `var`.
* Sự khác biệt giữa **Function Declaration** và **Function Expression**.

Đến đây, bạn đã hoàn thành **Phần I – Nền tảng JavaScript**. Từ **Buổi 9**, chúng ta sẽ bước sang **Phần II – Object và Array**, bắt đầu với **Object**: object literal, thuộc tính, phương thức, truy cập động, sao chép object, tham chiếu và các kỹ thuật làm việc với object theo chuẩn ES6+. Đây là chủ đề cốt lõi trong hầu hết các ứng dụng JavaScript hiện đại.
