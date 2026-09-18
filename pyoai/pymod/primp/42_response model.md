# Phần V — Novel Crawler

# Buổi 42 — Response Model

Ở Buổi 41, chúng ta xây:

```text
FetchRequest
     ↓
Fetcher
```

Hôm nay xây nửa còn lại:

```text
Fetcher
     ↓
FetchResponse
```

Mục tiêu là **Application không phụ thuộc `primp.Response`**.

---

# 1. Vấn đề

Nếu Application nhận trực tiếp:

```python
response = await primp_client.get(url)
```

thì Application sẽ biết `primp`.

Điều đó tạo coupling:

```text
Application
     ↓
primp.Response
     ↓
primp
```

Không tốt.

Ta muốn:

```text
Application
     ↓
FetchResponse
```

Còn Infrastructure chịu trách nhiệm:

```text
primp.Response
     ↓
adapter
     ↓
FetchResponse
```

---

# 2. Kiến trúc

```text
                    Infrastructure
                         │
                  primp.Response
                         │
                         ↓
                  adapt_response()
                         │
                         ↓
                  FetchResponse
                         │
                         ↓
                    Application
                         │
                         ↓
                    ChapterParser
```

Đây là **Anti-Corruption Layer / Adapter** ở boundary.

---

# 3. Response Model cơ bản

Ta bắt đầu:

```python id="gtdp8s"
from dataclasses import dataclass


@dataclass(frozen=True)
class FetchResponse:

    status_code: int
    url: str
    headers: dict[str, str]
    content: bytes
```

Ví dụ:

```python id="y5v7uh"
response = FetchResponse(
    status_code=200,
    url="https://example.com/chapter-1",
    headers={
        "content-type": "text/html",
    },
    content=b"<html>Hello</html>",
)
```

---

# 4. Tại sao `content` là `bytes`?

HTTP response thực chất là byte stream.

Ví dụ:

```text id="zlw42a"
HTTP
 ↓
bytes
 ↓
decode
 ↓
text
```

Nếu ta lưu trực tiếp:

```python id="l8ffh2"
text: str
```

thì đã mất raw bytes.

Với crawler, raw bytes đôi khi rất hữu ích:

* debug encoding
* lưu response
* hash content
* kiểm tra binary
* xử lý encoding đặc biệt

Do đó:

```python id="0i9vdb"
content: bytes
```

là lựa chọn tốt.

---

# 5. Property `text`

Ta thêm:

```python id="5rj1dq"
@dataclass(frozen=True)
class FetchResponse:

    status_code: int
    url: str
    headers: dict[str, str]
    content: bytes

    @property
    def text(self) -> str:

        return self.content.decode(
            "utf-8",
            errors="replace",
        )
```

Sử dụng:

```python id="z9n5j0"
print(response.text)
```

---

# 6. Nhưng UTF-8 có luôn đúng không?

Không.

Website có thể khai báo:

```html
<meta charset="utf-8">
```

hoặc:

```http
Content-Type: text/html; charset=utf-8
```

hoặc encoding khác.

Vì vậy:

```python id="vy2t8d"
content.decode("utf-8")
```

là **fallback đơn giản**, chưa phải encoding detector hoàn chỉnh.

Ở tầng Fetcher, ta chưa cần biến Response Model thành một hệ thống encoding phức tạp.

Parser có thể xử lý HTML encoding nếu cần.

---

# 7. HTTP status helpers

Response Model nên cung cấp các thông tin tiện dụng.

```python id="6xuh8x"
@property
def is_success(self) -> bool:
    return 200 <= self.status_code < 300
```

Ví dụ:

```python id="7bj9jp"
if response.is_success:
    print("OK")
```

---

# 8. Redirect

```python id="oj5t8t"
@property
def is_redirect(self) -> bool:
    return 300 <= self.status_code < 400
```

---

# 9. Client Error

```python id="f9pp7v"
@property
def is_client_error(self) -> bool:
    return 400 <= self.status_code < 500
```

Ví dụ:

```text id="5hx7d6"
400
401
403
404
429
```

---

# 10. Server Error

```python id="yqf2tc"
@property
def is_server_error(self) -> bool:
    return 500 <= self.status_code < 600
```

Ví dụ:

```text id="7ps4p8"
500
502
503
504
```

---

# 11. Full Response Model

Ta có:

```python id="6uln8a"
from dataclasses import dataclass


@dataclass(frozen=True)
class FetchResponse:

    status_code: int

    url: str

    headers: dict[str, str]

    content: bytes

    @property
    def text(self) -> str:

        return self.content.decode(
            "utf-8",
            errors="replace",
        )

    @property
    def is_success(self) -> bool:

        return 200 <= self.status_code < 300

    @property
    def is_redirect(self) -> bool:

        return 300 <= self.status_code < 400

    @property
    def is_client_error(self) -> bool:

        return 400 <= self.status_code < 500

    @property
    def is_server_error(self) -> bool:

        return 500 <= self.status_code < 600
```

Đây là phiên bản đủ tốt cho giai đoạn hiện tại.

---

# 12. Test Response Model

```python id="n6d7p4"
response = FetchResponse(
    status_code=200,
    url="https://example.com",
    headers={
        "content-type": "text/html",
    },
    content=b"<h1>Hello</h1>",
)

print(response.status_code)
print(response.url)
print(response.text)
print(response.is_success)
```

Kết quả:

```text id="5h89z2"
200
https://example.com
<h1>Hello</h1>
True
```

---

# 13. Test từng nhóm status

```python id="4ylk4m"
def test_status_helpers():

    assert FetchResponse(
        200,
        "https://example.com",
        {},
        b"",
    ).is_success

    assert FetchResponse(
        301,
        "https://example.com",
        {},
        b"",
    ).is_redirect

    assert FetchResponse(
        404,
        "https://example.com",
        {},
        b"",
    ).is_client_error

    assert FetchResponse(
        500,
        "https://example.com",
        {},
        b"",
    ).is_server_error
```

---

# 14. `headers` nên là gì?

Ta dùng:

```python id="ohp9mm"
dict[str, str]
```

Ví dụ:

```python id="u7n2qz"
{
    "content-type": "text/html",
    "content-length": "12345",
}
```

Application chỉ cần đọc:

```python id="7kqvuw"
content_type = response.headers.get(
    "content-type"
)
```

Nó không cần biết header object của primp.

---

# 15. Adapter từ primp

Trong Infrastructure:

```python id="z82x3x"
def adapt_response(
    response,
) -> FetchResponse:

    return FetchResponse(
        status_code=response.status_code,
        url=response.url,
        headers=dict(response.headers),
        content=response.content,
    )
```

Flow:

```text id="o9j5yz"
primp.Response
       │
       │ adapter
       ↓
FetchResponse
```

---

# 16. Tại sao không viết `FetchResponse(primp_response)`?

Ví dụ:

```python id="2p1w92"
class FetchResponse:

    def __init__(self, primp_response):
        ...
```

Không nên.

Khi đó Application Model lại biết:

```text id="3r9z1p"
primp_response
```

và abstraction bị leak.

Adapter tốt hơn:

```text id="51j7po"
Infrastructure
     │
     ├── primp
     │
     └── adapter
            ↓
       FetchResponse
```

---

# 17. Response Model không biết Retry

Không thêm:

```python id="7t5jzq"
response.should_retry
```

hoặc:

```python id="6t6j52"
response.retry()
```

Vì retry là policy.

Ta đã có:

```text id="jgyhpn"
RetryPolicy
RetryExecutor
```

Response chỉ cung cấp **facts**:

```text id="plh3ig"
status_code = 503
```

Policy quyết định:

```text id="1s6p75"
503 → retry?
```

Đây là separation rất quan trọng.

---

# 18. Response Model không biết Parser

Không:

```python id="8kj6ga"
response.parse_chapter()
```

Response chỉ:

```text id="qj9ecm"
HTTP data
```

Parser:

```text id="i3u0h3"
FetchResponse.text
      ↓
ChapterParser
      ↓
Chapter
```

---

# 19. Response Model không biết SQLite

Không:

```python id="t18w7f"
response.save()
```

Persistence là responsibility khác:

```text id="0av5zr"
Response
   ↓
Parser
   ↓
Domain Entity
   ↓
Repository
```

---

# 20. Response Model và `Content-Type`

Ta có thể thêm helper:

```python id="m1h8pq"
@property
def content_type(self) -> str | None:

    return self.headers.get(
        "content-type"
    )
```

Ví dụ:

```python id="6h18f3"
if response.content_type:
    print(response.content_type)
```

Nhưng tôi khuyên **chưa cần quá nhiều helper**.

---

# 21. Response Model nên đại diện cho cái gì?

Một câu rất quan trọng:

> `FetchResponse` đại diện cho kết quả của một HTTP fetch, không phải kết quả nghiệp vụ.

Ví dụ:

```text id="2oqp7m"
FetchResponse
    status = 200
    url = ...
    content = HTML
```

Không phải:

```text id="5szs7r"
FetchResponse
    chapter_title
    chapter_number
    novel_id
```

Các field đó thuộc:

```text id="p4j0ob"
Chapter
Novel
```

---

# 22. Response Model trong Novel Crawler

Giả sử website trả:

```html
<html>
    <h1>Chương 123</h1>
    ...
</html>
```

Fetcher trả:

```python id="qvgb6k"
FetchResponse(
    status_code=200,
    url=chapter_url,
    headers=...,
    content=...
)
```

Sau đó:

```python id="hkjf2x"
chapter = parser.parse(
    response.text
)
```

Kết quả:

```text id="4b0c79"
Chapter(
    number=123,
    title="Chương 123",
    content="..."
)
```

---

# 23. Đây là boundary cực đẹp

```text id="0k22jp"
HTTP world
───────────────
primp.Response
      ↓
adapter
      ↓
FetchResponse
───────────────
Application world
      ↓
ChapterParser
      ↓
Chapter
───────────────
Domain world
```

Mỗi tầng có model riêng.

---

# 24. Có cần `raise_for_status()` không?

Một số HTTP client có:

```python id="q2q6ce"
response.raise_for_status()
```

Nhưng tôi **không đưa method này vào Response Model** ở giai đoạn này.

Tại sao?

Vì:

```text id="l6k2or"
404
```

có thể là một kết quả bình thường đối với crawler.

Ví dụ chapter bị xóa:

```text
404
```

Application có thể muốn:

```text
mark chapter unavailable
```

chứ không nhất thiết muốn exception ngay.

Ở Buổi 48, chúng ta sẽ phân loại Error cụ thể.

---

# 25. `is_success` cũng không đồng nghĩa với "crawl thành công"

Ví dụ:

```http
200 OK
```

nhưng HTML:

```html
<html>
    <body>
        <div>Cloudflare challenge...</div>
    </body>
</html>
```

HTTP thành công:

```python id="jpp6st"
response.is_success == True
```

nhưng crawler nghiệp vụ thất bại.

Đây là hai tầng khác nhau:

```text id="34cyrf"
HTTP success
      ≠
Crawler success
```

Điểm này cực kỳ quan trọng khi xây crawler.

---

# 26. Ví dụ

```python id="hyn4ql"
response = FetchResponse(
    status_code=200,
    url="https://example.com/chapter",
    headers={},
    content=b"<html>Access denied</html>",
)
```

Ta có:

```python id="d7g0p5"
response.is_success
```

→ `True`

nhưng:

```text id="p4o0fb"
ChapterParser
      ↓
không tìm thấy chapter content
      ↓
ParseError
```

Đây sẽ là một loại lỗi khác với:

```text id="x1j0u5"
HTTP 503
```

Buổi 48 sẽ phân loại những lỗi này.

---

# 27. Response Model và final URL

Field:

```python id="6c0g4d"
url: str
```

không nhất thiết là URL ban đầu.

Ví dụ:

```text id="5owhpn"
Request URL
https://example.com/chapter

        ↓ 302

Final URL
https://example.com/login
```

Fetcher nên trả URL cuối cùng nếu HTTP client cung cấp nó.

Do đó:

```python id="3ck8jn"
response.url
```

rất hữu ích để debug redirect.

---

# 28. Full code của `response.py`

Tạo:

```text id="3j7u6a"
src/
└── crawler/
    └── application/
        └── ports/
            └── response.py
```

Nội dung:

```python id="l5d7vq"
from dataclasses import dataclass


@dataclass(frozen=True)
class FetchResponse:

    status_code: int

    url: str

    headers: dict[str, str]

    content: bytes

    @property
    def text(self) -> str:

        return self.content.decode(
            "utf-8",
            errors="replace",
        )

    @property
    def is_success(self) -> bool:

        return 200 <= self.status_code < 300

    @property
    def is_redirect(self) -> bool:

        return 300 <= self.status_code < 400

    @property
    def is_client_error(self) -> bool:

        return 400 <= self.status_code < 500

    @property
    def is_server_error(self) -> bool:

        return 500 <= self.status_code < 600
```

---

# 29. Adapter

Tạo:

```text id="4t4jbm"
src/
└── crawler/
    └── infrastructure/
        └── http/
            └── response_adapter.py
```

```python id="2u3r3x"
from crawler.application.ports.response import (
    FetchResponse,
)


def adapt_response(
    response,
) -> FetchResponse:

    return FetchResponse(
        status_code=response.status_code,
        url=response.url,
        headers=dict(response.headers),
        content=response.content,
    )
```

---

# 30. Ghép với `PrimpTransport`

Buổi 39 chúng ta có:

```python id="3o5y85"
class PrimpTransport:

    def __init__(self, client):
        self.client = client

    async def send(
        self,
        request,
    ):

        return await self.client.get(
            request.url,
            headers=request.headers,
            params=request.params,
            timeout=request.timeout,
        )
```

Bây giờ có thể hoàn thiện boundary:

```python id="ap8p3b"
class PrimpTransport:

    def __init__(self, client):
        self.client = client

    async def send(
        self,
        request,
    ) -> FetchResponse:

        raw_response = await self.client.get(
            request.url,
            headers=request.headers,
            params=request.params,
            timeout=request.timeout,
        )

        return adapt_response(
            raw_response
        )
```

Kể từ đây:

```text id="3u8v45"
PrimpTransport
```

không leak:

```text id="8x5r1c"
primp.Response
```

ra ngoài.

---

# 31. Flow hoàn chỉnh

```text id="qklw0f"
FetchRequest
    │
    │
    ↓
PrimpTransport
    │
    ↓
primp.AsyncClient
    │
    ↓
primp.Response
    │
    ↓
adapt_response()
    │
    ↓
FetchResponse
    │
    ↓
Application
```

Đây là boundary mà chúng ta muốn.

---

# 32. Test Adapter

Không cần Internet.

Tạo fake primp response:

```python id="f9s1go"
class FakePrimpResponse:

    status_code = 200

    url = "https://example.com"

    headers = {
        "content-type": "text/html",
    }

    content = b"<h1>Hello</h1>"
```

Test:

```python id="sp0y3v"
def test_adapter():

    response = adapt_response(
        FakePrimpResponse()
    )

    assert isinstance(
        response,
        FetchResponse,
    )

    assert response.status_code == 200

    assert response.url == (
        "https://example.com"
    )

    assert response.text == (
        "<h1>Hello</h1>"
    )
```

---

# 33. Test không phụ thuộc primp

Một test quan trọng:

```python id="xg25sy"
def test_response_model():

    response = FetchResponse(
        status_code=404,
        url="https://example.com/missing",
        headers={},
        content=b"not found",
    )

    assert response.is_client_error
    assert not response.is_success
```

Test này hoàn toàn không import:

```python id="8p7r2x"
import primp
```

Đó chính là mục tiêu.

---

# 34. Request + Response

Sau Buổi 41 và 42:

```text id="x4yqpy"
             Application
                  │
        ┌─────────┴─────────┐
        ↓                   ↓
 FetchRequest         FetchResponse
        │                   ↑
        └────→ Fetcher ─────┘
                  │
                  ↓
             Infrastructure
                  │
                  ↓
                primp
```

Chúng ta đã có **hai model độc lập với HTTP library**.

---

# 35. So sánh với cách làm sai

### ❌ Sai

```python id="iq1bca"
async def crawl(url):

    response = await primp.get(url)

    if response.status_code == 200:
        ...
```

Application biết:

```text
primp
```

---

### ✅ Đúng

```python id="8p4nqg"
async def crawl(url):

    request = FetchRequest(
        url=url
    )

    response = await fetcher.get(
        request
    )

    if response.is_success:
        ...
```

Application chỉ biết:

```text
FetchRequest
FetchResponse
Fetcher
```

---

# 36. Một lưu ý về `content` và `text`

Không nên lưu cả:

```python id="4m0bqj"
content: bytes
text: str
```

ngay từ đầu nếu chưa cần.

Vì:

```text id="0zj4si"
bytes
+
text
```

có thể nhân đôi bộ nhớ.

Với crawler hàng nghìn chapter, điều này đáng lưu ý.

Ta chọn:

```python id="cnm3jf"
content: bytes
```

và:

```python id="k5x6ei"
@property
def text(...)
```

để decode khi cần.

---

# 37. Một Response có thể rất lớn

Ví dụ chapter:

```text id="h4a8cs"
5 KB
20 KB
100 KB
500 KB
```

Nếu crawler chạy:

```text id="y54qws"
100 concurrent requests
```

thì response đang nằm trong memory đồng thời.

Do đó:

```text id="75zj65"
Semaphore
```

không chỉ chống overload server.

Nó cũng giúp kiểm soát:

```text memory
connections
CPU
```

Đây là lý do kiến trúc Buổi 34 vẫn rất quan trọng.

---

# 38. Response Model không chứa timestamp

Có thể bạn sẽ nghĩ:

```python id="wns7ur"
fetched_at: datetime
```

Có cần không?

Hiện tại tôi **không thêm**.

Timestamp là observability metadata và sẽ phù hợp hơn khi chúng ta làm:

```text
Buổi 49 — Observability / Logging
```

Ở đó ta sẽ có:

```text id="4f0qgz"
request_id
task_id
started_at
duration
status
proxy
profile
attempt
```

---

# 39. Response Model không chứa retry count

Không:

```python id="nhm7w2"
retry_count: int
```

vì retry là execution metadata.

Một Response:

```text id="q8qjqa"
HTTP 200
```

không cần biết nó đến từ:

```text id="0ym1hm"
attempt 1
```

hay:

```text id="r5d0f3"
attempt 3
```

Thông tin đó thuộc execution/observability layer.

---

# 40. Response Model cuối cùng của Buổi 42

Ta giữ nó **nhỏ**:

```python id="z5fbr5"
@dataclass(frozen=True)
class FetchResponse:

    status_code: int
    url: str
    headers: dict[str, str]
    content: bytes

    @property
    def text(self) -> str:
        return self.content.decode(
            "utf-8",
            errors="replace",
        )

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300

    @property
    def is_redirect(self) -> bool:
        return 300 <= self.status_code < 400

    @property
    def is_client_error(self) -> bool:
        return 400 <= self.status_code < 500

    @property
    def is_server_error(self) -> bool:
        return 500 <= self.status_code < 600
```

---

# 41. Kiến trúc sau Buổi 42

```text id="p4u9cx"
                  APPLICATION
                       │
              ┌────────┴────────┐
              ↓                 ↓
        FetchRequest       FetchResponse
              │                 ↑
              └───────┬─────────┘
                      ↓
                   Fetcher
                      │
                      ↓
                INFRASTRUCTURE
                      │
                ┌─────┴─────┐
                ↓           ↓
          PrimpTransport   Retry
                │
                ↓
        primp.AsyncClient
```

Điểm mấu chốt:

> **`primp` là implementation detail. `FetchRequest` và `FetchResponse` mới là contract mà Application sử dụng.**

---

## Kết quả Phần V đến hiện tại

```text
41. Request Model      ✅
       │
       ↓
42. Response Model     ✅
       │
       ↓
43. Fetcher Interface
       │
       ↓
44. PrimpFetcher
       │
       ↓
45. Retry Policy
       │
       ↓
46. Proxy Strategy
       │
       ↓
47. Browser Profile Strategy
       │
       ↓
48. Error Classification
       │
       ↓
49. Observability / Logging
       │
       ↓
50. Production Fetcher
```

**Buổi 43** sẽ rất quan trọng: chúng ta chính thức định nghĩa **`Fetcher` Port/Interface** bằng `Protocol`, rồi kiểm tra `PrimpFetcher`, `FakeFetcher` và `HttpxFetcher` có thể thay thế nhau mà Application không cần biết implementation nào đang chạy.
