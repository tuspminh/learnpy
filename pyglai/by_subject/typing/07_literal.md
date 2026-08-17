Trong Python, Literal là một công cụ gợi ý kiểu dữ liệu đặc biệt. Nó giúp bạn giới hạn một giá trị hoặc các phần tử trong danh sách chỉ được phép là một số giá trị cụ thể cố định (như chuỗi ký tự cụ thể hoặc số cụ thể), thay vì chấp nhận toàn bộ kiểu dữ liệu đó.
Vì Literal kiểm soát giá trị chính xác (chứ không chỉ là kiểu dữ liệu), bạn vẫn cần import Literal từ thư viện typing trên mọi phiên bản Python.
## Cách khai báo danh sách với Literal## 1. Giới hạn danh sách trạng thái cố định
Giả sử bạn làm một danh sách quản lý trạng thái của các đơn hàng. Bạn chỉ muốn danh sách này chứa các chuỗi "pending", "shipping", hoặc "delivered", các chuỗi khác đều là sai.

from typing import Literal
# Định nghĩa kiểu trạng thái hợp lệtype TrangThaiDonHang = Literal["pending", "shipping", "delivered"]
# Khai báo danh sách chỉ chứa các trạng thái trêndanh_sach_don: list[TrangThaiDonHang] = ["pending", "delivered", "pending"]
# Lỗi nếu dùng công cụ kiểm tra kiểu (như Mypy hoặc IDE):# danh_sach_don = ["pending", "canceled"] -> IDE sẽ báo đỏ ở "canceled"

## 2. Giới hạn các tùy chọn cấu hình hệ thống
Bạn có một danh sách chứa các cổng kết nối hoặc các chế độ hệ thống (ví dụ: chỉ cho phép số 80 hoặc 443).

from typing import Literal
type CongKetNoiAnToan = Literal[80, 443]
danh_sach_port: list[CongKetNoiAnToan] = [80, 443, 80]

## Ví dụ thực tế: Kết hợp hàm và kiểm tra giá trị đầu vào
Khi bạn kết hợp Literal vào hàm, IDE của bạn sẽ tự động gợi ý (Auto-complete) chính xác các từ bạn được phép điền, ngăn chặn việc gõ sai chính tả.

from typing import Literal
# Định nghĩa các quyền hợp lệ của người dùngtype QuyenUser = Literal["admin", "editor", "viewer"]
def kiem_tra_quyen(danh_sach_user: list[QuyenUser]) -> bool:
    for quyen in danh_sach_user:
        if quyen == "admin":
            return True
    return False
# Sử dụng đúngusers = ["viewer", "admin"] # IDE hiểu và hỗ trợ gợi ý chữ "admin", "viewer"
print(kiem_tra_quyen(users))
# Nếu bạn gõ nhầm: users = ["admint"] -> IDE sẽ cảnh báo ngay lập tức!

------------------------------
Bây giờ bạn đã nắm rất chắc lộ trình từ cách dùng list cơ bản, trộn kiểu dữ liệu (|), đặt bí danh (type), đến giới hạn giá trị (Literal).
Bạn có muốn chuyển sang tìm hiểu về Final (Để khai báo một danh sách hằng số, không cho phép gán lại hoặc chỉnh sửa) không?

