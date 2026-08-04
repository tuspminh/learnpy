# Buổi 5 — Xây dựng Plugin Loader & Discovery System

Đây là buổi học đưa framework từ mức **"có plugin"** lên **"quản lý plugin tự động"**.

Sau buổi này, bạn sẽ có một hệ thống mà chỉ cần thêm một thư mục plugin mới vào `plugins/`, framework sẽ tự phát hiện, kiểm tra và đăng ký plugin mà không cần sửa bất kỳ dòng mã nào trong `Worker`.

---

# Mục tiêu

Sau buổi học, framework sẽ hoạt động như sau:

```text
                plugins/

        ┌──────────┬──────────┬──────────┐
        │          │          │
   novelbin   truyenfull   tangthuvien
        │          │          │
        └──────┬───┴──────────┘
               │
         Plugin Loader
               │
               ▼
        Plugin Registry
               │
               ▼
         Crawl Worker
```

---

# 1. Discovery là gì?

Discovery là quá trình:

```text
plugins/

↓

quét thư mục

↓

tìm plugin hợp lệ

↓

import

↓

khởi tạo

↓

đăng ký Registry
```

Thay vì:

```python
registry.register(NovelBinPlugin())
registry.register(TruyenFullPlugin())
```

chúng ta sẽ làm hoàn toàn tự động.

---

# 2. Chuẩn hóa cấu trúc Plugin

Mỗi plugin phải tuân theo cùng một cấu trúc:

```text
plugins/
│
├── novelbin/
│
│   ├── __init__.py
│   ├── plugin.py
│   ├── parser.py
│   ├── config.py
│   └── manifest.py
│
├── truyenfull/
│
│   ├── __init__.py
│   ├── plugin.py
│   ├── parser.py
│   ├── config.py
│   └── manifest.py
```

Không tuân thủ cấu trúc → Loader bỏ qua.

---

# 3. Plugin Manifest

Mỗi plugin có một `manifest.py`.

Ví dụ:

```python
PLUGIN_NAME = "novelbin"

PLUGIN_VERSION = "1.0.0"

PLUGIN_CLASS = "NovelBinPlugin"

AUTHOR = "Garden"
```

Tại sao cần manifest?

* Không cần import toàn bộ plugin để lấy metadata.
* Kiểm tra phiên bản nhanh.
* Hiển thị thông tin plugin trên CLI.

Sau này có thể chuyển sang `manifest.toml` hoặc `manifest.json` mà không ảnh hưởng kiến trúc.

---

# 4. PluginLoader

Tạo:

```text
core/plugin/loader.py
```

```python
from pathlib import Path

class PluginLoader:

    def __init__(self, plugin_dir: Path):
        self.plugin_dir = plugin_dir
```

Nhiệm vụ:

* Quét thư mục.
* Kiểm tra cấu trúc.
* Import plugin.
* Khởi tạo.
* Trả về danh sách plugin.

---

# 5. Quét thư mục Plugin

```python
from pathlib import Path

plugin_dir = Path("src/crawler/plugins")

for path in plugin_dir.iterdir():

    if path.is_dir():

        print(path.name)
```

Kết quả:

```text
novelbin

truyenfull

mock
```

---

# 6. Kiểm tra Plugin hợp lệ

Plugin hợp lệ phải có:

```text
plugin.py

__init__.py
```

Ví dụ:

```python
plugin_file = path / "plugin.py"

if not plugin_file.exists():
    continue
```

Có thể mở rộng:

```text
plugin.py

manifest.py

config.py
```

---

# 7. Dynamic Import bằng `importlib`

Đây là kỹ thuật quan trọng.

Ví dụ:

```python
import importlib

module = importlib.import_module(
    "crawler.plugins.novelbin.plugin"
)
```

Bây giờ Python import động thay vì hard-code.

---

# 8. Quy ước Plugin Class

Mỗi `plugin.py` cần xuất ra:

```python
PLUGIN_CLASS = NovelBinPlugin
```

Ví dụ:

```python
class NovelBinPlugin(CrawlerPlugin):
    ...
    
PLUGIN_CLASS = NovelBinPlugin
```

Loader:

```python
plugin_cls = module.PLUGIN_CLASS

plugin = plugin_cls(context)
```

Ưu điểm:

* Không cần biết tên lớp.
* Không dùng `getattr()` theo tên chuỗi.
* Giảm lỗi khi đổi tên class.

---

# 9. Đăng ký vào Registry

```python
plugin = plugin_cls(context)

registry.register(plugin)
```

Lúc này:

```python
registry.names()
```

Kết quả:

```text
[
    "novelbin",
    "truyenfull",
    "mock"
]
```

---

# 10. Plugin State

Mỗi plugin có trạng thái:

```python
from enum import Enum

class PluginState(Enum):

    ENABLED = "enabled"

    DISABLED = "disabled"

    ERROR = "error"

    LOADED = "loaded"
```

Ví dụ:

```text
novelbin      ENABLED

mock          LOADED

abc           ERROR
```

Worker chỉ sử dụng plugin ở trạng thái `ENABLED`.

---

# 11. Plugin Compatibility

Ví dụ:

Framework:

```text
2.0.0
```

Plugin:

```text
supports

>=2.0

<3.0
```

Nếu không tương thích:

```text
Skip plugin
```

Manifest có thể thêm:

```python
FRAMEWORK_VERSION = ">=0.1,<1.0"
```

Đây là nền tảng để sau này phát triển marketplace.

---

# 12. Plugin Config

Mỗi plugin có thể có cấu hình riêng:

```text
plugins/

novelbin/

config.py
```

Ví dụ:

```python
TIMEOUT = 20

RETRY = 3

USER_AGENT = "Crawler"
```

Hoặc sau này:

```toml
timeout = 20

retry = 3
```

Loader sẽ đọc và truyền vào `PluginContext`.

---

# 13. CLI kiểm thử

### Quét plugin

```bash
python -m crawler plugin scan
```

Ví dụ:

```text
Scanning plugins...

✓ mock

✓ novelbin

✓ truyenfull

3 plugin(s) found.
```

---

### Nạp plugin

```bash
python -m crawler plugin load
```

Ví dụ:

```text
Loading plugins...

✓ mock

✓ novelbin

✓ truyenfull
```

---

### Reload

```bash
python -m crawler plugin reload
```

Thực hiện:

```text
Unload

↓

Clear Registry

↓

Load lại
```

Rất hữu ích trong quá trình phát triển.

---

### Hiển thị trạng thái

```bash
python -m crawler plugin status
```

Ví dụ:

```text
NAME           VERSION    STATE

mock           1.0.0      ENABLED

novelbin       1.0.0      ENABLED

truyenfull     1.0.0      ERROR
```

---

# 14. Unit Test

Ví dụ:

```python
def test_loader():

    loader = PluginLoader(plugin_dir)

    plugins = loader.scan()

    assert len(plugins) > 0
```

Kiểm tra import:

```python
def test_import():

    plugin = loader.load("mock")

    assert plugin.name == "mock"
```

Kiểm tra Registry:

```python
def test_registry():

    registry = PluginRegistry()

    registry.register(plugin)

    assert registry.exists("mock")
```

---

# 15. Kiến trúc sau Buổi 5

```text
core/
│
├── plugin/
│
├── base.py
├── context.py
├── capability.py
├── metadata.py
├── registry.py
├── loader.py
├── manager.py
├── state.py
└── exceptions.py
```

```text
plugins/
│
├── mock/
│
│   ├── __init__.py
│   ├── plugin.py
│   ├── manifest.py
│   └── config.py
│
├── novelbin/
│
└── truyenfull/
```

---

# Luồng hoạt động hoàn chỉnh

```text
python -m crawler plugin load

        │
        ▼

PluginLoader.scan()

        │
        ▼

PluginLoader.import()

        │
        ▼

Instantiate Plugin

        │
        ▼

Validate Metadata

        │
        ▼

Registry.register()

        │
        ▼

Worker sử dụng Plugin
```

---

# Bài tập

1. Xây dựng `PluginLoader` có các phương thức:

   * `scan()`
   * `load(name)`
   * `load_all()`
2. Chuẩn hóa cấu trúc thư mục plugin.
3. Thêm `manifest.py` cho `MockPlugin`.
4. Tạo `PluginState`.
5. Kiểm tra tính tương thích phiên bản framework và plugin.
6. Bổ sung các lệnh CLI:

   * `plugin scan`
   * `plugin load`
   * `plugin reload`
   * `plugin status`
7. Viết unit test cho:

   * Discovery
   * Dynamic import
   * Registry
   * Compatibility
   * Plugin state

---

# Chuẩn bị cho Buổi 6

Buổi tiếp theo chúng ta sẽ xây dựng **HTTP Client Layer** – một lớp mạng thống nhất mà **mọi plugin đều sử dụng**. Nội dung bao gồm:

* Thiết kế `Request` và `Response` model.
* `HttpClient` interface và cài đặt mặc định bằng `requests`.
* Quản lý `Session`, cookie, header và `User-Agent`.
* Timeout, retry với exponential backoff.
* Proxy, SSL, redirect.
* Middleware trước/sau request (logging, cache, rate limit).
* Mock HTTP Client để test plugin hoàn toàn offline.
* CLI kiểm thử:

  * `crawler http get <url>`
  * `crawler http head <url>`
  * `crawler http benchmark <url>`

Từ buổi này trở đi, **mọi plugin sẽ bị cấm gọi `requests.get()` trực tiếp**; tất cả truy cập mạng đều phải đi qua `HttpClient`, giúp việc kiểm thử, logging và thay đổi thư viện HTTP trở nên dễ dàng và nhất quán.
