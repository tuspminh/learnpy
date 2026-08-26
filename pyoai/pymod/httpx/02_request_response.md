# Buổi 2 — Request & Response Deep Dive

Ở buổi 1, bạn dùng:

```python
httpx.get(...)
httpx.post(...)
```

Hôm nay chúng ta đi sâu hơn vào **hai object cốt lõi của HTTPX**:

```text
Request
   ↓
HTTP Server
   ↓
Response
```

Đây là nền tảng để sau này học `Client`, authentication, retry, middleware/transport và async HTTPX.

---

# 1. Request là gì?

Khi bạn viết:

```python
import httpx

response = httpx.get("https://example.com")
```

HTTPX thực chất phải tạo ra một HTTP request.

Bạn có thể tự tạo `Request`:

```python
request = httpx.Request(
    "GET",
    "https://example.com",
)

print(request)
```

Kết quả dạng:

```text
<Request('GET', 'https://example.com')>
```

`Request` đại diện cho:

> "Tôi muốn gửi yêu cầu HTTP này."

---

# 2. Request gồm những gì?

Một HTTP request cơ bản:

```text
Request
│
├── method
├── url
├── headers
├── content
├── extensions
└── ...
```

Ví dụ:

```python
request = httpx.Request(
    "GET",
    "https://example.com",
)

print(request.method)
print(request.url)
print(request.headers)
```

---

# 3. HTTP Method

```python
request = httpx.Request(
    "POST",
    "https://example.com/api",
)

print(request.method)
```

Kết quả:

```text
POST
```

HTTPX cung cấp:

```python
request.method
```

thay vì bạn phải tự lưu method ở nơi khác.

---

# 4. URL

```python
request = httpx.Request(
    "GET",
    "https://example.com/search?q=python&page=2",
)

print(request.url)
```

Bạn có thể lấy:

```python
print(request.url.scheme)
print(request.url.host)
print(request.url.port)
print(request.url.path)
print(request.url.query)
```

Ví dụ URL:

```text
https://example.com:443/search?q=python&page=2
```

Có thể hình dung:

```text
https
  │
  └── scheme

example.com
  │
  └── host

443
  │
  └── port

/search
  │
  └── path

?q=python&page=2
  │
  └── query
```

---

# 5. URL trong HTTPX

HTTPX có object riêng:

```python
httpx.URL
```

Ví dụ:

```python
url = httpx.URL(
    "https://example.com/search?q=python"
)

print(url)
print(url.scheme)
print(url.host)
print(url.path)
print(url.query)
```

Điều này rất hữu ích khi xây dựng crawler hoặc API client.

---

# 6. Query Parameters

Đừng làm:

```python
url = (
    "https://example.com/search"
    "?q=python&page=2"
)
```

Thay vào đó:

```python
params = {
    "q": "python",
    "page": 2,
}

request = httpx.Request(
    "GET",
    "https://example.com/search",
    params=params,
)

print(request.url)
```

HTTPX sẽ tạo URL phù hợp.

---

# 7. Vì sao `params=` quan trọng?

Giả sử:

```python
params = {
    "q": "python httpx",
}
```

HTTPX sẽ encode:

```text
python httpx
```

thành dạng URL-safe.

Bạn không cần tự xử lý:

```text
space
&
?
=
%
```

Đây là một trong những lý do nên giao việc xây dựng URL cho HTTPX.

---

# 8. Headers

Request có headers:

```python
headers = {
    "User-Agent": "MyApp/1.0",
    "Accept": "application/json",
}

request = httpx.Request(
    "GET",
    "https://example.com",
    headers=headers,
)

print(request.headers)
```

Lấy một header:

```python
print(request.headers["user-agent"])
```

Hoặc:

```python
print(request.headers.get("user-agent"))
```

---

# 9. Headers không phân biệt hoa thường

Bạn viết:

```python
headers = {
    "User-Agent": "MyApp/1.0"
}
```

Sau đó:

```python
request.headers["user-agent"]
```

vẫn hoạt động.

HTTP headers về bản chất không phân biệt chữ hoa/chữ thường ở tên header.

---

# 10. Request Body

GET thường không có body.

POST có thể có body:

```python
request = httpx.Request(
    "POST",
    "https://example.com/api/users",
    content=b"hello",
)
```

Lấy body:

```python
print(request.content)
```

Kết quả:

```text
b'hello'
```

---

# 11. `content=`

Bạn có thể gửi bytes:

```python
response = httpx.post(
    "https://example.com",
    content=b"hello",
)
```

Hoặc string:

```python
response = httpx.post(
    "https://example.com",
    content="hello",
)
```

`content=` phù hợp khi bạn muốn kiểm soát trực tiếp HTTP body.

---

# 12. `data=`

Ví dụ form:

```python
data = {
    "username": "alice",
    "password": "123456",
}

response = httpx.post(
    "https://example.com/login",
    data=data,
)
```

Thông thường đây sẽ được dùng cho form URL-encoded.

---

# 13. `json=`

Khi API yêu cầu JSON:

```python
data = {
    "name": "Alice",
    "age": 25,
}

response = httpx.post(
    "https://example.com/users",
    json=data,
)
```

HTTPX sẽ xử lý việc serialize JSON cho bạn.

Bạn không cần:

```python
import json

json.dumps(data)
```

rồi tự tạo body.

---

# 14. `data=` vs `json=`

Đây là điểm phải nhớ.

### Form

```python
httpx.post(
    url,
    data={
        "username": "alice",
    },
)
```

### JSON

```python
httpx.post(
    url,
    json={
        "username": "alice",
    },
)
```

Tư duy:

```text
data=
    ↓
form-style data

json=
    ↓
application/json
```

---

# 15. Response là gì?

Sau khi gửi request:

```python
response = httpx.get(
    "https://example.com"
)
```

Bạn nhận:

```python
httpx.Response
```

Response đại diện cho:

> "Server đã trả lời request của tôi."

---

# 16. Các thành phần quan trọng của Response

```text
Response
│
├── status_code
├── headers
├── content
├── text
├── json()
├── url
├── request
└── history
```

---

# 17. Status Code

```python
response.status_code
```

Ví dụ:

```python
if response.status_code == 200:
    print("Success")
```

Nhưng trong code production, thường nên dùng:

```python
response.raise_for_status()
```

---

# 18. Response URL

```python
print(response.url)
```

Điều này đặc biệt hữu ích khi server redirect.

Ví dụ:

```text
Request URL
    ↓
http://example.com
    ↓
redirect
    ↓
https://example.com
```

`response.url` có thể cho bạn biết URL cuối cùng.

---

# 19. Response Headers

```python
print(response.headers)
```

Ví dụ:

```python
content_type = response.headers.get(
    "content-type"
)

print(content_type)
```

Bạn sẽ thường xuyên sử dụng:

```python
response.headers.get("content-type")
```

khi xử lý API/crawler.

---

# 20. Response Text

```python
html = response.text

print(html)
```

HTTPX sẽ decode response thành Python `str`.

---

# 21. Response Content

Nếu cần raw bytes:

```python
content = response.content

print(type(content))
```

Kết quả:

```text
<class 'bytes'>
```

Điều này quan trọng khi download:

```text
PDF
Image
ZIP
Audio
Video
```

Ví dụ:

```python
response = httpx.get(
    "https://example.com/file.pdf"
)

with open("file.pdf", "wb") as f:
    f.write(response.content)
```

---

# 22. Response JSON

API:

```python
response = httpx.get(
    "https://jsonplaceholder.typicode.com/users/1"
)
```

Parse:

```python
data = response.json()

print(data)
```

Sau đó:

```python
print(data["name"])
print(data["email"])
```

---

# 23. Response giữ Request gốc

Một điểm rất hay:

```python
response.request
```

Ví dụ:

```python
response = httpx.get(
    "https://example.com"
)

print(response.request)
```

Bạn có thể xem:

```python
print(response.request.method)
print(response.request.url)
print(response.request.headers)
```

Tức là:

```text
Response
   │
   └── request
          │
          ├── method
          ├── url
          └── headers
```

Điều này cực kỳ hữu ích khi debug.

---

# 24. Request → Response

Hãy nhớ mô hình:

```text
             HTTP
Python ──────────────────► Server
       Request

Python ◄────────────────── Server
       Response
```

Trong HTTPX:

```python
request = httpx.Request(...)

response = client.send(request)
```

Đây là một ý tưởng rất quan trọng.

Chúng ta không chỉ có:

```python
httpx.get()
```

mà còn có tầng thấp hơn:

```text
httpx.get()
    ↓
Client
    ↓
Request
    ↓
Transport
    ↓
Network
```

Sau này khi học architecture của HTTPX, bạn sẽ thấy thiết kế này rất mạnh.

---

# 25. `httpx.request()`

Thay vì:

```python
httpx.get(url)
```

có thể viết:

```python
httpx.request(
    "GET",
    url,
)
```

Hoặc:

```python
httpx.request(
    "POST",
    url,
    json={"name": "Alice"},
)
```

Điều này hữu ích khi method được xác định động:

```python
method = "GET"

response = httpx.request(
    method,
    url,
)
```

---

# 26. Tự tạo Request và gửi

Đây là bước quan trọng nhất của buổi hôm nay.

```python
import httpx

request = httpx.Request(
    "GET",
    "https://example.com",
)

with httpx.Client() as client:
    response = client.send(request)

print(response.status_code)
print(response.text)
```

So sánh:

### High-level

```python
response = httpx.get(url)
```

### Low-level

```python
request = httpx.Request(
    "GET",
    url,
)

response = client.send(request)
```

---

# 27. Tại sao cần biết `Request`?

Bởi vì khi xây dựng application lớn, bạn có thể muốn:

```text
Application
     │
     ▼
API Client
     │
     ▼
Create Request
     │
     ▼
Authentication
     │
     ▼
Retry
     │
     ▼
Logging
     │
     ▼
Send
     │
     ▼
Response
```

Thay vì rải khắp code:

```python
httpx.get(...)
httpx.post(...)
httpx.get(...)
httpx.post(...)
```

---

# 28. Một API Client nhỏ

Ví dụ:

```python
import httpx


class UserClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_user(self, user_id: int):
        url = f"{self.base_url}/users/{user_id}"

        response = httpx.get(url)

        response.raise_for_status()

        return response.json()
```

Sử dụng:

```python
client = UserClient(
    "https://jsonplaceholder.typicode.com"
)

user = client.get_user(1)

print(user["name"])
```

Đây mới chỉ là phiên bản đơn giản.

Ở **Buổi 4**, chúng ta sẽ refactor thành:

```text
UserClient
     │
     ▼
httpx.Client
```

để tận dụng connection pooling, default headers, cookies, base URL...

---

# 29. Một điều rất quan trọng: đừng tạo Client liên tục

Không nên:

```python
def get_user(user_id):
    with httpx.Client() as client:
        return client.get(...)
```

rồi gọi function hàng nghìn lần.

Ví dụ crawler:

```text
get page 1 → tạo connection
get page 2 → tạo connection
get page 3 → tạo connection
...
```

Sẽ rất lãng phí.

Tốt hơn:

```text
Client
  │
  ├── Request 1
  ├── Request 2
  ├── Request 3
  ├── Request 4
  └── Request 5
```

HTTPX có **connection pooling**.

Chúng ta sẽ học rất kỹ ở Buổi 4.

---

# 30. Bài tập Buổi 2

## Bài 1 — Request

Tạo một `httpx.Request`:

```text
GET
https://example.com/search
```

với:

```text
q=python
page=2
```

Sau đó in:

```text
method
url
query
headers
```

---

## Bài 2 — POST Request

Tạo request:

```text
POST
https://example.com/api/users
```

với JSON:

```python
{
    "name": "Alice",
    "age": 25
}
```

Không dùng `httpx.post()`.

Hãy sử dụng:

```python
httpx.Request(...)
```

---

## Bài 3 — Response

Gọi:

```text
https://jsonplaceholder.typicode.com/users/1
```

In:

```text
Status
URL
Content-Type
User-Agent request
Name
Email
```

---

## Bài 4 — Download

Dùng HTTPX download một file bất kỳ về máy.

Yêu cầu:

```text
response.content
→ mở file bằng "wb"
→ ghi bytes
```

---

## Bài 5 — Mini Project

Viết:

```text
UserAPIClient
```

có:

```python
get_user(user_id)
create_user(name, email)
```

Kiến trúc:

```text
UserAPIClient
      │
      ├── Request
      │
      ▼
    HTTPX
      │
      ▼
    Response
      │
      ├── status
      ├── headers
      └── json
```

**Mục tiêu của Buổi 2 không phải nhớ hết API của HTTPX**, mà phải hình thành được mô hình:

```text
Request
   │
   │ send
   ▼
HTTP Server
   │
   │ response
   ▼
Response
```

Sau khi nắm chắc mô hình này, **Buổi 3** chúng ta sẽ học toàn bộ HTTP Methods: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS`, đồng thời phân biệt rõ **`data=`, `json=`, `content=` và multipart upload**.
