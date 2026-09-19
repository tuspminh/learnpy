# 📖 Bài 17: Event Sourcing — Lưu state dưới dạng chuỗi sự kiện

> Chào mừng bạn đến **Level 5 — Chuyên sâu**. Đây là bài học **khó nhất** của cả lộ trình. Event Sourcing thay đổi **cách bạn nghĩ về state**: không lưu "state hiện tại", mà lưu **toàn bộ lịch sử sự kiện**. Từ đó, state hiện tại được **tái tạo bằng cách replay events**. Nghe thì đơn giản, nhưng nó mở ra một **thế giới mới** — và cũng đầy **cạm bẫy**.

---

## 🎯 Mục tiêu bài học

Sau bài này, bạn sẽ:

1. Hiểu **Event Sourcing** là gì và tại sao nó mạnh mẽ.
2. Phân biệt **Event Sourcing** vs **Event-Driven** vs **Event Notification**.
3. Biết **khi nào dùng**, **khi nào không** Event Sourcing.
4. Hiểu **Event Store** — cấu trúc và API.
5. Viết **Event-Sourced Aggregate** trong Python.
6. Hiểu **replay**, **snapshot**, **versioning**.
7. Biết **projection** — build read model từ events.
8. Tránh được **8 anti-pattern** khi dùng Event Sourcing.
9. Làm bài tập thực hành có chấm điểm.

---

## 1. Event Sourcing là gì?

### 1.1. Định nghĩa

> **Event Sourcing** là kỹ thuật lưu **toàn bộ lịch sử sự kiện** của một Aggregate, thay vì chỉ lưu state hiện tại. State hiện tại được **tái tạo bằng cách replay** toàn bộ events từ đầu.

### 1.2. Trực giác

Hãy nghĩ về **tài khoản ngân hàng**.

**Cách 1: Lưu state (truyền thống)**

```
accounts:
  id  | balance
  ----|--------
  A1  | 700,000
```

Bạn biết số dư hiện tại, nhưng **không biết**:
- Hôm qua số dư là bao nhiêu?
- Tiền vào từ đâu?
- Có giao dịch bất thường không?

**Cách 2: Lưu events (Event Sourcing)**

```
events:
  id  | aggregate_id | type             | amount  | occurred_at
  ----|--------------|------------------|---------|-------------
  1   | A1           | AccountOpened    | 0       | 2026-01-01
  2   | A1           | MoneyDeposited   | 1,000,000| 2026-01-02
  3   | A1           | MoneyWithdrawn   | -300,000 | 2026-01-03
  4   | A1           | MoneyDeposited   | 500,000 | 2026-01-04
  5   | A1           | MoneyWithdrawn   | -500,000 | 2026-01-05
```

**State hiện tại** = replay tất cả events:

```
0 + 1,000,000 - 300,000 + 500,000 - 500,000 = 700,000
```

**Điều kỳ diệu:** Bạn có **toàn bộ lịch sử**, không chỉ state.

### 1.3. Tại sao mạnh mẽ?

| Lợi ích | Giải thích |
|---|---|
| **Audit log tự nhiên** | Mọi thay đổi đều được ghi lại |
| **Time travel** | Replay đến bất kỳ thời điểm nào |
| **Debug dễ** | Biết chính xác chuyện gì xảy ra |
| **Event-driven tự nhiên** | Event có sẵn để publish |
| **Không mất dữ liệu** | Không UPDATE, không DELETE |
| **Rebuild read model** | Có thể rebuild bất kỳ lúc nào |
| **Business insight** | Phân tích hành vi user |

### 1.4. Event Sourcing vs Event-Driven vs Event Notification

Đây là **3 khái niệm khác nhau** mà nhiều dev nhầm.

| Tiêu chí | Event Notification | Event-Driven | Event Sourcing |
|---|---|---|---|
| **Event là gì** | Thông báo | Sự kiện | Nguồn sự thật |
| **Lưu event?** | Không | Có thể | **Bắt buộc** |
| **Replay?** | Không | Không | **Có** |
| **Source of truth** | DB | DB + event | **Event store** |
| **Độ phức tạp** | Thấp | Vừa | Cao |
| **Ví dụ** | "Order placed" (chỉ notify) | "Order placed" (handler update read model) | "Order placed" (lưu vào event store) |

**Insight:** Event Sourcing là **cấp độ cao nhất** — event là **source of truth**, không phải DB.

---

## 2. Khi nào dùng Event Sourcing?

### 2.1. Nên dùng khi

**1. Cần audit log đầy đủ**

- Ngân hàng, bảo hiểm, y tế, pháp lý.
- Mọi thay đổi phải được ghi lại.

**2. Cần time travel**

- Analytics: "User làm gì trong 30 ngày qua?"
- Compliance: "State tại thời điểm X là gì?"

**3. Cần rebuild read model**

- Khi thêm read model mới, replay events để build.
- Khi read model bị hỏng, replay để fix.

**4. Domain có tính "event-heavy"**

- Trading, IoT, gaming, logistics.
- Nhiều sự kiện nhỏ xảy ra liên tục.

**5. Cần debug phức tạp**

- Bug khó reproduce? Replay events để reproduce.

**6. Cần tích hợp nhiều hệ thống**

- Event store là source of truth, nhiều consumer.

### 2.2. KHÔNG nên dùng khi

**1. CRUD đơn giản**

- Blog, todo list, admin panel.
- Event Sourcing là over-engineering.

**2. Không cần audit**

- Nếu không cần lịch sử, đừng dùng.

**3. Team chưa có kinh nghiệm**

- Event Sourcing có **learning curve** cao.
- Cần hiểu CQRS, eventual consistency, versioning.

**4. Query phức tạp**

- Event Sourcing **không phù hợp** cho query phức tạp.
- Cần CQRS + read model.

**5. Dữ liệu lớn, tần suất cao**

- Mỗi thay đổi = 1 event → storage tăng nhanh.
- Cần snapshot để tối ưu.

### 2.3. Quy tắc ngón tay

> **Nếu bạn không chắc mình cần Event Sourcing, bạn KHÔNG cần.**
>
> Nó là **công cụ mạnh** nhưng **đắt**. Chỉ dùng khi **audit** hoặc **time travel** là yêu cầu **bắt buộc**.

---

## 3. Event Store

### 3.1. Định nghĩa

> **Event Store** là nơi lưu events. Nó là **append-only** — chỉ thêm, không sửa, không xóa.

### 3.2. API tối thiểu

```python
class EventStore(Protocol):
    def append(
        self,
        aggregate_id: UUID,
        events: list[DomainEvent],
        expected_version: int,
    ) -> None:
        """Thêm events cho aggregate. Raise nếu version không khớp."""
        ...

    def load(
        self,
        aggregate_id: UUID,
    ) -> list[DomainEvent]:
        """Load tất cả events của aggregate theo thứ tự."""
        ...

    def load_from_version(
        self,
        aggregate_id: UUID,
        from_version: int,
    ) -> list[DomainEvent]:
        """Load events từ version X."""
        ...
```

**Điểm mấu chốt:**

- `append` có **optimistic concurrency** qua `expected_version`.
- `load` trả về **toàn bộ** events theo thứ tự.
- **Không có** `update`, `delete`.

### 3.3. Schema

```sql
CREATE TABLE events (
    id              UUID PRIMARY KEY,
    aggregate_id    UUID NOT NULL,
    aggregate_type  VARCHAR(100) NOT NULL,
    version         INT NOT NULL,
    event_type      VARCHAR(100) NOT NULL,
    payload         JSONB NOT NULL,
    occurred_at     TIMESTAMPTZ NOT NULL,
    UNIQUE (aggregate_id, version)   -- optimistic concurrency
);

CREATE INDEX idx_events_aggregate ON events (aggregate_id, version);
CREATE INDEX idx_events_type ON events (event_type, occurred_at);
```

**Điểm mấu chốt:**

- `UNIQUE (aggregate_id, version)` — đảm bảo không có 2 events cùng version.
- `payload` là JSON — chứa data của event.
- `version` tăng dần từ 1.

### 3.4. Optimistic Concurrency

**Vấn đề:** 2 request cùng update 1 aggregate.

**Giải pháp:** Mỗi event có `version`. Khi `append`, check version khớp.

```python
# Request A: load aggregate (version 5)
# Request B: load aggregate (version 5)

# Request A: append events (expected_version=5)
# → OK, version giờ là 7

# Request B: append events (expected_version=5)
# → FAIL! Version đã là 7
# → Raise ConcurrencyError
```

**Điều này quan trọng** — Event Sourcing không dùng lock, mà dùng optimistic concurrency.

### 3.5. Implementation đơn giản (in-memory)

```python
from collections import defaultdict
from uuid import UUID
from shop.domain.events.base import DomainEvent


class ConcurrencyError(Exception):
    def __init__(self, aggregate_id: UUID, expected: int, actual: int) -> None:
        super().__init__(
            f"Aggregate {aggregate_id}: expected version {expected}, "
            f"actual {actual}"
        )


class InMemoryEventStore:
    def __init__(self) -> None:
        self._events: dict[UUID, list[DomainEvent]] = defaultdict(list)

    def append(
        self,
        aggregate_id: UUID,
        events: list[DomainEvent],
        expected_version: int,
    ) -> None:
        current_version = len(self._events[aggregate_id])
        if current_version != expected_version:
            raise ConcurrencyError(aggregate_id, expected_version, current_version)

        self._events[aggregate_id].extend(events)

    def load(self, aggregate_id: UUID) -> list[DomainEvent]:
        return list(self._events[aggregate_id])

    def load_from_version(
        self,
        aggregate_id: UUID,
        from_version: int,
    ) -> list[DomainEvent]:
        return self._events[aggregate_id][from_version:]
```

### 3.6. Implementation SQLAlchemy

```python
from sqlalchemy.orm import Session
from sqlalchemy import text
import json
from uuid import UUID


class SqlAlchemyEventStore:
    def __init__(self, session: Session) -> None:
        self._session = session

    def append(
        self,
        aggregate_id: UUID,
        events: list[DomainEvent],
        expected_version: int,
    ) -> None:
        # Check version
        current_version = self._session.execute(
            text("""
                SELECT COALESCE(MAX(version), 0) FROM events
                WHERE aggregate_id = :aid
            """),
            {"aid": str(aggregate_id)},
        ).scalar() or 0

        if current_version != expected_version:
            raise ConcurrencyError(aggregate_id, expected_version, current_version)

        # Append events
        for i, event in enumerate(events, start=expected_version + 1):
            self._session.execute(
                text("""
                    INSERT INTO events
                    (id, aggregate_id, aggregate_type, version,
                     event_type, payload, occurred_at)
                    VALUES (:id, :aid, :atype, :ver, :etype, :payload, :at)
                """),
                {
                    "id": str(event.event_id),
                    "aid": str(aggregate_id),
                    "atype": event.__class__.__name__,
                    "ver": i,
                    "etype": event.__class__.__name__,
                    "payload": json.dumps(asdict(event), default=str),
                    "at": event.occurred_at,
                },
            )

    def load(self, aggregate_id: UUID) -> list[DomainEvent]:
        rows = self._session.execute(
            text("""
                SELECT event_type, payload FROM events
                WHERE aggregate_id = :aid
                ORDER BY version
            """),
            {"aid": str(aggregate_id)},
        ).fetchall()

        return [self._deserialize(row.event_type, row.payload) for row in rows]

    def _deserialize(self, event_type: str, payload: dict) -> DomainEvent:
        # Lookup event class từ registry
        cls = EVENT_REGISTRY[event_type]
        return cls(**payload)
```

---

## 4. Event-Sourced Aggregate

### 4.1. Bộ khung

Đây là **bộ khung Aggregate** cho Event Sourcing:

```python
from dataclasses import dataclass, field
from uuid import UUID
from shop.domain.events.base import DomainEvent


class EventSourcedAggregate:
    """
    Base class cho mọi Event-Sourced Aggregate.

    - Lưu version hiện tại.
    - Track uncommitted events.
    - Apply events để update state.
    """

    def __init__(self, aggregate_id: UUID) -> None:
        self._id = aggregate_id
        self._version = 0
        self._changes: list[DomainEvent] = []

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def version(self) -> int:
        return self._version

    @classmethod
    def from_history(
        cls,
        aggregate_id: UUID,
        events: list[DomainEvent],
    ) -> "EventSourcedAggregate":
        """Reconstruct từ event history."""
        obj = cls.__new__(cls)
        obj._id = aggregate_id
        obj._version = 0
        obj._changes = []

        for event in events:
            obj._apply(event)
            obj._version += 1

        return obj

    def _apply(self, event: DomainEvent) -> None:
        """Apply event — dispatch tới handler."""
        handler = getattr(self, f"_on_{type(event).__name__}", None)
        if handler is None:
            raise NotImplementedError(
                f"Missing handler for {type(event).__name__}"
            )
        handler(event)

    def _raise(self, event: DomainEvent) -> None:
        """Apply event và track là uncommitted."""
        self._apply(event)
        self._changes.append(event)
        self._version += 1

    def pull_changes(self) -> list[DomainEvent]:
        """Lấy uncommitted events."""
        changes = self._changes[:]
        self._changes.clear()
        return changes
```

**Điểm mấu chốt:**

- `_version` — số events đã apply.
- `_changes` — events chưa commit.
- `from_history` — reconstruct từ events.
- `_apply` — dispatch tới `_on_EventName`.
- `_raise` — apply + track.

### 4.2. Ví dụ: BankAccount

```python
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from shop.domain.events.base import DomainEvent
from shop.shared.domain.money import Money


# ---- Events ----
@dataclass(frozen=True)
class AccountOpened(DomainEvent):
    account_id: UUID = field(default=None)   # type: ignore
    owner_name: str = ""


@dataclass(frozen=True)
class MoneyDeposited(DomainEvent):
    account_id: UUID = field(default=None)   # type: ignore
    amount: Money = field(default=None)   # type: ignore


@dataclass(frozen=True)
class MoneyWithdrawn(DomainEvent):
    account_id: UUID = field(default=None)   # type: ignore
    amount: Money = field(default=None)   # type: ignore


@dataclass(frozen=True)
class AccountFrozen(DomainEvent):
    account_id: UUID = field(default=None)   # type: ignore
    reason: str = ""


# ---- Aggregate ----
class BankAccount(EventSourcedAggregate):
    """Event-Sourced Aggregate."""

    @classmethod
    def open(cls, owner_name: str) -> "BankAccount":
        if not owner_name.strip():
            raise ValueError("Tên không được rỗng")
        account_id = uuid4()
        account = cls(account_id)
        account._raise(AccountOpened(
            account_id=account_id,
            owner_name=owner_name.strip(),
        ))
        return account

    @property
    def owner_name(self) -> str:
        return self._owner_name

    @property
    def balance(self) -> Money:
        return self._balance

    @property
    def is_frozen(self) -> bool:
        return self._frozen

    def deposit(self, amount: Money) -> None:
        self._ensure_not_frozen()
        if amount.amount <= 0:
            raise ValueError("Số tiền phải > 0")
        self._raise(MoneyDeposited(
            account_id=self._id,
            amount=amount,
        ))

    def withdraw(self, amount: Money) -> None:
        self._ensure_not_frozen()
        if amount.amount <= 0:
            raise ValueError("Số tiền phải > 0")
        if amount.amount > self._balance.amount:
            raise InsufficientFunds()
        self._raise(MoneyWithdrawn(
            account_id=self._id,
            amount=amount,
        ))

    def freeze(self, reason: str) -> None:
        if self._frozen:
            raise AlreadyFrozen()
        self._raise(AccountFrozen(
            account_id=self._id,
            reason=reason,
        ))

    # ---- Event handlers ----
    def _on_AccountOpened(self, event: AccountOpened) -> None:
        self._owner_name = event.owner_name
        self._balance = Money(Decimal("0"), "VND")
        self._frozen = False

    def _on_MoneyDeposited(self, event: MoneyDeposited) -> None:
        self._balance = self._balance + event.amount

    def _on_MoneyWithdrawn(self, event: MoneyWithdrawn) -> None:
        self._balance = self._balance - event.amount

    def _on_AccountFrozen(self, event: AccountFrozen) -> None:
        self._frozen = True

    # ---- Guards ----
    def _ensure_not_frozen(self) -> None:
        if self._frozen:
            raise AccountFrozenError()
```

**Điểm mấu chốt:**

- Constructor **không** set state trực tiếp.
- `_on_EventName` set state.
- Business method gọi `_raise(event)`.
- Tất cả state được set qua events.

### 4.3. Sử dụng

```python
# Mở tài khoản
account = BankAccount.open("Nguyễn Văn An")
account.deposit(Money(Decimal("1000000"), "VND"))
account.deposit(Money(Decimal("500000"), "VND"))
account.withdraw(Money(Decimal("300000"), "VND"))

# State hiện tại
assert account.balance == Money(Decimal("1200000"), "VND")
assert account.version == 4   # 4 events

# Uncommitted events
events = account.pull_changes()
assert len(events) == 4
# [AccountOpened, MoneyDeposited, MoneyDeposited, MoneyWithdrawn]

# Save vào event store
event_store.append(account.id, events, expected_version=0)

# Load lại
loaded_events = event_store.load(account.id)
loaded = BankAccount.from_history(account.id, loaded_events)

assert loaded.balance == account.balance
assert loaded.version == account.version
```

### 4.4. Repository cho Event-Sourced Aggregate

```python
class EventSourcedBankAccountRepository:
    def __init__(self, event_store: EventStore) -> None:
        self._event_store = event_store

    def find_by_id(self, account_id: UUID) -> BankAccount | None:
        events = self._event_store.load(account_id)
        if not events:
            return None
        return BankAccount.from_history(account_id, events)

    def save(self, account: BankAccount) -> None:
        changes = account.pull_changes()
        if not changes:
            return
        self._event_store.append(
            aggregate_id=account.id,
            events=changes,
            expected_version=account.version - len(changes),
        )
```

**Chú ý:**

- `expected_version = account.version - len(changes)`.
- Vì `account.version` đã tăng sau mỗi `_raise`.

---

## 5. Replay và Snapshot

### 5.1. Replay là gì?

> **Replay** = apply lại toàn bộ events để reconstruct state.

```python
# Replay 1000 events
events = event_store.load(account_id)   # 1000 events
account = BankAccount.from_history(account_id, events)
```

**Vấn đề:** Nếu aggregate có 10,000 events → replay chậm.

### 5.2. Snapshot

> **Snapshot** = lưu state hiện tại của Aggregate tại một version, để không cần replay từ đầu.

**Ví dụ:**

```
Version 0: AccountOpened
Version 1: MoneyDeposited
Version 2: MoneyDeposited
...
Version 1000: MoneyWithdrawn
[SNAPSHOT at version 1000: balance = X]
Version 1001: MoneyDeposited
Version 1002: MoneyWithdrawn
```

Khi load:

1. Load snapshot tại version 1000.
2. Load events từ 1001.
3. Apply snapshot + events.

**Không cần replay 1000 events đầu.**

### 5.3. Implementation snapshot

```python
@dataclass(frozen=True)
class Snapshot:
    aggregate_id: UUID
    version: int
    state: dict   # serialized state
    created_at: datetime


class SnapshotStore:
    def save(self, aggregate_id: UUID, version: int, state: dict) -> None:
        ...

    def load_latest(self, aggregate_id: UUID) -> Snapshot | None:
        ...


class BankAccount(EventSourcedAggregate):
    def to_snapshot(self) -> dict:
        return {
            "owner_name": self._owner_name,
            "balance_amount": str(self._balance.amount),
            "balance_currency": self._balance.currency,
            "frozen": self._frozen,
        }

    @classmethod
    def from_snapshot(
        cls,
        aggregate_id: UUID,
        version: int,
        state: dict,
    ) -> "BankAccount":
        account = cls.__new__(cls)
        account._id = aggregate_id
        account._version = version
        account._changes = []
        account._owner_name = state["owner_name"]
        account._balance = Money(
            Decimal(state["balance_amount"]),
            state["balance_currency"],
        )
        account._frozen = state["frozen"]
        return account
```

### 5.4. Khi nào snapshot?

| Số events | Snapshot? |
|---|---|
| < 100 | Không |
| 100-1000 | Cân nhắc |
| > 1000 | Có |
| > 10,000 | Bắt buộc |

**Tần suất:** Mỗi 100-500 events.

### 5.5. Repository với snapshot

```python
class EventSourcedBankAccountRepository:
    def __init__(
        self,
        event_store: EventStore,
        snapshot_store: SnapshotStore,
        snapshot_every: int = 100,
    ) -> None:
        self._event_store = event_store
        self._snapshot_store = snapshot_store
        self._snapshot_every = snapshot_every

    def find_by_id(self, account_id: UUID) -> BankAccount | None:
        # 1. Load snapshot
        snapshot = self._snapshot_store.load_latest(account_id)

        if snapshot:
            account = BankAccount.from_snapshot(
                account_id, snapshot.version, snapshot.state
            )
            events = self._event_store.load_from_version(
                account_id, snapshot.version
            )
        else:
            events = self._event_store.load(account_id)
            if not events:
                return None
            account = BankAccount.from_history(account_id, events)
            return account

        # 2. Apply events từ snapshot
        for event in events:
            account._apply(event)
            account._version += 1

        return account

    def save(self, account: BankAccount) -> None:
        changes = account.pull_changes()
        if not changes:
            return

        expected_version = account.version - len(changes)
        self._event_store.append(account.id, changes, expected_version)

        # Snapshot nếu cần
        if account.version % self._snapshot_every == 0:
            self._snapshot_store.save(
                account.id,
                account.version,
                account.to_snapshot(),
            )
```

---

## 6. Projection — Build read model từ events

### 6.1. Vấn đề

Event Sourcing **không phù hợp cho query**. Muốn query "tất cả account có balance > 1 triệu" → phải replay **mọi account** → chậm.

**Giải pháp:** **Projection** — build read model từ events.

### 6.2. Projection là gì?

> **Projection** là một **event handler** đọc events và update **read model** (bảng denormalized).

### 6.3. Ví dụ: Account Summary Projection

```python
class AccountSummaryProjection:
    """
    Đọc events và update read model 'account_summary'.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def on_account_opened(self, event: AccountOpened) -> None:
        self._session.execute(
            text("""
                INSERT INTO account_summary
                (account_id, owner_name, balance, is_frozen, created_at)
                VALUES (:aid, :owner, 0, FALSE, :at)
            """),
            {
                "aid": str(event.account_id),
                "owner": event.owner_name,
                "at": event.occurred_at,
            },
        )

    def on_money_deposited(self, event: MoneyDeposited) -> None:
        self._session.execute(
            text("""
                UPDATE account_summary
                SET balance = balance + :amount
                WHERE account_id = :aid
            """),
            {
                "aid": str(event.account_id),
                "amount": str(event.amount.amount),
            },
        )

    def on_money_withdrawn(self, event: MoneyWithdrawn) -> None:
        self._session.execute(
            text("""
                UPDATE account_summary
                SET balance = balance - :amount
                WHERE account_id = :aid
            """),
            {
                "aid": str(event.account_id),
                "amount": str(event.amount.amount),
            },
        )

    def on_account_frozen(self, event: AccountFrozen) -> None:
        self._session.execute(
            text("""
                UPDATE account_summary
                SET is_frozen = TRUE
                WHERE account_id = :aid
            """),
            {"aid": str(event.account_id)},
        )
```

### 6.4. Query read model

```python
class AccountSummaryQuery:
    def __init__(self, session: Session) -> None:
        self._session = session

    def by_owner(self, owner_name: str) -> list[AccountSummaryDTO]:
        rows = self._session.execute(
            text("""
                SELECT account_id, owner_name, balance, is_frozen
                FROM account_summary
                WHERE owner_name = :owner
            """),
            {"owner": owner_name},
        ).fetchall()
        return [AccountSummaryDTO(...) for row in rows]

    def rich_accounts(self, min_balance: Decimal) -> list[AccountSummaryDTO]:
        rows = self._session.execute(
            text("""
                SELECT account_id, owner_name, balance, is_frozen
                FROM account_summary
                WHERE balance >= :min
            """),
            {"min": str(min_balance)},
        ).fetchall()
        return [AccountSummaryDTO(...) for row in rows]
```

### 6.5. Rebuild projection

**Lợi ích lớn nhất của Event Sourcing:**

> Bạn có thể **rebuild read model bất kỳ lúc nào** bằng cách replay toàn bộ events.

```python
def rebuild_account_summary(event_store: EventStore, session: Session) -> None:
    # 1. Xóa read model hiện tại
    session.execute(text("DELETE FROM account_summary"))

    # 2. Replay tất cả events
    projection = AccountSummaryProjection(session)
    all_events = event_store.load_all()   # cần method mới

    for event in all_events:
        handler = getattr(
            projection,
            f"on_{snake_case(type(event).__name__)}",
            None,
        )
        if handler:
            handler(event)

    session.commit()
```

**Điều kỳ diệu:** Thêm read model mới? Chỉ cần replay. Đổi schema read model? Replay lại.

---

## 7. Versioning events

Đây là **vấn đề khó** của Event Sourcing. Events **đã lưu** không được sửa.

### 7.1. Vấn đề

Event `MoneyDeposited` phiên bản 1:

```python
@dataclass(frozen=True)
class MoneyDeposited(DomainEvent):
    account_id: UUID
    amount: Money
```

Sau 6 tháng, business cần thêm field `description`:

```python
@dataclass(frozen=True)
class MoneyDeposited(DomainEvent):
    account_id: UUID
    amount: Money
    description: str = ""   # ← Field mới
```

**Vấn đề:** Events cũ **không có** `description`.

### 7.2. Giải pháp

**1. Default value**

```python
@dataclass(frozen=True)
class MoneyDeposited(DomainEvent):
    account_id: UUID = None   # type: ignore
    amount: Money = None   # type: ignore
    description: str = ""   # ← Default
```

**Đơn giản nhất.** Dùng khi field optional.

**2. Event versioning**

```python
@dataclass(frozen=True)
class MoneyDepositedV1(DomainEvent):
    account_id: UUID
    amount: Money

@dataclass(frozen=True)
class MoneyDepositedV2(DomainEvent):
    account_id: UUID
    amount: Money
    description: str
```

Handler phải handle cả 2:

```python
def _on_MoneyDepositedV1(self, event):
    self._balance = self._balance + event.amount

def _on_MoneyDepositedV2(self, event):
    self._balance = self._balance + event.amount
    self._descriptions.append(event.description)
```

**3. Upcasters**

Chuyển event cũ → event mới khi load:

```python
class EventUpcaster:
    def upcast(self, event: DomainEvent) -> DomainEvent:
        if isinstance(event, MoneyDepositedV1):
            return MoneyDepositedV2(
                event_id=event.event_id,
                occurred_at=event.occurred_at,
                account_id=event.account_id,
                amount=event.amount,
                description="",
            )
        return event
```

**4. Weak schema**

Không dùng dataclass, dùng dict:

```python
def _on_MoneyDeposited(self, event: dict) -> None:
    self._balance = self._balance + event["amount"]
    self._description = event.get("description", "")
```

**Nhược điểm:** Mất type safety.

### 7.3. Quy tắc

> **Thêm field optional** → OK với default value.
>
> **Đổi field** → cần versioning + upcaster.
>
> **Xóa field** → giữ để tương thích ngược.
>
> **Không bao giờ** sửa ý nghĩa của event cũ.

---

## 8. Tám anti-pattern khi dùng Event Sourcing

### ❌ Anti-pattern 1: Dùng Event Sourcing cho CRUD

```python
# ❌ SAI: Todo list dùng Event Sourcing
@dataclass(frozen=True)
class TodoCreated(DomainEvent): ...
@dataclass(frozen=True)
class TodoTitleChanged(DomainEvent): ...
@dataclass(frozen=True)
class TodoCompleted(DomainEvent): ...
```

**Fix:** CRUD dùng DB bình thường.

### ❌ Anti-pattern 2: Event store = message queue

```python
# ❌ SAI: Dùng event store như Kafka
event_store.append(...)   # Event đi qua message queue
```

**Fix:** Event store là **source of truth**. Message queue là **integration**. Tách 2 cái.

### ❌ Anti-pattern 3: Sửa events

```python
# ❌ SAI: Update event
UPDATE events SET payload = ... WHERE id = ...   # Không bao giờ!
```

**Fix:** Events **immutable**. Muốn correct → thêm compensation event.

### ❌ Anti-pattern 4: Query trực tiếp event store

```python
# ❌ SAI: Query event store
SELECT * FROM events WHERE payload->>'amount' > '1000000'
```

**Fix:** Query read model (projection).

### ❌ Anti-pattern 5: Không có snapshot

```python
# ❌ SAI: Aggregate có 1 triệu events
events = event_store.load(account_id)   # Load cả triệu events
```

**Fix:** Snapshot mỗi 100-500 events.

### ❌ Anti-pattern 6: Event chứa Entity

```python
# ❌ SAI
@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    order: Order   # Object thật → không serialize được
```

**Fix:** Event chứa primitive data.

```python
# ✅ ĐÚNG
@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    order_id: UUID = None   # type: ignore
    total_amount: str = ""
    line_count: int = 0
```

### ❌ Anti-pattern 7: Không handle versioning

```python
# ❌ SAI: Không có strategy cho versioning
@dataclass(frozen=True)
class MoneyDeposited(DomainEvent):
    account_id: UUID
    amount: Money
    # Thêm field mà không có default
```

**Fix:** Luôn thêm field với default.

### ❌ Anti-pattern 8: Event Sourcing cho mọi aggregate

```python
# ❌ SAI: Mọi aggregate đều Event-Sourced
class Customer(EventSourcedAggregate): ...
class Product(EventSourcedAggregate): ...
class Category(EventSourcedAggregate): ...
```

**Fix:** Chỉ Event-Sourced
còn nữa.....