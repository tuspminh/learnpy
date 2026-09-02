## Bài 2: Kết nối Python với PyMongo & Quản lý Biến Môi Trường

Sau khi hiểu cấu trúc nền tảng của MongoDB, bước tiếp theo là kết nối ứng dụng Python tới MongoDB server một cách an toàn và chuẩn hóa.

---

### 1. Cài đặt các thư viện cần thiết

Mở terminal/command prompt và cài đặt thư viện `pymongo` cùng với `python-dotenv` (để quản lý chuỗi kết nối an toàn):

```bash
pip install pymongo python-dotenv dnspython

```

* `pymongo`: Thư viện chính thức làm việc với MongoDB.
* `python-dotenv`: Giúp nạp các thông tin nhạy cảm (như mật khẩu, URI) từ file `.env`.
* `dnspython`: Bắt buộc nếu bạn dùng kết nối MongoDB Atlas (`mongodb+srv://`).

---

### 2. Quản lý chuỗi kết nối an toàn với `.env`

Tuyệt đối **không hardcode** chuỗi kết nối (URI) chứa mật khẩu vào trực tiếp file mã nguồn Python.

#### Bước 2.1: Tạo file `.env`

Tạo một file tên là `.env` nằm cùng thư mục gốc dự án của bạn và lưu chuỗi kết nối:

```env
# Nếu dùng Local:
MONGO_URI=mongodb://localhost:27017

# Hoặc nếu dùng MongoDB Atlas Cloud:
# MONGO_URI=mongodb+srv://user_cua_ban:password_cua_ban@cluster0.xxx.mongodb.net/?retryWrites=true&w=majority

```

---

### 3. Khởi tạo kết nối trong Python

Viết đoạn mã để kiểm tra kết nối trong file `connect.py`:

```python
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

# 1. Nạp biến môi trường từ file .env
load_dotenv()

# 2. Lấy chuỗi kết nối
MONGO_URI = os.getenv("MONGO_URI")

try:
    # 3. Khởi tạo MongoClient
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

    # 4. Kiểm tra kết nối tới server (ping)
    client.admin.command('ping')
    print("✅ Kết nối tới MongoDB thành công!")

    # 5. Chọn Database và Collection
    db = client["hoc_python_db"]       # Nếu chưa có, DB sẽ tự tạo khi thêm dữ liệu
    collection = db["nhan_vien"]       # Collection tương ứng

    print(f"Đã chọn Database: {db.name}")
    print(f"Đã chọn Collection: {collection.name}")

except ConnectionFailure:
    print("❌ Thất bại: Không thể kết nối tới server MongoDB. Hãy kiểm tra lại service hoặc URI!")
except Exception as e:
    print(f"❌ Có lỗi xảy ra: {e}")

```

---

### 4. Quản lý kết nối (Best Practices)

* **Tái sử dụng Connection Pool:** Đối với ứng dụng lớn, bạn nên khởi tạo `MongoClient` một lần duy nhất khi ứng dụng bắt đầu và dùng lại instance đó. `pymongo` tự động quản lý Connection Pool bên dưới.
* **Timeout:** Việc đặt `serverSelectionTimeoutMS=5000` (5 giây) giúp chương trình của bạn ngắt sớm thay vì treo vô thời hạn nếu kết nối mạng gặp sự cố.

---