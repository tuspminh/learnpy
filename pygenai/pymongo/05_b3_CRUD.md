## Bài 3: Chi tiết các thao tác CRUD Cơ bản với PyMongo

CRUD đại diện cho 4 thao tác cốt lõi: **C**reate (Tạo), **R**ead (Đọc), **U**pdate (Sửa), **D**elete (Xóa). Trong bài này, chúng ta sẽ thực hành chi tiết từng phương thức thông qua thư viện `pymongo`.

---

### 1. Create (Thêm dữ liệu)

Khi thêm dữ liệu vào MongoDB, mỗi document được biểu diễn dưới dạng một `dict` trong Python. MongoDB sẽ tự động sinh trường `_id` với kiểu dữ liệu `ObjectId` nếu bạn không cung cấp.

#### **Thêm 1 Document (`insert_one`)**

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["hoc_python_db"]
collection = db["nhan_vien"]

# Dữ liệu 1 nhân viên
nv_1 = {
    "ten": "Nguyễn Văn A",
    "tuoi": 25,
    "phong_ban": "IT",
    "luong": 1500,
    "kynang": ["Python", "MongoDB"]
}

# Thực hiện insert
result = collection.insert_one(nv_1)

print(f"✅ Đã thêm 1 bản ghi thành công.")
print(f"ID vừa tạo: {result.inserted_id}")  # Trả về ObjectId

```

#### **Thêm nhiều Document (`insert_many`)**

```python
danh_sach_nv = [
    {"ten": "Trần Thị B", "tuoi": 30, "phong_ban": "HR", "luong": 1200, "kynang": ["Tuyển dụng", "Giao tiếp"]},
    {"ten": "Lê Văn C", "tuoi": 22, "phong_ban": "IT", "luong": 1000, "kynang": ["Java", "SQL"]},
    {"ten": "Phạm Văn D", "tuoi": 28, "phong_ban": "Marketing", "luong": 1300, "kynang": ["SEO", "Content"]},
    {"ten": "Hoàng Thị E", "tuoi": 26, "phong_ban": "IT", "luong": 1600, "kynang": ["Python", "FastAPI"]}
]

result = collection.insert_many(danh_sach_nv)
print(f"✅ Đã thêm {len(result.inserted_ids)} bản ghi.")

```

---

### 2. Read (Truy vấn dữ liệu)

#### **Tìm 1 Document (`find_one`)**

Trả về document đầu tiên khớp với điều kiện lọc (hoặc `None` nếu không tìm thấy).

```python
# Tìm nhân viên tên 'Nguyễn Văn A'
nv = collection.find_one({"ten": "Nguyễn Văn A"})
print(nv)

# Tìm theo _id (Cần dùng ObjectId từ bson)
from bson.objectid import ObjectId
nv_by_id = collection.find_one({"_id": ObjectId(result.inserted_id)})

```

#### **Tìm nhiều Document (`find`) với Projection**

`find()` trả về một con trỏ (`Cursor`) chứa danh sách kết quả.

* **Projection:** Tham số thứ 2 của `find()` dùng để chỉ định các trường muốn lấy (`1`) hoặc loại bỏ (`0`).

```python
# Lấy tất cả nhân viên thuộc phòng "IT", chỉ lấy tên và lương (ẩn _id)
query = {"phong_ban": "IT"}
projection = {"_id": 0, "ten": 1, "luong": 1}

ket_qua = collection.find(query, projection)

for item in ket_qua:
    print(item)

```

---

### 3. Update (Cập nhật dữ liệu)

Trong MongoDB, bạn **bắt buộc** dùng các toán tử cập nhật (Update Operators) như `$set`, `$inc`, `$push` để sửa đổi dữ liệu. Nếu không có toán tử, document sẽ bị ghi đè hoàn toàn.

| Toán tử | Chức năng |
| --- | --- |
| **`$set`** | Gán/thay đổi giá trị của một trường |
| **`$inc`** | Tăng/giảm giá trị số một lượng nhất định |
| **`$push`** | Thêm một phần tử vào mảng |

#### **Cập nhật 1 Document (`update_one`)**

```python
# Tăng lương thêm 200 và cập nhật tuổi cho Nguyễn Văn A
dieu_kien = {"ten": "Nguyễn Văn A"}
cap_nhat = {
    "$set": {"tuoi": 26},
    "$inc": {"luong": 200}
}

res = collection.update_one(dieu_kien, cap_nhat)
print(f"Số bản ghi tìm thấy: {res.matched_count}, Số bản ghi đã sửa: {res.modified_count}")

```

#### **Cập nhật nhiều Document (`update_many`)**

```python
# Thêm kỹ năng "Git" cho toàn bộ nhân viên phòng IT
filter_it = {"phong_ban": "IT"}
update_skill = {"$push": {"kynang": "Git"}}

res = collection.update_many(filter_it, update_skill)
print(f"Đã cập nhật {res.modified_count} nhân viên IT.")

```

---

### 4. Delete (Xóa dữ liệu)

#### **Xóa 1 Document (`delete_one`)**

```python
# Xóa nhân viên 'Phạm Văn D'
res = collection.delete_one({"ten": "Phạm Văn D"})
print(f"Đã xóa {res.deleted_count} bản ghi.")

```

#### **Xóa nhiều Document (`delete_many`)**

```python
# Xóa toàn bộ nhân viên phòng HR
res = collection.delete_many({"phong_ban": "HR"})
print(f"Đã xóa {res.deleted_count} bản ghi phòng HR.")

# LƯU Ý: Xóa sạch toàn bộ Document trong collection (Dùng cẩn thận!)
# collection.delete_many({})

```

---

### Tóm tắt các hàm PyMongo cốt lõi

```
Create ──► insert_one(dict)           | insert_many([dict, dict])
Read   ──► find_one(filter, proj)     | find(filter, proj)
Update ──► update_one(filter, update) | update_many(filter, update)
Delete ──► delete_one(filter)         | delete_many(filter)

```

---