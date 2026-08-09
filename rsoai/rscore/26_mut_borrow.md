# Rust — Phần III: Ownership

# Buổi 26 — Mutable Borrow `&mut T`

Buổi 25 chúng ta học:

```rust
&T
```

tức **immutable borrow** — mượn để đọc.

Hôm nay học:

```rust
&mut T
```

tức **mutable borrow** — mượn để thay đổi dữ liệu.

Đây là một trong những cơ chế cốt lõi nhất của Rust vì nó liên quan trực tiếp đến:

* Ownership
* Borrowing
* Aliasing
* Mutation
* Data race
* Borrow Checker
* Memory safety

---

# 1. Vấn đề

Giả sử:

```rust
fn main() {
    let x = 10;

    let r = &x;

    *r = 20;
}
```

Code này không compile.

Vì `r` là:

```rust
&x
```

tức immutable reference.

Nó chỉ có quyền:

```text
READ
```

không có quyền:

```text
WRITE
```

---

# 2. Mutable Borrow

Muốn thay đổi value thông qua reference:

```rust
&mut
```

Ví dụ:

```rust
fn main() {
    let mut x = 10;

    let r = &mut x;

    *r = 20;

    println!("{x}");
}
```

Kết quả:

```text
20
```

Đây chính là:

```rust
&mut x
```

---

# 3. Phải có `mut` ở owner

Chú ý:

```rust
let mut x = 10;
```

không được bỏ `mut`.

Sai:

```rust
let x = 10;

let r = &mut x;
```

Rust sẽ báo lỗi vì `x` không mutable.

---

# 4. Có hai `mut` khác nhau

Đây là điểm rất quan trọng.

```rust
let mut x = 10;
let r = &mut x;
```

Có hai ý nghĩa:

### `mut x`

Cho phép value `x` bị thay đổi.

### `&mut x`

Cho phép reference `r` thay đổi value mà nó đang borrow.

Mental model:

```text
x
│
└── mutable data
     ▲
     │
     r = &mut x
     │
     └── mutable access
```

---

# 5. Dereference để thay đổi

```rust
fn main() {
    let mut x = 10;

    let r = &mut x;

    *r = 100;

    println!("{x}");
}
```

Ở đây:

```rust
*r
```

nghĩa là:

> value mà `r` đang trỏ tới.

Vì `r` là mutable reference nên:

```rust
*r = 100;
```

hợp lệ.

---

# 6. `&T` vs `&mut T`

| Reference | Đọc | Ghi |
| --------- | --: | --: |
| `&T`      |   ✅ |   ❌ |
| `&mut T`  |   ✅ |   ✅ |

Ví dụ:

```rust
let r = &x;
```

chỉ:

```text
READ
```

Còn:

```rust
let r = &mut x;
```

cho phép:

```text
READ
WRITE
```

---

# 7. Function nhận Mutable Borrow

Ví dụ:

```rust
fn increase(value: &mut i32) {
    *value += 1;
}

fn main() {
    let mut x = 10;

    increase(&mut x);

    println!("{x}");
}
```

Kết quả:

```text
11
```

Function:

```rust
fn increase(value: &mut i32)
```

không lấy ownership của `x`.

Nó chỉ mượn quyền mutable access.

---

# 8. Flow

Khi gọi:

```rust
increase(&mut x);
```

ta có:

```text
main
 │
 │ owns
 ▼
 x = 10
 │
 │ mutable borrow
 ▼
increase()
 │
 │ *value += 1
 ▼
 x = 11
```

Sau khi function kết thúc:

```text
mutable borrow kết thúc
```

Ownership vẫn ở `main`.

---

# 9. Mutable Borrow không chuyển Ownership

Ví dụ:

```rust
fn reset(value: &mut String) {
    value.clear();
}

fn main() {
    let mut text = String::from("Hello Rust");

    reset(&mut text);

    println!("{text}");
}
```

Sau `reset()`:

```text
text
```

vẫn thuộc về `main`.

Chỉ có quyền mutable access được mượn tạm thời.

---

# 10. Đây là khác biệt cực lớn

### Move

```rust
reset(text);
```

Nếu function:

```rust
fn reset(text: String)
```

thì ownership chuyển.

---

### Mutable Borrow

```rust
reset(&mut text);
```

Nếu function:

```rust
fn reset(text: &mut String)
```

thì ownership không chuyển.

---

# 11. Ví dụ thực tế với `String`

```rust
fn append_rust(text: &mut String) {
    text.push_str(" Rust");
}

fn main() {
    let mut text = String::from("Hello");

    append_rust(&mut text);

    println!("{text}");
}
```

Kết quả:

```text
Hello Rust
```

---

# 12. Tại sao cần `&mut`?

Nếu không có `&mut`, function muốn thay đổi `String` phải lấy ownership:

```rust
fn append_rust(mut text: String) {
    text.push_str(" Rust");
}
```

Sau đó:

```rust
append_rust(text);
```

`text` bị Move.

Nhưng chúng ta chỉ muốn:

> Cho function quyền sửa String.

Do đó:

```rust
fn append_rust(text: &mut String)
```

tốt hơn.

---

# 13. Quy tắc quan trọng nhất

Rust có một quy tắc:

> **Tại một thời điểm, bạn có thể có nhiều immutable references hoặc một mutable reference, nhưng không thể đồng thời có cả hai đang được sử dụng.**

Hình dung:

```text
OK:

&T
&T
&T
```

hoặc:

```text
OK:

&mut T
```

Nhưng không:

```text
❌

&T
&T
&mut T
```

---

# 14. Ví dụ lỗi

```rust
fn main() {
    let mut x = 10;

    let a = &x;
    let b = &mut x;

    println!("{a}");
    println!("{b}");
}
```

Không compile.

Vì:

```text
a → immutable borrow
b → mutable borrow
```

cùng tồn tại trong vùng sử dụng.

---

# 15. Tại sao Rust cấm?

Giả sử cho phép:

```text
a → &x
b → &mut x
```

Sau đó:

```rust
println!("{a}");
*b = 100;
println!("{a}");
```

Kết quả của `a` sẽ thay đổi trong khi `a` đang là reference.

Nếu nhiều thread cùng làm việc này, tình hình còn nguy hiểm hơn.

Rust muốn đảm bảo:

> Không có aliasing mutable access nguy hiểm.

---

# 16. Quy tắc "Aliasing XOR Mutation"

Đây là một mental model rất quan trọng:

```text
Aliasing XOR Mutation
```

Nghĩa là:

```text
Nhiều người cùng đọc
        HOẶC
Một người được quyền thay đổi
```

Không phải:

```text
Nhiều người đọc + một người thay đổi cùng lúc
```

---

# 17. Nhiều immutable borrow

Hoàn toàn hợp lệ:

```rust
fn main() {
    let x = 10;

    let a = &x;
    let b = &x;
    let c = &x;

    println!("{a}");
    println!("{b}");
    println!("{c}");
}
```

Mô hình:

```text
        ┌── a
        │
x ──────┼── b
        │
        └── c
```

Tất cả chỉ đọc.

---

# 18. Một mutable borrow

Hợp lệ:

```rust
fn main() {
    let mut x = 10;

    let a = &mut x;

    *a += 10;

    println!("{a}");
}
```

Mô hình:

```text
x
▲
│
a = &mut x
```

Chỉ một mutable access.

---

# 19. Hai mutable borrow đồng thời

Code:

```rust
fn main() {
    let mut x = 10;

    let a = &mut x;
    let b = &mut x;

    println!("{a}");
    println!("{b}");
}
```

Không compile.

Vì:

```text
a → &mut x
b → &mut x
```

đồng thời tồn tại.

---

# 20. Tại sao hai `&mut` nguy hiểm?

Ví dụ giả sử Rust cho phép:

```rust
let a = &mut x;
let b = &mut x;
```

Sau đó:

```rust
*a = 100;
*b = 200;
```

Ai kiểm soát giá trị cuối?

Có thể là:

```text
100
```

hoặc:

```text
200
```

Nếu concurrency xuất hiện, vấn đề còn nghiêm trọng hơn.

Rust ngăn từ compile time.

---

# 21. Mutable Borrow có tính độc quyền

Có thể nhớ:

```text
&T
=
shared access
```

còn:

```text
&mut T
=
exclusive access
```

Đây là cách hiểu rất tốt.

---

# 22. Scope của Mutable Borrow

Xét:

```rust
fn main() {
    let mut x = 10;

    {
        let r = &mut x;

        *r += 10;
    }

    println!("{x}");
}
```

Hợp lệ.

Flow:

```text
x
│
├── mutable borrow
│      │
│      └── r
│
└── borrow kết thúc
       │
       ▼
    x dùng lại
```

---

# 23. Non-Lexical Lifetimes

Rust hiện đại có khả năng nhận biết borrow kết thúc khi reference không còn được sử dụng, không nhất thiết phải chờ tới `}`.

Ví dụ:

```rust
fn main() {
    let mut x = 10;

    let r = &mut x;

    *r += 1;

    println!("{x}");
}
```

Điều này hợp lệ.

Sau:

```rust
*r += 1;
```

`r` không còn được sử dụng.

Rust có thể kết thúc borrow tại đó.

---

# 24. Ví dụ

```rust
fn main() {
    let mut x = 10;

    let r = &mut x;

    *r += 10;

    let s = &x;

    println!("{s}");
}
```

Compile được.

Vì:

```text
r
│
└── last use

s
│
└── borrow sau đó
```

Không overlap.

---

# 25. Nhưng nếu dùng `r` sau đó

```rust
fn main() {
    let mut x = 10;

    let r = &mut x;

    let s = &x;

    println!("{r}");
    println!("{s}");
}
```

Không compile.

Bởi vì:

```text
r → mutable borrow
s → immutable borrow
```

overlap.

---

# 26. Mutable Borrow với `String`

Một ví dụ rất quan trọng:

```rust
fn add_text(text: &mut String) {
    text.push_str(" World");
}

fn main() {
    let mut text = String::from("Hello");

    add_text(&mut text);

    println!("{text}");
}
```

Đây là pattern bạn sẽ sử dụng rất thường xuyên.

---

# 27. Mutable Borrow với `Vec`

```rust
fn add_number(numbers: &mut Vec<i32>) {
    numbers.push(100);
}

fn main() {
    let mut numbers = vec![1, 2, 3];

    add_number(&mut numbers);

    println!("{numbers:?}");
}
```

Kết quả:

```text
[1, 2, 3, 100]
```

---

# 28. Mutable Borrow với struct

```rust
struct User {
    name: String,
    age: u32,
}

fn birthday(user: &mut User) {
    user.age += 1;
}

fn main() {
    let mut user = User {
        name: String::from("Alice"),
        age: 20,
    };

    birthday(&mut user);

    println!("{} {}", user.name, user.age);
}
```

Kết quả:

```text
Alice 21
```

---

# 29. Đây là pattern rất quan trọng

Function:

```rust
fn update(user: &mut User)
```

có nghĩa:

> Tôi không sở hữu `User`, nhưng tôi cần quyền sửa `User`.

Đây là một trong những API design patterns quan trọng nhất của Rust.

---

# 30. `&mut self`

Khi học `struct` và `impl`, bạn sẽ gặp:

```rust
fn add_chapter(&mut self)
```

Nó có nghĩa:

> Method này cần quyền mutable borrow đối với object.

Ví dụ:

```rust
struct Counter {
    value: i32,
}

impl Counter {
    fn increment(&mut self) {
        self.value += 1;
    }
}

fn main() {
    let mut counter = Counter { value: 0 };

    counter.increment();
    counter.increment();

    println!("{}", counter.value);
}
```

Kết quả:

```text
2
```

---

# 31. `&self` vs `&mut self`

Bạn sẽ gặp ba dạng:

```rust
&self
```

```text
immutable borrow
```

```rust
&mut self
```

```text
mutable borrow
```

và:

```rust
self
```

```text
take ownership
```

Bảng:

| Function receiver | Ý nghĩa       |
| ----------------- | ------------- |
| `self`            | lấy ownership |
| `&self`           | borrow để đọc |
| `&mut self`       | borrow để sửa |

---

# 32. Mutable Borrow và method

Ví dụ:

```rust
struct Counter {
    value: i32,
}

impl Counter {
    fn value(&self) -> i32 {
        self.value
    }

    fn increment(&mut self) {
        self.value += 1;
    }
}
```

Sử dụng:

```rust
fn main() {
    let mut counter = Counter { value: 0 };

    println!("{}", counter.value());

    counter.increment();

    println!("{}", counter.value());
}
```

---

# 33. Một mutable borrow có thể thay đổi nhiều lần

```rust
fn main() {
    let mut x = 10;

    let r = &mut x;

    *r += 10;
    *r += 20;
    *r += 30;

    println!("{r}");
}
```

Kết quả:

```text
70
```

Một mutable reference có thể thực hiện nhiều mutation.

---

# 34. Mutable reference có thể truyền tiếp

Ví dụ:

```rust
fn add_ten(value: &mut i32) {
    *value += 10;
}

fn process(value: &mut i32) {
    add_ten(value);
    add_ten(value);
}

fn main() {
    let mut x = 0;

    process(&mut x);

    println!("{x}");
}
```

Kết quả:

```text
20
```

Flow:

```text
x
│
└── &mut x
      │
      ▼
   process
      │
      ├── add_ten
      └── add_ten
```

---

# 35. Reborrow

Đây là khái niệm quan trọng.

Khi bạn có:

```rust
&mut T
```

bạn có thể tạm thời tạo một mutable borrow mới từ nó.

Ví dụ:

```rust
fn add(value: &mut i32) {
    *value += 1;
}

fn process(value: &mut i32) {
    add(value);
    add(value);
}
```

Ở đây `value` được reborrow khi truyền vào `add`.

Conceptually:

```text
original &mut
      │
      ├── reborrow → add()
      │
      └── reborrow → add()
```

Chúng ta sẽ đào sâu reborrow ở phần Ownership Deep Dive.

---

# 36. Mutable Borrow trong collection

Đây là một pattern rất quan trọng:

```rust
fn increase_all(numbers: &mut Vec<i32>) {
    for number in numbers {
        *number += 1;
    }
}
```

Test:

```rust
fn main() {
    let mut numbers = vec![1, 2, 3];

    increase_all(&mut numbers);

    println!("{numbers:?}");
}
```

Kết quả:

```text
[2, 3, 4]
```

---

# 37. Tại sao `number` cần `*`?

Trong:

```rust
for number in numbers
```

với mutable vector borrow, `number` là mutable reference tới từng element.

Conceptually:

```text
number: &mut i32
```

Do đó:

```rust
*number += 1;
```

nghĩa là:

> Thay đổi value mà reference đang trỏ tới.

---

# 38. Ví dụ hoàn chỉnh — Shopping Cart

Đây là ví dụ thực tế.

```rust
struct Cart {
    items: Vec<String>,
}

fn add_item(cart: &mut Cart, item: String) {
    cart.items.push(item);
}

fn remove_last(cart: &mut Cart) {
    cart.items.pop();
}

fn print_cart(cart: &Cart) {
    println!("Cart:");

    for item in &cart.items {
        println!("- {item}");
    }
}

fn main() {
    let mut cart = Cart {
        items: Vec::new(),
    };

    add_item(&mut cart, String::from("Book"));
    add_item(&mut cart, String::from("Keyboard"));
    add_item(&mut cart, String::from("Mouse"));

    print_cart(&cart);

    remove_last(&mut cart);

    println!();
    print_cart(&cart);
}
```

Đây là architecture rất đáng chú ý:

```text
add_item
   │
   └── &mut Cart

remove_last
   │
   └── &mut Cart

print_cart
   │
   └── &Cart
```

Function chỉ nhận đúng quyền mà nó cần.

---

# 39. Principle: Least Privilege

Một nguyên tắc thiết kế API rất hay:

> Function chỉ nên nhận quyền truy cập cần thiết.

Nếu chỉ đọc:

```rust
fn print_cart(cart: &Cart)
```

Nếu cần sửa:

```rust
fn add_item(cart: &mut Cart)
```

Không nên viết:

```rust
fn print_cart(cart: &mut Cart)
```

nếu function không cần mutation.

---

# 40. Vì sao?

`&mut T` là quyền mạnh hơn:

```text
&T
 │
 └── READ

&mut T
 │
 ├── READ
 └── WRITE
```

Nếu chỉ cần đọc, dùng:

```rust
&T
```

giúp compiler có nhiều thông tin hơn về aliasing.

---

# 41. Một ví dụ Borrow Checker kinh điển

```rust
fn main() {
    let mut numbers = vec![1, 2, 3];

    let first = &numbers[0];

    numbers.push(4);

    println!("{first}");
}
```

Code này có thể bị compiler từ chối.

Tại sao?

`first` đang immutable borrow một phần của vector:

```text
first
 │
 ▼
numbers[0]
```

Sau đó:

```rust
numbers.push(4);
```

có thể cần mutable access tới toàn bộ vector.

Rust không cho phép hai quyền đó overlap theo cách không an toàn.

---

# 42. Vì sao `Vec::push` đặc biệt nguy hiểm?

`Vec` có thể realloc khi thêm element.

Ví dụ:

```text
BEFORE

Vec
│
└── heap allocation
     ├── 1
     ├── 2
     └── 3
```

Sau:

```rust
numbers.push(4);
```

có thể:

```text
OLD MEMORY
   X

NEW MEMORY
   ├── 1
   ├── 2
   ├── 3
   └── 4
```

Nếu `first` vẫn trỏ vào vùng memory cũ thì reference sẽ trở thành dangling reference.

Rust ngăn điều này tại compile time.

---

# 43. Cách sửa

Nếu không cần `first` nữa:

```rust
fn main() {
    let mut numbers = vec![1, 2, 3];

    let first = numbers[0];

    numbers.push(4);

    println!("{first}");
}
```

Vì `i32` là `Copy`.

Ta lấy value chứ không giữ reference.

---

# 44. Hoặc kết thúc borrow trước

```rust
fn main() {
    let mut numbers = vec![1, 2, 3];

    {
        let first = &numbers[0];

        println!("{first}");
    }

    numbers.push(4);
}
```

Borrow kết thúc trước `push`.

---

# 45. Đây chính là sức mạnh của Borrow Checker

Borrow Checker không đơn giản chỉ nói:

> "Không được."

Nó đang bảo vệ:

```text
memory safety
+
aliasing safety
+
lifetime safety
```

mà không cần garbage collector.

---

# 46. Mutable Borrow và concurrency

Một trong những mục tiêu lớn của quy tắc:

```text
&mut T
```

là ngăn data race.

Data race thường cần:

```text
1. nhiều thread
2. cùng truy cập memory
3. ít nhất một thread ghi
4. không có synchronization phù hợp
```

Rust thiết kế ownership/borrowing để loại bỏ nhiều lớp lỗi này ngay từ compile time.

---

# 47. Đây là lý do Rust mạnh

Các ngôn ngữ khác có thể cho:

```text
reference A → read
reference B → write
```

cùng lúc.

Rust nói:

```text
NO.
```

và buộc bạn thiết kế access pattern rõ ràng.

---

# 48. Một ví dụ thực tế hơn

Giả sử crawler có:

```rust
struct Chapter {
    title: String,
    content: String,
    downloaded: bool,
}
```

Function đánh dấu đã download:

```rust
fn mark_downloaded(chapter: &mut Chapter) {
    chapter.downloaded = true;
}
```

Function đọc:

```rust
fn print_chapter(chapter: &Chapter) {
    println!("{}", chapter.title);
    println!("Downloaded: {}", chapter.downloaded);
}
```

Sử dụng:

```rust
fn main() {
    let mut chapter = Chapter {
        title: String::from("Chapter 1"),
        content: String::from("Hello Rust"),
        downloaded: false,
    };

    print_chapter(&chapter);

    mark_downloaded(&mut chapter);

    print_chapter(&chapter);
}
```

Đây chính là cách Borrow sẽ xuất hiện trong project lớn.

---

# 49. Bài tập 1 — Mutable String

Viết:

```rust
fn uppercase(text: &mut String)
```

để biến:

```text
hello rust
```

thành:

```text
HELLO RUST
```

Gợi ý:

```rust
text.make_ascii_uppercase();
```

Test:

```rust
fn main() {
    let mut text = String::from("hello rust");

    uppercase(&mut text);

    println!("{text}");
}
```

---

# 50. Bài tập 2 — Mutable Vec

Viết:

```rust
fn double(numbers: &mut Vec<i32>)
```

Ví dụ:

```text
[1, 2, 3, 4]
```

thành:

```text
[2, 4, 6, 8]
```

Gợi ý:

```rust
for number in numbers {
    *number *= 2;
}
```

---

# 51. Bài tập 3 — Struct

Tạo:

```rust
struct User {
    name: String,
    age: u32,
}
```

Viết:

```rust
fn birthday(user: &mut User)
```

để tăng:

```text
age += 1
```

Test:

```rust
fn main() {
    let mut user = User {
        name: String::from("Alice"),
        age: 20,
    };

    birthday(&mut user);

    println!("{} {}", user.name, user.age);
}
```

---

# 52. Bài tập 4 — Shopping Cart

Tạo:

```rust
struct Cart {
    items: Vec<String>,
}
```

Viết:

```rust
fn add_item(cart: &mut Cart, item: String)
```

và:

```rust
fn clear_cart(cart: &mut Cart)
```

và:

```rust
fn print_cart(cart: &Cart)
```

Mục tiêu:

```text
&Cart
    → đọc

&mut Cart
    → thay đổi
```

---

# 53. Bài tập 5 — Tìm lỗi Borrow Checker

Hãy thử compile:

```rust
fn main() {
    let mut x = 10;

    let a = &x;
    let b = &mut x;

    println!("{a}");
    println!("{b}");
}
```

Sau đó sửa để chương trình compile.

Một cách:

```rust
fn main() {
    let mut x = 10;

    let a = &x;

    println!("{a}");

    let b = &mut x;

    *b += 10;

    println!("{b}");
}
```

Điểm quan trọng là hai borrow **không overlap**.

---

# 54. Bài tập 6 — Tư duy API

Cho:

```rust
struct Story {
    title: String,
    content: String,
    views: u64,
}
```

Hãy quyết định function nào nên dùng:

```text
Story
&Story
&mut Story
```

### A

```text
display_story
```

### B

```text
increase_views
```

### C

```text
take_ownership_and_store
```

Đáp án:

```text
A → &Story
B → &mut Story
C → Story
```

Đây là cách tư duy API rất quan trọng.

---

# 55. Mini Project — Story Manager

Hãy viết chương trình hoàn chỉnh:

```rust
struct Story {
    title: String,
    views: u64,
    published: bool,
}

fn publish(story: &mut Story) {
    story.published = true;
}

fn increase_views(story: &mut Story) {
    story.views += 1;
}

fn print_story(story: &Story) {
    println!("Title: {}", story.title);
    println!("Views: {}", story.views);
    println!("Published: {}", story.published);
}

fn main() {
    let mut story = Story {
        title: String::from("Learning Rust"),
        views: 0,
        published: false,
    };

    print_story(&story);

    publish(&mut story);

    increase_views(&mut story);
    increase_views(&mut story);
    increase_views(&mut story);

    println!();

    print_story(&story);
}
```

Kết quả:

```text
Title: Learning Rust
Views: 0
Published: false

Title: Learning Rust
Views: 3
Published: true
```

Hãy chú ý architecture:

```text
                 Story
                   │
       ┌───────────┼───────────┐
       │           │           │
       ▼           ▼           ▼
   &Story       &mut Story   &mut Story
       │           │           │
    print       publish     increase_views
```

---

# 56. Một nguyên tắc bạn nên nhớ từ hôm nay

Khi thiết kế function:

```text
Function cần làm gì?
```

### Chỉ đọc:

```rust
fn foo(value: &T)
```

### Cần sửa:

```rust
fn foo(value: &mut T)
```

### Cần sở hữu:

```rust
fn foo(value: T)
```

Có thể nhớ thành:

```text
T
│
├── ownership
│
&T
│
└── read

&mut T
│
└── read + write
```

---

# 57. Ba cấp độ quyền

Đây là mental model cực tốt:

```text
T
│
└── OWN
    "Tôi sở hữu value"

&T
│
└── BORROW
    "Tôi chỉ đọc"

&mut T
│
└── MUTABLE BORROW
    "Tôi mượn quyền đọc + sửa"
```

---

# 58. Ownership model hoàn chỉnh đến hiện tại

```text
                    VALUE
                      │
          ┌───────────┼───────────┐
          │           │           │
        Move        Copy        Borrow
          │           │           │
       transfer    implicit       │
                                  │
                           ┌──────┴──────┐
                           │             │
                          &T           &mut T
                           │             │
                         READ       READ + WRITE
```

Đây là nền tảng để bạn bước vào phần khó hơn.

---

# 59. Điều cần thuộc lòng

### `&T`

```text
shared / immutable borrow
```

Có thể có:

```text
&T
&T
&T
```

---

### `&mut T`

```text
exclusive / mutable borrow
```

Tại một thời điểm:

```text
&mut T
```

không được đồng thời overlap với immutable references đang được sử dụng.

---

### `&mut T` không lấy ownership

```rust
fn update(x: &mut T)
```

caller vẫn là owner.

---

### Muốn mutate qua reference

Dùng:

```rust
*r = value;
```

hoặc gọi các method mutable trên `r`.

---

# 60. Roadmap tiếp theo

```text
✓ Buổi 21 — Ownership
✓ Buổi 22 — Move
✓ Buổi 23 — Clone
✓ Buổi 24 — Copy
✓ Buổi 25 — Borrow
✓ Buổi 26 — Mutable Borrow      ← hôm nay
→ Buổi 27 — Slice
  Buổi 28 — String
  Buổi 29 — String vs &str
  Buổi 30 — Ownership Deep Dive
```

**Buổi 27 — Slice** sẽ nối trực tiếp với Borrow: chúng ta sẽ học `&[T]`, `&str`, range `..`, `..=`, slice của `String`/`Vec`, vì sao API nên dùng `&[T]` thay cho `&Vec<T>`, và xây dựng các function generic trên slice.
