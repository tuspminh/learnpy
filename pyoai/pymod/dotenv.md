**module dotenv:**

- **load_dotenv()** # dùng để tải các biến môi trường từ file `.env` vào hệ thống
  
- **dotenv_values()**: Đọc file `.env` và trả về một dữ liệu kiểu từ điển (`dict`) chứa các cặp khóa-giá trị, hoàn toàn không can thiệp hay thay đổi biến môi trường của hệ điều hành.
  
- **find_dotenv()**: Tự động tìm kiếm vị trí của file `.env` bằng cách rà soát ngược lên các thư mục cha.
  

Để viết và nạp tệp `.env` vào Python, bạn cần làm theo 2 bước đơn giản dưới đây.

### load_dotenv()

**1. Cách viết file .env**

Tạo một tệp tin mới và đặt tên chính xác là `.env` (không có phần mở rộng như `.txt`).

**Quy tắc viết:**

- Viết theo định dạng `TÊN_BIẾN=giá_trị`.
- Không dùng dấu cách xung quanh dấu `=`.
- Không cần dùng dấu ngoặc kép cho chuỗi (trừ khi chuỗi có dấu cách).
- Dùng dấu `#` ở đầu dòng để viết ghi chú.

**Ví dụ nội dung file .env:**

env

```text-x-trilium-auto
# Cấu hình Database
DB_HOST=localhost
DB_PORT=5432

# Khóa API bí mật
API_KEY=my_secret_api_key_123
```

---

**2. Cách nạp file .env vào Python**

Để Python đọc được các biến này, thư viện phổ biến và chuẩn nhất hiện nay là **python-dotenv**.

**Bước 2.1: Cài đặt thư viện**

Mở terminal và chạy lệnh:

bash

```text-x-trilium-auto
pip install python-dotenv
```

**Bước 2.2: Viết mã Python để nạp dữ liệu**

Tạo file `main.py` nằm **cùng thư mục** với file `.env` của bạn và viết code như sau:

python

```text-x-trilium-auto
import os
from dotenv import load_dotenv

# Nạp các biến môi trường từ file .env vào hệ thống
load_dotenv()

# Đọc dữ liệu bằng thư viện os chuẩn của Python
db_host = os.getenv("DB_HOST")
api_key = os.getenv("API_KEY")

# Sử dụng dữ liệu
print(f"Database Host: {db_host}")
print(f"API Key: {api_key}")
```

example:

.env

```text-x-trilium-auto
API_KEY="your_secret_key_here"
DATABASE_URL="mongodb://localhost:27017"
```

python

```text-x-trilium-auto
import os
from dotenv import load_dotenv

# Nạp toàn bộ cấu hình từ file .env vào môi trường hệ thống
load_dotenv()

# Lấy dữ liệu ra sử dụng bằng thư viện os của Python
api_key = os.getenv("API_KEY")
db_url = os.getenv("DATABASE_URL")

print(api_key)
```

**💡 Lưu ý quan trọng**

- **Luôn bảo mật:** Thêm `.env` vào file `.gitignore` để không vô tình tải mật khẩu lên GitHub.
- **Tạo file mẫu:** Tạo thêm một file tên là `.env.example` chỉ chứa các tên biến trống (ví dụ: `DB_HOST=`) để hướng dẫn người khác cách cấu hình mà không làm lộ mật khẩu thật.

Nếu bạn muốn tiếp tục triển khai dự án, hãy cho tôi biết:

- Bạn đang làm dự án về **mảng nào** (Web, Tool tự động, Data)?
- Bạn có cần kết nối với **cơ sở dữ liệu** hay **API cụ thể** nào không?
- Bạn có muốn cấu hình để **chạy trên Docker hoặc Deploy lên Cloud** không?

Hai hàm này giúp bạn xử lý file cấu hình linh hoạt hơn so với `load_dotenv()`.

### **1. Hàm find_dotenv()**

- **Chức năng**: Tự động tìm đường dẫn tuyệt đối của file `.env`.
- **Cơ chế**: Tìm ở thư mục hiện tại. Nếu không thấy, nó sẽ tìm ngược lên các thư mục cha.
- **Tham số chính**: `filename` (mặc định là `'.env'`), `raise_error_if_not_found` (mặc định là `False`).

### **2. Hàm dotenv_values()**

- **Chức năng**: Đọc file `.env` và trả về một **Python dictionary** (kiểu dữ liệu từ điển).
- **Đặc điểm**: Không tự động nạp các biến này vào môi trường hệ thống (`os.environ`). Điều này giúp tránh làm ghi đè hoặc ô nhiễm các biến môi trường gốc của máy tính.

---

**Ví dụ code minh họa**

Dưới đây là cách kết hợp cả hai hàm để đọc cấu hình an toàn:

python

```text-x-trilium-auto
import os
from dotenv import dotenv_values, find_dotenv

# 1. Tìm vị trí file .env tự động
path_to_env = find_dotenv()
print(f"Đã tìm thấy file .env tại: {path_to_env}")

# 2. Đọc nội dung file .env thành một dictionary
config = dotenv_values(path_to_env)

# 3. Truy cập dữ liệu từ dictionary vừa đọc
# Giả sử file .env của bạn có chứa DB_USER và DB_PASS
db_user = config.get("DB_USER")
db_pass = config.get("DB_PASS")

print(f"User: {db_user}")

# 4. Kiểm tra hệ thống để chứng minh os.environ không bị ảnh hưởng
print(os.getenv("DB_USER"))  # Sẽ trả về None vì biến chưa bị nạp vào hệ thống
```

---

**Khi nào nên dùng cách này?**

- Bạn có nhiều file cấu hình khác nhau (ví dụ: `.env.dev`, `.env.prod`) và muốn kiểm soát chính xác file nào được đọc.
- Bạn chỉ muốn lấy giá trị cấu hình để dùng trong code, không muốn cấu hình đó ảnh hưởng đến toàn bộ tiến trình hệ thống đang chạy.

Bạn có muốn tôi hướng dẫn cách **tự động chuyển đổi** giữa file cấu hình môi trường phát triển (Development) và môi trường thực tế (Production) bằng hai hàm này không?