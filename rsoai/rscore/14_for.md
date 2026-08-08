# Rust Professional 2026 — Buổi 14

## `for`, `Range` và tư duy Iterator

Buổi 14 là một bước chuyển rất quan trọng.

Từ:

```rust
while
loop
break
continue
```

chúng ta chuyển sang cách viết idiomatic Rust:

```rust
for item in collection {
    ...
}
```

Nếu `while` dạy bạn **điều khiển vòng lặp**, thì `for` bắt đầu dạy bạn **duyệt dữ liệu**.

Đây cũng là nền móng trực tiếp cho:

```text
Iterator
Iterator Adapter
map
filter
fold
collect
```

mà chúng ta sẽ học sâu hơn sau này.

---

# 1. `for` cơ bản

Cú pháp:

```rust
for variable in iterable {
    // code
}
```

Ví dụ:

```rust
fn main() {
    for number in 1..6 {
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

Chú ý:

```rust
1..6
```

không bao gồm `6`.

---

# 2. `Range`

Biểu thức:

```rust
1..6
```

tạo một range:

```text
1
2
3
4
5
```

Còn:

```rust
1..=6
```

bao gồm cả `6`:

```text
1
2
3
4
5
6
```

So sánh:

```text
1..6
 ↓
1 2 3 4 5

1..=6
 ↓
1 2 3 4 5 6
```

---

# 3. `..` và `..=`

Đây là hai syntax bạn phải nhớ:

```rust
start..end
```

→ exclusive end.

```rust
start..=end
```

→ inclusive end.

Ví dụ:

```rust
for i in 0..5 {
    println!("{i}");
}
```

Output:

```text
0
1
2
3
4
```

Trong khi:

```rust
for i in 0..=5 {
    println!("{i}");
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

---

# 4. `for` thực chất làm gì?

Đây là một insight rất quan trọng.

Khi bạn viết:

```rust
for item in collection {
    println!("{item}");
}
```

về bản chất Rust đang làm việc với:

```text
IntoIterator
      ↓
Iterator
      ↓
next()
      ↓
Some(item)
      ↓
body
      ↓
next()
```

Tư duy:

```text
for
 ↓
lấy iterator
 ↓
lấy từng item
 ↓
xử lý item
 ↓
hết item
 ↓
kết thúc
```

Do đó `for` là cửa ngõ để hiểu **Iterator**.

---

# 5. `for` tương đương với `while let`

Ví dụ:

```rust
let numbers = vec![10, 20, 30];

for number in numbers {
    println!("{number}");
}
```

Có thể hình dung gần tương đương:

```rust
let numbers = vec![10, 20, 30];

let mut iterator = numbers.into_iter();

while let Some(number) = iterator.next() {
    println!("{number}");
}
```

Không phải lúc nào compiler cũng hạ code theo đúng source-level này, nhưng về mặt tư duy thì rất hữu ích.

---

# 6. Vì vậy `for` rất quan trọng

Thay vì:

```rust
let mut i = 0;

while i < numbers.len() {
    println!("{}", numbers[i]);

    i += 1;
}
```

hãy viết:

```rust
for number in numbers {
    println!("{number}");
}
```

Đơn giản hơn rất nhiều.

---

# 7. `for` với `Vec`

```rust
fn main() {
    let numbers = vec![10, 20, 30, 40];

    for number in numbers {
        println!("{number}");
    }
}
```

Output:

```text
10
20
30
40
```

---

# 8. Một điểm rất quan trọng: ownership

Đoạn này:

```rust
for number in numbers {
    println!("{number}");
}
```

có thể **consume** `numbers`.

Sau loop:

```rust
println!("{:?}", numbers);
```

có thể gây lỗi ownership.

Ví dụ:

```rust
fn main() {
    let numbers = vec![10, 20, 30];

    for number in numbers {
        println!("{number}");
    }

    println!("{numbers:?}");
}
```

Đây là lỗi.

Tại sao?

Vì:

```text
numbers
   │
   └── into_iter()
         │
         └── lấy ownership
```

Đây là một trong những nơi đầu tiên bạn sẽ thấy `for` liên quan trực tiếp tới **ownership**.

---

# 9. Duyệt mà không lấy ownership

Dùng:

```rust
for number in &numbers {
    println!("{number}");
}
```

Bây giờ `numbers` vẫn tồn tại.

```rust
fn main() {
    let numbers = vec![10, 20, 30];

    for number in &numbers {
        println!("{number}");
    }

    println!("{numbers:?}");
}
```

Output:

```text
10
20
30
[10, 20, 30]
```

---

# 10. `for` với mutable reference

Nếu muốn thay đổi các phần tử:

```rust
fn main() {
    let mut numbers = vec![1, 2, 3, 4, 5];

    for number in &mut numbers {
        *number *= 2;
    }

    println!("{numbers:?}");
}
```

Output:

```text
[2, 4, 6, 8, 10]
```

---

# 11. Tại sao cần `*number`?

Trong:

```rust
for number in &mut numbers {
```

`number` là:

```text
&mut i32
```

không phải:

```text
i32
```

Muốn thay đổi giá trị bên trong reference:

```rust
*number
```

Ví dụ:

```rust
*number *= 2;
```

Tạm thời chỉ cần ghi nhớ:

```text
&number
    ↓
reference

&mut number
    ↓
mutable reference

*number
    ↓
dereference
```

Chúng ta sẽ học ownership/borrowing cực sâu ở phần sau.

---

# 12. Ba kiểu duyệt `Vec`

Đây là kiến thức cực kỳ quan trọng.

### Consume

```rust
for item in items {
}
```

### Borrow

```rust
for item in &items {
}
```

### Mutable borrow

```rust
for item in &mut items {
}
```

Tư duy:

```text
items
├── for item in items
│      → ownership
│
├── for item in &items
│      → shared borrow
│
└── for item in &mut items
       → mutable borrow
```

---

# 13. `for` với array

```rust
fn main() {
    let numbers = [10, 20, 30, 40];

    for number in numbers {
        println!("{number}");
    }
}
```

Output:

```text
10
20
30
40
```

---

# 14. `for` với tuple?

Tuple không phải một collection iterable theo cách thông thường.

Ví dụ:

```rust
let data = (10, 20, 30);
```

không thể đơn giản:

```rust
for value in data {
}
```

Tuple có số lượng phần tử cố định và các phần tử có thể khác kiểu:

```rust
let data = (10, "hello", true);
```

Trong khi iterator yêu cầu một chuỗi item cùng một kiểu.

---

# 15. `for` với `String`

Có thể duyệt Unicode scalar values bằng:

```rust
for character in "Hello" .chars() {
    println!("{character}");
}
```

Viết chuẩn:

```rust
fn main() {
    let text = "Hello";

    for character in text.chars() {
        println!("{character}");
    }
}
```

Output:

```text
H
e
l
l
o
```

---

# 16. Unicode

Ví dụ tiếng Việt:

```rust
fn main() {
    let text = "Xin chào";

    for character in text.chars() {
        println!("{character}");
    }
}
```

Output:

```text
X
i
n
 
c
h
à
o
```

Điều này dẫn đến một điểm rất quan trọng:

> `String` trong Rust không đơn giản là một mảng ký tự.

---

# 17. `.bytes()`

Ngoài:

```rust
.chars()
```

còn có:

```rust
.bytes()
```

Ví dụ:

```rust
fn main() {
    let text = "ABC";

    for byte in text.bytes() {
        println!("{byte}");
    }
}
```

Output:

```text
65
66
67
```

---

# 18. `chars()` vs `bytes()`

```text
chars()
    → Unicode scalar values

bytes()
    → UTF-8 bytes
```

Ví dụ:

```rust
let text = "A";
```

có:

```text
chars → 'A'
bytes → 65
```

Với Unicode, sự khác biệt rõ hơn.

---

# 19. `for` với `Range`

Ví dụ:

```rust
for i in 0..10 {
    println!("{i}");
}
```

Rất phù hợp để:

* đếm
* tạo index
* lặp N lần
* xử lý batch
* tạo test data

---

# 20. `rev()`

Muốn duyệt ngược:

```rust
fn main() {
    for i in (1..=5).rev() {
        println!("{i}");
    }
}
```

Output:

```text
5
4
3
2
1
```

`rev()` tạo một iterator đảo chiều.

---

# 21. `step_by()`

Muốn nhảy theo bước:

```rust
fn main() {
    for i in (0..10).step_by(2) {
        println!("{i}");
    }
}
```

Output:

```text
0
2
4
6
8
```

---

# 22. Kết hợp `rev()` và `step_by()`

```rust
fn main() {
    for i in (0..=10).rev().step_by(2) {
        println!("{i}");
    }
}
```

Output:

```text
10
8
6
4
2
0
```

---

# 23. `enumerate()`

Một trong những iterator method quan trọng nhất.

Giả sử:

```rust
let names = vec![
    "Alice",
    "Bob",
    "Charlie",
];
```

Muốn có index:

```rust
for (index, name) in names.iter().enumerate() {
    println!("{index}: {name}");
}
```

Output:

```text
0: Alice
1: Bob
2: Charlie
```

---

# 24. Tại sao `enumerate()` hữu ích?

Thay vì:

```rust
let mut index = 0;

for name in &names {
    println!("{index}: {name}");

    index += 1;
}
```

viết:

```rust
for (index, name) in names.iter().enumerate() {
    println!("{index}: {name}");
}
```

Ít state thủ công hơn.

Code dễ đọc hơn.

---

# 25. `enumerate()` trả tuple

Mỗi iteration:

```text
(index, item)
```

Ví dụ:

```text
(0, "Alice")
(1, "Bob")
(2, "Charlie")
```

Ta destructure:

```rust
for (index, name) in ... {
}
```

Đây là sự kết hợp giữa:

```text
iterator
+
tuple destructuring
```

---

# 26. `zip()`

Giả sử:

```rust
let names = ["Alice", "Bob", "Charlie"];
let ages = [20, 25, 30];
```

Muốn ghép:

```text
Alice → 20
Bob   → 25
Charlie → 30
```

Dùng:

```rust
fn main() {
    let names = ["Alice", "Bob", "Charlie"];
    let ages = [20, 25, 30];

    for (name, age) in names.iter().zip(ages.iter()) {
        println!("{name}: {age}");
    }
}
```

Output:

```text
Alice: 20
Bob: 25
Charlie: 30
```

---

# 27. `zip()` hoạt động như thế nào?

Hai iterator:

```text
names:
Alice
Bob
Charlie

ages:
20
25
30
```

`zip()` tạo:

```text
(Alice, 20)
(Bob, 25)
(Charlie, 30)
```

---

# 28. `zip()` dừng ở iterator ngắn hơn

Ví dụ:

```rust
fn main() {
    let names = ["Alice", "Bob", "Charlie"];
    let ages = [20, 25];

    for (name, age) in names.iter().zip(ages.iter()) {
        println!("{name}: {age}");
    }
}
```

Output:

```text
Alice: 20
Bob: 25
```

`Charlie` không xuất hiện.

---

# 29. `for` + `break`

Giống `loop`:

```rust
fn main() {
    for number in 1..=10 {
        if number == 5 {
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
```

---

# 30. `for` + `continue`

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

# 31. Nested `for`

```rust
fn main() {
    for x in 1..=3 {
        for y in 1..=3 {
            println!("x = {x}, y = {y}");
        }
    }
}
```

Output:

```text
x = 1, y = 1
x = 1, y = 2
x = 1, y = 3
x = 2, y = 1
x = 2, y = 2
x = 2, y = 3
x = 3, y = 1
x = 3, y = 2
x = 3, y = 3
```

---

# 32. Loop label với `for`

Có thể:

```rust
fn main() {
    'outer: for x in 1..=3 {
        for y in 1..=3 {
            println!("{x}, {y}");

            if x == 2 && y == 2 {
                break 'outer;
            }
        }
    }

    println!("Done");
}
```

Output:

```text
1, 1
1, 2
1, 3
2, 1
2, 2
Done
```

---

# 33. `for` với `Vec<String>`

Ví dụ:

```rust
fn main() {
    let stories = vec![
        String::from("Story A"),
        String::from("Story B"),
        String::from("Story C"),
    ];

    for story in &stories {
        println!("{story}");
    }

    println!("Total: {}", stories.len());
}
```

Dùng:

```rust
&stories
```

để không consume vector.

Đây là pattern bạn sẽ dùng rất thường xuyên trong project thực tế.

---

# 34. `iter()`

Bạn cũng có thể viết:

```rust
for story in stories.iter() {
    println!("{story}");
}
```

So sánh:

```rust
for story in &stories
```

và:

```rust
for story in stories.iter()
```

Trong nhiều tình huống chúng biểu diễn cùng ý tưởng:

```text
borrow từng phần tử
```

`&collection` thường ngắn gọn hơn.

---

# 35. `iter_mut()`

Muốn sửa từng phần tử:

```rust
fn main() {
    let mut numbers = vec![1, 2, 3];

    for number in numbers.iter_mut() {
        *number *= 10;
    }

    println!("{numbers:?}");
}
```

Output:

```text
[10, 20, 30]
```

---

# 36. `into_iter()`

Muốn consume:

```rust
fn main() {
    let numbers = vec![1, 2, 3];

    for number in numbers.into_iter() {
        println!("{number}");
    }
}
```

Sau đó `numbers` không còn được sử dụng.

Bạn sẽ gặp ba method cực kỳ quan trọng:

```text
iter()
    → &T

iter_mut()
    → &mut T

into_iter()
    → T
```

---

# 37. Bảng phải nhớ

| Cách                     | Item     |
| ------------------------ | -------- |
| `collection.iter()`      | `&T`     |
| `collection.iter_mut()`  | `&mut T` |
| `collection.into_iter()` | `T`      |

Ví dụ:

```rust
for item in collection.iter() {}
```

→ borrow.

```rust
for item in collection.iter_mut() {}
```

→ mutable borrow.

```rust
for item in collection.into_iter() {}
```

→ consume.

---

# 38. Đây chính là Ownership trong Iterator

Đây là phần rất quan trọng.

Giả sử:

```rust
let numbers = vec![1, 2, 3];
```

### Consume

```rust
for n in numbers {
}
```

```text
numbers
   ↓
ownership chuyển vào iterator
```

### Borrow

```rust
for n in &numbers {
}
```

```text
numbers
   ↓
&numbers
   ↓
iterator
```

### Mutable borrow

```rust
for n in &mut numbers {
}
```

```text
numbers
   ↓
&mut numbers
   ↓
iterator
```

---

# 39. Mini Project — Batch Story Processor

Bây giờ xây một ví dụ gần với project crawler/reader của bạn.

Ta có:

```rust
#[derive(Debug)]
struct Story {
    title: String,
    chapters: u32,
}
```

Danh sách:

```rust
fn main() {
    let stories = vec![
        Story {
            title: String::from("Story A"),
            chapters: 100,
        },
        Story {
            title: String::from("Story B"),
            chapters: 50,
        },
        Story {
            title: String::from("Story C"),
            chapters: 200,
        },
    ];

    for story in &stories {
        println!(
            "{} - {} chapters",
            story.title,
            story.chapters
        );
    }
}
```

Output:

```text
Story A - 100 chapters
Story B - 50 chapters
Story C - 200 chapters
```

---

# 40. Thêm index

```rust
fn main() {
    let stories = vec![
        Story {
            title: String::from("Story A"),
            chapters: 100,
        },
        Story {
            title: String::from("Story B"),
            chapters: 50,
        },
        Story {
            title: String::from("Story C"),
            chapters: 200,
        },
    ];

    for (index, story) in stories.iter().enumerate() {
        println!(
            "#{index} {} - {} chapters",
            story.title,
            story.chapters
        );
    }
}
```

Output:

```text
#0 Story A - 100 chapters
#1 Story B - 50 chapters
#2 Story C - 200 chapters
```

---

# 41. Lọc bằng `if`

Ví dụ chỉ xử lý truyện có trên 100 chapter:

```rust
for story in &stories {
    if story.chapters > 100 {
        println!("Large story: {}", story.title);
    }
}
```

Output:

```text
Large story: Story C
```

Đây là cách đơn giản trước khi học:

```text
filter()
```

ở phần Iterator.

---

# 42. Tính tổng chapter

```rust
fn main() {
    let stories = vec![
        Story {
            title: String::from("Story A"),
            chapters: 100,
        },
        Story {
            title: String::from("Story B"),
            chapters: 50,
        },
        Story {
            title: String::from("Story C"),
            chapters: 200,
        },
    ];

    let mut total = 0;

    for story in &stories {
        total += story.chapters;
    }

    println!("Total chapters: {total}");
}
```

Output:

```text
Total chapters: 350
```

Sau này chúng ta sẽ viết nó bằng:

```text
iter()
map()
sum()
```

nhưng hiện tại cách thủ công này giúp bạn hiểu rõ logic.

---

# 43. Tìm story lớn nhất

```rust
fn main() {
    let stories = vec![
        Story {
            title: String::from("Story A"),
            chapters: 100,
        },
        Story {
            title: String::from("Story B"),
            chapters: 50,
        },
        Story {
            title: String::from("Story C"),
            chapters: 200,
        },
    ];

    let mut max_chapters = 0;
    let mut max_title = "";

    for story in &stories {
        if story.chapters > max_chapters {
            max_chapters = story.chapters;
            max_title = &story.title;
        }
    }

    println!("{max_title}: {max_chapters}");
}
```

Output:

```text
Story C: 200
```

---

# 44. Một vấn đề thú vị

Ở đây:

```rust
let mut max_title = "";
```

`max_title` có kiểu:

```text
&str
```

nhưng:

```rust
&story.title
```

là:

```text
&String
```

Rust có thể thực hiện coercion phù hợp sang string slice trong context này.

Sau này khi học:

```text
References
Lifetimes
Deref
Deref coercion
```

bạn sẽ hiểu sâu hơn.

---

# 45. Mini Project hoàn chỉnh

Ta xây một **Story Batch Processor**:

```rust
#[derive(Debug)]
struct Story {
    title: String,
    chapters: u32,
    completed: bool,
}

fn main() {
    let stories = vec![
        Story {
            title: String::from("Rust Adventures"),
            chapters: 120,
            completed: true,
        },
        Story {
            title: String::from("Async World"),
            chapters: 80,
            completed: false,
        },
        Story {
            title: String::from("Crawler Master"),
            chapters: 200,
            completed: true,
        },
    ];

    println!("=== STORY LIST ===");

    for (index, story) in stories.iter().enumerate() {
        println!(
            "{}. {} | {} chapters | completed={}",
            index + 1,
            story.title,
            story.chapters,
            story.completed
        );
    }

    println!();
    println!("=== LARGE STORIES ===");

    for story in &stories {
        if story.chapters >= 100 {
            println!("{}", story.title);
        }
    }

    println!();
    println!("=== COMPLETED STORIES ===");

    for story in &stories {
        if story.completed {
            println!("{}", story.title);
        }
    }

    let mut total_chapters = 0;

    for story in &stories {
        total_chapters += story.chapters;
    }

    println!();
    println!("Total chapters: {total_chapters}");
}
```

Output:

```text
=== STORY LIST ===
1. Rust Adventures | 120 chapters | completed=true
2. Async World | 80 chapters | completed=false
3. Crawler Master | 200 chapters | completed=true

=== LARGE STORIES ===
Rust Adventures
Crawler Master

=== COMPLETED STORIES ===
Rust Adventures
Crawler Master

Total chapters: 400
```

---

# 46. Đây chính là nền tảng crawler

Hãy nhìn code trên theo góc nhìn framework:

```text
stories
   │
   ├── enumerate
   │
   ├── process
   │
   ├── filter
   │
   ├── aggregate
   │
   └── report
```

Sau này với Iterator:

```text
stories
  │
  ├── iter()
  ├── filter()
  ├── map()
  ├── collect()
  └── sum()
```

Ta sẽ có code declarative hơn rất nhiều.

---

# 47. `for` với range và index

Một pattern thường thấy:

```rust
let names = vec![
    "Alice",
    "Bob",
    "Charlie",
];

for i in 0..names.len() {
    println!("{}: {}", i, names[i]);
}
```

Code này chạy được.

Nhưng **không nên ưu tiên** nếu không cần index trực tiếp.

Tốt hơn:

```rust
for (i, name) in names.iter().enumerate() {
    println!("{i}: {name}");
}
```

---

# 48. Tại sao `enumerate()` tốt hơn?

Cách này:

```rust
for i in 0..names.len() {
    let name = &names[i];
}
```

đang suy nghĩ theo kiểu:

```text
index → truy cập collection
```

Trong khi:

```rust
for (i, name) in names.iter().enumerate() {
}
```

suy nghĩ:

```text
iterator → item + index
```

Đây là tư duy idiomatic Rust hơn.

---

# 49. Khi nào dùng range index?

Vẫn có trường hợp phù hợp.

Ví dụ khi bạn cần:

```text
i
i + 1
i * 2
```

hoặc truy cập nhiều collection theo cùng index.

Nhưng nếu chỉ muốn duyệt collection:

```rust
for item in &collection
```

thường tốt hơn.

---

# 50. `for` không chỉ dành cho số

Bạn có thể:

```rust
for item in vec
```

```rust
for item in array
```

```rust
for item in string.chars()
```

```rust
for item in iterator
```

```rust
for item in range
```

Tất cả đều dựa trên ý tưởng:

> **Iterable → Iterator → từng item**

---

# 51. Mental Model

Hãy ghi nhớ:

```text
               iterable
                   │
                   ▼
             IntoIterator
                   │
                   ▼
               Iterator
                   │
                   ▼
              next()
             /      \
         Some        None
           │           │
           ▼           ▼
          item        stop
```

`for` đứng ở phía trên abstraction này.

---

# 52. Bài tập 1 — Range

In:

```text
1
2
3
...
100
```

bằng `for`.

---

# 53. Bài tập 2 — Even

In các số chẵn từ:

```text
0 → 100
```

Dùng:

```rust
step_by()
```

Không dùng `if`.

---

# 54. Bài tập 3 — Countdown

In:

```text
10
9
8
...
1
```

Dùng:

```rust
rev()
```

---

# 55. Bài tập 4 — Enumerate

Cho:

```rust
let languages = vec![
    "Rust",
    "Python",
    "JavaScript",
    "Go",
];
```

Output:

```text
1. Rust
2. Python
3. JavaScript
4. Go
```

Dùng:

```rust
enumerate()
```

---

# 56. Bài tập 5 — Mutable iteration

Cho:

```rust
let mut numbers = vec![1, 2, 3, 4, 5];
```

Dùng:

```rust
for
```

để biến thành:

```text
[2, 4, 6, 8, 10]
```

Không tạo vector mới.

---

# 57. Bài tập 6 — Zip

Cho:

```rust
let names = ["Alice", "Bob", "Charlie"];
let scores = [80, 90, 95];
```

Output:

```text
Alice: 80
Bob: 90
Charlie: 95
```

Dùng:

```rust
zip()
```

---

# 58. Bài tập 7 — Find

Cho:

```rust
let numbers = vec![10, 20, 35, 40, 50];
```

Dùng `for` để tìm số đầu tiên chia hết cho:

```text
5
```

---

# 59. Bài tập 8 — Skip

Cho:

```rust
let numbers = 1..=20;
```

In tất cả số không chia hết cho `3`.

Dùng:

```rust
continue
```

---

# 60. Bài tập 9 — Nested Loop

Tạo bảng:

```text
1 x 1 = 1
1 x 2 = 2
...
9 x 9 = 81
```

Dùng hai `for`.

---

# 61. Bài tập 10 — Story Processor

Tạo:

```rust
struct Story {
    title: String,
    chapters: u32,
}
```

Danh sách 5 truyện.

Viết chương trình:

1. In danh sách.
2. In index.
3. Tính tổng chapter.
4. Tìm truyện có nhiều chapter nhất.
5. In các truyện có trên 100 chapter.

---

# 62. Challenge — Batch Chapter Processor

Tạo:

```rust
struct Chapter {
    number: u32,
    title: String,
    downloaded: bool,
}
```

Ví dụ:

```rust
let chapters = vec![
    Chapter {
        number: 1,
        title: String::from("Beginning"),
        downloaded: true,
    },
    Chapter {
        number: 2,
        title: String::from("Journey"),
        downloaded: false,
    },
    Chapter {
        number: 3,
        title: String::from("Battle"),
        downloaded: true,
    },
];
```

Viết chương trình:

```text
=== CHAPTERS ===

1. Beginning [downloaded]
2. Journey [pending]
3. Battle [downloaded]
```

Sau đó:

```text
Downloaded: 2
Pending: 1
```

Bắt buộc sử dụng:

```text
for
enumerate
if
```

---

# 63. Challenge nâng cao — Batch Worker

Mô phỏng crawler:

```rust
struct Task {
    id: u32,
    url: String,
}
```

Tạo:

```rust
Vec<Task>
```

Sau đó:

```text
for task in tasks
    ↓
process task
    ↓
success?
    ├── yes → continue
    └── failure → break
```

Mục tiêu là luyện:

```text
Vec
struct
for
ownership
borrowing
break
continue
```

---

# 64. Tổng kết Buổi 14

Bạn cần nắm chắc:

### `for`

```rust
for item in iterable {
}
```

### Range

```rust
0..10
```

```rust
0..=10
```

### Reverse

```rust
(0..10).rev()
```

### Step

```rust
(0..10).step_by(2)
```

### Index

```rust
iterator.enumerate()
```

### Ghép iterator

```rust
iter1.zip(iter2)
```

### Borrow

```rust
for item in &collection
```

### Mutable borrow

```rust
for item in &mut collection
```

### Consume

```rust
for item in collection
```

---

# 65. Ba dòng code phải thuộc

```rust
for item in &items {
    println!("{item:?}");
}
```

→ duyệt mà không consume collection.

```rust
for item in &mut items {
    // modify item
}
```

→ duyệt và sửa collection.

```rust
for (index, item) in items.iter().enumerate() {
    println!("{index}: {item:?}");
}
```

→ duyệt kèm index.

---

# Roadmap hiện tại

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
├── 13 — while / while let
└── 14 — for / Range / Iterator basics ← DONE
```

## Buổi 15 — Ownership

Đây sẽ là **một trong những buổi quan trọng nhất của toàn bộ Rust**.

Chúng ta sẽ bắt đầu từ:

```rust
let s1 = String::from("hello");
let s2 = s1;
```

và giải thích chính xác tại sao:

```rust
println!("{s1}");
```

lại lỗi.

Sau đó đi sâu vào:

```text
Stack
Heap
Move
Copy
Clone
Ownership rule
Drop
Scope
String
Vec
Function ownership
Return ownership
```

và cuối buổi xây **Ownership Lab** với hàng loạt ví dụ có thể copy vào `cargo run` để quan sát compiler.
