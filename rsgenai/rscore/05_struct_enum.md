Chào bạn! Chúc mừng bạn đã vượt qua thử thách khó nhằn nhất mang tên Ownership. Dù ban đầu khái niệm đó hơi "khó chịu", nhưng nó chính là chiếc chìa khóa vạn năng giúp code của bạn an toàn tuyệt đối.

Hôm nay, chúng ta sẽ bước sang **Phần 3: Cấu trúc & Tổ chức mã**. Bài học này sẽ tập trung vào **Structs, Enums và Pattern Matching**. Đây là những công cụ tuyệt vời để mô hình hóa thế giới thực và tổ chức dữ liệu trong Rust.

---

## Bài 5: Structs và Enums

### 1. Structs (Cấu trúc dữ liệu)

Nếu Tuple (đã học ở Bài 2) là một nhóm các giá trị ẩn danh, thì **Struct** cho phép bạn đặt tên cho từng phần dữ liệu, giúp mã nguồn rõ ràng và mang nhiều ý nghĩa hơn. Nó khá giống với `class` (dữ liệu) hoặc `struct` trong các ngôn ngữ như C++ hay Java.

**Khai báo và khởi tạo Struct:**

```rust
// Định nghĩa một Struct
struct User {
    username: String,
    email: String,
    sign_in_count: u64,
    active: bool,
}

fn main() {
    // Khởi tạo một đối tượng (instance) từ Struct
    // Phải thêm mut nếu muốn thay đổi thông tin sau này
    let mut user1 = User {
        email: String::from("hoc_rust@example.com"),
        username: String::from("rust_dev"),
        active: true,
        sign_in_count: 1,
    };

    // Truy cập và thay đổi trường dữ liệu bằng dấu chấm (.)
    user1.email = String::from("email_moi@example.com");
    println!("Username: {}", user1.username);
}

```

**Cú pháp cập nhật Struct (Struct Update Syntax):**
Khi bạn muốn tạo một instance mới từ một instance cũ nhưng chỉ thay đổi vài trường, Rust cung cấp cú pháp `..` rất tiện lợi.

```rust
let user2 = User {
    email: String::from("user2@example.com"),
    username: String::from("user2_dev"),
    ..user1 // Lấy các giá trị còn lại (active, sign_in_count) từ user1
};

```

---

### 2. Enums (Kiểu liệt kê)

Trong khi Struct dùng để gom các nhóm dữ liệu lại (A **và** B **và** C), thì Enum dùng để định nghĩa một kiểu dữ liệu có thể là một trong nhiều trường hợp khác nhau (A **hoặc** B **hoặc** C).

```rust
// Định nghĩa một Enum đơn giản
enum IpAddrKind {
    V4,
    V6,
}

let four = IpAddrKind::V4;
let six = IpAddrKind::V6;

```

**Sức mạnh thực sự của Enum trong Rust:**
Không giống như Enum trong C/C++ (chỉ là các con số được đặt tên), Enum trong Rust cho phép bạn **đính kèm dữ liệu trực tiếp** vào từng biến thể (variant). Các biến thể trong cùng một Enum thậm chí có thể chứa các kiểu dữ liệu khác nhau!

```rust
enum Message {
    Quit,                       // Không chứa dữ liệu
    Move { x: i32, y: i32 },    // Chứa một Struct vô danh
    Write(String),              // Chứa một String
    ChangeColor(i32, i32, i32), // Chứa 3 số nguyên (Tuple)
}

let msg = Message::Write(String::from("Chào mừng bạn!"));

```

---

### 3. Ứng dụng đỉnh cao: Enum `Option` và xử lý Null

Rust **không có giá trị `null**` (hay `nil`). Người tạo ra khái niệm Null đã từng gọi nó là "sai lầm tỷ đô" vì nó gây ra vô số lỗi sập chương trình (NullReferenceException).

Thay vào đó, Rust dùng một Enum tích hợp sẵn tên là `Option` để diễn đạt ý tưởng "có thể có giá trị, hoặc không có gì cả":

```rust
// Định nghĩa ngầm định của Option trong thư viện chuẩn:
// enum Option<T> {
//     Some(T), // Có chứa một giá trị kiểu T
//     None,    // Không có gì cả (tương đương với Null)
// }

let some_number = Some(5);
let some_string = Some("A string");
let absent_number: Option<i32> = None; // Bắt buộc phải khai báo kiểu khi gán None

```

Lợi ích? Trình biên dịch Rust sẽ *bắt buộc* bạn phải xử lý trường hợp `None` trước khi cho phép bạn sử dụng giá trị thực sự bên trong `Some`. Do đó, lỗi do quên kiểm tra Null bị loại bỏ hoàn toàn tại thời điểm biên dịch!

---

### 4. Pattern Matching với từ khóa `match`

Để làm việc với Enums (đặc biệt là lấy dữ liệu ra khỏi Enum như `Option`), bạn không thể dùng `if/else` thông thường. Rust cung cấp một cấu trúc điều khiển có tên là `match` (khá giống `switch/case` nhưng mạnh hơn vạn lần).

`match` so khớp một giá trị với một loạt các mẫu (patterns). **Quy tắc quan trọng:** `match` trong Rust phải "exhaustive" (đầy đủ), nghĩa là bạn bắt buộc phải liệt kê ra mọi trường hợp có thể xảy ra của Enum, nếu thiếu, code sẽ báo lỗi.

```rust
enum Coin {
    Penny,
    Nickel,
    Dime,
    Quarter(String), // Quý này thuộc tiểu bang nào
}

fn value_in_cents(coin: Coin) -> u8 {
    match coin {
        Coin::Penny => {
            println!("Đồng xu may mắn!");
            1 // Trả về 1
        }
        Coin::Nickel => 5,
        Coin::Dime => 10,
        Coin::Quarter(state) => { // Lấy dữ liệu String được đính kèm ra ngoài biến state
            println!("Đồng quarter của bang: {}", state);
            25
        }
    }
}

```