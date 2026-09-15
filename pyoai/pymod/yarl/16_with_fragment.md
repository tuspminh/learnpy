# Buổi 16 — `with_fragment()` trong `yarl`

Hôm nay chúng ta học:

> **`URL.with_fragment()` — thay đổi phần Fragment (`#...`) của URL một cách an toàn và immutable.**

Đây là phần khá quan trọng khi xây **URL normalization / deduplication / reader URL** cho Novel Crawler.

---

# 1. Fragment là gì?

Xét URL:

```text
https://example.com/novel/python?page=2#chapter-10
```

Ta có:

```text
https://example.com/novel/python?page=2#chapter-10
│       │             │       │
│       │             │       └── fragment
│       │             └────────── query
│       └──────────────────────── host
└──────────────────────────────── scheme
```

Trong Python:

```python
from yarl import URL

url = URL("https://example.com/novel/python?page=2#chapter-10")

print(url.scheme)
print(url.host)
print(url.path)
print(url.query)
print(url.fragment)
```

Kết quả:

```text
https
example.com
/novel/python
<aiohttp.helpers._Query object ...>
chapter-10
```

Phần chúng ta quan tâm hôm nay:

```python
url.fragment
```

---

# 2. `with_fragment()`

Cú pháp:

```python
new_url = url.with_fragment("new-fragment")
```

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/novel/python?page=2#chapter-10")

new_url = url.with_fragment("chapter-20")

print(new_url)
```

Kết quả:

```text
https://example.com/novel/python?page=2#chapter-20
```

Chỉ Fragment thay đổi:

```text
cũ:
https://example.com/novel/python?page=2#chapter-10

mới:
https://example.com/novel/python?page=2#chapter-20
                                      ↑
                                  thay đổi
```

---

# 3. `URL` là immutable

Đây là điểm rất quan trọng.

```python
from yarl import URL

url = URL("https://example.com/novel/python?page=2#chapter-10")

new_url = url.with_fragment("chapter-20")

print("url    :", url)
print("new_url:", new_url)
```

Kết quả:

```text
url    : https://example.com/novel/python?page=2#chapter-10
new_url: https://example.com/novel/python?page=2#chapter-20
```

`url` không bị thay đổi.

Có thể kiểm tra:

```python
print(url.fragment)
print(new_url.fragment)
```

Kết quả:

```text
chapter-10
chapter-20
```

Mô hình tư duy:

```text
url
 │
 │ with_fragment()
 ▼
new_url
```

Không phải:

```text
url bị sửa trực tiếp
```

---

# 4. `with_fragment()` chỉ thay Fragment

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com:8080/novel/python?page=2#chapter-10")

new_url = url.with_fragment("chapter-20")

print(new_url.scheme)
print(new_url.host)
print(new_url.port)
print(new_url.path)
print(new_url.query)
print(new_url.fragment)
```

Các phần khác vẫn giữ nguyên:

```text
scheme   = https
host     = example.com
port     = 8080
path     = /novel/python
query    = page=2
fragment = chapter-20
```

Đây là ưu điểm lớn của API:

```python
with_fragment()
```

thay vì tự xử lý chuỗi.

---

# 5. Xóa Fragment

Muốn bỏ Fragment:

```python
url.with_fragment(None)
```

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/novel/python?page=2#chapter-10")

clean_url = url.with_fragment(None)

print(clean_url)
```

Kết quả:

```text
https://example.com/novel/python?page=2
```

Kiểm tra:

```python
print(clean_url.fragment)
```

Kết quả:

```text
None
```

Đây là pattern cực kỳ hữu ích:

```python
network_url = url.with_fragment(None)
```

---

# 6. Fragment khác Query như thế nào?

Đây là phần **rất quan trọng đối với crawler**.

Ví dụ:

```text
https://example.com/chapter/10?page=2#content
```

Ta có:

```text
Query:
?page=2

Fragment:
#content
```

### Query

```text
?page=2
```

thường được gửi tới server.

Server có thể sử dụng:

```text
page=2
```

để quyết định nội dung response.

---

### Fragment

```text
#content
```

thường được trình duyệt sử dụng ở phía client để xác định vị trí trong tài liệu.

Ví dụ:

```text
https://example.com/article#comments
```

Trình duyệt có thể mở trang và nhảy xuống:

```text
Comments
```

---

# 7. Fragment thường không được gửi trong HTTP request

Đây là lý do `fragment` đặc biệt quan trọng trong crawler.

Giả sử:

```text
URL A
https://example.com/chapter/10#part-1
```

và:

```text
URL B
https://example.com/chapter/10#part-2
```

Về mặt server resource, chúng thường trỏ tới **cùng một tài nguyên HTTP**:

```text
https://example.com/chapter/10
```

Fragment:

```text
#part-1
#part-2
```

là thông tin phía client.

Vì vậy trong crawler, nếu mục tiêu là **fetch dữ liệu từ server**, thường nên loại bỏ Fragment:

```python
from yarl import URL

url = URL("https://example.com/chapter/10#part-1")

request_url = url.with_fragment(None)

print(request_url)
```

Kết quả:

```text
https://example.com/chapter/10
```

---

# 8. Đây là use case rất thực tế của Novel Crawler

Giả sử parser lấy được:

```html
<a href="/chuong-10#content">Chương 10</a>
<a href="/chuong-10#comments">Bình luận</a>
```

Ta nhận được:

```python
url1 = URL("https://example.com/chuong-10#content")
url2 = URL("https://example.com/chuong-10#comments")
```

Nếu crawler chỉ quan tâm nội dung chương:

```python
url1 = url1.with_fragment(None)
url2 = url2.with_fragment(None)

print(url1)
print(url2)
```

Kết quả:

```text
https://example.com/chuong-10
https://example.com/chuong-10
```

Bây giờ crawler có thể deduplicate:

```python
urls = {
    url1,
    url2,
}

print(len(urls))
```

Kết quả:

```text
1
```

Điều này giúp tránh fetch cùng một chapter hai lần.

---

# 9. Xây `strip_fragment()`

Ta có thể đóng gói logic:

```python
from yarl import URL


def strip_fragment(url: URL) -> URL:
    return url.with_fragment(None)
```

Test:

```python
url = URL("https://example.com/chapter/10?page=2#content")

clean_url = strip_fragment(url)

print(clean_url)
```

Kết quả:

```text
https://example.com/chapter/10?page=2
```

---

# 10. Đặt vào architecture của Crawler

Trong crawler của bạn, có thể có:

```text
Parser
   ↓
URL
   ↓
URL Normalizer
   ↓
Fetcher
```

Ví dụ:

```python
from yarl import URL


class URLNormalizer:
    @staticmethod
    def normalize(url: URL) -> URL:
        return url.with_fragment(None)
```

Sử dụng:

```python
url = URL("https://example.com/chapter/10#content")

normalized = URLNormalizer.normalize(url)

print(normalized)
```

Kết quả:

```text
https://example.com/chapter/10
```

---

# 11. Tại sao không dùng `str.replace()`?

Cách không nên làm:

```python
url_string = str(url)

url_string = url_string.replace("#content", "")
```

Có rất nhiều vấn đề.

Ví dụ:

```text
https://example.com/a#content
```

có thể dễ xử lý.

Nhưng khi URL phức tạp hơn:

```text
https://example.com/a?x=1&text=%23content#chapter
```

việc thao tác chuỗi rất dễ làm sai logic URL.

Thay vào đó:

```python
url.with_fragment(None)
```

Ý nghĩa rõ ràng:

> Tôi muốn thay đổi Fragment của URL.

---

# 12. Thay Fragment động

Ví dụ hệ thống reader:

```python
from yarl import URL

url = URL("https://example.com/novel/python")

for chapter in range(1, 6):
    chapter_url = url.with_fragment(f"chapter-{chapter}")

    print(chapter_url)
```

Kết quả:

```text
https://example.com/novel/python#chapter-1
https://example.com/novel/python#chapter-2
https://example.com/novel/python#chapter-3
https://example.com/novel/python#chapter-4
https://example.com/novel/python#chapter-5
```

---

# 13. Fragment cho Reader

Đây là nơi Fragment có ý nghĩa trong ứng dụng đọc truyện.

Ví dụ:

```text
https://reader.example.com/book/python#chapter-10
```

Có thể hiểu:

```text
URL:
https://reader.example.com/book/python

Fragment:
chapter-10
```

Ứng dụng reader có thể:

```python
from yarl import URL

url = URL("https://reader.example.com/book/python#chapter-10")

chapter_id = url.fragment

print(chapter_id)
```

Kết quả:

```text
chapter-10
```

Sau đó UI có thể:

```text
Load Book
    ↓
Read fragment
    ↓
chapter-10
    ↓
Scroll / open Chapter 10
```

Ở đây Fragment **không phải dữ liệu cần gửi tới server** mà là state của UI.

---

# 14. Query + Fragment

Một URL có thể đồng thời có Query và Fragment:

```text
https://example.com/search?q=python&page=2#results
```

Ta có:

```python
from yarl import URL

url = URL("https://example.com/search?q=python&page=2#results")

print(url.query)
print(url.fragment)
```

Query:

```text
q=python
page=2
```

Fragment:

```text
results
```

---

# 15. Xóa Fragment nhưng giữ Query

Đây là một pattern rất thường gặp:

```python
clean = url.with_fragment(None)
```

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/search?q=python&page=2#results")

clean = url.with_fragment(None)

print(clean)
```

Kết quả:

```text
https://example.com/search?q=python&page=2
```

Query vẫn còn:

```text
?q=python&page=2
```

Chỉ:

```text
#results
```

bị loại bỏ.

---

# 16. Chain với các `with_*()` đã học

Đây là lúc các bài trước bắt đầu kết nối với nhau.

Ví dụ:

```python
from yarl import URL

url = URL("http://old.example.com:8000/old/path?page=2#chapter-10")

new_url = (
    url.with_scheme("https")
    .with_host("new.example.com")
    .with_port(443)
    .with_path("/novel/python")
    .with_fragment(None)
)

print(new_url)
```

Kết quả:

```text
https://new.example.com/novel/python?page=2
```

Chúng ta đã thực hiện:

```text
with_scheme()
      ↓
with_host()
      ↓
with_port()
      ↓
with_path()
      ↓
with_fragment()
```

Mỗi operation tạo một URL mới.

---

# 17. Complete example

Đây là ví dụ hoàn chỉnh để bạn có thể chạy ngay:

```python
from yarl import URL


def main():
    url = URL("https://example.com:443/novel/python?page=2&sort=desc#chapter-10")

    print("Original URL")
    print("-" * 50)
    print(url)

    print("\nComponents")
    print("-" * 50)
    print("scheme   :", url.scheme)
    print("host     :", url.host)
    print("port     :", url.port)
    print("path     :", url.path)
    print("query    :", url.query_string)
    print("fragment :", url.fragment)

    # Thay fragment
    chapter_20 = url.with_fragment("chapter-20")

    print("\nChange fragment")
    print("-" * 50)
    print("original :", url)
    print("new      :", chapter_20)

    # Xóa fragment
    clean_url = url.with_fragment(None)

    print("\nRemove fragment")
    print("-" * 50)
    print("original :", url)
    print("clean    :", clean_url)

    # Kiểm tra immutable
    print("\nImmutable")
    print("-" * 50)
    print("original fragment :", url.fragment)
    print("new fragment      :", chapter_20.fragment)
    print("clean fragment    :", clean_url.fragment)


if __name__ == "__main__":
    main()
```

---

# 18. Một bài toán rất thực tế: URL trước khi Fetch

Ta tạo:

```python
from yarl import URL


def prepare_request_url(url: URL) -> URL:
    """
    Chuẩn hóa URL trước khi gửi HTTP request.
    Fragment không cần thiết cho network request.
    """
    return url.with_fragment(None)


def main():
    source_url = URL("https://example.com/chapter/10?source=truyen#content")

    request_url = prepare_request_url(source_url)

    print("Source URL:")
    print(source_url)

    print("\nRequest URL:")
    print(request_url)


if __name__ == "__main__":
    main()
```

Kết quả:

```text
Source URL:
https://example.com/chapter/10?source=truyen#content

Request URL:
https://example.com/chapter/10?source=truyen
```

Architecture:

```text
Parser
  │
  │ href
  ▼
URL
  │
  │ normalize
  ▼
URLNormalizer
  │
  │ remove fragment
  ▼
Request URL
  │
  ▼
Fetcher
  │
  ▼
HTTP Server
```

Đây là cách `yarl` rất hợp với kiến trúc crawler của bạn.

---

# 19. Khi nào KHÔNG nên xóa Fragment?

Không phải lúc nào cũng nên:

```python
url.with_fragment(None)
```

Nếu ứng dụng của bạn cần Fragment cho **client-side state**, hãy giữ nó.

Ví dụ:

```text
https://reader.example.com/novel/python#chapter-20
```

Fragment có thể có ý nghĩa:

```text
chapter-20
```

đối với Reader UI.

Vì vậy nên phân biệt:

### Network URL

```python
request_url = url.with_fragment(None)
```

### Reader URL

```python
reader_url = url
```

Không nên có quy tắc:

```text
mọi URL đều xóa fragment
```

mà nên có policy rõ ràng:

```text
Network layer → strip fragment
Reader layer  → preserve fragment
```

---

# 20. So sánh `with_query()` và `with_fragment()`

| Method            | Thay đổi | Ví dụ                     |
| ----------------- | -------- | ------------------------- |
| `with_scheme()`   | scheme   | `http → https`            |
| `with_host()`     | host     | `a.com → b.com`           |
| `with_port()`     | port     | `8000 → 9000`             |
| `with_path()`     | path     | `/a → /b`                 |
| `with_query()`    | query    | `?page=1 → ?page=2`       |
| `with_fragment()` | fragment | `#chapter-1 → #chapter-2` |

Điểm quan trọng:

```python
url.with_query(...)
```

thay **toàn bộ query**.

Trong khi:

```python
url.with_fragment(...)
```

thay **fragment**.

---

# 21. Bài tập thực hành

## Bài 1

Tạo:

```text
https://example.com/novel/python?page=2#chapter-10
```

Sau đó đổi thành:

```text
https://example.com/novel/python?page=2#chapter-20
```

bằng `with_fragment()`.

---

## Bài 2

Xóa Fragment:

```text
https://example.com/novel/python?page=2#chapter-20
```

thành:

```text
https://example.com/novel/python?page=2
```

---

## Bài 3

Viết:

```python
def strip_fragment(url: URL) -> URL: ...
```

để chuẩn hóa URL trước khi fetch.

---

## Bài 4 — crawler

Cho:

```python
urls = [
    "https://example.com/chapter/10#content",
    "https://example.com/chapter/10#comments",
    "https://example.com/chapter/11#content",
]
```

Chuyển tất cả thành URL network:

```text
https://example.com/chapter/10
https://example.com/chapter/10
https://example.com/chapter/11
```

sau đó deduplicate bằng `set`.

---

# 22. Kiến thức cần nhớ

Quan trọng nhất của Buổi 16:

```python
url.fragment
```

→ đọc Fragment.

```python
url.with_fragment("chapter-20")
```

→ thay Fragment.

```python
url.with_fragment(None)
```

→ xóa Fragment.

Và pattern đặc biệt quan trọng đối với crawler:

```python
request_url = url.with_fragment(None)
```

vì:

```text
Query
  ↓
thường thuộc request/server

Fragment
  ↓
thường thuộc client/browser
```

Do đó:

```text
Parser
   ↓
https://example.com/chapter/10#content
   ↓
normalize
   ↓
https://example.com/chapter/10
   ↓
Fetcher
```

**Buổi 17 — `with_name()`** sẽ chuyển sang một nhóm thao tác rất hữu ích với crawler: **thay đổi tên file cuối cùng của Path**, ví dụ:

```text
/chapter-10.html
       ↓
/chapter-20.html
```

và chúng ta sẽ kết nối nó với `path`, `name`, `suffix`, `stem` đã học.
