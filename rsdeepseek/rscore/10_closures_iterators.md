Chào mừng đến **Bài 10 - Closures và Iterators**! 🔄

Đây là bài học về **lập trình hàm** trong Rust - viết code ngắn gọn, biểu cảm và hiệu quả hơn!

---

## 📚 LÝ THUYẾT CỐT LÕI

### 1. Closures - Hàm ẩn danh

**Closures là functions có thể capture biến từ môi trường xung quanh:**

```rust
fn main() {
    // Closure cơ bản
    let add_one = |x| x + 1;
    println!("{}", add_one(5));  // 6
    
    // Closure với nhiều tham số
    let add = |a, b| a + b;
    println!("{}", add(3, 4));  // 7
    
    // Closure với block
    let complex = |x| {
        let y = x * 2;
        y + 3
    };
    println!("{}", complex(5));  // 13
    
    // Type annotation (optional)
    let multiply: fn(i32, i32) -> i32 = |a, b| a * b;
}
```

**Capture môi trường:**

```rust
fn main() {
    let x = 4;
    let equal_to_x = |z| z == x;  // Captures x từ môi trường
    
    let y = 4;
    println!("{}", equal_to_x(y));  // true
    
    // Move closure
    let x = vec![1, 2, 3];
    let equal_to_x = move |z| z == x;  // x bị moved vào closure
    // println!("{:?}", x);  // LỖI! x đã bị moved
    
    let y = vec![1, 2, 3];
    println!("{}", equal_to_x(y));  // true
}
```

### 2. Iterator - Duyệt collection hiệu quả

**Iterators là cách Rust xử lý dãy dữ liệu một cách lazy:**

```rust
fn main() {
    let v = vec![1, 2, 3, 4, 5];
    
    // Iterator cơ bản
    let v_iter = v.iter();  // immutable
    let v_iter_mut = v.iter_mut();  // mutable
    let v_into_iter = v.into_iter();  // lấy ownership
    
    // Lazy - chưa làm gì cả
    let v_iter = v.iter();
    
    // Collect - thực thi và collect thành collection mới
    let doubled: Vec<i32> = v.iter().map(|x| x * 2).collect();
    println!("{:?}", doubled);
    
    // Iterator methods
    let sum: i32 = v.iter().sum();
    let count = v.iter().count();
    let any_even = v.iter().any(|&x| x % 2 == 0);
    let all_positive = v.iter().all(|&x| x > 0);
    
    // Chain, filter, map
    let result: Vec<i32> = v.iter()
        .filter(|&&x| x % 2 == 0)
        .map(|&x| x * 10)
        .collect();
    println!("{:?}", result);  // [20, 40]
}
```

### 3. Iterator Methods QUAN TRỌNG

```rust
fn main() {
    let numbers = vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    
    // map - transform
    let squares: Vec<i32> = numbers.iter().map(|&x| x * x).collect();
    
    // filter - lọc
    let evens: Vec<i32> = numbers.iter().filter(|&&x| x % 2 == 0).cloned().collect();
    
    // fold - reduce
    let sum = numbers.iter().fold(0, |acc, &x| acc + x);
    
    // take - lấy n phần tử đầu
    let first_five: Vec<i32> = numbers.iter().take(5).cloned().collect();
    
    // skip - bỏ qua n phần tử đầu
    let last_five: Vec<i32> = numbers.iter().skip(5).cloned().collect();
    
    // zip - ghép 2 iterators
    let letters = vec!['a', 'b', 'c'];
    let zipped: Vec<(i32, char)> = numbers.iter()
        .take(3)
        .zip(letters.iter())
        .map(|(&n, &c)| (n, c))
        .collect();
    
    // enumerate - có index
    for (i, &num) in numbers.iter().enumerate() {
        println!("Index {}: {}", i, num);
    }
    
    // find - tìm phần tử đầu tiên
    let found = numbers.iter().find(|&&x| x > 7);
    println!("{:?}", found);  // Some(8)
    
    // any/all - kiểm tra
    println!("Has even? {}", numbers.iter().any(|&x| x % 2 == 0));
    println!("All positive? {}", numbers.iter().all(|&x| x > 0));
}
```

### 4. Lazy Evaluation và Performance

**Iterators là lazy, chỉ thực hiện khi được consumed:**

```rust
fn main() {
    let v = vec![1, 2, 3, 4, 5];
    
    // KHÔNG thực hiện ngay
    let iter = v.iter()
        .map(|x| {
            println!("Mapping {}", x);
            x * 2
        })
        .filter(|x| {
            println!("Filtering {}", x);
            x % 3 == 0
        });
    
    // Chỉ thực hiện khi collect
    let result: Vec<i32> = iter.collect();
    println!("{:?}", result);
    
    // Performance - thường nhanh hơn loop thủ công
    // do compiler có thể optimize
}
```

---

## 💻 THỰC HÀNH NGAY

**Tạo dự án: `cargo new bai10_closures`**

```rust
use std::collections::HashMap;

#[derive(Debug)]
struct Product {
    id: u32,
    name: String,
    price: f64,
    quantity: u32,
}

#[derive(Debug)]
struct Order {
    items: Vec<String>,
    total: f64,
}

fn main() {
    // 1. Closures cơ bản
    let add = |a: i32, b: i32| a + b;
    let multiply = |a, b| a * b;
    let square = |x: i32| -> i32 { x * x };
    
    println!("Add: {}", add(5, 3));
    println!("Multiply: {}", multiply(4, 5));
    println!("Square: {}", square(6));
    
    // 2. Closures capture
    let factor = 2;
    let multiply_by = |x| x * factor;
    println!("{}", multiply_by(10));
    
    // 3. Iterator cơ bản
    let numbers = vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    
    // Filter + map
    let processed: Vec<i32> = numbers.iter()
        .filter(|&&x| x % 2 == 0)
        .map(|&x| x * x)
        .collect();
    println!("Even squares: {:?}", processed);
    
    // 4. Chain operations
    let products = vec![
        Product { id: 1, name: "Laptop".to_string(), price: 999.99, quantity: 5 },
        Product { id: 2, name: "Mouse".to_string(), price: 29.99, quantity: 20 },
        Product { id: 3, name: "Keyboard".to_string(), price: 89.99, quantity: 10 },
        Product { id: 4, name: "Monitor".to_string(), price: 299.99, quantity: 3 },
    ];
    
    // Lọc sản phẩm > $50 và giá đã giảm 10%
    let expensive: Vec<_> = products.iter()
        .filter(|p| p.price > 50.0)
        .map(|p| (p.name.clone(), p.price * 0.9))
        .collect();
    println!("Expensive with discount: {:?}", expensive);
    
    // 5. Fold (reduce)
    let sum: i32 = numbers.iter().fold(0, |acc, &x| acc + x);
    let product: i32 = numbers.iter().fold(1, |acc, &x| acc * x);
    println!("Sum: {}, Product: {}", sum, product);
    
    // 6. Advanced iterator example
    let orders = vec![
        Order { items: vec!["Laptop".to_string(), "Mouse".to_string()], total: 1029.98 },
        Order { items: vec!["Keyboard".to_string()], total: 89.99 },
        Order { items: vec!["Monitor".to_string(), "Keyboard".to_string()], total: 389.98 },
    ];
    
    // Tìm đơn hàng > $100
    let big_orders: Vec<_> = orders.iter()
        .filter(|order| order.total > 100.0)
        .collect();
    println!("Big orders: {:?}", big_orders);
}
```

---

## 📝 BÀI TẬP BẮT BUỘC

```rust
// Bài 1: Closure cơ bản
// Tạo closure:
// - is_even: kiểm tra số chẵn
// - power: lũy thừa (2 tham số)
// - factorial: tính giai thừa (dùng recursion hoặc loop)

// Bài 2: Chuyển đổi dữ liệu với iterator
// Cho list các string: ["1", "2", "3", "4", "5"]
// Dùng iterator chuyển thành Vec<i32> (dùng parse)
// Bỏ qua các string không parse được

// Bài 3: Filter và Map
// Cho vec các số nguyên, giữ lại số chẵn, bình phương chúng
// Viết function process_numbers(numbers: &[i32]) -> Vec<i32>

// Bài 4: Sử dụng fold
// Viết function mean(numbers: &[f64]) -> Option<f64>
// Tính trung bình cộng, trả về None nếu slice rỗng

// Bài 5: Chain operations với struct
// Tạo struct Employee { name: String, department: String, salary: f64 }
// Cho list employees, tìm:
// - Tất cả employees có lương > 50000
// - Tên của họ (collect thành Vec<&str>)
// - Sắp xếp theo tên (alphabetical)
// - In ra tổng lương của những người này (dùng fold)
```

---

## 🎯 LƯU Ý QUAN TRỌNG

| Khái niệm | Cú pháp | Đặc điểm |
|-----------|---------|----------|
| **Closure** | `|param| body` | Capture môi trường |
| **Move closure** | `move |param| body` | Lấy ownership |
| **Iterator** | `iter()`, `iter_mut()`, `into_iter()` | Lazy, hiệu quả |
| **Map** | `.map(f)` | Transform từng phần tử |
| **Filter** | `.filter(f)` | Lọc phần tử |
| **Fold** | `.fold(init, f)` | Reduce giá trị |

---

## ⚡ MẸO HAY

1. **Closure types**: `Fn` (immutable), `FnMut` (mutable), `FnOnce` (ownership)
2. **`into_iter()`** lấy ownership của collection
3. **`iter_mut()`** cho phép sửa giá trị
4. **`filter_map()`** kết hợp filter + map
5. **`flat_map()`** flatten nested iterators
6. **`chain()`** nối 2 iterators

---

## 🔥 BÀI TẬP NÂNG CAO

```rust
// Hệ thống phân tích dữ liệu với iterators
// 1. Đọc dữ liệu từ file log (giả lập)
// 2. Parse mỗi dòng thành struct LogEntry { timestamp: String, level: String, message: String }
// 3. Dùng iterators để:
//    - Lọc ra log ERROR
//    - Đếm số lỗi mỗi loại (HashMap<String, u32>)
//    - Tìm lỗi dài nhất (theo message length)
//    - Nhóm log theo ngày (HashMap<String, Vec<LogEntry>>)
// 4. Sắp xếp và in ra báo cáo
//
// Bonus: Dùng closures để tạo custom filters
// let filter_by_level = |level: String| move |entry: &LogEntry| entry.level == level;
```

---

## ✅ CHECKLIST BÀI 10

- [ ] Hiểu closure và cách capture môi trường
- [ ] Biết dùng iterator và các method cơ bản
- [ ] Hiểu lazy evaluation của iterators
- [ ] Phân biệt được `iter()`, `iter_mut()`, `into_iter()`
- [ ] Dùng được `map`, `filter`, `fold`, `collect`
- [ ] Làm xong 5 bài tập cơ bản
- [ ] Thử bài tập nâng cao

---

**Hoàn thành bài tập, chia sẻ code để tôi review!**

Bài tiếp theo: **Bài 11 - Smart Pointers: Box, Rc, RefCell** - quản lý bộ nhớ nâng cao! 💡