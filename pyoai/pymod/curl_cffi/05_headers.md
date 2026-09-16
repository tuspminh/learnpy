# Buổi 5 — Headers chuyên sâu với `curl_cffi`

Hôm nay chúng ta đi sâu vào **HTTP Headers**, đặc biệt theo hướng phục vụ Novel Crawler.

Sau buổi này bạn sẽ hiểu:

```text
HTTP Request
│
├── URL
├── Method
├── Query
├── Headers
│   ├── User-Agent
│   ├── Accept
│   ├── Accept-Language
│   ├── Referer
│   ├── Origin
│   ├── Authorization
│   └── Cookie
│
└── Body
```

Và cuối buổi bắt đầu thiết kế:

```text
HeaderProvider
UserAgentProvider
```

---

# 1. Header là gì?

HTTP request:

```text
GET /chapter/1 HTTP/1.1
Host: example.com
User-Agent: ...
Accept: text/html
```

Các dòng:

```text
Host: example.com
User-Agent: ...
Accept: text/html
```

chính là **HTTP headers**.

Trong `curl_cffi`:

```python
from curl_cffi import requests


response = requests.get(
    "https://example.com",
    headers={
        "User-Agent": "MyNovelCrawler/1.0",
        "Accept": "text/html",
    },
)
```

---

# 2. `headers` là dictionary

Cách cơ bản:

```python
headers = {
    "User-Agent": "MyNovelCrawler/1.0",
    "Accept": "text/html",
}
```

Sau đó:

```python
response = requests.get(
    url,
    headers=headers,
)
```

Có thể tạo riêng:

```python
class HeaderProvider:
    def get(self) -> dict[str, str]:
        return {
            "User-Agent": "MyNovelCrawler/1.0",
            "Accept": "text/html",
        }
```

Nhưng abstraction này chưa cần vội. Chúng ta sẽ xây dần.

---

# 3. `User-Agent`

Đây là header quan trọng nhất khi crawler.

Ví dụ:

```python
headers = {
    "User-Agent": "MyNovelCrawler/1.0",
}
```

Request:

```python
response = requests.get(
    "https://httpbin.org/headers",
    headers=headers,
)

print(response.json())
```

Server sẽ nhận User-Agent mà bạn gửi.

---

# 4. User-Agent không phải browser fingerprint

Đây là điểm rất quan trọng trước khi sang phần `impersonate`.

Nếu bạn gửi:

```python
headers = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    )
}
```

thì bạn chỉ đang thay **HTTP User-Agent header**.

Nó không có nghĩa rằng toàn bộ request đã trở thành Chrome.

Có nhiều đặc điểm khác của HTTP/TLS/browser behavior.

Đó là lý do `curl_cffi` có:

```python
impersonate="chrome"
```

Phần này sẽ học riêng.

---

# 5. `Accept`

Header:

```text
Accept
```

cho server biết client mong muốn loại nội dung nào.

Ví dụ crawler HTML:

```python
headers = {
    "Accept": "text/html",
}
```

Có thể rộng hơn:

```python
headers = {
    "Accept": (
        "text/html,"
        "application/xhtml+xml,"
        "application/xml;q=0.9,"
        "*/*;q=0.8"
    ),
}
```

Trong crawler:

```text
Novel page
    ↓
HTML
    ↓
Accept: text/html
```

---

# 6. `Accept-Language`

Với website tiếng Việt:

```python
headers = {
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
}
```

Server có thể sử dụng thông tin này để lựa chọn ngôn ngữ response.

Ví dụ:

```text
vi-VN
vi
en
```

Đây là **preference**, không phải mệnh lệnh server bắt buộc phải trả tiếng Việt.

---

# 7. `Referer`

Ví dụ crawler đang ở:

```text
https://example.com/novel/foo
```

và request:

```text
https://example.com/novel/foo/chapter-1
```

Có thể có:

```python
headers = {
    "Referer": "https://example.com/novel/foo",
}
```

Request:

```python
response = requests.get(
    chapter_url,
    headers=headers,
)
```

`Referer` có thể được website sử dụng để biết request đến từ đâu.

---

# 8. Chú ý chính tả: `Referer`

HTTP header chuẩn được viết:

```text
Referer
```

không phải:

```text
Referrer
```

Tên "Referer" là cách viết lịch sử của HTTP specification.

---

# 9. `Origin`

`Origin` thường quan trọng trong các request liên quan tới web application và CORS.

Ví dụ:

```python
headers = {
    "Origin": "https://example.com",
}
```

Có thể gặp:

```text
Origin: https://example.com
```

Đặc biệt khi làm việc với:

```text
AJAX
API
POST
CORS
web application
```

Không nên tùy tiện thêm `Origin` vào mọi request crawler.

---

# 10. `Authorization`

API có thể yêu cầu:

```text
Authorization: Bearer <token>
```

Ví dụ:

```python
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
}
```

Sau đó:

```python
response = requests.get(
    "https://example.com/api/books",
    headers=headers,
)
```

Trong application thực tế, **không hard-code token vào source code**.

Không nên:

```python
TOKEN = "abc123..."
```

Thay vào đó dùng:

```text
environment variable
secret manager
configuration
```

---

# 11. `Cookie`

Cookie có thể gửi thông qua `cookies=`:

```python
response = requests.get(
    url,
    cookies={
        "session": "abc123",
    },
)
```

Hoặc gửi trực tiếp bằng header:

```python
headers = {
    "Cookie": "session=abc123",
}
```

Thông thường nên ưu tiên:

```python
cookies={
    ...
}
```

thay vì tự xây:

```text
Cookie: a=1; b=2; c=3
```

Vì cookie có cơ chế quản lý riêng.

Phần Cookie/Session sẽ học kỹ sau.

---

# 12. Header hoàn chỉnh cho HTML crawler

Ví dụ:

```python
from curl_cffi import requests


headers = {
    "User-Agent": "MyNovelCrawler/1.0",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
}

response = requests.get(
    "https://example.com",
    headers=headers,
    timeout=10,
)

print(response.status_code)
```

Đây là một cấu hình hợp lý để bắt đầu.

---

# 13. Không nên copy toàn bộ header từ Chrome

Bạn có thể thấy DevTools của browser có rất nhiều header:

```text
Accept
Accept-Encoding
Accept-Language
Cache-Control
Connection
Cookie
Host
Referer
Sec-CH-UA
Sec-Fetch-Dest
Sec-Fetch-Mode
Sec-Fetch-Site
User-Agent
...
```

Không nên ngay lập tức copy tất cả:

```python
headers = {
    # 20 headers...
}
```

vào crawler.

Vì:

1. Một số header do browser tự quản lý.
2. Một số header phụ thuộc context.
3. Một số header không cần thiết.
4. Header giả không làm request tự động trở thành browser.

Nguyên tắc:

> **Chỉ gửi những header thực sự cần thiết.**

---

# 14. Header mặc định

HTTP client có thể tự thêm một số thông tin cần thiết vào request.

Vì vậy:

```python
requests.get(url)
```

không có nghĩa request thực tế chỉ có:

```text
GET URL
```

HTTP client và underlying library có thể xây dựng thêm các thành phần cần thiết.

Đừng phụ thuộc vào việc mọi header đều phải do bạn tự khai báo.

---

# 15. Kiểm tra request bằng `httpbin`

Đây là bài tập cực kỳ hữu ích.

```python
from curl_cffi import requests


response = requests.get(
    "https://httpbin.org/headers",
    headers={
        "User-Agent": "MyNovelCrawler/1.0",
        "Accept": "text/html",
        "Accept-Language": "vi-VN",
    },
)

print(response.json())
```

Bạn có thể quan sát:

```text
server nhận được gì
```

Thay vì đoán.

---

# 16. Header case

Bạn có thể viết:

```python
headers = {
    "User-Agent": "...",
}
```

hoặc:

```python
headers = {
    "user-agent": "...",
}
```

HTTP header names về bản chất không phân biệt hoa thường.

Nhưng trong project nên thống nhất convention:

```python
"User-Agent"
"Accept"
"Accept-Language"
"Referer"
```

Dễ đọc hơn.

---

# 17. Không mutate header global

Một lỗi thiết kế thường gặp:

```python
DEFAULT_HEADERS = {
    "User-Agent": "...",
}


def fetch(url):
    DEFAULT_HEADERS["Referer"] = url

    ...
```

Điều này nguy hiểm khi crawler chạy concurrent.

Ví dụ:

```text
Worker 1
    ↓
DEFAULT_HEADERS["Referer"] = A

Worker 2
    ↓
DEFAULT_HEADERS["Referer"] = B
```

Worker 1 có thể vô tình gửi header của Worker 2.

---

# 18. Tạo headers mới cho mỗi request

Tốt hơn:

```python
DEFAULT_HEADERS = {
    "Accept": "text/html",
}


def build_headers(user_agent: str):
    return {
        **DEFAULT_HEADERS,
        "User-Agent": user_agent,
    }
```

Sau đó:

```python
headers = build_headers(
    "MyNovelCrawler/1.0"
)
```

Mỗi request có dictionary riêng.

Đây là thói quen rất tốt khi crawler chạy multi-thread/multi-task.

---

# 19. `HeaderProvider`

Bây giờ bắt đầu abstraction.

```python
from abc import ABC, abstractmethod


class HeaderProvider(ABC):

    @abstractmethod
    def get(self) -> dict[str, str]:
        pass
```

Implementation:

```python
class DefaultHeaderProvider(HeaderProvider):

    def get(self) -> dict[str, str]:
        return {
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
        }
```

Fetcher:

```python
class Fetcher:

    def __init__(self, header_provider):
        self._header_provider = header_provider

    def fetch(self, url: str):
        headers = self._header_provider.get()

        return requests.get(
            url,
            headers=headers,
            timeout=10,
        )
```

Nhưng hiện tại vẫn còn một vấn đề:

```text
HeaderProvider
      │
      └── User-Agent?
```

---

# 20. Tách `UserAgentProvider`

Vì User-Agent sẽ có logic riêng:

```text
UserAgentProvider
       ↓
   User-Agent
```

Interface:

```python
from abc import ABC, abstractmethod


class UserAgentProvider(ABC):

    @abstractmethod
    def get(self) -> str:
        pass
```

Implementation đơn giản:

```python
class StaticUserAgentProvider(UserAgentProvider):

    def __init__(self, user_agent: str):
        self._user_agent = user_agent

    def get(self) -> str:
        return self._user_agent
```

---

# 21. Ghép `HeaderProvider` + `UserAgentProvider`

```python
class DefaultHeaderProvider(HeaderProvider):

    def __init__(
        self,
        user_agent_provider: UserAgentProvider,
    ):
        self._user_agent_provider = user_agent_provider

    def get(self) -> dict[str, str]:
        return {
            "User-Agent": self._user_agent_provider.get(),
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
        }
```

Đây là Dependency Injection:

```text
Fetcher
   │
   ▼
HeaderProvider
   │
   ▼
UserAgentProvider
```

---

# 22. Nhưng đừng abstraction quá mức

Đừng tạo:

```text
UserAgentFactory
HeaderFactory
AcceptHeaderBuilder
RefererHeaderBuilder
OriginHeaderBuilder
CookieHeaderBuilder
```

cho một crawler nhỏ.

Ta chỉ cần:

```text
HeaderProvider
      │
      └── UserAgentProvider
```

là đủ ở giai đoạn hiện tại.

---

# 23. Một Fetcher hoàn chỉnh hơn

```python
from curl_cffi import requests


class StaticUserAgentProvider:

    def __init__(self, user_agent: str):
        self._user_agent = user_agent

    def get(self) -> str:
        return self._user_agent


class HeaderProvider:

    def __init__(self, user_agent_provider):
        self._user_agent_provider = user_agent_provider

    def get(self) -> dict[str, str]:
        return {
            "User-Agent": self._user_agent_provider.get(),
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
        }


class Fetcher:

    def __init__(self, header_provider):
        self._header_provider = header_provider

    def fetch(self, url: str):
        headers = self._header_provider.get()

        return requests.get(
            url,
            headers=headers,
            timeout=10,
        )


def main():
    user_agent_provider = StaticUserAgentProvider(
        "MyNovelCrawler/1.0"
    )

    header_provider = HeaderProvider(
        user_agent_provider
    )

    fetcher = Fetcher(
        header_provider
    )

    response = fetcher.fetch(
        "https://httpbin.org/headers"
    )

    print(response.json())


if __name__ == "__main__":
    main()
```

---

# 24. Kiến trúc hiện tại

Sau Buổi 5, ta có:

```text
                    Application
                         │
                         ▼
                      Fetcher
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
       HeaderProvider       HttpClient (sau này)
              │
              ▼
      UserAgentProvider
              │
              ▼
       curl_cffi requests
```

Nhưng ta vẫn còn một vấn đề lớn:

```text
Fetcher
   ↓
requests.get()
```

Fetcher vẫn trực tiếp biết `curl_cffi`.

Ở các buổi tiếp theo ta sẽ xử lý bằng:

```text
HttpClient Interface
        ↓
CurlCffiHttpClient
        ↓
curl_cffi
```

---

# 25. Một nguyên tắc quan trọng cho crawler

Không nên nghĩ:

```text
"Càng nhiều headers càng giống browser"
```

Thay vào đó:

```text
Request
  ↓
Headers cần thiết
  ↓
Server behavior
  ↓
Quan sát response
  ↓
Điều chỉnh nếu cần
```

Đặc biệt:

```text
User-Agent
```

không phải một cơ chế bảo mật.

Và:

```text
impersonate
```

không nên được hiểu đơn giản là "đổi User-Agent".

Chúng ta sẽ đi sâu vào browser impersonation ở phần riêng.

---

# Bài tập Buổi 5

Tạo:

```text
lesson05.py
```

## Bài 1

Gửi request:

```python
requests.get(
    "https://httpbin.org/headers",
    headers={
        "User-Agent": "MyNovelCrawler/1.0",
        "Accept": "text/html",
        "Accept-Language": "vi-VN,vi;q=0.9",
    },
)
```

Kiểm tra server nhận được gì.

---

## Bài 2

Tạo:

```python
class StaticUserAgentProvider:
    ...
```

và:

```python
class HeaderProvider:
    ...
```

Sau đó:

```text
UserAgentProvider
       ↓
HeaderProvider
       ↓
Fetcher
       ↓
curl_cffi
```

---

## Bài 3 — suy nghĩ kiến trúc

Hãy thử trả lời:

> Nếu ngày mai ta muốn đổi từ `curl_cffi` sang `httpx`, những class nào **nên phải sửa**, và những class nào **không nên biết việc thay đổi đó**?

Đáp án kiến trúc mà chúng ta đang hướng tới:

```text
Domain
   ↓
Application
   ↓
HttpClient Interface
   ↓
Infrastructure
   ├── CurlCffiHttpClient
   └── HttpxHttpClient
```

Đây chính là nền để sau này Fetcher của Novel Crawler có thể thay đổi HTTP engine mà **Parser, Use Case và Domain không cần biết**.

**Buổi 6:** `Timeout` chuyên sâu — connect timeout, read timeout, total timeout, timeout exception và thiết kế `TimeoutConfig` cho crawler.
