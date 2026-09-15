# Buổi 11 — `with_scheme()`

Hôm nay chúng ta bắt đầu **Phần II — URL Manipulation**, với phương thức:

```python
URL.with_scheme()
```

Mục tiêu là hiểu thật chắc cách **thay đổi scheme của URL mà không làm thay đổi URL gốc**.

---

# 1. `scheme` là gì?

Ví dụ:

```text
https://example.com/novel/abc?page=2#top
^^^^^
scheme
```

Một URL thường có dạng:

```text
scheme://host/path?query#fragment
```

Ví dụ:

```python
from yarl import URL

url = URL("http://example.com/novel/abc?page=2")
```

Ta có:

```python
print(url.scheme)
print(url.host)
print(url.path)
print(url.query_string)
```

Kết quả:

```text
http
example.com
/novel/abc
page=2
```

---

# 2. `with_scheme()` dùng để làm gì?

Cú pháp:

```python
new_url = url.with_scheme("https")
```

Ví dụ:

```python
from yarl import URL

url = URL("http://example.com/novel/abc")

new_url = url.with_scheme("https")

print(url)
print(new_url)
```

Kết quả:

```text
http://example.com/novel/abc
https://example.com/novel/abc
```

URL ban đầu **không bị thay đổi**.

---

# 3. Đây là điểm cực kỳ quan trọng: URL immutable

`yarl.URL` là immutable.

Nghĩa là:

```python
url = URL("http://example.com/novel/abc")

url.with_scheme("https")

print(url)
```

Kết quả vẫn là:

```text
http://example.com/novel/abc
```

Bởi vì:

```python
url.with_scheme("https")
```

trả về **một URL mới**.

Phải viết:

```python
url = url.with_scheme("https")
```

hoặc:

```python
secure_url = url.with_scheme("https")
```

---

# 4. Ví dụ đầy đủ

```python
from yarl import URL


url = URL("http://example.com/novel/python?page=2")


print("Original:")
print(url)

secure_url = url.with_scheme("https")


print("\nNew URL:")
print(secure_url)


print("\nScheme:")
print("Original:", url.scheme)
print("New:", secure_url.scheme)
```

Kết quả:

```text
Original:
http://example.com/novel/python?page=2

New URL:
https://example.com/novel/python?page=2

Scheme:
Original: http
New: https
```

---

# 5. `with_scheme()` chỉ thay scheme

Ví dụ:

```python
url = URL("http://example.com:8080/novel/python?page=2#chapter-10")

new_url = url.with_scheme("https")
```

Ta kiểm tra:

```python
print(new_url)
```

Kết quả:

```text
https://example.com:8080/novel/python?page=2#chapter-10
```

Chỉ có:

```text
http
```

được thay thành:

```text
https
```

Các thành phần khác vẫn giữ nguyên:

```text
host       example.com
port       8080
path       /novel/python
query      page=2
fragment   chapter-10
```

---

# 6. Kiểm tra từng thành phần

```python
from yarl import URL


url = URL("http://example.com:8080/novel/python?page=2#chapter-10")

new_url = url.with_scheme("https")


print("scheme:", new_url.scheme)
print("host:", new_url.host)
print("port:", new_url.port)
print("path:", new_url.path)
print("query:", new_url.query)
print("fragment:", new_url.fragment)
```

Kết quả:

```text
scheme: https
host: example.com
port: 8080
path: /novel/python
query: <MultiDictProxy('page': '2')>
fragment: chapter-10
```

Điểm cần nhớ:

> `with_scheme()` không phải là phương thức xây lại URL từ đầu. Nó tạo một URL mới với scheme được thay đổi.

---

# 7. HTTP → HTTPS

Đây là trường hợp phổ biến nhất.

```python
from yarl import URL


url = URL("http://example.com/novel/python")

https_url = url.with_scheme("https")

print(https_url)
```

Kết quả:

```text
https://example.com/novel/python
```

Ta có thể viết thành function:

```python
from yarl import URL


def force_https(url: URL) -> URL:
    return url.with_scheme("https")


url = URL("http://example.com/novel/python")

secure_url = force_https(url)

print(secure_url)
```

---

# 8. Nhưng `with_scheme()` không kiểm tra website có hỗ trợ HTTPS

Đây là điểm rất quan trọng khi làm crawler.

```python
url = URL("http://example.com/novel/python")

https_url = url.with_scheme("https")
```

`yarl` tạo ra:

```text
https://example.com/novel/python
```

Nhưng điều đó **không có nghĩa server chắc chắn hỗ trợ HTTPS**.

`yarl` chỉ thực hiện:

```text
http
 ↓
https
```

Nó không gửi HTTP request.

Việc HTTPS có hoạt động hay không phải do HTTP client như `httpx` kiểm tra.

Ví dụ kiến trúc:

```text
yarl
 │
 │ URL manipulation
 ▼
https://example.com/novel/python
 │
 ▼
httpx
 │
 │ HTTP request
 ▼
Server
```

---

# 9. Không nên dùng `str.replace()`

Một cách dễ nghĩ ra:

```python
url = "http://example.com/novel/python"

url = url.replace("http://", "https://")
```

Không nên làm như vậy trong hệ thống crawler.

### Cách string

```python
url.replace("http://", "https://")
```

là thao tác text.

### Cách `yarl`

```python
url.with_scheme("https")
```

là thao tác trên **cấu trúc URL**.

Ví dụ:

```python
from yarl import URL

url = URL("http://example.com/novel/python?page=2")

secure_url = url.with_scheme("https")
```

Ta vẫn giữ được toàn bộ cấu trúc:

```text
scheme
host
path
query
fragment
```

---

# 10. Scheme có thể không chỉ là HTTP

Scheme không chỉ có:

```text
http
https
```

Một số scheme khác:

```text
ftp
ws
wss
file
```

Ví dụ:

```python
from yarl import URL


url = URL("http://example.com/data")

print(url.with_scheme("https"))
print(url.with_scheme("ftp"))
```

Kết quả tương ứng:

```text
https://example.com/data
ftp://example.com/data
```

Tuy nhiên, **việc yarl cho phép thay scheme không có nghĩa ứng dụng của bạn nên sử dụng scheme đó**.

Trong Novel Crawler, ta thường giới hạn:

```python
ALLOWED_SCHEMES = {"http", "https"}
```

---

# 11. Xây `SchemePolicy`

Đây là cách bắt đầu đưa `yarl` vào kiến trúc crawler.

```python
from yarl import URL


class SchemePolicy:
    ALLOWED_SCHEMES = {"http", "https"}

    @classmethod
    def validate(cls, url: URL) -> None:
        if url.scheme not in cls.ALLOWED_SCHEMES:
            raise ValueError(f"Unsupported URL scheme: {url.scheme}")
```

Test:

```python
from yarl import URL


url = URL("https://example.com/novel/python")

SchemePolicy.validate(url)

print("URL hợp lệ")
```

---

# 12. Force HTTPS + validate

Ta có thể xây:

```python
from yarl import URL


class SchemePolicy:
    ALLOWED_SCHEMES = {"http", "https"}

    @classmethod
    def validate(cls, url: URL) -> None:
        if url.scheme not in cls.ALLOWED_SCHEMES:
            raise ValueError(f"Unsupported scheme: {url.scheme}")

    @classmethod
    def force_https(cls, url: URL) -> URL:
        cls.validate(url)
        return url.with_scheme("https")
```

Sử dụng:

```python
url = URL("http://example.com/novel/python")

secure_url = SchemePolicy.force_https(url)

print(secure_url)
```

Kết quả:

```text
https://example.com/novel/python
```

---

# 13. Xử lý URL đã là HTTPS

Không cần viết:

```python
if url.scheme == "http":
    url = url.with_scheme("https")
```

Ta hoàn toàn có thể:

```python
url = URL("https://example.com/novel/python")

url = url.with_scheme("https")

print(url)
```

Kết quả:

```text
https://example.com/novel/python
```

Tuy nhiên trong application code, có thể viết rõ ý định hơn:

```python
def force_https(url: URL) -> URL:
    if url.scheme == "https":
        return url

    return url.with_scheme("https")
```

---

# 14. Dùng trong Novel Crawler

Giả sử parser lấy được:

```python
href = "http://truyen.example/novel/python"
```

Parser:

```python
from yarl import URL


novel_url = URL(href)

print(novel_url)
```

Kết quả:

```text
http://truyen.example/novel/python
```

Application có policy:

```python
secure_url = novel_url.with_scheme("https")
```

Kết quả:

```text
https://truyen.example/novel/python
```

Luồng:

```text
HTML
 │
 ▼
Parser
 │
 │ href
 ▼
URL(...)
 │
 ▼
URL Policy
 │
 │ with_scheme()
 ▼
Canonical / Secure URL
 │
 ▼
Fetcher
 │
 ▼
httpx
```

Điều này giúp **Parser không phải chứa business rule về HTTPS**.

---

# 15. Một ví dụ thực tế hơn

```python
from yarl import URL


def normalize_scheme(url: URL) -> URL:
    """
    Đưa HTTP URL về HTTPS.

    Chỉ chấp nhận HTTP/HTTPS.
    """

    if url.scheme not in {"http", "https"}:
        raise ValueError(f"Unsupported scheme: {url.scheme}")

    return url.with_scheme("https")


urls = [
    URL("http://example.com/novel/a"),
    URL("https://example.com/novel/b"),
]


for url in urls:
    normalized = normalize_scheme(url)

    print("Original :", url)
    print("Normalized:", normalized)
    print()
```

Kết quả:

```text
Original : http://example.com/novel/a
Normalized: https://example.com/novel/a

Original : https://example.com/novel/b
Normalized: https://example.com/novel/b
```

---

# 16. `origin()` cũng thay đổi theo scheme

Ví dụ:

```python
from yarl import URL


url = URL("http://example.com:8080/novel/python")

https_url = url.with_scheme("https")


print(url.origin())
print(https_url.origin())
```

Ta có:

```text
http://example.com:8080
https://example.com:8080
```

Điều này sẽ rất hữu ích khi chúng ta học:

**Buổi 20 — `origin()`**

---

# 17. Một pattern rất hay trong crawler

Thay vì truyền string khắp hệ thống:

```python
def fetch(url: str): ...
```

ta có thể làm:

```python
from yarl import URL


def fetch(url: URL): ...
```

Sau đó manipulation:

```python
url = URL("http://example.com/novel/python")

url = url.with_scheme("https")

print(url)
```

Điều này làm URL trở thành một object có cấu trúc rõ ràng.

---

# 18. Mini Project

Tạo file:

```text
lesson_11.py
```

Code hoàn chỉnh:

```python
from yarl import URL


class URLPolicy:
    ALLOWED_SCHEMES = {"http", "https"}

    @classmethod
    def validate(cls, url: URL) -> None:
        if url.scheme not in cls.ALLOWED_SCHEMES:
            raise ValueError(f"Unsupported scheme: {url.scheme}")

    @classmethod
    def force_https(cls, url: URL) -> URL:
        cls.validate(url)

        if url.scheme == "https":
            return url

        return url.with_scheme("https")


def main() -> None:

    urls = [
        URL("http://example.com/novel/python?page=1"),
        URL("https://example.com/novel/asyncio?page=2"),
    ]

    for url in urls:
        print("Original:")
        print(url)

        secure_url = URLPolicy.force_https(url)

        print("HTTPS:")
        print(secure_url)

        print("Original vẫn giữ nguyên:")
        print(url)

        print("-" * 50)


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python lesson_11.py
```

Bạn sẽ thấy:

```text
Original:
http://example.com/novel/python?page=1

HTTPS:
https://example.com/novel/python?page=1

Original vẫn giữ nguyên:
http://example.com/novel/python?page=1
--------------------------------------------------
Original:
https://example.com/novel/asyncio?page=2

HTTPS:
https://example.com/novel/asyncio?page=2

Original vẫn giữ nguyên:
https://example.com/novel/asyncio?page=2
--------------------------------------------------
```

---

# 19. Những gì cần nhớ

### `scheme`

```python
url.scheme
```

Lấy scheme.

### `with_scheme()`

```python
new_url = url.with_scheme("https")
```

Thay scheme.

### URL gốc không đổi

```python
url = URL("http://example.com")

new_url = url.with_scheme("https")
```

```text
url     → http://example.com
new_url → https://example.com
```

### Không nên

```python
str(url).replace("http://", "https://")
```

### Nên

```python
url.with_scheme("https")
```

### Quan trọng nhất

```text
with_scheme()
    ↓
không gửi request
    ↓
chỉ thay đổi cấu trúc URL
```

---

# Bài tập Buổi 11

### Bài 1

Cho:

```python
url = URL("http://example.com/novel/python?page=2")
```

Hãy chuyển thành:

```text
https://example.com/novel/python?page=2
```

---

### Bài 2

Viết:

```python
def force_https(url: URL) -> URL: ...
```

Yêu cầu:

* `http` → `https`
* `https` → giữ nguyên
* scheme khác → `ValueError`

---

### Bài 3

Cho:

```text
http://example.com:8080/novel/python?page=2#chapter-10
```

Dùng `with_scheme()` chuyển thành HTTPS và kiểm tra rằng:

```python
host
port
path
query
fragment
```

không thay đổi.

---

### Bài 4 — gắn vào Novel Crawler

Viết:

```python
class NovelURLPolicy: ...
```

có:

```python
validate()
force_https()
```

Sau đó:

```python
url = URL("http://truyen.example/novel/python")

url = NovelURLPolicy.force_https(url)

print(url)
```

Mục tiêu là bắt đầu hình thành:

```text
Parser
   ↓
URL
   ↓
NovelURLPolicy
   ↓
Fetcher
```

**Buổi 12 tiếp theo: `with_host()`** — thay đổi domain/host của URL, rất hữu ích khi crawler phải chuyển giữa domain chính, CDN, mirror hoặc test server.
