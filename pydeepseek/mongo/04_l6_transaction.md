Xuất sắc! Bạn chọn **Level 6: Transactions** - Đây là đỉnh cao của việc làm chủ MongoDB! 

Hãy tưởng tượng: Bạn đang xây dựng hệ thống ngân hàng, chuyển 100 triệu từ tài khoản A sang B. Nếu lưu A xong mà lưu B bị lỗi, tiền sẽ "bốc hơi" khỏi hệ thống. **Transactions** giúp bạn đảm bảo: **Hoặc là cả 2 thao tác thành công, hoặc là không có gì thay đổi** (All-or-Nothing).

---

## 🎯 PHẦN 6: TRANSACTIONS TRONG MONGODB

### 📌 ĐIỀU KIỆN TIÊN QUYẾT

Transactions trong MongoDB **chỉ hoạt động với Replica Set** (không dùng standalone). Đừng lo, tôi sẽ hướng dẫn bạn chạy Replica Set trên máy tính cá nhân cực kỳ đơn giản!

---

### BƯỚC 1: CÀI ĐẶT REPLICA SET (CHỈ 5 PHÚT)

**Cách 1: Dùng Docker (Khuyến nghị - Nhanh nhất)**

```bash
# Tạo network cho MongoDB
docker network create mongo-network

# Chạy 3 container MongoDB tạo thành Replica Set
docker run -d --name mongo1 --network mongo-network -p 27017:27017 mongo:latest mongod --replSet rs0 --bind_ip_all
docker run -d --name mongo2 --network mongo-network -p 27018:27017 mongo:latest mongod --replSet rs0 --bind_ip_all
docker run -d --name mongo3 --network mongo-network -p 27019:27017 mongo:latest mongod --replSet rs0 --bind_ip_all

# Kết nối vào mongo1 và khởi tạo Replica Set
docker exec -it mongo1 mongosh --eval "rs.initiate({
  _id: 'rs0',
  members: [
    {_id: 0, host: 'mongo1:27017'},
    {_id: 1, host: 'mongo2:27017'},
    {_id: 2, host: 'mongo3:27017'}
  ]
})"
```

**Cách 2: Không dùng Docker?** 
Hãy comment bên dưới, tôi sẽ hướng dẫn bạn cài đặt thủ công (dài hơn nhưng cũng được).

---

### BƯỚC 2: KẾT NỐI VÀO REPLICA SET

```python
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import time
from datetime import datetime
import random

# Kết nối vào Replica Set (lưu ý: thay địa chỉ nếu bạn dùng IP khác)
client = MongoClient(
    "mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0"
)

# Hoặc nếu dùng Docker với hostname khác
# client = MongoClient(
#     "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0"
# )

db = client['banking_system']

# Xóa dữ liệu cũ để test
db.accounts.delete_many({})
db.transaction_logs.delete_many({})

print("✅ Kết nối thành công vào Replica Set!")
print(f"📍 Primary node: {client.primary}\n")
```

---

### BƯỚC 3: TẠO DỮ LIỆU MẪU (TÀI KHOẢN NGÂN HÀNG)

```python
# Tạo các tài khoản ngân hàng
accounts = [
    {
        "_id": "acc_001",
        "owner": "Nguyễn Văn A",
        "balance": 100000000,  # 100 triệu
        "account_type": "saving",
        "created_at": datetime.now(),
        "transactions": []  # Lịch sử giao dịch
    },
    {
        "_id": "acc_002",
        "owner": "Trần Thị B",
        "balance": 50000000,  # 50 triệu
        "account_type": "checking",
        "created_at": datetime.now(),
        "transactions": []
    },
    {
        "_id": "acc_003",
        "owner": "Lê Văn C",
        "balance": 200000000,  # 200 triệu
        "account_type": "saving",
        "created_at": datetime.now(),
        "transactions": []
    }
]

db.accounts.insert_many(accounts)
print("✅ Đã tạo 3 tài khoản mẫu:")
for acc in db.accounts.find():
    print(f"  - {acc['owner']}: {acc['balance']:,}đ")
print()
```

---

### BƯỚC 4: TRANSACTION CƠ BẢN - CHUYỂN TIỀN

Đây là kịch bản **kinh điển** trong mọi hệ thống tài chính:

```python
def chuyen_tien(from_acc_id, to_acc_id, amount, description="Chuyển khoản"):
    """
    Hàm chuyển tiền AN TOÀN với Transaction
    
    Args:
        from_acc_id: ID tài khoản gửi
        to_acc_id: ID tài khoản nhận
        amount: Số tiền chuyển
        description: Nội dung chuyển khoản
    
    Returns:
        dict: Kết quả giao dịch
    """
    
    # BẮT ĐẦU SESSION (quan trọng!)
    with client.start_session() as session:
        # BẮT ĐẦU TRANSACTION
        session.start_transaction()
        
        try:
            print(f"\n🔄 Bắt đầu giao dịch: {amount:,}đ từ {from_acc_id} -> {to_acc_id}")
            
            # --- BƯỚC 1: Lấy thông tin tài khoản gửi ---
            from_acc = db.accounts.find_one(
                {"_id": from_acc_id},
                session=session  # 👈 QUAN TRỌNG: Gắn session vào query
            )
            
            if not from_acc:
                raise ValueError(f"Không tìm thấy tài khoản {from_acc_id}")
            
            if from_acc['balance'] < amount:
                raise ValueError(f"Số dư không đủ! Hiện có: {from_acc['balance']:,}đ")
            
            # --- BƯỚC 2: Lấy thông tin tài khoản nhận ---
            to_acc = db.accounts.find_one(
                {"_id": to_acc_id},
                session=session
            )
            
            if not to_acc:
                raise ValueError(f"Không tìm thấy tài khoản {to_acc_id}")
            
            # --- BƯỚC 3: Cập nhật số dư tài khoản gửi (trừ tiền) ---
            db.accounts.update_one(
                {"_id": from_acc_id},
                {"$inc": {"balance": -amount}},
                session=session
            )
            print(f"  ✅ Đã trừ {amount:,}đ từ {from_acc['owner']}")
            
            # --- BƯỚC 4: Cập nhật số dư tài khoản nhận (cộng tiền) ---
            db.accounts.update_one(
                {"_id": to_acc_id},
                {"$inc": {"balance": amount}},
                session=session
            )
            print(f"  ✅ Đã cộng {amount:,}đ cho {to_acc['owner']}")
            
            # --- BƯỚC 5: Ghi log giao dịch (để sau này kiểm tra) ---
            transaction_id = f"TXN_{int(time.time())}_{random.randint(1000, 9999)}"
            
            log_entry = {
                "transaction_id": transaction_id,
                "from_account": from_acc_id,
                "to_account": to_acc_id,
                "amount": amount,
                "description": description,
                "timestamp": datetime.now(),
                "status": "success",
                "from_balance_after": from_acc['balance'] - amount,
                "to_balance_after": to_acc['balance'] + amount
            }
            
            db.transaction_logs.insert_one(log_entry, session=session)
            print(f"  ✅ Đã ghi log: {transaction_id}")
            
            # --- BƯỚC 6: COMMIT TRANSACTION (THÀNH CÔNG) ---
            session.commit_transaction()
            print(f"🎉 GIAO DỊCH THÀNH CÔNG! {transaction_id}\n")
            
            return {
                "success": True,
                "transaction_id": transaction_id,
                "message": "Chuyển tiền thành công"
            }
            
        except Exception as e:
            # --- NẾU LỖI: ABORT TRANSACTION (ROLLBACK) ---
            print(f"❌ LỖI: {str(e)}")
            print("🔄 Đang rollback...")
            session.abort_transaction()
            print("✅ Đã rollback! Không có thay đổi nào được lưu.\n")
            
            return {
                "success": False,
                "error": str(e),
                "message": "Giao dịch thất bại"
            }
```

---

### BƯỚC 5: TEST TRANSACTION

```python
print("=" * 60)
print("🧪 TEST TRANSACTION - CHUYỂN TIỀN")
print("=" * 60)

# Lấy số dư ban đầu
print("\n📊 Số dư BAN ĐẦU:")
for acc in db.accounts.find({}, {"owner": 1, "balance": 1, "_id": 1}):
    print(f"  {acc['owner']}: {acc['balance']:,}đ")

# ===== TEST 1: Giao dịch thành công =====
print("\n" + "=" * 40)
print("TEST 1: Chuyển 10 triệu từ A -> B")
print("=" * 40)

result = chuyen_tien("acc_001", "acc_002", 10000000, "Chuyển tiền đầu tháng")
print(f"Kết quả: {result}")

# ===== TEST 2: Giao dịch thất bại (không đủ tiền) =====
print("\n" + "=" * 40)
print("TEST 2: Chuyển 200 triệu từ B -> C (B chỉ có 50tr)")
print("=" * 40)

result = chuyen_tien("acc_002", "acc_003", 200000000, "Mua nhà")
print(f"Kết quả: {result}")

# ===== TEST 3: Giao dịch với tài khoản không tồn tại =====
print("\n" + "=" * 40)
print("TEST 3: Chuyển đến tài khoản không tồn tại")
print("=" * 40)

result = chuyen_tien("acc_001", "acc_999", 5000000, "Chuyển nhầm")
print(f"Kết quả: {result}")

# Kiểm tra số dư CUỐI CÙNG
print("\n📊 Số dư CUỐI CÙNG:")
for acc in db.accounts.find({}, {"owner": 1, "balance": 1, "_id": 1}):
    print(f"  {acc['owner']}: {acc['balance']:,}đ")
```

---

### BƯỚC 6: TRANSACTION NÂNG CAO - NHIỀU THAO TÁC PHỨC TẠP

```python
def dat_hang_va_thanh_toan(user_id, cart_items, shipping_address):
    """
    Hệ thống đặt hàng với Transaction:
    1. Kiểm tra tồn kho từng sản phẩm
    2. Trừ stock
    3. Trừ tiền user
    4. Tạo đơn hàng
    5. Ghi log
    """
    
    with client.start_session() as session:
        session.start_transaction()
        
        try:
            print(f"\n🛒 Bắt đầu đặt hàng cho user {user_id}")
            total_amount = 0
            order_items = []
            
            # --- BƯỚC 1: Kiểm tra và trừ stock từng sản phẩm ---
            for item in cart_items:
                product_id = item['product_id']
                quantity = item['quantity']
                
                # Tìm sản phẩm (có lock để tránh race condition)
                product = db.products.find_one_and_update(
                    {
                        "_id": product_id,
                        "stock": {"$gte": quantity}  # Chỉ lấy nếu đủ hàng
                    },
                    {"$inc": {"stock": -quantity}},  # Trừ stock
                    session=session,
                    return_document=True
                )
                
                if not product:
                    raise ValueError(f"Sản phẩm {product_id} không đủ hàng hoặc không tồn tại")
                
                # Tính tiền
                subtotal = product['price'] * quantity
                total_amount += subtotal
                
                order_items.append({
                    "product_id": product_id,
                    "name": product['name'],
                    "price": product['price'],
                    "quantity": quantity,
                    "subtotal": subtotal
                })
                
                print(f"  ✅ Trừ stock: {product['name']} - còn {product['stock']}")
            
            # --- BƯỚC 2: Trừ tiền user ---
            user = db.users.find_one_and_update(
                {"_id": user_id, "balance": {"$gte": total_amount}},
                {"$inc": {"balance": -total_amount}},
                session=session,
                return_document=True
            )
            
            if not user:
                raise ValueError(f"User {user_id} không đủ tiền hoặc không tồn tại")
            
            print(f"  ✅ Trừ tiền: {total_amount:,}đ - Số dư còn {user['balance']:,}đ")
            
            # --- BƯỚC 3: Tạo đơn hàng ---
            order = {
                "user_id": user_id,
                "items": order_items,
                "total_amount": total_amount,
                "shipping_address": shipping_address,
                "status": "processing",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            order_id = db.orders.insert_one(order, session=session).inserted_id
            print(f"  ✅ Tạo đơn hàng: {order_id}")
            
            # --- BƯỚC 4: Ghi log thanh toán ---
            payment_log = {
                "order_id": order_id,
                "user_id": user_id,
                "amount": total_amount,
                "method": "bank_transfer",
                "status": "success",
                "timestamp": datetime.now()
            }
            db.payment_logs.insert_one(payment_log, session=session)
            print(f"  ✅ Ghi log thanh toán")
            
            # --- BƯỚC 5: Commit ---
            session.commit_transaction()
            print(f"🎉 ĐẶT HÀNG THÀNH CÔNG! Mã đơn: {order_id}\n")
            
            return {
                "success": True,
                "order_id": order_id,
                "total_amount": total_amount,
                "message": "Đặt hàng thành công"
            }
            
        except Exception as e:
            print(f"❌ LỖI: {str(e)}")
            print("🔄 Đang rollback...")
            session.abort_transaction()
            print("✅ Đã rollback! Không có thay đổi nào được lưu.\n")
            
            return {
                "success": False,
                "error": str(e),
                "message": "Đặt hàng thất bại"
            }
```

---

### BƯỚC 7: TEST HỆ THỐNG ĐẶT HÀNG

```python
# Tạo thêm dữ liệu cho hệ thống đặt hàng
print("\n" + "=" * 60)
print("🧪 TEST HỆ THỐNG ĐẶT HÀNG VỚI TRANSACTION")
print("=" * 60)

# Tạo thêm user và product
db.users.insert_one({
    "_id": "user_001",
    "name": "Nguyễn Văn A",
    "balance": 50000000,  # 50 triệu
    "created_at": datetime.now()
})

db.products.insert_many([
    {
        "_id": "prod_001",
        "name": "Laptop Dell XPS",
        "price": 25000000,
        "stock": 10
    },
    {
        "_id": "prod_002",
        "name": "iPhone 15 Pro",
        "price": 29990000,
        "stock": 5
    },
    {
        "_id": "prod_003",
        "name": "Tai nghe Sony WH-1000XM5",
        "price": 8000000,
        "stock": 20
    }
])

# Test đặt hàng thành công
cart = [
    {"product_id": "prod_001", "quantity": 1},
    {"product_id": "prod_003", "quantity": 2}
]

result = dat_hang_va_thanh_toan(
    user_id="user_001",
    cart_items=cart,
    shipping_address="123 Nguyễn Trãi, Hà Nội"
)
print(f"Kết quả: {result}")

# Test đặt hàng thất bại (không đủ tiền)
print("\n" + "=" * 40)
print("TEST ĐẶT HÀNG THẤT BẠI - KHÔNG ĐỦ TIỀN")
print("=" * 40)

cart_expensive = [
    {"product_id": "prod_001", "quantity": 2},  # 50 triệu
    {"product_id": "prod_002", "quantity": 1}   # 29.99 triệu -> Tổng ~80 triệu > 50tr
]

result = dat_hang_va_thanh_toan(
    user_id="user_001",
    cart_items=cart_expensive,
    shipping_address="456 Lê Lợi, Hà Nội"
)
print(f"Kết quả: {result}")
```

---

## 📊 SO SÁNH TRANSACTION VS KHÔNG TRANSACTION

```python
print("\n" + "=" * 60)
print("📊 SO SÁNH KHÔNG TRANSACTION VS CÓ TRANSACTION")
print("=" * 60)

print("""
❌  KHÔNG TRANSACTION:
   Tình huống: Chuyển tiền A -> B
   1. Trừ tiền A thành công ✅
   2. Cộng tiền B thất bại ❌ (mất kết nối, lỗi DB,...)
   🔥 Kết quả: TIỀN BỐC HƠI! A mất 10tr, B không nhận được

✅  CÓ TRANSACTION:
   Tình huống: Chuyển tiền A -> B
   1. Bắt đầu transaction
   2. Trừ tiền A (chưa commit)
   3. Cộng tiền B thất bại (lỗi)
   4. Abort transaction (ROLLBACK)
   ✅ Kết quả: KHÔNG CÓ GÌ THAY ĐỔI! An toàn tuyệt đối
""")

print("🔑 KIẾN THỨC QUAN TRỌNG:")
print("""
1. SESSION: Mỗi transaction cần 1 session riêng
2. TRANSACTION: start_transaction() -> commit_transaction() hoặc abort_transaction()
3. THAM SỐ session: Mọi query đều phải truyền session=session
4. ATOMIC: Hoặc tất cả thành công, hoặc tất cả thất bại
5. LOCKING: Dữ liệu bị khóa trong transaction (không ai sửa được)
""")
```

---

## 🎯 BÀI TẬP THỰC HÀNH

```python
"""
BÀI TẬP 1: Hệ thống quản lý tour du lịch
Tạo transaction cho việc đặt tour:
- Kiểm tra số chỗ còn lại
- Trừ chỗ
- Trừ tiền user
- Tạo booking
- Nếu thất bại -> rollback hết

BÀI TẬP 2: Hệ thống bán vé máy bay (KHÓ)
Xây dựng transaction với 2 phase:
1. Tạm giữ chỗ (hold seat) - 15 phút
2. Thanh toán (payment)
- Nếu hết 15 phút chưa thanh toán -> release seat
- Nếu thanh toán thất bại -> release seat

BÀI TẬP 3: Hệ thống chuyển khoản nhiều người (SIÊU KHÓ)
Chuyển tiền từ 1 tài khoản đến NHIỀU tài khoản cùng lúc:
- Tài khoản A: 100tr
- Chuyển A -> B: 20tr
- Chuyển A -> C: 30tr
- Chuyển A -> D: 40tr
Nếu bất kỳ ai lỗi -> rollback tất cả
"""
```

<details>
<summary><b>ĐÁP ÁN BÀI TẬP 1: Click để xem</b></summary>

```python
def dat_tour(user_id, tour_id, so_luong_nguoi):
    with client.start_session() as session:
        session.start_transaction()
        
        try:
            # Kiểm tra tour còn chỗ không
            tour = db.tours.find_one_and_update(
                {"_id": tour_id, "cho_trong": {"$gte": so_luong_nguoi}},
                {"$inc": {"cho_trong": -so_luong_nguoi}},
                session=session,
                return_document=True
            )
            
            if not tour:
                raise ValueError("Tour không đủ chỗ")
            
            # Trừ tiền
            tong_tien = tour['gia'] * so_luong_nguoi
            user = db.users.find_one_and_update(
                {"_id": user_id, "balance": {"$gte": tong_tien}},
                {"$inc": {"balance": -tong_tien}},
                session=session,
                return_document=True
            )
            
            if not user:
                raise ValueError("Không đủ tiền")
            
            # Tạo booking
            booking = {
                "user_id": user_id,
                "tour_id": tour_id,
                "so_luong": so_luong_nguoi,
                "tong_tien": tong_tien,
                "booking_date": datetime.now(),
                "status": "confirmed"
            }
            db.bookings.insert_one(booking, session=session)
            
            session.commit_transaction()
            return {"success": True, "booking": booking}
            
        except Exception as e:
            session.abort_transaction()
            return {"success": False, "error": str(e)}
```
</details>

---

## 🔥 TIPS VÀNG CHO TRANSACTIONS

1. **Giữ transaction ngắn nhất có thể** - Càng lâu càng dễ bị timeout và lock
2. **Không query chậm trong transaction** - Index là tối quan trọng
3. **Bắt lỗi cụ thể** - Phân biệt lỗi network, lỗi logic, lỗi timeout
4. **Retry logic** - Nếu lỗi network, thử lại 2-3 lần
5. **Theo dõi transaction** - Dùng `currentOp()` để xem transaction đang chạy

```python
# Retry logic mẫu
def chuyen_tien_voi_retry(from_acc, to_acc, amount, max_retry=3):
    for attempt in range(max_retry):
        result = chuyen_tien(from_acc, to_acc, amount)
        if result['success']:
            return result
        print(f"⏳ Thử lại lần {attempt + 1}/{max_retry}")
        time.sleep(1)
    return {"success": False, "error": "Quá số lần thử"}
```

---

## ❓ CÂU HỎI CHO BẠN

Chúc mừng bạn đã học xong **Level 6: Transactions**! 🎉

Giờ bạn đã có thể xây dựng hệ thống tài chính, đặt hàng, chuyển tiền một cách AN TOÀN tuyệt đối.

Bạn muốn học tiếp:

- **Level 7: Change Streams** - Làm realtime app, lắng nghe thay đổi database
- **Hay muốn tôi tổng hợp 1 project HOÀN CHỈNH kết hợp TẤT CẢ kiến thức đã học?**

Comment cho tôi biết nhé! 🚀