# Rust — Phần III: Ownership

# Buổi 25 — Borrow

Đây là một trong những buổi **quan trọng nhất của Rust**.

Từ trước đến giờ chúng ta đã học:

```text
Ownership
├── Move
├── Clone
└── Copy
```

Hôm nay thêm:

```text
Borrow
```

Mục tiêu của Borrow là:

> **Cho phép sử dụng một value mà không lấy ownership của value đó.**

Nói ngắn gọn:

```text
Move   → lấy quyền sở hữu
Borrow → mượn quyền sử dụng
```

---

# 1. Vấn đề mà Borrow giải quyết

Xét function:

```rust
fn print_text(text: String) {
    println!("{text}");
}

fn main() {
    let text = String::from("Hello Rust");

    print_text(text);

    println!("{text}");
}
```

Code này lỗi.

Tại sao?

Vì:

```text
text
 │
 │ Move
 ▼
print_text()
```

Sau khi gọi:

```rust
print_text(text);
```

`text` không còn ownership.

Nhưng chúng ta chỉ muốn:

> "Cho function xem nội dung của String."

Chúng ta **không muốn chuyển ownership**.

Đó chính là lúc Borrow xuất hiện.

---

# 2. Borrow bằng `&`

Thay vì:

```rust
fn print_text(text: String)
```

ta viết:

```rust
fn print_text(text: &String)
```

Toàn bộ chương trình:

```rust
fn print_text(text: &String) {
    println!("{text}");
}

fn main() {
    let text = String::from("Hello Rust");

    print_text(&text);

    println!("{text}");
}
```

Compile được.

---

# 3. Ý nghĩa của `&`

Ký hiệu:

```rust
&value
```

có nghĩa:

> Tạo một reference đến `value`.

Ví dụ:

```rust
let text = String::from("Rust");

let reference = &text;
```

Ta có:

```text
text
 │
 ▼
String("Rust")

reference
    │
    └──────────► text
```

`reference` **không sở hữu** `String`.

---

# 4. Ownership không thay đổi

Đây là điểm quan trọng nhất.

```rust
let text = String::from("Rust");

let reference = &text;
```

Ai sở hữu String?

```text
text → OWNER
```

Còn:

```text
reference → BORROWER
```

Do đó:

```rust
println!("{text}");
println!("{reference}");
```

đều hợp lệ.

---

# 5. Borrow không tạo ownership mới

Khi:

```rust
let b = &a;
```

không có:

```text
a ownership → b
```

mà là:

```text
a ───────────────► data

b ───────────────► a/data
    borrow
```

`a` vẫn là owner.

---

# 6. So sánh Move và Borrow

### Move

```rust
let a = String::from("Rust");
let b = a;
```

```text
a ──X
     \
      → b → String
```

`a` mất ownership.

---

### Borrow

```rust
let a = String::from("Rust");
let b = &a;
```

```text
a ───────────────► String
                    ▲
                    │
                    b
```

`a` vẫn owner.

---

# 7. Function với Borrow

Ví dụ:

```rust
fn print_name(name: &String) {
    println!("Name: {name}");
}

fn main() {
    let name = String::from("Alice");

    print_name(&name);

    println!("After: {name}");
}
```

Flow:

```text
main
 │
 │ owns String
 ▼
name
 │
 │ borrow
 ▼
print_name(&name)
 │
 │ use
 ▼
return
 │
 ▼
name vẫn valid
```

---

# 8. Borrow nhiều lần

Đây là sức mạnh rất lớn.

```rust
fn print_text(text: &String) {
    println!("{text}");
}

fn main() {
    let text = String::from("Rust");

    print_text(&text);
    print_text(&text);
    print_text(&text);

    println!("{text}");
}
```

Tất cả đều hợp lệ.

Bởi vì mỗi lần:

```text
&text
```

chỉ là một borrow.

Ownership vẫn nằm ở:

```text
text
```

---

# 9. Có thể có nhiều immutable borrow

```rust
fn main() {
    let text = String::from("Rust");

    let a = &text;
    let b = &text;
    let c = &text;

    println!("{a}");
    println!("{b}");
    println!("{c}");
}
```

Hoàn toàn hợp lệ.

Conceptually:

```text
             ┌── a
             │
text ────────┼── b
             │
             └── c
```

Tất cả chỉ đọc.

---

# 10. Quy tắc đầu tiên của Borrowing

Rust cho phép:

> **Có nhiều immutable references cùng lúc.**

Ví dụ:

```rust
let r1 = &value;
let r2 = &value;
let r3 = &value;
```

Hợp lệ.

---

# 11. Tại sao nhiều immutable borrow an toàn?

Vì:

```text
&value
```

chỉ đọc.

Ví dụ:

```text
             ┌── read
             │
value ───────┼── read
             │
             └── read
```

Không ai thay đổi value.

Do đó không xảy ra race/conflict kiểu:

```text
người A đang đọc
người B thay đổi
```

---

# 12. Borrow không copy dữ liệu

Đây là một hiểu nhầm phổ biến.

```rust
let text = String::from("Hello");

let a = &text;
let b = &text;
```

Không phải:

```text
text → "Hello"
a    → copy "Hello"
b    → copy "Hello"
```

Mà:

```text
             ┌── a
             │
text → "Hello"
             │
             └── b
```

Chỉ có một String.

---

# 13. Borrowing `i32`

Borrow không chỉ dành cho `String`.

```rust
fn print_number(number: &i32) {
    println!("{number}");
}

fn main() {
    let number = 100;

    print_number(&number);

    println!("{number}");
}
```

---

# 14. Nhưng `i32` đã là Copy

Đúng.

Bạn có thể viết:

```rust
fn print_number(number: i32) {
    println!("{number}");
}
```

vẫn không mất ownership.

Nhưng mục tiêu của Borrow không chỉ là tránh Move.

Borrow đặc biệt quan trọng với các type:

```text
String
Vec<T>
HashMap<K, V>
struct lớn
resource-owning types
```

---

# 15. Borrow giúp tránh `clone()`

Ví dụ không tốt:

```rust
fn print_text(text: String) {
    println!("{text}");
}

fn main() {
    let text = String::from("Rust");

    print_text(text.clone());
    print_text(text.clone());
    print_text(text.clone());
}
```

Ta đang tạo nhiều bản sao không cần thiết.

Thay vào đó:

```rust
fn print_text(text: &String) {
    println!("{text}");
}

fn main() {
    let text = String::from("Rust");

    print_text(&text);
    print_text(&text);
    print_text(&text);
}
```

Không cần clone.

---

# 16. Đây là tư duy Rust rất quan trọng

Khi bạn thấy:

```rust
text.clone()
```

hãy tự hỏi:

> "Function thực sự cần ownership hay chỉ cần đọc dữ liệu?"

Nếu chỉ cần đọc:

```rust
&text
```

thường là lựa chọn tốt hơn.

---

# 17. Borrow một struct

```rust
struct User {
    name: String,
    age: u32,
}

fn print_user(user: &User) {
    println!("name = {}", user.name);
    println!("age = {}", user.age);
}

fn main() {
    let user = User {
        name: String::from("Alice"),
        age: 25,
    };

    print_user(&user);

    println!("User: {}", user.name);
}
```

`print_user()` không sở hữu `User`.

---

# 18. Borrow từng field

Bạn có thể borrow field:

```rust
let user = User {
    name: String::from("Alice"),
    age: 25,
};

let name = &user.name;
```

Sau đó:

```rust
println!("{name}");
```

`user` vẫn sở hữu toàn bộ struct.

---

# 19. Borrow và field access

Ví dụ:

```rust
struct User {
    name: String,
    age: u32,
}

fn main() {
    let user = User {
        name: String::from("Alice"),
        age: 20,
    };

    let name = &user.name;

    println!("name = {name}");
    println!("age = {}", user.age);
}
```

Hợp lệ.

---

# 20. Borrow một phần của struct

Rust cho phép:

```text
User
├── name
└── age
```

Bạn có thể:

```rust
let name = &user.name;
```

mà không cần borrow toàn bộ object theo cách bạn có thể tưởng tượng.

Đây là nền tảng quan trọng cho việc Rust quản lý aliasing rất chặt chẽ.

---

# 21. Dereference

Nếu:

```rust
let x = 10;
let r = &x;
```

thì:

```rust
r
```

là reference.

Muốn truy cập value phía sau reference, có thể dùng:

```rust
*r
```

Ví dụ:

```rust
fn main() {
    let x = 10;
    let r = &x;

    println!("x = {x}");
    println!("r = {r}");
    println!("*r = {}", *r);
}
```

---

# 22. `&` và `*`

Hai ký hiệu này thường đi cùng nhau:

```text
& → tạo reference
* → dereference
```

Ví dụ:

```rust
let x = 10;

let r = &x;
```

```text
x = 10

r ─────► x
```

Dereference:

```rust
*r
```

có nghĩa:

```text
r ─────► x
         │
         ▼
        10
```

---

# 23. Ví dụ rõ hơn

```rust
fn main() {
    let x = 42;

    let r = &x;

    println!("r  = {r}");
    println!("*r = {}", *r);
}
```

Kết quả:

```text
r  = 42
*r = 42
```

Rust có cơ chế tự dereference trong rất nhiều trường hợp, nên bạn sẽ thường thấy:

```rust
println!("{r}");
```

thay vì:

```rust
println!("{}", *r);
```

---

# 24. Borrow trong function

```rust
fn square(value: &i32) -> i32 {
    *value * *value
}

fn main() {
    let x = 5;

    let result = square(&x);

    println!("x = {x}");
    println!("result = {result}");
}
```

Function nhận:

```rust
&i32
```

không phải:

```rust
i32
```

---

# 25. Với `String`

```rust
fn length(text: &String) -> usize {
    text.len()
}

fn main() {
    let text = String::from("Rust");

    let size = length(&text);

    println!("text = {text}");
    println!("size = {size}");
}
```

Ownership vẫn ở `main`.

---

# 26. Nhưng `&String` thường chưa phải API tốt nhất

Đây là một điểm quan trọng.

Bạn có thể viết:

```rust
fn print_text(text: &String) {
    println!("{text}");
}
```

Nhưng idiomatic Rust thường ưu tiên:

```rust
fn print_text(text: &str) {
    println!("{text}");
}
```

Tại sao?

Chúng ta sẽ học sâu ở:

> **Buổi 29 — `String` vs `&str`**

Hiện tại chỉ cần nhớ:

```text
&String
```

là borrow một `String`.

```text
&str
```

là string slice/reference đến string data.

---

# 27. Borrow và return

Đây là phần bắt đầu quan trọng.

Bạn có thể return một reference:

```rust
fn first_character(text: &String) -> &str {
    &text[0..1]
}
```

Nhưng Rust cần đảm bảo reference trả về không sống lâu hơn data.

Ví dụ:

```rust
fn get_text() -> &String {
    let text = String::from("Rust");

    &text
}
```

Không compile.

Tại sao?

`text` bị destroy khi function kết thúc.

Nhưng reference vẫn muốn tồn tại.

Rust chặn lỗi này.

Phần này sẽ dẫn chúng ta tới **Lifetime** ở các buổi advanced sau.

---

# 28. Borrowing không kéo dài ownership

Ví dụ:

```rust
fn print_text(text: &String) {
    println!("{text}");
}
```

Khi function kết thúc:

```text
print_text
    │
    ▼
borrow kết thúc
```

Nhưng:

```text
String
```

vẫn thuộc về caller.

---

# 29. Borrow scope

Ví dụ:

```rust
fn main() {
    let text = String::from("Rust");

    {
        let r = &text;

        println!("{r}");
    }

    println!("{text}");
}
```

Scope của `r`:

```text
{
    let r = &text;

    println!("{r}");
}
```

Sau `}`:

```text
r → hết scope
```

`text` vẫn tồn tại.

---

# 30. Nhiều borrow

```rust
fn main() {
    let text = String::from("Rust");

    let r1 = &text;
    let r2 = &text;

    println!("{r1}");
    println!("{r2}");
}
```

Hợp lệ.

Conceptually:

```text
       r1
        │
        ▼
text ──────── String
        ▲
        │
       r2
```

---

# 31. Immutable borrow

Ký hiệu:

```rust
&T
```

Ví dụ:

```rust
let r = &x;
```

Ý nghĩa:

> Tôi mượn `x` để đọc.

Bạn không thể dùng immutable reference để thay đổi value.

Ví dụ:

```rust
fn main() {
    let x = 10;

    let r = &x;

    // *r = 20;
}
```

Nếu bỏ comment:

```rust
*r = 20;
```

sẽ lỗi.

---

# 32. Tại sao?

Vì:

```rust
let x = 10;
let r = &x;
```

`r` là:

```text
immutable borrow
```

Nó chỉ có quyền đọc.

```text
r
│
├── READ ✓
└── WRITE ✗
```

---

# 33. Ownership Rules

Đến đây bạn cần bắt đầu ghi nhớ ba quy tắc:

### Rule 1

Mỗi value có một owner.

### Rule 2

Có thể có nhiều immutable references:

```text
&T
&T
&T
```

### Rule 3

Không được đồng thời có mutable reference với immutable references trong cùng vùng sử dụng.

Rule 3 chúng ta sẽ học sâu ở **Buổi 26 — Mutable Borrow**.

---

# 34. Ví dụ với function

Đây là pattern cực kỳ quan trọng:

```rust
fn calculate_length(text: &String) -> usize {
    text.len()
}

fn main() {
    let text = String::from("Hello Rust");

    let length = calculate_length(&text);

    println!("'{text}' has {length} characters.");
}
```

Đây là kiểu code bạn sẽ gặp liên tục trong Rust.

---

# 35. So sánh 3 cách

### Cách 1 — Move

```rust
fn process(text: String)
```

Caller:

```rust
process(text);
```

Ownership:

```text
caller → function
```

---

### Cách 2 — Borrow

```rust
fn process(text: &String)
```

Caller:

```rust
process(&text);
```

Ownership:

```text
caller → vẫn giữ
```

---

### Cách 3 — Clone

```rust
process(text.clone());
```

Ownership:

```text
caller → bản gốc
function → bản copy
```

---

# 36. Khi nào dùng cái nào?

Một quy tắc thực tế:

```text
Function cần sở hữu data?
        │
       YES
        │
        ▼
      String
```

Nếu:

```text
Function chỉ đọc data?
        │
       YES
        │
        ▼
      &T / &str
```

Nếu:

```text
Function cần một bản độc lập?
        │
       YES
        │
        ▼
      clone()
```

---

# 37. Ví dụ thực tế

Giả sử ứng dụng đọc truyện.

Ta có:

```rust
struct Chapter {
    title: String,
    content: String,
}
```

Function hiển thị chapter:

```rust
fn display_chapter(chapter: &Chapter) {
    println!("Title: {}", chapter.title);
    println!("{}", chapter.content);
}
```

Không cần:

```rust
fn display_chapter(chapter: Chapter)
```

vì display không cần ownership.

---

# 38. Tại sao Borrow cực kỳ quan trọng trong ứng dụng lớn?

Nếu không có Borrow, bạn sẽ phải clone rất nhiều:

```text
Database
   │
   ▼
Repository
   │
   ▼
Service
   │
   ▼
Parser
   │
   ▼
UI
```

Nếu mỗi tầng đều clone:

```text
data
 ↓ clone
 ↓ clone
 ↓ clone
 ↓ clone
```

thì:

```text
memory ↑
CPU ↑
allocation ↑
```

Borrow giúp truyền reference:

```text
data
 │
 ├── &data → service
 │
 ├── &data → parser
 │
 └── &data → UI
```

Không cần sao chép toàn bộ data.

---

# 39. Ví dụ Repository

Một pattern rất quan trọng cho project lớn:

```rust
struct User {
    id: u64,
    name: String,
}

struct UserRepository {
    users: Vec<User>,
}
```

Function:

```rust
impl UserRepository {
    fn print_users(&self) {
        for user in &self.users {
            println!("{}: {}", user.id, user.name);
        }
    }
}
```

Ở đây:

```rust
&self
```

là borrow repository.

Chúng ta sẽ học `&self` rất sâu khi tới OOP/struct/impl.

---

# 40. Borrow trong vòng lặp

```rust
fn main() {
    let names = vec![
        String::from("Alice"),
        String::from("Bob"),
        String::from("Charlie"),
    ];

    for name in &names {
        println!("{name}");
    }

    println!("{names:?}");
}
```

Chú ý:

```rust
for name in &names
```

chứ không:

```rust
for name in names
```

Vì:

```text
&names
```

borrow vector thay vì lấy ownership.

---

# 41. Đây là pattern rất quan trọng

Khi làm việc với collection:

```rust
for item in &collection
```

thường có nghĩa:

> Duyệt collection bằng immutable borrow.

Ví dụ:

```rust
for item in &numbers {
    println!("{item}");
}
```

Collection vẫn tồn tại sau loop.

---

# 42. Borrow và indexing

```rust
fn main() {
    let numbers = vec![10, 20, 30];

    let first = &numbers[0];

    println!("first = {first}");
    println!("numbers = {numbers:?}");
}
```

`first` chỉ borrow element đầu tiên.

---

# 43. Borrow và method

```rust
let text = String::from("Rust");

let length = text.len();
```

Bạn có thể nghĩ conceptually:

```text
text.len()
   ↓
borrow text
```

Các method như:

```rust
len()
is_empty()
contains()
```

thường chỉ cần borrow object.

Rust cho phép syntax rất tự nhiên.

---

# 44. Một ví dụ hoàn chỉnh

Tạo project:

```bash
cargo new borrow_demo
cd borrow_demo
```

`src/main.rs`:

```rust
struct Book {
    title: String,
    author: String,
}

fn print_book(book: &Book) {
    println!("Title : {}", book.title);
    println!("Author: {}", book.author);
}

fn title_length(book: &Book) -> usize {
    book.title.len()
}

fn main() {
    let book = Book {
        title: String::from("The Rust Book"),
        author: String::from("Rust Community"),
    };

    print_book(&book);

    let length = title_length(&book);

    println!("Title length: {length}");
    println!("Book still exists: {}", book.title);
}
```

Chạy:

```bash
cargo run
```

Kết quả tương tự:

```text
Title : The Rust Book
Author: Rust Community
Title length: 13
Book still exists: The Rust Book
```

Điểm quan trọng:

```text
book
 │
 ├── borrow → print_book
 │
 └── borrow → title_length
```

`book` không bị Move.

---

# 45. Bài thực hành 1 — sửa Move thành Borrow

Code lỗi:

```rust
fn print_user(user: User) {
    println!("{}", user.name);
}

fn main() {
    let user = User {
        name: String::from("Alice"),
    };

    print_user(user);

    println!("{}", user.name);
}
```

Hãy sửa thành Borrow.

Đáp án:

```rust
struct User {
    name: String,
}

fn print_user(user: &User) {
    println!("{}", user.name);
}

fn main() {
    let user = User {
        name: String::from("Alice"),
    };

    print_user(&user);

    println!("{}", user.name);
}
```

---

# 46. Bài thực hành 2 — nhiều borrow

Hãy chạy:

```rust
fn main() {
    let text = String::from("Rust");

    let a = &text;
    let b = &text;
    let c = &text;

    println!("{a}");
    println!("{b}");
    println!("{c}");
}
```

Sau đó tự giải thích:

```text
Ai là owner?
Ai là borrower?
Có bao nhiêu String?
Có bao nhiêu reference?
```

Đáp án:

```text
Owner:
text

Borrowers:
a
b
c

String:
1

References:
3
```

---

# 47. Bài thực hành 3 — Borrow collection

Viết function:

```rust
fn print_numbers(numbers: &Vec<i32>)
```

Sau đó:

```rust
fn main() {
    let numbers = vec![10, 20, 30, 40];

    print_numbers(&numbers);

    println!("{numbers:?}");
}
```

Sau này chúng ta sẽ cải thiện:

```rust
&Vec<i32>
```

thành:

```rust
&[i32]
```

Đó chính là Slice.

---

# 48. Bài thực hành 4 — Borrow trong nhiều function

Viết:

```rust
struct Story {
    title: String,
    author: String,
    chapters: u32,
}
```

Tạo:

```rust
fn print_story(story: &Story)
```

```rust
fn print_title(story: &Story)
```

```rust
fn chapter_count(story: &Story) -> u32
```

Sau đó:

```rust
fn main() {
    let story = Story {
        title: String::from("Rust Adventures"),
        author: String::from("Alice"),
        chapters: 100,
    };

    print_story(&story);
    print_title(&story);

    let count = chapter_count(&story);

    println!("chapters = {count}");
    println!("story = {}", story.title);
}
```

Mục tiêu là:

> Không sử dụng `clone()` ở bất kỳ đâu.

---

# 49. Thử thách quan trọng

Hãy viết một function:

```rust
fn longest_title(a: &str, b: &str) -> &str
```

Function trả về title dài hơn.

Ví dụ:

```rust
fn main() {
    let a = String::from("Rust");
    let b = String::from("The Rust Programming Language");

    let result = longest_title(&a, &b);

    println!("Longest: {result}");
}
```

Đây là bài tập cực kỳ tốt vì nó kết hợp:

```text
Borrow
+
Reference
+
&str
+
Return reference
```

và sẽ mở đường cho việc học **Lifetime** sau này.

---

# 50. Mental Model cần nhớ

Đừng nghĩ:

```text
&String = String khác
```

Hãy nghĩ:

```text
String
  │
  ├── owner
  │
  └── &String
          │
          └── borrower
```

Owner:

```text
quản lý lifetime/resource
```

Borrower:

```text
chỉ mượn quyền truy cập
```

---

# 51. Ownership model sau Buổi 25

Bạn đã có:

```text
                 VALUE
                   │
          ┌────────┼────────┐
          │        │        │
        Move     Copy     Borrow
          │        │        │
      ownership  implicit   &
      chuyển      copy      reference
```

Và:

```text
Borrow
  │
  └── Immutable Borrow
          │
          └── &T
```

Buổi tiếp theo:

```text
Mutable Borrow
     │
     └── &mut T
```

---

# 52. Ba quy tắc vàng

Từ hôm nay hãy thuộc lòng:

### 1.

```rust
&T
```

= immutable borrow.

### 2.

```rust
&value
```

= tạo reference tới value.

### 3.

Borrow **không chuyển ownership**.

Ví dụ:

```rust
let text = String::from("Rust");

let reference = &text;
```

Sau đó:

```rust
println!("{text}");
```

vẫn hợp lệ.

---

# 53. Câu hỏi kiểm tra

Bạn nên tự trả lời được mà chưa chạy code:

### Câu 1

```rust
let s = String::from("Rust");
let r = &s;
println!("{s}");
```

Có compile không?

**Có.**

---

### Câu 2

```rust
let s = String::from("Rust");
let r1 = &s;
let r2 = &s;
```

Có bao nhiêu owner?

**Một: `s`.**

---

### Câu 3

```rust
fn print(s: &String) {}
```

Function có ownership của `String` không?

**Không.**

---

### Câu 4

```rust
let r = &s;
```

`r` có phải một `String` mới không?

**Không.**

---

### Câu 5

```rust
let x = &s;
```

`&` nghĩa là gì?

**Tạo một reference/borrow tới `s`.**

---

# 54. Một câu cực kỳ quan trọng

Trong Rust:

> **Nếu function chỉ cần đọc dữ liệu, hãy nghĩ đến Borrow trước khi nghĩ đến Clone.**

Thay vì:

```rust
process(data.clone());
```

hãy hỏi:

```text
process(&data)
```

có đủ không?

Nếu đủ, Borrow thường là lựa chọn tốt hơn.

---

## Roadmap

```text
✓ 21 Ownership
✓ 22 Move
✓ 23 Clone
✓ 24 Copy
✓ 25 Borrow              ← hôm nay
→ 26 Mutable Borrow
  27 Slice
  28 String
  29 String vs &str
  30 Ownership Deep Dive
```

**Buổi 26 — Mutable Borrow** sẽ là phần cực kỳ quan trọng: `&mut T`, `&mut` ownership model, thay đổi dữ liệu thông qua reference, quy tắc **“hoặc một mutable reference, hoặc nhiều immutable references”**, reborrow, mutable function parameters và các lỗi Borrow Checker kinh điển.
