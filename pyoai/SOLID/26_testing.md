# Buổi 26 — Testing Architecture

Hôm nay chúng ta chuyển từ:

> **"Code được thiết kế để test"**

sang:

> **"Architecture được thiết kế để test từng tầng độc lập."**

Đây là một trong những buổi quan trọng nhất của toàn bộ phần SOLID.

---

# 1. Mục tiêu

Story Crawler hiện tại:

```text
CLI
 ↓
Application
 ↓
Domain
 ↓
Repository Interface
 ↓
SQLite Repository
```

và:

```text
Crawler
 ↓
HttpClient
 ↓
HTTP
```

Ta muốn test thành:

```text
                 Tests
                   │
        ┌──────────┼──────────┐
        ↓          ↓          ↓
     Domain    Application Infrastructure
        │          │          │
        ↓          ↓          ↓
     Entity     Fake DI      SQLite
```

Không phải test mọi thứ bằng SQLite + Internet.

---

# 2. Testing Pyramid

Hãy hình dung:

```text
                /\
               /  \
              / E2E\
             /------\
            /  Integ \
           /----------\
          / Unit Tests \
         /--------------\
```

Thông thường:

```text
Unit
████████████████████
Integration
██████
E2E
██
```

Unit test nhiều nhất.

Integration ít hơn.

E2E ít nhất.

---

# 3. Vì sao Architecture ảnh hưởng Testing?

Architecture xấu:

```python
class CrawlerManager:

    def crawl(self, url):

        db = sqlite3.connect(...)

        response = requests.get(...)

        soup = BeautifulSoup(...)

        ...

        print(...)
```

Muốn test:

```text
CrawlerManager
   ↓
Internet
   ↓
SQLite
   ↓
HTML
```

Rất khó.

Architecture tốt:

```text
CrawlStory
 ↓
Crawler interface
 ↓
Repository interface
```

Ta thay:

```text
Crawler → FakeCrawler
Repository → FakeRepository
```

và test cực nhanh.

---

# 4. Nguyên tắc quan trọng

Một unit test tốt nên:

```text
Fast
Isolated
Deterministic
Repeatable
```

### Fast

Không network.

### Isolated

Không phụ thuộc test khác.

### Deterministic

Cùng input → cùng kết quả.

### Repeatable

Chạy 1 lần hay 1.000 lần đều giống nhau.

---

# 5. Test Domain trước

Domain là tầng dễ test nhất.

Ví dụ:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Story:

    title: str
    source: Source
    url: Url
```

Test:

```python
def test_story():

    story = Story(
        title="Test Story",
        source=Source("source_a"),
        url=Url(
            "https://source-a.com/story/1"
        ),
    )

    assert story.title == "Test Story"
```

Không:

```text
SQLite
HTTP
CLI
```

---

# 6. Test Value Object

Ví dụ:

```python
@dataclass(frozen=True)
class Url:

    value: str

    def __post_init__(self):

        if not self.value.startswith(
            "http"
        ):
            raise ValueError(
                "Invalid URL"
            )
```

Test:

```python
def test_valid_url():

    url = Url(
        "https://example.com"
    )

    assert url.value == (
        "https://example.com"
    )
```

---

# 7. Test Domain Invariant

```python
def test_invalid_url():

    with pytest.raises(ValueError):

        Url("invalid")
```

Đây là test rất quan trọng.

Domain rule phải được bảo vệ ngay tại Domain.

---

# 8. Application Test

Đây mới là phần quan trọng.

`CrawlStory`:

```python
class CrawlStory:

    def __init__(
        self,
        registry,
        repository,
    ):
        self.registry = registry
        self.repository = repository

    def execute(self, url):

        crawler = self.registry.find(url)

        story = crawler.crawl(url)

        self.repository.save(story)

        return story
```

Ta không muốn:

```text
requests
BeautifulSoup
SQLite
```

---

# 9. Fake Crawler

```python
class FakeCrawler:

    def __init__(self, story):
        self.story = story
        self.received_url = None

    def can_handle(self, url):
        return True

    def crawl(self, url):

        self.received_url = url

        return self.story
```

---

# 10. Fake Repository

```python
class FakeStoryRepository:

    def __init__(self):

        self.items = []

    def save(self, story):

        self.items.append(story)
```

Đây là **Fake**, không phải Mock.

Nó có behavior thật nhưng đơn giản.

---

# 11. Fake Registry

```python
class FakeCrawlerRegistry:

    def __init__(self, crawler):

        self.crawler = crawler

    def find(self, url):

        return self.crawler
```

---

# 12. Application Unit Test

```python
def test_crawl_story():

    story = Story(
        title="Test Story",
        source=Source("source_a"),
        url=Url(
            "https://source-a.com/story/1"
        ),
    )

    crawler = FakeCrawler(story)

    registry = FakeCrawlerRegistry(
        crawler
    )

    repository = FakeStoryRepository()

    use_case = CrawlStory(
        registry=registry,
        repository=repository,
    )

    result = use_case.execute(
        story.url
    )

    assert result == story
```

Đây là **pure application test**.

Không có:

```text
Internet
SQLite
BeautifulSoup
requests
```

---

# 13. Test Side Effect

Không chỉ test return value.

Ta cần kiểm tra:

```text
CrawlStory
 ↓
repository.save()
```

Vì đây là behavior của Use Case.

```python
assert repository.items == [
    story
]
```

---

# 14. Test URL được truyền đúng

FakeCrawler lưu:

```python
self.received_url = url
```

Test:

```python
assert (
    crawler.received_url
    == story.url
)
```

Ta vừa test:

```text
Input
 ↓
Crawler
```

---

# 15. Test khi crawler fail

Crawler:

```python
class FailingCrawler:

    def can_handle(self, url):
        return True

    def crawl(self, url):

        raise CrawlerError(
            "Network failed"
        )
```

Test:

```python
def test_crawl_failure():

    crawler = FailingCrawler()

    registry = FakeCrawlerRegistry(
        crawler
    )

    repository = FakeStoryRepository()

    use_case = CrawlStory(
        registry,
        repository,
    )

    with pytest.raises(CrawlerError):

        use_case.execute(
            Url(
                "https://source-a.com/1"
            )
        )
```

---

# 16. Điều quan trọng hơn

Sau exception:

```text
repository.save()
```

không được gọi.

Vì crawler chưa tạo Story.

Với Fake Repository:

```python
assert repository.items == []
```

Đây là test behavior.

---

# 17. Test "No Crawler"

Registry:

```python
class CrawlerRegistry:

    def find(self, url):

        for crawler in self.crawlers:

            if crawler.can_handle(url):
                return crawler

        raise UnsupportedUrlError(url.value)
```

Test:

```python
def test_no_crawler():

    registry = CrawlerRegistry()

    with pytest.raises(
        UnsupportedUrlError
    ):

        registry.find(
            Url(
                "https://unknown.com"
            )
        )
```

---

# 18. Test Registry

Có 2 crawler:

```python
registry.register(
    SourceACrawler(...)
)

registry.register(
    SourceBCrawler(...)
)
```

Test:

```python
crawler = registry.find(
    Url(
        "https://source-b.com/story/1"
    )
)

assert isinstance(
    crawler,
    SourceBCrawler
)
```

Registry test không cần database.

---

# 19. Infrastructure Test

Đây là nơi test SQLite thật.

```python
connection = sqlite3.connect(
    ":memory:"
)

connection.row_factory = sqlite3.Row
```

Sau đó:

```python
initialize_database(
    connection
)
```

Repository:

```python
repository = SQLiteStoryRepository(
    connection
)
```

---

# 20. Integration Test

```python
def test_sqlite_repository():

    connection = sqlite3.connect(
        ":memory:"
    )

    connection.row_factory = sqlite3.Row

    initialize_database(
        connection
    )

    repository = SQLiteStoryRepository(
        connection
    )

    story = make_story()

    repository.save(story)

    result = repository.get_by_url(
        story.url
    )

    assert result == story
```

Đây là Integration Test.

---

# 21. Vì sao test SQLite thật?

Vì ta cần kiểm tra:

```text
SQL
 ↓
SQLite
 ↓
row
 ↓
mapping
 ↓
Domain
```

Nếu mock SQLite:

```python
connection = Mock()
```

ta không biết:

```text
SQL có đúng không?
schema có đúng không?
UNIQUE có hoạt động không?
mapping có đúng không?
```

---

# 22. Test Constraint

Schema:

```sql
url TEXT NOT NULL UNIQUE
```

Test upsert hoặc uniqueness.

Ví dụ nếu không dùng upsert:

```python
with pytest.raises(
    sqlite3.IntegrityError
):
    repository.save(story)
```

Test này thuộc Infrastructure.

---

# 23. Parser Test

Parser cũng là Infrastructure.

HTML fixture:

```python
HTML = """
<html>
    <body>
        <h1 class="story-title">
            My Story
        </h1>
    </body>
</html>
"""
```

Test:

```python
def test_parse_story():

    parser = SourceAStoryParser()

    story = parser.parse(
        HTML,
        Url(
            "https://source-a.com/1"
        ),
    )

    assert story.title == "My Story"
```

Không Internet.

---

# 24. Tại sao Parser không cần HTTP?

Vì:

```text
HttpClient
```

và:

```text
Parser
```

đã được tách.

Do đó ta có thể test:

```text
HTML fixture
 ↓
Parser
 ↓
Story
```

độc lập.

Đây chính là **SRP + DIP** tạo ra testability.

---

# 25. HTTP Client Test

HTTP Client là nơi có network.

Có hai hướng:

### Unit test

Mock HTTP library.

### Integration test

Gọi một test server.

Không nên phụ thuộc website thật.

---

# 26. Đừng test bằng website production

Sai:

```python
def test_crawler():

    crawler.crawl(
        "https://some-real-site.com"
    )
```

Test có thể fail vì:

```text
network down
site changed
Cloudflare
rate limit
server down
HTML changed
```

Test không còn deterministic.

---

# 27. Test Fixture

Tạo:

```text
tests/
├── fixtures/
│   ├── source_a_story.html
│   └── source_b_story.html
```

Parser test đọc fixture.

```python
html = Path(
    "tests/fixtures/source_a_story.html"
).read_text(
    encoding="utf-8"
)
```

Sau này HTML thay đổi, ta có thể kiểm soát fixture.

---

# 28. CLI Test

CLI nên test:

```text
arguments
 ↓
handler
 ↓
application
 ↓
output
```

Nhưng dùng Fake Application.

Ví dụ:

```python
class FakeApplication:

    def execute(self, url):

        return Story(
            title="Test",
            source=Source("fake"),
            url=url,
        )
```

---

# 29. CLI Test

```python
def test_crawl_command(capsys):

    app = FakeApplication()

    args = argparse.Namespace(
        url="https://example.com"
    )

    result = handle_crawl(
        args,
        app,
    )

    captured = capsys.readouterr()

    assert result == 0

    assert "Test" in captured.out
```

Không SQLite.

Không HTTP.

---

# 30. Đây chính là DI

CLI nhận:

```python
app
```

Application nhận:

```python
repository
registry
```

Crawler nhận:

```python
http_client
parser
```

Mọi tầng đều có thể thay dependency.

```text
CLI
 ↓
Fake App

App
 ↓
Fake Repository
Fake Registry

Crawler
 ↓
Fake HTTP
Fake Parser
```

---

# 31. Testing Matrix

Ta có:

| Component               | Test type   | Dependency          |
| ----------------------- | ----------- | ------------------- |
| `Url`                   | Unit        | None                |
| `Story`                 | Unit        | None                |
| `CrawlStory`            | Unit        | Fake                |
| `CrawlerRegistry`       | Unit        | Fake                |
| `SourceAParser`         | Unit        | HTML fixture        |
| `SourceACrawler`        | Unit        | Fake HTTP/Parser    |
| `SQLiteStoryRepository` | Integration | SQLite memory       |
| CLI                     | Unit        | Fake App            |
| Full system             | E2E         | Real infrastructure |

Đây là một architecture testable.

---

# 32. Contract Testing

Đây là phần rất hay khi có nhiều Plugin.

Ta có contract:

```python
class Crawler(Protocol):

    def can_handle(
        self,
        url: Url,
    ) -> bool:
        ...

    def crawl(
        self,
        url: Url,
    ) -> Story:
        ...
```

Mỗi plugin phải pass cùng một bộ test.

---

# 33. Ví dụ Contract Test

```python
def assert_crawler_contract(
    crawler,
    valid_url,
):

    assert crawler.can_handle(
        valid_url
    )

    story = crawler.crawl(
        valid_url
    )

    assert isinstance(
        story,
        Story
    )
```

Source A:

```python
assert_crawler_contract(
    SourceACrawler(...),
    source_a_url,
)
```

Source B:

```python
assert_crawler_contract(
    SourceBCrawler(...),
    source_b_url,
)
```

---

# 34. Đây liên quan trực tiếp tới LSP

LSP nói:

> Subtype phải có thể thay thế abstraction mà không phá contract.

Contract test chính là cách rất thực tế để kiểm tra điều đó.

```text
Crawler
  ↑
  ├── SourceA
  ├── SourceB
  └── SourceC
```

Tất cả phải đáp ứng contract.

---

# 35. Architecture Test

Ta còn có thể kiểm tra dependency.

Ví dụ:

```text
domain/
```

không được import:

```text
requests
sqlite3
bs4
```

Đây là **Architecture Test**.

Mục tiêu:

```text
Domain
  ✗ requests
  ✗ sqlite3
  ✗ BeautifulSoup
```

---

# 36. Vì sao Architecture Test quan trọng?

Ban đầu architecture:

```text
Domain
 ↓
Infrastructure
```

Sau vài tháng một developer thêm:

```python
from infrastructure.sqlite import ...
```

vào Domain.

Code vẫn chạy.

Unit test có thể vẫn pass.

Nhưng architecture đã bị phá.

Architecture Test giúp phát hiện điều đó.

---

# 37. Testing không chỉ để bắt bug

Đây là insight quan trọng.

Test còn là:

```text
Design Feedback
```

Nếu một class rất khó test:

```text
10 dependencies
5 external services
3 global states
```

thì vấn đề có thể nằm ở **architecture**, không phải ở test.

---

# 38. Testability là architectural quality

So sánh:

### Code khó test

```text
CrawlerManager
├── SQLite
├── requests
├── BeautifulSoup
├── filesystem
├── logging
├── notifier
└── CLI
```

### Code dễ test

```text
CrawlStory
├── Crawler
└── Repository
```

và:

```text
Crawler
├── HttpClient
└── Parser
```

Dependencies rõ ràng.

---

# 39. Test Use Case hoàn toàn offline

Đây là bài test quan trọng nhất của Buổi 26:

```text
             CrawlStory
             /        \
            /          \
     FakeRegistry    FakeRepository
          │
          ▼
      FakeCrawler
```

Chạy:

```bash
pytest
```

không cần:

```text
Internet
SQLite
BeautifulSoup
requests
```

Nếu test này pass, Application architecture của chúng ta đang khá tốt.

---

# 40. Test toàn bộ pipeline

Sau khi unit test ổn, ta có integration test:

```text
SourceACrawler
      ↓
Fake HTTP
      ↓
Real Parser
      ↓
Story
      ↓
SQLite Repository
      ↓
SQLite :memory:
```

Đây là integration test rất giá trị.

---

# 41. Sau đó mới E2E

Cuối cùng:

```text
CLI
 ↓
Application
 ↓
Crawler
 ↓
HTTP
 ↓
Parser
 ↓
Repository
 ↓
SQLite
```

Đây là E2E.

Nhưng không cần hàng trăm E2E test.

Một vài test quan trọng là đủ.

---

# 42. Test Structure

Tôi khuyên project hiện tại dùng:

```text
tests/
│
├── unit/
│   ├── domain/
│   ├── application/
│   ├── crawler/
│   └── presentation/
│
├── integration/
│   ├── persistence/
│   └── http/
│
├── contract/
│   └── crawlers/
│
├── fixtures/
│   ├── source_a/
│   └── source_b/
│
└── e2e/
```

---

# 43. Test Naming

Không nên:

```python
def test_crawler():
    ...
```

Nên mô tả behavior:

```python
def test_crawl_story_saves_story():
    ...
```

```python
def test_crawl_story_returns_crawled_story():
    ...
```

```python
def test_registry_rejects_unsupported_url():
    ...
```

Tên test nên nói:

> **System phải làm gì?**

---

# 44. Một nguyên tắc quan trọng

Đừng test implementation quá mức.

Ví dụ:

```python
assert crawler.http.get.called
```

không phải lúc nào cũng cần.

Quan trọng hơn:

```python
assert result == expected_story
```

Test behavior thay vì implementation detail.

---

# 45. Mock quá nhiều là smell

Ví dụ:

```python
mock1
mock2
mock3
mock4
mock5
mock6
```

rồi test:

```python
mock1.assert_called_once()
mock2.assert_called_once()
...
```

Nếu test trở nên cực kỳ phức tạp:

> Có thể architecture đang quá coupled.

Hãy xem xét:

```text
Fake
In-memory implementation
Pure function
Smaller abstraction
```

---

# 46. Fake Repository rất hữu ích

Ví dụ:

```python
class InMemoryStoryRepository:

    def __init__(self):
        self._stories = {}

    def save(self, story):
        self._stories[
            story.url.value
        ] = story

    def get_by_url(self, url):
        return self._stories.get(
            url.value
        )
```

Nó có thể được dùng:

```text
Unit test
Development
Prototype
CLI demo
```

---

# 47. Nhưng Fake không thay Integration Test

Đây là lỗi phổ biến:

> "Có FakeRepository rồi nên không cần test SQLite."

Sai.

Fake kiểm tra:

```text
Application behavior
```

SQLite test kiểm tra:

```text
Persistence implementation
```

Cần cả hai.

---

# 48. SOLID và Testing

Buổi này kết nối toàn bộ SOLID:

### SRP

Class nhỏ → dễ test.

### OCP

Thêm implementation → test riêng.

### LSP

Contract test.

### ISP

Interface nhỏ → fake dễ viết.

### DIP

Dependency Injection → dependency có thể thay thế.

Đặc biệt:

> **DIP là một trong những nguyên lý tạo ra testability mạnh nhất.**

---

# 49. Architecture hiện tại

```text
                    CLI
                     │
                     ▼
              ┌─────────────┐
              │ CrawlStory  │
              └──────┬──────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
   CrawlerRegistry       StoryRepository
          │                     ▲
          ▼                     │
    SourceACrawler       SQLiteRepository
       │       │
       ▼       ▼
   HttpClient Parser
```

Testing:

```text
CLI
 ↓
Fake Application

Application
 ↓
Fake Crawler
Fake Repository

Crawler
 ↓
Fake HTTP
Real/Fake Parser

Repository
 ↓
SQLite :memory:
```

---

# 50. Bài tập Buổi 26

## Bài 1 — Application Unit Test

Viết:

```python
test_crawl_story_saves_story()
```

Kiểm tra:

```text
execute()
 ↓
crawler.crawl()
 ↓
repository.save()
 ↓
return Story
```

---

## Bài 2 — Failure Test

Kiểm tra:

```text
CrawlerError
 ↓
execute()
 ↓
exception
 ↓
repository không save
```

---

## Bài 3 — Registry Test

Test:

```text
Source A URL
→ SourceACrawler
```

và:

```text
Unknown URL
→ UnsupportedUrlError
```

---

## Bài 4 — Parser Test

Dùng fixture:

```text
source_a_story.html
```

Không Internet.

---

## Bài 5 — SQLite Integration Test

Dùng:

```python
sqlite3.connect(":memory:")
```

test:

```text
save()
get_by_url()
exists()
```

---

## Bài 6 — CLI Test

Dùng:

```text
FakeApplication
```

và kiểm tra output.

---

# 51. Challenge — Test Architecture

Hãy tạo:

```text
tests/
├── unit/
├── integration/
├── contract/
└── e2e/
```

và đạt:

```text
pytest tests/unit
```

→ không cần Internet.

```text
pytest tests/integration
```

→ chỉ dùng SQLite in-memory / controlled infrastructure.

```text
pytest tests/contract
```

→ tất cả crawler plugin phải pass contract.

---

# 52. Checklist kiến trúc

Sau Buổi 26, hãy tự kiểm tra:

```text
[ ] Domain không import infrastructure
[ ] Application không import sqlite3
[ ] Application không import requests
[ ] Parser không gọi HTTP
[ ] Crawler không save database
[ ] CLI không tạo SQLite trực tiếp
[ ] CLI không gọi requests
[ ] Application test không cần Internet
[ ] Repository có integration test
[ ] Plugin có contract test
```

Nếu tất cả đều `[x]`, architecture của chúng ta đã khá vững.

---

# 53. Bức tranh lớn

Chúng ta đã đi từ:

```text
Buổi 20
Mini Project
```

đến:

```text
Buổi 21
Domain + Crawler Port
```

```text
Buổi 22
Plugin Architecture
```

```text
Buổi 23
HTTP Client + Parser
```

```text
Buổi 24
SQLite Repository
```

```text
Buổi 25
CLI + Dependency Injection
```

và hôm nay:

```text
Buổi 26
Testing Architecture
```

Architecture hiện tại đã đủ tốt để bước sang **async**.

---

# Buổi 27 — Async Crawler

Đây sẽ là bước chuyển rất thú vị:

```text
Crawler
   ↓
HttpClient
   ↓
sync requests
```

sẽ thành:

```text
AsyncCrawler
     ↓
AsyncHttpClient
     ↓
httpx.AsyncClient
     ↓
asyncio
```

và chúng ta sẽ xử lý đồng thời:

```text
Story
 ├── Chapter 1 ──┐
 ├── Chapter 2 ──┤
 ├── Chapter 3 ──┼── concurrent
 ├── Chapter 4 ──┤
 └── Chapter 5 ──┘
```

Quan trọng nhất: **chúng ta sẽ giữ nguyên Application/Domain abstraction hiện tại**, chỉ thay Infrastructure implementation. Đây sẽ là một ví dụ rất thực tế về **OCP + DIP + LSP** trong một hệ thống async.
