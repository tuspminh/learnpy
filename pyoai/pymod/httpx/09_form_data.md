# Buổi 9 — Form Data trong HTTPX

Hôm nay chúng ta học cách gửi **HTML Form Data** bằng HTTPX.

Đây là phần rất quan trọng vì khi làm crawler/scraper, bạn thường gặp:

```text
Login form
Search form
Filter form
POST form
Web form
```

Mental model:

```text
Python dict
    ↓
data=
    ↓
HTTPX encode
    ↓
application/x-www-form-urlencoded
    ↓
Server
```

---

# 1. Form Data là gì?

Một HTML form đơn giản:

```html
<form method="post">
    <input name="username">
    <input name="password">
    <button type="submit">Login</button>
</form>
```

Khi submit, browser có thể gửi:

```http
POST /login HTTP/1.1
Content-Type: application/x-www-form-urlencoded

username=alice&password=secret
```

Đây là **form URL encoded**.

Trong HTTPX, cách biểu diễn rất đơn giản:

```python
import httpx

response = httpx.post(
    "https://example.com/login",
    data={
        "username": "alice",
        "password": "secret",
    },
)
```

---

# 2. `data=` nghĩa là gì?

Khi dùng:

```python
data={
    "username": "alice",
    "password": "secret",
}
```

HTTPX hiểu rằng bạn đang gửi form data.

Về concept:

```text
data={}
   ↓
username=alice&password=secret
   ↓
HTTP request body
```

---

# 3. `data=` khác `params=`

Đây là điểm phải nhớ.

### `params=`

Đi vào **URL**:

```python
client.get(
    "/search",
    params={
        "q": "python",
    },
)
```

Kết quả:

```text
/search?q=python
```

### `data=`

Đi vào **request body**:

```python
client.post(
    "/search",
    data={
        "q": "python",
    },
)
```

Concept:

```text
params=
    ↓
URL

data=
    ↓
BODY
```

---

# 4. So sánh

```python
client.get(
    "/search",
    params={
        "q": "python",
    },
)
```

```http
GET /search?q=python
```

Trong khi:

```python
client.post(
    "/search",
    data={
        "q": "python",
    },
)
```

có body dạng form.

Đây là khác biệt cực kỳ quan trọng.

---

# 5. Form Encoding

Ví dụ:

```python
data = {
    "username": "alice",
    "password": "123456",
}
```

HTTPX sẽ encode thành dạng tương đương:

```text
username=alice&password=123456
```

và request có:

```http
Content-Type: application/x-www-form-urlencoded
```

---

# 6. Không tự encode

Không nên tự làm:

```python
from urllib.parse import urlencode

body = urlencode({
    "username": "alice",
    "password": "123456",
})
```

rồi:

```python
client.post(
    url,
    content=body,
)
```

trong trường hợp HTTPX đã có abstraction phù hợp.

Nên:

```python
client.post(
    url,
    data={
        "username": "alice",
        "password": "123456",
    },
)
```

Để HTTPX xử lý encoding.

---

# 7. Form Data thường dùng POST

Ví dụ login:

```python
response = client.post(
    "/login",
    data={
        "username": "alice",
        "password": "secret",
    },
)
```

Đây là pattern rất phổ biến.

Luồng:

```text
POST /login
      ↓
form data
      ↓
Server
      ↓
Set-Cookie
      ↓
CookieJar
```

Kết hợp trực tiếp với **Buổi 8 — Cookies**.

---

# 8. Login + Cookie Session

Ví dụ:

```python
import httpx

with httpx.Client(
    base_url="https://example.com",
) as client:

    response = client.post(
        "/login",
        data={
            "username": "alice",
            "password": "secret",
        },
    )

    response.raise_for_status()

    print(client.cookies)

    response = client.get("/profile")

    response.raise_for_status()

    print(response.text)
```

Nếu server dùng session cookie:

```text
POST /login
    ↓
Set-Cookie
    ↓
client.cookies
    ↓
GET /profile
    ↓
Cookie
```

---

# 9. `data=` không có nghĩa là JSON

Đây là lỗi rất phổ biến.

Sai tư duy:

```python
client.post(
    "/users",
    data={
        "name": "Alice",
    },
)
```

và nghĩ:

```text
"HTTPX gửi JSON"
```

Không.

Nếu bạn muốn JSON:

```python
client.post(
    "/users",
    json={
        "name": "Alice",
    },
)
```

Hai request này khác nhau.

---

# 10. `data=` vs `json=`

## Form

```python
client.post(
    "/users",
    data={
        "name": "Alice",
        "age": 20,
    },
)
```

Concept body:

```text
name=Alice&age=20
```

Content-Type:

```text
application/x-www-form-urlencoded
```

---

## JSON

```python
client.post(
    "/users",
    json={
        "name": "Alice",
        "age": 20,
    },
)
```

Concept body:

```json
{
    "name": "Alice",
    "age": 20
}
```

Content-Type:

```text
application/json
```

---

# 11. Server quyết định bạn phải dùng gì

Không phải:

```text
POST → luôn data
```

hoặc:

```text
API → luôn json
```

Bạn phải xem API/HTML form yêu cầu gì.

Ví dụ:

```text
HTML form
    ↓
application/x-www-form-urlencoded

JSON API
    ↓
application/json

File upload
    ↓
multipart/form-data
```

---

# 12. Form với nhiều fields

Ví dụ:

```python
data = {
    "username": "alice",
    "password": "secret",
    "remember": "1",
    "language": "vi",
}
```

Gửi:

```python
response = client.post(
    "/login",
    data=data,
)
```

---

# 13. Checkbox

HTML:

```html
<input
    type="checkbox"
    name="remember"
    value="1"
>
```

Nếu được chọn, browser có thể gửi:

```text
remember=1
```

HTTPX:

```python
data = {
    "remember": "1",
}
```

Nếu server yêu cầu format cụ thể, hãy gửi đúng format đó.

Đừng mặc định:

```python
"remember": True
```

sẽ luôn tương đương với browser.

API/form backend có thể yêu cầu:

```text
1
yes
on
true
```

---

# 14. Select

HTML:

```html
<select name="category">
    <option value="python">
        Python
    </option>

    <option value="rust">
        Rust
    </option>
</select>
```

Nếu chọn Python:

```python
data = {
    "category": "python",
}
```

---

# 15. Hidden input

Crawler thường gặp:

```html
<input
    type="hidden"
    name="csrf_token"
    value="abc123"
>
```

Form thực tế:

```python
data = {
    "username": "alice",
    "password": "secret",
    "csrf_token": "abc123",
}
```

Đây là use case cực kỳ quan trọng.

---

# 16. CSRF Token

Một website có thể yêu cầu:

```text
GET /login
    ↓
HTML
    ↓
csrf_token
    ↓
POST /login
```

HTTPX phải:

```text
1. GET login page
2. Parse HTML
3. Extract CSRF token
4. POST form
5. Cookie/session tiếp tục
```

Với kiến thức bạn đã học về **Selectolax/BeautifulSoup**, bạn có thể kết hợp rất tự nhiên:

```text
HTTPX
  ↓
HTML
  ↓
Selectolax
  ↓
CSRF token
  ↓
HTTPX POST data=
```

Đây là một workflow crawler rất thực tế.

---

# 17. Ví dụ CSRF

Giả sử HTML:

```html
<form method="post">
    <input
        type="hidden"
        name="csrf_token"
        value="abc123"
    >

    <input name="username">
    <input name="password">
</form>
```

Sau khi GET:

```python
response = client.get("/login")
```

Parse:

```python
from selectolax.parser import HTMLParser

tree = HTMLParser(response.text)

token = tree.css_first(
    'input[name="csrf_token"]'
).attributes["value"]
```

Sau đó:

```python
response = client.post(
    "/login",
    data={
        "username": "alice",
        "password": "secret",
        "csrf_token": token,
    },
)
```

Workflow:

```text
HTTPX GET
    ↓
HTML
    ↓
Selectolax
    ↓
CSRF token
    ↓
HTTPX POST
    ↓
data={}
```

Đây là một ví dụ rất sát với công việc scraper.

---

# 18. Form URL Encoding

Các ký tự đặc biệt sẽ được HTTPX encode phù hợp.

Ví dụ:

```python
data = {
    "q": "python httpx & asyncio",
}
```

Không cần tự:

```python
quote(...)
```

HTTPX xử lý phần encoding.

---

# 19. Unicode

Form có thể chứa:

```python
data = {
    "keyword": "lập trình Python",
}
```

HTTPX xử lý việc encode request body.

Bạn không cần tự biến:

```text
lập trình Python
```

thành percent-encoding.

---

# 20. Multiple values

HTML form có thể có nhiều input cùng name:

```html
<input name="tag" value="python">
<input name="tag" value="httpx">
<input name="tag" value="asyncio">
```

Backend có thể mong đợi:

```text
tag=python&tag=httpx&tag=asyncio
```

Có thể biểu diễn dữ liệu theo dạng nhiều giá trị:

```python
data = [
    ("tag", "python"),
    ("tag", "httpx"),
    ("tag", "asyncio"),
]
```

Đây là một kỹ thuật rất hữu ích khi form có **duplicate field names**.

---

# 21. Dictionary vs list of tuples

### Dictionary

```python
data = {
    "username": "alice",
    "password": "secret",
}
```

Phù hợp khi mỗi key có một value.

### List of tuples

```python
data = [
    ("tag", "python"),
    ("tag", "httpx"),
    ("tag", "asyncio"),
]
```

Phù hợp khi cần giữ:

```text
same key
multiple values
```

Mental model:

```text
dict
    ↓
key → value

list[tuple]
    ↓
(key, value)
(key, value)
(key, value)
```

---

# 22. Form checkbox nhiều giá trị

Ví dụ:

```html
<input name="tag" value="python">
<input name="tag" value="httpx">
```

Dùng:

```python
data = [
    ("tag", "python"),
    ("tag", "httpx"),
]
```

Đây là pattern bạn nên nhớ.

---

# 23. Form Data và Headers

Bạn có thể kiểm tra request:

```python
response = client.post(
    "/login",
    data={
        "username": "alice",
        "password": "secret",
    },
)

print(response.request.headers)
```

Bạn sẽ thấy HTTPX đã thiết lập Content-Type phù hợp cho form request.

---

# 24. Debug Body

Bạn có thể kiểm tra:

```python
request = response.request

print(request.headers)
print(request.content)
```

Ví dụ body có dạng bytes.

Đây là kỹ thuật cực kỳ hữu ích khi server trả:

```text
400 Bad Request
```

và bạn không biết request của mình sai ở đâu.

---

# 25. `data=` với GET?

Về mặt API HTTPX, `data=` chủ yếu được dùng khi gửi request body, đặc biệt với POST/PUT/PATCH.

Nếu bạn muốn query string:

```python
params={}
```

Ví dụ:

```python
client.get(
    "/search",
    params={
        "q": "python",
    },
)
```

Nếu muốn form body:

```python
client.post(
    "/search",
    data={
        "q": "python",
    },
)
```

Hãy giữ hai khái niệm tách biệt:

```text
params → URL
data   → BODY
```

---

# 26. Form Data trong PUT/PATCH

Form encoding không chỉ dành cho POST.

Ví dụ:

```python
client.put(
    "/users/10",
    data={
        "name": "Alice",
    },
)
```

Hoặc:

```python
client.patch(
    "/users/10",
    data={
        "name": "Alice",
    },
)
```

Tất nhiên server phải hỗ trợ kiểu request đó.

---

# 27. Một FormClient

Ta có thể tạo abstraction:

```python
import httpx


class FormClient:

    def __init__(self, base_url: str):
        self.client = httpx.Client(
            base_url=base_url,
            timeout=10.0,
        )

    def submit(
        self,
        path: str,
        data: dict[str, str],
    ):
        response = self.client.post(
            path,
            data=data,
        )

        response.raise_for_status()

        return response

    def close(self):
        self.client.close()
```

Sử dụng:

```python
with FormClient(
    "https://example.com"
) as client:

    response = client.submit(
        "/login",
        {
            "username": "alice",
            "password": "secret",
        },
    )
```

---

# 28. Kết hợp với Cookie Session

Ta có:

```text
FormClient
    │
    ├── httpx.Client
    │       │
    │       ├── CookieJar
    │       ├── Headers
    │       ├── Timeout
    │       └── Connection Pool
    │
    └── submit()
```

Login:

```python
client.post(
    "/login",
    data={
        "username": "...",
        "password": "...",
    },
)
```

Sau đó session tiếp tục tồn tại trong Client nếu server thiết lập cookie phù hợp.

---

# 29. Form Login hoàn chỉnh

Ví dụ architecture:

```python
import httpx


class WebsiteSession:

    def __init__(self, base_url: str):
        self.client = httpx.Client(
            base_url=base_url,
            headers={
                "User-Agent": "MyCrawler/1.0",
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

    def get_profile(self):
        response = self.client.get(
            "/profile"
        )

        response.raise_for_status()

        return response.text

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
```

Sử dụng:

```python
with WebsiteSession(
    "https://example.com"
) as session:

    session.login(
        "alice",
        "secret",
    )

    html = session.get_profile()
```

---

# 30. Đừng nhầm Form với Multipart

Đây là bước chuẩn bị cho Buổi 11.

### Form URL encoded

```python
data={
    "name": "Alice",
}
```

Body concept:

```text
name=Alice
```

Content-Type:

```text
application/x-www-form-urlencoded
```

### Multipart

```python
files={
    "avatar": ...
}
```

Body:

```text
multipart/form-data
```

Dùng cho các form có upload file hoặc multipart fields.

---

# 31. Ba loại request body cần thuộc

Từ hôm nay hãy hình thành bảng này:

| HTTPX     | Body      | Content-Type thường gặp             |
| --------- | --------- | ----------------------------------- |
| `params=` | URL query | —                                   |
| `data=`   | Form      | `application/x-www-form-urlencoded` |
| `json=`   | JSON      | `application/json`                  |
| `files=`  | Multipart | `multipart/form-data`               |

Mental model:

```text
params=
   ↓
URL

data=
   ↓
Form Body

json=
   ↓
JSON Body

files=
   ↓
Multipart Body
```

Đây là một trong những bảng quan trọng nhất của phần HTTPX Request nâng cao.

---

# 32. Bài tập 1 — Form Login

Viết:

```python
response = client.post(
    "/login",
    data={
        "username": "alice",
        "password": "secret",
    },
)
```

Sau đó in:

```python
response.request.headers
```

và:

```python
response.request.content
```

Xác định:

```text
Content-Type
Body
```

---

# 33. Bài tập 2 — Params vs Data

Viết hai request:

### Request A

```python
client.get(
    "/search",
    params={
        "q": "python",
    },
)
```

### Request B

```python
client.post(
    "/search",
    data={
        "q": "python",
    },
)
```

Sau đó so sánh:

```python
response.request.url
response.request.content
```

Mục tiêu:

> Nhìn vào request và xác định dữ liệu nằm ở URL hay body.

---

# 34. Bài tập 3 — Multiple Fields

Tạo:

```python
data = [
    ("tag", "python"),
    ("tag", "httpx"),
    ("tag", "asyncio"),
]
```

Gửi bằng:

```python
client.post(...)
```

Sau đó kiểm tra request body.

---

# 35. Bài tập 4 — CSRF

Tạo HTML giả:

```html
<form>
    <input
        type="hidden"
        name="csrf_token"
        value="abc123"
    >
</form>
```

Dùng Selectolax để lấy:

```text
abc123
```

Sau đó xây:

```python
data = {
    "username": "alice",
    "password": "secret",
    "csrf_token": token,
}
```

---

# 36. Bài tập 5 — Login Session

Xây:

```text
WebsiteSession
│
├── login()
├── get_profile()
├── get_dashboard()
└── close()
```

Luồng:

```text
login()
   ↓
POST + data={}
   ↓
Set-Cookie
   ↓
CookieJar
   ↓
get_profile()
   ↓
Cookie
```

---

# 37. Bài tập 6 — Debug HTTP

Viết helper:

```python
def debug_request(response):
    ...
```

In:

```text
METHOD
URL
HEADERS
BODY
```

Ví dụ output:

```text
POST
https://example.com/login

Headers:
Content-Type: ...

Body:
username=alice&password=secret
```

**Không log password trong ứng dụng thật.** Bài tập này chỉ để học HTTP request structure.

---

# 38. Bài tập tư duy

Cho:

```python
client.post(
    "/login",
    params={
        "next": "/dashboard",
    },
    data={
        "username": "alice",
        "password": "secret",
    },
)
```

Hãy trả lời:

### Câu 1

`next` nằm ở đâu?

### Câu 2

`username` nằm ở đâu?

### Câu 3

Request body có phải JSON không?

### Câu 4

`Content-Type` body thường là gì?

### Câu 5

Nếu server trả:

```http
Set-Cookie: session=abc123
```

Cookie sẽ được quản lý ở đâu?

---

# Tổng kết Buổi 9

## `params=`

```python
params={
    "page": 2,
}
```

→ **Query String**

```text
?page=2
```

---

## `data=`

```python
data={
    "username": "alice",
    "password": "secret",
}
```

→ **Form Body**

```text
username=alice&password=secret
```

---

## `json=`

```python
json={
    "username": "alice",
}
```

→ **JSON Body**

```json
{
    "username": "alice"
}
```

---

## `files=`

```python
files={
    "file": ...
}
```

→ **Multipart**

Sẽ học ở Buổi 11–12.

---

# Mental model cuối buổi

```text
                  HTTPX Request
                       │
          ┌────────────┼────────────┐
          │            │            │
       params=       data=        json=
          │            │            │
          ▼            ▼            ▼
        URL          Form         JSON
          │            │            │
          ▼            ▼            ▼
      Query String    Body         Body
```

Và kết hợp với những gì đã học:

```text
                    HTTPX Client
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
    Headers           Cookies           Timeout
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                      Request
                         │
              ┌──────────┼──────────┐
              │          │          │
           params=      data=      json=
              │          │          │
             URL        Form       JSON
```

### Roadmap hiện tại

```text
6. Query parameters       ✅
7. Headers                ✅
8. Cookies                ✅
9. Form data              ← hiện tại
10. JSON request
11. Multipart upload
12. File upload
13. Streaming response
14. Redirect
15. Authentication
```

**Buổi 10 — JSON Request** sẽ đi sâu vào `json=`: serialization, `Content-Type`, nested object, list, `None`, boolean, encoding, `response.json()`, xử lý JSON API lỗi và đặc biệt là **phân biệt `json=` với `content=` và `data=`**.
