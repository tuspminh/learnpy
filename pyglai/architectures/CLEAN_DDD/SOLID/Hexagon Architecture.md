Hexagonal Architecture (Kiến trúc Lục giác), hay còn gọi là mô hình Ports and Adapters, là một kiểu kiến trúc phần mềm do _Alistair Cockburn_ giới thiệu vào năm 2005.

Mục tiêu cốt lõi của kiến trúc này là tách biệt hoàn toàn Logic nghiệp vụ (Domain/Core) khỏi các yếu tố công nghệ bên ngoài (UI, Cơ sở dữ liệu, Framework, Web Service). Nhờ đó, phần mềm có thể dễ dàng chạy thử nghiệm độc lập hoặc thay đổi công nghệ mà không làm ảnh hưởng đến mã nguồn cốt lõi.

* * *

## 1\. Tại sao lại gọi là "Kiến trúc Lục giác"?

Hình lục giác (Hexagon) chỉ là một hình ảnh ẩn dụ, không mang ý nghĩa hệ thống phải có đúng 6 cạnh hay 6 phần.

Alistair Cockburn chọn hình lục giác vì nó đại diện cho một thực thể có nhiều bề mặt tiếp xúc. Mỗi cạnh của lục giác đại diện cho một cổng kết nối (Port), cho phép các tác nhân bên ngoài tương tác với phần lõi bên trong theo những mục đích khác nhau.

* * *

## 2\. Hai thành phần cốt lõi: Ports và Adapters

Điểm mấu chốt của kiến trúc này là sự phân chia rạch ròi giữa Interface (Port) và Chi tiết triển khai (Adapter).
    
    
           TÁC NHÂN BÊN NGOÀI
      (Người dùng, Cronjob, Test)
                  │
                  ▼
        ┌───────────────────┐
        │  Driving Adapter  │ (Ví dụ: FastAPI Controller, CLI)
        └─────────┬─────────┘
                  │ (Gọi)
                  ▼
        ┌───────────────────┐
        │   Driving Port    │ (Inbound Interface - do Core định nghĩa)
        ├───────────────────┤
        │                   │
        │    CORE LOGIC     │ (Domain / Use Cases)
        │                   │
        ├───────────────────┤
        │   Driven Port     │ (Outbound Interface - do Core định nghĩa)
        └─────────┬─────────┘
                  │ (Triển khai / Cài đặt)
                  ▼
        ┌───────────────────┐
        │  Driven Adapter   │ (Ví dụ: SQLAlchemy Repository, AWS SES Class)
        └───────────────────┘
                  │
                  ▼
           HỆ THỐNG BÊN NGOÀI
        (PostgreSQL, Mailchimp)
    

## A. Ports (Cổng)

Port là các Interface (hoặc lớp trừu tượng lớp `ABC` trong Python) nằm hoàn toàn bên trong tầng Core. Port quy định hệ thống _muốn làm gì_ chứ không nói _làm như thế nào_. Có hai loại Port:

  * Driving Ports (Cổng chủ động / Inbound): Là các cổng mở ra cho bên ngoài gọi vào Core. Ví dụ: Interface của một Use Case (`CreateOrderUseCase`).
  * Driven Ports (Cổng bị động / Outbound): Là các cổng do Core định nghĩa để tương tác với bên ngoài. Ví dụ: Interface dùng để lưu dữ liệu (`OrderRepository`) hay gửi tin nhắn (`SMSNotification`).



## B. Adapters (Bộ chuyển đổi)

Adapter là các lớp triển khai cụ thể (Implementation) nằm ở tầng bên ngoài (Infrastructure). Chúng bọc xung quanh các Port để chuyển đổi dữ liệu từ định dạng bên ngoài thành dữ liệu Core hiểu được (và ngược lại).

  * Driving Adapters (Primary Adapters): Lắng nghe yêu cầu từ tác nhân bên ngoài (Người dùng, Hệ thống khác), chuyển yêu cầu đó thành lệnh và gọi vào Driving Port. _Ví dụ: FastAPI router, GraphQL resolver, CLI script._
  * Driven Adapters (Secondary Adapters): Triển khai mã nguồn thực tế cho Driven Port. Khi Core gọi Port này, Adapter sẽ thực thi nhiệm vụ kỹ thuật cụ thể. _Ví dụ: Lớp cấu hình`PostgreSQLRepository` dùng SQLAlchemy, lớp `S3FileStorage` dùng boto3._



* * *

## 3\. Nguyên lý Đảo ngược phụ thuộc (DIP) vận hành thế nào?

Nếu không có DIP, tầng Core sẽ phải `import` các thư viện bên ngoài để gọi trực tiếp (ví dụ: Core gọi thư viện Postgres). Điều này làm Core bị dính chặt vào công nghệ.

Trong Hexagonal Architecture:

  1. Tầng Core tự định nghĩa ra Driven Port (Lớp trừu tượng).
  2. Tầng Infrastructure (Adapter) `import` Core để hiện thực hóa Port đó.
  3. Khi chạy ứng dụng, ta dùng Dependency Injection (DI) để tiêm Adapter vào Core.



👉 Mọi phụ thuộc đều hướng vào tâm (Core). Core không biết và không quan tâm thế giới bên ngoài đang dùng công nghệ gì.

* * *

## 4\. Cấu trúc thư mục (Folder Structure) chuẩn trong Python

Dưới đây là cách tổ chức một dự án Python áp dụng Hexagonal Architecture phổ biến:
    
    
    my_project/
    │
    ├── src/
    │   ├── domain/               # ── TẦNG CORE (Không import thư viện ngoài)
    │   │   ├── entities.py       # Chứa các Object nghiệp vụ (Ví dụ: Order, Product)
    │   │   ├── exceptions.py     # Lỗi nghiệp vụ chuyên biệt
    │   │   └── ports.py          # Định nghĩa TẤT CẢ Driving & Driven Ports (Interface)
    │   │
    │   ├── application/          # ── TẦNG ỨNG DỤNG (Chứa Use Cases điều phối)
    │   │   └── use_cases.py      # Xử lý luồng nghiệp vụ lớn thông qua các Ports
    │   │
    │   ├── infrastructure/       # ── TẦNG NGOÀI (Chứa các Adapters công nghệ)
    │   │   ├── adapters/
    │   │   │   ├── db_postgres.py# Triển khai Driven Port (Lưu DB thật)
    │   │   │   └── email_aws.py  # Triển khai Driven Port (Gửi email thật)
    │   │   └── controllers/
    │   │       ├── api_v1.py     # Driving Adapter (FastAPI Endpoints)
    │   │       └── cli.py        # Driving Adapter (Command Line Tools)
    │   │
    │   ├── container.py          # Nơi cấu hình Dependency Injection (Ráp nối Ports & Adapters)
    │   └── main.py               # Điểm kích hoạt ứng dụng
    │
    └── tests/                    # ── TẦNG KIỂM THỬ (Cực kỳ sạch sẽ vì có các Port)
        ├── test_domain.py
        └── test_use_cases.py     # Test sử dụng Mock Adapters mà không cần DB thật
    

* * *

## 5\. Ưu điểm và Nhược điểm lớn nhất

## Ưu điểm 👍

  * Cực kỳ dễ Test: Bạn có thể viết Unit Test cho toàn bộ luồng nghiệp vụ phức tạp của Use Case trong vài mili-giây bằng cách viết một `MockAdapter` thay thế cho DB/Email mà không cần cài Docker hay Network.
  * Độc lập công nghệ: Đổi từ MySQL sang MongoDB, hay từ FastAPI sang một framework mới nổi trong tương lai? Bạn chỉ cần viết lại tầng `infrastructure`, giữ nguyên 100% logic phần `domain`.
  * Tránh lỗi dây chuyền: Việc thay đổi giao diện (UI) hay nâng cấp phiên bản thư viện Database không bao giờ làm hỏng logic tính toán tiền hay logic tạo đơn hàng.



## Nhược điểm 👎

  * Tăng sự rườm rà (Boilerplate Code): Với mỗi tính năng, bạn phải tạo thêm Interface (Port), tạo Class triển khai (Adapter), rồi lại viết code cấu hình DI.
  * Tốn thời gian ánh xạ dữ liệu (Mapping): Bạn thường phải chuyển đổi qua lại giữa Model của Database (ví dụ SQLAlchemy Model) và Model nghiệp vụ của Domain (ví dụ Pydantic/Dataclass Entity) để tránh làm rò rỉ chi tiết DB vào tầng lõi.
  * Overkill cho dự án nhỏ: Nếu dự án của bạn chỉ làm các tác vụ CRUD cơ bản (chỉ đọc và ghi dữ liệu lên bảng), Hexagonal Architecture sẽ làm phức tạp hóa vấn đề một cách không cần thiết.



* * *

Nếu bạn muốn đi sâu hơn vào triển khai thực tế, hãy cho tôi biết:

  * Bạn có muốn xem code minh họa cách Mapping dữ liệu từ một DB Model sang một Domain Entity mà không vi phạm quy tắc của Hexagonal không?
  * Hoặc bạn muốn tìm hiểu cách áp dụng Unit of Work pattern để quản lý DB Transaction xuyên suốt qua nhiều Port trong mô hình này?