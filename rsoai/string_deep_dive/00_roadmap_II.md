Được. Hai roadmap này **nên hợp nhất**, vì roadmap ban đầu phù hợp để học tuần tự, còn roadmap mới có thêm chiều sâu về **memory, ownership và performance**.

Mình đề xuất giữ **10 buổi của roadmap ban đầu**, nhưng tích hợp các nội dung deep dive vào từng buổi thay vì kéo lên 15 buổi.

# Phần II — `String` Ownership & Memory Deep Dive

### Buổi 11 — `String` là gì?

* `String` vs `str` vs `&str`
* `String` là owned UTF-8 string
* Cấu trúc `String`
* `String` và `Vec<u8>`
* Khi nào dùng `String`, khi nào dùng `&str`
* Memory model tổng quan

### Buổi 12 — `String::from`

* `String::from("hello")`
* Literal → `String`
* Copy dữ liệu từ literal
* Heap allocation
* `From<&str> for String`
* `String::from` vs `to_string`
* Cost model

### Buổi 13 — `to_string()`

* `ToString` trait
* `Display` và `ToString`
* `"hello".to_string()`
* `42.to_string()`
* `String::from()` vs `to_string()`
* Khi nào `to_string()` gây formatting
* `to_owned()` và `to_string()` khác nhau thế nào

### Buổi 14 — `push` / `push_str`

* `push(char)`
* `push_str(&str)`
* UTF-8 encoding khi `push`
* Allocation khi append
* Reallocation
* `push` vs `push_str`
* Performance considerations

### Buổi 15 — `+` và `format!`

* `String + &str`
* Ownership khi dùng `+`
* `Add<&str>`
* Tại sao bên trái phải là `String`
* `format!`
* `format!` vs `+`
* Nhiều chuỗi: cách nào tốt hơn?
* Allocation và performance

### Buổi 16 — Capacity / Length

* `len()`
* `capacity()`
* `is_empty()`
* UTF-8 và `len()`
* `reserve()`
* `reserve_exact()`
* `shrink_to_fit()`
* Capacity growth
* Reallocation

### Buổi 17 — Heap Allocation & Memory Layout

* `String` nằm ở stack/heap như thế nào
* `ptr`
* `len`
* `capacity`
* Heap allocation
* Reallocation
* Dangling pointer được Rust ngăn chặn thế nào
* `String` vs `Vec<u8>`
* Memory visualization

### Buổi 18 — Ownership với `String`

* Move
* Copy không xảy ra
* `clone()`
* Borrow `&String`
* Borrow `&str`
* Mutable borrow `&mut String`
* Ownership transfer
* Function nhận/trả `String`
* Function nhận/trả `&str`

### Buổi 19 — `String` vs `&str`

* Owned vs borrowed
* Stack vs heap
* Lifetime
* API design
* `&String` vs `&str`
* Khi nào return `String`
* Khi nào return `&str`
* `Cow<str>` preview
* Best practices

### Buổi 20 — `String` Performance & Deep Dive

* Allocation cost
* Reallocation cost
* `with_capacity()`
* `reserve()`
* `push_str` batching
* `format!`
* `+`
* `clone`
* Borrowing
* Benchmark tư duy
* Thiết kế API String hiệu quả

---

# Phần III — String Manipulation

Sau khi đã hiểu ownership + memory, mình đề xuất tách phần thao tác chuỗi thành một phần riêng:

### Buổi 21 — `insert` / `insert_str`

### Buổi 22 — `pop` / `remove`

### Buổi 23 — `truncate` / `clear`

### Buổi 24 — `replace` / `replacen`

### Buổi 25 — `replace_range`

### Buổi 26 — `split_off`

### Buổi 27 — `retain`

### Buổi 28 — `drain`

### Buổi 29 — `chars` / `char_indices`

### Buổi 30 — `bytes` / `as_bytes`

---

# Phần IV — UTF-8 & String Deep Dive

### Buổi 31 — UTF-8 trong `String`

### Buổi 32 — Byte vs `char`

### Buổi 33 — Unicode Scalar Value

### Buổi 34 — Unicode Boundary

### Buổi 35 — Indexing String

### Buổi 36 — Slicing String an toàn

### Buổi 37 — `chars()` Deep Dive

### Buổi 38 — `char_indices()` Deep Dive

### Buổi 39 — Unicode Combining Characters

### Buổi 40 — Unicode Grapheme Cluster

---

# Phần V — String API & Advanced

### Buổi 41 — `split`

### Buổi 42 — `split_whitespace`

### Buổi 43 — `lines`

### Buổi 44 — `split_at`

### Buổi 45 — `strip_prefix` / `strip_suffix`

### Buổi 46 — `starts_with` / `ends_with`

### Buổi 47 — `contains`

### Buổi 48 — `find` / `rfind`

### Buổi 49 — `matches` / `match_indices`

### Buổi 50 — String Mini Project

---

## Roadmap tổng thể

Như vậy chúng ta có một progression hợp lý hơn:

```text
PHẦN I
String Literal & str
    │
    ├── "hello"
    ├── str / &str
    ├── memory
    ├── UTF-8
    ├── raw string
    ├── byte string
    ├── char
    ├── slice
    └── lifetime / 'static
              │
              ▼
PHẦN II
String Ownership & Memory
              │
              ├── String
              ├── String::from
              ├── to_string
              ├── push / push_str
              ├── + / format!
              ├── len / capacity
              ├── heap
              ├── ownership
              ├── String ↔ &str
              └── performance
              │
              ▼
PHẦN III
String Manipulation
              │
              ├── insert
              ├── remove
              ├── pop
              ├── truncate
              ├── clear
              ├── replace
              ├── drain
              └── retain
              │
              ▼
PHẦN IV
UTF-8 Deep Dive
              │
              ├── bytes
              ├── char
              ├── boundary
              ├── slicing
              ├── chars
              ├── char_indices
              └── grapheme
              │
              ▼
PHẦN V
String API & Advanced
              │
              ├── split
              ├── find
              ├── match
              ├── prefix/suffix
              ├── iterators
              └── Mini Project
```

**Mình khuyên dùng roadmap này.** Nó đi từ **literal → borrowed → owned → memory → ownership → manipulation → UTF-8 → advanced API**, đúng với cách Rust thực sự vận hành.

Và từ **Buổi 11**, chúng ta sẽ bắt đầu theo roadmap hợp nhất này: **Buổi 11 — `String` là gì?**
