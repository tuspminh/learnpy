# Buổi 19 — Request Options

Ở Buổi 18, chúng ta có:

```text
PrimpFetcher
├── Client
├── Default Headers
├── Default Params
└── Default Timeout
```

Hôm nay ta giải quyết vấn đề:

> **Nếu một request cần cấu hình khác với mặc định thì thiết kế thế nào?**

Ví dụ:

```text
Request A → timeout 10s
Request B → timeout 30s

Request A → Referer A
Request B → Referer B

Request A → page=1
Request B → page=2
```

Mục tiêu cuối bài:

```text
Application
     ↓
RequestOptions
     ↓
Fetcher
     ↓
Primp
```

---

# 1. Vì sao cần Request Options?

Hiện tại ta có:

```python
response = fetcher.get(
    url,
    params={"page": 2},
    headers={"Referer": novel_url},
    timeout=20,
)
```

Khi số lượng option tăng lên:

```python
response = fetcher.get(
    url,
    params=...,
    headers=...,
    timeout=...,
    proxy=...,
    verify=...,
    ...
)
```

API bắt đầu dài.

Đến một lúc:

```text
get(
    url,
    params,
    headers,
    timeout,
    proxy,
    verify,
    ...
)
```

rất khó quản lý.

Ta có thể gom các option **thuộc về một request** vào một object.

---

# 2. Request Options là gì?

Ví dụ:

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

Một request:

```python
options = RequestOptions(
    timeout=30,
    headers={
        "Referer": "https://example.com/novel"
    },
    params={
        "page": 2
    },
)
```

Ta có:

```text
RequestOptions
├── timeout
├── headers
└── params
```

---

# 3. Vì sao dùng `default_factory`?

Không nên:

```python
@dataclass
class RequestOptions:

    headers: dict = {}

    params: dict = {}
```

Vì mutable default.

Nên:

```python
@dataclass
class RequestOptions:

    headers: dict[str, str] = field(
        default_factory=dict
    )

    params: dict = field(
        default_factory=dict
    )
```

Mỗi instance có dictionary riêng.

```text
options1.headers
        ↓
   dictionary A

options2.headers
        ↓
   dictionary B
```

---

# 4. Request Options khác Default Config

Đây là điểm quan trọng nhất của bài.

### Default config

```text
Fetcher
├── default timeout = 10
├── default headers
└── default params
```

Ổn định:

```text
request 1
request 2
request 3
request 4
```

### Request Options

```text
Request 1
└── timeout = 30

Request 2
└── timeout = 5

Request 3
└── timeout = 60
```

Sơ đồ:

```text
Fetcher Defaults
       │
       │
       ├───────────────┐
       │               │
       ▼               ▼
 Request 1          Request 2
 Options            Options
 timeout=30         timeout=5
```

---

# 5. Ví dụ đơn giản

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


options = RequestOptions(
    timeout=30,
    headers={
        "X-Test": "hello",
    },
    params={
        "page": 2,
    },
)

print(options)
```

Kết quả conceptually:

```text
RequestOptions(
    timeout=30,
    headers={'X-Test': 'hello'},
    params={'page': 2}
)
```

---

# 6. Dùng với `PrimpFetcher`

Ta xây:

```python
import primp
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


class PrimpFetcher:

    def __init__(
        self,
        timeout: float = 10,
        default_headers: dict[str, str] | None = None,
        default_params: dict | None = None,
    ):

        self.client = primp.Client(
            headers=default_headers or {}
        )

        self.default_timeout = timeout

        self.default_params = (
            default_params.copy()
            if default_params
            else {}
        )

    def get(
        self,
        url: str,
        *,
        options: RequestOptions | None = None,
    ):

        options = options or RequestOptions()

        timeout = (
            options.timeout
            if options.timeout is not None
            else self.default_timeout
        )

        params = self.default_params.copy()

        params.update(
            options.params
        )

        return self.client.get(
            url,
            params=params,
            headers=options.headers,
            timeout=timeout,
        )
```

---

# 7. Sử dụng

Default:

```python
fetcher = PrimpFetcher(
    timeout=10,
    default_headers={
        "Accept": "text/html",
        "Accept-Language": "vi-VN",
    },
    default_params={
        "lang": "vi",
    },
)
```

Request bình thường:

```python
response = fetcher.get(
    "https://httpbin.org/get"
)
```

Nó dùng:

```text
timeout = 10
lang = vi
default headers
```

---

# 8. Request override timeout

```python
response = fetcher.get(
    "https://httpbin.org/delay/5",

    options=RequestOptions(
        timeout=20,
    ),
)
```

Luồng:

```text
Default timeout
       │
      10s
       │
       ▼
RequestOptions
       │
      20s
       │
       ▼
Final timeout = 20s
```

---

# 9. Request-specific Params

```python
response = fetcher.get(
    "https://httpbin.org/get",

    options=RequestOptions(
        params={
            "page": 5,
        }
    ),
)
```

Nếu default:

```python
{
    "lang": "vi"
}
```

thì final:

```python
{
    "lang": "vi",
    "page": 5,
}
```

---

# 10. Request-specific Headers

Ví dụ chapter page:

```python
response = fetcher.get(
    chapter_url,

    options=RequestOptions(
        headers={
            "Referer": novel_url,
        }
    ),
)
```

Ta có:

```text
Default Headers
├── Accept
└── Accept-Language

Request Headers
└── Referer
```

---

# 11. Một vấn đề: merge Headers

Trong code trước:

```python
headers=options.headers
```

có một vấn đề conceptual.

Nếu `primp` xử lý request headers theo kiểu override toàn bộ collection, ta có thể mất default headers.

Ta nên chủ động tạo:

```python
final_headers = self.default_headers.copy()

final_headers.update(
    options.headers
)
```

Do đó Fetcher nên lưu default headers:

```python
self.default_headers = (
    default_headers.copy()
    if default_headers
    else {}
)
```

Sau đó:

```python
final_headers = self.default_headers.copy()

final_headers.update(
    options.headers
)
```

---

# 12. Fetcher hoàn chỉnh hơn

```python
import primp

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


class PrimpFetcher:

    def __init__(
        self,
        timeout: float = 10,
        default_headers: dict[str, str] | None = None,
        default_params: dict | None = None,
    ):

        self.default_timeout = timeout

        self.default_headers = (
            default_headers.copy()
            if default_headers
            else {}
        )

        self.default_params = (
            default_params.copy()
            if default_params
            else {}
        )

        self.client = primp.Client(
            headers=self.default_headers
        )

    def get(
        self,
        url: str,
        *,
        options: RequestOptions | None = None,
    ):

        options = options or RequestOptions()

        timeout = (
            options.timeout
            if options.timeout is not None
            else self.default_timeout
        )

        final_headers = (
            self.default_headers.copy()
        )

        final_headers.update(
            options.headers
        )

        final_params = (
            self.default_params.copy()
        )

        final_params.update(
            options.params
        )

        return self.client.get(
            url,
            headers=final_headers,
            params=final_params,
            timeout=timeout,
        )
```

---

# 13. Nhưng có một chi tiết architecture

Ta đang có:

```python
self.client = primp.Client(
    headers=self.default_headers
)
```

và lại:

```python
self.client.get(
    headers=final_headers
)
```

Tức là default headers được cấu hình **hai tầng**.

Không cần thiết.

Có thể chọn một chiến lược rõ ràng.

### Strategy A

Client giữ default headers:

```text
Client
└── default headers
```

Request chỉ truyền:

```text
request-specific headers
```

### Strategy B

Fetcher giữ default headers:

```text
Fetcher
└── default headers
```

Mỗi request merge rồi truyền xuống:

```text
Fetcher
   ↓
final headers
   ↓
Client
```

Ở giai đoạn học này, **Strategy B dễ hiểu hơn khi chúng ta muốn kiểm soát việc merge**.

---

# 14. Thiết kế tôi khuyên dùng ở bài này

```python
self.client = primp.Client()
```

và:

```python
final_headers = self.default_headers.copy()

final_headers.update(
    options.headers
)
```

Sau đó:

```python
self.client.get(
    url,
    headers=final_headers,
    params=final_params,
    timeout=timeout,
)
```

Toàn bộ merge nằm ở:

```text
PrimpFetcher
```

không phụ thuộc vào semantics merge của client.

---

# 15. Phiên bản sạch

```python
import primp

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


class PrimpFetcher:

    def __init__(
        self,
        timeout: float = 10,
        default_headers: dict[str, str] | None = None,
        default_params: dict | None = None,
    ):

        self.client = primp.Client()

        self.default_timeout = timeout

        self.default_headers = (
            default_headers.copy()
            if default_headers
            else {}
        )

        self.default_params = (
            default_params.copy()
            if default_params
            else {}
        )

    def get(
        self,
        url: str,
        *,
        options: RequestOptions | None = None,
    ):

        options = options or RequestOptions()

        final_timeout = (
            options.timeout
            if options.timeout is not None
            else self.default_timeout
        )

        final_headers = (
            self.default_headers.copy()
        )

        final_headers.update(
            options.headers
        )

        final_params = (
            self.default_params.copy()
        )

        final_params.update(
            options.params
        )

        return self.client.get(
            url,
            headers=final_headers,
            params=final_params,
            timeout=final_timeout,
        )
```

---

# 16. Test hoàn chỉnh

Tạo:

```text
lesson_19.py
```

```python
import primp

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


class PrimpFetcher:

    def __init__(
        self,
        timeout: float = 10,
        default_headers: dict[str, str] | None = None,
        default_params: dict | None = None,
    ):

        self.client = primp.Client()

        self.default_timeout = timeout

        self.default_headers = (
            default_headers.copy()
            if default_headers
            else {}
        )

        self.default_params = (
            default_params.copy()
            if default_params
            else {}
        )

    def get(
        self,
        url: str,
        *,
        options: RequestOptions | None = None,
    ):

        options = options or RequestOptions()

        final_timeout = (
            options.timeout
            if options.timeout is not None
            else self.default_timeout
        )

        final_headers = (
            self.default_headers.copy()
        )

        final_headers.update(
            options.headers
        )

        final_params = (
            self.default_params.copy()
        )

        final_params.update(
            options.params
        )

        return self.client.get(
            url,
            headers=final_headers,
            params=final_params,
            timeout=final_timeout,
        )


def main():

    fetcher = PrimpFetcher(
        timeout=10,

        default_headers={
            "Accept": "text/html",
            "Accept-Language": "vi-VN",
        },

        default_params={
            "lang": "vi",
        },
    )

    response = fetcher.get(
        "https://httpbin.org/get",

        options=RequestOptions(
            params={
                "page": 2,
            },
            headers={
                "X-Crawler": "NovelCrawler",
            },
            timeout=20,
        ),
    )

    print("Status:", response.status_code)
    print("URL:", response.url)
    print()
    print(response.text)


if __name__ == "__main__":
    main()
```

---

# 17. Kiểm tra kết quả

Ta kỳ vọng URL có:

```text
lang=vi
page=2
```

và headers có:

```text
Accept
Accept-Language
X-Crawler
```

Timeout request:

```text
20
```

thay vì default:

```text
10
```

---

# 18. Request Options trong Novel Crawler

Đây là chỗ nó bắt đầu có ý nghĩa.

Giả sử:

```text
Novel
 ├── listing
 ├── detail
 ├── chapter 1
 ├── chapter 2
 └── image
```

Mỗi loại request có thể có option khác nhau.

### Listing

```python
RequestOptions(
    params={
        "page": 2,
    }
)
```

### Chapter

```python
RequestOptions(
    headers={
        "Referer": novel_url,
    }
)
```

### Slow endpoint

```python
RequestOptions(
    timeout=30,
)
```

Architecture:

```text
Crawler
   │
   ├── Listing Request
   │      └── RequestOptions
   │
   ├── Novel Request
   │      └── RequestOptions
   │
   └── Chapter Request
          └── RequestOptions
                │
                ▼
             Fetcher
                │
                ▼
              primp
```

---

# 19. Request Options không phải Domain Model

Đừng đặt:

```text
domain/
└── RequestOptions.py
```

vì:

```text
RequestOptions
```

là HTTP/client concern.

Nó thuộc infrastructure/application boundary, ví dụ:

```text
infrastructure/
└── http/
    ├── primp_fetcher.py
    └── request_options.py
```

hoặc:

```text
application/
└── ports/
    └── fetcher.py

infrastructure/
└── http/
    └── primp_fetcher.py
```

Tùy architecture cuối cùng.

---

# 20. Đừng đưa `primp.Response` vào Domain

Sai:

```python
class Novel:

    def __init__(
        self,
        response: primp.Response,
    ):
        ...
```

Domain không nên biết:

```text
primp
HTTP
headers
timeout
proxy
TLS
```

Domain chỉ biết:

```text
Novel
Chapter
Author
Content
```

---

# 21. Request Options và DDD

Ta có thể nhìn:

```text
                Application
                     │
                     ▼
              Fetcher Port
                     │
              RequestOptions
                     │
                     ▼
             Infrastructure
                     │
                PrimpFetcher
                     │
                     ▼
                   primp
```

`RequestOptions` có thể nằm ở boundary tùy thiết kế.

Nhưng:

```text
Domain
  X
  └── không biết primp
```

Đây là nguyên tắc quan trọng.

---

# 22. Có nên đưa Proxy vào RequestOptions ngay?

Ví dụ:

```python
@dataclass
class RequestOptions:

    timeout: float | None = None
    proxy: str | None = None
```

**Chưa nên.**

Tại sao?

Chúng ta đã có:

```text
14 Proxy
```

và tương lai:

```text
36 Proxy Pool
46 Proxy Strategy
```

Proxy không đơn giản là một option bình thường.

Ví dụ production crawler:

```text
Request
   ↓
Proxy Strategy
   ↓
Proxy Pool
   ↓
selected proxy
   ↓
Fetcher
```

Nếu nhét tất cả vào:

```python
RequestOptions(
    proxy=...,
    user_agent=...,
    impersonate=...,
    verify=...,
    ...
)
```

thì rất nhanh biến thành:

```text
God RequestOptions
```

Không tốt.

---

# 23. Tương tự với Browser Profile

Không nên vội:

```python
RequestOptions(
    impersonate="chrome_146",
)
```

ở bài này.

Sau này chúng ta sẽ có:

```text
Browser Profile
├── User-Agent
├── impersonation
├── headers
├── TLS behavior
└── ...
```

và:

```text
47 Browser Profile Strategy
```

Khi đó architecture rõ ràng hơn.

---

# 24. Request Options nên giữ nhỏ

Ở giai đoạn này:

```python
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

Là đủ.

Đừng biến nó thành:

```python
@dataclass
class RequestOptions:

    timeout: ...
    headers: ...
    params: ...
    cookies: ...
    proxy: ...
    verify: ...
    ca_cert_file: ...
    impersonate: ...
    http2: ...
    user_agent: ...
    retry: ...
    rate_limit: ...
    cache: ...
    logging: ...
```

Đó là dấu hiệu abstraction đang đi quá xa.

---

# 25. Một cải tiến nhỏ: immutable Options

Nếu muốn request configuration không bị thay đổi sau khi tạo:

```python
@dataclass(frozen=True)
class RequestOptions:

    timeout: float | None = None

    headers: dict[str, str] = field(
        default_factory=dict
    )

    params: dict = field(
        default_factory=dict
    )
```

Nhưng chú ý:

```python
frozen=True
```

chỉ ngăn:

```python
options.timeout = 20
```

Nó **không biến dictionary bên trong thành immutable**.

Ví dụ:

```python
options.headers["X-Test"] = "hello"
```

vẫn có thể thay đổi dictionary.

Đây là lý do ở production có thể cần immutable mapping hoặc copy sâu tùy yêu cầu.

**Chưa cần làm vậy ở bài này.**

---

# 26. Request Options và Retry

Hiện tại:

```text
RequestOptions
├── timeout
├── headers
└── params
```

Không có:

```text
retry
```

vì retry thuộc một abstraction khác:

```text
Request
   ↓
Fetcher
   ↓
Exception
   ↓
Retry Policy
```

Roadmap:

```text
19 Request Options
       ↓
20 Client Lifecycle
       ↓
...
35 Timeout + Retry
       ↓
45 Retry Policy
```

Ta giữ đúng roadmap.

---

# 27. Bài tập

### Bài 1

Tạo:

```python
RequestOptions(
    timeout=30
)
```

và gọi:

```text
https://httpbin.org/delay/5
```

---

### Bài 2

Default:

```python
{
    "lang": "vi"
}
```

Request:

```python
{
    "page": 3
}
```

Kiểm tra:

```python
response.url
```

---

### Bài 3

Default header:

```python
{
    "X-Client": "NovelCrawler"
}
```

Request:

```python
{
    "X-Request": "Chapter"
}
```

Kiểm tra:

```text
https://httpbin.org/headers
```

---

### Bài 4 — quan trọng

Kiểm tra override:

```python
default_params = {
    "lang": "vi",
    "page": 1,
}
```

Request:

```python
params = {
    "page": 5,
}
```

Kết quả phải là:

```python
{
    "lang": "vi",
    "page": 5,
}
```

---

# 28. Tổng kết

Sau Buổi 19, `PrimpFetcher` đã có tư duy:

```text
                    PrimpFetcher
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
 Default Config    Request Options    Client
        │                │                │
        ├── headers      ├── headers      │
        ├── params       ├── params       │
        └── timeout      └── timeout      │
                         │                │
                         └──────┬─────────┘
                                ▼
                              primp
```

Nguyên tắc:

```text
Default
    ↓
cấu hình chung

RequestOptions
    ↓
cấu hình riêng request

Client
    ↓
lifecycle + connection reuse

Primp
    ↓
HTTP transport
```

Và quan trọng nhất:

> **Đừng biến `RequestOptions` thành nơi chứa mọi thứ.** Chỉ đưa vào đó những option thực sự thuộc về một HTTP request. Proxy Pool, Browser Profile, Retry Policy... sẽ được thiết kế thành các abstraction riêng ở các buổi sau.

### Roadmap

```text
13 Authentication            ✅
14 Proxy                     ✅
15 SSL / Verify              ✅
16 Session / Connection      ✅
17 Default Headers           ✅
18 Default Params            ✅
19 Request Options           ✅
20 Client Lifecycle          ← tiếp theo
```

**Buổi 20 — Client Lifecycle** sẽ khép lại Phần II: `Client` được tạo ở đâu, sống bao lâu, khi nào đóng, context manager, cleanup, thread/concurrency considerations, và thiết kế lifecycle của `PrimpFetcher` trước khi bước sang **Browser Impersonation**.
