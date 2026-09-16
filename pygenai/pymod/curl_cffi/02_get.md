Để lấy **Page Source (HTML)** và **Tải hình ảnh** bằng `curl_cffi`, bạn dùng thuộc tính:

* `response.text`: Đọc mã HTML dạng văn bản (`str`).
* `response.content`: Đọc dữ liệu ảnh dạng nhị phân (`bytes`) rồi ghi vào file.

---

### 1. Code lấy HTML Page Source

```python
from curl_cffi import requests

url = "https://nowsecure.nl"  # Ví dụ trang có Cloudflare

# Lấy HTML và giả lập Chrome để bypass anti-bot
response = requests.get(url, impersonate="chrome")

if response.status_code == 200:
    # 1. Lấy HTML dạng chuỗi (String)
    html_source = response.text
    print("Trích đoạn HTML:")
    print(html_source[:300])

    # 2. Lưu vào file HTML local
    with open("page_source.html", "w", encoding="utf-8") as f:
        f.write(html_source)
    print("Đã lưu thành công file page_source.html")
else:
    print(f"Lỗi truy cập: {response.status_code}")

```

---

### 2. Code Tải Hình Ảnh (Image Downloader)

Khi tải file nhị phân như hình ảnh (PNG, JPG, WebP), hãy sử dụng **`response.content`**:

```python
from curl_cffi import requests

image_url = "https://httpbin.org/image/png"

# Gửi GET request
response = requests.get(image_url, impersonate="chrome")

if response.status_code == 200:
    # Lấy dữ liệu bytes và ghi ra file dưới dạng 'wb' (write binary)
    with open("downloaded_image.png", "wb") as f:
        f.write(response.content)
    print("Tải ảnh thành công!")
else:
    print(f"Lỗi tải ảnh: {response.status_code}")

```

---

### 3. Kết hợp: Bóc tách ảnh từ Page Source và Tải về

Bạn có thể dùng kết hợp `BeautifulSoup` (thư viện `bs4`) để cào HTML, lọc lấy đường dẫn tất cả thẻ `<img>` và tải ảnh hàng loạt:

```python
import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from curl_cffi import requests

target_url = "https://books.toscrape.com/"

# Tạo thư mục lưu ảnh
os.makedirs("downloaded_images", exist_ok=True)

# 1. Lấy Page Source
session = requests.Session(impersonate="chrome")
response = session.get(target_url)

# 2. Parse HTML để tìm link ảnh
soup = BeautifulSoup(response.text, "html.parser")
img_tags = soup.find_all("img")

# 3. Duyệt và tải từng ảnh
for idx, img in enumerate(img_tags):
    img_src = img.get("src")
    if not img_src:
        continue

    # Chuyển đổi tương đối -> đường dẫn tuyệt đối (Absolute URL)
    full_img_url = urljoin(target_url, img_src)
    
    # Tải ảnh
    img_res = session.get(full_img_url)
    if img_res.status_code == 200:
        file_name = f"downloaded_images/image_{idx + 1}.jpg"
        with open(file_name, "wb") as f:
            f.write(img_res.content)
        print(f"Đã tải: {file_name}")

```