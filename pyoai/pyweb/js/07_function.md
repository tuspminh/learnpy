# Buổi 7. Function trong JavaScript (Hàm)

**Chủ đề:** Function Declaration • Function Expression • Arrow Function • Tham số • Giá trị trả về • Default Parameter • Rest Parameter • Callback • Higher-Order Function • So sánh với Python

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Hiểu bản chất của hàm trong JavaScript.
> * Thành thạo các cách khai báo hàm.
> * Biết khi nào dùng Function Declaration, Function Expression và Arrow Function.
> * Hiểu callback và higher-order function.
> * So sánh tư duy viết hàm giữa JavaScript và Python.

---

# 1. Function là gì?

Function (hàm) là một khối mã có thể tái sử dụng để thực hiện một công việc cụ thể.

Không dùng hàm:

```javascript
console.log("Xin chào An");
console.log("Xin chào Bình");
console.log("Xin chào Lan");
```

Dùng hàm:

```javascript
function greet(name) {
    console.log(`Xin chào ${name}`);
}

greet("An");
greet("Bình");
greet("Lan");
```

Kết quả:

```text
Xin chào An
Xin chào Bình
Xin chào Lan
```

---

# 2. Cấu trúc của Function

```javascript
function tenHam(thamSo1, thamSo2) {

    // xử lý

    return ketQua;

}
```

Gồm:

* Tên hàm
* Danh sách tham số
* Thân hàm
* Giá trị trả về (`return`)

---

# 3. Function Declaration

Đây là cách phổ biến nhất.

```javascript
function add(a, b) {
    return a + b;
}

const result = add(3, 5);

console.log(result);
```

Kết quả:

```text
8
```

---

# 4. Tham số (Parameters)

```javascript
function introduce(name, age) {
    console.log(`${name} - ${age}`);
}

introduce("Lan", 20);
```

Kết quả:

```text
Lan - 20
```

---

# 5. Đối số (Arguments)

Trong lời gọi:

```javascript
introduce("Lan", 20);
```

* `"Lan"` là **argument**
* `name` là **parameter**

Đây là hai khái niệm thường bị nhầm lẫn.

---

# 6. Giá trị trả về

```javascript
function square(x) {
    return x * x;
}

console.log(square(6));
```

Kết quả:

```text
36
```

---

Nếu không có `return`:

```javascript
function hello() {
    console.log("Hello");
}

const result = hello();

console.log(result);
```

Kết quả:

```text
Hello
undefined
```

Mặc định JavaScript trả về `undefined`.

---

# 7. Function Expression

Có thể lưu hàm vào biến.

```javascript
const multiply = function(a, b) {
    return a * b;
};

console.log(multiply(4, 5));
```

Kết quả:

```text
20
```

Khác với Function Declaration, Function Expression **không được hoisting đầy đủ** (sẽ học chi tiết ở Buổi 8).

---

# 8. Arrow Function

Được giới thiệu từ ES6.

```javascript
const add = (a, b) => {
    return a + b;
};

console.log(add(2, 3));
```

---

Nếu chỉ có một biểu thức:

```javascript
const add = (a, b) => a + b;
```

Tương đương:

```javascript
function add(a, b) {
    return a + b;
}
```

---

# 9. Arrow Function với một tham số

```javascript
const square = x => x * x;

console.log(square(5));
```

---

Không có tham số:

```javascript
const hello = () => {
    console.log("Hello");
};
```

---

# 10. Default Parameter

```javascript
function greet(name = "Khách") {
    console.log(`Xin chào ${name}`);
}

greet();
greet("An");
```

Kết quả:

```text
Xin chào Khách
Xin chào An
```

So với Python:

```python
def greet(name="Khách"):
    print(name)
```

Rất giống nhau.

---

# 11. Rest Parameter

Thu nhận nhiều tham số.

```javascript
function sum(...numbers) {

    let total = 0;

    for (const n of numbers) {
        total += n;
    }

    return total;

}

console.log(sum(1,2,3,4,5));
```

Kết quả:

```text
15
```

Python:

```python
def sum(*numbers):
```

JavaScript:

```javascript
function sum(...numbers)
```

---

# 12. Function là Object

Trong JavaScript:

```javascript
function hello() {}

console.log(typeof hello);
```

Kết quả:

```text
function
```

Về bản chất, Function là một đối tượng đặc biệt (callable object), vì vậy bạn có thể:

* Gán vào biến.
* Truyền làm tham số.
* Trả về từ một hàm khác.

---

# 13. Callback Function

Callback là hàm được truyền vào hàm khác.

```javascript
function process(callback) {
    callback();
}

process(function() {
    console.log("Đang xử lý...");
});
```

Kết quả:

```text
Đang xử lý...
```

Arrow Function:

```javascript
process(() => {
    console.log("Done");
});
```

---

# 14. Higher-Order Function

Là hàm:

* Nhận hàm làm tham số.
* Hoặc trả về một hàm.

Ví dụ:

```javascript
function calculate(a, b, operation) {
    return operation(a, b);
}

const result = calculate(
    10,
    20,
    (x, y) => x + y
);

console.log(result);
```

Kết quả:

```text
30
```

Đây là nền tảng của các phương thức như `map()`, `filter()`, `reduce()`.

---

# 15. Phạm vi của tham số

```javascript
function test(a) {
    console.log(a);
}

test(10);

console.log(a);
```

Kết quả:

```text
10
ReferenceError
```

Tham số chỉ tồn tại bên trong hàm.

---

# 16. Hàm gọi hàm

```javascript
function square(x) {
    return x * x;
}

function sumSquare(a, b) {
    return square(a) + square(b);
}

console.log(sumSquare(2, 3));
```

Kết quả:

```text
13
```

---

# 17. Ví dụ hoàn chỉnh

```javascript
function calculateTotal(price, quantity, discount = 0) {

    const total = price * quantity;

    return total - discount;

}

const invoice = calculateTotal(
    120000,
    3,
    50000
);

console.log(`Tổng tiền: ${invoice}`);
```

Kết quả:

```text
Tổng tiền: 310000
```

---

# 18. So sánh với Python

| Python        | JavaScript            |
| ------------- | --------------------- |
| `def`         | `function`            |
| `lambda`      | `=>` (Arrow Function) |
| `return`      | `return`              |
| `*args`       | `...args`             |
| Hàm là object | Hàm cũng là object    |

---

# 19. Function Declaration vs Function Expression vs Arrow Function

| Đặc điểm        | Declaration | Expression    | Arrow               |
| --------------- | ----------- | ------------- | ------------------- |
| Có tên          | Có          | Có hoặc không | Thường gán vào biến |
| Hoisting        | Có          | Không đầy đủ  | Không               |
| Có `this` riêng | Có          | Có            | Không               |
| Ngắn gọn        | Trung bình  | Trung bình    | Rất ngắn            |

> **Lưu ý:** Khác biệt về `this` sẽ được học kỹ ở Buổi 23.

---

# 20. Best Practices

## Đặt tên theo động từ

Tốt:

```javascript
calculateTotal()
getUser()
saveBook()
sendEmail()
```

Không tốt:

```javascript
data()
abc()
run1()
```

---

## Mỗi hàm chỉ nên làm một việc

Không nên:

```javascript
function processUser() {
    // đọc file
    // gửi email
    // ghi database
    // in báo cáo
}
```

Nên tách thành:

```javascript
loadUser()
saveUser()
sendEmail()
printReport()
```

---

## Trả về giá trị thay vì in trực tiếp

Không nên:

```javascript
function add(a, b) {
    console.log(a + b);
}
```

Nên:

```javascript
function add(a, b) {
    return a + b;
}
```

---

## Ưu tiên Arrow Function cho callback

```javascript
numbers.map(x => x * 2);
```

Rõ ràng và ngắn gọn.

---

# 21. Những lỗi người học Python thường gặp

## Lỗi 1: Quên `return`

Sai:

```javascript
function add(a, b) {
    a + b;
}

console.log(add(2, 3));
```

Kết quả:

```text
undefined
```

---

## Lỗi 2: Gọi hàm trước khi khai báo bằng Function Expression

```javascript
hello();

const hello = function() {
    console.log("Hi");
};
```

Lỗi:

```text
ReferenceError
```

Trong khi:

```javascript
hello();

function hello() {
    console.log("Hi");
}
```

Hoạt động bình thường.

---

## Lỗi 3: Nhầm Rest Parameter với Spread Operator

Rest:

```javascript
function sum(...numbers) {}
```

Spread:

```javascript
const arr = [1,2,3];

console.log(...arr);
```

Cùng ký hiệu `...` nhưng khác mục đích.

---

## Lỗi 4: Viết Arrow Function nhiều dòng mà quên `return`

Sai:

```javascript
const add = (a, b) => {
    a + b;
};
```

Kết quả:

```text
undefined
```

Đúng:

```javascript
const add = (a, b) => {
    return a + b;
};
```

Hoặc:

```javascript
const add = (a, b) => a + b;
```

---

# 22. Bài tập thực hành

## Bài 1

Viết hàm:

```javascript
add(a, b)
```

Trả về tổng hai số.

---

## Bài 2

Viết hàm:

```javascript
isEven(number)
```

Trả về:

* `true`
* `false`

---

## Bài 3

Viết Arrow Function tính diện tích hình chữ nhật.

```javascript
const area = (width, height) => ...
```

---

## Bài 4

Viết hàm:

```javascript
sum(...numbers)
```

Cho phép truyền bao nhiêu số cũng được.

Ví dụ:

```javascript
sum(1,2,3,4,5)
```

Kết quả:

```text
15
```

---

## Bài 5 (Thử thách)

Cho dữ liệu:

```javascript
const students = [
    { name: "An", score: 90 },
    { name: "Lan", score: 70 },
    { name: "Minh", score: 82 }
];
```

Viết chương trình:

1. Tạo hàm `getGrade(score)` trả về:

   * `"Giỏi"` nếu điểm ≥ 80.
   * `"Khá"` nếu điểm ≥ 65.
   * `"Trung bình"` nếu điểm ≥ 50.
   * `"Yếu"` nếu dưới 50.
2. Dùng vòng lặp để duyệt danh sách học sinh.
3. In kết quả theo định dạng:

```text
An: 90 - Giỏi
Lan: 70 - Khá
Minh: 82 - Giỏi
```

---

# Tổng kết buổi 7

Bạn đã học:

* Function Declaration.
* Function Expression.
* Arrow Function.
* Parameter và Argument.
* `return`, Default Parameter và Rest Parameter.
* Callback Function và Higher-Order Function.
* Các nguyên tắc viết hàm rõ ràng, dễ tái sử dụng.

Đây là nền tảng cực kỳ quan trọng. Từ **Buổi 8**, chúng ta sẽ đi sâu vào **Scope (phạm vi biến), Lexical Scope và Hoisting** để hiểu vì sao JavaScript hoạt động như vậy, cũng như lý do nên ưu tiên `let` và `const` thay vì `var`. Những kiến thức này sẽ giúp bạn tránh nhiều lỗi khó phát hiện trong các dự án thực tế.
