# Phần III — UI Architecture

# Buổi 32 — Application State

Ở Buổi 31, chúng ta đã học **Dependency Injection**.

Bây giờ chúng ta gặp một vấn đề rất quan trọng khi ứng dụng PySide6 bắt đầu lớn:

> **State của ứng dụng nên nằm ở đâu?**

Ví dụ Story Reader của chúng ta có:

```text
Story đang chọn
Chapter đang đọc
Trang hiện tại
Từ khóa tìm kiếm
Filter
Sort
Theme
Trạng thái crawler
Download progress
```

Nếu mỗi widget tự giữ một phần state, application sẽ rất khó quản lý.

Hôm nay chúng ta xây dựng mental model cho **Application State**.

---

# 1. State là gì?

State đơn giản là:

> **Thông tin mô tả trạng thái hiện tại của application.**

Ví dụ:

```python
selected_story_id = 10
selected_chapter_id = 35
search_keyword = "python"
current_page = 2
dark_mode = True
```

Tất cả đều là state.

---

# 2. State khác với dữ liệu

Đây là điểm rất quan trọng.

Database có:

```text
Story
Chapter
Author
```

Đó là **persistent data**.

Trong khi:

```text
selected_story_id = 10
current_page = 2
search_keyword = "python"
```

là **runtime state**.

Ví dụ:

```text
Database
    │
    ├── Story 1
    ├── Story 2
    └── Story 3

Application State
    │
    ├── selected_story = Story 2
    ├── current_chapter = 15
    └── search = "python"
```

Khi đóng app:

```text
Application State → mất
```

Database:

```text
Database → vẫn còn
```

---

# 3. Ba loại State

Trong architecture, chúng ta nên phân biệt ít nhất:

```text
Domain State
Application State
UI State
```

---

# 4. Domain State

Domain State thuộc về business/domain.

Ví dụ:

```python
@dataclass
class Story:
    id: int
    title: str
    status: str
```

Story có:

```text
title
status
author
chapters
```

Đây là state của domain object.

Ví dụ:

```python
story.status = "completed"
```

Đây không phải UI state.

---

# 5. Application State

Application State mô tả trạng thái của toàn application.

Ví dụ Story Reader:

```python
@dataclass
class AppState:

    selected_story_id: int | None = None
    selected_chapter_id: int | None = None

    search_keyword: str = ""

    current_page: int = 1
```

Đây là state mà nhiều thành phần trong application có thể quan tâm.

---

# 6. UI State

UI State liên quan trực tiếp đến presentation.

Ví dụ:

```text
Sidebar đang mở
Dialog đang visible
Loading indicator
Current tab
Splitter position
```

Ví dụ:

```python
@dataclass
class UIState:

    sidebar_visible: bool = True
    current_tab: str = "stories"
    loading: bool = False
```

---

# 7. Một ví dụ rất rõ

Story Reader:

```text
Domain State
────────────────────
Story.title
Story.status
Chapter.content


Application State
────────────────────
selected_story_id
selected_chapter_id
search_keyword


UI State
────────────────────
sidebar_visible
current_tab
loading
```

Đừng gom tất cả vào một object.

---

# 8. Anti-pattern: Mỗi Widget giữ State riêng

Ví dụ:

```python
class StoryList(QWidget):

    def __init__(self):
        self.selected_story_id = None
```

Chapter widget:

```python
class ChapterList(QWidget):

    def __init__(self):
        self.selected_story_id = None
```

Reader:

```python
class Reader(QWidget):

    def __init__(self):
        self.selected_story_id = None
```

Bây giờ:

```text
StoryList
    selected_story = 10

ChapterList
    selected_story = 11

Reader
    selected_story = 10
```

💥 State không đồng bộ.

---

# 9. Single Source of Truth

Một nguyên tắc rất quan trọng:

> **Một state quan trọng nên có một nguồn sự thật duy nhất.**

Ví dụ:

```text
                AppState
                   │
          selected_story_id = 10
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
    StoryList   ChapterList  Reader
```

Các UI component đọc state.

Không tự tạo bản sao state.

---

# 10. Application State Object

Ta có thể bắt đầu đơn giản:

```python
from dataclasses import dataclass


@dataclass
class AppState:

    selected_story_id: int | None = None
    selected_chapter_id: int | None = None

    search_keyword: str = ""

    current_page: int = 1
```

Sau đó:

```python
state = AppState()
```

---

# 11. State Mutation

Ví dụ:

```python
state.selected_story_id = 10
```

hoặc:

```python
state.search_keyword = "python"
```

Nhưng có một vấn đề:

> Ai thay đổi state?

Nếu bất kỳ widget nào cũng được phép:

```python
state.selected_story_id = ...
```

thì architecture lại trở nên khó kiểm soát.

---

# 12. Không nên để Widget tùy ý mutate State

Không nên:

```python
class StoryList:

    def on_click(self, story_id):
        app_state.selected_story_id = story_id
```

Nếu application lớn, hàng chục widget có thể sửa state.

Thay vào đó:

```text
Widget
   ↓
Controller / ViewModel
   ↓
Application State
```

---

# 13. Controller thay đổi State

Ví dụ:

```python
class StoryController:

    def __init__(self, state):
        self.state = state

    def select_story(self, story_id):
        self.state.selected_story_id = story_id
```

UI:

```text
User click Story
        ↓
Controller
        ↓
AppState
```

---

# 14. Nhưng State thay đổi thì UI phải biết

Đây mới là vấn đề lớn.

Ví dụ:

```python
state.selected_story_id = 10
```

Làm sao:

```text
ChapterList
Reader
StatusBar
```

biết rằng state đã thay đổi?

Chúng ta cần **notification**.

Đây chính là cầu nối sang:

**Buổi 33 — Event Bus**

và:

**Buổi 34 — Signal-based Architecture.**

---

# 15. State + Signal

Trong PySide6 có thể làm:

```python
from PySide6.QtCore import QObject, Signal


class AppState(QObject):

    story_changed = Signal(object)

    def __init__(self):
        super().__init__()

        self._selected_story_id = None

    @property
    def selected_story_id(self):
        return self._selected_story_id

    def select_story(self, story_id):

        if self._selected_story_id == story_id:
            return

        self._selected_story_id = story_id

        self.story_changed.emit(
            story_id
        )
```

Bây giờ:

```python
state.story_changed.connect(
    chapter_list.on_story_changed
)
```

---

# 16. Tại sao không dùng public attribute?

Thay vì:

```python
state.selected_story_id = 10
```

ta dùng:

```python
state.select_story(10)
```

Vì method có thể:

```text
validate
detect change
emit signal
log
persist
```

Ví dụ:

```python
def select_story(self, story_id):

    if story_id == self._selected_story_id:
        return

    self._selected_story_id = story_id

    self.story_changed.emit(
        story_id
    )
```

---

# 17. State trở thành Observable State

Mental model:

```text
                AppState
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
   StoryList   ChapterList   Reader
        ▲          ▲          ▲
        │          │          │
        └──── signals ────────┘
```

State thay đổi:

```text
AppState
   ↓
Signal
   ↓
UI cập nhật
```

---

# 18. Immutable State

Một hướng khác là coi state như immutable.

Ví dụ:

```python
@dataclass(frozen=True)
class AppState:

    selected_story_id: int | None = None
    search_keyword: str = ""
    current_page: int = 1
```

Không:

```python
state.selected_story_id = 10
```

Thay vào đó tạo state mới:

```python
new_state = AppState(
    selected_story_id=10,
    search_keyword=state.search_keyword,
    current_page=state.current_page,
)
```

Mental model:

```text
State 1
   ↓
Action
   ↓
State 2
```

Cách này rất mạnh khi application lớn, nhưng với PySide6 thuần Python chúng ta chưa cần áp dụng ngay cho mọi thứ.

---

# 19. Mutable vs Immutable

### Mutable

```python
state.current_page = 2
```

Ưu:

* đơn giản
* dễ hiểu
* phù hợp Python
* phù hợp app nhỏ/vừa

Nhược:

* khó trace mutation
* dễ bị thay đổi từ nhiều nơi

### Immutable

```text
State 1 → State 2 → State 3
```

Ưu:

* dễ trace
* predictable
* phù hợp state management lớn

Nhược:

* nhiều object
* code phức tạp hơn

---

# 20. State Machine

Có những state không nên chỉ là boolean.

Ví dụ crawler:

```python
is_running = True
```

không đủ.

Có thể:

```python
class CrawlStatus(Enum):

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    CANCELLING = "cancelling"
    COMPLETED = "completed"
    FAILED = "failed"
```

State:

```python
@dataclass
class CrawlState:

    status: CrawlStatus = CrawlStatus.IDLE
    progress: int = 0
    error: str | None = None
```

Đây là một **state machine đơn giản**.

---

# 21. State Transition

Ví dụ:

```text
IDLE
 │
 │ start
 ▼
RUNNING
 │
 ├── pause ──→ PAUSED
 │                │
 │                │ resume
 │                ▼
 │             RUNNING
 │
 ├── cancel ─→ CANCELLING
 │
 └── finish ─→ COMPLETED
```

Điều này đặc biệt hữu ích cho project Story Reader.

---

# 22. Application State không phải Database

Đừng làm:

```python
state.stories = database.get_all_stories()
```

rồi coi `state` là database.

Database:

```text
Persistent Storage
```

State:

```text
Runtime Context
```

Service:

```text
Business Operation
```

Ba thứ khác nhau.

---

# 23. State không phải Cache

Cache:

```text
key → value
```

mục tiêu:

```text
performance
```

State:

```text
application context
```

Ví dụ:

```text
selected_story_id
```

là state.

Trong khi:

```text
story_123 → Story object
```

có thể là cache.

---

# 24. State và Service

Service không nên phụ thuộc trực tiếp vào UI State.

Ví dụ không nên:

```python
class StoryService:

    def __init__(self, app_state):
        ...
```

nếu `app_state` chỉ chứa:

```text
current_tab
sidebar_visible
```

Business logic không cần biết UI.

---

# 25. Application State có thể được Service sử dụng?

Có, nhưng cần cẩn thận.

Ví dụ:

```text
current_user
current_project
```

có thể là Application Context.

Nhưng:

```text
current_tab
sidebar_visible
```

là UI State.

Nguyên tắc:

> **Dependency nên đi theo đúng layer.**

---

# 26. State trong MVVM

MVVM rất hợp với Application State.

```text
                 AppState
                    │
                    ▼
                ViewModel
                    │
                    ▼
                   View
```

Ví dụ:

```python
class StoryViewModel(QObject):

    stories_changed = Signal()

    def __init__(
        self,
        state,
        service,
    ):
        super().__init__()

        self.state = state
        self.service = service
```

ViewModel là cầu nối:

```text
Application State
        ↕
ViewModel
        ↕
View
```

---

# 27. State trong MVC

MVC:

```text
User
 ↓
View
 ↓
Controller
 ↓
Model / Service
 ↓
State
```

Controller có thể thay đổi Application State:

```python
class StoryController:

    def __init__(
        self,
        state,
        service,
    ):
        self.state = state
        self.service = service

    def select_story(self, story_id):
        self.state.select_story(story_id)
```

---

# 28. Một thiết kế tốt hơn

Thay vì cho Controller sửa trực tiếp:

```python
self.state.selected_story_id = story_id
```

dùng API của State:

```python
self.state.select_story(story_id)
```

Như vậy State kiểm soát mutation.

```text
Controller
    │
    ▼
 AppState
    │
    ├── validate
    ├── update
    └── notify
```

---

# 29. Ví dụ hoàn chỉnh

```python
from PySide6.QtCore import QObject, Signal


class AppState(QObject):

    story_changed = Signal(object)
    chapter_changed = Signal(object)

    def __init__(self):
        super().__init__()

        self._story_id = None
        self._chapter_id = None

    @property
    def story_id(self):
        return self._story_id

    @property
    def chapter_id(self):
        return self._chapter_id

    def select_story(self, story_id):

        if story_id == self._story_id:
            return

        self._story_id = story_id

        self.story_changed.emit(
            story_id
        )

    def select_chapter(self, chapter_id):

        if chapter_id == self._chapter_id:
            return

        self._chapter_id = chapter_id

        self.chapter_changed.emit(
            chapter_id
        )
```

---

# 30. Controller

```python
class StoryController:

    def __init__(
        self,
        state,
        service,
    ):
        self.state = state
        self.service = service

    def select_story(self, story_id):

        self.state.select_story(
            story_id
        )
```

---

# 31. View

```python
class StoryWindow(QMainWindow):

    def __init__(self, state):
        super().__init__()

        self.state = state

        self.state.story_changed.connect(
            self.on_story_changed
        )

    def on_story_changed(self, story_id):

        print(
            "Selected story:",
            story_id,
        )
```

---

# 32. Wiring bằng DI

Đây là nơi Buổi 31 kết nối với Buổi 32:

```python
state = AppState()

service = StoryService(
    repository
)

controller = StoryController(
    state,
    service,
)

window = StoryWindow(
    state
)
```

Ta có:

```text
Composition Root
       │
       ├── AppState
       │
       ├── Service
       │
       ├── Controller
       │
       └── View
```

---

# 33. Nhưng có một vấn đề

Nếu application lớn:

```text
AppState
```

có thể trở thành:

```python
@dataclass
class AppState:

    selected_story_id: int | None
    selected_chapter_id: int | None
    search_keyword: str
    current_page: int
    filter_status: str
    sort_column: str
    theme: str
    sidebar_visible: bool
    ...
```

Sau một thời gian:

```text
🚨 God State
```

Không tốt.

---

# 34. Chia State theo Domain

Thay vì:

```text
AppState
 ├── everything
```

có thể:

```text
ApplicationState
 │
 ├── NavigationState
 ├── StoryState
 ├── ReaderState
 ├── SearchState
 └── CrawlState
```

Ví dụ:

```python
@dataclass
class ReaderState:

    story_id: int | None = None
    chapter_id: int | None = None
    page: int = 1
```

Search:

```python
@dataclass
class SearchState:

    keyword: str = ""
    page: int = 1
```

Crawler:

```python
@dataclass
class CrawlState:

    status: CrawlStatus = CrawlStatus.IDLE
    progress: int = 0
```

---

# 35. Composite Application State

Có thể:

```python
@dataclass
class ApplicationState:

    reader: ReaderState
    search: SearchState
    crawl: CrawlState
```

Mental model:

```text
ApplicationState
       │
 ┌─────┼──────┐
 ▼     ▼      ▼
Reader Search Crawl
State  State  State
```

Đây là thiết kế tốt hơn cho application lớn.

---

# 36. State Ownership

Câu hỏi rất quan trọng:

> **Ai sở hữu state?**

Ví dụ:

```text
Application
    │
    └── ApplicationState
```

Application giữ state.

Các component:

```text
Controller
ViewModel
View
```

được inject hoặc subscribe.

```text
          ApplicationState
                 │
       ┌─────────┼─────────┐
       ▼         ▼         ▼
 Controller  ViewModel    View
```

---

# 37. State Lifecycle

State thường sống cùng application:

```text
QApplication
     │
     ▼
Application
     │
     ▼
ApplicationState
```

Khi app đóng:

```text
ApplicationState destroyed
```

Nhưng một state nhỏ có thể sống ngắn hơn:

```text
DialogState
```

```text
Dialog opened
     ↓
DialogState created
     ↓
Dialog closed
     ↓
destroy
```

---

# 38. State Persistence

Có những state cần giữ lại sau khi đóng app:

```text
window size
window position
theme
last opened story
last opened chapter
```

Nhưng đừng nhầm:

```text
runtime state
```

với:

```text
persistent state
```

Có thể dùng:

```text
QSettings
```

mà chúng ta sẽ học sâu ở **Buổi 87**.

Ví dụ:

```text
Application State
       │
       ├── runtime
       │
       └── persistent subset
                  ↓
               QSettings
```

---

# 39. State và Undo/Redo

Một lợi ích thú vị của state model là có thể lưu:

```text
State 1
State 2
State 3
State 4
```

Từ đó xây:

```text
Undo
Redo
History
```

Đặc biệt hữu ích cho editor.

Không phải application nào cũng cần, nhưng mental model rất quan trọng.

---

# 40. State Transition nên rõ ràng

Thay vì:

```python
state.status = "running"
```

có thể:

```python
state.start()
```

Thay vì:

```python
state.status = "paused"
```

dùng:

```python
state.pause()
```

Vì method thể hiện **business transition**.

```text
start()
pause()
resume()
cancel()
complete()
```

rõ hơn:

```text
status = ...
```

---

# 41. Application State ≠ Event Bus

Đây là hai thứ chúng ta sẽ dùng cùng nhau nhưng chúng khác nhau.

### State

Trả lời:

> **Hiện tại application đang ở trạng thái nào?**

Ví dụ:

```text
selected_story = 10
```

### Event

Trả lời:

> **Điều gì vừa xảy ra?**

Ví dụ:

```text
StorySelected
```

---

# 42. State vs Event

Ví dụ:

```text
StorySelected(10)
```

là event.

Sau event:

```text
selected_story_id = 10
```

là state.

Mental model:

```text
Event
  │
  ▼
State Transition
  │
  ▼
New State
```

Đây là nền tảng cực kỳ quan trọng cho Buổi 33.

---

# 43. State vs Signal

Signal của Qt:

```python
story_changed.emit(10)
```

là cơ chế **notification**.

State:

```python
state.story_id == 10
```

là **data hiện tại**.

Signal nói:

> "Có thay đổi."

State nói:

> "Hiện tại đang là 10."

---

# 44. Một architecture rất đẹp

```text
                    Application
                         │
                         ▼
                  ApplicationState
                         │
                ┌────────┴────────┐
                ▼                 ▼
           State Transition      Events
                │                 │
                ▼                 ▼
            ViewModels        Event Bus
                │                 │
                ▼                 ▼
               Views           Services
```

Chúng ta chưa cần implement toàn bộ ngay.

Nhưng đây là mental model để hướng tới architecture production.

---

# 45. Story Reader State

Hãy thiết kế state cho project cuối:

```text
Story Reader
```

Tôi đề xuất:

```python
@dataclass
class ReaderState:

    story_id: int | None = None
    chapter_id: int | None = None

    page: int = 1

    font_size: int = 18
    auto_scroll: bool = False
```

Search:

```python
@dataclass
class SearchState:

    keyword: str = ""
    page: int = 1
```

Crawler:

```python
@dataclass
class CrawlState:

    status: CrawlStatus = CrawlStatus.IDLE
    progress: int = 0
    current_url: str | None = None
    error: str | None = None
```

UI:

```python
@dataclass
class UIState:

    sidebar_visible: bool = True
    current_tab: str = "stories"
```

---

# 46. ApplicationState

```python
@dataclass
class ApplicationState:

    reader: ReaderState
    search: SearchState
    crawl: CrawlState
    ui: UIState
```

Khởi tạo:

```python
state = ApplicationState(
    reader=ReaderState(),
    search=SearchState(),
    crawl=CrawlState(),
    ui=UIState(),
)
```

---

# 47. Luồng khi người dùng chọn Story

```text
User
 │
 │ click Story #10
 ▼
StoryList
 │
 ▼
Controller
 │
 ▼
state.reader.story_id = 10
 │
 ▼
state notification
 │
 ├──────────────┐
 ▼              ▼
ChapterList    Reader
 │              │
 ▼              ▼
load chapters  load story
```

Đây chính là **state-driven UI**.

---

# 48. Nguyên tắc thiết kế State

Hãy nhớ 7 nguyên tắc:

### 1. Single Source of Truth

```text
Một state quan trọng → một nguồn.
```

### 2. State không phải Database

```text
Runtime ≠ Persistence
```

### 3. State không phải Event

```text
Current value ≠ Something happened
```

### 4. State không phải UI

```text
Application State ≠ Widget State
```

### 5. Mutation phải có kiểm soát

```text
select_story()
```

tốt hơn:

```text
state.story_id = ...
```

### 6. Chia State khi nó lớn

```text
ReaderState
SearchState
CrawlState
```

### 7. Business logic không phụ thuộc UI State

```text
Domain/Application
       ↓
không biết QWidget
```

---

# 49. Bài tập 1 — Phân loại State

Cho danh sách:

```text
1. selected_story_id
2. QPushButton.isEnabled()
3. Story.title
4. current_tab
5. crawl_progress
6. database connection
7. search_keyword
8. window_width
9. Chapter.content
10. current_chapter_id
```

Hãy phân loại thành:

```text
Domain State
Application State
UI State
Infrastructure
```

---

# 50. Bài tập 2 — Thiết kế ReaderState

Thiết kế:

```text
ReaderState
```

cho Story Reader có:

```text
story
chapter
page
font size
line spacing
auto scroll
reading mode
```

Hãy quyết định field nào thực sự là state.

---

# 51. Bài tập 3 — State Transition

Thiết kế:

```text
CrawlState
```

với:

```text
IDLE
RUNNING
PAUSED
CANCELLING
COMPLETED
FAILED
```

và các method:

```python
start()
pause()
resume()
cancel()
complete()
fail()
```

Không cho phép transition sai.

Ví dụ:

```text
COMPLETED → pause()
```

phải bị từ chối.

---

# 52. Bài tập 4 — Signal

Viết:

```python
class ReaderState(QObject):
    ...
```

có:

```python
story_changed
chapter_changed
page_changed
```

Khi:

```python
state.set_page(5)
```

thì:

```python
page_changed.emit(5)
```

---

# 53. Bài tập 5 — Controller + State

Viết:

```python
class ReaderController:
    ...
```

nhận:

```text
ReaderState
ReaderService
```

và implement:

```python
open_story(story_id)
open_chapter(chapter_id)
next_page()
previous_page()
```

Controller không được trực tiếp truy cập database.

---

# 54. Bài tập 6 — DI + Application State

Dùng kiến thức Buổi 31:

```text
Composition Root
```

hãy wiring:

```text
ReaderState
ReaderService
ReaderController
ReaderWindow
```

thành:

```text
ReaderWindow
      ↑
ReaderController
      ↓
ReaderService
      ↓
Repository

ReaderController
      ↓
ReaderState
      ↓
ReaderWindow
```

---

# 55. Bài tập 7 — Tìm lỗi architecture

Cho:

```python
class StoryList(QWidget):

    def __init__(self):
        self.selected_story_id = None

    def select_story(self, story_id):
        self.selected_story_id = story_id
```

và:

```python
class Reader(QWidget):

    def __init__(self):
        self.selected_story_id = None
```

Hãy giải thích tại sao đây là architecture không tốt.

Sau đó refactor thành:

```text
ApplicationState
      ↓
StoryList
Reader
```

---

# 56. Bài tập 8 — Mini Project

Xây một **State Manager** nhỏ:

```text
Application
    │
    ▼
AppState
    │
    ├── ReaderState
    ├── SearchState
    └── CrawlState
```

Yêu cầu:

```text
1. State thay đổi được
2. State phát Signal
3. View subscribe Signal
4. Controller thay đổi State
5. Không widget nào tự sở hữu application state
```

---

# 57. Kiến trúc sau Buổi 32

Đến thời điểm này:

```text
                 Main
                  │
                  ▼
          Composition Root
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
    Services    State       Views
       │          │          │
       ▼          ▼          ▼
 Repository   State Events  Controller
       │
       ▼
    Database
```

Và dependency direction:

```text
Presentation
     ↓
Application
     ↓
Domain
```

Infrastructure implement abstraction:

```text
Infrastructure
      ↑
Repository Interface
      ↑
Application
```

---

# 58. Điều quan trọng nhất của Buổi 32

Đừng nhớ:

```python
@dataclass
class AppState:
    ...
```

mà hãy nhớ mental model:

```text
             STATE
               │
       "Hiện tại là gì?"
               │
               ▼
        Single Source
          of Truth
               │
               ▼
       State Transition
               │
               ▼
          Notification
               │
               ▼
              UI
```

Trong khi:

```text
EVENT
  │
  │ "Điều gì vừa xảy ra?"
  ▼
Event Bus / Signal
```

Hai khái niệm này sẽ kết hợp cực kỳ mạnh trong hai buổi tiếp theo.

---

## Tiếp theo — Buổi 33: Event Bus

Chúng ta sẽ xây từ đầu:

```text
Publisher
    │
    ▼
 Event Bus
    │
 ┌──┼──────────┐
 ▼  ▼          ▼
 A  B          C
```

và áp dụng vào Story Reader:

```text
Crawler
   │
   │ CrawlProgress
   ▼
EventBus
   │
   ├── Dashboard
   ├── ProgressBar
   ├── StatusBar
   └── Logger
```

Đặc biệt, **Buổi 33 sẽ phân biệt rất rõ `Signal`, `Event Bus`, `Application State` và `Service Call`**, vì đây là 4 cơ chế rất dễ bị trộn lẫn khi xây PySide6 application lớn.
