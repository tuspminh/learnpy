Unit of Work (UoW) là một mẫu thiết kế (Design Pattern) có nhiệm vụ quản lý vòng đời của một Transaction (Giao dịch) chứa nhiều thao tác thay đổi dữ liệu. Hãy tưởng tượng UoW như một "người giám sát": nó gom tất cả các hành động thêm, sửa, xóa dữ liệu trong một phiên làm việc lại, sau đó thực hiện Commit (lưu tất cả) hoặc Rollback (hủy bỏ tất cả nếu có một bước bị lỗi).

Mục đích cốt lõi của UoW là đảm bảo tính toàn vẹn dữ liệu (ACID) và ngăn chặn tình trạng dữ liệu bị nửa vời (ví dụ: tài khoản A đã bị trừ tiền nhưng tài khoản B chưa nhận được tiền).

* * *

## 📍 Unit of Work nằm ở đâu trong các kiến trúc?

Để hiểu vị trí của UoW, chúng ta cần nhìn vào mối quan hệ giữa Clean Architecture, DDD (Domain-Driven Design) và SOLID.

Mẫu thiết kế này được chia làm 2 phần (Interface và Implementation) và nằm ở 2 lớp khác nhau để đảm bảo nguyên lý Dependency Inversion (D trong SOLID):
    
    
           ┌─────────────────────────────────────────────────────────┐
           │                 PRESENTATION LAYER (API)                │
           └────────────────────────────┬────────────────────────────┘
                                        │ Gọi Use Case
           ┌────────────────────────────▼────────────────────────────┐
           │                 APPLICATION LAYER (Use Case)            │
           │                                                         │
           │  ► Chứa Interface: AbstractUnitOfWork (Trừu tượng)       │ <--- BẠN ĐỊNH NGHĨA NÓ Ở ĐÂY
           └────────────────────────────▲────────────────────────────┘
                                        │
                                        │ Triển khai thực tế (Implement)
           ┌────────────────────────────┴────────────────────────────┐
           │               INFRASTRUCTURE LAYER (Hạ tầng)            │
           │                                                         │
           │  ► Chứa Implementation: SQLAlchemyUnitOfWork            │ <--- CÔNG NGHỆ THỰC TẾ Ở ĐÀY
           └─────────────────────────────────────────────────────────┘
    

## 1\. Trong Clean Architecture (Mô hình củ hành)

  * Về mặt ý niệm (Interface): UoW nằm ở Application Layer (Lớp ứng dụng / Use Case). Tại đây, nó chỉ là một lớp trừu tượng (Abstract Class) định nghĩa các hàm như `commit()`, `rollback()`, `__enter__`, `__exit__`. Lớp Use Case sẽ sử dụng Interface này để điều khiển Transaction mà không cần biết phía sau là công nghệ gì.
  * Về mặt công nghệ (Implementation): UoW nằm ở Infrastructure Layer (Lớp hạ tầng). Đây là nơi mã nguồn thực tế sử dụng các thư viện như `SQLAlchemy Session`, `Django ORM Transaction`, hay `Motor (MongoDB) Session` để hiện thực hóa các lệnh commit/rollback đó.



## 2\. Trong Domain-Driven Design (DDD)

  * UoW đóng vai trò là người bảo vệ tính toàn vẹn của một Aggregate (Cụm thực thể).
  * Trong DDD, bạn không bao giờ lưu từng Entity nhỏ lẻ. Bạn sẽ lưu cả một cụm dữ liệu thông qua Aggregate Root (ví dụ: Lưu một `Đơn hàng` gồm nhiều `Chi tiết đơn hàng`). UoW sẽ bọc toàn bộ quá trình lưu cụm dữ liệu này lại thành một giao dịch duy nhất. Nó giữ vai trò đồng bộ hóa các Repositories khác nhau trong cùng một luồng xử lý.



## 3\. Trong các nguyên lý SOLID

UoW là minh chứng rõ ràng nhất cho nguyên lý D (Dependency Inversion Principle):

  * Thay vì lớp Use Case (mức cao) trực tiếp gọi `db.session.commit()` của SQLAlchemy (mức thấp - chi tiết công nghệ), Use Case sẽ gọi `uow.commit()`.
  * Cả lớp cao và lớp thấp đều phụ thuộc vào một bản thiết kế trừu tượng là `AbstractUnitOfWork`.



* * *

## 💡 Ví dụ ẩn dụ thực tế cho dễ hình dung

Hãy nghĩ về tính năng "Giỏ hàng & Thanh toán":

  1. Hệ thống cần: Trừ tiền khách hàng -> Giảm số lượng tồn kho của sản phẩm -> Tạo hóa đơn.
  2. Nếu không có Unit of Work: Bạn dùng các Repository riêng lẻ. Hệ thống trừ tiền thành công, nhưng đến bước giảm tồn kho thì DB bị sập lỗi. Kết quả: Khách mất tiền nhưng không có hóa đơn, tồn kho giữ nguyên. Hệ thống bị lỗi dữ liệu nghiêm trọng.
  3. Nếu có Unit of Work: UoW sẽ bọc cả 3 hành động trên vào một khối `with uow:`. Nếu bước giảm tồn kho bị lỗi, UoW lập tức ra lệnh Rollback tiền lại cho khách hàng như chưa có chuyện gì xảy ra. Dữ liệu luôn luôn sạch sẽ.



Để giúp bạn áp dụng chính xác mẫu thiết kế này vào dự án của mình, hãy cho tôi biết thêm:

  * Hệ thống của bạn có cần xử lý các tác vụ bất đồng bộ (Asynchronous / Asyncio) không?
  * Bạn có muốn tìm hiểu cách viết Unit Test với FakeUnitOfWork (chạy trên RAM, không cần DB thật) cho kiến trúc này không?