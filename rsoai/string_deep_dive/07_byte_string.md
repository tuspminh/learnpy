# Rust String Deep Dive — Phần I

# Buổi 7 — Byte String `b"..."`

Buổi này chúng ta chuyển từ **Unicode text (`str`)** sang **raw bytes (`[u8]`)**.

Đây là kiến thức rất quan trọng trước khi đi vào:

* File I/O
* Network
* HTTP
* Binary protocol
* Serialization
* `Vec<u8>`
* `&[u8]`
* `String::from_utf8()`
* `String::from_utf8_lossy()`

---

# 1. Byte String là gì?

Rust hỗ trợ byte string literal:

```rust
b"hello"
```

Khác với:

```rust
"hello"
```

### String literal

```rust
"hello"
```

có kiểu:

```rust
&'static str
```

### Byte string literal

```rust
b"hello"
```

có kiểu:

```rust
&'static [u8; 5]
```

và thường được **coerce** thành:

```rust
&'static [u8]
```

Mental model:

```text
"hello"
    ↓
UTF-8 text
    ↓
&str
```

Trong khi:

```text
b"hello"
    ↓
raw bytes
    ↓
&[u8]
```

---

# 2. Ví dụ cơ bản

```rust
fn main() {
    let text = "hello";
    let bytes = b"hello";

    println!("{text:?}");
    println!("{bytes:?}");
}
```

Kết quả:

```text
"hello"
[104, 101, 108, 108, 111]
```

Vì:

```text
h = 104
e = 101
l = 108
l = 108
o = 111
```

---

# 3. Kiểu dữ liệu

Ta có thể kiểm tra:

```rust
fn main() {
    let bytes: &[u8] = b"hello";

    println!("{bytes:?}");
}
```

Điều này hợp lệ.

Nhưng:

```rust
let text: &str = b"hello";
```

sẽ không compile.

Bởi vì:

```text
&str
≠
&[u8]
```

---

# 4. `str` và `[u8]` khác nhau

Đây là distinction cực kỳ quan trọng.

```text
str
```

mang invariant:

> Dữ liệu bên trong phải là UTF-8 hợp lệ.

Trong khi:

```text
[u8]
```

chỉ là:

> Một sequence các byte.

Ví dụ:

```rust
let bytes: &[u8] = &[0xff, 0xfe, 0xfd];
```

hoàn toàn hợp lệ.

Nhưng:

```rust
let text: &str = ...
```

không thể chứa sequence UTF-8 invalid như vậy.

---

# 5. Byte string không phải String

Đừng nhầm:

```rust
b"hello"
```

với:

```rust
String::from("hello")
```

Chúng hoàn toàn khác nhau.

```text
"hello"
    ↓
&str
```

```text
b"hello"
    ↓
&[u8]
```

```text
String::from("hello")
    ↓
String
```

---

# 6. Byte string chứa bytes

Ví dụ:

```rust
let bytes = b"ABC";
```

Các byte:

```text
A = 65
B = 66
C = 67
```

Ta có:

```rust
println!("{:?}", bytes);
```

Output:

```text
[65, 66, 67]
```

---

# 7. Memory model

String literal:

```rust
let text = "ABC";
```

Conceptually:

```text
STACK
┌──────────────────┐
│ pointer          │
│ length = 3       │
└────────┬─────────┘
         │
         ▼
STATIC MEMORY
┌───────────────┐
│ A │ B │ C     │
└───────────────┘
```

Byte string:

```rust
let bytes = b"ABC";
```

Conceptually:

```text
STACK
┌──────────────────┐
│ pointer          │
│ length = 3       │
└────────┬─────────┘
         │
         ▼
STATIC MEMORY
┌───────────────┐
│ 65 │ 66 │ 67  │
└───────────────┘
```

Memory representation của view rất giống:

```text
&str
```

và:

```text
&[u8]
```

đều có conceptual:

```text
pointer + length
```

Nhưng semantics khác nhau.

---

# 8. Byte string có lifetime `'static`

Ví dụ:

```rust
let bytes: &'static [u8] = b"hello";
```

Hợp lệ.

Giống string literal:

```rust
let text: &'static str = "hello";
```

Dữ liệu literal tồn tại trong suốt lifetime của chương trình.

---

# 9. Byte string và UTF-8

Đây là phần quan trọng.

Byte string:

```rust
b"hello"
```

chỉ cho phép những ký tự có thể biểu diễn trực tiếp thành byte đơn.

Ví dụ:

```rust
b"hello"
```

hợp lệ.

Nhưng:

```rust
b"Xin chào"
```

**không hợp lệ**.

Tại sao?

Vì byte string literal không phải Unicode string literal.

---

# 10. Ví dụ Unicode

Code:

```rust
fn main() {
    let a = "é";
    let b = b"é";
}
```

`b"é"` sẽ không compile.

Trong khi:

```rust
let a = "é";
```

hoàn toàn hợp lệ.

Vì:

```text
"é"
 ↓
UTF-8
 ↓
C3 A9
```

Còn byte string yêu cầu mỗi element trong literal phù hợp với byte representation được phép của byte literal.

---

# 11. Muốn biểu diễn UTF-8 bytes thì sao?

Bạn có thể viết:

```rust
let bytes = "é".as_bytes();
```

Kết quả:

```text
[195, 169]
```

hoặc:

```text
[0xC3, 0xA9]
```

Đây là:

```text
&str
 ↓
as_bytes()
 ↓
&[u8]
```

Không tạo allocation.

---

# 12. `b"..."` rất hữu ích cho ASCII

Ví dụ:

```rust
const HTTP_GET: &[u8] = b"GET";
const HTTP_HOST: &[u8] = b"Host";
const CRLF: &[u8] = b"\r\n";
```

Đây là pattern rất phổ biến khi làm:

* networking
* HTTP parser
* protocol parser
* binary parser

---

# 13. Byte String hỗ trợ escape

Ví dụ:

```rust
let bytes = b"hello\nworld";
```

Kết quả:

```text
[104, 101, 108, 108, 111, 10, 119, 111, 114, 108, 100]
```

`\n`:

```text
10
```

---

# 14. Một số escape phổ biến

```rust
b"\n"
```

là:

```text
10
```

```rust
b"\r"
```

là:

```text
13
```

```rust
b"\t"
```

là:

```text
9
```

```rust
b"\\"
```

là:

```text
92
```

```rust
b"\""
```

là:

```text
34
```

---

# 15. Hexadecimal byte escape

Byte string hỗ trợ:

```rust
b"\x48\x65\x6c\x6c\x6f"
```

Các byte:

```text
48 = H
65 = e
6C = l
6C = l
6F = o
```

Do đó:

```rust
fn main() {
    let bytes = b"\x48\x65\x6c\x6c\x6f";

    println!("{bytes:?}");
}
```

Output:

```text
[72, 101, 108, 108, 111]
```

---

# 16. `\xNN` rất hữu ích khi làm protocol

Ví dụ:

```rust
let bytes = b"\x01\x02\x03\xff";
```

Kết quả:

```text
[1, 2, 3, 255]
```

Đây không phải text.

Đây là:

```text
raw byte sequence
```

---

# 17. Byte String và `u8`

Rust:

```rust
u8
```

có range:

```text
0..=255
```

Vì vậy:

```rust
let data: &[u8] = b"ABC";
```

có thể hình dung:

```text
&[u8]
   │
   ├── 65
   ├── 66
   └── 67
```

---

# 18. `b"ABC"` có phải `Vec<u8>` không?

Không.

```rust
b"ABC"
```

là một **byte string literal**.

Nó là một array literal có kích thước cố định:

```text
[u8; 3]
```

Khi sử dụng trong context phù hợp, nó được borrow/coerce thành:

```text
&[u8]
```

Không phải:

```text
Vec<u8>
```

---

# 19. So sánh ba kiểu

```rust
let a = b"ABC";
let b = b"ABC".as_slice();
let c = b"ABC".to_vec();
```

Conceptually:

```text
a
↓
&[u8; 3]

b
↓
&[u8]

c
↓
Vec<u8>
```

`c` có ownership và heap allocation.

---

# 20. `Vec<u8>` là owned bytes

```rust
let data = b"ABC".to_vec();
```

Ta có:

```text
Vec<u8>
┌─────────────────┐
│ pointer         │
│ length          │
│ capacity        │
└────────┬────────┘
         │
         ▼
       HEAP
┌─────────────────┐
│ 65 │ 66 │ 67    │
└─────────────────┘
```

Trong khi:

```rust
b"ABC"
```

không cần heap allocation mới.

---

# 21. Đây là pattern quan trọng

```text
b"ABC"
   ↓
&[u8]
   ↓
borrowed bytes
```

```text
b"ABC".to_vec()
   ↓
Vec<u8>
   ↓
owned bytes
```

Tương tự:

```text
"ABC"
   ↓
&str
```

```text
"ABC".to_string()
   ↓
String
```

Ta có cặp:

```text
text:
&str ←→ String

bytes:
&[u8] ←→ Vec<u8>
```

---

# 22. Bảng so sánh

| Literal             | Type                 | Ownership       |
| ------------------- | -------------------- | --------------- |
| `"ABC"`             | `&str`               | borrowed        |
| `b"ABC"`            | `&[u8]` / `&[u8; 3]` | borrowed/static |
| `"ABC".to_string()` | `String`             | owned           |
| `b"ABC".to_vec()`   | `Vec<u8>`            | owned           |

---

# 23. Byte String vs Raw String

Buổi trước chúng ta học:

```rust
r"hello\nworld"
```

Raw string có nghĩa:

> Không xử lý escape sequence thông thường.

Byte string:

```rust
b"hello\nworld"
```

có nghĩa:

> Đây là bytes và escape sequence vẫn được xử lý.

Hai concept khác nhau.

---

# 24. Có thể kết hợp raw + byte

Rust hỗ trợ:

```rust
br"hello\nworld"
```

Đây là:

> raw byte string literal.

Ví dụ:

```rust
let data = br"hello\nworld";
```

Nó chứa ký tự:

```text
hello
\
n
world
```

chứ không biến:

```text
\n
```

thành newline.

---

# 25. So sánh

```rust
b"hello\nworld"
```

chứa:

```text
hello
world
```

với newline.

Trong khi:

```rust
br"hello\nworld"
```

chứa literal:

```text
hello\nworld
```

---

# 26. `b""` và `br""`

Mental model:

```text
"..." 
 ↓
Unicode text
```

```text
r"..."
 ↓
raw Unicode text
```

```text
b"..."
 ↓
bytes
```

```text
br"..."
 ↓
raw bytes
```

Đây là bốn dạng literal rất đáng nhớ.

---

# 27. Byte string không phải binary data arbitrary hoàn toàn

Điểm tinh tế:

```rust
b"\xff"
```

có thể tạo byte `255`.

Nhưng syntax của byte string literal vẫn có các quy tắc riêng; nó không phải một cách viết tùy ý mọi binary blob.

Ví dụ:

```rust
b"\x00\x01\x02\xff"
```

rất phù hợp để biểu diễn byte sequence.

---

# 28. Byte String dùng khi nào?

### 1. Network protocol

```rust
const HEADER: &[u8] = b"HTTP/1.1";
```

### 2. File format

```rust
const MAGIC: &[u8] = b"PNG";
```

### 3. Binary protocol

```rust
const MAGIC: &[u8] = b"RUST";
```

### 4. ASCII protocol

```rust
const CRLF: &[u8] = b"\r\n";
```

---

# 29. Ví dụ kiểm tra file signature

Giả sử một format bắt đầu bằng:

```text
RUST
```

Ta có:

```rust
const MAGIC: &[u8] = b"RUST";

fn is_valid(data: &[u8]) -> bool {
    data.starts_with(MAGIC)
}
```

Sử dụng:

```rust
fn main() {
    let data = b"RUST hello";

    println!("{}", is_valid(data));
}
```

Output:

```text
true
```

---

# 30. Đây là cách tư duy rất Rust

Thay vì:

```rust
String
```

cho mọi thứ, hãy hỏi:

> Tôi đang xử lý **text** hay **bytes**?

Nếu là text:

```text
str / String
```

Nếu là bytes:

```text
[u8] / Vec<u8>
```

---

# 31. Text → bytes

```rust
let text = "Hello";

let bytes = text.as_bytes();
```

Kiểu:

```text
&[u8]
```

Không allocation.

Memory:

```text
"Hello"
    │
    ▼
UTF-8 bytes
    │
    ▼
&[u8]
```

---

# 32. Bytes → String

Ngược lại:

```rust
let bytes = b"Hello";

let text = String::from_utf8(bytes.to_vec()).unwrap();
```

Tại sao phải kiểm tra?

Vì:

```text
[u8]
```

không đảm bảo UTF-8.

Rust phải xác nhận:

```text
bytes
 ↓
valid UTF-8?
 ↓
yes → String
no  → error
```

---

# 33. `String::from_utf8`

Ví dụ:

```rust
fn main() {
    let bytes = vec![72, 101, 108, 108, 111];

    let text = String::from_utf8(bytes).unwrap();

    println!("{text}");
}
```

Output:

```text
Hello
```

---

# 34. Bytes invalid UTF-8

```rust
fn main() {
    let bytes = vec![0xff, 0xfe, 0xfd];

    let result = String::from_utf8(bytes);

    println!("{result:?}");
}
```

Kết quả:

```text
Err(...)
```

Đây là một concept cực kỳ quan trọng:

```text
Vec<u8>
```

không mặc định là:

```text
String
```

---

# 35. `from_utf8_lossy`

Nếu bạn muốn chuyển bytes thành text và thay thế sequence invalid:

```rust
let bytes = &[0xff, 0xfe];

let text = String::from_utf8_lossy(bytes);

println!("{text}");
```

Rust sẽ sử dụng replacement character:

```text
�
```

---

# 36. Byte string và network

Hãy tưởng tượng TCP nhận:

```text
[72, 101, 108, 108, 111]
```

Bạn chưa thể mặc định nói:

```text
"Hello"
```

Trước hết bạn có:

```text
bytes
```

Sau đó nếu protocol nói rằng payload là UTF-8:

```text
bytes
 ↓
UTF-8 validation
 ↓
text
```

Đây là cách xử lý đúng.

---

# 37. Đây là lý do Rust phân biệt `str` và `[u8]`

Rust không muốn bạn vô tình giả định:

```text
bytes = text
```

Thực tế:

```text
bytes
```

có thể là:

* UTF-8
* JPEG
* PNG
* ZIP
* encrypted data
* compressed data
* network packet
* arbitrary binary

Chỉ khi biết encoding mới chuyển sang:

```text
str
```

---

# 38. Một ví dụ thực tế

```rust
fn parse_message(data: &[u8]) {
    if let Ok(text) = std::str::from_utf8(data) {
        println!("Text: {text}");
    } else {
        println!("Binary data");
    }
}
```

Ở đây:

```text
&[u8]
 ↓
from_utf8()
 ↓
Result<&str, Utf8Error>
```

Không allocation.

---

# 39. `std::str::from_utf8`

Có hai hướng:

```rust
String::from_utf8(Vec<u8>)
```

và:

```rust
std::str::from_utf8(&[u8])
```

Khác nhau về ownership.

### `from_utf8`

```text
Vec<u8>
 ↓
String
```

### `str::from_utf8`

```text
&[u8]
 ↓
&str
```

---

# 40. Đây là pattern cực kỳ quan trọng

```text
Owned bytes
Vec<u8>
   │
   │ validation
   ▼
String
```

Trong khi:

```text
Borrowed bytes
&[u8]
   │
   │ validation
   ▼
&str
```

---

# 41. Ví dụ zero-copy

```rust
fn parse(data: &[u8]) -> Option<&str> {
    std::str::from_utf8(data).ok()
}
```

Nếu bytes hợp lệ UTF-8:

```text
&[u8]
 ↓
&str
```

Không cần tạo `String`.

Đây là **zero-copy conversion**.

---

# 42. Nhưng có một điều kiện

`&str` chỉ hợp lệ nếu bytes:

```text
valid UTF-8
```

Rust đảm bảo invariant này.

Vì vậy:

```rust
std::str::from_utf8(bytes)
```

trả về:

```rust
Result<&str, Utf8Error>
```

chứ không đơn giản:

```rust
&str
```

---

# 43. Byte String với `const`

Byte literals cực kỳ hữu ích với constant:

```rust
const MAGIC: &[u8] = b"RUST";
const CRLF: &[u8] = b"\r\n";
const GET: &[u8] = b"GET";
```

Không cần runtime allocation.

---

# 44. Ví dụ protocol parser nhỏ

```rust
const CRLF: &[u8] = b"\r\n";

fn has_crlf(data: &[u8]) -> bool {
    data.windows(2).any(|window| window == CRLF)
}

fn main() {
    let data = b"Hello\r\nWorld";

    println!("{}", has_crlf(data));
}
```

Output:

```text
true
```

Đây là cách byte string bắt đầu trở nên hữu ích trong code thực tế.

---

# 45. `b"..."` rất phù hợp với `starts_with`

```rust
fn is_http(data: &[u8]) -> bool {
    data.starts_with(b"GET")
}
```

Hoặc:

```rust
fn is_http(data: &[u8]) -> bool {
    data.starts_with(b"POST")
}
```

Không cần tạo `String`.

---

# 46. So sánh text parser và byte parser

### Text parser

```rust
fn parse(data: &str) {
    // Unicode text
}
```

### Byte parser

```rust
fn parse(data: &[u8]) {
    // raw bytes
}
```

Byte parser thường phù hợp hơn khi:

```text
protocol
file format
network packet
binary format
```

---

# 47. Bẫy thường gặp #1

Sai tư duy:

```rust
let bytes = b"hello";
let text: &str = bytes;
```

Không compile.

Phải:

```rust
let text = std::str::from_utf8(bytes).unwrap();
```

vì Rust phải xác nhận UTF-8.

---

# 48. Bẫy thường gặp #2

Nghĩ:

```rust
b"hello"
```

là:

```rust
Vec<u8>
```

Sai.

Nó là byte string literal.

Nếu cần `Vec<u8>`:

```rust
let data = b"hello".to_vec();
```

---

# 49. Bẫy thường gặp #3

Nghĩ:

```rust
b"hello"
```

có heap allocation.

Không nên nghĩ như vậy.

Nó là literal có static lifetime, tương tự string literal:

```text
program/static memory
```

Nếu gọi:

```rust
.to_vec()
```

thì mới tạo owned vector.

---

# 50. Bẫy thường gặp #4

Nghĩ byte string là Unicode.

Không.

```text
"你好"
```

là Unicode text.

```text
b"ABC"
```

là bytes.

Nếu muốn bytes UTF-8 của Unicode:

```rust
"你好".as_bytes()
```

---

# 51. Bẫy thường gặp #5

Nhầm `char` với `u8`.

```rust
'A'
```

là:

```text
char
```

còn:

```rust
b'A'
```

là:

```text
u8
```

Đây là khác biệt cực kỳ quan trọng.

```text
'A'
 ↓
char

b'A'
 ↓
u8
```

---

# 52. Đây là cầu nối sang Buổi 8

Chúng ta sẽ học:

```text
char vs &str
```

Ví dụ:

```rust
'A'
```

vs:

```rust
"A"
```

vs:

```rust
b"A"
```

Ba thứ:

```text
'A'
 ↓
char

"A"
 ↓
&str

b"A"
 ↓
&[u8]
```

Đây là ba abstraction khác nhau.

---

# 53. Bài tập 1 — Kiểu dữ liệu

Không chạy code, hãy xác định type:

```rust
let a = "hello";
let b = b"hello";
let c = 'h';
let d = b'h';
```

Đáp án cần suy luận:

```text
a = ?
b = ?
c = ?
d = ?
```

---

# 54. Bài tập 2 — Bytes

Viết chương trình:

```rust
let data = b"Rust";
```

in ra:

```text
[82, 117, 115, 116]
```

Sau đó giải thích từng byte.

---

# 55. Bài tập 3 — UTF-8

Viết chương trình:

```rust
let text = "é";
```

lấy bytes của nó:

```rust
let bytes = text.as_bytes();
```

và in:

```text
[195, 169]
```

Sau đó giải thích tại sao:

```text
text.len() == 2
```

nhưng:

```text
text.chars().count() == 1
```

---

# 56. Bài tập 4 — Bytes → `&str`

Viết:

```rust
fn parse(data: &[u8]) -> Option<&str>
```

sao cho:

```rust
parse(b"Hello")
```

trả về:

```text
Some("Hello")
```

và dữ liệu invalid UTF-8 trả về:

```text
None
```

Gợi ý:

```rust
std::str::from_utf8(...)
```

---

# 57. Bài tập 5 — Protocol

Viết:

```rust
fn is_get_request(data: &[u8]) -> bool
```

Sao cho:

```rust
is_get_request(b"GET / HTTP/1.1")
```

→ `true`

và:

```rust
is_get_request(b"POST / HTTP/1.1")
```

→ `false`

Gợi ý:

```rust
starts_with()
```

---

# 58. Bài tập 6 — Memory Model

Giải thích sự khác nhau:

```rust
let a = "hello";
let b = b"hello";
let c = a.as_bytes();
let d = b.to_vec();
```

Hãy xác định:

```text
a:
type = ?
ownership = ?
allocation = ?

b:
type = ?
ownership = ?
allocation = ?

c:
type = ?
ownership = ?
allocation = ?

d:
type = ?
ownership = ?
allocation = ?
```

---

# 59. Bài tập Deep Dive

Phân tích:

```rust
fn inspect(data: &[u8]) {
    println!("{data:?}");

    match std::str::from_utf8(data) {
        Ok(text) => println!("text = {text}"),
        Err(_) => println!("binary"),
    }
}

fn main() {
    inspect(b"Hello");
    inspect(&[0xff, 0xfe, 0xfd]);
}
```

Giải thích chính xác:

```text
1. b"Hello" có type gì?
2. Vì sao truyền được vào &[u8]?
3. from_utf8() có allocation không?
4. Tại sao [0xff, 0xfe, 0xfd] không trở thành &str?
5. Tại sao Rust cần Result?
```

---

# 60. Tổng kết Buổi 7

Hãy ghi nhớ sơ đồ này:

```text
                    RUST STRING/BYTES

                  "hello"
                     │
                     ▼
                   &str
                     │
              UTF-8 invariant
                     │
                     ▼
              text / Unicode


                  b"hello"
                     │
                     ▼
                   &[u8]
                     │
              arbitrary bytes
                     │
                     ▼
             byte-oriented data
```

Owned version:

```text
&str
 │
 │ to_string()
 ▼
String
```

và:

```text
&[u8]
 │
 │ to_vec()
 ▼
Vec<u8>
```

Conversion có validation:

```text
&[u8]
 │
 │ str::from_utf8()
 ▼
Result<&str, Utf8Error>
```

Owned conversion:

```text
Vec<u8>
 │
 │ String::from_utf8()
 ▼
Result<String, FromUtf8Error>
```

Và bốn literal cần phân biệt:

```text
"hello"
    → &str

r"hello\n"
    → raw &str

b"hello"
    → &[u8]

br"hello\n"
    → raw &[u8]
```

**Mental model quan trọng nhất của Buổi 7:**

> `str` biểu diễn **text UTF-8**, còn `[u8]` biểu diễn **raw bytes**. `b"..."` tạo byte string literal; nó không phải `String` và cũng không phải Unicode `str`.
