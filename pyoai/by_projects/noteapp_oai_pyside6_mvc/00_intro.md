Rất hay. Đây là một dự án rất phù hợp để học **PySide6 + MVC + SQLite3**. Nếu làm đúng cách thì sau dự án này bạn sẽ có nền tảng để xây dựng các ứng dụng lớn hơn như Todo, Password Manager, Student Manager, Knowledge Base...

## Mục tiêu khóa học

Chúng ta sẽ xây dựng ứng dụng **Simple Note**.

```text-x-trilium-auto
+-----------------------------------------------------------+
| Toolbar                                                   |
+----------------------+------------------------------------+
|                      |                                    |
|  Danh sách ghi chú   |      Nội dung ghi chú              |
|                      |                                    |
| + Công việc          |  Tiêu đề                           |
| + Python             |                                    |
| + Ý tưởng            |  --------------------------------  |
|                      |                                    |
|                      |  QTextEdit                         |
|                      |                                    |
|                      |                                    |
|                      |                                    |
+----------------------+------------------------------------+
```

### Chức năng

- Hiển thị danh sách ghi chú bên trái
- Thêm ghi chú
- Xóa ghi chú
- Chọn ghi chú
- Hiển thị nội dung
- Sửa nội dung
- Lưu SQLite
- Sau này mở rộng:
  - tìm kiếm
  - tag
  - markdown
  - autosave
  - export pdf

---

# Mục tiêu lớn hơn

Quan trọng nhất **không phải làm được ứng dụng**, mà là học cách tổ chức source code.

Sau khóa này bạn sẽ hiểu:

- MVC là gì
- Vì sao không nên viết toàn bộ code trong MainWindow
- Model chịu trách nhiệm gì
- View chịu trách nhiệm gì
- Controller chịu trách nhiệm gì
- Database nằm ở đâu
- Signal/Slot đi theo hướng nào

Đó mới là thứ dùng được cho mọi dự án PySide6.

---

# Cấu trúc MVC

Đầu tiên đừng nghĩ MVC là cái gì quá cao siêu.

Ví dụ:

Bạn đi ăn nhà hàng.

Có ba người.

## Model

Là đầu bếp.

Chỉ biết nấu ăn.

Không quan tâm khách là ai.

Không biết ai gọi món.

```text-x-trilium-auto
Khách:
Cho tôi cơm.

Đầu bếp:
Đây.
```

---

## View

Là phục vụ.

Chỉ biết hiển thị.

Có khách bấm nút.

Có textbox.

Có list.

Có menu.

Không biết SQL.

Không biết SQLite.

Không biết ghi dữ liệu.

---

## Controller

Là quản lý.

Khách bấm nút

↓

Quản lý nhận

↓

Đưa yêu cầu xuống bếp

↓

Nhận món

↓

Đưa cho phục vụ

↓

Phục vụ hiển thị

MVC chính là vậy.

---

# Trong ứng dụng ghi chú

## View

Hiển thị giao diện.

```text-x-trilium-auto
QMainWindow

├── QListWidget
├── QTextEdit
├── QPushButton
├── QLabel
└── Toolbar
```

Không được viết SQL ở đây.

Sai:

```text-x-trilium-auto
cursor.execute(...)
```

Không.

View chỉ có:

```text-x-trilium-auto
button.clicked

list.currentItemChanged

textChanged
```

---

## Model

Model quản lý dữ liệu.

Ví dụ:

```text-x-trilium-auto
notes

id
title
content
created_at
updated_at
```

Model có các hàm

```text-x-trilium-auto
create_note()

delete_note()

update_note()

get_note()

get_all_notes()
```

Model không biết GUI.

---

## Controller

Controller nối hai bên.

Ví dụ:

Người dùng bấm

```text-x-trilium-auto
New Note
```

Controller sẽ

```text-x-trilium-auto
View

↓

Controller

↓

Model

↓

SQLite

↓

Model

↓

Controller

↓

View
```

---

# Dự án sẽ có cấu trúc

```text-x-trilium-auto
note_app/

│
├── main.py
│
├── database/
│   │
│   ├── database.py
│   └── note.db
│
├── model/
│   │
│   └── note_model.py
│
├── view/
│   │
│   ├── main_window.py
│   └── widgets.py
│
├── controller/
│   │
│   └── note_controller.py
│
├── ui/
│
├── resources/
│
└── utils/
```

Đây là cấu trúc khá chuẩn.

---

# Luồng dữ liệu

Ví dụ tạo ghi chú mới.

```text-x-trilium-auto
User

↓

Click New

↓

View

↓

Controller

↓

Model

↓

SQLite

↓

Model

↓

Controller

↓

View refresh

↓

ListWidget hiện ghi chú
```

Luôn nhớ:

**View không nói chuyện với Database.**

---

# Database

SQLite chỉ có một bảng.

```text-x-trilium-auto
notes
```

```text-x-trilium-auto
id INTEGER PRIMARY KEY

title TEXT

content TEXT

created_at TEXT

updated_at TEXT
```

Rất đơn giản.

---

# Module Database

```text-x-trilium-auto
database.py
```

Chỉ có nhiệm vụ

```text-x-trilium-auto
connect()

create_tables()
```

Không viết giao diện.

---

# Module Model

Ví dụ

```text-x-trilium-auto
class NoteModel:

    def create_note()

    def delete_note()

    def update_note()

    def get_note()

    def get_all_notes()
```

Model không import PySide6.

Đây là nguyên tắc rất quan trọng.

---

# Module View

Ví dụ

```text-x-trilium-auto
class MainWindow(QMainWindow):
```

Chỉ tạo

```text-x-trilium-auto
QListWidget

QTextEdit

Toolbar

Button
```

Không SQL.

Không sqlite.

Không commit.

---

# Module Controller

Ví dụ

```text-x-trilium-auto
class NoteController:
```

Controller sẽ kết nối

```text-x-trilium-auto
button.clicked.connect(...)
```

Ví dụ

```text-x-trilium-auto
New

↓

create_note()

↓

refresh_list()
```

Hoặc

```text-x-trilium-auto
QListWidget.currentRowChanged

↓

load_note()

↓

set QTextEdit
```

---

# Sơ đồ tổng thể

```text-x-trilium-auto
                  USER
                    │
                    ▼
             MainWindow(View)
                    │
          signal / slot
                    │
                    ▼
             NoteController
            /              \
           ▼                ▼
     NoteModel          SQLite
```

---

# Những nguyên tắc sẽ học xuyên suốt

Trong toàn bộ khóa học, chúng ta sẽ tuân thủ các nguyên tắc sau:

1. **Mỗi lớp chỉ có một trách nhiệm (Single Responsibility).**
2. **Không viết SQL trong View.**
3. **Không để Model phụ thuộc vào PySide6.**
4. **Controller là cầu nối duy nhất giữa View và Model.**
5. **Tách biệt rõ giao diện, xử lý nghiệp vụ và lưu trữ dữ liệu.**
6. **Mỗi module nhỏ, dễ đọc và dễ kiểm thử.**

---

# Lộ trình dự án

Chúng ta sẽ xây dựng ứng dụng theo từng buổi:

| Buổi | Nội dung |
| --- | --- |
| **Buổi 1** | Kiến trúc MVC, tạo cấu trúc thư mục, tạo cửa sổ chính và kết nối SQLite |
| **Buổi 2** | Thiết kế giao diện với `QSplitter`, `QListWidget`, `QTextEdit`, `QToolBar` |
| **Buổi 3** | Xây dựng lớp `Database` quản lý kết nối SQLite và khởi tạo bảng |
| **Buổi 4** | Xây dựng `NoteModel` với các thao tác CRUD (Create, Read, Update, Delete) |
| **Buổi 5** | Xây dựng `NoteController`, kết nối View với Model |
| **Buổi 6** | Chức năng tạo, chọn và hiển thị ghi chú |
| **Buổi 7** | Chỉnh sửa nội dung, tự động lưu (Auto Save) |
| **Buổi 8** | Xóa ghi chú, hộp thoại xác nhận, xử lý lỗi |
| **Buổi 9** | Tìm kiếm ghi chú theo tiêu đề và nội dung |
| **Buổi 10** | Hoàn thiện giao diện, icon, menu, phím tắt và đóng gói ứng dụng |

## Phong cách giảng dạy

Mình sẽ không chỉ đưa mã nguồn hoàn chỉnh ngay từ đầu. Thay vào đó, mỗi buổi sẽ:

- Giải thích **vì sao** cần một thành phần trước khi viết mã.
- Viết mã từng bước, phân tích từng dòng quan trọng.
- Minh họa luồng dữ liệu giữa **View → Controller → Model → SQLite**.
- Chỉ ra các lỗi người mới thường gặp và cách khắc phục.
- Sau mỗi buổi đều có bài tập mở rộng để bạn tự thực hành.

Đến cuối khóa, bạn sẽ không chỉ có một ứng dụng ghi chú hoạt động tốt mà còn hiểu cách tổ chức một dự án PySide6 theo mô hình MVC để áp dụng cho nhiều loại ứng dụng khác.
