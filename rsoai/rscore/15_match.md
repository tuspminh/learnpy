Đúng. Roadmap bạn đưa ra xác định **Buổi 15 = `match`**, nên phần trước tôi đã đi lệch roadmap. Ta quay lại đúng chương trình.

# Rust — Phần II: Control Flow

# Buổi 15 — `match`

`match` là một trong những tính năng quan trọng nhất của Rust. Nó không chỉ tương đương với `switch` trong một số ngôn ngữ khác, mà còn là nền tảng để làm việc với:

* `enum`
* `Option<T>`
* `Result<T, E>`
* pattern matching
* destructuring
* error handling
* state machine

Mục tiêu buổi này là hiểu `match` từ cơ bản đến mức có thể sử dụng trong code thực tế.

---

# 1. `match` là gì?

Cú pháp cơ bản:

```rust
match value {
    pattern1 => expression1,
    pattern2 => expression2,
    pattern3 => expression3,
}
```

Ví dụ:

```rust
fn main() {
    let number = 3;

    match number {
        1 => println!("One"),
        2 => println!("Two"),
        3 => println!("Three"),
        _ => println!("Other"),
    }
}
```

Chạy:

```bash
cargo run
```

Kết quả:

```text
Three
```

---

# 2. Mental model

Hãy nghĩ:

```text
value
  │
  ▼
 match
  │
  ├── pattern 1 ? → không
  ├── pattern 2 ? → không
  ├── pattern 3 ? → có
  │
  ▼
expression
```

Với:

```rust
let number = 3;
```

Rust kiểm tra:

```text
3 == 1 → false
3 == 2 → false
3 == 3 → true
```

Sau đó chạy:

```rust
println!("Three");
```

---

# 3. `_` là wildcard

Ví dụ:

```rust
fn main() {
    let number = 100;

    match number {
        1 => println!("One"),
        2 => println!("Two"),
        3 => println!("Three"),
        _ => println!("Other"),
    }
}
```

`_` có nghĩa:

> Bất kỳ giá trị nào khác.

Do đó:

```text
1 → One
2 → Two
3 → Three
100 → Other
```

---

# 4. `match` phải exhaustive

Đây là một nguyên tắc cực kỳ quan trọng.

Code:

```rust
fn main() {
    let number = 5;

    match number {
        1 => println!("One"),
        2 => println!("Two"),
    }
}
```

Rust không chấp nhận.

Tại sao?

Vì:

```text
i32
```

có rất nhiều giá trị:

```text
-2
-1
0
1
2
3
...
```

Bạn mới xử lý:

```text
1
2
```

nhưng chưa xử lý những giá trị còn lại.

Rust yêu cầu `match` phải **exhaustive**.

Sửa:

```rust
match number {
    1 => println!("One"),
    2 => println!("Two"),
    _ => println!("Other"),
}
```

---

# 5. Đây là điểm rất mạnh của Rust

Trong nhiều ngôn ngữ, programmer có thể quên xử lý một trường hợp.

Rust compiler cố gắng phát hiện điều đó.

Ví dụ với `enum`:

```rust
enum Direction {
    Up,
    Down,
    Left,
    Right,
}
```

Nếu:

```rust
match direction {
    Direction::Up => println!("Up"),
    Direction::Down => println!("Down"),
}
```

compiler biết rằng:

```text
Left
Right
```

chưa được xử lý.

Đây là một trong những lý do `match` rất phù hợp để xây dựng **state machine và domain model**.

---

# 6. `match` là expression

Điểm cực kỳ quan trọng:

> `match` không chỉ là statement. Nó là expression.

Ví dụ:

```rust
fn main() {
    let number = 3;

    let message = match number {
        1 => "one",
        2 => "two",
        3 => "three",
        _ => "other",
    };

    println!("{message}");
}
```

Ở đây:

```rust
match number { ... }
```

trả về một giá trị.

Có thể hình dung:

```text
match
  ↓
"three"
  ↓
message
```

---

# 7. Các branch phải trả kiểu tương thích

Code:

```rust
let message = match number {
    1 => "one",
    2 => "two",
    _ => "other",
};
```

Tất cả đều trả:

```text
&str
```

Nhưng:

```rust
let message = match number {
    1 => "one",
    2 => 100,
    _ => "other",
};
```

sẽ lỗi vì branch trả về những kiểu khác nhau.

```text
"one"  → &str
100    → integer
"other" → &str
```

Rust yêu cầu `match` expression có một kiểu kết quả phù hợp.

---

# 8. Block trong `match`

Mỗi arm có thể chứa nhiều câu lệnh:

```rust
fn main() {
    let number = 3;

    let result = match number {
        1 => {
            println!("Matched one");
            10
        }

        2 => {
            println!("Matched two");
            20
        }

        _ => {
            println!("Matched something else");
            0
        }
    };

    println!("result = {result}");
}
```

Output:

```text
Matched something else
result = 0
```

Chú ý:

```rust
{
    println!("...");
    0
}
```

Giá trị cuối cùng:

```rust
0
```

là giá trị của block.

---

# 9. Match nhiều giá trị

Bạn có thể dùng `|`.

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

`|` có nghĩa:

```text
OR
```

---

# 10. Range

Rust hỗ trợ range pattern.

```rust
fn main() {
    let age = 25;

    match age {
        0..=12 => println!("Child"),
        13..=17 => println!("Teenager"),
        18..=59 => println!("Adult"),
        60.. => println!("Senior"),
    }
}
```

Ở đây:

```rust
0..=12
```

nghĩa là:

```text
0 đến 12
```

Bao gồm cả `12`.

---

# 11. `..=` khác `..`

Trong pattern:

```rust
0..=10
```

nghĩa:

```text
0 <= x <= 10
```

Còn:

```rust
0..10
```

không phải cách bạn nên dùng để biểu diễn inclusive range trong pattern.

Trong `match`, hãy nhớ:

```text
..=
```

là range bao gồm điểm cuối.

---

# 12. Match với boolean

```rust
fn main() {
    let is_admin = true;

    match is_admin {
        true => println!("Admin"),
        false => println!("User"),
    }
}
```

Có thể viết:

```rust
let role = match is_admin {
    true => "admin",
    false => "user",
};

println!("{role}");
```

---

# 13. Match với `char`

```rust
fn main() {
    let c = 'a';

    match c {
        'a' | 'e' | 'i' | 'o' | 'u' => {
            println!("Vowel");
        }

        _ => {
            println!("Consonant");
        }
    }
}
```

---

# 14. Match với `String`

Ví dụ:

```rust
fn main() {
    let command = String::from("start");

    match command.as_str() {
        "start" => println!("Starting"),
        "stop" => println!("Stopping"),
        "pause" => println!("Pausing"),
        _ => println!("Unknown command"),
    }
}
```

Ở đây:

```rust
command.as_str()
```

chuyển sang:

```text
&str
```

để dễ match với string literals.

---

# 15. Match với `enum`

Đây mới là nơi `match` thực sự mạnh.

```rust
enum Direction {
    Up,
    Down,
    Left,
    Right,
}

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

Rust biết chính xác enum có bao nhiêu variant.

---

# 16. Enum + dữ liệu

Enum có thể chứa dữ liệu.

```rust
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
}
```

Match:

```rust
fn main() {
    let message = Message::Write(String::from("Hello"));

    match message {
        Message::Quit => {
            println!("Quit");
        }

        Message::Move { x, y } => {
            println!("Move: x={x}, y={y}");
        }

        Message::Write(text) => {
            println!("Write: {text}");
        }
    }
}
```

Đây chính là **pattern matching + destructuring**.

---

# 17. Destructuring

Trong:

```rust
Message::Move { x, y }
```

Rust lấy dữ liệu từ enum:

```text
Message::Move
       │
       ├── x
       └── y
```

và bind chúng vào:

```rust
x
y
```

Tương tự:

```rust
Message::Write(text)
```

lấy `String` bên trong và bind vào:

```rust
text
```

---

# 18. Match tuple

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

Đây là pattern matching.

---

# 19. `_` trong tuple

Ví dụ:

```rust
let point = (10, 20);

match point {
    (0, 0) => println!("Origin"),
    (0, _) => println!("Y axis"),
    (_, 0) => println!("X axis"),
    _ => println!("Normal point"),
}
```

`_` nghĩa:

> Tôi không quan tâm giá trị này.

---

# 20. Binding bằng pattern

Bạn có thể đặt tên cho dữ liệu:

```rust
fn main() {
    let number = 10;

    match number {
        0 => println!("Zero"),
        n => println!("Number = {n}"),
    }
}
```

Arm:

```rust
n => ...
```

match mọi giá trị và bind nó vào `n`.

Do đó:

```text
10
 ↓
n = 10
```

---

# 21. `@` binding

Rust có syntax nâng cao:

```rust
fn main() {
    let age = 25;

    match age {
        n @ 18..=60 => {
            println!("Adult age: {n}");
        }

        _ => {
            println!("Outside range");
        }
    }
}
```

`n @ 18..=60` nghĩa:

> Nếu giá trị nằm trong range này, bind chính giá trị đó vào `n`.

---

# 22. Match Guard

Match guard cho phép thêm điều kiện.

```rust
fn main() {
    let number = 10;

    match number {
        n if n > 0 => println!("Positive"),
        n if n < 0 => println!("Negative"),
        _ => println!("Zero"),
    }
}
```

Ở đây:

```rust
n if n > 0
```

nghĩa:

```text
match n
AND
n > 0
```

---

# 23. Match guard rất hữu ích

Ví dụ:

```rust
fn classify(number: i32) -> &'static str {
    match number {
        n if n < 0 => "negative",
        0 => "zero",
        n if n > 0 => "positive",
    }
}
```

Test:

```rust
fn main() {
    println!("{}", classify(-10));
    println!("{}", classify(0));
    println!("{}", classify(20));
}
```

Output:

```text
negative
zero
positive
```

---

# 24. Match với `Option<T>`

Đây là kiến thức cực kỳ quan trọng.

Rust không có:

```text
null
```

theo kiểu truyền thống.

Thay vào đó thường dùng:

```rust
Option<T>
```

Ví dụ:

```rust
let value: Option<i32> = Some(10);
```

`Option` có hai variant:

```text
Some(value)
None
```

Match:

```rust
fn main() {
    let value: Option<i32> = Some(10);

    match value {
        Some(number) => println!("Value = {number}"),
        None => println!("No value"),
    }
}
```

---

# 25. Vì sao `Option` + `match` rất mạnh?

Bạn bắt buộc phải xử lý:

```text
Some
None
```

Ví dụ:

```rust
fn get_username(id: u32) -> Option<String> {
    if id == 1 {
        Some(String::from("alice"))
    } else {
        None
    }
}
```

Sử dụng:

```rust
fn main() {
    let username = get_username(1);

    match username {
        Some(name) => println!("User: {name}"),
        None => println!("User not found"),
    }
}
```

---

# 26. `Result<T, E>`

Một enum quan trọng khác:

```text
Result<T, E>
```

có:

```text
Ok(T)
Err(E)
```

Ví dụ:

```rust
fn divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 {
        Err(String::from("Cannot divide by zero"))
    } else {
        Ok(a / b)
    }
}
```

Match:

```rust
fn main() {
    match divide(10.0, 2.0) {
        Ok(result) => println!("Result = {result}"),
        Err(error) => println!("Error: {error}"),
    }
}
```

---

# 27. Đây là nền tảng Error Handling

Sau này khi làm:

```text
File I/O
Database
HTTP
JSON
CLI
Crawler
Repository
```

bạn sẽ gặp:

```rust
Result<T, E>
```

rất thường xuyên.

Ví dụ:

```rust
match std::fs::read_to_string("data.txt") {
    Ok(content) => println!("{content}"),
    Err(error) => println!("Failed: {error}"),
}
```

---

# 28. Match lồng nhau

Bạn có thể viết:

```rust
enum Status {
    Success,
    Failed,
}

fn main() {
    let status = Status::Success;

    match status {
        Status::Success => {
            println!("Success");
        }

        Status::Failed => {
            println!("Failed");
        }
    }
}
```

Nhưng trong code thực tế, cố gắng tránh nesting quá sâu.

Sau này:

```text
if let
while let
?
```

sẽ giúp code gọn hơn trong những trường hợp phù hợp.

---

# 29. Match với reference

Ví dụ:

```rust
fn main() {
    let number = 10;
    let reference = &number;

    match reference {
        &10 => println!("Ten"),
        &n => println!("Other: {n}"),
    }
}
```

Tuy nhiên trong Rust hiện đại, bạn sẽ thường gặp pattern matching ergonomics giúp giảm nhu cầu viết `&` thủ công trong nhiều tình huống.

Ví dụ với `Option`:

```rust
fn main() {
    let value = Some(10);

    match &value {
        Some(number) => println!("Value = {number}"),
        None => println!("None"),
    }

    println!("{value:?}");
}
```

Điểm quan trọng là phải chú ý:

```text
match value
```

và:

```text
match &value
```

có thể tạo ra hành vi ownership khác nhau.

---

# 30. Match và ownership

Đây là phần rất quan trọng để chuẩn bị cho Ownership sau này.

Ví dụ:

```rust
fn main() {
    let value = Some(String::from("hello"));

    match value {
        Some(text) => println!("{text}"),
        None => println!("None"),
    }
}
```

`value` có thể bị consume tùy cách pattern sử dụng nó.

Nếu cần giữ lại:

```rust
fn main() {
    let value = Some(String::from("hello"));

    match &value {
        Some(text) => println!("{text}"),
        None => println!("None"),
    }

    println!("{value:?}");
}
```

Ở đây chúng ta match trên reference:

```rust
&value
```

thay vì consume `value`.

---

# 31. Match nhiều pattern

```rust
fn main() {
    let day = 6;

    match day {
        1 | 2 | 3 | 4 | 5 => println!("Weekday"),
        6 | 7 => println!("Weekend"),
        _ => println!("Invalid"),
    }
}
```

---

# 32. Match range + guard

Có thể kết hợp:

```rust
fn main() {
    let age = 25;

    match age {
        0..=17 => println!("Minor"),
        18..=60 => println!("Adult"),
        61..=120 => println!("Senior"),
        _ => println!("Invalid"),
    }
}
```

---

# 33. `match` thay thế nhiều `if`

Ví dụ:

```rust
let status = "pending";

if status == "pending" {
    println!("Waiting");
} else if status == "running" {
    println!("Running");
} else if status == "done" {
    println!("Done");
} else {
    println!("Unknown");
}
```

Có thể viết:

```rust
match status {
    "pending" => println!("Waiting"),
    "running" => println!("Running"),
    "done" => println!("Done"),
    _ => println!("Unknown"),
}
```

Rất rõ ràng khi có nhiều trường hợp rời rạc.

---

# 34. Match trong ứng dụng CLI

Điều này đặc biệt phù hợp với những CLI bạn đang học.

Ví dụ:

```rust
enum Command {
    Crawl,
    List,
    Read,
    Exit,
}
```

Xử lý:

```rust
fn execute(command: Command) {
    match command {
        Command::Crawl => {
            println!("Start crawling...");
        }

        Command::List => {
            println!("List stories...");
        }

        Command::Read => {
            println!("Read story...");
        }

        Command::Exit => {
            println!("Bye!");
        }
    }
}
```

Khi thêm:

```rust
Delete
```

compiler có thể giúp bạn tìm tất cả những `match` cần cập nhật.

Đây là một lợi ích rất lớn khi thiết kế domain bằng enum.

---

# 35. Ví dụ hoàn chỉnh — Story Status

Hãy xây một mô hình gần với project crawler của bạn:

```rust
#[derive(Debug)]
enum StoryStatus {
    Pending,
    Crawling,
    Completed,
    Failed,
}
```

Function:

```rust
fn status_message(status: StoryStatus) -> &'static str {
    match status {
        StoryStatus::Pending => "Waiting to crawl",
        StoryStatus::Crawling => "Currently crawling",
        StoryStatus::Completed => "Crawl completed",
        StoryStatus::Failed => "Crawl failed",
    }
}
```

`main`:

```rust
fn main() {
    let status = StoryStatus::Crawling;

    let message = status_message(status);

    println!("{message}");
}
```

Output:

```text
Currently crawling
```

---

# 36. Story Status nâng cao

Thêm dữ liệu:

```rust
#[derive(Debug)]
enum StoryStatus {
    Pending,
    Crawling { chapter: u32 },
    Completed { chapters: u32 },
    Failed { reason: String },
}
```

Function:

```rust
fn describe(status: &StoryStatus) {
    match status {
        StoryStatus::Pending => {
            println!("Waiting...");
        }

        StoryStatus::Crawling { chapter } => {
            println!("Crawling chapter {chapter}");
        }

        StoryStatus::Completed { chapters } => {
            println!("Completed: {chapters} chapters");
        }

        StoryStatus::Failed { reason } => {
            println!("Failed: {reason}");
        }
    }
}
```

Test:

```rust
fn main() {
    let status = StoryStatus::Crawling {
        chapter: 42,
    };

    describe(&status);
}
```

Output:

```text
Crawling chapter 42
```

Đây đã là một mô hình khá gần với application architecture thực tế.

---

# 37. Complete Lab

Tạo project:

```bash
cargo new match_lab
cd match_lab
```

Thay `src/main.rs`:

```rust
#[derive(Debug)]
enum CrawlStatus {
    Pending,
    Crawling { chapter: u32 },
    Completed { chapters: u32 },
    Failed { reason: String },
}

fn describe(status: &CrawlStatus) -> String {
    match status {
        CrawlStatus::Pending => {
            String::from("Waiting to crawl")
        }

        CrawlStatus::Crawling { chapter } => {
            format!("Crawling chapter {chapter}")
        }

        CrawlStatus::Completed { chapters } => {
            format!("Completed: {chapters} chapters")
        }

        CrawlStatus::Failed { reason } => {
            format!("Failed: {reason}")
        }
    }
}

fn main() {
    let statuses = vec![
        CrawlStatus::Pending,

        CrawlStatus::Crawling {
            chapter: 10,
        },

        CrawlStatus::Completed {
            chapters: 100,
        },

        CrawlStatus::Failed {
            reason: String::from("Network error"),
        },
    ];

    for status in &statuses {
        println!("{status:?}");
        println!("{}", describe(status));
        println!();
    }
}
```

Chạy:

```bash
cargo run
```

Bạn sẽ nhận được output tương tự:

```text
Pending
Waiting to crawl

Crawling { chapter: 10 }
Crawling chapter 10

Completed { chapters: 100 }
Completed: 100 chapters

Failed { reason: "Network error" }
Failed: Network error
```

---

# 38. Tại sao tôi dùng `&CrawlStatus`?

Function:

```rust
fn describe(status: &CrawlStatus)
```

thay vì:

```rust
fn describe(status: CrawlStatus)
```

là một chủ đề liên quan tới **borrowing**.

Ở thời điểm này bạn chưa cần đi sâu, chỉ cần nhận ra:

```rust
&status
```

cho phép function quan sát dữ liệu mà không lấy ownership.

Chúng ta sẽ học kỹ phần này trong phần Ownership/Borrowing.

---

# 39. Bài tập thực hành

## Bài 1 — Number classifier

Viết:

```rust
fn classify(number: i32) -> &'static str
```

Kết quả:

```text
negative
zero
small positive
large positive
```

Quy tắc:

```text
< 0       → negative
0         → zero
1..=10    → small positive
11..      → large positive
```

---

## Bài 2 — Traffic light

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
Yellow → Slow down
Green  → Go
```

---

# 40. Bài 3 — `Option`

Viết:

```rust
fn find_story(id: u32) -> Option<String>
```

Nếu:

```text
id == 1
```

trả:

```rust
Some(String::from("Rust Book"))
```

ngược lại:

```rust
None
```

Trong `main`, dùng `match` để in:

```text
Found: Rust Book
```

hoặc:

```text
Story not found
```

---

# 41. Bài 4 — `Result`

Viết:

```rust
fn divide(a: i32, b: i32) -> Result<i32, String>
```

Nếu:

```text
b == 0
```

trả:

```rust
Err(...)
```

ngược lại:

```rust
Ok(...)
```

Dùng `match` để xử lý cả hai trường hợp.

---

# 42. Bài 5 — Story crawler

Tạo:

```rust
enum CrawlResult {
    Success {
        chapters: u32,
    },

    Failed {
        error: String,
    },

    Skipped {
        reason: String,
    },
}
```

Viết:

```rust
fn report(result: &CrawlResult)
```

Output:

```text
Success: 100 chapters
Failed: timeout
Skipped: already up to date
```

---

# 43. Bài 6 — Mini state machine

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
fn next_state(state: State) -> State
```

Thiết kế:

```text
Idle    → Running
Running → Paused
Paused  → Running
Stopped → Stopped
```

Đây là bài rất quan trọng vì `match` thường được dùng để xây dựng **state machine**.

---

# 44. Những lỗi cần tránh

### Lỗi 1 — Quên exhaustive

```rust
match number {
    1 => ...
}
```

Phải có:

```rust
_ => ...
```

hoặc xử lý đầy đủ các pattern.

---

### Lỗi 2 — Lạm dụng `_`

Không nên lúc nào cũng:

```rust
match status {
    _ => ...
}
```

Nếu enum có các trạng thái quan trọng:

```text
Pending
Running
Completed
Failed
```

hãy match rõ từng variant.

Compiler sẽ giúp bạn khi enum thay đổi.

---

### Lỗi 3 — Nhầm `match` với `switch`

`match` mạnh hơn `switch` rất nhiều.

Nó hỗ trợ:

```text
literal
range
enum
tuple
struct
Option
Result
destructuring
guards
binding
nested patterns
```

---

# 45. Tư duy chuyên nghiệp

Khi thiết kế Rust code, hãy bắt đầu suy nghĩ:

```text
Có bao nhiêu trạng thái?
```

Nếu câu trả lời là:

```text
Pending
Running
Completed
Failed
```

thì cân nhắc:

```rust
enum
```

sau đó:

```rust
match
```

Thay vì tạo:

```text
status = 1
status = 2
status = 3
status = 4
```

Rust khuyến khích mô hình hóa domain một cách rõ ràng.

---

# 46. Tổng kết Buổi 15

Bạn cần nắm chắc các khái niệm:

```text
match
│
├── arm
├── pattern
├── exhaustive
├── _
├── |
├── range
├── binding
├── @
├── guard
├── destructuring
├── enum
├── Option<T>
└── Result<T, E>
```

Đặc biệt ghi nhớ:

> **`match` là expression và phải exhaustive.**

Và:

> **`enum` + `match` là một trong những cặp công cụ quan trọng nhất để thiết kế domain trong Rust.**

### Roadmap tiếp theo

```text
Buổi 15  → match              ← hôm nay
Buổi 16  → if let
Buổi 17  → while let
Buổi 18  → break & continue
Buổi 19  → Labels
Buổi 20  → Mini Project
```

**Buổi 16 sẽ đi sâu vào `if let`**, đặc biệt là cách dùng `if let` với `Option`, `Result` và enum để thay thế những `match` đơn giản mà không làm mất đi sức mạnh của pattern matching.
