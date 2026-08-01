# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 26: Testing (Phần 1) - Unit Testing với `unittest` từ cơ bản đến chuyên nghiệp

> **Đây là một trong những kỹ năng quan trọng nhất của lập trình viên chuyên nghiệp.**

Một lập trình viên mới thường nghĩ:

> "Code chạy là được."

Một lập trình viên chuyên nghiệp nghĩ:

> "Làm sao để chứng minh code luôn chạy đúng sau mỗi lần sửa?"

Câu trả lời là:

> **Testing**

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ:

* Hiểu Testing là gì.
* Hiểu Unit Test.
* Hiểu Integration Test.
* Hiểu Functional Test.
* Thành thạo `unittest`.
* Biết viết Test Case.
* Biết Assertion.
* Hiểu `setUp()` và `tearDown()`.
* Biết tổ chức thư mục test.

---

# Phần I. Vì sao cần Testing?

Giả sử bạn viết hàm:

```python
def add(a, b):
    return a + b
```

Bạn thử:

```python
print(add(2, 3))
```

↓

```text
5
```

Bạn nghĩ:

> Đúng rồi.

---

Một tháng sau.

Bạn sửa:

```python
def add(a, b):
    return a - b
```

Không để ý.

Ứng dụng vẫn chạy.

Nhưng:

```text
2 + 3

↓

-1
```

Nếu không có Test.

↓

Không ai phát hiện.

---

# Testing giống kiểm tra chất lượng

Ví dụ:

Nhà máy sản xuất:

```text
100.000 chai nước
```

Không thể:

Mở từng chai.

↓

Có bộ phận:

```text
QA
```

Kiểm tra.

Testing cũng vậy.

---

# Phần II. Các loại Testing

## Unit Test

Kiểm tra:

> Một hàm.

Ví dụ:

```python
calculate_salary()
```

---

## Integration Test

Kiểm tra:

```text
API

↓

Database

↓

Redis
```

Làm việc cùng nhau.

---

## Functional Test

Kiểm tra:

Toàn bộ chức năng.

Ví dụ:

```text
Login

↓

Dashboard

↓

Logout
```

---

## End-to-End Test

Giống người dùng thật.

Ví dụ:

Mở trình duyệt.

↓

Đăng nhập.

↓

Mua hàng.

↓

Thanh toán.

---

# Chúng ta học gì?

Trong vài buổi tới:

> **Unit Testing**

Đây là nền tảng.

---

# Phần III. unittest

Python có sẵn:

```python
import unittest
```

Không cần cài thêm.

---

Ví dụ đầu tiên

```python
import unittest


def add(a, b):
    return a + b


class TestAdd(unittest.TestCase):
    def test_add(self):

        self.assertEqual(add(2, 3), 5)


if __name__ == "__main__":
    unittest.main()
```

Chạy:

```text
.
```

↓

```text
OK
```

---

# Nếu sai

```python
def add(a, b):
    return a - b
```

↓

```text
FAIL
```

---

# Phần IV. Test Case

Một Test Case:

```python
class TestAdd(unittest.TestCase):
```

Có nhiều:

```python
def test_xxx():
```

Ví dụ:

```python
def test_positive():
```

```python
def test_negative():
```

```python
def test_zero():
```

---

Python tự chạy:

```text
test_
```

---

# Quy tắc đặt tên

Đúng:

```python
test_login()
```

Sai:

```python
login_test()
```

---

# Phần V. Assertion

Assertion là:

> Điều kiện phải đúng.

---

## assertEqual

```python
self.assertEqual(add(2, 3), 5)
```

---

## assertTrue

```python
self.assertTrue(10 > 5)
```

---

## assertFalse

```python
self.assertFalse(3 > 5)
```

---

## assertIsNone

```python
self.assertIsNone(result)
```

---

## assertIsNotNone

```python
self.assertIsNotNone(user)
```

---

## assertIn

```python
self.assertIn("admin", users)
```

---

## assertNotIn

```python
self.assertNotIn("guest", admins)
```

---

## assertGreater

```python
self.assertGreater(score, 80)
```

---

## assertLess

```python
self.assertLess(age, 60)
```

---

## assertRaises

Kiểm tra Exception.

```python
with self.assertRaises(ZeroDivisionError):
    divide(10, 0)
```

---

# Phần VI. setUp()

Giả sử:

```python
wallet = Wallet()
```

Phải tạo:

10 lần.

Không nên.

---

Dùng:

```python
def setUp(self):

    self.wallet = Wallet()
```

Python gọi:

Trước mỗi test.

---

Ví dụ

```python
class TestWallet(unittest.TestCase):
    def setUp(self):

        self.wallet = Wallet()
```

Sau đó:

```python
self.wallet
```

Dùng mọi nơi.

---

# tearDown()

Sau mỗi test.

Ví dụ:

Đóng:

* File
* Database
* Socket

```python
def tearDown(self):

    self.db.close()
```

---

# Thứ tự

```text
setUp()

↓

test

↓

tearDown()

↓

setUp()

↓

test

↓

tearDown()
```

---

# Phần VII. Ví dụ Wallet

```python
class Wallet:
    def __init__(self):

        self.balance = 100

    def deposit(self, amount):

        self.balance += amount

    def withdraw(self, amount):

        self.balance -= amount
```

Test:

```python
class TestWallet(unittest.TestCase):
    def setUp(self):

        self.wallet = Wallet()

    def test_deposit(self):

        self.wallet.deposit(50)

        self.assertEqual(self.wallet.balance, 150)

    def test_withdraw(self):

        self.wallet.withdraw(30)

        self.assertEqual(self.wallet.balance, 70)
```

---

# Phần VIII. assertRaises

Ví dụ:

```python
class Wallet:
    def withdraw(self, amount):

        if amount > self.balance:
            raise ValueError
```

Test:

```python
def test_not_enough_money(self):

    with self.assertRaises(ValueError):
        self.wallet.withdraw(1000)
```

---

# Phần IX. Test Organization

Một dự án.

```text
project/

    app/

    tests/
```

Ví dụ:

```text
project/

│

├── app/

│      wallet.py

│      user.py

│

└── tests/

       test_wallet.py

       test_user.py
```

Đây là chuẩn.

---

# Phần X. Chạy Test

Chạy:

```bash
python -m unittest
```

Hoặc:

```bash
python -m unittest discover
```

Python sẽ tự tìm:

```text
test*
```

---

# Chạy file

```bash
python -m unittest test_wallet.py
```

---

# Chạy class

```bash
python -m unittest test_wallet.TestWallet
```

---

# Chạy method

```bash
python -m unittest test_wallet.TestWallet.test_deposit
```

---

# Phần XI. Test độc lập

Sai.

```python
def test_a():

    tạo dữ liệu
```

↓

```python
def test_b():

    dùng dữ liệu test_a
```

Không nên.

Mỗi test:

Độc lập.

---

# Phần XII. Một test chỉ kiểm tra một việc

Sai.

```python
test_everything()
```

Đúng.

```python
test_login_success()
```

```python
test_login_wrong_password()
```

```python
test_login_empty_password()
```

---

# Phần XIII. AAA Pattern

Professional.

```text
Arrange

↓

Act

↓

Assert
```

Ví dụ.

```python
def test_deposit(self):

    # Arrange
    wallet = Wallet()

    # Act
    wallet.deposit(50)

    # Assert
    self.assertEqual(wallet.balance, 150)
```

Đây là cách viết được khuyến nghị.

---

# Phần XIV. Những lỗi phổ biến

## Sai

Một test:

500 dòng.

---

## Sai

Test phụ thuộc nhau.

---

## Sai

Test dùng Database thật.

(Unit Test nên tránh phụ thuộc bên ngoài.)

---

## Sai

Không kiểm tra Exception.

---

## Sai

Một test:

10 assert.

Nên chia nhỏ.

---

# Phần XV. Bài tập

## Bài 1

Viết test:

```python
add()
```

---

## Bài 2

Viết test:

```python
subtract()
```

---

## Bài 3

Viết:

```python
Wallet
```

↓

Test:

```text
deposit

withdraw

balance
```

---

## Bài 4

Viết:

```python
Calculator
```

↓

Test:

```text
+

-

*

/
```

---

## Bài 5

Test:

```python
safe_divide()
```

↓

Exception.

---

## Bài 6

Viết:

```python
BankAccount
```

↓

Test:

* Deposit
* Withdraw
* Overdraw
* Invalid Amount

---

# Mini Project

# Viết Unit Test cho Repository

Đây là ví dụ gần với các dự án bạn đã học về **Repository Pattern**, **Clean Architecture** và **DDD**.

Cấu trúc:

```text
project/
│
├── app/
│   ├── models/
│   │   └── book.py
│   ├── repositories/
│   │   └── book_repository.py
│   └── services/
│       └── book_service.py
│
└── tests/
    ├── test_book_repository.py
    └── test_book_service.py
```

### `BookRepository`

Các phương thức:

* `add(book)`
* `get_by_id(book_id)`
* `update(book)`
* `delete(book_id)`

### Yêu cầu kiểm thử

* Thêm sách thành công.
* Không tìm thấy sách.
* Cập nhật đúng dữ liệu.
* Xóa thành công.
* Xóa một sách không tồn tại.

Lưu ý:

* Với Unit Test, hãy dùng **Repository trong bộ nhớ (InMemory Repository)** thay vì SQLite thật.
* Mỗi test phải độc lập và khởi tạo dữ liệu riêng trong `setUp()`.

---

# Tổng kết buổi 26

Hôm nay bạn đã học:

* ✅ Testing là gì.
* ✅ Unit Test.
* ✅ Integration Test.
* ✅ Functional Test.
* ✅ `unittest`.
* ✅ `TestCase`.
* ✅ Assertion.
* ✅ `setUp()`.
* ✅ `tearDown()`.
* ✅ `assertRaises()`.
* ✅ AAA Pattern.
* ✅ Tổ chức thư mục `tests/`.

---

# Góc lập trình viên chuyên nghiệp

Một sai lầm phổ biến là chỉ kiểm thử **đầu vào hợp lệ**.

Ví dụ:

```python
def divide(a, b):
    return a / b
```

Nhiều người chỉ test:

```python
divide(10, 2)
```

Nhưng một bộ Unit Test tốt cần bao phủ:

* Giá trị bình thường.
* Giá trị biên (boundary values).
* Giá trị rỗng (`None`, chuỗi rỗng... nếu phù hợp).
* Đầu vào không hợp lệ.
* Ngoại lệ (`ZeroDivisionError`, `ValueError`...).

Đây là tư duy giúp phần mềm ổn định khi phát triển lâu dài.

---

# Chuẩn bị cho Buổi 27

Ở **Buổi 27**, chúng ta sẽ học **Testing nâng cao** với các chủ đề mà lập trình viên Python chuyên nghiệp sử dụng hằng ngày:

* `setUpClass()` và `tearDownClass()`.
* `subTest()`.
* `skip`, `skipIf`, `expectedFailure`.
* Test Suite.
* Test Loader.
* Test Runner.
* Code Coverage.
* Tổ chức bộ test cho các dự án nhiều module.

Sau buổi đó, chúng ta sẽ chuyển sang **`pytest`** – framework kiểm thử mạnh mẽ và phổ biến nhất trong hệ sinh thái Python hiện nay, cùng với **Mock**, **Fixture**, **Parametrize**, và kiểm thử cho FastAPI, PySide6, Scrapy, Celery và các dự án crawler thực tế.
