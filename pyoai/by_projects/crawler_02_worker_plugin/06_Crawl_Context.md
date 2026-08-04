Đúng rồi. Roadmap ban đầu của chúng ta là:

> **Buổi 6. Crawl Context**
> **Buổi 7. Request Client**
> **Buổi 8. Parser Engine**

Tôi đã đi nhầm thứ tự khi đưa `Request Client` lên trước. Thực tế, trong kiến trúc framework chuyên nghiệp thì **CrawlContext phải được xây dựng trước**, vì nó là **Dependency Container** của toàn bộ framework.

Đây mới là thứ tự hợp lý:

```
Plugin
    │
    ▼
CrawlContext
    │
    ├── HttpClient
    ├── ParserEngine
    ├── Repository
    ├── Logger
    ├── Settings
    ├── EventBus
    └── Cache
```

---

# Buổi 6 — Xây dựng Crawl Context

## Mục tiêu

Sau buổi này chúng ta sẽ có một **Context Object** quản lý toàn bộ dependency của framework.

Plugin sẽ không còn:

```python
client = RequestsHttpClient()

repo = BookRepository()

logger = Logger()
```

mà chỉ còn:

```python
plugin = NovelBinPlugin(context)
```

mọi thứ đều lấy từ `context`.

---

# 1. CrawlContext là gì?

Có thể xem nó như **Backpack (ba lô)** mà Worker đưa cho Plugin.

Trong ba lô có:

```
HttpClient

ParserEngine

Repository

Logger

Settings

Cache

EventBus

Clock

...
```

Plugin muốn dùng gì thì lấy từ Context.

---

# 2. Vì sao cần CrawlContext?

Nếu không có Context:

```python
class NovelPlugin:

    def __init__(self):

        self.http = RequestsHttpClient()

        self.parser = ParserEngine()

        self.repo = BookRepository()

        self.logger = Logger()

        self.cache = Cache()
```

Plugin sẽ:

* phụ thuộc vào implementation
* khó test
* khó thay thế
* khó mock

---

Có Context:

```python
class NovelPlugin:

    def __init__(self, context):

        self.context = context
```

Sau đó:

```python
response = self.context.http.get(url)

book = self.context.parsers.book.parse(response)

self.context.logger.info(...)
```

---

# 3. Kiến trúc

```
crawler/

core/

context/

    __init__.py

    context.py

    settings.py

    service_container.py
```

---

# 4. Thiết kế CrawlContext

```python
from dataclasses import dataclass

@dataclass(slots=True)
class CrawlContext:

    http: HttpClient

    parser_engine: ParserEngine

    repository: Repository

    logger: Logger

    settings: Settings
```

Đây là phiên bản đầu tiên.

---

# 5. Dependency Injection

Worker tạo Context.

```
Worker

↓

Context

↓

Plugin
```

Ví dụ:

```python
context = CrawlContext(

    http=http,

    parser_engine=parser,

    repository=repo,

    logger=logger,

    settings=settings
)
```

Plugin:

```python
plugin = NovelBinPlugin(context)
```

---

# 6. Không tạo object trong Plugin

Sai:

```python
class Plugin:

    def __init__(self):

        self.client = RequestsHttpClient()
```

Đúng:

```python
class Plugin:

    def __init__(self, context):

        self.context = context
```

Đây là nguyên tắc cực kỳ quan trọng.

---

# 7. Settings

Tạo:

```python
@dataclass(slots=True)
class Settings:

    timeout: int = 20

    retry: int = 3

    user_agent: str = "Crawler"

    verify_ssl: bool = True
```

Plugin:

```python
timeout = self.context.settings.timeout
```

---

# 8. Logger

Plugin:

```python
self.context.logger.info(
    "Fetch book"
)
```

Không cần import logging.

---

# 9. Cache

Sau này:

```python
html = self.context.cache.get(url)
```

Nếu không có:

```python
response = self.context.http.get(url)
```

Plugin không cần biết cache nằm ở đâu.

---

# 10. Event Bus

Sau này Worker có thể lắng nghe:

```
BookFound

ChapterFound

ImageFound

ErrorOccurred
```

Plugin:

```python
self.context.events.emit(
    BookFound(book)
)
```

Worker tự xử lý.

---

# 11. Service Container

Nếu Context ngày càng lớn:

```
context

↓

20 thuộc tính
```

không đẹp.

Ta tạo ServiceContainer.

```python
class ServiceContainer:

    def register(name, service)

    def get(name)
```

Ví dụ:

```python
context.services.get("http")
```

hoặc

```python
context.http
```

đều được.

---

# 12. Mock Context

Đây là thứ dùng rất nhiều khi test.

```python
context = CrawlContext(

    http=MockHttpClient(),

    parser_engine=MockParser(),

    repository=MockRepository(),

    logger=MockLogger(),

    settings=Settings()
)
```

Plugin không biết đây là Mock.

---

# 13. CLI kiểm thử

## Kiểm tra Context

```bash
crawler dev context show
```

Output

```
HttpClient

RequestsHttpClient

Parser

ParserEngine

Repository

SQLiteRepository

Logger

StandardLogger
```

---

## Kiểm tra Settings

```bash
crawler dev context settings
```

Output

```
timeout = 20

retry = 3

verify_ssl = True
```

---

## Kiểm tra Service

```bash
crawler dev context services
```

Output

```
http

parser

repository

logger

settings
```

---

## Test Mock Context

```bash
crawler dev context mock
```

Output

```
HttpClient -> MockHttpClient

Repository -> MockRepository

PASS
```

---

# 14. Unit Test

```python
def test_context():

    context = CrawlContext(...)

    assert context.http is not None
```

Kiểm tra Settings:

```python
def test_settings():

    settings = Settings()

    assert settings.timeout == 20
```

---

# 15. Kiến trúc sau Buổi 6

```
context/

    context.py

    settings.py

    service_container.py
```

```
Worker

↓

Context

↓

Plugin

↓

HttpClient

↓

ParserEngine

↓

Repository
```

---

# Một cải tiến mà tôi khuyên áp dụng

Đây là điểm tôi muốn cải tiến so với roadmap ban đầu.

Thay vì để `CrawlContext` chỉ là một `dataclass`, hãy thiết kế nó như **Application Context**, tương tự cách các framework lớn (Flask, FastAPI, Django, Scrapy) quản lý dịch vụ.

Ví dụ:

```python
context.http
context.parser
context.repository
context.logger
context.settings
```

được truy cập như thuộc tính, nhưng bên trong đều lấy từ **ServiceContainer**.

```python
class CrawlContext:
    @property
    def http(self):
        return self.services.get(HttpClient)

    @property
    def repository(self):
        return self.services.get(BookRepository)
```

Ưu điểm:

* Không phải sửa `CrawlContext` mỗi khi thêm một service mới.
* Có thể thay thế `HttpClient`, `Repository` hay `Logger` bằng mock hoặc implementation khác chỉ bằng cách đăng ký lại trong `ServiceContainer`.
* Plugin và Worker chỉ phụ thuộc vào abstraction, không phụ thuộc implementation.

Với cách này, **Buổi 7 (Request Client)** sẽ chỉ cần đăng ký `RequestsHttpClient` vào `CrawlContext`, và toàn bộ plugin sẽ sử dụng được ngay mà không cần sửa constructor của plugin hay worker. Đây là kiến trúc linh hoạt hơn và rất phù hợp với mục tiêu xây dựng một framework crawler có khả năng mở rộng lâu dài.
