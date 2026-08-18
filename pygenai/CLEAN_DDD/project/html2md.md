Dưới đây là thiết kế và mã nguồn hoàn chỉnh cho ứng dụng tự động dọn dẹp HTML clipboard và chuyển sang Markdown, được cấu trúc chuẩn theo kiến trúc **Clean Architecture & Domain-Driven Design (DDD)** với giao diện **Flet** hỗ trợ luôn hiện trên màn hình (*Always-on-Top*).

### Yêu cầu thư viện

```bash
pip install flet beautifulsoup4 html2text pywin32

```

---

### Cấu trúc dự án

```text
clip2md/
├── domain/              # Khái niệm nghiệp vụ cốt lõi (Không phụ thuộc lib bên ngoài)
│   ├── entities.py
│   └── interfaces.py
├── application/         # Các Use Cases điều hướng luồng xử lý
│   └── use_cases.py
├── infrastructure/      # Chi tiết kỹ thuật (Win32 API, BeautifulSoup, Html2Text)
│   ├── clipboard_adapter.py
│   ├── html_cleaner_adapter.py
│   └── markdown_converter_adapter.py
├── presentation/        # Giao diện Flet UI
│   └── views.py
└── main.py              # Composition Root (Dependency Injection & Start App)

```

---

### Mã nguồn chi tiết

#### 1. Domain Layer (`domain/`)

**`domain/entities.py`**

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ClipboardContent:
    raw_html: str
    plain_text: str

    def has_html(self) -> bool:
        return bool(self.raw_html and self.raw_html.strip())

@dataclass
class CleanedMarkdown:
    content: str

```

**`domain/interfaces.py`**

```python
from abc import ABC, abstractmethod
from typing import Optional, Callable
from domain.entities import ClipboardContent, CleanedMarkdown

class IClipboardService(ABC):
    @abstractmethod
    def read_html(self) -> Optional[ClipboardContent]:
        pass

    @abstractmethod
    def write_text(self, text: str) -> None:
        pass

    @abstractmethod
    def start_listening(self, callback: Callable[[], None]) -> None:
        pass

    @abstractmethod
    def stop_listening(self) -> None:
        pass

class IHtmlCleanerService(ABC):
    @abstractmethod
    def clean(self, raw_html: str) -> str:
        pass

class IMarkdownConverterService(ABC):
    @abstractmethod
    def convert(self, clean_html: str) -> CleanedMarkdown:
        pass

```

---

#### 2. Infrastructure Layer (`infrastructure/`)

**`infrastructure/clipboard_adapter.py`** (Xử lý Windows Metadata Header CF_HTML)

```python
import re
import time
import threading
import win32clipboard
import win32con
from typing import Optional, Callable
from domain.entities import ClipboardContent
from domain.interfaces import IClipboardService

class Win32ClipboardAdapter(IClipboardService):
    def __init__(self):
        self._CF_HTML = win32clipboard.RegisterClipboardFormat("HTML Format")
        self._listening = False
        self._thread: Optional[threading.Thread] = None
        self._last_sequence_number = 0

    def _strip_windows_meta(self, raw_data: str) -> str:
        """Cắt bỏ phần header metadata của Windows CF_HTML"""
        fragment_match = re.search(
            r"<!--StartFragment-->(.*?)<!--EndFragment-->", 
            raw_data, 
            re.DOTALL | re.IGNORECASE
        )
        if fragment_match:
            return fragment_match.group(1).strip()
        
        # Fallback nếu không có thẻ fragment comment
        clean_data = re.sub(r"^(?:[A-Za-z0-9-]+:[^\r\n]*\r?\n)+", "", raw_data)
        return clean_data.strip()

    def read_html(self) -> Optional[ClipboardContent]:
        try:
            win32clipboard.OpenClipboard(0)
            raw_html = None
            plain_text = ""

            if win32clipboard.IsClipboardFormatAvailable(self._CF_HTML):
                data = win32clipboard.GetClipboardData(self._CF_HTML)
                if isinstance(data, bytes):
                    data = data.decode("utf-8", errors="ignore")
                raw_html = self._strip_windows_meta(data)

            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                plain_text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT) or ""

            return ClipboardContent(raw_html=raw_html or "", plain_text=plain_text)
        except Exception:
            return None
        finally:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass

    def write_text(self, text: str) -> None:
        try:
            win32clipboard.OpenClipboard(0)
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
        except Exception:
            pass
        finally:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass

    def start_listening(self, callback: Callable[[], None]) -> None:
        self._listening = True
        self._thread = threading.Thread(target=self._poll_clipboard, args=(callback,), daemon=True)
        self._thread.start()

    def stop_listening(self) -> None:
        self._listening = False

    def _poll_clipboard(self, callback: Callable[[], None]) -> None:
        while self._listening:
            try:
                seq = win32clipboard.GetClipboardSequenceNumber()
                if seq != self._last_sequence_number:
                    self._last_sequence_number = seq
                    callback()
            except Exception:
                pass
            time.sleep(0.4)

```

**`infrastructure/html_cleaner_adapter.py`**

```python
from bs4 import BeautifulSoup
from domain.interfaces import IHtmlCleanerService

class BeautifulSoupCleanerAdapter(IHtmlCleanerService):
    JUNK_TAGS = [
        "script", "style", "noscript", "iframe", "header", "footer", 
        "nav", "aside", "form", "button", "input", "svg", "amp-embed"
    ]

    def clean(self, raw_html: str) -> str:
        soup = BeautifulSoup(raw_html, "html.parser")

        # 1. Loại bỏ các thẻ rác/quảng cáo
        for tag in self.JUNK_TAGS:
            for match in soup.find_all(tag):
                match.decompose()

        # 2. Xóa các class/id quảng cáo phổ biến
        for element in soup.find_all(True):
            attrs_to_check = str(element.get("class", [])) + str(element.get("id", ""))
            if any(ad_kw in attrs_to_check.lower() for ad_kw in ["ad-", "banner", "sponsor", "popup", "social-share"]):
                element.decompose()
                continue
            
            # Xóa bớt thuộc tính rác nhưng giữ nguyên tag structure
            element.attrs = {k: v for k, v in element.attrs.items() if k in ["href", "src", "alt", "title", "lang"]}

        return str(soup)

```

**`infrastructure/markdown_converter_adapter.py`**

```python
import html2text
from domain.entities import CleanedMarkdown
from domain.interfaces import IMarkdownConverterService

class Html2TextConverterAdapter(IMarkdownConverterService):
    def __init__(self):
        self._converter = html2text.HTML2Text()
        # Cấu hình tối ưu giữ khối code
        self._converter.body_width = 0  # Không ngắt dòng cứng
        self._converter.ignore_links = False
        self._converter.ignore_images = False
        self._converter.ignore_emphasis = False
        self._converter.mark_code = True
        self._converter.escape_snob = True

    def convert(self, clean_html: str) -> CleanedMarkdown:
        markdown_text = self._converter.handle(clean_html)
        return CleanedMarkdown(content=markdown_text.strip())

```

---

#### 3. Application Layer (`application/`)

**`application/use_cases.py`**

```python
from domain.interfaces import IClipboardService, IHtmlCleanerService, IMarkdownConverterService

class ProcessClipboardUseCase:
    def __init__(
        self,
        clipboard_service: IClipboardService,
        html_cleaner: IHtmlCleanerService,
        markdown_converter: IMarkdownConverterService
    ):
        self.clipboard_service = clipboard_service
        self.html_cleaner = html_cleaner
        self.markdown_converter = markdown_converter
        self._is_internal_update = False

    def execute() -> bool:
        if self._is_internal_update:
            self._is_internal_update = False
            return False

        content = self.clipboard_service.read_html()
        if not content or not content.has_html():
            return False

        # Luồng xử lý DDD
        cleaned_html = self.html_cleaner.clean(content.raw_html)
        cleaned_md = self.markdown_converter.convert(cleaned_html)

        if cleaned_md.content and cleaned_md.content != content.plain_text:
            self._is_internal_update = True
            self.clipboard_service.write_text(cleaned_md.content)
            return True

        return False

```

---

#### 4. Presentation Layer (`presentation/`) & Entrypoint (`main.py`)

**`main.py`**

```python
import flet as ft
from infrastructure.clipboard_adapter import Win32ClipboardAdapter
from infrastructure.html_cleaner_adapter import BeautifulSoupCleanerAdapter
from infrastructure.markdown_converter_adapter import Html2TextConverterAdapter
from application.use_cases import ProcessClipboardUseCase

def main(page: ft.Page):
    # Cấu hình Window Floating & Always-on-top
    page.title = "Clip2MD"
    page.window.width = 280
    page.window.height = 160
    page.window.always_on_top = True
    page.window.resizable = False
    page.padding = 12
    page.theme_mode = ft.ThemeMode.DARK

    # Dependency Injection Setup
    clipboard_adapter = Win32ClipboardAdapter()
    cleaner_adapter = BeautifulSoupCleanerAdapter()
    converter_adapter = Html2TextConverterAdapter()

    process_use_case = ProcessClipboardUseCase(
        clipboard_service=clipboard_adapter,
        html_cleaner=cleaner_adapter,
        markdown_converter=converter_adapter
    )

    # UI State Controls
    status_text = ft.Text("Chế độ: Đang TẮT", color=ft.Colors.RED_400, weight=ft.FontWeight.BOLD)
    last_action_text = ft.Text("Sẵn sàng...", size=11, color=ft.Colors.GREY_400)

    def on_clipboard_changed():
        if process_use_case.execute():
            last_action_text.value = "Đã chuyển HTML sang Code/MD!"
            last_action_text.color = ft.Colors.GREEN_400
            page.update()

    def toggle_mode(e):
        if e.control.value:
            clipboard_adapter.start_listening(on_clipboard_changed)
            status_text.value = "Chế độ: Đang BẬT"
            status_text.color = ft.Colors.GREEN_400
            last_action_text.value = "Đang bắt lệnh Copy..."
        else:
            clipboard_adapter.stop_listening()
            status_text.value = "Chế độ: Đang TẮT"
            status_text.color = ft.Colors.RED_400
            last_action_text.value = "Đã tạm dừng."
        page.update()

    switch = ft.Switch(label="Kích hoạt", value=False, on_change=toggle_mode)

    page.add(
        ft.Column(
            [
                ft.Row([switch], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=1),
                status_text,
                last_action_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8
        )
    )

if __name__ == "__main__":
    ft.app(target=main)

```

---

### Điểm nổi bật trong thiết kế

1. **Clean Architecture & DDD Boundary**:
* **Domain**: Đóng gói các thực thể `ClipboardContent`, `CleanedMarkdown` độc lập hoàn toàn với framework UI hay thư viện bên ngoài.
* **Infrastructure**: Đóng gói các adapter xử lý Windows API (`CF_HTML`), BeautifulSoup, và Html2Text.
* **Application**: `ProcessClipboardUseCase` chỉ điều phối việc đọc -> làm sạch -> chuyển đổi -> ghi đè.


2. **Xử lý Windows Clipboard Metadata**: Adapter `Win32ClipboardAdapter` giải mã đúng định dạng `HTML Format` của Windows, bóc tách chính xác phần HTML nội dung bên trong cặp tag `<!--StartFragment-->` và `<!--EndFragment-->`.
3. **Bảo tồn Code block**: Thư viện `html2text` được cấu hình `mark_code=True` và `body_width=0` kết hợp loại bỏ các thẻ rác từ BeautifulSoup, giúp giữ trọn vẹn cú pháp các khối thẻ `<pre>` và `<code>`.
4. **Tránh vòng lặp Copy (Recursion Prevention)**: `ProcessClipboardUseCase` duy trì cờ `_is_internal_update` để bỏ qua việc xử lý lại chính đoạn văn bản Markdown vừa ghi vào clipboard.