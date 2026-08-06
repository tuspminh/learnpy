Chào mừng đến **Bài 4: Ownership - TRÁI TIM của Rust**! ❤️

Đây là bài học **QUAN TRỌNG NHẤT** trong toàn bộ lộ trình. Hiểu được ownership, bạn sẽ hiểu được Rust.

---

## 🧠 TƯ DUY NỀN TẢNG

**Rust KHÔNG có garbage collector** như Java/Python. Thay vào đó, Rust dùng hệ thống **ownership** để quản lý bộ nhớ tại compile time.

**3 quy tắc VÀNG:**

1. Mỗi giá trị trong Rust có một **owner** (biến sở hữu)
2. Tại một thời điểm, chỉ có **một owner** duy nhất
3. Khi owner ra khỏi scope, giá trị sẽ bị **drop** (giải phóng bộ nhớ)

---

## 📚 LÝ THUYẾT CỐT LÕI

### 1. Move semantics (Chuyển quyền sở hữu)

```rust
let s1 = String::from("hello");
let s2 = s1;  // s1 bị MOVE vào s2

// println!("{}", s1);  // LỖI! s1 không còn hợp lệ
println!("{}", s2);     // OK: "hello"
```

**GIẢI THÍCH:** Khi gán `s1` cho `s2`, Rust không copy dữ liệu mà **di chuyển** quyền sở hữu. `s1` không còn hợp lệ để tránh double-free.

### 2. Clone (Copy sâu)

```rust
let s1 = String::from("hello");
let s2 = s1.clone();  // Copy DEEP, cả hai đều hợp lệ

println!("s1 = {}, s2 = {}", s1, s2);  // OK!
```

### 3. Copy trait (Kiểu dữ liệu đơn giản)

**Các kiểu nằm trên stack** (như số nguyên, bool) tự động copy:

```rust
let x = 5;
let y = x;     // Copy, không move

println!("x = {}, y = {}", x, y);  // OK!
```

**Các kiểu có Copy trait:** integer, float, bool, char, tuple (nếu các phần tử đều Copy)

### 4. Ownership và hàm

```rust
fn main() {
    let s = String::from("hello");
    takes_ownership(s);  // s bị MOVE vào hàm
    
    // println!("{}", s);  // LỖI!
    
    let x = 5;
    makes_copy(x);       // x bị COPY (vì i32 có Copy)
    println!("{}", x);   // OK!
}

fn takes_ownership(some_string: String) {
    println!("{}", some_string);
}  // some_string bị drop

fn makes_copy(some_integer: i32) {
    println!("{}", some_integer);
}  // không gì xảy ra
```

### 5. Return values và ownership

```rust
fn main() {
    let s1 = gives_ownership();      // move vào s1
    let s2 = String::from("hello");
    let s3 = takes_and_gives_back(s2);  // s2 move, s3 nhận
    
    println!("{}", s1);  // OK
    // println!("{}", s2);  // LỖI!
    println!("{}", s3);  // OK
}

fn gives_ownership() -> String {
    let some_string = String::from("yours");
    some_string  // move ra ngoài
}

fn takes_and_gives_back(a_string: String) -> String {
    a_string  // move vào và ra
}
```

---

## 💻 THỰC HÀNH NGAY

**Tạo dự án mới: `cargo new bai4_ownership`**

```rust
fn main() {
    // 1. Move
    let s1 = String::from("Rust");
    let s2 = s1;
    println!("s2: {}", s2);
    // println!("s1: {}", s1); // Bỏ comment để thấy lỗi!
    
    // 2. Clone
    let s3 = String::from("Hello");
    let s4 = s3.clone();
    println!("s3: {}, s4: {}", s3, s4);  // Cả 2 OK!
    
    // 3. Copy (integer)
    let a = 10;
    let b = a;
    println!("a: {}, b: {}", a, b);  // Cả 2 OK!
    
    // 4. Hàm với ownership
    let my_string = String::from("world");
    take_ownership(my_string);
    // println!("{}", my_string); // LỖI!
    
    let my_number = 100;
    make_copy(my_number);
    println!("{}", my_number);  // OK!
    
    // 5. Return ownership
    let s = give_back();
    println!("{}", s);
    
    let s5 = String::from("take and give");
    let s6 = take_and_give_back(s5);
    println!("{}", s6);
    // println!("{}", s5); // LỖI!
}

fn take_ownership(s: String) {
    println!("Nhận: {}", s);
} // s bị drop ở đây

fn make_copy(n: i32) {
    println!("Copy: {}", n);
} // n là copy nên không sao

fn give_back() -> String {
    let s = String::from("Returned");
    s  // move ra ngoài
}

fn take_and_give_back(s: String) -> String {
    println!("Nhận: {}", s);
    s  // trả lại ownership
}
```

---

## 📝 BÀI TẬP BẮT BUỘC

```rust
// Bài 1: Dự đoán kết quả (không chạy code!)
// let s = String::from("hello");
// let t = s;
// let u = t.clone();
// println!("{}", s); // Hỏi: In ra gì? Lỗi hay "hello"?

// Bài 2: Giải thích lỗi và sửa
/*
fn main() {
    let s = String::from("rust");
    print_string(s);
    println!("s: {}", s);  // Lỗi ở đây
}

fn print_string(s: String) {
    println!("{}", s);
}
*/

// Bài 3: Viết hàm calculate_length(s: String) -> (String, usize)
// Trả về tuple (String, usize) với String là chuỗi gốc và usize là độ dài
// KHÔNG dùng clone()

// Bài 4: Tạo hàm first_word(s: &String) -> &str (sẽ học ở bài 5)
// Nhưng giờ hãy viết hàm lấy từ đầu tiên bằng cách:
// - Dùng s.chars() và vòng lặp
// - Trả về String (sẽ copy)

// Bài 5: Cho struct Person { name: String, age: u8 }
// Viết hàm take_person(p: Person) in ra thông tin
// Gọi thử và thấy lỗi ownership, sau đó sửa bằng clone()
```

---

## 🎯 LƯU Ý QUAN TRỌNG

| Tình huống | Xảy ra | Ví dụ |
|------------|--------|-------|
| **Move** | String, Vec, các kiểu heap | `let s2 = s1;` |
| **Copy** | integer, bool, char | `let b = a;` |
| **Clone** | Copy sâu (tốn chi phí) | `let s2 = s1.clone();` |
| **Drop** | Biến ra khỏi scope | `}` kết thúc hàm |

---

## ⚡ MẸO GHI NHỚ

**Visualize memory:**
- **Stack:** kích thước cố định, copy nhanh (số nguyên, bool...)
- **Heap:** kích thước động, cần quản lý (String, Vec...)

**Khi nào copy vs move:**
- Nếu có `Copy` trait → copy
- Còn lại → move

---

## ✅ CHECKLIST BÀI 4

- [ ] Hiểu 3 quy tắc ownership
- [ ] Phân biệt move, clone, copy
- [ ] Biết scope và drop
- [ ] Hiểu ownership khi truyền vào hàm
- [ ] Làm xong 5 bài tập
- [ ] Sửa được lỗi "use of moved value"

---

**HOÀN THÀNH BÀI TẬP, CHIA SẺ CODE ĐỂ TÔI REVIEW!**

Bài tiếp theo: **Bài 5 - References & Borrowing** (cách "mượn" mà không lấy ownership). Bạn đã sẵn sàng chưa? 🚀