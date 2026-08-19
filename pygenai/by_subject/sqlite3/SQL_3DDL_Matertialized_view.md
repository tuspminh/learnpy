**Materialized View (View lưu trữ vật lý)** là một đối tượng CSDL lưu trữ vĩnh viễn **kết quả thực tế** của một câu lệnh truy vấn (`SELECT`) xuống đĩa cứng, thay vì chỉ lưu trữ định nghĩa câu lệnh như View thông thường. Nó hoạt động như một bản "chụp ảnh" (snapshot) dữ liệu tại một thời điểm nhất định để phục vụ các truy vấn đọc cực nhanh mà không cần tính toán lại từ đầu.

| Tiêu chí | View thông thường (Standard View) | Materialized View |
| --- | --- | --- |
| **Bản chất** | **Bảng ảo**, chỉ lưu câu lệnh SQL định nghĩa. | **Bảng thật**, lưu trực tiếp dữ liệu kết quả xuống đĩa. |
| **Hiệu năng đọc** | Phụ thuộc vào độ phức tạp của câu lệnh gốc (`JOIN`, `GROUP BY`). | **Cực nhanh** (Đọc trực tiếp dữ liệu đã pre-computed như một bảng thường). |
| **Dung lượng lưu trữ** | Gần như bằng 0. | Tốn dung lượng đĩa cứng tương ứng với tập kết quả. |
| **Tính thời gian thực** | **100% Real-time** (mỗi lần gọi là DB chạy lại query trên dữ liệu mới nhất). | **Có độ trễ** (Dữ liệu chỉ mới đến thời điểm được `REFRESH` gần nhất). |
| **Tải hệ thống (CPU/RAM)** | Tốn tài nguyên **mỗi lần người dùng query**. | Tốn tài nguyên **khi thực hiện Refresh**, nhẹ khi người dùng đọc. |

---

**Cách thức làm tươi dữ liệu (Refresh Mechanism)**

Do không tự động phản ánh thay đổi từ bảng gốc theo thời gian thực, Materialized View cần được làm tươi thông qua câu lệnh chuyên dụng:

```sql
-- Cú pháp trong PostgreSQL
REFRESH MATERIALIZED VIEW view_name;

-- Trong Oracle / PostgreSQL nâng cao có thể đặt lịch Refresh định kỳ hoặc dùng CONCURRENTLY để không lock bảng khi đang refresh:
REFRESH MATERIALIZED VIEW CONCURRENTLY view_name;

```

---

**Khi nào NÊN dùng Materialized View?**

* **Báo cáo Data Warehouse / BI / Dashboard:** Cần tính toán các hàm tổng hợp (`SUM`, `AVG`, `COUNT`), `GROUP BY`, `JOIN` trên hàng triệu hay hàng tỷ dòng dữ liệu.
* **Chấp nhận độ trễ dữ liệu:** Báo cáo không yêu cầu chính xác từng giây (ví dụ: Báo cáo doanh thu ngày, thống kê hiệu suất bán hàng theo tuần, dashboard quản trị).
* **Ứng dụng Read-heavy:** Tần suất người dùng xem báo cáo rất nhiều, việc chạy lại câu lệnh gốc liên tục sẽ làm nghẽn CSDL.
* **Tích hợp dữ liệu từ hệ thống bên ngoài:** Tổng hợp dữ liệu từ nhiều nguồn khác nhau (như qua Database Link / Foreign Data Wrapper) vốn có tốc độ kết nối chậm.

---

**Khi nào KHÔNG NÊN dùng?**

* **Yêu cầu dữ liệu chính xác 100% theo thời gian thực:** Các nghiệp vụ như số dư tài khoản ngân hàng, đặt vé máy bay, quản lý tồn kho tức thời.
* **Bảng gốc bị ghi (`INSERT`, `UPDATE`, `DELETE`) quá dồn dập:** Nếu phải `REFRESH` Materialized View liên tục theo từng giây, chi phí ghi xuống đĩa sẽ làm quá tải máy chủ CSDL.
* **Truy vấn đơn giản:** Các câu lệnh truy vấn đã có Index và chạy dưới vài mili-giây thì chỉ cần dùng View thông thường.