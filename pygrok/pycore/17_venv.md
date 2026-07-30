**Bài 17: Thư viện bên ngoài & Virtual Environment**

Khi làm dự án thực tế, bạn gần như **không bao giờ** chỉ dùng thư viện chuẩn của Python.  
Bài này giúp bạn biết cách dùng thư viện bên ngoài một cách chuyên nghiệp và sạch sẽ.

---

### 1. Virtual Environment (Môi trường ảo) – Bắt buộc phải biết

**Tại sao cần venv?**
- Mỗi dự án dùng các phiên bản thư viện khác nhau
- Tránh xung đột giữa các dự án
- Giữ máy tính sạch sẽ
- Dễ đóng gói và triển khai

#### 1.1. Tạo và kích hoạt môi trường ảo

```bash
# Tạo môi trường ảo tên .venv
python -m venv .venv

# Kích hoạt trên Windows
.venv\Scripts\activate

# Kích hoạt trên macOS / Linux
source .venv/bin/activate
```

Khi kích hoạt thành công, bạn sẽ thấy `(.venv)` ở đầu dòng lệnh.

#### 1.2. Tắt môi trường ảo
```bash
deactivate
```

---

### 2. Pip – Quản lý thư viện

```bash
# Cài thư viện
pip install requests
pip install pandas numpy
pip install requests==2.31.0          # cài phiên bản cụ thể

# Xem các thư viện đã cài
pip list

# Xem thông tin một thư viện
pip show requests

# Gỡ thư viện
pip uninstall requests

# Cập nhật pip
python -m pip install --upgrade pip
```

---

### 3. File `requirements.txt` (Rất quan trọng)

Đây là cách chuẩn để chia sẻ dự án với người khác.

```bash
# Tạo file requirements.txt từ môi trường hiện tại
pip freeze > requirements.txt

# Cài tất cả thư viện từ file
pip install -r requirements.txt
```

Nội dung file `requirements.txt` trông như thế này:
```
requests==2.32.3
pandas==2.2.2
numpy==2.0.0
```

---

### 4. Thư viện `requests` – Gọi API

Đây là thư viện phổ biến nhất để gửi HTTP request.

#### 4.1. Cài đặt
```bash
pip install requests
```

#### 4.2. Ví dụ cơ bản – GET request

```python
import requests

response = requests.get("https://api.github.com")

print(response.status_code)  # 200 = thành công
print(response.headers)
print(response.text[:200])  # nội dung thô
```

#### 4.3. Làm việc với JSON API (rất hay dùng)

```python
import requests

response = requests.get("https://api.github.com/users/octocat")

if response.status_code == 200:
    data = response.json()  # chuyển thành dict
    print("Tên:", data["name"])
    print("Công ty:", data["company"])
    print("Số public repo:", data["public_repos"])
else:
    print("Lỗi:", response.status_code)
```

#### 4.4. Gửi dữ liệu (POST)

```python
import requests

url = "https://httpbin.org/post"
data = {"ten": "An", "tuoi": 20}

response = requests.post(url, json=data)
print(response.status_code)
print(response.json())
```

#### 4.5. Xử lý lỗi khi gọi API

```python
import requests

try:
    response = requests.get("https://api.github.com/users/octocat", timeout=5)
    response.raise_for_status()  # tự động raise lỗi nếu status >= 400
    data = response.json()
    print(data["name"])
except requests.exceptions.Timeout:
    print("Quá thời gian chờ")
except requests.exceptions.ConnectionError:
    print("Không kết nối được server")
except requests.exceptions.HTTPError as e:
    print("Lỗi HTTP:", e)
except Exception as e:
    print("Lỗi khác:", e)
```

---

### 5. Một số thư viện phổ biến bạn sẽ dùng nhiều

| Thư viện       | Công dụng chính                     |
|----------------|-------------------------------------|
| `requests`     | Gọi API / HTTP                      |
| `pandas`       | Xử lý dữ liệu dạng bảng             |
| `numpy`        | Tính toán số học, mảng              |
| `openpyxl`     | Đọc/ghi file Excel                  |
| `beautifulsoup4`| Crawl dữ liệu web                  |
| `pillow`       | Xử lý ảnh                           |
| `flask` / `fastapi` | Xây dựng web API               |
| `pytest`       | Viết unit test                      |

---

### 6. Quy trình chuẩn khi bắt đầu một dự án mới

```bash
# 1. Tạo thư mục dự án
mkdir my_project
cd my_project

# 2. Tạo môi trường ảo
python -m venv .venv

# 3. Kích hoạt
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Mac/Linux

# 4. Cài thư viện cần thiết
pip install requests pandas

# 5. Tạo file requirements.txt
pip freeze > requirements.txt

# 6. Bắt đầu viết code
```

---

### Bài tập Bài 17

**Bài 1:**  
- Tạo môi trường ảo tên `.venv`
- Kích hoạt nó
- Cài thư viện `requests`
- Tạo file `requirements.txt`

**Bài 2:**  
Viết chương trình dùng `requests` lấy thông tin user GitHub bất kỳ (ví dụ: `octocat`, `torvalds`…) và in ra:
- Tên
- Bio
- Số public repositories
- Địa chỉ blog (nếu có)

**Bài 3:**  
Gọi API công khai: `https://jsonplaceholder.typicode.com/users`  
In ra danh sách 5 user đầu tiên (tên + email).

**Bài 4:**  
Viết hàm `lay_gia_bitcoin()` dùng API công khai (ví dụ CoinGecko hoặc API khác) để lấy giá Bitcoin hiện tại và in ra.

**Bài 5 (nâng cao):**  
Viết chương trình đơn giản:
1. Gọi API lấy danh sách bài viết (`https://jsonplaceholder.typicode.com/posts`)
2. Lưu 10 bài đầu tiên vào file `posts.json`
3. Đọc lại file và in tiêu đề các bài viết

---

Làm xong gửi code + kết quả (hoặc mô tả bạn đã làm được những gì).  
Tôi sẽ chữa bài và mở **Bài 18: Xử lý dữ liệu với Pandas (cơ bản)**.

Biết dùng `venv` + `pip` + `requests` là bạn đã sẵn sàng làm việc với dữ liệu thực tế và API. Cứ làm kỹ nhé!