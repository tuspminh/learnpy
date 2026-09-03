# Python OOP Master — Buổi 37

# Command Pattern

Hôm nay chúng ta học **Command Pattern**.

Nếu Buổi 36:

> **Observer = “Có chuyện xảy ra → thông báo cho những ai quan tâm.”**

thì Command:

> **Command = “Đóng gói một hành động thành một object.”**

Đặc biệt, Command rất phù hợp với **PySide6 + Crawler Dashboard** của bạn:

```text
Button
   ↓
Command
   ↓
Application Service
   ↓
Crawler
```

Ví dụ:

```text
Start
Pause
Resume
Stop
Retry
Delete
Refresh
```

đều có thể trở thành Command.

---

# 1. Mục tiêu

Sau buổi này bạn sẽ hiểu:

* Command Pattern là gì?
* Command Object
* Receiver
* Invoker
* Client
* `execute()`
* Command + DI
* Command + PySide6
* Command Queue
* Undo / Redo
* Macro Command
* Command vs Strategy
* Command vs Factory
* Command vs Observer
* Command trong crawler
* Khi nào không nên dùng Command

---

# 2. Bài toán

Giả sử PySide6 Dashboard có:

```text
[Start]
[Pause]
[Resume]
[Stop]
[Retry]
```

Cách đơn giản:

```python
start_button.clicked.connect(
    crawler.start
)

pause_button.clicked.connect(
    crawler.pause
)

resume_button.clicked.connect(
    crawler.resume
)

stop_button.clicked.connect(
    crawler.stop
)
```

Với application nhỏ thì hoàn toàn ổn.

Nhưng khi application lớn:

```text
Button
Menu
Keyboard Shortcut
Toolbar
CLI
Context Menu
```

đều có thể thực hiện:

```text
Start
Pause
Resume
Stop
Retry
```

Logic gọi trực tiếp sẽ bắt đầu phân tán.

Command giải quyết vấn đề này.

---

# 3. Ý tưởng của Command

Thay vì:

```text
Button → crawler.pause()
```

ta có:

```text
Button
  ↓
PauseCrawlerCommand
  ↓
execute()
  ↓
crawler.pause()
```

Command đóng gói:

```text
ACTION
```

thành:

```text
OBJECT
```

---

# 4. Command cơ bản

Interface:

```python
from abc import ABC, abstractmethod


class Command(ABC):

    @abstractmethod
    def execute(self):
        pass
```

Concrete Command:

```python
class StartCrawlerCommand(Command):

    def __init__(self, crawler):
        self.crawler = crawler

    def execute(self):
        self.crawler.start()
```

Một Command khác:

```python
class PauseCrawlerCommand(Command):

    def __init__(self, crawler):
        self.crawler = crawler

    def execute(self):
        self.crawler.pause()
```

---

# 5. Receiver

Ai thực sự thực hiện hành động?

```python
class Crawler:

    def start(self):
        print("Crawler started")

    def pause(self):
        print("Crawler paused")

    def resume(self):
        print("Crawler resumed")

    def stop(self):
        print("Crawler stopped")
```

`Crawler` chính là **Receiver**.

Command không thực hiện business logic chính.

Nó chỉ biết:

```text
"Muốn Start → gọi crawler.start()"
```

---

# 6. Sử dụng

```python
crawler = Crawler()

command = StartCrawlerCommand(
    crawler
)

command.execute()
```

Output:

```text
Crawler started
```

Luồng:

```text
Client
  ↓
Command
  ↓
Receiver
```

---

# 7. Bốn thành phần của Command Pattern

Đây là phần cần nhớ.

```text
Client
   ↓
Command
   ↓
Receiver
```

và:

```text
Invoker
   ↓
Command.execute()
```

Cụ thể:

### Receiver

Object thực hiện công việc.

```text
Crawler
```

### Command

Đóng gói action.

```text
StartCrawlerCommand
PauseCrawlerCommand
```

### Invoker

Object yêu cầu Command chạy.

```text
Button
Menu
CommandQueue
```

### Client

Object cấu hình các thành phần.

```text
Application / Composition Root
```

---

# 8. Invoker

Ta tạo:

```python
class CommandInvoker:

    def execute(self, command):
        command.execute()
```

Sử dụng:

```python
invoker = CommandInvoker()

invoker.execute(
    StartCrawlerCommand(crawler)
)
```

Kiến trúc:

```text
Invoker
   ↓
Command.execute()
   ↓
Crawler
```

Invoker không cần biết crawler.

---

# 9. Tại sao phải cần Invoker?

Đây là câu hỏi quan trọng.

Nếu chỉ:

```python
command.execute()
```

thì Command Pattern có vẻ hơi thừa.

Invoker trở nên hữu ích khi chúng ta muốn:

```text
queue
history
undo
redo
logging
retry
schedule
macro
```

Ví dụ:

```text
Invoker
   ↓
Command Queue
   ↓
Command
```

---

# 10. Command Queue

Giả sử crawler có rất nhiều thao tác:

```text
Start
Pause
Resume
Retry
Stop
```

Ta có thể đưa chúng vào queue:

```python
from collections import deque


class CommandQueue:

    def __init__(self):
        self._queue = deque()

    def add(self, command):
        self._queue.append(command)

    def run_next(self):
        command = self._queue.popleft()
        command.execute()
```

---

# 11. Sử dụng Queue

```python
queue = CommandQueue()

queue.add(
    StartCrawlerCommand(crawler)
)

queue.add(
    PauseCrawlerCommand(crawler)
)
```

Sau đó:

```python
queue.run_next()
```

Output:

```text
Crawler started
```

Tiếp:

```python
queue.run_next()
```

Output:

```text
Crawler paused
```

Ta đã biến:

```text
Action
```

thành:

```text
Data + executable object
```

---

# 12. Đây là sức mạnh lớn của Command

Method bình thường:

```python
crawler.pause()
```

chạy ngay.

Command:

```python
PauseCrawlerCommand(crawler)
```

có thể:

```text
lưu lại
xếp hàng
delay
retry
log
undo
redo
serialize
schedule
```

trước khi thực thi.

Đây là lý do Command Pattern rất mạnh.

---

# 13. Command trong PySide6

Giả sử:

```text
[Start]
[Pause]
[Resume]
```

Ta có:

```python
start_command = StartCrawlerCommand(
    crawler
)

pause_command = PauseCrawlerCommand(
    crawler
)
```

Button:

```python
start_button.clicked.connect(
    start_command.execute
)

pause_button.clicked.connect(
    pause_command.execute
)
```

Kiến trúc:

```text
QPushButton
    ↓
Command
    ↓
Crawler
```

UI không cần biết chi tiết business operation.

---

# 14. Keyboard Shortcut

Một ưu điểm rất hay.

Ta có cùng một Command:

```python
pause_command
```

Button dùng:

```python
pause_button.clicked.connect(
    pause_command.execute
)
```

Shortcut cũng dùng:

```python
shortcut.activated.connect(
    pause_command.execute
)
```

Menu cũng dùng:

```python
pause_action.triggered.connect(
    pause_command.execute
)
```

Ba UI element:

```text
Button
Menu
Shortcut
```

đều dùng:

```text
PauseCrawlerCommand
```

Không duplicate logic.

---

# 15. Đây chính là Reuse Action

Không tốt:

```text
Button → crawler.pause()
Menu  → crawler.pause()
Ctrl+P → crawler.pause()
```

Tốt:

```text
Button ──┐
Menu ────┼→ PauseCommand → Crawler
Shortcut ┘
```

---

# 16. Command + Dependency Injection

Command nhận Receiver qua constructor:

```python
class PauseCrawlerCommand:

    def __init__(self, crawler):
        self.crawler = crawler

    def execute(self):
        self.crawler.pause()
```

Composition Root:

```python
crawler = Crawler()

pause_command = PauseCrawlerCommand(
    crawler
)
```

Đây chính là DI.

---

# 17. Command không nên chứa quá nhiều business logic

Không nên:

```python
class PauseCrawlerCommand:

    def execute(self):

        if crawler.running:
            crawler.status = "paused"

        for worker in crawler.workers:
            ...

        database.update(...)

        ...
```

Nếu Command trở thành nơi chứa toàn bộ business logic thì architecture sẽ xấu.

Nên:

```python
class PauseCrawlerCommand:

    def execute(self):
        self.crawler.pause()
```

Business logic nằm ở:

```text
Crawler
Application Service
Domain
```

tùy architecture.

---

# 18. Command + Application Service

Trong Clean Architecture, có thể thiết kế:

```text
PySide6
   ↓
Command
   ↓
Application Service
   ↓
Domain
```

Ví dụ:

```python
class PauseCrawlerCommand:

    def __init__(self, service):
        self.service = service

    def execute(self):
        self.service.pause_crawler()
```

Application:

```python
class CrawlerService:

    def pause_crawler(self):
        ...
```

Kiến trúc:

```text
UI
 ↓
Command
 ↓
Application
 ↓
Domain
```

Đây là hướng rất phù hợp với hệ thống crawler của bạn.

---

# 19. Command + CQRS

Bạn đã học CQRS.

Command Pattern rất dễ kết hợp với CQRS.

Ví dụ:

```text
Command
├── StartCrawler
├── PauseCrawler
├── ResumeCrawler
├── StopCrawler
└── RetryChapter
```

Trong khi Query:

```text
Query
├── GetCrawlerStatus
├── GetProgress
├── GetChapterList
└── GetErrorList
```

Có thể hình dung:

```text
                 Application
                     │
             ┌───────┴────────┐
             ↓                ↓
         Commands           Queries
             ↓                ↓
        Modify State       Read State
```

Command = thay đổi state.

Query = đọc state.

---

# 20. Command Object chứa dữ liệu

Command không chỉ có method.

Nó có thể chứa data.

Ví dụ:

```python
class RetryChapterCommand:

    def __init__(
        self,
        chapter_id,
        max_attempts=3,
    ):
        self.chapter_id = chapter_id
        self.max_attempts = max_attempts

    def execute(self, service):
        return service.retry_chapter(
            self.chapter_id,
            self.max_attempts,
        )
```

Object:

```text
RetryChapterCommand
├── chapter_id
├── max_attempts
└── execute()
```

---

# 21. Command như một Message

Đây là tư duy rất quan trọng.

Command:

```python
RetryChapterCommand(
    chapter_id=100,
    max_attempts=3,
)
```

có thể được xem như:

```text
MESSAGE
```

gửi tới application.

```text
UI
 ↓
Command Message
 ↓
Application
 ↓
Handler
```

Đây là bước tiến gần tới:

```text
Message Queue
Task Queue
RQ
Celery
Dramatiq
```

những thứ bạn cũng đang học.

---

# 22. Command Handler

Thay vì:

```python
command.execute()
```

ta có:

```python
class RetryChapterHandler:

    def __init__(self, crawler_service):
        self.service = crawler_service

    def handle(self, command):
        return self.service.retry_chapter(
            command.chapter_id
        )
```

Command:

```python
class RetryChapterCommand:

    def __init__(self, chapter_id):
        self.chapter_id = chapter_id
```

Handler:

```text
Command
   ↓
Handler
   ↓
Application Service
```

Đây là kiến trúc thường thấy trong hệ thống lớn.

---

# 23. Command có thể được Queue

Ví dụ:

```text
RetryChapterCommand(10)
RetryChapterCommand(11)
RetryChapterCommand(12)
```

Queue:

```text
┌───────────────────────────────┐
│ Command Queue                 │
├───────────────────────────────┤
│ RetryChapterCommand(10)       │
│ RetryChapterCommand(11)       │
│ RetryChapterCommand(12)       │
└───────────────────────────────┘
```

Worker:

```text
Queue
 ↓
Worker
 ↓
Handler
 ↓
Application
```

Đây chính là cầu nối từ OOP Pattern sang distributed/task architecture.

---

# 24. Undo

Một ứng dụng rất nổi tiếng của Command là:

> **Undo / Redo**

Ví dụ:

```text
Insert
Delete
Update
```

Command có:

```python
class Command(ABC):

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass
```

Ví dụ:

```python
class AddStoryCommand(Command):

    def __init__(self, repository, story):
        self.repository = repository
        self.story = story

    def execute(self):
        self.repository.add(self.story)

    def undo(self):
        self.repository.delete(
            self.story.id
        )
```

---

# 25. Command History

```python
class CommandHistory:

    def __init__(self):
        self._history = []

    def execute(self, command):
        command.execute()
        self._history.append(command)

    def undo(self):
        command = self._history.pop()
        command.undo()
```

Sử dụng:

```python
history.execute(
    AddStoryCommand(
        repository,
        story,
    )
)
```

Undo:

```python
history.undo()
```

---

# 26. Redo

Redo thường cần hai stack:

```text
undo_stack
redo_stack
```

Sau khi execute:

```text
undo_stack
   ↑
Command
```

Undo:

```text
undo_stack
    ↓
redo_stack
```

Redo:

```text
redo_stack
    ↓
undo_stack
```

Mô hình:

```text
          execute
             ↓
        ┌─────────┐
        │   Undo  │
        └────┬────┘
             │ undo
             ↓
        ┌─────────┐
        │   Redo  │
        └─────────┘
```

---

# 27. Macro Command

Một Command có thể chứa nhiều Command.

```python
class MacroCommand:

    def __init__(self, commands):
        self.commands = commands

    def execute(self):

        for command in self.commands:
            command.execute()
```

Ví dụ:

```python
macro = MacroCommand([
    StartCrawlerCommand(crawler),
    RefreshDashboardCommand(dashboard),
])
```

Sau đó:

```python
macro.execute()
```

Thực hiện nhiều action.

---

# 28. Composite Command

Đây là một ứng dụng rất đẹp:

```text
MacroCommand
├── Command A
├── Command B
└── Command C
```

Macro cũng là Command:

```python
class MacroCommand(Command):

    def execute(self):
        ...
```

Vì vậy có thể:

```text
Command
  ↑
MacroCommand
```

Đây là cách áp dụng tư duy **Composite**.

---

# 29. Command vs Strategy

Hai Pattern này rất dễ nhầm.

### Strategy

Đóng gói:

```text
ALGORITHM
```

Ví dụ:

```text
RetryStrategy
├── Fixed
└── Exponential
```

### Command

Đóng gói:

```text
ACTION / REQUEST
```

Ví dụ:

```text
CrawlerCommand
├── Start
├── Pause
├── Resume
└── Stop
```

Nhớ:

```text
Strategy → HOW?
Command  → DO WHAT?
```

---

# 30. Command vs Factory

Factory:

```text
"Tạo object nào?"
```

Command:

```text
"Thực hiện action nào?"
```

Có thể kết hợp:

```text
CommandFactory
      ↓
PauseCrawlerCommand
```

---

# 31. Command vs Observer

Observer:

```text
Event xảy ra
    ↓
Thông báo
    ↓
Observers
```

Command:

```text
User yêu cầu action
    ↓
Command
    ↓
execute()
```

Ví dụ:

```text
User click Pause
       ↓
PauseCommand
       ↓
Crawler.pause()
```

Sau đó:

```text
Crawler
   ↓
CrawlerPaused Event
   ↓
Observer
   ├── Dashboard
   └── Logger
```

**Command và Observer có thể kết hợp rất đẹp.**

---

# 32. Command + Observer

Đây là architecture rất đáng chú ý:

```text
                    User
                     │
                     ↓
                  Command
                     │
                  execute()
                     │
                     ↓
                  Crawler
                     │
                  emit Event
                     │
          ┌──────────┼──────────┐
          ↓          ↓          ↓
      Dashboard    Logger     Metrics
```

Command:

```text
User → Action
```

Observer:

```text
System → Notification
```

Hai hướng ngược nhau.

---

# 33. Crawler Dashboard hoàn chỉnh

Ta có:

```text
                 PySide6 UI
                     │
          ┌──────────┼──────────┐
          ↓          ↓          ↓
        Button      Menu     Shortcut
          │          │          │
          └──────────┼──────────┘
                     ↓
                 Command
                     │
                     ↓
              Application
                     │
                     ↓
                  Crawler
                     │
                  Event
                     │
       ┌─────────────┼─────────────┐
       ↓             ↓             ↓
   Dashboard       Logger        Metrics
```

Đây là architecture cực kỳ mạnh.

---

# 34. Ví dụ đầy đủ

Receiver:

```python
class Crawler:

    def start(self):
        print("START")

    def pause(self):
        print("PAUSE")

    def resume(self):
        print("RESUME")

    def stop(self):
        print("STOP")
```

Command:

```python
class StartCommand:

    def __init__(self, crawler):
        self.crawler = crawler

    def execute(self):
        self.crawler.start()
```

```python
class PauseCommand:

    def __init__(self, crawler):
        self.crawler = crawler

    def execute(self):
        self.crawler.pause()
```

```python
class ResumeCommand:

    def __init__(self, crawler):
        self.crawler = crawler

    def execute(self):
        self.crawler.resume()
```

```python
class StopCommand:

    def __init__(self, crawler):
        self.crawler = crawler

    def execute(self):
        self.crawler.stop()
```

---

# 35. Command Registry

Có thể lưu:

```python
commands = {
    "start": StartCommand(crawler),
    "pause": PauseCommand(crawler),
    "resume": ResumeCommand(crawler),
    "stop": StopCommand(crawler),
}
```

CLI:

```python
commands["pause"].execute()
```

UI:

```python
pause_button.clicked.connect(
    commands["pause"].execute
)
```

Shortcut:

```python
shortcut.activated.connect(
    commands["pause"].execute
)
```

Một Command được sử dụng ở nhiều interface.

---

# 36. Điều này rất phù hợp với CLI + GUI

Project crawler của bạn có thể có:

```text
CLI
GUI
REST API
Worker
```

Tất cả có thể gửi cùng Command:

```text
             ┌── CLI
             │
             ├── GUI
             │
             └── API
                  │
                  ↓
              Command
                  ↓
             Application
```

Ví dụ:

```text
PauseCrawlerCommand
```

không quan tâm request đến từ:

```text
PySide6
CLI
HTTP API
```

---

# 37. Command và Queue Worker

Vì bạn đã học RQ/Redis, hãy nhìn architecture:

```text
PySide6
   ↓
Command
   ↓
Queue
   ↓
Worker
   ↓
Handler
   ↓
Application
```

Ví dụ:

```text
RetryChapterCommand(123)
```

được đưa vào queue.

Worker lấy:

```text
RetryChapterCommand(123)
```

rồi:

```text
Handler
   ↓
retry_chapter(123)
```

Đây chính là một bước từ **Design Pattern → Task Queue Architecture**.

---

# 38. Một lưu ý quan trọng

Không phải lúc nào cũng cần Command Object.

Nếu bạn chỉ có:

```python
button.clicked.connect(
    service.refresh
)
```

thì rất đơn giản và tốt.

Đừng biến thành:

```text
RefreshCommand
RefreshHandler
CommandBus
CommandFactory
CommandRegistry
CommandInvoker
```

chỉ để gọi:

```python
service.refresh()
```

Command đáng dùng khi bạn cần:

```text
queue
history
undo
redo
logging
scheduling
retry
macro
decoupling
multiple invocation sources
```

---

# 39. Testing Command

Command rất dễ test.

Fake Receiver:

```python
class FakeCrawler:

    def __init__(self):
        self.started = False

    def start(self):
        self.started = True
```

Test:

```python
crawler = FakeCrawler()

command = StartCommand(
    crawler
)

command.execute()

assert crawler.started is True
```

Không cần PySide6.

Không cần GUI.

Không cần network.

---

# 40. Bài tập 1 — Basic Command

Tạo:

```text
Command
├── StartCrawlerCommand
├── PauseCrawlerCommand
├── ResumeCrawlerCommand
└── StopCrawlerCommand
```

Receiver:

```text
Crawler
```

Invoker:

```text
CommandInvoker
```

Yêu cầu:

```python
invoker.execute(
    PauseCrawlerCommand(crawler)
)
```

---

# 41. Bài tập 2 — Command Queue

Tạo:

```python
CommandQueue
```

API:

```python
add(command)
run_next()
run_all()
```

Test:

```python
queue.add(command1)
queue.add(command2)
queue.add(command3)

queue.run_all()
```

---

# 42. Bài tập 3 — Undo/Redo ⭐

Tạo:

```text
Command
├── execute()
└── undo()
```

Implement:

```text
AddStoryCommand
DeleteStoryCommand
UpdateStoryCommand
```

Sau đó:

```text
CommandHistory
├── execute()
├── undo()
└── redo()
```

---

# 43. Bài tập 4 — PySide6 ⭐⭐

Thiết kế:

```text
Crawler Dashboard
```

với:

```text
[Start] [Pause] [Resume] [Stop]
```

Mỗi button sử dụng Command.

Yêu cầu:

```text
Button
   ↓
Command
   ↓
Application Service
   ↓
Crawler
```

Không cho Button gọi trực tiếp:

```python
crawler.pause()
```

---

# 44. Bài tập 5 — Tổng hợp ⭐⭐⭐

Kết hợp:

```text
Factory
Builder
Strategy
Observer
Command
DI
```

Architecture:

```text
                         CLI / PySide6
                               │
                               ↓
                            Command
                               │
                               ↓
                        Application Service
                               │
                ┌──────────────┼──────────────┐
                ↓              ↓              ↓
             Parser         Retry          Storage
             Strategy       Strategy       Strategy
                │              │              │
                └──────────────┼──────────────┘
                               ↓
                            Crawler
                               │
                             Event
                               │
                ┌──────────────┼──────────────┐
                ↓              ↓              ↓
            Dashboard        Logger         Metrics
```

Factory:

```text
ParserFactory
RetryStrategyFactory
```

Builder:

```text
CrawlerConfigBuilder
```

Command:

```text
StartCrawlerCommand
PauseCrawlerCommand
ResumeCrawlerCommand
StopCrawlerCommand
RetryChapterCommand
```

Observer:

```text
CrawlStarted
ChapterCompleted
ChapterFailed
CrawlFinished
```

Đây chính là bài tập tổng hợp rất mạnh.

---

# 45. Tư duy quan trọng nhất của Buổi 37

Hãy phân biệt:

```text
Strategy
    ↓
Đóng gói ALGORITHM

Command
    ↓
Đóng gói ACTION

Observer
    ↓
Đóng gói NOTIFICATION
```

Ví dụ crawler:

```text
Strategy
→ ExponentialBackoff

Command
→ PauseCrawlerCommand

Observer
→ DashboardObserver
```

---

# 46. Năm Pattern đã học

| Buổi   | Pattern     | Câu hỏi                   |
| ------ | ----------- | ------------------------- |
| 32     | Singleton   | Có bao nhiêu instance?    |
| 33     | Factory     | Tạo object nào?           |
| 34     | Builder     | Xây object thế nào?       |
| 35     | Strategy    | Dùng algorithm nào?       |
| 36     | Observer    | Ai cần biết event?        |
| **37** | **Command** | **Thực hiện action nào?** |

Có thể nhớ thành:

```text
Singleton → Instance
Factory   → Creation
Builder   → Construction
Strategy  → Behavior
Observer  → Notification
Command   → Action
```

---

# 47. Tổng kết

**Command Pattern** biến:

```python
crawler.pause()
```

thành:

```python
PauseCrawlerCommand(
    crawler
)
```

Sau đó:

```python
command.execute()
```

Điều này cho phép action trở thành một **object có thể quản lý được**:

```text
Command
   ↓
queue
history
undo
redo
retry
schedule
macro
worker
```

Và với crawler dashboard, architecture rất đẹp sẽ là:

```text
User
 ↓
PySide6
 ↓
Command
 ↓
Application Service
 ↓
Crawler
 ↓
Event
 ↓
Observer
 ↓
Dashboard / Logger / Metrics
```

Đây là một trong những kiến trúc quan trọng nhất cần nắm trước khi bước sang các hệ thống **Command Bus, Event Bus, Queue Worker và CQRS**.
