# Buổi 3 — `Response` trong `curl_cffi`

Hôm nay ta tập trung hoàn toàn vào object:

```python
response = requests.get(...)
```

Đây là phần rất quan trọng, vì trong crawler:

```text
HTTP Server
    ↓
curl_cffi
    ↓
Response
    ↓
Fetcher
    ↓
Parser
```

Fetcher không chỉ lấy HTML. Nó phải **đọc và đánh giá Response** trước khi đưa dữ liệu xuống Parser.

---

# 1. Tạo một Response

```python
from curl_cffi import requests


response = requests.get(
    "https://httpbin.org/get",
    timeout=10,
)

print(type(response))
```

Bạn sẽ nhận được object kiểu:

```text
curl_cffi.requests.Response
```

Có thể hình dung:

```text
Response
├── status_code
├── headers
├── cookies
├── text
├── content
├── url
├── encoding
├── json()
├── ok
├── reason
└── ...
```

---

# 2. `status_code`

Đây là thuộc tính quan trọng nhất.

```python
response.status_code
```

Ví dụ:

```python
from curl_cffi import requests


response = requests.get(
    "https://httpbin.org/status/200"
)

print(response.status_code)
```

Kết quả:

```text
200
```

Crawler thường quan tâm:

```text
2xx → thành công
3xx → redirect
4xx → request/client problem
5xx → server problem
```

Ví dụ:

```python
if response.status_code == 200:
    print("OK")
```

---

# 3. Không nên chỉ kiểm tra `== 200`

Trong crawler thực tế:

```python
if response.status_code == 200:
    ...
```

không phải lúc nào cũng đủ.

Ví dụ server có thể trả:

```text
201
204
206
```

tùy loại request/resource.

Do đó thường cần phân biệt:

```python
status = response.status_code

if 200 <= status < 300:
    print("Success")
elif 300 <= status < 400:
    print("Redirect")
elif 400 <= status < 500:
    print("Client error")
elif 500 <= status < 600:
    print("Server error")
```

---

# 4. `response.ok`

Có thể kiểm tra:

```python
print(response.ok)
```

Ví dụ:

```python
response = requests.get(
    "https://httpbin.org/status/200"
)

print(response.ok)
```

Thông thường:

```text
True
```

Nếu response thuộc nhóm lỗi HTTP:

```python
response = requests.get(
    "https://httpbin.org/status/404"
)

print(response.ok)
```

thì:

```text
False
```

Mental model:

```text
response.ok
      ↓
HTTP response có được xem là thành công không?
```

Tuy nhiên, **đừng dùng `ok` để thay thế hoàn toàn `status_code`**.

Trong crawler, `403`, `404`, `429`, `500`, `503` có ý nghĩa rất khác nhau.

---

# 5. `reason`

```python
print(response.reason)
```

Ví dụ có thể nhận:

```text
OK
```

hoặc:

```text
Not Found
```

Ví dụ:

```python
response = requests.get(
    "https://httpbin.org/status/404"
)

print(response.status_code)
print(response.reason)
```

Mental model:

```text
status_code = 404
reason      = "NOT FOUND"
```

`status_code` nên được dùng cho logic.

`reason` chủ yếu hữu ích cho:

* logging
* debugging
* diagnostic information

---

# 6. `response.url`

Đây là URL cuối cùng mà response tương ứng.

```python
print(response.url)
```

Ví dụ:

```python
response = requests.get(
    "https://httpbin.org/get"
)

print(response.url)
```

Có thể dùng để kiểm tra:

```text
URL ban đầu
        ↓
redirect
        ↓
URL cuối cùng
```

Điều này rất hữu ích khi crawler xử lý:

```text
canonical URL
redirect
short URL
pagination
chapter URL
```

---

# 7. Redirect

Ví dụ:

```python
response = requests.get(
    "https://httpbin.org/redirect/1"
)

print(response.status_code)
print(response.url)
```

Nếu redirect được follow, bạn thường sẽ thấy response cuối cùng.

Có thể kiểm tra lịch sử redirect:

```python
print(response.history)
```

Mental model:

```text
URL A
 ↓
301/302
 ↓
URL B
 ↓
200
 ↓
Response
```

---

# 8. `response.history`

Ví dụ:

```python
response = requests.get(
    "https://httpbin.org/redirect/2"
)

for item in response.history:
    print(
        item.status_code,
        item.url,
    )

print("Final:", response.url)
```

Điều này đặc biệt hữu ích khi debug website có nhiều redirect.

Trong crawler:

```text
requested_url
      ↓
redirect chain
      ↓
final_url
```

Ta có thể lưu lại cả:

```python
requested_url
final_url
```

để phục vụ URL normalization sau này.

---

# 9. `headers`

Response headers:

```python
print(response.headers)
```

Ví dụ:

```python
response = requests.get(
    "https://httpbin.org/get"
)

print(response.headers)
```

Bạn sẽ thấy những header như:

```text
content-type
content-length
date
server
...
```

---

# 10. Lấy một header cụ thể

Không cần lấy toàn bộ:

```python
content_type = response.headers.get(
    "content-type"
)

print(content_type)
```

Ví dụ:

```python
content_type = response.headers.get("Content-Type")
```

HTTP header names thường được xử lý không phân biệt hoa thường ở tầng HTTP.

Nhưng trong code Python, nên thống nhất cách viết:

```python
response.headers.get("content-type")
```

---

# 11. Những Response Header quan trọng với crawler

Một số header rất đáng quan tâm:

```text
Content-Type
Content-Length
Content-Encoding
Cache-Control
ETag
Last-Modified
Location
Set-Cookie
Retry-After
```

Đặc biệt:

### `Content-Type`

```python
content_type = response.headers.get(
    "content-type"
)
```

Ví dụ:

```text
text/html; charset=UTF-8
```

Parser HTML có thể xử lý.

Nhưng nếu:

```text
application/pdf
```

thì đây không còn là HTML page nữa.

---

# 12. `text`

Đây là thuộc tính chúng ta dùng rất nhiều trong Novel Crawler:

```python
html = response.text
```

Kiểu dữ liệu:

```python
str
```

Ví dụ:

```python
response = requests.get(
    "https://example.com"
)

html = response.text

print(type(html))
print(html[:500])
```

Pipeline:

```text
curl_cffi
    ↓
Response
    ↓
response.text
    ↓
str
    ↓
Selectolax
```

---

# 13. `content`

Khác với `text`:

```python
response.content
```

là bytes.

```python
data = response.content

print(type(data))
```

Kết quả:

```text
<class 'bytes'>
```

Dùng cho:

```text
image
PDF
ZIP
audio
binary file
```

Ví dụ:

```python
data = response.content

with open("output.bin", "wb") as f:
    f.write(data)
```

---

# 14. `text` vs `content`

Đây là điểm cần nhớ:

```text
response.text
      ↓
    str
      ↓
HTML / text


response.content
      ↓
   bytes
      ↓
binary
```

Trong Novel Crawler:

```text
Chapter page
     ↓
response.text
     ↓
HTML parser
```

Còn:

```text
Cover image
     ↓
response.content
     ↓
save file
```

---

# 15. `encoding`

Có thể kiểm tra:

```python
print(response.encoding)
```

Ví dụ:

```text
UTF-8
```

Encoding rất quan trọng với website tiếng Việt.

Nếu server khai báo:

```text
Content-Type: text/html; charset=utf-8
```

client có thể sử dụng thông tin đó để decode response.

---

# 16. Đừng vội tự decode bytes

Một lỗi phổ biến:

```python
html = response.content.decode("utf-8")
```

Trong nhiều trường hợp nó hoạt động.

Nhưng không nên mặc định rằng mọi website đều:

```text
UTF-8
```

Tốt hơn là để HTTP client xử lý text decoding phù hợp, hoặc xử lý encoding một cách có chủ đích khi website có vấn đề.

---

# 17. JSON Response

Nếu server trả JSON:

```python
response = requests.get(
    "https://httpbin.org/json"
)
```

Có thể:

```python
data = response.json()

print(type(data))
print(data)
```

Thông thường:

```text
dict
```

Ví dụ:

```python
from curl_cffi import requests


response = requests.get(
    "https://httpbin.org/json"
)

data = response.json()

print(data)
```

---

# 18. Không gọi `.json()` cho HTML

Nếu:

```text
Content-Type: text/html
```

thì không nên:

```python
response.json()
```

Thay vào đó:

```python
response.text
```

Một HTTP client không thể biết business meaning của response.

Do đó application phải biết:

```text
HTML → parser HTML
JSON → JSON parser
image → bytes
PDF → PDF parser
```

---

# 19. `cookies`

Response có thể chứa cookies:

```python
print(response.cookies)
```

Ví dụ server gửi:

```text
Set-Cookie
```

thì cookie có thể xuất hiện trong response.

Cookies rất quan trọng khi làm:

```text
login
session
authentication
website state
```

Phần này chúng ta sẽ học kỹ ở **Buổi 13 — Cookies**.

---

# 20. `raise_for_status()`

Ta đã gặp ở Buổi 1.

```python
response.raise_for_status()
```

Ví dụ:

```python
response = requests.get(
    "https://httpbin.org/status/404"
)

response.raise_for_status()
```

Nếu HTTP status là lỗi, exception sẽ được raise.

Đối với script nhỏ:

```python
response.raise_for_status()
```

rất tiện.

Nhưng với crawler production:

```text
403
404
408
429
500
502
503
504
```

không nên gom tất cả thành:

```text
Exception
```

Ta cần phân loại.

---

# 21. Thiết kế `Response` cho Fetcher

Đây là phần quan trọng nhất của buổi hôm nay.

Đừng để Application phụ thuộc trực tiếp vào:

```python
curl_cffi.requests.Response
```

Ví dụ không tốt:

```python
class CrawlChapter:

    def execute(self):
        response = self.http_client.get(url)

        if response.status_code == 200:
            html = response.text
```

Application lúc này biết:

```text
curl_cffi Response
```

Đó là coupling.

---

# 22. Tạo `HttpResponse`

Ta có thể định nghĩa abstraction:

```python
from dataclasses import dataclass


@dataclass
class HttpResponse:
    status_code: int
    url: str
    headers: dict[str, str]
    text: str
    content: bytes
```

Infrastructure:

```python
from curl_cffi import requests


class CurlCffiHttpClient:

    def get(self, url: str) -> HttpResponse:
        response = requests.get(
            url,
            timeout=10,
        )

        return HttpResponse(
            status_code=response.status_code,
            url=str(response.url),
            headers=dict(response.headers),
            text=response.text,
            content=response.content,
        )
```

Bây giờ:

```text
                Infrastructure
                     │
                 curl_cffi
                     │
                     ▼
            curl_cffi.Response
                     │
                     ▼
              HttpResponse
                     │
                     ▼
              Application
```

Application **không cần biết curl_cffi tồn tại**.

Đây là hướng mà chúng ta sẽ tiếp tục xây trong các buổi sau.

---

# 23. Một `HttpResponse` tốt hơn

Sau này có thể thiết kế:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class HttpResponse:
    status_code: int
    url: str
    headers: dict[str, str]
    content: bytes

    @property
    def text(self) -> str:
        ...
```

Hoặc tách:

```text
HttpResponse
    │
    ├── status_code
    ├── url
    ├── headers
    ├── content
    └── text
```

Đây là nơi ta sẽ quyết định **response model của Fetcher**.

Chưa cần abstraction quá sớm.

---

# 24. Ví dụ hoàn chỉnh Buổi 3

```python
from curl_cffi import requests


def inspect_response(response):
    print("=" * 60)

    print("STATUS CODE :", response.status_code)
    print("OK          :", response.ok)
    print("REASON      :", response.reason)
    print("URL         :", response.url)
    print("ENCODING    :", response.encoding)

    print(
        "CONTENT TYPE:",
        response.headers.get("content-type"),
    )

    print(
        "CONTENT LEN :",
        len(response.content),
    )

    print(
        "HISTORY     :",
        response.history,
    )

    print("=" * 60)


def main():
    response = requests.get(
        "https://httpbin.org/get",
        timeout=10,
    )

    inspect_response(response)

    print(response.text[:500])


if __name__ == "__main__":
    main()
```

---

# 25. Mental model sau Buổi 3

Hãy nhớ `Response` theo 4 nhóm:

```text
Response
│
├── 1. HTTP status
│      ├── status_code
│      ├── ok
│      └── reason
│
├── 2. Request/result URL
│      ├── url
│      └── history
│
├── 3. Metadata
│      ├── headers
│      ├── cookies
│      └── encoding
│
└── 4. Body
       ├── text
       ├── content
       └── json()
```

Và trong Novel Crawler:

```text
curl_cffi.Response
        │
        ▼
   HttpResponse
        │
        ▼
      Fetcher
        │
        ▼
    page-source
        │
        ▼
     Parser
        │
        ▼
     Domain
```

### Bài tập

Viết một `ResponseInspector`:

```python
class ResponseInspector:

    def inspect(self, response):
        ...
```

Nó phải in:

```text
Status
OK
Reason
URL
Content-Type
Encoding
Content-Length
Redirect history
```

Sau đó thử với:

```text
https://httpbin.org/get
https://httpbin.org/status/404
https://httpbin.org/redirect/2
```

**Buổi 4** ta sẽ học `POST`, `data`, `json`, form submission và multipart — đồng thời phân biệt rõ **query string vs request body**, vì đây là nền tảng để hiểu toàn bộ HTTP client.
