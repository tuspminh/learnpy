# Rust — Phần III: Ownership

# Buổi 23 — Clone

Hôm nay chúng ta học **`Clone`** — cơ chế tạo ra **một bản sao độc lập** của value.

Đây là bài rất quan trọng vì sau khi hiểu `Move`, người mới học Rust thường gặp lỗi:

```text
borrow of moved value
```

và phản xạ ngay:

```rust
value.clone()
```

Nhưng **Clone không phải thuốc chữa mọi lỗi Ownership**.

Mục tiêu hôm nay là hiểu chính xác:

```text
Move
Copy
Clone
Borrow
```

khác nhau như thế nào và **khi nào nên dùng `clone()`**.

---

# 1. Clone là gì?

`Clone` là một trait trong Rust:

```rust
trait Clone {
    fn clone(&self) -> Self;
}
```

Ý tưởng:

```text
value
  │
  │ clone()
  ├──────────────┐
  ▼              ▼
original       copy
```

Sau khi clone:

```text
original
   ↓
value A

clone
   ↓
value B
```

Hai value độc lập về ownership.

---

# 2. Ví dụ đơn giản nhất

```rust
fn main() {
    let s1 = String::from("Rust");

    let s2 = s1.clone();

    println!("s1 = {s1}");
    println!("s2 = {s2}");
}
```

Output:

```text
s1 = Rust
s2 = Rust
```

Khác với:

```rust
let s2 = s1;
```

---

# 3. So sánh Move và Clone

## Move

```rust
let s2 = s1;
```

Flow:

```text
s1
 │
 │ move
 ▼
s2
```

Sau đó:

```text
s1 → invalid
s2 → owner
```

---

## Clone

```rust
let s2 = s1.clone();
```

Flow:

```text
        ┌── s1
        │
value ──┤
        │
        └── s2
```

Sau đó:

```text
s1 → valid
s2 → valid
```

---

# 4. Clone với String

Đây là ví dụ quan trọng nhất.

```rust
fn main() {
    let original = String::from("hello");

    let copy = original.clone();

    println!("original: {original}");
    println!("copy: {copy}");
}
```

Có thể hình dung:

```text
STACK                         HEAP

original ───────────────────> "hello"

copy     ───────────────────> "hello"
```

Có **hai allocation độc lập**.

---

# 5. Clone không phải chỉ copy pointer

Đây là điểm cực kỳ quan trọng.

`String` có thể hình dung:

```text
String
┌───────────────┐
│ ptr           │──────┐
│ len           │      │
│ capacity      │      ▼
└───────────────┘   HEAP
                    "hello"
```

Khi:

```rust
let copy = original.clone();
```

Rust tạo allocation mới:

```text
original ────────> HEAP A
                    "hello"

copy ────────────> HEAP B
                    "hello"
```

Không phải:

```text
original ──┐
           ├──────> SAME HEAP
copy ──────┘
```

---

# 6. Tại sao phải tạo dữ liệu mới?

Nếu hai `String` cùng sở hữu một heap allocation:

```text
original ──┐
           ├──> heap
copy ──────┘
```

khi một bên drop:

```text
original
 ↓
free(heap)
```

bên kia sẽ trỏ vào memory đã giải phóng.

Rust không cho phép ownership kiểu đó.

`Clone` tạo một value **có ownership riêng**.

---

# 7. Clone có thể tốn tài nguyên

Ví dụ:

```rust
let huge_text = String::from("...");
let copy = huge_text.clone();
```

Nếu `huge_text` có:

```text
100 MB
```

thì clone có thể tạo thêm:

```text
100 MB
```

allocation.

Do đó:

```text
clone()
```

không miễn phí.

---

# 8. Đây là lý do không nên lạm dụng Clone

Một pattern người mới hay viết:

```rust
fn process(story: Story) {
    // ...
}
```

Có:

```rust
let story = get_story();

process(story.clone());
```

Chỉ vì muốn giữ `story`.

Nhưng nếu `process()` thực sự chỉ cần đọc:

```rust
fn process(story: &Story) {
    // ...
}
```

thì clone là không cần thiết.

Đây là lý do chúng ta học:

```text
Buổi 25 — Borrow
```

---

# 9. Clone không phải Borrow

So sánh:

```rust
let copy = story.clone();
```

với:

```rust
inspect(&story);
```

### Clone

```text
story
 │
 ├── original
 │
 └── independent copy
```

### Borrow

```text
story
 │
 └── reference
```

Borrow không tạo bản sao dữ liệu.

---

# 10. Ví dụ Borrow không Clone

```rust
fn inspect(text: &String) {
    println!("{text}");
}

fn main() {
    let text = String::from("Rust");

    inspect(&text);

    println!("{text}");
}
```

Không cần:

```rust
text.clone()
```

vì function chỉ mượn `text`.

---

# 11. Clone và Move trong function

### Move

```rust
fn consume(text: String) {
    println!("{text}");
}

fn main() {
    let text = String::from("Rust");

    consume(text);

    // text không còn usable
}
```

### Clone

```rust
fn consume(text: String) {
    println!("{text}");
}

fn main() {
    let text = String::from("Rust");

    consume(text.clone());

    println!("{text}");
}
```

Ở đây:

```text
text
 │
 ├── original
 │
 └── clone → consume()
```

Function consume bản clone.

Original vẫn thuộc `main`.

---

# 12. Đây là một use case hợp lý của Clone

Ví dụ:

```rust
fn save_title(title: String) {
    println!("Saving: {title}");
}
```

Nếu bạn vừa cần giữ title:

```rust
fn main() {
    let title = String::from("Rust Book");

    save_title(title.clone());

    println!("Original: {title}");
}
```

Đây có thể là thiết kế hợp lý.

Nhưng hãy luôn hỏi:

> Có thật sự cần hai ownership không?

---

# 13. Clone với `Vec`

`Vec<T>` cũng implement `Clone` nếu `T: Clone`.

```rust
fn main() {
    let numbers = vec![1, 2, 3];

    let copy = numbers.clone();

    println!("{numbers:?}");
    println!("{copy:?}");
}
```

Output:

```text
[1, 2, 3]
[1, 2, 3]
```

---

# 14. Clone với Vec<String>

Ví dụ:

```rust
fn main() {
    let books = vec![
        String::from("Rust"),
        String::from("Python"),
        String::from("Go"),
    ];

    let copied_books = books.clone();

    println!("{books:?}");
    println!("{copied_books:?}");
}
```

Điều quan trọng:

```text
Vec
 │
 ├── String
 ├── String
 └── String
```

Clone `Vec<String>` sẽ clone các phần tử `String`.

---

# 15. Clone là recursive

Với:

```rust
Vec<String>
```

quá trình conceptually:

```text
Vec.clone()
    │
    ├── String.clone()
    ├── String.clone()
    └── String.clone()
```

Do đó cần:

```text
Vec<T>: Clone
```

khi:

```text
T: Clone
```

---

# 16. Clone với Struct

Giả sử:

```rust
struct Story {
    title: String,
}
```

Code:

```rust
fn main() {
    let story = Story {
        title: String::from("Rust Book"),
    };

    let copy = story.clone();
}
```

Code này **không compile**.

Tại sao?

`Story` chưa implement `Clone`.

---

# 17. Derive Clone

Rust cho phép:

```rust
#[derive(Clone)]
struct Story {
    title: String,
}
```

Sau đó:

```rust
fn main() {
    let story = Story {
        title: String::from("Rust Book"),
    };

    let copy = story.clone();

    println!("{}", story.title);
    println!("{}", copy.title);
}
```

Chạy được.

---

# 18. `#[derive(Clone)]`

Đây là một attribute:

```rust
#[derive(Clone)]
```

Rust tự động sinh implementation `Clone` cho struct nếu các field cần thiết cũng `Clone`.

Ví dụ:

```rust
#[derive(Clone)]
struct Story {
    title: String,
    author: String,
}
```

Vì:

```text
String: Clone
```

nên:

```text
Story: Clone
```

---

# 19. Clone với nested struct

Ví dụ:

```rust
#[derive(Clone)]
struct Chapter {
    title: String,
}

#[derive(Clone)]
struct Story {
    title: String,
    chapters: Vec<Chapter>,
}
```

Khi:

```rust
let copy = story.clone();
```

conceptually:

```text
Story.clone()
 │
 ├── title.clone()
 │
 └── chapters.clone()
       │
       ├── Chapter.clone()
       ├── Chapter.clone()
       └── ...
```

Đây là **deep structural cloning** theo implementation của từng field.

---

# 20. Không phải Clone lúc nào cũng "deep copy"

Đây là nuance rất quan trọng.

Không nên định nghĩa:

> `Clone` = deep copy mọi thứ.

Chính xác hơn:

> `Clone` tạo một giá trị mới theo semantics do type định nghĩa.

Ví dụ một type có thể implement `Clone` bằng cách clone một handle, reference-count, hoặc resource abstraction thay vì sao chép toàn bộ underlying resource.

Do đó:

```text
Clone ≠ luôn luôn deep copy tất cả resource
```

---

# 21. Clone trait

Trait có dạng đơn giản:

```rust
pub trait Clone {
    fn clone(&self) -> Self;
}
```

Ý nghĩa:

```text
&self
 │
 │ clone
 ▼
Self
```

Original không bị consume.

Đó là lý do:

```rust
let copy = value.clone();
```

vẫn dùng được:

```rust
value
```

sau đó.

---

# 22. Clone nhận `&self`

Điểm này rất đáng chú ý.

Nếu:

```rust
fn clone(&self) -> Self
```

thì:

```text
clone()
```

**borrow object**, không lấy ownership của original.

Ví dụ:

```rust
let a = String::from("Rust");

let b = a.clone();

println!("{a}");
```

`a` vẫn tồn tại.

---

# 23. Clone vs một function consume

So sánh:

```rust
fn consume(value: String)
```

và:

```rust
fn clone(&self) -> Self
```

### consume

```text
value
 ↓
ownership transferred
```

### clone

```text
&value
 ↓
new independent value
```

---

# 24. `clone()` với `String`

Bạn có thể test:

```rust
fn main() {
    let a = String::from("Rust");

    let b = a.clone();

    drop(b);

    println!("{a}");
}
```

Output:

```text
Rust
```

`b` bị drop.

`a` vẫn còn.

Điều này chứng minh hai allocation độc lập.

---

# 25. Clone và Drop

```rust
fn main() {
    let a = String::from("Rust");

    let b = a.clone();

    println!("{a}");
    println!("{b}");
}
```

Cuối scope:

```text
b → drop
a → drop
```

Hai value có ownership riêng.

---

# 26. Clone với `Option`

Ví dụ:

```rust
fn main() {
    let value = Some(String::from("Rust"));

    let copy = value.clone();

    println!("{value:?}");
    println!("{copy:?}");
}
```

Output:

```text
Some("Rust")
Some("Rust")
```

Vì:

```text
Option<String>: Clone
```

do:

```text
String: Clone
```

---

# 27. Clone với `Result`

Ví dụ:

```rust
fn main() {
    let result: Result<String, String> =
        Ok(String::from("Rust"));

    let copy = result.clone();

    println!("{result:?}");
    println!("{copy:?}");
}
```

Nếu cả:

```text
T: Clone
E: Clone
```

thì:

```text
Result<T, E>: Clone
```

---

# 28. Clone trong Error Handling

Điều này về sau sẽ rất quan trọng.

Ví dụ:

```rust
#[derive(Clone, Debug)]
struct CrawlError {
    message: String,
}
```

Có thể clone error khi một phần hệ thống cần giữ bản sao.

Nhưng cũng không nên clone error vô lý.

Rust khuyến khích API rõ ràng về ownership.

---

# 29. Clone và `Arc`

Đây là một trường hợp đặc biệt rất quan trọng.

Sau này bạn sẽ gặp:

```rust
use std::sync::Arc;
```

Ví dụ:

```rust
let data = Arc::new(String::from("Rust"));

let a = data.clone();
let b = data.clone();
```

Ở đây:

```text
a.clone()
```

**không clone toàn bộ String**.

Nó clone `Arc` handle và tăng reference count.

Mô hình:

```text
          ┌─────────────┐
          │ String data │
          └─────────────┘
             ▲   ▲   ▲
             │   │   │
             a   b  data
```

Đây là ví dụ rất tốt để nhớ:

> `Clone` có semantics phụ thuộc vào type.

---

# 30. Clone và Rc

Tương tự:

```rust
use std::rc::Rc;

let data = Rc::new(String::from("Rust"));

let a = Rc::clone(&data);
let b = Rc::clone(&data);
```

Ở đây clone `Rc` không tạo thêm một `String`.

Nó tạo thêm một owner thông qua reference counting.

```text
Rc
 │
 ├── owner 1
 ├── owner 2
 └── owner 3
       │
       ▼
    String
```

Điều này rất khác:

```rust
String::clone()
```

---

# 31. Vì vậy hãy nhớ

```text
Clone
```

không tự nó nói cho bạn biết:

```text
"Bao nhiêu byte đã được copy?"
```

Muốn biết, phải xem semantics của type.

Ví dụ:

```text
String::clone()
→ clone string data

Vec<String>::clone()
→ clone vector + elements

Rc<T>::clone()
→ clone Rc handle / increment count

Arc<T>::clone()
→ clone Arc handle / increment count
```

---

# 32. Clone và Performance

Giả sử:

```rust
struct Story {
    title: String,
    content: String,
    images: Vec<String>,
}
```

Nếu:

```rust
let copy = story.clone();
```

có thể rất đắt.

Mô hình:

```text
Story
 │
 ├── title       → allocation
 ├── content     → allocation lớn
 └── images      → Vec
       ├── image
       ├── image
       ├── image
       └── ...
```

Clone có thể tạo rất nhiều allocation.

---

# 33. Đây là vấn đề thực tế với crawler

Trong crawler framework của bạn:

```rust
struct Chapter {
    title: String,
    content: String,
    images: Vec<String>,
}
```

Nếu content:

```text
500 KB
```

và images:

```text
100 URLs
```

thì:

```rust
let backup = chapter.clone();
```

có thể tạo một bản sao đáng kể.

Nếu bạn chỉ cần đọc:

```rust
fn parse(chapter: &Chapter)
```

thì clone là không cần thiết.

---

# 34. Khi nào Clone hợp lý?

Một số trường hợp:

### 1. Cần hai ownership độc lập

```rust
let b = a.clone();
```

### 2. API thực sự yêu cầu ownership

```rust
process(a.clone());
```

nhưng caller vẫn cần `a`.

### 3. Snapshot dữ liệu

```text
current state
     ↓
clone
     ↓
snapshot
```

### 4. Cache

```text
original
   ↓
clone
   ↓
cache
```

### 5. Test

Tạo dữ liệu test độc lập.

---

# 35. Khi nào không nên Clone?

### Trường hợp 1

Function chỉ đọc:

```rust
fn inspect(story: &Story)
```

Không cần:

```rust
inspect(story.clone());
```

---

### Trường hợp 2

Có thể Move luôn:

```rust
save(story);
```

Nếu caller không cần `story` nữa.

Không cần:

```rust
save(story.clone());
```

---

### Trường hợp 3

Chỉ cần một phần dữ liệu:

Thay vì:

```rust
process(story.clone());
```

có thể thiết kế API:

```rust
process(&story.title);
```

---

# 36. Clone như một "escape hatch"

Có một anti-pattern:

```text
Compiler:
    value moved

Developer:
    clone()

Compiler:
    okay

Developer:
    done
```

Đây không phải cách học Rust tốt.

Thay vào đó:

```text
Compiler:
    value moved

Developer:
    tại sao value bị move?

    ↓

    Function có cần ownership không?

    ↓

    Nếu không:
        borrow

    Nếu có:
        move

    Nếu thực sự cần 2 values:
        clone
```

Đây là tư duy chuyên nghiệp.

---

# 37. Clone vs Borrow

Một ví dụ cực kỳ quan trọng:

### Cách 1 — Clone

```rust
fn print_title(title: String) {
    println!("{title}");
}

fn main() {
    let title = String::from("Rust");

    print_title(title.clone());

    println!("{title}");
}
```

### Cách 2 — Borrow

```rust
fn print_title(title: &str) {
    println!("{title}");
}

fn main() {
    let title = String::from("Rust");

    print_title(&title);

    println!("{title}");
}
```

Cách 2 thường tốt hơn nếu function chỉ cần đọc.

---

# 38. Clone vs Move

```rust
fn consume(title: String) {
    println!("{title}");
}

fn main() {
    let title = String::from("Rust");

    consume(title);
}
```

Đây có thể là cách tốt nhất nếu:

```text
main không cần title nữa
```

Không clone.

---

# 39. Một nguyên tắc thiết kế API

Khi thiết kế function:

### Nếu function cần sở hữu:

```rust
fn save(story: Story)
```

### Nếu chỉ đọc:

```rust
fn inspect(story: &Story)
```

### Nếu cần thay đổi:

```rust
fn update(story: &mut Story)
```

Đừng thiết kế:

```rust
fn inspect(story: Story)
```

rồi bắt caller:

```rust
inspect(story.clone());
```

chỉ vì function không thực sự cần ownership.

---

# 40. Clone trong Pipeline

Ví dụ crawler:

```text
HTTP
 │
 ▼
Response
 │
 ▼
Parser
 │
 ▼
Story
 │
 ├──────────────┐
 ▼              ▼
Repository     Cache
```

Nếu cả Repository và Cache thực sự cần ownership độc lập:

```text
Story
 │
 ├── move → Repository
 │
 └── clone → Cache
```

Nhưng nếu Cache chỉ đọc:

```text
Story
 │
 ├── move → Repository
 │
 └── borrow → Cache
```

Có thể tránh clone.

---

# 41. Clone trong Multi-thread

Sau này khi học concurrency:

```rust
use std::sync::Arc;
```

thường sẽ gặp:

```rust
let config = Arc::new(config);

let worker_config = Arc::clone(&config);
```

Ở đây:

```text
Arc::clone
```

thường là cách idiomatic.

Không nên viết:

```rust
config.clone()
```

về mặt readability, dù cả hai có thể gọi cùng semantics.

`Arc::clone(&config)` làm rõ:

> Tôi đang clone smart-pointer handle, không phải clone toàn bộ data.

---

# 42. Tự implement Clone

Bạn có thể tự viết:

```rust
#[derive(Debug)]
struct User {
    name: String,
}
```

và implement:

```rust
impl Clone for User {
    fn clone(&self) -> Self {
        Self {
            name: self.name.clone(),
        }
    }
}
```

Sau đó:

```rust
fn main() {
    let user = User {
        name: String::from("Alice"),
    };

    let copy = user.clone();

    println!("{user:?}");
    println!("{copy:?}");
}
```

---

# 43. Tại sao `self.name.clone()`?

Bởi vì:

```text
self
 ↓
borrow
```

Function clone không được consume original.

Sau đó:

```rust
name: self.name.clone()
```

tạo `String` mới.

Mô hình:

```text
user
 │
 └── name ────────> String A

copy
 │
 └── name ────────> String B
```

---

# 44. Clone với field không Clone

Ví dụ:

```rust
struct MyType {
    data: String,
}
```

`String` Clone được.

Nhưng nếu:

```rust
struct MyType {
    resource: SomeNonCloneType,
}
```

thì không thể tự động:

```rust
#[derive(Clone)]
```

nếu field không implement `Clone`.

Compiler sẽ báo lỗi.

Điều này rất hợp lý:

> Rust không thể tự đoán cách tạo bản sao hợp lệ của resource.

---

# 45. Clone có thể chứa logic riêng

Một type có thể định nghĩa:

```rust
impl Clone for MyType {
    fn clone(&self) -> Self {
        // custom behavior
    }
}
```

Do đó `clone()` không phải một phép copy máy móc.

Type author quyết định semantics.

---

# 46. `clone_from()`

Trait `Clone` còn có:

```rust
fn clone_from(&mut self, source: &Self)
```

Ví dụ:

```rust
let mut a = String::from("hello");
let b = String::from("Rust");

a.clone_from(&b);
```

Sau đó:

```text
a = "Rust"
b = "Rust"
```

Điểm đáng chú ý:

```text
clone()
```

thường tạo value mới.

Còn:

```text
clone_from()
```

clone vào một value đã tồn tại và type có thể tối ưu việc tái sử dụng allocation.

---

# 47. Khi nào `clone_from()` hữu ích?

Khi bạn có:

```rust
let mut destination = ...
let source = ...
```

và muốn:

```text
destination ← clone(source)
```

Type có thể tái sử dụng resource đã cấp phát.

Đây là optimization cấp thấp hơn.

Không cần sử dụng thường xuyên khi mới học.

Nhưng bạn nên biết nó tồn tại.

---

# 48. Bài tập 1 — Clone cơ bản

Chạy:

```rust
fn main() {
    let a = String::from("Rust");

    let b = a.clone();

    println!("a = {a}");
    println!("b = {b}");
}
```

Sau đó giải thích:

```text
a còn usable?
b còn usable?
hai biến có ownership độc lập?
```

---

# 49. Bài tập 2 — Move vs Clone

Viết hai chương trình.

### Chương trình A

```rust
let a = String::from("Rust");
let b = a;
```

### Chương trình B

```rust
let a = String::from("Rust");
let b = a.clone();
```

Sau đó lập bảng:

|                    | Move | Clone |
| ------------------ | ---- | ----- |
| `a` còn usable?    | ?    | ?     |
| `b` tồn tại?       | ?    | ?     |
| allocation mới?    | ?    | ?     |
| ownership độc lập? | ?    | ?     |

---

# 50. Bài tập 3 — Struct

Tạo:

```rust
#[derive(Clone, Debug)]
struct Story {
    title: String,
    author: String,
}
```

Sau đó:

```rust
fn main() {
    let story = Story {
        title: String::from("Rust Book"),
        author: String::from("Rust Team"),
    };

    let copy = story.clone();

    println!("{story:?}");
    println!("{copy:?}");
}
```

Quan sát kết quả.

---

# 51. Bài tập 4 — Nested Clone

Tạo:

```rust
#[derive(Clone, Debug)]
struct Chapter {
    title: String,
}

#[derive(Clone, Debug)]
struct Story {
    title: String,
    chapters: Vec<Chapter>,
}
```

Tạo một `Story` có 3 chapter.

Clone nó:

```rust
let backup = story.clone();
```

Sau đó in:

```rust
println!("{story:#?}");
println!("{backup:#?}");
```

Hãy vẽ ownership tree:

```text
story
 │
 ├── title
 │
 └── chapters
       ├── Chapter
       ├── Chapter
       └── Chapter
```

và bản clone tương ứng.

---

# 52. Bài tập 5 — Tìm Clone thừa

Cho:

```rust
fn print_story(story: &Story) {
    println!("{}", story.title);
}
```

Code:

```rust
let story = get_story();

print_story(&story);
```

Có cần:

```rust
print_story(&story.clone());
```

không?

**Không.**

Hãy giải thích tại sao.

---

# 53. Bài tập 6 — Clone hợp lý

Cho:

```rust
fn save_story(story: Story) {
    println!("Saved: {}", story.title);
}
```

Bạn muốn giữ `story` sau khi save.

Viết:

```rust
let story = ...;
```

và gọi:

```text
save_story(...)
```

sao cho sau đó vẫn có thể:

```rust
println!("{}", story.title);
```

Trong bài này `clone()` có thể là một giải pháp hợp lý.

---

# 54. Bài tập 7 — Clone vs Arc

Chạy:

```rust
use std::sync::Arc;

fn main() {
    let data = Arc::new(String::from("Rust"));

    let a = Arc::clone(&data);
    let b = Arc::clone(&data);

    println!("{data}");
    println!("{a}");
    println!("{b}");
}
```

Hãy giải thích:

```text
data
a
b
```

có phải đang chứa ba bản sao của `String` không?

**Không.**

Chúng là ba `Arc` handle cùng sở hữu dữ liệu thông qua reference counting.

---

# 55. Bài tập 8 — Crawler

Tạo:

```rust
#[derive(Clone, Debug)]
struct CrawlConfig {
    user_agent: String,
    timeout: u64,
}
```

Sau đó:

```rust
let config = CrawlConfig {
    user_agent: String::from("RustCrawler"),
    timeout: 30,
};

let worker_config = config.clone();
```

In:

```text
config
worker_config
```

Sau đó trả lời:

> Tại sao trong một crawler framework, việc clone một config nhỏ có thể hợp lý hơn clone một `Chapter` chứa hàng MB content?

---

# 56. Bài tập 9 — Đừng Clone

Cho:

```rust
fn inspect(story: &Story) {
    println!("{}", story.title);
}
```

Code:

```rust
let story = get_story();

inspect(story.clone());
```

Hãy sửa thành code **không clone**.

Đáp án về tư duy:

```text
inspect(&story)
```

---

# 57. Bài tập 10 — Thiết kế API

Với:

```rust
struct Story {
    title: String,
}
```

Thiết kế 3 API:

```text
save
inspect
rename
```

Sao cho:

```text
save    → ownership
inspect → borrow
rename  → mutable borrow
```

Bạn nên nghĩ đến:

```rust
fn save(story: Story)
fn inspect(story: &Story)
fn rename(story: &mut Story)
```

Đây là thiết kế API Rust cơ bản nhưng cực kỳ quan trọng.

---

# 58. Mental Model

Sau Buổi 23, hãy nhìn:

```rust
let b = a.clone();
```

như:

```text
a
│
├──── original value
│
└──── clone()
       │
       ▼
     b
```

Trong khi:

```rust
let b = a;
```

là:

```text
a
 │
 │ MOVE
 ▼
b
```

Còn:

```rust
foo(&a);
```

là:

```text
a
 │
 │ BORROW
 ▼
foo
```

---

# 59. Một bảng tổng hợp cực kỳ quan trọng

| Cách                | Ownership          |             Tạo dữ liệu mới | Original còn dùng? |
| ------------------- | ------------------ | --------------------------: | -----------------: |
| `let b = a`         | Move               |                Thường không |                  ❌ |
| `let b = a.clone()` | Clone              | Có, theo semantics của type |                  ✅ |
| `foo(a)`            | Move/Copy tùy type |            Không nhất thiết |   ❌ với non-`Copy` |
| `foo(&a)`           | Borrow             |                       Không |                  ✅ |
| `foo(&mut a)`       | Mutable Borrow     |                       Không |                  ✅ |
| `Rc::clone(&a)`     | Clone handle       |             Không clone `T` |                  ✅ |
| `Arc::clone(&a)`    | Clone handle       |             Không clone `T` |                  ✅ |

---

# 60. Nguyên tắc vàng

Khi compiler báo:

```text
value moved
```

**đừng lập tức viết:**

```rust
.clone()
```

Hãy suy nghĩ theo thứ tự:

```text
① Có thể Move luôn không?
        ↓
② Nếu không, function có chỉ cần đọc?
        ↓
    &T / &str
        ↓
③ Nếu cần thay đổi?
        ↓
    &mut T
        ↓
④ Nếu thực sự cần hai ownership độc lập?
        ↓
    clone()
```

Đây là tư duy sẽ giúp code Rust của bạn tốt hơn rất nhiều.

---

# 61. Tổng kết Buổi 23

Bạn cần nắm chắc:

```text
Clone
│
├── tạo một value mới
│
├── original vẫn còn
│
├── thường có chi phí
│
├── semantics phụ thuộc vào type
│
├── #[derive(Clone)]
│
├── String::clone()
│      → clone dữ liệu String
│
├── Vec<T>::clone()
│      → clone elements
│
├── Rc::clone()
│      → clone handle
│
└── Arc::clone()
       → clone handle
```

Quan trọng nhất:

> **Move chuyển ownership. Clone tạo thêm một value theo semantics của type. Borrow chỉ cho phép truy cập mà không lấy ownership.**

---

# 62. Roadmap

```text
✓ Buổi 21 — Ownership
✓ Buổi 22 — Move
▶ Buổi 23 — Clone          ← hôm nay
  Buổi 24 — Copy
  Buổi 25 — Borrow
  Buổi 26 — Mutable Borrow
  Buổi 27 — Slice
  Buổi 28 — String
  Buổi 29 — String vs &str
  Buổi 30 — Ownership Deep Dive
```

**Buổi 24 — Copy** sẽ giải thích tại sao:

```rust
let a = 10;
let b = a;
println!("{a}");
```

lại hợp lệ, trong khi:

```rust
let a = String::from("Rust");
let b = a;
println!("{a}");
```

lại lỗi; đồng thời đi sâu vào `Copy` trait, `Clone` vs `Copy`, điều kiện để một type được `Copy`, stack semantics và cách tự thiết kế các type `Copy`.
