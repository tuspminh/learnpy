# Iterator Deep Dive — Buổi 22

# Thiết kế thư viện sử dụng Iterator

Đây là buổi chuyển từ **"biết dùng Iterator"** sang **"biết thiết kế API dựa trên Iterator"**.

Trong code production, Iterator không chỉ là:

```python
for item in items:
    ...
```

Mà nó ảnh hưởng trực tiếp đến:

* API design
* Memory usage
* Streaming
* Composition
* Testability
* Type hint
* Separation of concerns
* Plugin architecture
* Crawler architecture
* Data pipeline

Đặc biệt với framework crawler mà bạn đang xây dựng, kiến thức hôm nay rất quan trọng.

---

# 1. Vấn đề của API trả về List

Giả sử ta thiết kế:

```python
class ChapterCrawler:

    def crawl(self) -> list[Chapter]:
        ...
```

API này nói rằng:

> "Tôi sẽ tạo toàn bộ Chapter trước rồi trả cho bạn."

Ví dụ:

```python
chapters = crawler.crawl()

for chapter in chapters:
    save(chapter)
```

Nếu có:

```text
100 chapters
```

thì ổn.

Nhưng:

```text
100,000 chapters
```

hoặc:

```text
10,000,000 chapters
```

thì bắt đầu có vấn đề.

---

# 2. Thiết kế tốt hơn

Thay:

```python
def crawl(self) -> list[Chapter]:
```

bằng:

```python
from collections.abc import Iterator

def crawl(self) -> Iterator[Chapter]:
    ...
```

Consumer:

```python
for chapter in crawler.crawl():
    save(chapter)
```

Bây giờ crawler có thể streaming.

---

# 3. `Iterable` và `Iterator`

Đây là phần **cực kỳ quan trọng**.

Nhiều người sử dụng hai khái niệm này lẫn lộn.

---

## Iterable

Một object là Iterable nếu có thể:

```python
iter(obj)
```

Ví dụ:

```python
list_data = [1, 2, 3]

iter(list_data)
```

List là:

```text
Iterable
```

nhưng bản thân List **không phải Iterator**.

---

## Iterator

Iterator phải hỗ trợ:

```python
next(obj)
```

Ví dụ:

```python
iterator = iter([1, 2, 3])

next(iterator)
```

---

# 4. Quan hệ

Hãy nhớ:

```text
Iterable
    │
    │ iter()
    ▼
Iterator
    │
    │ next()
    ▼
Value
```

Ví dụ:

```python
numbers = [1, 2, 3]

iterator = iter(numbers)

next(iterator)
```

---

# 5. Protocol

Python không yêu cầu bạn kế thừa:

```python
Iterator
```

Bạn chỉ cần implement protocol phù hợp.

Iterable:

```python
def __iter__(self):
    ...
```

Iterator:

```python
def __iter__(self):
    return self

def __next__(self):
    ...
```

Đây là **Structural Typing / Duck Typing**.

---

# 6. Thiết kế Collection riêng

Giả sử xây dựng:

```python
class BookCollection:
    ...
```

Ta muốn:

```python
books = BookCollection()

for book in books:
    print(book)
```

Có thể viết:

```python
class BookCollection:

    def __init__(self, books):
        self._books = books

    def __iter__(self):
        return iter(self._books)
```

Đây là một Iterable.

---

# 7. Tại sao `__iter__()` nên trả Iterator?

```python
def __iter__(self):
    return iter(self._books)
```

Mỗi lần gọi:

```python
iter(books)
```

sẽ tạo Iterator mới.

Điều này cho phép:

```python
for book in books:
    ...

for book in books:
    ...
```

cả hai vòng lặp đều hoạt động.

---

# 8. Sai lầm phổ biến

Không nên:

```python
class BadCollection:

    def __init__(self):
        self._iterator = iter([1, 2, 3])

    def __iter__(self):
        return self._iterator
```

Sau:

```python
collection = BadCollection()

print(list(collection))
print(list(collection))
```

Kết quả:

```text
[1, 2, 3]
[]
```

Vì Iterator đã exhausted.

---

# 9. Iterable có thể tạo Iterator mới

Đây là sự khác biệt:

```text
Iterable
    │
    ├── iter() → Iterator A
    │
    └── iter() → Iterator B
```

Iterator:

```text
Iterator
    │
    └── next() → state hiện tại
```

---

# 10. API nên trả `Iterable` hay `Iterator`?

Câu hỏi rất hay.

Ví dụ:

```python
def get_books() -> Iterable[Book]:
    ...
```

nghĩa là:

> API cung cấp một nguồn dữ liệu có thể lặp.

Còn:

```python
def get_books() -> Iterator[Book]:
    ...
```

nghĩa là:

> API trả về chính một Iterator có state và single-pass.

---

# 11. `Iterable` thường linh hoạt hơn

Ví dụ:

```python
from collections.abc import Iterable


def process_books(
    books: Iterable[Book]
):
    for book in books:
        ...
```

Hàm này nhận được:

```python
list
tuple
set
generator
iterator
database cursor
custom collection
```

Miễn là chúng là Iterable.

Đây là nguyên tắc API rất tốt:

> **Nhận abstraction rộng, không yêu cầu implementation cụ thể.**

---

# 12. Đừng viết

```python
def process_books(
    books: list[Book]
):
    ...
```

nếu bạn thực sự chỉ cần:

```python
for book in books:
    ...
```

Vì như vậy API bị giới hạn không cần thiết.

---

# 13. Ví dụ

Tốt:

```python
from collections.abc import Iterable


def total_price(
    books: Iterable[Book]
) -> float:

    return sum(
        book.price
        for book in books
    )
```

Có thể truyền:

```python
total_price(book_list)
```

hoặc:

```python
total_price(book_generator())
```

hoặc:

```python
total_price(database_cursor)
```

---

# 14. Library Design Principle

Nếu function chỉ cần:

```text
iterate
```

hãy yêu cầu:

```python
Iterable[T]
```

Không yêu cầu:

```python
list[T]
```

---

Nếu function cần:

```text
next()
```

và stateful iteration:

```python
Iterator[T]
```

---

# 15. Generator API

Một API rất đẹp:

```python
from collections.abc import Iterator


def read_lines(
    path: str
) -> Iterator[str]:

    with open(path, encoding="utf-8") as file:

        for line in file:
            yield line
```

Consumer:

```python
for line in read_lines("app.log"):
    print(line)
```

---

# 16. Tách Source và Consumer

Đây là architecture rất quan trọng.

Source:

```python
def read_books() -> Iterator[Book]:
    ...
```

Consumer:

```python
def save_books(
    books: Iterable[Book]
):
    for book in books:
        repository.save(book)
```

Ghép:

```python
save_books(
    read_books()
)
```

Hai thành phần không phụ thuộc trực tiếp vào nhau.

---

# 17. Composable API

Đây là sức mạnh rất lớn của Iterator.

Ta có:

```python
def read_books() -> Iterator[Book]:
    ...
```

Filter:

```python
def filter_completed(
    books: Iterable[Book]
) -> Iterator[Book]:

    for book in books:

        if book.completed:
            yield book
```

Transform:

```python
def normalize(
    books: Iterable[Book]
) -> Iterator[Book]:

    for book in books:

        book.title = book.title.strip()

        yield book
```

Pipeline:

```python
books = read_books()

books = filter_completed(books)

books = normalize(books)
```

Cuối cùng:

```python
save_books(books)
```

---

# 18. Pipeline Architecture

```text
Source
  │
  ▼
Filter
  │
  ▼
Transform
  │
  ▼
Validate
  │
  ▼
Save
```

Tất cả đều:

```python
Iterable[T]
        ↓
Iterator[T]
```

---

# 19. Generic Iterator

Bây giờ chúng ta đưa Type Hint vào.

```python
from collections.abc import Iterable, Iterator
from typing import TypeVar


T = TypeVar("T")
```

Viết:

```python
def filter_items(
    items: Iterable[T],
    predicate
) -> Iterator[T]:

    for item in items:

        if predicate(item):
            yield item
```

Đây là một API generic.

---

# 20. Generic Transform

```python
from collections.abc import Callable, Iterable, Iterator
from typing import TypeVar


T = TypeVar("T")
U = TypeVar("U")


def transform(
    items: Iterable[T],
    func: Callable[[T], U]
) -> Iterator[U]:

    for item in items:
        yield func(item)
```

Sử dụng:

```python
numbers = [1, 2, 3]

result = transform(
    numbers,
    lambda x: x * 2
)
```

Type:

```text
Iterable[int]
        ↓
Iterator[int]
```

---

Nếu:

```python
transform(
    numbers,
    str
)
```

thì:

```text
Iterable[int]
        ↓
Iterator[str]
```

Đây chính là generic pipeline.

---

# 21. `yield` giúp API rất đẹp

Thay vì:

```python
def filter_items(items):

    result = []

    for item in items:

        if condition(item):
            result.append(item)

    return result
```

Ta viết:

```python
def filter_items(items):

    for item in items:

        if condition(item):
            yield item
```

Ưu điểm:

* Lazy
* Streaming
* Không intermediate list
* Composable
* Memory efficient

---

# 22. Library nên tránh materialization không cần thiết

Không nên:

```python
def process(items):

    items = list(items)

    ...
```

nếu không thực sự cần.

Bởi vì người dùng có thể truyền:

```python
generator()
```

và bạn vừa phá vỡ tính lazy.

---

# 23. Khi nào materialize?

Chỉ khi cần:

### Length

```python
len(items)
```

### Random access

```python
items[100]
```

### Reuse

```python
for x in items:
    ...

for x in items:
    ...
```

### Sorting

```python
sorted(items)
```

---

# 24. API có thể cung cấp cả hai

Ví dụ:

```python
class BookRepository:

    def iter_books(self) -> Iterator[Book]:
        ...

    def list_books(self) -> list[Book]:
        return list(self.iter_books())
```

Đây là API rất tốt.

Người dùng muốn streaming:

```python
for book in repo.iter_books():
    ...
```

Người dùng muốn materialize:

```python
books = repo.list_books()
```

---

# 25. Đây là pattern rất mạnh

```text
iter_books()
    ↓
Iterator
    ↓
lazy

list_books()
    ↓
list(iter_books())
    ↓
eager
```

Một implementation.

Hai cách sử dụng.

---

# 26. Ví dụ Repository

```python
from collections.abc import Iterator


class BookRepository:

    def iter_books(self) -> Iterator[Book]:

        cursor = self.connection.execute(
            """
            SELECT id, title
            FROM books
            """
        )

        for row in cursor:

            yield Book(
                id=row["id"],
                title=row["title"]
            )

    def list_books(self) -> list[Book]:

        return list(
            self.iter_books()
        )
```

Đây là cách thiết kế rất phù hợp với ứng dụng SQLite của bạn.

---

# 27. Iterator trong Plugin Architecture

Với crawler plugin:

```python
class NovelPlugin:

    def iter_books(self) -> Iterator[Book]:
        ...
```

Plugin A:

```python
def iter_books(self):

    yield Book(...)
    yield Book(...)
```

Plugin B:

```python
def iter_books(self):

    yield Book(...)
    yield Book(...)
```

Framework không cần biết dữ liệu đến từ đâu.

---

# 28. Plugin Contract

Bạn có thể định nghĩa:

```python
from abc import ABC, abstractmethod
from collections.abc import Iterator


class NovelPlugin(ABC):

    @abstractmethod
    def iter_books(self) -> Iterator[Book]:
        ...
```

Framework:

```python
def crawl(
    plugin: NovelPlugin
):

    for book in plugin.iter_books():
        save(book)
```

---

# 29. Async Library Design

Nếu dữ liệu đến từ network:

```python
from collections.abc import AsyncIterator


class AsyncNovelPlugin:

    async def iter_books(
        self
    ) -> AsyncIterator[Book]:

        ...
        yield book
```

Consumer:

```python
async for book in plugin.iter_books():
    await save(book)
```

---

# 30. Sync và Async API

Một library tốt có thể phân biệt:

```text
Sync
    ↓
Iterator[T]

Async
    ↓
AsyncIterator[T]
```

Không nên cố ép Async API thành Sync.

---

# 31. Interface cho Crawler

Ví dụ:

```python
from collections.abc import Iterator


class Crawler:

    def iter_urls(self) -> Iterator[str]:
        ...

    def iter_pages(self) -> Iterator[Page]:
        ...

    def iter_books(self) -> Iterator[Book]:
        ...

    def iter_chapters(self) -> Iterator[Chapter]:
        ...
```

Pipeline:

```text
iter_urls()
   ↓
iter_pages()
   ↓
iter_books()
   ↓
iter_chapters()
```

---

# 32. Một thiết kế tốt hơn

Thay vì:

```python
crawl() -> list[Book]
```

ta có:

```python
iter_books() -> Iterator[Book]
```

Tên `iter_*` còn truyền đạt **ý nghĩa API** rất rõ:

> "Hàm này trả dữ liệu dạng stream/iterator."

---

# 33. `Iterable` ở Input

Ví dụ:

```python
def process_chapters(
    chapters: Iterable[Chapter]
):
    ...
```

Bạn không quan tâm:

```text
List?
Tuple?
Generator?
Database Cursor?
Iterator?
```

Bạn chỉ cần:

```text
Có thể iterate.
```

Đây là abstraction tốt.

---

# 34. Iterator ở Output

Ví dụ:

```python
def parse_chapters(
    html: str
) -> Iterator[Chapter]:
    ...
```

Điều này truyền đạt:

> Parser có thể tạo nhiều Chapter và chúng được sinh từng cái một.

---

# 35. Đây là một API rất mạnh

```python
def parse_chapters(
    html: str
) -> Iterator[Chapter]:
```

thay vì:

```python
def parse_chapters(
    html: str
) -> list[Chapter]:
```

Nếu một ngày website có:

```text
1 chapter
```

→ vẫn hoạt động.

Nếu:

```text
100 chapters
```

→ vẫn hoạt động.

Nếu:

```text
100,000 chapters
```

→ vẫn có thể streaming.

---

# 36. Iterator Adapter

Một kỹ thuật hay trong library design là Adapter.

Ví dụ API cũ:

```python
def get_books() -> list[Book]:
    ...
```

Ta có thể tạo:

```python
def iter_books() -> Iterator[Book]:

    yield from get_books()
```

Bây giờ API mới hỗ trợ streaming ở tầng downstream.

---

# 37. Iterator Decorator

Ta có thể decorate Iterator.

Ví dụ logging:

```python
def log_items(items):

    for item in items:

        print("Processing:", item)

        yield item
```

Pipeline:

```python
items = read_items()

items = log_items(items)

save_items(items)
```

---

# 38. Retry Iterator

Crawler thường cần retry.

```python
def retry(
    items,
    attempts=3
):
    ...
```

Tuy nhiên cần phân biệt:

> Retry từng item

với:

> Retry toàn bộ iterator.

Đây là vấn đề thiết kế API, không đơn giản chỉ là `try/except`.

Ví dụ đơn giản:

```python
def process(items):

    for item in items:

        for attempt in range(3):

            try:
                yield download(item)
                break

            except Exception:
                if attempt == 2:
                    raise
```

---

# 39. Iterator và Error Handling

Một Iterator có thể phát sinh exception **ở giữa quá trình iteration**.

Ví dụ:

```python
def items():

    yield 1
    yield 2

    raise RuntimeError("Network error")

    yield 3
```

Consumer:

```python
try:

    for item in items():
        print(item)

except RuntimeError:
    ...
```

Điều này quan trọng trong streaming API.

---

# 40. Iterator và Resource Management

Một API như:

```python
def read_file() -> Iterator[str]:
    ...
```

có thể giữ file mở trong quá trình iteration.

Ví dụ:

```python
def read_file(path):

    with open(path) as f:

        for line in f:
            yield line
```

File chỉ đóng khi generator hoàn thành hoặc bị đóng.

Đây là một lý do phải thiết kế lifecycle cẩn thận.

---

# 41. Không nên trả Iterator "mồ côi"

Ví dụ nguy hiểm:

```python
def get_cursor():

    connection = sqlite3.connect(...)

    cursor = connection.execute(...)

    return cursor
```

Ai đóng:

```text
connection?
```

Nếu API trả Iterator nhưng resource lifecycle không rõ ràng, có thể gây leak.

---

# 42. Pattern tốt hơn

Đóng resource trong generator:

```python
def iter_books(connection):

    cursor = connection.execute(
        "SELECT * FROM books"
    )

    try:

        for row in cursor:
            yield row

    finally:

        cursor.close()
```

Hoặc để tầng quản lý connection chịu trách nhiệm rõ ràng.

---

# 43. Library Contract phải nói rõ

Một API Iterator production nên trả lời được:

```text
1. Iterator có single-pass không?
2. Có lazy không?
3. Có giữ resource không?
4. Khi nào resource được đóng?
5. Có thể iterate lần hai không?
6. Exception có thể xảy ra ở đâu?
7. Có thread-safe không?
8. Có async version không?
```

Đây là tư duy API design cấp production.

---

# 44. Mini Library

Hãy thiết kế một thư viện nhỏ:

```text
streamkit/
│
├── __init__.py
├── source.py
├── transform.py
├── filter.py
└── pipeline.py
```

---

## `source.py`

```python
from collections.abc import Iterator


def numbers(
    start: int,
    end: int
) -> Iterator[int]:

    for value in range(start, end):
        yield value
```

---

## `transform.py`

```python
from collections.abc import Callable, Iterable, Iterator
from typing import TypeVar


T = TypeVar("T")
U = TypeVar("U")


def map_items(
    items: Iterable[T],
    func: Callable[[T], U]
) -> Iterator[U]:

    for item in items:
        yield func(item)
```

---

## `filter.py`

```python
from collections.abc import Callable, Iterable, Iterator
from typing import TypeVar


T = TypeVar("T")


def filter_items(
    items: Iterable[T],
    predicate: Callable[[T], bool]
) -> Iterator[T]:

    for item in items:

        if predicate(item):
            yield item
```

---

# 45. Sử dụng Library

```python
from streamkit.source import numbers
from streamkit.transform import map_items
from streamkit.filter import filter_items


items = numbers(1, 100)

items = filter_items(
    items,
    lambda x: x % 2 == 0
)

items = map_items(
    items,
    lambda x: x * x
)

for item in items:
    print(item)
```

Pipeline:

```text
numbers
   ↓
filter
   ↓
map
   ↓
consumer
```

Không có List trung gian.

---

# 46. Thiết kế fluent API

Sau này ta có thể xây:

```python
(
    Stream(numbers(1, 100))
    .filter(lambda x: x % 2 == 0)
    .map(lambda x: x * x)
    .take(10)
)
```

Đây chính là nền tảng để xây dựng một **Iterator-based Data Pipeline Library**.

---

# 47. Nhưng đừng over-engineer

Không phải lúc nào cũng cần:

```python
Stream
Pipeline
Node
Stage
Executor
Scheduler
...
```

Nếu chỉ cần:

```python
def filter_items(...):
    yield ...
```

thì đó có thể là thiết kế tốt hơn.

Nguyên tắc:

> **Abstraction chỉ nên xuất hiện khi nó giải quyết một vấn đề thực tế.**

---

# 48. Testing Iterator

Đây là phần rất quan trọng.

Test:

```python
def test_numbers():

    result = list(
        numbers(1, 5)
    )

    assert result == [
        1, 2, 3, 4
    ]
```

---

# 49. Test Lazy

Không chỉ test output.

Ta cần test:

> Iterator có thực sự lazy không?

Ví dụ:

```python
def source():

    print("created")

    yield 1
```

Tạo:

```python
gen = source()
```

Không nên in:

```text
created
```

Chỉ khi:

```python
next(gen)
```

mới thực hiện code bên trong generator.

---

# 50. Test Single Pass

```python
gen = numbers(1, 5)

assert list(gen) == [1, 2, 3, 4]

assert list(gen) == []
```

Điều này xác nhận semantics.

---

# 51. Test Iterable

Nếu class là Collection:

```python
collection = BookCollection(...)

assert list(collection) == expected
assert list(collection) == expected
```

Hai lần đều phải hoạt động nếu API tuyên bố collection có thể iterate lại.

---

# 52. API Design Rules

Bạn có thể ghi lại bộ quy tắc này:

### Rule 1

Nếu chỉ cần iterate:

```python
Iterable[T]
```

### Rule 2

Nếu trả stream single-pass:

```python
Iterator[T]
```

### Rule 3

Nếu có async I/O:

```python
AsyncIterator[T]
```

### Rule 4

Không materialize nếu không cần.

### Rule 5

Document resource lifecycle.

### Rule 6

Document single-pass/reusable.

### Rule 7

Cho phép consumer quyết định có materialize hay không.

---

# 53. Architecture cho ứng dụng crawler của bạn

Một kiến trúc rất hợp lý:

```text
                    Crawler Framework
                           │
              ┌────────────┴────────────┐
              │                         │
          Sync Plugin              Async Plugin
              │                         │
              ▼                         ▼
        Iterator[Book]          AsyncIterator[Book]
              │                         │
              └────────────┬────────────┘
                           ▼
                       Pipeline
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
          Validate       Transform      Filter
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                       Repository
```

Điểm quan trọng:

**Framework không cần biết dữ liệu được materialize hay streaming.**

---

# 54. Design Principle quan trọng nhất hôm nay

Thay vì thiết kế:

```python
def get_data() -> list[Data]:
```

hãy suy nghĩ:

```python
def iter_data() -> Iterator[Data]:
```

và ở tầng consumer:

```python
for data in iter_data():
    ...
```

Nếu thực sự cần List:

```python
data = list(iter_data())
```

Như vậy:

> **Quyền quyết định materialization thuộc về consumer.**

Đây là một thiết kế API rất mạnh.

---

# Bài tập Buổi 22

## Bài 1 — Custom Collection

Viết:

```python
class BookCollection:
    ...
```

Yêu cầu:

```python
books = BookCollection(...)

for book in books:
    ...
```

và:

```python
list(books)
```

có thể gọi nhiều lần.

---

## Bài 2 — Generic Pipeline

Viết:

```python
map_items()
filter_items()
take()
```

với API:

```python
Iterable[T] → Iterator[T]
```

Ví dụ:

```python
items = numbers(1, 1000)

items = filter_items(
    items,
    lambda x: x % 2 == 0
)

items = map_items(
    items,
    lambda x: x * x
)

items = take(items, 10)
```

---

## Bài 3 — Repository

Thiết kế:

```python
class BookRepository:

    def iter_books(self) -> Iterator[Book]:
        ...

    def list_books(self) -> list[Book]:
        ...
```

Trong đó:

```python
list_books()
```

phải được xây dựng từ:

```python
iter_books()
```

chứ không được duplicate logic query.

---

## Bài 4 — Crawler Plugin

Thiết kế interface:

```python
class NovelPlugin(ABC):

    @abstractmethod
    def iter_books(self) -> Iterator[Book]:
        ...
```

Sau đó viết hai plugin giả:

```text
SiteAPlugin
SiteBPlugin
```

Framework phải xử lý cả hai bằng cùng một pipeline:

```python
for book in plugin.iter_books():
    repository.save(book)
```

---

# Tổng kết Buổi 22

Đây là những kiến thức bạn cần nắm thật chắc:

```text
Iterable
    ↓
iter()
    ↓
Iterator
    ↓
next()
```

và trong thiết kế API:

```text
Input
    ↓
Iterable[T]

Output
    ↓
Iterator[T]
```

Async:

```text
AsyncIterable[T]
        ↓
AsyncIterator[T]
        ↓
async for
```

Quan trọng nhất:

> **Đừng ép dữ liệu thành List nếu API của bạn chỉ cần khả năng iteration.**

Thiết kế tốt:

```python
def process(
    items: Iterable[T]
) -> ...
```

và:

```python
def generate() -> Iterator[T]:
    yield ...
```

Cho phép:

```text
List
Tuple
Generator
Iterator
File
Database Cursor
Custom Collection
```

đều đi qua cùng một API.

---

## Bước tiếp theo

**Buổi 23 — Dự án thực tế: xây dựng một Iterator/Streaming Library hoàn chỉnh.**

Chúng ta sẽ kết hợp toàn bộ khóa học:

```text
Iterator
+
Generator
+
itertools
+
Lazy Evaluation
+
Infinite Iterator
+
Async Iterator
+
Typing
+
Pipeline
+
Error Handling
+
Backpressure
```

để xây một mini library theo kiểu production, có cấu trúc package, `Iterable[T]`/`Iterator[T]`, sync + async pipeline, `map`, `filter`, `take`, `batch`, retry, logging và test.
