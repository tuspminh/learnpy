# Giáo trình Rust Professional 2026

# Giai đoạn 1 — Rust Foundation

# Buổi 5 — Functions Deep Dive

> **Mục tiêu**

Sau buổi học này bạn sẽ:

* Hiểu Function trong Rust hoạt động như thế nào.
* Phân biệt **Statement** và **Expression** (điểm rất quan trọng trong Rust).
* Biết cách truyền tham số.
* Biết cách trả về giá trị.
* Trả về nhiều giá trị bằng Tuple.
* Hiểu early return.
* Hiểu Diverging Function (`!`).
* Biết cách tổ chức hàm theo chuẩn Rust.

Đây là một trong những buổi quan trọng nhất vì **Rust là ngôn ngữ expression-oriented**. Nếu chưa hiểu điều này, bạn sẽ gặp khó khăn với `if`, `match`, `loop` và nhiều tính năng khác.

---

# 1. Function là gì?

Function (hàm) là một khối mã thực hiện một nhiệm vụ cụ thể.

Ví dụ đơn giản:

```rust
fn greet() {
    println!("Hello Rust!");
}

fn main() {
    greet();
}
```

Kết quả:

```text
Hello Rust!
```

---

# 2. Cú pháp của Function

```rust
fn function_name(parameter: Type) -> ReturnType {
    // body
}
```

Ví dụ:

```rust
fn square(x: i32) -> i32 {
    x * x
}
```

Trong đó:

* `fn`: từ khóa khai báo hàm.
* `square`: tên hàm.
* `x: i32`: tham số.
* `-> i32`: kiểu trả về.
* `x * x`: giá trị trả về.

---

# 3. Hàm không có tham số

```rust
fn show_banner() {
    println!("==================");
    println!(" Student Manager");
    println!("==================");
}

fn main() {
    show_banner();
}
```

Output:

```text
==================
 Student Manager
==================
```

---

# 4. Hàm có tham số

```rust
fn greet(name: &str) {
    println!("Hello {name}");
}

fn main() {
    greet("Alice");
    greet("Bob");
}
```

Output:

```text
Hello Alice
Hello Bob
```

---

# 5. Nhiều tham số

```rust
fn add(a: i32, b: i32) {
    println!("{}", a + b);
}

fn main() {
    add(3, 5);
}
```

Output

```text
8
```

---

# 6. Trả về giá trị

```rust
fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn main() {
    let result = add(10, 20);

    println!("{result}");
}
```

Output

```text
30
```

---

# 7. Không cần `return`

Đây là điểm khác với C, Java hoặc Python.

Rust:

```rust
fn square(x: i32) -> i32 {
    x * x
}
```

Không có:

```rust
return
```

vẫn hợp lệ.

Vì:

```rust
x * x
```

là **Expression**.

---

# 8. Statement vs Expression

Đây là khái niệm cực kỳ quan trọng.

## Statement

Statement thực hiện một hành động nhưng **không tạo ra giá trị**.

Ví dụ:

```rust
let x = 5;
```

Đây là Statement.

Nó không trả về giá trị.

---

## Expression

Expression luôn tạo ra một giá trị.

Ví dụ:

```rust
5 + 10
```

Expression có giá trị:

```text
15
```

---

Ví dụ khác

```rust
3 * 7
```

Giá trị:

```text
21
```

---

# 9. Block cũng là Expression

Đây là điểm rất mạnh của Rust.

```rust
fn main() {
    let x = {
        let a = 5;
        let b = 6;

        a + b
    };

    println!("{x}");
}
```

Output

```text
11
```

Block trả về:

```rust
a + b
```

---

Nếu viết

```rust
a + b;
```

thì sao?

Compiler báo lỗi.

Vì:

```rust
;
```

biến Expression thành Statement.

---

# 10. Dấu `;` rất quan trọng

Ví dụ đúng:

```rust
fn add() -> i32 {
    5
}
```

Sai:

```rust
fn add() -> i32 {
    5;
}
```

Compiler:

```text
expected i32

found ()
```

Tại sao?

Vì:

```rust
5;
```

đã trở thành Statement.

Statement có kiểu:

```text
()
```

---

# 11. Unit Type `()`

Rust có kiểu đặc biệt:

```text
()
```

gọi là **Unit Type**.

Ví dụ:

```rust
fn greet() {
    println!("Hello");
}
```

Thực chất compiler hiểu:

```rust
fn greet() -> () {
    println!("Hello");
}
```

---

# 12. Early Return

```rust
fn divide(a: i32, b: i32) -> i32 {
    if b == 0 {
        return 0;
    }

    a / b
}

fn main() {
    println!("{}", divide(10, 2));
    println!("{}", divide(10, 0));
}
```

Output

```text
5
0
```

Sử dụng `return` khi muốn thoát hàm sớm.

---

# 13. Trả về nhiều giá trị

Rust không hỗ trợ nhiều giá trị riêng lẻ.

Thay vào đó dùng Tuple.

```rust
fn student() -> (&'static str, u8) {
    ("Alice", 20)
}

fn main() {
    let (name, age) = student();

    println!("{name}");
    println!("{age}");
}
```

---

# 14. Hàm gọi hàm

```rust
fn square(x: i32) -> i32 {
    x * x
}

fn area(side: i32) -> i32 {
    square(side)
}

fn main() {
    println!("{}", area(5));
}
```

Output

```text
25
```

---

# 15. Function là First-Class?

Rust **không coi hàm là first-class object theo cách của Python hay JavaScript**, nhưng hàm có thể được truyền dưới dạng **function pointer** hoặc thông qua **closure**. Chúng ta sẽ học kỹ ở các buổi về Closure và Functional Programming.

Ví dụ:

```rust
fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn calculate(f: fn(i32, i32) -> i32, a: i32, b: i32) -> i32 {
    f(a, b)
}

fn main() {
    let result = calculate(add, 3, 4);
    println!("{result}");
}
```

---

# 16. Diverging Function

Một số hàm **không bao giờ trả về**.

Ví dụ:

```rust
fn forever() -> ! {
    loop {}
}
```

Kiểu:

```text
!
```

được gọi là **Never Type**.

Ví dụ khác:

```rust
fn fatal_error(message: &str) -> ! {
    panic!("{message}");
}
```

---

# 17. Ví dụ hoàn chỉnh

```rust
fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn multiply(a: i32, b: i32) -> i32 {
    a * b
}

fn divide(a: i32, b: i32) -> i32 {
    if b == 0 {
        return 0;
    }

    a / b
}

fn main() {
    println!("Add      : {}", add(5, 3));
    println!("Multiply : {}", multiply(5, 3));
    println!("Divide   : {}", divide(10, 2));
}
```

Output

```text
Add      : 8
Multiply : 15
Divide   : 5
```

---

# 18. Mini Project — Calculator

```rust
fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn sub(a: i32, b: i32) -> i32 {
    a - b
}

fn mul(a: i32, b: i32) -> i32 {
    a * b
}

fn div(a: i32, b: i32) -> Option<i32> {
    if b == 0 {
        None
    } else {
        Some(a / b)
    }
}

fn main() {
    println!("10 + 5 = {}", add(10, 5));
    println!("10 - 5 = {}", sub(10, 5));
    println!("10 * 5 = {}", mul(10, 5));

    match div(10, 5) {
        Some(result) => println!("10 / 5 = {result}"),
        None => println!("Không thể chia cho 0"),
    }
}
```

> **Lưu ý:** `Option` và `match` sẽ được học chi tiết ở các buổi sau. Hiện tại bạn chỉ cần biết đây là cách Rust biểu diễn một giá trị có thể tồn tại hoặc không.

---

# 19. Viết Unit Test

Một ưu điểm lớn của Rust là kiểm thử được tích hợp ngay trong Cargo.

```rust
fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
    }

    #[test]
    fn test_add_negative() {
        assert_eq!(add(-2, 3), 1);
    }
}
```

Chạy:

```bash
cargo test
```

---

# 20. Best Practices

## 1. Mỗi hàm chỉ nên làm một việc

Tốt:

```rust
fn calculate_total() {}
fn print_invoice() {}
```

Không nên:

```rust
fn do_everything() {}
```

---

## 2. Ưu tiên Expression

Thay vì:

```rust
fn max(a: i32, b: i32) -> i32 {
    if a > b {
        return a;
    }

    return b;
}
```

Nên viết:

```rust
fn max(a: i32, b: i32) -> i32 {
    if a > b {
        a
    } else {
        b
    }
}
```

Đây là phong cách rất "Rust".

---

## 3. Dùng `return` khi cần thoát sớm

Điều này giúp xử lý lỗi hoặc điều kiện đặc biệt rõ ràng hơn.

---

# Những lỗi người mới thường gặp

1. **Đặt dấu `;` sau biểu thức trả về**, khiến hàm trả về `()` thay vì kiểu mong muốn.
2. **Quên khai báo kiểu trả về (`-> Type`)** khi hàm cần trả về giá trị.
3. **Lạm dụng `return`** ở cuối hàm. Trong Rust, biểu thức cuối cùng thường đủ.
4. **Viết hàm quá dài**, thực hiện nhiều nhiệm vụ khác nhau.
5. **Nhầm giữa Statement và Expression**, đặc biệt trong `if`, `match` và block.

---

# Bài tập thực hành

## Bài 1

Viết các hàm:

* `square(x)`
* `cube(x)`
* `factorial(n)` (dùng vòng lặp, chưa dùng đệ quy)

In kết quả trong `main()`.

---

## Bài 2

Viết hàm:

```rust
fn min(a: i32, b: i32) -> i32
```

Sử dụng `if` như một expression, không dùng `return` ở cuối hàm.

---

## Bài 3

Viết hàm trả về Tuple:

```text
(name, age, city)
```

Sau đó destructure và in từng giá trị.

---

## Bài 4

Tạo một module `math` (đặt trong `src/math.rs`) chứa các hàm:

* `add`
* `sub`
* `mul`

Gọi chúng từ `main.rs`. Bài này sẽ giúp bạn làm quen với việc tách mã nguồn trước khi học Module và Crate chi tiết.

---

# Tổng kết

Trong buổi học này, bạn đã học được:

* Cách khai báo và sử dụng hàm trong Rust.
* Truyền tham số và trả về giá trị.
* Sự khác biệt giữa **Statement** và **Expression**.
* Vai trò quan trọng của dấu `;`.
* `Unit Type` (`()`).
* Trả về nhiều giá trị bằng Tuple.
* Early return và `Never Type` (`!`).
* Viết và chạy Unit Test với `cargo test`.

## Chuẩn bị cho buổi 6

Ở **Buổi 6 – Comments & Documentation Deep Dive**, chúng ta sẽ học:

* Comment một dòng và nhiều dòng.
* Documentation Comment (`///`, `//!`).
* Cách viết tài liệu theo chuẩn Rust.
* Sinh tài liệu HTML bằng `cargo doc`.
* Viết ví dụ chạy được trong tài liệu (doctest).
* Quy ước tài liệu cho thư viện và dự án mã nguồn mở.
* Thực hành xây dựng một thư viện nhỏ với tài liệu đầy đủ và có thể kiểm thử bằng `cargo test` và `cargo doc`.
