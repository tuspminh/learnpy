# Buổi 9 — `page.update()` Deep Dive

Hôm nay chúng ta đi sâu vào một cơ chế **cốt lõi của Flet**:

```python
page.update()
```

Nếu Buổi 8 chúng ta học:

```text
Event
   ↓
State
   ↓
Render
```

thì hôm nay chúng ta học chính xác bước:

```text
State/UI thay đổi
       ↓
   page.update()
       ↓
Flet đồng bộ UI
```

> **Lưu ý quan trọng:** `page.update()` không phải là "render toàn bộ ứng dụng từ đầu" theo nghĩa đơn giản. Hãy hiểu nó là thao tác yêu cầu Flet **đồng bộ những thay đổi của control tree với UI đang chạy**.

---

# 1. `page.update()` là gì?

Ví dụ:

```python
import flet as ft


def main(page: ft.Page):

    text = ft.Text("Hello")

    page.add(text)

    text.value = "Hello Flet"

    page.update()


ft.run(main)
```

Có hai giai đoạn:

```text
Ban đầu:

Text
└── "Hello"
```

Sau:

```python
text.value = "Hello Flet"
```

Python object đã thay đổi:

```text
Text
└── "Hello Flet"
```

Nhưng UI phía client cần được đồng bộ.

```python
page.update()
```

thực hiện bước đó.

---

# 2. Đừng hiểu `update()` là "thay đổi state"

Đây là distinction cực kỳ quan trọng.

```python
count += 1
```

là:

```text
State mutation
```

Còn:

```python
page.update()
```

là:

```text
UI synchronization
```

Hai việc khác nhau.

```text
             Application
                 │
                 ▼
              State
                 │
          count = 1
                 │
                 ▼
              Render
                 │
                 ▼
          Control property
                 │
                 ▼
          page.update()
                 │
                 ▼
          Client UI
```

---

# 3. Ví dụ dễ hiểu nhất

```python
text.value = "Hello"
```

thay đổi object phía Python.

Nhưng:

```python
page.update()
```

mới yêu cầu Flet đồng bộ thay đổi đó.

Vì vậy hãy nhớ:

```text
Python object ≠ Client UI
```

---

# 4. `page.update()` trong Event Handler

Pattern kinh điển:

```python
def handle_click(e):
    text.value = "Clicked!"
    page.update()
```

Flow:

```text
User
 ↓
Click
 ↓
handle_click()
 ↓
text.value thay đổi
 ↓
page.update()
 ↓
UI thay đổi
```

---

# 5. Nếu không gọi `page.update()`?

Ví dụ:

```python
def handle_click(e):
    text.value = "Clicked!"
```

Bạn đã thay đổi:

```python
text.value
```

nhưng không yêu cầu đồng bộ UI.

Kết quả có thể là:

```text
Python side
    ↓
"Clicked!"

Client UI
    ↓
"Hello"
```

Đây là tình trạng:

> **stale UI**

UI hiển thị dữ liệu cũ.

---

# 6. `page.update()` giống như một "commit"

Bạn có thể hình dung:

```text
text.value = "A"
text.visible = False
button.disabled = True
```

là các mutation.

Sau đó:

```python
page.update()
```

giống như:

```text
Commit changes
      ↓
Sync to UI
```

Đây là mental model rất hữu ích.

---

# 7. Nhiều thay đổi → một update

Không nên:

```python
text.value = "Loading"
page.update()

button.disabled = True
page.update()

status.value = "Please wait"
page.update()
```

Nếu không có lý do đặc biệt.

Tốt hơn:

```python
text.value = "Loading"
button.disabled = True
status.value = "Please wait"

page.update()
```

Tư duy:

```text
Mutation
Mutation
Mutation
Mutation
   ↓
ONE UPDATE
```

---

# 8. Vì sao nên gom update?

Bởi vì mỗi lần đồng bộ có thể liên quan đến:

```text
Python
 ↓
Control tree
 ↓
Flet protocol
 ↓
Client
 ↓
UI rendering
```

Do đó:

```text
10 mutations
+
1 update
```

thường hợp lý hơn:

```text
10 mutations
+
10 updates
```

---

# 9. Ví dụ thực tế

```python
def start_loading(e):

    status.value = "Loading..."
    progress.value = 0
    button.disabled = True
    error_text.value = ""

    page.update()
```

Một event thay đổi nhiều UI elements.

Chỉ cần:

```python
page.update()
```

một lần.

---

# 10. `page.update()` không phải state management

Đừng nhầm:

```python
page.update()
```

với:

```text
State Management
```

Flet không tự biến:

```python
page.update()
```

thành Redux, MobX, Zustand hay một hệ thống state management.

Bạn vẫn phải thiết kế:

```text
State
Events
State transitions
Rendering
```

`page.update()` chỉ là một phần trong quá trình đồng bộ UI.

---

# 11. `Control.update()`

Ngoài:

```python
page.update()
```

Flet còn có cơ chế update ở cấp control.

Mental model:

```text
Page
 ├── Header
 ├── Content
 │    ├── Text
 │    └── Button
 └── Footer
```

Bạn có thể cập nhật từ page:

```python
page.update()
```

hoặc trong những trường hợp phù hợp, update một control/subtree.

Ví dụ conceptually:

```python
container.update()
```

Điểm cần nhớ:

> `page.update()` là lựa chọn phổ biến và dễ hiểu nhất khi bạn đang quản lý UI từ page.

---

# 12. Khi nào dùng `page.update()`?

Trong các app nhỏ:

```python
def on_click(e):
    text.value = "Hello"
    page.update()
```

rất rõ ràng.

Khi component được thiết kế riêng:

```python
class MyComponent:
    ...
```

việc update cục bộ có thể giúp encapsulation tốt hơn.

---

# 13. `update()` và control chưa được add vào tree

Đây là điểm rất quan trọng.

Ví dụ:

```python
text = ft.Text("Hello")

text.value = "Changed"

page.update()
```

Nhưng:

```text
text
```

chưa nằm trong page/control tree.

Thì UI không có gì để hiển thị.

Bạn cần:

```python
page.add(text)
```

trước.

---

# 14. Control Tree

Nhắc lại Buổi 3:

```text
Page
│
├── Text
├── Button
└── Container
     │
     └── Text
```

`page.update()` hoạt động trên **control tree** mà Flet đang quản lý.

Nếu control không nằm trong tree:

```text
Page
└── ...

Text ← detached
```

thì việc thay đổi nó không tự nhiên làm nó xuất hiện trên UI.

---

# 15. `page.add()` và `page.update()`

Một điểm dễ gây nhầm.

Ví dụ:

```python
page.add(
    ft.Text("Hello")
)
```

Flet quản lý việc thêm control vào page.

Trong các thao tác thông thường, bạn không cần biến mọi dòng:

```python
page.add(...)
page.update()
```

thành một nghi thức bắt buộc.

Điều quan trọng là hiểu:

```text
Mutation control tree
        ↓
Flet sync
```

---

# 16. `page.update()` sau `page.add()`

Ví dụ:

```python
text = ft.Text("Hello")

page.controls.append(text)

page.update()
```

Ở đây bạn trực tiếp mutation:

```python
page.controls
```

nên `page.update()` rất quan trọng để đồng bộ.

Trong khi:

```python
page.add(text)
```

là API cấp cao hơn để thêm control.

---

# 17. Đừng lạm dụng `page.controls`

Ví dụ:

```python
page.controls.append(...)
```

có thể làm được.

Nhưng trong code ứng dụng:

```python
page.add(...)
```

thường rõ nghĩa hơn.

Tương tự:

```python
container.controls.append(...)
```

so với API phù hợp của container.

---

# 18. `page.update()` và render function

Buổi 8 chúng ta có:

```python
def render():
    text.value = str(count)
```

Handler:

```python
def increment(e):
    nonlocal count

    count += 1

    render()
    page.update()
```

Đây là architecture rất sạch cho app nhỏ.

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

# 19. Một update ở cuối render

Bạn có thể tổ chức:

```python
def render():
    text.value = str(count)
    status.value = "Running"
    button.disabled = False
```

Sau đó:

```python
def increment(e):
    nonlocal count

    count += 1

    render()
    page.update()
```

Điều này tạo boundary rõ ràng:

```text
render()
```

chịu trách nhiệm:

> UI phải trông như thế nào?

```text
page.update()
```

chịu trách nhiệm:

> Đồng bộ thay đổi đó.

---

# 20. `render()` không phải `update()`

Đừng viết:

```python
def render():
    text.value = ...
    page.update()
```

rồi gọi:

```python
render()
render()
render()
```

trong mọi trường hợp.

Bạn có thể tách:

```text
render
=
mutate controls
```

và:

```text
update
=
sync UI
```

Ví dụ:

```python
def render():
    text.value = str(count)
    status.value = "Ready"
```

Sau đó:

```python
render()
page.update()
```

---

# 21. Tại sao separation này hữu ích?

Sau này bạn có thể:

```text
State
 ↓
render()
 ↓
inspect UI state
 ↓
page.update()
```

Điều này làm architecture dễ test hơn.

Ví dụ:

```python
count = 5
render()

assert text.value == "5"
```

Không nhất thiết phải chạy UI thật để kiểm tra toàn bộ logic render.

---

# 22. `page.update()` và event frequency

Không phải event nào cũng giống nhau.

Ví dụ:

```text
Button click
```

tần suất thấp.

Nhưng:

```text
TextField on_change
```

có thể xảy ra rất thường xuyên:

```text
H
He
Hel
Hell
Hello
```

Nếu mỗi ký tự:

```python
render()
page.update()
```

thì ứng dụng có thể phải đồng bộ rất nhiều lần.

Đây là nơi bạn cần bắt đầu suy nghĩ về:

```text
Update frequency
```

---

# 23. Ví dụ Search Box

```python
def on_change(e):
    search_text.value = e.control.value

    render()
    page.update()
```

Nếu user gõ:

```text
python
```

có thể có nhiều event.

```text
p
py
pyt
pyth
pytho
python
```

Nếu mỗi event đều gọi network:

```text
p     → API
py    → API
pyt   → API
pyth  → API
...
```

thì rất tệ.

Đây là lý do sau này ta cần:

```text
debounce
throttle
async
```

---

# 24. `page.update()` và async

Đây là tình huống cực kỳ thực tế.

Ví dụ:

```python
async def load_data(e):
    button.disabled = True
    status.value = "Loading..."

    page.update()

    data = await fetch_data()

    status.value = "Done"
    button.disabled = False

    page.update()
```

Có hai UI synchronization points:

```text
START
 ↓
Loading UI
 ↓
await
 ↓
Finish
 ↓
Final UI
```

---

# 25. Vì sao update trước `await`?

Nếu:

```python
button.disabled = True
status.value = "Loading..."
```

nhưng chưa sync:

```text
Python state
   ↓
await network
```

user có thể chưa thấy:

```text
Loading...
```

Bạn muốn:

```text
User click
 ↓
UI → Loading
 ↓
network
 ↓
UI → Done
```

Do đó:

```python
page.update()
await ...
```

là một pattern quan trọng.

---

# 26. Exception trong async handler

Ví dụ tốt hơn:

```python
async def load_data(e):

    button.disabled = True
    status.value = "Loading..."
    page.update()

    try:
        data = await fetch_data()

        status.value = "Success"

    except Exception:
        status.value = "Error"

    finally:
        button.disabled = False
        page.update()
```

Flow:

```text
CLICK
 ↓
LOADING
 ↓
await
 ├── SUCCESS
 └── ERROR
 ↓
FINAL UPDATE
```

---

# 27. Loading UI và update boundary

Một nguyên tắc rất thực tế:

```text
Before long operation:
    update UI

After long operation:
    update UI
```

Ví dụ:

```python
status.value = "Downloading..."
page.update()

await download()

status.value = "Downloaded"
page.update()
```

---

# 28. `page.update()` không block Python logic

Bạn cần phân biệt:

```python
page.update()
```

với:

```python
time.sleep(10)
```

Ví dụ:

```python
status.value = "Loading"
page.update()

time.sleep(10)

status.value = "Done"
page.update()
```

Nếu chạy trên UI/event context không phù hợp, `time.sleep()` có thể làm UI không phản hồi.

Vấn đề không phải `page.update()`.

Vấn đề là:

```text
blocking operation
```

Đây là lý do async rất quan trọng.

---

# 29. Batch mutation

Ví dụ:

```python
def success():

    title.value = "Success"
    status.value = "Completed"
    progress.value = 100
    button.disabled = False

    page.update()
```

Tư duy:

```text
4 UI mutations
        ↓
1 synchronization
```

Đây là pattern bạn nên sử dụng thường xuyên.

---

# 30. Stale UI

Một bug phổ biến:

```python
count += 1
```

nhưng:

```python
page.update()
```

không được gọi ở thời điểm cần thiết.

State:

```text
count = 5
```

UI:

```text
4
```

Ta gọi đây là:

```text
State/UI mismatch
```

---

# 31. Debug stale UI

Khi UI hiển thị sai, kiểm tra:

### Bước 1

State:

```python
print(count)
```

### Bước 2

Control:

```python
print(text.value)
```

### Bước 3

Update:

```python
page.update()
```

### Bước 4

Event:

```python
print("handler called")
```

Mental model:

```text
Event?
 ↓
State changed?
 ↓
Control changed?
 ↓
UI synced?
```

---

# 32. Một lỗi rất hay gặp

```python
def increment(e):
    count += 1
    text.value = str(count)
```

Nhưng không:

```python
page.update()
```

UI không phản ánh thay đổi.

---

# 33. Một lỗi khác

```python
def increment(e):
    text.value = str(count)
    count += 1
    page.update()
```

Thứ tự sai.

Nếu:

```text
count = 0
```

thì:

```python
text.value = "0"
count = 1
```

UI vẫn hiển thị:

```text
0
```

Bạn phải:

```python
count += 1
text.value = str(count)
page.update()
```

Flow:

```text
State
 ↓
Derived UI
 ↓
Sync
```

---

# 34. Một lỗi architecture khác

```python
def increment(e):
    count += 1
    text.value = str(count)
    page.update()

def decrement(e):
    count -= 1
    text.value = str(count)
    page.update()

def reset(e):
    count = 0
    text.value = str(count)
    page.update()
```

Ba handler đều chứa:

```text
State mutation
UI rendering
UI update
```

Với app lớn, duplication sẽ tăng.

---

# 35. Tách `render()`

Tốt hơn:

```python
def render():
    text.value = str(count)
```

Handler:

```python
def increment(e):
    nonlocal count
    count += 1

    render()
    page.update()
```

```python
def decrement(e):
    nonlocal count
    count -= 1

    render()
    page.update()
```

```python
def reset(e):
    nonlocal count
    count = 0

    render()
    page.update()
```

---

# 36. Tách `refresh()`

Bạn cũng có thể tạo:

```python
def refresh():
    render()
    page.update()
```

Sau đó:

```python
def increment(e):
    nonlocal count

    count += 1
    refresh()
```

Nhưng hãy cẩn thận.

`refresh()` nên có semantics rõ ràng:

```text
render + synchronize
```

để không gây hiểu nhầm.

---

# 37. Pattern hoàn chỉnh

```python
import flet as ft


def main(page: ft.Page):

    count = 0

    text = ft.Text(size=30)

    def render():
        text.value = str(count)

    def refresh():
        render()
        page.update()

    def increment(e):
        nonlocal count
        count += 1
        refresh()

    def decrement(e):
        nonlocal count
        count -= 1
        refresh()

    render()

    page.add(
        text,
        ft.Row(
            controls=[
                ft.Button("-", on_click=decrement),
                ft.Button("+", on_click=increment),
            ]
        ),
    )


ft.run(main)
```

---

# 38. `page.update()` và initial render

Một câu hỏi:

> Có cần `page.update()` sau `page.add()` không?

Trong code Flet thông thường, bạn dùng:

```python
page.add(...)
```

để thêm UI vào page.

Không nên máy móc viết:

```python
page.add(...)
page.update()
```

sau mọi `page.add()`.

Điều quan trọng là hiểu **khi nào bạn đang thực hiện mutation cần đồng bộ** và API nào đã thực hiện việc đó cho bạn.

---

# 39. Dynamic Controls

Ví dụ:

```python
list_view = ft.Column()

page.add(list_view)
```

Sau đó:

```python
list_view.controls.append(
    ft.Text("Item 1")
)

page.update()
```

Ta có:

```text
Page
└── Column
    └── Item 1
```

---

# 40. Dynamic list

```python
items = []

def add_item(e):

    items.append(
        ft.Text(f"Item {len(items) + 1}")
    )

    page.update()
```

Nhưng lưu ý:

```python
items
```

ở đây đang là UI controls.

Nếu muốn architecture tốt hơn, nên phân biệt:

```text
Data State
```

và:

```text
UI Controls
```

---

# 41. Data State vs Control Tree

Ví dụ:

```python
todos = [
    "Python",
    "Flet",
]
```

là data state.

Còn:

```python
todo_column.controls
```

là UI representation.

Không nên coi:

```python
todo_column.controls
```

là database của app.

Tốt hơn:

```text
todos
 ↓
render_todos()
 ↓
todo_column
```

---

# 42. Render list

```python
def render_todos():

    todo_column.controls.clear()

    for todo in todos:
        todo_column.controls.append(
            ft.Text(todo)
        )
```

Sau đó:

```python
def add_todo(e):
    todos.append("Learn Flet")

    render_todos()
    page.update()
```

Flow:

```text
todos
 ↓
render_todos()
 ↓
controls
 ↓
page.update()
```

Đây là pattern cực kỳ quan trọng.

---

# 43. Một điểm cần cẩn thận

Nếu mỗi lần render bạn:

```python
todo_column.controls.clear()
```

rồi tạo toàn bộ controls lại, thì với danh sách rất lớn có thể không tối ưu.

Ví dụ:

```text
10 items
```

không đáng lo.

Nhưng:

```text
100,000 items
```

thì cần kiến trúc khác.

Sau này chúng ta sẽ học:

```text
ListView
Lazy rendering
Virtualization
Pagination
```

---

# 44. `page.update()` và Performance

Đừng nghĩ:

```text
page.update()
```

càng nhiều càng tốt.

Cũng đừng nghĩ:

```text
page.update()
```

luôn là bottleneck.

Điều quan trọng là:

```text
How often?
How much changed?
How large is the UI?
What event frequency?
```

Ví dụ:

```text
Button click
→ update
```

hoàn toàn bình thường.

Nhưng:

```text
mouse movement
→ 60 updates/sec
→ rebuild 10,000 controls
```

có thể là vấn đề.

---

# 45. Event frequency table

| Event          |       Tần suất |
| -------------- | -------------: |
| Button click   |           Thấp |
| Form submit    |           Thấp |
| Text change    | Trung bình/cao |
| Keyboard event |            Cao |
| Mouse move     |        Rất cao |
| Timer          |   Tùy interval |
| Stream         | Có thể rất cao |

Vì vậy update strategy phải phụ thuộc event.

---

# 46. Debounce

Ví dụ search:

```text
User:
p
py
pyt
pyth
python
```

Không muốn:

```text
API
API
API
API
API
```

mà muốn:

```text
User stops typing
       ↓
wait 300ms
       ↓
API
```

Đó là:

> Debounce.

Đây là kiến thức chúng ta sẽ dùng khi xây app thực tế.

---

# 47. `page.update()` và component design

Nếu bạn có:

```text
Header
Sidebar
Content
Footer
```

đừng để mọi nơi gọi:

```python
page.update()
```

một cách tùy tiện.

Có thể thiết kế:

```text
App
 ├── Header
 ├── Sidebar
 └── Content
```

Mỗi component quản lý state/UI của nó.

App orchestration quản lý:

```text
Global state
Navigation
Cross-component updates
```

Đây là bước tiến tới architecture lớn.

---

# 48. Quy tắc thiết kế

Một handler tốt:

```python
def on_click(e):
    change_state()
    render()
    page.update()
```

Một handler xấu:

```python
def on_click(e):
    # state
    # database
    # HTTP
    # UI
    # validation
    # navigation
    # logging
    # 200 lines
```

---

# 49. Mental Model cuối cùng

Bạn nên ghi nhớ:

```text
              EVENT
                │
                ▼
        ┌───────────────┐
        │ State Change  │
        └───────┬───────┘
                │
                ▼
             RENDER
                │
                ▼
        Control properties
                │
                ▼
          page.update()
                │
                ▼
          Client/UI sync
```

`page.update()` nằm **cuối chuỗi**.

Nó không thay thế:

```text
State
Render
Event
Architecture
```

---

# 50. Mini Project — Counter chuẩn architecture

Đây là phiên bản bạn nên tự viết lại:

```python
import flet as ft


def main(page: ft.Page):

    count = 0

    counter = ft.Text(
        size=40,
    )

    def render():
        counter.value = str(count)

    def refresh():
        render()
        page.update()

    def increment(e):
        nonlocal count

        count += 1
        refresh()

    def decrement(e):
        nonlocal count

        count -= 1
        refresh()

    def reset(e):
        nonlocal count

        count = 0
        refresh()

    render()

    page.add(
        counter,

        ft.Row(
            controls=[
                ft.Button(
                    "-",
                    on_click=decrement,
                ),
                ft.Button(
                    "Reset",
                    on_click=reset,
                ),
                ft.Button(
                    "+",
                    on_click=increment,
                ),
            ]
        ),
    )


ft.run(main)
```

Architecture:

```text
             count
               │
               ▼
            render()
               │
               ▼
           counter
               │
               ▼
         page.update()
```

---

# 51. Bài tập Buổi 9

## Bài 1 — Counter

Viết Counter có:

```text
[ - ] [ Reset ] [ + ]

       10
```

State:

```python
count
```

Không được dùng:

```python
counter.value
```

làm source of truth.

---

## Bài 2 — Todo

State:

```python
todos = []
```

UI:

```text
Todo: 2

□ Learn Python
□ Learn Flet

[Input................] [Add]
```

Flow:

```text
Add
 ↓
todos.append()
 ↓
render_todos()
 ↓
page.update()
```

---

## Bài 3 — Loading

State:

```python
status = "idle"
```

Có 4 trạng thái:

```text
idle
loading
success
error
```

UI phải phụ thuộc vào:

```python
status
```

không được tạo:

```python
is_loading
is_success
is_error
```

đồng thời.

---

## Bài 4 — Deep Dive

Hãy thử tạo:

```text
[ Add ]
```

Mỗi click:

```text
State:
items = [...]
```

UI:

```text
Item 1
Item 2
Item 3
...
```

Yêu cầu:

```text
Data State
    ↓
render_items()
    ↓
Column
    ↓
page.update()
```

**Không được lấy `column.controls` làm nguồn dữ liệu chính.**

---

# 52. Những gì bạn cần nhớ sau Buổi 9

### `page.update()`

```python
page.update()
```

= đồng bộ thay đổi UI với client.

### State

```python
count += 1
```

= thay đổi dữ liệu.

### Render

```python
text.value = str(count)
```

= chuyển state thành UI representation.

### Update

```python
page.update()
```

= sync.

Và pattern:

```text
EVENT
  ↓
STATE
  ↓
RENDER
  ↓
UPDATE
```

Đây là **4 tầng tư duy nền tảng** mà bạn sẽ sử dụng xuyên suốt quá trình học Flet.

---

# Roadmap

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
08. State cơ bản                             ✅
09. page.update() deep dive                 ← hiện tại
10. Mini Project: Todo App
```

**Buổi 10 sẽ là Mini Project — Todo App**, nhưng chúng ta sẽ không làm kiểu "viết một file 200 dòng". Ta sẽ xây Todo App **từng bước theo kiến trúc `State → Event → Render → Update`**, sau đó mở rộng thêm validation, checkbox, delete, filter và tổ chức code thành các phần rõ ràng.
