Chào mừng đến **Bài 14 - Macros**! 🪄

Đây là bài học về **metaprogramming** - viết code để tạo ra code! Macros là một trong những tính năng mạnh mẽ nhất của Rust, cho phép bạn mở rộng ngôn ngữ và viết code DRY hơn.

---

## 📚 LÝ THUYẾT CỐT LÕI

### 1. Macros là gì?

**Macros là cách để viết code sinh ra code khác:**

```rust
// Macro thường dùng: println!, vec!, format!
fn main() {
    // println! là macro, không phải function
    println!("Hello, {}", "world");
    
    // vec! macro tạo Vector
    let v = vec![1, 2, 3];
    
    // Macro có thể có pattern matching
    match v {
        [first, ..] => println!("First: {}", first),
    }
}
```

### 2. Declarative Macros (macro_rules!)

**Macro đơn giản nhất, dùng pattern matching:**

```rust
// Định nghĩa macro
macro_rules! say_hello {
    () => {
        println!("Hello, world!");
    };
}

macro_rules! greet {
    ($name:expr) => {
        println!("Hello, {}!", $name);
    };
    
    ($name:expr, $greeting:expr) => {
        println!("{}, {}!", $greeting, $name);
    };
}

macro_rules! create_function {
    ($name:ident) => {
        fn $name() {
            println!("Function {} called", stringify!($name));
        }
    };
}

create_function!(foo);
create_function!(bar);

fn main() {
    say_hello!();  // Hello, world!
    greet!("Alice");  // Hello, Alice!
    greet!("Bob", "Hi");  // Hi, Bob!
    foo();  // Function foo called
    bar();  // Function bar called
}
```

**Macro với repetition:**

```rust
macro_rules! vec2 {
    ($($x:expr),*) => {
        {
            let mut temp_vec = Vec::new();
            $(
                temp_vec.push($x);
            )*
            temp_vec
        }
    };
}

macro_rules! sum {
    ($($x:expr),*) => {
        {
            let mut sum = 0;
            $(
                sum += $x;
            )*
            sum
        }
    };
}

macro_rules! hashmap {
    ($($key:expr => $value:expr),* $(,)?) => {
        {
            let mut map = std::collections::HashMap::new();
            $(
                map.insert($key, $value);
            )*
            map
        }
    };
}

fn main() {
    let v = vec2![1, 2, 3, 4];
    println!("{:?}", v);  // [1, 2, 3, 4]
    
    let total = sum![1, 2, 3, 4, 5];
    println!("Sum: {}", total);  // 15
    
    let map = hashmap![
        "name" => "Alice",
        "age" => 30,
    ];
    println!("{:?}", map);
}
```

### 3. Pattern trong Macros

**Các pattern thường dùng:**

```rust
macro_rules! debug {
    // Pattern cơ bản
    ($msg:expr) => {
        println!("[DEBUG] {}", $msg);
    };
    
    // Pattern với format
    ($format:expr, $($args:expr),*) => {
        println!("[DEBUG] {}", format!($format, $($args),*));
    };
    
    // Pattern với block
    ($msg:expr, $block:block) => {
        println!("[DEBUG] {}: Starting", $msg);
        let result = $block;
        println!("[DEBUG] {}: Completed", $msg);
        result
    };
}

macro_rules! assert_with_msg {
    ($cond:expr, $msg:expr) => {
        if !$cond {
            panic!("Assertion failed: {}", $msg);
        }
    };
}

fn main() {
    debug!("Simple message");
    debug!("Value: {}", 42);
    
    let result = debug!("Calculating", {
        let x = 10;
        let y = 20;
        x + y
    });
    println!("Result: {}", result);
    
    assert_with_msg!(2 + 2 == 4, "Math is broken!");
}
```

### 4. Token Tree và Fragments

**Các fragment specifiers:**

```rust
// item: function, struct, enum, etc.
// block: code block
// stmt: statement
// pat: pattern
// expr: expression
// ty: type
// ident: identifier
// path: path (e.g., std::collections::HashMap)
// tt: token tree
// meta: meta item (attributes)

macro_rules! create_struct {
    ($name:ident, $($field:ident: $ty:ty),*) => {
        struct $name {
            $($field: $ty),*
        }
        
        impl $name {
            fn new($($field: $ty),*) -> Self {
                Self {
                    $($field),*
                }
            }
            
            fn display(&self) -> String {
                format!("{} {{ {} }}", stringify!($name), 
                    vec![$(format!("{}: {:?}", stringify!($field), self.$field)),*].join(", "))
            }
        }
    };
}

create_struct!(Person, name: String, age: u32, email: String);

fn main() {
    let person = Person::new("Alice".to_string(), 30, "alice@email.com".to_string());
    println!("{}", person.display());
}
```

### 5. Procedural Macros (Giới thiệu)

**Procedural macros là macros mạnh hơn, dùng code Rust để xử lý AST:**

```rust
// Cần crate riêng
// Cargo.toml:
// [lib]
// proc-macro = true

// lib.rs:
// use proc_macro::TokenStream;
// 
// #[proc_macro]
// pub fn my_macro(input: TokenStream) -> TokenStream {
//     // Xử lý TokenStream và trả về code mới
// }
```

---

## 💻 THỰC HÀNH NGAY

**Tạo dự án: `cargo new bai14_macros`**

```rust
// 1. Macro cơ bản
macro_rules! log {
    ($level:expr, $msg:expr) => {
        println!("[{}] {}", $level, $msg);
    };
    
    ($level:expr, $format:expr, $($args:expr),*) => {
        println!("[{}] {}", $level, format!($format, $($args),*));
    };
}

// 2. Macro với repetition
macro_rules! make_tuple {
    ($($x:expr),*) => {
        ($($x),*)
    };
}

// 3. Macro tạo enum
macro_rules! define_enum {
    ($name:ident, $($variant:ident),*) => {
        #[derive(Debug, Clone, Copy, PartialEq)]
        enum $name {
            $($variant),*
        }
        
        impl $name {
            fn variants() -> Vec<Self> {
                vec![$($name::$variant),*]
            }
            
            fn name(&self) -> &'static str {
                match self {
                    $(Self::$variant => stringify!($variant)),*
                }
            }
        }
    };
}

// 4. Macro với repetition và optional
macro_rules! default_value {
    () => { 0 };
    ($value:expr) => { $value };
}

// 5. Macro với nhiều patterns
macro_rules! timed {
    ($block:block) => {{
        let start = std::time::Instant::now();
        let result = $block;
        let duration = start.elapsed();
        println!("Time: {:?}", duration);
        result
    }};
    
    ($name:expr, $block:block) => {{
        let start = std::time::Instant::now();
        let result = $block;
        let duration = start.elapsed();
        println!("{}: {:?}", $name, duration);
        result
    }};
}

// 6. Macro với type checking
macro_rules! assert_type {
    ($x:expr, $ty:ty) => {
        let _: $ty = $x;
    };
}

define_enum!(Color, Red, Green, Blue, Yellow);

fn main() {
    // log macro
    log!("INFO", "Application started");
    log!("DEBUG", "Value: {}", 42);
    log!("ERROR", "Something went wrong: {}", "Out of memory");
    
    // make_tuple
    let tuple = make_tuple![1, "hello", 3.14];
    println!("Tuple: {:?}", tuple);
    
    // enum macro
    let color = Color::Red;
    println!("Color: {:?}, Name: {}", color, color.name());
    println!("All variants: {:?}", Color::variants());
    
    // timed macro
    let result = timed!("Complex operation", {
        let mut sum = 0;
        for i in 0..1000000 {
            sum += i;
        }
        sum
    });
    println!("Result: {}", result);
    
    // assert_type
    assert_type!(5, i32);
    assert_type!("hello", &str);
    
    // default_value
    let x = default_value!();
    let y = default_value!(100);
    println!("x: {}, y: {}", x, y);
}

// 7. Macro trong impl
macro_rules! auto_debug {
    ($type:ty) => {
        impl std::fmt::Debug for $type {
            fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
                write!(f, concat!("Custom Debug for ", stringify!($type)))
            }
        }
    };
}

struct MyType {
    value: i32,
}

auto_debug!(MyType);

fn main() {
    let my_type = MyType { value: 42 };
    println!("{:?}", my_type);  // Custom Debug for MyType
}
```

---

## 📝 BÀI TẬP BẮT BUỘC

```rust
// Bài 1: Macro repeat
// Tạo macro repeat!($n, $block) 
// Lặp block $n lần
// Ví dụ: repeat!(3, println!("Hello"));

// Bài 2: Macro for struct builder
// Tạo macro builder! cho struct
// Ví dụ: builder!(Person, name: String, age: u32)
// Sinh code với method set_name, set_age, build()

// Bài 3: Macro for test cases
// Tạo macro test_cases!($name:ident, $($input:expr => $expected:expr),*)
// Sinh code test với nhiều test cases

// Bài 4: Macro for logging
// Tạo macro trace! với log levels
// Có thể bật/tắt theo compile time (debug/release)
// Format: [LEVEL] file:line - message

// Bài 5: Macro for validation
// Tạo macro validate! {
//     field: condition => error_message
// }
// Ví dụ: validate! {
//     age: age >= 0 => "Age cannot be negative",
//     age: age <= 150 => "Age too high"
// }
// Sinh code kiểm tra và return Vec<String> errors
```

---

## 🎯 LƯU Ý QUAN TRỌNG

| Khái niệm | Cú pháp | Sử dụng |
|-----------|---------|----------|
| **macro_rules!** | `macro_rules! name { ... }` | Declarative macros |
| **Pattern matching** | `($pattern) => { ... }` | Match syntax |
| **Repetition** | `$($x:expr),*` | Lặp nhiều lần |
| **Fragment specifier** | `expr`, `ident`, `ty`, `block` | Kiểu dữ liệu trong pattern |
| **Token tree** | `tt` | Bất kỳ token nào |

---

## ⚡ MẸO HAY

1. **`stringify!`** - chuyển token thành string
2. **`concat!`** - nối strings
3. **`include_str!`** - include file content
4. **`env!`** - đọc environment variable
5. **`option_env!`** - đọc env variable (Option)
6. **`cfg!`** - compile-time configuration

---

## 🔥 BÀI TẬP NÂNG CAO

```rust
// Tạo DSL (Domain Specific Language) cho REST API
// 1. Macro route! để define API endpoints
// route! {
//     GET "/users" => get_users,
//     POST "/users" => create_user,
//     GET "/users/:id" => get_user,
//     PUT "/users/:id" => update_user,
//     DELETE "/users/:id" => delete_user,
// }

// 2. Sinh code cho:
// - Router setup với axum/warp
// - Request/Response structs
// - Validation
// - Documentation (OpenAPI)

// 3. Thêm middleware support
// 4. Error handling tự động
// 5. Type-safe parameters (path, query, body)

// Bonus: Tạo macro thông minh hơn với proc-macros
// Sử dụng syn và quote để parse và generate code
```

---

## ✅ CHECKLIST BÀI 14

- [ ] Hiểu macro là gì và khi nào dùng
- [ ] Biết viết declarative macros với macro_rules!
- [ ] Sử dụng pattern matching trong macros
- [ ] Hiểu repetition syntax
- [ ] Biết các fragment specifiers
- [ ] Biết procedual macros (concept)
- [ ] Làm xong 5 bài tập cơ bản
- [ ] Thử bài tập nâng cao

---

**Hoàn thành bài tập, chia sẻ code để tôi review!**

Bài tiếp theo: **Bài 15 - Testing và Benchmarking** - đảm bảo code của bạn luôn đúng! 🧪