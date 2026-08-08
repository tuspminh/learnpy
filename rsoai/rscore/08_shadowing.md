# Rust Professional 2026

## Giai đoạn 1 — Rust Foundation

## Buổi 8 — Shadowing, `const` & `static` Deep Dive

Buổi này rất quan trọng vì chúng ta sẽ làm rõ ba cơ chế thường bị người mới trộn lẫn:

```text
let
  ↓
variable binding

let mut
  ↓
mutable binding

shadowing
  ↓
binding mới

const
  ↓
compile-time constant

static
  ↓
một vùng dữ liệu có địa chỉ cố định trong toàn chương trình
```

---

# 1. Ôn lại `let`

```rust
fn main() {
    let x = 10;

    println!("{x}");
}
```

Ở đây:

```text
x ──────► 10
```

`x` là immutable.

Không thể:

```rust
x = 20;
```

---

# 2. `let mut`

```rust
fn main() {
    let mut x = 10;

    x = 20;

    println!("{x}");
}
```

Ta có:

```text
x
│
├── 10
│
└── 20
```

Đây là **mutation**.

Binding `x` vẫn là cùng một binding.

---

# 3. Shadowing

```rust
fn main() {
    let x = 10;

    let x = 20;

    println!("{x}");
}
```

Kết quả:

```text
20
```

Nhưng đây **không phải mutation**.

Có thể hình dung:

```text
binding 1
x ───► 10

binding 2
x ───► 20
```

Binding thứ hai **che khuất** binding thứ nhất.

Đây gọi là:

> Shadowing

---

# 4. Shadowing có thể thay đổi kiểu

Đây là một ưu điểm rất hay.

```rust
fn main() {
    let value = "100";

    let value: i32 = value.parse().unwrap();

    println!("{value}");
}
```

Ban đầu:

```text
value: &str
```

Sau shadowing:

```text
value: i32
```

---

# 5. Tại sao `mut` không làm được điều này?

```rust
fn main() {
    let mut value = "100";

    value = 100;
}
```

Không compile.

Vì binding ban đầu có kiểu:

```text
&str
```

và `mut` chỉ cho phép **thay đổi giá trị cùng kiểu**, không thay đổi kiểu của binding.

Trong khi:

```rust
let value = "100";
let value = 100;
```

là hai binding khác nhau.

---

# 6. Shadowing nhiều lần

```rust
fn main() {
    let value = 10;

    let value = value + 5;

    let value = value * 2;

    let value = value - 10;

    println!("{value}");
}
```

Tính:

```text
10
 ↓ +5
15
 ↓ ×2
30
 ↓ -10
20
```

Output:

```text
20
```

Đây là pattern rất phổ biến trong Rust.

---

# 7. Shadowing trong Scope

Ví dụ:

```rust
fn main() {
    let x = 10;

    {
        let x = 20;

        println!("inside: {x}");
    }

    println!("outside: {x}");
}
```

Output:

```text
inside: 20
outside: 10
```

Cấu trúc:

```text
main scope
│
│ x = 10
│
└── inner scope
     │
     │ x = 20
     │
     └── kết thúc
     
x trở lại binding bên ngoài
```

---

# 8. Shadowing không phá hủy ngay binding cũ

Ví dụ:

```rust
fn main() {
    let x = String::from("Hello");

    let x = 100;

    println!("{x}");
}
```

Binding mới `x` có kiểu `i32`.

Binding cũ `String` sẽ không còn được truy cập bằng tên `x`, nhưng vòng đời của giá trị cũ vẫn tuân theo ownership/scope của nó.

Điểm này sẽ cực kỳ quan trọng khi chúng ta học:

> Ownership

---

# 9. Shadowing vs Mutation

So sánh:

### Mutation

```rust
let mut x = 10;
x = 20;
```

### Shadowing

```rust
let x = 10;
let x = 20;
```

|                          | Mutation | Shadowing |
| ------------------------ | -------- | --------- |
| Binding mới?             | Không    | Có        |
| Cần `mut`?               | Có       | Không     |
| Có thể đổi kiểu?         | Không    | Có        |
| Cùng tên?                | Có       | Có        |
| Tạo giá trị binding mới? | Không    | Có        |

---

# 10. Pattern thực tế: Parse dữ liệu

Đây là một ví dụ rất quan trọng:

```rust
fn main() {
    let input = "42";

    let input: i32 = input.parse().unwrap();

    let input = input * 2;

    println!("{input}");
}
```

Ta có pipeline:

```text
String
  │
  ▼
parse
  │
  ▼
i32
  │
  ▼
multiply
  │
  ▼
i32
```

Không cần tạo:

```text
raw_input
parsed_input
result
```

mà có thể dùng cùng một tên:

```rust
input
```

Đây là một pattern Rust rất đẹp.

---

# 11. `const`

`const` dùng để khai báo **constant**.

Ví dụ:

```rust
const MAX_RETRIES: u32 = 3;

fn main() {
    println!("{MAX_RETRIES}");
}
```

Tên constant thường viết:

```text
SCREAMING_SNAKE_CASE
```

Ví dụ:

```rust
const MAX_CONNECTIONS: usize = 100;
const DEFAULT_PORT: u16 = 8080;
const APP_NAME: &str = "MyApp";
```

---

# 12. `const` phải có kiểu

Đây là điểm quan trọng.

Không viết:

```rust
const MAX_RETRIES = 3;
```

Phải viết:

```rust
const MAX_RETRIES: u32 = 3;
```

---

# 13. `const` không phải variable

```rust
const MAX_RETRIES: u32 = 3;
```

Không có:

```text
một object runtime bình thường
```

theo cách bạn nên hình dung đối với `let`.

`const` biểu diễn một giá trị hằng có thể được sử dụng trong các ngữ cảnh compile-time phù hợp.

---

# 14. `const` phải là compile-time evaluable

Ví dụ hợp lệ:

```rust
const SECONDS_PER_MINUTE: u32 = 60;
const MINUTES_PER_HOUR: u32 = 60;

const SECONDS_PER_HOUR: u32 =
    SECONDS_PER_MINUTE * MINUTES_PER_HOUR;
```

Compiler có thể tính:

```text
60 × 60
```

tại compile time.

---

# 15. Không phải mọi hàm đều dùng được trong `const`

Ví dụ:

```rust
fn get_value() -> i32 {
    100
}
```

Tùy trường hợp, việc gọi một hàm thông thường trong initializer của `const` không hợp lệ.

Muốn hàm có thể được gọi trong ngữ cảnh compile-time, Rust cung cấp:

```rust
const fn
```

Ví dụ:

```rust
const fn square(x: i32) -> i32 {
    x * x
}

const VALUE: i32 = square(10);

fn main() {
    println!("{VALUE}");
}
```

Kết quả:

```text
100
```

---

# 16. `const fn`

`const fn` là function có thể được sử dụng trong các ngữ cảnh yêu cầu giá trị compile-time, với những giới hạn mà Rust cho phép.

Ví dụ:

```rust
const fn calculate_port(base: u16) -> u16 {
    base + 1
}

const PORT: u16 = calculate_port(8080);
```

---

# 17. `const` có scope

Constant có thể được khai báo trong module:

```rust
const APP_NAME: &str = "Novel Reader";

fn main() {
    println!("{APP_NAME}");
}
```

Hoặc bên trong function:

```rust
fn main() {
    const MAX: i32 = 100;

    println!("{MAX}");
}
```

---

# 18. `const` không cần `mut`

Bạn không thể viết:

```rust
const mut MAX: i32 = 10;
```

Constant về bản chất là immutable.

---

# 19. `static`

Bây giờ tới khái niệm khó hơn.

```rust
static APP_NAME: &str = "Novel Reader";
```

`static` khai báo một **static item** có một địa chỉ cố định trong bộ nhớ trong suốt thời gian chạy của chương trình.

Ví dụ:

```rust
static VERSION: &str = "1.0.0";

fn main() {
    println!("{VERSION}");
}
```

---

# 20. `const` vs `static`

Đây là bảng cực kỳ quan trọng:

|                          | `const`                     | `static`                      |
| ------------------------ | --------------------------- | ----------------------------- |
| Có tên                   | Có                          | Có                            |
| Có kiểu                  | Bắt buộc                    | Bắt buộc                      |
| Có địa chỉ cố định riêng | Không nên xem như vậy       | Có                            |
| Có một storage duy nhất  | Không theo cách `static` có | Có                            |
| Mặc định immutable       | Có                          | Có                            |
| Có thể `mut`             | Không                       | Có, nhưng unsafe khi truy cập |
| Dùng cho global data     | Có thể                      | Có                            |
| Thường dùng              | compile-time values         | global storage                |

---

# 21. Ví dụ `const`

```rust
const MAX_USERS: usize = 1000;

fn main() {
    println!("{MAX_USERS}");
}
```

Thường dùng cho:

* giới hạn
* cấu hình compile-time
* số cố định
* đơn vị
* flag compile-time

---

# 22. Ví dụ `static`

```rust
static APP_VERSION: &str = "1.0.0";

fn main() {
    println!("{APP_VERSION}");
}
```

Thường dùng khi bạn thực sự cần một static item có storage cố định.

---

# 23. `static mut`

Rust cho phép:

```rust
static mut COUNTER: u32 = 0;
```

Nhưng đây là khu vực **unsafe**.

Trong Rust hiện đại, bạn không nên dùng `static mut` cho trạng thái toàn cục thông thường.

Ví dụ:

```rust
static mut COUNTER: u32 = 0;
```

Việc truy cập mutable global có thể tạo ra data race.

Thay vào đó, các abstraction an toàn như:

* `AtomicUsize`
* `Mutex`
* `RwLock`
* `OnceLock`
* `LazyLock`

thường phù hợp hơn.

Chúng ta sẽ học khi bước vào Concurrency và Smart Pointer.

---

# 24. Global Configuration

Ví dụ:

```rust
const DEFAULT_PORT: u16 = 8080;
const MAX_CONNECTIONS: usize = 100;

fn main() {
    println!("Port: {DEFAULT_PORT}");
    println!("Max connections: {MAX_CONNECTIONS}");
}
```

Đây là cách rất phù hợp để định nghĩa các giá trị cấu hình cố định.

---

# 25. Module + Constants

Ví dụ cấu trúc:

```text
src/
├── main.rs
└── config.rs
```

`config.rs`:

```rust
pub const APP_NAME: &str = "Novel Reader";
pub const DEFAULT_PORT: u16 = 8080;
pub const MAX_RETRIES: u32 = 3;
```

`main.rs`:

```rust
mod config;

fn main() {
    println!("App: {}", config::APP_NAME);
    println!("Port: {}", config::DEFAULT_PORT);
    println!("Retries: {}", config::MAX_RETRIES);
}
```

Chạy:

```bash
cargo run
```

Kết quả:

```text
App: Novel Reader
Port: 8080
Retries: 3
```

---

# 26. Shadowing trong xử lý CLI

Ví dụ sau này khi xây dựng CLI:

```rust
fn main() {
    let port = "8080";

    let port: u16 = port.parse().unwrap();

    println!("Starting server on port {port}");
}
```

Đây là pattern rất tự nhiên:

```text
raw input
    ↓
String
    ↓
parse
    ↓
u16
```

---

# 27. Shadowing trong xử lý HTTP

Một pattern phổ biến:

```rust
fn main() {
    let url = "https://example.com";

    let url = url.trim();

    println!("{url}");
}
```

Mỗi bước tạo một binding mới.

Điều này giúp tránh:

```text
url_raw
url_trimmed
url_normalized
url_final
```

nếu các biến trung gian không cần tồn tại độc lập.

---

# 28. Shadowing trong validation

```rust
fn main() {
    let username = "  alice  ";

    let username = username.trim();

    let username = username.to_lowercase();

    println!("{username}");
}
```

Pipeline:

```text
"  alice  "
     │
     ▼
"alice"
     │
     ▼
"alice"
```

Đây là style rất phù hợp với Rust.

---

# 29. Một ví dụ quan trọng về scope

```rust
fn main() {
    let value = 10;

    {
        let value = value + 5;

        println!("inner = {value}");
    }

    println!("outer = {value}");
}
```

Output:

```text
inner = 15
outer = 10
```

Binding inner:

```text
value = 15
```

không thay đổi binding outer:

```text
value = 10
```

---

# 30. Shadowing với `mut`

Có thể kết hợp:

```rust
fn main() {
    let mut x = 10;

    x += 5;

    let x = x * 2;

    println!("{x}");
}
```

Quá trình:

```text
x mutable = 10
     │
     ▼
x mutable = 15
     │
 shadowing
     ▼
x immutable = 30
```

Pattern này rất hữu ích:

> Mutable trong giai đoạn xây dựng → immutable sau khi hoàn tất.

---

# 31. Mini Project — Application Config

Tạo project:

```bash
cargo new app_config
cd app_config
```

`src/main.rs`:

```rust
const APP_NAME: &str = "Novel Reader";
const VERSION: &str = "1.0.0";
const DEFAULT_PORT: u16 = 8080;
const MAX_RETRIES: u32 = 3;

fn print_config() {
    println!("==============================");
    println!("Application Configuration");
    println!("==============================");

    println!("Name    : {APP_NAME}");
    println!("Version : {VERSION}");
    println!("Port    : {DEFAULT_PORT}");
    println!("Retries : {MAX_RETRIES}");
}

fn main() {
    print_config();
}
```

Chạy:

```bash
cargo run
```

Kết quả:

```text
==============================
Application Configuration
==============================
Name    : Novel Reader
Version : 1.0.0
Port    : 8080
Retries : 3
```

---

# 32. Mini Project nâng cao — Input Pipeline

```rust
fn main() {
    let input = "   42   ";

    let input = input.trim();

    let input: i32 = input.parse().unwrap();

    let input = input * 2;

    println!("Result: {input}");
}
```

Kết quả:

```text
Result: 84
```

Ta có:

```text
&str
 │
 ├── trim()
 │
 ▼
&str
 │
 ├── parse()
 │
 ▼
i32
 │
 ├── * 2
 │
 ▼
i32
```

Đây là tư duy **data transformation pipeline** mà bạn sẽ sử dụng rất nhiều khi viết Rust.

---

# 33. Một nguyên tắc rất quan trọng

Khi viết Rust, hãy tự hỏi:

> "Tôi đang thay đổi giá trị hiện tại hay tạo một giá trị mới?"

Nếu là:

> thay đổi cùng một trạng thái

dùng:

```rust
let mut value = ...;
value = ...;
```

Nếu là:

> biến đổi dữ liệu qua nhiều bước

cân nhắc:

```rust
let value = ...;
let value = transform(value);
let value = transform(value);
```

Đây là một trong những cách viết Rust sạch và an toàn.

---

# 34. `const` không phải "global variable"

Đừng suy nghĩ:

```text
const = global variable
```

Tư duy tốt hơn:

```text
const
    ↓
compile-time constant
```

Còn:

```text
static
    ↓
static storage
```

---

# 35. Khi nào dùng gì?

### Giá trị không đổi

```rust
let name = "Alice";
```

### Giá trị cần thay đổi

```rust
let mut count = 0;
```

### Biến đổi kiểu / pipeline

```rust
let value = "42";
let value: i32 = value.parse().unwrap();
```

### Hằng compile-time

```rust
const MAX_RETRIES: u32 = 3;
```

### Global static storage

```rust
static APP_VERSION: &str = "1.0";
```

---

# 36. Bài tập thực hành

## Bài 1 — Mutation

Viết chương trình:

```text
counter = 0
counter += 1
counter += 1
counter += 1
```

In:

```text
Counter: 3
```

---

## Bài 2 — Shadowing

Bắt đầu:

```rust
let value = "100";
```

Sau đó:

```text
&str
 ↓
i32
 ↓
i32 × 10
 ↓
i32 / 2
```

Tất cả sử dụng tên `value`.

---

## Bài 3 — Đổi kiểu

Viết:

```rust
let input = "3.14";
```

Shadowing để chuyển thành:

```text
f64
```

Sau đó nhân với:

```text
2.0
```

---

## Bài 4 — Constants

Tạo:

```rust
const APP_NAME: &str = ...;
const VERSION: &str = ...;
const DEFAULT_PORT: u16 = ...;
const MAX_CONNECTIONS: usize = ...;
```

In thành bảng cấu hình.

---

## Bài 5 — Scope

Dự đoán output:

```rust
fn main() {
    let x = 10;

    {
        let x = 20;

        {
            let x = 30;

            println!("{x}");
        }

        println!("{x}");
    }

    println!("{x}");
}
```

Sau đó chạy thử.

---

# 37. Bài tập nâng cao

Viết chương trình xử lý:

```text
"   100   "
```

Pipeline:

```text
input
 ↓
trim
 ↓
parse i32
 ↓
+ 50
 ↓
× 2
 ↓
- 100
```

Yêu cầu:

**Chỉ sử dụng tên `input` cho tất cả các bước shadowing.**

Kết quả cuối cùng phải là:

```text
200
```

---

# 38. Những lỗi người mới thường gặp

### Lỗi 1 — Nhầm shadowing với mutation

```rust
let x = 10;
let x = 20;
```

Không phải:

```text
x bị thay đổi
```

mà là:

```text
binding mới che binding cũ
```

---

### Lỗi 2 — Dùng `mut` khi không cần

Không nên:

```rust
let mut name = "Alice";
```

nếu `name` không bao giờ thay đổi.

---

### Lỗi 3 — Dùng `static mut` tùy tiện

Đây là một trong những vùng dễ phá vỡ memory safety nếu sử dụng sai.

---

### Lỗi 4 — Nhầm `const` với runtime configuration

Nếu người dùng nhập:

```text
port = 9000
```

thì đây không phải `const`.

Đó là runtime data.

---

# Tổng kết Buổi 8

Bạn cần ghi nhớ bảng này:

| Nhu cầu                         | Công cụ                                                 |
| ------------------------------- | ------------------------------------------------------- |
| Giá trị không thay đổi          | `let`                                                   |
| Muốn thay đổi giá trị           | `let mut`                                               |
| Biến đổi dữ liệu qua nhiều bước | Shadowing                                               |
| Giá trị compile-time cố định    | `const`                                                 |
| Static storage                  | `static`                                                |
| Global mutable state            | Atomic/Mutex/etc., không nên tùy tiện dùng `static mut` |

Đặc biệt hãy nhớ:

```rust
let x = 10;
let x = 20;
```

khác:

```rust
let mut x = 10;
x = 20;
```

Đây là hai cơ chế hoàn toàn khác nhau.

---

# Kiến thức đã hoàn thành

Đến hết Buổi 8, chúng ta đã có:

```text
Rust Foundation
│
├── 01 Rust Introduction
├── 02 Cargo
├── 03 Variables
├── 04 Data Types
├── 05 Functions
├── 06 Comments & Documentation
├── 07 Formatting Output
└── 08 Shadowing & Constants
```

## Buổi 9 — Operators Deep Dive

Buổi tiếp theo chúng ta sẽ học toàn bộ hệ thống toán tử của Rust:

* Arithmetic operators
* Comparison operators
* Logical operators
* Assignment operators
* Bitwise operators
* Range operators
* `..` và `..=`
* Operator precedence
* Overflow
* Checked / Wrapping / Saturating / Overflowing arithmetic
* `+=`, `-=`, `*=`, `/=`
* Toán tử trên `bool`
* Thực hành xây dựng một **Expression Calculator** bằng Rust.
