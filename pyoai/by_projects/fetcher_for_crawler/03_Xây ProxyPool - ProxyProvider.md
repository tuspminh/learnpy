# Buổi 3 — Xây `ProxyPool` + `ProxyProvider`

Hôm nay ta xây thành phần chịu trách nhiệm **quản lý và xoay vòng proxy**.

Mục tiêu:

```text
ProxyPool
    │
    ├── thêm proxy
    ├── xoay vòng proxy
    ├── bỏ qua DEAD
    ├── bỏ qua DISABLED
    └── quản lý thứ tự proxy

Fetcher
    │
    ▼
ProxyProvider
    │
    ▼
ProxyPool
```

Điểm quan trọng: **Fetcher không quản lý danh sách proxy**.

---

# 1. Bài toán thực tế

Giả sử có:

```text
Proxy A
Proxy B
Proxy C
Proxy D
```

Fetcher thực hiện:

```text
request 1 → A
request 2 → B
request 3 → C
request 4 → D
request 5 → A
request 6 → B
...
```

Đây là **Round-Robin**.

Nhưng nếu:

```text
B = DEAD
```

thì:

```text
request 1 → A
request 2 → C
request 3 → D
request 4 → A
...
```

Nếu:

```text
C = DISABLED
```

thì cũng bỏ qua C.

---

# 2. Interface `ProxyProvider`

Ta bắt đầu bằng abstraction.

```python
# domain/proxy/interfaces.py

from abc import ABC, abstractmethod

from .entities import Proxy


class ProxyProvider(ABC):

    @abstractmethod
    def get_proxy(self) -> Proxy:
        """Return next available proxy."""
        raise NotImplementedError
```

Fetcher chỉ cần biết:

```python
proxy = proxy_provider.get_proxy()
```

Nó không biết proxy được lưu ở:

```text
memory
SQLite
Redis
file
API
```

---

# 3. Vì sao `ProxyPool` không phải Repository?

Đây là điểm DDD rất quan trọng.

`Repository` thường đại diện cho việc:

```text
lưu trữ / truy xuất Aggregate
```

Ví dụ sau này:

```python
class ProxyRepository:
    def get(self, proxy_id):
        ...

    def save(self, proxy):
        ...
```

Còn `ProxyPool` có trách nhiệm:

```text
quản lý tập proxy đang được sử dụng
+
selection/rotation
```

Do đó:

```text
ProxyRepository
    ↓
Persistence

ProxyPool
    ↓
Runtime selection
```

Hai khái niệm khác nhau.

---

# 4. In-memory ProxyPool

Ta tạo:

```text
infrastructure/
└── proxy/
    └── proxy_pool.py
```

Code phiên bản đầu tiên:

```python
from domain.proxy.entities import Proxy
from domain.proxy.interfaces import ProxyProvider


class ProxyPool(ProxyProvider):

    def __init__(self, proxies: list[Proxy]):
        self._proxies = proxies
        self._index = 0

    def get_proxy(self) -> Proxy:
        ...
```

Ta sẽ xây từng bước.

---

# 5. Round-Robin cơ bản

Giả sử:

```python
proxies = [
    Proxy(ProxyUrl("http://proxy-a:8080")),
    Proxy(ProxyUrl("http://proxy-b:8080")),
    Proxy(ProxyUrl("http://proxy-c:8080")),
]
```

Ta cần:

```text
index = 0 → A
index = 1 → B
index = 2 → C
index = 0 → A
```

Dùng modulo:

```python
self._index = (
    self._index + 1
) % len(self._proxies)
```

---

# 6. Code

```python
class ProxyPool(ProxyProvider):

    def __init__(self, proxies: list[Proxy]):
        if not proxies:
            raise ValueError("Proxy pool cannot be empty")

        self._proxies = proxies
        self._index = 0

    def get_proxy(self) -> Proxy:

        proxy = self._proxies[self._index]

        self._index = (
            self._index + 1
        ) % len(self._proxies)

        return proxy
```

---

# 7. Test

```python
def test_round_robin():

    a = Proxy(
        ProxyUrl("http://proxy-a:8080")
    )

    b = Proxy(
        ProxyUrl("http://proxy-b:8080")
    )

    c = Proxy(
        ProxyUrl("http://proxy-c:8080")
    )

    pool = ProxyPool([a, b, c])

    assert pool.get_proxy() is a
    assert pool.get_proxy() is b
    assert pool.get_proxy() is c
    assert pool.get_proxy() is a
    assert pool.get_proxy() is b
```

Đây là Round-Robin cơ bản.

---

# 8. Nhưng có vấn đề

Proxy mới tạo có:

```text
UNKNOWN
```

Theo thiết kế Buổi 2:

```text
UNKNOWN
ALIVE
DEAD
DISABLED
```

Pool không nên đưa `DEAD` hoặc `DISABLED` cho Fetcher.

Ta tạo:

```python
def _available_proxies(self) -> list[Proxy]:
    return [
        proxy
        for proxy in self._proxies
        if proxy.is_available
    ]
```

Nhưng nhớ rằng:

```python
@property
def is_available(self):
    return self.status == ProxyStatus.ALIVE
```

Vậy proxy `UNKNOWN` cũng không được chọn.

---

# 9. Có một vấn đề thiết kế

Nếu proxy mới load từ SQLite:

```text
A UNKNOWN
B UNKNOWN
C UNKNOWN
```

thì:

```python
pool.get_proxy()
```

không có proxy nào available.

Nhưng **đây lại chính là điều ta cần**, bởi vì:

> Proxy phải được health-check trước khi fetch.

Vì vậy trong kiến trúc cuối cùng, `ProxyPool` không nhất thiết phải yêu cầu proxy đã `ALIVE`.

Ta có thể để Pool chọn:

```text
UNKNOWN
ALIVE
```

nhưng bỏ:

```text
DEAD
DISABLED
```

Điều này phù hợp với flow:

```text
Pool
 ↓
UNKNOWN proxy
 ↓
HealthChecker
 ↓
ALIVE
 ↓
Fetcher
```

---

# 10. Định nghĩa `is_selectable`

Thay vì:

```python
is_available
```

ta tạo khái niệm chính xác hơn:

```python
@property
def is_selectable(self) -> bool:
    return self.status != ProxyStatus.DISABLED
```

Nhưng `DEAD` thì sao?

Ta muốn proxy DEAD có thể được thử lại sau này.

Vì vậy:

```text
UNKNOWN → selectable
ALIVE   → selectable
DEAD    → selectable sau một khoảng thời gian
DISABLED → không selectable
```

Đây là lý do ở production ta **không nên dùng một boolean `alive`**.

---

# 11. Phiên bản đơn giản cho Buổi 3

Hôm nay ta chưa xây cooldown.

Ta quy định:

```text
UNKNOWN  → chọn
ALIVE    → chọn
DEAD     → bỏ qua
DISABLED → bỏ qua
```

Thêm vào Entity:

```python
@property
def is_selectable(self) -> bool:
    return self.status in {
        ProxyStatus.UNKNOWN,
        ProxyStatus.ALIVE,
    }
```

---

# 12. ProxyPool lọc proxy

```python
class ProxyPool(ProxyProvider):

    def __init__(self, proxies: list[Proxy]):
        if not proxies:
            raise ValueError(
                "Proxy pool cannot be empty"
            )

        self._proxies = proxies
        self._index = 0

    def get_proxy(self) -> Proxy:

        total = len(self._proxies)

        for _ in range(total):

            proxy = self._proxies[self._index]

            self._index = (
                self._index + 1
            ) % total

            if proxy.is_selectable:
                return proxy

        raise RuntimeError(
            "No selectable proxy available"
        )
```

---

# 13. Vì sao dùng vòng `for`?

Giả sử:

```text
A ALIVE
B DEAD
C ALIVE
D DEAD
```

Lần đầu:

```text
A
```

lần sau:

```text
B → bỏ
C → chọn
```

lần sau:

```text
D → bỏ
A → chọn
```

Ta không được:

```python
while True:
    ...
```

vì nếu toàn bộ proxy đều DEAD:

```text
A DEAD
B DEAD
C DEAD
```

thì sẽ:

```text
while True
   ↓
A
B
C
A
B
C
...
```

→ infinite loop.

Giới hạn:

```python
for _ in range(total):
```

giúp ta chắc chắn terminate.

---

# 14. Test bỏ qua DEAD

```python
def test_skip_dead_proxy():

    a = Proxy(
        ProxyUrl("http://proxy-a:8080")
    )

    b = Proxy(
        ProxyUrl("http://proxy-b:8080")
    )

    c = Proxy(
        ProxyUrl("http://proxy-c:8080")
    )

    b.mark_dead()

    pool = ProxyPool([a, b, c])

    assert pool.get_proxy() is a
    assert pool.get_proxy() is c
    assert pool.get_proxy() is a
    assert pool.get_proxy() is c
```

---

# 15. Test DISABLED

```python
def test_skip_disabled_proxy():

    a = Proxy(
        ProxyUrl("http://proxy-a:8080")
    )

    b = Proxy(
        ProxyUrl("http://proxy-b:8080")
    )

    b.disable()

    pool = ProxyPool([a, b])

    assert pool.get_proxy() is a
    assert pool.get_proxy() is a
```

---

# 16. Test tất cả đều chết

```python
def test_no_selectable_proxy():

    a = Proxy(
        ProxyUrl("http://proxy-a:8080")
    )

    b = Proxy(
        ProxyUrl("http://proxy-b:8080")
    )

    a.mark_dead()
    b.mark_dead()

    pool = ProxyPool([a, b])

    try:
        pool.get_proxy()
    except RuntimeError:
        assert True
    else:
        assert False
```

Sau này ta sẽ tạo exception riêng:

```text
NoAvailableProxy
```

thay vì `RuntimeError`.

---

# 17. Nhưng Pool đang hơi "biết quá nhiều"

Hiện tại:

```text
ProxyPool
   ↓
ProxyStatus
   ↓
Proxy Entity
```

Điều này **không sai**.

Pool là Domain/Application concept liên quan trực tiếp tới Proxy.

Nhưng ta cần tránh việc Pool biết:

```text
httpx
HTTP status
timeout
network error
```

Pool tuyệt đối không được:

```python
httpx.get(...)
```

Health check thuộc component khác.

---

# 18. Flow sau Buổi 3

Ta đang tiến tới:

```text
                  Fetcher
                     │
                     ▼
              ProxyProvider
                     │
                     ▼
                 ProxyPool
                     │
                     ▼
                Proxy A
                     │
                     ▼
             HealthChecker
                /       \
              DEAD     ALIVE
               │          │
               ▼          ▼
            next       HttpClient
                          │
                          ▼
                         URL
```

Đây là kiến trúc rất tốt cho việc test.

---

# 19. Dependency Injection

Fetcher sẽ nhận Pool từ bên ngoài:

```python
class Fetcher:

    def __init__(
        self,
        proxy_provider: ProxyProvider,
    ):
        self._proxy_provider = proxy_provider
```

Khởi tạo:

```python
pool = ProxyPool(proxies)

fetcher = Fetcher(
    proxy_provider=pool
)
```

Fetcher không cần:

```python
ProxyPool(...)
```

bên trong.

Đây là **Dependency Injection**.

---

# 20. Lợi ích của DI

Production:

```text
Fetcher
   ↓
ProxyPool
```

Test:

```text
Fetcher
   ↓
FakeProxyProvider
```

Ví dụ:

```python
class FakeProxyProvider:

    def __init__(self, proxy):
        self.proxy = proxy

    def get_proxy(self):
        return self.proxy
```

Test:

```python
fake = FakeProxyProvider(proxy)

fetcher = Fetcher(
    proxy_provider=fake
)
```

Không cần proxy thật.

Không cần Internet.

Không cần `httpx`.

Đây chính là một trong những lợi ích lớn nhất của SOLID.

---

# 21. Một vấn đề cần giải quyết ở buổi sau

Hiện tại ta có:

```text
UNKNOWN
   ↓
ProxyPool
   ↓
Proxy
```

Nhưng làm thế nào kiểm tra:

```text
Proxy còn sống?
```

Ta **không muốn**:

```python
class Proxy:

    def check(self):
        httpx.get(...)
```

Mà sẽ tạo:

```text
ProxyHealthChecker
```

và implementation:

```text
HttpxProxyHealthChecker
```

Flow:

```text
ProxyPool
    ↓
Proxy
    ↓
ProxyHealthChecker
    ↓
HTTP request
    ↓
ALIVE / DEAD
```

---

# 22. Kiến trúc hiện tại

Sau 3 buổi:

```text
domain/
│
└── proxy/
    │
    ├── entities.py
    │      ├── Proxy
    │      ├── ProxyUrl
    │      └── ProxyStatus
    │
    └── interfaces.py
           └── ProxyProvider


infrastructure/
│
└── proxy/
       └── proxy_pool.py
```

Và dependency:

```text
ProxyPool
     │
     ▼
ProxyProvider
     ▲
     │
   Fetcher
```

---

# 23. Một lưu ý về thiết kế production

Ta **chưa nên** vội thêm:

```text
random.choice()
```

để xoay proxy.

Có hai kiểu:

### Random

```python
random.choice(proxies)
```

### Round-Robin

```text
A → B → C → A → B → C
```

Với crawler, Round-Robin dễ:

* test
* debug
* theo dõi
* dự đoán hành vi

Sau này ta có thể thiết kế abstraction:

```text
ProxySelectionStrategy
       │
       ├── RoundRobinStrategy
       ├── RandomStrategy
       └── WeightedStrategy
```

Đây sẽ là một bài rất hay về **Strategy Pattern + OCP**.

---

# Bài tập Buổi 3

Tự xây `ProxyPool` với các yêu cầu:

```text
1. Không nhận pool rỗng.

2. Round-robin:
   A → B → C → A → B → C

3. Bị DEAD:
   A → C → A → C

4. DISABLED:
   bỏ qua hoàn toàn.

5. Nếu tất cả không selectable:
   raise NoAvailableProxy.

6. Không sử dụng httpx.
```

Kiến trúc mục tiêu:

```text
             Fetcher
                │
                ▼
         ProxyProvider
                ▲
                │
           ProxyPool
                │
                ▼
              Proxy
```

**Buổi 4** ta sẽ xây `UserAgentPool`: xoay vòng User-Agent, thiết kế `UserAgentProvider`, sau đó bắt đầu ghép **Proxy + User-Agent** thành request context. Sau đó mới bước sang `httpx sync`.
