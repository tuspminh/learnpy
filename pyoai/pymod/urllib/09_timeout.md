# Buổi 9: Timeout, Retry và Connection Handling

> Đây là một trong những buổi quan trọng nhất nếu bạn muốn viết **HTTP Client chuyên nghiệp**.

Trong các ví dụ trước, chúng ta thường viết:
    
    
    response = urlopen(url)

Nhưng trong môi trường thực tế, rất nhiều tình huống có thể xảy ra:

  * Server phản hồi quá chậm. 
  * Mất kết nối Internet. 
  * DNS không phân giải được. 
  * Server trả về lỗi 500. 
  * Server tạm thời quá tải (503). 
  * Kết nối bị reset giữa chừng. 
  * Timeout khi tải file lớn. 



Nếu không xử lý các tình huống này, chương trình của bạn sẽ rất dễ bị treo hoặc thất bại.

* * *

# Mục tiêu

Sau buổi học này, bạn sẽ:

  * Hiểu các loại Timeout. 
  * Hiểu Retry là gì. 
  * Biết khi nào nên Retry. 
  * Thiết kế `RetryPolicy`. 
  * Thiết kế `HttpClient` có khả năng chịu lỗi. 
  * Biết Exponential Backoff. 



* * *

# 1\. Timeout là gì?

Ví dụ:
    
    
    urlopen(url)

Nếu server không trả lời thì sao?
    
    
    Python
    
    ↓
    
    Đợi...
    
    ↓
    
    Đợi...
    
    ↓
    
    Đợi...
    
    ↓
    
    ???

Chương trình có thể treo rất lâu.

* * *

# 2\. Timeout trong urllib
    
    
    from urllib.request import urlopen
    
    response = urlopen(
        url,
        timeout=10
    )

Sau:
    
    
    10 giây

Python sẽ dừng chờ và phát sinh ngoại lệ.

* * *

# 3\. Các loại Timeout

Trong HTTP client hiện đại thường có:
    
    
    Connect Timeout
    
    Read Timeout
    
    Write Timeout
    
    Pool Timeout

`urllib` chỉ cho phép truyền một giá trị `timeout`, áp dụng cho các thao tác trên socket.

* * *

# 4\. Ví dụ Timeout
    
    
    from urllib.request import urlopen
    
    urlopen(
        "https://example.com",
        timeout=5
    )

Nếu quá 5 giây:
    
    
    TimeoutError

hoặc ngoại lệ liên quan đến socket sẽ được phát sinh.

* * *

# 5\. Bắt Timeout
    
    
    import socket
    from urllib.request import urlopen
    
    try:
    
        urlopen(
            url,
            timeout=5
        )
    
    except socket.timeout:
    
        print("Timeout")

Trong một số trường hợp, `urllib.error.URLError` sẽ bao bọc (`wrap`) lỗi timeout bên trong. Chúng ta sẽ xử lý điều này ở các buổi về `urllib.error`.

* * *

# 6\. Retry là gì?

Ví dụ:

Lần đầu:
    
    
    500

Lần hai:
    
    
    200

Nếu không Retry:
    
    
    FAILED

Nếu Retry:
    
    
    SUCCESS

* * *

# 7\. Khi nào nên Retry?

Nên:
    
    
    Timeout
    
    502
    
    503
    
    504
    
    Connection Reset

Không nên:
    
    
    400
    
    401
    
    403
    
    404

Vì đây thường là lỗi từ phía yêu cầu của client.

* * *

# 8\. Retry đơn giản
    
    
    for _ in range(3):
    
        try:
    
            response = urlopen(url)
    
            break
    
        except Exception:
    
            pass

Nhưng cách này còn quá đơn giản và không nên dùng trong dự án thực tế.

* * *

# 9\. Delay giữa các lần Retry

Không nên:
    
    
    Retry
    
    Retry
    
    Retry

Ngay lập tức.

Nên:
    
    
    Retry
    
    ↓
    
    1 giây
    
    ↓
    
    Retry
    
    ↓
    
    2 giây
    
    ↓
    
    Retry

* * *

# 10\. time.sleep()
    
    
    import time
    
    time.sleep(2)

* * *

# 11\. Exponential Backoff

Đây là kỹ thuật được hầu hết các SDK hiện đại sử dụng.

Ví dụ:
    
    
    Lần 1
    
    1 giây
    
    Lần 2
    
    2 giây
    
    Lần 3
    
    4 giây
    
    Lần 4
    
    8 giây

Thay vì gửi dồn dập các request khi server đang quá tải.

* * *

# 12\. Công thức
    
    
    delay = 2 ** retry

Ví dụ:
    
    
    for retry in range(5):
    
        print(
            2 ** retry
        )

Kết quả:
    
    
    1
    
    2
    
    4
    
    8
    
    16

* * *

# 13\. RetryPolicy

Thay vì viết:
    
    
    retry = 3

Ta tạo lớp:
    
    
    class RetryPolicy:
        ...

* * *

# 14\. Thiết kế
    
    
    class RetryPolicy:
    
        def __init__(
    
            self,
    
            retries=3,
    
            delay=1,
    
            backoff=2,
        ):
    
            self.retries = retries
    
            self.delay = delay
    
            self.backoff = backoff

* * *

# 15\. Tính Delay
    
    
    def get_delay(
        self,
        retry
    ):
    
        return (
            self.delay
            * (
                self.backoff
                ** retry
            )
        )

Ví dụ:
    
    
    1
    
    2
    
    4
    
    8

* * *

# 16\. HttpClient tích hợp Retry
    
    
    class HttpClient:
    
        def __init__(
    
            self,
    
            retry_policy=None,
        ):
    
            self.retry_policy = (
                retry_policy
            )

* * *

# 17\. Retry Loop
    
    
    policy = self.retry_policy
    
    for attempt in range(
        policy.retries
    ):
    
        try:
    
            return self._request(...)
    
        except Exception:
    
            ...

Lưu ý: Không nên bắt `Exception` một cách quá rộng trong mã nguồn thực tế. Chúng ta sẽ tinh chỉnh danh sách ngoại lệ cần retry ở các buổi tiếp theo.

* * *

# 18\. Delay
    
    
    import time
    
    delay = policy.get_delay(
        attempt
    )
    
    time.sleep(delay)

* * *

# 19\. Callback
    
    
    def on_retry(
    
        attempt,
    
        error,
    
        delay,
    ):
        ...

Ví dụ:
    
    
    Retry #2
    
    Timeout
    
    waiting 4s

Điều này rất hữu ích để log hoặc cập nhật giao diện.

* * *

# 20\. Kiến trúc
    
    
    HttpClient
    │
    ├── RetryPolicy
    ├── Downloader
    ├── Headers
    ├── MultipartEncoder
    └── ApiClient

* * *

# 21\. Thiết kế RetryPolicy nâng cao
    
    
    class RetryPolicy:
    
        retries = 5
    
        delay = 1
    
        backoff = 2
    
        retry_on = (
            TimeoutError,
        )

Sau này ta sẽ mở rộng:
    
    
    retry_on = (
    
        TimeoutError,
    
        ConnectionResetError,
    
        OSError,
    )

Hoặc xử lý dựa trên mã trạng thái HTTP (502, 503, 504).

* * *

# 22\. Jitter

Một vấn đề:

1000 client cùng Retry.
    
    
    1s
    
    ↓
    
    1000 request
    
    ↓
    
    Server chết tiếp

Giải pháp:
    
    
    1.2s
    
    0.9s
    
    1.7s
    
    1.4s

Thêm ngẫu nhiên:
    
    
    import random
    
    delay += random.random()

Đây gọi là **Jitter**.

* * *

# 23\. Retry có chọn lọc

Không phải request nào cũng nên Retry.

Ví dụ:
    
    
    POST
    
    ↓
    
    Tạo đơn hàng

Retry có thể tạo:
    
    
    2 đơn hàng

Vì vậy:
    
    
    GET
    
    ✓ Retry
    
    
    DELETE
    
    Tùy trường hợp
    
    
    POST
    
    Cẩn thận
    
    
    PUT
    
    Có thể Retry nếu API hỗ trợ idempotent

Khái niệm quan trọng ở đây là **idempotency** (tính lặp lại an toàn).

* * *

# 24\. Cấu trúc dự án
    
    
    httpclient/
    │
    ├── retry.py
    ├── client.py
    ├── api.py
    ├── downloader.py
    ├── multipart.py
    ├── headers.py
    ├── exceptions.py
    └── examples/

* * *

# Những lỗi thường gặp

## 1\. Retry vô hạn

Sai:
    
    
    while True:
    
        ...

Có thể khiến chương trình không bao giờ kết thúc.

Đúng:
    
    
    for _ in range(
        retries
    ):

* * *

## 2\. Retry cả lỗi 404
    
    
    404
    
    ↓
    
    Retry
    
    ↓
    
    404
    
    ↓
    
    Retry

Không có ý nghĩa.

* * *

## 3\. Không Sleep

Sai:
    
    
    Retry
    
    Retry
    
    Retry

Điều này có thể làm server quá tải hơn.

* * *

## 4\. Bắt tất cả ngoại lệ
    
    
    except Exception:

Trong thực tế, hãy bắt các ngoại lệ cụ thể như:

  * `socket.timeout`
  * `ConnectionResetError`
  * `urllib.error.URLError` (khi nguyên nhân là lỗi mạng) 



và chỉ retry với các lỗi có khả năng thành công ở lần sau.

* * *

# Bài tập

## Bài 1

Viết:
    
    
    class RetryPolicy:

Có:

  * retries 
  * delay 
  * backoff 
  * `get_delay()`



* * *

## Bài 2

Viết:
    
    
    retry(
        func
    )

Tự động:

  * Retry 
  * Sleep 
  * Exponential Backoff 



Gợi ý:
    
    
    def retry(func, policy):
        ...

* * *

## Bài 3

Tích hợp `RetryPolicy` vào `HttpClient`.

Đảm bảo mọi request đều sử dụng cùng một chính sách retry.

* * *

## Bài 4

Viết callback:
    
    
    on_retry(
        attempt,
        delay,
        error
    )

Hiển thị:
    
    
    Retry #2
    Timeout
    Waiting 4s...

* * *

# Thiết kế hướng Framework

Đến buổi 9, chúng ta đã có khá nhiều thành phần:
    
    
    httpclient/
    │
    ├── client.py
    ├── api.py
    ├── downloader.py
    ├── multipart.py
    ├── retry.py
    ├── headers.py
    ├── exceptions.py
    ├── response.py
    └── examples/

Đây không còn là các ví dụ rời rạc mà đã bắt đầu hình thành một **framework HTTP client** có thể tái sử dụng cho nhiều dự án.

# Tổng kết

Trong buổi học này, bạn đã nắm được:

  * Vai trò của `timeout` trong `urllib`. 
  * Khi nào nên và không nên retry. 
  * Exponential Backoff và Jitter. 
  * Thiết kế lớp `RetryPolicy`. 
  * Tích hợp retry vào `HttpClient`. 
  * Những lưu ý về idempotency khi retry các phương thức HTTP. 



Ở **buổi 10** , chúng ta sẽ học **Authentication Deep Dive** , bao gồm:

  * Basic Authentication 
  * Bearer Token 
  * API Key 
  * Digest Authentication 
  * OAuth 2.0 (tổng quan) 
  * `urllib.request.HTTPBasicAuthHandler`
  * `HTTPPasswordMgr`
  * Thiết kế `AuthProvider` để hỗ trợ nhiều cơ chế xác thực trong cùng một `HttpClient`.

