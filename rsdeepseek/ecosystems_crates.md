Trong hệ sinh thái Rust, các thư viện bên ngoài được gọi là crates và được quản lý tập trung tại trang web crates.io. Kể từ năm 2026, cộng đồng Rust đã chuẩn hóa một bộ công cụ "bất di bất dịch" mà hầu như dự án thực tế nào cũng cần dùng tới [v1, v2].
Dưới đây là các crate phổ biến nhất được chia theo từng nhóm tính năng cụ thể:
------------------------------
## 1. Nhóm Tiện Ích Cốt Lõi (Core Utilities)## tokio – Lập trình bất đồng bộ (Async Runtime)
Rust không có sẵn bộ thực thi async trong thư viện chuẩn. tokio chính là nền tảng tiêu chuẩn để viết các ứng dụng mạng, web server, hoặc các tác vụ cần xử lý đồng thời (concurrency) với hiệu năng cực cao.

* Ứng dụng: Làm backend server, gọi API bất đồng bộ.

## serde – Mã hóa và giải mã dữ liệu (Serialization)
Đây là crate mạnh mẽ và phổ biến nhất dùng để chuyển đổi qua lại giữa các cấu trúc dữ liệu trong Rust (Struct, Enum) sang các định dạng như JSON, YAML, TOML, hay Binary và ngược lại.

* Ứng dụng: Đi kèm với hai crate phụ là serde_json và toml.

## rand – Tạo số ngẫu nhiên
Như bạn đã thấy ở ví dụ đầu tiên, rand cung cấp toàn bộ các công cụ từ tạo số, ký tự ngẫu nhiên cơ bản cho đến các thuật toán băm ngẫu nhiên bảo mật cao (cryptographically secure).
------------------------------
## 2. Nhóm Phát Triển Ứng Dụng Web & Backend## axum hoặc actix-web – Web Framework

* axum: Framework được phát triển bởi chính đội ngũ làm ra tokio. Nó có thiết kế cực kỳ hiện đại, tận dụng tối đa hệ thống kiểu dữ liệu (types) và macro của Rust, hiện đang là lựa chọn số một cho các dự án mới.
* actix-web: Một framework đời đầu, có tốc độ xử lý thuộc top nhanh nhất thế giới trong các bảng xếp hạng benchmark.

## reqwest – Thư viện gọi API (HTTP Client)
Tương tự như axios trong JavaScript hay requests trong Python. Nó giúp bạn gửi các yêu cầu GET, POST HTTP tới các server khác một cách dễ dàng (hỗ trợ cả async và đồng bộ).
## sqlx hoặc diesel – Thao tác với Cơ sở dữ liệu (Database)

* sqlx: Cho phép viết mã SQL thuần, kiểm tra lỗi cú pháp SQL ngay khi biên dịch (compile-time) và hỗ trợ async hoàn toàn (PostgreSQL, MySQL, SQLite).
* diesel: Một bộ ORM truyền thống mạnh mẽ, giúp bạn thao tác với database thông qua code Rust thuần túy mà không cần viết SQL.

------------------------------
## 3. Nhóm Xử Lý Lỗi, Ghi Log & Hệ Thống## anyhow và thiserror – Quản lý lỗi chuyên nghiệp

* anyhow: Dùng cho các ứng dụng (Applications). Nó cho phép bạn gom tất cả các loại lỗi khác nhau về một kiểu duy nhất là anyhow::Result, cực kỳ hợp khi đi chung với toán tử ?.
* thiserror: Dùng khi bạn tự viết thư viện (Libraries). Nó giúp bạn tự định nghĩa ra các kiểu lỗi riêng của mình một cách tường minh.

## tracing hoặc log – Ghi nhật ký hệ thống (Logging)
Thay vì dùng println! để in thông tin ra màn hình, các dự án thực tế dùng tracing để ghi lại nhật ký hoạt động (INFO, WARN, ERROR) của chương trình, giúp dễ dàng kiểm tra lỗi khi phần mềm đã chạy trên máy chủ.
## clap – Viết ứng dụng giao diện dòng lệnh (CLI)
Nếu bạn muốn viết một công cụ chạy bằng terminal (như git, cargo), clap sẽ tự động bóc tách các tham số người dùng nhập vào (arguments, flags) và tự tạo trang hướng dẫn --help rất chuyên nghiệp.
------------------------------
## Cách sử dụng một Crate bất kỳ:
Để thêm một crate vào dự án, bạn chỉ cần chạy lệnh sau trong terminal tại thư mục dự án của mình:

cargo add <tên_crate># Ví dụ: cargo add tokio serde --features full

Hoặc khai báo thủ công trong file Cargo.toml:

[dependencies]
serde = { version = "1.0", features = ["derive"] }

Bạn có muốn chọn ra một nhóm cụ thể (ví dụ như xây dựng một web server cơ bản hoặc đọc ghi file JSON) để chúng ta cùng viết một đoạn mã ví dụ thực tế sử dụng các crate này không? Hãy cho tôi biết nhé!

