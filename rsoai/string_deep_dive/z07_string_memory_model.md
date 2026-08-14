# Rust String Deep Dive — Buổi 7

## String Memory Model — `String` vs `&str` từ Stack → Heap → Pointer → Length → Capacity

Buổi này là một trong những buổi **quan trọng nhất của toàn bộ phần String**.

Nếu hiểu rõ buổi này, bạn sẽ không còn học Rust String theo kiểu thuộc lòng:

```rust
String
&str
to_string()
as_str()
```

mà sẽ hiểu **vì sao chúng hoạt động như vậy**.

---

# 1. Câu hỏi trung tâm của Buổi 7

Hãy nhìn:

```rust
let s1 = "Hello";
let s2 = String::from("Hello");
```

Hai biến đều chứa:

```text
Hello
```

Nhưng chúng **không giống nhau**.

Ta cần trả lời:

```text
1. "Hello" nằm ở đâu?
2. s1 thực chất là gì?
3. String::from("Hello") tạo ra gì?
4. Heap nằm ở đâu?
5. &str chứa gì?
6. String chứa gì?
7. Vì sao String có thể push()?
8. Vì sao &str không thể push()?
9. capacity là gì?
10. String::from() và &str liên quan thế nào?
```

---

# 2. Trước hết: `str` là gì?

Trong Rust:

```rust
str
```

là **string slice type**.

Nhưng bạn gần như không viết:

```rust
let x: str;
```

bởi vì `str` là **dynamically sized type — DST**.

Thay vào đó ta sử dụng:

```rust
&str
```

Tức:

```text
str
 ↑
borrowed view
```

---

# 3. `&str` là một fat pointer

Đây là khái niệm cực kỳ quan trọng.

Một `&str` về mặt conceptual gồm:

```text
pointer
+
length
```

Ví dụ:

```rust
let s = "Hello";
```

Khi dùng:

```rust
s
```

ta có thể hình dung:

```text
&str
┌──────────────────────┐
│ pointer              │ ───────┐
│ length = 5           │        │
└──────────────────────┘        │
                                ▼
                        H e l l o
```

Tức:

```text
&str = (pointer, length)
```

---

# 4. Tại sao cần length?

Một pointer đơn thuần:

```text
pointer → H e l l o
```

không biết string kết thúc ở đâu.

Rust không dùng:

```text
\0
```

để kết thúc string.

Vì vậy `&str` cần:

```text
pointer
length
```

Ví dụ:

```text
pointer → H e l l o
length  → 5
```

Rust biết chính xác:

```text
5 bytes
```

---

# 5. Đây là lý do Rust String không cần null terminator

C:

```text
char*
 ↓
H e l l o \0
```

Rust:

```text
&str
 ↓
pointer + length
```

Ví dụ:

```text
┌──────────────┐
│ pointer      │─────→ H e l l o
│ length = 5   │
└──────────────┘
```

Do đó:

```rust
let s = "hello\0world";
```

hoàn toàn hợp lệ.

Rust biết string dài bao nhiêu nhờ length.

---

# 6. `len()` trả về gì?

Đây là điểm rất quan trọng:

```rust
let s = "Hello";
println!("{}", s.len());
```

Kết quả:

```text
5
```

Nhưng:

```rust
let s = "Xin chào";
```

thì:

```rust
println!("{}", s.len());
```

không phải số ký tự theo cách con người thường nghĩ.

Nó là:

> **số byte UTF-8**

---

# 7. Ví dụ Unicode

```rust
let s = "é";
```

`é` trong UTF-8:

```text
C3 A9
```

2 bytes.

Do đó:

```rust
assert_eq!(s.len(), 2);
```

nhưng:

```rust
assert_eq!(s.chars().count(), 1);
```

Ta có:

```text
bytes = 2
chars = 1
```

---

# 8. `&str` không chứa UTF-8 bytes trực tiếp trong chính nó

Đây là distinction quan trọng.

```rust
let s = "Hello";
```

`&str` conceptual:

```text
┌────────────────────┐
│ pointer            │ ─────→ H e l l o
│ length = 5         │
└────────────────────┘
```

Các bytes nằm ở nơi mà pointer trỏ tới.

`&str` chỉ là **view** vào dữ liệu.

---

# 9. String literal nằm ở đâu?

Ví dụ:

```rust
let s = "Hello";
```

`"Hello"` là **string literal**.

Nó có lifetime:

```text
'static
```

và thường được lưu trong binary/program image.

Conceptual:

```text
Program binary
┌──────────────────────┐
│ machine code         │
│ constants            │
│ "Hello"              │
└──────────────────────┘
          ▲
          │
          │ pointer
          │
        &str
```

Vì vậy:

```rust
let s: &'static str = "Hello";
```

là hợp lệ.

---

# 10. `'static` ở đây nghĩa gì?

```rust
let s = "Hello";
```

String literal sống trong suốt thời gian chương trình chạy.

Do đó:

```rust
let s: &'static str = "Hello";
```

hợp lệ.

Nhưng cần nhớ:

> `'static` nói về lifetime, không phải nói rằng dữ liệu nằm trên stack.

Đây là hai khái niệm khác nhau.

---

# 11. Bây giờ đến `String`

```rust
let s = String::from("Hello");
```

`String` khác `&str`.

Conceptual:

```text
String
┌───────────────────────┐
│ pointer               │─────┐
│ length = 5            │     │
│ capacity = 5          │     │
└───────────────────────┘     │
                              ▼
                            HEAP
                       ┌─────────────┐
                       │ H e l l o   │
                       └─────────────┘
```

---

# 12. String gồm 3 thành phần

Ở mức conceptual, `String` có:

```text
pointer
length
capacity
```

Tức:

```text
String
┌────────────────────┐
│ ptr                │
│ len                │
│ capacity           │
└────────────────────┘
```

Dữ liệu thực tế nằm trên heap.

---

# 13. `length` vs `capacity`

Đây là hai khái niệm rất quan trọng.

Ví dụ:

```rust
let mut s = String::from("Hello");
```

Ta có thể hình dung:

```text
length   = 5
capacity = 5
```

Nhưng sau:

```rust
s.push('!');
```

có thể:

```text
length   = 6
capacity = 8
```

hoặc một capacity khác tùy implementation.

Điểm quan trọng:

```text
length ≤ capacity
```

---

# 14. Capacity là gì?

`capacity` là số byte mà `String` đã cấp phát trên heap để có thể sử dụng.

Ví dụ:

```text
capacity = 10
length   = 5
```

Heap:

```text
┌──────────────────────────────┐
│ H e l l o _ _ _ _ _          │
└──────────────────────────────┘
  ←── length 5 ──→
  ←──── capacity 10 ──────────→
```

5 bytes đang được sử dụng.

5 bytes còn lại có thể dùng cho dữ liệu mới.

---

# 15. Kiểm tra capacity

```rust
fn main() {
    let s = String::from("Hello");

    println!("len = {}", s.len());
    println!("capacity = {}", s.capacity());
}
```

Bạn sẽ thấy capacity ít nhất đủ chứa 5 bytes.

Nhưng:

> Không nên phụ thuộc vào một con số capacity cụ thể nếu bạn không tự chỉ định capacity.

Implementation có thể thay đổi.

---

# 16. `String` có thể grow vì có capacity

Ví dụ:

```rust
let mut s = String::from("Hello");

s.push('!');
```

Rust có thể ghi thêm:

```text
Hello!
```

vào phần memory đã allocate.

Nếu capacity không đủ:

```text
old heap
    ↓
allocate new region
    ↓
copy/move data
    ↓
free old region
```

Conceptual:

```text
old:
┌─────────┐
│ Hello   │
└─────────┘

        ↓ capacity không đủ

new:
┌─────────────────┐
│ Hello!          │
└─────────────────┘
```

---

# 17. Vì sao `&str` không có capacity?

Bởi vì `&str` **không sở hữu buffer**.

Nó chỉ borrow một vùng text đã tồn tại.

Ví dụ:

```rust
let s = String::from("Hello");
let slice = &s[..];
```

Ta có:

```text
String
┌─────────────────┐
│ ptr             │──────┐
│ len             │      │
│ capacity        │      │
└─────────────────┘      │
                         ▼
                       HEAP
                    ┌─────────┐
                    │ Hello   │
                    └─────────┘
                         ▲
                         │
                     &str
                    ┌─────────┐
                    │ ptr     │
                    │ len     │
                    └─────────┘
```

`&str` không cần capacity.

---

# 18. `&str` chỉ biết phần nó nhìn thấy

Ví dụ:

```rust
let s = String::from("Hello World");

let part = &s[0..5];
```

Ta có:

```text
String
       ↓
Hello World
│────────────│
│
└── &str → Hello
```

`&str` biết:

```text
pointer → H
length  = 5
```

Nó không cần biết `String` có:

```text
capacity = 20
```

---

# 19. Đây chính là "slice"

`&str` là một dạng slice.

Ví dụ:

```rust
let s = String::from("Hello World");

let a = &s[0..5];
let b = &s[6..11];
```

Ta có:

```text
String buffer:

H e l l o   W o r l d
│─────────│
    a

            │─────────│
                 b
```

Cả `a` và `b` đều borrow cùng một buffer.

Không copy string.

---

# 20. Đây là lý do `&str` hiệu quả

Ví dụ:

```rust
fn print_text(s: &str) {
    println!("{s}");
}
```

Bạn có thể truyền:

```rust
let a = "Hello";
let b = String::from("World");

print_text(a);
print_text(&b);
```

Không cần copy nội dung.

---

# 21. `String` → `&str`

Đây là conversion cực kỳ quan trọng:

```rust
let s = String::from("Hello");

let slice: &str = &s;
```

Hoặc:

```rust
let slice = s.as_str();
```

Hai cách phổ biến:

```rust
&s
```

và:

```rust
s.as_str()
```

---

# 22. Vì sao `&s` hoạt động?

`String` implement `Deref<Target = str>`.

Conceptually:

```text
String
   │
   │ Deref
   ▼
str
```

Do đó Rust có thể tự động coerce:

```rust
let s = String::from("Hello");

foo(&s);
```

nếu:

```rust
fn foo(value: &str) {}
```

---

# 23. Deref coercion

Ví dụ:

```rust
fn print_text(s: &str) {
    println!("{s}");
}

fn main() {
    let s = String::from("Hello");

    print_text(&s);
}
```

Bạn không cần:

```rust
print_text(s.as_str());
```

Rust tự thực hiện coercion:

```text
&String
   ↓
&str
```

---

# 24. Đây là một trong những lý do API Rust thường dùng `&str`

Nếu function chỉ cần đọc text:

```rust
fn greet(name: &str) {
    println!("Hello {name}");
}
```

thì không cần:

```rust
fn greet(name: String)
```

vì `String` yêu cầu ownership.

`&str` linh hoạt hơn.

Bạn có thể truyền:

```rust
"Rust"
```

hoặc:

```rust
String::from("Rust")
```

---

# 25. `String` → `&str` không copy

Ví dụ:

```rust
let s = String::from("Hello");
let view = &s;
```

Không có:

```text
copy Hello
```

Thay vào đó:

```text
s
 │
 ▼
HEAP: Hello
 ▲
 │
view
```

`view` chỉ borrow.

---

# 26. `&str` → `String`

Chiều ngược lại cần tạo ownership:

```rust
let s: &str = "Hello";

let owned = s.to_string();
```

hoặc:

```rust
let owned = String::from(s);
```

Lúc này Rust phải tạo một `String` mới.

Conceptual:

```text
&str
 │
 │ copy bytes
 ▼
heap allocation
 │
 ▼
String
```

---

# 27. Đây là điểm cần phân biệt

```rust
let a = String::from("Hello");
let b = &a;
```

→ không copy.

Nhưng:

```rust
let a = "Hello";
let b = a.to_string();
```

→ tạo owned String.

Mental model:

```text
String → &str
    ↓
borrow

&str → String
    ↓
allocate + own
```

---

# 28. Ownership

`String` sở hữu dữ liệu.

```rust
let s = String::from("Hello");
```

`String` là owner của heap buffer.

Khi:

```rust
drop(s);
```

buffer được giải phóng.

---

# 29. `&str` không sở hữu dữ liệu

```rust
let s = String::from("Hello");
let view = &s;
```

`view` không sở hữu:

```text
Hello
```

Owner vẫn là:

```text
s
```

Do đó:

```text
s
 ↓
owns heap

view
 ↓
borrows heap
```

---

# 30. Ownership diagram

```text
STACK

s
┌──────────────────────┐
│ ptr ───────────────┐ │
│ len = 5            │ │
│ cap = 5            │ │
└────────────────────┼─┘
                     │
                     ▼
HEAP
┌──────────────────────┐
│ H e l l o            │
└──────────────────────┘
          ▲
          │
          │
view      │
┌─────────┴────────────┐
│ ptr                  │
│ len = 5              │
└──────────────────────┘
```

---

# 31. Move của `String`

```rust
let s1 = String::from("Hello");
let s2 = s1;
```

Điều gì xảy ra?

Không phải copy toàn bộ `"Hello"`.

Conceptually:

```text
s1
 ↓
┌──────────────┐
│ ptr          │
│ len          │
│ capacity     │
└──────────────┘
```

sau:

```rust
let s2 = s1;
```

ownership của descriptor được move:

```text
s1 → invalid
s2 → owner
```

Heap data vẫn là một buffer.

---

# 32. Vì sao Rust không double free?

Nếu:

```text
s1
```

và:

```text
s2
```

cùng sở hữu cùng heap buffer, khi cả hai drop:

```text
double free
```

sẽ xảy ra.

Rust giải quyết bằng ownership:

```text
s1
 ↓ move
s2
```

Sau move:

```text
s1 = unusable
```

---

# 33. `String` và stack

Đây là điểm thường bị hiểu sai.

Người ta hay nói:

> String nằm trên heap.

Không chính xác hoàn toàn.

`String` object/descriptor nằm ở nơi variable được lưu, thường là stack nếu local variable.

Heap chứa:

```text
actual bytes
```

Ví dụ:

```text
STACK
┌─────────────────────┐
│ String              │
│ ptr                 │
│ len                 │
│ capacity            │
└─────────┬───────────┘
          │
          ▼
HEAP
┌─────────────────────┐
│ actual UTF-8 bytes  │
└─────────────────────┘
```

---

# 34. `&str` cũng có descriptor

Local:

```rust
let s = "Hello";
```

conceptually:

```text
STACK
┌────────────────────┐
│ pointer            │
│ length             │
└─────────┬──────────┘
          │
          ▼
STATIC DATA
┌────────────────────┐
│ Hello              │
└────────────────────┘
```

Không có heap allocation mới cho literal.

---

# 35. `String::from("Hello")`

Quá trình conceptually:

```text
"Hello"
    │
    │ read literal
    ▼
allocate heap
    │
    ▼
copy UTF-8 bytes
    │
    ▼
String
```

Ta có:

```text
STACK
String descriptor
      │
      ▼
HEAP
Hello
```

---

# 36. `String::with_capacity`

Nếu biết trước cần bao nhiêu bytes:

```rust
let mut s = String::with_capacity(100);
```

Rust cấp phát capacity khoảng:

```text
100 bytes
```

ngay từ đầu.

Sau đó:

```rust
s.push_str("Hello");
```

không nhất thiết phải reallocate.

---

# 37. Tại sao capacity quan trọng?

Ví dụ bạn tạo string lớn:

```rust
let mut s = String::new();

for i in 0..1_000_000 {
    s.push_str(&i.to_string());
}
```

String sẽ nhiều lần grow.

Nếu biết trước kích thước gần đúng:

```rust
let mut s = String::with_capacity(10_000_000);
```

có thể giảm số lần allocation/reallocation.

---

# 38. `len()` và `capacity()`

Ví dụ:

```rust
let mut s = String::with_capacity(100);

println!("{}", s.len());
println!("{}", s.capacity());
```

Ban đầu:

```text
len = 0
capacity = 100
```

Sau:

```rust
s.push_str("Hello");
```

có:

```text
len = 5
capacity = 100
```

Conceptual:

```text
┌──────────────────────────────────────────┐
│ H e l l o _ _ _ _ _ _ _ _ _ _ _ ...      │
└──────────────────────────────────────────┘
←──── 5 ────→
←──────────── 100 ────────────────────────→
```

---

# 39. Capacity không phải length

Đừng nhầm:

```text
length = dữ liệu đang sử dụng
capacity = bộ nhớ đã cấp phát
```

Invariant:

```text
0 <= length <= capacity
```

---

# 40. UTF-8 khiến capacity cũng tính byte

Ví dụ:

```rust
let mut s = String::with_capacity(10);
s.push_str("é");
```

`é` cần:

```text
2 bytes
```

nên:

```text
len = 2
```

không phải:

```text
len = 1
```

Capacity:

```text
10 bytes
```

---

# 41. `push()` vs `push_str()`

`String` có:

```rust
push(char)
```

và:

```rust
push_str(&str)
```

Ví dụ:

```rust
let mut s = String::from("Hello");

s.push('!');
s.push_str(" Rust");
```

Kết quả:

```text
Hello! Rust
```

---

# 42. Tại sao `push()` nhận `char`?

```rust
s.push('é');
```

`push()` nhận một Unicode scalar value.

Trong khi:

```rust
s.push_str("é");
```

nhận một string slice.

Do đó:

```text
push
 ↓
char

push_str
 ↓
&str
```

---

# 43. `String` có thể mutate

```rust
let mut s = String::from("Hello");

s.push('!');
```

Tại sao?

Vì:

```text
String
 ↓
owns buffer
 ↓
có capacity
 ↓
có thể thay đổi nội dung
```

---

# 44. `&str` không mutate

```rust
let s = "Hello";
```

Bạn không thể:

```rust
s.push('!');
```

Vì:

```text
&str
 ↓
borrowed view
 ↓
không có ownership/capacity
```

Ngay cả:

```rust
let mut s = "Hello";
```

cũng không làm `&str` thành growable string.

`mut` chỉ cho phép thay đổi binding, không biến `&str` thành `String`.

---

# 45. Ví dụ quan trọng

```rust
let mut s = "Hello";

s = "World";
```

Điều này có thể hợp lệ.

Nhưng:

```rust
s.push('!');
```

không hợp lệ.

Vì `s` vẫn là:

```text
&str
```

`mut` ở đây nghĩa:

```text
binding có thể được gán lại
```

không phải:

```text
string content có thể grow
```

---

# 46. `mut` vs mutability của dữ liệu

So sánh:

```rust
let mut a = String::from("Hello");
a.push('!');
```

với:

```rust
let mut b = "Hello";
b = "World";
```

### `a`

```text
mut String
→ mutate owned buffer
```

### `b`

```text
mut &str
→ thay đổi reference/value mà binding trỏ tới
```

Không phải mutate literal.

---

# 47. `String` không phải `str`

Đừng nghĩ:

```text
String = mutable str
```

Không chính xác.

Có thể hình dung:

```text
str
 ↓
text data type

&str
 ↓
borrowed view

String
 ↓
owned growable UTF-8 buffer
```

---

# 48. Bảng so sánh

|             | `String`                 | `&str`                  |
| ----------- | ------------------------ | ----------------------- |
| Ownership   | Có                       | Không                   |
| Heap buffer | Có thể có                | Không sở hữu            |
| Grow        | Có                       | Không                   |
| Mutate      | Có                       | Không qua shared `&str` |
| Capacity    | Có                       | Không                   |
| Length      | Có                       | Có                      |
| UTF-8       | Có                       | Có                      |
| Borrow      | Có thể borrow            | Đã là borrow            |
| Literal     | Không phải literal       | Literal mặc định        |
| Cost        | allocation có thể xảy ra | thường chỉ là view      |

---

# 49. `String` có thể borrow thành `&str`

```rust
let name = String::from("Rust");

let view: &str = &name;
```

Flow:

```text
String
   │
   │ borrow
   ▼
&str
```

---

# 50. `&str` có thể tạo `String`

```rust
let view = "Rust";

let name = view.to_owned();
```

hoặc:

```rust
let name = view.to_string();
```

Flow:

```text
&str
   │
   │ allocate/copy
   ▼
String
```

---

# 51. `to_string()` không phải conversion miễn phí

Ví dụ:

```rust
let s = "Hello";

let owned = s.to_string();
```

Có allocation/copy dữ liệu.

Do đó nếu function chỉ cần đọc:

```rust
fn process(s: &str)
```

thường tốt hơn:

```rust
fn process(s: String)
```

nếu không cần ownership.

---

# 52. API design

Đây là nguyên tắc cực kỳ quan trọng:

Nếu function chỉ **đọc** string:

```rust
fn print_name(name: &str) {
    println!("{name}");
}
```

Nếu function cần **sở hữu** string:

```rust
fn store_name(name: String) {
    // giữ lại name
}
```

Nếu function cần **thay đổi caller's String**:

```rust
fn add_suffix(name: &mut String) {
    name.push_str("_user");
}
```

Ba trường hợp:

```text
read
 ↓
&str

own
 ↓
String

mutate
 ↓
&mut String
```

---

# 53. `&mut String`

Ví dụ:

```rust
fn add_exclamation(s: &mut String) {
    s.push('!');
}

fn main() {
    let mut text = String::from("Hello");

    add_exclamation(&mut text);

    println!("{text}");
}
```

Output:

```text
Hello!
```

---

# 54. Tại sao không phải `&mut str`?

`&mut str` tồn tại:

```rust
let s = String::from("Hello");
let slice: &mut str = &mut s[..];
```

nhưng nó rất khác với:

```rust
&mut String
```

`&mut String` cho phép thay đổi growable buffer thông qua `String` API.

`&mut str` là mutable view vào một vùng text có kích thước cố định.

---

# 55. `&mut str` không thể grow

Ví dụ conceptual:

```text
String buffer
┌──────────────────────┐
│ Hello                │
└──────────────────────┘
```

`&mut str` nhìn vào:

```text
Hello
```

Nó không sở hữu:

```text
capacity
```

nên không thể nói:

```text
"Hello" → "Hello World"
```

bằng cách mở rộng slice.

---

# 56. `String` là owner + buffer management

Có thể xem:

```text
String
```

là abstraction quản lý:

```text
allocation
+
length
+
capacity
+
UTF-8 invariant
+
ownership
```

Trong khi:

```text
&str
```

chỉ là:

```text
pointer
+
length
+
UTF-8 invariant
+
borrow
```

Đây là mental model cực kỳ hữu ích.

---

# 57. UTF-8 invariant

Rust đảm bảo:

```text
str
```

luôn chứa UTF-8 hợp lệ.

Đây là lý do bạn không thể tùy tiện sửa một byte trong `String` để tạo ra UTF-8 invalid.

Rust không cho:

```rust
let mut s = String::from("é");
```

rồi thao tác byte tùy ý theo cách phá vỡ invariant.

Bạn có thể truy cập bytes:

```rust
s.as_bytes()
```

nhưng đó là:

```text
&[u8]
```

và việc sửa bytes trực tiếp phải tuân thủ các invariant an toàn của Rust.

---

# 58. `String::from("Hello")` memory model

Hãy ghi nhớ hình ảnh này:

```text
STACK
┌─────────────────────────┐
│ String                  │
│                         │
│ ptr ─────────────────┐  │
│ len = 5              │  │
│ capacity = 5         │  │
└──────────────────────┼──┘
                       │
                       ▼
HEAP
┌───────────────────────┐
│ H │ e │ l │ l │ o     │
└───────────────────────┘
```

---

# 59. String literal memory model

```rust
let s = "Hello";
```

Conceptually:

```text
STACK
┌─────────────────────┐
│ &str                │
│ ptr ──────────────┐ │
│ len = 5            │ │
└───────────────────┼─┘
                    │
                    ▼
STATIC MEMORY
┌─────────────────────┐
│ H │ e │ l │ l │ o   │
└─────────────────────┘
```

---

# 60. `String` vs literal

```rust
let a = "Hello";
let b = String::from("Hello");
```

Conceptually:

```text
a:
&str
 │
 └────→ static "Hello"


b:
String
 │
 └────→ heap "Hello"
```

Hai `"Hello"` không nhất thiết là cùng một memory region.

---

# 61. `clone()`

Ví dụ:

```rust
let a = String::from("Hello");
let b = a.clone();
```

Bây giờ:

```text
a ─────→ heap A: Hello

b ─────→ heap B: Hello
```

Đây là deep copy của string data.

Khác:

```rust
let b = a;
```

là move ownership.

---

# 62. Move vs Clone

```text
let b = a;
```

```text
ownership transfer
```

Trong khi:

```text
let b = a.clone();
```

```text
allocate/copy
```

Mental model:

```text
move:
A ─────────→ B
same heap

clone:
A ─────────→ heap A
B ─────────→ heap B
```

---

# 63. `String` và `&str` trong function

Ví dụ:

```rust
fn hello(name: &str) {
    println!("Hello {name}");
}
```

Có thể gọi:

```rust
hello("Rust");

let s = String::from("Rust");
hello(&s);
```

Đây là API rất idiomatic.

---

# 64. Vì sao không dùng generic ngay?

Bạn có thể thấy:

```rust
fn hello<S: AsRef<str>>(name: S)
```

hoặc:

```rust
fn hello<S: Into<String>>(name: S)
```

Nhưng ở giai đoạn này:

```rust
fn hello(name: &str)
```

thường đơn giản và đúng khi chỉ cần đọc.

Đừng generic hóa API khi chưa có lý do.

---

# 65. Một API design pattern rất quan trọng

### Chỉ đọc:

```rust
fn parse(input: &str)
```

### Cần mutate:

```rust
fn normalize(input: &mut String)
```

### Cần ownership:

```rust
fn save(input: String)
```

### Trả về borrowed data:

```rust
fn first_word(input: &str) -> &str
```

Đây là nền tảng để học lifetime ở các buổi sau.

---

# 66. Ví dụ `first_word`

```rust
fn first_word(s: &str) -> &str {
    match s.find(' ') {
        Some(index) => &s[..index],
        None => s,
    }
}
```

Dữ liệu:

```text
Hello Rust
```

Function trả:

```text
Hello
```

Không allocation.

Không tạo `String` mới.

Chỉ tạo:

```text
&str slice
```

---

# 67. Memory model của `first_word`

Input:

```text
String
 ↓
Hello Rust
```

Output:

```text
&str
 ↓
Hello
```

Conceptual:

```text
HEAP
┌───────────────────────┐
│ H e l l o   R u s t   │
└───────────────────────┘
  ↑─────────↑
     &str
```

Không copy:

```text
H e l l o
```

---

# 68. Đây là sức mạnh của slice

Một `&str` có thể nhìn:

```text
một phần của String
```

mà không sở hữu phần đó.

Đây là lý do:

```rust
fn first_word(s: &str) -> &str
```

rất hiệu quả.

---

# 69. Nhưng borrowing có luật

Ví dụ:

```rust
let mut s = String::from("Hello");

let word = &s[..];

s.push_str(" World");

println!("{word}");
```

Code này sẽ gặp borrow checker error.

Tại sao?

Vì:

```text
word
 ↓
immutable borrow

s.push_str()
 ↓
mutable borrow
```

hai borrow xung đột.

Đây là nơi:

```text
String memory model
+
ownership
+
borrowing
```

gặp nhau.

---

# 70. Đây là lý do hiểu memory model quan trọng

Nếu bạn chỉ học:

```text
String = string
&str = string slice
```

thì borrow checker sẽ rất khó hiểu.

Nhưng nếu hiểu:

```text
String owns buffer
&str borrows buffer
```

thì lỗi trở nên logic:

```text
Không thể vừa có view đang được sử dụng
vừa thay đổi buffer underlying.
```

---

# 71. Một ví dụ khác

```rust
let mut text = String::from("Hello");

let view = &text;

println!("{view}");

text.push('!');
```

Điều này có thể hợp lệ vì borrow `view` đã kết thúc trước mutation, tùy phạm vi sử dụng theo non-lexical lifetimes.

Rust hiện đại phân tích **last use** của borrow.

Điều quan trọng không phải chỉ là:

```text
scope của biến
```

mà còn:

```text
last use của reference
```

---

# 72. Mental model chính xác hơn

Không nên nghĩ:

```text
&str = pointer
```

Mà nên nghĩ:

```text
&str =
    pointer
    +
    length
```

Không nên nghĩ:

```text
String = heap pointer
```

Mà nên nghĩ:

```text
String =
    pointer
    +
    length
    +
    capacity
    +
    ownership
```

---

# 73. Bảng memory model

| Type      | Conceptual representation   |
| --------- | --------------------------- |
| `char`    | Unicode scalar value        |
| `&str`    | pointer + length            |
| `String`  | pointer + length + capacity |
| `&[u8]`   | pointer + length            |
| `Vec<u8>` | pointer + length + capacity |

Bạn sẽ thấy:

```text
&str ≈ &[u8]
```

về **shape**.

Nhưng `&str` có invariant:

```text
UTF-8 valid
```

---

# 74. `String` và `Vec<u8>`

Một insight rất sâu:

```text
String
```

và:

```text
Vec<u8>
```

có memory layout conceptual tương tự:

```text
pointer
length
capacity
```

Nhưng:

```text
String
```

phải giữ:

```text
UTF-8 invariant
```

trong khi:

```text
Vec<u8>
```

có thể chứa bất kỳ byte nào.

---

# 75. Đây là lý do có `String::from_utf8`

Bạn có:

```rust
let bytes: Vec<u8>;
```

muốn chuyển thành:

```rust
String
```

Rust phải kiểm tra:

```text
bytes có phải UTF-8 hợp lệ không?
```

Do đó:

```rust
String::from_utf8(bytes)
```

có thể fail.

Điều này sẽ rất quan trọng khi học:

* networking
* file
* HTTP
* binary data
* serialization

---

# 76. Bài tập Buổi 7 — Cơ bản

## Bài 1

Giải thích memory model:

```rust
let s = "Hello";
```

Hãy vẽ:

```text
stack
static memory
pointer
length
```

---

## Bài 2

Giải thích:

```rust
let s = String::from("Hello");
```

Hãy vẽ:

```text
stack
heap
pointer
length
capacity
```

---

## Bài 3

Dự đoán:

```rust
let s = String::from("Hello");

println!("{}", s.len());
println!("{}", s.capacity());
```

Điều gì chắc chắn?

Điều gì **không nên giả định**?

---

# 77. Bài tập Buổi 7 — UTF-8

Phân tích:

```rust
let a = "A";
let b = "é";
let c = "你";
let d = "🚀";
```

Hãy dự đoán:

```text
a.len()
b.len()
c.len()
d.len()

a.chars().count()
b.chars().count()
c.chars().count()
d.chars().count()
```

Sau đó giải thích tại sao.

---

# 78. Bài tập — ownership

Phân tích:

```rust
let a = String::from("Hello");
let b = a;

println!("{a}");
```

Tại sao lỗi?

---

# 79. Bài tập — clone

Phân tích:

```rust
let a = String::from("Hello");
let b = a.clone();

println!("{a}");
println!("{b}");
```

Hãy vẽ memory model.

---

# 80. Bài tập — borrowing

Phân tích:

```rust
fn print_text(s: &str) {
    println!("{s}");
}

fn main() {
    let a = "Hello";
    let b = String::from("World");

    print_text(a);
    print_text(&b);
}
```

Giải thích tại sao cả hai đều hoạt động.

---

# 81. Bài tập — API design

Viết 3 function:

### Function 1

Chỉ đọc text:

```rust
fn ...
```

### Function 2

Thêm `"!"` vào cuối `String`:

```rust
fn ...
```

### Function 3

Nhận ownership của `String` và lưu nó vào một struct:

```rust
fn ...
```

Hãy chọn đúng giữa:

```text
&str
&mut String
String
```

---

# 82. Deep Dive Challenge

Không chạy code, phân tích:

```rust
fn main() {
    let mut s = String::from("Hello");

    let a = &s[..5];

    println!("{a}");

    s.push_str(" Rust");

    println!("{s}");
}
```

Câu hỏi:

```text
1. Code có compile không?
2. Nếu không, borrow nào gây vấn đề?
3. Nếu di chuyển println!("{a}") xuống sau push_str thì sao?
4. Nếu bỏ a thì sao?
5. Nếu dùng a.to_string() thì sao?
```

---

# 83. Deep Dive Challenge 2

Phân tích:

```rust
fn first_word(s: &str) -> &str {
    &s[..5]
}

fn main() {
    let s = String::from("Hello Rust");

    let word = first_word(&s);

    println!("{word}");
}
```

Hãy giải thích:

```text
1. first_word có tạo String mới không?
2. word sở hữu "Hello" không?
3. "Hello" nằm ở đâu?
4. word chứa gì?
5. lifetime của word liên quan đến s như thế nào?
```

---

# 84. Kiến thức phải thuộc sau Buổi 7

Bạn cần nhớ chính xác:

```text
String
=
owned + growable UTF-8 buffer
=
pointer + length + capacity
```

và:

```text
&str
=
borrowed UTF-8 slice
=
pointer + length
```

Conversion:

```text
String → &str
    ↓
borrow / no allocation

&str → String
    ↓
allocation + copy
```

Ownership:

```text
String
    ↓
owns data

&str
    ↓
borrows data
```

Mutation:

```text
String
    ↓
growable

&str
    ↓
fixed-size view
```

---

# 85. Mental model cuối cùng

Hãy ghi nhớ hình ảnh này:

```text
                  STRING ECOSYSTEM

       ┌───────────────────────────────┐
       │          String               │
       │                               │
       │ ptr ──────────────────────┐   │
       │ len                       │   │
       │ capacity                  │   │
       └───────────────────────────┼───┘
                                   │
                                   ▼
                              ┌─────────┐
                              │  HEAP   │
                              │         │
                              │ Hello   │
                              │ Rust    │
                              └────┬────┘
                                   ▲
                                   │
                         ┌─────────┴────────┐
                         │      &str        │
                         │                  │
                         │ ptr              │
                         │ len              │
                         └──────────────────┘
```

Và:

```text
String
  │
  ├── owns
  ├── grows
  ├── has capacity
  └── can mutate

&str
  │
  ├── borrows
  ├── does not own
  ├── no capacity
  └── is a view
```

**Một câu bạn nên thuộc lòng:**

> **`String` quản lý một vùng UTF-8 có ownership và capacity; `&str` chỉ là một view `(pointer, length)` vào một vùng UTF-8 đã tồn tại.**

Buổi 8 sẽ đi sâu vào **UTF-8 Memory Model**: `bytes` vs `chars` vs `graphemes`, tại sao `String[0]` không tồn tại, slicing `&s[a..b]`, UTF-8 boundary, panic khi slice sai boundary, và cách Rust đảm bảo `str` luôn là UTF-8 hợp lệ.
