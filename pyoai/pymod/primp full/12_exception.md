# Buổi 12 — Exception trong `primp`

Ở Buổi 11, ta đã học **Timeout**. Nhưng timeout chỉ là **một loại lỗi**.

Trong crawler thực tế, request có thể thất bại vì:

```text
DNS
 │
 ├── Không resolve được domain
 │
 ├── Connection failed
 │
 ├── Timeout
 │
 ├── SSL error
 │
 └── HTTP 4xx / 5xx
```

Buổi này chúng ta học cách **bắt và phân loại lỗi** để sau này xây `RetryPolicy`.

---

# 1. Vì sao Exception quan trọng trong Crawler?

Nếu viết:

```python
response = client.get(url)
```

thì request không phải lúc nào cũng trả về `Response`.

Có hai nhóm tình huống:

```text
Request
   │
   ├── Thành công
   │      └── Response
   │
   └── Thất bại ở network/client
          └── Exception
```

Ví dụ:

```text
https://example.com
        ↓
      200
        ↓
    Response
```

Nhưng:

```text
https://domain-khong-ton-tai-xyz.com
        ↓
    DNS Error
        ↓
    Exception
```

Đây là điểm cực kỳ quan trọng:

> **HTTP 500 là một Response, không nhất thiết là Exception.**

Trong khi:

> **Timeout thường xảy ra trước khi có Response hoàn chỉnh.**

---

# 2. HTTP Error và Exception khác nhau

Giả sử server trả:

```text
HTTP/1.1 404 Not Found
```

Ta vẫn nhận được:

```python
response
```

và:

```python
response.status_code == 404
```

Tương tự:

```text
500
502
503
504
```

vẫn có thể là một `Response`.

Mô hình:

```text
HTTP request
      │
      ▼
   Server
      │
      ├── 200 ──► Response
      ├── 404 ──► Response
      ├── 500 ──► Response
      └── 503 ──► Response
```

Còn:

```text
DNS failure
Connection failure
Timeout
SSL failure
```

thường xảy ra ở tầng client/network:

```text
HTTP request
      │
      ▼
 Network
      │
      ├── DNS error
      ├── Connection error
      ├── Timeout
      └── SSL error
             │
             ▼
         Exception
```

---

# 3. Exception cơ bản

Ta bắt lỗi bằng:

```python
try:
    response = client.get(url)
except Exception as exc:
    print(exc)
```

Ví dụ:

```python
import primp


def main():
    client = primp.Client()

    try:
        response = client.get(
            "https://domain-khong-ton-tai-xyz.com",
            timeout=5,
        )

        print(response.status_code)

    except Exception as exc:
        print("Request failed!")
        print("Error:", exc)


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python lesson_12.py
```

Bạn có thể nhận được một exception liên quan đến DNS/network.

---

# 4. Không nên chỉ `except Exception`

Code này:

```python
try:
    response = client.get(url)
except Exception:
    print("Request failed")
```

chạy được, nhưng với crawler production thì **chưa đủ tốt**.

Vì ta không biết:

```text
Timeout?
DNS?
Connection?
SSL?
Proxy?
Programming bug?
```

Ví dụ:

```python
try:
    response = client.get(url)

except Exception as exc:
    print(type(exc))
```

Ta có thể quan sát loại exception:

```python
print(type(exc).__name__)
print(str(exc))
```

Ví dụ:

```python
except Exception as exc:
    print("Exception type:", type(exc).__name__)
    print("Message:", str(exc))
```

Đây là kỹ thuật rất hữu ích khi học một HTTP library.

---

# 5. Exception hierarchy

Một HTTP client thường có nhiều loại lỗi:

```text
Exception
   │
   └── HTTP Client Error
          │
          ├── Timeout
          ├── Connection Error
          ├── DNS Error
          ├── SSL Error
          └── ...
```

**Tên class chính xác của từng exception trong `primp` phụ thuộc API/version hiện tại**, vì vậy khi xây abstraction production chúng ta không nên đoán tên exception.

Ở giai đoạn học này, trước tiên hãy quan sát:

```python
type(exc)
```

Ví dụ:

```python
import primp


def main():
    client = primp.Client()

    try:
        client.get(
            "https://domain-khong-ton-tai-xyz.com",
            timeout=5,
        )

    except Exception as exc:
        print("Type:")
        print(type(exc))

        print("\nName:")
        print(type(exc).__name__)

        print("\nMessage:")
        print(str(exc))


if __name__ == "__main__":
    main()
```

---

# 6. Timeout cũng là Exception

Đây là phần nối trực tiếp với Buổi 11.

```python
import primp


def main():
    client = primp.Client()

    try:
        response = client.get(
            "https://httpbin.org/delay/10",
            timeout=2,
        )

        print(response.status_code)

    except Exception as exc:
        print("Request failed")
        print("Type:", type(exc).__name__)
        print("Message:", exc)


if __name__ == "__main__":
    main()
```

Flow:

```text
client.get()
    │
    ▼
Server không phản hồi đủ nhanh
    │
    ▼
Timeout
    │
    ▼
Exception
    │
    ▼
except
```

Do đó:

```text
Timeout
```

không phải:

```text
Response(status_code=408)
```

nhất thiết.

---

# 7. Connection Error

Ví dụ kết nối đến một port không mở:

```python
import primp


def main():
    client = primp.Client()

    try:
        response = client.get(
            "http://127.0.0.1:59999",
            timeout=3,
        )

        print(response.status_code)

    except Exception as exc:
        print("Request failed")
        print("Type:", type(exc).__name__)
        print("Message:", exc)


if __name__ == "__main__":
    main()
```

Ở đây:

```text
127.0.0.1:59999
        ↓
Không có server lắng nghe
        ↓
Connection failure
        ↓
Exception
```

---

# 8. DNS Error

Ví dụ:

```python
import primp


def main():
    client = primp.Client()

    try:
        client.get(
            "https://this-domain-does-not-exist-123456789.com",
            timeout=5,
        )

    except Exception as exc:
        print("Request failed")
        print("Type:", type(exc).__name__)
        print("Message:", exc)


if __name__ == "__main__":
    main()
```

Flow:

```text
URL
 ↓
DNS lookup
 ↓
Không tìm thấy IP
 ↓
Exception
```

---

# 9. SSL Error

SSL/TLS cũng có thể gây lỗi.

Ví dụ:

```python
import primp


def main():
    client = primp.Client()

    try:
        response = client.get(
            "https://expired.badssl.com/",
            timeout=5,
        )

        print(response.status_code)

    except Exception as exc:
        print("Request failed")
        print("Type:", type(exc).__name__)
        print("Message:", exc)


if __name__ == "__main__":
    main()
```

Điểm quan trọng:

```text
SSL failure
    ↓
không có HTTP Response bình thường
    ↓
Exception
```

Ta sẽ học SSL/Verify kỹ hơn ở **Buổi 15**.

---

# 10. HTTP 404 không nhất thiết Exception

Đây là một bài test rất quan trọng.

```python
import primp


def main():
    client = primp.Client()

    response = client.get(
        "https://httpbin.org/status/404"
    )

    print("Status:", response.status_code)
    print("URL:", response.url)


if __name__ == "__main__":
    main()
```

Kết quả:

```text
Status: 404
```

Tức là:

```text
Request
   ↓
Server
   ↓
404
   ↓
Response
```

Không nên nhầm:

```text
404 = Exception
```

---

# 11. 500 cũng vậy

```python
import primp


def main():
    client = primp.Client()

    response = client.get(
        "https://httpbin.org/status/500"
    )

    print("Status:", response.status_code)


if __name__ == "__main__":
    main()
```

Ta có:

```text
Response
   │
   └── status_code = 500
```

Đây là **HTTP-level failure**, khác với **network-level exception**.

---

# 12. Hai tầng lỗi

Đây là kiến thức rất quan trọng đối với crawler.

## Tầng 1 — Transport/Network

```text
DNS
Connection
Timeout
SSL
Proxy
```

→ Exception

---

## Tầng 2 — HTTP

```text
400
401
403
404
408
429
500
502
503
504
```

→ Response

---

Mô hình:

```text
                 Request
                    │
                    ▼
              Network Layer
                    │
          ┌─────────┴─────────┐
          │                   │
       Failure              Success
          │                   │
      Exception               ▼
                    HTTP Response
                         │
                ┌────────┴────────┐
                │                 │
              2xx              4xx/5xx
                │                 │
             Success          HTTP Error
```

Đây chính là nền tảng cho **Error Classification** sau này.

---

# 13. Viết Fetcher bắt Exception

Bây giờ quay lại architecture của Novel Crawler.

Ta có:

```text
Application
     │
     ▼
Fetcher Interface
     │
     ▼
PrimpFetcher
     │
     ▼
primp
```

Fetcher không nên để toàn bộ exception thô tràn lên Application.

Phiên bản đơn giản:

```python
import primp


class PrimpFetcher:

    def __init__(self, timeout: float = 10):
        self.client = primp.Client()
        self.default_timeout = timeout

    def get(
        self,
        url: str,
        timeout: float | None = None,
    ):
        if timeout is None:
            timeout = self.default_timeout

        try:
            return self.client.get(
                url,
                timeout=timeout,
            )

        except Exception as exc:
            print("Fetch failed:")
            print("URL:", url)
            print("Error:", type(exc).__name__)
            print("Message:", exc)

            raise
```

---

# 14. Tại sao lại `raise`?

Đừng làm:

```python
except Exception:
    return None
```

Ví dụ:

```python
response = fetcher.get(url)

if response is None:
    ...
```

Cách này làm mất thông tin lỗi.

Tệ hơn nữa:

```text
DNS error
Timeout
SSL error
Connection error
```

đều biến thành:

```python
None
```

Application không biết chuyện gì xảy ra.

---

Thay vào đó:

```python
except Exception as exc:
    log_error(exc)
    raise
```

`raise` giữ nguyên exception để tầng trên xử lý.

Flow:

```text
primp
  │
  ▼
Exception
  │
  ▼
PrimpFetcher
  │
  ├── log
  │
  └── raise
        │
        ▼
Application
```

---

# 15. `raise` khác `raise exc`

Có một chi tiết Python rất đáng nhớ.

Nên viết:

```python
except Exception:
    raise
```

thay vì:

```python
except Exception as exc:
    raise exc
```

Trong trường hợp re-raise exception, `raise` giữ traceback tự nhiên tốt hơn.

Ví dụ:

```python
try:
    ...
except Exception:
    raise
```

Đây là pattern rất phổ biến.

---

# 16. Logging thay vì `print`

Vì bạn đã học `logging deep dive`, crawler thực tế nên dùng:

```python
import logging
import primp


logger = logging.getLogger(__name__)


class PrimpFetcher:

    def __init__(self, timeout: float = 10):
        self.client = primp.Client()
        self.default_timeout = timeout

    def get(
        self,
        url: str,
        timeout: float | None = None,
    ):
        if timeout is None:
            timeout = self.default_timeout

        try:
            return self.client.get(
                url,
                timeout=timeout,
            )

        except Exception:
            logger.exception(
                "Request failed: %s",
                url,
            )
            raise
```

`logger.exception()` rất hữu ích vì nó tự ghi traceback khi đang ở trong `except`.

---

# 17. Không bắt lỗi quá sớm

Một lỗi kiến trúc thường gặp:

```python
class PrimpFetcher:

    def get(self, url):
        try:
            return self.client.get(url)

        except Exception:
            return None
```

Sau đó:

```text
Parser
   ↓
None
```

Parser bắt đầu phải xử lý:

```python
if response is None:
    ...
```

Đây là thiết kế không tốt.

Parser không nên biết:

```text
Timeout
DNS
SSL
Proxy
Connection
```

Parser chỉ cần:

```text
Response → parse
```

---

# 18. Exception nên được xử lý ở đâu?

Kiến trúc hiện tại:

```text
                Application
                     │
                     ▼
             Fetcher Interface
                     │
                     ▼
              PrimpFetcher
                     │
                     ▼
                   primp
```

Exception:

```text
primp
  │
  ▼
Network Exception
  │
  ▼
PrimpFetcher
  │
  ├── log
  ├── classify (sau này)
  └── raise/domain error
          │
          ▼
      Application
```

Parser:

```text
Parser
  ↑
Response
```

không trực tiếp xử lý network exception.

---

# 19. Chuẩn bị cho Retry

Đây là lý do Buổi 12 rất quan trọng.

Không phải exception nào cũng nên retry.

Ví dụ:

| Lỗi              | Retry?                      |
| ---------------- | --------------------------- |
| Timeout          | Có thể                      |
| Connection error | Có thể                      |
| DNS error        | Có thể, tùy trường hợp      |
| SSL error        | Thường không retry liên tục |
| 404              | Thường không                |
| 403              | Không nên retry mù quáng    |
| 429              | Có thể, cần backoff         |
| 500              | Có thể                      |
| 502              | Có thể                      |
| 503              | Có thể                      |
| 504              | Có thể                      |

Sau này chúng ta sẽ xây:

```text
Exception
    │
    ▼
Error Classification
    │
    ├── Retryable
    │
    └── Non-Retryable
```

Nhưng **chưa xây RetryPolicy ở Buổi 12**. Nó thuộc các phần sau của roadmap.

---

# 20. Một Fetcher hoàn chỉnh của Buổi 12

Đây là phiên bản mình khuyên bạn giữ lại làm mốc:

```python
import logging

import primp


logger = logging.getLogger(__name__)


class PrimpFetcher:

    def __init__(self, timeout: float = 10):
        self.client = primp.Client()
        self.default_timeout = timeout

    def get(
        self,
        url: str,
        timeout: float | None = None,
    ):
        if timeout is None:
            timeout = self.default_timeout

        try:
            response = self.client.get(
                url,
                timeout=timeout,
            )

            return response

        except Exception:
            logger.exception(
                "GET request failed: %s",
                url,
            )
            raise


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    fetcher = PrimpFetcher(timeout=5)

    # Thành công
    response = fetcher.get(
        "https://httpbin.org/get"
    )

    print("Status:", response.status_code)

    # Exception
    try:
        fetcher.get(
            "https://domain-khong-ton-tai-xyz.com"
        )

    except Exception as exc:
        print()
        print("Caught by application:")
        print("Type:", type(exc).__name__)
        print("Message:", exc)


if __name__ == "__main__":
    main()
```

---

# 21. Test 4 trường hợp

Bạn nên tự tạo:

```text
lesson_12.py
```

và test lần lượt.

### Test 1 — Thành công

```python
fetcher.get("https://httpbin.org/get")
```

Kỳ vọng:

```text
Response
200
```

### Test 2 — 404

```python
response = fetcher.get(
    "https://httpbin.org/status/404"
)

print(response.status_code)
```

Kỳ vọng:

```text
404
```

**Không coi 404 là network exception.**

### Test 3 — Timeout

```python
fetcher = PrimpFetcher(timeout=2)

fetcher.get(
    "https://httpbin.org/delay/10"
)
```

Kỳ vọng:

```text
Exception
```

### Test 4 — DNS

```python
fetcher.get(
    "https://domain-khong-ton-tai-xyz.com"
)
```

Kỳ vọng:

```text
Exception
```

---

# 22. Bài tập Buổi 12

## Bài 1

Viết:

```python
safe_get(url)
```

trả về:

```text
Response nếu thành công
Exception nếu thất bại
```

---

## Bài 2

In:

```python
type(exc).__name__
str(exc)
```

khi request thất bại.

---

## Bài 3

Test:

```text
200
404
500
Timeout
DNS failure
```

và tự lập bảng:

```text
Case             Response?       Exception?
------------------------------------------------
200
404
500
Timeout
DNS
```

---

## Bài 4 — Quan trọng

Giải thích bằng lời của bạn:

> Tại sao `404` và `Timeout` phải được xử lý khác nhau?

Nếu bạn hiểu được câu này thì bạn đã nắm được nền tảng của **Error Classification**.

---

# 23. Kiến trúc chúng ta đang xây

Sau 12 buổi:

```text
                  Novel Crawler
                       │
                       ▼
                Application
                       │
                       ▼
                Fetcher Interface
                       │
                       ▼
                 PrimpFetcher
                       │
             ┌─────────┴─────────┐
             │                   │
          Success              Failure
             │                   │
             ▼                   ▼
          Response            Exception
             │                   │
             ▼                   ▼
           Parser          Logging / Handling
```

Và roadmap tiếp theo sẽ mở rộng thành:

```text
Exception
    │
    ▼
Error Classification
    │
    ├── Timeout
    ├── Connection
    ├── DNS
    ├── SSL
    ├── Proxy
    └── HTTP Error
             │
             ▼
        Retry Policy
```

**Buổi 13 — Authentication** sẽ chuyển sang một chủ đề mới: Basic Auth, Bearer Token, API Key, `Authorization` header và cách thiết kế authentication mà không làm `PrimpFetcher` bị phụ thuộc cứng vào một kiểu auth.
