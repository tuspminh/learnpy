# OOP Deep Dive - Buổi 11

# Composition, Aggregation, Delegation và Mixins (Deep Dive)

Đây là một trong những buổi quan trọng nhất của toàn bộ khóa OOP.

Thực tế, trong các dự án Python lớn (Django, SQLAlchemy, PySide6, FastAPI, Requests...), **kế thừa (Inheritance) được dùng ít hơn nhiều so với Composition**.

Có một câu nói rất nổi tiếng trong lập trình hướng đối tượng:

> **Favor Composition over Inheritance**
> 
> (Ưu tiên Composition hơn Inheritance.)

Sau buổi này, bạn sẽ hiểu tại sao.

---

# Mục tiêu

Sau buổi học này bạn sẽ hiểu:

- Composition
- Aggregation
- Association
- Delegation
- Mixins
- HAS-A Relationship
- IS-A vs HAS-A
- Khi nào dùng Inheritance
- Khi nào dùng Composition

---

# 1. Ôn tập: Inheritance

Kế thừa biểu diễn mối quan hệ:

```text-x-trilium-auto
IS-A
```

Ví dụ

```text-x-trilium-auto
Dog IS-A Animal

Car IS-A Vehicle

Manager IS-A Employee
```

Code

```text-x-trilium-auto
class Animal:
    pass


class Dog(Animal):
    pass
```

Không có vấn đề gì.

---

# 2. Nhưng nhiều người dùng sai

Ví dụ:

```text-x-trilium-auto
class Engine:
    pass


class Car(Engine):
    pass
```

Điều này sai.

Car KHÔNG PHẢI Engine.

Đúng phải là:

```text-x-trilium-auto
Car

HAS-A

Engine
```

---

# 3. HAS-A Relationship

Ví dụ:

```text-x-trilium-auto
Car

↓

Engine
```

Xe có động cơ.

Không phải:

```text-x-trilium-auto
Car

↓

Là Engine
```

---

Code

```text-x-trilium-auto
class Engine:

    def start(self):
        print("Engine started")


class Car:

    def __init__(self):

        self.engine = Engine()
```

Đây là:

# Composition

---

# 4. Composition là gì?

Composition:

```text-x-trilium-auto
Object

↓

Chứa

↓

Object khác
```

Ví dụ

```text-x-trilium-auto
class CPU:
    pass


class RAM:
    pass


class Computer:

    def __init__(self):

        self.cpu = CPU()

        self.ram = RAM()
```

Sơ đồ

```text-x-trilium-auto
Computer

├── CPU

├── RAM
```

Computer được cấu tạo từ CPU và RAM.

---

# 5. Composition mạnh hơn kế thừa ở đâu?

Ví dụ

```text-x-trilium-auto
class DieselEngine:
    pass

class ElectricEngine:
    pass
```

Car:

```text-x-trilium-auto
class Car:

    def __init__(self, engine):

        self.engine = engine
```

Sử dụng

```text-x-trilium-auto
car = Car(DieselEngine())

car2 = Car(ElectricEngine())
```

Không cần sửa class `Car`.

---

# 6. Nếu dùng Inheritance?

Bạn sẽ phải:

```text-x-trilium-auto
DieselCar

ElectricCar

HybridCar

...
```

Class sẽ tăng rất nhanh.

Đây gọi là:

> Class Explosion

---

# 7. Aggregation

Aggregation rất giống Composition.

Khác ở vòng đời object.

Composition

```text-x-trilium-auto
Car

↓

Engine

↓

Engine chết khi Car chết
```

Aggregation

```text-x-trilium-auto
Team

↓

Player

↓

Player vẫn tồn tại
```

Ví dụ

```text-x-trilium-auto
class Player:

    def __init__(self,name):

        self.name=name
```

---

```text-x-trilium-auto
class Team:

    def __init__(self):

        self.players=[]
```

---

```text-x-trilium-auto
p=Player("An")

team=Team()

team.players.append(p)
```

Nếu:

```text-x-trilium-auto
del team
```

Player vẫn còn.

---

# 8. So sánh

Composition

```text-x-trilium-auto
House

↓

Room
```

Xóa House

↓

Room cũng mất.

---

Aggregation

```text-x-trilium-auto
School

↓

Student
```

Xóa School

↓

Student vẫn tồn tại.

---

# 9. Association

Association đơn giản là:

Hai object biết nhau.

Ví dụ

```text-x-trilium-auto
class Teacher:
    pass


class Student:
    pass
```

```text-x-trilium-auto
teacher.students.append(student)
```

Không có sở hữu.

Chỉ liên kết.

---

# 10. Delegation

Delegation cực kỳ phổ biến.

Ví dụ

```text-x-trilium-auto
class Engine:

    def start(self):

        print("Engine started")
```

---

```text-x-trilium-auto
class Car:

    def __init__(self):

        self.engine=Engine()

    def start(self):

        self.engine.start()
```

Người dùng:

```text-x-trilium-auto
car.start()
```

Thực tế:

```text-x-trilium-auto
Car

↓

Engine.start()
```

Car giao việc cho Engine.

Đây gọi là:

Delegation

---

# 11. Delegation trong Python

Ví dụ

```text-x-trilium-auto
class Logger:

    def log(self,msg):

        print(msg)
```

---

```text-x-trilium-auto
class Service:

    def __init__(self):

        self.logger=Logger()

    def log(self,msg):

        self.logger.log(msg)
```

Service không log.

Logger log.

---

# 12. Mixins là gì?

Mixin KHÔNG PHẢI Base Class.

Mixin chỉ thêm một hành vi nhỏ.

Ví dụ

```text-x-trilium-auto
class JsonMixin:

    def to_json(self):

        ...
```

Mixin không nên có trách nhiệm quản lý trạng thái chính của đối tượng.

---

# 13. Ví dụ

```text-x-trilium-auto
class TimestampMixin:

    def created_time(self):

        ...
```

---

```text-x-trilium-auto
class SaveMixin:

    def save(self):

        ...
```

---

```text-x-trilium-auto
class Book(

    TimestampMixin,

    SaveMixin

):
    pass
```

Book có thêm hai khả năng:

- save
- timestamp

---

# 14. Đặc điểm Mixins

Mixin thường:

- nhỏ
- ít state
- chỉ thêm chức năng
- không đại diện cho đối tượng trong miền nghiệp vụ

Ví dụ

```text-x-trilium-auto
Book

IS-A Timestamp?
```

Không.

Timestamp chỉ là khả năng.

---

# 15. Django dùng Mixins

Ví dụ

```text-x-trilium-auto
class BookView(

    LoginRequiredMixin,

    PermissionRequiredMixin,

    ListView

):
```

Các mixin thêm:

- login
- permission

Không tạo class mới.

---

# 16. PySide6

Ví dụ

```text-x-trilium-auto
class MainWindow(

    QMainWindow,

    Ui_MainWindow
):
```

`Ui_MainWindow` gần giống một mixin: nó bổ sung phương thức `setupUi()` và các thuộc tính giao diện, còn `QMainWindow` mới là lớp đại diện cho cửa sổ chính.

---

# 17. Hệ thống crawler của chúng ta

Không nên:

```text-x-trilium-auto
TruyenFullRetryCacheProxySource
```

Thay vào đó:

```text-x-trilium-auto
class RetryMixin:
    pass

class CacheMixin:
    pass

class HeaderMixin:
    pass
```

---

```text-x-trilium-auto
class TruyenFullSource(

    RetryMixin,

    CacheMixin,

    HeaderMixin,

    BaseSource
):
    pass
```

Đẹp hơn rất nhiều.

---

# 18. Thiết kế Plugin

Base:

```text-x-trilium-auto
class BaseSource:

    def fetch(self):

        ...
```

Mixin

```text-x-trilium-auto
class RetryMixin:

    def fetch(self):

        print("Retry")

        return super().fetch()
```

Mixin

```text-x-trilium-auto
class CacheMixin:

    def fetch(self):

        print("Cache")

        return super().fetch()
```

Source

```text-x-trilium-auto
class TruyenFull(

    RetryMixin,

    CacheMixin,

    BaseSource

):
    pass
```

MRO

```text-x-trilium-auto
Retry

↓

Cache

↓

Download
```

---

# 19. Khi nào dùng gì?

## Dùng Inheritance

Khi:

```text-x-trilium-auto
Dog

IS-A

Animal
```

---

## Dùng Composition

Khi:

```text-x-trilium-auto
Car

HAS-A

Engine
```

---

## Dùng Aggregation

Khi:

```text-x-trilium-auto
Team

HAS

Players
```

nhưng Player sống độc lập.

---

## Dùng Mixins

Khi muốn thêm:

- Logging
- Retry
- Cache
- Timestamp
- Serialization
- Permission

---

## Dùng Delegation

Khi object chỉ chuyển việc sang object khác.

---

# 20. Sai lầm phổ biến

## Sai

Dùng kế thừa cho mọi thứ.

Ví dụ

```text-x-trilium-auto
class Car(Engine)
```

---

## Sai

Mixin có quá nhiều trạng thái.

Mixin nên nhẹ.

---

## Sai

Mixin phụ thuộc chặt vào một class cụ thể.

Mixin lý tưởng nên tái sử dụng được ở nhiều lớp khác nhau.

---

## Sai

Lạm dụng Multiple Inheritance để biểu diễn quan hệ HAS-A.

---

# 21. So sánh

| Quan hệ | Ý nghĩa |
| --- | --- |
| Inheritance | IS-A |
| Composition | HAS-A (sở hữu mạnh) |
| Aggregation | HAS-A (sở hữu yếu) |
| Association | Có liên kết |
| Delegation | Giao việc |
| Mixins | Thêm hành vi |

---

# 22. Áp dụng vào dự án Crawler

Đây là kiến trúc mà mình khuyến nghị cho dự án crawler truyện của bạn.

```text-x-trilium-auto
                 BaseSource
                     ▲
                     │
          TruyenFullSource
                     ▲
     ┌───────────────┼───────────────┐
     │               │               │
 RetryMixin     CacheMixin     HeaderMixin
```

Trong khi đó, các thành phần khác nên dùng **Composition**:

```text-x-trilium-auto
CrawlerService
│
├── HttpClient
├── Parser
├── Database
├── Logger
└── Scheduler
```

Ví dụ:

```text-x-trilium-auto
class CrawlerService:
    def __init__(
        self,
        http_client,
        parser,
        repository,
        logger,
    ):
        self.http_client = http_client
        self.parser = parser
        self.repository = repository
        self.logger = logger
```

Ở đây:

- `CrawlerService` **HAS-A** `HttpClient`
- `CrawlerService` **HAS-A** `Parser`
- `CrawlerService` **HAS-A** `Repository`

Đây là thiết kế linh hoạt hơn rất nhiều so với việc kế thừa.

---

# Tổng kết Buổi 11

```text-x-trilium-auto
                    OOP Relationship

                   +--------------+
                   |     IS-A     |
                   | Inheritance  |
                   +--------------+

                           |

          +------------------------------------+

                           |

                   +--------------+
                   |    HAS-A     |
                   | Composition  |
                   +--------------+

                           |

         +----------+-----------+-----------+

         |                      |           |

 Aggregation             Delegation      Mixins
```

## Điều quan trọng nhất cần nhớ

> **Không phải cứ có hai class là dùng kế thừa.**

Hãy tự hỏi:

- Đây có phải quan hệ **IS-A** không?
  - Có → Cân nhắc **Inheritance**.
- Đây có phải quan hệ **HAS-A** không?
  - Có → Thường nên dùng **Composition**.
- Tôi chỉ muốn bổ sung một khả năng nhỏ (logging, retry, cache...)?
  - → Dùng **Mixin**.
- Tôi chỉ muốn chuyển việc sang một đối tượng khác?
  - → Dùng **Delegation**.

Đây là nguyên tắc mà hầu hết các dự án Python chuyên nghiệp đều áp dụng.

---

# Bài tập thực hành

## Bài 1

Thiết kế hệ thống quản lý xe:

- `Engine`
- `Transmission`
- `Wheel`
- `Car`

Yêu cầu:

- `Car` sử dụng **Composition** để chứa các thành phần trên.
- Viết phương thức `start()` của `Car` bằng cách **delegate** sang `Engine.start()`.

---

## Bài 2

Thiết kế hệ thống bóng đá:

- `Player`
- `Team`

Yêu cầu:

- Một `Team` chứa nhiều `Player`.
- Chứng minh đây là **Aggregation** bằng cách tạo `Player`, thêm vào `Team`, sau đó xóa `Team` và giải thích vì sao `Player` vẫn có thể tồn tại.

---

## Bài 3

Tạo ba mixin:

- `LoggingMixin`
- `RetryMixin`
- `JsonMixin`

Sau đó tạo:

```text-x-trilium-auto
class ApiClient(
    LoggingMixin,
    RetryMixin,
    JsonMixin,
):
    pass
```

Mỗi mixin nên thêm một hành vi riêng và không quản lý trạng thái nghiệp vụ.

---

## Bài 4 (Áp dụng dự án crawler)

Thiết kế kiến trúc sau bằng mã Python:

```text-x-trilium-auto
CrawlerService
│
├── HttpClient
├── HtmlParser
├── NovelRepository
├── Logger
└── Source (BaseSource/TruyenFullSource)
```

Yêu cầu:

- `CrawlerService` dùng **Composition** để kết hợp các thành phần.
- `TruyenFullSource` kế thừa `BaseSource`.
- Thêm `RetryMixin` và `CacheMixin` vào `TruyenFullSource`.
- Vẽ MRO của `TruyenFullSource` và giải thích luồng thực thi của `fetch()` khi tất cả các lớp đều gọi `super().fetch()`.

---

# Chuẩn bị cho Buổi 12

Từ buổi sau, chúng ta sẽ bước sang **Polymorphism (Đa hình)**, một trong bốn trụ cột của OOP.

Chúng ta sẽ không chỉ học override, mà sẽ đi sâu vào:

- Đa hình thực sự là gì.
- Duck Typing – triết lý đặc trưng của Python.
- Abstract Base Classes (ABC).
- `abc.ABC`, `@abstractmethod`.
- Protocol (PEP 544) và Static Duck Typing.
- Cách thiết kế API mở rộng cho plugin crawler và các ứng dụng lớn.

Đây là phần giúp bạn viết những hệ thống có khả năng mở rộng cao mà không cần sửa mã nguồn hiện có.