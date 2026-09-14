# Buổi 3 — `yarl` Immutable và `with_*()`

Hôm nay chúng ta học một đặc điểm **cốt lõi** của `yarl`:

> `URL` là **immutable**. Mọi thao tác thay đổi URL đều tạo ra **URL mới**, không sửa URL hiện tại.

Điều này đặc biệt hữu ích trong crawler vì ta có thể giữ `base_url` ổn định rồi tạo ra nhiều URL dẫn xuất.

---

## 1. Immutable là gì?

Ví dụ với một số object mutable:

```python
data = [1, 2, 3]

data.append(4)

print(data)
```

`data` bị thay đổi.

Nhưng với `yarl.URL`:

```python
from yarl import URL


url = URL("https://example.com")


new_url = url / "novels"


print("url     =", url)
print("new_url =", new_url)
```

Kết quả:

```text
url     = https://example.com
new_url = https://example.com/novels
```

URL ban đầu vẫn giữ nguyên.

---

# 2. Tại sao `URL` immutable?

Hãy tưởng tượng crawler của bạn có:

```python
BASE_URL = URL("https://example.com")
```

Sau đó:

```python
novel_url = BASE_URL / "novel" / "python"

chapter_url = novel_url / "chapter-1"

image_url = novel_url / "images" / "cover.jpg"
```

Ta có:

```text
                    BASE_URL
                       │
              https://example.com
                       │
                  novel_url
                       │
               /novel/python
                 /         \
                /           \
       chapter_url       image_url
       /chapter-1       /images/cover.jpg
```

Nếu URL mutable, việc thay đổi một object dùng chung có thể gây ra bug rất khó phát hiện.

Immutable giúp:

```text
BASE_URL
   │
   ├── không thay đổi
   │
   ├── novel_url
   │
   ├── chapter_url
   │
   └── image_url
```

---

# 3. `with_scheme()`

Giả sử:

```python
from yarl import URL


url = URL("http://example.com/novel/python")

new_url = url.with_scheme("https")

print(url)
print(new_url)
```

Kết quả:

```text
http://example.com/novel/python
https://example.com/novel/python
```

URL gốc không đổi.

---

## 4. Kiểm tra object identity

Ta có thể chứng minh:

```python
from yarl import URL


url = URL("http://example.com")

new_url = url.with_scheme("https")

print(url is new_url)
```

Kết quả:

```text
False
```

Hai object khác nhau.

---

# 5. `with_host()`

```python
from yarl import URL


url = URL("https://example.com/novel/python")

new_url = url.with_host("crawler.example.com")

print(url)
print(new_url)
```

Kết quả:

```text
https://example.com/novel/python
https://crawler.example.com/novel/python
```

Chỉ host thay đổi.

---

# 6. `with_port()`

```python
from yarl import URL


url = URL("https://example.com/novel/python")

new_url = url.with_port(8080)

print(url)
print(new_url)
```

Kết quả:

```text
https://example.com/novel/python
https://example.com:8080/novel/python
```

---

# 7. `with_path()`

Đây là thao tác rất hữu ích.

```python
from yarl import URL


url = URL("https://example.com/novel/python")

new_url = url.with_path("/novel/python/chapter-1")

print(url)
print(new_url)
```

Kết quả:

```text
https://example.com/novel/python
https://example.com/novel/python/chapter-1
```

---

# 8. `with_path()` thay toàn bộ path

Đây là điểm cần chú ý.

Không phải:

```text
path + path mới
```

mà là:

```text
path cũ
   ↓
THAY THẾ
   ↓
path mới
```

Ví dụ:

```python
url = URL("https://example.com/a/b/c")

new_url = url.with_path("/x/y")

print(new_url)
```

Kết quả:

```text
https://example.com/x/y
```

Không phải:

```text
https://example.com/a/b/c/x/y
```

---

# 9. `with_query()`

Đây là một trong những API quan trọng nhất của `yarl`.

Ví dụ:

```python
from yarl import URL


url = URL("https://example.com/novels")

new_url = url.with_query(page=2)

print(url)
print(new_url)
```

Kết quả:

```text
https://example.com/novels
https://example.com/novels?page=2
```

---

# 10. Thêm nhiều query parameters

```python
url = URL("https://example.com/novels")

new_url = url.with_query(
    page=2,
    sort="new",
    limit=20,
)

print(new_url)
```

Kết quả:

```text
https://example.com/novels?page=2&sort=new&limit=20
```

---

# 11. Query dictionary

Bạn cũng có thể truyền dictionary:

```python
from yarl import URL


params = {
    "page": 2,
    "sort": "new",
    "limit": 20,
}


url = URL("https://example.com/novels")

new_url = url.with_query(params)

print(new_url)
```

Kết quả:

```text
https://example.com/novels?page=2&sort=new&limit=20
```

Đây sẽ rất tiện khi xây pagination.

---

# 12. `with_fragment()`

```python
from yarl import URL


url = URL("https://example.com/novel/python")

new_url = url.with_fragment("chapter-10")

print(url)
print(new_url)
```

Kết quả:

```text
https://example.com/novel/python
https://example.com/novel/python#chapter-10
```

---

# 13. Xóa fragment

Có thể truyền `None`:

```python
url = URL("https://example.com/novel/python#chapter-10")

new_url = url.with_fragment(None)

print(url)
print(new_url)
```

Kết quả:

```text
https://example.com/novel/python#chapter-10
https://example.com/novel/python
```

Điều này rất hữu ích cho **URL normalization**.

---

# 14. Kết hợp nhiều `with_*()`

Đây mới là sức mạnh thực sự.

```python
from yarl import URL


url = URL("http://example.com/novel/python")


new_url = (
    url.with_scheme("https")
    .with_host("reader.example.com")
    .with_port(8443)
    .with_path("/books/python")
    .with_query(page=2)
    .with_fragment("chapter-10")
)


print("Original:")
print(url)

print()

print("New:")
print(new_url)
```

Kết quả:

```text
Original:
http://example.com/novel/python

New:
https://reader.example.com:8443/books/python?page=2#chapter-10
```

Đặc biệt:

```python
url
```

vẫn giữ nguyên.

---

# 15. Nhưng có một vấn đề

Không nên lạm dụng:

```python
new_url = (
    url.with_scheme(...)
    .with_host(...)
    .with_port(...)
    .with_path(...)
    .with_query(...)
    .with_fragment(...)
)
```

nếu chỉ muốn xây dựng một URL mới từ đầu.

Ví dụ nếu ta muốn:

```text
https://example.com/novel/python?page=2
```

thì:

```python
URL("https://example.com/novel/python").with_query(page=2)
```

rất hợp lý.

Nhưng nếu URL ban đầu hoàn toàn không liên quan:

```python
URL("ftp://google.com/a").with_scheme("https").with_host("example.com")
```

thì code trở nên khó đọc.

**Nguyên tắc:**

> `with_*()` thích hợp khi ta có một URL gần đúng và muốn tạo một biến thể của nó.

---

# 16. `/` và `with_path()` khác nhau

Đây là điểm rất quan trọng.

### `/`

Dùng để **xây dựng path**:

```python
url = URL("https://example.com")

url = url / "novel" / "python"

print(url)
```

→

```text
https://example.com/novel/python
```

### `with_path()`

Dùng để **thay thế path**:

```python
url = URL("https://example.com/old/path")

new_url = url.with_path("/new/path")
```

→

```text
https://example.com/new/path
```

Có thể nhớ:

```text
/            → build path
with_path() → replace path
```

---

# 17. `with_query()` rất quan trọng với Pagination

Trong crawler truyện, giả sử:

```text
https://example.com/truyen?page=1
```

Ta không nên:

```python
url = URL("https://example.com/truyen?page=1")

url = URL(str(url).replace("page=1", "page=2"))
```

Đây là xử lý string rất dễ lỗi.

Thay vào đó:

```python
url = URL("https://example.com/truyen?page=1")

next_url = url.with_query(page=2)

print(next_url)
```

→

```text
https://example.com/truyen?page=2
```

---

# 18. Pagination function

Ta có thể viết:

```python
from yarl import URL


def page_url(url: URL, page: int) -> URL:
    return url.with_query(page=page)


def main() -> None:
    base_url = URL("https://example.com/truyen")

    for page in range(1, 6):
        url = page_url(base_url, page)
        print(url)


if __name__ == "__main__":
    main()
```

Kết quả:

```text
https://example.com/truyen?page=1
https://example.com/truyen?page=2
https://example.com/truyen?page=3
https://example.com/truyen?page=4
https://example.com/truyen?page=5
```

Đây chính là kiểu code chúng ta có thể dùng trong **Novel Parser/Pagination**.

---

# 19. Một ví dụ thực tế hơn

Giả sử website có:

```text
/truyen/python
/truyen/python?page=2
/truyen/python?page=3
```

Ta tạo:

```python
from yarl import URL


class Pagination:
    def __init__(self, base_url: URL):
        self.base_url = base_url

    def get_page(self, page: int) -> URL:
        return self.base_url.with_query(page=page)


def main() -> None:
    base_url = URL("https://example.com/truyen/python")

    pagination = Pagination(base_url)

    for page in range(1, 4):
        url = pagination.get_page(page)
        print(url)


if __name__ == "__main__":
    main()
```

Output:

```text
https://example.com/truyen/python?page=1
https://example.com/truyen/python?page=2
https://example.com/truyen/python?page=3
```

---

# 20. URL normalization

Immutable rất hữu ích khi normalize URL.

Ví dụ:

```text
https://example.com/chapter-1#content
```

và:

```text
https://example.com/chapter-1#comments
```

Nếu fragment không có ý nghĩa đối với crawler, ta có thể:

```python
from yarl import URL


def normalize(url: URL) -> URL:
    return url.with_fragment(None)


url1 = URL("https://example.com/chapter-1#content")

url2 = URL("https://example.com/chapter-1#comments")


print(normalize(url1))
print(normalize(url2))
```

Kết quả:

```text
https://example.com/chapter-1
https://example.com/chapter-1
```

Sau đó:

```python
print(normalize(url1) == normalize(url2))
```

→

```text
True
```

Điều này rất hữu ích cho:

```text
URL Deduplication
        ↓
Crawler Queue
        ↓
Visited URLs
```

---

# 21. Tạo URL mới từ URL cũ

Một pattern rất hay:

```python
def normalize(url: URL) -> URL:
    return url.with_fragment(None)
```

Hoặc:

```python
def force_https(url: URL) -> URL:
    return url.with_scheme("https")
```

Hoặc:

```python
def set_page(url: URL, page: int) -> URL:
    return url.with_query(page=page)
```

Các function này có đặc điểm:

```text
URL
 ↓
URL mới
```

Không có side effect.

Đây là kiểu function rất phù hợp với tư duy **functional + DDD**.

---

# 22. Một ví dụ gần với kiến trúc crawler của bạn

Ta có thể tạo một `URLPolicy` đơn giản:

```python
from yarl import URL


class URLPolicy:
    def normalize(self, url: URL) -> URL:
        return url.with_fragment(None)

    def force_https(self, url: URL) -> URL:
        return url.with_scheme("https")

    def page(self, url: URL, page: int) -> URL:
        return url.with_query(page=page)

    def is_allowed(self, url: URL) -> bool:
        return url.scheme == "https" and url.host == "example.com"


def main() -> None:
    policy = URLPolicy()

    url = URL("http://example.com/truyen/python?page=1#content")

    print("Original:")
    print(url)

    print()

    print("HTTPS:")
    print(policy.force_https(url))

    print()

    print("Page 2:")
    print(policy.page(url, 2))

    print()

    print("Normalized:")
    print(policy.normalize(url))


if __name__ == "__main__":
    main()
```

Đây chưa phải architecture cuối cùng, nhưng nó cho thấy cách `yarl` có thể trở thành một **building block** cho URL policy của crawler.

---

# 23. Một điều cần đặc biệt nhớ về `with_query()`

Nếu URL đang có query:

```python
url = URL("https://example.com/truyen?page=1&sort=new")
```

thì:

```python
new_url = url.with_query(page=2)
```

sẽ tạo query mới theo dữ liệu bạn truyền vào; nó không phải là API "chỉnh đúng một key và giữ nguyên mọi key cũ" theo cách bạn có thể tưởng tượng.

Nếu muốn giữ các tham số hiện có rồi thay `page`, ta sẽ học cách xử lý `url.query` ở phần **Query Deep Dive**.

Ví dụ đó sẽ đặc biệt quan trọng khi website có:

```text
?page=2&sort=new&category=python
```

và ta chỉ muốn đổi:

```text
page=3
```

mà vẫn giữ:

```text
sort=new
category=python
```

---

# 24. Bài tập thực hành

### Bài 1 — `with_*()`

Cho:

```python
url = URL("http://example.com:8080/old/path?page=1#content")
```

Tạo URL mới:

```text
https://reader.example.com:8443/new/path?page=2#chapter-2
```

**Không được sửa `url`.**

---

### Bài 2 — chứng minh immutable

Viết chương trình:

```python
url = URL("http://example.com")

new_url = url.with_scheme("https")

print(url)
print(new_url)
print(url is new_url)
```

Giải thích tại sao:

```text
False
```

---

### Bài 3 — Pagination

Viết:

```python
def make_page_url(url: URL, page: int) -> URL: ...
```

Cho:

```python
base = URL("https://example.com/truyen/python")
```

tạo:

```text
page 1
page 2
page 3
page 4
page 5
```

---

### Bài 4 — URL normalization

Viết:

```python
def normalize_url(url: URL) -> URL: ...
```

Sao cho:

```text
https://example.com/chapter-1#content
https://example.com/chapter-1#comment
https://example.com/chapter-1#anything
```

đều trở thành:

```text
https://example.com/chapter-1
```

---

## Tổng kết Buổi 3

Hôm nay cần nắm chắc:

```text
                 URL
                  │
             immutable
                  │
        ┌─────────┼─────────┐
        ↓         ↓         ↓
 with_scheme  with_host  with_port
        │
        ├── with_path()
        │
        ├── with_query()
        │
        └── with_fragment()
```

Và phân biệt:

```python
url / "novel" / "python"
```

→ **xây thêm path**

với:

```python
url.with_path("/novel/python")
```

→ **thay toàn bộ path**

và:

```python
url.with_query(page=2)
```

→ **tạo URL với query mới**.

**Buổi 4** chúng ta sẽ học sâu về **path manipulation**: `/`, `joinpath()`, `parent`, `name`, `suffix`, `with_name()`, `with_suffix()`, relative path và cách dùng chúng để xử lý **URL chapter/image/file** trong crawler.
