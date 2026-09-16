# Buổi 4 — POST, JSON và Request Body trong `primp`

Ở 3 buổi đầu, chúng ta đã có:

```text
01. Client + Response
02. GET + Query Parameters
03. Headers
```

Hôm nay chuyển sang **POST request**.

Đây là phần rất quan trọng vì nhiều API hiện đại không dùng:

```text
GET /search?keyword=python
```

mà dùng:

```text
POST /search

{
    "keyword": "python",
    "page": 2
}
```

---

# 1. GET vs POST

### GET

Dữ liệu thường nằm trong URL:

```text
GET /search?keyword=python&page=2
```

Trong `primp`:

```python
response = client.get(
    url,
    params={
        "keyword": "python",
        "page": 2,
    },
)
```

---

### POST

Dữ liệu thường nằm trong **request body**:

```text
POST /search

{
    "keyword": "python",
    "page": 2
}
```

Trong `primp`, chúng ta sẽ sử dụng các tham số body phù hợp với kiểu dữ liệu cần gửi.

---

# 2. POST cơ bản

Ví dụ với `httpbin`:

```python
import primp


def main():
    client = primp.Client()

    response = client.post(
        "https://httpbin.org/post",
    )

    print("Status:", response.status_code)
    print(response.text)


if __name__ == "__main__":
    main()
```

Ở đây chúng ta gửi một POST request nhưng chưa có body.

---

# 3. Gửi JSON

Đây là trường hợp quan trọng nhất khi làm API client.

Ví dụ dữ liệu:

```python
payload = {
    "username": "alice",
    "age": 25,
}
```

Sau đó gửi:

```python
response = client.post(
    "https://httpbin.org/post",
    json=payload,
)
```

Code đầy đủ:

```python
import primp


def main():
    client = primp.Client()

    payload = {
        "username": "alice",
        "age": 25,
    }

    response = client.post(
        "https://httpbin.org/post",
        json=payload,
    )

    print("Status:", response.status_code)
    print(response.text)


if __name__ == "__main__":
    main()
```

---

# 4. `json=` có ý nghĩa gì?

Khi viết:

```python
json=payload
```

ta đang nói với HTTP client:

> "Hãy serialize object Python này thành JSON và gửi nó làm request body."

Ví dụ:

```python
payload = {
    "title": "Python",
    "page": 2,
}
```

sẽ được gửi về dạng JSON tương đương:

```json
{
    "title": "Python",
    "page": 2
}
```

Đây là khác biệt rất lớn so với:

```python
params=payload
```

---

# 5. `params=` vs `json=`

Đây là phần cần nhớ.

## `params=`

```python
client.get(
    url,
    params={
        "page": 2,
    },
)
```

Tạo query string:

```text
?page=2
```

---

## `json=`

```python
client.post(
    url,
    json={
        "page": 2,
    },
)
```

Dữ liệu nằm trong body:

```json
{
    "page": 2
}
```

Sơ đồ:

```text
params=
    ↓
URL
    ↓
/search?page=2


json=
    ↓
Request Body
    ↓
{
    "page": 2
}
```

---

# 6. Kiểm tra JSON mà server nhận được

`httpbin` rất tiện cho việc học.

```python
import primp


def main():
    client = primp.Client()

    response = client.post(
        "https://httpbin.org/post",
        json={
            "keyword": "python",
            "page": 2,
            "limit": 20,
        },
    )

    data = response.json()

    print("JSON server nhận:")
    print(data["json"])


if __name__ == "__main__":
    main()
```

Kết quả sẽ tương tự:

```text
{
    'keyword': 'python',
    'page': 2,
    'limit': 20
}
```

---

# 7. `response.json()`

Ở buổi 1 chúng ta đã biết:

```python
response.text
```

Nếu server trả JSON, có thể dùng:

```python
response.json()
```

Ví dụ:

```python
data = response.json()

print(type(data))
```

Thường sẽ nhận:

```text
<class 'dict'>
```

Sau đó:

```python
print(data["json"])
```

---

# 8. JSON nested

JSON thực tế thường phức tạp hơn:

```python
payload = {
    "user": {
        "name": "Alice",
        "age": 25,
    },
    "books": [
        {
            "title": "Python",
            "page": 100,
        },
        {
            "title": "HTTP",
            "page": 200,
        },
    ],
}
```

Gửi:

```python
response = client.post(
    "https://httpbin.org/post",
    json=payload,
)
```

Không cần tự:

```python
json.dumps(...)
```

trước khi truyền vào `json=`.

---

# 9. Không nên làm `json.dumps()` một cách thừa thãi

Ví dụ:

```python
import json

payload = {
    "name": "Alice",
}

body = json.dumps(payload)

response = client.post(
    url,
    json=body,
)
```

Đây là cách dễ gây nhầm.

Nếu API của `primp` hỗ trợ `json=`, hãy truyền **Python object**:

```python
payload = {
    "name": "Alice",
}

response = client.post(
    url,
    json=payload,
)
```

Tư duy:

```text
Python dict
    ↓
json=
    ↓
serialize JSON
    ↓
HTTP body
```

---

# 10. `data=` khác `json=`

Đây là phần rất quan trọng.

Giả sử website có HTML form:

```html
<form>
    <input name="username">
    <input name="password">
</form>
```

Dữ liệu form thường có dạng:

```text
username=alice&password=123
```

Trong HTTP client, đây là **form data**, khác JSON.

Conceptually:

```text
json=
    ↓
application/json

data=
    ↓
form/body data
```

Ví dụ:

```python
response = client.post(
    "https://httpbin.org/post",
    data={
        "username": "alice",
        "password": "123",
    },
)
```

---

# 11. So sánh `json=` và `data=`

### JSON API

```python
response = client.post(
    url,
    json={
        "username": "alice",
        "password": "123",
    },
)
```

Body conceptually:

```json
{
    "username": "alice",
    "password": "123"
}
```

---

### HTML form

```python
response = client.post(
    url,
    data={
        "username": "alice",
        "password": "123",
    },
)
```

Body conceptually:

```text
username=alice&password=123
```

---

# 12. `Content-Type`

Đây là nơi **Headers** của Buổi 3 kết nối với POST.

JSON request thường sử dụng:

```text
Content-Type: application/json
```

Form URL encoded thường sử dụng:

```text
Content-Type: application/x-www-form-urlencoded
```

Do đó:

```text
json=
   ↓
JSON serialization
   ↓
Content-Type phù hợp


data=
   ↓
form/body encoding
   ↓
Content-Type phù hợp
```

Với `primp`, nên ưu tiên API cấp cao như `json=`/`data=` thay vì tự serialize và tự quản lý `Content-Type` nếu không có lý do đặc biệt.

---

# 13. POST + Query Parameters

POST vẫn có thể có query parameters.

Ví dụ:

```python
response = client.post(
    "https://httpbin.org/post",
    params={
        "source": "crawler",
    },
    json={
        "page": 2,
    },
)
```

Request conceptually:

```text
POST /post?source=crawler

{
    "page": 2
}
```

Tức:

```text
params=
    ↓
URL

json=
    ↓
Body
```

Hai thứ này độc lập.

---

# 14. POST + Headers + JSON

Đây là một request tương đối hoàn chỉnh:

```python
import primp


def main():
    client = primp.Client()

    response = client.post(
        "https://httpbin.org/post",
        headers={
            "Accept": "application/json",
        },
        params={
            "source": "novel-crawler",
        },
        json={
            "keyword": "python",
            "page": 2,
        },
    )

    print("Status:", response.status_code)

    data = response.json()

    print("URL:")
    print(data["url"])

    print("\nHeaders:")
    print(data["headers"])

    print("\nJSON:")
    print(data["json"])


if __name__ == "__main__":
    main()
```

Đây là pattern:

```text
                    POST
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
      params       headers       json
        │            │            │
        ▼            ▼            ▼
       URL        metadata       body
```

---

# 15. Ứng dụng vào Novel Crawler

Crawler truyện của bạn chủ yếu sẽ fetch HTML bằng:

```python
GET
```

nhưng POST có thể xuất hiện ở:

```text
login
search API
AJAX endpoint
API lấy chapter
API lấy metadata
API pagination
```

Ví dụ website có API:

```text
POST /api/search
```

Body:

```json
{
    "keyword": "tiên hiệp",
    "page": 2
}
```

Fetcher có thể làm:

```python
import primp


class PrimpFetcher:

    def __init__(self):
        self.client = primp.Client()

    def post_json(
        self,
        url: str,
        payload: dict,
    ):
        return self.client.post(
            url,
            json=payload,
        )
```

Sau này chúng ta sẽ **không dừng ở đây**, vì architecture chuẩn sẽ cần:

```text
Request
   │
   ▼
Fetcher
   │
   ▼
Primp
   │
   ▼
Response
```

và request sẽ có model riêng.

---

# 16. Tạo Request Model — tư duy chuẩn bị cho DDD

Ví dụ đơn giản:

```python
from dataclasses import dataclass, field


@dataclass
class HttpRequest:
    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, object] = field(default_factory=dict)
    json: object | None = None
```

Ta có thể tạo:

```python
request = HttpRequest(
    method="POST",
    url="https://example.com/api/search",
    json={
        "keyword": "python",
        "page": 2,
    },
)
```

Sau đó:

```text
HttpRequest
     │
     ▼
PrimpFetcher
     │
     ▼
primp.Client.post(...)
```

Đây là hướng chúng ta sẽ dùng về sau khi xây **Fetcher hoàn chỉnh**.

---

# 17. Một lỗi thiết kế cần tránh

Không nên để domain biết:

```python
primp.Client
```

Ví dụ ❌:

```python
class NovelService:

    def search(self, keyword):
        client = primp.Client()

        return client.post(
            "...",
            json={"keyword": keyword},
        )
```

Domain/application của bạn đang bị phụ thuộc vào infrastructure.

Thay vào đó:

```text
Application
    │
    ▼
Fetcher Interface
    │
    ▼
PrimpFetcher
    │
    ▼
primp
```

Ví dụ:

```python
from abc import ABC, abstractmethod


class Fetcher(ABC):

    @abstractmethod
    def get(self, url: str, **kwargs):
        ...

    @abstractmethod
    def post(self, url: str, **kwargs):
        ...
```

Sau này:

```python
class PrimpFetcher(Fetcher):

    def get(self, url: str, **kwargs):
        return self.client.get(url, **kwargs)

    def post(self, url: str, **kwargs):
        return self.client.post(url, **kwargs)
```

---

# 18. Bài tập thực hành

## Bài 1 — POST JSON

Gửi:

```python
{
    "title": "Python",
    "page": 10,
    "author": "Alice",
}
```

tới:

```text
https://httpbin.org/post
```

và in JSON server nhận được.

---

## Bài 2 — POST Form

Gửi:

```python
{
    "username": "alice",
    "password": "secret",
}
```

bằng `data=`.

Sau đó kiểm tra:

```python
data = response.json()

print(data["form"])
```

So sánh với `data["json"]`.

---

## Bài 3 — POST + params

Tạo request:

```text
POST /post?source=novel&page=2
```

với body:

```json
{
    "keyword": "tiên hiệp"
}
```

Gợi ý:

```python
response = client.post(
    url,
    params={...},
    json={...},
)
```

---

## Bài 4 — Phân biệt 3 loại dữ liệu

Tự viết 3 request:

```python
params={}
```

```python
data={}
```

```python
json={}
```

và ghi lại:

```text
Dữ liệu nằm ở đâu?
Content-Type là gì?
Server đọc dữ liệu bằng cách nào?
```

Đây là bài quan trọng, vì sau này khi debug API crawler, việc nhìn request rồi xác định **query / form / JSON body** sẽ giúp bạn tìm lỗi rất nhanh.

---

# Tổng kết Buổi 4

```text
GET
 │
 └── params
       ↓
      URL


POST
 │
 ├── params
 │     ↓
 │    URL
 │
 ├── data
 │     ↓
 │    Form / body
 │
 └── json
       ↓
      JSON body
```

Cần đặc biệt nhớ:

```text
params ≠ data ≠ json
```

và:

```text
json=
```

thường là lựa chọn tự nhiên khi gọi **JSON API**.

### Roadmap hiện tại

```text
01. Client + Response             ✓
02. GET + Query Parameters        ✓
03. Headers                      ✓
04. POST + JSON                  ← hôm nay
05. Cookies
06. Form Data
07. Response JSON
08. Redirect
09. Timeout
10. Exception
...
14. Proxy
...
21. Browser Impersonation
...
31. AsyncClient
...
44. PrimpFetcher
```

**Buổi 5** chúng ta sẽ học **Cookies trong `primp`**: cookie request, `Set-Cookie`, cookie persistence, client session, và vì sao việc **tái sử dụng một `Client`** quan trọng đối với crawler.
