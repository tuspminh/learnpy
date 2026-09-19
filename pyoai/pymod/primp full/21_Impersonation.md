# Phần III — Browser Impersonation

# Buổi 21 — Vì sao cần Impersonation?

Từ Buổi 21, chúng ta bước sang một phần **quan trọng nhất của `primp`**.

Ở Phần II, ta học:

```text
HTTP Client
├── GET / POST
├── Headers
├── Cookies
├── Proxy
├── SSL
├── Timeout
├── Connection
└── Client Lifecycle
```

Bây giờ câu hỏi thay đổi:

> **Nếu server không chỉ nhìn HTTP request mà còn nhìn "dấu vết" của client thì sao?**

Đó là lý do cần **Browser Impersonation**.

`primp` hiện mô tả impersonation là khả năng mô phỏng browser ở các lớp như **TLS, HTTP/2 và default headers**, chứ không đơn thuần đổi `User-Agent`. ([Docs.rs][1])

---

# 1. HTTP Client thông thường là gì?

Giả sử:

```python
import primp

client = primp.Client()

response = client.get(
    "https://example.com"
)
```

Website nhận được một request.

Ở mức đơn giản:

```text
Python
  │
  ▼
primp.Client
  │
  ▼
HTTP Request
  │
  ▼
Server
```

Ta có thể thay đổi:

```python
headers={
    "User-Agent": "...",
    "Accept": "...",
}
```

Nhưng:

> **Header chỉ là một phần của danh tính HTTP client.**

Đây là điểm mấu chốt của Buổi 21.

---

# 2. Tại sao đổi User-Agent chưa đủ?

Giả sử bạn gửi:

```python
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/146.0.0.0 Safari/537.36"
    )
}
```

Bạn đang nói với server:

```text
"Tôi là Chrome."
```

Nhưng bên dưới HTTP header còn có:

```text
TLS
HTTP/2
Connection behavior
Header characteristics
```

Có thể hình dung:

```text
                 Request
                    │
       ┌────────────┼─────────────┐
       │            │             │
    Headers        TLS          HTTP/2
       │            │             │
   User-Agent    Handshake      Settings
   Accept        Extensions     Frames
   Sec-*         Cipher suites  Ordering
```

Nếu chỉ sửa:

```text
User-Agent = Chrome
```

nhưng các tầng khác vẫn có đặc điểm của một HTTP library, thì server có thể nhận thấy sự không nhất quán.

Các dự án browser impersonation tồn tại chính vì TLS handshake và HTTP/2 handshake của HTTP client thông thường có thể khác browser thật. ([GitHub][2])

---

# 3. Browser Fingerprint là gì?

Ta chưa đi sâu vào fingerprint ở Buổi 22.

Hiện tại chỉ cần hiểu:

> **Fingerprint là tập hợp các đặc điểm mà server có thể quan sát để phân biệt loại client.**

Ví dụ:

```text
Browser Fingerprint
│
├── User-Agent
├── HTTP headers
├── TLS fingerprint
├── HTTP/2 behavior
├── Header ordering
├── HTTP/2 settings
└── Một số đặc điểm protocol khác
```

Không phải tất cả đều là "fingerprint" theo nghĩa chính xác ở mọi hệ thống, nhưng về mặt học tập ta có thể xem đây là **client identity surface**.

---

# 4. TLS fingerprint là gì?

Khi HTTPS được thiết lập:

```text
Client
   │
   │ ClientHello
   ▼
Server
```

Client gửi thông tin trong TLS handshake.

Một browser thật có cách cấu hình TLS nhất định.

Ví dụ:

```text
Chrome
   ↓
TLS ClientHello
   ↓
Server
```

Một HTTP library:

```text
Python HTTP Client
   ↓
TLS ClientHello
   ↓
Server
```

Hai ClientHello có thể khác nhau.

Server có thể quan sát các đặc điểm đó.

Đây là nền tảng của **TLS fingerprinting**.

Chúng ta sẽ học kỹ ở:

```text
25. TLS fingerprint
```

---

# 5. HTTP/2 fingerprint cũng tồn tại

Nếu connection sử dụng HTTP/2:

```text
Client
   ↓
HTTP/2
   ↓
Server
```

HTTP/2 có những đặc điểm như:

```text
SETTINGS
WINDOW_UPDATE
Pseudo-header ordering
Priority-related behavior
...
```

Browser có cấu hình/behavior riêng.

`primp` hiện tài liệu hóa browser impersonation với **TLS + HTTP/2 + default headers**; cấu hình impersonation còn có dữ liệu HTTP/2 riêng. ([Docs.rs][1])

Ta sẽ học HTTP/2 fingerprint ở:

```text
26. HTTP/2
```

---

# 6. Vì vậy Browser Impersonation làm gì?

Thay vì:

```text
Python HTTP Client
       ↓
      Server
```

ta muốn:

```text
Python
  │
  ▼
primp
  │
  ├── Browser-like headers
  ├── Browser-like TLS
  └── Browser-like HTTP/2
  │
  ▼
Server
```

Nói đơn giản:

> **Không chỉ nói "tôi là Chrome", mà cố gắng làm cho các đặc điểm giao tiếp tương ứng với một profile Chrome.**

Đó là lý do gọi là:

```text
Browser Impersonation
```

chứ không phải:

```text
User-Agent Spoofing
```

---

# 7. `primp` hỗ trợ Browser Profiles

Phiên bản hiện tại của `primp` liệt kê nhiều profile:

```text
Chrome
Safari
Edge
Firefox
Opera
```

và nhiều phiên bản cụ thể, ví dụ Chrome 144–153 trong tài liệu hiện tại. ([Docs.rs][3])

Ví dụ khái niệm:

```python
client = primp.Client(
    impersonate="chrome_146"
)
```

Ở đây:

```text
chrome_146
```

không nên hiểu đơn giản là:

```text
User-Agent = Chrome 146
```

Mà là một **browser impersonation profile**.

---

# 8. So sánh hai cách

## Cách 1 — Chỉ đổi User-Agent

```python
import primp

client = primp.Client()

response = client.get(
    "https://example.com",
    headers={
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/146.0.0.0 "
            "Safari/537.36"
        )
    },
)
```

Mô hình:

```text
User-Agent
    │
    ▼
"Chrome"
```

Nhưng:

```text
TLS       → vẫn client library
HTTP/2    → vẫn client library
Headers   → có thể không đồng bộ
```

---

# 9. Cách 2 — Browser Impersonation

Ví dụ:

```python
import primp

client = primp.Client(
    impersonate="chrome_146"
)

response = client.get(
    "https://example.com"
)
```

Mô hình:

```text
                 chrome_146
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
     Headers        TLS         HTTP/2
        │            │            │
        └────────────┼────────────┘
                     ▼
                   Server
```

Đây là khác biệt cốt lõi.

---

# 10. Impersonation không phải Browser Automation

Cực kỳ quan trọng.

`primp`:

```text
HTTP Client
```

Không phải:

```text
Playwright
Selenium
Chrome Browser
```

Ví dụ:

```text
primp
   ↓
HTTP request
   ↓
Server
```

Trong khi browser automation:

```text
Python
  ↓
Playwright
  ↓
Chromium
  ↓
JavaScript
  ↓
DOM
  ↓
Network
```

So sánh:

|                     | `primp` impersonation | Browser automation |
| ------------------- | --------------------- | ------------------ |
| Chạy browser thật   | ❌                     | ✅                  |
| JavaScript runtime  | ❌                     | ✅                  |
| DOM                 | ❌                     | ✅                  |
| HTTP request        | ✅                     | ✅                  |
| Browser-like TLS    | ✅                     | Browser thật       |
| Browser-like HTTP/2 | ✅                     | Browser thật       |
| Chi phí             | thấp hơn              | cao hơn            |

Vì vậy:

> **Browser impersonation không biến `primp` thành Chrome.**

Nó làm HTTP client mô phỏng các đặc điểm giao tiếp của browser ở những lớp mà thư viện hỗ trợ.

---

# 11. Tại sao crawler cần điều này?

Đây là nơi liên quan trực tiếp đến **Novel Crawler** của bạn.

Crawler của chúng ta:

```text
Novel Crawler
      │
      ▼
Fetcher
      │
      ▼
HTTP Client
      │
      ▼
Novel Website
```

Một số website có thể có cơ chế phân biệt:

```text
Browser
vs
Generic HTTP Client
```

Ví dụ:

```text
Generic HTTP client
       ↓
Server
       ↓
Response A
```

trong khi:

```text
Browser-like client
       ↓
Server
       ↓
Response B
```

Response B có thể không phải "bypass" gì cả; đơn giản website có thể xử lý các loại client khác nhau.

---

# 12. Nhưng Impersonation không đảm bảo bypass

Đây là điểm cần nhớ.

Không được suy luận:

```text
impersonate="chrome"
       ↓
mọi anti-bot đều bypass
```

**Sai.**

Website có thể sử dụng nhiều lớp khác:

```text
IP reputation
      │
      ├── Rate limit
      ├── Cookies
      ├── JavaScript
      ├── CAPTCHA
      ├── TLS fingerprint
      ├── HTTP/2 fingerprint
      ├── Browser fingerprint
      └── Behavioral signals
```

Impersonation chỉ giải quyết **một phần client fingerprint/protocol characteristics**.

Do đó:

```text
Impersonation
    ≠
Anti-bot bypass guaranteed
```

---

# 13. Một ví dụ tư duy rất quan trọng

Giả sử bạn gửi:

```text
User-Agent:
Chrome/146
```

Server thấy:

```text
User-Agent → Chrome
TLS         → unusual
HTTP/2      → unusual
```

Có sự không nhất quán:

```text
             ┌── Chrome-looking
Headers ─────┤
             │
TLS ─────────┼── Non-Chrome-looking
             │
HTTP/2 ──────┘
```

Browser impersonation cố gắng làm:

```text
             ┌── Chrome
Headers ─────┤
             │
TLS ─────────┼── Chrome profile
             │
HTTP/2 ──────┘
```

Đây là **consistency**.

---

# 14. Từ "giả User-Agent" sang "giả Browser Profile"

Ta có ba cấp độ:

### Level 1

```text
User-Agent spoofing
```

Ví dụ:

```python
headers={
    "User-Agent": "Chrome..."
}
```

---

### Level 2

```text
Browser-like headers
```

Ví dụ:

```text
User-Agent
Sec-CH-UA
Sec-CH-UA-Mobile
Sec-CH-UA-Platform
Accept
Accept-Language
Sec-Fetch-*
...
```

---

### Level 3

```text
Browser impersonation
```

```text
Headers
   +
TLS
   +
HTTP/2
   +
Browser profile
```

`primp` hướng tới Level 3. Tài liệu chính thức mô tả các profile impersonation là cấu hình cho **TLS, HTTP/2 và default headers**. ([Docs.rs][1])

---

# 15. Test đầu tiên

Ta tạo:

```text
lesson_21.py
```

### Không impersonation

```python
import primp


def main():
    client = primp.Client()

    response = client.get(
        "https://tls.peet.ws/api/all"
    )

    print(response.text)


if __name__ == "__main__":
    main()
```

Endpoint này thường được dùng để quan sát các thuộc tính TLS/HTTP của request.

---

# 16. Test với Chrome impersonation

```python
import primp


def main():
    client = primp.Client(
        impersonate="chrome_146"
    )

    response = client.get(
        "https://tls.peet.ws/api/all"
    )

    print(response.text)


if __name__ == "__main__":
    main()
```

Sau đó so sánh:

```text
Normal Client
       │
       ▼
TLS / HTTP information


Chrome impersonation
       │
       ▼
TLS / HTTP information
```

Mục tiêu của bài này **không phải** là nhớ từng trường fingerprint.

Mục tiêu là:

> Nhìn thấy rằng `impersonate` có thể thay đổi **protocol-level characteristics**, chứ không chỉ `User-Agent`.

---

# 17. Kiểm tra phiên bản `primp`

Vì API và browser profiles thay đổi theo phiên bản, hãy kiểm tra package của bạn:

```bash
pip show primp
```

Hoặc:

```python
import importlib.metadata

print(
    importlib.metadata.version("primp")
)
```

Tại thời điểm hiện tại, tài liệu Rust của `primp` đang ở dòng 2.0.x và liệt kê các profile Chrome 144–153, trong đó có `chrome_146`. ([Docs.rs][3])

Điều này rất quan trọng vì các bài học cũ dùng profile như:

```python
chrome_131
```

có thể không còn phản ánh profile hiện tại.

---

# 18. Impersonation nằm ở đâu trong Architecture?

Đừng đưa:

```python
impersonate="chrome_146"
```

vào Domain.

Sai:

```text
Novel
 └── impersonate="chrome_146"  ❌
```

Cũng không nên để Parser biết:

```text
Parser
 └── Browser profile ❌
```

Đúng:

```text
Application
      │
      ▼
Fetcher Interface
      │
      ▼
PrimpFetcher
      │
      ▼
Browser Profile
      │
      ▼
primp.Client
```

---

# 19. Sau này chúng ta sẽ thiết kế BrowserProfile

Hiện tại **chưa cần code abstraction này**.

Nhưng hãy hình dung:

```python
BrowserProfile(
    browser="chrome",
    version=146,
    os="windows",
)
```

Sau đó:

```text
BrowserProfile
       ↓
PrimpFetcher
       ↓
primp.Client(
    impersonate=...
)
```

Tại Buổi 24 chúng ta sẽ bắt đầu đi sâu:

```text
impersonate_os
```

và sau đó:

```text
TLS fingerprint
HTTP/2
Headers + fingerprint
```

---

# 20. Bức tranh toàn bộ Phần III

Sau Buổi 21, hãy giữ mô hình này trong đầu:

```text
                    BROWSER IMPERSONATION
                              │
             ┌────────────────┼────────────────┐
             │                │                │
          Headers            TLS             HTTP/2
             │                │                │
             └────────────────┼────────────────┘
                              │
                       Browser Profile
                              │
                              ▼
                        primp.Client
                              │
                              ▼
                           Server
```

Các buổi tiếp theo sẽ lần lượt tháo từng lớp:

```text
21  Vì sao cần impersonation
 │
 └── Tại sao User-Agent chưa đủ?
          │
          ▼
22  Chrome fingerprint
          │
          ▼
23  Firefox / Safari / Edge
          │
          ▼
24  impersonate_os
          │
          ▼
25  TLS fingerprint
          │
          ▼
26  HTTP/2
          │
          ▼
27  Headers + fingerprint
          │
          ▼
28  Fingerprint thực tế
          │
          ▼
29  httpx vs primp
          │
          ▼
30  BrowserClient
```

## Bài tập Buổi 21

Chạy **hai request**:

```python
# 1. Normal
client = primp.Client()

# 2. Chrome impersonation
client = primp.Client(
    impersonate="chrome_146"
)
```

đến:

```text
https://tls.peet.ws/api/all
```

và quan sát sự khác nhau.

**Đừng cố học thuộc JSON fingerprint ở bài này.** Hãy tập trung vào một ý:

> **`User-Agent` chỉ là một phần của danh tính client; Browser Impersonation cố gắng làm cho nhiều đặc điểm của giao tiếp HTTP/TLS/HTTP2 phù hợp với một browser profile.** ([Docs.rs][1])

Buổi 22 chúng ta sẽ đi thẳng vào **Chrome Fingerprint: Chrome thực sự để lại những dấu vết gì, và `primp` profile liên quan đến chúng như thế nào.**

[1]: https://docs.rs/primp/latest/primp/imp/index.html?utm_source=chatgpt.com "primp::imp - Rust"
[2]: https://github.com/bigbio2002/curl-impersonate?utm_source=chatgpt.com "GitHub - bigbio2002/curl-impersonate: fork of original curl-impersonate by the author of curl_cffi for Python · GitHub"
[3]: https://docs.rs/crate/primp/latest?utm_source=chatgpt.com "primp 2.0.1 - Docs.rs"
