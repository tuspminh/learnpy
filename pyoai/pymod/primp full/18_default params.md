# Buổi 18 — Default Params

Ở Buổi 17 chúng ta học:

```text
Default Headers
```

Hôm nay áp dụng cùng tư duy cho:

```text
Default Query Parameters
```

Mục tiêu là hiểu rõ:

```text
Client
 ├── Default Params
 │
 └── Request Params
```

và đặc biệt quan trọng với **Novel Crawler + pagination**.

> Lưu ý: tài liệu/API công khai của `primp` hiện không cho thấy rõ một Python `Client(..., params=...)` constructor option tương đương `headers`. Vì vậy hôm nay tôi sẽ **không giả định `primp.Client(params=...)` tồn tại**. Ta sẽ xây `DefaultParams` ở `PrimpFetcher`, rồi merge trước khi gọi `client.get()`. Đây là cách an toàn theo API đã học. ([GitHub][1])

---

# 1. Query Params là gì?

Ví dụ:

```text
https://example.com/chapters?page=2&limit=20
```

Phần:

```text
?page=2&limit=20
```

là query string.

Tách ra:

```text
page  = 2
limit = 20
```

Với `primp`:

```python
response = client.get(
    "https://example.com/chapters",
    params={
        "page": 2,
        "limit": 20,
    },
)
```

---

# 2. Vấn đề lặp lại

Giả sử API crawler yêu cầu:

```text
lang=vi
format=html
```

ở mọi request.

Ta có:

```python
client.get(
    url1,
    params={
        "lang": "vi",
        "format": "html",
        "page": 1,
    },
)

client.get(
    url2,
    params={
        "lang": "vi",
        "format": "html",
        "page": 2,
    },
)

client.get(
    url3,
    params={
        "lang": "vi",
        "format": "html",
        "page": 3,
    },
)
```

Rất lặp.

Ta muốn:

```text
Default Params
    ↓
lang=vi
format=html

Request Params
    ↓
page=1
page=2
page=3
```

---

# 3. Default Params khác Default Headers

Headers:

```python
headers={
    "Accept": "text/html",
}
```

Params:

```python
params={
    "lang": "vi",
}
```

Khác nhau về HTTP:

```text
Headers
    ↓
HTTP request metadata

Params
    ↓
URL query string
```

Ví dụ:

```python
client.get(
    "https://example.com/novels",
    headers={
        "Accept": "text/html",
    },
    params={
        "page": 2,
    },
)
```

Kết quả conceptually:

```text
GET /novels?page=2 HTTP/...
Accept: text/html
```

---

# 4. Default Params trong Fetcher

Ta tạo:

```python
class PrimpFetcher:

    def __init__(
        self,
        default_params: dict | None = None,
    ):
        self.default_params = default_params or {}
```

Ví dụ:

```python
fetcher = PrimpFetcher(
    default_params={
        "lang": "vi",
        "format": "html",
    }
)
```

Sau đó:

```python
fetcher.get(
    url,
    params={
        "page": 2,
    },
)
```

Fetcher sẽ tạo:

```text
lang=vi
format=html
page=2
```

---

# 5. Viết hàm merge

Đây là phần quan trọng nhất của bài.

```python
def merge_params(
    default: dict,
    request: dict | None,
) -> dict:

    result = default.copy()

    if request:
        result.update(request)

    return result
```

Ví dụ:

```python
default = {
    "lang": "vi",
    "format": "html",
}

request = {
    "page": 2,
}

result = merge_params(default, request)

print(result)
```

Kết quả:

```python
{
    "lang": "vi",
    "format": "html",
    "page": 2,
}
```

---

# 6. Nếu trùng key?

Ví dụ:

```python
default = {
    "lang": "vi",
}
```

Request:

```python
request = {
    "lang": "en",
}
```

Sau:

```python
result.update(request)
```

ta có:

```python
{
    "lang": "en",
}
```

Tức:

```text
Request Params
       ↓
override
       ↓
Default Params
```

Sơ đồ:

```text
Default
lang=vi
format=html

        +

Request
lang=en
page=2

        ↓

Final
lang=en
format=html
page=2
```

Đây thường là semantics mong muốn: request-specific configuration override default configuration.

---

# 7. Tại sao phải `copy()`?

Không nên:

```python
def merge_params(default, request):

    result = default

    result.update(request)

    return result
```

Vì:

```python
result = default
```

không tạo dictionary mới.

Nó chỉ tạo thêm một reference:

```text
default ─────┐
             ▼
          dictionary
             ▲
             │
result ──────┘
```

Khi:

```python
result.update(...)
```

thì `default` cũng bị thay đổi.

---

## Đúng:

```python
result = default.copy()
```

Sơ đồ:

```text
default
   │
   └── copy()
          ↓
       result
```

Hai dictionary độc lập.

---

# 8. Xây `PrimpFetcher`

Bây giờ kết hợp với kiến thức Buổi 16:

```python
import primp


class PrimpFetcher:

    def __init__(
        self,
        timeout: float = 10,
        default_params: dict | None = None,
    ):
        self.client = primp.Client()

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
        params: dict | None = None,
        timeout: float | None = None,
    ):

        if timeout is None:
            timeout = self.default_timeout

        final_params = self.default_params.copy()

        if params:
            final_params.update(params)

        return self.client.get(
            url,
            params=final_params,
            timeout=timeout,
        )
```

Đây là phiên bản rất phù hợp với giai đoạn hiện tại.

---

# 9. Sử dụng

```python
fetcher = PrimpFetcher(
    default_params={
        "lang": "vi",
        "format": "html",
    }
)
```

Request:

```python
response = fetcher.get(
    "https://httpbin.org/get",
    params={
        "page": 2,
    },
)
```

Conceptually request:

```text
https://httpbin.org/get
    ?lang=vi
    &format=html
    &page=2
```

---

# 10. Test hoàn chỉnh

Tạo:

```text
lesson_18.py
```

```python
import primp


class PrimpFetcher:

    def __init__(
        self,
        timeout: float = 10,
        default_params: dict | None = None,
    ):
        self.client = primp.Client()

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
        params: dict | None = None,
        timeout: float | None = None,
    ):

        if timeout is None:
            timeout = self.default_timeout

        final_params = self.default_params.copy()

        if params:
            final_params.update(params)

        return self.client.get(
            url,
            params=final_params,
            timeout=timeout,
        )


def main():

    fetcher = PrimpFetcher(
        default_params={
            "lang": "vi",
            "format": "html",
        }
    )

    response = fetcher.get(
        "https://httpbin.org/get",
        params={
            "page": 2,
        },
    )

    print("Status:", response.status_code)
    print("URL:", response.url)
    print()
    print(response.text)


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python lesson_18.py
```

Bạn sẽ thấy `httpbin` trả về query arguments.

---

# 11. Default Params rất hữu ích cho pagination

Đây mới là phần liên quan trực tiếp đến Novel Crawler.

Giả sử website có:

```text
https://example.com/novels?page=1
https://example.com/novels?page=2
https://example.com/novels?page=3
```

Parser phát hiện:

```python
next_page = 2
```

Fetcher:

```python
fetcher.get(
    listing_url,
    params={
        "page": next_page,
    },
)
```

Nếu có default:

```python
default_params = {
    "lang": "vi",
}
```

thì:

```text
lang=vi
page=2
```

---

# 12. Nhưng Novel Crawler của chúng ta thường không cần Default Params cho pagination

Đây là một nuance rất quan trọng.

Với crawler website:

```text
/truyen/abc/trang-2
```

thì pagination có thể nằm trong **path**, không phải query:

```text
/trang-2
```

Hoặc:

```text
?page=2
```

Nếu là:

```text
?page=2
```

thì `params=` phù hợp.

Nếu là:

```text
/trang-2
```

thì dùng `yarl` để xây URL.

Nhớ kiến trúc đã học:

```text
Parser
   ↓
phát hiện next URL
   ↓
yarl
   ↓
URL hoàn chỉnh
   ↓
Fetcher
```

Không nên ép mọi pagination thành `params`.

---

# 13. Query Params + `yarl`

Ví dụ URL:

```text
https://example.com/novels?page=2
```

Có thể xây bằng `yarl`:

```python
from yarl import URL


url = URL("https://example.com/novels")

url = url.with_query(
    page=2,
)

print(url)
```

Kết quả:

```text
https://example.com/novels?page=2
```

Sau đó:

```python
fetcher.get(str(url))
```

Trong trường hợp này:

```text
yarl
 ↓
URL construction

primp
 ↓
HTTP transport
```

---

# 14. Hai cách truyền query

## Cách A — `yarl`

```python
url = URL(
    "https://example.com/novels"
).with_query(
    page=2
)

response = client.get(str(url))
```

## Cách B — `primp params`

```python
response = client.get(
    "https://example.com/novels",
    params={
        "page": 2,
    },
)
```

Cả hai đều có thể tạo query string.

Nhưng architecture của crawler chúng ta ưu tiên:

```text
URL manipulation
    ↓
yarl

HTTP transport
    ↓
primp
```

---

# 15. Duplicate Query Parameters

Đây là chỗ `dict` bắt đầu có giới hạn.

Ví dụ muốn:

```text
?tag=action&tag=romance
```

Một dictionary:

```python
{
    "tag": "action"
}
```

không thể biểu diễn hai key giống nhau.

Có thể cần:

```python
[
    ("tag", "action"),
    ("tag", "romance"),
]
```

hoặc cấu trúc mà API `primp`/URL builder của bạn hỗ trợ.

Điểm cần nhớ:

```text
dict
    ↓
mỗi key → một value

duplicate query
    ↓
cần multi-value representation
```

Đây cũng là lý do ta không nên viết một `DefaultParams` abstraction quá cứng ngay từ đầu.

---

# 16. Default Params không nên mutate

Sai:

```python
class PrimpFetcher:

    def get(self, url, params=None):

        if params:
            self.default_params.update(params)

        return self.client.get(
            url,
            params=self.default_params,
        )
```

Giả sử:

```text
Default:
lang=vi
```

Request 1:

```text
page=1
```

Sau request 1:

```text
Default:
lang=vi
page=1
```

Request 2:

```text
page=2
```

Sau request 2:

```text
Default:
lang=vi
page=2
```

Default đã bị biến thành request state.

Đây là bug architecture.

---

# 17. Đúng: mỗi request tạo params mới

```python
final_params = self.default_params.copy()

if params:
    final_params.update(params)
```

Luồng:

```text
Default Params
      │
      ├── Request 1 → copy → page=1
      │
      ├── Request 2 → copy → page=2
      │
      └── Request 3 → copy → page=3
```

Default luôn:

```text
lang=vi
format=html
```

---

# 18. Default Params và `None`

Có một chi tiết nhỏ:

```python
if params:
```

sẽ bỏ qua:

```python
params={}
```

Điều này thường ổn.

Nhưng nếu sau này cần semantics:

```text
None = không override
{}   = override bằng empty
```

thì phải thiết kế khác.

Hiện tại **chưa cần phức tạp hóa**.

---

# 19. Default Params và boolean

Ví dụ:

```python
params={
    "include_content": True,
}
```

Đừng tự nghĩ rằng URL chắc chắn sẽ là:

```text
include_content=True
```

hoặc:

```text
include_content=true
```

Query serialization phụ thuộc HTTP client/serializer.

Nếu API yêu cầu chính xác:

```text
true
```

thì hãy test.

Ví dụ:

```python
response = client.get(
    "https://httpbin.org/get",
    params={
        "include_content": True,
    },
)
```

Sau đó kiểm tra:

```python
print(response.url)
```

Đây là cách học tốt hơn việc đoán serialization.

---

# 20. Default Params và `None`

Ví dụ:

```python
params={
    "page": None,
}
```

Không nên mặc định cho rằng server sẽ nhận:

```text
?page=None
```

Tùy serializer.

Nếu URL chính xác quan trọng, hãy kiểm tra:

```python
print(response.url)
```

---

# 21. Đừng đưa pagination vào Default Params

Ví dụ **sai ý tưởng**:

```python
fetcher = PrimpFetcher(
    default_params={
        "page": 1,
    }
)
```

Sau đó:

```python
fetcher.get(url)
```

Rồi đổi:

```python
fetcher.default_params["page"] = 2
```

Đây là mutable shared state.

Không tốt.

Pagination là **request-specific**:

```python
fetcher.get(
    url,
    params={
        "page": 2,
    },
)
```

---

# 22. Default Params phù hợp với gì?

Ví dụ:

```text
API version
locale
fixed feature flag
fixed response mode
tenant
```

Ví dụ:

```python
default_params = {
    "lang": "vi",
    "api_version": "2",
}
```

Trong khi:

```text
page
chapter
novel_id
search
```

thường là request-specific.

---

# 23. Architecture

Bây giờ Fetcher của chúng ta đã có:

```text
PrimpFetcher
│
├── Client
│
├── Timeout
│
├── Default Headers
│
└── Default Params
```

Request:

```text
                    PrimpFetcher
                         │
            ┌────────────┼────────────┐
            ↓            ↓            ↓
      default headers  timeout   default params
                                      │
                                      +
                               request params
                                      │
                                      ↓
                                  primp
```

---

# 24. Kết hợp Buổi 16 + 17 + 18

Ta có:

```python
import primp


class PrimpFetcher:

    def __init__(
        self,
        timeout: float = 10,
        default_headers: dict[str, str] | None = None,
        default_params: dict | None = None,
    ):
        self.client = primp.Client(
            headers=default_headers or {},
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
        params: dict | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ):

        if timeout is None:
            timeout = self.default_timeout

        final_params = self.default_params.copy()

        if params:
            final_params.update(params)

        return self.client.get(
            url,
            params=final_params,
            headers=headers,
            timeout=timeout,
        )
```

Sử dụng:

```python
fetcher = PrimpFetcher(
    timeout=15,

    default_headers={
        "Accept": "text/html",
        "Accept-Language": "vi-VN",
    },

    default_params={
        "lang": "vi",
    },
)
```

Request:

```python
response = fetcher.get(
    "https://httpbin.org/get",

    params={
        "page": 2,
    },

    headers={
        "X-Crawler": "NovelCrawler",
    },
)
```

Conceptually:

```text
Client Defaults
├── Accept
├── Accept-Language
└── lang=vi

Request
├── X-Crawler
└── page=2
```

---

# 25. Một nguyên tắc kiến trúc rất quan trọng

Ta có ba loại configuration:

```text
Client-level
    ↓
Ổn định trong vòng đời Client

Request-level
    ↓
Chỉ có ý nghĩa với một request

Dynamic state
    ↓
Thay đổi trong quá trình chạy
```

Ví dụ:

```text
Client-level
├── default headers
├── proxy
├── SSL
└── timeout mặc định

Request-level
├── page
├── Referer
├── special headers
└── request timeout override

Dynamic state
├── cookies
├── retry count
└── runtime metrics
```

Đây là cách tư duy sẽ giúp architecture crawler không bị rối.

---

# 26. Bài tập

### Bài 1

Tạo:

```python
fetcher = PrimpFetcher(
    default_params={
        "lang": "vi",
        "format": "html",
    }
)
```

Sau đó:

```python
fetcher.get(
    "https://httpbin.org/get",
    params={
        "page": 3,
    },
)
```

Kiểm tra:

```python
response.url
```

---

### Bài 2

Test override:

```python
default_params = {
    "lang": "vi",
}
```

request:

```python
params = {
    "lang": "en",
}
```

Kiểm tra URL cuối cùng.

---

### Bài 3 — Quan trọng

Chứng minh rằng `default_params` không bị mutate.

```python
fetcher = PrimpFetcher(
    default_params={
        "lang": "vi",
    }
)

fetcher.get(
    url,
    params={
        "page": 2,
    },
)

print(fetcher.default_params)
```

Kết quả mong muốn:

```python
{
    "lang": "vi"
}
```

**Không được xuất hiện:**

```python
{
    "lang": "vi",
    "page": 2,
}
```

---

# 27. Tóm tắt Buổi 18

Nhớ 6 điểm:

```text
1. Query params nằm trong URL.

2. Default Params là params dùng chung cho nhiều request.

3. Request Params nên override Default Params khi trùng key.

4. Không mutate Default Params.

5. Pagination thường là Request Params, không phải Default Params.

6. yarl và primp có trách nhiệm khác nhau:
   yarl  → URL manipulation
   primp → HTTP transport
```

Kiến trúc hiện tại:

```text
                         PrimpFetcher
                              │
                 ┌────────────┼────────────┐
                 │            │            │
                 ▼            ▼            ▼
              Client       Timeout    Default Params
                 │                         │
                 │                    + Request Params
                 │                         │
                 └────────────┬────────────┘
                              ▼
                            primp
                              │
                              ▼
                           Internet
```

Roadmap:

```text
16. Session / Connection Reuse  ✅
17. Default Headers             ✅
18. Default Params              ← hôm nay
19. Request Options
20. Client Lifecycle
```

**Buổi 19 — Request Options** sẽ gom những thứ mà *chỉ một request* cần thay đổi: timeout riêng, headers riêng, params riêng, redirect, proxy/SSL/impersonation tùy request và cách thiết kế một `RequestOptions` sạch cho `PrimpFetcher` mà không biến nó thành một "God object".

[1]: https://github.com/ChirikjianLab/primp-python/pulls?utm_source=chatgpt.com "Pull requests · ChirikjianLab/primp-python · GitHub"
