Chào bạn! Bạn đã vượt qua Bài 9 về Module và Package - tuyệt vời! Bây giờ chúng ta bước vào **Bài 10: File I/O và Serialization** - kỹ năng quan trọng để lưu trữ và trao đổi dữ liệu giữa các chương trình.

---

# 📘 BÀI 10: FILE I/O VÀ SERIALIZATION

---

## 🎯 MỤC TIÊU BÀI HỌC

Sau bài này, bạn sẽ:
- Đọc/ghi file text với các chế độ khác nhau
- Sử dụng **Context Manager** (`with`) để quản lý file an toàn
- Làm việc với **JSON** - định dạng phổ biến nhất
- Xử lý **CSV** files - dữ liệu bảng
- Serialize object với **Pickle**
- Làm việc với đường dẫn file (path) bằng `pathlib`
- Xử lý file binary (hình ảnh, âm thanh...)

---

## 📖 PHẦN 1: LÝ THUYẾT CÔ ĐỌNG

### 1.1. Mở và đọc file cơ bản

```python
# Cách 1: Mở và đóng thủ công (KHÔNG KHUYẾN KHÍCH)
file = open("data.txt", "r")
content = file.read()
file.close()  # Quên close = memory leak!

# Cách 2: Context Manager (KHUYẾN KHÍCH) - Tự động đóng file
with open("data.txt", "r", encoding="utf-8") as file:
    content = file.read()
    print(content)
# File tự động đóng sau khi ra khỏi with block
```

**Các chế độ mở file (mode):**

| Mode | Mô tả |
|------|-------|
| `'r'` | Đọc (Read) - Mặc định |
| `'w'` | Ghi (Write) - Ghi đè lên file cũ |
| `'a'` | Thêm (Append) - Thêm vào cuối file |
| `'x'` | Tạo mới (Create) - Lỗi nếu file đã tồn tại |
| `'r+'` | Đọc và ghi |
| `'w+'` | Ghi và đọc (ghi đè) |
| `'b'` | Binary mode - `'rb'`, `'wb'` |

---

### 1.2. Các phương thức đọc/ghi file

```python
# ĐỌC FILE
with open("data.txt", "r", encoding="utf-8") as f:
    # Đọc toàn bộ nội dung
    content = f.read()
    
    # Đọc từng dòng
    line = f.readline()
    
    # Đọc tất cả dòng thành list
    lines = f.readlines()

# GHI FILE
with open("output.txt", "w", encoding="utf-8") as f:
    # Ghi chuỗi
    f.write("Hello World!\n")
    
    # Ghi nhiều dòng
    lines = ["Line 1\n", "Line 2\n", "Line 3\n"]
    f.writelines(lines)

# THÊM VÀO CUỐI FILE
with open("output.txt", "a", encoding="utf-8") as f:
    f.write("This line is appended!\n")
```

---

### 1.3. JSON - Định dạng phổ biến nhất

**JSON (JavaScript Object Notation)** - Định dạng trao đổi dữ liệu phổ biến:

```python
import json

# Dữ liệu Python
data = {
    "name": "Nguyễn Văn A",
    "age": 25,
    "is_student": False,
    "scores": [8.5, 9.0, 7.5],
    "address": {"street": "123 Main St", "city": "Hanoi"},
}

# GHI JSON
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# ĐỌC JSON
with open("data.json", "r", encoding="utf-8") as f:
    loaded_data = json.load(f)

# Chuyển Python → JSON string
json_string = json.dumps(data, ensure_ascii=False, indent=2)

# Chuyển JSON string → Python
python_data = json.loads(json_string)
```

---

### 1.4. CSV - Dữ liệu bảng

```python
import csv

# GHI CSV
data = [["Tên", "Tuổi", "Điểm"], ["An", 20, 8.5], ["Bình", 21, 9.0], ["Châu", 19, 7.5]]

with open("data.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(data)

# GHI CSV với DictWriter
students = [
    {"name": "An", "age": 20, "score": 8.5},
    {"name": "Bình", "age": 21, "score": 9.0},
    {"name": "Châu", "age": 19, "score": 7.5},
]

with open("students.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = ["name", "age", "score"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(students)

# ĐỌC CSV
with open("students.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"{row['name']}: {row['age']} tuổi, {row['score']} điểm")
```

---

### 1.5. Pickle - Serialize Python objects

**Pickle lưu bất kỳ object Python nào (cả class, function)**

```python
import pickle


# Định nghĩa class
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def greet(self):
        return f"Hello, I'm {self.name}"


# Tạo object
person = Person("Nguyễn Văn A", 25)

# GHI PICKLE
with open("person.pkl", "wb") as f:
    pickle.dump(person, f)

# ĐỌC PICKLE
with open("person.pkl", "rb") as f:
    loaded_person = pickle.load(f)

print(loaded_person.greet())  # Hello, I'm Nguyễn Văn A
```

**⚠️ Lưu ý:** Pickle không an toàn với dữ liệu từ nguồn không tin cậy!

---

### 1.6. pathlib - Làm việc với đường dẫn hiện đại

```python
from pathlib import Path

# Tạo Path object
path = Path("data")
file_path = path / "file.txt"  # Nối đường dẫn

# Kiểm tra
print(file_path.exists())  # File tồn tại?
print(file_path.is_file())  # Là file?
print(file_path.is_dir())  # Là thư mục?
print(file_path.suffix)  # .txt
print(file_path.stem)  # file (không có extension)
print(file_path.parent)  # data/

# Tạo thư mục
path.mkdir(exist_ok=True)  # Tạo nếu chưa tồn tại

# Lấy danh sách files
for file in Path(".").glob("*.py"):
    print(file.name)

# Đọc/ghi với pathlib
with open(file_path, "w") as f:
    f.write("Hello")

# Xóa file
if file_path.exists():
    file_path.unlink()

# Xóa thư mục
if path.exists():
    path.rmdir()  # Thư mục phải rỗng
```

---

### 1.7. Xử lý file binary (Hình ảnh, âm thanh...)

```python
# ĐỌC FILE BINARY
with open("image.jpg", "rb") as f:
    binary_data = f.read()
    print(f"Size: {len(binary_data)} bytes")

# GHI FILE BINARY
with open("copy.jpg", "wb") as f:
    f.write(binary_data)


# COPY BINARY LỚN (đọc từng chunk để tiết kiệm memory)
def copy_large_file(src, dst, chunk_size=8192):
    """Copy file lớn bằng cách đọc từng chunk"""
    with open(src, "rb") as f_src:
        with open(dst, "wb") as f_dst:
            while True:
                chunk = f_src.read(chunk_size)
                if not chunk:
                    break
                f_dst.write(chunk)
```

---

## 💻 PHẦN 2: CODE VÍ DỤ THỰC TẾ

### Ví dụ 1: Hệ thống quản lý dữ liệu đa định dạng

```python
import json
import csv
import pickle
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class DataManager:
    """Quản lý dữ liệu với nhiều định dạng"""

    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def save_json(self, filename: str, data: Dict[str, Any]):
        """Lưu JSON"""
        filepath = self.data_dir / f"{filename}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filepath

    def load_json(self, filename: str) -> Dict[str, Any]:
        """Đọc JSON"""
        filepath = self.data_dir / f"{filename}.json"
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_csv(self, filename: str, data: List[Dict[str, Any]]):
        """Lưu CSV"""
        if not data:
            return
        filepath = self.data_dir / f"{filename}.csv"
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        return filepath

    def load_csv(self, filename: str) -> List[Dict[str, str]]:
        """Đọc CSV"""
        filepath = self.data_dir / f"{filename}.csv"
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def save_pickle(self, filename: str, data: Any):
        """Lưu Pickle"""
        filepath = self.data_dir / f"{filename}.pkl"
        with open(filepath, "wb") as f:
            pickle.dump(data, f)
        return filepath

    def load_pickle(self, filename: str) -> Any:
        """Đọc Pickle"""
        filepath = self.data_dir / f"{filename}.pkl"
        with open(filepath, "rb") as f:
            return pickle.load(f)

    def save_text(self, filename: str, content: str):
        """Lưu text"""
        filepath = self.data_dir / f"{filename}.txt"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath

    def load_text(self, filename: str) -> str:
        """Đọc text"""
        filepath = self.data_dir / f"{filename}.txt"
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def list_files(self, extension: str = None):
        """Liệt kê files"""
        if extension:
            return list(self.data_dir.glob(f"*.{extension}"))
        return list(self.data_dir.glob("*"))

    def delete_file(self, filename: str):
        """Xóa file"""
        filepath = self.data_dir / filename
        if filepath.exists():
            filepath.unlink()
            return True
        return False


# SỬ DỤNG
dm = DataManager("my_data")

# Dữ liệu mẫu
students = [
    {"id": "SV001", "name": "Nguyễn Văn A", "age": 20, "score": 8.5},
    {"id": "SV002", "name": "Trần Thị B", "age": 21, "score": 9.0},
    {"id": "SV003", "name": "Lê Văn C", "age": 19, "score": 7.5},
]

# Lưu các định dạng
dm.save_json("students", students)
dm.save_csv("students", students)
dm.save_pickle("students", students)
dm.save_text("students_summary", f"Total: {len(students)} students")

# Đọc các định dạng
json_data = dm.load_json("students")
csv_data = dm.load_csv("students")
pickle_data = dm.load_pickle("students")
text_data = dm.load_text("students_summary")

print("JSON:", json_data[0])
print("CSV:", csv_data[0])
print("Pickle:", pickle_data[0])
print("Text:", text_data)

# Liệt kê files
print("\nFiles:", [f.name for f in dm.list_files()])
```

---

### Ví dụ 2: Hệ thống log với rotation

```python
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import time


class Logger:
    """Hệ thống log với rotation tự động"""

    def __init__(self, log_dir="logs", max_size_mb=5, max_files=5):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.max_size_mb = max_size_mb
        self.max_files = max_files
        self.current_file = (
            self.log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        )

    def _rotate_if_needed(self):
        """Kiểm tra và rotate log nếu cần"""
        if self.current_file.exists():
            size_mb = self.current_file.stat().st_size / (1024 * 1024)
            if size_mb >= self.max_size_mb:
                # Đổi tên file hiện tại thành file cũ
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                old_file = self.log_dir / f"app_{timestamp}.log"
                self.current_file.rename(old_file)

                # Xóa file cũ nếu vượt quá số lượng
                log_files = sorted(self.log_dir.glob("app_*.log"))
                if len(log_files) > self.max_files:
                    for f in log_files[: -self.max_files]:
                        f.unlink()

                # Tạo file mới
                self.current_file.touch()

    def log(self, level: str, message: str, extra: Dict[str, Any] = None):
        """Ghi log"""
        self._rotate_if_needed()

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.upper(),
            "message": message,
            "extra": extra or {},
        }

        with open(self.current_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def info(self, message: str, extra: Dict[str, Any] = None):
        self.log("INFO", message, extra)

    def error(self, message: str, extra: Dict[str, Any] = None):
        self.log("ERROR", message, extra)

    def warning(self, message: str, extra: Dict[str, Any] = None):
        self.log("WARNING", message, extra)

    def debug(self, message: str, extra: Dict[str, Any] = None):
        self.log("DEBUG", message, extra)

    def read_logs(self, limit: int = 100, level: str = None):
        """Đọc log gần nhất"""
        if not self.current_file.exists():
            return []

        logs = []
        with open(self.current_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    if level is None or log_entry.get("level") == level.upper():
                        logs.append(log_entry)
                except json.JSONDecodeError:
                    continue

        return logs[-limit:]

    def clear(self):
        """Xóa log hiện tại"""
        if self.current_file.exists():
            self.current_file.unlink()
            self.current_file.touch()


# SỬ DỤNG
logger = Logger("my_logs", max_size_mb=0.001, max_files=3)  # 1KB cho test

# Ghi logs
for i in range(10):
    logger.info(f"User {i} logged in", {"user_id": i, "ip": "127.0.0.1"})
    time.sleep(0.1)

try:
    result = 10 / 0
except Exception as e:
    logger.error(f"Division error: {e}", {"operation": "division", "values": [10, 0]})

# Đọc logs
print("\n=== RECENT LOGS ===")
for log in logger.read_logs(limit=5):
    print(f"[{log['level']}] {log['timestamp']}: {log['message']}")
    if log.get("extra"):
        print(f"  Extra: {log['extra']}")
```

---

### Ví dụ 3: Công cụ backup file tự động

```python
import os
import shutil
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class FileBackup:
    """Công cụ backup và restore file"""

    def __init__(self, source_dir: str, backup_dir: str):
        self.source_dir = Path(source_dir)
        self.backup_dir = Path(backup_dir)
        self.metadata_file = self.backup_dir / "metadata.json"

        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Tạo metadata nếu chưa có
        if not self.metadata_file.exists():
            self._save_metadata({})

    def _get_file_hash(self, filepath: Path) -> str:
        """Tính hash của file"""
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _load_metadata(self) -> Dict:
        """Đọc metadata"""
        with open(self.metadata_file, "r") as f:
            return json.load(f)

    def _save_metadata(self, metadata: Dict):
        """Lưu metadata"""
        with open(self.metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

    def backup(self, file_pattern: str = "*") -> List[str]:
        """Backup files matching pattern"""
        metadata = self._load_metadata()
        backed_up = []

        for file_path in self.source_dir.glob(file_pattern):
            if not file_path.is_file():
                continue

            # Tính hash để kiểm tra thay đổi
            file_hash = self._get_file_hash(file_path)
            rel_path = str(file_path.relative_to(self.source_dir))

            # Kiểm tra nếu file đã thay đổi
            if rel_path in metadata and metadata[rel_path]["hash"] == file_hash:
                continue

            # Backup file
            backup_path = self.backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(file_path, backup_path)

            # Lưu metadata
            metadata[rel_path] = {
                "hash": file_hash,
                "size": file_path.stat().st_size,
                "modified": datetime.fromtimestamp(
                    file_path.stat().st_mtime
                ).isoformat(),
                "backup_time": datetime.now().isoformat(),
            }

            backed_up.append(rel_path)

        self._save_metadata(metadata)
        return backed_up

    def restore(self, file_pattern: str = "*") -> List[str]:
        """Restore files từ backup"""
        restored = []

        for backup_path in self.backup_dir.glob(file_pattern):
            if not backup_path.is_file():
                continue

            rel_path = str(backup_path.relative_to(self.backup_dir))
            target_path = self.source_dir / rel_path

            # Backup hiện tại trước khi restore
            if target_path.exists():
                temp_path = target_path.with_suffix(target_path.suffix + ".bak")
                shutil.copy2(target_path, temp_path)

            # Restore
            shutil.copy2(backup_path, target_path)
            restored.append(rel_path)

        return restored

    def diff(self) -> Dict:
        """So sánh source và backup"""
        metadata = self._load_metadata()
        diff = {"new": [], "modified": [], "deleted": [], "unchanged": []}

        # Files trong source
        for file_path in self.source_dir.glob("**/*"):
            if not file_path.is_file():
                continue

            rel_path = str(file_path.relative_to(self.source_dir))
            file_hash = self._get_file_hash(file_path)

            if rel_path not in metadata:
                diff["new"].append(rel_path)
            elif metadata[rel_path]["hash"] != file_hash:
                diff["modified"].append(rel_path)
            else:
                diff["unchanged"].append(rel_path)

        # Files bị xóa
        for rel_path in metadata:
            if not (self.source_dir / rel_path).exists():
                diff["deleted"].append(rel_path)

        return diff

    def status(self):
        """Hiển thị trạng thái backup"""
        metadata = self._load_metadata()

        print("\n📁 BACKUP STATUS")
        print("=" * 50)
        print(f"Source: {self.source_dir}")
        print(f"Backup: {self.backup_dir}")
        print(f"Files backed up: {len(metadata)}")

        total_size = sum(info["size"] for info in metadata.values())
        print(f"Total size: {total_size / (1024 * 1024):.2f} MB")

        diff = self.diff()
        if diff["new"]:
            print(f"\n🟢 New files: {len(diff['new'])}")
        if diff["modified"]:
            print(f"🟡 Modified files: {len(diff['modified'])}")
        if diff["deleted"]:
            print(f"🔴 Deleted files: {len(diff['deleted'])}")

        print(f"✅ Unchanged: {len(diff['unchanged'])}")


# SỬ DỤNG
import tempfile

# Tạo thư mục test
with tempfile.TemporaryDirectory() as tmpdir:
    source = Path(tmpdir) / "source"
    backup = Path(tmpdir) / "backup"

    # Tạo files test
    source.mkdir()
    (source / "file1.txt").write_text("Hello World!")
    (source / "file2.txt").write_text("Python Programming")
    (source / "sub").mkdir()
    (source / "sub" / "file3.txt").write_text("Nested file")

    # Backup
    bk = FileBackup(source, backup)
    print("=== BACKING UP ===")
    backed = bk.backup()
    print(f"Backed up: {backed}")

    # Xem status
    bk.status()

    # Sửa file
    (source / "file1.txt").write_text("Modified content!")
    (source / "file2.txt").write_text("Another change")
    (source / "new_file.txt").write_text("Brand new!")

    # Xem diff
    print("\n=== DIFF ===")
    diff = bk.diff()
    print(f"New: {diff['new']}")
    print(f"Modified: {diff['modified']}")
    print(f"Deleted: {diff['deleted']}")

    # Backup mới
    print("\n=== BACKUP AGAIN ===")
    new_backed = bk.backup()
    print(f"Newly backed up: {new_backed}")

    bk.status()
```

---

## 🧪 PHẦN 3: BÀI TẬP VỀ NHÀ (10 bài)

### 📌 Bài tập cơ bản (6 bài)

**Bài 1:** Viết chương trình đọc file `input.txt`, đếm số từ, số dòng, số ký tự và ghi kết quả vào `output.txt`.

**Bài 2:** Viết chương trình đọc file JSON chứa danh sách sinh viên, tính điểm trung bình và ghi vào file CSV mới.

**Bài 3:** Viết chương trình sao chép một file lớn (hình ảnh, video) sử dụng binary mode.

**Bài 4:** Viết chương trình tìm kiếm và thay thế text trong file: `find_replace(filename, old_text, new_text)`.

**Bài 5:** Viết chương trình đọc file CSV và in ra dữ liệu dưới dạng bảng đẹp.

**Bài 6:** Viết chương trình lưu và đọc dữ liệu Python object (dict, list) sử dụng pickle.

---

### ⭐ Bài tập nâng cao (4 bài)

**Bài 7:** Xây dựng hệ thống log tự động với các level: DEBUG, INFO, WARNING, ERROR. Log được ghi vào file với timestamp.

**Bài 8:** Tạo công cụ merge nhiều CSV files thành một CSV duy nhất (cùng cấu trúc).

**Bài 9:** Xây dựng chương trình backup tự động:
- Backup các file trong thư mục
- Chỉ backup file đã thay đổi (dùng hash)
- Lưu metadata về backup

**Bài 10:** Xây dựng công cụ chuyển đổi định dạng:
- CSV → JSON
- JSON → CSV
- XML → JSON
- Sử dụng tham số command line

---

## 🏗️ MINI-PROJECT: HỆ THỐNG QUẢN LÝ DỮ LIỆU ĐA ĐỊNH DẠNG

```python
"""
Xây dựng hệ thống quản lý dữ liệu với các định dạng:

1. DataManager class:
   - save_json(data, filename)
   - load_json(filename)
   - save_csv(data, filename)
   - load_csv(filename)
   - save_pickle(data, filename)
   - load_pickle(filename)
   - save_text(text, filename)
   - load_text(filename)
   - convert(from_format, to_format, data)

2. Features:
   - Tự động tạo thư mục nếu chưa có
   - Kiểm tra file tồn tại
   - Xử lý encoding (UTF-8)
   - Error handling

3. Data types supported:
   - JSON
   - CSV
   - Pickle
   - Text
   - YAML (bonus)
   - Excel (bonus)

4. CLI:
   python data_manager.py save students.json --json
   python data_manager.py load students.json --json
   python data_manager.py convert students.csv --to json
"""

# Hãy tự viết!
```

---

## ✅ KIỂM TRA CODE FILE I/O CHUYÊN NGHIỆP

- [ ] Sử dụng `with` statement cho file operations
- [ ] Xác định encoding đúng (`utf-8`)
- [ ] Xử lý exception (FileNotFoundError, PermissionError)
- [ ] Sử dụng `pathlib` thay vì `os.path`
- [ ] Đóng file đúng cách (tự động với `with`)
- [ ] Xử lý file binary khi cần
- [ ] Sử dụng `newline=''` cho CSV (để tránh lỗi trên Windows)
- [ ] Kiểm tra file tồn tại trước khi đọc

---

## 🔥 THỬ THÁCH (Bonus)

```python
# Tạo context manager custom để đo thời gian và log
@contextmanager
def timed_operation(name):
    start = time.time()
    yield
    end = time.time()
    print(f"{name} took {end - start:.2f}s")


# Sử dụng
with timed_operation("Loading JSON"):
    data = load_large_json("big_data.json")
```

---

## 🎯 TÓM TẮT KIẾN THỨC QUAN TRỌNG

| Định dạng | Khi nào dùng | Ưu điểm | Nhược điểm |
|-----------|--------------|---------|------------|
| **Text** | Dữ liệu đơn giản | Dễ đọc, phổ biến | Không cấu trúc |
| **JSON** | Trao đổi dữ liệu web | Cấu trúc rõ ràng, phổ biến | Không support binary |
| **CSV** | Dữ liệu bảng | Excel-friendly, nhẹ | Giới hạn kiểu dữ liệu |
| **Pickle** | Lưu Python objects | Giữ nguyên object | Không an toàn, Python-only |

---

**Chúc mừng bạn đã hoàn thành Bài 10! Bây giờ bạn đã có thể làm việc với dữ liệu trong thế giới thực.** 💪

*Bài 11 sẽ dạy bạn về Iterator và Generator - tối ưu hóa bộ nhớ khi xử lý dữ liệu lớn!*

**Hãy gửi code các bài tập để tôi review nhé!** 🚀