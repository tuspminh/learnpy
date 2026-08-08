# Rust Professional 2026 — Buổi 12

## `loop`, `break`, `continue` và Loop Labels

Buổi 12 bắt đầu phần **Iteration & Loop Control** của Rust.

Điểm quan trọng nhất hôm nay không phải chỉ là biết viết:

```rust
loop {
    ...
}
```

mà là hiểu một tư duy rất đặc trưng của Rust:

> **`loop` là một expression và có thể trả về giá trị.**

Sau buổi này, bạn sẽ có nền tảng để học `while`, `for`, iterator và sau này là async loop.

---

# 1. Bản đồ Buổi 12

```text
Loop
│
├── loop
│
├── break
│   └── break value
│
├── continue
│
├── nested loop
│
├── loop labels
│   ├── 'outer
│   └── break 'outer
│
├── loop as expression
│
└── Mini Project
    └── Interactive CLI Menu
```

---

# 2. `loop` cơ bản

Cú pháp:

```rust
loop {
    // code
}
```

Ví dụ:

```rust
fn main() {
    loop {
        println!("Hello");
    }
}
```

Chương trình sẽ chạy vô hạn:

```text
Hello
Hello
Hello
Hello
...
```

Đây gọi là:

```text
infinite loop
```

---

# 3. Dừng `loop` bằng `break`

```rust
fn main() {
    loop {
        println!("Hello");

        break;
    }

    println!("Done");
}
```

Output:

```text
Hello
Done
```

Flow:

```text
loop
 ↓
println
 ↓
break
 ↓
thoát loop
 ↓
Done
```

---

# 4. `break` chỉ thoát loop gần nhất

Ví dụ:

```rust
fn main() {
    loop {
        println!("Inside");

        break;
    }

    println!("Outside");
}
```

`break` kết thúc `loop`.

---

# 5. `loop` + biến đếm

```rust
fn main() {
    let mut count = 0;

    loop {
        count += 1;

        println!("count = {count}");

        if count >= 5 {
            break;
        }
    }
}
```

Output:

```text
count = 1
count = 2
count = 3
count = 4
count = 5
```

Đây là pattern cơ bản:

```text
loop
 ↓
update state
 ↓
check condition
 ↓
break?
```

---

# 6. Tại sao cần `mut`?

Ta có:

```rust
let mut count = 0;
```

vì:

```rust
count += 1;
```

thay đổi giá trị của `count`.

Nếu:

```rust
let count = 0;
```

thì:

```rust
count += 1;
```

sẽ lỗi.

Đây nối trực tiếp với kiến thức về **immutability** đã học trước đó.

---

# 7. `break` có thể trả về giá trị

Đây là phần quan trọng nhất.

Rust cho phép:

```rust
let result = loop {
    break 42;
};
```

Sau đó:

```rust
println!("{result}");
```

Output:

```text
42
```

---

# 8. `loop` là expression

Ví dụ:

```rust
fn main() {
    let result = loop {
        break 100;
    };

    println!("result = {result}");
}
```

Output:

```text
result = 100
```

Tư duy:

```text
loop
 ↓
break value
 ↓
expression value
```

---

# 9. `loop` có thể dùng để tìm giá trị

Ví dụ:

```rust
fn main() {
    let mut count = 0;

    let result = loop {
        count += 1;

        if count == 10 {
            break count * 2;
        }
    };

    println!("result = {result}");
}
```

Output:

```text
result = 20
```

Ở đây:

```rust
break count * 2;
```

trả:

```text
20
```

cho:

```rust
let result
```

---

# 10. Đây là tư duy expression-oriented

Bạn đã học:

```rust
let result = if condition {
    value_a
} else {
    value_b
};
```

Buổi 11:

```rust
let result = match value {
    pattern => result,
    _ => result,
};
```

Buổi 12:

```rust
let result = loop {
    break value;
};
```

Ba cấu trúc đều có thể tạo giá trị:

```text
if
 ↓
value

match
 ↓
value

loop
 ↓
break value
 ↓
value
```

Đây là một pattern rất quan trọng trong Rust.

---

# 11. `break` không có value

```rust
loop {
    break;
}
```

Giá trị của loop là:

```text
()
```

Tương đương:

```rust
let result = loop {
    break;
};
```

thì:

```text
result: ()
```

---

# 12. `break` có value

```rust
let result = loop {
    break 100;
};
```

Kiểu:

```text
result: i32
```

---

# 13. Giá trị `break` phải thống nhất

Ví dụ:

```rust
let result = loop {
    if condition {
        break 10;
    }

    break 20;
};
```

Hợp lệ vì cả hai đều là:

```text
i32
```

Nhưng không nên:

```rust
let result = loop {
    if condition {
        break 10;
    }

    break "hello";
};
```

Vì:

```text
10       → i32
"hello"  → &str
```

Rust không thể xác định kiểu của `result`.

---

# 14. `continue`

`continue` không kết thúc loop.

Nó:

> bỏ qua phần còn lại của vòng lặp hiện tại và chuyển sang iteration tiếp theo.

Ví dụ:

```rust
fn main() {
    let mut count = 0;

    loop {
        count += 1;

        if count == 3 {
            continue;
        }

        println!("{count}");

        if count >= 5 {
            break;
        }
    }
}
```

Output:

```text
1
2
4
5
```

---

# 15. Flow của `continue`

Khi:

```text
count == 3
```

thì:

```text
continue
   ↓
bỏ qua println
   ↓
quay lại đầu loop
```

Do đó `3` không được in.

---

# 16. `break` vs `continue`

| Keyword    | Ý nghĩa                  |
| ---------- | ------------------------ |
| `break`    | Thoát loop               |
| `continue` | Sang iteration tiếp theo |

Ví dụ:

```rust
loop {
    if condition_a {
        break;
    }

    if condition_b {
        continue;
    }

    println!("work");
}
```

Tư duy:

```text
break
 ↓
EXIT

continue
 ↓
NEXT ITERATION
```

---

# 17. Cẩn thận với `continue`

Ví dụ:

```rust
let mut count = 0;

loop {
    if count == 5 {
        continue;
    }

    count += 1;
}
```

Đây là lỗi logic.

Khi:

```text
count == 5
```

thì:

```text
continue
```

được gọi mãi.

`count` không còn tăng nữa.

Kết quả:

```text
infinite loop
```

---

# 18. Pattern an toàn hơn

```rust
let mut count = 0;

loop {
    count += 1;

    if count == 5 {
        continue;
    }

    if count > 10 {
        break;
    }
}
```

Luôn chú ý:

> Có trạng thái nào bị `continue` bỏ qua khiến điều kiện `break` không bao giờ đạt được không?

Đây là một lỗi rất thường gặp khi viết loop.

---

# 19. `loop` với nhiều điều kiện

Ví dụ:

```rust
fn main() {
    let mut number = 0;

    loop {
        number += 1;

        if number % 2 == 0 {
            continue;
        }

        println!("{number}");

        if number >= 10 {
            break;
        }
    }
}
```

Output:

```text
1
3
5
7
9
```

Lưu ý:

`10` không được in vì trước đó:

```rust
if number % 2 == 0 {
    continue;
}
```

đã chuyển sang iteration tiếp theo.

---

# 20. Nested loop

Rust cho phép loop bên trong loop.

```rust
fn main() {
    loop {
        println!("Outer");

        loop {
            println!("Inner");

            break;
        }

        break;
    }
}
```

Output:

```text
Outer
Inner
```

---

# 21. Vấn đề với nested loop

`break`:

```rust
break;
```

chỉ thoát loop gần nhất.

Ví dụ:

```rust
loop {
    println!("outer");

    loop {
        println!("inner");

        break;
    }

    println!("still outer");

    break;
}
```

Output:

```text
outer
inner
still outer
```

---

# 22. Loop Labels

Khi có nested loop, Rust cho phép đặt tên cho loop.

Cú pháp:

```rust
'outer: loop {
    ...
}
```

Sau đó:

```rust
break 'outer;
```

---

# 23. Ví dụ

```rust
fn main() {
    'outer: loop {
        println!("Outer");

        loop {
            println!("Inner");

            break 'outer;
        }
    }

    println!("Done");
}
```

Output:

```text
Outer
Inner
Done
```

`break 'outer` đã thoát **loop bên ngoài**.

---

# 24. Tại sao có dấu `'`?

Label:

```rust
'outer
```

có syntax đặc biệt của Rust.

Nó không phải:

```rust
&str
```

và cũng không phải:

```rust
char
```

Nó là:

```text
loop label
```

Sau này bạn sẽ gặp dấu `'` rất nhiều khi học **lifetime**.

Nhưng:

```rust
'outer
```

ở đây **không phải lifetime**.

---

# 25. Nested loop + label

Ví dụ kinh điển:

```rust
fn main() {
    let mut x = 0;

    'outer: loop {
        x += 1;

        let mut y = 0;

        loop {
            y += 1;

            println!("x = {x}, y = {y}");

            if x == 2 && y == 2 {
                break 'outer;
            }

            if y == 3 {
                break;
            }
        }
    }

    println!("Finished");
}
```

Output:

```text
x = 1, y = 1
x = 1, y = 2
x = 1, y = 3
x = 2, y = 1
x = 2, y = 2
Finished
```

---

# 26. `continue` cũng có label

Không chỉ:

```rust
break 'outer;
```

mà còn:

```rust
continue 'outer;
```

Ví dụ:

```rust
fn main() {
    'outer: loop {
        println!("Outer");

        loop {
            println!("Inner");

            continue 'outer;
        }
    }
}
```

Chương trình sẽ liên tục quay lại:

```text
'outer
```

---

# 27. `break 'outer` vs `break`

```text
break
 ↓
thoát loop hiện tại
```

Trong khi:

```text
break 'outer
 ↓
thoát loop có label 'outer
```

---

# 28. `continue` vs `continue 'outer`

```rust
continue;
```

→ iteration tiếp theo của loop hiện tại.

```rust
continue 'outer;
```

→ iteration tiếp theo của loop có label `'outer`.

---

# 29. Ví dụ thực tế — tìm số nguyên tố

Hãy xem một ví dụ sử dụng nested loop.

```rust
fn main() {
    let number = 17;
    let mut is_prime = true;

    if number < 2 {
        is_prime = false;
    } else {
        let mut divisor = 2;

        loop {
            if divisor * divisor > number {
                break;
            }

            if number % divisor == 0 {
                is_prime = false;
                break;
            }

            divisor += 1;
        }
    }

    println!("{number} is prime: {is_prime}");
}
```

Output:

```text
17 is prime: true
```

---

# 30. Nhưng ta có thể tận dụng `loop` expression

```rust
fn is_prime(number: u32) -> bool {
    if number < 2 {
        return false;
    }

    let mut divisor = 2;

    loop {
        if divisor * divisor > number {
            break true;
        }

        if number % divisor == 0 {
            break false;
        }

        divisor += 1;
    }
}
```

Đây là code rất đáng chú ý.

Ta có:

```rust
break true;
```

hoặc:

```rust
break false;
```

nên:

```rust
loop
```

trả về:

```text
bool
```

---

# 31. Phân tích

```rust
let result = loop {
    ...
    break true;
};
```

tương đương tư duy:

```text
loop
 ↓
tìm kết quả
 ↓
break result
 ↓
return result
```

Đây là cách rất tự nhiên trong Rust.

---

# 32. Mini Project — Number Guess Engine

Không cần input người dùng ngay.

```rust
fn find_target(target: i32) -> i32 {
    let mut number = 0;

    loop {
        number += 1;

        if number == target {
            break number;
        }
    }
}

fn main() {
    let result = find_target(10);

    println!("Found: {result}");
}
```

Output:

```text
Found: 10
```

---

# 33. Mini Project — Counter

```rust
fn count_to(limit: u32) {
    let mut count = 0;

    loop {
        count += 1;

        println!("{count}");

        if count >= limit {
            break;
        }
    }
}

fn main() {
    count_to(5);
}
```

---

# 34. Mini Project — Sum

Dùng `loop` để tính:

```text
1 + 2 + 3 + ... + 100
```

```rust
fn main() {
    let mut number = 1;
    let mut sum = 0;

    loop {
        sum += number;

        if number >= 100 {
            break;
        }

        number += 1;
    }

    println!("sum = {sum}");
}
```

Output:

```text
sum = 5050
```

---

# 35. Viết bằng `loop` expression

Ta có thể refactor:

```rust
fn main() {
    let mut number = 1;

    let sum = loop {
        if number > 100 {
            break 5050;
        }

        number += 1;
    };

    println!("{sum}");
}
```

Nhưng cách này không tốt vì chúng ta hard-code `5050`.

Tốt hơn:

```rust
fn main() {
    let mut number = 1;
    let mut sum = 0;

    let result = loop {
        sum += number;

        if number >= 100 {
            break sum;
        }

        number += 1;
    };

    println!("sum = {result}");
}
```

Đây là cách tốt hơn.

---

# 36. Mini Project — Retry Engine

Một pattern rất quan trọng trong ứng dụng thực tế:

```text
attempt
 ↓
operation
 ↓
success?
 ├── YES → return
 └── NO
      ↓
    retry
```

Ví dụ mô phỏng:

```rust
fn connect(max_attempts: u32) -> bool {
    let mut attempt = 0;

    loop {
        attempt += 1;

        println!("Attempt {attempt}");

        if attempt == 3 {
            break true;
        }

        if attempt >= max_attempts {
            break false;
        }
    }
}

fn main() {
    let connected = connect(5);

    println!("Connected: {connected}");
}
```

Output:

```text
Attempt 1
Attempt 2
Attempt 3
Connected: true
```

---

# 37. Đây là nền tảng cho framework sau này

Pattern:

```rust
loop {
    attempt();

    if success {
        break result;
    }

    if should_stop {
        break error;
    }

    retry();
}
```

sẽ xuất hiện trong:

* crawler
* worker
* network client
* retry system
* task runner
* CLI
* job processing
* connection pool

---

# 38. Mini Project — Interactive CLI Menu

Đây là project quan trọng nhất hôm nay.

Ta mô phỏng:

```text
=====================
      MAIN MENU
=====================

1. Start
2. Status
3. Stop
4. Exit
```

Code:

```rust
use std::io::{self, Write};

fn main() {
    loop {
        println!();
        println!("=====================");
        println!("      MAIN MENU");
        println!("=====================");
        println!("1. Start");
        println!("2. Status");
        println!("3. Stop");
        println!("4. Exit");

        print!("Choose: ");
        io::stdout().flush().unwrap();

        let mut input = String::new();

        io::stdin()
            .read_line(&mut input)
            .unwrap();

        let choice = input.trim();

        match choice {
            "1" => {
                println!("Starting...");
            }

            "2" => {
                println!("Status: Running");
            }

            "3" => {
                println!("Stopping...");
            }

            "4" => {
                println!("Goodbye!");
                break;
            }

            _ => {
                println!("Invalid choice.");
            }
        }
    }
}
```

---

# 39. Chạy project

Tạo:

```bash
cargo new cli_menu
cd cli_menu
cargo run
```

Ví dụ:

```text
=====================
      MAIN MENU
=====================
1. Start
2. Status
3. Stop
4. Exit

Choose: 2
Status: Running
```

Sau đó menu xuất hiện lại.

Chọn:

```text
4
```

thì:

```text
Goodbye!
```

và chương trình kết thúc.

---

# 40. Kiến trúc của chương trình

Bạn vừa kết hợp:

```text
loop
  │
  ├── display menu
  │
  ├── read input
  │
  ├── match command
  │    │
  │    ├── 1
  │    ├── 2
  │    ├── 3
  │    └── 4 → break
  │
  └── repeat
```

Đây là một pattern rất quan trọng khi xây CLI.

---

# 41. Refactor thành function

Thay vì nhét tất cả vào `main`:

```rust
use std::io::{self, Write};

fn show_menu() {
    println!();
    println!("=====================");
    println!("      MAIN MENU");
    println!("=====================");
    println!("1. Start");
    println!("2. Status");
    println!("3. Stop");
    println!("4. Exit");
}

fn read_choice() -> String {
    print!("Choose: ");
    io::stdout().flush().unwrap();

    let mut input = String::new();

    io::stdin()
        .read_line(&mut input)
        .unwrap();

    input.trim().to_string()
}

fn main() {
    loop {
        show_menu();

        let choice = read_choice();

        match choice.as_str() {
            "1" => println!("Starting..."),
            "2" => println!("Status: Running"),
            "3" => println!("Stopping..."),

            "4" => {
                println!("Goodbye!");
                break;
            }

            _ => println!("Invalid choice."),
        }
    }
}
```

Đây là thiết kế tốt hơn.

---

# 42. Tại sao `choice.as_str()`?

`read_choice()` trả:

```rust
String
```

Trong:

```rust
match choice.as_str()
```

chúng ta lấy:

```text
String
 ↓
&str
```

để match với:

```rust
"1"
"2"
"3"
"4"
```

Sau này khi học ownership/borrowing, bạn sẽ hiểu sâu hơn tại sao đây là cách phù hợp.

---

# 43. Một điểm quan trọng về `String`

Ta có:

```rust
let choice = read_choice();
```

`choice` là:

```text
String
```

Nhưng:

```rust
match choice.as_str()
```

không chuyển ownership của `String` đi.

Nó tạo một string slice:

```text
&str
```

tham chiếu vào dữ liệu bên trong.

Đây sẽ là nền tảng cho:

```text
Borrowing
References
Ownership
```

mà chúng ta sẽ học kỹ ở phần sau.

---

# 44. Bài tập 1 — Counter

Viết:

```rust
fn count_to(limit: u32)
```

Sử dụng `loop`.

Ví dụ:

```text
count_to(5)
```

Output:

```text
1
2
3
4
5
```

Không dùng `while`.

---

# 45. Bài tập 2 — Even Numbers

Dùng `loop` in:

```text
2
4
6
8
10
```

Không dùng `for`.

---

# 46. Bài tập 3 — Skip

Dùng:

```rust
continue
```

để in các số từ `1` đến `10`, nhưng bỏ qua:

```text
5
```

Kết quả:

```text
1
2
3
4
6
7
8
9
10
```

---

# 47. Bài tập 4 — Sum

Dùng:

```rust
loop
break value
```

để tính:

```text
1 + 2 + ... + 100
```

Yêu cầu:

```rust
let result = loop {
    ...
};
```

Kết quả:

```text
5050
```

---

# 48. Bài tập 5 — Find First Divisible

Viết:

```rust
fn find_first_divisible(
    start: u32,
    divisor: u32,
) -> u32
```

Ví dụ:

```rust
find_first_divisible(10, 7)
```

Kết quả:

```text
14
```

Sử dụng:

```text
loop
break value
```

---

# 49. Bài tập 6 — Retry

Viết:

```rust
fn retry(max_attempts: u32) -> bool
```

Giả lập:

```text
attempt 1 → fail
attempt 2 → fail
attempt 3 → success
```

Nếu `max_attempts < 3`:

```text
false
```

Nếu đủ số lần:

```text
true
```

---

# 50. Bài tập 7 — Nested Loop

Tạo output:

```text
1 1
1 2
1 3

2 1
2 2
2 3

3 1
3 2
3 3
```

Sử dụng **hai `loop` lồng nhau**.

Không dùng `for`.

---

# 51. Bài tập 8 — Loop Label

Viết chương trình có:

```text
outer loop
    inner loop
```

Khi:

```text
x == 3
y == 2
```

thoát cả hai loop.

Bắt buộc sử dụng:

```rust
'outer:
```

và:

```rust
break 'outer;
```

---

# 52. Bài tập 9 — Continue Label

Tạo hai loop:

```text
outer
  inner
```

Khi một điều kiện nào đó xảy ra trong inner loop, hãy:

```rust
continue 'outer;
```

để bỏ toàn bộ iteration hiện tại của outer loop.

---

# 53. Bài tập 10 — Interactive CLI

Nâng cấp menu thành:

```text
========================
     STORY MANAGER
========================

1. List stories
2. Add story
3. Remove story
4. Search story
5. Exit
```

Dùng:

```text
loop
match
break
```

Chưa cần database.

Chỉ cần in:

```text
List stories...
Add story...
Remove story...
Search story...
```

Đây chính là bước đầu tiên hướng tới **CLI framework** mà bạn có thể sử dụng cho project crawler sau này.

---

# 54. Challenge — Mini Crawler Worker

Mô phỏng một crawler worker:

```rust
enum TaskResult {
    Success,
    Retry,
    Stop,
}
```

Viết:

```rust
fn run_worker() {
    loop {
        ...
    }
}
```

Logic:

```text
Success → tiếp tục task tiếp theo

Retry → thử lại

Stop → break

```

Ví dụ:

```rust
match result {
    TaskResult::Success => {
        println!("Task completed");
    }

    TaskResult::Retry => {
        println!("Retrying...");
        continue;
    }

    TaskResult::Stop => {
        println!("Worker stopped");
        break;
    }
}
```

Đây là một bài tập rất đáng làm vì nó kết hợp:

```text
enum
+
match
+
loop
+
break
+
continue
```

---

# 55. Tư duy quan trọng nhất hôm nay

Đừng học:

```rust
loop
break
continue
```

như ba keyword rời rạc.

Hãy nhìn chúng như một hệ thống:

```text
                 ┌───────────────┐
                 │     loop      │
                 └───────┬───────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
              ▼          ▼          ▼
           normal     continue    break
              │          │          │
              │          │          ▼
              │          │       exit loop
              │          │
              │          ▼
              │       next iteration
              │
              ▼
         next statement
```

Và đặc biệt:

```text
break value
     ↓
loop expression
     ↓
result
```

---

# 56. Ba pattern cần thuộc

### Pattern 1 — Loop đến khi điều kiện

```rust
loop {
    do_something();

    if condition {
        break;
    }
}
```

### Pattern 2 — Bỏ qua iteration

```rust
loop {
    if should_skip {
        continue;
    }

    do_something();
}
```

### Pattern 3 — Loop trả kết quả

```rust
let result = loop {
    if success {
        break value;
    }
};
```

Nếu bạn nắm chắc ba pattern này, bạn đã có nền tảng rất tốt.

---

# 57. Tổng kết

Sau Buổi 12 bạn cần hiểu:

```text
loop
├── infinite loop
├── break
├── continue
├── break value
├── loop expression
├── nested loop
├── loop label
├── break 'label
└── continue 'label
```

Và đặc biệt phải hiểu:

```rust
let result = loop {
    ...
    break value;
};
```

Đây không phải một mẹo cú pháp.

Nó là biểu hiện của triết lý:

> **Rust có xu hướng biến control flow thành expression có giá trị.**

Ta đã thấy:

```text
if      → value
match   → value
loop    → value
```

---

# Roadmap

```text
Rust Foundation
│
├── 01 — Rust Introduction
├── 02 — Cargo
├── 03 — Variables
├── 04 — Data Types
├── 05 — Functions
├── 06 — Comments & Documentation
├── 07 — Formatting
├── 08 — Shadowing & Constants
├── 09 — Operators
├── 10 — if / else / else if
├── 11 — match & Pattern Matching
└── 12 — loop / break / continue       ← DONE
```

## Buổi 13 — `while`

Buổi tiếp theo sẽ đi sâu vào:

```rust
while condition {
    ...
}
```

nhưng không chỉ học cú pháp. Ta sẽ so sánh thật kỹ:

```text
loop
while
```

và xây dựng các ví dụ:

* Counter
* Input validation
* Menu loop
* Retry loop
* Sentinel loop
* `while` + `break`
* `while` + `continue`
* `while` với mutable state
* `while let`
* refactor `loop` → `while`
* mini project **Input Validator** hoàn chỉnh.
