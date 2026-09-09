# Buổi 2 — Thiết kế Proxy Domain Model

Hôm nay ta **chưa dùng `httpx`**.

Mục tiêu là xây phần **Domain của Proxy** thật sạch theo DDD + SOLID. Sau buổi này ta sẽ có nền tảng để xây `ProxyPool`, health check và rotation ở các buổi tiếp theo.

---

# 1. Vấn đề cần giải quyết

Fetcher của app crawl truyện sẽ phải làm việc với proxy:

```text
Proxy
 ├── URL
 ├── trạng thái
 ├── số lần thất bại
 ├── số lần thành công
 ├── lần kiểm tra cuối
 └── thời điểm lỗi gần nhất
```

Nhưng ta không muốn code kiểu:

```python
proxy = {
    "url": "http://127.0.0.1:8080",
    "alive": True,
    "failures": 2,
}
```

Vì:

* không có type rõ ràng
* không bảo vệ invariant
* logic nằm rải rác
* dễ sửa sai state

DDD yêu cầu ta biến **Proxy thành một Domain Entity**.

---

# 2. Domain Entity `Proxy`

Tạo:

```text
domain/
└── proxy/
    ├── entities.py
    ├── value_objects.py
    └── exceptions.py
```

Trước tiên:

```python
# domain/proxy/entities.py

from dataclasses import dataclass


@dataclass
class Proxy:
    url: str
    failure_count: int = 0
    success_count: int = 0
```

Sử dụng:

```python
proxy = Proxy(
    url="http://127.0.0.1:8080"
)

print(proxy.url)
print(proxy.failure_count)
```

Nhưng model này vẫn còn quá yếu.

---

# 3. Proxy cần trạng thái

Ta không nên dùng:

```python
alive = True
```

vì thực tế proxy có nhiều trạng thái.

Ví dụ:

```text
UNKNOWN
ALIVE
DEAD
DISABLED
```

Ta tạo Enum:

```python
from enum import Enum


class ProxyStatus(Enum):
    UNKNOWN = "unknown"
    ALIVE = "alive"
    DEAD = "dead"
    DISABLED = "disabled"
```

Bây giờ:

```python
proxy = Proxy(
    url="http://127.0.0.1:8080",
    status=ProxyStatus.UNKNOWN,
)
```

---

# 4. Tại sao `UNKNOWN` quan trọng?

Khi mới load proxy:

```text
SQLite
   ↓
Proxy
   ↓
UNKNOWN
```

Ta chưa thể nói:

```text
ALIVE
```

vì chưa kiểm tra.

Do đó:

```text
UNKNOWN
   │
   │ health check
   ▼
 ALIVE
```

hoặc:

```text
UNKNOWN
   │
   │ health check
   ▼
 DEAD
```

---

# 5. Entity hoàn chỉnh hơn

```python
from dataclasses import dataclass
from enum import Enum


class ProxyStatus(Enum):
    UNKNOWN = "unknown"
    ALIVE = "alive"
    DEAD = "dead"
    DISABLED = "disabled"


@dataclass
class Proxy:
    url: str
    status: ProxyStatus = ProxyStatus.UNKNOWN

    failure_count: int = 0
    success_count: int = 0
```

Test:

```python
proxy = Proxy("http://127.0.0.1:8080")

print(proxy)
```

Kết quả:

```text
Proxy(
    url='http://127.0.0.1:8080',
    status=UNKNOWN,
    failure_count=0,
    success_count=0
)
```

---

# 6. Nhưng có một vấn đề

Người dùng có thể tạo:

```python
Proxy(
    url="",
    failure_count=-100,
)
```

hoặc:

```python
Proxy(
    url="abc",
    success_count=-10,
)
```

Domain phải bảo vệ chính nó.

Đây là **Domain Invariant**.

Ta muốn:

```text
url != ""
failure_count >= 0
success_count >= 0
```

---

# 7. Validation trong Entity

Ta dùng `__post_init__`:

```python
from dataclasses import dataclass


@dataclass
class Proxy:
    url: str
    status: ProxyStatus = ProxyStatus.UNKNOWN

    failure_count: int = 0
    success_count: int = 0

    def __post_init__(self):
        if not self.url:
            raise ValueError("Proxy URL cannot be empty")

        if self.failure_count < 0:
            raise ValueError(
                "failure_count cannot be negative"
            )

        if self.success_count < 0:
            raise ValueError(
                "success_count cannot be negative"
            )
```

Bây giờ:

```python
Proxy("")
```

sẽ lỗi.

---

# 8. Nhưng URL nên là Value Object

Đây là một điểm rất quan trọng trong DDD.

Hiện tại:

```python
url: str
```

không cho biết đây có phải URL hợp lệ hay không.

Ta tạo:

```text
ProxyUrl
```

---

# 9. `ProxyUrl`

```python
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class ProxyUrl:

    value: str

    def __post_init__(self):
        parsed = urlparse(self.value)

        if parsed.scheme not in {"http", "https"}:
            raise ValueError(
                "Proxy must use http or https"
            )

        if not parsed.hostname:
            raise ValueError(
                "Proxy hostname is required"
            )
```

Ta có:

```python
proxy_url = ProxyUrl(
    "http://127.0.0.1:8080"
)
```

---

# 10. Vì sao `frozen=True`?

Value Object nên thường immutable.

```python
@dataclass(frozen=True)
class ProxyUrl:
    value: str
```

Không nên:

```python
proxy_url.value = "http://other-proxy"
```

Thay vào đó tạo Value Object mới:

```python
new_url = ProxyUrl(
    "http://other-proxy:8080"
)
```

Điều này làm Domain dễ suy luận hơn.

---

# 11. Proxy Entity sử dụng ProxyUrl

Bây giờ:

```python
@dataclass
class Proxy:
    url: ProxyUrl
    status: ProxyStatus = ProxyStatus.UNKNOWN

    failure_count: int = 0
    success_count: int = 0
```

Sử dụng:

```python
proxy = Proxy(
    url=ProxyUrl(
        "http://127.0.0.1:8080"
    )
)
```

---

# 12. Proxy phải tự thay đổi state

Không nên để Application làm:

```python
proxy.failure_count += 1
proxy.status = ProxyStatus.DEAD
```

Logic Domain nên nằm trong Entity.

Ta tạo:

```python
def mark_alive(self):
    self.status = ProxyStatus.ALIVE
```

và:

```python
def mark_dead(self):
    self.status = ProxyStatus.DEAD
    self.failure_count += 1
```

---

# 13. Thêm `mark_success`

Một request thành công:

```python
def mark_success(self):
    self.status = ProxyStatus.ALIVE
    self.success_count += 1
```

Một request thất bại:

```python
def mark_failure(self):
    self.status = ProxyStatus.DEAD
    self.failure_count += 1
```

Entity lúc này:

```python
@dataclass
class Proxy:
    url: ProxyUrl
    status: ProxyStatus = ProxyStatus.UNKNOWN

    failure_count: int = 0
    success_count: int = 0

    def mark_alive(self):
        self.status = ProxyStatus.ALIVE

    def mark_dead(self):
        self.status = ProxyStatus.DEAD
        self.failure_count += 1

    def mark_success(self):
        self.status = ProxyStatus.ALIVE
        self.success_count += 1

    def mark_failure(self):
        self.status = ProxyStatus.DEAD
        self.failure_count += 1
```

---

# 14. `mark_alive()` và `mark_success()` khác nhau

Điểm này rất đáng chú ý.

Health check:

```text
Proxy
 ↓
health check
 ↓
ALIVE
```

nên:

```python
proxy.mark_alive()
```

Còn fetch thành công:

```text
GET chapter
 ↓
200 OK
 ↓
success
```

nên:

```python
proxy.mark_success()
```

`mark_success()` vừa:

```text
status = ALIVE
success_count += 1
```

---

# 15. Thêm thời gian kiểm tra

Ta muốn biết:

```text
last_checked_at
```

và:

```text
last_failure_at
```

Dùng `datetime`:

```python
from datetime import datetime


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

# 16. Update health check

```python
def mark_health_check(
    self,
    alive: bool,
    checked_at: datetime,
):
    self.last_checked_at = checked_at

    if alive:
        self.status = ProxyStatus.ALIVE
    else:
        self.status = ProxyStatus.DEAD
        self.failure_count += 1
        self.last_failure_at = checked_at
```

Nhưng ở đây ta đang truyền:

```python
alive: bool
```

Có thể thiết kế tốt hơn.

Ta sẽ refactor ở các buổi sau khi xây `ProxyHealthChecker`.

---

# 17. Domain Entity phiên bản Buổi 2

Tạm thời ta có:

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from urllib.parse import urlparse


class ProxyStatus(Enum):
    UNKNOWN = "unknown"
    ALIVE = "alive"
    DEAD = "dead"
    DISABLED = "disabled"


@dataclass(frozen=True)
class ProxyUrl:

    value: str

    def __post_init__(self):
        parsed = urlparse(self.value)

        if parsed.scheme not in {"http", "https"}:
            raise ValueError(
                "Proxy must use http or https"
            )

        if not parsed.hostname:
            raise ValueError(
                "Proxy hostname is required"
            )


@dataclass
class Proxy:

    url: ProxyUrl

    status: ProxyStatus = ProxyStatus.UNKNOWN

    failure_count: int = 0
    success_count: int = 0

    last_checked_at: datetime | None = None
    last_failure_at: datetime | None = None

    def __post_init__(self):

        if self.failure_count < 0:
            raise ValueError(
                "failure_count cannot be negative"
            )

        if self.success_count < 0:
            raise ValueError(
                "success_count cannot be negative"
            )

    def mark_alive(self):
        self.status = ProxyStatus.ALIVE

    def mark_dead(self):
        self.status = ProxyStatus.DEAD
        self.failure_count += 1

    def mark_success(self):
        self.status = ProxyStatus.ALIVE
        self.success_count += 1

    def mark_failure(self):
        self.status = ProxyStatus.DEAD
        self.failure_count += 1
```

---

# 18. Một cải tiến quan trọng: `is_available`

Application không nên viết:

```python
if proxy.status == ProxyStatus.ALIVE:
```

khắp nơi.

Entity nên cung cấp behavior:

```python
@property
def is_available(self) -> bool:
    return self.status == ProxyStatus.ALIVE
```

Sau đó:

```python
if proxy.is_available:
    ...
```

---

# 19. `disable()`

Có trường hợp proxy không phải "chết".

Ví dụ:

```text
Proxy bị admin vô hiệu hóa
```

Ta cần:

```python
def disable(self):
    self.status = ProxyStatus.DISABLED
```

và:

```python
def enable(self):
    self.status = ProxyStatus.UNKNOWN
```

Không nên tự động:

```text
DISABLED → ALIVE
```

vì `ALIVE` phải là kết quả của health check.

Do đó:

```text
disable()
   ↓
DISABLED

enable()
   ↓
UNKNOWN
   ↓
health check
   ↓
ALIVE / DEAD
```

Đây là một invariant tốt.

---

# 20. Toàn bộ state machine

Proxy của chúng ta có thể hình dung:

```text
                    health check
               ┌────────────────────┐
               │                    │
               ▼                    │
           ┌─────────┐              │
           │ UNKNOWN │              │
           └────┬────┘              │
                │                   │
          ┌─────┴─────┐             │
          ▼           ▼             │
      ┌───────┐   ┌──────┐         │
      │ ALIVE │   │ DEAD │◄────────┘
      └───┬───┘   └───┬──┘
          │           │
          │ failure   │
          ▼           │
         DEAD ◄───────┘

             disable
                │
                ▼
          ┌──────────┐
          │ DISABLED │
          └────┬─────┘
               │ enable
               ▼
           UNKNOWN
```

Đây chính là tư duy **Domain Model**, chứ không đơn giản là lưu vài biến.

---

# 21. Một câu hỏi DDD quan trọng

Tại sao:

```python
proxy.mark_failure()
```

tốt hơn:

```python
proxy.failure_count += 1
proxy.status = ProxyStatus.DEAD
```

?

Bởi vì business rule nằm trong Entity:

```text
mark_failure()
      │
      ├── tăng failure_count
      └── chuyển DEAD
```

Sau này nếu rule thay đổi:

```text
3 failure liên tiếp → DEAD
```

ta chỉ sửa Domain.

Không cần đi tìm hàng chục chỗ trong Application Layer.

---

# 22. SOLID ở Buổi 2

### SRP

`Proxy` quản lý **state và behavior của proxy**.

Nó không:

```text
❌ gọi HTTP
❌ kiểm tra internet
❌ đọc SQLite
❌ chọn proxy
```

### DIP

Domain không biết:

```text
httpx
requests
sqlite3
Redis
```

### OCP

Sau này có thể thêm:

```text
HttpProxy
SocksProxy
ResidentialProxy
```

mà không phá toàn bộ Fetcher.

---

# 23. Test Domain trước

Đây là điểm rất quan trọng trong kiến trúc chúng ta đang xây.

Test:

```python
def test_new_proxy_is_unknown():
    proxy = Proxy(
        ProxyUrl("http://127.0.0.1:8080")
    )

    assert proxy.status == ProxyStatus.UNKNOWN
```

Test success:

```python
def test_proxy_success():

    proxy = Proxy(
        ProxyUrl("http://127.0.0.1:8080")
    )

    proxy.mark_success()

    assert proxy.status == ProxyStatus.ALIVE
    assert proxy.success_count == 1
```

Test failure:

```python
def test_proxy_failure():

    proxy = Proxy(
        ProxyUrl("http://127.0.0.1:8080")
    )

    proxy.mark_failure()

    assert proxy.status == ProxyStatus.DEAD
    assert proxy.failure_count == 1
```

Test invalid URL:

```python
def test_invalid_proxy_url():

    try:
        ProxyUrl("hello")
    except ValueError:
        assert True
    else:
        assert False
```

---

# 24. Kiến trúc sau Buổi 2

Ta đã đi từ:

```text
Fetcher
   ↓
httpx
```

đến kiến trúc:

```text
Application
     │
     ▼
   Fetcher
     │
     ▼
ProxyProvider
     │
     ▼
 Proxy Entity
     │
     ├── ProxyUrl
     ├── ProxyStatus
     ├── failure_count
     ├── success_count
     └── state transitions
```

Nhưng **chưa có ProxyProvider implementation**.

Đó chính là nội dung tiếp theo.

---

## Bài tập Buổi 2

Bạn hãy tự viết lại `Proxy` sao cho có các API:

```python
proxy.mark_alive()
proxy.mark_dead()
proxy.mark_success()
proxy.mark_failure()

proxy.disable()
proxy.enable()

proxy.is_available
```

và đảm bảo:

```text
ProxyUrl
 ├── không rỗng
 ├── có scheme http/https
 └── có hostname

Proxy
 ├── failure_count >= 0
 ├── success_count >= 0
 └── DISABLED không được coi là available
```

**Buổi 3:** ta sẽ xây **`ProxyPool` + `ProxyProvider`**, trong đó có **round-robin rotation**, loại proxy `DEAD/DISABLED`, và chuẩn bị interface để sau này cắm SQLite/Redis mà **Fetcher không cần thay đổi**.
