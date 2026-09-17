# Phần III — Browser Impersonation

# Buổi 27 — Headers + Fingerprint

Ở Buổi 25 và 26, chúng ta đã có:

```text
TLS Fingerprint
        +
HTTP/2 Fingerprint
```

Hôm nay thêm lớp thứ ba:

```text
Headers
   +
TLS
   +
HTTP/2
   ↓
Fingerprint Consistency
```

Đây là bài rất quan trọng, vì **browser impersonation không chỉ là chọn `User-Agent`**.

Tài liệu hiện tại của `primp 2.0.1` mô tả browser impersonation là cấu hình **TLS + HTTP/2 + default headers**, và mỗi browser profile ánh xạ tới fingerprint/configuration tương ứng. ([Docs.rs][1])

---

# 1. Nhìn lại toàn bộ Browser Persona

Đến đây ta có:

```text
                 Browser Profile
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
        TLS          HTTP/2       Headers
          │            │            │
          ▼            ▼            ▼
    TLS fingerprint  H2 behavior  HTTP identity
```

Hay:

```text
Chrome 146 + Windows
          │
          ├── TLS
          ├── HTTP/2
          └── Headers
```

Mục tiêu không phải làm cho từng lớp "trông giống Chrome" một cách độc lập.

Mục tiêu là:

> **Các lớp phải mô tả một persona nhất quán.**

---

# 2. Ví dụ đơn giản nhất

Ta có:

```python
import primp

client = primp.Client(
    impersonate="chrome_146",
)
```

`primp` sẽ sử dụng browser profile tương ứng.

Theo tài liệu hiện tại, profile chứa:

```text
Chrome 146
    ├── TLS configuration
    ├── HTTP/2 configuration
    └── default headers
```

([Docs.rs][1])

Do đó không nên hiểu:

```text
impersonate="chrome_146"
        ↓
User-Agent = Chrome
```

mà:

```text
impersonate="chrome_146"
        ↓
BrowserSettings
    ├── TLS
    ├── HTTP/2
    └── Headers
```

---

# 3. Headers nằm ở tầng nào?

Ta có:

```text
Application
    ↓
HTTP
    ↓
Headers
```

Ví dụ:

```http
User-Agent: ...
Accept: text/html
Accept-Language: vi-VN
```

Trong khi:

```text
TLS
```

xảy ra trước HTTP.

Mô hình:

```text
TCP
 ↓
TLS
 ↓
HTTP/2
 ↓
HTTP Headers
```

Vì vậy:

```text
User-Agent
```

không thể thay đổi:

```text
TLS ClientHello
```

---

# 4. Vì sao chỉ đổi User-Agent là chưa đủ?

Ví dụ:

```python
import primp

client = primp.Client(
    headers={
        "User-Agent": "Chrome ..."
    }
)
```

Bạn chỉ đang nói:

```text
HTTP Header
    ↓
Chrome-like
```

Nhưng bên dưới vẫn có:

```text
TLS
HTTP/2
```

của client.

Do đó:

```text
User-Agent = Chrome
```

không đồng nghĩa:

```text
TLS = Chrome
HTTP/2 = Chrome
```

---

# 5. `primp` giải quyết vấn đề này thế nào?

Khi chọn:

```python
client = primp.Client(
    impersonate="chrome_146"
)
```

profile được dùng để cấu hình nhiều lớp.

Tài liệu source của `primp` hiện mô tả:

```text
BrowserSettings
├── TLS
└── HTTP/2
```

và profile `Impersonate` ánh xạ tới TLS fingerprint + default headers. Hàm `get_browser_settings` resolve browser settings theo browser version và OS. ([Docs.rs][1])

Có thể hình dung:

```text
"chrome_146"
      │
      ▼
Browser Profile
      │
 ┌────┼────┐
 ▼    ▼    ▼
TLS  H2  Headers
```

---

# 6. Headers của Browser Profile

Các browser profile thực tế có thể chứa các header như:

```text
User-Agent
Accept
Accept-Encoding
Accept-Language
Sec-CH-UA
Sec-CH-UA-Mobile
Sec-CH-UA-Platform
Sec-Fetch-*
Upgrade-Insecure-Requests
...
```

Source của các browser impersonation profile cho thấy những header như `sec-ch-ua`, `sec-ch-ua-mobile`, `sec-ch-ua-platform`, `User-Agent`, `Accept`, `Sec-Fetch-*` được cấu hình cùng browser profile. ([Docs.rs][2])

---

# 7. `Sec-CH-UA` là gì?

Chrome có nhóm Client Hints.

Ví dụ:

```text
Sec-CH-UA
```

có thể mô tả browser brands/version.

Ví dụ minh họa:

```http
Sec-CH-UA: "Chromium";v="..."
```

Cùng với:

```text
Sec-CH-UA-Mobile
Sec-CH-UA-Platform
```

Những header này khiến việc tự tay thay đổi `User-Agent` càng dễ tạo inconsistency.

---

# 8. Ví dụ inconsistency

Giả sử:

```python
client = primp.Client(
    impersonate="chrome_146",
    impersonate_os="windows",
)
```

Profile có persona:

```text
Chrome 146
Windows
```

Sau đó ta tự override:

```python
headers = {
    "User-Agent": "Firefox/146"
}
```

Ta tạo:

```text
User-Agent → Firefox
TLS         → Chrome
HTTP/2      → Chrome
Client Hints → Chrome
```

Persona trở nên mâu thuẫn.

```text
             ❌
       Browser Persona
              │
      ┌───────┼────────┐
      ▼       ▼        ▼
   Firefox   Chrome   Chrome
     UA       TLS      H2
```

Đây chính là điều cần tránh.

---

# 9. Một ví dụ còn tệ hơn

```python
client = primp.Client(
    impersonate="chrome_146",
    impersonate_os="windows",
)
```

nhưng request:

```python
client.get(
    url,
    headers={
        "User-Agent": "Safari",
        "Sec-CH-UA-Platform": '"macOS"',
        "Accept-Language": "ja-JP",
    },
)
```

Ta đã tạo:

```text
TLS          → Chrome
HTTP/2       → Chrome
User-Agent   → Safari
Platform     → macOS
Language     → Japanese
OS profile   → Windows
```

Không phải một browser persona rõ ràng.

---

# 10. Không phải custom header nào cũng sai

Điều này cũng rất quan trọng.

Không nên hiểu:

> "Dùng impersonation thì tuyệt đối không được thêm header."

Không đúng.

Có những header thuộc **request context**.

Ví dụ:

```text
Referer
Authorization
Cookie
```

có thể phụ thuộc vào request cụ thể.

Ví dụ Novel Crawler:

```python
response = client.get(
    chapter_url,
    headers={
        "Referer": novel_url,
    },
)
```

Đây có thể là request-specific information, không nhất thiết phá browser persona.

---

# 11. Phân loại Headers

Ta có thể chia thành hai nhóm.

## Nhóm A — Browser-profile headers

```text
User-Agent
Sec-CH-UA
Sec-CH-UA-Mobile
Sec-CH-UA-Platform
Sec-Fetch-*
Accept
Accept-Encoding
...
```

Đây là những header nên đặc biệt cẩn thận khi override.

---

## Nhóm B — Request-context headers

Ví dụ:

```text
Referer
Authorization
Cookie
```

Những header này có thể thay đổi theo request/session.

Mô hình:

```text
Browser Profile
       │
       └── Stable headers

Request
       │
       └── Context-specific headers
```

---

# 12. Default Headers vs Request Headers

Đây chính là kiến thức Buổi 17 + Buổi 19.

Ta có:

```text
Client
 │
 └── default headers
```

và:

```text
Request
 │
 └── request headers
```

Ví dụ:

```python
client = primp.Client(
    impersonate="chrome_146",
    headers={
        "Accept-Language": "vi-VN,vi;q=0.9",
    },
)
```

Sau đó:

```python
response = client.get(
    url,
    headers={
        "Referer": novel_url,
    },
)
```

Ý tưởng:

```text
Client defaults
      +
Request-specific
      ↓
Final request
```

---

# 13. Nhưng `Accept-Language` cũng cần suy nghĩ

Giả sử:

```text
Browser Profile
    Chrome + Windows
```

và ta đặt:

```http
Accept-Language: ja-JP
```

Không nhất thiết sai về mặt protocol.

Một người dùng Chrome Windows hoàn toàn có thể dùng Japanese.

Nhưng nếu bạn đang cố mô hình hóa một persona cụ thể, thì:

```text
Browser
OS
Language
Region
```

cũng nên có chủ ý.

Không nên random:

```text
Windows
+
Japanese
+
Vietnamese IP
+
Safari UA
```

mà không có lý do.

---

# 14. Browser Fingerprint là nhiều tín hiệu

Ta có:

```text
Browser Identity
│
├── Browser
├── Version
├── OS
├── TLS
├── HTTP/2
├── Headers
├── Cookies
├── IP
└── Request behavior
```

Trong đó:

```text
TLS + HTTP/2 + Headers
```

là trọng tâm của `primp` browser impersonation.

Còn:

```text
Cookies
IP
Request behavior
```

không phải thứ `impersonate` tự động giải quyết.

---

# 15. Cookies cũng ảnh hưởng session identity

Ví dụ:

```text
Session A
    Browser = Chrome
    OS = Windows
    Cookies = X
```

Sau đó:

```text
Request 1 → Chrome + Windows + Cookies X
Request 2 → Chrome + Windows + Cookies X
Request 3 → Chrome + Windows + Cookies X
```

hợp lý hơn việc thay đổi browser profile giữa từng request.

Đây liên kết trực tiếp với Buổi 9:

```text
Cookies
```

và Buổi 20:

```text
Client Lifecycle
```

---

# 16. IP/Proxy cũng là một signal

Ta có:

```text
Browser Persona
       +
IP
       +
Cookies
       +
Request behavior
```

Ví dụ:

```text
Chrome Windows
+
Proxy A
```

rồi ngay lập tức:

```text
Chrome Windows
+
Proxy B ở quốc gia khác
```

không nhất thiết sai, nhưng đó là một thay đổi session/network context cần được thiết kế có chủ ý.

Đây là lý do sau này:

```text
ProxyPool
```

sẽ là một abstraction riêng.

---

# 17. Browser Profile không nên chứa tất cả mọi thứ

Không nên thiết kế:

```python
@dataclass
class BrowserProfile:
    browser: str
    version: str
    os: str
    proxy: str
    cookie: dict
    retry: int
    timeout: float
    rate_limit: float
```

Đây là **God Object**.

Tốt hơn:

```text
BrowserProfile
    ├── browser
    ├── version
    └── os

ProxyConfig
    └── proxy

RequestOptions
    ├── timeout
    ├── params
    └── request headers

RetryPolicy
    └── retry behavior
```

Đúng với hướng DDD/SOLID mà bạn đang học.

---

# 18. Browser Profile trong Infrastructure

Ta có:

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

Infrastructure:

```python
import primp


def create_client(profile: BrowserProfile):
    return primp.Client(
        impersonate=(
            f"{profile.browser}_{profile.version}"
        ),
        impersonate_os=profile.os,
    )
```

---

# 19. Đừng hard-code Headers để "sửa" fingerprint

Ví dụ không nên:

```python
client = primp.Client(
    impersonate="chrome_146",
    headers={
        "User-Agent": "...",
        "Sec-CH-UA": "...",
        "Sec-CH-UA-Platform": "...",
    },
)
```

trừ khi bạn **thực sự biết** tại sao cần override.

Bởi vì bạn đang bắt đầu tự quản lý một phần mà browser profile đã quản lý.

Nguyên tắc:

> **Hãy để `impersonate` quản lý browser identity trước; chỉ override khi có yêu cầu cụ thể.**

---

# 20. Test: xem headers thực tế

Dùng:

```text
https://httpbin.org/headers
```

Ví dụ:

```python
import primp


def main():
    client = primp.Client(
        impersonate="chrome_146",
        impersonate_os="windows",
    )

    response = client.get(
        "https://httpbin.org/headers"
    )

    print(response.text)


if __name__ == "__main__":
    main()
```

Ta có thể quan sát các headers mà server nhìn thấy.

---

# 21. Test Browser Profile vs Manual UA

```python
import primp


URL = "https://httpbin.org/headers"


def main():

    profile_client = primp.Client(
        impersonate="chrome_146",
        impersonate_os="windows",
    )

    manual_client = primp.Client(
        headers={
            "User-Agent": "Mozilla/5.0 Chrome/146",
        }
    )

    print("=" * 80)
    print("PROFILE")
    print("=" * 80)

    print(
        profile_client.get(URL).text
    )

    print("=" * 80)
    print("MANUAL USER-AGENT")
    print("=" * 80)

    print(
        manual_client.get(URL).text
    )


if __name__ == "__main__":
    main()
```

Điều cần hiểu:

```text
Manual UA
    ↓
chỉ thay đổi một phần HTTP identity
```

Trong khi:

```text
impersonate
    ↓
browser profile
    ├── TLS
    ├── HTTP/2
    └── default headers
```

([Docs.rs][1])

---

# 22. Test một profile nhưng override UA

Đây là bài rất đáng làm.

```python
import primp


URL = "https://httpbin.org/headers"


def main():

    client = primp.Client(
        impersonate="chrome_146",
        impersonate_os="windows",
    )

    response = client.get(
        URL,
        headers={
            "User-Agent": "MyCrawler/1.0",
        },
    )

    print(response.text)


if __name__ == "__main__":
    main()
```

Server sẽ nhìn thấy UA do request cung cấp.

Nhưng:

```text
TLS
HTTP/2
Sec-CH-UA
...
```

vẫn có thể đến từ browser profile.

Đó chính là ví dụ về:

```text
❌ persona inconsistency
```

nếu mục tiêu của bạn là mô phỏng Chrome nguyên bản.

---

# 23. Không phải inconsistency nào cũng có thể nhìn thấy bằng `httpbin`

Đây là điểm rất quan trọng.

```text
httpbin
```

chủ yếu cho bạn xem HTTP request.

Nó không phải công cụ đầy đủ để kiểm tra:

```text
TLS ClientHello
HTTP/2 SETTINGS
pseudo-header ordering
```

Muốn quan sát network fingerprint, endpoint như:

```text
https://tls.peet.ws/api/all
```

hữu ích hơn.

Vì vậy:

```text
httpbin
   ↓
HTTP headers

tls.peet.ws
   ↓
TLS + HTTP/network information
```

---

# 24. Bài test toàn diện

Tạo:

```text
lesson_27.py
```

```python
import primp


TLS_URL = "https://tls.peet.ws/api/all"
HEADERS_URL = "https://httpbin.org/headers"


def main():

    client = primp.Client(
        impersonate="chrome_146",
        impersonate_os="windows",
    )

    print("=" * 80)
    print("HTTP HEADERS")
    print("=" * 80)

    response = client.get(HEADERS_URL)
    print(response.text)

    print()
    print("=" * 80)
    print("TLS / HTTP2")
    print("=" * 80)

    response = client.get(TLS_URL)
    print(response.text)


if __name__ == "__main__":
    main()
```

Đây là bài test rất tốt để hình dung:

```text
                 Chrome 146
                     │
                  Windows
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
       HTTP                    TLS/H2
          │                     │
       Headers              Fingerprint
```

---

# 25. `Referer` là ví dụ tốt của Request Context

Trong Novel Crawler, giả sử:

```text
Novel page
    ↓
Chapter page
```

Ta có:

```python
response = client.get(
    chapter_url,
    headers={
        "Referer": novel_url,
    },
)
```

Đây là header có ý nghĩa **request context**.

Ta không cần biến:

```text
Referer
```

thành một phần cố định của browser fingerprint.

---

# 26. `Authorization` cũng vậy

Ví dụ API:

```python
response = client.get(
    url,
    headers={
        "Authorization": f"Bearer {token}",
    },
)
```

`Authorization` thuộc:

```text
Authentication
```

chứ không phải:

```text
Chrome fingerprint
```

Do đó kiến trúc:

```text
BrowserProfile
Authentication
RequestOptions
```

nên tách nhau.

---

# 27. `Cookie` cũng không nên hard-code vào BrowserProfile

Sai:

```python
@dataclass
class BrowserProfile:
    browser: str
    version: str
    os: str
    cookies: dict
```

Tốt hơn:

```text
BrowserProfile
       │
       ├── Chrome 146
       └── Windows

Client Session
       │
       └── Cookies
```

Cookie thuộc session state.

---

# 28. Browser Profile + RequestOptions

Đây là kiến trúc đẹp hơn:

```python
from dataclasses import dataclass, field


@dataclass(frozen=True)
class BrowserProfile:
    browser: str
    version: str
    os: str


@dataclass
class RequestOptions:
    headers: dict[str, str] = field(
        default_factory=dict
    )
    params: dict = field(
        default_factory=dict
    )
    timeout: float | None = None
```

Khi request:

```text
Application
     │
     ├── BrowserProfile
     │
     └── RequestOptions
              │
              ▼
          PrimpFetcher
              │
              ▼
          primp.Client
```

---

# 29. Merge Headers cẩn thận

Ví dụ:

```python
default_headers = {
    "Accept-Language": "vi-VN",
}
```

request:

```python
request_headers = {
    "Referer": "https://example.com",
}
```

merge:

```python
final_headers = default_headers.copy()
final_headers.update(request_headers)
```

Kết quả:

```python
{
    "Accept-Language": "vi-VN",
    "Referer": "https://example.com",
}
```

Nhưng nếu:

```python
request_headers = {
    "User-Agent": "Firefox..."
}
```

thì bạn đã override một phần browser identity.

Đây là lý do API abstraction không nên khuyến khích override tùy tiện.

---

# 30. Một `PrimpFetcher` hợp lý

Ở mức hiện tại:

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

    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict | None = None,
        timeout: float | None = None,
    ):
        return self.client.get(
            url,
            headers=headers,
            params=params,
            timeout=timeout,
        )
```

Đây chưa phải `Production Fetcher`.

Chúng ta vẫn còn:

```text
Retry
Proxy
Rate Limit
Error Classification
Logging
```

ở Phần IV/V.

---

# 31. Một nguyên tắc SOLID rất hay ở đây

`PrimpFetcher` không nên chịu trách nhiệm:

```text
Parser
Retry policy
Proxy pool
Rate limiter
Browser profile generation
```

Tách concern:

```text
PrimpFetcher
    ↓
HTTP transport

BrowserProfile
    ↓
Browser identity

RetryPolicy
    ↓
Retry behavior

ProxyStrategy
    ↓
Proxy selection

RateLimiter
    ↓
Request pacing
```

Sau này:

```text
PrimpFetcher
      │
      ├── BrowserProfile
      ├── ProxyStrategy
      ├── RetryPolicy
      └── RateLimiter
```

Đó chính là composition.

---

# 32. Một misconception quan trọng

Không nên nói:

> "Fingerprint giống Chrome thì server không biết đây là crawler."

Không có cơ sở để kết luận như vậy.

Browser fingerprint chỉ là **một nhóm tín hiệu**.

Server có thể còn quan sát:

```text
IP
TLS
HTTP/2
Headers
Cookies
Request frequency
URL patterns
Authentication
Behavior
...
```

`primp` giúp mô phỏng các đặc điểm network/browser profile nhất định; nó không biến Python thành một trình duyệt Chromium thực sự và không đảm bảo vượt qua mọi hệ thống phát hiện. PyPI hiện mô tả nó là HTTP client có browser impersonation capabilities. ([PyPI][3])

---

# 33. Bài tập 1 — Profile chuẩn

Chạy:

```python
import primp


client = primp.Client(
    impersonate="chrome_146",
    impersonate_os="windows",
)

response = client.get(
    "https://httpbin.org/headers"
)

print(response.text)
```

Quan sát:

```text
User-Agent
Sec-CH-UA
Sec-CH-UA-Platform
Sec-Fetch-*
Accept
...
```

Không cần học thuộc giá trị.

Mục tiêu là nhận ra:

```text
impersonate
    ↓
default browser headers
```

---

# 34. Bài tập 2 — Override User-Agent

Thử:

```python
response = client.get(
    "https://httpbin.org/headers",
    headers={
        "User-Agent": "MyCrawler/1.0",
    },
)

print(response.text)
```

Sau đó tự trả lời:

```text
User-Agent đã đổi?

TLS có tự đổi theo không?

HTTP/2 có tự đổi theo không?

Sec-CH-UA có tự biến thành MyCrawler không?
```

Đây chính là bản chất của:

```text
Header override
```

so với:

```text
Browser impersonation
```

---

# 35. Bài tập 3 — Request-specific Header

Thử:

```python
response = client.get(
    "https://httpbin.org/headers",
    headers={
        "Referer": "https://example.com/",
    },
)

print(response.text)
```

So sánh với bài 2.

Mục tiêu:

```text
User-Agent
    → browser identity

Referer
    → request context
```

---

# 36. Bài tập 4 — So sánh 3 tầng

Tạo ba client:

```python
normal = primp.Client()

manual = primp.Client(
    headers={
        "User-Agent": "Mozilla/5.0 Chrome/146",
    }
)

impersonated = primp.Client(
    impersonate="chrome_146",
    impersonate_os="windows",
)
```

Sau đó kiểm tra:

```text
https://httpbin.org/headers
```

và:

```text
https://tls.peet.ws/api/all
```

Mục tiêu là xây dựng trực giác:

```text
NORMAL
   ↓
normal HTTP client

MANUAL UA
   ↓
browser-like HTTP header

IMPERSONATED
   ↓
browser profile
   ├── headers
   ├── TLS
   └── HTTP/2
```

---

# 37. Bức tranh sau Buổi 27

Đến đây:

```text
                Browser Profile
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
      Browser          OS             Version
        │              │              │
        └──────────────┼──────────────┘
                       ▼
               Network Persona
                       │
           ┌───────────┼───────────┐
           ▼           ▼           ▼
          TLS        HTTP/2      Headers
           │           │           │
           ▼           ▼           ▼
      fingerprint   fingerprint   identity
```

Và:

```text
Session
   │
   ├── Cookies
   ├── Client
   ├── Browser Profile
   └── Network context
```

---

# 38. Kiến thức quan trọng nhất

Đừng ghi nhớ:

```text
"Chrome = User-Agent Chrome"
```

Hãy ghi nhớ:

```text
Chrome Persona
    =
Browser version
    +
OS
    +
TLS
    +
HTTP/2
    +
Headers
```

và khi có session:

```text
Browser Persona
    +
Cookies
    +
IP/Proxy
    +
Request behavior
```

---

# Roadmap

```text
PHẦN III — BROWSER IMPERSONATION

21. Vì sao cần impersonation       ✅
22. Chrome fingerprint              ✅
23. Firefox / Safari / Edge         ✅
24. impersonate_os                   ✅
25. TLS fingerprint                  ✅
26. HTTP/2                           ✅
27. Headers + fingerprint            ✅
28. Fingerprint thực tế              ← tiếp theo
29. So sánh httpx vs primp
30. Xây BrowserClient
```

**Buổi 28 — Fingerprint thực tế** sẽ không học thêm một API mới ngay, mà chúng ta sẽ làm một bài **fingerprint lab**: chạy `normal`, `User-Agent thủ công`, `chrome`, `firefox`, `edge` rồi thu thập **Headers + TLS + HTTP/2** để lập bảng so sánh và hiểu chính xác `primp` đang thay đổi những lớp nào.

[1]: https://docs.rs/primp/latest/primp/imp/index.html?utm_source=chatgpt.com "primp::imp - Rust"
[2]: https://docs.rs/xkit/latest/src/xkit/tls/impersonate/chrome/v123.rs.html?utm_source=chatgpt.com "v123.rs - source"
[3]: https://pypi.org/project/primp/2.0.1/?utm_source=chatgpt.com "primp · PyPI"
