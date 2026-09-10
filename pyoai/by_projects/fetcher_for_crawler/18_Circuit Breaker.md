# Buổi 18 — Circuit Breaker

Ở Buổi 17, chúng ta đã có:

```text
Proxy
├── status
├── failure_count
├── success_count
├── last_failure_at
└── last_checked_at
```

và đã biết cách persist state vào SQLite.

Bây giờ ta giải quyết vấn đề:

> **Nếu một Proxy liên tục thất bại, làm sao ngăn Fetcher tiếp tục gửi request vào nó?**

Đây là nhiệm vụ của **Circuit Breaker**.

---

# 1. Vấn đề thực tế

Giả sử có:

```text
Proxy A
```

và A đã hỏng.

Nếu crawler có:

```text
1000 requests
```

mỗi request đều:

```text
A
 ↓
timeout
 ↓
retry
 ↓
timeout
```

thì chúng ta đang:

* tốn thời gian timeout;
* tốn connection;
* tăng latency;
* lãng phí retry;
* liên tục sử dụng một proxy đã biết là có vấn đề.

Ta muốn:

```text
A thất bại nhiều lần
       ↓
Circuit OPEN
       ↓
không gửi request vào A
       ↓
sau cooldown
       ↓
thử kiểm tra lại
```

---

# 2. Circuit Breaker là gì?

Circuit Breaker là cơ chế:

> **Tạm thời ngăn request đi tới một dependency đang thất bại liên tục.**

Mô hình kinh điển có 3 state:

```text
CLOSED
   │
   │ failures >= threshold
   ▼
 OPEN
   │
   │ cooldown hết
   ▼
HALF_OPEN
   │
   ├── success ──→ CLOSED
   │
   └── failure ──→ OPEN
```

Đây là state machine quan trọng nhất của bài.

---

# 3. Ba trạng thái

## CLOSED

Bình thường.

```text
request
   ↓
Proxy
   ↓
server
```

Request được phép đi qua.

---

## OPEN

Circuit đang mở.

```text
request
   ↓
Circuit Breaker
   ↓
BLOCK
```

Không gửi request tới proxy.

Điều này rất quan trọng:

> **OPEN không có nghĩa Proxy đã bị xóa hoặc vĩnh viễn chết.**

Nó chỉ có nghĩa:

> "Tạm thời không cho request đi qua."

---

## HALF_OPEN

Sau một khoảng cooldown:

```text
OPEN
 ↓
cooldown hết
 ↓
HALF_OPEN
```

Ta cho **một request thử nghiệm** đi qua.

Nếu thành công:

```text
HALF_OPEN
    ↓
success
    ↓
CLOSED
```

Nếu thất bại:

```text
HALF_OPEN
    ↓
failure
    ↓
OPEN
```

---

# 4. Circuit Breaker khác Proxy State

Đây là điểm rất quan trọng.

Ở Buổi 17 ta có:

```text
Proxy.status
```

Ví dụ:

```text
UNKNOWN
ALIVE
DEAD
DISABLED
```

Circuit Breaker có:

```text
CircuitState
```

```text
CLOSED
OPEN
HALF_OPEN
```

**Không nên gộp hai thứ thành một enum.**

---

# 5. Vì sao không dùng luôn `ProxyStatus`?

Ví dụ:

```text
ProxyStatus.DEAD
```

không nói được:

```text
đã cooldown chưa?
được phép thử lại chưa?
đang HALF_OPEN không?
```

Trong khi:

```text
CircuitState.OPEN
```

nói rõ:

```text
request bị chặn
```

và:

```text
CircuitState.HALF_OPEN
```

nói rõ:

```text
đang thử recovery
```

Do đó:

```text
Proxy State
     +
Circuit State
```

là hai dimension khác nhau.

---

# 6. Một ví dụ

Proxy A:

```text
Proxy.status = DEAD
Circuit.state = OPEN
```

Proxy B:

```text
Proxy.status = ALIVE
Circuit.state = CLOSED
```

Proxy C:

```text
Proxy.status = ALIVE
Circuit.state = HALF_OPEN
```

Ba trạng thái này hoàn toàn có thể tồn tại độc lập.

---

# 7. Circuit Breaker thuộc đâu?

Ta cần phân biệt:

```text
Proxy Entity
```

với:

```text
Circuit Breaker
```

Circuit Breaker không nhất thiết phải là property của `Proxy`.

Một thiết kế tốt:

```text
Domain
├── Proxy
└── CircuitBreaker
```

Ví dụ:

```text
Proxy
   │
   └── identity/state

CircuitBreaker
   │
   └── failure protection state
```

---

# 8. Model `CircuitState`

```python
from enum import Enum


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"
```

---

# 9. CircuitBreakerConfig

Ta không hard-code threshold.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class CircuitBreakerConfig:
    failure_threshold: int = 3
    recovery_timeout: float = 30.0

    def __post_init__(self):
        if self.failure_threshold <= 0:
            raise ValueError("failure_threshold must be > 0")

        if self.recovery_timeout <= 0:
            raise ValueError("recovery_timeout must be > 0")
```

Ví dụ:

```text
3 failures
+
30 seconds
```

---

# 10. Model cơ bản

Ta có:

```python
class CircuitBreaker:
    def __init__(
        self,
        config: CircuitBreakerConfig,
    ):
        self._config = config
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._opened_at = None
```

---

# 11. `state`

```python
@property
def state(self) -> CircuitState:
    return self._state
```

và:

```python
@property
def failure_count(self) -> int:
    return self._failure_count
```

---

# 12. Record Failure

Khi request thất bại:

```python
def record_failure(
    self,
    now: datetime,
) -> None:

    if self._state == CircuitState.OPEN:
        return

    self._failure_count += 1

    if self._failure_count >= self._config.failure_threshold:
        self._state = CircuitState.OPEN
        self._opened_at = now
```

Ví dụ threshold = 3:

```text
failure 1
   ↓
CLOSED

failure 2
   ↓
CLOSED

failure 3
   ↓
OPEN
```

---

# 13. Record Success

```python
def record_success(self) -> None:

    self._failure_count = 0
    self._opened_at = None
    self._state = CircuitState.CLOSED
```

Điều này reset circuit.

```text
OPEN
 ↓
HALF_OPEN
 ↓ success
 ↓
CLOSED
```

---

# 14. `can_execute()`

Circuit phải quyết định:

> Request có được phép đi qua không?

```python
def can_execute(
    self,
    now: datetime,
) -> bool:

    if self._state == CircuitState.CLOSED:
        return True

    if self._state == CircuitState.OPEN:
        if self._opened_at is None:
            return False

        elapsed = (now - self._opened_at).total_seconds()

        if elapsed < self._config.recovery_timeout:
            return False

        self._state = CircuitState.HALF_OPEN

        return True

    if self._state == CircuitState.HALF_OPEN:
        return False

    return False
```

Ở đây có một ý rất quan trọng:

> Khi HALF_OPEN, chỉ cho **một trial request** đi qua.

---

# 15. Tại sao HALF_OPEN phải đặc biệt?

Nếu:

```text
OPEN
 ↓
30 seconds
 ↓
HALF_OPEN
```

mà ta cho:

```text
100 requests
```

cùng đi vào:

```text
A
A
A
A
A
...
```

thì circuit breaker mất ý nghĩa.

Ta chỉ muốn:

```text
HALF_OPEN
    ↓
trial request #1
```

Nếu thành công:

```text
CLOSED
```

Nếu thất bại:

```text
OPEN
```

---

# 16. Cần thêm "trial in progress"

Thiết kế đơn giản hơn:

```python
class CircuitBreaker:

    def __init__(...):
        ...
        self._half_open_trial = False
```

Khi chuyển sang HALF_OPEN:

```python
self._state = CircuitState.HALF_OPEN
self._half_open_trial = False
```

Sau đó:

```python
def can_execute(self, now):

    if self._state == CircuitState.CLOSED:
        return True

    if self._state == CircuitState.OPEN:
        ...
        self._state = CircuitState.HALF_OPEN
        self._half_open_trial = False

    if self._state == CircuitState.HALF_OPEN:
        if self._half_open_trial:
            return False

        self._half_open_trial = True
        return True
```

Như vậy:

```text
HALF_OPEN
   │
   ├── first request → ALLOW
   │
   └── second request → BLOCK
```

---

# 17. Success trong HALF_OPEN

```python
def record_success(self) -> None:

    self._failure_count = 0
    self._opened_at = None
    self._half_open_trial = False
    self._state = CircuitState.CLOSED
```

Flow:

```text
OPEN
 ↓
cooldown
 ↓
HALF_OPEN
 ↓
trial success
 ↓
CLOSED
```

---

# 18. Failure trong HALF_OPEN

```python
def record_failure(
    self,
    now: datetime,
) -> None:

    if self._state == CircuitState.HALF_OPEN:
        self._state = CircuitState.OPEN
        self._opened_at = now
        self._half_open_trial = False
        return

    if self._state == CircuitState.OPEN:
        return

    self._failure_count += 1

    if self._failure_count >= self._config.failure_threshold:
        self._state = CircuitState.OPEN
        self._opened_at = now
```

Flow:

```text
OPEN
 ↓
cooldown
 ↓
HALF_OPEN
 ↓
trial failure
 ↓
OPEN
```

---

# 19. Full CircuitBreaker

Một phiên bản hoàn chỉnh hơn:

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass(frozen=True)
class CircuitBreakerConfig:
    failure_threshold: int = 3
    recovery_timeout: float = 30.0

    def __post_init__(self):

        if self.failure_threshold <= 0:
            raise ValueError("failure_threshold must be > 0")

        if self.recovery_timeout <= 0:
            raise ValueError("recovery_timeout must be > 0")


class CircuitBreaker:
    def __init__(
        self,
        config: CircuitBreakerConfig,
    ):
        self._config = config

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._opened_at: datetime | None = None
        self._half_open_trial = False

    @property
    def state(self) -> CircuitState:
        return self._state

    @property
    def failure_count(self) -> int:
        return self._failure_count

    def can_execute(
        self,
        now: datetime,
    ) -> bool:

        if self._state == CircuitState.CLOSED:
            return True

        if self._state == CircuitState.OPEN:
            if self._opened_at is None:
                return False

            elapsed = (now - self._opened_at).total_seconds()

            if elapsed < self._config.recovery_timeout:
                return False

            self._state = CircuitState.HALF_OPEN
            self._half_open_trial = False

        if self._state == CircuitState.HALF_OPEN:
            if self._half_open_trial:
                return False

            self._half_open_trial = True
            return True

        return False

    def record_success(self) -> None:

        self._failure_count = 0
        self._opened_at = None
        self._half_open_trial = False
        self._state = CircuitState.CLOSED

    def record_failure(
        self,
        now: datetime,
    ) -> None:

        if self._state == CircuitState.OPEN:
            return

        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
            self._opened_at = now
            self._half_open_trial = False

            return

        self._failure_count += 1

        if self._failure_count >= self._config.failure_threshold:
            self._state = CircuitState.OPEN
            self._opened_at = now
```

---

# 20. Test State Machine

Đây là phần quan trọng nhất của Buổi 18.

## Test 1 — CLOSED

```python
breaker = CircuitBreaker(
    CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=30,
    )
)

assert breaker.state == CircuitState.CLOSED
```

---

## Test 2 — Failure chưa đủ threshold

```text
threshold = 3
```

Sau:

```text
failure 1
failure 2
```

phải:

```text
CLOSED
```

---

## Test 3 — Threshold đạt

```text
failure 1
failure 2
failure 3
```

phải:

```text
OPEN
```

---

# 21. Test OPEN

Ngay sau khi OPEN:

```python
assert not breaker.can_execute(now)
```

Request bị block.

---

# 22. Test cooldown

Giả sử:

```text
opened_at = 10:00:00
recovery_timeout = 30s
```

Tại:

```text
10:00:20
```

→ vẫn:

```text
OPEN
```

Tại:

```text
10:00:31
```

→:

```text
HALF_OPEN
```

và trial request được phép.

---

# 23. Test recovery

```text
OPEN
 ↓
cooldown
 ↓
HALF_OPEN
 ↓
trial
 ↓
success
```

Kết quả:

```text
CLOSED
failure_count = 0
```

---

# 24. Test recovery failure

```text
OPEN
 ↓
cooldown
 ↓
HALF_OPEN
 ↓
trial
 ↓
failure
```

Kết quả:

```text
OPEN
```

---

# 25. Circuit Breaker đặt ở đâu trong Fetcher?

Ta có:

```text
Fetcher
   │
   ▼
Proxy
   │
   ▼
CircuitBreaker
   │
   ├── OPEN → không request
   │
   └── CLOSED/HALF_OPEN
            ↓
        HttpClient
```

Flow:

```text
Fetch request
     │
     ▼
select Proxy
     │
     ▼
check Circuit
     │
 ┌───┴────┐
 │        │
OPEN   allowed
 │        │
STOP      ▼
       HTTP request
```

---

# 26. Circuit Breaker và Proxy Rotation

Đây là nơi hai cơ chế bắt đầu kết hợp.

Giả sử:

```text
A = OPEN
B = CLOSED
C = CLOSED
```

Proxy selection:

```text
A
 ↓
Circuit OPEN
 ↓
skip A
 ↓
B
 ↓
request
```

Đây là một lý do Circuit Breaker phải tích hợp với Proxy Selection.

---

# 27. `ProxyPool` có nên biết CircuitBreaker?

**Không nên** ở thiết kế hiện tại.

Không làm:

```python
class ProxyPool:
    def __init__(
        self,
        proxies,
        circuit_breakers,
    ): ...
```

vì ProxyPool bắt đầu biết quá nhiều.

Thay vào đó:

```text
ProxyPool
   ↓
candidate Proxy
   ↓
CircuitBreaker
   ↓
can_execute?
```

Một service ở tầng cao hơn sẽ phối hợp.

---

# 28. ProxyCircuitRegistry

Khi có nhiều Proxy:

```text
A → Circuit A
B → Circuit B
C → Circuit C
```

ta cần mapping:

```python
circuits: dict[str, CircuitBreaker]
```

Ví dụ:

```python
class ProxyCircuitRegistry:
    def __init__(
        self,
        config: CircuitBreakerConfig,
    ):
        self._config = config
        self._circuits = {}

    def get(
        self,
        proxy: Proxy,
    ) -> CircuitBreaker:

        key = proxy.url.value

        if key not in self._circuits:
            self._circuits[key] = CircuitBreaker(self._config)

        return self._circuits[key]
```

---

# 29. Vì sao Registry hữu ích?

Ta muốn:

```text
Proxy A
   ↓
Circuit A

Proxy B
   ↓
Circuit B

Proxy C
   ↓
Circuit C
```

Không được dùng một CircuitBreaker chung cho tất cả proxy:

```text
          Circuit
             │
       ┌─────┼─────┐
       ▼     ▼     ▼
       A     B     C
```

Nếu A chết 3 lần:

```text
Circuit OPEN
```

thì B và C cũng bị block.

Sai.

Phải:

```text
A → Circuit A
B → Circuit B
C → Circuit C
```

---

# 30. Circuit Breaker và Proxy State

Sau một timeout:

```text
HTTP timeout
     │
     ├───────────────┐
     ▼               ▼
Proxy                Circuit
mark_failure()       record_failure()
     │               │
     ▼               ▼
DEAD                 OPEN
```

Ta có **hai state thay đổi**.

Ví dụ:

```text
Proxy:
DEAD

Circuit:
OPEN
```

Sau recovery:

```text
Circuit
OPEN
 ↓
HALF_OPEN
```

không nhất thiết lập tức:

```text
Proxy
DEAD → ALIVE
```

Chỉ khi trial request thành công:

```text
Proxy.mark_success()
Circuit.record_success()
```

mới trở thành:

```text
Proxy = ALIVE
Circuit = CLOSED
```

---

# 31. Đây là điểm kiến trúc cực kỳ quan trọng

Không làm:

```text
Proxy.status = CircuitState.OPEN
```

Hai khái niệm khác nhau:

```text
Proxy State
────────────
UNKNOWN
ALIVE
DEAD
DISABLED


Circuit State
─────────────
CLOSED
OPEN
HALF_OPEN
```

Có thể biểu diễn:

```text
             Proxy A
                │
        ┌───────┴────────┐
        │                │
        ▼                ▼
   Proxy State       Circuit State
      DEAD              OPEN
```

---

# 32. Circuit Breaker có cần SQLite không?

Phiên bản đầu:

**Không nhất thiết.**

Circuit Breaker thường là runtime state:

```text
Application memory
```

Khi restart:

```text
Circuit state reset
```

Trong khi Proxy state:

```text
SQLite
```

có thể persistent.

Điều này hoàn toàn hợp lý.

---

# 33. Nhưng có một vấn đề

Nếu:

```text
Proxy A
status = DEAD
```

được lưu SQLite.

Application restart:

```text
Circuit A = CLOSED
```

thì:

```text
Proxy = DEAD
Circuit = CLOSED
```

Có mâu thuẫn không?

Không nhất thiết.

Ý nghĩa:

```text
Proxy DEAD
```

= lần gần nhất Proxy thất bại.

```text
Circuit CLOSED
```

= circuit runtime hiện tại chưa tích lũy đủ failure để block request.

Tuy nhiên khi startup, hệ thống có thể quyết định:

```text
DEAD Proxy
   ↓
health check
```

trước khi dùng.

Đây là logic của `HealthyProxySelector`.

---

# 34. Circuit Breaker + Health Check

Một flow tốt:

```text
ProxyPool
   ↓
candidate A
   ↓
Circuit A
   ↓
OPEN?
 ┌─┴────┐
Yes     No
 │       │
skip     ▼
       Health Check
          │
      ┌───┴────┐
      ▼        ▼
    DEAD     ALIVE
      │        │
      ▼        ▼
   next      HTTP
             request
```

Sau này orchestration sẽ phức tạp hơn.

Đó chính là lý do:

**Buổi 20 — Fetch Orchestration**

sẽ rất quan trọng.

---

# 35. Circuit Breaker ≠ Retry

Một lần nữa cần nhớ:

### Retry

```text
request
 ↓
failure
 ↓
retry
```

### Circuit Breaker

```text
failure
 ↓
failure
 ↓
failure
 ↓
OPEN
 ↓
block future requests
```

Retry xử lý:

> "Request này có nên thử lại không?"

Circuit Breaker xử lý:

> "Có nên cho request mới đi tới dependency này không?"

---

# 36. Circuit Breaker ≠ Rate Limiting

Rate Limiting:

```text
10 requests / second
```

Circuit Breaker:

```text
dependency đang fail
→ block
```

Hai cơ chế bổ sung cho nhau:

```text
Request
   ↓
Rate Limiter
   ↓
Circuit Breaker
   ↓
Proxy
   ↓
HTTP
```

---

# 37. Circuit Breaker ≠ Proxy Rotation

Rotation:

```text
A → B → C
```

Circuit Breaker:

```text
A → OPEN
```

Khi kết hợp:

```text
A
 ↓
Circuit OPEN
 ↓
skip
 ↓
B
 ↓
Circuit CLOSED
 ↓
request
```

---

# 38. Kiến trúc sau Buổi 18

```text
                         Fetcher
                            │
                            ▼
                     ProxySelector
                            │
                            ▼
                         Proxy A
                            │
                            ▼
                    Circuit Registry
                            │
                            ▼
                     CircuitBreaker
                       │          │
                     OPEN      ALLOWED
                       │          │
                     skip         ▼
                              Health Check
                                   │
                                   ▼
                               HttpClient
```

State:

```text
Proxy A
├── ProxyStatus.DEAD
└── CircuitState.OPEN
```

---

# 39. Dependency graph

```text
CircuitBreaker
     │
     ├── CircuitBreakerConfig
     │
     └── Clock / current time
```

Nên inject Clock thay vì:

```python
datetime.now()
```

giống Buổi 17.

Ví dụ:

```python
class CircuitBreaker:
    def __init__(
        self,
        config: CircuitBreakerConfig,
        clock: Clock,
    ):
        self._config = config
        self._clock = clock
```

Điều này giúp test cooldown cực kỳ dễ.

---

# 40. Test bằng FakeClock

Ví dụ:

```python
clock = FakeClock(datetime(2026, 9, 10, 10, 0, 0))
```

Failure:

```python
breaker.record_failure(clock.now())
breaker.record_failure(clock.now())
breaker.record_failure(clock.now())
```

Circuit:

```text
OPEN
```

Sau đó:

```python
clock.advance(seconds=20)
```

```python
assert not breaker.can_execute(clock.now())
```

Tiếp:

```python
clock.advance(seconds=11)
```

```python
assert breaker.can_execute(clock.now())
```

Circuit:

```text
HALF_OPEN
```

Không cần:

```text
time.sleep(31)
```

Đây là cách test production-quality.

---

# 41. Bài tập Buổi 18

## Bài 1 — State Machine

Implement:

```text
CircuitState
CircuitBreakerConfig
CircuitBreaker
```

với:

```text
CLOSED
OPEN
HALF_OPEN
```

---

## Bài 2 — Threshold

Test:

```text
threshold = 3

failure #1 → CLOSED
failure #2 → CLOSED
failure #3 → OPEN
```

---

## Bài 3 — Cooldown

Test:

```text
OPEN
 ↓ 20s
OPEN
 ↓ 10s
HALF_OPEN
```

---

## Bài 4 — Recovery

Test:

```text
OPEN
 ↓
HALF_OPEN
 ↓ success
CLOSED
```

---

## Bài 5 — Failed Recovery

Test:

```text
OPEN
 ↓
HALF_OPEN
 ↓ failure
OPEN
```

---

## Bài 6 — One Trial Only

Trong `HALF_OPEN`:

```text
request #1 → allowed
request #2 → blocked
request #3 → blocked
```

---

## Bài 7 — Multiple Proxy

Tạo:

```text
A → Circuit A
B → Circuit B
C → Circuit C
```

Đảm bảo:

```text
A OPEN
```

không ảnh hưởng:

```text
B CLOSED
C CLOSED
```

---

# 42. Roadmap hiện tại

```text
13 Domain Service                 ✅
14 Application Service            ✅
15 Dependency Injection           ✅
16 Repository cho Proxy           ✅
17 Proxy State + Persistence      ✅
18 Circuit Breaker                ← HIỆN TẠI
19 Rate Limiting
20 Fetch Orchestration
```

Và sau Buổi 18, chúng ta sẽ có ba lớp bảo vệ khác nhau:

```text
                 Request
                    │
                    ▼
              Rate Limiter
                    │
                    ▼
             Circuit Breaker
                    │
                    ▼
             Proxy Selection
                    │
                    ▼
              Health Check
                    │
                    ▼
                HTTP
```

**Điểm cần ghi nhớ nhất của Buổi 18:**

```text
Proxy State
    ≠
Circuit State
```

và:

```text
Retry       = thử lại request hiện tại
Rotation    = đổi Proxy
Circuit     = chặn request mới tới Proxy đang thất bại
Rate Limit  = giới hạn tốc độ request
```

Bốn cơ chế này **không thay thế nhau**; chúng sẽ được phối hợp ở **Buổi 20 — Fetch Orchestration**.
