# Rust String Deep Dive — Phần I

# Buổi 9 — String Slice `&str`

Buổi này là một trong những buổi **quan trọng nhất của toàn bộ phần String**.

Mục tiêu là hiểu thật sâu:

* `str` là gì?
* `&str` là gì?
* `String` và `&str` khác nhau thế nào?
* String slice được tạo ra sao?
* `&s[start..end]` hoạt động thế nào?
* Vì sao `&s[0..1]` có thể panic?
* UTF-8 boundary là gì?
* `&str` có phải là một String không?
* `&str` có allocation không?
* `String` → `&str` có copy dữ liệu không?

---

# 1. Trước hết: `String` và `&str`

Hai kiểu này thường xuyên xuất hiện cùng nhau:

```rust
String
```

và:

```rust
&str
```

Mental model:

```text
String
    ↓
owned UTF-8 string

&str
    ↓
borrowed UTF-8 string slice
```

Ví dụ:

```rust
let owned = String::from("Hello");
let borrowed = &owned;
```

Ở đây:

```text
owned
  ↓
String

borrowed
  ↓
&String
```

Nhưng Rust có deref coercion:

```rust
let text: &str = &owned;
```

---

# 2. `str` là gì?

Bạn thường thấy:

```rust
&str
```

nhưng type thật sự phía dưới là:

```rust
str
```

`str` là **dynamically sized type (DST)**.

Bạn không thể:

```rust
let x: str;
```

theo cách thông thường.

Thay vào đó:

```rust
let x: &str;
```

Bạn thao tác với `str` thông qua một pointer như:

```text
&str
Box<str>
Arc<str>
```

Trong thực tế, `&str` là dạng phổ biến nhất.

---

# 3. `&str` là một fat pointer

Đây là kiến thức memory cực kỳ quan trọng.

Một:

```rust
&str
```

conceptually chứa:

```text
pointer
length
```

Ví dụ:

```rust
let text = "Hello";
```

`text`:

```text
&str
```

có thể hình dung:

```text
STACK

┌──────────────────┐
│ pointer          │──────┐
│ length = 5       │      │
└──────────────────┘      │
                          ▼
                    "Hello"
                    UTF-8 bytes
```

Trên hệ thống 64-bit:

```text
pointer = 8 bytes
length  = 8 bytes
-------------------
&str    = 16 bytes
```

---

# 4. Kiểm tra kích thước

```rust
use std::mem::size_of;

fn main() {
    println!("{}", size_of::<&str>());
}
```

Trên hệ thống 64-bit thường:

```text
16
```

Trong khi:

```rust
println!("{}", size_of::<&String>());
```

thường:

```text
8
```

Vì:

```text
&String
```

chỉ là một pointer thông thường.

---

# 5. `String` thì khác

`String` conceptually:

```text
┌──────────────┐
│ pointer      │
│ length       │
│ capacity     │
└──────┬───────┘
       │
       ▼
      HEAP
┌────────────────┐
│ UTF-8 bytes    │
└────────────────┘
```

Trong khi `&str`:

```text
┌──────────────┐
│ pointer      │
│ length       │
└──────┬───────┘
       │
       ▼
 UTF-8 bytes
```

---

# 6. So sánh memory

### `String`

```text
String
 ├── ptr
 ├── len
 └── capacity
        │
        ▼
      heap
```

### `&str`

```text
&str
 ├── ptr
 └── len
        │
        ▼
 existing UTF-8 data
```

`&str` **không sở hữu dữ liệu**.

---

# 7. String slice là gì?

Ví dụ:

```rust
let text = String::from("Hello Rust");
```

Ta có thể lấy một phần:

```rust
let slice = &text[0..5];
```

Khi đó:

```text
text:
Hello Rust
│────│
slice
```

`slice` có type:

```text
&str
```

---

# 8. Không copy dữ liệu

Đây là điểm cực kỳ quan trọng.

Khi viết:

```rust
let text = String::from("Hello Rust");
let slice = &text[0..5];
```

Rust **không tạo một String mới**.

Không có:

```text
heap 1:
Hello Rust

heap 2:
Hello
```

Thay vào đó:

```text
HEAP

H e l l o   R u s t
↑─────────↑
    slice
```

`slice` chỉ trỏ vào vùng dữ liệu hiện có.

---

# 9. Memory model

Conceptually:

```text
String
┌──────────────┐
│ ptr ───────────────┐
│ len = 10      │    │
│ capacity      │    │
└──────────────┘    │
                    ▼
                ┌──────────────────┐
                │ Hello Rust       │
                └──────────────────┘
                  ↑───────↑
                    &str
```

`&str`:

```text
┌──────────────┐
│ ptr ────────────────┐
│ len = 5             │
└─────────────────────┘
```

---

# 10. Slice syntax

Cú pháp:

```rust
&value[start..end]
```

Ví dụ:

```rust
let text = "Hello Rust";

let a = &text[0..5];
let b = &text[6..10];
```

Kết quả:

```text
a = "Hello"
b = "Rust"
```

---

# 11. Range là half-open

Rust dùng:

```text
[start..end]
```

nghĩa là:

```text
start <= index < end
```

Ví dụ:

```rust
&text[0..5]
```

lấy:

```text
0
1
2
3
4
```

Không lấy:

```text
5
```

---

# 12. Các dạng range

Bạn có:

```rust
&text[0..5]
```

```rust
&text[..5]
```

```rust
&text[5..]
```

```rust
&text[..]
```

Tương ứng:

```text
0 → 5
begin → 5
5 → end
begin → end
```

---

# 13. `&str` có thể slice từ `&str`

Không chỉ `String`.

```rust
let text = "Hello Rust";

let slice = &text[0..5];
```

Ở đây:

```text
text: &str
slice: &str
```

Bạn đang tạo một `&str` nhỏ hơn từ `&str` lớn hơn.

---

# 14. Nhưng có một vấn đề cực kỳ quan trọng

String của Rust là UTF-8.

Ví dụ:

```rust
let text = "é";
```

UTF-8:

```text
C3 A9
```

Có:

```text
text.len() == 2
```

Không phải:

```text
1
```

---

# 15. Vì vậy slicing tính theo byte

```rust
let text = "é";
```

Bạn có:

```rust
&text[0..2]
```

Hợp lệ.

Nhưng:

```rust
&text[0..1]
```

sẽ panic.

Tại sao?

Vì:

```text
é
↓
C3 A9
```

Index `1` nằm **giữa một UTF-8 code point**.

---

# 16. UTF-8 boundary

Đây là concept quan trọng nhất của buổi này.

Với:

```text
é
```

bytes:

```text
index:

0       1       2
│       │       │
C3      A9
```

Boundary hợp lệ:

```text
0
2
```

Boundary không hợp lệ:

```text
1
```

Do đó:

```rust
&text[0..2]
```

OK.

Nhưng:

```rust
&text[0..1]
```

panic.

---

# 17. ASCII thì dễ hơn

Ví dụ:

```rust
let text = "Hello";
```

UTF-8:

```text
H e l l o
```

Mỗi ký tự ASCII = 1 byte.

Do đó:

```rust
&text[0..1]
```

lấy:

```text
"H"
```

```rust
&text[0..3]
```

lấy:

```text
"Hel"
```

---

# 18. Unicode thì không thể giả định

Ví dụ:

```rust
let text = "Xin chào";
```

Phần:

```text
à
```

chiếm 2 bytes UTF-8.

Do đó byte indexing có thể không trùng character indexing.

---

# 19. Ví dụ gây panic

```rust
fn main() {
    let text = "é";

    let slice = &text[0..1];

    println!("{slice}");
}
```

Chương trình panic runtime.

Rust sẽ báo lỗi liên quan đến:

```text
byte index 1 is not a char boundary
```

Đây không phải lỗi ngẫu nhiên.

Rust đang bảo vệ invariant UTF-8 của `str`.

---

# 20. Tại sao Rust phải làm vậy?

Giả sử Rust cho phép:

```rust
&text[0..1]
```

với:

```text
é = C3 A9
```

Ta sẽ nhận:

```text
C3
```

Nhưng:

```text
C3
```

không phải UTF-8 string hợp lệ.

Khi đó:

```text
&str
```

sẽ chứa invalid UTF-8.

Rust không cho phép điều đó.

---

# 21. Đây là invariant cực kỳ quan trọng

Rust đảm bảo:

```text
&str
```

luôn chứa:

```text
valid UTF-8
```

Do đó khi slicing:

```text
[start..end]
```

Rust yêu cầu:

```text
start = UTF-8 boundary
end   = UTF-8 boundary
```

---

# 22. UTF-8 boundary là gì?

Đơn giản hóa:

Một boundary hợp lệ nằm:

```text
trước một code point
```

hoặc:

```text
sau một code point
```

Không được nằm:

```text
giữa các bytes của một code point
```

Ví dụ:

```text
é = C3 A9

0       1       2
│       │       │
C3      A9
```

Boundary:

```text
0, 2
```

---

# 23. Unicode 3 bytes

Ví dụ:

```rust
let text = "中";
```

UTF-8:

```text
E4 B8 AD
```

Index:

```text
0    1    2    3
│    │    │    │
E4   B8   AD
```

Valid boundaries:

```text
0
3
```

Invalid:

```text
1
2
```

---

# 24. Unicode 4 bytes

Emoji:

```rust
let text = "🦀";
```

UTF-8:

```text
F0 9F A6 80
```

Index:

```text
0    1    2    3    4
│    │    │    │    │
F0   9F   A6   80
```

Boundary:

```text
0
4
```

Không phải:

```text
1
2
3
```

---

# 25. Cách slice Unicode an toàn

Nếu bạn muốn lấy character đầu tiên:

Không làm:

```rust
&text[0..1]
```

Mà:

```rust
let first = text.chars().next();
```

Nếu cần nhiều characters:

```rust
let first_three: String =
    text.chars().take(3).collect();
```

---

# 26. Nhưng `chars()` trả về `char`

Ví dụ:

```rust
let text = "你好";

let first = text.chars().next();
```

Kết quả:

```text
Some('你')
```

Nếu bạn muốn `&str`, có thể dùng:

```rust
let first = text.char_indices().next()
    .map(|(i, c)| &text[i..i + c.len_utf8()]);
```

Nhưng đây là code khá verbose.

---

# 27. `char_indices()`

Đây là iterator rất hữu ích.

```rust
let text = "aé中";
```

```rust
for (index, c) in text.char_indices() {
    println!("{index}: {c}");
}
```

Conceptually:

```text
0: a
1: é
3: 中
```

Tại sao?

```text
a → 1 byte
é → 2 bytes
中 → 3 bytes
```

Nên byte offset:

```text
a
0

é
1

中
3
```

---

# 28. `char_indices()` rất quan trọng

Nó cho:

```text
(byte_index, char)
```

chứ không phải:

```text
(character_index, char)
```

Ví dụ:

```text
"aé中"
```

có:

```text
byte index:

a → 0
é → 1
中 → 3
```

---

# 29. Tìm một `&str` slice theo character

Ví dụ:

```rust
fn first_char_slice(text: &str) -> Option<&str> {
    let (start, ch) = text.char_indices().next()?;

    Some(&text[start..start + ch.len_utf8()])
}
```

Test:

```rust
fn main() {
    println!("{:?}", first_char_slice("Rust"));
    println!("{:?}", first_char_slice("你好"));
    println!("{:?}", first_char_slice("🦀"));
}
```

Conceptually:

```text
Some("R")
Some("你")
Some("🦀")
```

---

# 30. `String` → `&str`

Đây là operation bạn sẽ dùng liên tục.

```rust
let owned = String::from("Hello");

let slice: &str = &owned;
```

Không copy.

Không allocation.

Chỉ tạo borrowed view.

---

# 31. Deref coercion

Thậm chí:

```rust
fn print_text(text: &str) {
    println!("{text}");
}

fn main() {
    let s = String::from("Hello");

    print_text(&s);
}
```

Hoàn toàn hợp lệ.

Tại sao?

Rust thực hiện:

```text
&String
   ↓
deref coercion
   ↓
&str
```

---

# 32. Đây là pattern cực kỳ quan trọng

Nếu function chỉ cần đọc text:

```rust
fn process(text: &str)
```

thường tốt hơn:

```rust
fn process(text: String)
```

nếu function không cần ownership.

Vì caller có thể truyền:

```rust
String
```

hoặc:

```rust
&str
```

---

# 33. Ví dụ API tốt

```rust
fn greet(name: &str) {
    println!("Hello, {name}");
}
```

Có thể gọi:

```rust
greet("Alice");
```

hoặc:

```rust
let name = String::from("Alice");

greet(&name);
```

Một function hỗ trợ cả hai.

---

# 34. Tại sao không dùng `String`?

Nếu viết:

```rust
fn greet(name: String)
```

thì:

```rust
greet("Alice");
```

không compile trực tiếp.

Bạn phải tạo owned `String`:

```rust
greet("Alice".to_string());
```

Không cần thiết nếu function chỉ đọc.

---

# 35. `&str` không ownership

Ví dụ:

```rust
fn main() {
    let text = String::from("Hello");

    let slice = &text;

    println!("{slice}");
}
```

`slice` không sở hữu:

```text
"Hello"
```

`text` mới sở hữu data.

---

# 36. Lifetime của `&str`

Ví dụ:

```rust
fn first_word(text: &str) -> &str {
    text.split_whitespace().next().unwrap()
}
```

`&str` trả về borrow từ:

```text
input text
```

Compiler hiểu lifetime relationship.

Conceptually:

```text
input
  │
  └─────── borrowed ───────► result
```

---

# 37. Không thể trả về reference tới local String

Code sai:

```rust
fn create() -> &str {
    let text = String::from("Hello");

    &text
}
```

Vì:

```text
text
 ↓
local variable
 ↓
function return
 ↓
text destroyed
```

Nếu trả `&str`, reference sẽ dangling.

Rust compiler chặn điều này.

---

# 38. Nhưng string literal thì khác

```rust
fn hello() -> &'static str {
    "Hello"
}
```

Hợp lệ.

Vì string literal có:

```text
'static
```

lifetime.

---

# 39. `&str` có thể trỏ vào nhiều nơi

Ví dụ:

```rust
let a: &str = "Hello";
```

Nó trỏ vào:

```text
static memory
```

Hoặc:

```rust
let s = String::from("Hello");
let b: &str = &s;
```

Nó trỏ vào:

```text
heap của String
```

Hoặc:

```rust
let slice = &some_array[..];
```

Tùy nguồn dữ liệu.

---

# 40. Vì vậy `&str` nói về abstraction, không phải memory location

`&str` chỉ nói:

```text
Tôi đang borrow một vùng UTF-8 string.
```

Nó không nói:

```text
Dữ liệu chắc chắn nằm trên heap.
```

Hoặc:

```text
Dữ liệu chắc chắn nằm trên stack.
```

---

# 41. String literal

```rust
let text = "Hello";
```

`text`:

```text
&'static str
```

Dữ liệu thường nằm trong vùng read-only/static của executable.

---

# 42. String slice của `String`

```rust
let text = String::from("Hello Rust");
let slice = &text[0..5];
```

`slice`:

```text
&str
```

trỏ vào:

```text
String's heap allocation
```

---

# 43. Cùng type, khác source

```text
"Hello"
   ↓
&'static str
```

và:

```text
String::from("Hello")
        ↓
&String
        ↓
&str
```

Cả hai cuối cùng đều có:

```text
&str
```

nhưng lifetime và ownership khác nhau.

---

# 44. Slice không tạo allocation

Ví dụ:

```rust
let text = String::from("Hello Rust");

let a = &text[0..5];
let b = &text[6..10];
```

Có:

```text
1 allocation
```

cho `String`.

Không có thêm allocation cho:

```text
a
b
```

---

# 45. Đây là lý do slice rất hiệu quả

Bạn có:

```text
large String
```

và muốn parse:

```text
header
body
field
token
```

Bạn có thể tạo:

```text
&str
&str
&str
&str
```

mà không copy dữ liệu.

Đây là nền tảng của zero-copy parsing.

---

# 46. Ví dụ parser

```rust
fn parse_name(line: &str) -> &str {
    line.split(':').next().unwrap()
}
```

Ví dụ:

```rust
let line = "name:Alice";

let name = parse_name(line);

println!("{name}");
```

Output:

```text
name
```

`name` là borrowed slice.

Không tạo String mới.

---

# 47. `split()`

Một trong những API quan trọng:

```rust
let text = "hello world rust";

for word in text.split(' ') {
    println!("{word}");
}
```

Mỗi `word` là:

```text
&str
```

Không phải `String`.

---

# 48. `split_whitespace()`

```rust
let text = "hello   world";

for word in text.split_whitespace() {
    println!("{word}");
}
```

Các phần tử:

```text
&str
```

Đây là một ví dụ rất rõ về zero-copy parsing.

---

# 49. `split_at()`

Rust còn có:

```rust
let text = "Hello Rust";

let (left, right) = text.split_at(5);
```

Kết quả:

```text
left  = "Hello"
right = " Rust"
```

Cả hai đều:

```text
&str
```

Không allocation.

---

# 50. Nhưng `split_at()` cũng yêu cầu boundary

Ví dụ:

```rust
let text = "é";

let (a, b) = text.split_at(1);
```

sẽ panic.

Vì index `1` không phải UTF-8 boundary.

---

# 51. `split_at_checked()`

Trong Rust hiện đại có API checked để tránh panic:

```rust
let result = text.split_at_checked(1);
```

Nếu index không hợp lệ:

```text
None
```

Thay vì panic.

Tư duy:

```text
split_at()
    ↓
panic nếu invalid

split_at_checked()
    ↓
Option
```

---

# 52. Kiểm tra boundary

Rust cung cấp:

```rust
text.is_char_boundary(index)
```

Ví dụ:

```rust
let text = "é";

println!("{}", text.is_char_boundary(0));
println!("{}", text.is_char_boundary(1));
println!("{}", text.is_char_boundary(2));
```

Conceptually:

```text
true
false
true
```

---

# 53. Đây là API cực kỳ hữu ích

Nếu bạn đang làm parser byte-oriented:

```rust
if text.is_char_boundary(index) {
    let part = &text[..index];
}
```

Bạn đảm bảo slicing không panic.

---

# 54. `&str` không hỗ trợ indexing bằng integer

Không:

```rust
text[0]
```

Nhưng:

```rust
&text[0..5]
```

lại hợp lệ nếu boundary đúng.

Lý do:

```text
text[0]
```

không xác định rõ:

```text
byte?
char?
grapheme?
```

Rust buộc bạn nói rõ abstraction.

---

# 55. Đây là triết lý thiết kế rất hay

Rust không cố đoán:

```text
text[0]
```

Bạn phải chọn:

```text
bytes()
```

hoặc:

```text
chars()
```

hoặc:

```text
slice range
```

hoặc grapheme API từ crate Unicode phù hợp.

---

# 56. So sánh ba cách

```rust
let text = "Hello";
```

### Byte

```rust
text.as_bytes()
```

### Character

```rust
text.chars()
```

### String slice

```rust
&text[0..3]
```

Mỗi API giải quyết một vấn đề khác nhau.

---

# 57. Deep Dive: `&str` là borrowed view

Đây là câu bạn nên nhớ:

> `&str` không phải là một String nhỏ; nó là một **view** vào UTF-8 data đang tồn tại ở đâu đó.

Ví dụ:

```text
String
┌────────────────────┐
│ Hello Rust         │
└────────────────────┘
       ▲
       │
      &str
```

---

# 58. Multiple slices

Bạn có thể:

```rust
let text = String::from("Hello Rust");

let a = &text[0..5];
let b = &text[6..10];
```

Cả hai:

```text
a ─────► Hello
b ─────► Rust
```

cùng borrow một allocation.

---

# 59. Borrow checker

Ví dụ:

```rust
let mut text = String::from("Hello");

let slice = &text[0..5];

text.push_str(" Rust");

println!("{slice}");
```

Code này không compile.

Tại sao?

Vì `slice` đang immutable borrow:

```text
slice
  │
  └──► text
```

Bạn không thể đồng thời mutable borrow:

```text
text.push_str(...)
```

---

# 60. Mental model

Khi có:

```rust
let slice = &text[..];
```

thì:

```text
text
 │
 └──── immutable borrow ───► slice
```

Không thể trong cùng lifetime:

```text
&mut text
```

---

# 61. Đây là điều cực kỳ quan trọng trong parser

Ví dụ:

```rust
fn parse(text: &str) -> Vec<&str> {
    text.split_whitespace().collect()
}
```

Function này có thể trả về nhiều slices:

```text
input
 │
 ├──► &str
 ├──► &str
 ├──► &str
 └──► &str
```

Tất cả borrow từ input.

Không cần clone từng token.

---

# 62. Nhưng Vec đó không sở hữu strings

```rust
let words = parse("hello rust");
```

`words` chứa:

```text
Vec<&str>
```

không phải:

```text
Vec<String>
```

Nếu source string biến mất, các slices không thể sống tiếp.

---

# 63. Đây là zero-copy parser

Pattern:

```text
input: &str
   │
   ├── token: &str
   ├── token: &str
   ├── token: &str
   └── token: &str
```

Không:

```text
String
String
String
String
```

Đây là một trong những kỹ thuật Rust rất mạnh.

---

# 64. Khi nào phải dùng `String`?

Nếu dữ liệu cần sống độc lập với source:

```rust
let owned = token.to_string();
```

Khi đó:

```text
&str
 ↓
String
```

và dữ liệu được copy/allocate.

---

# 65. So sánh

### Borrowed

```rust
let token: &str = ...
```

Ưu điểm:

* nhanh
* không allocation
* không copy
* zero-copy

Nhược điểm:

* phụ thuộc lifetime source

### Owned

```rust
let token: String = ...
```

Ưu điểm:

* độc lập source
* có thể giữ lâu

Nhược điểm:

* allocation
* copy dữ liệu

---

# 66. Pattern thiết kế API

Nếu function chỉ đọc:

```rust
fn parse(input: &str)
```

Nếu function cần giữ dữ liệu:

```rust
fn create(input: &str) -> String
```

Nếu function cần ownership:

```rust
fn consume(input: String)
```

Đây là cách chọn type rất quan trọng trong Rust.

---

# 67. Bài tập 1

Không chạy code, dự đoán:

```rust
fn main() {
    let text = String::from("Hello Rust");

    let a = &text[0..5];
    let b = &text[6..10];

    println!("{a}");
    println!("{b}");
}
```

Kết quả?

---

# 68. Bài tập 2

Code này có lỗi gì?

```rust
fn main() {
    let text = "é";

    let part = &text[0..1];

    println!("{part}");
}
```

Giải thích chính xác:

```text
1. "é" có bao nhiêu bytes?
2. UTF-8 bytes là gì?
3. index 1 nằm ở đâu?
4. Tại sao Rust panic?
```

---

# 69. Bài tập 3

Viết:

```rust
fn first_word(text: &str) -> &str
```

Ví dụ:

```rust
first_word("hello rust")
```

→

```text
"hello"
```

Gợi ý:

```rust
split_whitespace()
```

---

# 70. Bài tập 4

Viết:

```rust
fn words(text: &str) -> Vec<&str>
```

Ví dụ:

```rust
words("Rust is fast")
```

→

```text
["Rust", "is", "fast"]
```

Yêu cầu:

> Không tạo `String` cho từng word.

---

# 71. Bài tập 5 — UTF-8 Boundary

Với:

```rust
let text = "aé中🦀";
```

Hãy xác định các byte boundary hợp lệ.

Tính:

```rust
text.len()
```

và vẽ:

```text
byte index:
0
1
2
3
...
```

Sau đó xác định:

```rust
&text[0..1]
&text[1..3]
&text[3..6]
&text[6..10]
```

cái nào hợp lệ.

---

# 72. Bài tập 6 — Memory Deep Dive

Phân tích:

```rust
fn main() {
    let text = String::from("Hello Rust");

    let a = &text[0..5];
    let b = &text[6..10];

    println!("{a}");
    println!("{b}");
}
```

Hãy vẽ memory:

```text
STACK
┌───────────────┐
│ text          │
├───────────────┤
│ a             │
├───────────────┤
│ b             │
└───────────────┘

HEAP
┌─────────────────────┐
│ Hello Rust          │
└─────────────────────┘
```

và xác định:

```text
text.ptr
text.len
text.capacity

a.ptr
a.len

b.ptr
b.len
```

---

# 73. Bài tập 7 — Borrow Checker

Đoạn code này có compile không?

```rust
fn main() {
    let mut text = String::from("Hello");

    let slice = &text[..];

    text.push_str(" Rust");

    println!("{slice}");
}
```

Nếu không compile:

1. Xác định immutable borrow.
2. Xác định mutable borrow.
3. Giải thích conflict.
4. Viết lại code hợp lệ.

---

# 74. Bài tập 8 — Zero-Copy Parser

Viết function:

```rust
fn parse_user(input: &str) -> (&str, &str)
```

Input:

```text
"alice:12345"
```

Output:

```text
("alice", "12345")
```

Yêu cầu:

* Không tạo `String`.
* Không clone.
* Không allocation.
* Hai kết quả phải là `&str`.

Gợi ý:

```rust
split_once(':')
```

---

# 75. Tổng kết Buổi 9

Mental model quan trọng nhất:

```text
String
│
│ owns
▼
UTF-8 bytes
│
│ borrow
▼
&str
```

`&str`:

```text
┌──────────────┐
│ pointer      │
│ length       │
└──────────────┘
```

String slice:

```rust
&text[start..end]
```

không copy dữ liệu:

```text
String
┌─────────────────────┐
│ Hello Rust          │
└─────────────────────┘
  ▲─────▲
    &str
```

Nhưng `start` và `end` **phải là UTF-8 boundaries**.

```text
ASCII:
H e l l o
0 1 2 3 4 5

Unicode:
é = C3 A9
0       1       2
│       │       │
boundary       boundary
```

Vì vậy:

```rust
&"Hello"[0..2]   // OK
&"é"[0..2]       // OK
&"é"[0..1]       // panic
```

Và cuối cùng, hãy nhớ sự khác biệt:

```text
char
 ↓
Unicode scalar value

&str
 ↓
borrowed UTF-8 string

String
 ↓
owned UTF-8 string

u8
 ↓
one byte

&[u8]
 ↓
borrowed bytes
```

**Buổi 10** sẽ đi sâu vào **Lifetime của String Literal `'static`**: tại sao `"hello"` có thể sống suốt chương trình, `&'static str` thực sự có nghĩa gì, string literal được lưu ở đâu, lifetime annotation hoạt động thế nào, và vì sao function có thể trả về `&'static str` nhưng không thể trả về reference tới một `String` local.
