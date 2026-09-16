**`curl_cffi`** là thư viện Python binding cho `libcurl` thông qua CFFI (C Foreign Function Interface), nổi tiếng với khả năng **giả lập dấu vết HTTP/TLS (Browser Fingerprinting)** giống hệt các trình duyệt thật như Chrome, Safari hay Firefox để vượt qua hệ thống chống cào dữ liệu (Anti-bot / Cloudflare).

---

**Cài đặt**

```bash
pip install curl_cffi --upgrade

```

---

**Tính năng cốt lõi**

* **Giả lập Browser Fingerprint:** Mô phỏng chính xác TLS/JA3 và HTTP/2 fingerprints của Chrome, Safari, Edge mà không cần chạy trình duyệt thật (Headless Browser) như Selenium/Playwright.
* **Tốc độ vượt trội:** Chạy trên nền tảng `libcurl` bằng C, hiệu năng nhanh hơn nhiều so với `requests` hay `httpx`.
* **Cú pháp thân thiện:** Hỗ trợ API dạng `requests` (`requests.get`, `Session`) và cả Async/Await (`AsyncSession`).
* **Hỗ trợ HTTP/2 & HTTP/3:** Đầy đủ giao thức mạng hiện đại.

---

**Cách sử dụng phổ biến**

1. **Gửi Request cơ bản với Browser Impersonation**

```python
from curl_cffi import requests

# Giả lập trình duyệt Chrome phiên bản mới
response = requests.get(
    "https://nowsecure.nl", 
    impersonate="chrome"
)

print(response.status_code)
print(response.text[:200])

```

2. **Sử dụng Session duy trì Cookie & Headers**

```python
from curl_cffi import requests

session = requests.Session(impersonate="chrome120")

# Request 1: Đăng nhập/Khởi tạo
res1 = session.get("https://httpbin.org/cookies/set/session_id/12345")

# Request 2: Truy cập trang nội bộ với cookie đã lưu
res2 = session.get("https://httpbin.org/cookies")
print(res2.json())

```

3. **Chạy Bất đồng bộ (Async)**

```python
import asyncio
from curl_cffi.requests import AsyncSession

async def fetch():
    async with AsyncSession(impersonate="safari17_0") as s:
        response = await s.get("https://httpbin.org/ip")
        print(response.json())

asyncio.run(fetch())

```

---

**So sánh `curl_cffi` với các thư viện khác**

| Tiêu chí | `requests` / `httpx` | `curl_cffi` | Selenium / Playwright |
| --- | --- | --- | --- |
| **Tốc độ** | Rất nhanh | Rất nhanh | Chậm (tốn RAM/CPU) |
| **Vượt Cloudflare/Akamai** | Dễ bị phát hiện (Rất kém) | **Rất tốt** (Giả lập TLS) | Tốt (nhưng dễ lộ automation) |
| **Render JavaScript** | Không hỗ trợ | Không hỗ trợ | Có hỗ trợ |
| **Dấu vết TLS (JA3/JA4)** | Chuẩn Python (BoringSSL/OpenSSL) | **Chuẩn Browser** (libcurl-impersonate) | Chuẩn Browser thật |