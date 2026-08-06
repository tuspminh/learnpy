Chào mừng đến **Bài 5: References & Borrowing**! 🔄

Đây là bài học GIÚP BẠN THOÁT KHỎI ownership một cách an toàn. Thay vì di chuyển ownership, bạn có thể **mượn** dữ liệu.

---

## 📚 LÝ THUYẾT CỐT LÕI

### 1. References (Tham chiếu)

**Tham chiếu cho phép bạn truy cập dữ liệu mà KHÔNG lấy ownership.**

```rust
fn main() {
    let s1 = String::from("hello");
    let len = calculate_length(&s1);  // &s1 là reference
    println!("'{}' có độ dài {}", s1, len);  // s1 vẫn hợp lệ!
}

fn calculate_length(s: &String) -> usize {  // s là reference
    s.len()
}  // s không bị drop vì không có ownership
```

### 2. Mutable References (Tham chiếu có thể thay đổi)

**Muốn sửa dữ liệu qua reference, dùng `&mut`:**

```rust
fn main() {
    let mut s = String::from("hello");
    change(&mut s);
    println!("{}", s);  // "hello, world"
}

fn change(s: &mut String) {
    s.push_str(", world");  // sửa được vì là &mut
}
```

### 3. Quy tắc QUAN TRỌNG của Borrowing

**Rule 1:** Trong cùng một scope, bạn KHÔNG thể có cả mutable reference và immutable reference cùng lúc.

```rust
let mut s = String::from("hello");

let r1 = &s;      // immutable reference
let r2 = &s;      // immutable reference (OK)
let r3 = &mut s;  // LỖI! không thể có immutable + mutable cùng lúc

println!("{}, {}, {}", r1, r2, r3);
```

**Rule 2:** Nếu có mutable reference, không thể có bất kỳ reference nào khác.

```rust
let mut s = String::from("hello");

let r1 = &mut s;
// let r2 = &mut s;  // LỖI! chỉ được 1 mutable reference
// let r3 = &s;      // LỖI! không thể có immutable

println!("{}", r1);
```

**Rule 3:** References phải luôn hợp lệ (không có dangling references).

```rust
fn dangle() -> &String {  // LỖI!
    let s = String::from("hello");
    &s  // trả về reference của s
}  // s bị drop, reference trở thành dangling
```

### 4. Reference Scopes

**References có scope riêng, có thể tách biệt:**

```rust
let mut s = String::from("hello");

let r1 = &s;
let r2 = &s;
println!("{} và {}", r1, r2);  // r1, r2 không dùng nữa sau đây

let r3 = &mut s;  // OK! vì r1, r2 đã hết scope
println!("{}", r3);
```

---

## 💻 THỰC HÀNH NGAY

**Tạo dự án: `cargo new bai5_borrowing`**

```rust
fn main() {
    // 1. Immutable reference
    let s1 = String::from("Rust");
    let len = get_length(&s1);
    println!("'{}' dài {} ký tự", s1, len);  // s1 vẫn dùng được!
    
    // 2. Mutable reference
    let mut s2 = String::from("Hello");
    add_world(&mut s2);
    println!("{}", s2);  // "Hello World"
    
    // 3. Nhiều immutable references
    let s3 = String::from("learning");
    let r1 = &s3;
    let r2 = &s3;
    println!("r1: {}, r2: {}", r1, r2);  // OK!
    
    // 4. Lỗi: không thể có mutable + immutable
    let mut s4 = String::from("error");
    let r3 = &s4;
    // let r4 = &mut s4;  // Bỏ comment để thấy lỗi!
    println!("{}", r3);
    
    // 5. Scope của references
    let mut s5 = String::from("hello");
    {
        let r5 = &mut s5;  // mutable reference trong scope nhỏ
        r5.push_str("!!!");
    }  // r5 hết scope ở đây
    let r6 = &s5;  // OK! r5 không còn
    println!("{}", r6);
    
    // 6. Fix dangling reference
    let s6 = no_dangle();
    println!("{}", s6);
}

fn get_length(s: &String) -> usize {
    s.len()
}  // s là reference, không bị drop

fn add_world(s: &mut String) {
    s.push_str(" World");
}

fn no_dangle() -> String {
    let s = String::from("safe");
    s  // trả về ownership, không phải reference
}
```

---

## 📝 BÀI TẬP BẮT BUỘC

```rust
// Bài 1: Sửa lỗi
/*
fn main() {
    let mut s = String::from("hello");
    let r1 = &s;
    let r2 = &mut s;
    println!("{} {}", r1, r2);
}
*/

// Bài 2: Viết hàm first_word(s: &String) -> &str
// Trả về từ đầu tiên trong chuỗi (dùng &str)
// Gợi ý: dùng s.chars() và đếm vị trí khoảng trắng

// Bài 3: Viết hàm reverse(s: &mut String) đảo ngược chuỗi
// Ví dụ: "hello" -> "olleh"
// Gợi ý: dùng s.chars().rev().collect()

// Bài 4: Tạo struct Calculator với field value: i32
// Implement:
// - new(v: i32) -> Self
// - add(&mut self, n: i32) thay đổi value
// - get_value(&self) -> i32 trả về value

// Bài 5: Cho array numbers = [1, 2, 3, 4, 5]
// Viết hàm sum(slice: &[i32]) -> i32 tính tổng
// Truyền &numbers vào (slice reference)
```

---

## 🎯 LƯU Ý QUAN TRỌNG

| Khái niệm | Cú pháp | Tính chất |
|-----------|---------|-----------|
| **Immutable reference** | `&T` | Đọc được, không sửa |
| **Mutable reference** | `&mut T` | Đọc và sửa được |
| **Borrowing rule 1** | - | 1 mutable HOẶC nhiều immutable |
| **Borrowing rule 2** | - | References phải luôn hợp lệ |

---

## ⚡ MẸO GHI NHỚ

**Khi nào dùng reference?**

✅ Nên dùng:
- Hàm chỉ đọc dữ liệu → `&T`
- Hàm cần sửa dữ liệu → `&mut T`
- Tránh copy dữ liệu lớn

❌ Không dùng:
- Khi cần sở hữu dữ liệu (ví dụ: lưu vào struct)
- Khi dữ liệu sống ngắn hơn reference (dangling)

---

## 🔥 BÀI TẬP NÂNG CAO

```rust
// Viết hàm reverse_words(s: &mut String)
// Input: "hello world rust" -> Output: "rust world hello"
// Yêu cầu: 
// - Dùng &mut String
// - Không tạo String mới (chỉ sửa trên s)
// - Gợi ý: split, collect, reverse, clear, push_str
```

---

## ✅ CHECKLIST BÀI 5

- [ ] Phân biệt `&T` và `&mut T`
- [ ] Hiểu 2 rules của borrowing
- [ ] Biết scope của references
- [ ] Tránh được dangling references
- [ ] Làm xong 5 bài tập cơ bản
- [ ] Thử bài tập nâng cao

---

**Hoàn thành bài tập, chia sẻ code để tôi review!**

Bài tiếp theo: **Bài 6 - Struct và Method** - xây dựng kiểu dữ liệu tùy chỉnh. Bạn đã sẵn sàng? 🏗️