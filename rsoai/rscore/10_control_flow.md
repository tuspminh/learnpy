# Rust Professional 2026

## Giai đoạn 1 — Rust Foundation

## Buổi 10 — Control Flow: `if`, `else`, `else if`

Buổi 10 là một buổi **rất quan trọng**.

Trong Rust, `if` không đơn thuần chỉ là một cấu trúc điều khiển. Nó còn là một **expression có thể trả về giá trị**.

Đây là một trong những khác biệt quan trọng giữa cách viết Rust và cách viết Python/C-like mà bạn cần hình thành từ sớm.

---

# 1. Bản đồ Control Flow

Sau buổi này, bạn sẽ hiểu:

```text
Control Flow
│
├── if
│   ├── if
│   ├── if / else
│   └── if / else if / else
│
├── if as expression
│
├── nested if
│
├── block & scope
│
├── boolean conditions
│
└── if let
```

Sau đó:

```text
Buổi 11 → match
Buổi 12 → loop
Buổi 13 → while
Buổi 14 → for
```

---

# 2. `if` cơ bản

Cú pháp:

```rust
if condition {
    // code
}
```

Ví dụ:

```rust
fn main() {
    let age = 20;

    if age >= 18 {
        println!("Adult");
    }
}
```

Kết quả:

```text
Adult
```

---

# 3. Điều kiện phải là `bool`

Rust yêu cầu điều kiện của `if` phải là `bool`.

Đúng:

```rust
if age >= 18 {
    println!("Adult");
}
```

Sai:

```rust
if age {
    println!("Adult");
}
```

Nếu:

```rust
let age = 20;
```

thì `age` là `i32`, không phải `bool`.

Rust **không tự động chuyển**:

```text
20 → true
0  → false
```

như một số ngôn ngữ khác.

---

# 4. `if / else`

```rust
fn main() {
    let age = 16;

    if age >= 18 {
        println!("Adult");
    } else {
        println!("Minor");
    }
}
```

Output:

```text
Minor
```

Flow:

```text
             age >= 18?
               │
          ┌────┴────┐
         YES        NO
          │          │
       Adult       Minor
```

---

# 5. `else if`

Khi có nhiều trường hợp:

```rust
fn main() {
    let score = 8.5;

    if score >= 9.0 {
        println!("Excellent");
    } else if score >= 8.0 {
        println!("Very Good");
    } else if score >= 6.5 {
        println!("Good");
    } else if score >= 5.0 {
        println!("Pass");
    } else {
        println!("Fail");
    }
}
```

Kết quả:

```text
Very Good
```

---

# 6. Rust kiểm tra từ trên xuống dưới

Ví dụ:

```rust
let score = 9.5;

if score >= 5.0 {
    println!("Pass");
} else if score >= 9.0 {
    println!("Excellent");
}
```

Kết quả:

```text
Pass
```

Tại sao?

Vì:

```text
9.5 >= 5.0
```

đã là `true`.

Rust thực hiện branch đầu tiên và không tiếp tục.

Vì vậy thứ tự điều kiện rất quan trọng.

Nên viết:

```rust
if score >= 9.0 {
    ...
} else if score >= 5.0 {
    ...
}
```

---

# 7. `if` là Expression

Đây là phần quan trọng nhất của buổi này.

Trong Rust:

```rust
if condition {
    value1
} else {
    value2
}
```

có thể **trả về một giá trị**.

Ví dụ:

```rust
fn main() {
    let age = 20;

    let status = if age >= 18 {
        "adult"
    } else {
        "minor"
    };

    println!("{status}");
}
```

Output:

```text
adult
```

---

# 8. Đây là tư duy cực kỳ quan trọng

Bạn có thể viết:

```rust
let status;

if age >= 18 {
    status = "adult";
} else {
    status = "minor";
}
```

Nhưng Rust thường khuyến khích cách:

```rust
let status = if age >= 18 {
    "adult"
} else {
    "minor"
};
```

Tư duy:

```text
condition
    ↓
if expression
    ↓
value
```

---

# 9. `if` có kiểu dữ liệu

Ví dụ:

```rust
let x = if true {
    10
} else {
    20
};
```

Kiểu của `x`:

```text
i32
```

Vì cả hai branch đều trả về `i32`.

---

# 10. Hai branch phải tương thích kiểu

Đoạn này:

```rust
let value = if true {
    10
} else {
    "hello"
};
```

không hợp lệ.

Vì:

```text
branch 1 → i32
branch 2 → &str
```

Rust không biết `value` phải có kiểu gì.

---

# 11. Ví dụ đúng

```rust
let value = if true {
    10
} else {
    20;
};
```

Lưu ý dấu `;`.

Đoạn trên thực tế có vấn đề về kiểu vì branch đầu trả `i32`, branch sau là `()` do semicolon.

Đây là lý do cần hiểu:

> Trong Rust, dấu `;` ảnh hưởng đến việc một block trả về expression hay không.

Cách đúng:

```rust
let value = if true {
    10
} else {
    20
};
```

---

# 12. Expression và `;`

Đây là kiến thức nền tảng.

```rust
{
    10
}
```

trả:

```text
10
```

Nhưng:

```rust
{
    10;
}
```

trả:

```text
()
```

Vì:

```text
expression không có ;
    ↓
giá trị của expression

expression có ;
    ↓
statement
    ↓
()
```

Ví dụ:

```rust
fn main() {
    let x = {
        10
    };

    println!("{x}");
}
```

Output:

```text
10
```

---

# 13. Block cũng là Expression

Rust cho phép:

```rust
let result = {
    let a = 10;
    let b = 20;

    a + b
};
```

Kết quả:

```text
30
```

Dòng cuối:

```rust
a + b
```

không có `;`.

Do đó nó trở thành giá trị trả về của block.

---

# 14. Kết hợp `if` và block

```rust
let result = if true {
    let a = 10;
    let b = 20;

    a + b
} else {
    0
};
```

Kết quả:

```text
30
```

Bạn nên bắt đầu hình thành tư duy:

```text
if
↓
expression
↓
value
```

---

# 15. Ví dụ thực tế — Grade

```rust
fn main() {
    let score = 8.5;

    let grade = if score >= 9.0 {
        "A"
    } else if score >= 8.0 {
        "B"
    } else if score >= 6.5 {
        "C"
    } else if score >= 5.0 {
        "D"
    } else {
        "F"
    };

    println!("Grade: {grade}");
}
```

Output:

```text
Grade: B
```

---

# 16. Nested `if`

Bạn có thể đặt `if` bên trong `if`.

```rust
fn main() {
    let age = 20;
    let has_ticket = true;

    if age >= 18 {
        if has_ticket {
            println!("Allowed");
        } else {
            println!("Need ticket");
        }
    } else {
        println!("Too young");
    }
}
```

Flow:

```text
age >= 18?
│
├── NO → Too young
│
└── YES
      │
      └── has_ticket?
             │
             ├── YES → Allowed
             └── NO  → Need ticket
```

---

# 17. Nhưng nested `if` có thể trở nên xấu

Ví dụ:

```rust
if age >= 18 {
    if has_ticket {
        if !is_banned {
            if is_member {
                println!("Allowed");
            }
        }
    }
}
```

Rất khó đọc.

Có thể kết hợp điều kiện:

```rust
if age >= 18 && has_ticket && !is_banned && is_member {
    println!("Allowed");
}
```

Thường dễ đọc hơn.

---

# 18. `if` với Boolean

Ví dụ:

```rust
let is_admin = true;

if is_admin {
    println!("Admin");
}
```

Không cần:

```rust
if is_admin == true
```

Cả hai có thể hoạt động, nhưng:

```rust
if is_admin
```

là cách idiomatic hơn.

---

# 19. Phủ định Boolean

Thay vì:

```rust
if is_banned == false {
    println!("Allowed");
}
```

thường viết:

```rust
if !is_banned {
    println!("Allowed");
}
```

---

# 20. Kết hợp nhiều điều kiện

```rust
let age = 25;
let is_member = true;
let is_banned = false;

if age >= 18 && is_member && !is_banned {
    println!("Access granted");
}
```

Đọc:

```text
age >= 18
AND
is_member
AND
NOT is_banned
```

---

# 21. Scope của `if`

Mỗi block `{}` tạo scope.

```rust
fn main() {
    let x = 10;

    if x > 5 {
        let y = 20;

        println!("{y}");
    }

    // println!("{y}"); // lỗi
}
```

`y` chỉ tồn tại trong block:

```text
if block
┌────────────────┐
│ y = 20         │
│                │
│ dùng được      │
└────────────────┘

ra ngoài → y không tồn tại
```

---

# 22. Shadowing trong `if`

```rust
fn main() {
    let value = 10;

    if value > 5 {
        let value = 20;

        println!("inner: {value}");
    }

    println!("outer: {value}");
}
```

Output:

```text
inner: 20
outer: 10
```

Đây liên quan trực tiếp đến Buổi 8.

---

# 23. `if` có thể trả về `String`

```rust
fn main() {
    let age = 20;

    let message = if age >= 18 {
        String::from("You are an adult")
    } else {
        String::from("You are a minor")
    };

    println!("{message}");
}
```

Cả hai branch đều có kiểu:

```text
String
```

nên hợp lệ.

---

# 24. `if` trả về số

```rust
fn main() {
    let a = 10;
    let b = 20;

    let max = if a > b {
        a
    } else {
        b
    };

    println!("max = {max}");
}
```

Đây chính là pattern:

```text
condition
    ↓
select value
```

---

# 25. Viết hàm `max`

```rust
fn max(a: i32, b: i32) -> i32 {
    if a > b {
        a
    } else {
        b
    }
}

fn main() {
    let result = max(10, 20);

    println!("{result}");
}
```

Output:

```text
20
```

Chú ý:

```rust
if a > b {
    a
} else {
    b
}
```

không có `return`.

Đây là **implicit return của expression**.

---

# 26. `return` vẫn tồn tại

Bạn vẫn có thể:

```rust
fn max(a: i32, b: i32) -> i32 {
    if a > b {
        return a;
    }

    b
}
```

Nhưng Rust thường ưu tiên expression-oriented style:

```rust
fn max(a: i32, b: i32) -> i32 {
    if a > b {
        a
    } else {
        b
    }
}
```

---

# 27. Một điểm cực kỳ quan trọng

Đừng viết:

```rust
fn max(a: i32, b: i32) -> i32 {
    if a > b {
        return a;
    } else {
        return b;
    }
}
```

Code này không sai.

Nhưng Rust thường có thể viết gọn:

```rust
fn max(a: i32, b: i32) -> i32 {
    if a > b {
        a
    } else {
        b
    }
}
```

Hãy tập suy nghĩ:

> **Expression trước, statement sau.**

---

# 28. `if` không có `else`

Ví dụ:

```rust
let x = 10;

if x > 5 {
    println!("Greater");
}
```

Đây là hợp lệ.

Nhưng:

```rust
let result = if x > 5 {
    100
};
```

không hợp lệ theo cách bạn mong muốn, vì nếu điều kiện false thì expression không có giá trị `100` để trả về.

Nếu muốn `if` trả giá trị, thông thường cần cả hai nhánh:

```rust
let result = if x > 5 {
    100
} else {
    0
};
```

---

# 29. `if let`

Bây giờ chúng ta chạm vào một tính năng rất quan trọng.

Ví dụ có:

```rust
let value = Some(10);
```

Ta có thể:

```rust
if let Some(number) = value {
    println!("number = {number}");
}
```

Output:

```text
number = 10
```

---

# 30. Tại sao `if let` tồn tại?

Rust có hệ thống **pattern matching** rất mạnh.

Sau này chúng ta sẽ học:

```rust
match
```

Nhưng đôi khi bạn chỉ quan tâm một pattern.

Thay vì:

```rust
match value {
    Some(number) => println!("{number}"),
    None => {}
}
```

có thể viết:

```rust
if let Some(number) = value {
    println!("{number}");
}
```

---

# 31. `if let` với `Option`

Ví dụ:

```rust
fn main() {
    let username = Some("alice");

    if let Some(name) = username {
        println!("Hello, {name}");
    }
}
```

Output:

```text
Hello, alice
```

Nếu:

```rust
let username: Option<&str> = None;
```

thì block không chạy.

---

# 32. `if let ... else`

Có thể viết:

```rust
fn main() {
    let username: Option<&str> = None;

    if let Some(name) = username {
        println!("Hello, {name}");
    } else {
        println!("No username");
    }
}
```

Output:

```text
No username
```

---

# 33. `if let` sẽ rất quan trọng sau này

Khi học:

```text
Option<T>
Result<T, E>
enum
match
error handling
```

`if let` sẽ xuất hiện rất thường xuyên.

---

# 34. `if` và `match`

Tạm thời có thể hình dung:

```text
if
 ↓
boolean condition

match
 ↓
pattern matching
```

Ví dụ:

```rust
if age >= 18 {
    ...
}
```

Trong khi:

```rust
match age {
    18 => ...,
    20 => ...,
    _ => ...,
}
```

`match` mạnh hơn nhiều khi xử lý nhiều pattern.

Buổi 11 chúng ta sẽ đào sâu.

---

# 35. Mini Project — Grade Analyzer

Tạo project:

```bash
cargo new grade_analyzer
cd grade_analyzer
```

`src/main.rs`:

```rust
fn calculate_grade(score: f64) -> &'static str {
    if score >= 9.0 {
        "A"
    } else if score >= 8.0 {
        "B"
    } else if score >= 6.5 {
        "C"
    } else if score >= 5.0 {
        "D"
    } else {
        "F"
    }
}

fn is_passed(score: f64) -> bool {
    score >= 5.0
}

fn main() {
    let score = 8.5;

    let grade = calculate_grade(score);
    let passed = is_passed(score);

    println!("==============================");
    println!("        GRADE ANALYZER");
    println!("==============================");

    println!("Score  : {score:.2}");
    println!("Grade  : {grade}");
    println!("Passed : {passed}");
}
```

Chạy:

```bash
cargo run
```

Kết quả:

```text
==============================
        GRADE ANALYZER
==============================
Score  : 8.50
Grade  : B
Passed : true
```

---

# 36. Phân tích `calculate_grade`

```rust
fn calculate_grade(score: f64) -> &'static str {
```

Hàm nhận:

```text
f64
```

và trả:

```text
&'static str
```

Logic:

```text
score >= 9.0 → A
score >= 8.0 → B
score >= 6.5 → C
score >= 5.0 → D
otherwise    → F
```

Đây là một ví dụ hoàn hảo để luyện `if / else if / else`.

---

# 37. Cẩn thận với thứ tự

Không nên:

```rust
if score >= 5.0 {
    "D"
} else if score >= 9.0 {
    "A"
}
```

Với:

```text
score = 10
```

Rust sẽ chọn:

```text
10 >= 5
```

→ `true`

và trả `"D"`.

Vì vậy:

> **Điều kiện cụ thể hơn nên đặt trước điều kiện tổng quát hơn.**

---

# 38. Mini Project 2 — Access Controller

```rust
fn can_access(
    age: u32,
    is_member: bool,
    is_banned: bool,
) -> bool {
    if age < 18 {
        false
    } else if is_banned {
        false
    } else if !is_member {
        false
    } else {
        true
    }
}

fn main() {
    let age = 25;
    let is_member = true;
    let is_banned = false;

    let allowed = can_access(
        age,
        is_member,
        is_banned,
    );

    println!("Access: {allowed}");
}
```

---

# 39. Có thể viết ngắn hơn

Hàm trên có thể viết:

```rust
fn can_access(
    age: u32,
    is_member: bool,
    is_banned: bool,
) -> bool {
    age >= 18 && is_member && !is_banned
}
```

Đây là một ví dụ rất hay về:

```text
boolean expression
        ↓
return value
```

---

# 40. Nhưng đừng quá thích code ngắn

Code:

```rust
age >= 18 && is_member && !is_banned
```

ngắn.

Nhưng khi business rule phức tạp, có thể tốt hơn:

```rust
if age < 18 {
    false
} else if is_banned {
    false
} else if !is_member {
    false
} else {
    true
}
```

Mục tiêu không phải:

> ít dòng nhất.

Mục tiêu là:

> **dễ hiểu nhất mà vẫn rõ ràng.**

---

# 41. Mini Project 3 — Temperature Analyzer

```rust
fn describe_temperature(temp: f64) -> &'static str {
    if temp < 0.0 {
        "Freezing"
    } else if temp < 15.0 {
        "Cold"
    } else if temp < 25.0 {
        "Cool"
    } else if temp < 35.0 {
        "Warm"
    } else {
        "Hot"
    }
}

fn main() {
    let temperature = 28.5;

    let description = describe_temperature(temperature);

    println!("Temperature : {temperature:.1}°C");
    println!("Description : {description}");
}
```

Kết quả:

```text
Temperature : 28.5°C
Description : Warm
```

---

# 42. Bài tập 1 — Positive / Negative / Zero

Viết chương trình:

```rust
let number = -10;
```

In một trong ba:

```text
Positive
Negative
Zero
```

Yêu cầu sử dụng:

```text
if
else if
else
```

---

# 43. Bài tập 2 — Maximum

Viết hàm:

```rust
fn max(a: i32, b: i32) -> i32
```

Không dùng thư viện.

Ví dụ:

```rust
max(10, 20)
```

phải trả:

```text
20
```

---

# 44. Bài tập 3 — Minimum

Viết:

```rust
fn min(a: i32, b: i32) -> i32
```

Ví dụ:

```rust
min(10, 20)
```

→

```text
10
```

---

# 45. Bài tập 4 — Grade

Viết hàm:

```rust
fn grade(score: f64) -> &'static str
```

Quy tắc:

```text
>= 9.0 → A
>= 8.0 → B
>= 6.5 → C
>= 5.0 → D
< 5.0  → F
```

---

# 46. Bài tập 5 — Admission

Cho:

```rust
let age = 22;
let score = 8.5;
```

Điều kiện:

```text
age >= 18
AND
score >= 7.0
```

In:

```text
Accepted
```

hoặc:

```text
Rejected
```

---

# 47. Bài tập 6 — Nested Scope

Dự đoán output:

```rust
fn main() {
    let x = 10;

    if x > 5 {
        let x = 20;

        println!("A: {x}");

        if x > 15 {
            let x = 30;
            println!("B: {x}");
        }

        println!("C: {x}");
    }

    println!("D: {x}");
}
```

Sau đó chạy thử và giải thích tại sao.

---

# 48. Bài tập 7 — `if` Expression

Viết:

```rust
let number = 10;

let result = if number % 2 == 0 {
    "even"
} else {
    "odd"
};
```

Sau đó in:

```text
10 is even
```

---

# 49. Bài tập 8 — `if let`

Cho:

```rust
let value = Some(100);
```

Viết:

```rust
if let ...
```

để in:

```text
Value: 100
```

Sau đó thử:

```rust
let value: Option<i32> = None;
```

và thêm `else`.

---

# 50. Bài tập 9 — Mini Project

## User Access Analyzer

Tạo chương trình với:

```rust
let age = 25;
let is_member = true;
let is_banned = false;
let has_verified_email = true;
```

Quy tắc:

```text
1. Nếu age < 18
   → "Too young"

2. Nếu bị banned
   → "Account banned"

3. Nếu không phải member
   → "Membership required"

4. Nếu email chưa verified
   → "Email verification required"

5. Nếu tất cả hợp lệ
   → "Access granted"
```

Hãy triển khai bằng:

```text
if
else if
else
```

Sau đó refactor thành một hàm:

```rust
fn check_access(...) -> &'static str
```

---

# 51. Thử thách — Không dùng `mut`

Hãy viết:

```text
Temperature Analyzer
```

nhận một nhiệt độ:

```rust
let temperature = 31.5;
```

và tạo:

```text
temperature
    ↓
if expression
    ↓
description
```

Yêu cầu:

* Không dùng `mut`.
* Không dùng `return`.
* Không dùng biến trung gian không cần thiết.
* Hàm trả về `&'static str`.

---

# 52. Tư duy Rust cần hình thành

Đừng chỉ nhìn:

```rust
if condition {
    ...
}
```

Hãy nhìn:

```text
condition
    ↓
decision
    ↓
expression
    ↓
value
```

Ví dụ:

```rust
let category = if age >= 18 {
    "adult"
} else {
    "minor"
};
```

Đây chính là **expression-oriented programming**.

---

# 53. `if` — Statement hay Expression?

Câu trả lời:

> Trong Rust, `if` là expression.

Nó có thể đứng một mình:

```rust
if age >= 18 {
    println!("Adult");
}
```

hoặc tạo giá trị:

```rust
let status = if age >= 18 {
    "adult"
} else {
    "minor"
};
```

Đây là kiến thức nền tảng để sau này hiểu:

```text
match
loop
block
function return
Result
Option
```

---

# 54. Tổng kết Buổi 10

Bạn cần nắm chắc:

```text
if
├── if
├── if / else
├── if / else if / else
│
├── condition phải là bool
│
├── if là expression
│
├── expression có thể trả value
│
├── các branch phải có kiểu tương thích
│
├── block tạo scope
│
└── if let dùng để match một pattern
```

Đặc biệt nhớ pattern này:

```rust
let result = if condition {
    value_a
} else {
    value_b
};
```

Đây là một trong những idiom Rust quan trọng nhất.

---

# Roadmap tiếp theo

Hiện tại:

```text
Rust Foundation
│
├── Buổi 01 — Rust Introduction
├── Buổi 02 — Cargo
├── Buổi 03 — Variables
├── Buổi 04 — Data Types
├── Buổi 05 — Functions
├── Buổi 06 — Comments & Documentation
├── Buổi 07 — Formatting
├── Buổi 08 — Shadowing & Constants
├── Buổi 09 — Operators
└── Buổi 10 — if / else / else if  ← DONE
```

### Buổi 11 — `match` & Pattern Matching

Đây sẽ là bước chuyển rất quan trọng từ **control flow thông thường** sang tư duy Rust thực sự:

```rust
match value {
    1 => ...,
    2 => ...,
    3 => ...,
    _ => ...,
}
```

Chúng ta sẽ học:

* `match` expression
* exhaustive matching
* `_`
* nhiều pattern
* range pattern
* destructuring cơ bản
* `match` trả value
* `match` với `enum`
* `match` với `Option`
* `match` với `Result`
* `if let` vs `match`
* pattern matching sâu hơn
* mini project **Command Parser** hoàn chỉnh.
