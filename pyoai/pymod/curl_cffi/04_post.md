# Buổi 4 — POST, `data`, `json` và Request Body với `curl_cffi`

Ở Buổi 2 ta học:

```text
GET
 ├── URL
 ├── params
 └── headers
```

Hôm nay đi thêm một tầng:

```text
HTTP Request
│
├── Method
│   ├── GET
│   └── POST
│
├── URL
│
├── Query String
│   └── params
│
├── Headers
│
└── Body
    ├── data
    ├── json
    └── files
```

Điểm quan trọng nhất của Buổi 4:

> **`params` nằm trên URL; `data` và `json` nằm trong request body.**

---

# 1. POST cơ bản

Với `curl_cffi`, POST rất đơn giản:

```python
from curl_cffi import requests


response = requests.post(
    "https://httpbin.org/post",
)

print(response.status_code)
print(response.text)
```

Ta gửi:

```text
POST /post
```

thay vì:

```text
GET /post
```

---

# 2. GET vs POST

Ví dụ GET:

```python
response = requests.get(
    "https://httpbin.org/get"
)
```

POST:

```python
response = requests.post(
    "https://httpbin.org/post"
)
```

Mental model:

```text
GET
    URL
     ↓
    Server


POST
    URL
     +
    Body
     ↓
    Server
```

---

# 3. `params` vẫn dùng được với POST

Đây là điểm rất dễ nhầm.

Ta có thể:

```python
response = requests.post(
    "https://httpbin.org/post",
    params={
        "page": 2,
    },
)
```

Request về mặt logic:

```text
POST /post?page=2
```

`params` **không phải request body**.

---

# 4. `data` — form/body data

Ví dụ:

```python
response = requests.post(
    "https://httpbin.org/post",
    data={
        "username": "python",
        "password": "123456",
    },
)
```

Server có thể nhận form data:

```text
username=python
password=123456
```

Đây là kiểu request rất phổ biến với các form HTML truyền thống.

---

# 5. Xem server nhận được gì

Dùng `httpbin` để quan sát:

```python
from curl_cffi import requests


response = requests.post(
    "https://httpbin.org/post",
    data={
        "username": "python",
        "password": "123456",
    },
)

print(response.json())
```

Bạn có thể thấy server phân tích request thành các phần như:

```text
form
headers
args
data
url
```

Đây là cách rất tốt để học HTTP client:

```text
Python code
    ↓
HTTP request
    ↓
httpbin
    ↓
inspect request
```

---

# 6. `data` và HTML Form

Giả sử website có:

```html
<form method="POST">
    <input name="username">
    <input name="password">
</form>
```

Ta có thể gửi:

```python
response = requests.post(
    url,
    data={
        "username": "alice",
        "password": "secret",
    },
)
```

Mental model:

```text
HTML Form
    ↓
name=value
    ↓
data={}
    ↓
POST
```

---

# 7. `json` — JSON request body

API hiện đại thường không dùng form encoding mà dùng JSON.

Ví dụ:

```python
response = requests.post(
    "https://httpbin.org/post",
    json={
        "title": "Python",
        "page": 1,
    },
)
```

Request body về logic:

```json
{
    "title": "Python",
    "page": 1
}
```

Đây là điểm khác với:

```python
data={
    "title": "Python",
    "page": 1,
}
```

---

# 8. `data` vs `json`

Cần phân biệt rất rõ:

```python
data={
    "name": "python",
}
```

và:

```python
json={
    "name": "python",
}
```

Chúng biểu diễn **hai kiểu request body khác nhau**.

Mental model:

```text
data
 ↓
form/body encoding


json
 ↓
JSON body
```

Với API JSON:

```python
response = requests.post(
    url,
    json={
        "name": "python",
    },
)
```

thường rõ ràng hơn việc tự:

```python
import json

response = requests.post(
    url,
    data=json.dumps({
        "name": "python",
    }),
)
```

---

# 9. Không cần tự `json.dumps()`

Không nên làm:

```python
import json

payload = {
    "name": "python",
}

response = requests.post(
    url,
    data=json.dumps(payload),
)
```

nếu mục tiêu của bạn đơn giản chỉ là gửi JSON.

Dùng:

```python
response = requests.post(
    url,
    json=payload,
)
```

Code rõ ràng hơn.

---

# 10. Kiểm tra Content-Type

Khi gửi JSON:

```python
response = requests.post(
    "https://httpbin.org/post",
    json={
        "name": "python",
    },
)
```

HTTP request cần biểu diễn rằng body là JSON.

Đây chính là vai trò của:

```text
Content-Type
```

Mental model:

```text
json={}
   ↓
JSON request body
   +
Content-Type phù hợp
```

Bạn có thể tự kiểm tra request server nhận được bằng:

```python
print(response.json())
```

---

# 11. `data` với string

`data` không chỉ nhận dictionary.

Ví dụ:

```python
response = requests.post(
    "https://httpbin.org/post",
    data="hello world",
)
```

Ở đây body là raw data:

```text
hello world
```

Có thể tự chỉ định Content-Type:

```python
response = requests.post(
    "https://httpbin.org/post",
    data="hello world",
    headers={
        "Content-Type": "text/plain",
    },
)
```

---

# 12. `content-type` rất quan trọng

Một request có thể có:

```text
Content-Type: application/json
```

hoặc:

```text
Content-Type: application/x-www-form-urlencoded
```

hoặc:

```text
Content-Type: multipart/form-data
```

hoặc:

```text
Content-Type: text/plain
```

Nhìn vào `Content-Type`, server biết cách diễn giải body.

---

# 13. POST + params + json

Ba tầng có thể cùng tồn tại:

```python
response = requests.post(
    "https://httpbin.org/post",

    params={
        "source": "crawler",
    },

    json={
        "title": "Python",
        "page": 1,
    },
)
```

Mental model:

```text
POST
│
├── URL
│   └── ?source=crawler
│
└── Body
    └── JSON
        {
            "title": "Python",
            "page": 1
        }
```

Đây là một mental model rất quan trọng.

---

# 14. POST + headers

Ta có thể kết hợp:

```python
response = requests.post(
    "https://httpbin.org/post",
    headers={
        "User-Agent": "MyNovelCrawler/1.0",
        "Accept": "application/json",
    },
    json={
        "title": "Python",
    },
    timeout=10,
)
```

Request lúc này có:

```text
URL
Query
Headers
Body
Timeout
```

---

# 15. POST Form hoàn chỉnh

```python
from curl_cffi import requests


def main():
    response = requests.post(
        "https://httpbin.org/post",
        data={
            "username": "alice",
            "password": "secret",
        },
        headers={
            "User-Agent": "MyNovelCrawler/1.0",
        },
        timeout=10,
    )

    response.raise_for_status()

    print(response.status_code)
    print(response.json())


if __name__ == "__main__":
    main()
```

---

# 16. POST JSON hoàn chỉnh

```python
from curl_cffi import requests


def main():
    payload = {
        "title": "Python",
        "author": "Guido",
        "page": 1,
    }

    response = requests.post(
        "https://httpbin.org/post",
        json=payload,
        headers={
            "User-Agent": "MyNovelCrawler/1.0",
        },
        timeout=10,
    )

    response.raise_for_status()

    result = response.json()

    print("Status:", response.status_code)
    print("JSON:", result)


if __name__ == "__main__":
    main()
```

---

# 17. Upload file — `files`

`curl_cffi` cũng hỗ trợ multipart form.

Ví dụ:

```python
from curl_cffi import requests


with open("example.txt", "rb") as f:
    response = requests.post(
        "https://httpbin.org/post",
        files={
            "file": f,
        },
    )

print(response.status_code)
print(response.json())
```

Mental model:

```text
POST
 ↓
multipart/form-data
 ├── field
 ├── field
 └── file
```

Phần upload file sẽ được học kỹ hơn sau.

---

# 18. Form + file

Có thể kết hợp:

```python
with open("example.txt", "rb") as f:
    response = requests.post(
        "https://httpbin.org/post",
        data={
            "title": "Novel",
        },
        files={
            "file": f,
        },
    )
```

Đây là kiểu request thường gặp trong web application.

---

# 19. `POST` không có nghĩa là "an toàn"

Một hiểu nhầm phổ biến:

```text
GET  → không an toàn
POST → an toàn
```

Không chính xác.

HTTP method không tự đảm bảo:

* encryption
* authentication
* authorization
* privacy

Nếu dùng HTTPS:

```text
https://
```

thì TLS mới là thành phần mã hóa kết nối.

---

# 20. Liên hệ với Novel Crawler

Crawler truyện của bạn chủ yếu sẽ:

```text
GET
 ↓
Listing page
 ↓
Novel detail
 ↓
Chapter page
 ↓
Image
```

Nên `POST` có thể không phải thành phần chính.

Tuy nhiên, vẫn cần biết POST vì website có thể sử dụng:

```text
POST /api/search
POST /ajax/chapter
POST /api/login
POST /api/graphql
```

Ví dụ một trang có API:

```text
POST /api/search
```

body:

```json
{
    "keyword": "Tiên Hiệp",
    "page": 2
}
```

Fetcher của chúng ta phải hỗ trợ:

```python
http_client.post(...)
```

---

# 21. Interface nên thiết kế thế nào?

Không nên chỉ có:

```python
class HttpClient:

    def get(...):
        ...
```

Mà sau này:

```python
from abc import ABC, abstractmethod


class HttpClient(ABC):

    @abstractmethod
    def get(self, url: str, **kwargs):
        pass

    @abstractmethod
    def post(self, url: str, **kwargs):
        pass
```

Infrastructure:

```python
from curl_cffi import requests


class CurlCffiHttpClient(HttpClient):

    def get(self, url: str, **kwargs):
        return requests.get(
            url,
            **kwargs,
        )

    def post(self, url: str, **kwargs):
        return requests.post(
            url,
            **kwargs,
        )
```

Nhưng **chưa nên dừng ở đây**.

Sau này ta sẽ thiết kế request/response model sạch hơn:

```text
HttpClient
   │
   ├── get()
   ├── post()
   │
   ▼
HttpRequest
   │
   ├── url
   ├── params
   ├── headers
   ├── data
   ├── json
   └── timeout
```

---

# 22. Một điều quan trọng về abstraction

Không nên tạo:

```python
class GetRequestBuilder:
    ...
    
class PostRequestBuilder:
    ...
    
class JsonBodyBuilder:
    ...
    
class FormBodyBuilder:
    ...
```

ngay từ bây giờ.

Đây là **over-abstraction**.

Ở giai đoạn hiện tại:

```python
requests.get(...)
requests.post(...)
```

đã đủ rõ.

Ta chỉ abstraction khi có nhu cầu thực tế từ Fetcher.

---

# 23. Bài thực hành

Tạo:

```text
lesson04.py
```

## Bài 1 — Form

Gửi:

```text
username = python
password = crawler
```

đến:

```text
https://httpbin.org/post
```

Sau đó in:

```text
status
form
headers
url
```

---

## Bài 2 — JSON

Gửi:

```python
{
    "title": "Đấu Phá Thương Khung",
    "author": "Thiên Tằm Thổ Đậu",
    "page": 2,
}
```

bằng:

```python
json=...
```

Sau đó kiểm tra server nhận được gì.

---

## Bài 3 — Kết hợp

Viết:

```python
response = requests.post(
    url,
    params=...,
    headers=...,
    json=...,
    timeout=10,
)
```

và giải thích được:

```text
params → URL
headers → HTTP headers
json → request body
timeout → client configuration
```

---

# Tóm tắt Buổi 4

```text
curl_cffi
│
├── GET
│    └── params
│
└── POST
     │
     ├── params → query string
     ├── headers
     ├── data   → form/raw body
     ├── json   → JSON body
     └── files  → multipart
```

Đặc biệt phải nhớ:

```text
params ≠ data ≠ json
```

Ví dụ:

```python
requests.post(
    "https://example.com/api",
    params={"page": 2},
    data={"name": "python"},
)
```

nghĩa là:

```text
POST /api?page=2
Content-Type: ...

Body:
name=python
```

Còn:

```python
requests.post(
    "https://example.com/api",
    params={"page": 2},
    json={"name": "python"},
)
```

là:

```text
POST /api?page=2

Body:
{"name": "python"}
```

**Buổi 5** ta sẽ học **Headers chuyên sâu**: `User-Agent`, `Accept`, `Referer`, `Origin`, `Cookie`, `Authorization`, header mặc định, header browser và cách xây `HeaderProvider`/`UserAgentProvider` cho Fetcher của Novel Crawler.
