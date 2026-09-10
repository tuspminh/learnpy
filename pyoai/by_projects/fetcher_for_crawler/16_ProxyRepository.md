# Buổi 16 — Repository cho Proxy

Ở Buổi 15, chúng ta đã hoàn thành **Dependency Injection + Composition Root**.

Bây giờ bước tiếp theo là giải quyết một vấn đề mới:

> `ProxyPool` hiện chỉ giữ Proxy trong RAM. Nếu application restart, toàn bộ Proxy và trạng thái của nó biến mất.

Trong project crawler thực tế, chúng ta cần:

```text
Proxy
├── url
├── status
├── failure_count
├── success_count
├── last_checked_at
└── last_failure_at
```

được **lưu persistent**.

Đây là lúc đưa **Repository Pattern** vào Fetcher.

---

# 1. ProxyPool và ProxyRepository không phải một thứ

Đây là điểm đầu tiên cần phân biệt thật rõ.

### ProxyPool

Lo việc:

```text
Proxy rotation
Proxy selection
Round-robin
Skip unavailable proxy
```

Nó phục vụ **runtime**.

### ProxyRepository

Lo việc:

```text
Save Proxy
Find Proxy
Load Proxies
Update Proxy
Delete Proxy
```

Nó phục vụ **persistence**.

Vì vậy:

```text
ProxyPool
    ≠
ProxyRepository
```

Ví dụ:

```text
             Runtime
                │
                ▼
           ProxyPool
                │
                │ selection
                ▼
              Proxy


             Persistence
                │
                ▼
         ProxyRepository
                │
                ▼
             SQLite
```

---

# 2. Vì sao không cho ProxyPool tự lưu SQLite?

Một thiết kế sai thường gặp:

```python
class ProxyPool:
    def __init__(self):
        self._db = sqlite3.connect(...)
```

sau đó:

```python
def get_proxy(self):
    ...
    self._db.execute(...)
```

Lúc này:

```text
ProxyPool
   ├── rotation
   ├── selection
   ├── SQLite
   ├── SQL
   └── persistence
```

`ProxyPool` bắt đầu có quá nhiều trách nhiệm.

Vi phạm **SRP**.

Ngoài ra:

```text
ProxyPool → sqlite3
```

làm Domain/Application bị coupling với Infrastructure.

---

# 3. Repository Pattern

Repository cung cấp một abstraction:

```text
Application / Domain
        │
        ▼
 ProxyRepository
        ▲
        │
SQLiteProxyRepository
        │
        ▼
      SQLite
```

Application chỉ biết:

```python
ProxyRepository
```

không biết:

```python
sqlite3
```

---

# 4. Thiết kế ProxyRepository Interface

Ta bắt đầu từ nhu cầu nghiệp vụ.

Ví dụ:

```python
from abc import ABC, abstractmethod


class ProxyRepository(ABC):
    @abstractmethod
    def save(self, proxy: Proxy) -> None: ...

    @abstractmethod
    def get_by_url(self, url: ProxyUrl) -> Proxy | None: ...

    @abstractmethod
    def list_all(self) -> list[Proxy]: ...

    @abstractmethod
    def delete(self, url: ProxyUrl) -> None: ...
```

Đây là **Port**.

Chưa có SQLite.

---

# 5. Vì sao Repository nhận Domain Entity?

Ta có:

```python
def save(self, proxy: Proxy) -> None:
```

chứ không phải:

```python
def save(
    url: str,
    status: str,
    failure_count: int,
    ...
):
```

Repository làm việc với:

```text
Domain Entity
```

nó không nên buộc Application phải biết cách persistence được biểu diễn như thế nào.

---

# 6. Repository không phải DAO

Hai khái niệm thường bị nhầm.

### DAO

Thường gần database:

```text
SQL
row
column
database record
```

Ví dụ:

```python
dao.insert_proxy(...)
```

### Repository

Đứng ở abstraction cao hơn:

```text
Proxy Entity
     ↓
ProxyRepository
     ↓
Persistence
```

Repository nói ngôn ngữ của Domain:

```python
repository.save(proxy)
```

chứ không phải:

```python
repository.insert_row(...)
```

---

# 7. SQLite Implementation

Infrastructure:

```text
infrastructure/
└── persistence/
    └── sqlite/
        └── proxy_repository.py
```

Ta implement:

```python
class SQLiteProxyRepository(ProxyRepository):
    def __init__(self, connection):
        self._connection = connection
```

Đây chính là DI:

```text
SQLiteProxyRepository
        ↓
connection
```

Repository không tự tạo connection.

---

# 8. Database Schema

Một schema đơn giản:

```sql
CREATE TABLE proxies (
    url TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    failure_count INTEGER NOT NULL DEFAULT 0,
    success_count INTEGER NOT NULL DEFAULT 0,
    last_checked_at TEXT,
    last_failure_at TEXT
);
```

Ví dụ:

```text
proxies
──────────────────────────────────────────
url
status
failure_count
success_count
last_checked_at
last_failure_at
```

---

# 9. Mapping Domain → SQLite

Domain:

```python
Proxy(
    url=ProxyUrl(...),
    status=ProxyStatus.ALIVE,
    failure_count=2,
    success_count=10,
)
```

Database:

```text
url              status    failure_count
─────────────────────────────────────────
http://proxy1    ALIVE     2
```

Repository chịu trách nhiệm mapping.

Đây là một nguyên tắc rất quan trọng:

> **Persistence format không nên rò rỉ vào Domain.**

---

# 10. `save()`

Ví dụ:

```python
class SQLiteProxyRepository(ProxyRepository):
    def __init__(self, connection):
        self._connection = connection

    def save(self, proxy: Proxy) -> None:

        self._connection.execute(
            """
            INSERT INTO proxies (
                url,
                status,
                failure_count,
                success_count,
                last_checked_at,
                last_failure_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(url)
            DO UPDATE SET
                status = excluded.status,
                failure_count = excluded.failure_count,
                success_count = excluded.success_count,
                last_checked_at = excluded.last_checked_at,
                last_failure_at = excluded.last_failure_at
            """,
            (
                proxy.url.value,
                proxy.status.value,
                proxy.failure_count,
                proxy.success_count,
                proxy.last_checked_at,
                proxy.last_failure_at,
            ),
        )
```

Sau đó:

```python
self._connection.commit()
```

Nhưng **hãy chú ý**.

Ở project mà chúng ta đang xây dựng, đây chưa phải thiết kế cuối cùng.

---

# 11. Tại sao `commit()` trong Repository có thể là vấn đề?

Vì chúng ta đã học **Unit of Work** trước đó.

Giả sử Application:

```text
save Proxy A
save Proxy B
save Proxy C
```

Nếu mỗi Repository tự:

```python
commit()
```

thì:

```text
save A → COMMIT
save B → COMMIT
save C → ERROR
```

Database có thể rơi vào trạng thái:

```text
A saved
B saved
C failed
```

Trong khi nghiệp vụ có thể muốn:

```text
A + B + C
```

là một transaction.

Do đó:

> **Repository không nên mặc định sở hữu transaction boundary.**

Đây sẽ kết nối trực tiếp với **Unit of Work** mà bạn đã học.

---

# 12. Kiến trúc tốt hơn

```text
Application Service
       │
       ▼
   UnitOfWork
       │
       ├── ProxyRepository
       │
       ├── NovelRepository
       │
       └── ChapterRepository
       │
       ▼
    SQLite
```

Repository:

```text
CRUD / persistence
```

UoW:

```text
transaction boundary
```

---

# 13. Vì vậy phiên bản Repository đầu tiên

Ta có thể để:

```python
class SQLiteProxyRepository:
    def save(self, proxy):
        self._connection.execute(...)
```

và **không commit**.

Transaction được quản lý bên ngoài.

Ví dụ:

```python
connection.execute("BEGIN")

proxy_repository.save(proxy_a)
proxy_repository.save(proxy_b)
proxy_repository.save(proxy_c)

connection.commit()
```

Nếu lỗi:

```python
connection.rollback()
```

Sau này UoW sẽ làm việc này đẹp hơn.

---

# 14. `get_by_url()`

```python
def get_by_url(
    self,
    url: ProxyUrl,
) -> Proxy | None:

    row = self._connection.execute(
        """
        SELECT
            url,
            status,
            failure_count,
            success_count,
            last_checked_at,
            last_failure_at
        FROM proxies
        WHERE url = ?
        """,
        (url.value,),
    ).fetchone()

    if row is None:
        return None

    return self._to_domain(row)
```

---

# 15. Mapping SQLite Row → Domain

Ta tạo helper:

```python
def _to_domain(self, row) -> Proxy:

    return Proxy(
        url=ProxyUrl(row[0]),
        status=ProxyStatus(row[1]),
        failure_count=row[2],
        success_count=row[3],
        last_checked_at=row[4],
        last_failure_at=row[5],
    )
```

Tuy nhiên code production nên tránh magic index.

Tốt hơn:

```python
self._connection.row_factory = sqlite3.Row
```

Sau đó:

```python
def _to_domain(self, row) -> Proxy:

    return Proxy(
        url=ProxyUrl(row["url"]),
        status=ProxyStatus(row["status"]),
        failure_count=row["failure_count"],
        success_count=row["success_count"],
        last_checked_at=row["last_checked_at"],
        last_failure_at=row["last_failure_at"],
    )
```

Dễ đọc hơn nhiều.

---

# 16. `list_all()`

```python
def list_all(self) -> list[Proxy]:

    rows = self._connection.execute(
        """
        SELECT
            url,
            status,
            failure_count,
            success_count,
            last_checked_at,
            last_failure_at
        FROM proxies
        ORDER BY url
        """
    ).fetchall()

    return [self._to_domain(row) for row in rows]
```

---

# 17. `delete()`

```python
def delete(self, url: ProxyUrl) -> None:

    self._connection.execute(
        """
        DELETE FROM proxies
        WHERE url = ?
        """,
        (url.value,),
    )
```

---

# 18. Hoàn chỉnh Repository

Một phiên bản đầu tiên:

```python
from abc import ABC, abstractmethod
import sqlite3


class ProxyRepository(ABC):
    @abstractmethod
    def save(self, proxy: Proxy) -> None: ...

    @abstractmethod
    def get_by_url(
        self,
        url: ProxyUrl,
    ) -> Proxy | None: ...

    @abstractmethod
    def list_all(self) -> list[Proxy]: ...

    @abstractmethod
    def delete(self, url: ProxyUrl) -> None: ...


class SQLiteProxyRepository(ProxyRepository):
    def __init__(
        self,
        connection: sqlite3.Connection,
    ):
        self._connection = connection

    def save(self, proxy: Proxy) -> None:

        self._connection.execute(
            """
            INSERT INTO proxies (
                url,
                status,
                failure_count,
                success_count,
                last_checked_at,
                last_failure_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(url)
            DO UPDATE SET
                status = excluded.status,
                failure_count = excluded.failure_count,
                success_count = excluded.success_count,
                last_checked_at = excluded.last_checked_at,
                last_failure_at = excluded.last_failure_at
            """,
            (
                proxy.url.value,
                proxy.status.value,
                proxy.failure_count,
                proxy.success_count,
                proxy.last_checked_at,
                proxy.last_failure_at,
            ),
        )

    def get_by_url(
        self,
        url: ProxyUrl,
    ) -> Proxy | None:

        row = self._connection.execute(
            """
            SELECT
                url,
                status,
                failure_count,
                success_count,
                last_checked_at,
                last_failure_at
            FROM proxies
            WHERE url = ?
            """,
            (url.value,),
        ).fetchone()

        if row is None:
            return None

        return self._to_domain(row)

    def list_all(self) -> list[Proxy]:

        rows = self._connection.execute(
            """
            SELECT
                url,
                status,
                failure_count,
                success_count,
                last_checked_at,
                last_failure_at
            FROM proxies
            ORDER BY url
            """
        ).fetchall()

        return [self._to_domain(row) for row in rows]

    def delete(self, url: ProxyUrl) -> None:

        self._connection.execute(
            """
            DELETE FROM proxies
            WHERE url = ?
            """,
            (url.value,),
        )

    @staticmethod
    def _to_domain(row) -> Proxy:

        return Proxy(
            url=ProxyUrl(row["url"]),
            status=ProxyStatus(row["status"]),
            failure_count=row["failure_count"],
            success_count=row["success_count"],
            last_checked_at=row["last_checked_at"],
            last_failure_at=row["last_failure_at"],
        )
```

---

# 19. Nhưng còn `sqlite3` ở đâu?

Đây là điều rất quan trọng về Clean Architecture.

Không:

```text
domain/
    proxy_repository.py
        import sqlite3  ❌
```

Mà:

```text
domain/
    repositories/
        proxy.py
```

chứa abstraction:

```python
class ProxyRepository(ABC): ...
```

Còn:

```text
infrastructure/
    persistence/
        sqlite/
            proxy_repository.py
```

mới:

```python
import sqlite3
```

Kiến trúc:

```text
                 DOMAIN
                    │
             ProxyRepository
                    ▲
                    │ implements
                    │
              INFRASTRUCTURE
                    │
        SQLiteProxyRepository
                    │
                    ▼
                 sqlite3
```

---

# 20. Fake Repository

DI giúp ta tạo Fake Repository cực dễ.

```python
class FakeProxyRepository(ProxyRepository):
    def __init__(self):
        self._items: dict[str, Proxy] = {}

    def save(self, proxy: Proxy) -> None:
        self._items[proxy.url.value] = proxy

    def get_by_url(
        self,
        url: ProxyUrl,
    ) -> Proxy | None:

        return self._items.get(url.value)

    def list_all(self) -> list[Proxy]:

        return list(self._items.values())

    def delete(self, url: ProxyUrl) -> None:

        self._items.pop(url.value, None)
```

Bây giờ test:

```text
Application
     ↓
FakeProxyRepository
     ↓
dict
```

Không cần SQLite.

---

# 21. Repository không phải ProxyPool

Ví dụ có 100 proxy trong database:

```text
SQLite
  │
  │ list_all()
  ▼
100 Proxy
  │
  ▼
ProxyPool
```

ProxyPool có thể giữ:

```text
A
B
C
D
...
```

và thực hiện:

```text
A → B → C → D → A
```

Repository chỉ làm:

```text
LOAD
SAVE
UPDATE
DELETE
```

Đây là hai abstraction khác nhau.

---

# 22. Ai tạo ProxyPool?

Đây là câu hỏi quan trọng sau khi có Repository.

Không để:

```python
class ProxyPool:
    def __init__(self):
        repository = SQLiteProxyRepository(...)
        proxies = repository.list_all()
```

Sai.

Thay vào đó Composition Root:

```python
proxy_repository = SQLiteProxyRepository(connection)

proxies = proxy_repository.list_all()

proxy_pool = ProxyPool(proxies)
```

Graph:

```text
SQLite
   │
   ▼
ProxyRepository
   │
   ▼
list_all()
   │
   ▼
Proxy[]
   │
   ▼
ProxyPool
```

---

# 23. Nhưng có một vấn đề mới

Khi Proxy thay đổi:

```python
proxy.mark_dead()
```

thì database chưa tự thay đổi.

Ta có:

```text
Proxy
  │
  └── mark_dead()
        │
        ▼
   memory changed
```

nhưng:

```text
SQLite
   │
   └── vẫn dữ liệu cũ
```

Cần:

```python
proxy.mark_dead()

repository.save(proxy)
```

Đây là persistence synchronization.

---

# 24. Ai gọi `repository.save()`?

Đây là nơi Application Service bắt đầu đóng vai trò.

Ví dụ:

```python
class CheckProxyService:
    def __init__(
        self,
        health_service: ProxyHealthService,
        proxy_repository: ProxyRepository,
    ):
        self._health_service = health_service
        self._proxy_repository = proxy_repository

    def execute(self, proxy: Proxy) -> bool:

        healthy = self._health_service.verify(proxy)

        self._proxy_repository.save(proxy)

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
Proxy.mark_alive()
       │
       ▼
ProxyRepository.save()
       │
       ▼
SQLite
```

---

# 25. Nhưng chưa nên vội đưa Repository vào Fetcher

Đây là một điểm kiến trúc rất quan trọng.

Ta **không nên** biến Fetcher thành:

```text
Fetcher
 ├── HTTP
 ├── Proxy
 ├── UA
 ├── Retry
 ├── Policy
 ├── Repository
 ├── SQLite
 └── Transaction
```

Nếu làm vậy:

> Fetcher lại trở thành God Object.

Hiện tại nên giữ:

```text
Fetcher
    │
    ├── ProxySelector
    ├── UA Provider
    ├── HttpClient
    ├── ErrorClassifier
    └── FetchPolicy
```

Persistence sẽ được orchestration ở Application layer.

---

# 26. Đây chính là DDD + Clean Architecture

Ta đang có:

```text
DOMAIN
─────────────────────────
Proxy
ProxyUrl
ProxyStatus

ProxyRepository
ProxyHealthService
HealthyProxySelector


APPLICATION
─────────────────────────
FetchUrlService
Fetcher
FetchPolicy
ErrorClassifier


INFRASTRUCTURE
─────────────────────────
HttpxClient
SQLiteProxyRepository
SQLite Connection
```

Dependency:

```text
Infrastructure
      ↓
Application
      ↓
Domain
```

nhưng abstraction:

```text
Domain
   ↑
Infrastructure implementation
```

---

# 27. Repository và DIP

Không:

```text
Application
    ↓
SQLiteProxyRepository
    ↓
sqlite3
```

Mà:

```text
Application
    ↓
ProxyRepository
    ↑
SQLiteProxyRepository
```

Đây chính là:

> **Dependency Inversion Principle**

Application không quan tâm database là:

```text
SQLite
PostgreSQL
Redis
JSON
Memory
```

---

# 28. Fake vs SQLite

Cùng một interface:

```python
ProxyRepository
```

có thể có:

```text
                 ProxyRepository
                  ▲    ▲    ▲
                  │    │    │
                  │    │    └── InMemoryProxyRepository
                  │    └─────── FakeProxyRepository
                  └──────────── SQLiteProxyRepository
```

Production:

```python
repository = SQLiteProxyRepository(connection)
```

Test:

```python
repository = FakeProxyRepository()
```

Application không cần thay đổi.

Đây chính là sức mạnh của abstraction + DI.

---

# 29. Composition Root sau Buổi 16

Buổi 15:

```text
Composition Root
   │
   ├── ProxyPool
   ├── UserAgentPool
   ├── HttpxClient
   ├── HealthChecker
   ├── HealthService
   ├── ProxySelector
   ├── Fetcher
   └── ApplicationService
```

Bây giờ thêm:

```text
Composition Root
   │
   ├── Database Connection
   │
   ├── ProxyRepository
   │
   ├── ProxyPool
   │
   ├── UserAgentPool
   │
   ├── HttpClient
   │
   ├── HealthChecker
   │
   ├── HealthService
   │
   ├── ProxySelector
   │
   ├── FetchPolicy
   │
   ├── Fetcher
   │
   └── ApplicationService
```

---

# 30. Bài tập thực hành Buổi 16

## Bài 1 — Interface

Tạo:

```text
domain/
└── repositories/
    └── proxy.py
```

với:

```python
class ProxyRepository(ABC): ...
```

có:

```text
save()
get_by_url()
list_all()
delete()
```

---

## Bài 2 — SQLite

Tạo:

```text
infrastructure/
└── persistence/
    └── sqlite/
        └── proxy_repository.py
```

Implement:

```text
SQLiteProxyRepository
```

---

## Bài 3 — Fake

Tạo:

```text
tests/
└── fakes/
    └── proxy_repository.py
```

với:

```text
FakeProxyRepository
```

---

## Bài 4 — Round trip

Test:

```text
Proxy
  ↓
save()
  ↓
SQLite
  ↓
get_by_url()
  ↓
Proxy
```

và kiểm tra:

```text
url
status
failure_count
success_count
last_checked_at
last_failure_at
```

đều được khôi phục đúng.

---

## Bài 5 — Quan trọng nhất

Test:

```text
Proxy
  ↓
mark_dead()
  ↓
repository.save()
  ↓
repository.get_by_url()
```

Kết quả phải:

```text
status == DEAD
```

---

# 31. Roadmap chúng ta đang ở đâu?

```text
13 Domain Service                 ✅
        ↓
14 Application Service            ✅
        ↓
15 Dependency Injection           ✅
        ↓
16 Repository cho Proxy           ← HIỆN TẠI
        ↓
17 Proxy State
        ↓
18 Circuit Breaker
        ↓
19 Rate Limiting
        ↓
20 Fetch Orchestration
```

Buổi 16 tạo nền móng persistence, nhưng **chưa đưa UoW vào**. Vì bạn đã học SQLite Connection Manager + UoW ở track riêng, chúng ta sẽ tận dụng kiến thức đó ở bước phù hợp thay vì trộn quá nhiều abstraction vào bài này.

### Mental model cần nhớ

```text
Proxy
  │
  │ domain state
  ▼
ProxyRepository       ← abstraction
  ▲
  │ implementation
  │
SQLiteProxyRepository
  │
  ▼
SQLite
```

Còn:

```text
ProxyRepository
```

**không thay thế**:

```text
ProxyPool
```

mà:

```text
ProxyRepository = persistence
ProxyPool       = runtime selection
```

Đây là hai khái niệm bạn cần giữ thật chắc trước khi sang **Buổi 17 — Proxy State + Persistence**, nơi chúng ta sẽ thiết kế sâu hơn cách `ALIVE / DEAD / DISABLED`, `failure_count`, cooldown và việc đồng bộ state giữa **Domain → Repository → SQLite**.
