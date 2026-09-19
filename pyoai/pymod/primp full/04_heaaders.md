# Buổi 3 — Headers trong `primp`

Ở buổi 2, chúng ta đã học:

```python
client.get(
    url,
    params={
        "page": 2,
    },
)
```

Hôm nay học **HTTP Headers**. Đây là phần cực kỳ quan trọng đối với crawler vì server thường dựa vào headers để biết request đến từ đâu và client đang muốn nhận dữ liệu kiểu gì.

---

# 1. HTTP Headers là gì?

Một HTTP request có thể hình dung:

```text
Request
│
├── Method
│     GET
│
├── URL
│     https://example.com/
│
├── Headers
│     User-Agent
│     Accept
│     Referer
│     ...
│
└── Body
```

Ví dụ request:

```text
GET /truyen?page=2 HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
Accept: text/html
```

Trong `primp`:

```python
response = client.get(
    url,
    headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html",
    },
)
```

---

# 2. Request Header cơ bản

Code đầy đủ:

```python
import primp


def main():
    client = primp.Client()

    response = client.get(
        "https://httpbin.org/headers",
        headers={
            "User-Agent": "MyCrawler/1.0",
            "Accept": "text/html",
        },
    )

    print("Status:", response.status_code)
    print(response.text)


if __name__ == "__main__":
    main()
```

`httpbin` sẽ trả lại những headers mà server nhận được.

---

# 3. `User-Agent`

Một trong những header quan trọng nhất:

```python
headers = {
    "User-Agent": "MyCrawler/1.0",
}
```

Ví dụ browser:

```text
Mozilla/5.0 ...
```

Nhưng cần phân biệt:

```text
User-Agent
    ↓
chỉ là một HTTP header
```

với:

```text
Browser impersonation
    ↓
mô phỏng nhiều đặc điểm của browser
```

Đây là lý do ở các buổi sau chúng ta sẽ không chỉ đơn giản:

```python
headers = {
    "User-Agent": "Chrome..."
}
```

mà sẽ học:

```python
primp.Client(
    impersonate="chrome_146"
)
```

---

# 4. `Accept`

Cho server biết client ưu tiên loại nội dung nào.

Ví dụ:

```python
headers = {
    "Accept": "text/html",
}
```

Hoặc:

```python
headers = {
    "Accept": "application/json",
}
```

Crawler HTML:

```python
response = client.get(
    url,
    headers={
        "Accept": "text/html",
    },
)
```

API:

```python
response = client.get(
    url,
    headers={
        "Accept": "application/json",
    },
)
```

---

# 5. `Accept-Language`

Ví dụ:

```python
headers = {
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
}
```

Server có thể sử dụng header này để lựa chọn ngôn ngữ phản hồi.

Ví dụ:

```text
vi-VN
vi
en
```

Trong crawler website truyện Việt Nam, đôi khi đây là header hữu ích.

---

# 6. `Referer`

Ví dụ người dùng đi:

```text
listing
   ↓
novel detail
   ↓
chapter
```

Request chapter có thể có:

```python
headers = {
    "Referer": "https://example.com/truyen/abc",
}
```

Request:

```python
response = client.get(
    "https://example.com/truyen/abc/chuong-1",
    headers={
        "Referer": "https://example.com/truyen/abc",
    },
)
```

**Lưu ý:** `Referer` không phải lúc nào cũng cần và không nên tùy tiện giả mạo để vượt cơ chế kiểm soát của website. Ta sẽ dùng nó chủ yếu để hiểu HTTP semantics và các trường hợp website yêu cầu context hợp lệ.

---

# 7. Nhiều headers

Có thể truyền một dictionary:

```python
headers = {
    "User-Agent": "MyCrawler/1.0",
    "Accept": "text/html",
    "Accept-Language": "vi-VN,vi;q=0.9",
    "Referer": "https://example.com/",
}
```

Sau đó:

```python
response = client.get(
    url,
    headers=headers,
)
```

Ví dụ hoàn chỉnh:

```python
import primp


def main():
    client = primp.Client()

    headers = {
        "User-Agent": "NovelCrawler/1.0",
        "Accept": "text/html",
        "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
    }

    response = client.get(
        "https://httpbin.org/headers",
        headers=headers,
    )

    print(response.text)


if __name__ == "__main__":
    main()
```

---

# 8. Default Headers của Client

Nếu mọi request đều sử dụng cùng một header, ta không muốn viết:

```python
client.get(url1, headers=headers)
client.get(url2, headers=headers)
client.get(url3, headers=headers)
```

liên tục.

Thay vào đó, có thể cấu hình client với headers mặc định theo API của `primp`.

Ví dụ:

```python
import primp


def main():
    client = primp.Client(
        headers={
            "Accept-Language": "vi-VN,vi;q=0.9",
        }
    )

    response = client.get(
        "https://httpbin.org/headers"
    )

    print(response.text)


if __name__ == "__main__":
    main()
```

Tư duy:

```text
Client
│
├── default headers
│
├── Request 1
├── Request 2
├── Request 3
└── Request 4
```

---

# 9. Default Header + Request Header

Đây là pattern rất quan trọng.

Giả sử:

```python
client = primp.Client(
    headers={
        "Accept-Language": "vi-VN,vi;q=0.9",
    }
)
```

Một request riêng có:

```python
response = client.get(
    url,
    headers={
        "Accept": "application/json",
    },
)
```

Conceptually:

```text
Client defaults
       +
Request-specific headers
       ↓
Final request headers
```

Do đó nên phân biệt:

### Header ổn định

```text
Accept-Language
```

### Header thay đổi theo request

```text
Referer
Accept
Authorization
```

---

# 10. Header không phải tất cả

Đây là phần quan trọng nhất của buổi hôm nay.

Giả sử:

```python
headers = {
    "User-Agent": "Mozilla/5.0 Chrome..."
}
```

Ta **không thể kết luận**:

```text
"Request này hoàn toàn giống Chrome."
```

Bởi HTTP client còn có nhiều đặc điểm khác.

Có thể hình dung:

```text
Browser
│
├── HTTP headers
├── TLS
├── HTTP version
├── connection behavior
├── compression
└── other protocol characteristics
```

Còn:

```python
headers={
    "User-Agent": "Chrome..."
}
```

chỉ thay đổi một phần.

---

# 11. Đây chính là lý do học `primp`

`primp` có option:

```python
impersonate="chrome_146"
```

Ví dụ:

```python
import primp


def main():
    client = primp.Client(
        impersonate="chrome_146"
    )

    response = client.get(
        "https://tls.peet.ws/api/all"
    )

    print(response.text)


if __name__ == "__main__":
    main()
```

Ở đây:

```text
headers thủ công
       │
       ▼
chỉ kiểm soát headers

impersonate
       │
       ▼
primp cố gắng mô phỏng
browser profile tương ứng
```

Các profile impersonation cụ thể phụ thuộc phiên bản `primp`; vì vậy khi chúng ta tới phần chuyên sâu, mình sẽ kiểm tra danh sách profile của phiên bản đang dùng thay vì học thuộc một danh sách có thể thay đổi.

---

# 12. Header rotation — đừng nhầm với browser rotation

Trong crawler, bạn có thể có:

```python
USER_AGENTS = [
    "...",
    "...",
    "...",
]
```

và chọn:

```python
user_agent = random.choice(USER_AGENTS)
```

Nhưng:

```text
UA rotation
```

khác:

```text
Browser profile rotation
```

Ví dụ:

```text
UA rotation
    ↓
thay đổi User-Agent

Browser profile
    ↓
thay đổi toàn bộ profile impersonation
```

Đây là lý do kiến trúc Fetcher sau này nên có abstraction:

```text
BrowserProfile
      │
      ▼
PrimpClientFactory
      │
      ▼
PrimpFetcher
```

thay vì nhét:

```python
random.choice(USER_AGENTS)
```

vào mọi nơi.

---

# 13. Header cho Novel Crawler

Một cấu hình ban đầu có thể là:

```python
DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
}
```

Sau đó:

```python
import primp


class PrimpFetcher:

    def __init__(self):
        self.client = primp.Client(
            headers={
                "Accept": (
                    "text/html,"
                    "application/xhtml+xml"
                ),
                "Accept-Language": (
                    "vi-VN,vi;q=0.9,en;q=0.8"
                ),
            }
        )

    def fetch(self, url: str):
        return self.client.get(url)
```

Nhưng **chưa nên coi đây là Fetcher production**.

Chúng ta còn phải giải quyết:

```text
Timeout
Exception
Proxy
Retry
Cookies
Impersonation
Error classification
Logging
```

---

# 14. Một nguyên tắc thiết kế quan trọng

Không nên làm:

```python
class NovelParser:

    def parse(self, url):
        client = primp.Client(...)
        response = client.get(url)
```

Parser không nên biết `primp`.

Kiến trúc:

```text
                 Application
                      │
                      ▼
                   Fetcher
                      │
                      ▼
                PrimpFetcher
                      │
                      ▼
                   primp
                      │
                      ▼
                   HTTP
                      │
                      ▼
                   HTML
                      │
                      ▼
                   Parser
```

Parser chỉ nhận:

```python
html: str
```

Ví dụ:

```python
html = fetcher.fetch(url)

novel = parser.parse(html)
```

Đây chính là **Dependency Inversion**.

Sau này nếu muốn đổi:

```text
primp → httpx
```

thì Parser không phải sửa.

---

# 15. Thực hành

## Bài 1 — Headers

Chạy:

```python
import primp


client = primp.Client()

response = client.get(
    "https://httpbin.org/headers",
    headers={
        "User-Agent": "NovelCrawler/1.0",
        "Accept": "text/html",
        "Accept-Language": "vi-VN",
    },
)

print(response.text)
```

Quan sát server nhận được gì.

---

## Bài 2 — Default headers

Tạo:

```python
client = primp.Client(
    headers={
        "Accept-Language": "vi-VN",
    }
)
```

Sau đó thực hiện **hai request**.

Quan sát xem header mặc định xuất hiện như thế nào.

---

## Bài 3 — Request-specific header

Tạo:

```python
client = primp.Client(
    headers={
        "Accept-Language": "vi-VN",
    }
)
```

Request:

```python
response = client.get(
    "https://httpbin.org/headers",
    headers={
        "X-Crawler-Page": "listing",
    },
)
```

Kiểm tra kết quả.

Mục tiêu:

```text
default header
      +
request header
      ↓
final request
```

---

## Bài 4 — So sánh

Thử hai client:

```python
client1 = primp.Client(
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)
```

và:

```python
client2 = primp.Client(
    impersonate="chrome_146"
)
```

Gửi request tới:

```text
https://tls.peet.ws/api/all
```

Sau đó lưu output của hai request lại.

**Chưa cần phân tích TLS fingerprint.** Ta sẽ dành riêng phần đó cho các buổi **21–30 Browser Impersonation**.

---

## Tóm tắt Buổi 3

```text
primp.Client
    │
    ├── headers={}
    │
    └── impersonate=
```

Headers:

```text
User-Agent
Accept
Accept-Language
Referer
Authorization
...
```

Và cần nhớ:

```text
User-Agent ≠ Browser fingerprint
```

```text
headers
   ↓
HTTP-level metadata

impersonate
   ↓
browser profile
```

### Chuỗi kiến thức hiện tại

```text
01 Client + Response
        ↓
02 GET + params
        ↓
03 Headers  ← hôm nay
        ↓
04 POST + JSON
        ↓
05 Cookies
        ↓
06 Form Data
        ↓
...
14 Proxy
        ↓
21 Browser Impersonation
```

**Buổi 4** chúng ta sẽ học **POST + JSON trong `primp`**, sau đó phân biệt thật rõ `json=`, `data=`, request body và `Content-Type`.
