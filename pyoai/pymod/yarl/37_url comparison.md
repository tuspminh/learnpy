# Buổi 37 — URL Comparison

Ở **Buổi 36**, chúng ta đã học:

```text
Raw URL
   ↓
Resolver
   ↓
Normalizer
```

Bây giờ đến bước tiếp theo:

> **Làm thế nào xác định hai URL có được xem là cùng một URL hay không?**

Đây là nền tảng trực tiếp cho **deduplication ở Buổi 38**.

---

# 1. Hai URL có giống nhau không?

Ví dụ:

```python
from yarl import URL

a = URL("https://example.com/chapter-1")
b = URL("https://example.com/chapter-1")

print(a == b)
```

Kết quả:

```text
True
```

Yarl cho phép so sánh trực tiếp:

```python
a == b
```

---

# 2. URL khác string

Ví dụ:

```python
url = URL("https://example.com/chapter-1")

print(url == "https://example.com/chapter-1")
```

Không nên thiết kế logic crawler dựa vào việc so sánh lẫn lộn:

```python
URL == str
```

Hãy thống nhất:

```text
Application
    ↓
yarl.URL
    ↓
comparison
```

Tức là:

```python
a == b
```

trong đó cả hai đều là:

```python
URL
```

---

# 3. Fragment làm hai URL khác nhau

Ví dụ:

```python
from yarl import URL

a = URL("https://example.com/chapter-1#top")
b = URL("https://example.com/chapter-1#comments")

print(a == b)
```

Kết quả:

```text
False
```

Vì về mặt URL representation:

```text
#top
```

khác:

```text
#comments
```

Nhưng crawler lại thường không quan tâm fragment.

Do đó:

```python
a_normalized = a.with_fragment(None)
b_normalized = b.with_fragment(None)

print(a_normalized == b_normalized)
```

Kết quả:

```text
True
```

Đây chính là lý do Buổi 36 có:

```python
def normalize_url(url: URL) -> URL:
    return url.with_fragment(None)
```

---

# 4. So sánh raw URL và normalized URL

Ta có:

```text
A:
https://example.com/chapter-1#top

B:
https://example.com/chapter-1#content
```

So sánh trực tiếp:

```python
a == b
```

→ `False`

So sánh sau normalization:

```python
normalize_url(a) == normalize_url(b)
```

→ `True`

Có thể viết:

```python
from yarl import URL


def normalize_url(url: URL) -> URL:
    return url.with_fragment(None)


def same_url(a: URL, b: URL) -> bool:
    return normalize_url(a) == normalize_url(b)
```

Test:

```python
a = URL("https://example.com/chapter-1#top")
b = URL("https://example.com/chapter-1#content")

print(same_url(a, b))
```

Kết quả:

```text
True
```

---

# 5. Đây là một abstraction rất hữu ích

Ta có:

```python
def same_url(a: URL, b: URL) -> bool:
    return normalize_url(a) == normalize_url(b)
```

Nhưng cần hiểu:

> `same_url()` không có nghĩa là "hai URL chắc chắn trỏ tới cùng resource trong mọi trường hợp".

Nó có nghĩa:

> **Hai URL được xem là tương đương theo normalization policy hiện tại.**

Đây là distinction rất quan trọng.

---

# 6. `/novel` và `/novel/`

Ví dụ:

```python
from yarl import URL

a = URL("https://example.com/novel")
b = URL("https://example.com/novel/")

print(a == b)
```

Kết quả:

```text
False
```

Yarl không tự nói:

```text
/novel == /novel/
```

Và crawler cũng **không nên tự quyết định** chúng giống nhau.

Có thể:

```text
/novel
```

redirect tới:

```text
/novel/
```

nhưng cũng có thể là hai endpoint khác nhau.

---

# 7. Nếu website xác định chúng tương đương

Khi đó ta có thể đưa rule vào normalization policy.

Ví dụ:

```python
from yarl import URL


def normalize_url(url: URL) -> URL:
    url = url.with_fragment(None)

    if url.path != "/" and url.path.endswith("/"):
        url = url.with_path(url.path.rstrip("/"))

    return url
```

Bây giờ:

```python
a = URL("https://example.com/novel")
b = URL("https://example.com/novel/")

print(normalize_url(a) == normalize_url(b))
```

→ `True`

Nhưng nhớ:

**Không nên bật rule này global nếu chưa xác định semantics của website.**

---

# 8. Query khác nhau

Ví dụ:

```python
a = URL("https://example.com/search?q=python")
b = URL("https://example.com/search?q=sqlite")

print(a == b)
```

Kết quả:

```text
False
```

Đúng.

Hai request tìm kiếm khác nhau.

---

# 9. Query parameter order

Ví dụ:

```python
a = URL("https://example.com/search?a=1&b=2")
b = URL("https://example.com/search?b=2&a=1")

print(a == b)
```

Đừng vội xây:

```python
def same_url(a, b):
    return sorted(a.query.items()) == sorted(b.query.items())
```

Bởi vì query ordering và duplicate parameters có thể có semantics riêng.

Ví dụ:

```text
?tag=python&tag=sqlite
```

khác về thứ tự so với:

```text
?tag=sqlite&tag=python
```

Nếu website dùng thứ tự đó, việc sort sẽ làm mất thông tin.

**Nguyên tắc:**

> Không thay đổi query để phục vụ comparison nếu chưa có URL policy rõ ràng.

---

# 10. Duplicate query parameters

Ví dụ:

```python
from yarl import URL

a = URL(
    "https://example.com/search"
    "?tag=python&tag=sqlite"
)

b = URL(
    "https://example.com/search"
    "?tag=sqlite&tag=python"
)

print(a == b)
```

Hai URL này có representation khác nhau.

Đừng biến query thành:

```python
dict(url.query)
```

để so sánh.

Vì:

```python
dict(url.query)
```

không phải cách phù hợp để giữ toàn bộ semantics của duplicate parameters.

Ta đã học:

```python
url.query.getall("tag")
```

---

# 11. Scheme khác nhau

```python
a = URL("http://example.com/chapter-1")
b = URL("https://example.com/chapter-1")

print(a == b)
```

→ `False`

Không được normalize:

```text
http → https
```

chỉ vì bạn muốn hai URL bằng nhau.

`http` và `https` là hai scheme khác nhau.

---

# 12. Host khác nhau

```python
a = URL("https://example.com/chapter-1")
b = URL("https://cdn.example.com/chapter-1")

print(a == b)
```

→ `False`

Đây cũng là lý do crawler phải phân biệt:

```text
same host
```

và:

```text
same origin
```

---

# 13. Origin comparison

Ta đã học `origin()` ở Buổi 20.

```python
from yarl import URL

a = URL("https://example.com/chapter-1")
b = URL("https://example.com/chapter-2")

print(a.origin())
print(b.origin())
```

Cả hai có cùng origin:

```text
https://example.com
```

Có thể kiểm tra:

```python
print(a.origin() == b.origin())
```

→ `True`

Nhưng:

```python
a == b
```

→ `False`

Bởi vì:

```text
origin
```

chỉ là:

```text
scheme + host + port
```

không bao gồm path/query/fragment.

---

# 14. URL comparison có nhiều cấp độ

Đây là cách rất tốt để tư duy:

```text
Level 1
Exact URL comparison
        ↓
a == b
```

---

```text
Level 2
Normalized URL comparison
        ↓
normalize(a) == normalize(b)
```

---

```text
Level 3
Origin comparison
        ↓
a.origin() == b.origin()
```

---

```text
Level 4
Site policy comparison
        ↓
same crawl resource?
```

Không nên dùng một hàm duy nhất cho tất cả.

---

# 15. `same_url()` cho crawler

Ở crawler, ta có thể bắt đầu đơn giản:

```python
from yarl import URL


def normalize_url(url: URL) -> URL:
    return url.with_fragment(None)


def same_url(a: URL, b: URL) -> bool:
    return normalize_url(a) == normalize_url(b)
```

Test:

```python
urls = [
    (
        URL("https://example.com/chapter-1#top"),
        URL("https://example.com/chapter-1#content"),
    ),
    (
        URL("https://example.com/chapter-1"),
        URL("https://example.com/chapter-2"),
    ),
    (
        URL("https://example.com/novel"),
        URL("https://example.com/novel/"),
    ),
]

for a, b in urls:
    print(a)
    print(b)
    print("same:", same_url(a, b))
    print()
```

Kết quả về mặt policy:

```text
chapter-1#top
chapter-1#content
same: True


chapter-1
chapter-2
same: False


/novel
/novel/
same: False
```

Đây là behavior khá an toàn.

---

# 16. Comparison bằng normalized URL

Có một cách khác rất hữu ích:

```python
normalized_a = normalize_url(a)
normalized_b = normalize_url(b)

if normalized_a == normalized_b:
    ...
```

Đặc biệt quan trọng khi sau này chúng ta có:

```text
Set[URL]
```

hoặc:

```text
dict[URL, ...]
```

Ta muốn object được đưa vào collection đã được normalize.

---

# 17. Đừng viết comparison bằng `str()`

Không cần:

```python
str(a) == str(b)
```

nếu cả hai đã là:

```python
URL
```

Hãy:

```python
a == b
```

Yarl được thiết kế để xử lý URL như object.

---

# 18. Đừng comparison bằng `.human_repr()`

Ví dụ:

```python
a.human_repr() == b.human_repr()
```

không phải cách tốt để xây URL identity.

`human_repr()` chủ yếu hữu ích cho:

```text
debug
logging
display
```

Không nên dùng nó làm canonical identity của crawler.

---

# 19. Đừng comparison bằng `raw_path`

Tương tự:

```python
a.raw_path == b.raw_path
```

chỉ so sánh path representation.

Nó không xét:

```text
scheme
host
port
query
fragment
```

Do đó không phải URL comparison hoàn chỉnh.

---

# 20. Một class nhỏ nếu cần

Nếu crawler lớn dần, ta có thể gom logic:

```python
from yarl import URL


class URLComparator:

    @staticmethod
    def normalize(url: URL) -> URL:
        return url.with_fragment(None)

    @classmethod
    def same(cls, a: URL, b: URL) -> bool:
        return cls.normalize(a) == cls.normalize(b)
```

Sử dụng:

```python
a = URL("https://example.com/chapter-1#top")
b = URL("https://example.com/chapter-1#content")

print(URLComparator.same(a, b))
```

Nhưng hiện tại tôi **không khuyến khích** tạo class chỉ cho hai method.

Function vẫn đủ tốt:

```python
normalize_url()
same_url()
```

Đúng với nguyên tắc abstraction mà chúng ta đang theo đuổi trong Novel Crawler.

---

# 21. Comparison trong kiến trúc crawler

Pipeline bây giờ:

```text
                  HTML
                    │
                    ▼
               selectolax
                    │
                    ▼
                href/src
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
              URL Comparator
                    │
                    ▼
             URL Deduplicator
```

Trong đó:

### Resolver

```text
relative → absolute
```

### Normalizer

```text
URL → normalized URL
```

### Comparator

```text
URL A ?= URL B
```

### Deduplicator

```text
loại URL trùng
```

Đây là 4 responsibility khác nhau.

---

# 22. Một ví dụ gần với Novel Crawler

Giả sử parser lấy được:

```text
https://site.com/chapter-1#top
https://site.com/chapter-1#content
https://site.com/chapter-1
https://site.com/chapter-2
```

Ta normalize:

```text
https://site.com/chapter-1
https://site.com/chapter-1
https://site.com/chapter-1
https://site.com/chapter-2
```

Comparison cho biết:

```text
1 == 2 → True
1 == 3 → True
1 == 4 → False
```

Nhưng **comparison chưa xóa phần tử nào**.

Đó là nhiệm vụ của Buổi 38.

---

# 23. Một test suite nhỏ

```python
from yarl import URL


def normalize_url(url: URL) -> URL:
    return url.with_fragment(None)


def same_url(a: URL, b: URL) -> bool:
    return normalize_url(a) == normalize_url(b)


def test_same_exact_url():
    a = URL("https://example.com/chapter-1")
    b = URL("https://example.com/chapter-1")

    assert same_url(a, b)


def test_same_url_different_fragment():
    a = URL("https://example.com/chapter-1#top")
    b = URL("https://example.com/chapter-1#content")

    assert same_url(a, b)


def test_different_path():
    a = URL("https://example.com/chapter-1")
    b = URL("https://example.com/chapter-2")

    assert not same_url(a, b)


def test_different_scheme():
    a = URL("http://example.com/chapter-1")
    b = URL("https://example.com/chapter-1")

    assert not same_url(a, b)


def test_trailing_slash_is_different_by_default():
    a = URL("https://example.com/novel")
    b = URL("https://example.com/novel/")

    assert not same_url(a, b)
```

Chạy:

```bash
pytest -v
```

---

# 24. Quy tắc thiết kế quan trọng

Đối với Novel Crawler của bạn, tôi đề xuất identity mặc định:

```text
Normalized URL
=
scheme
+
host
+
port
+
path
+
query
```

và:

```text
fragment
```

được loại bỏ trước khi đưa vào crawler identity.

Tức là:

```text
https://example.com/chapter-1#top
                         │
                         ▼
https://example.com/chapter-1
```

Nhưng:

```text
/novel
/novel/
```

vẫn giữ khác nhau.

Và:

```text
?a=1&b=2
?b=2&a=1
```

chưa tự động coi là giống nhau.

Đây là một policy **an toàn và conservative**.

---

# 25. Tổng kết Buổi 37

Ta có:

```python
a == b
```

cho **exact comparison**.

Nếu crawler có normalization:

```python
normalize_url(a) == normalize_url(b)
```

cho **normalized comparison**.

Origin:

```python
a.origin() == b.origin()
```

cho **same-origin comparison**.

Ba khái niệm này không được trộn lẫn.

Kiến trúc:

```text
URL
 │
 ├── Resolver
 │
 ├── Normalizer
 │
 ├── Comparator
 │
 └── Deduplicator
```

Và bước tiếp theo rất tự nhiên:

# Buổi 38 — URL Deduplication

Chúng ta sẽ lấy một danh sách như:

```python
urls = [
    URL("https://example.com/chapter-1#top"),
    URL("https://example.com/chapter-1#content"),
    URL("https://example.com/chapter-1"),
    URL("https://example.com/chapter-2"),
]
```

và xây **deduplicator thực sự cho crawler** bằng:

```text
set[URL]
```

sau đó nâng lên:

```text
URL → normalized URL → seen set → crawl queue
```

và xử lý luôn trường hợp crawler gặp cùng một chapter từ **nhiều trang listing/pagination khác nhau**.
