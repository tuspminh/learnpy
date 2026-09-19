# Buổi 35 — Timeout + Retry

Đến đây crawler của chúng ta đã có:

```text
31 AsyncClient
32 async GET
33 Concurrent Requests
34 Semaphore
```

Nhưng một crawler thực tế sẽ gặp:

```text
HTTP request
     │
     ├── success
     │
     ├── timeout
     ├── connection error
     ├── SSL error
     ├── 429
     ├── 500
     └── ...
```

Vì vậy hôm nay chúng ta xây:

```text
Request
   ↓
Timeout
   ↓
Exception / Response
   ↓
Retry Policy
   ↓
Retry?
   ├── YES → request lại
   └── NO  → fail
```

Mục tiêu quan trọng nhất của Buổi 35 là **không viết retry một cách tùy tiện**.

---

# 1. Timeout và Retry là hai vấn đề khác nhau

### Timeout

Timeout trả lời:

> Request được phép chờ tối đa bao lâu?

Ví dụ:

```python
response = await client.get(
    url,
    timeout=10,
)
```

### Retry

Retry trả lời:

> Nếu request thất bại, có nên thử lại không? Nếu có thì bao nhiêu lần?

Ví dụ:

```text
GET
 ↓
timeout
 ↓
retry #1
 ↓
timeout
 ↓
retry #2
 ↓
success
```

Do đó:

```text
Timeout ≠ Retry
```

---

# 2. Vì sao timeout bắt buộc phải có?

Không có timeout, một crawler có thể gặp:

```text
Request 1 ──────────────── ?
Request 2 ──────────────── ?
Request 3 ──────────────── ?
```

Một request treo quá lâu có thể giữ:

* task;
* semaphore slot;
* connection;
* tài nguyên crawler.

Ta muốn:

```text
GET
 ↓
10 seconds
 ↓
không có kết quả
 ↓
timeout
 ↓
retry / fail
```

---

# 3. Timeout đơn giản

Với `primp.AsyncClient`:

```python
response = await client.get(
    url,
    timeout=10,
)
```

Ví dụ:

```python id="g0n5qe"
import asyncio

import primp


async def main():

    async with primp.AsyncClient(
        impersonate="chrome_146",
        impersonate_os="windows",
    ) as client:

        try:

            response = await client.get(
                "https://httpbin.org/delay/10",
                timeout=2,
            )

            print(
                response.status_code
            )

        except Exception as exc:

            print(
                "ERROR:",
                type(exc).__name__,
                exc,
            )


if __name__ == "__main__":
    asyncio.run(main())
```

Điểm cần nhớ:

```text
timeout=2
```

không có nghĩa:

> Server phải trả HTTP 2xx trong 2 giây.

Nó là giới hạn thời gian của request operation theo API của client.

---

# 4. Đừng bắt đầu bằng `except Exception: retry`

Một cách rất dễ viết:

```python
try:
    response = await client.get(url)
except Exception:
    await client.get(url)
```

Nhưng đây là retry rất tệ.

Vì exception có thể là:

```text
DNS failure
Connection failure
Timeout
SSL failure
Invalid URL
...
```

Và HTTP failure có thể **không phải exception**:

```text
404
500
502
503
429
```

Cho nên trước khi retry, chúng ta cần phân loại.

---

# 5. Retry cái gì?

Có thể chia thành hai nhóm lớn.

## Nhóm A — Exception

Ví dụ:

```text
Timeout
Connection error
Temporary network error
```

Một số lỗi dạng này **có thể** retry.

## Nhóm B — HTTP status

Ví dụ:

```text
429
500
502
503
504
```

Một số status **có thể** retry.

Trong khi:

```text
400
401
403
404
```

thường không nên tự động retry vô hạn.

Nhưng đây là **policy**, không phải quy luật tuyệt đối.

---

# 6. Retry phải có giới hạn

Không bao giờ:

```python
while True:
    retry()
```

Crawler có thể bị kẹt mãi.

Ta cần:

```text
max_attempts = 3
```

Ví dụ:

```text
attempt 1
   ↓
failed
   ↓
attempt 2
   ↓
failed
   ↓
attempt 3
   ↓
failed
   ↓
give up
```

---

# 7. `max_attempts` và `max_retries`

Hai cách đặt tên rất dễ nhầm.

### `max_attempts=3`

Tổng cộng tối đa 3 lần request:

```text
1 + 2 + 3
```

### `max_retries=3`

Request ban đầu + 3 lần retry:

```text
initial
retry 1
retry 2
retry 3
```

Tổng cộng:

```text
4 attempts
```

Trong course này tôi khuyên dùng:

```python
max_attempts
```

vì dễ hiểu hơn.

---

# 8. Retry Policy

Đừng nhét policy vào HTTP client.

Ta tạo một object đơn giản:

```python id="z3o7qv"
from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
```

Ví dụ:

```python
policy = RetryPolicy(
    max_attempts=3
)
```

---

# 9. Retry loop cơ bản

```python id="7gux5k"
async def fetch_with_retry(
    client,
    url,
    policy,
):

    for attempt in range(
        1,
        policy.max_attempts + 1,
    ):

        try:

            response = await client.get(
                url,
                timeout=10,
            )

            return response

        except Exception as exc:

            print(
                f"Attempt {attempt} failed:",
                type(exc).__name__,
            )

    raise RuntimeError(
        f"Request failed after "
        f"{policy.max_attempts} attempts"
    )
```

Đây mới chỉ là **khung retry**.

Chưa phải production retry.

---

# 10. Vấn đề của code trên

Giả sử:

```text
404
```

`client.get()` có thể vẫn trả response:

```python
response.status_code == 404
```

Không đi vào:

```python
except Exception
```

Do đó retry logic phải kiểm tra cả:

```text
Exception
+
HTTP status
```

---

# 11. Xác định retryable status

Ta có thể bắt đầu đơn giản:

```python id="y9g4ur"
RETRYABLE_STATUS_CODES = {
    429,
    500,
    502,
    503,
    504,
}
```

Sau đó:

```python
if response.status_code in RETRYABLE_STATUS_CODES:
    ...
```

Còn:

```python
404
```

thì thường kết thúc ngay.

---

# 12. Retry response

Ví dụ:

```python id="h9w5jq"
async def fetch_with_retry(
    client,
    url,
    policy,
):

    for attempt in range(
        1,
        policy.max_attempts + 1,
    ):

        try:

            response = await client.get(
                url,
                timeout=10,
            )

            if response.status_code not in {
                429,
                500,
                502,
                503,
                504,
            }:
                return response

            print(
                f"HTTP {response.status_code}, "
                f"attempt={attempt}"
            )

        except Exception as exc:

            print(
                f"Exception "
                f"attempt={attempt}: "
                f"{type(exc).__name__}"
            )

    raise RuntimeError(
        f"Request failed: {url}"
    )
```

Nhưng vẫn còn thiếu một thứ rất quan trọng:

```text
Backoff
```

---

# 13. Tại sao không retry ngay lập tức?

Không nên:

```text
fail
 ↓
retry
 ↓
fail
 ↓
retry
 ↓
fail
 ↓
retry
```

liên tục trong vài milliseconds.

Điều này có thể:

* tiếp tục gây áp lực lên server;
* gặp rate limit;
* làm network congestion tệ hơn;
* khiến nhiều crawler retry cùng lúc.

Ta cần chờ.

---

# 14. Fixed Backoff

Đơn giản nhất:

```python
await asyncio.sleep(2)
```

Ví dụ:

```text
attempt 1
 ↓
fail
 ↓
wait 2s
 ↓
attempt 2
 ↓
fail
 ↓
wait 2s
 ↓
attempt 3
```

Đây là:

```text
Fixed Backoff
```

---

# 15. Exponential Backoff

Phổ biến hơn:

```text
retry 1 → 1s
retry 2 → 2s
retry 3 → 4s
retry 4 → 8s
```

Công thức:

```python
delay = base_delay * 2 ** (attempt - 1)
```

Ví dụ:

```python id="u1c7x4"
base_delay = 1

for attempt in range(1, 5):

    delay = base_delay * (
        2 ** (attempt - 1)
    )

    print(delay)
```

Kết quả:

```text
1
2
4
8
```

---

# 16. Exponential Backoff + Jitter

Nếu 1.000 crawler cùng retry:

```text
t = 0
1000 requests fail

t = 1
1000 requests retry

t = 3
1000 requests retry

t = 7
1000 requests retry
```

Có thể tạo ra "thundering herd".

Ta thêm random jitter:

```text
1.13s
2.72s
4.18s
8.64s
```

Thay vì tất cả cùng retry chính xác cùng thời điểm.

---

# 17. Retry Policy hoàn chỉnh hơn

Ta có thể thiết kế:

```python id="u2a6nq"
from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:

    max_attempts: int = 3

    base_delay: float = 1.0

    max_delay: float = 30.0

    retryable_statuses: frozenset[int] = frozenset({
        429,
        500,
        502,
        503,
        504,
    })
```

Ý nghĩa:

```text
max_attempts
    ↓
số lần thử tối đa

base_delay
    ↓
delay ban đầu

max_delay
    ↓
không cho delay tăng vô hạn

retryable_statuses
    ↓
HTTP status nào được retry
```

---

# 18. Tính backoff

```python
def calculate_delay(
    policy: RetryPolicy,
    attempt: int,
) -> float:

    delay = policy.base_delay * (
        2 ** (attempt - 1)
    )

    return min(
        delay,
        policy.max_delay,
    )
```

Test:

```python
policy = RetryPolicy(
    base_delay=1,
    max_delay=10,
)

for attempt in range(1, 8):
    print(
        attempt,
        calculate_delay(
            policy,
            attempt,
        ),
    )
```

Kết quả:

```text
1 → 1
2 → 2
3 → 4
4 → 8
5 → 10
6 → 10
7 → 10
```

---

# 19. Retry với jitter

Thêm:

```python
import random


def calculate_delay(
    policy: RetryPolicy,
    attempt: int,
) -> float:

    delay = policy.base_delay * (
        2 ** (attempt - 1)
    )

    delay = min(
        delay,
        policy.max_delay,
    )

    jitter = random.uniform(
        0,
        delay * 0.25,
    )

    return delay + jitter
```

Ví dụ:

```text
base = 4s
jitter = 0.73s

→ 4.73s
```

Mục đích của jitter là tránh các task retry đồng bộ.

---

# 20. Nhưng hôm nay chưa cần quá phức tạp

Để học architecture, trước tiên dùng:

```text
RetryPolicy
    ↓
max_attempts
base_delay
max_delay
retryable_statuses
```

Sau này có thể tách:

```text
BackoffStrategy
```

nếu project thực sự cần nhiều chiến lược.

---

# 21. `RetryPolicy` không nên biết `primp`

Đây là DDD/SOLID rất quan trọng.

Không nên:

```python
class RetryPolicy:
    def retry_primp_error(...):
        ...
```

Policy nên biết:

```text
attempt
status
exception
```

chứ không cần biết:

```text
primp.Client
primp.AsyncClient
```

Tốt hơn:

```text
Application / Infrastructure
          ↓
     Retry Policy
          ↓
       decision
          ↓
      HTTP client
```

---

# 22. Một abstraction nhỏ: `should_retry`

```python
def should_retry(
    policy: RetryPolicy,
    *,
    attempt: int,
    status_code: int | None = None,
    exception: Exception | None = None,
) -> bool:

    if attempt >= policy.max_attempts:
        return False

    if exception is not None:
        return True

    if status_code in policy.retryable_statuses:
        return True

    return False
```

Đây là bước đầu của **Retry Decision**.

---

# 23. Nhưng retry mọi Exception có tốt không?

Không.

Ví dụ:

```text
Invalid URL
```

không cần retry.

```text
Authentication error
```

thường không giải quyết bằng retry.

```text
Programming bug
```

không nên retry.

Do đó trong architecture production ta cần:

```text
Exception
    ↓
Error Classifier
    ↓
Transient?
    ├── YES → retry
    └── NO  → fail
```

Chúng ta sẽ quay lại vấn đề này ở:

```text
Buổi 48 — Error Classification
```

Hiện tại chỉ cần hiểu nguyên tắc.

---

# 24. Retry HTTP 429

`429 Too Many Requests` đặc biệt quan trọng với crawler.

Server có thể trả:

```text
429
```

và đôi khi có:

```text
Retry-After
```

Ví dụ:

```text
Retry-After: 5
```

Khi đó server đang nói:

> Hãy đợi rồi thử lại.

Do đó retry strategy nên có khả năng ưu tiên `Retry-After` khi có giá trị hợp lệ.

Đây là một điểm rất quan trọng khi sau này kết hợp:

```text
Semaphore
+
Rate Limiter
+
Retry
```

---

# 25. Retry-After concept

Ví dụ:

```python
retry_after = response.headers.get(
    "Retry-After"
)
```

Nếu có:

```text
Retry-After: 5
```

ta có thể chờ:

```python
await asyncio.sleep(5)
```

thay vì tự tính:

```text
1s
2s
4s
```

Trong production cần parse header cẩn thận vì `Retry-After` có thể biểu diễn delay hoặc HTTP date.

---

# 26. Một `RetryExecutor`

Ta có thể gom retry loop:

```python id="8x7xjm"
import asyncio


class RetryExecutor:

    def __init__(
        self,
        policy: RetryPolicy,
    ):
        self.policy = policy

    async def execute(
        self,
        operation,
    ):
        ...
```

Nhưng **chưa nên triển khai abstraction này ngay** nếu chưa cần.

Với crawler hiện tại, một function:

```python
fetch_with_retry()
```

là đủ để hiểu.

---

# 27. Complete example

Đây là phiên bản đầy đủ vừa đủ cho Buổi 35:

```python id="m3b1tj"
import asyncio
from dataclasses import dataclass

import primp


@dataclass(frozen=True)
class RetryPolicy:

    max_attempts: int = 3

    base_delay: float = 1.0

    max_delay: float = 10.0

    retryable_statuses: frozenset[int] = frozenset({
        429,
        500,
        502,
        503,
        504,
    })


def calculate_delay(
    policy: RetryPolicy,
    attempt: int,
) -> float:

    delay = policy.base_delay * (
        2 ** (attempt - 1)
    )

    return min(
        delay,
        policy.max_delay,
    )


async def fetch_with_retry(
    client: primp.AsyncClient,
    url: str,
    policy: RetryPolicy,
):
    last_exception = None

    for attempt in range(
        1,
        policy.max_attempts + 1,
    ):

        try:

            print(
                f"[attempt={attempt}] "
                f"GET {url}"
            )

            response = await client.get(
                url,
                timeout=10,
            )

            if (
                response.status_code
                not in policy.retryable_statuses
            ):
                return response

            print(
                f"HTTP {response.status_code}"
            )

            if attempt < policy.max_attempts:

                delay = calculate_delay(
                    policy,
                    attempt,
                )

                print(
                    f"Retry in {delay:.2f}s"
                )

                await asyncio.sleep(
                    delay
                )

        except Exception as exc:

            last_exception = exc

            print(
                f"Exception: "
                f"{type(exc).__name__}"
            )

            if attempt < policy.max_attempts:

                delay = calculate_delay(
                    policy,
                    attempt,
                )

                print(
                    f"Retry in {delay:.2f}s"
                )

                await asyncio.sleep(
                    delay
                )

    if last_exception is not None:
        raise last_exception

    raise RuntimeError(
        f"Request failed after "
        f"{policy.max_attempts} attempts: "
        f"{url}"
    )


async def main():

    policy = RetryPolicy(
        max_attempts=3,
        base_delay=1,
        max_delay=5,
    )

    async with primp.AsyncClient(
        impersonate="chrome_146",
        impersonate_os="windows",
    ) as client:

        response = await fetch_with_retry(
            client,
            "https://httpbin.org/get",
            policy,
        )

        print()
        print(
            "SUCCESS:",
            response.status_code,
        )


if __name__ == "__main__":
    asyncio.run(main())
```

---

# 28. Kết hợp Semaphore + Retry

Đây là phần rất quan trọng.

Ta đã có:

```text
Buổi 34
Semaphore
```

và:

```text
Buổi 35
Retry
```

Có thể ghép:

```python
async def fetch_one(
    client,
    semaphore,
    policy,
    url,
):
    async with semaphore:

        return await fetch_with_retry(
            client,
            url,
            policy,
        )
```

Flow:

```text
gather()
   ↓
Semaphore(10)
   ↓
fetch_one()
   ↓
Retry Policy
   ↓
primp.AsyncClient
   ↓
HTTP
```

---

# 29. Nhưng có một vấn đề architecture

Giả sử:

```text
Semaphore = 10
```

Request A timeout.

Nếu:

```python
async with semaphore:
    await retry(...)
```

thì A giữ **một semaphore slot trong toàn bộ quá trình retry**.

Ví dụ:

```text
A attempt 1
   ↓
timeout
   ↓
wait 2s
   ↓
A attempt 2
   ↓
timeout
   ↓
wait 4s
   ↓
A attempt 3
```

Trong toàn bộ thời gian đó:

```text
A vẫn giữ slot
```

Điều này có thể là policy đúng hoặc không, tùy crawler.

Ở level hiện tại, **giữ slot cho toàn bộ logical fetch** là cách đơn giản và dễ hiểu.

Sau này nếu cần tối ưu concurrency/retry behavior, ta sẽ thiết kế kỹ hơn.

---

# 30. Retry + Semaphore + 100 chapters

Ví dụ:

```text
100 chapters
     ↓
gather()
     ↓
Semaphore(10)
     ↓
10 logical fetches
     ↓
     ├── chapter 1 → success
     ├── chapter 2 → timeout → retry
     ├── chapter 3 → success
     ├── chapter 4 → 500 → retry
     └── ...
```

Trong khi retry:

```text
chapter 2
    ↓
backoff
    ↓
retry
```

Các task khác vẫn có thể tiếp tục tùy semaphore slot và trạng thái của chúng.

---

# 31. Retry không có nghĩa request chắc chắn thành công

Ví dụ:

```text
404
```

Ta không retry.

```text
500
```

retry.

Nhưng:

```text
500
500
500
```

sau 3 attempts:

```text
FAILED
```

Kết quả cuối cùng phải phản ánh thất bại.

Không được biến:

```text
failed
```

thành:

```text
success
```

chỉ vì retry đã chạy.

---

# 32. Retry Policy và DDD/SOLID

Architecture:

```text
Application
    │
    ↓
AsyncFetcher
    │
    ├── Semaphore
    │
    ├── RetryPolicy
    │
    └── BrowserClient
             │
             ↓
        primp.AsyncClient
```

`RetryPolicy` là policy/configuration.

Nó không nên biết:

```text
selectolax
SQLite
Novel
Chapter
```

Domain cũng không nên import:

```python
import primp
```

---

# 33. Vị trí của Retry trong Clean Architecture

Một cách nhìn:

```text
┌───────────────────────────────┐
│         Application           │
│                               │
│   CrawlChapter                │
└──────────────┬────────────────┘
               │
               ↓
┌───────────────────────────────┐
│      Infrastructure           │
│                               │
│   AsyncFetcher                │
│      ├── Semaphore            │
│      ├── Retry Policy         │
│      └── Browser Client       │
│             ↓                 │
│        primp.AsyncClient      │
└───────────────────────────────┘
```

Domain:

```text
Novel
Chapter
CrawlTask
```

không cần biết Retry hoạt động thế nào.

---

# 34. Retry và idempotency

Đây là kiến thức rất quan trọng.

GET thường được xem là phù hợp hơn cho retry tự động vì nó được thiết kế để lấy resource mà không yêu cầu tạo side effect mới.

Ví dụ:

```text
GET /chapter/100
```

retry tương đối tự nhiên.

Nhưng:

```text
POST /payment
```

retry có thể nguy hiểm nếu request đã được server xử lý nhưng client không nhận được response.

Vì vậy:

```text
Retry Policy
```

không chỉ dựa vào:

```text
Exception
```

mà còn phải xem:

```text
HTTP method
+
request semantics
+
status
```

Đây sẽ rất quan trọng khi sau này `Request Model` được xây ở Buổi 41.

---

# 35. Retry trong Novel Crawler

Với crawler của chúng ta:

```text
GET chapter
```

thường là workload phù hợp với retry.

Ví dụ:

```text
Chapter 120
    ↓
GET
    ↓
timeout
    ↓
wait 1.3s
    ↓
GET
    ↓
503
    ↓
wait 2.6s
    ↓
GET
    ↓
200
    ↓
Parser
```

Sau đó:

```text
HTML
 ↓
selectolax
 ↓
Chapter
 ↓
Repository
```

---

# 36. Một lỗi cần tránh: retry cả parsing

Không nên:

```python
try:
    response = await fetch()
    chapter = parser.parse(response.text)
    repository.save(chapter)

except Exception:
    retry()
```

Vì nếu:

```text
HTTP thành công
Parser lỗi
```

thì retry HTTP có thể hoàn toàn vô ích.

Tách:

```text
HTTP Retry
     ↓
Response
     ↓
Parser
     ↓
Parse Error
```

Retry policy HTTP chỉ nên chịu trách nhiệm cho HTTP operation.

---

# 37. Test retry mà không cần phụ thuộc Internet

Đây là cách tốt hơn để unit test.

Tạo fake client:

```python id="9h4z3k"
class FakeResponse:

    def __init__(
        self,
        status_code: int,
    ):
        self.status_code = status_code


class FakeClient:

    def __init__(self):
        self.calls = 0

    async def get(
        self,
        url,
        timeout=None,
    ):
        self.calls += 1

        if self.calls < 3:
            return FakeResponse(500)

        return FakeResponse(200)
```

Test:

```python id="g6tr3s"
async def main():

    client = FakeClient()

    policy = RetryPolicy(
        max_attempts=3,
        base_delay=0.01,
        max_delay=0.1,
    )

    response = await fetch_with_retry(
        client,
        "http://test",
        policy,
    )

    print(
        "status:",
        response.status_code,
    )

    print(
        "calls:",
        client.calls,
    )
```

Kết quả:

```text
status: 200
calls: 3
```

Đây là test rất có giá trị.

---

# 38. Test case nên có

Sau này unit test:

```text
1. success ngay lần đầu
2. timeout → success
3. 500 → success
4. 500 → 500 → success
5. 500 → 500 → 500 → fail
6. 404 → không retry
7. 429 → retry
8. max_attempts
9. backoff
10. exception được propagate
```

Đây mới là retry implementation đáng tin cậy.

---

# 39. Bài tập thực hành

### Bài 1 — Timeout

Gọi:

```text
https://httpbin.org/delay/5
```

với:

```python
timeout=1
```

Quan sát exception.

---

### Bài 2 — Fake retry

Tạo:

```text
FakeClient
```

cho:

```text
attempt 1 → 500
attempt 2 → 500
attempt 3 → 200
```

Kết quả phải:

```text
calls = 3
status = 200
```

---

### Bài 3 — Không retry 404

Fake:

```text
404
```

Đảm bảo:

```text
calls = 1
```

---

### Bài 4 — Retry exhausted

Fake:

```text
500
500
500
500
...
```

với:

```python
max_attempts=3
```

Đảm bảo chỉ có:

```text
3 attempts
```

---

# 40. Bài tập chính

Hãy tự xây:

```python
class RetryPolicy:
    ...
```

với:

```text
max_attempts
base_delay
max_delay
retryable_statuses
```

và:

```python
async def fetch_with_retry(
    client,
    url,
    policy,
):
    ...
```

Yêu cầu:

```text
✓ timeout
✓ retry HTTP 429
✓ retry 500
✓ retry 502
✓ retry 503
✓ retry 504
✓ exponential backoff
✓ max_attempts
✓ không retry 404
✓ không tạo AsyncClient mới
✓ không parse HTML
✓ không truy cập database
```

---

# 41. Kiến trúc sau Buổi 35

Bây giờ crawler đã tiến thêm một bước lớn:

```text
                       Application
                            │
                            ↓
                    AsyncNovelFetcher
                            │
                   ┌────────┴────────┐
                   ↓                 ↓
              Semaphore         RetryPolicy
                   │                 │
                   └────────┬────────┘
                            ↓
                    AsyncBrowserClient
                            │
                            ↓
                   primp.AsyncClient
                            │
                            ↓
                           HTTP
```

Và HTTP flow:

```text
                 GET
                  │
                  ↓
               Timeout
                  │
          ┌───────┴────────┐
          ↓                ↓
       Response         Exception
          │                │
          ↓                ↓
    status check      retry decision
          │                │
          └───────┬────────┘
                  ↓
             Retry Policy
                  │
             ┌────┴────┐
             ↓         ↓
           retry      fail
             │
             ↓
          backoff
             │
             ↓
            GET
```

---

# 42. Roadmap

```text
31. AsyncClient             ✅
32. async GET               ✅
33. Concurrent Requests     ✅
34. Semaphore               ✅
35. Timeout + Retry         ✅
36. Proxy Pool              ← tiếp theo
37. User-Agent / Browser Profile Pool
38. Rate Limiting
39. Fetcher Architecture
40. Async Novel Fetcher
```

**Điểm mấu chốt của Buổi 35:**

```text
Timeout
    =
request được phép chờ bao lâu

Retry
    =
sau failure có thử lại không

Backoff
    =
giữa các lần retry chờ bao lâu

Retry Policy
    =
quyết định tất cả những điều trên
```

Và trong Novel Crawler, flow bắt đầu trở thành:

```text
Chapter URLs
     ↓
gather()
     ↓
Semaphore
     ↓
Timeout
     ↓
Retry Policy
     ↓
Primp AsyncClient
     ↓
Response
     ↓
Parser
```

Buổi 36 sẽ đưa **Proxy Pool** vào đúng vị trí trong flow này, từ một `ProxyConfig` đơn lẻ đã học ở Buổi 14 sang **nhiều proxy + chọn proxy + rotation + proxy failure handling**.
