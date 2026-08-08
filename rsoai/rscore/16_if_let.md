# Rust — Phần II: Control Flow

# Buổi 16 — `if let`

Hôm nay chúng ta học **`if let`**.

Đây là cú pháp rất quan trọng vì nó kết hợp:

```text
if
+
pattern matching
```

`if let` đặc biệt hữu ích khi bạn chỉ quan tâm **một pattern cụ thể**, thay vì phải viết đầy đủ một `match`.

---

# 1. Vấn đề của `match`

Giả sử có:

```rust
fn main() {
    let value = Some(10);

    match value {
        Some(number) => {
            println!("Number = {number}");
        }
        None => {}
    }
}
```

Code hoàn toàn đúng.

Nhưng chúng ta đang nói:

> Nếu là `Some`, làm gì đó. Nếu `None`, không làm gì.

Việc viết:

```rust
None => {}
```

khá dư thừa.

Rust cung cấp:

```rust
if let
```

để giải quyết chính trường hợp này.

---

# 2. Cú pháp cơ bản

```rust
if let PATTERN = VALUE {
    // code
}
```

Ví dụ:

```rust
fn main() {
    let value = Some(10);

    if let Some(number) = value {
        println!("Number = {number}");
    }
}
```

Output:

```text
Number = 10
```

Mental model:

```text
value
  │
  ▼
Some(10)
  │
  │ match pattern?
  ▼
Some(number)
  │
  ▼
number = 10
```

---

# 3. So sánh `match` và `if let`

### `match`

```rust
match value {
    Some(number) => println!("Number = {number}"),
    None => {}
}
```

### `if let`

```rust
if let Some(number) = value {
    println!("Number = {number}");
}
```

Có thể hiểu:

```text
match
→ xử lý nhiều trường hợp

if let
→ quan tâm một trường hợp
```

---

# 4. `if let` không chỉ dành cho `Option`

Ví dụ enum:

```rust
enum Status {
    Pending,
    Running,
    Completed,
}
```

Ta chỉ quan tâm `Running`:

```rust
fn main() {
    let status = Status::Running;

    if let Status::Running = status {
        println!("Crawler is running");
    }
}
```

Output:

```text
Crawler is running
```

Không cần:

```rust
match status {
    Status::Running => println!("Crawler is running"),
    _ => {}
}
```

---

# 5. `if let` với dữ liệu bên trong enum

Đây là trường hợp rất quan trọng.

```rust
enum Message {
    Text(String),
    Number(i32),
}
```

Ta chỉ quan tâm `Text`:

```rust
fn main() {
    let message = Message::Text(String::from("Hello"));

    if let Message::Text(text) = message {
        println!("Text = {text}");
    }
}
```

Output:

```text
Text = Hello
```

Pattern:

```rust
Message::Text(text)
```

vừa kiểm tra variant vừa lấy dữ liệu bên trong.

---

# 6. `if let` với `else`

`if let` có thể có `else`.

```rust
fn main() {
    let value = Some(10);

    if let Some(number) = value {
        println!("Found: {number}");
    } else {
        println!("No value");
    }
}
```

Output:

```text
Found: 10
```

Có thể xem nó tương đương về ý tưởng với:

```rust
match value {
    Some(number) => println!("Found: {number}"),
    None => println!("No value"),
}
```

---

# 7. `if let` + `else if let`

Bạn có thể kiểm tra nhiều pattern.

```rust
enum Status {
    Pending,
    Running,
    Completed,
}

fn main() {
    let status = Status::Running;

    if let Status::Pending = status {
        println!("Pending");
    } else if let Status::Running = status {
        println!("Running");
    } else if let Status::Completed = status {
        println!("Completed");
    }
}
```

Code này hợp lệ.

Nhưng nếu có nhiều trường hợp như vậy:

> `match` thường dễ đọc hơn.

---

# 8. Quy tắc chọn `match` hay `if let`

Hãy nhớ:

### Một pattern quan trọng

Dùng:

```rust
if let
```

### Nhiều pattern quan trọng

Dùng:

```rust
match
```

Ví dụ:

```rust
if let Some(user) = user {
    println!("{user:?}");
}
```

rất hợp lý.

Nhưng:

```rust
match status {
    Pending => ...
    Running => ...
    Completed => ...
    Failed => ...
}
```

thì `match` rõ ràng hơn.

---

# 9. `if let` với `Option`

Đây là use case phổ biến nhất.

```rust
fn main() {
    let username = Some("alice");

    if let Some(name) = username {
        println!("Hello, {name}");
    }
}
```

Nếu:

```rust
let username: Option<&str> = None;
```

thì:

```rust
if let Some(name) = username {
    println!("Hello, {name}");
}
```

không chạy.

Không có lỗi.

---

# 10. `if let` với `None`

Bạn cũng có thể match `None`:

```rust
fn main() {
    let value: Option<i32> = None;

    if let None = value {
        println!("No value");
    }
}
```

Nhưng trường hợp này thường:

```rust
if value.is_none() {
    println!("No value");
}
```

dễ đọc hơn.

Đây là một nguyên tắc:

> Không phải cứ pattern matching được thì nhất thiết phải dùng `if let`.

---

# 11. `if let` với `Result`

Đây là use case cực kỳ thực tế.

```rust
fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        Err(String::from("Cannot divide by zero"))
    } else {
        Ok(a / b)
    }
}
```

Ta chỉ quan tâm `Ok`:

```rust
fn main() {
    let result = divide(10, 2);

    if let Ok(value) = result {
        println!("Result = {value}");
    }
}
```

Output:

```text
Result = 5
```

---

# 12. `if let` + `else` với Result

```rust
fn main() {
    let result = divide(10, 0);

    if let Ok(value) = result {
        println!("Result = {value}");
    } else {
        println!("Operation failed");
    }
}
```

Nhưng nếu cần lấy cả error:

```rust
fn main() {
    let result = divide(10, 0);

    if let Ok(value) = result {
        println!("Result = {value}");
    } else if let Err(error) = result {
        println!("Error: {error}");
    }
}
```

Tuy nhiên cách này có một vấn đề ownership cần chú ý, và trong trường hợp muốn xử lý đầy đủ `Ok`/`Err`, `match` thường phù hợp hơn.

---

# 13. `if let` là pattern matching

Đừng nghĩ:

```rust
if let
```

chỉ là cú pháp rút gọn của:

```rust
if
```

Mental model chính xác hơn:

```text
if let
   │
   ├── pattern
   │
   └── value
```

Ví dụ:

```rust
if let Some(x) = value
```

có nghĩa:

> Nếu `value` khớp pattern `Some(x)`, thực hiện block.

---

# 14. Pattern có thể destructure

Ví dụ:

```rust
enum Message {
    Move { x: i32, y: i32 },
    Quit,
}
```

Ta có:

```rust
fn main() {
    let message = Message::Move { x: 10, y: 20 };

    if let Message::Move { x, y } = message {
        println!("x = {x}, y = {y}");
    }
}
```

Output:

```text
x = 10, y = 20
```

Đây chính là:

```text
pattern matching
+
destructuring
```

---

# 15. `_` trong `if let`

Bạn có thể bỏ qua dữ liệu.

```rust
enum Message {
    Text(String),
    Number(i32),
}

fn main() {
    let message = Message::Text(String::from("Hello"));

    if let Message::Text(_) = message {
        println!("This is a text message");
    }
}
```

Ở đây:

```rust
Message::Text(_)
```

có nghĩa:

> Là `Text`, nhưng tôi không quan tâm nội dung.

---

# 16. Binding

Nếu muốn lấy dữ liệu:

```rust
if let Message::Text(text) = message {
    println!("{text}");
}
```

Nếu không cần:

```rust
if let Message::Text(_) = message {
    println!("Text message");
}
```

---

# 17. `if let` với tuple

Pattern matching không chỉ dành cho enum.

```rust
fn main() {
    let point = (10, 20);

    if let (x, y) = point {
        println!("x = {x}, y = {y}");
    }
}
```

Ở đây pattern:

```rust
(x, y)
```

luôn khớp với tuple hai phần tử.

Vì vậy ví dụ này chủ yếu để minh họa destructuring; `if let` có giá trị nhất khi pattern có thể **không khớp**.

Ví dụ tốt hơn:

```rust
let point = (0, 20);

if let (0, y) = point {
    println!("On Y axis: {y}");
}
```

Output:

```text
On Y axis: 20
```

Nếu:

```rust
let point = (10, 20);
```

block không chạy.

---

# 18. `if let` với range

Bạn cũng có thể dùng pattern:

```rust
fn main() {
    let age = 25;

    if let 18..=60 = age {
        println!("Adult");
    }
}
```

Nếu:

```text
18 <= age <= 60
```

thì block chạy.

---

# 19. `if let` + guard

Pattern có thể kết hợp với guard.

Ví dụ:

```rust
fn main() {
    let value = Some(20);

    if let Some(number) = value
        && number > 10
    {
        println!("Number is greater than 10");
    }
}
```

Cú pháp điều kiện `let` như trên là một tính năng hiện đại của Rust.

Mental model:

```text
Some(number)
     │
     ▼
number > 10
     │
     ▼
execute
```

Nếu compiler/toolchain của bạn chưa hỗ trợ cú pháp này, có thể viết tương đương bằng nested `if`.

---

# 20. `if let` có thể trả về giá trị

Giống `if`, `if let` cũng có thể được dùng như expression.

Ví dụ:

```rust
fn main() {
    let value = Some(10);

    let result = if let Some(number) = value {
        number * 2
    } else {
        0
    };

    println!("{result}");
}
```

Output:

```text
20
```

Mental model:

```text
Some(10)
   │
   ▼
if let
   │
   ▼
20
```

---

# 21. Điều kiện phải trả cùng kiểu

Ví dụ:

```rust
let result = if let Some(number) = value {
    number * 2
} else {
    0
};
```

Hai nhánh đều trả:

```text
i32
```

Nhưng:

```rust
let result = if let Some(number) = value {
    number * 2
} else {
    "none"
};
```

sẽ lỗi vì:

```text
if branch → i32
else branch → &str
```

---

# 22. `if let` với một enum thực tế

Hãy quay lại project crawler.

```rust
#[derive(Debug)]
enum CrawlResult {
    Success { chapters: u32 },
    Failed { error: String },
    Skipped { reason: String },
}
```

Nếu chỉ muốn log thành công:

```rust
fn main() {
    let result = CrawlResult::Success {
        chapters: 120,
    };

    if let CrawlResult::Success { chapters } = result {
        println!("Crawled {chapters} chapters");
    }
}
```

Output:

```text
Crawled 120 chapters
```

Không cần xử lý:

```text
Failed
Skipped
```

---

# 23. `if let` rất hợp với event

Ví dụ:

```rust
enum Event {
    ChapterDownloaded(u32),
    ImageDownloaded(String),
    Error(String),
}
```

Nếu function chỉ quan tâm chapter:

```rust
fn handle_event(event: Event) {
    if let Event::ChapterDownloaded(chapter) = event {
        println!("Chapter downloaded: {chapter}");
    }
}
```

Đây là pattern thường gặp trong:

```text
event system
message queue
GUI
async application
crawler
state machine
```

---

# 24. `if let` với nested enum

Ví dụ:

```rust
enum Response {
    Success(Option<String>),
    Failed,
}
```

Ta có:

```rust
fn main() {
    let response = Response::Success(Some(String::from("Hello")));

    if let Response::Success(Some(message)) = response {
        println!("Message: {message}");
    }
}
```

Pattern:

```text
Response::Success(
    Some(message)
)
```

khớp cả hai tầng.

---

# 25. `if let` và Ownership

Đây là phần cần đặc biệt chú ý.

```rust
fn main() {
    let value = Some(String::from("hello"));

    if let Some(text) = value {
        println!("{text}");
    }

    // value có thể đã được move
}
```

Vì `text` lấy ownership của `String`.

Nếu muốn giữ `value`, có thể match reference:

```rust
fn main() {
    let value = Some(String::from("hello"));

    if let Some(text) = &value {
        println!("{text}");
    }

    println!("{value:?}");
}
```

Mental model:

```text
value
  │
  ├── owns String
  │
  └── &value
        │
        └── borrowed
```

Đây là bước chuẩn bị rất quan trọng cho phần Ownership/Borrowing.

---

# 26. `if let` và `match` — bảng so sánh

| Trường hợp                 | Nên dùng          |
| -------------------------- | ----------------- |
| Xử lý tất cả variant       | `match`           |
| Chỉ quan tâm một variant   | `if let`          |
| Có 2–3 pattern quan trọng  | thường `match`    |
| Một pattern + fallback     | `if let ... else` |
| Destructure enum           | cả hai            |
| `Option` chỉ lấy `Some`    | `if let`          |
| `Result` chỉ quan tâm `Ok` | `if let`          |
| State machine              | `match`           |

---

# 27. Khi nào KHÔNG nên dùng `if let`

Ví dụ:

```rust
enum State {
    Idle,
    Running,
    Paused,
    Completed,
}
```

Nếu bạn viết:

```rust
if let State::Idle = state {
    ...
} else if let State::Running = state {
    ...
} else if let State::Paused = state {
    ...
} else {
    ...
}
```

Code này bắt đầu khó đọc.

Nên dùng:

```rust
match state {
    State::Idle => ...
    State::Running => ...
    State::Paused => ...
    State::Completed => ...
}
```

Nguyên tắc:

> `if let` cho **một pattern nổi bật**; `match` cho **phân loại nhiều trường hợp**.

---

# 28. Complete Example — Story Repository

Hãy xây một ví dụ gần với hệ thống đọc truyện của bạn.

```rust
#[derive(Debug)]
struct Story {
    id: u32,
    title: String,
}

fn find_story(id: u32) -> Option<Story> {
    if id == 1 {
        Some(Story {
            id: 1,
            title: String::from("Rust Journey"),
        })
    } else {
        None
    }
}

fn main() {
    let result = find_story(1);

    if let Some(story) = result {
        println!("Found story:");
        println!("ID: {}", story.id);
        println!("Title: {}", story.title);
    } else {
        println!("Story not found");
    }
}
```

Output:

```text
Found story:
ID: 1
Title: Rust Journey
```

Đây là một pattern rất phổ biến:

```text
Repository
    │
    ▼
Option<Story>
    │
    ▼
if let Some(story)
```

---

# 29. Complete Example — Crawl Result

```rust
#[derive(Debug)]
enum CrawlResult {
    Success {
        chapters: u32,
    },
    Failed {
        error: String,
    },
}

fn crawl_story() -> CrawlResult {
    CrawlResult::Success {
        chapters: 100,
    }
}

fn main() {
    let result = crawl_story();

    if let CrawlResult::Success { chapters } = result {
        println!("Successfully crawled {chapters} chapters");
    } else {
        println!("Crawl was not successful");
    }
}
```

---

# 30. Complete Example — CLI Command

Giả sử:

```rust
enum Command {
    Crawl,
    Read,
    List,
    Exit,
}
```

Nếu chỉ muốn xử lý `Crawl`:

```rust
fn execute(command: Command) {
    if let Command::Crawl = command {
        println!("Starting crawler...");
    }
}
```

Nhưng nếu cần xử lý toàn bộ:

```rust
fn execute(command: Command) {
    match command {
        Command::Crawl => println!("Crawling..."),
        Command::Read => println!("Reading..."),
        Command::List => println!("Listing..."),
        Command::Exit => println!("Exiting..."),
    }
}
```

Đây chính là cách phân biệt thực tế giữa hai công cụ.

---

# 31. Lab hoàn chỉnh

Tạo project:

```bash
cargo new if_let_lab
cd if_let_lab
```

Thay `src/main.rs`:

```rust
#[derive(Debug)]
struct Story {
    id: u32,
    title: String,
}

enum CrawlResult {
    Success {
        story: Story,
    },

    Failed {
        error: String,
    },
}

fn crawl() -> CrawlResult {
    CrawlResult::Success {
        story: Story {
            id: 1,
            title: String::from("Learning Rust"),
        },
    }
}

fn main() {
    let result = crawl();

    if let CrawlResult::Success { story } = result {
        println!("Crawl successful!");
        println!("ID: {}", story.id);
        println!("Title: {}", story.title);
    } else {
        println!("Crawl failed!");
    }
}
```

Chạy:

```bash
cargo run
```

Kết quả:

```text
Crawl successful!
ID: 1
Title: Learning Rust
```

---

# 32. Bài tập 1 — Option

Viết:

```rust
fn get_username(id: u32) -> Option<String>
```

Quy tắc:

```text
id == 1 → Some("alice")
id != 1 → None
```

Sau đó dùng:

```rust
if let Some(username) = ...
```

để in username.

---

# 33. Bài tập 2 — Enum

Tạo:

```rust
enum DownloadStatus {
    Pending,
    Downloading(u32),
    Completed,
    Failed(String),
}
```

Viết code chỉ xử lý:

```text
Downloading
```

bằng:

```rust
if let
```

Ví dụ:

```text
Downloading: 75%
```

---

# 34. Bài tập 3 — Story

Tạo:

```rust
enum StoryStatus {
    Draft,
    Published,
    Archived,
}
```

Chỉ khi:

```text
Published
```

thì in:

```text
Story is available for reading.
```

Dùng `if let`.

---

# 35. Bài tập 4 — Nested Pattern

Tạo:

```rust
enum ApiResponse {
    Success(Option<String>),
    Error(String),
}
```

Xử lý duy nhất trường hợp:

```text
Success(Some(data))
```

bằng một `if let`.

Ví dụ:

```text
Data: Hello Rust
```

---

# 36. Bài tập 5 — `if let` expression

Viết:

```rust
let message = ...
```

sao cho:

```text
Some("hello") → "Found: hello"
None          → "Not found"
```

Sử dụng:

```rust
if let ... else ...
```

và trả về `String`.

---

# 37. Challenge — Crawler

Xây dựng:

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
fn handle_result(result: CrawlResult)
```

Yêu cầu:

* Nếu `Success` → in số chapter.
* Nếu không phải `Success` → in `"Crawler did not complete successfully"`.

Bắt buộc dùng:

```rust
if let
```

---

# 38. Challenge nâng cao

Tạo:

```rust
enum Event {
    ChapterDownloaded {
        chapter: u32,
    },

    ImageDownloaded {
        url: String,
    },

    Error {
        message: String,
    },
}
```

Viết:

```rust
fn handle_event(event: Event)
```

Chỉ xử lý:

```text
ChapterDownloaded
```

bằng `if let`.

Sau đó viết phiên bản thứ hai bằng `match`.

So sánh:

```text
if let
vs
match
```

và tự trả lời:

> Phiên bản nào thể hiện rõ ý định hơn?

---

# 39. Kiến thức cần nhớ

Sau Buổi 16, bạn cần hiểu:

```text
if let PATTERN = VALUE
```

và:

```text
if let PATTERN = VALUE {
    ...
} else {
    ...
}
```

Đồng thời hiểu được:

```text
if let
   ↓
pattern matching
   ↓
destructuring
   ↓
Option / Result / enum
```

Đặc biệt:

```rust
if let Some(value) = option {
    ...
}
```

là một pattern bạn sẽ gặp **rất thường xuyên** trong Rust thực tế.

---

# 40. `match` vs `if let`

Hãy ghi nhớ mental model này:

```text
                    Pattern Matching
                          │
             ┌────────────┴────────────┐
             │                         │
          match                     if let
             │                         │
      nhiều trường hợp          một trường hợp
             │                         │
      exhaustive             có thể bỏ qua phần còn lại
```

`match` thiên về:

> **"Tất cả các trường hợp có thể xảy ra là gì?"**

`if let` thiên về:

> **"Tôi chỉ quan tâm trường hợp này."**

---

# 41. Roadmap tiếp theo

Chúng ta đang đi đúng roadmap:

```text
Buổi 11 → if
Buổi 12 → loop
Buổi 13 → while
Buổi 14 → for
Buổi 15 → match
Buổi 16 → if let          ← hôm nay
Buổi 17 → while let
Buổi 18 → break & continue
Buổi 19 → Labels
Buổi 20 → Mini Project
```

**Buổi 17 — `while let`** sẽ nối trực tiếp từ bài này: chúng ta sẽ dùng pattern matching để tạo vòng lặp, đặc biệt với `Option`, iterator và các cấu trúc dữ liệu có thể trả về `Some/None`.
