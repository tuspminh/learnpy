Chào bạn! Tiếp tục hành trình nâng cao kỹ năng lập trình Rust, hôm nay chúng ta sẽ hoàn thiện **Phần 3: Cấu trúc & Tổ chức mã**  với **Bài 6: Phương thức (`impl`), Hệ thống Module và Các tập hợp dữ liệu (Collections)**.

Bài học này sẽ giúp bạn biến các Struct/Enum thụ động thành các đối tượng có hành vi linh hoạt, đồng thời biết cách tổ chức dự án lớn và quản lý các chuỗi dữ liệu động.

---

# Bài 6: Phương thức (`impl`), Hệ thống Module & Collections

## 1. Phương thức (Methods) và khối `impl`

Ở Bài 5, chúng ta đã học cách tạo Struct để gom nhóm dữ liệu. Tuy nhiên, để một Struct thực sự hữu ích, nó cần có các **hành vi (behavior)**. Trong Rust, chúng ta định nghĩa các hàm gắn liền với một Struct/Enum bên trong khối **`impl`** (viết tắt của *implementation*).

### Khác biệt giữa Hàm và Phương thức

* **Hàm (Function):** Được gọi độc lập (ví dụ: `cong_hai_so(1, 2)`).
* **Phương thức (Method):** Được gọi trên một instance của Struct/Enum thông qua dấu chấm (ví dụ: `rect.dien_tich()`). Tham số đầu tiên của phương thức luôn là `self`.

```rust
struct Rectangle {
    width: u32,
    height: u32,
}

// Khối triển khai phương thức cho Rectangle
impl Rectangle {
    // Phương thức tính diện tích
    // &self có nghĩa là mượn (borrow) instance hiện tại để đọc dữ liệu
    fn dien_tich(&self) -> u32 {
        self.width * self.height
    }

    // Phương thức kiểm tra xem hình này có chứa trọn hình khác không
    fn chua_duoc(&self, other: &Rectangle) -> bool {
        self.width > other.width && self.height > other.height
    }

    // Associated Function (Hàm gắn kèm): Không nhận &self làm tham số.
    // Thường dùng làm hàm khởi tạo (Constructor).
    fn hinh_vuong(size: u32) -> Self {
        Self {
            width: size,
            height: size,
        }
    }
}

fn main() {
    let rect1 = Rectangle { width: 30, height: 50 };
    let rect2 = Rectangle { width: 10, height: 40 };
    
    // Gọi phương thức
    println!("Diện tích rect1: {}", rect1.dien_tich());
    println!("rect1 có chứa rect2 không? {}", rect1.chua_duoc(&rect2));

    // Gọi Associated Function bằng cú pháp ::
    let sq = Rectangle::hinh_vuong(20);
    println!("Diện tích hình vuông: {}", sq.dien_tich());
}

```

---

## 2. Hệ thống Module (Packages, Crates, Modules)

Khi dự án phình to, bạn không thể viết tất cả code trong một file `src/main.rs`. Rust cung cấp hệ thống phân cấp để quản lý scope và độ riêng tư (privacy):

1. 
**Package:** Một dự án Cargo chứa file `Cargo.toml`.


2. **Crate:** Một cây các Module tạo nên một thư viện (Library crate) hoặc một file thực thi (Binary crate).
3. **Module:** Dùng từ khóa `mod` để gom nhóm code và quản lý quyền truy cập.

### Quy tắc công khai (`pub`)

Mặc định trong Rust, **tất cả code (hàm, struct, enum, module) đều là Riêng tư (Private)**. Nếu muốn cho phép file/module khác sử dụng, bạn phải thêm từ khóa `pub` (public).

```rust
// File: src/main.rs hoặc src/lib.rs

mod quan_ly_kho {
    // Module con công khai
    pub mod san_pham {
        pub struct Product {
            pub name: String, // Trường dữ liệu công khai
            price: f64,       // Trường dữ liệu riêng tư (chỉ truy cập được bên trong san_pham)
        }

        impl Product {
            pub fn new(name: &str, price: f64) -> Product {
                Product {
                    name: String::from(name),
                    price,
                }
            }
        }
    }
}

// Sử dụng từ khóa 'use' để đưa đường dẫn vào scope ngắn gọn hơn
use quan_ly_kho::san_pham::Product;

fn main() {
    let sp = Product::new("Bàn phím cơ", 1500000.0);
    println!("Tên sản phẩm: {}", sp.name);
    // println!("Giá: {}", sp.price); // LỖI! Trường 'price' là private.
}

```

---

## 3. Các tập hợp dữ liệu phổ biến (Collections)

Khác với Array hay Tuple có độ dài cố định , các tập hợp (Collections) trong Rust lưu trữ dữ liệu trên bộ nhớ **Heap**, nghĩa là số lượng phần tử có thể co giãn linh hoạt trong quá trình chương trình chạy.

### A. `Vec<T>` (Vector)

Vector cho phép bạn lưu trữ danh sách các giá trị **cùng kiểu** nằm liền kề nhau trên Heap.

```rust
fn main() {
    // Khởi tạo vector rỗng hoặc dùng macro vec!
    let mut v: Vec<i32> = Vec::new();
    v.push(5);
    v.push(6);
    v.push(7);

    // Cách khởi tạo nhanh bằng macro
    let v2 = vec![1, 2, 3, 4, 5];

    // Đọc phần tử an toàn bằng get() (trả về Option<&T>)
    match v2.get(2) {
        Some(value) => println!("Phần tử thứ 3 là: {}", value),
        None => println!("Không có phần tử ở vị trí này."),
    }

    // Duyệt qua Vector bằng vòng lặp for
    for i in &v {
        println!("{}", i);
    }
}

```

### B. Chuỗi ký tự nâng cao (`String` và `&str`)

Trong Rust, chuỗi ký tự được mã hóa hoàn toàn bằng UTF-8. Có 2 kiểu chuỗi bạn sẽ gặp liên tục:

* `&str` (String Slice): Tham chiếu đến một chuỗi UTF-8 (thường cố định, không sửa đổi).
* `String`: Chuỗi động, được cấp phát trên Heap, có thể thay đổi kích thước.

```rust
fn main() {
    let mut s = String::from("Xin chào");
    s.push_str(", Rust!"); // Nối chuỗi
    println!("{}", s);

    // Nối hai chuỗi bằng toán tử + hoặc format!
    let s1 = String::from("Hello, ");
    let s2 = String::from("World!");
    let s3 = format!("{}{}", s1, s2); // format! không chiếm Ownership của s1, s2
    println!("{}", s3);
}

```

### C. `HashMap<K, V>` (Bảng băm Key-Value)

`HashMap` lưu trữ dữ liệu dưới dạng cặp **Khóa - Giá trị** (Key - Value). Bạn truy cập giá trị thông qua khóa thay vì chỉ số mảng.

```rust
use std::collections::HashMap;

fn main() {
    let mut diem_so = HashMap::new();

    // Thêm dữ liệu
    diem_so.insert(String::from("Toán"), 9);
    diem_so.insert(String::from("Văn"), 8);

    // Truy cập giá trị bằng key
    let mon_hoc = String::from("Toán");
    if let Some(&diem) = diem_so.get(&mon_hoc) {
        println!("Điểm môn {}: {}", mon_hoc, diem);
    }

    // Lặp qua tất cả cặp Key-Value
    for (key, value) in &diem_so {
        println!("{}: {}", key, value);
    }
}

```

---

Như vậy, chúng ta đã hoàn thành trọn vẹn **Phần 3: Cấu trúc & Tổ chức mã**!

Bạn đã sẵn sàng để bước sang **Phần 4: Tư duy nâng cao**  với **Bài 7: Xử lý lỗi (Error Handling với `Result` và `panic!`)** - chìa khóa giúp viết các ứng dụng không bao giờ bị crash bất ngờ chưa?