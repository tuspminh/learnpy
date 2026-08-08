# Rust Professional 2026

## Giai đoạn 1 — Rust Foundation

## Buổi 9 — Operators Deep Dive

Buổi này chúng ta sẽ học **toàn bộ hệ thống toán tử trong Rust**, không chỉ dừng ở `+ - * /`.

Mục tiêu là sau buổi này bạn có thể đọc và viết các biểu thức Rust một cách chắc chắn, đồng thời hiểu một vấn đề rất quan trọng của Rust:

> **Integer overflow được xử lý như thế nào?**

---

# 1. Bản đồ Operators trong Rust

Chúng ta sẽ đi qua:

```text
Operators
│
├── Arithmetic
│   ├── +
│   ├── -
│   ├── *
│   ├── /
│   └── %
│
├── Comparison
│   ├── ==
│   ├── !=
│   ├── >
│   ├── <
│   ├── >=
│   └── <=
│
├── Logical
│   ├── &&
│   ├── ||
│   └── !
│
├── Assignment
│   ├── =
│   ├── +=
│   ├── -=
│   ├── *=
│   ├── /=
│   └── %=
│
├── Bitwise
│   ├── &
│   ├── |
│   ├── ^
│   ├── !
│   ├── <<
│   └── >>
│
└── Range
    ├── ..
    └── ..=
```

---

# 2. Arithmetic Operators

Các toán tử toán học cơ bản:

```rust
+
-
*
/
%
```

Ví dụ:

```rust
fn main() {
    let a = 20;
    let b = 6;

    println!("a + b = {}", a + b);
    println!("a - b = {}", a - b);
    println!("a * b = {}", a * b);
    println!("a / b = {}", a / b);
    println!("a % b = {}", a % b);
}
```

Output:

```text
a + b = 26
a - b = 14
a * b = 120
a / b = 3
a % b = 2
```

---

# 3. Integer Division

Đây là điều người mới rất dễ nhầm.

```rust
let result = 7 / 2;
```

Kết quả:

```text
3
```

Không phải:

```text
3.5
```

Vì:

```text
i32 / i32 → i32
```

Nếu muốn `3.5`:

```rust
let result = 7.0 / 2.0;

println!("{result}");
```

Kết quả:

```text
3.5
```

Hoặc:

```rust
let result = 7 as f64 / 2 as f64;
```

---

# 4. Remainder `%`

```rust
fn main() {
    println!("{}", 10 % 3);
    println!("{}", 20 % 4);
    println!("{}", 15 % 7);
}
```

Output:

```text
1
0
1
```

Ứng dụng:

```rust
if number % 2 == 0 {
    println!("Even");
}
```

Kiểm tra số chẵn/lẻ là một trong những ứng dụng phổ biến nhất của `%`.

---

# 5. Negative Numbers và `%`

Rust xử lý phần dư theo phép chia số nguyên.

Ví dụ:

```rust
fn main() {
    println!("{}", -10 % 3);
    println!("{}", 10 % -3);
}
```

Đừng nên suy luận `%` đơn giản là "modulo toán học" trong mọi trường hợp; nó là **remainder operation**.

---

# 6. Comparison Operators

Các toán tử:

```text
==
!=
>
<
>=
<=
```

Ví dụ:

```rust
fn main() {
    let age = 20;

    println!("{}", age == 20);
    println!("{}", age != 30);
    println!("{}", age > 18);
    println!("{}", age < 30);
    println!("{}", age >= 20);
    println!("{}", age <= 20);
}
```

Kết quả là:

```text
true
true
true
true
true
true
```

---

# 7. Comparison luôn trả về `bool`

Ví dụ:

```rust
let result = 10 > 5;
```

Kiểu:

```text
bool
```

Giá trị:

```text
true
```

Vì vậy có thể:

```rust
if result {
    println!("10 is greater");
}
```

---

# 8. `==` và `=`

Cực kỳ quan trọng.

```rust
=
```

là **assignment**.

```rust
x = 10;
```

Trong khi:

```rust
==
```

là **comparison**.

```rust
x == 10
```

Ví dụ:

```rust
let x = 10;

if x == 10 {
    println!("Correct");
}
```

---

# 9. `!=`

```rust
let age = 20;

if age != 18 {
    println!("Not 18");
}
```

---

# 10. Logical Operators

Rust có:

```text
&&
||
!
```

---

# 11. AND `&&`

Cả hai điều kiện phải đúng.

```rust
let age = 20;
let has_ticket = true;

if age >= 18 && has_ticket {
    println!("Allowed");
}
```

Logic:

```text
age >= 18     → true
has_ticket    → true

true && true  → true
```

---

# 12. OR `||`

Chỉ cần một điều kiện đúng.

```rust
let is_admin = false;
let is_owner = true;

if is_admin || is_owner {
    println!("Access granted");
}
```

Logic:

```text
false || true → true
```

---

# 13. NOT `!`

Đảo boolean.

```rust
let active = true;

println!("{}", !active);
```

Output:

```text
false
```

---

# 14. Truth Table

## AND

```text
A       B       A && B
----------------------
false   false   false
false   true    false
true    false   false
true    true    true
```

## OR

```text
A       B       A || B
----------------------
false   false   false
false   true    true
true    false   true
true    true    true
```

## NOT

```text
!false → true
!true  → false
```

---

# 15. Short-circuit Evaluation

Đây là một tính năng cực kỳ quan trọng.

Rust không phải lúc nào cũng đánh giá cả hai vế.

Ví dụ:

```rust
let a = false;
let b = expensive_check();

if a && b {
    println!("...");
}
```

Nếu:

```text
a == false
```

thì Rust biết:

```text
false && anything = false
```

nên không cần đánh giá `b`.

Tương tự:

```rust
true || anything
```

luôn là:

```text
true
```

---

# 16. Ví dụ Short-circuit

```rust
fn check() -> bool {
    println!("check() called");
    true
}

fn main() {
    let result = false && check();

    println!("result = {result}");
}
```

Output:

```text
result = false
```

Bạn sẽ không thấy:

```text
check() called
```

vì `check()` không được gọi.

---

# 17. Assignment

Toán tử:

```rust
=
```

Ví dụ:

```rust
let mut x = 10;

x = 20;
```

---

# 18. Compound Assignment

Rust hỗ trợ:

```text
+=
-=
*=
/=
%=
```

Ví dụ:

```rust
fn main() {
    let mut x = 10;

    x += 5;
    println!("{x}");

    x -= 3;
    println!("{x}");

    x *= 2;
    println!("{x}");

    x /= 4;
    println!("{x}");

    x %= 3;
    println!("{x}");
}
```

---

# 19. `x += 5` tương đương gì?

Về mặt ý tưởng:

```rust
x += 5;
```

tương đương:

```rust
x = x + 5;
```

Tương tự:

```rust
x -= 5;
```

tương đương:

```rust
x = x - 5;
```

---

# 20. Bitwise Operators

Đây là phần quan trọng nếu sau này bạn làm:

* networking
* binary protocol
* embedded
* systems programming
* cryptography
* performance optimization

Rust có:

```text
&
|
^
!
<<
>>
```

---

# 21. Bitwise AND `&`

Ví dụ:

```rust
fn main() {
    let a = 0b1100;
    let b = 0b1010;

    println!("{:04b}", a & b);
}
```

Phép tính:

```text
1100
1010
----
1000
```

Kết quả:

```text
1000
```

---

# 22. Bitwise OR `|`

```rust
let a = 0b1100;
let b = 0b1010;

println!("{:04b}", a | b);
```

Kết quả:

```text
1110
```

---

# 23. Bitwise XOR `^`

```rust
let a = 0b1100;
let b = 0b1010;

println!("{:04b}", a ^ b);
```

Kết quả:

```text
0110
```

XOR:

```text
0 ^ 0 = 0
0 ^ 1 = 1
1 ^ 0 = 1
1 ^ 1 = 0
```

---

# 24. Bitwise NOT `!`

Ví dụ với `u8`:

```rust
let x: u8 = 0b0000_1111;

println!("{:08b}", !x);
```

Kết quả:

```text
11110000
```

---

# 25. Left Shift `<<`

```rust
let x = 1u8;

println!("{}", x << 3);
```

Kết quả:

```text
8
```

Bởi vì:

```text
00000001
    ↓ << 3
00001000
```

Có thể hiểu đơn giản:

```text
1 × 2³ = 8
```

---

# 26. Right Shift `>>`

```rust
let x = 16u8;

println!("{}", x >> 2);
```

Kết quả:

```text
4
```

Tương đương gần như:

```text
16 / 2² = 4
```

với integer semantics phù hợp.

---

# 27. Range Operators

Rust có hai toán tử range cơ bản:

```text
..
..=
```

Ví dụ:

```rust
1..5
```

tạo range:

```text
1 2 3 4
```

Không bao gồm `5`.

---

# 28. Inclusive Range

```rust
1..=5
```

bao gồm:

```text
1 2 3 4 5
```

---

# 29. Range với `for`

```rust
fn main() {
    for i in 1..5 {
        println!("{i}");
    }
}
```

Output:

```text
1
2
3
4
```

---

# 30. Inclusive Range

```rust
fn main() {
    for i in 1..=5 {
        println!("{i}");
    }
}
```

Output:

```text
1
2
3
4
5
```

Range sẽ được học sâu hơn cùng với **Iterator**.

---

# 31. Range của ký tự

Có thể làm việc với range của `char`:

```rust
for c in 'a'..='e' {
    println!("{c}");
}
```

Output:

```text
a
b
c
d
e
```

---

# 32. Range trong Slice

Ví dụ:

```rust
fn main() {
    let numbers = [10, 20, 30, 40, 50];

    let slice = &numbers[1..4];

    println!("{slice:?}");
}
```

Kết quả:

```text
[20, 30, 40]
```

Lý do:

```text
index:   0   1   2   3   4
value:  10  20  30  40  50
             └───────┘
             1..4
```

---

# 33. Operator Precedence

Ví dụ:

```rust
let result = 2 + 3 * 4;
```

Không phải:

```text
(2 + 3) × 4
```

mà là:

```text
2 + (3 × 4)
```

Kết quả:

```text
14
```

---

# 34. Dùng Parentheses

Khi biểu thức phức tạp, hãy dùng `()`.

```rust
let result = (2 + 3) * 4;
```

Kết quả:

```text
20
```

Đừng cố ghi nhớ mọi precedence nếu parentheses làm code rõ ràng hơn.

---

# 35. Ví dụ thực tế

Tính điểm trung bình:

```rust
let math = 8.0;
let physics = 9.0;
let english = 7.5;

let average = (math + physics + english) / 3.0;

println!("{average:.2}");
```

Kết quả:

```text
8.17
```

---

# 36. Integer Overflow

Đây là phần **rất quan trọng trong Rust**.

Ví dụ:

```rust
fn main() {
    let x: u8 = 255;

    let y = x + 1;

    println!("{y}");
}
```

`u8` chỉ có:

```text
0..=255
```

Nên:

```text
255 + 1
```

bị overflow.

Trong debug build, chương trình có thể panic.

---

# 37. Vì sao Rust quan tâm Overflow?

Trong systems programming, overflow có thể gây ra bug nghiêm trọng.

Ví dụ:

```text
buffer size
memory size
packet length
file size
array index
```

Do đó Rust cung cấp nhiều cách xử lý overflow rõ ràng.

---

# 38. `checked_*`

Ví dụ:

```rust
fn main() {
    let x: u8 = 255;

    let result = x.checked_add(1);

    println!("{result:?}");
}
```

Kết quả:

```text
None
```

Nếu không overflow:

```rust
let x: u8 = 100;

println!("{:?}", x.checked_add(20));
```

Kết quả:

```text
Some(120)
```

---

# 39. `wrapping_*`

`wrapping` cho phép số quay vòng.

```rust
fn main() {
    let x: u8 = 255;

    let result = x.wrapping_add(1);

    println!("{result}");
}
```

Kết quả:

```text
0
```

Vì:

```text
255 + 1
 ↓
0
```

theo modulo `256`.

---

# 40. `saturating_*`

Saturating arithmetic dừng ở giới hạn.

```rust
fn main() {
    let x: u8 = 255;

    let result = x.saturating_add(1);

    println!("{result}");
}
```

Kết quả:

```text
255
```

Không quay về `0`.

---

# 41. `overflowing_*`

Trả về:

```text
(value, overflowed)
```

Ví dụ:

```rust
fn main() {
    let x: u8 = 255;

    let result = x.overflowing_add(1);

    println!("{result:?}");
}
```

Kết quả:

```text
(0, true)
```

---

# 42. Bốn kiểu xử lý Overflow

Hãy nhớ:

```text
checked
    ↓
Option<T>

wrapping
    ↓
wrap around

saturating
    ↓
clamp at boundary

overflowing
    ↓
(value, bool)
```

Bảng:

| Method            | Kết quả overflow |
| ----------------- | ---------------- |
| `checked_add`     | `None`           |
| `wrapping_add`    | Wrap             |
| `saturating_add`  | Giữ max/min      |
| `overflowing_add` | Trả value + flag |

---

# 43. Các phép toán tương ứng

Không chỉ có:

```rust
checked_add()
```

Mà còn:

```text
checked_sub
checked_mul
checked_div

wrapping_add
wrapping_sub
wrapping_mul

saturating_add
saturating_sub
saturating_mul

overflowing_add
overflowing_sub
overflowing_mul
```

---

# 44. Ví dụ thực tế — Counter

Giả sử counter:

```rust
let counter: u8 = 255;
```

Nếu muốn phát hiện lỗi:

```rust
let next = counter.checked_add(1);
```

Nếu muốn vòng lại:

```rust
let next = counter.wrapping_add(1);
```

Nếu muốn giữ nguyên 255:

```rust
let next = counter.saturating_add(1);
```

---

# 45. Ví dụ thực tế — Byte

Trong systems programming:

```rust
let a: u8 = 200;
let b: u8 = 100;

let result = a.wrapping_add(b);

println!("{result}");
```

Đây có thể phù hợp với các phép toán byte cần modulo `256`.

---

# 46. Type Conversion

Rust **không tự động chuyển kiểu số** trong nhiều trường hợp.

Ví dụ:

```rust
let a: i32 = 10;
let b: i64 = 20;

let result = a + b;
```

Không compile.

Bạn phải chuyển:

```rust
let result = i64::from(a) + b;
```

hoặc:

```rust
let result = a as i64 + b;
```

---

# 47. `as`

Ví dụ:

```rust
let x: i32 = 100;

let y = x as i64;

println!("{y}");
```

---

# 48. `as` cần cẩn thận

Ví dụ:

```rust
let x: i16 = 300;

let y = x as u8;

println!("{y}");
```

Bạn không nên coi `as` là "chuyển kiểu an toàn trong mọi trường hợp".

Nó có semantics riêng khi giá trị không biểu diễn được trong kiểu đích.

Khi dữ liệu có khả năng lỗi, hãy dùng API chuyển đổi phù hợp như `TryFrom`/`try_into()` — chúng ta sẽ học kỹ hơn sau.

---

# 49. Một Calculator nhỏ

Bây giờ chúng ta áp dụng những gì đã học.

```rust
fn main() {
    let a = 20;
    let b = 6;

    println!("====================");
    println!("     CALCULATOR");
    println!("====================");

    println!("a       = {a}");
    println!("b       = {b}");
    println!("a + b   = {}", a + b);
    println!("a - b   = {}", a - b);
    println!("a * b   = {}", a * b);
    println!("a / b   = {}", a / b);
    println!("a % b   = {}", a % b);
}
```

Chạy:

```bash
cargo run
```

---

# 50. Calculator nâng cao

```rust
fn main() {
    let a: f64 = 20.0;
    let b: f64 = 6.0;

    println!("============================");
    println!("        CALCULATOR");
    println!("============================");

    println!("A       : {a}");
    println!("B       : {b}");
    println!("A + B   : {:.2}", a + b);
    println!("A - B   : {:.2}", a - b);
    println!("A * B   : {:.2}", a * b);
    println!("A / B   : {:.2}", a / b);
}
```

---

# 51. Kiểm tra điều kiện

```rust
fn main() {
    let age = 20;
    let has_ticket = true;

    let can_enter = age >= 18 && has_ticket;

    println!("Can enter: {can_enter}");
}
```

---

# 52. Calculator kết hợp Boolean

```rust
fn main() {
    let a = 20;
    let b = 6;

    println!("a > b      : {}", a > b);
    println!("a == b     : {}", a == b);
    println!("a != b     : {}", a != b);
    println!("a % b == 0 : {}", a % b == 0);
}
```

---

# 53. Mini Project — Score Analyzer

Tạo:

```bash
cargo new score_analyzer
cd score_analyzer
```

`src/main.rs`:

```rust
fn main() {
    let math = 8.5;
    let physics = 7.5;
    let chemistry = 9.0;

    let average = (math + physics + chemistry) / 3.0;

    let passed =
        average >= 5.0 &&
        math >= 4.0 &&
        physics >= 4.0 &&
        chemistry >= 4.0;

    println!("==============================");
    println!("       SCORE ANALYZER");
    println!("==============================");

    println!("Math      : {math:.2}");
    println!("Physics   : {physics:.2}");
    println!("Chemistry : {chemistry:.2}");
    println!("------------------------------");
    println!("Average   : {average:.2}");
    println!("Passed    : {passed}");
}
```

Chạy:

```bash
cargo run
```

---

# 54. Phân tích biểu thức `passed`

Biểu thức:

```rust
let passed =
    average >= 5.0 &&
    math >= 4.0 &&
    physics >= 4.0 &&
    chemistry >= 4.0;
```

Có thể đọc như:

```text
average >= 5
      AND
math >= 4
      AND
physics >= 4
      AND
chemistry >= 4
```

Tất cả phải đúng.

---

# 55. Bài tập 1 — Calculator

Tạo:

```rust
let a = 15;
let b = 4;
```

In:

```text
Sum
Difference
Product
Quotient
Remainder
```

---

# 56. Bài tập 2 — Even / Odd

Viết:

```rust
let number = 42;
```

Kiểm tra:

```text
Even
```

hoặc:

```text
Odd
```

Gợi ý:

```rust
number % 2 == 0
```

---

# 57. Bài tập 3 — Range

In:

```text
1
2
3
4
5
6
7
8
9
10
```

bằng:

```rust
for ...
```

Sau đó thử:

```rust
1..10
```

và:

```rust
1..=10
```

Quan sát sự khác nhau.

---

# 58. Bài tập 4 — Bitwise

Cho:

```rust
let a = 0b1100;
let b = 0b1010;
```

Tính:

```text
a & b
a | b
a ^ b
```

In kết quả ở binary.

---

# 59. Bài tập 5 — Overflow

Thử:

```rust
let x: u8 = 255;
```

So sánh:

```rust
x.checked_add(1)
x.wrapping_add(1)
x.saturating_add(1)
x.overflowing_add(1)
```

Ghi lại kết quả của từng phương pháp.

---

# 60. Bài tập 6 — Expression

Không chạy ngay, hãy đoán:

```rust
let result = 10 + 5 * 2 - 4 / 2;
```

Sau đó chạy.

Tiếp tục:

```rust
let result = (10 + 5) * (2 - 4) / 2;
```

So sánh.

---

# 61. Bài tập 7 — Access Control

Cho:

```rust
let age = 25;
let is_member = true;
let is_banned = false;
```

Người dùng được phép truy cập khi:

```text
age >= 18
AND
is_member == true
AND
is_banned == false
```

Viết biểu thức Rust tạo ra:

```rust
let can_access = ...;
```

---

# 62. Bài tập 8 — Mini Project

Xây dựng:

## `ticket_checker`

Input giả lập:

```rust
let age = 22;
let has_ticket = true;
let is_vip = false;
```

Quy tắc:

```text
Được vào nếu:

(age >= 18 && has_ticket)
OR
is_vip
```

In:

```text
Age       : 22
Ticket    : true
VIP       : false
Can Enter : true
```

---

# 63. Những lỗi cần tránh

### 1. Nhầm `/`

```rust
7 / 2
```

với:

```rust
7.0 / 2.0
```

Một bên là integer division, một bên là floating-point division.

---

### 2. Nhầm `=` và `==`

```text
=   assignment
==  comparison
```

---

### 3. Quên short-circuit

```rust
false && expensive()
```

không nhất thiết gọi `expensive()`.

---

### 4. Không chú ý overflow

Đặc biệt khi làm việc với:

```text
u8
u16
u32
u64
i8
i16
...
```

---

### 5. Lạm dụng `as`

Đặc biệt với conversion có nguy cơ mất dữ liệu.

---

# 64. Sơ đồ tư duy Buổi 9

```text
Operators
│
├── Arithmetic
│   ├── +
│   ├── -
│   ├── *
│   ├── /
│   └── %
│
├── Comparison
│   ├── ==
│   ├── !=
│   ├── >
│   ├── <
│   ├── >=
│   └── <=
│
├── Logical
│   ├── &&
│   ├── ||
│   └── !
│
├── Assignment
│   ├── =
│   ├── +=
│   ├── -=
│   ├── *=
│   ├── /=
│   └── %=
│
├── Bitwise
│   ├── &
│   ├── |
│   ├── ^
│   ├── !
│   ├── <<
│   └── >>
│
└── Range
    ├── ..
    └── ..=
```

---

# 65. Kiến thức quan trọng nhất

Nếu bạn chỉ nhớ 10 điều sau buổi này, hãy nhớ:

```text
1.  / trên integer là integer division
2.  % lấy remainder
3.  == là comparison
4.  = là assignment
5.  && và || có short-circuit
6.  .. không bao gồm endpoint
7.  ..= bao gồm endpoint
8.  Rust không tự động convert integer types tùy ý
9.  Integer overflow cần được xử lý có chủ đích
10. checked/wrapping/saturating/overflowing có semantics khác nhau
```

---

# Chuẩn bị Buổi 10

Đến đây chúng ta đã hoàn thành phần lớn nền tảng biểu thức. **Buổi 10** sẽ là một bước rất quan trọng:

## Control Flow — `if`, `else`, `else if`

Chúng ta sẽ học không chỉ:

```rust
if condition {
}
```

mà còn đào sâu:

* `if` là **expression** chứ không chỉ là statement.
* `if` trả về giá trị.
* `let result = if ...`.
* Nested `if`.
* `else if`.
* Điều kiện phức tạp.
* Scope của block.
* `if` với `let`.
* Pattern matching cơ bản.
* `if let`.
* So sánh tư duy `if` của Rust với Python.
* Mini project **Grade Analyzer** hoàn chỉnh.

Sau đó chúng ta sẽ bước sang `match`, `loop`, `while`, `for` và xây dựng được các chương trình CLI có flow thực sự.
