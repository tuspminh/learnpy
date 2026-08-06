Chào mừng đến **Bài 6: Struct và Method**! 🏗️

Đây là bài học giúp bạn tạo ra **kiểu dữ liệu tùy chỉnh** - nền tảng cho mọi ứng dụng thực tế.

---

## 📚 LÝ THUYẾT CỐT LÕI

### 1. Struct (Cấu trúc)

**Struct là cách nhóm các dữ liệu liên quan lại với nhau:**

```rust
// Định nghĩa struct
struct Person {
    name: String,
    age: u32,
    email: String,
}

fn main() {
    // Tạo instance
    let person1 = Person {
        name: String::from("Alice"),
        age: 30,
        email: String::from("alice@email.com"),
    };
    
    // Truy cập field
    println!("Tên: {}", person1.name);
}
```

### 2. Tuple Struct

**Struct không có tên field, chỉ có kiểu:**

```rust
struct Color(i32, i32, i32);
struct Point(i32, i32);

fn main() {
    let black = Color(0, 0, 0);
    let origin = Point(0, 0);
    
    println!("Đen: ({}, {}, {})", black.0, black.1, black.2);
}
```

### 3. Unit Struct

**Struct không có field nào (dùng để đánh dấu):**

```rust
struct Empty;  // unit struct
struct User;   // có thể dùng để implement trait
```

### 4. Method (Phương thức)

**Gắn hàm vào struct bằng `impl`:**

```rust
struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    // Method - nhận &self
    fn area(&self) -> u32 {
        self.width * self.height
    }
    
    // Method mutable
    fn scale(&mut self, factor: u32) {
        self.width *= factor;
        self.height *= factor;
    }
    
    // Associated function (không có self) - như static method
    fn square(size: u32) -> Rectangle {
        Rectangle {
            width: size,
            height: size,
        }
    }
}

fn main() {
    let mut rect = Rectangle {
        width: 10,
        height: 20,
    };
    
    println!("Diện tích: {}", rect.area());  // 200
    
    rect.scale(2);
    println!("Sau scale: {}x{}", rect.width, rect.height);  // 20x40
    
    let square = Rectangle::square(5);  // gọi associated function
    println!("Hình vuông: {}x{}", square.width, square.height);
}
```

### 5. Self và &self

```rust
impl Rectangle {
    // &self: đọc dữ liệu (immutable borrow)
    fn area(&self) -> u32 { ... }
    
    // &mut self: thay đổi dữ liệu (mutable borrow)
    fn scale(&mut self, factor: u32) { ... }
    
    // self: lấy ownership (ít dùng)
    fn consume(self) { ... }
    
    // Không có self: associated function
    fn new(w: u32, h: u32) -> Rectangle { ... }
}
```

---

## 💻 THỰC HÀNH NGAY

**Tạo dự án: `cargo new bai6_struct`**

```rust
#[derive(Debug)]  // cho phép in struct với {:?}
struct Book {
    title: String,
    author: String,
    pages: u32,
    read: bool,
}

impl Book {
    // Associated function - tạo sách mới
    fn new(title: &str, author: &str, pages: u32) -> Book {
        Book {
            title: String::from(title),
            author: String::from(author),
            pages,
            read: false,
        }
    }
    
    // Method - đọc sách
    fn read(&mut self) {
        self.read = true;
        println!("Đã đọc '{}'", self.title);
    }
    
    // Method - kiểm tra đã đọc chưa
    fn is_read(&self) -> bool {
        self.read
    }
    
    // Method - lấy thông tin
    fn info(&self) -> String {
        format!("'{}' của {}, {} trang", 
                self.title, self.author, self.pages)
    }
}

fn main() {
    // Tạo sách
    let mut book1 = Book::new("Rust Programming", "John Doe", 350);
    let book2 = Book::new("Python Basics", "Jane Smith", 200);
    
    // Debug print
    println!("{:?}", book1);
    println!("{:#?}", book1);  // pretty print
    
    // Dùng methods
    println!("{}", book1.info());
    book1.read();
    println!("Đã đọc? {}", book1.is_read());
    
    // Struct update syntax
    let book3 = Book {
        title: String::from("Advanced Rust"),
        ..book2  // copy các field còn lại từ book2
    };
    println!("{}", book3.info());
}

// Tuple struct
struct RGB(u8, u8, u8);

fn main() {
    let red = RGB(255, 0, 0);
    println!("R: {}, G: {}, B: {}", red.0, red.1, red.2);
}
```

---

## 📝 BÀI TẬP BẮT BUỘC

```rust
// Bài 1: Tạo struct Student
// Fields: name (String), age (u8), grade (f32)
// Methods:
// - new(name: &str, age: u8) -> Student (grade mặc định 0.0)
// - update_grade(&mut self, new_grade: f32)
// - is_passing(&self) -> bool (grade >= 5.0)
// - display(&self) -> String (format: "Name: X, Age: Y, Grade: Z")

// Bài 2: Tạo struct BankAccount
// Fields: account_number: String, balance: f64
// Methods:
// - new(account_number: &str) -> BankAccount (balance = 0.0)
// - deposit(&mut self, amount: f64) -> f64 (trả về balance mới)
// - withdraw(&mut self, amount: f64) -> Result<f64, String> 
//   (không cho rút quá balance)
// - transfer(&mut self, to: &mut BankAccount, amount: f64) -> Result<(), String>

// Bài 3: Sử dụng struct trong hàm
// Tạo struct Point {x: f64, y: f64}
// Viết hàm distance(p1: &Point, p2: &Point) -> f64
// (Công thức: sqrt((x2-x1)^2 + (y2-y1)^2))

// Bài 4: Struct lồng nhau
// Tạo struct Address {street: String, city: String}
// Tạo struct Person {name: String, age: u8, address: Address}
// Implement method display_full_info(&self) -> String

// Bài 5: Tuple struct với validation
// Tạo struct Email(String) với method validate(&self) -> bool
// Email hợp lệ: có '@' và '.'
```

---

## 🎯 LƯU Ý QUAN TRỌNG

| Khái niệm | Cú pháp | Mục đích |
|-----------|---------|----------|
| **Struct** | `struct Name { field: Type }` | Nhóm dữ liệu |
| **Tuple struct** | `struct Name(Type1, Type2)` | Struct không tên field |
| **Method** | `fn method(&self) {}` | Hành động trên instance |
| **Associated function** | `fn new() -> Self {}` | Constructor, không cần instance |
| **Self** | `Self` trong impl | Đại diện cho kiểu struct |

---

## ⚡ MẸO HAY

1. **`#[derive(Debug)]`** - in struct dễ dàng
2. **`#[derive(Clone, Copy)]`** - struct có thể copy
3. **Struct update syntax** - `..other_struct` copy field
4. **Khi dùng `String` trong struct**: nhớ ownership

---

## 🔥 BÀI TẬP NÂNG CAO

```rust
// Tạo struct ShoppingCart
// Fields: items: Vec<String>, total: f64
// Methods:
// - new() -> Self
// - add_item(&mut self, item: &str, price: f64)
// - remove_item(&mut self, item: &str) -> bool (trả về true nếu xóa được)
// - checkout(&self) -> String (in ra hóa đơn)
// - apply_discount(&mut self, percent: f64)

// Bonus: Đảm bảo price không âm khi add_item (dùng Result)
```

---

## ✅ CHECKLIST BÀI 6

- [ ] Hiểu cú pháp struct và các loại struct
- [ ] Biết cách tạo instance và truy cập field
- [ ] Implement method với `impl`
- [ ] Phân biệt `&self`, `&mut self`, và associated function
- [ ] Làm xong 5 bài tập cơ bản
- [ ] Thử bài tập nâng cao

---

**Hoàn thành bài tập, chia sẻ code để tôi review!**

Bài tiếp theo: **Bài 7 - Enum và Pattern Matching** - xử lý nhiều trạng thái một cách an toàn! 🌈