# Buổi 16 — Session / Connection Reuse

Ở Buổi 15 chúng ta đã học **SSL / Verify**. Hôm nay đi vào một vấn đề rất quan trọng khi xây crawler:

> **Tại sao không nên tạo `primp.Client()` mới cho mỗi request?**

Mục tiêu cuối buổi:

```text
Novel Crawler
    ↓
PrimpFetcher
    ↓
1 Client sống lâu
    ↓
Connection Pool
    ↓
TCP / TLS / HTTP connection reuse
```

Việc giữ một client/session lâu dài cho phép thư viện HTTP quản lý và tái sử dụng các kết nối phù hợp thay vì tạo lại kết nối từ đầu cho từng request. Đây là một nguyên tắc phổ biến của HTTP clients; ví dụ Requests tài liệu hóa rõ keep-alive tự động trong một Session. ([GitHub][1])

---

# 1. Vấn đề: tạo Client cho từng request

Ví dụ **không nên làm**:

```python
import primp


def get(url: str):
    client = primp.Client()
    return client.get(url)


urls = [
    "https://httpbin.org/get?a=1",
    "https://httpbin.org/get?a=2",
    "https://httpbin.org/get?a=3",
]

for url in urls:
    response = get(url)
    print(response.status_code)
```

Mỗi lần:

```text
get()
 ↓
Client()
 ↓
request
 ↓
Client kết thúc
```

Sau đó request tiếp theo:

```text
get()
 ↓
Client()
 ↓
request
```

Ta không có một client lâu sống để quản lý state/connection pool xuyên suốt chuỗi request.

---

# 2. Client sống lâu

Thay vào đó:

```python
import primp


client = primp.Client()

urls = [
    "https://httpbin.org/get?a=1",
    "https://httpbin.org/get?a=2",
    "https://httpbin.org/get?a=3",
]

for url in urls:
    response = client.get(url)
    print(response.status_code)
```

Luồng trở thành:

```text
             ┌──────────────┐
             │ primp.Client │
             └──────┬───────┘
                    │
          ┌─────────┼─────────┐
          ↓         ↓         ↓
       request 1  request 2  request 3
          │         │         │
          └─────────┴─────────┘
              connection pool
```

Đây chính là pattern chúng ta muốn trong `PrimpFetcher`.

---

# 3. Connection reuse thực sự là gì?

Giả sử crawler cần tải:

```text
https://example.com/novel/a
https://example.com/novel/b
https://example.com/novel/c
```

Nếu mỗi request phải thiết lập kết nối mới, quá trình có thể gồm:

```text
TCP connection
    ↓
TLS handshake
    ↓
HTTP request
    ↓
HTTP response
    ↓
connection close
```

Request tiếp:

```text
TCP connection
    ↓
TLS handshake
    ↓
HTTP request
    ↓
HTTP response
```

Có rất nhiều chi phí kết nối.

Với connection reuse:

```text
TCP connection
    ↓
TLS handshake
    ↓
HTTP request #1
    ↓
HTTP response
    ↓
HTTP request #2
    ↓
HTTP response
    ↓
HTTP request #3
    ↓
HTTP response
```

Không phải lúc nào connection cũng được reuse — server, protocol, idle timeout, proxy và các điều kiện mạng có thể khiến connection phải được tạo lại.

---

# 4. TCP + TLS là phần tốn kém

Hãy nhớ flow từ Buổi 15:

```text
Python
   │
   ├── TCP connection
   │
   ├── TLS handshake
   │
   └── HTTP request
           │
           ↓
        Server
```

Nếu crawler tải hàng nghìn chapter:

```text
Chapter 1
    TCP
    TLS
    HTTP

Chapter 2
    TCP
    TLS
    HTTP

Chapter 3
    TCP
    TLS
    HTTP

...
```

thì connection reuse giúp client có cơ hội dùng lại connection phù hợp:

```text
TCP
TLS
│
├── Chapter 1
├── Chapter 2
├── Chapter 3
├── Chapter 4
└── Chapter 5
```

Với crawler, đây là lý do rất quan trọng để `Fetcher` sở hữu client lâu sống.

---

# 5. Session còn giữ state

Có một điểm rất quan trọng:

**Session ≠ chỉ connection pool.**

Client/session thường còn liên quan đến state của HTTP client, chẳng hạn:

```text
Client
├── connection pool
├── cookies
├── default headers
├── authentication configuration
├── proxy configuration
└── TLS configuration
```

Chúng ta đã học Cookies ở Buổi 9.

Ví dụ:

```python
client = primp.Client()

client.get(login_url)

client.get(protected_url)
```

Nếu client giữ cookie/session state phù hợp, request thứ hai có thể tiếp tục sử dụng state được thiết lập từ request trước.

Nếu cứ tạo:

```python
primp.Client()
```

mới liên tục thì bạn đang phá vỡ ý tưởng về một HTTP session liên tục.

---

# 6. Đây là lý do `PrimpFetcher` nên giữ Client

Code hiện tại của chúng ta:

```python
import primp


class PrimpFetcher:

    def __init__(
        self,
        timeout: float = 10,
    ):
        self.client = primp.Client()
        self.default_timeout = timeout

    def get(
        self,
        url: str,
        *,
        timeout: float | None = None,
    ):
        if timeout is None:
            timeout = self.default_timeout

        return self.client.get(
            url,
            timeout=timeout,
        )
```

Điểm quan trọng nằm ở:

```python
self.client = primp.Client()
```

nằm trong `__init__`.

---

# 7. Không tạo Client trong `get()`

### Sai về architecture

```python
class PrimpFetcher:

    def get(self, url: str):

        client = primp.Client()

        return client.get(url)
```

Mỗi lần:

```text
fetcher.get()
      ↓
Client()
      ↓
request
```

### Đúng hơn

```python
class PrimpFetcher:

    def __init__(self):
        self.client = primp.Client()

    def get(self, url: str):
        return self.client.get(url)
```

Luồng:

```text
PrimpFetcher
      │
      └── Client
            │
            ├── GET chapter 1
            ├── GET chapter 2
            ├── GET chapter 3
            └── GET chapter 4
```

---

# 8. Demo thực tế

Tạo:

```text
lesson_16.py
```

Code hoàn chỉnh:

```python
import primp
import time


def main():

    client = primp.Client()

    urls = [
        "https://httpbin.org/get?chapter=1",
        "https://httpbin.org/get?chapter=2",
        "https://httpbin.org/get?chapter=3",
        "https://httpbin.org/get?chapter=4",
        "https://httpbin.org/get?chapter=5",
    ]

    for url in urls:

        start = time.perf_counter()

        response = client.get(
            url,
            timeout=10,
        )

        elapsed = time.perf_counter() - start

        print(
            response.status_code,
            f"{elapsed:.3f}s",
            response.url,
        )


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python lesson_16.py
```

Bạn sẽ thấy thời gian mỗi request không giống nhau.

**Không nên dùng kết quả benchmark đơn giản này để kết luận chắc chắn rằng request thứ N luôn nhanh hơn request thứ nhất.** Internet, server, DNS, proxy và connection state đều ảnh hưởng.

---

# 9. So sánh hai thiết kế

## Thiết kế A — Client per request

```python
def fetch(url: str):

    client = primp.Client()

    return client.get(url)
```

Architecture:

```text
fetch()
 ├── Client
 └── request

fetch()
 ├── Client
 └── request

fetch()
 ├── Client
 └── request
```

---

## Thiết kế B — Shared client trong Fetcher

```python
class PrimpFetcher:

    def __init__(self):
        self.client = primp.Client()

    def fetch(self, url: str):
        return self.client.get(url)
```

Architecture:

```text
PrimpFetcher
      │
      ▼
Primp Client
      │
      ├── request
      ├── request
      ├── request
      ├── request
      └── request
```

**Thiết kế B phù hợp hơn với crawler.**

---

# 10. Đừng nhầm Session với Connection

Đây là phần rất quan trọng.

Có thể hình dung:

```text
SESSION / CLIENT
        │
        ├── Cookies
        ├── Default Headers
        ├── Authentication
        ├── Proxy
        ├── TLS config
        │
        └── Connection Pool
                  │
                  ├── Connection A
                  ├── Connection B
                  └── Connection C
```

Session/client là **lớp quản lý**.

Connection là **kết nối mạng cụ thể**.

---

# 11. Connection Pool

Ví dụ crawler chạy concurrent:

```text
Primp Client
      │
      ▼
Connection Pool
      │
      ├── connection 1 → example.com
      ├── connection 2 → example.com
      ├── connection 3 → example.com
      └── connection 4 → another.com
```

Client có thể quản lý nhiều connection tùy nhu cầu và implementation.

Điều này đặc biệt quan trọng khi sau này chúng ta học:

```text
31 AsyncClient
32 async GET
33 Concurrent Requests
34 Semaphore
```

Khi đó:

```text
AsyncClient
    ↓
Connection Pool
    ↓
Concurrent requests
```

---

# 12. Connection reuse không có nghĩa "một connection duy nhất"

Đây là hiểu nhầm phổ biến.

Không phải:

```text
Client
  ↓
ONE TCP connection
  ↓
everything
```

Mà có thể là:

```text
Client
  ↓
Connection Pool
  ├── Connection A
  ├── Connection B
  ├── Connection C
  └── Connection D
```

Đặc biệt khi concurrent.

---

# 13. Với Novel Crawler

Giả sử một truyện có:

```text
Novel
 ├── Chapter 1
 ├── Chapter 2
 ├── Chapter 3
 ├── ...
 └── Chapter 1000
```

Không nên:

```python
for chapter in chapters:

    client = primp.Client()

    response = client.get(chapter.url)
```

Nên:

```python
client = primp.Client()

for chapter in chapters:

    response = client.get(chapter.url)
```

Nhưng tốt hơn nữa là đưa HTTP ra khỏi Application:

```text
Crawler Use Case
       │
       ▼
   Fetcher
       │
       ▼
 PrimpFetcher
       │
       ▼
 Primp Client
       │
       ▼
 HTTP
```

---

# 14. `PrimpFetcher` hiện tại

Chúng ta có thể hoàn thiện nhẹ:

```python
import primp


class PrimpFetcher:

    def __init__(
        self,
        timeout: float = 10,
        proxy: str | None = None,
        verify: bool = True,
        ca_cert_file: str | None = None,
    ):
        client_kwargs = {
            "verify": verify,
        }

        if proxy is not None:
            client_kwargs["proxy"] = proxy

        if ca_cert_file is not None:
            client_kwargs["ca_cert_file"] = ca_cert_file

        self.client = primp.Client(
            **client_kwargs
        )

        self.default_timeout = timeout

    def get(
        self,
        url: str,
        *,
        timeout: float | None = None,
    ):

        if timeout is None:
            timeout = self.default_timeout

        return self.client.get(
            url,
            timeout=timeout,
        )

    def post(
        self,
        url: str,
        *,
        data: dict | None = None,
        json: object | None = None,
        timeout: float | None = None,
    ):

        if timeout is None:
            timeout = self.default_timeout

        return self.client.post(
            url,
            data=data,
            json=json,
            timeout=timeout,
        )
```

Điểm quan trọng:

```python
self.client = primp.Client(...)
```

chỉ chạy **một lần khi tạo Fetcher**.

---

# 15. Vòng đời của Fetcher

Đây là concept chúng ta cần nhớ:

```text
Application start
       │
       ▼
Create PrimpFetcher
       │
       ▼
Create Primp Client
       │
       ▼
Crawler chạy
       │
       ├── GET listing
       ├── GET novel
       ├── GET chapter 1
       ├── GET chapter 2
       ├── GET chapter 3
       └── ...
       │
       ▼
Application shutdown
       │
       ▼
Fetcher/client lifecycle ends
```

Không phải:

```text
GET
 ↓
Create Client
 ↓
Destroy Client

GET
 ↓
Create Client
 ↓
Destroy Client
```

---

# 16. Nhưng connection vẫn có thể bị đóng

Connection reuse **không đảm bảo connection luôn tồn tại**.

Ví dụ:

```text
Client
  │
  ▼
Connection Pool
  │
  ▼
Server
```

Server có thể đóng idle connection.

Hoặc:

```text
Proxy
  ↓
đóng connection
```

Hoặc:

```text
Network
  ↓
connection reset
```

Khi đó client cần thiết lập connection mới.

Đây là hành vi bình thường của HTTP clients. Các connection pooled có thể trở nên stale nếu phía server/proxy đã đóng chúng; những tình huống như vậy có thể dẫn tới lỗi connection và thường cần xử lý ở tầng retry/error handling. ([GitHub][2])

Vì vậy:

```text
Connection reuse
        ≠
Connection guaranteed forever
```

---

# 17. Đây chính là lý do Buổi 12 và Buổi 16 liên quan nhau

Buổi 12:

```text
Exception
```

Buổi 16:

```text
Connection Reuse
```

Sau này:

```text
Connection error
      ↓
Error Classification
      ↓
Retry Policy
```

Roadmap của chúng ta:

```text
16 Session / Connection Reuse
          ↓
...
35 Timeout + Retry
          ↓
45 Retry Policy
```

Không nên vội nhét retry vào Buổi 16.

---

# 18. Một lỗi kiến trúc rất dễ mắc

Ví dụ Application:

```python
class CrawlChapter:

    def execute(self, url):

        client = primp.Client()

        response = client.get(url)

        ...
```

Đây là Application Layer biết `primp`.

Không tốt.

Chúng ta muốn:

```text
Application
     │
     │ Fetcher Interface
     ▼
Fetcher
     │
     ▼
PrimpFetcher
     │
     ▼
primp
```

Ví dụ:

```python
from typing import Protocol


class Fetcher(Protocol):

    def get(self, url: str):
        ...
```

Implementation:

```python
class PrimpFetcher:

    def __init__(self):
        self.client = primp.Client()

    def get(self, url: str):
        return self.client.get(url)
```

Application:

```python
class CrawlChapterUseCase:

    def __init__(self, fetcher: Fetcher):
        self.fetcher = fetcher

    def execute(self, url: str):

        response = self.fetcher.get(url)

        return response
```

Bây giờ:

```text
UseCase
   │
   │ Fetcher
   ▼
PrimpFetcher
   │
   │ one long-lived Client
   ▼
primp
```

Đây chính là nền móng cho **Buổi 43 — Fetcher Interface** sau này.

---

# 19. Một Fetcher = một Client?

Không nhất thiết trong mọi hệ thống.

Có thể có:

```text
Fetcher
 ├── Client A
 ├── Client B
 └── Client C
```

Ví dụ sau này Proxy Pool:

```text
Proxy A → Client A
Proxy B → Client B
Proxy C → Client C
```

hoặc thiết kế khác:

```text
Proxy Pool
      ↓
Client
      ↓
request(proxy=...)
```

**Chưa quyết định ở Buổi 16.**

Chúng ta sẽ học vấn đề này kỹ hơn ở:

```text
36 Proxy Pool
37 User-Agent / Browser Profile Pool
46 Proxy Strategy
47 Browser Profile Strategy
```

---

# 20. Test bài học

## Test 1 — cùng một Client

```python
import primp


def main():

    client = primp.Client()

    for i in range(5):

        response = client.get(
            "https://httpbin.org/get",
            params={
                "request": i,
            },
            timeout=10,
        )

        print(
            i,
            response.status_code,
            response.url,
        )


if __name__ == "__main__":
    main()
```

---

## Test 2 — Client sống trong Fetcher

```python
import primp


class PrimpFetcher:

    def __init__(self):

        self.client = primp.Client()

    def get(self, url: str):

        return self.client.get(
            url,
            timeout=10,
        )


def main():

    fetcher = PrimpFetcher()

    for i in range(5):

        response = fetcher.get(
            "https://httpbin.org/get"
        )

        print(
            i,
            response.status_code,
        )


if __name__ == "__main__":
    main()
```

---

# 21. Bài tập

### Bài 1

Viết:

```python
class PrimpFetcher:
    ...
```

có:

```python
get()
post()
```

và chỉ tạo:

```python
primp.Client()
```

**một lần**.

---

### Bài 2

Thử viết phiên bản sai:

```python
class BadFetcher:

    def get(self, url):

        client = primp.Client()

        return client.get(url)
```

và phiên bản đúng:

```python
class GoodFetcher:

    def __init__(self):
        self.client = primp.Client()

    def get(self, url):
        return self.client.get(url)
```

Sau đó giải thích bằng sơ đồ:

```text
BadFetcher
?

GoodFetcher
?
```

---

### Bài 3 — Novel Crawler

Giả sử:

```python
chapters = [
    "https://example.com/chapter-1",
    "https://example.com/chapter-2",
    "https://example.com/chapter-3",
]
```

Thiết kế:

```text
CrawlChapterUseCase
        ↓
Fetcher
        ↓
PrimpFetcher
        ↓
Primp Client
```

Yêu cầu:

* Use Case không import `primp`
* `PrimpFetcher` sở hữu client
* Một Fetcher xử lý nhiều chapter
* timeout mặc định = 10 giây

---

# 22. Kiến thức cần nhớ

Buổi 16 chỉ cần nhớ **5 điểm**:

```text
1. Không tạo Client mới cho mỗi request.

2. Client nên có lifecycle dài hơn một request.

3. Client/session có thể quản lý connection pool và HTTP state.

4. Connection reuse ≠ connection luôn tồn tại.

5. PrimpFetcher nên sở hữu một Client lâu sống.
```

Kiến trúc hiện tại của chúng ta:

```text
                    Novel Crawler
                         │
                         ▼
                   Application
                         │
                         ▼
                      Fetcher
                         │
                         ▼
                   PrimpFetcher
                         │
                  ┌──────┴──────┐
                  │             │
             timeout        Client
                                │
                        ┌───────┴───────┐
                        │               │
                   Connection       HTTP State
                      Pool        Cookies / Headers
                        │
                        ▼
                     Internet
```

**Buổi 17 — Default Headers** sẽ xây tiếp trên chính `Primp.Client`: thay vì truyền `headers=` lặp lại ở từng request, chúng ta thiết kế **default headers ở Client/Fetcher**, đồng thời phân biệt rõ **default header** với **browser fingerprint**.

[1]: https://github.com/psf/requests/blob/main/docs/user/advanced.rst?utm_source=chatgpt.com "requests/docs/user/advanced.rst at main · psf/requests · GitHub"
[2]: https://github.com/OpenCTI-Platform/opencti/issues/16414?utm_source=chatgpt.com "feat(client-python): add configurable connection retry/backoff to the default requests session · Issue #16414 · OpenCTI-Platform/opencti · GitHub"
