# Buổi 7 — Headers trong HTTPX

Hôm nay chúng ta học **HTTP Headers** thật kỹ.

Headers xuất hiện trong hầu hết HTTP request:

```text
Client
   │
   │  Headers
   │  ├── User-Agent
   │  ├── Accept
   │  ├── Authorization
   │  ├── Content-Type
   │  └── ...
   │
   ▼
Server
```

Nếu bạn muốn làm **API Client, crawler, scraper**, phần này cực kỳ quan trọng.

---

# 1. Header là gì?

Một HTTP request có thể trông như:

```http
GET /users HTTP/1.1
Host: example.com
User-Agent: MyClient/1.0
Accept: application/json
Authorization: Bearer abc123
```

Các dòng:

```text
Host: example.com
User-Agent: MyClient/1.0
Accept: application/json
Authorization: Bearer abc123
```

là **HTTP headers**.

Trong HTTPX:

```python
import httpx

response = httpx.get(
    "https://example.com",
    headers={
        "User-Agent": "MyClient/1.0",
        "Accept": "application/json",
    },
)
```

---

# 2. Headers là metadata

Đừng nhầm:

```text
Headers
```

với:

```text
Body
```

Ví dụ:

```http
POST /users HTTP/1.1

Content-Type: application/json

{
    "name": "Alice"
}
```

Ta có:

```text
Headers
    ↓
Content-Type: application/json

Body
    ↓
{"name": "Alice"}
```

Headers mô tả request/response.

Body chứa dữ liệu thực tế.

---

# 3. Xem request headers

Đây là kỹ thuật debug rất quan trọng.

```python
import httpx

response = httpx.get(
    "https://example.com",
    headers={
        "User-Agent": "MyClient/1.0",
    },
)

print(response.request.headers)
```

Bạn sẽ thấy các headers HTTPX thực sự sử dụng.

---

# 4. `httpx.Headers`

HTTPX có class:

```python
httpx.Headers
```

Bạn có thể tạo:

```python
headers = httpx.Headers({
    "User-Agent": "MyClient/1.0",
    "Accept": "application/json",
})
```

Sau đó:

```python
response = httpx.get(
    url,
    headers=headers,
)
```

Trong code đơn giản, dictionary thường đủ:

```python
headers = {
    "User-Agent": "MyClient/1.0"
}
```

Nhưng `httpx.Headers` hữu ích khi bạn cần thao tác headers chuyên sâu.

---

# 5. Header phổ biến nhất: `User-Agent`

`User-Agent` cho server biết client đang sử dụng gì.

Ví dụ:

```python
headers = {
    "User-Agent": "MyCrawler/1.0",
}
```

Request:

```python
response = httpx.get(
    url,
    headers=headers,
)
```

Trong crawler, **nên có User-Agent rõ ràng** thay vì để client trông như một request vô danh.

Ví dụ:

```python
USER_AGENT = (
    "MyStoryCrawler/1.0 "
    "(contact: admin@example.com)"
)
```

---

# 6. User-Agent không phải "lá chắn"

Một hiểu lầm phổ biến:

> "Đổi User-Agent là có thể vượt mọi anti-bot."

Không.

User-Agent chỉ là **một header**.

Server có thể kiểm tra thêm:

```text
IP
TLS fingerprint
Cookies
Rate
Headers
Behavior
JavaScript
Authentication
...
```

Do đó:

```python
headers={
    "User-Agent": "Mozilla/5.0 ..."
}
```

không biến HTTPX thành browser.

Điểm này rất quan trọng khi bạn làm crawler.

---

# 7. `Accept`

`Accept` nói với server:

> Client muốn nhận loại dữ liệu nào.

Ví dụ API JSON:

```python
headers = {
    "Accept": "application/json",
}
```

Server có thể trả:

```http
Content-Type: application/json
```

---

# 8. `Accept` không giống `Content-Type`

Đây là một điểm **rất quan trọng**.

### `Accept`

Client nói:

```text
"Tôi muốn nhận JSON."
```

```http
Accept: application/json
```

### `Content-Type`

Nói:

```text
"Body tôi gửi lên là JSON."
```

```http
Content-Type: application/json
```

Tư duy:

```text
Accept
Client ───────────────→ Server
       "Tôi muốn nhận gì?"

Content-Type
Client ───────────────→ Server
       "Tôi đang gửi gì?"
```

---

# 9. Ví dụ

```python
response = httpx.post(
    url,
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json",
    },
    content='{"name": "Alice"}',
)
```

Tuy nhiên, khi dùng:

```python
json={}
```

HTTPX sẽ giúp bạn xử lý `Content-Type` phù hợp.

Ví dụ:

```python
response = httpx.post(
    url,
    json={
        "name": "Alice",
    },
)
```

Phần JSON request chúng ta sẽ học kỹ ở **Buổi 10**.

---

# 10. `Authorization`

Một header cực kỳ quan trọng:

```http
Authorization: Bearer abc123
```

HTTPX:

```python
headers = {
    "Authorization": "Bearer abc123",
}

response = client.get(
    "/users",
    headers=headers,
)
```

Đây là pattern phổ biến của REST API.

---

# 11. API Key

Một số API dùng:

```http
X-API-Key: abc123
```

HTTPX:

```python
headers = {
    "X-API-Key": "abc123",
}
```

Hoặc API có thể yêu cầu:

```http
Authorization: Api-Key abc123
```

Điều quan trọng:

> Format authentication phụ thuộc vào API.

Không phải API nào cũng dùng Bearer.

---

# 12. `Referer`

Một header bạn sẽ gặp nhiều khi làm web:

```http
Referer: https://example.com/
```

HTTPX:

```python
headers = {
    "Referer": "https://example.com/",
}
```

Nó cho server biết request hiện tại được điều hướng từ URL nào.

---

# 13. `Accept-Language`

Ví dụ:

```python
headers = {
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
}
```

Server có thể sử dụng thông tin này để chọn ngôn ngữ phù hợp.

Ví dụ:

```text
vi-VN
vi
en
```

---

# 14. `Accept-Encoding`

HTTP client thường hỗ trợ compressed responses.

Ví dụ:

```http
Accept-Encoding: gzip, deflate
```

HTTPX xử lý nhiều chi tiết HTTP encoding cho bạn, vì vậy **không nên tùy tiện tự xây header này** nếu bạn không có lý do rõ ràng.

Nguyên tắc:

> Để HTTPX quản lý những header thuộc về transport/protocol khi có thể.

---

# 15. Client-level Headers

Đây là phần nối trực tiếp với Buổi 4.

Bạn có thể:

```python
client = httpx.Client(
    headers={
        "User-Agent": "MyCrawler/1.0",
        "Accept": "application/json",
    }
)
```

Sau đó:

```python
client.get("/users")
client.get("/posts")
client.get("/articles")
```

Các request sử dụng headers mặc định của Client.

---

# 16. Request-level Headers

Bạn cũng có thể override/thêm header cho một request:

```python
client = httpx.Client(
    headers={
        "User-Agent": "MyCrawler/1.0",
    }
)

response = client.get(
    "/users",
    headers={
        "Accept": "application/json",
    },
)
```

Tư duy:

```text
Client headers
      │
      ▼
Request headers
      │
      ▼
Final request
```

---

# 17. Header inheritance

Đây là concept cần nhớ.

Ví dụ:

```python
client = httpx.Client(
    headers={
        "User-Agent": "MyCrawler/1.0",
        "Accept": "application/json",
    }
)
```

Request:

```python
client.get(
    "/users",
    headers={
        "X-Request-ID": "123",
    },
)
```

Request cuối cùng có thể có:

```text
User-Agent: MyCrawler/1.0
Accept: application/json
X-Request-ID: 123
```

Tức là request-level headers không có nghĩa:

> "Xóa toàn bộ headers của Client."

Chúng được **merge** theo cơ chế của HTTPX.

---

# 18. Override header

Nếu Client có:

```python
headers={
    "Accept": "application/json",
}
```

và request:

```python
headers={
    "Accept": "text/html",
}
```

thì request-specific value có thể override giá trị mặc định tương ứng.

Tư duy:

```text
Client:
Accept = application/json

Request:
Accept = text/html

          ↓

Final:
Accept = text/html
```

---

# 19. Xóa một default header

Trong API client thực tế đôi khi bạn cần:

```text
Client có header mặc định
nhưng request đặc biệt không muốn dùng nó.
```

Đây là lúc cần hiểu sâu hơn về cơ chế merge của HTTPX thay vì đơn giản coi headers là dictionary độc lập.

Một cách tiếp cận tốt là:

> Chỉ đưa vào Client những headers thực sự mang tính global.

Ví dụ:

```python
client = httpx.Client(
    headers={
        "User-Agent": "MyCrawler/1.0",
    }
)
```

Còn:

```text
Authorization
Content-Type
Accept
```

có thể thay đổi theo từng API/request.

---

# 20. Header case-insensitive

HTTP header names **không phân biệt hoa thường**.

Các cách sau về mặt HTTP đều tương đương:

```text
Content-Type
content-type
CONTENT-TYPE
```

Trong HTTPX:

```python
response.request.headers["content-type"]
```

và:

```python
response.request.headers["Content-Type"]
```

có thể truy cập cùng header.

Điều này khác với một số dictionary thông thường của Python.

---

# 21. Duplicate Headers

HTTP cho phép một số header xuất hiện nhiều lần hoặc có nhiều giá trị.

Đây là lý do `httpx.Headers` không đơn giản chỉ là:

```python
dict[str, str]
```

Ví dụ concept:

```text
Accept: application/json
Accept: text/plain
```

hoặc:

```text
Accept: application/json, text/plain
```

HTTPX có cơ chế xử lý header values phù hợp với HTTP.

---

# 22. Header value không phải lúc nào cũng đơn giản

Ví dụ:

```python
headers = {
    "Accept": "application/json, text/plain",
}
```

Đây là **một header có nhiều media type**.

Đừng nhầm:

```python
["application/json", "text/plain"]
```

với format HTTP header mà server mong đợi.

Bạn phải theo specification/API documentation.

---

# 23. Default Headers của HTTPX

Khi bạn tạo:

```python
client = httpx.Client()
```

HTTPX có thể tự quản lý/thêm một số headers cần thiết.

Do đó:

```python
headers = {
    "User-Agent": "MyCrawler/1.0",
}
```

không có nghĩa request cuối cùng **chỉ có đúng một header**.

HTTPX và transport layer còn có thể thêm các thông tin cần thiết cho HTTP request.

Đây là lý do nên debug:

```python
response.request.headers
```

thay vì đoán.

---

# 24. Debug Headers — Kỹ năng quan trọng

Hãy tập thói quen:

```python
import httpx

response = httpx.get(
    "https://example.com",
    headers={
        "User-Agent": "MyCrawler/1.0",
        "Accept": "text/html",
    },
)

print("URL:")
print(response.request.url)

print("\nHeaders:")
print(response.request.headers)
```

Ta đang kiểm tra:

```text
Request
├── URL
├── Method
├── Headers
└── Body
```

Đây là cách debug HTTP client rất tốt.

---

# 25. Request object

HTTPX cho phép truy cập request:

```python
request = response.request
```

Sau đó:

```python
print(request.method)
print(request.url)
print(request.headers)
```

Ví dụ:

```python
print(response.request.method)
# GET

print(response.request.url)
# https://example.com/...

print(response.request.headers)
```

---

# 26. Headers của Response

Không chỉ Request mới có headers.

Response cũng có:

```python
response.headers
```

Ví dụ:

```python
response = httpx.get(
    "https://example.com"
)

print(response.headers)
```

Ta có:

```text
Request Headers
       ↓
     Server
       ↓
Response Headers
```

---

# 27. Một số Response Headers quan trọng

Ví dụ:

```text
Content-Type
Content-Length
Cache-Control
Set-Cookie
Location
ETag
Last-Modified
```

Trong các buổi sau:

```text
Set-Cookie
    ↓
Buổi 8 — Cookies

Content-Type
    ↓
Buổi 9/10 — Form / JSON

Location
    ↓
Buổi 14 — Redirect
```

Bạn sẽ thấy các phần HTTPX liên kết với nhau.

---

# 28. `Content-Type`

Ví dụ server trả:

```http
Content-Type: application/json
```

Bạn có thể:

```python
content_type = response.headers.get(
    "content-type"
)

print(content_type)
```

Hoặc:

```python
print(response.headers["content-type"])
```

Nhưng `.get()` an toàn hơn nếu header có thể không tồn tại.

---

# 29. `Content-Length`

```python
length = response.headers.get(
    "content-length"
)

print(length)
```

Header này có thể cho biết kích thước body theo byte nếu server cung cấp.

Không phải response nào cũng có `Content-Length`.

Đặc biệt streaming/chunked responses có thể hoạt động khác.

---

# 30. `Set-Cookie`

Server có thể trả:

```http
Set-Cookie: session=abc123
```

Bạn có thể nhìn thấy:

```python
print(response.headers)
```

Nhưng khi làm việc với cookies, **đừng tự parse cookie bằng tay nếu không cần**.

Hãy để:

```python
httpx.Client
```

quản lý cookie jar.

Chúng ta sẽ học ở **Buổi 8**.

---

# 31. Header factory

Khi xây crawler, đừng rải headers khắp code:

```python
client.get(
    url,
    headers={
        "User-Agent": "...",
    }
)
```

ở 20 nơi.

Tạo cấu hình:

```python
DEFAULT_HEADERS = {
    "User-Agent": "MyCrawler/1.0",
    "Accept": "text/html",
}
```

Sau đó:

```python
client = httpx.Client(
    headers=DEFAULT_HEADERS
)
```

---

# 32. API Client

Ví dụ:

```python
class GitHubLikeClient:

    def __init__(self, token: str):

        self.client = httpx.Client(
            base_url="https://api.example.com",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "MyAPIClient/1.0",
            },
        )

    def get_user(self, username: str):

        response = self.client.get(
            f"/users/{username}"
        )

        response.raise_for_status()

        return response.json()

    def close(self):
        self.client.close()
```

Đây chính là hướng chúng ta sẽ phát triển dần thành một **production HTTP client**.

---

# 33. Không hard-code secret

Sai:

```python
headers = {
    "Authorization": "Bearer abc123secret",
}
```

Trong source code.

Nên:

```python
token = get_token_somehow()

headers = {
    "Authorization": f"Bearer {token}",
}
```

Trong production:

```text
Environment
    ↓
Configuration
    ↓
API Client
    ↓
Authorization header
```

Không commit API key/token vào Git.

---

# 34. Một lỗi rất phổ biến

Bạn có:

```python
client = httpx.Client(
    headers={
        "Authorization": "Bearer OLD_TOKEN",
    }
)
```

Sau đó token thay đổi:

```python
token = "NEW_TOKEN"
```

nhưng Client vẫn giữ:

```text
OLD_TOKEN
```

Vì vậy authentication state cần được thiết kế rõ ràng.

Đây là một trong những lý do Buổi 15 sẽ học Authentication riêng.

---

# 35. Header và JSON

Ở Buổi 10 chúng ta sẽ học:

```python
client.post(
    "/users",
    json={
        "name": "Alice",
    },
)
```

HTTPX sẽ giúp xử lý request body và Content-Type.

Do đó **không nên lúc nào cũng tự viết**:

```python
headers={
    "Content-Type": "application/json"
}
```

nếu HTTPX đã có cơ chế phù hợp cho kiểu request bạn đang sử dụng.

Nguyên tắc:

> Đừng tự quản lý thứ HTTPX đã quản lý tốt, trừ khi API yêu cầu behavior đặc biệt.

---

# 36. Header Architecture

Một API Client tốt có thể tổ chức:

```text
APIClient
│
├── Client defaults
│   ├── User-Agent
│   └── Accept
│
├── Authentication
│   └── Authorization
│
└── Request-specific
    ├── Content-Type
    ├── Idempotency-Key
    └── X-Request-ID
```

Không phải mọi header đều nên nằm ở cùng một cấp.

---

# 37. Ví dụ thực tế

```python
import httpx


class ArticleClient:

    def __init__(self, token: str):

        self.client = httpx.Client(
            base_url="https://api.example.com",
            headers={
                "User-Agent": "ArticleClient/1.0",
                "Accept": "application/json",
                "Authorization": f"Bearer {token}",
            },
            timeout=10.0,
        )

    def get_article(self, article_id: int):

        response = self.client.get(
            f"/articles/{article_id}"
        )

        response.raise_for_status()

        return response.json()

    def close(self):
        self.client.close()
```

Sử dụng:

```python
with ArticleClient(token) as client:
    ...
```

Nếu muốn hỗ trợ `with`, ta bổ sung:

```python
def __enter__(self):
    return self

def __exit__(self, exc_type, exc, tb):
    self.close()
```

---

# 38. Header lifecycle

Hãy hình thành mô hình:

```text
                    Client
                      │
              Default Headers
                      │
                      ▼
                   Request
                      │
             Request Headers
                      │
                      ▼
                Final Headers
                      │
                      ▼
                   Server
                      │
                      ▼
              Response Headers
```

Đây là mental model rất quan trọng.

---

# 39. Bài tập 1 — User-Agent

Tạo:

```python
client = httpx.Client(
    headers={
        "User-Agent": "MyCrawler/1.0",
    }
)
```

Gửi request.

Sau đó in:

```python
response.request.headers
```

Xác định `User-Agent` thực sự được gửi.

---

# 40. Bài tập 2 — Client vs Request

Tạo Client:

```python
headers={
    "User-Agent": "MyCrawler/1.0",
    "Accept": "application/json",
}
```

Request:

```python
headers={
    "X-Request-ID": "123",
}
```

In:

```python
response.request.headers
```

và xác định final headers.

---

# 41. Bài tập 3 — Override

Client:

```python
headers={
    "Accept": "application/json",
}
```

Request:

```python
headers={
    "Accept": "text/html",
}
```

Kiểm tra:

```python
response.request.headers
```

Xác định `Accept` cuối cùng là gì.

---

# 42. Bài tập 4 — Request vs Response

Gửi request:

```python
response = httpx.get(
    "https://example.com"
)
```

In:

```python
response.request.headers
```

và:

```python
response.headers
```

Tạo bảng:

```text
Request Headers
----------------
...

Response Headers
----------------
...
```

Sau đó giải thích sự khác nhau.

---

# 43. Bài tập 5 — Xây Header Configuration

Viết:

```python
class HTTPConfig:
    ...
```

chứa:

```text
user_agent
accept
authorization
```

Sau đó tạo:

```python
httpx.Client(...)
```

từ configuration này.

Mục tiêu là tách:

```text
Configuration
      ↓
HTTP Client
```

thay vì hard-code mọi thứ trong API client.

---

# 44. Bài tập 6 — Crawler Headers

Tạo:

```python
DEFAULT_HEADERS = {
    "User-Agent": "...",
    "Accept": "text/html",
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
}
```

Dùng với:

```python
httpx.Client(
    headers=DEFAULT_HEADERS
)
```

Sau đó crawl 3 URL và kiểm tra request headers.

---

# 45. Bài tập 7 — API Client

Thiết kế:

```text
ArticleClient
│
├── User-Agent
├── Accept
├── Authorization
├── timeout
├── base_url
│
├── get_article()
├── list_articles()
└── close()
```

Không được lặp:

```python
headers={...}
```

ở từng method nếu header mang tính global.

---

# Tổng kết Buổi 7

Bạn cần nắm chắc:

### Request headers

```python
response.request.headers
```

### Response headers

```python
response.headers
```

### Request headers

```python
client.get(
    url,
    headers={
        "X-Request-ID": "123"
    },
)
```

### Client default headers

```python
httpx.Client(
    headers={
        "User-Agent": "MyCrawler/1.0",
    }
)
```

### Các header quan trọng

```text
User-Agent
Accept
Authorization
Content-Type
Referer
Accept-Language
Content-Length
Set-Cookie
Location
```

### Đặc biệt nhớ

```text
Accept
   =
"Tôi muốn nhận gì?"

Content-Type
   =
"Tôi đang gửi gì?"
```

và:

```text
Client Headers
      ↓
Request Headers
      ↓
Final Request
```

---

# Roadmap Phần II

Bạn đang đi đúng roadmap:

```text
6. Query parameters       ✅
7. Headers                ← hôm nay
8. Cookies
9. Form data
10. JSON request
11. Multipart upload
12. File upload
13. Streaming response
14. Redirect
15. Authentication
```

**Buổi 8 — Cookies** sẽ rất thú vị vì chúng ta sẽ nối trực tiếp:

```text
Response
   │
   └── Set-Cookie
          ↓
      CookieJar
          ↓
       Client
          ↓
    Request tiếp theo
          │
          └── Cookie
```

và xây một ví dụ **login → giữ session → gọi các endpoint yêu cầu đăng nhập**.
