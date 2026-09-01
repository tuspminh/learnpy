Chào bạn! Rất vui được đồng hành cùng bạn trên hành trình chinh phục MongoDB với Python. Tôi sẽ không chỉ dạy lý thuyết suông, mà sẽ hướng dẫn bạn theo cách của một lập trình viên thực chiến.

Chúng ta sẽ học theo phương pháp **"Học qua dự án" (Project-based Learning)**. Hãy cùng xây dựng một hệ thống quản lý thư viện đơn giản nhé.

---

### Phần 1: Chuẩn bị "Vũ khí" (Cài đặt)

Trước khi code, bạn cần cài 2 thứ:

1.  **MongoDB**: Tải [MongoDB Community Server](https://www.mongodb.com/try/download/community) và cài đặt. Sau đó khởi động dịch vụ (mặc định chạy ở `localhost:27017`).
2.  **Driver pymongo**: Đây là thư viện giúp Python kết nối với MongoDB. Mở Terminal và gõ:
    ```bash
    pip install pymongo
    ```

---

### Phần 2: Kết nối Database (Bước chân đầu tiên)

```python
from pymongo import MongoClient

# 1. Kết nối tới MongoDB (Giống như cắm dây điện)
client = MongoClient('mongodb://localhost:27017/')

# 2. Tạo hoặc chọn Database (Nếu chưa có, MongoDB sẽ tự tạo khi bạn thêm dữ liệu)
db = client['quan_ly_thu_vien'] 

# 3. Tạo hoặc chọn Collection (tương đương với Table trong SQL)
collection_sach = db['sach']

print("Kết nối thành công!")
```

---

### Phần 3: Các thao tác CRUD (Linh hồn của lập trình)

Đây là 4 thao tác cơ bản nhất: **Create** (Thêm), **Read** (Đọc), **Update** (Sửa), **Delete** (Xóa).

#### 1. CREATE (Thêm dữ liệu)
Trong MongoDB, dữ liệu được lưu dưới dạng **Document** (tương tự như Dictionary trong Python).

```python
# Thêm 1 cuốn sách
cuon_sach = {
    "ten_sach": "Nhà giả kim",
    "tac_gia": "Paulo Coelho",
    "nam_xb": 1988,
    "gia": 150000,
    "the_loai": "Tiểu thuyết",
    "danh_gia": 4.5
}

# insert_one: Thêm 1 document
ket_qua = collection_sach.insert_one(cuon_sach)
print(f"Đã thêm sách với ID: {ket_qua.inserted_id}")

# Thêm nhiều sách cùng lúc
nhieu_sach = [
    {"ten_sach": "Dế mèn phiêu lưu ký", "tac_gia": "Tô Hoài", "gia": 80000},
    {"ten_sach": "Số đỏ", "tac_gia": "Vũ Trọng Phụng", "gia": 120000},
    {"ten_sach": "Hoàng tử bé", "tac_gia": "Saint-Exupéry", "gia": 50000}
]
collection_sach.insert_many(nhieu_sach)
print("Đã thêm nhiều sách!")
```
> **Lưu ý:** Nếu bạn không truyền `_id`, MongoDB sẽ tự tạo cho bạn một `ObjectId` duy nhất.

---

#### 2. READ (Truy vấn dữ liệu)
Đây là phần quan trọng nhất. Ta dùng `find()` hoặc `find_one()`.

```python
# Tìm 1 cuốn sách đầu tiên
sach_dau_tien = collection_sach.find_one()
print(sach_dau_tien)

# Tìm tất cả sách có giá <= 100.000
# {} là điều kiện. Ở đây dùng toán tử "$lte" (less than or equal)
for sach in collection_sach.find({"gia": {"$lte": 100000}}):
    print(f"- {sach['ten_sach']} | Giá: {sach['gia']}")

# Tìm sách của tác giả "Paulo Coelho" và chỉ lấy tên sách + giá (bỏ qua _id)
for sach in collection_sach.find(
    {"tac_gia": "Paulo Coelho"}, 
    {"_id": 0, "ten_sach": 1, "gia": 1}
):
    print(sach)
```

---

#### 3. UPDATE (Cập nhật dữ liệu)
Sử dụng `update_one()` hoặc `update_many()`.

```python
# Cập nhật: Tăng giá sách "Dế mèn" lên 100.000
# { "ten_sach": "Dế mèn phiêu lưu ký" } -> Điều kiện tìm
# { "$set": {"gia": 100000} } -> Toán tử $set dùng để gán giá trị mới
collection_sach.update_one(
    {"ten_sach": "Dế mèn phiêu lưu ký"},
    {"$set": {"gia": 100000}}
)

# Cập nhật nhiều: Thêm trường "khuyen_mai" = 10% cho tất cả sách có giá > 100.000
collection_sach.update_many(
    {"gia": {"$gt": 100000}},  # $gt: greater than
    {"$set": {"khuyen_mai": "10%"}}
)
print("Đã cập nhật khuyến mãi!")
```

---

#### 4. DELETE (Xóa dữ liệu)
Hãy cẩn thận với lệnh này.

```python
# Xóa 1 cuốn sách có tên "Hoàng tử bé"
collection_sach.delete_one({"ten_sach": "Hoàng tử bé"})

# Xóa tất cả sách có giá < 60000
xoa_nhieu = collection_sach.delete_many({"gia": {"$lt": 60000}})
print(f"Đã xóa {xoa_nhieu.deleted_count} cuốn sách")

# (Cực kỳ nguy hiểm) Xóa TOÀN BỘ collection
# collection_sach.delete_many({}) 
```

---

### Phần 4: Nâng cao - Các toán tử thường dùng (Cheat Sheet)

Khi bạn đi làm, 80% thời gian bạn sẽ dùng các toán tử sau:

| Mục đích | Toán tử | Ví dụ |
| :--- | :--- | :--- |
| **So sánh** | `$eq` (bằng), `$ne` (khác) | `{"tuoi": {"$gte": 18}}` |
| | `$gt` (lớn hơn), `$gte` (lớn hơn hoặc bằng) | |
| | `$lt` (nhỏ hơn), `$lte` (nhỏ hơn hoặc bằng) | |
| **Logic** | `$and`, `$or`, `$not` | `{"$or": [{"gia": 100}, {"gia": 200}]}` |
| **Mảng** | `$in` (trong danh sách) | `{"the_loai": {"$in": ["Khoa học", "Viễn tưởng"]}}` |
| **Cập nhật** | `$set` (gán giá trị) | `{"$set": {"trang_thai": "het_hang"}}` |
| | `$inc` (tăng/giảm số) | `{"$inc": {"so_luong": -1}}` (bán 1 cuốn) |
| | `$push` (thêm vào mảng) | `{"$push": {"danh_gia": 5}}` |

---

### Phần 5: Bài tập thực hành cho bạn

Hãy mở PyCharm hoặc VSCode lên và tự làm thử nhé:

1.  Tạo database `shop_quan_ao`.
2.  Tạo collection `san_pham`.
3.  Thêm vào 5 sản phẩm (có các trường: `ten`, `gia`, `size` (list), `mau_sac`).
4.  **Truy vấn:** In ra tất cả sản phẩm có giá từ 200.000 đến 500.000.
5.  **Cập nhật:** Tăng giá tất cả sản phẩm có size "L" lên thêm 10%.
6.  **Xóa:** Xóa sản phẩm có tên bạn không thích.

---

### Lời khuyên cho bạn (Kinh nghiệm xương máu)

1.  **Không bao giờ dùng `delete_many({})` hay `update_many({})` khi chưa check kỹ.** Hãy dùng `find()` với cùng điều kiện để xem sẽ ảnh hưởng bao nhiêu bản ghi trước.
2.  **Index là vua:** Khi dữ liệu lớn, hãy học cách tạo Index (giống như mục lục sách) để truy vấn nhanh hơn gấp 1000 lần.
    ```python
    collection_sach.create_index([("tac_gia", 1)]) # 1 là tăng dần, -1 là giảm dần
    ```
3.  **Phân biệt rõ:** `find()` trả về một `Cursor` (con trỏ), bạn phải dùng vòng lặp `for` để lấy dữ liệu. `find_one()` trả về thẳng một dictionary.

---

Bạn đã nắm được phần lõi rồi đấy! Bây giờ, hãy thử làm bài tập tôi giao ở Phần 5. Nếu gặp lỗi hay thắc mắc gì, cứ chụp màn hình lỗi hoặc code của bạn gửi lên đây, tôi sẽ giúp bạn fix ngay.

**Câu hỏi dành cho bạn:** Bạn muốn xây dựng ứng dụng gì với MongoDB? (Ví dụ: Web bán hàng, quản lý nhân sự, hay crawl dữ liệu?). Nói cho tôi biết để tôi điều chỉnh bài hướng dẫn tiếp theo cho sát với mục tiêu của bạn nhé!