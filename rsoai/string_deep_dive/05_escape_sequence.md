# Rust String Deep Dive — Buổi 5

## Escape Sequence, Unicode Escape và String Literal Parsing

Ở 4 buổi trước, ta đã xây dựng nền tảng:

```text
"hello"
   ↓
&'static str
   ↓
UTF-8 bytes
```

và hiểu:

```text
String / str
    ↓
UTF-8
    ↓
bytes
    ↓
chars / Unicode scalar values
```

Hôm nay ta đi sâu vào **cách viết các ký tự đặc biệt trong string literal** và quan trọng hơn:

> **Escape sequence là cú pháp của Rust source code, không phải một ký tự đặc biệt được lưu nguyên xi trong string.**

---

# 1. Escape sequence là gì?

Ví dụ:

```rust
let s = "Hello\nRust";
```

Trong source code, ta thấy:

```text
\
n
```

Nhưng giá trị thực tế của string là:

```text
Hello
Rust
```

Tức là:

```text
"\n"
```

được compiler diễn giải thành:

```text
newline character
```

Mental model:

```text
Rust source
    │
    ▼
"Hello\nRust"
    │
    │ compiler parses escape
    ▼
UTF-8 string value
    │
    ▼
Hello
Rust
```

---

# 2. Các escape sequence cơ bản

Rust hỗ trợ các escape phổ biến:

| Escape     | Ý nghĩa              |
| ---------- | -------------------- |
| `\n`       | newline              |
| `\r`       | carriage return      |
| `\t`       | tab                  |
| `\\`       | backslash            |
| `\"`       | double quote         |
| `\0`       | null character       |
| `\xNN`     | byte có giá trị hex  |
| `\u{NNNN}` | Unicode scalar value |

Ta sẽ lần lượt phân tích.

---

# 3. `\n` — newline

Ví dụ:

```rust
fn main() {
    println!("Hello\nRust");
}
```

Output:

```text
Hello
Rust
```

String thực tế chứa:

```text
H e l l o \n R u s t
```

Trong đó:

```text
\n
```

là một ký tự newline.

---

# 4. `\n` không phải hai ký tự

Đây là một điểm quan trọng.

Trong:

```rust
let s = "A\nB";
```

không phải có:

```text
A
\
n
B
```

mà có:

```text
A
newline
B
```

Vì vậy:

```rust
assert_eq!("A\nB".len(), 3);
```

Có:

```text
A       → 1 byte
newline → 1 byte
B       → 1 byte
```

Tổng:

```text
3 bytes
```

---

# 5. `\r` — carriage return

```rust
let s = "Hello\rRust";
```

`\r` là carriage return.

Khái niệm này xuất phát từ terminal/typewriter và đặc biệt quan trọng khi xử lý newline giữa các hệ điều hành.

Hai dạng newline phổ biến:

```text
Unix/Linux/macOS:
\n

Windows:
\r\n
```

Ví dụ:

```rust
let unix = "Hello\nRust";
let windows = "Hello\r\nRust";
```

Đây là lý do khi xử lý file text, bạn có thể gặp:

```text
\n
```

hoặc:

```text
\r\n
```

---

# 6. `\t` — tab

```rust
fn main() {
    println!("Name:\tRust");
    println!("Version:\t1.0");
}
```

Có thể hiển thị:

```text
Name:   Rust
Version:    1.0
```

`\t` là một tab character.

---

# 7. `\\` — backslash

Muốn string chứa:

```text
\
```

thì source code phải viết:

```rust
let path = "C:\\Users\\Rust";
```

Giá trị thực tế:

```text
C:\Users\Rust
```

Tại sao cần `\\`?

Vì:

```text
\
```

là ký hiệu bắt đầu escape.

Do đó:

```rust
"\"
```

không hợp lệ theo cách bạn mong muốn.

Còn:

```rust
"\\"
```

nghĩa là:

```text
một backslash
```

---

# 8. `\"` — double quote

String literal Rust dùng:

```rust
"..."
```

Do đó nếu muốn chứa dấu:

```text
"
```

phải escape:

```rust
let s = "Rust says: \"Hello\"";
```

Giá trị:

```text
Rust says: "Hello"
```

---

# 9. `\'` thì sao?

Trong Rust, `'` không cần escape trong double-quoted string:

```rust
let s = "It's Rust";
```

hoàn toàn hợp lệ.

Bạn chủ yếu gặp:

```rust
'\n'
'\t'
'\\'
'\''
```

khi làm việc với **character literal**.

Ví dụ:

```rust
let quote = '\'';
```

Ở đây:

```text
'...' 
```

là `char`, nên `'` bên trong cần escape.

---

# 10. `\0` — null character

Rust hỗ trợ:

```rust
let s = "hello\0world";
```

String này hoàn toàn hợp lệ.

Nó chứa:

```text
hello
NULL
world
```

Điểm cực kỳ quan trọng:

> Rust string không dùng null byte để đánh dấu kết thúc string.

Khác với C.

---

# 11. Rust String vs C String

C thường sử dụng:

```text
"hello\0"
```

để xác định string kết thúc ở đâu.

Rust thì:

```text
&str
=
pointer + length
```

Do đó:

```rust
let s = "hello\0world";
```

hoàn toàn hợp lệ.

Rust biết:

```text
length = 11
```

và không cần tìm `\0`.

Mental model:

```text
C string
┌───────────────────────┐
│ h e l l o \0          │
└───────────────────────┘
                ↑
             terminator


Rust &str
┌───────────────────────┐
│ pointer + length      │
└───────────────────────┘
        │
        ▼
h e l l o \0 w o r l d
```

---

# 12. `\xNN` — byte hexadecimal

Rust cho phép escape byte bằng:

```text
\xNN
```

Trong đó:

```text
NN
```

là hai chữ số hexadecimal.

Ví dụ:

```rust
let s = "\x41";
```

`0x41` là:

```text
A
```

Do đó:

```rust
assert_eq!("\x41", "A");
```

---

# 13. Ví dụ `\x`

```rust
fn main() {
    let a = "\x41";
    let b = "\x42";
    let c = "\x43";

    println!("{a}{b}{c}");
}
```

Output:

```text
ABC
```

Bởi vì:

```text
0x41 → A
0x42 → B
0x43 → C
```

---

# 14. `\xNN` có giới hạn

Đây là phần cần chú ý.

`\xNN` biểu diễn **một byte**, không phải tùy ý một Unicode character.

Ví dụ ASCII:

```rust
let a = "\x41";
```

rất đơn giản.

Nhưng với Unicode:

```text
é
```

UTF-8 cần nhiều byte.

Do đó bạn không nên nghĩ:

```text
\xE9
```

tự động có nghĩa:

```text
é
```

Trong UTF-8, Unicode character và byte representation là hai tầng khác nhau.

Đây là lý do Rust còn có Unicode escape:

```text
\u{...}
```

---

# 15. Unicode escape `\u{...}`

Rust cho phép:

```rust
let heart = "\u{2764}";
```

Kết quả:

```text
❤
```

Hoặc:

```rust
let rocket = "\u{1F680}";
```

Kết quả:

```text
🚀
```

Đây là cách biểu diễn **Unicode scalar value**.

---

# 16. Ví dụ Unicode escape

```rust
fn main() {
    let a = "\u{41}";
    let b = "\u{00E9}";
    let c = "\u{4F60}";
    let d = "\u{1F680}";

    println!("{a}");
    println!("{b}");
    println!("{c}");
    println!("{d}");
}
```

Kết quả:

```text
A
é
你
🚀
```

---

# 17. `\u{}` khác `\xNN`

Đây là điểm cần thuộc:

```text
\xNN
```

→ byte escape.

Trong khi:

```text
\u{NNNN}
```

→ Unicode scalar value escape.

Mental model:

```text
\x41
 ↓
byte 0x41
 ↓
A
```

Trong khi:

```text
\u{1F680}
 ↓
Unicode scalar value
 ↓
🚀
 ↓
UTF-8 encoding
 ↓
4 bytes
```

---

# 18. Unicode escape không phải UTF-8 byte sequence

Ví dụ:

```rust
let rocket = "\u{1F680}";
```

Source code chứa:

```text
\u{1F680}
```

Compiler hiểu:

```text
Unicode scalar value U+1F680
```

Sau đó string được biểu diễn bằng UTF-8.

Do đó:

```rust
assert_eq!(rocket.chars().count(), 1);
assert_eq!(rocket.len(), 4);
```

Ta có:

```text
1 Unicode scalar value
4 UTF-8 bytes
```

---

# 19. Unicode escape có thể viết ngắn

Ví dụ:

```rust
"\u{41}"
```

tương đương:

```rust
"A"
```

Không nhất thiết phải viết đủ:

```text
\u{0041}
```

Bạn có thể viết:

```text
\u{41}
```

Miễn là code point hợp lệ.

---

# 20. Escape trong `char`

Các escape sequence cũng áp dụng cho character literal.

Ví dụ:

```rust
let newline = '\n';
let tab = '\t';
let quote = '\'';
let slash = '\\';
```

Type của tất cả là:

```text
char
```

---

# 21. `char` và string escape

So sánh:

```rust
let a = '\n';
let b = "\n";
```

Type:

```text
a → char
b → &str
```

Nhưng giá trị biểu diễn cùng một newline character.

Mental model:

```text
'\n'
 ↓
one Unicode scalar value

"\n"
 ↓
string containing one character
```

---

# 22. Escape Unicode trong `char`

```rust
let rocket = '\u{1F680}';
```

Đây là một `char`.

```rust
println!("{rocket}");
```

Output:

```text
🚀
```

Ta có:

```rust
assert_eq!(rocket, '🚀');
```

---

# 23. Escape sequence được compiler xử lý

Một mental model:

```text
Source code
    │
    ▼
"Hello\nRust"
    │
    ▼
lexer/parser
    │
    ▼
newline character
    │
    ▼
UTF-8 representation
```

Điều này rất quan trọng khi đọc source code.

Bạn nhìn thấy:

```text
\n
```

nhưng runtime string không chứa hai ký tự:

```text
\
n
```

trừ khi bạn viết:

```rust
"\\n"
```

---

# 24. `"\n"` vs `"\\n"`

Đây là bài tập kinh điển.

### Trường hợp 1

```rust
let a = "\n";
```

Giá trị:

```text
newline
```

### Trường hợp 2

```rust
let b = "\\n";
```

Giá trị:

```text
\n
```

Tức là:

```text
backslash
+
n
```

Do đó:

```rust
println!("{:?}", a);
println!("{:?}", b);
```

sẽ giúp bạn quan sát representation.

---

# 25. `Debug` rất hữu ích khi học escape

Ví dụ:

```rust
fn main() {
    let a = "\n";
    let b = "\\n";

    println!("{a:?}");
    println!("{b:?}");
}
```

Bạn có thể thấy dạng escaped representation.

Đây là kỹ thuật rất hữu ích khi debug string.

---

# 26. Escape và `println!`

Có hai tầng cần phân biệt:

```text
Rust string literal
+
formatting macro
```

Ví dụ:

```rust
println!("Hello\nRust");
```

Compiler xử lý literal:

```text
"Hello\nRust"
```

thành string có newline.

Sau đó `println!` in nó.

---

# 27. `println!` tự thêm newline

Ví dụ:

```rust
println!("Hello");
```

Bạn không cần:

```rust
println!("Hello\n");
```

vì `println!` tự thêm newline cuối output.

Nếu viết:

```rust
println!("Hello\n");
```

thì sẽ có thêm newline.

Có thể hình dung:

```text
"Hello\n"
        +
println!'s newline
        ↓
hai newline
```

---

# 28. `print!` khác `println!`

```rust
print!("Hello");
print!("Rust");
```

Output:

```text
HelloRust
```

Trong khi:

```rust
println!("Hello");
println!("Rust");
```

Output:

```text
Hello
Rust
```

Do `println!` tự thêm `\n`.

---

# 29. Escape backslash trong Windows path

Một ví dụ thực tế:

```rust
let path = "C:\\Users\\Garden\\Documents";
```

Giá trị:

```text
C:\Users\Garden\Documents
```

Nếu viết:

```rust
let path = "C:\Users\Garden";
```

sẽ gặp vấn đề vì `\` bắt đầu escape.

Đây là một trong những trường hợp raw string cực kỳ hữu ích.

---

# 30. Raw String

Rust có:

```rust
r"..."
```

Ví dụ:

```rust
let path = r"C:\Users\Garden\Documents";
```

Không cần:

```text
\\
```

Giá trị chính là:

```text
C:\Users\Garden\Documents
```

---

# 31. Raw string không xử lý escape thông thường

Ví dụ:

```rust
let s = r"Hello\nRust";
```

Đây **không phải**:

```text
Hello
Rust
```

mà là literal text:

```text
Hello\nRust
```

Tức là hai ký tự:

```text
\
n
```

---

# 32. So sánh

```rust
let a = "Hello\nRust";
let b = r"Hello\nRust";
```

### `a`

```text
Hello
Rust
```

### `b`

```text
Hello\nRust
```

Mental model:

```text
"..." 
 ↓
escape được diễn giải

r"..."
 ↓
escape không được diễn giải theo cách thông thường
```

---

# 33. Raw string rất hữu ích cho regex

Ví dụ regex:

```text
\d+\.\d+
```

Nếu dùng regular string:

```rust
let pattern = "\\d+\\.\\d+";
```

Khó đọc.

Raw string:

```rust
let pattern = r"\d+\.\d+";
```

dễ đọc hơn rất nhiều.

---

# 34. Raw string với JSON

Ví dụ:

```rust
let json = r#"{"name":"Rust","version":"1.0"}"#;
```

Ta không cần escape toàn bộ dấu `"`.

Đây là một use case cực kỳ quan trọng.

---

# 35. Raw string có `#`

Rust hỗ trợ:

```rust
r#"..."#
```

hoặc:

```rust
r##"..."##
```

Tại sao?

Để cho phép chứa:

```text
"
```

mà không kết thúc string.

Ví dụ:

```rust
let s = r#"He said "Hello""#;
```

Giá trị:

```text
He said "Hello"
```

---

# 36. Quy tắc raw string

Cơ bản:

```rust
r"hello"
```

Nếu nội dung chứa:

```text
"
```

có thể dùng:

```rust
r#"hello "world""#
```

Nếu nội dung chứa:

```text
"#
```

có thể tăng số lượng `#`:

```rust
r##"hello "# world"##
```

Mental model:

```text
r#"... " ... "#
 ^^          ^^
```

Số lượng `#` ở đầu và cuối phải khớp.

---

# 37. Raw string không phải "không escape tuyệt đối"

Cách nói chính xác hơn:

> Raw string không diễn giải các escape sequence thông thường.

Ví dụ:

```rust
r"\n"
```

chứa:

```text
\
n
```

chứ không phải newline.

Nhưng syntax của raw string vẫn có quy tắc delimiter:

```text
r#"..."#
```

Do đó `"` và `#` vẫn liên quan đến việc kết thúc literal.

---

# 38. Raw byte string

Ngoài:

```rust
r"..."
```

Rust còn có:

```rust
br"..."
```

Đây là **raw byte string literal**.

Ví dụ:

```rust
let data = br"hello\nworld";
```

Type là:

```text
&[u8; N]
```

theo kiểu literal array reference.

Khi coerced có thể dùng như:

```text
&[u8]
```

Đây là chủ đề byte string riêng, ta sẽ đào sâu sau.

---

# 39. Byte string bình thường

Rust có:

```rust
b"hello"
```

Ví dụ:

```rust
let bytes = b"Hello";
```

Đây không phải:

```text
&str
```

mà là byte string literal.

Mental model:

```text
"Hello"
 ↓
&str
 ↓
UTF-8 text

b"Hello"
 ↓
byte array
 ↓
[u8]
```

---

# 40. Vì sao byte string hữu ích?

Khi làm việc với:

* binary protocol
* network packet
* file format
* C APIs
* raw bytes
* cryptography
* serialization

bạn thường không muốn Rust tự coi dữ liệu là UTF-8 text.

Ví dụ:

```rust
let magic = b"PNG";
```

Đây là bytes:

```text
P → 80
N → 78
G → 71
```

---

# 41. Escape Unicode và UTF-8 — tổng hợp

Ví dụ:

```rust
let s = "\u{1F680}";
```

Quá trình khái niệm:

```text
source
  │
  ▼
\u{1F680}
  │
  ▼
Unicode scalar value
  │
  ▼
🚀
  │
  ▼
UTF-8
  │
  ▼
4 bytes
```

Đây là pipeline rất quan trọng.

---

# 42. Escape không thay đổi bản chất `str`

Ví dụ:

```rust
let a = "é";
let b = "\u{E9}";
```

Hai string này có cùng giá trị:

```rust
assert_eq!(a, b);
```

Cả hai đều là:

```text
&str
```

và đều được biểu diễn bằng UTF-8.

Khác biệt chỉ nằm ở:

```text
source representation
```

---

# 43. Ví dụ cực kỳ quan trọng

```rust
let a = "é";
let b = "\u{E9}";
let c = "\xC3\xA9";
```

Về ý tưởng:

```text
a
 ↓
literal character

b
 ↓
Unicode scalar value

c
 ↓
UTF-8 bytes
```

Cả ba có thể biểu diễn cùng nội dung Unicode nếu byte escape tạo ra UTF-8 hợp lệ.

Điểm này giúp bạn phân biệt:

```text
character-level escape
vs
byte-level escape
```

---

# 44. Nhưng hãy cẩn thận với `\x`

`\xNN` là byte-oriented.

Do đó:

```rust
"\xC3\xA9"
```

tạo hai bytes:

```text
C3 A9
```

đây là UTF-8 encoding của:

```text
é
```

Trong khi:

```rust
"\u{E9}"
```

nói trực tiếp:

```text
Unicode scalar value U+00E9
```

Compiler sau đó encode thành UTF-8.

Hai cách khác nhau về tầng biểu diễn.

---

# 45. Một nguyên tắc rất quan trọng

Khi làm việc với Rust text:

```text
Source syntax
      ↓
Unicode scalar values
      ↓
UTF-8 bytes
```

Escape sequence chủ yếu nằm ở tầng:

```text
Source syntax
```

Ví dụ:

```text
\n
\u{E9}
\xC3
```

Compiler chuyển chúng thành giá trị string thực tế.

---

# 46. Escape sequence trong format string

Ví dụ:

```rust
let name = "Rust";

println!("Hello, {name}\nWelcome!");
```

Ở đây có:

```text
{name}
```

là format syntax.

Còn:

```text
\n
```

là string escape.

Hai cơ chế khác nhau.

```text
"{name}\n"
   │       │
   │       └── escape sequence
   │
   └────────── formatting capture
```

---

# 47. Một ví dụ hoàn chỉnh

```rust
fn main() {
    let name = "Rust";
    let path = r"C:\Users\Rust";
    let quote = "Rust says: \"Hello\"";
    let rocket = "\u{1F680}";

    println!("Name: {name}");
    println!("Path: {path}");
    println!("Quote: {quote}");
    println!("Rocket: {rocket}");
}
```

Kết quả:

```text
Name: Rust
Path: C:\Users\Rust
Quote: Rust says: "Hello"
Rocket: 🚀
```

---

# 48. Bảng tổng kết escape

| Syntax   | Kết quả                 |
| -------- | ----------------------- |
| `\n`     | newline                 |
| `\r`     | carriage return         |
| `\t`     | tab                     |
| `\\`     | `\`                     |
| `\"`     | `"`                     |
| `\0`     | null byte               |
| `\x41`   | byte `0x41`             |
| `\u{41}` | Unicode scalar `U+0041` |

Đặc biệt:

```text
\xNN
```

là byte-oriented.

```text
\u{...}
```

là Unicode scalar-oriented.

---

# 49. Bài tập Buổi 5

## Bài 1 — Dự đoán kết quả

```rust
fn main() {
    let a = "\n";
    let b = "\\n";
    let c = "\"";
    let d = "\\";
    
    println!("{a:?}");
    println!("{b:?}");
    println!("{c:?}");
    println!("{d:?}");
}
```

Giải thích từng giá trị.

---

## Bài 2 — Unicode

Viết `"🚀"` bằng Unicode escape:

```rust
let rocket = ???;
```

Sau đó kiểm tra:

```rust
assert_eq!(rocket.chars().count(), 1);
assert_eq!(rocket.len(), 4);
```

---

## Bài 3 — Hex escape

Viết:

```text
ABC
```

bằng `\xNN`.

Gợi ý:

```text
A = 0x41
B = 0x42
C = 0x43
```

---

## Bài 4 — So sánh

Giải thích sự khác nhau:

```rust
let a = "\n";
let b = "\\n";
let c = r"\n";
```

---

## Bài 5 — Raw string

Viết string chứa chính xác:

```text
C:\Users\Garden\Documents\rust\main.rs
```

theo **hai cách**:

### Cách 1

Regular string.

### Cách 2

Raw string.

---

# 50. Deep Dive Challenge

Không chạy chương trình, hãy phân tích:

```rust
fn main() {
    let a = "\u{41}";
    let b = "\x41";
    let c = "A";

    println!("{}", a == b);
    println!("{}", b == c);

    println!("{}", a.len());
    println!("{}", b.len());
    println!("{}", c.len());
}
```

Hãy trả lời:

```text
1. a có giá trị gì?
2. b có giá trị gì?
3. c có giá trị gì?
4. a == b?
5. b == c?
6. a.len()?
7. b.len()?
8. c.len()?
```

---

# 51. Mental model cuối Buổi 5

Bạn cần hình thành được mô hình:

```text
                    Rust source
                        │
              ┌─────────┼─────────┐
              │         │         │
             \n        \xNN     \u{...}
              │         │         │
              ▼         ▼         ▼
           character   byte   Unicode scalar
              │         │         │
              └─────────┼─────────┘
                        ▼
                   UTF-8 bytes
                        │
                        ▼
                      &str
```

Và phân biệt:

```text
"..."       → normal string literal
r"..."      → raw string literal
b"..."      → byte string literal
br"..."     → raw byte string literal
```

Một insight rất quan trọng:

> **Escape sequence là cách biểu diễn dữ liệu trong source code; sau khi compiler xử lý literal, runtime chủ yếu làm việc với giá trị string/UTF-8 bytes chứ không biết rằng bạn đã viết `\u{E9}` hay trực tiếp viết `é`.**

**Buổi 6** sẽ đi sâu toàn bộ **Raw String Literal `r"..."`, `r#"..."#`, nhiều `#`, delimiter parsing, multiline raw string, JSON/regex/HTML/SQL thực tế và khi nào raw string thực sự tốt hơn regular string.**
