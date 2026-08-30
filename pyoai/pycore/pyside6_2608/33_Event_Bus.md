# Phần III — UI Architecture

# Buổi 33 — Event Bus trong PySide6

Ở **Buổi 32**, chúng ta đã xây dựng `Application State` và phân biệt:

```text
State  → "Hiện tại đang là gì?"
Event  → "Điều gì vừa xảy ra?"
```

Hôm nay chúng ta học **Event Bus** — một pattern cực kỳ hữu ích khi ứng dụng PySide6 bắt đầu có nhiều module.

---

# 1. Event Bus là gì?

Event Bus là một trung gian cho phép các component:

* **publish event**
* **subscribe event**
* không cần biết trực tiếp nhau.

Thay vì:

```text
Crawler ─────────→ Dashboard
       ─────────→ StatusBar
       ─────────→ Logger
       ─────────→ Notification
```

ta có:

```text
                Event Bus
              ↗     ↑     ↖
             /      │      \
        Dashboard Status  Logger
             ↑
          Crawler
```

Crawler chỉ cần:

```python
event_bus.publish(...)
```

Nó **không cần biết** Dashboard tồn tại.

---

# 2. Tại sao cần Event Bus?

Giả sử Story Reader có crawler.

Crawler phát sinh:

```text
CrawlStarted
CrawlProgress
ChapterDownloaded
CrawlCompleted
CrawlFailed
```

Nếu không có Event Bus:

```python
class Crawler:

    def __init__(
        self,
        dashboard,
        status_bar,
        logger,
        notification,
    ):
        ...
```

Crawler phải biết rất nhiều thứ.

Đây là coupling cao.

---

# 3. Coupling

Ví dụ:

```text
Crawler
 ├── Dashboard
 ├── StatusBar
 ├── Logger
 └── Notification
```

Crawler bị phụ thuộc vào presentation.

Architecture trở nên:

```text
Infrastructure
      ↓
Presentation
```

Đây là hướng dependency không đẹp.

---

# 4. Với Event Bus

Crawler chỉ phụ thuộc:

```python
EventBus
```

```text
Crawler
   │
   ▼
EventBus
   │
   ├── Dashboard
   ├── StatusBar
   ├── Logger
   └── Notification
```

Crawler không biết các subscriber.

Đây chính là **loose coupling**.

---

# 5. Event là gì?

Event thường là một object immutable mô tả một điều đã xảy ra.

Ví dụ:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class CrawlStarted:
    story_id: int
```

Progress:

```python
@dataclass(frozen=True)
class CrawlProgress:
    story_id: int
    current: int
    total: int
```

Completed:

```python
@dataclass(frozen=True)
class CrawlCompleted:
    story_id: int
```

---

# 6. Event nên là quá khứ

Tên event thường dùng dạng:

```text
StorySelected
ChapterDownloaded
CrawlStarted
CrawlCompleted
```

Không nên:

```text
StartCrawl
DownloadChapter
```

Vì:

```text
Event = điều đã xảy ra
Command = yêu cầu thực hiện
```

Đây là một distinction rất quan trọng.

---

# 7. Event vs Command

### Command

```text
StartCrawl
```

nghĩa:

> Hãy bắt đầu crawl.

### Event

```text
CrawlStarted
```

nghĩa:

> Crawl đã bắt đầu.

Mental model:

```text
Command
   │
   ▼
Handler
   │
   ▼
Action
   │
   ▼
Event
```

Chúng ta chưa cần xây Command Bus hôm nay.

---

# 8. Event Bus cơ bản nhất

Python thuần:

```python
class EventBus:

    def __init__(self):
        self._handlers = {}

    def subscribe(self, event_type, handler):
        self._handlers.setdefault(
            event_type,
            []
        ).append(handler)

    def publish(self, event):

        event_type = type(event)

        for handler in self._handlers.get(
            event_type,
            []
        ):
            handler(event)
```

Đây là phiên bản đơn giản nhất.

---

# 9. Sử dụng

```python
bus = EventBus()
```

Subscribe:

```python
bus.subscribe(
    CrawlStarted,
    on_crawl_started,
)
```

Publish:

```python
bus.publish(
    CrawlStarted(
        story_id=10
    )
)
```

Flow:

```text
publish()
   ↓
EventBus
   ↓
CrawlStarted handlers
   ↓
on_crawl_started()
```

---

# 10. Ví dụ hoàn chỉnh

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class CrawlStarted:
    story_id: int


class EventBus:

    def __init__(self):
        self._handlers = {}

    def subscribe(self, event_type, handler):

        self._handlers.setdefault(
            event_type,
            []
        ).append(handler)

    def publish(self, event):

        for handler in self._handlers.get(
            type(event),
            []
        ):
            handler(event)


def dashboard_handler(event):
    print(
        "Dashboard:",
        event.story_id,
    )


def logger_handler(event):
    print(
        "LOG: crawl started",
        event.story_id,
    )


bus = EventBus()

bus.subscribe(
    CrawlStarted,
    dashboard_handler,
)

bus.subscribe(
    CrawlStarted,
    logger_handler,
)

bus.publish(
    CrawlStarted(10)
)
```

Kết quả:

```text
Dashboard: 10
LOG: crawl started 10
```

---

# 11. Điểm mạnh

Crawler chỉ cần:

```python
bus.publish(
    CrawlStarted(10)
)
```

Crawler không biết:

```text
Dashboard
Logger
StatusBar
Notification
```

Đây là điểm quan trọng nhất.

---

# 12. Event Bus trong PySide6

Trong PySide6, chúng ta có một lựa chọn rất tự nhiên:

```text
QObject
Signal
```

Có thể xây Event Bus dựa trên Signal.

---

# 13. Event Bus bằng Signal

```python
from PySide6.QtCore import QObject, Signal


class EventBus(QObject):

    event_published = Signal(object)

    def publish(self, event):
        self.event_published.emit(event)
```

Subscribe:

```python
bus.event_published.connect(
    handler
)
```

Publish:

```python
bus.publish(
    CrawlStarted(10)
)
```

---

# 14. Nhưng cách này chưa tối ưu

Nếu tất cả subscriber nhận tất cả event:

```text
event_published
      │
 ┌────┼────┬────┐
 ▼    ▼    ▼    ▼
 A    B    C    D
```

Mỗi handler phải tự kiểm tra:

```python
if isinstance(event, CrawlStarted):
    ...
```

Không đẹp.

Ta có thể xây Event Bus typed hơn.

---

# 15. Typed Event Bus

```python
from collections import defaultdict
from typing import Callable


class EventBus:

    def __init__(self):
        self._handlers = defaultdict(list)

    def subscribe(
        self,
        event_type,
        handler: Callable,
    ):
        self._handlers[event_type].append(
            handler
        )

    def publish(self, event):

        handlers = self._handlers[
            type(event)
        ]

        for handler in handlers:
            handler(event)
```

---

# 16. unsubscribe

Đây là vấn đề rất quan trọng.

Nếu widget:

```text
created
   ↓
subscribe
```

sau đó:

```text
destroyed
```

nhưng EventBus vẫn giữ reference tới handler:

```text
EventBus
   ↓
handler
   ↓
Widget
```

Widget có thể không được garbage collect đúng như mong muốn.

Vì vậy cần:

```python
unsubscribe()
```

---

# 17. Implement unsubscribe

```python
class EventBus:

    def __init__(self):
        self._handlers = {}

    def subscribe(
        self,
        event_type,
        handler,
    ):
        self._handlers.setdefault(
            event_type,
            []
        ).append(handler)

    def unsubscribe(
        self,
        event_type,
        handler,
    ):
        handlers = self._handlers.get(
            event_type,
            []
        )

        if handler in handlers:
            handlers.remove(handler)

    def publish(self, event):

        for handler in self._handlers.get(
            type(event),
            []
        ):
            handler(event)
```

---

# 18. `subscribe()` nên trả về unsubscribe function

Một design đẹp hơn:

```python
unsubscribe = bus.subscribe(
    CrawlStarted,
    handler,
)
```

Sau đó:

```python
unsubscribe()
```

Ví dụ:

```python
def subscribe(
    self,
    event_type,
    handler,
):

    self._handlers.setdefault(
        event_type,
        []
    ).append(handler)

    def unsubscribe():
        self._handlers[
            event_type
        ].remove(handler)

    return unsubscribe
```

---

# 19. Event Bus + QObject lifecycle

Trong PySide6, ta có thể để QObject quản lý subscription.

Ví dụ ý tưởng:

```python
class Dashboard(QObject):

    def __init__(self, bus):
        super().__init__()

        self.bus = bus

        self.bus.subscribe(
            CrawlProgress,
            self.on_progress,
        )
```

Khi Dashboard bị destroy, cần cleanup subscription.

Đây là một vấn đề cần đặc biệt chú ý khi thiết kế Event Bus cho GUI.

---

# 20. Event Bus không phải Signal

Đây là điểm rất quan trọng.

### Signal

Thường là giao tiếp:

```text
Object A
   ↓
Object B
```

Ví dụ:

```python
button.clicked.connect(
    window.on_clicked
)
```

### Event Bus

Giao tiếp:

```text
Publisher
    ↓
Event Bus
    ↓
Multiple subscribers
```

Publisher không biết subscriber.

---

# 21. Signal phù hợp khi nào?

Ví dụ:

```text
QPushButton
    ↓
MainWindow
```

hoặc:

```text
Worker
    ↓
ProgressWidget
```

Nếu A biết B:

```python
worker.progress.connect(
    progress_bar.setValue
)
```

Signal là lựa chọn rất tốt.

---

# 22. Event Bus phù hợp khi nào?

Khi:

```text
A
```

không nên biết:

```text
B
C
D
```

Ví dụ:

```text
Crawler
   ↓
EventBus
   ├── Dashboard
   ├── Logger
   ├── Notification
   └── Statistics
```

---

# 23. Đừng lạm dụng Event Bus

Đây là lỗi architecture rất phổ biến.

Không nên:

```text
Button
 ↓
EventBus
 ↓
MainWindow
```

nếu đơn giản chỉ cần:

```python
button.clicked.connect(
    main_window.on_click
)
```

Event Bus làm architecture phức tạp hơn.

Nguyên tắc:

> **Dùng Signal cho local communication. Event Bus cho cross-module communication.**

---

# 24. Local vs Global Communication

### Local

```text
Widget
 ↓
Widget
```

dùng:

```text
Signal
```

### Module

```text
Crawler
 ↓
Application
```

có thể:

```text
Event Bus
```

---

# 25. Story Reader Architecture

Ví dụ:

```text
                  EventBus
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
   Dashboard      StatusBar      Logger
       ▲
       │
    Crawler
```

Crawler:

```python
bus.publish(
    CrawlProgress(
        story_id=10,
        current=50,
        total=100,
    )
)
```

Dashboard:

```python
def on_progress(event):

    percent = (
        event.current
        / event.total
        * 100
    )

    self.progress_bar.setValue(
        int(percent)
    )
```

Logger:

```python
def on_progress(event):

    logger.info(
        "Story %s: %s/%s",
        event.story_id,
        event.current,
        event.total,
    )
```

Crawler không biết hai component này.

---

# 26. Event Bus + Application State

Đây là phần nối trực tiếp với Buổi 32.

Ví dụ:

```text
Command
   │
   ▼
Controller
   │
   ▼
State mutation
   │
   ▼
Event
   │
   ▼
EventBus
   │
   ├── ViewModel
   ├── UI
   └── Logger
```

Ví dụ:

```text
User chọn Story
       ↓
Controller
       ↓
state.select_story(10)
       ↓
StorySelected
       ↓
EventBus
       ↓
ChapterList / Reader
```

---

# 27. Nhưng State có cần Event Bus không?

Không nhất thiết.

Ta có thể:

```text
AppState
   ↓
Signal
   ↓
View
```

Ví dụ:

```python
state.story_changed.connect(
    reader.on_story_changed
)
```

Event Bus chỉ cần khi event cần được phân phối rộng hơn.

---

# 28. State + Signal vs Event Bus

Một cách phân biệt thực tế:

### State

```text
"Story hiện tại là 10"
```

### State Signal

```text
"Story hiện tại vừa thay đổi"
```

### Event Bus

```text
"StorySelected event vừa xảy ra"
```

### Service

```text
"Load chapter 10"
```

---

# 29. Một ví dụ đầy đủ

```text
User
 │
 ▼
StoryList
 │
 │ clicked
 ▼
Controller
 │
 ├──────────────→ State
 │                  │
 │                  ▼
 │              story_id = 10
 │
 └──────────────→ Service
                       │
                       ▼
                  Repository
                       │
                       ▼
                    SQLite
```

Sau đó:

```text
Controller
    │
    ▼
EventBus
    │
    ▼
StorySelected
    │
 ┌──┼────────────┐
 ▼  ▼            ▼
Reader Chapter Status
```

Đây là architecture bắt đầu có khả năng scale.

---

# 30. Event nên immutable

Nên:

```python
@dataclass(frozen=True)
class StorySelected:

    story_id: int
```

Không nên:

```python
event.story_id = 20
```

Event đại diện cho một fact đã xảy ra.

Không nên để subscriber thay đổi nó.

---

# 31. Event không nên chứa QObject

Không nên:

```python
@dataclass
class StorySelected:

    widget: QWidget
```

Event nên chứa dữ liệu domain/application:

```python
@dataclass(frozen=True)
class StorySelected:

    story_id: int
```

Không:

```text
Event
  ↓
QWidget
```

Điều này giữ Event Bus độc lập với UI.

---

# 32. Event không nên chứa quá nhiều dữ liệu

Không nên:

```python
@dataclass
class StorySelected:

    story: Story
    chapters: list[Chapter]
    repository: Repository
    widget: QWidget
```

Nên:

```python
@dataclass(frozen=True)
class StorySelected:

    story_id: int
```

Subscriber cần dữ liệu gì thì dùng Service/Repository để lấy.

---

# 33. Event Naming Convention

Tôi đề xuất:

```text
StorySelected
StoryCreated
StoryDeleted

ChapterSelected
ChapterDownloaded
ChapterUpdated

CrawlStarted
CrawlProgress
CrawlCompleted
CrawlFailed

DownloadStarted
DownloadProgress
DownloadCompleted
DownloadFailed
```

Tránh:

```text
StoryEvent
DataEvent
UpdateEvent
SomethingChanged
```

Tên càng cụ thể càng tốt.

---

# 34. Event Bus và Thread

Đây là vấn đề quan trọng đối với PySide6.

Nếu worker chạy:

```text
QThread
```

và publish event:

```python
bus.publish(event)
```

thì cần hiểu event đang được xử lý ở thread nào.

Không nên mặc định:

```text
Event Bus = thread safe
```

Một Event Bus Python đơn giản:

```python
self._handlers
```

không tự nhiên trở thành thread-safe.

---

# 35. GUI Thread Rule

Nhớ nguyên tắc:

```text
Worker Thread
     │
     │ data/event
     ▼
GUI Thread
     │
     ▼
QWidget
```

Worker không nên trực tiếp:

```python
label.setText(...)
```

Thay vào đó:

```text
Worker
  ↓
Signal/Event
  ↓
GUI Thread
  ↓
Widget
```

---

# 36. Event Bus không tự động giải quyết Threading

Ví dụ:

```text
Worker Thread
    │
    ▼
EventBus
    │
    ▼
Widget
```

Không nên mặc định rằng Widget callback sẽ chạy an toàn trong GUI thread.

Khi kết hợp Event Bus với `QThread`, chúng ta phải thiết kế rõ:

```text
thread affinity
queued signal
event delivery
```

Đây sẽ là vấn đề chúng ta đào sâu ở **Phần IV — Threading & Concurrency**.

---

# 37. Event Bus có thể trở thành God Object

Một Event Bus chứa:

```text
500 event types
```

và:

```text
200 subscribers
```

sẽ trở thành:

```text
Global Event Soup
```

Rất khó debug.

Ví dụ:

```text
EventBus
 ├── StorySelected
 ├── UserLoggedIn
 ├── ThemeChanged
 ├── CrawlProgress
 ├── DownloadProgress
 ├── ...
 └── 200 more
```

Do đó Event Bus cần giới hạn phạm vi.

---

# 38. Một Event Bus toàn cục?

Có thể:

```python
event_bus = EventBus()
```

rồi mọi nơi import:

```python
from app.events import event_bus
```

Nhưng tôi **không khuyến khích** trong architecture lớn.

Đây là:

```text
Global State
```

và làm dependency trở nên ẩn.

---

# 39. Dependency Injection tốt hơn

Thay vì:

```python
from app.events import event_bus
```

dùng:

```python
class Crawler:

    def __init__(self, event_bus):
        self.event_bus = event_bus
```

Composition Root:

```python
event_bus = EventBus()

crawler = Crawler(
    event_bus=event_bus
)
```

Đây là nơi kiến thức **Buổi 31 — Dependency Injection** phát huy tác dụng.

---

# 40. Event Bus Interface

Nếu muốn architecture tốt hơn:

```python
from typing import Protocol


class EventPublisher(Protocol):

    def publish(self, event):
        ...


class EventSubscriber(Protocol):

    def subscribe(
        self,
        event_type,
        handler,
    ):
        ...
```

Application chỉ cần abstraction.

Infrastructure có implementation cụ thể.

---

# 41. Event Bus trong Clean Architecture

Có thể hình dung:

```text
Presentation
     │
     ▼
Application
     │
     ▼
 Event Port
     │
     ▼
Event Bus Implementation
```

Nhưng không nhất thiết phải tạo interface ngay từ đầu.

Nếu project nhỏ:

```text
EventBus
```

đơn giản là đủ.

---

# 42. Một implementation thực tế hơn

```python
from collections import defaultdict
from collections.abc import Callable


class EventBus:

    def __init__(self):
        self._handlers = defaultdict(list)

    def subscribe(
        self,
        event_type: type,
        handler: Callable,
    ):

        self._handlers[
            event_type
        ].append(handler)

        return lambda: self.unsubscribe(
            event_type,
            handler,
        )

    def unsubscribe(
        self,
        event_type: type,
        handler: Callable,
    ):

        handlers = self._handlers.get(
            event_type,
            []
        )

        try:
            handlers.remove(handler)
        except ValueError:
            pass

    def publish(self, event):

        for handler in tuple(
            self._handlers.get(
                type(event),
                ()
            )
        ):
            handler(event)
```

Tại sao:

```python
tuple(...)
```

?

Để snapshot danh sách handler trước khi iterate.

Một handler có thể unsubscribe chính nó trong lúc xử lý event.

---

# 43. Error Handling

Một vấn đề:

```python
for handler in handlers:
    handler(event)
```

Nếu:

```text
handler A → OK
handler B → exception
handler C → ?
```

Nếu không xử lý:

```text
handler B
   ↓
exception
   ↓
publish() dừng
   ↓
handler C không chạy
```

Đây có thể là behavior không mong muốn.

---

# 44. Một chiến lược

```python
def publish(self, event):

    for handler in tuple(
        self._handlers.get(type(event), ())
    ):
        try:
            handler(event)
        except Exception:
            logger.exception(
                "Event handler failed"
            )
```

Nhưng cũng không nên luôn nuốt exception.

Trong development:

```text
fail fast
```

có thể tốt hơn.

Trong production event processing:

```text
isolate handler failure
```

có thể phù hợp hơn.

Đây là quyết định architecture, không phải chỉ là syntax.

---

# 45. Event Bus có return value không?

Thông thường:

```python
bus.publish(event)
```

không nên trả:

```python
[result1, result2, result3]
```

Event Bus dùng cho **notification**.

Nếu cần:

```text
request → response
```

thì dùng:

```text
Service Call
Command
Query
```

hoặc cơ chế khác.

---

# 46. Event Bus không thay thế Service Layer

Sai:

```python
bus.publish(
    LoadStoryRequested(10)
)
```

rồi hy vọng một subscriber nào đó load story.

Có thể làm được, nhưng architecture trở nên khó theo dõi.

Nếu Controller cần lấy Story:

```python
story = service.get_story(10)
```

rõ ràng hơn.

Event Bus nên chủ yếu dùng cho:

```text
notification
integration
decoupling
```

---

# 47. Bảng phân biệt quan trọng

| Cơ chế      | Ý nghĩa                               |
| ----------- | ------------------------------------- |
| Method call | Tôi cần kết quả từ B                  |
| Signal      | A thông báo cho B                     |
| Event Bus   | A phát fact cho nhiều subscriber      |
| State       | Trạng thái hiện tại                   |
| Service     | Thực hiện use case/business operation |
| Repository  | Persistence                           |
| Command     | Yêu cầu thực hiện hành động           |

Nếu nhớ được bảng này, architecture PySide6 của bạn sẽ rõ ràng hơn rất nhiều.

---

# 48. Story Reader — Architecture hoàn chỉnh hơn

```text
                       Main
                        │
                        ▼
                Composition Root
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
    Services          State           EventBus
       │                │                │
       ▼                ▼                ▼
 Repository        ViewModels        Subscribers
       │                │                │
       ▼                ▼          ┌─────┼─────┐
    SQLite             Views       │     │     │
                                Dashboard Logger Status
```

Đây là kiến trúc chúng ta đang hướng tới.

---

# 49. Bài tập 1 — Viết Event Bus

Tự implement:

```python
class EventBus:
    ...
```

phải hỗ trợ:

```python
subscribe()
unsubscribe()
publish()
```

---

# 50. Bài tập 2 — Event

Tạo:

```python
@dataclass(frozen=True)
class StorySelected:
    story_id: int
```

và:

```python
@dataclass(frozen=True)
class ChapterSelected:
    chapter_id: int
```

Subscribe hai event độc lập.

---

# 51. Bài tập 3 — Multiple Subscribers

Một event:

```text
CrawlProgress
```

có 4 subscriber:

```text
Dashboard
ProgressBar
StatusBar
Logger
```

Khi:

```python
bus.publish(
    CrawlProgress(
        story_id=1,
        current=50,
        total=100,
    )
)
```

cả 4 phải nhận event.

---

# 52. Bài tập 4 — unsubscribe

Test:

```python
unsubscribe = bus.subscribe(
    CrawlProgress,
    handler,
)
```

Sau:

```python
unsubscribe()
```

thì:

```python
bus.publish(event)
```

handler không được gọi.

---

# 53. Bài tập 5 — Event Bus + Controller

Thiết kế:

```text
StoryController
       │
       ├── State
       │
       └── EventBus
```

Khi:

```python
controller.select_story(10)
```

phải:

```text
1. update state
2. publish StorySelected
```

---

# 54. Bài tập 6 — Event Bus vs Signal

Cho các tình huống:

```text
A. QPushButton → MainWindow
B. Worker → ProgressBar
C. Crawler → Dashboard + Logger + Notification
D. Controller → Reader
E. State → ViewModel
```

Hãy chọn:

```text
Signal
Event Bus
Method Call
```

cho từng trường hợp và giải thích.

---

# 55. Bài tập 7 — Architecture Review

Cho:

```python
class Crawler:

    def __init__(
        self,
        dashboard,
        status_bar,
        logger,
        notification,
    ):
        ...
```

Hãy refactor thành:

```text
Crawler
   │
   ▼
EventBus
   │
   ├── Dashboard
   ├── StatusBar
   ├── Logger
   └── Notification
```

---

# 56. Mini Project

Xây một:

# `PySide6 Event Bus Demo`

UI:

```text
┌─────────────────────────────────────┐
│         Event Bus Demo              │
├─────────────────────────────────────┤
│                                     │
│ [Start Crawl]                       │
│                                     │
│ Progress: ███████░░░ 70%            │
│                                     │
│ Events:                             │
│ ┌─────────────────────────────────┐ │
│ │ CrawlStarted                    │ │
│ │ CrawlProgress 10/100            │ │
│ │ CrawlProgress 20/100            │ │
│ │ CrawlProgress 30/100            │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

Architecture:

```text
MainWindow
    │
    ▼
Controller
    │
    ▼
Crawler
    │
    ▼
EventBus
    │
 ┌──┼────────────┐
 ▼  ▼            ▼
UI Logger    EventLog
```

Mục tiêu không phải làm UI đẹp.

Mục tiêu là hiểu:

```text
Publisher
Subscriber
Event
EventBus
State
Signal
```

---

# 57. Checklist sau Buổi 33

Bạn nên tự trả lời được:

* Event là gì?
* Event khác Command như thế nào?
* Event Bus giải quyết coupling nào?
* `subscribe()` hoạt động thế nào?
* Tại sao cần `unsubscribe()`?
* Tại sao event nên immutable?
* Signal và Event Bus khác nhau thế nào?
* Khi nào **không nên** dùng Event Bus?
* Event Bus có thay thế Service không?
* Event Bus có phải State không?
* Event Bus có tự giải quyết threading không?
* Vì sao nên inject Event Bus thay vì global singleton?

Nếu trả lời được những câu này thì bạn đã nắm được nền tảng của Event Bus.

---

# 58. Mental Model cuối buổi

Hãy giữ mô hình này:

```text
                 USER
                   │
                   ▼
                 VIEW
                   │
                   ▼
              CONTROLLER
              /         \
             ▼           ▼
          SERVICE       STATE
             │           │
             ▼           ▼
        REPOSITORY     SIGNAL
             │           │
             ▼           ▼
          DATABASE       UI


          CROSS-MODULE EVENTS
                   │
                   ▼
                EVENT BUS
                   │
          ┌────────┼────────┐
          ▼        ▼        ▼
       Logger   Dashboard  Notification
```

**Một quy tắc rất đáng nhớ:**

```text
Method Call
    → Tôi cần một hành động / kết quả.

Signal
    → Object này thông báo cho object kia.

State
    → Đây là trạng thái hiện tại.

Event Bus
    → Đây là một fact mà nhiều module có thể quan tâm.

Service
    → Đây là use case / business operation.
```

### Buổi tiếp theo — **Buổi 34: Signal-based Architecture**

Chúng ta sẽ đi sâu hơn vào chính cơ chế mà PySide6 cung cấp:

```text
QObject
   │
   ├── Signal
   ├── Slot
   ├── connect()
   ├── disconnect()
   ├── emit()
   └── Queued Connection
```

Sau đó chúng ta sẽ thiết kế một kiến trúc kết hợp:

```text
                 Application
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
      Application State        Event Bus
          │                       │
       Signals                 Events
          │                       │
          └───────────┬───────────┘
                      ▼
                  ViewModel
                      │
                      ▼
                     View
```

Đây sẽ là buổi rất quan trọng trước khi chuyển sang **Buổi 35 — Project Structure**.
