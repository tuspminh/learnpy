Được. Chúng ta sẽ học **`primp` theo kiểu từng bước, có hệ thống**, và mình sẽ gắn trực tiếp với mục tiêu **Novel Crawler** của bạn.

`primp` hiện là HTTP client Python viết dựa trên Rust, nổi bật ở khả năng **browser impersonation** — mô phỏng fingerprint của các trình duyệt như Chrome, Firefox, Safari, Edge — và có cả API sync lẫn async. Phiên bản mới nhất hiện tại trên PyPI là **2.0.1**, phát hành ngày 13/09/2026, yêu cầu Python ≥ 3.10. ([PyPI][1])

# Roadmap học PRIMP

Mình đề xuất học theo 5 phần:

```text
PHẦN I — CƠ BẢN
01. Cài đặt + Client
02. GET request
03. Response
04. Headers
05. Query Parameters
06. POST
07. JSON
08. Form Data
09. Cookies
10. Redirect

PHẦN II — HTTP CLIENT
11. Timeout
12. Exception
13. Authentication
14. Proxy
15. SSL / Verify
16. Session / Connection Reuse
17. Default Headers
18. Default Params
19. Request Options
20. Client Lifecycle

PHẦN III — BROWSER IMPERSONATION
21. Vì sao cần impersonation
22. Chrome fingerprint
23. Firefox / Safari / Edge
24. impersonate_os
25. TLS fingerprint
26. HTTP/2
27. Headers + fingerprint
28. Fingerprint thực tế
29. So sánh httpx vs primp
30. Xây BrowserClient

PHẦN IV — ASYNC + CRAWLER
31. AsyncClient
32. async GET
33. Concurrent Requests
34. Semaphore
35. Timeout + Retry
36. Proxy Pool
37. User-Agent / Browser Profile Pool
38. Rate Limiting
39. Fetcher Architecture
40. Async Novel Fetcher

PHẦN V — NOVEL CRAWLER
41. Request Model
42. Response Model
43. Fetcher Interface
44. PrimpFetcher
45. Retry Policy
46. Proxy Strategy
47. Browser Profile Strategy
48. Error Classification
49. Observability / Logging
50. Production Fetcher
```

Đặc biệt, **không nên học `primp` chỉ như một thư viện gửi GET/POST**. Với project crawler của bạn, phần quan trọng nhất sẽ là:

```text
                 Novel Crawler
                       │
                       ▼
                 Fetcher Interface
                       │
                       ▼
                  PrimpFetcher
                       │
            ┌──────────┼──────────┐
            ▼          ▼          ▼
         Proxy      Browser     Retry
                     Profile
                       │
                       ▼
                  primp.Client
                       │
                       ▼
                    HTTP
```

---

# Buổi 1 — Cài đặt và `primp.Client`

## 1. PRIMP là gì?

Có thể hiểu đơn giản:

```text
requests
    │
    └── HTTP client đơn giản

httpx
    │
    ├── sync
    ├── async
    ├── HTTP/2
    └── modern API

primp
    │
    ├── sync
    ├── async
    ├── Rust backend
    └── browser impersonation
```

Điểm đáng chú ý của `primp` là:

```python
primp.Client(
    impersonate="chrome_146"
)
```

Thay vì chỉ gửi một HTTP request thông thường, client có thể mô phỏng đặc điểm giao tiếp của browser profile được hỗ trợ. PyPI hiện liệt kê các profile Chrome, Safari, Edge, Firefox, Opera và một số OS profile. ([PyPI][1])

---

# 2. Cài đặt

Nếu dùng `pip`:

```bash
pip install -U primp
```

Hoặc với `uv`:

```bash
uv add primp
```

Kiểm tra:

```bash
python -c "import primp; print(primp)"
```

PRIMP hiện yêu cầu:

```text
Python >= 3.10
```

và có wheel cho nhiều nền tảng phổ biến. ([PyPI][1])

---

# 3. Request đầu tiên

Tạo:

```text
lesson01.py
```

Code hoàn chỉnh:

```python
import primp


def main():
    client = primp.Client()

    response = client.get("https://httpbin.org/get")

    print("Status:", response.status_code)
    print("URL:", response.url)
    print("Headers:")
    print(response.headers)
    print()
    print("Body:")
    print(response.text)


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python lesson01.py
```

Ta có:

```text
Client
   │
   │ GET
   ▼
https://httpbin.org/get
   │
   ▼
Response
   ├── status_code
   ├── url
   ├── headers
   └── text
```

---

# 4. `Client` là gì?

Đây là object đại diện cho HTTP client.

```python
client = primp.Client()
```

Sau đó dùng:

```python
client.get(...)
client.post(...)
client.put(...)
client.patch(...)
client.delete(...)
client.head(...)
client.options(...)
```

Ví dụ:

```python
response = client.get(
    "https://httpbin.org/get"
)
```

Không nên hiểu:

```python
client.get()
```

là "tải một URL".

Đúng hơn:

```text
Client
  ↓
Request
  ↓
HTTP Server
  ↓
Response
```

---

# 5. Response

Sau:

```python
response = client.get(
    "https://httpbin.org/get"
)
```

`response` là object chứa kết quả HTTP.

Một số thuộc tính quan trọng:

```python
response.status_code
response.url
response.headers
response.text
response.content
```

Ví dụ:

```python
print(response.status_code)
```

Có thể nhận:

```text
200
```

---

## `text`

```python
print(response.text)
```

Là nội dung response dưới dạng `str`.

Ví dụ:

```html
<html>
    <body>
        Hello
    </body>
</html>
```

Rất phù hợp với crawler của bạn:

```text
HTTP response
      ↓
response.text
      ↓
selectolax
      ↓
Parser
```

---

# 6. `content`

Khác với:

```python
response.text
```

thì:

```python
response.content
```

là bytes.

Ví dụ:

```python
content = response.content

print(type(content))
```

Kết quả:

```text
<class 'bytes'>
```

Điều này quan trọng khi tải:

```text
ảnh
PDF
ebook
file binary
```

Ví dụ crawler:

```python
response = client.get(image_url)

image_data = response.content

with open("cover.jpg", "wb") as f:
    f.write(image_data)
```

---

# 7. Status code

HTTP status code cực kỳ quan trọng trong Fetcher.

Ví dụ:

```python
response = client.get(url)

print(response.status_code)
```

Một số mã cần nhớ:

```text
200 → OK

301 → Moved Permanently
302 → Found

400 → Bad Request
401 → Unauthorized
403 → Forbidden
404 → Not Found
429 → Too Many Requests

500 → Internal Server Error
502 → Bad Gateway
503 → Service Unavailable
504 → Gateway Timeout
```

Trong crawler, chúng ta sẽ không xử lý tất cả giống nhau.

Ví dụ:

```text
200
 ↓
SUCCESS

404
 ↓
NOT_FOUND

403
 ↓
BLOCKED

429
 ↓
RATE_LIMITED

500
 ↓
SERVER_ERROR

timeout
 ↓
NETWORK_ERROR
```

Đây sẽ trở thành nền tảng cho phần:

```text
Retry Policy
Error Classification
```

sau này.

---

# 8. Browser impersonation

Đây là phần làm `primp` đặc biệt đáng học.

Ví dụ:

```python
import primp


client = primp.Client(
    impersonate="chrome_146"
)

response = client.get(
    "https://tls.peet.ws/api/all"
)

print(response.text)
```

Đây cũng là ví dụ được PyPI sử dụng trong quick start hiện tại. ([PyPI][1])

`tls.peet.ws` là một endpoint rất hữu ích để **quan sát thông tin TLS/HTTP mà server nhìn thấy**, nên chúng ta sẽ dùng nó trong các buổi sau để hiểu impersonation.

---

# 9. `impersonate` không đơn giản là đổi User-Agent

Đây là điểm **rất quan trọng**.

Nhiều người nghĩ:

```python
headers = {
    "User-Agent": "Mozilla/5.0 ..."
}
```

là đã giả Chrome.

Không hẳn.

Browser fingerprint có thể liên quan tới nhiều tầng:

```text
                    Browser
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Headers        TLS          HTTP/2
                       │
                       ▼
                  Fingerprint
```

Vì vậy:

```python
User-Agent = Chrome
```

không đồng nghĩa:

```text
TLS fingerprint = Chrome
```

PRIMP tập trung vào việc impersonate browser ở mức sâu hơn header đơn thuần. ([PyPI][1])

**Nhưng:** impersonation không đảm bảo một website sẽ cho phép truy cập; các hệ thống chống bot có thể sử dụng nhiều tín hiệu khác nhau.

---

# 10. Một ví dụ phù hợp với Novel Crawler

Giả sử:

```python
import primp


def fetch(url: str) -> str:
    client = primp.Client(
        impersonate="chrome_146"
    )

    response = client.get(url)

    if response.status_code != 200:
        raise RuntimeError(
            f"HTTP {response.status_code}: {url}"
        )

    return response.text


def main():
    html = fetch(
        "https://example.com"
    )

    print(html[:500])


if __name__ == "__main__":
    main()
```

Nhưng **đây chưa phải kiến trúc cuối cùng**.

Sau này chúng ta sẽ chuyển thành:

```text
Application
    │
    ▼
NovelFetchUseCase
    │
    ▼
Fetcher Interface
    │
    ▼
PrimpFetcher
    │
    ├── Primp Client
    ├── Proxy
    ├── Browser Profile
    ├── Retry
    ├── Timeout
    └── Logging
```

Ví dụ interface:

```python
from abc import ABC, abstractmethod


class Fetcher(ABC):

    @abstractmethod
    def fetch(self, url: str) -> str:
        ...
```

Sau đó:

```python
class PrimpFetcher(Fetcher):

    def fetch(self, url: str) -> str:
        ...
```

Điều này khớp với Fetcher architecture mà bạn đã học trước đó với `httpx`: **Parser không cần biết HTTP client bên dưới là `httpx` hay `primp`.**

---

# 11. Bài tập Buổi 1

### Bài 1

Viết chương trình:

```text
lesson01_1.py
```

gọi:

```text
https://httpbin.org/get
```

và in:

```text
Status
URL
Headers
Body
```

---

### Bài 2

Thử:

```python
response = client.get(
    "https://httpbin.org/status/404"
)
```

và kiểm tra:

```python
response.status_code
```

---

### Bài 3

Thử:

```python
response = client.get(
    "https://httpbin.org/bytes/100"
)
```

Sau đó:

```python
print(type(response.text))
print(type(response.content))
```

Quan sát sự khác nhau.

---

### Bài 4 — quan trọng

Thử:

```python
client = primp.Client(
    impersonate="chrome_146"
)

response = client.get(
    "https://tls.peet.ws/api/all"
)

print(response.text)
```

Không cần hiểu hết output ở thời điểm này.

Mục tiêu chỉ là **thấy được browser impersonation hoạt động như một khái niệm riêng**.

---

## Sau Buổi 1

Ta sẽ đi tiếp:

```text
Buổi 1  Client + Response
   ↓
Buổi 2  GET + Query Parameters
   ↓
Buổi 3  Headers
   ↓
Buổi 4  POST + JSON
   ↓
Buổi 5  Cookies
   ↓
...
Buổi 14 Proxy
   ↓
Buổi 21 Browser Impersonation
   ↓
Buổi 31 AsyncClient
   ↓
Buổi 44 PrimpFetcher
```

Mình sẽ giữ cách dạy **code đầy đủ, chạy được ngay, giải thích từng thành phần**, và khi tới phần Fetcher sẽ nối trực tiếp `primp` vào kiến trúc **DDD + SOLID + Repository/Fetcher** của Novel Crawler của bạn.

[1]: https://pypi.org/project/primp/2.0.1/?utm_source=chatgpt.com "primp · PyPI"
