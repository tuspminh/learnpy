# Python OOP Master — Buổi 32

# Singleton Pattern

Trong phần trước chúng ta đã hoàn thành **SOLID**. Bây giờ bước sang **Design Pattern**, bắt đầu bằng một pattern rất nổi tiếng nhưng cũng rất dễ bị lạm dụng: **Singleton**.

---

# 1. Mục tiêu buổi học

Sau buổi này bạn cần hiểu:

* Singleton là gì?
* Tại sao cần Singleton?
* `__new__()` hoạt động như thế nào?
* Singleton khác `__init__()` như thế nào?
* Singleton trong Python
* Module Singleton — cách Pythonic
* Singleton thread-safe
* Singleton bằng Metaclass
* Singleton vs Dependency Injection
* Vì sao Singleton thường bị lạm dụng?
* Khi nào nên và không nên dùng Singleton
* Áp dụng vào `DatabaseManager` của project crawler

---

# 2. Singleton là gì?

**Singleton Pattern** đảm bảo rằng một class chỉ có **một instance duy nhất** trong một phạm vi xác định.

Ví dụ:

```text
Application
     │
     ├── Service A ──┐
     ├── Service B ──┼──> Singleton
     └── Service C ──┘
```

Tất cả cùng truy cập một object.

Ví dụ:

```python
a = Singleton()
b = Singleton()

print(a is b)
```

Kết quả:

```text
True
```

Tức là:

```text
a
│
└──────┐
       ↓
   Singleton Object
       ↑
       │
b ─────┘
```

---

# 3. Vì sao cần Singleton?

Giả sử application có một `Config`.

Ta không muốn:

```python
config1 = Config()
config2 = Config()
config3 = Config()
```

mỗi object lại chứa một bản config khác nhau.

Ta muốn:

```text
Config
  ↑
  │
  ├── Service A
  ├── Service B
  └── Service C
```

Tất cả sử dụng cùng một instance.

Một số trường hợp có thể phù hợp:

* process-wide configuration
* registry
* một số resource manager
* một số cache/registry có lifecycle toàn ứng dụng

Nhưng **không phải cứ dùng chung object là phải dùng Singleton**.

Đây là điểm cực kỳ quan trọng.

---

# 4. Singleton đơn giản nhất

Python cho phép can thiệp quá trình tạo object thông qua:

```python
__new__()
```

Ví dụ:

```python
class Singleton:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance
```

Sử dụng:

```python
a = Singleton()
b = Singleton()

print(a is b)
```

Kết quả:

```text
True
```

---

# 5. `__new__()` và `__init__()`

Đây là phần rất quan trọng.

Khi viết:

```python
obj = MyClass()
```

Python thực hiện đại khái:

```text
__new__()
   ↓
tạo instance
   ↓
__init__()
   ↓
khởi tạo instance
```

Ví dụ:

```python
class User:

    def __new__(cls):
        print("__new__")
        return super().__new__(cls)

    def __init__(self):
        print("__init__")
```

Chạy:

```python
user = User()
```

Kết quả:

```text
__new__
__init__
```

`__new__()` tạo object.

`__init__()` khởi tạo object.

---

# 6. Vấn đề với Singleton

Xét:

```python
class Singleton:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        print("Initialize")
```

Chạy:

```python
a = Singleton()
b = Singleton()
c = Singleton()
```

Có thể thấy:

```text
Initialize
Initialize
Initialize
```

Trong khi:

```python
a is b is c
```

là:

```text
True
```

Điều này cho thấy:

> Có thể chỉ có một instance nhưng `__init__()` vẫn được gọi nhiều lần.

---

# 7. Ngăn `__init__()` chạy nhiều lần

Ta có thể sử dụng một flag.

```python
class Singleton:

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):

        if self._initialized:
            return

        self._initialized = True

        print("Initialize only once")
```

Test:

```python
a = Singleton()
b = Singleton()
c = Singleton()
```

Output:

```text
Initialize only once
```

Và:

```python
print(a is b)
print(b is c)
```

```text
True
True
```

---

# 8. Nhưng Singleton này có vấn đề thiết kế

Ta đang có:

```python
class Singleton:

    _instance = None
```

Class tự quản lý lifecycle của chính nó.

Điều này khiến dependency trở nên **ẩn**.

Ví dụ:

```python
class OrderService:

    def process(self):
        db = DatabaseManager()
```

Nhìn vào constructor:

```python
OrderService()
```

ta không biết `OrderService` phụ thuộc vào:

```text
DatabaseManager
```

Dependency bị giấu bên trong class.

Đây chính là vấn đề mà **Dependency Injection** giải quyết.

---

# 9. Singleton vs Dependency Injection

### Singleton

```python
class Service:

    def run(self):
        db = DatabaseManager()
```

Dependency:

```text
Service
   │
   └── tự tạo DatabaseManager
```

### Dependency Injection

```python
class Service:

    def __init__(self, db):
        self.db = db
```

Wiring:

```python
db = DatabaseManager()
service = Service(db)
```

Dependency:

```text
Composition Root
       │
       ├── DatabaseManager
       │
       ↓
    Service
```

DI làm dependency **explicit**.

---

# 10. Pythonic Singleton: Module Singleton

Trong Python, có một cách rất tự nhiên để tạo singleton.

Đó là:

> **Module chính là một singleton theo cơ chế import của Python.**

Ví dụ:

```text
app/
├── config.py
├── service.py
└── main.py
```

### `config.py`

```python
class Config:

    def __init__(self):
        self.debug = True
        self.database_url = "sqlite:///app.db"


config = Config()
```

### `service.py`

```python
from config import config


def run():
    print(config.debug)
```

### `main.py`

```python
from config import config

print(config.debug)
```

Module `config` được Python cache trong:

```python
sys.modules
```

Vì vậy các nơi import module đó sẽ dùng cùng module object.

Đây thường là cách đơn giản hơn rất nhiều so với việc viết một Singleton class phức tạp.

---

# 11. Module Singleton

Ta có thể viết:

```python
# config.py

class AppConfig:

    def __init__(self):
        self.debug = True
        self.database = "app.db"


config = AppConfig()
```

Sau đó:

```python
from config import config
```

Ở nhiều module khác nhau:

```python
from config import config
```

Ta đang sử dụng cùng object:

```text
config.py
    │
    └── config
          ↑
          │
     ┌────┼────┐
     │    │    │
   A.py B.py C.py
```

Đây là một trong những cách tôi thường ưu tiên trước khi nghĩ tới Singleton Pattern bằng class.

---

# 12. Singleton bằng Metaclass

Python còn có thể implement Singleton bằng metaclass.

```python
class SingletonMeta(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):

        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(
                *args,
                **kwargs
            )

        return cls._instances[cls]
```

Sau đó:

```python
class DatabaseManager(metaclass=SingletonMeta):

    def __init__(self):
        print("Initialize database")
```

Test:

```python
a = DatabaseManager()
b = DatabaseManager()

print(a is b)
```

Kết quả:

```text
Initialize database
True
```

`__call__()` của metaclass kiểm soát quá trình:

```python
DatabaseManager()
```

---

# 13. Cách này hoạt động thế nào?

Khi bạn viết:

```python
DatabaseManager()
```

Python thực chất gọi:

```text
DatabaseManager.__class__.__call__()
```

và vì:

```python
DatabaseManager.__class__
```

là:

```python
SingletonMeta
```

nên:

```python
SingletonMeta.__call__()
```

được thực hiện.

Luồng:

```text
DatabaseManager()
       ↓
SingletonMeta.__call__()
       ↓
instance đã tồn tại?
     /     \
   Yes      No
    ↓        ↓
 return    tạo instance
             ↓
          lưu cache
             ↓
           return
```

---

# 14. Thread Safety

Đây là vấn đề quan trọng khi dùng:

```python
threading
ThreadPoolExecutor
```

Giả sử:

```python
if cls._instance is None:
    cls._instance = super().__new__(cls)
```

Hai thread có thể cùng chạy:

```text
Thread A                Thread B

check instance          check instance
      ↓                       ↓
    None                    None
      ↓                       ↓
 create object            create object
```

Kết quả có thể không còn đúng ý tưởng Singleton.

---

# 15. Thread-safe Singleton

Có thể sử dụng:

```python
threading.Lock
```

Ví dụ:

```python
from threading import Lock


class Singleton:

    _instance = None
    _lock = Lock()

    def __new__(cls):

        if cls._instance is None:

            with cls._lock:

                if cls._instance is None:
                    cls._instance = super().__new__(cls)

        return cls._instance
```

Test:

```python
a = Singleton()
b = Singleton()

print(a is b)
```

```text
True
```

Ý tưởng:

```text
        instance?
           │
      ┌────┴────┐
      │         │
     Yes        No
      │         │
    return     Lock
                │
             check lại
                │
              create
```

Điểm quan trọng là **check lại bên trong lock**.

---

# 16. GIL có giải quyết vấn đề này không?

Không nên thiết kế concurrency dựa trên giả định:

> “Python có GIL nên Singleton tự động thread-safe.”

Đặc biệt khi code cần hoạt động chính xác trong môi trường concurrent và có nhiều bước kiểm tra/khởi tạo.

Hãy thể hiện synchronization một cách rõ ràng nếu invariant của bạn yêu cầu nó.

---

# 17. Singleton trong ứng dụng Crawler

Đây là phần quan trọng nhất đối với project của bạn.

Bạn có thể rất dễ nghĩ:

```python
class DatabaseManager(Singleton):
    ...
```

hoặc:

```python
db = DatabaseManager()
```

rồi mọi nơi lấy database manager global.

Ví dụ:

```text
Crawler
   │
   ├── Repository
   │       ↓
   │   DatabaseManager
   │
   ├── Service
   │       ↓
   │   DatabaseManager
   │
   └── Dashboard
           ↓
       DatabaseManager
```

Có vẻ rất tiện.

Nhưng kiến trúc có thể trở nên:

```text
Global State
    ↓
mọi nơi phụ thuộc
    ↓
khó test
    ↓
khó thay thế
    ↓
khó kiểm soát lifecycle
```

---

# 18. Cách tốt hơn: Dependency Injection

Thay vì:

```python
class StoryRepository:

    def __init__(self):
        self.db = DatabaseManager()
```

hãy viết:

```python
class StoryRepository:

    def __init__(self, db):
        self.db = db
```

Composition Root:

```python
db = DatabaseManager()

repository = StoryRepository(db)
```

Kiến trúc:

```text
Composition Root
       │
       ├── DatabaseManager
       │
       ↓
StoryRepository
       ↓
StoryService
```

Dependency được truyền xuống.

---

# 19. Singleton và Repository

Ví dụ bạn có:

```python
class SQLiteStoryRepository:
    ...
```

Không nên mặc định:

```python
class SQLiteStoryRepository:

    def __init__(self):
        self.db = GlobalSingletonDatabase()
```

Tốt hơn:

```python
class SQLiteStoryRepository:

    def __init__(self, db):
        self.db = db
```

Sau đó:

```python
db = DatabaseManager()

story_repository = SQLiteStoryRepository(db)
```

Điều này phù hợp hơn với:

* SOLID
* DIP
* Dependency Injection
* Clean Architecture
* Unit Testing

---

# 20. Test cũng dễ hơn

Không Singleton:

```python
class FakeDatabase:
    def save(self, data):
        print("fake save")


db = FakeDatabase()

repository = StoryRepository(db)
```

Test:

```python
repository.save(story)
```

Ta có thể thay:

```text
Production
    ↓
SQLiteDatabase

Testing
    ↓
FakeDatabase
```

Không cần sửa `StoryRepository`.

Đây chính là sức mạnh của DI.

---

# 21. Khi nào Singleton phù hợp?

Có thể cân nhắc Singleton khi:

### 1. Thực sự cần một instance

Ví dụ:

```text
Application Registry
Configuration Registry
Resource Manager
```

### 2. Lifecycle thực sự mang tính global

Ví dụ resource chỉ nên tồn tại một lần trong process.

### 3. Shared state là chủ ý

Không phải vô tình tạo ra global state.

### 4. Chi phí tạo nhiều instance thực sự có ý nghĩa

Nhưng vẫn cần cân nhắc Factory/Cache/Pool trước khi chọn Singleton.

---

# 22. Khi nào KHÔNG nên dùng?

Không nên biến mọi service thành Singleton:

```python
UserService
OrderService
PaymentService
StoryService
CrawlerService
```

Không nên:

```python
class OrderService(Singleton):
    ...
```

chỉ vì:

> “Application chỉ cần một OrderService.”

Đó chưa phải lý do đủ mạnh.

DI hoàn toàn có thể tạo một instance:

```python
order_service = OrderService(repository)
```

và truyền cùng object đó cho các nơi cần.

Không cần Singleton.

---

# 23. Singleton tạo Global State

Đây là vấn đề lớn nhất.

Ví dụ:

```python
DatabaseManager.instance()
```

ở khắp codebase.

Ta sẽ có:

```text
Module A ──┐
Module B ──┤
Module C ──┼──> Global Singleton
Module D ──┤
Module E ──┘
```

Không biết rõ:

* ai tạo?
* ai thay đổi?
* ai đóng?
* lifecycle bao lâu?
* test có reset được không?

Đây là lý do Singleton thường bị xem là **global state được khoác áo OOP**.

---

# 24. Singleton làm Unit Test khó hơn

Ví dụ:

```python
class Config:

    _instance = None
```

Test 1:

```python
config.debug = True
```

Test 2:

```python
config.debug
```

có thể bị ảnh hưởng bởi Test 1.

Các test không còn độc lập.

Trong khi DI:

```python
service = Service(fake_config)
```

Test nào muốn config gì thì truyền config đó.

---

# 25. Singleton vs Borg

Một pattern khác là **Borg / Monostate**.

Singleton:

```text
A ──┐
    ├── same object
B ──┘
```

Borg:

```text
A ──> object A ──┐
                 │
B ──> object B ──┼── shared state
                 │
C ──> object C ──┘
```

Borg có nhiều object nhưng chúng chia sẻ state.

Ví dụ:

```python
class Borg:

    _state = {}

    def __init__(self):
        self.__dict__ = self._state
```

Test:

```python
a = Borg()
b = Borg()

print(a is b)
```

```text
False
```

Nhưng:

```python
a.name = "Python"

print(b.name)
```

```text
Python
```

Vì state được chia sẻ.

Đây **không phải Singleton**.

---

# 26. So sánh

| Pattern          |                   Object | State | Đặc điểm            |
| ---------------- | -----------------------: | ----: | ------------------- |
| Singleton        |                        1 | chung | Một instance        |
| Borg             |                    nhiều | chung | Shared state        |
| Module Singleton | thường 1 object exported | chung | Pythonic            |
| DI               |                    tùy ý | tùy ý | Dependency explicit |
| Factory          |                    nhiều | tùy ý | Tạo object          |

Điểm cuối rất quan trọng:

> **Factory và Singleton giải quyết hai bài toán khác nhau.**

Factory:

```text
Tạo object nào?
```

Singleton:

```text
Có bao nhiêu instance?
```

---

# 27. Singleton + SOLID

Hãy nhìn lại những gì chúng ta vừa học.

### SRP

Singleton phải có trách nhiệm rõ ràng.

### OCP

Không nên để Singleton tạo ra hàng loạt dependency cố định.

### LSP

Nếu Singleton nằm trong hierarchy thì subtype vẫn phải substitutable.

### ISP

Không nên biến Singleton thành một "God Service" với hàng chục method.

### DIP

Đây là điểm dễ xung đột nhất.

Singleton:

```text
Service
   ↓
Global Singleton
```

DI + DIP:

```text
Service
   ↓
Abstraction
   ↑
Concrete implementation
```

Vì vậy:

> Singleton thường làm dependency trở nên implicit, trong khi DIP khuyến khích dependency explicit.

---

# 28. Một kiến trúc thực tế cho Crawler

Không nên:

```text
                Global Singleton
                 DatabaseManager
                  ↑   ↑   ↑
                  │   │   │
              Parser Service Crawler
```

Tốt hơn:

```text
                 Composition Root
                        │
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
   DatabaseManager   HttpClient      Logger
        │               │
        ↓               ↓
   Repository         Crawler
        │               │
        └───────┬───────┘
                ↓
             Use Case
```

Dependencies được wiring tại một nơi.

Ví dụ:

```python
def build_application():

    db = DatabaseManager()
    client = HttpClient()
    parser = StoryParser()

    repository = SQLiteStoryRepository(db)

    crawler = Crawler(
        client=client,
        parser=parser,
        repository=repository,
    )

    return crawler
```

Đây chính là tư duy **Composition Root + DI** mà bạn đã học ở Buổi 26 và DIP ở Buổi 31.

---

# 29. Một nguyên tắc rất quan trọng

Đừng hỏi:

> “Làm thế nào để biến class này thành Singleton?”

Hãy hỏi:

> “Tại sao application cần chính xác một instance?”

Nếu câu trả lời là:

> “Vì nhiều nơi cần dùng nó.”

Thì chưa đủ.

DI đã giải quyết được việc chia sẻ object:

```python
db = DatabaseManager()

repo1 = Repository(db)
repo2 = AnotherRepository(db)
service = Service(db)
```

Một instance vẫn có thể được chia sẻ mà **không cần Singleton Pattern**.

---

# 30. Bài tập thực hành

## Bài 1 — Singleton cơ bản

Viết:

```python
class AppConfig:
    ...
```

Yêu cầu:

```python
a = AppConfig()
b = AppConfig()

assert a is b
```

---

## Bài 2 — `__init__()` chỉ chạy một lần

```python
class DatabaseManager:
    ...
```

Yêu cầu:

```python
a = DatabaseManager()
b = DatabaseManager()
c = DatabaseManager()
```

Output:

```text
Database initialized
```

chỉ xuất hiện **một lần**.

---

## Bài 3 — Thread-safe

Sử dụng:

```python
threading
Lock
```

Tạo nhiều thread:

```text
Thread 1 ──┐
Thread 2 ──┤
Thread 3 ──┼──> Singleton
Thread 4 ──┤
Thread 5 ──┘
```

Kiểm tra tất cả nhận cùng instance.

---

# 31. Bài tập kiến trúc — rất quan trọng

Giả sử bạn có code:

```python
class StoryRepository:

    def __init__(self):
        self.db = DatabaseManager()
```

và:

```python
class StoryService:

    def __init__(self):
        self.repository = StoryRepository()
```

Sau đó `DatabaseManager` được viết thành Singleton.

### Hãy refactor thành:

```text
Composition Root
       │
       ├── DatabaseManager
       │
       ↓
StoryRepository
       ↓
StoryService
```

Không được để:

```python
StoryService()
```

tự tạo:

```python
StoryRepository()
```

và Repository tự tạo:

```python
DatabaseManager()
```

Mục tiêu:

```python
db = DatabaseManager()

repository = StoryRepository(db)

service = StoryService(repository)
```

Đây là bài tập kết nối trực tiếp:

```text
Composition
      ↓
Dependency Injection
      ↓
DIP
      ↓
Design Pattern
```

---

# 32. Tổng kết Buổi 32

Bạn cần nhớ 6 ý chính:

### 1. Singleton

```text
Một class → một instance
```

### 2. `__new__()`

Dùng để kiểm soát quá trình tạo instance.

### 3. Module Singleton

Trong Python thường là cách đơn giản và tự nhiên hơn:

```python
# config.py

config = Config()
```

### 4. Thread safety

Nếu Singleton được dùng trong concurrent code, phải cân nhắc synchronization.

### 5. Singleton có mặt trái

```text
Singleton
   ↓
Global State
   ↓
Implicit Dependency
   ↓
Testing khó
```

### 6. Singleton không thay thế DI

Đây là câu quan trọng nhất của buổi học:

> **Một object được chia sẻ không đồng nghĩa với việc nó phải là Singleton.**

Bạn hoàn toàn có thể:

```python
db = DatabaseManager()

service1 = Service(db)
service2 = Service(db)
service3 = Service(db)
```

mà vẫn chỉ có **một instance**.

---

# 33. Bức tranh Design Pattern

Chúng ta vừa bắt đầu:

```text
Design Pattern
      │
      ├── Creational
      │      │
      │      ├── Singleton ← Buổi 32
      │      ├── Factory  ← Buổi 33
      │      └── Builder  ← Buổi 34
      │
      ├── Behavioral
      │      ├── Strategy
      │      ├── Observer
      │      └── Command
      │
      └── Data Access
             └── Repository
```

Và pattern tiếp theo sẽ rất quan trọng:

# **Buổi 33 — Factory Pattern**

Chúng ta sẽ học cách thiết kế:

```text
Factory
   │
   ├── SiteAParser
   ├── SiteBParser
   ├── SiteCParser
   └── SiteDParser
```

để **tạo đúng implementation mà không để client phụ thuộc trực tiếp vào class cụ thể**.

Đặc biệt, Buổi 33 sẽ nối trực tiếp:

```text
Factory
   +
OCP
   +
DIP
   +
DI
   +
Plugin Architecture
```

và áp dụng vào **Parser Factory của crawler**.
