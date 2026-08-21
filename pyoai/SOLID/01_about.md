

# Buổi 1 — SOLID là gì?

Trước khi học S, O, L, I, D, chúng ta cần hiểu **tại sao SOLID tồn tại**.

Hãy tưởng tượng bạn có:

```python
class OrderService:

    def create_order(self):
        ...

    def calculate_price(self):
        ...

    def save_to_database(self):
        ...

    def send_email(self):
        ...

    def generate_pdf(self):
        ...

    def log(self):
        ...
```

Code này có thể:

* chạy đúng
* test được
* production vẫn chạy

Nhưng khi requirement thay đổi:

```text
Database đổi
Email provider đổi
PDF library đổi
Pricing rule đổi
Logging system đổi
```

một class bị thay đổi liên tục.

Đây chính là vấn đề SOLID muốn chúng ta suy nghĩ về.

---

## 1. SOLID không phải một Design Pattern

Đây là distinction rất quan trọng.

Design Pattern:

```text
Factory
Strategy
Adapter
Observer
Repository
```

thường trả lời:

> **Tôi có thể giải quyết một loại vấn đề thiết kế như thế nào?**

SOLID trả lời:

> **Tôi nên đánh giá chất lượng thiết kế của mình như thế nào?**

Ví dụ:

```text
Strategy Pattern
       ↓
có thể giúp thực hiện OCP
```

hoặc:

```text
Dependency Injection
       ↓
có thể giúp thực hiện DIP
```

Nhưng:

```text
Strategy ≠ OCP
DI ≠ DIP
```

Đây là hai khái niệm khác nhau.

---

# 2. Vấn đề cốt lõi: Change

Phần lớn SOLID xoay quanh một câu hỏi:

> **Nếu phần mềm thay đổi, tôi phải sửa bao nhiêu thứ?**

Ví dụ:

```python
class ReportService:

    def generate(self):
        data = self.load_data()
        data = self.calculate(data)
        pdf = self.create_pdf(data)
        self.send_email(pdf)
```

Ban đầu rất tiện.

Nhưng sau đó:

```text
PDF → HTML
Email → Telegram
SQLite → PostgreSQL
Calculation → rule mới
```

Mỗi thay đổi có thể kéo theo việc sửa:

```text
ReportService
```

Nếu `ReportService` trở thành trung tâm của mọi thứ, coupling tăng lên.

---

# 3. Coupling

**Coupling** = mức độ một thành phần phụ thuộc vào thành phần khác.

Ví dụ:

```python
class UserService:

    def __init__(self):
        self.repository = SQLiteUserRepository()
```

`UserService` phụ thuộc trực tiếp vào:

```text
SQLiteUserRepository
```

Do đó:

```text
UserService
      ↓
SQLite
```

Nếu muốn chuyển sang:

```text
PostgreSQLUserRepository
```

ta phải thay đổi `UserService`.

Một thiết kế khác:

```python
class UserService:

    def __init__(self, repository):
        self.repository = repository
```

Bây giờ:

```text
UserService
      ↓
Repository abstraction
      ↑
      │
 ┌────┴─────┐
 │          │
SQLite    PostgreSQL
```

Đây là ý tưởng cực kỳ quan trọng của SOLID.

---

# 4. Cohesion

Nếu coupling hỏi:

> “Class này phụ thuộc vào bao nhiêu thứ?”

thì cohesion hỏi:

> “Những thứ bên trong class này có thực sự thuộc về nhau không?”

Ví dụ:

```python
class UserService:

    def create_user(self):
        ...

    def delete_user(self):
        ...

    def send_email(self):
        ...

    def resize_image(self):
        ...

    def generate_pdf(self):
        ...
```

Cohesion thấp.

Trong khi:

```python
class UserService:

    def create_user(self):
        ...

    def delete_user(self):
        ...

    def update_user(self):
        ...
```

cohesion cao hơn.

Một cách nhớ:

```text
High Cohesion
    +
Low Coupling
    ↓
Good Design
```

Đây chính là nền tảng để hiểu SOLID.

---

# 5. SOLID gồm 5 principle

```text
S — Single Responsibility Principle
O — Open/Closed Principle
L — Liskov Substitution Principle
I — Interface Segregation Principle
D — Dependency Inversion Principle
```

Nhưng đừng học chúng như 5 điều luật độc lập.

Chúng liên kết với nhau:

```text
SRP
 ↓
giảm responsibility
 ↓
giảm coupling
 ↓
OCP
 ↓
dễ mở rộng
 ↓
LSP
 ↓
subtype đúng contract
 ↓
ISP
 ↓
interface nhỏ
 ↓
DIP
 ↓
dependency hướng vào abstraction
```

---

# 6. Một mental model tốt hơn

Thay vì nhớ:

```text
S = ...
O = ...
L = ...
I = ...
D = ...
```

hãy nhớ:

```text
              CHANGE
                │
                ↓
        ┌───────────────┐
        │   SOLID       │
        └───────────────┘
          │ │ │ │ │
          ↓ ↓ ↓ ↓ ↓
          S O L I D
```

SOLID chủ yếu giúp chúng ta **quản lý sự thay đổi**.

---

# Bài tập Buổi 1

Cho class:

```python
class OrderManager:

    def create_order(self, items):
        ...

    def calculate_total(self, items):
        ...

    def save_order(self, order):
        ...

    def send_confirmation_email(self, order):
        ...

    def generate_invoice_pdf(self, order):
        ...

    def log(self, message):
        ...
```

Hãy phân tích:

### Câu 1

Class này có những responsibility nào?

### Câu 2

Có những **reason to change** nào?

### Câu 3

Dependency nào đang có khả năng tạo coupling?

### Câu 4

Cohesion của class này cao hay thấp? Vì sao?

### Câu 5

Nếu ngày mai:

```text
SQLite → PostgreSQL
Email → Telegram
PDF → HTML
```

thì class này bị ảnh hưởng như thế nào?

---

**Buổi 2 chúng ta sẽ đi sâu vào SRP**, và tôi sẽ đặc biệt giải thích câu rất dễ hiểu sai:

> **“Một class chỉ có một responsibility” thực sự nghĩa là gì?**

Sau đó chúng ta sẽ dùng **OrderService → OrderRepository → EmailService → InvoiceGenerator** để refactor từ code xấu sang thiết kế tốt, thay vì chỉ học lý thuyết.
