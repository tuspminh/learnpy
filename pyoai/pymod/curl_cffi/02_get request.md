# Buổi 2 — GET Request chuyên sâu với `curl_cffi`

Hôm nay ta tập trung vào **GET request** và 4 thứ bạn sẽ dùng liên tục trong Novel Crawler:

```text
URL
Query Parameters
Headers
User-Agent
```

Mục tiêu cuối buổi:

```text
curl_cffi
    ↓
GET Request
    ├── URL
    ├── params
    ├── headers
    └── User-Agent
```

---

## 1. GET request cơ bản

```python
from curl_cffi import requests


response = requests.get(
    "https://example.com"
)

print(response.status_code)
print(response.text)
```

Tương đương về ý tưởng với:

```text
GET https://example.com
```

---

# 2. Query Parameters

Giả sử ta cần request:

```text
https://example.com/search?q=python&page=2
```

Không nên tự nối chuỗi:

```python
url = "https://example.com/search?q=python&page=2"
```

Mà dùng `params`:

```python
from curl_cffi import requests


response = requests.get(
    "https://example.com/search",
    params={
        "q": "python",
        "page": 2,
    },
)

print(response.url)
```

Ý tưởng:

```text
params
   ↓
{"q": "python", "page": 2}
   ↓
GET
   ↓
/search?q=python&page=2
```

---

# 3. Vì sao `params` quan trọng với crawler?

Ví dụ website truyện có:

```text
https://example.com/truyen?page=1
https://example.com/truyen?page=2
https://example.com/truyen?page=3
```

Ta có thể viết:

```python
from curl_cffi import requests


BASE_URL = "https://example.com/truyen"


for page in range(1, 4):
    response = requests.get(
        BASE_URL,
        params={"page": page},
        timeout=10,
    )

    print(response.url)
```

Kết quả logic:

```text
https://example.com/truyen?page=1
https://example.com/truyen?page=2
https://example.com/truyen?page=3
```

Đây chính là nền tảng cho **pagination crawler**.

---

# 4. Nhiều query parameters

Ví dụ:

```text
/search?q=python&page=2&sort=newest
```

Code:

```python
response = requests.get(
    "https://example.com/search",
    params={
        "q": "python",
        "page": 2,
        "sort": "newest",
    },
)
```

Không cần tự xử lý:

```python
"?q=" + ...
```

hay:

```python
"&page=" + ...
```

`curl_cffi` sẽ encode query parameters cho request.

---

# 5. Query parameter có Unicode

Ví dụ:

```python
response = requests.get(
    "https://example.com/search",
    params={
        "q": "tiên hiệp",
    },
)
```

Không nên tự:

```python
url = "https://example.com/search?q=tiên hiệp"
```

Việc encode URL nên giao cho HTTP client.

Điều này đặc biệt hữu ích với crawler tiếng Việt.

---

# 6. Query parameter lặp lại

Có những API sử dụng:

```text
?tag=python&tag=crawler&tag=http
```

Ta có thể truyền dạng list/tuple:

```python
response = requests.get(
    "https://example.com/search",
    params=[
        ("tag", "python"),
        ("tag", "crawler"),
        ("tag", "http"),
    ],
)
```

Đây là một pattern quan trọng khi làm việc với query string phức tạp.

---

# 7. Headers

GET request có thể gửi HTTP headers:

```python
response = requests.get(
    "https://example.com",
    headers={
        "Accept": "text/html",
    },
)
```

Ví dụ crawler:

```python
headers = {
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
}

response = requests.get(
    "https://example.com",
    headers=headers,
)
```

---

# 8. User-Agent

Đây là một header đặc biệt quan trọng đối với crawler.

Ví dụ:

```python
headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    "https://example.com",
    headers=headers,
)
```

Ta có thể kiểm tra server nhận được gì bằng một HTTP inspection service.

Ví dụ:

```python
from curl_cffi import requests


headers = {
    "User-Agent": "MyNovelCrawler/1.0"
}

response = requests.get(
    "https://httpbin.org/headers",
    headers=headers,
)

print(response.text)
```

---

# 9. Không nên hard-code User-Agent trong Fetcher

Đây là điểm bắt đầu liên quan tới kiến trúc của project.

Không nên:

```python
class Fetcher:

    def fetch(self, url):
        return requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 ..."
            },
        )
```

Vì sau này bạn muốn:

```text
UserAgentProvider
       ↓
   Fetcher
```

Ví dụ:

```python
class UserAgentProvider:

    def get(self) -> str:
        ...
```

Fetcher:

```python
class Fetcher:

    def __init__(self, user_agent_provider):
        self._user_agent_provider = user_agent_provider

    def fetch(self, url):
        user_agent = self._user_agent_provider.get()

        return requests.get(
            url,
            headers={
                "User-Agent": user_agent,
            },
        )
```

Đây chính là **Dependency Injection** mà bạn đã học trong Fetcher.

---

# 10. `impersonate` — điểm rất đặc biệt của `curl_cffi`

Đây là một trong những lý do chính để dùng `curl_cffi`.

Ví dụ:

```python
from curl_cffi import requests


response = requests.get(
    "https://example.com",
    impersonate="chrome",
)

print(response.status_code)
```

Thay vì chỉ thay:

```text
User-Agent
```

`curl_cffi` có thể mô phỏng nhiều đặc điểm HTTP/TLS của browser tương ứng.

Điểm này khác với:

```python
requests
```

và cũng là phần chúng ta sẽ học kỹ ở **Phần III**.

Hiện tại chỉ cần nhớ:

```python
impersonate="chrome"
```

không đơn giản chỉ có nghĩa:

```text
User-Agent = Chrome
```

Nó liên quan tới **TLS/browser fingerprinting**.

---

# 11. Kết hợp `params` + `headers` + `timeout`

Đây là một request thực tế hơn:

```python
from curl_cffi import requests


url = "https://example.com/search"

params = {
    "q": "python",
    "page": 2,
}

headers = {
    "User-Agent": "MyNovelCrawler/1.0",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "vi-VN,vi;q=0.9",
}

response = requests.get(
    url,
    params=params,
    headers=headers,
    timeout=10,
)

print("Status:", response.status_code)
print("URL:", response.url)
print("Length:", len(response.content))
```

Ta đang có:

```text
                    GET
                     │
       ┌─────────────┼─────────────┐
       ↓             ↓             ↓
      URL          params        headers
       │             │             │
       └─────────────┼─────────────┘
                     ↓
                 curl_cffi
                     ↓
                  Response
```

---

# 12. Một Fetcher tối giản

Bây giờ bắt đầu chuyển từ học library sang architecture.

```python
from curl_cffi import requests


class Fetcher:

    def fetch(self, url: str) -> str:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "MyNovelCrawler/1.0",
            },
        )

        response.raise_for_status()

        return response.text


def main():
    fetcher = Fetcher()

    html = fetcher.fetch(
        "https://example.com"
    )

    print(html[:500])


if __name__ == "__main__":
    main()
```

Đây **chưa phải production Fetcher**.

Chúng ta cố tình chưa đưa vào:

```text
Proxy
Retry
User-Agent rotation
Cookie
Session
Error mapping
Proxy health check
Logging
Rate limiting
```

Các phần đó sẽ được xây từng bước.

---

# 13. Một lỗi kiến trúc cần tránh

Đừng viết:

```python
def fetch(url):
    response = requests.get(
        url,
        params={...},
        headers={...},
        timeout=10,
        proxies={...},
        impersonate="chrome",
    )
```

rồi vài trăm dòng sau:

```python
requests.get(...)
```

```python
requests.get(...)
```

```python
requests.get(...)
```

Kết quả là toàn project phụ thuộc trực tiếp vào `curl_cffi`.

Mục tiêu cuối cùng của chúng ta là:

```text
Application
     │
     ▼
 HttpClient Interface
     │
     ▼
CurlCffiHttpClient
     │
     ▼
 curl_cffi
```

Ví dụ:

```python
from abc import ABC, abstractmethod


class HttpClient(ABC):

    @abstractmethod
    def get(self, url: str):
        pass
```

Infrastructure:

```python
from curl_cffi import requests


class CurlCffiHttpClient(HttpClient):

    def get(self, url: str):
        return requests.get(
            url,
            timeout=10,
        )
```

Đây mới là hướng phù hợp với **Clean Architecture + DDD + SOLID** của Novel Crawler.

---

# 14. So sánh với `httpx` bạn đã học

Bạn đã học `httpx` trước đó nên cần hình thành mental model:

```text
httpx
    requests.get()
          ↓
       Response
```

và:

```text
curl_cffi
    requests.get()
          ↓
       Response
```

API nhìn khá quen thuộc:

```python
response = requests.get(
    url,
    params=params,
    headers=headers,
    timeout=10,
)
```

Nhưng `curl_cffi` có thêm những khả năng đặc trưng như:

```python
impersonate="chrome"
```

và nền tảng bên dưới là `libcurl`.

**Không nên kết luận ngay rằng `curl_cffi` luôn tốt hơn `httpx`.** Hai thư viện có mục tiêu và trade-off khác nhau. Phần so sánh sâu sẽ để ở **Buổi 28**.

---

# Bài tập Buổi 2

Viết chương trình:

```text
lesson02.py
```

Yêu cầu:

### 1. GET

```text
https://httpbin.org/get
```

### 2. Query

Gửi:

```text
name = python
page = 2
category = crawler
```

### 3. Headers

Gửi:

```text
User-Agent = MyNovelCrawler/1.0
Accept = application/json
```

### 4. In ra

```text
Status
Final URL
Content-Type
Response body
```

Khung code:

```python
from curl_cffi import requests


def main():
    response = requests.get(
        "https://httpbin.org/get",
        params={
            "name": "python",
            "page": 2,
            "category": "crawler",
        },
        headers={
            "User-Agent": "MyNovelCrawler/1.0",
            "Accept": "application/json",
        },
        timeout=10,
    )

    print("Status:", response.status_code)
    print("URL:", response.url)
    print("Content-Type:", response.headers.get("content-type"))
    print(response.text)


if __name__ == "__main__":
    main()
```

## Sau Buổi 2 cần nắm chắc

```text
requests.get()
    │
    ├── url
    ├── params
    ├── headers
    ├── timeout
    │
    └── impersonate
             ↓
         Response
             ├── status_code
             ├── headers
             ├── text
             └── content
```

**Buổi 3:** `Response` chuyên sâu — status, headers, cookies, encoding, JSON, redirect, `ok`, `reason`, `url`, và cách biến `curl_cffi.Response` thành một `HttpResponse` sạch để đưa vào kiến trúc Fetcher của Novel Crawler.
