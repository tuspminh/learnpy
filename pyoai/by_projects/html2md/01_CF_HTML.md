# Buổi 1 — Windows Clipboard + CF_HTML

Mục tiêu hôm nay: **chưa dùng Flet, BeautifulSoup hay html2text**. Ta chỉ xây phần lõi để hiểu chính xác dữ liệu mà Chrome/Edge đưa vào Clipboard khi bạn `Ctrl+C`.

Sau buổi này, ta phải làm được:

```text
Chrome / Edge
    │
    │ Ctrl+C
    ▼
Windows Clipboard
    │
    ├── CF_UNICODETEXT
    │
    └── CF_HTML
          │
          ▼
     Python đọc được
          │
          ▼
     lấy HTML fragment
```

---

# 1. Tại sao không dùng `pyperclip`?

Nếu bạn làm:

```python
import pyperclip

text = pyperclip.paste()
print(text)
```

thì chủ yếu bạn nhận được **plain text**.

Trong khi chúng ta cần:

```html
<p>Hello <strong>world</strong></p>

<pre><code>
def hello():
    print("Hello")
</code></pre>
```

Bởi vì sau này chúng ta cần biết:

* đâu là heading
* đâu là paragraph
* đâu là link
* đâu là `<pre>`
* đâu là `<code>`
* đâu là inline code
* class nào chứa ngôn ngữ lập trình

Do đó phải đọc **HTML format** của Windows Clipboard.

---

# 2. Windows Clipboard có nhiều format

Khi bạn copy một đoạn HTML từ browser, clipboard không chỉ chứa một chuỗi.

Có thể có:

```text
CF_UNICODETEXT
CF_TEXT
CF_HTML
CF_BITMAP
...
```

Trong project này, chúng ta quan tâm nhất:

```text
CF_HTML
```

và dự phòng:

```text
CF_UNICODETEXT
```

Có thể hình dung:

```text
Clipboard
│
├── Unicode text
│     └── "Hello world"
│
└── HTML
      └── "<p>Hello <b>world</b></p>"
```

Đây chính là lý do app của chúng ta có thể lấy HTML thay vì chỉ lấy text.

---

# 3. Cài `pywin32`

Trên Windows:

```bash
pip install pywin32
```

Kiểm tra:

```bash
python -c "import win32clipboard; print('OK')"
```

Nếu thấy:

```text
OK
```

là được.

---

# 4. Tạo project

Hôm nay chỉ cần:

```text
clip2md/
│
├── src/
│   └── clip2md/
│       ├── __init__.py
│       ├── clipboard.py
│       └── main.py
│
└── tests/
```

Tạo:

```text
src/clip2md/clipboard.py
```

---

# 5. Mở Windows Clipboard

Code đầu tiên:

```python
import win32clipboard


def open_clipboard():
    win32clipboard.OpenClipboard()


def close_clipboard():
    win32clipboard.CloseClipboard()
```

Nhưng cách này chưa an toàn.

Nếu exception xảy ra:

```python
win32clipboard.OpenClipboard()

# lỗi ở đây

win32clipboard.CloseClipboard()
```

thì clipboard có thể không được đóng.

Ta sẽ dùng context manager ở phiên bản đơn giản:

```python
from contextlib import contextmanager

import win32clipboard


@contextmanager
def clipboard():
    win32clipboard.OpenClipboard()

    try:
        yield
    finally:
        win32clipboard.CloseClipboard()
```

Sử dụng:

```python
with clipboard():
    print("Clipboard opened")
```

Đây chính là tư duy mà bạn đã học khi làm Context Manager:

```text
enter
  ↓
work
  ↓
finally
  ↓
exit
```

---

# 6. Liệt kê các format trong Clipboard

Windows cung cấp:

```python
win32clipboard.EnumClipboardFormats()
```

Ta viết:

```python
import win32clipboard


def list_formats():
    formats = []

    with clipboard():
        fmt = 0

        while True:
            fmt = win32clipboard.EnumClipboardFormats(fmt)

            if fmt == 0:
                break

            formats.append(fmt)

    return formats
```

Nhưng số:

```text
13
49161
49301
...
```

không dễ đọc.

Ta cần tên format.

---

# 7. Đăng ký format CF_HTML

Điểm thú vị là `CF_HTML` không phải lúc nào cũng có một hằng số cố định kiểu:

```python
CF_HTML = 12345
```

Windows có thể đăng ký clipboard format:

```python
win32clipboard.RegisterClipboardFormat("HTML Format")
```

Do đó:

```python
CF_HTML = win32clipboard.RegisterClipboardFormat("HTML Format")
```

Sau đó:

```python
print(CF_HTML)
```

sẽ cho ra một số ID.

Ví dụ có thể là:

```text
49321
```

**Không được hard-code số này.**

---

# 8. Viết hàm lấy HTML

Tạo:

```python
HTML_FORMAT = win32clipboard.RegisterClipboardFormat("HTML Format")
```

Sau đó:

```python
def get_html():
    with clipboard():
        if not win32clipboard.IsClipboardFormatAvailable(HTML_FORMAT):
            return None

        data = win32clipboard.GetClipboardData(HTML_FORMAT)

        return data
```

Thử:

```python
html = get_html()

print(html)
```

---

# 9. Có thể gặp `bytes`

Đây là điểm cần chú ý.

Dữ liệu CF_HTML thường được trả về dưới dạng bytes hoặc dữ liệu có thể cần decode.

Ta không nên ngay lập tức làm:

```python
str(data)
```

vì có thể biến dữ liệu thành:

```text
b'Version:0.9...'
```

thay vì HTML thật.

Ta viết:

```python
def decode_html(data: bytes | str) -> str:
    if isinstance(data, str):
        return data

    return data.decode("utf-8", errors="replace")
```

---

# 10. Chương trình đầu tiên

`main.py`:

```python
from clip2md.clipboard import get_html


def main():
    html = get_html()

    if html is None:
        print("Clipboard không chứa HTML.")
        return

    print("===== RAW CF_HTML =====")
    print(html)


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python -m clip2md.main
```

---

# 11. Test với Chrome

Mở một trang web có:

```html
<h1>Python</h1>
<p>Xin chào <strong>Python</strong></p>
```

Chọn đoạn đó:

```text
Ctrl+C
```

Sau đó chạy:

```bash
python -m clip2md.main
```

Bạn có thể thấy dạng:

```text
Version:0.9
StartHTML:00000097
EndHTML:00000384
StartFragment:00000131
EndFragment:00000348
SourceURL:https://...

<html>
<body>
<!--StartFragment-->
<h1>Python</h1>
<p>Xin chào <strong>Python</strong></p>
<!--EndFragment-->
</body>
</html>
```

Đây chính là thứ chúng ta cần.

---

# 12. CF_HTML Metadata

Bây giờ hãy quan sát:

```text
Version:0.9
StartHTML:00000097
EndHTML:00000384
StartFragment:00000131
EndFragment:00000348
SourceURL:...
```

Đây **không phải nội dung HTML**.

Nó là metadata để Windows và ứng dụng khác biết:

```text
HTML bắt đầu ở byte nào?
HTML kết thúc ở byte nào?

Fragment bắt đầu ở byte nào?
Fragment kết thúc ở byte nào?
```

Đặc biệt:

```text
StartFragment
EndFragment
```

rất quan trọng với app của chúng ta.

---

# 13. Tại sao không đơn giản tìm `<html>`?

Ta có thể nghĩ:

```python
start = html.find("<html>")
```

Nhưng không nên.

Browser có thể đưa:

```html
<html>
<head>
...
</head>

<body>

<!--StartFragment-->

<p>Hello</p>

<!--EndFragment-->

</body>
</html>
```

Thứ chúng ta thực sự muốn thường là:

```html
<p>Hello</p>
```

chứ không cần:

```html
<html>
<head>
...
</head>
<body>
...
</body>
</html>
```

Vì vậy Windows đã cung cấp:

```text
StartFragment
EndFragment
```

cho chúng ta.

---

# 14. Bài tập quan trọng

Tạo hàm:

```python
def extract_fragment(raw_html: str) -> str:
    ...
```

Mục tiêu:

Input:

```text
Version:0.9
StartHTML:...
EndHTML:...
StartFragment:...
EndFragment:...

<html>
<body>
<!--StartFragment-->
<p>Hello</p>
<pre><code>print("hello")</code></pre>
<!--EndFragment-->
</body>
</html>
```

Output:

```html
<p>Hello</p>
<pre><code>print("hello")</code></pre>
```

---

# 15. Đừng dùng regex để parse byte offset một cách tùy tiện

Một lỗi phổ biến là:

```python
start = raw_html.find("<!--StartFragment-->")
end = raw_html.find("<!--EndFragment-->")
```

Cách này có thể dùng như fallback, nhưng **không nên là parser chính**.

Bởi vì CF_HTML header đã cung cấp:

```text
StartFragment
EndFragment
```

và các giá trị này là **byte offsets**.

Ví dụ:

```text
StartFragment:00000172
EndFragment:00000321
```

không nhất thiết là character index trong Python string.

Đây là lý do chúng ta phải xử lý:

```text
bytes
```

trước, rồi mới decode.

---

# 16. Parser đúng hướng

Kiến trúc:

```python
def extract_fragment(data: bytes) -> str:
    header = ...
    
    start = ...
    end = ...

    fragment = data[start:end]

    return fragment.decode(...)
```

Tức là:

```text
raw bytes
    │
    ▼
parse header
    │
    ▼
StartFragment
EndFragment
    │
    ▼
bytes[start:end]
    │
    ▼
decode UTF-8
    │
    ▼
HTML fragment
```

Đây sẽ là nội dung chính của **Buổi 2**.

---

# 17. Fallback Unicode text

Một app production không nên giả định clipboard lúc nào cũng có HTML.

Ví dụ user copy từ:

* Notepad
* terminal
* PDF
* một website không cung cấp HTML
* một ứng dụng desktop khác

thì có thể chỉ có:

```text
CF_UNICODETEXT
```

Ta viết:

```python
def get_text():
    with clipboard():
        if not win32clipboard.IsClipboardFormatAvailable(
            win32clipboard.CF_UNICODETEXT
        ):
            return None

        return win32clipboard.GetClipboardData(
            win32clipboard.CF_UNICODETEXT
        )
```

Sau này pipeline sẽ quyết định:

```text
Clipboard
    │
    ├── CF_HTML ?
    │      │
    │      └── YES → HTML pipeline
    │
    └── NO
           │
           ▼
       Unicode text
```

---

# 18. API mà chúng ta muốn đạt được

Sau Buổi 1, module `clipboard.py` nên hướng tới API:

```python
class ClipboardReader:

    def read_html(self) -> str | None:
        ...

    def read_text(self) -> str | None:
        ...

    def has_html(self) -> bool:
        ...

    def has_text(self) -> bool:
        ...
```

Sau này:

```python
reader = ClipboardReader()

html = reader.read_html()

if html:
    process(html)
```

UI Flet hoàn toàn không cần biết Windows Clipboard API hoạt động thế nào.

---

# 19. Bài tập Buổi 1

## Bài 1

Viết:

```python
list_formats()
```

và in ra các clipboard format hiện tại.

---

## Bài 2

Viết:

```python
get_text()
```

Test bằng cách copy:

```text
Hello Python
```

---

## Bài 3

Viết:

```python
get_html()
```

Test bằng Chrome/Edge.

---

## Bài 4 — quan trọng nhất

Copy đoạn:

```html
<h1>Python</h1>

<p>
    Học <strong>Python</strong>
    và dùng <code>print()</code>
</p>

<pre><code>
def hello():
    print("Hello")
</code></pre>
```

Sau đó quan sát **raw CF_HTML**.

Bạn cần xác định:

```text
Version
StartHTML
EndHTML
StartFragment
EndFragment
SourceURL
```

và tìm vị trí:

```text
<!--StartFragment-->
<!--EndFragment-->
```

---

# 20. Kết quả cuối Buổi 1

Kiến thức quan trọng nhất hôm nay không phải `pywin32`.

Mà là hiểu:

```text
Ctrl+C
   ↓
Windows Clipboard
   ↓
Clipboard có nhiều FORMAT
   ↓
CF_HTML
   ↓
CF_HTML header
   ↓
StartHTML / EndHTML
StartFragment / EndFragment
   ↓
HTML fragment
```

Và kiến trúc của app sẽ là:

```text
                 Clip2MD
                    │
          ┌─────────┴─────────┐
          │                   │
    Clipboard Layer       Flet UI
          │
          ▼
      CF_HTML
          │
          ▼
   HTML Fragment
          │
          ▼
    HTML Cleaner
          │
          ▼
     Markdown
          │
          ▼
      Clipboard
```

**Buổi 2** chúng ta sẽ tập trung hoàn toàn vào phần khó nhất của Clipboard: **viết một `CFHTMLParser` chuẩn để đọc header, xử lý byte offset, `StartFragment/EndFragment`, encoding và fallback khi browser tạo CF_HTML không chuẩn**. Đây sẽ là nền móng để sau đó BeautifulSoup nhận đúng HTML thay vì nhận cả metadata Windows.
