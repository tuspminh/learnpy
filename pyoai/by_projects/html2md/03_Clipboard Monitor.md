# Buổi 3 — Clipboard Monitor: phát hiện `Ctrl+C` và chống vòng lặp

Buổi 3 chúng ta bắt đầu biến app từ:

```text
đọc clipboard thủ công
```

thành:

```text
ứng dụng chạy nền
        │
        ▼
theo dõi Clipboard
        │
        ▼
phát hiện người dùng Ctrl+C
        │
        ▼
đọc CF_HTML
```

Điểm khó nhất hôm nay là **app tự ghi Clipboard cũng tạo ra một clipboard change**. Nếu không xử lý, app sẽ tự kích hoạt chính nó vô hạn.

---

# 1. Mục tiêu

Sau buổi này ta muốn có:

```python
monitor = ClipboardMonitor()

monitor.start()
```

và khi bạn:

```text
Chrome
   ↓
Ctrl+C
```

terminal xuất:

```text
Clipboard changed
HTML detected
```

Kiến trúc:

```text
                 Windows Clipboard
                        │
                        ▼
              ClipboardMonitor
                        │
                 change detected
                        │
                        ▼
               ClipboardReader
                        │
                        ▼
                   CF_HTML
                        │
                        ▼
                HTML fragment
```

---

# 2. Không nên dùng vòng lặp polling đơn giản?

Cách dễ nhất:

```python
while True:
    clipboard = read_clipboard()

    if clipboard != previous:
        process()

    time.sleep(0.5)
```

Có thể chạy, nhưng không phải thiết kế tốt nhất.

Nhược điểm:

* liên tục query Clipboard
* có độ trễ
* đọc Clipboard quá nhiều
* khó phân biệt thay đổi do app
* khó tích hợp UI/event system

Windows có cơ chế tốt hơn:

```text
Clipboard sequence number
```

---

# 3. Clipboard sequence number

Windows duy trì một số:

```text
Clipboard sequence number
```

Mỗi khi Clipboard thay đổi, số này tăng.

Ví dụ:

```text
100
```

sau người dùng copy:

```text
101
```

copy lần nữa:

```text
102
```

app ghi Clipboard:

```text
103
```

Ta chỉ cần nhớ:

```python
last_sequence
```

và kiểm tra:

```text
current_sequence != last_sequence
```

---

# 4. Lấy sequence number

Windows API:

```text
GetClipboardSequenceNumber
```

Với `pywin32`, ta có thể gọi:

```python
import win32clipboard


sequence = win32clipboard.GetClipboardSequenceNumber()
```

Thử:

```python
print(
    win32clipboard.GetClipboardSequenceNumber()
)
```

Sau đó copy một đoạn text.

Chạy lại:

```python
print(
    win32clipboard.GetClipboardSequenceNumber()
)
```

Bạn sẽ thấy số thay đổi.

---

# 5. Tạo `ClipboardMonitor`

Tạo:

```text
src/clip2md/monitor.py
```

Code cơ bản:

```python
import time

import win32clipboard


class ClipboardMonitor:

    def __init__(self):
        self._last_sequence = (
            win32clipboard.GetClipboardSequenceNumber()
        )

    def run(self):
        while True:
            current = (
                win32clipboard.GetClipboardSequenceNumber()
            )

            if current != self._last_sequence:
                self._last_sequence = current

                self.on_change()

            time.sleep(0.2)

    def on_change(self):
        print("Clipboard changed")
```

Chạy:

```python
monitor = ClipboardMonitor()
monitor.run()
```

---

# 6. Test

Chạy chương trình.

Ban đầu:

```text
waiting...
```

Copy text trên browser:

```text
Ctrl+C
```

Terminal:

```text
Clipboard changed
```

Copy lần nữa:

```text
Ctrl+C
```

lại:

```text
Clipboard changed
```

Đây chính là event đầu tiên của app.

---

# 7. Nhưng `time.sleep()` có vấn đề

Code:

```python
while True:
    ...
    time.sleep(0.2)
```

có nghĩa:

```text
CPU
 │
 ├── kiểm tra
 │
 ├── ngủ 200ms
 │
 ├── kiểm tra
 │
 ├── ngủ 200ms
 │
 └── ...
```

Với app nhỏ có thể chấp nhận.

Nhưng app production nên dùng Windows notification mechanism:

```text
AddClipboardFormatListener
```

Windows có thể thông báo:

```text
WM_CLIPBOARDUPDATE
```

khi Clipboard thay đổi.

Kiến trúc tốt hơn:

```text
Windows
   │
   │ WM_CLIPBOARDUPDATE
   ▼
Hidden Window
   │
   ▼
ClipboardMonitor
   │
   ▼
callback
```

Đây sẽ là phần nâng cao trong cuối Buổi 3.

Trước hết chúng ta dùng sequence number để hiểu concept.

---

# 8. Monitor không nên biết HTML

Một lỗi kiến trúc là:

```python
class ClipboardMonitor:

    def run(self):
        ...

        html = read_html()
        ...
```

Không nên.

`ClipboardMonitor` chỉ nên biết:

> Clipboard thay đổi.

Nó không cần biết:

* HTML là gì
* Markdown là gì
* BeautifulSoup là gì
* code block là gì

Ta dùng callback.

---

# 9. Callback

Thiết kế:

```python
class ClipboardMonitor:

    def __init__(self, on_change):
        self.on_change = on_change
```

Khi phát hiện:

```python
self.on_change()
```

Sử dụng:

```python
def handle_clipboard():
    print("Clipboard changed!")


monitor = ClipboardMonitor(
    on_change=handle_clipboard
)

monitor.run()
```

Pipeline:

```text
ClipboardMonitor
       │
       │ event
       ▼
 on_change()
       │
       ▼
 ClipboardReader
```

---

# 10. Typing cho callback

Vì bạn đang học Python chuyên sâu, nên từ đầu chúng ta thiết kế type rõ ràng:

```python
from collections.abc import Callable


Callback = Callable[[], None]
```

Sau đó:

```python
class ClipboardMonitor:

    def __init__(
        self,
        on_change: Callback,
    ):
        self._on_change = on_change
```

---

# 11. Thêm `stop()`

Một vòng lặp vô hạn:

```python
while True:
```

không tốt.

Ta cần:

```python
monitor.stop()
```

Thiết kế:

```python
class ClipboardMonitor:

    def __init__(self, on_change):
        self._on_change = on_change
        self._running = False

    def start(self):
        self._running = True

        while self._running:
            ...

    def stop(self):
        self._running = False
```

Bây giờ:

```text
start()
  │
  ▼
running = True
  │
  ▼
monitor loop
  │
  ▼
stop()
  │
  ▼
running = False
  │
  ▼
exit
```

---

# 12. Thêm `poll_interval`

Không hard-code:

```python
time.sleep(0.2)
```

Ta dùng:

```python
class ClipboardMonitor:

    def __init__(
        self,
        on_change,
        poll_interval: float = 0.2,
    ):
        self._on_change = on_change
        self._poll_interval = poll_interval
        self._running = False
```

Sau đó:

```python
time.sleep(self._poll_interval)
```

---

# 13. Phiên bản hoàn chỉnh đầu tiên

```python
import time
from collections.abc import Callable

import win32clipboard


Callback = Callable[[], None]


class ClipboardMonitor:

    def __init__(
        self,
        on_change: Callback,
        poll_interval: float = 0.2,
    ):
        self._on_change = on_change
        self._poll_interval = poll_interval

        self._last_sequence = (
            win32clipboard.GetClipboardSequenceNumber()
        )

        self._running = False

    def start(self) -> None:
        self._running = True

        while self._running:
            self._check()

            time.sleep(
                self._poll_interval
            )

    def stop(self) -> None:
        self._running = False

    def _check(self) -> None:
        current = (
            win32clipboard.GetClipboardSequenceNumber()
        )

        if current == self._last_sequence:
            return

        self._last_sequence = current

        self._on_change()
```

---

# 14. Test monitor

```python
from clip2md.monitor import ClipboardMonitor


def handle_change():
    print("Clipboard changed")


monitor = ClipboardMonitor(
    on_change=handle_change,
)

monitor.start()
```

Copy:

```text
Hello
```

Kết quả:

```text
Clipboard changed
```

Copy:

```text
Python
```

Kết quả:

```text
Clipboard changed
Clipboard changed
```

---

# 15. Kết nối `ClipboardReader`

Bây giờ:

```python
from clip2md.clipboard import ClipboardReader
from clip2md.monitor import ClipboardMonitor


reader = ClipboardReader()


def handle_change():
    html = reader.read_html()

    if html is None:
        print("No HTML")

        return

    print("===== HTML =====")
    print(html)


monitor = ClipboardMonitor(
    on_change=handle_change,
)

monitor.start()
```

Pipeline:

```text
Ctrl+C
  │
  ▼
sequence changed
  │
  ▼
handle_change()
  │
  ▼
read_html()
  │
  ▼
CFHTMLParser
  │
  ▼
HTML fragment
```

---

# 16. Vấn đề cực kỳ quan trọng: Clipboard tự thay đổi

Giả sử sau này chúng ta có:

```python
def handle_change():
    html = reader.read_html()

    markdown = convert(html)

    writer.write(markdown)
```

`writer.write(markdown)` sẽ làm:

```text
Clipboard sequence

100
 ↓
User Ctrl+C
 ↓
101
 ↓
App detects
 ↓
App writes Markdown
 ↓
102
```

Monitor thấy:

```text
102 != 101
```

và gọi:

```python
handle_change()
```

lần nữa.

Kết quả:

```text
101 → app process
102 → app process
103 → app process
104 → app process
...
```

Đây là **self-triggering loop**.

---

# 17. Giải pháp 1 — Ignore next change

Có thể làm:

```python
class ClipboardMonitor:

    def __init__(self, ...):
        self._ignore_next = False
```

Khi app sắp ghi:

```python
monitor.ignore_next_change()
```

Sau đó:

```python
if self._ignore_next:
    self._ignore_next = False
    return
```

Nhưng cách này có vấn đề.

Ví dụ:

```text
App đang ghi Clipboard
      │
      ├── sequence 101
      │
User Ctrl+C rất nhanh
      │
      └── sequence 102
```

`ignore_next` có thể bỏ nhầm clipboard của user.

Do đó không nên dựa hoàn toàn vào flag.

---

# 18. Giải pháp tốt hơn — theo dõi sequence

Ta cần biết:

```text
sequence nào do app tạo
```

Ví dụ:

```python
self._last_written_sequence
```

Sau khi ghi Clipboard:

```text
current sequence = 102
```

Ta lưu:

```python
self._last_written_sequence = 102
```

Monitor:

```python
if current == self._last_written_sequence:
    return
```

Như vậy:

```text
User Ctrl+C
    ↓
101
    ↓
process
    ↓
App writes
    ↓
102
    ↓
ignore 102
```

---

# 19. Nhưng vẫn còn một race condition

Có một vấn đề:

```text
App ghi Clipboard
      ↓
GetClipboardSequenceNumber()
```

có thể có thay đổi khác xảy ra giữa hai thao tác.

Do đó một thiết kế tốt hơn là `ClipboardWriter` trả về sequence sau khi ghi.

Ví dụ:

```python
class ClipboardWriter:

    def write_text(self, text: str) -> int:
        ...
        return (
            win32clipboard.GetClipboardSequenceNumber()
        )
```

Sau đó pipeline:

```python
sequence = writer.write_text(markdown)

monitor.mark_self_change(sequence)
```

---

# 20. `ClipboardWriter`

Tạo:

```text
src/clip2md/writer.py
```

```python
import win32clipboard


class ClipboardWriter:

    def write_text(self, text: str) -> int:
        win32clipboard.OpenClipboard()

        try:
            win32clipboard.EmptyClipboard()

            win32clipboard.SetClipboardData(
                win32clipboard.CF_UNICODETEXT,
                text,
            )

        finally:
            win32clipboard.CloseClipboard()

        return (
            win32clipboard.GetClipboardSequenceNumber()
        )
```

---

# 21. Monitor hỗ trợ self-change

```python
class ClipboardMonitor:

    def __init__(
        self,
        on_change,
        poll_interval: float = 0.2,
    ):
        self._on_change = on_change
        self._poll_interval = poll_interval

        self._last_sequence = (
            win32clipboard.GetClipboardSequenceNumber()
        )

        self._self_sequences: set[int] = set()

        self._running = False

    def mark_self_change(
        self,
        sequence: int,
    ) -> None:
        self._self_sequences.add(sequence)
```

Trong `_check()`:

```python
def _check(self):
    current = (
        win32clipboard.GetClipboardSequenceNumber()
    )

    if current == self._last_sequence:
        return

    self._last_sequence = current

    if current in self._self_sequences:
        self._self_sequences.remove(current)

        return

    self._on_change()
```

---

# 22. Vì sao dùng `set`?

Ta có:

```python
self._self_sequences: set[int]
```

thay vì:

```python
self._self_sequence: int | None
```

vì trong tương lai pipeline có thể bất đồng bộ.

Có thể xảy ra:

```text
App write #1 → sequence 101
App write #2 → sequence 102
```

trước khi monitor xử lý event.

Set cho phép:

```text
{101, 102}
```

và xử lý chính xác.

---

# 23. Tuy nhiên sequence number không phải identity tuyệt đối

Đây là điểm kiến trúc quan trọng.

Sequence number chỉ nói:

> Clipboard đã thay đổi.

Nó không nói:

> Ai thay đổi Clipboard?

Vì vậy ta vẫn cần:

```text
self-generated sequence
```

để phối hợp giữa Writer và Monitor.

---

# 24. Thiết kế tốt hơn: `ClipboardEvent`

Thay vì callback:

```python
Callable[[], None]
```

ta có thể truyền event:

```python
from dataclasses import dataclass


@dataclass(slots=True)
class ClipboardEvent:
    sequence: int
```

Callback:

```python
Callable[[ClipboardEvent], None]
```

Sau đó:

```python
event = ClipboardEvent(
    sequence=current,
)

self._on_change(event)
```

Handler:

```python
def handle_change(event: ClipboardEvent):
    print(
        "Clipboard changed:",
        event.sequence,
    )
```

Sau này ta có thể thêm:

```python
@dataclass(slots=True)
class ClipboardEvent:
    sequence: int
    has_html: bool
    has_text: bool
```

Nhưng hiện tại chỉ cần `sequence`.

---

# 25. Trạng thái monitor

Ta có thể hình dung:

```text
                  ┌────────────┐
                  │   STOPPED  │
                  └─────┬──────┘
                        │ start()
                        ▼
                  ┌────────────┐
             ┌───►│   RUNNING  │
             │    └─────┬──────┘
             │          │
             │          │ change
             │          ▼
             │    ┌────────────┐
             │    │  CALLBACK  │
             │    └─────┬──────┘
             │          │
             └──────────┘
                        │
                        │ stop()
                        ▼
                  ┌────────────┐
                  │   STOPPED  │
                  └────────────┘
```

Đây chính là state machine nhỏ.

---

# 26. Một vấn đề nữa: callback có thể làm app chết

Nếu:

```python
self._on_change()
```

ném exception:

```python
ValueError
```

thì:

```text
monitor loop
     ↓
callback
     ↓
exception
     ↓
program chết
```

Không tốt.

Ta có thể bảo vệ:

```python
def _check(self):
    ...
    
    try:
        self._on_change()
    except Exception as exc:
        print(
            f"Clipboard callback failed: {exc}"
        )
```

Sau này chúng ta sẽ thay `print()` bằng `logging`.

---

# 27. Một thiết kế hoàn chỉnh hơn

```python
import time
from collections.abc import Callable

import win32clipboard


class ClipboardMonitor:

    def __init__(
        self,
        on_change: Callable[[int], None],
        poll_interval: float = 0.2,
    ):
        self._on_change = on_change
        self._poll_interval = poll_interval

        self._last_sequence = (
            win32clipboard.GetClipboardSequenceNumber()
        )

        self._self_sequences: set[int] = set()

        self._running = False

    def start(self) -> None:
        if self._running:
            return

        self._running = True

        while self._running:
            self._check()

            time.sleep(
                self._poll_interval
            )

    def stop(self) -> None:
        self._running = False

    def mark_self_change(
        self,
        sequence: int,
    ) -> None:
        self._self_sequences.add(sequence)

    def _check(self) -> None:
        current = (
            win32clipboard.GetClipboardSequenceNumber()
        )

        if current == self._last_sequence:
            return

        self._last_sequence = current

        if current in self._self_sequences:
            self._self_sequences.remove(current)

            return

        try:
            self._on_change(current)

        except Exception as exc:
            print(
                f"Clipboard callback failed: {exc}"
            )
```

Đây là một phiên bản đủ tốt để chúng ta tiếp tục xây project.

---

# 28. Test self-change

Giả sử:

```python
monitor = ClipboardMonitor(
    on_change=lambda seq: print(
        "USER CHANGE:",
        seq,
    )
)

writer = ClipboardWriter()
```

Khi app ghi:

```python
sequence = writer.write_text(
    "# Hello"
)

monitor.mark_self_change(sequence)
```

Monitor sẽ thấy sequence đó nhưng:

```text
self sequence
    ↓
ignore
```

Nếu user sau đó:

```text
Ctrl+C
```

sẽ có sequence mới:

```text
102
```

không nằm trong:

```python
_self_sequences
```

nên:

```text
USER CHANGE: 102
```

---

# 29. Bây giờ ghép thành Pipeline mini

Chưa cần BeautifulSoup.

```python
from clip2md.clipboard import ClipboardReader
from clip2md.monitor import ClipboardMonitor


reader = ClipboardReader()


def handle_clipboard(sequence: int):
    html = reader.read_html()

    if html is None:
        print("Clipboard không có HTML")

        return

    print("=" * 60)
    print("Sequence:", sequence)
    print("HTML:")
    print(html)
    print("=" * 60)


monitor = ClipboardMonitor(
    on_change=handle_clipboard,
)

monitor.start()
```

Khi copy từ Chrome:

```text
============================================================
Sequence: 421
HTML:

<h1>Python</h1>
<p>Hello <strong>world</strong></p>

============================================================
```

---

# 30. Một vấn đề thực tế: Copy text không phải HTML

Ví dụ copy từ Notepad:

```text
hello python
```

Clipboard thay đổi.

Monitor gọi:

```python
reader.read_html()
```

trả:

```python
None
```

Đây là hành vi đúng.

Sau này pipeline sẽ:

```text
Clipboard changed
       │
       ▼
has HTML?
   ┌───┴───┐
  YES      NO
   │        │
   ▼        ▼
HTML      ignore
```

Tức app của chúng ta **chỉ hoạt động khi clipboard có HTML**.

---

# 31. Tại sao chưa nên chuyển sang Flet?

Nếu đưa Flet vào ngay:

```text
Flet
 │
 ├── UI
 ├── clipboard
 ├── parser
 ├── event loop
 └── processing
```

chúng ta sẽ có một đống vấn đề:

* Flet event loop
* thread
* blocking
* Windows message loop
* UI update
* clipboard API

trộn lẫn với nhau.

Thay vào đó:

```text
             CORE
              │
     ┌────────┼─────────┐
     │        │         │
 Clipboard  Parser   Pipeline
     │
     ▼
   Monitor
              │
              ▼
            Flet
```

UI chỉ quan sát core.

Đây là kiến trúc tốt hơn.

---

# 32. Bài tập Buổi 3

### Bài 1

Viết `ClipboardMonitor` sử dụng:

```python
GetClipboardSequenceNumber()
```

và phát hiện:

```text
Ctrl+C
```

---

### Bài 2

Thêm:

```python
start()
stop()
```

---

### Bài 3

Thêm callback:

```python
on_change(sequence)
```

---

### Bài 4

Kết nối:

```text
Monitor
   ↓
ClipboardReader
   ↓
CFHTMLParser
```

Khi copy HTML, in fragment.

---

### Bài 5 — quan trọng

Viết:

```python
ClipboardWriter
```

và chứng minh rằng:

```text
user copy
   ↓
monitor
   ↓
writer
   ↓
clipboard changed
```

**không tạo vòng lặp vô hạn**.

---

# 33. Bài tập nâng cao

Thử mô phỏng:

```text
User Ctrl+C
     ↓
sequence 100
     ↓
App nhận
     ↓
App ghi sequence 101
     ↓
App ghi tiếp sequence 102
     ↓
User Ctrl+C sequence 103
```

Monitor phải:

```text
100 → process
101 → ignore
102 → ignore
103 → process
```

Nếu làm được bài này, cơ chế event của chúng ta khá chắc.

---

# 34. Kiến trúc hiện tại

Sau 3 buổi:

```text
┌───────────────────────────────┐
│        Windows Clipboard      │
└───────────────┬───────────────┘
                │
                ▼
       ClipboardMonitor
                │
                │ sequence
                ▼
       ClipboardReader
                │
                ▼
           CF_HTML
                │
                ▼
         CFHTMLParser
                │
                ▼
         HTML Fragment
```

Và chúng ta đã giải quyết được 3 vấn đề nền tảng:

```text
1. Đọc CF_HTML
2. Loại metadata Windows
3. Theo dõi Clipboard + chống self-trigger
```

---

## Bước tiếp theo — Buổi 4

Đây mới là lúc chúng ta bắt đầu **BeautifulSoup**.

Chúng ta sẽ xây:

```text
HTML Fragment
      │
      ▼
BeautifulSoup
      │
      ▼
HTML Cleaner
      │
      ├── remove script
      ├── remove style
      ├── remove iframe
      ├── remove svg
      ├── remove comments
      ├── remove hidden elements
      └── giữ nguyên pre/code
              │
              ▼
        Clean HTML
```

Đặc biệt, Buổi 4 sẽ thiết kế `HTMLCleaner` theo kiểu **rule/policy**, thay vì viết một hàm `clean_html()` khổng lồ. Điều này rất quan trọng vì sau này ta sẽ cần xử lý hàng loạt website có cấu trúc quảng cáo khác nhau.
