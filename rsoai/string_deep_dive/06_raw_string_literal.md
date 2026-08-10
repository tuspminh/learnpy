# Rust String Deep Dive — Buổi 6

## Raw String Literal — `r"..."`, `r#"..."#`, `r##"..."##`

Hôm nay ta đào sâu **Raw String Literal**. Đây là phần rất thực tế khi bạn làm Rust với:

* Regex
* JSON
* HTML
* SQL
* Windows path
* Template
* JavaScript/CSS nhúng
* Code generation
* Configuration
* Embedded text

Mục tiêu cuối buổi: nhìn vào một đoạn như:

```rust
let json = r##"{"name":"Rust","pattern":"\d+\.\d+"}"##;
```

và hiểu **chính xác compiler đang parse nó như thế nào**.

---

# 1. Raw string literal là gì?

String bình thường:

```rust
let s = "Hello\nRust";
```

Rust xử lý:

```text
\n
```

thành newline.

Raw string:

```rust
let s = r"Hello\nRust";
```

thì:

```text
\n
```

được giữ nguyên.

Giá trị là:

```text
Hello\nRust
```

Mental model:

```text
Normal string:

"Hello\nRust"
       │
       ▼
    escape
       │
       ▼
Hello
Rust


Raw string:

r"Hello\nRust"
       │
       ▼
không xử lý \n
       │
       ▼
Hello\nRust
```

---

# 2. Syntax cơ bản

Cú pháp đơn giản nhất:

```rust
r"hello"
```

Ví dụ:

```rust
fn main() {
    let s = r"Hello\nRust";

    println!("{s}");
}
```

Output:

```text
Hello\nRust
```

Không xuống dòng.

---

# 3. So sánh trực tiếp

```rust
fn main() {
    let normal = "Hello\nRust";
    let raw = r"Hello\nRust";

    println!("normal:");
    println!("{normal}");

    println!("raw:");
    println!("{raw}");
}
```

Kết quả:

```text
normal:
Hello
Rust

raw:
Hello\nRust
```

Đây là khác biệt cốt lõi.

---

# 4. Raw string không có escape processing thông thường

Ví dụ:

```rust
let s = r"\n\t\\\"";
```

Tất cả những thứ này:

```text
\n
\t
\\
\"
```

được coi như text.

Vì vậy string chứa:

```text
\
n
\
t
\
\
\
"
```

Nói cách khác:

> Trong raw string, backslash không còn là escape character theo cách của normal string literal.

---

# 5. Vì sao cần raw string?

Hãy xem Windows path.

Normal string:

```rust
let path = "C:\\Users\\Garden\\Rust\\src";
```

Ta phải escape:

```text
\
```

thành:

```text
\\
```

Raw string:

```rust
let path = r"C:\Users\Garden\Rust\src";
```

dễ đọc hơn nhiều.

---

# 6. Regex là use case kinh điển

Giả sử regex:

```text
\d+\.\d+
```

Normal string:

```rust
let pattern = "\\d+\\.\\d+";
```

Có hai tầng escape:

```text
Rust string
    ↓
regex
```

Ta phải escape cho Rust trước.

Raw string:

```rust
let pattern = r"\d+\.\d+";
```

Regex engine nhận đúng:

```text
\d+\.\d+
```

Code dễ đọc hơn rất nhiều.

---

# 7. Hai parser cùng tồn tại

Đây là insight rất quan trọng.

Với:

```rust
let pattern = "\\d+\\.\\d+";
```

có:

```text
Rust parser
     ↓
"d+..."
     ↓
Regex parser
```

Bạn phải suy nghĩ về **hai ngôn ngữ escape**.

Với:

```rust
let pattern = r"\d+\.\d+";
```

Rust không xử lý backslash.

Do đó regex engine nhận text gần như trực tiếp.

---

# 8. JSON

JSON thường chứa rất nhiều dấu `"`.

Ví dụ:

```json
{"name":"Rust","version":"1.0"}
```

Normal Rust string:

```rust
let json = "{\"name\":\"Rust\",\"version\":\"1.0\"}";
```

Khá khó đọc.

Raw string:

```rust
let json = r#"{"name":"Rust","version":"1.0"}"#;
```

Dễ đọc hơn rất nhiều.

---

# 9. Tại sao JSON cần `#`?

Bạn có:

```text
r"..."
```

Nhưng JSON chứa:

```text
"
```

Ví dụ:

```rust
r"{"name":"Rust"}"
```

Compiler sẽ không biết:

```text
"
```

nào là quote trong nội dung và quote kết thúc string.

Do đó Rust cho phép thêm `#`:

```rust
r#"{"name":"Rust"}"#
```

Delimiter trở thành:

```text
r#"
...
"#
```

---

# 10. Cấu trúc `r#"..."#`

Hãy nhìn thật kỹ:

```rust
r#"hello"#
```

Cấu trúc:

```text
r
#
"
──────── content ────────
"
#
```

Hay:

```text
r#" CONTENT "#
```

`#` là một phần của **delimiter**, không phải content.

Do đó giá trị string chỉ là:

```text
CONTENT
```

---

# 11. Một `#`

Ví dụ:

```rust
let s = r#"Hello "Rust""#;
```

Giá trị:

```text
Hello "Rust"
```

Không cần:

```rust
\"Rust\"
```

---

# 12. Hai `#`

Bạn có thể dùng:

```rust
let s = r##"Hello "Rust" ## world"##;
```

Delimiter:

```text
r##"
...
"##
```

Nội dung:

```text
Hello "Rust" ## world
```

---

# 13. Nhiều `#`

Rust cho phép nhiều `#`:

```rust
r###"content"###
```

hoặc:

```rust
r#####"content"#####
```

v.v.

Quy tắc:

```text
số # ở đầu = số # ở cuối
```

Ví dụ:

```rust
r###"hello"###
```

hợp lệ.

Nhưng:

```rust
r###"hello"##
```

không hợp lệ.

---

# 14. Tại sao cần nhiều `#`?

Giả sử nội dung có:

```text
"#
```

Ví dụ:

```text
Hello "#
World
```

Nếu dùng:

```rust
r#"Hello "# World"#
```

thì delimiter:

```text
"#
```

đã xuất hiện trong content.

Compiler có thể coi đó là kết thúc string.

Giải pháp:

```rust
r##"Hello "# World"##
```

Bây giờ delimiter kết thúc là:

```text
"##
```

Trong content chỉ có:

```text
"#
```

nên không kết thúc string.

---

# 15. Đây chính là mục đích của `#`

Mental model:

```text
r"..."          delimiter = "
r#"..."#        delimiter = "#
r##"..."##      delimiter = "##
r###"..."###    delimiter = "###
```

Càng nhiều `#`:

```text
→ delimiter càng khó xuất hiện trong content
```

---

# 16. Compiler xác định delimiter thế nào?

Ví dụ:

```rust
r##"hello"## 
```

Compiler đọc:

```text
r
##
"
```

và biết:

> String này kết thúc khi gặp `"##`.

Nó không kết thúc tại một dấu:

```text
"
```

đơn lẻ.

Đây là bản chất của raw string delimiter.

---

# 17. Ví dụ

```rust
fn main() {
    let s = r##"He said "Hello" and wrote "#END""##;

    println!("{s}");
}
```

Giá trị:

```text
He said "Hello" and wrote "#END"
```

Vì delimiter là:

```text
"##
```

Trong content:

```text
"#
```

không đủ để đóng string.

---

# 18. Raw string multiline

Raw string rất phù hợp với text nhiều dòng.

Ví dụ:

```rust
let text = r#"
Hello
Rust
World
"#;
```

Giá trị thực sự bắt đầu bằng newline:

```text

Hello
Rust
World

```

Chú ý:

> newline sau `r#"` cũng là một phần của string.

---

# 19. Indentation cũng là content

Ví dụ:

```rust
let text = r#"
    Hello
    Rust
    World
"#;
```

String chứa cả:

```text
newline
4 spaces
Hello
newline
4 spaces
Rust
...
```

Raw string **không tự động loại bỏ indentation**.

Đây là điểm cần nhớ khi dùng raw string cho template.

---

# 20. HTML template

Ví dụ:

```rust
let html = r#"
<!DOCTYPE html>
<html>
<head>
    <title>Rust</title>
</head>
<body>
    <h1>Hello Rust</h1>
</body>
</html>
"#;
```

Đây là use case rất phổ biến.

Bạn không cần escape:

```text
"
```

trong HTML attribute.

---

# 21. HTML có attribute quotes

Ví dụ:

```rust
let html = r#"<div class="container">Hello</div>"#;
```

Nếu dùng normal string:

```rust
let html = "<div class=\"container\">Hello</div>";
```

Raw string dễ đọc hơn:

```text
r#"<div class="container">Hello</div>"#
```

---

# 22. JavaScript nhúng

Ví dụ:

```rust
let script = r#"
<script>
    const message = "Hello Rust";
    console.log(message);
</script>
"#;
```

Normal string sẽ cần escape nhiều dấu quote.

Raw string giúp giữ nguyên source.

---

# 23. CSS nhúng

```rust
let css = r#"
body {
    font-family: "Arial";
    margin: 0;
    padding: 0;
}
"#;
```

Rất tiện khi viết template hoặc test.

---

# 24. SQL

Ví dụ:

```rust
let sql = r#"
SELECT *
FROM users
WHERE name = 'Rust';
"#;
```

Raw string giúp SQL giữ nguyên format.

Đặc biệt hữu ích khi query dài:

```rust
let sql = r#"
SELECT
    id,
    username,
    email,
    created_at
FROM users
WHERE active = 1
ORDER BY created_at DESC;
"#;
```

---

# 25. Nhưng raw string không phải lúc nào cũng tốt

Ví dụ:

```rust
let name = "Rust";

let message = r#"Hello, {name}"#;
```

Kết quả là:

```text
Hello, {name}
```

Không tự interpolation.

Raw string chỉ thay đổi cách Rust parse literal.

Nó không biến string thành template engine.

---

# 26. Raw string + format!

Bạn có thể kết hợp:

```rust
let name = "Rust";

let message = format!(
    r#"Hello, {name}"#
);
```

Với Rust format syntax hiện đại, `{name}` vẫn được xử lý bởi `format!`.

Điểm quan trọng:

```text
raw string
```

chỉ kiểm soát **literal parsing**.

Còn:

```text
format!
```

là một cơ chế khác.

---

# 27. Raw string không phải runtime feature

Đây là insight quan trọng.

```rust
r"hello"
```

không phải một object đặc biệt tại runtime.

Nó chỉ là:

> **cú pháp literal của Rust source code.**

Sau khi compiler xử lý, bạn vẫn có:

```text
&str
```

Ví dụ:

```rust
let a = "hello";
let b = r"hello";

assert_eq!(a, b);
```

Hai giá trị giống nhau.

---

# 28. Type của raw string

```rust
let s = r"Hello";
```

Type:

```text
&str
```

Thông thường là:

```text
&'static str
```

nếu literal nằm trực tiếp trong code.

Không có type mới như:

```text
RawString
```

Rust không có type runtime riêng cho raw string literal.

---

# 29. Raw string và normal string có cùng runtime representation

Ví dụ:

```rust
let a = "Hello\n";
let b = r"Hello
";
```

Hai string có thể có cùng giá trị nếu nội dung cuối cùng giống nhau.

Compiler không giữ metadata kiểu:

```text
"string này được viết bằng raw literal"
```

Sau compile, đó chỉ là string data.

---

# 30. Raw string và UTF-8

Raw string vẫn là UTF-8.

Ví dụ:

```rust
let s = r"Xin chào 🚀";
```

vẫn là:

```text
&str
   ↓
UTF-8
```

Raw string chỉ ảnh hưởng:

```text
source-level escape parsing
```

Nó không thay đổi encoding.

---

# 31. Raw string không có nghĩa "ASCII"

Sai:

```text
raw string = không UTF-8
```

Đúng:

```text
raw string
    ↓
vẫn là Rust str
    ↓
vẫn UTF-8
```

Ví dụ:

```rust
let s = r"你好 🚀";
```

hoàn toàn hợp lệ.

---

# 32. Raw string với Unicode

Bạn có thể viết trực tiếp:

```rust
let s = r"Xin chào 世界 🚀";
```

và:

```rust
println!("{}", s.len());
println!("{}", s.chars().count());
```

Kết quả `len()` vẫn tính byte UTF-8.

Raw string không thay đổi quy tắc này.

---

# 33. Raw string và `\u{}`

Đây là điểm rất dễ nhầm.

Normal:

```rust
let a = "\u{1F680}";
```

→ `🚀`

Raw:

```rust
let b = r"\u{1F680}";
```

→ text:

```text
\u{1F680}
```

Không chuyển thành rocket.

Đây là bằng chứng rõ nhất:

```text
normal string
    ↓
escape processing

raw string
    ↓
literal text
```

---

# 34. Raw string và `\n`

Tương tự:

```rust
let a = "\n";
let b = r"\n";
```

Ta có:

```text
a
↓
newline

b
↓
backslash + n
```

Do đó:

```rust
assert_ne!(a, b);
```

---

# 35. Raw string và backslash

Ví dụ Windows path:

```rust
let path = r"C:\Users\Rust";
```

Không cần:

```rust
C:\\Users\\Rust
```

Đây là lý do raw strings đặc biệt hữu ích cho:

```text
regex
Windows paths
LaTeX
shell commands
JSON
HTML
SQL
```

---

# 36. Raw string với regex — phân tích sâu

Giả sử regex:

```text
^\d{4}-\d{2}-\d{2}$
```

Normal:

```rust
let pattern = "^\\d{4}-\\d{2}-\\d{2}$";
```

Có hai ngôn ngữ:

```text
Rust:
\\ → \

Regex:
\d → digit
```

Raw:

```rust
let pattern = r"^\d{4}-\d{2}-\d{2}$";
```

Compiler không biến:

```text
\d
```

thành thứ gì khác.

Regex engine nhận:

```text
^\d{4}-\d{2}-\d{2}$
```

---

# 37. Raw string với JSON — phân tích sâu

Normal:

```rust
let json = "{\"name\":\"Rust\",\"age\":10}";
```

Rust phải xử lý:

```text
\"
```

để tạo:

```text
"
```

Raw:

```rust
let json = r#"{"name":"Rust","age":10}"#;
```

Rust không cần escape quote trong content vì delimiter là:

```text
"#
```

---

# 38. Khi nào cần tăng số `#`?

Quy tắc thực tế:

> Chọn số `#` đủ lớn để delimiter `"###...` không xuất hiện trong content.

Ví dụ content chứa:

```text
"#
```

dùng:

```rust
r##"..."##
```

Content chứa:

```text
"##
```

dùng:

```rust
r###"..."###
```

v.v.

---

# 39. Một ví dụ thực tế với Markdown

Markdown có thể chứa:

````text
```rust
fn main() {}
````

````

Bạn có thể nhúng:

```rust
let markdown = r#"
```rust
fn main() {
    println!("Hello");
}
````

"#;

````

Đây là một lý do raw strings rất hữu ích trong tool generate documentation.

---

# 40. Raw string trong code generator

Giả sử Rust program tạo ra Python code:

```rust
let python = r#"
def hello():
    print("Hello")
"#;
````

Bạn có thể giữ nguyên Python source.

Nếu dùng normal string:

```rust
let python = "\ndef hello():\n    print(\"Hello\")\n";
```

khó đọc hơn.

---

# 41. Raw string trong template engine

Ví dụ HTML:

```rust
let template = r#"
<!DOCTYPE html>
<html>
<body>
    <h1>{{ title }}</h1>
</body>
</html>
"#;
```

Template syntax:

```text
{{ title }}
```

được giữ nguyên.

Raw string không can thiệp vào:

```text
{{ ... }}
```

---

# 42. Một lỗi phổ biến

Nhiều người nghĩ:

```rust
r"hello\n"
```

sẽ tự động convert:

```text
\n
```

thành newline.

Không.

Nó giữ nguyên:

```text
\
n
```

Nếu muốn newline thực sự:

```rust
"hello\n"
```

---

# 43. Một lỗi phổ biến khác

Nghĩ rằng:

```rust
r#"..."#
```

có thể chứa bất kỳ thứ gì.

Không hoàn toàn.

Nó vẫn phải tuân thủ delimiter.

Nếu content chứa:

```text
"#
```

thì:

```rust
r#"content "# more"#
```

có thể kết thúc sớm.

Khi đó tăng số `#`:

```rust
r##"content "# more"##
```

---

# 44. Raw string không xử lý quote theo kiểu `\"`

Ví dụ:

```rust
let s = r#"Hello \"Rust\""#;
```

Giá trị **không phải**:

```text
Hello "Rust"
```

mà là:

```text
Hello \"Rust\"
```

Bởi vì:

```text
\"
```

trong raw string không phải escape.

Đây là một bài kiểm tra rất hay.

---

# 45. So sánh toàn diện

| Literal    |       `\n` |       `\"` |   `\u{41}` |
| ---------- | ---------: | ---------: | ---------: |
| `"..."`    | được xử lý | được xử lý | được xử lý |
| `r"..."`   | giữ nguyên | giữ nguyên | giữ nguyên |
| `r#"..."#` | giữ nguyên | giữ nguyên | giữ nguyên |

Khác nhau giữa:

```text
r"..."
r#"..."#
r##"..."##
```

không phải escape behavior.

Chúng đều là raw string.

Khác biệt chính là:

```text
delimiter
```

---

# 46. Normal string vs raw string

### Normal

```rust
let s = "C:\\Users\\Rust\nHello";
```

Source:

```text
C:\\Users\\Rust\nHello
```

Runtime:

```text
C:\Users\Rust
Hello
```

### Raw

```rust
let s = r"C:\Users\Rust\nHello";
```

Runtime:

```text
C:\Users\Rust\nHello
```

---

# 47. Một ví dụ lớn

```rust
fn main() {
    let html = r##"
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: "Arial";
        }
    </style>
</head>
<body>
    <h1>Hello Rust 🚀</h1>
</body>
</html>
"##;

    println!("{html}");
}
```

Điểm cần quan sát:

* nhiều dòng
* dấu `"`
* CSS
* HTML
* Unicode
* không cần escape backslash/quote

Đây là một use case thực tế của raw string.

---

# 48. Raw byte string

Ta có:

```rust
let data = br"Hello\nRust";
```

Khác:

```rust
let data = r"Hello\nRust";
```

Type khác nhau.

```text
r"..."
 ↓
&str

br"..."
 ↓
&[u8]
```

Ví dụ:

```rust
fn main() {
    let text = r"Hello\n";
    let bytes = br"Hello\n";

    println!("{}", text);
    println!("{:?}", bytes);
}
```

Text:

```text
Hello\n
```

Bytes tương ứng với:

```text
H e l l o \ n
```

---

# 49. Raw string không phải giải pháp cho mọi thứ

Ví dụ:

```rust
let message = r"Hello {name}";
```

Nếu bạn cần interpolation động, raw string không giúp.

Bạn cần:

```rust
format!("Hello {name}")
```

hoặc template engine.

Raw string giải quyết:

> **escaping ở source code**

chứ không giải quyết:

> **template rendering**

---

# 50. Khi nào nên dùng raw string?

### Nên dùng

Khi content chứa nhiều:

```text
\
"
\n
\t
regex syntax
HTML syntax
JSON quotes
SQL quotes
```

Đặc biệt:

```text
Regex
JSON
HTML
SQL
Windows path
Templates
Code generation
Multiline text
```

---

# 51. Khi nào không cần?

Nếu string đơn giản:

```rust
let name = "Rust";
```

không cần:

```rust
r"Rust"
```

Viết raw string trong trường hợp không cần thiết có thể làm code kém quen thuộc.

Thông thường:

```rust
"Hello"
```

tự nhiên hơn:

```rust
r"Hello"
```

---

# 52. Rule thực tế

Một quy tắc đơn giản:

```text
String đơn giản
    ↓
"..."

Nhiều escape
    ↓
r"..."

Có quote trong content
    ↓
r#"..."#

Có delimiter conflict
    ↓
r##"..."##
```

Đừng lạm dụng `#`.

---

# 53. Deep Dive: delimiter

Hãy hiểu chính xác:

```rust
r###"Hello"###
```

không phải:

```text
r
+
###"
+
Hello
+
"###
```

về mặt runtime.

`###` chỉ là một phần của **syntax delimiter**.

Runtime value chỉ là:

```text
Hello
```

Do đó:

```rust
let a = r"Hello";
let b = r#"Hello"#;
let c = r##"Hello"##;

assert_eq!(a, b);
assert_eq!(b, c);
```

---

# 54. Một insight về compiler

Khi compiler đọc:

```rust
r##"Hello \"Rust\""##
```

nó không xử lý:

```text
\"
```

như escape.

Content thực tế là:

```text
Hello \"Rust\"
```

Raw string parser chủ yếu cần xác định:

```text
opening delimiter
+
closing delimiter
+
content
```

Đây là điểm khác biệt căn bản với normal string literal parser.

---

# 55. Bài tập Buổi 6

## Bài 1

Dự đoán output:

```rust
fn main() {
    let a = "Hello\nRust";
    let b = r"Hello\nRust";

    println!("{a:?}");
    println!("{b:?}");
}
```

---

## Bài 2

Hai string này có bằng nhau không?

```rust
let a = "\u{1F680}";
let b = r"\u{1F680}";
```

Giải thích tại sao.

---

## Bài 3

Viết string:

```text
C:\Users\Garden\Documents\rust\main.rs
```

bằng:

1. normal string
2. raw string

---

## Bài 4

Viết JSON:

```json
{
    "name": "Rust",
    "language": "systems",
    "version": "1.0"
}
```

bằng raw string.

---

# 56. Bài tập nâng cao — Regex

Cho regex:

```text
^\d{4}-\d{2}-\d{2}$
```

Viết:

### Cách 1 — normal string

```rust
let pattern = ???;
```

### Cách 2 — raw string

```rust
let pattern = ???;
```

Sau đó giải thích tại sao cách 2 dễ đọc hơn.

---

# 57. Bài tập nâng cao — Raw delimiter

Hãy tạo một raw string chứa chính xác:

```text
Hello "Rust" "# "## "###
```

Yêu cầu:

* không dùng `\"`
* sử dụng raw string
* chọn số `#` tối thiểu cần thiết

Đây là bài tập rất tốt để kiểm tra bạn đã thực sự hiểu delimiter hay chưa.

---

# 58. Bài tập thực chiến

Viết:

```rust
fn main() {
    let html = ???;

    println!("{html}");
}
```

với HTML:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Rust String</title>
</head>
<body>
    <h1>Hello "Rust" 🚀</h1>
    <p>Path: C:\Users\Rust</p>
</body>
</html>
```

Yêu cầu:

* multiline
* giữ nguyên indentation
* không escape `"`
* không escape `\`
* sử dụng raw string

---

# 59. Kiến thức phải thuộc sau Buổi 6

### Normal string

```rust
"Hello\nRust"
```

Escape được xử lý.

### Raw string

```rust
r"Hello\nRust"
```

Escape không được xử lý.

### Raw string có delimiter

```rust
r#"Hello "Rust""#
```

### Nhiều delimiter

```rust
r##"Hello "# Rust"##
```

### Raw string vẫn là UTF-8

```text
r"..."
 ↓
&str
 ↓
UTF-8
```

### Raw string không phải runtime type riêng

```text
"Hello"
r"Hello"
r#"Hello"#
```

sau khi compile đều là string values bình thường.

---

# 60. Mental model cuối buổi

Hãy ghi nhớ:

```text
                    STRING LITERAL
                          │
             ┌────────────┴────────────┐
             │                         │
        normal string              raw string
             │                         │
          "..."                      r"..."
             │                         │
      escape processing          literal content
             │                         │
             └────────────┬────────────┘
                          ▼
                       &str
                          │
                          ▼
                        UTF-8
```

Và với raw string:

```text
r"..." 
r#"..."#
r##"..."##
r###"..."###
     │
     ▼
khác nhau chủ yếu ở delimiter
```

**Điểm quan trọng nhất của Buổi 6:**

> `r"..."` không làm String "đặc biệt" ở runtime. Nó chỉ nói với Rust compiler: **hãy coi phần nội dung này gần như nguyên văn và đừng diễn giải các escape sequence thông thường**.

Buổi tiếp theo nên đi vào **String Memory Model**: `&str` thực sự gồm **pointer + length** như thế nào, `String` gồm **pointer + length + capacity**, stack/heap, ownership, borrowing, `String → &str`, `&str → String`, `Deref`, và tại sao `String` có thể grow nhưng `&str` thì không.
