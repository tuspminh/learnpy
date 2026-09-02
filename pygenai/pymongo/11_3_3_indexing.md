## Giai đoạn 3 - Bài 3: Indexing & Tối ưu hiệu năng câu lệnh bằng `.explain()`

Khi tập dữ liệu lớn lên đến hàng trăm nghìn hay hàng triệu bản ghi, việc truy vấn không có Chỉ mục (Index) sẽ khiến MongoDB phải quét toàn bộ dữ liệu trên đĩa (COLLSCAN). Điều này dẫn đến phản hồi cực chậm và làm quá tải hệ thống.

Trong bài này, chúng ta sẽ học cách tạo Index để tăng tốc truy vấn và đọc kế hoạch thực thi bằng `.explain()`.

---

### 1. Khái niệm Index trong MongoDB

Index là một cấu trúc dữ liệu đặc biệt (thường là cây B-Tree) lưu trữ một phần nhỏ của tập dữ liệu theo thứ tự đã được sắp xếp.

* **Không có Index (COLLSCAN - Collection Scan):** MongoDB quét lần lượt từng document từ đầu đến cuối collection.
* **Có Index (IXSCAN - Index Scan):** MongoDB định vị trực tiếp vị trí dữ liệu cần tìm thông qua cây Index, giúp tốc độ truy vấn tăng hàng trăm lần.

> Mặc định, MongoDB luôn tự động tạo một Unique Index cho trường `_id`.

---

### 2. Các loại Index phổ biến & Cách tạo trong PyMongo

Ta sử dụng phương thức `create_index()` để tạo Index trên Collection.

#### **2.1. Single Field Index (Index đơn)**

Index trên một trường duy nhất. Thích hợp cho các truy vấn lọc hoặc sắp xếp theo 1 trường cụ thể.

```python
import pymongo
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["hoc_python_db"]
collection = db["nhan_vien"]

# Tạo Index tăng dần cho trường 'ten'
collection.create_index([("ten", pymongo.ASCENDING)])
print("✅ Đã tạo Index cho trường 'ten'")

```

#### **2.2. Compound Index (Index phức hợp)**

Index trên nhiều trường kết hợp. Rất quan trọng khi bạn thường xuyên lọc hoặc sắp xếp theo nhiều điều kiện cùng lúc.

Thứ tự khai báo các trường tuân theo quy tắc **ESR (Equal, Sort, Range)**:

1. **Equal:** Các trường lọc chính xác (ví dụ: `phong_ban = "IT"`).
2. **Sort:** Các trường dùng để sắp xếp (ví dụ: `sort("luong")`).
3. **Range:** Các trường lọc theo khoảng (ví dụ: `tuoi > 25`).

```python
# Tạo Compound Index cho 'phong_ban' (Tăng dần) và 'luong' (Giảm dần)
collection.create_index([
    ("phong_ban", pymongo.ASCENDING),
    ("luong", pymongo.DESCENDING)
])

```

#### **2.3. Unique Index (Index duy nhất)**

Đảm bảo không có 2 document nào có cùng giá trị trên trường được đánh Index (ví dụ: `email`, `ma_nv`).

```python
# Đảm bảo trường 'email' không bị trùng lặp
collection.create_index([("email", pymongo.ASCENDING)], unique=True)

```

---

### 3. Phân tích hiệu năng câu lệnh bằng `.explain()`

Để biết một câu truy vấn có đang dùng Index hay không và mất bao nhiêu thời gian thực thi, ta sử dụng phương thức `.explain()` trên Cursor.

```python
# Thêm tham số executionStats để lấy chi tiết thông số hiệu năng
query = {"phong_ban": "IT"}

# Thực thi explain
explanation = collection.find(query).explain()

# Lấy thông tin về Stage thực thi chính
execution_stats = explanation['executionStats']
winning_plan = explanation['queryPlanner']['winningPlan']

print("--- KẾT QUẢ PHÂN TÍCH HIỆU NĂNG ---")
print(f"Trạng thái thực thi (Stage): {winning_plan['stage']}")
print(f"Tổng số document bị quét (totalDocsExamined): {execution_stats['totalDocsExamined']}")
print(f"Số document trả về (nReturned): {execution_stats['nReturned']}")
print(f"Thời gian thực thi (executionTimeMillis): {execution_stats['executionTimeMillis']} ms")

```

#### **Cách đọc chỉ số từ `.explain()`:**

* **`stage`:**
* `COLLSCAN`: **Xấu!** Đang quét toàn bộ bảng do thiếu Index.
* `IXSCAN`: **Tốt!** Đang quét bằng Index.
* `FETCH`: Lấy bản ghi thực tế từ đĩa dựa trên vị trí tìm được từ Index.


* **`totalDocsExamined` vs `nReturned`:**
* Nửa đêm lý tưởng: `totalDocsExamined` gần bằng `nReturned`.
* Nếu `totalDocsExamined = 100,000` nhưng `nReturned = 5` ➔ Câu truy vấn hoạt động rất kém hiệu quả!



---

### 4. Quản lý Index trong PyMongo

```python
# 1. Liệt kê toàn bộ Index hiện có trong Collection
indexes = collection.list_indexes()
print("--- Danh sách Index ---")
for idx in indexes:
    print(idx['name'])

# 2. Xóa 1 Index cụ thể theo tên
collection.drop_index("ten_1")

# 3. Xóa tất cả Index (ngoại trừ _id)
# collection.drop_indexes()

```

---

### Lưu ý quan trọng khi dùng Index

1. **Index làm chậm thao tác GHI (`insert`, `update`, `delete`):** Mỗi khi thêm/sửa/xóa dữ liệu, MongoDB phải cập nhật lại cây Index tương ứng. Do đó, **chỉ tạo Index cho các trường thực sự cần thiết** cho việc truy vấn.
2. **Kích thước Index:** Index được lưu trữ trên RAM. Nếu bộ nhớ RAM không đủ chứa toàn bộ Index, hiệu năng hệ thống sẽ giảm sút đáng kể.

---