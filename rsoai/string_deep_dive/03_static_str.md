# Rust String Deep Dive — Buổi 3

## String Literal trong Memory — `&'static str`, Compile Time và Runtime

Buổi 1 ta biết:

```rust
"hello"
```

là string literal và có type:

```rust
&'static str
```

Buổi 2 ta biết:

```rust
&str
```

có thể hình dung như:

```text
pointer + length
```

Hôm nay ta nối hai kiến thức đó lại để hiểu sâu hơn:

> **Khi viết `"hello"` trong Rust, dữ liệu thực sự nằm ở đâu? `&'static str` nghĩa chính xác là gì? Tại sao có thể trả string literal khỏi function mà không bị dangling reference?**

---

# 1. Nhìn lại một chương trình đơn giản

```rust
fn main() {
    let name = "Rust";

    println!("{name}");
}
```

Ta có:

```text
name
  │
  ▼
"Rust"
```

Nhưng cần phân biệt:

```text
name
```

và:

```text
"Rust"
```

`name` là một biến.

`"Rust"` là string literal.

---

# 2. Compiler biết `"Rust"` ngay từ lúc compile

Đây là điểm quan trọng.

Khi compiler gặp:

```rust
let name = "Rust";
```

nó biết literal là:

```text
R
u
s
t
```

ngay từ **compile time**.

Không cần:

```text
user input
network
file
database
```

để biết nội dung literal.

Ví dụ:

```rust
fn main() {
    let a = "Hello";
    let b = "Rust";
    let c = "Programming";
}
```

Compiler đã biết toàn bộ nội dung:

```text
Hello
Rust
Programming
```

trước khi chương trình chạy.

---

# 3. String literal được đưa vào executable

Một mental model đơn giản:

```text
Rust source code
       │
       ▼
    compiler
       │
       ▼
 executable
       │
       ├── machine code
       │
       └── string literal data
```

Ví dụ:

```rust
fn main() {
    println!("Hello Rust");
}
```

Literal:

```text
"Hello Rust"
```

được compiler đưa vào chương trình đã biên dịch.

Có thể hình dung:

```text
Executable
┌───────────────────────────────┐
│ machine code                  │
│                               │
│ ...                           │
│                               │
│ "Hello Rust"                  │
│                               │
│ ...                           │
└───────────────────────────────┘
```

---

# 4. Đừng hiểu quá đơn giản rằng nó luôn là "read-only memory"

Ở mức hệ điều hành / linker / platform, layout cụ thể có thể khác nhau.

Thông thường string literals được đặt trong vùng dữ liệu của executable có tính chất **read-only**.

Mental model tốt cho việc học Rust:

```text
executable
┌──────────────────────┐
│ code                 │
├──────────────────────┤
│ read-only data       │
│                      │
│ "Hello"              │
│ "Rust"               │
│ "Programming"        │
└──────────────────────┘
```

Điểm quan trọng hơn vị trí vật lý chính xác là:

> String literal không phải một `String` heap-owned được tạo mới mỗi lần chương trình chạy qua câu lệnh.

---

# 5. `&'static str` xuất hiện ở đây

Xét:

```rust
let name = "Rust";
```

Type chính xác có thể xem là:

```rust
&'static str
```

Tách ra:

```text
&
│
└── reference

'static
│
└── lifetime

str
│
└── dynamically sized string slice
```

Vậy:

```rust
&'static str
```

có nghĩa:

> một reference tới `str` có lifetime kéo dài trong toàn bộ thời gian chương trình.

---

# 6. `'static` không phải là "static variable"

Đây là lỗi hiểu rất phổ biến.

Khi thấy:

```rust
&'static str
```

đừng nghĩ:

```text
static variable
```

`'static` ở đây là **lifetime**.

Ví dụ:

```rust
fn get_name() -> &'static str {
    "Rust"
}
```

`'static` nói về:

```text
lifetime của reference
```

chứ không nói rằng function tạo ra một biến `static`.

---

# 7. Vì sao literal có thể sống `'static`?

Xét:

```rust
fn get_name() -> &'static str {
    "Rust"
}
```

Function bắt đầu:

```text
get_name()
    │
    ▼
"Rust"
```

Function kết thúc:

```text
get_name()
    │
    ▼
return
```

Nhưng dữ liệu literal:

```text
"Rust"
```

không biến mất khi function kết thúc.

Nó thuộc về chương trình đã chạy.

Có thể hình dung:

```text
Program lifetime
│
├──────────────────────────────────────┐
│                                      │
│  "Rust"                              │
│                                      │
└──────────────────────────────────────┘
```

Do đó function có thể trả:

```rust
&'static str
```

mà không tạo dangling reference.

---

# 8. So sánh với local variable

Đây mới là phần quan trọng.

Code này không hợp lệ:

```rust
fn get_name() -> &str {
    let name = String::from("Rust");

    &name
}
```

Vì:

```text
function
│
├── name
│
└── return &name
```

Khi function kết thúc:

```text
name
  ↓
destroyed
```

nhưng reference vẫn muốn trỏ tới:

```text
name
```

Đó là dangling reference.

Rust ngăn điều này.

---

# 9. So sánh hai trường hợp

### Trường hợp 1

```rust
fn get_name() -> &'static str {
    "Rust"
}
```

An toàn.

```text
"Rust"
│
└── tồn tại trong program lifetime
```

### Trường hợp 2

```rust
fn get_name() -> &str {
    let s = String::from("Rust");
    &s
}
```

Không an toàn.

```text
s
│
├── function scope
│
└── destroyed
      ↑
      │
   &s còn trỏ tới?
```

Rust từ chối.

---

# 10. Đây là lý do lifetime tồn tại

Rust muốn đảm bảo:

```text
reference
    ↓
dữ liệu vẫn còn sống
```

Không bao giờ:

```text
reference
    ↓
❌ dữ liệu đã bị destroy
```

String literal rất đặc biệt vì:

```text
"Rust"
    ↓
program lifetime
```

nên:

```rust
&'static str
```

an toàn.

---

# 11. String literal không cần heap allocation

Xét:

```rust
let name = "Rust";
```

Không nên hình dung:

```text
STACK
name
 │
 ▼
HEAP
Rust
```

như với:

```rust
let name = String::from("Rust");
```

Với literal, mental model phù hợp hơn:

```text
STACK
name
┌───────────────────┐
│ pointer           │
│ length = 4        │
└─────────┬─────────┘
          │
          ▼
PROGRAM DATA
┌───────────────────┐
│ R u s t           │
└───────────────────┘
```

Trong khi `String`:

```text
STACK
name
┌───────────────────┐
│ ptr               │
│ len               │
│ capacity           │
└─────────┬─────────┘
          │
          ▼
HEAP
┌───────────────────┐
│ R u s t           │
└───────────────────┘
```

---

# 12. So sánh `&str` literal và `String`

```rust
fn main() {
    let a = "Rust";
    let b = String::from("Rust");
}
```

Mental model:

```text
a: &'static str
│
└───────────────┐
                ▼
         executable data
         ┌───────────┐
         │ R u s t   │
         └───────────┘


b: String
│
├── pointer ─────────────┐
├── length = 4           │
└── capacity = ...       │
                         ▼
                       HEAP
                   ┌───────────┐
                   │ R u s t   │
                   └───────────┘
```

Hai chuỗi có cùng nội dung nhưng **cách sở hữu dữ liệu hoàn toàn khác nhau**.

---

# 13. Literal có thể được sử dụng ở nhiều nơi

Ví dụ:

```rust
fn main() {
    let a = "Rust";
    let b = "Rust";
    let c = "Rust";
}
```

Ta không nên mặc định nghĩ rằng có ba bản copy độc lập trên heap.

Compiler/linker có thể tối ưu và chia sẻ literal.

Mental model:

```text
a ─────┐
b ─────┼──────► "Rust"
c ─────┘
```

Tuy nhiên:

> Đừng viết code phụ thuộc vào việc hai literal có cùng địa chỉ memory hay không.

Đó là chi tiết implementation/optimization, không phải contract mà bạn nên dựa vào.

---

# 14. Có thể so sánh pointer không?

Bạn có thể gặp:

```rust
let a = "Rust";
let b = "Rust";
```

Đừng thiết kế logic dựa vào:

```text
address(a) == address(b)
```

Thay vào đó:

```rust
assert_eq!(a, b);
```

So sánh **giá trị string**, không phải địa chỉ.

Đây là nguyên tắc tốt:

```text
semantic equality
    ↓
"Rust" == "Rust"
```

thay vì:

```text
memory identity
    ↓
cùng địa chỉ?
```

---

# 15. String literal có thể chứa Unicode

Ví dụ:

```rust
let text = "Xin chào 🌏";
```

Compiler biết byte representation UTF-8 của literal.

Có thể hình dung:

```text
"Xin chào 🌏"
      │
      ▼
UTF-8 bytes
      │
      ▼
embedded program data
```

Đây là lý do sau này:

```rust
text.len()
```

không nhất thiết bằng số ký tự bạn nhìn thấy.

Ví dụ:

```rust
let text = "é";
```

`é` trong UTF-8 có thể chiếm nhiều hơn 1 byte.

Phần này chúng ta sẽ đào sâu ở buổi UTF-8.

---

# 16. `&'static str` có thể được lưu trong `static`

Rust có:

```rust
static LANGUAGE: &str = "Rust";
```

Hoặc rõ hơn:

```rust
static LANGUAGE: &'static str = "Rust";
```

Ở đây ta thực sự có một **static item**.

Điều này khác với:

```rust
let language = "Rust";
```

Hãy phân biệt:

```text
"Rust"
    ↓
string literal
    ↓
&'static str
```

và:

```rust
static LANGUAGE: &'static str = "Rust";
    ↓
static item
```

---

# 17. `static` và `'static` khác nhau

Đây là kiến thức phải thuộc.

### `static`

```rust
static NAME: &str = "Rust";
```

Là khai báo một static item.

### `'static`

```rust
&'static str
```

là lifetime annotation.

Hai khái niệm liên quan nhưng không giống nhau.

---

# 18. Một ví dụ về `static`

```rust
static LANGUAGE: &str = "Rust";

fn main() {
    println!("{LANGUAGE}");
}
```

`LANGUAGE` tồn tại trong toàn bộ chương trình.

Nhưng literal:

```rust
"Rust"
```

vốn đã có lifetime `'static`.

Do đó:

```rust
static LANGUAGE: &'static str = "Rust";
```

hoàn toàn hợp lý.

---

# 19. Có thể trả literal từ function

Đây là pattern rất phổ biến:

```rust
fn default_language() -> &'static str {
    "Rust"
}
```

Hoặc:

```rust
fn status() -> &'static str {
    "success"
}
```

Hoặc:

```rust
fn error_message() -> &'static str {
    "Something went wrong"
}
```

Các string này:

```text
không cần String
không cần heap allocation
không cần ownership transfer
```

nếu nội dung hoàn toàn cố định.

---

# 20. Nhưng đừng lạm dụng `'static`

Một lỗi thiết kế API:

```rust
fn process(input: &'static str) {
    ...
}
```

Nếu function chỉ cần đọc string, thường không nên ép caller phải cung cấp `'static`.

Tốt hơn:

```rust
fn process(input: &str) {
    ...
}
```

Tại sao?

Vì:

```rust
&'static str
```

là một subset rất nhỏ của:

```rust
&str
```

Có thể hình dung:

```text
&str
┌──────────────────────────────────┐
│ mọi borrowed string              │
│                                  │
│    &'static str                  │
│       ┌──────────────┐           │
│       │ string       │           │
│       │ literals     │           │
│       └──────────────┘           │
└──────────────────────────────────┘
```

---

# 21. Ví dụ về API quá restrictive

Không nên viết:

```rust
fn print_name(name: &'static str) {
    println!("{name}");
}
```

nếu bạn chỉ muốn in string.

Vì:

```rust
let name = String::from("Rust");

print_name(&name);
```

sẽ không đáp ứng yêu cầu `'static`.

Thay vào đó:

```rust
fn print_name(name: &str) {
    println!("{name}");
}
```

sẽ nhận được:

```rust
print_name("Rust");
```

và:

```rust
let name = String::from("Rust");
print_name(&name);
```

---

# 22. Khi nào nên dùng `&'static str`?

Có một số trường hợp hợp lý:

### Constant message

```rust
fn version() -> &'static str {
    "1.0.0"
}
```

### Enum → fixed text

```rust
enum Level {
    Info,
    Error,
}

impl Level {
    fn as_str(&self) -> &'static str {
        match self {
            Level::Info => "INFO",
            Level::Error => "ERROR",
        }
    }
}
```

Ở đây rất hợp lý vì tất cả kết quả đều là literal cố định.

---

# 23. Ví dụ thực tế

```rust
enum Status {
    Success,
    Failed,
    Pending,
}

impl Status {
    fn as_str(&self) -> &'static str {
        match self {
            Status::Success => "success",
            Status::Failed => "failed",
            Status::Pending => "pending",
        }
    }
}
```

Sử dụng:

```rust
fn main() {
    let status = Status::Success;

    println!("{}", status.as_str());
}
```

Không cần:

```rust
String::from(...)
```

vì dữ liệu cố định.

---

# 24. Literal và `const`

Ta cũng có:

```rust
const APP_NAME: &str = "Rust App";
```

và:

```rust
static APP_NAME: &str = "Rust App";
```

Chúng không hoàn toàn giống nhau.

### `const`

```rust
const APP_NAME: &str = "Rust App";
```

là compile-time constant.

### `static`

```rust
static APP_NAME: &str = "Rust App";
```

là một static item có một vị trí cố định trong chương trình.

Đây là chủ đề sâu hơn về `const`/`static`; ở đây chỉ cần phân biệt.

---

# 25. Một insight quan trọng: `String` không phải cách duy nhất để có text

Ta có:

```text
                    Text
                     │
         ┌───────────┴───────────┐
         │                       │
       String                    &str
         │                       │
      owned                    borrowed
         │                       │
      dynamic                 slice
         │                       │
       heap                  various source
```

`&str` có thể đến từ:

```text
string literal
String
array of bytes qua hợp lệ UTF-8
substring/slice
```

Do đó khi API chỉ cần đọc text:

```rust
fn parse(input: &str)
```

là abstraction rất mạnh.

---

# 26. Một ví dụ kết hợp toàn bộ kiến thức

```rust
fn get_default_name() -> &'static str {
    "Anonymous"
}

fn greet(name: &str) {
    println!("Hello, {name}!");
}

fn main() {
    let default_name = get_default_name();

    greet(default_name);

    let user_name = String::from("Garden");

    greet(&user_name);
}
```

Ở đây có hai nguồn `&str`.

### Nguồn 1

```rust
get_default_name()
```

trả:

```text
&'static str
```

### Nguồn 2

```rust
&user_name
```

có thể coercion thành:

```text
&str
```

Function:

```rust
greet(name: &str)
```

không cần biết dữ liệu đến từ đâu.

Đây chính là abstraction tốt.

---

# 27. Memory model tổng hợp

Chương trình:

```rust
fn get_default_name() -> &'static str {
    "Anonymous"
}

fn main() {
    let name = get_default_name();

    let user = String::from("Rust");

    println!("{name}");
    println!("{user}");
}
```

Mental model:

```text
STACK
─────────────────────────────

name
┌─────────────────────┐
│ ptr                 │──────┐
│ len                 │      │
└─────────────────────┘      │
                             │
user                         │
┌─────────────────────┐      │
│ ptr ────────────────┼──┐   │
│ len                 │  │   │
│ capacity            │  │   │
└─────────────────────┘  │   │
                         │   │
                         ▼   ▼

PROGRAM / READ-ONLY DATA
─────────────────────────────
"Anonymous"
┌─────────────────────┐
│ A n o n y m o u s   │
└─────────────────────┘


HEAP
─────────────────────────────
"Rust"
┌─────────────────────┐
│ R u s t             │
└─────────────────────┘
```

Điểm mấu chốt:

```text
name
  ↓
borrowed view
  ↓
static program data
```

trong khi:

```text
user
  ↓
owner
  ↓
heap data
```

---

# 28. Một misconception rất nguy hiểm

Không nên nói:

> "`&str` luôn nằm trên stack."

Không chính xác.

`&str` là **reference value** và giá trị reference có thể được lưu trong stack, struct, register, heap... tùy context.

Còn dữ liệu mà `&str` trỏ tới có thể nằm ở:

```text
string literal → program/static data
String → heap
array → stack hoặc nơi owner nằm
```

Do đó phải tách:

```text
reference
```

và:

```text
referenced data
```

Đây là tư duy memory rất quan trọng trong Rust.

---

# 29. Một misconception khác

Không nên nghĩ:

```text
&str = pointer tới null-terminated C string
```

Rust `str` **không sử dụng `\0` để đánh dấu kết thúc**.

Độ dài được lưu riêng:

```text
&str
┌───────────────┐
│ pointer       │
│ length        │
└───────────────┘
```

Vì vậy string có thể chứa null byte:

```rust
let text = "hello\0world";
```

Đây vẫn là một Rust string hợp lệ.

---

# 30. Tại sao thiết kế này quan trọng?

Nhờ:

```text
pointer + length
```

Rust có thể:

* không cần scan tìm `\0`
* hỗ trợ substring hiệu quả
* hỗ trợ embedded null
* kiểm soát bounds
* làm việc trực tiếp với UTF-8 bytes

Đây là một trong những điểm khác biệt quan trọng giữa Rust string và C string.

---

# Bài tập Buổi 3

## Bài 1 — Type

Cho:

```rust
let text = "Rust";
```

Hãy xác định type đầy đủ nhất của `text`.

---

## Bài 2 — Lifetime

Giải thích tại sao function này hợp lệ:

```rust
fn language() -> &'static str {
    "Rust"
}
```

nhưng function này không hợp lệ:

```rust
fn language() -> &str {
    let s = String::from("Rust");
    &s
}
```

---

## Bài 3 — Memory

Vẽ memory model cho:

```rust
fn main() {
    let a = "Rust";

    let b = String::from("Rust");
}
```

Phải phân biệt:

```text
a
b
literal
heap
pointer
length
capacity
```

---

## Bài 4 — API Design

Function nào tốt hơn?

```rust
fn print_name(name: &'static str) {
    println!("{name}");
}
```

hay:

```rust
fn print_name(name: &str) {
    println!("{name}");
}
```

Giải thích tại sao.

---

## Bài 5 — `static` vs `'static`

Giải thích sự khác nhau giữa:

```rust
static NAME: &str = "Rust";
```

và:

```rust
fn name() -> &'static str {
    "Rust"
}
```

---

# Mini Challenge

Hãy viết một chương trình:

```text
Status:
    Success
    Error
    Loading
```

và implement:

```rust
fn as_str(&self) -> &'static str
```

sao cho:

```rust
let status = Status::Success;

println!("{}", status.as_str());
```

in:

```text
success
```

Sau đó giải thích:

1. Tại sao return type là `&'static str`?
2. Tại sao không cần `String`?
3. `"success"` được sở hữu bởi ai?
4. Tại sao return reference này không dangling?

---

## Tổng kết Buổi 3

Mental model quan trọng nhất:

```text
String literal
      │
      ▼
 &'static str
      │
      ▼
┌───────────────┐
│ pointer       │
│ length        │
└───────┬───────┘
        │
        ▼
program's static data
```

Trong khi:

```text
String
   │
   ├── pointer
   ├── length
   └── capacity
          │
          ▼
        heap
```

Và đặc biệt:

```text
'static
   ≠
static
```

`'static` là **lifetime**.

`static` là **một loại item/khai báo static**.

**Buổi 4** chúng ta sẽ đi vào phần cực kỳ quan trọng: **UTF-8 trong Rust** — byte, code point, Unicode scalar value, `char`, tại sao `"é".len()` không phải 1, tại sao `"你好".len()` không phải 2, và tại sao Rust cấm `string[0]`.
