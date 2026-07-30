# Plugin Architecture Deep Dive

# Buổi 9: Hot Reload - Nạp lại Plugin khi đang chạy

> **Mục tiêu**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu Hot Reload và Live Reload khác nhau thế nào. 
>   * Thành thạo `importlib.reload()`. 
>   * Hiểu các vấn đề của Python Module Cache. 
>   * Reload Plugin mà không cần restart ứng dụng. 
>   * Thay thế Plugin Instance an toàn. 
>   * Chuẩn bị cho Version Compatibility (Buổi 10). 
> 


* * *

# Roadmap
    
    
    Phần I - Foundation
    
    ✓ Buổi 1 : Plugin là gì
    ✓ Buổi 2 : Plugin Contract
    ✓ Buổi 3 : importlib
    ✓ Buổi 4 : inspect
    ✓ Buổi 5 : Discovery
    
    Phần II - Runtime
    
    ✓ Buổi 6 : Registry & Manager
    ✓ Buổi 7 : Lifecycle
    ✓ Buổi 8 : Dependency Injection
    ➜ Buổi 9 : Hot Reload
    □ Buổi 10 : Version Compatibility
    □ Buổi 11 : Event System
    □ Buổi 12 : Hook System

Đây là một trong những chủ đề khó nhất của Plugin Architecture.

* * *

# 1\. Hot Reload là gì?

Giả sử Framework đang chạy.
    
    
    Application
    
    ↓
    
    Plugin A
    
    ↓
    
    Plugin B
    
    ↓
    
    Plugin C

Bạn sửa
    
    
    plugins/truyenfull/plugin.py

Thông thường phải
    
    
    Stop App
    
    ↓
    
    Run App
    
    ↓
    
    Load Plugin

Hot Reload

↓
    
    
    Save File
    
    ↓
    
    Reload Plugin
    
    ↓
    
    Done

Không restart Application.

* * *

# 2\. Hot Reload ≠ Live Reload

Đây là hai khái niệm rất hay bị nhầm.

## Live Reload
    
    
    Save File
    
    ↓
    
    Restart Program
    
    ↓
    
    Reload Everything

Ví dụ

  * Flask Debug 
  * Django Development Server 



* * *

## Hot Reload
    
    
    Save File
    
    ↓
    
    Reload đúng Plugin
    
    ↓
    
    Application vẫn chạy

Ví dụ

  * VSCode Extension 
  * IntelliJ Plugin 
  * Unreal Engine 
  * Unity 



* * *

# 3\. Python Import Cache

Python chỉ import một module **một lần**.

Ví dụ
    
    
    import plugins.truyenfull

Sau đó
    
    
    import plugins.truyenfull

Python

↓

Không import nữa.

Vì sao?

* * *

# 4\. `sys.modules`

Python có một cache.
    
    
    import sys
    
    print(sys.modules)

Bên trong
    
    
    {
        "os": module,
    
        "json": module,
    
        "plugins.truyenfull": module
    }

Lần import sau

↓

Python lấy luôn trong cache.

* * *

# 5\. Minh họa
    
    
    import importlib
    
    m1 = importlib.import_module(
        "plugins.truyenfull"
    )
    
    m2 = importlib.import_module(
        "plugins.truyenfull"
    )
    
    print(m1 is m2)

↓
    
    
    True

Chỉ có một object module.

* * *

# 6\. Reload

Python cung cấp
    
    
    importlib.reload(module)

Ví dụ
    
    
    module = importlib.import_module(
        "plugins.truyenfull"
    )
    
    importlib.reload(module)

↓

Python đọc lại file.

* * *

# 7\. Nhưng có một hiểu lầm lớn

Nhiều người nghĩ
    
    
    reload(module)

↓

Mọi object đều cập nhật.

Sai.

* * *

Ví dụ
    
    
    class Plugin:
    
        version = 1

Tạo object
    
    
    plugin = Plugin()

Sau đó sửa
    
    
    version = 2

Reload
    
    
    reload(module)

Object cũ

↓

Vẫn
    
    
    version = 1

* * *

# 8\. Vì sao?

Object đã tồn tại.
    
    
    Plugin Class
    
    ↓
    
    plugin object

Reload

↓

Tạo
    
    
    Plugin Class mới

Nhưng

Object cũ

↓

Không đổi.

* * *

# 9\. Muốn dùng code mới?

Phải tạo object mới.
    
    
    plugin = Plugin()

Không phải
    
    
    reload(module)

Đây là điều cực kỳ quan trọng.

* * *

# 10\. Quy trình Hot Reload
    
    
    Plugin đang chạy
    
    ↓
    
    Disable
    
    ↓
    
    Shutdown
    
    ↓
    
    Reload Module
    
    ↓
    
    Find Plugin Class
    
    ↓
    
    Instantiate
    
    ↓
    
    Inject Context
    
    ↓
    
    Initialize
    
    ↓
    
    Enable
    
    ↓
    
    Replace Registry

Đây là quy trình chuẩn.

* * *

# 11\. PluginManager

Ta thêm
    
    
    class PluginManager:
    
        def reload(self, name):
    
            ...

* * *

# 12\. Bước 1

Lấy PluginRecord
    
    
    record = registry.get(name)

* * *

# 13\. Bước 2

Shutdown
    
    
    lifecycle.disable(record)
    
    lifecycle.shutdown(record)

Đảm bảo:

  * đóng file, 
  * đóng DB, 
  * dừng thread, 
  * giải phóng tài nguyên. 



* * *

# 14\. Bước 3

Reload Module
    
    
    module = inspect.getmodule(
        record.plugin.__class__
    )
    
    importlib.reload(module)

Đây là lý do buổi 4 chúng ta học:
    
    
    inspect.getmodule()

* * *

# 15\. Bước 4

Tìm Class mới
    
    
    classes = inspect.getmembers(
        module,
        inspect.isclass
    )

↓
    
    
    NewPlugin

* * *

# 16\. Bước 5

Khởi tạo Plugin mới
    
    
    plugin = NewPlugin()

Đừng dùng object cũ.

* * *

# 17\. Bước 6

Inject Context
    
    
    plugin.initialize(
        context
    )

* * *

# 18\. Bước 7

Enable
    
    
    plugin.enable()

* * *

# 19\. Bước 8

Cập nhật Registry
    
    
    registry.register(plugin)

Plugin cũ

↓

Biến mất.

Plugin mới

↓

Hoạt động.

* * *

# 20\. Flow đầy đủ
    
    
    Plugin
    
    ↓
    
    Disable
    
    ↓
    
    Shutdown
    
    ↓
    
    Reload Module
    
    ↓
    
    New Class
    
    ↓
    
    New Object
    
    ↓
    
    Inject Context
    
    ↓
    
    Enable
    
    ↓
    
    Registry Update

* * *

# 21\. Vấn đề 1 - Background Thread

Giả sử Plugin
    
    
    class Plugin:
    
        def enable(self):
    
            threading.Thread(
                target=self.worker
            ).start()

Nếu reload

↓

Thread cũ

↓

Vẫn chạy.

Kết quả
    
    
    2 Worker

Giải pháp:
    
    
    disable()
    
    ↓
    
    shutdown()
    
    ↓
    
    join thread
    
    ↓
    
    reload

Không bao giờ reload khi thread cũ còn sống.

* * *

# 22\. Vấn đề 2 - Event Listener

Plugin
    
    
    event_bus.subscribe(
        "download",
        self.download
    )

Reload

↓

Plugin mới

↓

Subscribe tiếp.

Plugin cũ

↓

Vẫn subscribe.

Kết quả
    
    
    download
    
    ↓
    
    2 callback

Giải pháp:
    
    
    disable()
    
    ↓
    
    unsubscribe()

* * *

# 23\. Vấn đề 3 - Cache

Plugin
    
    
    self.cache = {}

Reload

↓

Cache mất.

Nếu muốn giữ cache:
    
    
    Cache
    
    ↓
    
    PluginContext
    
    ↓
    
    Shared

Không đặt cache trong Plugin nếu cần tồn tại qua nhiều lần reload.

* * *

# 24\. Vấn đề 4 - Singleton

Sai
    
    
    plugin = Plugin()
    
    GLOBAL_PLUGIN = plugin

Reload

↓

GLOBAL_PLUGIN

↓

Object cũ.

Không được dùng biến toàn cục để lưu plugin đang hoạt động.

* * *

# 25\. Kiến trúc mới
    
    
               PluginManager
    
                     │
    
              reload(name)
    
                     │
    
         ┌───────────┼────────────┐
    
         ▼           ▼            ▼
    
     Lifecycle   importlib    Registry
    
         │           │            │
    
         ▼           ▼            ▼
    
     Shutdown   New Module   Replace Plugin

* * *

# 26\. Một ví dụ hoàn chỉnh
    
    
    import importlib
    import inspect
    
    
    class PluginManager:
    
        def reload(self, name):
    
            record = self.registry.get(name)
    
            self.lifecycle.disable(record)
    
            self.lifecycle.shutdown(record)
    
            module = inspect.getmodule(
                record.plugin.__class__
            )
    
            importlib.reload(module)
    
            plugins = self.loader.load(
                module.__name__
            )
    
            plugin = plugins[0]
    
            plugin.initialize(
                self.context
            )
    
            plugin.enable()
    
            self.registry.register(plugin)

Trong thực tế, cần bổ sung xử lý lỗi để nếu reload thất bại thì plugin cũ vẫn tiếp tục hoạt động.

* * *

# 27\. Rollback khi Reload thất bại

Đây là điểm mà nhiều framework chuyên nghiệp rất chú trọng.

Quy trình an toàn:
    
    
    Plugin cũ đang chạy
            │
            ▼
    Tạo Plugin mới
            │
            ▼
    Initialize thành công?
          /   \
        Có     Không
        │        │
        ▼        ▼
    Enable   Giữ Plugin cũ
        │
        ▼
    Thay Registry

**Không nên** xóa plugin cũ khỏi Registry trước khi plugin mới sẵn sàng.

* * *

# 28\. Hot Reload và Dependency Injection

Nhờ `PluginContext`, plugin mới không cần tạo lại:

  * Logger 
  * Database 
  * HttpClient 
  * Config 
  * EventBus 



Framework chỉ việc:
    
    
    plugin.initialize(self.context)

Mọi dịch vụ được tái sử dụng.

* * *

# 29\. Áp dụng vào Story Framework

Giả sử bạn đang phát triển plugin:
    
    
    plugins/
    └── truyenfull/
        ├── plugin.py
        ├── parser.py
        └── config.py

Bạn sửa thuật toán parse trong:
    
    
    parser.py

Framework có thể:
    
    
    Phát hiện file thay đổi
            │
            ▼
    Reload module plugin
            │
            ▼
    Khởi tạo plugin mới
            │
            ▼
    Crawler tiếp tục chạy

Không cần dừng Dashboard hay đóng toàn bộ ứng dụng.

* * *

# 30\. Hạn chế của `importlib.reload()`

`reload()` không phải "viên đạn bạc".

Một số trường hợp vẫn khó xử lý:

  * Các module import lẫn nhau (circular imports). 
  * Object đã được truyền sang nơi khác vẫn giữ class cũ. 
  * Decorator hoặc metaclass có trạng thái toàn cục. 
  * Extension viết bằng C/C++ thường không hỗ trợ reload đúng cách. 
  * Các singleton toàn cục và thread nền cần được quản lý riêng. 



Đó là lý do nhiều framework plugin chuyên nghiệp xem Hot Reload là một tính năng phức tạp và luôn kết hợp với Lifecycle, Registry và Dependency Injection.

* * *

# Best Practices

## 1\. Luôn tạo Plugin Instance mới

❌ Sai
    
    
    reload(module)
    
    plugin.enable()

✔ Đúng
    
    
    reload(module)
    
    plugin = NewPlugin()

* * *

## 2\. Shutdown trước khi Reload

Đừng reload khi plugin còn:

  * Thread đang chạy. 
  * Timer. 
  * Socket. 
  * File mở. 
  * Event Listener. 



* * *

## 3\. Giữ dịch vụ dùng chung trong Context

Logger, Database, HttpClient... nên nằm trong `PluginContext`, không nằm trong plugin.

* * *

## 4\. Hỗ trợ Rollback

Nếu plugin mới khởi tạo thất bại, hãy giữ plugin cũ tiếp tục hoạt động thay vì để hệ thống mất chức năng.

* * *

# Bài tập

## Bài 1

Viết phương thức:
    
    
    reload(plugin_name)

thực hiện:

  1. Disable plugin. 
  2. Shutdown plugin. 
  3. Reload module. 
  4. Tạo plugin mới. 
  5. Initialize. 
  6. Enable. 
  7. Cập nhật Registry. 



* * *

## Bài 2

Mở rộng `PluginManager.reload()` để nếu `initialize()` hoặc `enable()` ném ngoại lệ thì:

  * ghi log lỗi, 
  * giữ nguyên plugin cũ, 
  * không làm gián đoạn ứng dụng. 



* * *

## Bài 3

Thiết kế `PluginContext` sao cho cache được chia sẻ giữa các lần Hot Reload, trong khi trạng thái nội bộ của plugin vẫn được tạo mới.

* * *

# Chuẩn bị cho Buổi 10

Đến đây framework đã có:

  * ✅ Discovery 
  * ✅ Loader 
  * ✅ Registry 
  * ✅ Lifecycle 
  * ✅ Dependency Injection 
  * ✅ Hot Reload 



Nhưng còn một bài toán lớn trong các hệ thống plugin:

> **Nếu plugin yêu cầu Framework phiên bản 2.0, nhưng ứng dụng đang chạy Framework 1.5 thì sao?**

Hoặc:

> **Hai plugin phụ thuộc vào các phiên bản khác nhau của cùng một API thì xử lý như thế nào?**

Ở **Buổi 10: Version Compatibility & Dependency Resolution**, chúng ta sẽ xây dựng hệ thống metadata, kiểm tra phiên bản, ràng buộc phụ thuộc và quy trình từ chối nạp plugin không tương thích — một thành phần quan trọng trong các hệ sinh thái plugin chuyên nghiệp như VS Code, pytest và Home Assistant.

