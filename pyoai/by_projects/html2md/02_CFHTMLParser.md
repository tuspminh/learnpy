# Buổi 2 — Xây dựng `CFHTMLParser` chuẩn

Hôm nay chúng ta bỏ qua Flet, BeautifulSoup và `html2text`.

Mục tiêu duy nhất:

> **Từ dữ liệu `CF_HTML` thô của Windows Clipboard → lấy chính xác HTML fragment mà người dùng đã copy.**

Pipeline:

```text
Chrome / Edge
     │
     │ Ctrl+C
     ▼
Windows Clipboard
     │
     ▼
CF_HTML bytes
     │
     ▼
CFHTMLParser
     │
     ├── Version
     ├── StartHTML
     ├── EndHTML
     ├── StartFragment
     ├── EndFragment
     └── SourceURL
             │
             ▼
       HTML Fragment
```

---

# 1. CF_HTML thực chất là gì?

Một clipboard HTML thường có dạng:

```text
Version:0.9
StartHTML:00000105
EndHTML:00000582
StartFragment:00000170
EndFragment:00000517
SourceURL:https://example.com/

<html>
<head>
...
</head>
<body>
<!--StartFragment-->
<h1>Hello Python</h1>
<p>Xin chào</p>
<!--EndFragment-->
</body>
</html>
```

Ta cần phân biệt:

### Header

```text
Version:0.9
StartHTML:...
EndHTML:...
StartFragment:...
EndFragment:...
SourceURL:...
```

### HTML document

```html
<html>
...
</html>
```

### HTML fragment

```html
<h1>Hello Python</h1>
<p>Xin chào</p>
```

App của chúng ta chủ yếu cần **fragment**.

---

# 2. Tại sao phải xử lý `bytes`?

Đây là vấn đề rất quan trọng.

Header chứa:

```text
StartFragment:00000170
EndFragment:00000517
```

Các offset này liên quan đến **byte position**, không đơn giản là index của Python `str`.

Ví dụ:

```python
text = "Xin chào"
```

Số character:

```text
7
```

nhưng UTF-8 bytes:

```text
X  i  n     c  h  à  o
1  1  1  1  1  1  2  1
```

`à` chiếm 2 bytes.

Vì vậy:

```python
data[170:517]
```

phải được thực hiện trên:

```python
bytes
```

chứ không phải sau khi decode thành string.

---

# 3. Kiến trúc module

Chúng ta tạo:

```text
src/
└── clip2md/
    ├── __init__.py
    ├── clipboard.py
    └── cf_html.py
```

`cf_html.py` chịu trách nhiệm:

```text
raw bytes
   ↓
parse header
   ↓
metadata
   ↓
extract fragment
```

---

# 4. Dataclass cho metadata

Đây là nơi `dataclass` rất phù hợp.

```python
from dataclasses import dataclass


@dataclass(slots=True)
class CFHTMLHeader:
    version: str | None = None
    start_html: int | None = None
    end_html: int | None = None
    start_fragment: int | None = None
    end_fragment: int | None = None
    source_url: str | None = None
```

Ta muốn:

```python
header.start_fragment
```

thay vì:

```python
header["StartFragment"]
```

Điều này làm code phía sau dễ đọc hơn rất nhiều.

---

# 5. Parse header

Tạo:

```python
def parse_header(data: bytes) -> CFHTMLHeader:
    ...
```

Đầu tiên tìm phần header.

CF_HTML header kết thúc trước HTML.

Thông thường ta có:

```text
\r\n\r\n
```

giữa header và HTML.

Có thể tìm:

```python
separator = data.find(b"\r\n\r\n")
```

Sau đó:

```python
header_bytes = data[:separator]
```

Decode:

```python
header_text = header_bytes.decode(
    "ascii",
    errors="replace",
)
```

Tại sao `ascii`?

Bởi vì các field header như:

```text
StartHTML:00000105
StartFragment:00000170
```

chỉ chứa ASCII.

---

# 6. Parse từng dòng

Ví dụ:

```text
Version:0.9
StartHTML:00000105
EndHTML:00000582
StartFragment:00000170
EndFragment:00000517
SourceURL:https://example.com/
```

Ta có:

```python
for line in header_text.splitlines():
    print(line)
```

Sau đó:

```python
key, value = line.split(":", 1)
```

**Chú ý `1`**.

Không dùng:

```python
line.split(":")
```

vì:

```text
SourceURL:https://example.com/
```

có nhiều dấu `:`.

---

# 7. Parse offset

Ví dụ:

```text
StartHTML:00000105
```

Ta lấy:

```python
int("00000105")
```

kết quả:

```text
105
```

Viết helper:

```python
def parse_int(value: str) -> int | None:
    value = value.strip()

    if not value:
        return None

    try:
        return int(value)
    except ValueError:
        return None
```

---

# 8. Hoàn thiện `parse_header`

```python
from dataclasses import dataclass


@dataclass(slots=True)
class CFHTMLHeader:
    version: str | None = None
    start_html: int | None = None
    end_html: int | None = None
    start_fragment: int | None = None
    end_fragment: int | None = None
    source_url: str | None = None


def parse_int(value: str) -> int | None:
    value = value.strip()

    if not value:
        return None

    try:
        return int(value)
    except ValueError:
        return None


def parse_header(data: bytes) -> CFHTMLHeader:
    separator = data.find(b"\r\n\r\n")

    if separator == -1:
        raise ValueError("Invalid CF_HTML header")

    header_bytes = data[:separator]

    header_text = header_bytes.decode(
        "ascii",
        errors="replace",
    )

    header = CFHTMLHeader()

    for line in header_text.splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        key = key.strip()
        value = value.strip()

        if key == "Version":
            header.version = value

        elif key == "StartHTML":
            header.start_html = parse_int(value)

        elif key == "EndHTML":
            header.end_html = parse_int(value)

        elif key == "StartFragment":
            header.start_fragment = parse_int(value)

        elif key == "EndFragment":
            header.end_fragment = parse_int(value)

        elif key == "SourceURL":
            header.source_url = value

    return header
```

---

# 9. Extract fragment

Bây giờ phần quan trọng nhất:

```python
def extract_fragment(data: bytes) -> str:
    header = parse_header(data)

    if header.start_fragment is None:
        raise ValueError("Missing StartFragment")

    if header.end_fragment is None:
        raise ValueError("Missing EndFragment")

    fragment_bytes = data[
        header.start_fragment:
        header.end_fragment
    ]

    return fragment_bytes.decode(
        "utf-8",
        errors="replace",
    )
```

Đây là phiên bản đầu tiên.

---

# 10. Tại sao phải validate offset?

Không nên tin dữ liệu clipboard một cách tuyệt đối.

Browser hoặc ứng dụng khác có thể đưa dữ liệu không hợp lệ.

Ví dụ:

```text
StartFragment:500
EndFragment:100
```

Nếu không kiểm tra:

```python
data[500:100]
```

sẽ trả về:

```python
b""
```

và ta sẽ không biết nguyên nhân.

Ta nên validate:

```python
def validate_header(
    header: CFHTMLHeader,
    data_length: int,
) -> None:

    if header.start_fragment is None:
        raise ValueError("Missing StartFragment")

    if header.end_fragment is None:
        raise ValueError("Missing EndFragment")

    if header.start_fragment < 0:
        raise ValueError("Invalid StartFragment")

    if header.end_fragment < 0:
        raise ValueError("Invalid EndFragment")

    if header.start_fragment > header.end_fragment:
        raise ValueError(
            "StartFragment > EndFragment"
        )

    if header.end_fragment > data_length:
        raise ValueError(
            "EndFragment outside clipboard data"
        )
```

---

# 11. Hoàn thiện `extract_fragment`

```python
def extract_fragment(data: bytes) -> str:
    header = parse_header(data)

    validate_header(
        header,
        len(data),
    )

    fragment = data[
        header.start_fragment:
        header.end_fragment
    ]

    return fragment.decode(
        "utf-8",
        errors="replace",
    )
```

Pipeline hiện tại:

```text
bytes
 │
 ▼
parse_header()
 │
 ▼
CFHTMLHeader
 │
 ▼
validate_header()
 │
 ▼
data[start:end]
 │
 ▼
decode UTF-8
 │
 ▼
HTML fragment
```

---

# 12. Nhưng có một vấn đề với UTF-8

Bạn có thể nghĩ:

```python
fragment.decode("utf-8")
```

là đủ.

Trong phần lớn trường hợp browser hiện đại, nó hoạt động tốt.

Nhưng app production nên có fallback.

Ta viết:

```python
def decode_html(data: bytes) -> str:
    for encoding in (
        "utf-8",
        "windows-1252",
        "latin-1",
    ):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue

    return data.decode(
        "utf-8",
        errors="replace",
    )
```

Sau này có thể cải thiện.

---

# 13. Xử lý `StartHTML` và `EndHTML`

Ngoài fragment, header còn có:

```text
StartHTML
EndHTML
```

Ta có thể viết:

```python
def extract_html_document(data: bytes) -> str:
    header = parse_header(data)

    if header.start_html is None:
        raise ValueError("Missing StartHTML")

    if header.end_html is None:
        raise ValueError("Missing EndHTML")

    validate_range(
        header.start_html,
        header.end_html,
        len(data),
    )

    html = data[
        header.start_html:
        header.end_html
    ]

    return decode_html(html)
```

Sau này có thể dùng khi debug.

---

# 14. Tách `validate_range`

Code tốt hơn:

```python
def validate_range(
    start: int,
    end: int,
    length: int,
) -> None:

    if start < 0:
        raise ValueError(
            "Start offset cannot be negative"
        )

    if end < 0:
        raise ValueError(
            "End offset cannot be negative"
        )

    if start > end:
        raise ValueError(
            "Start offset > end offset"
        )

    if end > length:
        raise ValueError(
            "End offset exceeds data length"
        )
```

Sau đó:

```python
validate_range(
    header.start_fragment,
    header.end_fragment,
    len(data),
)
```

---

# 15. Xử lý marker `StartFragment`

Có một điều thực tế rất đáng chú ý.

Một số clipboard provider có:

```text
StartFragment
EndFragment
```

chuẩn.

Một số trường hợp có thể có marker:

```html
<!--StartFragment-->
...
<!--EndFragment-->
```

Nếu metadata bị sai hoặc thiếu, chúng ta có thể fallback bằng marker.

```python
START_MARKER = b"<!--StartFragment-->"
END_MARKER = b"<!--EndFragment-->"
```

Helper:

```python
def extract_by_markers(data: bytes) -> str:
    start_marker = b"<!--StartFragment-->"
    end_marker = b"<!--EndFragment-->"

    start = data.find(start_marker)

    if start == -1:
        raise ValueError(
            "StartFragment marker not found"
        )

    start += len(start_marker)

    end = data.find(
        end_marker,
        start,
    )

    if end == -1:
        raise ValueError(
            "EndFragment marker not found"
        )

    return decode_html(data[start:end])
```

---

# 16. Strategy tốt hơn

Đừng dùng marker trước.

Ta thiết kế:

```text
extract_fragment()
        │
        ▼
Có StartFragment/EndFragment?
        │
      YES
        │
        ▼
   offset extraction
        │
      ERROR?
        │
        ▼
 marker fallback
```

Tức là:

```python
def extract_fragment(data: bytes) -> str:
    try:
        return extract_by_offsets(data)
    except ValueError:
        return extract_by_markers(data)
```

Đây là một **fallback strategy**.

---

# 17. Xây class `CFHTMLParser`

Đến đây ta có thể đóng gói.

```python
class CFHTMLParser:

    def __init__(self, data: bytes):
        self.data = data
        self.header = parse_header(data)

    def extract_fragment(self) -> str:
        ...

    def extract_document(self) -> str:
        ...
```

Sử dụng:

```python
parser = CFHTMLParser(raw_data)

print(parser.header)

fragment = parser.extract_fragment()

print(fragment)
```

Đây là API chúng ta muốn giữ lâu dài.

---

# 18. Phiên bản hoàn chỉnh Buổi 2

`cf_html.py`:

```python
from dataclasses import dataclass


@dataclass(slots=True)
class CFHTMLHeader:
    version: str | None = None
    start_html: int | None = None
    end_html: int | None = None
    start_fragment: int | None = None
    end_fragment: int | None = None
    source_url: str | None = None


def parse_int(value: str) -> int | None:
    value = value.strip()

    if not value:
        return None

    try:
        return int(value)
    except ValueError:
        return None


def decode_html(data: bytes) -> str:
    for encoding in (
        "utf-8",
        "windows-1252",
        "latin-1",
    ):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue

    return data.decode(
        "utf-8",
        errors="replace",
    )


def parse_header(data: bytes) -> CFHTMLHeader:
    separator = data.find(b"\r\n\r\n")

    if separator == -1:
        raise ValueError(
            "Invalid CF_HTML header"
        )

    header_text = data[:separator].decode(
        "ascii",
        errors="replace",
    )

    header = CFHTMLHeader()

    for line in header_text.splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        key = key.strip()
        value = value.strip()

        match key:
            case "Version":
                header.version = value

            case "StartHTML":
                header.start_html = parse_int(value)

            case "EndHTML":
                header.end_html = parse_int(value)

            case "StartFragment":
                header.start_fragment = parse_int(value)

            case "EndFragment":
                header.end_fragment = parse_int(value)

            case "SourceURL":
                header.source_url = value

    return header


def validate_range(
    start: int,
    end: int,
    length: int,
) -> None:

    if start < 0:
        raise ValueError(
            "Start offset cannot be negative"
        )

    if end < 0:
        raise ValueError(
            "End offset cannot be negative"
        )

    if start > end:
        raise ValueError(
            "Start offset > end offset"
        )

    if end > length:
        raise ValueError(
            "End offset exceeds data length"
        )


class CFHTMLParser:

    def __init__(self, data: bytes):
        self.data = data
        self.header = parse_header(data)

    def extract_document(self) -> str:
        start = self.header.start_html
        end = self.header.end_html

        if start is None:
            raise ValueError(
                "Missing StartHTML"
            )

        if end is None:
            raise ValueError(
                "Missing EndHTML"
            )

        validate_range(
            start,
            end,
            len(self.data),
        )

        return decode_html(
            self.data[start:end]
        )

    def extract_fragment(self) -> str:
        start = self.header.start_fragment
        end = self.header.end_fragment

        if start is not None and end is not None:
            try:
                validate_range(
                    start,
                    end,
                    len(self.data),
                )

                return decode_html(
                    self.data[start:end]
                )

            except ValueError:
                pass

        return self._extract_by_markers()

    def _extract_by_markers(self) -> str:
        start_marker = b"<!--StartFragment-->"
        end_marker = b"<!--EndFragment-->"

        start = self.data.find(start_marker)

        if start == -1:
            raise ValueError(
                "StartFragment marker not found"
            )

        start += len(start_marker)

        end = self.data.find(
            end_marker,
            start,
        )

        if end == -1:
            raise ValueError(
                "EndFragment marker not found"
            )

        return decode_html(
            self.data[start:end]
        )
```

---

# 19. Kết nối với Clipboard

`clipboard.py`:

```python
import win32clipboard

from .cf_html import CFHTMLParser


HTML_FORMAT = win32clipboard.RegisterClipboardFormat(
    "HTML Format"
)


class ClipboardReader:

    def read_html(self) -> str | None:
        win32clipboard.OpenClipboard()

        try:
            if not win32clipboard.IsClipboardFormatAvailable(
                HTML_FORMAT
            ):
                return None

            raw = win32clipboard.GetClipboardData(
                HTML_FORMAT
            )

            if isinstance(raw, str):
                raw = raw.encode(
                    "utf-8",
                    errors="replace",
                )

            parser = CFHTMLParser(raw)

            return parser.extract_fragment()

        finally:
            win32clipboard.CloseClipboard()
```

Test:

```python
from clip2md.clipboard import ClipboardReader


def main():
    reader = ClipboardReader()

    html = reader.read_html()

    if html is None:
        print("No HTML in clipboard")
        return

    print(html)


if __name__ == "__main__":
    main()
```

---

# 20. Test thực tế

Copy từ browser một đoạn như:

```html
<h1>Python</h1>

<p>
    Đây là <strong>Python</strong>.
</p>

<pre><code>
def hello():
    print("Hello")
</code></pre>
```

Chạy:

```bash
python -m clip2md.main
```

Kết quả mong muốn:

```html
<h1>Python</h1>

<p>
    Đây là <strong>Python</strong>.
</p>

<pre><code>
def hello():
    print("Hello")
</code></pre>
```

**Không được xuất hiện:**

```text
Version:0.9
StartHTML:...
EndHTML:...
StartFragment:...
EndFragment:...
SourceURL:...
```

Đó chính là thành công của Buổi 2.

---

# 21. Test quan trọng hơn: Unicode

Hãy thử copy:

```html
<h1>Xin chào Việt Nam 🇻🇳</h1>

<p>
    Python là ngôn ngữ lập trình rất thú vị.
</p>

<pre><code>
print("Xin chào 👋")
</code></pre>
```

Nếu kết quả vẫn chính xác:

```html
<h1>Xin chào Việt Nam 🇻🇳</h1>
```

thì chúng ta đã xác nhận parser đang xử lý byte offset đúng hướng.

---

# 22. Unit test

Đây là phần mình muốn bạn chú ý.

Không nên test parser bằng Chrome mỗi lần.

Ta tạo fixture:

```python
RAW_CF_HTML = (
    b"Version:0.9\r\n"
    b"StartHTML:00000100\r\n"
    b"EndHTML:00000200\r\n"
    b"StartFragment:00000120\r\n"
    b"EndFragment:00000160\r\n"
    b"SourceURL:https://example.com/\r\n"
    b"\r\n"
    b"<html><body>"
    b"XXXXXXXXXXXXXXXXXXXX"
    b"<p>Hello</p>"
    b"YYYYYYYYYYYYYYYYYYYY"
    b"</body></html>"
)
```

Nhưng chú ý: **offset phải đúng với dữ liệu thực tế**.

Do đó tốt hơn là viết helper tạo fixture.

```python
def build_cf_html(fragment: str) -> bytes:
    ...
```

Đây sẽ là bài tập nâng cao của Buổi 2.

---

# 23. Bài tập

### Bài 1 — `CFHTMLHeader`

Viết test:

```python
header = parse_header(data)

assert header.version == "0.9"
assert header.source_url == "https://example.com/"
```

---

### Bài 2 — `extract_document`

Đảm bảo:

```python
parser.extract_document()
```

trả về toàn bộ:

```html
<html>
...
</html>
```

---

### Bài 3 — `extract_fragment`

Đảm bảo:

```python
parser.extract_fragment()
```

chỉ trả về:

```html
<p>Hello</p>
```

---

### Bài 4 — Unicode

Test:

```text
Xin chào Việt Nam 🇻🇳
```

```text
你好
```

```text
こんにちは
```

```text
Привет
```

---

### Bài 5 — malformed data

Test:

```text
StartFragment > EndFragment
```

và:

```text
EndFragment > len(data)
```

Parser phải raise:

```python
ValueError
```

hoặc fallback marker.

---

# 24. Kiến trúc sau Buổi 2

Bây giờ project đã có tầng đầu tiên khá sạch:

```text
                    Browser
                       │
                      Ctrl+C
                       │
                       ▼
              Windows Clipboard
                       │
                       ▼
                ClipboardReader
                       │
                       ▼
                    CF_HTML
                       │
                       ▼
                 CFHTMLParser
                       │
             ┌─────────┴─────────┐
             │                   │
       parse_header()      extract_fragment()
             │                   │
             ▼                   ▼
       CFHTMLHeader          HTML fragment
```

Và quan trọng nhất:

> **BeautifulSoup chưa biết Windows Clipboard là gì.**

Nó chỉ nhận:

```html
<p>Hello</p>
<pre><code>...</code></pre>
```

Đây chính là boundary tốt giữa **Windows infrastructure** và **HTML processing**.

---

# 25. Bài tập cuối buổi — rất quan trọng

Hãy tự viết lại từ đầu, **không copy code ở trên**, 4 thành phần:

```text
CFHTMLHeader
parse_header()
CFHTMLParser
ClipboardReader
```

và đạt API:

```python
reader = ClipboardReader()

html = reader.read_html()

print(html)
```

Kết quả phải là **HTML fragment sạch metadata Windows**.

### Sau khi hoàn thành Buổi 2

Chúng ta sẽ sang **Buổi 3 — Clipboard Monitor**:

```text
Windows Clipboard
       │
       ▼
detect change
       │
       ▼
CF_HTML ?
       │
       ▼
extract fragment
```

và đặc biệt xử lý bài toán khó:

```text
User Ctrl+C
      ↓
App đọc clipboard
      ↓
App xử lý
      ↓
App ghi Markdown
      ↓
Clipboard changed
      ↓
App KHÔNG được tự bắt chính clipboard của nó
```

Tức là chúng ta sẽ xây **event loop + clipboard sequence tracking + chống infinite loop**, trước khi bắt đầu đưa BeautifulSoup vào.
