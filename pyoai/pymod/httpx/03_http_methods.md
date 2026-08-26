# Buổi 3 — HTTP Methods với HTTPX

Buổi này chúng ta tập trung vào **HTTP Methods** và cách HTTPX biểu diễn chúng.

Mục tiêu:

```text
GET
POST
PUT
PATCH
DELETE
HEAD
OPTIONS
```

và đặc biệt hiểu:

```text
data=
json=
content=
files=
```

---

# 1. HTTP Method là gì?

Một HTTP Request có dạng khái quát:

```text
METHOD /path HTTP/1.1
Host: example.com
Content-Type: ...

<body>
```

Ví dụ:

```text
GET /users/10 HTTP/1.1
Host: example.com
```

Method cho server biết **client muốn thực hiện hành động gì**.

---

# 2. GET

GET thường dùng để **lấy dữ liệu**.

HTTPX:

```python
import httpx

response = httpx.get(
    "https://jsonplaceholder.typicode.com/users/1"
)

print(response.status_code)
print(response.json())
```

Hoặc:

```python
with httpx.Client() as client:
    response = client.get(
        "https://jsonplaceholder.typicode.com/users/1"
    )
```

---

# 3. GET với Query Parameters

Không nên:

```python
url = "https://example.com/search?q=python&page=2"
```

Nên:

```python
params = {
    "q": "python",
    "page": 2,
}

response = httpx.get(
    "https://example.com/search",
    params=params,
)
```

HTTPX tạo URL:

```text
https://example.com/search?q=python&page=2
```

---

# 4. GET thường không có Request Body

Thông thường:

```text
GET
 │
 ├── URL
 ├── Query params
 └── Headers
```

Ví dụ:

```python
response = httpx.get(
    url,
    params={"page": 2},
    headers={"Accept": "application/json"},
)
```

Khi cần truyền dữ liệu cho GET, **query parameters** thường là lựa chọn phù hợp.

---

# 5. POST

POST thường dùng để **tạo resource hoặc gửi dữ liệu để server xử lý**.

Ví dụ:

```python
data = {
    "name": "Alice",
    "email": "alice@example.com",
}

response = httpx.post(
    "https://example.com/users",
    json=data,
)
```

Request về mặt khái niệm:

```text
POST /users HTTP/1.1
Content-Type: application/json

{
    "name": "Alice",
    "email": "alice@example.com"
}
```

---

# 6. POST với `json=`

Đây là cách rất phổ biến khi làm REST API:

```python
payload = {
    "title": "Hello",
    "body": "Python HTTPX",
}

response = httpx.post(
    url,
    json=payload,
)
```

HTTPX sẽ serialize dictionary thành JSON.

Bạn không cần:

```python
import json

body = json.dumps(payload)
```

---

# 7. POST với `data=`

`data=` thường dùng cho form data.

```python
form = {
    "username": "alice",
    "password": "secret",
}

response = httpx.post(
    url,
    data=form,
)
```

Khác với:

```python
json=form
```

Hãy nhớ:

```text
data=
   ↓
form-style request

json=
   ↓
JSON request
```

---

# 8. `content=` — raw body

Khi bạn muốn gửi trực tiếp bytes hoặc text:

```python
response = httpx.post(
    url,
    content=b"hello world",
)
```

Hoặc:

```python
response = httpx.post(
    url,
    content="hello world",
)
```

`content=` phù hợp khi bạn **muốn kiểm soát raw HTTP body**.

---

# 9. So sánh `data`, `json`, `content`

Đây là phần cực kỳ quan trọng:

| Argument   | Mục đích         |
| ---------- | ---------------- |
| `params=`  | Query string     |
| `data=`    | Form/body data   |
| `json=`    | JSON body        |
| `content=` | Raw body         |
| `files=`   | Multipart upload |

Ví dụ:

```python
httpx.post(
    url,
    params={"page": 1},
    json={"name": "Alice"},
)
```

Có thể hiểu:

```text
URL:
    ?page=1

BODY:
    {"name": "Alice"}
```

---

# 10. PUT

PUT thường được sử dụng để **thay thế/cập nhật resource**.

Ví dụ:

```python
user = {
    "name": "Alice",
    "email": "alice@example.com",
}

response = httpx.put(
    "https://example.com/users/1",
    json=user,
)
```

Concept:

```text
PUT /users/1
```

Nghĩa gần như:

```text
"Đây là representation mới của resource /users/1"
```

---

# 11. PUT vs POST

Ví dụ:

```text
POST /users
```

Thường có nghĩa:

```text
"Tạo một user mới"
```

Trong khi:

```text
PUT /users/10
```

thường có nghĩa:

```text
"Đặt/cập nhật user có ID = 10"
```

Tư duy:

```text
POST
/users
   ↓
server quyết định ID


PUT
/users/10
   ↓
client xác định resource
```

---

# 12. PATCH

PATCH dùng cho **partial update**.

Ví dụ user:

```json
{
    "name": "Alice",
    "email": "alice@example.com",
    "age": 25
}
```

Bạn chỉ muốn đổi `name`.

Không nhất thiết gửi toàn bộ object.

```python
response = httpx.patch(
    "https://example.com/users/10",
    json={
        "name": "Bob",
    },
)
```

Concept:

```text
PATCH /users/10

{
    "name": "Bob"
}
```

---

# 13. PUT vs PATCH

Đây là điểm rất hay bị nhầm.

### PUT

```text
Replace / update representation
```

Ví dụ:

```python
httpx.put(
    "/users/10",
    json={
        "name": "Bob",
        "email": "bob@example.com",
        "age": 30,
    },
)
```

### PATCH

```text
Partial modification
```

```python
httpx.patch(
    "/users/10",
    json={
        "name": "Bob",
    },
)
```

Tư duy:

```text
PUT
    Resource mới

PATCH
    Một phần thay đổi
```

---

# 14. DELETE

DELETE dùng để xóa resource.

```python
response = httpx.delete(
    "https://example.com/users/10"
)

print(response.status_code)
```

Ví dụ:

```text
DELETE /users/10
```

---

# 15. DELETE có body không?

HTTP specification không cấm tuyệt đối body trong DELETE, nhưng API thực tế thường không yêu cầu body.

Thông thường:

```python
httpx.delete(
    "/users/10"
)
```

là đủ.

---

# 16. HEAD

HEAD tương tự GET nhưng client yêu cầu **headers mà không cần response body**.

```python
response = httpx.head(
    "https://example.com"
)

print(response.status_code)
print(response.headers)
```

Có thể dùng để kiểm tra:

```text
Content-Length
Content-Type
Last-Modified
ETag
```

mà không cần tải toàn bộ nội dung.

---

# 17. Khi nào HEAD hữu ích?

Ví dụ crawler muốn kiểm tra file:

```text
https://example.com/book.pdf
```

Trước khi download, có thể kiểm tra:

```text
Content-Type
Content-Length
```

Nếu:

```text
Content-Type: application/pdf
Content-Length: 50 MB
```

bạn biết trước file lớn đến mức nào.

---

# 18. OPTIONS

OPTIONS dùng để hỏi server:

> Server hỗ trợ những HTTP methods/options nào?

HTTPX:

```python
response = httpx.options(
    "https://example.com"
)

print(response.status_code)
print(response.headers)
```

Một header thường gặp:

```text
Allow: GET, POST, PUT, DELETE
```

OPTIONS cũng có vai trò quan trọng trong **CORS / preflight request** ở web.

---

# 19. HTTPX có API cho tất cả Methods

HTTPX cung cấp:

```python
httpx.get()
httpx.post()
httpx.put()
httpx.patch()
httpx.delete()
httpx.head()
httpx.options()
```

Ngoài ra có:

```python
httpx.request()
```

Ví dụ:

```python
method = "PATCH"

response = httpx.request(
    method,
    url,
    json={"name": "Bob"},
)
```

Điều này hữu ích khi method đến từ configuration:

```python
method = config.method
```

---

# 20. `client.request()`

Với `Client` cũng tương tự:

```python
with httpx.Client() as client:
    response = client.request(
        "GET",
        "https://example.com",
    )
```

Hoặc:

```python
with httpx.Client() as client:
    response = client.request(
        "POST",
        "https://example.com/users",
        json={
            "name": "Alice",
        },
    )
```

---

# 21. Multipart File Upload

Đây là phần rất quan trọng trong HTTP client.

Giả sử server yêu cầu:

```text
multipart/form-data
```

HTTPX hỗ trợ:

```python
with open("avatar.jpg", "rb") as file:
    response = httpx.post(
        url,
        files={
            "avatar": file,
        },
    )
```

HTTPX sẽ xây dựng multipart request.

---

# 22. File + Form Fields

Có thể gửi cả field và file:

```python
data = {
    "username": "alice",
}

with open("avatar.jpg", "rb") as file:
    response = httpx.post(
        url,
        data=data,
        files={
            "avatar": file,
        },
    )
```

Concept:

```text
multipart/form-data
│
├── username = alice
│
└── avatar = avatar.jpg
```

Đây là pattern bạn sẽ gặp rất nhiều khi làm API client.

---

# 23. Upload với tuple

HTTPX còn cho phép kiểm soát metadata của file:

```python
files = {
    "avatar": (
        "avatar.jpg",
        open("avatar.jpg", "rb"),
        "image/jpeg",
    ),
}
```

Cấu trúc:

```text
(
    filename,
    file object,
    content type,
)
```

Ví dụ:

```python
with open("avatar.jpg", "rb") as file:
    files = {
        "avatar": (
            "avatar.jpg",
            file,
            "image/jpeg",
        )
    }

    response = httpx.post(
        url,
        files=files,
    )
```

---

# 24. Đừng nhầm `files=` với `content=`

### Raw file

```python
with open("data.bin", "rb") as f:
    response = httpx.post(
        url,
        content=f.read(),
    )
```

Server nhận raw bytes.

### Multipart

```python
with open("data.bin", "rb") as f:
    response = httpx.post(
        url,
        files={"file": f},
    )
```

Server nhận:

```text
multipart/form-data
```

Đây là **hai protocol-level behavior khác nhau**.

---

# 25. Một REST API Client

Bây giờ ghép các method lại:

```python
import httpx


class UserClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get(self, user_id: int):
        return httpx.get(
            f"{self.base_url}/users/{user_id}"
        )

    def create(self, name: str, email: str):
        return httpx.post(
            f"{self.base_url}/users",
            json={
                "name": name,
                "email": email,
            },
        )

    def update(self, user_id: int, name: str):
        return httpx.put(
            f"{self.base_url}/users/{user_id}",
            json={
                "name": name,
            },
        )

    def patch(self, user_id: int, name: str):
        return httpx.patch(
            f"{self.base_url}/users/{user_id}",
            json={
                "name": name,
            },
        )

    def delete(self, user_id: int):
        return httpx.delete(
            f"{self.base_url}/users/{user_id}"
        )
```

Đây là API client rất đơn giản.

Nhưng có một vấn đề lớn:

```text
Mỗi method
    ↓
tạo request độc lập
    ↓
không tận dụng tốt connection pooling
```

Đó chính là vấn đề chúng ta sẽ giải quyết ở **Buổi 4 — `httpx.Client`**.

---

# 26. Tư duy HTTPX cần hình thành

Bạn nên nhìn API của HTTPX như sau:

```text
                    HTTPX
                      │
          ┌───────────┴───────────┐
          │                       │
       Request                 Response
          │                       │
    ┌─────┼─────┐           ┌─────┼─────┐
    │     │     │           │     │     │
 method  URL headers       status headers body
          │                       │
          └────── HTTP ───────────┘
```

Và body:

```text
Request Body
│
├── json=
├── data=
├── content=
└── files=
```

---

# 27. Bảng tổng kết

| Method  | Mục đích thường gặp     |
| ------- | ----------------------- |
| GET     | Lấy resource            |
| POST    | Tạo/gửi dữ liệu         |
| PUT     | Replace/update resource |
| PATCH   | Partial update          |
| DELETE  | Xóa resource            |
| HEAD    | Lấy headers             |
| OPTIONS | Hỏi capabilities        |

Và:

| HTTPX      | Sử dụng          |
| ---------- | ---------------- |
| `params=`  | Query string     |
| `headers=` | HTTP headers     |
| `json=`    | JSON body        |
| `data=`    | Form/body data   |
| `content=` | Raw body         |
| `files=`   | Multipart upload |

---

# Bài tập Buổi 3

### Bài 1

Viết 7 request tương ứng:

```text
GET
POST
PUT
PATCH
DELETE
HEAD
OPTIONS
```

và xác định method của từng `Response` thông qua:

```python
response.request.method
```

---

### Bài 2

Tạo POST request gửi:

```python
{
    "name": "Alice",
    "age": 25
}
```

theo **3 cách**:

```text
json=
data=
content=
```

Sau đó giải thích sự khác nhau giữa chúng.

---

### Bài 3

Viết function:

```python
def create_user(name: str, email: str):
    ...
```

sử dụng:

```text
POST
JSON
raise_for_status()
response.json()
```

---

### Bài 4

Viết:

```python
def update_user(user_id: int, name: str):
    ...
```

sử dụng `PATCH`.

---

### Bài 5 — File Upload

Viết function:

```python
def upload_file(path: str):
    ...
```

sử dụng:

```python
files=
```

và in:

```text
status code
response headers
response body
```

---

### Bài 6 — Mini REST Client

Thiết kế:

```text
UserClient
│
├── get_user()
├── create_user()
├── update_user()
├── patch_user()
└── delete_user()
```

Chưa cần tối ưu architecture.

Mục tiêu là bạn phải **tự nhiên chuyển từ HTTP operation → HTTPX method → Request → Response**.

---

## Chuỗi kiến thức đến đây

```text
Buổi 1
HTTPX Foundation
     │
     ▼
Buổi 2
Request / Response
     │
     ▼
Buổi 3
HTTP Methods + Body
     │
     ▼
Buổi 4
httpx.Client
     │
     ├── Connection Pool
     ├── Default Headers
     ├── Cookies
     ├── Base URL
     └── Client Lifecycle
```

**Buổi 4 là một bước rất quan trọng**: chúng ta sẽ bỏ cách dùng `httpx.get()`/`httpx.post()` độc lập và học `httpx.Client` như một **long-lived HTTP client**, từ đó bắt đầu tiến gần đến cách xây dựng HTTP client production thực tế.
