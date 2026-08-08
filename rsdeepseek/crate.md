Trong hệ sinh thái của ngôn ngữ Rust, một Crate chính là một đơn vị biên dịch nhỏ nhất.
Nói một cách dễ hiểu hơn, crate tương đương với một thư viện (library) hoặc một gói mã nguồn (package/module) trong các ngôn ngữ khác (như npm package trong Node.js, pip package trong Python, hay jar trong Java).
Mọi đoạn mã Rust bạn viết hoặc tải về từ internet đều tồn tại dưới hình thức một Crate.
------------------------------
## 1. Phân loại Crate
Rust chia crate làm hai loại chính dựa trên mục đích sử dụng:

* Binary Crate (Crate nhị phân):
* Là một chương trình có thể biên dịch thành một file chạy được (file .exe trên Windows hoặc file chạy trên Linux/Mac).
   * Bắt buộc phải có một file tên là main.rs và chứa hàm fn main().
* Library Crate (Crate thư viện):
* Là một tập hợp các đoạn mã (hàm, struct, enum) được viết ra nhằm mục đích cho các chương trình khác tái sử dụng, không thể chạy trực tiếp độc lập.
   * Bắt buộc phải có một file tên là lib.rs và không có hàm main().

------------------------------
## 2. Mối quan hệ giữa Crate, Package và Cargo
Để quản lý dự án, Rust sử dụng một công cụ gọi là Cargo (trình quản lý gói). Cấu trúc quản lý được phân cấp như sau:

* Crate: Là file mã nguồn đơn lẻ hoặc một nhóm file được biên dịch cùng nhau (như main.rs hoặc lib.rs).
* Package (Gói): Là một dự án hoàn chỉnh do Cargo quản lý, được định nghĩa bởi file Cargo.toml. Một Package có thể chứa nhiều Crate nhị phân nhưng chỉ được chứa tối đa một Crate thư viện.

------------------------------
## 3. Ví dụ trực quan
Khi bạn tạo một dự án mới bằng lệnh:

cargo new my_project

Cargo sẽ tạo ra một Package tên là my_project. Bên trong thư mục src/, nó tự động tạo ra file main.rs. Bản thân file main.rs này chính là một Binary Crate thuộc sở hữu của package đó.
Nếu bạn tải một thư viện như rand hay serde từ trang crates.io về dùng, nghĩa là bạn đang tích hợp các Library Crate của người khác vào dự án của mình để tiết kiệm thời gian viết code.
Bạn có muốn thử tạo một Crate thư viện cục bộ do chính mình viết để kết nối và sử dụng bên trong một Crate nhị phân không? Hãy cho tôi biết nhé!

