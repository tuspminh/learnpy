# Buổi 4 - Xây dựng Controller và kết nối View với Model

Đây là buổi mà ứng dụng của chúng ta **bắt đầu "sống"**.

Ở 3 buổi trước:

- ✅ Đã có giao diện
- ✅ Đã có SQLite
- ✅ Đã có Model

Nhưng tất cả vẫn chưa nói chuyện với nhau.

Hôm nay chúng ta sẽ xây dựng **Controller**.

Đây chính là "bộ não" của ứng dụng.

---

# Mục tiêu buổi học

Sau buổi này ứng dụng sẽ hoạt động như sau:

```text-x-trilium-auto
Khởi động App
        │
        ▼
Đọc tất cả ghi chú từ SQLite
        │
        ▼
Hiển thị lên QListWidget
        │
        ▼
Click một ghi chú
        │
        ▼
Tiêu đề và nội dung xuất hiện bên phải
        │
        ▼
Nhấn nút +
        │
        ▼
Tạo ghi chú mới
        │
        ▼
Refresh danh sách
```

Chúng ta **chưa lưu khi gõ**, việc đó sẽ làm ở buổi 5.

---

# Controller là gì?

Đây là điều quan trọng nhất của MVC.

Controller **không tạo giao diện**.

Controller **không viết SQL**.

Controller chỉ làm nhiệm vụ điều phối.

Ví dụ:

```text-x-trilium-auto
Button +

↓

Controller

↓

Model.create()

↓

SQLite

↓

Controller

↓

Refresh View
```

---

# Luồng chương trình

```text-x-trilium-auto
MainWindow

↓

LeftPanel

↓

User Click

↓

Controller

↓

NoteModel

↓

SQLite

↓

Controller

↓

RightPanel
```

---

# Chúng ta sẽ sửa những file nào?

```text-x-trilium-auto
controller/

    note_controller.py

view/

    left_panel.py

    right_panel.py

main.py
```

---

# Bước 1 - Chuẩn bị LeftPanel

Hiện tại chúng ta đã có

```text-x-trilium-auto
self.note_list
```

Đây là QListWidget.

Mỗi dòng trong danh sách sẽ đại diện cho một Note.

Ví dụ

```text-x-trilium-auto
Python

SQLite

MVC

Docker
```

---

## Thêm hàm clear()

Trong `LeftPanel`

```text-x-trilium-auto
def clear(self):

    self.note_list.clear()
```

---

## Thêm hàm add_note()

```text-x-trilium-auto
from PySide6.QtWidgets import QListWidgetItem
```

```text-x-trilium-auto
def add_note(self, note):

    item = QListWidgetItem(note.title)

    item.setData(Qt.UserRole, note.id)

    self.note_list.addItem(item)
```

---

## Vì sao dùng Qt.UserRole?

Một QListWidget chỉ hiển thị:

```text-x-trilium-auto
Python
```

Nhưng trong SQLite

```text-x-trilium-auto
id = 12

title = Python
```

Ta phải lưu ID.

Qt cho phép lưu dữ liệu ẩn.

```text-x-trilium-auto
item.setData(Qt.UserRole, note.id)
```

Sau này lấy lại:

```text-x-trilium-auto
item.data(Qt.UserRole)
```

Rất quan trọng.

---

# Bước 2 - Chuẩn bị RightPanel

Thêm

```text-x-trilium-auto
def show_note(self, note):

    self.title_edit.setText(note.title)

    self.content_edit.setPlainText(note.content)
```

---

Thêm

```text-x-trilium-auto
def clear(self):

    self.title_edit.clear()

    self.content_edit.clear()
```

---

# Bước 3 - Viết Controller

Đây là phần quan trọng nhất.

```text-x-trilium-auto
from model.note_model import NoteModel


class NoteController:

    def __init__(self, view):

        self.view = view

        self.model = NoteModel()

        self.current_note = None

        self.connect_signals()

        self.load_notes()
```

---

## current_note

Biến này lưu

```text-x-trilium-auto
Note đang mở
```

Ví dụ

```text-x-trilium-auto
Python
```

↓

Người dùng sửa

↓

Controller biết đang sửa note nào.

---

# connect_signals()

```text-x-trilium-auto
def connect_signals(self):

    left = self.view.left_panel

    left.btn_add.clicked.connect(

        self.create_note

    )

    left.note_list.currentItemChanged.connect(

        self.select_note

    )
```

---

## Signal

```text-x-trilium-auto
Button

↓

clicked

↓

Controller
```

Đây là nguyên lý Signal / Slot của Qt.

---

# load_notes()

```text-x-trilium-auto
def load_notes(self):

    left = self.view.left_panel

    left.clear()

    notes = self.model.get_all()

    for note in notes:

        left.add_note(note)
```

---

Luồng

```text-x-trilium-auto
SQLite

↓

Model

↓

Controller

↓

QListWidget
```

---

# create_note()

```text-x-trilium-auto
def create_note(self):

    note_id = self.model.create(

        "New Note"

    )

    self.load_notes()

    self.select_by_id(note_id)
```

---

Sau khi tạo

```text-x-trilium-auto
SQLite

↓

id=10

↓

Refresh

↓

Tự chọn note mới
```

---

# select_by_id()

```text-x-trilium-auto
def select_by_id(self, note_id):

    list_widget = self.view.left_panel.note_list

    for row in range(list_widget.count()):

        item = list_widget.item(row)

        if item.data(Qt.UserRole) == note_id:

            list_widget.setCurrentItem(item)

            return
```

---

# select_note()

Đây là hàm quan trọng nhất.

```text-x-trilium-auto
def select_note(self, current, previous):

    if current is None:

        return

    note_id = current.data(Qt.UserRole)

    note = self.model.get(note_id)

    self.current_note = note

    self.view.right_panel.show_note(note)
```

---

Luồng

```text-x-trilium-auto
Click QListWidget

↓

currentItemChanged

↓

Controller

↓

Model.get()

↓

SQLite

↓

Note Object

↓

RightPanel
```

---

# Điều gì xảy ra khi click?

Ví dụ người dùng click

```text-x-trilium-auto
SQLite
```

QListWidget gửi

```text-x-trilium-auto
item
```

↓

Controller lấy

```text-x-trilium-auto
item.data(Qt.UserRole)
```

↓

Có id

↓

Model

↓

SQLite

↓

Đọc dữ liệu

↓

RightPanel

---

# main.py

Không cần thay đổi nhiều.

```text-x-trilium-auto
window = MainWindow()

controller = NoteController(window)

window.show()
```

Controller sẽ tự:

- kết nối signal
- load dữ liệu

---

# Luồng hoàn chỉnh

## Khi mở chương trình

```text-x-trilium-auto
main.py

↓

Controller

↓

load_notes()

↓

SQLite

↓

QListWidget
```

---

## Khi tạo

```text-x-trilium-auto
+

↓

create_note()

↓

SQLite

↓

Refresh

↓

Select

↓

Hiện bên phải
```

---

## Khi click

```text-x-trilium-auto
QListWidget

↓

Signal

↓

Controller

↓

SQLite

↓

RightPanel
```

---

# Kiến thức mới: Signal không nên xử lý trực tiếp trong View

Sai:

```text-x-trilium-auto
self.btn_add.clicked.connect(
    lambda:
        sqlite.execute(...)
)
```

View đang truy cập SQLite.

Đó là vi phạm MVC.

Đúng:

```text-x-trilium-auto
clicked

↓

Controller

↓

Model

↓

SQLite
```

---

# Tại sao Controller lưu `current_note`?

Giả sử người dùng đang sửa:

```text-x-trilium-auto
Python
```

Làm sao biết ghi xuống database dòng nào?

Controller nhớ

```text-x-trilium-auto
self.current_note.id
```

Buổi sau chỉ cần

```text-x-trilium-auto
update(current_note)
```

Không cần tìm lại.

---

# Cấu trúc MVC sau buổi 4

```text-x-trilium-auto
                   User

                     │

                     ▼

             MainWindow(View)

                     │

          Signal / Slot

                     │

                     ▼

             NoteController

             │            │

             ▼            ▼

      NoteModel      current_note

             │

             ▼

          SQLite
```

Đến đây bạn đã có một ứng dụng đúng mô hình MVC: **View chỉ hiển thị**, **Model chỉ thao tác dữ liệu**, **Controller điều phối mọi tương tác**.

---

# Bài tập thực hành

1. Khi tạo ghi chú mới, thay tiêu đề mặc định `"New Note"` thành `"Untitled"`.
2. Sau khi chọn ghi chú, hiển thị thông báo trên `StatusBar`:

```text-x-trilium-auto
Loaded: Python
```

3. Nếu cơ sở dữ liệu chưa có ghi chú nào, tự động tạo một ghi chú đầu tiên khi khởi động ứng dụng.
4. Thêm nút **Refresh** trên `QToolBar` và khi bấm sẽ gọi `load_notes()`.

---

# Buổi 5 (Rất quan trọng)

Đây sẽ là buổi biến ứng dụng thành một phần mềm ghi chú thực thụ. Chúng ta sẽ xây dựng:

- **Auto Save** khi người dùng gõ tiêu đề hoặc nội dung.
- Tránh lưu liên tục bằng `QTimer` (debounce).
- Đánh dấu trạng thái "đã chỉnh sửa".
- Cập nhật `updated_at`.
- Tự động làm mới danh sách khi tiêu đề thay đổi.

Đây cũng là dịp để học cách xử lý các sự kiện `textChanged`, tránh vòng lặp tín hiệu (signal loop) và xây dựng trải nghiệm người dùng mượt mà như các ứng dụng ghi chú chuyên nghiệp.
