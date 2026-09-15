# Buổi 13 — `with_port()`

Hôm nay chúng ta học:

```python
URL.with_port()
```

Mục tiêu là hiểu cách **thay đổi port của URL** bằng `yarl`, đồng thời phân biệt rõ:

* `host`
* `port`
* `scheme`
* port mặc định của HTTP/HTTPS
* `with_port(None)`
* cách ứng dụng trong **Novel Crawler**

---

# 1. Port là gì?

Ví dụ:

```text
https://example.com:8080/novel/python
                  ^^^^
                  port
```

URL được chia thành:

```text
https://example.com:8080/novel/python
^^^^^   ^^^^^^^^^^^ ^^^^
scheme     host     port
```

Với `yarl`:

```python
from yarl import URL

url = URL("https://example.com:8080/novel/python")

print("scheme:", url.scheme)
print("host  :", url.host)
print("port  :", url.port)
```

Kết quả:

```text
scheme: https
host  : example.com
port  : 8080
```

---

# 2. `with_port()` cơ bản

Cú pháp:

```python
new_url = url.with_port(9000)
```

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com:8080/novel/python")

new_url = url.with_port(9000)

print(url)
print(new_url)
```

Kết quả:

```text
https://example.com:8080/novel/python
https://example.com:9000/novel/python
```

Chỉ port thay đổi.

---

# 3. URL immutable

Giống hai buổi trước:

```python
url.with_port(9000)
```

không thay đổi `url`.

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com:8080/novel/python")

url.with_port(9000)

print(url)
```

Vẫn là:

```text
https://example.com:8080/novel/python
```

Phải:

```python
url = url.with_port(9000)
```

hoặc:

```python
new_url = url.with_port(9000)
```

---

# 4. Port không ảnh hưởng đến path

```python
from yarl import URL

url = URL("https://example.com:8080/novel/python/chapter-10")

new_url = url.with_port(9000)

print(new_url)
```

Kết quả:

```text
https://example.com:9000/novel/python/chapter-10
```

Path:

```text
/novel/python/chapter-10
```

vẫn giữ nguyên.

---

# 5. Query và fragment cũng giữ nguyên

```python
from yarl import URL

url = URL("https://example.com:8080/novel/python?page=2&sort=new#chapter-10")

new_url = url.with_port(9000)

print(new_url)
```

Kết quả:

```text
https://example.com:9000/novel/python?page=2&sort=new#chapter-10
```

Ta có:

```text
scheme      https       ← giữ
host        example.com ← giữ
port        8080 → 9000 ← thay
path        /novel/python ← giữ
query       page=2&sort=new ← giữ
fragment    chapter-10 ← giữ
```

---

# 6. Kiểm tra bằng code

```python
from yarl import URL


url = URL("https://example.com:8080/novel/python?page=2#chapter-10")

new_url = url.with_port(9000)


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
https://example.com:8080/novel/python?page=2#chapter-10

New:
https://example.com:9000/novel/python?page=2#chapter-10

Components:
scheme  : https
host    : example.com
port    : 9000
path    : /novel/python
query   : page=2
fragment: chapter-10
```

---

# 7. Port mặc định

Đây là phần rất quan trọng.

HTTP thường sử dụng:

```text
http  → 80
https → 443
```

Ví dụ:

```python
from yarl import URL

http_url = URL("http://example.com")
https_url = URL("https://example.com")

print(http_url.port)
print(https_url.port)
```

Trong URL không ghi port:

```text
http://example.com
https://example.com
```

`yarl` vẫn hiểu port mặc định tương ứng trong thuộc tính URL.

Điều này khác với việc URL có ghi rõ:

```text
https://example.com:443
```

và:

```text
https://example.com
```

Trong nhiều trường hợp chúng trỏ đến cùng endpoint mạng, nhưng **chuỗi URL có thể khác nhau**.

---

# 8. Đặt port 443 cho HTTPS

Ta có thể viết:

```python
from yarl import URL

url = URL("http://example.com/novel/python")

url = url.with_scheme("https")
url = url.with_port(443)

print(url)
```

Kết quả sẽ biểu diễn URL với port đã chỉ định.

Tuy nhiên, trong thực tế **không nhất thiết phải ghi `:443`**.

Thông thường:

```text
https://example.com
```

đã đủ để client sử dụng HTTPS port mặc định.

Do đó:

```python
url.with_scheme("https")
```

thường là đủ nếu mục tiêu chỉ là chuyển HTTP → HTTPS.

---

# 9. `with_port(None)` — xóa explicit port

Đây là tính năng rất hữu ích.

Giả sử:

```python
from yarl import URL

url = URL("https://example.com:8080/novel/python")

print(url)
```

Ta có:

```text
https://example.com:8080/novel/python
```

Muốn bỏ port explicit:

```python
new_url = url.with_port(None)

print(new_url)
```

Kết quả:

```text
https://example.com/novel/python
```

Đây là một pattern cần nhớ:

```python
url.with_port(9000)  # thay port
url.with_port(None)  # bỏ explicit port
```

---

# 10. Ví dụ thực tế

```python
from yarl import URL


url = URL("https://example.com:8080/novel/python")

print("Original:")
print(url)

without_port = url.with_port(None)

print("\nWithout explicit port:")
print(without_port)
```

Kết quả:

```text
Original:
https://example.com:8080/novel/python

Without explicit port:
https://example.com/novel/python
```

---

# 11. `with_port()` không thay host

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com:8080/novel/python")

new_url = url.with_port(9000)

print(new_url.host)
print(new_url.port)
```

Kết quả:

```text
example.com
9000
```

Host vẫn:

```text
example.com
```

Port:

```text
8080 → 9000
```

Nếu muốn thay host:

```python
url.with_host("mirror.example.com")
```

---

# 12. Có thể chain `with_host()` và `with_port()`

Ví dụ:

```python
from yarl import URL

url = URL("http://example.com:8080/novel/python")

new_url = url.with_scheme("https").with_host("mirror.example.com").with_port(8443)

print(new_url)
```

Kết quả:

```text
https://mirror.example.com:8443/novel/python
```

Ta vừa thay:

```text
http
 ↓
https
```

```text
example.com
 ↓
mirror.example.com
```

```text
8080
 ↓
8443
```

---

# 13. Đây chính là URL transformation pipeline

Ta có thể hình dung:

```text
http://example.com:8080/novel/python
       │
       │ with_scheme()
       ▼
https://example.com:8080/novel/python
       │
       │ with_host()
       ▼
https://mirror.example.com:8080/novel/python
       │
       │ with_port()
       ▼
https://mirror.example.com:8443/novel/python
```

Đây là một trong những lý do `yarl` rất phù hợp để xây dựng URL layer cho crawler.

---

# 14. Port validation

Port phải nằm trong khoảng hợp lệ của TCP/UDP:

```text
0 → 65535
```

Trong application code, nếu nhận port từ config/user input, nên validate.

Ví dụ:

```python
def validate_port(port: int) -> None:
    if not 0 <= port <= 65535:
        raise ValueError(f"Invalid port: {port}")
```

Sau đó:

```python
validate_port(8080)
```

---

# 15. Không nên tự ghép port bằng string

Không nên:

```python
url = "https://example.com/novel/python"

url = url.replace("example.com", "example.com:8080")
```

Đây là string manipulation.

Với `yarl`:

```python
from yarl import URL

url = URL("https://example.com/novel/python")

url = url.with_port(8080)
```

URL vẫn được xử lý như một cấu trúc URL.

---

# 16. Port trong Novel Crawler

Thông thường crawler production sẽ dùng:

```text
https://truyen.example.com
```

không cần port explicit.

Nhưng khi **development/testing**, bạn rất hay gặp:

```text
http://localhost:8000
http://localhost:8080
http://127.0.0.1:9000
```

Ví dụ parser sinh ra:

```python
from yarl import URL

url = URL("https://truyen.example.com/novel/python")
```

Trong môi trường test, ta muốn chuyển sang server local:

```python
test_url = url.with_host("localhost").with_port(8000)

print(test_url)
```

Kết quả:

```text
https://localhost:8000/novel/python
```

Đây là một use case rất thực tế cho **integration testing**.

---

# 17. Test server cho crawler

Giả sử crawler bình thường:

```text
https://truyen.example.com/novel/python
```

Nhưng khi test:

```text
http://localhost:8000/novel/python
```

Ta có:

```python
from yarl import URL


production_url = URL("https://truyen.example.com/novel/python")

test_url = production_url.with_scheme("http").with_host("localhost").with_port(8000)

print("Production:")
print(production_url)

print("\nTest:")
print(test_url)
```

Kết quả:

```text
Production:
https://truyen.example.com/novel/python

Test:
http://localhost:8000/novel/python
```

Điểm hay:

**Path `/novel/python` được giữ nguyên.**

---

# 18. Xây `TestURLResolver`

Nếu muốn tách logic này:

```python
from yarl import URL


class TestURLResolver:
    def __init__(
        self,
        host: str,
        port: int,
        scheme: str = "http",
    ):
        self._host = host
        self._port = port
        self._scheme = scheme

    def resolve(self, url: URL) -> URL:
        return url.with_scheme(self._scheme).with_host(self._host).with_port(self._port)
```

Sử dụng:

```python
production_url = URL("https://truyen.example.com/novel/python?page=2")

resolver = TestURLResolver(
    host="localhost",
    port=8000,
)

test_url = resolver.resolve(production_url)

print(test_url)
```

Kết quả:

```text
http://localhost:8000/novel/python?page=2
```

---

# 19. Một điểm kiến trúc rất đáng chú ý

Không nên để `Parser` tự quyết định:

```python
url.with_host(...)
url.with_port(...)
url.with_scheme(...)
```

Parser nên tập trung vào:

```text
HTML
 ↓
parse
 ↓
URL
```

Còn các policy như:

```text
HTTPS
Mirror
Test server
Proxy
Environment
```

nên thuộc tầng phù hợp của application/infrastructure.

Ví dụ:

```text
                 Parser
                   │
                   ▼
             URL("...")
                   │
                   ▼
           URL Transformation
            │       │       │
            ▼       ▼       ▼
         scheme    host    port
                   │
                   ▼
                Fetcher
                   │
                   ▼
                 httpx
```

Đây chính là tư duy DDD/SOLID mà chúng ta đã dùng trong Fetcher.

---

# 20. Mini Project — `EndpointResolver`

Ta ghép ba bài đã học:

* `with_scheme()`
* `with_host()`
* `with_port()`

```python
from yarl import URL


class EndpointResolver:
    def __init__(
        self,
        scheme: str,
        host: str,
        port: int | None = None,
    ):
        self._scheme = scheme
        self._host = host
        self._port = port

    def resolve(self, url: URL) -> URL:
        result = url.with_scheme(self._scheme).with_host(self._host)

        if self._port is not None:
            result = result.with_port(self._port)
        else:
            result = result.with_port(None)

        return result


def main() -> None:

    original = URL("https://truyen.example.com/novel/python?page=2#chapter-10")

    resolver = EndpointResolver(
        scheme="http",
        host="localhost",
        port=8000,
    )

    result = resolver.resolve(original)

    print("Original:")
    print(original)

    print("\nResolved:")
    print(result)


if __name__ == "__main__":
    main()
```

Kết quả:

```text
Original:
https://truyen.example.com/novel/python?page=2#chapter-10

Resolved:
http://localhost:8000/novel/python?page=2#chapter-10
```

---

# 21. Bài tập thực hành

### Bài 1

Cho:

```python
url = URL("https://example.com:8080/novel/python?page=2")
```

Đổi port thành:

```text
9000
```

---

### Bài 2

Xóa explicit port:

```python
url = URL("https://example.com:8080/novel/python")
```

Mong muốn:

```text
https://example.com/novel/python
```

---

### Bài 3

Tạo URL:

```text
https://mirror.example.com:8443/novel/python?page=2
```

từ:

```text
http://example.com:8080/novel/python?page=2
```

Chỉ sử dụng:

```python
with_scheme()
with_host()
with_port()
```

---

### Bài 4 — Crawler

Viết:

```python
class EndpointResolver: ...
```

nhận:

```python
scheme
host
port
```

và chuyển một `URL` bất kỳ sang endpoint đó nhưng **giữ nguyên path + query + fragment**.

---

# Tổng kết Buổi 13

Ba phương thức chúng ta đã có:

```python
url.with_scheme("https")
url.with_host("mirror.example.com")
url.with_port(8443)
```

Có thể chain:

```python
new_url = url.with_scheme("https").with_host("mirror.example.com").with_port(8443)
```

Kết quả:

```text
https://mirror.example.com:8443/novel/python
```

Và đặc biệt:

```python
url.with_port(None)
```

→ xóa **explicit port**.

### Bức tranh hiện tại

```text
URL
 │
 ├── with_scheme()  → scheme
 ├── with_host()    → host
 └── with_port()    → port
```

**Buổi 14 — `with_path()`** sẽ quan trọng hơn nữa đối với Novel Crawler: chúng ta sẽ học cách thay toàn bộ path, xử lý `/novel/...`, `/chapter/...`, trailing slash, encoded path và cách tránh nhầm `with_path()` với phép `/` của `yarl`.
