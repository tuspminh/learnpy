# Rust Professional 2026

## Giai đoạn 1 — Rust Foundation

## Buổi 7 — Formatting Output Deep Dive

> **Mục tiêu**

Sau buổi này bạn sẽ hiểu sâu hệ thống output và formatting của Rust, đặc biệt là cơ chế phía sau `println!`.

Chúng ta sẽ học:

* `print!`, `println!`
* `eprint!`, `eprintln!`
* Placeholder `{}`.
* Positional arguments.
* Named arguments.
* Format specifiers.
* Số nguyên, số thực.
* Căn lề và padding.
* `Debug` và `Display`.
* `{:?}`, `{:#?}`.
* Tự implement `Display`.
* Tự implement `Debug`.
* Mini project CLI hiển thị bảng dữ liệu.

---

# 1. Output trong Rust

Rust có 4 macro output cơ bản:

```rust
print!
println!
eprint!
eprintln!
```

Có thể hình dung:

```text
                    Output
                      │
          ┌───────────┴───────────┐
          │                       │
       stdout                  stderr
          │                       │
    print! / println!       eprint! / eprintln!
```

---

# 2. `print!`

```rust
fn main() {
    print!("Hello");
    print!(" Rust");
}
```

Kết quả:

```text
Hello Rust
```

`print!` **không tự động xuống dòng**.

---

# 3. `println!`

```rust
fn main() {
    println!("Hello");
    println!("Rust");
}
```

Kết quả:

```text
Hello
Rust
```

`println!` tương đương với:

```text
print + newline
```

---

# 4. Format Placeholder

Cách cơ bản:

```rust
fn main() {
    let name = "Alice";
    let age = 20;

    println!("Name: {}", name);
    println!("Age: {}", age);
}
```

Output:

```text
Name: Alice
Age: 20
```

---

# 5. Inline Arguments

Rust có cú pháp rất tiện:

```rust
fn main() {
    let name = "Alice";
    let age = 20;

    println!("Name: {name}");
    println!("Age: {age}");
}
```

Đây là style nên ưu tiên khi chỉ cần chèn biến đơn giản.

---

# 6. Nhiều biến

```rust
fn main() {
    let name = "Alice";
    let age = 20;
    let score = 9.5;

    println!(
        "Name: {name}, Age: {age}, Score: {score}"
    );
}
```

---

# 7. Positional Arguments

Bạn có thể chỉ rõ vị trí:

```rust
fn main() {
    println!("{0} {1} {0}", "Hello", "Rust");
}
```

Output:

```text
Hello Rust Hello
```

Index bắt đầu từ:

```text
0
```

---

# 8. Named Arguments

```rust
fn main() {
    println!(
        "{name} is {age} years old",
        name = "Alice",
        age = 20
    );
}
```

Output:

```text
Alice is 20 years old
```

---

# 9. Format số nguyên

```rust
fn main() {
    let n = 255;

    println!("Decimal: {n}");
    println!("Binary : {n:b}");
    println!("Octal  : {n:o}");
    println!("Hex    : {n:x}");
    println!("HEX    : {n:X}");
}
```

Output:

```text
Decimal: 255
Binary : 11111111
Octal  : 377
Hex    : ff
HEX    : FF
```

---

# 10. Binary

```rust
let n = 42;

println!("{n:b}");
```

Output:

```text
101010
```

---

# 11. Hexadecimal

```rust
let n = 255;

println!("{n:x}");
```

Output:

```text
ff
```

Hoặc:

```rust
println!("{n:X}");
```

Output:

```text
FF
```

---

# 12. Dấu `+`

Có thể hiển thị dấu của số:

```rust
fn main() {
    let x = 42;

    println!("{x:+}");
}
```

Output:

```text
+42
```

---

# 13. Padding bằng số 0

Ví dụ:

```rust
fn main() {
    let number = 42;

    println!("{number:05}");
}
```

Output:

```text
00042
```

Điều này rất hữu ích khi tạo:

* ID
* số thứ tự
* timestamp
* mã file

Ví dụ:

```rust
let chapter = 7;

println!("Chapter {:03}", chapter);
```

Output:

```text
Chapter 007
```

---

# 14. Độ rộng

```rust
fn main() {
    let name = "Rust";

    println!("{name:10}");
}
```

Output có độ rộng tối thiểu 10 ký tự.

---

# 15. Căn trái

```rust
fn main() {
    println!("{:<10}", "Rust");
}
```

Kết quả:

```text
Rust      
```

---

# 16. Căn phải

```rust
fn main() {
    println!("{:>10}", "Rust");
}
```

Kết quả:

```text
      Rust
```

---

# 17. Căn giữa

```rust
fn main() {
    println!("{:^10}", "Rust");
}
```

Kết quả gần như:

```text
   Rust   
```

---

# 18. Định dạng số thực

```rust
fn main() {
    let pi = 3.141592653589793;

    println!("{pi}");
}
```

Muốn giới hạn số chữ số sau dấu phẩy:

```rust
println!("{pi:.2}");
```

Output:

```text
3.14
```

---

# 19. Ví dụ tiền tệ

```rust
fn main() {
    let price = 1234567.891;

    println!("Price: {price:.2}");
}
```

Output:

```text
Price: 1234567.89
```

---

# 20. Scientific Notation

```rust
fn main() {
    let value = 1234567.89;

    println!("{value:e}");
}
```

Ví dụ:

```text
1.23456789e6
```

---

# 21. `Debug`

Đây là một khái niệm cực kỳ quan trọng.

Rust có hai format trait phổ biến:

```text
Display
Debug
```

`Debug` dùng để **debug dữ liệu**.

Cú pháp:

```rust
{:?}
```

Ví dụ:

```rust
fn main() {
    let values = [10, 20, 30];

    println!("{values:?}");
}
```

Output:

```text
[10, 20, 30]
```

---

# 22. Pretty Debug

Dùng:

```rust
{:#?}
```

Ví dụ:

```rust
fn main() {
    let values = [
        "Alice",
        "Bob",
        "Charlie",
    ];

    println!("{values:#?}");
}
```

Output:

```text
[
    "Alice",
    "Bob",
    "Charlie",
]
```

Rất hữu ích khi debug cấu trúc dữ liệu lớn.

---

# 23. Debug Struct

Ví dụ:

```rust
#[derive(Debug)]
struct Student {
    name: String,
    age: u8,
    score: f32,
}

fn main() {
    let student = Student {
        name: String::from("Alice"),
        age: 20,
        score: 9.5,
    };

    println!("{student:?}");
}
```

Output:

```text
Student { name: "Alice", age: 20, score: 9.5 }
```

Pretty:

```rust
println!("{student:#?}");
```

Output:

```text
Student {
    name: "Alice",
    age: 20,
    score: 9.5,
}
```

---

# 24. Tại sao phải `#[derive(Debug)]`?

Rust không tự động biết cách debug một struct do bạn tạo.

Bạn phải yêu cầu compiler sinh implementation:

```rust
#[derive(Debug)]
```

Sau này khi học Trait, bạn sẽ hiểu chính xác:

```text
#[derive(Debug)]
```

đã làm gì.

---

# 25. Display

`Display` dùng để biểu diễn dữ liệu **dành cho người dùng**.

Ví dụ:

```text
Display → User-facing
Debug   → Developer-facing
```

Đây là sự khác biệt rất quan trọng.

---

# 26. Tự implement Display

Ví dụ:

```rust
use std::fmt;

struct Student {
    name: String,
    age: u8,
}

impl fmt::Display for Student {
    fn fmt(
        &self,
        f: &mut fmt::Formatter<'_>,
    ) -> fmt::Result {
        write!(
            f,
            "{} ({})",
            self.name,
            self.age
        )
    }
}

fn main() {
    let student = Student {
        name: String::from("Alice"),
        age: 20,
    };

    println!("{student}");
}
```

Output:

```text
Alice (20)
```

---

# 27. `Display` vs `Debug`

| Trait        | Syntax  | Mục đích                |
| ------------ | ------- | ----------------------- |
| Display      | `{}`    | Hiển thị cho người dùng |
| Debug        | `{:?}`  | Debug                   |
| Pretty Debug | `{:#?}` | Debug đẹp               |

Ví dụ:

```rust
println!("{student}");
println!("{student:?}");
println!("{student:#?}");
```

---

# 28. Tại sao `println!` làm được điều này?

Đây là phần quan trọng về mặt kiến trúc.

Khi bạn viết:

```rust
println!("{student}");
```

Rust sử dụng formatting system và trait:

```text
Display
```

Compiler kiểm tra xem `Student` có implement `Display` hay không.

Nếu không có:

```text
error[E0277]
```

đại loại:

```text
`Student` doesn't implement `std::fmt::Display`
```

Đây là ví dụ đầu tiên cho thấy **Trait System** của Rust kiểm soát khả năng sử dụng kiểu dữ liệu.

Trait sẽ được học sâu hơn sau này.

---

# 29. `eprint!` và `eprintln!`

Đây là output cho:

```text
stderr
```

Ví dụ:

```rust
fn main() {
    eprintln!("Something went wrong!");
}
```

Thông thường:

```text
println! → stdout
eprintln! → stderr
```

---

# 30. Khi nào dùng stderr?

CLI chuyên nghiệp thường tách:

```text
stdout
    ↓
kết quả bình thường

stderr
    ↓
warning / error / diagnostic
```

Ví dụ:

```rust
fn main() {
    println!("Download completed.");

    eprintln!("Warning: file already exists.");
}
```

Điều này rất quan trọng khi output được pipe vào chương trình khác.

---

# 31. `print!` và Flush

Một điểm nâng cao:

`print!` không nhất thiết xuất hiện ngay trên terminal nếu output đang được buffer.

Ví dụ:

```rust
use std::io::{self, Write};

fn main() {
    print!("Loading...");

    io::stdout().flush().unwrap();

    // Công việc lâu...
}
```

`flush()` yêu cầu Rust đẩy dữ liệu đang buffer ra stdout.

Đây sẽ trở nên quan trọng khi chúng ta xây dựng:

* CLI progress bar
* interactive CLI
* downloader
* crawler
* terminal UI

---

# 32. Mini Project — Student Table

Bây giờ chúng ta xây dựng một chương trình CLI nhỏ.

```rust
#[derive(Debug)]
struct Student {
    id: u32,
    name: String,
    age: u8,
    score: f32,
}

fn main() {
    let students = [
        Student {
            id: 1,
            name: String::from("Alice"),
            age: 20,
            score: 9.5,
        },
        Student {
            id: 2,
            name: String::from("Bob"),
            age: 21,
            score: 8.75,
        },
        Student {
            id: 3,
            name: String::from("Charlie"),
            age: 19,
            score: 7.8,
        },
    ];

    println!(
        "{:<5} {:<12} {:<5} {:>8}",
        "ID",
        "Name",
        "Age",
        "Score"
    );

    println!("{}", "-".repeat(35));

    for student in students {
        println!(
            "{:<5} {:<12} {:<5} {:>8.2}",
            student.id,
            student.name,
            student.age,
            student.score
        );
    }
}
```

Kết quả:

```text
ID    Name         Age      Score
-----------------------------------
1     Alice        20         9.50
2     Bob          21         8.75
3     Charlie      19         7.80
```

Đây chính là ứng dụng thực tế của:

* alignment
* width
* precision
* formatting

---

# 33. Cải tiến bằng Display

Bây giờ tạo `Display`:

```rust
use std::fmt;

struct Student {
    id: u32,
    name: String,
    age: u8,
    score: f32,
}

impl fmt::Display for Student {
    fn fmt(
        &self,
        f: &mut fmt::Formatter<'_>,
    ) -> fmt::Result {
        write!(
            f,
            "{:<5} {:<12} {:<5} {:>8.2}",
            self.id,
            self.name,
            self.age,
            self.score
        )
    }
}

fn main() {
    let student = Student {
        id: 1,
        name: String::from("Alice"),
        age: 20,
        score: 9.5,
    };

    println!("{student}");
}
```

Bây giờ:

```rust
println!("{student}");
```

đã biết cách hiển thị `Student`.

---

# 34. Một kiến trúc rất quan trọng

Bạn có thể hình dung:

```text
println!
   │
   ▼
format_args!
   │
   ▼
Formatting Traits
   │
   ├── Display
   ├── Debug
   ├── Binary
   ├── LowerHex
   ├── UpperHex
   ├── Octal
   └── ...
```

Đây chính là một trong những nơi Rust sử dụng **Trait** rất mạnh.

---

# 35. Mini Project hoàn chỉnh — CLI Report

Tạo:

```bash
cargo new student_report
cd student_report
```

Thay `src/main.rs` bằng:

```rust
use std::fmt;

struct Student {
    id: u32,
    name: String,
    age: u8,
    score: f32,
}

impl fmt::Display for Student {
    fn fmt(
        &self,
        f: &mut fmt::Formatter<'_>,
    ) -> fmt::Result {
        write!(
            f,
            "{:<5} {:<15} {:<5} {:>8.2}",
            self.id,
            self.name,
            self.age,
            self.score
        )
    }
}

fn main() {
    let students = vec![
        Student {
            id: 1,
            name: String::from("Alice"),
            age: 20,
            score: 9.50,
        },
        Student {
            id: 2,
            name: String::from("Bob"),
            age: 21,
            score: 8.75,
        },
        Student {
            id: 3,
            name: String::from("Charlie"),
            age: 19,
            score: 7.80,
        },
    ];

    println!("================ STUDENTS ================");

    println!(
        "{:<5} {:<15} {:<5} {:>8}",
        "ID",
        "Name",
        "Age",
        "Score"
    );

    println!("{}", "-".repeat(40));

    for student in &students {
        println!("{student}");
    }

    println!("{}", "-".repeat(40));

    println!("Total students: {}", students.len());
}
```

Chạy:

```bash
cargo run
```

Bạn sẽ có một CLI report thực tế.

---

# 36. `Debug` trong quá trình phát triển

Trong quá trình phát triển, bạn sẽ thường dùng:

```rust
println!("{value:?}");
```

hoặc:

```rust
println!("{value:#?}");
```

Đặc biệt hữu ích với:

```text
Vec
HashMap
Option
Result
Struct
Enum
```

Ví dụ:

```rust
let data = vec![
    ("Alice", 20),
    ("Bob", 21),
];

println!("{data:#?}");
```

---

# 37. `dbg!` — công cụ debug cực kỳ hữu ích

Rust còn có macro:

```rust
dbg!
```

Ví dụ:

```rust
fn main() {
    let x = 10;
    let y = 20;

    let result = dbg!(x + y);

    println!("{result}");
}
```

`dbg!` in ra:

* file
* line
* expression
* giá trị

Ví dụ:

```text
[src/main.rs:5] x + y = 30
30
```

---

# 38. `dbg!` khác `println!`

`println!`:

```rust
println!("{x}");
```

Dành cho output của chương trình.

`dbg!`:

```rust
dbg!(x);
```

Dành cho developer debug.

Ngoài ra, `dbg!` **trả lại chính giá trị của expression**, nên có thể dùng giữa một biểu thức.

Ví dụ:

```rust
let result = dbg!(10 * 20);
```

---

# 39. Bài tập thực hành

## Bài 1 — Formatting

Cho:

```rust
let name = "Rust";
let version = 2024;
let score = 9.87654;
```

In:

```text
Name    : Rust
Version : 2024
Score   : 9.88
```

---

## Bài 2 — Number Formatting

Với:

```rust
let n = 255;
```

In:

```text
Decimal : 255
Binary  : 11111111
Octal   : 377
Hex     : FF
```

---

## Bài 3 — Padding

Với:

```rust
let chapter = 7;
```

In:

```text
Chapter 007
```

---

## Bài 4 — Debug

Tạo:

```rust
struct Book {
    title: String,
    pages: u32,
}
```

Thêm:

```rust
#[derive(Debug)]
```

Sau đó in bằng:

```rust
{:?}
```

và:

```rust
{:#?}
```

So sánh kết quả.

---

# 40. Bài tập nâng cao

Tạo:

```rust
struct Book {
    id: u32,
    title: String,
    author: String,
    pages: u32,
    price: f64,
}
```

Yêu cầu:

### `Debug`

Có thể debug:

```rust
println!("{book:#?}");
```

### `Display`

Hiển thị:

```text
ID    Title                Author          Pages      Price
-------------------------------------------------------------
1     Rust Programming     Steve           500        29.99
```

### CLI

Tạo ít nhất 3 cuốn sách và hiển thị thành bảng.

---

# 41. Kiến thức quan trọng cần ghi nhớ

Có 4 tầng bạn cần phân biệt:

```text
println!
   │
   ├── `{}`    → Display
   │
   └── `{:?}`  → Debug
```

Và:

```text
stdout
   │
   ├── print!
   └── println!

stderr
   │
   ├── eprint!
   └── eprintln!
```

---

# Tổng kết Buổi 7

Bạn đã học được:

### Output

```rust
print!
println!
eprint!
eprintln!
```

### Formatting

```rust
{}
{:?}
{:#?}
```

### Number Formatting

```rust
{:b}
{:o}
{:x}
{:X}
```

### Alignment

```rust
{:<10}
{:>10}
{:^10}
```

### Precision

```rust
{:.2}
```

### Padding

```rust
{:05}
```

### Debugging

```rust
dbg!(value)
```

### Trait

Bạn đã bắt đầu chạm vào một khái niệm cực kỳ quan trọng của Rust:

```rust
impl Display for MyType
```

Mặc dù chúng ta chưa học Trait chính thức, bạn đã thấy cách Rust sử dụng trait để xác định **một kiểu dữ liệu có thể được format như thế nào**.

---

# Kiến thức cần thuộc lòng

Nếu gặp:

```rust
println!("{value}");
```

hãy nghĩ:

```text
Display
```

Nếu gặp:

```rust
println!("{value:?}");
```

hãy nghĩ:

```text
Debug
```

Nếu gặp:

```rust
println!("{value:#?}");
```

hãy nghĩ:

```text
Pretty Debug
```

Nếu muốn debug nhanh:

```rust
dbg!(value);
```

Nếu cần in lỗi cho CLI:

```rust
eprintln!("Error: ...");
```

---

## Buổi 8 — Shadowing & Constants Deep Dive

Ở buổi tiếp theo chúng ta sẽ quay lại một chủ đề rất quan trọng từ Buổi 3 nhưng đào sâu hơn:

* Shadowing thực sự hoạt động như thế nào.
* Shadowing vs `mut`.
* Shadowing trong nested scope.
* Shadowing và thay đổi kiểu dữ liệu.
* `const`.
* `static`.
* `const` vs `let`.
* `const` vs `static`.
* Compile-time evaluation.
* Quy tắc đặt tên constant.
* Các pattern thực tế trong project Rust.
* Mini project cấu hình ứng dụng bằng `const` và `static`.

Sau Buổi 8, chúng ta sẽ bước sang **Control Flow**, nơi bạn bắt đầu xây dựng các chương trình Rust có logic thực sự.
