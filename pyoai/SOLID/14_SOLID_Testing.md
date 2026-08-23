# Buổi 14 — SOLID + Testing

Đây là buổi cực kỳ quan trọng, vì chúng ta sẽ nối:

```text
SOLID
  ↓
Architecture
  ↓
Dependency Injection
  ↓
Testability
  ↓
Unit Test
```

Một dấu hiệu rất tốt của thiết kế SOLID là:

> **Code dễ test mà không cần dựng cả hệ thống thật.**

Ngược lại, nếu một class rất khó test, đó thường là dấu hiệu nó đang có coupling quá cao hoặc boundary chưa tốt.

---

# 1. Testing và SOLID liên quan thế nào?

Hãy xem code:

```python
class OrderService:

    def __init__(self):
        self.repo = SQLiteOrderRepository()
        self.email = SMTPEmailSender()
        self.payment = StripePayment()
```

Method:

```python
def create_order(self, order):
    self.payment.charge(order.total)
    self.repo.save(order)
    self.email.send(order.customer_email)
```

Muốn test:

```text
create_order()
```

ta phải có:

```text
SQLite
SMTP
Stripe
Network
```

Đây là vấn đề.

Không phải testing framework có vấn đề.

**Architecture có vấn đề.**

---

# 2. Refactor bằng Dependency Injection

Thay vì:

```python
class OrderService:

    def __init__(self):
        self.repo = SQLiteOrderRepository()
        self.email = SMTPEmailSender()
        self.payment = StripePayment()
```

ta viết:

```python
class OrderService:

    def __init__(
        self,
        repo,
        email,
        payment,
    ):
        self.repo = repo
        self.email = email
        self.payment = payment
```

Production:

```python
service = OrderService(
    repo=SQLiteOrderRepository(),
    email=SMTPEmailSender(),
    payment=StripePayment(),
)
```

Test:

```python
service = OrderService(
    repo=FakeRepository(),
    email=FakeEmailSender(),
    payment=FakePayment(),
)
```

Đây chính là:

```text
DIP
+
Dependency Injection
+
Testability
```

---

# 3. Testability là gì?

**Testability** là mức độ dễ dàng kiểm tra behavior của code.

Code có testability cao thường:

```text
ít global state
ít hidden dependency
ít concrete dependency
dependency injectable
behavior rõ ràng
side effect được cô lập
```

Code testability thấp thường:

```text
new object bên trong
global variable
database trực tiếp
network trực tiếp
filesystem trực tiếp
time trực tiếp
random trực tiếp
```

---

# 4. Unit Test

Unit test kiểm tra một đơn vị behavior tương đối độc lập.

Ví dụ:

```python
def calculate_total(price, quantity):
    return price * quantity
```

Test:

```python
def test_calculate_total():
    assert calculate_total(100, 3) == 300
```

Đây là test rất tốt vì:

```text
input
  ↓
function
  ↓
output
```

Không có:

```text
database
network
filesystem
```

---

# 5. Unit test và SRP

Một function:

```python
def calculate_total(price, quantity):
    ...
```

rất dễ test.

Nhưng:

```python
def process_order():
    validate()
    calculate()
    save_database()
    send_email()
    call_payment_api()
    write_log()
```

sẽ khó test hơn.

Tại sao?

Vì nó có quá nhiều responsibility.

```text
SRP
 ↓
smaller responsibility
 ↓
smaller unit
 ↓
easier testing
```

Đây là mối quan hệ trực tiếp giữa SRP và testing.

---

# 6. Test Double

Trong testing, ta thường không muốn sử dụng dependency thật.

Thay vào đó dùng:

```text
Test Double
```

Các loại quan trọng:

```text
Stub
Mock
Fake
Spy
Dummy
```

Trong buổi này tập trung:

```text
Stub
Mock
Fake
```

---

# 7. Stub

Stub cung cấp dữ liệu cố định để test.

Ví dụ:

```python
class StubUserRepository:

    def get_by_id(self, user_id):
        return User(
            id=user_id,
            name="Alice",
        )
```

Service:

```python
class UserService:

    def __init__(self, repo):
        self.repo = repo

    def get_user_name(self, user_id):
        user = self.repo.get_by_id(user_id)
        return user.name
```

Test:

```python
def test_get_user_name():

    repo = StubUserRepository()

    service = UserService(repo)

    assert service.get_user_name(1) == "Alice"
```

Stub trả về dữ liệu mà test cần.

---

# 8. Fake

Fake là implementation đơn giản nhưng **có behavior thực sự**.

Ví dụ production:

```python
class SQLiteUserRepository:

    def save(self, user):
        ...

    def get_by_id(self, user_id):
        ...
```

Fake:

```python
class InMemoryUserRepository:

    def __init__(self):
        self.users = {}

    def save(self, user):
        self.users[user.id] = user

    def get_by_id(self, user_id):
        return self.users.get(user_id)
```

Fake không phải mock.

Nó thực sự thực hiện repository behavior, chỉ là bằng memory.

---

# 9. Fake cực kỳ hữu ích trong Python

Ví dụ:

```python
repo = InMemoryUserRepository()

service = UserService(repo)

service.create_user(...)
service.create_user(...)

assert repo.get_by_id(1) is not None
```

Không cần SQLite.

Không cần:

```text
temporary database
migration
connection
cleanup
```

---

# 10. Mock

Mock thường được sử dụng để kiểm tra:

> Dependency có được gọi đúng hay không?

Ví dụ:

```python
from unittest.mock import Mock
```

Tạo mock:

```python
repo = Mock()
```

Cấu hình:

```python
repo.get_by_id.return_value = User(
    id=1,
    name="Alice",
)
```

Test:

```python
service = UserService(repo)

result = service.get_user_name(1)

assert result == "Alice"
```

Kiểm tra call:

```python
repo.get_by_id.assert_called_once_with(1)
```

---

# 11. Stub vs Mock

Điểm khác biệt quan trọng:

### Stub

Quan tâm:

```text
dependency trả về gì?
```

### Mock

Quan tâm:

```text
dependency được gọi như thế nào?
```

Ví dụ:

```text
Stub
  ↓
"Đây là User Alice"
```

Mock:

```text
"Bạn đã gọi get_by_id(1)"
```

---

# 12. Fake vs Stub

### Stub

Thường rất đơn giản:

```python
class StubRepository:

    def get_by_id(self, user_id):
        return User(1, "Alice")
```

### Fake

Có behavior:

```python
class InMemoryRepository:

    def __init__(self):
        self.data = {}

    def save(self, user):
        self.data[user.id] = user

    def get_by_id(self, user_id):
        return self.data.get(user_id)
```

Fake giống một implementation đơn giản của production component.

---

# 13. Ví dụ hoàn chỉnh

Ta có domain:

```python
from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
```

Repository contract:

```python
from typing import Protocol


class UserRepository(Protocol):

    def save(self, user: User) -> None:
        ...

    def get_by_id(self, user_id: int) -> User | None:
        ...
```

Service:

```python
class UserService:

    def __init__(self, repo: UserRepository):
        self.repo = repo

    def create_user(
        self,
        user: User,
    ) -> None:

        self.repo.save(user)
```

---

# 14. Fake Repository

```python
class InMemoryUserRepository:

    def __init__(self):
        self.data: dict[int, User] = {}

    def save(self, user: User) -> None:
        self.data[user.id] = user

    def get_by_id(
        self,
        user_id: int,
    ) -> User | None:

        return self.data.get(user_id)
```

Test:

```python
def test_create_user():

    repo = InMemoryUserRepository()

    service = UserService(repo)

    user = User(
        id=1,
        name="Alice",
    )

    service.create_user(user)

    assert repo.get_by_id(1) == user
```

Đây là test rất sạch.

---

# 15. DIP tạo ra Test Boundary

Nhìn architecture:

```text
UserService
     ↓
UserRepository
     ↑
     │
 ┌───┴─────────────┐
 │                 │
SQLiteRepository   FakeRepository
```

Production:

```text
UserService
     ↓
SQLite
```

Test:

```text
UserService
     ↓
Fake
```

**Business code không thay đổi.**

Đây là lợi ích cực lớn của DIP.

---

# 16. Mock trong trường hợp này

Ta cũng có thể:

```python
from unittest.mock import Mock
```

```python
def test_create_user():

    repo = Mock()

    service = UserService(repo)

    user = User(
        id=1,
        name="Alice",
    )

    service.create_user(user)

    repo.save.assert_called_once_with(user)
```

Test này kiểm tra interaction.

---

# 17. Nhưng đừng Mock mọi thứ

Đây là một lỗi phổ biến:

```text
Mock everything
```

Ví dụ:

```python
repo = Mock()
parser = Mock()
validator = Mock()
payment = Mock()
email = Mock()
logger = Mock()
clock = Mock()
```

Test trở thành:

```text
Mock
 ↓
Mock
 ↓
Mock
 ↓
Mock
```

và cuối cùng test chỉ chứng minh:

> Mock được gọi đúng với mock khác.

Không còn kiểm tra nhiều behavior thật.

---

# 18. Fake thường tốt hơn Mock cho Repository

Ví dụ:

```text
Repository
```

thường phù hợp với:

```text
Fake
```

hơn là mock.

Vì ta muốn test behavior:

```python
service.create_user(user)

assert repo.get_by_id(user.id) == user
```

thay vì:

```python
repo.save.assert_called_once_with(user)
```

Test behavior thường bền vững hơn test implementation detail.

---

# 19. Testing Behavior vs Implementation

Test xấu:

```python
repo.save.assert_called_once()
repo.commit.assert_called_once()
repo.connection.execute.assert_called_once()
```

Test tốt hơn:

```python
service.create_user(user)

saved = repo.get_by_id(user.id)

assert saved == user
```

Câu hỏi:

> **User có được lưu hay không?**

quan trọng hơn:

> `commit()` được gọi chính xác một lần hay không?

---

# 20. OCP + Testing

Giả sử:

```python
class PaymentGateway(Protocol):

    def charge(self, amount: int) -> None:
        ...
```

Có:

```text
StripePayment
MomoPayment
PaypalPayment
```

Thêm implementation:

```text
TestPaymentGateway
```

rất dễ.

```python
class FakePaymentGateway:

    def __init__(self):
        self.charged = []

    def charge(self, amount):
        self.charged.append(amount)
```

Test:

```python
payment = FakePaymentGateway()

service = PaymentService(payment)

service.pay(500)

assert payment.charged == [500]
```

OCP tạo ra khả năng thay implementation.

Khả năng thay implementation tạo ra testability.

---

# 21. ISP + Testing

Interface quá lớn:

```python
class Crawler(Protocol):

    def crawl(self): ...
    def parse(self): ...
    def download(self): ...
    def login(self): ...
    def upload(self): ...
    def notify(self): ...
```

Test phải fake tất cả:

```text
crawl
parse
download
login
upload
notify
```

Trong khi component chỉ cần:

```python
class Parser(Protocol):

    def parse(self, html):
        ...
```

Fake trở nên rất nhỏ:

```python
class FakeParser:

    def parse(self, html):
        return Story(...)
```

ISP giúp giảm test setup.

---

# 22. LSP + Testing

Nếu implementation thực sự tuân thủ contract:

```text
Repository
    ↑
SQLiteRepository
FakeRepository
```

thì cùng một test behavior có thể chạy với cả hai.

Ví dụ:

```python
def repository_contract(repo):

    user = User(1, "Alice")

    repo.save(user)

    assert repo.get_by_id(1) == user
```

Chạy:

```python
repository_contract(
    InMemoryUserRepository()
)
```

và:

```python
repository_contract(
    SQLiteUserRepository(...)
)
```

Nếu một implementation fail contract:

```text
LSP violation
```

---

# 23. Contract Test

Đây là kỹ thuật rất hay.

Viết một bộ test cho abstraction:

```python
def test_repository_contract(repo):
    ...
```

Sau đó chạy với:

```text
SQLiteRepository
PostgresRepository
MemoryRepository
```

Ví dụ:

```python
def test_repository_contract(repo):

    user = User(
        id=1,
        name="Alice",
    )

    repo.save(user)

    result = repo.get_by_id(1)

    assert result == user
```

Nếu tất cả implementation đều pass:

```text
Repository contract
        ↓
SQLite      PASS
Memory      PASS
Postgres    PASS
```

Đây là sự kết hợp rất đẹp của:

```text
LSP
+
DIP
+
Testing
```

---

# 24. Dependency Injection làm test dễ như thế nào?

Không DI:

```python
class OrderService:

    def __init__(self):
        self.repo = SQLiteRepository()
```

Test:

```text
OrderService
     ↓
SQLite
     ↓
Database
```

Có DI:

```python
class OrderService:

    def __init__(self, repo):
        self.repo = repo
```

Test:

```text
OrderService
     ↓
FakeRepository
```

Ta đã biến:

```text
hard dependency
```

thành:

```text
replaceable dependency
```

---

# 25. Constructor Injection

Đây thường là lựa chọn tốt nhất.

```python
class UserService:

    def __init__(
        self,
        repo: UserRepository,
    ):
        self.repo = repo
```

Dependency được biết ngay khi object được tạo.

Ưu điểm:

```text
explicit
easy to test
object luôn ở trạng thái hợp lệ
dependency visible
```

---

# 26. Method Injection

Dependency chỉ cần cho một operation:

```python
class ReportService:

    def generate(
        self,
        data,
        formatter,
    ):
        return formatter(data)
```

Không nhất thiết:

```python
class ReportService:

    def __init__(self, formatter):
        ...
```

Nếu formatter chỉ được dùng một lần, method injection có thể hợp lý hơn.

---

# 27. Function Injection

Python còn đơn giản hơn:

```python
class PriceService:

    def __init__(
        self,
        tax_calculator,
    ):
        self.tax_calculator = tax_calculator
```

Dependency:

```python
def calculate_tax(price):
    return price * 0.1
```

Test:

```python
def fake_tax(price):
    return 0
```

Inject:

```python
service = PriceService(fake_tax)
```

Không cần class.

---

# 28. Mock `unittest.mock`

Python có sẵn:

```python
from unittest.mock import Mock
```

và:

```python
from unittest.mock import MagicMock
```

Ví dụ:

```python
repo = Mock()

repo.get_by_id.return_value = User(
    id=1,
    name="Alice",
)
```

Kiểm tra:

```python
repo.get_by_id.assert_called_once_with(1)
```

Một số method hữu ích:

```text
assert_called()
assert_called_once()
assert_called_with()
assert_called_once_with()
assert_not_called()
call_count
```

---

# 29. `side_effect`

Có thể mô phỏng exception:

```python
repo.get_by_id.side_effect = RuntimeError(
    "Database error"
)
```

Test:

```python
import pytest


def test_database_error():

    with pytest.raises(RuntimeError):
        service.get_user(1)
```

---

# 30. Nhưng Mock không thay thế Design

Một misconception:

> "Dùng Mock thì architecture xấu cũng test được."

Có thể test được.

Nhưng test sẽ trở thành:

```text
mock everything
```

Architecture vẫn coupling.

Mục tiêu không phải:

> Làm cho code xấu vẫn test được.

Mục tiêu là:

> Thiết kế code tốt để testing trở nên tự nhiên.

---

# 31. SOLID → Testability

Có thể nhìn toàn bộ như sau:

```text
SRP
 ↓
small responsibilities
 ↓
small tests
```

```text
OCP
 ↓
replaceable implementations
 ↓
easy test doubles
```

```text
LSP
 ↓
substitutability
 ↓
contract tests
```

```text
ISP
 ↓
small interfaces
 ↓
small fakes/mocks
```

```text
DIP
 ↓
injectable dependencies
 ↓
isolated unit tests
```

---

# 32. Một ví dụ xấu

```python
class CrawlerManager:

    def crawl(self, url):

        response = requests.get(url)

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        title = soup.find("h1").text

        conn = sqlite3.connect(
            "stories.db"
        )

        conn.execute(
            "INSERT INTO stories(title) VALUES (?)",
            (title,),
        )

        conn.commit()

        send_email(
            "admin@example.com",
            title,
        )
```

Một method đang làm:

```text
HTTP
HTML parsing
business logic
database
notification
```

Testing cực khó.

---

# 33. Refactor

Ta tạo:

```text
HTTP Client
Parser
Repository
Notifier
Use Case
```

```python
class CrawlStory:

    def __init__(
        self,
        client,
        parser,
        repository,
        notifier,
    ):
        self.client = client
        self.parser = parser
        self.repository = repository
        self.notifier = notifier

    def execute(self, url):

        html = self.client.get(url)

        story = self.parser.parse(html)

        self.repository.save(story)

        self.notifier.notify(story)
```

---

# 34. Test Use Case

Fake:

```python
class FakeClient:

    def get(self, url):
        return "<h1>Python</h1>"
```

```python
class FakeParser:

    def parse(self, html):
        return Story(
            id=1,
            title="Python",
        )
```

```python
class FakeRepository:

    def __init__(self):
        self.saved = []

    def save(self, story):
        self.saved.append(story)
```

```python
class FakeNotifier:

    def __init__(self):
        self.notifications = []

    def notify(self, story):
        self.notifications.append(story)
```

---

# 35. Test

```python
def test_crawl_story():

    client = FakeClient()
    parser = FakeParser()
    repository = FakeRepository()
    notifier = FakeNotifier()

    use_case = CrawlStory(
        client,
        parser,
        repository,
        notifier,
    )

    use_case.execute(
        "https://example.com"
    )

    assert len(repository.saved) == 1

    assert repository.saved[0].title == "Python"

    assert len(notifier.notifications) == 1
```

Không cần:

```text
Internet
SQLite
SMTP
```

Đây chính là architecture tốt.

---

# 36. Testing Architecture

Một architecture tốt thường có:

```text
                 Tests
                   │
        ┌──────────┼──────────┐
        ↓          ↓          ↓
      Domain   Application Infrastructure
        │          │             │
      fast       fast          slower
```

### Domain test

Rất nhanh:

```text
pure logic
```

### Application test

Dùng:

```text
Fake
Stub
Mock
```

### Infrastructure test

Có thể dùng:

```text
SQLite
HTTP test server
filesystem
```

---

# 37. Đừng biến mọi test thành Unit Test

Không phải test nào cũng phải mock.

Ví dụ Repository:

```python
SQLiteUserRepository
```

nên có integration test thật với SQLite.

```text
SQLiteRepository
       ↓
SQLite test database
```

Ta muốn kiểm tra:

```text
SQL
schema
mapping
transaction
```

Nếu mock SQLite thì ta không test những thứ đó.

---

# 38. Test Pyramid

Có thể hình dung:

```text
             /\
            /  \
           / E2E\
          /------\
         /Integr. \
        /----------\
       / Unit Tests \
      /______________\
```

Thông thường:

```text
nhiều Unit Test
ít Integration Test hơn
ít E2E Test nhất
```

Vì Unit Test:

```text
nhanh
rẻ
ổn định
```

---

# 39. Nhưng đừng cực đoan

Không phải:

```text
100% Mock
```

hay:

```text
100% Unit Test
```

Mục tiêu:

> **Test đúng boundary.**

Ví dụ crawler:

```text
Domain
→ Unit Test

Use Case
→ Unit Test + Fake

Parser
→ Unit Test

SQLite Repository
→ Integration Test

HTTP client
→ Integration Test

Toàn hệ thống
→ một số E2E
```

---

# 40. Một nguyên tắc rất quan trọng

> **Mock boundary, không mock implementation detail.**

Ví dụ:

```text
Application
     ↓
Repository
```

Mock/Fake:

```text
Repository
```

hợp lý.

Nhưng:

```text
Application
     ↓
Repository
     ↓
SQLite connection
     ↓
cursor
```

rồi mock:

```text
cursor.execute()
cursor.fetchone()
cursor.commit()
```

thường là dấu hiệu test đang đi quá sâu vào implementation.

---

# 41. SOLID + Testing Matrix

| Principle   | Testing benefit          |
| ----------- | ------------------------ |
| SRP         | test nhỏ                 |
| OCP         | dễ thay implementation   |
| LSP         | contract testing         |
| ISP         | test double nhỏ          |
| DIP         | dependency injection     |
| Composition | isolation                |
| Protocol    | fake dễ dàng             |
| Dataclass   | state rõ ràng            |
| Callable    | inject behavior đơn giản |

---

# 42. Bài tập 1 — Stub

Viết:

```python
class WeatherService:
    ...
```

nhận:

```text
WeatherRepository
```

Method:

```python
get_temperature(city)
```

Viết `StubWeatherRepository` trả:

```text
Hanoi → 30
Saigon → 32
```

Test service.

---

# 43. Bài tập 2 — Fake

Viết:

```python
InMemoryStoryRepository
```

có:

```python
save(story)
get_by_id(id)
delete(id)
```

Không dùng SQLite.

Sau đó viết test cho CRUD.

---

# 44. Bài tập 3 — Mock

Viết:

```python
EmailService
```

với dependency:

```python
mailer
```

Test:

```text
send_welcome_email()
```

phải kiểm tra:

```text
mailer.send()
```

được gọi đúng:

```text
recipient
subject
body
```

---

# 45. Bài tập 4 — Contract Test

Tạo:

```text
Repository Protocol
```

và:

```text
InMemoryRepository
SQLiteRepository
```

Viết một bộ test chung:

```python
def test_repository_contract(repo):
    ...
```

Chạy test đó cho cả hai implementation.

Đây là bài tập rất quan trọng để hiểu **LSP trong thực tế**.

---

# 46. Bài tập 5 — Refactoring

Cho code:

```python
class OrderService:

    def create_order(self, order):

        conn = sqlite3.connect(
            "orders.db"
        )

        conn.execute(...)

        requests.post(
            "https://payment.example.com",
            json=order,
        )

        smtplib.SMTP(...)

        conn.commit()
```

Yêu cầu:

```text
1. Tách responsibility
2. Tạo Protocol
3. Dependency Injection
4. Fake
5. Unit Test
6. Integration Test boundary
```

Kiến trúc mục tiêu:

```text
OrderService
   │
   ├── OrderRepository
   │
   ├── PaymentGateway
   │
   └── EmailSender
```

---

# 47. Bài tập lớn — Testable Crawler

Đây là bài rất sát với hệ thống crawler mà bạn đang học.

Thiết kế:

```text
                    CrawlStory
                         │
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
    HttpClient         Parser          Repository
        │                │                │
      Fake             Fake             Fake
```

Test:

```text
1. HTTP failure
2. Parse failure
3. Invalid story
4. Repository failure
5. Successful crawl
6. Duplicate story
```

Sau đó viết integration test:

```text
SQLiteRepository
        ↓
SQLite test DB
```

---

# 48. Insight quan trọng nhất của Buổi 14

Có một vòng lặp rất đẹp:

```text
SOLID
  ↓
loose coupling
  ↓
dependency injection
  ↓
replaceable dependencies
  ↓
test doubles
  ↓
isolated tests
  ↓
feedback nhanh
  ↓
refactoring an toàn
```

Và ngược lại:

```text
Code khó test
     ↓
dependency quá chặt
     ↓
coupling cao
     ↓
architecture có vấn đề
```

Cho nên:

> **Testability không chỉ là vấn đề testing. Nó là một tiêu chí đánh giá architecture.**

---

# 49. Mental Model của Buổi 14

Hãy nhớ 4 tầng:

```text
                TEST
                 │
        ┌────────┴────────┐
        ↓                 ↓
    Behavior          Interaction
        │                 │
     Fake/Stub           Mock
        │
        ↓
   Dependency Injection
        │
        ↓
      SOLID
```

Và một nguyên tắc thực chiến:

> **Nếu muốn biết abstraction của bạn có tốt hay không, hãy thử viết test cho component đó mà không khởi động cả hệ thống.**

Nếu phải dựng:

```text
Database
Redis
HTTP
SMTP
Filesystem
Queue
```

chỉ để test một business rule nhỏ, hãy nghi ngờ architecture.

---

## Roadmap hiện tại

```text
# Phần V — SOLID kết hợp

✅ Buổi 12 — SOLID + Design Patterns
✅ Buổi 13 — SOLID + Python
✅ Buổi 14 — SOLID + Testing
⬜ Buổi 15 — SOLID + DDD

# Phần VI — SOLID trong Clean Architecture

⬜ Buổi 16 — Clean Architecture
⬜ Buổi 17 — CLI
              ↓
           Application
              ↓
            Domain
              ↓
       Repository Interface
              ↓
         SQLite Repository

⬜ Buổi 18 — Crawler
              ↓
           Use Case
              ↓
       Crawler Interface
              ↓
        Crawler Plugin

⬜ Buổi 19 — Refactoring
              CrawlerManager
                    ↓
              từng bước
                    ↓
           SOLID Architecture
```

**Buổi 15 sẽ nối SOLID với DDD**, đặc biệt là `Entity`, `Value Object`, `Aggregate`, `Domain Service`, `Repository`, `Application Service` và quan trọng nhất: **tại sao DDD + SOLID + Dependency Direction tạo thành nền tảng rất tốt cho Clean Architecture.**
