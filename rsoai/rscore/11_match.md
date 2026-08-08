# Rust Professional 2026 — Buổi 11

## `match` & Pattern Matching

Buổi 11 là một **cột mốc quan trọng** trong quá trình học Rust.

Nếu `if` giúp bạn tư duy:

```text
điều kiện → đúng / sai
```

thì `match` giúp bạn tư duy:

```text
giá trị → pattern nào phù hợp?
```

Đây chính là nền tảng để sau này học rất sâu về:

* `enum`
* `Option<T>`
* `Result<T, E>`
* Error Handling
* State Machine
* Parser
* CLI
* Protocol
* Rust idiomatic code

---

# 1. `match` là gì?

Cú pháp cơ bản:

```rust
match value {
    pattern1 => expression1,
    pattern2 => expression2,
    pattern3 => expression3,
    _ => expression_default,
}
```

Ví dụ:

```rust
fn main() {
    let number = 2;

    match number {
        1 => println!("One"),
        2 => println!("Two"),
        3 => println!("Three"),
        _ => println!("Other"),
    }
}
```

Output:

```text
Two
```

---

# 2. Tư duy của `match`

Với:

```rust
let number = 2;
```

Rust kiểm tra:

```text
number
  │
  ├── 1 ? → No
  ├── 2 ? → YES
  │
  └── dừng
```

Nó chọn **pattern đầu tiên khớp**.

---

# 3. `match` là expression

Giống `if`, `match` có thể trả về giá trị.

```rust
fn main() {
    let number = 2;

    let name = match number {
        1 => "One",
        2 => "Two",
        3 => "Three",
        _ => "Other",
    };

    println!("{name}");
}
```

Output:

```text
Two
```

Đây là một pattern cực kỳ quan trọng:

```rust
let result = match value {
    pattern => value,
    _ => value,
};
```

---

# 4. `match` phải exhaustive

Đây là một đặc điểm cực kỳ quan trọng của Rust.

Bạn **không thể** viết:

```rust
let number = 10;

match number {
    1 => println!("One"),
    2 => println!("Two"),
}
```

Vì `number` có thể là:

```text
3
4
5
...
```

Rust yêu cầu bạn xử lý tất cả khả năng.

---

# 5. `_` — wildcard

Để xử lý phần còn lại:

```rust
match number {
    1 => println!("One"),
    2 => println!("Two"),
    _ => println!("Other"),
}
```

`_` có nghĩa:

> Bất kỳ giá trị nào còn lại.

---

# 6. `_` không bind giá trị

Ví dụ:

```rust
match number {
    1 => println!("One"),
    _ => println!("Something else"),
}
```

`_` chỉ dùng để nói:

```text
tôi không quan tâm giá trị cụ thể là gì
```

Nếu bạn muốn lấy giá trị đó, dùng biến:

```rust
match number {
    1 => println!("One"),
    other => println!("Other: {other}"),
}
```

Ví dụ `number = 10`:

```text
Other: 10
```

---

# 7. Pattern binding

```rust
fn main() {
    let number = 100;

    match number {
        0 => println!("Zero"),
        value => println!("Value = {value}"),
    }
}
```

`value` là một pattern binding.

Nó nhận giá trị:

```text
value = 100
```

---

# 8. `_` vs variable pattern

Hai cái này rất khác nhau:

```rust
_
```

nghĩa:

```text
tôi không cần giá trị
```

Trong khi:

```rust
value
```

nghĩa:

```text
hãy bind giá trị vào biến value
```

---

# 9. Nhiều pattern cùng một branch

Rust cho phép:

```rust
fn main() {
    let number = 2;

    match number {
        1 | 2 | 3 => println!("Small"),
        4 | 5 | 6 => println!("Medium"),
        _ => println!("Large"),
    }
}
```

Output:

```text
Small
```

Toán tử:

```rust
|
```

ở đây có nghĩa:

> hoặc pattern này.

---

# 10. Range Pattern

Rust cho phép range pattern.

```rust
fn main() {
    let number = 7;

    match number {
        1..=5 => println!("1 to 5"),
        6..=10 => println!("6 to 10"),
        _ => println!("Other"),
    }
}
```

Output:

```text
6 to 10
```

Lưu ý:

```rust
1..=5
```

bao gồm `5`.

---

# 11. Match nhiều khoảng

Ví dụ grade:

```rust
fn grade(score: u8) -> &'static str {
    match score {
        90..=100 => "A",
        80..=89 => "B",
        70..=79 => "C",
        60..=69 => "D",
        _ => "F",
    }
}

fn main() {
    println!("{}", grade(85));
}
```

Output:

```text
B
```

---

# 12. Guard với `if`

Rust cho phép pattern có thêm điều kiện:

```rust
match number {
    x if x > 0 => println!("Positive"),
    x if x < 0 => println!("Negative"),
    _ => println!("Zero"),
}
```

Ví dụ hoàn chỉnh:

```rust
fn main() {
    let number = -10;

    match number {
        x if x > 0 => println!("Positive"),
        x if x < 0 => println!("Negative"),
        _ => println!("Zero"),
    }
}
```

Output:

```text
Negative
```

---

# 13. `match` với `bool`

```rust
fn main() {
    let active = true;

    match active {
        true => println!("Active"),
        false => println!("Inactive"),
    }
}
```

Có thể viết ngắn hơn:

```rust
if active {
    println!("Active");
}
```

Vì vậy không phải lúc nào cũng nên dùng `match`.

---

# 14. Khi nào dùng `if`, khi nào dùng `match`?

### `if`

Phù hợp với:

```text
boolean condition
```

Ví dụ:

```rust
if age >= 18 {
    ...
}
```

### `match`

Phù hợp với:

```text
nhiều pattern
```

Ví dụ:

```rust
match command {
    "start" => ...,
    "stop" => ...,
    "pause" => ...,
    _ => ...,
}
```

---

# 15. `match` rất mạnh với enum

Đây là nơi `match` bắt đầu trở nên thực sự quan trọng.

Ví dụ:

```rust
enum Direction {
    Up,
    Down,
    Left,
    Right,
}
```

Sau đó:

```rust
fn main() {
    let direction = Direction::Up;

    match direction {
        Direction::Up => println!("Going up"),
        Direction::Down => println!("Going down"),
        Direction::Left => println!("Going left"),
        Direction::Right => println!("Going right"),
    }
}
```

Output:

```text
Going up
```

---

# 16. Exhaustiveness với enum

Điểm rất hay:

```rust
enum Direction {
    Up,
    Down,
    Left,
    Right,
}
```

Nếu bạn viết:

```rust
match direction {
    Direction::Up => println!("Up"),
}
```

Rust báo lỗi.

Vì còn:

```text
Down
Left
Right
```

Rust compiler bắt bạn xử lý đầy đủ.

Đây là một trong những sức mạnh lớn nhất của Rust.

---

# 17. Không nhất thiết cần `_`

Với enum:

```rust
match direction {
    Direction::Up => println!("Up"),
    Direction::Down => println!("Down"),
    Direction::Left => println!("Left"),
    Direction::Right => println!("Right"),
}
```

Đây thường tốt hơn:

```rust
match direction {
    Direction::Up => println!("Up"),
    Direction::Down => println!("Down"),
    Direction::Left => println!("Left"),
    _ => println!("Other"),
}
```

Vì nếu sau này thêm:

```rust
Diagonal
```

compiler sẽ báo cho bạn biết những nơi cần cập nhật.

Đây là **safety by compiler**.

---

# 18. `match` trả về value với enum

```rust
enum Direction {
    Up,
    Down,
    Left,
    Right,
}

fn direction_name(direction: Direction) -> &'static str {
    match direction {
        Direction::Up => "Up",
        Direction::Down => "Down",
        Direction::Left => "Left",
        Direction::Right => "Right",
    }
}

fn main() {
    let direction = Direction::Left;

    println!("{}", direction_name(direction));
}
```

---

# 19. Enum có dữ liệu

Rust enum không chỉ chứa giá trị đơn giản.

Ví dụ:

```rust
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
}
```

Đây là một điểm cực kỳ mạnh của Rust.

`Message` có thể có nhiều dạng dữ liệu khác nhau.

---

# 20. Match enum có dữ liệu

```rust
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
}

fn main() {
    let message = Message::Move {
        x: 10,
        y: 20,
    };

    match message {
        Message::Quit => {
            println!("Quit");
        }

        Message::Move { x, y } => {
            println!("Move to ({x}, {y})");
        }

        Message::Write(text) => {
            println!("Message: {text}");
        }
    }
}
```

Output:

```text
Move to (10, 20)
```

---

# 21. Đây là Pattern Matching thực sự

Ở đây:

```rust
Message::Move { x, y }
```

không chỉ kiểm tra loại.

Nó còn **destructure** dữ liệu:

```text
Message::Move {
    x: 10,
    y: 20
}

        ↓

x = 10
y = 20
```

---

# 22. Destructuring tuple

Pattern matching không chỉ dành cho enum.

Ví dụ:

```rust
fn main() {
    let point = (10, 20);

    match point {
        (0, 0) => println!("Origin"),
        (0, y) => println!("On Y axis: {y}"),
        (x, 0) => println!("On X axis: {x}"),
        (x, y) => println!("Point: ({x}, {y})"),
    }
}
```

Nếu:

```text
point = (10, 20)
```

Output:

```text
Point: (10, 20)
```

---

# 23. Pattern matching rất mạnh

Bạn có thể hình dung:

```text
match
│
├── literal
│   └── 10
│
├── variable
│   └── x
│
├── wildcard
│   └── _
│
├── multiple pattern
│   └── 1 | 2 | 3
│
├── range
│   └── 1..=10
│
├── tuple
│   └── (x, y)
│
└── enum
    └── Message::Move { x, y }
```

Đây là nền móng cho pattern matching của Rust.

---

# 24. `Option<T>`

Bây giờ chúng ta gặp một type cực kỳ quan trọng.

Rust không có `null` theo cách truyền thống.

Thay vào đó có:

```rust
enum Option<T> {
    Some(T),
    None,
}
```

Về mặt ý tưởng:

```text
Option<T>
│
├── Some(value)
│
└── None
```

---

# 25. Match với `Option`

```rust
fn main() {
    let number = Some(10);

    match number {
        Some(value) => println!("Value: {value}"),
        None => println!("No value"),
    }
}
```

Output:

```text
Value: 10
```

---

# 26. `None`

```rust
fn main() {
    let number: Option<i32> = None;

    match number {
        Some(value) => println!("Value: {value}"),
        None => println!("No value"),
    }
}
```

Output:

```text
No value
```

---

# 27. Vì sao `Option` quan trọng?

Ví dụ một hàm tìm kiếm:

```rust
fn find_user(id: u32) -> Option<&'static str> {
    if id == 1 {
        Some("Alice")
    } else {
        None
    }
}
```

Không tìm thấy:

```text
None
```

Tìm thấy:

```text
Some("Alice")
```

Không cần:

```text
null
```

và giảm rất nhiều lỗi null reference.

---

# 28. Match kết quả của function

```rust
fn find_user(id: u32) -> Option<&'static str> {
    if id == 1 {
        Some("Alice")
    } else {
        None
    }
}

fn main() {
    let result = find_user(1);

    match result {
        Some(name) => println!("Found: {name}"),
        None => println!("User not found"),
    }
}
```

---

# 29. `if let` vs `match`

Nếu bạn cần cả hai trường hợp:

```rust
match result {
    Some(name) => println!("Found: {name}"),
    None => println!("Not found"),
}
```

Nếu chỉ quan tâm `Some`:

```rust
if let Some(name) = result {
    println!("Found: {name}");
}
```

Tư duy:

```text
match
→ xử lý nhiều pattern

if let
→ quan tâm một pattern
```

---

# 30. `match` với `Option` và biến đổi value

```rust
fn double(value: Option<i32>) -> Option<i32> {
    match value {
        Some(number) => Some(number * 2),
        None => None,
    }
}

fn main() {
    println!("{:?}", double(Some(10)));
    println!("{:?}", double(None));
}
```

Output:

```text
Some(20)
None
```

Đây là tư duy rất quan trọng sau này khi học:

```text
Option
Result
map
and_then
?
```

---

# 31. Match với String slice

```rust
fn main() {
    let command = "start";

    match command {
        "start" => println!("Starting..."),
        "stop" => println!("Stopping..."),
        "pause" => println!("Paused"),
        _ => println!("Unknown command"),
    }
}
```

Đây là pattern cực kỳ phù hợp để xây CLI.

---

# 32. Mini Project — Command Parser

Chúng ta xây một parser đơn giản.

```rust
enum Command {
    Start,
    Stop,
    Pause,
    Unknown,
}

fn parse_command(input: &str) -> Command {
    match input {
        "start" => Command::Start,
        "stop" => Command::Stop,
        "pause" => Command::Pause,
        _ => Command::Unknown,
    }
}

fn execute(command: Command) {
    match command {
        Command::Start => println!("Starting application..."),
        Command::Stop => println!("Stopping application..."),
        Command::Pause => println!("Pausing application..."),
        Command::Unknown => println!("Unknown command."),
    }
}

fn main() {
    let input = "start";

    let command = parse_command(input);

    execute(command);
}
```

Output:

```text
Starting application...
```

---

# 33. Phân tích kiến trúc

Chúng ta đang có:

```text
input
  │
  ▼
parse_command()
  │
  ▼
Command enum
  │
  ▼
execute()
```

Đây là tư duy kiến trúc rất quan trọng.

Thay vì:

```rust
if input == "start" {
    ...
} else if input == "stop" {
    ...
}
```

chúng ta chuyển:

```text
String
 ↓
Domain enum
 ↓
Business logic
```

Đây là hướng tư duy sẽ cực kỳ hữu ích khi bạn xây CLI và framework Rust sau này.

---

# 34. Enum giúp loại bỏ "magic string"

Thay vì khắp chương trình:

```rust
"start"
"stop"
"pause"
```

sau khi parse, chúng ta có:

```rust
Command::Start
Command::Stop
Command::Pause
```

Compiler có thể kiểm tra chúng.

---

# 35. Match và compiler safety

Giả sử:

```rust
enum Command {
    Start,
    Stop,
    Pause,
}
```

Sau này thêm:

```rust
enum Command {
    Start,
    Stop,
    Pause,
    Restart,
}
```

Compiler có thể chỉ ra các `match` chưa xử lý:

```rust
Restart
```

Đây là một ưu điểm cực lớn khi ứng dụng phát triển.

---

# 36. Mini Project — Traffic Light

```rust
enum TrafficLight {
    Red,
    Yellow,
    Green,
}

fn action(light: TrafficLight) -> &'static str {
    match light {
        TrafficLight::Red => "Stop",
        TrafficLight::Yellow => "Prepare",
        TrafficLight::Green => "Go",
    }
}

fn main() {
    let light = TrafficLight::Green;

    println!("{}", action(light));
}
```

Output:

```text
Go
```

---

# 37. Match với nhiều pattern

Ví dụ:

```rust
fn classify(number: i32) -> &'static str {
    match number {
        0 => "zero",
        1 | 2 | 3 => "small",
        4..=10 => "medium",
        _ => "large",
    }
}

fn main() {
    println!("{}", classify(7));
}
```

Output:

```text
medium
```

---

# 38. Match Guard

Ví dụ:

```rust
fn classify(number: i32) -> &'static str {
    match number {
        x if x < 0 => "negative",
        0 => "zero",
        x if x > 100 => "very large",
        _ => "normal",
    }
}
```

Ở đây:

```rust
x if x < 0
```

nghĩa:

```text
match x
AND
x < 0
```

---

# 39. Một lỗi tư duy phổ biến

Đừng biến mọi `if` thành `match`.

Ví dụ:

```rust
if age >= 18 {
    println!("Adult");
}
```

Không cần:

```rust
match age {
    x if x >= 18 => println!("Adult"),
    _ => {}
}
```

Code sau dài hơn và khó đọc hơn.

Hãy dùng:

```text
if
→ boolean logic

match
→ pattern matching
```

---

# 40. Mini Project hoàn chỉnh — Command Dispatcher

Tạo:

```bash
cargo new command_dispatcher
cd command_dispatcher
```

`src/main.rs`:

```rust
#[derive(Debug)]
enum Command {
    Start,
    Stop,
    Pause,
    Status,
    Unknown,
}

fn parse_command(input: &str) -> Command {
    match input {
        "start" => Command::Start,
        "stop" => Command::Stop,
        "pause" => Command::Pause,
        "status" => Command::Status,
        _ => Command::Unknown,
    }
}

fn execute(command: Command) {
    match command {
        Command::Start => {
            println!("Application started.");
        }

        Command::Stop => {
            println!("Application stopped.");
        }

        Command::Pause => {
            println!("Application paused.");
        }

        Command::Status => {
            println!("Application is running.");
        }

        Command::Unknown => {
            println!("Unknown command.");
        }
    }
}

fn main() {
    let input = "status";

    let command = parse_command(input);

    println!("Command: {command:?}");

    execute(command);
}
```

Chạy:

```bash
cargo run
```

Output:

```text
Command: Status
Application is running.
```

---

# 41. Tại sao dùng `#[derive(Debug)]`?

Enum:

```rust
Command
```

không mặc định hỗ trợ:

```rust
println!("{:?}", command);
```

Thêm:

```rust
#[derive(Debug)]
```

Rust tự sinh implementation cần thiết cho debug formatting.

Chúng ta sẽ học `derive` rất kỹ ở phần Struct/Traits.

---

# 42. Bài tập 1 — Number Classifier

Viết:

```rust
fn classify(number: i32) -> &'static str
```

Quy tắc:

```text
0          → Zero
1..=10     → Small
11..=100   → Medium
101..      → Large
negative   → Negative
```

Sử dụng `match`.

---

# 43. Bài tập 2 — Day

Tạo:

```rust
enum Day {
    Monday,
    Tuesday,
    Wednesday,
    Thursday,
    Friday,
    Saturday,
    Sunday,
}
```

Viết:

```rust
fn is_weekend(day: Day) -> bool
```

Kết quả:

```text
Saturday → true
Sunday   → true
others   → false
```

---

# 44. Bài tập 3 — Traffic Light

Tạo:

```rust
enum TrafficLight {
    Red,
    Yellow,
    Green,
}
```

Viết:

```rust
fn action(light: TrafficLight) -> &'static str
```

Kết quả:

```text
Red    → Stop
Yellow → Prepare
Green  → Go
```

---

# 45. Bài tập 4 — `Option`

Viết:

```rust
fn print_value(value: Option<i32>)
```

Nếu:

```rust
Some(100)
```

in:

```text
Value: 100
```

Nếu:

```rust
None
```

in:

```text
No value
```

Bắt buộc dùng `match`.

---

# 46. Bài tập 5 — Tuple Pattern

Cho:

```rust
let point = (10, 0);
```

Viết `match` để phân loại:

```text
(0, 0) → Origin
(x, 0) → X axis
(0, y) → Y axis
(x, y) → Other
```

---

# 47. Bài tập 6 — Command Parser

Tạo:

```rust
enum Command {
    Start,
    Stop,
    Restart,
    Status,
    Unknown,
}
```

Viết:

```rust
fn parse_command(input: &str) -> Command
```

Xử lý:

```text
"start"
"stop"
"restart"
"status"
```

---

# 48. Bài tập 7 — Command Executor

Viết:

```rust
fn execute(command: Command)
```

Kết quả:

```text
Start   → Starting...
Stop    → Stopping...
Restart → Restarting...
Status  → Running...
Unknown → Unknown command
```

---

# 49. Bài tập 8 — Mini Project

## User Role System

Tạo:

```rust
enum Role {
    Admin,
    Moderator,
    User,
    Guest,
}
```

Viết:

```rust
fn permissions(role: Role) -> &'static str
```

Quy tắc:

```text
Admin     → "read write delete"
Moderator → "read write"
User      → "read"
Guest     → "none"
```

Sau đó viết:

```rust
fn can_delete(role: Role) -> bool
```

Chỉ:

```text
Admin → true
```

các role khác:

```text
false
```

---

# 50. Bài tập 9 — State Machine

Đây là bài quan trọng.

Tạo:

```rust
enum State {
    Idle,
    Running,
    Paused,
    Stopped,
}
```

Viết:

```rust
fn describe(state: State) -> &'static str
```

và:

```rust
fn can_start(state: State) -> bool
```

Quy tắc:

```text
Idle     → true
Stopped  → true
Running  → false
Paused   → false
```

Đây chính là nền tảng để sau này bạn xây:

```text
Crawler
Worker
Task Manager
Download Manager
CLI Application
```

---

# 51. Bài tập Deep Dive

Không chạy ngay. Hãy dự đoán:

```rust
fn main() {
    let number = 5;

    let result = match number {
        0 => "zero",
        1 | 2 | 3 => "small",
        4..=10 => "medium",
        x if x > 100 => "large",
        _ => "other",
    };

    println!("{result}");
}
```

Đáp án:

```text
medium
```

Vì:

```text
5
↓
0?              No
1 | 2 | 3?      No
4..=10?         YES
```

`match` dừng tại đó.

---

# 52. So sánh `if` và `match`

| Tình huống            | Nên dùng           |
| --------------------- | ------------------ |
| `age >= 18`           | `if`               |
| `is_admin && active`  | `if`               |
| Nhiều giá trị cụ thể  | `match`            |
| Enum                  | `match`            |
| `Option`              | `match` / `if let` |
| Pattern destructuring | `match`            |
| Boolean đơn giản      | `if`               |
| State machine         | `match`            |

---

# 53. Tư duy quan trọng nhất của Buổi 11

Đừng học `match` như:

> Một phiên bản `switch` của Rust.

Cách hiểu này **quá nông**.

Hãy hiểu:

```text
match
=
Pattern Matching
```

Nó có thể:

```text
match
├── giá trị
├── enum
├── tuple
├── Option
├── Result
├── range
├── nhiều pattern
├── destructuring
└── guard
```

Đây là một trong những tính năng làm Rust khác biệt rất rõ so với nhiều ngôn ngữ khác.

---

# 54. Kiến thức cần thuộc sau Buổi 11

Bạn cần thực sự hiểu:

```rust
match value {
    pattern => expression,
    _ => expression,
}
```

và các pattern:

```rust
1
"start"
1 | 2 | 3
1..=10
x
_
Some(x)
None
(x, y)
Enum::Variant
Enum::Variant { x, y }
```

Đồng thời phải hiểu:

```text
match
    ↓
exhaustive
    ↓
compiler kiểm tra
    ↓
pattern matching
```

---

# 55. Roadmap hiện tại

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
├── Buổi 10 — if / else / else if
└── Buổi 11 — match & Pattern Matching  ← DONE
```

## Buổi 12 — `loop`

Chúng ta sẽ chuyển sang **Iteration & Loop Control**:

```rust
loop {
    ...
}
```

và đi sâu vào:

* `loop`
* infinite loop
* `break`
* `continue`
* `break value`
* `loop` trả về giá trị
* nested loop
* label cho loop
* `'outer: loop`
* `break 'outer`
* `continue 'outer`
* xây dựng menu CLI bằng `loop`
* mini project **Interactive CLI Menu**

Đặc biệt, chúng ta sẽ khám phá một điểm rất Rust:

```rust
let result = loop {
    ...
    break value;
};
```

Tức là **`loop` cũng là expression có thể trả về giá trị**, nối tiếp trực tiếp tư duy expression-oriented mà chúng ta vừa học ở `if` và `match`.
