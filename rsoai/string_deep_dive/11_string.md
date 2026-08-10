# Rust String Deep Dive — Phần II

# Buổi 11 — `String` là gì?

Hôm nay chúng ta chuyển từ:

```text
"hello"
&str
str
```

sang một khái niệm cực kỳ quan trọng:

```rust
String
```

Nếu `&str` là **borrowed string slice**, thì `String` là **owned, growable UTF-8 string**.

---

# 1. `String` là gì?

Định nghĩa ngắn gọn:

> `String` là một kiểu dữ liệu sở hữu một vùng nhớ chứa chuỗi UTF-8 và có thể tăng/giảm kích thước.

Ví dụ:

```rust
fn main() {
    let name = String::from("Rust");

    println!("{name}");
}
```

Type:

```text
name: String
```

Khác với:

```rust
let name = "Rust";
```

có type:

```text
name: &'static str
```

---

# 2. `String` khác `&str` ở đâu?

Đây là kiến thức quan trọng nhất của buổi hôm nay.

```rust
let a = "hello";

let b = String::from("hello");
```

Conceptually:

```text
a
│
│ &str
│
▼
"hello"
(static data)
```

Trong khi:

```text
b
│
│ String
│
▼
heap
┌───────────────┐
│ h e l l o     │
└───────────────┘
```

Ta có:

|                 | `&str`              | `String`  |
| --------------- | ------------------- | --------- |
| Ownership       | Borrowed            | Owned     |
| Growable        | ❌                   | ✅         |
| Heap allocation | Không nhất thiết    | Thường có |
| UTF-8           | ✅                   | ✅         |
| Mutable         | reference phụ thuộc | ✅         |
| Có thể append   | ❌ trực tiếp         | ✅         |
| Có `capacity()` | ❌                   | ✅         |

---

# 3. `String` là owned type

Đây là điểm cốt lõi:

```rust
let name = String::from("Rust");
```

`name` **sở hữu** dữ liệu của chuỗi.

Conceptually:

```text
name
 │
 │ owns
 ▼
heap
┌────────────────┐
│ R u s t        │
└────────────────┘
```

Khi `name` đi ra khỏi scope:

```text
name
 ↓
drop
 ↓
heap memory được giải phóng
```

Đây chính là RAII/resource ownership trong Rust.

---

# 4. `String` có thể thay đổi

Ví dụ:

```rust
fn main() {
    let mut text = String::from("Hello");

    text.push(' ');
    text.push_str("Rust");

    println!("{text}");
}
```

Output:

```text
Hello Rust
```

Điểm quan trọng:

```rust
let mut text
```

vì chúng ta đang mutate `String`.

---

# 5. String literal thì sao?

Bạn không thể làm:

```rust
let text = "Hello";

text.push('!');
```

Vì:

```text
text: &str
```

`&str` không phải owned growable string.

Muốn thay đổi:

```rust
let mut text = String::from("Hello");

text.push('!');
```

---

# 6. Tại sao `String` có thể grow?

Bên trong `String` quản lý một vùng nhớ động.

Conceptually:

```text
String
┌───────────────┐
│ ptr           │ ──────────┐
│ len           │           │
│ capacity      │           ▼
└───────────────┘       heap
                     ┌───────────────┐
                     │ H e l l o     │
                     └───────────────┘
```

Ba thông tin quan trọng:

```text
ptr
len
capacity
```

Chúng ta sẽ đào rất sâu vào ba thành phần này ở các buổi sau.

---

# 7. `len` là gì?

Ví dụ:

```rust
let s = String::from("Hello");
```

Ta có:

```rust
s.len()
```

kết quả:

```text
5
```

Vì:

```text
H = 1 byte
e = 1
l = 1
l = 1
o = 1
```

Tổng:

```text
5 bytes
```

---

# 8. Nhưng `len()` không phải số ký tự

Đây là lỗi rất phổ biến.

```rust
let s = String::from("Xin chào");

println!("{}", s.len());
```

Không nên suy nghĩ:

```text
"Xin chào" = 7 characters
```

mà:

```text
len() = số bytes UTF-8
```

Ví dụ:

```rust
let s = String::from("你好");

println!("{}", s.len());
```

Mỗi ký tự Trung Quốc thường chiếm 3 bytes UTF-8.

Vì vậy:

```text
len() = 6
```

chứ không phải:

```text
2
```

---

# 9. `String` luôn chứa UTF-8 hợp lệ

Rust `String` đảm bảo dữ liệu bên trong là:

```text
valid UTF-8
```

Ví dụ:

```rust
let s = String::from("Hello");
let s = String::from("Xin chào");
let s = String::from("你好");
let s = String::from("🦀");
```

Tất cả đều hợp lệ.

---

# 10. Vì sao Rust yêu cầu UTF-8?

Rust thiết kế `String` dựa trên UTF-8 để:

* hỗ trợ Unicode
* tương thích tốt với text quốc tế
* biểu diễn ASCII hiệu quả
* tránh trạng thái String chứa UTF-8 không hợp lệ

Ví dụ ASCII:

```text
A → 1 byte
B → 1 byte
C → 1 byte
```

Unicode:

```text
é → nhiều byte tùy biểu diễn
你 → 3 bytes
🦀 → 4 bytes
```

---

# 11. `String` và `Vec<u8>`

Đây là một connection cực kỳ quan trọng.

Có thể hình dung:

```text
String
   │
   ▼
UTF-8 bytes
   │
   ▼
Vec<u8>-like storage
```

Thực tế `String` được implement dựa trên cơ chế tương tự `Vec<u8>`.

Bạn có thể chuyển:

```rust
let s = String::from("Hello");

let bytes = s.into_bytes();
```

Type:

```text
Vec<u8>
```

---

# 12. Ví dụ

```rust
fn main() {
    let text = String::from("Rust");

    let bytes = text.into_bytes();

    println!("{bytes:?}");
}
```

Output:

```text
[82, 117, 115, 116]
```

Vì:

```text
R → 82
u → 117
s → 115
t → 116
```

---

# 13. `into_bytes()` làm gì với ownership?

Đây là:

```rust
let text = String::from("Rust");

let bytes = text.into_bytes();
```

Sau đó:

```rust
println!("{text}");
```

sẽ không compile.

Tại sao?

Vì:

```text
text
 ↓
into_bytes()
 ↓
ownership chuyển sang Vec<u8>
```

Conceptually:

```text
String
   │
   │ move
   ▼
Vec<u8>
```

Không cần copy toàn bộ dữ liệu.

---

# 14. `String` có thể convert sang `&str`

Bạn có:

```rust
let text = String::from("Hello");
```

Có thể:

```rust
let slice: &str = &text;
```

Conceptually:

```text
text: String
   │
   │ borrow
   ▼
slice: &str
```

`slice` không sở hữu dữ liệu.

---

# 15. Đây là pattern cực kỳ phổ biến

```rust
fn print_text(text: &str) {
    println!("{text}");
}

fn main() {
    let text = String::from("Hello Rust");

    print_text(&text);
}
```

Function nhận:

```text
&str
```

nhưng chúng ta truyền:

```text
&String
```

Rust cho phép coercion:

```text
&String
   ↓
&str
```

---

# 16. Tại sao API thường dùng `&str`?

Giả sử:

```rust
fn print_text(text: &str) {
    println!("{text}");
}
```

Function này nhận được cả:

```rust
print_text("Hello");
```

và:

```rust
let s = String::from("Hello");
print_text(&s);
```

Nhưng nếu viết:

```rust
fn print_text(text: &String) {
    println!("{text}");
}
```

thì API kém linh hoạt hơn.

Không thể trực tiếp:

```rust
print_text("Hello");
```

theo cách thông thường.

Vì vậy:

> Nếu function chỉ cần đọc string, thường ưu tiên `&str`.

---

# 17. `String` có thể mutable

```rust
let mut text = String::from("Hello");

text.push('!');
```

Nhưng:

```rust
let text = String::from("Hello");

text.push('!');
```

không compile.

Vì binding không mutable.

---

# 18. `mut` thuộc về binding

Điều này rất quan trọng:

```rust
let mut text = String::from("Hello");
```

Không có nghĩa:

```text
String luôn mutable
```

Mà:

```text
binding `text` cho phép mutable access
```

Rust phân biệt:

```text
ownership
mutability
borrowing
```

---

# 19. `String` có thể thay đổi kích thước

Ví dụ:

```rust
let mut s = String::from("Hi");

s.push('!');

println!("{s}");
```

Ban đầu:

```text
Hi
```

Sau:

```text
Hi!
```

Đây là lý do `String` được gọi là:

> growable string

---

# 20. `String` không phải fixed-size array

So sánh:

```rust
let bytes = [1, 2, 3];
```

với:

```rust
let mut s = String::from("abc");
```

Array:

```text
size cố định
```

String:

```text
size có thể thay đổi
```

---

# 21. `String` có `capacity`

Ví dụ:

```rust
let mut s = String::new();

println!("{}", s.len());
println!("{}", s.capacity());
```

Ban đầu có thể:

```text
len      = 0
capacity = 0
```

Sau:

```rust
s.push_str("Hello");
```

ta có:

```text
len      = 5
capacity >= 5
```

**Lưu ý:** capacity chính xác bao nhiêu phụ thuộc implementation/growth strategy; đừng hard-code giả định về mức tăng.

---

# 22. `len` vs `capacity`

Ví dụ:

```rust
let mut s = String::with_capacity(100);
```

Conceptually:

```text
len      = 0
capacity = 100
```

Sau:

```rust
s.push_str("Hello");
```

thì:

```text
len      = 5
capacity = 100
```

Không cần allocation mới nếu vẫn còn đủ capacity.

---

# 23. Tại sao capacity quan trọng?

Nếu bạn append rất nhiều:

```rust
let mut s = String::new();

for _ in 0..1_000 {
    s.push_str("hello");
}
```

String có thể phải reallocate nhiều lần khi capacity không đủ.

Bạn có thể dự trù:

```rust
let mut s = String::with_capacity(5_000);
```

Sau đó append.

Điều này có thể giảm số lần reallocation.

---

# 24. `String::new()`

Cách tạo String rỗng:

```rust
let s = String::new();
```

Type:

```text
String
```

Ví dụ:

```rust
fn main() {
    let mut text = String::new();

    text.push_str("Hello");
    text.push(' ');

    println!("{text}");
}
```

---

# 25. `String::from()`

Cách phổ biến:

```rust
let s = String::from("Hello");
```

Đây là conversion:

```text
&str
 ↓
String
```

Ví dụ:

```rust
let a = "Hello";
let b = String::from(a);
```

---

# 26. `.to_string()`

Bạn cũng có:

```rust
let s = "Hello".to_string();
```

Kết quả:

```text
String
```

Nghĩa conceptually:

```text
&str
 ↓
String
```

Chúng ta sẽ học kỹ `String::from` và `to_string()` ở Buổi 12–13.

---

# 27. `String::from` không chỉ nhận literal

Ví dụ:

```rust
let a = "Hello";

let b = String::from(a);
```

Ở đây:

```text
a: &str
b: String
```

Hoặc:

```rust
let b = String::from("Hello");
```

---

# 28. `String` có thể concatenate

Ví dụ:

```rust
let mut s = String::from("Hello");

s.push_str(" Rust");
```

Kết quả:

```text
Hello Rust
```

Đây là một trong những use case quan trọng nhất của `String`.

---

# 29. `String` ownership

Xem:

```rust
fn main() {
    let s = String::from("Hello");

    let x = s;

    println!("{x}");
}
```

Hợp lệ.

Nhưng:

```rust
println!("{s}");
```

sẽ lỗi.

Vì:

```text
s
 ↓ move
x
```

`String` không implement `Copy`.

---

# 30. Tại sao `String` không `Copy`?

Giả sử:

```text
String
 ├── pointer
 ├── length
 └── capacity
```

Nếu copy bằng bitwise:

```text
s1
 ├── ptr ───► heap
 ├── len
 └── capacity

s2
 ├── ptr ───► same heap
 ├── len
 └── capacity
```

Hai `String` cùng sở hữu một allocation.

Khi cả hai drop:

```text
s1 → free
s2 → free again
```

→ double free.

Rust giải quyết bằng ownership + move.

---

# 31. `clone()` nếu thực sự muốn copy

```rust
let s1 = String::from("Hello");

let s2 = s1.clone();

println!("{s1}");
println!("{s2}");
```

Conceptually:

```text
s1 ─────► heap A
          "Hello"

s2 ─────► heap B
          "Hello"
```

Hai allocation độc lập.

---

# 32. `String` và scope

```rust
fn main() {
    {
        let s = String::from("Hello");

        println!("{s}");
    }

    // s không còn tồn tại
}
```

Khi scope kết thúc:

```text
s
 ↓
drop
 ↓
heap memory released
```

Không cần:

```text
free(s)
```

Không cần garbage collector.

---

# 33. `Drop`

`String` implement `Drop`.

Conceptually:

```text
scope ends
     ↓
String::drop()
     ↓
heap memory released
```

Đây là một phần cực kỳ quan trọng của ownership model.

---

# 34. `String` không chỉ là text

Ở mức abstraction:

```text
String
=
owned UTF-8 byte buffer
```

Đây là mental model rất tốt.

Không nên nghĩ:

```text
String = array of characters
```

Mà nên nghĩ:

```text
String = owned UTF-8 bytes
```

---

# 35. Vì vậy không thể indexing như array

Bạn có thể:

```rust
let numbers = [10, 20, 30];

println!("{}", numbers[0]);
```

Nhưng không thể:

```rust
let s = String::from("Hello");

println!("{}", s[0]);
```

Rust không cho phép String indexing trực tiếp bằng integer.

Lý do sâu hơn nằm ở UTF-8.

Chúng ta sẽ mổ xẻ vấn đề này ở **Phần IV — UTF-8 Deep Dive**.

---

# 36. Một ký tự có thể nhiều bytes

Ví dụ:

```rust
let s = String::from("🦀");
```

Có thể hình dung:

```text
🦀
 ↓
4 UTF-8 bytes
```

Nếu String hỗ trợ:

```rust
s[0]
```

thì câu hỏi:

```text
s[0] = byte?
hay
s[0] = char?
```

Không có câu trả lời đơn giản mà không làm rõ semantics.

Vì vậy Rust không cho indexing String trực tiếp.

---

# 37. `String` và Unicode

```rust
let s = String::from("Xin chào 🌍");
```

String vẫn là:

```text
valid UTF-8
```

Nhưng:

```rust
s.len()
```

là byte length.

Nếu muốn iterate Unicode scalar values:

```rust
for c in s.chars() {
    println!("{c}");
}
```

---

# 38. `String` có thể chuyển thành bytes

```rust
let s = String::from("Rust");

let bytes = s.as_bytes();
```

Type:

```text
&[u8]
```

Đây là borrow, không consume `s`.

Sau đó vẫn có thể:

```rust
println!("{s}");
```

---

# 39. `as_bytes()` vs `into_bytes()`

Đây là distinction rất quan trọng:

### `as_bytes()`

```rust
let s = String::from("Rust");

let bytes = s.as_bytes();
```

Type:

```text
&[u8]
```

Không lấy ownership.

### `into_bytes()`

```rust
let s = String::from("Rust");

let bytes = s.into_bytes();
```

Type:

```text
Vec<u8>
```

Ownership chuyển đi.

---

# 40. Mental model

Hãy nhớ:

```text
String
│
├── owns
│
├── UTF-8 bytes
│
├── growable
│
├── heap-backed storage
│
├── len
│
├── capacity
│
└── ownership-aware
```

Trong khi:

```text
&str
│
├── borrows
├── UTF-8 bytes
├── unsized
└── không sở hữu data
```

---

# 41. Ví dụ tổng hợp

```rust
fn show(text: &str) {
    println!("text = {text}");
    println!("bytes = {}", text.len());
}

fn main() {
    let mut text = String::from("Hello");

    text.push(' ');
    text.push_str("Rust");

    show(&text);
}
```

Output:

```text
text = Hello Rust
bytes = 10
```

Flow:

```text
"Hello"
   ↓
String::from
   ↓
String
   ↓
push
   ↓
push_str
   ↓
&String
   ↓
coerce
   ↓
&str
   ↓
show()
```

---

# 42. Một ví dụ ownership hoàn chỉnh

```rust
fn create_message() -> String {
    let mut message = String::from("Hello");

    message.push_str(" Rust");

    message
}

fn print_message(message: &str) {
    println!("{message}");
}

fn main() {
    let message = create_message();

    print_message(&message);

    println!("{message}");
}
```

Flow:

```text
create_message()
       │
       ▼
   String owned
       │
       │ return ownership
       ▼
     main
       │
       │ borrow
       ▼
     &str
       │
       ▼
 print_message()
```

Đây là pattern cực kỳ phổ biến trong Rust.

---

# 43. Pattern API nên ghi nhớ

Nếu function **tạo dữ liệu mới**:

```rust
fn create_name() -> String
```

Nếu function **chỉ đọc dữ liệu**:

```rust
fn print_name(name: &str)
```

Nếu function **cần sửa String mà caller sở hữu**:

```rust
fn normalize(name: &mut String)
```

Nếu function **cần nhận ownership**:

```rust
fn consume(name: String)
```

Đây chính là tư duy ownership-driven API design.

---

# 44. Bài tập

## Bài 1

Cho:

```rust
let a = "Rust";
let b = String::from("Rust");
```

Hãy giải thích:

```text
type của a?
type của b?
ai sở hữu data?
data nằm ở đâu?
a có grow được không?
b có grow được không?
```

---

## Bài 2

Viết chương trình:

```text
String ban đầu:
"Rust"

append:
" is"

append:
" awesome"
```

Kết quả:

```text
Rust is awesome
```

Sử dụng:

```rust
push()
push_str()
```

---

## Bài 3

Dự đoán output:

```rust
fn main() {
    let mut s = String::from("abc");

    println!("{}", s.len());

    s.push('d');

    println!("{}", s.len());
}
```

---

## Bài 4

Giải thích tại sao:

```rust
let s = String::from("Hello");

let x = s;

println!("{s}");
```

không compile.

Sau đó sửa bằng hai cách:

```text
1. move có chủ đích
2. clone
```

---

## Bài 5 — Memory

Vẽ memory model cho:

```rust
let s = String::from("Hello");
```

Phải thể hiện:

```text
stack
 ├── pointer
 ├── len
 └── capacity

heap
 └── UTF-8 bytes
```

---

## Bài 6 — API

Viết ba function:

```rust
fn create_message() -> String
```

```rust
fn print_message(message: &str)
```

```rust
fn append_world(message: &mut String)
```

Sau đó sử dụng cả ba trong `main()`.

---

# 45. Kiến thức cần thuộc sau Buổi 11

Nếu chỉ nhớ **10 điều**, hãy nhớ:

```text
1. String là owned string.
2. String chứa UTF-8.
3. String có thể grow.
4. String thường dùng heap allocation.
5. String quản lý ptr + len + capacity.
6. String không implement Copy.
7. String được drop khi owner ra khỏi scope.
8. &str là borrowed string slice.
9. &String thường có thể coerce thành &str.
10. String ≈ owned UTF-8 byte buffer.
```

Mental model quan trọng nhất:

```text
              String
                │
          owns UTF-8 data
                │
       ┌────────┴────────┐
       ▼                 ▼
     stack              heap
   ptr/len/cap        UTF-8 bytes
       │
       └────── owns ─────┘
```

**Buổi 12 tiếp theo: `String::from` — từ `&str` → `String`, allocation thực sự xảy ra thế nào, `From` trait hoạt động ra sao, và so sánh sâu `String::from()` với `.to_string()`.**
