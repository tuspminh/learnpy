# Rust — Phần II: Control Flow

# Buổi 17 — `while let`

Ở Buổi 16, chúng ta học:

```rust
if let PATTERN = VALUE
```

Hôm nay mở rộng ý tưởng đó thành:

```rust
while let PATTERN = VALUE
```

Mục tiêu là hiểu **`while let` không chỉ là một cú pháp ngắn**, mà là công cụ rất hữu ích để:

* lặp khi pattern còn khớp;
* xử lý `Option<T>`;
* xử lý iterator;
* lấy dữ liệu từng phần;
* xây dựng parser/state machine đơn giản;
* hiểu sâu hơn mối quan hệ giữa `pattern matching` và `control flow`.

---

# 1. `while let` là gì?

Cú pháp:

```rust
while let PATTERN = EXPRESSION {
    // code
}
```

Ý nghĩa:

> Chạy vòng lặp **chừng nào expression còn khớp với pattern**.

Ví dụ:

```rust
fn main() {
    let mut value = Some(3);

    while let Some(number) = value {
        println!("{number}");

        value = None;
    }
}
```

Output:

```text
3
```

---

# 2. So sánh với `if let`

Buổi trước:

```rust
if let Some(value) = option {
    println!("{value}");
}
```

chạy **một lần** nếu pattern khớp.

Còn:

```rust
while let Some(value) = option {
    // ...
}
```

sẽ tiếp tục kiểm tra pattern sau mỗi vòng.

Mental model:

```text
             expression
                  │
                  ▼
          pattern có khớp?
             │        │
            YES       NO
             │         │
             ▼         ▼
          chạy       thoát
             │
             ▼
       kiểm tra lại
```

---

# 3. Ví dụ cơ bản nhất

```rust
fn main() {
    let mut stack = vec![1, 2, 3];

    while let Some(value) = stack.pop() {
        println!("{value}");
    }
}
```

Output:

```text
3
2
1
```

Đây là ví dụ **cực kỳ quan trọng**.

---

# 4. Tại sao nó hoạt động?

`Vec::pop()` trả về:

```rust
Option<T>
```

Cụ thể:

```text
Có phần tử:
Some(value)

Hết phần tử:
None
```

Vòng lặp:

```rust
while let Some(value) = stack.pop()
```

có nghĩa:

```text
pop()
   │
   ├── Some(value) → chạy body
   │
   └── None        → dừng
```

Đây là một trong những use case kinh điển của `while let`.

---

# 5. Hãy nhìn từng vòng

Ban đầu:

```rust
let mut stack = vec![1, 2, 3];
```

Trạng thái:

```text
[1, 2, 3]
```

### Vòng 1

```rust
stack.pop()
```

→ `Some(3)`

```text
value = 3
```

Stack:

```text
[1, 2]
```

---

### Vòng 2

```rust
stack.pop()
```

→ `Some(2)`

Stack:

```text
[1]
```

---

### Vòng 3

```rust
stack.pop()
```

→ `Some(1)`

Stack:

```text
[]
```

---

### Vòng 4

```rust
stack.pop()
```

→ `None`

Pattern:

```rust
Some(value)
```

không khớp.

Vòng lặp kết thúc.

---

# 6. Đây chính là pattern matching trong loop

Bạn có thể xem:

```rust
while let Some(value) = stack.pop() {
    println!("{value}");
}
```

gần giống:

```rust
loop {
    match stack.pop() {
        Some(value) => {
            println!("{value}");
        }

        None => {
            break;
        }
    }
}
```

Hai đoạn code thể hiện cùng một ý tưởng.

Nhưng:

```rust
while let
```

ngắn và thể hiện ý định rõ hơn.

---

# 7. `while let` với `Vec`

Ví dụ xử lý task queue:

```rust
fn main() {
    let mut tasks = vec![
        "Download",
        "Parse",
        "Save",
    ];

    while let Some(task) = tasks.pop() {
        println!("Processing: {task}");
    }
}
```

Output:

```text
Processing: Save
Processing: Parse
Processing: Download
```

Lưu ý:

`Vec::pop()` lấy phần tử từ cuối nên đây là **LIFO**.

```text
Last In
   ↓
First Out
```

---

# 8. Xây Stack

Đây là một ví dụ rất tốt để hiểu `while let`.

```rust
struct Stack<T> {
    items: Vec<T>,
}

impl<T> Stack<T> {
    fn new() -> Self {
        Self {
            items: Vec::new(),
        }
    }

    fn push(&mut self, value: T) {
        self.items.push(value);
    }

    fn pop(&mut self) -> Option<T> {
        self.items.pop()
    }
}

fn main() {
    let mut stack = Stack::new();

    stack.push(10);
    stack.push(20);
    stack.push(30);

    while let Some(value) = stack.pop() {
        println!("Popped: {value}");
    }
}
```

Output:

```text
Popped: 30
Popped: 20
Popped: 10
```

---

# 9. `while let` với `Option`

Không nhất thiết phải dùng `Vec`.

Ví dụ:

```rust
fn main() {
    let mut value = Some(10);

    while let Some(number) = value {
        println!("number = {number}");

        value = if number > 0 {
            Some(number - 1)
        } else {
            None
        };
    }
}
```

Output:

```text
number = 10
number = 9
number = 8
number = 7
number = 6
number = 5
number = 4
number = 3
number = 2
number = 1
number = 0
```

Đây là một dạng state transition.

---

# 10. Phân tích ví dụ trên

Ban đầu:

```text
Some(10)
```

Mỗi vòng:

```text
Some(10)
 ↓
Some(9)
 ↓
Some(8)
 ↓
...
 ↓
Some(0)
 ↓
None
```

Vì:

```rust
while let Some(number) = value
```

chỉ chạy khi:

```rust
value == Some(...)
```

Khi:

```rust
value == None
```

vòng lặp dừng.

---

# 11. `while let` với `Iterator`

Đây là phần rất quan trọng.

Ví dụ:

```rust
fn main() {
    let numbers = vec![10, 20, 30];

    let mut iter = numbers.into_iter();

    while let Some(number) = iter.next() {
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

Tại sao?

`Iterator::next()` trả về:

```rust
Option<Item>
```

Cụ thể:

```text
Có phần tử
→ Some(item)

Hết
→ None
```

Do đó:

```rust
while let Some(item) = iter.next()
```

rất tự nhiên.

---

# 12. Đây là cầu nối tới Iterator

Bạn sẽ sớm học:

```text
Iterator
├── next()
├── map()
├── filter()
├── collect()
├── find()
├── position()
└── enumerate()
```

Trong đó:

```rust
next()
```

thường có dạng:

```rust
Option<Item>
```

Vì vậy:

```rust
while let Some(item) = iterator.next()
```

là một pattern quan trọng cần nhớ.

---

# 13. Nhưng tại sao không dùng `for`?

Ví dụ:

```rust
let numbers = vec![10, 20, 30];

for number in numbers {
    println!("{number}");
}
```

Đơn giản hơn.

Vậy tại sao cần:

```rust
while let Some(number) = iter.next()
```

?

Vì `while let` cho phép bạn **kiểm soát quá trình lấy từng item**.

Ví dụ:

```rust
fn main() {
    let numbers = vec![10, 20, 30, 40, 50];

    let mut iter = numbers.into_iter();

    while let Some(number) = iter.next() {
        println!("{number}");

        if number == 30 {
            break;
        }
    }
}
```

Output:

```text
10
20
30
```

---

# 14. `while let` + `break`

Đây là sự kết hợp rất tự nhiên:

```rust
while let Some(value) = something() {
    if condition {
        break;
    }
}
```

Ví dụ:

```rust
fn main() {
    let mut stack = vec![1, 2, 3, 4, 5];

    while let Some(value) = stack.pop() {
        if value == 3 {
            break;
        }

        println!("{value}");
    }
}
```

Output:

```text
5
4
```

Khi pop được `3`, `break`.

---

# 15. `while let` + `continue`

Ví dụ:

```rust
fn main() {
    let mut stack = vec![1, 2, 3, 4, 5];

    while let Some(value) = stack.pop() {
        if value % 2 == 0 {
            continue;
        }

        println!("{value}");
    }
}
```

Output:

```text
5
3
1
```

Các số chẵn bị bỏ qua.

---

# 16. `while let` với enum

Ví dụ:

```rust
enum Command {
    Continue,
    Stop,
}
```

Ta có:

```rust
fn main() {
    let mut commands = vec![
        Command::Continue,
        Command::Continue,
        Command::Stop,
    ];

    while let Some(command) = commands.pop() {
        match command {
            Command::Continue => {
                println!("Continue");
            }

            Command::Stop => {
                println!("Stop");
                break;
            }
        }
    }
}
```

Output:

```text
Stop
```

Do `pop()` lấy từ cuối.

---

# 17. `while let` với enum pattern trực tiếp

Không nhất thiết pattern phải là `Some`.

Ví dụ:

```rust
enum State {
    Running,
    Stopped,
}
```

Bạn có thể:

```rust
fn main() {
    let mut state = State::Running;

    while let State::Running = state {
        println!("Running");

        state = State::Stopped;
    }
}
```

Output:

```text
Running
```

Khi:

```text
state == State::Stopped
```

pattern không còn khớp và loop kết thúc.

---

# 18. State Machine đơn giản

Ví dụ:

```rust
enum State {
    Start,
    Running(u32),
    Done,
}

fn main() {
    let mut state = State::Start;

    while let State::Running(count) = state {
        println!("Running: {count}");

        state = if count >= 5 {
            State::Done
        } else {
            State::Running(count + 1)
        };
    }

    println!("Finished");
}
```

Nhưng chú ý:

Ban đầu:

```rust
State::Start
```

không khớp:

```rust
State::Running(count)
```

nên vòng lặp **không chạy lần nào**.

Đây là ví dụ tốt để hiểu rằng `while let` kiểm tra pattern **ngay trước mỗi iteration**.

---

# 19. Sửa state machine

Nếu muốn `Start` chuyển sang `Running`:

```rust
enum State {
    Start,
    Running(u32),
    Done,
}

fn main() {
    let mut state = State::Start;

    loop {
        state = match state {
            State::Start => {
                println!("Starting...");
                State::Running(1)
            }

            State::Running(count) => {
                println!("Running: {count}");

                if count >= 5 {
                    State::Done
                } else {
                    State::Running(count + 1)
                }
            }

            State::Done => {
                println!("Done!");
                break;
            }
        };
    }
}
```

Đây lại là trường hợp `match` phù hợp hơn.

Điểm cần học:

> `while let` rất phù hợp khi **một pattern là điều kiện tiếp tục của vòng lặp**.

---

# 20. `while let` với nested pattern

Ví dụ:

```rust
fn main() {
    let mut values = vec![
        Some(10),
        Some(20),
        None,
    ];

    while let Some(Some(value)) = values.pop() {
        println!("{value}");
    }
}
```

Phân tích:

```text
values.pop()
     │
     ▼
Option<Option<i32>>
```

Pattern:

```rust
Some(Some(value))
```

phải khớp hai tầng.

---

# 21. Điều gì xảy ra khi gặp `None` bên trong?

Giả sử:

```text
values = [
    Some(10),
    Some(20),
    None
]
```

`pop()`:

```text
None
```

Kết quả:

```text
None
```

không khớp:

```rust
Some(Some(value))
```

→ loop dừng ngay.

Điều này cho thấy pattern có thể mô tả **cấu trúc dữ liệu phức tạp**.

---

# 22. `while let` với `Result`

Bạn cũng có thể làm:

```rust
fn next_number(value: &mut i32) -> Result<i32, String> {
    if *value <= 0 {
        Err(String::from("Finished"))
    } else {
        *value -= 1;
        Ok(*value)
    }
}

fn main() {
    let mut value = 5;

    while let Ok(number) = next_number(&mut value) {
        println!("{number}");
    }
}
```

Output:

```text
4
3
2
1
0
```

Khi function trả:

```rust
Err(...)
```

pattern:

```rust
Ok(number)
```

không khớp.

Loop kết thúc.

---

# 23. Nhưng hãy cẩn thận

Code:

```rust
while let Ok(value) = some_operation() {
    ...
}
```

có nghĩa:

> Khi gặp `Err`, tôi sẽ âm thầm kết thúc vòng lặp.

Nếu `Err` là lỗi quan trọng, đây có thể là cách xử lý không tốt.

Trong trường hợp cần phân biệt:

```text
Ok
Err
```

thì:

```rust
match
```

thường tốt hơn.

Ví dụ:

```rust
loop {
    match some_operation() {
        Ok(value) => {
            println!("{value}");
        }

        Err(error) => {
            eprintln!("Error: {error}");
            break;
        }
    }
}
```

---

# 24. `while let` và ownership

Ví dụ:

```rust
fn main() {
    let mut stack = vec![
        String::from("A"),
        String::from("B"),
        String::from("C"),
    ];

    while let Some(value) = stack.pop() {
        println!("{value}");
    }
}
```

Điều này rất đẹp vì:

```rust
pop()
```

transfer ownership của phần tử ra ngoài vector.

```text
Vec<String>
    │
    │ pop()
    ▼
Option<String>
    │
    ▼
Some(value)
    │
    ▼
value owns String
```

Đây là một pattern bạn sẽ gặp thường xuyên trong Rust.

---

# 25. Ví dụ thực tế — Task Queue

Hãy xây một task queue đơn giản:

```rust
struct Task {
    id: u32,
    name: String,
}

fn main() {
    let mut queue = vec![
        Task {
            id: 1,
            name: String::from("Download"),
        },
        Task {
            id: 2,
            name: String::from("Parse"),
        },
        Task {
            id: 3,
            name: String::from("Save"),
        },
    ];

    while let Some(task) = queue.pop() {
        println!(
            "Processing task {}: {}",
            task.id,
            task.name
        );
    }
}
```

Output:

```text
Processing task 3: Save
Processing task 2: Parse
Processing task 1: Download
```

Đây chính là dạng logic có thể xuất hiện trong crawler worker.

---

# 26. Task Queue FIFO

Nếu muốn FIFO thay vì LIFO, `Vec::pop()` không phù hợp.

Có thể dùng `VecDeque`.

```rust
use std::collections::VecDeque;

struct Task {
    id: u32,
    name: String,
}

fn main() {
    let mut queue = VecDeque::new();

    queue.push_back(Task {
        id: 1,
        name: String::from("Download"),
    });

    queue.push_back(Task {
        id: 2,
        name: String::from("Parse"),
    });

    queue.push_back(Task {
        id: 3,
        name: String::from("Save"),
    });

    while let Some(task) = queue.pop_front() {
        println!(
            "Processing task {}: {}",
            task.id,
            task.name
        );
    }
}
```

Output:

```text
Processing task 1: Download
Processing task 2: Parse
Processing task 3: Save
```

Đây là một ví dụ thực tế rất đáng nhớ:

```text
Vec
→ stack / LIFO

VecDeque
→ queue / FIFO
```

---

# 27. `while let` + `VecDeque`

Pattern:

```rust
while let Some(task) = queue.pop_front() {
    process(task);
}
```

cực kỳ tự nhiên.

Mental model:

```text
Queue
 │
 ├── Task 1 → process
 ├── Task 2 → process
 ├── Task 3 → process
 │
 └── None → stop
```

---

# 28. Ví dụ thực tế — Crawl Queue

```rust
use std::collections::VecDeque;

#[derive(Debug)]
struct CrawlTask {
    story_id: u32,
    chapter: u32,
}

fn main() {
    let mut queue = VecDeque::new();

    queue.push_back(CrawlTask {
        story_id: 1,
        chapter: 1,
    });

    queue.push_back(CrawlTask {
        story_id: 1,
        chapter: 2,
    });

    queue.push_back(CrawlTask {
        story_id: 2,
        chapter: 1,
    });

    while let Some(task) = queue.pop_front() {
        println!(
            "Crawling story={} chapter={}",
            task.story_id,
            task.chapter
        );
    }
}
```

Output:

```text
Crawling story=1 chapter=1
Crawling story=1 chapter=2
Crawling story=2 chapter=1
```

Đây là code có cấu trúc rất gần với một crawler worker đơn giản.

---

# 29. `while let` không phải lúc nào cũng tốt hơn `for`

So sánh:

```rust
let numbers = vec![1, 2, 3];

for number in numbers {
    println!("{number}");
}
```

với:

```rust
let numbers = vec![1, 2, 3];
let mut iter = numbers.into_iter();

while let Some(number) = iter.next() {
    println!("{number}");
}
```

Trong trường hợp đơn giản:

```rust
for
```

tốt hơn.

Vì:

```text
for
→ biểu đạt "duyệt toàn bộ"

while let
→ biểu đạt "lặp khi pattern còn khớp"
```

---

# 30. Khi nào nên dùng `while let`?

### Trường hợp 1

API trả:

```rust
Option<T>
```

và bạn muốn lấy từng phần tử cho tới `None`.

```rust
while let Some(item) = source.next() {
    ...
}
```

### Trường hợp 2

Bạn đang pop queue:

```rust
while let Some(task) = queue.pop_front() {
    ...
}
```

### Trường hợp 3

Bạn có state/pattern xác định điều kiện tiếp tục:

```rust
while let State::Running(...) = state {
    ...
}
```

### Trường hợp 4

Bạn muốn kết hợp pattern matching với vòng lặp.

---

# 31. Khi nào không nên dùng?

Nếu chỉ duyệt collection:

```rust
for item in collection {
    ...
}
```

thường tốt hơn.

Nếu cần xử lý nhiều trạng thái:

```rust
match value {
    Some(...) => ...
    None => ...
}
```

thường tốt hơn.

Nếu lỗi `Err` cần được xử lý rõ ràng:

```rust
match
```

thường tốt hơn:

```rust
while let Ok(...)
```

---

# 32. Complete Lab

Tạo project:

```bash
cargo new while_let_lab
cd while_let_lab
```

Thay `src/main.rs`:

```rust
use std::collections::VecDeque;

#[derive(Debug)]
struct CrawlTask {
    story_id: u32,
    chapter: u32,
}

fn main() {
    let mut queue = VecDeque::new();

    queue.push_back(CrawlTask {
        story_id: 1,
        chapter: 1,
    });

    queue.push_back(CrawlTask {
        story_id: 1,
        chapter: 2,
    });

    queue.push_back(CrawlTask {
        story_id: 1,
        chapter: 3,
    });

    queue.push_back(CrawlTask {
        story_id: 2,
        chapter: 1,
    });

    while let Some(task) = queue.pop_front() {
        println!(
            "Processing story={} chapter={}",
            task.story_id,
            task.chapter
        );
    }

    println!("Queue completed.");
}
```

Chạy:

```bash
cargo run
```

Kết quả:

```text
Processing story=1 chapter=1
Processing story=1 chapter=2
Processing story=1 chapter=3
Processing story=2 chapter=1
Queue completed.
```

---

# 33. Lab nâng cao — Worker

Bây giờ thêm function:

```rust
use std::collections::VecDeque;

#[derive(Debug)]
struct CrawlTask {
    story_id: u32,
    chapter: u32,
}

fn process_task(task: CrawlTask) {
    println!(
        "[WORKER] story={} chapter={}",
        task.story_id,
        task.chapter
    );
}

fn main() {
    let mut queue = VecDeque::new();

    queue.push_back(CrawlTask {
        story_id: 1,
        chapter: 1,
    });

    queue.push_back(CrawlTask {
        story_id: 1,
        chapter: 2,
    });

    queue.push_back(CrawlTask {
        story_id: 2,
        chapter: 1,
    });

    while let Some(task) = queue.pop_front() {
        process_task(task);
    }

    println!("[WORKER] Queue completed");
}
```

Đây là pattern nền tảng cho:

```text
Producer
   ↓
Queue
   ↓
Worker
   ↓
Process
```

Sau này khi học:

```text
thread
channel
async
Tokio
```

bạn sẽ gặp lại tư tưởng này.

---

# 34. Bài tập thực hành

## Bài 1 — Stack

Tạo:

```rust
let mut stack = vec![10, 20, 30, 40, 50];
```

Dùng:

```rust
while let
```

để lấy toàn bộ phần tử.

Kết quả:

```text
50
40
30
20
10
```

---

## Bài 2 — Queue

Dùng:

```rust
VecDeque
```

thêm:

```text
Task 1
Task 2
Task 3
Task 4
```

Sau đó dùng:

```rust
while let Some(...)
```

để xử lý theo FIFO.

Kết quả:

```text
Task 1
Task 2
Task 3
Task 4
```

---

# 35. Bài 3 — Countdown bằng `Option`

Viết:

```rust
fn main() {
    let mut value = Some(10);

    // while let
}
```

Kết quả:

```text
10
9
8
7
6
5
4
3
2
1
0
```

Khi tới `0`, chuyển thành:

```rust
None
```

---

# 36. Bài 4 — Iterator thủ công

Cho:

```rust
let numbers = vec![10, 20, 30, 40, 50];

let mut iter = numbers.into_iter();
```

Dùng:

```rust
while let Some(number) = iter.next()
```

để in từng số.

Sau đó sửa để dừng khi gặp:

```text
30
```

---

# 37. Bài 5 — Download queue

Tạo:

```rust
#[derive(Debug)]
struct DownloadTask {
    url: String,
}
```

Tạo:

```rust
VecDeque<DownloadTask>
```

và thêm:

```text
https://example.com/a
https://example.com/b
https://example.com/c
```

Dùng:

```rust
while let Some(task) = queue.pop_front()
```

để xử lý.

---

# 38. Challenge — Crawler Worker

Xây:

```rust
enum CrawlTask {
    DownloadChapter {
        story_id: u32,
        chapter: u32,
    },

    DownloadImage {
        url: String,
    },

    SaveChapter {
        chapter: u32,
    },
}
```

Tạo:

```rust
VecDeque<CrawlTask>
```

Sau đó:

```rust
while let Some(task) = queue.pop_front() {
    match task {
        CrawlTask::DownloadChapter {
            story_id,
            chapter,
        } => {
            println!(
                "Download story={story_id}, chapter={chapter}"
            );
        }

        CrawlTask::DownloadImage { url } => {
            println!("Download image: {url}");
        }

        CrawlTask::SaveChapter { chapter } => {
            println!("Save chapter: {chapter}");
        }
    }
}
```

Đây là một bài rất đáng làm vì nó kết hợp:

```text
VecDeque
   +
while let
   +
enum
   +
match
   +
destructuring
```

Bạn đang bắt đầu sử dụng các thành phần cốt lõi của Rust cùng nhau.

---

# 39. Mental Model quan trọng nhất

Hãy nhớ:

```text
while let Some(value) = expression
```

không nên đọc đơn giản là:

> "while có value"

Mà hãy đọc:

> **"Trong khi kết quả của expression còn khớp với pattern `Some(value)` thì tiếp tục."**

Ví dụ:

```rust
while let Some(task) = queue.pop_front() {
    process(task);
}
```

đọc thành:

> "Trong khi queue còn trả về `Some(task)`, lấy task và xử lý."

Khi queue trả:

```rust
None
```

→ dừng.

---

# 40. Tổng kết Buổi 17

Bạn cần nắm chắc:

```text
while let
│
├── pattern matching
├── Option
├── Vec::pop()
├── VecDeque::pop_front()
├── Iterator::next()
├── enum
├── destructuring
├── break
├── continue
└── ownership
```

Công thức quan trọng:

```rust
while let Some(value) = something() {
    // process value
}
```

Các pattern thực tế:

```rust
while let Some(item) = iterator.next() {
    ...
}
```

```rust
while let Some(task) = queue.pop_front() {
    ...
}
```

```rust
while let Some(value) = stack.pop() {
    ...
}
```

---

# Roadmap

```text
Buổi 11 → if
Buổi 12 → loop
Buổi 13 → while
Buổi 14 → for
Buổi 15 → match
Buổi 16 → if let
Buổi 17 → while let       ← hôm nay
Buổi 18 → break & continue
Buổi 19 → Labels
Buổi 20 → Mini Project
```

**Buổi 18** chúng ta sẽ hệ thống hóa `break` và `continue`, bao gồm `break` trả về giá trị, `loop` như một expression, cách điều khiển vòng lặp phức tạp và cách kết hợp chúng với `match`/`while let`.
