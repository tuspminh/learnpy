# Rust — Phần III: Ownership

# Buổi 22 — Move

Hôm nay chúng ta đi sâu vào **Move** — cơ chế quan trọng nhất đứng sau rất nhiều compiler error của Rust.

Sau buổi này, bạn phải hiểu được:

```text
let b = a;
```

không phải lúc nào cũng có nghĩa là:

```text
b = copy(a)
```

Trong Rust, với các kiểu **không implement `Copy`**, câu lệnh này thường có nghĩa:

```text
Ownership của value chuyển từ a → b
```

---

# 1. Move là gì?

Ví dụ:

```rust
fn main() {
    let s1 = String::from("hello");

    let s2 = s1;

    println!("{s2}");
}
```

Code chạy bình thường.

Sau:

```rust
let s2 = s1;
```

ta có:

```text
s1 ──X──> String

s2 ──────> String
             │
             ▼
          "hello"
```

`String` hiện thuộc về `s2`.

`s1` đã bị **moved**.

---

# 2. Tại sao Rust phải Move?

Hãy nhìn cấu trúc đơn giản hóa của `String`:

```text
STACK                         HEAP

s1
┌──────────────┐
│ ptr ─────────┼──────────────> "hello"
│ len = 5      │
│ capacity = 5 │
└──────────────┘
```

Nếu Rust cho phép:

```rust
let s2 = s1;
```

tạo ra một bản sao nông:

```text
STACK                         HEAP

s1 ─────┐
        ├────────────────────> "hello"
s2 ─────┘
```

thì có hai biến cùng nghĩ rằng chúng sở hữu cùng một allocation.

Khi `s1` bị drop:

```text
s1
 ↓
free("hello")
```

sau đó `s2` vẫn còn:

```text
s2 ─────> freed memory
```

Đây là **use-after-free**.

Nếu `s2` tiếp tục được drop, có nguy cơ **double free**.

Rust giải quyết bằng:

```text
s1
 │
 │ move
 ▼
s2
```

Sau Move:

```text
s1 = invalid
s2 = owner
```

---

# 3. Move không nhất thiết là copy dữ liệu

Đây là điểm cực kỳ quan trọng.

Khi:

```rust
let s2 = s1;
```

với `String`, Rust **không cần copy toàn bộ `"hello"` sang một allocation mới**.

Thay vào đó, ownership được chuyển.

Có thể hình dung:

```text
Trước:

s1 ─────────> Heap data


Sau:

s1  X

s2 ─────────> Heap data
```

Điều này giúp Move rất hiệu quả.

---

# 4. Move khác Clone

Hai khái niệm:

```text
Move
Clone
```

hoàn toàn khác nhau.

### Move

```rust
let s2 = s1;
```

```text
ownership:
s1 ─────→ s2
```

### Clone

```rust
let s2 = s1.clone();
```

```text
ownership:

s1 ─────→ data A

s2 ─────→ data B
```

`Clone` tạo một value độc lập.

Buổi 23 chúng ta sẽ đi sâu vào `Clone`.

---

# 5. Ví dụ Move cơ bản

```rust
fn main() {
    let name = String::from("Rust");

    let other = name;

    println!("{other}");
}
```

Output:

```text
Rust
```

Nhưng:

```rust
println!("{name}");
```

sẽ lỗi.

---

# 6. Compiler error

Thử:

```rust
fn main() {
    let name = String::from("Rust");

    let other = name;

    println!("{name}");
    println!("{other}");
}
```

Chạy:

```bash
cargo check
```

Bạn sẽ nhận lỗi tương tự:

```text
error[E0382]: borrow of moved value: `name`
```

Thông điệp quan trọng:

```text
value moved here
```

và:

```text
value borrowed here after move
```

Compiler đang nói:

```text
name đã bị move
nhưng bạn lại sử dụng name
```

---

# 7. Đọc compiler error theo Flow

Khi gặp:

```text
borrow of moved value
```

hãy tìm:

### Bước 1

Value ban đầu:

```rust
let name = String::from("Rust");
```

### Bước 2

Tìm nơi Move:

```rust
let other = name;
```

### Bước 3

Tìm nơi sử dụng sau Move:

```rust
println!("{name}");
```

Flow:

```text
name
 │
 │ owns
 ▼
String
 │
 │ move
 ▼
other
 │
 ▼
name invalid
```

---

# 8. Move xảy ra khi gán

Một trường hợp phổ biến:

```rust
let a = String::from("Rust");
let b = a;
```

Đây là Move.

Nhưng Move không chỉ xảy ra khi assignment.

---

# 9. Move khi truyền vào function

Ví dụ:

```rust
fn consume(value: String) {
    println!("{value}");
}

fn main() {
    let name = String::from("Rust");

    consume(name);

    println!("{name}");
}
```

`name` được Move vào:

```text
consume()
```

Flow:

```text
main
 │
 │ name
 │
 │ move
 ▼
consume
 │
 └── value
```

Sau khi gọi:

```rust
consume(name);
```

`name` không còn usable.

---

# 10. Function có thể "consume" value

Đây là thuật ngữ bạn sẽ gặp thường xuyên:

> **consume a value**

Ví dụ:

```rust
fn process_story(story: String) {
    println!("Processing {story}");
}
```

Function này **consume** `String`.

Khi:

```rust
process_story(title);
```

ownership chuyển vào function.

---

# 11. Move khi return

Move cũng xảy ra khi return.

```rust
fn create_story() -> String {
    let title = String::from("Rust Book");

    title
}
```

Ở đây:

```text
title
  │
  │ move
  ▼
return value
  │
  ▼
caller
```

Ví dụ:

```rust
fn main() {
    let story = create_story();

    println!("{story}");
}
```

Ownership đã được chuyển từ `create_story()` về `main`.

---

# 12. Move vào function rồi trả ra

Đây là pattern rất hay:

```rust
fn process(value: String) -> String {
    println!("Processing {value}");

    value
}
```

Sau đó:

```rust
fn main() {
    let value = String::from("Rust");

    let value = process(value);

    println!("{value}");
}
```

Flow:

```text
main
 │
 │ value
 ▼
process()
 │
 │ ownership
 ▼
value
 │
 │ return
 ▼
main
 │
 └── value
```

Ownership đi qua function.

---

# 13. Shadowing giúp pattern này đẹp hơn

```rust
let value = String::from("Rust");

let value = process(value);
```

Đây là **shadowing**, không phải mutation.

Biến binding mới:

```text
value #1
   ↓
move
   ↓
value #2
```

Chúng ta sẽ học shadowing kỹ hơn ở phần Variables.

---

# 14. Move trong Struct

Ví dụ:

```rust
struct Story {
    title: String,
}
```

Tạo:

```rust
fn main() {
    let title = String::from("Rust Book");

    let story = Story {
        title,
    };

    println!("{}", story.title);
}
```

Ownership:

```text
title
  │
  │ move
  ▼
story.title
```

Sau khi tạo `story`, biến:

```rust
title
```

không còn usable.

---

# 15. Kiểm tra

```rust
fn main() {
    let title = String::from("Rust Book");

    let story = Story {
        title,
    };

    println!("{title}");
}
```

Lỗi.

Vì:

```text
title
 ↓
move
 ↓
story.title
```

---

# 16. Move từng field

Điều thú vị là Rust có thể Move từng field.

```rust
struct Story {
    title: String,
    author: String,
}
```

```rust
fn main() {
    let story = Story {
        title: String::from("Rust Book"),
        author: String::from("Rust Team"),
    };

    let title = story.title;

    println!("{title}");
}
```

`title` đã được move khỏi `story`.

Nhưng `author` vẫn còn thuộc `story`.

Có thể hình dung:

```text
story
 │
 ├── title ──→ moved
 │
 └── author ──→ still owned
```

---

# 17. Partial Move

Khái niệm này gọi là:

> **Partial Move**

Ví dụ:

```rust
struct Story {
    title: String,
    author: String,
}

fn main() {
    let story = Story {
        title: String::from("Rust"),
        author: String::from("Alice"),
    };

    let title = story.title;

    println!("{title}");
    println!("{}", story.author);
}
```

Code này có thể chạy.

Vì:

```text
story.title
```

đã được Move, nhưng:

```text
story.author
```

vẫn còn.

---

# 18. Nhưng không thể dùng toàn bộ Struct

Ví dụ:

```rust
let title = story.title;

println!("{story:?}");
```

sẽ có vấn đề nếu `Story` derive `Debug`, vì toàn bộ `story` đã ở trạng thái partially moved.

Ví dụ:

```rust
#[derive(Debug)]
struct Story {
    title: String,
    author: String,
}
```

Sau:

```rust
let title = story.title;
```

không thể coi `story` như một value hoàn chỉnh nữa.

---

# 19. Move trong Tuple

```rust
fn main() {
    let data = (
        String::from("Rust"),
        String::from("Python"),
    );

    let first = data.0;

    println!("{first}");
    println!("{}", data.1);
}
```

Ở đây:

```text
data
 ├── .0 → moved
 └── .1 → still valid
```

Đây cũng là Partial Move.

---

# 20. Move trong Vec

Với `Vec`, cần cẩn thận.

```rust
fn main() {
    let books = vec![
        String::from("Rust"),
        String::from("Python"),
        String::from("Go"),
    ];

    let first = books[0];

    println!("{first}");
}
```

Code này không compile.

Tại sao?

`books[0]` là một phần tử được truy cập qua indexing, nhưng việc lấy trực tiếp `String` sẽ cố Move value ra khỏi `Vec`.

Rust không cho phép Move một non-`Copy` value ra khỏi borrowed container theo cách này.

---

# 21. Nếu muốn lấy phần tử khỏi Vec?

Có nhiều cách.

Ví dụ:

```rust
let first = books.remove(0);
```

`remove()` thực sự lấy ownership của phần tử ra khỏi `Vec`.

```text
Vec
 ├── Rust  ← remove
 ├── Python
 └── Go
```

Sau:

```text
first ──→ Rust
```

Đây là một ví dụ rất thực tế của Ownership.

---

# 22. `Vec::pop()`

Một cách khác:

```rust
let last = books.pop();
```

Kết quả:

```rust
Option<String>
```

Ví dụ:

```rust
if let Some(book) = books.pop() {
    println!("Removed: {book}");
}
```

Ở đây ownership của phần tử được lấy ra khỏi Vec.

---

# 23. Move và `for`

Đây là một nơi Move rất dễ xuất hiện.

```rust
fn main() {
    let books = vec![
        String::from("Rust"),
        String::from("Python"),
        String::from("Go"),
    ];

    for book in books {
        println!("{book}");
    }

    println!("{books:?}");
}
```

Code lỗi.

Tại sao?

Vòng:

```rust
for book in books
```

đã **consume `books`**.

Các phần tử được lấy ownership ra khỏi collection.

Flow:

```text
books
 │
 │ into iteration
 ▼
for
 │
 ├── book 1
 ├── book 2
 └── book 3
```

Sau vòng lặp:

```text
books → moved
```

---

# 24. Đây là lý do `into_iter()` quan trọng

Về bản chất:

```rust
for book in books
```

đối với `Vec<T>` có thể hiểu theo hướng:

```rust
for book in books.into_iter()
```

`into_iter()` **consumes collection**.

Nó chuyển ownership của các phần tử ra khỏi collection.

---

# 25. So sánh ba kiểu iteration

Sau này bạn sẽ thường gặp:

```rust
for book in books
```

```rust
for book in &books
```

```rust
for book in &mut books
```

Ý nghĩa ownership:

```text
books
 │
 ├── into → ownership
 │
 ├── &    → immutable borrow
 │
 └── &mut → mutable borrow
```

Hai dòng cuối thuộc phần Borrowing.

Nhưng ngay từ hôm nay hãy nhớ:

> `for x in collection` có thể consume collection.

---

# 26. Ví dụ crawler rất thực tế

Giả sử:

```rust
let tasks = vec![
    String::from("chapter-1"),
    String::from("chapter-2"),
    String::from("chapter-3"),
];
```

Nếu:

```rust
for task in tasks {
    process(task);
}
```

thì sau loop:

```text
tasks → moved
```

Điều này có thể hoàn toàn đúng nếu worker muốn **consume task queue**.

---

# 27. Move có lợi, không phải vấn đề

Đừng nghĩ:

> Move là thứ compiler gây khó chịu.

Không.

Move là một cơ chế rất mạnh.

Ví dụ:

```rust
fn process_task(task: Task) {
    // function owns task
}
```

Khi task được chuyển vào worker:

```text
Producer
   │
   │ ownership
   ▼
Worker
   │
   ▼
process
   │
   ▼
drop
```

Không cần:

```text
reference counting
garbage collector
manual free
```

---

# 28. Move giúp API rõ ràng

Nhìn function:

```rust
fn save_story(story: Story)
```

ta biết:

> Function này nhận ownership của `Story`.

Nhìn:

```rust
fn inspect_story(story: &Story)
```

ta biết:

> Function chỉ mượn.

Đây là một trong những điểm Rust API rất rõ ràng.

---

# 29. Move với `Option<T>`

Ví dụ:

```rust
fn main() {
    let story = Some(String::from("Rust"));

    let value = story.unwrap();

    println!("{value}");
}
```

`unwrap()` lấy ownership của `String`.

Sau đó `story` đã bị consume.

Đây là lý do một số method có chữ:

```text
self
```

thay vì:

```text
&self
```

sẽ consume object.

---

# 30. `self` và Move

Sau này khi học `impl`, bạn sẽ gặp:

```rust
impl Story {
    fn consume(self) {
        println!("{}", self.title);
    }
}
```

Khi:

```rust
story.consume();
```

`self` được Move vào method.

Sau đó:

```rust
story
```

không còn usable.

Có thể hiểu:

```text
story
 │
 │ move
 ▼
self
```

Đây là một pattern rất quan trọng trong Rust API design.

---

# 31. Ba kiểu receiver

Sau này bạn sẽ gặp:

```rust
self
&self
&mut self
```

Có thể nhớ sơ bộ:

```text
self
  ↓
take ownership

&self
  ↓
borrow

&mut self
  ↓
mutable borrow
```

Hôm nay chúng ta tập trung vào:

```text
self → Move
```

---

# 32. Move và enum

Ví dụ:

```rust
enum CrawlTask {
    Story(String),
    Chapter(String),
}
```

```rust
let task = CrawlTask::Story(
    String::from("Rust"),
);
```

Khi match:

```rust
match task {
    CrawlTask::Story(title) => {
        println!("{title}");
    }

    CrawlTask::Chapter(title) => {
        println!("{title}");
    }
}
```

`match` có thể lấy ownership của dữ liệu trong enum.

Sau:

```rust
match task { ... }
```

`task` có thể đã được consumed.

---

# 33. Đây chính là lý do `match` mạnh

`match` không chỉ kiểm tra giá trị.

Nó còn **destructure và Move**.

Ví dụ:

```rust
match task {
    CrawlTask::Story(title) => {
        process(title);
    }

    CrawlTask::Chapter(title) => {
        process(title);
    }
}
```

`title` nhận ownership.

---

# 34. Move trong `match`

Hãy nhớ pattern:

```text
enum
 ↓
match
 ↓
destructure
 ↓
move fields
```

Đây sẽ cực kỳ quan trọng khi bạn học:

```text
Option
Result
Error handling
State machine
Trait
Async
```

---

# 35. `match` với reference

Sau này khi không muốn Move, bạn có thể:

```rust
match &task {
    CrawlTask::Story(title) => {
        println!("{title}");
    }

    CrawlTask::Chapter(title) => {
        println!("{title}");
    }
}
```

Ở đây:

```text
&task
```

là borrow.

Do đó `task` vẫn tồn tại.

Đây chính là cầu nối từ:

```text
Move
```

sang:

```text
Borrow
```

---

# 36. Move và Closure

Rust closure cũng có thể capture ownership.

Ví dụ:

```rust
fn main() {
    let name = String::from("Rust");

    let consume = move || {
        println!("{name}");
    };

    consume();
}
```

Từ khóa:

```rust
move
```

ở closure có ý nghĩa:

> Closure lấy ownership của những giá trị mà nó capture.

Sau này khi học Closure và Async, phần này rất quan trọng.

---

# 37. `move` keyword không chỉ dùng trong assignment

Có hai khái niệm cần phân biệt:

### Move semantics

```rust
let b = a;
```

### `move` keyword

```rust
move || {
    ...
}
```

Cả hai đều liên quan đến ownership, nhưng `move` trong closure là cú pháp chỉ định capture ownership.

---

# 38. Move không xảy ra với mọi kiểu

Ví dụ:

```rust
let x = 10;
let y = x;

println!("{x}");
```

vẫn chạy.

Vì:

```text
i32: Copy
```

Do đó:

```text
x
 │
 ├── copy → y
 │
 └── x vẫn valid
```

---

# 39. Bảng so sánh

| Code                       | Hành vi        |
| -------------------------- | -------------- |
| `let b = a` với `String`   | Move           |
| `let b = a` với `Vec<i32>` | Move           |
| `let b = a` với `i32`      | Copy           |
| `foo(a)` với `String`      | Move           |
| `foo(a)` với `i32`         | Copy           |
| `foo(&a)`                  | Borrow         |
| `foo(&mut a)`              | Mutable Borrow |
| `a.clone()`                | Tạo bản sao    |

---

# 40. Move vs Copy vs Clone

Đây là bảng bạn nên thuộc:

```text
                 String
                   │
          ┌────────┼────────┐
          │        │        │
        Move     Clone    Borrow
          │        │        │
          ▼        ▼        ▼
       owner     copy     reference
       đổi       mới      không owner
```

Còn:

```text
i32
 │
 └── Copy
```

---

# 41. Khi nào Move là lựa chọn tốt?

Rất nhiều trường hợp.

Ví dụ:

```rust
fn save_story(story: Story) {
    database.save(story);
}
```

Nếu function cuối cùng phải lưu và sở hữu `story`, nhận ownership là hợp lý.

Không cần clone:

```rust
database.save(story.clone());
```

Nếu không thực sự cần hai bản.

---

# 42. Tránh Clone vô tội vạ

Người mới học Rust thường gặp lỗi:

```text
borrow of moved value
```

và giải quyết mọi thứ bằng:

```rust
.clone()
```

Ví dụ:

```rust
let story2 = story.clone();
process(story2);
```

Code chạy.

Nhưng có thể:

```text
clone toàn bộ dữ liệu
↓
copy heap allocation
↓
tốn memory
↓
tốn CPU
```

Move thường rẻ hơn Clone.

Đừng dùng `clone()` chỉ để làm compiler im lặng.

---

# 43. Tư duy đúng

Khi compiler báo Move:

Đừng hỏi ngay:

> "Làm sao clone?"

Hãy hỏi:

> "Function này có thực sự cần ownership không?"

Nếu không:

```text
&value
```

Nếu cần:

```text
value
```

Nếu cần một bản sao độc lập:

```text
value.clone()
```

Đây chính là tư duy Rust.

---

# 44. Bài tập 1 — Basic Move

Dự đoán kết quả:

```rust
fn main() {
    let a = String::from("Rust");
    let b = a;

    println!("{b}");
}
```

Sau đó trả lời:

```text
a còn usable không?
b có phải owner không?
```

---

# 45. Bài tập 2 — Move Error

Sửa:

```rust
fn main() {
    let a = String::from("Rust");
    let b = a;

    println!("{a}");
    println!("{b}");
}
```

Có ít nhất hai hướng:

```text
1. dùng b
2. clone a trước khi move
```

Ở bài này hãy thử **không dùng clone** trước.

---

# 46. Bài tập 3 — Function Move

Cho:

```rust
fn process(title: String) {
    println!("Processing: {title}");
}
```

Viết:

```rust
fn main()
```

sao cho:

```text
Processing: Rust Book
```

được in ra.

Sau đó thử sử dụng `title` sau:

```rust
process(title);

println!("{title}");
```

và giải thích lỗi.

---

# 47. Bài tập 4 — Return Move

Viết:

```rust
fn transform(value: String) -> String
```

Function chuyển:

```text
rust
```

thành:

```text
RUST
```

Sau đó:

```rust
let value = String::from("rust");

let value = transform(value);

println!("{value}");
```

Mục tiêu:

```text
RUST
```

---

# 48. Bài tập 5 — Struct Move

Tạo:

```rust
struct Story {
    title: String,
    author: String,
}
```

Sau đó:

```rust
let title = String::from("Rust Book");

let story = Story {
    title,
    author: String::from("Rust Team"),
};
```

Hãy thử:

```rust
println!("{title}");
```

và giải thích compiler.

---

# 49. Bài tập 6 — Partial Move

Cho:

```rust
struct Story {
    title: String,
    author: String,
}
```

Tạo:

```rust
let story = Story {
    title: String::from("Rust"),
    author: String::from("Alice"),
};
```

Move:

```rust
let title = story.title;
```

Sau đó thử:

```rust
println!("{}", story.author);
```

và:

```rust
println!("{}", story.title);
```

Dự đoán cái nào compile.

---

# 50. Bài tập 7 — Vec Ownership

Cho:

```rust
let books = vec![
    String::from("Rust"),
    String::from("Python"),
    String::from("Go"),
];
```

Thử:

```rust
for book in books {
    println!("{book}");
}

println!("{books:?}");
```

Giải thích tại sao `books` không còn usable.

---

# 51. Bài tập 8 — Crawler Task

Quay lại project buổi 20.

Tạo:

```rust
enum CrawlTask {
    Story(String),
    Chapter(String),
}
```

và:

```rust
fn process_task(task: CrawlTask) {
    match task {
        CrawlTask::Story(name) => {
            println!("Story: {name}");
        }

        CrawlTask::Chapter(name) => {
            println!("Chapter: {name}");
        }
    }
}
```

Sau đó:

```rust
let task = CrawlTask::Story(
    String::from("Rust Book")
);

process_task(task);
```

Hãy thử dùng:

```rust
println!("{:?}", task);
```

sau `process_task`.

Quan sát compiler và giải thích:

```text
task
 ↓
process_task
 ↓
match
 ↓
ownership consumed
```

---

# 52. Bài tập 9 — Không dùng Clone

Đây là bài tập quan trọng.

Cho:

```rust
fn save(title: String) {
    println!("Saving {title}");
}
```

Bạn có:

```rust
let title = String::from("Rust Book");
```

Hãy thiết kế code sao cho:

```text
title
 ↓
save()
```

mà **không clone**.

Sau đó trả lời:

> Sau khi `save()` kết thúc, có cần `title` nữa không?

Nếu không cần, Move là thiết kế hợp lý.

---

# 53. Bài tập 10 — Thiết kế API

Giả sử có:

```rust
struct Story {
    title: String,
}
```

Bạn cần 3 function:

```rust
fn save(story: Story)
```

```rust
fn inspect(story: &Story)
```

```rust
fn rename(story: &mut Story)
```

Chưa cần viết function body.

Hãy giải thích:

```text
save
 ↓
ownership

inspect
 ↓
borrow

rename
 ↓
mutable borrow
```

Đây là bài chuẩn bị trực tiếp cho:

```text
Buổi 25 — Borrow
Buổi 26 — Mutable Borrow
```

---

# 54. Một mental model rất quan trọng

Từ hôm nay hãy nhìn Rust như thế này:

```text
VALUE
 │
 ▼
OWNER
 │
 ├── move ───────→ new owner
 │
 ├── borrow ─────→ temporary access
 │
 ├── clone ──────→ independent value
 │
 └── copy ───────→ duplicated bits/value
```

Trong đó:

```text
Move
```

là **chuyển quyền sở hữu**.

---

# 55. Ownership Flow của một `String`

Hãy đọc đoạn code:

```rust
fn create() -> String {
    String::from("Rust")
}

fn process(value: String) -> String {
    println!("{value}");
    value
}

fn main() {
    let a = create();

    let b = process(a);

    println!("{b}");
}
```

Flow:

```text
create()
   │
   │ ownership
   ▼
a
   │
   │ move
   ▼
process(value)
   │
   │ return ownership
   ▼
b
```

Không cần clone.

Không cần GC.

Không cần free.

---

# 56. Đây chính là sức mạnh của Move

Một pipeline thực tế:

```text
HTTP Response
      │
      ▼
Parser
      │
      │ ownership
      ▼
Story
      │
      ▼
Repository
      │
      │ ownership
      ▼
Database
```

Mỗi tầng có thể **chuyển ownership** khi nó thực sự chịu trách nhiệm với resource.

Đây sẽ là một phần rất quan trọng khi sau này chúng ta xây crawler framework Rust.

---

# 57. Tổng kết Buổi 22

Bạn cần nhớ 8 ý:

```text
1. Move = chuyển ownership

2. String thường Move khi assignment

3. Function nhận T có thể lấy ownership

4. Return T có thể chuyển ownership về caller

5. Move không nhất thiết copy heap data

6. Move giúp tránh double free/use-after-free

7. Copy khác Move

8. Clone khác Move
```

Mental model:

```text
let a = String::from("Rust");

let b = a;
```

không đọc là:

```text
a → b
```

mà đọc là:

```text
a
 │
 │ ownership MOVE
 ▼
b
```

và:

```text
a = invalid
b = owner
```

---

# 58. Roadmap tiếp theo

```text
✓ Buổi 21 — Ownership
▶ Buổi 22 — Move          ← hôm nay
  Buổi 23 — Clone
  Buổi 24 — Copy
  Buổi 25 — Borrow
  Buổi 26 — Mutable Borrow
  Buổi 27 — Slice
  Buổi 28 — String
  Buổi 29 — String vs &str
  Buổi 30 — Ownership Deep Dive
```

**Buổi 23 — Clone** sẽ rất quan trọng vì chúng ta sẽ phân biệt thật kỹ **Move vs Clone**, shallow/deep copy, `Clone` trait, chi phí clone, `clone_from()`, và đặc biệt là **khi nào clone là thiết kế đúng và khi nào clone chỉ là cách né compiler**.
