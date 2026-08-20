Clean Architecture (Kiến trúc Sạch) do Robert C. Martin (Uncle Bob) giới thiệu là một mô hình kiến trúc phần mềm lấy Domain (Nghiệp vụ cốt lõi) làm trung tâm. Điểm đặc trưng nhất của Clean Architecture là việc tổ chức mã nguồn theo các vòng tròn đồng tâm.

Quy tắc tối thượng của kiến trúc này là Quy tắc phụ thuộc (The Dependency Rule): Vòng tròn bên trong không được phép biết bất kỳ điều gì về vòng tròn bên ngoài. Mọi sự phụ thuộc (mã import) chỉ được phép trỏ từ ngoài vào trong.

* * *

## 🎡 Sơ đồ 4 Lớp Đồng Tâm trong Clean Architecture

Dưới đây là cách phân chia các lớp (layers) từ trong ra ngoài và mối liên kết trực tiếp với dự án Crawl/Đọc sách của bạn:
    
    
                   ┌──────────────────────────────────────────────┐
                   │    LAYER 4: INFRASTRUCTURE (Vòng ngoài cùng)  │
                   │    - SQLite (SQL thuần), requests, PyMuPDF   │
                   │    └──────────────────────────────────────┐  │
                   │       LAYER 3: PRESENTATION (Giao diện)   │  │
                   │       - CLI (Argparse), FastAPI, Flask    │  │
                   │       └────────────────────────────────┐  │  │
                   │          LAYER 2: APPLICATION          │  │  │
                   │          - Use Cases (Tải sách, Đọc)  │  │  │
                   │          └──────────────────────────┐  │  │  │
                   │             LAYER 1: DOMAIN (Lõi)   │  │  │  │
                   │             - Book, Slide, Entities │  │  │  │
                   │             └───────────────────────┘  │  │  │
                   │                                        │  │  │
                   └────────────────────────────────────────┘  │  │
                                                               └──┘
    

* * *

## 🔎 Chi tiết Trách nhiệm của Từng Lớp (Từ Trong ra Ngoài)

## Lớp 1: Domain Layer (Nghiệp vụ cốt lõi - Trung tâm)

Đây là nơi chứa các quy tắc nghiệp vụ cao cấp nhất của doanh nghiệp. Nó hoàn toàn độc lập với công nghệ.

  * Chứa những gì? Entities, Value Objects, Domain Events, và Interfaces (Abstract Classes) của Repositories.
  * Quy tắc Python: Tuyệt đối không import bất kỳ thư viện bên ngoài nào (như `requests`, `fitz`, `sqlite3`). Chỉ dùng Python thuần (`dataclasses`, `typing`, `abc`).
  * Lý do: Cho dù bạn đổi từ ứng dụng Web sang ứng dụng di động, quy tắc thế nào là một cuốn "Sách", thế nào là một "Chương" vẫn không hề thay đổi.



## Lớp 2: Application Layer (Luồng xử lý ứng dụng)

Lớp này chứa các quy tắc nghiệp vụ đặc thù của ứng dụng, thường được gọi là Use Cases hoặc Interactors.

  * Chứa những gì? Các class Use Case (ví dụ: `DownloadBookUseCase`), DTO (Data Transfer Objects), Interface của Unit of Work.
  * Nhiệm vụ: Điều phối luồng dữ liệu đi vào và đi ra khỏi Domain. Nó nhận dữ liệu từ tầng ngoài, gọi Domain Model xử lý, rồi ra lệnh cho Repository lưu trữ.
  * Quy tắc Python: Lớp này biết đến lớp Domain nhưng hoàn toàn mù tịt về việc dữ liệu được lưu vào SQLite hay MySQL, giao diện là CLI hay Web API.



## Lớp 3: Presentation Layer (Giao diện người dùng)

Đây là "bộ mặt" của ứng dụng, chịu trách nhiệm giao tiếp trực tiếp với người dùng hoặc hệ thống bên ngoài.

  * Chứa những gì? Giao diện dòng lệnh CLI (`argparse`), Controllers, Routes của FastAPI/Flask, Validators của dữ liệu đầu vào.
  * Nhiệm vụ: Nhận yêu cầu từ người dùng (HTTP request hoặc câu lệnh Terminal), chuyển đổi dữ liệu thô thành các DTO nguyên thủy, rồi chuyển giao cho Use Case xử lý.



## Lớp 4: Infrastructure Layer (Hạ tầng và Công nghệ)

Vòng tròn ngoài cùng là nơi chứa tất cả các chi tiết công nghệ dễ thay đổi.

  * Chứa những gì? Lớp triển khai thực tế (Implementation) của Repositories (`SQLiteBookRepository`), cấu hình kết nối Database, thư viện cào web (`BeautifulSoup`, `requests`), thư viện xử lý file (`PyMuPDF`).
  * Nhiệm vụ: Hiện thực hóa các bản thiết kế trừu tượng do tầng Domain/Application yêu cầu.



* * *

## ⚙️ Luồng đi của Dữ liệu và Cách Đảo ngược Phụ thuộc (D trong SOLID)

Nhìn vào sơ đồ, bạn sẽ thấy một mâu thuẫn: Use Case (Lớp 2) cần gọi hàm `.save_metadata()` của SQLite Repository (Lớp 4) để lưu sách. Nhưng quy tắc kiến trúc cấm Lớp 2 import Lớp 4!

Clean Architecture giải quyết bài toán này bằng Dependency Inversion (Đảo ngược phụ thuộc) thông qua cơ chế Dependency Injection (Tiêm phụ thuộc):
    
    
    TẦNG APPLICATION (Lớp 2)
      │  ► Định nghĩa bản thiết kế: AbstractClass BookRepository
      ▼
    TẦNG INFRASTRUCTURE (Lớp 4)
         ► Kế thừa và viết code thực tế: class SQLiteBookRepository(BookRepository)
    

Khi ứng dụng khởi chạy (`main.py` ở tầng Presentation), nó đóng vai trò là "Người lắp ráp Lego":

  1. Khởi tạo đối tượng cụ thể ở tầng hạ tầng: `repo = SQLiteBookRepository(conn)`
  2. Tiêm (Inject) đối tượng này vào Constructor của Use Case: `use_case = DownloadBookUseCase(book_repo=repo)`
  3. Nhờ vậy, Use Case có thể gọi `self.book_repo.save_metadata()` mà bản thân nó vẫn chỉ nghĩ rằng mình đang tương tác với Interface trừu tượng ở tầng ứng dụng.



* * *

## 💎 5 Lợi ích Tối thượng giúp Clean Architecture Đáng giá từng dòng Code

  1. Độc lập với Framework: Bạn không bị trói buộc vào FastAPI hay Django. Framework chỉ là công cụ ở vòng ngoài cùng. Nếu Django lỗi thời, bạn chuyển sang FastAPI trong vài giờ vì toàn bộ logic nghiệp vụ nằm ở lớp trong không bị dính một dòng code Django nào.
  2. Độc lập với Database: Bạn có thể bắt đầu dự án với SQLite cho nhẹ nhàng. Khi hệ thống lớn lên, bạn đổi sang PostgreSQL hoặc MongoDB bằng cách viết một lớp Repository mới. Tầng nghiệp vụ không cần sửa, không cần test lại.
  3. Độc lập với UI: Bạn có thể dễ dàng thay đổi giao diện CLI thành giao diện Web, hoặc chạy bằng các câu lệnh tự động (Cron job) mà không làm ảnh hưởng đến lõi hệ thống.
  4. Siêu dễ viết Unit Test (High Testability): Bạn có thể test toàn bộ logic kinh doanh phức tạp nhất của Use Case và Domain mà không cần bật Database thật, không cần mạng internet. Chỉ cần tiêm các `FakeRepository` chạy trên RAM vào (như bài pytest trước) là xong.
  5. Dễ dàng làm việc nhóm: Do các lớp được phân tách ranh giới rõ ràng, một lập trình viên có thể tập trung viết logic cào web (Tầng 4), trong khi một lập trình viên khác viết quy tắc tính toán slide (Tầng 1) mà không bao giờ bị xung đột code (Conflict git) với nhau.



Ứng dụng của bạn hiện tại đã áp dụng trọn vẹn từ Clean Architecture, DDD, SOLID cho đến CQRS và Async Events. Bạn có muốn tổng kết lại toàn bộ mã nguồn thành một cấu trúc thư mục hoàn chỉnh cuối cùng để sẵn sàng đóng gói dự án không?