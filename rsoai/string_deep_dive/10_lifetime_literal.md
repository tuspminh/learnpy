# Rust String Deep Dive — Phần I

# Buổi 10 — Lifetime của String Literal `'static`

Đây là **buổi cuối của Phần I — String Literal & `str`**, và cũng là buổi rất quan trọng để nối kiến thức:

```text
String Literal
      ↓
&str
      ↓
UTF-8
      ↓
memory
      ↓
ownership
      ↓
borrow
      ↓
lifetime
```

Mục tiêu hôm nay:

* Hiểu chính xác `"hello"` có lifetime gì.
* Hiểu `'static` nghĩa là gì.
* Phân biệt `&str` và `&'static str`.
* Hiểu tại sao string literal có thể trả về từ function.
* Hiểu tại sao `&String` local không thể trả về.
* Hiểu lifetime của slice lấy từ `String`.
* Hiểu `'static` không đồng nghĩa với "global variable".
* Hiểu relationship giữa lifetime và ownership.

---

# 1. String literal `"hello"` có lifetime `'static`

Khi viết:

```rust
let text = "hello";
```

Type có thể hiểu là:

```rust
&'static str
```

Không chỉ:

```rust
&str
```

Tức là:

```text
"hello"
   ↓
&'static str
```

---

# 2. `'static` nghĩa là gì?

Lifetime `'static` nghĩa là:

> Reference có thể tồn tại trong suốt lifetime của chương trình.

Ví dụ:

```rust
fn get_text() -> &'static str {
    "hello"
}
```

Hoàn toàn hợp lệ.

Vì `"hello"` có lifetime `'static`.

---

# 3. Tại sao literal có thể sống lâu như vậy?

Xem:

```rust
fn main() {
    let text = "hello";

    println!("{text}");
}
```

Dữ liệu của:

```text
"hello"
```

không phải được tạo mới mỗi lần `let text`.

String literal được compiler đưa vào binary/executable như static data.

Conceptually:

```text
Executable
┌─────────────────────────────┐
│ machine code                │
│ ...                         │
│ "hello"                     │
│ "Rust"                      │
│ "world"                     │
└─────────────────────────────┘
```

Dữ liệu này tồn tại trong suốt thời gian process chạy.

---

# 4. `"hello"` không phải `String`

Đây là điều cần nhớ:

```rust
let a = "hello";
```

không tạo:

```text
String
```

mà tạo:

```text
&'static str
```

Trong khi:

```rust
let b = String::from("hello");
```

tạo:

```text
String
```

---

# 5. So sánh

```rust
let a = "hello";
let b = String::from("hello");
```

Conceptually:

```text
a
↓
&'static str
↓
static memory
```

Trong khi:

```text
b
↓
String
↓
heap allocation
↓
"hello"
```

---

# 6. `a` không sở hữu `"hello"`

```rust
let a = "hello";
```

`a` chỉ là một reference.

Nó không sở hữu dữ liệu.

```text
a
│
│ borrow
▼
"hello"
```

Dữ liệu literal thuộc về chương trình/runtime, không thuộc về biến `a`.

---

# 7. Vì sao `a` có thể copy?

```rust
let a = "hello";
let b = a;

println!("{a}");
println!("{b}");
```

Hợp lệ.

Vì:

```text
&str
```

là một reference type và có thể `Copy`.

Không có ownership transfer đối với underlying literal.

---

# 8. `'static` không có nghĩa là immutable reference

Một misconception:

> `'static` nghĩa là dữ liệu immutable.

Không hoàn toàn.

`'static` nói về **lifetime** của reference.

Ví dụ:

```text
'static
```

trả lời câu hỏi:

> Reference có thể sống bao lâu?

Nó không trực tiếp trả lời:

> Data có mutable hay không?

Tuy nhiên string literal trong Rust được truy cập qua `&str`, và bạn không thể mutate literal.

---

# 9. `&'static str`

Bạn có thể khai báo rõ:

```rust
let text: &'static str = "hello";
```

Điều này hợp lệ.

Nhưng thường không cần viết `'static`:

```rust
let text = "hello";
```

Compiler tự biết.

---

# 10. `&str` và `&'static str`

Đây:

```rust
let a: &str = "hello";
```

và:

```rust
let b: &'static str = "hello";
```

đều hợp lệ.

Vì:

```text
&'static str
```

có thể được sử dụng ở nơi cần:

```text
&str
```

`'static` là lifetime cụ thể hơn.

---

# 11. Lifetime là phần của reference type

Có thể hình dung:

```text
&'a str
```

gồm:

```text
&
│
├── lifetime = 'a
│
└── type = str
```

Ví dụ:

```text
&'static str
```

nghĩa:

```text
reference
   │
   ├── lifetime: 'static
   │
   └── pointee: str
```

---

# 12. Tại sao function này hợp lệ?

```rust
fn hello() -> &'static str {
    "hello"
}
```

Flow:

```text
hello()
   ↓
"hello"
   ↓
static data
   ↓
&'static str
```

Không có local variable nào bị borrow.

---

# 13. Function này cũng hợp lệ

```rust
fn get_name() -> &'static str {
    "Alice"
}
```

Bạn có thể:

```rust
fn main() {
    let name = get_name();

    println!("{name}");
}
```

---

# 14. Đây là pattern phổ biến

Bạn có thể dùng:

```rust
fn error_message(code: u32) -> &'static str {
    match code {
        404 => "Not Found",
        500 => "Internal Server Error",
        _ => "Unknown Error",
    }
}
```

Tất cả các branch đều trả:

```text
&'static str
```

---

# 15. Tại sao cách này rất hiệu quả?

Function:

```rust
fn error_message(code: u32) -> &'static str
```

không cần:

```rust
String::from(...)
```

Không allocation.

Không copy.

Các literal đã nằm trong static program data.

---

# 16. Ví dụ

```rust
fn status(code: u16) -> &'static str {
    match code {
        200 => "OK",
        404 => "Not Found",
        500 => "Internal Server Error",
        _ => "Unknown",
    }
}
```

Memory conceptually:

```text
static data
┌────────────────────────────┐
│ "OK"                       │
│ "Not Found"                │
│ "Internal Server Error"    │
│ "Unknown"                  │
└────────────────────────────┘
```

Function chỉ trả reference tới chúng.

---

# 17. Nhưng local `String` thì khác

Xem:

```rust
fn hello() -> &str {
    let text = String::from("hello");

    &text
}
```

Code này **không compile**.

Tại sao?

```text
hello()
 │
 ├── text được tạo
 │
 ├── &text được tạo
 │
 └── function kết thúc
          ↓
       text bị drop
```

Reference sẽ trỏ vào dữ liệu đã bị destroy.

---

# 18. Memory model

Trong function:

```rust
let text = String::from("hello");
```

Conceptually:

```text
STACK
┌───────────────┐
│ text          │
│ ptr ──────────────┐
│ len             │ │
│ capacity        │ │
└─────────────────┘ │
                    ▼
HEAP
┌─────────────────┐
│ hello           │
└─────────────────┘
```

Khi function return:

```text
text
 ↓
drop
 ↓
heap freed
```

Nếu trả:

```text
&text
```

thì reference sẽ trở thành dangling reference.

Rust không cho phép.

---

# 19. Đây chính là lý do lifetime tồn tại

Rust compiler cần đảm bảo:

```text
reference
    ↓
data vẫn còn sống
```

Không được:

```text
reference
    ↓
dead data
```

Đó là một trong những mục tiêu cốt lõi của borrow checker.

---

# 20. So sánh hai function

### Hợp lệ

```rust
fn a() -> &'static str {
    "hello"
}
```

### Không hợp lệ

```rust
fn b() -> &str {
    let s = String::from("hello");
    &s
}
```

Khác biệt:

```text
a()
 ↓
static data
 ↓
program lifetime
```

Trong khi:

```text
b()
 ↓
local String
 ↓
function lifetime
 ↓
drop
```

---

# 21. Một điểm cực kỳ quan trọng

`'static` **không có nghĩa là mọi `String` đều sống mãi**.

Ví dụ:

```rust
let s = String::from("hello");
```

`String` này không `'static`.

Nó sống theo scope/ownership của biến `s`.

---

# 22. `String` có thể chứa literal nhưng không phải static

Ví dụ:

```rust
let s = String::from("hello");
```

Có hai giai đoạn:

```text
"hello"
   ↓
source/static literal
   ↓
String::from(...)
   ↓
copy UTF-8 bytes
   ↓
heap
```

Sau đó `s` sở hữu **một bản sao** dữ liệu.

---

# 23. Đây là điểm rất hay bị nhầm

```rust
let a = "hello";
let b = String::from("hello");
```

Không phải:

```text
a ─────┐
       ├── cùng một String
b ─────┘
```

Mà conceptually:

```text
a ─────► static "hello"

b ─────► heap "hello"
```

Hai vùng dữ liệu khác nhau.

---

# 24. `String::from()` có allocation

```rust
let s = String::from("hello");
```

Thường cần heap allocation.

Trong khi:

```rust
let s = "hello";
```

không cần heap allocation cho literal.

---

# 25. Lifetime của slice từ `String`

Xem:

```rust
fn first_word(text: &str) -> &str {
    text.split_whitespace().next().unwrap()
}
```

Nếu:

```rust
let s = String::from("hello rust");

let word = first_word(&s);
```

thì:

```text
s
│
└──────────────► heap
                 │
                 ├── "hello"
                 └── "rust"

word
 │
 └──────────────► "hello"
```

`word` chỉ sống được khi `s` còn sống.

---

# 26. Lifetime relationship

Conceptually:

```text
'a
│
├──── s
│
├──── &s
│
└──── word
```

Compiler đảm bảo:

```text
lifetime(word) <= lifetime(s)
```

---

# 27. Đây là lý do function này có thể trả `&str`

```rust
fn first_word(text: &str) -> &str {
    text.split_whitespace().next().unwrap()
}
```

Không cần ghi lifetime:

```rust
fn first_word<'a>(text: &'a str) -> &'a str
```

Compiler áp dụng lifetime elision.

Nhưng về mặt logic có thể hiểu:

```text
input lifetime
      │
      └────► output lifetime
```

---

# 28. Viết explicit lifetime

Ta có thể viết:

```rust
fn first_word<'a>(text: &'a str) -> &'a str {
    text.split_whitespace().next().unwrap()
}
```

Nghĩa:

> Input `text` được borrow trong lifetime `'a`, output cũng borrow dữ liệu trong cùng lifetime `'a`.

---

# 29. Đây không phải tạo lifetime

Điểm quan trọng:

```rust
'a
```

không phải một vùng memory.

Không phải:

```text
'a = 10 seconds
```

Lifetime là một **constraint/region được compiler theo dõi**.

---

# 30. `'static` cũng là lifetime constraint

Khi viết:

```rust
&'static str
```

ta nói:

```text
reference này có thể tồn tại trong toàn bộ chương trình.
```

Không phải:

```text
memory address cố định tuyệt đối
```

và cũng không phải:

```text
global variable
```

---

# 31. `'static` có hai cách sử dụng

Đây là một deep-dive quan trọng.

Bạn có thể gặp:

```rust
T: 'static
```

và:

```rust
&'static T
```

Hai khái niệm liên quan nhưng **không giống nhau**.

---

# 32. `&'static str`

Ví dụ:

```rust
let s: &'static str = "hello";
```

Nghĩa:

```text
reference tới str
có lifetime 'static
```

---

# 33. `T: 'static`

Ví dụ:

```rust
fn foo<T: 'static>(value: T) {
}
```

Điều này **không có nghĩa**:

```text
value sống mãi
```

Mà có nghĩa gần đúng:

> `T` không chứa borrowed references có lifetime ngắn hơn `'static`.

Ví dụ `String` thỏa mãn:

```text
String: 'static
```

vì `String` sở hữu dữ liệu của nó.

---

# 34. Đây là một điểm rất quan trọng

`String`:

```rust
String
```

có thể satisfy:

```text
T: 'static
```

nhưng object `String` vẫn được drop bình thường.

Ví dụ:

```rust
fn consume<T: 'static>(value: T) {
    drop(value);
}
```

Hoàn toàn hợp lệ.

`'static` ở đây không có nghĩa object sống mãi.

---

# 35. Ví dụ

```rust
fn require_static<T: 'static>(_: T) {}

fn main() {
    let s = String::from("hello");

    require_static(s);
}
```

Hợp lệ.

Mặc dù `s` không phải biến global.

---

# 36. Vì sao?

Vì `String` sở hữu bytes:

```text
String
 └── owns heap data
```

Nó không chứa:

```text
&'short str
```

nên không có borrowed data ngắn hạn cần bảo vệ.

---

# 37. Nhưng reference local thì sao?

```rust
fn require_static<T: 'static>(_: T) {}

fn main() {
    let x = 10;
    let r = &x;

    require_static(r);
}
```

Thông thường không hợp lệ.

Vì:

```text
r: &'short i32
```

không phải:

```text
&'static i32
```

---

# 38. Mental model

`String`:

```text
String
 ↓
owns data
 ↓
không phụ thuộc lifetime của data bên ngoài
```

`&str`:

```text
&str
 ↓
borrows data
 ↓
phụ thuộc lifetime source
```

String literal:

```text
&'static str
 ↓
borrows static program data
```

---

# 39. Một ví dụ cực kỳ hay

```rust
fn get_message(ok: bool) -> &'static str {
    if ok {
        "Success"
    } else {
        "Failed"
    }
}
```

Tất cả literal:

```text
"Success"
"Failed"
```

đều có:

```text
'static
```

nên return type hợp lệ.

---

# 40. Nếu muốn return `String`

Bạn cũng có thể:

```rust
fn get_message(ok: bool) -> String {
    if ok {
        "Success".to_string()
    } else {
        "Failed".to_string()
    }
}
```

Nhưng ở đây bạn đang tạo owned string.

Nếu không cần ownership:

```rust
-> &'static str
```

rẻ hơn.

---

# 41. So sánh

### Static reference

```rust
fn message() -> &'static str {
    "Hello"
}
```

```text
allocation: 0
copy:       0
ownership:  borrowed
```

### Owned String

```rust
fn message() -> String {
    "Hello".to_string()
}
```

Conceptually:

```text
allocation: có thể có
copy:       có
ownership:  caller
```

---

# 42. Khi nào dùng `'static`?

Rất phù hợp cho:

### Constant message

```rust
fn error_message(code: u32) -> &'static str
```

### Static lookup

```rust
static NAMES: &[&str] = &[
    "Alice",
    "Bob",
    "Charlie",
];
```

### Enum → message

```rust
enum Error {
    NotFound,
    PermissionDenied,
}

impl Error {
    fn message(&self) -> &'static str {
        match self {
            Self::NotFound => "Not found",
            Self::PermissionDenied => "Permission denied",
        }
    }
}
```

---

# 43. `const` và `static`

Bạn sẽ thường gặp:

```rust
const APP_NAME: &str = "My App";
```

và:

```rust
static APP_NAME: &str = "My App";
```

Đừng vội đồng nhất hai khái niệm này.

`const` và `static` có semantics khác nhau.

Điều cần nhớ trong buổi này:

```text
"hello"
```

bản thân literal có thể được sử dụng với lifetime `'static`.

---

# 44. `const`

Ví dụ:

```rust
const GREETING: &str = "Hello";
```

Có thể:

```rust
fn main() {
    println!("{GREETING}");
}
```

---

# 45. `static`

```rust
static GREETING: &str = "Hello";
```

Đây là một static item.

Bạn có thể tham chiếu:

```rust
fn main() {
    println!("{GREETING}");
}
```

---

# 46. `static` variable không giống string literal

Ví dụ:

```rust
static MESSAGE: &str = "Hello";
```

Có:

```text
MESSAGE
   │
   ▼
&str
   │
   ▼
"Hello"
```

Trong khi literal:

```rust
let x = "Hello";
```

thì:

```text
x
│
▼
&str
│
▼
"Hello"
```

Cả hai có thể trỏ tới static string data, nhưng `static` item là một khái niệm riêng của Rust.

---

# 47. `'static` không có nghĩa "nên dùng càng nhiều càng tốt"

Một lỗi thiết kế phổ biến:

```rust
fn process(data: &'static str)
```

khi function thực tế chỉ cần:

```rust
fn process(data: &str)
```

`'static` làm API restrictive hơn.

Ví dụ:

```rust
fn process(data: &'static str) {
}
```

Không thể truyền arbitrary borrowed string:

```rust
let s = String::from("hello");
process(&s);
```

vì:

```text
&s
```

không có `'static`.

---

# 48. API tốt hơn

Nếu function chỉ cần đọc:

```rust
fn process(data: &str) {
}
```

thay vì:

```rust
fn process(data: &'static str) {
}
```

Đây là nguyên tắc:

> Đừng yêu cầu `'static` nếu bạn không thực sự cần `'static`.

---

# 49. Ví dụ thực tế

Không tốt:

```rust
fn print_name(name: &'static str) {
    println!("{name}");
}
```

Tốt:

```rust
fn print_name(name: &str) {
    println!("{name}");
}
```

Function thứ hai nhận được:

```rust
print_name("Alice");
```

và:

```rust
let name = String::from("Alice");
print_name(&name);
```

---

# 50. `'static` thường xuất hiện trong async/thread

Bạn sẽ gặp:

```rust
thread::spawn(...)
```

và:

```rust
Send + 'static
```

hoặc:

```rust
Box<dyn Trait + 'static>
```

Đây là nơi lifetime `'static` trở nên rất quan trọng trong Rust nâng cao.

Nhưng đừng hiểu:

```text
T: 'static
```

là:

```text
T sống mãi
```

Hãy hiểu:

```text
T không chứa non-static borrowed references.
```

---

# 51. Ví dụ với thread

Một thread có thể tiếp tục chạy sau khi scope hiện tại kết thúc.

Nếu thread borrow:

```rust
let x = 10;

std::thread::spawn(|| {
    println!("{x}");
});
```

Rust phải đảm bảo `x` vẫn tồn tại.

Một closure được spawn thường cần:

```text
'static
```

để không giữ reference ngắn hạn nguy hiểm.

---

# 52. String literal trong thread

```rust
std::thread::spawn(|| {
    println!("Hello");
});
```

Không có vấn đề với literal:

```text
"Hello"
 ↓
'static
```

---

# 53. Nhưng local reference thì khác

```rust
let text = String::from("Hello");

std::thread::spawn(|| {
    println!("{text}");
});
```

Closure không thể đơn giản borrow `text` local theo cách thread yêu cầu, vì thread có thể outlive scope hiện tại.

Thông thường cần ownership:

```rust
let text = String::from("Hello");

std::thread::spawn(move || {
    println!("{text}");
});
```

Đây là một ví dụ rất đẹp về:

```text
ownership
+
borrow
+
lifetime
```

---

# 54. Lifetime không phải garbage collection

Rust không dùng GC để giải quyết lifetime.

Thay vào đó:

```text
ownership
+
borrowing
+
lifetime analysis
```

được compiler kiểm tra tại compile time.

---

# 55. Tổng kết memory

### String literal

```text
"Hello"
   │
   ▼
static program data
   │
   ▼
&'static str
```

### String

```text
String
 ├── ptr
 ├── len
 └── capacity
       │
       ▼
     heap
```

### Slice

```text
&str
 ├── ptr
 └── len
       │
       ▼
  existing UTF-8 data
```

---

# 56. So sánh lifetime

### Literal

```rust
let s = "hello";
```

Conceptually:

```text
s: &'static str
```

### Borrow String

```rust
let s = String::from("hello");
let x = &s;
```

Conceptually:

```text
x: &'a str
```

với:

```text
'a <= lifetime(s)
```

### Local reference

```rust
let x = &local;
```

`x` chỉ có thể tồn tại trong phạm vi mà `local` còn valid.

---

# 57. Bảng tổng kết Phần I

| Concept          | Type           | Ownership | UTF-8          |
| ---------------- | -------------- | --------- | -------------- |
| `"hello"`        | `&'static str` | borrowed  | Có             |
| `&s[..]`         | `&str`         | borrowed  | Có             |
| `String::from()` | `String`       | owned     | Có             |
| `'A'`            | `char`         | value     | Unicode scalar |
| `b'A'`           | `u8`           | value     | byte           |
| `b"ABC"`         | `&[u8]`        | borrowed  | raw bytes      |

---

# 58. Mental model cuối cùng

Bạn nên hình dung Rust String như sau:

```text
                 TEXT
                  │
       ┌──────────┴──────────┐
       │                     │
    UTF-8                  Unicode
    bytes                   scalar
       │                     │
       ▼                     ▼
     &str                   char
       │
       │ borrow
       ▼
  existing data
       │
 ┌─────┴──────────────┐
 │                    │
literal              String
 │                    │
 ▼                    ▼
'static              owned
```

Và lifetime:

```text
"hello"
   │
   ▼
&'static str
   │
   └── có thể sống suốt chương trình
```

trong khi:

```text
String
   │
   ▼
&str
   │
   └── chỉ sống tối đa bằng source data
```

---

# 59. Bài tập tổng hợp Buổi 10

### Bài 1

Giải thích type:

```rust
let a = "hello";
let b: &'static str = "world";
```

Tại sao cả hai đều hợp lệ?

---

### Bài 2

Giải thích tại sao function này compile:

```rust
fn message() -> &'static str {
    "Hello Rust"
}
```

nhưng function này không:

```rust
fn message() -> &str {
    let s = String::from("Hello Rust");
    &s
}
```

---

### Bài 3

Viết:

```rust
fn error_message(code: u16) -> &'static str
```

với:

```text
200 → "OK"
400 → "Bad Request"
401 → "Unauthorized"
404 → "Not Found"
500 → "Internal Server Error"
other → "Unknown Error"
```

Không tạo `String`.

---

### Bài 4

Viết:

```rust
fn first_word(text: &str) -> &str
```

sao cho:

```rust
first_word("Rust is fast")
```

trả:

```text
"Rust"
```

Giải thích lifetime của input và output.

---

### Bài 5 — Lifetime Deep Dive

Phân tích:

```rust
fn first_word<'a>(text: &'a str) -> &'a str {
    text.split_whitespace().next().unwrap()
}
```

Giải thích chính xác ý nghĩa của:

```text
'a
&'a str
-> &'a str
```

và tại sao compiler cần relationship này.

---

### Bài 6 — Ownership

Phân tích:

```rust
fn main() {
    let text = String::from("Hello Rust");

    let word = &text[0..5];

    println!("{word}");
}
```

Hãy xác định:

```text
text owns gì?
word owns gì?
word borrow từ đâu?
word sống bao lâu?
có allocation mới không?
```

---

### Bài 7 — `'static` Trap

Đoạn nào hợp lệ?

```rust
fn a() -> &'static str {
    "hello"
}
```

```rust
fn b() -> &'static str {
    let s = String::from("hello");
    &s
}
```

```rust
fn c() -> &'static str {
    const MESSAGE: &str = "hello";
    MESSAGE
}
```

Giải thích từng trường hợp.

---

### Bài 8 — Deep Dive

Giải thích sự khác nhau giữa:

```rust
&'static str
```

và:

```rust
T: 'static
```

Đặc biệt giải thích tại sao:

```rust
String
```

có thể thỏa:

```text
String: 'static
```

mặc dù một `String` cụ thể hoàn toàn có thể bị `drop`.

---

# 60. Hoàn thành Phần I

Sau Buổi 10, bạn đã có nền tảng khá sâu về:

```text
String Literal
      ↓
str
      ↓
&str
      ↓
UTF-8
      ↓
char
      ↓
byte
      ↓
String Slice
      ↓
UTF-8 Boundary
      ↓
Borrow
      ↓
Lifetime
      ↓
'static
```

Đây là nền tảng để học tiếp **Rust String thực chiến**.

Phần tiếp theo nên đi vào **`String` Deep Dive**:

```text
Phần II — String Ownership & Memory

Buổi 11 — String là gì?
Buổi 12 — String Memory Layout
Buổi 13 — String Heap Allocation
Buổi 14 — String Capacity
Buổi 15 — push / push_str
Buổi 16 — insert / insert_str
Buổi 17 — pop / remove
Buổi 18 — truncate / clear
Buổi 19 — String ↔ &str
Buổi 20 — String Ownership & Borrowing
Buổi 21 — String Clone
Buổi 22 — String Move
Buổi 23 — String Lifetime
Buổi 24 — String Performance
Buổi 25 — Mini Project
```

Đặc biệt **Buổi 12–14** sẽ rất quan trọng nếu mục tiêu của bạn là hiểu Rust ở mức **memory/ownership/performance**, vì chúng ta sẽ trực tiếp mổ xẻ:

```text
String
┌──────────────┐
│ ptr          │──────► heap
│ len          │
│ capacity     │
└──────────────┘
```

và tìm hiểu chính xác `len`, `capacity`, reallocation, growth strategy và tại sao `String` có thể rất nhanh nhưng vẫn an toàn.
