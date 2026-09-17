# Buổi 14 — Proxy với `primp`

Ở Buổi 13 chúng ta học Authentication. Hôm nay đi vào **Proxy**, một thành phần rất quan trọng với Novel Crawler.

Mục tiêu của buổi này:

```text
Proxy cơ bản
    ↓
HTTP / HTTPS Proxy
    ↓
Proxy URL
    ↓
Proxy Authentication
    ↓
Proxy + Timeout
    ↓
Proxy + PrimpFetcher
    ↓
Chuẩn bị ProxyPool
```

Theo tài liệu hiện tại của `primp` 2.0.1, proxy được hỗ trợ ở mức `Client`, với các kiểu cấu hình HTTP/HTTPS và SOCKS; API Rust hiện tại có `Proxy::http()`, `Proxy::https()`, `Proxy::all()` và hỗ trợ Basic proxy authentication. ([Docs.rs][1])

> **Lưu ý:** Phần dưới đây tập trung vào Python API `primp`. Vì tài liệu Python bindings thay đổi theo phiên bản, nếu API proxy trên bản `primp` bạn cài khác với ví dụ, hãy kiểm tra đúng version trước khi áp dụng vào project.

---

# 1. Proxy là gì?

Không có proxy:

```text
Python
   │
   │ HTTP Request
   ▼
Internet
   │
   ▼
Website
```

Có proxy:

```text
Python
   │
   │ HTTP Request
   ▼
 Proxy
   │
   │ Request
   ▼
Internet
   │
   ▼
Website
```

Website nhìn thấy kết nối từ **proxy**, thay vì kết nối trực tiếp từ client của bạn.

---

# 2. Proxy không phải VPN

Đừng đồng nhất:

```text
Proxy ≠ VPN
```

Proxy thường được cấu hình ở cấp application/client:

```text
Python
  │
  └── primp
       │
       └── proxy
```

VPN thường tác động ở cấp hệ điều hành/network interface.

Với crawler, ta thường quan tâm proxy ở cấp HTTP client vì có thể quyết định:

```text
Request A → Proxy A
Request B → Proxy B
Request C → Proxy C
```

Sau này chính điều này sẽ dẫn đến:

```text
ProxyPool
```

---

# 3. Tại sao Novel Crawler cần Proxy?

Ví dụ crawler:

```text
Novel Crawler
      │
      ├── Request 1
      ├── Request 2
      ├── Request 3
      ├── Request 4
      └── Request 5
```

Nếu tất cả đi trực tiếp:

```text
Crawler
   │
   ▼
Website
```

thì server có thể nhìn thấy toàn bộ traffic đến từ cùng một network origin.

Khi có proxy:

```text
             ┌── Proxy A ──► Website
Crawler ─────┼── Proxy B ──► Website
             └── Proxy C ──► Website
```

Nhưng **proxy không phải cách đảm bảo vượt anti-bot hoặc rate limit**. Website vẫn có thể nhận diện client bằng nhiều tín hiệu khác nhau.

---

# 4. Proxy URL

Một proxy thường có dạng:

```text
http://host:port
```

Ví dụ:

```text
http://127.0.0.1:8080
```

Hoặc:

```text
http://proxy.example.com:3128
```

Proxy có authentication:

```text
http://username:password@proxy.example.com:3128
```

HTTPS proxy:

```text
https://proxy.example.com:443
```

SOCKS5:

```text
socks5://127.0.0.1:1080
```

`primp` hiện hỗ trợ SOCKS ở tầng proxy configuration. ([Docs.rs][2])

---

# 5. HTTP Proxy và HTTPS URL

Đây là chỗ rất dễ nhầm.

Có hai thứ:

```text
A. Protocol của proxy
B. Protocol của website
```

Ví dụ:

```text
Website:
https://example.com

Proxy:
http://127.0.0.1:8080
```

Hoàn toàn có thể tồn tại:

```text
Python
  │
  │ HTTPS request
  ▼
HTTP Proxy
  │
  ▼
https://example.com
```

Đừng nghĩ:

```text
HTTPS website
    ↓
bắt buộc
    ↓
HTTPS proxy
```

Không phải vậy.

---

# 6. Proxy cơ bản

Với phiên bản Python binding cụ thể của `primp`, bạn nên kiểm tra API:

```python
import primp

print(primp)
```

và:

```python
help(primp.Client)
```

Nếu bản bạn đang dùng expose proxy trực tiếp trên `Client`, cấu hình sẽ có dạng tương tự:

```python
import primp


client = primp.Client(
    proxy="http://127.0.0.1:8080"
)
```

Tuy nhiên, **đừng copy mù dòng này nếu phiên bản Python `primp` của bạn không nhận `proxy=`**. API Rust hiện tại dùng `Proxy` objects trên `ClientBuilder`, trong khi Python binding có thể expose abstraction khác. Tài liệu chính thức hiện tại xác nhận proxy là một cấu hình của client. ([Docs.rs][2])

---

# 7. Cách kiểm tra IP

Một endpoint rất tiện để test proxy là:

```text
https://httpbin.org/ip
```

Không proxy:

```python
import primp


def main():
    client = primp.Client()

    response = client.get(
        "https://httpbin.org/ip"
    )

    print(response.text)


if __name__ == "__main__":
    main()
```

Kết quả kiểu:

```json
{
  "origin": "xxx.xxx.xxx.xxx"
}
```

---

# 8. Khi có proxy

Mục tiêu test:

```text
Direct request
      ↓
IP A

Proxy request
      ↓
IP B
```

Nếu IP vẫn giống nhau thì có thể:

* proxy không được sử dụng;
* proxy không hoạt động;
* proxy server đang NAT theo cách khác;
* endpoint/test environment không phản ánh như bạn mong đợi.

Vì vậy **đừng chỉ nhìn HTTP 200 để kết luận proxy hoạt động**.

---

# 9. Proxy Authentication

Một proxy có thể yêu cầu:

```text
username
password
```

Ví dụ:

```text
proxy.example.com:8080
username = alice
password = secret
```

Một cách biểu diễn:

```text
http://alice:secret@proxy.example.com:8080
```

Ở tầng HTTP proxy, credential có thể được gửi bằng:

```http
Proxy-Authorization: Basic ...
```

Tài liệu `primp` hiện tại có API `basic_auth(username, password)` trên proxy configuration để thiết lập `Proxy-Authorization`. ([Docs.rs][2])

---

# 10. Proxy Auth khác Website Auth

Đây là điểm rất quan trọng.

Website authentication:

```http
Authorization: Bearer TOKEN
```

Proxy authentication:

```http
Proxy-Authorization: Basic ...
```

Hai credential này phục vụ hai đối tượng khác nhau:

```text
                    Request
                       │
             ┌─────────┴─────────┐
             │                   │
         Proxy Auth          Website Auth
             │                   │
      Proxy-Authorization   Authorization
```

Không được nhầm:

```text
Authorization
```

với:

```text
Proxy-Authorization
```

---

# 11. Proxy + Timeout

Proxy tạo thêm một tầng network:

```text
Python
  │
  ▼
Proxy
  │
  ▼
Website
```

Do đó timeout càng quan trọng.

Ví dụ:

```python
response = client.get(
    "https://httpbin.org/get",
    timeout=10,
)
```

Flow:

```text
Request
   │
   ▼
Connect Proxy
   │
   ▼
Connect Website
   │
   ▼
Receive Response
```

Nếu proxy chết:

```text
Request
   │
   ▼
Proxy
   X
Timeout / Connection Exception
```

Đây là lý do sau này `ProxyPool` phải có:

```text
Proxy
 ├── URL
 ├── health
 ├── failure count
 ├── latency
 └── cooldown
```

---

# 12. Proxy + Exception

Liên hệ Buổi 12:

```text
Proxy
   │
   ├── hoạt động
   │      └── Response
   │
   └── chết
          └── Exception
```

Ví dụ:

```python
import primp


client = primp.Client(
    proxy="http://127.0.0.1:59999"
)

try:
    response = client.get(
        "https://httpbin.org/ip",
        timeout=5,
    )

    print(response.status_code)

except Exception as exc:
    print("Proxy request failed")
    print("Type:", type(exc).__name__)
    print("Message:", exc)
```

Nếu port không có proxy server:

```text
127.0.0.1:59999
       ↓
Connection failure
       ↓
Exception
```

---

# 13. Proxy không nên nằm trong Parser

Kiến trúc vẫn giữ nguyên:

```text
Application
      │
      ▼
Fetcher Interface
      │
      ▼
PrimpFetcher
      │
      ├── Timeout
      ├── Authentication
      ├── Proxy
      └── Headers
             │
             ▼
           primp
```

Parser:

```text
Response
   │
   ▼
Parser
```

không cần biết request dùng proxy nào.

---

# 14. Thiết kế `ProxyConfig`

Đây là abstraction đầu tiên mình muốn bạn làm quen:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ProxyConfig:
    url: str
    username: str | None = None
    password: str | None = None
```

Ví dụ:

```python
proxy = ProxyConfig(
    url="http://proxy.example.com:8080",
    username="alice",
    password="secret",
)
```

Nhưng **không nên lập tức nhét logic HTTP vào dataclass**.

Nó chỉ là configuration:

```text
ProxyConfig
     │
     ▼
PrimpFetcher
     │
     ▼
primp
```

---

# 15. Proxy URL Builder

Nếu proxy có username/password, chúng ta cần cẩn thận với URL encoding.

Ví dụ password:

```text
p@ss:word
```

không thể tùy tiện nối:

```text
http://alice:p@ss:word@host:8080
```

Đây là lý do `yarl` mà bạn đã học rất hữu ích.

Ví dụ:

```python
from yarl import URL


url = URL("http://proxy.example.com:8080")

url = url.with_user("alice")
url = url.with_password("secret")

print(url)
```

Ý tưởng kiến trúc:

```text
ProxyConfig
     │
     ▼
Proxy URL Builder
     │
     ▼
yarl.URL
     │
     ▼
primp
```

`yarl` xử lý URL.

`primp` xử lý HTTP.

Đúng với nguyên tắc chúng ta đã dùng khi học `yarl`.

---

# 16. Không log password

Đây là lỗi rất nguy hiểm:

```python
print(proxy.url)
```

nếu URL chứa:

```text
username:password@
```

Bạn có thể vô tình log:

```text
http://alice:secret@proxy.example.com:8080
```

Trong crawler production:

```text
❌ Log credential
❌ Log API key
❌ Log Bearer token
❌ Log proxy password
```

Nên sanitize:

```text
http://alice:***@proxy.example.com:8080
```

---

# 17. Proxy Pool

Bây giờ bắt đầu thấy lý do roadmap của bạn có:

```text
36. Proxy Pool
```

Một proxy:

```text
Proxy A
```

không nên được coi là luôn sống.

Ta có:

```text
ProxyPool
   │
   ├── Proxy A
   ├── Proxy B
   ├── Proxy C
   └── Proxy D
```

Khi request:

```text
Request
   │
   ▼
ProxyPool
   │
   ▼
Select Proxy
   │
   ▼
Fetcher
```

---

# 18. Nhưng Buổi 14 chưa xây ProxyPool

Chúng ta chỉ xây nền:

```text
ProxyConfig
```

và:

```text
PrimpFetcher
```

Sau này mới:

```text
ProxyPool
   ↓
ProxyStrategy
   ↓
Health Check
   ↓
Retry
   ↓
Cooldown
```

Nếu làm tất cả ngay bây giờ, architecture sẽ nhảy quá nhanh.

---

# 19. `PrimpFetcher` với Proxy

Mức abstraction hiện tại:

```python
import primp


class PrimpFetcher:

    def __init__(
        self,
        timeout: float = 10,
        proxy: str | None = None,
    ):
        kwargs = {}

        if proxy is not None:
            kwargs["proxy"] = proxy

        self.client = primp.Client(**kwargs)

        self.default_timeout = timeout

    def get(
        self,
        url: str,
        *,
        timeout: float | None = None,
    ):
        if timeout is None:
            timeout = self.default_timeout

        return self.client.get(
            url,
            timeout=timeout,
        )
```

Sử dụng:

```python
fetcher = PrimpFetcher(
    timeout=10,
    proxy="http://127.0.0.1:8080",
)
```

**Nhưng một lần nữa:** tên tham số Python `proxy=` cần khớp với bản `primp` bạn đang cài. Nếu constructor báo `unexpected keyword argument 'proxy'`, đừng sửa kiến trúc; hãy kiểm tra API Python binding của version đó trước. Tài liệu Rust hiện tại xác nhận proxy được gắn vào `Client` configuration, nhưng không nên suy diễn tên keyword Python từ Rust API. ([Docs.rs][2])

---

# 20. Một thiết kế tốt hơn cho project

Thay vì:

```python
PrimpFetcher(
    proxy="..."
)
```

ta có thể tiến tới:

```python
@dataclass(frozen=True)
class FetcherConfig:
    timeout: float = 10
    proxy: str | None = None
```

rồi:

```text
FetcherConfig
      │
      ├── timeout
      ├── proxy
      ├── headers
      └── ...
             │
             ▼
        PrimpFetcher
```

Nhưng hiện tại **chưa cần gom hết configuration**.

Chúng ta sẽ làm việc đó dần dần qua:

```text
16 Session
17 Default Headers
18 Default Params
19 Request Options
20 Client Lifecycle
```

---

# 21. Proxy trong kiến trúc cuối cùng

Sau khi hoàn thành phần HTTP Client, kiến trúc sẽ tiến tới:

```text
                    Novel Crawler
                         │
                         ▼
                    Application
                         │
                         ▼
                  Fetcher Interface
                         │
                         ▼
                   PrimpFetcher
                         │
          ┌──────────────┼──────────────┐
          │              │              │
       Timeout          Auth          Proxy
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                    Primp Client
                         │
                         ▼
                      Internet
```

Sau này:

```text
Proxy
  │
  ▼
ProxyPool
  │
  ├── Selection Strategy
  ├── Health Check
  ├── Failure Count
  ├── Cooldown
  └── Rotation
```

---

# 22. Proxy + Browser Impersonation

Một request hoàn chỉnh trong crawler tương lai có thể là:

```text
Request
   │
   ├── URL
   ├── Headers
   ├── Timeout
   ├── Authentication
   ├── Proxy
   └── Browser Profile
              │
              ▼
          Primp Client
```

Ví dụ:

```text
Chrome profile
      +
Proxy A
      +
User-Agent
      +
Cookies
      +
Timeout
```

Nhưng **proxy và browser impersonation là hai vấn đề khác nhau**:

```text
Proxy
→ đường đi của network traffic

Impersonation
→ đặc điểm HTTP/TLS/browser profile
```

Không nên coi proxy là một phần của browser fingerprint.

---

# 23. Bài tập Buổi 14

### Bài 1 — Direct

Gọi:

```text
https://httpbin.org/ip
```

không proxy.

---

### Bài 2 — Proxy

Dùng một proxy hợp lệ của bạn:

```python
proxy = "http://HOST:PORT"
```

và gọi:

```text
https://httpbin.org/ip
```

So sánh IP.

---

### Bài 3 — Proxy chết

Dùng:

```text
127.0.0.1:59999
```

và:

```python
timeout=5
```

Quan sát:

```python
type(exc).__name__
```

---

### Bài 4 — Proxy Authentication

Nếu bạn có authenticated proxy:

```text
username
password
host
port
```

hãy test:

```text
proxy
  ↓
httpbin.org/ip
```

---

### Bài 5 — Architecture

Thiết kế:

```python
@dataclass(frozen=True)
class ProxyConfig:
    ...
```

với:

```text
url
username
password
```

nhưng **không để `ProxyConfig` thực hiện HTTP request**.

---

# 24. Điều cần nhớ sau Buổi 14

Ba thứ phải phân biệt rõ:

```text
┌─────────────────────┬────────────────────────────┐
│ Thành phần          │ Vai trò                    │
├─────────────────────┼────────────────────────────┤
│ Authentication      │ Xác thực với website       │
│ Proxy               │ Trung gian network         │
│ Browser Impersonate │ Mô phỏng client/browser    │
└─────────────────────┴────────────────────────────┘
```

Và flow:

```text
                  Request
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
    Timeout        Auth         Proxy
        │            │            │
        └────────────┼────────────┘
                     ▼
                primp.Client
                     │
                     ▼
                  Website
```

**Buổi 15 — SSL / Verify** sẽ nối trực tiếp với Proxy: TLS handshake, certificate verification, `verify`, vì sao **không nên tắt certificate verification một cách tùy tiện**, và cách xử lý SSL trong `PrimpFetcher`.

[1]: https://docs.rs/crate/primp/latest?utm_source=chatgpt.com "primp 2.0.1 - Docs.rs"
[2]: https://docs.rs/primp/latest/primp/struct.Proxy.html?utm_source=chatgpt.com "Proxy in primp - Rust"
