# Buổi 17 — Proxy State + Persistence

Ở Buổi 16, chúng ta đã tạo:

```text
Proxy
   ↓
ProxyRepository
   ↓
SQLiteProxyRepository
   ↓
SQLite
```

Nhưng mới chỉ giải quyết **lưu Proxy**.

Bây giờ cần giải quyết câu hỏi quan trọng hơn:

> **Khi Proxy thay đổi trạng thái trong lúc crawler chạy, làm thế nào state được quản lý đúng và đồng bộ xuống database?**

Đây là nền tảng trực tiếp cho **Circuit Breaker ở Buổi 18**.

---

# 1. Bài toán thực tế

Giả sử có 3 proxy:

```text
Proxy A
Proxy B
Proxy C
```

Crawler chạy:

```text
A → timeout
A → timeout
A → timeout
```

Ta không muốn cứ tiếp tục dùng A.

State cần thay đổi:

```text
UNKNOWN
   ↓
ALIVE
   ↓
DEAD
```

và:

```text
failure_count = 3
```

Sau đó:

```text
ProxyPool
    ↓
bỏ qua A
    ↓
B
```

Nhưng database cũng phải biết:

```text
A
status = DEAD
failure_count = 3
```

Nếu application restart:

```text
Memory mất
```

nhưng SQLite vẫn giữ:

```text
A = DEAD
```

Do đó crawler không lập tức sử dụng lại A.

---

# 2. State Machine của Proxy

Ở Buổi 2 chúng ta có:

```text
UNKNOWN
ALIVE
DEAD
DISABLED
```

Nhưng bây giờ phải thiết kế transition rõ ràng.

```text
                   check success
             ┌──────────────────────┐
             │                      ▼
          UNKNOWN ───────────────> ALIVE
             │                      │
             │                      │ failure
             │                      ▼
             └──────────────────> DEAD
                                    │
                                    │ recovery check
                                    │ success
                                    ▼
                                  ALIVE

DISABLED ── enable ──> UNKNOWN
```

`DISABLED` khác `DEAD`.

### DEAD

Proxy có vấn đề kỹ thuật.

Có thể hồi phục.

### DISABLED

Proxy bị **administratively disabled**.

Không được tự động sử dụng lại.

---

# 3. DEAD không có nghĩa là vĩnh viễn

Đây là một lỗi thiết kế phổ biến.

Không nên:

```python id="n5v3w8"
if proxy.status == ProxyStatus.DEAD:
    never_use_again()
```

Proxy có thể:

```text
timeout
   ↓
DEAD
   ↓
5 phút
   ↓
health check
   ↓
ALIVE
```

Do đó `DEAD` là một **runtime state**, không nhất thiết là permanent state.

---

# 4. Proxy Entity phải quản lý state

Không nên để Application tự sửa:

```python id="c2drq1"
proxy.status = ProxyStatus.DEAD
proxy.failure_count += 1
```

Điều này làm business invariant bị phân tán.

Thay vào đó:

```python id="k8g2pl"
proxy.mark_failure()
```

Entity tự quản lý.

Ví dụ:

```python id="u0r6pr"
@dataclass
class Proxy:
    url: ProxyUrl
    status: ProxyStatus = ProxyStatus.UNKNOWN

    failure_count: int = 0
    success_count: int = 0

    last_checked_at: datetime | None = None
    last_failure_at: datetime | None = None
```

---

# 5. `mark_success()`

```python id="s3sj24"
def mark_success(self) -> None:

    self.success_count += 1
    self.status = ProxyStatus.ALIVE
```

Nhưng production nên cập nhật thêm thời gian:

```python id="e7y0wy"
def mark_success(
    self,
    now: datetime,
) -> None:

    self.success_count += 1
    self.status = ProxyStatus.ALIVE
    self.last_checked_at = now
```

---

# 6. `mark_failure()`

```python id="e3j1i9"
def mark_failure(
    self,
    now: datetime,
) -> None:

    self.failure_count += 1
    self.last_failure_at = now
    self.status = ProxyStatus.DEAD
```

Ta có invariant:

```text
failure_count tăng
        +
last_failure_at cập nhật
        +
status = DEAD
```

Tất cả phải xảy ra cùng nhau.

Đây là lý do Entity nên chứa behavior.

---

# 7. Nhưng health check và actual request khác nhau

Đây là điểm rất quan trọng từ Buổi 6.

### Health check

```text
Proxy
 ↓
HealthChecker
 ↓
reachable?
```

### Actual request

```text
Proxy
 ↓
GET chapter
 ↓
timeout?
403?
429?
500?
```

Không nên coi mọi HTTP error là Proxy DEAD.

Ví dụ:

```text
Proxy A
   ↓
GET example.com
   ↓
403 Forbidden
```

Có thể:

```text
Proxy vẫn hoạt động
Website từ chối request
```

Do đó:

```text
403 ≠ automatically DEAD
```

---

# 8. Proxy State nên được thay đổi bởi ai?

Kiến trúc tốt:

```text
Infrastructure
    │
    ▼
HealthChecker
    │
    ▼
Health Result
    │
    ▼
Domain Service
    │
    ▼
Proxy.mark_alive()
Proxy.mark_dead()
```

Ví dụ:

```python id="jq6s4c"
class ProxyHealthService:
    def __init__(
        self,
        checker: ProxyHealthChecker,
    ):
        self._checker = checker

    def verify(
        self,
        proxy: Proxy,
        now: datetime,
    ) -> bool:

        result = self._checker.check(proxy)

        if result.reachable:
            proxy.mark_alive(now)
            return True

        proxy.mark_dead(now)
        return False
```

Entity quản lý **state transition**.

Service quản lý **khi nào transition xảy ra**.

---

# 9. State và Persistence

Sau:

```python id="49m1ob"
proxy.mark_dead(now)
```

RAM:

```text
Proxy A
status = DEAD
failure_count = 3
```

SQLite vẫn có thể:

```text
status = ALIVE
failure_count = 2
```

Đây là inconsistency.

Cần:

```python id="kn1v6u"
proxy.mark_dead(now)

repository.save(proxy)
```

Flow:

```text
Proxy
 │
 │ state transition
 ▼
Proxy = DEAD
 │
 │ persist
 ▼
ProxyRepository
 │
 ▼
SQLite
```

---

# 10. Nhưng đừng để Entity biết Repository

Sai:

```python id="oj0r6q"
class Proxy:
    def mark_dead(self):
        self.status = ProxyStatus.DEAD

        repository.save(self)
```

Entity không nên biết:

```text
SQLite
Repository
Connection
SQL
```

Domain Entity chỉ biết:

```text
state
behavior
invariants
```

---

# 11. Application Service là nơi phối hợp

Ví dụ:

```python id="7e5b6v"
class CheckProxyService:
    def __init__(
        self,
        health_service: ProxyHealthService,
        repository: ProxyRepository,
        clock: Clock,
    ):
        self._health_service = health_service
        self._repository = repository
        self._clock = clock

    def execute(
        self,
        proxy: Proxy,
    ) -> bool:

        now = self._clock.now()

        healthy = self._health_service.verify(
            proxy,
            now,
        )

        self._repository.save(proxy)

        return healthy
```

Flow:

```text
Application Service
       │
       ▼
ProxyHealthService
       │
       ▼
Proxy.mark_alive/dead()
       │
       ▼
ProxyRepository.save()
       │
       ▼
SQLite
```

---

# 12. Vì sao inject `Clock`?

Đây là một kỹ thuật rất hữu ích cho testing.

Nếu Entity gọi trực tiếp:

```python
datetime.now()
```

thì test thời gian rất khó.

Thay vào đó:

```python id="4z76lm"
class Clock(ABC):
    @abstractmethod
    def now(self) -> datetime: ...
```

Production:

```python id="3m7qvh"
class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(timezone.utc)
```

Test:

```python id="xw9w3p"
class FakeClock(Clock):
    def __init__(self, current_time):
        self._current_time = current_time

    def now(self):
        return self._current_time
```

Test sẽ deterministic.

---

# 13. Không nên dùng local time cho state

Đối với crawler production, nên lưu timestamp theo:

```text
UTC
```

Ví dụ:

```python id="dy9q7m"
datetime.now(timezone.utc)
```

Database có thể lưu ISO 8601:

```text
2026-09-10T05:30:00+00:00
```

Sau này GUI chuyển sang timezone của người dùng.

---

# 14. Persistence Model

Ta có Domain:

```python id="k84f9f"
Proxy(
    url=ProxyUrl(...),
    status=ProxyStatus.DEAD,
    failure_count=3,
    success_count=10,
    last_checked_at=...,
    last_failure_at=...,
)
```

SQLite:

```text
┌─────────────────────────────────────┐
│ proxies                             │
├─────────────────────────────────────┤
│ url                                 │
│ status                              │
│ failure_count                       │
│ success_count                       │
│ last_checked_at                     │
│ last_failure_at                     │
└─────────────────────────────────────┘
```

Repository mapping:

```text
Domain
  ↓
Repository
  ↓
SQLite
```

---

# 15. Một vấn đề mới: Load Proxy lúc startup

Giả sử database:

```text
A DEAD
B ALIVE
C ALIVE
```

Application startup:

```python id="fw4f6a"
proxies = repository.list_all()

proxy_pool = ProxyPool(proxies)
```

ProxyPool nhận:

```text
A DEAD
B ALIVE
C ALIVE
```

Sau đó:

```text
get_proxy()
   ↓
A → skip
B → return
```

Đây là sự kết hợp:

```text
Persistence
      ↓
Domain State
      ↓
Runtime Pool
```

---

# 16. Startup Flow

Toàn bộ flow:

```text id="x3kzly"
                    APPLICATION START
                           │
                           ▼
                  ProxyRepository
                           │
                           ▼
                     SQLiteProxy
                           │
                           ▼
                     list_all()
                           │
                           ▼
                    Proxy[] objects
                           │
                           ▼
                       ProxyPool
                           │
                           ▼
                    Fetcher ready
```

---

# 17. Runtime Flow

Request:

```text id="3wxm6g"
Fetcher
   │
   ▼
ProxyPool
   │
   ▼
Proxy A
   │
   ▼
HealthService
   │
   ├── healthy
   │
   └── unhealthy
          │
          ▼
      mark_dead()
          │
          ▼
      Repository
          │
          ▼
        SQLite
```

Nếu A DEAD:

```text
ProxyPool
   │
   ▼
Proxy B
```

---

# 18. Có nên `save()` sau mỗi request?

Không nhất thiết.

Nếu crawler có:

```text
100 requests/second
```

và mỗi request:

```text
mark_success()
repository.save()
SQLite write
commit
```

thì database sẽ bị write rất nhiều.

Đây là vấn đề **write amplification**.

Production có thể dùng:

```text
Memory state
      ↓
batched persistence
      ↓
SQLite
```

hoặc:

```text
Domain Event
      ↓
ProxyStateChanged
      ↓
Persistence handler
```

Nhưng hiện tại **chưa cần nhảy sang Event-Driven Architecture**.

Roadmap hiện tại chỉ cần hiểu:

> State trong Domain và state persistent phải có chiến lược đồng bộ.

---

# 19. Một chiến lược đơn giản cho Fetcher

Ở phiên bản đầu:

```text
Proxy failure
    ↓
mark_failure()
    ↓
repository.save()
```

Proxy success:

```text
Proxy success
    ↓
mark_success()
    ↓
repository.save()
```

Ưu điểm:

* đơn giản
* dễ hiểu
* dễ test
* state không dễ mất

Nhược điểm:

* nhiều database writes

Sau này có thể tối ưu.

---

# 20. Proxy failure count

Đây là dữ liệu rất quan trọng cho Buổi 18.

Ví dụ:

```text
failure_count
0
1
2
3
4
...
```

Ta có thể đặt rule:

```text
failure_count >= 3
        ↓
DEAD
```

Nhưng có một điểm cần phân biệt:

### Cách 1

Một failure → DEAD ngay.

```text
failure
  ↓
DEAD
```

### Cách 2

Failure threshold.

```text
failure 1
   ↓
UNKNOWN/DEGRADED

failure 2
   ↓
DEGRADED

failure 3
   ↓
DEAD
```

Cách 2 phù hợp production hơn trong một số hệ thống.

---

# 21. Có nên thêm `DEGRADED` ngay không?

**Chưa.**

Roadmap hiện tại:

```text
UNKNOWN
ALIVE
DEAD
DISABLED
```

là đủ.

Buổi 18 chúng ta sẽ có:

```text
Circuit Breaker
```

và lúc đó mới phân tích sâu:

```text
failure threshold
cooldown
half-open
recovery
```

Không nên làm Domain Model quá phức tạp quá sớm.

---

# 22. `enable()` và `disable()`

Admin có thể:

```python id="f9lh7m"
proxy.disable()
```

State:

```text
ALIVE
  ↓
DISABLED
```

Sau đó ProxyPool:

```python id="j8okg5"
if proxy.is_selectable:
```

sẽ bỏ qua.

Khi admin muốn sử dụng lại:

```python id="j0y2ab"
proxy.enable()
```

Ta có:

```text
DISABLED
   ↓
UNKNOWN
```

không nên:

```text
DISABLED → ALIVE
```

vì cần health check lại.

---

# 23. `is_selectable`

Domain:

```python id="h5i2pw"
@property
def is_selectable(self) -> bool:
    return self.status in {
        ProxyStatus.UNKNOWN,
        ProxyStatus.ALIVE,
    }
```

Nhưng cần cẩn thận:

Nếu `DEAD` có cooldown:

```text
DEAD
 ↓
cooldown hết
 ↓
có thể health check
```

thì `is_selectable` không còn là:

```python
status == ALIVE
```

đơn giản nữa.

Đây là lý do Buổi 18 sẽ cần mở rộng state machine.

---

# 24. Repository không nên quyết định Proxy có sống hay không

Sai:

```python id="u1t7px"
class SQLiteProxyRepository:
    def get_available_proxies(self): ...
```

rồi Repository tự quyết định:

```text
ALIVE
DEAD
DISABLED
```

Repository chỉ persistence.

Rule:

```text
"Proxy nào được chọn?"
```

thuộc Domain/Application.

Do đó:

```text
ProxyRepository
    ↓
load data

HealthyProxySelector
    ↓
business selection
```

---

# 25. Query repository cho runtime có nên có?

Sau này có thể:

```python id="l0f0sx"
repository.list_available()
```

nhưng cần phân biệt:

```text
database filtering
```

với:

```text
domain selection
```

Nếu query chỉ để tối ưu:

```sql
WHERE status != 'DISABLED'
```

thì có thể hợp lý.

Nhưng không nên nhồi toàn bộ business rule vào SQL.

---

# 26. Test State Transition

Đây là các test quan trọng nhất.

### Test success

```python id="jyf9se"
proxy = make_proxy()

proxy.mark_success(now)

assert proxy.status == ProxyStatus.ALIVE
assert proxy.success_count == 1
```

### Test failure

```python id="s6qg11"
proxy = make_proxy()

proxy.mark_failure(now)

assert proxy.status == ProxyStatus.DEAD
assert proxy.failure_count == 1
assert proxy.last_failure_at == now
```

### Test disable

```python id="g2v2wp"
proxy.disable()

assert proxy.status == ProxyStatus.DISABLED
assert not proxy.is_selectable
```

### Test enable

```python id="wq8v8v"
proxy.disable()
proxy.enable()

assert proxy.status == ProxyStatus.UNKNOWN
```

---

# 27. Test Persistence

```text
Proxy
  ↓
mark_failure()
  ↓
repository.save()
  ↓
repository.get_by_url()
```

Sau đó:

```python id="l7l9ci"
loaded = repository.get_by_url(proxy.url)

assert loaded is not None
assert loaded.status == ProxyStatus.DEAD
assert loaded.failure_count == 1
```

Đây là một **persistence round-trip test**.

---

# 28. Test Restart Simulation

Đây là bài test rất hay.

```text
Application 1
     │
     ▼
Proxy A
     │
 mark_dead()
     │
     ▼
SQLite
```

Sau đó giả lập application restart:

```text
Application 2
     │
     ▼
SQLite
     │
     ▼
list_all()
     │
     ▼
Proxy A
```

Kiểm tra:

```python id="8h7o1z"
assert proxy.status == ProxyStatus.DEAD
```

Nếu test này pass thì ta đã chứng minh:

> **Proxy state không mất khi application restart.**

---

# 29. Kiến trúc sau Buổi 17

```text
                     ┌───────────────┐
                     │ Proxy Entity  │
                     └───────┬───────┘
                             │
                    state transition
                             │
              ┌──────────────┴──────────────┐
              │                             │
        mark_alive()                  mark_dead()
        mark_success()                mark_failure()
              │                             │
              └──────────────┬──────────────┘
                             │
                             ▼
                    ProxyRepository
                             │
                             ▼
                  SQLiteProxyRepository
                             │
                             ▼
                           SQLite
```

Runtime:

```text
SQLite
  ↓
Repository
  ↓
Proxy[]
  ↓
ProxyPool
  ↓
Fetcher
```

---

# 30. Toàn bộ Fetcher Architecture hiện tại

```text
CLI / PySide6
       │
       ▼
Application Service
       │
       ▼
     Fetcher
       │
       ├─────────────── UserAgentProvider
       │
       ├─────────────── FetchPolicy
       │
       ├─────────────── ErrorClassifier
       │
       ▼
HealthyProxySelector
       │
       ▼
ProxyHealthService
       │
       ▼
ProxyHealthChecker
       │
       ▼
HttpClient
       │
       ▼
HttpxClient
```

Persistence chạy song song:

```text
                 Proxy
                  │
          state transition
                  │
                  ▼
         ProxyRepository
                  │
                  ▼
                SQLite
```

---

# 31. Điểm rất quan trọng: State ≠ Persistence

Hãy nhớ:

```text
Proxy State
```

là **Domain**.

Còn:

```text
SQLite
```

là **Infrastructure**.

Repository là cầu nối:

```text
Domain State
      │
      ▼
Repository
      │
      ▼
Persistence
```

Không được đảo ngược:

```text
SQLite
   ↓
quyết định Domain behavior
```

---

# 32. Bài tập Buổi 17

### Bài 1

Hoàn thiện:

```python
Proxy.mark_success()
Proxy.mark_failure()
Proxy.disable()
Proxy.enable()
```

và đảm bảo invariant:

```text
failure_count >= 0
success_count >= 0
```

---

### Bài 2

Viết:

```python
CheckProxyService
```

flow:

```text
check
 ↓
mark_alive / mark_dead
 ↓
repository.save
```

---

### Bài 3

Viết `FakeClock`.

Test mà **không dùng `datetime.now()` trực tiếp**.

---

### Bài 4

Test persistence:

```text
Proxy
 ↓
mark_dead
 ↓
save
 ↓
load
```

---

### Bài 5 — quan trọng

Giả lập restart:

```text
App #1
  ↓
load Proxy
  ↓
Proxy DEAD
  ↓
save
  ↓
restart
  ↓
App #2
  ↓
load Proxy
  ↓
Proxy vẫn DEAD
```

---

# 33. Roadmap tiếp theo

Chúng ta hiện đang ở:

```text
13 Domain Service                 ✅
14 Application Service            ✅
15 Dependency Injection           ✅
16 Repository cho Proxy           ✅
17 Proxy State + Persistence      ← HIỆN TẠI
18 Circuit Breaker
19 Rate Limiting
20 Fetch Orchestration
```

Và **Buổi 18 — Circuit Breaker** sẽ xây trên chính những thứ vừa học:

```text
Proxy
 ├── failure_count
 ├── status
 ├── last_failure_at
 └── state transition
          │
          ▼
    Circuit Breaker
          │
          ├── CLOSED
          ├── OPEN
          └── HALF_OPEN
```

Đặc biệt, ta sẽ phân biệt rất rõ:

```text
Proxy State
       ≠
Circuit Breaker State
```

Đây là một điểm kiến trúc quan trọng để tránh biến `Proxy.status` thành một “thùng chứa” mọi loại state của Fetcher.
