# 🎯 CHI TIẾT QUERY OPERATORS - "VŨ KHÍ" QUAN TRỌNG NHẤT CỦA MONGODB

Chào bạn! Bạn đã quyết định đào sâu vào **Query Operators** - đây là quyết định cực kỳ thông minh! 

Hãy tưởng tượng Query Operators như **"ngôn ngữ"** để bạn giao tiếp với MongoDB. Bạn biết càng nhiều operators, bạn càng có thể "hỏi" database những câu hỏi phức tạp và nhận được câu trả lời chính xác.

---

## 📚 TỔNG QUAN - CÁC NHÓM QUERY OPERATORS

Trong MongoDB, Query Operators được chia thành 5 nhóm chính:

| Nhóm | Mục đích | Ví dụ |
|------|----------|-------|
| **So sánh** (Comparison) | So sánh giá trị | `$eq`, `$gt`, `$lt`, `$in` |
| **Logic** (Logical) | Kết hợp nhiều điều kiện | `$and`, `$or`, `$nor`, `$not` |
| **Mảng** (Array) | Làm việc với mảng | `$all`, `$elemMatch`, `$size` |
| **Phạm vi** (Element) | Kiểm tra kiểu dữ liệu | `$exists`, `$type` |
| **Đặc biệt** (Evaluation) | Điều kiện phức tạp | `$regex`, `$text`, `$where` |

---

## 1️⃣ NHÓM SO SÁNH (COMPARISON OPERATORS)

Đây là nhóm **quan trọng nhất**, bạn dùng ít nhất 70% thời gian!

### 1.1 Toán tử cơ bản: `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`

```python
from pymongo import MongoClient
from datetime import datetime
import pprint

# Kết nối và tạo dữ liệu mẫu
client = MongoClient('mongodb://localhost:27017/')
db = client['query_demo']
collection = db['products']

# Xóa dữ liệu cũ và tạo dữ liệu mới
collection.delete_many({})
products = [
    {
        "name": "iPhone 15 Pro",
        "price": 29990000,
        "brand": "Apple",
        "rating": 4.8,
        "stock": 45,
        "release_date": datetime(2023, 9, 15),
        "colors": ["Titan", "Trắng", "Đen"],
        "ram": 8,
        "storage": 256,
        "discount": 5,
        "is_available": True
    },
    {
        "name": "iPhone 15",
        "price": 21990000,
        "brand": "Apple",
        "rating": 4.3,
        "stock": 5,
        "release_date": datetime(2023, 9, 15),
        "colors": ["Hồng", "Xanh", "Đen"],
        "ram": 6,
        "storage": 128,
        "discount": 0,
        "is_available": True
    },
    {
        "name": "Samsung Galaxy S24",
        "price": 24990000,
        "brand": "Samsung",
        "rating": 4.6,
        "stock": 32,
        "release_date": datetime(2024, 1, 17),
        "colors": ["Đen", "Tím", "Vàng"],
        "ram": 12,
        "storage": 512,
        "discount": 10,
        "is_available": True
    },
    {
        "name": "Xiaomi 14 Pro",
        "price": 15990000,
        "brand": "Xiaomi",
        "rating": 4.4,
        "stock": 78,
        "release_date": datetime(2023, 11, 1),
        "colors": ["Đen", "Trắng", "Xanh"],
        "ram": 12,
        "storage": 256,
        "discount": 15,
        "is_available": True
    },
    {
        "name": "Google Pixel 8 Pro",
        "price": 18990000,
        "brand": "Google",
        "rating": 4.2,
        "stock": 0,
        "release_date": datetime(2023, 10, 4),
        "colors": ["Trắng", "Đen", "Xanh"],
        "ram": 12,
        "storage": 128,
        "discount": 8,
        "is_available": False
    },
    {
        "name": "Samsung Z Fold 5",
        "price": 39990000,
        "brand": "Samsung",
        "rating": 4.7,
        "stock": 12,
        "release_date": datetime(2023, 8, 10),
        "colors": ["Đen", "Xanh"],
        "ram": 12,
        "storage": 512,
        "discount": 20,
        "is_available": True
    },
    {
        "name": "OnePlus 12",
        "price": 20990000,
        "brand": "OnePlus",
        "rating": 4.5,
        "stock": 25,
        "release_date": datetime(2024, 2, 1),
        "colors": ["Đen", "Xanh"],
        "ram": 12,
        "storage": 256,
        "discount": 5,
        "is_available": True
    },
    {
        "name": "Realme GT 5 Pro",
        "price": 13990000,
        "brand": "Realme",
        "rating": 4.1,
        "stock": 50,
        "release_date": datetime(2023, 12, 1),
        "colors": ["Đen", "Trắng"],
        "ram": 8,
        "storage": 256,
        "discount": 12,
        "is_available": True
    }
]
collection.insert_many(products)
print("✅ Đã tạo 8 sản phẩm mẫu!\n")
```

#### **1.1.1 `$eq` (Bằng - Equal)**

```python
print("=" * 60)
print("1.1 $eq - Tìm sản phẩm có giá chính xác")
print("=" * 60)

# Tìm sản phẩm giá đúng 21,990,000đ
result = collection.find({"price": {"$eq": 21990000}})
print("📱 Sản phẩm giá 21,990,000đ:")
for doc in result:
    print(f"  - {doc['name']}: {doc['price']:,}đ")
print()

# $eq có thể viết gọn là { "price": 21990000 } - không cần $eq
result = collection.find({"price": 21990000})
print("📱 Cách viết ngắn: { 'price': 21990000 }")
for doc in result:
    print(f"  - {doc['name']}: {doc['price']:,}đ")
```

#### **1.1.2 `$ne` (Khác - Not Equal)**

```python
print("\n" + "=" * 60)
print("1.2 $ne - Tìm sản phẩm KHÔNG PHẢI Apple")
print("=" * 60)

result = collection.find({"brand": {"$ne": "Apple"}})
print("📱 Sản phẩm không phải Apple:")
for doc in result:
    print(f"  - {doc['name']}: {doc['brand']}")
```

#### **1.1.3 `$gt` (Lớn hơn - Greater Than) và `$gte` (Lớn hơn hoặc bằng)**

```python
print("\n" + "=" * 60)
print("1.3 $gt và $gte - Lọc theo giá")
print("=" * 60)

# $gt: Lớn hơn
result = collection.find({"price": {"$gt": 25000000}})
print("💰 Sản phẩm > 25 triệu:")
for doc in result:
    print(f"  - {doc['name']}: {doc['price']:,}đ")

# $gte: Lớn hơn hoặc bằng
print("\n💰 Sản phẩm >= 20 triệu:")
result = collection.find({"price": {"$gte": 20000000}})
for doc in result:
    print(f"  - {doc['name']}: {doc['price']:,}đ")
```

#### **1.1.4 `$lt` (Nhỏ hơn - Less Than) và `$lte` (Nhỏ hơn hoặc bằng)**

```python
print("\n" + "=" * 60)
print("1.4 $lt và $lte - Lọc theo giá")
print("=" * 60)

# $lt: Nhỏ hơn
result = collection.find({"price": {"$lt": 20000000}})
print("💰 Sản phẩm < 20 triệu:")
for doc in result:
    print(f"  - {doc['name']}: {doc['price']:,}đ")

# $lte: Nhỏ hơn hoặc bằng
print("\n💰 Sản phẩm <= 20 triệu:")
result = collection.find({"price": {"$lte": 20000000}})
for doc in result:
    print(f"  - {doc['name']}: {doc['price']:,}đ")
```

#### **1.1.5 `$in` (Trong danh sách)**

```python
print("\n" + "=" * 60)
print("1.5 $in - Lọc theo danh sách")
print("=" * 60)

# Tìm sản phẩm của Apple hoặc Samsung
result = collection.find({
    "brand": {"$in": ["Apple", "Samsung"]}
})
print("📱 Apple hoặc Samsung:")
for doc in result:
    print(f"  - {doc['name']}: {doc['brand']}")

# $in với số
print("\n💰 Giá trong khoảng [15tr, 20tr, 25tr]:")
result = collection.find({
    "price": {"$in": [15000000, 20000000, 25000000]}
})
for doc in result:
    print(f"  - {doc['name']}: {doc['price']:,}đ")
```

#### **1.1.6 `$nin` (Không trong danh sách - Not In)**

```python
print("\n" + "=" * 60)
print("1.6 $nin - Không nằm trong danh sách")
print("=" * 60)

# Tìm sản phẩm không phải Apple, Samsung, Xiaomi
result = collection.find({
    "brand": {"$nin": ["Apple", "Samsung", "Xiaomi"]}
})
print("📱 Sản phẩm không thuộc Apple, Samsung, Xiaomi:")
for doc in result:
    print(f"  - {doc['name']}: {doc['brand']}")
```

#### **1.1.7 Ứng dụng thực tế: Lọc sản phẩm trong khoảng giá**

```python
print("\n" + "=" * 60)
print("🎯 ỨNG DỤNG: Bộ lọc sản phẩm theo khoảng giá")
print("=" * 60)

def filter_products_by_price(min_price, max_price):
    """Lọc sản phẩm trong khoảng giá"""
    result = collection.find({
        "price": {"$gte": min_price, "$lte": max_price}
    })
    return list(result)

# Lọc sản phẩm từ 15-22 triệu
products_in_range = filter_products_by_price(15000000, 22000000)
print(f"📱 Sản phẩm từ 15-22 triệu ({len(products_in_range)} sản phẩm):")
for p in products_in_range:
    print(f"  - {p['name']}: {p['price']:,}đ | Rating: {p['rating']}")
```

---

## 2️⃣ NHÓM LOGIC (LOGICAL OPERATORS)

### 2.1 `$and` - VÀ

```python
print("\n" + "=" * 60)
print("2.1 $and - Kết hợp nhiều điều kiện (VÀ)")
print("=" * 60)

# Tìm sản phẩm vừa Apple, vừa giá < 25tr, vừa stock > 10
result = collection.find({
    "$and": [
        {"brand": "Apple"},
        {"price": {"$lt": 25000000}},
        {"stock": {"$gt": 10}}
    ]
})
print("🍎 Apple, giá < 25tr, stock > 10:")
for doc in result:
    print(f"  - {doc['name']}: {doc['price']:,}đ | Stock: {doc['stock']}")

# Cách viết ngắn: MongoDB mặc định là $and
print("\n📝 Cách viết ngắn (không cần $and):")
result = collection.find({
    "brand": "Apple",
    "price": {"$lt": 25000000},
    "stock": {"$gt": 10}
})
for doc in result:
    print(f"  - {doc['name']}: {doc['price']:,}đ | Stock: {doc['stock']}")
```

### 2.2 `$or` - HOẶC

```python
print("\n" + "=" * 60)
print("2.2 $or - Kết hợp điều kiện (HOẶC)")
print("=" * 60)

# Tìm sản phẩm hoặc giá < 15tr, hoặc rating >= 4.7
result = collection.find({
    "$or": [
        {"price": {"$lt": 15000000}},
        {"rating": {"$gte": 4.7}}
    ]
})
print("📱 Giá < 15tr HOẶC rating >= 4.7:")
for doc in result:
    print(f"  - {doc['name']}: {doc['price']:,}đ | Rating: {doc['rating']}")
```

### 2.3 `$nor` - KHÔNG HOẶC

```python
print("\n" + "=" * 60)
print("2.3 $nor - Không thỏa mãn bất kỳ điều kiện nào")
print("=" * 60)

# Tìm sản phẩm không phải Apple và không có giá > 30tr
result = collection.find({
    "$nor": [
        {"brand": "Apple"},
        {"price": {"$gt": 30000000}}
    ]
})
print("📱 Không phải Apple VÀ không > 30tr:")
for doc in result:
    print(f"  - {doc['name']}: {doc['brand']} | {doc['price']:,}đ")
```

### 2.4 `$not` - PHỦ ĐỊNH

```python
print("\n" + "=" * 60)
print("2.4 $not - Phủ định một điều kiện")
print("=" * 60)

# Tìm sản phẩm có rating không >= 4.5 (tức < 4.5)
result = collection.find({
    "rating": {"$not": {"$gte": 4.5}}
})
print("📱 Rating < 4.5:")
for doc in result:
    print(f"  - {doc['name']}: {doc['rating']}")

# Tìm sản phẩm không có stock = 0
result = collection.find({
    "stock": {"$not": {"$eq": 0}}
})
print("\n📦 Stock > 0:")
for doc in result:
    print(f"  - {doc['name']}: {doc['stock']}")
```

---

## 3️⃣ NHÓM MẢNG (ARRAY OPERATORS)

### 3.1 `$all` - Chứa TẤT CẢ các phần tử

```python
print("\n" + "=" * 60)
print("3.1 $all - Chứa tất cả các giá trị trong mảng")
print("=" * 60)

# Tìm sản phẩm có cả màu Đen VÀ Trắng
result = collection.find({
    "colors": {"$all": ["Đen", "Trắng"]}
})
print("🎨 Sản phẩm có màu Đen và Trắng:")
for doc in result:
    print(f"  - {doc['name']}: {doc['colors']}")
```

### 3.2 `$elemMatch` - Tìm phần tử trong mảng thỏa mãn nhiều điều kiện

```python
print("\n" + "=" * 60)
print("3.2 $elemMatch - Tìm phần tử thỏa mãn NHIỀU điều kiện")
print("=" * 60)

# Giả sử có mảng đánh giá chi tiết
collection.update_one(
    {"name": "iPhone 15 Pro"},
    {"$set": {
        "reviews": [
            {"user": "Alice", "rating": 5, "comment": "Tuyệt vời"},
            {"user": "Bob", "rating": 4, "comment": "Máy đẹp"},
            {"user": "Charlie", "rating": 2, "comment": "Đắt quá"}
        ]
    }}
)

# Tìm sản phẩm có review rating = 5 và comment chứa "Tuyệt vời"
result = collection.find({
    "reviews": {
        "$elemMatch": {
            "rating": 5,
            "comment": {"$regex": "Tuyệt"}
        }
    }
})
print("📱 Sản phẩm có review 5 sao và comment tuyệt:")
for doc in result:
    print(f"  - {doc['name']}")
    for review in doc.get('reviews', []):
        if review['rating'] == 5:
            print(f"    ⭐ {review['user']}: {review['comment']}")
```

### 3.3 `$size` - Kiểm tra độ dài mảng

```python
print("\n" + "=" * 60)
print("3.3 $size - Lọc theo độ dài mảng")
print("=" * 60)

# Tìm sản phẩm có đúng 3 màu
result = collection.find({
    "colors": {"$size": 3}
})
print("🌈 Sản phẩm có đúng 3 màu:")
for doc in result:
    print(f"  - {doc['name']}: {len(doc['colors'])} màu - {doc['colors']}")
```

### 3.4 `$exists` - Kiểm tra field tồn tại

```python
print("\n" + "=" * 60)
print("3.4 $exists - Kiểm tra field tồn tại")
print("=" * 60)

# Tìm sản phẩm có field discount
result = collection.find({
    "discount": {"$exists": True}
})
print("🏷️ Sản phẩm có giảm giá:")
for doc in result:
    print(f"  - {doc['name']}: giảm {doc.get('discount', 0)}%")

# Tìm sản phẩm KHÔNG có field discount
result = collection.find({
    "discount": {"$exists": False}
})
print("\n🏷️ Sản phẩm KHÔNG có giảm giá:")
for doc in result:
    print(f"  - {doc['name']}")
```

### 3.5 `$type` - Kiểm tra kiểu dữ liệu

```python
print("\n" + "=" * 60)
print("3.5 $type - Lọc theo kiểu dữ liệu")
print("=" * 60)

# BSON Types thường dùng:
# 1: Double, 2: String, 3: Object, 4: Array, 
# 8: Boolean, 9: Date, 16: Int, 18: Long

# Tìm field là boolean
result = collection.find({
    "is_available": {"$type": 8}  # 8 = Boolean
})
print("🔢 Sản phẩm có is_available là boolean:")
for doc in result:
    print(f"  - {doc['name']}: is_available = {doc['is_available']}")
```

---

## 4️⃣ NHÓM ĐÁNH GIÁ (EVALUATION OPERATORS)

### 4.1 `$regex` - Biểu thức chính quy (Tìm kiếm theo mẫu)

```python
print("\n" + "=" * 60)
print("4.1 $regex - Tìm kiếm với biểu thức chính quy")
print("=" * 60)

# Tìm sản phẩm bắt đầu bằng "iPhone"
result = collection.find({
    "name": {"$regex": "^iPhone"}
})
print("📱 Tên bắt đầu bằng 'iPhone':")
for doc in result:
    print(f"  - {doc['name']}")

# Tìm sản phẩm chứa "Pro" (không phân biệt hoa thường)
result = collection.find({
    "name": {"$regex": "pro", "$options": "i"}  # i = case-insensitive
})
print("\n🔍 Tên chứa 'Pro' (không phân biệt hoa thường):")
for doc in result:
    print(f"  - {doc['name']}")
```

### 4.2 `$text` - Tìm kiếm full-text (Cần tạo text index)

```python
print("\n" + "=" * 60)
print("4.2 $text - Tìm kiếm full-text")
print("=" * 60)

# Tạo text index trên field name
collection.create_index([("name", "text")])

# Tìm kiếm từ "iPhone"
result = collection.find({
    "$text": {"$search": "iPhone"}
})
print("📱 Tìm kiếm từ khóa 'iPhone':")
for doc in result:
    print(f"  - {doc['name']} | Score: {doc.get('score', 0)}")

# Tìm kiếm nhiều từ
result = collection.find({
    "$text": {"$search": "Samsung Pro"}
})
print("\n🔍 Tìm kiếm 'Samsung Pro':")
for doc in result:
    print(f"  - {doc['name']}")
```

---

## 5️⃣ CÁC TOÁN TỬ ĐẶC BIỆT KHÁC

### 5.1 `$mod` - Chia lấy dư

```python
print("\n" + "=" * 60)
print("5.1 $mod - Lọc theo phép chia lấy dư")
print("=" * 60)

# Giả sử có các sản phẩm với ID là số
# Thêm field product_id cho demo
for i, product in enumerate(collection.find()):
    collection.update_one(
        {"_id": product["_id"]},
        {"$set": {"product_id": i + 1}}
    )

# Tìm sản phẩm có product_id chẵn (product_id % 2 == 0)
result = collection.find({
    "product_id": {"$mod": [2, 0]}  # [divisor, remainder]
})
print("🔢 Sản phẩm có product_id chẵn:")
for doc in result:
    print(f"  - {doc['name']}: product_id = {doc['product_id']}")
```

### 5.2 `$where` - Sử dụng JavaScript (CẨN THẬN - Chậm)

```python
print("\n" + "=" * 60)
print("5.2 $where - Sử dụng JavaScript (Chậm, hạn chế dùng)")
print("=" * 60)

# $where dùng khi không thể dùng operator khác
result = collection.find({
    "$where": "this.price > 20000000 && this.rating > 4.5"
})
print("📱 $where: Price > 20tr và rating > 4.5:")
for doc in result:
    print(f"  - {doc['name']}: {doc['price']:,}đ | Rating: {doc['rating']}")

# ⚠️ LƯU Ý: $where rất CHẬM vì phải thực thi JavaScript
# Nên dùng các operators thay thế
print("\n⚠️ Nên dùng $and thay vì $where:")
result = collection.find({
    "$and": [
        {"price": {"$gt": 20000000}},
        {"rating": {"$gt": 4.5}}
    ]
})
for doc in result:
    print(f"  - {doc['name']}: {doc['price']:,}đ | Rating: {doc['rating']}")
```

---

## 🎯 ỨNG DỤNG THỰC TẾ - API LỌC SẢN PHẨM

Hãy xây dựng một API lọc sản phẩm thực tế:

```python
def filter_products(
    brands=None,           # Danh sách hãng
    min_price=None,       # Giá tối thiểu
    max_price=None,       # Giá tối đa
    min_rating=None,      # Rating tối thiểu
    colors=None,          # Danh sách màu
    in_stock=None,        # Còn hàng?
    search_keyword=None,  # Từ khóa tìm kiếm
    sort_by=None,         # Sắp xếp theo field
    sort_order=1,         # 1: tăng dần, -1: giảm dần
    limit=10,             # Giới hạn số lượng
    skip=0                # Bỏ qua bao nhiêu
):
    """
    Hàm lọc sản phẩm với nhiều tiêu chí
    """
    query = {}
    
    # 1. Lọc theo hãng (sử dụng $in)
    if brands:
        query["brand"] = {"$in": brands}
    
    # 2. Lọc theo khoảng giá (sử dụng $gte, $lte)
    price_filter = {}
    if min_price is not None:
        price_filter["$gte"] = min_price
    if max_price is not None:
        price_filter["$lte"] = max_price
    if price_filter:
        query["price"] = price_filter
    
    # 3. Lọc theo rating (sử dụng $gte)
    if min_rating:
        query["rating"] = {"$gte": min_rating}
    
    # 4. Lọc theo màu (sử dụng $in)
    if colors:
        query["colors"] = {"$in": colors}
    
    # 5. Lọc theo tồn kho (sử dụng $gt)
    if in_stock is not None:
        query["stock"] = {"$gt": 0} if in_stock else {"$eq": 0}
    
    # 6. Tìm kiếm full-text (sử dụng $text)
    if search_keyword:
        query["$text"] = {"$search": search_keyword}
    
    # 7. Thực hiện query
    cursor = collection.find(query)
    
    # 8. Sắp xếp
    if sort_by:
        cursor = cursor.sort(sort_by, sort_order)
    
    # 9. Phân trang
    cursor = cursor.skip(skip).limit(limit)
    
    return list(cursor)
```

**Test API filter:**

```python
print("\n" + "=" * 60)
print("🎯 TEST API LỌC SẢN PHẨM")
print("=" * 60)

# 1. Lọc sản phẩm Apple, giá 20-30tr, rating >= 4.5
print("\n1️⃣ Lọc: Apple, 20-30tr, rating >= 4.5:")
results = filter_products(
    brands=["Apple"],
    min_price=20000000,
    max_price=30000000,
    min_rating=4.5
)
for p in results:
    print(f"  - {p['name']}: {p['price']:,}đ | Rating: {p['rating']}")

# 2. Lọc sản phẩm có màu Đen hoặc Trắng, còn hàng
print("\n2️⃣ Lọc: Màu Đen hoặc Trắng, còn hàng:")
results = filter_products(
    colors=["Đen", "Trắng"],
    in_stock=True
)
for p in results:
    print(f"  - {p['name']}: {p['colors']} | Stock: {p['stock']}")

# 3. Tìm kiếm từ khóa "Pro", sắp xếp theo giá giảm dần
print("\n3️⃣ Tìm kiếm: 'Pro', sắp xếp giá giảm dần:")
results = filter_products(
    search_keyword="Pro",
    sort_by="price",
    sort_order=-1
)
for p in results:
    print(f"  - {p['name']}: {p['price']:,}đ")
```

---

## 📊 SO SÁNH CÁC OPERATOR

```python
print("\n" + "=" * 60)
print("📊 MA TRẬN SO SÁNH CÁC OPERATOR")
print("=" * 60)

print("""
┌─────────────┬─────────────────┬────────────────────────────────────┐
│ Operator    │ Khi nào dùng     │ Ví dụ                             │
├─────────────┼─────────────────┼────────────────────────────────────┤
│ $eq, $ne    │ So sánh bằng    │ {"status": "active"}               │
│ $gt, $lt    │ So sánh số       │ {"price": {"$gt": 100}}           │
│ $in, $nin   │ Danh sách        │ {"brand": {"$in": ["A","B"]}}     │
│ $and         │ Tất cả điều kiện │ {"$and": [cond1, cond2]}         │
│ $or          │ Ít nhất 1 điều kiện│ {"$or": [cond1, cond2]}          │
│ $all         │ Mảng chứa TẤT CẢ  │ {"tags": {"$all": ["hot","new"]}} │
│ $elemMatch   │ Phần tử thỏa mãn  │ {"reviews": {"$elemMatch": {...}}}│
│ $size        │ Độ dài mảng      │ {"tags": {"$size": 3}}            │
│ $exists      │ Field tồn tại    │ {"discount": {"$exists": true}}   │
│ $regex       │ Tìm kiếm mẫu     │ {"name": {"$regex": "^iPhone"}}   │
│ $text        │ Full-text search │ {"$text": {"$search": "iPhone"}}  │
└─────────────┴─────────────────┴────────────────────────────────────┘
""")
```

---

## 🎯 BÀI TẬP THỰC HÀNH

```python
"""
BÀI TẬP 1: Lọc sản phẩm với nhiều điều kiện
Viết query tìm sản phẩm:
- Hãng Samsung hoặc Apple
- Giá từ 20-30 triệu
- Rating >= 4.5
- Còn hàng (>0)
- Có màu Đen hoặc Trắng

BÀI TẬP 2: Tìm kiếm nâng cao
Tìm sản phẩm:
- Tên chứa "Pro" (không phân biệt hoa thường)
- Hoặc brand = "Xiaomi"
- Giá < 25 triệu

BÀI TẬP 3: Lọc theo mảng
Tìm sản phẩm:
- Có đúng 3 màu
- Màu bao gồm "Đen"
- Không có màu "Hồng"

BÀI TẬP 4: Thực tế - Bộ lọc sản phẩm cho web
Xây dựng bộ lọc hoàn chỉnh như Shopee/Tiki:
- Lọc theo giá: 0-5tr, 5-10tr, 10-20tr, 20-50tr, >50tr
- Lọc theo hãng: checkbox
- Lọc theo rating: 3+, 4+, 4.5+
- Lọc theo khuyến mãi: có giảm giá
- Lọc theo tình trạng: còn hàng/hết hàng
- Sắp xếp: giá tăng/giảm, rating, mới nhất
"""
```

<details>
<summary><b>ĐÁP ÁN BÀI TẬP 1: Click để xem</b></summary>

```python
# BÀI TẬP 1
result = collection.find({
    "$and": [
        {"brand": {"$in": ["Samsung", "Apple"]}},
        {"price": {"$gte": 20000000, "$lte": 30000000}},
        {"rating": {"$gte": 4.5}},
        {"stock": {"$gt": 0}},
        {"colors": {"$in": ["Đen", "Trắng"]}}
    ]
})
```
</details>

<details>
<summary><b>ĐÁP ÁN BÀI TẬP 2: Click để xem</b></summary>

```python
# BÀI TẬP 2
result = collection.find({
    "$or": [
        {"name": {"$regex": "pro", "$options": "i"}},
        {"brand": "Xiaomi"}
    ],
    "price": {"$lt": 25000000}
})
```
</details>

<details>
<summary><b>ĐÁP ÁN BÀI TẬP 3: Click để xem</b></summary>

```python
# BÀI TẬP 3
result = collection.find({
    "$and": [
        {"colors": {"$size": 3}},
        {"colors": {"$in": ["Đen"]}},
        {"colors": {"$nin": ["Hồng"]}}
    ]
})
```
</details>

<details>
<summary><b>ĐÁP ÁN BÀI TẬP 4: Click để xem</b></summary>

```python
# BÀI TẬP 4 - Bộ lọc hoàn chỉnh
def ecommerce_filter(
    price_range=None,  # "0-5tr", "5-10tr", "10-20tr", "20-50tr", "50tr+"
    brands=None,
    rating_min=None,   # 3, 4, 4.5
    has_discount=None,
    in_stock=None,
    sort_by=None       # "price_asc", "price_desc", "rating", "newest"
):
    query = {}
    
    # 1. Lọc theo giá
    if price_range:
        price_map = {
            "0-5tr": {"$lte": 5000000},
            "5-10tr": {"$gte": 5000000, "$lte": 10000000},
            "10-20tr": {"$gte": 10000000, "$lte": 20000000},
            "20-50tr": {"$gte": 20000000, "$l