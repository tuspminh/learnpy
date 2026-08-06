Chào mừng đến **Bài 8 - Collection: Vector, String, HashMap**! 🗂️

Đây là bài học về các **cấu trúc dữ liệu động** - công cụ không thể thiếu để lưu trữ và xử lý dữ liệu trong thực tế.

---

## 📚 LÝ THUYẾT CỐT LÕI

### 1. Vector - Mảng động

**Vector là mảng có thể thay đổi kích thước:**

```rust
fn main() {
    // Tạo Vector
    let mut v: Vec<i32> = Vec::new();  // Cách 1
    let mut v = vec![1, 2, 3];         // Cách 2 (macro)
    
    // Thêm phần tử
    v.push(4);
    v.push(5);
    
    // Đọc phần tử
    let first = &v[0];          // Truy cập trực tiếp (panic nếu out of range)
    let second = v.get(1);      // Trả về Option (an toàn)
    
    match second {
        Some(value) => println!("Giá trị: {}", value),
        None => println!("Không tồn tại"),
    }
    
    // Duyệt Vector
    for i in &v {
        println!("{}", i);
    }
    
    // Duyệt và sửa
    for i in &mut v {
        *i *= 2;  // Nhân đôi mỗi phần tử
    }
    
    // Pop
    let last = v.pop();  // Option<T>
    println!("Pop: {:?}", last);
}
```

### 2. String - Chuỗi Unicode

**String trong Rust rất khác biệt!**

```rust
fn main() {
    // Tạo String
    let mut s = String::new();
    let s = String::from("hello");
    let s = "hello".to_string();
    
    // Nối chuỗi
    let mut s = String::from("Hello");
    s.push_str(", world!");  // Thêm string
    s.push('!');             // Thêm char
    
    // Nối với +
    let s1 = String::from("Hello");
    let s2 = String::from("World");
    let s3 = s1 + &s2;  // s1 bị moved! s2 được mượn
    // println!("{}", s1);  // LỖI! s1 đã bị moved
    
    // Format macro (không move ownership)
    let s1 = String::from("Hello");
    let s2 = String::from("World");
    let s3 = format!("{} {}", s1, s2);  // Cả 2 vẫn hợp lệ
    println!("s1={}, s2={}, s3={}", s1, s2, s3);
    
    // Indexing trong String (Rust KHÔNG cho index trực tiếp!)
    // let c = s[0];  // LỖI! String là UTF-8
    
    // Cách đúng để truy cập
    let s = "hello";
    let c = s.chars().nth(0);  // Some('h')
    
    // Duyệt các ký tự
    for c in "नमस्ते".chars() {
        println!("{}", c);
    }
    
    // Duyệt bytes
    for b in "hello".bytes() {
        println!("{}", b);
    }
}
```

### 3. HashMap - Bảng băm (Key-Value)

**HashMap lưu trữ dữ liệu theo cặp key-value:**

```rust
use std::collections::HashMap;

fn main() {
    // Tạo HashMap
    let mut scores = HashMap::new();
    
    // Thêm phần tử
    scores.insert(String::from("Blue"), 10);
    scores.insert(String::from("Red"), 50);
    
    // Lấy giá trị
    let team = String::from("Blue");
    let score = scores.get(&team);  // Option<&i32>
    
    match score {
        Some(value) => println!("Blue: {}", value),
        None => println!("Không tìm thấy"),
    }
    
    // Duyệt HashMap
    for (key, value) in &scores {
        println!("{}: {}", key, value);
    }
    
    // Sửa giá trị
    scores.insert(String::from("Blue"), 25);  // Override
    
    // entry + or_insert - chỉ chèn nếu chưa có
    scores.entry(String::from("Yellow")).or_insert(100);
    scores.entry(String::from("Blue")).or_insert(99);  // Không đổi (đã có)
    
    // Đếm số lần xuất hiện
    let text = "hello world wonderful world";
    let mut map = HashMap::new();
    
    for word in text.split_whitespace() {
        let count = map.entry(word).or_insert(0);
        *count += 1;
    }
    println!("{:?}", map);  // {"world": 2, "wonderful": 1, "hello": 1}
}
```

---

## 💻 THỰC HÀNH NGAY

**Tạo dự án: `cargo new bai8_collection`**

```rust
use std::collections::HashMap;

#[derive(Debug)]
struct Student {
    name: String,
    scores: Vec<f64>,
}

impl Student {
    fn new(name: &str) -> Self {
        Student {
            name: String::from(name),
            scores: Vec::new(),
        }
    }
    
    fn add_score(&mut self, score: f64) {
        self.scores.push(score);
    }
    
    fn average(&self) -> Option<f64> {
        if self.scores.is_empty() {
            None
        } else {
            let sum: f64 = self.scores.iter().sum();
            Some(sum / self.scores.len() as f64)
        }
    }
}

fn main() {
    // 1. Vector cơ bản
    let mut numbers = vec![1, 2, 3, 4, 5];
    numbers.push(6);
    
    // Sử dụng iterator
    let doubled: Vec<i32> = numbers.iter().map(|x| x * 2).collect();
    println!("Doubled: {:?}", doubled);
    
    // 2. String operations
    let mut text = String::from("Rust");
    text.push_str(" Programming");
    text.push('!');
    println!("{}", text);
    
    // 3. HashMap
    let mut students = HashMap::new();
    
    // Thêm sinh viên
    let mut alice = Student::new("Alice");
    alice.add_score(8.5);
    alice.add_score(9.0);
    alice.add_score(7.5);
    
    let mut bob = Student::new("Bob");
    bob.add_score(6.0);
    bob.add_score(7.0);
    
    students.insert("Alice".to_string(), alice);
    students.insert("Bob".to_string(), bob);
    
    // In thông tin
    for (name, student) in &students {
        match student.average() {
            Some(avg) => println!("{} - Average: {:.1}", name, avg),
            None => println!("{} - No scores", name),
        }
        println!("  Scores: {:?}", student.scores);
    }
    
    // 4. Đếm từ
    let text = "the quick brown fox jumps over the lazy dog";
    let mut word_count = HashMap::new();
    
    for word in text.split_whitespace() {
        *word_count.entry(word).or_insert(0) += 1;
    }
    println!("Word count: {:?}", word_count);
}
```

---

## 📝 BÀI TẬP BẮT BUỘC

```rust
// Bài 1: Tìm số trung vị trong Vector
// Cho vec![5, 2, 8, 1, 9, 3]
// Sắp xếp và tìm giá trị ở giữa
// (Gợi ý: sort, len, chia lấy nguyên)

// Bài 2: Chuyển đổi String
// Hàm reverse_words(s: &str) -> String
// Input: "hello world rust" -> Output: "rust world hello"

// Bài 3: Đếm số lần xuất hiện trong Vector
// Hàm count_occurrences(v: &[i32]) -> HashMap<i32, u32>
// Input: [1, 2, 1, 3, 2, 1] -> {1: 3, 2: 2, 3: 1}

// Bài 4: Phân loại sinh viên theo điểm
// Tạo struct Student { name: String, grade: u8 }
// Hàm group_by_grade(students: Vec<Student>) -> HashMap<String, Vec<String>>
// Key: "Excellent" (>=8), "Good" (6-7), "Fail" (<6)
// Value: danh sách tên sinh viên

// Bài 5: Hệ thống từ điển đơn giản
// Tạo struct Dictionary { words: HashMap<String, String> }
// Methods:
// - new() -> Self
// - add_word(&mut self, word: &str, definition: &str)
// - get_definition(&self, word: &str) -> Option<&str>
// - remove_word(&mut self, word: &str) -> bool
// - list_words(&self) -> Vec<&str>
```

---

## 🎯 LƯU Ý QUAN TRỌNG

| Collection | Đặc điểm | Khi nào dùng |
|------------|----------|--------------|
| **Vec<T>** | Mảng động, có index | Dữ liệu có thứ tự, thêm/xóa cuối |
| **String** | Chuỗi UTF-8 | Xử lý văn bản, Unicode |
| **HashMap<K,V>** | Key-Value, không thứ tự | Tìm kiếm nhanh, ánh xạ |

---

## ⚡ MẸO HAY

1. **`vec![...]`** macro tạo vector nhanh
2. **`iter()`** không lấy ownership, **`into_iter()`** lấy ownership
3. **`collect()`** chuyển iterator sang collection
4. **`entry().or_insert()`** - update or insert
5. **String index**: dùng `chars().nth(i)` thay vì `s[i]`

---

## 🔥 BÀI TẬP NÂNG CAO

```rust
// Hệ thống quản lý sản phẩm
// struct Product { id: u32, name: String, price: f64, category: String }
// struct Inventory { products: HashMap<u32, Product>, categories: HashMap<String, Vec<u32>> }
//
// Methods:
// - add_product(&mut self, product: Product)
// - get_product(&self, id: u32) -> Option<&Product>
// - get_products_by_category(&self, category: &str) -> Vec<&Product>
// - update_price(&mut self, id: u32, new_price: f64) -> Result<(), String>
// - get_total_value(&self) -> f64
// - find_cheapest(&self) -> Option<&Product>
// - get_category_stats(&self) -> HashMap<String, (usize, f64)>
//   (số lượng, tổng giá trị theo category)
```

---

## ✅ CHECKLIST BÀI 8

- [ ] Biết tạo và thao tác với Vector
- [ ] Hiểu String và các thao tác
- [ ] Biết dùng HashMap
- [ ] Hiểu ownership khi dùng collection
- [ ] Làm xong 5 bài tập cơ bản
- [ ] Thử bài tập nâng cao

---

**Hoàn thành bài tập, chia sẻ code để tôi review!**

Bài tiếp theo: **Bài 9 - Generic Types và Traits** - viết code tổng quát, tái sử dụng! 🎯