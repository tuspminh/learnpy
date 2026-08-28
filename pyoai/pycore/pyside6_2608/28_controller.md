# Phần III — UI Architecture

# Buổi 28 — Controller trong PySide6

Ở Buổi 26 ta học **MVC**, Buổi 27 học **MVVM**. Hôm nay chúng ta giải quyết một câu hỏi rất quan trọng:

> **Nếu đã có ViewModel, vậy Controller còn cần không?**

Câu trả lời là: **có thể có, nhưng không phải lúc nào cũng cần.**

Mục tiêu của Buổi 28 là hiểu **Controller thực sự làm gì**, tránh biến Controller thành "God Object", và biết khi nào nên dùng **Controller**, khi nào nên dùng **ViewModel**, khi nào nên dùng **Service**.

---

# 1. Controller là gì?

Controller là thành phần đứng giữa:

```text
User
 ↓
View
 ↓
Controller
 ↓
Application
```

Nó chịu trách nhiệm **điều phối hành động**.

Ví dụ:

```text
User click "Save"
        │
        ▼
   Controller
        │
        ▼
   StoryService
        │
        ▼
     Story
```

Controller không nên chứa toàn bộ business logic.

---

# 2. Controller không phải Service

Đây là điểm đầu tiên cần phân biệt.

### Controller

Quan tâm:

```text
"User vừa làm gì?"
```

### Service

Quan tâm:

```text
"Ứng dụng phải làm gì?"
```

Ví dụ:

```python
def save_story(self):
    title = self.view.title_input.text()

    self.service.create_story(title)
```

Controller:

```text
lấy input
   ↓
gọi service
```

Service:

```text
create_story()
   ↓
thực hiện use case
```

---

# 3. Controller không nên chứa business rule

Sai:

```python
class StoryController:

    def save(self):
        title = self.view.title_input.text()

        if not title:
            return

        if len(title) > 200:
            return

        if self.view.chapter_count == 0:
            return

        ...
```

Controller đang trở thành nơi chứa business rules.

Đúng hơn:

```text
Controller
    ↓
StoryService
    ↓
Story
```

và:

```python
class Story:

    def __init__(self, title):
        if not title:
            raise ValueError(
                "Title is required"
            )
```

---

# 4. Controller làm gì?

Một Controller tốt thường có 5 nhiệm vụ:

```text
1. Nhận user action
2. Lấy input từ View
3. Gọi Application Service / Use Case
4. Xử lý kết quả
5. Ra lệnh cho View cập nhật
```

Ví dụ:

```python
def create_story(self):
    title = self.view.title()

    try:
        story = self.service.create(title)

    except ValueError as e:
        self.view.show_error(str(e))
        return

    self.view.clear_form()
    self.view.show_success()
```

---

# 5. Controller giống "traffic controller"

Hãy tưởng tượng:

```text
              User
               │
               ▼
             View
               │
               ▼
          Controller
          /    |    \
         /     |     \
        ▼      ▼      ▼
    Service  Router  Dialog
```

Controller không trực tiếp làm mọi việc.

Nó chỉ nói:

> "Việc này chuyển cho Service."

> "Việc kia chuyển cho View."

> "Lỗi này hiển thị Dialog."

---

# 6. Ví dụ Todo MVC

Ta có View:

```python
class TodoView(QWidget):

    def __init__(self):
        super().__init__()

        self.input = QLineEdit()
        self.add_button = QPushButton("Add")

        ...
```

Controller:

```python
class TodoController:

    def __init__(self, view, service):
        self.view = view
        self.service = service

        self.view.add_button.clicked.connect(
            self.create_todo
        )

    def create_todo(self):
        title = self.view.input.text()

        try:
            todo = self.service.create(title)

        except ValueError as e:
            self.view.show_error(str(e))
            return

        self.view.clear_input()
        self.view.show_success()
```

Rất đơn giản.

---

# 7. Controller không nhất thiết là QObject

Bạn có thể viết:

```python
class TodoController:

    def __init__(self, view, service):
        ...
```

Không nhất thiết phải:

```python
class TodoController(QObject):
```

Controller là **architecture concept**, không phải Qt widget.

Tuy nhiên trong những architecture phức tạp, việc kế thừa `QObject` có thể hữu ích nếu Controller cần:

```text
Signal
Slot
Timer
Event
```

---

# 8. Controller và Signal/Slot

PySide6 làm Controller rất tự nhiên.

```text
QPushButton
    │
 clicked
    │
    ▼
Controller
    │
    ▼
Service
```

Code:

```python
self.view.save_button.clicked.connect(
    self.save
)
```

Controller nhận Signal.

---

# 9. Controller với nhiều View

Ví dụ Story Reader:

```text
MainWindow
    │
    ├── SourcePanel
    ├── StoryPanel
    └── ChapterPanel
```

Ta có:

```text
SourceController
StoryController
ChapterController
```

Thay vì:

```text
MainController
    ├── source
    ├── story
    ├── chapter
    ├── reader
    ├── crawler
    ├── download
    └── settings
```

Cách thứ hai rất dễ biến thành God Object.

---

# 10. God Controller

Một Controller bắt đầu như:

```python
class StoryController:

    def create(self):
        ...

    def update(self):
        ...

    def delete(self):
        ...
```

Sau đó:

```python
class StoryController:

    def create(self):
        ...

    def update(self):
        ...

    def delete(self):
        ...

    def crawl(self):
        ...

    def download(self):
        ...

    def parse_html(self):
        ...

    def export_epub(self):
        ...

    def backup_database(self):
        ...

    def restore_database(self):
        ...

    def login(self):
        ...
```

Đây là dấu hiệu:

> **Controller đang trở thành God Object.**

---

# 11. Cách giải quyết

Tách theo use case:

```text
StoryController
      │
      ├── CreateStory
      ├── UpdateStory
      └── DeleteStory

CrawlerController
      │
      ├── StartCrawler
      ├── PauseCrawler
      └── StopCrawler

ReaderController
      │
      ├── OpenChapter
      ├── NextChapter
      └── PreviousChapter
```

Sau này ta có thể chuyển thành:

```text
Application
├── CreateStoryUseCase
├── DeleteStoryUseCase
├── CrawlStoryUseCase
└── ReadChapterUseCase
```

Điều này rất gần với **Clean Architecture / DDD** mà bạn đã học.

---

# 12. Controller vs ViewModel

Đây là phần quan trọng nhất của buổi học.

## Controller

Tập trung vào:

```text
Action
```

Ví dụ:

```text
clicked
submitted
selected
deleted
```

## ViewModel

Tập trung vào:

```text
State
```

Ví dụ:

```text
loading
error
stories
selected_story
can_delete
search_text
```

Có thể nhớ:

```text
Controller → What happened?
ViewModel  → What is the current state?
```

---

# 13. So sánh

|                  | Controller                | ViewModel      |
| ---------------- | ------------------------- | -------------- |
| Nhận user action | ✅                         | ✅              |
| Quản lý UI state | ❌/ít                      | ✅              |
| Business logic   | ❌                         | ❌              |
| Gọi Service      | ✅                         | ✅              |
| Signal           | Có thể                    | Rất thường     |
| State observable | Không phải mục tiêu chính | Mục tiêu chính |
| Phù hợp MVC      | ✅                         | Không bắt buộc |
| Phù hợp MVVM     | Có thể                    | ✅              |

---

# 14. Controller trong MVC

Kiến trúc:

```text
View
 │
 ▼
Controller
 │
 ▼
Model
```

Controller là thành phần trung tâm của interaction.

---

# 15. ViewModel trong MVVM

Kiến trúc:

```text
View
 │
 ▼
ViewModel
 │
 ▼
Model
```

ViewModel giữ state:

```text
todos
loading
error
selection
```

View phản ứng với state.

---

# 16. Có thể kết hợp Controller + ViewModel không?

**Có.**

Ví dụ app lớn:

```text
                 MainWindow
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
     StoryController       StoryListViewModel
          │                     │
          ▼                     ▼
     StoryService          StoryListModel
```

Nhưng phải có lý do rõ ràng.

Nếu Controller và ViewModel đều xử lý:

```text
create()
delete()
refresh()
```

thì dễ bị trùng trách nhiệm.

---

# 17. Một nguyên tắc quan trọng

Không nên hỏi:

> "MVC hay MVVM tốt hơn?"

Nên hỏi:

> **"UI này có complexity như thế nào?"**

Ví dụ:

### App đơn giản

```text
QWidget
```

### App vừa

```text
View
Controller
Service
```

### App nhiều state

```text
View
ViewModel
Service
```

### App rất lớn

```text
View
ViewModel / Controller
Application
Domain
Infrastructure
```

---

# 18. Controller và Navigation

Controller còn rất hữu ích trong việc điều hướng.

Ví dụ:

```text
MainWindow
   │
   ├── StoryList
   ├── StoryDetail
   └── Reader
```

User:

```text
click Story
```

Controller:

```python
def open_story(self, story_id):
    story = self.service.get_story(story_id)

    self.view.show_story(story)
```

Hoặc:

```python
self.view.show_reader(story_id)
```

Controller có thể điều phối navigation.

---

# 19. Nhưng Navigation cũng có thể tách riêng

App lớn:

```text
NavigationController
```

Ví dụ:

```python
class NavigationController:

    def show_story_list(self):
        ...

    def show_story_detail(self, story_id):
        ...

    def show_reader(self, chapter_id):
        ...
```

Khi đó:

```text
StoryController
       │
       ▼
NavigationController
```

Đây là một dạng **Coordinator** mà chúng ta sẽ gặp trong architecture nâng cao.

---

# 20. Controller và Dialog

Ví dụ:

```text
User click Delete
       │
       ▼
Controller
       │
       ▼
Confirm Dialog
       │
       ▼
Service.delete()
```

Controller điều phối:

```python
def delete_story(self):
    if not self.view.confirm_delete():
        return

    try:
        self.service.delete(
            self.view.selected_story_id()
        )

    except Exception as e:
        self.view.show_error(str(e))
```

Controller không tự thực hiện:

```python
DELETE FROM stories
```

---

# 21. Controller và asynchronous task

Sau này chúng ta sẽ học:

```text
QThread
QRunnable
QThreadPool
asyncio
```

Controller có thể khởi động task:

```text
User
 ↓
Controller
 ↓
Worker
 ↓
Service
```

Worker:

```text
crawl
download
parse
```

Kết quả:

```text
Worker
 ↓
Signal
 ↓
Controller/ViewModel
 ↓
View
```

Điều này sẽ rất hữu ích cho Story Reader.

---

# 22. Controller không nên biết quá nhiều về Qt

Ví dụ tốt:

```python
def create_story(self):
    title = self.view.get_title()

    result = self.service.create(title)

    self.view.show_story(result)
```

Ví dụ Controller quá phụ thuộc UI:

```python
def create_story(self):
    title = self.view.title_input.text()

    self.view.title_input.setStyleSheet(...)
    self.view.progress_bar.setValue(...)
    self.view.list_widget.clear()
    self.view.status_bar.showMessage(...)
```

Controller đang thao túng quá nhiều chi tiết UI.

Khi đó View nên cung cấp các method abstraction:

```python
self.view.show_error(...)
self.view.show_success(...)
self.view.clear_form()
self.view.show_loading(...)
```

---

# 23. Controller vs UI API

Thay vì:

```python
self.view.error_label.setText(
    "Invalid title"
)

self.view.error_label.show()
```

View cung cấp:

```python
self.view.show_error(
    "Invalid title"
)
```

Controller chỉ cần biết:

```text
"Hiển thị lỗi"
```

chứ không cần biết:

```text
"lỗi được hiển thị bằng QLabel nào?"
```

Đây là **encapsulation**.

---

# 24. Controller tốt và Controller xấu

### Controller tốt

```text
10–30 dòng/use case
```

thường khá dễ hiểu.

```python
def create_story(self):
    title = self.view.title()

    try:
        self.service.create(title)

    except ValueError as e:
        self.view.show_error(str(e))
        return

    self.view.clear_form()
    self.view.refresh()
```

### Controller xấu

```text
500–1000 dòng
```

và chứa:

```text
SQL
HTTP
Parsing
Business rules
File processing
UI manipulation
Thread management
Logging
Caching
```

Đây là lúc phải refactor.

---

# 25. Một quy tắc refactoring rất hữu ích

Nếu Controller có:

```python
if ...
for ...
while ...
try ...
except ...
```

không có nghĩa là sai.

Nhưng nếu có rất nhiều:

```text
if/else
for
SQL
HTTP
business rules
```

thì hãy hỏi:

> "Logic này thực sự thuộc layer nào?"

---

# 26. Ví dụ refactor

Controller ban đầu:

```python
def save_story(self):
    title = self.view.title()

    if not title:
        self.view.show_error("Required")
        return

    conn = sqlite3.connect("story.db")

    cursor = conn.execute(
        "SELECT id FROM stories WHERE title=?",
        (title,),
    )

    if cursor.fetchone():
        self.view.show_error(
            "Already exists"
        )
        return

    conn.execute(
        "INSERT INTO stories(title) VALUES(?)",
        (title,),
    )

    conn.commit()

    self.view.refresh()
```

Có quá nhiều trách nhiệm.

---

# 27. Sau refactoring

Controller:

```python
def save_story(self):
    title = self.view.title()

    try:
        self.service.create_story(title)

    except ValueError as e:
        self.view.show_error(str(e))
        return

    self.view.clear_form()
    self.view.refresh()
```

Service:

```python
class StoryService:

    def create_story(self, title):
        story = Story(title)

        if self.repository.exists(title):
            raise ValueError(
                "Story already exists"
            )

        self.repository.save(story)

        return story
```

Repository:

```python
class StoryRepository:

    def exists(self, title):
        ...

    def save(self, story):
        ...
```

Kiến trúc:

```text
Controller
    ↓
Service
    ↓
Domain
    ↓
Repository
    ↓
SQLite
```

---

# 28. Controller và Dependency Injection

Đừng để Controller tự tạo mọi dependency:

```python
class StoryController:

    def __init__(self, view):
        self.view = view
        self.service = StoryService()
        self.repository = StoryRepository()
```

Điều này tạo coupling.

Tốt hơn:

```python
class StoryController:

    def __init__(
        self,
        view,
        service,
    ):
        self.view = view
        self.service = service
```

Khởi tạo bên ngoài:

```python
service = StoryService(...)
controller = StoryController(
    view,
    service,
)
```

Đây là bước chuẩn bị cho **Buổi 31 — Dependency Injection**.

---

# 29. Controller và Testing

Controller có thể test bằng fake View:

```python
class FakeView:

    def title(self):
        return "Test Story"

    def show_error(self, message):
        self.error = message

    def clear_form(self):
        self.cleared = True
```

Fake Service:

```python
class FakeService:

    def create_story(self, title):
        return Story(title)
```

Test:

```python
view = FakeView()
service = FakeService()

controller = StoryController(
    view,
    service,
)

controller.save_story()

assert view.cleared is True
```

Không nhất thiết phải chạy UI thật.

---

# 30. Controller và Qt Model/View

Đây là nơi kết nối với Phần II.

Ta có:

```text
             Controller
                 │
                 ▼
              Service
                 │
                 ▼
            List[Story]
                 │
                 ▼
          StoryListModel
                 │
                 ▼
             QListView
```

Controller không cần biết `QListView` đang render từng row thế nào.

Nó chỉ cần:

```python
self.model.set_stories(stories)
```

hoặc tốt hơn, sau này để state/model được cập nhật thông qua application architecture.

---

# 31. Một architecture tốt cho Story Reader

Ở giai đoạn này:

```text
┌──────────────────────────────────┐
│          Presentation             │
│                                  │
│ MainWindow                       │
│ StoryView                        │
│ StoryListModel                   │
│ StoryController                  │
│ StoryViewModel                   │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│          Application              │
│                                  │
│ StoryService                     │
│ ChapterService                   │
│ CrawlService                     │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│             Domain               │
│                                  │
│ Story                            │
│ Chapter                          │
│ Author                           │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│         Infrastructure           │
│                                  │
│ Repository                       │
│ SQLite                           │
│ HTTP                             │
└──────────────────────────────────┘
```

---

# 32. Một câu hỏi rất quan trọng

Giả sử:

```text
User click Delete
```

Ai quyết định:

> "Story này có được phép xóa không?"

**Không phải Controller.**

Controller chỉ:

```text
"User muốn xóa Story #10."
```

Service/Domain quyết định:

```text
"Story #10 có được phép xóa hay không."
```

Đây là boundary cực kỳ quan trọng.

---

# 33. Ai quyết định cái gì?

Hãy nhớ bảng này:

| Câu hỏi                  | Thành phần           |
| ------------------------ | -------------------- |
| User click gì?           | View                 |
| User muốn làm gì?        | Controller/ViewModel |
| Làm use case nào?        | Application Service  |
| Có được phép không?      | Domain               |
| Lưu ở đâu?               | Repository           |
| Lưu bằng SQLite thế nào? | Infrastructure       |
| Hiển thị thế nào?        | View                 |
| UI đang loading?         | ViewModel            |
| Story nào đang selected? | ViewModel/Qt Model   |

---

# 34. Controller có còn cần trong MVVM?

Không nhất thiết.

Trong MVVM:

```text
View
 │
 ▼
ViewModel
 │
 ▼
Service
```

ViewModel có thể thay vai trò interaction của Controller.

Ví dụ:

```python
self.view_model.create_story(
    title
)
```

ViewModel:

```python
def create_story(self, title):
    try:
        self.service.create(title)
    except ValueError as e:
        self.error_changed.emit(str(e))
```

Trong trường hợp này:

```text
ViewModel ≈ Controller + UI State
```

Nhưng không hoàn toàn đồng nghĩa.

---

# 35. Khi nào Controller vẫn hữu ích với MVVM?

Ví dụ application có navigation phức tạp:

```text
MainWindow
 │
 ├── StoryList
 ├── StoryDetail
 ├── Reader
 └── Settings
```

Một:

```text
NavigationController
```

có thể điều phối:

```text
StoryList
   ↓
StoryDetail
   ↓
Reader
```

Trong khi:

```text
StoryListViewModel
```

chỉ quản lý state của StoryList.

Đây là cách kết hợp hợp lý.

---

# 36. Quy tắc thiết kế Controller

Hãy áp dụng 7 quy tắc:

### Rule 1

Controller nhận action.

### Rule 2

Controller không chứa business rule.

### Rule 3

Controller không truy cập database trực tiếp.

### Rule 4

Controller gọi Service/Use Case.

### Rule 5

Controller không thao túng quá sâu vào widget.

### Rule 6

Một Controller nên có scope rõ ràng.

### Rule 7

Nếu Controller ngày càng lớn → tìm logic để chuyển sang layer phù hợp.

---

# 37. Bài tập 1

Phân loại các đoạn code:

### A

```python
if not title:
    raise ValueError(
        "Title required"
    )
```

### B

```python
title = self.title_input.text()
```

### C

```python
self.service.create_story(title)
```

### D

```python
INSERT INTO stories(...)
```

### E

```python
self.error_label.setText(
    "Invalid title"
)
```

Hãy xác định:

```text
View
Controller
Service
Domain
Repository
```

---

# 38. Bài tập 2 — Tìm God Object

Cho:

```python
class StoryController:

    def create_story(self):
        ...

    def delete_story(self):
        ...

    def crawl_website(self):
        ...

    def parse_html(self):
        ...

    def save_database(self):
        ...

    def download_image(self):
        ...

    def export_epub(self):
        ...

    def change_theme(self):
        ...

    def open_settings(self):
        ...
```

Hãy đề xuất cách tách thành:

```text
StoryController
CrawlerService
Parser
Repository
DownloadService
EpubExporter
SettingsViewModel
NavigationController
```

---

# 39. Bài tập 3 — Thiết kế Controller

Viết:

```python
class TodoController:
    ...
```

với:

```text
create_todo()
delete_todo()
complete_todo()
```

Controller phải:

* lấy input từ View
* gọi Service
* xử lý lỗi
* yêu cầu View cập nhật

Không được:

```text
sqlite3
business rule
SQL
```

---

# 40. Bài tập 4 — MVC hay MVVM?

Cho mỗi trường hợp, chọn:

```text
MVC
MVVM
Cả hai
Không cần
```

### A

Calculator đơn giản.

### B

Todo App có 5 trạng thái UI.

### C

Story Reader có:

```text
Story List
Search
Filter
Selection
Loading
Download
Error
Reading Progress
```

### D

Ứng dụng có navigation giữa 20 màn hình.

### E

Một custom dialog chỉ có 2 nút.

---

# 41. Bài tập 5 — Architecture Challenge

Hãy thiết kế:

```text
StoryList
```

với:

```text
Search
Filter
Refresh
Delete
Selection
Loading
Error
```

Bạn phải quyết định:

```text
View
Controller
ViewModel
Service
Qt Model
Repository
```

nằm ở đâu.

Sơ đồ mục tiêu:

```text
                     User
                       │
                       ▼
                 StoryListView
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
        ViewModel           Controller?
             │                   │
             └─────────┬─────────┘
                       ▼
                 StoryService
                       │
                       ▼
                StoryRepository
                       │
                       ▼
                    SQLite
```

**Điểm quan trọng:** bạn phải tự quyết định có cần Controller hay không.

Đây chính là bài tập kiến trúc chứ không còn là bài tập API PySide6 nữa.

---

# 42. Tổng kết Buổi 28

Hãy ghi nhớ:

```text
Controller
    =
Action Orchestration
```

Không phải:

```text
Controller
    =
Business Logic
```

Không phải:

```text
Controller
    =
Database
```

Không phải:

```text
Controller
    =
Everything
```

Một Controller tốt:

```text
User Action
     ↓
Controller
     ↓
Service / Use Case
     ↓
Domain
```

Trong MVVM:

```text
User Action
     ↓
ViewModel
     ↓
Service
     ↓
Domain
```

và:

```text
ViewModel
     ↓
UI State
     ↓
View
```

### Mental Model cuối cùng

```text
                 ┌─────────────┐
                 │    View     │
                 └──────┬──────┘
                        │
                  User Action
                        │
                        ▼
              ┌─────────────────┐
              │ Controller OR   │
              │   ViewModel     │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │    Service      │
              │    / Use Case   │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │     Domain      │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   Repository    │
              └────────┬────────┘
                       │
                       ▼
                    SQLite
```

**Buổi 29 — Service Layer** sẽ là bước rất quan trọng: chúng ta sẽ làm rõ **Service khác Controller ở đâu, Domain Service khác Application Service thế nào, Use Case là gì**, và xây `StoryService` theo cách phù hợp với Clean Architecture/DDD thay vì biến Service thành một "God Service".
