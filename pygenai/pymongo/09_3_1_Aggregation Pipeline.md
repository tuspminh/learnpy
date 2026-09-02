## Giai đoạn 3 - Bài 1: Aggregation Pipeline trong PyMongo

**Aggregation Framework** là công cụ xử lý và phân tích dữ liệu mạnh mẽ nhất của MongoDB. Bạn có thể dung nó để thực hiện các công việc tính toán phức tạp như: gom nhóm, tính tổng/trung bình, biến đổi dữ liệu, hoặc lọc dữ liệu đa tầng.

---

### 1. Khái niệm Pipeline (Chuỗi xử lý)

Cơ chế hoạt động của Aggregation dựa trên khái niệm **Pipeline** (Đường ống).

Dữ liệu sẽ chảy qua một chuỗi các **Stage** (công đoạn). Kết quả Output của Stage trước sẽ là Input cho Stage tiếp theo.

```
Collection ──► [ $match ] ──► [ $group ] ──► [ $project ] ──► Kết quả

```

Trong PyMongo, ta dùng phương thức `collection.aggregate([list_cac_stages])`.

---

### 2. Các Stage cốt lõi trong Aggregation

#### **2.1. Stage `$match`: Lọc dữ liệu**

Tương tự như câu lệnh `find()`, giúp lọc ra các document thỏa mãn điều kiện trước khi đưa vào các tính toán phía sau (nên đặt ở đầu Pipeline để tối ưu hiệu năng).

```python
# Stage lọc nhân viên thuộc phòng IT
stage_match = {
    "$match": {
        "phong_ban": "IT"
    }
}

```

#### **2.2. Stage `$group`: Gom nhóm & Tích tụ dữ liệu**

Gom nhóm các document có cùng giá trị lại với nhau (giống `GROUP BY` trong SQL) và tính toán dữ liệu bằng các **Accumulator Operators**:

* `$sum`: Tính tổng (hoặc đếm số lượng bằng cách tính tổng số `1`).
* `$avg`: Tính trung bình cộng.
* `$min`, `$max`: Lấy giá trị nhỏ nhất / lớn nhất.
* `$push`: Gom tất cả giá trị vào một mảng.

> *Lưu ý:* Bắt buộc phải khai báo trường `_id` trong `$group` để chỉ định trường dùng làm tiêu chí gom nhóm.

```python
# Stage nhóm theo phòng ban và tính:
# - Tổng số nhân viên ($sum: 1)
# - Lương trung bình ($avg: "$luong")
stage_group = {
    "$group": {
        "_id": "$phong_ban",                # Gom nhóm theo phong_ban
        "tong_so_nv": {"$sum": 1},          # Đếm số lượng
        "luong_trung_binh": {"$avg": "$luong"}  # Dấu '$' trước luong nghĩa là lấy giá trị của field luong
    }
}

```

#### **2.3. Stage `$project`: Biến đổi cấu trúc Output**

Giúp tái cấu trúc dữ liệu trả về: chọn trường muốn giữ (`1`), loại bỏ trường (`0`), đổi tên trường hoặc tạo ra trường tính toán mới.

```python
# Stage tạo lại định dạng kết quả hiển thị
stage_project = {
    "$project": {
        "_id": 0,                           # Bỏ trường _id
        "ten_phong": "$_id",                # Lấy giá trị _id vừa nhóm gán thành ten_phong
        "tong_so_nv": 1,
        "luong_tb": {"$round": ["$luong_trung_binh", 2]} # Làm tròn 2 chữ số thập phân
    }
}

```

#### **2.4. Stage `$unwind`: Tách mảng (Deconstruct Array)**

Nếu document chứa một mảng, `$unwind` sẽ tách document đó thành **nhiều document nhỏ**, mỗi document chứa 1 phần tử của mảng. Rất hữu ích khi cần gom nhóm hoặc phân tích dữ liệu nằm bên trong mảng.

Giả sử document: `{"ten": "A", "kynang": ["Python", "Git"]}`

Sau khi `$unwind: "$kynang"` sẽ tách thành 2 document:

1. `{"ten": "A", "kynang": "Python"}`
2. `{"ten": "A", "kynang": "Git"}`

---

### 3. Ví dụ thực hành tổng hợp trong PyMongo

#### **Bài toán 1: Thống kê lương trung bình & tổng số nhân viên theo từng phòng ban (Lương > 1000)**

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["hoc_python_db"]
collection = db["nhan_vien"]

pipeline_thong_ke = [
    # Stage 1: Chỉ lọc nhân viên có lương > 1000
    {"$match": {"luong": {"$gt": 1000}}},

    # Stage 2: Gom nhóm theo phòng ban
    {
        "$group": {
            "_id": "$phong_ban",
            "tong_nv": {"$sum": 1},
            "luong_tb": {"$avg": "$luong"}
        }
    },

    # Stage 3: Sắp xếp theo lương trung bình giảm dần
    {"$sort": {"luong_tb": -1}},

    # Stage 4: Làm đẹp kết quả Output
    {
        "$project": {
            "_id": 0,
            "phong_ban": "$_id",
            "tong_nv": 1,
            "luong_tb": {"$round": ["$luong_tb", 0]}
        }
    }
]

# Thực thi Pipeline
ket_qua = collection.aggregate(pipeline_thong_ke)

print("--- THỐNG KÊ LƯƠNG THEO PHÒNG BAN ---")
for row in ket_qua:
    print(f"Phòng: {row['phong_ban']} | Số lượng: {row['tong_nv']} | Lương TB: {row['luong_tb']} USD")

```

---

#### **Bài toán 2: Đếm số lượng nhân viên sở hữu từng loại kỹ năng (Dùng `$unwind`)**

```python
pipeline_kynang = [
    # Stage 1: Tách mảng kynang
    {"$unwind": "$kynang"},

    # Stage 2: Gom nhóm theo từng kỹ năng đơn lẻ
    {
        "$group": {
            "_id": "$kynang",
            "so_luong_nv": {"$sum": 1}
        }
    },

    # Stage 3: Sắp xếp kỹ năng được nhiều người sở hữu nhất
    {"$sort": {"so_luong_nv": -1}}
]

ket_qua_kynang = collection.aggregate(pipeline_kynang)

print("\n--- THỐNG KÊ KỸ NĂNG NỔI BẬT ---")
for row in ket_qua_kynang:
    print(f"Kỹ năng: {row['_id']} | Số nhân viên: {row['so_luong_nv']}")

```

---

### Tổng kết thứ tự viết Pipeline phổ biến

```
$match (Lọc) ──► $unwind (Tách mảng) ──► $group (Gom nhóm/Tính toán) ──► $sort (Sắp xếp) ──► $project (Định dạng)

```

---