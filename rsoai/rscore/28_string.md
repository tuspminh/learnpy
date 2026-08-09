# Rust — Phần III: Ownership

# Buổi 28 — `String`

Hôm nay chúng ta đi sâu vào **`String`**. Đây là bài rất quan trọng vì `String` là nơi bạn bắt đầu thấy rõ sự kết hợp giữa:

```text
Ownership
   ↓
Heap
   ↓
Borrow
   ↓
Slice
   ↓
UTF-8
   ↓
&str
```

Mục tiêu sau buổi này:

* Hiểu `String` thực sự là gì.
* Phân biệt `String` với `&str`.
* Hiểu Stack/Heap của `String`.
* Thành thạo `push`, `push_str`, `+`, `format!`.
* Hiểu `len()` và UTF-8.
* Thành thạo `chars()`, `bytes()`.
* Hiểu `as_str()`, `as_bytes()`.
* Hiểu `capacity()`, `reserve()`, `shrink_to_fit()`.
* Hiểu ownership khi thao tác với `String`.
* Biết khi nào nên dùng `String`, khi nào dùng `&str`.

---

# 1. `String` là gì?

Trong Rust:

```rust
let name = String::from("Rust");
```

`name` có type:

```text
String
```

Đây là một **owned, growable UTF-8 string**.

Có thể hiểu:

```text
String
├── sở hữu dữ liệu
├── dữ liệu nằm trên heap
├── có thể thay đổi kích thước
└── chứa UTF-8
```

---

# 2. `String` khác gì String Literal?

So sánh:

```rust
let a = "Hello";
let b = String::from("Hello");
```

Type:

```text
a
└── &str

b
└── String
```

Có thể hình dung:

```text
"Hello"
   │
   └── borrowed string slice

String::from("Hello")
   │
   └── owned String
```

---

# 3. Chương trình đầu tiên

```rust
fn main() {
    let name = String::from("Rust");

    println!("{name}");
}
```

Chạy:

```bash
cargo run
```

Kết quả:

```text
Rust
```

---

# 4. Vì sao cần `String`?

String literal:

```rust
let text = "Hello";
```

không thể thay đổi nội dung theo cách thông thường.

Ví dụ:

```rust
let mut text = "Hello";

text.push_str(" Rust");
```

Code này không hợp lệ vì `text` là `&str`.

Trong khi:

```rust
let mut text = String::from("Hello");

text.push_str(" Rust");
```

hoàn toàn hợp lệ.

---

# 5. `String` có thể grow

```rust
fn main() {
    let mut text = String::from("Hello");

    text.push_str(" Rust");

    println!("{text}");
}
```

Kết quả:

```text
Hello Rust
```

---

# 6. `String` nằm ở đâu?

Đây là phần quan trọng.

```rust
let name = String::from("Rust");
```

Có thể hình dung:

```text
Stack
┌──────────────┐
│ ptr          │──────┐
│ length = 4   │      │
│ capacity = 4 │      │
└──────────────┘      │
                      ▼
                    Heap
              ┌─────────────┐
              │ R u s t     │
              └─────────────┘
```

`String` trên stack chứa metadata.

Dữ liệu string thực tế nằm trên heap.

---

# 7. Ba thành phần quan trọng

Một `String` conceptually có:

```text
pointer
length
capacity
```

Ví dụ:

```rust
let text = String::from("Hello");
```

Có thể hình dung:

```text
pointer ───────► H e l l o
length = 5
capacity >= 5
```

---

# 8. `len()`

```rust
fn main() {
    let text = String::from("Hello");

    println!("{}", text.len());
}
```

Kết quả:

```text
5
```

Nhưng cần nhớ:

> `String::len()` trả về số **byte**, không phải số ký tự nhìn thấy.

Điều này cực kỳ quan trọng với Unicode.

---

# 9. ASCII

Với ASCII:

```rust
let text = String::from("Hello");
```

Mỗi ký tự:

```text
H → 1 byte
e → 1 byte
l → 1 byte
l → 1 byte
o → 1 byte
```

Do đó:

```rust
text.len()
```

bằng:

```text
5
```

---

# 10. Unicode

Bây giờ:

```rust
fn main() {
    let text = String::from("Xin chào");

    println!("bytes = {}", text.len());
    println!("chars = {}", text.chars().count());
}
```

Bạn sẽ thấy hai giá trị khác nhau.

Tại sao?

Vì Rust lưu String dưới dạng UTF-8.

Ví dụ:

```text
X       → 1 byte
i       → 1 byte
n       → 1 byte
space   → 1 byte
c       → 1 byte
h       → 1 byte
à       → nhiều byte
o       → 1 byte
```

---

# 11. UTF-8 là nền tảng của `String`

Rust `String` luôn chứa UTF-8 hợp lệ.

Điều này có nghĩa:

```text
String
   ↓
UTF-8 bytes
   ↓
không phải array char
```

Đừng nghĩ:

```text
String = Vec<char>
```

Không phải.

---

# 12. `push()`

Thêm một `char`:

```rust
fn main() {
    let mut text = String::from("Rust");

    text.push('!');

    println!("{text}");
}
```

Kết quả:

```text
Rust!
```

Syntax:

```rust
text.push(char);
```

Ví dụ:

```rust
text.push('A');
text.push('你');
text.push('😊');
```

---

# 13. `push_str()`

Thêm một `&str`:

```rust
fn main() {
    let mut text = String::from("Hello");

    text.push_str(" Rust");

    println!("{text}");
}
```

Kết quả:

```text
Hello Rust
```

Syntax:

```rust
text.push_str(&str);
```

---

# 14. `push` vs `push_str`

| Method       | Nhận   |
| ------------ | ------ |
| `push()`     | `char` |
| `push_str()` | `&str` |

Ví dụ:

```rust
text.push('!');
```

và:

```rust
text.push_str(" Rust");
```

---

# 15. `String + &str`

Rust hỗ trợ:

```rust
let result = a + &b;
```

Ví dụ:

```rust
fn main() {
    let a = String::from("Hello ");
    let b = String::from("Rust");

    let result = a + &b;

    println!("{result}");
}
```

Kết quả:

```text
Hello Rust
```

---

# 16. Nhưng có một điều rất quan trọng

Sau:

```rust
let result = a + &b;
```

biến:

```rust
a
```

không còn sử dụng được.

Vì `+` lấy ownership của `a`.

Conceptually:

```text
a
│
└────── ownership ──────► result
```

Còn:

```text
b
```

được borrow.

---

# 17. Test Move

```rust
fn main() {
    let a = String::from("Hello ");
    let b = String::from("Rust");

    let result = a + &b;

    println!("{result}");
    println!("{b}");

    // println!("{a}"); // lỗi
}
```

`a` đã bị move.

---

# 18. Vì sao `+` thiết kế như vậy?

Conceptually:

```rust
a + &b
```

gần với:

```rust
String + &str
```

Method tương ứng:

```rust
add(self, rhs: &str) -> String
```

Điểm quan trọng là:

```text
self
```

được consume.

Do đó:

```rust
a
```

bị move.

---

# 19. `format!()` thường dễ đọc hơn

Thay vì:

```rust
let result = first + " " + &last;
```

có thể dùng:

```rust
let result = format!("{first} {last}");
```

Ví dụ:

```rust
fn main() {
    let first = String::from("Hello");
    let last = String::from("Rust");

    let result = format!("{first} {last}");

    println!("{result}");
    println!("{first}");
    println!("{last}");
}
```

Cả `first` và `last` vẫn dùng được.

---

# 20. `format!()` không consume biến

Ví dụ:

```rust
let name = String::from("Rust");

let message = format!("Hello {name}");

println!("{name}");
```

Hợp lệ.

Đây là lý do `format!()` rất tiện khi xây dựng text.

---

# 21. `clone()`

Bạn có thể clone:

```rust
let a = String::from("Hello");
let b = a.clone();
```

Sau đó:

```rust
println!("{a}");
println!("{b}");
```

Cả hai đều tồn tại.

Nhưng:

```text
clone()
```

tạo bản sao dữ liệu.

Không nên lạm dụng `clone()` chỉ để né ownership.

---

# 22. `String::new()`

Có thể tạo String rỗng:

```rust
let mut text = String::new();
```

Sau đó:

```rust
text.push_str("Hello");
```

Ví dụ:

```rust
fn main() {
    let mut text = String::new();

    text.push_str("Hello");
    text.push(' ');

    text.push_str("Rust");

    println!("{text}");
}
```

Kết quả:

```text
Hello Rust
```

---

# 23. `String::with_capacity()`

Nếu biết trước dữ liệu sẽ lớn:

```rust
let mut text = String::with_capacity(100);
```

Rust cấp capacity ban đầu.

Ví dụ:

```rust
fn main() {
    let mut text = String::with_capacity(100);

    println!("length = {}", text.len());
    println!("capacity = {}", text.capacity());
}
```

Có thể cho:

```text
length = 0
capacity = 100
```

---

# 24. `len()` vs `capacity()`

Đây là hai khái niệm khác nhau.

```text
length
```

= số byte đang sử dụng.

```text
capacity
```

= số byte có thể chứa trước khi cần cấp phát thêm.

Ví dụ:

```text
capacity = 20
length   = 5
```

có nghĩa:

```text
đang dùng 5 byte
có chỗ cho tối đa 20 byte
```

---

# 25. Demo Capacity

```rust
fn main() {
    let mut text = String::with_capacity(10);

    println!("length   = {}", text.len());
    println!("capacity = {}", text.capacity());

    text.push_str("Hello");

    println!("length   = {}", text.len());
    println!("capacity = {}", text.capacity());
}
```

---

# 26. `reserve()`

Bạn có thể yêu cầu thêm capacity:

```rust
let mut text = String::new();

text.reserve(100);
```

Ví dụ:

```rust
fn main() {
    let mut text = String::new();

    text.reserve(100);

    println!("capacity = {}", text.capacity());
}
```

---

# 27. Vì sao `reserve()` hữu ích?

Giả sử bạn biết:

```text
sắp append rất nhiều dữ liệu
```

thay vì để String liên tục reallocate:

```text
grow
grow
grow
grow
```

có thể:

```rust
text.reserve(10_000);
```

Điều này có thể giúp giảm số lần allocation.

---

# 28. `shrink_to_fit()`

Nếu String đang có capacity dư:

```rust
text.shrink_to_fit();
```

Rust sẽ cố gắng giảm capacity về mức cần thiết.

Ví dụ:

```rust
fn main() {
    let mut text = String::with_capacity(1000);

    text.push_str("Hello");

    println!("before = {}", text.capacity());

    text.shrink_to_fit();

    println!("after = {}", text.capacity());
}
```

Capacity sau đó thường gần với số byte cần thiết, nhưng không nên dựa vào một con số cụ thể.

---

# 29. `clear()`

Xóa toàn bộ nội dung:

```rust
fn main() {
    let mut text = String::from("Hello Rust");

    text.clear();

    println!("text = '{text}'");
    println!("length = {}", text.len());
}
```

Kết quả:

```text
text = ''
length = 0
```

Điểm đáng chú ý:

`clear()` làm length về `0`, nhưng capacity thường vẫn được giữ lại.

Điều này hữu ích nếu bạn sẽ tái sử dụng String.

---

# 30. `is_empty()`

```rust
let text = String::new();

println!("{}", text.is_empty());
```

Kết quả:

```text
true
```

---

# 31. `contains()`

```rust
fn main() {
    let text = String::from("Rust is fast");

    println!("{}", text.contains("Rust"));
    println!("{}", text.contains("Python"));
}
```

Kết quả:

```text
true
false
```

---

# 32. `starts_with()`

```rust
let text = String::from("Rust Programming");

println!("{}", text.starts_with("Rust"));
```

Kết quả:

```text
true
```

---

# 33. `ends_with()`

```rust
let text = String::from("hello.rs");

println!("{}", text.ends_with(".rs"));
```

Kết quả:

```text
true
```

---

# 34. `replace()`

```rust
fn main() {
    let text = String::from("Rust is hard");

    let result = text.replace("hard", "powerful");

    println!("{result}");
}
```

Kết quả:

```text
Rust is powerful
```

Chú ý:

```rust
replace()
```

trả về String mới.

Nó không sửa String gốc.

---

# 35. `trim()`

```rust
fn main() {
    let text = "   Hello Rust   ";

    let trimmed = text.trim();

    println!("{trimmed}");
}
```

Kết quả:

```text
Hello Rust
```

`trim()` trả về:

```rust
&str
```

Đây là ví dụ rất hay về `String`/`&str`.

---

# 36. `to_string()`

Bạn có thể chuyển nhiều giá trị thành String:

```rust
let number = 123;

let text = number.to_string();
```

Type:

```text
String
```

Ví dụ:

```rust
fn main() {
    let number = 123;

    let text = number.to_string();

    println!("{text}");
}
```

---

# 37. `String::from()`

```rust
let text = String::from("Hello");
```

Đây là cách phổ biến để tạo String từ `&str`.

---

# 38. `to_owned()`

Bạn cũng có thể:

```rust
let text = "Hello".to_owned();
```

Kết quả:

```text
String
```

Về ý tưởng:

```text
&str
  ↓
to_owned()
  ↓
String
```

---

# 39. `as_str()`

Từ:

```rust
String
```

có thể lấy:

```rust
&str
```

Ví dụ:

```rust
fn print_text(text: &str) {
    println!("{text}");
}

fn main() {
    let text = String::from("Hello");

    print_text(text.as_str());
}
```

---

# 40. Nhưng thường không cần `as_str()`

Rust có coercion.

Do đó:

```rust
print_text(&text);
```

thường đã đủ.

Ví dụ:

```rust
fn print_text(text: &str) {
    println!("{text}");
}

fn main() {
    let text = String::from("Hello");

    print_text(&text);
}
```

---

# 41. `as_bytes()`

Bạn có thể lấy UTF-8 bytes:

```rust
fn main() {
    let text = String::from("Rust");

    let bytes = text.as_bytes();

    println!("{bytes:?}");
}
```

Kết quả dạng:

```text
[82, 117, 115, 116]
```

---

# 42. Tại sao `as_bytes()` quan trọng?

Nó cho phép làm việc ở tầng byte:

```text
String
  ↓
&str
  ↓
&[u8]
```

Ví dụ:

```rust
let text = String::from("Rust");

let bytes: &[u8] = text.as_bytes();
```

---

# 43. `chars()`

Nếu muốn duyệt Unicode characters:

```rust
fn main() {
    let text = String::from("Rust");

    for ch in text.chars() {
        println!("{ch}");
    }
}
```

Kết quả:

```text
R
u
s
t
```

---

# 44. Unicode với `chars()`

```rust
fn main() {
    let text = String::from("Xin chào");

    for ch in text.chars() {
        println!("{ch}");
    }
}
```

`chars()` duyệt theo Unicode scalar values, không phải byte.

---

# 45. `bytes()`

Nếu muốn duyệt byte:

```rust
fn main() {
    let text = String::from("Rust");

    for byte in text.bytes() {
        println!("{byte}");
    }
}
```

Kết quả:

```text
82
117
115
116
```

---

# 46. `chars()` vs `bytes()`

Đây là bảng cần nhớ:

| Method    | Duyệt                 |
| --------- | --------------------- |
| `chars()` | Unicode scalar values |
| `bytes()` | UTF-8 bytes           |

Ví dụ với:

```text
"à"
```

`chars()`:

```text
à
```

nhưng `bytes()` trả về nhiều byte.

---

# 47. Không thể index String như Array

Điều này **không hợp lệ**:

```rust
let text = String::from("Hello");

let c = text[0];
```

Rust không cho phép.

Tại sao?

Vì UTF-8:

```text
character ≠ byte
```

---

# 48. Tại sao Rust cấm String indexing?

Giả sử:

```text
"Xin chào"
```

Nếu:

```rust
text[0]
```

thì bạn đang hỏi:

> byte thứ 0 hay character thứ 0?

Rust không muốn có API mơ hồ.

Do đó bạn phải chọn:

```rust
text.bytes()
```

hoặc:

```rust
text.chars()
```

---

# 49. String Slice

Bạn có thể slice:

```rust
let text = String::from("Hello");

let hello = &text[0..5];
```

Type:

```text
&str
```

Nhưng boundary phải hợp lệ.

---

# 50. Ví dụ nguy hiểm

Không làm tùy tiện:

```rust
let text = String::from("é");

let part = &text[0..1];
```

Có thể panic vì `é` trong UTF-8 chiếm nhiều byte và byte index `1` không nằm tại character boundary.

---

# 51. Cách an toàn hơn

Nếu muốn lấy character:

```rust
let text = String::from("é");

if let Some(ch) = text.chars().next() {
    println!("{ch}");
}
```

---

# 52. `split_whitespace()`

Một thao tác cực kỳ hữu ích:

```rust
let text = "Rust is awesome";

for word in text.split_whitespace() {
    println!("{word}");
}
```

Kết quả:

```text
Rust
is
awesome
```

Các phần trả về là:

```rust
&str
```

---

# 53. `lines()`

Xử lý text nhiều dòng:

```rust
fn main() {
    let text = "line one\nline two\nline three";

    for line in text.lines() {
        println!("{line}");
    }
}
```

---

# 54. `String` với input

Đây là pattern cực kỳ quan trọng:

```rust
use std::io;

fn main() {
    let mut input = String::new();

    io::stdin()
        .read_line(&mut input)
        .unwrap();

    println!("You typed: {input}");
}
```

`read_line()` cần:

```rust
&mut String
```

vì nó ghi dữ liệu vào String.

---

# 55. Input hoàn chỉnh

```rust
use std::io;

fn main() {
    println!("Enter your name:");

    let mut name = String::new();

    io::stdin()
        .read_line(&mut name)
        .unwrap();

    let name = name.trim();

    println!("Hello, {name}!");
}
```

Ở đây:

```text
stdin
  ↓
&mut String
  ↓
trim()
  ↓
&str
```

Đây là một pipeline Rust rất điển hình.

---

# 56. `String` và Ownership

Ví dụ:

```rust
fn main() {
    let a = String::from("Hello");

    let b = a;

    println!("{b}");

    // println!("{a}"); // lỗi
}
```

Vì:

```text
a
 ↓ move
b
```

---

# 57. `String` và Borrow

```rust
fn print_text(text: &String) {
    println!("{text}");
}

fn main() {
    let text = String::from("Hello");

    print_text(&text);

    println!("{text}");
}
```

Không move.

Tuy nhiên API tốt hơn thường là:

```rust
fn print_text(text: &str)
```

---

# 58. API tốt hơn

Thay:

```rust
fn print_text(text: &String)
```

bằng:

```rust
fn print_text(text: &str)
```

Sau đó:

```rust
fn main() {
    let owned = String::from("Hello");
    let literal = "Rust";

    print_text(&owned);
    print_text(literal);
}

fn print_text(text: &str) {
    println!("{text}");
}
```

Function dùng được cả:

```text
String
&str
```

---

# 59. Một ví dụ thực tế — Text Builder

```rust
fn build_message(name: &str, age: u32) -> String {
    format!("Hello {name}, you are {age} years old.")
}

fn main() {
    let message = build_message("Alice", 25);

    println!("{message}");
}
```

Kết quả:

```text
Hello Alice, you are 25 years old.
```

Đây là một pattern tốt:

```text
Input
   ↓
&str

Output
   ↓
String
```

Vì function:

* không cần sở hữu input
* nhưng tạo và trả về dữ liệu mới

---

# 60. Một pattern cực kỳ quan trọng

```rust
fn normalize(text: &str) -> String {
    text.trim().to_lowercase()
}
```

Ví dụ:

```rust
fn main() {
    let input = "   RUST Programming   ";

    let result = normalize(input);

    println!("{result}");
}

fn normalize(text: &str) -> String {
    text.trim().to_lowercase()
}
```

Kết quả:

```text
rust programming
```

Đây là thiết kế API rất đẹp:

```text
&str → String
```

---

# 61. Mini Project — Text Processor

Bây giờ xây một mini project nhỏ.

Yêu cầu:

```text
Input:
"   Rust is fast and safe   "

Output:
Original
Trimmed
Word count
Character count
Byte count
Uppercase
```

Code:

```rust
fn word_count(text: &str) -> usize {
    text.split_whitespace().count()
}

fn char_count(text: &str) -> usize {
    text.chars().count()
}

fn normalize(text: &str) -> String {
    text.trim().to_string()
}

fn main() {
    let text = String::from("   Rust is fast and safe   ");

    let normalized = normalize(&text);

    println!("Original: '{}'", text);
    println!("Trimmed: '{}'", normalized);
    println!("Words: {}", word_count(&text));
    println!("Chars: {}", char_count(&text));
    println!("Bytes: {}", text.len());
    println!("Uppercase: {}", normalized.to_uppercase());
}
```

Chạy:

```bash
cargo run
```

---

# 62. Phiên bản có tiếng Việt

Thử:

```rust
fn main() {
    let text = String::from("   Xin chào Rust   ");

    println!("Bytes: {}", text.len());
    println!("Chars: {}", text.chars().count());

    for ch in text.chars() {
        print!("{ch} ");
    }

    println!();
}
```

Bạn sẽ thấy:

```text
bytes != chars
```

Đây là một trong những đặc điểm quan trọng nhất của Rust String.

---

# 63. Mini Project — Story Title Processor

Vì bạn đang xây hệ thống crawl/đọc truyện, hãy thử một bài gần với project thực tế.

```rust
struct Book {
    title: String,
    author: String,
}

fn normalize_title(title: &str) -> String {
    title.trim().to_string()
}

fn display_book(book: &Book) {
    println!("Title : {}", book.title);
    println!("Author: {}", book.author);
}

fn main() {
    let book = Book {
        title: String::from("   The Beginning After The End   "),
        author: String::from("TurtleMe"),
    };

    let normalized_title = normalize_title(&book.title);

    println!("Normalized title: {normalized_title}");

    display_book(&book);
}
```

Điểm cần chú ý:

```text
Book
 │
 ├── title: String
 │
 └── author: String
```

Khi truyền:

```rust
&book.title
```

function chỉ borrow String dưới dạng `&str`.

---

# 64. Mini Project — Chapter Parser

Một ví dụ gần với crawler:

```rust
fn parse_chapter_title(raw: &str) -> String {
    raw.trim().to_string()
}

fn parse_chapter_number(raw: &str) -> Option<u32> {
    raw.trim()
        .strip_prefix("Chapter ")?
        .parse()
        .ok()
}

fn main() {
    let raw_title = String::from("  Chapter 125  ");

    let title = parse_chapter_title(&raw_title);
    let number = parse_chapter_number(&raw_title);

    println!("Title : {title}");
    println!("Number: {number:?}");
}
```

Kết quả:

```text
Title : Chapter 125
Number: Some(125)
```

Đây là cách `String`, `&str`, ownership và parsing bắt đầu kết hợp với nhau.

---

# 65. Ownership Pipeline

Một pattern rất quan trọng:

```text
String
  │
  │ borrow
  ▼
&str
  │
  │ process
  ▼
String
```

Ví dụ:

```rust
fn normalize(text: &str) -> String {
    text.trim().to_lowercase()
}
```

Không cần:

```text
clone input
```

---

# 66. `String` không phải lúc nào cũng cần thiết

Nếu dữ liệu chỉ tồn tại cố định:

```rust
fn greeting() -> &'static str {
    "Hello Rust"
}
```

Không cần:

```rust
fn greeting() -> String {
    String::from("Hello Rust")
}
```

Nếu không cần ownership/growability, `&str` có thể phù hợp hơn.

---

# 67. Nhưng dữ liệu từ runtime thường là `String`

Ví dụ:

```text
User input
HTTP response
File content
Database data
Crawler content
Generated text
```

thường cần:

```rust
String
```

vì dữ liệu có lifetime động và cần ownership.

---

# 68. Quy tắc thực chiến

### Function nhận text để đọc:

```rust
fn process(text: &str)
```

### Function cần tạo text mới:

```rust
fn process(text: &str) -> String
```

### Struct sở hữu text:

```rust
struct Book {
    title: String,
}
```

### Text cố định:

```rust
let title: &str = "Rust";
```

---

# 69. Một lỗi thiết kế thường gặp

Không nên tự động viết:

```rust
fn process(text: &String)
```

chỉ vì biến của bạn là:

```rust
String
```

Hãy hỏi:

> Function có thực sự cần `String` hay chỉ cần nội dung text?

Nếu chỉ cần nội dung:

```rust
fn process(text: &str)
```

---

# 70. Bài tập 1 — String Builder

Viết function:

```rust
fn build_full_name(first: &str, last: &str) -> String
```

Input:

```text
"Nguyen"
"Dau"
```

Output:

```text
"Nguyen Dau"
```

---

# 71. Bài tập 2 — Normalize

Viết:

```rust
fn normalize(text: &str) -> String
```

Input:

```text
"   HELLO RUST   "
```

Output:

```text
"hello rust"
```

Gợi ý:

```rust
text.trim().to_lowercase()
```

---

# 72. Bài tập 3 — Word Count

Viết:

```rust
fn word_count(text: &str) -> usize
```

Input:

```text
"Rust is fast and safe"
```

Output:

```text
5
```

---

# 73. Bài tập 4 — Character Count

Viết:

```rust
fn char_count(text: &str) -> usize
```

Test:

```rust
println!("{}", char_count("Xin chào"));
```

Không dùng:

```rust
len()
```

Phải dùng:

```rust
chars().count()
```

---

# 74. Bài tập 5 — Byte Count

Viết:

```rust
fn byte_count(text: &str) -> usize
```

Test với:

```text
Hello
Xin chào
你好
😊
```

So sánh:

```text
bytes
chars
```

---

# 75. Bài tập 6 — Chapter Title

Viết:

```rust
fn clean_chapter_title(title: &str) -> String
```

Input:

```text
"   Chapter 100: The Beginning   "
```

Output:

```text
"Chapter 100: The Beginning"
```

---

# 76. Bài tập 7 — Chapter Number

Viết:

```rust
fn parse_chapter_number(title: &str) -> Option<u32>
```

Input:

```text
"Chapter 125"
```

Output:

```text
Some(125)
```

---

# 77. Bài tập 8 — Text Statistics

Tạo:

```rust
struct TextStats {
    bytes: usize,
    chars: usize,
    words: usize,
}
```

Viết:

```rust
fn analyze(text: &str) -> TextStats
```

Test:

```rust
let text = "Rust is fast and safe";

let stats = analyze(text);

println!("bytes = {}", stats.bytes);
println!("chars = {}", stats.chars);
println!("words = {}", stats.words);
```

---

# 78. Bài tập 9 — Mutable String

Viết chương trình:

```text
String ban đầu:
Rust

append:
" is awesome"

append:
"!"

Output:
Rust is awesome!
```

Bắt buộc sử dụng:

```rust
push_str()
push()
```

---

# 79. Bài tập 10 — Capacity

Viết chương trình:

```rust
let mut text = String::with_capacity(100);
```

Sau đó:

1. In capacity.
2. Append text.
3. In length.
4. In capacity.
5. `clear()`.
6. In length.
7. In capacity.

Quan sát điều gì thay đổi và điều gì không.

---

# 80. Bài tập 11 — API Design

Cho:

```rust
struct Book {
    title: String,
    description: String,
}
```

Viết:

```rust
fn print_book(book: &Book)
fn normalize_title(title: &str) -> String
fn count_words(text: &str) -> usize
```

Mục tiêu là tập thiết kế API bằng:

```text
&Book
&str
String
```

đúng mục đích.

---

# 81. Tổng kết `String`

Bạn cần nhớ bảng này:

| Thành phần       | Ý nghĩa                  |
| ---------------- | ------------------------ |
| `String`         | Owned, growable UTF-8    |
| `&str`           | Borrowed string slice    |
| `String::new()`  | String rỗng              |
| `String::from()` | Tạo String từ `&str`     |
| `push()`         | Thêm `char`              |
| `push_str()`     | Thêm `&str`              |
| `len()`          | Số byte                  |
| `chars()`        | Unicode scalar values    |
| `bytes()`        | UTF-8 bytes              |
| `capacity()`     | Capacity hiện tại        |
| `reserve()`      | Yêu cầu thêm capacity    |
| `clear()`        | Xóa nội dung             |
| `as_str()`       | `&str`                   |
| `as_bytes()`     | `&[u8]`                  |
| `trim()`         | Loại whitespace đầu/cuối |
| `format!()`      | Tạo String mới           |

---

# 82. Mental Model cuối buổi

Hãy nhớ sơ đồ này:

```text
                TEXT
                 │
        ┌────────┴────────┐
        │                 │
     String              &str
        │                 │
     OWNED              BORROWED
        │                 │
        │                 │
      Heap             Slice
        │                 │
        └────────┬────────┘
                 │
               UTF-8
                 │
        ┌────────┴────────┐
        │                 │
      bytes             chars
      &[u8]          Unicode values
```

Và đặc biệt:

```text
String
  │
  ├── len()       → bytes
  ├── capacity()  → allocated capacity
  ├── push()      → char
  ├── push_str()  → &str
  ├── chars()     → Unicode
  ├── bytes()     → UTF-8 bytes
  ├── as_str()    → &str
  └── as_bytes()  → &[u8]
```

---

## Roadmap tiếp theo

```text
✓ 21 Ownership
✓ 22 Move
✓ 23 Clone
✓ 24 Copy
✓ 25 Borrow
✓ 26 Mutable Borrow
✓ 27 Slice
✓ 28 String                 ← hôm nay
→ 29 String vs &str
  30 Ownership Deep Dive
```

**Buổi 29 — `String` vs `&str`** sẽ là bài cực kỳ quan trọng: chúng ta sẽ không chỉ học sự khác nhau về syntax mà sẽ đi sâu vào **ownership, borrowing, lifetime, heap, stack, API design, `&String` vs `&str`, coercion `String → &str`, `Cow<str>`, return `String`/`&str`, struct chứa String và lifetime**, kèm một mini project parser text theo kiểu production Rust.
