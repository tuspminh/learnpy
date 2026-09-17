# Buổi 30 — Xây dựng `BrowserClient`

Đây là buổi **kết thúc Phần III — Browser Impersonation**.

Trong 9 buổi vừa rồi chúng ta đã đi từ:

```text
Browser Fingerprint
        ↓
Chrome / Firefox / Edge
        ↓
OS
        ↓
TLS
        ↓
HTTP/2
        ↓
Headers
        ↓
Fingerprint thực tế
        ↓
httpx vs primp
```

Bây giờ gom chúng thành một abstraction vừa đủ dùng cho **Novel Crawler**:

```text
BrowserProfile
       ↓
BrowserClient
       ↓
primp.Client
       ↓
HTTP
```

Theo tài liệu hiện tại, `primp 2.0.1` hỗ trợ Python >= 3.10, các profile Chrome 144–153, Firefox 140/146–151, Edge 144–153, Safari 18.5/26.x, Opera 126–135 và các OS profile như Windows, macOS, Linux, Android, iOS. ([PyPI][1])

---

# 1. Mục tiêu của `BrowserClient`

Ta **không muốn** application viết trực tiếp:

```python
import primp

client = primp.Client(
    impersonate="chrome_146",
    impersonate_os="windows",
)
```

ở khắp nơi.

Thay vào đó:

```text
Application
     │
     ↓
BrowserClient
     │
     ↓
primp.Client
```

Application chỉ cần nói:

```python
client.get(url)
```

Còn:

```text
Browser
Version
OS
TLS
HTTP/2
Headers
```

được quản lý bên trong.

---

# 2. Đừng thiết kế `BrowserClient` quá lớn

Một thiết kế không tốt:

```python
class BrowserClient:

    def __init__(
        self,
        browser,
        version,
        os,
        proxy,
        timeout,
        retry,
        rate_limit,
        cookies,
        auth,
        ...
    ):
        ...
```

Đây sẽ trở thành **God Object**.

Chúng ta đã học cách tách:

```text
BrowserProfile
ProxyConfig
RequestOptions
RetryPolicy
RateLimiter
```

Vì vậy:

```text
BrowserClient
│
├── BrowserProfile
│
└── primp.Client
```

là đủ cho buổi này.

---

# 3. Thiết kế `BrowserProfile`

Tạo:

```text
lesson30/
└── browser_profile.py
```

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserProfile:
    """
    Mô tả browser persona mà client muốn impersonate.
    """

    browser: str
    version: str
    os: str

    @property
    def impersonate(self) -> str:
        return f"{self.browser}_{self.version}"
```

Ví dụ:

```python
profile = BrowserProfile(
    browser="chrome",
    version="146",
    os="windows",
)

print(profile.impersonate)
```

Kết quả:

```text
chrome_146
```

---

# 4. Nhưng có một vấn đề

Không phải profile nào cũng có dạng:

```text
browser_version
```

Ví dụ:

```text
safari_18.5
```

có version dạng decimal.

Hoặc profile generic:

```text
chrome
firefox
safari
edge
```

Do đó trong architecture thực tế, ta có thể dùng:

```python
@dataclass(frozen=True)
class BrowserProfile:
    impersonate: str
    os: str | None = None
```

Đây là thiết kế **tốt hơn cho adapter layer**, vì `primp` chính là nơi chịu trách nhiệm hiểu tên profile.

```python
profile = BrowserProfile(
    impersonate="chrome_146",
    os="windows",
)
```

Tôi chọn cách này cho `BrowserClient`.

---

# 5. BrowserProfile hoàn chỉnh

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserProfile:
    """
    Browser impersonation profile.

    Ví dụ:
        chrome_146 + windows
        firefox_146 + windows
        edge_146 + windows
    """

    impersonate: str
    os: str | None = None
```

Đơn giản nhưng rất quan trọng.

Nó đại diện cho:

```text
BrowserProfile
│
├── Browser
├── Version
└── OS
```

Còn:

```text
TLS
HTTP/2
Default headers
```

không cần lưu thủ công trong class này.

Vì chúng được `primp` resolve từ browser profile. Tài liệu `primp` mô tả `Impersonate` là browser version mapping tới TLS fingerprint/default headers và `ImpersonateOS` dùng để tạo browser fingerprint theo OS. ([Docs.rs][2])

---

# 6. Xây `BrowserClient`

Tạo:

```text
browser_client.py
```

```python
import primp

from browser_profile import BrowserProfile


class BrowserClient:

    def __init__(
        self,
        profile: BrowserProfile,
    ):
        self.profile = profile

        self.client = primp.Client(
            impersonate=profile.impersonate,
            impersonate_os=profile.os,
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

Đây là phiên bản đầu tiên.

---

# 7. Sử dụng

```python
from browser_client import BrowserClient
from browser_profile import BrowserProfile


def main():

    profile = BrowserProfile(
        impersonate="chrome_146",
        os="windows",
    )

    client = BrowserClient(profile)

    response = client.get(
        "https://httpbin.org/headers"
    )

    print(response.status_code)
    print(response.text)


if __name__ == "__main__":
    main()
```

Kiến trúc:

```text
main.py
   │
   ↓
BrowserProfile
   │
   ↓
BrowserClient
   │
   ↓
primp.Client
   │
   ↓
httpbin
```

---

# 8. Tại sao `BrowserClient` giữ Client?

Không làm:

```python
def get(self, url):

    client = primp.Client(
        impersonate="chrome_146"
    )

    return client.get(url)
```

Mỗi request lại tạo client.

Thay vào đó:

```python
class BrowserClient:

    def __init__(self, profile):
        self.client = primp.Client(
            impersonate=profile.impersonate,
            impersonate_os=profile.os,
        )
```

rồi:

```python
client.get(url1)
client.get(url2)
client.get(url3)
```

Đây chính là nguyên tắc **long-lived client** chúng ta đã học.

---

# 9. Một BrowserClient = một browser persona

Đây là quy tắc rất quan trọng.

Ví dụ:

```python
chrome_windows = BrowserClient(
    BrowserProfile(
        impersonate="chrome_146",
        os="windows",
    )
)
```

Sau đó:

```text
chrome_windows
       │
       ├── request 1
       ├── request 2
       ├── request 3
       └── request 4
```

Tất cả dùng cùng persona.

Không nên:

```text
request 1 → Chrome
request 2 → Firefox
request 3 → Safari
request 4 → Chrome
```

chỉ để "random".

Browser profile nên đại diện cho một **stable client identity** trong session.

---

# 10. Factory

Bây giờ ta không muốn application phải tự tạo `BrowserProfile`.

Tạo:

```text
browser_client_factory.py
```

```python
from browser_client import BrowserClient
from browser_profile import BrowserProfile


class BrowserClientFactory:

    def create_chrome(
        self,
        version: str = "146",
        os: str = "windows",
    ) -> BrowserClient:

        profile = BrowserProfile(
            impersonate=f"chrome_{version}",
            os=os,
        )

        return BrowserClient(profile)

    def create_firefox(
        self,
        version: str = "146",
        os: str = "windows",
    ) -> BrowserClient:

        profile = BrowserProfile(
            impersonate=f"firefox_{version}",
            os=os,
        )

        return BrowserClient(profile)

    def create_edge(
        self,
        version: str = "146",
        os: str = "windows",
    ) -> BrowserClient:

        profile = BrowserProfile(
            impersonate=f"edge_{version}",
            os=os,
        )

        return BrowserClient(profile)
```

Sử dụng:

```python
factory = BrowserClientFactory()

chrome = factory.create_chrome()

response = chrome.get(
    "https://httpbin.org/headers"
)

print(response.text)
```

---

# 11. Nhưng Factory này có đang hơi quá không?

Có.

Ở project nhỏ:

```python
BrowserClient(
    BrowserProfile(
        impersonate="chrome_146",
        os="windows",
    )
)
```

đã đủ.

Factory chỉ thực sự hữu ích khi application có:

```text
Profile configuration
Environment configuration
Plugin configuration
Profile pool
Dependency Injection
```

Do đó hiện tại chúng ta chỉ cần hiểu Pattern, **chưa cần xây Factory phức tạp**.

Đây là cách tránh abstraction quá mức.

---

# 12. RequestOptions

Chúng ta đã học RequestOptions ở Buổi 19.

Giờ đưa nó vào `BrowserClient`.

```python
from dataclasses import dataclass, field


@dataclass
class RequestOptions:
    timeout: float | None = None

    headers: dict[str, str] = field(
        default_factory=dict
    )

    params: dict = field(
        default_factory=dict
    )
```

Sau đó:

```python
class BrowserClient:

    def __init__(
        self,
        profile: BrowserProfile,
    ):
        self.profile = profile

        self.client = primp.Client(
            impersonate=profile.impersonate,
            impersonate_os=profile.os,
        )

    def get(
        self,
        url: str,
        *,
        options: RequestOptions | None = None,
    ):
        options = options or RequestOptions()

        return self.client.get(
            url,
            headers=options.headers,
            params=options.params,
            timeout=options.timeout,
        )
```

---

# 13. Nhưng có một vấn đề nhỏ

Ta đang truyền:

```python
params={}
headers={}
timeout=None
```

mọi request.

Không phải lúc nào cũng cần.

Ta có thể xây request kwargs:

```python
def _build_kwargs(
    options: RequestOptions,
) -> dict:

    kwargs = {}

    if options.headers:
        kwargs["headers"] = options.headers

    if options.params:
        kwargs["params"] = options.params

    if options.timeout is not None:
        kwargs["timeout"] = options.timeout

    return kwargs
```

Sau đó:

```python
def get(
    self,
    url: str,
    *,
    options: RequestOptions | None = None,
):
    options = options or RequestOptions()

    kwargs = self._build_kwargs(options)

    return self.client.get(
        url,
        **kwargs,
    )
```

Thiết kế này sạch hơn.

---

# 14. BrowserClient hoàn chỉnh

Đây là phiên bản tôi muốn bạn giữ lại.

```python
import primp

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BrowserProfile:
    impersonate: str
    os: str | None = None


@dataclass
class RequestOptions:
    timeout: float | None = None

    headers: dict[str, str] = field(
        default_factory=dict
    )

    params: dict = field(
        default_factory=dict
    )


class BrowserClient:

    def __init__(
        self,
        profile: BrowserProfile,
    ):
        self.profile = profile

        self.client = primp.Client(
            impersonate=profile.impersonate,
            impersonate_os=profile.os,
        )

    def _build_kwargs(
        self,
        options: RequestOptions,
    ) -> dict:

        kwargs = {}

        if options.headers:
            kwargs["headers"] = options.headers

        if options.params:
            kwargs["params"] = options.params

        if options.timeout is not None:
            kwargs["timeout"] = options.timeout

        return kwargs

    def get(
        self,
        url: str,
        *,
        options: RequestOptions | None = None,
    ):
        options = (
            options
            if options is not None
            else RequestOptions()
        )

        kwargs = self._build_kwargs(
            options
        )

        return self.client.get(
            url,
            **kwargs,
        )
```

---

# 15. Test

Tạo:

```text
test_browser_client.py
```

```python
from browser_client import (
    BrowserClient,
    BrowserProfile,
    RequestOptions,
)


def main():

    profile = BrowserProfile(
        impersonate="chrome_146",
        os="windows",
    )

    client = BrowserClient(profile)

    options = RequestOptions(
        timeout=10,
        headers={
            "Accept-Language": "vi-VN,vi;q=0.9",
        },
        params={
            "page": 1,
        },
    )

    response = client.get(
        "https://httpbin.org/get",
        options=options,
    )

    print("Status:", response.status_code)
    print("URL:", response.url)
    print()
    print(response.text)


if __name__ == "__main__":
    main()
```

---

# 16. BrowserClient hiện tại có trách nhiệm gì?

```text
BrowserClient
│
├── BrowserProfile
│
├── tạo primp.Client
│
├── giữ client sống lâu
│
├── GET
│
└── RequestOptions
```

Nó **chưa** có:

```text
❌ Retry
❌ Proxy Pool
❌ Rate Limit
❌ Error Classification
❌ Logging
❌ Metrics
```

Đó là chủ ý.

Những thành phần này sẽ xuất hiện ở **phần IV và V**.

---

# 17. Tại sao không cho Proxy vào BrowserProfile?

Sai:

```python
@dataclass
class BrowserProfile:

    impersonate: str
    os: str
    proxy: str
```

Vì:

```text
Chrome
+
Windows
```

là browser identity.

Trong khi:

```text
proxy
```

là network routing.

Hai khái niệm khác nhau:

```text
BrowserProfile
    │
    ├── Browser
    ├── Version
    └── OS

ProxyConfig
    │
    ├── URL
    └── Credentials
```

Sau này:

```text
BrowserClient
       │
       ├── BrowserProfile
       └── ProxyConfig
```

---

# 18. Và Cookies?

Cũng không đưa vào BrowserProfile.

Vì:

```text
BrowserProfile
```

là **persona configuration**.

Trong khi:

```text
Cookies
```

là **session state**.

Ta có:

```text
Browser Profile
       │
       ↓
Client
       │
       ↓
Session State
       │
       ├── Cookies
       ├── Authentication
       └── Connection state
```

Đây là một distinction rất quan trọng khi xây crawler.

---

# 19. Response Adapter

Bây giờ đến một vấn đề từ Buổi 29.

Application không nên phụ thuộc trực tiếp vào:

```python
primp.Response
```

Tạo:

```python
from dataclasses import dataclass


@dataclass
class FetchResponse:

    status_code: int

    url: str

    headers: dict

    content: bytes

    @property
    def text(self) -> str:

        return self.content.decode(
            "utf-8",
            errors="replace",
        )
```

Sau đó:

```python
def _adapt_response(
    response,
) -> FetchResponse:

    return FetchResponse(
        status_code=response.status_code,
        url=str(response.url),
        headers=dict(response.headers),
        content=response.content,
    )
```

Và:

```python
def get(...):

    response = self.client.get(...)

    return self._adapt_response(
        response
    )
```

---

# 20. Tại sao Adapter quan trọng?

Sau này:

```text
Application
     │
     ↓
FetchResponse
     ↑
     │
 ┌───┴────┐
 │        │
httpx   primp
```

Application không cần biết:

```text
httpx.Response
```

hay:

```text
primp.Response
```

Nó chỉ biết:

```python
response.status_code
response.url
response.headers
response.text
response.content
```

Đây chính là **Adapter Pattern**.

---

# 21. Kiến trúc sau Buổi 30

Đây là kiến trúc quan trọng nhất của toàn bộ Phần III:

```text
                    Application
                         │
                         ↓
                  Fetcher Interface
                         │
                         ↓
                   BrowserClient
                         │
                 ┌───────┴────────┐
                 ↓                ↓
          BrowserProfile      RequestOptions
                 │
                 ↓
            primp.Client
                 │
       ┌─────────┼─────────┐
       ↓         ↓         ↓
      TLS      HTTP/2    Headers
       │         │         │
       └─────────┼─────────┘
                 ↓
               HTTP
                 ↓
             Response
                 ↓
          Response Adapter
                 ↓
            FetchResponse
                 ↓
             Application
```

---

# 22. Clean Architecture

Đặt vào architecture Novel Crawler:

```text
src/
└── crawler/
    │
    ├── domain/
    │
    │   └── ...
    │
    ├── application/
    │
    │   └── ...
    │
    └── infrastructure/
        │
        └── http/
            │
            ├── browser_profile.py
            ├── browser_client.py
            ├── fetch_response.py
            └── primp_adapter.py
```

Điểm quan trọng:

```text
domain
   ↓
KHÔNG import primp
```

Chỉ:

```text
infrastructure
       ↓
     primp
```

Đây chính là Dependency Rule của Clean Architecture.

---

# 23. DDD perspective

`BrowserProfile` có thể được xem như một **configuration value object** ở infrastructure boundary.

Nhưng đừng vội đưa nó vào Domain.

Novel Domain không quan tâm:

```text
Chrome 146
TLS
HTTP/2
User-Agent
```

Domain quan tâm:

```text
Novel
Chapter
ChapterContent
CrawlTask
CrawlResult
```

Do đó:

```text
Domain
   │
   └── Novel / Chapter


Infrastructure
   │
   └── BrowserProfile / BrowserClient / primp
```

---

# 24. SOLID

`BrowserClient` hiện tại đang phục vụ khá rõ một responsibility:

```text
BrowserClient
    →
quản lý HTTP client theo browser profile
```

Dependency inversion:

```text
Application
     ↓
Fetcher Protocol
     ↓
BrowserClient
     ↓
primp
```

Open/Closed:

```text
Fetcher
  ├── HttpxFetcher
  └── PrimpFetcher
```

Sau này muốn thêm:

```text
CurlFetcher
AiohttpFetcher
MockFetcher
```

không cần sửa Application.

---

# 25. Một điểm cực kỳ quan trọng: BrowserClient không phải Fetcher cuối cùng

Đây là nơi chúng ta cần giữ architecture sạch.

Hiện tại:

```text
BrowserClient
```

là một abstraction của:

```text
browser-aware HTTP client
```

Nhưng production crawler sẽ cần:

```text
Fetcher
│
├── Timeout
├── Retry
├── Proxy
├── Browser Profile
├── Error Classification
├── Logging
└── Metrics
```

Vì vậy sau này:

```text
PrimpFetcher
     │
     └── BrowserClient
```

hoặc thậm chí:

```text
PrimpFetcher
     │
     ├── BrowserProfile
     ├── ProxyStrategy
     ├── RetryPolicy
     └── RateLimiter
```

Chúng ta sẽ quyết định chi tiết sau khi học các phần tiếp theo.

**Không cần nhồi tất cả vào Buổi 30.**

---

# 26. Một phiên bản thực tế hơn

Sau khi hiểu architecture, ta có thể viết:

```python
import primp

from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserProfile:
    impersonate: str
    os: str | None = None


class BrowserClient:

    def __init__(
        self,
        profile: BrowserProfile,
    ):
        self.profile = profile

        self._client = primp.Client(
            impersonate=profile.impersonate,
            impersonate_os=profile.os,
        )

    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict | None = None,
        timeout: float | None = None,
    ):
        return self._client.get(
            url,
            headers=headers,
            params=params,
            timeout=timeout,
        )
```

Đây thực ra là version tôi khuyên dùng **ở thời điểm hiện tại**.

Không cần:

```text
Factory
Builder
Strategy
Manager
Registry
Pool
```

chỉ để tạo một HTTP client.

---

# 27. Test nhiều browser

Ta có thể tạo:

```python
profiles = [
    BrowserProfile(
        impersonate="chrome_146",
        os="windows",
    ),

    BrowserProfile(
        impersonate="firefox_146",
        os="windows",
    ),

    BrowserProfile(
        impersonate="edge_146",
        os="windows",
    ),
]
```

Sau đó:

```python
for profile in profiles:

    client = BrowserClient(profile)

    response = client.get(
        "https://httpbin.org/headers"
    )

    print(
        profile.impersonate,
        response.status_code,
    )
```

Điều này cho thấy `BrowserClient` đã trở thành một **stable boundary**.

---

# 28. Profile Configuration

Đừng hard-code profile trong Application:

```python
BrowserProfile(
    impersonate="chrome_146",
    os="windows",
)
```

khắp nơi.

Có thể đưa vào configuration:

```python
@dataclass(frozen=True)
class BrowserConfig:
    profile: str
    os: str | None
```

Ví dụ:

```python
config = BrowserConfig(
    profile="chrome_146",
    os="windows",
)
```

Sau đó:

```python
client = BrowserClient(
    BrowserProfile(
        impersonate=config.profile,
        os=config.os,
    )
)
```

Sau này config có thể đến từ:

```text
.env
YAML
TOML
CLI
Database
Plugin config
```

---

# 29. `random` có nên dùng không?

`primp` hiện có profile:

```text
random
```

và source API cũng có cơ chế random browser/OS profile. ([PyPI][1])

Nhưng **không nên** biến:

```text
mỗi request
    ↓
random browser
```

thành chiến lược mặc định.

Ví dụ:

```text
Request 1 → Chrome
Request 2 → Firefox
Request 3 → Safari
Request 4 → Edge
```

sẽ tạo ra một identity rất thiếu ổn định.

Tốt hơn:

```text
BrowserClient A
    ↓
Chrome 146 + Windows
    ↓
nhiều request
```

Nếu sau này cần pool profile:

```text
BrowserProfilePool
       │
       ├── Chrome 146 + Windows
       ├── Chrome 147 + Windows
       ├── Firefox 146 + Windows
       └── Edge 146 + Windows
```

thì đó sẽ là một **strategy riêng**, không nhét vào `BrowserClient`.

---

# 30. Bài tập thực hành

## Bài 1 — Chrome

```python
profile = BrowserProfile(
    impersonate="chrome_146",
    os="windows",
)
```

Gọi:

```text
https://httpbin.org/headers
```

---

## Bài 2 — Firefox

Đổi:

```python
impersonate="firefox_146"
```

So sánh headers.

---

## Bài 3 — Edge

Đổi:

```python
impersonate="edge_146"
```

---

## Bài 4 — TLS

Gọi:

```text
https://tls.peet.ws/api/all
```

và so sánh:

```text
Chrome
Firefox
Edge
```

---

## Bài 5 — RequestOptions

Test:

```python
options = RequestOptions(
    timeout=5,
    headers={
        "Referer": "https://example.com/",
    },
    params={
        "page": 2,
    },
)
```

Sau đó:

```python
response = client.get(
    url,
    options=options,
)
```

---

# 31. Bài tập kiến trúc

Tạo:

```text
lesson30/
│
├── browser_profile.py
├── browser_client.py
├── request_options.py
├── fetch_response.py
│
└── main.py
```

Mục tiêu:

```text
main.py
   ↓
BrowserProfile
   ↓
BrowserClient
   ↓
primp
   ↓
HTTP
   ↓
FetchResponse
```

Không để:

```python
main.py
```

import trực tiếp:

```python
import primp
```

Đây là bài tập rất tốt để luyện **Dependency Inversion**.

---

# 32. Tổng kết toàn bộ Phần III

Chúng ta bắt đầu:

```text
21. Vì sao cần impersonation
```

và kết thúc:

```text
30. BrowserClient
```

Toàn bộ kiến thức hiện tại:

```text
                 BrowserClient
                      │
                      ↓
                BrowserProfile
                      │
          ┌───────────┼───────────┐
          ↓           ↓           ↓
       Browser       OS         Version
          │
          ↓
       primp
          │
    ┌─────┼─────┐
    ↓     ↓     ↓
   TLS  HTTP/2 Headers
```

và:

```text
Application
      ↓
Fetcher Interface
      ↓
BrowserClient
      ↓
primp
```

---

# 33. Điều quan trọng nhất cần nhớ

### Không phải:

```text
BrowserClient = primp.Client
```

Mà:

```text
BrowserClient
    =
application-facing abstraction
    ↓
primp.Client
```

### Không phải:

```text
BrowserProfile = User-Agent
```

Mà:

```text
BrowserProfile
    ↓
Browser + Version + OS
    ↓
primp
    ↓
TLS + HTTP/2 + Headers
```

### Không phải:

```text
BrowserClient = toàn bộ Fetcher
```

Mà:

```text
BrowserClient
      ↓
một building block

PrimpFetcher
      ↓
production Fetcher
```

Đây là nền tảng để sang phần IV.

---

# Roadmap sau Buổi 30

```text
PHẦN I — CƠ BẢN
01 → 20                           ✅

PHẦN II — HTTP CLIENT
11 → 20                           ✅

PHẦN III — BROWSER IMPERSONATION
21. Vì sao cần impersonation       ✅
22. Chrome fingerprint             ✅
23. Firefox / Safari / Edge        ✅
24. impersonate_os                 ✅
25. TLS fingerprint                ✅
26. HTTP/2                         ✅
27. Headers + fingerprint          ✅
28. Fingerprint thực tế            ✅
29. httpx vs primp                 ✅
30. BrowserClient                  ✅
```

### PHẦN IV — ASYNC + CRAWLER

```text
31. AsyncClient
32. async GET
33. Concurrent Requests
34. Semaphore
35. Timeout + Retry
36. Proxy Pool
37. User-Agent / Browser Profile Pool
38. Rate Limiting
39. Fetcher Architecture
40. Async Novel Fetcher
```

Điểm chuyển tiếp rất đẹp là **Buổi 31 — `AsyncClient`**: chúng ta sẽ lấy chính `BrowserClient` vừa xây, chuyển sang async, rồi từ đó đi tới concurrent chapter fetching cho Novel Crawler. `primp 2.0.1` hiện có `AsyncClient` chính thức và ví dụ sử dụng `async with`, nên phần IV sẽ tiếp tục trực tiếp từ kiến trúc hôm nay. ([PyPI][1])

[1]: https://pypi.org/project/primp/2.0.1/?utm_source=chatgpt.com "primp · PyPI"
[2]: https://docs.rs/primp/latest/primp/imp/index.html?utm_source=chatgpt.com "primp::imp - Rust"
