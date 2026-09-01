Đây là bài tập tổng hợp thực tế mô phỏng **Hệ thống Quản lý Thư viện**. Bài tập này được thiết kế để kiểm tra toàn bộ kiến thức bạn đã học ở Giai đoạn 1: Tạo bảng, ràng buộc, CRUD, lọc `LIKE`, sắp xếp `ORDER BY` và phân trang `LIMIT / OFFSET`.

---

### **Đề bài: Hệ thống Quản lý Sách Thư viện**

Hãy viết một script Python duy nhất (ví dụ: `quan_ly_thuvien.py`) để thực hiện tuần tự các yêu cầu sau:

#### **Yêu cầu 1: Khởi tạo Database & Tạo Bảng**

* Tạo/kết nối đến file cơ sở dữ liệu `thuvien.db`.
* Tạo bảng `Sach` với các cột và ràng buộc sau:
* `id`: Số nguyên, Khóa chính, tự động tăng.
* `ten_sach`: Chuỗi, bắt buộc nhập (`NOT NULL`).
* `tac_gia`: Chuỗi, bắt buộc nhập (`NOT NULL`).
* `nam_xuat_ban`: Số nguyên.
* `gia_thue`: Số thực (VD: 15000.0), bắt buộc nhập.
* `ma_isbn`: Chuỗi, không được trùng lặp (`UNIQUE`).



#### **Yêu cầu 2: Thêm Dữ liệu (Create)**

Thêm 5 cuốn sách sau vào bảng `Sach` bằng câu lệnh `executemany` (sử dụng placeholder `?` an toàn):

1. ("Dế Mèn Phiêu Lưu Ký", "Tô Hoài", 1941, 10000.0, "ISBN001")
2. ("Nhà Giả Kim", "Paulo Coelho", 1988, 15000.0, "ISBN002")
3. ("Mắt Biếc", "Nguyễn Nhật Ánh", 1990, 12000.0, "ISBN003")
4. ("Tôi Thấy Hoa Vàng Trên Cỏ Xanh", "Nguyễn Nhật Ánh", 2010, 15000.0, "ISBN004")
5. ("Đắc Nhân Tâm", "Dale Carnegie", 1936, 18000.0, "ISBN005")

#### **Yêu cầu 3: Lọc & Tìm kiếm Dữ liệu (Read)**

1. **Tìm kiếm:** Tìm tất cả các cuốn sách của tác giả `"Nguyễn Nhật Ánh"`.
2. **Lọc chuỗi:** Tìm các cuốn sách mà tên có chứa từ `"Hoa"` (dùng `LIKE`).
3. **Sắp xếp & Phân trang:** Lấy danh sách tất cả cuốn sách, **sắp xếp theo giá thuê giảm dần** (`ORDER BY gia_thue DESC`), chỉ lấy **3 cuốn đầu tiên** (`LIMIT 3`).

#### **Yêu cầu 4: Cập nhật & Xóa (Update & Delete)**

1. **Cập nhật:** Sửa `gia_thue` của cuốn sách có `ma_isbn = 'ISBN001'` thành `11000.0`.
2. **Xóa:** Xóa cuốn sách có `ma_isbn = 'ISBN005'` ra khỏi cơ sở dữ liệu.

#### **Yêu cầu 5: Hiển thị lại kết quả cuối cùng**

In ra màn hình toàn bộ danh sách sách còn lại trong database sau khi đã thực hiện xong các bước Cập nhật & Xóa để xác nhận kết quả.

---

### **Khung Code Gợi Ý**

Bạn có thể dựa vào khung code dưới đây để bắt đầu làm bài:

```python
import sqlite3

# Đảm bảo dùng 'with' để tự động quản lý commit/close hoặc gọi thủ công chuẩn xác
with sqlite3.connect('thuvien.db') as conn:
    cursor = conn.cursor()
    
    # 1. Tạo bảng
    # ... (viết code SQL CREATE TABLE ở đây)
    
    # 2. Thêm dữ liệu
    # ... (viết code INSERT executemany ở đây)
    
    # 3. Lọc & Truy vấn
    # ... (viết các câu lệnh SELECT ở đây)
    
    # 4. Update & Delete
    # ... (viết code UPDATE và DELETE ở đây)
    
    # 5. Kiểm tra kết quả cuối cùng
    # ...

```

---