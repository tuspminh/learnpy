Chào mừng đến **Bài 7: Enum và Pattern Matching**! 🌈

Đây là một trong những tính năng MẠNH NHẤT của Rust. Enum giúp bạn biểu diễn nhiều trạng thái khác nhau, và pattern matching giúp xử lý chúng một cách an toàn.

---

## 📚 LÝ THUYẾT CỐT LÕI

### 1. Enum (Kiểu liệt kê)

**Enum định nghĩa một kiểu có thể nhận một trong nhiều giá trị khác nhau:**

```rust
// Định nghĩa enum đơn giản
enum Direction {
    Up,
    Down,
    Left,
    Right,
}

fn main() {
    let dir = Direction::Up;
    
    match dir {
        Direction::Up => println!("Đi lên"),
        Direction::Down => println!("Đi xuống"),
        Direction::Left => println!("Đi trái"),
        Direction::Right => println!("Đi phải"),
    }
}
```

### 2. Enum với dữ liệu

**Enum có thể chứa dữ liệu phức tạp:**

```rust
enum Message {
    Quit,                       // Không có dữ liệu
    Move { x: i32, y: i32 },    // Struct-like
    Write(String),              // Tuple-like
    ChangeColor(i32, i32, i32), // Tuple-like
}

fn process(msg: Message) {
    match msg {
        Message::Quit => println!("Thoát"),
        Message::Move { x, y } => println!("Di chuyển đến ({}, {})", x, y),
        Message::Write(text) => println!("Viết: {}", text),
        Message::ChangeColor(r, g, b) => {
            println!("Đổi màu: RGB({}, {}, {})", r, g, b)
        }
    }
}
```

### 3. Option<T> - Xử lý giá trị có thể null

**Option là enum quan trọng nhất trong Rust:**

```rust
enum Option<T> {
    Some(T),  // Có giá trị
    None,     // Không có giá trị
}
```

**Ví dụ thực tế:**

```rust
fn divide(x: i32, y: i32) -> Option<i32> {
    if y == 0 {
        None  // Không chia được
    } else {
        Some(x / y)  // Có kết quả
    }
}

fn main() {
    let result = divide(10, 2);
    
    // Cách 1: match
    match result {
        Some(value) => println!("Kết quả: {}", value),
        None => println!("Không thể chia"),
    }
    
    // Cách 2: if let
    if let Some(value) = result {
        println!("Kết quả: {}", value);
    }
    
    // Cách 3: unwrap (nguy hiểm!)
    // println!("{}", result.unwrap());  // panic nếu None
    
    // Cách 4: unwrap_or (an toàn)
    let value = result.unwrap_or(0);
    println!("Giá trị: {}", value);
}
```

### 4. Result<T, E> - Xử lý lỗi

**Result là enum cho xử lý lỗi:**

```rust
enum Result<T, E> {
    Ok(T),  // Thành công với giá trị T
    Err(E), // Thất bại với lỗi E
}
```

**Ví dụ:**

```rust
use std::fs::File;
use std::io::ErrorKind;

fn read_file() -> Result<String, std::io::Error> {
    let file = File::open("hello.txt")?;  // ? trả về lỗi nếu có
    // ... đọc file
    Ok(String::from("content"))
}

fn main() {
    let result = read_file();
    
    match result {
        Ok(content) => println!("File content: {}", content),
        Err(error) => match error.kind() {
            ErrorKind::NotFound => println!("File không tồn tại"),
            _ => println!("Lỗi khác: {}", error),
        }
    }
}
```

### 5. Pattern Matching nâng cao

**Pattern rất linh hoạt:**

```rust
// Destructuring struct
struct Point { x: i32, y: i32 }

let point = Point { x: 0, y: 7 };
match point {
    Point { x, y } if x == 0 => println!("x bằng 0, y={}", y),
    Point { x: 0, y } => println!("x bằng 0, y={}", y),
    Point { x, y: 0 } => println!("y bằng 0, x={}", x),
    Point { x, y } => println!("x={}, y={}", x, y),
}

// Destructuring enum
enum Color {
    RGB(u8, u8, u8),
    Hex(String),
}

match color {
    Color::RGB(r, g, b) if r == 0 => println!("Không có red"),
    Color::RGB(r, g, b) => println!("RGB({}, {}, {})", r, g, b),
    Color::Hex(s) => println!("Mã hex: {}", s),
}

// Destructuring array
let numbers = [1, 2, 3, 4, 5];
match numbers {
    [first, .., last] => println!("Đầu: {}, cuối: {}", first, last),
    [..] => println!("Array bình thường"),
}

// Destructuring tuple
let tuple = (1, 2, 3);
match tuple {
    (x, y, z) => println!("x={}, y={}, z={}", x, y, z),
}
```

---

## 💻 THỰC HÀNH NGAY

**Tạo dự án: `cargo new bai7_enum`**

```rust
#[derive(Debug)]
enum IpAddress {
    V4(u8, u8, u8, u8),
    V6(String),
}

#[derive(Debug)]
enum Coin {
    Penny,
    Nickel,
    Dime,
    Quarter,
}

impl Coin {
    fn value_in_cents(&self) -> u8 {
        match self {
            Coin::Penny => 1,
            Coin::Nickel => 5,
            Coin::Dime => 10,
            Coin::Quarter => 25,
        }
    }
}

#[derive(Debug)]
struct User {
    name: String,
    age: Option<u8>,  // có thể không có tuổi
}

fn main() {
    // 1. Enum với dữ liệu
    let ip1 = IpAddress::V4(192, 168, 1, 1);
    let ip2 = IpAddress::V6(String::from("::1"));
    println!("{:?}", ip1);
    println!("{:?}", ip2);
    
    // 2. Option
    let user1 = User {
        name: String::from("Alice"),
        age: Some(25),
    };
    let user2 = User {
        name: String::from("Bob"),
        age: None,
    };
    
    // Xử lý Option
    for user in [&user1, &user2] {
        match user.age {
            Some(age) => println!("{} - {} tuổi", user.name, age),
            None => println!("{} - Chưa có thông tin tuổi", user.name),
        }
    }
    
    // 3. Result
    let result = divide(10, 2);
    match result {
        Ok(value) => println!("Chia thành công: {}", value),
        Err(err) => println!("Lỗi: {}", err),
    }
    
    // 4. if let - ngắn gọn
    let coin = Coin::Quarter;
    if let Coin::Quarter = coin {
        println!("Quarter = 25 cents");
    }
    
    // 5. while let
    let mut stack = Vec::new();
    stack.push(1);
    stack.push(2);
    stack.push(3);
    
    while let Some(top) = stack.pop() {
        println!("Pop: {}", top);
    }
}

fn divide(x: i32, y: i32) -> Result<i32, String> {
    if y == 0 {
        Err(String::from("Không thể chia cho 0"))
    } else {
        Ok(x / y)
    }
}
```

---

## 📝 BÀI TẬP BẮT BUỘC

```rust
// Bài 1: Tạo enum Status với các trạng thái
// Active, Inactive, Pending, Archived
// Implement method description(&self) -> &str cho Status

// Bài 2: Tạo enum Payment
// - Cash
// - CreditCard { number: String, cvv: u16 }
// - BankTransfer { bank: String, account: String }
// Implement method process(&self) -> String (in ra phương thức thanh toán)

// Bài 3: Xử lý Option
// Hàm find_name(names: &[String], target: &str) -> Option<usize>
// Trả về index của target trong mảng, None nếu không tìm thấy
// Sử dụng vòng lặp với iterator

// Bài 4: Xử lý Result
// Hàm parse_number(s: &str) -> Result<i32, String>
// Chuyển string thành số, bắt lỗi parse
// (Gợi ý: dùng s.parse::<i32>())

// Bài 5: Pattern matching với struct
// Cho struct Order { id: u32, status: OrderStatus }
// Định nghĩa enum OrderStatus { Placed, Shipped, Delivered, Cancelled }
// Implement method display_status(&self) -> String
// In ra thông báo khác nhau cho mỗi trạng thái
```

---

## 🎯 LƯU Ý QUAN TRỌNG

| Khái niệm | Cú pháp | Sử dụng |
|-----------|---------|---------|
| **Enum** | `enum Name { Variant }` | Biểu diễn nhiều trạng thái |
| **Option** | `Option<T>` | Xử lý null an toàn |
| **Result** | `Result<T, E>` | Xử lý lỗi |
| **match** | `match value { pattern => }` | Pattern matching tổng quát |
| **if let** | `if let pattern = value` | Match chỉ 1 pattern |
| **while let** | `while let pattern = value` | Lặp với pattern |

---

## ⚡ MẸO HAY

1. **Luôn ưu tiên Option/Result** thay vì null
2. **Dùng `if let`** khi chỉ quan tâm 1 pattern
3. **Dùng `?` operator** trong function trả về Result
4. **`unwrap_or` / `unwrap_or_else`** an toàn hơn `unwrap`

---

## 🔥 BÀI TẬP NÂNG CAO

```rust
// Tạo hệ thống quản lý kho hàng
// enum ProductCategory { Electronics, Clothing, Food, Books }
// struct Product { id: u32, name: String, category: ProductCategory, price: f64, quantity: u32 }
// 
// Viết functions:
// - create_product(name: &str, category: ProductCategory, price: f64) -> Product
// - update_quantity(product: &mut Product, amount: i32) -> Result<(), String>
//   (không cho quantity âm)
// - get_category_products(products: &[Product], category: ProductCategory) -> Vec<&Product>
// - find_expensive_products(products: &[Product], min_price: f64) -> Vec<&Product>
// 
// Bonus: Tạo enum ProductError { InvalidQuantity, OutOfStock, NegativePrice }
// Sử dụng trong error handling
```

---

## ✅ CHECKLIST BÀI 7

- [ ] Hiểu enum và cách dùng
- [ ] Biết cách dùng Option và Result
- [ ] Thành thạo match và if let
- [ ] Biết destructuring enum, struct, tuple
- [ ] Làm xong 5 bài tập cơ bản
- [ ] Thử bài tập nâng cao

---

**Hoàn thành bài tập, chia sẻ code để tôi review!**

Bài tiếp theo: **Bài 8 - Collection: Vector, String, HashMap** - lưu trữ dữ liệu hiệu quả! 🗂️