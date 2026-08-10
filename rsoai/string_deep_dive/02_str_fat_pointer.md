# Rust String Deep Dive — Buổi 2

## `str` vs `&str` — Unsized Type, Slice và Fat Pointer

Ở buổi 1, ta đã có mental model:

```text
"hello"
   ↓
&'static str
```

Hôm nay chúng ta đào sâu vào câu hỏi:

> **`str` thực sự là gì? Tại sao ta gần như luôn thấy `&str` mà không thấy `str`?**

Đây là kiến thức nền tảng để hiểu ownership, slice, lifetime và memory layout trong Rust.

---

# 1. `str` và `&str` KHÔNG giống nhau

Đây là điều đầu tiên cần phân biệt.

```rust
str
```

là **một type**.

Còn:

```rust
&str
```

là **reference tới một `str`**.

Tương tự:

```rust
i32
```

và:

```rust
&i32
```

khác nhau.

Ví dụ:

```rust
let x: i32 = 10;
let y: &i32 = &x;
```

Tương tự về mặt khái niệm:

```rust
let text: &str = "hello";
```

Ở đây:

```text
str
↑
│
&str
```

`&str` là reference đến dữ liệu có kiểu `str`.

---

# 2. Vậy tại sao không viết?

Bạn có thể thử:

```rust
fn main() {
    let text: str = "hello";
}
```

Rust sẽ từ chối.

Lý do rất quan trọng:

> `str` là **DST — Dynamically Sized Type**.

Nói đơn giản:

```text
str
```

không có kích thước cố định tại compile time.

---

# 3. Rust cần biết kích thước của biến

Ví dụ:

```rust
let x: i32 = 10;
```

Compiler biết:

```text
i32 = 4 bytes
```

Do đó có thể hình dung:

```text
STACK

┌──────────────┐
│ x            │
│ 4 bytes      │
└──────────────┘
```

Nhưng:

```rust
str
```

có thể là:

```text
"Hi"
```

hoặc:

```text
"Hello"
```

hoặc:

```text
"Rust programming language"
```

Kích thước khác nhau.

```text
"Hi"       → 2 bytes
"Hello"    → 5 bytes
"Rust..."  → nhiều bytes
```

Vì vậy compiler không thể coi:

```rust
str
```

là một local variable có kích thước cố định.

---

# 4. Đây chính là DST

DST:

> Dynamically Sized Type

Một số DST quan trọng trong Rust:

```rust
str
[T]
dyn Trait
```

Trong đó:

```rust
str
```

là DST biểu diễn chuỗi UTF-8.

```rust
[T]
```

là slice của một mảng.

```rust
dyn Trait
```

là trait object.

Điểm chung:

> Compiler không biết kích thước cụ thể của chúng tại compile time.

---

# 5. Nhưng Rust vẫn cho chúng ta sử dụng `str`

Thông qua reference:

```rust
&str
```

Ví dụ:

```rust
let text: &str = "hello";
```

Tại đây compiler không cần biết:

```text
kích thước của str
```

để tạo biến `text`.

Nó chỉ cần biết kích thước của:

```text
&str
```

và reference này có kích thước cố định.

---

# 6. `&str` là một fat pointer

Đây là kiến thức rất quan trọng.

Một:

```rust
&i32
```

thường có thể hình dung là:

```text
pointer
```

Nhưng:

```rust
&str
```

có thêm thông tin về độ dài.

Mental model:

```text
&str

┌─────────────────┐
│ pointer         │
├─────────────────┤
│ length          │
└─────────────────┘
```

Hai thành phần:

```text
pointer
length
```

Vì vậy `&str` thường được gọi là:

> **fat pointer**

---

# 7. Ví dụ

```rust
let text = "hello";
```

Ta có thể hình dung:

```text
text: &str

┌────────────────────┐
│ pointer ───────────┼──────┐
│ length = 5         │      │
└────────────────────┘      │
                            ▼
                     ┌─────────────┐
                     │ h e l l o   │
                     └─────────────┘
```

`text` không chứa trực tiếp:

```text
h e l l o
```

Nó chứa thông tin:

```text
địa chỉ bắt đầu
độ dài
```

---

# 8. Vì sao cần length?

Bởi vì pointer chỉ cho biết:

> dữ liệu bắt đầu ở đâu?

Nó không cho biết:

> dữ liệu kết thúc ở đâu?

Ví dụ:

```text
memory

0x1000 → h
0x1001 → e
0x1002 → l
0x1003 → l
0x1004 → o
0x1005 → ?
```

Nếu chỉ có:

```text
pointer = 0x1000
```

thì Rust không biết string dài bao nhiêu.

Do đó:

```text
&str
=
pointer + length
```

---

# 9. Đây cũng chính là lý do `str` có thể là slice

Ví dụ:

```rust
let text = String::from("Hello Rust");
```

Ta có thể tạo:

```rust
let slice = &text[0..5];
```

Khi đó:

```text
String
┌──────────────────────┐
│ H e l l o   R u s t  │
└──────────────────────┘
  ↑
  │
  └── slice
```

`slice` có:

```text
pointer → H
length  → 5
```

Nó không tạo ra một String mới.

---

# 10. Slice không sở hữu dữ liệu

Đây là điều cực kỳ quan trọng.

```rust
let text = String::from("Hello Rust");

let part = &text[0..5];
```

`text`:

```text
owns data
```

`part`:

```text
borrows data
```

Hình dung:

```text
String
┌────────────────────────┐
│ Hello Rust             │
└────────────────────────┘
  ↑
  │
  │ pointer
  │
&str
┌──────────────┐
│ ptr │ len=5  │
└──────────────┘
```

---

# 11. String literal cũng là `&str`

Bây giờ quay lại:

```rust
let text = "hello";
```

Compiler suy luận:

```rust
let text: &str = "hello";
```

Nhưng chính xác hơn:

```rust
let text: &'static str = "hello";
```

Vì string literal có lifetime `'static`.

---

# 12. `&str` có thể trỏ tới nhiều nguồn dữ liệu

Đây là điểm rất hay.

### Trường hợp 1 — String literal

```rust
let a: &str = "hello";
```

### Trường hợp 2 — String

```rust
let s = String::from("hello");

let b: &str = &s;
```

### Trường hợp 3 — String slice

```rust
let s = String::from("hello world");

let c: &str = &s[0..5];
```

Cả ba đều là:

```text
&str
```

nhưng nguồn dữ liệu khác nhau.

---

# 13. Một API có thể nhận cả ba

Ví dụ:

```rust
fn print_text(text: &str) {
    println!("{text}");
}
```

Có thể gọi:

```rust
print_text("hello");
```

Hoặc:

```rust
let s = String::from("hello");

print_text(&s);
```

Hoặc:

```rust
let s = String::from("hello world");

print_text(&s[0..5]);
```

Đây là lý do:

> Khi function chỉ cần đọc string, `&str` thường là lựa chọn rất tốt.

---

# 14. `&String` và `&str`

Ta có:

```rust
let s = String::from("hello");
```

Có thể:

```rust
let a: &String = &s;
```

hoặc:

```rust
let b: &str = &s;
```

Nhưng khi viết API:

```rust
fn foo(s: &String)
```

thường kém linh hoạt hơn:

```rust
fn foo(s: &str)
```

Vì:

```rust
&str
```

có thể nhận:

```text
string literal
String
String slice
```

Còn:

```rust
&String
```

chủ yếu yêu cầu reference tới một `String`.

---

# 15. Deref coercion

Tại sao code này hoạt động?

```rust
fn print_text(text: &str) {
    println!("{text}");
}

fn main() {
    let s = String::from("Hello");

    print_text(&s);
}
```

Ta truyền:

```rust
&s
```

có type:

```rust
&String
```

nhưng function cần:

```rust
&str
```

Rust thực hiện **deref coercion**:

```text
&String
   ↓
&str
```

Điều này giúp API Rust rất tiện.

---

# 16. `String` thực chất liên quan trực tiếp đến `str`

Một mental model tốt:

```text
String
   │
   │ owns
   ▼
UTF-8 bytes

&str
   │
   │ borrows
   ▼
UTF-8 bytes
```

Ví dụ:

```rust
let s = String::from("Rust");
let slice = &s[..];
```

Ta có:

```text
s
┌───────────────────────┐
│ pointer               │
│ length                │
│ capacity              │
└───────────────────────┘
          │
          ▼
      heap memory
      ┌──────────┐
      │ R u s t  │
      └──────────┘

slice: &str
┌───────────────────────┐
│ pointer               │──────┐
│ length = 4            │      │
└───────────────────────┘      │
                               ▼
                           same memory
```

---

# 17. `String` và `&str` có cùng memory không?

Ví dụ:

```rust
let s = String::from("hello");
let slice = &s[..];
```

Có.

`slice` nhìn vào chính vùng memory mà `String` đang sở hữu.

Không có copy `"hello"`.

```text
String
   │
   └──────────┐
              ▼
          ┌─────────┐
          │ hello   │
          └─────────┘
              ▲
              │
             &str
```

---

# 18. Một ví dụ ownership cực kỳ quan trọng

```rust
fn main() {
    let s = String::from("hello");

    let slice = &s[..];

    println!("{s}");
    println!("{slice}");
}
```

Hợp lệ.

Vì:

```text
s
│
└── owner

slice
│
└── borrower
```

`slice` không lấy ownership của `s`.

---

# 19. Borrow checker bảo vệ slice

Ví dụ:

```rust
fn main() {
    let mut s = String::from("hello");

    let slice = &s[..];

    s.push_str(" world");

    println!("{slice}");
}
```

Code này sẽ bị lỗi.

Tại sao?

Vì:

```text
slice
   │
   └── immutable borrow
```

đang tồn tại trong khi:

```text
s.push_str(...)
```

cần mutable borrow.

Rust không cho:

```text
immutable borrow
+
mutable borrow
```

cùng tồn tại theo cách có thể gây vấn đề.

---

# 20. Đây chính là sức mạnh của `&str`

`&str` không chỉ là:

```text
"chuỗi"
```

Nó là một **view** vào dữ liệu string.

Có thể hình dung:

```text
Owner
┌───────────────────────────────┐
│ Hello Rust Programming        │
└───────────────────────────────┘
      ▲              ▲
      │              │
      │              │
   &str             &str
   "Hello"          "Rust"
```

Một String có thể có nhiều slice:

```rust
let s = String::from("Hello Rust Programming");

let a = &s[0..5];
let b = &s[6..10];
let c = &s[11..22];
```

Tất cả đều:

```text
borrow
```

chứ không:

```text
own
```

---

# 21. Nhưng có một vấn đề: UTF-8

Đoạn này cực kỳ quan trọng và sẽ là chủ đề sâu ở các buổi sau.

Bạn **không được** tùy tiện slice string theo character.

Ví dụ:

```rust
let s = "Xin chào";
```

Không thể giả định:

```rust
&s[0..3]
```

là ba ký tự.

Bởi vì Rust String sử dụng:

```text
UTF-8
```

Ví dụ:

```text
X       → 1 byte
i       → 1 byte
n       → 1 byte
chào    → nhiều byte
```

Rust slice theo **byte index**, không phải character index.

Chúng ta sẽ đào sâu phần này ở buổi UTF-8.

---

# 22. `str` là một primitive DST

Một điểm nâng cao:

```rust
str
```

không phải struct:

```rust
struct str { ... }
```

Nó là một **primitive dynamically sized type**.

Tương tự:

```rust
[T]
```

là slice type.

Ví dụ:

```rust
let numbers = [10, 20, 30, 40];

let slice: &[i32] = &numbers[..];
```

Ta thấy pattern:

```text
[i32]
  ↓
&[i32]
```

và:

```text
str
 ↓
&str
```

Rất giống nhau.

---

# 23. So sánh `&str` và `&[T]`

Ví dụ:

```rust
let numbers = [1, 2, 3, 4];

let slice = &numbers[..];
```

`slice`:

```text
&[i32]
```

có:

```text
pointer + length
```

Tương tự:

```rust
let text = "hello";
```

`text`:

```text
&str
```

cũng có:

```text
pointer + length
```

Mental model:

```text
&[T]
┌──────────────┐
│ pointer      │
│ length       │
└──────────────┘

&str
┌──────────────┐
│ pointer      │
│ length       │
└──────────────┘
```

---

# 24. `str` không phải `String`

Đây là lỗi khái niệm rất phổ biến.

Sai mental model:

```text
str = String
```

Đúng hơn:

```text
String
=
owned growable string

str
=
string slice type
```

Và:

```text
&str
=
reference to str
```

---

# 25. Memory model tổng hợp

Ví dụ:

```rust
fn main() {
    let s = String::from("Hello Rust");

    let a = &s[..5];
    let b = &s[6..];

    println!("{a}");
    println!("{b}");
}
```

Mental model:

```text
STACK

s
┌────────────────────────┐
│ ptr ───────────────────┼────┐
│ len = 10               │    │
│ capacity               │    │
└────────────────────────┘    │
                              │
a                             │
┌────────────────────────┐    │
│ ptr ───────────────────┼────┤
│ len = 5                 │    │
└────────────────────────┘    │
                              │
b                             │
┌────────────────────────┐    │
│ ptr ───────────────────┼────┤
│ len = 4                 │    │
└────────────────────────┘    │
                              │
                              ▼
HEAP

┌──────────────────────┐
│ H e l l o   R u s t  │
└──────────────────────┘
```

Ba object:

```text
s
a
b
```

đều liên quan đến cùng vùng dữ liệu.

Nhưng ownership chỉ thuộc về:

```text
s
```

---

# 26. Một nguyên tắc thiết kế API

Nếu function chỉ cần **đọc string**:

```rust
fn process(name: &str) {
    // ...
}
```

thường tốt hơn:

```rust
fn process(name: &String) {
    // ...
}
```

Nếu function cần **sở hữu dữ liệu**:

```rust
fn process(name: String) {
    // ...
}
```

Nếu function cần **tạo và trả về một String mới**:

```rust
fn create_name() -> String {
    String::from("Rust")
}
```

Nếu trả về một string literal cố định:

```rust
fn language() -> &'static str {
    "Rust"
}
```

---

# 27. Bảng tổng kết

| Type          | Ownership      | Size                 | Mutable? | Mục đích                   |
| ------------- | -------------- | -------------------- | -------- | -------------------------- |
| `str`         | —              | DST                  | —        | string slice type          |
| `&str`        | borrow         | fixed-size reference | không    | đọc/view string            |
| `String`      | own            | sized                | có       | dynamic string             |
| `&String`     | borrow         | fixed-size reference | không    | borrow một `String` cụ thể |
| `&mut String` | mutable borrow | fixed-size reference | có       | sửa `String`               |

---

# 28. Mental model cần thuộc

Hãy ghi nhớ sơ đồ này:

```text
                  UTF-8 data
                      │
          ┌───────────┴───────────┐
          │                       │
       String                     str
       owns                       DST
          │                       │
          │                       │
          ▼                       ▼
       &String                   &str
          │                       │
          └────── deref ──────────┘
```

Và:

```text
&str
 =
 pointer + length
```

---

# Bài tập Buổi 2

### Bài 1

Giải thích tại sao đoạn này không hợp lệ:

```rust
let text: str = "hello";
```

---

### Bài 2

Giải thích sự khác nhau:

```rust
str
&str
String
&String
```

---

### Bài 3

Đoán kết quả:

```rust
fn show(s: &str) {
    println!("{s}");
}

fn main() {
    let a = "Hello";
    let b = String::from("Rust");

    show(a);
    show(&b);
}
```

Tại sao cả hai đều hoạt động?

---

### Bài 4 — Ownership

Giải thích ownership và borrowing trong:

```rust
let s = String::from("Hello Rust");

let a = &s[0..5];
let b = &s[6..];

println!("{a}");
println!("{b}");
```

---

### Bài 5 — Deep Dive

Hãy tự vẽ memory model cho:

```rust
fn main() {
    let s = String::from("Hello Rust");

    let a = &s[..5];
    let b = &s[6..];

    println!("{a}");
    println!("{b}");
}
```

Phải thể hiện được:

```text
Stack
Heap
String
&str
pointer
length
ownership
borrow
```

---

## Kiến thức cốt lõi của Buổi 2

Nếu chỉ nhớ 5 điều:

```text
1. str ≠ String

2. str là DST (Dynamically Sized Type)

3. &str là reference tới str

4. &str có thể hình dung như:
   pointer + length

5. String owns data,
   &str chỉ borrow/view data
```

**Buổi 3** chúng ta sẽ đi sâu vào phần rất thú vị: **String Literal nằm chính xác ở đâu trong memory, `&'static str` hoạt động thế nào, read-only data, compile time vs runtime, và tại sao literal có thể được trả về từ function mà không gây dangling reference.**
