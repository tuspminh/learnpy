# Plugin Architecture Deep Dive

# Buổi 7: Plugin Lifecycle - Vòng đời hoàn chỉnh của Plugin

> **Mục tiêu**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu Lifecycle là gì. 
>   * Thiết kế vòng đời chuyên nghiệp cho Plugin. 
>   * Quản lý trạng thái Plugin. 
>   * Tách Load và Initialize. 
>   * Viết `LifecycleManager`. 
>   * Xây dựng nền tảng cho Dependency Injection (Buổi 8). 
> 


* * *

# Roadmap
    
    
    Phần I
    
    ✓ Buổi 1 : Plugin là gì
    ✓ Buổi 2 : Interface
    ✓ Buổi 3 : importlib
    ✓ Buổi 4 : inspect
    ✓ Buổi 5 : Discovery
    
    Phần II
    
    ✓ Buổi 6 : Registry & Manager
    ➜ Buổi 7 : Plugin Lifecycle
    □ Buổi 8 : Dependency Injection
    □ Buổi 9 : Hot Reload
    □ Buổi 10 : Version Compatibility

* * *

# 1\. Tại sao cần Lifecycle?

Hiện tại Framework làm việc như sau:
    
    
    Discovery
    
    ↓
    
    Loader
    
    ↓
    
    Plugin()
    
    ↓
    
    Registry

Đến đây plugin đã tồn tại.

Nhưng...

Plugin đã dùng được chưa?

Ví dụ
    
    
    class TruyenFull(BasePlugin):
    
        def initialize(self):
            self.session = requests.Session()

Sau khi gọi
    
    
    plugin = TruyenFull()

thì
    
    
    plugin.session

chưa tồn tại.

Framework phải gọi
    
    
    plugin.initialize()

* * *

# 2\. Constructor ≠ Initialize

Đây là sai lầm cực kỳ phổ biến.

Nhiều người viết
    
    
    class Plugin:
    
        def __init__(self):
    
            self.session = requests.Session()
    
            self.database = Database()
    
            self.redis = Redis()
    
            self.http = HttpClient()

Sai ở đâu?

* * *

Giả sử Framework chỉ muốn:
    
    
    Discovery

chưa muốn
    
    
    Connect Database

nhưng constructor đã chạy.

Không kiểm soát được.

* * *

Đúng hơn
    
    
    class Plugin:
    
        def __init__(self):
    
            self.session = None
    
        def initialize(self):
    
            self.session = requests.Session()

* * *

# 3\. Một Plugin có những trạng thái gì?

Một Plugin không chỉ có:
    
    
    Alive
    
    Dead

Mà có nhiều trạng thái.

Ví dụ
    
    
    Created
    
    ↓
    
    Loaded
    
    ↓
    
    Initialized
    
    ↓
    
    Enabled
    
    ↓
    
    Running
    
    ↓
    
    Disabled
    
    ↓
    
    Shutdown
    
    ↓
    
    Destroyed

Đây chính là

Lifecycle.

* * *

# 4\. Thiết kế State

Ta tạo Enum.
    
    
    from enum import Enum
    
    
    class PluginState(Enum):
    
        CREATED = "created"
    
        LOADED = "loaded"
    
        INITIALIZED = "initialized"
    
        ENABLED = "enabled"
    
        DISABLED = "disabled"
    
        SHUTDOWN = "shutdown"

Tại sao dùng `Enum` thay vì chuỗi?

  * Tránh lỗi chính tả (`"enable"` vs `"enabled"`). 
  * IDE hỗ trợ tự động hoàn thành. 
  * Dễ kiểm tra trạng thái hợp lệ. 



* * *

# 5\. PluginRecord

Ở buổi trước Registry lưu
    
    
    plugin

Bây giờ
    
    
    from dataclasses import dataclass
    
    
    @dataclass
    class PluginRecord:
    
        plugin: BasePlugin
    
        state: PluginState

Registry

↓
    
    
    {
        "TruyenFull":
    
            PluginRecord(...)
    }

Đây là cách mà nhiều framework hiện đại tổ chức dữ liệu.

* * *

# 6\. BasePlugin

Ta mở rộng Interface.
    
    
    from abc import ABC
    from abc import abstractmethod
    
    
    class BasePlugin(ABC):
    
        @abstractmethod
        def initialize(self):
            pass
    
        @abstractmethod
        def enable(self):
            pass
    
        @abstractmethod
        def disable(self):
            pass
    
        @abstractmethod
        def shutdown(self):
            pass

* * *

# 7\. LifecycleManager
    
    
    class LifecycleManager:
    
        def initialize(self, plugin):
    
            plugin.initialize()
    
        def enable(self, plugin):
    
            plugin.enable()
    
        def disable(self, plugin):
    
            plugin.disable()
    
        def shutdown(self, plugin):
    
            plugin.shutdown()

Đây mới chỉ là phiên bản đầu tiên.

* * *

# 8\. Cập nhật State
    
    
    class LifecycleManager:
    
        def initialize(self, record):
    
            record.plugin.initialize()
    
            record.state = PluginState.INITIALIZED

Sau khi gọi
    
    
    initialize()

Registry biết
    
    
    INITIALIZED

* * *

# 9\. Enable

Plugin có thể được load.

Nhưng chưa được sử dụng.

Ví dụ
    
    
    VSCode
    
    ↓
    
    Python Extension
    
    ↓
    
    Disabled

Plugin vẫn tồn tại.

Chỉ là chưa hoạt động.

Framework
    
    
    record.plugin.enable()
    
    record.state = ENABLED

* * *

# 10\. Disable

Ví dụ
    
    
    Plugin
    
    ↓
    
    Stop listening Event
    
    ↓
    
    Close Timer
    
    ↓
    
    Stop Worker

Không nhất thiết
    
    
    Destroy

Plugin vẫn nằm trong Registry.

* * *

# 11\. Shutdown

Khác Disable.

Disable

↓

Có thể Enable lại.

Shutdown

↓

Giải phóng tài nguyên.

Ví dụ
    
    
    class Plugin:
    
        def shutdown(self):
    
            self.session.close()
    
            self.db.close()

* * *

# 12\. Lifecycle đầy đủ
    
    
               Created
    
                  │
    
                  ▼
    
               Loaded
    
                  │
    
                  ▼
    
            Initialized
    
                  │
    
                  ▼
    
              Enabled
    
                  │
    
            ┌─────┴─────┐
    
            ▼           ▼
    
       Disabled      Shutdown

* * *

# 13\. PluginManager

Manager sẽ điều khiển Lifecycle.
    
    
    class PluginManager:
    
        def enable_all(self):
    
            for record in registry.all():
    
                lifecycle.enable(record)

Hoặc
    
    
    def initialize_all(self):
    
        ...

* * *

# 14\. Vì sao tách Lifecycle?

Sai
    
    
    manager.load()
    
    manager.initialize()
    
    manager.enable()
    
    manager.disable()
    
    manager.shutdown()

toàn bộ viết trong
    
    
    PluginManager

Manager sẽ quá lớn.

* * *

Đúng
    
    
    PluginManager
    
    ↓
    
    LifecycleManager
    
    ↓
    
    Plugin

Single Responsibility Principle.

* * *

# 15\. State Machine

Lifecycle thực chất là

Finite State Machine.

Ví dụ
    
    
    Created
    
    ↓
    
    Loaded
    
    ↓
    
    Initialized
    
    ↓
    
    Enabled

Không thể
    
    
    Created
    
    ↓
    
    Enabled

Nếu chưa
    
    
    Initialize

* * *

# 16\. Kiểm tra State
    
    
    def enable(record):
    
        if record.state != PluginState.INITIALIZED:
    
            raise RuntimeError(
                "Plugin chưa initialize."
            )
    
        record.plugin.enable()
    
        record.state = PluginState.ENABLED

Đây gọi là

State Validation.

* * *

# 17\. Transition

Một số chuyển trạng thái hợp lệ:
    
    
    Created
    
    ↓
    
    Loaded

✔

* * *
    
    
    Loaded
    
    ↓
    
    Initialized

✔

* * *
    
    
    Initialized
    
    ↓
    
    Enabled

✔

* * *
    
    
    Enabled
    
    ↓
    
    Created

❌

Không hợp lệ.

* * *

# 18\. Sơ đồ State Machine
    
    
               Created
                   │
                   ▼
                Loaded
                   │
                   ▼
             Initialized
                   │
                   ▼
               Enabled
              ▲       │
              │       ▼
          Disabled ←──┘
                   │
                   ▼
               Shutdown

Lưu ý:

  * `Disabled → Enabled` là hợp lệ. 
  * Sau `Shutdown` thông thường plugin không quay lại `Enabled`; muốn dùng lại thường phải nạp mới. 



* * *

# 19\. Một Plugin thực tế
    
    
    class TruyenFull(BasePlugin):
    
        def __init__(self):
    
            self.session = None
    
        def initialize(self):
    
            self.session = HttpClient()
    
        def enable(self):
    
            print("Enabled")
    
        def disable(self):
    
            print("Disabled")
    
        def shutdown(self):
    
            self.session.close()

Framework điều khiển hoàn toàn.

* * *

# 20\. Kiến trúc hiện tại
    
    
                   PluginManager
    
                          │
    
            ┌─────────────┼──────────────┐
    
            ▼             ▼              ▼
    
     Discovery       Loader        Lifecycle
    
            │             │              │
    
            └───────┬─────┘              │
    
                    ▼                    ▼
    
                 Registry ---------> Plugin

Từ bây giờ, Registry không chỉ biết Plugin nào tồn tại.

Nó còn biết
    
    
    State

của Plugin.

* * *

# 21\. Cải tiến Lifecycle với Hook

Thay vì chỉ gọi trực tiếp:
    
    
    plugin.initialize()

Framework có thể phát sinh các hook:
    
    
    before_initialize
            │
            ▼
    plugin.initialize()
            │
            ▼
    after_initialize

Điều này sẽ rất hữu ích ở phần Event System (Buổi 11–15), khi các plugin có thể quan sát hoặc can thiệp vào vòng đời của nhau.

* * *

# 22\. Hướng phát triển tiếp theo

Hiện tại:
    
    
    plugin.initialize()

không nhận tham số.

Nhưng plugin thực tế cần:

  * Logger 
  * Config 
  * Database 
  * EventBus 
  * HTTP Client 



Framework sẽ phải truyền chúng vào.

Ví dụ:
    
    
    plugin.initialize(context)

Hoặc:
    
    
    plugin.enable(context)

Đây chính là

> Dependency Injection

* * *

# Best Practices

## 1\. Constructor thật nhẹ

Chỉ khởi tạo:

  * biến, 
  * cấu hình mặc định, 
  * trạng thái ban đầu. 



Không:

  * kết nối Database, 
  * mở Socket, 
  * đọc file lớn, 
  * gọi API. 



* * *

## 2\. Enable và Initialize khác nhau

Initialize

↓

Chuẩn bị tài nguyên.

Enable

↓

Bắt đầu hoạt động.

* * *

## 3\. Shutdown luôn giải phóng tài nguyên

Đừng chỉ viết
    
    
    pass

Hãy đóng:

  * Session 
  * File 
  * Database 
  * Socket 
  * Thread Pool 



Nếu không, framework có thể bị rò rỉ tài nguyên.

* * *

## 4\. Kiểm tra State trước khi chuyển

Mọi thao tác nên xác nhận trạng thái hiện tại để tránh các chuyển trạng thái không hợp lệ.

* * *

# Bài tập

## Bài 1

Tạo
    
    
    PluginState(Enum)

với:

  * CREATED 
  * LOADED 
  * INITIALIZED 
  * ENABLED 
  * DISABLED 
  * SHUTDOWN 



* * *

## Bài 2

Viết
    
    
    LifecycleManager

quản lý:
    
    
    initialize()
    
    enable()
    
    disable()
    
    shutdown()

và cập nhật `PluginState`.

* * *

## Bài 3

Mở rộng `PluginRecord`
    
    
    @dataclass
    class PluginRecord:
    
        plugin: BasePlugin
    
        state: PluginState

và sửa `PluginRegistry` để lưu `PluginRecord` thay vì chỉ lưu đối tượng plugin.

* * *

# Chuẩn bị cho Buổi 8

Hiện tại framework gọi:
    
    
    plugin.initialize()

Nhưng plugin thực tế cần rất nhiều dịch vụ dùng chung:

  * Logger 
  * Config 
  * Database 
  * HTTP Client 
  * Event Bus 
  * Cache 



Nếu mỗi plugin tự tạo:
    
    
    self.db = Database()

thì:

  * khó kiểm thử, 
  * lãng phí tài nguyên, 
  * các plugin không chia sẻ được kết nối. 



Ở **Buổi 8: Dependency Injection & Plugin Context**, chúng ta sẽ xây dựng một `PluginContext` và cơ chế Dependency Injection để framework cung cấp các dịch vụ này cho plugin một cách thống nhất và dễ mở rộng. Đây là bước quan trọng để framework tiến gần hơn đến kiến trúc của các hệ thống plugin chuyên nghiệp.

