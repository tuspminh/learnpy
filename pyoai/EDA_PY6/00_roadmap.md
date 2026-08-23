Được. Với nền tảng bạn đang học **PySide6 + Clean Architecture + DDD + SOLID**, học **Event-Driven Architecture (EDA)** là bước rất hợp lý. Ta sẽ không chỉ học `Signal/Slot`, mà đi từ **Qt Event Loop → Event → Event Bus → Handler → Use Case → Domain Event**, rồi áp dụng vào một ứng dụng thực tế.

# Khóa học Event-Driven Architecture với PySide6

## Mục tiêu cuối khóa

Sau khóa này bạn có thể thiết kế ứng dụng theo luồng:

```text
User
 │
 ▼
PySide6 Widget
 │
 │ Signal
 ▼
Presentation
 │
 ▼
Command / Use Case
 │
 ▼
Domain
 │
 │ Domain Event
 ▼
Event Bus
 │
 ├────► Handler A
 │
 ├────► Handler B
 │
 └────► Handler C
```

Thay vì viết kiểu:

```python
def on_save_clicked(self):
    self.service.save(...)
    self.refresh_table()
    self.update_status()
    self.write_log()
    self.send_notification()
```

ta hướng tới:

```text
Button
  │
  ▼
SaveCommand
  │
  ▼
SaveNoteUseCase
  │
  ▼
NoteSavedEvent
  │
  ▼
EventBus
  ├── RefreshTableHandler
  ├── StatusBarHandler
  ├── LoggingHandler
  └── NotificationHandler
```

Đây chính là điểm quan trọng của EDA:

> **Object phát ra sự kiện không cần biết ai sẽ xử lý sự kiện đó.**

---

# Roadmap

## Phần I — Event-Driven Foundation

### Buổi 1 — Event-Driven Architecture là gì?

* Event là gì?
* Event-driven programming
* Event-driven architecture
* Event vs Command
* Event vs Message
* Producer / Consumer
* Event Handler
* Event Loop
* Loose Coupling
* Push vs Pull
* Synchronous vs Asynchronous Event

### Buổi 2 — Qt Event Loop Deep Dive

* `QApplication`
* Event Loop
* `exec()`
* Event Queue
* Event Dispatcher
* Mouse Event
* Keyboard Event
* Paint Event
* Timer Event
* Event propagation

### Buổi 3 — Signal / Slot Deep Dive

* `Signal`
* `Slot`
* `connect()`
* `emit()`
* Direct Connection
* Queued Connection
* Signal parameter
* Signal giữa các object
* Signal vs callback

### Buổi 4 — Xây Event Bus đầu tiên

```text
Event
  ↓
EventBus
  ↓
Handler
```

Ta tự xây:

```python
EventBus
EventHandler
Event
```

Ví dụ:

```python
class UserCreated:
    def __init__(self, user_id: int):
        self.user_id = user_id
```

---

# Phần II — Event Bus Architecture

### Buổi 5 — Event Bus Deep Dive

Thiết kế:

```text
EventBus
 ├── subscribe()
 ├── unsubscribe()
 └── publish()
```

Ví dụ:

```python
bus.subscribe(UserCreated, handler)
bus.publish(UserCreated(10))
```

### Buổi 6 — Typed Event Bus

Dùng:

```python
Generic
TypeVar
Protocol
Callable
```

để tạo Event Bus type-safe.

### Buổi 7 — Multiple Handlers

Một event:

```text
UserCreated
     │
     ├── SendWelcomeEmail
     ├── CreateProfile
     ├── WriteAuditLog
     └── UpdateDashboard
```

### Buổi 8 — Event Handler Lifecycle

* Register
* Unregister
* Handler lifetime
* Object lifetime
* Memory leak
* Weak reference
* QObject ownership

---

# Phần III — EDA + PySide6

### Buổi 9 — Widget không gọi Widget

Ta loại bỏ kiểu:

```python
self.window.table.refresh()
self.window.status.showMessage()
self.window.panel.reload()
```

Thay bằng:

```text
Widget
 ↓
Event
 ↓
EventBus
 ↓
Handler
 ↓
Widget update
```

### Buổi 10 — UI Event Bus

Xây:

```text
UI
 │
 ▼
UIEventBus
 │
 ├── NoteCreated
 ├── NoteUpdated
 ├── NoteDeleted
 └── NoteSelected
```

### Buổi 11 — Signal + Event Bus

Kết hợp:

```text
Qt Signal
    ↓
Event Adapter
    ↓
Application Event
    ↓
EventBus
```

Phân biệt rõ:

```text
Qt Event
Qt Signal
Application Event
Domain Event
```

### Buổi 12 — Event Adapter

Ví dụ:

```text
QPushButton.clicked
        ↓
CreateNoteCommand
        ↓
UseCase
```

---

# Phần IV — EDA + Clean Architecture

Đây sẽ là phần rất quan trọng với roadmap bạn đang học.

### Buổi 13 — Event trong Clean Architecture

Thiết kế:

```text
Presentation
     │
     ▼
Application
     │
     ▼
Domain
```

Event không được làm dependency ngược:

```text
Domain
  ❌
  ↓
PySide6
```

Domain phải độc lập:

```text
Domain Event
```

không phải:

```python
PySide6Signal
```

### Buổi 14 — Application Event

Phân biệt:

```text
UI Event
Application Event
Domain Event
Infrastructure Event
```

### Buổi 15 — Domain Event

Ví dụ:

```python
@dataclass(frozen=True)
class NoteCreated:
    note_id: int
```

Aggregate phát event:

```text
Note
 │
 │ create()
 ▼
NoteCreated
```

### Buổi 16 — Aggregate + Domain Events

Luồng:

```text
Command
   ↓
Use Case
   ↓
Aggregate
   ↓
Domain Event
   ↓
Event Bus
```

---

# Phần V — Command + Query + Event

### Buổi 17 — Command

```text
CreateNoteCommand
UpdateNoteCommand
DeleteNoteCommand
```

Command mang ý nghĩa:

> "Hãy làm việc này."

### Buổi 18 — Event

Event mang ý nghĩa:

> "Việc này đã xảy ra."

So sánh:

```text
Command
CreateNote
    ↓
    "Hãy tạo Note"

Event
NoteCreated
    ↓
    "Note đã được tạo"
```

### Buổi 19 — CQRS Foundation

```text
Command
   ↓
Write Model


Query
   ↓
Read Model
```

### Buổi 20 — CQRS + PySide6

Thiết kế:

```text
              ┌── Command ──► Write
UI ───────────┤
              └── Query ────► Read
```

---

# Phần VI — Async Event-Driven Architecture

Đây sẽ kết nối rất tốt với phần **asyncio** bạn đang học.

### Buổi 21 — Sync Event Bus

```text
publish()
   ↓
handler()
   ↓
return
```

### Buổi 22 — Async Event Bus

```text
publish()
   ↓
await handler()
```

### Buổi 23 — PySide6 + asyncio

Hiểu vấn đề:

```text
Qt Event Loop
       +
asyncio Event Loop
```

và tại sao không nên tùy tiện:

```python
asyncio.run(...)
```

bên trong GUI event handler.

### Buổi 24 — Worker + Event

Xây:

```text
GUI
 │
 ▼
Command
 │
 ▼
Worker
 │
 ├── ProgressEvent
 ├── CompletedEvent
 └── FailedEvent
```

---

# Phần VII — Production Architecture

### Buổi 25 — Event Store

Hiểu:

```text
Event
 ↓
Event Store
```

### Buổi 26 — Event Replay

Ví dụ:

```text
NoteCreated
NoteRenamed
NoteContentChanged
NoteDeleted
```

Replay:

```text
Event 1
   ↓
Event 2
   ↓
Event 3
   ↓
Current State
```

### Buổi 27 — Event Ordering

* Event ordering
* Event sequence
* Timestamp
* Event ID
* Correlation ID
* Causation ID

### Buổi 28 — Error Handling

* Handler exception
* Retry
* Dead Letter Event
* Failed Event
* Error isolation

### Buổi 29 — Transaction + Event

Tìm hiểu vấn đề:

```text
DB transaction
      +
publish event
```

và **Outbox Pattern**.

### Buổi 30 — Event-Driven Architecture hoàn chỉnh

Thiết kế production architecture:

```text
                 PySide6
                    │
             ┌──────▼──────┐
             │ Presentation │
             └──────┬──────┘
                    │
                 Command
                    │
             ┌──────▼──────┐
             │ Application │
             └──────┬──────┘
                    │
                 UseCase
                    │
             ┌──────▼──────┐
             │   Domain    │
             └──────┬──────┘
                    │
              Domain Event
                    │
             ┌──────▼──────┐
             │  Event Bus  │
             └──────┬──────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
    Handler A   Handler B   Handler C
        │           │           │
        ▼           ▼           ▼
       DB         Cache       UI
```

---

# Phần VIII — Project

## Buổi 31–35 — Note App Event-Driven

Ta sẽ xây một **Note Application bằng PySide6 + SQLite**.

Kiến trúc:

```text
                 ┌──────────────┐
                 │   PySide6    │
                 └──────┬───────┘
                        │
                      Signal
                        │
                        ▼
                 ┌──────────────┐
                 │   Command    │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │    UseCase   │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │    Domain    │
                 └──────┬───────┘
                        │
                 NoteCreated
                        │
                        ▼
                 ┌──────────────┐
                 │  Event Bus   │
                 └──────┬───────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
      DB Handler    UI Handler    Log Handler
```

Các chức năng:

* Create Note
* Update Note
* Delete Note
* Search Note
* Select Note
* Autosave
* Undo/Redo
* Background task
* Progress
* Error handling
* Logging
* Event history

---

# Cách chúng ta học

Mỗi buổi tôi sẽ dạy theo cấu trúc:

### 1. Concept

Giải thích bản chất, không học thuộc API.

### 2. Architecture

Vẽ flow:

```text
A → B → C → D
```

và giải thích **tại sao** thiết kế như vậy.

### 3. Code từ đơn giản → production

Ví dụ nhỏ trước:

```python
button.clicked.connect(...)
```

sau đó tiến tới:

```text
Signal
 ↓
Command
 ↓
UseCase
 ↓
Domain Event
 ↓
EventBus
 ↓
Handler
```

### 4. Refactoring

Ta sẽ cố tình viết code xấu:

```python
def on_save():
    save_database()
    refresh_table()
    update_status()
    write_log()
```

rồi refactor thành EDA.

### 5. Testing

Mỗi phần đều có test:

```text
Event
EventBus
Handler
UseCase
Domain Event
```

để cuối khóa có architecture có thể test được.

---

# Một nguyên tắc rất quan trọng

Khi học EDA với PySide6, tôi muốn bạn **không đồng nhất Signal/Slot với Event-Driven Architecture**.

`Signal/Slot` là cơ chế của Qt:

```text
button.clicked
      ↓
slot()
```

EDA là **kiến trúc ở cấp độ lớn hơn**:

```text
UI
 ↓
Command
 ↓
Application
 ↓
Domain
 ↓
Event
 ↓
Event Bus
 ↓
Handlers
```

Qt `Signal` chỉ có thể là **một cơ chế vận chuyển event** trong architecture đó.

---

## Bắt đầu: Buổi 1

**Buổi 1 — Event-Driven Architecture Foundation**

Ta sẽ đi thật sâu vào:

1. Event thực chất là gì?
2. Event-driven programming
3. Event-driven architecture
4. Event vs Command
5. Event vs Callback
6. Producer / Consumer
7. Event Handler
8. Event Loop
9. Loose Coupling
10. Ví dụ EDA bằng Python thuần
11. Sau đó chuyển sang PySide6

Và cuối buổi đầu tiên ta sẽ tự xây một flow nhỏ:

```text
Button
  ↓
Event
  ↓
EventBus
  ↓
Handler
```

**không dùng framework ngoài**, để bạn hiểu bản chất trước khi đưa vào Clean Architecture/DDD.
