# Buổi 3. Toán tử trong JavaScript (Operators)

**Chủ đề:** Toán tử số học • Gán • So sánh • Logic • Bitwise • Điều kiện • Nullish Coalescing (`??`) • Optional Chaining (`?.`) • `==` và `===`

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Thành thạo các toán tử cơ bản và nâng cao trong JavaScript.
> * Hiểu rõ sự khác nhau giữa `==` và `===`.
> * Biết sử dụng `??` và `?.` trong thực tế.
> * So sánh cách hoạt động với Python.
> * Tránh các lỗi phổ biến của người mới học JavaScript.

---

# 1. Toán tử là gì?

Toán tử (Operator) là ký hiệu dùng để thực hiện một phép toán trên dữ liệu (toán hạng).

Ví dụ:

```javascript
let a = 10;
let b = 5;

console.log(a + b);
```

Kết quả:

```
15
```

---

# 2. Các nhóm toán tử

JavaScript có nhiều nhóm toán tử:

| Nhóm              | Ví dụ               |       |       |
| ----------------- | ------------------- | ----- | ----- |
| Số học            | `+ - * / % **`      |       |       |
| Gán               | `=` `+=` `-=`       |       |       |
| So sánh           | `==` `===` `!=` `>` |       |       |
| Logic             | `&&` `              |       | ` `!` |
| Bitwise           | `&` `               | ` `^` |       |
| Điều kiện         | `?:`                |       |       |
| Nullish           | `??`                |       |       |
| Optional Chaining | `?.`                |       |       |

---

# 3. Toán tử số học

```javascript
let a = 10;
let b = 3;

console.log(a + b);
console.log(a - b);
console.log(a * b);
console.log(a / b);
console.log(a % b);
```

Kết quả:

```
13
7
30
3.3333333333333335
1
```

---

## Lũy thừa

```javascript
console.log(2 ** 3);
```

Kết quả:

```
8
```

Python:

```python
2**3
```

Giống hệt.

---

# 4. Toán tử tăng giảm

```javascript
let x = 5;

x++;

console.log(x);
```

Kết quả:

```
6
```

---

Giảm:

```javascript
x--;
```

---

## Prefix

```javascript
let a = 5;

console.log(++a);
```

Kết quả:

```
6
```

---

## Postfix

```javascript
let a = 5;

console.log(a++);
console.log(a);
```

Kết quả:

```
5
6
```

Khác biệt:

* `++a`: tăng trước, rồi dùng giá trị.
* `a++`: dùng giá trị hiện tại, rồi mới tăng.

---

# 5. Toán tử gán

```javascript
let score = 100;
```

---

## Cộng rồi gán

```javascript
score += 20;
```

Tương đương:

```javascript
score = score + 20;
```

---

Các toán tử tương tự:

```javascript
-=

*=

/=

%=

**=
```

Ví dụ:

```javascript
let money = 500;

money *= 2;

console.log(money);
```

Kết quả:

```
1000
```

---

# 6. Toán tử so sánh

```javascript
console.log(10 > 5);
```

```
true
```

---

```javascript
console.log(10 < 5);
```

```
false
```

---

```javascript
>=

<=

!=
```

---

# 7. `==` và `===`

Đây là chủ đề quan trọng nhất của buổi học.

## `==`

So sánh sau khi **ép kiểu** (type coercion).

Ví dụ:

```javascript
console.log(5 == "5");
```

Kết quả:

```
true
```

Vì JavaScript tự chuyển `"5"` thành `5`.

---

Ví dụ:

```javascript
console.log(false == 0);
```

Kết quả:

```
true
```

---

Ví dụ:

```javascript
console.log("" == 0);
```

Kết quả:

```
true
```

Đây là lý do nhiều lập trình viên tránh dùng `==`.

---

## `===`

So sánh **không ép kiểu**.

```javascript
console.log(5 === "5");
```

Kết quả:

```
false
```

---

```javascript
console.log(false === 0);
```

```
false
```

---

### Quy tắc vàng

**Luôn ưu tiên dùng `===` và `!==` trong mã nguồn hiện đại**, trừ khi bạn thực sự hiểu và cần hành vi ép kiểu của `==`.

---

# 8. So sánh Object

```javascript
const a = { name: "An" };
const b = { name: "An" };

console.log(a === b);
```

Kết quả:

```
false
```

Vì:

```
a ----> Object A

b ----> Object B
```

Hai đối tượng khác nhau trong bộ nhớ.

---

Nếu:

```javascript
const a = { name: "An" };

const b = a;

console.log(a === b);
```

Kết quả:

```
true
```

---

# 9. Toán tử logic

## AND

```javascript
console.log(true && true);
```

```
true
```

---

```javascript
console.log(true && false);
```

```
false
```

---

## OR

```javascript
console.log(true || false);
```

```
true
```

---

## NOT

```javascript
console.log(!true);
```

```
false
```

---

# 10. Short-circuit

JavaScript đánh giá biểu thức từ trái sang phải.

```javascript
console.log(false && console.log("Hello"));
```

Không in `"Hello"` vì `false && ...` đã chắc chắn là `false`.

---

```javascript
console.log(true || console.log("Hello"));
```

Cũng không in `"Hello"` vì `true || ...` luôn là `true`.

---

# 11. Toán tử ba ngôi (Ternary)

```javascript
let age = 20;

let result = age >= 18 ? "Người lớn" : "Trẻ em";

console.log(result);
```

Kết quả:

```
Người lớn
```

Python:

```python
result = "Người lớn" if age >= 18 else "Trẻ em"
```

---

# 12. Nullish Coalescing (`??`)

Dùng khi muốn lấy giá trị mặc định **chỉ khi giá trị là `null` hoặc `undefined`**.

```javascript
let name = null;

console.log(name ?? "Khách");
```

Kết quả:

```
Khách
```

---

Ví dụ:

```javascript
let score = 0;

console.log(score ?? 100);
```

Kết quả:

```
0
```

Vì `0` không phải `null` hoặc `undefined`.

---

# 13. So sánh `||` và `??`

```javascript
let score = 0;

console.log(score || 100);
```

Kết quả:

```
100
```

Do `0` là giá trị *falsy*.

---

Nhưng:

```javascript
console.log(score ?? 100);
```

Kết quả:

```
0
```

---

### Khi nào dùng?

* `||`: khi muốn thay thế mọi giá trị *falsy* (`0`, `""`, `false`, `null`, `undefined`, `NaN`).
* `??`: khi chỉ muốn thay thế `null` hoặc `undefined`.

---

# 14. Optional Chaining (`?.`)

Giả sử:

```javascript
const user = {
    name: "An"
};
```

Nếu:

```javascript
console.log(user.address.city);
```

Lỗi:

```
TypeError
```

---

Dùng:

```javascript
console.log(user.address?.city);
```

Kết quả:

```
undefined
```

Không phát sinh lỗi.

---

Có thể lồng nhiều cấp:

```javascript
console.log(user.address?.street?.name);
```

---

# 15. Bitwise

Ví dụ:

```javascript
console.log(5 & 3);
```

```
1
```

---

```javascript
console.log(5 | 3);
```

```
7
```

---

```javascript
console.log(5 ^ 3);
```

```
6
```

Bitwise chủ yếu dùng trong các bài toán xử lý bit, tối ưu hiệu năng hoặc giao tiếp với thiết bị. Trong phát triển web thông thường, bạn sẽ ít gặp hơn.

---

# 16. Thứ tự ưu tiên toán tử

Ví dụ:

```javascript
console.log(2 + 3 * 4);
```

Kết quả:

```
14
```

---

Muốn cộng trước:

```javascript
console.log((2 + 3) * 4);
```

Kết quả:

```
20
```

Luôn dùng ngoặc khi biểu thức phức tạp để tăng tính rõ ràng.

---

# 17. Ví dụ hoàn chỉnh

```javascript
const user = {
    name: "An",
    age: 20
};

const score = 0;
const city = user.address?.city ?? "Chưa cập nhật";

console.log("Tên:", user.name);
console.log("Thành phố:", city);

console.log("Điểm:", score || 100);
console.log("Điểm thật:", score ?? 100);

console.log("Đủ tuổi:", user.age >= 18);

console.log("So sánh:", 5 === "5");

const level = user.age >= 18 ? "Người lớn" : "Trẻ em";

console.log("Phân loại:", level);
```

Kết quả:

```
Tên: An
Thành phố: Chưa cập nhật
Điểm: 100
Điểm thật: 0
Đủ tuổi: true
So sánh: false
Phân loại: Người lớn
```

---

# 18. So sánh với Python

| Python                         | JavaScript      |
| ------------------------------ | --------------- |
| `==` không ép kiểu mạnh như JS | `==` có ép kiểu |
| Không có `===`                 | Có `===`        |
| `x if cond else y`             | `cond ? x : y`  |
| Không có `?.`                  | Có `?.`         |
| Không có `??`                  | Có `??`         |

---

# 19. Best Practices

* Luôn dùng `===` và `!==`.
* Ưu tiên `??` khi xử lý giá trị mặc định từ API hoặc cơ sở dữ liệu.
* Dùng `?.` để truy cập dữ liệu lồng nhau an toàn.
* Dùng ngoặc `()` để biểu thức rõ ràng, tránh phụ thuộc vào thứ tự ưu tiên toán tử.
* Không lạm dụng bitwise nếu không thực sự cần.

---

# 20. Những lỗi người học Python thường gặp

### Lỗi 1: Dùng `==` thay vì `===`

```javascript
console.log(0 == false);   // true
console.log(0 === false);  // false
```

---

### Lỗi 2: Dùng `||` thay cho `??`

```javascript
const quantity = 0;

console.log(quantity || 10); // 10
console.log(quantity ?? 10); // 0
```

Nếu `0` là giá trị hợp lệ, hãy dùng `??`.

---

### Lỗi 3: Quên dùng `?.`

```javascript
const user = {};

console.log(user.profile.name);
```

Lỗi vì `profile` chưa tồn tại.

Đúng:

```javascript
console.log(user.profile?.name);
```

---

### Lỗi 4: So sánh hai object bằng `===`

```javascript
const a = { id: 1 };
const b = { id: 1 };

console.log(a === b); // false
```

Muốn so sánh nội dung, cần so sánh từng thuộc tính hoặc sử dụng hàm chuyên biệt.

---

# 21. Bài tập thực hành

### Bài 1

Viết chương trình tính:

* Tổng
* Hiệu
* Tích
* Thương
* Phần dư
* Lũy thừa

của hai số.

---

### Bài 2

Khai báo:

```javascript
const age = 16;
```

Dùng toán tử ba ngôi để in:

* `"Đủ tuổi"`
* `"Chưa đủ tuổi"`

---

### Bài 3

Tạo object:

```javascript
const student = {
    name: "Lan"
};
```

In ra:

* `student.address?.city`
* `student.address?.street?.name`

Quan sát kết quả.

---

### Bài 4

So sánh kết quả của các biểu thức sau và giải thích vì sao:

```javascript
5 == "5"
5 === "5"
false == 0
false === 0
null == undefined
null === undefined
```

---

### Bài 5 (Thử thách)

Cho dữ liệu:

```javascript
const employee = {
    name: "Minh",
    department: {
        manager: {
            name: "Hùng"
        }
    }
};
```

Viết chương trình:

* In tên nhân viên.
* In tên quản lý bằng `?.`.
* Nếu phòng ban hoặc quản lý không tồn tại thì hiển thị `"Chưa có quản lý"` bằng `??`.
* Dùng toán tử ba ngôi để phân loại nhân viên theo tuổi (tự thêm thuộc tính `age`).

---

## Tổng kết buổi 3

Bạn đã nắm được:

* Các toán tử số học, gán, so sánh và logic.
* Sự khác biệt quan trọng giữa `==` và `===`.
* Cơ chế **short-circuit** của `&&` và `||`.
* Cách sử dụng **Nullish Coalescing (`??`)** và **Optional Chaining (`?.`)** trong các tình huống thực tế.
* Các lỗi phổ biến mà lập trình viên Python thường gặp khi chuyển sang JavaScript.

**Buổi 4** sẽ tập trung vào **String**: chuỗi trong JavaScript, **Template Literal**, ký tự Unicode, escape sequence, các phương thức xử lý chuỗi quan trọng (`slice`, `substring`, `replace`, `split`, `trim`, `includes`, `startsWith`, `endsWith`, `padStart`, `padEnd`,...), cùng nhiều ví dụ thực tế và so sánh chi tiết với Python.
