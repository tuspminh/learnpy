Trong Python, Callable (đọc là Cáp-lơ-bồ) là một công cụ gợi ý kiểu dữ liệu (Type Hinting) dùng để đại diện cho bất kỳ thực thể nào có thể gọi được bằng cặp dấu ngoặc tròn () [typing-callable].
Các đối tượng được coi là Callable bao gồm: Hàm thông thường (functions), Hàm ẩn danh (lambda), Phương thức của Class (methods), hoặc bản thân một Class (khi ta gọi Class để tạo Object).
Từ Python 3.9 trở lên, bạn nên import Callable từ thư viện tiêu chuẩn collections.abc thay vì import từ typing [typing-callable].
------------------------------
## 1. Cú pháp cơ bản của Callable
Cú pháp chuẩn để định nghĩa một Callable bao gồm hai phần: Kiểu dữ liệu của các tham số đầu vào (đặt trong ngoặc vuông []) và Kiểu dữ liệu trả về [typing-callable].
$$\text{Callable[ [Kiểu\_Tham\_Số\_1, Kiểu\_Tham\_Số\_2, ...], Kiểu\_Trả\_Về ]}$$ 
## Các ví dụ khai báo cơ bản:

* Callable[[int, int], int]: Nhận vào 2 số nguyên, trả về 1 số nguyên [typing-callable].
* Callable[[str], None]: Nhận vào 1 chuỗi, không trả về gì cả (None) [typing-callable].
* Callable[[], bool]: Không nhận tham số đầu vào, trả về giá trị Đúng/Sai (bool) [typing-callable].

------------------------------
## 2. Các trường hợp sử dụng Callable thực tế## Trường hợp 1: Hàm nhận vào một hàm khác làm bộ lọc (Callback)
Giả sử bạn viết một hàm tính toán tổng quát, nhận vào một danh sách số và một quy tắc lọc (là một hàm Callable).

from collections.abc import Callable
# Hàm nhan vao mot danh sach và một ham loc dieu kiendef loc_va_in(danh_sach: list[int], dieu_kien: Callable[[int], bool]) -> None:
    for so in danh_sach:
        if dieu_kien(so): # Gọi hàm Callable ở đây
            print(f"Thỏa mãn: {so}")
# Định nghĩa các hàm điều kiện khác nhaudef la_so_chan(n: int) -> bool:
    return n % 2 == 0
# Sử dụngnumbers = [1, 2, 3, 4, 5, 6]
loc_va_in(numbers, la_so_chan) 

## Trường hợp 2: Hàm trả về một hàm khác (Factory Function)
Đây chính là nền tảng cốt lõi giúp bạn hiểu cách viết Decorator mà chúng ta vừa học ở phần trước.

from collections.abc import Callable
# Hàm tạo ra hàm nhân (Multiplier Factory)def tao_ham_nhan(he_so: int) -> Callable[[int], int]:
    def ham_nhan(x: int) -> int:
        return x * he_so
    return ham_nhan
# Tạo ra hàm nhân đôi và hàm nhân banhan_doi = tao_ham_nhan(2)nhan_ba = tao_ham_nhan(3)

print(nhan_doi(5))  # Kết quả: 10
print(nhan_ba(5))   # Kết quả: 15

------------------------------
## 3. Kỹ thuật nâng cao với Callable## Cách viết tắt khi không quan tâm đến tham số đầu vào: ...
Nếu bạn viết một Decorator tổng quát có thể bọc cho mọi loại hàm (bất kể hàm đó có bao nhiêu tham số, kiểu dữ liệu gì), bạn có thể dùng dấu ba chấm ... để đại diện cho danh sách tham số [typing-callable].

from collections.abc import Callablefrom typing import Any
# Chấp nhận hàm gốc có BẤT KỲ tham số nào (...), miễn là trả về kiểu dữ liệu bất kỳ (Any)def bo_trang_tri_don_gian(ham_goc: Callable[..., Any]) -> Callable[..., Any]:
    def ham_boc(*args: Any, **kwargs: Any) -> Any:
        return ham_goc(*args, **kwargs)
    return ham_boc

## Kiểm tra một đối tượng có phải là Callable hay không bằng code?
Ngoài việc dùng để gợi ý kiểu dữ liệu (Type Hinting), Python có sẵn một hàm runtime tên là callable() giúp bạn kiểm tra xem một biến có thể bấm nút gọi () được hay không.

def ham_test():
    return "Hello"
bien_chuoi = "Hello"

print(callable(ham_test))   # Kết quả: True (Gọi được bằng ham_test())
print(callable(bien_chuoi)) # Kết quả: False (Không thể gọi bien_chuoi())

------------------------------
Bạn đã thấy mối liên kết chặt chẽ giữa Callable và các kiến thức trước đó về Decorator chưa? Bạn có muốn thực hành viết thử một hàm nhận vào Callable để xử lý logic, hay muốn chuyển sang chủ đề tiếp theo là lập trình hướng đối tượng OOP nâng cao trong Python không?

