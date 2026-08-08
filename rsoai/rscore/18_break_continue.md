# Rust — Phần II: Control Flow

# Buổi 18 — `break` & `continue`

Buổi hôm nay tập trung vào hai từ khóa cực kỳ quan trọng:

```rust
break
continue
```

Nhìn thì đơn giản, nhưng trong Rust chúng còn có một điểm rất đáng chú ý:

> **`break` có thể trả về giá trị.**

Điều này biến `loop` thành một **expression**, rất hữu ích khi xây dựng logic xử lý dữ liệu, worker, parser, retry loop và state machine.

---

# 1. `break` là gì?

`break` dùng để:

> **Thoát ngay khỏi vòng lặp hiện tại.**

Ví dụ:

```rust
fn main() {
    let mut count = 0;

    loop {
        println!("count = {count}");

        count += 1;

        if count == 5 {
            break;
        }
    }

    println!("Done");
}
```

Output:

```text
count = 0
count = 1
count = 2
count = 3
count = 4
Done
```

Flow:

```text
loop
 │
 ├── iteration
 │
 ├── iteration
 │
 ├── iteration
 │
 └── break
       │
       ▼
     exit
```

---

# 2. `break` chỉ thoát vòng lặp

Ví dụ:

```rust
fn main() {
    loop {
        println!("Before");

        break;

        println!("After");
    }

    println!("Outside");
}
```

`After` không bao giờ chạy.

Kết quả:

```text
Before
Outside
```

---

# 3. `continue` là gì?

`continue` không thoát vòng lặp.

Nó:

> **Bỏ qua phần còn lại của iteration hiện tại và chuyển sang iteration tiếp theo.**

Ví dụ:

```rust
fn main() {
    for number in 1..=5 {
        if number == 3 {
            continue;
        }

        println!("{number}");
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

Khi:

```text
number == 3
```

thì:

```rust
continue;
```

→ bỏ qua `println!`.

---

# 4. So sánh trực quan

```text
break
  ↓
THOÁT vòng lặp


continue
  ↓
BỎ QUA iteration hiện tại
  ↓
iteration tiếp theo
```

Ví dụ:

```rust
for i in 1..=10 {
    if i == 3 {
        continue;
    }

    if i == 8 {
        break;
    }

    println!("{i}");
}
```

Output:

```text
1
2
4
5
6
7
```

Phân tích:

```text
1 → print
2 → print
3 → continue
4 → print
5 → print
6 → print
7 → print
8 → break
```

---

# 5. `break` trong `while`

```rust
fn main() {
    let mut number = 0;

    while number < 10 {
        println!("{number}");

        if number == 5 {
            break;
        }

        number += 1;
    }
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

Điểm quan trọng:

```rust
number < 10
```

vẫn còn đúng ở `5`.

Nhưng:

```rust
break;
```

được thực hiện trước khi iteration tiếp theo bắt đầu.

---

# 6. `continue` trong `while`

```rust
fn main() {
    let mut number = 0;

    while number < 10 {
        number += 1;

        if number % 2 == 0 {
            continue;
        }

        println!("{number}");
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

---

# 7. Cẩn thận với `continue` trong `while`

Đây là lỗi rất phổ biến.

Sai:

```rust
fn main() {
    let mut number = 0;

    while number < 10 {
        if number % 2 == 0 {
            continue;
        }

        number += 1;
        println!("{number}");
    }
}
```

Tại:

```text
number = 0
```

điều kiện:

```rust
number % 2 == 0
```

đúng.

→ `continue`

Nhưng:

```rust
number += 1;
```

không bao giờ được chạy.

Kết quả:

```text
infinite loop
```

---

# 8. Sửa lại

Cần cập nhật state trước `continue`:

```rust
fn main() {
    let mut number = 0;

    while number < 10 {
        number += 1;

        if number % 2 == 0 {
            continue;
        }

        println!("{number}");
    }
}
```

Đây là một nguyên tắc rất quan trọng:

> Với `while`, hãy đảm bảo state điều khiển vòng lặp vẫn được cập nhật trước `continue`.

---

# 9. `break` trong `loop`

Đây là use case kinh điển:

```rust
fn main() {
    let mut number = 0;

    loop {
        number += 1;

        if number == 10 {
            break;
        }
    }

    println!("number = {number}");
}
```

`loop` không cần điều kiện kết thúc.

```rust
loop {
    ...
}
```

chỉ kết thúc khi có:

```rust
break;
```

hoặc một cơ chế khác làm flow không tiếp tục.

---

# 10. `break` có thể trả về giá trị

Đây là tính năng rất quan trọng.

Ví dụ:

```rust
fn main() {
    let result = loop {
        break 42;
    };

    println!("{result}");
}
```

Output:

```text
42
```

Tức là:

```rust
let result = loop {
    break 42;
};
```

có nghĩa:

```text
loop
 ↓
break 42
 ↓
result = 42
```

---

# 11. `loop` là expression

Trong Rust:

```rust
let result = loop {
    break 42;
};
```

`loop` có giá trị.

Đây là một điểm khác biệt quan trọng với cách nhiều người mới học Rust hình dung về vòng lặp.

---

# 12. Ví dụ thực tế — tìm số

```rust
fn main() {
    let result = loop {
        let number = 10;

        if number > 5 {
            break number;
        }
    };

    println!("Found: {result}");
}
```

Output:

```text
Found: 10
```

---

# 13. `break` với expression

Bạn cũng có thể:

```rust
fn main() {
    let result = loop {
        let value = 100;

        if value == 100 {
            break value * 2;
        }
    };

    println!("{result}");
}
```

Output:

```text
200
```

---

# 14. Retry loop

Đây là use case thực tế.

Giả sử muốn thử một operation tối đa 3 lần:

```rust
fn main() {
    let mut attempts = 0;

    let result = loop {
        attempts += 1;

        println!("Attempt {attempts}");

        if attempts == 3 {
            break "Success";
        }
    };

    println!("Result: {result}");
}
```

Output:

```text
Attempt 1
Attempt 2
Attempt 3
Result: Success
```

---

# 15. Retry thực tế hơn

```rust
fn perform_operation(attempt: u32) -> Result<String, String> {
    if attempt >= 3 {
        Ok(String::from("Success"))
    } else {
        Err(String::from("Temporary failure"))
    }
}

fn main() {
    let mut attempts = 0;

    let result = loop {
        attempts += 1;

        match perform_operation(attempts) {
            Ok(value) => break Ok(value),

            Err(error) => {
                println!("Attempt {attempts}: {error}");

                if attempts >= 5 {
                    break Err(error);
                }
            }
        }
    };

    println!("Final result: {result:?}");
}
```

Output:

```text
Attempt 1: Temporary failure
Attempt 2: Temporary failure
Final result: Ok("Success")
```

Điểm rất hay:

```rust
break Ok(value)
```

hoặc:

```rust
break Err(error)
```

`loop` trả về:

```rust
Result<String, String>
```

---

# 16. `break` trả về `Option`

Ví dụ tìm phần tử:

```rust
fn main() {
    let numbers = vec![10, 20, 30, 40];

    let result = loop {
        for number in &numbers {
            if *number == 30 {
                break Some(*number);
            }
        }

        break None;
    };

    println!("{result:?}");
}
```

Output:

```text
Some(30)
```

Tuy nhiên ví dụ này chưa tối ưu; sau này bạn sẽ biết các iterator method như:

```rust
find()
```

có thể biểu đạt việc này tốt hơn.

Nhưng nó giúp hiểu:

```rust
break Some(value)
```

---

# 17. `break` trong `while let`

Kết hợp kiến thức Buổi 17:

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

Khi gặp:

```text
3
```

→ `break`.

---

# 18. `continue` trong `while let`

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

---

# 19. `break` trong `for`

```rust
fn main() {
    for number in 1..=10 {
        if number == 6 {
            break;
        }

        println!("{number}");
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

---

# 20. `continue` trong `for`

```rust
fn main() {
    for number in 1..=10 {
        if number % 2 == 0 {
            continue;
        }

        println!("{number}");
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

---

# 21. `break` và `continue` trong nested loop

Đây là lúc chúng ta gặp một vấn đề.

```rust
fn main() {
    for i in 1..=3 {
        for j in 1..=3 {
            if j == 2 {
                break;
            }

            println!("i={i}, j={j}");
        }
    }
}
```

Output:

```text
i=1, j=1
i=2, j=1
i=3, j=1
```

`break` chỉ thoát:

```text
inner loop
```

không thoát:

```text
outer loop
```

---

# 22. `continue` cũng chỉ áp dụng loop gần nhất

```rust
fn main() {
    for i in 1..=2 {
        for j in 1..=3 {
            if j == 2 {
                continue;
            }

            println!("i={i}, j={j}");
        }
    }
}
```

Output:

```text
i=1, j=1
i=1, j=3
i=2, j=1
i=2, j=3
```

`continue` áp dụng cho:

```text
inner loop
```

---

# 23. Muốn điều khiển outer loop?

Rust có:

```text
labels
```

Ví dụ:

```rust
'outer: for i in 1..=3 {
    for j in 1..=3 {
        if j == 2 {
            break 'outer;
        }

        println!("i={i}, j={j}");
    }
}
```

Output:

```text
i=1, j=1
```

Đây là chủ đề của:

# Buổi 19 — Labels

---

# 24. `break` có giá trị trong nested loop

Bạn có thể có:

```rust
let result = loop {
    for number in 1..=10 {
        if number == 5 {
            break number;
        }
    }

    break 0;
};
```

Nhưng chú ý:

```rust
break number;
```

chỉ break `for`.

Nó không trả trực tiếp giá trị cho `loop` bên ngoài.

Nếu muốn thoát nhiều tầng:

```rust
break 'label value;
```

Đó chính là lý do labels rất quan trọng.

---

# 25. `continue` và `match`

Ví dụ crawler:

```rust
enum CrawlResult {
    Success,
    Failed,
    Skipped,
}

fn main() {
    let results = vec![
        CrawlResult::Success,
        CrawlResult::Failed,
        CrawlResult::Skipped,
        CrawlResult::Success,
    ];

    for result in results {
        match result {
            CrawlResult::Success => {
                println!("Success");
            }

            CrawlResult::Failed => {
                println!("Failed");
            }

            CrawlResult::Skipped => {
                continue;
            }
        }
    }
}
```

Output:

```text
Success
Failed
Success
```

`continue` nằm trong nhánh `match`, nhưng nó tác động đến vòng `for` bên ngoài.

---

# 26. `break` + `match`

Ví dụ:

```rust
enum Event {
    Continue,
    Stop,
}

fn main() {
    let events = vec![
        Event::Continue,
        Event::Continue,
        Event::Stop,
        Event::Continue,
    ];

    for event in events {
        match event {
            Event::Continue => {
                println!("Processing...");
            }

            Event::Stop => {
                println!("Stopping...");
                break;
            }
        }
    }
}
```

Output:

```text
Processing...
Processing...
Stopping...
```

Event sau `Stop` không được xử lý.

---

# 27. `break` trả về dữ liệu từ `match`

Một pattern cực kỳ hữu ích:

```rust
fn main() {
    let result = loop {
        let value = 42;

        let action = match value {
            0 => break "zero",
            1..=10 => break "small",
            _ => break "large",
        };

        println!("{action}");
    };

    println!("{result}");
}
```

Ở đây mỗi branch có thể:

```rust
break ...
```

để trả kết quả ra ngoài loop.

---

# 28. Ví dụ — Worker

Hãy xây worker đơn giản:

```rust
#[derive(Debug)]
enum WorkerCommand {
    Process(u32),
    Stop,
}

fn main() {
    let commands = vec![
        WorkerCommand::Process(1),
        WorkerCommand::Process(2),
        WorkerCommand::Process(3),
        WorkerCommand::Stop,
        WorkerCommand::Process(4),
    ];

    for command in commands {
        match command {
            WorkerCommand::Process(id) => {
                println!("Processing task {id}");
            }

            WorkerCommand::Stop => {
                println!("Worker stopped");
                break;
            }
        }
    }
}
```

Output:

```text
Processing task 1
Processing task 2
Processing task 3
Worker stopped
```

Task `4` không được xử lý.

---

# 29. Ví dụ — Skip invalid task

```rust
#[derive(Debug)]
struct Task {
    id: u32,
    valid: bool,
}

fn main() {
    let tasks = vec![
        Task {
            id: 1,
            valid: true,
        },
        Task {
            id: 2,
            valid: false,
        },
        Task {
            id: 3,
            valid: true,
        },
    ];

    for task in tasks {
        if !task.valid {
            continue;
        }

        println!("Processing task {}", task.id);
    }
}
```

Output:

```text
Processing task 1
Processing task 3
```

---

# 30. `continue` là "guard"

Một cách viết rất đẹp:

```rust
for task in tasks {
    if !task.valid {
        continue;
    }

    process(task);
}
```

Thay vì:

```rust
for task in tasks {
    if task.valid {
        process(task);
    }
}
```

Hai cách đều đúng.

Nhưng khi logic xử lý phức tạp:

```rust
for task in tasks {
    if task.cancelled {
        continue;
    }

    if task.invalid {
        continue;
    }

    if task.expired {
        continue;
    }

    process(task);
}
```

`continue` tạo ra một dạng **guard clause** rất rõ ràng.

---

# 31. `break` cũng có thể là guard

Ví dụ:

```rust
for task in tasks {
    if task.is_shutdown {
        break;
    }

    process(task);
}
```

Ý nghĩa:

> Nếu nhận shutdown signal thì dừng worker.

Đây là pattern rất thực tế.

---

# 32. Complete Example — Crawler Worker

Hãy kết hợp toàn bộ kiến thức:

```rust
use std::collections::VecDeque;

#[derive(Debug)]
enum CrawlTask {
    DownloadChapter {
        story_id: u32,
        chapter: u32,
    },

    DownloadImage {
        url: String,
    },

    Stop,
}

fn main() {
    let mut queue = VecDeque::new();

    queue.push_back(CrawlTask::DownloadChapter {
        story_id: 1,
        chapter: 1,
    });

    queue.push_back(CrawlTask::DownloadImage {
        url: String::from("https://example.com/image.jpg"),
    });

    queue.push_back(CrawlTask::DownloadChapter {
        story_id: 1,
        chapter: 2,
    });

    queue.push_back(CrawlTask::Stop);

    queue.push_back(CrawlTask::DownloadChapter {
        story_id: 1,
        chapter: 3,
    });

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

            CrawlTask::Stop => {
                println!("Worker stopping...");
                break;
            }
        }
    }

    println!("Worker finished.");
}
```

Output:

```text
Download story=1, chapter=1
Download image: https://example.com/image.jpg
Download story=1, chapter=2
Worker stopping...
Worker finished.
```

Đây là một ví dụ rất tốt để ghi nhớ:

```text
VecDeque
   ↓
while let
   ↓
match
   ↓
break
```

---

# 33. `loop` + `break value` — Pattern cực kỳ quan trọng

Hãy học kỹ pattern này:

```rust
let result = loop {
    match operation() {
        Ok(value) => break Ok(value),

        Err(error) => {
            if should_stop() {
                break Err(error);
            }
        }
    }
};
```

Ý tưởng:

```text
loop
 │
 ├── operation
 │
 ├── Ok
 │    └── break Ok(value)
 │
 └── Err
      └── break Err(error)
```

Kết quả của cả `loop` là:

```rust
Result<T, E>
```

Đây là pattern sẽ rất hữu ích khi bạn học:

```text
Result
Error Handling
Iterator
async
Tokio
```

---

# 34. `break` phải trả cùng kiểu

Ví dụ:

```rust
let result = loop {
    if condition() {
        break 10;
    }

    break 20;
};
```

Cả hai:

```text
i32
```

→ hợp lệ.

Nhưng:

```rust
let result = loop {
    if condition() {
        break 10;
    }

    break "hello";
};
```

sẽ lỗi.

Vì:

```text
break 10
→ i32

break "hello"
→ &str
```

Rust yêu cầu một expression có một kiểu nhất quán.

---

# 35. `break` không phải `return`

Đây là điểm rất quan trọng.

```rust
fn example() {
    loop {
        break;
    }

    println!("After loop");
}
```

`break`:

```text
thoát loop
```

nhưng function vẫn tiếp tục.

Trong khi:

```rust
fn example() {
    loop {
        return;
    }

    println!("After loop");
}
```

`return`:

```text
thoát function
```

Mental model:

```text
break
  ↓
loop


return
  ↓
function
```

---

# 36. `continue` không phải `break`

```text
continue
    ↓
iteration hiện tại kết thúc
    ↓
iteration tiếp theo


break
    ↓
loop kết thúc
```

Ví dụ:

```rust
for i in 1..=5 {
    if i == 2 {
        continue;
    }

    if i == 4 {
        break;
    }

    println!("{i}");
}
```

Output:

```text
1
3
```

---

# 37. Bài tập 1 — `break`

Viết:

```rust
fn main() {
    for i in 1..=100 {
        // dừng khi i == 10
    }
}
```

Kết quả:

```text
1
2
3
...
9
```

---

# 38. Bài tập 2 — `continue`

In các số từ `1..=20`, nhưng bỏ qua số chia hết cho `3`.

Kết quả không được chứa:

```text
3
6
9
12
15
18
```

Bắt buộc dùng:

```rust
continue;
```

---

# 39. Bài tập 3 — `loop` trả giá trị

Viết:

```rust
let result = loop {
    // ...
};
```

sao cho kết quả là:

```text
100
```

bằng:

```rust
break 100;
```

---

# 40. Bài tập 4 — Countdown

Viết:

```rust
let mut number = 10;

loop {
    // in number
    // giảm number
    // khi number == 0 thì break
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

---

# 41. Bài tập 5 — Skip task

Cho:

```rust
struct Task {
    id: u32,
    valid: bool,
}
```

Tạo 5 task.

Dùng:

```rust
continue
```

để bỏ qua task không hợp lệ.

---

# 42. Bài tập 6 — Stop worker

Tạo:

```rust
enum Command {
    Process(u32),
    Stop,
}
```

Cho:

```text
Process(1)
Process(2)
Process(3)
Stop
Process(4)
```

Dùng:

```rust
break
```

để task `4` không được xử lý.

---

# 43. Challenge — Retry

Viết function:

```rust
fn operation(attempt: u32) -> Result<String, String>
```

Quy tắc:

```text
attempt < 3
→ Err("Temporary error")

attempt >= 3
→ Ok("Success")
```

Sau đó viết:

```rust
let result = loop {
    ...
};
```

và thử tối đa 5 lần.

Nếu thành công:

```text
Success
```

Nếu thất bại sau 5 lần:

```text
Failed after 5 attempts
```

Bắt buộc dùng:

```rust
break Ok(...)
break Err(...)
```

---

# 44. Challenge lớn — Crawler Worker

Xây:

```rust
enum CrawlTask {
    Chapter(u32),
    Image(String),
    Invalid,
    Stop,
}
```

Queue:

```text
Chapter(1)
Invalid
Image(...)
Chapter(2)
Invalid
Stop
Chapter(3)
```

Yêu cầu:

```text
Chapter
→ process

Image
→ process

Invalid
→ continue

Stop
→ break
```

Flow:

```text
Queue
  │
  ▼
while let Some(task)
  │
  ▼
match task
  │
  ├── Chapter → process
  ├── Image   → process
  ├── Invalid → continue
  └── Stop    → break
```

Đây là bài tập tổng hợp rất quan trọng.

---

# 45. Kiến thức cốt lõi của Buổi 18

Bạn cần phân biệt chính xác:

| Keyword    | Tác dụng                 |
| ---------- | ------------------------ |
| `break`    | Thoát loop               |
| `continue` | Sang iteration tiếp theo |
| `return`   | Thoát function           |

Và đặc biệt:

```rust
let result = loop {
    break value;
};
```

`loop` có thể trả về giá trị.

---

# 46. Mental Model

Hãy ghi nhớ:

```text
             LOOP
               │
       ┌───────┴────────┐
       │                │
   continue           break
       │                │
       ▼                ▼
next iteration      exit loop
                        │
                        ▼
                  optional value
```

Ví dụ:

```rust
let result = loop {
    if success {
        break Ok(value);
    }

    if fatal_error {
        break Err(error);
    }

    continue;
};
```

Đây là một pattern cực kỳ mạnh trong Rust.

---

# Roadmap tiếp theo

```text
Buổi 11 → if
Buổi 12 → loop
Buổi 13 → while
Buổi 14 → for
Buổi 15 → match
Buổi 16 → if let
Buổi 17 → while let
Buổi 18 → break & continue       ← hôm nay
Buổi 19 → Labels
Buổi 20 → Mini Project
```

**Buổi 19 — Labels** sẽ giải quyết một vấn đề chúng ta vừa chạm tới: khi có **nested loop**, `break`/`continue` mặc định chỉ tác động đến vòng lặp gần nhất. Chúng ta sẽ học `'outer`, `break 'outer`, `continue 'outer` và đặc biệt là **label + `break value`**.
