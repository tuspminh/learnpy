# Rust Professional 2026 — Buổi 13

## `while`, điều kiện lặp và `while let`

Buổi 13 tiếp tục phần **Control Flow & Iteration**.

Ở Buổi 12, chúng ta học:

```rust
loop {
    ...
}
```

và điều khiển bằng:

```rust
break
continue
```

Hôm nay chúng ta học:

```rust
while condition {
    ...
}
```

Điểm quan trọng là bạn phải biết **khi nào dùng `loop`, khi nào dùng `while`**, thay vì chỉ nhớ cú pháp.

---

# 1. `while` là gì?

`while` thực hiện một block **chừng nào điều kiện còn `true`**.

Cú pháp:

```rust
while condition {
    // code
}
```

Ví dụ:

```rust
fn main() {
    let mut count = 1;

    while count <= 5 {
        println!("{count}");
        count += 1;
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

Flow:

```text
        ┌─────────────┐
        │ condition?  │
        └──────┬──────┘
               │
        ┌──────┴──────┐
       true          false
        │               │
        ▼               ▼
      body            exit
        │
        └───────→ condition
```

---

# 2. `while` khác `loop` như thế nào?

### `loop`

```rust
loop {
    ...
}
```

Luôn chạy cho tới khi:

```rust
break;
```

### `while`

```rust
while condition {
    ...
}
```

Tự động dừng khi:

```text
condition == false
```

So sánh:

```text
loop
 ↓
chạy
 ↓
phải break

while
 ↓
kiểm tra condition
 ↓
false → tự thoát
```

---

# 3. Ví dụ tương đương

Dùng `loop`:

```rust
fn main() {
    let mut count = 1;

    loop {
        if count > 5 {
            break;
        }

        println!("{count}");

        count += 1;
    }
}
```

Dùng `while`:

```rust
fn main() {
    let mut count = 1;

    while count <= 5 {
        println!("{count}");

        count += 1;
    }
}
```

Cách `while` rõ ràng hơn vì điều kiện kết thúc nằm ngay trên đầu loop.

---

# 4. Khi nào nên dùng `while`?

`while` phù hợp khi bạn biết:

> **Điều kiện để tiếp tục chạy là gì?**

Ví dụ:

```rust
while count < 100
```

hoặc:

```rust
while !input.is_empty()
```

hoặc:

```rust
while running
```

---

# 5. Khi nào nên dùng `loop`?

`loop` phù hợp khi logic thoát phức tạp.

Ví dụ:

```rust
loop {
    let result = do_work();

    match result {
        Success(value) => break value,
        Retry => continue,
        Stop => break default_value,
    }
}
```

Ở đây có nhiều đường thoát.

`loop` thường tự nhiên hơn `while`.

---

# 6. `while` với Boolean

Ví dụ:

```rust
fn main() {
    let mut running = true;

    while running {
        println!("Running");

        running = false;
    }

    println!("Stopped");
}
```

Output:

```text
Running
Stopped
```

Đây là một pattern rất phổ biến:

```text
state
 ↓
while state
 ↓
do work
 ↓
update state
```

---

# 7. `while` cần `bool`

Rust yêu cầu:

```rust
while condition
```

trong đó `condition` phải là:

```text
bool
```

Đúng:

```rust
while count < 10 {
    ...
}
```

Sai:

```rust
while count {
    ...
}
```

nếu `count` là số nguyên.

Rust không coi:

```text
0 → false
1 → true
```

như một số ngôn ngữ khác.

---

# 8. `while` kiểm tra trước khi chạy

Ví dụ:

```rust
fn main() {
    let count = 10;

    while count < 5 {
        println!("Hello");
    }
}
```

Không có output.

Vì:

```text
10 < 5
↓
false
↓
không chạy body
```

Đây gọi là:

> **pre-test loop**

---

# 9. `loop` khác ở điểm này

```rust
loop {
    println!("Hello");
    break;
}
```

body luôn chạy ít nhất một lần.

Trong khi:

```rust
while false {
    println!("Hello");
}
```

không chạy lần nào.

---

# 10. `while` + `break`

Bạn hoàn toàn có thể dùng `break`:

```rust
fn main() {
    let mut count = 0;

    while count < 10 {
        count += 1;

        if count == 5 {
            break;
        }

        println!("{count}");
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

Khi:

```text
count == 5
```

`break` lập tức thoát loop.

---

# 11. `while` + `continue`

```rust
fn main() {
    let mut count = 0;

    while count < 10 {
        count += 1;

        if count % 2 == 0 {
            continue;
        }

        println!("{count}");
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

Các số chẵn bị bỏ qua.

---

# 12. Cẩn thận với `continue`

Ví dụ nguy hiểm:

```rust
let mut count = 0;

while count < 10 {
    if count == 5 {
        continue;
    }

    count += 1;
}
```

Khi:

```text
count == 5
```

thì:

```text
continue
 ↓
quay lại while
 ↓
count vẫn = 5
 ↓
continue
 ↓
...
```

→ infinite loop.

---

# 13. Cách sửa

Đảm bảo state được cập nhật trước `continue`:

```rust
let mut count = 0;

while count < 10 {
    count += 1;

    if count == 5 {
        continue;
    }

    println!("{count}");
}
```

Hoặc tránh `continue` nếu không cần thiết.

---

# 14. `while` với counter

Pattern phổ biến:

```rust
let mut i = 0;

while i < limit {
    // work

    i += 1;
}
```

Ví dụ:

```rust
fn main() {
    let mut i = 0;

    while i < 5 {
        println!("i = {i}");

        i += 1;
    }
}
```

Output:

```text
i = 0
i = 1
i = 2
i = 3
i = 4
```

---

# 15. Off-by-one error

Một lỗi rất phổ biến:

```rust
let mut i = 0;

while i <= 5 {
    println!("{i}");
    i += 1;
}
```

Output:

```text
0
1
2
3
4
5
```

Nếu bạn muốn đúng 5 lần:

```rust
while i < 5
```

→

```text
0
1
2
3
4
```

Hãy đặc biệt chú ý:

```text
< 
<=
```

---

# 16. `while` với input

Bây giờ làm ví dụ thực tế.

```rust
use std::io;

fn main() {
    let mut input = String::new();

    while input.trim() != "exit" {
        println!("Type 'exit' to quit:");

        input.clear();

        io::stdin()
            .read_line(&mut input)
            .unwrap();

        println!("You typed: {}", input.trim());
    }

    println!("Goodbye!");
}
```

Ý tưởng:

```text
while input != "exit"
        ↓
read input
        ↓
process
        ↓
repeat
```

---

# 17. Một vấn đề trong ví dụ trên

Lần đầu:

```rust
let mut input = String::new();
```

`input` rỗng.

Điều kiện:

```rust
input.trim() != "exit"
```

→ `true`.

Sau đó mới đọc input.

Đây là một ví dụ cho thấy `while` đôi khi không phải cấu trúc tự nhiên nhất cho interactive program.

---

# 18. `loop` phù hợp hơn

Ta có thể viết:

```rust
use std::io;

fn main() {
    loop {
        println!("Type 'exit' to quit:");

        let mut input = String::new();

        io::stdin()
            .read_line(&mut input)
            .unwrap();

        let input = input.trim();

        if input == "exit" {
            break;
        }

        println!("You typed: {input}");
    }

    println!("Goodbye!");
}
```

Đây là code rõ ràng hơn.

Tư duy:

```text
loop
 ↓
read input
 ↓
check command
 ├── exit → break
 └── other → process
```

---

# 19. So sánh hai cách

### `while`

```rust
while condition {
    ...
}
```

Tốt khi:

```text
điều kiện tiếp tục rõ ràng ngay từ đầu
```

### `loop`

```rust
loop {
    ...
    if condition {
        break;
    }
}
```

Tốt khi:

```text
cần thực hiện một hành động
rồi mới biết có tiếp tục hay không
```

---

# 20. `while let`

Đây là phần rất quan trọng.

Rust có:

```rust
while let pattern = expression {
    ...
}
```

Ví dụ:

```rust
fn main() {
    let mut value = Some(3);

    while let Some(number) = value {
        println!("{number}");

        value = if number > 1 {
            Some(number - 1)
        } else {
            None
        };
    }
}
```

Output:

```text
3
2
1
```

---

# 21. Phân tích `while let`

Điều kiện:

```rust
while let Some(number) = value
```

có nghĩa:

```text
value có match Some(...) không?
```

Nếu có:

```text
Some(number)
```

→ chạy body.

Nếu:

```text
None
```

→ thoát.

---

# 22. `while let` rất mạnh

Nó kết hợp:

```text
while
+
pattern matching
```

Tư duy:

```text
while
    │
    └── pattern matches?
           │
        YES │ NO
           │  └── exit
           ▼
          body
```

---

# 23. `while let` với iterator

Ví dụ:

```rust
fn main() {
    let numbers = vec![10, 20, 30];

    let mut iterator = numbers.into_iter();

    while let Some(number) = iterator.next() {
        println!("{number}");
    }
}
```

Output:

```text
10
20
30
```

Đây là một ví dụ rất quan trọng.

Ta sẽ học `Iterator` chuyên sâu ở phần sau.

---

# 24. Tại sao `iterator.next()` trả `Option`?

Vì iterator có thể:

```text
còn phần tử
    ↓
Some(value)

hết phần tử
    ↓
None
```

Do đó:

```rust
while let Some(value) = iterator.next()
```

có nghĩa:

> Cứ lấy phần tử tiếp theo chừng nào vẫn còn phần tử.

Đây là một pattern Rust cực kỳ tự nhiên.

---

# 25. `while let` vs `loop + match`

Bạn có thể viết:

```rust
loop {
    match iterator.next() {
        Some(value) => {
            println!("{value}");
        }

        None => {
            break;
        }
    }
}
```

Nhưng ngắn hơn:

```rust
while let Some(value) = iterator.next() {
    println!("{value}");
}
```

Đây chính là lý do `while let` tồn tại.

---

# 26. `while let` với `Option`

Ví dụ:

```rust
fn main() {
    let mut values = vec![
        Some(10),
        Some(20),
        Some(30),
        None,
    ];

    while let Some(value) = values.pop() {
        println!("{value}");
    }
}
```

Output:

```text
30
20
10
```

Khi `pop()` trả:

```text
None
```

loop kết thúc.

---

# 27. `while let` không chỉ dùng với `Option`

Nó dùng với **pattern bất kỳ**.

Ví dụ:

```rust
fn main() {
    let mut value = Some((10, 20));

    while let Some((x, y)) = value {
        println!("x = {x}, y = {y}");

        value = None;
    }
}
```

Ở đây chúng ta đồng thời destructure:

```text
Some
 ↓
tuple
 ↓
(x, y)
```

---

# 28. `while let` với enum

Ví dụ:

```rust
enum State {
    Running(u32),
    Stopped,
}

fn main() {
    let mut state = State::Running(3);

    while let State::Running(count) = state {
        println!("Running: {count}");

        if count == 1 {
            state = State::Stopped;
        } else {
            state = State::Running(count - 1);
        }
    }

    println!("Stopped");
}
```

Output:

```text
Running: 3
Running: 2
Running: 1
Stopped
```

Đây là một ví dụ rất hay về **state machine**.

---

# 29. `while` không phải expression như `loop`

Đây là điểm cần phân biệt.

Bạn có thể:

```rust
let result = loop {
    break 10;
};
```

Nhưng không sử dụng `while` theo cùng cách để lấy giá trị cuối loop.

Tư duy:

```text
loop
→ có thể break value

while
→ chủ yếu là điều khiển lặp
```

Nếu cần tính toán và trả kết quả từ loop, `loop` thường tự nhiên hơn.

---

# 30. Ví dụ: tìm số đầu tiên chia hết cho 7

Dùng `while`:

```rust
fn main() {
    let mut number = 1;

    while number % 7 != 0 {
        number += 1;
    }

    println!("Found: {number}");
}
```

Output:

```text
Found: 7
```

---

# 31. Nhưng nếu có giới hạn?

Ví dụ:

```text
Tìm số đầu tiên chia hết cho 7
nhưng chỉ tìm tối đa 100 lần.
```

Có thể:

```rust
fn main() {
    let mut number = 1;
    let mut attempts = 0;

    while number % 7 != 0 && attempts < 100 {
        number += 1;
        attempts += 1;
    }

    println!("number = {number}");
    println!("attempts = {attempts}");
}
```

Đây là nhiều điều kiện trong `while`.

---

# 32. Nhiều điều kiện

```rust
while condition_a && condition_b {
    ...
}
```

Ví dụ:

```rust
while count < 100 && !finished {
    ...
}
```

Hoặc:

```rust
while retries < max_retries && !success {
    ...
}
```

Đây là pattern rất phổ biến trong production code.

---

# 33. `while` + boolean state

Ví dụ worker:

```rust
fn main() {
    let mut running = true;
    let mut task = 1;

    while running {
        println!("Processing task {task}");

        task += 1;

        if task > 5 {
            running = false;
        }
    }

    println!("Worker stopped.");
}
```

---

# 34. Refactor worker

Có thể viết:

```rust
fn main() {
    let mut task = 1;

    while task <= 5 {
        println!("Processing task {task}");

        task += 1;
    }

    println!("Worker stopped.");
}
```

Cách thứ hai đơn giản hơn vì điều kiện dừng trực tiếp là:

```text
task <= 5
```

Không cần thêm:

```rust
running
```

---

# 35. Nguyên tắc

Nếu bạn có:

```rust
let mut running = true;
```

chỉ để viết:

```rust
while running
```

hãy tự hỏi:

> Tôi có thể biểu diễn điều kiện trực tiếp không?

Ví dụ:

```rust
while task <= 5
```

thường tốt hơn:

```rust
while running
```

nếu `running` không mang thêm ý nghĩa business.

---

# 36. Mini Project — Input Validator

Bây giờ xây một chương trình thực tế.

Yêu cầu:

```text
Người dùng nhập tuổi.
Nếu tuổi < 0 hoặc > 150:
    nhập lại.

Nếu hợp lệ:
    kết thúc.
```

Code:

```rust
use std::io;

fn main() {
    loop {
        println!("Enter your age:");

        let mut input = String::new();

        io::stdin()
            .read_line(&mut input)
            .unwrap();

        let age: i32 = match input.trim().parse() {
            Ok(value) => value,
            Err(_) => {
                println!("Invalid number.");
                continue;
            }
        };

        if !(0..=150).contains(&age) {
            println!("Age must be between 0 and 150.");
            continue;
        }

        println!("Valid age: {age}");

        break;
    }
}
```

---

# 37. Phân tích project

Chương trình có:

```text
loop
 │
 ├── read input
 │
 ├── parse
 │    ├── Ok → age
 │    └── Err → continue
 │
 ├── validate
 │    ├── invalid → continue
 │    └── valid
 │
 └── break
```

Bạn vừa kết hợp:

```text
loop
+
match
+
continue
+
break
+
range
```

Đây chính là kiểu code thực tế mà bạn sẽ viết rất nhiều.

---

# 38. Tại sao không dùng `while`?

Có thể, nhưng:

```rust
loop {
    ...
    if invalid {
        continue;
    }

    if valid {
        break;
    }
}
```

diễn đạt rất tự nhiên:

> Cứ hỏi cho đến khi có dữ liệu hợp lệ.

Đây là trường hợp `loop` phù hợp hơn `while`.

---

# 39. Mini Project — Password Validator

Yêu cầu:

```text
Nhập password.

Password hợp lệ khi:
- dài >= 8 ký tự
```

Code:

```rust
use std::io;

fn main() {
    loop {
        println!("Enter password:");

        let mut password = String::new();

        io::stdin()
            .read_line(&mut password)
            .unwrap();

        let password = password.trim();

        if password.len() < 8 {
            println!("Password too short.");
            continue;
        }

        println!("Password accepted.");

        break;
    }
}
```

---

# 40. Nhưng password thực tế phức tạp hơn

Sau này bạn có thể kiểm tra:

```text
length
uppercase
lowercase
digit
special character
```

Ví dụ:

```text
Password requirements:
✓ >= 8 chars
✓ uppercase
✓ lowercase
✓ number
✓ special character
```

Khi đó có thể tách:

```rust
fn validate_password(password: &str) -> bool
```

và loop chỉ lo UI/control flow.

Đây là tư duy **separation of concerns**.

---

# 41. Mini Project — Retry Simulator

```rust
fn main() {
    let max_attempts = 5;
    let mut attempts = 0;
    let mut success = false;

    while attempts < max_attempts && !success {
        attempts += 1;

        println!("Attempt {attempts}");

        if attempts == 3 {
            success = true;
        }
    }

    if success {
        println!("Operation succeeded.");
    } else {
        println!("Operation failed.");
    }
}
```

Output:

```text
Attempt 1
Attempt 2
Attempt 3
Operation succeeded.
```

---

# 42. Refactor retry bằng `loop`

Nếu operation có nhiều trạng thái:

```rust
enum Result {
    Success,
    Retry,
    Fatal,
}
```

thì `loop + match` thường tốt hơn:

```rust
loop {
    match operation() {
        Result::Success => break,
        Result::Retry => continue,
        Result::Fatal => break,
    }
}
```

Đây là một pattern bạn sẽ gặp rất nhiều trong hệ thống thực tế.

---

# 43. `while let` — pattern quan trọng cần nhớ

Hãy ghi nhớ:

```rust
while let Some(value) = iterator.next() {
    println!("{value}");
}
```

Nó có nghĩa:

```text
while
    pattern vẫn match
        ↓
    chạy body
```

Không match:

```text
↓
thoát
```

---

# 44. So sánh 3 loại loop

| Cấu trúc    | Mục đích                     |
| ----------- | ---------------------------- |
| `loop`      | Lặp vô điều kiện, tự `break` |
| `while`     | Lặp khi condition là `true`  |
| `while let` | Lặp khi pattern match        |

Ví dụ:

```rust
loop {
    ...
}
```

```rust
while running {
    ...
}
```

```rust
while let Some(value) = iterator.next() {
    ...
}
```

---

# 45. Decision Tree

Khi viết loop, hãy tự hỏi:

```text
Có condition đơn giản không?
        │
       YES
        │
        ▼
     while
```

Nếu:

```text
Cần xử lý nhiều trạng thái / nhiều đường break?
        │
       YES
        │
        ▼
      loop
```

Nếu:

```text
Đang lấy dữ liệu từ Option/pattern?
        │
       YES
        │
        ▼
   while let
```

---

# 46. Bài tập 1 — Counter

Viết:

```rust
fn count_to(limit: u32)
```

dùng `while`.

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

---

# 47. Bài tập 2 — Countdown

Viết:

```rust
fn countdown(mut n: i32)
```

Ví dụ:

```text
countdown(5)
```

Output:

```text
5
4
3
2
1
Go!
```

---

# 48. Bài tập 3 — Even Numbers

Dùng `while` in:

```text
2
4
6
8
10
```

Không dùng `for`.

---

# 49. Bài tập 4 — Sum

Viết:

```rust
fn sum_to(n: u32) -> u32
```

Dùng `while`.

Ví dụ:

```text
sum_to(100)
```

→

```text
5050
```

---

# 50. Bài tập 5 — Find Divisible

Viết:

```rust
fn find_first_divisible(
    start: u32,
    divisor: u32,
) -> u32
```

Dùng `while`.

Ví dụ:

```text
find_first_divisible(10, 7)
```

→

```text
14
```

---

# 51. Bài tập 6 — Input Validation

Viết chương trình yêu cầu người dùng nhập:

```text
1 → Start
2 → Stop
3 → Exit
```

Nếu nhập khác:

```text
Invalid command.
```

Tiếp tục hỏi.

Nếu nhập `3`:

```text
Goodbye.
```

Bạn có thể dùng:

```text
loop
match
continue
break
```

---

# 52. Bài tập 7 — `while let`

Cho:

```rust
let mut values = vec![
    Some(10),
    Some(20),
    Some(30),
];
```

Dùng:

```rust
while let
```

để lấy từng giá trị.

Output:

```text
30
20
10
```

Gợi ý:

```rust
values.pop()
```

---

# 53. Bài tập 8 — State Machine

Tạo:

```rust
enum State {
    Running(u32),
    Stopped,
}
```

Dùng:

```rust
while let State::Running(count) = state
```

để chạy:

```text
Running: 5
Running: 4
Running: 3
Running: 2
Running: 1
Stopped
```

---

# 54. Bài tập 9 — Retry Engine

Tạo:

```rust
enum TaskResult {
    Success,
    Retry,
    Fatal,
}
```

Viết:

```rust
loop
```

để:

```text
Success → break
Retry   → continue
Fatal   → break
```

Đây là bài tập rất quan trọng cho hướng **crawler/worker framework** sau này.

---

# 55. Bài tập 10 — Interactive CLI

Xây:

```text
========================
     STORY MANAGER
========================

1. List stories
2. Add story
3. Search story
4. Settings
5. Exit
```

Yêu cầu:

```text
1 → List stories...
2 → Add story...
3 → Search story...
4 → Settings...
5 → Exit
other → Invalid command
```

Chương trình phải chạy liên tục cho đến khi chọn `5`.

---

# 56. Challenge — Story Worker

Hãy mô phỏng worker:

```rust
enum WorkerState {
    Running,
    Paused,
    Stopped,
}
```

Tạo vòng lặp:

```text
Running
   ↓
process task
   ↓
Paused?
   ↓
resume
   ↓
Stopped?
   ↓
break
```

Mục tiêu là luyện:

```text
enum
match
loop
while
break
continue
```

---

# 57. Những lỗi cần tránh

### Lỗi 1 — Quên cập nhật biến

```rust
let mut count = 0;

while count < 10 {
    println!("{count}");
}
```

→ infinite loop.

---

### Lỗi 2 — `continue` trước update

```rust
while count < 10 {
    if count == 5 {
        continue;
    }

    count += 1;
}
```

→ infinite loop.

---

### Lỗi 3 — Off-by-one

```rust
while count <= 10
```

khác:

```rust
while count < 10
```

---

### Lỗi 4 — Dùng `while` cho logic quá phức tạp

Nếu có:

```text
Success
Retry
Pause
Fatal
Stop
```

thì:

```rust
loop + match
```

thường dễ hiểu hơn.

---

# 58. Tư duy quan trọng nhất

Bạn cần phân biệt:

```text
loop
```

là:

> "Cứ chạy, tôi sẽ quyết định khi nào dừng."

```text
while
```

là:

> "Cứ chạy miễn điều kiện này còn đúng."

```text
while let
```

là:

> "Cứ chạy miễn pattern này còn match."

Đây là cách tư duy quan trọng hơn việc thuộc syntax.

---

# 59. Tổng kết Buổi 13

Bạn cần nắm chắc:

```text
while
├── condition
├── break
├── continue
├── multiple conditions
├── mutable state
├── counter
└── input validation
```

và đặc biệt:

```text
while let
├── Option
├── Iterator
├── enum
└── destructuring
```

Pattern quan trọng:

```rust
while condition {
    ...
}
```

```rust
while let Some(value) = iterator.next() {
    ...
}
```

Và nhớ sự khác biệt:

```text
loop
    → break-driven

while
    → condition-driven

while let
    → pattern-driven
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
├── 12 — loop / break / continue
└── 13 — while / while let       ← DONE
```

## Buổi 14 — `for` & `Range`

Đây sẽ là buổi rất quan trọng vì chúng ta chuyển từ **manual loop** sang **iteration**:

```rust
for i in 0..10 {
    println!("{i}");
}
```

Chúng ta sẽ học:

* `for`
* `Range`
* `0..10`
* `0..=10`
* `rev()`
* `step_by()`
* iterate `Vec`
* iterate `String`
* iterate array
* `enumerate()`
* `zip()`
* `for` với references
* `for` + ownership
* `for` + `break`
* `for` + `continue`
* nested `for`
* loop labels
* mini project **Batch Story Processor**.
