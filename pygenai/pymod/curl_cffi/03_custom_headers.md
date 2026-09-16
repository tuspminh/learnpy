Một số trang web sử dụng kỹ thuật **chống cào hotlink** (Anti-Hotlinking) để ngăn chặn việc tải trực tiếp hình ảnh. Để vượt qua cơ chế này, bạn cần gửi kèm:

* **`Referer` / `Origin**`: Xác nhận request xuất phát từ chính trang web đó chứ không phải script bên ngoài.
* **`Cookie`**: Xác thực phiên làm việc (Session) hoặc xác thực qua Cloudflare/Anti-bot.
* **`User-Agent`**: Khai báo trình duyệt nhất quán.

---

### 1. Thêm Headers và Cookies trực tiếp vào Request

Bạn có thể truyền trực tiếp `headers` và `cookies` dưới dạng `dict` vào phương thức `requests.get()`:

```python
from curl_cffi import requests

image_url = "https://example.com/protected-image.jpg"

# 1. Cấu hình Headers (đặc biệt là Referer)
custom_headers = {
    "Referer": "https://example.com/gallery",  # Header quan trọng nhất chống hotlink
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
    "Sec-Fetch-Dest": "image",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "same-origin",
}

# 2. Cấu hình Cookies nếu trang yêu cầu Login hoặc Token
custom_cookies = {
    "session_id": "abc123xyz_token_key",
    "cf_clearance": "cloudflare_bypass_token_here",
}

# 3. Thực hiện tải ảnh
response = requests.get(
    image_url,
    headers=custom_headers,
    cookies=custom_cookies,
    impersonate="chrome"  # Tự động đồng bộ các TLS Fingerprint tương ứng
)

if response.status_code == 200:
    with open("protected_image.jpg", "wb") as f:
        f.write(response.content)
    print("Tải ảnh thành công!")
else:
    print(f"Lỗi {response.status_code}: Không thể tải ảnh.")

```

---

### 2. Sử dụng `Session` (Khuyên dùng khi cào hàng loạt)

Sử dụng `Session` giúp tự động giữ lại Cookie thu được từ lần truy cập đầu tiên (trang chủ/trang chứa ảnh) và truyền sang các request tải ảnh tiếp theo.

```python
from curl_cffi import requests

# Khởi tạo Session
session = requests.Session(impersonate="chrome")

# Cấu hình Headers chung cho toàn bộ Session
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "en-US,en;q=0.9",
})

# Bước 1: Truy cập trang chứa ảnh để nhận Cookie / Token chống cào
page_url = "https://example.com/post/123"
page_res = session.get(page_url)

# Bước 2: Tải ảnh với Referer là trang vừa truy cập
image_url = "https://example.com/cdn/images/pic1.jpg"

# Cập nhật Referer động đúng với trang chứa ảnh
image_headers = {
    "Referer": page_url
}

img_res = session.get(image_url, headers=image_headers)

if img_res.status_code == 200:
    with open("image_via_session.jpg", "wb") as f:
        f.write(img_res.content)
    print("Tải ảnh bằng Session thành công!")

```

---

### 3. Mẹo xử lý một số chuỗi Header phức tạp (Raw Cookie String)

Nếu bạn copy chuỗi Cookie thô từ Developer Tools (F12) trên trình duyệt (dạng `key1=val1; key2=val2`), bạn không cần parse ra `dict` thủ công mà có thể truyền trực tiếp vào header `Cookie`:

```python
raw_cookie = "cf_clearance=XYZ123; sessionid=ABC456; _ga=GA1.1.789"

headers = {
    "Referer": "https://example.com/",
    "Cookie": raw_cookie  # Truyền trực tiếp chuỗi cookie
}

response = requests.get(
    "https://example.com/image.jpg",
    headers=headers,
    impersonate="chrome"
)

```