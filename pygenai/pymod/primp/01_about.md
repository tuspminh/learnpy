**`primp`** (Python Requests IMPersonate) là một thư viện Python nhẹ, tốc độ cao được thiết kế để giả lập các dấu vân tay trình duyệt (TLS/JA3 và HTTP/2 fingerprints). Thư viện này giúp bypass các hệ thống chống bot như Cloudflare, Akamai hay Datadome mà không cần dùng đến các trình duyệt nặng như Selenium hay Playwright.

Thư viện được viết trên nền tảng **Rust** (dựa trên crate `rquest`) nên có hiệu năng vượt trội so với `requests` tiêu chuẩn.

---

### Key Features (Tính năng nổi bật)

* **Browser Impersonation:** Giả lập chính xác dấu vân tay TLS/JA3 và HTTP/2 của Chrome, Firefox, Safari, Edge trên các hệ điều hành khác nhau (Windows, macOS, iOS, Android).
* **Hiệu năng cao:** Xử lý bất đồng bộ (async) và đồng bộ (sync) nhanh nhờ backend Rust.
* **API thân thiện:** Cú pháp tương tự thư viện `requests` hoặc `httpx`.
* **Hỗ trợ Proxy:** Hỗ trợ HTTP, HTTPS, SOCKS5 proxies.
* **Auto Cookie Management:** Tự động lưu và quản lý cookie giữa các request.

---

### Cài đặt

```bash
pip install primp

```

---

### Hướng dẫn sử dụng cơ bản

#### 1. Gọi Request Đồng bộ (Synchronous)

```python
import primp

# Khởi tạo Client giả lập Chrome 126 trên Windows
client = primp.Client(impersonate="chrome_126", os="windows")

# Thực hiện GET request
response = client.get("https://httpbin.org/headers")

print(f"Status Code: {response.status_code}")
print(response.json())

```

#### 2. Gọi Request Bất đồng bộ (Asynchronous)

```python
import asyncio
import primp

async def main():
    # Khởi tạo AsyncClient
    client = primp.AsyncClient(impersonate="firefox_120")
    
    response = await client.get("https://httpbin.org/ip")
    print(response.text)

asyncio.run(main())

```

#### 3. Cấu hình Proxy và Headers

```python
import primp

proxy_url = "http://username:password@proxy_host:proxy_port"

client = primp.Client(
    impersonate="safari_17_0",
    proxy=proxy_url,
    headers={"Custom-Header": "Value"},
    cookie_store=True, # Tự động giữ cookie giữa các request
    timeout=10 # Timeout theo giây
)

response = client.get("https://nowsecure.nl")
print(response.status_code)

```

---

### Các tham số chính trong `Client`

| Tham số | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `impersonate` | `str` | Trình duyệt muốn giả lập (vd: `chrome_120`, `chrome_126`, `firefox_120`, `safari_17_0`). |
| `os` | `str` | Hệ điều hành giả lập (`windows`, `macos`, `linux`, `ios`, `android`). |
| `proxy` | `str` | URL Proxy (HTTP/HTTPS/SOCKS5). |
| `headers` | `dict` | Custom HTTP headers bổ sung. |
| `cookie_store` | `bool` | Bật/Tắt tự động lưu cookie (Default: `True`). |
| `timeout` | `float` | Thời gian chờ request tối đa (giây). |
| `verify` | `bool` | Bật/Tắt xác thực chứng chỉ SSL (Default: `True`). |

---

### Ưu điểm & Nhược điểm

* **Ưu điểm:**
* Bỏ qua tốt các lớp bảo vệ TLS fingerprinting mà `requests` hay `httpx` thông thường bị chặn.
* Nhẹ và tiêu tốn cực kỳ ít CPU/RAM so with Headless Browsers.
* Tốc độ cực nhanh do viết bằng Rust.


* **Nhược điểm:**
* Chỉ giải quyết được vấn đề ở tầng mạng (TLS/HTTP Header).
* **Không thực thi JavaScript:** Nếu trang web yêu cầu giải captcha phức tạp bằng JS (Turnstile, ReCAPTCHA v3), bạn vẫn cần kết hợp thêm công cụ giải captcha hoặc trình duyệt thật.