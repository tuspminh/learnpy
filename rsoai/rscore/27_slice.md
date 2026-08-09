# Rust — Phần III: Ownership

# Buổi 27 — Slice

Hôm nay chúng ta học **Slice** — một khái niệm cực kỳ quan trọng vì nó kết nối trực tiếp:

```text
Ownership
   ↓
Borrow
   ↓
Mutable Borrow
   ↓
Slice
   ↓
String / &str
```

Sau buổi này bạn cần hiểu chắc:

* Slice là gì
* `&[T]`
* `&str`
* Slice của Array
* Slice của `Vec`
* Range `..`, `..=`
* Mutable Slice `&mut [T]`
* Vì sao API nên dùng `&[T]` thay vì `&Vec<T>`
* Vì sao Slice không sở hữu dữ liệu
* Tại sao Slice là nền tảng của API Rust idiomatic

---

# 1. Slice là gì?

Hiểu đơn giản:

> **Slice là một reference tới một phần của collection.**

Ví dụ:

```rust
let numbers = [10, 20, 30, 40, 50];
```

Ta lấy phần:

```text
20, 30, 40
```

bằng:

```rust
&numbers[1..4]
```

Kết quả là:

```text
&[20, 30, 40]
```

Slice **không sở hữu** dữ liệu.

---

# 2. Array ban đầu

```rust
fn main() {
    let numbers = [10, 20, 30, 40, 50];

    println!("{numbers:?}");
}
```

Array:

```text
index
  0    1    2    3    4
  │    │    │    │    │
  ▼    ▼    ▼    ▼    ▼
[10,  20,  30,  40,  50]
```

---

# 3. Tạo Slice

```rust
fn main() {
    let numbers = [10, 20, 30, 40, 50];

    let slice = &numbers[1..4];

    println!("{slice:?}");
}
```

Kết quả:

```text
[20, 30, 40]
```

Chú ý:

```rust
&numbers[1..4]
```

không tạo Array mới.

Nó tạo một **reference tới vùng dữ liệu**.

---

# 4. Range `1..4`

Trong Rust:

```rust
1..4
```

nghĩa là:

```text
1
2
3
```

Không bao gồm `4`.

Đây là:

```text
start inclusive
end exclusive
```

Hay:

```text
[start, end)
```

---

# 5. Minh họa

Array:

```text
index:    0    1    2    3    4
          │    │    │    │    │
value:   10   20   30   40   50
```

Slice:

```rust
&numbers[1..4]
```

lấy:

```text
          ┌───────────────┐
          │    │    │     │
         20   30   40
```

Không lấy:

```text
10
50
```

---

# 6. Slice không sở hữu dữ liệu

Đây là điểm quan trọng nhất.

```rust
let numbers = [10, 20, 30, 40, 50];

let slice = &numbers[1..4];
```

Có:

```text
numbers
   │
   ▼
[10, 20, 30, 40, 50]
      ▲         ▲
      │         │
      └─────────┘
          slice
```

`slice` chỉ mượn dữ liệu.

Owner vẫn là:

```rust
numbers
```

---

# 7. Type của Slice

Một slice của `i32` có type:

```rust
&[i32]
```

Ví dụ:

```rust
let numbers = [10, 20, 30, 40];

let slice: &[i32] = &numbers[1..3];
```

---

# 8. `&[T]`

Đây là syntax tổng quát:

```rust
&[T]
```

Ví dụ:

```rust
&[i32]
```

```rust
&[String]
```

```rust
&[User]
```

```rust
&[Book]
```

Nghĩa:

> Immutable reference tới một sequence các phần tử kiểu `T`.

---

# 9. Slice có length

Ví dụ:

```rust
fn main() {
    let numbers = [10, 20, 30, 40, 50];

    let slice = &numbers[1..4];

    println!("length = {}", slice.len());
}
```

Kết quả:

```text
length = 3
```

---

# 10. Slice có thể index

```rust
fn main() {
    let numbers = [10, 20, 30, 40, 50];

    let slice = &numbers[1..4];

    println!("{}", slice[0]);
    println!("{}", slice[1]);
    println!("{}", slice[2]);
}
```

Kết quả:

```text
20
30
40
```

Chú ý:

```text
slice[0]
```

không phải:

```text
numbers[0]
```

Mà tương ứng:

```text
numbers[1]
```

---

# 11. Slice có index riêng

Ví dụ:

```rust
let numbers = [10, 20, 30, 40, 50];

let slice = &numbers[2..5];
```

Ta có:

```text
numbers:

index   0   1   2   3   4
        10  20  30  40  50

slice:

index   0   1   2
        30  40  50
```

Slice bắt đầu lại từ index `0`.

---

# 12. Range đầy đủ

Có nhiều cách viết slice.

### `1..4`

```rust
&numbers[1..4]
```

### `..4`

```rust
&numbers[..4]
```

nghĩa:

```text
0..4
```

### `1..`

```rust
&numbers[1..]
```

nghĩa:

```text
1..len
```

### `..`

```rust
&numbers[..]
```

nghĩa:

> Toàn bộ collection.

---

# 13. Ví dụ

```rust
fn main() {
    let numbers = [10, 20, 30, 40, 50];

    let a = &numbers[..3];
    let b = &numbers[2..];
    let c = &numbers[..];

    println!("{a:?}");
    println!("{b:?}");
    println!("{c:?}");
}
```

Kết quả:

```text
[10, 20, 30]
[30, 40, 50]
[10, 20, 30, 40, 50]
```

---

# 14. Slice của `Vec`

Slice không chỉ dùng với Array.

```rust
fn main() {
    let numbers = vec![10, 20, 30, 40, 50];

    let slice = &numbers[1..4];

    println!("{slice:?}");
}
```

Kết quả:

```text
[20, 30, 40]
```

---

# 15. Array và Vec đều có thể tạo Slice

Đây là điểm cực kỳ quan trọng.

```rust
let array = [1, 2, 3, 4];

let a: &[i32] = &array[1..3];
```

và:

```rust
let vector = vec![1, 2, 3, 4];

let b: &[i32] = &vector[1..3];
```

Cả hai đều tạo:

```rust
&[i32]
```

---

# 16. Đây chính là lý do Slice mạnh

Ta có thể viết:

```rust
fn sum(numbers: &[i32]) -> i32 {
    numbers.iter().sum()
}
```

Function này có thể nhận:

```text
Array
Vec
Array Slice
Vec Slice
```

---

# 17. Ví dụ hoàn chỉnh

```rust
fn sum(numbers: &[i32]) -> i32 {
    numbers.iter().sum()
}

fn main() {
    let array = [1, 2, 3, 4, 5];

    let vector = vec![10, 20, 30, 40, 50];

    println!("{}", sum(&array));
    println!("{}", sum(&vector));
}
```

Kết quả:

```text
15
150
```

Đây là một API rất idiomatic Rust.

---

# 18. Tại sao `&[i32]` nhận được Array?

Khi truyền:

```rust
sum(&array)
```

Rust thực hiện một **unsized coercion** từ:

```text
&[i32; 5]
```

sang:

```text
&[i32]
```

Bạn chưa cần đào sâu cơ chế này ngay.

Chỉ cần nhớ:

```text
&[i32; N]
       ↓
   & [i32]
```

---

# 19. Tại sao `&[i32]` nhận được Vec?

`Vec<i32>` có thể được borrow thành slice:

```rust
&vector
```

hoặc:

```rust
&vector[..]
```

để tạo:

```rust
&[i32]
```

Ví dụ:

```rust
fn print_numbers(numbers: &[i32]) {
    println!("{numbers:?}");
}

fn main() {
    let numbers = vec![1, 2, 3];

    print_numbers(&numbers);
}
```

---

# 20. `&Vec<T>` vs `&[T]`

Đây là kiến thức API cực kỳ quan trọng.

Bạn có thể viết:

```rust
fn print_numbers(numbers: &Vec<i32>) {
    println!("{numbers:?}");
}
```

Nhưng thường nên viết:

```rust
fn print_numbers(numbers: &[i32]) {
    println!("{numbers:?}");
}
```

Tại sao?

Vì function chỉ cần:

> một sequence các `i32` để đọc.

Nó không cần biết caller đang sử dụng:

```text
Vec
Array
Slice
```

---

# 21. So sánh

### API hẹp

```rust
fn process(numbers: &Vec<i32>)
```

Chỉ nhận:

```text
Vec<i32>
```

---

### API rộng hơn

```rust
fn process(numbers: &[i32])
```

Nhận:

```text
[i32; N]
Vec<i32>
&[i32]
```

và các loại dữ liệu có thể coerce phù hợp.

---

# 22. Đây là nguyên tắc API

Nếu function chỉ cần:

> "một danh sách phần tử để đọc"

thường dùng:

```rust
&[T]
```

thay vì:

```rust
&Vec<T>
```

Ví dụ:

```rust
fn find_max(numbers: &[i32]) -> Option<i32>
```

---

# 23. Ví dụ `find_max`

```rust
fn find_max(numbers: &[i32]) -> Option<i32> {
    numbers.iter().copied().max()
}

fn main() {
    let numbers = vec![10, 50, 20, 40];

    match find_max(&numbers) {
        Some(value) => println!("Max = {value}"),
        None => println!("Empty"),
    }
}
```

Kết quả:

```text
Max = 50
```

---

# 24. Slice và `iter()`

Slice thường kết hợp với:

```rust
.iter()
```

Ví dụ:

```rust
fn sum(numbers: &[i32]) -> i32 {
    numbers.iter().sum()
}
```

Mental model:

```text
&[i32]
   │
   ▼
 iter()
   │
   ▼
Iterator
```

Chúng ta sẽ học Iterator sâu hơn ở phần Intermediate.

---

# 25. Mutable Slice

Immutable slice:

```rust
&[T]
```

Mutable slice:

```rust
&mut [T]
```

Ví dụ:

```rust
fn double(numbers: &mut [i32]) {
    for number in numbers {
        *number *= 2;
    }
}
```

---

# 26. Test Mutable Slice

```rust
fn double(numbers: &mut [i32]) {
    for number in numbers {
        *number *= 2;
    }
}

fn main() {
    let mut numbers = vec![1, 2, 3, 4];

    double(&mut numbers);

    println!("{numbers:?}");
}
```

Kết quả:

```text
[2, 4, 6, 8]
```

---

# 27. Mutable Slice của Array

Không chỉ Vec:

```rust
fn double(numbers: &mut [i32]) {
    for number in numbers {
        *number *= 2;
    }
}

fn main() {
    let mut numbers = [1, 2, 3, 4];

    double(&mut numbers);

    println!("{numbers:?}");
}
```

Kết quả:

```text
[2, 4, 6, 8]
```

---

# 28. Mutable Slice một phần

Đây là điểm rất thú vị.

```rust
fn double(numbers: &mut [i32]) {
    for number in numbers {
        *number *= 2;
    }
}

fn main() {
    let mut numbers = [1, 2, 3, 4, 5];

    double(&mut numbers[1..4]);

    println!("{numbers:?}");
}
```

Kết quả:

```text
[1, 4, 6, 8, 5]
```

Chỉ:

```text
20? 
```

Không.

Ta có:

```text
original:

[1, 2, 3, 4, 5]
    └─────────┘
       slice

sau:

[1, 4, 6, 8, 5]
```

---

# 29. Slice không copy dữ liệu

Ví dụ:

```rust
let mut numbers = [1, 2, 3, 4, 5];

let slice = &mut numbers[1..4];

slice[0] = 100;
```

Sau đó:

```rust
println!("{numbers:?}");
```

Kết quả:

```text
[1, 100, 3, 4, 5]
```

Điều này chứng minh:

> Slice đang trỏ vào dữ liệu gốc.

---

# 30. Hình dung memory

```text
numbers
   │
   ▼
┌────┬────┬────┬────┬────┐
│ 1  │ 2  │ 3  │ 4  │ 5  │
└────┴────┴────┴────┴────┘
      ▲              ▲
      │              │
      └── slice ─────┘
```

Slice không tạo:

```text
[2, 3, 4]
```

ở vùng memory khác.

Nó chỉ borrow vùng:

```text
2, 3, 4
```

---

# 31. Slice có kích thước runtime

Array:

```rust
[i32; 5]
```

biết chính xác length:

```text
5
```

Ngay trong type.

Nhưng:

```rust
[i32; 10]
```

là type khác.

Trong khi:

```rust
&[i32]
```

không chứa length trong type.

Length được biết ở runtime.

---

# 32. Slice là DST

`[T]` là một **Dynamically Sized Type — DST**.

Bạn không thể có local variable kiểu:

```rust
let x: [i32] = ...;
```

theo cách thông thường.

Nhưng có thể có:

```rust
&[i32]
```

vì reference chứa thông tin cần thiết để truy cập slice.

---

# 33. Fat Pointer

Đây là phần deep dive quan trọng.

Một:

```rust
&[i32]
```

conceptually chứa:

```text
┌───────────────┐
│ pointer       │
├───────────────┤
│ length        │
└───────────────┘
```

Ví dụ:

```text
&[10, 20, 30]
```

có thể hình dung:

```text
pointer ───────► 10 20 30
length = 3
```

Đây là lý do slice biết:

```rust
slice.len()
```

dù `[T]` không chứa length trong type.

---

# 34. Đừng nhầm Slice với Array

Array:

```rust
[i32; 3]
```

có:

```text
fixed size
```

Slice:

```rust
[i32]
```

có:

```text
runtime length
```

Reference:

```rust
&[i32]
```

là cách phổ biến để sử dụng slice.

---

# 35. Ví dụ

```rust
fn main() {
    let array = [10, 20, 30];

    println!("{}", array.len());

    let slice = &array[..];

    println!("{}", slice.len());
}
```

Cả hai đều có `.len()`, nhưng type khác nhau.

---

# 36. Slice nested

Bạn có thể slice một slice:

```rust
fn main() {
    let numbers = [1, 2, 3, 4, 5];

    let a = &numbers[1..5];
    let b = &a[1..3];

    println!("{a:?}");
    println!("{b:?}");
}
```

Kết quả:

```text
[2, 3, 4, 5]
[3, 4]
```

---

# 37. Range không hợp lệ

Ví dụ:

```rust
let numbers = [1, 2, 3];

let slice = &numbers[0..10];
```

Chương trình panic khi chạy.

Vì index vượt giới hạn.

Rust đảm bảo không truy cập memory ngoài phạm vi.

---

# 38. Empty Slice

Bạn có thể tạo slice rỗng:

```rust
fn main() {
    let numbers = [1, 2, 3];

    let empty = &numbers[0..0];

    println!("length = {}", empty.len());
}
```

Kết quả:

```text
length = 0
```

---

# 39. `&[]`

Bạn cũng có thể có empty slice:

```rust
let numbers: &[i32] = &[];
```

Ví dụ:

```rust
fn print_numbers(numbers: &[i32]) {
    if numbers.is_empty() {
        println!("Empty");
        return;
    }

    println!("{numbers:?}");
}
```

---

# 40. Slice và Function API

Đây là pattern cực kỳ quan trọng.

Không tốt:

```rust
fn average(numbers: &Vec<f64>) -> f64
```

Tốt hơn:

```rust
fn average(numbers: &[f64]) -> Option<f64>
```

Vì function không quan tâm collection cụ thể là gì.

---

# 41. Ví dụ Average

```rust
fn average(numbers: &[f64]) -> Option<f64> {
    if numbers.is_empty() {
        return None;
    }

    let sum: f64 = numbers.iter().sum();

    Some(sum / numbers.len() as f64)
}

fn main() {
    let numbers = vec![10.0, 20.0, 30.0];

    match average(&numbers) {
        Some(value) => println!("Average = {value}"),
        None => println!("Empty"),
    }
}
```

Kết quả:

```text
Average = 20
```

---

# 42. Slice và ownership

Function:

```rust
fn sum(numbers: &[i32]) -> i32
```

không lấy ownership.

Caller:

```rust
let numbers = vec![1, 2, 3];

sum(&numbers);

println!("{numbers:?}");
```

hoàn toàn hợp lệ.

---

# 43. Slice và Borrow

Đây là mối quan hệ:

```text
Slice
  │
  └── thường được sử dụng thông qua reference
           │
           ├── &[T]
           │
           └── &mut [T]
```

Vì vậy Slice là phần mở rộng tự nhiên của Borrow.

---

# 44. Slice và String

Bây giờ đến phần cực kỳ quan trọng.

String:

```rust
let text = String::from("Hello Rust");
```

Bạn có thể tạo:

```rust
let slice = &text[0..5];
```

Type:

```rust
&str
```

Ví dụ:

```rust
fn main() {
    let text = String::from("Hello Rust");

    let hello = &text[0..5];

    println!("{hello}");
}
```

Kết quả:

```text
Hello
```

---

# 45. `&str` chính là string slice

Hãy nhớ:

```text
&[T]
    ↓
slice của T

&str
    ↓
string slice
```

`&str` là một dạng slice đặc biệt cho UTF-8 string data.

Buổi 28 và 29 chúng ta sẽ đào sâu phần này.

---

# 46. String literal cũng là `&str`

Ví dụ:

```rust
let text = "Hello Rust";
```

`text` có type:

```rust
&str
```

Không phải:

```rust
String
```

---

# 47. Đây là điều bạn cần bắt đầu phân biệt

```rust
let a = String::from("Hello");
```

Type:

```text
String
```

Còn:

```rust
let b = "Hello";
```

type:

```text
&str
```

Mental model:

```text
String
 └── owned string

&str
 └── borrowed string slice
```

---

# 48. Function nhận `&str`

```rust
fn print_text(text: &str) {
    println!("{text}");
}
```

Bạn có thể truyền:

```rust
let a = String::from("Hello");
print_text(&a);
```

hoặc:

```rust
let b = "Hello";
print_text(b);
```

Đây là một API cực kỳ linh hoạt.

---

# 49. Tại sao `&str` mạnh?

Function:

```rust
fn print_text(text: &str)
```

không quan tâm caller có:

```text
String
&str
String slice
string literal
```

Miễn là chúng có thể cung cấp `&str`.

Đây là tư duy API rất quan trọng trong Rust.

---

# 50. Mutable String Slice

Bạn có thể tạo:

```rust
&mut str
```

nhưng đây là phần nâng cao.

Ví dụ với ASCII:

```rust
fn uppercase(text: &mut str) {
    text.make_ascii_uppercase();
}

fn main() {
    let mut text = String::from("hello");

    uppercase(&mut text);

    println!("{text}");
}
```

Kết quả:

```text
HELLO
```

`&mut str` có thể sửa dữ liệu string trong những giới hạn phù hợp.

---

# 51. UTF-8 và Slice

Có một điều rất quan trọng:

Rust String sử dụng UTF-8.

Do đó:

```rust
let text = String::from("Xin chào");
```

không thể tùy tiện:

```rust
&text[0..1]
```

vì byte `1` có thể nằm giữa một ký tự UTF-8.

Có thể panic.

Đây là lý do xử lý `String` trong Rust cần hiểu:

```text
bytes
UTF-8
chars
str
String
```

Chúng ta sẽ học kỹ ở Buổi 28–29.

---

# 52. Ví dụ UTF-8

```rust
fn main() {
    let text = String::from("Xin chào");

    println!("bytes = {}", text.len());
    println!("chars = {}", text.chars().count());
}
```

Hai con số có thể khác nhau.

Vì:

```text
len()
```

đo số byte.

Còn:

```text
chars().count()
```

đếm Unicode scalar values.

---

# 53. Slice và Unicode

Không nên nghĩ:

```text
String
= array of characters
```

Trong Rust:

```text
String
   ↓
UTF-8 bytes
```

và:

```text
&str
   ↓
UTF-8 string slice
```

Đây là lý do slice boundary phải hợp lệ trên UTF-8 boundary.

---

# 54. Ví dụ hoàn chỉnh — Text Processor

```rust
fn first_word(text: &str) -> &str {
    match text.split_whitespace().next() {
        Some(word) => word,
        None => "",
    }
}

fn word_count(text: &str) -> usize {
    text.split_whitespace().count()
}

fn main() {
    let text = String::from("Rust is fast and safe");

    let first = first_word(&text);
    let count = word_count(&text);

    println!("First word: {first}");
    println!("Word count: {count}");
    println!("Original: {text}");
}
```

Kết quả:

```text
First word: Rust
Word count: 5
Original: Rust is fast and safe
```

Điểm quan trọng:

```text
String
   │
   ├── &str → first_word
   │
   └── &str → word_count
```

Không clone.

Không move.

---

# 55. Slice và lifetime

Bạn chưa cần học Lifetime ngay, nhưng cần hiểu một điều:

```rust
fn first(numbers: &[i32]) -> &i32
```

reference trả về phụ thuộc vào lifetime của input.

Ví dụ:

```rust
fn first(numbers: &[i32]) -> &i32 {
    &numbers[0]
}
```

Rust hiểu rằng:

> Reference trả về không thể sống lâu hơn slice mà nó mượn.

Đây là nền tảng để sau này học Lifetime.

---

# 56. Ví dụ `first`

```rust
fn first(numbers: &[i32]) -> Option<&i32> {
    numbers.first()
}

fn main() {
    let numbers = vec![10, 20, 30];

    if let Some(value) = first(&numbers) {
        println!("First = {value}");
    }
}
```

Không ownership transfer.

---

# 57. Slice của struct

```rust
struct User {
    name: String,
    age: u32,
}

fn print_users(users: &[User]) {
    for user in users {
        println!("{} - {}", user.name, user.age);
    }
}

fn main() {
    let users = vec![
        User {
            name: String::from("Alice"),
            age: 20,
        },
        User {
            name: String::from("Bob"),
            age: 25,
        },
    ];

    print_users(&users);
}
```

Đây là pattern rất thực tế.

---

# 58. Slice trong Repository

Ví dụ project quản lý truyện:

```rust
struct Chapter {
    title: String,
    number: u32,
}
```

Repository có:

```rust
struct ChapterRepository {
    chapters: Vec<Chapter>,
}
```

Function:

```rust
fn print_chapters(chapters: &[Chapter]) {
    for chapter in chapters {
        println!("{} - {}", chapter.number, chapter.title);
    }
}
```

Ta có:

```rust
print_chapters(&repository.chapters);
```

Function không cần biết repository dùng `Vec`.

---

# 59. Đây là kiến trúc tốt

Thay vì:

```rust
fn process(chapters: &Vec<Chapter>)
```

nên:

```rust
fn process(chapters: &[Chapter])
```

Bởi vì tầng domain chỉ quan tâm:

> "Tôi có một tập các Chapter."

Không quan tâm:

```text
Vec?
Array?
Slice?
```

---

# 60. Mutable Slice trong Repository

Ví dụ:

```rust
fn mark_all_read(chapters: &mut [Chapter]) {
    for chapter in chapters {
        println!("Processing {}", chapter.title);
    }
}
```

Sau này có thể:

```rust
struct Chapter {
    title: String,
    read: bool,
}
```

và:

```rust
fn mark_all_read(chapters: &mut [Chapter]) {
    for chapter in chapters {
        chapter.read = true;
    }
}
```

---

# 61. So sánh API

### Không tối ưu:

```rust
fn process(data: &Vec<i32>)
```

### Tốt:

```rust
fn process(data: &[i32])
```

### Không tối ưu:

```rust
fn process(data: &mut Vec<i32>)
```

nếu function chỉ sửa phần tử.

### Tốt:

```rust
fn process(data: &mut [i32])
```

Nếu function không cần:

```text
push
pop
reserve
capacity
```

thì không cần biết đó là `Vec`.

---

# 62. Khi nào phải dùng `&Vec<T>`?

Có những trường hợp bạn thực sự cần API của `Vec`:

```rust
push()
pop()
capacity()
reserve()
```

Ví dụ:

```rust
fn add_item(items: &mut Vec<String>, item: String) {
    items.push(item);
}
```

Ở đây:

```text
&mut [String]
```

không có `.push()`.

Vì slice không quản lý capacity.

Do đó:

```rust
&mut Vec<T>
```

có thể phù hợp khi function cần thay đổi kích thước collection.

---

# 63. Đây là distinction rất quan trọng

```text
&[T]
    ↓
read elements

&mut [T]
    ↓
modify elements

&Vec<T>
    ↓
access Vec-specific API

&mut Vec<T>
    ↓
modify elements + grow/shrink Vec
```

---

# 64. Mini Project — Statistics

Tạo:

```rust
fn sum(numbers: &[i32]) -> i32
fn max(numbers: &[i32]) -> Option<i32>
fn min(numbers: &[i32]) -> Option<i32>
fn average(numbers: &[i32]) -> Option<f64>
```

Code hoàn chỉnh:

```rust
fn sum(numbers: &[i32]) -> i32 {
    numbers.iter().sum()
}

fn max(numbers: &[i32]) -> Option<i32> {
    numbers.iter().copied().max()
}

fn min(numbers: &[i32]) -> Option<i32> {
    numbers.iter().copied().min()
}

fn average(numbers: &[i32]) -> Option<f64> {
    if numbers.is_empty() {
        return None;
    }

    Some(sum(numbers) as f64 / numbers.len() as f64)
}

fn main() {
    let numbers = vec![10, 20, 30, 40, 50];

    println!("sum = {}", sum(&numbers));
    println!("max = {:?}", max(&numbers));
    println!("min = {:?}", min(&numbers));
    println!("average = {:?}", average(&numbers));
}
```

Chạy:

```bash
cargo run
```

Kết quả:

```text
sum = 150
max = Some(50)
min = Some(10)
average = Some(30.0)
```

---

# 65. Thử với Array

Không sửa function.

Chỉ thay:

```rust
let numbers = vec![10, 20, 30, 40, 50];
```

bằng:

```rust
let numbers = [10, 20, 30, 40, 50];
```

Function vẫn chạy.

Đây chính là giá trị của:

```rust
&[i32]
```

---

# 66. Thử với một phần collection

```rust
fn main() {
    let numbers = [10, 20, 30, 40, 50];

    let part = &numbers[1..4];

    println!("sum = {}", sum(part));
}
```

Kết quả:

```text
sum = 90
```

vì:

```text
20 + 30 + 40 = 90
```

---

# 67. Thử Mutable Slice

```rust
fn double(numbers: &mut [i32]) {
    for number in numbers {
        *number *= 2;
    }
}

fn main() {
    let mut numbers = [10, 20, 30, 40, 50];

    double(&mut numbers[1..4]);

    println!("{numbers:?}");
}
```

Kết quả:

```text
[10, 40, 60, 80, 50]
```

---

# 68. Bài tập 1 — `find_max`

Viết:

```rust
fn find_max(numbers: &[i32]) -> Option<i32>
```

Ví dụ:

```rust
let numbers = [5, 10, 3, 20, 7];

println!("{:?}", find_max(&numbers));
```

Kết quả:

```text
Some(20)
```

---

# 69. Bài tập 2 — `reverse`

Viết:

```rust
fn reverse(numbers: &mut [i32])
```

Input:

```text
[1, 2, 3, 4, 5]
```

Output:

```text
[5, 4, 3, 2, 1]
```

Gợi ý:

```rust
numbers.reverse();
```

---

# 70. Bài tập 3 — chỉ xử lý một phần

Cho:

```rust
let mut numbers = [1, 2, 3, 4, 5, 6];
```

Hãy viết function:

```rust
fn double(numbers: &mut [i32])
```

sau đó chỉ double:

```text
index 2 → 4
```

Kết quả:

```text
[1, 2, 6, 8, 10, 6]
```

---

# 71. Bài tập 4 — Story

Tạo:

```rust
struct Chapter {
    number: u32,
    title: String,
}
```

Viết:

```rust
fn print_chapters(chapters: &[Chapter])
```

Test với:

```rust
let chapters = vec![
    Chapter {
        number: 1,
        title: String::from("Beginning"),
    },
    Chapter {
        number: 2,
        title: String::from("Journey"),
    },
];
```

---

# 72. Bài tập 5 — Mutable Story Slice

Thêm:

```rust
read: bool
```

vào `Chapter`.

Viết:

```rust
fn mark_all_read(chapters: &mut [Chapter])
```

để:

```text
read = false
```

thành:

```text
read = true
```

---

# 73. Bài tập 6 — API Design

Cho ba function:

```text
display_numbers
sort_numbers
add_number
```

Hãy chọn type parameter phù hợp.

Gợi ý:

```text
display_numbers
→ &[i32]

sort_numbers
→ &mut [i32]

add_number
→ &mut Vec<i32>
```

Tại sao `add_number` không dùng `&mut [i32]`?

Vì nó cần:

```rust
push()
```

để tăng kích thước collection.

---

# 74. Bài tập 7 — String Slice

Viết:

```rust
fn first_word(text: &str) -> &str
```

Ví dụ:

```rust
let text = String::from("Rust is amazing");

let word = first_word(&text);

println!("{word}");
```

Kết quả:

```text
Rust
```

Không được dùng:

```rust
clone()
```

Không được tạo `String` mới.

Đây là bài chuẩn bị trực tiếp cho **Buổi 28 — String**.

---

# 75. Mental Model quan trọng

Hãy ghi nhớ:

```text
Array
[T; N]
   │
   │ borrow
   ▼
&[T]
```

và:

```text
Vec<T>
   │
   │ borrow
   ▼
&[T]
```

và:

```text
String
   │
   │ borrow
   ▼
&str
```

---

# 76. Bức tranh Ownership hiện tại

Sau 27 buổi:

```text
                    Ownership
                        │
              ┌─────────┴─────────┐
              │                   │
             Move              Borrow
                                  │
                         ┌────────┴────────┐
                         │                 │
                        &T              &mut T
                         │                 │
                       READ          READ + WRITE
                         │                 │
                         └────────┬────────┘
                                  │
                                Slice
                                  │
                         ┌────────┴────────┐
                         │                 │
                        &[T]           &mut [T]
                         │
                         │
                       &str
```

---

# 77. Những điều cần thuộc lòng

### 1. Slice không sở hữu dữ liệu

```rust
let slice = &numbers[1..4];
```

`numbers` vẫn là owner.

### 2. Slice thường được dùng qua reference

```rust
&[T]
```

### 3. Mutable slice

```rust
&mut [T]
```

### 4. Slice có thể lấy từ Array

```rust
&array[..]
```

### 5. Slice có thể lấy từ Vec

```rust
&vec[..]
```

### 6. API thường nên ưu tiên

```rust
&[T]
```

thay vì:

```rust
&Vec<T>
```

khi chỉ cần đọc sequence.

### 7. `String` có string slice

```rust
&str
```

---

# 78. Một quy tắc API cực kỳ đáng nhớ

Khi viết function, hãy hỏi:

> **Function cần biết collection cụ thể hay chỉ cần dữ liệu bên trong?**

Nếu chỉ cần dữ liệu:

```rust
fn process(items: &[Item])
```

Nếu cần sửa phần tử:

```rust
fn process(items: &mut [Item])
```

Nếu cần thay đổi kích thước `Vec`:

```rust
fn process(items: &mut Vec<Item>)
```

Đây là một trong những nguyên tắc giúp code Rust của bạn trở nên **idiomatic** thay vì chỉ "compile được".

---

# 79. Roadmap

```text
✓ Buổi 21 — Ownership
✓ Buổi 22 — Move
✓ Buổi 23 — Clone
✓ Buổi 24 — Copy
✓ Buổi 25 — Borrow
✓ Buổi 26 — Mutable Borrow
✓ Buổi 27 — Slice              ← hôm nay
→ Buổi 28 — String
  Buổi 29 — String vs &str
  Buổi 30 — Ownership Deep Dive
```

**Buổi 28 — String** sẽ đi sâu vào `String` từ gốc: heap allocation, UTF-8, `push`, `push_str`, `insert`, `remove`, `replace`, `clear`, `capacity`, `reserve`, `as_str`, `as_bytes`, `chars`, `bytes`, ownership của String và cách Rust quản lý UTF-8.
