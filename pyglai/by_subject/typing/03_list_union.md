Để khai báo một danh sách chứa nhiều kiểu dữ liệu trộn lẫn (ví dụ: vừa có số nguyên, vừa có chuỗi), bạn cần kết hợp list với toán tử | (toán tử OR - Union). Cú pháp này được áp dụng từ Python 3.10 trở lên và cũng không cần import từ thư viện typing.
## Cách khai báo danh sách trộn lẫn kiểu dữ liệu## 1. Danh sách chứa một trong các kiểu chỉ định (Union)
Nếu danh sách có thể chứa cả số nguyên (int) và chuỗi (str), bạn dùng dấu | giữa hai kiểu đó:

# Danh sách chứa cả int và strmixed_list: list[int | str] = [1, "Apple", 2, "Banana"]

## 2. Danh sách chứa bất kỳ kiểu dữ liệu nào (Any)
Nếu bạn muốn danh sách có thể chứa hoàn toàn bất kỳ thứ gì (không giới hạn kiểu), bạn buộc phải import Any từ typing:

from typing import Any
# Cho phép chứa mọi kiểu dữ liệuflexible_list: list[Any] = [1, "Apple", 3.14, True, [1, 2]]

## 3. Danh sách lồng nhau (Nested List)
Nếu bạn có một danh sách chứa các danh sách con, và các danh sách con đó chứa số nguyên:

# Danh sách của các danh sách số nguyênmatrix: list[list[int]] = [[1, 2], [3, 4]]

## Bảng so sánh các phiên bản Python

| Kiểu danh sách | Python 3.8 trở xuống | Python 3.9 & 3.10+ |
|---|---|---|
| Chỉ chứa 1 kiểu | from typing import List List[int] | list[int] (Không cần import) |
| Trộn lẫn nhiều kiểu | from typing import List, Union List[Union[int, str]] | list[int | str] (Từ Python 3.10+, không cần import) [1, 2] |

Bạn có muốn xem cách áp dụng kiểu trộn lẫn này vào tham số của một hàm để xử lý dữ liệu linh hoạt hơn không?

