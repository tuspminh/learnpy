# Phần III — Browser Impersonation

# Buổi 24 — `impersonate_os`

Ở Buổi 23, chúng ta đã thấy:

```text
Chrome
Firefox
Safari
Edge
```

không phải chỉ là tên browser.

Hôm nay thêm một thành phần rất quan trọng:

```text
Browser + OS
```

Ví dụ:

```text
Chrome + Windows
Chrome + macOS
Chrome + Android
Safari + macOS
Safari + iOS
Firefox + Windows
```

Trong `primp`, `impersonate_os` cho phép chỉ định OS platform khi tạo browser fingerprint. Tài liệu hiện tại liệt kê các giá trị như `windows`, `macos`, `linux`, `android`, `ios` và `random`.

---

# 1. Vì sao Browser cần OS?

Ta thường nghĩ:

```text
Browser = Chrome
```

nhưng thực tế một browser chạy trên:

```text
Windows
macOS
Linux
Android
```

có thể có những đặc điểm khác nhau.

Mô hình:

```text
Browser
    +
OS
    ↓
Browser Profile
    ↓
Fingerprint
```

Ví dụ:

```text
Chrome
+
Windows
↓
Chrome Windows profile
```

khác về persona so với:

```text
Chrome
+
macOS
↓
Chrome macOS profile
```

---

# 2. `impersonate_os` là gì?

Ví dụ:

```python
import primp

client = primp.Client(
    impersonate="chrome_146",
    impersonate_os="windows",
)
```

Ta đang nói với `primp`:

```text
Browser = Chrome 146
OS      = Windows
```

Một ví dụ khác:

```python
client = primp.Client(
    impersonate="chrome_146",
    impersonate_os="macos",
)
```

```text
Browser = Chrome 146
OS      = macOS
```

Theo API hiện tại, `Client` hỗ trợ tham số `impersonate_os`.

---

# 3. Tại sao OS ảnh hưởng fingerprint?

Hãy nhìn một browser profile:

```text
Chrome 146
    │
    ├── User-Agent
    ├── Client Hints
    ├── TLS
    ├── HTTP/2
    └── OS characteristics
```

Nếu đổi OS:

```text
Chrome 146 + Windows
```

sang:

```text
Chrome 146 + macOS
```

thì một số thông tin browser-facing có thể thay đổi.

Ví dụ điển hình là:

```text
Sec-CH-UA-Platform
```

hoặc các thông tin tương tự được browser sử dụng để mô tả platform.

Nhưng:

> **Không nên tự suy luận rằng `impersonate_os` chỉ đơn giản là đổi `Sec-CH-UA-Platform`.**

Nó là một phần của cơ chế xây browser fingerprint trong `primp`.

---

# 4. `impersonate` và `impersonate_os` là hai thứ khác nhau

Đây là điểm rất quan trọng.

```python
client = primp.Client(
    impersonate="chrome_146",
)
```

xác định:

```text
Browser profile
```

Trong khi:

```python
client = primp.Client(
    impersonate="chrome_146",
    impersonate_os="windows",
)
```

thêm:

```text
OS profile
```

Mô hình:

```text
                  Client
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
   impersonate          impersonate_os
          │                   │
          ▼                   ▼
   Chrome 146            Windows
          │                   │
          └─────────┬─────────┘
                    ▼
             Browser Persona
```

---

# 5. Các OS hiện tại

Theo tài liệu `primp`, enum `ImpersonateOS` hiện có:

```text
windows
macos
linux
android
ios
random
```

Có thể kiểm tra trực tiếp trên Python:

```python
import primp

print(primp.ImpersonateOS)
```

Hoặc:

```python
import primp

print(list(primp.ImpersonateOS))
```

Tùy cách Python binding expose enum trong version bạn cài.

---

# 6. Chrome + Windows

Ví dụ:

```python
import primp


client = primp.Client(
    impersonate="chrome_146",
    impersonate_os="windows",
)

response = client.get(
    "https://example.com"
)

print(response.status_code)
```

Mô hình:

```text
Chrome 146
    +
Windows
    ↓
primp
    ↓
HTTP request
```

---

# 7. Chrome + macOS

```python
import primp


client = primp.Client(
    impersonate="chrome_146",
    impersonate_os="macos",
)

response = client.get(
    "https://example.com"
)

print(response.status_code)
```

Bây giờ:

```text
Chrome 146
    +
macOS
```

---

# 8. Chrome + Linux

```python
client = primp.Client(
    impersonate="chrome_146",
    impersonate_os="linux",
)
```

Ta có:

```text
Chrome 146
    +
Linux
```

---

# 9. Chrome + Android

```python
client = primp.Client(
    impersonate="chrome_146",
    impersonate_os="android",
)
```

Mô hình:

```text
Chrome
   +
Android
   ↓
Mobile browser persona
```

Đây là trường hợp thú vị vì browser + OS bắt đầu thể hiện rõ khái niệm **device persona**.

---

# 10. Safari + iOS

Safari là trường hợp rất đáng chú ý.

Ta có:

```python
client = primp.Client(
    impersonate="safari_26",
    impersonate_os="ios",
)
```

Mô hình:

```text
Safari 26
    +
iOS
    ↓
Safari mobile persona
```

Trong khi:

```python
client = primp.Client(
    impersonate="safari_26",
    impersonate_os="macos",
)
```

lại là:

```text
Safari 26
    +
macOS
```

Đây là hai persona khác nhau về mặt mô hình.

---

# 11. Không phải Browser + OS nào cũng hợp lý

Đây là điểm cần suy nghĩ.

Ví dụ:

```text
Safari + Linux
```

là combination rất bất thường.

Trong khi:

```text
Safari + macOS
Safari + iOS
```

là những combination tự nhiên hơn.

Tương tự:

```text
Chrome + Windows
Chrome + macOS
Chrome + Linux
Chrome + Android
```

là các combination phổ biến.

Vì vậy Browser Profile không nên được tạo bằng:

```python
random_browser()
random_os()
```

một cách độc lập.

Sai:

```text
Browser = random
OS      = random
```

Có thể sinh:

```text
Safari + Linux
Edge + iOS
```

là những persona không hợp lý.

---

# 12. Browser Profile nên là một combination

Thay vì:

```python
browser = random.choice(...)
os = random.choice(...)
```

hãy tư duy:

```text
BrowserProfile
       │
       ├── Browser
       ├── Version
       └── OS
```

Ví dụ:

```python
profile = {
    "browser": "chrome",
    "version": 146,
    "os": "windows",
}
```

hoặc:

```python
profile = {
    "browser": "safari",
    "version": 26,
    "os": "macos",
}
```

Đây là bước đầu để sau này xây:

```text
BrowserProfile
```

trong `BrowserClient`.

---

# 13. Tư duy Domain Model

Nếu áp dụng kiến trúc bạn đang học:

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
chrome_windows = BrowserProfile(
    browser="chrome",
    version="146",
    os="windows",
)
```

và:

```python
chrome_linux = BrowserProfile(
    browser="chrome",
    version="146",
    os="linux",
)
```

Hai object:

```text
chrome_windows
chrome_linux
```

là hai profile khác nhau.

---

# 14. Nhưng đừng vội đưa `primp` vào Domain

Đây là phần quan trọng đối với kiến trúc Novel Crawler.

Không nên:

```python
@dataclass
class BrowserProfile:
    impersonate: primp.Impersonate
```

Domain không nên phụ thuộc:

```python
import primp
```

Tốt hơn:

```python
@dataclass(frozen=True)
class BrowserProfile:
    browser: str
    version: str
    os: str
```

Sau đó Infrastructure chuyển đổi:

```text
BrowserProfile
      │
      ▼
PrimpProfileMapper
      │
      ▼
primp.Client(...)
```

---

# 15. Mapper

Ví dụ đơn giản:

```python
import primp


class PrimpProfileMapper:

    def to_client_kwargs(
        self,
        profile: BrowserProfile,
    ) -> dict:
        return {
            "impersonate": (
                f"{profile.browser}_{profile.version}"
            ),
            "impersonate_os": profile.os,
        }
```

Sử dụng:

```python
profile = BrowserProfile(
    browser="chrome",
    version="146",
    os="windows",
)

mapper = PrimpProfileMapper()

kwargs = mapper.to_client_kwargs(profile)

client = primp.Client(**kwargs)
```

Ta có:

```text
Domain
  │
  ▼
BrowserProfile
  │
  ▼
Mapper
  │
  ▼
primp.Client
```

Đây là hướng Clean Architecture tốt hơn.

---

# 16. Nhưng hiện tại chưa cần Mapper phức tạp

Ở Buổi 24, ta chỉ cần:

```python
client = primp.Client(
    impersonate="chrome_146",
    impersonate_os="windows",
)
```

Chưa cần:

```text
Factory
Strategy
Registry
Mapper
Builder
```

hàng loạt.

Chúng ta đang học theo nguyên tắc:

> **Abstraction xuất hiện khi complexity thực sự xuất hiện.**

---

# 17. Test fingerprint

Dùng endpoint:

```text
https://tls.peet.ws/api/all
```

Ta có thể chạy:

```python
import primp


URL = "https://tls.peet.ws/api/all"


def test(profile: str, os: str):
    client = primp.Client(
        impersonate=profile,
        impersonate_os=os,
    )

    response = client.get(URL)

    print("=" * 70)
    print(profile, "+", os)
    print("=" * 70)

    print(response.text)


def main():
    test(
        "chrome_146",
        "windows",
    )

    test(
        "chrome_146",
        "macos",
    )

    test(
        "chrome_146",
        "linux",
    )


if __name__ == "__main__":
    main()
```

---

# 18. Bài thực hành tốt hơn

Ta tạo danh sách:

```python
PROFILES = [
    ("chrome_146", "windows"),
    ("chrome_146", "macos"),
    ("chrome_146", "linux"),
]
```

Sau đó:

```python
for browser, os in PROFILES:
    client = primp.Client(
        impersonate=browser,
        impersonate_os=os,
    )

    response = client.get(
        "https://tls.peet.ws/api/all"
    )

    print(browser, os)
    print(response.text)
```

Hãy quan sát đặc biệt:

```text
User-Agent
headers
TLS
HTTP/2
```

Mục tiêu là nhận ra:

```text
Chrome 146 + Windows
       ≠
Chrome 146 + macOS
```

ở cấp độ persona/configuration.

---

# 19. `impersonate_os="random"`

`primp` hiện có:

```text
random
```

cho OS impersonation.

Ví dụ:

```python
client = primp.Client(
    impersonate="chrome_146",
    impersonate_os="random",
)
```

Nhưng với crawler production:

> **Không nên dùng random một cách tùy tiện.**

Vì:

```text
Request 1 → Windows
Request 2 → Linux
Request 3 → Android
Request 4 → macOS
```

trong cùng một logical session sẽ tạo persona không ổn định.

---

# 20. Session là một persona

Kết hợp với Buổi 9 và Buổi 16:

```text
Session
   │
   ├── Cookies
   ├── Client
   ├── Browser profile
   └── OS
```

Ví dụ:

```text
Session A
    Browser = Chrome 146
    OS      = Windows
```

thì:

```text
Request 1 → Chrome/Windows
Request 2 → Chrome/Windows
Request 3 → Chrome/Windows
```

hợp lý hơn:

```text
Request 1 → Chrome/Windows
Request 2 → Firefox/Linux
Request 3 → Safari/iOS
```

---

# 21. Proxy cũng phải nằm ngoài Browser Profile

Đừng tạo:

```python
BrowserProfile(
    browser="chrome",
    version="146",
    os="windows",
    proxy="..."
)
```

nếu mục tiêu là giữ các concern độc lập.

Nên:

```text
BrowserProfile
   │
   ├── Browser
   ├── Version
   └── OS

ProxyConfig
   │
   └── Proxy URL
```

Sau đó:

```text
BrowserClient
   │
   ├── BrowserProfile
   └── ProxyConfig
```

Đây là **composition**.

---

# 22. Kiến trúc hiện tại

Sau Buổi 24:

```text
                    BrowserClient
                         │
             ┌───────────┴───────────┐
             │                       │
             ▼                       ▼
      BrowserProfile            ProxyConfig
             │
      ┌──────┼──────┐
      ▼      ▼      ▼
   Browser Version  OS
             │
             ▼
        Primp Client
```

Sau này:

```text
BrowserClient
    │
    ├── BrowserProfile
    ├── ProxyStrategy
    ├── RetryPolicy
    └── RateLimiter
```

Nhưng từng thành phần sẽ được học riêng.

---

# 23. Một vấn đề thực tế: OS không phải fingerprint đầy đủ

Không nên nghĩ:

```text
chrome_146
+
windows
=
complete Chrome fingerprint
```

Không đúng.

Ta vẫn còn:

```text
TLS
HTTP/2
Headers
Cookies
IP
Browser-side JavaScript
...
```

Mô hình đầy đủ hơn:

```text
             Browser Persona
                    │
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
   Browser          OS         Protocol
      │             │             │
   Chrome        Windows      TLS/HTTP2
                                  │
                                  ▼
                              Headers
```

`impersonate_os` chỉ là **một thành phần**.

---

# 24. Điều cực kỳ quan trọng: Browser fingerprint ≠ Browser thật

Ta vẫn phải nhớ:

```text
primp.Client(
    impersonate="chrome_146",
    impersonate_os="windows",
)
```

không tạo:

```text
Windows
   ↓
Chrome executable
   ↓
Chromium engine
   ↓
JavaScript
```

Nó vẫn là:

```text
Python
   ↓
primp
   ↓
HTTP/TLS stack
```

với browser-like configuration.

Vì vậy:

```text
Browser impersonation
        ≠
Browser automation
```

---

# 25. Liên hệ trực tiếp với Novel Crawler

Sau này configuration có thể rất đẹp:

```python
profile = BrowserProfile(
    browser="chrome",
    version="146",
    os="windows",
)
```

Fetcher:

```text
Novel Crawler
      │
      ▼
PrimpFetcher
      │
      ▼
BrowserProfile
      │
      ├── Chrome 146
      └── Windows
      │
      ▼
primp.Client
```

Application chỉ biết:

```python
response = fetcher.get(url)
```

không biết:

```text
TLS
HTTP/2
impersonate
impersonate_os
```

Đây chính là abstraction boundary mà chúng ta muốn.

---

# 26. Bài tập chính

Tạo:

```text
lesson_24.py
```

```python
import primp


URL = "https://tls.peet.ws/api/all"


PROFILES = [
    {
        "name": "Chrome Windows",
        "impersonate": "chrome_146",
        "os": "windows",
    },
    {
        "name": "Chrome macOS",
        "impersonate": "chrome_146",
        "os": "macos",
    },
    {
        "name": "Chrome Linux",
        "impersonate": "chrome_146",
        "os": "linux",
    },
]


def test_profile(profile: dict):
    print("=" * 80)
    print(profile["name"])
    print("=" * 80)

    client = primp.Client(
        impersonate=profile["impersonate"],
        impersonate_os=profile["os"],
    )

    response = client.get(URL)

    print(response.text)
    print()


def main():
    for profile in PROFILES:
        test_profile(profile)


if __name__ == "__main__":
    main()
```

Sau khi chạy, hãy so sánh:

```text
Chrome 146 + Windows
Chrome 146 + macOS
Chrome 146 + Linux
```

---

# 27. Bài tập kiến trúc

Tạo:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserProfile:
    browser: str
    version: str
    os: str
```

Sau đó:

```python
profile = BrowserProfile(
    browser="chrome",
    version="146",
    os="windows",
)
```

Viết hàm:

```python
def build_primp_kwargs(
    profile: BrowserProfile,
) -> dict:
    ...
```

sao cho:

```python
build_primp_kwargs(profile)
```

trả về:

```python
{
    "impersonate": "chrome_146",
    "impersonate_os": "windows",
}
```

**Chưa cần tạo class Factory.**

Mục tiêu chỉ là luyện cách tách:

```text
BrowserProfile
       ↓
primp configuration
```

---

# 28. Tổng kết Buổi 24

Ta có:

```text
Buổi 22
Chrome fingerprint
        ↓
Buổi 23
Browser family
        ↓
Buổi 24
Browser + OS
```

Công thức tư duy:

```text
Browser
   +
Version
   +
OS
   ↓
Browser Persona
```

Ví dụ:

```text
Chrome 146 + Windows
Chrome 146 + macOS
Chrome 146 + Linux
Chrome 146 + Android
```

là những profile khác nhau.

Và trong `primp`:

```python
client = primp.Client(
    impersonate="chrome_146",
    impersonate_os="windows",
)
```

`impersonate` xác định browser profile, còn `impersonate_os` bổ sung OS platform cho việc tạo browser fingerprint. Các OS được hỗ trợ hiện tại gồm Windows, macOS, Linux, Android, iOS và random.

---

## Mốc hiện tại

```text
PHẦN III — BROWSER IMPERSONATION

21. Vì sao cần impersonation       ✅
22. Chrome fingerprint              ✅
23. Firefox / Safari / Edge         ✅
24. impersonate_os                   ✅
25. TLS fingerprint
26. HTTP/2
27. Headers + fingerprint
28. Fingerprint thực tế
29. So sánh httpx vs primp
30. Xây BrowserClient
```

**Buổi 25 — TLS Fingerprint** sẽ là phần kỹ thuật sâu hơn: ta sẽ đi từ `ClientHello` → TLS version → cipher suites → extensions → ALPN → JA3/JA4 và cuối cùng hiểu chính xác `primp` đang cố mô phỏng điều gì ở tầng TLS.
