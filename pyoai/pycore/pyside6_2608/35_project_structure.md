# Phần III — UI Architecture

# Buổi 35 — Project Structure

Đây là **buổi tổng kết Phần III**.

Sau Buổi 25–34, chúng ta đã đi từ:

```text
UI
 ↓
MVC
 ↓
MVVM
 ↓
Controller
 ↓
Service
 ↓
Repository
 ↓
Dependency Injection
 ↓
Application State
 ↓
Event Bus
 ↓
Signal-based Architecture
```

Hôm nay chúng ta ghép tất cả thành **một cấu trúc project PySide6 có khả năng mở rộng**.

---

# 1. Vấn đề của project PySide6 nhỏ

Ban đầu chúng ta thường viết:

```text
main.py
```

với:

```python
class MainWindow(QMainWindow):
    ...
```

Rồi vài tuần sau:

```text
main.py
```

có:

```text
MainWindow
Dialog
Database
Repository
Crawler
Service
Worker
Model
Settings
Logging
```

và cuối cùng:

```text
main.py = 3000 lines
```

Đây là vấn đề chúng ta muốn tránh.

---

# 2. Tư duy quan trọng nhất

Không tổ chức project theo:

```text
"Class nào tiện thì bỏ vào đây"
```

Mà tổ chức theo **responsibility**.

Ví dụ:

```text
Domain
Application
Infrastructure
Presentation
```

---

# 3. Kiến trúc tổng thể

Ta hướng tới:

```text
                    ┌──────────────┐
                    │ Presentation │
                    │   PySide6    │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Application  │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          Domain      Infrastructure   Events
              │            │
              │            ▼
              │         SQLite
              │
              ▼
         Business Rules
```

Đây cũng rất gần với những gì bạn đã học về **Clean Architecture / DDD**.

---

# 4. Project structure

Một cấu trúc thực tế:

```text
story_reader/
│
├── pyproject.toml
├── README.md
│
├── src/
│   └── story_reader/
│
│       ├── main.py
│       │
│       ├── app/
│       │   ├── application.py
│       │   ├── config.py
│       │   └── state.py
│       │
│       ├── domain/
│       │   ├── models/
│       │   ├── services/
│       │   └── repositories/
│       │
│       ├── application/
│       │   ├── services/
│       │   ├── use_cases/
│       │   └── dto/
│       │
│       ├── infrastructure/
│       │   ├── database/
│       │   ├── repositories/
│       │   └── crawlers/
│       │
│       ├── presentation/
│       │   ├── windows/
│       │   ├── dialogs/
│       │   ├── widgets/
│       │   ├── viewmodels/
│       │   └── models/
│       │
│       ├── events/
│       │   ├── bus.py
│       │   └── events.py
│       │
│       └── resources/
│
└── tests/
    ├── unit/
    └── integration/
```

Đây là cấu trúc khá lớn.

**Không phải project nào cũng cần tất cả thư mục này ngay từ đầu.**

---

# 5. `src/` layout

Vì bạn đã học `Python src layout`, chúng ta dùng:

```text
src/
    story_reader/
```

thay vì:

```text
story_reader/
    main.py
```

Lợi ích chính là giảm khả năng vô tình import source code từ working directory và giúp project gần với cách package Python thực tế được build/test.

---

# 6. `main.py` phải cực kỳ mỏng

Đây là nguyên tắc quan trọng.

Không nên:

```python
# main.py

class MainWindow:
    ...

class Repository:
    ...

class Service:
    ...

class Worker:
    ...
```

Nên:

```python
from story_reader.app.application import Application


def main():
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
```

`main.py` chỉ là **entry point**.

---

# 7. Application là gì?

Ví dụ:

```text
app/
├── application.py
├── config.py
└── state.py
```

`Application` chịu trách nhiệm **composition**.

Nó tạo:

```text
Database
Repository
Service
EventBus
State
ViewModel
Window
```

---

# 8. Application chính là Composition Root

Đây là khái niệm rất quan trọng từ Buổi 31 — Dependency Injection.

Ví dụ:

```python
class Application:

    def __init__(self):

        self.event_bus = EventBus()

        self.state = AppState()

        self.database = Database()

        self.repository = StoryRepository(
            self.database
        )

        self.service = StoryService(
            self.repository
        )

        self.view_model = StoryViewModel(
            self.service,
            self.state,
        )

        self.window = MainWindow(
            self.view_model
        )
```

Nhìn vào đây ta thấy toàn bộ dependency graph.

---

# 9. Domain Layer

Domain chứa business concepts.

Ví dụ:

```text
domain/
├── models/
│   ├── story.py
│   └── chapter.py
│
├── services/
│   └── story_service.py
│
└── repositories/
    └── story_repository.py
```

---

# 10. Domain Model

Ví dụ:

```python
from dataclasses import dataclass


@dataclass
class Story:

    id: int
    title: str
    author: str | None = None
```

Domain model:

```text
Không biết:
    PySide6
    QWidget
    SQLite
    QMainWindow
```

Nó chỉ biết business.

---

# 11. Repository Interface

Trong Domain:

```python
from typing import Protocol


class StoryRepository(Protocol):

    def get_by_id(
        self,
        story_id: int,
    ) -> Story | None:
        ...
```

Domain/application không cần biết repository thực tế dùng:

```text
SQLite
PostgreSQL
API
JSON
Mock
```

---

# 12. Infrastructure

Infrastructure chứa implementation.

Ví dụ:

```text
infrastructure/
├── database/
│   └── sqlite.py
│
├── repositories/
│   └── sqlite_story_repository.py
│
└── crawlers/
    ├── site_a.py
    └── site_b.py
```

Ở đây chúng ta có:

```python
class SQLiteStoryRepository:
    ...
```

---

# 13. Dependency Direction

Điều quan trọng:

```text
Presentation
     ↓
Application
     ↓
Domain

Infrastructure
     ↓
implements
Domain interfaces
```

Không nên:

```text
Domain
   ↓
PySide6
```

hoặc:

```text
Domain
   ↓
SQLite
```

---

# 14. Application Layer

Application layer điều phối use case.

Ví dụ:

```text
application/
├── use_cases/
│   ├── load_story.py
│   ├── delete_story.py
│   └── crawl_story.py
│
├── dto/
└── services/
```

Ví dụ:

```python
class LoadStoryUseCase:

    def __init__(self, repository):
        self.repository = repository

    def execute(self, story_id):
        return self.repository.get_by_id(
            story_id
        )
```

---

# 15. Presentation

Đây là nơi PySide6 sống.

```text
presentation/
├── windows/
├── dialogs/
├── widgets/
├── viewmodels/
└── models/
```

Ví dụ:

```text
windows/
    main_window.py

dialogs/
    settings_dialog.py

widgets/
    story_card.py
    progress_widget.py

viewmodels/
    story_view_model.py

models/
    story_list_model.py
```

---

# 16. `View` là PySide6

Ví dụ:

```python
class MainWindow(QMainWindow):

    def __init__(self, view_model):
        super().__init__()

        self.view_model = view_model
```

View có:

```text
QMainWindow
QWidget
QLabel
QPushButton
QListView
QTableView
```

---

# 17. ViewModel

ViewModel:

```python
class StoryViewModel(QObject):

    title_changed = Signal(str)
    loading_changed = Signal(bool)

    def __init__(self, service):
        super().__init__()

        self.service = service
```

Nó là cầu nối:

```text
View
 ↕
ViewModel
 ↕
Application
```

---

# 18. Qt Model khác Domain Model

Đây là một điểm cực kỳ quan trọng.

Domain:

```python
@dataclass
class Story:
    id: int
    title: str
```

Qt Model:

```python
class StoryListModel(
    QAbstractListModel
):
    ...
```

Hai cái **không phải cùng một thứ**.

---

# 19. Domain Model

Đại diện:

```text
Business concept
```

Ví dụ:

```text
Story
Chapter
Author
Source
```

---

# 20. Qt Model

Đại diện:

```text
Data presentation for View
```

Ví dụ:

```text
QListView
QTableView
QTreeView
```

Qt Model biết:

```text
row
column
role
QModelIndex
```

Domain Model không cần biết những thứ này.

---

# 21. Events

Sau Buổi 33:

```text
events/
├── bus.py
└── events.py
```

Ví dụ:

```python
@dataclass(frozen=True)
class StorySelected:
    story_id: int
```

và:

```python
class EventBus:
    ...
```

---

# 22. Signals

Signal không nhất thiết phải có thư mục riêng.

Signal thường nằm trên QObject cần phát nó:

```python
class StoryViewModel(QObject):

    title_changed = Signal(str)
```

```python
class Worker(QObject):

    progress_changed = Signal(int)
```

Điều này giữ signal gần với owner của nó.

---

# 23. App State

Có thể đặt:

```text
app/state.py
```

Ví dụ:

```python
class AppState(QObject):

    selected_story_changed = Signal(int)

    def __init__(self):
        super().__init__()

        self._selected_story_id = None
```

State là application-wide state.

---

# 24. Config

```text
app/config.py
```

Ví dụ:

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:

    database_path: Path
    download_path: Path
```

Không nên để config rải rác:

```python
DB = "data.db"

DOWNLOAD_DIR = "downloads"

API_URL = "..."
```

khắp project.

---

# 25. `Application` hoàn chỉnh hơn

```python
from PySide6.QtWidgets import QApplication


class Application:

    def __init__(self):

        self.qt_app = QApplication([])

        self.event_bus = EventBus()

        self.state = AppState()

        self.database = SQLiteDatabase()

        self.repository = (
            SQLiteStoryRepository(
                self.database
            )
        )

        self.service = StoryService(
            self.repository
        )

        self.view_model = StoryViewModel(
            self.service,
            self.state,
            self.event_bus,
        )

        self.window = MainWindow(
            self.view_model
        )

    def run(self):

        self.window.show()

        return self.qt_app.exec()
```

---

# 26. Dependency Graph

Nhìn vào:

```python
self.repository = SQLiteStoryRepository(
    self.database
)
```

ta có:

```text
SQLiteDatabase
      ↓
SQLiteStoryRepository
      ↓
StoryService
      ↓
StoryViewModel
      ↓
MainWindow
```

Đây chính là **Dependency Injection**.

---

# 27. Composition Root

Có thể vẽ:

```text
                 Application
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
     Database     EventBus      State
        │
        ▼
   Repository
        │
        ▼
     Service
        │
        ▼
   ViewModel
        │
        ▼
       View
```

`Application` biết tất cả.

Nhưng:

```text
View không biết Database
Service không biết View
Domain không biết PySide6
```

Đây là điều chúng ta muốn.

---

# 28. MainWindow không tạo dependency

Không nên:

```python
class MainWindow(QMainWindow):

    def __init__(self):
        self.db = SQLiteDatabase()
        self.repo = StoryRepository(self.db)
        self.service = StoryService(self.repo)
```

MainWindow đang làm composition.

Sai responsibility.

---

# 29. MainWindow nhận dependency

Nên:

```python
class MainWindow(QMainWindow):

    def __init__(
        self,
        view_model,
    ):
        super().__init__()

        self.view_model = view_model
```

Application tạo dependency.

---

# 30. ViewModel nhận Service

```python
class StoryViewModel(QObject):

    def __init__(
        self,
        service,
    ):
        super().__init__()

        self.service = service
```

Không:

```python
self.repository = SQLiteStoryRepository(...)
```

ViewModel không nên biết infrastructure cụ thể.

---

# 31. Service nhận Repository

```python
class StoryService:

    def __init__(
        self,
        repository,
    ):
        self.repository = repository
```

Service không tạo:

```python
SQLiteConnection()
```

---

# 32. Repository nhận Database

```python
class SQLiteStoryRepository:

    def __init__(
        self,
        database,
    ):
        self.database = database
```

Tất cả dependency được inject từ bên ngoài.

---

# 33. Đây là Dependency Inversion

Ta có:

```text
MainWindow
    ↓
ViewModel
    ↓
Service
    ↓
Repository
    ↓
Database
```

Nhưng dependency implementation nên được quản lý ở Composition Root.

```text
Application
    ├── SQLiteDatabase
    ├── SQLiteRepository
    ├── StoryService
    ├── ViewModel
    └── MainWindow
```

---

# 34. Không cần over-engineering

Có thể bạn sẽ nghĩ:

> Vậy mọi class phải có interface?

Không.

Project nhỏ:

```text
StoryService
SQLiteStoryRepository
MainWindow
```

là đủ.

Khi cần test hoặc thay implementation:

```text
Protocol
Mock
Fake
```

mới thêm.

---

# 35. Project nhỏ

Nếu app chỉ khoảng vài nghìn dòng:

```text
src/app/
├── main.py
├── models.py
├── database.py
├── services.py
├── views/
└── widgets/
```

hoàn toàn được.

Không nhất thiết phải có:

```text
domain/
application/
infrastructure/
presentation/
```

ngay lập tức.

---

# 36. Project vừa

Có thể:

```text
app/
├── domain/
├── application/
├── infrastructure/
└── presentation/
```

Đây là mức tôi khuyên dùng cho project Story Reader.

---

# 37. Project lớn

Khi lớn hơn:

```text
app/
├── app/
├── domain/
├── application/
├── infrastructure/
├── presentation/
├── events/
├── workers/
├── resources/
└── tests/
```

và chia tiếp theo feature.

---

# 38. Feature-based Structure

Một cách khác:

```text
story_reader/
│
├── stories/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── presentation/
│
├── chapters/
│   ├── domain/
│   ├── application/
│   └── presentation/
│
└── crawler/
    ├── domain/
    ├── application/
    └── infrastructure/
```

Đây là **feature-based architecture**.

---

# 39. Layer-based vs Feature-based

### Layer-based

```text
domain/
application/
infrastructure/
presentation/
```

Dễ học.

### Feature-based

```text
stories/
chapters/
crawler/
reader/
```

Dễ scale theo business feature.

Không có kiến trúc duy nhất đúng cho mọi project.

---

# 40. Với Story Reader

Tôi khuyên ban đầu dùng:

```text
layer-based
```

vì project đang phục vụ mục tiêu học architecture.

Sau khi project lớn hơn:

```text
feature-based
```

có thể là bước refactor tiếp theo.

---

# 41. Import Rules

Một trong những thứ quan trọng nhất.

Ví dụ:

```text
presentation
    ↓
application
    ↓
domain
```

Presentation có thể import Application.

Application có thể import Domain.

Domain không import Presentation.

---

# 42. Infrastructure

Infrastructure implement interface của Domain/Application.

Ví dụ:

```text
domain/
    repositories.py

infrastructure/
    repositories/
        sqlite_story_repository.py
```

Infrastructure phụ thuộc abstraction.

---

# 43. Tránh circular import

Ví dụ nguy hiểm:

```text
main_window.py
    ↓
service.py
    ↓
main_window.py
```

hoặc:

```text
viewmodel.py
    ↓
window.py
    ↓
viewmodel.py
```

Nếu architecture rõ ràng:

```text
View
 ↓
ViewModel
 ↓
Service
 ↓
Repository
```

thì circular import giảm đáng kể.

---

# 44. `__init__.py`

Không cần export mọi thứ.

Ví dụ:

```text
presentation/
├── windows/
│   ├── __init__.py
│   └── main_window.py
```

Không nhất thiết phải:

```python
from .main_window import MainWindow
```

trừ khi bạn muốn public API nội bộ rõ ràng.

---

# 45. Resources

Ví dụ:

```text
resources/
├── icons/
├── images/
├── styles/
└── ui/
```

Sau này:

```text
.qrc
```

sẽ đưa resource vào Qt Resource System.

Đó là nội dung của **Buổi 90–94**.

---

# 46. Tests

Đừng để:

```text
tests/
```

thành một đống file.

Có thể:

```text
tests/
├── unit/
│   ├── domain/
│   ├── application/
│   └── presentation/
│
└── integration/
    ├── database/
    └── repositories/
```

---

# 47. Domain Test

Domain dễ test:

```python
def test_story_title():
    story = Story(
        id=1,
        title="Naruto",
    )

    assert story.title == "Naruto"
```

Không cần:

```python
QApplication
```

---

# 48. Service Test

Có thể dùng Fake Repository:

```python
class FakeStoryRepository:

    def get_by_id(self, story_id):
        return Story(
            id=story_id,
            title="Test",
        )
```

Inject:

```python
service = StoryService(
    FakeStoryRepository()
)
```

Đây chính là lợi ích của DI.

---

# 49. ViewModel Test

Có thể test signal.

Ví dụ:

```python
spy = QSignalSpy(
    view_model.title_changed
)

view_model.load_story(1)

assert spy.count() == 1
```

`QSignalSpy` rất hữu ích khi test PySide6 signal behavior.

---

# 50. UI Test

UI test sẽ phức tạp hơn:

```text
QApplication
    ↓
Widget
    ↓
User interaction
    ↓
Signal
    ↓
ViewModel
```

Chúng ta sẽ học testing sâu hơn ở **Buổi 98**.

---

# 51. Đừng để SQL trong UI

Sai:

```python
class MainWindow:

    def load_story(self):

        cursor.execute(
            "SELECT * FROM stories"
        )
```

Đây là architecture smell rất rõ.

Nên:

```text
MainWindow
 ↓
ViewModel
 ↓
Service
 ↓
Repository
 ↓
SQLite
```

---

# 52. Đừng để business logic trong Widget

Sai:

```python
class StoryCard(QWidget):

    def on_click(self):

        if story.status == "completed":
            ...
        elif ...
```

Nếu đó là business rule, nên nằm ở:

```text
Domain
```

hoặc:

```text
Application Service
```

Widget chủ yếu xử lý UI.

---

# 53. Đừng để Repository phát Signal UI

Sai:

```python
class SQLiteRepository(QObject):

    story_loaded = Signal(object)
```

Repository không cần biết UI.

Nên:

```text
Repository
    ↓
return Story
```

rồi:

```text
ViewModel
    ↓
Signal
```

---

# 54. Đừng để Domain Model kế thừa QObject nếu không cần

Không:

```python
class Story(QObject):
    ...
```

nếu Story chỉ là domain entity.

Nên:

```python
@dataclass
class Story:
    ...
```

---

# 55. Một project hoàn chỉnh

```text
story_reader/
│
├── pyproject.toml
│
├── src/
│   └── story_reader/
│
│       ├── main.py
│       │
│       ├── app/
│       │   ├── application.py
│       │   ├── config.py
│       │   └── state.py
│       │
│       ├── domain/
│       │   ├── models/
│       │   │   ├── story.py
│       │   │   └── chapter.py
│       │   │
│       │   └── repositories/
│       │       └── story_repository.py
│       │
│       ├── application/
│       │   ├── services/
│       │   │   └── story_service.py
│       │   │
│       │   └── use_cases/
│       │       ├── load_story.py
│       │       └── delete_story.py
│       │
│       ├── infrastructure/
│       │   ├── database/
│       │   │   └── sqlite.py
│       │   │
│       │   └── repositories/
│       │       └── sqlite_story_repository.py
│       │
│       ├── events/
│       │   ├── bus.py
│       │   └── events.py
│       │
│       └── presentation/
│           ├── windows/
│           │   └── main_window.py
│           │
│           ├── dialogs/
│           │
│           ├── widgets/
│           │   ├── story_card.py
│           │   └── progress_widget.py
│           │
│           ├── viewmodels/
│           │   └── story_view_model.py
│           │
│           └── models/
│               └── story_list_model.py
│
└── tests/
    ├── unit/
    └── integration/
```

---

# 56. Data flow

Khi user click Story:

```text
┌──────────┐
│   View   │
└────┬─────┘
     │ Signal
     ▼
┌──────────────┐
│  Controller  │
└────┬─────────┘
     │
     ▼
┌──────────────┐
│  ViewModel   │
└────┬─────────┘
     │ method call
     ▼
┌──────────────┐
│   Service    │
└────┬─────────┘
     │
     ▼
┌──────────────┐
│ Repository   │
└────┬─────────┘
     │
     ▼
┌──────────────┐
│   SQLite     │
└──────────────┘
```

Sau đó:

```text
SQLite
   ↓
Repository
   ↓
Service
   ↓
ViewModel
   ↓ Signal
View
```

---

# 57. Cross-module event

Crawler hoàn thành:

```text
Crawler
   │
   ▼
EventBus
   │
   ├────────→ Dashboard
   │
   ├────────→ Logger
   │
   ├────────→ StatusBar
   │
   └────────→ Notification
```

Crawler không cần import:

```python
Dashboard
Logger
StatusBar
Notification
```

---

# 58. Toàn bộ architecture

Đây là hình ảnh mental model quan trọng nhất của **Phần III**:

```text
                         ┌─────────────────┐
                         │   Main / App     │
                         │ Composition Root │
                         └────────┬────────┘
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
             ▼                    ▼                    ▼
          State                EventBus            Config
             │                    │
          Signal               Events
             │                    │
             ▼                    ▼
       ┌───────────┐       ┌────────────┐
       │ ViewModel │       │ Subscribers│
       └─────┬─────┘       └────────────┘
             │
          Signal
             │
             ▼
       ┌───────────┐
       │   View    │
       └───────────┘
             │
             │
             ▼
       ┌───────────┐
       │ Controller│
       └─────┬─────┘
             │
             ▼
       ┌───────────┐
       │  Service  │
       └─────┬─────┘
             │
             ▼
       ┌───────────┐
       │Repository │
       └─────┬─────┘
             │
             ▼
       ┌───────────┐
       │ Database  │
       └───────────┘
```

---

# 59. Quy tắc dependency

Bạn có thể ghi lại thành:

```text
View
 ↓
ViewModel / Controller
 ↓
Application Service
 ↓
Domain
```

và:

```text
Infrastructure
     ↓
implements
     ↓
Domain/Application abstraction
```

Trong khi:

```text
Domain
  X→ PySide6
  X→ SQLite
  X→ HTTPX
  X→ QFileDialog
```

---

# 60. Quy tắc cho từng layer

| Layer          | Được biết            | Không nên biết          |
| -------------- | -------------------- | ----------------------- |
| View           | ViewModel, Qt        | SQLite, SQL             |
| ViewModel      | Service, State       | QWidget cụ thể          |
| Controller     | Use Case/Service     | Database                |
| Service        | Domain, Repository   | QWidget                 |
| Repository     | Database             | QWidget                 |
| Domain         | Business rules       | Qt                      |
| Infrastructure | DB, HTTP, filesystem | UI                      |
| Event Bus      | Events/subscribers   | Business implementation |

---

# 61. Bài tập lớn của Buổi 35

Không cần code toàn bộ Story Reader.

Hãy tự thiết kế structure:

```text
story_reader/
```

với các thành phần:

```text
Story
Chapter
Source
Crawler
StoryRepository
ChapterRepository
StoryService
CrawlerService
MainWindow
StoryListModel
StoryViewModel
EventBus
AppState
SQLiteDatabase
```

Phân loại từng class vào:

```text
Domain
Application
Infrastructure
Presentation
App
Events
```

Đây là bài tập rất quan trọng.

---

# 62. Bài tập 2 — Dependency Graph

Vẽ:

```text
MainWindow
     ↓
ViewModel
     ↓
Service
     ↓
Repository
     ↓
Database
```

Sau đó thêm:

```text
AppState
EventBus
```

vào đúng vị trí.

---

# 63. Bài tập 3 — Composition Root

Viết:

```python
class Application:

    def __init__(self):
        ...
```

nó phải tạo:

```text
Database
Repository
Service
State
EventBus
ViewModel
MainWindow
```

Không được để:

```python
MainWindow()
```

tự tạo Repository.

---

# 64. Bài tập 4 — Architecture Violation

Tìm lỗi trong code:

```python
class MainWindow(QMainWindow):

    def __init__(self):

        self.db = sqlite3.connect(
            "story.db"
        )

    def load_story(self):

        cursor = self.db.cursor()

        cursor.execute(
            "SELECT * FROM stories"
        )
```

Có ít nhất **3 vấn đề architecture**.

Hãy tự sửa thành:

```text
MainWindow
 ↓
ViewModel
 ↓
Service
 ↓
Repository
 ↓
SQLite
```

---

# 65. Bài tập 5 — Testability

Viết:

```python
class FakeStoryRepository:
    ...
```

sau đó inject vào:

```python
StoryService
```

Mục tiêu:

```text
Không cần SQLite
Không cần PySide6
Không cần GUI
```

vẫn test được business logic.

---

# 66. Mini Project tổng kết Phần III

Tạo:

# `Story Manager`

Chức năng:

```text
┌─────────────────────────────────────────┐
│ Story Manager                           │
├─────────────┬───────────────────────────┤
│ Stories     │ Story Detail              │
│             │                           │
│ Naruto      │ Title: Naruto             │
│ One Piece   │ Author: Kishimoto         │
│ Bleach      │ Chapters: 700             │
│             │                           │
│             │ [Delete] [Refresh]        │
└─────────────┴───────────────────────────┘
```

Architecture:

```text
MainWindow
     │
     ▼
StoryViewModel
     │
     ▼
StoryService
     │
     ▼
StoryRepository
     │
     ▼
SQLite
```

State:

```text
AppState
   │
   └── selected_story_id
```

Signals:

```text
story_selected
story_changed
loading_changed
error_occurred
```

Event Bus:

```text
StoryDeleted
StoryUpdated
```

---

# 67. Sau Mini Project, bạn đã hoàn thành Phần III

Bạn đã đi qua:

```text
25  UI / Business separation
26  MVC
27  MVVM
28  Controller
29  Service Layer
30  Repository
31  Dependency Injection
32  Application State
33  Event Bus
34  Signal Architecture
35  Project Structure
```

Đây là bước chuyển rất lớn:

```text
PySide6 beginner
       ↓
PySide6 application developer
```

---

# 68. Chuẩn bị sang Phần IV

Phần tiếp theo cực kỳ quan trọng với loại application mà bạn muốn xây:

# **Phần IV — Threading & Concurrency**

Roadmap:

```text
36. GUI Thread
37. Vì sao GUI bị freeze?
38. QThread
39. Worker Object Pattern
40. Signal giữa Worker và GUI
41. Progress Bar
42. Cancel Task
43. QThreadPool
44. QRunnable
45. Concurrent Tasks
46. PySide6 + asyncio
47. PySide6 + HTTP
48. Mini Project — Download Manager
```

Đặc biệt với **Story Reader/Crawler**, phần này sẽ biến architecture hiện tại:

```text
Crawler
   ↓
Service
   ↓
Repository
```

thành:

```text
                 GUI Thread
                     │
                     ▼
                Controller
                     │
                     ▼
                  Worker
                     │
             ┌───────┴───────┐
             │               │
          Crawling        Download
             │               │
             └───────┬───────┘
                     │
                  Signals
                     │
                     ▼
                 GUI Thread
```

và chúng ta sẽ giải quyết vấn đề kinh điển của PySide6:

> **Tại sao chỉ một vòng `for` hoặc một HTTP request có thể làm toàn bộ GUI "Not Responding"?**

**Buổi 36 sẽ bắt đầu từ chính bản chất của GUI Thread và Qt Event Loop**, chứ chưa vội học `QThread` bằng cách copy-paste code.
