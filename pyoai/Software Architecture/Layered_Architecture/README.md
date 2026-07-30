Mô hình **3 tầng (Layered Architecture / 3-Tier Architecture)** là một trong những kiến trúc phổ biến nhất trong phát triển phần mềm. Đây cũng là kiến trúc rất phù hợp với dự án của bạn (hệ thống cào truyện + quản lý + đọc truyện bằng **PySide6 + SQLite3**).

---

# 1. Kiến trúc 3 tầng là gì?

Ý tưởng rất đơn giản:

> Mỗi tầng chỉ làm **một nhiệm vụ duy nhất**.

```text-x-trilium-auto
+-------------------------+
|    Presentation Layer   |
| (UI, API, CLI, Web)     |
+-----------+-------------+
            |
            v
+-------------------------+
|    Business Layer       |
|  (Service, Logic)       |
+-----------+-------------+
            |
            v
+-------------------------+
|     Data Layer          |
| Repository, Database    |
+-------------------------+
```

Hay còn gọi là

```text-x-trilium-auto
UI
 ↓
Service
 ↓
Repository
 ↓
Database
```

---

# 2. Presentation Layer

Đây là tầng giao diện.

Ví dụ:

- PySide6
- Web (Flask/FastAPI)
- CLI

Nó chỉ có nhiệm vụ

- hiển thị dữ liệu
- nhận thao tác người dùng

Nó KHÔNG xử lý nghiệp vụ.

Ví dụ

```text-x-trilium-auto
User bấm nút

↓

UI

↓

Service

↓

Repository

↓

Database
```

Ví dụ

```text-x-trilium-auto
class MainWindow(QMainWindow):

    def load_books(self):
        books = self.book_service.get_all_books()

        for book in books:
            self.list_widget.addItem(book.title)
```

UI không SQL.

UI không đọc SQLite.

UI không biết bảng gì.

---

# 3. Business Layer

Đây là trái tim của chương trình.

Nó chứa toàn bộ nghiệp vụ.

Ví dụ

```text-x-trilium-auto
Đăng nhập

Tính tiền

Kiểm tra quyền

Kiểm tra dữ liệu

Cào truyện

Download chapter

Retry

Scheduler

...
```

Ví dụ

```text-x-trilium-auto
class BookService:

    def get_all_books(self):
        return self.repo.get_all()
```

Hay

```text-x-trilium-auto
class ChapterService:

    def download_missing(self):

        books = self.book_repo.need_update()

        for book in books:
            self.downloader.download(book)
```

---

# 4. Data Layer

Đây là tầng dữ liệu.

Chỉ có nhiệm vụ

```text-x-trilium-auto
CRUD

Create

Read

Update

Delete
```

Ví dụ

```text-x-trilium-auto
class BookRepository:

    def get_all(self):

        sql = "SELECT * FROM books"

        ...
```

Repository KHÔNG biết PySide.

Repository KHÔNG biết Button.

Repository KHÔNG biết nghiệp vụ.

---

# 5. Luồng dữ liệu

Ví dụ người dùng nhấn

```text-x-trilium-auto
Refresh
```

Quy trình

```text-x-trilium-auto
Button

↓

MainWindow

↓

BookService

↓

BookRepository

↓

SQLite

↓

BookRepository

↓

BookService

↓

MainWindow

↓

TableView
```

---

# 6. Ví dụ thực tế

Giả sử app quản lý truyện.

Người dùng bấm

```text-x-trilium-auto
Refresh Story
```

Presentation

```text-x-trilium-auto
class MainWindow:

    def refresh(self):

        self.story_service.refresh()
```

Business

```text-x-trilium-auto
class StoryService:

    def refresh(self):

        stories = self.source.fetch_latest()

        self.repo.save_all(stories)
```

Data

```text-x-trilium-auto
class StoryRepository:

    def save_all(self, stories):

        ...
```

---

# 7. Ví dụ Login

Presentation

```text-x-trilium-auto
Username

Password

↓

LoginService
```

Business

```text-x-trilium-auto
Kiểm tra

↓

Repository
```

Repository

```text-x-trilium-auto
SELECT * FROM users
```

Database

```text-x-trilium-auto
SQLite
```

---

# 8. Cấu trúc project

```text-x-trilium-auto
project/

    ui/

        main_window.py
        book_page.py
        login_dialog.py

    services/

        book_service.py
        story_service.py
        user_service.py

    repositories/

        book_repository.py
        chapter_repository.py
        user_repository.py

    database/

        sqlite.py

    models/

        book.py
        chapter.py
        user.py
```

---

# 9. Dependency

```text-x-trilium-auto
UI

↓

Service

↓

Repository

↓

Database
```

Không được làm ngược.

Sai

```text-x-trilium-auto
Repository

↓

UI
```

Hoặc

```text-x-trilium-auto
Database

↓

Service

↓

UI

↓

Database
```

---

# 10. Không được vi phạm tầng

Sai

```text-x-trilium-auto
class MainWindow:

    def load(self):

        conn = sqlite3.connect(...)
```

UI đang truy cập DB.

Sai.

---

Sai

```text-x-trilium-auto
class Repository:

    QMessageBox.information(...)
```

Repository không được hiện MessageBox.

---

Sai

```text-x-trilium-auto
Repository

↓

requests.get(...)
↓

HTML Parser
```

Repository không nên đi lấy dữ liệu Internet.

Đó là nhiệm vụ của Service.

---

# 11. Ví dụ hoàn chỉnh

```text-x-trilium-auto
UI

↓

StoryService

↓

CrawlerService

↓

Parser

↓

StoryRepository

↓

SQLite
```

Trong đó

```text-x-trilium-auto
UI
```

chỉ biết

```text-x-trilium-auto
story_service.refresh()
```

Service

```text-x-trilium-auto
download()

parse()

validate()

save()
```

Repository

```text-x-trilium-auto
INSERT

UPDATE

DELETE

SELECT
```

---

# 12. Ưu điểm

- **Dễ bảo trì:** Thay đổi giao diện không ảnh hưởng tầng dữ liệu.
- **Dễ kiểm thử:** Có thể kiểm thử Service và Repository độc lập.
- **Tái sử dụng:** Cùng Service có thể dùng cho PySide6, CLI hoặc API.
- **Tách biệt trách nhiệm:** Mỗi tầng chỉ đảm nhận một vai trò.

---

# 13. Nhược điểm

- Dự án nhỏ sẽ có nhiều lớp hơn cần thiết.
- Nếu phân chia không hợp lý, Service có thể trở thành "God Object" chứa quá nhiều nghiệp vụ.
- Nghiệp vụ phức tạp có thể phải đi qua nhiều tầng, làm tăng số lượng lời gọi hàm.

---

# 14. Áp dụng cho dự án hệ thống cào truyện của bạn

Một cách tổ chức phù hợp là:

```text-x-trilium-auto
story_crawler/

├── ui/                    # Presentation
│   ├── main_window.py
│   ├── dashboard.py
│   ├── reader.py
│   └── widgets/
│
├── services/              # Business
│   ├── story_service.py
│   ├── chapter_service.py
│   ├── crawl_service.py
│   ├── download_service.py
│   ├── scheduler_service.py
│   └── monitor_service.py
│
├── repositories/          # Data Access
│   ├── story_repository.py
│   ├── chapter_repository.py
│   ├── source_repository.py
│   ├── task_repository.py
│   └── log_repository.py
│
├── database/
│   ├── connection.py
│   ├── migrations.py
│   └── schema.sql
│
├── models/
│   ├── story.py
│   ├── chapter.py
│   ├── source.py
│   ├── crawl_task.py
│   └── log.py
│
├── plugins/               # Các nguồn cào (TruyenFull, TangThuVien...)
├── parsers/               # Phân tích HTML/JSON
├── network/               # HTTP Client
├── core/                  # Cấu hình, DI, tiện ích
└── main.py
```

Trong kiến trúc này, các plugin cào truyện và parser hoạt động như các thành phần hạ tầng (infrastructure) được `CrawlService` sử dụng. `Repository` chỉ chịu trách nhiệm lưu và truy xuất dữ liệu từ SQLite, còn toàn bộ quy trình "tải trang → phân tích → kiểm tra → lưu" nằm trong tầng Service.

---

## Bước tiếp theo

Sau khi nắm vững mô hình 3 tầng, bạn nên học tiếp các kiến trúc nâng cao theo thứ tự:

1. **MVC (Model–View–Controller)** — nền tảng của nhiều ứng dụng GUI.
2. **MVVM (Model–View–ViewModel)** — rất phù hợp với PySide6/QML và giao diện hiện đại.
3. **Clean Architecture** — tách biệt nghiệp vụ khỏi framework và cơ sở dữ liệu.
4. **Domain-Driven Design (DDD)** — dành cho các hệ thống lớn với nghiệp vụ phức tạp.

Đối với dự án cào và đọc truyện bằng PySide6 của bạn, mình khuyến nghị bắt đầu với **3 tầng + Repository Pattern**, sau đó nâng cấp dần lên **Clean Architecture** khi quy mô dự án tăng lên.