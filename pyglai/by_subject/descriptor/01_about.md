Trong Python, descriptor (bộ mô tả) là một đối tượng thuộc tính cho phép bạn kiểm soát cách lấy, gán hoặc xóa giá trị của một thuộc tính khác. Một đối tượng được coi là descriptor khi nó thực thi ít nhất một trong các phương thức đặc biệt của giao thức: __get__, __set__, hoặc __delete__. [1, 2, 3] 
## Giao thức Descriptor

* __get__(self, instance, owner): Dùng khi bạn truy cập (đọc) giá trị của thuộc tính.
* __set__(self, instance, value): Dùng khi bạn gán (ghi) giá trị mới cho thuộc tính.
* __delete__(self, instance): Dùng khi bạn xóa thuộc tính.

## Phân loại Descriptor

* Non-data descriptor: Chỉ có phương thức __get__. Ít gặp hơn, dùng trong các phương thức (methods) của class.
* Data descriptor: Có chứa __set__ hoặc __delete__ (hoặc cả hai). Có độ ưu tiên cao hơn từ điển dữ liệu (__dict__) của instance.

## Ứng dụng thực tế

* Xây dựng các hàm cốt lõi bên trong Python như @property, classmethod, và staticmethod.
* Kiểm tra tính hợp lệ dữ liệu (ví dụ: ép kiểu, chặn giá trị âm cho tuổi hoặc giá trị số dương).
* Tái sử dụng logic kiểm soát thuộc tính cho nhiều class khác nhau mà không cần lặp lại code. Bạn có thể tìm hiểu sâu hơn trên [Real Python Descriptors Guide](https://realpython.com/python-descriptors/). [3] 

Nếu bạn muốn, tôi có thể cung cấp:

* Một ví dụ code cụ thể về cách tạo một custom data descriptor.
* Cách phân biệt chi tiết giữa data descriptor và non-data descriptor.

Bạn muốn tìm hiểu phần nào tiếp theo?

[1] [https://kb.pavietnam.vn](https://kb.pavietnam.vn/descriptors-trong-python-la-gi.html)
[2] [https://vn.linkedin.com](https://vn.linkedin.com/pulse/python-magic-metaclasses-descriptors-oscar-martin-bahamonde-mu%C3%B1oz?tl=vi)
[3] [https://realpython.com](https://translate.google.com/translate?u=https://realpython.com/python-descriptors/&hl=vi&sl=en&tl=vi&client=sge)
