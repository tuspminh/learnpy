# Phần III — UI Architecture

## Buổi 25 — Tách UI khỏi Business Logic

Đây là buổi **rất quan trọng**. Từ buổi này chúng ta bắt đầu chuyển từ tư duy:

> "Viết một app PySide6 chạy được"

sang:

> "Thiết kế một app PySide6 có kiến trúc tốt, dễ test, dễ mở rộng."

Đặc biệt, kiến thức này sẽ là nền móng cho các buổi **MVC → MVVM → Controller → Service → Repository → DI → Event Bus** và cuối cùng là project **Story Reader Desktop**.

---

# 1. Vấn đề: nhét tất cả vào `MainWindow`

Một người mới thường viết:

```python
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.input = QLineEdit()
        self.button = QPushButton("Add")

        layout = QVBoxLayout()
        layout.addWidget(self.input)
        layout.addWidget(self.button)

        central = QWidget()
        central.setLayout(layout)

        self.setCentralWidget(central)

        self.button.clicked.connect(self.add_user)

    def add_user(self):
        name = self.input.text()

        if not name:
            QMessageBox.warning(
                self,
                "Error",
                "Name is required",
            )
            return

        # business logic
        if len(name) < 3:
            QMessageBox.warning(
                self,
                "Error",
                "Name too short",
            )
            return

        # database
        print(f"INSERT INTO users ... {name}")

        QMessageBox.information(
            self,
            "Success",
            "User created",
        )
```

Code này **chạy được**.

Nhưng kiến trúc có vấn đề.

---

# 2. `MainWindow` đang làm quá nhiều việc

Trong ví dụ trên:

```text
MainWindow
   │
   ├── UI
   │
   ├── Input validation
   │
   ├── Business logic
   │
   ├── Database
   │
   ├── Error handling
   │
   └── Notification
```

Một class đang đảm nhiệm quá nhiều trách nhiệm.

Đây chính là vấn đề mà chúng ta đã học trong SOLID:

> **SRP — Single Responsibility Principle**

`MainWindow` nên chủ yếu chịu trách nhiệm về **presentation/UI**.

Không nên biết:

```python
INSERT INTO users ...
```

Không nên quyết định:

```python
if len(name) < 3:
```

Không nên chứa business rule phức tạp.

---

# 3. Mental Model

Hãy chia ứng dụng thành các tầng.

```text
┌─────────────────────────┐
│          UI             │
│       PySide6           │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│    Application Logic    │
│      / Use Case         │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│     Business Logic      │
│        Domain           │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Infrastructure / DB     │
└─────────────────────────┘
```

Ví dụ:

```text
User click "Add"
       │
       ▼
     UI
       │
       ▼
CreateUser
       │
       ▼
 User rules
       │
       ▼
 Repository
       │
       ▼
    SQLite
```

Điểm quan trọng:

> UI không cần biết **database hoạt động như thế nào**.

---

# 4. UI nên làm gì?

UI có thể:

### Nhận input

```python
name = self.input.text()
```

### Hiển thị dữ liệu

```python
self.label.setText(name)
```

### Phát event

```python
self.button.clicked.connect(...)
```

### Hiển thị lỗi

```python
QMessageBox.warning(...)
```

### Hiển thị loading

```python
self.progress.show()
```

Nhưng UI không nên chứa business rule lớn.

---

# 5. Business Logic là gì?

Ví dụ application quản lý sách.

Rule:

```text
Một Story phải có title.
Title không được rỗng.
Title tối đa 200 ký tự.
```

Đây là business rule.

Không nên viết:

```python
class StoryWindow(QMainWindow):

    def save(self):
        title = self.input.text()

        if not title:
            ...
```

và để rule nằm trong UI.

Thay vào đó:

```python
class Story:

    def __init__(self, title: str):
        title = title.strip()

        if not title:
            raise ValueError("Title is required")

        if len(title) > 200:
            raise ValueError("Title too long")

        self.title = title
```

Bây giờ rule không còn phụ thuộc PySide6.

---

# 6. Tại sao điều này quan trọng?

Ta có thể test:

```python
def test_story_title_required():
    try:
        Story("")
    except ValueError:
        assert True
```

Không cần:

```python
QApplication(...)
```

Không cần:

```python
QMainWindow(...)
```

Không cần:

```python
QMessageBox
```

Đây là một trong những lợi ích lớn nhất của việc tách UI.

---

# 7. Ví dụ kiến trúc đơn giản

Ta xây:

```text
User
 │
 ├── name
 │
 └── email
```

Business layer:

```python
class UserService:

    def create_user(self, name: str, email: str):
        name = name.strip()
        email = email.strip()

        if not name:
            raise ValueError("Name is required")

        if "@" not in email:
            raise ValueError("Invalid email")

        print("Create user")

        return {
            "name": name,
            "email": email,
        }
```

UI:

```python
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.service = UserService()

        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.button = QPushButton("Create")

        layout = QVBoxLayout()

        layout.addWidget(self.name_input)
        layout.addWidget(self.email_input)
        layout.addWidget(self.button)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

        self.button.clicked.connect(self.create_user)

    def create_user(self):
        try:
            user = self.service.create_user(
                self.name_input.text(),
                self.email_input.text(),
            )

        except ValueError as e:
            QMessageBox.warning(
                self,
                "Error",
                str(e),
            )
            return

        QMessageBox.information(
            self,
            "Success",
            f"Created {user['name']}",
        )
```

Đã tốt hơn rất nhiều.

---

# 8. Nhưng vẫn chưa hoàn hảo

Ta vẫn có:

```python
self.service = UserService()
```

trong UI.

Điều này tạo coupling:

```text
MainWindow
     │
     │ depends directly
     ▼
UserService
```

Sau này chúng ta sẽ học:

> **Dependency Injection**

ở Buổi 31.

Nhưng hiện tại chưa cần giải quyết.

---

# 9. UI → Service

Hãy hình dung:

```text
             PySide6
                │
                │ user action
                ▼
        ┌───────────────┐
        │  MainWindow   │
        └───────┬───────┘
                │
                │ create_user()
                ▼
        ┌───────────────┐
        │  UserService  │
        └───────┬───────┘
                │
                ▼
           Business
```

UI nói:

> "User vừa click Create."

Service quyết định:

> "Có được phép tạo User hay không?"

Đây là sự phân chia trách nhiệm.

---

# 10. Một nguyên tắc cực kỳ quan trọng

Hãy nhớ:

> **UI nên biết "làm thế nào để hiển thị".**

> **Business layer nên biết "điều gì được phép xảy ra".**

Ví dụ:

### UI

```python
self.button.setEnabled(False)
```

UI concern.

### Business

```python
if story.status == "completed":
    raise ValueError("Cannot add chapter")
```

Business concern.

---

# 11. Không có nghĩa là UI không được validation

Đây là điểm rất dễ hiểu sai.

Ví dụ:

```python
QLineEdit
```

có thể dùng:

```python
QIntValidator
```

Đó là **UI validation**.

Ví dụ:

```text
Age
 ↓
"abc"
 ↓
UI chặn
```

Hoàn toàn hợp lý.

Nhưng business rule:

```text
User phải >= 18 tuổi
```

không nên chỉ nằm trong UI.

Bởi vì sau này có thể có:

```text
PySide6 UI
       │
CLI ───┤
       │
REST API
       │
       ▼
   UserService
```

Tất cả đều phải tuân thủ:

```text
age >= 18
```

---

# 12. Presentation Validation vs Business Validation

Đây là distinction rất quan trọng.

| Loại                | Ví dụ                          | Nơi xử lý |
| ------------------- | ------------------------------ | --------- |
| UI validation       | Chỉ cho nhập số                | UI        |
| UI validation       | Required field                 | UI        |
| UI validation       | Format email                   | UI        |
| Business rule       | User phải >= 18                | Domain    |
| Business rule       | Story không được trùng chapter | Domain    |
| Business rule       | Không thể publish story rỗng   | Domain    |
| Database constraint | UNIQUE                         | Database  |

Có thể có nhiều tầng validation.

---

# 13. Refactor ví dụ Todo

Giả sử Todo App:

```python
class TodoWindow(QMainWindow):

    def add_todo(self):
        title = self.input.text()

        if not title:
            return

        if len(title) > 100:
            return

        self.todos.append(title)

        self.list_widget.addItem(title)
```

Ta tách:

```text
TodoWindow
      │
      ▼
TodoService
      │
      ▼
Todo
```

---

## Domain

```python
class Todo:

    def __init__(self, title: str):
        title = title.strip()

        if not title:
            raise ValueError("Todo title is required")

        if len(title) > 100:
            raise ValueError(
                "Todo title must be <= 100 characters"
            )

        self.title = title
```

---

## Service

```python
class TodoService:

    def create(self, title: str) -> Todo:
        todo = Todo(title)

        # Sau này:
        # repository.save(todo)

        return todo
```

---

## UI

```python
class TodoWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.service = TodoService()

        self.input = QLineEdit()
        self.button = QPushButton("Add")

        self.button.clicked.connect(
            self.add_todo
        )

    def add_todo(self):
        try:
            todo = self.service.create(
                self.input.text()
            )

        except ValueError as e:
            QMessageBox.warning(
                self,
                "Invalid Todo",
                str(e),
            )
            return

        print(todo.title)
```

UI đã trở nên khá mỏng.

---

# 14. "Thin UI"

Một architecture tốt thường hướng đến:

```text
UI
│
├── nhận input
├── gọi application/service
├── nhận kết quả
└── render
```

Thay vì:

```text
UI
│
├── input
├── validation
├── business
├── database
├── networking
├── threading
├── caching
├── logging
├── file system
└── rendering
```

Ta gọi ý tưởng đầu tiên là:

> **Thin UI**

---

# 15. UI không nên gọi Database trực tiếp

Ví dụ không nên:

```python
class MainWindow:

    def save(self):
        conn = sqlite3.connect("app.db")

        conn.execute(
            "INSERT INTO story ..."
        )

        conn.commit()
```

Bởi vì:

```text
MainWindow
    ↓
SQLite
```

làm UI phụ thuộc infrastructure.

Sau này:

```text
MainWindow
     ↓
Application Service
     ↓
Repository
     ↓
SQLite
```

Đây chính là hướng chúng ta sẽ xây trong các buổi tiếp theo.

---

# 16. Từ đây hình thành kiến trúc

Chúng ta đang tiến dần tới:

```text
┌──────────────────────────────┐
│         Presentation         │
│                              │
│       PySide6 Widgets        │
│       Qt Models              │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│        Application           │
│                              │
│       Use Cases              │
│       Services               │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│           Domain             │
│                              │
│       Entity                 │
│       Value Object           │
│       Business Rules         │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Infrastructure         │
│                              │
│       SQLite                 │
│       HTTP                   │
│       File System            │
└──────────────────────────────┘
```

Đây cũng rất gần với những gì bạn đã học về **Clean Architecture / DDD / SOLID**.

---

# 17. Một nguyên tắc kiến trúc quan trọng

Ta muốn dependency đi theo hướng:

```text
UI
 ↓
Application
 ↓
Domain
```

và:

```text
Infrastructure
```

được kết nối thông qua abstraction ở các buổi sau.

Không muốn:

```text
Domain
 ↓
PySide6
```

Ví dụ **sai**:

```python
class Story:

    def save(self):
        QMessageBox.information(...)
```

Domain không nên biết PySide6 tồn tại.

---

# 18. Một cách kiểm tra rất hay

Khi viết một class, hãy hỏi:

> **"Nếu bỏ PySide6 ra, class này còn hoạt động được không?"**

Ví dụ:

```python
class Story:
    ...
```

Nếu có thể chạy:

```python
story = Story("Harry Potter")
```

mà không cần QApplication → tốt.

---

Còn:

```python
class Story:

    def save(self):
        QMessageBox(...)
```

thì:

```text
Story
 ↓
PySide6
```

Coupling quá mạnh.

---

# 19. Bài tập 1 — Refactor

Cho code:

```python
class MainWindow(QMainWindow):

    def add_story(self):
        title = self.title_input.text()

        if not title:
            QMessageBox.warning(
                self,
                "Error",
                "Title required",
            )
            return

        if len(title) > 200:
            QMessageBox.warning(
                self,
                "Error",
                "Title too long",
            )
            return

        conn = sqlite3.connect("stories.db")

        conn.execute(
            "INSERT INTO stories(title) VALUES(?)",
            (title,),
        )

        conn.commit()

        QMessageBox.information(
            self,
            "Success",
            "Story added",
        )
```

Hãy xác định:

```text
UI responsibility
Business responsibility
Infrastructure responsibility
```

---

# 20. Bài tập 2 — Thiết kế lại

Hãy đưa code về:

```text
MainWindow
     │
     ▼
StoryService
     │
     ▼
Story
```

Chưa cần Repository.

Mục tiêu:

```python
story = service.create_story(title)
```

và `MainWindow` không chứa:

```python
sqlite3
```

---

# 21. Bài tập 3 — Câu hỏi kiến trúc

Hãy trả lời 5 câu:

### Câu 1

`QMessageBox` thuộc layer nào?

### Câu 2

`Story.title không được rỗng` thuộc layer nào?

### Câu 3

`SQLite INSERT` thuộc layer nào?

### Câu 4

`QLineEdit` chỉ cho nhập số thuộc layer nào?

### Câu 5

Nếu đổi SQLite thành PostgreSQL, class nào **không nên phải sửa**?

---

# 22. Mini Project — Todo App v2

Ở Buổi 10 chúng ta có:

```text
Todo App v1
```

Bây giờ hãy nâng cấp thành:

```text
Todo App v2
```

Kiến trúc:

```text
todo_app/
│
├── main.py
│
├── domain/
│   └── todo.py
│
├── application/
│   └── todo_service.py
│
└── presentation/
    └── main_window.py
```

Luồng:

```text
                 User
                  │
                  ▼
            MainWindow
                  │
                  │ create()
                  ▼
            TodoService
                  │
                  ▼
                Todo
```

Chưa cần:

```text
Repository
Database
Thread
Event Bus
Dependency Injection
```

Chúng ta sẽ bổ sung dần.

---

# 23. Kiến thức quan trọng nhất của Buổi 25

Nếu chỉ nhớ **5 điều**, hãy nhớ:

### 1.

```text
UI ≠ Business Logic
```

### 2.

```text
UI ≠ Database
```

### 3.

Business rule nên độc lập với PySide6.

### 4.

Hướng tới:

```text
Thin UI
```

### 5.

Thiết kế dependency:

```text
Presentation
      ↓
Application
      ↓
Domain
```

thay vì:

```text
Everything
    ↓
MainWindow
```

---

# 24. Nhìn trước Buổi 26

Buổi 25 mới chỉ trả lời:

> **Tại sao phải tách UI khỏi Business Logic?**

Buổi 26 chúng ta sẽ đi sâu vào:

# **MVC trong PySide6**

Ta sẽ xây mô hình:

```text
              ┌───────────┐
              │   Model   │
              └─────┬─────┘
                    │
             data / state
                    │
                    ▼
┌───────────┐             ┌──────────────┐
│   View    │ ◄────────── │  Controller  │
└───────────┘             └──────────────┘
      │                          │
      └──────── user action ─────┘
```

Và quan trọng hơn, chúng ta sẽ phân biệt **MVC truyền thống** với **Qt Model/View**, bởi vì hai khái niệm này rất dễ bị nhầm lẫn khi học PySide6.
