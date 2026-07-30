# Plugin Architecture Deep Dive

# Buổi 8: Dependency Injection & Plugin Context – Xây dựng Plugin chuyên nghiệp

> **Mục tiêu**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu Dependency Injection (DI) là gì. 
>   * Phân biệt IoC và DI. 
>   * Biết vì sao Plugin Framework luôn cần Context. 
>   * Xây dựng `PluginContext`. 
>   * Thiết kế Service Container đơn giản. 
>   * Inject Logger, Config, Database, HTTP Client vào Plugin. 
>   * Chuẩn bị cho Hot Reload (Buổi 9). 
> 


* * *

# Roadmap
    
    
    Phần I
    ✓ Buổi 1 : Plugin là gì
    ✓ Buổi 2 : Plugin Contract
    ✓ Buổi 3 : importlib
    ✓ Buổi 4 : inspect
    ✓ Buổi 5 : Discovery
    
    Phần II
    ✓ Buổi 6 : Registry & Manager
    ✓ Buổi 7 : Lifecycle
    ➜ Buổi 8 : Dependency Injection
    □ Buổi 9 : Hot Reload
    □ Buổi 10 : Version Compatibility

* * *

# 1\. Bài toán

Plugin hiện tại
    
    
    class TruyenFull(BasePlugin):
    
        def initialize(self):
    
            self.http = HttpClient()
    
            self.db = Database()
    
            self.logger = Logger()
    
            self.config = Config()

Nhìn có vẻ bình thường.

Nhưng đây là thiết kế **rất tệ**.

* * *

# 2\. Vấn đề

Giả sử có
    
    
    100 Plugin

Mỗi Plugin

↓
    
    
    HttpClient()

thì sẽ có
    
    
    100 HttpClient

Nếu
    
    
    Database()

↓

100 Connection

Nếu
    
    
    Logger()

↓

100 Logger

Đây là lãng phí tài nguyên.

* * *

# 3\. Ai nên tạo HttpClient?

Plugin?

Hay Framework?

Đáp án:

> Framework.

Plugin chỉ nên **sử dụng**.

Không nên **tạo**.

* * *

# 4\. Dependency là gì?

Ví dụ
    
    
    class Downloader:
    
        def __init__(self):
    
            self.http = HttpClient()

Downloader

↓

phụ thuộc

↓

HttpClient

Ta nói
    
    
    Downloader
    
    depends on
    
    HttpClient

* * *

# 5\. Dependency Injection là gì?

Thay vì

Plugin tự tạo
    
    
    self.http = HttpClient()

Framework đưa vào
    
    
    plugin.http = http_client

Hoặc
    
    
    plugin.initialize(http_client)

Đây gọi là

> Dependency Injection

* * *

# 6\. Ví dụ đơn giản

Không dùng DI
    
    
    class Service:
    
        def __init__(self):
    
            self.logger = Logger()

Có DI
    
    
    class Service:
    
        def __init__(
    
            self,
    
            logger
    
        ):
    
            self.logger = logger

Framework
    
    
    logger = Logger()
    
    service = Service(logger)

Service không biết Logger được tạo thế nào.

* * *

# 7\. IoC và DI

Nhiều người nhầm hai khái niệm này.

## Inversion of Control

Framework điều khiển Plugin.
    
    
    Framework
    
    ↓
    
    Plugin

* * *

## Dependency Injection

Framework cung cấp Dependency.
    
    
    Framework
    
    ↓
    
    Logger
    
    ↓
    
    Plugin

DI là một cách hiện thực IoC.

* * *

# 8\. PluginContext

Framework sẽ tạo một Context.
    
    
    class PluginContext:
    
        pass

Trong đó chứa
    
    
    Logger
    
    Config
    
    Database
    
    HttpClient
    
    EventBus
    
    Cache

Plugin chỉ cần Context.

* * *

# 9\. Thiết kế PluginContext
    
    
    from dataclasses import dataclass
    
    
    @dataclass
    class PluginContext:
    
        logger: object
    
        config: object
    
        database: object
    
        http: object

Phiên bản đầu tiên rất đơn giản.

* * *

# 10\. BasePlugin

Thay đổi Interface

Trước
    
    
    initialize()

Sau
    
    
    initialize(context)
    
    
    class BasePlugin(ABC):
    
        @abstractmethod
        def initialize(
    
            self,
    
            context
    
        ):
    
            pass

* * *

# 11\. Plugin
    
    
    class TruyenFull(BasePlugin):
    
        def initialize(
    
            self,
    
            context
    
        ):
    
            self.context = context
    
            context.logger.info("Init")

Plugin không cần biết

Logger ở đâu.

* * *

# 12\. Framework

Framework tạo
    
    
    logger = Logger()
    
    config = Config()
    
    db = Database()
    
    http = HttpClient()

Sau đó
    
    
    context = PluginContext(
    
        logger,
    
        config,
    
        db,
    
        http
    )

Rồi
    
    
    plugin.initialize(context)

* * *

# 13\. Lợi ích

Nếu đổi
    
    
    SQLite

↓
    
    
    PostgreSQL

Plugin không đổi.

Chỉ Framework đổi.

* * *

# 14\. Service Container

Thay vì
    
    
    context.database
    
    context.http
    
    context.logger

Ta có
    
    
    container.resolve(Logger)

Đây gọi là

Service Container.

* * *

# 15\. Viết Container
    
    
    class Container:
    
        def __init__(self):
    
            self._services = {}

* * *

# 16\. Register Service
    
    
    def register(
    
        self,
    
        key,
    
        service
    
    ):
    
        self._services[key] = service

Ví dụ
    
    
    container.register(
    
        "logger",
    
        Logger()
    )

* * *

# 17\. Resolve
    
    
    def resolve(
    
        self,
    
        key
    
    ):
    
        return self._services[key]

Plugin
    
    
    logger = container.resolve(
    
        "logger"
    )

* * *

# 18\. PluginContext dùng Container
    
    
    class PluginContext:
    
        def __init__(
    
            self,
    
            container
    
        ):
    
            self.container = container

Plugin
    
    
    logger = context.container.resolve(
    
        "logger"
    )

Đây là cách linh hoạt hơn.

* * *

# 19\. Dùng Type thay vì String

Thay vì
    
    
    resolve("logger")

Ta dùng
    
    
    resolve(Logger)
    
    
    container.register(
    
        Logger,
    
        Logger()
    )

Resolve
    
    
    logger = container.resolve(
    
        Logger
    )

Ưu điểm:

  * IDE hỗ trợ tốt hơn. 
  * Tránh lỗi gõ sai `"logger"`. 
  * Dễ refactor. 



* * *

# 20\. Constructor Injection

Một cách khác
    
    
    class Plugin:
    
        def __init__(
    
            self,
    
            logger,
    
            database
    
        ):
    
            ...

Framework
    
    
    Plugin(
    
        logger,
    
        database
    )

Đây gọi là

Constructor Injection.

* * *

# 21\. Setter Injection
    
    
    plugin.logger = logger

Đây là

Setter Injection.

* * *

# 22\. Method Injection
    
    
    initialize(
    
        context
    )

Đây là

Method Injection.

* * *

# 23\. Chúng ta dùng gì?

Trong Plugin Framework

Mình khuyến nghị
    
    
    Method Injection

vì

Lifecycle đã có
    
    
    initialize()

Ta chỉ cần
    
    
    initialize(context)

Đơn giản.

Rõ ràng.

* * *

# 24\. Kiến trúc mới
    
    
                  PluginManager
    
                         │
    
                 PluginContext
    
                         │
    
         ┌───────────────┼───────────────┐
    
         ▼               ▼               ▼
    
     Logger          Database        HttpClient
    
                         │
    
                         ▼
    
                     Plugin

* * *

# 25\. Thêm EventBus

Sau này Context sẽ là
    
    
    PluginContext(
    
        logger,
    
        config,
    
        database,
    
        http,
    
        cache,
    
        event_bus,
    
        settings,
    
        scheduler
    )

Plugin chỉ cần
    
    
    context.event_bus

* * *

# 26\. Tích hợp với Lifecycle

Buổi trước
    
    
    plugin.initialize()

Giờ
    
    
    plugin.initialize(
    
        context
    )

LifecycleManager
    
    
    record.plugin.initialize(
    
        self.context
    )

* * *

# 27\. Service Lifetime

Đây là khái niệm rất quan trọng.

Có ba loại vòng đời dịch vụ:

Lifetime| Ý nghĩa| Ví dụ  
---|---|---  
Singleton| Một instance dùng chung| Logger, Config  
Scoped| Một instance cho mỗi phiên làm việc| Transaction  
Transient| Mỗi lần yêu cầu tạo mới| Parser tạm thời  
  
Ví dụ:
    
    
    Logger
    
    Plugin A ─┐
    Plugin B ─┼──► Logger #1
    Plugin C ─┘

Tất cả cùng dùng một Logger.

* * *

# 28\. Nâng cấp Container

Thay vì chỉ lưu object:
    
    
    _services = {
        Logger: Logger()
    }

Sau này chúng ta có thể lưu cả thông tin:
    
    
    _services = {
        Logger: {
            "instance": Logger(),
            "lifetime": "singleton"
        }
    }

Đây là nền tảng để phát triển thành một DI Container hoàn chỉnh.

* * *

# 29\. Kiến trúc hiện tại
    
    
                     PluginManager
                            │
                            ▼
                    LifecycleManager
                            │
                            ▼
                    PluginContext
                            │
            ┌───────────────┼────────────────┐
            ▼               ▼                ▼
         Logger         Database        HttpClient
                            │
                            ▼
                         Plugin

Framework đã bắt đầu giống kiến trúc của:

  * ASP.NET Core 
  * FastAPI (Dependency Injection) 
  * Home Assistant 
  * VS Code Extension Host 



* * *

# 30\. Áp dụng vào Story Framework

Đối với dự án crawler truyện, `PluginContext` có thể chứa:
    
    
    @dataclass
    class PluginContext:
        logger: Logger
        config: Config
        http_client: HttpClient
        database: StoryRepository
        cache: Cache
        event_bus: EventBus

Khi đó plugin chỉ cần:
    
    
    class TruyenFullPlugin(BasePlugin):
    
        def initialize(self, context: PluginContext):
            self.context = context
    
        def search(self, keyword: str):
            response = self.context.http_client.get(
                f"https://truyenfull.vn/tim-kiem/?tukhoa={keyword}"
            )
            self.context.logger.info("Đã tìm kiếm thành công")
            return response.text

Plugin không cần biết:

  * `HttpClient` dùng `requests` hay `httpx`. 
  * `StoryRepository` dùng SQLite hay PostgreSQL. 
  * Logger ghi ra console hay file. 



Toàn bộ những quyết định đó do Framework chịu trách nhiệm.

* * *

# Best Practices

## 1\. Plugin không tự tạo Service

❌
    
    
    self.db = Database()

✔
    
    
    self.db = context.database

* * *

## 2\. Context chỉ chứa dịch vụ dùng chung

Không nên đưa dữ liệu nghiệp vụ như:
    
    
    current_story
    current_chapter

vào `PluginContext`.

Những dữ liệu này nên được truyền trực tiếp vào các phương thức nghiệp vụ.

* * *

## 3\. Interface phụ thuộc abstraction

Nếu có thể, hãy inject:
    
    
    DatabaseProtocol

thay vì:
    
    
    SQLiteDatabase

Điều này giúp thay thế implementation dễ dàng hơn.

* * *

## 4\. Không biến Context thành "God Object"

Đừng nhồi hàng chục thuộc tính không liên quan vào `PluginContext`. Nếu quá lớn, hãy chia thành các nhóm dịch vụ hoặc dùng Service Container để truy xuất theo nhu cầu.

* * *

# Bài tập

## Bài 1

Tạo `PluginContext` chứa:

  * `logger`
  * `config`
  * `http_client`
  * `database`



và sửa `BasePlugin.initialize(context)` để sử dụng Context.

* * *

## Bài 2

Viết `Container` hỗ trợ:
    
    
    register(key, service)
    resolve(key)

Sau đó đăng ký:

  * `Logger`
  * `Config`
  * `HttpClient`



và thử lấy chúng từ plugin.

* * *

## Bài 3

Sửa `LifecycleManager.initialize()` để:

  1. Tạo `PluginContext`. 
  2. Truyền Context vào plugin. 
  3. Cập nhật `PluginState`. 



* * *

# Chuẩn bị cho Buổi 9

Hiện nay, nếu sửa mã nguồn của plugin:
    
    
    plugins/
        truyenfull/
            plugin.py

thì phải:
    
    
    Dừng ứng dụng
        ↓
    Chạy lại
        ↓
    Nạp lại plugin

Điều này không phù hợp với các hệ thống lớn.

Ở **Buổi 9: Hot Reload** , chúng ta sẽ học cách:

  * phát hiện plugin thay đổi, 
  * dùng `importlib.reload()` để nạp lại module, 
  * thay thế instance plugin đang chạy, 
  * giữ nguyên `PluginContext` và các dịch vụ dùng chung, 



giúp framework cập nhật plugin mà **không cần khởi động lại toàn bộ ứng dụng**. Đây là một tính năng rất hữu ích trong quá trình phát triển và mở rộng hệ thống plugin.

