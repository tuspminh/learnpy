# Buổi 5. Cấu trúc điều khiển trong JavaScript

**Chủ đề:** `if` • `else` • `else if` • `switch` • Toán tử ba ngôi (`?:`) • Truthy & Falsy • Điều kiện lồng nhau • Guard Clause • Best Practices

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Thành thạo các cấu trúc rẽ nhánh trong JavaScript.
> * Hiểu cách JavaScript đánh giá điều kiện.
> * Hiểu khái niệm **Truthy** và **Falsy**.
> * Biết khi nào dùng `if`, `switch` và toán tử ba ngôi.
> * Viết được các chương trình xử lý logic thực tế.

---

# 1. Điều khiển luồng là gì?

Mặc định chương trình chạy từ trên xuống dưới:

```text
Dòng 1
↓

Dòng 2
↓

Dòng 3
↓

Kết thúc
```

Nhưng thực tế, chương trình cần đưa ra quyết định:

* Nếu đăng nhập thành công → vào trang chủ.
* Nếu chưa đăng nhập → chuyển đến trang đăng nhập.
* Nếu là quản trị viên → hiển thị chức năng quản trị.

Đó là vai trò của **cấu trúc điều khiển**.

---

# 2. Câu lệnh `if`

Cú pháp:

```javascript
if (điều_kiện) {
    // thực hiện khi điều kiện đúng
}
```

Ví dụ:

```javascript
const age = 20;

if (age >= 18) {
    console.log("Đủ tuổi");
}
```

Kết quả:

```text
Đủ tuổi
```

Nếu điều kiện sai:

```javascript
const age = 15;

if (age >= 18) {
    console.log("Đủ tuổi");
}

console.log("Kết thúc");
```

Kết quả:

```text
Kết thúc
```

---

# 3. `if...else`

```javascript
const age = 16;

if (age >= 18) {
    console.log("Người lớn");
} else {
    console.log("Trẻ em");
}
```

Kết quả:

```text
Trẻ em
```

---

# 4. `if...else if...else`

```javascript
const score = 82;

if (score >= 90) {
    console.log("Xuất sắc");
} else if (score >= 80) {
    console.log("Giỏi");
} else if (score >= 65) {
    console.log("Khá");
} else if (score >= 50) {
    console.log("Trung bình");
} else {
    console.log("Yếu");
}
```

Kết quả:

```text
Giỏi
```

---

# 5. Điều kiện lồng nhau

```javascript
const age = 20;
const hasLicense = true;

if (age >= 18) {
    if (hasLicense) {
        console.log("Được phép lái xe");
    } else {
        console.log("Chưa có bằng lái");
    }
}
```

Có thể viết gọn hơn:

```javascript
if (age >= 18 && hasLicense) {
    console.log("Được phép lái xe");
}
```

---

# 6. Truthy và Falsy

Đây là một trong những đặc điểm quan trọng nhất của JavaScript.

JavaScript không chỉ chấp nhận `true` và `false` trong điều kiện.

Ví dụ:

```javascript
if ("Hello") {
    console.log("Được thực hiện");
}
```

Kết quả:

```text
Được thực hiện
```

Vì `"Hello"` là **Truthy**.

---

# 7. Các giá trị Falsy

JavaScript chỉ có một số ít giá trị được coi là **Falsy**:

| Giá trị     | Giải thích       |
| ----------- | ---------------- |
| `false`     | Boolean sai      |
| `0`         | Số 0             |
| `-0`        | Âm 0             |
| `0n`        | BigInt bằng 0    |
| `""`        | Chuỗi rỗng       |
| `null`      | Không có giá trị |
| `undefined` | Chưa có giá trị  |
| `NaN`       | Không phải số    |

Ví dụ:

```javascript
if (0) {
    console.log("A");
} else {
    console.log("B");
}
```

Kết quả:

```text
B
```

---

# 8. Các giá trị Truthy

Hầu hết các giá trị còn lại đều là Truthy:

```javascript
"Hello"
1
-5
[]
{}
Symbol()
123n
```

Ví dụ:

```javascript
if ([]) {
    console.log("Array là Truthy");
}
```

Kết quả:

```text
Array là Truthy
```

Ngay cả object rỗng cũng là Truthy:

```javascript
if ({}) {
    console.log("Object là Truthy");
}
```

---

# 9. So sánh với Python

Python:

```python
if []:
    print("Có")
else:
    print("Không")
```

Kết quả:

```text
Không
```

JavaScript:

```javascript
if ([]) {
    console.log("Có");
} else {
    console.log("Không");
}
```

Kết quả:

```text
Có
```

> **Đây là điểm khác biệt rất quan trọng.**
>
> Trong JavaScript, `[]` và `{}` luôn là Truthy.

---

# 10. Toán tử ba ngôi (`?:`)

Đã học ở buổi trước, nhưng đây là nơi sử dụng phổ biến nhất.

```javascript
const age = 20;

const message = age >= 18
    ? "Người lớn"
    : "Trẻ em";

console.log(message);
```

---

# 11. `switch`

Dùng khi có nhiều nhánh theo một giá trị.

```javascript
const day = 3;

switch (day) {
    case 1:
        console.log("Thứ Hai");
        break;

    case 2:
        console.log("Thứ Ba");
        break;

    case 3:
        console.log("Thứ Tư");
        break;

    default:
        console.log("Không hợp lệ");
}
```

Kết quả:

```text
Thứ Tư
```

---

# 12. Vai trò của `break`

Nếu quên `break`:

```javascript
const day = 1;

switch (day) {
    case 1:
        console.log("Một");

    case 2:
        console.log("Hai");

    case 3:
        console.log("Ba");
}
```

Kết quả:

```text
Một
Hai
Ba
```

Hiện tượng này gọi là **fall-through**.

---

# 13. Gom nhiều `case`

```javascript
const month = 2;

switch (month) {
    case 12:
    case 1:
    case 2:
        console.log("Mùa đông");
        break;

    default:
        console.log("Mùa khác");
}
```

---

# 14. Guard Clause

Đây là kỹ thuật được dùng rất nhiều trong các dự án thực tế.

Thay vì:

```javascript
function login(user) {
    if (user !== null) {
        console.log("Xin chào");
    }
}
```

Viết:

```javascript
function login(user) {
    if (!user) {
        return;
    }

    console.log("Xin chào");
}
```

Ưu điểm:

* Giảm lồng nhau.
* Dễ đọc.
* Dễ bảo trì.

---

# 15. Ví dụ hoàn chỉnh

```javascript
const user = {
    name: "An",
    age: 20,
    role: "admin"
};

if (!user) {
    console.log("Không có người dùng");
} else {
    console.log(`Xin chào ${user.name}`);

    if (user.age >= 18) {
        console.log("Đã đủ tuổi");
    }

    switch (user.role) {
        case "admin":
            console.log("Quản trị viên");
            break;

        case "editor":
            console.log("Biên tập viên");
            break;

        default:
            console.log("Người dùng");
    }
}
```

Kết quả:

```text
Xin chào An
Đã đủ tuổi
Quản trị viên
```

---

# 16. So sánh với Python

| Python                 | JavaScript  |
| ---------------------- | ----------- |
| `if`                   | `if`        |
| `elif`                 | `else if`   |
| `else`                 | `else`      |
| `match` (Python 3.10+) | `switch`    |
| `x if c else y`        | `c ? x : y` |

---

# 17. Best Practices

## Luôn dùng dấu `{}`

Không nên:

```javascript
if (age >= 18)
    console.log("OK");
```

Nên:

```javascript
if (age >= 18) {
    console.log("OK");
}
```

---

## Không lồng quá nhiều `if`

Sai:

```javascript
if (...) {
    if (...) {
        if (...) {
            ...
        }
    }
}
```

Hãy cân nhắc dùng **Guard Clause** hoặc tách thành hàm.

---

## Dùng `switch` khi có nhiều nhánh cố định

Không nên:

```javascript
if (role === "admin") ...
else if (role === "editor") ...
else if (role === "guest") ...
```

Có thể dùng:

```javascript
switch (role) {
    ...
}
```

---

## Dùng `===`

```javascript
if (age === 18) {
}
```

Không nên:

```javascript
if (age == 18) {
}
```

---

# 18. Những lỗi người học Python thường gặp

## Lỗi 1: Quên dấu `{}`

Sai:

```javascript
if (true)
    console.log("A");
    console.log("B");
```

`"B"` luôn được in.

---

## Lỗi 2: Cho rằng `[]` là Falsy

Sai:

```javascript
if ([]) {
    console.log("Không chạy");
}
```

Thực tế:

```text
Không chạy ❌

Array là Truthy ✔
```

---

## Lỗi 3: Quên `break`

```javascript
switch (x) {
    case 1:
        ...
}
```

Có thể gây lỗi **fall-through** nếu không chủ ý.

---

## Lỗi 4: Dùng nhiều `if` độc lập

Sai:

```javascript
if (score >= 90) {
    console.log("A");
}

if (score >= 80) {
    console.log("B");
}
```

Với `score = 95`, cả hai điều kiện đều đúng và sẽ in cả `"A"` lẫn `"B"`.

Đúng:

```javascript
if (score >= 90) {
    console.log("A");
} else if (score >= 80) {
    console.log("B");
}
```

---

# 19. Bài tập thực hành

## Bài 1

Nhập điểm số (`score`).

Hiển thị:

* Xuất sắc
* Giỏi
* Khá
* Trung bình
* Yếu

---

## Bài 2

Viết chương trình kiểm tra năm nhuận.

Điều kiện:

* Chia hết cho 400 → năm nhuận.
* Chia hết cho 4 nhưng không chia hết cho 100 → năm nhuận.
* Ngược lại → không phải năm nhuận.

---

## Bài 3

Cho:

```javascript
const role = "editor";
```

Dùng `switch` để in:

* admin
* editor
* guest
* unknown

---

## Bài 4

Cho:

```javascript
const user = {
    name: "Lan"
};
```

Nếu người dùng có tên thì in:

```text
Xin chào Lan
```

Nếu không có dữ liệu người dùng (`null` hoặc `undefined`) thì in:

```text
Không có người dùng
```

Hãy áp dụng **Guard Clause**.

---

## Bài 5 (Thử thách)

Viết chương trình mô phỏng hệ thống đăng nhập:

```javascript
const user = {
    username: "admin",
    password: "123456",
    active: true,
    role: "admin"
};
```

Yêu cầu:

1. Nếu `user` là `null` → `"Không tìm thấy người dùng"`.
2. Nếu `active` là `false` → `"Tài khoản bị khóa"`.
3. Nếu vai trò là `"admin"` → `"Chào Quản trị viên"`.
4. Nếu vai trò là `"editor"` → `"Chào Biên tập viên"`.
5. Các trường hợp khác → `"Chào Người dùng"`.

---

# Tổng kết buổi 5

Bạn đã học:

* `if`, `else`, `else if`.
* `switch` và hiện tượng **fall-through**.
* Toán tử ba ngôi (`?:`) trong ngữ cảnh điều kiện.
* Khái niệm **Truthy** và **Falsy** – một trong những điểm khác biệt lớn giữa JavaScript và Python.
* Kỹ thuật **Guard Clause** để giảm lồng nhau và tăng tính dễ đọc của mã nguồn.

Ở **Buổi 6**, chúng ta sẽ học về **vòng lặp trong JavaScript**: `for`, `while`, `do...while`, `for...of`, `for...in`, cùng với `break`, `continue`, vòng lặp lồng nhau và các kỹ thuật duyệt mảng, chuỗi và object theo phong cách hiện đại.
