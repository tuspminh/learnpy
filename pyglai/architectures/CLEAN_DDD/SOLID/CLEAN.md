Clean Architecture (Kiến trúc Sạch) do _Robert C. Martin_ (Uncle Bob) giới thiệu vào năm 2012. Đây là một mô hình kiến trúc tiến hóa cao hơn, bao quát hơn Hexagonal Architecture, nhưng chia sẻ chung một lý tưởng cốt lõi: Độc lập với công nghệ và đặt Logic nghiệp vụ làm trung tâm hệ thống.

Điểm đặc trưng nhất của Clean Architecture là cấu trúc các tầng theo các vòng tròn đồng tâm và tuân thủ tuyệt đối một quy tắc tối thượng gọi là Quy tắc phụ thuộc (The Dependency Rule).

* * *

## 1\. Sơ đồ các vòng tròn đồng tâm (The Dependency Rule)

Trong Clean Architecture, hệ thống được chia làm 4 tầng chính từ trong ra ngoài:
    
    
           ┌──────────────────────────────────────────────┐
           │ TẦNG NGOÀI CÙNG (Frameworks & Drivers)        │
           │  - Khai báo Database thực tế, Web, UI, Devices│
           │       ▼ (Phụ thuộc vào)                      │
           │ ┌──────────────────────────────────────────┐ │
           │ │ TẦNG TRUNG GIAN (Interface Adapters)     │ │
           │ │  - Controllers, Presenters, Gateways     │ │
           │ │       ▼ (Phụ thuộc vào)                  │ │
           │ │ ┌──────────────────────────────────────┐ │ │
           │ │ │ TẦNG ỨNG DỤNG (Use Cases)            │ │ │
           │ │ │  - Logic vận hành đặc thù của app    │ │ │
           │ │ │       ▼ (Phụ thuộc vào)              │ │ │
           │ │ │ ┌──────────────────────────────────┐ │ │ │
           │ │ │ │ TẦNG TRUNG TÂM (Entities)         │ │ │ │
           │ │ │ │  - Nghiệp vụ cốt lõi (Enterprise) │ │ │ │
           │ │ │ └──────────────────────────────────┘ │ │ │
           │ │ └──────────────────────────────────────┘ │ │
           │ └──────────────────────────────────────────┘ │
           └──────────────────────────────────────────────┘
    

👉 Quy tắc phụ thuộc (The Dependency Rule): Mọi mã nguồn ở vòng tròn bên ngoài có thể biết và phụ thuộc vào vòng tròn bên trong. Tuy nhiên, mã nguồn ở vòng tròn bên trong tuyệt đối KHÔNG ĐƯỢC BIẾT bất cứ điều gì ở vòng tròn bên ngoài. (Ví dụ: Class ở tầng Entities hay Use Cases không được phép `import` bất kỳ thứ gì từ tầng Web hay Database).

* * *

## 2\. Chi tiết 4 tầng trong Clean Architecture

## Tầng 1: Entities (Nghiệp vụ doanh nghiệp cốt lõi)

  * Nhiệm vụ: Chứa các đối tượng nghiệp vụ (Business Objects) và các quy tắc tính toán cốt lõi nhất, có thể dùng chung cho nhiều ứng dụng khác nhau của doanh nghiệp.
  * Đặc điểm: Tầng này "sống thọ" nhất. Dù bạn đổi ứng dụng từ Web sang App Mobile, hay đổi luồng vận hành thì các quy tắc toán học/nghiệp vụ ở đây vẫn giữ nguyên.
  * _Ví dụ trong Python:_ Một class `User` với hàm kiểm tra xem user có đủ tuổi đăng ký hay không.



## Tầng 2: Use Cases (Nghiệp vụ đặc thù của ứng dụng)

  * Nhiệm vụ: Chứa logic vận hành hệ thống, điều phối dòng dữ liệu đi từ và đến các Entities để đạt được mục tiêu của một tính năng cụ thể.
  * Đặc điểm: Nếu giao diện ứng dụng thay đổi, tầng này không bị ảnh hưởng. Nhưng nếu luồng nghiệp vụ thay đổi (ví dụ: bổ sung bước kiểm tra số dư trước khi thanh toán), code ở đây sẽ thay đổi.
  * _Ví dụ trong Python:_ Class `RegisterUserUseCase` nhận thông tin, gọi Entity kiểm tra hợp lệ, rồi gọi cổng lưu trữ để lưu vào DB.



## Tầng 3: Interface Adapters (Bộ chuyển đổi giao diện)

  * Nhiệm vụ: Làm cầu nối ngôn ngữ giữa tầng Use Cases/Entities và tầng Framework bên ngoài. Nó chuyển đổi dữ liệu từ định dạng tiện lợi cho DB/Web thành định dạng tiện lợi cho Use Cases (và ngược lại).
  * Thành phần: Controllers (nhận request), Presenters (chuẩn hóa response trả về giao diện), Gateways (các Interface/Repositories để Use Case gọi dữ liệu).



## Tầng 4: Frameworks & Drivers (Tầng ngoài cùng)

  * Nhiệm vụ: Đây là nơi chứa các công nghệ chi tiết, các công cụ, thư viện mà bạn chọn để chạy ứng dụng.
  * Thành phần: Cấu hình Web Framework (FastAPI, Django), Hệ quản trị CSDL (Postgres, MongoDB), các SDK bên thứ ba (AWS, Firebase). Tầng này gần như chỉ gồm code glue (gắn kết) và cấu hình.



* * *

## 3\. Cách dữ liệu vượt qua biên giới các tầng (Data Crossing Boundaries)

Một câu hỏi phổ biến: _Nếu Use Case nằm ở tầng trong và không được phép biết tầng DB ở ngoài, làm sao Use Case lưu được dữ liệu?_

Câu trả lời chính là ứng dụng Dependency Inversion Principle (DIP):

  1. Tầng Use Cases định nghĩa một Interface (Ví dụ: `UserRepository`).
  2. Tầng Interface Adapters/Frameworks hiện thực hóa Interface đó bằng một Class thực tế (Ví dụ: `SQLAlchemyUserRepository`).
  3. Khi luồng xử lý chạy qua, dữ liệu được đóng gói thành các cấu trúc đơn giản như DTO (Data Transfer Object) hoặc dict thuần trong Python để truyền qua biên giới các tầng, tuyệt đối không truyền trực tiếp các Model của Database (như SQLAlchemy Model) vào tầng trong.



* * *

## 4\. So sánh nhanh: Clean Architecture vs Hexagonal Architecture

Dù có vẻ bề ngoài khác nhau, hai kiến trúc này có mối quan hệ họ hàng rất gần gũi.

Tiêu chí| Hexagonal Architecture| Clean Architecture  
---|---|---  
Bản chất| Tập trung vào mối quan hệ giữa Bên trong (Core) và Bên ngoài (Infrastructure) thông qua các cổng.| Tập trung vào việc phân rã hệ thống thành nhiều tầng đồng tâm có độ trừu tượng tăng dần.  
Cách phân chia| Chia làm 2 phần lớn: Core (Domain + Use Cases) và Khung bên ngoài (Adapters).| Chia làm 4 tầng rất rạch ròi (`Entities` tách riêng khỏi `Use Cases`).  
Ứng dụng| Phù hợp với các hệ thống hướng sự kiện, tích hợp nhiều dịch vụ bên ngoài độc lập.| Phù hợp với các hệ thống doanh nghiệp lớn, có quy tắc nghiệp vụ (Business Rules) cực kỳ phức tạp.  
  
_Thực tế:_ Nhiều lập trình viên thường gộp chung ý tưởng của cả hai: Dùng các vòng tròn đồng tâm của Clean Architecture để phân tầng nội bộ bên trong lõi Hexagon.

* * *

Nếu bạn muốn tiếp tục làm chủ mô hình này, hãy cho tôi biết:

  * Bạn có muốn xem cách thiết lập DTO (Data Transfer Object) bằng `Pydantic` hoặc `dataclasses` để truyền dữ liệu an toàn giữa các tầng của Clean Architecture không?
  * Hay bạn muốn tìm hiểu cách xử lý Exceptions (Ngoại lệ) từ tầng ngoài cùng (DB lỗi) quay ngược trở lại tầng trong cùng một cách sạch sẽ?