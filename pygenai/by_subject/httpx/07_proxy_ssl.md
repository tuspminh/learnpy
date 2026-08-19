Khi làm việc với mạng nội bộ doanh nghiệp (Corporate Network), dữ liệu bảo mật microservices hoặc crawl web chống bị chặn IP, việc cấu hình **Proxy** và **SSL Certificates (TLS)** là kỹ năng không thể thiếu.

Dưới đây là hướng dẫn chi tiết từng trường hợp với `httpx`.

---

## 1. Cấu hình Proxy

Trong `httpx` (từ phiên bản `0.24.0` trở đi), bạn thiết lập proxy rất đơn giản bằng tham số `proxy` ở cấp độ Client.

### A. Proxy cơ bản & Auth Proxy

```python
import httpx

# 1. Proxy HTTP / HTTPS không cần mật khẩu
client = httpx.Client(proxy="http://127.0.0.1:8080")

# 2. Proxy có Username & Password (HTTP Basic Auth)
proxy_url = "http://username:password@proxy.example.com:8080"
with httpx.Client(proxy=proxy_url) as client:
    response = client.get("https://httpbin.org/ip")
    print("IP hiện tại:", response.json())

```

### B. Sử dụng SOCKS5 Proxy

Nếu bạn muốn dùng SOCKS5 proxy (như Tor hoặc Shadowsocks), bạn cần cài thêm thư viện phụ thuộc `socks`:

```bash
pip install httpx[socks]

```

```python
import httpx

# Sử dụng protocol socks5://
client = httpx.Client(proxy="socks5://127.0.0.1:1080")

```

### C. Định tuyến nhiều Proxy bằng `mounts` (Routing/Fine-grained)

Nếu bạn muốn dùng các proxy khác nhau cho các domain/protocol khác nhau (hoặc bỏ qua proxy cho domain nội bộ):

```python
import httpx

# Định nghĩa các transport với proxy tương ứng
mounts = {
    "http://": httpx.HTTPTransport(proxy="http://proxy-http.com:8080"),
    "https://": httpx.HTTPTransport(proxy="http://proxy-https.com:8080"),
    "all://internal.company.com": None # Bỏ qua proxy khi gọi domain nội bộ
}

client = httpx.Client(mounts=mounts)

```

### D. Tự động đọc biến môi trường (Environment Variables)

Nếu bạn muốn `httpx` tự động dùng proxy khai báo sẵn trên hệ điều hành (`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`), tham số `trust_env` mặc định đã là `True`:

```python
import httpx

# httpx sẽ tự động đọc biến môi trường HTTP_PROXY / HTTPS_PROXY
client = httpx.Client(trust_env=True)

```

---

## 2. Cấu hình Custom SSL / TLS Certificates

### A. Tắt xác thực SSL (`verify=False`)

Dùng khi bạn test local, dev environment hoặc kết nối tới server dùng **Self-signed Certificate** (Chứng chỉ tự ký).

> ⚠️ **Cảnh báo:** Không nên dùng `verify=False` trên môi trường Production vì nó khiến ứng dụng dễ bị tấn công Man-in-the-Middle (MitM).

```python
import httpx

# Tắt kiểm tra chứng chỉ SSL
response = httpx.get("https://self-signed.badssl.com", verify=False)
print("Status:", response.status_code)

```

### B. Sử dụng Custom CA Certificate (File `.pem` / `.crt`)

Khi công ty bạn dùng SSL Proxy nội bộ (như Charles Proxy, Fiddler, Fortinet, Zscaler) hoặc server dùng Self-signed CA, bạn truyền đường dẫn tới tệp chứng chỉ CA vào tham số `verify`:

```python
import httpx

# Đường dẫn tới file CA Bundle / Custom Certificate
custom_ca_path = "/path/to/company_corporate_ca.pem"

with httpx.Client(verify=custom_ca_path) as client:
    response = client.get("https://internal-api.company.com")
    print(response.json())

```

### C. Client Certificates / Mutual TLS (mTLS)

Trong kiến trúc bảo mật cao (như ngân hàng, fintech), Server yêu cầu Client cũng phải gửi chứng chỉ để xác thực hai chiều (Mutual TLS).

`httpx` hỗ trợ tham số `cert`:

```python
import httpx

# Trường hợp 1: Cert và Key nằm chung trong 1 file .pem
client = httpx.Client(cert="/path/to/client_cert_and_key.pem")

# Trường hợp 2: Cert và Key tách rời làm 2 file khác nhau
client = httpx.Client(
    cert=(
        "/path/to/client_cert.pem", # File Certificate
        "/path/to/client_key.pem"   # File Private Key
    )
)

# Trường hợp 3: Key có Password bảo vệ
client = httpx.Client(
    cert=(
        "/path/to/client_cert.pem",
        "/path/to/client_key.pem",
        "my_key_password"          # Mật khẩu giải mã Private Key
    )
)

```

---

## 3. Tổng hợp Mẫu Code Production (Kèo cả Proxy lẫn mTLS)

Dưới đây là ví dụ hoàn chỉnh khởi tạo một **AsyncClient** kết hợp vừa chạy qua **Proxy**, vừa xác thực **mTLS** và dùng **Custom CA**:

```python
import asyncio
import httpx

async def main():
    proxy_url = "http://user:secret@proxy.corporate.com:8080"
    custom_ca = "/certs/corporate_ca.pem"
    client_cert = ("/certs/app_client.crt", "/certs/app_client.key")

    async with httpx.AsyncClient(
        proxy=proxy_url,           # Đi qua Proxy
        verify=custom_ca,          # Xác thực SSL Server bằng Custom CA
        cert=client_cert,          # Gửi Client Cert cho mTLS
        timeout=10.0
    ) as client:
        try:
            response = await client.get("https://secure-api.bank.com/v1/accounts")
            response.raise_for_status()
            print("Kết nối an toàn thành công:", response.status_code)
        except httpx.HTTPError as exc:
            print(f"Lỗi kết nối: {exc}")

asyncio.run(main())

```