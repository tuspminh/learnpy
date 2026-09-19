# Buổi 38 — URL Deduplication

Ở Buổi 37 chúng ta đã có:

```text
URL
 ↓
Normalization
 ↓
Comparison
```

Bây giờ chúng ta giải quyết bài toán thực tế:

> Crawler lấy được hàng nghìn URL từ nhiều trang khác nhau. Làm sao đảm bảo cùng một URL không bị crawl nhiều lần?

Đây chính là **URL deduplication**.

---

# 1. Deduplication là gì?

Ví dụ parser thu được:

```python
urls = [
    URL("https://example.com/chapter-1"),
    URL("https://example.com/chapter-2"),
    URL("https://example.com/chapter-1"),
    URL("https://example.com/chapter-3"),
    URL("https://example.com/chapter-2"),
]
```

Ta muốn:

```text
chapter-1
chapter-2
chapter-3
```

thay vì:

```text
chapter-1
chapter-2
chapter-1
chapter-3
chapter-2
```

---

# 2. Cách đơn giản nhất: `set`

Vì `yarl.URL` có thể dùng làm phần tử của `set`:

```python
from yarl import URL


urls = [
    URL("https://example.com/chapter-1"),
    URL("https://example.com/chapter-2"),
    URL("https://example.com/chapter-1"),
]

unique_urls = set(urls)

for url in unique_urls:
    print(url)
```

Kết quả chỉ còn các URL khác nhau.

Đây là cách cơ bản nhất.

---

# 3. Nhưng có một vấn đề

Nhớ Buổi 36:

```text
https://example.com/chapter-1#top
https://example.com/chapter-1#content
```

về raw URL là khác nhau.

Do đó:

```python
from yarl import URL


a = URL("https://example.com/chapter-1#top")
b = URL("https://example.com/chapter-1#content")

print(a == b)
```

→ `False`.

Nếu làm:

```python
urls = {a, b}
```

ta vẫn có **2 URL**.

Trong crawler, nếu policy của chúng ta bỏ fragment thì điều này không mong muốn.

---

# 4. Normalize trước khi deduplicate

Đây là nguyên tắc quan trọng nhất của bài:

```text
Raw URL
   ↓
Normalize
   ↓
Deduplicate
```

Không phải:

```text
Raw URL
   ↓
Deduplicate
   ↓
Normalize
```

Ví dụ:

```python
from yarl import URL


def normalize_url(url: URL) -> URL:
    return url.with_fragment(None)


urls = [
    URL("https://example.com/chapter-1#top"),
    URL("https://example.com/chapter-1#content"),
    URL("https://example.com/chapter-2"),
]

unique_urls = {
    normalize_url(url)
    for url in urls
}

for url in unique_urls:
    print(url)
```

Ta sẽ còn:

```text
https://example.com/chapter-1
https://example.com/chapter-2
```

---

# 5. Vì sao `set` rất phù hợp?

Cấu trúc:

```python
seen: set[URL]
```

cho phép kiểm tra:

```python
if url in seen:
    ...
```

Ví dụ:

```python
from yarl import URL


seen: set[URL] = set()

urls = [
    URL("https://example.com/chapter-1"),
    URL("https://example.com/chapter-2"),
    URL("https://example.com/chapter-1"),
]

for url in urls:
    if url in seen:
        print("Duplicate:", url)
        continue

    seen.add(url)
    print("New:", url)
```

Kết quả:

```text
New: https://example.com/chapter-1
New: https://example.com/chapter-2
Duplicate: https://example.com/chapter-1
```

Đây chính là pattern cực kỳ phổ biến trong crawler.

---

# 6. `seen` là gì?

Trong crawler:

```python
seen: set[URL]
```

thường được gọi là:

```text
visited
seen
discovered
known_urls
```

Ý nghĩa có thể hơi khác nhau tùy architecture.

Ví dụ:

### `seen`

URL đã từng được phát hiện.

```text
Parser → seen
```

### `visited`

URL đã thực sự được fetch.

```text
Queue → Fetcher → visited
```

### `queued`

URL đã được đưa vào queue.

Đừng trộn các khái niệm này nếu crawler của bạn cần tracking trạng thái chi tiết.

---

# 7. Deduplicator đơn giản

Ta có thể viết:

```python
from yarl import URL


class URLDeduplicator:

    def __init__(self):
        self._seen: set[URL] = set()

    def add(self, url: URL) -> bool:
        if url in self._seen:
            return False

        self._seen.add(url)
        return True

    def contains(self, url: URL) -> bool:
        return url in self._seen
```

Sử dụng:

```python
deduplicator = URLDeduplicator()

url = URL("https://example.com/chapter-1")

print(deduplicator.add(url))
print(deduplicator.add(url))
```

Kết quả:

```text
True
False
```

Ý nghĩa:

```text
True
```

→ URL mới.

```text
False
```

→ URL đã tồn tại.

---

# 8. Nhưng class trên còn thiếu normalization

Nếu:

```python
a = URL("https://example.com/chapter-1#top")
b = URL("https://example.com/chapter-1#content")
```

thì:

```python
deduplicator.add(a)
deduplicator.add(b)
```

sẽ trả:

```text
True
True
```

Không đúng với policy crawler của chúng ta.

Do đó:

```python
class URLDeduplicator:

    def __init__(self):
        self._seen: set[URL] = set()

    def add(self, url: URL) -> bool:
        normalized = normalize_url(url)

        if normalized in self._seen:
            return False

        self._seen.add(normalized)
        return True
```

---

# 9. Phiên bản hoàn chỉnh đầu tiên

```python
from yarl import URL


def normalize_url(url: URL) -> URL:
    return url.with_fragment(None)


class URLDeduplicator:

    def __init__(self):
        self._seen: set[URL] = set()

    def add(self, url: URL) -> bool:
        normalized = normalize_url(url)

        if normalized in self._seen:
            return False

        self._seen.add(normalized)
        return True

    def contains(self, url: URL) -> bool:
        normalized = normalize_url(url)
        return normalized in self._seen

    def __len__(self) -> int:
        return len(self._seen)
```

Test:

```python
deduplicator = URLDeduplicator()

urls = [
    URL("https://example.com/chapter-1#top"),
    URL("https://example.com/chapter-1#content"),
    URL("https://example.com/chapter-1"),
    URL("https://example.com/chapter-2"),
]

for url in urls:
    added = deduplicator.add(url)

    print(
        f"{'NEW' if added else 'DUPLICATE':10} {url}"
    )

print("Total:", len(deduplicator))
```

Kết quả:

```text
NEW        https://example.com/chapter-1#top
DUPLICATE  https://example.com/chapter-1#content
DUPLICATE  https://example.com/chapter-1
NEW        https://example.com/chapter-2
Total: 2
```

---

# 10. Tại sao `add()` trả về `bool` rất tiện?

Thay vì:

```python
if not deduplicator.contains(url):
    deduplicator.add(url)
    queue.put(url)
```

ta có thể:

```python
if deduplicator.add(url):
    queue.put(url)
```

Code crawler trở nên rất rõ:

```text
phát hiện URL
     ↓
deduplicator.add()
     │
     ├── True  → URL mới → Queue
     │
     └── False → bỏ qua
```

---

# 11. Đây là nơi deduplication thực sự xảy ra

Ví dụ parser:

```python
chapter_urls = parse_chapter_links(
    page_url,
    html,
)
```

Parser trả:

```python
[
    URL("https://site.com/chapter-1"),
    URL("https://site.com/chapter-2"),
    URL("https://site.com/chapter-1"),
]
```

Crawler:

```python
for url in chapter_urls:
    if deduplicator.add(url):
        queue.put(url)
```

Parser **không cần biết** URL đã được crawl chưa.

Đây là separation of concerns rất tốt.

---

# 12. Deduplication giữa nhiều trang

Đây mới là trường hợp thực tế của Novel Crawler.

Giả sử:

```text
Trang listing 1
    ↓
chapter-1
chapter-2
chapter-3

Trang listing 2
    ↓
chapter-3
chapter-4
chapter-5

Trang listing 3
    ↓
chapter-5
chapter-6
chapter-7
```

Nếu mỗi parser tự dedup:

```text
Listing 1 → local set
Listing 2 → local set
Listing 3 → local set
```

thì vẫn có duplicate giữa các trang.

Cần một `URLDeduplicator` dùng chung:

```text
                   ┌── Listing 1
                   │
                   ├── Listing 2
Parser ────────────┼── Listing 3
                   │
                   └── Novel page
                          │
                          ▼
                  URLDeduplicator
                          │
                          ▼
                       Queue
```

---

# 13. Ví dụ thực tế

```python
from yarl import URL


deduplicator = URLDeduplicator()

page_1 = [
    URL("https://site.com/chapter-1"),
    URL("https://site.com/chapter-2"),
    URL("https://site.com/chapter-3"),
]

page_2 = [
    URL("https://site.com/chapter-3"),
    URL("https://site.com/chapter-4"),
    URL("https://site.com/chapter-5"),
]

page_3 = [
    URL("https://site.com/chapter-5"),
    URL("https://site.com/chapter-6"),
]

for page_urls in [page_1, page_2, page_3]:

    for url in page_urls:

        if deduplicator.add(url):
            print("QUEUE:", url)
        else:
            print("SKIP :", url)
```

Kết quả:

```text
QUEUE: https://site.com/chapter-1
QUEUE: https://site.com/chapter-2
QUEUE: https://site.com/chapter-3

SKIP : https://site.com/chapter-3
QUEUE: https://site.com/chapter-4
QUEUE: https://site.com/chapter-5

SKIP : https://site.com/chapter-5
QUEUE: https://site.com/chapter-6
```

Đây chính là behavior mà crawler framework cần.

---

# 14. Deduplication với `set` có hiệu năng tốt

Nếu có:

```python
seen: set[URL]
```

thì:

```python
url in seen
```

thường có độ phức tạp trung bình:

```text
O(1)
```

Trong khi nếu dùng list:

```python
seen: list[URL]
```

và:

```python
if url in seen:
```

thì phải tìm tuần tự:

```text
O(n)
```

Với crawler hàng trăm nghìn URL, sự khác biệt rất đáng kể.

---

# 15. Sai lầm: dùng list để dedup

Không nên:

```python
seen = []

for url in urls:
    if url not in seen:
        seen.append(url)
```

Nếu:

```text
100,000 URLs
```

thì việc tìm kiếm trong list sẽ ngày càng tốn thời gian.

Thay vào đó:

```python
seen: set[URL] = set()
```

---

# 16. Nhưng `set` không giữ thứ tự

Ví dụ:

```python
urls = {
    URL("https://site.com/chapter-1"),
    URL("https://site.com/chapter-2"),
    URL("https://site.com/chapter-3"),
}
```

Không nên dựa vào thứ tự iteration của set để quyết định thứ tự crawl.

Nếu crawler cần:

```text
discovery order
```

thì queue nên chịu trách nhiệm về thứ tự.

Ví dụ:

```text
Deduplicator
     ↓
Queue
     ↓
Worker
```

---

# 17. Deduplication và Queue là hai responsibility khác nhau

Không nên biến:

```python
URLDeduplicator
```

thành:

```text
dedup
queue
retry
priority
worker
```

Một design sạch:

```text
URLDeduplicator
        │
        │ accepted?
        ▼
      Queue
        │
        ▼
      Worker
```

Ví dụ:

```python
if deduplicator.add(url):
    queue.put(url)
```

Rất rõ ràng.

---

# 18. `seen` trước hay sau Queue?

Đây là một câu hỏi architecture rất quan trọng.

Thông thường với crawler:

```text
discover
   ↓
normalize
   ↓
deduplicate
   ↓
queue
```

Tức là đánh dấu URL ngay khi **discovered/queued**.

Ví dụ:

```python
if deduplicator.add(url):
    queue.put(url)
```

Như vậy nếu cùng URL xuất hiện 10 lần trước khi worker xử lý:

```text
URL A
URL A
URL A
URL A
...
```

chỉ một lần được đưa vào queue.

---

# 19. Nhưng `seen` không phải `visited`

Điều này rất quan trọng.

Ví dụ:

```text
seen
```

có nghĩa:

```text
URL đã được phát hiện
```

Còn:

```text
visited
```

có thể có nghĩa:

```text
URL đã được fetch
```

Có thể xảy ra:

```text
seen = True
visited = False
```

khi URL đã nằm trong queue nhưng worker chưa xử lý.

---

# 20. Production crawler thường cần nhiều trạng thái hơn

Sau này architecture có thể là:

```text
DISCOVERED
     ↓
QUEUED
     ↓
FETCHING
     ↓
SUCCESS
```

hoặc:

```text
FAILED
   ↓
RETRY
   ↓
FETCHING
```

Lúc đó một `set[URL]` đơn giản có thể chưa đủ.

Có thể cần:

```python
dict[URL, CrawlState]
```

nhưng **chưa cần làm ở bài này**.

Hiện tại:

```python
set[URL]
```

là abstraction phù hợp.

---

# 21. Deduplication phải dùng normalized URL

Đây là lỗi rất dễ mắc.

Sai:

```python
seen.add(url)

normalized = normalize_url(url)

if normalized in seen:
    ...
```

Đúng:

```python
normalized = normalize_url(url)

if normalized in seen:
    return False

seen.add(normalized)
```

Tức là:

```text
          URL
           │
           ▼
      normalize
           │
           ▼
      normalized
           │
           ▼
          set
```

Không phải:

```text
URL → set → normalize
```

---

# 22. Tách `normalize` khỏi `deduplicate`

Đừng viết:

```python
class URLDeduplicator:
    # 300 dòng normalization logic
```

Tốt hơn:

```python
def normalize_url(url: URL) -> URL:
    ...
```

và:

```python
class URLDeduplicator:
    ...
```

Deduplicator chỉ quan tâm:

> URL này đã xuất hiện chưa?

Normalization chịu trách nhiệm:

> URL này nên được biểu diễn như thế nào?

---

# 23. Một phiên bản tốt hơn

Ta có thể truyền normalization function:

```python
from collections.abc import Callable
from yarl import URL


class URLDeduplicator:

    def __init__(
        self,
        normalizer: Callable[[URL], URL],
    ):
        self._normalizer = normalizer
        self._seen: set[URL] = set()

    def add(self, url: URL) -> bool:
        normalized = self._normalizer(url)

        if normalized in self._seen:
            return False

        self._seen.add(normalized)
        return True

    def contains(self, url: URL) -> bool:
        normalized = self._normalizer(url)
        return normalized in self._seen

    def __len__(self) -> int:
        return len(self._seen)
```

Sử dụng:

```python
def normalize_url(url: URL) -> URL:
    return url.with_fragment(None)


deduplicator = URLDeduplicator(
    normalizer=normalize_url
)
```

Đây là **Dependency Injection**.

---

# 24. Nhưng có nên dùng abstraction này ngay?

Với project của bạn:

**Có thể**, nhưng chưa bắt buộc.

Nếu hiện tại chỉ có:

```python
normalize_url()
```

thì:

```python
class URLDeduplicator:
```

gọi trực tiếp:

```python
normalize_url(url)
```

là đơn giản hơn.

Khi plugin/site có normalization policy khác nhau, DI mới có giá trị.

Đây là nguyên tắc:

> **Không abstraction trước khi có variation thực tế.**

---

# 25. Novel Crawler hoàn chỉnh hơn

Một flow đơn giản:

```python
from yarl import URL


def normalize_url(url: URL) -> URL:
    return url.with_fragment(None)


class URLDeduplicator:

    def __init__(self):
        self._seen: set[URL] = set()

    def add(self, url: URL) -> bool:
        url = normalize_url(url)

        if url in self._seen:
            return False

        self._seen.add(url)
        return True
```

Crawler:

```python
deduplicator = URLDeduplicator()

for chapter_url in chapter_urls:

    if not deduplicator.add(chapter_url):
        continue

    queue.put(chapter_url)
```

Architecture:

```text
selectolax
    │
    │ extract href
    ▼
yarl.URL
    │
    ▼
normalize_url()
    │
    ▼
URLDeduplicator
    │
    ├── duplicate → discard
    │
    └── new
         │
         ▼
       Queue
```

---

# 26. Deduplication giữa nhiều loại URL

Trong Novel Crawler, bạn sẽ có:

```text
Novel URL
Chapter URL
Image URL
Pagination URL
```

Không nhất thiết tất cả dùng cùng một deduplication policy.

Ví dụ:

```text
Novel URL
    ↓
NovelDeduplicator

Chapter URL
    ↓
ChapterDeduplicator

Image URL
    ↓
ImageDeduplicator
```

Nhưng ở framework level, có thể dùng một abstraction chung:

```python
set[URL]
```

và policy quyết định normalization.

---

# 27. Deduplication Image URL

Ví dụ chapter chứa:

```html
<img src="/images/page-1.jpg">
<img src="/images/page-1.jpg#x">
<img src="https://cdn.example.com/images/page-1.jpg">
```

Sau resolution/normalization:

```text
/images/page-1.jpg
/images/page-1.jpg
https://cdn.example.com/images/page-1.jpg
```

Có thể dedup:

```text
page-1.jpg
```

nhưng CDN URL vẫn khác host:

```text
example.com
```

vs:

```text
cdn.example.com
```

Không được tự coi chúng là cùng URL chỉ vì filename giống nhau.

---

# 28. Deduplication không phải canonicalization

Ví dụ:

```text
https://example.com/chapter-1
```

và:

```text
https://www.example.com/chapter-1
```

Có thể website coi một URL là canonical và URL kia redirect.

Nhưng deduplicator không nên tự suy đoán:

```text
www.example.com == example.com
```

Đây là nhiệm vụ của:

**Buổi 39 — Canonical URL.**

---

# 29. Test đầy đủ

```python
from yarl import URL


def normalize_url(url: URL) -> URL:
    return url.with_fragment(None)


class URLDeduplicator:

    def __init__(self):
        self._seen: set[URL] = set()

    def add(self, url: URL) -> bool:
        normalized = normalize_url(url)

        if normalized in self._seen:
            return False

        self._seen.add(normalized)
        return True

    def contains(self, url: URL) -> bool:
        return normalize_url(url) in self._seen

    def __len__(self) -> int:
        return len(self._seen)


def test_duplicate_exact_url():
    dedup = URLDeduplicator()

    url = URL("https://example.com/chapter-1")

    assert dedup.add(url) is True
    assert dedup.add(url) is False


def test_duplicate_fragment():
    dedup = URLDeduplicator()

    a = URL("https://example.com/chapter-1#top")
    b = URL("https://example.com/chapter-1#content")

    assert dedup.add(a) is True
    assert dedup.add(b) is False


def test_different_chapters():
    dedup = URLDeduplicator()

    a = URL("https://example.com/chapter-1")
    b = URL("https://example.com/chapter-2")

    assert dedup.add(a) is True
    assert dedup.add(b) is True


def test_contains():
    dedup = URLDeduplicator()

    url = URL("https://example.com/chapter-1")

    dedup.add(url)

    assert dedup.contains(url)


def test_length():
    dedup = URLDeduplicator()

    dedup.add(URL("https://example.com/chapter-1"))
    dedup.add(URL("https://example.com/chapter-1#top"))
    dedup.add(URL("https://example.com/chapter-2"))

    assert len(dedup) == 2
```

Chạy:

```bash
pytest -v
```

---

# 30. Pattern quan trọng nhất của Buổi 38

Bạn nên ghi nhớ pattern này:

```python
normalized = normalize_url(url)

if normalized in seen:
    return

seen.add(normalized)

queue.put(normalized)
```

Hoặc đóng gói:

```python
if deduplicator.add(url):
    queue.put(url)
```

Đây là pattern cực kỳ hữu ích trong crawler.

---

# 31. Toàn bộ pipeline đến hiện tại

Chúng ta đã đi từ:

### Buổi 31

```text
Relative URL
     ↓
Absolute URL
```

### Buổi 32

```text
<a href>
     ↓
URL
```

### Buổi 33

```text
Pagination
     ↓
Next URL
```

### Buổi 34

```text
Chapter link
     ↓
Chapter URL
```

### Buổi 35

```text
<img src>
     ↓
Image URL
```

### Buổi 36

```text
URL
 ↓
Normalization
```

### Buổi 37

```text
URL A
   ↕
Comparison
   ↕
URL B
```

### Buổi 38

```text
URLs
 ↓
Normalize
 ↓
Deduplicate
 ↓
Queue
```

Toàn bộ:

```text
                 HTML
                   │
                   ▼
              selectolax
                   │
             href / src
                   │
                   ▼
                yarl.URL
                   │
                   ▼
              URL Resolver
                   │
                   ▼
             URL Normalizer
                   │
                   ▼
           URL Deduplicator
                   │
            ┌──────┴──────┐
            │             │
        duplicate        new
            │             │
          discard         ▼
                       Queue
                         │
                         ▼
                       Fetcher
```

---

# 32. Bài tập thực hành

Hãy tự viết:

```python
class URLDeduplicator:
    ...
```

với API:

```python
dedup = URLDeduplicator()

dedup.add(url)       # True nếu URL mới
dedup.add(url)       # False nếu duplicate

dedup.contains(url)  # True / False

len(dedup)           # số URL duy nhất
```

Input:

```python
urls = [
    URL("https://site.com/chapter-1#top"),
    URL("https://site.com/chapter-1#content"),
    URL("https://site.com/chapter-2"),
    URL("https://site.com/chapter-1"),
    URL("https://site.com/chapter-3"),
    URL("https://site.com/chapter-2#top"),
]
```

Expected:

```text
NEW        chapter-1#top
DUPLICATE  chapter-1#content
NEW        chapter-2
DUPLICATE  chapter-1
NEW        chapter-3
DUPLICATE  chapter-2#top
```

và:

```python
len(dedup) == 3
```

---

## Tư duy kiến trúc cần nhớ

Đừng để `URLDeduplicator` làm tất cả mọi việc:

```text
❌ Parser
❌ Fetcher
❌ Queue
❌ HTTP
❌ Database
```

Nó chỉ cần làm đúng một việc:

```text
URL
 ↓
normalized identity
 ↓
đã thấy chưa?
```

Sau bài này, mảnh ghép còn thiếu là **Canonical URL**. Ở **Buổi 39**, chúng ta sẽ xử lý trường hợp website tự khai báo URL chuẩn bằng:

```html
<link rel="canonical" href="...">
```

và phân biệt rất rõ:

```text
Normalization
vs
Deduplication
vs
Canonicalization
```

để tránh biến `canonical URL` thành một phiên bản deduplication "thông minh quá mức".
