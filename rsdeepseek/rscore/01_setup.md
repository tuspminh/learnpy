Tuyệt vời! Mới bắt đầu là cơ hội để học đúng ngay từ đầu. Rust sẽ "uốn nắn" tư duy lập trình của bạn rất tốt.

Chúng ta học theo **phương pháp "học qua làm"**, mỗi buổi chỉ **45-60 phút**.

---

## BÀI 1: CÀI ĐẶT & "XIN CHÀO"

### 1. Cài Rust (trên Linux/Mac/WSL2):
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```
Trên Windows: tải `rustup-init.exe` từ rustup.rs

### 2. Kiểm tra:
```bash
rustc --version   # phiên bản compiler
cargo --version   # phiên bản trình quản lý dự án
```

### 3. Tạo dự án đầu tiên:
```bash
cargo new hello_rust
cd hello_rust
```

### 4. Mở file `src/main.rs`, bạn sẽ thấy:
```rust
fn main() {
    println!("Hello, world!");
}
```

### 5. Chạy:
```bash
cargo run   # compile + chạy luôn
```

---

## 🧠 HIỂU NGAY 3 ĐIỀU CỐT LÕI

**① `fn main()`** - điểm bắt đầu của mọi chương trình Rust

**② `println!`** - có dấu `!` là macro (sẽ học sau), dùng để in ra màn hình

**③ `cargo`** - vừa là compiler, vừa quản lý thư viện, vừa chạy test

---

## 📝 BÀI TẬP BẮT BUỘC

**Trong file `main.rs`, hãy làm:**

```rust
// 1. In ra: "Tôi đang học Rust!"
// 2. Tạo biến x = 5, y = 10, in ra "Tổng = 15"
// 3. Tạo biến z = x + y, in ra với format: "Giá trị z là: {z}"
// 4. In ra nhiều dòng: 
//    Dòng 1
//    Dòng 2
//    Dòng 3
```

**Gợi ý:** dùng `println!("... {}", ten_bien)` để in biến

---

## ⚠️ LƯU Ý VÀNG

- **Mỗi câu lệnh kết thúc bằng `;`** - nếu quên sẽ báo lỗi
- **Tên biến phải là `snake_case`** - ví dụ: `my_variable`, không dùng `myVariable`
- **Chạy `cargo check`** để kiểm tra lỗi nhanh, không cần compile hết
- **Sửa lỗi nhờ compiler** - Rust báo lỗi rất chi tiết, đọc kỹ là biết sửa

---

## 📖 ĐỌC THÊM CHO BÀI 1

Đọc [Chương 1-2 của Rust Book](https://doc.rust-lang.org/book/ch01-00-getting-started.html) (khoảng 15 phút)

---

## ✅ CHECKLIST HOÀN THÀNH BÀI 1

- [ ] Cài đặt Rust thành công
- [ ] Chạy được "Hello, world!"
- [ ] Hiểu cách dùng `println!`
- [ ] Làm xong 4 bài tập trên
- [ ] Đã chạy `cargo check` ít nhất 1 lần

---

**Sau khi làm xong, comment code của bạn xuống đây để tôi kiểm tra.**

Hoặc nếu gặp lỗi gì, paste nguyên lỗi vào tôi sẽ hướng dẫn sửa từng bước!

Sẵn sàng cho **Bài 2 - Biến và Kiểu dữ liệu**? 🚀