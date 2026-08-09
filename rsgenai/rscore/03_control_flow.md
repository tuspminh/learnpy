Chào mừng bạn đến với Bài 3! Sau khi đã nắm được cách lưu trữ dữ liệu với các biến, hôm nay chúng ta sẽ học cách đóng gói code để tái sử dụng (Hàm) và cách điều hướng tư duy logic của chương trình (Cấu trúc điều khiển).

Đây là phần có nhiều điểm thú vị vì Rust định nghĩa lại một vài khái niệm quen thuộc theo cách rất chặt chẽ.

---

## 1. Hàm (Functions)

Hàm trong Rust được khai báo bằng từ khóa `fn`. Bạn có thể đặt hàm ở bất kỳ đâu, miễn là trình biên dịch có thể nhìn thấy nó (không cần phải khai báo hàm trước khi gọi như C/C++).

### Truyền tham số và trả về giá trị

Rust yêu cầu bạn **bắt buộc phải khai báo kiểu dữ liệu** cho các tham số truyền vào hàm và kiểu dữ liệu trả về (nếu có).

```rust
fn main() {
    let ket_qua = cong_hai_so(5, 7);
    println!("Kết quả là: {}", ket_qua);
}

// Hàm nhận vào 2 tham số kiểu i32 và trả về một giá trị kiểu i32
fn cong_hai_so(x: i32, y: i32) -> i32 {
    x + y
}

```

### Câu lệnh (Statements) vs. Biểu thức (Expressions)

Hãy nhìn kỹ vào dòng `x + y` trong hàm `cong_hai_so` ở trên. Bạn có thấy **không có dấu chấm phẩy (`;`)** ở cuối không? Đây là một đặc trưng cốt lõi của Rust:

* **Câu lệnh (Statement):** Là các hành động thực hiện một thao tác nào đó nhưng **không trả về giá trị**. Ví dụ: `let y = 6;` là một câu lệnh. Các câu lệnh kết thúc bằng dấu `;`.
* **Biểu thức (Expression):** Là đoạn code tính toán ra và **trả về một giá trị**. Ví dụ: `5 + 6` là một biểu thức. Khi bạn gọi một hàm, đó cũng là một biểu thức.

Trong Rust, nếu dòng cuối cùng của một hàm không có dấu `;`, nó tự động trở thành giá trị trả về của hàm đó. Bạn vẫn có thể dùng từ khóa `return x + y;`, nhưng cách viết bỏ dấu `;` (gọi là *implicit return*) là chuẩn mực (idiomatic) được tất cả các lập trình viên Rust sử dụng.

---

## 2. Cấu trúc rẽ nhánh (if / else)

Cấu trúc `if` trong Rust khá giống các ngôn ngữ khác, nhưng có hai điểm khác biệt lớn:

1. Bạn không cần ngoặc đơn `()` bọc quanh điều kiện.
2. Điều kiện **bắt buộc phải là kiểu `bool**` (true/false). Rust không tự động ép kiểu các số khác 0 thành `true` như C/C++ hay JavaScript.

```rust
let number = 7;

if number % 2 == 0 {
    println!("Số chẵn");
} else if number % 3 == 0 {
    println!("Chia hết cho 3");
} else {
    println!("Không thuộc các trường hợp trên");
}

```

### Dùng `if` trong một câu lệnh `let`

Vì `if` trong Rust là một **biểu thức** (expression), nó có thể trả về giá trị. Nhờ đó, bạn có thể gán thẳng kết quả của một khối `if` cho một biến:

```rust
let condition = true;
// Biến number sẽ nhận giá trị 5 nếu condition là true, ngược lại là 6
let number = if condition { 5 } else { 6 }; 

// Lưu ý: Các nhánh trả về (5 và 6) phải có CÙNG kiểu dữ liệu!

```

---

## 3. Vòng lặp (Loops)

Rust cung cấp 3 loại vòng lặp: `loop`, `while`, và `for`.

### `loop` (Vòng lặp vô hạn)

Từ khóa `loop` sẽ chạy khối code bên trong nó mãi mãi, cho đến khi bạn gọi lệnh `break` để thoát ra một cách rõ ràng.

```rust
let mut counter = 0;

let result = loop {
    counter += 1;

    if counter == 10 {
        // Break có thể mang theo giá trị để trả về cho vòng lặp!
        break counter * 2; 
    }
};
println!("Kết quả từ vòng lặp: {}", result); // In ra 20

```

### `while` (Lặp có điều kiện)

Dùng khi bạn muốn vòng lặp chạy chừng nào một điều kiện vẫn còn đúng.

```rust
let mut number = 3;

while number != 0 {
    println!("{}!", number);
    number -= 1;
}
println!("Phóng tàu!");

```

### `for` (Vòng lặp an toàn và phổ biến nhất)

Mặc dù bạn có thể dùng `while` để duyệt qua một mảng, nhưng cách đó dễ gây lỗi (nếu index vượt quá độ dài mảng) và chậm hơn (do Rust phải kiểm tra biên mảng ở mỗi bước lặp). Thay vào đó, hãy dùng `for`:

```rust
let a = [10, 20, 30, 40, 50];

// Duyệt qua từng phần tử trong mảng
for element in a {
    println!("Giá trị là: {}", element);
}

// Lặp theo một khoảng (Range) từ 1 đến 3 (không bao gồm 4)
for number in 1..4 {
    println!("Đếm: {}", number);
}

```

> **Mẹo:** Dùng `1..=4` nếu bạn muốn lấy cả số 4 (inclusive range).

---

Đến đây, bạn đã có đủ công cụ cơ bản để viết những chương trình tính toán logic trong Rust. Nhưng điều làm nên sự khác biệt thực sự của Rust sắp đến rồi.