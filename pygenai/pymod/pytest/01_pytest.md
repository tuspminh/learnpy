Chào bạn! Chào mừng bạn đến với **pytest** — framework kiểm thử (testing) phổ biến và mạnh mẽ nhất trong hệ sinh thái Python.

So với thư viện mặc định `unittest`, `pytest` viết ngắn gọn hơn nhiều nhờ cơ chế tự phát hiện bài test và câu lệnh `assert` nguyên bản của Python.

---

### 1. Cài đặt

Mở terminal và cài đặt pytest qua pip:

```bash
pip install pytest

```

---

### 2. Viết bài test đầu tiên

Pytest tự động tìm các file có dạng `test_*.py` hoặc `*_test.py` và chạy các hàm bắt đầu bằng từ khóa `test_`.

Tạo một file tên là `test_math.py`:

```python
# Hàm cần kiểm thử (thường sẽ import từ module khác)
def add(a, b):
    return a + b


def divide(a, b):
    if b == 0:
        raise ValueError("Không thể chia cho 0")
    return a / b


# Các hàm test
def test_add_positive_numbers():
    assert add(2, 3) == 5


def test_add_negative_numbers():
    assert add(-1, -1) == -2
```

---

### 3. Cách chạy test

Mở terminal tại thư mục chứa file và gõ:

```bash
pytest

```

**Một số tham số lệnh hữu ích:**

* `pytest -v`: Hiển thị chi tiết từng hàm test (Verbose).
* `pytest test_math.py`: Chỉ chạy riêng file `test_math.py`.
* `pytest -k "add"`: Chỉ chạy các hàm test có chứa từ "add" trong tên.

---

### 4. Kiểm tra Ngoại lệ (Exception Handling)

Khi bạn muốn kiểm tra xem một hàm có ném ra lỗi như mong đợi hay không khi truyền dữ liệu sai, dùng `pytest.raises`:

```python
import pytest


def test_divide_by_zero():
    with pytest.raises(ValueError) as exc_info:
        divide(10, 0)

    # Kiểm tra thông điệp lỗi trả về
    assert str(exc_info.value) == "Không thể chia cho 0"
```

---

### 5. Sử dụng Fixture (Dựng môi trường test)

**Fixture** giúp bạn chuẩn bị dữ liệu hoặc khởi tạo đối tượng trước khi test (VD: tạo kết nối Database, mở file, tạo dữ liệu mẫu).

```python
import pytest


@pytest.fixture
def sample_user():
    return {"username": "dev_python", "role": "admin"}


def test_user_role(sample_user):
    assert sample_user["role"] == "admin"
```

---

### 6. Parametrize (Chạy 1 hàm test với nhiều bộ dữ liệu)

Thay vì viết nhiều hàm test giống nhau, bạn có thể truyền nhiều tập input/output vào một hàm test duy nhất:

```python
import pytest


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (1, 2, 3),
        (5, 5, 10),
        (-1, 1, 0),
        (0, 0, 0),
    ],
)
def test_add_multiple_cases(a, b, expected):
    assert add(a, b) == expected
```

---