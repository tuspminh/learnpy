Khi bạn phải làm việc với các kiểu dữ liệu phức tạp hoặc lặp đi lặp lại nhiều lần (ví dụ: list[str | int | None]), việc viết lại toàn bộ cụm đó sẽ làm mã nguồn bị dài và rối mắt.
Để giải quyết vấn đề này, Python cho phép bạn đặt một cái tên ngắn gọn đại diện cho kiểu dữ liệu phức tạp đó, gọi là Type Alias (Bí danh kiểu).
## Cách tạo Type Alias từ Python 3.12 trở lên (Khuyên dùng)
Từ Python 3.12, một từ khóa mới là type đã được đưa vào ngôn ngữ. Bạn có thể tạo bí danh kiểu trực tiếp mà không cần import từ typing.

# Định nghĩa một bí danh kiểu mới bằng từ khóa typetype ThongTinHocSinh = list[str | int | None]
# Bây giờ bạn có thể dùng tên ngắn gọn này để khai báo biếndanh_sach_1: ThongTinHocSinh = ["An", 18, None]danh_sach_2: ThongTinHocSinh = ["Bình", None, 19]

## Cách viết ở các phiên bản cũ hơn (Python 3.10 - 3.11)
Nếu bạn dùng Python 3.10 hoặc 3.11, từ khóa type chưa xuất hiện. Bạn phải import TypeAlias từ thư viện typing để đánh dấu.

from typing import TypeAlias
# Khai báo kiểu cũThongTinHocSinh: TypeAlias = list[str | int | None]
danh_sach: ThongTinHocSinh = ["An", 18, None]

## Ví dụ thực tế: Giúp hàm gọn gàng hơn
Hãy xem sự khác biệt khi áp dụng Type Alias vào một hàm xử lý dữ liệu bảng (Matrix) chứa tọa độ pixel list[list[int | float]].
## ❌ Cách viết khi CHƯA dùng Type Alias (Rất rối):

def xu_ly_toa_do(danh_sach_diem: list[list[int | float]]) -> list[list[int | float]]:
    # Thao tác xử lý...
    return danh_sach_diem

## Cách viết sạch sẽ hơn VỚI Type Alias (Python 3.12+):

# Đặt tên ngắn gọn cho kiểu dữ liệutype ToaDoPixel = list[list[int | float]]
# Hàm bây giờ cực kỳ ngắn gọn và dễ đọcdef xu_ly_toa_do(danh_sach_diem: ToaDoPixel) -> ToaDoPixel:
    # Thao tác xử lý...
    return danh_sach_diem

------------------------------
Tiếp theo, bạn có muốn tìm hiểu về Literal (Giới hạn phần tử trong danh sách chỉ được phép là một số giá trị cố định, ví dụ danh sách các ngày trong tuần: ["Thứ 2", "Thứ 3", ...]) không?

