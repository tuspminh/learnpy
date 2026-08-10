Chắc chắn. Với Rust, **String / `str` / `&str` / string literal** là một trong những chủ đề rất quan trọng vì nó liên quan trực tiếp đến **ownership, borrowing, lifetime, UTF-8, memory layout và slice**.

Tôi sẽ dạy theo kiểu **deep dive**, không chỉ học cú pháp.

# Rust Deep Dive — String & String Literal

## Roadmap

Ta sẽ chia chủ đề thành các buổi:

### Phần I — String Literal & `str`

1. **Buổi 1 — String Literal (`"hello"`)**
2. **Buổi 2 — `str` và `&str`**
3. **Buổi 3 — String Literal nằm ở đâu trong memory?**
4. **Buổi 4 — UTF-8 và String**
5. **Buổi 5 — Escape Sequence**
6. **Buổi 6 — Raw String `r"..."`**
7. **Buổi 7 — Byte String `b"..."`**
8. **Buổi 8 — `char` vs `&str`**
9. **Buổi 9 — String Slice**
10. **Buổi 10 — Lifetime của String Literal**

### Phần II — `String`

11. `String` là gì?
12. `String::from`
13. `to_string()`
14. `push`
15. `push_str`
16. `+` và `format!`
17. Capacity / Length
18. Heap allocation
19. Ownership với `String`
20. `String` vs `&str`

### Phần III — Deep Dive

21. UTF-8 representation
22. `len()` thực sự trả về gì?
23. Indexing String
24. `chars()`
25. `bytes()`
26. `char_indices()`
27. slicing UTF-8
28. `String` memory layout
29. `&str` fat pointer
30. Lifetime + string literal
31. `static`
32. `Cow<str>`
33. API design với `String` / `&str`
34. Performance
35. Mini Project

---

# Buổi 1 — String Literal

Trước tiên hãy quên `String` trong vài phút.

Rust có một thứ rất cơ bản:

```rust
"hello"
```

Đây gọi là:

> **String literal**

Ví dụ:

```rust
fn main() {
    let name = "Rust";

    println!("{}", name);
}
```

Ta có:

```text
"Rust"
  ↓
string literal
```

Điểm cực kỳ quan trọng:

```rust
"Rust"
```

**không phải `String`.**

Nó cũng không phải một chuỗi mutable.

---

# 1. Type của `"hello"` là gì?

Xét:

```rust
let text = "hello";
```

Rust suy luận:

```rust
text: &str
```

Tức là:

```rust
let text: &str = "hello";
```

Ta có thể viết:

```rust
fn main() {
    let text: &str = "hello";

    println!("{}", text);
}
```

Đây là một trong những kiến thức nền tảng nhất của Rust.

---

# 2. `&str` nghĩa là gì?

Tạm thời hiểu:

```rust
&str
```

là:

> một **reference đến một string slice**.

Ví dụ:

```rust
let text: &str = "hello";
```

Có thể hình dung:

```text
text
 │
 ▼
┌─────────────────┐
│ h e l l o       │
└─────────────────┘
```

`text` không sở hữu dữ liệu `"hello"`.

Nó chỉ **trỏ tới dữ liệu**.

---

# 3. String literal có ownership không?

Đây là điểm rất quan trọng.

```rust
let a = "hello";
```

Bạn không cần:

```rust
drop(a);
```

theo nghĩa quản lý vùng nhớ heap như với `String`.

String literal được compiler đưa vào binary của chương trình.

Ví dụ:

```rust
fn main() {
    let a = "hello";
    let b = a;

    println!("{}", a);
    println!("{}", b);
}
```

Code này hợp lệ.

Tại sao?

Bởi vì:

```rust
a
```

không sở hữu một vùng memory heap chứa `"hello"`.

---

# 4. String literal có thể copy

Ví dụ:

```rust
fn main() {
    let a = "hello";
    let b = a;

    println!("a = {}", a);
    println!("b = {}", b);
}
```

Output:

```text
a = hello
b = hello
```

Trong khi với `String`:

```rust
fn main() {
    let a = String::from("hello");
    let b = a;

    println!("{}", a);
}
```

Compiler báo lỗi vì:

```text
a
│
└── moved → b
```

Nhưng:

```rust
let a = "hello";
let b = a;
```

thì:

```text
a ─────┐
       │
       ▼
    "hello"

b ─────┘
```

Hai biến có thể cùng tham chiếu đến cùng dữ liệu.

---

# 5. String literal có lifetime đặc biệt

String literal:

```rust
"hello"
```

có lifetime:

```rust
'static
```

Tức là:

```rust
&'static str
```

Có thể hiểu:

```rust
"hello"
```

thực chất có thể xem như:

```rust
&'static str
```

Ví dụ:

```rust
fn get_name() -> &'static str {
    "Rust"
}
```

Hoàn toàn hợp lệ.

Tại sao function có thể trả về reference?

Bởi vì `"Rust"` tồn tại trong toàn bộ lifetime của chương trình.

---

# 6. `'static` ở đây nghĩa là gì?

Đây là một điểm cần hiểu chính xác.

```rust
&'static str
```

nghĩa là:

> reference này có thể tồn tại trong toàn bộ thời gian chương trình chạy.

Ví dụ:

```rust
fn language() -> &'static str {
    "Rust"
}
```

Ta có:

```text
Program Start
     │
     ▼
   "Rust"
     │
     │
     │
     ▼
Program End
```

Dữ liệu literal tồn tại xuyên suốt chương trình.

---

# 7. String literal được lưu ở đâu?

Ví dụ:

```rust
let language = "Rust";
```

Một cách hình dung đơn giản:

```text
STACK
┌──────────────────┐
│ language         │
│ pointer          │──────┐
│ length = 4       │      │
└──────────────────┘      │
                          ▼
READ-ONLY DATA / BINARY
┌────────────────────────────┐
│ R │ u │ s │ t              │
└────────────────────────────┘
```

Đây là mô hình khái niệm hữu ích.

Điểm cần nhớ:

```text
String literal
    ↓
compile-time known
    ↓
embedded in executable
    ↓
lifetime = 'static
```

---

# 8. String literal là immutable

Bạn không thể:

```rust
fn main() {
    let text = "hello";

    text.push('!');
}
```

Không được.

Vì `text` có type:

```rust
&str
```

và `&str` không cung cấp API để mutate nội dung underlying string literal.

Bạn cũng không thể:

```rust
let mut text = "hello";

text.push('!');
```

`mut` ở đây **không biến `&str` thành mutable string**.

```rust
let mut text = "hello";
```

chỉ có nghĩa:

> biến `text` có thể được gán sang một `&str` khác.

Ví dụ:

```rust
fn main() {
    let mut text = "hello";

    text = "world";

    println!("{}", text);
}
```

Hợp lệ.

Nhưng:

```rust
text.push('!');
```

không hợp lệ.

---

# 9. `mut` khác với mutable data

Đây là lỗi người mới Rust rất hay mắc.

```rust
let mut text = "hello";
```

Không có nghĩa:

```text
"hello"
   ↑
mutable
```

Mà là:

```text
text
 │
 ├── có thể thay đổi reference
 │
 ▼
"hello"
```

Ví dụ:

```rust
let mut text = "hello";

text = "Rust";
text = "world";
```

`text` thay đổi nơi nó trỏ tới.

Dữ liệu literal không bị thay đổi.

---

# 10. String literal có thể nhiều dòng

Rust hỗ trợ:

```rust
let text = "hello
world";
```

Ví dụ:

```rust
fn main() {
    let text = "Hello
Rust";

    println!("{}", text);
}
```

Output:

```text
Hello
Rust
```

---

# 11. Escape sequence

String literal hỗ trợ escape.

Ví dụ:

```rust
let text = "Hello\nRust";
```

Output:

```text
Hello
Rust
```

Một số escape quan trọng:

| Syntax | Ý nghĩa         |
| ------ | --------------- |
| `\n`   | newline         |
| `\r`   | carriage return |
| `\t`   | tab             |
| `\\`   | `\`             |
| `\"`   | `"`             |
| `\'`   | `'`             |
| `\0`   | null            |
| `\xNN` | byte hex        |

Ví dụ:

```rust
fn main() {
    println!("Hello\nRust");
    println!("Hello\tRust");
    println!("She said: \"Hello\"");
}
```

---

# 12. Unicode trong string literal

Rust string literal là UTF-8.

Ví dụ:

```rust
let a = "Xin chào";
let b = "こんにちは";
let c = "你好";
let d = "🚀";
```

Tất cả đều hợp lệ.

```rust
fn main() {
    let a = "Xin chào";
    let b = "こんにちは";
    let c = "你好";
    let d = "🚀";

    println!("{}", a);
    println!("{}", b);
    println!("{}", c);
    println!("{}", d);
}
```

Rust xử lý string dưới dạng UTF-8.

Điều này cực kỳ quan trọng khi sau này học:

```rust
.len()
.chars()
.bytes()
.char_indices()
```

---

# 13. `&str` không chỉ dùng cho literal

Đây là điểm cực kỳ quan trọng.

Ta có:

```rust
let a = "hello";
```

`a` là:

```rust
&str
```

Nhưng `&str` cũng có thể được tạo từ `String`.

```rust
let s = String::from("hello");

let slice: &str = &s;
```

Ta có:

```text
String
┌───────────────┐
│ hello         │
└───────────────┘
       ▲
       │
       │
     &str
```

Do đó:

```text
"hello"
   ↓
 &str

String
   ↓
 &String
   ↓
 &str
```

Đây là nền tảng của việc thiết kế API Rust.

---

# 14. So sánh ba thứ

Hãy nhớ bảng này:

| Code                    | Type           |
| ----------------------- | -------------- |
| `"hello"`               | `&'static str` |
| `let s: &str`           | `&str`         |
| `String::from("hello")` | `String`       |

Ví dụ:

```rust
let a = "hello";

let b: &str = "world";

let c = String::from("Rust");
```

Ta có:

```text
a → &'static str
b → &str
c → String
```

---

# 15. Tại sao Rust có `String` và `&str`?

Đây là câu hỏi rất quan trọng.

### `String`

Dùng khi bạn cần:

* ownership
* heap allocation
* grow
* mutate
* lưu trữ dynamic string

Ví dụ:

```rust
let mut name = String::from("Rust");

name.push_str(" Programming");
```

### `&str`

Dùng khi bạn chỉ cần:

* đọc
* borrow
* string slice
* không cần sở hữu dữ liệu

Ví dụ:

```rust
fn print_name(name: &str) {
    println!("{}", name);
}
```

Có thể truyền:

```rust
print_name("Rust");
```

hoặc:

```rust
let name = String::from("Rust");

print_name(&name);
```

Đây chính là sức mạnh của borrowing.

---

# 16. Ví dụ quan trọng nhất

```rust
fn print_text(text: &str) {
    println!("{}", text);
}

fn main() {
    let a = "Hello";

    let b = String::from("Rust");

    print_text(a);
    print_text(&b);
}
```

Ở đây:

```text
"Hello"
   │
   ▼
  &str
   │
   ▼
print_text()
```

và:

```text
String
   │
   ▼
 &String
   │
   ▼
 &str
   │
   ▼
print_text()
```

Rust cho phép coercion:

```text
&String → &str
```

---

# 17. Một mental model rất quan trọng

Từ bây giờ hãy suy nghĩ:

```text
String
```

là:

> **owned, growable UTF-8 string**

còn:

```text
&str
```

là:

> **borrowed view vào UTF-8 string data**

và:

```text
"hello"
```

là:

> **string literal, có type `&'static str`**

---

# 18. Bài tập Buổi 1

### Bài 1

Đoán type:

```rust
let a = "Rust";
```

### Bài 2

Code nào hợp lệ?

```rust
let mut a = "hello";

a = "world";
```

và:

```rust
let mut a = "hello";

a.push('!');
```

### Bài 3

Giải thích:

```rust
fn get_name() -> &'static str {
    "Rust"
}
```

Tại sao function có thể trả về reference?

### Bài 4

Viết:

```rust
fn print_message(message: &str)
```

sao cho có thể gọi cả:

```rust
print_message("Hello");
```

và:

```rust
let message = String::from("Rust");
print_message(&message);
```

### Bài 5 — Deep Dive

Giải thích sự khác biệt:

```rust
let a = "hello";
let b = String::from("hello");
```

theo 4 khía cạnh:

```text
1. Type
2. Ownership
3. Memory
4. Mutability
```

---

## Tóm tắt Buổi 1

Nếu chỉ cần nhớ **7 điều**, hãy nhớ:

```text
"hello"
   ↓
string literal
   ↓
&'static str
```

và:

```text
String ≠ &str
```

`String`:

```text
owned
heap
growable
mutable
```

`&str`:

```text
borrowed
string slice
read-only view
```

String literal:

```text
"hello"
```

là:

```rust
&'static str
```

và:

```rust
let mut s = "hello";
```

**không làm nội dung `"hello"` mutable** — nó chỉ cho phép biến `s` thay đổi reference.

Buổi tiếp theo nên đi thẳng vào **`str` vs `&str`**, đặc biệt là **`str` là unsized type (`?Sized`), tại sao không thể viết `let x: str`, và vì sao `&str` lại là một fat pointer gồm `pointer + length`**. Đây là phần bắt đầu thực sự “deep dive” vào cách Rust biểu diễn string trong memory.
