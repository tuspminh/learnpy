## Giai đoạn 3 - Bài 2: Thiết kế Dữ liệu (Data Modeling) & Join dữ liệu với `$lookup`

Một trong những quyết định quan trọng nhất khi làm việc với NoSQL là **xác định cấu trúc dữ liệu**. Khác với SQL (nơi dữ liệu luôn được chuẩn hóa thành các bảng riêng biệt), MongoDB cung cấp cho bạn 2 cách thiết kế mô hình mối quan hệ: **Embedded (Nhúng)** và **Referenced (Tham chiếu)**.

---

### 1. Embedded Documents (Mô hình Nhúng)

**Mô hình Nhúng** lưu trữ toàn bộ dữ liệu liên quan bên trong cùng một Document dưới dạng Document con (Sub-document) hoặc Mảng (Array).

```json
// Collection: nhan_vien (Embedded Address)
{
  "_id": "nv01",
  "ten": "Nguyễn Văn A",
  "dia_chi": {
    "duong": "123 Lê Lợi",
    "thanh_pho": "TP.HCM"
  }
}

```

#### **Khi nào nên dùng Embedded?**

* Mối quan hệ là **1 - 1** hoặc **1 - N (Số lượng nhỏ)** (ví dụ: nhân viên - địa chỉ, bài viết - danh sách nhãn tag).
* Dữ liệu liên quan luôn được truy vấn **cùng lúc** với Document chính.
* Dữ liệu con ít khi thay đổi độc lập.

#### **Ưu điểm & Nhược điểm:**

* 🟢 **Tốc độ cực nhanh:** Chỉ cần 1 truy vấn đơn lẻ là lấy đủ dữ liệu (không cần Join).
* 🔴 **Giới hạn kích thước:** Một Document trong MongoDB có giới hạn tối đa **16MB**. Dữ liệu con phát triển vô tận sẽ gây tràn bộ nhớ.

---

### 2. Referenced Documents (Mô hình Tham chiếu)

**Mô hình Tham chiếu** chia dữ liệu thành các Collection riêng biệt và liên kết chúng bằng ID (tương tự Khóa ngoại - Foreign Key trong SQL).

```json
// Collection: phong_ban
{ "_id": "pb_it", "ten_phong": "Công nghệ thông tin" }

// Collection: nhan_vien (Referenced)
{
  "_id": "nv01",
  "ten": "Nguyễn Văn A",
  "phong_ban_id": "pb_it"
}

```

#### **Khi nào nên dùng Referenced?**

* Mối quan hệ là **1 - N (Số lượng lớn)** hoặc **N - N** (ví dụ: Tác giả - Bài viết, Khách hàng - Đơn hàng).
* Dữ liệu con thường xuyên được truy vấn độc lập.
* Tránh tình trạng lặp lại dữ liệu (Data Duplication).

---

### 3. Join dữ liệu giữa các Collection với Stage `$lookup`

Khi thiết kế theo dạng Tham chiếu (Referenced), để lấy dữ liệu kết hợp từ 2 Collection, ta dùng Stage **`$lookup`** trong Aggregation Pipeline (tương tự `LEFT JOIN` trong SQL).

#### **Cấu trúc của `$lookup`:**

```python
{
    "$lookup": {
        "from": "<collection_can_join>",      # Tên collection muốn nối tới
        "localField": "<truong_o_col_hien_tai>", # Trường chứa ID ở collection hiện tại
        "foreignField": "<truong_o_col_can_join>", # Trường chứa ID khớp ở collection được nối
        "as": "<ten_mang_ket_qua>"             # Tên mảng chứa dữ liệu sau khi join
    }
}

```

---

### 4. Ví dụ thực hành trong PyMongo

Hãy tạo dữ liệu mẫu với 2 Collection: `phong_ban` và `nhan_vien`.

#### **Bước 1: Chuẩn bị dữ liệu mẫu**

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["hoc_python_db"]

# 1. Collection phòng ban
db["phong_ban"].drop()  # Làm sạch dữ liệu cũ
db["phong_ban"].insert_many([
    {"_id": "PB01", "ten_phong": "Phòng IT", "tang": 3},
    {"_id": "PB02", "ten_phong": "Phòng Marketing", "tang": 2}
])

# 2. Collection nhân viên (Tham chiếu tới phòng ban qua phong_ban_id)
db["nhan_vien"].drop()
db["nhan_vien"].insert_many([
    {"ten": "Nguyễn Văn A", "luong": 1500, "phong_ban_id": "PB01"},
    {"ten": "Trần Thị B", "luong": 1200, "phong_ban_id": "PB02"},
    {"ten": "Lê Văn C", "luong": 1800, "phong_ban_id": "PB01"}
])

print("✅ Đã tạo xong dữ liệu mẫu!")

```

#### **Bước 2: Thực hiện `$lookup` để Join dữ liệu**

```python
pipeline_join = [
    # Stage 1: Nối bảng nhan_vien với phong_ban
    {
        "$lookup": {
            "from": "phong_ban",            # Nối tới collection 'phong_ban'
            "localField": "phong_ban_id",    # Field của nhan_vien
            "foreignField": "_id",          # Field tương ứng của phong_ban
            "as": "thong_tin_phong"          # Lưu kết quả vào mảng 'thong_tin_phong'
        }
    },

    # Stage 2: Biến mảng 'thong_tin_phong' (1 phần tử) thành Document phẳng bằng $unwind
    {
        "$unwind": "$thong_tin_phong"
    },

    # Stage 3: Làm đẹp kết quả Output
    {
        "$project": {
            "_id": 0,
            "ten_nv": "$ten",
            "luong": 1,
            "ten_phong": "$thong_tin_phong.ten_phong",
            "tang": "$thong_tin_phong.tang"
        }
    }
]

ket_qua = db["nhan_vien"].aggregate(pipeline_join)

print("\n--- KẾT QUẢ JOIN DỮ LIỆU ---")
for row in ket_qua:
    print(f"NV: {row['ten_nv']} | Lương: {row['luong']} | Phòng: {row['ten_phong']} (Tầng {row['tang']})")

```

---

### Tổng kết quy tắc thiết kế dữ liệu

* **Dữ liệu được đọc cùng nhau?** ➔ **Embedded**
* **Dữ liệu độc lập / Thay đổi liên tục / Vượt quá 16MB?** ➔ **Referenced + `$lookup**`