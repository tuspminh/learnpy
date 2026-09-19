# Phần III — Browser Impersonation

# Buổi 22 — Chrome Fingerprint

Ở Buổi 21 chúng ta đã có ý tưởng:

> **User-Agent ≠ Browser Fingerprint.**

Hôm nay ta đi sâu vào **Chrome fingerprint**, nhưng sẽ tập trung vào phần `primp` thực sự có thể mô phỏng ở tầng HTTP/TLS/HTTP2, tránh nhầm với fingerprint JavaScript của trình duyệt.

`primp` 2.0.1 hiện mô tả browser impersonation là cấu hình **TLS, HTTP/2 và default headers**, và mỗi profile Chrome tương ứng với một bộ cấu hình browser-specific. ([Docs.rs][1])

---

# 1. Chrome Fingerprint là gì?

Có thể hiểu đơn giản:

```text
Chrome Fingerprint
        │
        ├── HTTP characteristics
        ├── TLS characteristics
        ├── HTTP/2 characteristics
        └── Browser-side characteristics
```

Nhưng cần chia thành hai nhóm.

### Nhóm A — Network fingerprint

```text
HTTP
TLS
HTTP/2
```

Đây là phần `primp` đặc biệt quan tâm.

### Nhóm B — Browser/JavaScript fingerprint

Ví dụ:

```text
navigator
screen
canvas
WebGL
fonts
audio
timezone
```

Những thứ này thường yêu cầu **browser thật + JavaScript** để quan sát.

`primp` không phải Chromium và không chạy JavaScript browser. Vì vậy:

> **`primp` không tái tạo toàn bộ Chrome fingerprint.**

Nó chủ yếu mô phỏng các đặc điểm network/browser protocol mà profile của nó định nghĩa.

---

# 2. Hãy nhìn Chrome như một "profile"

Thay vì suy nghĩ:

```text
Chrome = User-Agent
```

hãy nghĩ:

```text
Chrome 146
    │
    ├── User-Agent
    ├── Default headers
    ├── TLS configuration
    ├── HTTP/2 configuration
    └── OS-related characteristics
```

Đây cũng chính là cách `primp` tổ chức impersonation.

Trong tài liệu hiện tại, `Impersonate` map một browser version tới **TLS fingerprint và default headers**, còn module impersonation chứa riêng dữ liệu HTTP/2. ([Docs.rs][2])

---

# 3. Chrome Profile trong `primp`

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

Ta có:

```text
"chrome_146"
      │
      ▼
Chrome browser profile
      │
      ├── TLS settings
      ├── HTTP/2 settings
      └── default headers
```

Danh sách hiện tại của `primp 2.0.1` có các profile:

```text
chrome_144
chrome_145
chrome_146
chrome_147
chrome_148
...
chrome_153
chrome
```

Ngoài ra còn Firefox, Safari, Edge và Opera. ([Docs.rs][1])

---

# 4. `chrome` và `chrome_146`

Có hai cách tư duy:

```python
impersonate="chrome"
```

và:

```python
impersonate="chrome_146"
```

Trong tài liệu Rust của `primp`, profile không có version cụ thể như `Chrome` có thể được resolve thành một version cụ thể; tài liệu cũng cung cấp các profile version cụ thể. ([Docs.rs][2])

Vì vậy:

### Generic

```python
client = primp.Client(
    impersonate="chrome"
)
```

Ý tưởng:

```text
Chrome family
    ↓
chọn profile phù hợp
```

### Pinned

```python
client = primp.Client(
    impersonate="chrome_146"
)
```

Ý tưởng:

```text
Chrome 146
    ↓
profile cụ thể
```

Trong crawler production, việc **pin version** có thể hữu ích khi bạn muốn reproducibility.

---

# 5. Tại sao Chrome fingerprint không chỉ là Header?

Giả sử:

```python
client = primp.Client()

response = client.get(
    url,
    headers={
        "User-Agent": "Chrome..."
    }
)
```

Ta mới thay đổi:

```text
HTTP Header
```

Trong khi:

```text
TLS
HTTP/2
```

vẫn có thể có đặc điểm khác.

Hình dung:

```text
                 Request
                    │
        ┌───────────┼───────────┐
        │           │           │
     Headers       TLS        HTTP/2
        │           │           │
      Chrome      Other       Other
```

Đây là fingerprint **không nhất quán**.

---

# 6. Impersonation cố gắng tạo sự nhất quán

Khi dùng:

```python
client = primp.Client(
    impersonate="chrome_146"
)
```

mô hình trở thành:

```text
                 Chrome 146
                     │
        ┌────────────┼────────────┐
        │            │            │
     Headers        TLS         HTTP/2
        │            │            │
     Chrome       Chrome        Chrome
```

Đây là khái niệm quan trọng nhất của bài:

> **Fingerprint consistency.**

Các dự án browser impersonation như `curl-impersonate` cũng mô tả cách tiếp cận tương tự: thay đổi TLS configuration, TLS extensions, HTTP/2 settings và headers để request có đặc điểm gần browser mục tiêu. ([GitHub][3])

---

# 7. Chrome Fingerprint — tầng Headers

Chrome request có nhiều header hơn chỉ:

```text
User-Agent
Accept
```

Có thể gặp:

```text
Accept
Accept-Language
Accept-Encoding
User-Agent
Sec-CH-UA
Sec-CH-UA-Mobile
Sec-CH-UA-Platform
Sec-Fetch-Dest
Sec-Fetch-Mode
Sec-Fetch-Site
Sec-Fetch-User
```

Nhưng **đừng tự copy toàn bộ header Chrome vào `primp`**.

Vì:

```text
Browser Profile
       │
       └── đã có default headers
```

`primp` documentation nói rõ browser settings bao gồm default headers. ([Docs.rs][2])

Do đó:

```python
client = primp.Client(
    impersonate="chrome_146"
)
```

đã khác với:

```python
client = primp.Client()
```

mà không cần tự viết hàng chục header.

---

# 8. Một nguyên tắc quan trọng: đừng "over-customize"

Giả sử:

```python
client = primp.Client(
    impersonate="chrome_146"
)
```

Sau đó bạn tự thêm:

```python
headers={
    "User-Agent": "Chrome 120",
}
```

Bạn vừa tạo:

```text
Chrome 146 profile
       +
Chrome 120 User-Agent
```

Có thể dẫn tới:

```text
Fingerprint inconsistency
```

Vì vậy:

> **Khi dùng browser profile, hãy để profile quản lý những thuộc tính mà nó đã định nghĩa, chỉ override khi bạn thực sự có lý do.**

---

# 9. Chrome Fingerprint — tầng TLS

Đây là phần chúng ta sẽ học kỹ ở Buổi 25.

Hiện tại chỉ cần biết:

```text
Chrome
  ↓
TLS ClientHello
```

ClientHello chứa nhiều đặc điểm:

```text
TLS versions
Cipher suites
Extensions
Supported groups
Signature algorithms
ALPN
...
```

Một HTTP library thông thường có thể tạo TLS handshake khác Chrome.

Browser impersonation thay đổi TLS configuration để phù hợp với profile mục tiêu.

`primp` hiện mô tả từng browser version bằng TLS configuration riêng trong `BrowserSettings`. ([Docs.rs][2])

---

# 10. Chrome Fingerprint — tầng HTTP/2

Nếu sử dụng HTTP/2:

```text
Chrome
  ↓
HTTP/2 connection
```

có những thông tin như:

```text
SETTINGS
Pseudo-header order
HTTP/2 connection settings
```

`primp` có các kiểu dữ liệu như:

```text
Http2Data
PseudoOrder
SettingsOrder
```

trong module impersonation. ([Docs.rs][2])

Ta sẽ học kỹ ở:

```text
Buổi 26 — HTTP/2
```

---

# 11. Một Chrome Profile thực chất là gì?

Ta có thể mô hình hóa về mặt khái niệm:

```python
@dataclass
class ChromeProfile:
    version: int
    tls: TLSProfile
    http2: HTTP2Profile
    headers: HeadersProfile
```

Không phải code API của `primp`, mà là **mô hình tư duy**.

Ví dụ:

```text
ChromeProfile(146)
       │
       ├── TLS
       │     ├── cipher suites
       │     ├── extensions
       │     └── ALPN
       │
       ├── HTTP/2
       │     ├── SETTINGS
       │     └── pseudo-header order
       │
       └── Headers
             ├── User-Agent
             ├── Accept
             └── browser headers
```

Đây là cách chúng ta sẽ thiết kế `BrowserClient` ở Buổi 30.

---

# 12. Chrome Desktop vs Chrome Android

Một điểm rất quan trọng.

Không nên nghĩ:

```text
Chrome = một fingerprint duy nhất
```

Mà:

```text
Chrome
├── Windows
├── macOS
├── Linux
├── Android
└── ...
```

Cùng Chrome nhưng OS khác nhau có thể dẫn tới những khác biệt về profile.

Đây là lý do roadmap của chúng ta có riêng:

```text
24. impersonate_os
```

Trong `primp`, `ImpersonateOS` được mô tả là OS platform dùng khi tạo browser fingerprints. ([Docs.rs][2])

---

# 13. Ví dụ tư duy

### Chrome trên Windows

```text
Chrome
  +
Windows
  ↓
Browser profile A
```

### Chrome trên macOS

```text
Chrome
  +
macOS
  ↓
Browser profile B
```

### Chrome trên Android

```text
Chrome
  +
Android
  ↓
Browser profile C
```

Vì vậy:

```text
Browser
   +
OS
   ↓
Fingerprint
```

Đây chính là lý do Buổi 24 rất quan trọng.

---

# 14. Fingerprint ≠ Identity tuyệt đối

Đây cũng là một điểm cần tránh hiểu sai.

Nếu hai request có:

```text
Chrome-like TLS
Chrome-like HTTP/2
Chrome-like headers
```

không có nghĩa server chắc chắn kết luận:

```text
"Đây chính xác là Chrome thật."
```

Fingerprint chỉ là tập hợp tín hiệu.

Server có thể kết hợp:

```text
Fingerprint
+
IP
+
Cookies
+
Request behavior
+
Rate
+
JavaScript signals
+
...
```

Do đó:

```text
Browser impersonation
        ≠
Real browser
```

và:

```text
Browser fingerprint
        ≠
User identity
```

---

# 15. Test thực tế

Ta dùng endpoint fingerprint để quan sát.

## Test 1 — Normal Client

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

---

## Test 2 — Chrome 146

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

Sau đó so sánh.

Bạn có thể lưu kết quả:

```text
normal.json
chrome_146.json
```

rồi tìm:

```text
tls
http2
user_agent
headers
```

---

# 16. Test 3 — Chrome generic

```python
import primp


def main():
    client = primp.Client(
        impersonate="chrome"
    )

    response = client.get(
        "https://tls.peet.ws/api/all"
    )

    print(response.text)


if __name__ == "__main__":
    main()
```

So sánh:

```text
chrome
vs
chrome_146
```

Đây là một bài thực hành rất tốt để hiểu:

```text
generic browser profile
        vs
version-specific profile
```

---

# 17. Đừng chỉ nhìn User-Agent

Khi test, nếu bạn thấy:

```text
User-Agent:
Mozilla/5.0 ...
```

đừng kết luận:

> "À, primp đã giả Chrome."

Hãy xem thêm:

```text
TLS
HTTP/2
```

Tư duy đúng:

```text
                 Chrome Profile
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Headers        TLS         HTTP/2
          │            │            │
          └────────────┼────────────┘
                       ▼
                    Request
```

---

# 18. `primp` không phải Selenium

Một lần nữa:

```text
primp
```

không có:

```text
DOM
JavaScript
navigator
canvas
WebGL
document
window
```

Do đó nếu website sử dụng JavaScript để kiểm tra:

```javascript
navigator.webdriver
```

hoặc:

```javascript
canvas fingerprint
```

thì `primp` không thể đơn giản giải quyết bằng:

```python
impersonate="chrome_146"
```

Đó là một lớp hoàn toàn khác.

---

# 19. Liên hệ với Novel Crawler

Đây là kiến trúc chúng ta hướng tới:

```text
Novel Crawler
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
       ├── Chrome
       ├── Firefox
       ├── Safari
       └── Edge
       │
       ▼
primp.Client
       │
       ▼
Novel Website
```

Application chỉ cần:

```python
response = fetcher.get(url)
```

Nó không cần biết:

```text
TLS
HTTP/2
Chrome fingerprint
```

Đây là **separation of concerns**.

---

# 20. Không nên làm thế này

```python
class NovelService:

    def crawl(self, url):
        client = primp.Client(
            impersonate="chrome_146"
        )

        response = client.get(url)

        ...
```

Sai về architecture.

Vì Application/Domain đang biết:

```text
primp
chrome_146
```

---

# 21. Nên làm thế này

```python
class PrimpFetcher:

    def __init__(self):
        self.client = primp.Client(
            impersonate="chrome_146"
        )

    def get(self, url):
        return self.client.get(url)
```

Application:

```python
class CrawlChapter:

    def __init__(self, fetcher):
        self.fetcher = fetcher

    def execute(self, url):
        return self.fetcher.get(url)
```

Kết quả:

```text
Application
    │
    │ get(url)
    ▼
Fetcher
    │
    ▼
PrimpFetcher
    │
    ▼
Chrome 146 Profile
    │
    ▼
primp
```

---

# 22. Một vấn đề rất quan trọng: Profile + Headers

Giả sử:

```python
client = primp.Client(
    impersonate="chrome_146"
)
```

Sau đó:

```python
response = client.get(
    url,
    headers={
        "User-Agent": "MyCrawler/1.0"
    }
)
```

Bạn vừa phá vỡ một phần browser profile.

Không phải lúc nào override cũng sai, nhưng cần hiểu:

```text
Profile
   ↓
có default headers
```

và:

```text
Request headers
   ↓
override
```

Do đó:

> **Custom headers nên được thêm có chủ đích, không nên tùy tiện ghi đè browser headers.**

---

# 23. Browser Profile không đồng nghĩa "ẩn danh"

Một misconception khác:

```text
Chrome impersonation
       ↓
IP ẩn
```

Sai.

Impersonation **không tự thay đổi IP**.

Muốn thay đổi network route:

```text
Proxy
```

là một vấn đề khác.

Ta có:

```text
Browser Profile
      +
Proxy
      +
Cookies
      +
Rate Limit
```

là những concern riêng biệt.

Trong kiến trúc crawler:

```text
BrowserProfileStrategy
ProxyStrategy
RetryPolicy
RateLimiter
```

không nên gộp thành một class khổng lồ.

Đây chính là hướng SOLID mà ta sẽ áp dụng sau này.

---

# 24. Bài thực hành chính

Tạo:

```text
lesson_22.py
```

```python
import primp


URL = "https://tls.peet.ws/api/all"


def test_normal():
    client = primp.Client()

    response = client.get(URL)

    print("=" * 70)
    print("NORMAL CLIENT")
    print("=" * 70)
    print(response.text)


def test_chrome():
    client = primp.Client(
        impersonate="chrome_146"
    )

    response = client.get(URL)

    print("=" * 70)
    print("CHROME 146")
    print("=" * 70)
    print(response.text)


def main():
    test_normal()
    test_chrome()


if __name__ == "__main__":
    main()
```

Sau đó trả lời 4 câu:

```text
1. User-Agent của hai request khác nhau thế nào?

2. TLS information khác nhau ở đâu?

3. HTTP/2 information khác nhau ở đâu?

4. Điều gì chứng minh rằng impersonation
   không chỉ đơn giản là đổi User-Agent?
```

---

# 25. Bài tập nâng cao — lưu fingerprint

Ta có thể lưu response:

```python
from pathlib import Path
import primp


URL = "https://tls.peet.ws/api/all"


def fetch(impersonate=None):
    client = primp.Client(
        impersonate=impersonate
    ) if impersonate else primp.Client()

    return client.get(URL).text


def main():
    Path("normal.json").write_text(
        fetch(),
        encoding="utf-8",
    )

    Path("chrome_146.json").write_text(
        fetch("chrome_146"),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
```

Sau đó dùng editor để diff:

```text
normal.json
     vs
chrome_146.json
```

Đây là cách học fingerprint **tốt hơn nhiều so với học thuộc lý thuyết**.

---

# 26. Những gì cần nhớ sau Buổi 22

Chỉ cần nhớ 6 điểm:

### ① User-Agent chỉ là một tín hiệu

```text
User-Agent
   ≠
Browser fingerprint
```

### ② Chrome fingerprint có nhiều lớp

```text
Headers
TLS
HTTP/2
Browser-side signals
```

### ③ `primp` tập trung vào network/browser protocol impersonation

```text
TLS
HTTP/2
default headers
```

([Docs.rs][2])

### ④ `chrome_146` là browser profile

Không chỉ là:

```text
User-Agent = Chrome 146
```

### ⑤ Profile phải nhất quán

```text
Chrome profile
    ↓
Headers + TLS + HTTP/2
```

### ⑥ Impersonation không biến `primp` thành browser thật

```text
primp
   ≠
Chromium
```

---

## Roadmap tiếp theo

```text
21. Vì sao cần impersonation        ✅
22. Chrome fingerprint              ✅
23. Firefox / Safari / Edge
24. impersonate_os
25. TLS fingerprint
26. HTTP/2
27. Headers + fingerprint
28. Fingerprint thực tế
29. So sánh httpx vs primp
30. Xây BrowserClient
```

**Buổi 23** sẽ mở rộng từ Chrome sang **Firefox / Safari / Edge**: chúng khác Chrome ở đâu, tại sao không thể coi mọi browser là cùng một fingerprint, và cách chọn `impersonate` profile trong `primp` mà không biến Fetcher thành một đống `if/elif`.

[1]: https://docs.rs/crate/primp/latest?utm_source=chatgpt.com "primp 2.0.1 - Docs.rs"
[2]: https://docs.rs/primp/latest/primp/imp/index.html?utm_source=chatgpt.com "primp::imp - Rust"
[3]: https://github.com/bigbio2002/curl-impersonate?utm_source=chatgpt.com "GitHub - bigbio2002/curl-impersonate: fork of original curl-impersonate by the author of curl_cffi for Python · GitHub"
