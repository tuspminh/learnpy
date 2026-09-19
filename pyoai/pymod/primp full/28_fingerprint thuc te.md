# Buổi 28 — Fingerprint thực tế

Ở buổi 27 chúng ta đã hiểu:

```text
Browser Persona
    =
Browser Version
+
OS
+
TLS
+
HTTP/2
+
Headers
```

Buổi 28 sẽ **không chỉ học lý thuyết nữa**, mà chúng ta sẽ làm một lab để **quan sát fingerprint thực tế**.

`primp 2.0.1` hiện có các profile như Chrome 144–153, Firefox 140/146–151, Edge 144–153..., cùng các OS profile `windows`, `macos`, `linux`, `android`, `ios`... ([PyPI][1])

---

# 1. Mục tiêu buổi học

Chúng ta sẽ so sánh:

```text
1. primp.Client()
2. primp.Client() + User-Agent thủ công
3. Chrome 146 + Windows
4. Firefox 146 + Windows
5. Edge 146 + Windows
```

Và quan sát:

```text
HTTP Headers
      │
      ├── User-Agent
      ├── Client Hints
      ├── Accept
      ├── Sec-Fetch-*
      │
      ↓
TLS
      │
      ├── TLS version
      ├── cipher
      ├── extensions
      ├── curves
      │
      ↓
HTTP/2
      │
      ├── SETTINGS
      ├── pseudo-header order
      └── HTTP/2 fingerprint
```

Endpoint `tls.peet.ws` hiện cung cấp `/api/all`, `/api/clean`, `/api/tls` và hiển thị cả TLS fingerprint, HTTP version, HTTP/2 fingerprint, JA3/JA4... ([TrackMe - Fingerprinting API][2])

---

# 2. Trước tiên: Fingerprint thực tế là gì?

Có một điểm rất quan trọng.

Chúng ta **không nói**:

> "Đây là toàn bộ fingerprint của browser."

Mà nên nói:

> **Observed network fingerprint snapshot** — snapshot những đặc điểm mạng mà server quan sát được.

Ví dụ:

```text
Chrome 146 + Windows

             Server
                │
        ┌───────┴────────┐
        │                │
     HTTP             Network
        │                │
   Headers           TLS / HTTP2
        │                │
   User-Agent        TLS version
   Sec-CH-UA         Cipher
   Sec-Fetch-*       Extensions
                     HTTP/2
```

Đây chỉ là **network-level fingerprint**.

Nó không bao gồm đầy đủ:

```text
Canvas fingerprint
WebGL
Audio fingerprint
Screen resolution
JavaScript environment
DOM behavior
Mouse behavior
```

vì `primp` là HTTP client, **không phải Chromium browser**.

---

# 3. Vì sao User-Agent không đủ?

Đây là bài thực hành quan trọng nhất.

Ta có:

```python
import primp

client = primp.Client(
    headers={
        "User-Agent": "Mozilla/5.0 Chrome/146"
    }
)
```

Nhìn HTTP header có vẻ giống Chrome.

Nhưng:

```text
User-Agent
    ↓
Chrome
```

không có nghĩa:

```text
TLS
    ↓
Chrome

HTTP/2
    ↓
Chrome

Client Hints
    ↓
Chrome
```

Trong khi browser impersonation của `primp` gắn profile với TLS, HTTP/2 và default headers. ([Docs.rs][3])

Đó chính là khác biệt giữa:

```text
UA spoofing
```

và:

```text
Browser impersonation
```

---

# 4. Lab 1 — Quan sát HTTP Headers

Tạo:

```text
lesson28/
└── 01_headers.py
```

Code hoàn chỉnh:

```python
import json

import primp


URL = "https://httpbin.org/headers"


def test_client(name: str, client: primp.Client):
    print("=" * 70)
    print(name)
    print("=" * 70)

    response = client.get(URL)

    print("Status:", response.status_code)
    print("URL:", response.url)

    data = response.json()

    print(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        )
    )

    print()


def main():
    # 1. Normal client
    normal = primp.Client()

    # 2. Manual User-Agent
    manual_ua = primp.Client(
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/146.0.0.0 "
                "Safari/537.36"
            )
        }
    )

    # 3. Chrome impersonation
    chrome = primp.Client(
        impersonate="chrome_146",
        impersonate_os="windows",
    )

    # 4. Firefox impersonation
    firefox = primp.Client(
        impersonate="firefox_146",
        impersonate_os="windows",
    )

    # 5. Edge impersonation
    edge = primp.Client(
        impersonate="edge_146",
        impersonate_os="windows",
    )

    test_client("1. Normal", normal)
    test_client("2. Manual User-Agent", manual_ua)
    test_client("3. Chrome 146 + Windows", chrome)
    test_client("4. Firefox 146 + Windows", firefox)
    test_client("5. Edge 146 + Windows", edge)


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python 01_headers.py
```

---

# 5. Hãy chú ý điều gì?

Đặc biệt nhìn:

```text
User-Agent
```

và nếu endpoint trả về:

```text
sec-ch-ua
sec-ch-ua-mobile
sec-ch-ua-platform
sec-fetch-site
sec-fetch-mode
sec-fetch-user
sec-fetch-dest
accept
accept-language
```

Browser profile có thể thiết lập nhiều header liên quan đến persona chứ không chỉ User-Agent. Tài liệu `primp` mô tả mỗi browser version map tới TLS fingerprint và default headers. ([Docs.rs][3])

Ví dụ về cấu hình Chrome impersonation trong hệ sinh thái underlying của thư viện có thể thấy:

```text
sec-ch-ua
sec-ch-ua-mobile
sec-ch-ua-platform
User-Agent
Accept
Sec-Fetch-*
```

được cấu hình cùng profile. ([Docs.rs][4])

---

# 6. Lab 2 — Quan sát TLS + HTTP/2

Tạo:

```text
02_network.py
```

Code:

```python
import json

import primp


URL = "https://tls.peet.ws/api/all"


def inspect(
    name: str,
    client: primp.Client,
):
    print("=" * 80)
    print(name)
    print("=" * 80)

    response = client.get(URL)

    print("Status:", response.status_code)

    data = response.json()

    print(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        )
    )

    print()


def main():
    normal = primp.Client()

    chrome = primp.Client(
        impersonate="chrome_146",
        impersonate_os="windows",
    )

    firefox = primp.Client(
        impersonate="firefox_146",
        impersonate_os="windows",
    )

    edge = primp.Client(
        impersonate="edge_146",
        impersonate_os="windows",
    )

    inspect("NORMAL", normal)
    inspect("CHROME 146 WINDOWS", chrome)
    inspect("FIREFOX 146 WINDOWS", firefox)
    inspect("EDGE 146 WINDOWS", edge)


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python 02_network.py
```

---

# 7. Không nên chỉ `print(response.text)`

Ở đây chúng ta đang chuyển sang tư duy **data collection**.

Thay vì:

```python
print(response.text)
```

ta làm:

```python
data = response.json()
```

sau đó tìm các field quan trọng.

Ví dụ endpoint hiện có thể trả về các thông tin như:

```text
JA3
JA4
TLS
HTTP
TLS extensions
TLS curves
HTTP/2 fingerprint
```

Trang API hiện tại của `tls.peet.ws` cũng hiển thị:

```text
Used TLS
Used HTTP
Total http/2 frames
Supported HTTP
Supported TLS
TLS cipher suites
TLS extensions
TLS curves
```

và các fingerprint như JA3, JA4, Akamai HTTP/2 fingerprint. ([TrackMe - Fingerprinting API][2])

**Nhưng:** schema endpoint có thể thay đổi.

Vì vậy crawler không nên viết:

```python
data["some_field"]["another_field"]
```

một cách cứng nhắc nếu không cần thiết.

---

# 8. Lab 3 — Tạo FingerprintSnapshot

Bây giờ chúng ta bắt đầu thiết kế theo phong cách architecture mà bạn đang học.

Tạo:

```text
03_snapshot.py
```

```python
from dataclasses import dataclass
from typing import Any

import primp


@dataclass
class FingerprintSnapshot:
    profile: str
    os: str | None
    headers: dict[str, Any]
    network: dict[str, Any]
```

Đây là **DTO / observation model**.

Nó không phải:

```text
Domain Entity
```

và cũng không phải:

```text
BrowserProfile
```

Hai khái niệm này khác nhau.

---

# 9. BrowserProfile vs FingerprintSnapshot

### BrowserProfile

Là **cấu hình chúng ta muốn sử dụng**:

```python
@dataclass(frozen=True)
class BrowserProfile:
    browser: str
    version: str
    os: str
```

Ví dụ:

```text
Chrome
146
Windows
```

---

### FingerprintSnapshot

Là **những gì server quan sát được**:

```text
JA3
JA4
TLS
HTTP
Headers
HTTP/2
...
```

Do đó:

```text
BrowserProfile
      │
      │ configure
      ↓
Primp Client
      │
      │ request
      ↓
Server
      │
      │ observes
      ↓
FingerprintSnapshot
```

Đây là distinction rất quan trọng.

---

# 10. Lab hoàn chỉnh — Fingerprint Collector

Bây giờ gom mọi thứ thành một chương trình.

Tạo:

```text
04_fingerprint_lab.py
```

```python
import json
from dataclasses import dataclass
from typing import Any

import primp


@dataclass
class FingerprintSnapshot:
    profile: str
    os: str | None
    headers: dict[str, Any]
    network: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile": self.profile,
            "os": self.os,
            "headers": self.headers,
            "network": self.network,
        }


def create_client(
    profile: str | None,
    os: str | None,
) -> primp.Client:

    if profile is None:
        return primp.Client()

    return primp.Client(
        impersonate=profile,
        impersonate_os=os,
    )


def collect(
    profile: str,
    os: str | None,
) -> FingerprintSnapshot:

    client = create_client(
        profile=None if profile == "normal" else profile,
        os=os,
    )

    headers_response = client.get(
        "https://httpbin.org/headers"
    )

    network_response = client.get(
        "https://tls.peet.ws/api/all"
    )

    return FingerprintSnapshot(
        profile=profile,
        os=os,
        headers=headers_response.json(),
        network=network_response.json(),
    )


def print_summary(
    snapshot: FingerprintSnapshot,
):
    print("=" * 80)
    print(
        f"PROFILE: {snapshot.profile} "
        f"| OS: {snapshot.os}"
    )
    print("=" * 80)

    headers = snapshot.headers.get(
        "headers",
        {},
    )

    print("User-Agent:")
    print(
        headers.get(
            "User-Agent",
            "<not available>",
        )
    )

    print()

    print("Client Hints:")

    for key in (
        "Sec-Ch-Ua",
        "Sec-Ch-Ua-Mobile",
        "Sec-Ch-Ua-Platform",
    ):
        print(
            f"{key}: "
            f"{headers.get(key, '<not available>')}"
        )

    print()

    network = snapshot.network

    print("Network:")

    for key in (
        "http_version",
        "tls",
        "ja3",
        "ja4",
    ):
        print(
            f"{key}: "
            f"{network.get(key, '<not available>')}"
        )

    print()


def main():

    profiles = [
        ("normal", None),
        ("chrome_146", "windows"),
        ("firefox_146", "windows"),
        ("edge_146", "windows"),
    ]

    snapshots = []

    for profile, os in profiles:

        try:
            snapshot = collect(
                profile,
                os,
            )

            snapshots.append(snapshot)

            print_summary(snapshot)

        except Exception as exc:
            print(
                f"FAILED: {profile}: {exc}"
            )

    with open(
        "fingerprints.json",
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            [
                snapshot.to_dict()
                for snapshot in snapshots
            ],
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(
        "Saved to fingerprints.json"
    )


if __name__ == "__main__":
    main()
```

---

# 11. Kết quả chúng ta đang xây dựng

Sau khi chạy:

```text
lesson28/
│
├── 01_headers.py
├── 02_network.py
├── 03_snapshot.py
├── 04_fingerprint_lab.py
│
└── fingerprints.json
```

`fingerprints.json` sẽ có cấu trúc đại khái:

```json
[
    {
        "profile": "normal",
        "os": null,
        "headers": {
            "headers": {
                "User-Agent": "..."
            }
        },
        "network": {
            "...": "..."
        }
    },
    {
        "profile": "chrome_146",
        "os": "windows",
        "headers": {
            "headers": {
                "User-Agent": "...",
                "Sec-Ch-Ua": "...",
                "Sec-Ch-Ua-Platform": "..."
            }
        },
        "network": {
            "...": "..."
        }
    }
]
```

Điểm quan trọng là:

**đừng cố dự đoán fingerprint.**

Hãy:

```text
Configure
    ↓
Request
    ↓
Observe
    ↓
Record
    ↓
Compare
```

---

# 12. Một bài test rất đáng làm

Thử:

```python
chrome = primp.Client(
    impersonate="chrome_146",
    impersonate_os="windows",
)
```

sau đó thử:

```python
chrome = primp.Client(
    impersonate="chrome_146",
    impersonate_os="macos",
)
```

So sánh.

Ta đang thay:

```text
Chrome 146
```

thành:

```text
Chrome 146
+
Windows
```

và:

```text
Chrome 146
+
macOS
```

`primp` có API/profile OS riêng để điều chỉnh browser fingerprint theo nền tảng. ([Docs.rs][3])

---

# 13. Một thử nghiệm còn quan trọng hơn

Thử ba trường hợp:

### A — Chỉ đổi User-Agent

```python
primp.Client(
    headers={
        "User-Agent": "Chrome..."
    }
)
```

### B — Chrome impersonation

```python
primp.Client(
    impersonate="chrome_146",
)
```

### C — Chrome + Windows

```python
primp.Client(
    impersonate="chrome_146",
    impersonate_os="windows",
)
```

Tư duy cần hình thành:

```text
A
│
└── Header spoofing


B
│
├── Headers
├── TLS
└── HTTP/2


C
│
├── Browser
├── Version
├── OS
├── Headers
├── TLS
└── HTTP/2
```

Đây chính là lý do `primp` phù hợp với phần Browser Impersonation của crawler.

---

# 14. Nhưng đừng hiểu sai về fingerprint

Có một sai lầm rất dễ mắc:

```text
Fingerprint giống Chrome
        ↓
Server không phát hiện crawler
```

**Không đúng.**

Fingerprint chỉ là **một nhóm tín hiệu**.

Server còn có thể quan sát:

```text
                    Request
                       │
       ┌───────────────┼────────────────┐
       ↓               ↓                ↓
   Network          Behavior          Session
       │               │                │
      TLS          request rate       cookies
      HTTP/2       timing             IP
      Headers      navigation         proxy
      IP            pattern            auth
```

Ví dụ crawler:

```text
Chrome fingerprint
+
1000 request/second
+
không có navigation behavior
+
IP cố định
```

vẫn có thể rất khác traffic browser thông thường.

Vì vậy các bài sau mới tiếp tục xây:

```text
Fingerprint
      +
Proxy
      +
Rate Limit
      +
Session
      +
Retry
```

---

# 15. Áp dụng vào Novel Crawler

Đây mới là phần quan trọng đối với project của bạn.

Không nên làm:

```python
class PrimpFetcher:

    def get(self, url):
        client = primp.Client(
            impersonate="chrome_146",
            impersonate_os="windows",
        )

        return client.get(url)
```

Vì mỗi request lại tạo client mới.

Chúng ta đã học Buổi 16:

```text
Long-lived Client
```

Do đó:

```text
Application
    │
    ↓
Fetcher
    │
    ↓
BrowserProfile
    │
    ↓
Primp Client
    │
    ├── TLS
    ├── HTTP/2
    ├── Headers
    └── Cookies
```

---

# 16. Kiến trúc bắt đầu hình thành

Hiện tại:

```text
                 Novel Crawler
                       │
                       ↓
                  Fetcher
                       │
             ┌─────────┴─────────┐
             ↓                   ↓
       RequestOptions      BrowserProfile
             │                   │
             │                   ↓
             │              Primp Client
             │                   │
             └─────────┬─────────┘
                       ↓
                    HTTP
```

Về sau chúng ta sẽ thêm:

```text
BrowserProfile
ProxyStrategy
RetryPolicy
RateLimiter
ErrorClassifier
```

nhưng **không nhét tất cả vào BrowserProfile**.

---

# 17. Một thiết kế đúng

```python
@dataclass(frozen=True)
class BrowserProfile:
    browser: str
    version: str
    os: str


@dataclass(frozen=True)
class ProxyConfig:
    url: str


@dataclass(frozen=True)
class RequestOptions:
    timeout: float | None = None
    headers: dict[str, str] | None = None
    params: dict | None = None
```

Sau đó:

```text
PrimpFetcher
│
├── BrowserProfile
├── ProxyConfig
├── RequestOptions
├── RetryPolicy       ← Buổi 45
└── RateLimiter       ← Buổi 38
```

Đây là **Separation of Concerns**.

---

# 18. Fingerprint thực tế ≠ Fingerprint hoàn hảo

Ta nên dùng thuật ngữ:

```text
Observed Network Fingerprint
```

thay vì:

```text
Real Browser Fingerprint
```

Bởi vì:

```text
primp
```

không chạy:

```text
Chrome.exe
```

và cũng không có:

```text
DOM
JavaScript
Canvas
WebGL
GPU
AudioContext
```

Nó impersonate ở tầng HTTP/network. Tài liệu chính thức mô tả rõ browser impersonation của `primp` xoay quanh TLS, HTTP/2 và default headers. ([Docs.rs][3])

---

# 19. Bài tập thực hành

Bạn hãy tự chạy:

### Bài 1

So sánh:

```text
normal
chrome_146 + windows
chrome_146 + linux
chrome_146 + macos
```

---

### Bài 2

So sánh:

```text
chrome_146 + windows
firefox_146 + windows
edge_146 + windows
```

---

### Bài 3

Tạo bảng:

```text
Profile       User-Agent    HTTP    TLS    JA3    JA4
-------------------------------------------------------
normal        ...
chrome_146    ...
firefox_146   ...
edge_146      ...
```

---

### Bài 4

Thử phá persona:

```python
client = primp.Client(
    impersonate="chrome_146",
    impersonate_os="windows",
    headers={
        "User-Agent": "Firefox/146"
    },
)
```

Sau đó quan sát.

Mục tiêu **không phải** tìm cách vượt hệ thống chống bot, mà để tận mắt thấy:

```text
Browser profile
       ↓
một persona thống nhất

manual override
       ↓
có thể tạo sự không nhất quán
```

---

# 20. Tư duy quan trọng nhất của Buổi 28

Trước Buổi 28:

```text
Chrome 146
    =
User-Agent Chrome 146
```

Sau Buổi 28:

```text
Chrome 146
    =
Browser profile
       │
       ├── Headers
       ├── TLS
       ├── HTTP/2
       └── OS
```

Và:

```text
Fingerprint
```

không phải một giá trị duy nhất.

Nó là **tập hợp nhiều tín hiệu quan sát được**:

```text
             Network Fingerprint
                     │
       ┌─────────────┼─────────────┐
       ↓             ↓             ↓
    Headers         TLS          HTTP/2
       │             │             │
      UA          ClientHello   SETTINGS
   Client Hints   Cipher        pseudo-order
   Sec-Fetch      Extensions    behavior
```

`primp` hiện thực hóa chính ý tưởng này trong browser impersonation profile; tài liệu source của thư viện có `BrowserSettings`, `Http2Data`, `SettingsOrder`, `PseudoOrder` và ánh xạ browser version tới TLS fingerprint/default headers. ([Docs.rs][3])

---

## Roadmap

Đến đây:

```text
21. Vì sao cần impersonation       ✅
22. Chrome fingerprint             ✅
23. Firefox / Safari / Edge        ✅
24. impersonate_os                 ✅
25. TLS fingerprint                ✅
26. HTTP/2                         ✅
27. Headers + fingerprint          ✅
28. Fingerprint thực tế            ✅
```

### Tiếp theo — Buổi 29

```text
So sánh httpx vs primp
```

Chúng ta sẽ đặt hai client cạnh nhau:

```text
httpx
  vs
primp
```

và so sánh theo đúng góc nhìn **Novel Crawler**:

```text
API
Headers
Cookies
Session
HTTP/2
TLS
Browser impersonation
Proxy
Timeout
Exception
Performance
Architecture
```

để xác định **chỗ nào nên dùng httpx, chỗ nào nên dùng primp**, thay vì mặc định nghĩ rằng `primp` luôn tốt hơn.

[1]: https://pypi.org/project/primp/2.0.1/?utm_source=chatgpt.com "primp · PyPI"
[2]: https://tls.peet.ws/?utm_source=chatgpt.com "TrackMe | Home"
[3]: https://docs.rs/primp/latest/primp/imp/index.html?utm_source=chatgpt.com "primp::imp - Rust"
[4]: https://docs.rs/xkit/latest/src/xkit/tls/impersonate/chrome/v118.rs.html?utm_source=chatgpt.com "v118.rs - source"
