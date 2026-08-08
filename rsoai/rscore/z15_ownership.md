# Rust Professional 2026 — Buổi 15

# Ownership — Nền móng quan trọng nhất của Rust

Nếu phải chọn **một chủ đề phân biệt Rust với phần lớn ngôn ngữ lập trình khác**, thì đó là:

> **Ownership — quyền sở hữu dữ liệu.**

Sau buổi này, bạn cần hiểu được tại sao Rust có thể đảm bảo memory safety mà không cần garbage collector.

Chúng ta sẽ không học Ownership theo kiểu thuộc lòng vài quy tắc. Ta sẽ xây dựng **mental model về Stack → Heap → Ownership → Move → Copy → Clone → Drop**.

---

# 1. Vấn đề Rust muốn giải quyết

Trong C/C++, programmer có thể gặp:

```text
use-after-free
double free
dangling pointer
memory leak
data race
```

Ví dụ ý tưởng:

```text
pointer
   ↓
memory
   ↓
free()
   ↓
pointer vẫn tồn tại
   ↓
use pointer
   ↓
💥
```

Rust thiết kế Ownership để compiler ngăn những lỗi này **ngay tại compile time**.

---

# 2. Ba quy tắc Ownership

Rust có ba quy tắc nền tảng.

## Rule 1

> Mỗi value trong Rust có một owner.

Ví dụ:

```rust
fn main() {
    let name = String::from("Alice");
}
```

Ở đây:

```text
name
  ↓
String value
```

`name` là owner.

---

## Rule 2

> Chỉ có một owner tại một thời điểm.

Điều này cực kỳ quan trọng.

```rust
let s1 = String::from("hello");
let s2 = s1;
```

Sau dòng:

```rust
let s2 = s1;
```

`s1` không còn là owner nữa.

Ownership đã chuyển sang:

```text
s2
```

---

## Rule 3

> Khi owner ra khỏi scope, value được drop.

Ví dụ:

```rust
fn main() {
    {
        let name = String::from("Alice");

        println!("{name}");
    }

    // name không còn tồn tại
}
```

Khi kết thúc block:

```text
{
    let name = ...
}
       ↓
scope kết thúc
       ↓
name drop
       ↓
String memory được giải phóng
```

---

# 3. Stack và Heap

Để hiểu Ownership, trước tiên phải hiểu hai vùng memory quan trọng:

```text
Stack
Heap
```

---

# 4. Stack là gì?

Stack phù hợp với dữ liệu có:

* kích thước cố định
* biết trước tại compile time
* thời gian sống tương đối đơn giản

Ví dụ:

```rust
let x = 10;
let y = 20;
```

Có thể hình dung:

```text
STACK

┌──────────┐
│ x = 10   │
├──────────┤
│ y = 20   │
└──────────┘
```

---

# 5. Heap là gì?

Heap dùng cho dữ liệu mà kích thước có thể thay đổi hoặc không thuận tiện lưu trực tiếp trên stack.

Ví dụ:

```rust
let s = String::from("hello");
```

Có thể hình dung:

```text
STACK                      HEAP

┌──────────────┐          ┌─────────────┐
│ s            │ ───────► │ h e l l o   │
├──────────────┤          └─────────────┘
│ ptr          │
│ len = 5      │
│ capacity = 5 │
└──────────────┘
```

`String` chứa thông tin quản lý vùng heap.

Đơn giản hóa:

```text
String
├── pointer
├── length
└── capacity
```

---

# 6. Vì sao `String` đặc biệt?

So sánh:

```rust
let x = 10;
```

với:

```rust
let s = String::from("hello");
```

`i32` có kích thước cố định.

```text
i32
→ 4 bytes
```

Còn `String` có thể:

```rust
String::from("hello")
String::from("this is a very long string")
```

Kích thước nội dung thay đổi.

Do đó dữ liệu String nằm trên heap.

---

# 7. Copy đơn giản

Xét:

```rust
fn main() {
    let x = 10;
    let y = x;

    println!("x = {x}");
    println!("y = {y}");
}
```

Output:

```text
x = 10
y = 10
```

Không có vấn đề.

Vì `i32` implement trait:

```text
Copy
```

Rust có thể copy giá trị.

Mô hình:

```text
x = 10
     │
     ├── copy ──► y = 10
```

Hai biến độc lập.

---

# 8. Nhưng `String` thì khác

```rust
fn main() {
    let s1 = String::from("hello");
    let s2 = s1;

    println!("{s2}");
}
```

Điều này hợp lệ.

Nhưng:

```rust
fn main() {
    let s1 = String::from("hello");
    let s2 = s1;

    println!("{s1}");
}
```

Compiler báo lỗi.

Thông thường bạn sẽ thấy kiểu lỗi:

```text
borrow of moved value: `s1`
```

---

# 9. Tại sao Rust không copy String?

Giả sử Rust tự động copy toàn bộ:

```text
s1 ─────┐
        │
        ▼
     "hello"

s2 ─────┘
        │
        ▼
     "hello"
```

Có nghĩa là heap phải được copy.

Nhưng Rust muốn tránh việc copy dữ liệu heap một cách không cần thiết.

Thay vào đó:

```text
s1
 │
 └────► "hello"

s2
 │
 └────► "hello"
```

Nếu cả hai cùng quản lý cùng một vùng heap:

```text
s1 ───┐
      ├──► heap
s2 ───┘
```

thì khi scope kết thúc:

```text
s1 → free(heap)
s2 → free(heap)
```

→ **double free**.

Rust ngăn vấn đề này bằng Move.

---

# 10. Move

Code:

```rust
let s1 = String::from("hello");
let s2 = s1;
```

thực hiện:

```text
s1
 │
 └────► heap "hello"

        MOVE
         ↓

s2
 │
 └────► heap "hello"
```

Sau move:

```text
s1 = invalid
s2 = owner
```

Không phải heap được copy.

**Ownership được chuyển.**

---

# 11. Đây là lý do tên gọi "Move"

```rust
let s1 = String::from("hello");
let s2 = s1;
```

Không nên suy nghĩ:

> s2 nhận một bản sao của s1.

Hãy suy nghĩ:

> **s1 chuyển ownership cho s2.**

Đây là mental model cực kỳ quan trọng.

---

# 12. Test ngay

Tạo project:

```bash
cargo new ownership_lab
cd ownership_lab
```

Thay `src/main.rs`:

```rust
fn main() {
    let s1 = String::from("hello");
    let s2 = s1;

    println!("s2 = {s2}");
}
```

Chạy:

```bash
cargo run
```

Output:

```text
s2 = hello
```

Bây giờ thử:

```rust
fn main() {
    let s1 = String::from("hello");
    let s2 = s1;

    println!("s1 = {s1}");
    println!("s2 = {s2}");
}
```

Chạy:

```bash
cargo check
```

Bạn sẽ thấy compiler từ chối chương trình.

---

# 13. `cargo check` rất quan trọng

Trong quá trình học Rust, hãy sử dụng:

```bash
cargo check
```

thường xuyên.

Nó kiểm tra:

```text
syntax
type
ownership
borrowing
lifetimes
```

mà không cần build executable hoàn chỉnh.

Quy trình học rất hiệu quả:

```text
viết code
   ↓
cargo check
   ↓
đọc compiler error
   ↓
sửa
   ↓
cargo check
```

Rust compiler chính là một "người thầy".

---

# 14. Scope

Ownership gắn chặt với scope.

```rust
fn main() {
    let s = String::from("hello");

    println!("{s}");
}
```

Scope của `s`:

```text
fn main() {
    ┌──────────────────────────┐
    │ let s = ...              │
    │                          │
    │ println!("{s}");         │
    └──────────────────────────┘
}
```

Khi ra khỏi scope:

```text
s
↓
drop
```

---

# 15. Nested scope

```rust
fn main() {
    let outer = String::from("outer");

    {
        let inner = String::from("inner");

        println!("{outer}");
        println!("{inner}");
    }

    println!("{outer}");
}
```

`inner` biến mất khi block kết thúc.

```text
main scope
│
├── outer
│
└── inner scope
    │
    └── inner
         ↓
       drop
```

---

# 16. Drop

Rust tự động gọi cơ chế `drop` khi owner ra khỏi scope.

Bạn không cần:

```text
free()
delete()
release()
```

như trong một số ngôn ngữ khác.

Ví dụ:

```rust
fn main() {
    let s = String::from("hello");

    println!("{s}");
}
```

Cuối scope:

```text
String
  ↓
Drop
  ↓
release heap memory
```

---

# 17. Drop theo thứ tự

Ví dụ:

```rust
fn main() {
    let a = String::from("A");
    let b = String::from("B");
    let c = String::from("C");

    println!("{a}, {b}, {c}");
}
```

Khi scope kết thúc, local variables được drop theo thứ tự thích hợp của Rust; về mặt thực hành bạn nên nhớ rằng Rust tự quản lý lifetime của các local values và bạn không cần tự giải phóng chúng.

---

# 18. Function và Ownership

Đây là nơi Ownership bắt đầu thực sự quan trọng.

```rust
fn take_ownership(s: String) {
    println!("{s}");
}

fn main() {
    let s = String::from("hello");

    take_ownership(s);

    println!("{s}");
}
```

Lỗi.

Tại sao?

```text
main
 │
 │ s owns String
 │
 ▼
take_ownership(s)
 │
 │ ownership moves
 ▼
function owns String
```

Sau khi gọi:

```rust
take_ownership(s);
```

`main` không còn ownership.

---

# 19. Function nhận `i32`

Ngược lại:

```rust
fn use_number(x: i32) {
    println!("{x}");
}

fn main() {
    let x = 10;

    use_number(x);

    println!("{x}");
}
```

Hoàn toàn hợp lệ.

Vì `i32: Copy`.

```text
x = 10
 │
 ├── copy → function
 │
 └── x vẫn dùng được
```

---

# 20. `String` return ownership

Function có thể trả ownership:

```rust
fn create_string() -> String {
    String::from("hello")
}

fn main() {
    let s = create_string();

    println!("{s}");
}
```

Ownership:

```text
create_string
      │
      │ creates String
      ▼
   return
      │
      ▼
      s
```

---

# 21. Move vào function rồi move ra

Ví dụ:

```rust
fn take_and_return(s: String) -> String {
    println!("{s}");

    s
}

fn main() {
    let s1 = String::from("hello");

    let s2 = take_and_return(s1);

    println!("{s2}");
}
```

Ownership:

```text
s1
 │
 ▼
function
 │
 ▼
s2
```

---

# 22. Đây là pattern phổ biến nhưng hơi bất tiện

Ví dụ:

```rust
fn calculate_length(s: String) -> (String, usize) {
    let length = s.len();

    (s, length)
}
```

Sau đó:

```rust
let (s, length) = calculate_length(s);
```

Bạn phải trả ownership lại.

Rust cung cấp **borrowing** để giải quyết vấn đề này.

Đó là bài tiếp theo của Ownership.

---

# 23. `Copy`

Một số kiểu implement `Copy`.

Ví dụ:

```rust
let x = 10;
let y = x;

println!("{x}");
println!("{y}");
```

Một số kiểu thường gặp:

```text
i32
u32
i64
f64
bool
char
```

và các tuple/array nếu tất cả thành phần cũng `Copy`.

---

# 24. `Clone`

Nếu muốn tạo bản sao rõ ràng của dữ liệu heap:

```rust
let s1 = String::from("hello");
let s2 = s1.clone();

println!("{s1}");
println!("{s2}");
```

Output:

```text
hello
hello
```

Ở đây:

```text
s1 ───► heap A
s2 ───► heap B
```

Hai vùng memory khác nhau.

---

# 25. `Clone` khác `Copy`

### Copy

```rust
let x = 10;
let y = x;
```

Compiler tự copy.

### Clone

```rust
let s1 = String::from("hello");
let s2 = s1.clone();
```

Bạn **chủ động yêu cầu tạo bản sao**.

---

# 26. Vì sao Clone không miễn phí?

Ví dụ:

```rust
let huge_string = String::from("...");
let another = huge_string.clone();
```

Có thể phải:

```text
allocate heap
copy bytes
```

Nếu dữ liệu rất lớn, `clone()` có thể tốn chi phí đáng kể.

Do đó:

> Đừng dùng `.clone()` chỉ để làm compiler hết báo lỗi mà không hiểu tại sao.

Đây là một thói quen rất quan trọng khi viết Rust chuyên nghiệp.

---

# 27. Ownership với `Vec`

Ví dụ:

```rust
fn main() {
    let numbers = vec![1, 2, 3];

    let other = numbers;

    println!("{other:?}");
}
```

`numbers` bị move.

---

# 28. Clone Vec

```rust
fn main() {
    let numbers = vec![1, 2, 3];

    let other = numbers.clone();

    println!("numbers = {numbers:?}");
    println!("other = {other:?}");
}
```

Output:

```text
numbers = [1, 2, 3]
other = [1, 2, 3]
```

Có hai vector độc lập.

---

# 29. Ownership và `String`

Hãy nhớ:

```rust
let a = String::from("hello");
let b = a;
```

là:

```text
MOVE
```

Không phải:

```text
COPY
```

Còn:

```rust
let b = a.clone();
```

là:

```text
DEEP COPY
```

---

# 30. Ownership với struct

Ví dụ:

```rust
struct User {
    name: String,
    age: u32,
}

fn main() {
    let user1 = User {
        name: String::from("Alice"),
        age: 20,
    };

    let user2 = user1;

    println!("{}", user2.name);
}
```

`user1` bị move sang `user2`.

---

# 31. Tại sao struct bị move?

Vì struct chứa:

```text
String
```

và `String` không phải `Copy`.

Do đó toàn bộ struct không thể tự động `Copy`.

---

# 32. Struct chỉ chứa Copy types

Ví dụ:

```rust
#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}
```

Bạn có thể:

```rust
fn main() {
    let p1 = Point { x: 10, y: 20 };
    let p2 = p1;

    println!("{p1:?}");
    println!("{p2:?}");
}
```

Nhưng chú ý:

`Debug` không làm struct `Copy`.

Muốn `Copy`:

```rust
#[derive(Debug, Copy, Clone)]
struct Point {
    x: i32,
    y: i32,
}
```

Bây giờ:

```rust
fn main() {
    let p1 = Point { x: 10, y: 20 };
    let p2 = p1;

    println!("{p1:?}");
    println!("{p2:?}");
}
```

hợp lệ.

---

# 33. `Copy` và `Clone` thường đi cùng nhau

Một pattern:

```rust
#[derive(Debug, Copy, Clone)]
struct Point {
    x: i32,
    y: i32,
}
```

Nhưng:

```rust
String
```

không implement `Copy`.

Bạn có thể:

```rust
#[derive(Debug, Clone)]
struct User {
    name: String,
}
```

nhưng không thể tùy tiện:

```rust
#[derive(Debug, Copy, Clone)]
struct User {
    name: String,
}
```

Compiler sẽ từ chối `Copy`.

---

# 34. Tại sao `String` không Copy?

Nếu `String` là `Copy`, câu này:

```rust
let s2 = s1;
```

sẽ phải copy toàn bộ heap data.

Điều đó có thể rất đắt.

Rust chọn:

```text
assignment
   ↓
MOVE
```

để tránh implicit heap copy.

Nếu programmer thực sự muốn copy:

```rust
s1.clone()
```

---

# 35. Ownership và assignment

Hãy đặc biệt chú ý:

```rust
let s1 = String::from("hello");
let s2 = s1;
```

Assignment không đơn thuần là:

```text
copy
```

mà với non-Copy types là:

```text
move
```

Đây là một trong những điểm khác biệt lớn của Rust.

---

# 36. Ownership và function argument

Có thể mô hình hóa:

```rust
fn process(data: String) {
}
```

là:

```text
caller
  │
  │ move
  ▼
function
```

Sau đó caller không còn sử dụng value.

---

# 37. Function return

```rust
fn process(data: String) -> String {
    data
}
```

Ownership:

```text
caller
  │
  ▼
function
  │
  ▼
caller receives ownership
```

Rust không làm mất dữ liệu.

Ownership chỉ di chuyển.

---

# 38. Ownership không phải "memory location"

Đây là một hiểu lầm phổ biến.

Ownership không đơn giản là:

```text
biến nào đang chứa địa chỉ memory?
```

Ownership là **quyền quản lý lifetime của value**.

Ví dụ:

```text
s1 owns String
       ↓ move
s2 owns String
```

Heap data có thể vẫn ở cùng một địa chỉ.

Thứ thay đổi là:

```text
owner
```

---

# 39. Mental model quan trọng nhất hôm nay

Khi gặp:

```rust
let b = a;
```

hãy hỏi:

### `a` có phải Copy không?

Nếu:

```text
YES
```

→ copy.

Nếu:

```text
NO
```

→ move.

Đây là câu hỏi đầu tiên bạn nên tự hỏi.

---

# 40. Ownership Lab

Bây giờ tạo file:

```text
src/main.rs
```

với:

```rust
fn main() {
    let s1 = String::from("Rust");

    println!("Before move:");
    println!("s1 = {s1}");

    let s2 = s1;

    println!();
    println!("After move:");
    println!("s2 = {s2}");
}
```

Chạy:

```bash
cargo run
```

Output:

```text
Before move:
s1 = Rust

After move:
s2 = Rust
```

---

# 41. Thí nghiệm Move

Sửa thành:

```rust
fn main() {
    let s1 = String::from("Rust");
    let s2 = s1;

    println!("s1 = {s1}");
    println!("s2 = {s2}");
}
```

Chạy:

```bash
cargo check
```

Đọc lỗi compiler.

Đừng chỉ sửa ngay.

Hãy tự trả lời:

```text
1. Ai là owner ban đầu?
2. Dòng nào move ownership?
3. Sau move ai là owner?
4. Tại sao s1 không còn dùng được?
```

Đây chính là cách học Rust hiệu quả.

---

# 42. Thí nghiệm Copy

```rust
fn main() {
    let x = 100;
    let y = x;

    println!("x = {x}");
    println!("y = {y}");
}
```

Không lỗi.

Hãy tự hỏi:

```text
Tại sao String move nhưng i32 copy?
```

---

# 43. Thí nghiệm Clone

```rust
fn main() {
    let s1 = String::from("Rust");
    let s2 = s1.clone();

    println!("s1 = {s1}");
    println!("s2 = {s2}");
}
```

Không lỗi.

Mental model:

```text
s1 ───► heap A
s2 ───► heap B
```

---

# 44. Thí nghiệm Function

```rust
fn consume(value: String) {
    println!("value = {value}");
}

fn main() {
    let text = String::from("hello");

    consume(text);

    println!("{text}");
}
```

Compiler sẽ báo lỗi.

Hãy vẽ:

```text
main
 │
 └── text
       │
       │ move
       ▼
    consume()
```

---

# 45. Thí nghiệm Return

```rust
fn consume(value: String) -> String {
    println!("value = {value}");

    value
}

fn main() {
    let text = String::from("hello");

    let text = consume(text);

    println!("{text}");
}
```

Điều này hợp lệ.

Ownership:

```text
text
 ↓
consume
 ↓
text mới
```

---

# 46. Bài tập 1 — Move

Dự đoán đoạn code nào compile:

### A

```rust
let x = 10;
let y = x;

println!("{x}");
```

### B

```rust
let x = String::from("hello");
let y = x;

println!("{x}");
```

### C

```rust
let x = String::from("hello");
let y = x.clone();

println!("{x}");
```

Hãy tự trả lời trước khi chạy.

---

# 47. Bài tập 2 — Function

Cho:

```rust
fn print_text(text: String) {
    println!("{text}");
}
```

Viết `main` sao cho:

```text
text
 ↓
function
 ↓
sau function vẫn sử dụng được text
```

Có ít nhất hai cách để giải quyết.

Một cách sẽ là:

```text
clone
```

Cách còn lại sẽ dẫn chúng ta tới:

```text
borrowing
```

ở buổi tiếp theo.

---

# 48. Bài tập 3 — Vec

Cho:

```rust
let numbers = vec![1, 2, 3];
```

Viết:

```rust
let other = numbers;
```

Sau đó thử sử dụng cả:

```rust
numbers
other
```

Quan sát compiler.

Sau đó sửa bằng:

```rust
clone()
```

và giải thích sự khác nhau.

---

# 49. Bài tập 4 — Struct

Tạo:

```rust
struct Book {
    title: String,
    pages: u32,
}
```

Sau đó:

```rust
let book1 = Book {
    title: String::from("Rust"),
    pages: 300,
};

let book2 = book1;
```

Thử sử dụng:

```rust
book1
book2
```

Xác định chính xác tại sao compiler báo lỗi.

---

# 50. Bài tập 5 — Copy struct

Tạo:

```rust
#[derive(Debug, Copy, Clone)]
struct Point {
    x: i32,
    y: i32,
}
```

Sau đó:

```rust
let p1 = Point { x: 10, y: 20 };
let p2 = p1;
```

Sử dụng cả:

```rust
p1
p2
```

và giải thích tại sao hoạt động.

---

# 51. Bài tập 6 — Ownership Transfer

Viết:

```rust
fn create_message() -> String
```

Function phải tạo:

```text
"Hello Rust"
```

và trả ownership về `main`.

---

# 52. Challenge — Story Ownership

Dùng project truyện của bạn:

```rust
#[derive(Debug)]
struct Story {
    title: String,
    chapters: u32,
}
```

Viết:

```rust
fn process_story(story: Story) {
    println!("{:?}", story);
}
```

Trong `main`:

```rust
let story = Story {
    title: String::from("Rust Story"),
    chapters: 100,
};

process_story(story);
```

Sau đó thử:

```rust
println!("{}", story.title);
```

Compiler sẽ từ chối.

Hãy giải thích chính xác:

```text
1. story ban đầu owner là ai?
2. process_story nhận gì?
3. ownership chuyển ở đâu?
4. ai trở thành owner?
5. tại sao main không dùng story nữa?
6. khi function kết thúc, chuyện gì xảy ra?
```

---

# 53. Challenge nâng cao — Story Pipeline

Tạo:

```rust
fn normalize_story(story: Story) -> Story
```

Function nhận ownership.

Sau đó trả ownership.

Pipeline:

```text
main
 │
 ▼
normalize_story
 │
 ▼
validate_story
 │
 ▼
save_story
```

Tất cả đều nhận:

```rust
Story
```

và trả:

```rust
Story
```

Mục tiêu là quan sát ownership di chuyển qua pipeline.

Ví dụ:

```rust
fn normalize_story(mut story: Story) -> Story {
    story.title = story.title.trim().to_string();
    story
}

fn validate_story(story: Story) -> Story {
    story
}

fn save_story(story: Story) {
    println!("Saving: {}", story.title);
}

fn main() {
    let story = Story {
        title: String::from("  Rust Story  "),
        chapters: 100,
    };

    let story = normalize_story(story);
    let story = validate_story(story);

    save_story(story);
}
```

Mental model:

```text
Story
  │
  ▼
normalize
  │
  ▼
validate
  │
  ▼
save
  │
  ▼
drop
```

Đây là pattern rất đáng chú ý khi sau này bạn xây:

```text
Crawler
Parser
Repository
Service
UseCase
```

---

# 54. Những điều chưa học hôm nay

Bạn có thể thấy việc truyền:

```rust
String
```

vào function khá "cứng".

Ví dụ:

```rust
fn calculate_length(s: String) -> usize
```

sẽ consume `String`.

Ta muốn:

```text
function chỉ đọc dữ liệu
        ↓
không lấy ownership
        ↓
caller vẫn dùng được
```

Rust giải quyết bằng:

# Borrowing & References

Đây chính là chủ đề **Buổi 16**.

Chúng ta sẽ học:

```text
&
&mut
reference
dereference
borrowing
shared reference
mutable reference
aliasing
mutable aliasing
borrow checker
ownership + borrowing
function parameters
return references
```

và đặc biệt là hai quy tắc cực kỳ quan trọng:

```text
Có thể có nhiều immutable references
HOẶC
một mutable reference

nhưng không thể đồng thời cả hai.
```

Đây là nơi **Borrow Checker** bắt đầu thực sự trở nên rõ ràng.

---

# 55. Checklist Buổi 15

Trước khi chuyển sang Buổi 16, bạn nên tự giải thích được:

* [ ] Ownership là gì?
* [ ] Owner là gì?
* [ ] Scope là gì?
* [ ] Khi nào value bị drop?
* [ ] Stack và Heap khác nhau thế nào?
* [ ] `String` tại sao liên quan tới Heap?
* [ ] Move là gì?
* [ ] Tại sao `String` bị move?
* [ ] Tại sao `i32` có thể Copy?
* [ ] `Copy` khác `Clone` thế nào?
* [ ] Function có thể lấy ownership như thế nào?
* [ ] Function trả ownership như thế nào?
* [ ] Struct chứa `String` bị move ra sao?
* [ ] Vì sao không nên lạm dụng `.clone()`?

Nếu bạn hiểu được toàn bộ checklist này, bạn đã nắm **phần lõi của Ownership**.

**Buổi 16: References & Borrowing — `&`, `&mut` và Borrow Checker.** Đây sẽ là bước tiếp theo để biến Ownership từ lý thuyết thành kỹ năng viết Rust thực tế.
