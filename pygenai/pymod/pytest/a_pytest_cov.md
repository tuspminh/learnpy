**`pytest-cov`** là một plugin của Pytest kết hợp với thư viện `coverage` để đo lường tỷ lệ mã nguồn (line of code) được thực thi trong quá trình chạy kiểm thử.

---

## 1. Cài đặt

Mở terminal và cài đặt `pytest-cov` qua `pip`:

```bash
pip install pytest-cov

```

---

## 2. Cách sử dụng cơ bản

Giả sử dự án của bạn có cấu trúc như sau:

```text
my_project/
│── src/
│   ├── __init__.py
│   └── math_ops.py
└── tests/
    └── test_math_ops.py

```

File `src/math_ops.py`:

```python
def add(a, b):
    return a + b


def is_even(number):
    if number % 2 == 0:
        return True
    return False  # Giả sử hàm này chưa được test hết
```

File `tests/test_math_ops.py`:

```python
from src.math_ops import add


def test_add():
    assert add(2, 3) == 5
```

### Lệnh chạy đo Coverage:

Chạy `pytest` kèm tham số `--cov`:

```bash
pytest --cov=src

```

**Kết quả hiển thị trên terminal:**

```text
Name                Stmts   Miss  Cover
---------------------------------------
src/__init__.py         0      0   100%
src/math_ops.py         6      3    50%
---------------------------------------
TOTAL                   6      3    50%

```

* **Stmts (Statements):** Tổng số dòng lệnh.
* **Miss:** Số dòng lệnh **chưa** được chạy qua trong các bài test.
* **Cover:** Tỷ lệ phần trăm bao phủ code.

---

## 3. Xem chi tiết các dòng code chưa được Test

### Cách 1: Hiển thị dòng bị thiếu ngay trên Terminal

Thêm tùy chọn `--cov-report=term-missing`:

```bash
pytest --cov=src --cov-report=term-missing

```

**Kết quả:**

```text
Name                Stmts   Miss  Cover   Missing
-------------------------------------------------
src/math_ops.py         6      3    50%   4-6
-------------------------------------------------
TOTAL                   6      3    50%

```

*(Cột `Missing` cho biết các dòng `4-6` trong file `math_ops.py` chưa được test).*

### Cách 2: Xuất báo cáo dạng HTML (Trực quan nhất)

Xuất kết quả ra giao diện web trực quan:

```bash
pytest --cov=src --cov-report=html

```

Lệnh này sẽ tạo ra một thư mục tên là `htmlcov/`. Bạn chỉ cần mở file `htmlcov/index.html` bằng trình duyệt web (Chrome, Firefox, Edge) để xem chi tiết từng file, trong đó các dòng code chưa được chạy test sẽ được tô màu đỏ.

---

## 4. Đặt ngưỡng Coverage tối thiểu (Fail nếu dưới chỉ tiêu)

Trong quy trình CI/CD, bạn có thể bắt buộc dự án phải đạt một tỷ lệ coverage nhất định (ví dụ 80%). Nếu không đạt, lệnh pytest sẽ trả về lỗi:

```bash
pytest --cov=src --cov-fail-under=80

```

Nếu tỷ lệ đạt dưới 80%, Pytest sẽ báo `FAIL` ngay lập tức.

---

## 5. Cấu hình cố định bằng file `pyproject.toml` hoặc `.coveragerc`

Để không phải gõ lại các tham số dài dòng mỗi khi chạy test, bạn có thể thêm cấu hình vào file `pyproject.toml` ở thư mục gốc của dự án:

```toml
[tool.pytest.ini_options]
addopts = "--cov=src --cov-report=term-missing --cov-report=html"

```

Sau khi cấu hình, bạn chỉ cần gõ duy nhất lệnh:

```bash
pytest

```