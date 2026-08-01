# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 37: Pytest (Phần 9) – Test Design Pattern và kiến trúc Test chuyên nghiệp

> Viết được test chạy là bước đầu.
> Viết được **bộ test dễ đọc, dễ mở rộng, dễ bảo trì trong nhiều năm** mới là kỹ năng của lập trình viên chuyên nghiệp.

Trong dự án nhỏ:

```text
tests/
    test_user.py
```

có thể đủ.

Nhưng dự án lớn:

```text
1000+
test cases
```

nếu không có kiến trúc:

* Test bị trùng code.
* Sửa một model phải sửa hàng chục test.
* Không biết test nào đang kiểm tra điều gì.
* Debug rất khó.

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ:

* Hiểu AAA Pattern.
* Hiểu Given-When-Then.
* Thiết kế test rõ ràng.
* Biết Test Data Builder.
* Biết Object Mother.
* Biết Factory Pattern trong Testing.
* Thiết kế Unit Test cho Service.
* Thiết kế Repository Test.
* Xây kiến trúc test cho dự án Python lớn.

---

# Roadmap Pytest

```text
Buổi 29
Pytest cơ bản

Buổi 30
Fixture

Buổi 31
Parametrize

Buổi 32
MonkeyPatch

Buổi 33
Mock

Buổi 34
Integration Test

Buổi 35
E2E Test

Buổi 36
Coverage

Buổi 37
Test Design Pattern
```

---

# Phần I

# AAA Pattern

AAA là pattern phổ biến nhất trong Unit Testing.

AAA:

```text
Arrange

↓

Act

↓

Assert
```

---

# 1. Arrange

Chuẩn bị dữ liệu.

Ví dụ:

```python
user = User(name="Alice")
```

---

# 2. Act

Thực hiện hành động.

```python
result = service.create_user(user)
```

---

# 3. Assert

Kiểm tra kết quả.

```python
assert result.name == "Alice"
```

---

Ví dụ hoàn chỉnh:

```python
def test_create_user():

    # Arrange

    user = User("Alice")

    # Act

    result = service.create(user)

    # Assert

    assert result.name == "Alice"
```

---

Đây là format mà hầu hết team Python chuyên nghiệp sử dụng.

---

# Phần II

# Vì sao AAA quan trọng?

Không có AAA:

```python
def test_user():

    user = User()

    repo.save(user)

    result = repo.find(1)

    assert result
```

Khó đọc.

---

Có AAA:

```python
def test_user():

    # Arrange

    user = User()

    # Act

    result = create_user(user)

    # Assert

    assert result
```

Người đọc hiểu ngay.

---

# Phần III

# Given - When - Then

BDD style.

Rất phổ biến trong:

* Cucumber.
* Behave.
* Acceptance Test.

---

Cấu trúc:

```text
Given

↓

When

↓

Then
```

---

Ví dụ:

Yêu cầu:

> Khi user đăng nhập đúng mật khẩu thì vào dashboard.

---

Given:

```text
Có user tồn tại
```

---

When:

```text
Gửi username/password
```

---

Then:

```text
Nhận token
```

---

Python:

```python
def test_login():

    # Given

    user = create_user()

    # When

    token = login(user)

    # Then

    assert token is not None
```

---

# Phần IV

# Test Isolation

Một nguyên tắc quan trọng:

> Một test không được phụ thuộc test khác.

---

Sai:

```python
def test_create():

    create_user()


def test_delete():

    delete_user()
```

Test delete phụ thuộc create.

---

Nếu:

```text
test_create FAIL
```

thì:

```text
test_delete FAIL
```

---

Đúng:

Mỗi test tự chuẩn bị:

```python
def test_delete():

    user = create_user()

    delete_user(user)

    assert ...
```

---

# Phần V

# Test Data Builder Pattern

Vấn đề:

Model lớn.

Ví dụ:

```python
class User:
    def __init__(self, name, email, age, address, phone, role, created_at): ...
```

---

Test:

```python
user = User("Alice", "a@test.com", 20, "Hanoi", "123", "admin", datetime.now())
```

Rất dài.

---

Giải pháp:

## Builder

---

Tạo:

```text
tests/

builders/

    user_builder.py
```

---

Code:

```python
class UserBuilder:
    def __init__(self):

        self.user = User(name="Test", email="test@test.com")

    def with_name(self, name):

        self.user.name = name

        return self

    def build(self):

        return self.user
```

---

Dùng:

```python
user = UserBuilder().with_name("Alice").build()
```

---

Rất dễ đọc.

---

# Phần VI

# Object Mother Pattern

Ý tưởng:

Tạo sẵn object phổ biến.

Ví dụ:

```text
tests/

fixtures/

    users.py
```

---

Code:

```python
def normal_user():

    return User(name="Alice", role="user")


def admin_user():

    return User(name="Admin", role="admin")
```

---

Test:

```python
def test_admin():

    user = admin_user()

    assert user.role == "admin"
```

---

Dễ tái sử dụng.

---

# Phần VII

# Factory Pattern trong Testing

Khi cần tạo nhiều dữ liệu.

Ví dụ:

```python
class UserFactory:
    @staticmethod
    def create(role="user"):

        return User(name="Test", role=role)
```

---

Dùng:

```python
user = UserFactory.create()
```

---

Hoặc:

```python
admin = UserFactory.create(role="admin")
```

---

# Phần VIII

# Service Test Pattern

Kiến trúc:

```text
Service

 |

Repository
```

---

Không test database.

Dùng Mock.

---

Ví dụ:

```python
def test_register_user():

    # Arrange

    repo = Mock()

    service = UserService(repo)

    # Act

    result = service.register("Alice")

    # Assert

    assert result.name == "Alice"

    repo.save.assert_called_once()
```

---

Đây là Unit Test chuẩn.

---

# Phần IX

# Repository Test Pattern

Repository khác Service.

Repository cần test:

* SQL.
* Mapping.
* Query.

Dùng Integration Test.

---

Ví dụ:

```python
def test_save_user(database):

    repo = UserRepository(database)

    user = User("Alice")

    repo.save(user)

    result = repo.find(user.id)

    assert result.name == "Alice"
```

---

---

# Phần X

# Test Naming Convention

Tên test phải mô tả hành vi.

---

Không tốt:

```python
test_user1()
```

---

Tốt:

```python
test_create_user_with_valid_email()
```

---

Hoặc:

```python
test_login_should_fail_when_password_invalid()
```

---

Nguyên tắc:

Tên test = Business Behavior.

---

# Phần XI

# Test Folder Architecture

Dự án lớn:

```text
tests/

├── unit/

│
├── integration/

│
├── e2e/


├── fixtures/

│
├── builders/

│
├── factories/


└── conftest.py
```

---

Ví dụ:

```text
tests/unit/services/

    test_user_service.py


tests/integration/repositories/

    test_user_repository.py
```

---

# Phần XII

# Áp dụng vào Clean Architecture

Ví dụ:

```text
app/

├── domain/

├── application/

├── infrastructure/

└── presentation/
```

---

Test:

```text
tests/

├── unit/

│
│── domain/

│
│── application/


├── integration/

│
│── infrastructure/


└── e2e/

    api/
```

---

Mapping:

| Layer      | Test        |
| ---------- | ----------- |
| Domain     | Unit        |
| Service    | Unit + Mock |
| Repository | Integration |
| API        | E2E         |

---

# Phần XIII

# Ví dụ thực tế: Story Crawler

Kiến trúc:

```text
CrawlerService

↓

ChapterRepository

↓

SQLite
```

---

## Unit Test

Test:

```text
CrawlerService
```

Mock:

```text
Repository
Downloader
```

---

## Integration Test

Test:

```text
Repository

+

SQLite
```

---

## E2E

Test:

```text
Start Crawl

↓

Save Chapter

↓

Read Chapter
```

---

# Phần XIV

# Anti Pattern trong Testing

## 1. Test quá nhiều implementation

Sai:

```python
assert service.call_repository()
```

Không quan trọng.

---

Đúng:

```python
assert result.success
```

---

## 2. Test quá dài

Một test:

```text
200 dòng
```

Nên chia nhỏ.

---

## 3. Duplicate setup

Sai:

```python
user = User(...)
```

lặp 100 lần.

Dùng:

* Fixture.
* Factory.
* Builder.

---

# Phần XV

# Mini Project

Thiết kế Test Architecture cho:

## Book Management System

Code:

```text
BookService

BookRepository

Database

REST API
```

---

Tạo:

```text
tests/

├── unit/

│
│── test_book_service.py


├── integration/

│
│── test_book_repository.py


└── e2e/

    └── test_book_api.py
```

---

Áp dụng:

* AAA.
* Fixture.
* Factory.
* Builder.
* Mock.

---

# Bài tập

## Bài 1

Viết lại test theo AAA:

```python
def test_x(): ...
```

---

## Bài 2

Tạo:

```text
UserFactory
```

---

## Bài 3

Tạo:

```text
UserBuilder
```

---

## Bài 4

Viết:

```text
UserService Unit Test
```

dùng Mock.

---

## Bài 5

Thiết kế:

```text
Story Crawler Test Architecture
```

---

# Tổng kết Buổi 37

Bạn đã học:

✅ AAA Pattern
✅ Given-When-Then
✅ Test Isolation
✅ Test Data Builder
✅ Object Mother
✅ Factory Pattern
✅ Service Test Pattern
✅ Repository Test Pattern
✅ Test Naming
✅ Test Architecture
✅ Clean Architecture Testing

---

# Góc nhìn Senior Python Developer

Một bộ test chuyên nghiệp không chỉ là:

```text
pytest chạy xanh
```

Mà phải đạt:

```text
Readable

+

Maintainable

+

Fast

+

Reliable
```

Một test tốt phải trả lời được:

> "Nếu test này fail, tôi biết ngay tính năng nào bị lỗi."

Đó là sự khác biệt giữa:

**người biết viết test**

và

**kỹ sư xây dựng hệ thống kiểm thử.**

---

# Chuẩn bị Buổi 38

**Pytest (Phần 10) – Testing trong Clean Architecture và Domain Driven Design**

Nội dung:

* Test Domain Model.
* Test Entity.
* Test Value Object.
* Test Aggregate.
* Test Use Case.
* Test Repository Interface.
* Test Dependency Injection.
* Xây bộ test cho hệ thống Python Enterprise.
