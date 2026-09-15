# Buổi 20 — `origin()` trong `yarl`

Hôm nay chúng ta kết thúc **Phần II — URL Manipulation** bằng một API rất quan trọng:

```python
url.origin()
```

`origin()` đặc biệt hữu ích khi xây crawler vì nó cho phép chúng ta lấy **phần gốc của URL**:

```text
scheme + host + port
```

Ví dụ:

```text
https://example.com:8080/novel/python/chapter/10?page=2#content
└───────────────────────┘
         origin
```

---

# 1. `origin()` là gì?

Tạo URL:

```python
from yarl import URL

url = URL("https://example.com:8080/novel/python/chapter/10?page=2#content")

print(url)
print(url.origin())
```

Kết quả:

```text
https://example.com:8080/novel/python/chapter/10?page=2#content
https://example.com:8080
```

Như vậy:

```text
URL đầy đủ
│
├── scheme     https
├── host       example.com
├── port       8080
├── path       /novel/python/chapter/10
├── query      page=2
└── fragment   content
```

Còn:

```python
url.origin()
```

chỉ lấy:

```text
https://example.com:8080
```

---

# 2. Origin gồm những gì?

Có thể nhớ:

```text
origin = scheme + host + port
```

Ví dụ:

```text
https://example.com:8443/novel/python?page=2#chapter-10
│     │           │
│     │           └── port
│     └────────────── host
└──────────────────── scheme
```

Origin:

```text
https://example.com:8443
```

Không bao gồm:

```text
/novel/python
?page=2
#chapter-10
```

---

# 3. `origin()` khác `host`

Đây là điểm rất dễ nhầm.

```python
from yarl import URL

url = URL("https://example.com:8080/novel/python")

print("scheme:", url.scheme)
print("host  :", url.host)
print("port  :", url.port)
print("origin:", url.origin())
```

Kết quả:

```text
scheme: https
host  : example.com
port  : 8080
origin: https://example.com:8080
```

So:

```text
host
↓
example.com
```

Còn:

```text
origin
↓
https://example.com:8080
```

---

# 4. `origin()` không chứa Path

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/novel/python/chapter/10")

print(url.origin())
```

Kết quả:

```text
https://example.com
```

Không phải:

```text
https://example.com/novel/python/chapter/10
```

---

# 5. `origin()` không chứa Query

```python
from yarl import URL

url = URL("https://example.com/search?q=python&page=2")

print(url.origin())
```

Kết quả:

```text
https://example.com
```

Query:

```text
?q=python&page=2
```

không thuộc origin.

---

# 6. `origin()` không chứa Fragment

```python
from yarl import URL

url = URL("https://example.com/article#comments")

print(url.origin())
```

Kết quả:

```text
https://example.com
```

Fragment:

```text
#comments
```

không thuộc origin.

---

# 7. Port là phần rất quan trọng

So sánh:

```python
from yarl import URL

a = URL("https://example.com")
b = URL("https://example.com:8443")

print(a.origin())
print(b.origin())
```

Kết quả:

```text
https://example.com
https://example.com:8443
```

Hai origin khác nhau.

Điều này rất quan trọng khi làm:

```text
Crawler
Proxy
Security
Same-origin
Request policy
```

---

# 8. Port mặc định

Ví dụ HTTP:

```python
from yarl import URL

url = URL("http://example.com:80/novel/python")

print(url.origin())
```

Và HTTPS:

```python
url = URL("https://example.com:443/novel/python")

print(url.origin())
```

Khi xử lý origin, cần hiểu rằng **port mặc định của scheme có ý nghĩa trong việc xác định endpoint**, và cách URL được chuẩn hóa/hiển thị có thể khác tùy trường hợp.

Trong crawler, đừng tự giả định:

```python
url.origin() == "scheme://host:port"
```

luôn phải chứa port rõ ràng. Hãy để `yarl` xử lý representation của URL.

---

# 9. Origin rất hữu ích để kiểm tra crawler scope

Đây là một use case cực kỳ thực tế.

Giả sử crawler chỉ được phép crawl:

```text
https://example.com
```

Ta có:

```python
from yarl import URL

allowed_origin = URL("https://example.com")

target = URL("https://example.com/novel/python/chapter/10")

print(allowed_origin.origin())
print(target.origin())
```

Ta có thể kiểm tra:

```python
if target.origin() == allowed_origin.origin():
    print("Allowed")
else:
    print("Blocked")
```

Kết quả:

```text
Allowed
```

---

# 10. Nhưng không nên kiểm tra bằng `startswith()`

Cách nguy hiểm:

```python
if str(url).startswith("https://example.com"):
    ...
```

Ví dụ:

```text
https://example.com.evil.com
```

cũng bắt đầu bằng:

```text
https://example.com
```

nhưng rõ ràng không phải domain:

```text
example.com
```

Đây là một trong những lý do URL nên được parse thành cấu trúc thay vì kiểm tra string.

---

# 11. Dùng `origin()` cho crawler policy

Ta có thể tạo:

```python
from yarl import URL


class CrawlScope:
    def __init__(self, origin: URL):
        self._origin = origin.origin()

    def allows(self, url: URL) -> bool:
        return url.origin() == self._origin
```

Sử dụng:

```python
def main():
    scope = CrawlScope(URL("https://example.com"))

    urls = [
        URL("https://example.com/novel/python"),
        URL("https://example.com/chapter/10"),
        URL("https://other.com/novel/python"),
    ]

    for url in urls:
        print(url, "=>", scope.allows(url))


if __name__ == "__main__":
    main()
```

Kết quả:

```text
https://example.com/novel/python => True
https://example.com/chapter/10 => True
https://other.com/novel/python => False
```

---

# 12. Nhưng `origin` không đồng nghĩa với "cùng website"

Ví dụ:

```text
https://example.com
https://example.com/api
https://example.com/novel/python
```

cùng origin.

Nhưng:

```text
https://cdn.example.com
```

là origin khác.

Mặc dù:

```text
example.com
cdn.example.com
```

có liên quan về mặt domain, chúng không phải cùng origin.

Đây là distinction rất quan trọng:

```text
Origin
    ↓
scheme + host + port
```

không phải:

```text
"cùng domain gốc"
```

---

# 13. Subdomain

Ví dụ:

```python
from yarl import URL

a = URL("https://example.com")
b = URL("https://www.example.com")
c = URL("https://cdn.example.com")

print(a.origin())
print(b.origin())
print(c.origin())
```

Kết quả:

```text
https://example.com
https://www.example.com
https://cdn.example.com
```

Ba origin khác nhau.

Nếu crawler của bạn muốn cho phép subdomain, policy phải thể hiện điều đó rõ ràng.

Ví dụ:

```text
example.com
├── www.example.com
├── api.example.com
└── cdn.example.com
```

Không nên dùng `origin()` rồi suy ra:

```text
mọi subdomain đều allowed
```

---

# 14. `origin()` + `scheme`

Origin còn giúp phân biệt HTTP và HTTPS:

```python
from yarl import URL

http_url = URL("http://example.com/novel/python")

https_url = URL("https://example.com/novel/python")

print(http_url.origin())
print(https_url.origin())
```

Kết quả:

```text
http://example.com
https://example.com
```

Hai origin khác nhau.

Điều này rất hữu ích nếu crawler có policy:

```text
HTTPS only
```

---

# 15. `origin()` + `with_scheme()`

Kết hợp kiến thức Buổi 11:

```python
from yarl import URL

url = URL("http://example.com/novel/python")

print("Before:", url.origin())

https_url = url.with_scheme("https")

print("After :", https_url.origin())
```

Kết quả:

```text
Before: http://example.com
After : https://example.com
```

---

# 16. `origin()` + `with_host()`

Buổi 12:

```python
from yarl import URL

url = URL("https://example.com/novel/python")

mirror = url.with_host("mirror.example.com")

print(url.origin())
print(mirror.origin())
```

Kết quả:

```text
https://example.com
https://mirror.example.com
```

Origin thay đổi vì host thay đổi.

---

# 17. `origin()` + `with_port()`

Buổi 13:

```python
from yarl import URL

url = URL("http://localhost:8000/novel/python")

print(url.origin())

new_url = url.with_port(9000)

print(new_url.origin())
```

Kết quả:

```text
http://localhost:8000
http://localhost:9000
```

Đây là use case rất thực tế khi test crawler với local server.

---

# 18. `origin()` + `with_path()`

Buổi 14:

```python
from yarl import URL

url = URL("https://example.com/novel/python")

new_url = url.with_path("/chapter/10")

print(url.origin())
print(new_url.origin())
```

Kết quả:

```text
https://example.com
https://example.com
```

Path thay đổi nhưng origin không thay đổi.

---

# 19. `origin()` + `with_query()`

Buổi 15:

```python
from yarl import URL

url = URL("https://example.com/search?q=python")

new_url = url.with_query({"q": "sqlite"})

print(url.origin())
print(new_url.origin())
```

Kết quả:

```text
https://example.com
https://example.com
```

Query thay đổi nhưng origin không thay đổi.

---

# 20. `origin()` + `with_fragment()`

Buổi 16:

```python
from yarl import URL

url = URL("https://example.com/chapter/10#content")

new_url = url.with_fragment("comments")

print(url.origin())
print(new_url.origin())
```

Kết quả:

```text
https://example.com
https://example.com
```

Fragment không ảnh hưởng origin.

---

# 21. Bảng tổng hợp cực kỳ quan trọng

Cho:

```text
https://example.com:8080/novel/python?page=2#chapter-10
```

Ta có:

| Thành phần | Giá trị                    |
| ---------- | -------------------------- |
| `scheme`   | `https`                    |
| `host`     | `example.com`              |
| `port`     | `8080`                     |
| `path`     | `/novel/python`            |
| `query`    | `page=2`                   |
| `fragment` | `chapter-10`               |
| `origin()` | `https://example.com:8080` |

Như vậy:

```text
                    URL
                     │
       ┌─────────────┼───────────────┐
       │             │               │
     Origin         Path            Query
       │                              │
 ┌─────┼─────┐                        │
scheme host port                     ?...
                                     
                                Fragment
                                    │
                                   #...
```

---

# 22. Xây `SameOriginPolicy`

Đây là ví dụ rất phù hợp với kiến trúc crawler.

```python
from yarl import URL


class SameOriginPolicy:
    def __init__(self, base_url: URL):
        self.base_origin = base_url.origin()

    def allows(self, url: URL) -> bool:
        return url.origin() == self.base_origin
```

Test:

```python
def main():
    base_url = URL("https://example.com/novel/python")

    policy = SameOriginPolicy(base_url)

    test_urls = [
        URL("https://example.com/chapter/1"),
        URL("https://example.com/chapter/2?page=2"),
        URL("https://example.com/chapter/3#content"),
        URL("https://other.com/chapter/4"),
        URL("http://example.com/chapter/5"),
        URL("https://example.com:8080/chapter/6"),
    ]

    for url in test_urls:
        print(f"{url} -> {policy.allows(url)}")


if __name__ == "__main__":
    main()
```

Kết quả logic:

```text
https://example.com/chapter/1 -> True
https://example.com/chapter/2?page=2 -> True
https://example.com/chapter/3#content -> True
https://other.com/chapter/4 -> False
http://example.com/chapter/5 -> False
https://example.com:8080/chapter/6 -> False
```

Điểm đáng chú ý:

```text
Path khác        → vẫn True
Query khác       → vẫn True
Fragment khác    → vẫn True

Scheme khác      → False
Host khác        → False
Port khác        → False
```

Đây chính là ý nghĩa của **origin**.

---

# 23. Cẩn thận với crawler policy

Trong crawler thật, bạn có thể muốn:

```text
Allowed:
https://example.com/*
```

Nhưng đôi khi muốn:

```text
Allowed:
https://example.com/*
https://cdn.example.com/images/*
```

Lúc đó chỉ có:

```python
url.origin() == base.origin()
```

là chưa đủ.

Bạn có thể cần policy:

```text
CrawlScope
    │
    ├── allowed origins
    │
    ├── allowed paths
    │
    ├── denied paths
    │
    └── allowed schemes
```

Đây sẽ là nền tảng tốt cho bài:

> **URL Policy** ở phần Architecture sau này.

---

# 24. `origin()` và Proxy

Trong Fetcher mà chúng ta đã xây dựng, URL có thể đi qua proxy.

Ví dụ:

```text
Target:
https://example.com/novel/python

Proxy:
http://127.0.0.1:8080
```

Origin của target vẫn là:

```text
https://example.com
```

Proxy không làm thay đổi:

```python
url.origin()
```

Đây là điểm quan trọng:

```text
Target URL
    ↓
origin()
    ↓
https://example.com
```

Proxy là **transport configuration**, không phải origin của resource.

---

# 25. Complete example cho Novel Crawler

```python
from yarl import URL


class CrawlScope:
    def __init__(self, base_url: URL):
        self.base_origin = base_url.origin()

    def allows(self, url: URL) -> bool:
        return url.origin() == self.base_origin


def main():
    base_url = URL("https://example.com/novel/python")

    scope = CrawlScope(base_url)

    urls = [
        URL("https://example.com/novel/python"),
        URL("https://example.com/novel/python/chapter/1"),
        URL("https://example.com/novel/python/chapter/2?page=2"),
        URL("https://example.com/novel/python/chapter/3#content"),
        URL("https://cdn.example.com/image.jpg"),
        URL("https://other.example.com/chapter/1"),
        URL("http://example.com/chapter/1"),
    ]

    print("Base origin:")
    print(scope.base_origin)

    print("\nCrawl scope:")
    print("-" * 70)

    for url in urls:
        status = "ALLOW" if scope.allows(url) else "BLOCK"

        print(f"{status:5} | {url.origin():35} | {url}")


if __name__ == "__main__":
    main()
```

Kiểu output:

```text
Base origin:
https://example.com

Crawl scope:
----------------------------------------------------------------------
ALLOW | https://example.com             | https://example.com/novel/python
ALLOW | https://example.com             | https://example.com/novel/python/chapter/1
ALLOW | https://example.com             | https://example.com/novel/python/chapter/2?page=2
ALLOW | https://example.com             | https://example.com/novel/python/chapter/3#content
BLOCK | https://cdn.example.com         | https://cdn.example.com/image.jpg
BLOCK | https://other.example.com       | https://other.example.com/chapter/1
BLOCK | http://example.com              | http://example.com/chapter/1
```

---

# 26. Phần II đã hoàn thành

Chúng ta đã đi qua nhóm URL manipulation:

```text
11. with_scheme()
12. with_host()
13. with_port()
14. with_path()
15. with_query()
16. with_fragment()
17. with_name()
18. with_suffix()
19. parent
20. origin()
```

Có thể hình dung:

```text
                    yarl.URL
                       │
          ┌────────────┼────────────┐
          │            │            │
       Endpoint       Path         State
          │            │            │
   scheme/host/port   path         query
                                   fragment
          │            │
   with_scheme()    with_path()
   with_host()      with_name()
   with_port()      with_suffix()
                    parent
```

---

# 27. Tổng kết kiến thức cần nhớ

## Lấy origin

```python
url.origin()
```

Ví dụ:

```text
https://example.com:8080
```

---

## Origin không chứa

```text
/path
?query
#fragment
```

---

## Origin phụ thuộc vào

```text
scheme
host
port
```

---

## Rất hữu ích cho crawler

```python
url.origin() == base_url.origin()
```

để xây **same-origin / crawl-scope policy**.

Nhưng nhớ:

> `origin()` không phải "domain gốc" theo nghĩa subdomain. `example.com` và `cdn.example.com` là hai origin khác nhau.

---

# Bài tập Buổi 20

Cho:

```python
from yarl import URL

url = URL("https://example.com:8443/novel/python/chapter/10?page=2#content")
```

### Bài 1

In:

```text
scheme
host
port
path
query
fragment
origin
```

---

### Bài 2

Tạo:

```python
new_url = url.with_path("/novel/python/chapter/20")
```

Kiểm tra:

```python
url.origin() == new_url.origin()
```

Kết quả phải là:

```text
True
```

---

### Bài 3

Tạo URL:

```text
http://example.com:8443/novel/python
```

và kiểm tra origin có giống URL ban đầu không.

---

### Bài 4 — crawler

Viết:

```python
def same_origin(a: URL, b: URL) -> bool: ...
```

sao cho:

```python
same_origin(URL("https://example.com/a"), URL("https://example.com/b"))
```

→ `True`

nhưng:

```python
same_origin(URL("https://example.com/a"), URL("https://other.com/b"))
```

→ `False`.

---

### Bài 5 — quan trọng

Viết:

```python
class CrawlScope: ...
```

với:

```python
scope = CrawlScope(URL("https://example.com/novel/python"))
```

và method:

```python
scope.allows(url)
```

Chỉ cho phép URL có cùng origin.

---

## 🎯 Sau Buổi 20

Bạn đã có nền tảng đủ tốt để chuyển sang **Phần III — Query String chuyên sâu**:

```text
21. URL.with_query()
22. Dictionary → query
23. List/Tuple → query
24. Duplicate query parameters
25. query
26. query_string
27. query.get()
28. query.getall()
29. Encoding / decoding
30. Unicode trong URL
```

Phần III sẽ đặc biệt quan trọng cho crawler vì chúng ta sẽ xử lý những URL kiểu:

```text
/search?keyword=python&page=2
/search?tag=python&tag=sqlite
/chapter?id=123&source=abc
```

và học kỹ cách **đọc, sửa, giữ duplicate parameters và xây query URL một cách an toàn**.
