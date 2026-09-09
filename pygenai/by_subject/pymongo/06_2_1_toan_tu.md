## Giai đoạn 2 - Bài 1: Các toán tử truy vấn nâng cao trong PyMongo

Trong các bài học trước, bạn đã học cách lọc dữ liệu theo điều kiện bằng chính xác (`{"phong_ban": "IT"}`). Tuy nhiên, trong ứng dụng thực tế, nhu cầu lọc dữ liệu đa dạng hơn rất nhiều (so sánh, kết hợp nhiều điều kiện, tìm kiếm theo chuỗi,...).

MongoDB cung cấp các **Toán tử truy vấn (Query Operators)** có tiền tố là dấu `$`.

---

### 1. Toán tử So sánh (Comparison Operators)

Các toán tử so sánh giúp bạn lọc dữ liệu dựa trên các khoảng giá trị số hoặc thời gian:

* `$gt`: Lớn hơn (> - Greater Than)
* `$gte`: Lớn hơn hoặc bằng (>= - Greater Than or Equal)
* `$lt`: Nhỏ hơn (< - Less Than)
* `$lte`: Nhỏ hơn hoặc bằng (<= - Less Than or Equal)
* `$ne`: Khác (!= - Not Equal)
* `$in`: Nằm trong một danh sách giá trị
* `$nin`: Không nằm trong danh sách giá trị

#### Ví dụ thực hành:

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["hoc_python_db"]
collection = db["nhan_vien"]

# 1. Tìm nhân viên có lương LỚN HƠN 1200
query_gt = {"luong": {"$gt": 1200}}
print("--- Nhân viên lương > 1200 ---")
for nv in collection.find(query_gt, {"_id": 0, "ten": 1, "luong": 1}):
    print(nv)

# 2. Tìm nhân viên thuộc phòng 'IT' HOẶC 'Marketing' dùng $in
query_in = {"phong_ban": {"$in": ["IT", "Marketing"]}}
print("\n--- Nhân viên phòng IT hoặc Marketing ---")
for nv in collection.find(query_in, {"_id": 0, "ten": 1, "phong_ban": 1}):
    print(nv)

# 3. Tìm nhân viên có tuổi từ 22 đến 28 (kết hợp $gte và $lte)
query_range = {"tuoi": {"$gte": 22, "$lte": 28}}

```

---

### 2. Toán tử Logic (Logical Operators)

Dùng để kết hợp nhiều điều kiện phức tạp lại với nhau:

* `$and`: Tất cả điều kiện phải đúng (mặc định trong MongoDB nếu bạn viết nhiều trường trong 1 dictionary).
* `$or`: Chỉ cần ít nhất một điều kiện đúng.
* `$nor`: Tất cả điều kiện đều phải sai.
* `$not`: Phủ định điều kiện.

#### Ví dụ thực hành:

```python
# 1. Toán tử $or: Tìm nhân viên thuộc phòng 'IT' HOẶC có lương >= 1500
query_or = {
    "$or": [
        {"phong_ban": "IT"},
        {"luong": {"$gte": 1500}}
    ]
}

print("--- Kết quả $or ---")
for nv in collection.find(query_or, {"_id": 0, "ten": 1, "phong_ban": 1, "luong": 1}):
    print(nv)

# 2. Toán tử $and tường minh: Tìm nhân viên vừa có tuổi > 23 VỪA có kỹ năng 'Python'
query_and = {
    "$and": [
        {"tuoi": {"$gt": 23}},
        {"kynang": "Python"}
    ]
}

```

---

### 3. Tìm kiếm theo chuỗi với `$regex` (Regular Expression)

Toán tử `$regex` cho phép tìm kiếm dữ liệu dạng văn bản theo mẫu chuỗi (mẫu biểu thức chính quy). Rất thích hợp cho các chức năng tìm kiếm (Search bar).

* Tìm theo từ bắt đầu: `^từ_khóa`
* Tìm theo từ kết thúc: `từ_khóa$`
* Không phân biệt chữ hoa / chữ thường: Thêm tham số `"$options": "i"`

#### Ví dụ thực hành:

```python
# 1. Tìm nhân viên có tên BẮT ĐẦU bằng chữ "Nguyễn"
query_regex_start = {"ten": {"$regex": "^Nguyễn"}}

# 2. Tìm nhân viên trong tên CÓ CHỨA chữ "văn" (không phân biệt chữ hoa/thường 'văn', 'Văn', 'VĂN')
query_regex_contains = {
    "ten": {
        "$regex": "văn",
        "$options": "i"  # 'i' = case-insensitive
    }
}

print("--- Kết quả tìm kiếm theo Regex ('văn') ---")
for nv in collection.find(query_regex_contains, {"_id": 0, "ten": 1}):
    print(nv)

```

---

### 4. Kiểm tra sự tồn tại của trường dữ liệu (`$exists`)

Do MongoDB là Schema-less (không cố định khung dữ liệu), một số document có thể có hoặc không có một trường nào đó. Ta dùng `$exists` để kiểm tra.

```python
# Tìm tất cả nhân viên CÓ trường 'trang_thai'
query_exists = {"trang_thai": {"$exists": True}}

# Tìm tất cả nhân viên KHÔNG CÓ trường 'trang_thai'
query_not_exists = {"trang_thai": {"$exists": False}}

```

---

### Tổng kết cú pháp truy vấn nâng cao

```python
{
    "<trường_dữ_liệu>": {
        "<toán_tử>": <giá_trị>
    }
}
# Ví dụ: {"tuoi": {"$gt": 25}}
# Ví dụ $or: {"$or": [{"phong_ban": "IT"}, {"luong": {"$gt": 2000}}]}

```

---