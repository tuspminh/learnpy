Chào mừng đến **Bài 9 - Generic Types và Traits**! 🎯

Đây là bài học giúp bạn viết code **tổng quát, linh hoạt và tái sử dụng** - một trong những kỹ năng quan trọng nhất của lập trình viên Rust chuyên nghiệp.

---

## 📚 LÝ THUYẾT CỐT LÕI

### 1. Generic Types - Kiểu tổng quát

**Generic cho phép viết code làm việc với nhiều kiểu dữ liệu khác nhau:**

```rust
// Generic trong function
fn largest<T>(list: &[T]) -> &T {
    let mut largest = &list[0];
    for item in list {
        if item > largest {  // LỖI! T chưa có trait PartialOrd
            largest = item;
        }
    }
    largest
}

// Sửa: ràng buộc T phải có trait PartialOrd (sẽ học dưới)
fn largest<T: PartialOrd>(list: &[T]) -> &T {
    let mut largest = &list[0];
    for item in list {
        if item > largest {
            largest = item;
        }
    }
    largest
}
```

**Generic trong Struct:**

```rust
struct Point<T> {
    x: T,
    y: T,
}

// Có thể có nhiều generic parameters
struct Pair<T, U> {
    first: T,
    second: U,
}

fn main() {
    let p1 = Point { x: 5, y: 10 };        // Point<i32>
    let p2 = Point { x: 1.0, y: 4.0 };      // Point<f64>
    let p3 = Point { x: 5, y: 10.0 };       // LỖI! kiểu khác nhau
    
    let pair = Pair { first: 5, second: "hello" };  // Pair<i32, &str>
}
```

**Generic trong Enum:**

```rust
enum Option<T> {
    Some(T),
    None,
}

enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

**Generic trong Method:**

```rust
struct Point<T> {
    x: T,
    y: T,
}

impl<T> Point<T> {
    fn x(&self) -> &T {
        &self.x
    }
}

// Chỉ implement cho kiểu cụ thể
impl Point<f64> {
    fn distance_from_origin(&self) -> f64 {
        (self.x.powi(2) + self.y.powi(2)).sqrt()
    }
}

fn main() {
    let p = Point { x: 5, y: 10 };
    println!("x = {}", p.x());  // 5
    
    let p2 = Point { x: 1.0, y: 2.0 };
    println!("distance = {}", p2.distance_from_origin());
}
```

### 2. Traits - Định nghĩa hành vi chung

**Trait giống như interface trong các ngôn ngữ khác:**

```rust
// Định nghĩa trait
trait Summary {
    fn summarize(&self) -> String;
}

// Implement trait cho struct
struct NewsArticle {
    headline: String,
    content: String,
}

impl Summary for NewsArticle {
    fn summarize(&self) -> String {
        format!("{} - ...", self.headline)
    }
}

struct Tweet {
    username: String,
    content: String,
}

impl Summary for Tweet {
    fn summarize(&self) -> String {
        format!("{}: {}", self.username, self.content)
    }
}

fn main() {
    let article = NewsArticle {
        headline: String::from("Rust 2024 Released"),
        content: String::from("New features: ..."),
    };
    
    let tweet = Tweet {
        username: String::from("@rustlang"),
        content: String::from("Rust 2024 is awesome!"),
    };
    
    println!("{}", article.summarize());
    println!("{}", tweet.summarize());
}
```

### 3. Traits làm tham số

**Trait bounds - ràng buộc trait:**

```rust
// Cách 1: Trait bound syntax
fn notify<T: Summary>(item: &T) {
    println!("Breaking news: {}", item.summarize());
}

// Cách 2: impl Trait (sugar syntax)
fn notify(item: &impl Summary) {
    println!("Breaking news: {}", item.summarize());
}

// Cách 3: Nhiều trait bounds
fn compare_and_print<T: Summary + Display>(item1: &T, item2: &T) {
    println!("Item1: {}", item1.summarize());
    println!("Item2: {}", item2.summarize());
}

// Cách 4: where clause (dễ đọc hơn)
fn some_function<T, U>(t: &T, u: &U) -> i32
where
    T: Display + Clone,
    U: Clone + Debug,
{
    // ...
    42
}
```

### 4. Default Implementation

```rust
trait Animal {
    fn make_sound(&self) -> String;
    
    // Default implementation
    fn sleep(&self) -> String {
        String::from("Zzz...")
    }
}

struct Dog;
struct Cat;

impl Animal for Dog {
    fn make_sound(&self) -> String {
        String::from("Woof!")
    }
}

impl Animal for Cat {
    fn make_sound(&self) -> String {
        String::from("Meow!")
    }
    // sleep có thể override hoặc không
}

fn main() {
    let dog = Dog;
    println!("{} {}", dog.make_sound(), dog.sleep());
    // Woof! Zzz...
}
```

### 5. Trait Objects - Đa hình động

```rust
trait Draw {
    fn draw(&self);
}

struct Circle {
    radius: f64,
}

impl Draw for Circle {
    fn draw(&self) {
        println!("Drawing circle with radius {}", self.radius);
    }
}

struct Rectangle {
    width: f64,
    height: f64,
}

impl Draw for Rectangle {
    fn draw(&self) {
        println!("Drawing rectangle {}x{}", self.width, self.height);
    }
}

// Trait object: Box<dyn Draw>
fn draw_shapes(shapes: Vec<Box<dyn Draw>>) {
    for shape in shapes {
        shape.draw();
    }
}

fn main() {
    let shapes: Vec<Box<dyn Draw>> = vec![
        Box::new(Circle { radius: 1.0 }),
        Box::new(Rectangle { width: 2.0, height: 3.0 }),
    ];
    draw_shapes(shapes);
}
```

---

## 💻 THỰC HÀNH NGAY

**Tạo dự án: `cargo new bai9_generics`**

```rust
use std::fmt::Display;

// 1. Generic struct
struct Container<T> {
    items: Vec<T>,
}

impl<T> Container<T> {
    fn new() -> Self {
        Container { items: Vec::new() }
    }
    
    fn add(&mut self, item: T) {
        self.items.push(item);
    }
    
    fn get(&self, index: usize) -> Option<&T> {
        self.items.get(index)
    }
    
    fn len(&self) -> usize {
        self.items.len()
    }
}

// 2. Trait
trait Greetable {
    fn greet(&self) -> String;
    fn farewell(&self) -> String {
        String::from("Goodbye!")
    }
}

// 3. Implement trait
struct Person {
    name: String,
    age: u32,
}

impl Greetable for Person {
    fn greet(&self) -> String {
        format!("Hello, my name is {} and I'm {} years old", self.name, self.age)
    }
    
    // farewell có default, không cần implement
}

struct Robot {
    model: String,
}

impl Greetable for Robot {
    fn greet(&self) -> String {
        format!("Beep boop! I'm model {}", self.model)
    }
    
    fn farewell(&self) -> String {
        String::from("Beep boop, shutting down!")
    }
}

// 4. Generic function
fn print_greeting<T: Greetable + Display>(item: &T) {
    println!("{} - {}", item, item.greet());
}

fn main() {
    // Container
    let mut container = Container::new();
    container.add(1);
    container.add(2);
    container.add(3);
    println!("Length: {}", container.len());
    println!("Item 0: {:?}", container.get(0));
    
    // Greetable
    let alice = Person {
        name: String::from("Alice"),
        age: 30,
    };
    let robot = Robot {
        model: String::from("RustBot"),
    };
    
    println!("{}", alice.greet());
    println!("{}", alice.farewell());
    println!("{}", robot.greet());
    println!("{}", robot.farewell());
    
    // 5. Trait object example
    let greetables: Vec<Box<dyn Greetable>> = vec![
        Box::new(alice),
        Box::new(robot),
    ];
    
    for g in &greetables {
        println!("{}", g.greet());
    }
}

// 6. Derive macros
#[derive(Debug, Clone, PartialEq)]
struct Point2D {
    x: f64,
    y: f64,
}

impl Display for Point2D {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "({}, {})", self.x, self.y)
    }
}

impl Greetable for Point2D {
    fn greet(&self) -> String {
        format!("I'm at point {}", self)
    }
}
```

---

## 📝 BÀI TẬP BẮT BUỘC

```rust
// Bài 1: Generic function cho max
// Viết hàm find_max<T: PartialOrd>(items: &[T]) -> Option<&T>
// Trả về None nếu slice rỗng, ngược lại trả về phần tử lớn nhất

// Bài 2: Generic struct Pair
// struct Pair<T> { first: T, second: T }
// Implement:
// - new(first: T, second: T) -> Self
// - swap(&mut self) - đổi chỗ
// - get_first(&self) -> &T
// - get_second(&self) -> &T
// - max(&self) -> &T (chỉ khi T: PartialOrd)

// Bài 3: Trait Printable
// Tạo trait Printable với method print(&self)
// Implement cho i32, String, và Vec<T> (in các phần tử)

// Bài 4: Generic function với trait bounds
// Viết function process_data<T>(data: &T) where T: Display + Clone
// In data ra, clone và in ra 2 lần

// Bài 5: Trait object
// Tạo trait Area { fn area(&self) -> f64 }
// Implement cho Rectangle {width, height} và Circle {radius}
// Tạo vector các trait object và tính tổng diện tích
```

---

## 🎯 LƯU Ý QUAN TRỌNG

| Khái niệm | Cú pháp | Sử dụng |
|-----------|---------|---------|
| **Generic type** | `<T>` | Code tổng quát, tái sử dụng |
| **Trait** | `trait Name { fn method(&self); }` | Định nghĩa hành vi chung |
| **Trait bound** | `T: Trait` | Ràng buộc generic |
| **impl Trait** | `fn foo(x: impl Trait)` | Sugar syntax |
| **Trait object** | `Box<dyn Trait>` | Đa hình động |

---

## ⚡ MẸO HAY

1. **Trait bounds** giúp compiler bắt lỗi sớm
2. **`impl Trait`** ngắn hơn `<T: Trait>` nhưng ít linh hoạt hơn
3. **Trait object** dùng khi cần động (runtime)
4. **`where` clause** giúp code dễ đọc với nhiều bounds
5. **Derive macros** (`#[derive]`) tự động implement các trait

---

## 🔥 BÀI TẬP NÂNG CAO

```rust
// Hệ thống đồ họa với generic và trait
// 1. Tạo trait Shape với method area(&self) -> f64 và perimeter(&self) -> f64
// 2. Tạo struct Rectangle, Circle, Triangle
// 3. Tạo struct Group<T: Shape> { shapes: Vec<T> } và GroupDynamic { shapes: Vec<Box<dyn Shape>> }
// 4. Implement cho cả 2 loại Group:
//    - total_area(&self) -> f64
//    - filter_by_area(&self, min_area: f64) -> Vec<&T> (cho Group<T>)
// 5. So sánh ưu nhược điểm của generic vs trait object
// 6. Bonus: Tạo trait Transform { fn scale(&mut self, factor: f64); }
//    và implement cho các shape
```

---

## ✅ CHECKLIST BÀI 9

- [ ] Hiểu generic type và cách dùng
- [ ] Biết cách định nghĩa trait
- [ ] Implement trait cho struct
- [ ] Dùng trait bounds trong hàm
- [ ] Phân biệt được trait object vs generic
- [ ] Làm xong 5 bài tập cơ bản
- [ ] Thử bài tập nâng cao

---

**Hoàn thành bài tập, chia sẻ code để tôi review!**

Bài tiếp theo: **Bài 10 - Closures và Iterators** - lập trình hàm trong Rust! 🔄