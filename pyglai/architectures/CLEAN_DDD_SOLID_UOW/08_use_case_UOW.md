Unit of Work (UoW) thường bị hiểu nhầm là chỉ dành riêng cho Database (DB) vì các thư viện ORM nổi tiếng (như SQLAlchemy trong Python, Hibernate trong Java, hay Entity Framework trong .NET) đã tích hợp sẵn và sử dụng nó quá phổ biến.

Tuy nhiên, trên thực tế, Unit of Work là một mẫu thiết kế mang tính kiến trúc hệ thống (Architectural Pattern). Nó có thể áp dụng cho bất kỳ hệ thống nào cần quản lý một tập hợp các hành động thay đổi trạng thái theo cơ chế "Tất cả hoặc không có gì" (All-or-Nothing / Atomicity).

Dưới đây là các trường hợp thực tế ngoài Database áp dụng hoàn hảo mẫu thiết kế Unit of Work:

* * *

## 1\. Quản lý Hệ thống Tệp tin (File System Transactions)

Khi ứng dụng của bạn cần xử lý nhiều file cùng lúc (ví dụ: giải nén một gói tài liệu, ghi file cấu hình, sinh file PDF báo cáo). Nếu một file bị lỗi, bạn muốn hệ thống tự động xóa sạch các file đã tạo trước đó để tránh để lại file rác trên ổ cứng.
    
    
    # Minh họa UoW cho File System
    class FileSystemUnitOfWork:
        def __init__(self):
            self.created_files = []
    
        def __enter__(self):
            return self
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None:
                self.rollback()  # Xóa sạch các file đã lỡ tạo nếu có lỗi
            else:
                self.commit()    # Xác nhận hoàn thành
    
        def create_file(self, path, content):
            with open(path, "w") as f:
                f.write(content)
            self.created_files.append(path)
    
        def rollback(self):
            import os
            for path in self.created_files:
                if os.path.exists(path):
                    os.remove(path)
    

* * *

## 2\. Gọi các API bên ngoài liên hoàn (Distributed Transactions / Saga)

Hãy tưởng tượng luồng Đặt vé máy bay + Đặt phòng khách sạn:

  1. Ứng dụng gọi API bên hãng bay để giữ chỗ (Book Flight) thành công.
  2. Ứng dụng tiếp tục gọi API bên khách sạn để đặt phòng (Book Hotel) nhưng khách sạn báo Hết phòng (Lỗi).
  3. Lúc này, UoW sẽ kích hoạt hàm `rollback()`. Trong môi trường API, `rollback` có nghĩa là gọi một API hủy vé (Cancel Flight) để hoàn tác tác vụ đầu tiên, đảm bảo khách hàng không bị mất tiền oan.



* * *

## 3\. Gửi tin nhắn hàng loạt vào Message Queue / Event Broker (Kafka, RabbitMQ)

Trong kiến trúc hướng sự kiện (Event-Driven Architecture), một Use Case có thể sinh ra nhiều sự kiện (Events) khác nhau (ví dụ: `UserRegistered`, `WelcomeEmailSent`, `PointsRewarded`).

  * Nếu bạn bắn lẻ tẻ từng Event vào Kafka, và Use Case bị crash ở giữa chừng, các hệ thống khác sẽ nhận được Event sai lệch.
  * Giải pháp UoW: Gom tất cả các Event vào một hàng đợi tạm thời trên RAM. Chỉ khi nào toàn bộ Use Case chạy thành công, UoW mới "bấm nút" đẩy toàn bộ Event này vào Kafka một lượt (`Commit`).



* * *

## 4\. Quản lý State trong Ứng dụng Frontend (như Redux, Vuex, State Machine)

Khi người dùng thực hiện một thao tác phức tạp trên giao diện (như chỉnh sửa ảnh: Áp dụng bộ lọc -> Cắt ảnh -> Thêm văn bản).

  * UoW sẽ lưu giữ các thay đổi này trong một trạng thái tạm thời (Draft State).
  * Nếu người dùng bấm Save, UoW sẽ commit và cập nhật vào State chính của ứng dụng.
  * Nếu người dùng bấm Cancel, UoW sẽ rollback (hủy bỏ Draft State), giao diện quay về trạng thái ban đầu mà không làm biến đổi dữ liệu chính.



* * *

## 5\. Đồng bộ hóa giữa nhiều nguồn dữ liệu (Multi-datasource Sync)

Khi ứng dụng của bạn vừa phải lưu thông tin người dùng vào SQLite, vừa phải đẩy dữ liệu chỉ mục (Index) sang Elasticsearch để phục vụ tìm kiếm nhanh. UoW sẽ bọc cả hai hành động này lại:

  * Nếu SQLite lưu thành công nhưng Elasticsearch bị sập ──► UoW thực hiện xóa dữ liệu vừa lưu ở SQLite (Rollback) để đảm bảo hai bên không bị lệch pha dữ liệu.



* * *

## 📌 Tiêu chí để quyết định có nên dùng Unit of Work hay không?

Để biết một trường hợp có cần áp dụng UoW hay không, bạn hãy tự hỏi 3 câu hỏi sau:

  1. Có tính chất dây chuyền không? (Thao tác này thành công thì thao tác sau mới được chạy, hoặc nhiều thao tác phải đi cùng nhau).
  2. Có cần tính toàn vẹn (Atomicity) không? (Nếu một bước ở giữa bị lỗi, hệ thống có bị rơi vào trạng thái "nửa vời", sinh ra dữ liệu rác hoặc logic sai không?).
  3. Có thể hoàn tác (Rollback / Compensate) được không? (Bạn có cách nào để xóa file, hủy API, hoặc rollback DB để đưa hệ thống về trạng thái cũ không?).



Nếu câu trả lời là CÓ, thì đó chính là nơi Unit of Work cần được áp dụng, bất kể đó là DB, File, Mạng hay API.

Để giúp bạn hình dung rõ hơn về khả năng mở rộng này, bạn có muốn tích hợp thêm một Trình gửi Email hoặc Hệ thống tạo File log vào Unit of Work của ứng dụng đọc truyện hiện tại không?