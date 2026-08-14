# Buổi 10 — Mini Project: Todo App

Hôm nay chúng ta **kết thúc Giai đoạn I — Flet Foundation / Phần 1** bằng một project nhỏ nhưng cực kỳ quan trọng.

Mục tiêu không phải chỉ tạo được Todo App, mà là luyện toàn bộ kiến thức:

```text
Page
Controls
UI Tree
Layout
Responsive
Event
State
Render
page.update()
```

Và đặc biệt, chúng ta sẽ bắt đầu hình thành tư duy:

```text
DATA / STATE
      ↓
   RENDER
      ↓
     UI
      ↑
    EVENT
```

---

# 1. Project hôm nay

Chúng ta sẽ xây Todo App:

```text
┌──────────────────────────────────────────────┐
│                  Todo App                    │
├──────────────────────────────────────────────┤
│                                              │
│  [ Learn Python................ ] [ Add ]    │
│                                              │
│  All: 3    Active: 2    Completed: 1        │
│                                              │
│  [All] [Active] [Completed]                  │
│                                              │
│  ☑ Learn Python                         [×]  │
│  ☐ Learn Flet                           [×]  │
│  ☐ Learn Asyncio                        [×]  │
│                                              │
└──────────────────────────────────────────────┘
```

Chúng ta sẽ triển khai theo nhiều bước.

---

# 2. Kiến trúc trước khi code

Đây là điều tôi muốn bạn thay đổi trong cách học Flet.

Đừng bắt đầu bằng:

```python
ft.Text(...)
ft.Button(...)
ft.Column(...)
```

Hãy bắt đầu bằng:

```text
Todo App
│
├── State
│
├── Actions
│
├── Render
│
└── UI
```

Cụ thể:

```text
STATE
├── todos
├── input_text
└── filter_mode

ACTIONS
├── add_todo
├── toggle_todo
├── delete_todo
└── set_filter

RENDER
└── render()

UI
├── TextField
├── Button
├── Stats
├── Filter buttons
└── Todo list
```

---

# 3. Data Model

Đầu tiên chúng ta cần quyết định Todo là gì.

Một Todo cần:

```text
id
title
completed
```

Ví dụ:

```python
{
    "id": 1,
    "title": "Learn Python",
    "completed": False,
}
```

Todo khác:

```python
{
    "id": 2,
    "title": "Learn Flet",
    "completed": True,
}
```

---

# 4. Tạo Todo bằng `dataclass`

Thay vì dictionary, chúng ta dùng:

```python
from dataclasses import dataclass
```

Sau đó:

```python
@dataclass
class Todo:
    id: int
    title: str
    completed: bool = False
```

Bây giờ:

```python
todo = Todo(
    id=1,
    title="Learn Python",
)
```

Ta có:

```text
Todo
├── id = 1
├── title = "Learn Python"
└── completed = False
```

---

# 5. State

State của ứng dụng:

```python
todos = []
```

và:

```python
next_id = 1
```

Filter:

```python
filter_mode = "all"
```

Do đó:

```text
Application State
│
├── todos
├── next_id
└── filter_mode
```

---

# 6. Tại sao cần `next_id`?

Khi thêm:

```text
Todo 1
Todo 2
Todo 3
```

ta cần định danh chúng.

Không nên dựa vào index:

```python
todos[0]
todos[1]
todos[2]
```

vì khi xóa:

```text
1
2
3
```

có thể trở thành:

```text
1
3
```

ID giúp xác định object ổn định hơn.

---

# 7. UI Tree

Ta thiết kế:

```text
Page
│
└── Container
    │
    └── Column
        │
        ├── Title
        │
        ├── Input Row
        │   ├── TextField
        │   └── Add Button
        │
        ├── Statistics
        │
        ├── Filter Row
        │   ├── All
        │   ├── Active
        │   └── Completed
        │
        └── Todo List
```

Đây chính là kiến thức Buổi 3 + 5.

---

# 8. Tạo project

Cấu trúc ban đầu:

```text
todo_app/
│
└── main.py
```

`main.py`:

```python
import flet as ft
from dataclasses import dataclass
```

---

# 9. Todo model

```python
@dataclass
class Todo:
    id: int
    title: str
    completed: bool = False
```

---

# 10. Main

```python
def main(page: ft.Page):
    ...
```

và:

```python
ft.run(main)
```

---

# 11. Cấu hình Page

```python
def main(page: ft.Page):

    page.title = "Todo App"

    page.padding = 20
```

Chúng ta có:

```text
Page
├── title
└── padding
```

---

# 12. State

Trong `main()`:

```python
todos: list[Todo] = []
next_id = 1
filter_mode = "all"
```

Đây là **source of truth**.

Điểm rất quan trọng:

> UI controls không phải database.

Ví dụ:

```python
todo_list.controls
```

không phải source of truth.

`todos` mới là source of truth.

---

# 13. Tạo UI Controls

Title:

```python
title = ft.Text(
    "Todo App",
    size=30,
    weight=ft.FontWeight.BOLD,
)
```

Input:

```python
input_field = ft.TextField(
    hint_text="What do you want to do?",
    expand=True,
)
```

Button:

```python
add_button = ft.Button(
    "Add",
)
```

---

# 14. Todo List

```python
todo_list = ft.Column(
    spacing=10,
)
```

Stats:

```python
stats = ft.Text()
```

Filter buttons:

```python
all_button = ft.Button("All")
active_button = ft.Button("Active")
completed_button = ft.Button("Completed")
```

---

# 15. Tạo layout

Input row:

```python
input_row = ft.Row(
    controls=[
        input_field,
        add_button,
    ],
)
```

Filter row:

```python
filter_row = ft.Row(
    controls=[
        all_button,
        active_button,
        completed_button,
    ],
)
```

---

# 16. Main layout

```python
content = ft.Column(
    controls=[
        title,
        input_row,
        stats,
        filter_row,
        todo_list,
    ],
    spacing=15,
)
```

Sau đó:

```python
page.add(content)
```

---

# 17. Nhưng UI chưa làm gì cả

Hiện tại:

```text
State
todos = []

UI
empty
```

Chúng ta cần:

```text
Event
 ↓
State
 ↓
Render
 ↓
Update
```

---

# 18. Action: Add Todo

Viết:

```python
def add_todo(e):
    ...
```

Lấy text:

```python
text = input_field.value.strip()
```

Nếu rỗng:

```python
if not text:
    return
```

---

# 19. Thêm Todo

```python
def add_todo(e):
    nonlocal next_id

    text = input_field.value.strip()

    if not text:
        return

    todo = Todo(
        id=next_id,
        title=text,
    )

    todos.append(todo)

    next_id += 1
```

State:

```text
todos
│
├── Todo(1, "Learn Python")
└── Todo(2, "Learn Flet")
```

---

# 20. Reset Input

Sau khi thêm:

```python
input_field.value = ""
```

Nhưng nhớ:

> Đây là UI mutation.

Còn:

```python
todos.append(todo)
```

là state mutation.

Hai thứ khác nhau.

---

# 21. Render Todo

Bây giờ:

```python
def render_todos():
    ...
```

Trước tiên:

```python
todo_list.controls.clear()
```

Sau đó duyệt:

```python
for todo in todos:
    ...
```

---

# 22. Tạo một Todo Row

Mỗi Todo:

```text
☐ Learn Python                   [Delete]
```

Ta có:

```python
checkbox = ft.Checkbox(
    label=todo.title,
    value=todo.completed,
)
```

Delete:

```python
delete_button = ft.Button(
    "Delete",
)
```

---

# 23. Todo Row

```python
row = ft.Row(
    controls=[
        checkbox,
        delete_button,
    ],
)
```

Sau đó:

```python
todo_list.controls.append(row)
```

---

# 24. Vấn đề closure

Đây là chỗ rất quan trọng về Python.

Ta muốn:

```python
checkbox.on_change
```

biết Todo nào đang được thay đổi.

Có thể viết:

```python
def toggle_todo(e, todo):
    todo.completed = e.control.value
```

Nhưng event handler của Flet cần một argument event.

Có thể tạo closure:

```python
def make_toggle_handler(todo):
    def handler(e):
        todo.completed = e.control.value

    return handler
```

Sau đó:

```python
checkbox.on_change = make_toggle_handler(todo)
```

---

# 25. Delete handler

Tương tự:

```python
def make_delete_handler(todo):
    def handler(e):
        todos.remove(todo)
        render()

    return handler
```

Điểm quan trọng:

```text
handler
   ↓
giữ reference tới todo
```

Đây chính là closure.

---

# 26. Render cần update?

Ta có thể thiết kế:

```python
def render():
    render_todos()
    render_stats()
    render_filters()
```

Sau đó:

```python
def refresh():
    render()
    page.update()
```

Từ đây:

```text
State
 ↓
render()
 ↓
page.update()
```

---

# 27. `render_todos()`

Phiên bản đầu tiên:

```python
def render_todos():

    todo_list.controls.clear()

    for todo in todos:

        checkbox = ft.Checkbox(
            label=todo.title,
            value=todo.completed,
        )

        delete_button = ft.Button(
            "Delete",
        )

        checkbox.on_change = make_toggle_handler(todo)
        delete_button.on_click = make_delete_handler(todo)

        todo_list.controls.append(
            ft.Row(
                controls=[
                    checkbox,
                    delete_button,
                ],
            )
        )
```

---

# 28. Render Statistics

Ta cần:

```text
All: 3
Active: 2
Completed: 1
```

Tính:

```python
total = len(todos)
completed = sum(
    todo.completed
    for todo in todos
)
active = total - completed
```

Sau đó:

```python
stats.value = (
    f"All: {total}   "
    f"Active: {active}   "
    f"Completed: {completed}"
)
```

---

# 29. Đây là Derived State

Nhớ Buổi 8:

```python
completed
active
```

không nhất thiết phải lưu.

Chúng được tính từ:

```python
todos
```

Do đó:

```text
todos
 ↓
completed
active
total
```

Đây là **derived state**.

---

# 30. Render Filter

State:

```python
filter_mode = "all"
```

Ta cần filter:

```python
def get_visible_todos():

    if filter_mode == "all":
        return todos

    if filter_mode == "active":
        return [
            todo
            for todo in todos
            if not todo.completed
        ]

    if filter_mode == "completed":
        return [
            todo
            for todo in todos
            if todo.completed
        ]

    return todos
```

---

# 31. Filter là derived data

Không tạo:

```python
active_todos = []
completed_todos = []
```

rồi cố đồng bộ chúng.

Chỉ cần:

```python
todos
```

và:

```python
filter_mode
```

Sau đó:

```python
visible_todos = get_visible_todos()
```

---

# 32. Filter event

```python
def set_filter(mode):

    def handler(e):
        nonlocal filter_mode

        filter_mode = mode

        refresh()

    return handler
```

Gắn:

```python
all_button.on_click = set_filter("all")
active_button.on_click = set_filter("active")
completed_button.on_click = set_filter("completed")
```

---

# 33. Filter trong render

Sửa:

```python
for todo in todos:
```

thành:

```python
for todo in get_visible_todos():
```

Bây giờ:

```text
filter_mode = "active"
```

thì chỉ render Todo chưa hoàn thành.

---

# 34. Toggle Todo

```python
def make_toggle_handler(todo):

    def handler(e):

        todo.completed = e.control.value

        refresh()

    return handler
```

Flow:

```text
Checkbox
 ↓
Event
 ↓
todo.completed
 ↓
render
 ↓
page.update
```

---

# 35. Delete Todo

```python
def make_delete_handler(todo):

    def handler(e):

        todos.remove(todo)

        refresh()

    return handler
```

Flow:

```text
Delete
 ↓
todos.remove(todo)
 ↓
render
 ↓
update
```

---

# 36. Add Todo hoàn chỉnh

```python
def add_todo(e):
    nonlocal next_id

    text = input_field.value.strip()

    if not text:
        return

    todos.append(
        Todo(
            id=next_id,
            title=text,
        )
    )

    next_id += 1

    input_field.value = ""

    refresh()
```

---

# 37. Render tổng

Ta có:

```python
def render():
    render_todos()
    render_stats()
```

và:

```python
def refresh():
    render()
    page.update()
```

Đây là architecture chính của project.

---

# 38. Initial Render

Trước khi user click:

```python
render()
```

Sau đó:

```python
page.add(content)
```

Tùy cách tổ chức UI, bạn có thể add UI rồi render state vào controls trước khi hiển thị.

Một pattern rõ ràng:

```python
render()

page.add(content)
```

---

# 39. Nhưng có một vấn đề

Khi `render_todos()` tạo controls mới mỗi lần:

```text
Todo
 ↓
Checkbox mới
Button mới
Row mới
```

Điều này đơn giản và rất phù hợp với project học tập.

Nhưng sau này với app lớn:

```text
10,000 Todo
```

ta sẽ phải suy nghĩ về:

```text
Control reuse
Virtualization
Lazy loading
Pagination
```

---

# 40. Todo App — Version 1

Đây là phiên bản hoàn chỉnh đầu tiên:

```python
import flet as ft
from dataclasses import dataclass


@dataclass
class Todo:
    id: int
    title: str
    completed: bool = False


def main(page: ft.Page):

    page.title = "Todo App"
    page.padding = 20

    # -------------------------
    # STATE
    # -------------------------

    todos: list[Todo] = []

    next_id = 1

    filter_mode = "all"

    # -------------------------
    # UI
    # -------------------------

    title = ft.Text(
        "Todo App",
        size=30,
        weight=ft.FontWeight.BOLD,
    )

    input_field = ft.TextField(
        hint_text="What do you want to do?",
        expand=True,
    )

    add_button = ft.Button("Add")

    stats = ft.Text()

    all_button = ft.Button("All")
    active_button = ft.Button("Active")
    completed_button = ft.Button("Completed")

    todo_list = ft.Column(
        spacing=10,
    )

    # -------------------------
    # STATE → DERIVED DATA
    # -------------------------

    def get_visible_todos():

        if filter_mode == "all":
            return todos

        if filter_mode == "active":
            return [
                todo
                for todo in todos
                if not todo.completed
            ]

        if filter_mode == "completed":
            return [
                todo
                for todo in todos
                if todo.completed
            ]

        return todos

    # -------------------------
    # EVENT HANDLERS
    # -------------------------

    def make_toggle_handler(todo):

        def handler(e):

            todo.completed = e.control.value

            refresh()

        return handler

    def make_delete_handler(todo):

        def handler(e):

            todos.remove(todo)

            refresh()

        return handler

    def set_filter(mode):

        def handler(e):
            nonlocal filter_mode

            filter_mode = mode

            refresh()

        return handler

    def add_todo(e):
        nonlocal next_id

        text = input_field.value.strip()

        if not text:
            return

        todos.append(
            Todo(
                id=next_id,
                title=text,
            )
        )

        next_id += 1

        input_field.value = ""

        refresh()

    # -------------------------
    # RENDER
    # -------------------------

    def render_stats():

        total = len(todos)

        completed = sum(
            todo.completed
            for todo in todos
        )

        active = total - completed

        stats.value = (
            f"All: {total}   "
            f"Active: {active}   "
            f"Completed: {completed}"
        )

    def render_todos():

        todo_list.controls.clear()

        for todo in get_visible_todos():

            checkbox = ft.Checkbox(
                label=todo.title,
                value=todo.completed,
                expand=True,
            )

            delete_button = ft.Button(
                "Delete",
            )

            checkbox.on_change = (
                make_toggle_handler(todo)
            )

            delete_button.on_click = (
                make_delete_handler(todo)
            )

            todo_list.controls.append(
                ft.Row(
                    controls=[
                        checkbox,
                        delete_button,
                    ],
                )
            )

    def render():

        render_stats()
        render_todos()

    # -------------------------
    # UPDATE
    # -------------------------

    def refresh():

        render()

        page.update()

    # -------------------------
    # EVENT BINDING
    # -------------------------

    add_button.on_click = add_todo

    all_button.on_click = set_filter("all")
    active_button.on_click = set_filter("active")
    completed_button.on_click = set_filter("completed")

    # -------------------------
    # LAYOUT
    # -------------------------

    input_row = ft.Row(
        controls=[
            input_field,
            add_button,
        ],
    )

    filter_row = ft.Row(
        controls=[
            all_button,
            active_button,
            completed_button,
        ],
    )

    content = ft.Column(
        controls=[
            title,
            input_row,
            stats,
            filter_row,
            todo_list,
        ],
        spacing=15,
    )

    # -------------------------
    # INITIAL RENDER
    # -------------------------

    render()

    page.add(content)


ft.run(main)
```

---

# 41. Phân tích kiến trúc

Code dài, nhưng hãy nhìn theo tầng.

## State

```python
todos
next_id
filter_mode
```

---

## Derived Data

```python
get_visible_todos()
```

---

## Actions

```python
add_todo()
make_toggle_handler()
make_delete_handler()
set_filter()
```

---

## Render

```python
render_stats()
render_todos()
render()
```

---

## Synchronization

```python
refresh()
```

---

## UI

```python
title
input_field
add_button
stats
filter buttons
todo_list
```

Đây chính là kiến trúc:

```text
┌─────────────────────────────┐
│           STATE             │
│ todos / filter / next_id    │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       DERIVED DATA          │
│ visible todos / statistics  │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│           RENDER            │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│             UI              │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│           EVENT             │
└──────────────┬──────────────┘
               │
               └───────────────→ STATE
```

---

# 42. Một vấn đề trong Version 1

Có một điểm architecture chưa tốt:

```python
todo.completed = e.control.value
```

State mutation đang nằm trực tiếp trong event handler.

Với app nhỏ không sao.

Nhưng nếu app lớn, chúng ta có thể tách:

```python
def toggle_todo(todo_id):
    ...
```

và:

```python
def delete_todo(todo_id):
    ...
```

---

# 43. Refactor State Actions

Ví dụ:

```python
def toggle_todo(todo_id, completed):

    for todo in todos:

        if todo.id == todo_id:
            todo.completed = completed
            return
```

Handler:

```python
def make_toggle_handler(todo):

    def handler(e):

        toggle_todo(
            todo.id,
            e.control.value,
        )

        refresh()

    return handler
```

Bây giờ:

```text
UI Event
 ↓
Action
 ↓
State
 ↓
Render
 ↓
Update
```

rõ ràng hơn.

---

# 44. Delete Action

```python
def delete_todo(todo_id):

    for todo in todos:

        if todo.id == todo_id:
            todos.remove(todo)
            return
```

Handler:

```python
def make_delete_handler(todo):

    def handler(e):

        delete_todo(todo.id)

        refresh()

    return handler
```

---

# 45. Add Action

Tương tự:

```python
def add_todo(title):
    nonlocal next_id

    todo = Todo(
        id=next_id,
        title=title,
    )

    todos.append(todo)

    next_id += 1
```

Event:

```python
def on_add(e):

    title = input_field.value.strip()

    if not title:
        return

    add_todo(title)

    input_field.value = ""

    refresh()
```

Đây là kiến trúc sạch hơn.

---

# 46. Validation

Todo không được rỗng:

```python
if not title:
    return
```

Nhưng app thực tế nên báo:

```text
Title cannot be empty.
```

Ta có:

```python
error_text = ft.Text()
```

State:

```python
error_message = ""
```

Render:

```python
error_text.value = error_message
```

---

# 47. Validation đúng tư duy State

Không nên chỉ:

```python
error_text.visible = True
```

mà có thể:

```python
error_message = "Todo cannot be empty"
```

Sau đó:

```python
error_text.value = error_message
```

State:

```text
error_message
```

UI:

```text
error_text
```

---

# 48. State hoàn chỉnh hơn

Todo App có thể có:

```python
todos = []

next_id = 1

filter_mode = "all"

error_message = ""

is_loading = False
```

Nhưng:

```text
total
active
completed
visible_todos
```

là derived.

---

# 49. Completed Todo

Ta có:

```python
todo.completed
```

UI:

```python
ft.Checkbox(
    value=todo.completed
)
```

Flow:

```text
User checks
 ↓
on_change
 ↓
todo.completed = True
 ↓
render
 ↓
page.update
```

Đây chính là kiến thức của Buổi 8 + 9 được áp dụng.

---

# 50. Filter

State:

```python
filter_mode = "active"
```

Derived:

```python
get_visible_todos()
```

UI chỉ hiển thị:

```text
Todo.completed == False
```

Flow:

```text
Click Active
 ↓
filter_mode = "active"
 ↓
render
 ↓
page.update
```

---

# 51. Vì sao không tạo 3 list?

Không nên:

```python
all_todos = []
active_todos = []
completed_todos = []
```

vì phải đồng bộ:

```text
add
delete
toggle
```

trên cả ba.

Chỉ cần:

```python
todos
```

và:

```python
filter_mode
```

---

# 52. Đây chính là "Single Source of Truth"

Khái niệm cực kỳ quan trọng:

> **Single Source of Truth**

Trong project:

```python
todos
```

là source of truth.

Không phải:

```python
todo_list.controls
```

Không phải:

```python
stats.value
```

Không phải:

```python
checkbox.value
```

Các UI control chỉ là **projection** của state.

```text
State
 ↓
UI
```

---

# 53. Một nguyên tắc cực kỳ quan trọng

Nếu Todo:

```python
completed = True
```

thì UI phải tự phản ánh:

```text
☑ Todo
```

Không được có tình trạng:

```text
State:
completed = True

UI:
☐ Todo
```

Nếu có:

```text
State/UI desynchronization
```

---

# 54. Todo App Version 2

Sau khi chạy Version 1, hãy tự nâng cấp:

```text
Todo App
│
├── Add
├── Complete
├── Delete
├── Filter
└── Statistics
```

Thêm:

```text
Clear Completed
```

Flow:

```text
Click
 ↓
todos = [
    todo
    for todo in todos
    if not todo.completed
]
 ↓
render
 ↓
update
```

---

# 55. Bài tập 1 — Clear Completed

Thêm button:

```text
[ Clear Completed ]
```

Action:

```python
def clear_completed():
    ...
```

Không được thao tác trực tiếp trên:

```python
todo_list.controls
```

Chỉ thao tác:

```python
todos
```

---

# 56. Bài tập 2 — Todo Counter

Hiển thị:

```text
3 tasks left
```

Derived:

```python
active = sum(
    not todo.completed
    for todo in todos
)
```

Không tạo:

```python
active_count
```

làm state riêng.

---

# 57. Bài tập 3 — Empty State

Khi:

```python
todos == []
```

hiển thị:

```text
No todos yet.
```

Khi có todo:

```text
No todos yet.
```

biến mất.

Bạn có thể dùng:

```python
empty_text = ft.Text(...)
```

và render:

```python
empty_text.visible = not todos
```

Điểm quan trọng:

```python
not todos
```

là derived state.

---

# 58. Bài tập 4 — Edit Todo

Thêm:

```text
☐ Learn Python      [Edit] [Delete]
```

Click Edit:

```text
[Learn Python........] [Save]
```

State có thể thêm:

```python
editing_todo_id = None
```

Đây là một state rất thú vị.

```text
None
 ↓
editing todo #2
 ↓
None
```

Bạn bắt đầu thấy:

> UI state thực chất cũng có thể được mô hình hóa bằng state machine.

---

# 59. Bài tập 5 — Search

Thêm:

```text
[ Search................ ]
```

State:

```python
search_text = ""
```

Derived:

```python
filtered_todos
```

Flow:

```text
User types
 ↓
search_text
 ↓
get_visible_todos()
 ↓
render
 ↓
update
```

Đây là bài tập chuẩn bị cho:

```text
Debounce
Async
API search
```

---

# 60. Bài tập 6 — Persist dữ liệu

Hiện tại:

```text
Run app
 ↓
todos
 ↓
RAM
```

Đóng app:

```text
todos mất
```

Hãy thiết kế:

```text
Todo State
    ↕
 SQLite
```

Đây sẽ kết nối trực tiếp với những kiến thức SQLite/Repository mà bạn đang học.

---

# 61. Bài tập 7 — Architecture nâng cao

Sau khi Version 1 chạy ổn, thử tổ chức:

```text
todo_app/
│
├── main.py
│
├── models/
│   └── todo.py
│
├── state/
│   └── todo_state.py
│
├── services/
│   └── todo_service.py
│
└── ui/
    └── todo_view.py
```

Chưa cần làm ngay.

Mục tiêu là bắt đầu thấy:

```text
Model
State
Service
UI
```

không nhất thiết phải nằm chung một file.

---

# 62. Điều quan trọng nhất của Project

Đừng tập trung vào:

```text
"Todo App đẹp chưa?"
```

Hãy tập trung vào:

```text
State có rõ không?

Event có rõ không?

State mutation có rõ không?

Render có rõ không?

Update có rõ không?
```

Nếu 5 thứ này rõ:

```text
UI đẹp
→ thêm CSS/theme/layout

Database
→ thêm Repository

Async
→ thêm async service

API
→ thêm API service

Plugin
→ thêm plugin architecture
```

sẽ dễ hơn rất nhiều.

---

# 63. Kiến trúc bạn vừa học

Todo App hiện tại có thể mô hình hóa:

```text
                  ┌───────────────┐
                  │     STATE     │
                  │               │
                  │ todos         │
                  │ filter_mode   │
                  │ next_id       │
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │    DERIVED    │
                  │               │
                  │ visible       │
                  │ statistics    │
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │    RENDER     │
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │      UI       │
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │     EVENT     │
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │    ACTION     │
                  └───────┬───────┘
                          │
                          └──────────→ STATE
```

Đây chính là nền móng để sau này xây Flet app lớn.

---

# 64. Checklist hoàn thành Buổi 10

Bạn nên tự viết Todo App từ đầu mà **không copy code**, và phải có:

* [ ] `Todo` bằng `dataclass`
* [ ] `todos` làm source of truth
* [ ] Add Todo
* [ ] Delete Todo
* [ ] Complete/Uncomplete
* [ ] Filter All
* [ ] Filter Active
* [ ] Filter Completed
* [ ] Statistics
* [ ] Empty state
* [ ] `render()`
* [ ] `page.update()`
* [ ] Không dùng UI controls làm database
* [ ] Không lưu derived state không cần thiết

Nếu làm được toàn bộ, bạn đã nắm khá chắc **Flet Foundation**.

---

# Giai đoạn I — Flet Foundation

### Phần 1 — Làm quen Flet

| Buổi | Nội dung                    | Trạng thái |
| ---- | --------------------------- | ---------- |
| 1    | Flet là gì? Kiến trúc Flet  | ✅          |
| 2    | `Page` và vòng đời ứng dụng | ✅          |
| 3    | Controls và UI Tree         | ✅          |
| 4    | Text, Button, Icon, Image   | ✅          |
| 5    | Row, Column, Container      | ✅          |
| 6    | Responsive Layout           | ✅          |
| 7    | Event và Event Handler      | ✅          |
| 8    | State cơ bản                | ✅          |
| 9    | `page.update()` deep dive   | ✅          |
| 10   | **Mini Project: Todo App**  | **✅**      |

## Kết quả sau Phần 1

Bạn đã có nền tảng:

```text
Flet
 │
 ├── Page
 ├── Control
 ├── UI Tree
 ├── Layout
 ├── Event
 ├── State
 ├── Render
 └── Update
```

**Giai đoạn tiếp theo** sẽ đi sâu vào **Flet UI & Layout**, đặc biệt là `Container`, `Row`, `Column`, `Stack`, `ResponsiveRow`, `GridView`, `ListView`, alignment, spacing, padding, margin, expand và cách thiết kế UI phức tạp mà không biến layout thành một mớ `Row/Column` khó bảo trì.
