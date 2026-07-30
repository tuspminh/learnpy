# Plugin Architecture Deep Dive

# Buổi 5: Plugin Discovery - Tự động phát hiện Plugin

> **Mục tiêu**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu Discovery là gì. 
>   * Thành thạo `pathlib`, `pkgutil`, `importlib.util`. 
>   * Tự động quét thư mục plugin. 
>   * Phát hiện package hợp lệ. 
>   * Kết hợp Discovery + Loader. 
>   * Hoàn thành Plugin Framework v1. 
> 


* * *

# Roadmap
    
    
    Phần I - Tư duy Plugin
    
    ✓ Buổi 1 : Plugin là gì
    ✓ Buổi 2 : Plugin Contract
    ✓ Buổi 3 : importlib
    ✓ Buổi 4 : inspect
    ➜ Buổi 5 : Plugin Discovery

Sau buổi hôm nay, framework của chúng ta sẽ có thể:
    
    
    plugins/
        truyenfull/
        wattpad/
        novelbin/
        metruyen/

Bạn chỉ cần tạo thêm thư mục `metruyen`.

Framework sẽ tự động:

  * phát hiện 
  * import 
  * khởi tạo 
  * đăng ký 



Không sửa một dòng code nào.

Đây chính là mục tiêu của Plugin Architecture.

* * *

# 1\. Discovery là gì?

Plugin Loader chỉ biết:
    
    
    loader.load("plugins.truyenfull")

Nhưng...

Làm sao Loader biết:
    
    
    plugins.truyenfull
    plugins.wattpad
    plugins.novelbin

Đây là nhiệm vụ của

> **Plugin Discovery**

Discovery = tìm plugin.

* * *

# 2\. Kiến trúc
    
    
    plugins/
    
        truyenfull/
    
        wattpad/
    
        novelbin/
    
        metruyen/

Framework

↓

Quét folder

↓

Tìm package

↓

Import

↓

inspect

↓

BasePlugin

↓

Registry

* * *

# 3\. Có những cách Discovery nào?

Python có khá nhiều cách.

Cách| Dùng khi  
---|---  
pathlib| Quét thư mục  
os.walk| Hệ thống cũ  
pkgutil| Package Python  
importlib.metadata| Plugin cài bằng pip  
Entry Point| Framework chuyên nghiệp  
  
Trong phần đầu khóa học chúng ta sẽ học

> pathlib + pkgutil

Đây là nền tảng của hầu hết Plugin Framework.

* * *

# 4\. pathlib

Ví dụ
    
    
    plugins/
    
        truyenfull/
    
        wattpad/
    
        novelbin/
    
    
    from pathlib import Path
    
    plugins = Path("plugins")

Liệt kê
    
    
    for item in plugins.iterdir():
    
        print(item)

Kết quả
    
    
    plugins/truyenfull
    
    plugins/wattpad
    
    plugins/novelbin

* * *

# 5\. Chỉ lấy thư mục
    
    
    for item in plugins.iterdir():
    
        if item.is_dir():
    
            print(item.name)

↓
    
    
    truyenfull
    
    wattpad
    
    novelbin

* * *

# 6\. Chuyển thành module name

Framework cần
    
    
    plugins.truyenfull

không phải
    
    
    plugins/truyenfull

Ta làm
    
    
    module_name = f"plugins.{item.name}"

↓
    
    
    plugins.truyenfull

* * *

# 7\. Discovery đầu tiên
    
    
    from pathlib import Path
    
    
    class PluginDiscovery:
    
        def discover(self):
    
            plugins = []
    
            root = Path("plugins")
    
            for item in root.iterdir():
    
                if item.is_dir():
    
                    plugins.append(
                        f"plugins.{item.name}"
                    )
    
            return plugins

Kết quả
    
    
    [
        "plugins.truyenfull",
        "plugins.wattpad",
        "plugins.novelbin"
    ]

* * *

# 8\. Nhưng có bug!

Giả sử
    
    
    plugins/
    
        __pycache__/
    
        docs/
    
        image/
    
        truyenfull/

Framework sẽ nhận luôn
    
    
    docs
    
    image

Không đúng.

Ta cần lọc.

* * *

# 9\. Package Python

Một package truyền thống có
    
    
    plugins/
    
        truyenfull/
    
            __init__.py

Kiểm tra
    
    
    (item / "__init__.py").exists()

Ví dụ
    
    
    if (
        item.is_dir()
        and (item / "__init__.py").exists()
    ):
        ...

Đây là cách đơn giản để xác định package trước PEP 420.

* * *

# 10\. pkgutil

Python cung cấp
    
    
    import pkgutil

Đây là cách chuyên nghiệp hơn.

Ví dụ
    
    
    import plugins
    
    import pkgutil
    
    
    for info in pkgutil.iter_modules(
        plugins.__path__
    ):
    
        print(info.name)

↓
    
    
    truyenfull
    
    wattpad
    
    novelbin

Ưu điểm

Không cần quan tâm hệ điều hành.

* * *

# 11\. ModuleInfo

`pkgutil`

trả về
    
    
    ModuleInfo

Có
    
    
    info.name

↓
    
    
    truyenfull
    
    
    info.ispkg

↓
    
    
    True

* * *

# 12\. Discovery bằng pkgutil
    
    
    import pkgutil
    
    import plugins
    
    
    class PluginDiscovery:
    
        def discover(self):
    
            modules = []
    
            for info in pkgutil.iter_modules(
                plugins.__path__
            ):
    
                modules.append(
                    f"plugins.{info.name}"
                )
    
            return modules

Đây là cách thường dùng trong nhiều framework Python.

* * *

# 13\. Kết hợp Loader

Discovery

↓
    
    
    [
        "plugins.truyenfull",
        "plugins.wattpad"
    ]

Loader

↓
    
    
    plugin = loader.load(name)

Framework

↓
    
    
    plugins = []
    
    for name in discovery.discover():
    
        plugins.extend(
            loader.load(name)
        )

Đây chính là Plugin Framework đầu tiên.

* * *

# 14\. Kiến trúc hoàn chỉnh
    
    
                   Discovery
    
                        │
    
                        ▼
    
           plugins.truyenfull
    
           plugins.wattpad
    
           plugins.novelbin
    
                        │
    
                        ▼
    
                    Loader
    
                        │
    
                 importlib
    
                        │
    
                   inspect
    
                        │
    
                 BasePlugin
    
                        │
    
                  instantiate
    
                        │
    
                    Plugin

* * *

# 15\. Viết Framework
    
    
    class PluginFramework:
    
        def __init__(
    
            self,
    
            discovery,
    
            loader
    
        ):
    
            self.discovery = discovery
    
            self.loader = loader
    
        def load_plugins(self):
    
            plugins = []
    
            for module in self.discovery.discover():
    
                plugins.extend(
    
                    self.loader.load(module)
    
                )
    
            return plugins

Đã là Framework đúng nghĩa.

* * *

# 16\. Plugin mới

Ban đầu
    
    
    plugins/
    
        truyenfull/
    
        wattpad/

Framework

↓
    
    
    2 plugins

Ngày mai
    
    
    plugins/
    
        truyenfull/
    
        wattpad/
    
        metruyen/

Không sửa Framework.

Framework

↓
    
    
    3 plugins

Đó chính là Open/Closed Principle.

* * *

# 17\. Thêm Registry

Thay vì
    
    
    plugins = []

Ta tạo
    
    
    registry = {}
    
    
    registry[plugin.name] = plugin

↓
    
    
    registry["TruyenFull"]
    
    registry["Wattpad"]

Đây sẽ là nội dung buổi 6.

* * *

# 18\. Thêm cấu trúc chuẩn

Để dự án dễ mở rộng, chúng ta thống nhất mỗi plugin có cấu trúc:
    
    
    plugins/
    │
    ├── truyenfull/
    │   ├── __init__.py
    │   ├── plugin.py
    │   ├── parser.py
    │   └── config.py
    │
    ├── wattpad/
    │   ├── __init__.py
    │   ├── plugin.py
    │   ├── parser.py
    │   └── config.py
    │
    └── novelbin/
        ├── __init__.py
        ├── plugin.py
        ├── parser.py
        └── config.py

Sau này `plugin.py` sẽ chứa class kế thừa `BasePlugin`, còn `parser.py` chỉ là helper.

* * *

# 19\. Hạn chế của Discovery hiện tại

Framework mới chỉ tìm thấy plugin.

Chưa có:

  * Version 
  * Dependency 
  * Enable/Disable 
  * Lifecycle 
  * Metadata 
  * Config 



Ví dụ
    
    
    Plugin
    
    ↓
    
    Load
    
    ↓
    
    ???
    
    ↓
    
    Ready

Dấu `???` chính là

> **Lifecycle**

* * *

# 20\. Plugin Framework v1

Đến đây chúng ta đã có:
    
    
    Plugin Framework
    
            │
    
            ▼
    
    Discovery
    
            │
    
            ▼
    
    Loader
    
            │
    
            ▼
    
    inspect
    
            │
    
            ▼
    
    Plugin Instance

Đây là kiến trúc tối thiểu của một Plugin Framework.

* * *

# Ví dụ hoàn chỉnh (Framework v1)

Đây là phiên bản gộp ba thành phần Discovery + Loader + Framework:
    
    
    from pathlib import Path
    import importlib
    import inspect
    
    from interfaces import BasePlugin
    
    
    class PluginDiscovery:
        def discover(self):
            root = Path("plugins")
            modules = []
    
            for item in root.iterdir():
                if item.is_dir() and (item / "__init__.py").exists():
                    modules.append(f"plugins.{item.name}")
    
            return modules
    
    
    class PluginLoader:
        def load(self, module_name):
            module = importlib.import_module(module_name)
    
            plugins = []
    
            for _, cls in inspect.getmembers(module, inspect.isclass):
                if issubclass(cls, BasePlugin) and cls is not BasePlugin:
                    plugins.append(cls())
    
            return plugins
    
    
    class PluginFramework:
        def __init__(self):
            self.discovery = PluginDiscovery()
            self.loader = PluginLoader()
    
        def load_plugins(self):
            result = []
    
            for module_name in self.discovery.discover():
                result.extend(self.loader.load(module_name))
    
            return result

Đây chưa phải phiên bản cuối cùng, nhưng đã thể hiện đầy đủ luồng xử lý của một plugin framework cơ bản.

* * *

# Best Practices

## 1\. Discovery và Loader phải tách riêng

❌ Sai
    
    
    discover()
    
    ↓
    
    import()
    
    ↓
    
    instantiate()

tất cả trong một class.

✔ Đúng
    
    
    Discovery
    
    ↓
    
    Loader
    
    ↓
    
    Registry

Mỗi class chỉ có một trách nhiệm (Single Responsibility Principle).

* * *

## 2\. Không dùng `os.listdir()` nếu đã dùng `pathlib`

`pathlib`:

  * dễ đọc, 
  * hướng đối tượng, 
  * đa nền tảng, 
  * kết hợp tốt với `importlib`. 



* * *

## 3\. Chuẩn hóa cấu trúc plugin

Mọi plugin nên tuân theo cùng một layout để Discovery không phải xử lý nhiều ngoại lệ.

* * *

# Bài tập

## Bài 1

Viết `PluginDiscovery` sử dụng `pathlib`:
    
    
    discover() -> list[str]

Trả về:
    
    
    [
        "plugins.truyenfull",
        "plugins.wattpad"
    ]

* * *

## Bài 2

Viết lại `PluginDiscovery` bằng `pkgutil.iter_modules()` và so sánh ưu, nhược điểm với cách dùng `pathlib`.

* * *

## Bài 3

Ghép ba thành phần:

  * `PluginDiscovery`
  * `PluginLoader`
  * `PluginFramework`



để chương trình có thể tự động nạp tất cả plugin trong thư mục `plugins/`.

* * *

# Chuẩn bị cho Buổi 6

Đến đây, framework đã có thể:

  * Khám phá plugin. 
  * Import động. 
  * Tìm class plugin. 
  * Khởi tạo instance. 



Nhưng một câu hỏi mới xuất hiện:

> Sau khi nạp 100 plugin, **lưu chúng ở đâu để tìm kiếm, bật/tắt và quản lý hiệu quả?**

Đó chính là vai trò của **Plugin Registry** và **Plugin Manager**.

Ở **Buổi 6** , chúng ta sẽ xây dựng **Registry Pattern** , giúp framework quản lý plugin theo tên, loại, trạng thái và metadata — một thành phần không thể thiếu trong các hệ thống plugin chuyên nghiệp như VS Code, pytest hay Home Assistant.

