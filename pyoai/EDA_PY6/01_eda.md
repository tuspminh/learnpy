# Buổi 1 — Event-Driven Architecture Foundation

Hôm nay chúng ta **chưa vội học `Signal/Slot` của PySide6**. Trước tiên phải hiểu bản chất của Event-Driven Architecture bằng Python thuần.

Mục tiêu cuối buổi:

```text
Producer
   │
   │ Event
   ▼
Event Bus
   │
   ├────► Handler A
   │
   ├────► Handler B
   │
   └────► Handler C
```

---

# 1. Event là gì?

**Event = một sự kiện đã xảy ra.**

Ví dụ trong ứng dụng:

```text
UserCreated
OrderCreated
OrderPaid
FileDownloaded
NoteCreated
NoteDeleted
DownloadCompleted
```

Điểm quan trọng:

> Event mô tả **điều đã xảy ra**, không phải yêu cầu làm việc gì.

Ví dụ:

```text
UserCreated
```

nghĩa là:

> User đã được tạo.

Không phải:

```text
CreateUser
```

vì `CreateUser` mang nghĩa:

> Hãy tạo User.

Đây là sự khác nhau rất quan trọng.

---

# 2. Event vs Command

Đây là khái niệm chúng ta sẽ sử dụng xuyên suốt khóa học.

## Command

Command là **mệnh lệnh**.

```text
CreateNote
DeleteNote
UpdateNote
```

Ý nghĩa:

```text
"Hãy tạo Note"
```

---

## Event

Event là **thông báo về một sự kiện đã xảy ra**.

```text
NoteCreated
NoteDeleted
NoteUpdated
```

Ý nghĩa:

```text
"Note đã được tạo"
```

Có thể hình dung:

```text
Command
   │
   │ "Hãy làm việc này"
   ▼
Use Case
   │
   ▼
Domain
   │
   │ "Việc này đã xảy ra"
   ▼
Event
```

---

# 3. Ví dụ thực tế

Giả sử người dùng nhấn:

```text
[Save Note]
```

Ta có:

```text
SaveNoteCommand
```

Use Case xử lý:

```text
SaveNoteCommand
        ↓
SaveNoteUseCase
        ↓
NoteRepository.save()
```

Sau khi thành công:

```text
NoteSaved
```

Event này có thể được nhiều thành phần quan tâm:

```text
                    NoteSaved
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
    Refresh UI     Write Log    Update Cache
```

Điểm cực kỳ quan trọng:

**`SaveNoteUseCase` không cần biết những Handler này tồn tại.**

---

# 4. Tại sao cần Event-Driven Architecture?

Hãy xem code truyền thống.

```python
class NoteService:

    def save(self, note):
        self.repository.save(note)

        self.ui.refresh()

        self.logger.info("Note saved")

        self.cache.invalidate()

        self.notification.notify()
```

Có một vấn đề lớn.

`NoteService` biết quá nhiều:

```text
NoteService
 ├── Repository
 ├── UI
 ├── Logger
 ├── Cache
 └── Notification
```

Coupling rất cao.

Nếu thêm:

```text
Analytics
```

ta lại sửa `NoteService`.

---

# 5. Event-Driven giải quyết như thế nào?

Ta chuyển thành:

```python
class NoteService:

    def save(self, note):
        self.repository.save(note)

        self.event_bus.publish(
            NoteSaved(note.id)
        )
```

Sau đó:

```text
NoteSaved
    │
    ├──► RefreshUIHandler
    ├──► LoggingHandler
    ├──► CacheHandler
    └──► NotificationHandler
```

`NoteService` không biết các Handler.

Đây chính là:

> **Loose Coupling**

---

# 6. Producer và Consumer

EDA thường có hai vai trò:

## Producer

Thành phần tạo/phát event.

```text
Producer
    │
    ▼
Event
```

Ví dụ:

```python
event_bus.publish(NoteSaved(note.id))
```

---

## Consumer

Thành phần nhận và xử lý event.

```text
Event
  │
  ▼
Consumer
```

Ví dụ:

```python
def handle(event: NoteSaved):
    print(f"Note {event.note_id} saved")
```

---

# 7. Event Handler

Handler là code chịu trách nhiệm xử lý một Event.

Ví dụ:

```python
class NoteSavedHandler:

    def handle(self, event):
        print(
            f"Note {event.note_id} đã được lưu"
        )
```

Flow:

```text
NoteSaved
    ↓
NoteSavedHandler
    ↓
handle()
```

Một event có thể có nhiều handler.

```text
NoteSaved
    │
    ├──► UpdateUIHandler
    ├──► LogHandler
    ├──► CacheHandler
    └──► NotificationHandler
```

---

# 8. Event không nên biết Handler

Một Event chỉ chứa dữ liệu.

Ví dụ:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class NoteSaved:
    note_id: int
```

Nó không nên chứa:

```python
class NoteSaved:

    def handle(self):
        ...
```

vì như vậy Event bắt đầu biết cách xử lý chính nó.

Ta muốn:

```text
Event
  ↓
EventBus
  ↓
Handler
```

chứ không phải:

```text
Event
  ↓
tự xử lý
```

---

# 9. Tự xây Event Bus

Bây giờ chúng ta xây thành phần quan trọng nhất.

```text
EventBus
```

Nhiệm vụ:

```text
subscribe()
publish()
```

---

## Phiên bản đầu tiên

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

Đây chính là Event Bus tối giản.

---

# 10. Sử dụng Event Bus

Tạo Event:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class NoteSaved:
    note_id: int
```

Handler:

```python
def handle_note_saved(event):
    print(
        f"Note {event.note_id} đã được lưu"
    )
```

Tạo Bus:

```python
bus = EventBus()
```

Đăng ký:

```python
bus.subscribe(
    NoteSaved,
    handle_note_saved
)
```

Phát event:

```python
bus.publish(
    NoteSaved(note_id=10)
)
```

Kết quả:

```text
Note 10 đã được lưu
```

---

# 11. Một Event — nhiều Handler

Đây mới là sức mạnh của Event Bus.

```python
def refresh_ui(event):
    print("Refresh UI")


def write_log(event):
    print("Write log")


def update_cache(event):
    print("Update cache")
```

Đăng ký:

```python
bus.subscribe(
    NoteSaved,
    refresh_ui
)

bus.subscribe(
    NoteSaved,
    write_log
)

bus.subscribe(
    NoteSaved,
    update_cache
)
```

Publish:

```python
bus.publish(
    NoteSaved(10)
)
```

Kết quả:

```text
Refresh UI
Write log
Update cache
```

Ta có:

```text
                    NoteSaved
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
         Refresh     Logging    Cache
```

---

# 12. Producer hoàn toàn không biết Consumer

Đây là phần quan trọng nhất.

Producer:

```python
class NoteService:

    def __init__(self, repository, event_bus):
        self.repository = repository
        self.event_bus = event_bus

    def save(self, note):
        self.repository.save(note)

        self.event_bus.publish(
            NoteSaved(note.id)
        )
```

Notice:

`NoteService` không có:

```python
refresh_ui()
```

Không có:

```python
write_log()
```

Không có:

```python
update_cache()
```

Nó chỉ biết:

```text
"Note đã được lưu"
```

và phát:

```text
NoteSaved
```

---

# 13. Đây chính là Open/Closed Principle

Giả sử ban đầu:

```text
NoteSaved
 ├── UI Handler
 └── Log Handler
```

Sau này muốn thêm:

```text
Analytics Handler
```

Ta không cần sửa:

```python
NoteService
```

Chỉ cần:

```python
bus.subscribe(
    NoteSaved,
    analytics_handler
)
```

Kiến trúc trở thành:

```text
NoteSaved
    │
    ├── UI
    ├── Log
    ├── Analytics
    └── Cache
```

Đây là một ứng dụng rất tự nhiên của **OCP**.

---

# 14. Event vs Callback

Hai thứ này khá giống nhau nhưng không giống về kiến trúc.

Callback:

```python
def save(callback):
    ...
    callback()
```

Caller phải đưa callback vào:

```python
save(refresh_ui)
```

Nó tạo dependency:

```text
Service
   │
   ▼
Callback
```

Event:

```python
event_bus.publish(
    NoteSaved(10)
)
```

Producer không biết ai nghe event.

```text
Producer
   │
   ▼
Event
   │
   ▼
EventBus
   │
   ├── Handler A
   ├── Handler B
   └── Handler C
```

Đây là sự khác biệt kiến trúc rất lớn.

---

# 15. Event Loop là gì?

EDA thường liên quan đến **Event Loop**.

Ý tưởng cơ bản:

```text
┌──────────────────────┐
│      Event Queue     │
├──────────────────────┤
│ Click                │
│ KeyPress             │
│ Timer                │
│ Paint                │
└──────────┬───────────┘
           │
           ▼
      Event Loop
           │
           ▼
       Dispatcher
           │
           ▼
        Handler
```

Ứng dụng GUI hoạt động dựa rất nhiều vào mô hình này.

Khi bạn:

```python
button.clicked.connect(on_clicked)
```

bạn đang đăng ký một handler cho một sự kiện.

Sau đó khi người dùng click:

```text
Mouse
  ↓
Qt Event System
  ↓
clicked
  ↓
on_clicked()
```

---

# 16. PySide6 và EDA

Đây là nơi mọi thứ bắt đầu kết nối.

PySide6 đã có Event-Driven Architecture ở cấp framework.

Ví dụ:

```python
button.clicked.connect(
    self.on_clicked
)
```

Ta có:

```text
QPushButton
     │
     │ clicked
     ▼
Signal
     │
     ▼
Slot
```

Nhưng đây mới chỉ là **Qt-level event**.

Sau này ta sẽ xây thêm application-level event:

```text
Qt Signal
    │
    ▼
Command
    │
    ▼
Use Case
    │
    ▼
Domain Event
    │
    ▼
Event Bus
```

---

# 17. Ba tầng Event chúng ta sẽ phân biệt

Trong khóa học này, hãy nhớ ba khái niệm:

### Qt Event

Ví dụ:

```text
MousePress
KeyPress
Paint
Close
```

### Application Event

Ví dụ:

```text
NoteSelected
SearchRequested
NoteSaveRequested
```

### Domain Event

Ví dụ:

```text
NoteCreated
NoteUpdated
NoteDeleted
```

Sau này architecture sẽ là:

```text
                PySide6
                   │
             Qt Signal/Event
                   │
                   ▼
             Application
                   │
              Command
                   │
                   ▼
               UseCase
                   │
                   ▼
                Domain
                   │
             Domain Event
                   │
                   ▼
               EventBus
```

Đây là kiến trúc chúng ta sẽ xây dần.

---

# 18. Bài tập thực hành

Hãy tự viết một Event Bus nhỏ có:

```python
bus.subscribe(...)
bus.publish(...)
```

và ba event:

```text
UserCreated
UserDeleted
UserUpdated
```

Tạo các handler:

```text
LogHandler
EmailHandler
UIHandler
```

Mục tiêu:

```text
UserCreated
    │
    ├──► LogHandler
    ├──► EmailHandler
    └──► UIHandler
```

---

# 19. Bài tập nâng cao

Sau khi làm được phần trên, thử xây:

```text
OrderCreated
OrderPaid
OrderCancelled
```

Ví dụ:

```text
OrderPaid
    │
    ├──► UpdateOrderStatus
    ├──► SendEmail
    ├──► WriteLog
    └──► UpdateDashboard
```

**Không được để `OrderService` gọi trực tiếp các Handler.**

---

# 20. Kiến thức cốt lõi của Buổi 1

Bạn chỉ cần nhớ 6 câu này:

```text
1. Event = điều đã xảy ra.

2. Command = yêu cầu thực hiện một hành động.

3. Producer phát Event.

4. Consumer/Handler xử lý Event.

5. Event Bus kết nối Producer và Consumer.

6. Producer không cần biết Consumer.
```

Và architecture:

```text
             PRODUCER
                 │
                 │ publish(Event)
                 ▼
             EVENT BUS
                 │
       ┌─────────┼─────────┐
       ▼         ▼         ▼
    Handler   Handler   Handler
```

Đây là nền móng để sang **Buổi 2 — Qt Event Loop Deep Dive**, nơi ta sẽ mổ xẻ chính `QApplication.exec()`, event queue, event dispatcher, event propagation và tại sao một ứng dụng PySide6 có thể chạy mà không cần một vòng `while` do chúng ta tự viết.
