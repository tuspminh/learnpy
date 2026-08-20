Các Design Patterns phổ biến trong Python

  * **Creational Patterns (Khởi tạo đối tượng):**
    * **Singleton:** Đảm bảo một class chỉ có duy nhất một thể hiện (instance) trong suốt vòng đời ứng dụng.
    * **Factory Method:** Tạo đối tượng mà không cần chỉ định rõ class cụ thể sẽ được khởi tạo.
    * **Builder:** Xây dựng các đối tượng phức tạp từng bước một.
  * **Structural Patterns (Cấu trúc):**
    * **Adapter:** Giúp các interface không tương thích có thể làm việc cùng nhau.
    * **Decorator:** Thêm tính năng mới cho đối tượng mà không làm thay đổi mã nguồn gốc của nó (Python hỗ trợ sẵn cú pháp `@decorator`).
    * **Facade:** Cung cấp một giao diện chung, đơn giản cho một tập hợp các giao diện phức tạp trong một hệ thống con.
  * **Behavioral Patterns (Hành vi):**
    * **Observer:** Cho phép một đối tượng thông báo cho các đối tượng khác (observers) về sự thay đổi trạng thái của nó.
    * **Strategy:** Cho phép thay đổi thuật toán hoặc hành vi lúc chạy (runtime) bằng cách chọn một class chiến lược cụ thể.
    * **State:** Cho phép một đối tượng thay đổi hành vi của nó khi trạng thái nội bộ của nó thay đổi.