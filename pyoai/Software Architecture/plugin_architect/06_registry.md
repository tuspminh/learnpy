# Plugin Architecture Deep Dive

# Buổi 6: Plugin Registry & Plugin Manager - Trái tim của Plugin Framework

> **Mục tiêu**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu Registry Pattern. 
>   * Phân biệt Plugin Loader và Plugin Manager. 
>   * Xây dựng Plugin Registry chuyên nghiệp. 
>   * Quản lý plugin theo tên, loại và trạng thái. 
>   * Chuẩn bị nền tảng cho Lifecycle (Buổi 7). 
> 


* * *

# Roadmap
    
    
    Phần I - Tư duy Plugin
    
    ✓ Buổi 1 : Plugin là gì
    ✓ Buổi 2 : Plugin Contract
    ✓ Buổi 3 : importlib
    ✓ Buổi 4 : inspect
    ✓ Buổi 5 : Plugin Discovery
    
    Phần II - Plugin Loader
    
    ➜ Buổi 6 : Registry & Manager
    □ Buổi 7 : Plugin Lifecycle
    □ Buổi 8 : Dependency Injection
    □ Buổi 9 : Hot Reload
    □ Buổi 10 : Version Compatibility

* * *

# 1\. Hệ thống hiện tại

Hiện tại chúng ta đã có
    
    
    Discovery
    
    ↓
    
    Loader
    
    ↓
    
    Plugin Instance

Ví dụ
    
    
    plugins = framework.load_plugins()

Kết quả
    
    
    [
        TruyenFull(),
        Wattpad(),
        NovelBin()
    ]

Có vẻ ổn.

Nhưng...

* * *

# 2\. Vấn đề

Giả sử có
    
    
    plugins = [
    
        TruyenFull(),
    
        Wattpad(),
    
        NovelBin(),
    
        Metruyen(),
    
        RoyalRoad()
    ]

Muốn lấy
    
    
    NovelBin

Bạn phải
    
    
    for plugin in plugins:
    
        if plugin.name == "NovelBin":
    
            ...

Nếu có

  * 300 plugin 
  * 500 plugin 



thì rất chậm.

* * *

# 3\. Registry là gì?

Registry là nơi đăng ký (Register) tất cả plugin.

Giống như:

  * Danh bạ điện thoại 
  * Từ điển 
  * Danh sách nhân viên 



Ví dụ
    
    
    Plugin Registry
    
    ↓
    
    TruyenFull
    
    ↓
    
    Object

* * *

# 4\. Registry Pattern

Đây là một Design Pattern rất phổ biến.

Thay vì
    
    
    plugins = []

Ta dùng
    
    
    plugins = {}

Ví dụ
    
    
    plugins = {
    
        "TruyenFull": TruyenFull(),
    
        "Wattpad": Wattpad(),
    
        "NovelBin": NovelBin()
    }

Lấy plugin
    
    
    plugins["NovelBin"]

Độ phức tạp
    
    
    O(1)

* * *

# 5\. Vì sao Dictionary?

Giả sử có

1000 plugin

List
    
    
    NovelBin
    
    ↓
    
    Linear Search
    
    ↓
    
    O(n)

Dictionary
    
    
    NovelBin
    
    ↓
    
    Hash
    
    ↓
    
    O(1)

Đây là lý do gần như mọi Plugin Framework đều dùng Registry.

* * *

# 6\. Thiết kế PluginRegistry
    
    
    class PluginRegistry:
    
        def __init__(self):
    
            self._plugins = {}

Registry chỉ quản lý dữ liệu.

Không import.

Không discovery.

Không lifecycle.

* * *

# 7\. Register
    
    
    class PluginRegistry:
    
        def register(self, plugin):
    
            self._plugins[plugin.name] = plugin

Ví dụ
    
    
    registry.register(
    
        TruyenFull()
    )

↓
    
    
    {
        "TruyenFull": object
    }

* * *

# 8\. Get Plugin
    
    
    plugin = registry.get("TruyenFull")

Cài đặt
    
    
    def get(self, name):
    
        return self._plugins[name]

Hoặc an toàn hơn
    
    
    def get(self, name):
    
        return self._plugins.get(name)

* * *

# 9\. Tại sao dùng `dict.get()`?

Sai
    
    
    plugin = registry._plugins[name]

Nếu không tồn tại

↓
    
    
    KeyError

Đúng
    
    
    plugin = registry._plugins.get(name)

↓
    
    
    None

Framework sẽ dễ xử lý hơn.

* * *

# 10\. Remove Plugin
    
    
    def unregister(self, name):
    
        self._plugins.pop(name, None)

Không lỗi nếu plugin không tồn tại.

* * *

# 11\. Kiểm tra tồn tại
    
    
    def contains(self, name):
    
        return name in self._plugins

Ví dụ
    
    
    registry.contains("NovelBin")

↓
    
    
    True

* * *

# 12\. Liệt kê Plugin
    
    
    def all(self):
    
        return list(
            self._plugins.values()
        )

Hoặc
    
    
    for plugin in registry.all():
    
        print(plugin.name)

* * *

# 13\. Registry đầy đủ
    
    
    class PluginRegistry:
    
        def __init__(self):
    
            self._plugins = {}
    
        def register(self, plugin):
    
            self._plugins[plugin.name] = plugin
    
        def unregister(self, name):
    
            self._plugins.pop(name, None)
    
        def get(self, name):
    
            return self._plugins.get(name)
    
        def contains(self, name):
    
            return name in self._plugins
    
        def all(self):
    
            return list(self._plugins.values())

Đây là phiên bản đầu tiên.

* * *

# 14\. Plugin Manager là gì?

Đây là phần rất nhiều người nhầm.

Registry

↓

Chỉ lưu dữ liệu.

Manager

↓

Điều khiển.

* * *

Ví dụ
    
    
    Manager
    
    ↓
    
    Load
    
    Enable
    
    Disable
    
    Shutdown
    
    Reload

Manager sử dụng Registry.

* * *

# 15\. Quan hệ giữa các thành phần
    
    
            PluginManager
    
                  │
    
          ┌───────┼────────┐
    
          ▼       ▼        ▼
    
     Discovery  Loader  Registry

Manager giống như "nhạc trưởng".

* * *

# 16\. PluginManager v1
    
    
    class PluginManager:
    
        def __init__(
    
            self,
    
            discovery,
    
            loader,
    
            registry
    
        ):
    
            self.discovery = discovery
    
            self.loader = loader
    
            self.registry = registry

* * *

# 17\. Load tất cả Plugin
    
    
    def load_plugins(self):
    
        modules = self.discovery.discover()
    
        for module in modules:
    
            plugins = self.loader.load(module)
    
            for plugin in plugins:
    
                self.registry.register(plugin)

Kết quả
    
    
    Discovery
    
    ↓
    
    Loader
    
    ↓
    
    Registry

* * *

# 18\. Tìm Plugin
    
    
    plugin = manager.registry.get(
        "TruyenFull"
    )

Sau này sẽ đổi thành
    
    
    manager.get_plugin(
        "TruyenFull"
    )

Manager che giấu Registry.

* * *

# 19\. Kiến trúc hoàn chỉnh
    
    
                   PluginManager
    
                          │
    
         ┌────────────────┼────────────────┐
    
         ▼                ▼                ▼
    
    Discovery          Loader          Registry
    
         │                │                │
    
         └────────────┬───┘                │
    
                      ▼                    │
    
                 Plugin Object─────────────┘

* * *

# 20\. Luồng hoạt động
    
    
    Application
    
    ↓
    
    PluginManager
    
    ↓
    
    Discovery
    
    ↓
    
    plugins.truyenfull
    
    ↓
    
    Loader
    
    ↓
    
    importlib
    
    ↓
    
    inspect
    
    ↓
    
    Plugin()
    
    ↓
    
    Registry
    
    ↓
    
    Application sử dụng

* * *

# 21\. Vấn đề mới

Giả sử
    
    
    registry.register(plugin)

Plugin đã được lưu.

Nhưng

Plugin có sẵn sàng chưa?

Ví dụ
    
    
    class TruyenFull:
    
        def initialize(self):
    
            self.session = requests.Session()

Nếu chưa gọi
    
    
    initialize()

Plugin chưa dùng được.

* * *

# 22\. Lifecycle xuất hiện

Một plugin không chỉ có
    
    
    Load
    
    ↓
    
    Done

Mà sẽ có
    
    
    Load
    
    ↓
    
    Validate
    
    ↓
    
    Initialize
    
    ↓
    
    Enable
    
    ↓
    
    Running
    
    ↓
    
    Disable
    
    ↓
    
    Shutdown

Đây gọi là

> Plugin Lifecycle

Buổi sau sẽ học rất sâu.

* * *

# 23\. Cải tiến Registry bằng Metadata

Hiện tại
    
    
    _plugins = {
    
        "TruyenFull": plugin
    }

Sau này có thể lưu
    
    
    _plugins = {
    
        "TruyenFull": {
    
            "plugin": plugin,
    
            "enabled": True,
    
            "version": "1.2",
    
            "author": "Garden",
    
            "loaded": True
        }
    }

Hoặc tốt hơn, dùng một lớp dữ liệu:
    
    
    from dataclasses import dataclass
    
    @dataclass
    class PluginRecord:
        plugin: BasePlugin
        enabled: bool = False
        version: str = ""
        author: str = ""

Cách này giúp Registry dễ mở rộng và type-safe hơn.

* * *

# 24\. Kiến trúc mục tiêu của Story Framework
    
    
    StoryFramework/
    
    framework/
    
        discovery.py
    
        loader.py
    
        registry.py
    
        manager.py
    
        lifecycle.py
    
    interfaces/
    
    plugins/

Từ buổi sau, `PluginManager` sẽ không chỉ "nạp" plugin mà còn điều khiển toàn bộ vòng đời của chúng.

* * *

# Best Practices

## 1\. Registry không được import Plugin

Sai
    
    
    class Registry:
    
        import plugins

Registry chỉ lưu trữ.

* * *

## 2\. Manager điều phối

Manager gọi
    
    
    Discovery
    
    ↓
    
    Loader
    
    ↓
    
    Registry

Không làm thay công việc của từng thành phần.

* * *

## 3\. Không để Application truy cập trực tiếp Registry

Thay vì:
    
    
    manager.registry.get(...)

hãy cung cấp API:
    
    
    manager.get_plugin(...)

Điều này giúp sau này thay đổi cách lưu trữ mà không ảnh hưởng mã nguồn bên ngoài.

* * *

## 4\. Tránh trùng tên plugin

Nếu hai plugin cùng có:
    
    
    name = "Downloader"

thì plugin sau sẽ ghi đè plugin trước.

Giải pháp:

  * Kiểm tra khi `register()`. 
  * Hoặc dùng định danh duy nhất (ví dụ: `author.plugin_name` hoặc UUID). 



* * *

# Bài tập

## Bài 1

Viết `PluginRegistry` với các phương thức:
    
    
    register(plugin)
    
    unregister(name)
    
    get(name)
    
    contains(name)
    
    all()

* * *

## Bài 2

Viết `PluginManager` sử dụng:

  * `PluginDiscovery`
  * `PluginLoader`
  * `PluginRegistry`



để tự động nạp tất cả plugin.

* * *

## Bài 3

Mở rộng `register()` để từ chối plugin trùng tên:
    
    
    if registry.contains(plugin.name):
        raise ValueError(...)

* * *

# Chuẩn bị cho Buổi 7

Đến đây framework đã có:

  * ✅ Discovery 
  * ✅ Loader 
  * ✅ Reflection 
  * ✅ Registry 
  * ✅ Manager 



Nhưng vẫn còn thiếu phần quan trọng nhất:

> **Một plugin được nạp rồi thì khi nào được khởi tạo? Khi nào được bật? Khi nào được tắt?**

Đó là nội dung của **Buổi 7: Plugin Lifecycle** , nơi chúng ta sẽ xây dựng vòng đời hoàn chỉnh của plugin với các trạng thái như `Loaded`, `Initialized`, `Enabled`, `Disabled` và `Unloaded`, tương tự cách VS Code, Home Assistant và pytest quản lý extension của chúng.

