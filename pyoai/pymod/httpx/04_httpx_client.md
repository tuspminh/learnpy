# Buổi 4 — `httpx.Client`: HTTP Client thực thụ

Từ Buổi 1–3, chúng ta chủ yếu dùng:

```python
httpx.get(...)
httpx.post(...)
httpx.put(...)
```

Cách này phù hợp với request đơn giản.

Nhưng khi xây dựng:

* REST API Client
* Web Crawler
* Scraper
* Authentication client
* Service gọi API nhiều lần

thì chúng ta cần:

```python
httpx.Client
```

Đây là một trong những phần **quan trọng nhất của HTTPX**.

---

# 1. Vấn đề của `httpx.get()`

Giả sử crawler cần lấy 1.000 URL:

```python
for url in urls:
    response = httpx.get(url)
```

Về mặt thiết kế, mỗi request độc lập với nhau.

Ta không có một object đại diện cho:

> "Phiên làm việc HTTP của ứng dụng này."

Trong khi một HTTP client thực tế thường cần duy trì:

```text
Client
 │
 ├── Headers mặc định
 ├── Cookies
 ├── Authentication
 ├── Connection pool
 ├── Base URL
 └── Configuration
```

Đó chính là nhiệm vụ của `httpx.Client`.

---

# 2. Tạo Client

Cách cơ bản:

```python
import httpx

client = httpx.Client()

response = client.get(
    "https://example.com"
)

print(response.status_code)

client.close()
```

Ta có:

```text
Client
  │
  └── GET
       ↓
    Response
```

---

# 3. Dùng Context Manager

Cách nên dùng:

```python
import httpx

with httpx.Client() as client:
    response = client.get(
        "https://example.com"
    )

    print(response.status_code)
```

Khi ra khỏi:

```python
with
```

HTTPX sẽ đóng Client.

Tư duy:

```text
with Client()
      │
      ├── request 1
      ├── request 2
      ├── request 3
      └── request 4
      │
      ▼
    close()
```

---

# 4. Tại sao phải `close()`?

Client quản lý các resource liên quan đến network.

Nếu bạn tạo:

```python
client = httpx.Client()
```

thì cuối lifecycle nên:

```python
client.close()
```

Hoặc:

```python
with httpx.Client() as client:
    ...
```

`with` là cách an toàn hơn.

---

# 5. Client có thể thực hiện mọi HTTP method

```python
with httpx.Client() as client:

    response = client.get(url)

    response = client.post(
        url,
        json=data,
    )

    response = client.put(
        url,
        json=data,
    )

    response = client.patch(
        url,
        json=data,
    )

    response = client.delete(url)
```

API rất giống:

```python
httpx.get()
httpx.post()
```

nhưng Client có thêm **state và connection management**.

---

# 6. Connection Pooling

Đây là lý do lớn nhất để sử dụng `Client`.

Giả sử:

```text
Request 1 → example.com
Request 2 → example.com
Request 3 → example.com
Request 4 → example.com
```

Nếu mỗi request phải tạo connection mới:

```text
TCP connection
     ↓
TLS handshake
     ↓
HTTP request
     ↓
HTTP response
     ↓
close
```

sẽ tốn chi phí.

Client có thể giữ và tái sử dụng connection:

```text
Client
 │
 └── Connection Pool
       │
       ├── Connection A
       ├── Connection B
       └── Connection C
```

Request tiếp theo có thể sử dụng connection đã tồn tại.

Đây gọi là:

> **Connection pooling**

---

# 7. Ví dụ crawler

Không nên:

```python
for url in urls:
    response = httpx.get(url)
```

Nên:

```python
with httpx.Client() as client:
    for url in urls:
        response = client.get(url)
```

Bây giờ tất cả request đi qua cùng một Client.

```text
Client
 │
 ├── GET url1
 ├── GET url2
 ├── GET url3
 ├── GET url4
 └── GET url5
```

Đây là pattern rất quan trọng trong crawler.

---

# 8. Default Headers

Client cho phép cấu hình headers mặc định.

```python
headers = {
    "User-Agent": "MyCrawler/1.0",
    "Accept": "application/json",
}

with httpx.Client(
    headers=headers
) as client:

    response = client.get(url)
```

Bây giờ mọi request sử dụng Client đều có các headers này.

---

# 9. So sánh

Không dùng Client:

```python
httpx.get(
    url,
    headers={
        "User-Agent": "MyCrawler/1.0"
    }
)
```

Request tiếp theo:

```python
httpx.get(
    url2,
    headers={
        "User-Agent": "MyCrawler/1.0"
    }
)
```

Rất lặp code.

Với Client:

```python
with httpx.Client(
    headers={
        "User-Agent": "MyCrawler/1.0"
    }
) as client:

    client.get(url1)
    client.get(url2)
    client.get(url3)
```

Đây chính là **configuration at client level**.

---

# 10. Request có thể override Client headers

Ví dụ:

```python
with httpx.Client(
    headers={
        "User-Agent": "MyCrawler/1.0",
        "Accept": "application/json",
    }
) as client:

    response = client.get(
        url,
        headers={
            "Accept": "text/html",
        },
    )
```

Client có default:

```text
Accept: application/json
```

Request có:

```text
Accept: text/html
```

Request-specific configuration có thể điều chỉnh configuration mặc định.

Tư duy:

```text
Client defaults
       │
       ▼
Request-specific settings
       │
       ▼
Final Request
```

---

# 11. Default Query Parameters

Client cũng có thể cấu hình params mặc định.

```python
with httpx.Client(
    params={
        "api_key": "abc123",
    }
) as client:

    response = client.get(
        "https://example.com/users"
    )
```

Request sẽ có:

```text
?api_key=abc123
```

Điều này rất hữu ích với API yêu cầu một parameter chung.

---

# 12. Base URL

Đây là tính năng cực kỳ hữu ích khi xây REST API Client.

Thay vì:

```python
client.get(
    "https://api.example.com/users"
)

client.get(
    "https://api.example.com/posts"
)
```

có thể:

```python
with httpx.Client(
    base_url="https://api.example.com"
) as client:

    client.get("/users")
    client.get("/posts")
```

Tư duy:

```text
base_url
    │
    ▼
https://api.example.com
    │
    ├── /users
    ├── /posts
    └── /articles
```

---

# 13. Base URL trong API Client

Ví dụ:

```python
class UserClient:

    def __init__(self):
        self.client = httpx.Client(
            base_url="https://api.example.com"
        )

    def get_user(self, user_id):
        return self.client.get(
            f"/users/{user_id}"
        )
```

Sử dụng:

```python
client = UserClient()

response = client.get_user(10)
```

HTTPX sẽ request đến:

```text
https://api.example.com/users/10
```

---

# 14. Nhưng Client phải được đóng

Class phía trên còn một vấn đề:

```python
client = UserClient()
```

phải đảm bảo:

```python
self.client.close()
```

Một thiết kế tốt hơn:

```python
class UserClient:

    def __init__(self):
        self.client = httpx.Client(
            base_url="https://api.example.com"
        )

    def close(self):
        self.client.close()
```

Sử dụng:

```python
client = UserClient()

try:
    response = client.get_user(10)
finally:
    client.close()
```

Hoặc sau này ta sẽ thiết kế context manager.

---

# 15. Cookies

Client có thể duy trì cookies.

```python
with httpx.Client() as client:

    response = client.get(
        "https://example.com"
    )

    print(client.cookies)
```

Nếu server trả:

```text
Set-Cookie: session=abc123
```

cookie có thể được lưu trong Client.

Request sau có thể gửi cookie phù hợp.

Tư duy:

```text
Request 1
   │
   ▼
Server
   │
   └── Set-Cookie
          │
          ▼
       Client
          │
          ▼
Request 2
   │
   └── Cookie
```

Đây là lý do Client giống một **HTTP session**.

---

# 16. Khởi tạo Cookie

Bạn cũng có thể cấu hình:

```python
cookies = {
    "session": "abc123",
}

with httpx.Client(
    cookies=cookies
) as client:

    response = client.get(url)
```

---

# 17. Authentication

Client cũng rất phù hợp để cấu hình authentication.

Ví dụ Basic Auth:

```python
with httpx.Client(
    auth=("alice", "secret")
) as client:

    response = client.get(
        "https://example.com/private"
    )
```

Tất cả request qua Client có thể sử dụng authentication này.

Sau này chúng ta sẽ có riêng một buổi về Authentication.

---

# 18. Default Timeout

Client có thể cấu hình timeout:

```python
timeout = httpx.Timeout(10.0)

with httpx.Client(
    timeout=timeout
) as client:

    response = client.get(url)
```

Sau này chúng ta sẽ học timeout rất sâu.

---

# 19. Client là một Object có State

Đây là điểm quan trọng nhất về mặt kiến trúc.

`httpx.get()`:

```text
stateless-ish request
```

Trong khi:

```python
client = httpx.Client()
```

là một object giữ configuration/state:

```text
Client
│
├── base_url
├── headers
├── params
├── cookies
├── auth
├── timeout
├── transport
└── connection pool
```

Vì vậy:

```text
httpx.get()
```

phù hợp:

```text
Request đơn lẻ
```

Còn:

```text
httpx.Client
```

phù hợp:

```text
Application / Service / Crawler / API Client
```

---

# 20. Một API Client tốt hơn

Bây giờ refactor `UserClient`.

```python
import httpx


class UserClient:

    def __init__(self, base_url: str):
        self.client = httpx.Client(
            base_url=base_url,
            headers={
                "Accept": "application/json",
            },
        )

    def get_user(self, user_id: int):
        response = self.client.get(
            f"/users/{user_id}"
        )

        response.raise_for_status()

        return response.json()

    def close(self):
        self.client.close()
```

Sử dụng:

```python
client = UserClient(
    "https://jsonplaceholder.typicode.com"
)

try:
    user = client.get_user(1)
    print(user)
finally:
    client.close()
```

---

# 21. Dùng Context Manager cho API Client

Ta có thể làm API client hỗ trợ:

```python
with UserClient(...) as client:
    user = client.get_user(1)
```

Code:

```python
import httpx


class UserClient:

    def __init__(self, base_url: str):
        self.client = httpx.Client(
            base_url=base_url
        )

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.client.close()

    def get_user(self, user_id: int):
        response = self.client.get(
            f"/users/{user_id}"
        )

        response.raise_for_status()

        return response.json()
```

Sử dụng:

```python
with UserClient(
    "https://jsonplaceholder.typicode.com"
) as client:

    user = client.get_user(1)

    print(user["name"])
```

Đây là thiết kế sạch hơn.

---

# 22. `Client` và Dependency Injection

Sau này khi học Clean Architecture/DDD, bạn sẽ gặp pattern:

```text
Application
    │
    ▼
UserService
    │
    ▼
UserAPIClient
    │
    ▼
httpx.Client
```

Thay vì UserService tự tạo HTTP client:

```python
class UserService:

    def __init__(self):
        self.client = httpx.Client()
```

ta có thể inject:

```python
class UserService:

    def __init__(self, client):
        self.client = client
```

Ví dụ:

```python
http_client = httpx.Client(
    base_url="https://api.example.com"
)

service = UserService(
    client=http_client
)
```

Điều này cực kỳ hữu ích khi testing.

Chúng ta sẽ quay lại vấn đề này ở phần **Testing + MockTransport**.

---

# 23. Client Lifecycle

Bạn cần hình thành tư duy:

```text
Create Client
      │
      ▼
Configure Client
      │
      ▼
Use Client
      │
      ├── Request 1
      ├── Request 2
      ├── Request 3
      └── Request N
      │
      ▼
Close Client
```

Đừng coi `Client` đơn giản chỉ là:

```python
client.get(...)
```

Nó là **một resource có lifecycle**.

---

# 24. Pattern nên dùng

### Request đơn lẻ

```python
response = httpx.get(url)
```

### Nhiều request

```python
with httpx.Client() as client:
    for url in urls:
        response = client.get(url)
```

### API Client

```python
class APIClient:

    def __init__(self):
        self.client = httpx.Client(...)
```

### Application lớn

```text
Application
     │
     ▼
Service
     │
     ▼
API Client
     │
     ▼
httpx.Client
```

---

# 25. `Client` vs `httpx.get()`

|                     | `httpx.get()`                       | `httpx.Client` |
| ------------------- | ----------------------------------- | -------------- |
| Request đơn         | ✅                                   | ✅              |
| Nhiều request       | ⚠️                                  | ✅              |
| Connection pooling  | Không tận dụng client-level pooling | ✅              |
| Default headers     | ❌                                   | ✅              |
| Default params      | ❌                                   | ✅              |
| Cookies             | ❌                                   | ✅              |
| Base URL            | ❌                                   | ✅              |
| Auth cấu hình chung | ❌                                   | ✅              |
| Lifecycle           | đơn request                         | rõ ràng        |
| API Client          | Không phù hợp                       | ✅              |
| Crawler             | Không tối ưu                        | ✅              |

---

# 26. Bài tập Buổi 4

## Bài 1 — Client cơ bản

Viết:

```python
with httpx.Client() as client:
    ...
```

và gửi 5 request đến:

```text
https://example.com
```

In:

```text
status
url
```

---

## Bài 2 — Default Headers

Tạo Client với:

```text
User-Agent: MyCrawler/1.0
Accept: application/json
```

Sau đó gửi request.

Kiểm tra:

```python
response.request.headers
```

để xác nhận headers đã được gửi.

---

## Bài 3 — Base URL

Tạo:

```python
client = httpx.Client(
    base_url="https://jsonplaceholder.typicode.com"
)
```

Sau đó gọi:

```text
/users/1
/users/2
/users/3
```

mà **không lặp lại domain**.

---

## Bài 4 — Cookies

Tạo Client với:

```python
cookies={
    "session": "abc123"
}
```

Gửi request và kiểm tra:

```python
response.request.headers
```

---

## Bài 5 — API Client

Thiết kế:

```text
UserAPIClient
│
├── get_user()
├── create_user()
├── update_user()
└── delete_user()
```

Nhưng lần này:

**chỉ được sử dụng một `httpx.Client` duy nhất.**

---

# 27. Bài tập quan trọng nhất

Viết:

```python
class APIClient:
    ...
```

có:

```python
with APIClient(...) as client:
    client.get(...)
    client.post(...)
```

Yêu cầu:

```text
1. Có httpx.Client
2. Có base_url
3. Có default headers
4. Có timeout
5. Có close()
6. Hỗ trợ with
7. get()
8. post()
```

Kiến trúc:

```text
              APIClient
                  │
          ┌───────┴────────┐
          │                │
      Configuration      Lifecycle
          │                │
     ┌────┼────┐       __enter__
     │    │    │       __exit__
   URL Headers Timeout
          │
          ▼
     httpx.Client
          │
          ▼
    Connection Pool
          │
          ▼
       Server
```

Đây chính là nền móng để từ buổi sau chúng ta bắt đầu xây dựng **HTTP Client có kiến trúc tốt**, thay vì chỉ gọi HTTPX như một utility function.

### Roadmap tiếp theo

```text
Buổi 1  HTTPX Foundation
   ↓
Buổi 2  Request / Response
   ↓
Buổi 3  HTTP Methods
   ↓
Buổi 4  httpx.Client ← hiện tại
   ↓
Buổi 5  Timeout
   ↓
Buổi 6  Query Parameters Deep Dive
   ↓
Buổi 7  Headers Deep Dive
   ↓
Buổi 8  Cookies
   ↓
Buổi 9  Form Data
   ↓
Buổi 10 Multipart / File Upload
```

**Điểm cần nhớ nhất của Buổi 4:** `httpx.Client` không chỉ là một cách viết khác của `httpx.get()`. Nó là **long-lived HTTP client**, quản lý configuration và connection pooling, và là thành phần nên nằm ở trung tâm khi bạn xây dựng API client hoặc crawler thực tế.
