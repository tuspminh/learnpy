# 📘 Selectolax — Buổi 7: Selectolax + HTTPX

Hôm nay chúng ta ghép hai thứ đã học:

```text
HTTPX
  ↓
HTTP Response
  ↓
HTML
  ↓
Selectolax
  ↓
CSS Selector
  ↓
Extract data
```

Đây là bước chuyển từ **HTML parsing** sang **scraping thực tế**.

---

# 1. Kiến trúc đầu tiên

Ta không nên viết tất cả vào một function:

```python
def scrape(url):
    response = httpx.get(url)
    tree = HTMLParser(response.text)
    ...
```

Có thể làm như vậy để học, nhưng khi project lớn lên sẽ rất khó bảo trì.

Ta tách:

```text
Fetcher
   ↓
HTML
   ↓
Parser
   ↓
Data
```

Cụ thể:

```text
┌──────────────┐
│   HTTPX      │
│   Fetcher    │
└──────┬───────┘
       │
       │ HTML
       ▼
┌──────────────┐
│  Selectolax  │
│    Parser    │
└──────┬───────┘
       │
       │ dict / model
       ▼
     Data
```

Đây là kiến trúc chúng ta sẽ tiếp tục phát triển ở các buổi sau.

---

# 2. Cài đặt

Nếu dùng `uv`:

```bash
uv add httpx selectolax
```

Hoặc:

```bash
pip install httpx selectolax
```

Import:

```python
import httpx

from selectolax.parser import HTMLParser
```

---

# 3. Request cơ bản với HTTPX

```python
import httpx


response = httpx.get(
    "https://example.com"
)

print(response.status_code)
print(response.text)
```

Ta nhận được:

```text
HTTP Response
│
├── status_code
├── headers
├── text
├── content
└── url
```

---

# 4. Response → Selectolax

Đây là cầu nối quan trọng:

```python
response = httpx.get(
    "https://example.com"
)

html = response.text

tree = HTMLParser(html)
```

Sau đó:

```python
title = tree.css_first("title")

if title:
    print(title.text())
```

Pipeline:

```text
response.text
     ↓
HTMLParser(...)
     ↓
tree
     ↓
css_first()
```

---

# 5. Viết scraper tối giản

```python
import httpx
from selectolax.parser import HTMLParser


def scrape(url: str):
    response = httpx.get(url)

    tree = HTMLParser(response.text)

    title = tree.css_first("title")

    return title.text().strip() if title else None


print(scrape("https://example.com"))
```

Đây là scraper đầu tiên.

Nhưng production thì **chưa đủ tốt**.

---

# 6. Kiểm tra Status Code

Không nên parse HTML ngay.

Ví dụ server trả:

```text
404
```

thì:

```python
tree = HTMLParser(response.text)
```

không có nhiều ý nghĩa.

Ta nên:

```python
if response.status_code != 200:
    ...
```

HTTPX cung cấp:

```python
response.raise_for_status()
```

Ví dụ:

```python
response = httpx.get(url)

response.raise_for_status()

tree = HTMLParser(response.text)
```

Nếu:

```text
200
```

→ tiếp tục.

Nếu:

```text
404
500
403
...
```

→ HTTPX raise exception tương ứng.

---

# 7. `raise_for_status()`

Ví dụ:

```python
import httpx


try:
    response = httpx.get(url)
    response.raise_for_status()

except httpx.HTTPStatusError as exc:
    print(exc)
```

Điều này giúp parser không phải xử lý HTTP error.

---

# 8. Tách Fetcher

Đây là bước quan trọng.

```python
class HTTPFetcher:

    def fetch(self, url: str) -> str:
        response = httpx.get(url)

        response.raise_for_status()

        return response.text
```

Sử dụng:

```python
fetcher = HTTPFetcher()

html = fetcher.fetch(
    "https://example.com"
)
```

Fetcher chỉ quan tâm:

```text
URL
 ↓
HTTP
 ↓
HTML
```

Nó không biết:

```text
CSS selector
Article
Story
Database
```

---

# 9. Parser

Parser:

```python
class PageParser:

    def parse_title(self, html: str) -> str | None:
        tree = HTMLParser(html)

        node = tree.css_first("title")

        if node is None:
            return None

        return node.text().strip()
```

Sử dụng:

```python
fetcher = HTTPFetcher()
parser = PageParser()

html = fetcher.fetch(url)

title = parser.parse_title(html)

print(title)
```

Architecture:

```text
HTTPFetcher
     ↓
   HTML
     ↓
 PageParser
     ↓
   Data
```

---

# 10. Tại sao tách Fetcher và Parser?

Giả sử sau này bạn muốn test parser.

Không cần Internet.

Chỉ cần:

```python
html = """
<html>
<head>
    <title>Hello</title>
</head>
</html>
"""
```

Sau đó:

```python
parser = PageParser()

assert parser.parse_title(html) == "Hello"
```

Parser hoàn toàn độc lập với HTTP.

Đây là **separation of concerns**.

---

# 11. HTTPX Client

Không nên luôn luôn:

```python
httpx.get(...)
```

khi crawler có nhiều request.

Nên dùng:

```python
client = httpx.Client()
```

Ví dụ:

```python
import httpx


with httpx.Client() as client:

    response = client.get(
        "https://example.com"
    )

    response.raise_for_status()

    print(response.text)
```

---

# 12. Tại sao `Client` tốt hơn?

Crawler thường:

```text
URL 1
 ↓
URL 2
 ↓
URL 3
 ↓
URL 4
 ↓
URL 5
```

`Client` cho phép quản lý:

* connection pooling
* headers mặc định
* cookies
* timeout
* auth
* proxy
* transport

và các request có thể tái sử dụng connection.

---

# 13. HTTPFetcher sử dụng Client

```python
import httpx


class HTTPFetcher:

    def __init__(self):
        self.client = httpx.Client()

    def fetch(self, url: str) -> str:
        response = self.client.get(url)

        response.raise_for_status()

        return response.text

    def close(self):
        self.client.close()
```

Dùng:

```python
fetcher = HTTPFetcher()

try:
    html = fetcher.fetch(url)
finally:
    fetcher.close()
```

Tốt hơn nữa:

```python
with httpx.Client() as client:
    ...
```

---

# 14. Thiết kế Fetcher bằng Context Manager

Ta có thể:

```python
class HTTPFetcher:

    def __init__(self):
        self.client = httpx.Client()

    def fetch(self, url: str) -> str:
        response = self.client.get(url)
        response.raise_for_status()
        return response.text

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
```

Sử dụng:

```python
with HTTPFetcher() as fetcher:

    html = fetcher.fetch(url)
```

---

# 15. Headers

Một website có thể kiểm tra:

```text
User-Agent
Accept
Accept-Language
Referer
```

HTTPX:

```python
headers = {
    "User-Agent": "Mozilla/5.0",
}
```

Request:

```python
response = client.get(
    url,
    headers=headers,
)
```

---

# 16. Default Headers

Tốt hơn:

```python
class HTTPFetcher:

    def __init__(self):

        self.client = httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "text/html",
            }
        )
```

Mọi request của Client sẽ sử dụng headers mặc định đó.

---

# 17. Headers không phải "bypass anti-bot"

Cần phân biệt:

```text
User-Agent
```

với:

```text
Anti-bot bypass
```

User-Agent chỉ là metadata HTTP bình thường.

Không nên giả định:

```python
User-Agent = Chrome
```

là website sẽ cho phép crawler.

Website có thể còn kiểm tra:

* rate limit
* cookies
* IP
* JavaScript
* CAPTCHA
* session
* authentication

---

# 18. Timeout

Crawler không được phép chờ vô hạn.

Không nên:

```python
httpx.get(url)
```

trong crawler production mà không quan tâm timeout.

Có thể cấu hình:

```python
timeout = httpx.Timeout(
    10.0
)
```

Sau đó:

```python
client = httpx.Client(
    timeout=timeout
)
```

---

# 19. Timeout chi tiết

HTTPX cho phép phân biệt:

```python
timeout = httpx.Timeout(
    connect=5.0,
    read=10.0,
    write=10.0,
    pool=5.0,
)
```

Ý nghĩa:

```text
connect
    ↓
Kết nối server

read
    ↓
Đọc response

write
    ↓
Gửi request body

pool
    ↓
Chờ connection pool
```

Crawler thực tế rất nên hiểu phần này.

---

# 20. Xử lý Timeout

```python
try:
    response = client.get(url)

except httpx.TimeoutException:
    print("Request timeout")
```

HTTPX có exception hierarchy.

Ví dụ:

```text
httpx.HTTPError
│
├── RequestError
│   ├── ConnectError
│   ├── ReadError
│   └── TimeoutException
│
└── HTTPStatusError
```

Không cần nhớ hết ngay.

Quan trọng là biết:

```python
except httpx.HTTPError:
```

có thể bắt lỗi HTTPX tổng quát.

---

# 21. Retry

Giả sử:

```text
Request 1 → timeout
Request 2 → timeout
Request 3 → thành công
```

Crawler không nên lập tức bỏ URL.

Ta có thể retry.

Ví dụ đơn giản:

```python
import time
import httpx


def fetch(
    client: httpx.Client,
    url: str,
    retries: int = 3,
):
    for attempt in range(retries):

        try:
            response = client.get(url)

            response.raise_for_status()

            return response.text

        except httpx.HTTPError:

            if attempt == retries - 1:
                raise

            time.sleep(1)
```

---

# 22. Retry với exponential backoff

Không nên:

```python
time.sleep(1)
time.sleep(1)
time.sleep(1)
```

Có thể:

```text
attempt 1 → 1s
attempt 2 → 2s
attempt 3 → 4s
```

Code:

```python
delay = 2 ** attempt

time.sleep(delay)
```

Ví dụ:

```python
for attempt in range(retries):

    try:
        response = client.get(url)
        response.raise_for_status()
        return response.text

    except httpx.HTTPError:

        if attempt == retries - 1:
            raise

        time.sleep(2 ** attempt)
```

---

# 23. Nhưng không nên retry mọi HTTP status

Ví dụ:

```text
404 Not Found
```

Retry 10 lần thường vô nghĩa.

```text
403 Forbidden
```

Retry liên tục cũng không phải chiến lược tốt.

Trong crawler, cần phân biệt:

```text
Transient error
     ↓
Có thể retry

Permanent error
     ↓
Không retry
```

Ví dụ thường có thể xem xét retry:

```text
408
429
500
502
503
504
```

Nhưng policy cụ thể nên phụ thuộc website/API và header `Retry-After` nếu server cung cấp.

---

# 24. Kiểm tra status code thủ công

```python
response = client.get(url)

if response.status_code == 404:
    print("Not found")

elif response.status_code == 429:
    print("Rate limited")

elif response.status_code >= 500:
    print("Server error")

else:
    response.raise_for_status()
```

---

# 25. `response.text` vs `response.content`

Hai thứ này khác nhau.

### `response.text`

```python
html = response.text
```

Là:

```text
bytes → decode → str
```

Phù hợp với Selectolax.

### `response.content`

```python
data = response.content
```

Là:

```text
bytes
```

Phù hợp khi xử lý:

* binary
* image
* PDF
* file

---

# 26. Selectolax nhận HTML

Thông thường:

```python
tree = HTMLParser(
    response.text
)
```

Sau đó:

```python
title = tree.css_first("title")

if title:
    print(title.text())
```

---

# 27. Viết `Scraper`

Bây giờ kết hợp:

```python
class Scraper:

    def __init__(self, fetcher, parser):
        self.fetcher = fetcher
        self.parser = parser

    def scrape(self, url):
        html = self.fetcher.fetch(url)
        return self.parser.parse(html)
```

Parser:

```python
class PageParser:

    def parse(self, html):
        tree = HTMLParser(html)

        title = tree.css_first("title")

        return {
            "title": (
                title.text().strip()
                if title
                else None
            )
        }
```

Sử dụng:

```python
fetcher = HTTPFetcher()
parser = PageParser()

scraper = Scraper(
    fetcher,
    parser,
)

data = scraper.scrape(
    "https://example.com"
)

print(data)
```

---

# 28. Architecture

Đến đây:

```text
             URL
              │
              ▼
       ┌──────────────┐
       │ HTTPFetcher  │
       └──────┬───────┘
              │
             HTML
              │
              ▼
       ┌──────────────┐
       │ HTMLParser   │
       │ Selectolax   │
       └──────┬───────┘
              │
             Data
```

Và `Scraper` chỉ orchestration:

```text
Scraper
   │
   ├── Fetcher
   │
   └── Parser
```

Đây chính là hướng Clean Architecture / SOLID mà bạn đang học.

---

# 29. Article Scraper

Giờ áp dụng vào crawler bài viết.

```python
class ArticleParser:

    def parse(self, html: str) -> dict:
        tree = HTMLParser(html)

        title = tree.css_first("h1")
        content = tree.css_first(
            ".article-content"
        )

        return {
            "title": (
                title.text().strip()
                if title
                else None
            ),
            "content": (
                content.html
                if content
                else None
            ),
        }
```

Fetcher:

```python
class HTTPFetcher:

    def __init__(self):
        self.client = httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0",
            },
            timeout=10.0,
        )

    def fetch(self, url: str) -> str:
        response = self.client.get(url)
        response.raise_for_status()

        return response.text

    def close(self):
        self.client.close()
```

---

# 30. Full example

```python
import httpx

from selectolax.parser import HTMLParser


class HTTPFetcher:

    def __init__(self):
        self.client = httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0",
            },
            timeout=10.0,
        )

    def fetch(self, url: str) -> str:
        response = self.client.get(url)

        response.raise_for_status()

        return response.text

    def close(self):
        self.client.close()


class ArticleParser:

    def parse(self, html: str) -> dict:
        tree = HTMLParser(html)

        title = tree.css_first("h1")
        content = tree.css_first(
            ".article-content"
        )

        return {
            "title": (
                title.text().strip()
                if title
                else None
            ),
            "content": (
                content.html
                if content
                else None
            ),
        }


fetcher = HTTPFetcher()
parser = ArticleParser()

try:

    html = fetcher.fetch(
        "https://example.com/article"
    )

    article = parser.parse(html)

    print(article)

finally:
    fetcher.close()
```

Đây là một scraper thực sự, dù còn đơn giản.

---

# 31. Một cải tiến quan trọng: trả cả URL

Khi parser parse:

```python
{
    "title": "...",
    "content": "..."
}
```

ta có thể muốn:

```python
{
    "url": "...",
    "title": "...",
    "content": "..."
}
```

Nhưng URL là thông tin của Fetcher/request chứ không phải HTML.

Do đó có thể để `Scraper` thêm:

```python
data["url"] = url
```

Ví dụ:

```python
class Scraper:

    def scrape(self, url):
        html = self.fetcher.fetch(url)

        data = self.parser.parse(html)

        data["url"] = url

        return data
```

---

# 32. Đây là lý do không nên để Parser gọi HTTP

Nếu Parser làm:

```python
class ArticleParser:

    def parse(self, url):
        response = httpx.get(url)
```

thì:

```text
Parser
 ├── HTTP
 ├── HTML
 ├── Selectolax
 ├── Retry
 ├── Timeout
 └── Extraction
```

Nó trở thành **God Object**.

Còn:

```text
HTTPFetcher
    → HTTP

ArticleParser
    → HTML parsing

Scraper
    → orchestration
```

rõ ràng hơn nhiều.

---

# 33. Retry nên thuộc Fetcher

Đừng:

```python
ArticleParser
    ↓
retry HTTP
```

Parser không biết HTTP.

Nên:

```text
HTTPFetcher
 ├── timeout
 ├── headers
 ├── retry
 ├── status code
 └── HTTP errors

ArticleParser
 ├── Selectolax
 ├── selector
 └── extraction
```

---

# 34. Một Fetcher tốt hơn

Ta có thể bắt đầu:

```python
class HTTPFetcher:

    def __init__(
        self,
        timeout=10.0,
        retries=3,
    ):
        self.timeout = timeout
        self.retries = retries

        self.client = httpx.Client(
            timeout=timeout,
            headers={
                "User-Agent": "Mozilla/5.0",
            },
        )
```

Sau này sẽ mở rộng thành:

```text
HTTPFetcher
│
├── Client
├── Headers
├── Timeout
├── RetryPolicy
├── RateLimiter
├── Proxy
└── Logging
```

Đó chính là nền tảng crawler framework.

---

# 35. Bài tập Buổi 7

## Bài 1 — Fetcher

Viết:

```python
class HTTPFetcher:
    def fetch(self, url: str) -> str:
        ...
```

Yêu cầu:

* dùng `httpx.Client`
* timeout 10 giây
* User-Agent
* `raise_for_status()`

---

## Bài 2 — Parser

Viết:

```python
class PageParser:

    def parse(self, html: str) -> dict:
        ...
```

HTML:

```html
<html>
<head>
    <title>Hello Python</title>
</head>

<body>

    <h1>Python</h1>

    <div class="content">
        <p>Hello</p>
        <p>Selectolax</p>
    </div>

</body>
</html>
```

Kết quả:

```python
{
    "title": "Hello Python",
    "heading": "Python",
    "content": [
        "Hello",
        "Selectolax",
    ],
}
```

---

# 36. Bài 3 — Scraper

Thiết kế:

```python
class Scraper:

    def __init__(
        self,
        fetcher,
        parser,
    ):
        ...

    def scrape(self, url):
        ...
```

Pipeline:

```text
URL
 ↓
Fetcher
 ↓
HTML
 ↓
Parser
 ↓
dict
```

---

# 37. Bài 4 — Retry

Viết:

```python
fetch(
    url,
    retries=3,
)
```

với:

```text
attempt 1
 ↓
failure
 ↓ 1s

attempt 2
 ↓
failure
 ↓ 2s

attempt 3
 ↓
success
```

---

# 38. Bài 5 — Status Code

Thiết kế logic:

```text
2xx → parse

404 → không retry

429 → retry

5xx → retry

timeout → retry
```

Đừng retry vô hạn.

---

# 39. Bài 6 — Mini Project

Xây:

```text
simple_scraper/
│
├── fetcher.py
├── parser.py
├── scraper.py
└── main.py
```

### `fetcher.py`

```python
HTTPFetcher
```

### `parser.py`

```python
ArticleParser
```

### `scraper.py`

```python
Scraper
```

### `main.py`

```python
url
 ↓
Scraper
 ↓
article
 ↓
print
```

---

# 🧠 Tổng kết Buổi 7

Bạn cần nắm chắc 6 khái niệm:

### ① HTTPX

```python
response = client.get(url)
```

### ② Status

```python
response.raise_for_status()
```

### ③ HTML

```python
html = response.text
```

### ④ Selectolax

```python
tree = HTMLParser(html)
```

### ⑤ Parser

```python
tree.css_first(...)
tree.css(...)
```

### ⑥ Separation

```text
Fetcher
   ↓
 HTML
   ↓
Parser
   ↓
 Data
```

Và kiến trúc quan trọng nhất của hôm nay:

```text
                    ┌──────────────┐
                    │    Scraper   │
                    │ Orchestrator │
                    └──────┬───────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
      ┌─────────────┐             ┌─────────────┐
      │ HTTPFetcher │             │    Parser   │
      │   HTTPX     │             │ Selectolax  │
      └──────┬──────┘             └──────┬──────┘
             │                           │
             ▼                           │
            HTML ───────────────────────►│
                                         ▼
                                       Data
```

**Buổi 8** sẽ xây hẳn `ArticleExtractor` theo pipeline:

```text
URL
 ↓
HTTPFetcher
 ↓
HTMLCleaner
 ↓
Selectolax
 ↓
ArticleExtractor
 ↓
┌────────────────┐
│ title          │
│ content        │
│ author         │
│ published_at   │
│ images         │
└────────────────┘
```

Đây sẽ là buổi đầu tiên chúng ta ghép **HTTPX + Selectolax + HTMLCleaner + Extraction** thành một component crawler có cấu trúc tương đối giống production.
