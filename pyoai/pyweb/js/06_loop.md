# Buổi 6. Vòng lặp trong JavaScript (Loop)

**Chủ đề:** `for` • `while` • `do...while` • `for...of` • `for...in` • `break` • `continue` • Vòng lặp lồng nhau • Best Practices

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Thành thạo tất cả các loại vòng lặp trong JavaScript.
> * Biết khi nào nên dùng từng loại.
> * Hiểu sự khác biệt giữa `for...of` và `for...in`.
> * So sánh với Python.
> * Tránh những lỗi phổ biến khi duyệt mảng và object.

---

# 1. Vòng lặp là gì?

Vòng lặp (Loop) cho phép thực hiện một khối lệnh nhiều lần.

Không dùng vòng lặp:

```javascript
console.log("Hello");
console.log("Hello");
console.log("Hello");
console.log("Hello");
console.log("Hello");
```

Dùng vòng lặp:

```javascript
for (let i = 0; i < 5; i++) {
    console.log("Hello");
}
```

---

# 2. Vòng lặp `for`

Đây là vòng lặp phổ biến nhất.

Cú pháp:

```javascript
for (khởi_tạo; điều_kiện; cập_nhật) {

}
```

Ví dụ:

```javascript
for (let i = 1; i <= 5; i++) {
    console.log(i);
}
```

Kết quả:

```
1
2
3
4
5
```

---

## Phân tích

```javascript
for (let i = 1; i <= 5; i++)
```

Gồm ba phần:

### Khởi tạo

```javascript
let i = 1;
```

Chỉ chạy một lần.

---

### Điều kiện

```javascript
i <= 5
```

Nếu đúng → tiếp tục.

Nếu sai → kết thúc.

---

### Cập nhật

```javascript
i++
```

Sau mỗi lần lặp.

---

# 3. Duyệt ngược

```javascript
for (let i = 10; i >= 1; i--) {
    console.log(i);
}
```

---

# 4. Bước nhảy

```javascript
for (let i = 0; i <= 20; i += 2) {
    console.log(i);
}
```

Kết quả:

```
0
2
4
6
...
20
```

---

# 5. `while`

Thích hợp khi chưa biết trước số lần lặp.

```javascript
let i = 1;

while (i <= 5) {
    console.log(i);

    i++;
}
```

---

Ví dụ nhập dữ liệu đến khi hợp lệ:

```javascript
while (!isValid) {

}
```

Trong thực tế, bạn sẽ gặp nhiều trong các thuật toán hoặc khi xử lý dữ liệu liên tục.

---

# 6. `do...while`

Khác với `while`.

`do...while` luôn chạy **ít nhất một lần**.

```javascript
let i = 10;

do {
    console.log(i);

    i++;

} while (i < 5);
```

Kết quả:

```
10
```

Trong khi:

```javascript
while (i < 5) {
    console.log(i);
}
```

Không in gì.

---

# 7. `break`

Thoát khỏi vòng lặp ngay lập tức.

```javascript
for (let i = 1; i <= 10; i++) {

    if (i === 5) {
        break;
    }

    console.log(i);

}
```

Kết quả:

```
1
2
3
4
```

---

# 8. `continue`

Bỏ qua lần lặp hiện tại.

```javascript
for (let i = 1; i <= 5; i++) {

    if (i === 3) {
        continue;
    }

    console.log(i);

}
```

Kết quả:

```
1
2
4
5
```

---

# 9. `for...of`

Đây là cách hiện đại để duyệt **Iterable**.

Ví dụ:

```javascript
const fruits = [
    "Táo",
    "Cam",
    "Xoài"
];

for (const fruit of fruits) {
    console.log(fruit);
}
```

Kết quả:

```
Táo
Cam
Xoài
```

---

Duyệt String:

```javascript
const text = "Java";

for (const ch of text) {
    console.log(ch);
}
```

Kết quả:

```
J
a
v
a
```

---

So với Python:

Python:

```python
for item in fruits:
    print(item)
```

JavaScript:

```javascript
for (const item of fruits) {
    console.log(item);
}
```

Rất giống nhau.

---

# 10. `for...in`

`for...in` dùng để duyệt **tên thuộc tính (key)** của Object.

```javascript
const person = {
    name: "An",
    age: 20,
    city: "Hà Nội"
};

for (const key in person) {
    console.log(key);
}
```

Kết quả:

```
name
age
city
```

Muốn lấy giá trị:

```javascript
for (const key in person) {
    console.log(key, person[key]);
}
```

Kết quả:

```
name An
age 20
city Hà Nội
```

---

# 11. `for...of` và `for...in`

Đây là phần rất dễ nhầm.

## `for...of`

Lấy **giá trị**.

```javascript
const numbers = [10, 20, 30];

for (const value of numbers) {
    console.log(value);
}
```

Kết quả:

```
10
20
30
```

---

## `for...in`

Lấy **chỉ số (index)** khi dùng với Array.

```javascript
const numbers = [10, 20, 30];

for (const index in numbers) {
    console.log(index);
}
```

Kết quả:

```
0
1
2
```

Giá trị:

```javascript
console.log(numbers[index]);
```

---

### Quy tắc vàng

| Kiểu dữ liệu                | Vòng lặp nên dùng |
| --------------------------- | ----------------- |
| Array                       | `for...of`        |
| String                      | `for...of`        |
| Object                      | `for...in`        |
| Biết số lần lặp             | `for`             |
| Không biết trước số lần lặp | `while`           |

---

# 12. Duyệt Object bằng `Object.keys()`

Một cách hiện đại hơn:

```javascript
const person = {
    name: "Lan",
    age: 21
};

for (const key of Object.keys(person)) {
    console.log(key);
}
```

---

Lấy giá trị:

```javascript
for (const value of Object.values(person)) {
    console.log(value);
}
```

---

Lấy cả key và value:

```javascript
for (const [key, value] of Object.entries(person)) {
    console.log(key, value);
}
```

Đây là cách rất phổ biến trong các dự án hiện đại.

---

# 13. Vòng lặp lồng nhau

```javascript
for (let i = 1; i <= 3; i++) {

    for (let j = 1; j <= 3; j++) {

        console.log(i, j);

    }

}
```

Kết quả:

```
1 1
1 2
1 3
2 1
2 2
2 3
3 1
3 2
3 3
```

---

Ví dụ in bảng cửu chương:

```javascript
for (let i = 2; i <= 3; i++) {

    console.log(`Bảng ${i}`);

    for (let j = 1; j <= 10; j++) {
        console.log(`${i} x ${j} = ${i * j}`);
    }

}
```

---

# 14. Ví dụ hoàn chỉnh

```javascript
const students = [
    {
        name: "An",
        score: 90
    },
    {
        name: "Bình",
        score: 75
    },
    {
        name: "Lan",
        score: 82
    }
];

for (const student of students) {

    let level;

    if (student.score >= 80) {
        level = "Giỏi";
    } else {
        level = "Khá";
    }

    console.log(`${student.name}: ${student.score} (${level})`);
}
```

Kết quả:

```
An: 90 (Giỏi)
Bình: 75 (Khá)
Lan: 82 (Giỏi)
```

---

# 15. So sánh với Python

| Python            | JavaScript                      |
| ----------------- | ------------------------------- |
| `for x in list`   | `for...of`                      |
| `for key in dict` | `for...in` hoặc `Object.keys()` |
| `while`           | `while`                         |
| `break`           | `break`                         |
| `continue`        | `continue`                      |

---

# 16. Best Practices

## Ưu tiên `for...of` khi duyệt Array

Không nên:

```javascript
for (const i in numbers) {
    console.log(numbers[i]);
}
```

Nên:

```javascript
for (const number of numbers) {
    console.log(number);
}
```

---

## Dùng `Object.entries()`

Không nên:

```javascript
for (const key in user) {
    console.log(user[key]);
}
```

Nên:

```javascript
for (const [key, value] of Object.entries(user)) {
    console.log(key, value);
}
```

---

## Không sửa điều khiển vòng lặp tùy tiện

Ví dụ khó đọc:

```javascript
for (let i = 0; i < 10;) {
    i += Math.random() > 0.5 ? 2 : 1;
}
```

Hãy giữ phần cập nhật rõ ràng nếu có thể.

---

# 17. Những lỗi người học Python thường gặp

## Lỗi 1: Dùng `for...in` để duyệt Array

```javascript
const numbers = [10, 20, 30];

for (const item in numbers) {
    console.log(item);
}
```

Kết quả:

```
0
1
2
```

Đây là **chỉ số**, không phải giá trị.

---

## Lỗi 2: Quên tăng biến trong `while`

```javascript
let i = 1;

while (i <= 5) {
    console.log(i);
}
```

→ Vòng lặp vô hạn.

Đúng:

```javascript
i++;
```

---

## Lỗi 3: Quên `break`

```javascript
while (true) {

}
```

Nếu không có điều kiện dừng, chương trình sẽ chạy mãi.

---

## Lỗi 4: Chỉnh sửa mảng trong khi đang duyệt

```javascript
const numbers = [1, 2, 3, 4];

for (const n of numbers) {
    if (n === 2) {
        numbers.pop();
    }
}
```

Việc thay đổi cấu trúc mảng trong khi lặp có thể dẫn đến kết quả khó đoán. Nếu cần xóa hoặc thêm phần tử, hãy cân nhắc tạo một mảng mới hoặc lặp theo chỉ số một cách cẩn thận.

---

# 18. Bài tập thực hành

## Bài 1

In các số từ 1 đến 100 bằng `for`.

---

## Bài 2

Tính tổng các số từ 1 đến 100.

Kết quả:

```
5050
```

---

## Bài 3

Cho mảng:

```javascript
const fruits = [
    "Táo",
    "Cam",
    "Xoài",
    "Dưa hấu"
];
```

* Dùng `for...of` để in từng phần tử.
* Dùng `for` để in kèm chỉ số.

Ví dụ:

```
0: Táo
1: Cam
2: Xoài
3: Dưa hấu
```

---

## Bài 4

Cho object:

```javascript
const employee = {
    id: 1001,
    name: "Ngọc",
    department: "IT",
    salary: 25000000
};
```

In toàn bộ:

```
id: 1001
name: Ngọc
department: IT
salary: 25000000
```

Sử dụng `Object.entries()`.

---

## Bài 5 (Thử thách)

Cho dữ liệu:

```javascript
const classes = [
    {
        name: "Lớp A",
        students: [
            { name: "An", score: 90 },
            { name: "Bình", score: 65 }
        ]
    },
    {
        name: "Lớp B",
        students: [
            { name: "Lan", score: 88 },
            { name: "Minh", score: 55 }
        ]
    }
];
```

Yêu cầu:

1. Dùng **vòng lặp lồng nhau** để duyệt toàn bộ dữ liệu.
2. In tên lớp.
3. In từng học sinh và điểm.
4. Nếu điểm ≥ 80 thì in `"Giỏi"`, ngược lại in `"Cần cố gắng"`.

Ví dụ:

```
Lớp A
- An: 90 (Giỏi)
- Bình: 65 (Cần cố gắng)

Lớp B
- Lan: 88 (Giỏi)
- Minh: 55 (Cần cố gắng)
```

---

# Tổng kết buổi 6

Bạn đã học được:

* Cách sử dụng `for`, `while` và `do...while`.
* Vai trò của `break` và `continue`.
* Sự khác biệt rất quan trọng giữa `for...of` (duyệt giá trị) và `for...in` (duyệt khóa/chỉ số).
* Các cách hiện đại để duyệt `Object` bằng `Object.keys()`, `Object.values()` và `Object.entries()`.
* Các kỹ thuật viết vòng lặp rõ ràng, dễ bảo trì.

Ở **Buổi 7**, chúng ta sẽ bắt đầu một trong những chủ đề quan trọng nhất của JavaScript: **Function (Hàm)**. Bạn sẽ học từ Function Declaration, Function Expression, Arrow Function, tham số, giá trị trả về, callback và các mẫu thiết kế hàm thường gặp trong các dự án JavaScript hiện đại.
