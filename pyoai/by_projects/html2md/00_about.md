Được. Bài toán này rất phù hợp để làm thành một **Windows desktop utility chạy nền**, Flet chỉ đảm nhiệm UI, còn phần bắt clipboard và xử lý HTML là một core service độc lập.

Mình đề xuất không làm tất cả trong `main.py`, mà xây theo kiến trúc có thể mở rộng thành một app hoàn chỉnh.

## 1. Kiến trúc app

Luồng chính:

```text
┌──────────────────────┐
│      Web Browser     │
│ Chrome / Edge / FF   │
└──────────┬───────────┘
           │ Ctrl+C
           ▼
┌──────────────────────┐
│   Windows Clipboard  │
│                      │
│ CF_HTML              │
│ CF_UNICODETEXT       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────┐
│      Clipboard Monitor       │
│                              │
│ phát hiện clipboard thay đổi  │
└────────────┬─────────────────┘
             │
             ▼
┌──────────────────────────────┐
│       HTML Extractor         │
│                              │
│ bỏ Windows CF_HTML metadata  │
│ lấy phần HTML thực sự         │
└────────────┬─────────────────┘
             │
             ▼
┌──────────────────────────────┐
│       HTML Cleaner           │
│        BeautifulSoup         │
│                              │
│ remove:                      │
│ script / style / iframe      │
│ ads / tracking / navigation  │
│ class/id rác                 │
│ comments                     │
└────────────┬─────────────────┘
             │
             ▼
┌──────────────────────────────┐
│      Markdown Converter      │
│          html2text            │
│                              │
│ text                         │
│ heading                      │
│ link                         │
│ image                        │
│ ul / ol                      │
│ blockquote                   │
│                              │
│ ĐẶC BIỆT:                    │
│ <pre>                        │
│ <code>                       │
│ inline code                  │
└────────────┬─────────────────┘
             │
             ▼
┌──────────────────────────────┐
│      Markdown Clipboard      │
│                              │
│ ghi Markdown trở lại Windows │
└────────────┬─────────────────┘
             │
             ▼
       Ctrl+V ở đâu cũng được
```

Flet hiện có `page.window.always_on_top`, nên phần UI có thể luôn nằm trên các cửa sổ khác; đây là API desktop chính thức hiện tại. ([Flet][1])

---

# 2. Một điểm rất quan trọng: Clipboard Windows

Không nên dùng:

```python
pyperclip.copy(...)
```

cho phần **input HTML**.

Vì khi bạn copy từ Chrome/Edge, clipboard có thể chứa nhiều format:

```text
CF_UNICODETEXT
CF_TEXT
CF_HTML
CF_BITMAP
...
```

Trong đó chúng ta đặc biệt quan tâm:

```text
CF_HTML
```

Ví dụ clipboard HTML thực tế có thể trông gần như:

```text
Version:0.9
StartHTML:00000105
EndHTML:00000842
StartFragment:00000172
EndFragment:00000791
SourceURL:https://example.com/article

<html>
<body>
<!--StartFragment-->
<h1>Hello</h1>
<p>...</p>
<pre><code>print("hello")</code></pre>
<!--EndFragment-->
</body>
</html>
```

Phần:

```text
Version
StartHTML
EndHTML
StartFragment
EndFragment
SourceURL
```

là **CF_HTML metadata của Windows**.

Ta không đưa trực tiếp toàn bộ chuỗi đó vào BeautifulSoup.

Thay vào đó:

```text
CF_HTML
   │
   ▼
parse header
   │
   ▼
StartFragment
EndFragment
   │
   ▼
HTML fragment
```

Đây sẽ là một module riêng:

```text
clipboard/
    html_format.py
```

---

# 3. BeautifulSoup và html2text không nên gộp thành một hàm

Ta nên chia pipeline:

```text
raw clipboard
      ↓
extract HTML
      ↓
parse HTML
      ↓
clean HTML
      ↓
normalize HTML
      ↓
protect code
      ↓
html2text
      ↓
restore code
      ↓
Markdown
```

Điều này rất quan trọng.

Ví dụ:

```html
<p>Đây là ví dụ:</p>

<pre><code>def hello():
    print("hello")
</code></pre>
```

Ta muốn kết quả:

````markdown
Đây là ví dụ:

```python
def hello():
    print("hello")
```
````

Còn:

```html
<p>Gọi hàm <code>hello()</code> để chạy.</p>
```

phải thành:

```markdown
Gọi hàm `hello()` để chạy.
```

---

# 4. Những tag cần xử lý

BeautifulSoup có thể loại bỏ những thứ kiểu:

```python
REMOVE_TAGS = {
    "script",
    "style",
    "noscript",
    "iframe",
    "canvas",
    "svg",
    "form",
    "button",
    "input",
    "textarea",
    "select",
}
```

Nhưng **không nên xóa `<pre>` và `<code>`**.

Đây là nguyên tắc rất quan trọng của app.

Ta có thể có:

```text
<pre>
<code>
</code>
</pre>
```

và:

```text
<code>
```

riêng lẻ.

---

# 5. Xử lý quảng cáo

Không thể chỉ dựa vào tag.

Ví dụ website có:

```html
<div class="article">
    ...
</div>

<div class="advertisement">
    ...
</div>
```

Ta cần nhận diện:

```text
ad
ads
advertisement
advert
banner
sponsor
sponsored
popup
modal
cookie
tracking
social-share
newsletter
related
recommendation
```

dựa trên:

```text
id
class
role
aria-label
```

Ví dụ:

```python
AD_KEYWORDS = {
    "ad",
    "ads",
    "advert",
    "advertisement",
    "banner",
    "sponsor",
    "sponsored",
    "popup",
    "modal",
    "cookie",
    "newsletter",
}
```

Sau đó:

```python
def looks_like_ad(tag):
    ...
```

Tuy nhiên mình **không khuyến khích xóa tất cả element có chữ `related`** ngay từ đầu.

Ví dụ:

```html
<div class="related-concept">
```

có thể là nội dung bài viết.

Ta sẽ xây một `CleaningPolicy` sau này.

---

# 6. Code phải được ưu tiên bảo toàn

Đây sẽ là một trong những phần quan trọng nhất của project.

Ví dụ:

```html
<pre class="language-python"><code>
def add(a, b):
    return a + b
</code></pre>
```

Ta phải cố gắng giữ:

```text
language-python
```

để sau này sinh:

````markdown
```python
def add(a, b):
    return a + b
```
````

Các class phổ biến:

```text
language-python
language-javascript
language-js
language-typescript
language-ts
language-rust
language-go
language-java
language-cpp
language-c
language-bash
language-sql
language-json
language-html
language-css
```

có thể được nhận diện.

---

# 7. Cấu trúc project mình đề xuất

Mình muốn chúng ta xây app theo kiểu này:

```text
clipboard_markdown/
│
├── pyproject.toml
│
├── src/
│   └── clipboard_markdown/
│       │
│       ├── __init__.py
│       ├── __main__.py
│       │
│       ├── app.py
│       │
│       ├── clipboard/
│       │   ├── __init__.py
│       │   ├── monitor.py
│       │   ├── windows.py
│       │   └── html_format.py
│       │
│       ├── cleaner/
│       │   ├── __init__.py
│       │   ├── cleaner.py
│       │   ├── rules.py
│       │   └── policy.py
│       │
│       ├── converter/
│       │   ├── __init__.py
│       │   ├── markdown.py
│       │   └── code.py
│       │
│       ├── pipeline/
│       │   ├── __init__.py
│       │   └── processor.py
│       │
│       └── ui/
│           ├── __init__.py
│           ├── main_view.py
│           └── state.py
│
└── tests/
    ├── test_html_format.py
    ├── test_cleaner.py
    ├── test_converter.py
    └── test_pipeline.py
```

Đây cũng rất hợp với cách bạn đang học các kiến trúc Python trước đây: **tách core logic khỏi UI**.

---

# 8. Các dependency

Ban đầu:

```bash
pip install flet beautifulsoup4 html2text pywin32
```

Có thể thêm:

```bash
pip install lxml
```

để BeautifulSoup parse HTML nhanh hơn.

`pywin32` phụ trách Windows Clipboard API.

Flet hiện hỗ trợ chạy desktop native bằng `flet run`, nên app này không cần dựng web server riêng. ([Flet][2])

---

# 9. UI mình đề xuất

App không cần cửa sổ lớn.

Ví dụ:

```text
┌────────────────────────────────┐
│ Clipboard Markdown       ─ □ × │
├────────────────────────────────┤
│                                │
│       ● WORKING                │
│                                │
│       [ ON / OFF ]             │
│                                │
│ Last action:                   │
│ Chrome → Markdown              │
│                                │
│ Removed: 12 elements           │
│ Markdown: 4.2 KB               │
│                                │
│ Last processed:                │
│ 23:41:08                       │
│                                │
└────────────────────────────────┘
```

Có thể làm thêm:

```text
[● WORKING]
```

khi bật.

Khi tắt:

```text
[○ PAUSED]
```

---

# 10. Trạng thái app

Mình đề xuất state:

```python
class AppState:
    enabled: bool
    processing: bool
    last_source: str | None
    last_error: str | None
    processed_count: int
    removed_count: int
```

Và pipeline:

```text
IDLE
 │
 │ clipboard changed
 ▼
DETECTING
 │
 ▼
READING_HTML
 │
 ▼
CLEANING
 │
 ▼
CONVERTING
 │
 ▼
WRITING_CLIPBOARD
 │
 ▼
DONE
```

Nếu lỗi:

```text
ERROR
```

---

# 11. Vấn đề cực kỳ quan trọng: vòng lặp clipboard

Đây là bug lớn nhất mà chúng ta phải thiết kế ngay từ đầu.

Ví dụ:

```text
User Ctrl+C
      ↓
App phát hiện
      ↓
App xử lý
      ↓
App ghi Markdown vào Clipboard
      ↓
Clipboard thay đổi
      ↓
App phát hiện lại
      ↓
App xử lý Markdown
      ↓
App ghi lại Clipboard
      ↓
...
```

→ **infinite loop**.

Do đó `ClipboardMonitor` phải phân biệt:

```text
external clipboard change
```

và:

```text
clipboard change do chính app tạo
```

Có thể sử dụng:

```python
sequence_number
```

cùng với:

```python
ignore_next_change = True
```

nhưng tốt hơn nữa là thiết kế:

```text
last_seen_sequence
last_written_sequence
```

---

# 12. Chế độ hoạt động

App của chúng ta có thể có 3 mode:

### OFF

```text
Clipboard → không làm gì
```

### ON

```text
Ctrl+C HTML
    ↓
HTML → Clean → Markdown
    ↓
Clipboard
```

### DEBUG

Sau này có thể thêm:

```text
Ctrl+C
 ↓
hiển thị:
- raw CF_HTML
- extracted HTML
- cleaned HTML
- Markdown
```

Mode DEBUG cực kỳ hữu ích khi chúng ta gặp website có HTML kỳ quặc.

---

# 13. Một nâng cấp rất đáng làm

Sau phiên bản đầu tiên, app có thể hỗ trợ:

```text
Ctrl+C
```

→ tự động chuyển.

Nhưng đồng thời có:

```text
[ Process clipboard now ]
```

để người dùng có thể xử lý thủ công.

Và:

```text
[ Copy raw HTML ]
```

```text
[ Copy cleaned HTML ]
```

```text
[ Copy Markdown ]
```

để debug.

---

# 14. Roadmap chúng ta sẽ học và xây

Mình đề xuất làm thành **khóa học + project thực tế**, từng buổi hoàn thiện một phần.

### Phase I — Windows Clipboard

**Buổi 1**

* Kiến trúc project
* Flet desktop
* Windows Clipboard
* CF_UNICODETEXT
* CF_HTML
* đọc HTML từ clipboard

**Buổi 2**

* CF_HTML format
* `StartHTML`
* `EndHTML`
* `StartFragment`
* `EndFragment`
* parser metadata Windows
* lấy HTML fragment chính xác

**Buổi 3**

* Clipboard monitor
* phát hiện clipboard thay đổi
* sequence number
* tránh infinite loop

### Phase II — HTML Cleaner

**Buổi 4**

* BeautifulSoup
* parse tree
* remove tag

**Buổi 5**

* loại quảng cáo
* tracking
* navigation
* social
* cookie
* popup

**Buổi 6**

* cleaning rule system
* `CleaningPolicy`
* configurable rules

### Phase III — Markdown

**Buổi 7**

* html2text
* configuration
* heading
* paragraph
* link
* image

**Buổi 8**

* `<pre>`
* `<code>`
* inline code
* fenced code block
* language detection

**Buổi 9**

* bảo vệ code trước khi convert
* restore code sau khi convert
* xử lý indentation

### Phase IV — Pipeline

**Buổi 10**

* Processor
* pipeline architecture
* error handling

**Buổi 11**

* logging
* statistics
* retry
* performance

### Phase V — Flet UI

**Buổi 12**

* Flet window
* always-on-top
* ON/OFF
* status

**Buổi 13**

* UI state
* processing indicator
* error indicator
* history

### Phase VI — Production

**Buổi 14**

* settings
* cấu hình cleaning rules

**Buổi 15**

* system tray
* start with Windows
* minimize to tray

**Buổi 16**

* test

**Buổi 17**

* đóng gói `.exe`

**Buổi 18**

* hoàn thiện `Clip2MD`

---

## Và mình muốn chỉnh một điểm trong yêu cầu của bạn

Không nên thiết kế:

```text
Flet UI
   ↓
Clipboard
   ↓
BeautifulSoup
   ↓
html2text
```

thành một file lớn.

Nên thiết kế:

```text
                    ┌──────────────┐
                    │   Flet UI    │
                    └──────┬───────┘
                           │
                           ▼
┌──────────┐      ┌────────────────┐
│ Clipboard├─────►│    Pipeline    │
│ Monitor  │      └───────┬────────┘
└──────────┘              │
                          ▼
                 ┌─────────────────┐
                 │ HTML Extractor  │
                 └────────┬────────┘
                          ▼
                 ┌─────────────────┐
                 │ HTML Cleaner    │
                 └────────┬────────┘
                          ▼
                 ┌─────────────────┐
                 │ Markdown        │
                 │ Converter       │
                 └────────┬────────┘
                          ▼
                 ┌─────────────────┐
                 │ ClipboardWriter │
                 └─────────────────┘
```

Như vậy sau này bạn có thể test từng tầng **không cần chạy Flet và không cần copy trên Chrome**.

Đây là điểm rất quan trọng nếu mục tiêu của bạn là làm một ứng dụng Python thực sự tốt.

**Buổi 1 mình sẽ bắt đầu từ Windows Clipboard + CF_HTML**, viết một chương trình CLI cực nhỏ:

```text
Chrome
  ↓ Ctrl+C
Windows Clipboard
  ↓
Python
  ↓
in raw CF_HTML
  ↓
extract HTML fragment
  ↓
print HTML
```

Sau khi phần này chạy ổn, chúng ta mới đưa BeautifulSoup và Flet vào. Cách này sẽ giúp bạn hiểu rõ clipboard Windows thay vì chỉ ghép thư viện lại với nhau.

[1]: https://flet.dev/docs/types/window/?utm_source=chatgpt.com "Window | Flet"
[2]: https://flet.dev/docs/?utm_source=chatgpt.com "Introduction | Flet"
