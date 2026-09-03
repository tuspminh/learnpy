# Python OOP Master — Buổi 36

# Observer Pattern

Hôm nay chúng ta học **Observer Pattern** — một Pattern đặc biệt quan trọng đối với những gì bạn đang học về **Event-Driven Architecture và PySide6**.

Nếu Strategy trả lời:

> “Behavior nào sẽ được sử dụng?”

thì Observer trả lời:

> **“Khi một object thay đổi, làm thế nào để những object khác biết và phản ứng?”**

Đây chính là nền tảng tư duy phía sau:

```text
Event
Signal / Slot
Callback
Pub/Sub
GUI notification
Crawler progress
Logging
Monitoring
```

---

# 1. Mục tiêu

Sau buổi này bạn sẽ hiểu:

* Observer Pattern là gì?
* Subject và Observer
* `attach()`, `detach()`, `notify()`
* Loose Coupling
* Push vs Pull
* Observer với ABC
* Observer với callback/function
* Observer với `Protocol`
* Event-driven architecture
* Observer trong Crawler
* Observer trong PySide6
* Observer vs Pub/Sub
* Observer vs Mediator
* Memory leak và unsubscribe
* Thread-safety
* Async Observer
* Testing Observer

---

# 2. Bài toán

Giả sử crawler đang chạy:

```text
Crawler
   ↓
download chapter 1
   ↓
download chapter 2
   ↓
download chapter 3
```

Chúng ta muốn:

```text
Crawler
   ├── Dashboard
   ├── Logger
   ├── ProgressBar
   ├── Notification
   └── Metrics
```

Mỗi khi crawler tải xong một chapter:

```text
Crawler
   ↓
"Chapter 10 completed"
```

thì tất cả những thành phần quan tâm đều nhận được thông báo.

---

# 3. Cách làm không tốt

Ta có thể viết:

```python
class Crawler:

    def crawl(self):

        ...

        self.dashboard.update()

        self.logger.info(
            "Chapter completed"
        )

        self.progress_bar.setValue(50)

        self.notification.send(...)
```

Vấn đề là Crawler biết quá nhiều thứ.

```text
Crawler
 ├── Dashboard
 ├── Logger
 ├── ProgressBar
 └── Notification
```

Coupling rất cao.

Nếu bỏ Dashboard thì phải sửa Crawler.

Nếu thêm Telegram notification thì lại sửa Crawler.

---

# 4. Observer giải quyết thế nào?

Ta tạo:

```text
Subject
   │
   ├── Observer A
   ├── Observer B
   └── Observer C
```

Subject chỉ biết:

```text
Observer
```

không biết implementation cụ thể.

---

# 5. Mô hình Observer

Có hai thành phần chính.

## Subject

Object phát ra thông báo.

```text
Crawler
```

## Observer

Object nhận thông báo.

```text
Dashboard
Logger
Notification
```

Kiến trúc:

```text
                    Subject
                   /   |   \
                  /    |    \
                 ↓     ↓     ↓
           Observer Observer Observer
```

---

# 6. Ví dụ cơ bản

Ta định nghĩa Observer:

```python
from abc import ABC, abstractmethod


class Observer(ABC):

    @abstractmethod
    def update(self, event):
        pass
```

Concrete Observer:

```python
class Logger(Observer):

    def update(self, event):
        print(
            f"[LOG] {event}"
        )
```

Một Observer khác:

```python
class Dashboard(Observer):

    def update(self, event):
        print(
            f"[DASHBOARD] {event}"
        )
```

---

# 7. Subject

```python
class Subject:

    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self, event):

        for observer in self._observers:
            observer.update(event)
```

Đây là phần cốt lõi của Observer Pattern.

---

# 8. Sử dụng

```python
subject = Subject()

logger = Logger()
dashboard = Dashboard()

subject.attach(logger)
subject.attach(dashboard)

subject.notify(
    "Chapter 1 completed"
)
```

Output:

```text
[LOG] Chapter 1 completed
[DASHBOARD] Chapter 1 completed
```

Subject không cần biết:

```text
Logger
Dashboard
```

chỉ cần biết chúng là Observer.

---

# 9. `attach()`

Đăng ký Observer:

```python
subject.attach(logger)
```

Từ thời điểm này:

```text
Subject
   ↓
Logger
```

sẽ nhận notification.

---

# 10. `detach()`

Hủy đăng ký:

```python
subject.detach(logger)
```

Sau đó:

```python
subject.notify(...)
```

Logger không còn nhận event.

Đây là một phần **rất quan trọng** trong hệ thống event.

---

# 11. `notify()`

```python
def notify(self, event):

    for observer in self._observers:
        observer.update(event)
```

Subject gửi event cho toàn bộ Observer.

```text
Event
 ↓
Observer 1
 ↓
Observer 2
 ↓
Observer 3
```

---

# 12. Push Model

Trong ví dụ trên:

```python
observer.update(event)
```

Subject **push dữ liệu** vào Observer.

Ví dụ:

```python
event = {
    "type": "chapter_completed",
    "chapter_id": 10,
    "title": "Chapter 10",
}
```

Observer nhận trực tiếp event.

```text
Subject
   │
   │ event
   ↓
Observer
```

Đây gọi là **Push Model**.

---

# 13. Pull Model

Một cách khác:

```python
observer.update(subject)
```

Observer nhận Subject rồi tự lấy dữ liệu:

```python
class Dashboard:

    def update(self, subject):
        print(subject.progress)
```

Kiến trúc:

```text
Subject
   ↓
Observer
   ↓
pull data
   ↓
Subject
```

Đây gọi là **Pull Model**.

Trong Python application hiện đại, Push Model thường đơn giản hơn nếu event đã chứa đủ dữ liệu cần thiết.

---

# 14. Event Object

Thay vì truyền string:

```python
subject.notify(
    "chapter completed"
)
```

nên tạo event rõ ràng.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ChapterCompleted:
    chapter_id: int
    title: str
```

Notify:

```python
subject.notify(
    ChapterCompleted(
        chapter_id=10,
        title="Chapter 10",
    )
)
```

Đây là thiết kế tốt hơn.

---

# 15. Crawler Observer

Bây giờ áp dụng vào crawler.

```text
Crawler
   │
   │ event
   ├─────────────┐
   ↓             ↓
Logger       Dashboard
```

Event:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ChapterCompleted:
    chapter_id: int
    title: str
```

Observer:

```python
class CrawlerObserver(ABC):

    @abstractmethod
    def update(self, event):
        pass
```

---

# 16. Crawler Subject

```python
class Crawler:

    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self, event):

        for observer in self._observers:
            observer.update(event)
```

Khi crawl:

```python
class Crawler:

    ...

    def chapter_completed(
        self,
        chapter_id,
        title,
    ):

        event = ChapterCompleted(
            chapter_id=chapter_id,
            title=title,
        )

        self.notify(event)
```

---

# 17. Logger Observer

```python
class CrawlerLogger:

    def update(self, event):

        if isinstance(
            event,
            ChapterCompleted,
        ):
            print(
                f"Completed: {event.title}"
            )
```

Dashboard:

```python
class CrawlerDashboard:

    def update(self, event):

        if isinstance(
            event,
            ChapterCompleted,
        ):
            print(
                f"Progress: {event.chapter_id}"
            )
```

---

# 18. Kiến trúc lúc này

```text
                         Crawler
                            │
                       notify(event)
                            │
             ┌──────────────┼──────────────┐
             ↓              ↓              ↓
          Logger        Dashboard       Metrics
```

Crawler không biết:

```text
Logger
Dashboard
Metrics
```

Đây là **Loose Coupling**.

---

# 19. Đây chính là Event-Driven Architecture

Ta có:

```text
Crawler
   │
   │ emits
   ↓
Event
   │
   ├── Logger
   ├── Dashboard
   ├── Metrics
   └── Notification
```

Crawler không gọi trực tiếp:

```python
dashboard.update()
```

mà:

```python
self.notify(event)
```

Đây là chuyển từ:

```text
Direct Call
```

sang:

```text
Event
```

---

# 20. Pythonic Observer bằng callback

Python không bắt buộc phải tạo class Observer.

Ta có thể dùng function.

```python
class EventEmitter:

    def __init__(self):
        self._listeners = []

    def subscribe(self, callback):
        self._listeners.append(callback)

    def unsubscribe(self, callback):
        self._listeners.remove(callback)

    def emit(self, event):

        for callback in self._listeners:
            callback(event)
```

Sử dụng:

```python
def on_chapter_completed(event):
    print(
        f"Chapter: {event.title}"
    )
```

Đăng ký:

```python
emitter.subscribe(
    on_chapter_completed
)
```

Phát event:

```python
emitter.emit(
    ChapterCompleted(
        chapter_id=1,
        title="Chapter 1",
    )
)
```

Đây là cách rất Pythonic.

---

# 21. Callback có một ưu điểm lớn

Observer truyền thống:

```text
Observer interface
       ↓
Concrete Observer
```

Callback:

```text
Event
 ↓
function
```

Ít code hơn rất nhiều.

Nếu behavior đơn giản, callback thường là lựa chọn tốt.

---

# 22. Observer bằng Protocol

Nếu muốn type-safe:

```python
from typing import Protocol


class Observer(Protocol):

    def update(self, event) -> None:
        ...
```

Bất kỳ object nào có:

```python
update(event)
```

đều phù hợp.

Không cần:

```python
class MyObserver(Observer)
```

---

# 23. Observer trong PySide6

Đây là phần cực kỳ quan trọng với bạn.

PySide6 đã có cơ chế tương tự Observer:

```text
Signal
   ↓
Slot
```

Ví dụ:

```python
from PySide6.QtCore import QObject, Signal


class Worker(QObject):

    progress_changed = Signal(int)

    def work(self):

        for i in range(101):
            self.progress_changed.emit(i)
```

UI:

```python
worker.progress_changed.connect(
    progress_bar.setValue
)
```

Kiến trúc:

```text
Worker
  │
  │ Signal
  ↓
QProgressBar
```

Đây chính là tư duy Observer/Event-driven.

---

# 24. PySide6 Signal ≈ Observer

Có thể hình dung:

```text
Classic Observer

Subject
  ↓
notify()
  ↓
Observer.update()
```

PySide6:

```text
QObject
  ↓
signal.emit()
  ↓
slot()
```

Concept tương tự:

```text
Publisher
     ↓
Notification
     ↓
Subscriber
```

Nhưng Qt Signal/Slot là một hệ thống hoàn thiện hơn, có nhiều cơ chế riêng của Qt.

---

# 25. Crawler + PySide6

Đây là kiến trúc rất phù hợp project của bạn:

```text
                 Crawler Worker
                       │
                       │ Signal/Event
                       ↓
                Crawler Event
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
      Dashboard      Logger      Metrics
          │
          ↓
      ProgressBar
```

Ví dụ event:

```python
@dataclass(frozen=True)
class CrawlProgress:
    completed: int
    total: int
```

Worker phát:

```python
self.progress.emit(
    CrawlProgress(
        completed=10,
        total=100,
    )
)
```

UI nhận:

```python
def on_progress(event):
    value = (
        event.completed
        / event.total
        * 100
    )

    progress_bar.setValue(
        int(value)
    )
```

---

# 26. Observer giúp Crawler không phụ thuộc UI

Đây là điểm cực kỳ quan trọng.

**Không nên:**

```text
Crawler
   ↓
PySide6
```

Crawler core không nên biết:

```python
QProgressBar
QLabel
QMainWindow
Signal
```

Thay vào đó:

```text
Crawler
   ↓
Event
   ↓
Application/UI
```

Nhờ vậy bạn có thể chạy crawler từ:

```text
CLI
GUI
API
Test
Worker
```

mà không thay đổi domain logic.

---

# 27. Architecture tốt

```text
                ┌─────────────┐
                │   Crawler   │
                └──────┬──────┘
                       │
                    Event
                       │
             ┌─────────┴─────────┐
             ↓                   ↓
       Application            Adapter
             ↓                   ↓
          Logger              PySide6
                                 ↓
                              Signal
                                 ↓
                                  UI
```

Đây là một architecture tốt hơn rất nhiều so với:

```text
Crawler → QProgressBar
```

---

# 28. Observer và Clean Architecture

Trong Clean Architecture:

```text
Domain
   ↓
Application
   ↓
Infrastructure/UI
```

Domain/Application có thể phát event:

```text
Crawler
 ↓
CrawlerEvent
```

UI:

```text
CrawlerEvent
 ↓
PySide6 Adapter
 ↓
Signal
 ↓
Widget
```

UI không nên bị nhúng vào domain.

---

# 29. Một hệ thống Event hoàn chỉnh

Ta có thể tạo:

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

    def publish(self, event):

        event_type = type(event)

        for handler in self._handlers.get(
            event_type,
            [],
        ):
            handler(event)
```

Đăng ký:

```python
bus.subscribe(
    ChapterCompleted,
    logger.handle,
)
```

và:

```python
bus.subscribe(
    ChapterCompleted,
    dashboard.handle,
)
```

Publish:

```python
bus.publish(
    ChapterCompleted(
        chapter_id=10,
        title="Chapter 10",
    )
)
```

Đây bắt đầu chuyển từ **Observer Pattern** sang kiến trúc **Event Bus / Pub-Sub**.

---

# 30. Observer vs Event Bus

Đừng nhầm hai khái niệm.

### Observer

Subject biết danh sách Observer:

```text
Subject
 ├── Observer A
 ├── Observer B
 └── Observer C
```

### Event Bus

Publisher thường không cần biết subscriber cụ thể:

```text
Publisher
    ↓
 EventBus
    ↓
 ├── Handler A
 ├── Handler B
 └── Handler C
```

Event Bus làm trung gian.

---

# 31. Observer vs Pub/Sub

### Observer

Thường:

```text
Subject → Observers
```

Có quan hệ trực tiếp.

### Pub/Sub

Thường:

```text
Publisher
     ↓
 Message Broker
     ↓
Subscribers
```

Publisher không cần biết subscriber.

Ví dụ lớn hơn:

```text
Crawler
 ↓
Redis
 ↓
Worker
Dashboard
Logger
```

Đây là tư duy Pub/Sub.

---

# 32. Observer vs Mediator

### Observer

Một Subject thông báo cho nhiều Observer:

```text
Subject
 ├── A
 ├── B
 └── C
```

### Mediator

Nhiều object giao tiếp thông qua một mediator:

```text
A ─┐
B ─┼→ Mediator ←─ C
D ─┘
```

Mediator quản lý interaction giữa nhiều component.

---

# 33. Vấn đề quan trọng: Memory Leak

Hãy chú ý:

```python
subject.attach(observer)
```

Subject giữ reference đến:

```text
observer
```

Nếu Observer đáng lẽ phải được giải phóng nhưng vẫn đăng ký:

```text
Subject
  │
  └────→ Observer
```

Observer có thể không được garbage collector giải phóng như mong muốn.

Vì vậy cần:

```python
subject.detach(observer)
```

hoặc cơ chế lifecycle phù hợp.

---

# 34. Một lỗi thường gặp

Không nên:

```python
class Subject:

    def attach(self, observer):
        self._observers.append(observer)

    def attach(self, observer):
        self._observers.append(observer)
```

có thể khiến cùng một Observer được đăng ký nhiều lần.

Nên cân nhắc:

```python
class Subject:

    def attach(self, observer):

        if observer not in self._observers:
            self._observers.append(observer)
```

---

# 35. Thread Safety

Nếu crawler chạy bằng:

```text
ThreadPoolExecutor
```

và nhiều thread cùng:

```python
notify(event)
```

thì Observer collection có thể cần synchronization.

Ví dụ:

```python
from threading import Lock


class Subject:

    def __init__(self):
        self._observers = []
        self._lock = Lock()
```

Khi attach/detach:

```python
with self._lock:
    ...
```

Nhưng cần thiết kế kỹ hơn nếu notification xảy ra đồng thời.

Đặc biệt:

> **Không nên tùy tiện cập nhật PySide6 UI từ worker thread.**

GUI update phải đi qua cơ chế signal/slot phù hợp của Qt.

---

# 36. Observer và Asyncio

Trong async application:

```text
Async Crawler
      ↓
   Event
      ↓
Async Observer
```

Ví dụ:

```python
class AsyncObserver(Protocol):

    async def update(self, event):
        ...
```

Subject:

```python
class AsyncSubject:

    async def notify(self, event):

        for observer in self._observers:
            await observer.update(event)
```

Nhưng trong production cần quyết định:

```text
Sequential?
Concurrent?
Exception isolation?
Cancellation?
Backpressure?
```

Không nên đơn giản hóa thành `await` mọi Observer nếu Observer có thể chậm.

---

# 37. Exception trong Observer

Một vấn đề khác:

```python
for observer in self._observers:
    observer.update(event)
```

Nếu:

```text
Observer A → OK
Observer B → Exception
Observer C → không chạy
```

Có thể không mong muốn.

Một thiết kế:

```python
for observer in self._observers:

    try:
        observer.update(event)

    except Exception:
        logger.exception(
            "Observer failed"
        )
```

Như vậy một Observer lỗi không làm toàn bộ notification pipeline chết.

---

# 38. Testing Observer

Test rất đơn giản.

```python
class FakeObserver:

    def __init__(self):
        self.events = []

    def update(self, event):
        self.events.append(event)
```

Test:

```python
subject = Subject()

observer = FakeObserver()

subject.attach(observer)

event = "hello"

subject.notify(event)

assert observer.events == [
    "hello"
]
```

Test detach:

```python
subject.detach(observer)

subject.notify("world")

assert observer.events == [
    "hello"
]
```

---

# 39. Observer và SOLID

Observer hỗ trợ rất tốt:

### SRP

Subject:

```text
quản lý event
```

Observer:

```text
xử lý event
```

### OCP

Thêm:

```python
class TelegramNotifier:
    ...
```

không cần sửa Crawler.

### DIP

Crawler phụ thuộc event abstraction thay vì UI cụ thể.

### ISP

Observer interface nhỏ:

```python
update(event)
```

---

# 40. Một thiết kế tốt cho Story Crawler

Tôi khuyên bạn có thể tiến tới:

```text
domain/
    events/
        chapter_completed.py
        chapter_failed.py
        crawl_started.py
        crawl_finished.py

application/
    crawler_service.py

infrastructure/
    crawler/
    repository/

presentation/
    pyside6/
        dashboard.py
        adapters/
```

Events:

```text
CrawlStarted
ChapterDownloaded
ChapterSaved
ChapterFailed
CrawlPaused
CrawlResumed
CrawlFinished
```

Dashboard chỉ subscribe những event nó cần.

---

# 41. Ví dụ Event Model

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class CrawlStarted:
    story_id: int


@dataclass(frozen=True)
class ChapterCompleted:
    chapter_id: int
    title: str


@dataclass(frozen=True)
class ChapterFailed:
    chapter_id: int
    error: str


@dataclass(frozen=True)
class CrawlFinished:
    story_id: int
```

Sau đó:

```text
Crawler
  │
  ├── CrawlStarted
  ├── ChapterCompleted
  ├── ChapterFailed
  └── CrawlFinished
```

---

# 42. Dashboard không cần biết Crawler

Dashboard chỉ cần:

```python
def on_chapter_completed(event):
    ...
```

Logger:

```python
def on_chapter_completed(event):
    ...
```

Metrics:

```python
def on_chapter_completed(event):
    ...
```

Notification:

```python
def on_chapter_completed(event):
    ...
```

Tất cả độc lập.

---

# 43. Đây là tư duy quan trọng nhất của Observer

Không nghĩ:

```text
Crawler phải gọi Dashboard.
```

Hãy nghĩ:

```text
Crawler phát ra sự kiện.
```

Sau đó:

```text
Ai quan tâm thì subscribe.
```

Đây là một thay đổi rất lớn trong tư duy architecture:

```text
Imperative coupling
        ↓
Event-driven coupling
```

---

# 44. Khi nào KHÔNG nên dùng Observer?

Không phải lúc nào Observer cũng tốt.

Nếu chỉ có:

```python
result = service.execute()
```

và cần gọi:

```python
logger.log(result)
```

thì gọi trực tiếp có thể đơn giản hơn.

Observer phù hợp khi:

```text
Một event
   ↓
nhiều consumer
```

và các consumer có lifecycle/behavior tương đối độc lập.

---

# 45. Observer Pattern — bản chất

Hãy nhớ mô hình:

```text
                 SUBJECT
                    │
                  notify
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
    Observer     Observer     Observer
        │           │           │
      Logger     Dashboard    Metrics
```

Trong Python:

```python
subject.attach(observer)
subject.detach(observer)
subject.notify(event)
```

Ba method này chính là bộ khung cơ bản.

---

# 46. So sánh 4 Pattern đã học

| Pattern      | Câu hỏi                          |
| ------------ | -------------------------------- |
| Singleton    | Có bao nhiêu instance?           |
| Factory      | Tạo object nào?                  |
| Builder      | Xây object như thế nào?          |
| Strategy     | Dùng algorithm nào?              |
| **Observer** | **Ai cần biết khi có thay đổi?** |

Rất đáng nhớ:

```text
Singleton → Instance
Factory   → Creation
Builder   → Construction
Strategy  → Behavior
Observer  → Notification
```

---

# 47. Bài tập

### Bài 1 — Basic Observer

Tạo:

```text
NewsAgency
    ↓
NewsSubscriber
```

Có:

```text
EmailSubscriber
SMSSubscriber
DashboardSubscriber
```

Khi:

```python
agency.publish("Python 3.15 released")
```

tất cả Subscriber nhận được tin.

---

### Bài 2 — Callback Observer

Không dùng class Observer.

Tạo:

```python
EventEmitter
```

API:

```python
subscribe()
unsubscribe()
emit()
```

---

### Bài 3 — Crawler Event

Tạo:

```text
CrawlStarted
ChapterCompleted
ChapterFailed
CrawlFinished
```

Crawler phát event.

Tạo:

```text
Logger
Metrics
Dashboard
```

làm Observer.

---

### Bài 4 — ⭐ PySide6

Thiết kế:

```text
CrawlerWorker
      ↓
   Signal
      ↓
CrawlerEvent
      ↓
Dashboard
      ↓
QProgressBar
```

Yêu cầu:

* Worker không truy cập trực tiếp Widget.
* Dashboard không điều khiển crawler internals.
* Event chứa dữ liệu cần thiết.
* UI chỉ phản ứng với event.

---

### Bài 5 — ⭐⭐⭐ Architecture

Thiết kế:

```text
                    Crawler
                       │
                       ↓
                 EventDispatcher
                       │
       ┌───────────────┼───────────────┐
       ↓               ↓               ↓
    Logger         Dashboard        Metrics
                       │
                       ↓
                    PySide6
```

Hỗ trợ:

```text
subscribe
unsubscribe
publish
```

và event:

```text
CrawlStarted
ChapterCompleted
ChapterFailed
CrawlFinished
```

Sau đó viết test cho:

* subscribe
* unsubscribe
* multiple observers
* observer exception
* duplicate subscription

---

# 48. Tổng kết

Observer Pattern giúp chúng ta chuyển:

```text
Crawler
   ↓
Dashboard.update()
Logger.log()
Metrics.record()
Notification.send()
```

thành:

```text
Crawler
   ↓
Event
   ↓
┌──────────┬───────────┬──────────┐
↓          ↓           ↓
Dashboard  Logger     Metrics
```

Kết quả:

* giảm coupling
* dễ mở rộng
* dễ test
* phù hợp Event-Driven Architecture
* rất phù hợp GUI
* rất phù hợp crawler monitoring
* rất phù hợp PySide6 Signals/Slots

Và đặc biệt với project của bạn:

```text
Crawler
   ↓
Domain/Application Events
   ↓
PySide6 Adapter
   ↓
Signal
   ↓
Dashboard
```

đây là hướng kiến trúc rất đáng theo đuổi.

---

## Tiếp theo — Buổi 37

**Command Pattern**

Chúng ta sẽ đi từ:

```text
Button → trực tiếp gọi method
```

sang:

```text
Button
  ↓
Command
  ↓
execute()
  ↓
Action
```

và áp dụng vào **Crawler Dashboard**:

```text
PauseCrawlerCommand
ResumeCrawlerCommand
StopCrawlerCommand
RetryChapterCommand
StartCrawlerCommand
```

Sau đó sẽ thấy một kiến trúc rất mạnh:

```text
PySide6 UI
    ↓
Command
    ↓
Application Service
    ↓
Crawler
```

đồng thời mở đường cho **Undo/Redo, Command Queue và Worker Architecture**.
