# Buổi 15 — SSL / Verify với `primp`

Ở Buổi 14 chúng ta đã thêm Proxy. Hôm nay đi vào một phần rất quan trọng của HTTPS:

```text
HTTPS
  ↓
TLS
  ↓
Certificate
  ↓
Certificate Verification
```

Đặc biệt, bạn cần phân biệt:

```text
SSL/TLS encryption
        ≠
Certificate verification
```

Trong Python/client hiện đại, certificate verification mặc định được dùng để xác thực certificate và hostname của server; Python `ssl.create_default_context()` chẳng hạn cấu hình client mode với `CERT_REQUIRED` và kiểm tra hostname. ([GitHub][1])

Với `primp`, API hiện tại có các tùy chọn liên quan đến `verify` và CA certificate; một issue thực tế cũng cho thấy `primp.Client(verify=True, ca_cert_file=...)` được dùng khi môi trường có CA nội bộ. ([GitHub][2])

---

# 1. HTTPS thực sự làm gì?

Khi gọi:

```python
response = client.get(
    "https://example.com"
)
```

không đơn giản chỉ là:

```text
HTTP
 ↓
Server
```

Mà gần đúng là:

```text
Python
   │
   ▼
TCP connection
   │
   ▼
TLS handshake
   │
   ├── Server certificate
   ├── Certificate verification
   ├── Key negotiation
   └── Secure channel
   │
   ▼
HTTP request
   │
   ▼
Server
```

---

# 2. Certificate là gì?

Website HTTPS có certificate.

Ví dụ:

```text
example.com
     │
     ▼
TLS Certificate
     │
     ├── Subject
     ├── Issuer
     ├── Validity
     ├── Public Key
     └── SAN
```

Client dùng certificate để kiểm tra rằng server thực sự phù hợp với hostname đang truy cập.

Ví dụ:

```text
Request:
https://example.com
```

nhưng certificate lại dành cho:

```text
evil-example.com
```

thì verification phải thất bại.

---

# 3. Certificate Authority — CA

Certificate thường được ký bởi một CA đáng tin cậy.

Mô hình:

```text
Root CA
   │
   ▼
Intermediate CA
   │
   ▼
example.com certificate
```

Client có một trust store chứa các CA được tin cậy.

```text
Client
  │
  ├── Trusted CA 1
  ├── Trusted CA 2
  ├── Trusted CA 3
  └── ...
```

Khi server gửi certificate:

```text
Server
  │
  ▼
Certificate
  │
  ▼
Client kiểm tra chain
  │
  ├── Trusted → OK
  └── Unknown → Error
```

---

# 4. Verify nghĩa là gì?

Khi nói:

```text
verify=True
```

ý tưởng là:

> Client không chỉ mã hóa kết nối TLS mà còn kiểm tra certificate của server.

Ví dụ Python SSL client mặc định sử dụng:

```python
CERT_REQUIRED
```

và:

```python
check_hostname = True
```

trong `create_default_context()` cho server authentication. ([GitHub][1])

---

# 5. Test HTTPS bình thường

```python
import primp


def main():
    client = primp.Client()

    response = client.get(
        "https://httpbin.org/get"
    )

    print("Status:", response.status_code)
    print("URL:", response.url)


if __name__ == "__main__":
    main()
```

Thông thường:

```text
TLS handshake
     ↓
Certificate verified
     ↓
HTTP request
     ↓
200
```

---

# 6. Certificate verification failure

Để học, ta có thể dùng một endpoint test SSL không hợp lệ:

```text
https://expired.badssl.com/
```

Ví dụ:

```python
import primp


def main():
    client = primp.Client()

    try:
        response = client.get(
            "https://expired.badssl.com/",
            timeout=10,
        )

        print(response.status_code)

    except Exception as exc:
        print("Request failed")
        print("Type:", type(exc).__name__)
        print("Message:", exc)


if __name__ == "__main__":
    main()
```

Mục tiêu của bài test không phải là nhớ chính xác tên exception, mà hiểu flow:

```text
HTTPS
  ↓
TLS handshake
  ↓
Certificate invalid
  ↓
Verification failure
  ↓
Exception
```

Một lỗi certificate verification thực tế thường xuất hiện dưới dạng `CERTIFICATE_VERIFY_FAILED`; ví dụ một issue liên quan đến `primp` ghi nhận lỗi do không tìm thấy local issuer certificate. ([GitHub][2])

---

# 7. `verify=False` là gì?

Về khái niệm:

```python
client = primp.Client(
    verify=False
)
```

có nghĩa là client **không thực hiện certificate verification theo cách thông thường**.

Điều này khác hoàn toàn với:

```text
HTTPS
```

và:

```text
Certificate verification
```

Bạn có thể hình dung:

```text
verify=True

HTTPS
 │
 ├── Encryption
 │
 └── Certificate verification
```

Trong khi:

```text
verify=False

HTTPS
 │
 └── Encryption
      nhưng bỏ qua kiểm tra certificate
```

---

# 8. Tại sao `verify=False` nguy hiểm?

Giả sử:

```text
Crawler
   │
   ▼
HTTPS
   │
   ▼
Attacker
   │
   ▼
Fake server
```

Nếu client không xác minh certificate, việc mã hóa không còn đảm bảo rằng bạn đang nói chuyện với **đúng server**.

Nói đơn giản:

```text
Encryption
≠
Authentication of server
```

Certificate verification giúp chống việc client chấp nhận một server không đáng tin cậy.

---

# 9. Không dùng `verify=False` như cách sửa lỗi

Một lỗi rất phổ biến:

```text
SSL Error
    ↓
verify=False
    ↓
Works!
```

Nhưng đây thường chỉ là **che giấu nguyên nhân**.

Ví dụ certificate verification thất bại vì:

```text
CA store cũ
        ↓
Certificate chain không được tin
```

Giải pháp tốt hơn có thể là:

```text
Update CA
```

hoặc:

```text
Cấu hình CA certificate đúng
```

GitHub cũng mô tả một trường hợp SSL certificate problem có thể xuất phát từ CA root certificate đã lỗi thời. ([GitHub Docs][3])

---

# 10. CA certificate riêng

Trường hợp rất thực tế:

```text
Doanh nghiệp
    │
    ▼
Corporate Proxy
    │
    ▼
Internal CA
```

Máy tính có CA nội bộ:

```text
company-root-ca.pem
```

Client phải tin CA đó.

Một cách cấu hình được `primp` hỗ trợ là truyền CA certificate file cùng với verification. Một issue thực tế dùng:

```python
primp.Client(
    verify=True,
    ca_cert_file="/path/to/cert.pem",
)
```

để giải quyết local issuer certificate trong môi trường Zscaler. ([GitHub][2])

Ví dụ:

```python
import primp


client = primp.Client(
    verify=True,
    ca_cert_file="/path/to/company-ca.pem",
)

response = client.get(
    "https://internal.example.com"
)

print(response.status_code)
```

Điểm quan trọng:

```text
verify=True
+
CA phù hợp
```

thay vì:

```text
verify=False
```

---

# 11. Trust Store

Thông thường client không cần bạn chỉ định từng CA.

Nó sử dụng trust store của hệ thống/runtime.

Mô hình:

```text
Operating System
      │
      ▼
Trusted CA Store
      │
      ▼
HTTP Client
      │
      ▼
HTTPS Server
```

Nếu máy bạn có CA phù hợp:

```text
Certificate
    ↓
Trusted
    ↓
HTTPS OK
```

Nếu không:

```text
Certificate
    ↓
Unknown issuer
    ↓
Verification error
```

---

# 12. `verify=True` không có nghĩa certificate luôn hợp lệ

Đây là điểm cần hiểu chính xác.

```text
verify=True
```

không có nghĩa:

> "Hãy cho phép HTTPS."

Nó có nghĩa gần hơn:

> "Hãy xác minh certificate theo trust configuration."

Certificate có thể thất bại vì:

```text
Expired
Wrong hostname
Unknown issuer
Invalid chain
Not trusted
```

Khi đó request có thể thất bại.

---

# 13. Hostname verification

Ví dụ:

```text
Request:
https://example.com
```

Server certificate phải phù hợp với hostname.

Nếu certificate:

```text
CN/SAN = another-domain.com
```

thì:

```text
example.com
     ↓
certificate mismatch
     ↓
verification failure
```

Đây là lý do certificate không chỉ là:

```text
"Certificate tồn tại"
```

mà phải:

```text
Certificate
   +
Trusted chain
   +
Hostname match
   +
Validity
```

---

# 14. SSL Error thuộc tầng nào?

Liên hệ Buổi 12:

```text
HTTP
 │
 ├── 200 → Response
 ├── 404 → Response
 └── 500 → Response
```

Còn TLS:

```text
TLS
 │
 ├── Handshake OK
 │      ↓
 │    HTTP
 │
 └── Handshake failed
        ↓
     Exception
```

Do đó:

```text
SSL verification error
```

không phải:

```text
HTTP 495
```

một cách mặc định.

Nó xảy ra trước khi HTTP request hoàn thành.

---

# 15. SSL + Proxy

Đây là phần rất quan trọng vì bạn vừa học Proxy.

Không proxy:

```text
Crawler
   │
   ▼
TLS
   │
   ▼
Website
```

Có proxy:

```text
Crawler
   │
   ▼
Proxy
   │
   ▼
TLS
   │
   ▼
Website
```

Với HTTPS proxy, còn có khái niệm `CONNECT` tunnel:

```text
Crawler
   │
   │ CONNECT example.com:443
   ▼
Proxy
   │
   │ tunnel
   ▼
example.com:443
   │
   ▼
TLS handshake
```

Vì vậy:

```text
Proxy configuration
```

và:

```text
TLS verification
```

là hai concern khác nhau.

---

# 16. Corporate MITM Proxy

Đây là một case rất thực tế.

Một số corporate security proxy có thể thực hiện TLS interception:

```text
Crawler
   │
   ▼
Corporate Proxy
   │
   ├── TLS connection 1
   │
   ├── Inspect
   │
   └── TLS connection 2
   │
   ▼
Website
```

Khi đó proxy có thể dùng certificate được ký bởi:

```text
Corporate Root CA
```

Nếu client không trust CA này:

```text
TLS
 ↓
Certificate
 ↓
Unknown corporate CA
 ↓
CERTIFICATE_VERIFY_FAILED
```

Giải pháp đúng trong môi trường được quản trị thường là cài/trust CA phù hợp, không phải tắt verification. Trường hợp Zscaler được báo cáo với `primp` cũng minh họa đúng vấn đề này. ([GitHub][2])

---

# 17. `PrimpFetcher` với SSL configuration

Bây giờ mở rộng Fetcher của chúng ta.

```python
import primp


class PrimpFetcher:

    def __init__(
        self,
        timeout: float = 10,
        proxy: str | None = None,
        verify: bool = True,
        ca_cert_file: str | None = None,
    ):
        kwargs = {
            "verify": verify,
        }

        if proxy is not None:
            kwargs["proxy"] = proxy

        if ca_cert_file is not None:
            kwargs["ca_cert_file"] = ca_cert_file

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

Ở đây ta có:

```text
PrimpFetcher
   │
   ├── timeout
   ├── proxy
   ├── verify
   └── ca_cert_file
```

---

# 18. Nhưng đừng biến Fetcher thành "God Object"

Nếu tiếp tục:

```python
PrimpFetcher(
    timeout=10,
    proxy=...,
    verify=True,
    ca_cert_file=...,
    headers=...,
    params=...,
    cookies=...,
    auth=...,
    ...
)
```

constructor sẽ ngày càng dài.

Đó chính là lý do roadmap của chúng ta chia nhỏ:

```text
11 Timeout
12 Exception
13 Authentication
14 Proxy
15 SSL / Verify
16 Session / Connection Reuse
17 Default Headers
18 Default Params
19 Request Options
20 Client Lifecycle
```

Sau khi học hết phần II, ta mới có đủ kiến thức để thiết kế configuration sạch hơn.

---

# 19. Tách `TLSConfig`

Ở mức architecture, có thể bắt đầu:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class TLSConfig:
    verify: bool = True
    ca_cert_file: str | None = None
```

Ví dụ:

```python
tls = TLSConfig(
    verify=True,
    ca_cert_file="/path/to/company-ca.pem",
)
```

Sau đó:

```text
TLSConfig
    │
    ▼
PrimpFetcher
    │
    ▼
primp.Client
```

Nhưng nhớ:

> `TLSConfig` chỉ chứa configuration. Nó không thực hiện request.

---

# 20. Vì sao `verify=True` nên là default?

Cho crawler production:

```python
verify=True
```

nên là lựa chọn mặc định.

Tức:

```text
Default
   ↓
Secure verification
```

Nếu có môi trường đặc biệt:

```text
Self-signed
Corporate CA
Testing
Internal service
```

thì cấu hình riêng.

Không nên:

```python
verify=False
```

ngay từ đầu vì:

```text
"SSL hay lỗi"
```

không phải lý do đủ tốt để vô hiệu hóa certificate verification.

---

# 21. Test SSL

Tạo:

```text
lesson_15.py
```

### Test 1 — HTTPS bình thường

```python
import primp


client = primp.Client(
    verify=True,
)

response = client.get(
    "https://httpbin.org/get"
)

print(response.status_code)
```

Kỳ vọng:

```text
200
```

---

### Test 2 — Certificate invalid

```python
import primp


client = primp.Client(
    verify=True,
)

try:
    response = client.get(
        "https://expired.badssl.com/",
        timeout=10,
    )

    print(response.status_code)

except Exception as exc:
    print("Type:", type(exc).__name__)
    print("Message:", exc)
```

Mục tiêu:

```text
TLS certificate
      ↓
verification failure
      ↓
Exception
```

---

# 22. Test `verify=False`

Chỉ dùng để **học/testing**, không phải cấu hình production:

```python
import primp


client = primp.Client(
    verify=False,
)

try:
    response = client.get(
        "https://expired.badssl.com/",
        timeout=10,
    )

    print("Status:", response.status_code)

except Exception as exc:
    print("Type:", type(exc).__name__)
    print("Message:", exc)
```

Nếu phiên bản `primp` của bạn hỗ trợ `verify=False` trên path đang sử dụng, bạn sẽ thấy sự khác biệt.

Một điểm cần đặc biệt lưu ý: có báo cáo thực nghiệm cho `primp 1.3.x` rằng `verify=False` có thể không có hiệu lực khi một impersonation profile đang active, vì client TLS được dựng lại theo profile. Đây là chi tiết **version/profile-specific**, không nên tổng quát hóa cho mọi phiên bản `primp`. ([GitHub][4])

---

# 23. Điều này rất quan trọng cho phần Browser Impersonation

Roadmap của bạn sau này có:

```text
21. Vì sao cần impersonation
22. Chrome fingerprint
23. Firefox / Safari / Edge
24. impersonate_os
25. TLS fingerprint
26. HTTP/2
```

Như vậy SSL/TLS không chỉ liên quan đến:

```text
certificate
```

mà còn:

```text
TLS fingerprint
```

Hai khái niệm khác nhau:

```text
Certificate Verification
        │
        └── Server có đáng tin?

TLS Fingerprint
        │
        └── Client TLS handshake trông như thế nào?
```

Đừng gộp chúng.

---

# 24. Security Model

Sau Buổi 15, hãy ghi nhớ mô hình:

```text
                    HTTPS
                      │
             ┌────────┴────────┐
             │                 │
          Encryption       Authentication
             │                 │
          TLS data        Certificate
                               │
                         Verification
                               │
                    ┌──────────┴──────────┐
                    │                     │
               Trusted CA            Hostname
```

---

# 25. Tích hợp với Novel Crawler

Fetcher của chúng ta hiện tại đã có:

```text
PrimpFetcher
│
├── Timeout
├── Exception
├── Authentication
├── Proxy
└── SSL / Verify
```

Flow:

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
    ├── Auth
    ├── Proxy
    └── TLS verification
           │
           ▼
       primp.Client
           │
           ▼
        Internet
```

Parser hoàn toàn không cần biết:

```text
proxy nào
CA nào
TLS verify ra sao
authentication kiểu gì
```

Parser chỉ nhận:

```text
Response
```

---

# 26. Bài tập Buổi 15

### Bài 1

Gọi:

```text
https://httpbin.org/get
```

với:

```python
verify=True
```

---

### Bài 2

Gọi:

```text
https://expired.badssl.com/
```

với:

```python
verify=True
```

và in:

```python
type(exc).__name__
str(exc)
```

---

### Bài 3

Thử:

```python
verify=False
```

chỉ trong môi trường test và quan sát sự khác biệt.

---

### Bài 4 — Architecture

Tạo:

```python
@dataclass(frozen=True)
class TLSConfig:
    verify: bool = True
    ca_cert_file: str | None = None
```

Sau đó thiết kế:

```text
TLSConfig
    ↓
PrimpFetcher
    ↓
primp.Client
```

---

# 27. Tổng kết 11 → 15

Đến đây phần HTTP Client đã có một nền khá rõ:

```text
11 Timeout
      │
      ▼
12 Exception
      │
      ▼
13 Authentication
      │
      ▼
14 Proxy
      │
      ▼
15 SSL / Verify
```

Có thể nhìn thành:

```text
                     PrimpFetcher
                          │
       ┌──────────────────┼──────────────────┐
       │                  │                  │
    Timeout          Authentication       Proxy
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                    SSL / Verify
                          │
                          ▼
                     primp.Client
                          │
                          ▼
                       Server
```

**Buổi 16 — Session / Connection Reuse** sẽ rất quan trọng: vì sao không nên tạo `primp.Client()` cho từng request, connection reuse/keep-alive là gì, client state gồm những gì, và cách tổ chức một `PrimpFetcher` dùng **một client lâu dài** cho crawler.

[1]: https://github.com/python/cpython/blob/main/Lib/ssl.py?utm_source=chatgpt.com "cpython/Lib/ssl.py at main · python/cpython · GitHub"
[2]: https://github.com/deedy5/ddgs/issues/301?utm_source=chatgpt.com "SSL certificate handling bug · Issue #301 · deedy5/ddgs · GitHub"
[3]: https://docs.github.com/en/authentication/troubleshooting-ssh/error-ssl-certificate-problem-verify-that-the-ca-cert-is-ok?utm_source=chatgpt.com "Error: SSL certificate problem, verify that the CA cert is OK - GitHub Docs"
[4]: https://github.com/zinzied/TLS-Chameleon/blob/main/docs/NATIVE_BACKEND_RESEARCH.md?utm_source=chatgpt.com "TLS-Chameleon/docs/NATIVE_BACKEND_RESEARCH.md at main · zinzied/TLS-Chameleon · GitHub"
