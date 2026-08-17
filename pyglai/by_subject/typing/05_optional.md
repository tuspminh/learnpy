Trong Python, khi một phần tử trong danh sách hoặc một biến có thể có giá trị cụ thể hoặc là None (dữ liệu bị khuyết, trống), chúng ta sẽ sử dụng khái niệm Optional.
Từ Python 3.10 trở lên, cách viết đã được đơn giản hóa hoàn toàn bằng toán tử | và không cần import Optional từ thư viện typing nữa.
## Cách khai báo phần tử có thể nhận giá trị None## 1. Cách viết từ Python 3.10 trở lên (Khuyên dùng)
Bạn chỉ cần kết hợp kiểu dữ liệu mong muốn với None bằng dấu |.

# Danh sách chứa các chuỗi hoặc giá trị None (ví dụ: dữ liệu cào từ web bị thiếu)user_names: list[str | None] = ["An", None, "Bình", None, "Chi"]
# Danh sách chứa số nguyên hoặc None (ví dụ: điểm số của học sinh chưa thi)scores: list[int | None] = [8, 9, None, 10, None]

## 2. Cách viết cũ (Trước Python 3.10)
Nếu chạy dự án trên các phiên bản Python cũ hơn, bạn buộc phải import Optional từ typing. Cú pháp Optional[str] thực chất là cách viết ngắn gọn của Union[str, None].

from typing import List, Optional
# Cú pháp cũ tương đương với list[str | None]user_names: List[Optional[str]] = ["An", None, "Bình"]

## Ví dụ thực tế: Hàm xử lý danh sách có chứa None
Khi xử lý danh sách có chứa None, bạn luôn cần kiểm tra điều kiện if phan_tu is not None để tránh gặp lỗi hệ thống (như lỗi tính toán hoặc lỗi chuỗi).

def chuẩn_hóa_tên(danh_sách_thô: list[str | None]) -> list[str]:
    kết_quả: list[str] = []
    
    for tên in danh_sách_thô:
        # Kiểm tra nếu tên tồn tại (không phải None)
        if tên is not None:
            kết_quả.append(tên.strip().title()) # Viết hoa chữ cái đầu
            
    return kết_quả
# Sử dụng hàmdữ_liệu_xấu = ["  quang an ", None, "nguyễn bÌNH ", None]dữ_liệu_sạch = chuẩn_hóa_tên(dữ_liệu_xấu)

print(dữ_liệu_sạch) # Kết quả: ['Quang An', 'Nguyễn Bình']

## Bảng tổng hợp cách viết cũ và mới

| Tình huống | Cách viết cũ (Python < 3.10) | Cách viết mới (Python 3.10+) |
|---|---|---|
| Biến có thể là chuỗi hoặc None | Optional[str] | str | None |
| Danh sách chứa số hoặc None | List[Optional[int]] | list[int | None] |
| Hàm trả về danh sách hoặc None | Optional[List[str]] | list[str] | None |

Bạn có muốn chuyển sang tìm hiểu về cách dùng TypeAlias (Từ Python 3.12+) để đặt tên ngắn gọn cho các kiểu dữ liệu phức tạp (như list[str | int | None]) giúp mã nguồn sạch hơn không?

