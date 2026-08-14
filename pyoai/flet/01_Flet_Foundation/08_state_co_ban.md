# Buổi 8 — State cơ bản trong Flet

Đây là một buổi **rất quan trọng**.

Từ Buổi 7, chúng ta đã biết:

```text
Event
  ↓
Event Handler
  ↓
Thay đổi UI
  ↓
page.update()
```

Nhưng nếu ứng dụng lớn lên, cách:

```python
text.value = ...
button.disabled = ...
status.value = ...
```

rải khắp các handler sẽ nhanh chóng trở nên khó quản lý.

Hôm nay chúng ta chuyển sang tư duy:

```text
STATE
  ↓
UI
```

và:

```text
EVENT
  ↓
CHANGE STATE
  ↓
UPDATE UI
```

---

# 1. State là gì?

**State** là dữ liệu biểu diễn trạng thái hiện tại của ứng dụng.

Ví dụ Counter:

```python
count = 0
```

thì:

```text
count = 0
```

chính là state.

Khi click `+`:

```text
count = 0
    ↓
count = 1
```

UI:

```text
0
```

phải trở thành:

```text
1
```

---

# 2. State khác UI như thế nào?

Đây là khái niệm quan trọng nhất của buổi hôm nay.

Có:

```text
State
  ↓
count = 10

UI
  ↓
Text("10")
```

State là **dữ liệu**.

UI là **cách biểu diễn dữ liệu**.

Ví dụ:

```python
count = 10

counter_text = ft.Text("10")
```

Ta có:

```text
count
 ↓
10

counter_text
 ↓
"10"
```

Hai thứ này **không phải cùng một khái niệm**.

---

# 3. Sai lầm phổ biến

Người mới học Flet thường coi:

```python
counter.value
```

là state.

Ví dụ:

```python
counter = ft.Text("0")
```

rồi:

```python
counter.value = "1"
```

Cách này vẫn chạy.

Nhưng về architecture, bạn đang dùng:

```text
UI Control
   ↓
làm State
```

Trong app nhỏ có thể chấp nhận.

Nhưng app lớn:

```text
Database
API
Crawler
TTS
Reader
Settings
```

sẽ rất khó quản lý.

Tốt hơn:

```text
Application State
       ↓
       UI
```

---

# 4. State-driven UI

Tư duy chính:

```text
STATE
  ↓
RENDER
  ↓
UI
```

Ví dụ:

```python
count = 0
```

Render:

```python
ft.Text(str(count))
```

Khi state thay đổi:

```python
count = 1
```

render lại:

```python
ft.Text("1")
```

---

# 5. Counter đúng tư duy State

Ví dụ:

```python
import flet as ft


def main(page: ft.Page):

    count = 0

    counter = ft.Text(
        "0",
        size=30,
    )

    def increment(e):
        nonlocal count

        count += 1
        counter.value = str(count)

        page.update()

    page.add(
        counter,
        ft.Button(
            "+",
            on_click=increment,
        ),
    )


ft.run(main)
```

Ở đây:

```python
count
```

là state.

Còn:

```python
counter
```

là UI.

---

# 6. Tại sao cần `nonlocal`?

Đây là Python, không phải riêng Flet.

Ta có:

```python
def main(page):

    count = 0

    def increment(e):
        count += 1
```

Python sẽ báo lỗi vì:

```text
count
```

bị coi là local variable của `increment()`.

Muốn thay đổi biến ở scope bên ngoài:

```python
nonlocal count
```

Ví dụ:

```python
def increment(e):
    nonlocal count
    count += 1
```

---

# 7. Đây là một Closure

Code:

```python
def main(page):

    count = 0

    def increment(e):
        nonlocal count
        count += 1
```

`increment()` giữ được:

```text
count
```

của scope bên ngoài.

Đây là Python closure.

Trong Flet, closure xuất hiện rất nhiều khi viết event handler.

---

# 8. State có thể là nhiều biến

Ví dụ Todo:

```python
todos = []
```

Đây là state.

Khi user nhập:

```text
Learn Python
```

thì:

```python
todos.append("Learn Python")
```

State:

```text
[
    "Learn Python"
]
```

UI:

```text
□ Learn Python
```

---

# 9. State không nhất thiết là một biến đơn

State có thể là:

```python
count = 0
```

hoặc:

```python
username = "Garden"
```

hoặc:

```python
is_loading = False
```

hoặc:

```python
todos = []
```

hoặc:

```python
selected_book_id = 123
```

hoặc:

```python
settings = {
    "theme": "dark",
    "font_size": 18,
}
```

---

# 10. Các loại state cơ bản

Trong ứng dụng Flet, bạn sẽ thường gặp:

### Primitive State

```python
count = 0
```

### Boolean State

```python
is_loading = False
```

### String State

```python
search_text = ""
```

### Collection State

```python
todos = []
```

### Object State

```python
current_user = User(...)
```

---

# 11. UI State

Có một khái niệm cần phân biệt.

Ví dụ:

```python
is_loading = True
```

Đây là state.

Nó quyết định:

```text
Loading indicator
```

có hiển thị hay không.

Ví dụ:

```python
if is_loading:
    ...
```

---

# 12. Application State

Ví dụ app đọc truyện:

```python
current_book_id = 100
current_chapter_id = 5
```

Đây là application state.

UI có thể hiển thị:

```text
Truyện: Đại Chúa Tể
Chương: 5
```

State:

```text
current_book_id = 100
current_chapter_id = 5
```

---

# 13. State và Event

Đây là vòng lặp cơ bản:

```text
          ┌───────────────┐
          │               │
          ▼               │
        STATE             │
          │               │
          ▼               │
          UI              │
          │               │
          ▼               │
        EVENT             │
          │               │
          ▼               │
    EVENT HANDLER         │
          │               │
          └───────────────┘
```

Ví dụ:

```text
count = 0
   ↓
UI = "0"
   ↓
User click
   ↓
increment()
   ↓
count = 1
   ↓
UI = "1"
```

---

# 14. State Mutation

Thay đổi state:

```python
count += 1
```

hoặc:

```python
todos.append(todo)
```

hoặc:

```python
is_loading = True
```

Đây gọi là:

> State mutation.

---

# 15. State và render

Một pattern rất hữu ích:

```python
def render():
    ...
```

Ví dụ:

```python
def render():
    counter.value = str(count)
```

Sau đó:

```python
def increment(e):
    nonlocal count

    count += 1
    render()

    page.update()
```

Flow:

```text
Event
 ↓
State mutation
 ↓
render()
 ↓
page.update()
```

---

# 16. Tách `render()`

Ví dụ:

```python
import flet as ft


def main(page: ft.Page):

    count = 0

    counter = ft.Text(size=30)

    def render():
        counter.value = str(count)

    def increment(e):
        nonlocal count

        count += 1
        render()

        page.update()

    render()

    page.add(
        counter,
        ft.Button(
            "+",
            on_click=increment,
        ),
    )


ft.run(main)
```

Đây là một bước tiến rất tốt về architecture.

---

# 17. Tại sao `render()` hữu ích?

Nếu có:

```text
count
is_loading
error
username
todos
```

ta có thể tập trung logic UI:

```python
def render():
    ...
```

thay vì mỗi handler tự sửa 10 controls.

---

# 18. Ví dụ Loading State

Ta có:

```python
is_loading = False
```

UI:

```text
[Load Data]
```

Click:

```text
is_loading = True
```

UI:

```text
Loading...
```

Sau khi hoàn thành:

```text
is_loading = False
```

UI:

```text
Data loaded
```

---

# 19. Implement

```python
import flet as ft


def main(page: ft.Page):

    is_loading = False

    status = ft.Text()
    button = ft.Button("Load")

    def render():
        if is_loading:
            status.value = "Loading..."
            button.disabled = True
        else:
            status.value = "Ready"
            button.disabled = False

    def load_data(e):
        nonlocal is_loading

        is_loading = True
        render()
        page.update()

        # giả lập công việc

        is_loading = False
        render()
        page.update()

    button.on_click = load_data

    render()

    page.add(
        button,
        status,
    )


ft.run(main)
```

Điểm quan trọng:

```text
is_loading
```

là state.

Không phải:

```python
button.disabled
```

---

# 20. Derived State

Có một khái niệm rất quan trọng:

> Derived State.

Ví dụ:

```python
todos = [
    "Learn Python",
    "Learn Flet",
]
```

Ta không cần lưu:

```python
todo_count = 2
```

vì có thể tính:

```python
todo_count = len(todos)
```

`todo_count` là **derived state**.

---

# 21. Tránh lưu state dư thừa

Không nên:

```python
todos = []

todo_count = 0
```

rồi:

```python
todos.append(...)
todo_count += 1
```

Vì có thể xảy ra:

```text
todos = 3 items
todo_count = 2
```

State bị inconsistent.

Tốt hơn:

```python
todos = []
```

và:

```python
len(todos)
```

---

# 22. Ví dụ Todo

State:

```python
todos = []
```

Derived state:

```python
len(todos)
```

UI:

```text
Todos: 3
```

Render:

```python
count_text.value = f"Todos: {len(todos)}"
```

---

# 23. Boolean State

Boolean state cực kỳ phổ biến:

```python
is_dark = False
```

```python
is_loading = False
```

```python
is_logged_in = False
```

```python
is_menu_open = False
```

```python
is_editing = False
```

UI thường phụ thuộc trực tiếp vào boolean.

---

# 24. State transition

Thay vì nghĩ:

```python
is_loading = True
```

hãy bắt đầu nghĩ:

```text
READY
  ↓
LOAD
  ↓
LOADING
  ↓
SUCCESS
```

hoặc:

```text
LOADING
   ↓
ERROR
```

Đây chính là tư duy dẫn tới **State Machine**.

Chúng ta sẽ học sâu hơn sau này.

---

# 25. State Machine đơn giản

Ví dụ:

```python
status = "idle"
```

Các state:

```text
idle
loading
success
error
```

Flow:

```text
idle
 ↓
loading
 ↓
success
```

Nếu lỗi:

```text
idle
 ↓
loading
 ↓
error
```

UI:

```python
if status == "idle":
    ...

elif status == "loading":
    ...

elif status == "success":
    ...

elif status == "error":
    ...
```

---

# 26. Đây là cách xây API UI

Ví dụ:

```python
status = "loading"
```

UI:

```text
Loading...
```

Không cần:

```python
loading_text.visible = True
success_text.visible = False
error_text.visible = False
```

rải khắp event handler.

Thay vào đó:

```text
State
 ↓
Render
```

---

# 27. State với TextField

Ví dụ:

```python
name = ""
```

Event:

```python
def on_name_change(e):
    nonlocal name

    name = e.control.value
```

State:

```text
name
```

UI:

```text
TextField
```

Ta đang đồng bộ:

```text
TextField
   ↓
Event
   ↓
name state
```

---

# 28. Controlled Input

Đây là một khái niệm rất quan trọng trong UI framework.

```text
User
 ↓
TextField
 ↓
Event
 ↓
State
```

State trở thành nguồn dữ liệu chính.

Ví dụ:

```python
name = ""
```

User nhập:

```text
Garden
```

Handler:

```python
name = "Garden"
```

---

# 29. State → UI

Sau đó:

```python
greeting.value = f"Hello {name}"
```

Kết quả:

```text
State
name = "Garden"

        ↓

UI
Hello Garden
```

---

# 30. Một ví dụ hoàn chỉnh

```python
import flet as ft


def main(page: ft.Page):

    name = ""

    name_input = ft.TextField(
        label="Name",
    )

    greeting = ft.Text(
        size=24,
    )

    def render():
        greeting.value = (
            f"Hello, {name}"
            if name
            else "Hello"
        )

    def on_name_change(e):
        nonlocal name

        name = e.control.value

        render()
        page.update()

    name_input.on_change = on_name_change

    render()

    page.add(
        name_input,
        greeting,
    )


ft.run(main)
```

Flow:

```text
User types
    ↓
on_change
    ↓
name = value
    ↓
render()
    ↓
page.update()
```

---

# 31. State và UI Tree

Ở Buổi 3 chúng ta học:

```text
Page
└── Controls
```

Bây giờ thêm:

```text
State
   ↓
Render
   ↓
UI Tree
```

Architecture:

```text
              STATE
                │
                ▼
             RENDER
                │
                ▼
             UI TREE
                │
                ▼
              USER
                │
                ▼
              EVENT
                │
                ▼
          CHANGE STATE
```

Đây là vòng đời UI cơ bản.

---

# 32. Local State

State có thể nằm trong function:

```python
def main(page):

    count = 0
```

Đây là local state của app function.

Hoặc trong một component:

```python
def counter_component():
    count = 0
```

State chỉ phục vụ component đó.

---

# 33. Shared State

Giả sử:

```text
Header
Books
Reader
Sidebar
```

đều cần:

```python
current_user
```

Ta có shared state:

```text
              App State
                 │
       ┌─────────┼─────────┐
       ▼         ▼         ▼
     Header    Books     Reader
```

Đây là vấn đề sẽ trở nên rất quan trọng khi app lớn.

---

# 34. State ownership

Một câu hỏi quan trọng:

> State này thuộc về ai?

Ví dụ:

```python
search_text
```

chỉ dùng trong SearchView:

```text
SearchView
└── search_text
```

thì không cần global.

Nhưng:

```python
current_user
```

dùng toàn app:

```text
App
└── current_user
```

State nên được đặt ở scope phù hợp.

---

# 35. Không nên biến mọi thứ thành global

Sai:

```python
count = 0
todos = []
user = None
settings = {}
books = []
reader = None
```

ở module level.

Sau này sẽ thành:

```text
Global State Hell
```

Các component có thể thay đổi state bất kỳ lúc nào.

Khó debug.

---

# 36. State càng gần nơi sử dụng càng tốt

Nguyên tắc:

```text
Nếu chỉ 1 component dùng
    ↓
Local State

Nếu nhiều component cùng dùng
    ↓
Shared State

Nếu toàn app dùng
    ↓
App State
```

Đây là nguyên tắc architecture quan trọng.

---

# 37. Immutable vs Mutable State

Python cho phép:

```python
todos.append("Python")
```

Đây là mutation.

State object vẫn cùng object.

Trong một số state-management architecture hiện đại, người ta thích:

```python
new_todos = [
    *todos,
    "Python",
]
```

thay vì mutate trực tiếp.

Lý do:

```text
old state
   ↓
new state
```

dễ theo dõi hơn.

---

# 38. Flet không bắt buộc bạn phải immutable

Đây là điều cần nhớ.

Bạn hoàn toàn có thể:

```python
todos.append(todo)
```

trong Flet.

Flet không bắt buộc Redux/React-style immutable state.

Nhưng khi project lớn, tư duy:

```text
State
 ↓
Transition
 ↓
Render
```

vẫn rất hữu ích.

---

# 39. State Transition Function

Ta có thể viết:

```python
def add_todo(todo):
    todos.append(todo)
```

hoặc:

```python
def increment():
    return count + 1
```

Ý tưởng:

```text
Current State
      +
   Event
      ↓
New State
```

Ví dụ:

```text
count = 10
event = INCREMENT
       ↓
count = 11
```

Đây chính là nền móng của state management.

---

# 40. Event → State Transition

Ví dụ Todo:

```text
ADD_TODO
```

State:

```python
todos = []
```

Transition:

```python
todos.append("Learn Flet")
```

New state:

```python
[
    "Learn Flet"
]
```

UI render lại.

---

# 41. Event không nên trực tiếp điều khiển UI quá nhiều

Ví dụ kiểu khó bảo trì:

```python
def add_todo(e):
    todos.append(input.value)

    input.value = ""
    list_view.controls.append(...)
    count_text.value = ...
    empty_text.visible = False
    delete_button.disabled = ...
    ...
    page.update()
```

Handler đang làm:

```text
State
+
Rendering
+
Business logic
```

Tốt hơn:

```python
def add_todo(e):
    add_todo_to_state(
        input.value
    )

    render()
    page.update()
```

---

# 42. Pattern chúng ta đang hướng tới

```text
Event
  ↓
Action
  ↓
State Transition
  ↓
Render
  ↓
UI
```

Ví dụ:

```text
Click Add
    ↓
ADD_TODO
    ↓
todos.append(...)
    ↓
render()
    ↓
UI
```

---

# 43. Todo App state model

Hãy thiết kế state trước UI:

```python
todos = []

input_text = ""

filter_mode = "all"
```

Derived:

```python
todo_count = len(todos)
```

UI state:

```python
is_loading = False
```

Đây là cách thiết kế tốt hơn:

```text
UI trước
```

mà hãy:

```text
State trước
 ↓
UI sau
```

---

# 44. State model cho Novel Reader

Đây là ví dụ rất gần với project của bạn.

```python
current_book_id = None
current_chapter_id = None

is_loading = False

font_size = 18
theme = "dark"

reading_progress = 0
```

Derived:

```python
chapter_title
progress_percent
```

UI:

```text
Book
Chapter
Progress
Font size
Theme
```

---

# 45. State model cho Crawl Dashboard

Ví dụ:

```python
selected_source = None

is_crawling = False

worker_count = 0

jobs = []

error_message = None
```

Derived:

```python
active_jobs
failed_jobs
completed_jobs
```

UI:

```text
Dashboard
Sources
Jobs
Workers
Logs
```

Bạn có thể thấy:

> State chính là cầu nối giữa UI và application logic.

---

# 46. State Scope

Ta có thể hình dung:

```text
App State
│
├── User
│
├── Settings
│
└── Navigation
│
└── Page State
    │
    ├── Search
    ├── Books
    └── Reader
```

Mỗi state nên có owner rõ ràng.

---

# 47. Một nguyên tắc rất quan trọng

> **Don't store what you can derive.**

Ví dụ:

```python
todos = [...]
```

Không nhất thiết:

```python
todo_count = len(todos)
```

Không nhất thiết:

```python
has_todos = len(todos) > 0
```

Không nhất thiết:

```python
is_empty = len(todos) == 0
```

Ta có thể tính:

```python
len(todos)
```

và:

```python
bool(todos)
```

---

# 48. State và consistency

Nếu bạn lưu:

```python
todos = []
todo_count = 0
is_empty = True
```

thì mỗi lần mutation phải đảm bảo:

```text
todos
todo_count
is_empty
```

đều đồng bộ.

Càng nhiều state dư thừa:

```text
Càng nhiều cơ hội bug.
```

Do đó:

```text
Minimal State
+
Derived State
```

là chiến lược tốt.

---

# 49. Mini architecture

Một component đơn giản:

```python
class Counter:
    def __init__(self):
        self.count = 0
```

State:

```python
self.count
```

Action:

```python
def increment(self):
    self.count += 1
```

Render:

```python
def render(self):
    ...
```

Đây là bước đầu để chúng ta chuyển từ:

```text
Flet script
```

sang:

```text
Flet application architecture
```

---

# 50. Bài tập thực hành 1 — Counter State

Hãy xây:

```text
┌─────────────────────────┐
│                         │
│           0             │
│                         │
│      [-]       [+]      │
│                         │
└─────────────────────────┘
```

State:

```python
count = 0
```

Không được dùng:

```python
counter.value
```

làm state chính.

Phải có:

```text
count
 ↓
render()
 ↓
counter.value
```

---

# 51. Bài tập 2 — Name State

```text
┌─────────────────────────┐
│ Name                    │
│ [ Garden              ] │
│                         │
│ Hello, Garden           │
└─────────────────────────┘
```

State:

```python
name = ""
```

Event:

```text
on_change
```

Flow:

```text
TextField
 ↓
on_change
 ↓
name
 ↓
render
 ↓
greeting
```

---

# 52. Bài tập 3 — Todo State

State:

```python
todos = []
```

Thêm:

```text
Learn Python
Learn Flet
Learn Asyncio
```

State:

```python
[
    "Learn Python",
    "Learn Flet",
    "Learn Asyncio",
]
```

Derived:

```python
len(todos)
```

UI:

```text
Todos: 3

□ Learn Python
□ Learn Flet
□ Learn Asyncio
```

---

# 53. Bài tập 4 — Loading State

Tạo:

```python
is_loading = False
```

Khi click:

```text
is_loading = True
```

UI:

```text
Loading...
```

Sau khi hoàn thành:

```text
is_loading = False
```

UI:

```text
Done
```

Mục tiêu là **không dùng visibility của control làm state chính**.

Sai:

```python
loading.visible = True
```

làm state.

Đúng:

```python
is_loading = True
```

rồi:

```python
loading.visible = is_loading
```

---

# 54. Bài tập Deep Dive — State Machine

Xây một fake download:

```text
IDLE
 ↓
DOWNLOADING
 ↓
COMPLETED
```

hoặc:

```text
IDLE
 ↓
DOWNLOADING
 ↓
ERROR
```

State:

```python
status = "idle"
```

UI phụ thuộc vào:

```python
status
```

Bạn phải tránh tạo quá nhiều boolean:

```python
is_idle
is_downloading
is_completed
is_error
```

Thay vào đó:

```python
status = "idle"
```

Đây là bước chuẩn bị cho **State Machine** ở các buổi nâng cao.

---

# 55. Tổng kết Buổi 8

Bạn cần nắm chắc 8 ý:

### 1. State

```python
count = 0
```

### 2. UI

```python
ft.Text("0")
```

### 3. State ≠ UI

```text
State
 ↓
UI
```

### 4. Event thay đổi State

```text
Event
 ↓
State Mutation
```

### 5. Render

```text
State
 ↓
render()
 ↓
UI
```

### 6. Derived State

```python
len(todos)
```

không cần lưu riêng.

### 7. State Scope

```text
Local
Shared
App
```

### 8. State Flow

```text
             ┌──────────────┐
             │    STATE     │
             └──────┬───────┘
                    │
                    ▼
                RENDER
                    │
                    ▼
                    UI
                    │
                    ▼
                  EVENT
                    │
                    ▼
             STATE TRANSITION
                    │
                    └──────────→ STATE
```

---

# Roadmap chính xác

```text
Giai đoạn I — Flet Foundation

Phần 1 — Làm quen Flet

01. Flet là gì? Kiến trúc Flet              ✅
02. Page và vòng đời ứng dụng               ✅
03. Controls và UI Tree                     ✅
04. Text, Button, Icon, Image               ✅
05. Row, Column, Container                  ✅
06. Responsive Layout                       ✅
07. Event và Event Handler                  ✅
08. State cơ bản                             ← hiện tại
09. page.update() deep dive
10. Mini Project: Todo App
```

**Buổi 9** sẽ là một buổi deep dive rất quan trọng: **`page.update()` hoạt động như thế nào**, update control nào, update subtree, nhiều thay đổi trong một update, `page.update()` vs `control.update()`, vấn đề stale UI, batching và cách tư duy về **UI synchronization** trong Flet.
