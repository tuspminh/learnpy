# Rust — Phần II: Control Flow

# Buổi 19 — Labels

Hôm nay chúng ta học **Labels — nhãn cho vòng lặp**.

Đây là phần nhỏ về cú pháp nhưng rất quan trọng để hiểu sâu control flow của Rust, đặc biệt khi bạn có:

* nested loop;
* `break` nhiều tầng;
* `continue` nhiều tầng;
* `loop` lồng nhau;
* `break` trả về giá trị;
* crawler worker;
* parser;
* state machine.

---

# 1. Vấn đề của nested loop

Ví dụ:

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

Tại:

```rust
if j == 2 {
    break;
}
```

`break` chỉ thoát:

```text
inner loop
```

Không thoát:

```text
outer loop
```

---

# 2. Labels giải quyết vấn đề này

Rust cho phép đặt tên cho loop:

```rust
'outer: for i in 1..=3 {
    ...
}
```

Sau đó:

```rust
break 'outer;
```

có nghĩa:

> Thoát khỏi vòng lặp có label `'outer`.

---

# 3. Cú pháp

Label có dạng:

```rust
'label_name:
```

Ví dụ:

```rust
'outer:
```

Sau đó đặt trước loop:

```rust
'outer: loop {
    ...
}
```

hoặc:

```rust
'outer: for i in 1..=10 {
    ...
}
```

hoặc:

```rust
'outer: while condition {
    ...
}
```

---

# 4. Ví dụ cơ bản

```rust
fn main() {
    'outer: for i in 1..=3 {
        for j in 1..=3 {
            if j == 2 {
                break 'outer;
            }

            println!("i={i}, j={j}");
        }
    }

    println!("Done");
}
```

Output:

```text
i=1, j=1
Done
```

Flow:

```text
'outer
  │
  ├── i=1
  │    ├── j=1 → print
  │    └── j=2 → break 'outer
  │
  ▼
exit outer loop
```

---

# 5. Label bắt đầu bằng `'`

Đây là điểm cần nhớ.

Label:

```rust
'outer
```

khác với string:

```rust
"outer"
```

và khác variable:

```rust
outer
```

Cú pháp:

```rust
'label_name:
```

Ví dụ:

```rust
'search:
```

```rust
'outer:
```

```rust
'worker:
```

---

# 6. Label không phải lifetime

Bạn sẽ thấy Rust có cú pháp:

```rust
'a
```

trong lifetime.

Ví dụ sau này:

```rust
fn foo<'a>(value: &'a str) -> &'a str {
    value
}
```

Đó là **lifetime**.

Còn:

```rust
'outer: loop {
    ...
}
```

là **loop label**.

Chúng sử dụng cú pháp tương tự vì đều là lifetime-style labels trong Rust grammar, nhưng mục đích hoàn toàn khác nhau.

Ở bài hôm nay, hãy tập trung vào:

```rust
'label:
```

để điều khiển loop.

---

# 7. `break 'label`

Ví dụ:

```rust
fn main() {
    'outer: for i in 1..=5 {
        for j in 1..=5 {
            if i * j > 6 {
                break 'outer;
            }

            println!("i={i}, j={j}");
        }
    }
}
```

Khi:

```text
i * j > 6
```

thì:

```rust
break 'outer;
```

thoát toàn bộ outer loop.

---

# 8. `break` thường vs `break 'label`

### Không có label

```rust
for i in 1..=3 {
    for j in 1..=3 {
        break;
    }
}
```

`break`:

```text
→ inner loop
```

### Có label

```rust
'outer: for i in 1..=3 {
    for j in 1..=3 {
        break 'outer;
    }
}
```

`break 'outer`:

```text
→ outer loop
```

---

# 9. `continue 'label`

Labels không chỉ dùng với `break`.

Bạn cũng có:

```rust
continue 'outer;
```

Ví dụ:

```rust
fn main() {
    'outer: for i in 1..=3 {
        for j in 1..=3 {
            if j == 2 {
                continue 'outer;
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

Khi:

```text
j == 2
```

thay vì:

```text
continue inner
```

ta:

```rust
continue 'outer;
```

→ bỏ toàn bộ iteration hiện tại của outer loop.

---

# 10. Phân biệt `continue` và `continue 'outer`

Không label:

```rust
for i in 1..=3 {
    for j in 1..=3 {
        if j == 2 {
            continue;
        }
    }
}
```

→ tiếp tục `inner loop`.

Có label:

```rust
'outer: for i in 1..=3 {
    for j in 1..=3 {
        if j == 2 {
            continue 'outer;
        }
    }
}
```

→ tiếp tục `outer loop`.

---

# 11. Visualize

Không label:

```text
outer
 │
 ├── inner
 │    ├── j=1
 │    ├── j=2 → continue
 │    └── j=3
 │
 └── next outer
```

Có:

```rust
continue 'outer;
```

thì:

```text
outer
 │
 ├── inner
 │    ├── j=1
 │    └── j=2
 │          │
 │          ▼
 │      continue outer
 │
 ▼
next outer
```

---

# 12. Nested `loop`

Labels đặc biệt hữu ích với `loop`.

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

`break 'outer` thoát luôn loop bên ngoài.

---

# 13. Ba tầng loop

Rust có thể xử lý nhiều tầng.

```rust
fn main() {
    'outer: for a in 1..=3 {
        for b in 1..=3 {
            for c in 1..=3 {
                if a == 2 && b == 2 && c == 2 {
                    break 'outer;
                }

                println!("{a} {b} {c}");
            }
        }
    }

    println!("Finished");
}
```

Khi:

```text
a=2
b=2
c=2
```

thì:

```rust
break 'outer;
```

thoát cả ba tầng.

---

# 14. Tại sao labels quan trọng?

Giả sử:

```text
outer loop
    │
    ├── middle loop
    │      │
    │      └── inner loop
    │
```

Nếu dùng:

```rust
break;
```

chỉ thoát:

```text
inner
```

Nếu muốn thoát:

```text
outer
```

thì phải có:

```rust
break 'outer;
```

Labels cho phép bạn nói chính xác:

> Tôi muốn điều khiển **vòng lặp nào**.

---

# 15. Label cho `while`

Labels không chỉ dành cho `for`.

```rust
fn main() {
    let mut outer_count = 0;

    'outer: while outer_count < 3 {
        let mut inner_count = 0;

        while inner_count < 3 {
            println!(
                "outer={outer_count}, inner={inner_count}"
            );

            if inner_count == 1 {
                break 'outer;
            }

            inner_count += 1;
        }

        outer_count += 1;
    }

    println!("Done");
}
```

Output:

```text
outer=0, inner=0
outer=0, inner=1
Done
```

---

# 16. Label cho `loop`

```rust
fn main() {
    'outer: loop {
        let mut count = 0;

        loop {
            count += 1;

            if count == 3 {
                break 'outer;
            }
        }
    }

    println!("Finished");
}
```

---

# 17. `continue 'outer`

Ví dụ xử lý ma trận:

```rust
fn main() {
    let matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ];

    'row: for row in matrix {
        for value in row {
            if value == 5 {
                continue 'row;
            }

            println!("{value}");
        }
    }
}
```

Output:

```text
1
2
3
4
6
7
8
9
```

Khi gặp `5`:

```rust
continue 'row;
```

→ bỏ phần còn lại của row hiện tại.

---

# 18. Đây là một use case rất hay

Giả sử:

```text
row 1 → tất cả hợp lệ
row 2 → gặp invalid
row 3 → tất cả hợp lệ
```

Ta muốn:

```text
row 1 → xử lý
row 2 → bỏ toàn bộ
row 3 → xử lý
```

Dùng:

```rust
'row: for row in matrix {
    for value in row {
        if invalid(value) {
            continue 'row;
        }

        process(value);
    }
}
```

Đây là cách dùng label rất tự nhiên.

---

# 19. Tìm kiếm trong nested loop

Một use case kinh điển:

> Tìm phần tử trong ma trận và dừng toàn bộ vòng lặp khi tìm thấy.

```rust
fn main() {
    let matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ];

    let target = 5;

    'search: for row in matrix {
        for value in row {
            if value == target {
                println!("Found {target}");
                break 'search;
            }
        }
    }
}
```

Output:

```text
Found 5
```

---

# 20. Label + `break value`

Đây là phần quan trọng nhất của bài hôm nay.

Bạn đã học:

```rust
break value;
```

trong Buổi 18.

Bây giờ kết hợp:

```rust
break 'label value;
```

Ví dụ:

```rust
fn main() {
    let result = 'search: loop {
        for number in 1..=10 {
            if number == 5 {
                break 'search number;
            }
        }

        break 'search -1;
    };

    println!("Result = {result}");
}
```

Output:

```text
Result = 5
```

---

# 21. Điều gì đang xảy ra?

Có:

```text
'search
   │
   ▼
 outer loop
   │
   └── for
        │
        ├── 1
        ├── 2
        ├── 3
        ├── 4
        └── 5
             │
             ▼
       break 'search 5
             │
             ▼
       result = 5
```

Đây là một kỹ thuật rất mạnh.

---

# 22. Tìm kiếm trong matrix và trả về kết quả

Ví dụ:

```rust
fn main() {
    let matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ];

    let target = 6;

    let position = 'search: {
        for (row_index, row) in matrix.iter().enumerate() {
            for (column_index, value) in row.iter().enumerate() {
                if *value == target {
                    break 'search Some((row_index, column_index));
                }
            }
        }

        None
    };

    println!("{position:?}");
}
```

Output:

```text
Some((1, 2))
```

Ở đây `'search` không phải loop label mà là **block label**.

Đây là một khả năng rất hay của Rust:

```rust
'label: {
    ...
}
```

và:

```rust
break 'label value;
```

có thể thoát khỏi block và trả về giá trị.

---

# 23. Label không chỉ dành cho loop

Đây là điểm nâng cao.

Bạn có thể viết:

```rust
let result = 'search: {
    if condition {
        break 'search 100;
    }

    200
};
```

Nếu `condition == true`:

```text
result = 100
```

Nếu `false`:

```text
result = 200
```

Ví dụ hoàn chỉnh:

```rust
fn main() {
    let condition = true;

    let result = 'calculate: {
        if condition {
            break 'calculate 100;
        }

        200
    };

    println!("{result}");
}
```

Output:

```text
100
```

---

# 24. Vì sao block label hữu ích?

Nó cho phép tạo một scope có thể:

```text
return early
```

mà không cần:

* function;
* closure;
* nhiều biến mutable trung gian.

Ví dụ:

```rust
let value = 'compute: {
    let a = 10;
    let b = 20;

    if a < b {
        break 'compute a + b;
    }

    0
};
```

---

# 25. `break` trong block

Điều này cần nhớ:

```rust
let result = 'block: {
    break 'block 42;
};
```

Kết quả:

```text
result == 42
```

Có thể xem:

```text
'block: {
    ...
}
```

như một expression có khả năng:

```rust
break 'block value;
```

---

# 26. Label + `continue`

Với block thì không có `continue`.

`continue` chỉ áp dụng cho loop.

Ví dụ hợp lệ:

```rust
'outer: for i in 0..3 {
    ...
}
```

```rust
continue 'outer;
```

Nhưng:

```rust
'block: {
    continue 'block;
}
```

không hợp lệ vì block không phải loop.

---

# 27. Label + `break` trong crawler

Bây giờ đưa vào project crawler của bạn.

Giả sử cần tìm chapter:

```rust
struct Chapter {
    number: u32,
    title: String,
}
```

Có nhiều story:

```rust
fn main() {
    let stories = vec![
        vec![
            Chapter {
                number: 1,
                title: String::from("Start"),
            },
            Chapter {
                number: 2,
                title: String::from("Journey"),
            },
        ],
        vec![
            Chapter {
                number: 3,
                title: String::from("Return"),
            },
        ],
    ];

    let target = 3;

    'search: for story in &stories {
        for chapter in story {
            if chapter.number == target {
                println!("Found: {}", chapter.title);
                break 'search;
            }
        }
    }
}
```

Output:

```text
Found: Return
```

---

# 28. Trả về chapter tìm được

Tốt hơn nữa:

```rust
#[derive(Debug)]
struct Chapter {
    number: u32,
    title: String,
}

fn main() {
    let stories = vec![
        vec![
            Chapter {
                number: 1,
                title: String::from("Start"),
            },
            Chapter {
                number: 2,
                title: String::from("Journey"),
            },
        ],
        vec![
            Chapter {
                number: 3,
                title: String::from("Return"),
            },
        ],
    ];

    let target = 3;

    let result = 'search: {
        for story in &stories {
            for chapter in story {
                if chapter.number == target {
                    break 'search Some(chapter);
                }
            }
        }

        None
    };

    match result {
        Some(chapter) => {
            println!("Found: {}", chapter.title);
        }

        None => {
            println!("Chapter not found");
        }
    }
}
```

Output:

```text
Found: Return
```

Đây là pattern rất đáng học:

```text
nested search
     ↓
block label
     ↓
break 'search Some(value)
     ↓
Option<&Chapter>
```

---

# 29. Labels + `while let`

Có thể kết hợp tất cả:

```rust
fn main() {
    let mut stack = vec![1, 2, 3, 4, 5];

    'worker: while let Some(value) = stack.pop() {
        println!("Processing {value}");

        if value == 3 {
            println!("Stopping worker");
            break 'worker;
        }
    }

    println!("Worker finished");
}
```

Output:

```text
Processing 5
Processing 4
Processing 3
Stopping worker
Worker finished
```

---

# 30. Labels + `VecDeque`

Ví dụ:

```rust
use std::collections::VecDeque;

fn main() {
    let mut queue = VecDeque::from([
        1, 2, 3, 4, 5
    ]);

    'worker: while let Some(task) = queue.pop_front() {
        if task == 4 {
            println!("Shutdown signal");
            break 'worker;
        }

        println!("Processing task {task}");
    }
}
```

Output:

```text
Processing task 1
Processing task 2
Processing task 3
Shutdown signal
```

---

# 31. Labels trong worker thực tế

Giả sử crawler có:

```text
Worker
 │
 ├── Story
 │    │
 │    ├── Chapter
 │    │
 │    └── Image
 │
 └── shutdown
```

Bạn có thể có:

```rust
'worker: loop {
    for story in stories {
        for chapter in story.chapters {
            if shutdown_requested() {
                break 'worker;
            }

            process(chapter);
        }
    }
}
```

`break 'worker` cho phép shutdown từ rất sâu trong nested processing.

---

# 32. `continue 'worker`

Ví dụ một story bị lỗi:

```rust
'story: for story in stories {
    for chapter in &story.chapters {
        if chapter.is_invalid() {
            continue 'story;
        }

        process(chapter);
    }
}
```

Ý nghĩa:

> Nếu một chapter không hợp lệ, bỏ qua toàn bộ story hiện tại và chuyển sang story tiếp theo.

Đây là một use case thực tế của label.

---

# 33. Nested processing

Mental model:

```text
'story
 │
 ├── chapter 1
 │
 ├── chapter 2
 │
 ├── chapter 3 → invalid
 │                  │
 │                  ▼
 │            continue 'story
 │
 ▼
story tiếp theo
```

Không cần nhiều biến trạng thái.

---

# 34. Khi nào nên dùng Labels?

### Rất phù hợp khi:

```text
nested loops
```

và bạn cần:

```text
break outer
continue outer
```

Hoặc:

```text
nested search
```

và cần:

```text
return value
```

bằng:

```rust
break 'search value;
```

---

# 35. Khi nào không nên dùng?

Đừng lạm dụng label để tạo control flow quá phức tạp.

Ví dụ:

```rust
'a: loop {
    'b: loop {
        'c: loop {
            'd: loop {
                ...
            }
        }
    }
}
```

Nếu code có quá nhiều tầng, vấn đề thường nằm ở **thiết kế function** chứ không phải thiếu labels.

Có thể tách:

```rust
fn process_story(...)
fn process_chapter(...)
fn process_image(...)
```

sẽ dễ đọc hơn.

Nguyên tắc:

> Label là công cụ điều khiển flow, không phải công cụ thay thế kiến trúc tốt.

---

# 36. Complete Example — Story Search

Đây là ví dụ bạn nên tự gõ và chạy.

```rust
#[derive(Debug)]
struct Chapter {
    number: u32,
    title: String,
}

#[derive(Debug)]
struct Story {
    title: String,
    chapters: Vec<Chapter>,
}

fn find_chapter<'a>(
    stories: &'a [Story],
    target: u32,
) -> Option<&'a Chapter> {
    'search: {
        for story in stories {
            for chapter in &story.chapters {
                if chapter.number == target {
                    break 'search Some(chapter);
                }
            }
        }

        None
    }
}

fn main() {
    let stories = vec![
        Story {
            title: String::from("Rust Journey"),
            chapters: vec![
                Chapter {
                    number: 1,
                    title: String::from("Beginning"),
                },
                Chapter {
                    number: 2,
                    title: String::from("Ownership"),
                },
            ],
        },
        Story {
            title: String::from("Async Rust"),
            chapters: vec![
                Chapter {
                    number: 3,
                    title: String::from("Future"),
                },
                Chapter {
                    number: 4,
                    title: String::from("Tokio"),
                },
            ],
        },
    ];

    match find_chapter(&stories, 3) {
        Some(chapter) => {
            println!("Found chapter:");
            println!("Number: {}", chapter.number);
            println!("Title: {}", chapter.title);
        }

        None => {
            println!("Chapter not found");
        }
    }
}
```

Output:

```text
Found chapter:
Number: 3
Title: Future
```

---

# 37. Phân tích function

Function:

```rust
fn find_chapter<'a>(
    stories: &'a [Story],
    target: u32,
) -> Option<&'a Chapter>
```

đang nói:

```text
stories
   │
   ▼
for story
   │
   ▼
for chapter
   │
   ▼
target?
   │
   ├── YES → Some(&Chapter)
   │
   └── NO  → None
```

Label:

```rust
'search:
```

cho phép:

```rust
break 'search Some(chapter);
```

thoát khỏi block và trả kết quả.

Phần:

```rust
'a
```

ở function này là **lifetime**, không phải loop label. Đây cũng là một ví dụ tốt để thấy hai khái niệm dùng cú pháp `'...` nhưng khác hoàn toàn về vai trò.

---

# 38. Bài tập 1 — Nested Loop

Viết:

```rust
for i in 1..=5 {
    for j in 1..=5 {
        ...
    }
}
```

Khi:

```text
i == 3
j == 3
```

thì thoát **cả hai loop**.

Bắt buộc dùng:

```rust
'outer:
```

và:

```rust
break 'outer;
```

---

# 39. Bài tập 2 — `continue 'outer`

Cho:

```rust
let matrix = [
    [1, 2, 3],
    [4, 0, 6],
    [7, 8, 9],
];
```

Nếu một row chứa `0`, bỏ qua toàn bộ row.

Kết quả:

```text
1
2
3
7
8
9
```

Bắt buộc dùng:

```rust
continue 'row;
```

---

# 40. Bài tập 3 — Tìm kiếm

Cho:

```rust
let matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
];
```

Tìm:

```text
8
```

Khi tìm thấy:

```text
Found at row=2, col=1
```

và thoát cả hai loop bằng:

```rust
break 'search;
```

---

# 41. Bài tập 4 — `break 'search value`

Viết:

```rust
fn find_number(
    matrix: &[[i32; 3]; 3],
    target: i32,
) -> Option<(usize, usize)>
```

Ví dụ:

```rust
let position = find_number(&matrix, 8);
```

kết quả:

```text
Some((2, 1))
```

Hãy dùng:

```rust
'search: {
    ...
    break 'search Some(...);
    ...
    None
}
```

---

# 42. Bài tập 5 — Crawler

Tạo:

```rust
struct Chapter {
    number: u32,
    valid: bool,
}
```

và:

```rust
struct Story {
    title: String,
    chapters: Vec<Chapter>,
}
```

Nếu một chapter không hợp lệ:

```rust
continue 'story;
```

để bỏ qua toàn bộ story.

Flow:

```text
Story 1
 ├── Chapter 1 → OK
 ├── Chapter 2 → INVALID
 │                 ↓
 │            continue 'story
 │
Story 2
 ├── Chapter 1 → OK
 └── Chapter 2 → OK
```

---

# 43. Challenge — Crawler Worker

Xây hệ thống:

```rust
enum WorkerCommand {
    ProcessStory(u32),
    ProcessChapter(u32),
    SkipStory,
    Shutdown,
}
```

Có nested loop:

```text
worker
 └── stories
      └── chapters
```

Yêu cầu:

### `ProcessChapter`

```text
process
```

### `SkipStory`

```rust
continue 'story;
```

### `Shutdown`

```rust
break 'worker;
```

### Kết thúc

In:

```text
Worker stopped.
```

Đây là bài tập tổng hợp rất tốt trước Mini Project.

---

# 44. Những điều cần nhớ

### Label

```rust
'outer:
```

### Break outer

```rust
break 'outer;
```

### Continue outer

```rust
continue 'outer;
```

### Break có giá trị

```rust
break 'search value;
```

### Block có label

```rust
'search: {
    ...
}
```

---

# 45. Mental Model

Hãy nhớ hình ảnh này:

```text
                LABEL
                  │
                  ▼
          ┌───────────────┐
          │  OUTER LOOP   │ ← 'outer
          │               │
          │   ┌────────┐  │
          │   │ INNER  │  │
          │   │ LOOP   │  │
          │   └────────┘  │
          └───────────────┘
                  ▲
                  │
          break 'outer
          continue 'outer
```

Không label:

```rust
break;
```

→ loop gần nhất.

Có label:

```rust
break 'outer;
```

→ loop cụ thể.

---

# 46. Control Flow đã học đến đâu?

Bây giờ bạn đã có:

```text
if
 │
 ├── if / else
 │
loop
 │
 ├── break
 ├── continue
 └── loop expression
 │
while
 │
for
 │
match
 │
if let
 │
while let
 │
Labels
 ├── break 'label
 └── continue 'label
```

Bạn đã hoàn thành gần như toàn bộ **Control Flow cơ bản của Rust**.

---

# 47. Roadmap

```text
Buổi 11 → if
Buổi 12 → loop
Buổi 13 → while
Buổi 14 → for
Buổi 15 → match
Buổi 16 → if let
Buổi 17 → while let
Buổi 18 → break & continue
Buổi 19 → Labels          ← hôm nay
Buổi 20 → Mini Project
```

**Buổi 20 sẽ là Mini Project tổng hợp Control Flow**: chúng ta sẽ xây một chương trình CLI nhỏ mô phỏng **Crawler Task Manager**, sử dụng `enum`, `match`, `if let`, `while let`, `loop`, `break`, `continue`, `labels`, `VecDeque` và `Result/Option` để ghép toàn bộ kiến thức của Phần II thành một chương trình có thể chạy ngay.
