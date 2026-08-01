# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 31: Pytest (Phần 3) – Parametrize và Data Driven Testing chuyên nghiệp

> **Một trong những điểm mạnh nhất của pytest là khả năng kiểm thử hàng trăm trường hợp dữ liệu chỉ bằng vài dòng code.**

Trong thực tế, bạn thường gặp bài toán:

* Kiểm tra 100 URL crawler.
* Kiểm tra 500 input validator.
* Kiểm tra nhiều loại user.
* Kiểm tra nhiều database engine.
* Kiểm tra nhiều phiên bản API.

Nếu viết thủ công:

```python
def test_case_1(): ...


def test_case_2(): ...


def test_case_3(): ...
```

sẽ trở thành:

```text
1000 hàm test
```

Rất khó bảo trì.

Giải pháp:

> **Parametrize**

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ:

* Hiểu Data Driven Testing.
* Thành thạo `pytest.mark.parametrize`.
* Test nhiều bộ dữ liệu.
* Parametrize nhiều tham số.
* Kết hợp Fixture + Parametrize.
* Tạo test case động.
* Test Validator, Parser, Repository.
* Biết cách viết test chuyên nghiệp.

---

# Roadmap Pytest

```text
Buổi 29
✓ Pytest cơ bản

Buổi 30
✓ Fixture

Buổi 31
✓ Parametrize

Buổi 32
MonkeyPatch

Buổi 33
Mock trong pytest
```

---

# Phần I

# Data Driven Testing là gì?

Ý tưởng:

Không viết:

```text
Logic test
+
Dữ liệu test
```

chung một chỗ.

Tách:

```text
Test Function

+

Test Data
```

---

Ví dụ.

Hàm:

```python
def is_even(number):

    return number % 2 == 0
```

---

Cần test:

```text
2 -> True

4 -> True

5 -> False

7 -> False
```

---

Cách truyền thống:

```python
def test_2():
    assert is_even(2)


def test_4():
    assert is_even(4)


def test_5():
    assert not is_even(5)
```

Rất dài.

---

# Phần II

# Parametrize đầu tiên

Cú pháp:

```python
@pytest.mark.parametrize(
    "input, expected",
    [
        (...,...),
        (...,...)
    ]
)
```

---

Ví dụ:

```python
import pytest


def is_even(number):

    return number % 2 == 0


@pytest.mark.parametrize(
    "number, expected",
    [
        (2, True),
        (4, True),
        (5, False),
        (7, False),
    ],
)
def test_is_even(number, expected):

    assert is_even(number) == expected
```

---

Kết quả:

```text
test_is_even[2-True] PASSED

test_is_even[4-True] PASSED

test_is_even[5-False] PASSED

test_is_even[7-False] PASSED
```

---

Một function.

4 test case.

---

# Phần III

# Parametrize nhiều tham số

Ví dụ:

Hàm tính tổng:

```python
def add(a, b):

    return a + b
```

---

Test:

```python
@pytest.mark.parametrize("a,b,result", [(1, 2, 3), (10, 20, 30), (-1, 1, 0)])
def test_add(a, b, result):

    assert add(a, b) == result
```

---

Pytest tự sinh:

```text
1 + 2

10 + 20

-1 + 1
```

---

# Phần IV

# Parametrize với Exception

Ví dụ:

```python
def divide(a, b):

    if b == 0:
        raise ValueError

    return a / b
```

---

Test:

```python
@pytest.mark.parametrize("a,b", [(10, 0), (5, 0), (100, 0)])
def test_divide_error(a, b):

    with pytest.raises(ValueError):
        divide(a, b)
```

---

---

# Phần V

# Đặt tên cho Test Case

Mặc định:

```text
test_login[Alice-123]
```

Có thể đặt.

```python
@pytest.mark.parametrize(
    "username,password",
    [
        pytest.param("admin", "123", id="admin-login"),
        pytest.param("guest", "456", id="guest-login"),
    ],
)
def test_login(username, password): ...
```

Kết quả:

```text
test_login[admin-login]

test_login[guest-login]
```

---

Rất hữu ích khi CI/CD báo lỗi.

---

# Phần VI

# Parametrize với Dictionary

Ví dụ:

```python
cases = [{"name": "Alice", "age": 20}, {"name": "Bob", "age": 30}]
```

---

Test:

```python
@pytest.mark.parametrize("user", cases)
def test_user(user):

    assert user["age"] > 18
```

---

# Phần VII

# Parametrize Fixture

Đây là phần rất quan trọng.

Ví dụ:

```python
@pytest.fixture
def calculator():

    return Calculator()
```

---

Kết hợp:

```python
@pytest.mark.parametrize("a,b,result", [(1, 2, 3), (5, 5, 10)])
def test_add(calculator, a, b, result):

    assert calculator.add(a, b) == result
```

---

Luồng:

```text
Fixture

↓

Tạo Calculator

↓

Parametrize

↓

Chạy nhiều dữ liệu
```

---

# Phần VIII

# Parametrize Repository

Ví dụ:

Repository:

```python
class BookRepository:
    def search(self, keyword): ...
```

---

Test nhiều từ khóa:

```python
@pytest.mark.parametrize("keyword,count", [("python", 5), ("java", 3), ("rust", 2)])
def test_search(repository, keyword, count):

    result = repository.search(keyword)

    assert len(result) == count
```

---

Rất phù hợp:

* Database.
* Search engine.
* API.

---

# Phần IX

# Parametrize Parser HTML

Đây là ví dụ sát với dự án crawler.

Giả sử:

```python
def parse_title(html): ...
```

---

Nhiều website:

```python
cases = [("<h1>Book A</h1>", "Book A"), ("<h1>Book B</h1>", "Book B")]
```

---

Test:

```python
@pytest.mark.parametrize("html,title", cases)
def test_parser(html, title):

    assert parse_title(html) == title
```

---

Một parser.

Test nhiều website.

---

# Phần X

# Parametrize Login Validator

Ví dụ:

```python
def validate_password(password):

    return len(password) >= 8
```

---

Test:

```python
@pytest.mark.parametrize(
    "password,result", [("123", False), ("12345678", True), ("python123", True)]
)
def test_password(password, result):

    assert validate_password(password) == result
```

---

# Phần XI

# Parametrize với nhiều decorator

Có thể:

```python
@pytest.mark.parametrize("username", ["admin", "guest"])
@pytest.mark.parametrize("password", ["123", "456"])
def test_login(username, password): ...
```

---

Pytest tạo:

```text
admin + 123

admin + 456

guest + 123

guest + 456
```

Tổng:

```text
2 x 2 = 4 test
```

---

# Phần XII

# Skip từng trường hợp

Ví dụ:

```python
@pytest.mark.parametrize(
    "browser", ["chrome", pytest.param("ie", marks=pytest.mark.skip)]
)
def test_browser(browser): ...
```

---

# Phần XIII

# Parametrize với dữ liệu bên ngoài

Ví dụ:

CSV:

```text
username,password
alice,123
bob,456
```

Đọc:

```python
cases = load_csv()
```

Sau đó:

```python
@pytest.mark.parametrize(
    "user",
    cases
)
```

---

Ứng dụng:

* Kiểm thử API.
* Kiểm thử import/export.
* Kiểm thử dữ liệu lớn.

---

# Phần XIV

# Sai lầm khi dùng Parametrize

## Sai

Một test:

```python
10000 cases
```

Khó đọc.

---

Nên chia:

```text
normal cases

error cases

boundary cases
```

---

## Sai

Dữ liệu không có ý nghĩa:

```python
(123, "abc", 456)
```

Người khác không hiểu.

---

## Sai

Không đặt ID.

CI báo:

```text
test_xxx[abc123]
```

khó tìm.

---

# Phần XV

# Boundary Testing

Parametrize rất phù hợp để test biên.

Ví dụ:

Tuổi:

```python
def valid_age(age):

    return 18 <= age <= 60
```

---

Test:

```python
@pytest.mark.parametrize(
    "age,result", [(17, False), (18, True), (30, True), (60, True), (61, False)]
)
def test_age(age, result):

    assert valid_age(age) == result
```

---

Đây là kỹ thuật QA chuyên nghiệp.

---

# Phần XVI

# Mini Project

## Test Parser Crawler bằng Parametrize

Áp dụng vào hệ thống cào truyện.

Cấu trúc:

```
crawler/

├── parsers/

│   └── chapter_parser.py

└── tests/

    └── test_parser.py
```

---

Parser:

```python
parse_chapter(html)
```

Trả về:

```python
{"title": "...", "content": "..."}
```

---

Viết test:

## Case 1

HTML chuẩn.

---

## Case 2

Thiếu title.

---

## Case 3

Thiếu content.

---

## Case 4

HTML lỗi.

---

Dùng:

```python
@pytest.mark.parametrize()
```

để kiểm thử tất cả.

---

# Phần XVII

# Bài tập

## Bài 1

Test:

```python
is_prime()
```

với:

* 1
* 2
* 3
* 4
* 10
* 11

---

## Bài 2

Test:

```python
validate_email()
```

---

## Bài 3

Test:

```python
calculate_discount()
```

với nhiều mức giá.

---

## Bài 4

Test:

```python
BookRepository.search()
```

với nhiều keyword.

---

## Bài 5

Test:

```python
HTMLParser
```

với nhiều HTML.

---

# Tổng kết buổi 31

Hôm nay bạn đã học:

✅ Data Driven Testing
✅ `pytest.mark.parametrize`
✅ Nhiều tham số
✅ Test Exception
✅ Test ID
✅ Fixture + Parametrize
✅ Repository Testing
✅ Parser Testing
✅ Boundary Testing
✅ Dynamic Test Cases

---

# Góc lập trình viên chuyên nghiệp

Trong dự án thực tế, một bộ test tốt thường có cấu trúc:

```
tests/

├── unit/

│   ├── test_validator.py

│   ├── test_parser.py

│   └── test_service.py


├── integration/

│   ├── test_repository.py

│   └── test_database.py


└── e2e/

    └── test_workflow.py
```

Trong đó:

* **Fixture** chuẩn bị môi trường.
* **Parametrize** tạo dữ liệu kiểm thử.
* **Mock** cô lập phụ thuộc bên ngoài.

Ba kỹ thuật này kết hợp tạo thành nền tảng của Testing hiện đại trong Python.

---

# Chuẩn bị Buổi 32

Buổi tiếp theo:

# **Pytest (Phần 4) - MonkeyPatch và thay đổi môi trường khi Testing**

Bạn sẽ học:

* MonkeyPatch là gì.
* Khác biệt giữa Mock và MonkeyPatch.
* Thay đổi biến môi trường.
* Patch function.
* Patch attribute.
* Patch file system.
* Patch thời gian.
* Test config.
* Test API key.
* Test ứng dụng production mà không ảnh hưởng hệ thống thật.

Đây là kỹ thuật cực kỳ quan trọng khi kiểm thử các ứng dụng Python thực tế.
