Tuyệt vời! Dưới đây là một bài tập thực hành tổng hợp dựa trên một tình huống thực tế: Xây dựng hệ thống quản lý ví điện tử.
Bài tập này sẽ giúp bạn vận dụng toàn bộ các kiến thức từ đầu đến giờ: viết cú pháp hiện đại (Python 3.10+), không import typing khi không cần thiết, trộn kiểu |, dùng Literal, và Final.
------------------------------
## 📝 Bài tập: Quản lý lịch sử giao dịch
Bạn hãy viết code gợi ý kiểu dữ liệu (Type Hinting) cho bài toán sau:

   1. Bước 1 (Tạo Type Alias): Định nghĩa một kiểu dữ liệu có tên là LoaiGiaoDich. Kiểu này chỉ cho phép nhận 1 trong 3 chuỗi cố định: "nạp tiền", "rút tiền", hoặc "chuyển khoản".
   2. Bước 2 (Tạo Type Alias nâng cao): Định nghĩa một kiểu dữ liệu tên là LichSuGiaoDich. Đây là một Danh sách (List) chứa các phần tử. Mỗi phần tử có thể là LoaiGiaoDich (chuỗi trạng thái), hoặc là một số tiền (kiểu int), hoặc có thể bị khuyết (None).
   3. Bước 3 (Khai báo hằng số): Tạo một biến hằng số tên là DANH_SACH_MA_QUOC_GIA chứa các mã quốc gia được hỗ trợ là "VN", "US", "JP". Hãy đảm bảo biến này không thể bị gán lại và không thể thêm/bớt phần tử.
   4. Bước 4 (Định nghĩa hàm): Viết một hàm tên là xu_ly_vi.
   * Hàm này nhận vào tham số là một LichSuGiaoDich.
      * Hàm này trả về một Danh sách các số nguyên (list[int]) chứa các số tiền hợp lệ, hoặc trả về None nếu danh sách đầu vào không có số tiền nào.
   
------------------------------
## 💡 Gợi ý nhỏ trước khi viết:

* Hãy nhớ xem công cụ nào cần import từ typing (Literal, Final), và công cụ nào không cần import ở Python hiện đại (list, |, từ khóa type).
* Để tạo hằng số hoàn toàn đóng băng ở Bước 3, hãy kết hợp Final và tuple.

Bạn hãy thử viết code ra hoặc hình dung cách viết trong đầu, sau đó phản hồi lại để đối chiếu với đáp án chi tiết nhé!

