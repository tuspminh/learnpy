# 🎯 AGGREGATION TRONG MONGODB - "SIÊU NĂNG LỰC" PHÂN TÍCH DỮ LIỆU

Chào mừng bạn đến với **Aggregation Framework** - một trong những tính năng mạnh mẽ nhất của MongoDB! Nếu Query Operators là "ngôn ngữ" để tìm kiếm, thì Aggregation là **"cỗ máy phân tích"** giúp bạn biến dữ liệu thô thành những insight giá trị.

Hãy tưởng tượng Aggregation như một **dây chuyền sản xuất**:
- Dữ liệu đầu vào → Qua nhiều công đoạn (stages) → Dữ liệu đầu ra đã được xử lý
- Mỗi công đoạn là một `$stage` (bước xử lý)
- Các stages kết nối với nhau tạo thành **pipeline**

---

## 📚 TỔNG QUAN - PIPELINE LÀ GÌ?

```python
from pymongo import MongoClient
from datetime import datetime
import pprint

# Kết nối database
client = MongoClient('mongodb://localhost:27017/')
db = client['ecommerce_analytics']

# Xóa và tạo dữ liệu mới
db.orders.delete_many({})
db.products.delete_many({})
db.customers.delete_many({})

print("=" * 70)
print("📊 AGGREGATION FRAMEWORK - HƯỚNG DẪN CHI TIẾT")
print("=" * 70)
```

---

## 🏗️ DỮ LIỆU MẪU - HỆ THỐNG BÁN HÀNG

Hãy tạo dữ liệu đủ phức tạp để thấy sức mạnh của Aggregation:

```python
# ---------- 1. SẢN PHẨM ----------
products = [
    {
        "product_id": "P001",
        "name": "iPhone 15 Pro Max",
        "category": "Điện thoại",
        "brand": "Apple",
        "price": 29990000,
        "cost": 22000000,
        "tags": ["hot", "new", "premium"],
        "stock": 45,
        "rating": 4.8,
        "warranty_months": 24
    },
    {
        "product_id": "P002",
        "name": "Samsung Galaxy S24 Ultra",
        "category": "Điện thoại",
        "brand": "Samsung",
        "price": 25990000,
        "cost": 19000000,
        "tags": ["hot", "new", "premium"],
        "stock": 30,
        "rating": 4.6,
        "warranty_months": 24
    },
    {
        "product_id": "P003",
        "name": "MacBook Pro 14 M3",
        "category": "Laptop",
        "brand": "Apple",
        "price": 44990000,
        "cost": 35000000,
        "tags": ["premium", "work"],
        "stock": 15,
        "rating": 4.9,
        "warranty_months": 36
    },
    {
        "product_id": "P004",
        "name": "Xiaomi 14 Pro",
        "category": "Điện thoại",
        "brand": "Xiaomi",
        "price": 15990000,
        "cost": 12000000,
        "tags": ["new", "budget"],
        "stock": 78,
        "rating": 4.4,
        "warranty_months": 18
    },
    {
        "product_id": "P005",
        "name": "Dell XPS 16",
        "category": "Laptop",
        "brand": "Dell",
        "price": 38990000,
        "cost": 30000000,
        "tags": ["work", "premium"],
        "stock": 8,
        "rating": 4.7,
        "warranty_months": 24
    },
    {
        "product_id": "P006",
        "name": "Sony WH-1000XM5",
        "category": "Tai nghe",
        "brand": "Sony",
        "price": 7990000,
        "cost": 5000000,
        "tags": ["audio", "premium"],
        "stock": 50,
        "rating": 4.8,
        "warranty_months": 12
    },
    {
        "product_id": "P007",
        "name": "AirPods Pro 2",
        "category": "Tai nghe",
        "brand": "Apple",
        "price": 4990000,
        "cost": 3000000,
        "tags": ["audio", "hot"],
        "stock": 100,
        "rating": 4.6,
        "warranty_months": 12
    },
    {
        "product_id": "P008",
        "name": "Samsung Galaxy Watch 6",
        "category": "Smartwatch",
        "brand": "Samsung",
        "price": 9990000,
        "cost": 7000000,
        "tags": ["wearable"],
        "stock": 25,
        "rating": 4.3,
        "warranty_months": 18
    }
]
db.products.insert_many(products)

# ---------- 2. KHÁCH HÀNG ----------
customers = [
    {
        "customer_id": "C001",
        "name": "Nguyễn Văn A",
        "email": "a@gmail.com",
        "city": "Hà Nội",
        "age": 28,
        "gender": "male",
        "total_spent": 45000000,
        "membership": "gold",
        "join_date": datetime(2023, 1, 15)
    },
    {
        "customer_id": "C002",
        "name": "Trần Thị B",
        "email": "b@gmail.com",
        "city": "Hồ Chí Minh",
        "age": 32,
        "gender": "female",
        "total_spent": 120000000,
        "membership": "platinum",
        "join_date": datetime(2022, 6, 20)
    },
    {
        "customer_id": "C003",
        "name": "Lê Văn C",
        "email": "c@gmail.com",
        "city": "Đà Nẵng",
        "age": 25,
        "gender": "male",
        "total_spent": 25000000,
        "membership": "silver",
        "join_date": datetime(2023, 8, 1)
    },
    {
        "customer_id": "C004",
        "name": "Phạm Thị D",
        "email": "d@gmail.com",
        "city": "Hà Nội",
        "age": 35,
        "gender": "female",
        "total_spent": 89000000,
        "membership": "gold",
        "join_date": datetime(2022, 11, 10)
    },
    {
        "customer_id": "C005",
        "name": "Hoàng Văn E",
        "email": "e@gmail.com",
        "city": "Hồ Chí Minh",
        "age": 22,
        "gender": "male",
        "total_spent": 15000000,
        "membership": "silver",
        "join_date": datetime(2023, 10, 5)
    }
]
db.customers.insert_many(customers)

# ---------- 3. ĐƠN HÀNG ----------
orders = [
    {
        "order_id": "ORD001",
        "customer_id": "C001",
        "customer_name": "Nguyễn Văn A",
        "order_date": datetime(2024, 1, 10),
        "status": "delivered",
        "items": [
            {"product_id": "P001", "name": "iPhone 15 Pro Max", "quantity": 1, "price": 29990000},
            {"product_id": "P006", "name": "Sony WH-1000XM5", "quantity": 1, "price": 7990000}
        ],
        "total_amount": 37980000,
        "shipping_fee": 30000,
        "discount": 500000,
        "payment_method": "credit_card"
    },
    {
        "order_id": "ORD002",
        "customer_id": "C002",
        "customer_name": "Trần Thị B",
        "order_date": datetime(2024, 1, 12),
        "status": "delivered",
        "items": [
            {"product_id": "P003", "name": "MacBook Pro 14 M3", "quantity": 1, "price": 44990000},
            {"product_id": "P007", "name": "AirPods Pro 2", "quantity": 2, "price": 4990000}
        ],
        "total_amount": 54970000,
        "shipping_fee": 0,
        "discount": 1000000,
        "payment_method": "bank_transfer"
    },
    {
        "order_id": "ORD003",
        "customer_id": "C003",
        "customer_name": "Lê Văn C",
        "order_date": datetime(2024, 1, 15),
        "status": "shipped",
        "items": [
            {"product_id": "P002", "name": "Samsung Galaxy S24 Ultra", "quantity": 1, "price": 25990000}
        ],
        "total_amount": 25990000,
        "shipping_fee": 30000,
        "discount": 200000,
        "payment_method": "credit_card"
    },
    {
        "order_id": "ORD004",
        "customer_id": "C004",
        "customer_name": "Phạm Thị D",
        "order_date": datetime(2024, 1, 18),
        "status": "delivered",
        "items": [
            {"product_id": "P004", "name": "Xiaomi 14 Pro", "quantity": 1, "price": 15990000},
            {"product_id": "P005", "name": "Dell XPS 16", "quantity": 1, "price": 38990000},
            {"product_id": "P008", "name": "Samsung Galaxy Watch 6", "quantity": 1, "price": 9990000}
        ],
        "total_amount": 64970000,
        "shipping_fee": 0,
        "discount": 1500000,
        "payment_method": "credit_card"
    },
    {
        "order_id": "ORD005",
        "customer_id": "C001",
        "customer_name": "Nguyễn Văn A",
        "order_date": datetime(2024, 1, 20),
        "status": "pending",
        "items": [
            {"product_id": "P002", "name": "Samsung Galaxy S24 Ultra", "quantity": 2, "price": 25990000}
        ],
        "total_amount": 51980000,
        "shipping_fee": 30000,
        "discount": 1000000,
        "payment_method": "bank_transfer"
    },
    {
        "order_id": "ORD006",
        "customer_id": "C002",
        "customer_name": "Trần Thị B",
        "order_date": datetime(2024, 1, 22),
        "status": "delivered",
        "items": [
            {"product_id": "P001", "name": "iPhone 15 Pro Max", "quantity": 2, "price": 29990000},
            {"product_id": "P006", "name": "Sony WH-1000XM5", "quantity": 1, "price": 7990000}
        ],
        "total_amount": 67970000,
        "shipping_fee": 0,
        "discount": 2000000,
        "payment_method": "credit_card"
    },
    {
        "order_id": "ORD007",
        "customer_id": "C003",
        "customer_name": "Lê Văn C",
        "order_date": datetime(2024, 1, 25),
        "status": "cancelled",
        "items": [
            {"product_id": "P004", "name": "Xiaomi 14 Pro", "quantity": 1, "price": 15990000}
        ],
        "total_amount": 15990000,
        "shipping_fee": 30000,
        "discount": 0,
        "payment_method": "credit_card"
    },
    {
        "order_id": "ORD008",
        "customer_id": "C005",
        "customer_name": "Hoàng Văn E",
        "order_date": datetime(2024, 1, 28),
        "status": "delivered",
        "items": [
            {"product_id": "P007", "name": "AirPods Pro 2", "quantity": 3, "price": 4990000},
            {"product_id": "P008", "name": "Samsung Galaxy Watch 6", "quantity": 1, "price": 9990000}
        ],
        "total_amount": 24960000,
        "shipping_fee": 30000,
        "discount": 500000,
        "payment_method": "bank_transfer"
    }
]
db.orders.insert_many(orders)

print("✅ Đã tạo dữ liệu mẫu:")
print(f"   - {db.products.count_documents({})} sản phẩm")
print(f"   - {db.customers.count_documents({})} khách hàng")
print(f"   - {db.orders.count_documents({})} đơn hàng\n")
```

---

## 🏗️ CÁC STAGE CƠ BẢN TRONG AGGREGATION PIPELINE

### 1️⃣ `$match` - LỌC DỮ LIỆU (Giống find())

```python
print("=" * 70)
print("1️⃣ $match - Lọc dữ liệu đầu vào")
print("=" * 70)

# Lọc các đơn hàng đã giao thành công
pipeline = [
    {"$match": {"status": "delivered"}}
]

print("📦 Đơn hàng đã giao:")
for order in db.orders.aggregate(pipeline):
    print(f"  - {order['order_id']}: {order['customer_name']} - {order['total_amount']:,}đ")

# Kết hợp nhiều điều kiện
pipeline = [
    {"$match": {
        "$and": [
            {"status": "delivered"},
            {"total_amount": {"$gte": 50000000}}
        ]
    }}
]

print("\n💎 Đơn hàng đã giao, giá trị >= 50tr:")
for order in db.orders.aggregate(pipeline):
    print(f"  - {order['order_id']}: {order['total_amount']:,}đ")
```

---

### 2️⃣ `$group` - NHÓM DỮ LIỆU (Giống GROUP BY trong SQL)

```python
print("\n" + "=" * 70)
print("2️⃣ $group - Nhóm và tổng hợp dữ liệu")
print("=" * 70)

# 2.1: Thống kê theo trạng thái đơn hàng
pipeline = [
    {
        "$group": {
            "_id": "$status",  # Nhóm theo status
            "count": {"$sum": 1},  # Đếm số lượng
            "total_revenue": {"$sum": "$total_amount"},  # Tổng doanh thu
            "avg_order_value": {"$avg": "$total_amount"},  # Giá trị TB đơn hàng
            "max_order": {"$max": "$total_amount"},  # Đơn hàng lớn nhất
            "min_order": {"$min": "$total_amount"}  # Đơn hàng nhỏ nhất
        }
    }
]

print("📊 Thống kê theo trạng thái đơn hàng:")
for stat in db.orders.aggregate(pipeline):
    print(f"\n  Status: {stat['_id']}")
    print(f"    - Số lượng: {stat['count']} đơn")
    print(f"    - Tổng doanh thu: {stat['total_revenue']:,}đ")
    print(f"    - TB đơn hàng: {stat['avg_order_value']:,.0f}đ")
    print(f"    - Max: {stat['max_order']:,}đ")
    print(f"    - Min: {stat['min_order']:,}đ")
```

```python
# 2.2: Thống kê doanh thu theo tháng
pipeline = [
    {
        "$group": {
            "_id": {
                "year": {"$year": "$order_date"},
                "month": {"$month": "$order_date"}
            },
            "total_revenue": {"$sum": "$total_amount"},
            "order_count": {"$sum": 1},
            "avg_order_value": {"$avg": "$total_amount"}
        }
    },
    {"$sort": {"_id.year": 1, "_id.month": 1}}  # Sắp xếp theo tháng
]

print("\n📈 Doanh thu theo tháng:")
for stat in db.orders.aggregate(pipeline):
    print(f"  Tháng {stat['_id']['month']}/{stat['_id']['year']}:")
    print(f"    - {stat['order_count']} đơn hàng")
    print(f"    - Doanh thu: {stat['total_revenue']:,}đ")
    print(f"    - TB/đơn: {stat['avg_order_value']:,.0f}đ")
```

```python
# 2.3: Phân tích KHÁCH HÀNG - Ai chi tiêu nhiều nhất?
pipeline = [
    {
        "$group": {
            "_id": "$customer_id",
            "customer_name": {"$first": "$customer_name"},  # Lấy tên đầu tiên
            "total_spent": {"$sum": "$total_amount"},
            "order_count": {"$sum": 1},
            "avg_order_value": {"$avg": "$total_amount"},
            "last_order_date": {"$max": "$order_date"}
        }
    },
    {"$sort": {"total_spent": -1}},  # Sắp xếp giảm dần theo chi tiêu
    {"$limit": 5}  # Lấy top 5
]

print("\n🏆 TOP 5 KHÁCH HÀNG CHI TIÊU NHIỀU NHẤT:")
for idx, customer in enumerate(db.orders.aggregate(pipeline), 1):
    print(f"  {idx}. {customer['customer_name']}")
    print(f"     - Tổng chi: {customer['total_spent']:,}đ")
    print(f"     - Số đơn: {customer['order_count']}")
    print(f"     - TB/đơn: {customer['avg_order_value']:,.0f}đ")
    print(f"     - Đơn gần nhất: {customer['last_order_date'].strftime('%d/%m/%Y')}")
```

---

### 3️⃣ `$project` - BIẾN ĐỔI DỮ LIỆU (Chọn field, tạo field mới)

```python
print("\n" + "=" * 70)
print("3️⃣ $project - Chọn và biến đổi field")
print("=" * 70)

# 3.1: Chọn field và tạo field mới
pipeline = [
    {
        "$project": {
            "order_id": 1,
            "customer_name": 1,
            "total_amount": 1,
            # Tạo field mới
            "total_amount_usd": {"$divide": ["$total_amount", 25000]},  # Đổi sang USD
            "total_amount_vnd_formatted": {"$concat": [{"$toString": "$total_amount"}, " VND"]},
            "is_high_value": {"$cond": {"if": {"$gt": ["$total_amount", 50000000]}, "then": "Cao", "else": "Thấp"}},
            "order_year": {"$year": "$order_date"},
            "order_month": {"$month": "$order_date"},
            "order_day": {"$dayOfMonth": "$order_date"},
            "items_count": {"$size": "$items"}  # Số lượng sản phẩm trong đơn
        }
    },
    {"$limit": 3}
]

print("📝 Dữ liệu đã biến đổi:")
for order in db.orders.aggregate(pipeline):
    print(f"\n  {order['order_id']} - {order['customer_name']}")
    print(f"    - Tổng tiền: {order['total_amount_vnd_formatted']}")
    print(f"    - ≈ {order['total_amount_usd']:.2f} USD")
    print(f"    - Phân loại: {order['is_high_value']}")
    print(f"    - Ngày đặt: {order['order_day']}/{order['order_month']}/{order['order_year']}")
    print(f"    - Số sản phẩm: {order['items_count']}")
```

```python
# 3.2: Xử lý mảng với $map, $reduce
pipeline = [
    {
        "$project": {
            "order_id": 1,
            "customer_name": 1,
            # Tính tổng số lượng sản phẩm
            "total_quantity": {"$sum": "$items.quantity"},
            # Lấy tên các sản phẩm
            "product_names": "$items.name",
            # Tính tổng tiền từng sản phẩm (price * quantity)
            "items_detail": {
                "$map": {
                    "input": "$items",
                    "as": "item",
                    "in": {
                        "product": "$$item.name",
                        "quantity": "$$item.quantity",
                        "price": "$$item.price",
                        "subtotal": {"$multiply": ["$$item.price", "$$item.quantity"]}
                    }
                }
            }
        }
    },
    {"$limit": 2}
]

print("\n📦 Chi tiết sản phẩm trong đơn hàng:")
for order in db.orders.aggregate(pipeline):
    print(f"\n  {order['order_id']} - {order['customer_name']}")
    print(f"    Tổng số lượng: {order['total_quantity']}")
    for item in order['items_detail']:
        print(f"    - {item['product']}: {item['quantity']} x {item['price']:,}đ = {item['subtotal']:,}đ")
```

---

### 4️⃣ `$unwind` - GIẢI NÉN MẢNG (Tạo nhiều document từ 1 document)

```python
print("\n" + "=" * 70)
print("4️⃣ $unwind - Giải nén mảng thành các document riêng lẻ")
print("=" * 70)

# 4.1: Phân tích từng sản phẩm trong đơn hàng
pipeline = [
    {"$match": {"status": "delivered"}},
    {"$unwind": "$items"},  # Giải nén mảng items
    {
        "$group": {
            "_id": "$items.product_id",
            "product_name": {"$first": "$items.name"},
            "total_quantity_sold": {"$sum": "$items.quantity"},
            "total_revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}},
            "order_count": {"$sum": 1}
        }
    },
    {"$sort": {"total_revenue": -1}},
    {"$limit": 5}
]

print("🏆 TOP 5 SẢN PHẨM BÁN CHẠY NHẤT:")
for idx, product in enumerate(db.orders.aggregate(pipeline), 1):
    print(f"  {idx}. {product['product_name']}")
    print(f"     - Đã bán: {product['total_quantity_sold']} sản phẩm")
    print(f"     - Doanh thu: {product['total_revenue']:,}đ")
    print(f"     - Số đơn hàng: {product['order_count']}")
```

```python
# 4.2: Kết hợp $unwind với $lookup để JOIN
pipeline = [
    {"$unwind": "$items"},
    {
        "$lookup": {
            "from": "products",
            "localField": "items.product_id",
            "foreignField": "product_id",
            "as": "product_detail"
        }
    },
    {"$unwind": "$product_detail"},
    {
        "$project": {
            "order_id": 1,
            "customer_name": 1,
            "product_name": "$items.name",
            "quantity": "$items.quantity",
            "price": "$items.price",
            # Lấy thêm thông tin từ product_detail
            "category": "$product_detail.category",
            "brand": "$product_detail.brand",
            "profit_per_unit": {"$subtract": ["$items.price", "$product_detail.cost"]},
            "total_profit": {"$multiply": [
                {"$subtract": ["$items.price", "$product_detail.cost"]},
                "$items.quantity"
            ]}
        }
    },
    {"$limit": 5}
]

print("\n💰 PHÂN TÍCH LỢI NHUẬN THEO SẢN PHẨM:")
for order in db.orders.aggregate(pipeline):
    print(f"\n  Order {order['order_id']} - {order['customer_name']}")
    print(f"    - Sản phẩm: {order['product_name']}")
    print(f"    - {order['quantity']} x {order['price']:,}đ")
    print(f"    - Brand: {order['brand']}, Category: {order['category']}")
    print(f"    - Lợi nhuận/đơn vị: {order['profit_per_unit']:,}đ")
    print(f"    - Tổng lợi nhuận: {order['total_profit']:,}đ")
```

---

### 5️⃣ `$lookup` - JOIN GIỮA CÁC COLLECTION

```python
print("\n" + "=" * 70)
print("5️⃣ $lookup - JOIN dữ liệu giữa các collection")
print("=" * 70)

# 5.1: JOIN orders với customers
pipeline = [
    {
        "$lookup": {
            "from": "customers",
            "localField": "customer_id",
            "foreignField": "customer_id",
            "as": "customer_info"
        }
    },
    {"$unwind": "$customer_info"},  # customer_info là mảng, cần unwind
    {
        "$project": {
            "order_id": 1,
            "order_date": 1,
            "total_amount": 1,
            "status": 1,
            "customer_name": "$customer_info.name",
            "customer_city": "$customer_info.city",
            "customer_membership": "$customer_info.membership",
            "customer_age": "$customer_info.age"
        }
    },
    {"$limit": 3}
]

print("📋 Đơn hàng kèm thông tin khách hàng:")
for order in db.orders.aggregate(pipeline):
    print(f"\n  {order['order_id']} - {order['customer_name']}")
    print(f"    - Thành phố: {order['customer_city']}")
    print(f"    - Hạng thành viên: {order['customer_membership']}")
    print(f"    - Tuổi: {order['customer_age']}")
    print(f"    - Tổng tiền: {order['total_amount']:,}đ")
    print(f"    - Trạng thái: {order['status']}")
```

```python
# 5.2: JOIN nhiều collection - Phân tích đa chiều
pipeline = [
    {"$unwind": "$items"},
    {
        "$lookup": {
            "from": "products",
            "localField": "items.product_id",
            "foreignField": "product_id",
            "as": "product_detail"
        }
    },
    {"$unwind": "$product_detail"},
    {
        "$lookup": {
            "from": "customers",
            "localField": "customer_id",
            "foreignField": "customer_id",
            "as": "customer_info"
        }
    },
    {"$unwind": "$customer_info"},
    {
        "$group": {
            "_id": {
                "city": "$customer_info.city",
                "category": "$product_detail.category"
            },
            "total_revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}},
            "total_quantity": {"$sum": "$items.quantity"},
            "avg_price": {"$avg": "$items.price"}
        }
    },
    {"$sort": {"total_revenue": -1}}
]

print("\n🌏 DOANH THU THEO THÀNH PHỐ VÀ DANH MỤC SẢN PHẨM:")
for data in db.orders.aggregate(pipeline):
    print(f"\n  {data['_id']['city']} - {data['_id']['category']}:")
    print(f"    - Doanh thu: {data['total_revenue']:,}đ")
    print(f"    - Số lượng: {data['total_quantity']}")
    print(f"    - Giá TB: {data['avg_price']:,.0f}đ")
```

---

### 6️⃣ `$unwind` - PHÂN TÍCH NÂNG CAO VỚI MẢNG

```python
print("\n" + "=" * 70)
print("6️⃣ Phân tích tags sản phẩm với $unwind")
print("=" * 70)

# Phân tích tags phổ biến
pipeline = [
    {"$unwind": "$tags"},  # Giải nén mảng tags
    {
        "$group": {
            "_id": "$tags",
            "count": {"$sum": 1},
            "products": {"$push": "$name"}
        }
    },
    {"$sort": {"count": -1}}
]

print("🏷️ TAGS PHỔ BIẾN NHẤT:")
for tag in db.products.aggregate(pipeline):
    print(f"\n  #{tag['_id']} ({tag['count']} sản phẩm):")
    for product in tag['products'][:3]:
        print(f"    - {product}")
    if len(tag['products']) > 3:
        print(f"    - ... và {len(tag['products']) - 3} sản phẩm khác")
```

---

### 7️⃣ `$bucket` - PHÂN CHIA THÀNH CÁC NHÓM

```python
print("\n" + "=" * 70)
print("7️⃣ $bucket - Phân nhóm theo khoảng giá trị")
print("=" * 70)

# Phân tích đơn hàng theo giá trị
pipeline = [
    {
        "$bucket": {
            "groupBy": "$total_amount",
            "boundaries": [0, 10000000, 20000000, 30000000, 50000000, 100000000],
            "default": "≥ 100 triệu",
            "output": {
                "count": {"$sum": 1},
                "total_revenue": {"$sum": "$total_amount"},
                "avg_price": {"$avg": "$total_amount"},
                "orders": {"$push": "$order_id"}  # List các order
            }
        }
    }
]

print("📊 PHÂN PHỐI ĐƠN HÀNG THEO GIÁ TRỊ:")
for bucket in db.orders.aggregate(pipeline):
    boundary = bucket['_id']
    if boundary == "≥ 100 triệu":
        print(f"\n  📦 {boundary}:")
    else:
        print(f"\n  📦 {bucket['_id']:,}đ - {bucket['_id'] + 10000000:,}đ:")
    print(f"    - Số đơn: {bucket['count']}")
    print(f"    - Tổng doanh thu: {bucket['total_revenue']:,}đ")
    print(f"    - TB/đơn: {bucket['avg_price']:,.0f}đ")
    print(f"    - Mã đơn: {', '.join(bucket['orders'][:3])}")
    if len(bucket['orders']) > 3:
        print(f"    - ... và {len(bucket['orders']) - 3} đơn khác")
```

---

### 8️⃣ `$sort` - SẮP XẾP

```python
print("\n" + "=" * 70)
print("8️⃣ $sort - Sắp xếp dữ liệu")
print("=" * 70)

# Sắp xếp nhiều field
pipeline = [
    {"$sort": {
        "status": 1,  # Tăng dần
        "total_amount": -1  # Giảm dần
    }},
    {"$limit": 5}
]

print("📋 Sắp xếp theo status (a-z), total_amount (z-a):")
for order in db.orders.aggregate(pipeline):
    print(f"  {order['status']}: {order['order_id']} - {order['total_amount']:,}đ")
```

---

### 9️⃣ `$facet` - NHIỀU PIPELINE SONG SONG

```python
print("\n" + "=" * 70)
print("9️⃣ $facet - Chạy nhiều pipeline song song")
print("=" * 70)

pipeline = [
    {
        "$facet": {
            # Pipeline 1: Thống kê chung
            "overview": [
                {
                    "$group": {
                        "_id": None,
                        "total_orders": {"$sum": 1},
                        "total_revenue": {"$sum": "$total_amount"},
                        "avg_order_value": {"$avg": "$total_amount"}
                    }
                }
            ],
            # Pipeline 2: Top khách hàng
            "top_customers": [
                {
                    "$group": {
                        "_id": "$customer_id",
                        "name": {"$first": "$customer_name"},
                        "total_spent": {"$sum": "$total_amount"},
                        "order_count": {"$sum": 1}
                    }
                },
                {"$sort": {"total_spent": -1}},
                {"$limit": 3}
            ],
            # Pipeline 3: Thống kê theo status
            "status_stats": [
                {
                    "$group": {
                        "_id": "$status",
                        "count": {"$sum": 1},
                        "revenue": {"$sum": "$total_amount"}
                    }
                }
            ]
        }
    }
]

print("📊 BÁO CÁO TỔNG HỢP (Từ $facet):")
result = list(db.orders.aggregate(pipeline))[0]

print("\n📈 OVERVIEW:")
for stat in result['overview']:
    print(f"  - Tổng đơn: {stat['total_orders']}")
    print(f"  - Tổng doanh thu: {stat['total_revenue']:,}đ")
    print(f"  - TB/đơn: {stat['avg_order_value']:,.0f}đ")

print("\n🏆 TOP CUSTOMERS:")
for idx, customer in enumerate(result['top_custom