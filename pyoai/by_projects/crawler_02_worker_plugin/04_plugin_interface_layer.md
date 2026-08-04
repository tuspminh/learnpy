# Buổi 4 — Xây dựng Plugin Interface Layer

Đây là một trong những buổi quan trọng nhất của toàn bộ framework.

Nếu thiết kế **Plugin Interface** tốt, sau này bạn có thể:

* Thêm website mới mà **không sửa Worker**
* Thêm API source mà **không sửa Database**
* Test plugin **không cần Internet**
* Mock plugin để kiểm thử
* Hot reload plugin
* Plugin marketplace (sau này)

---

# Mục tiêu buổi học

Sau buổi này chúng ta sẽ có:

```
Worker
    │
    ▼
CrawlerPlugin (ABC)
    │
 ┌──┴─────────────┐
 │                │
 ▼                ▼
NovelBin      TruyenFull
Plugin         Plugin
```

Điểm quan trọng:

> **Worker chỉ biết `CrawlerPlugin`, không biết `NovelBinPlugin` hay `TruyenFullPlugin`.**

Đây chính là nguyên lý **Dependency Inversion Principle (DIP)**.

---

# 1. Kiến trúc Plugin

```
crawler/
│
├── core/
│
│   ├── plugin/
│   │
│   ├── base.py
│   ├── capability.py
│   ├── metadata.py
│   ├── registry.py
│   ├── manager.py
│   ├── exceptions.py
│   └── context.py
│
├── plugins/
│
│   ├── novelbin/
│   │
│   ├── truyenfull/
│   │
│   └── tangthuvien/
```

---

# 2. Plugin là gì?

Plugin là adapter giữa website và framework.

Website:

```
https://abc.com
```

↓

Plugin

↓

```
Book
Chapter
Image
```

Plugin **không được** lưu SQLite.

Plugin **không được** gọi Repository.

Plugin chỉ làm:

```
HTTP

↓

HTML

↓

Model
```

---

# 3. Base Plugin

Tạo:

```
core/plugin/base.py
```

```python
from abc import ABC, abstractmethod

from crawler.core.models.book import Book
from crawler.core.models.chapter import Chapter


class CrawlerPlugin(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def domain(self) -> str:
        ...

    @abstractmethod
    def get_book(self, url: str) -> Book:
        ...

    @abstractmethod
    def get_chapters(self, url: str) -> list[Chapter]:
        ...

    @abstractmethod
    def get_chapter(self, url: str) -> Chapter:
        ...
```

Đây là interface tối thiểu.

---

# 4. Vì sao dùng `ABC`?

Nếu dùng:

```python
class Plugin:
    pass
```

thì ai cũng có thể viết:

```python
class MyPlugin(Plugin):
    pass
```

Nhưng lại quên:

```
get_book()

get_chapters()
```

Worker sẽ crash.

ABC buộc plugin phải triển khai đầy đủ.

---

# 5. Plugin Metadata

Mỗi plugin cần metadata.

```
name

version

author

website

priority
```

Ví dụ:

```python
from dataclasses import dataclass


@dataclass(slots=True)
class PluginMetadata:

    name: str

    version: str

    author: str

    website: str
```

Plugin:

```python
metadata = PluginMetadata(
    name="NovelBin",
    version="1.0.0",
    author="Garden",
    website="https://..."
)
```

---

# 6. Capability

Không phải website nào cũng có cùng tính năng.

Ví dụ:

Website A

```
✔ Search

✔ Book

✔ Chapter
```

Website B

```
✔ Book

✔ Chapter

✘ Search
```

Ta tạo enum:

```python
from enum import Enum


class Capability(Enum):

    SEARCH = "search"

    BOOK = "book"

    CHAPTER = "chapter"

    IMAGE = "image"

    CATEGORY = "category"
```

Plugin khai báo:

```python
capabilities = {
    Capability.SEARCH,
    Capability.BOOK,
    Capability.CHAPTER,
}
```

Worker sẽ biết plugin hỗ trợ gì trước khi gọi.

---

# 7. Plugin Context

Plugin cần thông tin chung:

```
timeout

headers

cookies

proxy

logger
```

Không nên truyền từng biến.

Tạo:

```python
from dataclasses import dataclass


@dataclass
class PluginContext:

    timeout: int = 20

    user_agent: str = "Crawler"

    verify_ssl: bool = True
```

Plugin:

```python
plugin = NovelBinPlugin(context)
```

---

# 8. Mock Plugin

Đây là bí quyết giúp test toàn bộ framework mà không cần Internet.

```python
class MockPlugin(CrawlerPlugin):

    @property
    def name(self):
        return "mock"

    @property
    def domain(self):
        return "mock.local"

    def get_book(self, url):

        return Book(
            title="Demo",
            author="OpenAI"
        )

    def get_chapters(self, url):

        return []

    def get_chapter(self, url):

        return Chapter(
            title="Chapter 1",
            content="Hello"
        )
```

Worker dùng MockPlugin sẽ hoạt động như đang crawl thật.

---

# 9. Plugin Registry

Thay vì:

```python
if site == "novelbin":
    ...

elif site == "truyenfull":
    ...
```

Ta tạo Registry.

```python
class PluginRegistry:

    def __init__(self):

        self._plugins = {}

    def register(self, plugin):

        self._plugins[plugin.name] = plugin

    def get(self, name):

        return self._plugins[name]

    def names(self):

        return list(self._plugins)
```

Đăng ký:

```python
registry.register(MockPlugin())
```

Lấy:

```python
plugin = registry.get("mock")
```

---

# 10. Plugin Manager

Manager chịu trách nhiệm:

```
scan folder

↓

import plugin

↓

register

↓

kiểm tra version

↓

kiểm tra capability
```

Hiện tại chỉ cần:

```python
manager.load_plugins()
```

Buổi sau sẽ dùng `importlib` để tự động quét plugin.

---

# 11. CLI kiểm thử

Chúng ta sẽ có các lệnh:

```bash
python -m crawler plugin list
```

Ví dụ:

```
Installed plugins

mock

novelbin

truyenfull
```

---

Thông tin plugin:

```bash
python -m crawler plugin info mock
```

Kết quả:

```
Name

Version

Author

Capabilities
```

---

Kiểm tra plugin:

```bash
python -m crawler plugin doctor mock
```

Output:

```
✓ get_book()

✓ get_chapters()

✓ get_chapter()

PASS
```

Lệnh này rất hữu ích khi phát triển plugin mới.

---

# 12. Unit Test

Ví dụ:

```python
def test_registry():

    registry = PluginRegistry()

    registry.register(MockPlugin())

    assert "mock" in registry.names()
```

Kiểm tra metadata:

```python
def test_metadata():

    plugin = MockPlugin()

    assert plugin.name == "mock"
```

---

# 13. Kiến trúc sau Buổi 4

```
core/
│
├── plugin/
│
├── base.py
├── capability.py
├── metadata.py
├── registry.py
├── manager.py
├── context.py
└── exceptions.py
```

```
plugins/
│
├── mock/
│   └── plugin.py
│
├── novelbin/
│
└── truyenfull/
```

---

# Bài tập

1. Xây dựng `CrawlerPlugin` bằng `abc.ABC`.
2. Tạo `PluginMetadata`.
3. Tạo `Capability` bằng `Enum`.
4. Tạo `PluginContext`.
5. Viết `MockPlugin` trả về dữ liệu giả.
6. Xây dựng `PluginRegistry` với các phương thức:

   * `register()`
   * `unregister()`
   * `get()`
   * `names()`
   * `exists()`
7. Thêm các lệnh CLI:

   * `plugin list`
   * `plugin info`
   * `plugin doctor`
8. Viết unit test cho `MockPlugin` và `PluginRegistry`.

---

## Chuẩn bị cho Buổi 5

Ở buổi tiếp theo, chúng ta sẽ xây dựng **Plugin Loader & Discovery System**, bao gồm:

* Tự động quét thư mục `plugins/`
* Nạp plugin bằng `importlib`
* Đăng ký plugin tự động vào `PluginRegistry`
* Kiểm tra phiên bản, metadata và khả năng tương thích
* Hỗ trợ bật/tắt plugin bằng cấu hình
* Kiểm thử toàn bộ quy trình bằng CLI (`plugin scan`, `plugin load`, `plugin reload`) mà chưa cần kết nối tới website thật. Đây sẽ là nền tảng để sau này chỉ cần thả một thư mục plugin mới vào `plugins/` là framework có thể nhận diện và sử dụng ngay.
