# 📘 Buổi 12 — Fetch Policy

Chúng ta tiếp tục đúng roadmap:

```text
01 Architecture
02 Proxy Domain
03 ProxyPool
04 User-Agent Pool
05 HttpClient
06 Proxy Health Checker
07 Basic Fetcher
08 Proxy Rotation
09 User-Agent Rotation
10 Retry
11 Error Handling
👉 12 Fetch Policy
13 Domain Service
14 Application Service
15 Dependency Injection
...
```

Hôm nay là **bước rất quan trọng**: biến các thành phần rời rạc thành một hệ thống có **quyết định rõ ràng**.

---

# 1. Fetch Policy là gì?

Đến Buổi 11 chúng ta đã có:

```text
HTTP Error
     ↓
ErrorClassifier
     ↓
FetchErrorInfo
```

Ví dụ:

```python
FetchErrorInfo(
    kind=ErrorKind.TIMEOUT,
    retryable=True,
    proxy_related=True,
)
```

Nhưng vẫn còn câu hỏi:

> **Bây giờ Fetcher phải làm gì?**

Ví dụ:

```text
Timeout
```

Có thể cần:

```text
retry?
đổi proxy?
mark proxy DEAD?
backoff?
```

Đây chính là nhiệm vụ của:

```text
FetchPolicy
```

---

# 2. Policy không thực hiện hành động

Đây là nguyên tắc đầu tiên.

`FetchPolicy` **không nên tự gọi HTTP**, không tự sleep, không tự đổi proxy.

Nó chỉ:

> **đưa ra quyết định.**

Ví dụ:

```text
Error
 ↓
Classifier
 ↓
FetchErrorInfo
 ↓
FetchPolicy
 ↓
FetchDecision
```

---

# 3. Kiến trúc

```text
                   Fetcher
                      │
                      ▼
                HTTP Request
                      │
             ┌────────┴────────┐
             │                 │
          Success             Error
             │                 │
             │                 ▼
             │          ErrorClassifier
             │                 │
             │                 ▼
             │           ErrorInfo
             │                 │
             │                 ▼
             │            FetchPolicy
             │                 │
             │                 ▼
             │           FetchDecision
             │
             └────────────┬──────────────┐
                          │
                          ▼
                    Fetcher executes
```

---

# 4. FetchDecision

Chúng ta cần một object biểu diễn quyết định.

```python
from dataclasses import dataclass
```

Tạo:

```python
@dataclass(frozen=True)
class FetchDecision:
    retry: bool
    rotate_proxy: bool
    mark_proxy_dead: bool
    backoff: bool
```

Ví dụ:

```python
FetchDecision(
    retry=True,
    rotate_proxy=True,
    mark_proxy_dead=True,
    backoff=True,
)
```

Nghĩa là:

```text
Retry
  +
đổi proxy
  +
proxy DEAD
  +
backoff
```

---

# 5. Tại sao cần `FetchDecision`?

Một cách đơn giản có thể viết:

```python
if error.retryable:
    retry()
```

Nhưng crawler production sẽ nhanh chóng cần nhiều quyết định hơn.

Ví dụ:

```text
retry
rotate proxy
mark proxy dead
backoff
stop
```

Nếu viết tất cả bằng `if/elif` trong `Fetcher`:

```python
if timeout:
    ...
elif connection:
    ...
elif 429:
    ...
elif 500:
    ...
elif 403:
    ...
```

Fetcher sẽ trở thành **God Object**.

Thay vào đó:

```text
Fetcher
   ↓
Policy
   ↓
Decision
```

---

# 6. Thiết kế `FetchPolicy`

```python
from abc import ABC, abstractmethod


class FetchPolicy(ABC):
    @abstractmethod
    def decide(
        self,
        error_info: FetchErrorInfo,
    ) -> FetchDecision:
        raise NotImplementedError
```

Policy chỉ nhận:

```text
FetchErrorInfo
```

và trả:

```text
FetchDecision
```

---

# 7. DefaultFetchPolicy

Ta bắt đầu với policy đơn giản.

```python
class DefaultFetchPolicy(FetchPolicy):
    def decide(
        self,
        error_info: FetchErrorInfo,
    ) -> FetchDecision:

        if error_info.kind == ErrorKind.TIMEOUT:
            return FetchDecision(
                retry=True,
                rotate_proxy=True,
                mark_proxy_dead=True,
                backoff=True,
            )

        if error_info.kind == ErrorKind.CONNECTION:
            return FetchDecision(
                retry=True,
                rotate_proxy=True,
                mark_proxy_dead=True,
                backoff=True,
            )

        if error_info.kind == ErrorKind.NETWORK:
            return FetchDecision(
                retry=True,
                rotate_proxy=True,
                mark_proxy_dead=True,
                backoff=True,
            )

        if error_info.kind == ErrorKind.RATE_LIMIT:
            return FetchDecision(
                retry=True,
                rotate_proxy=False,
                mark_proxy_dead=False,
                backoff=True,
            )

        if error_info.kind == ErrorKind.HTTP_SERVER:
            return FetchDecision(
                retry=True,
                rotate_proxy=False,
                mark_proxy_dead=False,
                backoff=True,
            )

        return FetchDecision(
            retry=False,
            rotate_proxy=False,
            mark_proxy_dead=False,
            backoff=False,
        )
```

---

# 8. Nhưng có một vấn đề

Bạn sẽ nhận thấy:

```python
TIMEOUT
```

được coi là:

```text
proxy_related=True
```

Nhưng timeout **không phải lúc nào cũng do proxy**.

Ví dụ:

```text
Proxy
 ↓
Target server quá chậm
 ↓
Read timeout
```

Proxy hoàn toàn có thể vẫn sống.

Do đó, trong production chúng ta cần phân biệt:

```text
CONNECT timeout
```

và:

```text
READ timeout
```

Nhưng hiện tại abstraction `HttpClient` của chúng ta chưa expose đủ thông tin này.

**Buổi này chưa vội over-engineer.**

Chúng ta giữ policy đơn giản và sẽ mở rộng khi cần.

---

# 9. Quan trọng: Retry ≠ Rotate Proxy

Đây là nguyên tắc cần nhớ.

### Retry

```text
Proxy A
  ↓
request
  ↓
500
  ↓
retry
  ↓
Proxy A
```

### Rotation

```text
Proxy A
  ↓
request
  ↓
proxy failure
  ↓
Proxy B
```

Có thể kết hợp:

```text
Proxy A
  ↓
timeout
  ↓
DEAD
  ↓
Proxy B
  ↓
500
  ↓
retry
  ↓
Proxy B
  ↓
200
```

---

# 10. Policy cho từng lỗi

Đây là policy v1 chúng ta sử dụng.

## Timeout

```text
TIMEOUT
 ↓
Retry
 ↓
Rotate Proxy
 ↓
Mark Proxy DEAD
 ↓
Backoff
```

---

## Connection

```text
CONNECTION
 ↓
Retry
 ↓
Rotate Proxy
 ↓
Mark DEAD
 ↓
Backoff
```

---

## Network

```text
NETWORK
 ↓
Retry
 ↓
Rotate Proxy
 ↓
Backoff
```

---

## 429

```text
429
 ↓
Retry
 ↓
Backoff
```

Không mặc định:

```text
mark proxy DEAD
```

---

## 500

```text
500
 ↓
Retry
 ↓
Backoff
```

Không đánh dấu proxy DEAD.

---

## 404

```text
404
 ↓
STOP
```

---

## 403

```text
403
 ↓
STOP
```

Không mặc định:

```text
proxy DEAD
```

---

# 11. Retry attempt cũng phải nằm trong Policy

Đây là điểm chúng ta cần cải tiến từ Buổi 10.

Ví dụ:

```text
max_attempts = 3
```

Policy cần biết:

```text
attempt = 1
attempt = 2
attempt = 3
```

Nếu:

```text
attempt = 3
```

thì:

```text
retry = False
```

Do đó:

```python
class FetchPolicy(ABC):
    @abstractmethod
    def decide(
        self,
        *,
        attempt: int,
        error_info: FetchErrorInfo,
    ) -> FetchDecision:
        raise NotImplementedError
```

---

# 12. RetryConfig

```python
@dataclass(frozen=True)
class RetryConfig:
    max_attempts: int = 3
```

Validate:

```python
def __post_init__(self):
    if self.max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")
```

Full:

```python
@dataclass(frozen=True)
class RetryConfig:
    max_attempts: int = 3

    def __post_init__(self):
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
```

---

# 13. Policy hoàn chỉnh hơn

```python
class DefaultFetchPolicy(FetchPolicy):
    def __init__(
        self,
        retry_config: RetryConfig,
    ):
        self._retry_config = retry_config

    def decide(
        self,
        *,
        attempt: int,
        error_info: FetchErrorInfo,
    ) -> FetchDecision:

        if not error_info.retryable:
            return FetchDecision(
                retry=False,
                rotate_proxy=False,
                mark_proxy_dead=False,
                backoff=False,
            )

        if attempt >= self._retry_config.max_attempts:
            return FetchDecision(
                retry=False,
                rotate_proxy=False,
                mark_proxy_dead=False,
                backoff=False,
            )

        if error_info.kind in {
            ErrorKind.TIMEOUT,
            ErrorKind.CONNECTION,
        }:
            return FetchDecision(
                retry=True,
                rotate_proxy=True,
                mark_proxy_dead=True,
                backoff=True,
            )

        if error_info.kind == ErrorKind.NETWORK:
            return FetchDecision(
                retry=True,
                rotate_proxy=True,
                mark_proxy_dead=False,
                backoff=True,
            )

        if error_info.kind in {
            ErrorKind.RATE_LIMIT,
            ErrorKind.HTTP_SERVER,
        }:
            return FetchDecision(
                retry=True,
                rotate_proxy=False,
                mark_proxy_dead=False,
                backoff=True,
            )

        return FetchDecision(
            retry=False,
            rotate_proxy=False,
            mark_proxy_dead=False,
            backoff=False,
        )
```

---

# 14. Test Policy

Đây là phần cực kỳ quan trọng.

## Timeout

```python
def test_timeout_should_retry_and_rotate():
    policy = DefaultFetchPolicy(RetryConfig(max_attempts=3))

    info = FetchErrorInfo(
        kind=ErrorKind.TIMEOUT,
        retryable=True,
        proxy_related=True,
    )

    decision = policy.decide(
        attempt=1,
        error_info=info,
    )

    assert decision.retry is True
    assert decision.rotate_proxy is True
    assert decision.mark_proxy_dead is True
    assert decision.backoff is True
```

---

# 15. Test 429

```python
def test_429_should_retry_with_backoff():
    policy = DefaultFetchPolicy(RetryConfig(max_attempts=3))

    info = FetchErrorInfo(
        kind=ErrorKind.RATE_LIMIT,
        retryable=True,
        proxy_related=False,
        status_code=429,
    )

    decision = policy.decide(
        attempt=1,
        error_info=info,
    )

    assert decision.retry is True
    assert decision.rotate_proxy is False
    assert decision.mark_proxy_dead is False
    assert decision.backoff is True
```

---

# 16. Test 404

```python
def test_404_should_stop():
    policy = DefaultFetchPolicy(RetryConfig(max_attempts=3))

    info = FetchErrorInfo(
        kind=ErrorKind.HTTP_CLIENT,
        retryable=False,
        proxy_related=False,
        status_code=404,
    )

    decision = policy.decide(
        attempt=1,
        error_info=info,
    )

    assert decision.retry is False
    assert decision.rotate_proxy is False
    assert decision.mark_proxy_dead is False
    assert decision.backoff is False
```

---

# 17. Test max attempts

```python
def test_max_attempts_should_stop():
    policy = DefaultFetchPolicy(RetryConfig(max_attempts=3))

    info = FetchErrorInfo(
        kind=ErrorKind.HTTP_SERVER,
        retryable=True,
        proxy_related=False,
        status_code=500,
    )

    decision = policy.decide(
        attempt=3,
        error_info=info,
    )

    assert decision.retry is False
```

Đây là test rất quan trọng để đảm bảo:

```text
retry
retry
retry
retry
retry
...
```

không bao giờ xảy ra.

---

# 18. Fetcher sử dụng Policy thế nào?

Bây giờ ta ghép:

```text
Fetcher
  ↓
HttpClient
  ↓
Error
  ↓
Classifier
  ↓
Policy
  ↓
Decision
```

Ví dụ:

```python
try:
    response = self._http_client.get(
        request.url,
        headers=headers,
        proxy=proxy.url.value,
    )

except FetchError as exc:
    error_info = self._error_classifier.classify(exc)

    decision = self._fetch_policy.decide(
        attempt=attempt,
        error_info=error_info,
    )
```

Sau đó Fetcher **thực thi decision**.

---

# 19. Fetcher không nên chứa policy

Không nên:

```python
except FetchTimeoutError:
    proxy.mark_dead()
    time.sleep(1)
    retry()
```

rải khắp Fetcher.

Thay vào đó:

```python
except FetchError as exc:

    info = classifier.classify(exc)

    decision = policy.decide(
        attempt=attempt,
        error_info=info,
    )

    if decision.mark_proxy_dead:
        proxy.mark_dead()

    if decision.backoff:
        delay_strategy.sleep(attempt)

    if decision.rotate_proxy:
        ...
```

Fetcher lúc này chủ yếu đóng vai trò:

> **Orchestrator**

---

# 20. Nhưng `rotate_proxy` chưa có nghĩa là Policy tự rotate

Đây là điểm dễ hiểu nhầm.

Policy trả:

```python
rotate_proxy = True
```

Fetcher mới làm:

```text
ProxyProvider.get_proxy()
```

Policy **không biết ProxyPool**.

Như vậy:

```text
FetchPolicy
      │
      │ chỉ quyết định
      ▼
FetchDecision

Fetcher
      │
      │ thực hiện
      ├── ProxyProvider
      ├── DelayStrategy
      ├── HttpClient
      └── Proxy Entity
```

Đây là DIP + SRP.

---

# 21. Một request thực tế

Giả sử:

```text
Proxy A
UA1
URL = /chapter-100
```

### Attempt 1

```text
A
 ↓
health check
 ↓
ALIVE
 ↓
GET
 ↓
timeout
```

Classifier:

```text
TIMEOUT
retryable = true
proxy_related = true
```

Policy:

```text
retry = true
rotate_proxy = true
mark_proxy_dead = true
backoff = true
```

Fetcher:

```text
A.mark_dead()
     ↓
backoff
     ↓
Proxy B
```

---

### Attempt 2

```text
B
 ↓
GET
 ↓
500
```

Classifier:

```text
HTTP_SERVER
retryable = true
proxy_related = false
```

Policy:

```text
retry = true
rotate_proxy = false
mark_proxy_dead = false
backoff = true
```

Fetcher:

```text
backoff
 ↓
retry B
```

---

### Attempt 3

```text
B
 ↓
GET
 ↓
200
```

Kết thúc:

```text
FetchResult
```

---

# 22. Toàn bộ flow

```text
                    Request
                       │
                       ▼
                Select Proxy A
                       │
                       ▼
                 Health Check
                       │
                       ▼
                     ALIVE
                       │
                       ▼
                    GET URL
                       │
                    timeout
                       │
                       ▼
                ErrorClassifier
                       │
                       ▼
                    TIMEOUT
                       │
                       ▼
                  FetchPolicy
                       │
                       ▼
              ┌─────────────────┐
              │ retry = true    │
              │ rotate = true   │
              │ dead = true     │
              │ backoff = true  │
              └────────┬────────┘
                       │
                       ▼
                 A.mark_dead()
                       │
                       ▼
                    backoff
                       │
                       ▼
                Select Proxy B
                       │
                       ▼
                    GET URL
                       │
                      500
                       │
                       ▼
                ErrorClassifier
                       │
                       ▼
                  HTTP_SERVER
                       │
                       ▼
                  FetchPolicy
                       │
                       ▼
              retry=true
              rotate=false
              backoff=true
                       │
                       ▼
                  retry B
                       │
                       ▼
                     200
                       │
                       ▼
                 FetchResult
```

Đây chính là **Fetch Policy**.

---

# 23. Một điểm cần sửa so với Buổi 10

Ở Buổi 10, chúng ta có `RetryPolicy`:

```python
should_retry(...)
```

Bây giờ có:

```text
RetryPolicy
FetchPolicy
```

Có vẻ bị trùng.

### Vậy có nên giữ cả hai?

**Có thể, nhưng cần phân vai rõ.**

`RetryPolicy`:

> Chỉ trả lời **có retry hay không**.

`FetchPolicy`:

> Quyết định **toàn bộ chiến lược xử lý lỗi**.

Ví dụ:

```text
RetryPolicy
    ↓
retry?

FetchPolicy
    ↓
retry?
rotate?
mark dead?
backoff?
```

---

# 24. Có thể đơn giản hóa kiến trúc

Với Fetcher hiện tại, tôi khuyên chúng ta **không để hai policy cùng quyết định retry**.

Kiến trúc cuối cùng nên là:

```text
ErrorClassifier
       ↓
FetchPolicy
       ↓
FetchDecision
```

Trong đó:

```text
FetchPolicy
```

bao gồm luôn logic retry.

`RetryPolicy` từ Buổi 10 có thể được giữ lại như một abstraction nhỏ bên trong `FetchPolicy`, nếu sau này cần.

Ví dụ:

```text
FetchPolicy
   │
   ├── RetryPolicy
   ├── BackoffStrategy
   └── ProxyFailurePolicy
```

Nhưng **chưa cần tách thành nhiều class ở thời điểm này**.

Đây là cách tránh over-engineering.

---

# 25. Architecture hiện tại

Sau Buổi 12:

```text
fetcher/
│
├── domain/
│   ├── models/
│   │   ├── proxy.py
│   │   └── fetch.py
│   │
│   ├── errors.py
│   └── enums.py
│
├── application/
│   ├── fetcher.py
│   ├── error_classifier.py
│   ├── fetch_policy.py
│   └── retry.py
│
├── infrastructure/
│   └── http/
│       └── httpx_client.py
│
└── tests/
    ├── test_proxy.py
    ├── test_proxy_pool.py
    ├── test_user_agent.py
    ├── test_retry.py
    ├── test_error_classifier.py
    └── test_fetch_policy.py
```

---

# 26. DDD + SOLID

Buổi này thể hiện rất rõ SOLID.

### SRP

```text
ErrorClassifier
    → phân loại lỗi

FetchPolicy
    → quyết định

Fetcher
    → điều phối

HttpClient
    → HTTP transport
```

---

### OCP

Muốn policy mới:

```python
class ConservativeFetchPolicy(FetchPolicy): ...
```

Không cần sửa `Fetcher`.

---

### LSP

```text
FetchPolicy
   ↑
DefaultFetchPolicy
   ↑
ConservativeFetchPolicy
```

Có thể thay thế nhau.

---

### ISP

Interface nhỏ:

```python
class FetchPolicy(ABC):
    def decide(...):
        ...
```

---

### DIP

Fetcher phụ thuộc:

```text
FetchPolicy
ErrorClassifier
ProxyProvider
UserAgentProvider
HttpClient
```

không phụ thuộc implementation cụ thể.

---

# 27. Bài tập thực hành

Hãy implement đầy đủ:

```text
fetch_policy.py
```

gồm:

```python
FetchDecision
FetchPolicy
DefaultFetchPolicy
```

và test:

```text
TIMEOUT
    → retry
    → rotate proxy
    → mark dead
    → backoff

CONNECTION
    → retry
    → rotate proxy
    → mark dead

NETWORK
    → retry
    → rotate proxy

429
    → retry
    → backoff
    → không mark proxy dead

500
    → retry
    → backoff
    → không mark proxy dead

404
    → stop

403
    → stop

attempt == max_attempts
    → stop
```

---

# 🧠 Tóm tắt Buổi 12

Điều quan trọng nhất cần nhớ:

```text
ErrorClassifier
      ↓
"Đây là lỗi gì?"
      ↓
FetchErrorInfo
      ↓
FetchPolicy
      ↓
"Nên làm gì?"
      ↓
FetchDecision
      ↓
Fetcher
      ↓
"Thực hiện quyết định"
```

Và phân biệt:

```text
Retry
    = thử request lại

Proxy Rotation
    = đổi proxy

Backoff
    = chờ trước khi thử lại

Mark Proxy DEAD
    = thay đổi state của Proxy
```

Không gom tất cả thành một `retry()` duy nhất.

---

## 🔜 Buổi 13 — Domain Service

Tiếp theo chúng ta sẽ bắt đầu phần **DDD + SOLID thực sự** của Fetcher:

```text
Buổi 13 — Domain Service
```

Chúng ta sẽ phân tích một vấn đề rất thực tế:

> **Proxy selection + proxy health + proxy state có nên nằm trong Fetcher hay tách thành Domain Service?**

Sau đó thiết kế:

```text
ProxySelectionService
ProxyHealthService
```

và xem chính xác **logic nào thuộc Domain, logic nào thuộc Application**, tránh tình trạng `Fetcher` ngày càng trở thành một God Object.
