# Buổi 39. Pathlib trong Python (Python Intermediate)

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Hiểu `pathlib` là gì.
> * Biết tại sao nên dùng `Path` thay cho `os.path`.
> * Thành thạo tạo và xử lý đường dẫn.
> * Đọc, ghi file bằng `Path`.
> * Duyệt thư mục.
> * Tìm file bằng `glob()`.
> * Làm việc với metadata của file.
> * Xây dựng công cụ quản lý file thực tế.

---

# 1. Vấn đề với `os.path`

Trước đây Python thường dùng:

```python
import os

path = os.path.join("data", "users", "users.json")
```

Kết quả:

```text
data/users/users.json
```

Nhưng code dài và khó đọc.

---

`pathlib` cung cấp cách hướng đối tượng:

```python
from pathlib import Path


path = Path("data") / "users" / "users.json"
```

Rõ ràng hơn.

---

# 2. Pathlib là gì?

`pathlib` là module chuẩn Python để xử lý:

* File path.
* Directory path.
* File system.

Import:

```python
from pathlib import Path
```

---

# 3. Tạo Path object

```python
from pathlib import Path


p = Path("hello.txt")

print(p)
```

Output:

```text
hello.txt
```

Lưu ý:

`Path` chưa tạo file.

Nó chỉ là đối tượng đại diện cho đường dẫn.

---

# 4. Path hiện tại

```python
from pathlib import Path


p = Path.cwd()

print(p)
```

Ví dụ:

```text
/home/user/project
```

---

# 5. Home directory

```python
home = Path.home()

print(home)
```

Ví dụ:

```text
/home/user
```

---

# 6. Ghép đường dẫn

Không dùng:

```python
"data/" + "file.txt"
```

Dùng:

```python
path = Path("data") / "file.txt"
```

Ví dụ:

```python
path = Path("project") / "data" / "users.json"
```

Kết quả:

```text
project/data/users.json
```

---

# 7. Các thuộc tính quan trọng

Ví dụ:

```python
p = Path("/home/user/data/file.txt")
```

---

## Name

```python
p.name
```

Kết quả:

```text
file.txt
```

---

## Suffix

```python
p.suffix
```

Kết quả:

```text
.txt
```

---

## Stem

Tên file không có extension:

```python
p.stem
```

Kết quả:

```text
file
```

---

## Parent

Thư mục cha:

```python
p.parent
```

Kết quả:

```text
/home/user/data
```

---

# 8. Kiểm tra tồn tại

```python
p.exists()
```

Ví dụ:

```python
if p.exists():
    print("Found")
```

---

# 9. Kiểm tra file hay thư mục

## File

```python
p.is_file()
```

---

## Directory

```python
p.is_dir()
```

Ví dụ:

```python
if p.is_file():
    print("File")

elif p.is_dir():
    print("Folder")
```

---

# 10. Tạo thư mục

## Một thư mục

```python
folder = Path("data")

folder.mkdir()
```

---

## Tạo nhiều cấp

Ví dụ:

```text
data/
 └── users/
      └── images/
```

Dùng:

```python
folder.mkdir(parents=True)
```

---

## Không lỗi nếu tồn tại

```python
folder.mkdir(parents=True, exist_ok=True)
```

---

# 11. Tạo file

```python
file = Path("hello.txt")

file.touch()
```

Kết quả:

```text
hello.txt
```

---

# 12. Ghi file

Cách 1:

```python
file.write_text("Hello Python")
```

---

Đọc:

```python
content = file.read_text()

print(content)
```

Output:

```text
Hello Python
```

---

# 13. Encoding

Nên chỉ rõ:

```python
file.write_text("Xin chào", encoding="utf-8")
```

Đọc:

```python
text = file.read_text(encoding="utf-8")
```

---

# 14. Ghi binary

Ví dụ ảnh:

```python
data = b"abc"

file.write_bytes(data)
```

Đọc:

```python
data = file.read_bytes()
```

---

# 15. Mở file với open()

Path hỗ trợ:

```python
path = Path("data.txt")


with path.open("w", encoding="utf-8") as f:
    f.write("Hello")
```

---

# 16. Duyệt thư mục

Ví dụ:

```text
project/

├── main.py
├── data.json
└── image.png
```

Code:

```python
folder = Path("project")


for item in folder.iterdir():
    print(item)
```

Kết quả:

```text
project/main.py
project/data.json
project/image.png
```

---

# 17. Phân biệt file và folder

```python
for item in folder.iterdir():
    if item.is_file():
        print("FILE:", item)

    else:
        print("DIR:", item)
```

---

# 18. Tìm file bằng glob()

Ví dụ:

Tìm tất cả `.py`:

```python
folder.glob("*.py")
```

Ví dụ:

```python
for file in folder.glob("*.py"):
    print(file)
```

---

# 19. Tìm đệ quy

Cây thư mục:

```text
project

├── app.py

└── src

    └── main.py
```

Dùng:

```python
folder.rglob("*.py")
```

Kết quả:

```text
app.py

src/main.py
```

---

# 20. Đổi tên file

```python
old = Path("old.txt")

new = Path("new.txt")


old.rename(new)
```

---

# 21. Xóa file

```python
file.unlink()
```

---

# 22. Xóa thư mục rỗng

```python
folder.rmdir()
```

---

# 23. Absolute Path

```python
p = Path("data.txt")

print(p.absolute())
```

Ví dụ:

```text
/home/user/project/data.txt
```

---

# 24. Resolve()

```python
p.resolve()
```

Khác:

* chuyển thành đường dẫn tuyệt đối.
* xử lý `..`, `.`.

Ví dụ:

```python
Path("./data/../file.txt").resolve()
```

---

# 25. Metadata của file

Ví dụ:

```python
p.stat()
```

Kết quả:

```text
os.stat_result(...)
```

---

## Kích thước

```python
size = p.stat().st_size
```

Đơn vị:

```text
byte
```

---

## Thời gian sửa

```python
p.stat().st_mtime
```

---

# 26. Copy file

`pathlib` không có copy.

Dùng:

```python
import shutil


shutil.copy(source, destination)
```

---

# 27. Di chuyển file

```python
shutil.move(source, destination)
```

---

# 28. Pathlib và JSON

Ví dụ:

```python
from pathlib import Path
import json


path = Path("users.json")


data = {"name": "Alice"}


path.write_text(json.dumps(data), encoding="utf-8")
```

Đọc:

```python
data = json.loads(path.read_text(encoding="utf-8"))
```

---

# 29. Pathlib trong Project Structure

Ví dụ:

```text
myapp/

├── main.py

├── config/

│    └── settings.json

└── data/

     └── users.db
```

Không nên:

```python
"../config/settings.json"
```

Nên:

```python
BASE_DIR = Path(__file__).parent

CONFIG = BASE_DIR / "config" / "settings.json"
```

---

# 30. Pathlib với Python Package

Ví dụ:

```python
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
```

Lấy thư mục chứa module hiện tại.

---

# 31. Mini Project 1: File Scanner

Yêu cầu:

Quét thư mục:

```text
project/
```

In:

```text
Python files: 20

JSON files: 5

Images: 12
```

Code:

```python
from pathlib import Path


def scan(folder):

    counts = {}

    for file in folder.rglob("*"):
        if file.is_file():
            ext = file.suffix

            counts[ext] = counts.get(ext, 0) + 1

    return counts
```

---

# 32. Mini Project 2: Duplicate Finder

Ý tưởng:

Tìm file trùng:

```text
image1.png

copy/image1.png
```

Dựa trên:

* size.
* hash.

Cấu trúc:

```text
scanner/

├── main.py
├── finder.py
└── hash.py
```

---

# 33. Mini Project 3: Backup Tool

Tạo:

```text
backup/

├── source/

└── backup/
```

Chức năng:

* Copy file.
* Tạo folder theo ngày.
* Ghi log.

Ví dụ:

```text
backup/
2026-08-01/
```

---

# 34. Pathlib vs os.path

|                 | pathlib | os.path         |
| --------------- | ------- | --------------- |
| Hướng đối tượng | ✔       | ✖               |
| Dễ đọc          | ✔       | Trung bình      |
| Type Hint       | ✔       | ✖               |
| File operation  | ✔       | Cần module khác |
| Python hiện đại | ✔       | Cũ              |

---

# 35. Best Practices

## ✔ Luôn dùng Path trong project mới

Không:

```python
os.path.join()
```

Nên:

```python
Path() / "file"
```

---

## ✔ Không ghép chuỗi path

Sai:

```python
folder + "/file.txt"
```

---

## ✔ Dùng encoding

```python
read_text(encoding="utf-8")
```

---

## ✔ Tách Path khỏi Business Logic

Ví dụ:

Không:

```python
def save_user():

    path = Path("data/users.json")
```

Nên:

```python
def save_user(
    path: Path
):
```

---

# Tổng kết

Sau buổi học này bạn đã biết:

* `Path`.
* Tạo đường dẫn.
* `cwd()`.
* `home()`.
* `exists()`.
* `is_file()`.
* `is_dir()`.
* `mkdir()`.
* `touch()`.
* `read_text()`.
* `write_text()`.
* `glob()`.
* `rglob()`.
* `stat()`.
* `rename()`.
* `unlink()`.
* Ứng dụng Pathlib trong dự án.

---

# Sơ đồ Pathlib

```
                 pathlib

                    |
                  Path

     ┌──────────────┼──────────────┐
     │              │              │
  File          Directory       Metadata
     │              │              │
read/write     glob/rglob       stat()
     │
 JSON / CSV / LOG
```

---

# Bài tập thực hành

## Bài 1

Viết chương trình:

Nhập thư mục:

```text
D:/Projects
```

In:

* tổng số file.
* tổng số folder.
* dung lượng tổng.

---

## Bài 2

Viết File Organizer:

Trước:

```
Downloads/

a.jpg
b.png
c.pdf
d.zip
```

Sau:

```
Downloads/

Images/

    a.jpg
    b.png

Documents/

    c.pdf

Archives/

    d.zip
```

---

## Bài 3

Viết hàm:

```python
def find_files(
    folder: Path,
    extension: str
) -> list[Path]:
```

Trả về tất cả file có extension.

---

## Bài 4

Viết Backup Manager:

Class:

```python
class BackupManager:
```

Có:

```python
backup()

restore()
```

Sử dụng:

* Pathlib.
* shutil.
* datetime.

---

## Bài 5 (Thử thách)

Xây dựng một **Project Explorer CLI**:

Lệnh:

```bash
explorer list

explorer tree

explorer size

explorer search *.py
```

Yêu cầu:

* Dùng `pathlib`.
* Dùng `argparse` hoặc `click`.
* Có Type Hint.
* Có Logging.

---

# Chuẩn bị cho buổi sau

Ở **Buổi 40: Mini Project**, chúng ta sẽ tổng hợp toàn bộ kiến thức Python Intermediate:

* Module.
* Package.
* Virtual Environment.
* File.
* CSV.
* JSON.
* Datetime.
* Logging.
* Regex.
* Iterator.
* Generator.
* Decorator.
* Closure.
* Context Manager.
* Typing.
* Dataclass.
* Enum.
* NamedTuple.
* Pathlib.

Xây dựng một dự án thực tế hoàn chỉnh.
