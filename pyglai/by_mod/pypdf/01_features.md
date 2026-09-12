`pypdf` là một thư viện thuần Python (Pure-Python), miễn phí và mã nguồn mở. Điểm mạnh lớn nhất của nó là sự gọn nhẹ, dễ cài đặt (không phụ thuộc vào các thư viện C phức tạp) và rất mạnh về các tác vụ thao tác cấu trúc file (manipulation).

Dưới đây là bảng tổng hợp chi tiết các khả năng và giới hạn của `pypdf`:

## 1\. Quản lý cấu trúc file (Thế mạnh lớn nhất)

  * Chia nhỏ và Ghép nối (Split & Merge): Trích xuất một vài trang cụ thể, chia nhỏ file PDF lớn hoặc gộp nhiều file PDF lại thành một.
  * Trộn trang (Xen kẽ): Hỗ trợ trộn các trang từ các file khác nhau theo quy luật (ví dụ: xen kẽ trang chẵn/lẻ).
  * Xoay và Cắt trang (Rotate & Crop): Xoay trang theo các góc 90, 180, 270 độ; thay đổi kích thước vùng hiển thị (MediaBox, CropBox) của trang.



## 2\. Trích xuất thông tin (Extraction)

  * Đọc Metadata: Lấy các thông tin tổng quan của file như Tiêu đề (Title), Tác giả (Author), Người tạo (Creator), Ngày tạo...
  * Trích xuất văn bản (Text Extraction): Đọc được chữ từ các file PDF text kỹ thuật số (không đọc được từ file PDF dạng ảnh quét).
  * Trích xuất hình ảnh: Trích xuất các file ảnh gốc được nhúng bên trong trang PDF để lưu ra ngoài.



## 3\. Bảo mật và Mã hóa (Security)

  * Mã hóa (Encryption): Đặt mật khẩu mở file (User password) hoặc mật khẩu phân quyền (Owner password - giới hạn quyền in ấn, sao chép).
  * Giải mã (Decryption): Đọc và xử lý các file PDF có bảo mật (nếu bạn có mật khẩu).



## 4\. Xử lý nâng cao (Form & Interactive)

  * Điền Form PDF (AcroForms): Đọc các trường dữ liệu trong form PDF và tự động điền giá trị vào form đó.
  * Quản lý Bookmarks (Outlines): Đọc, tạo mới, chỉnh sửa hoặc xóa danh mục/mục lục liên kết trong file PDF.
  * Thêm Watermark (Hình mờ): Chèn logo, chữ chìm hoặc số trang đè lên các trang có sẵn bằng tính năng `merge_page`.



* * *

## ❌ Những giới hạn của `pypdf` (Không làm được hoặc làm rất yếu)

  * Không tạo được PDF từ đầu: Bạn không thể dùng `pypdf` để tự gõ văn bản, vẽ bảng, thiết kế layout rồi xuất ra PDF (ReportLab sẽ làm tốt việc này).
  * Không có OCR: Không thể đọc chữ từ file PDF scan/ảnh chụp.
  * Trích xuất bảng biểu kém: Không tự nhận diện và bóc tách dữ liệu dạng bảng thành cấu trúc hàng/cột hoàn chỉnh được như `pdfplumber`.



Tùy thuộc vào nhu cầu thực tế, bạn có muốn tôi hướng dẫn sâu hơn về cách điền dữ liệu vào Form PDF tự động hay cách chèn Watermark/Logo hàng loạt bằng `pypdf` không?