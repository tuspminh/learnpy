Xin chào! Bạn đã sẵn sàng cho **Bài 2: Biến và Kiểu dữ liệu** chưa? 🔥

---

## 📚 LÝ THUYẾT CỐT LÕI

### 1. Khai báo biến
```rust
let x = 5;           // immutable (mặc định)
let mut y = 10;      // mutable (có thể thay đổi)
y = 15;              // OK vì có mut
// x = 6;            // LỖI! không thể gán lại
```

### 2. Các kiểu dữ liệu cơ bản

**Số nguyên:**
```rust
let a: i32 = -100;    // số nguyên có dấu 32-bit
let b: u32 = 100;     // số nguyên không dấu 32-bit
let c: i8 = 127;      // 8-bit (-128 đến 127)
let d: isize = 10;    // phụ thuộc kiến trúc (64-bit trên 64-bit OS)
```

**Số thực:**
```rust
let e: f32 = 3.14;    // 32-bit
let f: f64 = 2.718;   // 64-bit (mặc định)
```

**Boolean:**
```rust
let g: bool = true;
let h = false;        // Rust tự suy kiểu
```

**Character:**
```rust
let letter = 'A';     // dùng nháy đơn
let emoji = '😊';      // Unicode 4 bytes
```

### 3. Shadowing (ghi đè biến)
```rust
let x = 5;
let x = x + 1;        // biến x mới "che" biến x cũ
let x = x * 2;        // x = 12
// KHÁC với mut: shadowing cho phép đổi kiểu dữ liệu!
let spaces = "   ";   // string
let spaces = spaces.len(); // số nguyên (3)
```

---

## 💻 THỰC HÀNH NGAY

Tạo dự án mới: `cargo new bai2_bien` và sửa `src/main.rs`:

```rust
fn main() {
    // 1. Khai báo biến immutable
    let ten = "An";
    println!("Tên: {}", ten);
    
    // 2. Khai báo mutable
    let mut tuoi = 25;
    println!("Tuổi: {}", tuoi);
    tuoi = 26;
    println!("Tuổi mới: {}", tuoi);
    
    // 3. Các kiểu số
    let so_nguyen: i32 = -50;
    let so_khong_dau: u32 = 100;
    let so_thuc = 3.14159;  // tự suy là f64
    println!("Số nguyên: {}, không dấu: {}, thực: {}", 
             so_nguyen, so_khong_dau, so_thuc);
    
    // 4. Boolean
    let is_rust_fun = true;
    if is_rust_fun {
        println!("Rust quá thú vị!");
    }
    
    // 5. Shadowing
    let y = 10;
    let y = y + 5;      // y = 15
    let y = y * 2;      // y = 30
    println!("y sau shadowing: {}", y);
    
    // 6. Shadowing đổi kiểu
    let message = "Hello";
    let message = message.len();  // từ &str thành usize
    println!("Độ dài: {}", message);
}
```

---

## 📝 BÀI TẬP (PHẢI LÀM)

**Mở dự án của bạn và hoàn thành:**

```rust
// Bài 1: Tính chu vi và diện tích hình chữ nhật
// Cho chiều_dài = 12.5, chiều_rộng = 8.2
// In ra: "Chu vi = X, Diện tích = Y"

// Bài 2: Chuyển đổi độ C sang độ F
// Công thức: F = C * 9/5 + 32
// Với C = 30, in ra "30°C = 86°F"

// Bài 3: Shadowing
// Tạo biến number = 100
// Shadow thành number = "Một trăm"
// In ra cả hai giá trị ở các bước

// Bài 4: Kiểm tra số chẵn lẻ
// Cho x = 7
// In ra "x là số chẵn" hoặc "x là số lẻ"
// (Gợi ý: dùng if và phép toán %)
```

---

## 🎯 LƯU Ý QUAN TRỌNG

| Điểm | Giải thích |
|------|-----------|
| **`mut` vs Shadowing** | `mut` thay đổi giá trị cùng kiểu; Shadowing đổi được cả kiểu |
| **Số nguyên mặc định** | Nếu không ghi kiểu, Rust chọn `i32` |
| **Số thực mặc định** | Nếu không ghi kiểu, Rust chọn `f64` |
| **println! với nhiều biến** | `println!("{} {} {}", a, b, c)` |
| **Kiểu chữ** | `"text"` là String/str; `'A'` là char |

---

## ❌ LỖI THƯỜNG GẶP

```rust
let x = 5;
x = 6;  // LỖI! quên mut
// Sửa: let mut x = 5;

let mut y = 10;
let y = "hello";  // LỖI! mut không đổi được kiểu
// Sửa: dùng shadowing: let y = "hello";
```

---

## ✅ CHECKLIST BÀI 2

- [ ] Hiểu immutable vs mutable
- [ ] Biết các kiểu: i32, u32, f64, bool, char
- [ ] Hiểu shadowing
- [ ] Làm xong 4 bài tập
- [ ] Chạy `cargo check` và sửa lỗi (nếu có)

---

**Chạy xong bài tập, paste code của bạn vào đây để tôi review!**  
Hoặc hỏi ngay nếu có lỗi/gì không hiểu.

Sẵn sàng cho **Bài 3: Hàm và Control Flow**? 🚀