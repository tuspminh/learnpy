# Phần II — HTTP Client

# Buổi 11 — Timeout trong `primp`

Từ đây chúng ta chuyển từ **biết dùng `primp`** sang **thiết kế HTTP Client đủ chắc để chạy crawler**.

```text
PHẦN II — HTTP CLIENT

11. Timeout             ← hôm nay
12. Exception
13. Authentication
14. Proxy
15. SSL / Verify
16. Session / Connection Reuse
17. Default Headers
18. Default Params
19. Request Options
20. Client Lifecycle
```

---

# 1. Timeout là gì?

Khi crawler gửi:

```python
response = client.get(url)
```

không có nghĩa server sẽ trả lời ngay.

Có thể xảy ra:

```text
Client
  │
  │ GET
  ▼
Server
  │
  │ ... đang xử lý ...
  │
  │ ... 10 giây ...
  │
  ▼
Response
```

Hoặc server không phản hồi:

```text
Client ───────────> Server
                       │
                       │
                       │
                       X
```

Nếu không có timeout phù hợp, worker crawler có thể bị treo quá lâu.

---

# 2. Vì sao crawler bắt buộc phải có Timeout?

Giả sử crawler có:

```text
100 workers
```

Mỗi request bị treo:

```text
5 phút
```

Nếu nhiều request cùng bị treo:

```text
Worker 1 → waiting
Worker 2 → waiting
Worker 3 → waiting
...
Worker 100 → waiting
```

Crawler gần như không còn khả năng xử lý URL mới.

Do đó:

> **Timeout là cơ chế bảo vệ worker.**

---

# 3. Timeout cơ bản

Với `primp`, ta truyền timeout vào request/client theo API của phiên bản đang sử dụng.

Ví dụ dạng request-level:

```python
import primp


def main():
    client = primp.Client()

    response = client.get(
        "https://httpbin.org/get",
        timeout=10,
    )

    print(response.status_code)


if __name__ == "__main__":
    main()
```

Ý nghĩa:

```text
timeout=10
```

là giới hạn thời gian chờ cho request theo semantics của `primp`/backend ở phiên bản bạn cài.

**Điểm quan trọng:** timeout không nên được hiểu đơn giản là “toàn bộ request chắc chắn bị kill đúng 10 giây”. HTTP client có nhiều giai đoạn khác nhau như DNS, connection, TLS, transfer; cách `primp` áp dụng timeout phụ thuộc API/version.

---

# 4. Timeout không phải Retry

Hai khái niệm này hoàn toàn khác:

```text
Timeout
   ↓
Request quá lâu
```

còn:

```text
Retry
   ↓
Quyết định gửi lại request
```

Ví dụ:

```text
Request
   │
   ├── timeout
   │
   ▼
Exception
   │
   ▼
Retry Policy
   │
   ├── retry
   └── give up
```

**Buổi 11 chỉ tập trung Timeout.**

Retry sẽ được xây sau khi chúng ta học Exception.

---

# 5. Ví dụ request bị timeout

Để test timeout, `httpbin` có endpoint delay:

```text
https://httpbin.org/delay/5
```

Server cố tình trì hoãn response.

Ví dụ:

```python
import primp


def main():
    client = primp.Client()

    response = client.get(
        "https://httpbin.org/delay/5",
        timeout=2,
    )

    print(response.status_code)


if __name__ == "__main__":
    main()
```

Nếu timeout được kích hoạt trước khi server trả response, request sẽ kết thúc bằng lỗi/exception.

Đây chính là lý do **Buổi 12 — Exception** sẽ ngay lập tức nối tiếp Buổi 11.

---

# 6. Timeout và Exception

Đừng viết:

```python
response = client.get(
    url,
    timeout=5,
)

print(response.text)
```

mà không nghĩ đến lỗi.

Trong crawler thực tế:

```text
timeout
   ↓
exception
   ↓
Fetcher xử lý
```

Ví dụ concept:

```python
try:
    response = client.get(
        url,
        timeout=10,
    )
except Exception as exc:
    print("Request failed:", exc)
```

Ở buổi 11 chưa cần phân loại exception.

Buổi 12 chúng ta sẽ làm việc đó.

---

# 7. Timeout quá lớn cũng là vấn đề

Ví dụ:

```python
timeout=300
```

tức 5 phút.

Có thể tưởng tượng:

```text
Worker
  │
  ├────────────── 5 phút ──────────────┐
  │                                    │
  │              BLOCKED               │
  └────────────────────────────────────┘
```

Với crawler:

```text
timeout quá lớn
       ↓
worker bị chiếm lâu
       ↓
throughput giảm
```

Nhưng timeout quá nhỏ cũng có vấn đề:

```text
timeout quá nhỏ
       ↓
request hợp lệ bị cắt
       ↓
retry tăng
       ↓
traffic tăng
```

Vì vậy timeout là **một policy**, không phải một con số tùy ý.

---

# 8. Timeout cho Novel Crawler

Một website truyện có thể:

```text
HTML page
       → nhanh

Chapter
       → nhanh

Image
       → chậm hơn

Proxy
       → có thể chậm

Server đang quá tải
       → rất chậm
```

Do đó sau này có thể có policy:

```text
HTML:
10s

Image:
30s

Large content:
60s
```

Nhưng **không nên hard-code những con số này ngay bây giờ**.

Chúng ta sẽ xây một abstraction cho timeout sau khi hiểu hết HTTP Client.

---

# 9. Timeout nên nằm ở đâu?

Không nên:

```python
class NovelParser:

    def parse(...):
        ...
```

Parser không liên quan HTTP.

Cũng không nên:

```python
class Novel:

    timeout = 10
```

Timeout là concern của HTTP infrastructure.

Nên:

```text
Application
     │
     ▼
Fetcher
     │
     ▼
Primp Client
     │
     ▼
HTTP Timeout
```

---

# 10. Fetcher abstraction

Hiện tại chúng ta có thể viết đơn giản:

```python
import primp


class PrimpFetcher:

    def __init__(
        self,
        timeout: float = 10,
    ):
        self.client = primp.Client()
        self.timeout = timeout

    def get(self, url: str):
        return self.client.get(
            url,
            timeout=self.timeout,
        )
```

Sử dụng:

```python
def main():
    fetcher = PrimpFetcher(
        timeout=10,
    )

    response = fetcher.get(
        "https://example.com"
    )

    print(response.status_code)


if __name__ == "__main__":
    main()
```

Kiến trúc:

```text
PrimpFetcher
     │
     ├── Client
     │
     └── timeout
            │
            ▼
        primp.get()
```

Đây là abstraction hợp lý ở thời điểm hiện tại.

---

# 11. Nhưng timeout có thể khác nhau theo request

Ví dụ:

```python
fetcher.get(
    url,
    timeout=30,
)
```

thay vì:

```python
fetcher = PrimpFetcher(timeout=30)
```

Ta có:

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
        timeout: float | None = None,
    ):
        timeout = (
            self.default_timeout
            if timeout is None
            else timeout
        )

        return self.client.get(
            url,
            timeout=timeout,
        )
```

Bây giờ:

```python
fetcher = PrimpFetcher(
    timeout=10
)
```

mặc định:

```text
10 seconds
```

nhưng có thể override:

```python
fetcher.get(
    image_url,
    timeout=30,
)
```

---

# 12. Default vs Request Override

Đây là pattern rất quan trọng:

```text
Fetcher
 │
 ├── default timeout = 10
 │
 └── request timeout
          │
          ├── None → dùng default
          │
          └── 30 → override
```

Code:

```python
timeout = (
    self.default_timeout
    if timeout is None
    else timeout
)
```

Đây là pattern chúng ta sẽ gặp lại ở:

```text
Default Headers
Default Params
Request Options
```

ở các buổi sau.

---

# 13. Timeout = float?

Có thể thiết kế:

```python
timeout: float
```

Ví dụ:

```python
5
```

hoặc:

```python
5.5
```

Nhưng trong architecture tốt hơn, sau này chúng ta có thể tạo:

```python
@dataclass(frozen=True)
class TimeoutConfig:
    connect: float
    read: float
    write: float
    total: float
```

Tuy nhiên:

> **Chưa cần làm ngay.**

Đừng biến một bài học cơ bản thành một hệ thống abstraction khổng lồ.

Hiện tại:

```python
timeout: float
```

là đủ để hiểu concept.

---

# 14. Timeout trong crawler loop

Giả sử:

```python
urls = [
    "...",
    "...",
    "...",
]
```

Fetcher:

```python
fetcher = PrimpFetcher(
    timeout=10,
)
```

Flow:

```text
URL 1
 │
 ▼
GET
 │
 ├── 200 → tiếp tục
 │
 └── timeout → exception


URL 2
 │
 ▼
GET
 │
 └── tiếp tục
```

Điều quan trọng là:

> Một request timeout không được làm chết toàn bộ crawler.

Nhưng để làm được điều đó đúng cách, chúng ta cần **Exception Handling**.

Đó là bài kế tiếp.

---

# 15. Timeout và Proxy

Đặc biệt quan trọng với crawler có proxy.

Flow:

```text
Crawler
   │
   ▼
Proxy
   │
   ▼
Website
```

Có thêm một điểm có thể delay:

```text
connect
   ↓
proxy connection
   ↓
TLS
   ↓
server processing
   ↓
response transfer
```

Do đó khi sử dụng proxy:

```text
timeout
```

càng trở thành một phần quan trọng của Fetcher policy.

Sau này architecture của chúng ta sẽ đi:

```text
Timeout
   ↓
Exception
   ↓
Proxy
   ↓
Retry
```

---

# 16. Timeout và Proxy Pool

Về sau bạn muốn:

```text
Proxy Pool
   │
   ├── Proxy A
   ├── Proxy B
   ├── Proxy C
   └── Proxy D
```

Nếu:

```text
Proxy A
   ↓
timeout
```

thì không nên chỉ:

```text
retry same request forever
```

mà policy có thể quyết định:

```text
Timeout
   ↓
Proxy A unhealthy?
   │
   ├── yes → đánh dấu proxy
   │
   └── no
```

Nhưng phần này sẽ học sau ở:

```text
14. Proxy
```

và Retry Policy sẽ được hoàn thiện trong Phần V.

---

# 17. Timeout không chỉ dành cho GET

POST cũng cần timeout:

```python
response = client.post(
    url,
    data={
        "username": "alice",
    },
    timeout=10,
)
```

JSON:

```python
response = client.post(
    url,
    json={
        "username": "alice",
    },
    timeout=10,
)
```

Vì timeout là property của HTTP operation, không phải riêng GET.

---

# 18. Một Fetcher hoàn chỉnh hơn

Ở mức hiện tại:

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

Sử dụng:

```python
def main():
    fetcher = PrimpFetcher(
        timeout=10,
    )

    response = fetcher.get(
        "https://example.com"
    )

    print(response.status_code)


if __name__ == "__main__":
    main()
```

---

# 19. Một điểm kiến trúc quan trọng

Đừng để:

```python
PrimpFetcher
```

khắp application code.

Application nên phụ thuộc abstraction:

```python
class Fetcher:
    ...
```

và infrastructure:

```text
PrimpFetcher
```

implement nó.

Concept:

```text
                 Application
                      │
                      ▼
               Fetcher Interface
                      ▲
                      │
                PrimpFetcher
                      │
                      ▼
                    primp
```

Timeout nằm ở infrastructure/request policy.

Sau này:

```text
PrimpFetcher
HttpxFetcher
MockFetcher
```

đều có thể có timeout.

---

# 20. Test thực tế

Tạo file:

```text
lesson_11.py
```

Code:

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
        timeout: float | None = None,
    ):
        if timeout is None:
            timeout = self.default_timeout

        return self.client.get(
            url,
            timeout=timeout,
        )


def main():
    fetcher = PrimpFetcher(
        timeout=10,
    )

    response = fetcher.get(
        "https://httpbin.org/get"
    )

    print("Status:", response.status_code)
    print("URL:", response.url)


if __name__ == "__main__":
    main()
```

Test bình thường trước:

```bash
python lesson_11.py
```

Sau đó thử endpoint delay:

```python
response = fetcher.get(
    "https://httpbin.org/delay/10",
    timeout=2,
)
```

Bạn sẽ có cơ hội quan sát timeout thực tế.

Nếu request phát sinh exception thì đó **không phải lỗi của bài test** — chính exception đó là thứ chúng ta sẽ xử lý trong **Buổi 12**.

---

# 21. Bài tập

### Bài 1 — Default timeout

Tạo:

```python
fetcher = PrimpFetcher(
    timeout=5
)
```

và gọi:

```python
fetcher.get(
    "https://httpbin.org/get"
)
```

---

### Bài 2 — Override timeout

Default:

```python
timeout=5
```

nhưng request:

```python
fetcher.get(
    url,
    timeout=20,
)
```

Xác định timeout nào được sử dụng.

---

### Bài 3 — Timeout thực tế

Thử:

```python
fetcher.get(
    "https://httpbin.org/delay/10",
    timeout=2,
)
```

Sau đó **chưa cần xử lý exception**, chỉ quan sát loại lỗi Python nhận được.

---

### Bài 4 — POST

Thử:

```python
fetcher.post(
    "https://httpbin.org/post",
    data={
        "keyword": "python",
    },
    timeout=10,
)
```

---

# 22. Tư duy quan trọng sau Buổi 11

Đừng chỉ nhớ:

```python
timeout=10
```

Mà hãy nhớ architecture:

```text
                   HTTP Request
                        │
                        ▼
                  ┌───────────┐
                  │  Timeout  │
                  └─────┬─────┘
                        │
              ┌─────────┴─────────┐
              │                   │
          Response             Timeout
              │                   │
              ▼                   ▼
          Processing           Exception
                                  │
                                  ▼
                            Retry Policy
```

Và trong Novel Crawler:

```text
Application
     │
     ▼
Fetcher Interface
     │
     ▼
PrimpFetcher
     │
     ├── Client
     ├── Timeout Policy
     │
     ▼
   primp
     │
     ▼
   Server
```

### Cốt lõi cần nhớ

1. **Timeout bảo vệ crawler khỏi request treo quá lâu.**
2. **Timeout ≠ Retry.**
3. Timeout là concern của HTTP/Fetcher, không phải Parser.
4. Nên có **default timeout** và khả năng **override theo request** khi cần.
5. Timeout xảy ra sẽ dẫn đến **Exception** — đây là lý do Buổi 12 tiếp nối trực tiếp.

**Buổi 12 — Exception trong `primp`** sẽ xây từ chính timeout hôm nay: phân biệt timeout, connection error, HTTP error, lỗi DNS/network và cách biến chúng thành các loại lỗi mà `Fetcher` của Novel Crawler có thể xử lý có hệ thống.
