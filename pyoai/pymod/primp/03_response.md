# Buổi 3 — Response trong `primp`

Hôm nay chúng ta tập trung hoàn toàn vào **Response**: sau khi `primp` gửi HTTP request, ta lấy dữ liệu trả về như thế nào và tổ chức nó cho đúng trong crawler.

> Theo roadmap của bạn: **03 — Response**. Phần Headers sẽ học ở Buổi 4.

---

# 1. Response là gì?

Khi bạn gọi:

```python
response = client.get("https://httpbin.org/get")
```

`primp` gửi request đến server.

Server trả về một **HTTP Response**.

Có thể hình dung:

```text
Python
  │
  │ GET
  ▼
┌──────────────────┐
│      Server      │
└──────────────────┘
  │
  │ HTTP Response
  ▼
┌──────────────────────────┐
│ status_code              │
│ headers                  │
│ url                      │
│ text                     │
│ content                  │
│ json()                   │
└──────────────────────────┘
```

Trong crawler, Response chính là **nguyên liệu đầu vào cho Parser**.

```text
PrimpFetcher
     │
     │ HTTP
     ▼
  Response
     │
     ▼
   Parser
     │
     ▼
 Novel / Chapter
```

---

# 2. Tạo Client

Bắt đầu bằng ví dụ đơn giản:

```python
import primp


def main():
    client = primp.Client()

    response = client.get(
        "https://httpbin.org/get"
    )

    print(response)


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python main.py
```

Bạn sẽ thấy một object Response.

Điểm quan trọng:

```python
response
```

**không phải là HTML/text trực tiếp**.

Nó là một object chứa toàn bộ thông tin server trả về.

---

# 3. `response.status_code`

Đây là thuộc tính quan trọng nhất.

```python
print(response.status_code)
```

Ví dụ:

```text
200
```

HTTP status code cho biết kết quả của request.

Một số code cần nhớ:

| Code | Ý nghĩa               |
| ---: | --------------------- |
|  200 | OK                    |
|  201 | Created               |
|  204 | No Content            |
|  301 | Moved Permanently     |
|  302 | Found / Redirect      |
|  400 | Bad Request           |
|  401 | Unauthorized          |
|  403 | Forbidden             |
|  404 | Not Found             |
|  429 | Too Many Requests     |
|  500 | Internal Server Error |
|  502 | Bad Gateway           |
|  503 | Service Unavailable   |

Trong crawler, status code cực kỳ quan trọng.

Ví dụ:

```python
response = client.get(url)

if response.status_code == 200:
    print("Success")

elif response.status_code == 404:
    print("Not found")

elif response.status_code == 403:
    print("Forbidden")

elif response.status_code == 429:
    print("Rate limited")
```

Sau này chúng ta sẽ dùng status code để xây:

```text
Error Classification
Retry Policy
Proxy Strategy
```

---

# 4. `response.url`

Lấy URL của response:

```python
print(response.url)
```

Ví dụ:

```python
response = client.get(
    "https://httpbin.org/get",
    params={
        "q": "python",
        "page": 2,
    },
)

print(response.url)
```

Bạn có thể nhận được URL tương tự:

```text
https://httpbin.org/get?q=python&page=2
```

Điều này rất hữu ích để debug.

Ví dụ crawler:

```python
print("Request URL:", response.url)
```

Khi crawler chạy hàng nghìn request, bạn sẽ biết chính xác request nào đã được gửi.

---

# 5. `response.headers`

Response cũng chứa HTTP response headers.

```python
print(response.headers)
```

Ví dụ server có thể trả về:

```text
Content-Type: application/json
Content-Length: ...
Server: ...
```

Ta có thể lấy một header cụ thể:

```python
content_type = response.headers.get("content-type")

print(content_type)
```

Hoặc:

```python
print(response.headers["content-type"])
```

Tuy nhiên `.get()` thường an toàn hơn vì header có thể không tồn tại.

```python
content_type = response.headers.get("content-type")

if content_type:
    print(content_type)
```

Phần Headers sẽ được học sâu hơn ở buổi riêng.

---

# 6. `response.text`

Đây là phần **rất quan trọng đối với Novel Crawler**.

Nếu server trả HTML:

```python
response = client.get(
    "https://example.com"
)

html = response.text

print(html)
```

`response.text` là nội dung dạng `str`.

Ví dụ:

```python
print(type(response.text))
```

Kết quả:

```text
<class 'str'>
```

Đây chính là thứ chúng ta sẽ truyền cho `selectolax`.

```text
primp
  │
  ▼
response
  │
  ▼
response.text
  │
  ▼
selectolax
  │
  ▼
Parser
```

Ví dụ:

```python
from selectolax.parser import HTMLParser
import primp


def main():
    client = primp.Client()

    response = client.get(
        "https://example.com"
    )

    html = response.text

    tree = HTMLParser(html)

    title = tree.css_first("title")

    if title:
        print(title.text())


if __name__ == "__main__":
    main()
```

Đây chính là cầu nối:

```text
Primp → Selectolax
```

mà chúng ta sẽ sử dụng trong Novel Crawler.

---

# 7. `response.content`

Ngoài `.text`, Response còn có dữ liệu dạng bytes:

```python
content = response.content

print(type(content))
```

Thông thường:

```text
<class 'bytes'>
```

Ví dụ:

```python
print(response.content[:100])
```

Có thể thấy:

```text
b'<!doctype html>...'
```

So sánh:

```python
response.text
```

với:

```python
response.content
```

|                 | `text`        | `content`          |
| --------------- | ------------- | ------------------ |
| Type            | `str`         | `bytes`            |
| Dùng cho HTML   | ✅             | Có thể             |
| Dùng cho binary | Không phù hợp | ✅                  |
| Parser HTML     | ✅             | Thường dùng `text` |
| Image           | ❌             | ✅                  |
| PDF             | ❌             | ✅                  |

Ví dụ tải ảnh:

```python
response = client.get(
    "https://example.com/image.jpg"
)

image_bytes = response.content
```

Sau đó:

```python
with open("image.jpg", "wb") as f:
    f.write(image_bytes)
```

---

# 8. `response.json()`

Nếu server trả JSON, ta có thể gọi:

```python
data = response.json()
```

Ví dụ:

```python
import primp


def main():
    client = primp.Client()

    response = client.get(
        "https://httpbin.org/get"
    )

    data = response.json()

    print(data)


if __name__ == "__main__":
    main()
```

`data` thường là Python object:

```python
print(type(data))
```

Có thể là:

```text
<class 'dict'>
```

Sau đó:

```python
print(data["url"])
```

Hoặc:

```python
print(data["headers"])
```

---

# 9. Không phải Response nào cũng có JSON

Đây là lỗi người mới rất dễ gặp.

Ví dụ:

```python
response = client.get(
    "https://example.com"
)

data = response.json()
```

Nếu server trả HTML thay vì JSON thì việc parse JSON sẽ thất bại.

Do đó:

```python
content_type = response.headers.get("content-type", "")

if "application/json" in content_type:
    data = response.json()
```

Đây là cách tư duy tốt hơn:

```text
Response
   │
   ├── HTML
   │      └── response.text
   │
   ├── JSON
   │      └── response.json()
   │
   ├── Image/PDF/File
   │      └── response.content
   │
   └── Error
          └── status_code
```

---

# 10. Một Response hoàn chỉnh

Bây giờ viết một chương trình kiểm tra Response:

```python
import primp


def main():
    client = primp.Client()

    response = client.get(
        "https://httpbin.org/get",
        params={
            "q": "python",
            "page": 2,
        },
    )

    print("=" * 50)
    print("STATUS")
    print("=" * 50)

    print(response.status_code)

    print()
    print("=" * 50)
    print("URL")
    print("=" * 50)

    print(response.url)

    print()
    print("=" * 50)
    print("HEADERS")
    print("=" * 50)

    print(response.headers)

    print()
    print("=" * 50)
    print("TEXT")
    print("=" * 50)

    print(response.text)

    print()
    print("=" * 50)
    print("CONTENT TYPE")
    print("=" * 50)

    print(type(response.content))

    print()
    print("=" * 50)
    print("JSON")
    print("=" * 50)

    print(response.json())


if __name__ == "__main__":
    main()
```

Đây là bài test đầu tiên bạn nên chạy.

---

# 11. Kiểm tra thành công

Trong crawler, không nên lập tức:

```python
html = response.text
```

mà nên kiểm tra trước:

```python
if response.status_code == 200:
    html = response.text
```

Ví dụ:

```python
import primp


def main():
    client = primp.Client()

    response = client.get(
        "https://example.com"
    )

    if response.status_code == 200:
        print("Request thành công")
        print(response.text)

    else:
        print(
            "Request thất bại:",
            response.status_code,
        )


if __name__ == "__main__":
    main()
```

---

# 12. Response trong Novel Crawler

Đây là phần quan trọng nhất đối với project của bạn.

Chúng ta **không muốn Parser biết `primp`**.

Không nên:

```python
class NovelParser:

    def parse(self, url):
        client = primp.Client()
        response = client.get(url)

        ...
```

Vì Parser lúc này vừa:

```text
HTTP
+
Parsing
```

bị trộn trách nhiệm.

Thay vào đó:

```text
                 ┌──────────────┐
                 │ PrimpFetcher │
                 └──────┬───────┘
                        │
                        ▼
                   HTTP Response
                        │
                        ▼
                 response.text
                        │
                        ▼
                ┌──────────────┐
                │ NovelParser  │
                └──────┬───────┘
                       │
                       ▼
                    Novel
```

Fetcher chịu trách nhiệm HTTP.

Parser chịu trách nhiệm HTML.

---

# 13. Ví dụ đơn giản

Fetcher:

```python
import primp


class PrimpFetcher:

    def __init__(self):
        self.client = primp.Client()

    def get(self, url: str):
        return self.client.get(url)
```

Parser:

```python
from selectolax.parser import HTMLParser


class NovelParser:

    def parse(self, html: str) -> str:
        tree = HTMLParser(html)

        title = tree.css_first("title")

        if title is None:
            return ""

        return title.text(strip=True)
```

Application:

```python
def main():
    fetcher = PrimpFetcher()
    parser = NovelParser()

    response = fetcher.get(
        "https://example.com"
    )

    if response.status_code != 200:
        print(
            "Fetch failed:",
            response.status_code,
        )
        return

    novel_title = parser.parse(
        response.text
    )

    print("Title:", novel_title)
```

Kiến trúc:

```text
Application
    │
    ├── Fetcher
    │      │
    │      └── PrimpFetcher
    │               │
    │               ▼
    │            primp
    │               │
    │               ▼
    │           Response
    │
    └── Parser
           │
           └── selectolax
```

Đây là nền tảng rất quan trọng cho các bài sau.

---

# 14. Đừng nhầm `Response` với `HTML`

Một lỗi thiết kế phổ biến:

```python
parser.parse(response)
```

Trong khi Parser chỉ cần:

```python
parser.parse(response.text)
```

Tốt hơn nữa, sau này chúng ta sẽ tạo riêng:

```python
HttpResponse
```

để application layer không phụ thuộc trực tiếp vào `primp.Response`.

Ví dụ tương lai:

```python
@dataclass
class HttpResponse:
    status_code: int
    url: str
    headers: dict[str, str]
    text: str
    content: bytes
```

Sau đó:

```text
primp.Response
       │
       ▼
PrimpFetcher
       │
       ▼
HttpResponse
       │
       ▼
Application
       │
       ▼
Parser
```

Đây chính là hướng **DDD + Clean Architecture** mà chúng ta sẽ xây ở phần cuối.

---

# 15. Bài tập thực hành

## Bài 1 — Kiểm tra Response

Viết chương trình:

```text
GET https://httpbin.org/get
```

in ra:

```text
Status:
URL:
Content-Type:
Body:
```

---

## Bài 2 — JSON

Gửi:

```python
params={
    "name": "python",
    "page": 5,
}
```

Sau đó:

```python
data = response.json()
```

in:

```text
URL:
Args:
```

---

## Bài 3 — HTML

GET:

```text
https://example.com
```

Sau đó lấy:

```python
response.text
```

và dùng:

```python
HTMLParser
```

để lấy:

```text
<title>
```

---

## Bài 4 — Phân loại Response

Viết:

```python
def inspect_response(response):
    ...
```

Nếu:

```text
200 → SUCCESS
404 → NOT FOUND
403 → FORBIDDEN
429 → RATE LIMITED
500–599 → SERVER ERROR
```

---

# 16. Tóm tắt Buổi 3

Bạn cần nhớ 6 thành phần này:

```python
response.status_code
response.url
response.headers
response.text
response.content
response.json()
```

Trong Novel Crawler:

```text
response.status_code
        │
        └── quyết định request thành công/thất bại

response.text
        │
        └── HTML → selectolax → Parser

response.content
        │
        └── image/pdf/binary

response.json()
        │
        └── JSON API
```

Và nguyên tắc kiến trúc:

> **Fetcher lấy Response — Parser xử lý nội dung.**

Buổi tiếp theo theo roadmap là **Buổi 4 — Headers trong `primp`**, sau đó **Buổi 5 — Query Parameters**.
