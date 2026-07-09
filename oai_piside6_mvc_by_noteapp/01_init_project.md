# Buổi 1 - Khởi tạo dự án PySide6 theo mô hình MVC

Hôm nay chúng ta **chưa viết chức năng ghi chú**. Mục tiêu là xây dựng **bộ khung của dự án**, giống như xây móng nhà trước khi xây tường.

Sau buổi học này, bạn sẽ hiểu:

- MVC hoạt động như thế nào.
- Cách tổ chức source code.
- Tạo project chuẩn.
- Tạo Main Window.
- Kết nối SQLite.
- Chạy được chương trình đầu tiên.

---

# Mục tiêu cuối buổi

Khi chạy chương trình sẽ có cửa sổ như sau:

```text-x-trilium-auto
+---------------------------------------------------------+
| Note App                                    □  □   X    |
+---------------------------------------------------------+
|                                                         |
|                 Welcome to Note App                     |
|                                                         |
+---------------------------------------------------------+
```

Đồng thời sẽ sinh ra file

```text-x-trilium-auto
note.db
```

trong thư mục database.

---

# Bước 1. Tạo Project

```text-x-trilium-auto
note_app/
│
├── main.py
│
├── database/
│   ├── __init__.py
│   ├── database.py
│   └── note.db
│
├── model/
│   ├── __init__.py
│   └── note_model.py
│
├── view/
│   ├── __init__.py
│   └── main_window.py
│
├── controller/
│   ├── __init__.py
│   └── note_controller.py
│
├── resources/
│
└── README.md
```

---

# Tại sao phải chia thư mục?

Nếu viết tất cả vào một file:

```text-x-trilium-auto
main.py

5000 dòng
```

thì sẽ rất khó bảo trì.

Ví dụ:

```text-x-trilium-auto
SQL

↓

GUI

↓

Menu

↓

Toolbar

↓

Save

↓

Load

↓

Search
```

Tất cả trộn lẫn.

Một project chỉ khoảng 3–5 nghìn dòng đã rất khó đọc.

Vì vậy phải tách.

---

# Vai trò từng thư mục

## database

Chỉ quản lý SQLite.

Ví dụ

```text-x-trilium-auto
connect()

create_table()

backup()

vacuum()
```

Không import PySide6.

---

## model

Đại diện dữ liệu.

Ví dụ

```text-x-trilium-auto
Note

Notebook

Tag
```

Model chỉ quan tâm dữ liệu.

---

## view

Chỉ tạo giao diện.

Ví dụ

```text-x-trilium-auto
QMainWindow

QPushButton

QTextEdit

QListWidget
```

Không viết SQL.

---

## controller

Điều khiển.

Ví dụ

```text-x-trilium-auto
button clicked

↓

save()

↓

model

↓

refresh view
```

---

# Luồng MVC

```text-x-trilium-auto
          User

            │

            ▼

          View

            │

         signal

            │

            ▼

      Controller

            │

            ▼

         Model

            │

            ▼

         SQLite
```

Hãy nhớ:

**View không bao giờ gọi SQLite trực tiếp.**

---

# Bước 2. Tạo Virtual Environment

Trong thư mục project:

```text-x-trilium-auto
python -m venv .venv
```

Kích hoạt:

### Windows

```text-x-trilium-auto
.venv\Scripts\activate
```

### Linux/macOS

```text-x-trilium-auto
source .venv/bin/activate
```

---

# Bước 3. Cài đặt thư viện

```text-x-trilium-auto
pip install pyside6
```

Kiểm tra:

```text-x-trilium-auto
pip list
```

Bạn sẽ thấy:

```text-x-trilium-auto
PySide6
PySide6_Addons
PySide6_Essentials
shiboken6
```

---

# Bước 4. Tạo Main Window

File

```text-x-trilium-auto
view/main_window.py
```

```text-x-trilium-auto
from PySide6.QtWidgets import (
    QMainWindow,
    QLabel
)
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Simple Note")

        self.resize(900, 600)

        label = QLabel("Welcome to Note App")

        label.setAlignment(Qt.AlignCenter)

        self.setCentralWidget(label)
```

---

## Phân tích

### Kế thừa

```text-x-trilium-auto
class MainWindow(QMainWindow):
```

Mọi cửa sổ chính đều kế thừa từ `QMainWindow`.

---

### Constructor

```text-x-trilium-auto
super().__init__()
```

Khởi tạo cửa sổ.

---

### Tiêu đề

```text-x-trilium-auto
self.setWindowTitle("Simple Note")
```

Hiển thị:

```text-x-trilium-auto
Simple Note
```

---

### Kích thước

```text-x-trilium-auto
self.resize(900,600)
```

Chỉ đặt kích thước ban đầu.

---

### Widget trung tâm

```text-x-trilium-auto
QMainWindow

┌─────────────────────┐
│ Toolbar             │
├─────────────────────┤
│                     │
│  Central Widget     │
│                     │
├─────────────────────┤
│ Status Bar          │
└─────────────────────┘
```

Hiện tại ta đặt:

```text-x-trilium-auto
QLabel
```

làm widget trung tâm.

---

# Bước 5. Tạo Database

File

```text-x-trilium-auto
database/database.py
```

```text-x-trilium-auto
import sqlite3 from pathlib import Path


class Database:

    def __init__(self):

        db_folder = Path(__file__).parent

        db_folder.mkdir(exist_ok=True)

        self.db_path = db_folder / "note.db"

        self.connection = sqlite3.connect(self.db_path)

    def create_tables(self):

        cursor = self.connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            content TEXT,

            created_at TEXT,

            updated_at TEXT

        )
        """)

        self.connection.commit()
```

---

## Tại sao dùng `pathlib`?

Nhiều người mới thường viết:

```text-x-trilium-auto
sqlite3.connect("note.db")
```

Nếu chạy chương trình từ thư mục khác, file database có thể được tạo sai vị trí.

Với `Path(__file__).parent`, cơ sở dữ liệu luôn được đặt cạnh `database.py`, giúp cấu trúc dự án ổn định hơn.

---

# Bước 6. Tạo Controller

Hiện tại controller chỉ khởi tạo View và Database.

File

```text-x-trilium-auto
controller/note_controller.py
```

```text-x-trilium-auto
from database.database import Database


class NoteController:

    def __init__(self, view):

        self.view = view

        self.database = Database()

        self.database.create_tables()
```

---

## Tại sao Database nằm trong Controller?

Sai:

```text-x-trilium-auto
MainWindow

↓

sqlite3
```

Đúng:

```text-x-trilium-auto
MainWindow

↓

Controller

↓

Database
```

View không biết SQLite tồn tại.

---

# Bước 7. Viết `main.py`

```text-x-trilium-auto
import sys

from PySide6.QtWidgets import QApplication

from view.main_window import MainWindow from controller.note_controller import NoteController


def main():

    app = QApplication(sys.argv)

    window = MainWindow()

    controller = NoteController(window)

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

---

# Chạy chương trình

```text-x-trilium-auto
python main.py
```

Kết quả:

```text-x-trilium-auto
Simple Note

Welcome to Note App
```

Đồng thời trong thư mục:

```text-x-trilium-auto
database/
```

xuất hiện

```text-x-trilium-auto
note.db
```

---

# Kiểm tra cơ sở dữ liệu

Mở SQLite bằng công cụ yêu thích (ví dụ DB Browser for SQLite hoặc tiện ích mở rộng SQLite trong VS Code), bạn sẽ thấy bảng:

```text-x-trilium-auto
notes
```

với các cột:

| Cột | Kiểu dữ liệu |
| --- | --- |
| id  | INTEGER PRIMARY KEY AUTOINCREMENT |
| title | TEXT |
| content | TEXT |
| created_at | TEXT |
| updated_at | TEXT |

Hiện tại bảng chưa có dữ liệu, điều này hoàn toàn bình thường.

---

# Kiến thức quan trọng cần nhớ

Đến cuối buổi 1, bạn nên nắm được:

- `QMainWindow` là cửa sổ chính của ứng dụng.
- `QApplication` quản lý vòng lặp sự kiện (event loop).
- `MainWindow` chỉ tạo và hiển thị giao diện.
- `Database` chịu trách nhiệm kết nối và khởi tạo SQLite.
- `NoteController` là cầu nối giữa View và Database.
- Sử dụng `pathlib.Path` để xác định vị trí tệp cơ sở dữ liệu một cách an toàn.
- Dự án đã được chia thành các module ngay từ đầu để dễ mở rộng.

---

# Bài tập thực hành

1. Đổi tiêu đề cửa sổ thành **My Notes**.
2. Đổi kích thước cửa sổ thành **1200 × 700**.
3. Thêm cột `is_pinned INTEGER DEFAULT 0` vào bảng `notes` (hãy xóa file `note.db` cũ trước khi chạy lại để tạo bảng mới).
4. Thêm phương thức `close()` vào lớp `Database` để đóng kết nối SQLite khi ứng dụng kết thúc (chúng ta sẽ gọi phương thức này ở các buổi sau).

---

## Buổi 2 (Preview)

Ở buổi tiếp theo, chúng ta sẽ thay `QLabel` bằng giao diện thực của ứng dụng:

```text-x-trilium-auto
+-----------------------------------------------------------+
| Toolbar                                                   |
+----------------------+------------------------------------+
| Danh sách ghi chú    | Tiêu đề                            |
|----------------------|------------------------------------|
| Python               |                                    |
| Công việc            | QTextEdit                          |
| Ý tưởng              |                                    |
| ...                  |                                    |
+----------------------+------------------------------------+
```

Bạn sẽ học các widget và layout quan trọng của PySide6 như **QSplitter**, **QListWidget**, **QTextEdit**, **QLineEdit**, **QToolBar** và cách tổ chức giao diện sao cho chuẩn, dễ mở rộng theo mô hình MVC.
