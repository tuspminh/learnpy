# Phần III — Browser Impersonation

# Buổi 26 — HTTP/2 Fingerprint

Ở Buổi 25 chúng ta đã đi xuống tầng TLS:

```text
Browser Profile
      ↓
TLS
      ↓
ClientHello
      ↓
TLS Fingerprint
```

Hôm nay đi tiếp một tầng:

```text
TLS
 ↓
ALPN
 ↓
HTTP/2
 ↓
HTTP/2 Fingerprint
```

Điểm quan trọng: `primp` hiện mô tả browser impersonation là sự kết hợp của **TLS + HTTP/2 + default headers**, và source của `primp` có các cấu hình riêng cho HTTP/2 như `Http2Data`, thứ tự SETTINGS và thứ tự pseudo-header. ([Docs.rs][1])

---

# 1. HTTP/2 là gì?

HTTP/1.1 quen thuộc:

```text
GET /chapter-1 HTTP/1.1
Host: example.com
Accept: text/html
```

HTTP/2 thay đổi cách truyền HTTP ở tầng protocol.

Thay vì coi request đơn giản như một đoạn text:

```text
HTTP/1.1
    ↓
text-based request
```

HTTP/2 sử dụng:

```text
HTTP/2
   ↓
Binary frames
   ↓
Streams
```

Mô hình:

```text
TCP
 ↓
TLS
 ↓
HTTP/2
 ├── Stream 1
 ├── Stream 3
 ├── Stream 5
 └── ...
```

---

# 2. HTTP/2 không phải HTTP/1.1 nhanh hơn một chút

Đây là cách hiểu sai phổ biến.

HTTP/2 là một **giao thức khác ở tầng HTTP**.

So sánh:

```text
HTTP/1.1
    │
    ├── text-based
    ├── request/response
    └── connection behavior
```

với:

```text
HTTP/2
    │
    ├── binary frames
    ├── streams
    ├── multiplexing
    ├── HPACK
    └── SETTINGS
```

---

# 3. HTTP/2 dùng binary frames

HTTP/2 truyền dữ liệu bằng frame.

Một số loại frame quan trọng:

```text
DATA
HEADERS
SETTINGS
WINDOW_UPDATE
RST_STREAM
PING
GOAWAY
```

Ví dụ:

```text
Connection
    │
    ├── SETTINGS
    ├── HEADERS
    ├── DATA
    ├── DATA
    └── ...
```

Đây là một lý do HTTP/2 có thể được fingerprint.

---

# 4. Browser không chỉ "dùng HTTP/2"

Hai browser đều có thể:

```text
HTTP/2
```

nhưng cách chúng khởi tạo và sử dụng HTTP/2 có thể khác.

Ví dụ:

```text
Chrome
 ├── SETTINGS
 ├── SETTINGS order
 ├── pseudo-header order
 └── connection behavior
```

Firefox:

```text
Firefox
 ├── SETTINGS khác
 ├── order khác
 ├── pseudo-header order khác
 └── behavior khác
```

Do đó:

```text
HTTP/2
```

chỉ là protocol.

Còn:

```text
HTTP/2 fingerprint
```

là đặc điểm cụ thể của client khi sử dụng protocol đó.

---

# 5. ALPN nối TLS với HTTP/2

Ở Buổi 25 chúng ta đã gặp:

```text
ALPN
```

ALPN = Application-Layer Protocol Negotiation.

Có thể hình dung:

```text
Client
  │
  │ TLS ClientHello
  │
  │ ALPN:
  │   h2
  │   http/1.1
  ▼
Server
```

Server và client thương lượng protocol.

Nếu kết quả là:

```text
h2
```

thì connection sử dụng HTTP/2.

---

# 6. Mô hình hoàn chỉnh

```text
Python
  │
  ▼
primp
  │
  ▼
TCP
  │
  ▼
TLS
  │
  ├── ClientHello
  ├── TLS fingerprint
  └── ALPN
        │
        ▼
       h2
        │
        ▼
     HTTP/2
        │
        ├── SETTINGS
        ├── HEADERS
        ├── DATA
        └── ...
```

Vì vậy:

```text
TLS fingerprint
```

và:

```text
HTTP/2 fingerprint
```

là hai lớp khác nhau nhưng liên quan với nhau.

---

# 7. HTTP/2 Multiplexing

Đây là một ưu điểm lớn.

HTTP/1.1 có thể hình dung:

```text
Connection
   │
   ├── Request 1
   │     ↓
   │   Response
   │
   ├── Request 2
   │     ↓
   │   Response
```

HTTP/2:

```text
Connection
   │
   ├── Stream 1 → Request A
   ├── Stream 3 → Request B
   ├── Stream 5 → Request C
   └── Stream 7 → Request D
```

Các stream có thể cùng tồn tại trên một connection.

Điều này đặc biệt quan trọng khi sau này chúng ta học:

```text
AsyncClient
Concurrent Requests
Semaphore
```

trong Phần IV.

---

# 8. Stream là gì?

Trong HTTP/2, mỗi request/response exchange có thể được gắn với một:

```text
Stream ID
```

Ví dụ:

```text
Stream 1
    GET /novel/abc

Stream 3
    GET /chapter/1

Stream 5
    GET /chapter/2
```

Tất cả có thể chạy trên cùng một HTTP/2 connection.

---

# 9. SETTINGS frame

Đây là phần **rất quan trọng đối với fingerprint**.

Khi HTTP/2 connection bắt đầu, client gửi:

```text
SETTINGS
```

Frame này chứa các thiết lập HTTP/2.

`primp` hiện có `SettingId` cho các setting như:

```text
HEADER_TABLE_SIZE
ENABLE_PUSH
MAX_CONCURRENT_STREAMS
INITIAL_WINDOW_SIZE
MAX_FRAME_SIZE
MAX_HEADER_LIST_SIZE
ENABLE_CONNECT_PROTOCOL
NO_RFC7540_PRIORITIES
```

([Docs.rs][2])

---

# 10. Ví dụ SETTINGS

Có thể hình dung:

```text
SETTINGS
├── HEADER_TABLE_SIZE = ...
├── ENABLE_PUSH = ...
├── MAX_CONCURRENT_STREAMS = ...
├── INITIAL_WINDOW_SIZE = ...
├── MAX_FRAME_SIZE = ...
└── MAX_HEADER_LIST_SIZE = ...
```

Browser A có thể gửi:

```text
A
B
C
D
E
```

Browser B:

```text
A
C
B
D
E
```

Không chỉ giá trị mà **thứ tự** cũng có thể là một đặc điểm được quan sát.

---

# 11. `SettingsOrder`

Đây là lý do source `primp` có:

```text
SettingsOrder
SettingsOrderBuilder
```

Tài liệu của `primp` mô tả `SettingsOrder` là thứ tự các setting trong SETTINGS frame; builder còn cho phép xây dựng thứ tự này. ([Docs.rs][3])

Mô hình:

```text
Browser Profile
      │
      ▼
HTTP/2 Settings
      │
      ▼
SettingsOrder
      │
      ▼
SETTINGS frame
```

---

# 12. Tại sao order lại quan trọng?

Nếu chỉ nhìn:

```text
A
B
C
D
```

ta có thể nghĩ:

```text
A B C D
```

và:

```text
D C B A
```

giống nhau vì chứa cùng dữ liệu.

Nhưng fingerprinting có thể quan tâm đến:

```text
value
+
order
+
behavior
```

Do đó:

```text
Settings
```

không chỉ là dictionary.

Nó còn có:

```text
ordering
```

---

# 13. Pseudo-Headers

HTTP/2 có một khái niệm rất quan trọng:

```text
Pseudo-headers
```

Ví dụ:

```text
:method
:scheme
:authority
:path
```

Đây không phải HTTP header bình thường.

Chúng bắt đầu bằng:

```text
:
```

Ví dụ request:

```text
:method: GET
:scheme: https
:authority: example.com
:path: /chapter/1
```

---

# 14. Pseudo-header order

Một HTTP/2 request có thể có:

```text
:method
:scheme
:authority
:path
```

Thứ tự này có thể được quan sát.

`primp` có `PseudoOrder` để biểu diễn thứ tự các HTTP/2 pseudo-header fields trong header block. ([Docs.rs][1])

Mô hình:

```text
HTTP/2 HEADERS
       │
       ├── :method
       ├── :scheme
       ├── :authority
       └── :path
```

---

# 15. Vì sao pseudo-header order liên quan fingerprint?

Giả sử:

```text
Client A
:method
:scheme
:authority
:path
```

Client B:

```text
:method
:path
:authority
:scheme
```

Nếu một client/browser luôn tạo header block theo một pattern nhất định, pattern đó có thể trở thành một tín hiệu fingerprint.

Tài liệu `primp` hiện có hẳn `PseudoOrder` và `PseudoOrderBuilder` cho mục đích cấu hình thứ tự này. ([Docs.rs][1])

---

# 16. `primp` Browser Profile

Đây là điểm quan trọng nhất của buổi học.

Khi bạn viết:

```python
import primp

client = primp.Client(
    impersonate="chrome_146"
)
```

không nên hiểu:

```text
Chrome 146
     ↓
User-Agent
```

Mà hãy hiểu:

```text
Chrome 146
      │
      ▼
Browser Settings
      │
 ┌────┼────────┐
 ▼    ▼        ▼
TLS  HTTP/2  Headers
```

Source hiện tại của `primp` mô tả `BrowserSettings` là cấu hình TLS và HTTP/2 để impersonate browser version; `get_browser_settings` resolve TLS/HTTP2/headers theo browser version và OS. ([Docs.rs][1])

---

# 17. Test HTTP/2 bằng `primp`

Ta tiếp tục dùng:

```text
https://tls.peet.ws/api/all
```

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

Trong output, tìm thông tin liên quan đến:

```text
HTTP version
TLS
HTTP/2
headers
```

**Không nên hard-code schema của endpoint**, vì đây là dịch vụ bên ngoài và response có thể thay đổi.

---

# 18. Test nhiều browser

```python
import primp


URL = "https://tls.peet.ws/api/all"


PROFILES = [
    "chrome_146",
    "firefox_146",
    "edge_146",
    "safari_26",
]


def main():
    for profile in PROFILES:

        client = primp.Client(
            impersonate=profile,
            impersonate_os="windows",
        )

        response = client.get(URL)

        print("=" * 80)
        print(profile)
        print("=" * 80)
        print(response.text)
        print()


if __name__ == "__main__":
    main()
```

Mục tiêu:

```text
Chrome
Firefox
Edge
Safari
```

không chỉ khác User-Agent.

Browser profile của `primp` được thiết kế để mô phỏng cả TLS và HTTP/2 characteristics. ([Docs.rs][1])

---

# 19. Edge là một ví dụ thú vị

Ở Buổi 23 ta đã nói:

```text
Edge
```

dựa trên Chromium.

Nhưng không nên suy ra:

```text
Edge = Chrome
```

hoàn toàn.

Tài liệu `primp` ghi rõ Edge sử dụng Chrome-based TLS/HTTP2 nhưng có Edge-specific headers. ([Docs.rs][1])

Có thể hình dung:

```text
Chrome
 ├── TLS
 ├── HTTP/2
 └── Chrome headers

Edge
 ├── Chrome-based TLS
 ├── Chrome-based HTTP/2
 └── Edge-specific headers
```

---

# 20. HTTP/2 Fingerprint gồm những gì?

Ở mức học hiện tại, hãy nhớ:

```text
HTTP/2 Fingerprint
│
├── SETTINGS
├── SETTINGS values
├── SETTINGS order
├── pseudo-header order
├── connection behavior
└── các đặc điểm HTTP/2 khác
```

Không nên định nghĩa cứng:

```text
HTTP/2 fingerprint = SETTINGS
```

vì như vậy quá đơn giản.

---

# 21. HTTP/2 không phải chỉ là Header

Sai lầm:

```text
HTTP/2 fingerprint
=
HTTP headers
```

Không.

Ta có:

```text
HTTP/2
│
├── Frames
├── Streams
├── SETTINGS
├── Flow control
├── HPACK
├── Pseudo-headers
└── Header encoding
```

Trong đó một số behavior có thể trở thành tín hiệu fingerprint.

---

# 22. HPACK

HTTP/2 sử dụng:

```text
HPACK
```

để nén header.

Ý tưởng:

```text
Headers
   ↓
HPACK compression
   ↓
Binary representation
```

Nó giúp giảm lượng dữ liệu truyền đi.

Ta chưa cần đi sâu vào thuật toán HPACK hôm nay.

Chỉ cần nhớ:

```text
HTTP/2
   ↓
Header compression
   ↓
HPACK
```

Sau này nếu muốn đi sâu network protocol, đây là một topic riêng.

---

# 23. Flow Control

HTTP/2 cũng có flow control.

Ví dụ:

```text
Client
  │
  │ DATA
  ▼
Server
```

Có window giới hạn lượng dữ liệu có thể gửi trước khi nhận thêm quyền gửi.

Liên quan đến:

```text
WINDOW_UPDATE
```

Đây cũng là một phần của HTTP/2 behavior.

---

# 24. HTTP/2 + concurrency

Đây là phần đặc biệt quan trọng với Novel Crawler.

Giả sử cần tải:

```text
chapter 1
chapter 2
chapter 3
chapter 4
```

HTTP/1.1:

```text
Connection A
 └── Request 1

Connection B
 └── Request 2

Connection C
 └── Request 3
```

HTTP/2 có thể:

```text
Connection A
 ├── Stream 1 → Chapter 1
 ├── Stream 3 → Chapter 2
 ├── Stream 5 → Chapter 3
 └── Stream 7 → Chapter 4
```

Đây là một lý do HTTP/2 rất quan trọng khi chúng ta bước sang:

```text
Part IV
Async + Crawler
```

---

# 25. Nhưng HTTP/2 không đồng nghĩa "gửi vô hạn request"

Đây là lỗi rất dễ mắc.

Có:

```text
multiplexing
```

không có nghĩa:

```text
unlimited concurrency
```

Server có thể giới hạn:

```text
MAX_CONCURRENT_STREAMS
```

Đây là một HTTP/2 SETTINGS parameter được `primp` mô hình hóa trong `SettingId`. ([Docs.rs][2])

Vì vậy sau này chúng ta vẫn cần:

```text
Semaphore
Rate Limiter
Concurrency limit
```

---

# 26. HTTP/2 và Rate Limiting

Trong Novel Crawler:

```text
HTTP/2
   +
Concurrency
   +
Rate Limiting
```

phải được thiết kế cùng nhau.

Ví dụ:

```text
100 chapters
     ↓
HTTP/2
     ↓
20 concurrent streams
     ↓
Rate limiter
     ↓
Fetcher
```

Không phải:

```text
100 chapters
     ↓
100 requests ngay lập tức
```

---

# 27. Một misconception rất nguy hiểm

Không nên nghĩ:

```text
HTTP/2 fingerprint giống Chrome
      ↓
website sẽ không phát hiện crawler
```

Không.

Fingerprint chỉ là **một tín hiệu**.

Server còn có thể quan sát:

```text
IP
Proxy
Cookies
Request frequency
URL behavior
TLS
HTTP/2
Headers
Response behavior
Authentication
...
```

Vì vậy browser impersonation không phải một "bypass anti-bot guarantee".

`primp` cũng tự mô tả mình là HTTP client có browser impersonation capabilities, không phải browser automation thực sự. ([PyPI][4])

---

# 28. Đừng random HTTP/2 profile mỗi request

Sai:

```text
Request 1 → Chrome HTTP/2
Request 2 → Firefox HTTP/2
Request 3 → Chrome HTTP/2
```

Tốt hơn:

```text
Session
   │
   └── BrowserProfile
          │
          ├── Chrome 146
          ├── Windows
          ├── TLS profile
          └── HTTP/2 profile
```

và giữ ổn định trong lifecycle của client.

Điều này khớp với những gì chúng ta đã học ở:

```text
Buổi 16 — Connection Reuse
Buổi 20 — Client Lifecycle
Buổi 24 — Browser + OS
```

---

# 29. Kiến trúc BrowserProfile hiện tại

Ta có thể mở rộng abstraction trước đây:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserProfile:
    browser: str
    version: str
    os: str
```

Ví dụ:

```python
profile = BrowserProfile(
    browser="chrome",
    version="146",
    os="windows",
)
```

Nhưng **không cần thêm**:

```python
tls_fingerprint: ...
http2_fingerprint: ...
ja3: ...
ja4: ...
```

Tại sao?

Vì những chi tiết đó đã được `primp` profile quản lý.

Ta chỉ nói:

```text
Chrome 146 + Windows
```

và Infrastructure:

```text
        BrowserProfile
              ↓
          primp.Client
              ↓
      ┌───────┼───────┐
      ↓       ↓       ↓
     TLS    HTTP/2  Headers
```

---

# 30. Clean Architecture

Kiến trúc Novel Crawler:

```text
┌─────────────────────────────┐
│        Application          │
│                             │
│      CrawlChapter           │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       Fetcher Interface     │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       Infrastructure        │
│                             │
│       PrimpFetcher          │
│            │                │
│            ▼                │
│       BrowserProfile        │
│            │                │
│            ▼                │
│       primp.Client          │
└─────────────────────────────┘
```

Application không cần biết:

```text
SETTINGS
HPACK
ALPN
ClientHello
PseudoOrder
```

Đó là Infrastructure concern.

---

# 31. Một `PrimpFetcher` nhỏ

Ở thời điểm hiện tại:

```python
import primp


class PrimpFetcher:

    def __init__(
        self,
        profile: str = "chrome_146",
        os: str = "windows",
    ):
        self.client = primp.Client(
            impersonate=profile,
            impersonate_os=os,
        )

    def get(self, url: str):
        return self.client.get(url)
```

Sử dụng:

```python
fetcher = PrimpFetcher(
    profile="chrome_146",
    os="windows",
)

response = fetcher.get(
    "https://example.com"
)

print(response.status_code)
```

Đây vẫn là abstraction đủ nhỏ.

---

# 32. Bài thực hành 1 — Quan sát HTTP/2

Tạo:

```text
lesson_26_01.py
```

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

Tìm trong output:

```text
HTTP version
TLS
headers
```

---

# 33. Bài thực hành 2 — So sánh browser profiles

```python
import primp


URL = "https://tls.peet.ws/api/all"


PROFILES = [
    "chrome_146",
    "firefox_146",
    "edge_146",
    "safari_26",
]


def main():
    for profile in PROFILES:

        client = primp.Client(
            impersonate=profile,
            impersonate_os="windows",
        )

        response = client.get(URL)

        print("=" * 80)
        print(f"PROFILE: {profile}")
        print("=" * 80)
        print(response.text)
        print()


if __name__ == "__main__":
    main()
```

Mục tiêu không phải ghi nhớ output.

Mục tiêu là hiểu:

```text
profile
   ↓
BrowserSettings
   ├── TLS
   ├── HTTP/2
   └── Headers
```

---

# 34. Bài thực hành 3 — Browser + OS

```python
import primp


URL = "https://tls.peet.ws/api/all"


PROFILES = [
    ("chrome_146", "windows"),
    ("chrome_146", "macos"),
    ("chrome_146", "linux"),
]


def main():
    for browser, os in PROFILES:

        client = primp.Client(
            impersonate=browser,
            impersonate_os=os,
        )

        response = client.get(URL)

        print("=" * 80)
        print(f"{browser} + {os}")
        print("=" * 80)

        print(response.text)


if __name__ == "__main__":
    main()
```

---

# 35. Bài thực hành 4 — Tự thiết kế Profile

Tạo:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserProfile:
    browser: str
    version: str
    os: str


profiles = [
    BrowserProfile(
        browser="chrome",
        version="146",
        os="windows",
    ),
    BrowserProfile(
        browser="firefox",
        version="146",
        os="windows",
    ),
]
```

Sau đó viết:

```python
def to_primp_kwargs(
    profile: BrowserProfile,
) -> dict:
    ...
```

Kết quả mong muốn:

```python
{
    "impersonate": "chrome_146",
    "impersonate_os": "windows",
}
```

và:

```python
{
    "impersonate": "firefox_146",
    "impersonate_os": "windows",
}
```

---

# 36. Tại sao bài này quan trọng với roadmap?

Chúng ta đang xây dần:

```text
BrowserClient
```

Nhưng chưa xây ngay.

Hiện tại kiến thức đã có:

```text
21  Impersonation
22  Chrome
23  Browser families
24  OS
25  TLS
26  HTTP/2
```

Tiếp theo:

```text
27  Headers + Fingerprint
28  Fingerprint thực tế
29  httpx vs primp
30  BrowserClient
```

Nghĩa là Buổi 26 hoàn thiện thêm một mảnh quan trọng:

```text
Browser Profile
│
├── Browser
├── Version
├── OS
├── TLS
└── HTTP/2
```

---

# 37. Tổng kết Buổi 26

Hãy ghi nhớ mô hình này:

```text
                 Browser Profile
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
         TLS         HTTP/2       Headers
          │            │            │
          ▼            ▼            ▼
      ClientHello   SETTINGS     HTTP fields
          │            │
          ▼            ▼
    TLS Fingerprint  H2 Fingerprint
```

Và HTTP/2:

```text
HTTP/2
│
├── Binary Frames
├── Streams
├── Multiplexing
├── SETTINGS
├── Pseudo-Headers
├── HPACK
├── Flow Control
└── HTTP/2 behavior
```

Đặc biệt:

```text
SETTINGS
    +
SETTINGS order
    +
Pseudo-header order
    +
HTTP/2 behavior
```

là những khái niệm quan trọng khi nói về HTTP/2 fingerprint. `primp` hiện có các cấu trúc riêng để mô hình hóa SETTINGS order và pseudo-header order, cho thấy đây là một phần có chủ đích trong browser impersonation của thư viện. ([Docs.rs][1])

### Roadmap

```text
PHẦN III — BROWSER IMPERSONATION

21. Vì sao cần impersonation       ✅
22. Chrome fingerprint              ✅
23. Firefox / Safari / Edge         ✅
24. impersonate_os                   ✅
25. TLS fingerprint                  ✅
26. HTTP/2                           ✅
27. Headers + fingerprint            ← tiếp theo
28. Fingerprint thực tế
29. So sánh httpx vs primp
30. Xây BrowserClient
```

**Buổi 27** chúng ta sẽ ghép ba lớp thành một vấn đề thực tế:

```text
Headers
   +
TLS
   +
HTTP/2
   ↓
Fingerprint consistency
```

và đặc biệt phân tích **tại sao tự sửa `User-Agent`, `Accept-Language`, `Sec-CH-UA-*` sau khi chọn `impersonate` có thể làm browser persona trở nên không nhất quán**.

[1]: https://docs.rs/primp/latest/primp/imp/index.html?utm_source=chatgpt.com "primp::imp - Rust"
[2]: https://docs.rs/primp/latest/primp/enum.SettingId.html?utm_source=chatgpt.com "SettingId in primp - Rust"
[3]: https://docs.rs/primp/latest/primp/struct.SettingsOrderBuilder.html?utm_source=chatgpt.com "SettingsOrderBuilder in primp - Rust"
[4]: https://pypi.org/project/primp/2.0.1/?utm_source=chatgpt.com "primp · PyPI"
