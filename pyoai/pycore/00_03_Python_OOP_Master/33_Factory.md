# Python OOP Master — Buổi 33

# Factory Pattern

Sau Singleton, chúng ta học một Pattern cực kỳ quan trọng trong Python architecture:

> **Factory Pattern — tách logic tạo object khỏi nơi sử dụng object.**

Đặc biệt với project crawler của bạn, Factory rất hữu ích để xử lý:

```text
Site A → SiteAParser
Site B → SiteBParser
Site C → SiteCParser
```

mà `Crawler` **không cần biết cách tạo từng Parser**.

---

# 1. Mục tiêu

Sau buổi này bạn sẽ hiểu:

* Factory Pattern là gì?
* Vì sao cần Factory?
* Simple Factory
* Factory Method
* Abstract Factory
* Factory + Polymorphism
* Factory + OCP
* Factory + DIP
* Registry-based Factory trong Python
* Factory cho Parser
* Factory cho Repository
* Factory cho HTTP Client
* Khi nào nên và không nên dùng Factory

---

# 2. Vấn đề mà Factory giải quyết

Giả sử chúng ta có:

```python
class SiteAParser:
    pass


class SiteBParser:
    pass


class SiteCParser:
    pass
```

Crawler:

```python
class Crawler:

    def crawl(self, site):
        if site == "site_a":
            parser = SiteAParser()

        elif site == "site_b":
            parser = SiteBParser()

        elif site == "site_c":
            parser = SiteCParser()

        ...
```

Ban đầu nhìn khá đơn giản.

Nhưng khi có:

```text
Site A
Site B
Site C
Site D
Site E
...
Site Z
```

thì:

```python
if ...
elif ...
elif ...
elif ...
```

sẽ trở thành một vấn đề.

---

# 3. Client đang biết quá nhiều

Trong ví dụ trên:

```text
Crawler
 ├── biết SiteAParser
 ├── biết SiteBParser
 ├── biết SiteCParser
 └── biết cách tạo chúng
```

Crawler đang đảm nhiệm hai việc:

```text
1. Crawl
2. Tạo Parser
```

Điều này vi phạm tư duy **SRP**.

Ngoài ra:

```text
Crawler
    ↓
Concrete Parser
```

làm dependency trở nên chặt.

Factory giúp đưa logic tạo object ra ngoài:

```text
Crawler
   ↓
Parser abstraction

ParserFactory
   ↓
Concrete Parser
```

---

# 4. Factory Pattern là gì?

Factory là một cơ chế chuyên trách việc:

> **Tạo object phù hợp dựa trên một input/context nào đó.**

Ví dụ:

```python
parser = ParserFactory.create("site_a")
```

Factory quyết định:

```text
"site_a"
    ↓
SiteAParser()
```

hoặc:

```text
"site_b"
    ↓
SiteBParser()
```

Client chỉ cần:

```python
parser.parse(html)
```

Client không cần biết:

```python
SiteAParser()
```

được tạo như thế nào.

---

# 5. Simple Factory

Cách đơn giản nhất:

```python
class SiteAParser:

    def parse(self, html):
        return "Parse Site A"


class SiteBParser:

    def parse(self, html):
        return "Parse Site B"


class ParserFactory:

    @staticmethod
    def create(site):

        if site == "site_a":
            return SiteAParser()

        if site == "site_b":
            return SiteBParser()

        raise ValueError(f"Unknown site: {site}")
```

Sử dụng:

```python
parser = ParserFactory.create("site_a")

print(parser.parse("<html>"))
```

Output:

```text
Parse Site A
```

---

# 6. Client đã đơn giản hơn

Không Factory:

```python
if site == "site_a":
    parser = SiteAParser()
elif site == "site_b":
    parser = SiteBParser()
```

Có Factory:

```python
parser = ParserFactory.create(site)
```

Kiến trúc:

```text
          Crawler
             │
             ↓
       ParserFactory
          /      \
         ↓        ↓
 SiteAParser   SiteBParser
```

Crawler không cần trực tiếp tạo Parser.

---

# 7. Factory + ABC

Ta có thể kết hợp Factory với abstraction.

```python
from abc import ABC, abstractmethod


class StoryParser(ABC):

    @abstractmethod
    def parse(self, html):
        pass
```

Concrete implementations:

```python
class SiteAParser(StoryParser):

    def parse(self, html):
        return {
            "site": "A",
            "title": "Story A",
        }


class SiteBParser(StoryParser):

    def parse(self, html):
        return {
            "site": "B",
            "title": "Story B",
        }
```

Factory:

```python
class ParserFactory:

    @staticmethod
    def create(site: str) -> StoryParser:

        if site == "site_a":
            return SiteAParser()

        if site == "site_b":
            return SiteBParser()

        raise ValueError(f"Unknown site: {site}")
```

Client:

```python
parser = ParserFactory.create("site_a")

result = parser.parse(html)
```

Điểm quan trọng:

```text
Crawler
   ↓
StoryParser
   ↑
   │
 ┌─┴───────────────┐
 │                 │
SiteAParser    SiteBParser
```

Factory chịu trách nhiệm tạo implementation.

---

# 8. Factory + Polymorphism

Đây chính là sức mạnh thực sự.

Crawler:

```python
class Crawler:

    def __init__(self, parser):
        self.parser = parser

    def crawl(self, html):
        return self.parser.parse(html)
```

Ta có thể:

```python
parser = ParserFactory.create("site_a")

crawler = Crawler(parser)
```

hoặc:

```python
parser = ParserFactory.create("site_b")

crawler = Crawler(parser)
```

Crawler không thay đổi.

```text
Site A
  ↓
SiteAParser
  ↓
      ┐
      ├──> Crawler
      ┘
Site B
  ↓
SiteBParser
  ↓
      ┐
      ├──> Crawler
      ┘
Site C
  ↓
SiteCParser
```

Đây là:

```text
Factory
   +
Polymorphism
   +
Dependency Injection
```

---

# 9. Vấn đề của Simple Factory

Simple Factory tốt hơn `if/elif` nằm trong Crawler.

Nhưng Factory vẫn có:

```python
if site == "site_a":
    ...
elif site == "site_b":
    ...
elif site == "site_c":
    ...
```

Khi thêm:

```text
Site D
```

phải sửa:

```python
ParserFactory
```

Điều này chưa thật sự tốt với **OCP**.

Chúng ta có thể tiến thêm một bước.

---

# 10. Registry-based Factory

Python rất phù hợp với cách này.

Ta dùng dictionary:

```python
class ParserFactory:

    _parsers = {
        "site_a": SiteAParser,
        "site_b": SiteBParser,
    }

    @classmethod
    def create(cls, site):
        try:
            parser_class = cls._parsers[site]
        except KeyError:
            raise ValueError(
                f"Unknown site: {site}"
            )

        return parser_class()
```

Sử dụng:

```python
parser = ParserFactory.create("site_a")
```

---

# 11. Tách `register()`

Ta có thể thiết kế đẹp hơn:

```python
class ParserFactory:

    _parsers = {}

    @classmethod
    def register(cls, name, parser_class):
        cls._parsers[name] = parser_class

    @classmethod
    def create(cls, name):
        try:
            parser_class = cls._parsers[name]
        except KeyError:
            raise ValueError(
                f"Unknown parser: {name}"
            )

        return parser_class()
```

Đăng ký:

```python
ParserFactory.register(
    "site_a",
    SiteAParser,
)

ParserFactory.register(
    "site_b",
    SiteBParser,
)
```

Sau đó:

```python
parser = ParserFactory.create("site_a")
```

---

# 12. Đây chính là Plugin Architecture

Bây giờ hãy tưởng tượng:

```text
ParserFactory
     │
     ├── site_a → SiteAParser
     ├── site_b → SiteBParser
     └── site_c → SiteCParser
```

Plugin có thể tự đăng ký:

```python
ParserFactory.register(
    "site_c",
    SiteCParser,
)
```

Core crawler không cần sửa.

Đây là một bước tiến lớn:

```text
Factory
   ↓
Registry
   ↓
Plugin Architecture
```

---

# 13. Ví dụ hoàn chỉnh cho Story Crawler

Ta thiết kế:

```text
domain/
    story.py

application/
    parser.py
    crawler.py

infrastructure/
    parsers/
        site_a.py
        site_b.py

factory/
    parser_factory.py
```

---

## Interface

```python
from abc import ABC, abstractmethod


class StoryParser(ABC):

    @abstractmethod
    def parse(self, html):
        pass
```

---

## Site A

```python
class SiteAParser(StoryParser):

    def parse(self, html):

        return {
            "title": "Story from Site A",
            "chapters": [],
        }
```

---

## Site B

```python
class SiteBParser(StoryParser):

    def parse(self, html):

        return {
            "title": "Story from Site B",
            "chapters": [],
        }
```

---

## Factory

```python
class ParserFactory:

    _parsers = {}

    @classmethod
    def register(cls, name, parser_class):
        cls._parsers[name] = parser_class

    @classmethod
    def create(cls, name):

        try:
            parser_class = cls._parsers[name]
        except KeyError:
            raise ValueError(
                f"Unknown parser: {name}"
            )

        return parser_class()
```

---

## Registration

```python
ParserFactory.register(
    "site_a",
    SiteAParser,
)

ParserFactory.register(
    "site_b",
    SiteBParser,
)
```

---

## Crawler

```python
class Crawler:

    def __init__(self, parser):
        self.parser = parser

    def crawl(self, html):

        return self.parser.parse(html)
```

---

## Composition Root

```python
def build_crawler(site):

    parser = ParserFactory.create(site)

    return Crawler(parser)
```

Sử dụng:

```python
crawler = build_crawler("site_a")

story = crawler.crawl(html)

print(story)
```

---

# 14. Flow hoàn chỉnh

```text
                  Composition Root
                         │
                         ↓
                  ParserFactory
                         │
                ┌────────┼────────┐
                ↓        ↓        ↓
             SiteA    SiteB    SiteC
             Parser   Parser   Parser
                │        │        │
                └────────┼────────┘
                         ↓
                      Crawler
                         ↓
                     Story Data
```

Đây là kiến trúc rất phù hợp với crawler framework.

---

# 15. Factory không nhất thiết phải là class

Đây là điểm Python rất quan trọng.

Factory có thể chỉ là function:

```python
def create_parser(site):

    if site == "site_a":
        return SiteAParser()

    if site == "site_b":
        return SiteBParser()

    raise ValueError(
        f"Unknown site: {site}"
    )
```

Sử dụng:

```python
parser = create_parser("site_a")
```

Đây cũng là Factory.

Không cần cố biến mọi Factory thành:

```python
class SomethingFactory:
```

---

# 16. Function Factory

Trong Python, nếu logic đơn giản:

```python
def create_parser(site):
    ...
```

thường dễ đọc hơn:

```python
class ParserFactory:
    @staticmethod
    def create(site):
        ...
```

Hai cách đều hợp lệ.

Hãy chọn dựa trên độ phức tạp.

---

# 17. Factory Method

Bây giờ đến một khái niệm chính thức hơn:

> **Factory Method**

Thay vì một factory class tập trung tạo mọi object, một class có thể định nghĩa một method chuyên tạo product.

Ví dụ:

```python
from abc import ABC, abstractmethod


class Notification(ABC):

    @abstractmethod
    def send(self, message):
        pass
```

Products:

```python
class EmailNotification(Notification):

    def send(self, message):
        print("Email:", message)


class SMSNotification(Notification):

    def send(self, message):
        print("SMS:", message)
```

Creator:

```python
class NotificationService(ABC):

    @abstractmethod
    def create_notification(self):
        pass

    def notify(self, message):

        notification = self.create_notification()

        notification.send(message)
```

Concrete creators:

```python
class EmailNotificationService(NotificationService):

    def create_notification(self):
        return EmailNotification()


class SMSNotificationService(NotificationService):

    def create_notification(self):
        return SMSNotification()
```

Sử dụng:

```python
service = EmailNotificationService()

service.notify("Hello")
```

---

# 18. Simple Factory vs Factory Method

|              | Simple Factory | Factory Method                    |
| ------------ | -------------- | --------------------------------- |
| Cách tạo     | Một factory    | Method trong creator              |
| `if/elif`    | thường có      | thường được phân tán qua subclass |
| Polymorphism | Có             | Rất mạnh                          |
| OCP          | Có thể hạn chế | tốt hơn                           |
| Độ phức tạp  | thấp           | cao hơn                           |

Không nên sử dụng Factory Method chỉ vì nó "chuẩn Design Pattern".

Nếu:

```python
def create_parser(site):
    ...
```

đã đủ tốt thì cứ dùng.

---

# 19. Abstract Factory

Một bước cao hơn là:

> **Tạo cả một family of related objects.**

Ví dụ UI:

```text
Windows UI
 ├── Button
 └── Checkbox

Mac UI
 ├── Button
 └── Checkbox
```

Abstract Factory:

```python
from abc import ABC, abstractmethod


class UIFactory(ABC):

    @abstractmethod
    def create_button(self):
        pass

    @abstractmethod
    def create_checkbox(self):
        pass
```

Windows:

```python
class WindowsFactory(UIFactory):

    def create_button(self):
        return WindowsButton()

    def create_checkbox(self):
        return WindowsCheckbox()
```

Mac:

```python
class MacFactory(UIFactory):

    def create_button(self):
        return MacButton()

    def create_checkbox(self):
        return MacCheckbox()
```

Abstract Factory phù hợp khi bạn cần tạo **nhóm object liên quan với nhau**.

---

# 20. Simple Factory → Factory Method → Abstract Factory

Có thể hình dung:

```text
Simple Factory
      ↓
Factory Method
      ↓
Abstract Factory
```

Nhưng **không phải cấp độ bắt buộc**.

Không phải:

```text
Factory Method > Simple Factory
```

theo nghĩa lúc nào cũng tốt hơn.

Pattern chỉ là công cụ.

---

# 21. Factory + OCP

Đây là điểm quan trọng.

Nếu viết:

```python
class ParserFactory:

    _parsers = {}
```

và:

```python
register()
```

ta có:

```text
Core
 │
 └── Factory
       ↑
       │
   register
       ↑
 ┌─────┼─────┐
SiteA SiteB SiteC
```

Thêm:

```python
class SiteDParser(StoryParser):
    ...
```

rồi:

```python
ParserFactory.register(
    "site_d",
    SiteDParser,
)
```

Core Crawler không thay đổi.

Đây là tư duy **Open/Closed Principle**.

---

# 22. Factory + DIP

Crawler:

```python
class Crawler:

    def __init__(self, parser):
        self.parser = parser
```

Crawler phụ thuộc:

```text
StoryParser
```

chứ không phụ thuộc:

```text
SiteAParser
SiteBParser
SiteCParser
```

Factory tạo concrete object:

```text
Factory
   ↓
Concrete implementation
   ↓
Abstraction
   ↓
Crawler
```

Factory nằm ở vùng composition/wiring.

Đây là cách rất đẹp để kết hợp:

```text
Factory
+
DIP
+
DI
```

---

# 23. Factory + Dependency Injection

Có hai cách:

### Cách 1

Factory trực tiếp tạo dependency:

```python
parser = ParserFactory.create("site_a")

crawler = Crawler(parser)
```

### Cách 2

Factory chỉ được sử dụng tại Composition Root:

```python
def build_application():

    parser = ParserFactory.create("site_a")

    crawler = Crawler(
        parser=parser
    )

    return crawler
```

Tôi ưu tiên cách 2.

Business/application code không nên tự ý gọi Factory khắp nơi.

---

# 24. Factory cho Repository

Factory không chỉ dành cho Parser.

Ví dụ:

```text
SQLite
PostgreSQL
Memory
```

Interface:

```python
class StoryRepository:
    ...
```

Factory:

```python
def create_repository(storage):

    if storage == "sqlite":
        return SQLiteStoryRepository()

    if storage == "memory":
        return InMemoryStoryRepository()

    raise ValueError(
        f"Unknown storage: {storage}"
    )
```

Sử dụng:

```python
repository = create_repository("sqlite")
```

---

# 25. Factory cho HTTP Client

Ví dụ:

```text
httpx
requests
fake
```

Factory:

```python
def create_http_client(kind):

    if kind == "httpx":
        return HttpxClient()

    if kind == "fake":
        return FakeHttpClient()

    raise ValueError(
        f"Unknown client: {kind}"
    )
```

Testing:

```python
client = create_http_client("fake")
```

Production:

```python
client = create_http_client("httpx")
```

---

# 26. Factory cho Database

Có thể:

```python
def create_database(config):

    if config.backend == "sqlite":
        return SQLiteDatabase(
            config.database_url
        )

    if config.backend == "postgres":
        return PostgresDatabase(
            config.database_url
        )

    raise ValueError(
        f"Unsupported backend: {config.backend}"
    )
```

Nhưng cần nhớ:

> Factory tạo Database không có nghĩa Database phải là Singleton.

Hai khái niệm hoàn toàn khác nhau.

---

# 27. Singleton vs Factory

Đây là một câu hỏi thường gặp.

### Singleton

Giải quyết:

```text
Có bao nhiêu instance?
```

### Factory

Giải quyết:

```text
Tạo instance nào?
```

Ví dụ:

```text
Factory
   │
   ├── SQLiteRepository
   ├── MemoryRepository
   └── PostgresRepository
```

Factory quyết định **loại object**.

Singleton quyết định **số lượng instance**.

Có thể kết hợp:

```text
Factory
   ↓
Singleton implementation
```

nhưng không nên mặc định làm vậy.

---

# 28. Factory vs Constructor

Nếu chỉ:

```python
user = User(name="Minh")
```

thì không cần Factory.

Factory hữu ích khi:

```text
loại object phụ thuộc runtime
        hoặc
quá trình tạo object phức tạp
        hoặc
cần ẩn concrete implementation
```

Ví dụ:

```python
parser = create_parser(site)
```

rất hợp lý.

Nhưng:

```python
user = UserFactory.create(name)
```

chỉ để thay cho:

```python
User(name)
```

thì thường là overengineering.

---

# 29. Factory và cấu hình runtime

Factory đặc biệt hữu ích khi implementation được quyết định bởi config:

```python
config.parser = "site_a"
```

Sau đó:

```python
parser = ParserFactory.create(
    config.parser
)
```

Hoặc:

```text
CLI
 │
 ├── --site site_a
 │
 ↓
Factory
 │
 ↓
SiteAParser
```

Điều này rất phù hợp với crawler CLI của bạn.

---

# 30. Registry Factory hoàn chỉnh hơn

Ta có thể viết:

```python
from typing import Type


class ParserFactory:

    _registry: dict[str, Type[StoryParser]] = {}

    @classmethod
    def register(
        cls,
        name: str,
        parser_class: Type[StoryParser],
    ):
        if name in cls._registry:
            raise ValueError(
                f"Parser already registered: {name}"
            )

        cls._registry[name] = parser_class

    @classmethod
    def create(cls, name: str) -> StoryParser:

        try:
            parser_class = cls._registry[name]
        except KeyError:
            raise ValueError(
                f"Unknown parser: {name}"
            )

        return parser_class()
```

Registration:

```python
ParserFactory.register(
    "site_a",
    SiteAParser,
)
```

Creation:

```python
parser = ParserFactory.create(
    "site_a"
)
```

---

# 31. Kiểm tra interface

Ta có thể thêm validation:

```python
class ParserFactory:

    _registry = {}

    @classmethod
    def register(cls, name, parser_class):

        if not issubclass(
            parser_class,
            StoryParser
        ):
            raise TypeError(
                "Parser must inherit StoryParser"
            )

        cls._registry[name] = parser_class
```

Bây giờ:

```python
ParserFactory.register(
    "site_a",
    SiteAParser,
)
```

hợp lệ.

Nhưng:

```python
class NotParser:
    pass
```

```python
ParserFactory.register(
    "bad",
    NotParser,
)
```

sẽ bị từ chối.

---

# 32. Nhưng Python còn có Duck Typing

Nếu bạn không muốn ép inheritance:

```python
class StoryParser(Protocol):
    def parse(self, html):
        ...
```

Factory có thể làm việc với Protocol.

Điều này rất hợp với Python hiện đại:

```text
Factory
   ↓
Protocol
   ↑
Concrete Parser
```

Không nhất thiết mọi implementation phải kế thừa ABC.

---

# 33. Factory trong kiến trúc Clean Architecture

Một cách tổ chức:

```text
src/
└── app/
    ├── domain/
    │
    ├── application/
    │   ├── ports/
    │   │   └── story_parser.py
    │   └── use_cases/
    │
    └── infrastructure/
        ├── parsers/
        │   ├── site_a.py
        │   ├── site_b.py
        │   └── site_c.py
        │
        └── factories/
            └── parser_factory.py
```

Dependency:

```text
Application
     ↓
StoryParser
     ↑
     │
Infrastructure
     │
 ┌───┼────┐
 A   B    C
```

Factory nằm ở phía infrastructure/composition.

---

# 34. Một lỗi kiến trúc cần tránh

Đừng viết:

```python
class Crawler:

    def crawl(self, site):

        parser = ParserFactory.create(site)

        ...
```

nếu bạn đang muốn application layer hoàn toàn độc lập với infrastructure.

Tốt hơn:

```python
parser = ParserFactory.create(site)

crawler = Crawler(parser)
```

Sau đó:

```python
crawler.crawl(html)
```

Như vậy Factory chỉ xuất hiện tại **Composition Root**.

---

# 35. Testing Factory

Test:

```python
def test_create_site_a_parser():

    parser = ParserFactory.create(
        "site_a"
    )

    assert isinstance(
        parser,
        SiteAParser
    )
```

Test unknown:

```python
import pytest


def test_unknown_parser():

    with pytest.raises(ValueError):
        ParserFactory.create(
            "unknown"
        )
```

Test registration:

```python
def test_register_parser():

    ParserFactory.register(
        "site_test",
        SiteAParser,
    )

    parser = ParserFactory.create(
        "site_test"
    )

    assert isinstance(
        parser,
        SiteAParser
    )
```

---

# 36. Factory có thể kết hợp Plugin

Đây là hướng nâng cao cho project của bạn.

Ví dụ:

```text
plugins/
├── site_a/
│   └── parser.py
├── site_b/
│   └── parser.py
└── site_c/
    └── parser.py
```

Mỗi plugin:

```python
ParserFactory.register(
    "site_a",
    SiteAParser,
)
```

Core:

```text
Crawler Framework
       │
       ↓
ParserFactory
       ↑
       │
 ┌─────┼─────┐
 ↓     ↓     ↓
A     B     C
Plugin Plugin Plugin
```

Đây là nền tảng để sau này chúng ta có thể xây:

> **Plugin Parser Framework**

---

# 37. Factory không phải phép thuật

Một sai lầm phổ biến:

```text
Có nhiều class
    ↓
Dùng Factory
```

Không phải.

Factory nên xuất hiện khi:

```text
Object creation
      ↓
có variation
      hoặc
creation phức tạp
      hoặc
runtime decision
      hoặc
cần decouple client
```

Nếu không có những vấn đề này:

```python
obj = MyClass()
```

vẫn là lựa chọn tốt nhất.

---

# 38. Quy tắc thực tế

Bạn có thể sử dụng quy tắc:

### Không cần Factory

```python
user = User()
```

### Có thể dùng Factory

```python
parser = create_parser(site)
```

### Factory rất hữu ích

```text
Runtime configuration
+
many implementations
+
plugin system
+
polymorphism
```

---

# 39. Kiến trúc chúng ta đang xây

Hãy nối tất cả kiến thức từ SOLID:

```text
                    Composition Root
                           │
                     ParserFactory
                           │
             ┌─────────────┼─────────────┐
             ↓             ↓             ↓
        SiteAParser   SiteBParser   SiteCParser
             │             │             │
             └─────────────┼─────────────┘
                           ↓
                      StoryParser
                           ↓
                        Crawler
```

Trong đó:

```text
SRP
 ↓
Factory có trách nhiệm tạo object

OCP
 ↓
Có thể thêm parser

LSP
 ↓
Parser phải substitutable

ISP
 ↓
Interface parser nhỏ

DIP
 ↓
Crawler phụ thuộc abstraction

DI
 ↓
Parser được inject vào Crawler
```

Đây chính là lúc **SOLID bắt đầu biến thành architecture thực tế**.

---

# 40. Bài tập

## Bài 1 — Simple Factory

Tạo:

```text
Dog
Cat
Bird
```

và:

```python
AnimalFactory.create("dog")
AnimalFactory.create("cat")
AnimalFactory.create("bird")
```

Mỗi object có:

```python
speak()
```

---

## Bài 2 — Payment Factory

Tạo:

```text
PayPal
Stripe
MoMo
```

Interface:

```python
class PaymentGateway:
    def pay(self, amount):
        ...
```

Factory:

```python
gateway = PaymentFactory.create("stripe")
```

---

## Bài 3 — Parser Factory

Tạo:

```text
SiteAParser
SiteBParser
SiteCParser
```

Factory:

```python
parser = ParserFactory.create("site_a")
```

Tất cả phải có:

```python
parse(html)
```

---

# 41. Bài tập nâng cao ⭐

Xây dựng:

```text
ParserFactory
```

với API:

```python
ParserFactory.register(
    "site_a",
    SiteAParser
)

ParserFactory.register(
    "site_b",
    SiteBParser
)
```

và:

```python
parser = ParserFactory.create("site_a")
```

Yêu cầu:

### 1. Không có `if/elif` trong `create()`

### 2. Không sửa Factory khi thêm parser

### 3. Parser phải tuân thủ abstraction

### 4. Unknown parser phải raise exception

### 5. Viết unit test

### 6. Crawler nhận parser bằng DI

Kiến trúc:

```text
ParserFactory
      │
      ├── register("site_a")
      ├── register("site_b")
      └── register("site_c")
                │
                ↓
             Parser
                │
                ↓
             Crawler
```

---

# 42. Bài tập kiến trúc ⭐⭐⭐

Thiết kế:

```text
Crawler Application
```

với:

```text
Site
 ├── Parser
 ├── Repository
 └── HttpClient
```

Ví dụ:

```text
Site A
 ├── SiteAParser
 ├── SQLiteStoryRepository
 └── HttpxClient

Site B
 ├── SiteBParser
 ├── SQLiteStoryRepository
 └── HttpxClient
```

Tạo:

```python
SiteFactory.create("site_a")
```

trả về một **object chứa cả bộ dependencies tương ứng**.

Mục tiêu:

```text
SiteFactory
     │
     ├── Site A
     │    ├── Parser
     │    ├── Repository
     │    └── HttpClient
     │
     └── Site B
          ├── Parser
          ├── Repository
          └── HttpClient
```

Đây là bước chuẩn bị rất tốt cho **Abstract Factory** và **Plugin Architecture**.

---

# 43. Tổng kết

Factory giải quyết một vấn đề rất cụ thể:

> **Tách việc tạo object khỏi nơi sử dụng object.**

Chuỗi tư duy:

```text
if/elif tạo object
       ↓
Simple Factory
       ↓
Registry Factory
       ↓
Plugin Architecture
```

Kết hợp với SOLID:

```text
Factory
   +
Polymorphism
   +
OCP
   +
DIP
   +
DI
```

Trong project crawler của bạn, một kiến trúc rất tự nhiên là:

```text
                    Composition Root
                           │
                           ↓
                    ParserFactory
                           │
              ┌────────────┼────────────┐
              ↓            ↓            ↓
         SiteAParser  SiteBParser  SiteCParser
              │            │            │
              └────────────┼────────────┘
                           ↓
                      StoryParser
                           ↓
                        Crawler
```

### Câu cần nhớ

> **Factory quyết định “tạo object nào”, còn Dependency Injection quyết định “đưa object đó vào đâu”.**

---

## Buổi tiếp theo — **Buổi 34: Builder Pattern**

Chúng ta sẽ xử lý một vấn đề khác:

```python
Story(
    title,
    author,
    source,
    category,
    description,
    cover,
    status,
    chapters,
    metadata,
    ...
)
```

Constructor quá nhiều tham số sẽ trở nên khó đọc và khó sử dụng.

Builder sẽ giúp chuyển thành:

```python
story = (
    StoryBuilder()
    .title("...")
    .author("...")
    .category("...")
    .status("ongoing")
    .build()
)
```

và chúng ta sẽ phân tích **khi nào Builder thực sự đáng dùng trong Python**, vì Python có `dataclass`, keyword arguments và factory nên không phải lúc nào cũng cần Builder.
