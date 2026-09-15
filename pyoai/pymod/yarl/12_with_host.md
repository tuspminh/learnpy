# Buổi 12 — `with_host()`

Hôm nay chúng ta học:

```python
URL.with_host()
```

Đây là phương thức dùng để **thay đổi host/domain của URL** mà vẫn giữ các thành phần khác như `scheme`, `path`, `query`, `fragment`.

---

## 1. Host là gì?

Ví dụ:

```text
https://www.example.com:8080/novel/python?page=2#chapter-10
         ^^^^^^^^^^^^^^^
              host
```

Với:

```python
from yarl import URL

url = URL("https://www.example.com:8080/novel/python?page=2#chapter-10")
```

Ta có:

```python
print(url.scheme)
print(url.host)
print(url.port)
print(url.path)
print(url.query_string)
print(url.fragment)
```

Kết quả:

```text
https
www.example.com
8080
/novel/python
page=2
chapter-10
```

---

# 2. `with_host()` cơ bản

Cú pháp:

```python
new_url = url.with_host("new-host.com")
```

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/novel/python")

new_url = url.with_host("mirror.example.com")

print(url)
print(new_url)
```

Kết quả:

```text
https://example.com/novel/python
https://mirror.example.com/novel/python
```

URL ban đầu vẫn không thay đổi.

---

# 3. `with_host()` cũng tuân theo immutable

Đây là lỗi rất dễ gặp:

```python
url = URL("https://example.com/novel/python")

url.with_host("mirror.example.com")

print(url)
```

Kết quả:

```text
https://example.com/novel/python
```

Phải gán kết quả:

```python
url = url.with_host("mirror.example.com")
```

hoặc:

```python
mirror_url = url.with_host("mirror.example.com")
```

---

# 4. Host thay đổi, path không thay đổi

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/novel/python/chapter-10")

new_url = url.with_host("cdn.example.com")

print(new_url)
```

Kết quả:

```text
https://cdn.example.com/novel/python/chapter-10
```

Ta chỉ thay:

```text
example.com
```

thành:

```text
cdn.example.com
```

Path:

```text
/novel/python/chapter-10
```

vẫn giữ nguyên.

---

# 5. Query cũng được giữ nguyên

```python
from yarl import URL

url = URL("https://example.com/novel/python?page=2&sort=new")

new_url = url.with_host("mirror.example.com")

print(new_url)
```

Kết quả:

```text
https://mirror.example.com/novel/python?page=2&sort=new
```

Query vẫn là:

```text
page=2&sort=new
```

---

# 6. Fragment cũng được giữ nguyên

```python
from yarl import URL

url = URL("https://example.com/novel/python?page=2#chapter-10")

new_url = url.with_host("mirror.example.com")

print(new_url)
```

Kết quả:

```text
https://mirror.example.com/novel/python?page=2#chapter-10
```

Chỉ host thay đổi.

---

# 7. Nhìn toàn bộ cấu trúc

Cho URL:

```text
https://example.com:8080/novel/python?page=2#chapter-10
```

Ta có:

```text
scheme       https
host         example.com
port         8080
path         /novel/python
query        page=2
fragment     chapter-10
```

Sau:

```python
new_url = url.with_host("mirror.example.com")
```

ta có:

```text
scheme       https       ← giữ
host         mirror.example.com ← thay
port         8080        ← giữ
path         /novel/python ← giữ
query        page=2      ← giữ
fragment     chapter-10  ← giữ
```

---

# 8. Ví dụ đầy đủ để kiểm tra

```python
from yarl import URL


url = URL("https://example.com:8080/novel/python?page=2&sort=new#chapter-10")

new_url = url.with_host("mirror.example.com")


print("Original:")
print(url)

print("\nNew:")
print(new_url)

print("\nComponents:")

print("scheme  :", new_url.scheme)
print("host    :", new_url.host)
print("port    :", new_url.port)
print("path    :", new_url.path)
print("query   :", new_url.query_string)
print("fragment:", new_url.fragment)
```

Kết quả:

```text
Original:
https://example.com:8080/novel/python?page=2&sort=new#chapter-10

New:
https://mirror.example.com:8080/novel/python?page=2&sort=new#chapter-10

Components:
scheme  : https
host    : mirror.example.com
port    : 8080
path    : /novel/python
query   : page=2&sort=new
fragment: chapter-10
```

---

# 9. `with_host()` không giống `with_path()`

Đây là điểm cần phân biệt.

### Thay host

```python
url.with_host("mirror.example.com")
```

```text
https://mirror.example.com/novel/python
```

### Thay path

```python
url.with_path("/book/python")
```

```text
https://example.com/book/python
```

Có thể hình dung:

```text
https://example.com/novel/python
        ^^^^^^^^^^^
           host

https://example.com/novel/python
                     ^^^^^^^^^^^^^
                         path
```

---

# 10. Host và hostname/domain

Trong yarl:

```python
url.host
```

là host đã được phân tích theo URL.

Ví dụ:

```python
url = URL("https://www.example.com:8080/novel")

print(url.host)
print(url.port)
```

Kết quả:

```text
www.example.com
8080
```

`with_host()` chỉ thay phần host:

```python
url.with_host("mirror.example.com")
```

---

# 11. Host có thể là subdomain khác

Ví dụ website có:

```text
www.example.com
api.example.com
cdn.example.com
img.example.com
```

Ta có:

```python
from yarl import URL

url = URL("https://www.example.com/novel/python")

api_url = url.with_host("api.example.com")
cdn_url = url.with_host("cdn.example.com")
img_url = url.with_host("img.example.com")

print(api_url)
print(cdn_url)
print(img_url)
```

Kết quả:

```text
https://api.example.com/novel/python
https://cdn.example.com/novel/python
https://img.example.com/novel/python
```

---

# 12. Ứng dụng rất thực tế: Mirror

Đây là một trường hợp khá phù hợp với crawler.

Giả sử:

```text
https://truyen.example.com/novel/python
```

Website có mirror:

```text
https://mirror.example.com
```

Ta có thể chuyển:

```python
from yarl import URL

url = URL("https://truyen.example.com/novel/python")

mirror_url = url.with_host("mirror.example.com")

print(mirror_url)
```

Kết quả:

```text
https://mirror.example.com/novel/python
```

---

# 13. Nhưng có một vấn đề quan trọng

`with_host()` **không đảm bảo host mới có resource tương ứng**.

Ví dụ:

```python
url = URL("https://truyen.example.com/novel/python")

mirror_url = url.with_host("mirror.example.com")
```

Yarl chỉ tạo:

```text
https://mirror.example.com/novel/python
```

Nó không biết:

```text
mirror.example.com
```

có tồn tại hay không.

Cũng giống `with_scheme()`:

```text
yarl
 ↓
thay đổi URL
 ↓
không gửi HTTP request
```

Việc kiểm tra server phải thuộc về Fetcher/httpx.

---

# 14. Thiết kế Mirror Resolver

Nếu crawler có nhiều domain mirror, không nên viết lung tung:

```python
url.with_host(...)
```

ở nhiều nơi.

Ta có thể tạo một class:

```python
from yarl import URL


class MirrorResolver:
    def __init__(self, mirror_host: str):
        self._mirror_host = mirror_host

    def resolve(self, url: URL) -> URL:
        return url.with_host(self._mirror_host)
```

Sử dụng:

```python
url = URL("https://truyen.example.com/novel/python")

resolver = MirrorResolver("mirror.example.com")

mirror_url = resolver.resolve(url)

print(mirror_url)
```

Kết quả:

```text
https://mirror.example.com/novel/python
```

---

# 15. Resolver với nhiều mirror

Ta có thể mở rộng:

```python
from yarl import URL


class MirrorResolver:
    def __init__(self, mirrors: list[str]):
        self._mirrors = mirrors

    def resolve_all(self, url: URL) -> list[URL]:
        return [url.with_host(host) for host in self._mirrors]
```

Sử dụng:

```python
url = URL("https://truyen.example.com/novel/python")

resolver = MirrorResolver(
    [
        "mirror1.example.com",
        "mirror2.example.com",
        "mirror3.example.com",
    ]
)

urls = resolver.resolve_all(url)

for item in urls:
    print(item)
```

Kết quả:

```text
https://mirror1.example.com/novel/python
https://mirror2.example.com/novel/python
https://mirror3.example.com/novel/python
```

---

# 16. Đây là chỗ `yarl` rất phù hợp với crawler

Thay vì:

```python
url = "https://truyen.example.com/novel/python"

mirror = url.replace("truyen.example.com", "mirror.example.com")
```

ta dùng:

```python
url = URL("https://truyen.example.com/novel/python")

mirror = url.with_host("mirror.example.com")
```

Lợi ích:

```text
String manipulation
        ↓
dễ lỗi
        ↓
URL manipulation
        ↓
yarl
        ↓
cấu trúc URL rõ ràng
```

---

# 17. Host + port

Đây là điểm cần chú ý.

Giả sử:

```python
from yarl import URL

url = URL("https://example.com:8080/novel/python")

new_url = url.with_host("mirror.example.com")

print(new_url)
```

Kết quả:

```text
https://mirror.example.com:8080/novel/python
```

**Host thay đổi nhưng port vẫn giữ nguyên.**

Nếu muốn thay cả port thì đó là việc của:

```python
with_port()
```

mà chúng ta sẽ học ở **Buổi 13**.

---

# 18. Host + scheme có thể chain

Các phương thức `with_*()` có thể kết hợp.

```python
from yarl import URL


url = URL("http://example.com/novel/python?page=2")

new_url = url.with_scheme("https").with_host("mirror.example.com")

print(new_url)
```

Kết quả:

```text
https://mirror.example.com/novel/python?page=2
```

Luồng:

```text
http://example.com/novel/python?page=2
             │
             ▼
with_scheme("https")
             │
             ▼
https://example.com/novel/python?page=2
             │
             ▼
with_host("mirror.example.com")
             │
             ▼
https://mirror.example.com/novel/python?page=2
```

---

# 19. Rất quan trọng: mỗi lần đều tạo URL mới

Ví dụ:

```python
from yarl import URL


original = URL("http://example.com/novel/python")

https_url = original.with_scheme("https")

mirror_url = https_url.with_host("mirror.example.com")

print(original)
print(https_url)
print(mirror_url)
```

Kết quả:

```text
http://example.com/novel/python

https://example.com/novel/python

https://mirror.example.com/novel/python
```

Ta có một chuỗi transformation:

```text
original
   │
   ├── with_scheme()
   │
   ▼
https_url
   │
   ├── with_host()
   │
   ▼
mirror_url
```

Đây là một pattern rất đẹp khi xử lý URL.

---

# 20. `with_host()` trong kiến trúc Novel Crawler

Với hệ thống crawler của bạn, có thể hình dung:

```text
                 HTML
                  │
                  ▼
               Parser
                  │
                  ▼
             URL("...")
                  │
                  ▼
           URL Policy
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
 with_scheme()         with_host()
        │                   │
        └─────────┬─────────┘
                  ▼
             Final URL
                  │
                  ▼
               Fetcher
                  │
                  ▼
                httpx
```

Điểm quan trọng là:

**Parser không cần biết cách xử lý mirror.**

Parser chỉ cần trả về:

```python
URL(href)
```

Application/domain policy quyết định URL nào được sử dụng.

---

# 21. Mini Project hoàn chỉnh

Tạo:

```text
lesson_12.py
```

```python
from yarl import URL


class MirrorResolver:
    def __init__(self, mirrors: list[str]):
        self._mirrors = mirrors

    def resolve_all(self, url: URL) -> list[URL]:
        return [url.with_host(host) for host in self._mirrors]


def main() -> None:

    original = URL("https://truyen.example.com/novel/python?page=2#chapter-10")

    resolver = MirrorResolver(
        [
            "mirror1.example.com",
            "mirror2.example.com",
            "mirror3.example.com",
        ]
    )

    print("Original:")
    print(original)

    print("\nMirrors:")

    for url in resolver.resolve_all(original):
        print(url)


if __name__ == "__main__":
    main()
```

Kết quả:

```text
Original:
https://truyen.example.com/novel/python?page=2#chapter-10

Mirrors:
https://mirror1.example.com/novel/python?page=2#chapter-10
https://mirror2.example.com/novel/python?page=2#chapter-10
https://mirror3.example.com/novel/python?page=2#chapter-10
```

Bạn có thể thấy rất rõ:

```text
             ORIGINAL
                 │
       ┌─────────┼─────────┐
       ▼         ▼         ▼
   mirror 1  mirror 2  mirror 3
       │         │         │
       └─────────┼─────────┘
                 │
        path/query/fragment
           vẫn giữ nguyên
```

---

# 22. Bài tập

### Bài 1 — Cơ bản

Cho:

```python
url = URL("https://example.com/novel/python?page=2")
```

Đổi host thành:

```text
mirror.example.com
```

---

### Bài 2 — Kiểm tra immutable

Chứng minh rằng:

```python
original
```

không thay đổi sau khi gọi:

```python
original.with_host(...)
```

---

### Bài 3 — Mirror

Viết:

```python
def create_mirror_url(url: URL, mirror_host: str) -> URL: ...
```

Ví dụ:

```python
url = URL("https://example.com/novel/python?page=2")

mirror = create_mirror_url(url, "mirror.example.com")

print(mirror)
```

Mong muốn:

```text
https://mirror.example.com/novel/python?page=2
```

---

### Bài 4 — Chain

Cho:

```text
http://example.com/novel/python?page=2
```

Hãy tạo:

```text
https://mirror.example.com/novel/python?page=2
```

chỉ bằng các phương thức `yarl`, không dùng `replace()`.

---

## Tóm tắt Buổi 12

| Mục đích    | Code                           |
| ----------- | ------------------------------ |
| Lấy host    | `url.host`                     |
| Thay host   | `url.with_host("example.com")` |
| Giữ URL gốc | Có                             |
| Thay path   | `with_path()`                  |
| Thay port   | `with_port()`                  |
| Thay scheme | `with_scheme()`                |

Pattern quan trọng:

```python
new_url = url.with_scheme("https").with_host("mirror.example.com")
```

Và tư duy cần giữ từ buổi này:

> **`yarl` không gửi request; `yarl` giúp ta biến đổi URL một cách có cấu trúc.**

**Buổi 13 — `with_port()`** sẽ nối tiếp rất tự nhiên: thay đổi port, xử lý `80/443`, port mặc định và cách kết hợp `host + port` trong crawler.
