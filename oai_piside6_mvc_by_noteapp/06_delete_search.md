# Buổi 6 - Xóa ghi chú, tìm kiếm và hoàn thiện giao diện

Đến buổi này, ứng dụng của chúng ta đã có thể:

- ✅ Tạo ghi chú
- ✅ Chọn ghi chú
- ✅ Chỉnh sửa
- ✅ Auto Save
- ✅ Lưu SQLite

Bây giờ chúng ta sẽ hoàn thiện các chức năng còn thiếu để ứng dụng có trải nghiệm giống một phần mềm thực tế.

---

# Mục tiêu buổi học

Sau buổi này, ứng dụng sẽ hỗ trợ:

- Xóa ghi chú
- Hộp thoại xác nhận trước khi xóa
- Tự động chọn ghi chú khác sau khi xóa
- Tìm kiếm theo tiêu đề
- Hiển thị số lượng ghi chú
- Cập nhật Status Bar

---

# Luồng xóa ghi chú

```text-x-trilium-auto
User

↓

Nhấn nút -

↓

QMessageBox

↓

Yes

↓

Controller

↓

Model.delete()

↓

SQLite

↓

Refresh List

↓

Chọn ghi chú khác

↓

Right Panel
```

---

# Bước 1. Kết nối nút Delete

Trong `connect_signals()`

```text-x-trilium-auto
left.btn_delete.clicked.connect(
    self.delete_note
)
```

---

# Bước 2. Hàm delete_note()

```text-x-trilium-auto
from PySide6.QtWidgets import QMessageBox
```

```text-x-trilium-auto
def delete_note(self):

    if self.current_note is None:
        return

    reply = QMessageBox.question(
        self.view,
        "Delete",
        "Delete this note?",
        QMessageBox.Yes | QMessageBox.No
    )

    if reply == QMessageBox.No:
        return

    self.model.delete(self.current_note.id)

    self.load_notes()

    self.current_note = None

    self.view.right_panel.clear()
```

---

# Giải thích

Nếu không hỏi xác nhận:

```text-x-trilium-auto
Click -

↓

Mất dữ liệu
```

Đây là trải nghiệm không tốt.

Nên luôn hỏi:

```text-x-trilium-auto
Delete this note?

[Yes]

[No]
```

---

# Bước 3. Tự động chọn ghi chú đầu tiên

Hiện tại sau khi xóa

```text-x-trilium-auto
QListWidget

↓

Không chọn gì
```

Không tiện.

Trong `load_notes()`

```text-x-trilium-auto
def load_notes(self):

    left = self.view.left_panel

    left.clear()

    notes = self.model.get_all()

    for note in notes:
        left.add_note(note)

    if left.note_list.count() > 0:
        left.note_list.setCurrentRow(0)
```

---

# Luồng

```text-x-trilium-auto
Delete

↓

Refresh

↓

Select Row 0

↓

RightPanel
```

---

# Nếu không còn ghi chú?

Nếu:

```text-x-trilium-auto
count()==0
```

Thì:

```text-x-trilium-auto
self.current_note = None

self.view.right_panel.clear()
```

---

# Bước 4. Thêm tìm kiếm

Toolbar đã có

```text-x-trilium-auto
search_edit
```

Ta kết nối

```text-x-trilium-auto
search_edit.textChanged.connect(
    self.search_note
)
```

---

# Trong Model

Thêm

```text-x-trilium-auto
def search(self, keyword):

    cursor = self.db.cursor()

    cursor.execute(

        """
        SELECT *

        FROM notes

        WHERE title LIKE ?

        ORDER BY updated_at DESC

        """,

        (f"%{keyword}%",)

    )

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

# search_note()

```text-x-trilium-auto
def search_note(self, text):

    left = self.view.left_panel

    left.clear()

    if text == "":

        notes = self.model.get_all()

    else:

        notes = self.model.search(text)

    for note in notes:

        left.add_note(note)
```

---

# Luồng

```text-x-trilium-auto
Typing

↓

Search

↓

SQLite

↓

ListWidget
```

---

# Bước 5. Đếm số ghi chú

Trong LeftPanel

Thêm

```text-x-trilium-auto
self.count_label = QLabel()
```

Cuối layout

```text-x-trilium-auto
layout.addWidget(
    self.count_label
)
```

---

Viết

```text-x-trilium-auto
def update_count(self):

    total = self.note_list.count()

    self.count_label.setText(

        f"Notes: {total}"

    )
```

---

Mỗi lần

```text-x-trilium-auto
load_notes()
```

Thêm

```text-x-trilium-auto
left.update_count()
```

---

Ví dụ

```text-x-trilium-auto
Notes: 12
```

---

# Bước 6. Hiển thị Status Bar

Sau khi tạo

```text-x-trilium-auto
self.view.statusBar().showMessage(

    "New note created"

)
```

---

Sau khi xóa

```text-x-trilium-auto
self.view.statusBar().showMessage(

    "Note deleted"

)
```

---

Sau khi tìm kiếm

```text-x-trilium-auto
self.view.statusBar().showMessage(

    f"Found {left.note_list.count()} notes"

)
```

---

# Cải thiện trải nghiệm

Nếu người dùng tìm

```text-x-trilium-auto
Docker
```

↓

Không có

Hiện

```text-x-trilium-auto
No note found.
```

---

# Tự động tạo ghi chú đầu tiên

Nếu

```text-x-trilium-auto
notes = self.model.get_all()
```

trả về

```text-x-trilium-auto
[]
```

Thì

```text-x-trilium-auto
self.model.create(
    "Welcome"
)

notes = self.model.get_all()
```

Như vậy lần đầu mở app sẽ luôn có một ghi chú.

---

# Tối ưu load_notes()

Đừng viết

```text-x-trilium-auto
self.model.get_all()
```

3 lần.

Nên

```text-x-trilium-auto
notes = self.model.get_all()
```

Chỉ một lần.

---

# Luồng hoàn chỉnh

```text-x-trilium-auto
Khởi động

↓

SQLite

↓

Controller

↓

ListWidget

↓

User Click

↓

RightPanel

↓

User Edit

↓

Timer

↓

SQLite

↓

Refresh

↓

Delete

↓

Refresh

↓

Search

↓

SQLite

↓

ListWidget
```

---

# Kiến thức mới

Hôm nay bạn đã học thêm:

## QMessageBox

Đây là widget rất quan trọng.

```text-x-trilium-auto
Information

Warning

Question

Critical
```

Hầu như mọi phần mềm đều dùng.

---

## LIKE trong SQLite

```text-x-trilium-auto
WHERE title LIKE '%python%'
```

Là cách tìm kiếm cơ bản.

---

## Status Bar

Một nơi rất hữu ích để thông báo:

```text-x-trilium-auto
Saving...

Saved

Deleted

Searching...

Ready
```

---

## Empty State

Nếu không có dữ liệu

↓

Đừng để màn hình trắng.

Hãy hiển thị

```text-x-trilium-auto
No notes
```

hoặc

```text-x-trilium-auto
Create your first note
```

Đây là UX (User Experience).

---

# Kiến thức kiến trúc

Đến đây dự án của chúng ta đã có kiến trúc khá chuẩn:

```text-x-trilium-auto
                    User

                      │

                      ▼

                MainWindow

             ┌─────────────┐
             │ Left Panel  │
             │ Right Panel │
             └─────────────┘

                      │

                  Signals

                      │

                      ▼

               NoteController

          ┌─────────┴─────────┐

          ▼                   ▼

      NoteModel         Current Note

          │

          ▼

       SQLite
```

Mỗi lớp đều có nhiệm vụ riêng:

- **View**: hiển thị và phát tín hiệu.
- **Controller**: xử lý luồng nghiệp vụ.
- **Model**: thao tác dữ liệu.
- **Database**: kết nối SQLite.

---

# Bài tập thực hành

1. Khi tìm kiếm, tìm cả trong **nội dung** (`content`) chứ không chỉ `title`.
2. Thêm nút **Clear Search** để xóa ô tìm kiếm và hiển thị lại toàn bộ ghi chú.
3. Hiển thị số ký tự của ghi chú hiện tại trên `StatusBar`, ví dụ:

```text-x-trilium-auto
Title: 18 chars | Content: 256 chars
```

4. Nếu người dùng xóa ghi chú cuối cùng, tự động tạo một ghi chú `"New Note"` để ứng dụng không rơi vào trạng thái trống.

---

# Buổi 7 (Bắt đầu nâng cấp kiến trúc)

Đến buổi 7, chúng ta sẽ **nâng cấp dự án lên cấp độ chuyên nghiệp**, không chỉ thêm tính năng mà còn cải thiện kiến trúc:

- Tách **Repository** ra khỏi `NoteModel` (Repository Pattern).
- Thêm **Service Layer** để xử lý nghiệp vụ.
- Sử dụng **Qt Model/View** (`QAbstractListModel`) thay cho `QListWidget` để hiển thị hàng nghìn ghi chú hiệu quả.
- Chuẩn bị nền tảng cho các tính năng lớn như **Tag**, **Notebook**, **Markdown**, **Undo/Redo**, **Export PDF**.

Từ buổi 7 trở đi, dự án sẽ tiến dần đến kiến trúc của các ứng dụng desktop chuyên nghiệp, đủ khả năng mở rộng mà không phải sửa lại toàn bộ mã nguồn.
