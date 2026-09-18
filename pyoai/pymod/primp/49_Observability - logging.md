# Buổi 49 — Observability / Logging

Ở Buổi 48, chúng ta đã xây được:

```text
HTTP / Exception
        ↓
ErrorClassifier
        ↓
FetchError
        ↓
RetryPolicy
        ↓
RetryDecision
```

Nhưng khi crawler chạy hàng nghìn chapter, một vấn đề mới xuất hiện:

> **Làm sao biết crawler đang làm gì và tại sao nó thất bại?**

Ví dụ chỉ có:

```text
ERROR: request failed
```

thì gần như vô dụng.

Ta cần biết:

```text
URL
attempt
status
proxy
browser profile
error
retry
delay
elapsed time
```

Đó chính là **Observability**.

---

# 1. Observability là gì?

Trong Fetcher, ta muốn trả lời được 3 nhóm câu hỏi:

```text
1. Request đã xảy ra chuyện gì?
2. Request mất bao lâu?
3. Request thất bại vì nguyên nhân nào?
```

Ba trụ cột phổ biến:

```text
Observability
├── Logs
├── Metrics
└── Traces
```

Trong Buổi 49, ta tập trung vào:

```text
Logs
+
structured logging
+
request context
+
timing
```

Metrics/tracing chỉ giới thiệu để chuẩn bị Buổi 50.

---

# 2. Logging không phải `print()`

Không nên:

```python
print("request failed")
```

Production crawler cần:

```python
logger.error(
    "fetch failed",
    extra={
        "url": request.url,
        "attempt": attempt,
        "status": response.status_code,
    },
)
```

Vì logger có thể:

```text
console
file
JSON
monitoring system
```

và có level:

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

---

# 3. Logging trong Novel Crawler

Ta muốn một request có lifecycle:

```text
request started
       ↓
attempt 1
       ↓
503
       ↓
retry
       ↓
attempt 2
       ↓
200
       ↓
request completed
```

Log tương ứng:

```text
INFO  fetch.start
WARNING fetch.retry
INFO  fetch.success
```

---

# 4. Không log mọi thứ ở mọi level

Quy tắc đơn giản:

| Level    | Dùng cho                    |
| -------- | --------------------------- |
| DEBUG    | chi tiết kỹ thuật           |
| INFO     | lifecycle bình thường       |
| WARNING  | retry / vấn đề tạm thời     |
| ERROR    | request thất bại            |
| CRITICAL | hệ thống không thể tiếp tục |

Ví dụ:

```text
DEBUG → selected context
INFO  → request started
WARNING → 503, retry
INFO → request succeeded
```

---

# 5. Tạo module logging

Cấu trúc:

```text
src/
└── crawler/
    └── infrastructure/
        └── logging/
            ├── __init__.py
            ├── config.py
            └── fetch_logger.py
```

---

# 6. Logging configuration

```python
# config.py

import logging


def configure_logging(
    level: int = logging.INFO,
) -> None:

    logging.basicConfig(
        level=level,
        format=(
            "%(asctime)s "
            "%(levelname)s "
            "%(name)s "
            "%(message)s"
        ),
    )
```

Sử dụng:

```python
from crawler.infrastructure.logging.config import (
    configure_logging,
)

configure_logging()
```

---

# 7. Logger riêng cho Fetcher

```python
# fetch_logger.py

import logging


logger = logging.getLogger(
    "crawler.fetcher"
)
```

Sau đó:

```python
logger.info("fetch started")
```

---

# 8. Nhưng message vẫn chưa đủ

Ví dụ:

```text
2026-09-18 23:00:00 INFO crawler.fetcher fetch started
```

Ta không biết:

```text
URL nào?
Proxy nào?
Context nào?
Attempt nào?
```

Do đó cần **Request Context**.

---

# 9. FetchLogContext

Tạo:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class FetchLogContext:

    url: str

    attempt: int

    context_name: str | None = None

    proxy_name: str | None = None
```

Ví dụ:

```python
context = FetchLogContext(
    url="https://example.com/chapter-10",
    attempt=1,
    context_name="chrome_windows",
    proxy_name="proxy-01",
)
```

---

# 10. Thêm task ID

Crawler thực tế thường chạy:

```text
100 chapter
```

đồng thời.

Nếu log:

```text
chapter-1
chapter-2
chapter-3
```

xen kẽ nhau, rất khó theo dõi.

Ta thêm:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class FetchLogContext:

    request_id: str

    url: str

    attempt: int

    context_name: str | None = None

    proxy_name: str | None = None
```

Ví dụ:

```text
request_id=8f42...
```

---

# 11. UUID

Có thể tạo:

```python
from uuid import uuid4


request_id = str(uuid4())
```

Ví dụ:

```text
e7e5f3d1-...
```

Nhưng với crawler lớn, UUID đầy đủ đôi khi khá dài.

Ta có thể dùng:

```python
request_id = uuid4().hex[:12]
```

Ví dụ:

```text
a31c9e42f812
```

---

# 12. Một log record hoàn chỉnh

Ta muốn:

```text
INFO fetch.start
request_id=a31c9e42f812
url=https://example.com/chapter-10
attempt=1
context=chrome_windows
proxy=proxy-01
```

Vấn đề là Python logging mặc định không có structured fields tiện lợi.

Ta sẽ tạo adapter.

---

# 13. LoggerAdapter

```python
import logging


class FetchLoggerAdapter(
    logging.LoggerAdapter
):

    def process(
        self,
        msg,
        kwargs,
    ):
        context = self.extra

        prefix = (
            f"request_id={context.request_id} "
            f"url={context.url} "
            f"attempt={context.attempt}"
        )

        return (
            f"{prefix} | {msg}",
            kwargs,
        )
```

Sử dụng:

```python
adapter = FetchLoggerAdapter(
    logger,
    context,
)

adapter.info("fetch started")
```

---

# 14. Nhưng context thay đổi theo attempt

Đây là điểm quan trọng.

Request:

```text
attempt 1 → Context A
attempt 2 → Context B
```

Không nên tạo một context cố định chứa proxy.

Thay vào đó:

```text
RequestContext
    │
    ├── request_id
    └── url

AttemptContext
    │
    ├── attempt
    ├── browser
    └── proxy
```

---

# 15. Tách RequestContext và AttemptContext

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RequestContext:

    request_id: str

    url: str


@dataclass(frozen=True)
class AttemptContext:

    request_id: str

    url: str

    attempt: int

    context_name: str

    proxy_name: str | None
```

Đây là model tốt hơn.

---

# 16. Vì sao?

Một request:

```text
request_id = abc123
```

có:

```text
attempt 1
proxy A
chrome

attempt 2
proxy B
chrome

attempt 3
proxy C
firefox
```

Tất cả đều thuộc:

```text
request_id=abc123
```

Nhưng mỗi attempt có context khác nhau.

---

# 17. Timing

Ta cần biết:

```text
request mất bao lâu?
```

Dùng:

```python
import time


started = time.perf_counter()

# HTTP request

elapsed = time.perf_counter() - started
```

Không dùng:

```python
time.time()
```

để đo duration.

`perf_counter()` phù hợp cho elapsed time.

---

# 18. Log request start

```python
logger.info(
    "fetch.start "
    "request_id=%s "
    "url=%s "
    "attempt=%s "
    "context=%s "
    "proxy=%s",
    request_id,
    request.url,
    attempt,
    context.profile.name,
    context.proxy.url if context.proxy else None,
)
```

Nhưng có một vấn đề.

---

# 19. Không được log proxy credentials

Nếu proxy:

```text
http://user:password@proxy.example.com:8080
```

tuyệt đối không log nguyên URL.

Sai:

```python
logger.info(
    "proxy=%s",
    proxy.url,
)
```

Có thể làm lộ:

```text
username
password
token
```

---

# 20. Mask proxy

Tạo:

```python
from urllib.parse import urlsplit


def mask_proxy(proxy_url: str) -> str:

    parsed = urlsplit(proxy_url)

    host = parsed.hostname or "unknown"

    port = (
        f":{parsed.port}"
        if parsed.port
        else ""
    )

    return f"{parsed.scheme}://{host}{port}"
```

Input:

```text
http://user:secret@proxy.example.com:8080
```

Output:

```text
http://proxy.example.com:8080
```

---

# 21. Không chỉ proxy

Cũng cần tránh log:

```text
Authorization
Cookie
API key
Bearer token
session token
password
```

Ví dụ:

```python
headers = {
    "Authorization": "Bearer abc123"
}
```

Không:

```python
logger.debug(
    "headers=%s",
    headers,
)
```

---

# 22. Request logging helper

Ta tạo:

```python
def log_fetch_start(
    *,
    request_id: str,
    request: FetchRequest,
    attempt: int,
    context_name: str,
    proxy_name: str | None,
) -> None:

    logger.info(
        "fetch.start "
        "request_id=%s "
        "url=%s "
        "attempt=%d "
        "context=%s "
        "proxy=%s",
        request_id,
        request.url,
        attempt,
        context_name,
        proxy_name,
    )
```

---

# 23. Log success

Khi:

```text
200
```

ta log:

```python
logger.info(
    "fetch.success "
    "request_id=%s "
    "status=%d "
    "elapsed=%.3f",
    request_id,
    response.status_code,
    elapsed,
)
```

Ví dụ:

```text
INFO fetch.success
request_id=abc123
status=200
elapsed=0.842
```

---

# 24. Log retry

Đây là log quan trọng nhất.

```python
logger.warning(
    "fetch.retry "
    "request_id=%s "
    "attempt=%d "
    "error=%s "
    "delay=%.3f "
    "change_proxy=%s",
    request_id,
    attempt,
    error.category.value,
    decision.delay,
    decision.change_proxy,
)
```

Ví dụ:

```text
WARNING fetch.retry
request_id=abc123
attempt=1
error=http_5xx
delay=1.734
change_proxy=False
```

---

# 25. Log final failure

Sau khi hết retry:

```python
logger.error(
    "fetch.failed "
    "request_id=%s "
    "attempt=%d "
    "error=%s",
    request_id,
    attempt,
    error.category.value,
)
```

Ví dụ:

```text
ERROR fetch.failed
request_id=abc123
attempt=3
error=timeout
```

---

# 26. Log proxy failure

Nếu:

```text
proxy_related=True
```

ta log riêng:

```python
logger.warning(
    "proxy.failure "
    "request_id=%s "
    "proxy=%s "
    "error=%s",
    request_id,
    proxy_name,
    error.category.value,
)
```

Điều này giúp sau này thống kê:

```text
Proxy A → 42 failures
Proxy B → 3 failures
Proxy C → 0 failures
```

---

# 27. Browser Context logging

Ví dụ:

```text
context=chrome_146_windows
```

Ta muốn biết:

```text
browser profile
OS
proxy
```

Nhưng không cần log toàn bộ fingerprint.

```python
logger.debug(
    "context.selected "
    "request_id=%s "
    "context=%s "
    "proxy=%s",
    request_id,
    context.profile.name,
    proxy_name,
)
```

---

# 28. Đừng log quá nhiều

Crawler có thể thực hiện:

```text
1,000,000 requests
```

Nếu mỗi request:

```text
10 log lines
```

thì:

```text
10 million lines
```

Do đó:

```text
INFO
```

nên đủ để theo dõi lifecycle chính.

```text
DEBUG
```

mới chứa chi tiết.

---

# 29. Quy tắc logging đề xuất

```text
DEBUG
├── selected context
├── request headers metadata
└── detailed timing

INFO
├── fetch.start
└── fetch.success

WARNING
├── retry
├── proxy failure
└── rate limit

ERROR
├── final fetch failure
└── unexpected infrastructure failure
```

---

# 30. Structured Logging tốt hơn text tự do

Text:

```text
request failed because proxy failed
```

khó machine-process.

Structured:

```text
event=fetch.failed
request_id=abc123
error=proxy
attempt=2
proxy=proxy-03
```

sau này có thể chuyển sang JSON:

```json
{
  "event": "fetch.failed",
  "request_id": "abc123",
  "attempt": 2,
  "error": "proxy",
  "proxy": "proxy-03"
}
```

Đây là nền tảng cho:

```text
ELK
Loki
Grafana
OpenTelemetry
```

nhưng hôm nay chưa cần tích hợp.

---

# 31. Event name

Tôi khuyên dùng event name ổn định:

```text
fetch.start
fetch.success
fetch.retry
fetch.failed

proxy.selected
proxy.failure

context.selected
```

Không nên:

```text
"Started fetching URL..."
```

vì event name thay đổi khó query.

---

# 32. Tạo FetchEvent

Ta có thể formalize:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class FetchEvent:

    name: str

    request_id: str

    url: str

    attempt: int

    status_code: int | None = None

    error: str | None = None

    elapsed: float | None = None

    delay: float | None = None
```

Ví dụ:

```python
FetchEvent(
    name="fetch.retry",
    request_id="abc123",
    url="https://example.com/chapter-10",
    attempt=1,
    status_code=503,
    error="http_5xx",
    delay=1.7,
)
```

---

# 33. Có nên đưa FetchEvent vào Domain?

**Không.**

Đây là observability concern.

Không nên:

```text
domain/chapter.py
    ↓
logger.info(...)
```

Domain không cần biết:

```text
logging
proxy
primp
HTTP
```

---

# 34. Logging thuộc Infrastructure

Kiến trúc:

```text
Application
    │
    ▼
Fetcher
    │
    ▼
Infrastructure
├── Primp
├── Proxy
├── Retry
└── Logging
```

Domain sạch.

---

# 35. Logging Decorator?

Có thể viết:

```python
@log_fetch
async def get(...):
    ...
```

Nhưng ở giai đoạn này **chưa nên**.

Vì Fetcher có nhiều event:

```text
attempt
proxy
retry
success
failure
```

Decorator sẽ nhanh chóng trở nên khó đọc.

Tốt hơn là logging tại orchestration boundary.

---

# 36. Tích hợp với PrimpFetcher

Skeleton:

```python
async def get(
    self,
    request: FetchRequest,
) -> FetchResponse:

    request_id = uuid4().hex[:12]

    for attempt in range(
        1,
        self.retry_policy.max_attempts + 1,
    ):

        context = self.context_strategy.select()

        started = time.perf_counter()

        log_fetch_start(
            request_id=request_id,
            request=request,
            attempt=attempt,
            context_name=context.profile.name,
            proxy_name=self.proxy_name(context),
        )

        try:

            await self.rate_limiter.acquire()

            async with self.semaphore:

                response = (
                    await context.transport.send(
                        request
                    )
                )

        except Exception as exc:

            elapsed = (
                time.perf_counter()
                - started
            )

            error = (
                self.error_classifier.classify(
                    exc
                )
            )

            decision = (
                self.retry_policy.decide(
                    attempt=attempt,
                    error=error,
                )
            )

            logger.warning(
                "fetch.error "
                "request_id=%s "
                "attempt=%d "
                "error=%s "
                "elapsed=%.3f",
                request_id,
                attempt,
                error.category.value,
                elapsed,
            )

            if not decision.retry:
                logger.error(
                    "fetch.failed "
                    "request_id=%s "
                    "error=%s",
                    request_id,
                    error.category.value,
                )
                raise

            logger.warning(
                "fetch.retry "
                "request_id=%s "
                "attempt=%d "
                "delay=%.3f",
                request_id,
                attempt,
                decision.delay,
            )

            await asyncio.sleep(
                decision.delay
            )

            continue

        elapsed = (
            time.perf_counter()
            - started
        )

        logger.info(
            "fetch.success "
            "request_id=%s "
            "attempt=%d "
            "status=%d "
            "elapsed=%.3f",
            request_id,
            attempt,
            response.status_code,
            elapsed,
        )

        return response

    raise RuntimeError(
        "Retry attempts exhausted"
    )
```

Đây là skeleton để hiểu flow; Buổi 50 chúng ta sẽ làm nó sạch hơn.

---

# 37. Một vấn đề mới: log context trong async

Crawler chạy:

```python
await asyncio.gather(
    fetch(url1),
    fetch(url2),
    fetch(url3),
)
```

Logs sẽ xen kẽ:

```text
url1
url2
url3
url1
url3
url2
```

Đây là bình thường.

Vì vậy:

```text
request_id
```

cực kỳ quan trọng.

Ta có:

```text
abc123 → chapter 1
def456 → chapter 2
ghi789 → chapter 3
```

Có thể filter theo ID.

---

# 38. ContextVar

Python có:

```python
contextvars.ContextVar
```

cho async context.

Ví dụ:

```python
from contextvars import ContextVar


request_id_var = ContextVar(
    "request_id",
    default="-",
)
```

Set:

```python
token = request_id_var.set(
    "abc123"
)
```

Lấy:

```python
request_id_var.get()
```

Reset:

```python
request_id_var.reset(token)
```

---

# 39. Tại sao ContextVar hữu ích?

Thay vì truyền:

```python
request_id
```

qua rất nhiều function:

```text
Fetcher
 ↓
Retry
 ↓
Transport
 ↓
Logger
```

ta có context:

```text
Async Task
   │
   └── request_id
```

Logger có thể đọc nó.

Đây là kỹ thuật rất hữu ích cho crawler lớn.

---

# 40. Nhưng chưa cần lạm dụng

Buổi 49 chúng ta chỉ cần hiểu:

```text
ContextVar
```

là nền tảng cho request-scoped logging.

Không cần biến mọi metadata thành ContextVar.

Các dữ liệu như:

```text
attempt
proxy
status
elapsed
```

vẫn nên truyền rõ ràng.

---

# 41. Metrics

Logging trả lời:

> Request này xảy ra chuyện gì?

Metrics trả lời:

> Hệ thống tổng thể đang hoạt động thế nào?

Ví dụ:

```text
requests_total = 10000

success_total = 9300

retry_total = 500

failed_total = 200

timeout_total = 100

proxy_failure_total = 80

average_latency = 0.84s
```

---

# 42. Counter

Ví dụ conceptual:

```python
requests_total += 1
```

Không nên dùng biến global đơn giản trong production concurrent system.

Sau này có thể dùng:

```text
Prometheus
OpenTelemetry
```

nhưng chưa cần ở Buổi 49.

---

# 43. Histogram

Latency nên là histogram:

```text
request duration

0–0.5s
0.5–1s
1–2s
2–5s
5s+
```

thay vì chỉ:

```text
average = 1.2s
```

Bởi average có thể che giấu request rất chậm.

---

# 44. Tracing

Tracing trả lời:

> Một operation đi qua hệ thống như thế nào?

Novel crawler:

```text
CrawlChapter
   ↓
Fetcher
   ↓
Retry
   ↓
Context
   ↓
Proxy
   ↓
HTTP
   ↓
Parser
   ↓
Repository
```

Một trace có thể chứa nhiều spans.

Buổi 50 chỉ cần hiểu concept.

---

# 45. Ba trụ cột

```text
                 Observability
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
         Logs       Metrics     Traces
          │           │           │
       What?        How many?   Where?
```

Ví dụ:

```text
Logs:
Proxy A failed

Metrics:
Proxy failures = 312

Trace:
CrawlChapter → Fetch → Retry → Proxy
```

---

# 46. Production log format

Cuối cùng ta muốn log gần như:

```text
2026-09-18T23:30:12.321
INFO
event=fetch.start
request_id=a31c9e42f812
url=/chapter-123
attempt=1
context=chrome_146_windows
proxy=proxy-03
```

Sau đó:

```text
2026-09-18T23:30:13.102
WARNING
event=fetch.retry
request_id=a31c9e42f812
attempt=1
error=http_5xx
status=503
delay=1.72
```

Cuối cùng:

```text
2026-09-18T23:30:15.210
INFO
event=fetch.success
request_id=a31c9e42f812
attempt=2
status=200
elapsed=0.821
```

Nhìn vào 3 dòng này ta đã biết gần như toàn bộ lifecycle.

---

# 47. Complete mini example

Đây là ví dụ nhỏ có thể chạy ngay:

```python
import logging
import time
from uuid import uuid4


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s "
        "%(levelname)s "
        "%(message)s"
    ),
)

logger = logging.getLogger("crawler.fetcher")


def fetch_simulation() -> None:

    request_id = uuid4().hex[:12]

    url = (
        "https://example.com/chapter-123"
    )

    for attempt in range(1, 3):

        started = time.perf_counter()

        logger.info(
            "event=fetch.start "
            "request_id=%s "
            "attempt=%d "
            "url=%s",
            request_id,
            attempt,
            url,
        )

        time.sleep(0.2)

        if attempt == 1:

            elapsed = (
                time.perf_counter()
                - started
            )

            logger.warning(
                "event=fetch.retry "
                "request_id=%s "
                "attempt=%d "
                "status=503 "
                "delay=1.0 "
                "elapsed=%.3f",
                request_id,
                attempt,
                elapsed,
            )

            time.sleep(1)

            continue

        elapsed = (
            time.perf_counter()
            - started
        )

        logger.info(
            "event=fetch.success "
            "request_id=%s "
            "attempt=%d "
            "status=200 "
            "elapsed=%.3f",
            request_id,
            attempt,
            elapsed,
        )

        return


if __name__ == "__main__":
    fetch_simulation()
```

Kết quả đại khái:

```text
INFO event=fetch.start request_id=abc123 attempt=1
WARNING event=fetch.retry request_id=abc123 attempt=1 status=503
INFO event=fetch.start request_id=abc123 attempt=2
INFO event=fetch.success request_id=abc123 attempt=2 status=200
```

---

# 48. Điểm kiến trúc rất quan trọng

Sau Buổi 48:

```text
ErrorClassifier
```

trả lời:

```text
"What happened?"
```

Sau Buổi 49:

```text
Observability
```

trả lời:

```text
"What happened over time?"
```

Hai thứ này khác nhau.

---

# 49. Architecture hiện tại

```text
                         Application
                              │
                              ▼
                           Fetcher
                              │
                              ▼
                       PrimpFetcher
                              │
       ┌──────────────────────┼──────────────────────┐
       │                      │                      │
       ▼                      ▼                      ▼
 RetryPolicy           ErrorClassifier          Observability
       │                      │                      │
       ▼                      ▼                      ├── Logs
 RetryDecision            FetchError               ├── Metrics
       │                                             └── Traces
       ▼
 BrowserContextStrategy
       │
       ▼
 BrowserContext
       │
 ┌─────┼──────┐
 ▼     ▼      ▼
Proxy Browser Transport
              │
              ▼
       primp.AsyncClient
```

---

# 50. SOLID sau Buổi 49

### Single Responsibility

```text
RetryPolicy
    → retry decision

ErrorClassifier
    → classify error

RateLimiter
    → request speed

BrowserStrategy
    → context selection

Observability
    → telemetry
```

Không có class nào phải làm tất cả.

### Dependency Inversion

Application vẫn chỉ biết:

```python
Fetcher
```

Logging nằm Infrastructure.

Domain không biết:

```text
primp
logging
proxy
HTTP
```

---

# 51. Một nguyên tắc production rất đáng nhớ

**Log đủ để debug nhưng không log bí mật.**

Không log:

```text
Authorization
Cookie
password
proxy password
API key
session token
```

Có thể log:

```text
request_id
host
path
status
attempt
proxy identifier
browser profile
error category
elapsed
```

Và nếu URL có query chứa token:

```text
https://example.com/page?token=SECRET
```

cũng cần sanitize trước khi log.

---

# 52. Part V đã gần hoàn thành

Hiện tại:

```text
41 Request Model             ✅
42 Response Model            ✅
43 Fetcher Interface         ✅
44 PrimpFetcher              ✅
45 Retry Policy              ✅
46 Proxy Strategy            ✅
47 Browser Profile Strategy  ✅
48 Error Classification      ✅
49 Observability / Logging   ← hôm nay
50 Production Fetcher        → tiếp theo
```

## Bài tập Buổi 49

Hãy mở `PrimpFetcher` của Buổi 48 và bổ sung tối thiểu 5 event:

```text
fetch.start
fetch.retry
fetch.success
fetch.failed
proxy.failure
```

Mỗi event nên có ít nhất:

```text
request_id
attempt
url/host
context
proxy
status/error
elapsed
```

Sau đó Buổi **50 — Production Fetcher** sẽ là bài tổng kết Part V: chúng ta gom toàn bộ:

```text
Request
Response
Fetcher Port
PrimpTransport
Primp AsyncClient
Retry
Error Classification
Proxy Strategy
Browser Profile Strategy
Rate Limiter
Semaphore
Timeout
Logging
```

thành một **Production-grade Async Novel Fetcher** nhưng vẫn giữ đúng ranh giới DDD/SOLID, không biến `PrimpFetcher` thành một God Object.
