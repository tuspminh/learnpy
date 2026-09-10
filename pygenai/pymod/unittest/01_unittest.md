**Unittest** là thư viện có sẵn (built-in) trong Python dùng để kiểm thử tự động (unit testing) các đoạn mã. Nó giúp bạn đảm bảo từng hàm, từng lớp (class) hoạt động đúng như mong đợi.

---

## 1. Cấu trúc cơ bản của một bài Test

Để viết unittest, bạn cần làm 3 bước:

1. `import unittest`
2. Tạo một class kế thừa từ `unittest.TestCase`
3. Viết các hàm test có tên **bắt đầu bằng từ `test_**`

### Ví dụ minh họa:

Giả sử bạn có tệp `calculator.py` chứa hàm tính toán:

```python
# calculator.py
def add(a, b):
    return a + b


def divide(a, b):
    if b == 0:
        raise ValueError("Không thể chia cho 0")
    return a / b
```

Tạo tệp `test_calculator.py` để viết code kiểm thử:

```python
# test_calculator.py
import unittest
from calculator import add, divide


class TestCalculator(unittest.TestCase):
    def test_add(self):
        # Kiểm tra tính năng cộng
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(-1, 1), 0)

    def test_divide(self):
        # Kiểm tra chia thông thường
        self.assertEqual(divide(6, 2), 3)

        # Kiểm tra chia cho 0 có quăng ra lỗi (exception) hay không
        with self.assertRaises(ValueError):
            divide(10, 0)


if __name__ == "__main__":
    unittest.main()
```

---

## 2. Các phương thức kiểm tra phổ biến (Assert Methods)

Trong `unittest.TestCase`, các câu lệnh `self.assert...` dùng để so sánh kết quả thực tế với kết quả kỳ vọng:

| Phương thức | Ý nghĩa |
| --- | --- |
| `self.assertEqual(a, b)` | Kiểm tra $a == b$ |
| `self.assertNotEqual(a, b)` | Kiểm tra $a \neq b$ |
| `self.assertTrue(x)` | Kiểm tra $x$ có giá trị True |
| `self.assertFalse(x)` | Kiểm tra $x$ có giá trị False |
| `self.assertIn(item, list)` | Kiểm tra `item` có nằm trong `list` hay không |
| `self.assertIsNone(x)` | Kiểm tra $x$ có phải là `None` hay không |
| `self.assertRaises(Error)` | Kiểm tra xem đoạn code có ném ra đúng lỗi mong muốn không |

---

## 3. Thiết lập và dọn dẹp: `setUp` & `tearDown`

Khi kiểm thử các hệ thống phức tạp (như thao tác với cơ sở dữ liệu hoặc tệp tin), bạn thường cần chuẩn bị dữ liệu trước khi test và xóa dữ liệu sau khi test xong.

```python
import unittest


class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Chạy TRƯỚC MỖI hàm test_
        # Dùng để khởi tạo dữ liệu mẫu, mở kết nối DB,...
        self.db_connection = "Connected"

    def tearDown(self):
        # Chạy SAU MỖI hàm test_
        # Dùng để đóng kết nối, xóa file tạm,...
        self.db_connection = "Disconnected"

    def test_query(self):
        self.assertEqual(self.db_connection, "Connected")
```

---

## 4. Cách chạy Unittest từ dòng lệnh (Terminal)

Bạn có thể chạy unittest trực tiếp từ terminal bằng các lệnh sau:

```bash
# Chạy file test cụ thể
python -m unittest test_calculator.py

# Tự động tìm và chạy tất cả các file test (có tên dạng test*.py)
python -m unittest discover

```