## Giai đoạn 2 - Bài 3: Phân trang & Sắp xếp (sort, skip, limit) trong PyMongo

Khi cơ sở dữ liệu lên đến hàng nghìn hoặc hàng triệu bản ghi, việc tải toàn bộ dữ liệu cùng lúc sẽ khiến ứng dụng bị chậm và tràn bộ nhớ. Bạn cần **Sắp xếp (Sorting)** và **Phân trang (Pagination)** để lấy đúng lượng dữ liệu cần thiết.

---

### 1. Sắp xếp dữ liệu với `sort()`

Phương thức `sort()` trong PyMongo nhận vào danh sách các cặp `(tên_trường, chiều_sắp_xếp)`.

* `1` hoặc `pymongo.ASCENDING`: Sắp xếp tăng dần (A-Z, 0-9, cũ -> mới).
* `-1` hoặc `pymongo.DESCENDING`: Sắp xếp giảm dần (Z-A, 9-0, mới -> cũ).

#### Ví dụ thực hành:

```python
import pymongo
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["hoc_python_db"]
collection = db["nhan_vien"]

# 1. Sắp xếp theo LƯƠNG giảm dần (Cao nhất -> Thấp nhất)
ds_luong_cao = collection.find().sort("luong", pymongo.DESCENDING)

print("--- Danh sách nhân viên theo lương giảm dần ---")
for nv in ds_luong_cao:
    print(f"{nv['ten']} - Lương: {nv['luong']}")

# 2. Sắp xếp đa tầng (Multiple fields):
# Sắp xếp theo Phòng ban TĂNG DẦN, nếu cùng phòng ban thì sắp xếp LƯƠNG GIẢM DẦN
ds_phong_luong = collection.find().sort([
    ("phong_ban", pymongo.ASCENDING),
    ("luong", pymongo.DESCENDING)
])

```

---

### 2. Giới hạn & Bỏ qua dữ liệu: `limit()` và `skip()`

* `limit(n)`: Chỉ lấy tối đa `n` kết quả đầu tiên.
* `skip(k)`: Bỏ qua `k` kết quả đầu tiên trước khi lấy.

```python
# Lấy TOP 3 nhân viên có lương cao nhất
top_3_luong = collection.find().sort("luong", pymongo.DESCENDING).limit(3)

print("--- TOP 3 Lương Cao Nhất ---")
for nv in top_3_luong:
    print(f"{nv['ten']} - Lương: {nv['luong']}")

```

---

### 3. Ky thuật Phân trang Cơ bản (Offset Pagination)

Phân trang là sự kết hợp giữa `skip()` và `limit()` dựa trên công thức:

$$\text{skip\_count} = (\text{trang\_hiện\_tại} - 1) \times \text{số\_bản\_ghi\_mỗi\_trang}$$

#### Hàm phân trang mẫu trong Python:

```python
def get_page(page_number=1, page_size=2):
    """
    Hàm lấy dữ liệu nhân viên theo trang
    """
    skip_count = (page_number - 1) * page_size
    
    # Thực hiện truy vấn kết hợp sort -> skip -> limit
    cursor = collection.find()\
                       .sort("ten", pymongo.ASCENDING)\
                       .skip(skip_count)\
                       .limit(page_size)
    
    total_docs = collection.count_documents({})
    total_pages = (total_docs + page_size - 1) // page_size  # Làm tròn lên
    
    print(f"\n--- Trang {page_number}/{total_pages} (Tổng: {total_docs} bản ghi) ---")
    for nv in cursor:
        print(f"- {nv['ten']} ({nv['phong_ban']})")

# Chạy thử phân trang
get_page(page_number=1, page_size=2)  # Trang 1
get_page(page_number=2, page_size=2)  # Trang 2

```

---

### 4. Hạn chế của Offset Pagination & Giải pháp Keyset Pagination

#### ⚠️ Vấn đề của `skip()` với tập dữ liệu lớn:

Khi bạn gọi `skip(100000)`, MongoDB vẫn phải đọc và duyệt qua $100.000$ bản ghi đầu tiên rồi mới bỏ qua chúng. Điều này gây tốn CPU và RAM nghiêm trọng khi số trang lớn.

#### 💡 Giải pháp: Keyset Pagination (Cursor-based Pagination)

Thay vì dùng `skip()`, ta lọc dữ liệu dựa trên giá trị của bản ghi cuối cùng của trang trước (ví dụ dùng `_id` hoặc mốc thời gian).

```python
# Lấy trang tiếp theo bằng cách lọc các _id LỚN HƠN _id của bản ghi cuối trang trước
last_id_page_1 = "64f1a2b3c4e5f6a7b8c9d0e1"  # ID của phần tử cuối ở trang 1

from bson.objectid import ObjectId

next_page = collection.find({"_id": {"$gt": ObjectId(last_id_page_1)}})\
                      .sort("_id", pymongo.ASCENDING)\
                      .limit(2)

```

> **Quy tắc vàng:**
> * Với tập dữ liệu nhỏ đến trung bình ($< 10.000$ bản ghi): Dùng `skip()` + `limit()` cho đơn giản.
> * Với tập dữ liệu lớn hoặc API cuộn vô tận (Infinite Scroll): Dùng **Keyset Pagination** dựa trên `_id`.
> 
> 

---