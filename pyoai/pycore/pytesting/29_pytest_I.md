# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 29: Pytest (Phần 1) – Làm chủ `pytest` từ cơ bản đến chuyên nghiệp

> **Nếu `unittest` là thư viện kiểm thử chuẩn của Python, thì `pytest` là framework kiểm thử được cộng đồng Python yêu thích nhất.**

Hiện nay, phần lớn các dự án sử dụng:

* FastAPI
* Flask
* Django
* SQLAlchemy
* Requests
* Pandas
* Pydantic
* Celery
* Scrapy
* LangChain
* Hay các dự án AI, Machine Learning

đều sử dụng **pytest**.

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ:

* Hiểu tại sao nên dùng `pytest`.
* Cài đặt và chạy `pytest`.
* Viết test đầu tiên.
* Hiểu cơ chế Discovery.
* Hiểu Assertion thông minh.
* Tổ chức thư mục kiểm thử.
* So sánh `pytest` và `unittest`.
* Viết Unit Test theo phong cách hiện đại.

---

# Roadmap phần Pytest

```text
Phần I. Pytest cơ bản
✓ Buổi 29

Phần II. Fixture
Buổi 30

Phần III. Parametrize
Buổi 31

Phần IV. MonkeyPatch
Buổi 32

Phần V. Mock
Buổi 33

Phần VI. Testing nâng cao
Buổi 34 -> 40
```

---

# Phần I. Vì sao pytest ra đời?

Hãy xem một Unit Test bằng `unittest`.

```python
import unittest


def add(a, b):
    return a + b


class TestMath(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)


if __name__ == "__main__":
    unittest.main()
```

Khá dài.

---

Pytest:

```python
def add(a, b):
    return a + b


def test_add():
    assert add(2, 3) == 5
```

Xong.

Không cần:

* TestCase
* main()
* assertEqual()

Đây là lý do pytest rất phổ biến.

---

# Phần II. Cài đặt

```bash
pip install pytest
```

Kiểm tra:

```bash
pytest --version
```

Ví dụ:

```text
pytest 8.x.x
```

---

# Phần III. Discovery

Pytest tự tìm:

```text
test_*.py

*_test.py
```

Ví dụ:

```text
tests/

    test_math.py

    test_user.py
```

Hoặc:

```text
math_test.py
```

đều được.

---

Tên hàm:

```python
def test_add():
```

Phải bắt đầu bằng:

```text
test_
```

---

# Phần IV. Test đầu tiên

math_utils.py

```python
def add(a, b):
    return a + b
```

---

test_math.py

```python
from math_utils import add


def test_add():

    assert add(2, 3) == 5
```

---

Chạy:

```bash
pytest
```

↓

```text
1 passed
```

---

# Nếu sai

```python
assert add(2, 3) == 6
```

Pytest báo:

```text
E

assert 5 == 6
```

Không cần:

```python
assertEqual()
```

---

# Phần V. Smart Assertion

Đây là điểm cực mạnh.

Ví dụ.

```python
assert 2 + 3 == 6
```

Pytest tự phân tích.

Kết quả.

```text
2 + 3

=

5
```

↓

```text
Expected

6
```

Bạn không cần viết:

```python
self.assertEqual(...)
```

---

Ví dụ.

```python
user = {"name": "Alice"}
```

```python
assert user["name"] == "Bob"
```

Pytest.

↓

```text
Alice != Bob
```

Rất trực quan.

---

# Phần VI. Exception

Trong unittest.

```python
with self.assertRaises(...)
```

---

Pytest.

```python
import pytest


def divide(a, b):
    return a / b


def test_zero():

    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

---

# Phần VII. Nhiều Test

```python
def test_add(): ...
```

```python
def test_subtract(): ...
```

```python
def test_divide(): ...
```

Không cần class.

---

# Có nên dùng Class?

Có thể.

```python
class TestMath:
    def test_add(self): ...
```

Không cần:

```python
unittest.TestCase
```

---

# Phần VIII. Chạy Test

Chạy toàn bộ.

```bash
pytest
```

---

Chạy file.

```bash
pytest test_math.py
```

---

Chạy hàm.

```bash
pytest test_math.py::test_add
```

---

Chạy class.

```bash
pytest test_math.py::TestMath
```

---

# Chế độ chi tiết

```bash
pytest -v
```

↓

```text
PASSED

FAILED
```

Rõ ràng.

---

# Phần IX. Tổ chức dự án

```text
project/

    app/

        models/

        services/

        repositories/

    tests/

        test_models.py

        test_services.py

        test_repositories.py
```

Đây là cấu trúc phổ biến.

---

# Phần X. Test theo AAA

```python
def test_deposit():

    # Arrange

    wallet = Wallet()

    # Act

    wallet.deposit(100)

    # Assert

    assert wallet.balance == 200
```

Đây vẫn là cách viết nên dùng.

---

# Phần XI. Chạy theo từ khóa

Ví dụ.

```bash
pytest -k wallet
```

↓

Chỉ chạy:

```text
wallet
```

---

Ví dụ.

```bash
pytest -k login
```

↓

Chỉ chạy:

```text
login
```

---

# Phần XII. Dừng khi gặp lỗi

```bash
pytest -x
```

↓

Lỗi đầu tiên.

↓

Dừng.

---

# Chạy N lỗi đầu

```bash
pytest --maxfail=3
```

↓

Dừng sau:

3 lỗi.

---

# Phần XIII. Xem print()

Thông thường.

```python
print("hello")
```

Pytest ẩn.

Muốn xem.

```bash
pytest -s
```

↓

Hiện.

---

# Phần XIV. Marker

Có thể đánh dấu.

Ví dụ.

```python
import pytest


@pytest.mark.slow
def test_download(): ...
```

Chạy.

```bash
pytest -m slow
```

Hoặc.

```bash
pytest -m "not slow"
```

---

# Phần XV. Skip

```python
import pytest


@pytest.mark.skip
def test_a(): ...
```

---

Có điều kiện.

```python
@pytest.mark.skipif(
    True,

    reason="Not ready"
)
```

---

# Phần XVI. XFail

Biết:

Có bug.

```python
@pytest.mark.xfail
def test_bug(): ...
```

↓

Không làm hỏng build.

---

# Phần XVII. unittest vs pytest

| unittest       | pytest                 |
| -------------- | ---------------------- |
| Có sẵn         | Cài thêm               |
| Cần TestCase   | Không cần              |
| assertEqual    | assert                 |
| Nhiều mã hơn   | Ngắn gọn               |
| Hỗ trợ tốt OOP | Hỗ trợ cả hàm và class |
| Ít plugin      | Rất nhiều plugin       |
| Chuẩn thư viện | Chuẩn cộng đồng        |

---

# Phần XVIII. Khi nào dùng unittest?

Khi:

* Không muốn cài thư viện.
* Làm việc trong môi trường bị hạn chế.
* Dự án cũ đã dùng unittest.

---

# Khi nào dùng pytest?

Hầu hết các dự án mới.

Đặc biệt:

* FastAPI
* Flask
* Django
* AI
* Data Science
* Automation
* Scrapy
* PySide6

---

# Phần XIX. Những lỗi phổ biến

## Sai

```python
assert True
```

Không có ý nghĩa.

---

## Sai

Một test.

```python
500 dòng
```

---

## Sai

Một test.

10 assert.

---

## Sai

Đặt tên.

```python
abc.py
```

Không có:

```text
test_
```

↓

Pytest không tìm.

---

# Phần XX. Thực hành

## Bài 1

Viết.

```python
test_add()
```

---

## Bài 2

Viết.

```python
test_subtract()
```

---

## Bài 3

Test.

```python
Wallet
```

---

## Bài 4

Test.

```python
Calculator
```

---

## Bài 5

Test.

```python
divide()
```

↓

Exception.

---

## Bài 6

Chạy.

```bash
pytest -v
```

---

# Mini Project

# Chuyển từ unittest sang pytest

Chúng ta đã có một `BookService` ở các buổi trước. Hãy chuyển bộ test sang `pytest`.

Cấu trúc:

```text
book_store/
│
├── app/
│   ├── services/
│   │   └── book_service.py
│   ├── repositories/
│   │   └── memory_repository.py
│   └── models/
│       └── book.py
│
└── tests/
    ├── test_book_service.py
    └── test_memory_repository.py
```

Yêu cầu:

* Viết test theo phong cách hàm (`test_*`).
* Sử dụng `assert` thay cho `assertEqual`.
* Kiểm tra:

  * Thêm sách.
  * Tìm sách.
  * Cập nhật sách.
  * Xóa sách.
  * Không tìm thấy sách.

Ở buổi sau, chúng ta sẽ thay việc khởi tạo dữ liệu lặp đi lặp lại bằng **Fixture**.

---

# Tổng kết buổi 29

Hôm nay bạn đã học:

* ✅ Cài đặt `pytest`
* ✅ Discovery
* ✅ Assertion thông minh
* ✅ `pytest.raises`
* ✅ Chạy test
* ✅ `-v`
* ✅ `-k`
* ✅ `-x`
* ✅ `--maxfail`
* ✅ `-s`
* ✅ Marker
* ✅ Skip
* ✅ XFail
* ✅ So sánh `pytest` và `unittest`

---

# Góc lập trình viên chuyên nghiệp

Nếu bạn đọc mã nguồn của các dự án lớn, bạn sẽ thấy một mô hình rất phổ biến:

```text
tests/
│
├── unit/
├── integration/
├── functional/
├── performance/
└── e2e/
```

Mỗi loại test có mục tiêu khác nhau:

| Loại        | Mục tiêu                           | Chạy thường xuyên       |
| ----------- | ---------------------------------- | ----------------------- |
| Unit        | Kiểm tra từng hàm/lớp              | ✅ Mỗi lần commit        |
| Integration | Kiểm tra nhiều thành phần phối hợp | ✅ Trước khi merge       |
| Functional  | Kiểm tra chức năng nghiệp vụ       | ✅ Trên CI               |
| Performance | Đo hiệu năng                       | Theo đợt                |
| End-to-End  | Mô phỏng người dùng thật           | Theo pipeline phát hành |

Trong các dự án crawler, FastAPI hoặc PySide6, bạn nên ưu tiên viết **Unit Test** trước, sau đó mới bổ sung Integration Test.

---

# Chuẩn bị cho Buổi 30

Ở **Buổi 30**, chúng ta sẽ học một trong những tính năng mạnh nhất của `pytest`:

# **Fixture**

Bạn sẽ học:

* Fixture là gì.
* Vì sao Fixture tốt hơn `setUp()`.
* Scope (`function`, `class`, `module`, `session`).
* `yield` Fixture.
* `autouse=True`.
* Chia sẻ Fixture bằng `conftest.py`.
* Thiết kế Fixture cho Repository, Service, SQLite, HTTP Client và ứng dụng crawler.

Sau buổi này, bạn sẽ thấy vì sao hầu hết các dự án Python hiện đại đều coi **Fixture** là nền tảng của toàn bộ hệ thống kiểm thử.
