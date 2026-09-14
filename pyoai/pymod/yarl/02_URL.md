# Buổi 2 — Cấu trúc `URL` trong `yarl`

Hôm nay chúng ta đi sâu vào **URL object**. Đây là nền tảng để sau này dùng `yarl` trong **Fetcher + Parser + Novel Crawler**.

---

## 1. Một URL gồm những gì?

Xét URL:

```text
https://user:password@example.com:8080/novels/python?page=2&sort=new#chapter
```

Có thể chia thành:

```text
https://user:password@example.com:8080/novels/python?page=2&sort=new#chapter
│     │                  │          │                 │                │
│     │                  │          │                 │                └─ fragment
│     │                  │          │                 └─ query
│     │                  │          └─ path
│     │                  └─ port
│     └─ user/password
└─ scheme
```

Trong `yarl`, chúng ta có thể truy cập từng phần.

---

# 2. `URL()` — tạo URL

```python
from yarl import URL

url = URL("https://example.com/novels/python")

print(url)
```

Kết quả:

```text
https://example.com/novels/python
```

Kiểm tra kiểu:

```python
print(type(url))
```

```text
<class 'yarl.URL'>
```

---

# 3. `scheme`

```python
url = URL("https://example.com/novels")

print(url.scheme)
```

Kết quả:

```text
https
```

Ví dụ:

```python
URL("http://example.com").scheme
```

→

```text
http
```

Đây là phần:

```text
https://
^^^^^
```

---

# 4. `host`

```python
url = URL("https://example.com/novels")

print(url.host)
```

Kết quả:

```text
example.com
```

Đây là:

```text
https://example.com/novels
       ^^^^^^^^^^^
```

Trong crawler:

```python
if url.host != "example.com":
    print("Không phải domain cần crawl")
```

---

# 5. `port`

```python
url = URL("https://example.com:8080/novels")

print(url.port)
```

Kết quả:

```text
8080
```

Nếu không chỉ định port:

```python
url = URL("https://example.com")

print(url.port)
```

thường sẽ cho:

```text
443
```

vì `https` có port mặc định là `443`.

Tương tự:

```python
URL("http://example.com").port
```

→

```text
80
```

---

# 6. `path`

```python
url = URL("https://example.com/novels/python")

print(url.path)
```

Kết quả:

```text
/novels/python
```

Đây là phần:

```text
https://example.com/novels/python
                    ^^^^^^^^^^^^^
```

Có thể dùng:

```python
print(url.parts)
```

để xem các phần path.

Ví dụ:

```python
url = URL("https://example.com/novels/python/chapter-1")

print(url.parts)
```

---

# 7. `query`

Xét:

```text
https://example.com/novels?page=2&sort=new
```

Ta có:

```python
url = URL("https://example.com/novels?page=2&sort=new")

print(url.query)
```

`query` là một cấu trúc dạng multidict.

Có thể truy cập:

```python
print(url.query["page"])
print(url.query["sort"])
```

Kết quả:

```text
2
new
```

---

# 8. `query_string`

Nếu muốn lấy query dưới dạng string:

```python
url = URL("https://example.com/novels?page=2&sort=new")

print(url.query_string)
```

Kết quả:

```text
page=2&sort=new
```

So sánh:

```python
print(url.query)
print(url.query_string)
```

Có thể hiểu:

```text
query
 ↓
cấu trúc dữ liệu

query_string
 ↓
chuỗi query
```

---

# 9. `fragment`

URL:

```text
https://example.com/novels/python#chapter-10
```

Lấy fragment:

```python
url = URL("https://example.com/novels/python#chapter-10")

print(url.fragment)
```

Kết quả:

```text
chapter-10
```

Phần này:

```text
https://example.com/novels/python#chapter-10
                                      ^^^^^^^^^
```

Trong crawler, fragment thường **không được gửi lên server**.

Ví dụ:

```text
/chapter-1#content
/chapter-1#comments
```

thường vẫn request cùng resource:

```text
/chapter-1
```

Đây là vấn đề chúng ta sẽ dùng khi làm **URL normalization**.

---

# 10. `user` và `password`

URL có thể chứa authentication:

```python
url = URL("https://john:secret@example.com/books")

print(url.user)
print(url.password)
print(url.host)
```

Kết quả:

```text
john
secret
example.com
```

Cấu trúc:

```text
https://john:secret@example.com
        └──────┬─────┘
             userinfo
```

Trong crawler thực tế, bạn thường **không muốn log password**.

Ví dụ không nên:

```python
logger.info("Fetching %s", url)
```

nếu URL có credentials.

---

# 11. `raw_path`

Đây là một phần quan trọng.

Giả sử:

```python
url = URL("https://example.com/novels/Đấu-Phá-Thương-Không")
```

`yarl` phải xử lý Unicode/encoding.

Ta có:

```python
print(url.path)
print(url.raw_path)
```

`path` là dạng đã decode ở mức API của `yarl`, còn `raw_path` giữ dạng encoded phù hợp với URL representation.

Đây là lý do **không nên tự `quote()` URL một cách tùy tiện** rồi lại đưa qua thư viện URL khác.

---

# 12. Unicode URL

Crawler truyện tiếng Việt rất dễ gặp trường hợp:

```text
https://example.com/truyện/đấu-phá-thương-không
```

Ta có thể:

```python
from yarl import URL


url = URL("https://example.com/truyện/đấu-phá-thương-không")

print(url)
print(url.path)
print(url.raw_path)
```

Điểm cần nhớ:

> Hãy để thư viện URL xử lý encoding thay vì tự nối chuỗi và tự encode/decode lung tung.

---

# 13. `origin()`

```python
url = URL("https://example.com:8080/novels/python?page=2")

print(url.origin())
```

Origin về cơ bản gồm:

```text
scheme + host + port
```

Ví dụ:

```text
https://example.com:8080
```

Điều này rất hữu ích khi xây:

```text
DomainPolicy
URLPolicy
SameOriginPolicy
```

cho crawler.

Ví dụ ý tưởng:

```python
def is_same_origin(url: URL, base: URL) -> bool:
    return url.origin() == base.origin()
```

---

# 14. `human_repr()`

`yarl` còn có:

```python
url.human_repr()
```

Ví dụ URL có Unicode/encoded characters:

```python
from yarl import URL


url = URL("https://example.com/đấu-phá-thương-không")

print("URL       :", url)
print("Human repr:", url.human_repr())
```

Điều này hữu ích khi **hiển thị URL cho người dùng/logging**, trong khi representation của URL có thể cần encoding để truyền qua HTTP.

---

# 15. URL absolute và relative

`yarl` cũng biểu diễn URL tương đối.

```python
from yarl import URL


url = URL("/novels/python")

print(url)
print(url.path)
```

URL này chưa có:

```text
scheme
host
```

Nó chỉ có:

```text
/novels/python
```

Ta có:

```python
print(url.is_absolute())
```

→

```text
False
```

Trong khi:

```python
url = URL("https://example.com/novels/python")

print(url.is_absolute())
```

→

```text
True
```

---

# 16. Đây là vấn đề cực quan trọng trong Parser

HTML có thể chứa:

```html
<a href="/novel/python">
```

hoặc:

```html
<a href="https://example.com/novel/python">
```

hoặc:

```html
<a href="../chapter-2">
```

Parser không nên xử lý tất cả bằng string.

Ví dụ:

```python
from yarl import URL


base_url = URL("https://example.com/novel/python")

href = "/chapter-1"

url = URL(href)

print(url)
```

Ta có:

```text
/chapter-1
```

Đây vẫn là relative URL.

Sau này chúng ta sẽ dùng cơ chế URL joining/resolution để biến nó thành:

```text
https://example.com/chapter-1
```

Đây chính là một phần cực kỳ quan trọng trong **Novel Parser** mà bạn đang học.

---

# 17. Kiểm tra URL

Có thể xây một policy đơn giản:

```python
from yarl import URL


def is_http_url(url: URL) -> bool:
    return url.scheme in {"http", "https"}


urls = [
    URL("https://example.com"),
    URL("http://example.com"),
    URL("ftp://example.com"),
    URL("/novel/python"),
]


for url in urls:
    print(url, "=>", is_http_url(url))
```

Kết quả:

```text
https://example.com => True
http://example.com => True
ftp://example.com => False
/novel/python => False
```

Đây chính là kiểu logic sau này có thể đặt trong:

```text
application/
    policies/

domain/
    value_objects/
```

thay vì nhét vào Fetcher.

---

# 18. Xây một `URLInspector`

Để luyện tập, chúng ta tạo một class:

```python
from yarl import URL


class URLInspector:
    def __init__(self, url: URL):
        self.url = url

    def show(self) -> None:
        print("URL       :", self.url)
        print("Scheme    :", self.url.scheme)
        print("User      :", self.url.user)
        print("Password  :", self.url.password)
        print("Host      :", self.url.host)
        print("Port      :", self.url.port)
        print("Path      :", self.url.path)
        print("Query     :", self.url.query)
        print("Query str :", self.url.query_string)
        print("Fragment  :", self.url.fragment)
        print("Origin    :", self.url.origin())
        print("Absolute  :", self.url.is_absolute())


def main() -> None:
    url = URL(
        "https://john:secret@example.com:8080/novels/python?page=2&sort=new#chapter"
    )

    inspector = URLInspector(url)
    inspector.show()


if __name__ == "__main__":
    main()
```

Đây là một chương trình hoàn chỉnh để bạn chạy thử.

---

# 19. Áp dụng vào Novel Crawler

Giả sử Fetcher nhận:

```python
url = URL("https://example.com/novel/python?page=2")
```

Fetcher có thể kiểm tra:

```python
if url.scheme not in {"http", "https"}:
    raise ValueError("Unsupported scheme")

if url.host != "example.com":
    raise ValueError("Unsupported host")
```

Parser có thể sử dụng:

```python
url.path
```

để phân biệt:

```text
/novel/...
/chapter/...
/category/...
```

Application layer có thể sử dụng:

```python
url.query
```

để xử lý:

```text
?page=2
```

Và URL normalization có thể xử lý:

```python
url.fragment
```

để tránh crawler coi:

```text
chapter-1#content
chapter-1#comment
```

là hai resource khác nhau.

---

# 20. Mô hình tư duy hôm nay

Hãy nhớ `URL` như một object:

```text
                    URL
                     │
       ┌─────────────┼─────────────┐
       │             │             │
    scheme          host          port
       │             │             │
     https       example.com      443
                     │
                    path
                     │
              /novel/python
                     │
                   query
                     │
                page=2
                     │
                 fragment
                     │
                  chapter
```

Thay vì coi:

```python
"https://example.com/novel/python?page=2"
```

là **một chuỗi dài**, hãy coi nó là:

```text
URL Object
 ├── scheme
 ├── host
 ├── port
 ├── path
 ├── query
 └── fragment
```

Đây là tư duy quan trọng nhất khi sử dụng `yarl`.

---

## Bài tập Buổi 2

### Bài 1

Phân tích URL:

```python
URL("https://user:pass@example.com:8443/novels/python?page=2&sort=new#chapter-10")
```

In toàn bộ:

```text
scheme
user
password
host
port
path
query
query_string
fragment
origin
```

### Bài 2

Tạo:

```python
base = URL("https://example.com")
```

và:

```text
/novels
/novels/python
/novels/python/chapter-1
```

Sau đó kiểm tra URL nào là absolute.

### Bài 3 — crawler

Viết hàm:

```python
def is_allowed_url(url: URL) -> bool: ...
```

Chỉ cho phép:

```text
https
example.com
```

Ví dụ:

```text
https://example.com/novel/abc       → True
http://example.com/novel/abc        → False
https://google.com/novel/abc        → False
ftp://example.com/file              → False
```

**Buổi 3** chúng ta sẽ học phần rất quan trọng: **`yarl` immutable + `with_*()`**, tức cách thay đổi `scheme`, `host`, `port`, `path`, `query`, `fragment` mà không sửa URL gốc. Đây là nền tảng để xây dựng URL một cách an toàn trong crawler.
