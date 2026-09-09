`pathlib` là thư viện tiêu chuẩn của Python (từ bản 3.4+) giúp xử lý đường dẫn tệp và thư mục theo phong cách hướng đối tượng (**Object-Oriented**). Nó giúp bạn quên đi các thao tác chuỗi rắc rối của `os.path` cũ kỹ và tự động tương thích tốt trên cả Windows, macOS lẫn Linux.

---

## 1. Khởi tạo và Thao tác cơ bản

Thay vì dùng chuỗi đơn thuần, bạn bọc đường dẫn vào đối tượng `Path`.

```python
from pathlib import Path

# Đường dẫn tới thư mục hiện tại
current_dir = Path.cwd()

# Đường dẫn tới thư mục Home của người dùng
home_dir = Path.home()

# Tạo đường dẫn mới (Dùng dấu / cực kỳ tiện lợi, tự xử lý separator theo OS)
file_path = Path("documents") / "python" / "notes.txt"

print(file_path)  # Windows: documents\python\notes.txt | Linux/Mac: documents/python/notes.txt

```

---

## 2. Bóc tách thông tin của đường dẫn

Giả sử bạn có đường dẫn: `path = Path("/home/user/data/report.pdf")`

* **`path.name`** -> `'report.pdf'` (Tên tệp đầy đủ)
* **`path.stem`** -> `'report'` (Tên tệp không chứa đuôi)
* **`path.suffix`** -> `'.pdf'` (Đuôi tệp)
* **`path.parent`** -> `PosixPath('/home/user/data')` (Thư mục cha)
* **`path.parts`** -> `('/', 'home', 'user', 'data', 'report.pdf')` (Tách thành tuple)

---

## 3. Kiểm tra thông tin đường dẫn

```python
path = Path("config.ini")

# Kiểm tra tồn tại
if path.exists():
    print("Đường dẫn tồn tại!")

# Kiểm tra xem là file hay folder
print(path.is_file())    # True nếu là tệp
print(path.is_dir())     # True nếu là thư mục

```

---

## 4. Đọc và Ghi tệp nhanh (Không cần `open()`)

`pathlib` hỗ trợ đọc/ghi trực tiếp cho các tệp nhỏ mà không cần tới câu lệnh `with open(...)`:

```python
file_path = Path("hello.txt")

# Ghi văn bản (Tự tạo file nếu chưa có, ghi đè nếu đã có)
file_path.write_text("Xin chào từ pathlib!", encoding="utf-8")

# Đọc văn bản
content = file_path.read_text(encoding="utf-8")
print(content)

# Ghi/Đọc dữ liệu nhị phân (binary)
file_path.write_bytes(b"Binary data")
data = file_path.read_bytes()

```

---

## 5. Duyệt và Tìm kiếm tệp (Globbing)

Đây là tính năng mạnh mẽ nhất của `pathlib` khi làm việc với thư mục.

```python
folder = Path("my_project")

# 1. Lấy tất cả các tệp/thư mục con trực tiếp
for item in folder.iterdir():
    print(item.name)

# 2. Tìm tất cả tệp .py trong thư mục hiện tại
for py_file in folder.glob("*.py"):
    print(py_file.name)

# 3. Tìm tất cả tệp .png trong thư mục hiện tại VÀ TẤT CẢ thư mục con (Recursive)
for image in folder.rglob("*.png"):
    print(image)

```

---

## 6. Quản lý Thư mục & Tệp tin

```python
# Tạo thư mục mới (exist_ok=True tránh lỗi nếu folder đã có sẵn, parents=True tạo luôn cả folder cha nếu chưa có)
new_dir = Path("logs/2026/09")
new_dir.mkdir(parents=True, exist_ok=True)

# Đổi tên hoặc di chuyển tệp
old_file = Path("old_name.txt")
new_file = Path("new_name.txt")
if old_file.exists():
    old_file.rename(new_file)

# Xóa tệp hoặc thư mục rỗng
file_to_delete = Path("temp.txt")
if file_to_delete.exists():
    file_to_delete.unlink()  # Xóa file

dir_to_delete = Path("empty_folder")
if dir_to_delete.exists():
    dir_to_delete.rmdir()   # Xóa folder rỗng

```

---

## Bảng so sánh nhanh: `os.path` vs `pathlib`

| Thao tác | Cách cũ (`os` / `os.path`) | Cách mới (`pathlib`) |
| --- | --- | --- |
| **Nối đường dẫn** | `os.path.join(a, b)` | `Path(a) / b` |
| **Lấy thư mục cha** | `os.path.dirname(p)` | `p.parent` |
| **Lấy tên file** | `os.path.basename(p)` | `p.name` |
| **Tạo thư mục** | `os.makedirs(p)` | `p.mkdir(parents=True)` |
| **Xóa tệp** | `os.remove(p)` | `p.unlink()` |
| **Đọc tệp văn bản** | `with open(p) as f: text = f.read()` | `text = p.read_text()` |