# Rust — Phần III: Ownership

# Buổi 21 — Ownership

Đây là **một trong những buổi quan trọng nhất của Rust**.

Nếu Python có:

```text
object → reference → garbage collector
```

thì Rust có:

```text
value
  ↓
owner
  ↓
ownership
  ↓
move / borrow
  ↓
compiler kiểm tra
  ↓
memory safety
```

Muốn học Rust sâu, bạn cần hiểu Ownership **ở mức mô hình bộ nhớ**, không chỉ nhớ vài quy tắc cú pháp.

---

# 1. Ownership là gì?

**Ownership = quyền sở hữu một giá trị trong bộ nhớ.**

Trong Rust, mỗi value có một **owner**.

Ví dụ:

```rust
fn main() {
    let name = String::from("Rust");
}
```

Ta có:

```text
name
 │
 │ owns
 ▼
String("Rust")
```

`name` là owner của `String`.

Khi `name` ra khỏi scope:

```rust
fn main() {
    let name = String::from("Rust");

} // name hết scope
```

Rust sẽ tự động giải phóng `String`.

Không cần:

```text
free()
delete()
gc.collect()
```

---

# 2. Tại sao Rust cần Ownership?

Rust muốn đạt được:

```text
Memory safety
+
No garbage collector
+
High performance
```

Đây là bài toán khó.

C/C++ cho phép programmer quản lý memory trực tiếp, nhưng dễ xảy ra:

```text
memory leak
double free
use-after-free
dangling pointer
```

Rust đưa ra một hệ thống luật để compiler kiểm tra những vấn đề này **trước khi chương trình chạy**.

Trung tâm của hệ thống đó là:

```text
Ownership
Borrowing
Lifetimes
```

---

# 3. Ba quy tắc Ownership

Rust có ba nguyên tắc nền tảng.

## Rule 1

> Mỗi value trong Rust có một owner.

Ví dụ:

```rust
let name = String::from("Rust");
```

```text
name ──────owns──────> String
```

---

## Rule 2

> Một thời điểm chỉ có một owner.

Ví dụ:

```rust
let name = String::from("Rust");
```

`name` sở hữu value.

Khi ownership chuyển sang biến khác:

```rust
let other = name;
```

thì:

```text
name
  │
  └── ownership ──→ other
```

`name` không còn owner nữa.

Đây chính là **Move**.

Buổi 22 chúng ta sẽ đào sâu.

---

## Rule 3

> Khi owner ra khỏi scope, value được drop.

Ví dụ:

```rust
fn main() {
    {
        let name = String::from("Rust");

        println!("{name}");
    }

    // name không còn tồn tại
}
```

Scope:

```text
main
│
├── inner scope
│   │
│   └── name
│
└── name dropped
```

---

# 4. Stack và Heap

Để hiểu Ownership, phải hiểu sơ bộ:

```text
Stack
Heap
```

---

# 5. Stack

Stack chứa những dữ liệu có kích thước cố định.

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

Các kiểu như:

```text
i32
u64
bool
char
f64
```

thường có kích thước cố định.

---

# 6. Heap

`String` khác.

```rust
let name = String::from("Rust");
```

Có thể hình dung:

```text
STACK                    HEAP

name                     R u s t
┌───────────────┐        ┌─────────┐
│ ptr ──────────┼───────>│ Rust    │
│ len = 4       │        └─────────┘
│ capacity = 4  │
└───────────────┘
```

`name` chứa thông tin quản lý buffer.

Dữ liệu `"Rust"` nằm trên heap.

---

# 7. Tại sao String nằm trên Heap?

Vì `String` có thể thay đổi kích thước:

```rust
let mut name = String::from("Rust");

name.push_str(" Programming");
```

Ban đầu:

```text
Rust
```

Sau đó:

```text
Rust Programming
```

Kích thước runtime không cố định.

Do đó cần heap allocation.

---

# 8. Ownership của String

```rust
fn main() {
    let name = String::from("Rust");

    println!("{name}");
}
```

Mô hình:

```text
STACK                     HEAP

name
┌─────────────────┐
│ ptr             │───────> "Rust"
│ len             │
│ capacity        │
└─────────────────┘
```

`name` sở hữu allocation trên heap.

---

# 9. Khi scope kết thúc

```rust
fn main() {
    let name = String::from("Rust");

    println!("{name}");
}
```

Cuối function:

```text
name
 ↓
drop()
 ↓
heap memory released
```

Rust tự động gọi cơ chế `Drop`.

Bạn không cần:

```rust
free(name);
```

---

# 10. Drop

Rust có cơ chế:

```text
Drop
```

cho những giá trị cần cleanup.

Với `String`, khi owner hết scope:

```text
String
  ↓
Drop
  ↓
release heap allocation
```

Điểm quan trọng:

> Rust giải phóng memory dựa trên scope và ownership.

Không cần garbage collector.

---

# 11. Scope

Ownership gắn cực kỳ chặt với scope.

Ví dụ:

```rust
fn main() {
    let x = 10;

    {
        let y = 20;

        println!("{x}");
        println!("{y}");
    }

    println!("{x}");

    // println!("{y}"); // lỗi
}
```

Scope của `y`:

```text
{
    let y = 20;

    ...
}
```

Khi `}`:

```text
y
↓
out of scope
↓
dropped
```

---

# 12. Scope của biến

Ví dụ:

```rust
fn main() {
    let a = 10;

    {
        let b = 20;

        println!("{a}");
        println!("{b}");
    }

    println!("{a}");
}
```

`a` sống:

```text
main scope
```

`b` sống:

```text
inner scope
```

---

# 13. Scope và lifetime không hoàn toàn giống nhau

Đây là điểm cần cẩn thận.

Ở giai đoạn hiện tại, hãy hiểu:

```text
scope
```

là vùng code mà binding có thể được sử dụng.

Còn:

```text
lifetime
```

là khái niệm sâu hơn liên quan đến thời gian reference hợp lệ.

Chúng ta chưa cần đào sâu lifetime hôm nay.

---

# 14. Ví dụ đầu tiên về Ownership

Chạy:

```rust
fn main() {
    let s = String::from("hello");

    println!("{s}");
}
```

Output:

```text
hello
```

Không có vấn đề gì.

---

# 15. Ownership khi gán

Bây giờ:

```rust
fn main() {
    let s1 = String::from("hello");

    let s2 = s1;

    println!("{s2}");
}
```

Output:

```text
hello
```

Nhưng điều quan trọng nằm ở đây:

```rust
let s2 = s1;
```

Ownership đã chuyển.

```text
s1 ──────→ String
             ↓
         ownership
             ↓
s2 ──────→ String
```

Thực tế sau lệnh này:

```text
s1 = invalid
s2 = owner
```

---

# 16. Tại sao Rust làm vậy?

Giả sử Rust cho phép cả hai cùng sở hữu:

```text
s1 ─┐
    ├──> heap memory
s2 ─┘
```

Khi:

```text
s1
```

ra khỏi scope:

```text
drop(s1)
```

heap memory bị giải phóng.

Nhưng:

```text
s2
```

vẫn đang trỏ đến vùng memory đó.

Khi `s2` ra khỏi scope:

```text
drop(s2)
```

Rust có thể cố giải phóng lần nữa.

Đó là:

```text
double free
```

Rust ngăn vấn đề này bằng Ownership.

---

# 17. Đây là lý do Move tồn tại

Thay vì:

```text
s1 ─┐
    ├──> heap
s2 ─┘
```

Rust làm:

```text
s1 ──ownership──> heap
          ↓
       move
          ↓
s2 ──ownership──> heap
```

Sau Move:

```text
s1 → invalid
s2 → owner
```

Không có hai owner.

---

# 18. Test compiler

Hãy thử:

```rust
fn main() {
    let s1 = String::from("hello");

    let s2 = s1;

    println!("{s1}");
    println!("{s2}");
}
```

Compile:

```bash
cargo run
```

Bạn sẽ nhận lỗi tương tự:

```text
borrow of moved value: `s1`
```

Đây là một trong những error message quan trọng nhất khi học Rust.

---

# 19. Đừng sợ compiler error

Khi học Rust:

```text
Compiler
   ↓
Error
   ↓
Đọc error
   ↓
Hiểu ownership
   ↓
Sửa code
```

Compiler chính là một phần của quá trình học.

Đừng chỉ sửa cho code chạy.

Hãy hỏi:

> Tại sao compiler không cho phép code này?

---

# 20. Integer thì sao?

Bây giờ:

```rust
fn main() {
    let x = 10;

    let y = x;

    println!("{x}");
    println!("{y}");
}
```

Code này **chạy được**.

Tại sao?

Vì `i32` là kiểu `Copy`.

```text
x = 10
 ↓
copy
 ↓
y = 10
```

Không có ownership move giống `String`.

Chúng ta sẽ học kỹ:

```text
Buổi 24 — Copy
```

---

# 21. So sánh String và i32

### String

```rust
let s1 = String::from("hello");
let s2 = s1;
```

→ Move.

### i32

```rust
let x = 10;
let y = x;
```

→ Copy.

Đây là sự khác biệt cực kỳ quan trọng.

---

# 22. Ownership với function

Đây là phần quan trọng.

```rust
fn consume(s: String) {
    println!("{s}");
}

fn main() {
    let name = String::from("Rust");

    consume(name);

    println!("{name}");
}
```

Code này lỗi.

Tại sao?

Khi:

```rust
consume(name);
```

ownership của `name` được chuyển vào function.

```text
main
 name
  │
  │ move
  ▼
consume()
   s
```

Sau khi gọi:

```rust
name
```

không còn sở hữu value.

---

# 23. Function nhận ownership

Hãy hình dung:

```rust
fn consume(s: String)
```

nghĩa là:

> Tôi nhận ownership của một `String`.

Khi gọi:

```rust
consume(name);
```

ta chuyển:

```text
name
 ↓
consume
```

---

# 24. Sau function

```rust
fn consume(s: String) {
    println!("{s}");
}
```

Khi `consume()` kết thúc:

```text
s
↓
drop
↓
heap released
```

Ownership đã chuyển vào function.

---

# 25. Đây là một pattern rất quan trọng

```text
Caller
  │
  │ ownership
  ▼
Function
  │
  ▼
Function owns value
  │
  ▼
Function ends
  │
  ▼
value dropped
```

Function có thể **consume** value.

---

# 26. Function trả ownership lại

Rust có thể chuyển ownership ngược lại.

```rust
fn create_name() -> String {
    let name = String::from("Rust");

    name
}

fn main() {
    let name = create_name();

    println!("{name}");
}
```

Flow:

```text
create_name
    │
    ├── create String
    │
    └── return String
            │
            ▼
          main
            │
          name
```

Ownership được chuyển từ function về caller.

---

# 27. Return value cũng có Ownership

Đây là điểm rất quan trọng.

```rust
fn create() -> String {
    let s = String::from("hello");

    s
}
```

`String` không bị mất khi function kết thúc.

Tại sao?

Vì ownership đã được transfer qua:

```rust
return s;
```

Sau đó:

```text
main
 ↓
owner
```

---

# 28. Ownership flow

Bạn nên tập nhìn code theo flow:

```text
let s = String::from("hello");
```

```text
main
 │
 └── s owns String
```

Sau:

```rust
let s2 = s;
```

```text
main
 │
 ├── s  ❌ moved
 │
 └── s2 ─── owns String
```

Sau:

```rust
consume(s2);
```

```text
main
 │
 └── consume
        │
        └── s2's String
```

Function kết thúc:

```text
String
 ↓
drop
```

---

# 29. Ownership và `println!`

Một điều rất hay:

```rust
let s = String::from("hello");

println!("{s}");
println!("{s}");
```

Hai lần đều được.

`println!` không lấy ownership của `s` chỉ vì bạn truyền nó vào format.

Nó có cơ chế borrowing/formatting phía sau.

Ở mức hiện tại, chỉ cần nhớ:

```text
println!("{s}")
```

không làm `s` bị move.

---

# 30. Ownership với tuple

Ví dụ:

```rust
fn main() {
    let data = (
        String::from("Rust"),
        String::from("Python"),
    );

    println!("{}", data.0);
    println!("{}", data.1);
}
```

`data` sở hữu cả hai `String`:

```text
data
 │
 ├── .0 → String
 │
 └── .1 → String
```

Khi `data` hết scope:

```text
data
 ↓
drop .0
drop .1
```

---

# 31. Ownership với Vec

```rust
fn main() {
    let books = vec![
        String::from("Rust"),
        String::from("Python"),
        String::from("Go"),
    ];

    println!("{books:?}");
}
```

`books` sở hữu:

```text
Vec
 │
 └── heap
      ├── Rust
      ├── Python
      └── Go
```

Khi:

```text
books
```

ra khỏi scope:

```text
Vec
 ↓
drop
 ↓
elements dropped
 ↓
buffer released
```

---

# 32. Ownership trong project crawler

Điều này rất quan trọng với project của bạn.

Ví dụ:

```rust
struct Story {
    title: String,
    chapters: Vec<String>,
}
```

Khi:

```rust
let story = Story {
    title: String::from("Rust Book"),
    chapters: vec![
        String::from("Chapter 1"),
        String::from("Chapter 2"),
    ],
};
```

`story` sở hữu:

```text
story
 │
 ├── title
 │     └── String
 │
 └── chapters
       └── Vec
            ├── String
            └── String
```

Đây là **ownership tree**.

---

# 33. Ownership tree

Hãy tập suy nghĩ:

```text
Story
 │
 ├── title ─────────── owns String
 │
 └── chapters ─────── owns Vec
                       │
                       ├── Chapter 1 String
                       └── Chapter 2 String
```

Khi:

```text
Story
```

bị drop:

```text
Story
 ↓
title dropped
chapters dropped
 ↓
Chapter Strings dropped
 ↓
heap memory released
```

Rust tự quản lý toàn bộ cây ownership này.

---

# 34. Đây là lý do Rust không cần Garbage Collector

Trong GC language:

```text
objects
   ↓
GC tìm objects không còn reachable
   ↓
cleanup
```

Rust:

```text
owner
 ↓
scope ends
 ↓
drop
 ↓
cleanup
```

Compiler biết ownership từ trước.

Do đó Rust có thể đạt:

```text
memory safety
+
predictable cleanup
+
no GC
```

---

# 35. Drop order

Ví dụ:

```rust
fn main() {
    let a = String::from("A");
    let b = String::from("B");
    let c = String::from("C");
}
```

Các local variables được cleanup theo thứ tự ngược lại:

```text
c
↓
b
↓
a
```

Có thể hình dung:

```text
STACK

c
b
a
```

Khi scope kết thúc:

```text
c → drop
b → drop
a → drop
```

---

# 36. Ownership không phải "biến chứa object"

Đây là một cách hiểu chưa đủ.

Không chỉ:

```text
name → String
```

Mà phải nghĩ:

```text
name
  │
  │ owns
  ▼
resource
```

Ownership là **quyền chịu trách nhiệm đối với resource**.

Resource có thể là:

```text
heap allocation
file handle
socket
database connection
lock
```

Đây là tư tưởng rất quan trọng của Rust:

> Resource Acquisition Is Initialization — RAII.

---

# 37. RAII

Rust tận dụng ownership để quản lý resource.

Ví dụ concept:

```text
File
 ↓
owner
 ↓
scope
 ↓
scope ends
 ↓
Drop
 ↓
file closed
```

Tương tự:

```text
MutexGuard
Socket
Database connection
String
Vec
```

Ownership không chỉ liên quan đến memory.

Nó là nền tảng của **resource management**.

---

# 38. Ownership và `Drop`

Rust cho phép type thực hiện cleanup thông qua trait:

```rust
Drop
```

Ví dụ:

```rust
struct Resource {
    name: String,
}

impl Drop for Resource {
    fn drop(&mut self) {
        println!(
            "Dropping {}",
            self.name
        );
    }
}
```

Test:

```rust
fn main() {
    let resource = Resource {
        name: String::from("Database"),
    };

    println!("Using resource");
}
```

Output:

```text
Using resource
Dropping Database
```

Bạn chưa cần học `Drop` sâu hôm nay.

Chỉ cần hiểu:

```text
owner hết scope
      ↓
Drop
      ↓
cleanup
```

---

# 39. Ownership không đồng nghĩa với Heap

Đây là một hiểu lầm phổ biến.

Ownership không chỉ áp dụng cho:

```text
String
Vec
Box
```

Mà áp dụng cho **mọi value**.

Ví dụ:

```rust
let x = 10;
```

`x` vẫn có ownership đối với value `10`.

Nhưng vì `i32` là `Copy`, việc gán:

```rust
let y = x;
```

sao chép value thay vì chuyển ownership theo cách của non-Copy types.

---

# 40. Ownership và Copy

Đây là chỗ cần phân biệt:

```text
Ownership
     │
     ├── Copy type
     │      └── assignment copies value
     │
     └── non-Copy type
            └── assignment moves ownership
```

Ví dụ:

```rust
let a = 10;
let b = a;
```

→ `Copy`.

Trong khi:

```rust
let a = String::from("hello");
let b = a;
```

→ `Move`.

Buổi 22–24 chúng ta sẽ tách từng trường hợp.

---

# 41. Một ví dụ rất quan trọng

Hãy đoán code nào compile.

### A

```rust
let a = String::from("hello");
let b = a;

println!("{b}");
```

Compile?

**Có.**

Vì `b` đã trở thành owner.

---

### B

```rust
let a = String::from("hello");
let b = a;

println!("{a}");
```

Compile?

**Không.**

Vì `a` đã bị move.

---

### C

```rust
let a = 10;
let b = a;

println!("{a}");
```

Compile?

**Có.**

Vì `i32: Copy`.

---

# 42. Ownership với function

### Consume

```rust
fn consume(value: String) {
    println!("{value}");
}
```

Call:

```rust
let value = String::from("Rust");

consume(value);
```

→ ownership chuyển vào function.

---

### Return

```rust
fn produce() -> String {
    String::from("Rust")
}
```

Call:

```rust
let value = produce();
```

→ ownership chuyển về caller.

---

# 43. Pattern quan trọng

Rust thường có:

```text
take ownership
return ownership
```

Ví dụ:

```rust
fn transform(value: String) -> String {
    value.to_uppercase()
}
```

```rust
let value = String::from("rust");

let value = transform(value);
```

Flow:

```text
value
 ↓
transform()
 ↓
new String
 ↓
value
```

Đây là một pattern hợp lệ, nhưng khi chương trình lớn sẽ có rất nhiều trường hợp bạn **không muốn chuyển ownership**.

Và đó chính là lý do chúng ta cần:

# Borrowing

ở Buổi 25.

---

# 44. Ownership vs Borrowing

Hiện tại hãy nhớ:

### Ownership

```rust
fn process(story: Story)
```

Function nhận:

```text
ownership
```

### Borrowing

Sau này:

```rust
fn process(story: &Story)
```

Function chỉ:

```text
borrow
```

Không lấy ownership.

Đây là sự khác biệt cốt lõi.

---

# 45. Tư duy quan trọng nhất hôm nay

Đừng đọc:

```rust
let b = a;
```

như một programmer Python:

> "b tham chiếu tới a."

Hãy đọc theo Rust:

> "Ownership của value đang được chuyển từ `a` sang `b`."

Đây là thay đổi tư duy rất lớn.

---

# 46. Bài tập 1 — Scope

Dự đoán code nào compile:

```rust
fn main() {
    let a = String::from("A");

    {
        let b = String::from("B");

        println!("{a}");
        println!("{b}");
    }

    println!("{a}");
}
```

Sau đó thử:

```rust
println!("{b}");
```

bên ngoài block.

Giải thích tại sao compiler báo lỗi.

---

# 47. Bài tập 2 — Move

Dự đoán:

```rust
fn main() {
    let name = String::from("Rust");

    let other = name;

    println!("{name}");
}
```

Sau đó sửa để chương trình compile.

Gợi ý:

```rust
println!("{other}");
```

---

# 48. Bài tập 3 — Function ownership

Cho:

```rust
fn consume(value: String) {
    println!("{value}");
}
```

Viết `main()` sao cho:

```text
Rust
```

được in ra và không có ownership error.

---

# 49. Bài tập 4 — Return ownership

Viết:

```rust
fn create_story() -> String
```

trả về:

```text
"Rust Crawler"
```

Sau đó:

```rust
let story = create_story();
```

và in:

```text
Rust Crawler
```

---

# 50. Bài tập 5 — Ownership trong crawler

Tạo:

```rust
struct Story {
    title: String,
}
```

Viết:

```rust
fn process_story(story: Story)
```

Function in:

```text
Processing: Rust Book
```

Sau đó thử:

```rust
let story = Story {
    title: String::from("Rust Book"),
};

process_story(story);

println!("{}", story.title);
```

Quan sát compiler.

Hãy tự giải thích:

```text
story
 ↓
process_story
 ↓
ownership moved
```

---

# 51. Bài tập 6 — Ownership Tree

Tạo:

```rust
struct Chapter {
    title: String,
}

struct Story {
    title: String,
    chapters: Vec<Chapter>,
}
```

Tạo:

```text
Story
 ├── title
 ├── Chapter 1
 └── Chapter 2
```

Sau đó viết:

```rust
fn consume_story(story: Story) {
    ...
}
```

và truyền `story` vào function.

Hãy tự vẽ ownership tree trước khi chạy code.

---

# 52. Bài tập 7 — Thử dự đoán compiler

Không chạy ngay.

Hãy dự đoán từng đoạn:

### Code 1

```rust
let x = 10;
let y = x;
println!("{x}");
```

### Code 2

```rust
let x = String::from("Rust");
let y = x;
println!("{x}");
```

### Code 3

```rust
let x = String::from("Rust");
consume(x);
println!("{x}");
```

### Code 4

```rust
let x = String::from("Rust");
let y = x;
println!("{y}");
```

Sau đó mới chạy `cargo check`.

Đây là cách học Rust hiệu quả hơn việc chỉ copy code.

---

# 53. `cargo check` rất hữu ích

Thay vì lúc nào cũng:

```bash
cargo run
```

hãy sử dụng:

```bash
cargo check
```

Nó kiểm tra:

```text
syntax
types
ownership
borrowing
```

mà không cần build executable hoàn chỉnh.

Trong quá trình học Ownership, bạn sẽ dùng:

```bash
cargo check
```

rất nhiều.

---

# 54. Quy trình học Ownership

Từ hôm nay, mỗi khi gặp compiler error, hãy làm 4 bước:

```text
1. Đọc error
      ↓
2. Xác định value nào
      ↓
3. Xác định owner hiện tại
      ↓
4. Xác định operation nào
   làm ownership thay đổi
```

Ví dụ:

```rust
let s1 = String::from("hello");
let s2 = s1;
println!("{s1}");
```

Phân tích:

```text
s1 owns String
      ↓
s2 = s1
      ↓
ownership moves
      ↓
s1 invalid
      ↓
println!("{s1}")
      ↓
ERROR
```

Đây chính là tư duy Rust.

---

# 55. Cheat Sheet Buổi 21

```text
OWNERSHIP
│
├── mỗi value có owner
│
├── một thời điểm chỉ có một owner
│
├── owner ra khỏi scope
│       ↓
│      drop
│
├── String / Vec
│       ↓
│      thường Move
│
├── i32 / bool / char
│       ↓
│      Copy
│
├── function nhận T
│       ↓
│      nhận ownership
│
├── function trả T
│       ↓
│      chuyển ownership về caller
│
└── muốn dùng mà không lấy ownership
        ↓
     Borrowing
```

---

# 56. Câu hỏi kiểm tra cuối buổi

Bạn cần tự trả lời được 7 câu này:

1. Ownership là gì?
2. Một value có thể có bao nhiêu owner tại cùng một thời điểm?
3. Khi owner ra khỏi scope thì chuyện gì xảy ra?
4. Tại sao `String` bị move nhưng `i32` thường được copy?
5. Khi truyền `String` vào `fn foo(value: String)`, ownership đi đâu?
6. Function có thể trả ownership cho caller không?
7. Vì sao Rust cần Borrowing?

Nếu bạn trả lời được 1–6 nhưng chưa trả lời chắc câu 7 thì **hoàn toàn bình thường**. Câu 7 chính là cầu nối sang Buổi 25.

---

# 57. Roadmap tiếp theo

```text
Buổi 21 — Ownership       ← hôm nay
     │
     ▼
Buổi 22 — Move
     │
     ▼
Buổi 23 — Clone
     │
     ▼
Buổi 24 — Copy
     │
     ▼
Buổi 25 — Borrow
     │
     ▼
Buổi 26 — Mutable Borrow
     │
     ▼
Buổi 27 — Slice
     │
     ▼
Buổi 28 — String
     │
     ▼
Buổi 29 — String vs &str
     │
     ▼
Buổi 30 — Ownership Deep Dive
```

**Điểm quan trọng nhất của Buổi 21:** từ bây giờ, khi nhìn một đoạn Rust code, hãy luôn hỏi **“Value này đang thuộc về ai?”**. Nếu hình dung được ownership tree và ownership flow, các lỗi `move`, `borrow`, `lifetime` về sau sẽ dễ hiểu hơn rất nhiều.
