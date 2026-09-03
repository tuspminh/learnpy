# Python OOP Master — Buổi 39

# Project 1 — Library Management System

Hôm nay chúng ta bắt đầu **project tổng hợp Design Pattern + SOLID + Repository + DI**.

Mục tiêu không phải chỉ làm một app quản lý thư viện, mà là học cách **ghép các kiến thức OOP thành một kiến trúc thực tế**.

---

# 1. Mục tiêu Buổi 39

Sau buổi này bạn sẽ xây được phiên bản đầu tiên:

```text
Library Management System

Book
Member
Loan
   │
   ↓
Service
   │
   ↓
Repository
   │
   ↓
SQLite
```

Và bắt đầu tích hợp:

| Kiến thức            | Vai trò             |
| -------------------- | ------------------- |
| OOP                  | Entity              |
| Encapsulation        | Bảo vệ state        |
| SOLID                | Thiết kế            |
| Repository           | Persistence         |
| Dependency Injection | Inject repository   |
| Factory              | Tạo infrastructure  |
| Builder              | Xây object phức tạp |
| Strategy             | Tính tiền phạt      |
| Command              | Đóng gói action     |
| Observer             | Event               |
| SQLite               | Persistence         |

Nhưng **không dùng tất cả ngay từ đầu**.

Đây là nguyên tắc rất quan trọng:

> Không phải project nào cũng cần tất cả Design Pattern.

Chúng ta sẽ xây từ đơn giản → nâng cấp.

---

# 2. Bài toán

Thư viện có:

### Book

```text
id
title
author
status
```

### Member

```text
id
name
email
```

### Loan

```text
id
book_id
member_id
borrowed_at
returned_at
```

Quy tắc:

```text
Book AVAILABLE
       ↓
    borrow
       ↓
Book BORROWED
```

Khi trả:

```text
Book BORROWED
       ↓
    return
       ↓
Book AVAILABLE
```

---

# 3. Kiến trúc

Phiên bản đầu:

```text
library/
│
├── domain/
│   ├── entities/
│   │   ├── book.py
│   │   ├── member.py
│   │   └── loan.py
│   │
│   └── repositories/
│       ├── book_repository.py
│       ├── member_repository.py
│       └── loan_repository.py
│
├── application/
│   └── services/
│       └── library_service.py
│
├── infrastructure/
│   ├── database.py
│   └── repositories/
│       ├── sqlite_book_repository.py
│       ├── sqlite_member_repository.py
│       └── sqlite_loan_repository.py
│
└── main.py
```

Dependency:

```text
main
 │
 ↓
LibraryService
 │
 ↓
Repository Interface
 │
 ↓
SQLite Repository
 │
 ↓
Database
```

Điểm quan trọng:

```text
Domain
   X
   │
   └── không biết SQLite
```

---

# 4. Domain Entity — Book

Tạo:

```text
domain/entities/book.py
```

```python
from dataclasses import dataclass
from enum import Enum


class BookStatus(Enum):
    AVAILABLE = "available"
    BORROWED = "borrowed"


@dataclass
class Book:
    id: int | None
    title: str
    author: str
    status: BookStatus = BookStatus.AVAILABLE

    def borrow(self) -> None:
        if self.status == BookStatus.BORROWED:
            raise ValueError("Book is already borrowed")

        self.status = BookStatus.BORROWED

    def return_book(self) -> None:
        if self.status == BookStatus.AVAILABLE:
            raise ValueError("Book is not borrowed")

        self.status = BookStatus.AVAILABLE
```

Đây là điểm rất quan trọng.

Không viết:

```python
book.status = BookStatus.BORROWED
```

khắp application.

Thay vào đó:

```python
book.borrow()
```

Business rule nằm trong Entity.

---

# 5. Member

`domain/entities/member.py`

```python
from dataclasses import dataclass


@dataclass
class Member:
    id: int | None
    name: str
    email: str
```

Sau này có thể thêm:

```python
def can_borrow(self, active_loans: int) -> bool:
    return active_loans < 5
```

Nhưng hiện tại giữ Entity đơn giản.

---

# 6. Loan

`domain/entities/loan.py`

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Loan:
    id: int | None
    book_id: int
    member_id: int
    borrowed_at: datetime
    returned_at: datetime | None = None

    @property
    def is_active(self) -> bool:
        return self.returned_at is None

    def return_book(self, returned_at: datetime) -> None:
        if not self.is_active:
            raise ValueError("Loan has already been returned")

        self.returned_at = returned_at
```

Ta có:

```python
loan.is_active
```

thay vì:

```python
loan.returned_at is None
```

ở khắp nơi.

---

# 7. Repository Interface

Đây là phần chúng ta vừa học ở Buổi 38.

## BookRepository

`domain/repositories/book_repository.py`

```python
from abc import ABC, abstractmethod

from domain.entities.book import Book


class BookRepository(ABC):

    @abstractmethod
    def get_by_id(self, book_id: int) -> Book | None:
        pass

    @abstractmethod
    def save(self, book: Book) -> None:
        pass

    @abstractmethod
    def delete(self, book_id: int) -> None:
        pass

    @abstractmethod
    def list_all(self) -> list[Book]:
        pass
```

---

# 8. MemberRepository

```python
from abc import ABC, abstractmethod

from domain.entities.member import Member


class MemberRepository(ABC):

    @abstractmethod
    def get_by_id(self, member_id: int) -> Member | None:
        pass

    @abstractmethod
    def save(self, member: Member) -> None:
        pass

    @abstractmethod
    def list_all(self) -> list[Member]:
        pass
```

---

# 9. LoanRepository

```python
from abc import ABC, abstractmethod

from domain.entities.loan import Loan


class LoanRepository(ABC):

    @abstractmethod
    def get_by_id(self, loan_id: int) -> Loan | None:
        pass

    @abstractmethod
    def get_active_loan(
        self,
        book_id: int,
    ) -> Loan | None:
        pass

    @abstractmethod
    def save(self, loan: Loan) -> None:
        pass
```

---

# 10. Tại sao Repository Interface nằm trong Domain?

Đây là kiến thức kiến trúc quan trọng.

Ta muốn:

```text
LibraryService
      ↓
BookRepository
```

chứ không muốn:

```text
LibraryService
      ↓
SQLiteBookRepository
```

Application chỉ biết:

```python
repository.get_by_id(...)
repository.save(...)
```

Không cần biết:

```python
sqlite3.connect(...)
cursor.execute(...)
```

---

# 11. Database

Tạo:

```text
infrastructure/database.py
```

```python
import sqlite3


class Database:
    def __init__(self, path: str):
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row

    def create_tables(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                status TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                member_id INTEGER NOT NULL,
                borrowed_at TEXT NOT NULL,
                returned_at TEXT
            );
            """
        )

        self.connection.commit()

    def close(self) -> None:
        self.connection.close()
```

---

# 12. SQLiteBookRepository

```python
from domain.entities.book import Book, BookStatus
from domain.repositories.book_repository import BookRepository


class SQLiteBookRepository(BookRepository):

    def __init__(self, connection):
        self.connection = connection

    def get_by_id(self, book_id: int) -> Book | None:
        row = self.connection.execute(
            """
            SELECT id, title, author, status
            FROM books
            WHERE id = ?
            """,
            (book_id,),
        ).fetchone()

        if row is None:
            return None

        return Book(
            id=row["id"],
            title=row["title"],
            author=row["author"],
            status=BookStatus(row["status"]),
        )

    def save(self, book: Book) -> None:
        if book.id is None:
            cursor = self.connection.execute(
                """
                INSERT INTO books(title, author, status)
                VALUES (?, ?, ?)
                """,
                (
                    book.title,
                    book.author,
                    book.status.value,
                ),
            )

            book.id = cursor.lastrowid

        else:
            self.connection.execute(
                """
                UPDATE books
                SET title = ?,
                    author = ?,
                    status = ?
                WHERE id = ?
                """,
                (
                    book.title,
                    book.author,
                    book.status.value,
                    book.id,
                ),
            )

        self.connection.commit()

    def delete(self, book_id: int) -> None:
        self.connection.execute(
            "DELETE FROM books WHERE id = ?",
            (book_id,),
        )

        self.connection.commit()

    def list_all(self) -> list[Book]:
        rows = self.connection.execute(
            """
            SELECT id, title, author, status
            FROM books
            ORDER BY id
            """
        ).fetchall()

        return [
            Book(
                id=row["id"],
                title=row["title"],
                author=row["author"],
                status=BookStatus(row["status"]),
            )
            for row in rows
        ]
```

Chú ý:

```text
SQLite Row
    ↓
Book
```

Repository làm nhiệm vụ mapping.

---

# 13. LibraryService

Bây giờ đến Application Layer.

```text
application/services/library_service.py
```

```python
from datetime import datetime

from domain.entities.book import Book
from domain.entities.member import Member
from domain.entities.loan import Loan

from domain.repositories.book_repository import BookRepository
from domain.repositories.member_repository import MemberRepository
from domain.repositories.loan_repository import LoanRepository


class LibraryService:

    def __init__(
        self,
        book_repository: BookRepository,
        member_repository: MemberRepository,
        loan_repository: LoanRepository,
    ):
        self.book_repository = book_repository
        self.member_repository = member_repository
        self.loan_repository = loan_repository

    def add_book(
        self,
        title: str,
        author: str,
    ) -> Book:

        book = Book(
            id=None,
            title=title,
            author=author,
        )

        self.book_repository.save(book)

        return book

    def register_member(
        self,
        name: str,
        email: str,
    ) -> Member:

        member = Member(
            id=None,
            name=name,
            email=email,
        )

        self.member_repository.save(member)

        return member
```

Đây chính là:

# Dependency Injection

Service không tự tạo:

```python
SQLiteBookRepository(...)
```

Mà nhận dependency từ bên ngoài:

```python
LibraryService(
    book_repository,
    member_repository,
    loan_repository,
)
```

---

# 14. Borrow Book

Thêm method:

```python
def borrow_book(
    self,
    book_id: int,
    member_id: int,
) -> Loan:

    book = self.book_repository.get_by_id(book_id)

    if book is None:
        raise ValueError("Book not found")

    member = self.member_repository.get_by_id(member_id)

    if member is None:
        raise ValueError("Member not found")

    active_loan = self.loan_repository.get_active_loan(book_id)

    if active_loan is not None:
        raise ValueError("Book is already borrowed")

    book.borrow()

    loan = Loan(
        id=None,
        book_id=book_id,
        member_id=member_id,
        borrowed_at=datetime.now(),
    )

    self.book_repository.save(book)
    self.loan_repository.save(loan)

    return loan
```

Workflow:

```text
borrow_book()
     │
     ├── get Book
     │
     ├── get Member
     │
     ├── check existing Loan
     │
     ├── book.borrow()
     │
     ├── save Book
     │
     └── save Loan
```

Đây là **Use Case**.

---

# 15. Return Book

```python
def return_book(self, book_id: int) -> None:

    book = self.book_repository.get_by_id(book_id)

    if book is None:
        raise ValueError("Book not found")

    loan = self.loan_repository.get_active_loan(book_id)

    if loan is None:
        raise ValueError("No active loan")

    book.return_book()

    loan.return_book(datetime.now())

    self.book_repository.save(book)
    self.loan_repository.save(loan)
```

Ta có:

```text
Return Book
    │
    ├── Book.return_book()
    │
    ├── Loan.return_book()
    │
    ├── save Book
    │
    └── save Loan
```

---

# 16. Composition Root

Đây là nơi rất quan trọng.

`main.py`

```python
from infrastructure.database import Database
from infrastructure.repositories.sqlite_book_repository import (
    SQLiteBookRepository,
)

from application.services.library_service import LibraryService


def main():
    database = Database("library.db")

    database.create_tables()

    book_repository = SQLiteBookRepository(
        database.connection
    )

    # member_repository
    # loan_repository

    service = LibraryService(
        book_repository=book_repository,
        member_repository=member_repository,
        loan_repository=loan_repository,
    )

    book = service.add_book(
        title="Clean Code",
        author="Robert C. Martin",
    )

    print(book)

    database.close()


if __name__ == "__main__":
    main()
```

Đây là:

```text
Composition Root
       │
       ├── tạo Database
       │
       ├── tạo Repository
       │
       ├── tạo Service
       │
       └── kết nối Dependency
```

Application không biết dependency được tạo ở đâu.

---

# 17. Tại sao kiến trúc này tốt?

So sánh.

## Cách xấu

```python
class LibraryService:

    def borrow_book(self, book_id, member_id):

        connection = sqlite3.connect("library.db")

        row = connection.execute(
            "SELECT ..."
        ).fetchone()

        ...
```

Service phụ thuộc:

```text
SQLite
SQL
Database
Schema
```

---

## Cách tốt

```python
class LibraryService:

    def __init__(
        self,
        book_repository,
        member_repository,
        loan_repository,
    ):
        ...
```

Service chỉ biết:

```text
BookRepository
MemberRepository
LoanRepository
```

Kiến trúc:

```text
            ┌───────────────┐
            │ LibraryService│
            └───────┬───────┘
                    │
          ┌─────────┼─────────┐
          ↓         ↓         ↓
        Book      Member     Loan
        Repo       Repo      Repo
          │         │         │
          └─────────┼─────────┘
                    ↓
                  SQLite
```

---

# 18. Bắt đầu tích hợp Strategy

Thư viện có thể tính tiền phạt.

Ví dụ:

```text
Quá hạn 5 ngày

Fixed:
50.000đ

Per Day:
5 × 10.000 = 50.000đ
```

Ta có:

```text
FineStrategy
    ├── NoFine
    ├── FixedFine
    └── PerDayFine
```

Interface:

```python
from abc import ABC, abstractmethod


class FineStrategy(ABC):

    @abstractmethod
    def calculate(self, overdue_days: int) -> int:
        pass
```

Implementation:

```python
class NoFineStrategy(FineStrategy):

    def calculate(self, overdue_days: int) -> int:
        return 0
```

```python
class PerDayFineStrategy(FineStrategy):

    def __init__(self, amount_per_day: int):
        self.amount_per_day = amount_per_day

    def calculate(self, overdue_days: int) -> int:
        return overdue_days * self.amount_per_day
```

Service:

```python
class FineService:

    def __init__(self, strategy: FineStrategy):
        self.strategy = strategy

    def calculate(self, overdue_days: int) -> int:
        return self.strategy.calculate(overdue_days)
```

DI:

```python
fine_service = FineService(
    strategy=PerDayFineStrategy(10_000)
)
```

Đây chính là:

```text
Strategy
    +
Dependency Injection
```

---

# 19. Test mà không cần SQLite

Đây là lợi ích cực lớn của Repository.

Ta tạo:

```python
class MemoryBookRepository:

    def __init__(self):
        self.books = {}

    def get_by_id(self, book_id):
        return self.books.get(book_id)

    def save(self, book):
        if book.id is None:
            book.id = len(self.books) + 1

        self.books[book.id] = book

    def delete(self, book_id):
        self.books.pop(book_id, None)

    def list_all(self):
        return list(self.books.values())
```

Sau đó:

```python
repository = MemoryBookRepository()

service = LibraryService(
    book_repository=repository,
    member_repository=member_repository,
    loan_repository=loan_repository,
)
```

Không cần:

```text
SQLite
database file
SQL
```

Unit test có thể chạy cực nhanh.

---

# 20. Pattern nào đang được sử dụng?

Trong phiên bản hiện tại:

```text
                LibraryService
                     │
                Dependency
                Injection
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
   Repository    Repository    Repository
        │
        ↓
      SQLite
```

Đã có:

### Repository

```text
Persistence abstraction
```

### Dependency Injection

```text
Dependencies được inject
```

### Strategy

```text
Fine calculation algorithm
```

### Entity

```text
Book
Member
Loan
```

---

# 21. Pattern nào sẽ thêm ở phần tiếp theo?

Chúng ta sẽ tiếp tục nâng cấp project.

```text
                  Library
                    │
       ┌────────────┼────────────┐
       ↓            ↓            ↓
     Entity     Repository     Service
                                  │
               ┌──────────────────┼────────────────┐
               ↓                  ↓                ↓
            Strategy           Command          Observer
               │                  │                │
             Fine             Borrow/Return      Events
```

Sau đó:

```text
Factory
   ↓
Infrastructure creation
```

và:

```text
Builder
   ↓
Complex object creation
```

---

# 22. Điều quan trọng nhất của Buổi 39

Đừng học Design Pattern theo kiểu:

```text
"Hôm nay phải nhét Factory vào."
"Hôm nay phải nhét Builder vào."
```

Hãy bắt đầu từ **problem**.

Ví dụ:

### Problem

Cần lưu Book.

→ Repository.

### Problem

Muốn thay SQLite bằng Memory Repository.

→ Dependency Injection.

### Problem

Có nhiều cách tính tiền phạt.

→ Strategy.

### Problem

UI, CLI, shortcut đều phải thực hiện `borrow`.

→ Command.

### Problem

Dashboard cần biết khi có người mượn sách.

→ Observer.

### Problem

Có nhiều implementation cần tạo theo configuration.

→ Factory.

Đó mới là cách tư duy Design Pattern chuyên nghiệp.

---

# 23. Bài tập Buổi 39

### Bài 1 — Entity

Tạo:

```text
Book
Member
Loan
```

và implement:

```python
book.borrow()
book.return_book()

loan.return_book()
```

---

### Bài 2 — Repository

Tạo:

```text
MemoryBookRepository
MemoryMemberRepository
MemoryLoanRepository
```

Không dùng SQLite.

---

### Bài 3 — LibraryService

Implement:

```python
add_book()

register_member()

borrow_book()

return_book()
```

---

### Bài 4 — Business Rules

Bổ sung:

```text
Một member tối đa 5 quyển đang mượn.
```

Nếu vượt:

```python
raise ValueError("Member has reached borrowing limit")
```

---

### Bài 5 — Strategy

Implement:

```text
NoFineStrategy
FixedFineStrategy
PerDayFineStrategy
```

---

# 24. Bài tập nâng cao ⭐

Thiết kế:

```text
LibraryService
       │
       ├── BookRepository
       ├── MemberRepository
       ├── LoanRepository
       └── FineStrategy
```

Sau đó viết:

```python
service = LibraryService(
    book_repository=...,
    member_repository=...,
    loan_repository=...,
    fine_strategy=...,
)
```

Mục tiêu:

> `LibraryService` không được import `sqlite3`.

Và:

> `LibraryService` không được biết `SQLiteBookRepository` tồn tại.

Nếu làm được điều này, bạn đã thực sự hiểu **DIP + DI + Repository** chứ không chỉ học thuộc Pattern.

---

# 25. Kiến trúc chúng ta đang hướng tới

Cuối project:

```text
                       ┌──────────────┐
                       │     CLI      │
                       └──────┬───────┘
                              │
                       ┌──────▼───────┐
                       │   Command    │
                       └──────┬───────┘
                              │
                       ┌──────▼───────┐
                       │    Service   │
                       └──────┬───────┘
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
       Repository          Strategy         Observer
             │
             ▼
        SQLite/Memory
```

Đây chính là kiểu kiến trúc mà sau này bạn có thể áp dụng trực tiếp vào **Story Crawler/Reader**:

```text
PySide6 / CLI
      ↓
Command
      ↓
Application Service
      ↓
Repository
      ↓
SQLite
```

và:

```text
Crawler
  ↓
Strategy
  ↓
Retry / Backoff
```

```text
Crawler
  ↓
Observer
  ↓
Dashboard / Logger / Metrics
```

**Buổi 40** sẽ nâng cấp project này thành một hệ thống hoàn chỉnh hơn: **SQLite + Factory + Builder + Strategy + Command + Observer + Repository + DI + Testing**, sau đó chúng ta chuyển sang **Sales Management System** để thấy các Pattern này có thể tái sử dụng như thế nào.
