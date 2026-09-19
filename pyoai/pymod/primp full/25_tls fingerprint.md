# Phần III — Browser Impersonation

# Buổi 25 — TLS Fingerprint

Ở Buổi 24 chúng ta có:

```text
Browser
   +
Version
   +
OS
   ↓
Browser Persona
```

Hôm nay đi xuống **tầng thấp hơn**:

```text
Browser Persona
       ↓
     TLS
       ↓
TLS Fingerprint
```

Đây là một trong những phần quan trọng nhất để hiểu `primp`.

`primp` hiện mô tả browser impersonation là việc cấu hình **TLS + HTTP/2 + default headers** theo browser profile; mỗi profile browser/version ánh xạ tới cấu hình TLS và headers tương ứng. ([Docs.rs][1])

---

# 1. TLS là gì?

Khi bạn gọi:

```python
import primp

client = primp.Client()

response = client.get(
    "https://example.com"
)
```

không phải Python lập tức gửi:

```text
GET / HTTP/1.1
```

Trước đó phải thiết lập HTTPS.

Đơn giản hóa:

```text
Python
   │
   ▼
TCP connection
   │
   ▼
TLS handshake
   │
   ▼
Encrypted connection
   │
   ▼
HTTP
```

TLS chịu trách nhiệm chính cho:

* mã hóa
* xác thực server
* thương lượng phiên bản TLS
* cipher suite
* extensions
* key exchange
* ALPN

---

# 2. TLS Fingerprint là gì?

Hai client đều có thể sử dụng:

```text
TLS 1.3
```

nhưng không nhất thiết gửi một `ClientHello` giống nhau.

Ví dụ:

```text
Client A
ClientHello
├── TLS version
├── cipher suites
├── extensions
├── supported groups
├── signature algorithms
└── key share
```

Client B:

```text
ClientHello
├── TLS version
├── cipher suites khác
├── extensions khác
├── thứ tự khác
└── supported groups khác
```

Server có thể quan sát những đặc điểm này.

Đó chính là nền tảng của khái niệm:

```text
TLS fingerprint
```

---

# 3. `ClientHello`

Muốn hiểu TLS fingerprint, trước hết phải hiểu:

```text
ClientHello
```

Một TLS handshake đơn giản:

```text
Client                         Server
  │                              │
  │────── ClientHello ──────────>│
  │                              │
  │<────── ServerHello ──────────│
  │                              │
  │<────── Certificate ──────────│
  │                              │
  │<────── ... ──────────────────│
  │                              │
  │════ encrypted connection ════│
```

`ClientHello` là phần cực kỳ quan trọng đối với fingerprint.

---

# 4. ClientHello chứa những gì?

Không cần nhớ tất cả ngay.

Ở mức hiện tại hãy nhớ:

```text
ClientHello
│
├── TLS version
├── Cipher Suites
├── Extensions
├── Supported Groups
├── Signature Algorithms
├── Key Share
└── ...
```

Một browser cụ thể có cách lựa chọn và sắp xếp các thành phần này.

Do đó:

```text
Chrome
```

và:

```text
Firefox
```

không nhất thiết có cùng TLS fingerprint.

---

# 5. Ví dụ đơn giản

Giả sử có:

```text
Client A
```

gửi:

```text
Cipher Suites:
A
B
C
D
```

Client B:

```text
Cipher Suites:
B
A
D
C
```

Dù cả hai đều hỗ trợ:

```text
A B C D
```

nhưng cách biểu diễn có thể khác.

Server có thể sử dụng nhiều đặc điểm kết hợp để phân biệt client.

---

# 6. TLS fingerprint không phải User-Agent

Đây là điều cần nhớ nhất trong toàn bộ Buổi 25.

Ta có:

```text
User-Agent
```

ở tầng HTTP.

Ví dụ:

```text
User-Agent: Mozilla/5.0 ...
```

Nhưng TLS fingerprint xuất hiện **trước HTTP**.

```text
                 HTTPS
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
       TLS                   HTTP
        │                     │
 fingerprint              User-Agent
```

Do đó đổi:

```python
headers={
    "User-Agent": "Chrome ..."
}
```

**không biến Python client thành Chrome ở tầng TLS.**

---

# 7. Đây chính là lý do Browser Impersonation quan trọng

Nếu chỉ làm:

```python
client = primp.Client(
    headers={
        "User-Agent": "Chrome..."
    }
)
```

thì:

```text
HTTP headers
     ↓
Chrome-like
```

nhưng:

```text
TLS
     ↓
vẫn là TLS stack của client
```

Đây là persona không đồng nhất.

Trong khi:

```python
client = primp.Client(
    impersonate="chrome_146"
)
```

`primp` sử dụng browser profile tương ứng, bao gồm cấu hình TLS, HTTP/2 và default headers. ([Docs.rs][1])

---

# 8. `primp` làm gì?

Tài liệu Rust của `primp` mô tả `Impersonate` là browser version mà mỗi variant ánh xạ tới **TLS fingerprint và default headers**. Module impersonation cũng bao gồm cấu hình HTTP/2. ([Docs.rs][1])

Có thể hình dung:

```text
primp
 │
 ├── Chrome 146
 │     │
 │     ├── TLS settings
 │     ├── HTTP/2 settings
 │     └── Headers
 │
 ├── Firefox 146
 │     │
 │     ├── TLS settings
 │     ├── HTTP/2 settings
 │     └── Headers
 │
 └── Safari 26
       │
       ├── TLS settings
       ├── HTTP/2 settings
       └── Headers
```

Đây chính là lý do `impersonate="chrome_146"` mạnh hơn việc tự đổi User-Agent.

---

# 9. Test `primp`

Theo PyPI hiện tại, ví dụ chính thức sử dụng:

```python
import primp

client = primp.Client(
    impersonate="chrome_146"
)

response = client.get(
    "https://tls.peet.ws/api/all"
)

print(response.text)
```

`primp 2.0.1` hiện có các profile Chrome từ `chrome_144` đến `chrome_153`, cùng các profile Firefox, Safari, Edge, Opera và OS tương ứng. ([PyPI][2])

---

# 10. Quan sát TLS fingerprint

Endpoint:

```text
https://tls.peet.ws/api/all
```

rất tiện để học vì nó phản hồi các thông tin liên quan tới kết nối TLS/HTTP.

Code:

```python
import primp


URL = "https://tls.peet.ws/api/all"


def main():
    client = primp.Client(
        impersonate="chrome_146",
        impersonate_os="windows",
    )

    response = client.get(URL)

    print(response.text)


if __name__ == "__main__":
    main()
```

Không nên cố định rằng endpoint sẽ luôn có chính xác một schema nào đó; hãy xem JSON thực tế trả về rồi phân tích.

---

# 11. So sánh không impersonate và impersonate

Đây là bài test quan trọng nhất.

```python
import primp


URL = "https://tls.peet.ws/api/all"


def test(name: str, client: primp.Client):
    print("=" * 80)
    print(name)
    print("=" * 80)

    response = client.get(URL)
    print(response.text)
    print()


def main():

    normal = primp.Client()

    chrome = primp.Client(
        impersonate="chrome_146",
        impersonate_os="windows",
    )

    test("NORMAL", normal)
    test("CHROME 146 WINDOWS", chrome)


if __name__ == "__main__":
    main()
```

Mục tiêu của bài này không phải:

```text
"Chrome chắc chắn vượt qua anti-bot"
```

mà là hiểu:

```text
Normal Client
     ≠
Browser impersonation
```

ở tầng network fingerprint.

---

# 12. TLS version

Một thành phần của TLS negotiation là version.

Ví dụ:

```text
TLS 1.2
TLS 1.3
```

Nhưng **không được hiểu fingerprint chỉ là TLS version**.

Ví dụ:

```text
Chrome
TLS 1.3
```

và:

```text
Firefox
TLS 1.3
```

vẫn có thể có fingerprint khác nhau.

Bởi vì còn:

```text
Cipher suites
Extensions
Supported groups
Signature algorithms
Key shares
...
```

---

# 13. Cipher Suites

Một TLS client có thể hỗ trợ nhiều cipher suites.

Ví dụ minh họa:

```text
TLS_AES_128_GCM_SHA256
TLS_AES_256_GCM_SHA384
TLS_CHACHA20_POLY1305_SHA256
```

Thứ tự và tập cipher suites là một trong những thành phần có thể góp phần vào fingerprint.

Đừng học theo kiểu:

```text
TLS fingerprint = cipher suite
```

mà hãy nhớ:

```text
TLS fingerprint
    =
nhiều thuộc tính của TLS handshake
```

---

# 14. TLS Extensions

Đây là phần sâu hơn.

`ClientHello` có thể chứa các extensions.

Ví dụ khái niệm:

```text
ClientHello
│
├── server_name
├── supported_versions
├── signature_algorithms
├── supported_groups
├── key_share
├── ALPN
└── ...
```

Browser profile có thể có:

```text
extension A
extension B
extension C
```

với thứ tự/cấu hình nhất định.

Client khác có thể:

```text
extension A
extension C
extension B
```

Vì vậy fingerprint không chỉ là "có extension hay không".

---

# 15. ALPN

Một extension đặc biệt quan trọng:

```text
ALPN
```

Application-Layer Protocol Negotiation.

Nó giúp client/server thương lượng protocol ứng dụng.

Ví dụ:

```text
h2
http/1.1
```

Mô hình:

```text
TLS handshake
      │
      ▼
ALPN
      │
 ┌────┴────┐
 ▼         ▼
h2       HTTP/1.1
```

Điều này dẫn trực tiếp sang **Buổi 26 — HTTP/2**.

---

# 16. TLS fingerprint và HTTP/2 fingerprint là hai chuyện khác nhau

Đừng gộp:

```text
TLS fingerprint
```

và:

```text
HTTP/2 fingerprint
```

thành một thứ.

Mô hình:

```text
Browser
   │
   ├───────────────┐
   ▼               ▼
 TLS              HTTP/2
   │               │
   ▼               ▼
TLS fingerprint   H2 fingerprint
```

`primp` impersonation hiện bao gồm cả TLS và HTTP/2 configuration. ([Docs.rs][1])

---

# 17. HTTP/2 fingerprint gồm gì?

Chúng ta sẽ học kỹ ở Buổi 26, nhưng hiện tại chỉ cần biết:

```text
HTTP/2
│
├── SETTINGS
├── WINDOW_UPDATE
├── pseudo-header order
├── PRIORITY-related behavior
└── ...
```

Tài liệu `primp` hiện có các cấu trúc riêng cho `Http2Data`, `PseudoOrder`, `SettingsOrder` và các HTTP/2 settings phục vụ browser impersonation. ([Docs.rs][1])

---

# 18. JA3 là gì?

Khi học TLS fingerprint, bạn sẽ gặp:

```text
JA3
```

JA3 là một cách biểu diễn fingerprint của TLS ClientHello thành một giá trị hash.

Tư duy đơn giản:

```text
ClientHello
     │
     ├── version
     ├── ciphers
     ├── extensions
     ├── curves
     └── point formats
             │
             ▼
         fingerprint
             │
             ▼
             hash
```

Kết quả thường được biểu diễn bằng MD5 hash.

Nhưng:

> **JA3 không phải toàn bộ TLS fingerprint hiện đại.**

Đây là điểm rất quan trọng.

---

# 19. JA4

JA4 là thế hệ fingerprinting rộng hơn, được thiết kế để cung cấp biểu diễn hữu ích hơn trong các môi trường hiện đại.

Vì vậy khi gặp:

```text
JA3
JA4
```

đừng nghĩ:

```text
JA3 = TLS
JA4 = TLS
```

mà:

```text
TLS handshake
      ↓
fingerprinting methodology
      ├── JA3
      └── JA4
```

Các tài liệu/phiên bản cũ của `primp` từng mô tả impersonation cùng TLS/JA3/JA4/HTTP2 fingerprints; tài liệu hiện tại của 2.0.x tập trung mô tả browser profiles dưới dạng TLS + HTTP/2 + headers. ([PyPI][3])

---

# 20. Đừng nhầm "JA3 giống nhau" với "browser giống nhau"

Ví dụ:

```text
Client A
JA3 = X
```

và:

```text
Client B
JA3 = X
```

không có nghĩa:

```text
A == B
```

về toàn bộ fingerprint.

Có thể khác:

```text
HTTP/2
Headers
Cookies
IP
TLS details khác ngoài những trường JA3 biểu diễn
```

Do đó:

```text
JA3
```

chỉ là **một measurement**, không phải toàn bộ danh tính browser.

---

# 21. `primp` và TLS fingerprint

Đây là kiến thức cốt lõi:

```python
client = primp.Client(
    impersonate="chrome_146"
)
```

không đơn giản là:

```text
User-Agent = Chrome
```

Mà profile được resolve thành các browser settings, trong đó có TLS và HTTP/2 configuration. Tài liệu Rust của `primp` mô tả `get_browser_settings` là hàm resolve browser settings gồm TLS, HTTP/2 và headers theo browser version + OS. ([Docs.rs][1])

Mô hình:

```text
"chrome_146"
      │
      ▼
Browser Settings
      │
 ┌────┼─────┐
 ▼    ▼     ▼
TLS  HTTP2 Headers
```

---

# 22. `impersonate_os` liên quan thế nào?

Buổi 24:

```python
client = primp.Client(
    impersonate="chrome_146",
    impersonate_os="windows",
)
```

Có thể hình dung:

```text
chrome_146
     +
windows
     │
     ▼
get_browser_settings(...)
     │
     ├── TLS
     ├── HTTP/2
     └── Headers
```

Đây là lý do Browser + OS phải được coi là **một persona có tính nhất quán**, thay vì random độc lập từng request. Tài liệu `primp` hiện xác nhận browser settings được resolve theo browser version và OS. ([Docs.rs][1])

---

# 23. Sai lầm phổ biến #1

```python
client = primp.Client(
    impersonate="chrome_146"
)

client.get(
    url,
    headers={
        "User-Agent": "Firefox..."
    }
)
```

Ta vừa nói:

```text
Chrome profile
```

nhưng lại gửi:

```text
Firefox User-Agent
```

Persona trở nên không nhất quán.

Nguyên tắc:

> Khi sử dụng browser impersonation, hạn chế override các header mà profile đã quản lý nếu không có lý do rõ ràng.

---

# 24. Sai lầm phổ biến #2

Tự nghĩ:

```python
headers = {
    "User-Agent": "...Chrome...",
    "Accept": "...",
}
```

là đủ để giả lập browser.

Không.

```text
Headers
   ≠
TLS
   ≠
HTTP/2
```

Một browser request là tổng hợp nhiều tầng:

```text
Browser
   │
   ├── Headers
   ├── TLS
   ├── HTTP/2
   ├── Cookies
   └── Browser-side behavior
```

---

# 25. Sai lầm phổ biến #3

Tự chỉnh TLS fingerprint ngay lập tức.

Ví dụ:

```text
Tôi muốn Chrome
→ tự sửa cipher suites
→ tự sửa extensions
→ tự sửa HTTP/2
```

Không nên làm vậy ở giai đoạn này.

`primp` đã cung cấp browser profiles được định nghĩa sẵn.

Hãy bắt đầu bằng:

```python
primp.Client(
    impersonate="chrome_146"
)
```

trước.

---

# 26. Kiến trúc của Novel Crawler

Đây là nơi kiến thức hôm nay kết nối với Fetcher mà bạn đang xây.

Application:

```text
CrawlChapter
      │
      ▼
Fetcher Interface
      │
      ▼
PrimpFetcher
      │
      ▼
BrowserProfile
      │
      ▼
primp.Client
      │
      ├── TLS
      ├── HTTP/2
      └── Headers
```

Domain không cần biết:

```text
JA3
JA4
TLS
ClientHello
HTTP/2
```

Đó là infrastructure concern.

---

# 27. Thiết kế `BrowserProfile`

Ở mức hiện tại:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserProfile:
    impersonate: str
    os: str | None = None
```

Ví dụ:

```python
chrome_windows = BrowserProfile(
    impersonate="chrome_146",
    os="windows",
)
```

Infrastructure:

```python
import primp


def create_client(profile: BrowserProfile):
    kwargs = {
        "impersonate": profile.impersonate,
    }

    if profile.os is not None:
        kwargs["impersonate_os"] = profile.os

    return primp.Client(**kwargs)
```

---

# 28. Đây là abstraction vừa đủ

Không nên ngay lập tức tạo:

```text
TLSFingerprint
TLSFingerprintFactory
JA3Builder
JA4Builder
HTTP2FingerprintFactory
BrowserFingerprintRegistry
BrowserProfileFactory
```

Chúng ta chưa cần.

Hiện tại:

```text
BrowserProfile
      ↓
primp.Client
```

là đủ.

Khi đến:

```text
Buổi 27
Headers + fingerprint
```

và:

```text
Buổi 28
Fingerprint thực tế
```

complexity mới tăng lên.

---

# 29. Bài thực hành 1 — Normal vs Chrome

Tạo:

```text
lesson_25_01.py
```

```python
import primp


URL = "https://tls.peet.ws/api/all"


def main():
    clients = {
        "normal": primp.Client(),
        "chrome": primp.Client(
            impersonate="chrome_146",
            impersonate_os="windows",
        ),
    }

    for name, client in clients.items():
        print("=" * 80)
        print(name)
        print("=" * 80)

        response = client.get(URL)

        print(response.text)
        print()


if __name__ == "__main__":
    main()
```

Hãy quan sát sự khác biệt.

---

# 30. Bài thực hành 2 — Chrome vs Firefox

```python
import primp


URL = "https://tls.peet.ws/api/all"


PROFILES = [
    ("chrome", "chrome_146"),
    ("firefox", "firefox_146"),
]


def main():
    for name, profile in PROFILES:
        client = primp.Client(
            impersonate=profile,
            impersonate_os="windows",
        )

        response = client.get(URL)

        print("=" * 80)
        print(name)
        print("=" * 80)
        print(response.text)


if __name__ == "__main__":
    main()
```

Câu hỏi cần tự trả lời:

```text
Chrome 146
     vs
Firefox 146

TLS giống nhau hoàn toàn?
HTTP/2 giống nhau?
Headers giống nhau?
```

Không cần đoán trước. Hãy quan sát output thực tế.

---

# 31. Bài thực hành 3 — Browser + OS

```python
import primp


URL = "https://tls.peet.ws/api/all"


PROFILES = [
    ("chrome_windows", "chrome_146", "windows"),
    ("chrome_macos", "chrome_146", "macos"),
    ("chrome_linux", "chrome_146", "linux"),
]


def main():
    for name, browser, os in PROFILES:

        client = primp.Client(
            impersonate=browser,
            impersonate_os=os,
        )

        response = client.get(URL)

        print("=" * 80)
        print(name)
        print("=" * 80)

        print(response.text)


if __name__ == "__main__":
    main()
```

Mục tiêu:

```text
Chrome + Windows
Chrome + macOS
Chrome + Linux
```

được coi là ba browser personas khác nhau.

---

# 32. Một nguyên tắc rất quan trọng cho Crawler

Đừng làm:

```text
request 1 → Chrome Windows
request 2 → Firefox Linux
request 3 → Safari iOS
request 4 → Chrome macOS
```

chỉ để "random fingerprint".

Thay vào đó:

```text
Crawler Session A
    │
    ├── Browser = Chrome 146
    ├── OS = Windows
    ├── Cookies
    └── Proxy
```

và dùng ổn định:

```text
Chapter 1 → same persona
Chapter 2 → same persona
Chapter 3 → same persona
...
```

Điều này phù hợp với kiến trúc Session/Client lifecycle mà chúng ta đã học ở Buổi 16–20.

---

# 33. Toàn bộ bức tranh đến hiện tại

Sau 25 buổi:

```text
HTTP
 │
 ├── GET
 ├── POST
 ├── Headers
 ├── Params
 ├── Cookies
 ├── Redirect
 ├── Timeout
 ├── Exception
 ├── Auth
 ├── Proxy
 └── SSL
          │
          ▼
Browser Impersonation
          │
          ├── Browser
          ├── Version
          ├── OS
          │
          ▼
        TLS
          │
          ├── ClientHello
          ├── Cipher Suites
          ├── Extensions
          ├── ALPN
          └── TLS Fingerprint
          │
          ▼
        HTTP/2
```

---

# 34. Điều cần nhớ sau Buổi 25

Nếu chỉ nhớ **5 câu**, hãy nhớ:

### ① User-Agent không phải TLS fingerprint

```text
User-Agent → HTTP
TLS fingerprint → TLS handshake
```

### ② TLS fingerprint chủ yếu liên quan đến ClientHello

```text
ClientHello
   ↓
TLS characteristics
   ↓
Fingerprint
```

### ③ Browser impersonation không chỉ đổi header

`primp` browser profiles bao gồm TLS, HTTP/2 và default headers. ([Docs.rs][1])

### ④ JA3/JA4 chỉ là các phương pháp biểu diễn fingerprint

Không đồng nhất:

```text
JA3 = toàn bộ browser fingerprint
```

### ⑤ Browser + OS + TLS + HTTP/2 phải được nhìn như một persona

```text
Browser
   +
Version
   +
OS
   +
TLS
   +
HTTP/2
   +
Headers
   ↓
Browser-like network persona
```

`primp 2.0.1` hiện cung cấp các browser profiles và OS profiles tương ứng, và tài liệu của nó mô tả việc resolve browser settings theo browser version/OS. ([PyPI][2])

---

## Roadmap

```text
PHẦN III — BROWSER IMPERSONATION

21. Vì sao cần impersonation       ✅
22. Chrome fingerprint              ✅
23. Firefox / Safari / Edge         ✅
24. impersonate_os                   ✅
25. TLS fingerprint                  ✅
26. HTTP/2                           ← tiếp theo
27. Headers + fingerprint
28. Fingerprint thực tế
29. So sánh httpx vs primp
30. Xây BrowserClient
```

**Buổi 26 sẽ đi thẳng vào HTTP/2 fingerprint**: `ALPN → h2 → SETTINGS frame → WINDOW_UPDATE → pseudo-header order → HTTP/2 fingerprint`, rồi dùng `primp` để quan sát sự khác biệt giữa HTTP/1.1 và HTTP/2.

[1]: https://docs.rs/primp/latest/primp/imp/index.html?utm_source=chatgpt.com "primp::imp - Rust"
[2]: https://pypi.org/project/primp/2.0.1/?utm_source=chatgpt.com "primp · PyPI"
[3]: https://pypi.org/project/primp/1.0.0/?utm_source=chatgpt.com "primp · PyPI"
