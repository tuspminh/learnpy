Dưới đây là một bài toán rất kinh điển trong thực tế: Máy tính của bạn chỉ có 8GB RAM, nhưng bạn được giao nhiệm vụ phải đọc và lọc dữ liệu từ một file log hệ thống khổng lồ nặng tới 20GB để tìm các dòng chứa mã lỗi "ERROR".
Nếu bạn dùng cách đọc file thông thường (như hàm .readlines()), Python sẽ cố gắng tải toàn bộ 20GB dữ liệu đó vào RAM cùng một lúc, dẫn đến việc máy tính bị treo hoặc báo lỗi Out of Memory (Tràn bộ nhớ) ngay lập tức.
Generator chính là "cứu tinh" tuyệt đối trong trường hợp này.

------------------------------

## Cách xử lý file log khổng lồ bằng Generator

Cơ chế hoạt động của file object trong Python vốn dĩ đã là một Generator. Khi bạn kết hợp nó với từ khóa yield, bạn sẽ tạo ra một đường ống dẫn dữ liệu (pipeline) cực kỳ mượt mà: Đọc một dòng từ ổ cứng -> Kiểm tra dữ liệu -> Xử lý/In ra màn hình -> Giải phóng dòng đó khỏi RAM -> Tiếp tục dòng tiếp theo.

## Mã nguồn tối ưu:

```
from collections.abc import Generator
import os

# 1. Hàm Generator đọc file theo từng dòng một cách "lười biếng"
def doc_file_log(duong_dan_file: str) -> Generator[str, None, None]:
    # Sử dụng open thông thường, Python sẽ không tải hết file vào RAM
    with open(duong_dan_file, mode="r", encoding="utf-8") as file:
        for dong in file:
            # yield từng dòng một cho người gọi xử lý
            yield dong

# 2. Hàm Generator thứ hai đóng vai trò bộ lọc dữ liệu (Filter Pipeline)
def loc_dong_loi(cac_dong_log: Generator[str, None, None]) -> Generator[str, None, None]:
    for dong in cac_dong_log:
        if "ERROR" in dong:
            yield dong.strip()
# ==========================================
# 🚀 SỬ DỤNG TRONG THỰC TẾ
# ==========================================

duong_dan = "he_thong_20GB.log"

# Khởi tạo các Generator (Lúc này chưa có dữ liệu nào được đọc vào RAM cả!)
luong_doc_file = doc_file_log(duong_dan)
luong_loc_loi = loc_dong_loi(luong_doc_file)

# Dữ liệu chỉ thực sự được nạp vào RAM TỪNG DÒNG MỘT khi vòng lặp for bắt đầu chạy
print("Đang quét file log để tìm lỗi...")
for dong_loi in luong_loc_loi:
    print(f" Phát hiện lỗi hệ thống: {dong_loi}")
    
    # Bạn có thể thêm điều kiện dừng nếu muốn, ví dụ chỉ lấy 5 lỗi đầu tiên rồi nghỉ
```
------------------------------

## Phân tích cơ chế chạy và mức tiêu thụ RAM

* RAM Tiêu thụ: Gần như bằng 0 (chỉ tốn vài KB để lưu trữ dòng văn bản hiện tại đang được xử lý). Dù file log có tăng lên 100GB hay 1TB, chương trình của bạn vẫn chạy ổn định với lượng RAM siêu nhỏ đó.
* Cơ chế Pipeline: Hàm loc_dong_loi sẽ liên tục gọi next() lên hàm doc_file_log. Khi doc_file_log đọc xong 1 dòng từ ổ cứng, nó chuyển dòng đó qua cho loc_dong_loi kiểm tra. Nếu dòng đó có chữ "ERROR", nó được in ra màn hình. Ngay sau đó, dòng dữ liệu đó sẽ bị xóa khỏi RAM để nhường chỗ cho dòng tiếp theo.

------------------------------

## 💡 Mẹo viết nhanh: Generator Expression

Nếu bạn thấy việc viết cả một hàm với từ khóa yield quá dài dòng cho các tác vụ lọc đơn giản, bạn có thể dùng cú pháp viết tắt (tương tự List Comprehension nhưng thay dấu ngoặc vuông [] thành ngoặc tròn ()).

Hai đoạn mã sau đây có chức năng và hiệu suất hoàn toàn y hệt nhau:

```
# Cách 1: Dùng hàm yield (Đã viết ở trên)
luong_loc_loi = loc_dong_loi(luong_doc_file)

# Cách 2: Dùng Generator Expression (Ngắn gọn chỉ trong 1 dòng)
luong_loc_loi_nhanh = (dong.strip() for dong in luong_doc_file if "ERROR" in dong)
```

Bạn có muốn thử sức với một bài tập thực hành tự viết Generator (ví dụ: Tạo ra một chuỗi số Fibonacci vô hạn hoặc đọc dữ liệu phân trang từ một API) không?

