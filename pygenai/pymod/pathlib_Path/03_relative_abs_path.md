Trong `pathlib`, việc quản lý và chuyển đổi giữa đường dẫn tương đối (relative) và tuyệt đối (absolute) rất ngắn gọn nhờ các phương thức được tích hợp sẵn.

---

## 1. Phân biệt hai loại đường dẫn

* **Đường dẫn tuyệt đối (Absolute Path):** Chỉ rõ vị trí chính xác của tệp/thư mục tính từ gốc hệ thống (Root directory).
* Windows: `C:\Users\Admin\Project\data.csv`
* Linux/macOS: `/home/user/Project/data.csv`


* **Đường dẫn tương đối (Relative Path):** Chỉ vị trí của tệp/thư mục dựa trên **thư mục làm việc hiện tại** (Current Working Directory - `CWD`).
* Ví dụ: `data/notes.txt` hoặc `../config.json`



---

## 2. Kiểm tra loại đường dẫn

Bạn dùng thuộc tính `.is_absolute()` để kiểm tra:

```python
from pathlib import Path

path1 = Path("/home/user/document.txt")
path2 = Path("data/document.txt")

print(path1.is_absolute())  # Output: True
print(path2.is_absolute())  # Output: False

```

---

## 3. Chuyển từ tương đối sang tuyệt đối

Để chuẩn hóa đường dẫn tương đối thành tuyệt đối, `pathlib` cung cấp 2 phương thức chính tùy theo mục đích:

### `path.resolve()` (Khuyên dùng)

`resolve()` sẽ nối đường dẫn với thư mục hiện tại (`CWD`), đồng thời tự động:

* Giải quyết các ký tự `.` (thư mục hiện tại) và `..` (thư mục cấp cha).
* Rút gọn các liên kết mềm (symlink - nếu có).

```python
from pathlib import Path

# Giả sử CWD là: /home/user/my_app

rel_path = Path("data/../config/settings.json")
abs_path = rel_path.resolve()

print(abs_path)
# Output: /home/user/my_app/config/settings.json

```

### `path.absolute()`

`absolute()` chỉ đơn thuần nối đường dẫn tương đối vào `CWD` hiện tại mà **không** rút gọn `..` hay giải quyết symlink.

```python
abs_path_raw = rel_path.absolute()
print(abs_path_raw)
# Output: /home/user/my_app/data/../config/settings.json

```

---

## 4. Chuyển từ tuyệt đối sang tương đối (`relative_to`)

Khi bạn muốn tính vị trí tương đối của một tệp so với một thư mục gốc nhất định, dùng phương thức `.relative_to()`:

```python
from pathlib import Path

file_path = Path("/home/user/projects/python/app.py")
base_dir = Path("/home/user/projects")

# Lấy đường dẫn tương đối từ base_dir đến file_path
rel_path = file_path.relative_to(base_dir)

print(rel_path)
# Output: python/app.py

```

> **Lưu ý:** Phương thức `.relative_to()` sẽ ném ra lỗi `ValueError` nếu `file_path` không nằm bên trong `base_dir`.

---

## 5. Mẹo làm việc an toàn trong dự án

Để tránh lỗi đường dẫn khi chạy script Python từ các thư mục làm việc khác nhau, cách hay nhất là lấy đường dẫn tuyệt đối dựa trên vị trí của chính file mã nguồn (`__file__`):

```python
from pathlib import Path

# Lấy thư mục chứa file mã nguồn hiện tại (tuyệt đối)
BASE_DIR = Path(__file__).resolve().parent

# Truy cập file dữ liệu nằm cùng project một cách an toàn
DATA_FILE = BASE_DIR / "data" / "input.csv"

print(DATA_FILE)

```