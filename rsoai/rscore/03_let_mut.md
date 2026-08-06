# Giáo trình Rust Professional 2026

# Giai đoạn 1 — Rust Foundation

# Buổi 3 — Variables & Mutability Deep Dive

> **Mục tiêu**

Sau buổi này bạn sẽ hiểu:

* Rust lưu biến như thế nào
* Vì sao Rust mặc định immutable
* `let`
* `mut`
* Shadowing
* Scope
* Type Inference
* Variable Binding
* Naming Convention
* Best Practice

Đây là một trong những buổi quan trọng nhất, vì tư duy về biến trong Rust rất khác Python, JavaScript hay C++.

---

# 1. Variable là gì?

Variable (biến) là **một tên (binding) gắn với một giá trị**.

Ví dụ:

```rust
fn main() {
    let age = 20;

    println!("{age}");
}
```

Ở đây:

```
age
 │
 ▼
20
```

Khác với nhiều ngôn ngữ, trong Rust `age` không chỉ đơn thuần là một "ô nhớ". Nó là một **binding** giữa tên và giá trị.

---

# 2. Biến trong Rust mặc định là Immutable

Đây là điều khiến nhiều người mới ngạc nhiên.

Ví dụ:

```rust
fn main() {
    let age = 20;

    age = 21;
}
```

Compiler báo lỗi:

```text
cannot assign twice to immutable variable
```

Rust mặc định:

```
Immutable
```

không phải

```
Mutable
```

---

## Tại sao?

Ví dụ Python:

```python
age = 20

age = 21

age = 30

age = "hello"

age = []
```

Biến có thể đổi liên tục.

Rust muốn hạn chế điều này để:

* giảm bug
* dễ đọc
* compiler tối ưu tốt hơn
* hỗ trợ concurrency an toàn

Đó là lý do **mọi biến đều bất biến (immutable) nếu bạn không nói rõ ngược lại**.

---

# 3. Mutable Variable

Nếu muốn thay đổi giá trị:

```rust
fn main() {
    let mut age = 20;

    age = 21;

    println!("{age}");
}
```

Kết quả:

```
21
```

Ở đây:

```
age

20

↓

21
```

`mut` báo cho compiler:

> "Tôi cho phép thay đổi biến này."

---

# 4. Ví dụ hoàn chỉnh

```rust
fn main() {
    let mut score = 0;

    println!("{score}");

    score += 10;

    println!("{score}");

    score += 30;

    println!("{score}");
}
```

Output

```
0
10
40
```

---

# 5. Immutable tốt hơn Mutable

Ví dụ

```rust
let x = 10;
```

Compiler biết:

```
x

không bao giờ thay đổi
```

Compiler có thể:

* tối ưu
* inline
* cache
* giảm kiểm tra

Đó là lý do Rust ưu tiên immutable.

---

# 6. Variable Binding

Ví dụ

```rust
let name = "Alice";
```

Không phải

```
name

=

Alice
```

mà là

```
name

bind

"Alice"
```

Rust dùng từ:

> Binding

---

# 7. Scope

Ví dụ

```rust
fn main() {
    let a = 10;

    {
        let b = 20;

        println!("{b}");
    }

    println!("{a}");
}
```

Kết quả

```
20
10
```

Nhưng

```rust
fn main() {
    {
        let b = 20;
    }

    println!("{b}");
}
```

Lỗi

```
cannot find value b
```

Vì `b` chỉ tồn tại trong block.

---

# 8. Block

Trong Rust

```
{}
```

là một block.

Ví dụ

```rust
fn main() {

    let a = 1;

    {
        let b = 2;
    }

}
```

Compiler hiểu

```
main

 ├── a

 └── block

      └── b
```

---

# 9. Type Inference

Rust có thể đoán kiểu.

```rust
let age = 20;
```

Compiler hiểu

```
i32
```

Ví dụ

```rust
let pi = 3.14;
```

Compiler

```
f64
```

Ví dụ

```rust
let ok = true;
```

Compiler

```
bool
```

---

# 10. Ghi rõ kiểu

Bạn có thể viết

```rust
let age: i32 = 20;
```

Hoặc

```rust
let pi: f64 = 3.14;
```

Hoặc

```rust
let active: bool = true;
```

---

# 11. Shadowing

Đây là điểm rất đặc trưng của Rust.

Ví dụ

```rust
fn main() {

    let x = 10;

    let x = 20;

    println!("{x}");

}
```

Kết quả

```
20
```

Có phải thay đổi biến không?

Không.

Compiler hiểu

```
x(10)

↓

x(20)
```

Đây là **binding mới**, không phải sửa giá trị cũ.

---

# 12. Shadowing khác Mutable

Mutable

```rust
let mut x = 10;

x = 20;
```

Shadowing

```rust
let x = 10;

let x = 20;
```

Khác nhau rất lớn.

Mutable:

```
cùng một biến
```

Shadowing:

```
biến mới
```

---

# 13. Shadowing đổi kiểu dữ liệu

Mutable

```rust
let mut x = 10;

x = "hello";
```

Không compile.

Shadowing

```rust
let x = 10;

let x = "hello";
```

Compile bình thường.

Đây là một ưu điểm lớn của shadowing.

---

# 14. Ví dụ thực tế

```rust
fn main() {
    let input = "42";

    let input: i32 = input.parse().unwrap();

    println!("{}", input * 2);
}
```

Ở đây:

Ban đầu

```
&str
```

Sau đó

```
i32
```

Compiler hoàn toàn chấp nhận nhờ shadowing.

---

# 15. Naming Convention

Rust dùng:

```
snake_case
```

Ví dụ

```rust
let student_name = "Alice";
```

Không nên

```rust
let StudentName = "";
```

Hoặc

```rust
let studentName = "";
```

---

# 16. Biến không dùng

Ví dụ

```rust
let age = 20;
```

Không dùng.

Compiler cảnh báo.

Nếu cố ý:

```rust
let _age = 20;
```

Hoặc

```rust
let _ = 20;
```

Không còn cảnh báo.

---

# 17. Ví dụ hoàn chỉnh

```rust
fn main() {
    let name = "Alice";

    let mut score = 80;

    println!("{name}");

    println!("{score}");

    score += 10;

    println!("{score}");

    let score = score * 2;

    println!("{score}");
}
```

Output

```
Alice

80

90

180
```

---

# 18. Ví dụ CLI nhỏ

```rust
fn main() {
    let app_name = "Student Manager";

    let mut version = 1;

    println!("{app_name}");

    println!("Version {version}");

    version += 1;

    println!("Version {version}");
}
```

Output

```
Student Manager
Version 1
Version 2
```

---

# 19. Best Practices

## Ưu tiên immutable

```rust
let name = "Alice";
```

Chỉ dùng `mut` khi thật sự cần.

---

## Dùng shadowing để chuyển đổi dữ liệu

```rust
let input = "100";
let input: i32 = input.parse().unwrap();
```

Rõ ràng hơn nhiều so với tạo nhiều biến trung gian.

---

## Đặt tên có ý nghĩa

Tốt:

```rust
let total_price = 100;
```

Không nên:

```rust
let x = 100;
```

---

## Khai báo kiểu khi cần

Rust suy luận kiểu rất tốt, nhưng với API công khai hoặc các giá trị dễ gây nhầm lẫn, việc ghi rõ kiểu giúp mã dễ đọc hơn:

```rust
let retries: u8 = 3;
```

---

# Những lỗi người mới thường gặp

1. **Quên `mut`** rồi cố gắng thay đổi giá trị của biến.
2. **Lạm dụng `mut`** cho mọi biến thay vì chỉ dùng khi cần.
3. **Nhầm shadowing với mutation**. `let x = ...; let x = ...;` tạo binding mới chứ không sửa binding cũ.
4. **Sử dụng biến ngoài phạm vi (scope)** dẫn đến lỗi biên dịch.
5. **Đặt tên không theo `snake_case`**, làm mã nguồn không nhất quán với hệ sinh thái Rust.

---

# Bài tập thực hành

## Bài 1

Khai báo:

```rust
name
age
salary
```

In ra màn hình bằng cú pháp định dạng mới:

```rust
println!("{name}");
```

---

## Bài 2

Tạo biến mutable:

```rust
counter
```

Tăng giá trị từ `0` lên `10` bằng nhiều phép cộng và in kết quả sau mỗi lần thay đổi.

---

## Bài 3

Thực hành shadowing:

```rust
let input = "123";
```

Chuyển thành số nguyên bằng `parse()` và in ra giá trị sau khi nhân đôi.

---

## Bài 4

Viết chương trình khai báo:

* `app_name`
* `version`
* `author`

Trong đó chỉ `version` là mutable. Tăng phiên bản thêm `1` rồi in toàn bộ thông tin.

---

# Tổng kết

Trong buổi học này, bạn đã nắm được:

* Biến trong Rust là **binding** giữa tên và giá trị.
* Biến mặc định là **immutable** để tăng tính an toàn và khả năng tối ưu.
* Cách sử dụng `mut` để cho phép thay đổi giá trị.
* Khái niệm **scope** và vòng đời của biến trong từng block.
* **Type inference** và cách khai báo kiểu tường minh.
* **Shadowing** và sự khác biệt với mutation.
* Quy ước đặt tên và các thực hành tốt khi làm việc với biến.

## Chuẩn bị cho buổi 4

Buổi tiếp theo sẽ đi sâu vào **Data Types Deep Dive**, bao gồm:

* Kiểu số nguyên (`i8` đến `i128`, `u8` đến `u128`, `isize`, `usize`)
* Kiểu số thực (`f32`, `f64`)
* `bool`, `char`
* Tuple và Array
* Kích thước bộ nhớ của từng kiểu
* Ép kiểu (`as`) và các lưu ý
* Overflow, Underflow và cách Rust xử lý trong chế độ Debug và Release
* Nhiều ví dụ thực tế có thể chạy ngay bằng `cargo run`.
