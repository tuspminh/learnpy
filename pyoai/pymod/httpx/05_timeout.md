# Buổi 5 — Timeout trong HTTPX

Timeout là một trong những phần **quan trọng nhất khi viết HTTP client production**.

Nếu bạn viết:

```python
response = httpx.get(url)
```

mà server không phản hồi, ứng dụng có thể phải chờ rất lâu.

Đặc biệt với crawler:

```text
1000 URL
   │
   ├── 998 URL bình thường
   ├── 1 URL chậm
   └── 1 URL treo
```

Nếu không kiểm soát timeout, worker có thể bị giữ lại rất lâu.

---

# 1. Timeout là gì?

Timeout có nghĩa:

> "Tôi chỉ chờ server/network trong khoảng thời gian nhất định. Nếu quá thời gian đó thì hủy request."

Ví dụ:

```python
import httpx

response = httpx.get(
    "https://example.com",
    timeout=5.0,
)
```

Nghĩa là HTTPX sử dụng timeout `5` giây.

---

# 2. Timeout mặc định

HTTPX **có timeout mặc định**, vì vậy request không mặc định chờ vô hạn.

Tuy nhiên trong ứng dụng thực tế, bạn thường nên **chủ động cấu hình timeout phù hợp với loại request**.

Ví dụ API nhanh:

```python
timeout = 5.0
```

Crawler:

```python
timeout = 15.0
```

Download file lớn:

```python
timeout = 60.0
```

Không nên áp dụng một timeout duy nhất cho mọi loại workload.

---

# 3. Timeout đơn giản

Bạn có thể truyền một số:

```python
import httpx

response = httpx.get(
    "https://example.com",
    timeout=5.0,
)
```

Hiểu đơn giản:

```text
timeout = 5 seconds
```

---

# 4. Timeout Exception

Khi timeout xảy ra, HTTPX có exception:

```python
httpx.TimeoutException
```

Ví dụ:

```python
import httpx

try:
    response = httpx.get(
        "https://example.com",
        timeout=5.0,
    )

except httpx.TimeoutException:
    print("Request timeout")
```

Đây là pattern cơ bản:

```text
request
   │
   ▼
timeout?
   │
   ├── no → response
   │
   └── yes
        ↓
 TimeoutException
```

---

# 5. Timeout không phải HTTP Error

Đây là một phân biệt rất quan trọng.

Nếu server trả:

```text
404
```

thì server **đã phản hồi**.

Nếu server trả:

```text
500
```

thì server **đã phản hồi**.

Nhưng timeout:

```text
server không phản hồi kịp
```

Do đó:

```python
response.raise_for_status()
```

không giải quyết timeout.

Bạn phải xử lý:

```python
except httpx.TimeoutException:
```

---

# 6. HTTP Error vs Timeout

```text
Network / HTTP
      │
      ├── Server trả 200
      │      ↓
      │   Success
      │
      ├── Server trả 404
      │      ↓
      │   HTTPStatusError
      │
      ├── Server trả 500
      │      ↓
      │   HTTPStatusError
      │
      └── Không phản hồi
             ↓
       TimeoutException
```

Đây là kiến thức rất quan trọng khi sau này xây retry system.

---

# 7. HTTPX có 4 loại timeout

HTTPX chia timeout thành:

```text
Timeout
│
├── Connect
├── Read
├── Write
└── Pool
```

Đây là phần quan trọng nhất của buổi hôm nay.

---

# 8. Connect Timeout

`connect timeout` là thời gian tối đa HTTPX chờ để **thiết lập connection với server**.

Ví dụ:

```python
timeout = httpx.Timeout(
    connect=5.0,
)
```

Concept:

```text
Python
   │
   │ connect
   ▼
Server
```

Nếu không thể kết nối trong thời gian cho phép:

```text
ConnectTimeout
```

---

# 9. Khi nào Connect Timeout xảy ra?

Ví dụ:

```text
DNS
 ↓
TCP connection
 ↓
TLS connection
```

Nếu network/server không thể thiết lập connection:

```text
Connect Timeout
```

Các nguyên nhân có thể:

* server không tồn tại
* firewall
* network lỗi
* server quá tải
* proxy lỗi
* DNS/network path có vấn đề

---

# 10. Read Timeout

Sau khi kết nối thành công, HTTPX phải chờ server gửi dữ liệu.

Ví dụ:

```text
Client
   │
   │ request
   ▼
Server
   │
   │ processing...
   │
   │ processing...
   ▼
response data
```

Nếu HTTPX chờ dữ liệu quá lâu:

```text
ReadTimeout
```

Ví dụ:

```python
timeout = httpx.Timeout(
    read=10.0,
)
```

---

# 11. Ví dụ Read Timeout

Giả sử server:

```text
Request
   ↓
processing 20 seconds
   ↓
response
```

Nhưng:

```python
read=5
```

thì:

```text
5 seconds
   ↓
ReadTimeout
```

---

# 12. Write Timeout

Write timeout kiểm soát thời gian gửi dữ liệu đến server.

Đặc biệt có ý nghĩa với request body lớn:

```text
Client
   │
   │ upload 500 MB
   ▼
Server
```

Nếu việc gửi dữ liệu bị chậm:

```text
WriteTimeout
```

Ví dụ:

```python
timeout = httpx.Timeout(
    write=10.0,
)
```

---

# 13. Pool Timeout

Đây là phần liên quan trực tiếp đến Buổi 4.

Ta có:

```text
httpx.Client
     │
     ▼
Connection Pool
```

Giả sử connection pool đã hết connection khả dụng.

Request mới phải chờ:

```text
Request
   │
   ▼
Connection Pool
   │
   └── no available connection
            │
            ▼
          waiting
```

Nếu chờ quá lâu:

```text
PoolTimeout
```

---

# 14. Tạo Timeout đầy đủ

HTTPX cho phép:

```python
import httpx

timeout = httpx.Timeout(
    10.0,
    connect=5.0,
)

with httpx.Client(
    timeout=timeout
) as client:
    response = client.get(url)
```

Ở đây:

```text
default timeout = 10s
connect timeout = 5s
```

Các timeout còn lại sẽ sử dụng default phù hợp.

---

# 15. Cấu hình từng loại

Bạn có thể chỉ rõ:

```python
timeout = httpx.Timeout(
    connect=5.0,
    read=10.0,
    write=10.0,
    pool=5.0,
)
```

Sau đó:

```python
with httpx.Client(
    timeout=timeout
) as client:

    response = client.get(url)
```

Tư duy:

```text
Timeout
│
├── connect = 5s
├── read    = 10s
├── write   = 10s
└── pool    = 5s
```

---

# 16. Vì sao không chỉ có `timeout=10`?

Vì 4 giai đoạn có bản chất khác nhau.

Ví dụ:

```text
Connect:
   Server có phản hồi không?

Read:
   Server đang gửi data như thế nào?

Write:
   Client có gửi data đi được không?

Pool:
   Client có lấy được connection không?
```

Một ứng dụng production có thể cần:

```text
connect: ngắn
read: dài
write: vừa
pool: ngắn
```

---

# 17. Cấu hình cho API Client

Ví dụ một API thường phải phản hồi nhanh:

```python
import httpx


timeout = httpx.Timeout(
    connect=3.0,
    read=10.0,
    write=10.0,
    pool=5.0,
)

client = httpx.Client(
    base_url="https://api.example.com",
    timeout=timeout,
)
```

Tư duy:

```text
API Client
   │
   ├── connect ≤ 3s
   ├── read ≤ 10s
   ├── write ≤ 10s
   └── pool ≤ 5s
```

---

# 18. Cấu hình cho Crawler

Crawler thường có workload khác.

Ví dụ:

```python
timeout = httpx.Timeout(
    connect=5.0,
    read=20.0,
    write=10.0,
    pool=5.0,
)
```

Vì một trang web có thể phản hồi chậm hơn API.

---

# 19. Timeout cho Download

Download file lớn cần suy nghĩ khác.

Ví dụ:

```python
timeout = httpx.Timeout(
    connect=10.0,
    read=60.0,
    write=30.0,
    pool=10.0,
)
```

Nhưng cần lưu ý:

> `read timeout` không đơn giản có nghĩa "toàn bộ download phải hoàn thành trong 60 giây".

Nó liên quan đến **thời gian chờ dữ liệu giữa các lần đọc**.

Đây là distinction rất quan trọng.

---

# 20. Read Timeout không phải Total Timeout

Giả sử:

```text
Server gửi chunk
↓
1 giây
↓
chunk
↓
1 giây
↓
chunk
↓
1 giây
↓
chunk
```

Nếu:

```python
read=5
```

thì mỗi lần HTTPX nhận dữ liệu trong khoảng timeout cho phép, request có thể tiếp tục.

Không phải:

```text
TOTAL REQUEST <= 5 seconds
```

Đây là lý do HTTP client production cần hiểu timeout semantics.

---

# 21. Timeout exception hierarchy

Bạn có thể bắt chung:

```python
try:
    response = client.get(url)

except httpx.TimeoutException:
    print("Timeout")
```

Hoặc bắt cụ thể:

```python
try:
    response = client.get(url)

except httpx.ConnectTimeout:
    print("Cannot connect")

except httpx.ReadTimeout:
    print("Server read timeout")

except httpx.WriteTimeout:
    print("Write timeout")

except httpx.PoolTimeout:
    print("Connection pool timeout")
```

---

# 22. Khi nào bắt cụ thể?

Nếu application chỉ cần:

> "Request timeout"

thì:

```python
except httpx.TimeoutException:
```

là đủ.

Nếu cần monitoring:

```text
Connect timeout = network issue
Read timeout    = server slow
Pool timeout    = client concurrency issue
Write timeout   = upload/network issue
```

thì nên bắt cụ thể.

---

# 23. Timeout + Retry

Đây là nơi timeout bắt đầu trở nên thú vị.

Ví dụ:

```python
try:
    response = client.get(url)

except httpx.TimeoutException:
    retry()
```

Nhưng **không phải timeout nào cũng nên retry vô điều kiện**.

Ví dụ:

```text
ConnectTimeout
    → thường có thể retry

ReadTimeout
    → có thể retry tùy API

WriteTimeout
    → cần cẩn thận với POST

PoolTimeout
    → có thể application đang quá concurrency
```

Đặc biệt:

```text
POST
```

có thể tạo resource.

Nếu request thành công ở server nhưng client timeout khi chờ response, retry POST có thể gây duplicate operation.

Đây là một vấn đề production rất quan trọng.

Chúng ta sẽ học sâu hơn ở phần **Retry Policy**.

---

# 24. Timeout + `raise_for_status()`

Hai thứ này giải quyết hai vấn đề khác nhau:

```python
try:
    response = client.get(url)

    response.raise_for_status()

except httpx.TimeoutException:
    print("Network timeout")

except httpx.HTTPStatusError:
    print("Server returned HTTP error")
```

Luồng:

```text
Request
   │
   ├── Timeout?
   │      └── TimeoutException
   │
   ▼
Response
   │
   ├── 2xx → OK
   │
   └── 4xx/5xx
          ↓
    HTTPStatusError
```

---

# 25. Một API Client hoàn chỉnh hơn

Kết hợp Buổi 4 + Buổi 5:

```python
import httpx


class APIClient:

    def __init__(self, base_url: str):
        timeout = httpx.Timeout(
            connect=5.0,
            read=10.0,
            write=10.0,
            pool=5.0,
        )

        self.client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers={
                "Accept": "application/json",
                "User-Agent": "MyAPIClient/1.0",
            },
        )

    def get(self, path: str):
        try:
            response = self.client.get(path)
            response.raise_for_status()
            return response

        except httpx.TimeoutException:
            print("Request timeout")
            raise

    def close(self):
        self.client.close()
```

Sử dụng:

```python
client = APIClient(
    "https://api.example.com"
)

try:
    response = client.get("/users")
    print(response.json())

finally:
    client.close()
```

---

# 26. Tốt hơn: Context Manager

Có thể kết hợp:

```python
import httpx


class APIClient:

    def __init__(self, base_url: str):
        timeout = httpx.Timeout(
            connect=5.0,
            read=10.0,
            write=10.0,
            pool=5.0,
        )

        self.client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
        )

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.client.close()

    def get(self, path: str):
        response = self.client.get(path)
        response.raise_for_status()
        return response
```

Sử dụng:

```python
with APIClient(
    "https://api.example.com"
) as client:

    response = client.get("/users")
```

---

# 27. Một pattern quan trọng cho crawler

Giả sử bạn crawl:

```python
urls = [
    "...",
    "...",
    "...",
]
```

Ta có:

```python
import httpx


timeout = httpx.Timeout(
    connect=5.0,
    read=15.0,
    write=10.0,
    pool=5.0,
)

with httpx.Client(
    timeout=timeout,
    headers={
        "User-Agent": "MyCrawler/1.0",
    },
) as client:

    for url in urls:
        try:
            response = client.get(url)
            response.raise_for_status()

            print(
                url,
                response.status_code,
            )

        except httpx.TimeoutException:
            print(
                "TIMEOUT:",
                url,
            )

        except httpx.HTTPStatusError as exc:
            print(
                "HTTP ERROR:",
                url,
                exc.response.status_code,
            )
```

Đây đã là nền tảng khá tốt cho một crawler.

---

# 28. Timeout không giải quyết mọi vấn đề

Đừng nghĩ:

```text
timeout
=
network reliability
```

Không phải.

Production HTTP client còn cần:

```text
Timeout
   +
Retry
   +
Backoff
   +
Rate Limit
   +
Connection Pool
   +
Error Handling
   +
Logging
```

Ví dụ:

```text
Request
   │
   ▼
Timeout
   │
   ├── success
   │
   └── failure
          │
          ▼
        Retry?
          │
          ▼
       Backoff
          │
          ▼
       Request
```

Đây sẽ là một phần quan trọng của các buổi nâng cao.

---

# 29. Timeout Cheat Sheet

| Timeout   | Kiểm soát              |
| --------- | ---------------------- |
| `connect` | Kết nối tới server     |
| `read`    | Chờ dữ liệu từ server  |
| `write`   | Gửi dữ liệu tới server |
| `pool`    | Chờ connection từ pool |

Cấu hình:

```python
timeout = httpx.Timeout(
    connect=5.0,
    read=10.0,
    write=10.0,
    pool=5.0,
)
```

Exception:

```python
httpx.ConnectTimeout
httpx.ReadTimeout
httpx.WriteTimeout
httpx.PoolTimeout
```

Hoặc bắt chung:

```python
httpx.TimeoutException
```

---

# Bài tập Buổi 5

## Bài 1 — Timeout cơ bản

Viết request có:

```text
timeout = 3 giây
```

và xử lý:

```python
httpx.TimeoutException
```

---

## Bài 2 — Timeout chi tiết

Tạo:

```python
httpx.Timeout(
    connect=3,
    read=10,
    write=5,
    pool=2,
)
```

Sử dụng nó với `httpx.Client`.

---

## Bài 3 — Phân biệt exception

Viết:

```python
try:
    ...
except httpx.ConnectTimeout:
    ...
except httpx.ReadTimeout:
    ...
except httpx.WriteTimeout:
    ...
except httpx.PoolTimeout:
    ...
```

và giải thích **mỗi exception xảy ra ở giai đoạn nào của HTTP lifecycle**.

---

## Bài 4 — API Client

Nâng cấp `APIClient` của Buổi 4:

```text
APIClient
│
├── base_url
├── headers
├── timeout
├── get()
├── post()
└── close()
```

Yêu cầu:

```text
connect = 5s
read    = 10s
write   = 10s
pool    = 5s
```

---

## Bài 5 — Crawler

Viết:

```python
def fetch(url: str) -> str:
    ...
```

Yêu cầu:

```text
1. GET
2. timeout
3. raise_for_status()
4. trả về response.text
5. bắt TimeoutException
6. bắt HTTPStatusError
```

---

## Bài 6 — Bài tập tư duy

Giả sử:

```text
connect = 3s
read    = 10s
write   = 5s
pool    = 2s
```

Phân tích 4 tình huống:

### Tình huống A

```text
Server không thể kết nối
```

→ timeout nào?

### Tình huống B

```text
Kết nối thành công nhưng server mất 20 giây mới gửi dữ liệu
```

→ timeout nào?

### Tình huống C

```text
Upload file lớn nhưng network gửi dữ liệu quá chậm
```

→ timeout nào?

### Tình huống D

```text
Connection pool đã đầy và request phải chờ connection
```

→ timeout nào?

---

# Kiến trúc chúng ta đã có

Sau 5 buổi:

```text
                    HTTPX
                      │
              ┌───────┴───────┐
              │               │
           Request          Response
              │               │
              └────── HTTP ───┘
                      │
                  Client
                      │
             Connection Pool
                      │
                   Timeout
                      │
        ┌─────────────┼─────────────┐
        │             │             │
     Connect        Read          Write
                      │
                    Pool
```

### Buổi 6

Chúng ta sẽ đi sâu vào **Query Parameters với HTTPX**:

```text
params={}
httpx.QueryParams
multiple values
list parameters
encoding
URL construction
pagination
filtering
search API
```

Đặc biệt chúng ta sẽ học cách xử lý những trường hợp thực tế như:

```text
?page=1&tag=python&tag=httpx
```

và:

```python
params = {
    "tag": ["python", "httpx"]
}
```

để hiểu chính xác HTTPX biến Python data thành query string như thế nào.
