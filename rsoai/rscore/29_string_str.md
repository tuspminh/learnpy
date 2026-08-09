# Rust — Phần III: Ownership

# Buổi 29 — `String` vs `&str`

Đây là một trong những bài **quan trọng nhất của Rust Foundation**.

Nếu hiểu chắc bài này, bạn sẽ bắt đầu nhìn Rust theo đúng tư duy:

```text
Ownership
   ↓
Borrowing
   ↓
String / &str
   ↓
Lifetime
   ↓
API Design
```

Hôm nay mục tiêu không chỉ là biết:

```rust
String
```

khác:

```rust
&str
```

mà phải hiểu **tại sao Rust thiết kế như vậy và khi nào dùng loại nào**.

---

# 1. Hai kiểu dữ liệu quan trọng nhất

```rust
String
```

và:

```rust
&str
```

Ví dụ:

```rust
let a = String::from("Hello");
let b = "Hello";
```

Type:

```text
a
└── String

b
└── &str
```

---

# 2. `String` là gì?

`String` là:

```text
owned
growable
UTF-8
heap allocated
```

Ví dụ:

```rust
let mut text = String::from("Hello");

text.push_str(" Rust");
```

`String` sở hữu dữ liệu.

Có thể hình dung:

```text
Stack
┌─────────────────┐
│ String          │
│ ptr             │──────┐
│ len             │      │
│ capacity        │      │
└─────────────────┘      │
                         ▼
                       Heap
                 ┌─────────────┐
                 │ Hello Rust  │
                 └─────────────┘
```

---

# 3. `&str` là gì?

`&str` là:

> một borrowed string slice.

Ví dụ:

```rust
let text = "Hello";
```

`text` có type:

```rust
&'static str
```

Ở mức cơ bản ta viết:

```rust
&str
```

Nó không sở hữu dữ liệu.

Nó chỉ **tham chiếu tới một vùng text đã tồn tại**.

---

# 4. Mental model

Hãy nhớ:

```text
String
└── "Tôi sở hữu text này."

&str
└── "Tôi chỉ đang mượn text này."
```

Đây chính là khác biệt cốt lõi.

---

# 5. Ví dụ đơn giản

```rust
fn main() {
    let owned = String::from("Hello");
    let borrowed = &owned;

    println!("{owned}");
    println!("{borrowed}");
}
```

Ở đây:

```text
owned
  │
  ▼
String
  │
  └──── borrow ────► borrowed: &str
```

---

# 6. `&String` và `&str`

Đây là nơi người mới thường nhầm.

Có ba kiểu:

```rust
String
&String
&str
```

Chúng hoàn toàn khác nhau.

```text
String
  │
  └── owned

&String
  │
  └── borrow String

&str
  │
  └── borrow string data
```

---

# 7. `&String` không giống `&str`

Ví dụ:

```rust
let text = String::from("Hello");

let a: &String = &text;
let b: &str = &text;
```

Cả hai đều borrow `text`.

Nhưng:

```text
&String
```

borrow **đối tượng String**.

Trong khi:

```text
&str
```

borrow **string slice**.

---

# 8. Vì sao API thường dùng `&str`?

Giả sử:

```rust
fn print_text(text: &String) {
    println!("{text}");
}
```

Bạn có:

```rust
let a = String::from("Hello");

print_text(&a);
```

Hoạt động.

Nhưng function này chỉ nhận:

```text
&String
```

---

# 9. API tốt hơn

Viết:

```rust
fn print_text(text: &str) {
    println!("{text}");
}
```

Bây giờ:

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

Cả hai đều hoạt động.

Đây là lý do:

> Khi function chỉ cần đọc text, ưu tiên `&str` thay vì `&String`.

---

# 10. Vì sao `&String` có thể truyền vào `&str`?

Rust có cơ chế:

```text
Deref Coercion
```

Ví dụ:

```rust
let text = String::from("Hello");

print_text(&text);
```

Function:

```rust
fn print_text(text: &str)
```

Rust tự chuyển:

```text
&String
   ↓
&str
```

khi phù hợp.

---

# 11. Có thể viết rõ bằng `as_str()`

```rust
let text = String::from("Hello");

print_text(text.as_str());
```

Hoặc:

```rust
print_text(&text);
```

Thường:

```rust
&text
```

gọn hơn.

---

# 12. String literal

Khi viết:

```rust
let text = "Hello";
```

đây là:

```rust
&'static str
```

Tại sao có `'static`?

Vì string literal được lưu trong binary của chương trình và tồn tại trong suốt lifetime của chương trình.

Conceptually:

```text
Binary
┌──────────────────┐
│ "Hello"          │
│ "Rust"           │
│ "Programming"    │
└──────────────────┘
        ▲
        │
        │
       &str
```

---

# 13. `String::from`

Trong:

```rust
let text = String::from("Hello");
```

quá trình conceptually:

```text
"Hello"
  │
  │ borrow
  ▼
&str
  │
  │ create owned data
  ▼
String
```

String tạo bản sao dữ liệu vào vùng memory mà nó sở hữu.

---

# 14. `to_string()`

Tương tự:

```rust
let text = "Hello".to_string();
```

Kết quả:

```text
String
```

---

# 15. `to_owned()`

Cũng có:

```rust
let text = "Hello".to_owned();
```

Kết quả:

```text
String
```

Mental model:

```text
&str
 │
 ├── to_string()
 │
 ├── to_owned()
 │
 └── String::from()
 │
 ▼
String
```

---

# 16. Khi nào dùng `String`?

Dùng `String` khi bạn cần **ownership**.

Ví dụ:

### Struct sở hữu dữ liệu

```rust
struct Book {
    title: String,
    author: String,
}
```

Đây là thiết kế rất phổ biến.

---

# 17. Tại sao struct thường dùng `String`?

```rust
struct Book {
    title: String,
}
```

Book phải sở hữu title.

Ví dụ:

```rust
fn create_book(title: &str) -> Book {
    Book {
        title: title.to_string(),
    }
}
```

Input:

```text
&str
```

Output:

```text
Book
  └── String
```

Đây là pattern cực kỳ quan trọng.

---

# 18. API pattern

Một function tốt:

```rust
fn create_book(title: &str) -> Book {
    Book {
        title: title.to_owned(),
    }
}
```

Tại boundary:

```text
borrow
   ↓
&str
   ↓
function
   ↓
owned
   ↓
String
```

---

# 19. Ví dụ

```rust
struct Book {
    title: String,
}

fn create_book(title: &str) -> Book {
    Book {
        title: title.to_string(),
    }
}

fn main() {
    let book = create_book("The Rust Book");

    println!("{}", book.title);
}
```

Hoạt động với:

```rust
create_book("The Rust Book");
```

và:

```rust
let title = String::from("The Rust Book");

create_book(&title);
```

---

# 20. Function nhận `String`

Bạn có thể viết:

```rust
fn consume(text: String) {
    println!("{text}");
}
```

Function này lấy ownership.

Ví dụ:

```rust
fn main() {
    let text = String::from("Hello");

    consume(text);

    // println!("{text}"); // lỗi
}

fn consume(text: String) {
    println!("{text}");
}
```

Sau:

```rust
consume(text);
```

ownership chuyển vào function.

---

# 21. Function nhận `&str`

Nếu chỉ đọc:

```rust
fn read(text: &str) {
    println!("{text}");
}
```

Thì:

```rust
fn main() {
    let text = String::from("Hello");

    read(&text);

    println!("{text}");
}
```

`text` vẫn còn.

---

# 22. So sánh

```rust
fn consume(text: String) {}
```

nghĩa:

```text
Tôi cần ownership.
```

Trong khi:

```rust
fn read(text: &str) {}
```

nghĩa:

```text
Tôi chỉ cần đọc text.
```

Đây là tư duy API rất quan trọng.

---

# 23. Khi function trả về String

Ví dụ:

```rust
fn uppercase(text: &str) -> String {
    text.to_uppercase()
}
```

Input:

```text
&str
```

Output:

```text
String
```

Tại sao?

Vì `to_uppercase()` tạo dữ liệu mới.

---

# 24. Ví dụ

```rust
fn uppercase(text: &str) -> String {
    text.to_uppercase()
}

fn main() {
    let text = "hello rust";

    let result = uppercase(text);

    println!("{result}");
}
```

Kết quả:

```text
HELLO RUST
```

---

# 25. Pattern cực kỳ quan trọng

Bạn sẽ gặp pattern này rất nhiều trong Rust:

```rust
fn process(input: &str) -> String
```

Nó có nghĩa:

```text
input
  ↓
borrow
  ↓
process
  ↓
create new owned result
  ↓
String
```

Đây là một API rất tự nhiên.

---

# 26. Nhưng `&str` không phải lúc nào cũng trả về được

Ví dụ:

```rust
fn greeting() -> &str {
    let text = String::from("Hello");

    &text
}
```

Code này không compile.

Tại sao?

`text` được tạo bên trong function.

Khi function kết thúc:

```text
text
 ↓
drop
```

Nhưng bạn lại muốn trả về:

```text
&text
```

Reference sẽ trỏ tới dữ liệu đã bị hủy.

Rust ngăn điều này.

---

# 27. Phải trả về `String`

Viết:

```rust
fn greeting() -> String {
    String::from("Hello")
}
```

Đây là hợp lệ.

```rust
fn main() {
    let message = greeting();

    println!("{message}");
}

fn greeting() -> String {
    String::from("Hello")
}
```

---

# 28. Trường hợp trả về `&str` hợp lệ

String literal:

```rust
fn greeting() -> &'static str {
    "Hello"
}
```

Bởi vì:

```text
"Hello"
```

sống suốt chương trình.

Thực tế thường có thể viết:

```rust
fn greeting() -> &'static str {
    "Hello"
}
```

---

# 29. Return `&str` từ input

Có một pattern khác rất quan trọng:

```rust
fn first_word(text: &str) -> &str {
    text.split_whitespace()
        .next()
        .unwrap_or("")
}
```

Ví dụ:

```rust
fn main() {
    let text = String::from("Rust is fast");

    let first = first_word(&text);

    println!("{first}");
}
```

Kết quả:

```text
Rust
```

Ở đây `first` borrow từ `text`.

---

# 30. Điều gì đang xảy ra?

```text
String
"Rust is fast"
│
├───────────────┐
│               │
▼               ▼
"Rust"         "is fast"
  │
  └── &str
```

`first` không tạo String mới.

Nó chỉ là slice.

---

# 31. So sánh `first_word`

Cách 1:

```rust
fn first_word(text: &str) -> &str {
    text.split_whitespace()
        .next()
        .unwrap_or("")
}
```

Cách 2:

```rust
fn first_word(text: &str) -> String {
    text.split_whitespace()
        .next()
        .unwrap_or("")
        .to_string()
}
```

Khác nhau:

### `&str`

```text
zero-copy
borrowed
```

### `String`

```text
owned
allocation/copy
```

---

# 32. Đây là trade-off quan trọng

```text
&str
│
├── không cần allocation mới
├── nhanh
├── borrow dữ liệu
└── phụ thuộc lifetime dữ liệu gốc

String
│
├── sở hữu dữ liệu
├── độc lập với nguồn
├── có thể lưu lâu hơn
└── có thể cần allocation
```

---

# 33. Ví dụ zero-copy parser

Đây là kiểu code rất quan trọng khi sau này bạn làm parser/crawler:

```rust
fn extract_title(html: &str) -> &str {
    html
}
```

Conceptually:

```text
HTTP response String
       │
       ▼
     &str
       │
       ▼
    parser
       │
       ▼
    slices
```

Không nhất thiết phải clone mọi thứ.

---

# 34. `String` vs `&str` trong crawler

Ví dụ:

```rust
struct Chapter {
    title: String,
    content: String,
}
```

Đây là dữ liệu domain.

Bạn muốn:

```text
Chapter
  ├── sở hữu title
  └── sở hữu content
```

Nhưng parser có thể:

```rust
fn parse_title(html: &str) -> String
```

hoặc nếu chỉ cần xử lý tạm:

```rust
fn find_title(html: &str) -> &str
```

Đây là phân biệt rất quan trọng.

---

# 35. `&String` có nên dùng?

Thông thường:

```rust
fn foo(value: &String)
```

không phải lựa chọn tốt nhất nếu bạn chỉ cần đọc text.

Nên:

```rust
fn foo(value: &str)
```

Vì `&str` tổng quát hơn.

Nó nhận được:

```text
String
&String
&str
string literal
String slice
```

thông qua coercion phù hợp.

---

# 36. Ví dụ

```rust
fn print_title(title: &str) {
    println!("Title: {title}");
}

fn main() {
    let a = String::from("Rust");
    let b = "Programming";

    print_title(&a);
    print_title(b);
}
```

---

# 37. `&str` có thể là slice của String

```rust
let text = String::from("Hello Rust");

let part = &text[0..5];
```

Ta có:

```text
text
└── String

part
└── &str
     │
     └── "Hello"
```

Không có String mới được tạo.

---

# 38. Vì vậy `&str` rất phù hợp cho parser

Ví dụ:

```rust
fn parse_word(text: &str) -> Option<&str> {
    text.split_whitespace().next()
}
```

Test:

```rust
fn main() {
    let text = "Rust is awesome";

    let word = parse_word(text);

    println!("{word:?}");
}
```

Kết quả:

```text
Some("Rust")
```

---

# 39. Lifetime bắt đầu xuất hiện

Bạn chưa cần học sâu lifetime ở buổi này, nhưng phải nhìn thấy nó.

Function:

```rust
fn first_word(text: &str) -> &str
```

conceptually compiler hiểu:

```text
input lifetime
      │
      ▼
output lifetime
```

Output `&str` phải sống không lâu hơn dữ liệu mà nó borrow.

---

# 40. Vì sao điều này quan trọng?

Ví dụ:

```rust
fn first_word(text: &str) -> &str {
    text.split_whitespace().next().unwrap()
}
```

Compiler biết:

```text
first_word()
     │
     └── output borrow từ input
```

Do đó:

```rust
let text = String::from("Hello Rust");

let word = first_word(&text);

println!("{text}");
println!("{word}");
```

hợp lệ.

---

# 41. Nhưng không được trả reference tới local String

Sai:

```rust
fn make_text() -> &str {
    let text = String::from("Hello");

    &text
}
```

Đúng:

```rust
fn make_text() -> String {
    String::from("Hello")
}
```

Hoặc:

```rust
fn make_text() -> &'static str {
    "Hello"
}
```

---

# 42. Một nguyên tắc vàng

Hãy nhớ:

> Nếu function tạo dữ liệu mới và muốn trả ownership → `String`.

```rust
fn create() -> String
```

Nếu function chỉ trả về một phần của dữ liệu đầu vào → có thể `&str`.

```rust
fn extract(input: &str) -> &str
```

---

# 43. Ví dụ parser

```rust
fn extract_extension(path: &str) -> Option<&str> {
    path.rsplit('.').next()
}
```

Test:

```rust
fn main() {
    let path = "book/chapter001.html";

    if let Some(ext) = extract_extension(path) {
        println!("Extension: {ext}");
    }
}
```

Kết quả:

```text
Extension: html
```

Không cần tạo String mới.

---

# 44. Nhưng nếu muốn normalize extension

```rust
fn normalize_extension(path: &str) -> Option<String> {
    path.rsplit('.')
        .next()
        .map(|ext| ext.to_lowercase())
}
```

Ở đây trả:

```text
Option<String>
```

vì `to_lowercase()` tạo dữ liệu mới.

---

# 45. So sánh hai API

### Zero-copy

```rust
fn extension(path: &str) -> Option<&str>
```

### Owned

```rust
fn normalized_extension(path: &str) -> Option<String>
```

Đây chính là cách Rust API thường được thiết kế.

---

# 46. Một ví dụ thực tế hơn

```rust
struct Chapter {
    title: String,
}

fn parse_title(raw: &str) -> String {
    raw.trim().to_string()
}

fn main() {
    let html_title = "   Chapter 100   ";

    let chapter = Chapter {
        title: parse_title(html_title),
    };

    println!("{}", chapter.title);
}
```

Pipeline:

```text
raw HTML
   │
   ▼
&str
   │
   ▼
parse
   │
   ▼
String
   │
   ▼
Chapter
```

---

# 47. Khi nào `String` thắng?

Dùng `String` khi:

* Struct cần sở hữu dữ liệu.
* Dữ liệu được tạo runtime.
* Dữ liệu cần mutate.
* Muốn trả ownership khỏi function.
* Dữ liệu phải sống độc lập với input.
* Muốn lưu trữ lâu dài.

Ví dụ:

```rust
struct User {
    name: String,
}
```

---

# 48. Khi nào `&str` thắng?

Dùng `&str` khi:

* Chỉ cần đọc text.
* Không cần ownership.
* Không cần mutate nội dung.
* Function chỉ parse/inspect dữ liệu.
* Muốn tránh allocation.
* Chỉ cần một slice của dữ liệu hiện có.

Ví dụ:

```rust
fn word_count(text: &str) -> usize
```

---

# 49. Khi nào `&mut String`?

Khi bạn muốn sửa String hiện có:

```rust
fn append_suffix(text: &mut String) {
    text.push_str("!");
}
```

Test:

```rust
fn main() {
    let mut text = String::from("Hello");

    append_suffix(&mut text);

    println!("{text}");
}
```

Kết quả:

```text
Hello!
```

Nhưng nhiều API có thể nhận:

```rust
&mut String
```

nếu cần thao tác String-specific.

---

# 50. `&mut str`?

Rust cũng có:

```rust
&mut str
```

Nhưng ít gặp hơn.

Ví dụ:

```rust
fn main() {
    let mut text = String::from("hello");

    let slice = &mut text[..];

    println!("{slice}");
}
```

Bạn sẽ học sâu hơn khi đi vào slice và lifetime nâng cao.

---

# 51. Bảng tổng hợp

| Type          | Ownership | Mutable | Mục đích            |
| ------------- | --------: | ------: | ------------------- |
| `String`      |        Có |      Có | Owned text          |
| `&String`     |     Không |   Không | Borrow String       |
| `&mut String` |     Không |      Có | Mutate String       |
| `&str`        |     Không |   Không | Borrow text         |
| `&mut str`    |     Không |      Có | Mutate string slice |

---

# 52. Quy tắc API rất quan trọng

Nếu function chỉ đọc:

```rust
fn process(text: &str)
```

Nếu function cần mutate String:

```rust
fn process(text: &mut String)
```

Nếu function cần lấy ownership:

```rust
fn process(text: String)
```

Nếu function tạo String mới:

```rust
fn process(text: &str) -> String
```

Hãy học thuộc 4 pattern này.

---

# 53. Ví dụ hoàn chỉnh

```rust
struct Book {
    title: String,
    author: String,
}

fn create_book(title: &str, author: &str) -> Book {
    Book {
        title: title.to_owned(),
        author: author.to_owned(),
    }
}

fn normalize_title(title: &str) -> String {
    title.trim().to_string()
}

fn print_book(book: &Book) {
    println!("Title : {}", book.title);
    println!("Author: {}", book.author);
}

fn main() {
    let raw_title = "   The Rust Programming Language   ";
    let raw_author = "Steve Klabnik";

    let title = normalize_title(raw_title);

    let book = create_book(&title, raw_author);

    print_book(&book);
}
```

Đây là một ví dụ rất tốt về:

```text
&str
 ↓
String
 ↓
struct ownership
 ↓
&Book
```

---

# 54. Mini Project — Text Parser

Bây giờ xây một parser nhỏ.

Input:

```text
"  Rust | Steve | 2026  "
```

Ta muốn:

```text
title  = "Rust"
author = "Steve"
year   = 2026
```

---

## Bước 1 — Struct

```rust
struct Book {
    title: String,
    author: String,
    year: u32,
}
```

---

## Bước 2 — Parser

```rust
fn parse_book(input: &str) -> Option<Book> {
    let mut parts = input.split('|');

    let title = parts.next()?.trim().to_string();
    let author = parts.next()?.trim().to_string();
    let year = parts.next()?.trim().parse().ok()?;

    Some(Book {
        title,
        author,
        year,
    })
}
```

---

## Bước 3 — Test

```rust
fn main() {
    let input = "  Rust | Steve | 2026  ";

    let book = parse_book(input);

    match book {
        Some(book) => {
            println!("Title : {}", book.title);
            println!("Author: {}", book.author);
            println!("Year  : {}", book.year);
        }

        None => {
            println!("Invalid book");
        }
    }
}
```

Kết quả:

```text
Title : Rust
Author: Steve
Year  : 2026
```

---

# 55. Phân tích ownership của parser

Input:

```rust
fn parse_book(input: &str)
```

Parser **không sở hữu input**.

Nhưng:

```rust
title: parts.next()?.trim().to_string()
```

tạo:

```text
String
```

Tương tự:

```text
author
```

được chuyển thành:

```text
String
```

Do đó `Book` sở hữu toàn bộ dữ liệu.

Sơ đồ:

```text
input: &str
     │
     ▼
 parser
     │
     ├── title → String
     ├── author → String
     └── year → u32
                │
                ▼
              Book
```

Đây là thiết kế cực kỳ tốt cho domain model.

---

# 56. Zero-copy version

Nếu chỉ muốn lấy title tạm thời:

```rust
fn extract_title(input: &str) -> Option<&str> {
    input
        .split('|')
        .next()
        .map(str::trim)
}
```

Test:

```rust
fn main() {
    let input = "  Rust | Steve | 2026  ";

    let title = extract_title(input);

    println!("{title:?}");
}
```

Kết quả:

```text
Some("Rust")
```

Không tạo String mới.

---

# 57. Đây là tư duy Rust quan trọng

Hai function:

```rust
fn extract_title(input: &str) -> Option<&str>
```

và:

```rust
fn parse_book(input: &str) -> Option<Book>
```

có hai mục tiêu khác nhau.

### `&str`

```text
borrow
zero-copy
temporary view
```

### `String`

```text
own
independent data
longer-lived result
```

---

# 58. Sai lầm phổ biến #1

Viết mọi function:

```rust
fn foo(text: String)
```

Điều này làm function lấy ownership không cần thiết.

Thường nên:

```rust
fn foo(text: &str)
```

nếu chỉ đọc.

---

# 59. Sai lầm phổ biến #2

Viết:

```rust
fn foo(text: &String)
```

trong mọi trường hợp.

Thông thường:

```rust
&str
```

linh hoạt hơn.

---

# 60. Sai lầm phổ biến #3

Clone chỉ để tránh borrow:

```rust
let copy = text.clone();

foo(copy);
```

Nếu `foo` chỉ cần đọc:

```rust
foo(&text);
```

thường tốt hơn.

---

# 61. Sai lầm phổ biến #4

Trả về reference tới dữ liệu local:

```rust
fn make() -> &str {
    let s = String::from("Hello");

    &s
}
```

Không hợp lệ.

Phải:

```rust
fn make() -> String {
    String::from("Hello")
}
```

---

# 62. Sai lầm phổ biến #5

Nhầm `String` với `&str`

Không phải:

```text
String = &str
```

Mà:

```text
String
   │
   │ borrow
   ▼
&str
```

---

# 63. Bài tập 1

Viết:

```rust
fn greet(name: &str) -> String
```

Input:

```text
"Rust"
```

Output:

```text
"Hello, Rust!"
```

---

# 64. Bài tập 2

Viết:

```rust
fn first_word(text: &str) -> &str
```

Test:

```rust
let text = "Rust is awesome";

println!("{}", first_word(text));
```

Output:

```text
Rust
```

Không tạo String mới.

---

# 65. Bài tập 3

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

---

# 66. Bài tập 4

Cho:

```rust
struct User {
    name: String,
    email: String,
}
```

Viết:

```rust
fn create_user(name: &str, email: &str) -> User
```

Không truyền:

```rust
String
```

vào function.

---

# 67. Bài tập 5

Viết:

```rust
fn extension(path: &str) -> Option<&str>
```

Test:

```rust
extension("book/chapter001.html")
```

Kết quả:

```text
Some("html")
```

---

# 68. Bài tập 6

Viết:

```rust
fn normalized_extension(path: &str) -> Option<String>
```

Test:

```rust
"book/CHAPTER001.HTML"
```

Kết quả:

```text
Some("html")
```

---

# 69. Bài tập 7 — API Design

Cho ba function:

```rust
fn a(text: ???)
fn b(text: ???)
fn c(text: ???)
```

Chọn type phù hợp:

### A

Function chỉ in text.

```text
?
```

### B

Function sửa nội dung String.

```text
?
```

### C

Function lấy ownership và lưu text vào struct.

```text
?
```

Đáp án nên là:

```text
A → &str
B → &mut String
C → String
```

---

# 70. Bài tập 8 — Parser

Tạo:

```rust
struct Chapter {
    title: String,
    number: u32,
}
```

Viết:

```rust
fn parse_chapter(input: &str) -> Option<Chapter>
```

Input:

```text
"Chapter 125 | The Beginning"
```

Output:

```text
Chapter {
    title: "The Beginning",
    number: 125,
}
```

---

# 71. Bài tập 9 — Zero-copy

Viết:

```rust
fn chapter_title(input: &str) -> Option<&str>
```

Input:

```text
"125|The Beginning"
```

Output:

```text
Some("The Beginning")
```

Không `.to_string()`.

---

# 72. Bài tập 10 — Ownership Challenge

Đoạn code:

```rust
fn main() {
    let title = String::from("Rust");

    let a = get_title(&title);

    println!("{title}");
    println!("{a}");
}

fn get_title(title: &str) -> &str {
    title
}
```

Hãy giải thích:

1. `title` trong `main` là gì?
2. `&title` là gì?
3. `title` trong `get_title()` là gì?
4. `a` là gì?
5. Có String nào được clone không?
6. Ai sở hữu dữ liệu?

Đáp án:

```text
main::title
    ↓
String
    ↓ borrow
&String
    ↓ deref coercion
&str
    ↓
get_title()
    ↓
&str
    ↓
a
```

Chỉ có **một String** sở hữu dữ liệu.

---

# 73. Cheat Sheet

```text
String
------
Owned
Heap
Growable
UTF-8
Có ownership


&str
---
Borrowed
String slice
Không ownership
UTF-8 view


Function chỉ đọc:
fn foo(text: &str)


Function sửa String:
fn foo(text: &mut String)


Function lấy ownership:
fn foo(text: String)


Function tạo text mới:
fn foo(text: &str) -> String


Struct sở hữu text:
struct X {
    text: String,
}


String → &str:
&string
string.as_str()


&str → String:
String::from(text)
text.to_string()
text.to_owned()
```

---

# 74. Mental Model cuối buổi

Đừng học thuộc máy móc.

Hãy suy nghĩ:

```text
                    TEXT
                     │
          ┌──────────┴──────────┐
          │                     │
       String                  &str
          │                     │
       OWNED                  BORROWED
          │                     │
       mutable               read/view
          │                     │
       heap data             slice
          │                     │
          └──────────┬──────────┘
                     │
                 API DESIGN
                     │
       ┌─────────────┼──────────────┐
       │             │              │
      String        &str         &mut String
       │             │              │
   ownership       read          mutation
```

Và quy tắc quan trọng nhất:

> **Function chỉ cần đọc text → `&str`.
> Function cần sở hữu text → `String`.
> Function cần sửa String → `&mut String`.**

Đây là một trong những quy tắc API quan trọng nhất bạn sẽ sử dụng xuyên suốt Rust.

---

## Tiếp theo: Buổi 30 — Ownership Deep Dive

Buổi cuối của phần Ownership sẽ tổng hợp toàn bộ:

```text
Ownership
Move
Clone
Copy
Borrow
Mutable Borrow
Slice
String
&str
Lifetime
Deref Coercion
Stack / Heap
Drop
RAII
```

và đặc biệt chúng ta sẽ xây một **mini project quản lý Book/Chapter bằng Rust**, để bạn phải tự quyết định chỗ nào dùng:

```rust
String
&str
&mut String
&Book
```

thay vì chỉ học lý thuyết.
