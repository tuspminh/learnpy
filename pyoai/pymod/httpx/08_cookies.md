# Buổi 8 — Cookies trong HTTPX

Cookies là phần rất quan trọng nếu bạn làm:

* Web crawler
* Scraper
* Login/session
* HTTP client
* Website yêu cầu session
* API sử dụng cookie authentication

Mental model hôm nay:

```text
Server
   │
   │ Set-Cookie
   ▼
HTTPX CookieJar
   │
   │ Cookie
   ▼
Request tiếp theo
```

---

# 1. Cookie là gì?

Server có thể trả:

```http
HTTP/1.1 200 OK
Set-Cookie: session_id=abc123
```

Browser sẽ lưu:

```text
session_id=abc123
```

Sau đó request tiếp theo:

```http
GET /profile
Cookie: session_id=abc123
```

Tức là:

```text
Request 1
   ↓
Server
   ↓
Set-Cookie
   ↓
Client lưu cookie
   ↓
Request 2
   ↓
Cookie được gửi lại
```

HTTPX có cơ chế quản lý việc này thông qua **CookieJar**.

---

# 2. Cookie khác Header thế nào?

Cookie thực tế được truyền qua HTTP headers:

```http
Cookie: session_id=abc123
```

Nhưng trong HTTPX, bạn không nên coi cookie đơn giản chỉ là:

```python
headers = {
    "Cookie": "session_id=abc123"
}
```

Thay vào đó:

```python
cookies = {
    "session_id": "abc123"
}
```

HTTPX sẽ quản lý cookie đúng ngữ cảnh hơn.

---

# 3. Gửi Cookie trực tiếp

Ví dụ:

```python
import httpx

response = httpx.get(
    "https://example.com/profile",
    cookies={
        "session_id": "abc123",
    },
)
```

HTTPX sẽ tạo request tương ứng với cookie.

---

# 4. Cookie + Client

Nếu nhiều request cần cùng cookie:

```python
with httpx.Client(
    cookies={
        "session_id": "abc123",
    }
) as client:

    response = client.get("/profile")
```

Các request của Client có thể sử dụng cookie đó.

Đây là lý do `Client` rất quan trọng.

---

# 5. Cookie session

Giả sử website:

```text
POST /login
     ↓
Set-Cookie: session=abc123
     ↓
GET /profile
Cookie: session=abc123
```

Ta muốn:

```text
Client
 │
 ├── login()
 │
 └── get_profile()
```

Cookie phải được giữ giữa hai request.

---

# 6. CookieJar

HTTPX có:

```python
client.cookies
```

Ví dụ:

```python
import httpx

client = httpx.Client()

print(client.cookies)
```

Đây là cookie jar của Client.

Mental model:

```text
httpx.Client
     │
     ├── headers
     ├── cookies
     ├── connection pool
     └── timeout
```

---

# 7. Server Set-Cookie

Giả sử server trả:

```http
Set-Cookie: session_id=abc123
```

Sau request:

```python
response = client.get(
    "https://example.com/login"
)
```

Client có thể lưu cookie do server thiết lập.

Bạn có thể kiểm tra:

```python
print(client.cookies)
```

---

# 8. Vì sao phải dùng Client?

So sánh:

### Không dùng Client

```python
httpx.get(...)
httpx.get(...)
httpx.get(...)
```

Mỗi request độc lập hơn về mặt state.

### Dùng Client

```python
with httpx.Client() as client:
    client.get(...)
    client.get(...)
    client.get(...)
```

Client giữ state giữa các request, bao gồm cookie state.

Đây là một trong những lý do lớn để dùng `httpx.Client` khi làm session-based application.

---

# 9. Cookie persistence

Ví dụ:

```python
with httpx.Client() as client:

    client.get(
        "https://example.com/login"
    )

    client.get(
        "https://example.com/profile"
    )
```

Nếu response login có:

```http
Set-Cookie: session=abc123
```

thì cookie có thể được lưu vào Client và được sử dụng cho request tiếp theo khi cookie phù hợp với URL.

---

# 10. Kiểm tra cookie

Bạn có thể:

```python
print(client.cookies)
```

Hoặc:

```python
print(dict(client.cookies))
```

Ví dụ:

```text
{
    "session": "abc123"
}
```

---

# 11. Set cookie thủ công

Bạn có thể:

```python
client.cookies.set(
    "session",
    "abc123",
)
```

Sau đó:

```python
response = client.get(
    "https://example.com/profile"
)
```

Client có thể gửi cookie phù hợp.

---

# 12. Xóa cookie

Bạn có thể quản lý cookie jar.

Ví dụ concept:

```python
client.cookies.clear()
```

Sau đó:

```python
print(client.cookies)
```

Cookie jar trở về trạng thái rỗng.

Điều này hữu ích khi:

* logout
* reset session
* test
* đổi user
* crawler nhiều account

---

# 13. Cookie không phải global string

Một lỗi tư duy phổ biến là:

```python
COOKIE = "session=abc123"
```

rồi:

```python
headers = {
    "Cookie": COOKIE
}
```

Cách này có thể hoạt động trong trường hợp rất đơn giản, nhưng bạn đang tự quản lý rất nhiều logic mà HTTPX đã có CookieJar.

Cookie thực tế còn có:

```text
name
value
domain
path
expires
max-age
secure
HttpOnly
SameSite
```

Do đó nên để CookieJar quản lý.

---

# 14. Cookie có Domain

Ví dụ server:

```http
Set-Cookie: session=abc123; Domain=example.com
```

Cookie này có phạm vi domain nhất định.

Ví dụ:

```text
example.com
api.example.com
```

việc cookie có được gửi hay không phụ thuộc các thuộc tính của cookie và URL request.

Đây là lý do không nên đơn giản hóa cookie thành:

```python
dict[str, str]
```

---

# 15. Cookie có Path

Ví dụ:

```http
Set-Cookie: session=abc123; Path=/account
```

Cookie này liên quan đến path:

```text
/account
```

Request:

```text
/account/profile
```

có thể phù hợp.

Nhưng:

```text
/public
```

thì không nhất thiết.

HTTPX CookieJar xử lý các rule này.

---

# 16. Secure Cookie

Cookie có thể có:

```http
Secure
```

Ví dụ:

```http
Set-Cookie: session=abc123; Secure
```

Ý nghĩa:

> Cookie chỉ nên được gửi qua HTTPS.

Đây là một cơ chế bảo mật quan trọng.

---

# 17. HttpOnly

Cookie có thể có:

```http
HttpOnly
```

Ví dụ:

```http
Set-Cookie: session=abc123; HttpOnly
```

Ý nghĩa chủ yếu là cookie không được JavaScript phía client truy cập theo cơ chế cookie của browser.

Đối với HTTPX — một HTTP client Python, bạn cần tập trung vào việc cookie được lưu và gửi theo request rules; HTTPX không phải browser và không thực thi JavaScript.

---

# 18. SameSite

Bạn sẽ gặp:

```text
SameSite=Lax
SameSite=Strict
SameSite=None
```

Đây chủ yếu là cơ chế browser liên quan đến cross-site requests.

Điểm quan trọng:

> HTTPX không phải browser.

Đừng kỳ vọng HTTPX sẽ mô phỏng toàn bộ cookie behavior của Chrome/Firefox.

---

# 19. Cookie và Browser

So sánh:

```text
Browser
│
├── Cookies
├── JavaScript
├── DOM
├── Local Storage
├── Service Worker
└── Browser security policies
```

Trong khi:

```text
HTTPX
│
├── HTTP request
├── HTTP response
├── CookieJar
├── Headers
├── Connection pool
└── Streaming
```

HTTPX là HTTP client, **không phải browser automation framework**.

Nếu website yêu cầu JavaScript để tạo token/session, HTTPX có thể không đủ.

---

# 20. Login Session

Đây là use case quan trọng nhất.

Giả sử:

```text
POST /login
```

Server trả:

```http
Set-Cookie: session=abc123
```

Sau đó:

```text
GET /dashboard
```

yêu cầu:

```http
Cookie: session=abc123
```

Code:

```python
import httpx


with httpx.Client(
    base_url="https://example.com"
) as client:

    response = client.post(
        "/login",
        data={
            "username": "alice",
            "password": "secret",
        },
    )

    response.raise_for_status()

    response = client.get(
        "/dashboard"
    )

    response.raise_for_status()

    print(response.text)
```

Điểm quan trọng:

```text
POST /login
     ↓
Set-Cookie
     ↓
Client.cookies
     ↓
GET /dashboard
     ↓
Cookie
```

---

# 21. Kiểm tra Cookie sau login

Ta có thể debug:

```python
with httpx.Client(
    base_url="https://example.com"
) as client:

    response = client.post(
        "/login",
        data={
            "username": "alice",
            "password": "secret",
        },
    )

    print(client.cookies)
```

Nếu server thực sự set cookie phù hợp, bạn có thể quan sát state của Client.

---

# 22. Cookie + Headers

Request có thể có cả:

```python
client = httpx.Client(
    headers={
        "User-Agent": "MyApp/1.0",
        "Accept": "application/json",
    },
    cookies={
        "locale": "vi",
    },
)
```

Mental model:

```text
Client
│
├── Headers
│
├── Cookies
│
├── Timeout
│
└── Connection Pool
```

Đây là một HTTP client stateful.

---

# 23. Session object

Bạn có thể tạo abstraction:

```python
class Session:
    def __init__(self):
        self.client = httpx.Client()

    def login(self):
        ...

    def get_profile(self):
        ...

    def close(self):
        self.client.close()
```

Từ đó:

```text
Session
   │
   ├── Client
   │     ├── CookieJar
   │     ├── Headers
   │     └── Pool
   │
   ├── login()
   └── get_profile()
```

Đây là pattern rất hữu ích cho scraper.

---

# 24. Ví dụ Web Crawler có Session

Giả sử website có:

```text
/login
/books
/books/1
/books/2
```

Ta thiết kế:

```python
import httpx


class BookSession:

    def __init__(self):
        self.client = httpx.Client(
            base_url="https://example.com",
            headers={
                "User-Agent": "BookCrawler/1.0",
            },
            timeout=10.0,
        )

    def login(
        self,
        username: str,
        password: str,
    ):
        response = self.client.post(
            "/login",
            data={
                "username": username,
                "password": password,
            },
        )

        response.raise_for_status()

    def get(self, path: str):
        response = self.client.get(path)
        response.raise_for_status()
        return response

    def close(self):
        self.client.close()
```

---

# 25. Context Manager

Tốt hơn:

```python
class BookSession:

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.close()
```

Sử dụng:

```python
with BookSession() as session:

    session.login(
        "alice",
        "secret",
    )

    response = session.get(
        "/books"
    )
```

---

# 26. Cookie lifecycle

Hãy ghi nhớ sơ đồ này:

```text
                    SERVER
                       │
                       │
              Set-Cookie: session=...
                       │
                       ▼
                ┌─────────────┐
                │   HTTPX     │
                │ CookieJar   │
                └─────────────┘
                       │
                       │ cookie matching
                       ▼
              Request tiếp theo
                       │
              Cookie: session=...
                       │
                       ▼
                    SERVER
```

Đây là mental model quan trọng nhất của Buổi 8.

---

# 27. Cookie Jar và nhiều domain

Một CookieJar có thể chứa cookie từ nhiều domain.

Ví dụ:

```text
example.com
api.example.com
cdn.example.com
```

Nhưng cookie chỉ được gửi khi phù hợp với domain/path/security rules.

Vì vậy:

```python
client.cookies
```

có thể chứa nhiều cookie hơn số cookie được gửi trong một request cụ thể.

---

# 28. Debug Cookie

Một pattern rất hữu ích:

```python
response = client.get(url)

print("Cookies:")
print(client.cookies)

print("\nRequest cookies:")
print(
    response.request.headers.get("cookie")
)

print("\nResponse Set-Cookie:")
print(
    response.headers.get("set-cookie")
)
```

Bạn có thể phân tích:

```text
Response
   │
   └── Set-Cookie
          ↓
      CookieJar
          ↓
       Request
          ↓
       Cookie
```

---

# 29. Đừng tự copy `Set-Cookie`

Không nên làm:

```python
cookie = response.headers["set-cookie"]

headers = {
    "Cookie": cookie,
}
```

Vì:

```text
Set-Cookie
```

và:

```text
Cookie
```

không phải cùng một format.

Ví dụ:

```http
Set-Cookie: session=abc123; Path=/; HttpOnly
```

request không gửi nguyên dòng đó:

```http
Cookie: session=abc123
```

CookieJar tồn tại chính là để xử lý những khác biệt này.

---

# 30. Cookie Authentication

Một số hệ thống dùng cookie làm authentication:

```text
Login
 ↓
session cookie
 ↓
authenticated requests
```

Trong trường hợp này:

```python
client = httpx.Client()
```

thực chất đang giữ **authentication state**.

Do đó:

```text
CookieJar
```

có thể là một phần quan trọng của security state.

---

# 31. Logout

Một website có thể:

```text
POST /logout
```

và server:

```http
Set-Cookie: session=; Max-Age=0
```

Client nhận response và cập nhật CookieJar.

Bạn cũng có thể chủ động reset:

```python
client.cookies.clear()
```

Nhưng cần phân biệt:

```text
Client-side cookie cleared
```

với:

```text
Server-side session invalidated
```

Hai việc này không nhất thiết giống nhau.

---

# 32. Multi-account crawler

Một ứng dụng crawler có thể có:

```text
Account A
   ↓
Client A
   ↓
CookieJar A

Account B
   ↓
Client B
   ↓
CookieJar B
```

**Không nên dùng chung một CookieJar cho nhiều account** nếu session phải độc lập.

Thiết kế:

```python
client_a = httpx.Client(...)
client_b = httpx.Client(...)
```

mỗi Client có state riêng.

---

# 33. Cookie Isolation

Đây là một nguyên tắc quan trọng:

```text
User A
  │
  └── Client A
        └── Cookies A

User B
  │
  └── Client B
        └── Cookies B
```

Không:

```text
User A ─┐
        ├── Shared Client
User B ─┘
```

nếu Client chứa session cookie của từng user.

---

# 34. Cookies + concurrency

Đây là vấn đề nâng cao.

Nếu nhiều task cùng sử dụng một Client:

```text
Task A ─┐
Task B ─┼── Client
Task C ─┘
```

và Client có session state:

```text
CookieJar
```

thì bạn phải suy nghĩ kỹ về state sharing.

Đặc biệt:

```text
Task A login account A
Task B login account B
```

mà dùng chung state có thể dẫn đến logic sai.

Đây là một trong những lý do architecture của HTTP client quan trọng khi chuyển sang async/concurrent crawler.

---

# 35. Cookie Persistence

Thông thường:

```python
client = httpx.Client()
```

cookie nằm trong memory.

Khi:

```python
client.close()
```

và process kết thúc, cookie không tự động trở thành một browser profile persistent.

Nếu bạn muốn:

```text
Run 1
   ↓
save session
   ↓
Run 2
   ↓
restore session
```

bạn phải thiết kế persistence riêng.

Ví dụ:

```text
CookieJar
   ↓
serialize
   ↓
JSON / database
   ↓
restore
```

Nhưng cần đặc biệt cẩn thận vì session cookie có thể là credential.

---

# 36. Security

Không nên log:

```python
print(client.cookies)
```

trong production nếu cookie chứa session authentication.

Cookie có thể tương đương với:

```text
"chìa khóa đăng nhập"
```

Nếu attacker lấy được session cookie, họ có thể sử dụng session tùy theo hệ thống.

Do đó:

```text
Logs
Database
Exception messages
Screenshots
```

không nên chứa session secrets một cách tùy tiện.

---

# 37. So sánh Cookie và Authorization

Hai kiểu authentication phổ biến:

### Cookie session

```text
Login
 ↓
Set-Cookie
 ↓
CookieJar
 ↓
Cookie
```

### Bearer token

```text
Token
 ↓
Authorization header
 ↓
Server
```

Ví dụ:

```python
headers = {
    "Authorization": f"Bearer {token}"
}
```

Cookie:

```python
cookies = {
    "session": session_id
}
```

Buổi 15 chúng ta sẽ đi sâu vào Authentication.

---

# 38. Bài tập 1 — Cookie thủ công

Tạo:

```python
client = httpx.Client(
    cookies={
        "session_id": "abc123",
    }
)
```

Gửi request.

Kiểm tra:

```python
response.request.headers
```

Xác định header `Cookie` thực tế.

---

# 39. Bài tập 2 — CookieJar

Tạo:

```python
client = httpx.Client()

client.cookies.set(
    "session_id",
    "abc123",
)
```

Sau đó request.

Kiểm tra:

```python
print(client.cookies)
```

và:

```python
print(response.request.headers)
```

---

# 40. Bài tập 3 — Login Session

Viết:

```python
class SessionClient:
    ...
```

có:

```text
login()
get_profile()
logout()
close()
```

Luồng:

```text
login()
   ↓
Cookie
   ↓
get_profile()
   ↓
logout()
```

---

# 41. Bài tập 4 — Debug Cookie

Viết function:

```python
def debug_cookies(
    client: httpx.Client,
    response: httpx.Response,
):
    ...
```

In:

```text
Client cookies
Response Set-Cookie
Request Cookie
```

Nhưng **không in password/token**.

---

# 42. Bài tập 5 — Multi-account

Thiết kế:

```text
AccountSession
│
├── username
├── httpx.Client
└── CookieJar
```

Tạo:

```python
account_a
account_b
```

đảm bảo cookie của A không ảnh hưởng B.

---

# 43. Bài tập 6 — Crawler Session

Thiết kế:

```text
CrawlerSession
│
├── httpx.Client
├── headers
├── cookies
├── timeout
│
├── login()
├── fetch()
└── close()
```

Mục tiêu:

```text
login
 ↓
session established
 ↓
crawl pages
 ↓
same cookies
 ↓
logout
```

---

# Tổng kết Buổi 8

Bạn cần nhớ:

### Gửi cookie

```python
client = httpx.Client(
    cookies={
        "session": "abc123",
    }
)
```

### CookieJar

```python
client.cookies
```

### Set cookie

```python
client.cookies.set(
    "session",
    "abc123",
)
```

### Clear

```python
client.cookies.clear()
```

### Debug

```python
response.request.headers.get("cookie")
```

và:

```python
response.headers.get("set-cookie")
```

---

## Mental model cần thuộc

```text
                ┌──────────────┐
                │    Server    │
                └──────┬───────┘
                       │
                  Set-Cookie
                       │
                       ▼
                ┌──────────────┐
                │ HTTPX Client │
                │              │
                │  CookieJar   │
                └──────┬───────┘
                       │
                Cookie matching
                       │
                       ▼
                ┌──────────────┐
                │   Request    │
                │ Cookie: ...  │
                └──────┬───────┘
                       │
                       ▼
                    Server
```

Và một nguyên tắc rất quan trọng:

> **Cookie là state của HTTP session.** Vì vậy khi xây crawler/API client có đăng nhập, hãy coi `httpx.Client + CookieJar` như một đơn vị session, thay vì rải cookie thủ công khắp code.

---

# Roadmap tiếp theo

```text
6. Query parameters       ✅
7. Headers                ✅
8. Cookies                ← hiện tại
9. Form data
10. JSON request
11. Multipart upload
12. File upload
13. Streaming response
14. Redirect
15. Authentication
```

**Buổi 9 — Form Data** chúng ta sẽ phân biệt thật rõ:

```text
data={}
json={}
files={}
```

và hiểu tại sao:

```python
client.post(
    "/login",
    data={
        "username": "...",
        "password": "...",
    },
)
```

khác hoàn toàn về HTTP request body so với:

```python
client.post(
    "/login",
    json={
        "username": "...",
        "password": "...",
    },
)
```

Đây là nền tảng rất quan trọng trước khi sang **JSON request và Multipart Upload**.
