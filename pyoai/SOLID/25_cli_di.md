# Buổi 25 — CLI + Dependency Injection

Hôm nay chúng ta hoàn thiện tầng **Presentation** của Story Crawler.

Mục tiêu:

```text
CLI
 ↓
Composition Root
 ↓
Application
 ↓
Domain
 ↓
Infrastructure
```

và đặc biệt hiểu sâu:

> **CLI không nên tự xây dependency của Application.**

---

# 1. Architecture

Sau Buổi 24:

```text
                    ┌─────────────┐
                    │     CLI     │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  CrawlStory │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
       CrawlerRegistry          StoryRepository
              │                         ▲
              ▼                         │
       SourceACrawler          SQLiteRepository
              │
       ┌──────┴──────┐
       ▼             ▼
   HttpClient      Parser
```

Nhưng CLI **không nên** trực tiếp biết toàn bộ cây dependency này.

---

# 2. Cách làm sai

Ví dụ:

```python
def crawl_command(url):

    connection = sqlite3.connect(
        "stories.db"
    )

    repository = SQLiteStoryRepository(
        connection
    )

    http = RequestsHttpClient()

    parser = SourceAStoryParser()

    crawler = SourceACrawler(
        http,
        parser,
    )

    registry = CrawlerRegistry()

    registry.register(crawler)

    use_case = CrawlStory(
        registry,
        repository,
    )

    story = use_case.execute(
        Url(url)
    )

    print(story.title)
```

Chạy được.

Nhưng CLI đang biết:

```text
SQLite
Requests
SourceA
Parser
Repository
Crawler
Use Case
```

Đây là coupling không cần thiết.

---

# 3. CLI nên biết gì?

CLI chỉ nên biết:

```text
command
arguments
options
output
error presentation
```

Ví dụ:

```bash
story-crawler crawl URL
```

CLI chuyển:

```text
URL
 ↓
Use Case
```

Nó không cần biết:

```text
SQLite
HTTPX
BeautifulSoup
Source A
```

---

# 4. Composition Root

Đây là nơi cực kỳ quan trọng.

Tạo:

```text
src/story_crawler/
├── presentation/
│   └── cli.py
│
├── application/
│   └── ...
│
├── domain/
│   └── ...
│
├── infrastructure/
│   └── ...
│
└── composition.py
```

`composition.py` chịu trách nhiệm:

> **Construct object graph.**

---

# 5. Object Graph

Ví dụ dependency:

```text
CrawlStory
├── CrawlerRegistry
│   └── SourceACrawler
│       ├── HttpClient
│       └── StoryParser
│
└── StoryRepository
    └── SQLiteStoryRepository
```

Composition Root sẽ xây toàn bộ:

```python
def build_application():
    ...
```

---

# 6. `build_application()`

```python
def build_application():

    connection = create_connection(
        "stories.db"
    )

    initialize_database(
        connection
    )

    repository = SQLiteStoryRepository(
        connection
    )

    http_client = RequestsHttpClient()

    parser = SourceAStoryParser()

    crawler = SourceACrawler(
        http_client=http_client,
        parser=parser,
    )

    registry = CrawlerRegistry()

    registry.register(crawler)

    return CrawlStory(
        registry=registry,
        repository=repository,
    )
```

Đây là **Composition Root**.

---

# 7. CLI bây giờ rất mỏng

```python
def crawl_command(url: str):

    app = build_application()

    story = app.execute(
        Url(url)
    )

    print(story.title)
```

CLI không biết:

```text
SQLite
Requests
Parser
Registry
```

---

# 8. Nhưng có một vấn đề

Nếu mỗi command đều:

```python
app = build_application()
```

thì:

```bash
story-crawler crawl ...
story-crawler list
story-crawler show ...
```

sẽ xây application nhiều lần.

Tốt hơn là CLI entrypoint xây application một lần.

---

# 9. Application Factory

Ta có:

```python
def build_application():
    ...
```

và CLI:

```python
def main():

    app = build_application()

    run_cli(app)
```

Sau đó:

```text
main()
 ↓
build_application()
 ↓
run_cli(app)
```

---

# 10. Với argparse

Ví dụ:

```python
import argparse


def create_parser():

    parser = argparse.ArgumentParser(
        prog="story-crawler"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    crawl = subparsers.add_parser(
        "crawl"
    )

    crawl.add_argument(
        "url"
    )

    return parser
```

---

# 11. CLI Handler

```python
def handle_crawl(args, app):

    story = app.execute(
        Url(args.url)
    )

    print(
        f"Crawled: {story.title}"
    )
```

Điểm quan trọng:

```text
handle_crawl()
```

nhận `app` từ bên ngoài.

Không tự tạo.

---

# 12. Dependency Injection

Ta có:

```python
def handle_crawl(args, app):
    ...
```

`app` là dependency được inject.

Đây là:

> **Dependency Injection**

Không phải:

```python
def handle_crawl(args):

    app = build_application()
```

---

# 13. Constructor Injection vs Function Injection

Trước đây:

```python
class CrawlStory:

    def __init__(
        self,
        repository,
        registry,
    ):
        ...
```

Đó là:

> Constructor Injection.

CLI:

```python
def handle_crawl(args, app):
```

là:

> Function/Method Injection.

Cả hai đều là Dependency Injection.

---

# 14. DI không đồng nghĩa với Framework

Bạn **không cần**:

```text
dependency-injector
injector
punq
```

để thực hiện Dependency Injection.

Python thuần đã đủ:

```python
service = Service(
    repository=repository
)
```

Đây là DI.

---

# 15. Composition Root nên là nơi duy nhất `new` infrastructure

Một nguyên tắc hữu ích:

```text
composition.py
```

có thể chứa:

```python
SQLiteStoryRepository(...)
RequestsHttpClient(...)
SourceACrawler(...)
```

Trong khi:

```text
domain/
application/
```

không nên tự tạo các implementation này.

---

# 16. Dependency Direction

Nhìn từ Application:

```text
Application
     ↓
Protocol
     ↑
Infrastructure
```

Nhìn từ Composition Root:

```text
Composition Root
      ↓
construct implementations
      ↓
inject
      ↓
Application
```

Composition Root có quyền biết tất cả.

Các tầng bên trong thì không.

---

# 17. Tại sao Composition Root có thể biết tất cả?

Vì nó là:

> **chỗ kết nối các thế giới lại với nhau.**

Ví dụ:

```text
Business world

CrawlStory
StoryRepository
StoryCrawler
```

và:

```text
Technical world

SQLite
Requests
BeautifulSoup
```

Composition Root:

```text
Business
   ↕
Composition Root
   ↕
Technical
```

---

# 18. Error Handling trong CLI

Infrastructure có thể ném:

```python
HttpTimeoutError
```

Crawler chuyển thành:

```python
CrawlerError
```

Application có thể để lỗi đi lên.

CLI xử lý:

```python
def handle_crawl(args, app):

    try:

        story = app.execute(
            Url(args.url)
        )

    except CrawlerError as exc:

        print(
            f"Error: {exc}"
        )

        return 1

    print(
        f"Crawled: {story.title}"
    )

    return 0
```

CLI chịu trách nhiệm:

> **presentation của error**

chứ không xử lý HTTP.

---

# 19. Exit Code

CLI production nên dùng exit code.

```python
return 0
```

thành công.

```python
return 1
```

thất bại.

Cuối cùng:

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

---

# 20. Đừng `print()` trong Application

Sai:

```python
class CrawlStory:

    def execute(self, url):

        story = ...

        print(
            "Crawl successful"
        )

        return story
```

Application không biết CLI tồn tại.

Đúng:

```python
class CrawlStory:

    def execute(self, url):

        return story
```

CLI:

```python
story = app.execute(url)

print(
    f"Crawled: {story.title}"
)
```

---

# 21. Tại sao?

Sau này bạn có thể có:

```text
CLI
PySide6
REST API
WebSocket
```

Tất cả đều dùng:

```text
CrawlStory
```

Nếu Application `print()`:

```text
PySide6
REST API
```

cũng bị kéo theo behavior CLI.

Không tốt.

---

# 22. CLI cũng không nên xử lý business rule

Sai:

```python
if url.endswith(".html"):
    ...
```

hoặc:

```python
if story.source == "source_a":
    ...
```

Business logic thuộc:

```text
Domain / Application
```

CLI chỉ:

```text
parse input
 ↓
call use case
 ↓
format output
```

---

# 23. Thiết kế CLI tốt

```text
CLI
│
├── Argument parsing
├── Input conversion
├── Output formatting
└── Error presentation
```

Không:

```text
HTTP
SQL
HTML parsing
business rules
```

---

# 24. Output Formatter

Khi CLI lớn lên:

```text
presentation/
├── cli.py
└── formatters.py
```

Ví dụ:

```python
def format_story(story):

    return (
        f"Title : {story.title}\n"
        f"Source: {story.source.name}\n"
        f"URL   : {story.url.value}"
    )
```

CLI:

```python
print(format_story(story))
```

---

# 25. JSON Output

Một ngày bạn muốn:

```bash
story-crawler crawl URL --json
```

Không cần sửa Application.

CLI format:

```python
import json


def format_story_json(story):

    return json.dumps({
        "title": story.title,
        "source": story.source.name,
        "url": story.url.value,
    })
```

Đây là một ví dụ nhỏ của **OCP**.

---

# 26. Application không thay đổi

Cho dù CLI output:

```text
human readable
```

hay:

```json
{
    "title": "..."
}
```

Use Case vẫn:

```python
story = app.execute(url)
```

Đây là separation giữa:

```text
Use Case
```

và:

```text
Presentation
```

---

# 27. Hoàn thiện `main()`

Một cấu trúc đơn giản:

```python
def main():

    parser = create_parser()

    args = parser.parse_args()

    app = build_application()

    if args.command == "crawl":

        return handle_crawl(
            args,
            app,
        )

    parser.error(
        "Unknown command"
    )
```

---

# 28. Nhưng `if/elif` ở CLI có vi phạm OCP?

Không nhất thiết.

Ví dụ:

```python
if args.command == "crawl":
    ...
elif args.command == "list":
    ...
```

không phải cứ `if` là vi phạm OCP.

Đây là một insight rất quan trọng.

Trong Buổi 4 chúng ta đã nói:

> `if/elif` **có thể** là code smell.

Không phải:

> `if/elif` luôn sai.

Nếu số command nhỏ và ổn định:

```python
if command == "crawl":
```

hoàn toàn hợp lý.

Đừng over-engineer.

---

# 29. Khi CLI có 30 commands?

Lúc đó có thể dùng registry:

```python
commands = {
    "crawl": handle_crawl,
    "list": handle_list,
    "show": handle_show,
}
```

Sau đó:

```python
handler = commands[args.command]

return handler(
    args,
    app,
)
```

Đây là Registry Pattern.

---

# 30. Test CLI

Đây là phần rất quan trọng cho Buổi 26.

Nhưng hôm nay ta chỉ nhìn architecture.

Ta muốn test:

```text
CLI
 ↓
Fake Application
```

Không:

```text
CLI
 ↓
SQLite
 ↓
Internet
```

---

# 31. Fake Application

Ví dụ:

```python
class FakeCrawlStory:

    def __init__(self, story):
        self.story = story
        self.received_url = None

    def execute(self, url):

        self.received_url = url

        return self.story
```

CLI có thể nhận Fake.

Đây chính là DI.

---

# 32. Tách `create_app`

Một thiết kế tốt:

```python
def main(app=None):

    if app is None:
        app = build_application()

    ...
```

Test:

```python
fake_app = FakeCrawlStory(...)

main(fake_app)
```

Nhưng có một điểm:

> Đừng biến mọi thứ thành dependency injection chỉ để test.

Nếu `build_application()` rất đơn giản và CLI nhỏ, có thể giữ:

```python
app = build_application()
```

và test handler riêng.

---

# 33. Một thiết kế sạch hơn

```text
presentation/
├── cli.py
├── commands.py
└── formatters.py

composition.py
```

### `cli.py`

```python
def main(app):
    ...
```

### `commands.py`

```python
def handle_crawl(args, app):
    ...
```

### `formatters.py`

```python
def format_story(story):
    ...
```

### `composition.py`

```python
def build_application():
    ...
```

Mỗi module có responsibility rõ ràng.

---

# 34. Toàn bộ flow

```text
$ story-crawler crawl URL
             │
             ▼
        argparse
             │
             ▼
       handle_crawl
             │
             ▼
        CrawlStory
             │
             ▼
      CrawlerRegistry
             │
             ▼
       SourceACrawler
             │
       ┌─────┴─────┐
       ▼           ▼
   HttpClient    Parser
       │           │
       └─────┬─────┘
             ▼
           Story
             │
             ▼
      StoryRepository
             │
             ▼
           SQLite
```

CLI chỉ đứng ở đầu và cuối flow.

---

# 35. Đây là SOLID nào?

## SRP

```text
CLI
Application
Crawler
Parser
Repository
```

mỗi thành phần có responsibility riêng.

## OCP

Thêm:

```text
Source B
JSON formatter
New command
```

có thể hạn chế modification vào core.

## LSP

```text
SourceACrawler
SourceBCrawler
```

phải tuân contract của `StoryCrawler`.

## ISP

```text
StoryRepository
HttpClient
StoryParser
```

là các abstraction nhỏ.

## DIP

```text
Application
 ↓
Protocol
 ↑
Infrastructure
```

---

# 36. Nguyên tắc vàng của Composition Root

Hãy nhớ câu này:

> **Dependency injection nên kết thúc ở Composition Root.**

Ví dụ:

```text
composition.py

RequestsHttpClient
        ↓
SourceACrawler
        ↓
CrawlerRegistry
        ↓
CrawlStory
```

Sau đó Application chạy độc lập với implementation cụ thể.

---

# 37. Cấu trúc project hiện tại

```text
src/story_crawler/

├── domain/
│   ├── story.py
│   ├── chapter.py
│   ├── crawler.py
│   └── repository.py
│
├── application/
│   ├── crawl_story.py
│   └── crawler_registry.py
│
├── infrastructure/
│   ├── http/
│   │   ├── client.py
│   │   └── requests_client.py
│   │
│   ├── crawler/
│   │   └── source_a/
│   │       ├── crawler.py
│   │       └── parser.py
│   │
│   └── persistence/
│       ├── connection.py
│       ├── schema.py
│       ├── mappers.py
│       └── sqlite_story_repository.py
│
├── presentation/
│   └── cli.py
│
└── composition.py
```

Đây đã là một architecture khá trưởng thành cho một project Python vừa/nhỏ.

---

# 38. Bài tập Buổi 25

### Bài 1

Tạo:

```text
composition.py
```

Implement:

```python
build_application()
```

---

### Bài 2

CLI hỗ trợ:

```bash
story-crawler crawl URL
```

---

### Bài 3

CLI không được import:

```python
requests
bs4
```

---

### Bài 4

CLI không được gọi:

```python
sqlite3.connect()
```

trực tiếp.

---

### Bài 5

Application không được:

```python
print()
```

---

### Bài 6

Thêm:

```bash
story-crawler crawl URL --json
```

nhưng **không sửa `CrawlStory`**.

---

# 39. Challenge lớn

Hãy đạt architecture:

```text
                 composition.py
                       │
         ┌─────────────┼─────────────┐
         ↓             ↓             ↓
   HTTP Client       Parser       Repository
         │             │             │
         └─────────────┼─────────────┘
                       ↓
                  Crawler
                       ↓
                 CrawlerRegistry
                       ↓
                   CrawlStory
                       ↑
                       │
                      CLI
```

Sau đó thử thay:

```text
RequestsHttpClient
```

bằng:

```text
FakeHttpClient
```

mà không sửa:

```text
SourceACrawler
CrawlStory
CLI
```

Nếu làm được thì bạn đã hiểu **Dependency Injection**, chứ không chỉ biết định nghĩa của nó.

---

# 40. Tư duy quan trọng nhất của Buổi 25

Đừng nghĩ DI là:

```python
def __init__(self, dependency):
```

DI sâu hơn thế.

Hãy nhìn:

```text
        WHAT
         │
         ▼
    Abstraction
         ▲
         │
        HOW
```

Application nói:

> Tôi cần `StoryRepository`.

Infrastructure nói:

> Tôi implement nó bằng SQLite.

Composition Root nói:

> Tôi sẽ ghép hai thứ lại.

Đây chính là tư duy **Dependency Inversion + Dependency Injection + Clean Architecture**.

---

## Tiếp theo — Buổi 26: Testing Architecture

Chúng ta sẽ không chỉ học `pytest`.

Ta sẽ kiểm tra toàn bộ architecture theo 4 tầng:

```text
Domain Tests
     ↓
Application Tests
     ↓
Infrastructure Tests
     ↓
CLI Tests
```

và đặc biệt sẽ làm một test rất quan trọng:

```text
CrawlStory
    ↓
FakeCrawler
    ↓
FakeRepository
```

để chứng minh **Application có thể test hoàn toàn không cần Internet, SQLite hay BeautifulSoup**.
