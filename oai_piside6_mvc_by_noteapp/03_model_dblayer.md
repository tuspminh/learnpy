# Buổi 3 - Thiết kế Database Layer và Model (CRUD)

Đây là một trong những buổi quan trọng nhất của khóa học.

Nhiều người học PySide6 thường mắc lỗi:

```text-x-trilium-auto
# main_window.py

cursor.execute(...)
connection.commit()

self.listWidget.addItem(...)
```

Mọi thứ đều viết trong `MainWindow`.

Ứng dụng vẫn chạy, nhưng sau vài nghìn dòng mã sẽ rất khó bảo trì.

Hôm nay chúng ta sẽ xây dựng **Database Layer** và **Model Layer** đúng chuẩn.

---

# Mục tiêu buổi học

Sau buổi này, dự án sẽ có cấu trúc:

```text-x-trilium-auto
note_app/

database/
    database.py

model/
    note.py
    note_model.py

view/
    main_window.py
    left_panel.py
    right_panel.py

controller/
    note_controller.py
```

Điểm quan trọng là:

> **Model chỉ làm việc với dữ liệu, hoàn toàn không biết PySide6 là gì.**

---

# Kiến trúc

```text-x-trilium-auto
          Controller
               │
               ▼
         NoteModel
               │
               ▼
          Database
               │
               ▼
            SQLite
```

Controller không làm SQL.

View cũng không làm SQL.

---

# Bước 1. Tạo lớp Note

Trong Python, dữ liệu cũng nên có một lớp đại diện.

Tạo file:

```text-x-trilium-auto
model/note.py
```

```text-x-trilium-auto
from dataclasses import dataclass


@dataclass class Note:
    id: int | None = None
    title: str = ""
    content: str = ""
    created_at: str = ""
    updated_at: str = ""
```

---

## Vì sao dùng `dataclass`?

Thay vì:

```text-x-trilium-auto
class Note:

    def __init__(
        self,
        id,
        title,
        content,
        created,
        updated
    ):
        ...
```

`@dataclass` sẽ tự tạo:

- `__init__()`
- `__repr__()`
- `__eq__()`

Giúp mã ngắn gọn hơn.

---

# Note object

Ví dụ:

```text-x-trilium-auto
note = Note(
    title="Python",
    content="Học MVC"
)
```

Đây là một **đối tượng Python**.

Không liên quan đến SQLite.

Không liên quan đến GUI.

---

# Bước 2. Hoàn thiện Database

File:

```text-x-trilium-auto
database/database.py
```

```text-x-trilium-auto
import sqlite3 from pathlib import Path


class Database:

    def __init__(self):

        db_path = Path(__file__).parent / "note.db"

        self.connection = sqlite3.connect(db_path)

        self.connection.row_factory = sqlite3.Row

        self.create_tables()

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

    def cursor(self):

        return self.connection.cursor()

    def commit(self):

        self.connection.commit()

    def close(self):

        self.connection.close()
```

---

## row_factory là gì?

Dữ liệu SQLite mặc định:

```text-x-trilium-auto
row = cursor.fetchone()

print(row)
```

Kết quả:

```text-x-trilium-auto
(1, 'Python', 'MVC')
```

Muốn lấy title:

```text-x-trilium-auto
row[1]
```

Khó đọc.

---

Nếu dùng:

```text-x-trilium-auto
connection.row_factory = sqlite3.Row
```

Ta có:

```text-x-trilium-auto
row["title"]
```

Rõ ràng hơn rất nhiều.

---

# Bước 3. Thiết kế NoteModel

Tạo file:

```text-x-trilium-auto
model/note_model.py
```

```text-x-trilium-auto
from datetime import datetime

from database.database import Database from model.note import Note
```

---

Khởi tạo:

```text-x-trilium-auto
class NoteModel:

    def __init__(self):

        self.db = Database()
```

---

## CRUD là gì?

Mọi phần mềm đều xoay quanh 4 thao tác:

```text-x-trilium-auto
Create

Read

Update

Delete
```

Viết tắt:

```text-x-trilium-auto
CRUD
```

---

# Create

```text-x-trilium-auto
def create(self, title):

    now = datetime.now().isoformat()

    cursor = self.db.cursor()

    cursor.execute(
        """
        INSERT INTO notes
        (
            title,
            content,
            created_at,
            updated_at
        )

        VALUES
        (
            ?,
            '',
            ?,
            ?
        )
        """,
        (
            title,
            now,
            now
        )
    )

    self.db.commit()

    return cursor.lastrowid
```

---

## lastrowid

SQLite tự tăng ID.

Ví dụ:

```text-x-trilium-auto
id

1

2

3

4
```

Sau khi INSERT.

```text-x-trilium-auto
cursor.lastrowid
```

Trả về:

```text-x-trilium-auto
4
```

---

# Read All

```text-x-trilium-auto
def get_all(self):

    cursor = self.db.cursor()

    cursor.execute("""
        SELECT *
        FROM notes
        ORDER BY updated_at DESC
    """)

    rows = cursor.fetchall()

    notes = []

    for row in rows:

        notes.append(

            Note(

                id=row["id"],

                title=row["title"],

                content=row["content"],

                created_at=row["created_at"],

                updated_at=row["updated_at"]

            )

        )

    return notes
```

---

## Tại sao trả về Note object?

Không nên:

```text-x-trilium-auto
[
    (1, "Python", "..."),
    (2, "SQLite", "...")
]
```

Nên:

```text-x-trilium-auto
[
    Note(...),
    Note(...)
]
```

Controller sẽ làm việc với object.

Đây là phong cách lập trình hướng đối tượng.

---

# Read One

```text-x-trilium-auto
def get(self, note_id):

    cursor = self.db.cursor()

    cursor.execute(

        "SELECT * FROM notes WHERE id=?",

        (note_id,)

    )

    row = cursor.fetchone()

    if row is None:

        return None

    return Note(

        id=row["id"],

        title=row["title"],

        content=row["content"],

        created_at=row["created_at"],

        updated_at=row["updated_at"]

    )
```

---

# Update

```text-x-trilium-auto
def update(self, note):

    now = datetime.now().isoformat()

    cursor = self.db.cursor()

    cursor.execute(

        """
        UPDATE notes

        SET

            title=?,

            content=?,

            updated_at=?

        WHERE id=?

        """,

        (

            note.title,

            note.content,

            now,

            note.id

        )

    )

    self.db.commit()
```

---

# Delete

```text-x-trilium-auto
def delete(self, note_id):

    cursor = self.db.cursor()

    cursor.execute(

        "DELETE FROM notes WHERE id=?",

        (note_id,)

    )

    self.db.commit()
```

---

# Luồng dữ liệu

Ví dụ:

Tạo ghi chú.

```text-x-trilium-auto
Controller

↓

model.create()

↓

SQLite

↓

id=5

↓

Controller
```

---

Hiển thị danh sách.

```text-x-trilium-auto
Controller

↓

model.get_all()

↓

SQLite

↓

List<Note>

↓

Controller

↓

View
```

---

# Điều rất quan trọng

View sẽ **không bao giờ** làm việc như thế này:

```text-x-trilium-auto
cursor.execute(...)
```

Sai.

View chỉ biết:

```text-x-trilium-auto
controller.load_notes()
```

Controller sẽ gọi:

```text-x-trilium-auto
model.get_all()
```

Model sẽ gọi:

```text-x-trilium-auto
SQLite
```

---

# Sơ đồ lớp

```text-x-trilium-auto
Database

│

├── cursor()

├── commit()

├── close()

└── create_tables()



↓

NoteModel

│

├── create()

├── get()

├── get_all()

├── update()

└── delete()



↓

Note
```

---

# Kiểm thử Model (không cần giao diện)

Một ưu điểm của việc tách Model là bạn có thể kiểm thử mà **không cần mở cửa sổ PySide6**.

Tạo tệp `test_model.py` ở thư mục gốc:

```text-x-trilium-auto
from model.note_model import NoteModel

model = NoteModel()

# Tạo ghi chú new_id = model.create("Ghi chú đầu tiên")
print(f"ID mới: {new_id}")

# Đọc tất cả for note in model.get_all():
    print(note)

# Đọc một ghi chú note = model.get(new_id)
print(note)

# Cập nhật note.content = "Đây là nội dung đã cập nhật." model.update(note)

# Xóa (bỏ comment nếu muốn thử) # model.delete(new_id)
```

Chạy:

```text-x-trilium-auto
python test_model.py
```

Nếu mọi thứ đúng, bạn đã kiểm thử được toàn bộ CRUD mà **không cần tạo** `**QApplication**`. Đây là một lợi ích rất lớn của kiến trúc MVC.

---

# Kiến thức quan trọng cần nhớ

Sau buổi 3, bạn nên nắm vững:

- **Database** chỉ quản lý kết nối SQLite và các thao tác cơ bản (`cursor`, `commit`, `close`).
- **Note** là lớp dữ liệu (Entity), đại diện cho một bản ghi trong bảng `notes`.
- **NoteModel** chứa toàn bộ nghiệp vụ truy cập dữ liệu (CRUD).
- **Model không phụ thuộc vào PySide6**, nên có thể tái sử dụng và kiểm thử độc lập.
- **Controller sẽ là lớp duy nhất gọi** `**NoteModel**` để lấy hoặc cập nhật dữ liệu.

---

# Bài tập thực hành

1. Bổ sung phương thức `count()` vào `NoteModel` để trả về tổng số ghi chú.
2. Bổ sung phương thức `search(keyword)` để tìm ghi chú theo tiêu đề (`LIKE '%keyword%'`).
3. Thêm cột `is_pinned INTEGER DEFAULT 0` vào bảng và cập nhật lớp `Note` để hỗ trợ ghim ghi chú.
4. Viết thêm một tệp `test_search.py` để kiểm thử chức năng tìm kiếm mà không cần giao diện.

---

# Buổi 4 (Preview)

Ở buổi tiếp theo, chúng ta sẽ bắt đầu xây dựng **Controller** đúng nghĩa:

- Kết nối các tín hiệu (signals) từ `LeftPanel` và `RightPanel`.
- Tải danh sách ghi chú từ `NoteModel` lên `QListWidget`.
- Khi người dùng bấm **+**, tạo ghi chú mới.
- Khi chọn một ghi chú trong danh sách, hiển thị tiêu đề và nội dung ở khung bên phải.

Đến hết buổi 4, ứng dụng sẽ lần đầu tiên hoạt động như một **phần mềm ghi chú thực sự**: tạo ghi chú, hiển thị danh sách và đọc nội dung từ cơ sở dữ liệu SQLite.
