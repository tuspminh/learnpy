Cấu hình Proxy trong `curl_cffi` vô cùng đơn giản và tương tự như thư viện `requests` gốc. Bạn chỉ cần định nghĩa tham số `proxies` dưới dạng dictionary chứa URL Proxy.

Thư viện hỗ trợ đầy đủ các giao thức: **HTTP**, **HTTPS**, **SOCKS5**, và **SOCKS5h** (giải mã DNS qua Proxy).

---

### 1. Định dạng URL Proxy chuẩn

* **HTTP/HTTPS Proxy:** `http://[user:password@]host:port`
* **SOCKS5 Proxy (DNS local):** `socks5://[user:password@]host:port`
* **SOCKS5h Proxy (DNS remote - khuyên dùng để tránh rò rỉ DNS):** `socks5h://[user:password@]host:port`

---

### 2. Cấu hình Proxy trong Request đơn lẻ

```python
from curl_cffi import requests

# 1. Định nghĩa cấu hình Proxy
proxies = {
    "http": "http://user:password@123.45.67.89:8080",
    "https": "http://user:password@123.45.67.89:8080",
}

# Hoặc dùng SOCKS5 Proxy
# proxies = {
#     "http": "socks5h://user:password@123.45.67.89:1080",
#     "https": "socks5h://user:password@123.45.67.89:1080",
# }

# 2. Gửi request qua Proxy
try:
    response = requests.get(
        "https://httpbin.org/ip",
        proxies=proxies,
        impersonate="chrome",
        timeout=10 # Nên đặt timeout khi dùng proxy
    )
    print("IP hiện tại của bạn qua Proxy:")
    print(response.json())
except Exception as e:
    print(f"Lỗi kết nối Proxy: {e}")

```

---

### 3. Cấu hình Proxy cố định trong `Session`

Nếu bạn tải nhiều ảnh hoặc cào dữ liệu qua nhiều trang, việc gắn Proxy vào `Session` giúp tất cả các request tự động đi qua Proxy đó mà không cần khai báo lại.

```python
from curl_cffi import requests

session = requests.Session(impersonate="chrome")

# Gán Proxy trực tiếp vào Session
session.proxies = {
    "http": "socks5h://127.0.0.1:9050",  # Ví dụ dùng Tor Proxy
    "https": "socks5h://127.0.0.1:9050",
}

# Tất cả request từ session này sẽ đi qua Proxy
res1 = session.get("https://httpbin.org/ip")
print("IP Request 1:", res1.json().get("origin"))

res2 = session.get("https://httpbin.org/headers")
print("Headers Request 2 thành công!")

```

---

### 4. Cấu hình Proxy bất đồng bộ (`AsyncSession`)

Khi cào dữ liệu hoặc tải ảnh số lượng lớn bằng Async:

```python
import asyncio
from curl_cffi.requests import AsyncSession

async def fetch_with_proxy():
    proxies = {
        "http": "http://123.45.67.89:8080",
        "https": "http://123.45.67.89:8080",
    }

    async with AsyncSession(proxies=proxies, impersonate="chrome") as session:
        response = await session.get("https://httpbin.org/ip")
        print(await response.json())

asyncio.run(fetch_with_proxy())

```

---

### 💡 Lưu ý quan trọng khi chọn loại SOCKS5

* **Nên ưu tiên dùng `socks5h://` thay vì `socks5://**`: Chuỗi `socks5h://` sẽ gửi domain name cho máy chủ Proxy phân giải DNS giúp bạn tránh rò rỉ DNS (DNS Leak) và bypass các trang bị chặn ở cấp độ DNS mạng cục bộ.