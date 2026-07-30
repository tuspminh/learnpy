# Context Manager Deep Dive – Buổi 12 (Buổi cuối)

# Xây dựng Resource Manager Framework theo phong cách Production

> Đây là buổi tổng kết toàn bộ khóa học.

Mục tiêu không phải học thêm một API mới, mà là **kết hợp toàn bộ kiến thức** thành một kiến trúc quản lý tài nguyên có thể sử dụng trong các dự án thực tế.

Đây cũng là mô hình rất phù hợp với dự án **Story Crawler** mà bạn đang phát triển.

* * *

# Mục tiêu

Sau buổi này, bạn sẽ biết cách thiết kế một hệ thống có:

  * Resource Manager 
  * Context Manager 
  * ExitStack 
  * AsyncExitStack 
  * Plugin 
  * Transaction 
  * Logging 
  * HTTP Session 
  * Database 
  * Cache 
  * Metrics 
  * Resource Lifecycle 



* * *

# 1\. Kiến trúc tổng thể

Một crawler production thường có rất nhiều tài nguyên:
    
    
    Application
    │
    ├── Config
    ├── Logger
    ├── Database
    ├── HTTP Session
    ├── Cache
    ├── Plugin Manager
    ├── Metrics
    ├── Event Bus
    └── Task Queue

Nếu quản lý bằng:
    
    
    db.connect()
    
    logger.start()
    
    http.open()
    
    cache.open()

thì:

  * dễ quên close 
  * khó rollback 
  * khó test 
  * dễ memory leak 



* * *

# 2\. Ý tưởng

Thay vì
    
    
    db.connect()
    ...
    db.close()

chúng ta muốn
    
    
    with ResourceManager() as app:
        ...

ResourceManager sẽ quản lý mọi thứ.

* * *

# 3\. Thiết kế
    
    
    ResourceManager
    │
    ├── Database
    ├── HttpSession
    ├── Cache
    ├── Logger
    ├── Metrics
    └── Plugins

* * *

# 4\. Database
    
    
    class Database:
    
        def __enter__(self):
    
            print("Connect DB")
    
            return self
    
        def __exit__(self, *args):
    
            print("Disconnect DB")

* * *

# 5\. Logger
    
    
    class Logger:
    
        def __enter__(self):
    
            print("Logger Start")
    
            return self
    
        def __exit__(self, *args):
    
            print("Logger Stop")

* * *

# 6\. HttpSession
    
    
    class HttpSession:
    
        def __enter__(self):
    
            print("HTTP Open")
    
            return self
    
        def __exit__(self, *args):
    
            print("HTTP Close")

* * *

# 7\. Cache
    
    
    class Cache:
    
        def __enter__(self):
    
            print("Cache Open")
    
            return self
    
        def __exit__(self, *args):
    
            print("Cache Close")

* * *

# 8\. ExitStack

Bây giờ
    
    
    from contextlib import ExitStack

* * *

# 9\. ResourceManager
    
    
    from contextlib import ExitStack
    
    
    class ResourceManager:
    
        def __enter__(self):
    
            self.stack = ExitStack()
    
            self.stack.__enter__()
    
            self.db = self.stack.enter_context(Database())
    
            self.http = self.stack.enter_context(HttpSession())
    
            self.logger = self.stack.enter_context(Logger())
    
            self.cache = self.stack.enter_context(Cache())
    
            return self
    
        def __exit__(self, exc_type, exc, tb):
    
            return self.stack.__exit__(
                exc_type,
                exc,
                tb,
            )

Sử dụng
    
    
    with ResourceManager() as app:
    
        print("Crawler Running")

Output
    
    
    Connect DB
    
    HTTP Open
    
    Logger Start
    
    Cache Open
    
    Crawler Running
    
    Cache Close
    
    Logger Stop
    
    HTTP Close
    
    Disconnect DB

* * *

# 10\. Thêm Plugin
    
    
    PluginA
    
    PluginB
    
    PluginC

Không nên
    
    
    with PluginA():
    
        with PluginB():
    
            ...

* * *

Đúng
    
    
    plugins = load_plugins()
    
    for plugin in plugins:
    
        stack.enter_context(plugin)

Đây là sức mạnh của ExitStack.

* * *

# 11\. Resource Registry

Một bước tiến hơn:
    
    
    class ResourceManager:
    
        def __init__(self):
    
            self.resources = {}

Đăng ký
    
    
    self.resources["db"] = db
    
    self.resources["http"] = http

Sử dụng
    
    
    app.resources["db"]

Hoặc đẹp hơn
    
    
    app.db

* * *

# 12\. Transaction
    
    
    class Transaction:
    
        def __enter__(self):
    
            print("BEGIN")
    
            return self
    
        def __exit__(self,
                     exc_type,
                     exc,
                     tb):
    
            if exc_type:
    
                print("ROLLBACK")
    
            else:
    
                print("COMMIT")

Sử dụng
    
    
    with ResourceManager() as app:
    
        with Transaction():
    
            ...

* * *

# 13\. Logging

Logger cũng nên là Context Manager.
    
    
    with Logger():
    
        process()

Nếu lỗi

↓

logger vẫn flush.

* * *

# 14\. Timer
    
    
    with Timer():
    
        crawl()

Không cần nhớ
    
    
    start
    
    ...
    
    stop

* * *

# 15\. Metrics

Ví dụ
    
    
    class Metrics:
    
        def __enter__(self):
    
            self.start()
    
            return self
    
        def __exit__(...):
    
            self.stop()

Có thể:

  * Prometheus 
  * Grafana 
  * OpenTelemetry 



* * *

# 16\. Async Version
    
    
    from contextlib import AsyncExitStack
    
    
    class AsyncResourceManager:
    
        async def __aenter__(self):
    
            self.stack = AsyncExitStack()
    
            await self.stack.__aenter__()
    
            ...
    
            return self
    
        async def __aexit__(...):
    
            return await self.stack.__aexit__(...)

Đây là phiên bản production của asyncio.

* * *

# 17\. Story Crawler

Bạn đang xây dựng
    
    
    StoryCrawler
    │
    ├── SQLite
    ├── HTTP
    ├── Repository
    ├── Plugin
    ├── Parser
    ├── Logger
    ├── Cache
    ├── Config
    └── Metrics

Có thể
    
    
    with ResourceManager() as app:
    
        parser = Parser()
    
        parser.parse(...)

Parser không cần biết

Database mở hay chưa.

Đó là Dependency Injection đơn giản.

* * *

# 18\. Lifecycle
    
    
    Application
    
    ↓
    
    Load Config
    
    ↓
    
    Logger
    
    ↓
    
    Database
    
    ↓
    
    Cache
    
    ↓
    
    HTTP
    
    ↓
    
    Plugins
    
    ↓
    
    Crawler
    
    ↓
    
    Plugins Cleanup
    
    ↓
    
    HTTP Close
    
    ↓
    
    Cache Close
    
    ↓
    
    Database Close
    
    ↓
    
    Logger Close

* * *

# 19\. Production Folder

Đây là cấu trúc mình khuyến nghị cho dự án **Story Crawler** :
    
    
    core/
    │
    ├── resources/
    │   ├── resource.py          # Resource base class
    │   ├── manager.py           # ResourceManager
    │   ├── registry.py          # Resource Registry
    │   ├── lifecycle.py         # Resource Lifecycle
    │   ├── async_manager.py
    │   └── exceptions.py
    │
    ├── context/
    │   ├── transaction.py
    │   ├── timer.py
    │   ├── logger.py
    │   ├── cache.py
    │   └── metrics.py
    │
    ├── plugins/
    │   ├── manager.py
    │   └── loader.py
    │
    ├── database/
    │   ├── connection.py
    │   ├── session.py
    │   └── repository.py
    │
    └── network/
        ├── session.py
        └── downloader.py

* * *

# 20\. Mô hình cuối cùng
    
    
    Application
            │
            ▼
     ResourceManager
            │
     ┌──────┼───────────────┐
     ▼      ▼       ▼       ▼
    DB     HTTP   Logger   Cache
     │       │       │       │
     └───────┼───────┴───────┘
             ▼
          ExitStack
             ▼
         Cleanup (LIFO)

* * *

# Best Practices

## 1\. Mọi tài nguyên đều nên là Context Manager

Ví dụ:

  * Database 
  * Lock 
  * Socket 
  * HTTP Session 
  * Cache 
  * Temporary File 



* * *

## 2\. Không gọi `close()` thủ công

Sai:
    
    
    db = Database()
    
    db.connect()
    
    ...
    
    db.close()

Đúng:
    
    
    with Database():

* * *

## 3\. Dùng ExitStack

Nếu số lượng tài nguyên không cố định.

* * *

## 4\. Async dùng AsyncExitStack

Không trộn lẫn:
    
    
    ExitStack

với
    
    
    async with

* * *

## 5\. Resource chỉ có một chủ sở hữu

Ví dụ
    
    
    Application
    
    ↓
    
    ResourceManager
    
    ↓
    
    Database

Không để nhiều thành phần cùng chịu trách nhiệm đóng một kết nối.

* * *

# Một phiên bản ResourceManager hoàn chỉnh hơn
    
    
    from contextlib import ExitStack
    
    
    class ResourceManager:
        def __init__(self):
            self.stack = ExitStack()
            self.resources = {}
    
        def register(self, name: str, resource):
            value = self.stack.enter_context(resource)
            self.resources[name] = value
            return value
    
        def __enter__(self):
            self.stack.__enter__()
    
            self.db = self.register("db", Database())
            self.http = self.register("http", HttpSession())
            self.logger = self.register("logger", Logger())
            self.cache = self.register("cache", Cache())
    
            return self
    
        def __exit__(self, exc_type, exc, tb):
            return self.stack.__exit__(exc_type, exc, tb)

Điểm mạnh:

  * Dễ thêm tài nguyên mới. 
  * Có `registry` để tra cứu. 
  * Toàn bộ cleanup được giao cho `ExitStack`. 



* * *

# Bài tập lớn (Capstone)

## Xây dựng ResourceManager cho Story Crawler

Thiết kế:
    
    
    StoryResourceManager
    │
    ├── SQLiteConnection
    ├── HttpSession
    ├── Config
    ├── Logger
    ├── Cache
    ├── Metrics
    ├── PluginManager
    └── Transaction

Yêu cầu:

  * Sử dụng `ExitStack`. 
  * Hỗ trợ bật/tắt từng tài nguyên bằng cấu hình. 
  * Có `register(name, resource)` để mở rộng. 
  * Tự động cleanup theo LIFO. 
  * Dễ chuyển sang `AsyncExitStack` trong tương lai. 



* * *

# Tổng kết toàn bộ khóa học Context Manager

Trong 12 buổi, chúng ta đã đi qua gần như toàn bộ hệ sinh thái Context Manager của Python:

Buổi| Chủ đề  
---|---  
1| Khái niệm và `with`  
2| `__enter__` và `__exit__`  
3| Exception Handling  
4| Thiết kế Class-based Context Manager  
5| Quản lý tài nguyên và Lifecycle  
6| Best Practices & Design Patterns  
7| `contextlib` và `@contextmanager`  
8| Nested Context Manager  
9| `ExitStack`  
10| Async Context Manager & `AsyncExitStack`  
11| Context Manager trong thư viện chuẩn  
12| Production Resource Manager  
  
* * *

# Bạn đã đạt đến mức nào?

Sau khóa học này, bạn không chỉ biết **dùng** Context Manager mà còn có thể:

  * Thiết kế API theo phong cách Pythonic. 
  * Xây dựng thư viện quản lý tài nguyên. 
  * Áp dụng `ExitStack` và `AsyncExitStack` trong các hệ thống lớn. 
  * Thiết kế kiến trúc quản lý tài nguyên cho các dự án như **Story Crawler** , hệ thống crawler, web service, hoặc ứng dụng desktop với **PySide6** và **SQLite**. 



Đây là mức kiến thức tương đương với những gì nhiều lập trình viên Python sử dụng khi phát triển các thư viện và ứng dụng production.

