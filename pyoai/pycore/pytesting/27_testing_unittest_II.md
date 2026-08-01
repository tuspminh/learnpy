# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 27: Testing (Phần 2) - `unittest` nâng cao: Test Suite, Test Loader, `subTest`, Skip, Code Coverage

> **Mục tiêu của buổi học hôm nay là giúp bạn chuyển từ việc "biết viết test" sang "biết tổ chức một hệ thống test chuyên nghiệp".**

Đây cũng là cách các dự án Python lớn như Django, CPython, SQLAlchemy và Requests tổ chức kiểm thử.

---

# Roadmap phần Testing

```text
Phần I. unittest cơ bản
✓ Buổi 26. Unit Test
✓ Buổi 27. unittest nâng cao

Phần II. Mocking
Buổi 28. unittest.mock

Phần III. pytest
Buổi 29. pytest cơ bản
Buổi 30. Fixture
Buổi 31. Parametrize
Buổi 32. MonkeyPatch
Buổi 33. Mock trong pytest

Phần IV. Testing nâng cao
Buổi 34. Integration Test
Buổi 35. API Testing
Buổi 36. Database Testing
Buổi 37. Async Testing
Buổi 38. GUI Testing (PySide6)
Buổi 39. Coverage & CI/CD

Phần V. Dự án thực tế
Buổi 40. Thiết kế hệ thống Testing hoàn chỉnh
```

---

# Phần I. Ôn tập

Buổi trước chúng ta đã học:

* `TestCase`
* `assertEqual`
* `assertRaises`
* `setUp`
* `tearDown`
* AAA Pattern

Hôm nay sẽ học cách quản lý **hàng trăm hoặc hàng nghìn test**.

---

# Phần II. `setUpClass()` và `tearDownClass()`

## Vấn đề

Giả sử bạn có:

```python
class TestDatabase(unittest.TestCase):
```

Mỗi test:

```python
setUp()

↓

Connect Database
```

Có:

```text
1000 test
```

↓

Kết nối:

```text
1000 lần
```

Rất chậm.

---

## Giải pháp

```python
import unittest


class TestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Connect database")

    @classmethod
    def tearDownClass(cls):
        print("Close database")

    def test_a(self):
        pass

    def test_b(self):
        pass
```

Kết quả:

```text
Connect database

test_a

test_b

Close database
```

Chỉ kết nối **một lần**.

---

## So sánh

| Hàm               | Gọi khi nào            |
| ----------------- | ---------------------- |
| `setUp()`         | Trước mỗi test         |
| `tearDown()`      | Sau mỗi test           |
| `setUpClass()`    | Một lần trước cả class |
| `tearDownClass()` | Một lần sau cả class   |

---

# Phần III. `subTest()`

Đây là tính năng rất mạnh nhưng ít người biết.

Ví dụ:

```python
def square(x):
    return x * x
```

Thông thường:

```python
def test_square1(): ...


def test_square2(): ...


def test_square3(): ...
```

Rất dài.

---

## Dùng `subTest`

```python
import unittest


class TestSquare(unittest.TestCase):
    def test_square(self):

        cases = [(2, 4), (3, 9), (5, 25), (10, 100)]

        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(square(value), expected)
```

---

## Nếu một test lỗi

Ví dụ:

```python
(5, 26)
```

Kết quả:

```text
FAIL: value=5
```

Nhưng:

```text
2

3

10
```

vẫn tiếp tục chạy.

---

## Khi nào dùng?

Rất phù hợp với:

* Hàm tính toán.
* Kiểm tra dữ liệu.
* Parser.
* Validator.
* Repository.

---

# Phần IV. Skip Test

Có khi:

Một test:

```text
Chưa hoàn thành.
```

Không muốn chạy.

---

## `@skip`

```python
import unittest


class TestUser(unittest.TestCase):
    @unittest.skip("Not implemented")
    def test_login(self):

        pass
```

Kết quả:

```text
skipped
```

---

## `skipIf`

```python
import sys
import unittest


class TestOS(unittest.TestCase):
    @unittest.skipIf(sys.platform == "win32", "Windows only")
    def test_linux(self): ...
```

---

## `skipUnless`

```python
@unittest.skipUnless(
    sys.platform == "linux",
    "Linux required"
)
```

---

# Phần V. `expectedFailure`

Giả sử:

Có bug.

Bạn biết.

Chưa sửa.

```python
@unittest.expectedFailure
def test_bug(): ...
```

Nếu:

Fail

↓

Python ghi:

```text
expected failure
```

Không làm toàn bộ bộ test thất bại.

---

# Phần VI. Test Suite

Giả sử:

Có:

```text
2000 test
```

Không muốn:

Chạy tất cả.

Muốn:

```text
Payment

+

User
```

---

## Tạo Test Suite

```python
import unittest

suite = unittest.TestSuite()
```

---

Thêm:

```python
suite.addTest(TestUser("test_login"))
```

Hoặc:

```python
suite.addTest(TestWallet("test_deposit"))
```

---

Chạy:

```python
runner = unittest.TextTestRunner()

runner.run(suite)
```

---

# Ví dụ

```python
import unittest


class TestMath(unittest.TestCase):
    def test_add(self):
        self.assertEqual(2 + 3, 5)

    def test_subtract(self):
        self.assertEqual(5 - 3, 2)


suite = unittest.TestSuite()

suite.addTest(TestMath("test_add"))

runner = unittest.TextTestRunner()

runner.run(suite)
```

---

# Phần VII. Test Loader

Không muốn thêm:

```python
suite.addTest(...)
```

1000 lần.

Python có:

```python
loader = unittest.TestLoader()
```

---

Ví dụ:

```python
suite = loader.loadTestsFromTestCase(TestMath)
```

---

Hoặc:

```python
suite = loader.discover("tests")
```

Python tự tìm:

```text
tests/
```

---

# Phần VIII. Test Runner

Runner:

↓

Thực thi Test.

```python
runner = unittest.TextTestRunner(verbosity=2)
```

Kết quả:

```text
test_login ... ok

test_logout ... ok
```

---

## verbosity

```text
0
```

Ít.

```text
1
```

Mặc định.

```text
2
```

Chi tiết.

---

# Phần IX. Code Coverage

Một sai lầm:

```text
100 test
```

↓

Nhưng:

Chỉ chạy:

```text
10%
```

Code.

---

Ví dụ:

```python
def check_age(age):

    if age >= 18:
        return True

    return False
```

Test:

```python
check_age(20)
```

Bạn chưa test:

```python
check_age(10)
```

Nhánh:

```python
False
```

Chưa được kiểm tra.

---

## Coverage là gì?

Là tỷ lệ mã nguồn đã được test thực thi.

Ví dụ:

```text
Coverage

95%
```

Không có nghĩa:

95% đúng.

Mà:

95% dòng code đã chạy trong test.

---

## Công cụ

Phổ biến nhất:

```bash
pip install coverage
```

Chạy:

```bash
coverage run -m unittest discover
```

Báo cáo:

```bash
coverage report
```

HTML:

```bash
coverage html
```

Sinh:

```text
htmlcov/
```

Mở:

```text
index.html
```

Bạn sẽ thấy:

* Dòng xanh: đã test.
* Dòng đỏ: chưa test.

---

# Phần X. Test Discovery

Python tự tìm:

```text
tests/
```

Có tên:

```text
test_*.py
```

Ví dụ:

```text
tests/

    test_user.py

    test_wallet.py

    test_database.py
```

---

# Phần XI. Tổ chức dự án

```text
project/

    app/

        models/

        services/

        repositories/

    tests/

        models/

        services/

        repositories/
```

Rất dễ quản lý.

---

# Phần XII. AAA + subTest

Ví dụ.

```python
class TestDiscount(unittest.TestCase):
    def test_discount(self):

        cases = [(100, 10, 90), (200, 20, 160), (300, 50, 150)]

        for price, percent, expected in cases:
            with self.subTest(price=price):
                # Arrange

                ...

                # Act

                ...

                # Assert

                self.assertEqual(...)
```

Đây là cách viết rất chuyên nghiệp.

---

# Phần XIII. Những lỗi phổ biến

## Sai

```python
sleep(5)
```

Trong test.

---

## Sai

Test phụ thuộc Internet.

---

## Sai

Test phụ thuộc thời gian hệ thống.

---

## Sai

Test dùng Database thật.

(Unit Test nên dùng dữ liệu giả hoặc mock.)

---

## Sai

Một test:

```python
test_everything()
```

---

## Sai

Không dùng:

```python
subTest()
```

Khi test nhiều bộ dữ liệu.

---

# Phần XIV. Thực hành

## Bài 1

Viết:

```python
setUpClass()
```

---

## Bài 2

Viết:

```python
tearDownClass()
```

---

## Bài 3

Viết:

```python
subTest()
```

↓

10 bộ dữ liệu.

---

## Bài 4

Viết:

```python
skipIf()
```

---

## Bài 5

Tạo:

```python
TestSuite
```

↓

Chạy:

```text
Wallet

+

Calculator
```

---

## Bài 6

Dùng:

```bash
coverage
```

↓

Đo:

Coverage.

---

# Mini Project

# Unit Test cho Ứng dụng Quản lý Truyện

Áp dụng vào dự án **crawler truyện** mà bạn đang học.

```text
story_app/
│
├── app/
│   ├── models/
│   ├── services/
│   ├── repositories/
│   ├── crawlers/
│   └── parsers/
│
└── tests/
    ├── test_models.py
    ├── test_services.py
    ├── test_repositories.py
    ├── test_parsers.py
    └── test_crawlers.py
```

### Yêu cầu

* Dùng `setUpClass()` để khởi tạo dữ liệu dùng chung.
* Dùng `subTest()` để kiểm tra nhiều URL hoặc nhiều định dạng HTML.
* Dùng `TestSuite` để chỉ chạy nhóm test của `parser`.
* Đo Code Coverage để xem parser đã được kiểm thử đầy đủ chưa.
* Các test không được gọi mạng thật hay cơ sở dữ liệu thật (chúng ta sẽ học cách dùng **Mock** ở buổi sau).

---

# Tổng kết buổi 27

Hôm nay bạn đã học:

* ✅ `setUpClass()`
* ✅ `tearDownClass()`
* ✅ `subTest()`
* ✅ `skip`
* ✅ `skipIf`
* ✅ `skipUnless`
* ✅ `expectedFailure`
* ✅ `TestSuite`
* ✅ `TestLoader`
* ✅ `TextTestRunner`
* ✅ Code Coverage
* ✅ Tổ chức bộ test chuyên nghiệp

---

# Góc lập trình viên chuyên nghiệp

Trong các dự án lớn, một Unit Test **không nên**:

* Gọi API thật.
* Ghi dữ liệu vào cơ sở dữ liệu thật.
* Gửi email thật.
* Gửi HTTP request thật.
* Đọc file cấu hình của môi trường production.

Thay vào đó, Unit Test cần **cô lập (isolate)** đối tượng đang kiểm thử. Để làm được điều này, chúng ta sẽ sử dụng **Mock**.

Ví dụ, khi kiểm thử một `BookService`, bạn không cần SQLite thật. Thay vào đó, bạn sẽ thay `BookRepository` bằng một đối tượng giả (Mock) để kiểm tra:

* `BookService` có gọi đúng phương thức của Repository không.
* Có truyền đúng tham số không.
* Có xử lý đúng kết quả trả về không.
* Có xử lý đúng ngoại lệ từ Repository không.

Đây là nền tảng của **Dependency Injection**, **Clean Architecture** và **Test-Driven Development (TDD)**.

---

# Chuẩn bị cho Buổi 28

Ở **Buổi 28**, chúng ta sẽ học một trong những chủ đề quan trọng nhất của kiểm thử Python:

# **Mocking với `unittest.mock`**

Bạn sẽ học:

* Mock là gì và tại sao phải dùng Mock.
* `Mock` và `MagicMock`.
* `patch()`, `patch.object()`, `patch.dict()`.
* `return_value`.
* `side_effect`.
* `call`, `call_args`, `assert_called_*`.
* Mock HTTP (`requests`), SQLite, Repository, File I/O và thời gian (`datetime`).
* Kiểm thử `Service` trong kiến trúc Repository + Clean Architecture mà không phụ thuộc vào hạ tầng thực tế.

Sau buổi này, bạn sẽ có đủ nền tảng để chuyển sang **pytest**, framework kiểm thử được sử dụng rộng rãi nhất trong cộng đồng Python hiện nay.
