**Pytest** và **Unittest** là hai khung kiểm thử (testing framework) phổ biến nhất trong Python. **Unittest** là thư viện có sẵn (built-in) theo phong cách hướng đối tượng, trong khi **Pytest** là thư viện bên thứ ba (cần cài đặt) với cú pháp hiện đại, ngắn gọn và linh hoạt hơn.

---

## 1. Bảng so sánh chi tiết

| Tiêu chí | Unittest | Pytest |
| --- | --- | --- |
| **Nguồn gốc** | Built-in (có sẵn trong Python) | Thư viện bên thứ ba (`pip install pytest`) |
| **Cú pháp** | Yêu cầu tạo Class kế thừa `unittest.TestCase` | Dùng hàm (function) thông thường, không bắt buộc dùng Class |
| **Câu lệnh Assert** | Sử dụng các hàm riêng: `self.assertEqual()`, `self.assertTrue()`... | Sử dụng câu lệnh `assert` tiêu chuẩn của Python: `assert a == b` |
| **Chuẩn bị môi trường (Setup/Teardown)** | Dùng hàm `setUp()` / `tearDown()` | Sử dụng `Fixtures` linh hoạt và tái sử dụng dễ dàng |
| **Kiểm thử tham số hóa (Parameterized testing)** | Phức tạp, cần cài thêm thư viện phụ | Rất dễ dàng với decorator `@pytest.mark.parametrize` |
| **Báo lỗi (Output)** | Báo lỗi cơ bản, ít chi tiết | Báo lỗi rất chi tiết (hiển thị rõ giá trị biến khi xảy ra lỗi) |
| **Khả năng mở rộng** | Hạn chế | Hệ sinh thái plugin phong phú (như `pytest-cov`, `pytest-xdist`...) |
| **Chạy test của framework khác** | Chỉ chạy được bài test viết bằng unittest | Chạy được cả test của **Pytest**, **Unittest** và **Nose** |

---

## 2. So sánh qua ví dụ mã nguồn

### Kiểm tra tính năng đơn giản

* **Unittest:**
```python
import unittest


class TestMath(unittest.TestCase):
    def test_add(self):
        self.assertEqual(1 + 2, 3)
        self.assertTrue(5 > 2)
```


* **Pytest:**
```python
def test_add():
    assert 1 + 2 == 3
    assert 5 > 2
```



### Kiểm thử nhiều tập dữ liệu (Parameterized Test)

* **Pytest (Rất gọn nhẹ):**
```python
import pytest


@pytest.mark.parametrize("a, b, expected", [(1, 2, 3), (5, 5, 10), (-1, 1, 0)])
def test_add_multiple(a, b, expected):
    assert a + b == expected
```



---

## 3. Bạn nên chọn cái nào?

### Nên dùng **Pytest** khi:

* Bắt đầu một dự án mới (từ nhỏ, vừa đến các hệ thống lớn).
* Muốn viết code test nhanh, ngắn gọn, dễ đọc và dễ bảo trì.
* Cần các tính năng nâng cao như **Fixtures**, **Parametrization** hoặc đo độ bao phủ mã nguồn (**Code Coverage**).
* Đang làm việc trong môi trường dự án thực tế tại các công ty (Pytest là chuẩn mực thực tế - *de facto standard* - trong ngành hiện nay).

### Nên dùng **Unittest** khi:

* Đang làm việc trong môi trường hạn chế, **không được phép cài đặt thư viện bên thứ ba** (chỉ sử dụng Python Standard Library).
* Bảo trì các dự án Python cũ (legacy project) đã được viết hoàn toàn bằng `unittest`.
* Đội ngũ phát triển đã quen thuộc với phong cách kiểm thử JUnit từ Java.

> **Mẹo nhỏ:** Bạn có thể bắt đầu viết test bằng cú pháp `unittest` và dùng `pytest` để chạy chúng, vì Pytest hỗ trợ chạy trực tiếp các tệp test của Unittest mà không cần sửa đổi mã nguồn.