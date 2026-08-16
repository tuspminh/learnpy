# Iterator Deep Dive — Buổi 23

# Dự án thực tế: Xây dựng Streaming Pipeline Library

Đây là **buổi cuối của khóa Iterator Deep Dive**.

Mục tiêu không còn là học thêm một API mới, mà là **ghép toàn bộ kiến thức Iterator thành một thư viện có kiến trúc thực tế**.

Chúng ta sẽ xây một mini library tên:

```text
streamkit/
```

cho phép viết:

```python
stream = (
    Stream(numbers(1, 100_000))
    .filter(lambda x: x % 2 == 0)
    .map(lambda x: x * x)
    .take(10)
)

for item in stream:
    print(item)
```

Điểm quan trọng:

> **Toàn bộ pipeline là lazy.**

Không tạo toàn bộ dữ liệu trung gian.

---

# 1. Mục tiêu dự án

Sau dự án, bạn sẽ xây được:

```text
streamkit
│
├── source
│
├── stream
│
├── operators
│   ├── map
│   ├── filter
│   ├── take
│   ├── skip
│   ├── batch
│   └── enumerate
│
├── async_stream
│
├── exceptions
│
└── tests
```

Kiến trúc:

```text
Source
  │
  ▼
Iterator
  │
  ▼
Filter
  │
  ▼
Map
  │
  ▼
Take
  │
  ▼
Consumer
```

---

# 2. Requirement

Ta muốn hỗ trợ:

```python
Stream(source)
```

và:

```python
.filter()
.map()
.take()
.skip()
.batch()
```

Ví dụ:

```python
result = (
    Stream(range(1_000_000))
    .filter(lambda x: x % 2 == 0)
    .map(lambda x: x * 10)
    .take(100)
)
```

Sau đó:

```python
for item in result:
    print(item)
```

---

# 3. Cấu trúc project

Tạo:

```text
streamkit/
│
├── pyproject.toml
│
├── src/
│   └── streamkit/
│       ├── __init__.py
│       ├── stream.py
│       ├── operators.py
│       └── sources.py
│
└── tests/
    └── test_stream.py
```

Đây là cấu trúc package Python hiện đại.

---

# 4. `sources.py`

Bắt đầu bằng source.

```python
from collections.abc import Iterator


def numbers(
    start: int,
    stop: int,
) -> Iterator[int]:

    for value in range(start, stop):
        yield value
```

Sử dụng:

```python
for number in numbers(1, 5):
    print(number)
```

Kết quả:

```text
1
2
3
4
```

Đây là Iterator lazy.

---

# 5. `operators.py`

Bây giờ viết `map`.

```python
from collections.abc import Callable, Iterable, Iterator
from typing import TypeVar


T = TypeVar("T")
U = TypeVar("U")


def map_items(
    items: Iterable[T],
    func: Callable[[T], U],
) -> Iterator[U]:

    for item in items:
        yield func(item)
```

Ví dụ:

```python
result = map_items(
    [1, 2, 3],
    lambda x: x * 2,
)

print(list(result))
```

Output:

```text
[2, 4, 6]
```

---

# 6. `filter_items`

```python
from collections.abc import Callable, Iterable, Iterator
from typing import TypeVar


T = TypeVar("T")


def filter_items(
    items: Iterable[T],
    predicate: Callable[[T], bool],
) -> Iterator[T]:

    for item in items:

        if predicate(item):
            yield item
```

Ví dụ:

```python
result = filter_items(
    range(10),
    lambda x: x % 2 == 0,
)

print(list(result))
```

Output:

```text
[0, 2, 4, 6, 8]
```

---

# 7. `take`

Operator rất quan trọng.

```python
from collections.abc import Iterable, Iterator
from typing import TypeVar


T = TypeVar("T")


def take(
    items: Iterable[T],
    count: int,
) -> Iterator[T]:

    if count < 0:
        raise ValueError("count must be >= 0")

    for index, item in enumerate(items):

        if index >= count:
            break

        yield item
```

Nhưng có một chi tiết:

Iterator phía trên có thể đã lấy dư một phần tử.

Ta sẽ cải thiện sau.

Cách đơn giản hơn:

```python
from itertools import islice


def take(
    items: Iterable[T],
    count: int,
) -> Iterator[T]:

    if count < 0:
        raise ValueError("count must be >= 0")

    yield from islice(items, count)
```

Đây là nơi kiến thức **Buổi 17 — itertools** được sử dụng.

---

# 8. `skip`

```python
from itertools import islice


def skip(
    items: Iterable[T],
    count: int,
) -> Iterator[T]:

    if count < 0:
        raise ValueError("count must be >= 0")

    yield from islice(items, count, None)
```

Ví dụ:

```python
print(
    list(
        skip(range(10), 5)
    )
)
```

Output:

```text
[5, 6, 7, 8, 9]
```

---

# 9. `batch`

Đây là operator rất hữu ích trong crawler/database.

Ta muốn:

```text
1
2
3
4
5
6
```

thành:

```text
[1, 2]
[3, 4]
[5, 6]
```

Code:

```python
from collections.abc import Iterable, Iterator
from typing import TypeVar


T = TypeVar("T")


def batch(
    items: Iterable[T],
    size: int,
) -> Iterator[list[T]]:

    if size <= 0:
        raise ValueError("size must be > 0")

    iterator = iter(items)

    while True:

        batch_items = []

        for _ in range(size):

            try:
                batch_items.append(
                    next(iterator)
                )

            except StopIteration:
                break

        if not batch_items:
            return

        yield batch_items
```

---

# 10. Test `batch`

```python
result = batch(
    range(7),
    3,
)

print(list(result))
```

Output:

```text
[
    [0, 1, 2],
    [3, 4, 5],
    [6],
]
```

Đây là một pattern cực kỳ hữu ích khi làm database.

---

# 11. `Stream`

Bây giờ đến phần quan trọng nhất.

File:

```text
stream.py
```

Code:

```python
from collections.abc import (
    Callable,
    Iterable,
    Iterator,
)
from typing import Generic, TypeVar

from .operators import (
    batch,
    filter_items,
    map_items,
    skip,
    take,
)


T = TypeVar("T")
U = TypeVar("U")
```

Class:

```python
class Stream(Generic[T]):

    def __init__(
        self,
        source: Iterable[T],
    ):
        self._source = source
```

---

# 12. `__iter__`

```python
class Stream(Generic[T]):

    def __init__(
        self,
        source: Iterable[T],
    ):
        self._source = source

    def __iter__(self) -> Iterator[T]:
        return iter(self._source)
```

Bây giờ:

```python
stream = Stream([1, 2, 3])

for item in stream:
    print(item)
```

---

# 13. `.map()`

```python
def map(
    self,
    func: Callable[[T], U],
) -> "Stream[U]":

    return Stream(
        map_items(
            self._source,
            func,
        )
    )
```

Sử dụng:

```python
stream = (
    Stream([1, 2, 3])
    .map(lambda x: x * 2)
)
```

---

# 14. `.filter()`

```python
def filter(
    self,
    predicate: Callable[[T], bool],
) -> "Stream[T]":

    return Stream(
        filter_items(
            self._source,
            predicate,
        )
    )
```

---

# 15. `.take()`

```python
def take(
    self,
    count: int,
) -> "Stream[T]":

    return Stream(
        take(
            self._source,
            count,
        )
    )
```

---

# 16. `.skip()`

```python
def skip(
    self,
    count: int,
) -> "Stream[T]":

    return Stream(
        skip(
            self._source,
            count,
        )
    )
```

---

# 17. `.batch()`

```python
def batch(
    self,
    size: int,
) -> "Stream[list[T]]":

    return Stream(
        batch(
            self._source,
            size,
        )
    )
```

Bây giờ chúng ta có:

```python
Stream(...)
    .map(...)
    .filter(...)
    .take(...)
    .skip(...)
    .batch(...)
```

---

# 18. Full `Stream`

Có thể viết:

```python
from collections.abc import (
    Callable,
    Iterable,
    Iterator,
)
from typing import Generic, TypeVar

from .operators import (
    batch,
    filter_items,
    map_items,
    skip,
    take,
)


T = TypeVar("T")
U = TypeVar("U")


class Stream(Generic[T]):

    def __init__(
        self,
        source: Iterable[T],
    ):
        self._source = source

    def __iter__(self) -> Iterator[T]:
        return iter(self._source)

    def map(
        self,
        func: Callable[[T], U],
    ) -> "Stream[U]":

        return Stream(
            map_items(
                self._source,
                func,
            )
        )

    def filter(
        self,
        predicate: Callable[[T], bool],
    ) -> "Stream[T]":

        return Stream(
            filter_items(
                self._source,
                predicate,
            )
        )

    def take(
        self,
        count: int,
    ) -> "Stream[T]":

        return Stream(
            take(
                self._source,
                count,
            )
        )

    def skip(
        self,
        count: int,
    ) -> "Stream[T]":

        return Stream(
            skip(
                self._source,
                count,
            )
        )

    def batch(
        self,
        size: int,
    ) -> "Stream[list[T]]":

        return Stream(
            batch(
                self._source,
                size,
            )
        )
```

---

# 19. Chúng ta vừa xây Fluent Iterator API

Bây giờ:

```python
stream = (
    Stream(range(1_000_000))
    .filter(lambda x: x % 2 == 0)
    .map(lambda x: x * 10)
    .take(10)
)
```

Consumer:

```python
for item in stream:
    print(item)
```

Output:

```text
0
20
40
60
80
100
120
140
160
180
```

---

# 20. Quan trọng: Chưa có computation

Khi viết:

```python
stream = (
    Stream(range(1_000_000))
    .filter(...)
    .map(...)
    .take(10)
)
```

chúng ta **chưa xử lý 1 triệu phần tử**.

Đây chính là:

> Lazy Pipeline.

---

# 21. Khi nào computation bắt đầu?

Khi:

```python
for item in stream:
    print(item)
```

hoặc:

```python
list(stream)
```

hoặc:

```python
sum(stream)
```

---

# 22. Pipeline thực sự hoạt động thế nào?

Ví dụ:

```python
Stream(range(1_000_000))
    .filter(is_even)
    .map(square)
    .take(10)
```

Không phải:

```text
range
 ↓
list filter
 ↓
list map
 ↓
list take
```

Mà:

```text
range
 ↓
filter
 ↓
map
 ↓
take
 ↓
consumer
```

Một phần tử chạy xuyên suốt pipeline.

---

# 23. Ví dụ từng bước

Nguồn:

```text
1
```

Filter:

```text
1 → bỏ
```

Nguồn:

```text
2
```

Filter:

```text
2 → giữ
```

Map:

```text
2 → 4
```

Take:

```text
4 → output
```

Tiếp tục:

```text
3 → bỏ
4 → 16
5 → bỏ
6 → 36
...
```

Đến đủ 10 phần tử thì `take()` dừng.

---

# 24. Đây là sức mạnh lớn của Lazy

Giả sử:

```python
range(1_000_000_000)
```

nhưng:

```python
.take(5)
```

Ta chỉ cần xử lý rất ít dữ liệu.

```python
stream = (
    Stream(range(1_000_000_000))
    .filter(lambda x: x % 2 == 0)
    .map(lambda x: x * x)
    .take(5)
)
```

Không cần tạo 1 tỷ phần tử trong RAM.

---

# 25. Terminal Operations

Cho đến hiện tại:

```python
map()
filter()
take()
skip()
```

là **lazy operations**.

Ta cần thêm:

```text
Terminal operations
```

Ví dụ:

```python
to_list()
count()
first()
sum()
```

---

# 26. `to_list()`

```python
def to_list(self) -> list[T]:

    return list(self._source)
```

---

# 27. `first()`

```python
def first(self) -> T:

    return next(
        iter(self._source)
    )
```

Nhưng nếu rỗng:

```python
next(iterator)
```

sẽ ném:

```text
StopIteration
```

Ta có thể thiết kế API rõ ràng hơn.

---

# 28. `first_or_none()`

```python
def first_or_none(
    self,
) -> T | None:

    return next(
        iter(self._source),
        None,
    )
```

Ví dụ:

```python
result = (
    Stream([])
    .first_or_none()
)

print(result)
```

Output:

```text
None
```

---

# 29. `count()`

```python
def count(self) -> int:

    total = 0

    for _ in self._source:
        total += 1

    return total
```

Điều này rất quan trọng:

> `count()` vẫn phải consume toàn bộ Iterator.

Không có:

```python
len(iterator)
```

---

# 30. `to_list()` và Memory

Nếu:

```python
Stream(range(10_000_000)).to_list()
```

thì chúng ta **cố ý materialize**.

Đây là hành vi hợp lệ.

API nên cho phép consumer quyết định:

```text
Lazy
  ↓
Stream

Eager
  ↓
to_list()
```

---

# 31. Thêm `reduce`

Có thể dùng:

```python
from functools import reduce
```

Ví dụ:

```python
def reduce(
    self,
    func,
    initial=None,
):
    ...
```

Nhưng không nhất thiết phải thêm mọi thứ vào Stream.

Một library tốt phải biết giới hạn abstraction.

---

# 32. Async Stream

Đây là phần nâng cao.

Ta muốn:

```python
async for item in stream:
    ...
```

Định nghĩa:

```python
from collections.abc import AsyncIterable, AsyncIterator


class AsyncStream:

    def __init__(
        self,
        source: AsyncIterable[T],
    ):
        self._source = source

    def __aiter__(
        self,
    ) -> AsyncIterator[T]:

        return self._source.__aiter__()
```

---

# 33. Async `map`

```python
from collections.abc import (
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Callable,
)


async def async_map(
    items: AsyncIterable[T],
    func: Callable[[T], Awaitable[U]],
) -> AsyncIterator[U]:

    async for item in items:
        yield await func(item)
```

---

# 34. Async `filter`

```python
async def async_filter(
    items: AsyncIterable[T],
    predicate: Callable[[T], Awaitable[bool]],
) -> AsyncIterator[T]:

    async for item in items:

        if await predicate(item):
            yield item
```

---

# 35. Async Pipeline

Ví dụ:

```python
stream = AsyncStream(
    crawl_urls()
)
```

Sau đó:

```python
stream = stream.map(fetch)
```

```python
stream = stream.filter(valid)
```

Consumer:

```python
async for page in stream:
    await save(page)
```

Đây chính là architecture crawler rất thực tế.

---

# 36. Error Handling

Một pipeline thực tế không thể chỉ có:

```python
map()
filter()
```

Network có thể lỗi:

```text
Timeout
ConnectionError
HTTP 500
Rate Limit
Invalid Response
```

Ta cần:

```python
retry()
```

---

# 37. Retry Operator

Ví dụ:

```python
def retry_map(
    items,
    func,
    attempts=3,
):
    for item in items:

        for attempt in range(attempts):

            try:
                yield func(item)
                break

            except Exception:

                if attempt == attempts - 1:
                    raise
```

Sử dụng:

```python
stream = (
    Stream(urls)
    .retry_map(fetch_page)
)
```

---

# 38. Nhưng retry có một vấn đề

Nếu:

```python
fetch_page(url)
```

có side effect:

```text
POST
DB INSERT
File write
```

retry có thể gây:

```text
duplicate operation
```

Do đó retry phải phụ thuộc semantics của operation.

Đây là lý do:

> **Không nên biến mọi thứ thành một generic retry decorator mà không hiểu side effect.**

---

# 39. Logging Operator

Ta có thể thêm:

```python
def tap(
    items,
    func,
):
    for item in items:
        func(item)
        yield item
```

Ví dụ:

```python
stream = (
    Stream(urls)
    .tap(lambda x: print("URL:", x))
    .map(fetch)
)
```

`tap()` không thay đổi dữ liệu.

Nó chỉ quan sát pipeline.

---

# 40. Metrics

Có thể mở rộng:

```python
stream = (
    Stream(urls)
    .count_metrics("download")
    .map(fetch)
)
```

Ví dụ đo:

```text
items processed
items failed
processing time
throughput
```

Đây là nền tảng cho monitoring crawler.

---

# 41. Backpressure

Sync Iterator tự nhiên có một dạng backpressure:

```python
for item in stream:
    process(item)
```

Source chỉ tạo item tiếp theo khi consumer yêu cầu:

```text
consumer
   │
   │ next()
   ▼
source
```

Nếu consumer chậm:

```text
next()
   ↓
source chờ
```

Source không cần tạo hàng triệu item trước.

---

# 42. Async Pipeline

Với Async Iterator:

```text
Producer
   ↓
AsyncIterator
   ↓
Consumer
```

Nếu muốn nhiều worker:

```text
Producer
   ↓
Queue
 ┌─┼─┐
 ▼ ▼ ▼
W1 W2 W3
```

Lúc này Queue chịu trách nhiệm backpressure.

---

# 43. Batch + Repository

Đây là một pattern rất hữu ích cho crawler.

```python
stream = (
    Stream(chapters)
    .filter(valid)
    .batch(100)
)
```

Sau đó:

```python
for batch in stream:
    repository.save_many(batch)
```

Thay vì:

```python
for chapter in chapters:
    repository.save(chapter)
```

Ta có:

```text
100 chapters
    ↓
1 database transaction
```

Có thể tăng throughput đáng kể.

---

# 44. Architecture thực tế

Một crawler pipeline có thể:

```text
URL Source
    │
    ▼
Iterator
    │
    ▼
Download
    │
    ▼
Parse
    │
    ▼
Validate
    │
    ▼
Transform
    │
    ▼
Batch(100)
    │
    ▼
Repository
```

Đây chính là lý do Iterator cực kỳ hữu ích trong hệ thống crawler.

---

# 45. Testing Pipeline

Test:

```python
def test_pipeline():

    result = (
        Stream(range(10))
        .filter(lambda x: x % 2 == 0)
        .map(lambda x: x * 10)
        .take(3)
        .to_list()
    )

    assert result == [
        0,
        20,
        40,
    ]
```

---

# 46. Test Lazy

Một test rất quan trọng:

```python
def source():

    print("source started")

    yield 1
    yield 2
```

Tạo:

```python
stream = Stream(source())
```

Không được chạy source ngay.

Chỉ khi:

```python
list(stream)
```

mới bắt đầu.

---

# 47. Test Infinite Iterator

```python
from itertools import count


stream = (
    Stream(count())
    .map(lambda x: x * 2)
    .take(5)
)

assert stream.to_list() == [
    0,
    2,
    4,
    6,
    8,
]
```

Đây là một bài test cực hay vì chứng minh:

> Pipeline lazy có thể xử lý infinite source.

---

# 48. Test Memory

Ta có thể dùng:

```python
import tracemalloc
```

Ví dụ:

```python
tracemalloc.start()

stream = (
    Stream(range(1_000_000))
    .map(lambda x: x * 2)
    .filter(lambda x: x % 3 == 0)
    .take(100)
)

result = stream.to_list()

current, peak = tracemalloc.get_traced_memory()

tracemalloc.stop()

print("Peak:", peak)
```

---

# 49. Type Checking

Một library production nên hỗ trợ:

```python
Stream[int]
Stream[str]
Stream[Book]
```

Ví dụ:

```python
numbers: Stream[int]
```

Sau:

```python
strings = numbers.map(str)
```

Type checker có thể suy luận:

```text
Stream[int]
    ↓ map(str)
Stream[str]
```

Đây là lý do chúng ta sử dụng:

```python
TypeVar
Generic
Callable
Iterable
Iterator
```

---

# 50. Một API hoàn chỉnh

Sau khi hoàn thiện, API có thể trông như:

```python
stream = (
    Stream(source)
    .map(func)
    .filter(predicate)
    .skip(10)
    .take(100)
    .batch(20)
)
```

Terminal:

```python
stream.to_list()
stream.count()
stream.first()
stream.first_or_none()
```

---

# 51. Mental Model cuối cùng

Hãy nhìn:

```python
Stream(source)
    .filter(...)
    .map(...)
    .take(...)
```

không phải là:

```text
data structure
```

mà là:

```text
computation description
```

Nó mô tả:

> "Khi consumer yêu cầu dữ liệu, hãy lấy source → filter → map → take."

Đây là tư duy **deferred computation**.

---

# 52. Iterator là một abstraction cực mạnh

Ban đầu bạn học:

```python
iter()
next()
```

Có vẻ rất đơn giản.

Nhưng từ đó có thể xây:

```text
Iterator
   ↓
Generator
   ↓
Lazy Pipeline
   ↓
Streaming API
   ↓
Database Cursor
   ↓
File Processing
   ↓
Crawler
   ↓
Async Stream
   ↓
Data Processing Framework
```

---

# 53. Toàn bộ khóa học Iterator

Chúng ta đã đi qua:

```text
Phần I — Foundation
```

* Iterable
* Iterator
* `iter()`
* `next()`
* Iterator Protocol

```text
Phần II — Tự xây Iterator
```

* Custom Iterator
* File Iterator
* Tree Iterator
* Linked List Iterator
* Infinite Iterator
* Reset Iterator

```text
Phần III — Generator
```

* Generator
* `yield`
* `yield from`
* Generator Expression

```text
Phần IV — Advanced
```

* `itertools`
* Lazy Evaluation
* Infinite Iterator
* Async Iterator
* Performance
* Library Design
* Real Project

---

# 54. Bản chất của Iterator

Nếu phải rút toàn bộ khóa học thành một câu:

> **Iterator là một abstraction cho phép consumer lấy dữ liệu từng bước thay vì buộc producer phải tạo toàn bộ dữ liệu trước.**

Và từ đó xuất hiện:

```text
Lazy
Streaming
Composable
Memory efficient
Backpressure
```

---

# 55. Checklist sau khóa học

Bạn nên tự trả lời được các câu hỏi sau.

### Cơ bản

* Iterable là gì?
* Iterator là gì?
* `iter()` làm gì?
* `next()` làm gì?
* `StopIteration` là gì?

### Custom Iterator

* Viết `__iter__()` thế nào?
* Viết `__next__()` thế nào?
* Khi nào `__iter__()` trả `self`?
* Khi nào nên tạo Iterator riêng?

### Generator

* Generator khác Iterator class thế nào?
* `yield` hoạt động thế nào?
* Generator frame là gì?
* `yield from` dùng khi nào?

### Advanced

* Lazy evaluation là gì?
* Infinite iterator xử lý thế nào?
* Async Iterator khác Iterator thế nào?
* `itertools` giúp gì?

### Performance

* Iterator tiết kiệm memory vì sao?
* Khi nào List nhanh hơn?
* Khi nào Generator nhanh hơn?
* Random access ảnh hưởng thế nào?

### Library Design

* Khi nào dùng `Iterable[T]`?
* Khi nào dùng `Iterator[T]`?
* Khi nào dùng `AsyncIterator[T]`?
* Làm sao thiết kế streaming API?
* Khi nào materialize?
* Làm sao thiết kế pipeline?

Nếu bạn trả lời được những câu này và tự viết lại `Stream` ở trên mà không nhìn code, thì bạn đã nắm Iterator ở mức khá sâu.

---

# 56. Bài tập tốt nghiệp

Hãy tự xây phiên bản `streamkit` hoàn chỉnh với API:

```python
Stream(source)
    .map(...)
    .filter(...)
    .flat_map(...)
    .skip(...)
    .take(...)
    .batch(...)
    .tap(...)
    .distinct()
```

và terminal:

```python
.to_list()
.first()
.first_or_none()
.count()
```

Yêu cầu:

```text
1. Lazy hoàn toàn
2. Generic typing
3. Không tạo intermediate List
4. Hỗ trợ infinite iterator
5. Có unit test
6. Benchmark memory
7. Benchmark performance
8. Có documentation
9. Có sync API
10. Có async API
```

Đây là project đủ tốt để chuyển sang kiến trúc **data pipeline / crawler pipeline** thực tế.

---

## Kết thúc Iterator Deep Dive

Điểm quan trọng nhất cần giữ lại:

```text
Iterable
   │
   │ iter()
   ▼
Iterator
   │
   │ next()
   ▼
value
```

và:

```text
Iterator
    ↓
Generator
    ↓
Lazy Evaluation
    ↓
Pipeline
    ↓
Streaming
    ↓
Production Architecture
```

**Iterator không chỉ là một tính năng của vòng `for`; nó là một abstraction để thiết kế hệ thống xử lý dữ liệu theo dòng.**

Với các dự án crawler/worker của bạn, tư duy này đặc biệt hữu ích ở các lớp **crawler source → parser → validator → batch → repository**, nơi không nên materialize toàn bộ dữ liệu vào RAM.
