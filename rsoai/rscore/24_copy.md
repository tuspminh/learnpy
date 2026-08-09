# Rust — Phần III: Ownership

# Buổi 24 — `Copy`

Hôm nay chúng ta học **`Copy`** — một trait rất quan trọng để hiểu tại sao:

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

lại lỗi.

Điểm cốt lõi của bài:

> **`Copy` cho phép một value được sao chép ngầm khi assignment, argument passing hoặc return value thay vì bị Move.**

---

# 1. Bài toán

Xét hai đoạn code.

### `i32`

```rust
fn main() {
    let a = 10;
    let b = a;

    println!("a = {a}");
    println!("b = {b}");
}
```

Compile được.

---

### `String`

```rust
fn main() {
    let a = String::from("Rust");
    let b = a;

    println!("a = {a}");
    println!("b = {b}");
}
```

Compile lỗi.

Tại sao?

Đây chính là vấn đề mà `Copy` giải thích.

---

# 2. `Copy` là gì?

`Copy` là một trait đặc biệt:

```rust
pub trait Copy: Clone {}
```

Một type implement `Copy` có nghĩa:

> Khi value được gán, truyền vào function hoặc trả về, Rust có thể sao chép value một cách ngầm định thay vì chuyển ownership.

Ví dụ:

```rust
let a = 10;
let b = a;
```

Conceptually:

```text
a = 10

      COPY
       ↓

b = 10
```

Cả `a` và `b` đều hợp lệ.

---

# 3. `Copy` khác `Clone`

Đây là điểm quan trọng nhất của buổi học.

### Clone

Bạn phải gọi rõ:

```rust
let b = a.clone();
```

### Copy

Rust tự động copy:

```rust
let b = a;
```

Không cần:

```rust
a.clone()
```

---

# 4. So sánh trực tiếp

```rust
let a = 10;
let b = a;
```

Với `i32`, đây là:

```text
COPY
```

Trong khi:

```rust
let a = String::from("Rust");
let b = a;
```

là:

```text
MOVE
```

---

# 5. Mental Model

Hãy tưởng tượng:

```text
i32
┌──────────┐
│    10    │
└──────────┘
```

Copy rất đơn giản:

```text
       ┌── a = 10
value ─┤
       └── b = 10
```

Không có ownership resource phức tạp.

---

# 6. `String` thì khác

`String` có thể hình dung:

```text
STACK

a
┌───────────────┐
│ ptr           │──────┐
│ len           │      │
│ capacity      │      │
└───────────────┘      ▼
                     HEAP
                    "Rust"
```

Nếu Rust tự động copy `String` bằng phép copy bit đơn giản:

```text
a ────────┐
          ├──────> "Rust"
b ────────┘
```

thì hai `String` sẽ cùng quản lý một allocation.

Đây là điều Rust không cho phép.

Vì vậy:

```rust
let b = a;
```

với `String` là **Move**.

---

# 7. Tại sao `String` không phải `Copy`?

Vì `String` sở hữu heap memory.

Nếu `String` là `Copy`, việc:

```rust
let b = a;
```

sẽ phải tạo ra một bản copy hợp lệ.

Nhưng `Copy` là **implicit bitwise copy**, không phải deep clone.

Rust không muốn:

```text
a ──┐
    ├──> same heap allocation
b ──┘
```

Do đó:

```text
String
❌ Copy
✅ Clone
```

---

# 8. `Copy` là implicit

Ví dụ:

```rust
fn main() {
    let x = 42;
    let y = x;

    println!("{x}");
    println!("{y}");
}
```

Bạn không viết:

```rust
let y = x.clone();
```

Rust tự thực hiện copy semantics.

---

# 9. Function arguments

`Copy` cũng hoạt động khi truyền argument.

```rust
fn print_number(n: i32) {
    println!("n = {n}");
}

fn main() {
    let x = 42;

    print_number(x);

    println!("x = {x}");
}
```

Compile được.

Vì:

```text
x
 │
 ├── copy → function
 │
 └── vẫn valid
```

---

# 10. Với `String`

```rust
fn print_text(text: String) {
    println!("{text}");
}

fn main() {
    let text = String::from("Rust");

    print_text(text);

    println!("{text}");
}
```

Lỗi.

Vì:

```text
text
 │
 │ MOVE
 ▼
print_text()
```

Sau khi function nhận ownership:

```text
text → invalid
```

---

# 11. `Copy` hoạt động khi assignment

```rust
let a = 10;
let b = a;
let c = a;
let d = a;
```

Tất cả đều hợp lệ.

Conceptually:

```text
       ┌── b = 10
       │
a = 10 ├── c = 10
       │
       └── d = 10
```

---

# 12. `Copy` hoạt động với function

```rust
fn foo(value: i32) {
    println!("{value}");
}

fn main() {
    let x = 100;

    foo(x);
    foo(x);
    foo(x);

    println!("{x}");
}
```

Tất cả đều hợp lệ.

Mỗi lần truyền:

```text
x
│
├── copy → foo
├── copy → foo
└── copy → foo
```

---

# 13. `Copy` hoạt động với return

Ví dụ:

```rust
fn get_number() -> i32 {
    100
}

fn main() {
    let x = get_number();

    println!("{x}");
}
```

Với các type `Copy`, việc return/assignment không tạo ra ownership complication giống các type resource-owning.

---

# 14. Những type cơ bản thường là `Copy`

Các scalar types như:

```text
i32
i64
u32
u64
usize
isize
f32
f64
bool
char
```

đều là `Copy`.

Ví dụ:

```rust
fn main() {
    let a: i32 = 10;
    let b = a;

    let x: bool = true;
    let y = x;

    let c: char = 'R';
    let d = c;

    println!("{a} {b}");
    println!("{x} {y}");
    println!("{c} {d}");
}
```

---

# 15. Tuple có thể là `Copy`

Điều kiện:

> Một tuple là `Copy` nếu tất cả các phần tử của nó đều `Copy`.

Ví dụ:

```rust
fn main() {
    let a = (10, 20, 30);

    let b = a;

    println!("{a:?}");
    println!("{b:?}");
}
```

Compile được.

Vì:

```text
i32 → Copy
i32 → Copy
i32 → Copy
```

nên:

```text
(i32, i32, i32) → Copy
```

---

# 16. Tuple với `String`

```rust
fn main() {
    let a = (10, String::from("Rust"));

    let b = a;

    println!("{a:?}");
}
```

Lỗi.

Vì:

```text
i32    → Copy
String → NOT Copy
```

Do đó:

```text
(i32, String)
→ NOT Copy
```

---

# 17. Array cũng có quy tắc tương tự

Nếu element type là `Copy`, array có thể là `Copy`.

```rust
fn main() {
    let a = [1, 2, 3];

    let b = a;

    println!("{a:?}");
    println!("{b:?}");
}
```

`[i32; 3]` là `Copy`.

---

# 18. Array chứa String

```rust
fn main() {
    let a = [
        String::from("Rust"),
        String::from("Python"),
    ];

    let b = a;

    println!("{a:?}");
}
```

Không được.

Vì:

```text
String → !Copy
```

---

# 19. Reference có thể là `Copy`

Đây là điểm rất quan trọng.

Ví dụ:

```rust
fn main() {
    let value = String::from("Rust");

    let a = &value;
    let b = a;

    println!("{a}");
    println!("{b}");
}
```

Compile được.

Tại sao?

`a` không sở hữu String.

Nó chỉ là reference.

Conceptually:

```text
value
  │
  ▼
"Rust"

a ───────┐
         │
b ───────┘
         │
         ▼
      value
```

Copy reference không copy String.

---

# 20. Đây là khác biệt cực kỳ quan trọng

```rust
let a = String::from("Rust");
let b = a;
```

→ Move.

Nhưng:

```rust
let a = String::from("Rust");

let r1 = &a;
let r2 = r1;
```

→ Copy reference.

Dữ liệu String vẫn chỉ có một owner:

```text
a
```

---

# 21. `&T` thường là `Copy`

Reference:

```rust
&T
```

có thể được copy.

Ví dụ:

```rust
fn main() {
    let x = 10;

    let a = &x;
    let b = a;

    println!("{x}");
    println!("{a}");
    println!("{b}");
}
```

---

# 22. `&mut T` thì sao?

Đây là nuance quan trọng.

Mutable reference:

```rust
&mut T
```

**không implement `Copy`.**

Ví dụ:

```rust
fn main() {
    let mut x = 10;

    let a = &mut x;
    let b = a;

    println!("{b}");
}
```

Move xảy ra đối với mutable reference.

Tại sao?

Vì nếu mutable references có thể tự do Copy:

```text
&mut x
&mut x
&mut x
```

thì có thể tồn tại nhiều mutable access đồng thời.

Điều đó phá vỡ quy tắc:

> Tại một thời điểm, chỉ có một mutable borrow.

---

# 23. Đây là lý do `&mut T` không Copy

Rust muốn đảm bảo:

```text
&mut T
```

có tính độc quyền.

Conceptually:

```text
x
│
└── &mut x
```

Không thể:

```text
x
├── &mut x
├── &mut x
└── &mut x
```

đồng thời.

Đây là nền tảng của **Borrow Checker**.

---

# 24. `Copy` và `Clone` có quan hệ

Trait declaration:

```rust
pub trait Copy: Clone {}
```

Điều này có nghĩa:

```text
Copy
  │
  └── requires Clone
```

Nếu type `Copy`, nó cũng phải `Clone`.

Ví dụ:

```rust
let x = 10;
let y = x.clone();
```

vẫn được.

Nhưng với type `Copy`:

```rust
let y = x;
```

thường đủ và idiomatic hơn.

---

# 25. `Copy` không phải `Clone`

Đừng hiểu:

```text
Copy = Clone
```

Không đúng.

### Copy

```text
implicit
```

### Clone

```text
explicit
```

Ví dụ:

```rust
let a = 10;
let b = a;
```

→ Copy.

Trong khi:

```rust
let b = a.clone();
```

→ Explicit Clone.

---

# 26. `Copy` không gọi `clone()` của bạn

Khi:

```rust
let b = a;
```

với type `Copy`, Rust áp dụng Copy semantics.

Nó không có nghĩa:

```rust
let b = a.clone();
```

theo nghĩa source-level.

Đây là một cơ chế ngôn ngữ riêng.

---

# 27. Derive Copy

Bạn có thể tự tạo type `Copy`.

Ví dụ:

```rust
#[derive(Debug, Copy, Clone)]
struct Point {
    x: i32,
    y: i32,
}
```

Sau đó:

```rust
fn main() {
    let p1 = Point { x: 10, y: 20 };

    let p2 = p1;

    println!("{p1:?}");
    println!("{p2:?}");
}
```

Compile được.

---

# 28. Tại sao phải derive cả `Clone`?

Vì:

```rust
Copy: Clone
```

nên một type `Copy` phải implement `Clone`.

Do đó thường viết:

```rust
#[derive(Copy, Clone)]
```

hoặc:

```rust
#[derive(Debug, Copy, Clone)]
```

---

# 29. Điều kiện để struct là `Copy`

Ví dụ:

```rust
#[derive(Copy, Clone)]
struct Point {
    x: i32,
    y: i32,
}
```

Được vì:

```text
x: i32 → Copy
y: i32 → Copy
```

Nhưng:

```rust
struct User {
    name: String,
}
```

không thể:

```rust
#[derive(Copy, Clone)]
struct User {
    name: String,
}
```

vì:

```text
String → !Copy
```

Compiler sẽ báo lỗi.

---

# 30. `Copy` là transitive

Đây là nguyên tắc:

```text
struct
  │
  ├── field A
  ├── field B
  └── field C
```

Muốn struct `Copy`:

```text
A → Copy
B → Copy
C → Copy
```

tất cả phải `Copy`.

---

# 31. Ví dụ

```rust
#[derive(Copy, Clone)]
struct Config {
    timeout: u64,
    retries: u32,
}
```

Hợp lệ.

Nhưng:

```rust
struct Config {
    timeout: u64,
    name: String,
}
```

Không thể `Copy`.

---

# 32. Có thể có `Copy` nhưng không `Clone` không?

Không.

Vì:

```rust
Copy: Clone
```

nên:

```text
Copy
 ↓
Clone
```

Nhưng:

```text
Clone
```

không đồng nghĩa với:

```text
Copy
```

Ví dụ:

```text
String
```

là:

```text
Clone
```

nhưng không:

```text
Copy
```

---

# 33. Bảng quan hệ

| Type            | Copy |           Clone |
| --------------- | ---: | --------------: |
| `i32`           |    ✅ |               ✅ |
| `bool`          |    ✅ |               ✅ |
| `char`          |    ✅ |               ✅ |
| `String`        |    ❌ |               ✅ |
| `Vec<T>`        |    ❌ |  nếu `T: Clone` |
| `&T`            |    ✅ |               ✅ |
| `&mut T`        |    ❌ |               ❌ |
| `(i32, i32)`    |    ✅ |               ✅ |
| `(i32, String)` |    ❌ | nếu field Clone |
| `Rc<T>`         |    ❌ |               ✅ |
| `Arc<T>`        |    ❌ |               ✅ |

---

# 34. `Copy` và ownership

Một điều quan trọng:

> `Copy` không loại bỏ Ownership.

Nó chỉ thay đổi hành vi khi value được sao chép.

Ví dụ:

```rust
let x = 10;
let y = x;
```

vẫn có ownership.

Nhưng `i32` có semantics cho phép copy.

---

# 35. Copy không phải "pass by reference"

Đây là hiểu nhầm phổ biến.

Khi:

```rust
fn foo(x: i32) {
}
```

và:

```rust
foo(value);
```

`value` được **copy**, không phải borrow.

Nếu:

```rust
let value = 100;
foo(value);

println!("{value}");
```

thì `value` vẫn usable vì nó là `Copy`.

---

# 36. So sánh

### Copy

```rust
fn foo(x: i32) {}

let a = 10;
foo(a);

println!("{a}");
```

### Borrow

```rust
fn foo(x: &i32) {}

let a = 10;
foo(&a);

println!("{a}");
```

Cả hai đều giữ `a`, nhưng cơ chế khác nhau.

---

# 37. Copy với `Option`

Nếu `T: Copy`, thì:

```rust
Option<T>
```

cũng có thể `Copy`.

Ví dụ:

```rust
fn main() {
    let a = Some(10);

    let b = a;

    println!("{a:?}");
    println!("{b:?}");
}
```

Compile được.

---

# 38. `Option<String>`

```rust
fn main() {
    let a = Some(String::from("Rust"));

    let b = a;

    println!("{a:?}");
}
```

Lỗi.

Bởi vì:

```text
String → !Copy
```

nên:

```text
Option<String> → !Copy
```

---

# 39. `Result`

Tương tự:

```rust
Result<T, E>
```

có thể `Copy` nếu cả:

```text
T → Copy
E → Copy
```

Ví dụ:

```rust
fn main() {
    let result: Result<i32, i32> = Ok(10);

    let copy = result;

    println!("{result:?}");
    println!("{copy:?}");
}
```

---

# 40. Copy và Enum

Enum cũng có thể `Copy`.

Ví dụ:

```rust
#[derive(Debug, Copy, Clone)]
enum Status {
    Pending,
    Running,
    Done,
}
```

Sau đó:

```rust
fn main() {
    let a = Status::Running;
    let b = a;

    println!("{a:?}");
    println!("{b:?}");
}
```

Compile được.

---

# 41. Enum có String thì sao?

```rust
enum Message {
    Text(String),
    Quit,
}
```

Không thể:

```rust
#[derive(Copy, Clone)]
```

vì:

```text
Text(String)
      ↑
    !Copy
```

Chỉ cần **một variant chứa field không Copy** là toàn enum không thể Copy.

---

# 42. Khi nào nên thiết kế type `Copy`?

`Copy` thường phù hợp với các value nhỏ, đơn giản, value-like.

Ví dụ:

```text
Point
Color
Size
Position
Coordinates
IDs
Flags
Dimensions
```

Ví dụ:

```rust
#[derive(Debug, Copy, Clone)]
struct Point {
    x: i32,
    y: i32,
}
```

---

# 43. `Copy` rất hợp với ID

Ví dụ:

```rust
#[derive(Debug, Copy, Clone)]
struct StoryId(u64);
```

Sau đó:

```rust
fn find_story(id: StoryId) {
    println!("{id:?}");
}

fn main() {
    let id = StoryId(100);

    find_story(id);

    println!("{id:?}");
}
```

Rất tiện.

`StoryId` là một value nhỏ.

---

# 44. Newtype + Copy

Đây là pattern Rust rất hay.

Thay vì:

```rust
fn get_story(id: u64)
```

có thể:

```rust
#[derive(Debug, Copy, Clone)]
struct StoryId(u64);
```

và:

```rust
fn get_story(id: StoryId) {
    println!("{id:?}");
}
```

Bạn vừa có:

```text
type safety
+
Copy semantics
```

---

# 45. Không nên biến mọi struct thành Copy

Ví dụ:

```rust
struct Story {
    title: String,
    content: String,
}
```

Không nên cố làm:

```text
Copy
```

vì semantics của object sở hữu dữ liệu lớn không phù hợp.

Thay vào đó:

```text
Story
 ├── Move
 ├── Borrow
 └── Clone khi thực sự cần
```

---

# 46. Copy và API design

Nếu API:

```rust
fn process(id: StoryId)
```

và:

```rust
StoryId: Copy
```

thì caller có thể:

```rust
process(id);
process(id);
process(id);
```

rất tự nhiên.

Nếu:

```rust
StoryId
```

là non-Copy thì API sẽ phức tạp hơn không cần thiết nếu ID chỉ là một scalar value.

---

# 47. Một ví dụ hoàn chỉnh

Hãy tạo project:

```bash
cargo new copy_demo
cd copy_demo
```

Thay `src/main.rs` bằng:

```rust
#[derive(Debug, Copy, Clone)]
struct Point {
    x: i32,
    y: i32,
}

#[derive(Debug, Copy, Clone)]
struct StoryId(u64);

fn print_point(point: Point) {
    println!("point = {point:?}");
}

fn print_story_id(id: StoryId) {
    println!("story id = {id:?}");
}

fn main() {
    let point = Point { x: 10, y: 20 };

    let copied_point = point;

    println!("point        = {point:?}");
    println!("copied_point = {copied_point:?}");

    print_point(point);
    print_point(point);

    let id = StoryId(100);

    print_story_id(id);
    print_story_id(id);

    println!("id = {id:?}");
}
```

Chạy:

```bash
cargo run
```

Bạn sẽ thấy tất cả đều hợp lệ.

---

# 48. Bài thực hành quan trọng

Hãy thử sửa:

```rust
#[derive(Debug, Copy, Clone)]
struct Point {
    x: i32,
    y: i32,
}
```

thành:

```rust
#[derive(Debug, Copy, Clone)]
struct Point {
    x: i32,
    name: String,
}
```

Compiler sẽ báo lỗi.

Hãy đọc error message.

Rust sẽ nói đại ý:

```text
the trait `Copy` cannot be implemented for this type
```

và chỉ ra:

```text
String
```

là nguyên nhân.

---

# 49. Thí nghiệm tiếp theo

Tạo:

```rust
#[derive(Debug, Clone)]
struct User {
    name: String,
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

Điều này hợp lệ.

Nhưng:

```rust
#[derive(Debug, Copy, Clone)]
```

thì không.

Từ đây bạn có thể thấy rõ:

```text
Clone
  ↑
String có

Copy
  ↑
String không có
```

---

# 50. Một lỗi tư duy rất phổ biến

Đừng nghĩ:

> "Type nhỏ thì tự động Copy."

Không chính xác.

Ví dụ một struct có thể nhỏ nhưng chứa một field không `Copy`.

Điều quyết định là **semantics của type và tất cả fields**, không đơn thuần là kích thước.

---

# 51. `Copy` không phải optimization tùy ý

Bạn không nên nghĩ:

> "Copy nhanh nên tôi derive Copy cho mọi thứ."

`Copy` là một phần **semantic contract** của type.

Nó nói rằng:

> Việc tạo một bản sao ngầm của value này là hợp lệ và không gây ra ownership/resource semantics nguy hiểm.

Do đó `Copy` nên được dùng cho các type có semantics giống value.

---

# 52. Quy tắc thiết kế thực tế

Hãy ưu tiên `Copy` cho:

```text
✔ integer IDs
✔ coordinates
✔ dimensions
✔ enums đơn giản
✔ flags
✔ small value objects
```

Cẩn thận với:

```text
❌ String
❌ Vec
❌ HashMap
❌ File handle
❌ Socket
❌ Database connection
❌ Resource-owning object
```

Những loại này thường không nên `Copy`.

---

# 53. Copy vs Clone — cách nhớ

Hãy nhớ câu này:

> **Copy = implicit. Clone = explicit.**

Ví dụ:

```rust
let b = a;
```

Nếu `a` là `Copy`:

```text
COPY
```

Nếu `a` không phải `Copy`:

```text
MOVE
```

Còn:

```rust
let b = a.clone();
```

là:

```text
EXPLICIT CLONE
```

---

# 54. Sơ đồ Ownership hiện tại

Sau ba buổi:

```text
                 Ownership
                     │
          ┌──────────┼──────────┐
          │          │          │
        Move       Copy       Clone
          │          │          │
     chuyển owner   implicit   explicit
          │          │          │
       String       i32       String
```

Và sắp tới:

```text
Ownership
    │
    ├── Move
    ├── Copy
    ├── Clone
    ├── Borrow
    └── Mutable Borrow
```

---

# 55. Mini Project — Geometry

Hãy xây dựng:

```rust
#[derive(Debug, Copy, Clone)]
struct Point {
    x: f64,
    y: f64,
}

#[derive(Debug, Copy, Clone)]
struct Size {
    width: f64,
    height: f64,
}

#[derive(Debug, Copy, Clone)]
struct Rect {
    position: Point,
    size: Size,
}
```

Viết:

```rust
fn move_rect(rect: Rect, dx: f64, dy: f64) -> Rect
```

và:

```rust
fn print_rect(rect: Rect)
```

Test:

```rust
fn main() {
    let rect = Rect {
        position: Point { x: 10.0, y: 20.0 },
        size: Size {
            width: 100.0,
            height: 50.0,
        },
    };

    let moved = move_rect(rect, 5.0, 10.0);

    print_rect(rect);
    print_rect(moved);
}
```

Điều thú vị là `rect` vẫn dùng được sau:

```rust
move_rect(rect, ...)
```

vì `Rect` là `Copy`.

---

# 56. Bài tập Ownership

### Bài 1

Đoán code nào compile:

```rust
let a = 10;
let b = a;
println!("{a}");
```

```rust
let a = String::from("Rust");
let b = a;
println!("{a}");
```

```rust
let a = true;
let b = a;
println!("{a}");
```

```rust
let a = vec![1, 2, 3];
let b = a;
println!("{a:?}");
```

---

### Bài 2

Giải thích:

```rust
let a = (10, true, 'R');
let b = a;

println!("{a:?}");
```

Tại sao compile?

---

### Bài 3

Giải thích:

```rust
let a = (10, String::from("Rust"));
let b = a;

println!("{a:?}");
```

Tại sao không compile?

---

### Bài 4

Giải thích:

```rust
let text = String::from("Rust");

let a = &text;
let b = a;

println!("{a}");
println!("{b}");
```

Tại sao `a` vẫn dùng được?

---

### Bài 5

Tạo:

```rust
#[derive(Debug, Copy, Clone)]
struct UserId(u64);
```

Viết function:

```rust
fn load_user(id: UserId)
```

và chứng minh rằng cùng một `UserId` có thể truyền nhiều lần.

---

# 57. Thử thách

Hãy tự viết:

```rust
#[derive(Debug, Copy, Clone)]
struct Point {
    x: i32,
    y: i32,
}

fn distance_squared(a: Point, b: Point) -> i32 {
    let dx = a.x - b.x;
    let dy = a.y - b.y;

    dx * dx + dy * dy
}
```

Test:

```rust
fn main() {
    let p1 = Point { x: 0, y: 0 };
    let p2 = Point { x: 3, y: 4 };

    let d1 = distance_squared(p1, p2);
    let d2 = distance_squared(p1, p2);

    println!("d1 = {d1}");
    println!("d2 = {d2}");

    println!("p1 = {p1:?}");
    println!("p2 = {p2:?}");
}
```

Kết quả:

```text
d1 = 25
d2 = 25
p1 = Point { x: 0, y: 0 }
p2 = Point { x: 3, y: 4 }
```

Đây là một ví dụ rất điển hình cho việc sử dụng `Copy` đúng cách.

---

# 58. Tổng kết Buổi 24

Bạn cần ghi nhớ 8 điểm:

```text
1. Copy là trait đặc biệt của Rust.

2. Copy xảy ra implicit.

3. Clone phải gọi explicit bằng clone().

4. Type Copy cũng phải Clone.

5. String là Clone nhưng không Copy.

6. i32 là Copy và Clone.

7. Struct chỉ Copy nếu tất cả field của nó Copy.

8. Copy phù hợp với các value nhỏ, đơn giản, không sở hữu
   resource phức tạp.
```

Mental model:

```text
let b = a;

        ┌── Copy → nếu a: Copy
        │
        └── Move → nếu a: !Copy
```

Trong khi:

```text
let b = a.clone();

        ↓

    Explicit Clone
```

Và:

```text
foo(&a);

        ↓

      Borrow
```

---

## Roadmap tiếp theo

```text
✓ Buổi 21 — Ownership
✓ Buổi 22 — Move
✓ Buổi 23 — Clone
✓ Buổi 24 — Copy       ← hôm nay
→ Buổi 25 — Borrow
  Buổi 26 — Mutable Borrow
  Buổi 27 — Slice
  Buổi 28 — String
  Buổi 29 — String vs &str
  Buổi 30 — Ownership Deep Dive
```

**Buổi 25 — Borrow** sẽ là một bước cực kỳ quan trọng: chúng ta sẽ đi sâu vào `&T`, `&mut T`, reference, dereference `*`, quy tắc borrowing, aliasing, lifetime cơ bản và cách thiết kế function để **không cần `clone()` một cách vô ích**.
