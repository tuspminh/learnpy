Được. Tôi sẽ dạy bạn **HTTPX từ nền tảng đến chuyên sâu**, theo kiểu học lập trình Python thực chiến: mỗi buổi có lý thuyết → code → phân tích → bài tập → mini project.

# Giáo trình HTTPX — Python HTTP Client Deep Dive

Mục tiêu cuối khóa: bạn có thể dùng HTTPX để xây dựng **API Client, Web Crawler, REST Client, Async HTTP Service**, kết hợp với `asyncio`, retry, timeout, connection pooling, authentication và testing.

## Phần I — HTTPX Foundation

1. **Buổi 1 — HTTPX là gì?**

   * HTTPX vs `requests`
   * Cài đặt
   * `httpx.get()`
   * `httpx.post()`
   * Response
   * Status code
   * Headers
   * Text / JSON / Content

2. **Buổi 2 — Request & Response Deep Dive**

   * `Request`
   * `Response`
   * URL
   * Query parameters
   * Headers
   * Cookies
   * Body
   * JSON body

3. **Buổi 3 — HTTP Methods**

   * GET
   * POST
   * PUT
   * PATCH
   * DELETE
   * HEAD
   * OPTIONS

4. **Buổi 4 — HTTPX Client**

   * `httpx.Client`
   * Connection pooling
   * Session-like behavior
   * Default headers
   * Default params
   * Cookies
   * Base URL

5. **Buổi 5 — Timeout**

   * Connect timeout
   * Read timeout
   * Write timeout
   * Pool timeout
   * `httpx.Timeout`

---

# Phần II — Request nâng cao

6. Query parameters
7. Headers
8. Cookies
9. Form data
10. JSON request
11. Multipart upload
12. File upload
13. Streaming response
14. Redirect
15. Authentication

# Phần III — Async HTTPX

16. `httpx.AsyncClient`
17. `async/await`
18. Concurrent requests
19. `asyncio.gather()`
20. Connection pooling async
21. Async timeout
22. Cancellation
23. Semaphore
24. Rate limiting
25. Async crawler

# Phần IV — Error Handling & Reliability

26. HTTPX exceptions
27. `raise_for_status()`
28. Retry
29. Exponential backoff
30. Retry policy
31. Circuit breaker
32. Rate limit `429`
33. Server errors `5xx`
34. Network errors
35. Production HTTP Client

# Phần V — HTTPX Architecture

36. Transport
37. `HTTPTransport`
38. `AsyncHTTPTransport`
39. Custom Transport
40. Mock Transport
41. Proxy
42. SSL/TLS
43. HTTP/2
44. Connection limits
45. Custom authentication

# Phần VI — Testing

46. Test HTTP Client
47. `MockTransport`
48. pytest
49. Async testing
50. Mock API
51. Contract testing
52. Integration testing

# Phần VII — Project

53. Xây dựng REST API Client
54. Xây dựng Async API Client
55. Xây dựng Web Crawler
56. Retry + Rate Limit
57. Proxy Pool
58. API Client Architecture
59. HTTP Client + Repository
60. **Final Project — Production-grade HTTP Client**

---

# Buổi 1 — HTTPX là gì?

## 1. HTTPX dùng để làm gì?

`httpx` là thư viện Python dùng để **gửi HTTP request đến server**.

Ví dụ:

```text
Python Application
       │
       │ HTTP Request
       ▼
   HTTP Server
       │
       │ HTTP Response
       ▼
Python Application
```

Ví dụ bạn muốn gọi:

```text
GET https://example.com
```

Python có thể dùng HTTPX:

```python
import httpx

response = httpx.get("https://example.com")

print(response.status_code)
print(response.text)
```

---

# 2. Cài đặt

Với `pip`:

```bash
pip install httpx
```

Nếu bạn đang sử dụng `uv`:

```bash
uv add httpx
```

Kiểm tra:

```python
import httpx

print(httpx.__version__)
```

---

# 3. Request đầu tiên

Code đơn giản nhất:

```python
import httpx

response = httpx.get("https://example.com")

print(response)
```

Bạn sẽ nhận được một object kiểu:

```text
<Response [200 OK]>
```

HTTPX không trả về trực tiếp HTML.

Nó trả về một object:

```python
httpx.Response
```

---

# 4. Status Code

Server trả về HTTP status code.

Ví dụ:

```python
response = httpx.get("https://example.com")

print(response.status_code)
```

Kết quả:

```text
200
```

Một số status code quan trọng:

| Code | Ý nghĩa               |
| ---: | --------------------- |
|  200 | OK                    |
|  201 | Created               |
|  204 | No Content            |
|  301 | Moved Permanently     |
|  302 | Found                 |
|  400 | Bad Request           |
|  401 | Unauthorized          |
|  403 | Forbidden             |
|  404 | Not Found             |
|  429 | Too Many Requests     |
|  500 | Internal Server Error |
|  502 | Bad Gateway           |
|  503 | Service Unavailable   |

Trong crawler/API client, việc hiểu status code cực kỳ quan trọng.

---

# 5. Đọc HTML

```python
import httpx

response = httpx.get("https://example.com")

html = response.text

print(html)
```

`response.text` là chuỗi Python:

```python
print(type(response.text))
```

Kết quả:

```text
<class 'str'>
```

Ví dụ:

```python
html = response.text

print(html[:500])
```

Lấy 500 ký tự đầu tiên.

---

# 6. `content` khác `text` thế nào?

HTTP response thực chất là **bytes**.

HTTPX cung cấp:

```python
response.content
```

Ví dụ:

```python
response = httpx.get("https://example.com")

print(type(response.content))
```

Kết quả:

```text
<class 'bytes'>
```

Trong khi:

```python
print(type(response.text))
```

là:

```text
<class 'str'>
```

Có thể hình dung:

```text
HTTP Response
     │
     ├── content → bytes
     │
     └── text    → str
```

Ví dụ:

```python
print(response.content[:100])
```

---

# 7. JSON Response

Đây là tính năng cực kỳ quan trọng khi làm REST API.

Giả sử server trả:

```json
{
    "id": 1,
    "name": "Alice"
}
```

HTTPX có:

```python
response.json()
```

Ví dụ:

```python
import httpx

response = httpx.get(
    "https://jsonplaceholder.typicode.com/users/1"
)

data = response.json()

print(data)
```

Kết quả dạng:

```python
{
    "id": 1,
    "name": "Leanne Graham",
    ...
}
```

Và:

```python
print(type(data))
```

thường là:

```text
<class 'dict'>
```

---

# 8. Headers

HTTP response có headers.

```python
response = httpx.get("https://example.com")

print(response.headers)
```

Bạn có thể lấy một header:

```python
print(response.headers["content-type"])
```

Hoặc:

```python
print(response.headers.get("content-type"))
```

Ví dụ:

```text
text/html; charset=UTF-8
```

Một số header quan trọng:

```text
Content-Type
Content-Length
Set-Cookie
Location
Cache-Control
Server
Date
```

---

# 9. Request Headers

Không chỉ response có headers.

Bạn cũng có thể gửi headers:

```python
import httpx

headers = {
    "User-Agent": "MyCrawler/1.0",
}

response = httpx.get(
    "https://example.com",
    headers=headers,
)

print(response.status_code)
```

Đây là nền tảng rất quan trọng khi sau này chúng ta xây dựng crawler.

---

# 10. Query Parameters

Ví dụ URL:

```text
https://example.com/search?q=python&page=2
```

Không nên tự nối string:

```python
url = "https://example.com/search?q=python&page=2"
```

HTTPX cho phép:

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

HTTPX sẽ tạo:

```text
https://example.com/search?q=python&page=2
```

Đây là cách nên sử dụng.

---

# 11. POST JSON

GET thường dùng để lấy dữ liệu.

POST thường dùng để gửi dữ liệu.

HTTPX:

```python
import httpx

data = {
    "username": "alice",
    "password": "123456",
}

response = httpx.post(
    "https://example.com/login",
    json=data,
)

print(response.status_code)
```

Điểm rất quan trọng:

```python
json=data
```

khác với:

```python
data=data
```

`json=` dùng khi muốn gửi JSON.

---

# 12. `response.raise_for_status()`

Đây là một API bạn cần nhớ.

Ví dụ:

```python
response = httpx.get("https://example.com")

response.raise_for_status()
```

Nếu:

```text
200
```

thì không có vấn đề.

Nếu:

```text
404
```

HTTPX sẽ raise exception tương ứng.

Ví dụ:

```python
try:
    response = httpx.get("https://example.com/not-found")
    response.raise_for_status()

except httpx.HTTPStatusError as exc:
    print("HTTP error:", exc)
```

Sau này chúng ta sẽ học toàn bộ hệ thống exception của HTTPX.

---

# 13. Một HTTPX request thực chất gồm gì?

Khi bạn viết:

```python
response = httpx.get(
    "https://example.com",
)
```

hãy tư duy:

```text
Python
  │
  │
  │  HTTP Request
  │
  ▼
┌─────────────────────┐
│ GET / HTTP/1.1      │
│ Host: example.com   │
│ User-Agent: ...     │
└─────────────────────┘
          │
          ▼
       Server
          │
          │ HTTP Response
          ▼
┌─────────────────────┐
│ HTTP/1.1 200 OK     │
│ Content-Type: ...   │
│                     │
│ <html>...</html>    │
└─────────────────────┘
          │
          ▼
    httpx.Response
```

Đây là mô hình nền tảng của toàn bộ khóa học.

---

# 14. Ví dụ tổng hợp

```python
import httpx


url = "https://jsonplaceholder.typicode.com/users"

params = {
    "_limit": 5,
}

headers = {
    "User-Agent": "MyApp/1.0",
}

response = httpx.get(
    url,
    params=params,
    headers=headers,
)

print("Status:", response.status_code)
print("URL:", response.url)
print("Content-Type:", response.headers.get("content-type"))

response.raise_for_status()

users = response.json()

for user in users:
    print(user["id"], user["name"])
```

Ở đây bạn đã sử dụng:

```text
httpx.get()
       │
       ├── URL
       ├── params
       ├── headers
       │
       ▼
   Response
       │
       ├── status_code
       ├── url
       ├── headers
       ├── json()
       ├── text
       ├── content
       └── raise_for_status()
```

---

# 15. Bài tập Buổi 1

### Bài 1

Gửi GET request tới:

```text
https://example.com
```

In:

```text
status code
url
content-type
độ dài HTML
```

### Bài 2

Gọi:

```text
https://jsonplaceholder.typicode.com/users
```

Parse JSON và in:

```text
id - name - email
```

### Bài 3

Gửi query:

```text
?page=2&limit=10
```

nhưng **không được tự nối chuỗi URL**.

Hãy sử dụng:

```python
params={}
```

### Bài 4 — quan trọng

Viết function:

```python
def get_json(url: str) -> dict:
    ...
```

Yêu cầu:

```text
GET
→ kiểm tra HTTP status
→ parse JSON
→ return dữ liệu
```

### Bài 5 — Mini Project

Viết:

```text
api_client.py
```

có:

```python
get()
post()
```

Ví dụ:

```python
client.get(url)
client.post(url, json=data)
```

**Buổi 2** chúng ta sẽ đi sâu vào `Request`, `Response`, URL, query params, headers, cookies và đặc biệt là **`httpx.Client`** — đây là bước chuyển từ việc "gọi HTTP đơn lẻ" sang thiết kế một HTTP client thực sự.
