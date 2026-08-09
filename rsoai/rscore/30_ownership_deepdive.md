# Rust — Phần III: Ownership

# Buổi 30 — Ownership Deep Dive

Đây là **buổi tổng kết Ownership**, nhưng cũng là buổi rất quan trọng vì từ đây chúng ta sẽ chuyển sang các phần khó hơn của Rust.

Mục tiêu hôm nay:

```text
Ownership
├── Stack / Heap
├── Move
├── Clone
├── Copy
├── Borrow
├── Mutable Borrow
├── Slice
├── String / &str
├── Drop
├── RAII
├── Deref Coercion
├── Lifetime cơ bản
└── Ownership trong thiết kế API
```

Cuối buổi chúng ta xây một **mini project quản lý Book/Chapter** có thể chạy ngay.

---

# 1. Ownership thực sự giải quyết vấn đề gì?

Trong các ngôn ngữ có garbage collector, bạn thường không trực tiếp quan tâm:

```text
Ai sở hữu object?
Khi nào object bị hủy?
Có bao nhiêu reference?
Reference còn hợp lệ không?
```

Rust thì khác.

Rust muốn đảm bảo:

```text
1. Không use-after-free
2. Không double free
3. Không dangling pointer
4. Không data race
5. Memory được giải phóng tự động
```

nhưng:

> Không cần garbage collector.

Đó chính là sức mạnh của Ownership.

---

# 2. Ba quy tắc Ownership

Rust có ba quy tắc nền tảng.

### Rule 1

> Mỗi value có một owner.

### Rule 2

> Chỉ có một owner tại một thời điểm.

### Rule 3

> Khi owner ra khỏi scope, value được drop.

Ví dụ:

```rust
fn main() {
    let name = String::from("Rust");

    println!("{name}");
}
```

Khi `main()` kết thúc:

```text
name
 ↓
drop
 ↓
String memory được giải phóng
```

---

# 3. Stack và Heap

Đây là nền tảng để hiểu Ownership.

## Stack

Thường chứa dữ liệu có kích thước cố định.

Ví dụ:

```rust
let x = 10;
let y = true;
```

Conceptually:

```text
Stack
┌─────────────┐
│ x = 10      │
│ y = true    │
└─────────────┘
```

---

# 4. Heap

Dữ liệu có kích thước động thường cần heap.

Ví dụ:

```rust
let text = String::from("Hello");
```

Conceptually:

```text
Stack
┌─────────────────┐
│ String          │
│ ptr ────────────┼──────┐
│ len = 5         │      │
│ capacity = 5    │      │
└─────────────────┘      │
                         ▼
Heap
┌─────────────────┐
│ Hello           │
└─────────────────┘
```

`String` trên stack chứa metadata.

Dữ liệu text thực tế nằm trên heap.

---

# 5. Vì sao `String` cần Ownership?

Vì heap memory phải có người chịu trách nhiệm.

Ví dụ:

```rust
let a = String::from("Hello");
```

Ta có:

```text
a
│
├── ptr
├── len
└── capacity
       │
       ▼
     Heap
    "Hello"
```

`a` là owner.

Khi `a` bị drop:

```text
a
 ↓
drop
 ↓
free heap
```

---

# 6. Move

Ví dụ:

```rust
let a = String::from("Hello");
let b = a;
```

Đây không phải deep copy.

Ownership chuyển:

```text
a
 │
 ▼
String
 │
 │ move
 ▼
b
```

Sau đó:

```rust
// println!("{a}");
```

không hợp lệ.

---

# 7. Vì sao Rust không copy String tự động?

Giả sử:

```text
a ───────┐
         ▼
       "Hello"
         ▲
         │
b ───────┘
```

Nếu cả `a` và `b` cùng nghĩ rằng mình sở hữu heap memory:

```text
a ──┐
    ├──► heap
b ──┘
```

Khi:

```text
drop(a)
drop(b)
```

có nguy cơ:

```text
double free
```

Rust tránh vấn đề này bằng Move.

---

# 8. Clone

Nếu thật sự muốn hai String độc lập:

```rust
let a = String::from("Hello");
let b = a.clone();
```

Conceptually:

```text
a ─────► "Hello"

b ─────► "Hello"
```

Hai vùng heap khác nhau.

---

# 9. Move vs Clone

```text
Move
────
a ──move──► b

Không tạo dữ liệu mới.


Clone
─────
a ──clone──► b

Tạo dữ liệu mới.
```

Do đó:

```rust
let b = a;
```

rẻ hơn:

```rust
let b = a.clone();
```

nhưng hai câu có semantics hoàn toàn khác nhau.

---

# 10. Copy

Các kiểu đơn giản:

```rust
let a = 10;
let b = a;

println!("{a}");
println!("{b}");
```

hoạt động.

Tại sao?

Vì `i32` implement:

```rust
Copy
```

Rust copy giá trị trực tiếp.

---

# 11. Copy vs Clone

Đây là điểm cần phân biệt rất rõ.

```text
Copy
────
implicit
cheap
bitwise copy
stack-oriented types


Clone
─────
explicit
có thể expensive
có thể cấp phát
```

Ví dụ:

```rust
let a = 10;
let b = a;
```

là Copy.

Trong khi:

```rust
let a = String::from("Hello");
let b = a.clone();
```

là Clone.

---

# 12. Những type thường Copy

Ví dụ:

```rust
i32
u32
usize
bool
char
f32
f64
```

và tuple nếu tất cả thành phần đều Copy:

```rust
let a = (10, true);
let b = a;

println!("{a:?}");
println!("{b:?}");
```

---

# 13. Borrow

Thay vì chuyển ownership:

```rust
fn print_name(name: String) {
    println!("{name}");
}
```

Ta borrow:

```rust
fn print_name(name: &String) {
    println!("{name}");
}
```

Hoặc tốt hơn với text:

```rust
fn print_name(name: &str) {
    println!("{name}");
}
```

---

# 14. Borrowing không lấy ownership

```rust
fn main() {
    let name = String::from("Rust");

    print_name(&name);

    println!("{name}");
}

fn print_name(name: &str) {
    println!("{name}");
}
```

Sơ đồ:

```text
name: String
   │
   │ borrow
   ▼
&str
   │
   ▼
print_name()
```

Sau function:

```text
name vẫn tồn tại
```

---

# 15. Immutable Borrow

Bạn có thể có nhiều immutable references:

```rust
let text = String::from("Rust");

let a = &text;
let b = &text;
let c = &text;
```

Điều này hợp lệ.

Conceptually:

```text
        ┌── a
        │
text ───┼── b
        │
        └── c
```

Tất cả chỉ đọc.

---

# 16. Mutable Borrow

Muốn sửa:

```rust
let mut text = String::from("Rust");

let reference = &mut text;

reference.push_str(" Programming");
```

Có một rule rất quan trọng:

> Tại một thời điểm, không thể vừa có mutable borrow vừa có immutable borrow đang hoạt động.

---

# 17. Vì sao?

Nếu:

```text
a ──► data
b ──► data
```

và:

```text
a = immutable
b = mutable
```

thì:

```text
a đang đọc
b đang sửa
```

có thể tạo trạng thái không nhất quán.

Rust ngăn điều đó ngay compile time.

---

# 18. Rule Borrowing

Bạn có thể có:

```text
Nhiều &T
```

hoặc:

```text
Một &mut T
```

nhưng không đồng thời:

```text
&T + &mut T
```

trong cùng vùng lifetime sử dụng.

Mental model:

```text
Read mode
─────────
&data
&data
&data


Write mode
──────────
&mut data
```

---

# 19. Slice

Slice là một view vào một phần dữ liệu.

Ví dụ:

```rust
let text = String::from("Hello Rust");

let hello = &text[0..5];
```

`hello` là:

```rust
&str
```

Conceptually:

```text
String
┌───────────────────┐
│ Hello Rust        │
└───────────────────┘
  ▲─────▲
  │
 &str
```

---

# 20. Slice không sở hữu dữ liệu

```rust
let text = String::from("Hello Rust");

let part = &text[0..5];
```

`part` không có heap riêng.

```text
text
 │
 ▼
"Hello Rust"
 ▲
 │
part: &str
```

---

# 21. Slice array

Slice không chỉ dành cho String.

```rust
let numbers = [1, 2, 3, 4, 5];

let part = &numbers[1..4];

println!("{part:?}");
```

Output:

```text
[2, 3, 4]
```

Type:

```rust
&[i32]
```

---

# 22. String và `&str`

Đây là điểm cần nhớ:

```text
String
──────
owned text


&str
────
borrowed text slice
```

Ví dụ:

```rust
let owned = String::from("Hello");
let borrowed: &str = &owned;
```

---

# 23. API Design

Đây là nơi Ownership bắt đầu trở thành kỹ năng thực tế.

### Chỉ đọc

```rust
fn print(text: &str)
```

### Sửa

```rust
fn modify(text: &mut String)
```

### Lấy ownership

```rust
fn consume(text: String)
```

### Trả ownership

```rust
fn create() -> String
```

### Nhận borrow, trả owned

```rust
fn normalize(text: &str) -> String
```

### Nhận borrow, trả slice

```rust
fn first_word(text: &str) -> &str
```

---

# 24. Deref Coercion

Ví dụ:

```rust
fn print(text: &str) {
    println!("{text}");
}

fn main() {
    let text = String::from("Hello");

    print(&text);
}
```

Bạn truyền:

```rust
&String
```

nhưng function cần:

```rust
&str
```

Rust tự thực hiện deref coercion phù hợp.

Conceptually:

```text
&String
  ↓
String
  ↓
str
  ↓
&str
```

Bạn không cần viết thủ công trong trường hợp thông thường.

---

# 25. `as_str()`

Có thể viết rõ:

```rust
print(text.as_str());
```

Hai cách:

```rust
print(&text);
```

và:

```rust
print(text.as_str());
```

thường đều đúng.

---

# 26. Drop

Rust có trait:

```rust
Drop
```

Một type có thể định nghĩa hành vi khi bị hủy.

Ví dụ:

```rust
struct Database {
    name: String,
}

impl Drop for Database {
    fn drop(&mut self) {
        println!("Database {} dropped", self.name);
    }
}

fn main() {
    let db = Database {
        name: "app.db".to_string(),
    };

    println!("Using database");
}
```

Kết quả conceptually:

```text
Using database
Database app.db dropped
```

---

# 27. RAII

Rust sử dụng tư tưởng:

> Resource Acquisition Is Initialization.

Nói đơn giản:

```text
Object được tạo
      ↓
Resource được sở hữu
      ↓
Object ra khỏi scope
      ↓
Drop
      ↓
Resource được giải phóng
```

Điều này cực kỳ quan trọng khi làm:

```text
File
Socket
Database connection
Mutex guard
Memory
Network resource
```

---

# 28. Scope

Ví dụ:

```rust
fn main() {
    {
        let text = String::from("Hello");

        println!("{text}");
    }

    // text không còn tồn tại
}
```

Scope:

```text
main
│
├── inner scope
│   ├── text created
│   ├── use
│   └── drop
│
└── continue
```

---

# 29. Ownership và function

Khi function nhận:

```rust
fn consume(value: String)
```

ownership chuyển:

```text
main
 │
 │ move
 ▼
consume
 │
 └── drop
```

Khi function nhận:

```rust
fn read(value: &str)
```

ownership không chuyển:

```text
main
 │
 │ borrow
 ▼
function
 │
 └── return
       │
       ▼
main vẫn owner
```

---

# 30. Ownership và struct

Đây là nơi rất quan trọng khi xây application.

```rust
struct Book {
    title: String,
    author: String,
}
```

`Book` sở hữu:

```text
title
author
```

Khi:

```rust
let book = Book {
    title: String::from("Rust"),
    author: String::from("Steve"),
};
```

ta có:

```text
book
├── title ──► heap
└── author ─► heap
```

Khi `book` drop:

```text
book
 ├── title → drop
 └── author → drop
```

---

# 31. Struct borrow

Không cần transfer ownership để đọc:

```rust
fn print_book(book: &Book) {
    println!("{}", book.title);
    println!("{}", book.author);
}
```

Dùng:

```rust
print_book(&book);
```

---

# 32. Struct mutable borrow

```rust
fn rename(book: &mut Book, title: &str) {
    book.title = title.to_string();
}
```

Test:

```rust
let mut book = Book {
    title: "Rust".to_string(),
    author: "Steve".to_string(),
};

rename(&mut book, "The Rust Book");
```

---

# 33. Một pattern rất quan trọng

Trong application thực tế:

```text
Domain object
    │
    │ ownership
    ▼
String / Vec / Struct
```

Các function xử lý thường:

```text
&Entity
&mut Entity
```

thay vì liên tục:

```text
Entity
```

để tránh move không cần thiết.

---

# 34. Ownership trong Repository

Ví dụ:

```rust
struct BookRepository;

impl BookRepository {
    fn save(&self, book: &Book) {
        println!("Saving: {}", book.title);
    }
}
```

Repository không cần sở hữu Book.

Nó chỉ đọc.

Đây là design rất tự nhiên:

```text
Service
   │
   ▼
Repository
   │
   └── &Book
```

---

# 35. Ownership trong Parser

Parser:

```rust
fn parse_book(input: &str) -> Option<Book>
```

Đây là một pattern cực kỳ tốt:

```text
raw data
   │
   ▼
&str
   │
   ▼
parser
   │
   ▼
Book
   │
   ├── String
   ├── String
   └── ...
```

Parser không cần sở hữu input.

Nhưng kết quả domain object sở hữu dữ liệu.

---

# 36. Lifetime cơ bản

Lifetime là phần tiếp theo rất quan trọng.

Ví dụ:

```rust
fn first_word(text: &str) -> &str {
    text.split_whitespace().next().unwrap()
}
```

Ý nghĩa:

```text
output &str
    │
    └── borrow từ input
```

Rust đảm bảo output không sống lâu hơn input.

---

# 37. Ví dụ

```rust
fn first_word(text: &str) -> &str {
    text.split_whitespace().next().unwrap()
}

fn main() {
    let text = String::from("Rust Programming");

    let word = first_word(&text);

    println!("{word}");
}
```

Hợp lệ.

---

# 38. Lifetime không phải garbage collector

Lifetime không phải:

```text
"Rust sẽ theo dõi object runtime."
```

Thay vào đó:

> Lifetime là thông tin compiler sử dụng để kiểm tra tính hợp lệ của references.

Phần lớn lifetime được compiler suy luận.

---

# 39. Khi nào phải viết lifetime?

Ví dụ nhiều reference:

```rust
fn longer<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() > b.len() {
        a
    } else {
        b
    }
}
```

Bạn sẽ học sâu ở phần Lifetime.

Hiện tại chỉ cần hiểu:

```text
reference không thể sống lâu hơn dữ liệu mà nó trỏ tới
```

---

# 40. Ownership Deep Dive — ví dụ tổng hợp

```rust
struct Book {
    title: String,
    author: String,
}

impl Book {
    fn new(title: &str, author: &str) -> Self {
        Self {
            title: title.to_owned(),
            author: author.to_owned(),
        }
    }

    fn rename(&mut self, title: &str) {
        self.title = title.to_owned();
    }

    fn print(&self) {
        println!("Title : {}", self.title);
        println!("Author: {}", self.author);
    }
}

fn main() {
    let mut book = Book::new(
        "The Rust Programming Language",
        "Steve Klabnik",
    );

    book.print();

    book.rename("The Rust Book");

    book.print();
}
```

Đây là một design rất chuẩn.

---

# 41. Phân tích code

Constructor:

```rust
fn new(title: &str, author: &str) -> Self
```

Input:

```text
borrowed
```

Output:

```text
owned
```

---

`rename()`:

```rust
fn rename(&mut self, title: &str)
```

Có hai loại borrow:

```text
self
 ↓
&mut self

title
 ↓
&str
```

Nó có thể:

```text
mutate Book
read title
```

---

`print()`:

```rust
fn print(&self)
```

Chỉ đọc.

---

# 42. Mini Project

Bây giờ xây một chương trình nhỏ:

```text
Book Library
```

Có:

```text
Book
Chapter
Library
```

---

# 43. Thiết kế

```text
Library
│
└── Vec<Book>

Book
├── title: String
├── author: String
└── chapters: Vec<Chapter>

Chapter
├── number: u32
└── title: String
```

---

# 44. Code hoàn chỉnh

Tạo project:

```bash
cargo new ownership_library
cd ownership_library
```

Thay `src/main.rs` bằng:

```rust
#[derive(Debug)]
struct Chapter {
    number: u32,
    title: String,
}

#[derive(Debug)]
struct Book {
    title: String,
    author: String,
    chapters: Vec<Chapter>,
}

impl Chapter {
    fn new(number: u32, title: &str) -> Self {
        Self {
            number,
            title: title.to_owned(),
        }
    }
}

impl Book {
    fn new(title: &str, author: &str) -> Self {
        Self {
            title: title.to_owned(),
            author: author.to_owned(),
            chapters: Vec::new(),
        }
    }

    fn add_chapter(&mut self, chapter: Chapter) {
        self.chapters.push(chapter);
    }

    fn chapter_count(&self) -> usize {
        self.chapters.len()
    }

    fn print(&self) {
        println!("========================");
        println!("Title : {}", self.title);
        println!("Author: {}", self.author);
        println!("Chapters: {}", self.chapter_count());

        for chapter in &self.chapters {
            println!(
                "  {}. {}",
                chapter.number,
                chapter.title
            );
        }
    }
}

struct Library {
    books: Vec<Book>,
}

impl Library {
    fn new() -> Self {
        Self {
            books: Vec::new(),
        }
    }

    fn add_book(&mut self, book: Book) {
        self.books.push(book);
    }

    fn print(&self) {
        println!("========== LIBRARY ==========");

        for book in &self.books {
            book.print();
        }
    }
}

fn main() {
    let mut book = Book::new(
        "The Rust Programming Language",
        "Steve Klabnik",
    );

    book.add_chapter(
        Chapter::new(1, "Getting Started")
    );

    book.add_chapter(
        Chapter::new(2, "Programming a Guessing Game")
    );

    book.add_chapter(
        Chapter::new(3, "Common Programming Concepts")
    );

    let mut library = Library::new();

    library.add_book(book);

    library.print();
}
```

Chạy:

```bash
cargo run
```

---

# 45. Ownership đang xuất hiện ở đâu?

### `Book::new`

```rust
fn new(title: &str, author: &str) -> Self
```

Borrow input.

Sau đó:

```rust
title: title.to_owned()
```

tạo ownership.

---

### `add_chapter`

```rust
fn add_chapter(&mut self, chapter: Chapter)
```

Function **nhận ownership** của `chapter`.

```text
caller
   │
   │ move
   ▼
add_chapter
   │
   ▼
Vec<Chapter>
```

---

# 46. Vì sao `chapter` phải move?

Khi:

```rust
self.chapters.push(chapter);
```

`Vec` cần sở hữu Chapter.

Do đó:

```text
Chapter
   │
   │ ownership
   ▼
Vec<Chapter>
```

Nếu chỉ borrow:

```rust
fn add_chapter(&mut self, chapter: &Chapter)
```

thì Vec không thể lưu reference một cách đơn giản nếu lifetime không phù hợp.

Domain model thường nên sở hữu dữ liệu.

---

# 47. `Library::add_book`

```rust
fn add_book(&mut self, book: Book) {
    self.books.push(book);
}
```

Tương tự:

```text
Book
 │
 │ move
 ▼
Vec<Book>
```

Sau:

```rust
library.add_book(book);
```

`book` không còn được dùng trực tiếp nữa.

---

# 48. Nhưng `print()` không move

```rust
for book in &self.books {
    book.print();
}
```

Ở đây:

```text
Vec<Book>
   │
   ├── &Book
   ├── &Book
   └── &Book
```

Không chuyển ownership.

---

# 49. Đây chính là Rust

Nếu bạn nhìn code:

```rust
fn add_book(&mut self, book: Book)
```

bạn phải lập tức hiểu:

```text
self
└── mutable borrow

book
└── ownership transfer
```

Nếu:

```rust
fn print(&self)
```

thì:

```text
self
└── immutable borrow
```

Đây là tư duy bạn cần đạt tới.

---

# 50. Bài tập nâng cấp mini project

Hãy tự thêm:

### 1. Tìm book

```rust
fn find_book(&self, title: &str) -> Option<&Book>
```

### 2. Tìm book mutable

```rust
fn find_book_mut(&mut self, title: &str) -> Option<&mut Book>
```

### 3. Tìm chapter

```rust
fn find_chapter(&self, number: u32) -> Option<&Chapter>
```

### 4. Xóa book

```rust
fn remove_book(&mut self, title: &str) -> Option<Book>
```

Đây là bài tập cực tốt về:

```text
&self
&mut self
Option<&T>
Option<&mut T>
Option<T>
ownership
```

---

# 51. Bài tập đặc biệt — phân tích ownership

Cho:

```rust
fn main() {
    let a = String::from("Rust");

    let b = &a;
    let c = &a;

    println!("{a}");
    println!("{b}");
    println!("{c}");
}
```

Hãy vẽ:

```text
a
│
├── b
└── c
```

và giải thích tại sao hợp lệ.

---

# 52. Bài tập mutable borrow

Phân tích:

```rust
fn main() {
    let mut text = String::from("Rust");

    let a = &mut text;

    a.push_str(" Programming");

    println!("{a}");
}
```

Tại sao hợp lệ?

---

# 53. Bài tập borrow conflict

Đoạn này:

```rust
let mut text = String::from("Rust");

let a = &text;
let b = &mut text;

println!("{a}");
println!("{b}");
```

Có thể gặp lỗi.

Hãy giải thích:

```text
a = immutable borrow
b = mutable borrow
```

và cách sửa.

---

# 54. Bài tập Move

```rust
let a = String::from("Rust");
let b = a;

println!("{a}");
```

Hãy giải thích:

```text
a
 ↓
move
 ↓
b
```

và sửa code để cả hai biến đều có thể sử dụng.

Có hai cách:

```rust
clone
```

hoặc thiết kế lại bằng borrow tùy mục đích.

---

# 55. Bài tập API Design

Cho:

```rust
struct User {
    name: String,
}
```

Hãy thiết kế:

```text
create_user
rename_user
print_user
consume_user
```

với type phù hợp.

Một thiết kế tốt:

```rust
fn create_user(name: &str) -> User

fn rename_user(user: &mut User, name: &str)

fn print_user(user: &User)

fn consume_user(user: User)
```

---

# 56. Ownership Cheat Sheet

```text
                 OWNERSHIP
                     │
       ┌─────────────┴─────────────┐
       │                           │
    Owner                      Borrower
       │                           │
    String                         │
    Vec<T>                         │
    Struct                         │
    Box<T>                         │
       │                           │
       │                  ┌────────┴────────┐
       │                  │                 │
       │                 &T              &mut T
       │                  │                 │
       │               read              modify
       │
       └──── move / drop
```

---

# 57. Quy tắc vàng của Ownership

Khi viết Rust, hãy tự hỏi 5 câu:

### 1. Ai sở hữu dữ liệu?

```text
String?
Struct?
Vec?
```

### 2. Function có cần lấy ownership không?

Nếu không:

```rust
&T
```

### 3. Function có cần sửa dữ liệu không?

Nếu có:

```rust
&mut T
```

### 4. Function có tạo dữ liệu mới không?

Nếu có thể trả:

```rust
T
```

### 5. Reference có sống lâu hơn dữ liệu không?

Nếu có vấn đề:

```text
lifetime / dangling reference
```

---

# 58. Mental model cuối cùng

Bạn nên nhìn Rust như thế này:

```text
                 VALUE
                   │
          ┌────────┴────────┐
          │                 │
       OWNER              BORROW
          │                 │
       String              &T
       Vec<T>              &str
       Book                &[T]
          │                 │
       Move               Read
       Drop               View
          │
          ▼
       &mut T
          │
       Modify
```

Và toàn bộ Ownership có thể cô đọng thành:

```text
OWNERSHIP
    ↓
MOVE
    ↓
BORROW
    ↓
& / &mut
    ↓
SLICE
    ↓
String / &str
    ↓
LIFETIME
    ↓
SAFE MEMORY
```

---

# 59. Bạn đã hoàn thành Phần III

Sau 10 buổi:

```text
21. Ownership              ✓
22. Move                   ✓
23. Clone                  ✓
24. Copy                   ✓
25. Borrow                 ✓
26. Mutable Borrow         ✓
27. Slice                  ✓
28. String                 ✓
29. String vs &str         ✓
30. Ownership Deep Dive    ✓
```

Từ đây bạn đã có nền tảng quan trọng nhất để hiểu Rust.

## Phần IV tiếp theo — Struct & Method

Một roadmap hợp lý tiếp theo sẽ là:

```text
Phần IV — Struct & Method

Buổi 31. Struct
Buổi 32. Tuple Struct
Buổi 33. Unit Struct
Buổi 34. impl
Buổi 35. Method
Buổi 36. Associated Function
Buổi 37. Self / &self / &mut self
Buổi 38. Constructor Pattern
Buổi 39. Encapsulation
Buổi 40. Mini Project
```

**Buổi 31 sẽ đi sâu vào `struct`: field, ownership trong struct, struct update syntax, destructuring, nested struct và thiết kế model thực tế**, sau đó xây tiếp trên mini project `Book/Chapter/Library` vừa hoàn thành.
