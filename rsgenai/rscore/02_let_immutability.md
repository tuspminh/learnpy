Chào bạn! Tinh thần học tập của bạn rất tuyệt vời. Tiếp tục với Nhập môn cơ bản ở Phần 1 của lộ trình, hôm nay chúng ta sẽ giải quyết một trong những khác biệt lớn nhất của Rust so với các ngôn ngữ khác ngay từ những dòng code đầu tiên.

## Bài 2: Biến (Variables), Tính bất biến (Mutability) và Kiểu dữ liệu

### 1. Tính bất biến (Immutability) - An toàn là trên hết

Trong Rust, theo mặc định, **tất cả các biến đều là bất biến (immutable)**. Điều này có nghĩa là khi một giá trị đã được gán cho một tên biến, bạn không thể thay đổi giá trị đó nữa. Đây là cách Rust "ép" bạn viết code an toàn, giúp tránh các lỗi liên quan đến việc dữ liệu bị thay đổi ngoài ý muốn (đặc biệt khi lập trình đa luồng).

```rust
fn main() {
    let x = 5;
    println!("Giá trị của x là: {}", x);
    
    // x = 6; // NẾU BẠN BỎ COMMENT DÒNG NÀY, RUST SẼ BÁO LỖI BIÊN DỊCH NGAY
}

```

### 2. Biến có thể thay đổi (Mutable Variables)

Tất nhiên, lập trình thì phải có lúc cần thay đổi dữ liệu. Để làm điều này, bạn chỉ cần thêm từ khóa `mut` (viết tắt của mutable) ngay sau `let`.

```rust
fn main() {
    let mut x = 5;
    println!("x ban đầu: {}", x);
    
    x = 6; // Hợp lệ vì có từ khóa mut
    println!("x lúc sau: {}", x);
}

```

### 3. Khái niệm Shadowing (Che khuất)

Rust cho phép bạn khai báo lại một biến với cùng một tên bằng cách dùng lại từ khóa `let`. Biến mới sẽ "che khuất" (shadow) biến cũ. Điểm mạnh của Shadowing so với `mut` là bạn có thể tính toán lại giá trị và **thay đổi luôn cả kiểu dữ liệu** của biến đó, trong khi vẫn giữ nguyên tên biến.

```rust
fn main() {
    let spaces = "   "; // Kiểu chuỗi (String) chứa 3 khoảng trắng
    let spaces = spaces.len(); // Khai báo lại (shadow), giờ spaces là kiểu số nguyên có giá trị là 3
    println!("Số khoảng trắng: {}", spaces);
}

```

---

### 4. Kiểu dữ liệu (Data Types)

Rust là ngôn ngữ kiểu tĩnh (statically typed), nghĩa là trình biên dịch phải biết kiểu của tất cả các biến tại thời điểm biên dịch. Tuy nhiên, nó đủ thông minh để tự suy luận kiểu dữ liệu từ giá trị bạn gán mà không cần bạn phải viết rõ ra (trừ vài trường hợp phức tạp).

Dữ liệu trong Rust chia làm hai nhóm chính: Vô hướng (Scalar) và Phức hợp (Compound).

**Nhóm Vô hướng (Scalar Types)**
Đại diện cho một giá trị duy nhất.

* **Số nguyên (Integer):** Số không có phần thập phân.
* **Số thực (Floating-Point):** Số có phần thập phân, bao gồm `f32` và `f64` (mặc định là `f64` vì các CPU hiện đại xử lý nó nhanh không kém `f32` mà lại chính xác hơn).
* **Kiểu Boolean:** Chỉ có hai giá trị `true` hoặc `false` (Ký hiệu là `bool`).
* **Kiểu Ký tự (Character):** Lưu trữ một ký tự duy nhất, sử dụng dấu nháy đơn. Khác với C++, `char` trong Rust chiếm 4 bytes và hỗ trợ mã hóa Unicode (bạn có thể lưu cả emoji). Ví dụ: `let cat = '😻';`

Dưới đây là bảng chi tiết các kiểu số nguyên trong Rust:

| Chiều dài | Có dấu (Cho phép số âm) | Không dấu (Chỉ số dương) |
| --- | --- | --- |
| 8-bit | `i8` | `u8` |
| 32-bit (Mặc định) | `i32` | `u32` |
| 64-bit | `i64` | `u64` |
| Phụ thuộc hệ điều hành (32/64 bit) | `isize` | `usize` |

**Nhóm Phức hợp (Compound Types)**
Gộp nhiều giá trị thành một kiểu duy nhất.

* **Tuple:** Một nhóm các giá trị có thể **khác kiểu nhau**, độ dài cố định.
```rust
let my_tuple: (i32, f64, u8) = (500, 6.4, 1);
let lay_so_nam_tram = my_tuple.0; // Truy cập phần tử bằng dấu chấm và chỉ số vị trí

```


* **Mảng (Array):** Một nhóm các giá trị **cùng kiểu**, độ dài cố định. Nó lưu trữ dữ liệu liền kề nhau trên bộ nhớ (Stack).
```rust
let my_array = [1, 2, 3, 4, 5];
let phan_tu_dau = my_array[0]; // Truy cập bằng ngoặc vuông

```



---

Bạn thấy cách Rust ép buộc sử dụng `mut` để cho phép thay đổi giá trị biến có thú vị không, và bạn đã sẵn sàng để chúng ta bước sang Bài 3 về **Hàm (Functions) và Cấu trúc điều khiển (Control Flow: if, else, loop)** chưa?