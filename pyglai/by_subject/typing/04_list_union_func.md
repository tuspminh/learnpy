Dưới đây là cách bạn áp dụng kiểu dữ liệu trộn lẫn (Union với toán tử |) vào tham số và kết quả trả về của một hàm trong Python (áp dụng từ Python 3.10 trở lên).
## Ví dụ thực tế về hàm nhận danh sách trộn lẫn kiểu## 1. Hàm xử lý danh sách vừa chứa Số vừa chứa Chuỗi
Giả sử bạn có một danh sách chứa cả số và chuỗi, bạn muốn viết một hàm để lọc và tính tổng tất cả các số có trong danh sách đó.

def tinh_tong_so(danh_sach: list[int | float | str]) -> float:
    tong = 0.0
    for phan_tu in danh_sach:
        # Kiểm tra nếu phần tử là kiểu số (int hoặc float)
        if isinstance(phan_tu, (int, float)):
            tong += phan_tu
    return tong
# Sử dụng hàmdata = [10, "Apple", 5.5, "Banana", 20]ket_qua = tinh_tong_so(data) 
print(ket_qua) # Kết quả: 35.5

## 2. Hàm trả về kết quả trộn lẫn hoặc danh sách trống
Bạn cũng có thể dùng | cho kiểu dữ liệu trả về (->). Ví dụ, hàm tìm kiếm các từ khóa có độ dài lớn hơn 5 ký tự. Hàm này sẽ trả về một list[str] hoặc trả về None nếu không tìm thấy.

def tim_tu_dai(danh_sach_tu: list[str]) -> list[str] | None:
    ket_qua = [tu for tu in danh_sach_tu if len(tu) > 5]
    
    if not ket_qua:
        return None
    return ket_qua
# Sử dụng hàmcac_tu = ["Python", "Code", "AI", "Developer"]
print(tim_tu_dai(cac_tu)) # Trả về: ['Python', 'Developer']

## Tóm tắt quy tắc viết nhanh

* Tham số đầu vào (danh_sach: list[int | str]): Cho phép hàm nhận vào một danh sách chứa cả int và str.
* Dữ liệu trả về (-> list[str] | None): Cho phép hàm trả về một danh sách chuỗi HOẶC giá trị None.

Bạn có muốn tìm hiểu thêm về cách dùng Optional (hoặc cách viết mới với None) khi một phần tử trong danh sách có thể bị khuyết (mang giá trị None) không?

