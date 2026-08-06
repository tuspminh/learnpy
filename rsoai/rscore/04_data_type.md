# Giáo trình Rust Professional 2026

# Giai đoạn 1 – Rust Foundation

# Buổi 4 – Data Types Deep Dive

> **Mục tiêu**

Sau buổi này bạn sẽ:

* Hiểu hệ thống kiểu dữ liệu của Rust.
* Biết kích thước bộ nhớ của từng kiểu dữ liệu.
* Phân biệt signed và unsigned integer.
* Hiểu `isize` và `usize`.
* Biết cách ép kiểu an toàn.
* Hiểu overflow và underflow.
* Sử dụng tuple và array thành thạo.
* Đọc được thông báo lỗi của compiler liên quan đến kiểu dữ liệu.

---

# 1. Hệ thống kiểu dữ liệu trong Rust

Rust là **statically typed language**.

Điều đó có nghĩa là **kiểu dữ liệu được xác định tại thời điểm biên dịch (compile time)**.

Ví dụ:

```rust
let age = 20;
```

Compiler suy luận:

```text
age: i32
```

Bạn không thể làm:

```rust
let age = 20;

age = "hello";
```

Lỗi:

```text
mismatched types
```

Rust sẽ từ chối biên dịch.

---

# 2. Hai nhóm kiểu dữ liệu

Rust chia thành hai nhóm lớn:

```text
Data Types
│
├── Scalar
│   ├── Integer
│   ├── Float
│   ├── Boolean
│   └── Character
│
└── Compound
    ├── Tuple
    └── Array
```

Trong buổi này chúng ta sẽ học toàn bộ nhóm trên.

---

# 3. Integer

Integer là số nguyên.

Rust hỗ trợ rất nhiều kiểu.

## Signed Integer

```text
i8
i16
i32
i64
i128
isize
```

Signed nghĩa là có:

```text
âm
0
dương
```

Ví dụ:

```rust
let temperature: i32 = -15;
```

---

## Unsigned Integer

```text
u8
u16
u32
u64
u128
usize
```

Unsigned:

```text
0
dương
```

Không có số âm.

Ví dụ:

```rust
let age: u8 = 25;
```

---

# 4. Kích thước bộ nhớ

| Kiểu | Bytes | Bit |
| ---- | ----: | --: |
| i8   |     1 |   8 |
| u8   |     1 |   8 |
| i16  |     2 |  16 |
| u16  |     2 |  16 |
| i32  |     4 |  32 |
| u32  |     4 |  32 |
| i64  |     8 |  64 |
| u64  |     8 |  64 |
| i128 |    16 | 128 |
| u128 |    16 | 128 |

---

# 5. Giá trị lớn nhất

Ví dụ:

```rust
fn main() {
    println!("{}", u8::MAX);
    println!("{}", u8::MIN);
}
```

Kết quả:

```text
255
0
```

Ví dụ:

```rust
fn main() {
    println!("{}", i8::MAX);
    println!("{}", i8::MIN);
}
```

Kết quả:

```text
127
-128
```

---

# 6. Tại sao i8 chỉ đến 127?

Một byte có:

```text
8 bit
```

Ví dụ:

```text
01111111
```

Bit đầu tiên là bit dấu.

Do đó:

```text
10000000
```

đại diện cho `-128`.

Đây là biểu diễn **Two's Complement**, sẽ được học sâu hơn ở phần quản lý bộ nhớ.

---

# 7. isize và usize

Đây là hai kiểu đặc biệt.

Kích thước của chúng phụ thuộc vào kiến trúc CPU.

Máy 64-bit:

```text
usize = 64 bit
```

Máy 32-bit:

```text
usize = 32 bit
```

---

Ví dụ:

```rust
let index: usize = 10;
```

Hầu hết API của Rust dùng:

```text
usize
```

Ví dụ:

```rust
let arr = [1, 2, 3];

println!("{}", arr[0]);
```

Ở đây:

```text
0
```

là `usize`.

---

# 8. Float

Rust có hai kiểu số thực.

```text
f32

f64
```

Thông thường:

```rust
let pi = 3.14;
```

Compiler suy luận:

```text
f64
```

---

Ví dụ:

```rust
fn main() {
    let x: f32 = 1.5;
    let y: f64 = 3.1415926535;

    println!("{x}");
    println!("{y}");
}
```

---

# 9. Boolean

Chỉ có hai giá trị.

```rust
true

false
```

Ví dụ:

```rust
fn main() {
    let active = true;
    let deleted = false;

    println!("{active}");
    println!("{deleted}");
}
```

---

# 10. Character

Khác với nhiều ngôn ngữ.

Rust dùng:

```rust
char
```

để biểu diễn **một Unicode Scalar Value**, không chỉ ký tự ASCII.

Ví dụ:

```rust
fn main() {
    let a = 'A';
    let b = 'Đ';
    let c = '😊';

    println!("{a}");
    println!("{b}");
    println!("{c}");
}
```

Output:

```text
A
Đ
😊
```

---

# 11. Tuple

Tuple là tập hợp nhiều giá trị có thể khác kiểu.

Ví dụ:

```rust
fn main() {
    let person = ("Alice", 20, true);

    println!("{:?}", person);
}
```

Kết quả:

```text
("Alice", 20, true)
```

---

## Truy cập

```rust
fn main() {
    let person = ("Alice", 20, true);

    println!("{}", person.0);
    println!("{}", person.1);
    println!("{}", person.2);
}
```

Output:

```text
Alice
20
true
```

---

## Destructuring

```rust
fn main() {
    let person = ("Bob", 25, false);

    let (name, age, active) = person;

    println!("{name}");
    println!("{age}");
    println!("{active}");
}
```

---

# 12. Array

Array có:

* cùng kiểu
* kích thước cố định

Ví dụ:

```rust
fn main() {
    let numbers = [10, 20, 30, 40];

    println!("{:?}", numbers);
}
```

---

## Truy cập

```rust
println!("{}", numbers[2]);
```

Kết quả

```text
30
```

---

# 13. Khai báo kiểu của Array

```rust
let numbers: [i32; 5] = [1,2,3,4,5];
```

Ý nghĩa

```text
[i32;5]
```

=

```text
5 phần tử

mỗi phần tử là i32
```

---

## Tạo mảng lặp

```rust
let zeros = [0; 10];
```

Kết quả:

```text
[0,0,0,0,0,0,0,0,0,0]
```

---

# 14. Overflow

Ví dụ:

```rust
fn main() {
    let x: u8 = 255;

    let y = x + 1;

    println!("{y}");
}
```

Ở chế độ Debug:

```text
thread 'main' panicked:
attempt to add with overflow
```

Trong Release:

```bash
cargo run --release
```

Giá trị có thể "quay vòng" (wrap) theo quy tắc của kiểu số nguyên nếu không bật các kiểm tra bổ sung.

---

# 15. Underflow

```rust
let x:u8 = 0;

let y = x - 1;
```

Debug:

```text
panic
```

---

# 16. Ép kiểu (`as`)

Ví dụ:

```rust
fn main() {
    let a: i32 = 10;

    let b = a as f64;

    println!("{b}");
}
```

Output:

```text
10
```

---

Ví dụ:

```rust
fn main() {
    let x = 65u8;

    let c = x as char;

    println!("{c}");
}
```

Output:

```text
A
```

---

# 17. Ví dụ tổng hợp

```rust
fn main() {
    let age: u8 = 20;

    let salary: i32 = 5000;

    let pi: f64 = 3.14;

    let active = true;

    let grade = 'A';

    println!("{age}");

    println!("{salary}");

    println!("{pi}");

    println!("{active}");

    println!("{grade}");
}
```

---

# 18. Mini Project – Student Profile

```rust
fn main() {
    let name = "Alice";
    let age: u8 = 20;
    let gpa: f32 = 3.75;
    let active = true;
    let grade = 'A';

    println!("====== Student ======");
    println!("Name   : {name}");
    println!("Age    : {age}");
    println!("GPA    : {gpa}");
    println!("Grade  : {grade}");
    println!("Active : {active}");
}
```

Kết quả:

```text
====== Student ======
Name   : Alice
Age    : 20
GPA    : 3.75
Grade  : A
Active : true
```

---

# Best Practices

## 1. Dùng `usize` cho chỉ số

```rust
let index: usize = 0;
```

Đây là kiểu mà hầu hết các API của thư viện chuẩn mong đợi khi truy cập mảng, vector và chuỗi.

---

## 2. Dùng kiểu nhỏ nhất nhưng đủ lớn

Ví dụ:

```rust
let month: u8 = 8;
```

thay vì:

```rust
let month: i128 = 8;
```

Tuy nhiên, đừng tối ưu quá sớm. Trong nhiều trường hợp, `i32` hoặc `usize` là lựa chọn hợp lý và dễ sử dụng.

---

## 3. Tránh lạm dụng `as`

Ép kiểu bằng `as` có thể làm mất dữ liệu:

```rust
let x: u16 = 300;
let y = x as u8; // chỉ giữ lại 8 bit thấp
```

Khi chuyển đổi có khả năng thất bại, hãy ưu tiên các API như `TryFrom` và `try_into()`. Chúng ta sẽ học kỹ ở phần Generic và Trait.

---

## 4. Dùng Tuple cho nhóm dữ liệu nhỏ

Tuple phù hợp để trả về 2–3 giá trị liên quan.

Nếu dữ liệu có ý nghĩa nghiệp vụ rõ ràng hoặc có nhiều trường, hãy dùng `struct` (sẽ học ở Buổi 31).

---

# Những lỗi người mới thường gặp

1. **Dùng `i32` để truy cập mảng** thay vì `usize`.
2. **Nhầm `char` với chuỗi (`&str`)**. `'A'` là `char`, còn `"A"` là chuỗi.
3. **Không để ý overflow/underflow** khi thao tác với kiểu số nhỏ như `u8`.
4. **Lạm dụng `as`** mà không kiểm tra khả năng mất dữ liệu.
5. **Nhầm Tuple với Array**: Tuple có thể chứa nhiều kiểu dữ liệu khác nhau, Array thì tất cả phần tử phải cùng kiểu.

---

# Bài tập thực hành

## Bài 1

Khai báo và in ra:

* `temperature: i16`
* `population: u64`
* `price: f64`
* `is_online: bool`
* `symbol: char`

---

## Bài 2

Tạo một tuple:

```text
(name, age, salary)
```

Sau đó:

* In từng phần tử bằng chỉ số (`.0`, `.1`, `.2`).
* Dùng destructuring để gán vào ba biến mới rồi in lại.

---

## Bài 3

Tạo mảng:

```rust
[10, 20, 30, 40, 50]
```

* In toàn bộ mảng.
* In phần tử đầu, cuối và phần tử ở giữa.

---

## Bài 4

Tạo mảng gồm 12 phần tử đều bằng `-1` bằng cú pháp lặp.

---

## Bài 5

Viết chương trình hiển thị thông tin một cuốn sách:

* Tên sách (`&str`)
* Năm xuất bản (`u16`)
* Giá (`f32`)
* Còn bán (`bool`)
* Mã phân loại (`char`)

In ra theo định dạng đẹp.

---

# Tổng kết

Trong buổi học này, bạn đã học được:

* Hệ thống kiểu dữ liệu cơ bản của Rust.
* Các kiểu số nguyên có dấu và không dấu.
* `isize` và `usize` cùng vai trò của chúng.
* Số thực (`f32`, `f64`), `bool`, `char`.
* Tuple và Array.
* Overflow, Underflow và cách Rust xử lý.
* Ép kiểu với `as` và những lưu ý quan trọng.

## Chuẩn bị cho buổi 5

Ở **Buổi 5 – Functions Deep Dive**, chúng ta sẽ học:

* Khai báo hàm (`fn`)
* Tham số và kiểu trả về
* Expression vs Statement
* Giá trị trả về không dùng `return`
* Hàm nhận và trả về nhiều giá trị
* Hàm lồng nhau và phạm vi
* Diverging function (`!`)
* Thực hành xây dựng một thư viện toán học nhỏ với nhiều hàm có thể kiểm thử bằng `cargo test`.

Đây là nền tảng quan trọng trước khi bước sang Control Flow và Ownership.
