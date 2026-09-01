Tuyệt vời! Bạn chọn **Level 5: Relationship** - Đây là quyết định cực kỳ đúng đắn! Vì **90% lỗi thiết kế database đến từ việc không hiểu rõ quan hệ dữ liệu**.

Hôm nay tôi sẽ dạy bạn **cách thiết kế database chuẩn chỉnh** cho các mối quan hệ 1-1, 1-n, và n-n. Đây là kiến thức phân biệt bạn là **Junior vs Senior Developer** đấy!

---

## 🎯 PHẦN 5: RELATIONSHIP TRONG MONGODB

### Khái niệm quan trọng nhất: **Embedding vs Referencing**

Trong MongoDB, có 2 cách để thể hiện quan hệ:

| **Embedding** (Nhúng) | **Referencing** (Tham chiếu) |
|:---|:---|
| Lưu dữ liệu con **ngay bên trong** document cha | Lưu **ID** của document con, giống như khóa ngoại trong SQL |
| Giống như bạn để **ví trong túi** | Giống như bạn **nhớ số tài khoản** để rút tiền |
| **Đọc nhanh** (1 query duy nhất) | **Đọc chậm hơn** (cần 2 query hoặc $lookup) |
| **Ghi chậm** (cập nhật cả document) | **Ghi nhanh** (cập nhật từng document) |
| Dùng khi dữ liệu con **ít thay đổi** | Dùng khi dữ liệu con **thay đổi thường xuyên** |

---

## 📚 VÍ DỤ THỰC TẾ: XÂY DỰNG HỆ THỐNG BÁN HÀNG

Hãy tạo một hệ thống **Shop bán hàng** với các mối quan hệ:

1. **User** (Người dùng) - **Cart** (Giỏ hàng): Quan hệ 1-1
2. **User** (Người dùng) - **Order** (Đơn hàng): Quan hệ 1-n
3. **Order** (Đơn hàng) - **Product** (Sản phẩm): Quan hệ n-n

---

### Bước 1: Tạo database và collections

```python
from pymongo import MongoClient
from datetime import datetime
import pprint
from bson import ObjectId

client = MongoClient('mongodb://localhost:27017/')
db = client['shop_online']

# Xóa dữ liệu cũ để chạy thử sạch
db.users.delete_many({})
db.products.delete_many({})
db.orders.delete_many({})

print("✅ Đã reset database!\n")
```

---

### Quan hệ 1-1: User ↔ Cart

**Giải thích:** Mỗi user có **1 và chỉ 1** giỏ hàng. Cart luôn đi cùng user, ít thay đổi cấu trúc.

**Cách làm:** Dùng **Embedding** - Nhúng Cart ngay trong User.

```python
# ---------- 1-1: EMBEDDING (User + Cart) ----------
print("=" * 50)
print("1. QUAN HỆ 1-1: User - Cart (Embedded)")
print("=" * 50)

user_with_cart = {
    "username": "nguyenvana",
    "email": "a@gmail.com",
    "phone": "0909123456",
    "created_at": datetime.now(),
    
    # 👇 Cart được nhúng ngay trong User
    "cart": {
        "items": [
            {
                "product_id": "prod_001",  # Chỉ lưu ID của sản phẩm
                "name": "Laptop Dell XPS",  # Denormalization (lưu thêm tên để khỏi query)
                "quantity": 1,
                "price": 25000000,
                "added_at": datetime.now()
            },
            {
                "product_id": "prod_002",
                "name": "Chuột Logitech MX",
                "quantity": 2,
                "price": 1500000,
                "added_at": datetime.now()
            }
        ],
        "total_items": 3,
        "total_price": 28000000,
        "updated_at": datetime.now()
    }
}

# Lưu user với cart vào DB
result = db.users.insert_one(user_with_cart)
user_id = result.inserted_id
print(f"✅ Đã tạo User với ID: {user_id}")
print(f"📦 Cart có {user_with_cart['cart']['total_items']} sản phẩm\n")

# 👉 LỢI ÍCH: Lấy user kèm cart bằng 1 query DUY NHẤT
user_data = db.users.find_one({"_id": user_id})
print("📖 Lấy user và cart chỉ với 1 query:")
print(f"  - User: {user_data['username']}")
print(f"  - Số lượng giỏ hàng: {len(user_data['cart']['items'])}")
print(f"  - Tổng tiền: {user_data['cart']['total_price']:,}đ")

# ➕ Thêm sản phẩm vào cart (cập nhật trực tiếp trong user)
print("\n🛒 Thêm sản phẩm mới vào giỏ hàng:")
db.users.update_one(
    {"_id": user_id},
    {
        "$push": {
            "cart.items": {
                "product_id": "prod_003",
                "name": "Bàn phím cơ Keychron",
                "quantity": 1,
                "price": 2500000,
                "added_at": datetime.now()
            }
        },
        "$inc": {
            "cart.total_items": 1,
            "cart.total_price": 2500000
        },
        "$set": {"cart.updated_at": datetime.now()}
    }
)

# Kiểm tra lại
updated_user = db.users.find_one({"_id": user_id})
print(f"  ✅ Đã cập nhật: {updated_user['cart']['total_items']} sản phẩm, {updated_user['cart']['total_price']:,}đ\n")
```

---

### Quan hệ 1-n: User ↔ Order

**Giải thích:** 1 user có **nhiều** đơn hàng. Mỗi đơn hàng là 1 document riêng biệt.

**Cách làm:** Dùng **Referencing** - User lưu list order IDs, Order lưu riêng.

```python
# ---------- 1-n: REFERENCING (User - Orders) ----------
print("=" * 50)
print("2. QUAN HỆ 1-n: User - Orders (Referencing)")
print("=" * 50)

# Tạo thêm vài user để test
users_list = [
    {"username": "tranvanb", "email": "b@gmail.com", "phone": "0909456789", "created_at": datetime.now()},
    {"username": "lethic", "email": "c@gmail.com", "phone": "0909789012", "created_at": datetime.now()},
]
db.users.insert_many(users_list)

# Tạo 1 user mới với order trống
new_user = {
    "username": "phamvand",
    "email": "d@gmail.com",
    "phone": "0909345678",
    "created_at": datetime.now(),
    "order_ids": []  # 👈 Chỉ lưu list ID tham chiếu đến các order
}
user_d = db.users.insert_one(new_user)
user_d_id = user_d.inserted_id

# Tạo các đơn hàng (Order documents)
order_1 = {
    "user_id": user_d_id,  # 👈 Reference ngược lại user
    "order_date": datetime.now(),
    "status": "delivered",
    "total_amount": 15000000,
    "items": [
        {"product_id": "prod_001", "name": "iPhone 15", "quantity": 1, "price": 15000000}
    ],
    "shipping_address": "123 Đường Láng, Hà Nội",
    "payment_method": "COD"
}

order_2 = {
    "user_id": user_d_id,
    "order_date": datetime.now(),
    "status": "processing",
    "total_amount": 32000000,
    "items": [
        {"product_id": "prod_004", "name": "iPad Pro", "quantity": 1, "price": 22000000},
        {"product_id": "prod_005", "name": "Apple Pencil", "quantity": 1, "price": 5000000},
        {"product_id": "prod_006", "name": "AirPods Pro", "quantity": 1, "price": 5000000}
    ],
    "shipping_address": "456 Nguyễn Trãi, Hà Nội",
    "payment_method": "Credit Card"
}

# Lưu orders vào collection riêng
order_1_id = db.orders.insert_one(order_1).inserted_id
order_2_id = db.orders.insert_one(order_2).inserted_id

# Cập nhật user với list order IDs
db.users.update_one(
    {"_id": user_d_id},
    {"$set": {"order_ids": [order_1_id, order_2_id]}}
)

print(f"✅ User {new_user['username']} đã có 2 đơn hàng:")
print(f"   - Order 1 ID: {order_1_id}")
print(f"   - Order 2 ID: {order_2_id}")

# 👉 LẤY USER KÈM TẤT CẢ ORDER (Cần 2 bước)
print("\n📖 Lấy user và tất cả orders:")
user_with_orders = db.users.find_one({"_id": user_d_id})

# Bước 1: Lấy user
print(f"  User: {user_with_orders['username']}")

# Bước 2: Lấy tất cả orders từ list ID
if user_with_orders.get('order_ids'):
    orders = db.orders.find(
        {"_id": {"$in": user_with_orders['order_ids']}}
    )
    print("  Đơn hàng:")
    for order in orders:
        print(f"    - {order['_id']}: {order['status']} - {order['total_amount']:,}đ")
print()

# 👉 CÁCH PRO HƠN: DÙNG $lookup (JOIN trong MongoDB)
print("🚀 Cách PRO: Dùng $lookup để JOIN User + Orders trong 1 query:")
pipeline = [
    {"$match": {"_id": user_d_id}},
    {
        "$lookup": {
            "from": "orders",  # Collection orders
            "localField": "_id",  # Field trong users
            "foreignField": "user_id",  # Field trong orders
            "as": "orders"  # Tên field chứa kết quả
        }
    }
]

result = db.users.aggregate(pipeline).next()
print(f"  User: {result['username']}")
print(f"  Tổng đơn: {len(result['orders'])}")
for order in result['orders']:
    print(f"    - {order['status']}: {order['total_amount']:,}đ")
```

---

### Quan hệ n-n: Order ↔ Product

**Giải thích:** 1 order có nhiều sản phẩm, 1 sản phẩm thuộc nhiều order.

**Cách làm:** Dùng **Embedding kết hợp Reference** - Lưu thông tin sản phẩm trong order nhưng chỉ lưu ID + tên + giá (denormalization).

```python
# ---------- n-n: MIXED (Order - Products) ----------
print("=" * 50)
print("3. QUAN HỆ n-n: Order - Products")
print("=" * 50)

# Tạo collection products (sản phẩm)
sample_products = [
    {
        "_id": "prod_001",
        "name": "iPhone 15 Pro Max",
        "brand": "Apple",
        "price": 29990000,
        "category": "Điện thoại",
        "stock": 45,
        "specs": {"ram": 8, "storage": 256, "color": "Titan"}
    },
    {
        "_id": "prod_002",
        "name": "Samsung Galaxy S24 Ultra",
        "brand": "Samsung",
        "price": 25990000,
        "category": "Điện thoại",
        "stock": 30,
        "specs": {"ram": 12, "storage": 512, "color": "Đen"}
    },
    {
        "_id": "prod_003",
        "name": "MacBook Pro 14 M3",
        "brand": "Apple",
        "price": 44990000,
        "category": "Laptop",
        "stock": 15,
        "specs": {"ram": 16, "storage": 512, "chip": "M3 Pro"}
    }
]
db.products.insert_many(sample_products)

# Tạo 1 order mới với nhiều sản phẩm
order_with_products = {
    "user_id": user_d_id,
    "order_date": datetime.now(),
    "status": "pending",
    "total_amount": 0,  # Sẽ tính sau
    # 👇 Embedded: Lưu thông tin sản phẩm TRỰC TIẾP trong order
    "items": [
        {
            "product_id": "prod_001",
            "name": "iPhone 15 Pro Max",  # Denormalization - lưu thêm tên
            "price": 29990000,  # Lưu giá tại thời điểm mua (quan trọng!)
            "quantity": 1,
            "subtotal": 29990000
        },
        {
            "product_id": "prod_002",
            "name": "Samsung Galaxy S24 Ultra",
            "price": 25990000,
            "quantity": 2,
            "subtotal": 51980000
        },
        {
            "product_id": "prod_003",
            "name": "MacBook Pro 14 M3",
            "price": 44990000,
            "quantity": 1,
            "subtotal": 44990000
        }
    ],
    "shipping_address": "789 Lê Văn Lương, Hà Nội",
    "payment_method": "Bank Transfer"
}

# Tính tổng tiền
order_with_products["total_amount"] = sum(item["subtotal"] for item in order_with_products["items"])

# Lưu order
new_order_id = db.orders.insert_one(order_with_products).inserted_id

print(f"✅ Đã tạo đơn hàng mới với {len(order_with_products['items'])} sản phẩm")
print(f"💰 Tổng tiền: {order_with_products['total_amount']:,}đ")

# 🎯 LẤY THÔNG TIN CHI TIẾT SẢN PHẨM KHI CẦN
print("\n📖 Lấy đơn hàng kèm thông tin chi tiết sản phẩm:")
order = db.orders.find_one({"_id": new_order_id})

for item in order['items']:
    # Lấy thêm thông tin chi tiết từ collection products (nếu cần)
    product_detail = db.products.find_one({"_id": item['product_id']})
    print(f"  - {item['name']}: {item['quantity']} x {item['price']:,}đ")
    if product_detail:
        print(f"    📦 Còn {product_detail['stock']} sản phẩm trong kho")
        print(f"    ⚙️ Thông số: {product_detail.get('specs', {})}")
```

---

## 📊 SO SÁNH CÁC CÁCH THIẾT KẾ

```python
print("=" * 50)
print("📊 TỔNG KẾT - KHI NÀO DÙNG GÌ?")
print("=" * 50)

print("""
1️⃣  QUAN HỆ 1-1: Dùng Embedding
   ✅ Lợi ích: Đọc nhanh, 1 query
   ✅ Áp dụng: User-Cart, User-Profile
   ⚠️  Lưu ý: Document có thể phình to nếu cart quá nhiều

2️⃣  QUAN HỆ 1-n: Dùng Referencing
   ✅ Lợi ích: Dễ quản lý, không bị giới hạn kích thước document
   ✅ Áp dụng: User-Orders, Category-Products
   ⚠️  Lưu ý: Cần nhiều query hoặc dùng $lookup

3️⃣  QUAN HỆ n-n: Dùng Mixed (Embedding + Referencing)
   ✅ Lợi ích: Lưu được snapshot tại thời điểm giao dịch
   ✅ Áp dụng: Order-Products, Student-Courses
   ⚠️  Lưu ý: Cần cân đối giữa denormalization và consistency
""")
```

---

## 🎯 BÀI TẬP THỰC HÀNH (QUAN TRỌNG)

Hãy tự thiết kế database cho các tình huống sau:

```python
"""
BÀI TẬP 1: Hệ thống Blog
- Author (Tác giả) - Post (Bài viết): 1-n
- Post - Category (Danh mục): n-n
- Post - Comment (Bình luận): 1-n (comment có thể lồng nhau)

Hỏi: 
- Post nên lưu author_id hay embed author?
- Comment nên embed trong post hay lưu riêng?
- Category nên embed hay reference?

BÀI TẬP 2: Hệ thống quản lý nhân sự
- Employee (Nhân viên) - Department (Phòng ban): n-1
- Employee - Project (Dự án): n-n
- Employee - Salary (Lương): 1-n (theo tháng)

Hỏi:
- Nên lưu department trong employee hay riêng?
- Salary nên lưu trong employee hay riêng?
- Nếu lưu riêng, dùng referencing hay embedding?
"""
```

---

## 💡 ĐÁP ÁN + GIẢI THÍCH CHI TIẾT

<details>
<summary><b>Bài tập 1: Click để xem đáp án</b></summary>

```python
# === BLOG DESIGN ===

# 1. Author - Post: Dùng REFERENCING
# Lý do: Author thay đổi thông tin (tên, email), không muốn update nhiều posts
authors = {
    "_id": ObjectId,
    "name": "Nguyễn Văn A",
    "email": "a@gmail.com"
}

posts = {
    "_id": ObjectId,
    "author_id": ObjectId,  # Reference
    "title": "Học MongoDB",
    "content": "...",
    "created_at": datetime.now()
}

# 2. Post - Category: Dùng REFERENCING (n-n)
# Lý do: Category ít thay đổi, 1 post có nhiều category
categories = {
    "_id": ObjectId,
    "name": "Programming",
    "slug": "programming"
}

posts = {
    # ... các field cũ
    "category_ids": [ObjectId, ObjectId]  # List references
}

# 3. Post - Comment: Dùng EMBEDDING (có giới hạn)
# Lý do: Comment luôn đi với post, đọc nhanh
# ⚠️ Lưu ý: Nếu comment quá nhiều (>100/200), nên dùng referencing
posts = {
    # ... các field cũ
    "comments": [
        {
            "user_name": "Trần Văn B",
            "content": "Bài viết hay!",
            "created_at": datetime.now(),
            "replies": [  # Comment lồng nhau (tối đa vài cấp)
                {
                    "user_name": "Admin",
                    "content": "Cảm ơn bạn!",
                    "created_at": datetime.now()
                }
            ]
        }
    ]
}
```
</details>

<details>
<summary><b>Bài tập 2: Click để xem đáp án</b></summary>

```python
# === HR SYSTEM DESIGN ===

# 1. Employee - Department: Dùng REFERENCING
# Lý do: Nhân viên có thể chuyển phòng ban, chỉ cần update 1 field
employees = {
    "_id": ObjectId,
    "name": "Nguyễn Văn A",
    "department_id": ObjectId,  # Reference
    "position": "Developer"
}

departments = {
    "_id": ObjectId,
    "name": "IT Department",
    "manager_id": ObjectId  # Reference tới employee
}

# 2. Employee - Project: Dùng REFERENCING (n-n)
# Lý do: 1 employee tham gia nhiều project, 1 project có nhiều employee
projects = {
    "_id": ObjectId,
    "name": "Xây dựng hệ thống CRM",
    "employee_ids": [ObjectId, ObjectId],  # List employees
    "start_date": datetime.now()
}

# Hoặc cách 2: Tạo bảng trung gian (JOIN table)
project_members = {
    "project_id": ObjectId,
    "employee_id": ObjectId,
    "role": "Backend Developer",
    "join_date": datetime.now()
}

# 3. Employee - Salary: Dùng REFERENCING (1-n)
# Lý do: Lương thay đổi theo tháng, lưu lịch sử là rất quan trọng
salaries = {
    "_id": ObjectId,
    "employee_id": ObjectId,  # Reference
    "month": "2024-01",
    "base_salary": 20000000,
    "bonus": 5000000,
    "total": 25000000,
    "paid_date": datetime.now()
}

employees = {
    # ... các field cũ
    "current_salary": 20000000,  # Denormalization để đọc nhanh
    "salary_history_ids": [ObjectId, ObjectId]  # Tham chiếu đến lịch sử
}
```
</details>

---

## 🚀 TIPS XƯƠNG MÁU (KINH NGHIỆM 5 NĂM)

1. **Ưu tiên Embedding khi có thể**, vì MongoDB được thiết kế để làm việc với document lớn (16MB/document).
2. **Denormalization là bạn**: Đừng ngại lưu trùng thông tin (ví dụ: lưu cả tên sản phẩm trong order) để tăng tốc đọc.
3. **Dùng ObjectId thay vì string tự tạo**: Nó bao gồm timestamp, có thể sort theo thời gian.
4. **Luôn thêm `created_at` và `updated_at`** vào mọi document - cứu bạn 1000 lần sau này.
5. **Đặt tên field rõ ràng**: `user_id` thay vì `uid`, `created_at` thay vì `c_at`.

---

## ❓ CÂU HỎI CHO BẠN

Sau khi học xong Level 5 (Relationship), bạn muốn học tiếp **Level 6: Transactions** hay **Level 7: Change Streams**?

- **Level 6: Transactions** → Dạy bạn cách đảm bảo toàn vẹn dữ liệu (ví dụ: chuyển khoản, đặt hàng, nếu lỗi thì rollback tất cả). Rất quan trọng cho hệ thống tài chính!
- **Level 7: Change Streams** → Dạy bạn lắng nghe thay đổi trong database (ví dụ: khi có đơn hàng mới, tự động gửi email). Ứng dụng realtime!

Hãy comment cho tôi biết nhé! 🎯