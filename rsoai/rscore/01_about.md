
# Buổi 1 — Rust là gì? Cài đặt môi trường

## Mục tiêu

Sau buổi này bạn sẽ:

* Biết Rust sinh ra để giải quyết vấn đề gì.
* Hiểu tại sao Rust nhanh.
* Hiểu compiler hoạt động như thế nào.
* Cài đặt môi trường.
* Chạy chương trình Rust đầu tiên.

---

# 1. Rust là gì?

Rust là ngôn ngữ lập trình hệ thống (Systems Programming Language) được thiết kế để:

* Nhanh như C/C++
* An toàn bộ nhớ (Memory Safety)
* Không cần Garbage Collector
* Hỗ trợ lập trình đồng thời (Concurrency) an toàn

Rust đạt được điều này nhờ ba khái niệm cốt lõi:

* Ownership
* Borrowing
* Lifetime

Đây cũng là ba chủ đề sẽ được học rất sâu trong giáo trình.

---

# 2. Rust dùng để làm gì?

Rust phù hợp cho nhiều lĩnh vực:

* CLI Tool
* Web Server
* HTTP Client
* Game Engine
* Operating System
* Embedded
* Database
* Browser
* Blockchain
* AI Runtime
* Network Programming

---

# 3. Tại sao Rust nhanh?

Rust biên dịch trực tiếp xuống mã máy (native code), không có máy ảo như Java hay Python.

Quá trình:

```text
Source Code (.rs)
        │
        ▼
Rust Compiler (rustc)
        │
        ▼
Machine Code
        │
        ▼
Executable
```

Điều này giúp chương trình đạt hiệu năng rất cao.

---

# 4. Cài đặt Rust

Trên Windows, macOS hoặc Linux, cách chính thức là dùng `rustup`:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

Sau khi cài đặt, kiểm tra:

```bash
rustc --version
cargo --version
```

Ví dụ kết quả:

```text
rustc 1.xx.x
cargo 1.xx.x
```

---

# 5. Tạo dự án đầu tiên

```bash
cargo new hello_rust
```

Di chuyển vào thư mục:

```bash
cd hello_rust
```

Cấu trúc:

```text
hello_rust/
│
├── Cargo.toml
└── src/
    └── main.rs
```

---

# 6. Chương trình đầu tiên

Mở `src/main.rs`:

```rust
fn main() {
    println!("Hello, Rust!");
}
```

Chạy:

```bash
cargo run
```

Kết quả:

```text
Hello, Rust!
```

---

# 7. Giải thích từng dòng

```rust
fn main() {
```

* `fn`: khai báo hàm.
* `main`: điểm bắt đầu của chương trình.
* `{}`: thân hàm.

```rust
println!("Hello, Rust!");
```

* `println!` là một **macro** (không phải hàm).
* Dấu `!` cho biết đây là macro.
* In chuỗi và tự động xuống dòng.

---

# 8. Thử thay đổi chương trình

```rust
fn main() {
    println!("Xin chào!");
    println!("Tôi đang học Rust.");
    println!("Ngày đầu tiên.");
}
```

Kết quả:

```text
Xin chào!
Tôi đang học Rust.
Ngày đầu tiên.
```

---

# 9. Bài tập thực hành

1. Tạo project `hello_rust`.
2. Chạy thành công bằng `cargo run`.
3. In ra:

   * Họ tên
   * Tuổi
   * Nghề nghiệp
4. Thêm một dòng:

   * `"Tôi sẽ chinh phục Rust!"`

Ví dụ:

```rust
fn main() {
    println!("Họ tên: Nguyễn Văn A");
    println!("Tuổi: 25");
    println!("Nghề nghiệp: Lập trình viên");
    println!("Tôi sẽ chinh phục Rust!");
}
```

---

# Tổng kết

Trong buổi đầu tiên, bạn đã:

* Hiểu Rust là gì.
* Biết các lĩnh vực ứng dụng của Rust.
* Cài đặt môi trường và Cargo.
* Tạo dự án đầu tiên.
* Chạy chương trình "Hello, Rust!".
* Hiểu cấu trúc cơ bản của một chương trình Rust.

---

### Buổi tiếp theo

Ở **Buổi 2**, chúng ta sẽ học **Cargo Deep Dive**. Không chỉ biết `cargo run`, mà sẽ tìm hiểu chi tiết:

* Kiến trúc của Cargo.
* Cấu trúc `Cargo.toml`.
* Package, Crate và Workspace.
* Các lệnh quan trọng (`build`, `check`, `test`, `doc`, `fmt`, `clippy`, `clean`, `install`, `update`,...).
* Quản lý dependency và phiên bản.
* Tạo thư viện (`lib`) và binary.
* Thực hành xây dựng một CLI nhỏ để hiểu toàn bộ quy trình làm việc với Cargo. Đây là nền tảng quan trọng trước khi đi sâu vào Ownership và các chủ đề nâng cao.
