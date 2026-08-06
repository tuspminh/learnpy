# Giáo trình Rust Professional 2026

# Giai đoạn 1 — Rust Foundation

# Buổi 2 — Cargo Deep Dive

> **Mục tiêu buổi học**

Sau buổi này bạn sẽ:

* Hiểu Cargo là gì và tại sao Rust cần Cargo.
* Biết cấu trúc của một Rust Project.
* Thành thạo các lệnh Cargo quan trọng.
* Hiểu Package, Crate, Target.
* Hiểu Cargo.toml.
* Quản lý Dependency.
* Biết Debug và Release Build.
* Có thể tạo CLI Project hoàn chỉnh.

---

# 1. Cargo là gì?

Cargo là **Build System + Package Manager** chính thức của Rust.

Nếu Python có:

* pip
* poetry
* hatch

Java có:

* Maven
* Gradle

NodeJS có:

* npm
* yarn
* pnpm

thì Rust có:

> Cargo

Cargo giúp:

* tạo project
* build project
* download package
* test
* benchmark
* format
* lint
* publish
* tạo document

Nói cách khác:

> **90% thời gian làm việc với Rust là dùng Cargo.**

---

# 2. Cargo làm được gì?

Ví dụ:

Tạo project

```bash
cargo new hello
```

Build

```bash
cargo build
```

Run

```bash
cargo run
```

Test

```bash
cargo test
```

Document

```bash
cargo doc
```

Publish

```bash
cargo publish
```

---

# 3. Tạo Project

```bash
cargo new hello_cli
```

Cấu trúc

```text
hello_cli
│
├── Cargo.toml
├── Cargo.lock
│
├── src
│   └── main.rs
│
└── target
```

Lưu ý:

Lần đầu chỉ có

```text
hello_cli
│
├── Cargo.toml
└── src
    └── main.rs
```

Sau khi build mới xuất hiện

```
target/
Cargo.lock
```

---

# 4. Cargo.toml

Ví dụ

```toml
[package]
name = "hello_cli"
version = "0.1.0"
edition = "2024"

[dependencies]
```

Ý nghĩa

```
[package]
```

Thông tin package.

```
name
```

Tên project.

```
version
```

Phiên bản.

```
edition
```

Phiên bản Rust Edition.

Hiện nay nên dùng

```
2024
```

---

# 5. Dependencies

Ví dụ

```toml
[dependencies]
rand = "0.9"
```

Cargo sẽ tự download.

Chạy

```
cargo build
```

Bạn sẽ thấy

```
Downloading...
Compiling...
Finished...
```

---

# 6. Sử dụng dependency

main.rs

```rust
use rand::Rng;

fn main() {
    let mut rng = rand::rng();

    let n = rng.random_range(1..=100);

    println!("{n}");
}
```

Chạy

```
cargo run
```

Mỗi lần sẽ in số khác nhau.

---

# 7. Cargo.lock

Rất nhiều người mới học không hiểu file này.

Cargo.toml

```
rand = "0.9"
```

Có nghĩa

```
0.9.x
```

Cargo.lock

```
rand 0.9.2
```

Nó khóa đúng version.

Đảm bảo

```
Máy A

=

Máy B

=

Server
```

đều build giống nhau.

---

# 8. Cargo Build

```
cargo build
```

Sinh ra

```
target/debug
```

Ví dụ

```
target/debug/hello_cli
```

---

# 9. Cargo Run

Thực chất

```
cargo run
```

=

```
cargo build

+

chạy executable
```

---

# 10. Cargo Check

Đây là lệnh cực kỳ hay.

```
cargo check
```

Cargo chỉ

* compile
* kiểm tra lỗi

KHÔNG tạo executable.

Nhanh hơn rất nhiều.

Trong lúc code

```
cargo check
```

được dùng rất nhiều.

---

# 11. Cargo Test

Ví dụ

```rust
fn add(a:i32,b:i32)->i32{
    a+b
}

#[cfg(test)]
mod tests {

    use super::*;

    #[test]
    fn test_add(){
        assert_eq!(add(2,3),5);
    }

}
```

Chạy

```
cargo test
```

Kết quả

```
running 1 test

ok
```

---

# 12. Cargo Clean

Xóa thư mục build

```
cargo clean
```

Target sẽ bị xóa.

---

# 13. Cargo Doc

Sinh document.

```
cargo doc --open
```

Cargo mở browser.

---

# 14. Cargo fmt

Format code.

```
cargo fmt
```

Ví dụ

Trước

```rust
fn main(){println!("hello");}
```

Sau

```rust
fn main() {
    println!("hello");
}
```

---

# 15. Cargo clippy

Kiểm tra code.

```
cargo clippy
```

Ví dụ

```rust
let x = true;

if x == true {

}
```

Clippy sẽ cảnh báo.

Nên viết

```rust
if x {

}
```

---

# 16. Cargo Tree

Cài

```
cargo install cargo-tree
```

Xem dependency

```
cargo tree
```

Ví dụ

```
hello

├── rand

├── getrandom

├── libc

...
```

---

# 17. Cargo Update

```
cargo update
```

Update Cargo.lock.

---

# 18. Debug vs Release

Thông thường

```
cargo run
```

chạy

```
Debug
```

Nếu muốn tối ưu

```
cargo run --release
```

Cargo build

```
target/release
```

Executable nhanh hơn rất nhiều.

---

# 19. Cấu trúc Project

```
hello_cli
│
├── Cargo.toml
│
├── Cargo.lock
│
├── src
│    └── main.rs
│
├── target
│
└── .gitignore
```

---

# 20. Ví dụ hoàn chỉnh

Tạo project

```
cargo new greeting
```

Thêm dependency

```toml
[dependencies]
rand = "0.9"
```

main.rs

```rust
use rand::Rng;

fn main() {
    println!("==== Greeting App ====");

    let names = [
        "Alice",
        "Bob",
        "Charlie",
        "David",
        "Emma",
    ];

    let mut rng = rand::rng();

    let idx = rng.random_range(0..names.len());

    println!("Hello {}", names[idx]);
}
```

Chạy

```
cargo run
```

Ví dụ

```
==== Greeting App ====

Hello Bob
```

Lần sau

```
==== Greeting App ====

Hello Emma
```

---

# 21. Thực hành

## Bài 1

Tạo project

```
student_info
```

In

```
Tên
Tuổi
Lớp
```

---

## Bài 2

Thêm `rand`.

Sinh điểm ngẫu nhiên

```
0..100
```

Ví dụ

```
Điểm: 78
```

---

## Bài 3

Tạo chương trình tung xúc xắc.

Ví dụ

```
🎲 = 5
```

---

## Bài 4

Sinh ngẫu nhiên

```
Đỏ
Xanh
Vàng
Đen
```

---

# Best Practices

* Luôn dùng `cargo check` trong quá trình phát triển để nhận phản hồi nhanh từ trình biên dịch.
* Chạy `cargo fmt` trước khi commit mã nguồn để giữ định dạng thống nhất.
* Chạy `cargo clippy` thường xuyên để phát hiện các vấn đề về phong cách và hiệu năng.
* Chỉ dùng `cargo run --release` hoặc `cargo build --release` khi cần đo hiệu năng hoặc phát hành.
* Không chỉnh sửa `Cargo.lock` bằng tay; hãy để Cargo quản lý.

---

# Những lỗi người mới thường gặp

1. **Xóa `Cargo.lock` không cần thiết**: Với ứng dụng, nên giữ file này trong hệ thống quản lý mã nguồn để đảm bảo mọi môi trường dùng cùng phiên bản dependency.
2. **Nhầm giữa `cargo build` và `cargo run`**: `cargo run` sẽ tự build nếu cần rồi mới chạy chương trình.
3. **Lạm dụng `cargo clean`**: Chỉ dùng khi cần giải phóng dung lượng hoặc xử lý lỗi build hiếm gặp.
4. **Không dùng `cargo check`**: Điều này làm chậm vòng lặp phát triển vì mỗi lần đều tạo file thực thi.

---

# Tổng kết

Trong buổi này bạn đã nắm được:

* Vai trò của Cargo trong hệ sinh thái Rust.
* Cấu trúc chuẩn của một dự án Rust.
* Ý nghĩa của `Cargo.toml` và `Cargo.lock`.
* Các lệnh Cargo quan trọng: `new`, `build`, `run`, `check`, `test`, `fmt`, `clippy`, `doc`, `clean`, `update`.
* Sự khác nhau giữa chế độ **Debug** và **Release**.
* Cách thêm và sử dụng dependency từ crates.io.

## Buổi tiếp theo

Ở **Buổi 3 – Variables & Mutability**, chúng ta sẽ đi sâu vào hệ thống biến của Rust, bao gồm:

* `let` và `let mut`
* Tính bất biến (immutability)
* Shadowing
* Quy tắc đặt tên
* Kiểu dữ liệu suy luận (type inference)
* Phạm vi của biến (scope)
* Hằng số (`const`) và sự khác biệt với biến
* Nhiều ví dụ minh họa và bài tập thực hành để hiểu tư duy thiết kế của Rust trước khi bước vào Ownership.
