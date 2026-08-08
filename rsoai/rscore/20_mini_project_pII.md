# Rust — Buổi 20

# Mini Project: Crawler Task Manager

Hôm nay chúng ta **không học thêm cú pháp mới là chính**. Mục tiêu là ghép toàn bộ kiến thức Control Flow của Buổi 11–19 thành một chương trình Rust hoàn chỉnh.

Project hôm nay sẽ mô phỏng một **Crawler Task Manager**:

```text
Task Queue
    │
    ▼
Worker
    │
    ├── CrawlStory
    ├── CrawlChapter
    ├── Skip
    └── Shutdown
```

Bạn sẽ sử dụng:

```text
if
loop
while
for
match
if let
while let
break
continue
labels
enum
struct
VecDeque
Option
Result
```

---

# 1. Mục tiêu project

Sau buổi này, bạn sẽ có một chương trình:

```text
┌──────────────────────────────┐
│     CRAWLER TASK MANAGER     │
├──────────────────────────────┤
│ Task Queue                   │
│                              │
│ 1. Crawl Story               │
│ 2. Crawl Chapter             │
│ 3. Invalid Task              │
│ 4. Shutdown                  │
└──────────────┬───────────────┘
               │
               ▼
           Worker Loop
               │
       ┌───────┼────────┐
       ▼       ▼        ▼
    Process   Skip    Shutdown
```

Đây chưa phải crawler HTTP thật.

Mục đích là xây **control-flow engine** trước.

Sau này khi học:

```text
Ownership
Borrowing
Struct
Trait
Error Handling
Iterator
Async
Tokio
```

chúng ta có thể nâng project này thành crawler thật.

---

# 2. Tạo project

Chạy:

```bash
cargo new crawler_task_manager
cd crawler_task_manager
```

Chạy thử:

```bash
cargo run
```

Bạn sẽ thấy:

```text
Hello, world!
```

Mở:

```text
src/main.rs
```

và thay toàn bộ nội dung bằng code bên dưới.

---

# 3. Thiết kế domain

Đầu tiên chúng ta cần Task.

```rust
#[derive(Debug)]
enum CrawlTask {
    CrawlStory {
        story_id: u32,
    },

    CrawlChapter {
        story_id: u32,
        chapter: u32,
    },

    Invalid,

    Shutdown,
}
```

Có 4 loại task:

```text
CrawlStory
CrawlChapter
Invalid
Shutdown
```

---

# 4. Vì sao dùng `enum`?

Đây là một task có thể có nhiều trạng thái/type.

Thay vì:

```rust
struct Task {
    task_type: String,
    story_id: Option<u32>,
    chapter: Option<u32>,
}
```

ta dùng:

```rust
enum CrawlTask {
    CrawlStory {
        story_id: u32,
    },

    CrawlChapter {
        story_id: u32,
        chapter: u32,
    },

    Invalid,

    Shutdown,
}
```

Rust đảm bảo dữ liệu đi cùng variant.

Ví dụ:

```rust
CrawlTask::CrawlChapter {
    story_id: 10,
    chapter: 5,
}
```

rất rõ ràng.

---

# 5. Tạo Queue

Dùng:

```rust
use std::collections::VecDeque;
```

`VecDeque` rất phù hợp cho queue:

```text
push_back()
pop_front()
```

Ví dụ:

```rust
let mut queue = VecDeque::new();

queue.push_back(1);
queue.push_back(2);
queue.push_back(3);
```

Queue:

```text
Front
  ↓
[1] [2] [3]
```

`pop_front()`:

```text
1
```

Queue còn:

```text
[2] [3]
```

---

# 6. Tạo task queue

```rust
let mut queue = VecDeque::new();

queue.push_back(CrawlTask::CrawlStory {
    story_id: 1,
});

queue.push_back(CrawlTask::CrawlChapter {
    story_id: 1,
    chapter: 1,
});

queue.push_back(CrawlTask::Invalid);

queue.push_back(CrawlTask::CrawlChapter {
    story_id: 1,
    chapter: 2,
});

queue.push_back(CrawlTask::Shutdown);

queue.push_back(CrawlTask::CrawlChapter {
    story_id: 1,
    chapter: 3,
});
```

Queue:

```text
┌─────────────┐
│ CrawlStory  │
├─────────────┤
│ Chapter 1   │
├─────────────┤
│ Invalid     │
├─────────────┤
│ Chapter 2   │
├─────────────┤
│ Shutdown    │
├─────────────┤
│ Chapter 3   │
└─────────────┘
```

---

# 7. Worker loop

Bây giờ chúng ta cần worker.

Pattern:

```rust
while let Some(task) = queue.pop_front() {
    ...
}
```

Đây chính là kiến thức Buổi 17.

Code:

```rust
while let Some(task) = queue.pop_front() {
    println!("Received task: {task:?}");
}
```

Worker sẽ chạy cho đến khi:

```rust
queue.pop_front()
```

trả về:

```rust
None
```

---

# 8. Xử lý bằng `match`

Bây giờ:

```rust
while let Some(task) = queue.pop_front() {
    match task {
        CrawlTask::CrawlStory { story_id } => {
            println!("Crawling story {story_id}");
        }

        CrawlTask::CrawlChapter {
            story_id,
            chapter,
        } => {
            println!(
                "Crawling story {story_id}, chapter {chapter}"
            );
        }

        CrawlTask::Invalid => {
            println!("Invalid task");
        }

        CrawlTask::Shutdown => {
            println!("Shutdown requested");
            break;
        }
    }
}
```

Đây là core của project.

---

# 9. Tại sao `break`?

Khi:

```rust
CrawlTask::Shutdown
```

được nhận:

```rust
break;
```

→ worker dừng.

Task phía sau:

```text
Chapter 3
```

không được xử lý.

---

# 10. Thêm `continue`

Task invalid:

```rust
CrawlTask::Invalid => {
    println!("Invalid task");
    continue;
}
```

`continue` sẽ bỏ qua phần còn lại của iteration.

Trong project này:

```rust
CrawlTask::Invalid => {
    println!("Invalid task");
    continue;
}
```

về mặt behavior chưa khác nhiều so với bỏ cuối branch, nhưng nó rất hữu ích khi branch có nhiều logic phía sau.

---

# 11. Thêm function `process_story`

Tách logic:

```rust
fn process_story(story_id: u32) {
    println!("Processing story {story_id}");
}
```

Chapter:

```rust
fn process_chapter(story_id: u32, chapter: u32) {
    println!(
        "Processing story {story_id}, chapter {chapter}"
    );
}
```

---

# 12. Complete version 1

```rust
use std::collections::VecDeque;

#[derive(Debug)]
enum CrawlTask {
    CrawlStory {
        story_id: u32,
    },

    CrawlChapter {
        story_id: u32,
        chapter: u32,
    },

    Invalid,

    Shutdown,
}

fn process_story(story_id: u32) {
    println!("Processing story {story_id}");
}

fn process_chapter(story_id: u32, chapter: u32) {
    println!(
        "Processing story {story_id}, chapter {chapter}"
    );
}

fn main() {
    let mut queue = VecDeque::new();

    queue.push_back(CrawlTask::CrawlStory {
        story_id: 1,
    });

    queue.push_back(CrawlTask::CrawlChapter {
        story_id: 1,
        chapter: 1,
    });

    queue.push_back(CrawlTask::Invalid);

    queue.push_back(CrawlTask::CrawlChapter {
        story_id: 1,
        chapter: 2,
    });

    queue.push_back(CrawlTask::Shutdown);

    queue.push_back(CrawlTask::CrawlChapter {
        story_id: 1,
        chapter: 3,
    });

    while let Some(task) = queue.pop_front() {
        match task {
            CrawlTask::CrawlStory { story_id } => {
                process_story(story_id);
            }

            CrawlTask::CrawlChapter {
                story_id,
                chapter,
            } => {
                process_chapter(story_id, chapter);
            }

            CrawlTask::Invalid => {
                println!("Invalid task");
                continue;
            }

            CrawlTask::Shutdown => {
                println!("Shutdown requested");
                break;
            }
        }
    }

    println!("Worker stopped.");
}
```

---

# 13. Chạy project

```bash
cargo run
```

Output:

```text
Processing story 1
Processing story 1, chapter 1
Invalid task
Processing story 1, chapter 2
Shutdown requested
Worker stopped.
```

Chú ý:

```text
Chapter 3
```

không xuất hiện.

Vì:

```rust
break;
```

đã dừng worker.

---

# 14. Thêm `Result`

Crawler thực tế chắc chắn có lỗi.

Ví dụ:

```rust
fn process_chapter(
    story_id: u32,
    chapter: u32,
) -> Result<(), String> {
    if chapter == 2 {
        return Err(String::from("Failed to download chapter"));
    }

    println!(
        "Processing story {story_id}, chapter {chapter}"
    );

    Ok(())
}
```

Bây giờ function có thể:

```text
Ok(())
```

hoặc:

```text
Err(...)
```

---

# 15. Xử lý Result bằng `match`

```rust
match process_chapter(story_id, chapter) {
    Ok(()) => {
        println!("Chapter completed");
    }

    Err(error) => {
        println!("Chapter failed: {error}");
    }
}
```

---

# 16. Tại sao `Result` rất phù hợp crawler?

Crawler có thể gặp:

```text
HTTP error
Network error
Timeout
Invalid HTML
Missing chapter
Invalid URL
Database error
```

Thay vì:

```rust
panic!
```

ta có:

```rust
Result<T, E>
```

Sau này khi học error handling chúng ta sẽ đi rất sâu vào phần này.

---

# 17. Thêm retry

Bây giờ project bắt đầu thú vị.

Giả sử chapter có thể fail.

Ta muốn:

```text
attempt 1
   ↓
fail
   ↓
attempt 2
   ↓
fail
   ↓
attempt 3
   ↓
success
```

Dùng:

```rust
loop
```

---

# 18. Hàm retry

```rust
fn download_chapter(
    story_id: u32,
    chapter: u32,
) -> Result<String, String> {
    let mut attempts = 0;

    loop {
        attempts += 1;

        println!(
            "Downloading story {story_id}, chapter {chapter}, attempt {attempts}"
        );

        if attempts == 3 {
            break Ok(format!(
                "Chapter {chapter} downloaded"
            ));
        }

        if attempts >= 5 {
            break Err(String::from("Maximum retries reached"));
        }
    }
}
```

Nhưng ví dụ này hơi kỳ vì luôn thành công ở lần 3.

Hãy biến nó thành logic có thể thay đổi.

---

# 19. Tách operation

```rust
fn attempt_download(
    chapter: u32,
    attempt: u32,
) -> Result<String, String> {
    if chapter == 1 && attempt < 3 {
        return Err(String::from("Temporary network error"));
    }

    Ok(format!("Chapter {chapter} downloaded"))
}
```

Bây giờ:

```text
chapter 1
attempt 1 → Err
attempt 2 → Err
attempt 3 → Ok
```

---

# 20. Retry function hoàn chỉnh

```rust
fn download_with_retry(
    chapter: u32,
    max_attempts: u32,
) -> Result<String, String> {
    let mut attempts = 0;

    loop {
        attempts += 1;

        match attempt_download(chapter, attempts) {
            Ok(value) => {
                break Ok(value);
            }

            Err(error) => {
                println!(
                    "Attempt {attempts} failed: {error}"
                );

                if attempts >= max_attempts {
                    break Err(error);
                }
            }
        }
    }
}
```

Đây là pattern cực kỳ quan trọng:

```rust
loop {
    match operation() {
        Ok(value) => break Ok(value),

        Err(error) => {
            if should_stop {
                break Err(error);
            }
        }
    }
}
```

---

# 21. Test retry

```rust
fn main() {
    match download_with_retry(1, 5) {
        Ok(message) => {
            println!("{message}");
        }

        Err(error) => {
            println!("Download failed: {error}");
        }
    }
}
```

Output:

```text
Attempt 1 failed: Temporary network error
Attempt 2 failed: Temporary network error
Chapter 1 downloaded
```

---

# 22. Kết hợp với Worker

Bây giờ:

```rust
CrawlChapter
```

không chỉ:

```rust
println!
```

mà sẽ:

```text
download
   ↓
retry
   ↓
Result
   ↓
worker xử lý
```

---

# 23. Complete Project

Đây là phiên bản hoàn chỉnh bạn nên copy vào:

```text
src/main.rs
```

```rust
use std::collections::VecDeque;

#[derive(Debug)]
enum CrawlTask {
    CrawlStory {
        story_id: u32,
    },

    CrawlChapter {
        story_id: u32,
        chapter: u32,
    },

    Invalid,

    Shutdown,
}

fn process_story(story_id: u32) {
    println!("Processing story {story_id}");
}

fn attempt_download(
    chapter: u32,
    attempt: u32,
) -> Result<String, String> {
    if chapter == 1 && attempt < 3 {
        return Err(String::from(
            "Temporary network error",
        ));
    }

    Ok(format!(
        "Chapter {chapter} downloaded"
    ))
}

fn download_with_retry(
    chapter: u32,
    max_attempts: u32,
) -> Result<String, String> {
    let mut attempts = 0;

    loop {
        attempts += 1;

        println!(
            "Download chapter {chapter}, attempt {attempts}"
        );

        match attempt_download(chapter, attempts) {
            Ok(value) => {
                break Ok(value);
            }

            Err(error) => {
                println!("Failed: {error}");

                if attempts >= max_attempts {
                    break Err(error);
                }
            }
        }
    }
}

fn process_chapter(
    story_id: u32,
    chapter: u32,
) -> Result<(), String> {
    println!(
        "Processing story {story_id}, chapter {chapter}"
    );

    let result = download_with_retry(chapter, 3)?;

    println!("{result}");

    Ok(())
}

fn main() {
    let mut queue = VecDeque::new();

    queue.push_back(CrawlTask::CrawlStory {
        story_id: 1,
    });

    queue.push_back(CrawlTask::CrawlChapter {
        story_id: 1,
        chapter: 1,
    });

    queue.push_back(CrawlTask::Invalid);

    queue.push_back(CrawlTask::CrawlChapter {
        story_id: 1,
        chapter: 2,
    });

    queue.push_back(CrawlTask::Shutdown);

    queue.push_back(CrawlTask::CrawlChapter {
        story_id: 1,
        chapter: 3,
    });

    'worker: while let Some(task) = queue.pop_front() {
        match task {
            CrawlTask::CrawlStory { story_id } => {
                process_story(story_id);
            }

            CrawlTask::CrawlChapter {
                story_id,
                chapter,
            } => {
                match process_chapter(story_id, chapter) {
                    Ok(()) => {
                        println!("Chapter completed");
                    }

                    Err(error) => {
                        println!(
                            "Chapter failed: {error}"
                        );
                    }
                }
            }

            CrawlTask::Invalid => {
                println!("Invalid task");
                continue 'worker;
            }

            CrawlTask::Shutdown => {
                println!("Shutdown requested");
                break 'worker;
            }
        }
    }

    println!("Worker stopped.");
}
```

---

# 24. Có một chi tiết rất quan trọng

Ở đây:

```rust
'worker: while let Some(task) = queue.pop_front() {
```

chúng ta đặt label:

```rust
'worker:
```

Sau đó:

```rust
break 'worker;
```

và:

```rust
continue 'worker;
```

Như vậy toàn bộ worker loop có tên:

```text
worker
```

---

# 25. Flow của chương trình

```text
                 VecDeque
                    │
                    ▼
          pop_front()
                    │
                    ▼
             while let Some
                    │
                    ▼
                  match
          ┌─────────┼──────────┐
          │         │          │
       Story      Chapter    Invalid
          │         │          │
          ▼         ▼          ▼
       process    retry    continue
                             │
                             ▼
                        next task

                    Shutdown
                        │
                        ▼
                   break worker
                        │
                        ▼
                  Worker stopped
```

Đây chính là toàn bộ kiến thức Control Flow mà chúng ta đã học.

---

# 26. `?` xuất hiện ở đâu?

Trong:

```rust
let result = download_with_retry(chapter, 3)?;
```

`?` có nghĩa:

```text
Ok(value)
   ↓
lấy value

Err(error)
   ↓
return Err(error)
```

Ở đây:

```rust
process_chapter()
```

có:

```rust
Result<(), String>
```

nên có thể dùng `?`.

Chúng ta sẽ học `?` thật kỹ trong phần **Error Handling**.

---

# 27. Thêm trạng thái Worker

Bây giờ nâng cấp một chút.

```rust
enum WorkerState {
    Running,
    Stopped,
}
```

Trong `main`:

```rust
let mut state = WorkerState::Running;
```

Khi shutdown:

```rust
state = WorkerState::Stopped;
break 'worker;
```

Sau loop:

```rust
match state {
    WorkerState::Running => {
        println!("Worker is still running");
    }

    WorkerState::Stopped => {
        println!("Worker stopped");
    }
}
```

Đây là cách `enum + match` bắt đầu trở thành **state machine**.

---

# 28. Mini State Machine

Bạn có thể hình dung:

```text
        ┌─────────┐
        │ RUNNING │
        └────┬────┘
             │
        Shutdown
             │
             ▼
        ┌─────────┐
        │ STOPPED │
        └─────────┘
```

Rust `enum` cực kỳ phù hợp để mô hình hóa những trạng thái như thế này.

Sau này đây sẽ là nền tảng để học:

```text
Trait
State Pattern
Async State Machine
Tokio
Actor Model
```

---

# 29. Thêm command `Pause`

Thử tự mở rộng:

```rust
enum CrawlTask {
    CrawlStory {
        story_id: u32,
    },

    CrawlChapter {
        story_id: u32,
        chapter: u32,
    },

    Invalid,

    Pause,

    Shutdown,
}
```

Khi:

```rust
CrawlTask::Pause
```

in:

```text
Worker paused.
```

Sau đó tiếp tục task tiếp theo.

Đây là lúc bạn sẽ thấy:

```rust
continue
```

có ý nghĩa.

---

# 30. Bài tập mở rộng 1 — Pause

Thêm:

```rust
Pause
```

và xử lý:

```rust
CrawlTask::Pause => {
    println!("Worker paused");
    continue 'worker;
}
```

---

# 31. Bài tập mở rộng 2 — Cancel Story

Thêm:

```rust
CancelStory {
    story_id: u32,
}
```

Nếu worker đang xử lý một story:

```text
Story 1
 ├── Chapter 1
 ├── Chapter 2
 ├── Cancel
 └── ...
```

hãy dùng:

```rust
continue 'story;
```

để chuyển sang story tiếp theo.

Đây sẽ là bài tập chuẩn bị cho:

```text
nested loop
+
labels
```

---

# 32. Bài tập mở rộng 3 — Tìm chapter

Viết:

```rust
fn find_chapter(
    stories: &[Story],
    target: u32,
) -> Option<&Chapter>
```

Sử dụng:

```rust
'search: {
    ...
}
```

và:

```rust
break 'search Some(chapter);
```

Nếu không tìm thấy:

```rust
None
```

Đây là bài tập rất quan trọng vì nó kết hợp:

```text
nested loop
label
break value
Option
match
```

---

# 33. Bài tập mở rộng 4 — Maximum Retry

Cho:

```rust
download_with_retry(
    chapter,
    max_attempts,
)
```

Yêu cầu:

```text
attempt 1
attempt 2
attempt 3
...
```

Không được vượt quá:

```text
max_attempts
```

Nếu thất bại:

```text
Download failed after N attempts
```

Nếu thành công:

```text
Download successful
```

---

# 34. Bài tập mở rộng 5 — Queue Statistics

Thêm:

```rust
struct WorkerStats {
    processed: u32,
    failed: u32,
    skipped: u32,
}
```

Mỗi task:

```text
Success → processed += 1
Error   → failed += 1
Invalid → skipped += 1
```

Cuối chương trình:

```text
========== STATISTICS ==========
Processed: 4
Failed:    1
Skipped:   2
================================
```

Đây là bước đầu tiên để biến mini project thành một application thực tế.

---

# 35. Bài tập lớn cuối Buổi 20

Hãy tự xây phiên bản **Crawler Task Manager v2** với:

```text
CrawlTask
 ├── CrawlStory
 ├── CrawlChapter
 ├── Pause
 ├── Invalid
 └── Shutdown
```

Có:

```text
VecDeque
    ↓
Worker
    ↓
while let
    ↓
match
    ↓
process
    ↓
Result
    ↓
retry
```

và:

```text
'worker
'story
```

để quản lý nested control flow.

Cuối cùng in:

```text
================================
       CRAWLER STATISTICS
================================
Processed : X
Failed    : X
Skipped   : X
Retries   : X
================================
Worker stopped.
```

---

# 36. Tổng kết toàn bộ Phần II

Bạn vừa hoàn thành:

```text
                 CONTROL FLOW
                      │
       ┌──────────────┼──────────────┐
       │              │              │
       ▼              ▼              ▼
      if            loops          match
                      │
          ┌───────────┼───────────┐
          │           │           │
         loop        while        for
          │           │           │
          ├───────────┼───────────┤
          │
       break
       continue
          │
        labels
          │
    break 'label
    continue 'label
```

Và Mini Project:

```text
enum
  ↓
VecDeque
  ↓
while let
  ↓
match
  ↓
loop
  ↓
break
  ↓
continue
  ↓
labels
  ↓
Result
  ↓
retry
```

Đây là một nền tảng rất tốt để bước sang phần tiếp theo.

---

# 37. Một nguyên tắc kiến trúc quan trọng

Qua project này, hãy bắt đầu hình thành tư duy:

> **Control Flow không chỉ là cú pháp; nó là cách mô hình hóa trạng thái và hành vi của chương trình.**

Ví dụ:

```rust
enum CrawlTask
```

mô hình hóa **task**.

```rust
enum WorkerState
```

mô hình hóa **state**.

```rust
Result<T, E>
```

mô hình hóa **success/failure**.

```rust
loop
```

mô hình hóa **worker lifecycle**.

```rust
break 'worker
```

mô hình hóa **shutdown**.

Đây chính là tư duy sẽ rất hữu ích khi sau này bạn xây crawler framework Rust thật.

---

# 38. Bạn đã hoàn thành Phase II

```text
Phase II — Control Flow

✓ Buổi 11 — if
✓ Buổi 12 — loop
✓ Buổi 13 — while
✓ Buổi 14 — for
✓ Buổi 15 — match
✓ Buổi 16 — if let
✓ Buổi 17 — while let
✓ Buổi 18 — break & continue
✓ Buổi 19 — Labels
✓ Buổi 20 — Mini Project
```

**Phần tiếp theo nên đi vào `Functions & Ownership`, thay vì nhảy ngay vào OOP.** Đây là điểm đặc biệt quan trọng trong Rust: trước khi học struct/trait theo kiểu thiết kế framework, chúng ta cần xây thật chắc **function → expression → ownership → borrowing → references → slices → lifetime cơ bản**. Sau đó mới tiến tới `struct`, `impl`, `trait` và architecture.
