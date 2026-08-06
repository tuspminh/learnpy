Chào mừng đến **Bài 3: Hàm và Control Flow**! Đây là bài học giúp code của bạn có cấu trúc và ra quyết định thông minh. 🧠

---

## 📚 LÝ THUYẾT CỐT LÕI

### 1. Hàm trong Rust

**Cú pháp cơ bản:**
```rust
fn ten_ham(tham_so: kieu) -> kieu_tra_ve {
    // code
    gia_tri_tra_ve  // KHÔNG có dấu ; (đây là expression)
}
```

**Ví dụ:**
```rust
fn cong_hai_so(a: i32, b: i32) -> i32 {
    a + b  // expression, không có ;
}

fn main() {
    let ket_qua = cong_hai_so(5, 3);
    println!("5 + 3 = {}", ket_qua);  // 8
}
```

**Statement vs Expression (QUAN TRỌNG):**
```rust
// Statement - thực hiện hành động, KHÔNG trả về giá trị
let x = 5;         // statement
println!("hi");     // statement

// Expression - trả về giá trị, CÓ thể gán hoặc dùng
let y = {
    let a = 10;
    let b = 20;
    a + b           // expression (không có ;)
};  // y = 30
```

### 2. Hàm không trả về (Unit `()`)
```rust
fn say_hello() {    // tương đương: -> ()
    println!("Hello!");
    // tự động return ()
}
```

### 3. Control Flow

**If/Else:**
```rust
let number = 7;

if number < 5 {
    println!("nhỏ hơn 5");
} else if number == 5 {
    println!("bằng 5");
} else {
    println!("lớn hơn 5");
}

// If là expression - có thể gán!
let result = if number > 0 { "positive" } else { "negative" };
println!("{}", result);
```

**Vòng lặp:**
```rust
// 1. loop - chạy mãi mãi (dùng break để dừng)
let mut count = 0;
let result = loop {
    count += 1;
    if count == 10 {
        break count * 2;  // có thể trả về giá trị
    }
};  // result = 20

// 2. while - lặp có điều kiện
let mut n = 3;
while n > 0 {
    println!("{}", n);
    n -= 1;
}

// 3. for - duyệt collection (phổ biến nhất!)
for i in 1..5 {  // 1,2,3,4 (KHÔNG gồm 5)
    println!("{}", i);
}

for i in 1..=5 {  // 1,2,3,4,5 (gồm 5)
    println!("{}", i);
}

// Duyệt mảng
let arr = [10, 20, 30];
for element in arr {
    println!("{}", element);
}
```

**`loop` với break có giá trị:**
```rust
let mut counter = 0;
let result = loop {
    counter += 1;
    if counter == 10 {
        break counter;  // trả về giá trị 10
    }
};
println!("Result: {}", result);  // 10
```

---

## 💻 THỰC HÀNH NGAY

**Tạo dự án mới: `cargo new bai3_function`**

```rust
fn main() {
    // 1. Gọi hàm
    say_hello();
    
    // 2. Hàm trả về giá trị
    let sum = add(10, 20);
    println!("10 + 20 = {}", sum);
    
    // 3. If/else
    let age = 18;
    check_age(age);
    
    // 4. Vòng lặp
    print_numbers();
    
    // 5. If as expression
    let is_even = |x| x % 2 == 0;  // closure (sẽ học sau)
    let status = if is_even(4) { "Even" } else { "Odd" };
    println!("Status: {}", status);
}

fn say_hello() {
    println!("Hello from Rust!");
}

fn add(a: i32, b: i32) -> i32 {
    a + b  // expression, không có ;
}

fn check_age(age: i32) {
    if age >= 18 {
        println!("Bạn đã đủ tuổi");
    } else {
        println!("Bạn còn nhỏ");
    }
}

fn print_numbers() {
    // In số từ 1 đến 5
    for i in 1..=5 {
        println!("Số: {}", i);
    }
    
    // Tính tổng
    let mut sum = 0;
    for i in 1..=100 {
        sum += i;
    }
    println!("Tổng 1-100: {}", sum);
}
```

---

## 📝 BÀI TẬP (PHẢI LÀM)

**Trong `src/main.rs` của bạn:**

```rust
// Bài 1: Viết hàm is_even(n: i32) -> bool
// Kiểm tra số chẵn, trả về true/false

// Bài 2: Viết hàm fibonacci(n: u32) -> u32 
// Trả về số Fibonacci thứ n (dùng vòng lặp)
// Ví dụ: fib(0)=0, fib(1)=1, fib(5)=5

// Bài 3: Viết hàm print_multiplication_table(n: i32)
// In bảng cửu chương của n từ 1-10

// Bài 4: Dùng loop để tính tổng các số lẻ từ 1-1000
// Break khi tổng > 10000, in ra tổng và số cuối cùng

// Bài 5: Cho mảng arr = [3, 5, 1, 8, 9, 2]
// Dùng for tìm và in ra số lớn nhất
```

**Code mẫu cho Bài 1+2 để tham khảo:**
```rust
fn is_even(n: i32) -> bool {
    n % 2 == 0
}

fn fibonacci(n: u32) -> u32 {
    if n == 0 { return 0; }
    if n == 1 { return 1; }
    
    let mut prev = 0;
    let mut curr = 1;
    
    for _ in 2..=n {
        let next = prev + curr;
        prev = curr;
        curr = next;
    }
    curr
}

fn main() {
    println!("5 là số chẵn? {}", is_even(5));
    println!("Fib(10) = {}", fibonacci(10));
}
```

---

## 🎯 LƯU Ý QUAN TRỌNG

| Khái niệm | Ví dụ đúng | Ví dụ sai |
|-----------|-----------|-----------|
| **Expression** | `a + b` | `a + b;` (thành statement) |
| **Return sớm** | `return x;` | `return x` (thiếu ;) |
| **Hàm trả về** | `fn add(a:i32,b:i32)->i32{a+b}` | `fn add(a:i32,b:i32){a+b}` |
| **Range** | `1..=5` (gồm 5) | `1..5` (không gồm 5) |

---

## ⚡ MẸO HAY

1. **`cargo fmt`** - tự động format code chuẩn
2. **`cargo clippy`** - bắt lỗi logic và tối ưu
3. Dùng `_` cho biến không dùng: `for _ in 0..10`
4. If/else trong Rust luôn cần `{}` dù chỉ 1 dòng

---

## ✅ CHECKLIST BÀI 3

- [ ] Phân biệt được statement và expression
- [ ] Biết cách viết hàm với tham số và trả về
- [ ] Dùng được if/else và cả 3 loại vòng lặp
- [ ] Hiểu range syntax `..` và `..=`
- [ ] Làm xong 5 bài tập
- [ ] Chạy `cargo fmt` để format code

---

**Chạy xong bài tập, paste code của bạn vào đây để tôi check!**  
Hoặc nếu có lỗi gì, paste luôn lỗi vào tôi sẽ chỉ bạn sửa.

Sẵn sàng cho **Bài 4: Ownership - Trái tim của Rust**? 💖 (Bài học QUAN TRỌNG NHẤT!)