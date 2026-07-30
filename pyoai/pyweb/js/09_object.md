# Lộ trình JavaScript (Roadmap)

Chúng ta đang học theo lộ trình bài bản dành cho lập trình viên (đặc biệt nếu bạn có nền tảng Python):

### Phần I. Nền tảng JavaScript ✅

* ✅ Buổi 1. Giới thiệu JavaScript, cài đặt môi trường
* ✅ Buổi 2. Biến và kiểu dữ liệu
* ✅ Buổi 3. Toán tử
* ✅ Buổi 4. Điều kiện
* ✅ Buổi 5. Vòng lặp
* ✅ Buổi 6. Function
* ✅ Buổi 7. Function nâng cao
* ✅ Buổi 8. Scope, Hoisting, Lexical Scope

---

# Phần II. Object & Array

* **Buổi 9. Object Deep Dive** ← Hôm nay
* Buổi 10. Array Deep Dive
* Buổi 11. Destructuring & Spread/Rest
* Buổi 12. Iterable, Iterator và Collection

---

# Buổi 9. Object Deep Dive

> **Mục tiêu**
>
> Sau buổi học này bạn sẽ:
>
> * Hiểu Object trong JavaScript thực chất là gì.
> * Thành thạo Object Literal.
> * Hiểu Reference Type.
> * Thao tác thêm, sửa, xóa thuộc tính.
> * Viết Method.
> * Hiểu `this` cơ bản.
> * Biết các API quan trọng như `Object.keys()`, `Object.values()`, `Object.entries()`, `Object.assign()`, `Object.freeze()`.
> * So sánh Object JavaScript với Dictionary Python.

---

# 1. Object là gì?

Trong JavaScript, gần như mọi thứ đều là object hoặc hoạt động như object.

Ví dụ:

```javascript
const user = {
    name: "An",
    age: 20,
    active: true
};
```

Object là tập hợp các cặp:

```text
key → value
```

Ví dụ:

```text
name   → "An"

age    → 20

active → true
```

Khác với Python:

```python
user = {"name": "An", "age": 20}
```

Object JavaScript giống Dictionary nhưng mạnh hơn rất nhiều.

---

# 2. Object Literal

Đây là cách tạo object phổ biến nhất.

```javascript
const book = {
    title: "JavaScript",
    author: "Garden",
    pages: 500
};
```

---

# 3. Truy cập thuộc tính

Có hai cách.

## Dot notation

```javascript
console.log(book.title);
```

Kết quả

```
JavaScript
```

---

## Bracket notation

```javascript
console.log(book["title"]);
```

Kết quả

```
JavaScript
```

---

### Khi nào dùng `[]`?

Khi tên thuộc tính nằm trong biến.

```javascript
const key = "author";

console.log(book[key]);
```

Không thể viết:

```javascript
book.key
```

vì sẽ tìm thuộc tính tên `"key"`.

---

# 4. Thêm thuộc tính

```javascript
const user = {};

user.name = "Lan";
user.age = 21;

console.log(user);
```

Kết quả

```javascript
{
    name: "Lan",
    age: 21
}
```

---

# 5. Cập nhật thuộc tính

```javascript
user.age = 22;
```

---

# 6. Xóa thuộc tính

```javascript
delete user.age;
```

---

Ví dụ

```javascript
const person = {
    name: "An",
    age: 20
};

delete person.age;

console.log(person);
```

Kết quả

```javascript
{
    name: "An"
}
```

---

# 7. Property và Method

Object có thể chứa dữ liệu.

```javascript
const student = {
    name: "Minh",
    score: 90
};
```

Hoặc chứa hàm.

```javascript
const student = {

    name: "Minh",

    sayHello() {
        console.log("Xin chào");
    }

};

student.sayHello();
```

Kết quả

```
Xin chào
```

---

# 8. `this` cơ bản

```javascript
const user = {

    name: "Lan",

    hello() {
        console.log(this.name);
    }

};

user.hello();
```

Kết quả

```
Lan
```

Ở đây:

```text
this

↓

user
```

**Lưu ý:** `this` là một trong những chủ đề khó nhất của JavaScript. Hôm nay chỉ học cách sử dụng cơ bản trong method. Cơ chế hoạt động đầy đủ sẽ được học ở **Buổi 23**.

---

# 9. Object là Reference Type

Đây là điểm khác biệt lớn với Number, String, Boolean.

```javascript
const a = {
    name: "Lan"
};

const b = a;
```

Hãy hình dung:

```text
a ───────┐
         │
         ▼
    Object #101

b ───────┘
```

Cả `a` và `b` cùng trỏ đến một object.

---

Ví dụ

```javascript
const a = {
    score: 90
};

const b = a;

b.score = 100;

console.log(a.score);
```

Kết quả

```
100
```

Không phải:

```
90
```

---

# 10. So sánh object

```javascript
const a = {
    x: 1
};

const b = {
    x: 1
};

console.log(a === b);
```

Kết quả

```
false
```

Vì:

```text
Object #1

≠

Object #2
```

---

Nhưng:

```javascript
const a = {
    x: 1
};

const b = a;

console.log(a === b);
```

Kết quả

```
true
```

---

# 11. Object.keys()

```javascript
const user = {
    name: "An",
    age: 20
};

console.log(Object.keys(user));
```

Kết quả

```javascript
[
    "name",
    "age"
]
```

---

# 12. Object.values()

```javascript
console.log(Object.values(user));
```

Kết quả

```javascript
[
    "An",
    20
]
```

---

# 13. Object.entries()

```javascript
console.log(Object.entries(user));
```

Kết quả

```javascript
[
    ["name", "An"],
    ["age", 20]
]
```

---

Có thể duyệt rất đẹp.

```javascript
for (const [key, value] of Object.entries(user)) {
    console.log(key, value);
}
```

Kết quả

```
name An

age 20
```

---

# 14. Object.assign()

Dùng để copy object.

```javascript
const user = {
    name: "Lan",
    age: 20
};

const copy = Object.assign({}, user);

copy.age = 99;

console.log(user.age);
```

Kết quả

```
20
```

Không còn dùng chung vùng nhớ.

---

# 15. Spread Operator

Hiện nay dùng nhiều hơn.

```javascript
const copy = {
    ...user
};
```

Kết quả giống:

```javascript
Object.assign({}, user)
```

---

# 16. Object.freeze()

Khóa object.

```javascript
const config = {
    port: 8080
};

Object.freeze(config);

config.port = 9000;

console.log(config.port);
```

Kết quả

```
8080
```

---

# 17. Object.seal()

Cho phép sửa.

Không cho:

* thêm
* xóa

```javascript
const user = {
    name: "Lan"
};

Object.seal(user);

user.name = "An";

user.age = 20;

delete user.name;

console.log(user);
```

Kết quả

```javascript
{
    name: "An"
}
```

---

# 18. Shallow Copy

```javascript
const user = {

    name: "Lan",

    address: {
        city: "Hà Nội"
    }

};

const copy = {
    ...user
};

copy.address.city = "Đà Nẵng";

console.log(user.address.city);
```

Kết quả

```
Đà Nẵng
```

Vì chỉ copy tầng đầu tiên.

Đây gọi là:

```text
Shallow Copy
```

---

# 19. Deep Copy (Giới thiệu)

Shallow Copy:

```text
user

↓

address

↓

city
```

Deep Copy:

```text
user'

↓

address'

↓

city'
```

Hiện nay có cách hiện đại:

```javascript
const copy = structuredClone(user);
```

Chúng ta sẽ học kỹ ở **Buổi 11**.

---

# 20. So sánh với Python

Python

```python
user = {"name": "Lan"}

print(user["name"])
```

JavaScript

```javascript
const user = {
    name: "Lan"
};

console.log(user.name);
```

---

# 21. Best Practices

## Dùng `const`

```javascript
const user = {};
```

Không cần dùng `let` nếu chỉ thay đổi thuộc tính.

```javascript
user.name = "Lan";
```

`const` chỉ ngăn việc gán lại biến:

```javascript
user = {};
```

không cho phép, nhưng vẫn có thể thay đổi nội dung object (trừ khi đã `freeze`).

---

## Ưu tiên Dot Notation

```javascript
user.name
```

Chỉ dùng:

```javascript
user[key]
```

khi key là biến hoặc có ký tự đặc biệt.

---

## Dùng `Object.entries()`

Thay vì:

```javascript
for (const key in user) {
    console.log(key, user[key]);
}
```

Có thể viết:

```javascript
for (const [key, value] of Object.entries(user)) {
    console.log(key, value);
}
```

Dễ đọc hơn.

---

# 22. Những lỗi người học Python thường gặp

## Lỗi 1: So sánh object bằng `===`

```javascript
{} === {}
```

Kết quả

```
false
```

---

## Lỗi 2: Nghĩ Spread là Deep Copy

Sai.

```javascript
const copy = {
    ...user
};
```

Chỉ copy một cấp.

---

## Lỗi 3: Dùng Arrow Function làm method

```javascript
const user = {
    name: "Lan",

    hello: () => {
        console.log(this.name);
    }
};
```

Kết quả thường không như mong đợi vì **Arrow Function không có `this` riêng**. Với method của object, hãy ưu tiên cú pháp:

```javascript
const user = {
    name: "Lan",
    hello() {
        console.log(this.name);
    }
};
```

---

## Lỗi 4: Dùng `for...in` mà không biết đang duyệt key

```javascript
for (const item in user) {
    console.log(item);
}
```

Kết quả là:

```
name

age
```

không phải giá trị.

---

# 23. Ví dụ hoàn chỉnh

```javascript
const library = {
    name: "Thư viện Trung tâm",
    books: [
        {
            title: "JavaScript",
            price: 250000
        },
        {
            title: "Python",
            price: 320000
        }
    ],

    printBooks() {
        console.log(`=== ${this.name} ===`);

        for (const book of this.books) {
            console.log(`${book.title} - ${book.price} VNĐ`);
        }
    }
};

library.printBooks();
```

Kết quả:

```
=== Thư viện Trung tâm ===
JavaScript - 250000 VNĐ
Python - 320000 VNĐ
```

---

# 24. Bài tập thực hành

## Bài 1

Tạo object `student` gồm:

* name
* age
* score

In toàn bộ thông tin.

---

## Bài 2

Viết method:

```javascript
introduce()
```

In:

```
Xin chào, tôi là ...
```

---

## Bài 3

Viết chương trình dùng:

* `Object.keys()`
* `Object.values()`
* `Object.entries()`

để duyệt object.

---

## Bài 4

Chứng minh object là **Reference Type**.

Gợi ý:

* Gán hai biến cùng trỏ đến một object.
* Thay đổi một biến.
* Quan sát biến còn lại.

---

## Bài 5 (Thử thách)

Xây dựng object:

```javascript
const company = {
    name: "ABC",
    employees: [
        {
            id: 1,
            name: "An",
            salary: 15000000
        },
        {
            id: 2,
            name: "Lan",
            salary: 18000000
        },
        {
            id: 3,
            name: "Minh",
            salary: 22000000
        }
    ]
};
```

Yêu cầu:

1. Viết method `printEmployees()` để in toàn bộ nhân viên.
2. Viết method `totalSalary()` trả về tổng lương của tất cả nhân viên.
3. Viết method `findEmployee(id)` trả về thông tin nhân viên theo `id`.
4. Nếu không tìm thấy nhân viên, trả về `null`.

---

# Tổng kết buổi 9

Trong buổi học này, bạn đã nắm được:

* Object Literal và cách tổ chức dữ liệu bằng object.
* Truy cập, thêm, sửa và xóa thuộc tính.
* Method và cách sử dụng `this` ở mức cơ bản.
* Bản chất **Reference Type** của object.
* Các API quan trọng: `Object.keys()`, `Object.values()`, `Object.entries()`, `Object.assign()`, `Object.freeze()` và `Object.seal()`.
* Sự khác nhau giữa **Shallow Copy** và **Deep Copy** (giới thiệu).

Ở **Buổi 10**, chúng ta sẽ học **Array Deep Dive**: các phương thức cốt lõi (`push`, `pop`, `shift`, `unshift`, `slice`, `splice`), cùng các phương thức lập trình hàm như `map`, `filter`, `reduce`, `find`, `some`, `every` và cách xử lý mảng theo phong cách JavaScript hiện đại.
