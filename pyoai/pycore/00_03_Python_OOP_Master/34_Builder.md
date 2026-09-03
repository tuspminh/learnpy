# Python OOP Master — Buổi 34

# Builder Pattern

Sau **Singleton** và **Factory**, hôm nay chúng ta học **Builder Pattern**.

Builder giải quyết một vấn đề rất quen thuộc trong OOP:

> **Object có quá nhiều tham số hoặc quá trình khởi tạo phức tạp.**

Ví dụ trong project đọc truyện của bạn, một `Story` có thể có:

```text
Story
├── title
├── author
├── description
├── cover_url
├── source
├── category
├── status
├── chapters
├── tags
└── metadata
```

Nếu constructor trở thành:

```python
Story(
    title,
    author,
    description,
    cover_url,
    source,
    category,
    status,
    chapters,
    tags,
    metadata,
)
```

thì code bắt đầu khó đọc.

Builder sẽ giúp chúng ta giải quyết vấn đề này.

---

# 1. Mục tiêu

Sau buổi này bạn sẽ hiểu:

* Builder Pattern là gì?
* Vì sao cần Builder?
* Telescoping Constructor là gì?
* Builder cơ bản
* Fluent Interface
* Method Chaining
* Immutable Object + Builder
* Builder với `dataclass`
* Builder vs Factory
* Builder vs Constructor
* Builder vs keyword arguments
* Director
* Builder trong crawler
* Khi nào **không nên** dùng Builder

---

# 2. Builder Pattern là gì?

Builder Pattern tách:

```text
quá trình xây dựng object
```

khỏi:

```text
object cuối cùng
```

Thay vì:

```python
story = Story(
    title,
    author,
    description,
    cover,
    source,
    category,
)
```

ta có:

```python
story = (
    StoryBuilder()
    .title("Kiếm Lai")
    .author("...")
    .category("Tiên hiệp")
    .source("Site A")
    .build()
)
```

Luồng:

```text
Builder
   │
   ├── title()
   ├── author()
   ├── category()
   ├── source()
   └── build()
          ↓
       Story
```

---

# 3. Vấn đề: Constructor quá nhiều tham số

Ví dụ:

```python
class Story:

    def __init__(
        self,
        title,
        author,
        description,
        cover_url,
        source,
        category,
        status,
        chapters,
    ):
        ...
```

Sử dụng:

```python
story = Story(
    "Story A",
    "Author A",
    "Description",
    "cover.jpg",
    "Site A",
    "Fantasy",
    "ongoing",
    [],
)
```

Vấn đề:

```text
"Description"
"cover.jpg"
"Site A"
"Fantasy"
"ongoing"
```

Nhìn vào rất khó biết argument nào tương ứng với parameter nào.

---

# 4. Keyword arguments đã cải thiện rất nhiều

Python có một giải pháp đơn giản:

```python
story = Story(
    title="Story A",
    author="Author A",
    description="Description",
    cover_url="cover.jpg",
    source="Site A",
    category="Fantasy",
    status="ongoing",
    chapters=[],
)
```

Tốt hơn rất nhiều.

Vì vậy:

> Trong Python, **đừng vội dùng Builder chỉ vì constructor có nhiều parameter.**

Nếu keyword arguments đã đủ rõ ràng thì Builder có thể là overengineering.

---

# 5. Telescoping Constructor

Một vấn đề khác:

```python
class User:

    def __init__(
        self,
        name,
        email=None,
        age=None,
        phone=None,
        address=None,
        avatar=None,
    ):
        ...
```

Khi optional parameters tăng:

```text
name
email
age
phone
address
avatar
...
```

constructor ngày càng lớn.

Builder có thể làm API rõ ràng hơn:

```python
user = (
    UserBuilder()
    .name("Minh")
    .email("minh@example.com")
    .age(30)
    .phone("...")
    .build()
)
```

---

# 6. Builder cơ bản

Ta bắt đầu đơn giản.

```python
class User:

    def __init__(
        self,
        name,
        email=None,
        age=None,
    ):
        self.name = name
        self.email = email
        self.age = age
```

Builder:

```python
class UserBuilder:

    def __init__(self):
        self._name = None
        self._email = None
        self._age = None

    def name(self, value):
        self._name = value
        return self

    def email(self, value):
        self._email = value
        return self

    def age(self, value):
        self._age = value
        return self

    def build(self):
        return User(
            name=self._name,
            email=self._email,
            age=self._age,
        )
```

Sử dụng:

```python
user = (
    UserBuilder()
    .name("Minh")
    .email("minh@example.com")
    .age(30)
    .build()
)
```

---

# 7. Tại sao `return self`?

Đây là kỹ thuật:

> **Method Chaining**

Ví dụ:

```python
builder.name("Minh")
```

trả về:

```python
builder
```

nên có thể tiếp tục:

```python
builder.name("Minh").email("...")
```

Rồi:

```python
builder.name("Minh").email("...").age(30)
```

Cuối cùng:

```python
.build()
```

---

# 8. Fluent Interface

Builder thường sử dụng **Fluent Interface**.

Code:

```python
user = (
    UserBuilder()
    .name("Minh")
    .email("minh@example.com")
    .age(30)
    .build()
)
```

đọc gần giống:

```text
Tạo UserBuilder
    ↓
đặt name
    ↓
đặt email
    ↓
đặt age
    ↓
build
```

Đây là lý do Builder rất dễ đọc khi object có nhiều configuration.

---

# 9. Thêm validation

Builder là nơi rất thích hợp để validate dữ liệu xây dựng object.

```python
class UserBuilder:

    def __init__(self):
        self._name = None
        self._email = None
        self._age = None

    def name(self, value):
        self._name = value
        return self

    def email(self, value):
        self._email = value
        return self

    def age(self, value):
        self._age = value
        return self

    def build(self):

        if not self._name:
            raise ValueError(
                "name is required"
            )

        if self._age is not None and self._age < 0:
            raise ValueError(
                "age must be >= 0"
            )

        return User(
            name=self._name,
            email=self._email,
            age=self._age,
        )
```

Bây giờ:

```python
user = UserBuilder().build()
```

sẽ lỗi:

```text
ValueError: name is required
```

---

# 10. Builder giúp enforce invariant

Đây là điểm rất quan trọng nếu bạn đã học DDD.

Giả sử:

```text
Story
```

phải luôn có:

```text
title
source
```

Ta không muốn tạo:

```python
Story(
    title="",
    source=None,
)
```

Builder có thể enforce:

```python
def build(self):

    if not self._title:
        raise ValueError("title required")

    if not self._source:
        raise ValueError("source required")

    return Story(
        title=self._title,
        source=self._source,
    )
```

Builder lúc này không chỉ làm code đẹp hơn.

Nó còn giúp bảo vệ **object invariant**.

---

# 11. Builder cho Story

Hãy áp dụng vào project crawler.

```python
class Story:

    def __init__(
        self,
        title,
        author,
        description,
        cover_url,
        source,
        category,
        status,
        chapters,
    ):
        self.title = title
        self.author = author
        self.description = description
        self.cover_url = cover_url
        self.source = source
        self.category = category
        self.status = status
        self.chapters = chapters
```

Builder:

```python
class StoryBuilder:

    def __init__(self):
        self._title = None
        self._author = None
        self._description = None
        self._cover_url = None
        self._source = None
        self._category = None
        self._status = None
        self._chapters = []

    def title(self, value):
        self._title = value
        return self

    def author(self, value):
        self._author = value
        return self

    def description(self, value):
        self._description = value
        return self

    def cover_url(self, value):
        self._cover_url = value
        return self

    def source(self, value):
        self._source = value
        return self

    def category(self, value):
        self._category = value
        return self

    def status(self, value):
        self._status = value
        return self

    def chapters(self, value):
        self._chapters = value
        return self

    def build(self):

        if not self._title:
            raise ValueError("title is required")

        if not self._source:
            raise ValueError("source is required")

        return Story(
            title=self._title,
            author=self._author,
            description=self._description,
            cover_url=self._cover_url,
            source=self._source,
            category=self._category,
            status=self._status,
            chapters=self._chapters,
        )
```

Sử dụng:

```python
story = (
    StoryBuilder()
    .title("Story A")
    .author("Author A")
    .description("...")
    .cover_url("...")
    .source("Site A")
    .category("Fantasy")
    .status("ongoing")
    .chapters([])
    .build()
)
```

---

# 12. Builder đặc biệt hữu ích với optional fields

Ví dụ:

```text
Required
├── title
└── source

Optional
├── author
├── description
├── cover
├── category
├── status
└── tags
```

Ta có:

```python
story = (
    StoryBuilder()
    .title("Story A")
    .source("Site A")
    .author("Author A")
    .category("Fantasy")
    .build()
)
```

Không cần:

```python
story = Story(
    "Story A",
    None,
    None,
    None,
    "Site A",
    "Fantasy",
    None,
    None,
)
```

---

# 13. Builder với `dataclass`

Python hiện đại thường dùng:

```python
from dataclasses import dataclass, field


@dataclass
class Story:

    title: str
    source: str
    author: str | None = None
    description: str | None = None
    cover_url: str | None = None
    category: str | None = None
    status: str | None = None
    chapters: list = field(
        default_factory=list
    )
```

Lúc này:

```python
story = Story(
    title="Story A",
    source="Site A",
    author="Author A",
)
```

đã rất sạch.

Do đó:

> `dataclass` thường làm giảm nhu cầu sử dụng Builder trong Python.

---

# 14. Vậy tại sao vẫn học Builder?

Vì Builder vẫn hữu ích khi **quá trình tạo object phức tạp**.

Ví dụ:

```text
Story
 ├── metadata
 ├── chapters
 ├── tags
 ├── validation
 ├── normalization
 ├── defaults
 └── derived values
```

Hoặc:

```text
CrawlerConfig
 ├── HTTP config
 ├── retry policy
 ├── concurrency
 ├── timeout
 ├── proxy
 ├── headers
 ├── parser
 └── storage
```

Builder có thể làm API configuration dễ sử dụng hơn.

---

# 15. Builder vs Factory

Đây là phần bắt buộc phải phân biệt.

### Factory

Trả lời:

> **Tạo loại object nào?**

Ví dụ:

```python
parser = ParserFactory.create("site_a")
```

Factory quyết định:

```text
site_a
   ↓
SiteAParser
```

### Builder

Trả lời:

> **Xây dựng object này như thế nào?**

Ví dụ:

```python
story = (
    StoryBuilder()
    .title("...")
    .author("...")
    .category("...")
    .build()
)
```

Builder quyết định:

```text
title
 ↓
author
 ↓
category
 ↓
build
 ↓
Story
```

---

# 16. Factory + Builder

Hai pattern có thể kết hợp.

Ví dụ:

```text
Factory
   ↓
chọn Builder
   ↓
Builder
   ↓
xây object
```

Ví dụ:

```python
builder = StoryBuilderFactory.create("site_a")

story = (
    builder
    .title("Story A")
    .author("Author A")
    .build()
)
```

Factory:

```text
site_a → SiteAStoryBuilder
site_b → SiteBStoryBuilder
```

Builder:

```text
SiteAStoryBuilder
       ↓
    Story
```

---

# 17. Builder vs Constructor

Constructor:

```python
story = Story(
    title="A",
    source="B",
    author="C",
)
```

Builder:

```python
story = (
    StoryBuilder()
    .title("A")
    .source("B")
    .author("C")
    .build()
)
```

Nếu object đơn giản:

```python
Story(...)
```

thường tốt hơn.

Nếu construction phức tạp:

```python
StoryBuilder()
```

có thể đáng giá.

---

# 18. Builder vs `**kwargs`

Một số người sẽ viết:

```python
Story(**data)
```

Ví dụ:

```python
data = {
    "title": "Story A",
    "source": "Site A",
    "author": "Author A",
}
```

Điều này rất phù hợp khi dữ liệu đến từ crawler:

```text
HTML
 ↓
Parser
 ↓
dict
 ↓
Story(**data)
```

Không nhất thiết cần Builder.

Builder phù hợp hơn khi:

```text
construction logic
+
validation
+
defaults
+
multiple steps
```

phức tạp.

---

# 19. Builder cho CrawlerConfig

Đây là một ví dụ thực tế hơn.

```python
class CrawlerConfig:

    def __init__(
        self,
        timeout,
        max_workers,
        retries,
        user_agent,
        proxy,
    ):
        self.timeout = timeout
        self.max_workers = max_workers
        self.retries = retries
        self.user_agent = user_agent
        self.proxy = proxy
```

Builder:

```python
class CrawlerConfigBuilder:

    def __init__(self):
        self._timeout = 30
        self._max_workers = 5
        self._retries = 3
        self._user_agent = None
        self._proxy = None

    def timeout(self, value):
        self._timeout = value
        return self

    def max_workers(self, value):
        self._max_workers = value
        return self

    def retries(self, value):
        self._retries = value
        return self

    def user_agent(self, value):
        self._user_agent = value
        return self

    def proxy(self, value):
        self._proxy = value
        return self

    def build(self):

        if self._timeout <= 0:
            raise ValueError(
                "timeout must be > 0"
            )

        if self._max_workers <= 0:
            raise ValueError(
                "max_workers must be > 0"
            )

        if self._retries < 0:
            raise ValueError(
                "retries must be >= 0"
            )

        return CrawlerConfig(
            timeout=self._timeout,
            max_workers=self._max_workers,
            retries=self._retries,
            user_agent=self._user_agent,
            proxy=self._proxy,
        )
```

Sử dụng:

```python
config = (
    CrawlerConfigBuilder()
    .timeout(10)
    .max_workers(20)
    .retries(5)
    .user_agent("MyCrawler/1.0")
    .build()
)
```

Đây là trường hợp Builder hợp lý hơn nhiều.

---

# 20. Immutable Object + Builder

Builder đặc biệt hữu ích khi object cuối cùng nên **immutable**.

Ví dụ:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class CrawlerConfig:

    timeout: int
    max_workers: int
    retries: int
```

Builder:

```python
class CrawlerConfigBuilder:

    def __init__(self):
        self._timeout = 30
        self._max_workers = 5
        self._retries = 3

    def timeout(self, value):
        self._timeout = value
        return self

    def max_workers(self, value):
        self._max_workers = value
        return self

    def retries(self, value):
        self._retries = value
        return self

    def build(self):
        return CrawlerConfig(
            timeout=self._timeout,
            max_workers=self._max_workers,
            retries=self._retries,
        )
```

Sau:

```python
config = (
    CrawlerConfigBuilder()
    .timeout(10)
    .max_workers(20)
    .build()
)
```

`config` không thể tùy tiện thay đổi:

```python
config.timeout = 100
```

sẽ lỗi.

---

# 21. Director

Trong Builder Pattern kinh điển còn có:

> **Director**

Director quyết định **trình tự xây dựng**.

Ví dụ:

```python
class Director:

    def __init__(self, builder):
        self.builder = builder

    def build_default(self):

        return (
            self.builder
            .title("Default Story")
            .source("Unknown")
            .status("unknown")
            .build()
        )
```

Sử dụng:

```python
builder = StoryBuilder()

director = Director(builder)

story = director.build_default()
```

Flow:

```text
Director
   │
   ↓
Builder
   │
   ├── title()
   ├── source()
   ├── status()
   └── build()
          ↓
        Story
```

---

# 22. Có cần Director trong Python?

Thông thường:

> **Không nhất thiết.**

Python có syntax rất linh hoạt:

```python
story = (
    StoryBuilder()
    .title("A")
    .source("B")
    .author("C")
    .build()
)
```

Director chỉ đáng dùng khi:

* có nhiều quy trình build cố định
* workflow phức tạp
* nhiều loại configuration preset
* muốn tái sử dụng construction sequence

---

# 23. Builder với preset

Một trường hợp Director hữu ích:

```text
Development
Production
Testing
```

Ví dụ:

```python
class CrawlerConfigDirector:

    @staticmethod
    def development():

        return (
            CrawlerConfigBuilder()
            .timeout(30)
            .max_workers(2)
            .retries(1)
            .build()
        )

    @staticmethod
    def production():

        return (
            CrawlerConfigBuilder()
            .timeout(10)
            .max_workers(20)
            .retries(5)
            .build()
        )
```

Sử dụng:

```python
config = CrawlerConfigDirector.production()
```

---

# 24. Builder và Dependency Injection

Builder tạo object:

```python
config = (
    CrawlerConfigBuilder()
    .timeout(10)
    .max_workers(20)
    .build()
)
```

Sau đó DI:

```python
crawler = Crawler(
    config=config,
    client=client,
    parser=parser,
    repository=repository,
)
```

Luồng:

```text
Builder
   ↓
Configuration
   ↓
Composition Root
   ↓
Dependency Injection
   ↓
Crawler
```

Đây là kiến trúc rất đẹp.

---

# 25. Builder + Factory + DI

Bây giờ kết hợp ba pattern:

```text
                  Composition Root
                         │
             ┌───────────┼───────────┐
             ↓           ↓           ↓
          Factory      Builder       ...
             │           │
             ↓           ↓
          Parser       Config
             │           │
             └─────┬─────┘
                   ↓
                 Crawler
```

Ví dụ:

```python
parser = ParserFactory.create("site_a")

config = (
    CrawlerConfigBuilder()
    .timeout(10)
    .max_workers(20)
    .retries(5)
    .build()
)

crawler = Crawler(
    parser=parser,
    config=config,
)
```

Rất phù hợp với tư duy Clean Architecture mà bạn đang học.

---

# 26. Builder và SOLID

### SRP

Builder chịu trách nhiệm construction.

Object chịu trách nhiệm behavior.

### OCP

Có thể thêm Builder mới cho các loại construction khác.

### DIP

Builder có thể nhận dependencies:

```python
Builder(repository)
```

thay vì tự tạo repository.

### LSP

Nếu có `AbstractBuilder`, implementation phải tuân thủ contract.

Nhưng không nên tạo abstraction chỉ để "cho đủ SOLID".

---

# 27. Một Builder không tốt

Đừng viết Builder như thế này:

```python
class UserBuilder:

    def __init__(self):
        self.user = User()

    def set_name(self, name):
        self.user.name = name
        return self

    def set_email(self, email):
        self.user.email = email
        return self

    def build(self):
        return self.user
```

Vấn đề:

```text
Builder
   ↓
mutable User
   ↓
User bị thay đổi trong quá trình build
```

Tốt hơn là Builder giữ state riêng:

```text
Builder state
    ↓
build()
    ↓
final object
```

---

# 28. Builder nên là temporary object

Tư duy:

```text
Builder
   ↓
configuration state
   ↓
build()
   ↓
final object
```

Builder không phải domain object.

Ví dụ:

```text
StoryBuilder ≠ Story
```

Builder chỉ là công cụ để tạo:

```text
Story
```

---

# 29. Builder với Collection

Ví dụ Story có nhiều chapters.

Thay vì:

```python
builder.chapters(chapters)
```

ta có thể:

```python
class StoryBuilder:

    def __init__(self):
        self._chapters = []

    def add_chapter(self, chapter):
        self._chapters.append(chapter)
        return self
```

Sử dụng:

```python
story = (
    StoryBuilder()
    .title("Story A")
    .source("Site A")
    .add_chapter(chapter1)
    .add_chapter(chapter2)
    .add_chapter(chapter3)
    .build()
)
```

Rất dễ đọc.

---

# 30. Builder trong crawler pipeline

Giả sử Parser trả về dữ liệu từng phần:

```text
HTML
 ↓
Parser
 ↓
title
author
description
cover
chapters
tags
 ↓
StoryBuilder
 ↓
Story
```

Ví dụ:

```python
builder = (
    StoryBuilder()
    .title(parser.title(html))
    .author(parser.author(html))
    .description(parser.description(html))
)
```

Sau đó:

```python
for chapter in parser.chapters(html):
    builder.add_chapter(chapter)

story = builder.build()
```

Đây là trường hợp Builder khá tự nhiên.

---

# 31. Builder và Parsing

Có thể thiết kế:

```python
def parse_story(html):

    builder = StoryBuilder()

    builder.title(extract_title(html))
    builder.author(extract_author(html))
    builder.description(extract_description(html))

    for chapter in extract_chapters(html):
        builder.add_chapter(chapter)

    return builder.build()
```

Pipeline:

```text
HTML
 ↓
Extraction
 ↓
Builder
 ↓
Validation
 ↓
Story
```

Điểm hay:

> Parser tập trung extraction, Builder tập trung construction/invariant.

Nếu thiết kế cẩn thận, trách nhiệm được tách khá rõ.

---

# 32. Builder không phải luôn tốt

Ví dụ object:

```python
@dataclass
class User:
    name: str
    age: int
```

Builder:

```python
UserBuilder().name("Minh").age(30).build()
```

là quá nhiều ceremony.

Chỉ cần:

```python
User(
    name="Minh",
    age=30,
)
```

Do đó:

> **Builder không phải “cách tạo object chuyên nghiệp hơn”.**

Nó chỉ là một công cụ giải quyết một loại vấn đề cụ thể.

---

# 33. Khi nào nên dùng Builder?

### Nên cân nhắc khi:

```text
Nhiều optional fields
        +
construction phức tạp
        +
validation
        +
nhiều bước
        +
object cần immutable
```

Ví dụ:

```text
CrawlerConfig
HTTPRequestConfig
Report
Query
Complex Domain Object
```

---

# 34. Khi nào không nên dùng?

Không nên:

```python
UserBuilder()
```

cho:

```python
User(name="Minh")
```

Không nên tạo Builder chỉ vì:

```text
"Design Pattern phải được sử dụng."
```

Đây là một trong những lỗi phổ biến khi mới học Design Pattern.

---

# 35. So sánh tổng hợp

| Cách              | Khi phù hợp                              |
| ----------------- | ---------------------------------------- |
| Constructor       | Object đơn giản                          |
| Keyword arguments | Nhiều fields nhưng construction đơn giản |
| `dataclass`       | Data-centric object                      |
| Factory           | Chọn loại object                         |
| Builder           | Construction phức tạp/nhiều bước         |
| Factory + Builder | Chọn builder rồi xây object              |

---

# 36. Factory vs Builder — nhớ bằng câu hỏi

Khi gặp bài toán:

### Câu hỏi 1

> Tôi cần tạo **loại object nào**?

→ **Factory**

```python
ParserFactory.create("site_a")
```

### Câu hỏi 2

> Tôi đã biết object cần tạo, nhưng nó cần **xây dựng như thế nào**?

→ **Builder**

```python
(
    StoryBuilder()
    .title(...)
    .author(...)
    .add_chapter(...)
    .build()
)
```

---

# 37. Bài tập 1 — UserBuilder

Tạo:

```python
UserBuilder()
```

API:

```python
user = (
    UserBuilder()
    .name("Minh")
    .email("minh@example.com")
    .age(30)
    .phone("0123")
    .build()
)
```

Yêu cầu:

* `name` bắt buộc
* `email` optional
* `age` optional
* `age >= 0`
* `build()` trả về `User`

---

# 38. Bài tập 2 — HTTP Request Builder

Tạo:

```python
HttpRequestBuilder()
```

API:

```python
request = (
    HttpRequestBuilder()
    .url("https://example.com")
    .method("GET")
    .header("User-Agent", "Crawler")
    .header("Accept", "text/html")
    .timeout(10)
    .build()
)
```

Object:

```text
HttpRequest
├── url
├── method
├── headers
└── timeout
```

Đây là bài rất phù hợp với kiến thức **HTTPX** bạn đã học.

---

# 39. Bài tập 3 — StoryBuilder

Tạo:

```python
story = (
    StoryBuilder()
    .title("Story A")
    .author("Author A")
    .source("Site A")
    .category("Fantasy")
    .add_chapter(chapter1)
    .add_chapter(chapter2)
    .add_chapter(chapter3)
    .build()
)
```

Yêu cầu:

```text
title   → required
source  → required
author  → optional
category → optional
chapters → 0..N
```

---

# 40. Bài tập nâng cao ⭐

Xây:

```text
CrawlerConfigBuilder
```

API:

```python
config = (
    CrawlerConfigBuilder()
    .timeout(10)
    .max_workers(20)
    .retries(5)
    .user_agent("MyCrawler")
    .proxy("...")
    .build()
)
```

Validation:

```text
timeout > 0
max_workers > 0
retries >= 0
```

Sau đó:

```python
crawler = Crawler(
    config=config,
    client=client,
    parser=parser,
    repository=repository,
)
```

Mục tiêu:

```text
Builder
   ↓
Config
   ↓
DI
   ↓
Crawler
```

---

# 41. Bài tập kiến trúc ⭐⭐⭐

Kết hợp:

```text
Factory + Builder + DI
```

Thiết kế:

```text
CLI
 │
 ├── --site site_a
 ├── --workers 20
 ├── --timeout 10
 └── --retries 5
          │
          ↓
   Composition Root
          │
     ┌────┴────┐
     ↓         ↓
  Factory    Builder
     ↓         ↓
  Parser     Config
     │         │
     └────┬────┘
          ↓
        Crawler
```

Ví dụ mục tiêu:

```python
parser = ParserFactory.create(args.site)

config = (
    CrawlerConfigBuilder()
    .timeout(args.timeout)
    .max_workers(args.workers)
    .retries(args.retries)
    .build()
)

crawler = Crawler(
    parser=parser,
    config=config,
)
```

Đây là một kiến trúc rất tốt để bạn thực hành sau khi đã học:

```text
SOLID
+
Factory
+
Builder
+
DI
```

---

# 42. Tổng kết Buổi 34

Ba ý quan trọng nhất:

### 1. Factory

```text
"Tôi cần object loại nào?"
```

```python
ParserFactory.create("site_a")
```

### 2. Builder

```text
"Tôi xây object này như thế nào?"
```

```python
(
    StoryBuilder()
    .title(...)
    .author(...)
    .add_chapter(...)
    .build()
)
```

### 3. Python không phải Java

Trong Python, trước khi dùng Builder hãy xem xét:

```text
Constructor
     ↓
Keyword arguments
     ↓
dataclass
     ↓
Factory
     ↓
Builder
```

Chọn giải pháp **đơn giản nhất nhưng vẫn rõ ràng**.

---

# Design Pattern roadmap

Chúng ta đã hoàn thành:

```text
Buổi 32 — Singleton       ✅
Buổi 33 — Factory         ✅
Buổi 34 — Builder         ✅
```

Tiếp theo:

# **Buổi 35 — Strategy Pattern**

Đây sẽ là một Pattern cực kỳ quan trọng đối với kiến trúc crawler:

```text
Crawler
   │
   ├── RetryStrategy
   │     ├── FixedRetry
   │     ├── ExponentialBackoff
   │     └── NoRetry
   │
   ├── ParserStrategy
   │
   └── StorageStrategy
```

Chúng ta sẽ học cách **thay đổi thuật toán/behavior tại runtime mà không sửa class chính**, và kết nối trực tiếp với **OCP + DIP + DI**.
