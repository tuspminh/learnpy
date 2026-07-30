# Buổi 7 - Nâng cấp kiến trúc với Repository Pattern và Service Layer

> **Đây là buổi quan trọng nhất về kiến trúc phần mềm.**

Từ buổi 1 → buổi 6, ứng dụng của chúng ta hoạt động rất tốt.

Nhưng nếu dự án phát triển lên:

- 5.000 ghi chú
- 50.000 ghi chú
- Tag
- Notebook
- Trash
- Markdown
- Sync Cloud
- AI Assistant

thì kiến trúc hiện tại sẽ bắt đầu bộc lộ hạn chế.

Hôm nay chúng ta sẽ **refactor** (cải tiến kiến trúc) giống như cách các lập trình viên chuyên nghiệp làm.

---

# Tại sao phải Refactor?

Hiện tại Controller gọi trực tiếp Model.

```text-x-trilium-auto
Controller

↓

NoteModel

↓

SQLite
```

Controller biết quá nhiều.

Ví dụ:

```text-x-trilium-auto
self.model.create(...)

self.model.delete(...)

self.model.search(...)

self.model.update(...)
```

Nếu sau này:

SQLite

↓

PostgreSQL

↓

MongoDB

↓

REST API

↓

Cloud

Controller sẽ phải sửa rất nhiều.

Đây là điều chúng ta không muốn.

---

# Kiến trúc mới

Thay vì

```text-x-trilium-auto
Controller

↓

Model

↓

SQLite
```

Ta sẽ có

```text-x-trilium-auto
Controller

↓

Service

↓

Repository

↓

Database

↓

SQLite
```

Đây là kiến trúc được sử dụng rất nhiều trong:

- Django
- Spring Boot
- ASP.NET
- Flutter
- Android
- Enterprise Python

---

# Kiến trúc tổng thể

```text-x-trilium-auto
                    User

                      │

                      ▼

                 MainWindow

                      │

                      ▼

                NoteController

                      │

                      ▼

                 NoteService

                      │

                      ▼

               NoteRepository

                      │

                      ▼

                  Database

                      │

                      ▼

                   SQLite
```

---

# Vai trò từng lớp

## View

Hiển thị giao diện.

Không biết SQLite.

Không biết SQL.

---

## Controller

Điều khiển giao diện.

Ví dụ:

```text-x-trilium-auto
Button

↓

Create Note
```

---

## Service

Xử lý nghiệp vụ.

Ví dụ:

Nếu title rỗng

↓

Đổi thành

```text-x-trilium-auto
Untitled
```

Hoặc

Nếu nội dung quá dài

↓

Tự động cắt.

---

## Repository

Chỉ làm SQL.

Ví dụ

```text-x-trilium-auto
INSERT

UPDATE

DELETE

SELECT
```

---

## Database

Quản lý connection.

---

# Thư mục mới

```text-x-trilium-auto
note_app/

database/

model/

repository/
    note_repository.py

service/
    note_service.py

controller/

view/
```

---

# Bước 1 - Tạo Repository

File

```text-x-trilium-auto
repository/note_repository.py
```

```text-x-trilium-auto
from database.database import Database from model.note import Note from datetime import datetime


class NoteRepository:

    def __init__(self):
        self.db = Database()
```

---

## create()

Đưa toàn bộ SQL từ `NoteModel` sang đây.

```text-x-trilium-auto
def create(self, title):

    now = datetime.now().isoformat()

    cursor = self.db.cursor()

    cursor.execute(
        """
        INSERT INTO notes(
            title,
            content,
            created_at,
            updated_at
        )
        VALUES(?,?,?,?)
        """,
        (
            title,
            "",
            now,
            now
        )
    )

    self.db.commit()

    return cursor.lastrowid
```

Tương tự:

- get()
- get_all()
- update()
- delete()
- search()

đều chuyển sang Repository.

---

# Repository có nhiệm vụ gì?

Repository chỉ biết

```text-x-trilium-auto
Python Object

↓

SQL

↓

SQLite

↓

Python Object
```

Không biết GUI.

Không biết Button.

Không biết Timer.

---

# Bước 2 - Tạo Service

File

```text-x-trilium-auto
service/note_service.py
```

```text-x-trilium-auto
from repository.note_repository import NoteRepository


class NoteService:

    def __init__(self):

        self.repo = NoteRepository()
```

---

# create_note()

```text-x-trilium-auto
def create_note(self, title):

    title = title.strip()

    if title == "":
        title = "Untitled"

    return self.repo.create(title)
```

---

Tại sao làm ở đây?

Sai:

```text-x-trilium-auto
Controller

↓

if title=="":
```

Nếu sau này có

- Mobile App
- Web App

Ta phải viết lại.

Đúng:

```text-x-trilium-auto
Controller

↓

Service

↓

Repository
```

Mọi luật nghiệp vụ đều nằm trong Service.

---

# update_note()

```text-x-trilium-auto
def update_note(self, note):

    note.title = note.title.strip()

    if note.title == "":
        note.title = "Untitled"

    self.repo.update(note)
```

---

# search()

```text-x-trilium-auto
def search(self, keyword):

    keyword = keyword.strip()

    return self.repo.search(keyword)
```

---

# Bước 3 - Controller

Controller không còn dùng

```text-x-trilium-auto
NoteModel
```

Thay bằng

```text-x-trilium-auto
from service.note_service import NoteService
```

```text-x-trilium-auto
self.service = NoteService()
```

---

Sau đó

Sai

```text-x-trilium-auto
self.model.create(...)
```

Đúng

```text-x-trilium-auto
self.service.create_note(...)
```

---

Sai

```text-x-trilium-auto
self.model.update(...)
```

Đúng

```text-x-trilium-auto
self.service.update_note(...)
```

---

Controller không còn biết SQL.

---

# Luồng mới

```text-x-trilium-auto
Button

↓

Controller

↓

Service

↓

Repository

↓

SQLite
```

---

# Tại sao Repository tốt?

Giả sử sau này

SQLite

↓

MySQL

Bạn chỉ sửa

```text-x-trilium-auto
NoteRepository
```

Controller không đổi.

View không đổi.

---

# Tại sao Service tốt?

Giả sử thêm luật

```text-x-trilium-auto
Title dài tối đa

100 ký tự
```

Bạn chỉ sửa

```text-x-trilium-auto
create_note()
```

Không sửa Controller.

---

# Ví dụ thực tế

Một ứng dụng ngân hàng.

```text-x-trilium-auto
Controller

↓

Transfer()

↓

Service

↓

Kiểm tra số dư

↓

Repository

↓

UPDATE account

↓

SQLite
```

Service chính là nơi kiểm tra

```text-x-trilium-auto
Có đủ tiền không?
```

Repository không kiểm tra.

Repository chỉ UPDATE.

---

# Nguyên tắc SOLID

Hôm nay chúng ta vô tình áp dụng:

## Single Responsibility

Một lớp

↓

Một nhiệm vụ.

Ví dụ

```text-x-trilium-auto
Repository

↓

SQL
```

---

```text-x-trilium-auto
Service

↓

Business Logic
```

---

```text-x-trilium-auto
Controller

↓

Signal
```

---

# Dependency

Sau refactor

```text-x-trilium-auto
Controller

↓

Service

↓

Repository

↓

Database
```

Không có chiều ngược lại.

Đây là kiến trúc rất đẹp.

---

# Chuẩn bị cho hàng nghìn ghi chú

Hiện tại

```text-x-trilium-auto
QListWidget
```

vẫn ổn.

Nhưng

```text-x-trilium-auto
10000 ghi chú
```

sẽ chậm.

Buổi sau chúng ta sẽ thay bằng

```text-x-trilium-auto
QAbstractListModel
```

là mô hình Qt Model/View thật sự.

Đây là cách:

- Qt Creator
- KDE
- VLC
- Autodesk Maya

quản lý dữ liệu lớn.

---

# Cấu trúc mới

```text-x-trilium-auto
note_app/

database/

model/

repository/

service/

controller/

view/

resources/

tests/
```

Bạn sẽ thấy kiến trúc này rất giống các dự án chuyên nghiệp.

---

# Kiến thức mới học được

Trong buổi này, bạn đã tiếp cận các khái niệm kiến trúc quan trọng:

- **Repository Pattern**: tách toàn bộ truy vấn SQL khỏi Controller và Service.
- **Service Layer**: tập trung toàn bộ nghiệp vụ (business logic), ví dụ chuẩn hóa tiêu đề hoặc kiểm tra dữ liệu.
- **Single Responsibility Principle (SRP)**: mỗi lớp chỉ có một trách nhiệm.
- **Dễ mở rộng**: thay đổi nguồn dữ liệu hoặc quy tắc nghiệp vụ mà không ảnh hưởng đến giao diện.

Đây là những nguyên tắc được áp dụng trong rất nhiều framework hiện đại.

---

# Bài tập thực hành

1. Di chuyển toàn bộ các câu lệnh SQL từ `NoteModel` sang `NoteRepository`, sau đó loại bỏ `NoteModel`.
2. Thêm một quy tắc trong `NoteService`: nếu tiêu đề dài hơn **100 ký tự**, tự động cắt còn 100 ký tự.
3. Thêm phương thức `rename_note(note_id, new_title)` vào `NoteService`, phương thức này sẽ:
  - `strip()` tiêu đề.
  - Thay tiêu đề rỗng bằng `"Untitled"`.
  - Gọi `NoteRepository` để cập nhật.
4. Tạo thư mục `tests/` và viết một bài kiểm thử đơn giản cho `NoteService.create_note()` mà **không cần chạy giao diện PySide6**.

---

# Buổi 8 (Rất quan trọng)

Ở buổi tiếp theo, chúng ta sẽ bắt đầu học **Qt Model/View Framework** – một trong những phần mạnh nhất của Qt.

Thay vì dùng `QListWidget`, chúng ta sẽ xây dựng:

- `QAbstractListModel`
- `QListView`
- Custom Model
- Custom Delegate (giới thiệu)
- Hiển thị hàng chục nghìn ghi chú một cách mượt mà

Đây là bước chuyển từ cách làm "widget-based" sang "model/view-based", cũng là nền tảng của các ứng dụng Qt chuyên nghiệp như **Qt Creator**, **KDE Dolphin**, **Maya** và nhiều phần mềm desktop lớn khác.
