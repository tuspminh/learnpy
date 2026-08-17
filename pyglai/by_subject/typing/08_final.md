Trong Python, Final là một công cụ gợi ý kiểu dữ liệu dùng để khai báo một hằng số. Khi bạn đánh dấu một biến hoặc một danh sách là Final, bạn đang báo cho công cụ kiểm tra kiểu dữ liệu (như Mypy hoặc IDE) biết rằng: giá trị này không được phép thay đổi hoặc gán lại trong suốt quá trình chương trình chạy.
Vì Final kiểm soát tính chất không thay đổi của biến, bạn vẫn cần import Final từ thư viện typing trên mọi phiên bản Python.
## Lưu ý quan trọng khi dùng Final với Danh sách (List)
Trong Python, danh sách (list) là một kiểu dữ liệu có thể thay đổi (mutable). Khi bạn dùng Final với list, nó sẽ ngăn bạn gán lại một danh sách mới cho biến đó, nhưng mặc định không ngăn được việc bạn chỉnh sửa các phần tử bên trong (như append hoặc pop).
Hãy xem ví dụ dưới đây để hiểu rõ cơ chế này:

from typing import Final
# 1. Khai báo một danh sách hằng sốCAU_HINH_HE_THONG: Final[list[str]] = ["localhost", "db_prod"]
# ❌ LỖI GÁN LẠI (IDE/Mypy sẽ báo lỗi đỏ ngay lập tức)CAU_HINH_HE_THONG = ["127.0.0.1", "db_dev"] 
# ⚠️ HÀNH VI MẶC ĐỊNH: Thêm phần tử thì Python vẫn cho phép chạy
CAU_HINH_HE_THONG.append("redis_cache") 

## Giải pháp tối ưu: Hằng số danh sách thực sự
Nếu bạn muốn tạo một danh sách hằng số hoàn toàn đóng băng (không cho gán lại và cũng không cho thêm/bớt phần tử), bạn nên kết hợp Final với kiểu tuple hoặc dùng Sequence.
## Cách 1: Kết hợp Final với tuple (Khuyên dùng cho danh sách hằng số)
Vì tuple là kiểu dữ liệu không thể chỉnh sửa (immutable), kết hợp với Final sẽ tạo ra một hằng số tuyệt đối.

from typing import Final
# Một danh sách mã lỗi cố định không thể sửa đổiMA_LOI_DON_HANG: Final[tuple[int, ...]] = (404, 500, 403)
# ❌ IDE và Python đều sẽ báo lỗi nếu bạn cố tình sửa:# MA_LOI_DON_HANG = (200,) --> Lỗi gán lại (do Final)# MA_LOI_DON_HANG.append(200) --> Lỗi không có hàm append (do tuple)

## Cách 2: Sử dụng Sequence để chỉ cho phép đọc (Read-only)
Khi truyền danh sách vào một hàm và bạn muốn đảm bảo hàm đó chỉ được đọc dữ liệu chứ không được sửa đổi danh sách gốc của bạn.

from typing import Finalfrom collections.abc import Sequence
# Sequence giúp biến này trở thành dữ liệu chỉ đọc (Read-only)DANH_SACH_KHOA: Final[Sequence[str]] = ["ID", "Name", "Age"]
# DANH_SACH_KHOA.append("Gender") -> IDE sẽ báo lỗi ngay vì Sequence không hỗ trợ append

------------------------------
Đến đây bạn đã nắm trọn vẹn các kỹ thuật gợi ý kiểu dữ liệu nâng cao và hiện đại nhất cho Danh sách trong Python (từ list cơ bản, trộn kiểu |, TypeAlias, Literal cho đến Final).
Bạn có muốn làm một bài tập thực hành nhỏ tổng hợp lại tất cả các kiến thức này để kiểm tra mức độ ghi nhớ không?

