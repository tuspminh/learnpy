Được. Với SOLID, tôi sẽ không dạy theo kiểu “5 chữ cái = 5 định nghĩa”, mà đi theo hướng **thiết kế phần mềm Python thực tế**, đặc biệt phù hợp với những gì bạn đang học như **OOP, DDD, Clean Architecture, Repository, CLI, crawler/worker**.

# SOLID Deep Dive — Python

## 1. Mục tiêu khóa học

Sau khóa này bạn sẽ hiểu:

* SOLID thực sự giải quyết **vấn đề gì**
* Khi nào một class đang có **quá nhiều trách nhiệm**
* Khi nào inheritance trở thành vấn đề
* Vì sao abstraction/interface tồn tại
* Dependency Injection thực chất là gì
* Cách thiết kế code để:

  * dễ test
  * dễ thay đổi
  * dễ mở rộng
  * ít coupling
  * ít regression
* Phân biệt **SOLID thật** với việc áp dụng SOLID máy móc
* SOLID kết hợp với:

  * OOP
  * Design Pattern
  * DDD
  * Clean Architecture
  * Repository Pattern
  * Dependency Injection
  * Plugin Architecture

---

# Roadmap

## Phần I — Foundation

### Buổi 1 — SOLID là gì?

* SOLID ra đời để giải quyết vấn đề gì?
* Coupling
* Cohesion
* Changeability
* Maintainability
* Code smell
* Vì sao code chạy đúng vẫn có thể là code xấu
* SOLID không phải là 5 quy tắc cứng nhắc
* SOLID và OOP

### Buổi 2 — SRP cơ bản

**Single Responsibility Principle**

* Responsibility là gì?
* “Một class chỉ có một responsibility” có chính xác không?
* Actor
* Reason to change
* Cohesion
* Separation of concerns

### Buổi 3 — SRP Deep Dive

* God Object
* God Service
* God Manager
* Fat Model
* Fat Controller
* Tách class
* Tách module
* Tách package
* Khi nào **không nên tách**
* SRP trong Python

### Buổi 4 — OCP

**Open/Closed Principle**

* Open for extension
* Closed for modification
* Tại sao `if/elif` có thể là code smell?
* Polymorphism
* Strategy Pattern
* Registry Pattern
* Plugin Architecture

### Buổi 5 — OCP Deep Dive

* Abstract Base Class
* Protocol
* Duck Typing
* Dependency Injection
* Runtime extension
* Plugin system
* OCP trong crawler architecture

---

# Phần II — LSP

### Buổi 6 — Liskov Substitution Principle

* Subtype
* Behavioral subtyping
* “Is-a” chưa đủ
* Contract
* Precondition
* Postcondition
* Invariant

### Buổi 7 — LSP Deep Dive

* Những inheritance hierarchy sai
* Rectangle/Square problem
* Exception violation
* Return type violation
* Mutable state
* `NotImplementedError` và LSP
* Khi nào composition tốt hơn inheritance

---

# Phần III — ISP

### Buổi 8 — Interface Segregation Principle

* Interface là gì trong Python?
* Fat interface
* Client
* Interface pollution
* ABC
* Protocol
* Duck typing

### Buổi 9 — ISP Deep Dive

Ví dụ:

```text
Crawler
 ├── crawl()
 ├── parse()
 ├── download()
 ├── login()
 ├── upload()
 └── notify()
```

→ tại sao đây có thể là một thiết kế tệ?

Thiết kế lại thành các abstraction nhỏ:

```text
Crawler
Parser
Downloader
Authenticator
Notifier
```

---

# Phần IV — DIP

### Buổi 10 — Dependency Inversion Principle

Đây là phần **cực kỳ quan trọng**.

* High-level module
* Low-level module
* Dependency
* Abstraction
* Dependency direction
* Dependency Inversion ≠ Dependency Injection

Ví dụ:

```python
class UserService:
    def __init__(self):
        self.repo = SQLiteUserRepository()
```

và:

```python
class UserService:
    def __init__(self, repo):
        self.repo = repo
```

### Buổi 11 — DIP Deep Dive

* Constructor Injection
* Method Injection
* Factory Injection
* Composition Root
* Abstract Factory
* Protocol
* Testing
* Mock/Fake
* DIP trong Clean Architecture

---

# Phần V — SOLID kết hợp

### Buổi 12 — SOLID + Design Patterns

Kết hợp:

* Strategy
* Factory
* Adapter
* Repository
* Observer
* Command
* Template Method

### Buổi 13 — SOLID + Python

* Duck typing
* `Protocol`
* `ABC`
* `dataclass`
* `typing`
* Higher-order function
* First-class function
* Composition

### Buổi 14 — SOLID + Testing

* Unit Test
* Mock
* Stub
* Fake
* Dependency Injection
* Testability
* Testing architecture

### Buổi 15 — SOLID + DDD

* Entity
* Value Object
* Aggregate
* Domain Service
* Repository
* Application Service

Đặc biệt:

```text
Domain
   ↓
Application
   ↓
Infrastructure
```

và dependency direction.

---

# Phần VI — SOLID trong Clean Architecture

### Buổi 16

Áp dụng SOLID vào:

```text
Entities
Use Cases
Interface Adapters
Frameworks & Drivers
```

### Buổi 17

Thiết kế:

```text
CLI
 ↓
Application
 ↓
Domain
 ↓
Repository Interface
 ↓
SQLite Repository
```

### Buổi 18

Thiết kế:

```text
Crawler
 ↓
Use Case
 ↓
Crawler Interface
 ↓
Crawler Plugin
```

### Buổi 19

Refactoring một hệ thống vi phạm SOLID.

Bắt đầu từ:

```python
class CrawlerManager:
    ...
```

và từng bước refactor thành architecture tốt.

---

# Phần VII — SOLID trong project thực tế

### Buổi 20 — Mini Project

Xây dựng:

**Story Crawler System**

```text
                    ┌──────────────┐
                    │     CLI      │
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │   Use Case   │
                    └──────┬───────┘
                           ↓
              ┌────────────┴────────────┐
              ↓                         ↓
       Crawler Interface          Repository
              ↓                         ↓
       ┌──────┴──────┐             SQLite
       ↓             ↓
   Source A       Source B
```

Phân tích từng SOLID principle trong hệ thống.

---

# Một nguyên tắc rất quan trọng

Tôi muốn bạn ghi nhớ điều này trước khi bắt đầu:

> **SOLID không phải mục tiêu. Maintainable software mới là mục tiêu.**

Ví dụ, code này:

```python
class UserService:
    def __init__(
        self,
        user_repository,
        email_service,
        logger,
        cache,
        event_bus,
        metrics,
        config,
    ):
        ...
```

có thể nhìn **rất SOLID**.

Nhưng nếu một use case đơn giản mà phải truyền 7 dependency thì kiến trúc có thể đang bị over-engineering.

Ngược lại:

```python
class User:
    ...
```

có thể có nhiều method và vẫn hoàn toàn ổn.

Vì vậy trong khóa này ta sẽ luôn đặt câu hỏi:

```text
WHY?
 ↓
Vấn đề gì đang tồn tại?
 ↓
SOLID principle nào liên quan?
 ↓
Có thực sự cần abstraction không?
 ↓
Thiết kế nào đơn giản nhất nhưng vẫn dễ thay đổi?
```

---

# Cách học

Mỗi buổi tôi sẽ dùng cấu trúc:

```text
1. Problem
2. Code smell
3. Principle
4. Mental model
5. Python implementation
6. Bad design
7. Refactoring
8. Design alternatives
9. Testing
10. Real-world application
11. Bài tập
```

Và đặc biệt tôi sẽ **không cho bạn học thuộc định nghĩa**.

Ví dụ với SRP, thay vì chỉ nói:

> “Một class chỉ nên có một lý do để thay đổi.”

ta sẽ mổ xẻ một class khoảng 100 dòng, tìm ra **các actor khác nhau**, xác định **các reason to change**, rồi refactor từng bước.

---
