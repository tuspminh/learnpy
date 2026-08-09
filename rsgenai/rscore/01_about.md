Chào bạn! Rất vui được chào đón bạn bước vào thế giới của Rust. Với tư cách là một lập trình viên Rust, tôi sẽ đồng hành cùng bạn trong hành trình này.

Rust là một ngôn ngữ tuyệt vời: nó cung cấp hiệu năng mạnh mẽ ngang ngửa C/C++ nhưng lại đảm bảo sự an toàn bộ nhớ (memory safety) tuyệt đối mà không cần dùng đến bộ thu gom rác (Garbage Collector). Tuy nhiên, tôi cũng sẽ nói thật với bạn: Rust có một "đường cong học tập" (learning curve) khá dốc, chủ yếu đến từ khái niệm quản lý bộ nhớ độc quyền của nó. Nhưng đừng lo lắng, chúng ta sẽ đi từng bước một, học đến đâu chắc đến đó bằng các ví dụ thực tế.

Dưới đây là lộ trình tổng quan mà chúng ta sẽ đi qua.

## Lộ trình học Rust (Từ Cơ bản đến Chuyên sâu)

* **Phần 1: Nhập môn cơ bản** (Cài đặt, Cargo, Biến, Kiểu dữ liệu, Hàm, Control Flow).
* **Phần 2: Trái tim của Rust** (Ownership, Borrowing, Lifetimes - *Đây là phần quan trọng và khó nhất*).
* **Phần 3: Cấu trúc & Tổ chức mã** (Structs, Enums, Pattern Matching, Modules, Collections).
* **Phần 4: Tư duy nâng cao** (Error Handling, Generics, Traits, Closures, Iterators).
* **Phần 5: Chuyên sâu & Thực chiến** (Smart Pointers, Concurrency/Đa luồng, Macros, Unsafe Rust, Viết dự án thực tế).

---

Hôm nay, chúng ta sẽ bắt đầu với **Bài 1**, tạo nền tảng vững chắc nhất cho bạn.

## Bài 1: Cài đặt, Cargo và "Hello, Rust!"

### 1. Cài đặt Rust

Cách chuẩn và an toàn nhất để cài đặt Rust là sử dụng công cụ có tên là `rustup`.

* **Trên Linux/macOS:** Mở terminal và chạy lệnh sau:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

```


* **Trên Windows:** Bạn truy cập trang chủ `rustup.rs`, tải file `rustup-init.exe` về và chạy. (Lưu ý: Windows yêu cầu phải có C++ Build Tools, trình cài đặt sẽ hướng dẫn bạn nếu máy bạn chưa có).

Sau khi cài xong, bạn mở một Terminal/Command Prompt mới và kiểm tra xem Rust đã sẵn sàng chưa bằng lệnh:

```bash
rustc --version
cargo --version

```

Nếu màn hình in ra phiên bản của Rust, chúc mừng bạn đã cài đặt thành công!

### 2. Cargo là gì?

Trong hệ sinh thái Rust, **Cargo** đóng vai trò cực kỳ quan trọng. Nó vừa là trình quản lý gói (package manager - giống `npm` của Node.js hay `pip` của Python), vừa là công cụ build dự án. Bạn sẽ dùng Cargo cho 99% các thao tác quản lý dự án thay vì gọi trực tiếp trình biên dịch `rustc`.

### 3. Chương trình đầu tiên: Hello, Rust!

Thay vì tạo file thủ công, chúng ta sẽ dùng Cargo để khởi tạo một dự án chuẩn mực.

**Bước 1:** Mở terminal và chạy lệnh:

```bash
cargo new hello_rust

```

Lệnh này tạo ra một thư mục tên là `hello_rust`.

**Bước 2:** Di chuyển vào thư mục dự án:

```bash
cd hello_rust

```

Bạn sẽ thấy cấu trúc thư mục như sau:

* `Cargo.toml`: File cấu hình của dự án (chứa thông tin dự án và các thư viện phụ thuộc - dependencies).
* `src/main.rs`: File mã nguồn chính của bạn.

**Bước 3:** Mở file `src/main.rs` bằng bất kỳ Text Editor nào (VS Code là một lựa chọn tuyệt vời với extension `rust-analyzer`). Bạn sẽ thấy Cargo đã viết sẵn đoạn code này:

```rust
fn main() {
    println!("Hello, world!");
}

```

**Giải thích chi tiết đoạn code:**

* `fn`: Từ khóa dùng để khai báo một hàm (function).
* `main()`: Hàm bắt buộc phải có trong mọi chương trình Rust có thể chạy được (executable). Đây là điểm bắt đầu (entry point) khi chương trình khởi chạy.
* `println!`: Dùng để in một chuỗi ra màn hình. **Lưu ý dấu `!**`: Trong Rust, khi bạn thấy dấu chấm than `!`, điều đó có nghĩa `println` là một **Macro**, không phải là một hàm (function) thông thường. (Chúng ta sẽ tìm hiểu Macro chuyên sâu ở Phần 5, hiện tại bạn chỉ cần nhớ cú pháp này để in ra màn hình).
* Dấu chấm phẩy `;` dùng để kết thúc một câu lệnh.

**Bước 4:** Chạy chương trình
Vẫn trong terminal tại thư mục `hello_rust`, bạn gõ:

```bash
cargo run

```

Cargo sẽ tự động biên dịch (compile) mã nguồn của bạn thành file thực thi và chạy nó. Bạn sẽ thấy dòng chữ `Hello, world!` hiện ra trên terminal.

---

Bạn đã cài đặt thành công Rust trên máy của mình chưa, hay bạn muốn chúng ta tiến thẳng sang **Bài 2: Biến (Variables), Tính bất biến (Mutability) và Kiểu dữ liệu** luôn?