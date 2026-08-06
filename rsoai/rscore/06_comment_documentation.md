# Giáo trình Rust Professional 2026

# Giai đoạn 1 – Rust Foundation

# Buổi 6 – Comments & Documentation Deep Dive

> **Mục tiêu**

Sau buổi học này bạn sẽ:

* Hiểu các loại comment trong Rust.
* Biết khi nào nên và không nên viết comment.
* Thành thạo Documentation Comment (`///`, `//!`).
* Biết cách sinh tài liệu HTML với `cargo doc`.
* Biết viết **doctest** (ví dụ trong tài liệu có thể chạy được).
* Biết tổ chức tài liệu cho thư viện (library crate).

> **Lưu ý quan trọng:** Một trong những điểm mạnh của Rust là **tài liệu (documentation) là một phần của mã nguồn**. Nhiều thư viện nổi tiếng có tài liệu được tạo trực tiếp từ source code.

---

# 1. Các loại Comment trong Rust

Rust có 4 loại chính:

| Loại              | Cú pháp     | Mục đích                                 |
| ----------------- | ----------- | ---------------------------------------- |
| Line Comment      | `//`        | Ghi chú thông thường                     |
| Block Comment     | `/* ... */` | Ghi chú nhiều dòng                       |
| Outer Doc Comment | `///`       | Tài liệu cho item (hàm, struct, enum...) |
| Inner Doc Comment | `//!`       | Tài liệu cho module hoặc crate           |

---

# 2. Line Comment

Đây là loại phổ biến nhất.

```rust
fn main() {
    // Khởi tạo biến tuổi
    let age = 20;

    println!("{age}");
}
```

Comment sau một dòng:

```rust
let age = 20; // tuổi của sinh viên
```

Compiler sẽ bỏ qua toàn bộ phần sau `//`.

---

# 3. Block Comment

Ví dụ:

```rust
fn main() {
    /*
        Đây là comment
        nhiều dòng.
    */

    println!("Hello");
}
```

---

## Có thể lồng nhau

Đây là điểm thú vị của Rust.

```rust
/*
Outer

    /*
    Inner
    */

End
*/
```

Trong C/C++ điều này không hợp lệ, nhưng Rust hỗ trợ **nested block comments**.

---

# 4. Khi nào nên viết Comment?

Comment nên giải thích:

* **Tại sao** làm như vậy.
* Quyết định thiết kế.
* Thuật toán phức tạp.
* Điều kiện đặc biệt.

Ví dụ tốt:

```rust
// Dùng binary search vì dữ liệu đã được sắp xếp.
```

---

# 5. Khi nào không nên viết?

Ví dụ không tốt:

```rust
// Khai báo biến x
let x = 10;
```

Hoặc:

```rust
// In ra màn hình
println!("{x}");
```

Những comment này chỉ lặp lại điều mà mã nguồn đã thể hiện rõ.

---

# 6. Documentation Comment (`///`)

Đây là loại comment quan trọng nhất khi viết thư viện.

Ví dụ:

```rust
/// Cộng hai số nguyên.
///
/// # Arguments
///
/// * `a` - Số thứ nhất.
/// * `b` - Số thứ hai.
///
/// # Returns
///
/// Tổng của hai số.
fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

---

# 7. Sinh tài liệu

Chạy:

```bash
cargo doc --open
```

Cargo sẽ:

* phân tích tất cả `///`
* tạo HTML
* mở trình duyệt

Bạn sẽ thấy tài liệu giống phong cách của thư viện chuẩn Rust.

---

# 8. Markdown trong Documentation

Rustdoc hỗ trợ Markdown.

```rust
/// # Calculator
///
/// Đây là thư viện tính toán.
///
/// ## Các hàm
///
/// - add
/// - sub
/// - mul
```

Tiêu đề, danh sách, bảng, liên kết... đều được hỗ trợ.

---

# 9. Ví dụ hoàn chỉnh

````rust
/// Trả về bình phương của một số.
///
/// # Example
///
/// ```
/// let value = square(5);
/// assert_eq!(value, 25);
/// ```
fn square(x: i32) -> i32 {
    x * x
}
````

Đây chính là **doctest**.

---

# 10. Doctest

Điểm đặc biệt của Rust:

Ví dụ trong tài liệu **có thể được biên dịch và chạy**.

Ví dụ:

````rust
/// Cộng hai số.
///
/// ```
/// let result = important_project::add(2,3);
/// assert_eq!(result,5);
/// ```
pub fn add(a:i32,b:i32)->i32{
    a+b
}
````

Chạy:

```bash
cargo test
```

Rust sẽ:

* compile ví dụ
* chạy ví dụ
* kiểm tra kết quả

Nếu ví dụ sai:

```rust
assert_eq!(result,6);
```

Test sẽ thất bại.

Đây là lý do tài liệu của Rust thường rất đáng tin cậy.

---

# 11. Documentation cho Struct

```rust
/// Thông tin sinh viên.
pub struct Student {
    /// Họ tên.
    pub name: String,

    /// Tuổi.
    pub age: u8,
}
```

Mỗi trường cũng có thể có tài liệu riêng.

---

# 12. Documentation cho Enum

```rust
/// Trạng thái người dùng.
pub enum Status {
    /// Đang hoạt động.
    Active,

    /// Đã khóa.
    Locked,
}
```

---

# 13. Documentation cho Module

Tạo file:

```text
src/math.rs
```

```rust
//! Module toán học.
//!
//! Module này cung cấp các phép tính cơ bản.

pub fn add(a:i32,b:i32)->i32{
    a+b
}
```

`//!` mô tả toàn bộ module.

---

# 14. Documentation cho Crate

Trong `src/lib.rs`

```rust
//! # Student Library
//!
//! Thư viện quản lý sinh viên.
//!
//! ## Features
//!
//! - Student
//! - Teacher
//! - Course
```

Đây là trang chủ của tài liệu.

---

# 15. Các phần thường gặp

Một hàm chuyên nghiệp thường có:

```rust
/// Mô tả
///
/// # Arguments
///
/// ...
///
/// # Returns
///
/// ...
///
/// # Errors
///
/// ...
///
/// # Panics
///
/// ...
///
/// # Examples
///
/// ...
```

---

# 16. Ví dụ Library hoàn chỉnh

`src/lib.rs`

````rust
//! # Calculator Library
//!
//! Thư viện ví dụ cho buổi học.

/// Cộng hai số.
///
/// # Arguments
///
/// * `a` - Số thứ nhất.
/// * `b` - Số thứ hai.
///
/// # Returns
///
/// Tổng của hai số.
///
/// # Examples
///
/// ```
/// let result = calculator::add(3, 4);
/// assert_eq!(result, 7);
/// ```
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}
````

Chạy:

```bash
cargo doc --open
cargo test
```

---

# 17. Comment TODO và FIXME

Rust không có cú pháp đặc biệt, nhưng cộng đồng thường dùng:

```rust
// TODO: Thêm kiểm tra dữ liệu đầu vào.
```

```rust
// FIXME: Xử lý lỗi chia cho 0.
```

Các IDE thường nhận diện và hiển thị chúng trong danh sách công việc.

---

# 18. Ví dụ thực tế

````rust
/// Kiểm tra xem tuổi có hợp lệ không.
///
/// # Arguments
///
/// * `age` - Tuổi của người dùng.
///
/// # Returns
///
/// `true` nếu tuổi nằm trong khoảng 0..=150.
///
/// # Examples
///
/// ```
/// assert!(is_valid_age(20));
/// assert!(!is_valid_age(200));
/// ```
pub fn is_valid_age(age: u8) -> bool {
    age <= 150
}
````

---

# 19. Mini Project – Math Library

Tạo project:

```bash
cargo new math_lib --lib
```

`src/lib.rs`

```rust
//! # Math Library
//!
//! Thư viện toán học cơ bản.

/// Cộng hai số.
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

/// Trừ hai số.
pub fn sub(a: i32, b: i32) -> i32 {
    a - b
}

/// Nhân hai số.
pub fn mul(a: i32, b: i32) -> i32 {
    a * b
}

/// Chia hai số.
///
/// Trả về `None` nếu mẫu số bằng 0.
pub fn div(a: i32, b: i32) -> Option<i32> {
    if b == 0 {
        None
    } else {
        Some(a / b)
    }
}
```

Sau đó:

```bash
cargo doc --open
cargo test
```

Đây là nền tảng để xây dựng các crate chuyên nghiệp sau này.

---

# Best Practices

## 1. Viết mã rõ ràng trước, comment sau

Không dùng comment để "chữa cháy" cho mã khó hiểu.

Không tốt:

```rust
// Tăng x lên 1
x += 1;
```

Tốt hơn là đặt tên biến và hàm rõ nghĩa.

---

## 2. Viết Documentation cho API công khai

Mọi `pub fn`, `pub struct`, `pub enum`, `pub trait` nên có `///`.

---

## 3. Luôn có ví dụ sử dụng

Ví dụ giúp người dùng hiểu API nhanh hơn và còn được kiểm tra bằng doctest.

---

## 4. Ghi rõ điều kiện lỗi

Nếu hàm có thể:

* panic
* trả về lỗi
* có giới hạn

hãy ghi rõ trong phần `# Panics` hoặc `# Errors`.

---

## 5. Giữ tài liệu đồng bộ với mã nguồn

Sau mỗi thay đổi API, hãy cập nhật documentation và chạy:

```bash
cargo test
cargo doc
```

để đảm bảo ví dụ vẫn đúng.

---

# Những lỗi người mới thường gặp

1. **Dùng `//` thay vì `///`** cho API công khai.
2. **Không cập nhật tài liệu** khi thay đổi hàm.
3. **Viết comment giải thích điều hiển nhiên** thay vì lý do thiết kế.
4. **Không có ví dụ sử dụng**, khiến người dùng phải đọc mã nguồn.
5. **Không chạy doctest**, dẫn đến ví dụ trong tài liệu bị lỗi theo thời gian.

---

# Bài tập thực hành

## Bài 1

Tạo crate thư viện:

```bash
cargo new student_lib --lib
```

Viết tài liệu cho:

* `Student`
* `Teacher`
* `Course`

---

## Bài 2

Viết hàm:

```rust
pub fn max(a: i32, b: i32) -> i32
```

Thêm:

* mô tả
* `# Arguments`
* `# Returns`
* `# Examples`

---

## Bài 3

Tạo module:

```text
math
```

Viết `//!` mô tả module và `///` cho từng hàm.

---

## Bài 4

Viết một ví dụ doctest cho hàm `factorial` và kiểm tra bằng:

```bash
cargo test
```

---

# Tổng kết

Trong buổi học này, bạn đã nắm được:

* Các loại comment trong Rust.
* Khi nào nên và không nên viết comment.
* Cách sử dụng `///` và `//!`.
* Cách tạo tài liệu HTML bằng `cargo doc`.
* Cách viết và chạy **doctest**.
* Quy tắc viết tài liệu cho thư viện chuyên nghiệp.

Đây là kỹ năng rất quan trọng nếu bạn muốn xây dựng crate công khai hoặc tham gia các dự án mã nguồn mở.

## Chuẩn bị cho buổi 7

Ở **Buổi 7 – Formatting Output Deep Dive**, chúng ta sẽ học rất sâu về hệ thống định dạng của Rust:

* Macro `print!`, `println!`, `eprint!`, `eprintln!`
* Placeholder `{}` và cú pháp định dạng nâng cao
* Định dạng số nguyên, số thực, căn lề, độ rộng, độ chính xác
* `Debug` (`{:?}`) và `Display` (`{}`)
* Tự triển khai (`implement`) trait `Display` và `Debug` cho kiểu dữ liệu của riêng mình
* Thực hành xây dựng một CLI hiển thị bảng dữ liệu đẹp mắt, chuẩn đầu ra của các công cụ dòng lệnh chuyên nghiệp.
