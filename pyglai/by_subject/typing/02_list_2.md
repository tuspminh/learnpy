Đúng vậy, khi dùng kiểu list viết thường từ Python 3.9 trở lên, bạn không cần import bất kỳ thứ gì từ thư viện typing để khai báo danh sách nữa.
Dưới đây là các lưu ý quan trọng khi bạn bỏ hoàn toàn thư viện typing để chuyển sang cú pháp mới:
## Cách viết không cần import typing## Khai báo biến cơ bản
Bạn viết trực tiếp tên kiểu dữ liệu mong muốn vào trong cặp dấu ngoặc vuông []:

# Danh sách số nguyênnumbers: list[int] = [1, 2, 3]
# Danh sách số thựcprices: list[float] = [10.5, 99.0]

## Định nghĩa kiểu cho Hàm (Function)
Bạn dùng list trực tiếp cho cả tham số đầu vào và kiểu dữ liệu trả về:

def tinh_tong(danh_sach: list[int]) -> int:
    return sum(danh_sach)
def lay_ten_nhan_vien() -> list[str]:
    return ["An", "Bình", "Chi"]

## Lưu ý về các kiểu dữ liệu khác
Không chỉ có list, từ Python 3.9 trở đi, bạn cũng có thể bỏ typing cho các kiểu dữ liệu dạng tập hợp (collections) phổ biến khác:

* Dict (Từ điển): Dùng dict[str, int] thay vì typing.Dict[str, int]
* Tuple (Bộ dữ liệu): Dùng tuple[int, str] thay vì typing.Tuple[int, str]
* Set (Tập hợp): Dùng set[str] thay vì typing.Set[str]

Bạn có muốn tìm hiểu thêm về cách gợi ý kiểu dữ liệu cho trường hợp danh sách chứa nhiều kiểu dữ liệu trộn lẫn (ví dụ: vừa chứa số vừa chứa chuỗi) không?

