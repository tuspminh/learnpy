# Rust String Deep Dive — Phần I

# Buổi 8 — `char` vs `&str`

Đây là buổi rất quan trọng vì từ đây bạn sẽ bắt đầu hiểu sâu cách Rust biểu diễn **Unicode**, thay vì chỉ nhìn String như một chuỗi ký tự.

Ba thứ cần phân biệt:

```rust
'A'
"A"
b"A"
```

tương ứng:

```text
'A'   → char
"A"   → &str
b"A"  → &[u8]
```

---

# 1. `char` là gì?

Trong Rust:

```rust
let c = 'A';
```

`c` có type:

```rust
char
```

`char` đại diện cho **một Unicode scalar value**.

Ví dụ:

```rust
let a = 'A';
let b = 'é';
let c = '中';
let d = '🦀';
```

Tất cả đều là:

```text
char
```

---

# 2. `char` không phải 1 byte

Đây là một lỗi tư duy rất phổ biến.

Trong Rust:

```rust
char
```

có kích thước:

```text
4 bytes
```

Ví dụ:

```rust
use std::mem::size_of;

fn main() {
    println!("{}", size_of::<char>());
}
```

Kết quả:

```text
4
```

Rust dùng 4 byte để biểu diễn một Unicode scalar value.

---

# 3. `&str` là gì?

Ví dụ:

```rust
let text = "Hello";
```

`text` có type:

```text
&str
```

`&str` là một **string slice**.

Nó đại diện cho một vùng bytes chứa dữ liệu UTF-8 hợp lệ.

Mental model:

```text
&str
┌──────────────┐
│ pointer      │
│ length       │
└──────────────┘
        │
        ▼
 UTF-8 bytes
```

---

# 4. `char` vs `&str`

Ví dụ:

```rust
let c = 'A';
let s = "A";
```

Ta có:

```text
c
↓
char
↓
một Unicode scalar value
```

Trong khi:

```text
s
↓
&str
↓
một sequence UTF-8 bytes
```

---

# 5. Một ký tự và một chuỗi

`char`:

```rust
let c = 'R';
```

chỉ có **một** Unicode scalar value.

`&str`:

```rust
let s = "Rust";
```

có nhiều ký tự.

```text
"Rust"
 ↓
R
u
s
t
```

---

# 6. Syntax khác nhau

Rust cố tình dùng:

```rust
'A'
```

cho `char`.

Và:

```rust
"A"
```

cho string.

Đây là quy tắc:

```text
'...'  → char
"..."  → &str
```

Ví dụ:

```rust
let a: char = 'A';
let b: &str = "A";
```

---

# 7. Không thể nhầm hai loại

Code này sai:

```rust
let c: char = "A";
```

Vì:

```text
"A"
```

là:

```text
&str
```

Không phải `char`.

Ngược lại:

```rust
let s: &str = 'A';
```

cũng sai.

---

# 8. Chuyển `char` thành `String`

Bạn có thể:

```rust
let c = 'A';

let s = c.to_string();
```

Kết quả:

```text
char
 ↓
String
```

Ví dụ:

```rust
fn main() {
    let c = '🦀';
    let s = c.to_string();

    println!("{s}");
}
```

---

# 9. `char` → `&str`?

Đây là điểm thú vị.

Rust không có phép chuyển trực tiếp đơn giản:

```rust
let c = 'A';

let s: &str = ???;
```

Vì `char` là một value độc lập còn `&str` là một borrowed view vào một vùng UTF-8.

Bạn thường dùng:

```rust
c.encode_utf8(&mut buffer)
```

hoặc nếu cần owned string:

```rust
c.to_string()
```

---

# 10. `char::encode_utf8`

Ví dụ:

```rust
fn main() {
    let c = 'é';
    let mut buffer = [0u8; 4];

    let s = c.encode_utf8(&mut buffer);

    println!("{s}");
    println!("{:?}", s.as_bytes());
}
```

Kết quả:

```text
é
[195, 169]
```

Ta thấy:

```text
'é'
   ↓
UTF-8
   ↓
C3 A9
```

---

# 11. Một `char` có thể chiếm bao nhiêu byte trong UTF-8?

Một `char` trong Rust luôn:

```text
4 bytes
```

nhưng khi encode UTF-8 thì có thể chiếm:

```text
1 → 4 bytes
```

Ví dụ:

| Character | UTF-8 bytes |
| --------- | ----------: |
| `A`       |           1 |
| `é`       |           2 |
| `中`       |           3 |
| `🦀`      |           4 |

---

# 12. Đây là điểm cực kỳ quan trọng

Không được suy luận:

```text
1 char = 1 byte
```

Trong Rust:

```text
char
```

không phải byte.

Và:

```text
UTF-8 encoded char
```

có thể từ 1 đến 4 bytes.

---

# 13. Ví dụ

```rust
fn main() {
    let chars = ['A', 'é', '中', '🦀'];

    for c in chars {
        let mut buffer = [0u8; 4];
        let encoded = c.encode_utf8(&mut buffer);

        println!(
            "{c} -> {} bytes -> {:?}",
            encoded.len(),
            encoded.as_bytes()
        );
    }
}
```

Kết quả conceptually:

```text
A -> 1 bytes -> [65]

é -> 2 bytes -> [195, 169]

中 -> 3 bytes -> [...]

🦀 -> 4 bytes -> [...]
```

---

# 14. `&str` được tạo từ UTF-8 bytes

Ví dụ:

```rust
let text = "é";
```

Trong memory:

```text
UTF-8:

C3 A9
```

`&str` nhìn vào vùng bytes đó:

```text
&str
┌────────────┐
│ pointer    │──────┐
│ len = 2    │      │
└────────────┘      ▼
                  C3 A9
```

Lưu ý:

```text
len = 2
```

là **2 bytes**, không phải 2 characters.

---

# 15. `str.len()` trả về bytes

Ví dụ:

```rust
fn main() {
    let a = "A";
    let b = "é";
    let c = "中";
    let d = "🦀";

    println!("{}", a.len());
    println!("{}", b.len());
    println!("{}", c.len());
    println!("{}", d.len());
}
```

Kết quả:

```text
1
2
3
4
```

---

# 16. Nhưng số character khác

```rust
fn main() {
    let text = "Aé中🦀";

    println!("bytes  = {}", text.len());
    println!("chars  = {}", text.chars().count());
}
```

Kết quả:

```text
bytes = 10
chars = 4
```

Vì:

```text
A    → 1
é    → 2
中   → 3
🦀   → 4

1 + 2 + 3 + 4 = 10
```

---

# 17. `chars()` là gì?

```rust
let text = "Rust";
```

Bạn có thể:

```rust
for c in text.chars() {
    println!("{c}");
}
```

Output:

```text
R
u
s
t
```

`chars()` tạo iterator trên Unicode scalar values.

---

# 18. `chars()` không trả về `&str`

Ví dụ:

```rust
let text = "Rust";

for c in text.chars() {
    // c: char
}
```

Ở đây:

```text
text
 ↓
&str

chars()
 ↓
Iterator<Item = char>
```

---

# 19. Đây là distinction quan trọng

```rust
let text = "Rust";
```

là:

```text
&str
```

Nhưng:

```rust
text.chars()
```

cho ra:

```text
char
char
char
char
```

Có thể hình dung:

```text
&str
 ↓
chars()
 ↓
Iterator<char>
```

---

# 20. `bytes()` khác `chars()`

Đây là một cặp cực kỳ quan trọng.

```rust
let text = "é";
```

### `chars()`

```rust
for c in text.chars() {
    println!("{c}");
}
```

→ một `char`:

```text
é
```

### `bytes()`

```rust
for b in text.bytes() {
    println!("{b}");
}
```

→ hai `u8`:

```text
195
169
```

---

# 21. So sánh

```text
"é"
 │
 ├── chars()
 │      ↓
 │     'é'
 │
 └── bytes()
        ↓
       195
       169
```

Đây là một trong những mental model quan trọng nhất khi học Rust String.

---

# 22. `char` vs `byte`

```rust
let c = 'é';
```

type:

```text
char
```

Còn:

```rust
let bytes = "é".bytes();
```

mỗi element:

```text
u8
```

Vì vậy:

```text
char
```

và:

```text
u8
```

hoàn toàn khác nhau.

---

# 23. `char` vs Unicode scalar value

Rust documentation thường mô tả:

```text
char = Unicode scalar value
```

Không phải mọi Unicode code point đều là scalar value.

Unicode có surrogate range:

```text
U+D800 .. U+DFFF
```

Các giá trị này không phải Unicode scalar values.

Rust `char` không cho phép chúng.

---

# 24. Ví dụ

Bạn có thể:

```rust
let c = '\u{1F980}';
```

Đây là:

```text
🦀
```

Nhưng không thể tạo một `char` surrogate Unicode.

Đây là một trong những lý do Rust có invariant mạnh cho `char`.

---

# 25. `char` có thể so sánh

```rust
fn main() {
    let a = 'a';
    let b = 'b';

    println!("{}", a < b);
}
```

Output:

```text
true
```

Vì `char` có thứ tự theo Unicode scalar value.

---

# 26. `char` có các method Unicode

Ví dụ:

```rust
let c = 'A';

println!("{}", c.is_alphabetic());
println!("{}", c.is_numeric());
println!("{}", c.is_whitespace());
```

Bạn cũng có:

```rust
c.to_lowercase()
c.to_uppercase()
```

---

# 27. Một điểm tinh tế: uppercase không nhất thiết là một char

Ví dụ:

```rust
let c = 'ß';
```

Unicode case conversion có thể tạo nhiều code point.

Vì vậy Rust có:

```rust
c.to_uppercase()
```

trả về iterator.

Không nên giả định:

```text
char → char
```

trong mọi phép biến đổi Unicode.

---

# 28. `&str` có thể chứa nhiều `char`

Ví dụ:

```rust
let text = "Hello 世界 🦀";
```

Đây là:

```text
&str
```

bên trong là UTF-8 bytes.

Khi gọi:

```rust
text.chars()
```

ta mới tách thành:

```text
H
e
l
l
o
 
世
界
 
🦀
```

---

# 29. `&str` không phải `Vec<char>`

Một người mới học thường tưởng:

```text
String
=
array of char
```

Trong Rust, không phải.

String/`str` là:

```text
UTF-8 bytes
```

không phải:

```text
char[]
```

---

# 30. Đây là thiết kế rất quan trọng

Nếu:

```text
String = Vec<char>
```

thì mỗi character sẽ cần 4 bytes.

Nhưng UTF-8 cho phép:

```text
ASCII → 1 byte
```

nên Rust có thể lưu:

```text
"Hello"
```

chỉ với:

```text
5 bytes
```

thay vì:

```text
5 × 4 = 20 bytes
```

---

# 31. Memory model

String:

```rust
let text = String::from("Hello");
```

Conceptually:

```text
STACK
┌──────────────┐
│ ptr          │
│ len = 5      │
│ capacity     │
└──────┬───────┘
       │
       ▼
HEAP
┌────────────────────┐
│ H │ e │ l │ l │ o  │
└────────────────────┘
```

Không có:

```text
char
char
char
char
char
```

---

# 32. `&str` cũng vậy

```rust
let text = "Hello";
```

Conceptually:

```text
&str
┌──────────────┐
│ ptr          │
│ len = 5      │
└──────┬───────┘
       │
       ▼
UTF-8
H e l l o
```

---

# 33. `char` thì khác

```rust
let c = '🦀';
```

Conceptually:

```text
STACK
┌──────────────┐
│ 4-byte value │
└──────────────┘
```

Không phải:

```text
pointer + length
```

---

# 34. `char` có size cố định

```rust
use std::mem::size_of;

fn main() {
    println!("{}", size_of::<char>());
    println!("{}", size_of::<u8>());
}
```

Output:

```text
4
1
```

Trong khi:

```rust
println!("{}", size_of::<&str>());
```

thường là:

```text
16
```

trên hệ thống 64-bit:

```text
pointer = 8
length  = 8
```

---

# 35. Một ví dụ rất quan trọng

```rust
fn inspect(text: &str) {
    println!("bytes = {}", text.len());
    println!("chars = {}", text.chars().count());
}

fn main() {
    inspect("Hello");
    inspect("你好");
    inspect("🦀");
}
```

Kết quả conceptually:

```text
Hello
bytes = 5
chars = 5

你好
bytes = 6
chars = 2

🦀
bytes = 4
chars = 1
```

---

# 36. Tại sao Rust không cho `text[0]`?

Bạn có:

```rust
let text = "你好";
```

Không thể:

```rust
println!("{}", text[0]);
```

Vì Rust không biết bạn muốn:

```text
byte
```

hay:

```text
char
```

và Unicode character có độ dài UTF-8 variable-width.

---

# 37. Muốn lấy `char`

Dùng:

```rust
let first = text.chars().next();
```

Ví dụ:

```rust
fn main() {
    let text = "你好";

    let first = text.chars().next();

    println!("{first:?}");
}
```

Output:

```text
Some('你')
```

---

# 38. Muốn lấy byte

Dùng:

```rust
let first_byte = text.bytes().next();
```

Kết quả:

```text
Some(...)
```

nhưng đó là **một byte UTF-8**, không nhất thiết là toàn bộ character.

Đây là lý do `bytes()` và `chars()` có semantics rất khác nhau.

---

# 39. Ví dụ `é`

```rust
let text = "é";
```

UTF-8:

```text
C3 A9
```

### `chars()`

```text
'é'
```

### `bytes()`

```text
195
169
```

### `len()`

```text
2
```

### `chars().count()`

```text
1
```

Bốn kết quả này phải nhớ.

---

# 40. `char` → UTF-8

```rust
let c = 'é';
```

Encode:

```rust
let mut buffer = [0u8; 4];

let encoded = c.encode_utf8(&mut buffer);
```

Ta nhận:

```text
&str
```

và:

```text
[195, 169]
```

---

# 41. UTF-8 → `char`

Nếu bạn có:

```rust
let text = "é";
```

Bạn có thể:

```rust
let c = text.chars().next().unwrap();
```

Kết quả:

```text
'é'
```

Nhưng lưu ý:

```text
&str → char
```

chỉ lấy **một Unicode scalar value**, không phải toàn bộ string.

---

# 42. Nếu String có nhiều char?

```rust
let text = "Rust";
```

Không thể:

```rust
let c: char = text;
```

Phải chọn một character:

```rust
let first = text.chars().next();
```

hoặc:

```rust
let chars: Vec<char> = text.chars().collect();
```

---

# 43. `Vec<char>`

Có thể tạo:

```rust
let chars: Vec<char> = "Rust 🦀".chars().collect();
```

Khi đó:

```text
String/str
     ↓
UTF-8
     ↓
chars()
     ↓
Vec<char>
```

Nhưng `Vec<char>` thường không phải representation tối ưu để lưu text.

---

# 44. Khi nào dùng `char`?

Dùng `char` khi bạn cần xử lý:

* một Unicode scalar value
* kiểm tra ký tự
* Unicode classification
* parsing từng ký tự
* pattern matching từng character

Ví dụ:

```rust
fn is_digit(c: char) -> bool {
    c.is_numeric()
}
```

---

# 45. Khi nào dùng `&str`?

Dùng `&str` khi bạn cần:

* text
* string slice
* đọc chuỗi
* truyền string vào function
* parsing text
* làm việc với UTF-8

Ví dụ:

```rust
fn greet(name: &str) {
    println!("Hello, {name}");
}
```

---

# 46. Khi nào dùng `u8`?

Dùng `u8` khi xử lý:

* raw bytes
* binary data
* network
* file
* protocol
* encoded data

Ví dụ:

```rust
fn checksum(data: &[u8]) -> u8 {
    data.iter().fold(0, |sum, byte| sum.wrapping_add(*byte))
}
```

---

# 47. Ba tầng abstraction

Đây là mental model bạn nên ghi nhớ:

```text
                Unicode Text
                     │
                     ▼
                   &str
                     │
             chars() │ bytes()
               │     │
               ▼     ▼
             char    u8
```

Hay:

```text
&str
 ├── chars() → char
 └── bytes() → u8
```

---

# 48. `char` không phải character theo nghĩa người dùng

Đây là deep dive quan trọng.

Rust:

```text
char
```

là:

> Unicode scalar value

Nó không nhất thiết tương ứng với một **grapheme cluster** mà người dùng nhìn thấy.

Ví dụ một ký tự hiển thị có thể được tạo từ nhiều Unicode scalar values.

---

# 49. Ví dụ Unicode combining mark

Một ký tự nhìn giống:

```text
é
```

có thể được biểu diễn bằng:

```text
U+00E9
```

hoặc:

```text
e + combining acute accent
```

Tức:

```text
'e'
+
'\u{301}'
```

Đây là **2 `char`** nhưng có thể hiển thị như **một grapheme**.

---

# 50. Vì vậy

Không nên nói:

```text
char = một ký tự người dùng nhìn thấy
```

Chính xác hơn:

```text
char
=
Unicode scalar value
```

Còn:

```text
grapheme cluster
=
một đơn vị hiển thị gần với "ký tự" mà người dùng cảm nhận
```

Đây là vấn đề Unicode nâng cao.

---

# 51. Ví dụ

```rust
fn main() {
    let text = "e\u{301}";

    println!("bytes: {}", text.len());
    println!("chars: {}", text.chars().count());
}
```

Có thể:

```text
bytes = 3
chars = 2
```

vì:

```text
e       → 1 byte
U+0301  → 2 bytes
```

Nhưng người dùng có thể nhìn thấy:

```text
é
```

như một grapheme.

---

# 52. Đây là lý do String processing khó

Khi xử lý String, phải xác định bạn đang cần:

```text
bytes?
chars?
graphemes?
```

Ba khái niệm:

```text
bytes
  ↓
UTF-8 encoding units

chars
  ↓
Unicode scalar values

graphemes
  ↓
user-perceived characters
```

---

# 53. Tổng kết cực kỳ quan trọng

| Expression    | Type     | Ý nghĩa              |
| ------------- | -------- | -------------------- |
| `'A'`         | `char`   | Unicode scalar value |
| `"A"`         | `&str`   | UTF-8 string slice   |
| `b'A'`        | `u8`     | một byte             |
| `b"A"`        | `&[u8]`  | byte string          |
| `"A".chars()` | iterator | `char`               |
| `"A".bytes()` | iterator | `u8`                 |

---

# 54. Mental model cuối buổi

Hãy nhớ:

```text
'A'
 │
 └── char
       │
       └── Unicode scalar value
```

```text
"A"
 │
 └── &str
       │
       └── UTF-8 bytes
```

```text
"A".chars()
 │
 └── Iterator<char>
```

```text
"A".bytes()
 │
 └── Iterator<u8>
```

Và:

```text
"你好🦀"
     │
     ├── len()
     │      ↓
     │    bytes
     │
     ├── chars()
     │      ↓
     │    Unicode scalar values
     │
     └── graphemes
            ↓
       user-perceived characters
```

---

# 55. Bài tập Buổi 8

### Bài 1

Xác định type:

```rust
let a = 'R';
let b = "R";
let c = b'R';
let d = b"R";
```

---

### Bài 2

Giải thích tại sao:

```rust
let text = "🦀";

println!("{}", text.len());
println!("{}", text.chars().count());
```

cho hai kết quả khác nhau.

---

### Bài 3

Viết function:

```rust
fn first_char(text: &str) -> Option<char>
```

Ví dụ:

```rust
first_char("Rust")
```

→

```text
Some('R')
```

và:

```rust
first_char("")
```

→

```text
None
```

---

### Bài 4

Viết function:

```rust
fn count_bytes_and_chars(text: &str)
```

in:

```text
bytes = ...
chars = ...
```

Thử với:

```text
"Hello"
"Xin chào"
"你好"
"🦀 Rust"
```

---

### Bài 5 — Deep Dive

Không chạy chương trình, hãy phân tích:

```rust
fn inspect(text: &str) {
    println!("len = {}", text.len());

    for c in text.chars() {
        println!("{c}");
    }

    for b in text.bytes() {
        println!("{b}");
    }
}

fn main() {
    inspect("é");
}
```

Hãy giải thích chính xác:

```text
1. &str chứa gì?
2. len() trả về gì?
3. chars() trả về gì?
4. bytes() trả về gì?
5. Tại sao 'é' là 1 char nhưng 2 bytes?
6. char có kích thước bao nhiêu?
7. Vì sao String của Rust lưu UTF-8 thay vì Vec<char>?
```

**Buổi 9** chúng ta sẽ đi sâu vào **String Slice — `&str`**, đặc biệt là `&str` được tạo như thế nào từ `String`, slicing bằng range, UTF-8 boundary, tại sao `&s[0..1]` có thể panic và cơ chế **borrowed string slice + memory layout**.
