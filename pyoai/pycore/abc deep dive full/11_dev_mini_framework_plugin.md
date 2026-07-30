# ABC Deep Dive - Buổi 11

# Xây dựng Mini Plugin Framework với ABC

> Đây là buổi quan trọng nhất của khóa học.

Từ buổi 1 → buổi 10, chúng ta học từng mảnh ghép:

  * ABC 
  * Abstract Method 
  * Abstract Property 
  * Template Method 
  * Generic 
  * MRO 
  * Mixins 
  * ABCMeta 



Hôm nay, chúng ta ghép tất cả lại để xây dựng một **Plugin Framework** gần giống:

  * Scrapy 
  * pytest 
  * SQLAlchemy Dialect 
  * Airflow Operators 
  * MkDocs Plugin 
  * Sphinx Extension 



Đồng thời cũng là kiến trúc rất phù hợp cho **dự án crawler truyện** của bạn.

* * *

# Mục tiêu

Sau buổi này bạn sẽ biết cách thiết kế:
    
    
    Framework
            │
            ▼
     PluginManager
            │
            ▼
     Plugin ABC
            │
            ▼
     TruyenFullPlugin
    
     WattpadPlugin
    
     TangThuVienPlugin
    
     WebNovelPlugin

* * *

# Kiến trúc hoàn chỉnh

Đây là kiến trúc mà chúng ta sẽ xây dựng.
    
    
    project/
    
    plugins/
    │
    ├── base/
    │      base_source.py
    │      manager.py
    │      registry.py
    │      mixins.py
    │
    ├── truyenfull/
    │      source.py
    │
    ├── wattpad/
    │      source.py
    │
    └── webnovel/
           source.py

Đây là kiến trúc mà rất nhiều framework Python đang sử dụng.

* * *

# Bước 1

## Định nghĩa Base Plugin
    
    
    from abc import ABC
    from abc import abstractmethod
    
    
    class BaseSource(ABC):
    
        @property
        @abstractmethod
        def site_name(self):
            ...
    
        @property
        @abstractmethod
        def base_url(self):
            ...
    
        @abstractmethod
        def search(self, keyword):
            ...
    
        @abstractmethod
        def get_detail(self, url):
            ...
    
        @abstractmethod
        def get_chapters(self, detail):
            ...

Đây là contract của plugin.

* * *

# Bước 2

## Thêm Template Method

Framework sẽ điều khiển toàn bộ quy trình.
    
    
    class BaseSource(ABC):
    
        ...
    
        def crawl(self, keyword):
    
            print(f"Crawling {self.site_name}")
    
            url = self.search(keyword)
    
            detail = self.get_detail(url)
    
            chapters = self.get_chapters(detail)
    
            return chapters

Plugin không cần viết:
    
    
    crawl()

Framework sẽ gọi.

* * *

# Bước 3

## Hook

Thêm hook.
    
    
    class BaseSource(ABC):
    
        ...
    
        def before(self):
            pass
    
        def after(self):
            pass
    
        def crawl(self, keyword):
    
            self.before()
    
            try:
    
                ...
    
            finally:
    
                self.after()

Đây là Template Method đầy đủ.

* * *

# Bước 4

## Logging Mixin
    
    
    class LoggingMixin:
    
        def log(self, msg):
    
            print("[LOG]", msg)

* * *

# Retry Mixin
    
    
    class RetryMixin:
    
        def retry(self):
    
            print("Retry...")

* * *

# Proxy Mixin
    
    
    class ProxyMixin:
    
        def get_proxy(self):
    
            return None

* * *

Plugin có thể kế thừa:
    
    
    class TruyenFull(
    
        LoggingMixin,
    
        RetryMixin,
    
        ProxyMixin,
    
        BaseSource
    
    ):
        ...

Đây là Multiple Inheritance đúng cách.

* * *

# Bước 5

## Generic Repository
    
    
    from typing import TypeVar
    from typing import Generic
    
    T = TypeVar("T")
    
    
    class Repository(
        Generic[T],
        ABC,
    ):
    
        @abstractmethod
        def save(
            self,
            obj: T,
        ):
            ...

Sau đó
    
    
    class StoryRepository(
        Repository[Story]
    ):
        ...

* * *

# Bước 6

## Registry

Plugin cần đăng ký.

Ví dụ
    
    
    class PluginRegistry:
    
        plugins = {}
    
        @classmethod
        def register(
            cls,
            plugin,
        ):
    
            cls.plugins[
                plugin.site_name
            ] = plugin

Đăng ký
    
    
    PluginRegistry.register(
        TruyenFull
    )

* * *

Kiểm tra
    
    
    print(
        PluginRegistry.plugins
    )
    
    
    {
        "TruyenFull": TruyenFull
    }

* * *

# Bước 7

## Plugin Manager

Đây là trung tâm framework.
    
    
    class PluginManager:
    
        def __init__(self):
    
            self.plugins = {}
    
        def load(self, plugin):
    
            obj = plugin()
    
            self.plugins[
                obj.site_name
            ] = obj

Sử dụng
    
    
    manager = PluginManager()
    
    manager.load(
        TruyenFull
    )

* * *

Lấy plugin
    
    
    plugin = manager.plugins[
        "TruyenFull"
    ]

* * *

# Bước 8

## Chạy Plugin
    
    
    plugin.crawl(
        "Harry Potter"
    )

Framework hoàn toàn không cần biết:
    
    
    Plugin nào
    
    ↓
    
    Website nào
    
    ↓
    
    HTML thế nào

Chỉ cần:
    
    
    BaseSource

Đây chính là Polymorphism.

* * *

# Bước 9

## Plugin Discovery

Framework chuyên nghiệp không đăng ký thủ công.

Ví dụ
    
    
    plugins/
    
    ↓
    
    importlib
    
    ↓
    
    import module
    
    ↓
    
    register

Pseudo code
    
    
    for module in plugins:
    
        import module

Plugin tự xuất hiện.

Đây là cách:

  * pytest 
  * Sphinx 
  * Scrapy 



hoạt động.

* * *

# Bước 10

## Plugin Metadata

Plugin nên có metadata.
    
    
    class TruyenFull(
    
        BaseSource
    ):
    
        plugin_name = "TruyenFull"
    
        version = "1.0"
    
        author = "Garden"

Framework
    
    
    print(plugin.version)

* * *

# Bước 11

## Plugin Health Check
    
    
    class BaseSource(
    
        ABC
    ):
    
        def check(self):
    
            return True

Framework
    
    
    for plugin:
    
        plugin.check()

Nếu
    
    
    False

Plugin bị disable.

* * *

# Bước 12

## Plugin Configuration
    
    
    class BaseSource:
    
        timeout = 30
    
        retry = 3
    
        headers = {}

Plugin
    
    
    class TruyenFull(
    
        BaseSource
    ):
    
        timeout = 60

Framework tự đọc.

* * *

# Bước 13

## Event Hook

Ví dụ
    
    
    before_search()
    
    after_search()
    
    before_download()
    
    after_download()

Framework
    
    
    crawl()
    
    ↓
    
    before_search()
    
    ↓
    
    search()
    
    ↓
    
    after_search()
    
    ↓
    
    before_download()
    
    ↓
    
    download()
    
    ↓
    
    after_download()

Plugin chỉ override nơi cần.

* * *

# Bước 14

## Plugin Lifecycle

Framework
    
    
    Load
    
    ↓
    
    Init
    
    ↓
    
    Ready
    
    ↓
    
    Run
    
    ↓
    
    Shutdown

Có thể định nghĩa
    
    
    initialize()
    
    shutdown()
    
    reload()

* * *

# Bước 15

## Kiến trúc hoàn chỉnh
    
    
                     PluginManager
                            │
                            │
                    PluginRegistry
                            │
              ┌─────────────┴─────────────┐
              │                           │
         BaseSource (ABC)          Repository[T]
              │
              │
       ┌──────┴─────────┐
       │                │
    LoggingMixin   RetryMixin
       │                │
       └────────┬───────┘
                │
        TruyenFullSource
                │
                ▼
          crawl()
                │
          Template Method
                │
     search()
     get_detail()
     get_chapters()
     save()

* * *

# Áp dụng vào dự án crawler của bạn

Đối với dự án crawler truyện, mình đề xuất cấu trúc sau:
    
    
    story_crawler/
    
    core/
    │
    ├── plugin_manager.py
    ├── registry.py
    ├── loader.py
    ├── events.py
    ├── lifecycle.py
    └── exceptions.py
    
    plugins/
    │
    ├── base/
    │      base_source.py
    │      mixins.py
    │      metadata.py
    │
    ├── truyenfull/
    │      source.py
    │
    ├── tangthuvien/
    │      source.py
    │
    ├── wattpad/
    │      source.py
    │
    └── webnovel/
           source.py
    
    repository/
    │
    ├── base.py
    ├── story_repository.py
    ├── chapter_repository.py
    └── author_repository.py
    
    models/
    │
    ├── story.py
    ├── chapter.py
    └── author.py

Kiến trúc này có nhiều ưu điểm:

  * Dễ thêm website mới. 
  * Mỗi plugin độc lập. 
  * Dễ kiểm thử. 
  * Dễ mở rộng bằng mixin (proxy, retry, cache, rate limit...). 
  * Có thể thay SQLite bằng PostgreSQL hoặc MySQL mà không ảnh hưởng plugin. 



* * *

# Những gì còn thiếu để thành Framework chuyên nghiệp

Hiện tại chúng ta đã có khoảng **80%** kiến thức để xây dựng một plugin framework.

20% còn lại gồm:

  * Dynamic Import (`importlib`) 
  * Auto Discovery 
  * Entry Points 
  * Decorator Registration 
  * Dependency Injection 
  * Event Bus 
  * Service Container 
  * Plugin Sandbox 
  * Async Plugin 



Đây là những chủ đề sẽ được học ở các khóa chuyên sâu về **Plugin Architecture** và **Framework Design**.

* * *

# Tổng kết toàn khóa (Buổi 1 → Buổi 11)

Bạn đã học được:

  * ✅ ABC 
  * ✅ Abstract Method 
  * ✅ Abstract Property 
  * ✅ Concrete Method 
  * ✅ Template Method Pattern 
  * ✅ `register()`
  * ✅ `__subclasshook__()`
  * ✅ `ABCMeta`
  * ✅ `__abstractmethods__`
  * ✅ Generic + TypeVar 
  * ✅ Multiple Inheritance 
  * ✅ MRO 
  * ✅ Mixins 
  * ✅ Plugin Framework 
  * ✅ Repository Pattern 
  * ✅ Registry Pattern 
  * ✅ Plugin Manager 
  * ✅ Hook & Lifecycle 



Đến đây, bạn đã có đủ nền tảng để đọc, hiểu và tự thiết kế nhiều framework Python hiện đại.

* * *

# Bài tập lớn (Capstone Project)

Hãy xây dựng một **Mini Crawler Framework** với các yêu cầu:

  1. **BaseSource (ABC)**
     * Abstract methods: 
       * `search()`
       * `get_detail()`
       * `get_chapters()`
       * `download_chapter()`
     * Template method: 
       * `crawl()`
  2. **Mixins**
     * `LoggingMixin`
     * `RetryMixin`
     * `RateLimitMixin`
     * `ProxyMixin`
  3. **PluginManager**
     * Đăng ký plugin. 
     * Khởi tạo plugin. 
     * Chạy plugin theo tên. 
  4. **Repository**
     * Generic `Repository[T]`. 
     * `StoryRepository`
     * `ChapterRepository`
  5. **Plugin**
     * Cài đặt một plugin mẫu `TruyenFullSource`. 



Đây sẽ là nền móng rất vững chắc để tiếp tục phát triển hệ thống crawler truyện chuyên nghiệp bằng **PySide6 + SQLite3** mà bạn đang theo đuổi.

