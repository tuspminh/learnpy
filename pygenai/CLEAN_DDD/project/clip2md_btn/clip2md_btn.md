Dưới đây là phân tích kiến trúc và cấu trúc phần mềm chi tiết theo **Clean Architecture** kết hợp **Domain-Driven Design (DDD)**, kèm mã nguồn triển khai hoàn chỉnh cho ứng dụng của bạn.

---

## 1. Phân tích Tên miền (Domain Analysis) & Đặt vấn đề

### Biền giới ngữ cảnh (Bounded Context)

Ứng dụng đóng vai trò là một **Clipboard Content Transformer**, tập trung vào tác vụ xử lý HTML định dạng rich text từ bộ nhớ tạm (đặc biệt là dữ liệu do Windows chèn metadata) và chuẩn hóa về dạng **Markdown sạch**, giữ trọn vẹn mã nguồn.

### Các thành phần chính của DDD

* **Value Objects**:
* `RawClipboardHTML`: Chứa dữ liệu thô thu thập từ Clipboard.
* `SanitizedHTML`: Chứa đoạn HTML đã loại bỏ Windows metadata và các thẻ HTML rác.
* `MarkdownText`: Sản phẩm đầu ra đã chuyển đổi.


* **Domain Services / Interfaces (Ports)**:
* `IClipboardService`: Lớp giao tiếp đọc/ghi Clipboard hệ thống.
* `IHTMLTransformer`: Lớp chịu trách nhiệm bóc tách metadata Windows, lọc thẻ rác và chuyển đổi sang Markdown.


* **Use Cases (Application Services)**:
* `ConvertClipboardHTMLToMarkdownUseCase`: Điều phối toàn bộ luồng công việc.



---

## 2. Cấu trúc Dự án (Clean Architecture)

```text
clip2md/
├── domain/                  # Lớp Tên miền (Độc lập tuyệt đối với thư viện ngoài)
│   ├── models.py            # Value Objects
│   └── interfaces.py        # Abstract Base Classes (Ports)
├── infrastructure/          # Lớp Hạ tầng (Triển khai Adapter cụ thể)
│   ├── clipboard_adapter.py # Adapter xử lý Clipboard hệ thống
│   └── html_adapter.py      # Adapter dùng BeautifulSoup4 & html2text
├── application/             # Lớp Ứng dụng (Use Case)
│   └── use_cases.py         # Quy trình chuyển đổi
└── presentation/            # Lớp Hiển thị (Flet UI)
    └── main.py              # Flet Interface & Window configurations

```

---

## 3. Triển khai Mã nguồn Chi tiết

### Step 1: `domain/models.py` (Value Objects)

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class RawClipboardHTML:
    content: str

    def is_empty(self) -> bool:
        return not bool(self.content and self.content.strip())

@dataclass(frozen=True)
class MarkdownText:
    value: str

```

---

### Step 2: `domain/interfaces.py` (Ports)

```python
from abc import ABC, abstractmethod
from domain.models import RawClipboardHTML, MarkdownText

class IClipboardService(ABC):
    @abstractmethod
    def read_html_or_text(self) -> RawClipboardHTML:
        """Đọc dữ liệu văn bản/HTML từ clipboard."""
        pass

    @abstractmethod
    def write_text(self, text: MarkdownText) -> None:
        """Ghi dữ liệu Markdown đã xử lý vào clipboard."""
        pass


class IHTMLTransformer(ABC):
    @abstractmethod
    def transform(self, raw_html: RawClipboardHTML) -> MarkdownText:
        """Chuyển đổi từ Raw HTML sang Markdown sạch."""
        pass

```

---

### Step 3: `infrastructure/html_adapter.py` (Xử lý Windows Meta, BS4 & html2text)

```python
import re
from bs4 import BeautifulSoup
import html2text
from domain.interfaces import IHTMLTransformer
from domain.models import RawClipboardHTML, MarkdownText

class BS4Html2TextTransformer(IHTMLTransformer):
    # Các thẻ rác cần loại bỏ triệt để
    DISCARD_TAGS = [
        "script", "style", "nav", "header", "footer", 
        "aside", "iframe", "form", "button", "svg", 
        "meta", "head", "noscript", "input"
    ]

    def __init__(self):
        self._h2t = html2text.HTML2Text()
        self._h2t.body_width = 0          # Không tự động ngắt dòng code dài
        self._h2t.ignore_links = False
        self._h2t.ignore_images = True     # Tập trung vào code & văn bản
        self._h2t.mark_code = True         # Đánh dấu khối code chuẩn
        self._h2t.code_tag_as_block = True

    def _strip_windows_metadata(self, html_str: str) -> str:
        """Loại bỏ phần Header Metadata của Windows Clipboard."""
        # Cách 1: Bóc tách nội dung nằm giữa StartFragment và EndFragment
        fragment_match = re.search(
            r"<!--StartFragment-->(.*?)<!--EndFragment-->", 
            html_str, 
            flags=re.DOTALL | re.IGNORECASE
        )
        if fragment_match:
            return fragment_match.group(1)

        # Cách 2: Loại bỏ các dòng header dạng "Version:0.9", "StartHTML:...", ...
        cleaned = re.sub(r"^(Version|StartHTML|EndHTML|StartFragment|EndFragment):\d+\r?\n", "", html_str, flags=re.MULTILINE)
        return cleaned

    def _clean_bs4(self, html_content: str) -> str:
        """Loại bỏ thẻ rác nhưng bảo toàn tuyệt đối thẻ code, pre, code inline."""
        soup = BeautifulSoup(html_content, "html.parser")

        # 1. Xóa bỏ các thẻ rác
        for tag_name in self.DISCARD_TAGS:
            for element in soup.find_all(tag_name):
                element.decompose()

        # 2. Xử lý khoảng trắng thừa xung quanh thẻ <pre> và <code> để tránh mất format
        for pre in soup.find_all("pre"):
            # Giữ nguyên cấu trúc dòng bên trong pre
            pre.preserve_whitespace = True

        return str(soup)

    def transform(self, raw_html: RawClipboardHTML) -> MarkdownText:
        if raw_html.is_empty():
            return MarkdownText(value="")

        # Bước 1: Xóa Windows Metadata
        content_without_meta = self._strip_windows_metadata(raw_html.content)

        # Bước 2: Dùng BS4 loại bỏ thẻ rác
        cleaned_html = self._clean_bs4(content_without_meta)

        # Bước 3: Chuyển đổi sang Markdown bằng html2text
        markdown_result = self._h2t.handle(cleaned_html)

        # Bước 4: Dọn dẹp dòng trống thừa
        cleaned_markdown = re.sub(r"\n{3,}", "\n\n", markdown_result).strip()

        return MarkdownText(value=cleaned_markdown)

```

---

### Step 4: `infrastructure/clipboard_adapter.py` (System Clipboard Interface)

Thư viện `pyperclip` hoặc giao diện Clipboard tích hợp của Flet có thể được wrap tại đây.

```python
import pyperclip
from domain.interfaces import IClipboardService
from domain.models import RawClipboardHTML, MarkdownText

class PyperclipAdapter(IClipboardService):
    def read_html_or_text(self) -> RawClipboardHTML:
        # Lấy nội dung văn bản/HTML đang có trên clipboard
        content = pyperclip.paste()
        return RawClipboardHTML(content=content or "")

    def write_text(self, text: MarkdownText) -> None:
        pyperclip.copy(text.value)

```

---

### Step 5: `application/use_cases.py` (Use Case logic)

```python
from domain.interfaces import IClipboardService, IHTMLTransformer

class ProcessClipboardToMarkdownUseCase:
    def __init__(self, clipboard_service: IClipboardService, transformer: IHTMLTransformer):
        self._clipboard_service = clipboard_service
        self._transformer = transformer

    def execute(self) -> bool:
        """Thực thi luồng: Đọc -> Biến đổi -> Ghi lại. Tra về True nếu thành công."""
        raw_data = self._clipboard_service.read_html_or_text()
        
        if raw_data.is_empty():
            return False

        markdown_text = self._transformer.transform(raw_data)
        
        if not markdown_text.value:
            return False

        self._clipboard_service.write_text(markdown_text)
        return True

```

---

### Step 6: `presentation/main.py` (Flet App UI)

Ứng dụng nhỏ gọn, luôn nổi trên các cửa sổ khác (`always_on_top`).

```python
import flet as ft
from infrastructure.clipboard_adapter import PyperclipAdapter
from infrastructure.html_adapter import BS4Html2TextTransformer
from application.use_cases import ProcessClipboardToMarkdownUseCase

def main(page: ft.Page):
    # Cấu hình cửa sổ nổi nhỏ gọn
    page.title = "HTML2MD"
    page.window.width = 160
    page.window.height = 100
    page.window.always_on_top = True
    page.window.resizable = False
    page.padding = 8
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Khởi tạo các phụ thuộc (Dependency Injection)
    clipboard_service = PyperclipAdapter()
    transformer = BS4Html2TextTransformer()
    use_case = ProcessClipboardToMarkdownUseCase(
        clipboard_service=clipboard_service,
        transformer=transformer
    )

    def on_activate_click(e):
        btn.disabled = True
        btn.icon = ft.Icons.HOURGLASS_EMPTY
        page.update()

        success = use_case.execute()

        if success:
            btn.icon = ft.Icons.CHECK_CIRCLE
            btn.style = ft.ButtonStyle(color=ft.Colors.GREEN)
            page.open(ft.SnackBar(ft.Text("Đã chuyển đổi sang Markdown!"), duration=1500))
        else:
            btn.icon = ft.Icons.ERROR_OUTLINE
            btn.style = ft.ButtonStyle(color=ft.Colors.RED)
            page.open(ft.SnackBar(ft.Text("Clipboard rỗng hoặc không đúng format HTML"), duration=1500))

        btn.disabled = False
        page.update()

    btn = ft.ElevatedButton(
        text="Convert",
        icon=ft.Icons.TRANSFORM,
        on_click=on_activate_click,
        style=ft.ButtonStyle(
            padding=ft.padding.all(10),
        )
    )

    page.add(btn)

if __name__ == "__main__":
    ft.app(target=main)

```

---

## 4. Các điểm cải tiến chính theo yêu cầu

1. **Gỡ bỏ Windows Metadata**: Regex pattern `<!--StartFragment-->(.*?)<!--EndFragment-->` giúp bóc tách đúng phần HTML nội dung thực sự do Windows copy.
2. **Bảo tồn Code block & Inline Code**:
* BS4 thực hiện `decompose()` loại bỏ `script`, `style`, `nav`, `header`... nhưng không can thiệp cấu trúc trong `<pre>` và `<code>`.
* Thư viện `html2text` được thiết lập `body_width = 0` nhằm giữ nguyên độ dài dòng code mà không chèn ký tự xuống dòng tự động.


3. **Mô hình DDD & Clean Architecture**:
* Tách biệt **UI** (`Flet`), **Adapter** (`pyperclip`, `BS4`, `html2text`), và **Logic nghiệp vụ lõi**. Bạn hoàn toàn có thể thay đổi giao diện hoặc chuyển sang thư viện Clipboard khác mà không ảnh hưởng tới thuật toán dọn dẹp HTML.



---