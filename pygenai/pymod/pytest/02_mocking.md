Trong kiểm thử phần mềm, **Mocking** là kỹ thuật thay thế một thành phần thực tế (API server, Database, File system...) bằng một đối tượng giả lập. Điều này giúp bài test:

* **Nhanh hơn:** Không phải chờ kết nối mạng hoặc truy vấn DB.
* **Độc lập:** Không phụ thuộc vào hạ tầng bên ngoài hay dữ liệu mạng chập chờn.
* **An toàn:** Không làm thay đổi hay xóa dữ liệu thực trên DB.

Để mock trong Pytest, thư viện chuẩn phổ biến nhất là `unittest.mock` (có sẵn trong Python) hoặc plugin `pytest-mock` (cần cài thêm `pip install pytest-mock` để dùng fixture `mocker`). Trong hướng dẫn này, chúng ta sẽ dùng `unittest.mock` chuẩn của Python.

---

### 1. Mocking cuộc gọi API HTTP

Giả sử bạn có file `service.py` chứa hàm lấy thông tin người dùng từ một API bên ngoài:

```python
# service.py
import requests


def get_user_data(user_id):
    response = requests.get(f"https://api.example.com/users/{user_id}")
    if response.status_code == 200:
        return response.json()
    return None
```

Để test hàm `get_user_data` mà **không gửi HTTP request thật**, bạn dùng `@patch` để giả lập thư viện `requests.get`:

```python
# test_service.py
from unittest.mock import patch, MagicMock
from service import get_user_data


@patch("service.requests.get")
def test_get_user_data_success(mock_get):
    # 1. Định nghĩa phản hồi giả lập của requests.get()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 1, "name": "Nguyen Van A"}

    # Gán response giả lập cho hàm mock_get
    mock_get.return_value = mock_response

    # 2. Gọi hàm cần test
    result = get_user_data(1)

    # 3. Kiểm tra kết quả
    assert result == {"id": 1, "name": "Nguyen Van A"}

    # Kiểm tra xem requests.get có được gọi đúng URL không
    mock_get.assert_called_once_with("https://api.example.com/users/1")
```

> **Lưu ý quan trọng về vị trí Patch:**
> Bạn phải patch vị trí **nơi hàm được sử dụng**, chứ không phải nơi hàm được định nghĩa. Vì file `service.py` gọi `requests.get`, đường dẫn patch đúng phải là `"service.requests.get"`.

---

### 2. Mocking Truy vấn Database

Giả sử bạn có hàm kiểm tra số dư tài khoản kết nối với Database SQL bằng `sqlite3` hoặc bất kỳ ORM nào:

```python
# db_service.py
import sqlite3


def check_account_balance(db_connection, account_id):
    cursor = db_connection.cursor()
    cursor.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,))
    row = cursor.fetchone()
    if row:
        return row[0]
    return 0.0
```

Thay vì mở kết nối DB thật, bạn tạo một đối tượng `MagicMock` đóng vai trò là `db_connection`:

```python
# test_db_service.py
from unittest.mock import MagicMock
from db_service import check_account_balance


def test_check_account_balance():
    # 1. Tạo Database Connection giả
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Cấu hình để db_connection.cursor() trả về cursor giả
    mock_conn.cursor.return_value = mock_cursor

    # Cấu hình để cursor.fetchone() trả về dữ liệu giả lập (số dư = 1500.0)
    mock_cursor.fetchone.return_value = (1500.0,)

    # 2. Gọi hàm kiểm thử với mock connection
    balance = check_account_balance(mock_conn, account_id=101)

    # 3. Assert kết quả
    assert balance == 1500.0

    # Kiểm tra lệnh SQL xem có được thực thi đúng tham số không
    mock_cursor.execute.assert_called_once_with(
        "SELECT balance FROM accounts WHERE id = ?", (101,)
    )
```

---

### 3. Xử lý ngoại lệ với Mock (`side_effect`)

Nếu bạn muốn giả lập trường hợp gọi API hoặc DB thất bại (ví dụ: mất mạng, timeout, hoặc lỗi DB):

```python
import requests
import pytest
from unittest.mock import patch
from service import get_user_data


@patch("service.requests.get")
def test_get_user_data_timeout(mock_get):
    # Dùng side_effect để ném ra Exception khi hàm được gọi
    mock_get.side_effect = requests.exceptions.Timeout

    # Kiểm tra xem hàm của chúng ta có xử lý lỗi đúng không
    with pytest.raises(requests.exceptions.Timeout):
        get_user_data(1)
```

---