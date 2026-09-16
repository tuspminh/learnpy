# Buổi 30 — Unicode trong URL với `yarl`

Đây là bài cuối của **Phần III — Query string chuyên sâu**.

Với Novel Crawler của bạn, Unicode đặc biệt quan trọng vì URL có thể chứa:

```text
truyện
tiên hiệp
kiếm hiệp
đấu phá thương khung
Nhất Niệm Vĩnh Hằng
```

Mục tiêu hôm nay là hiểu rõ:

```text
Unicode
   ↓
yarl.URL
   ↓
URL representation
   ↓
HTTP request
```

và tránh các lỗi như **tự encode**, **double encoding**, hoặc xử lý Unicode bằng string manipulation.

---

# 1. Unicode là gì?

Python 3 làm việc rất tốt với Unicode.

Ví dụ:

```python
text = "truyện kiếm hiệp"

print(text)
print(type(text))
```

Kết quả:

```text
truyện kiếm hiệp
<class 'str'>
```

Trong Python:

```python
"truyện"
```

là một chuỗi Unicode bình thường.

Bạn **không cần biến nó thành `%C3%...` bằng tay** khi xây URL.

---

# 2. Unicode trong query

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/search").with_query({
    "keyword": "truyện kiếm hiệp"
})

print(url)
```

`yarl` sẽ tạo URL representation phù hợp.

Sau đó:

```python
print(url.query["keyword"])
```

ta vẫn nhận được:

```text
truyện kiếm hiệp
```

Tư duy:

```text
Python
"truyện kiếm hiệp"
       │
       ▼
     yarl
       │
       ▼
URL representation
       │
       ▼
      HTTP
```

Bạn chỉ cần đưa **Unicode raw value** vào `yarl`.

---

# 3. Unicode trong path

Không chỉ query mới có Unicode.

Ví dụ website có URL:

```text
https://example.com/truyện/tiên-hiệp
```

Ta có thể:

```python
from yarl import URL

url = URL("https://example.com") / "truyện" / "tiên-hiệp"

print(url)
```

Sau đó:

```python
print(url.path)
```

`path` cho phép application làm việc với nội dung path theo dạng dễ hiểu.

Đây là một điểm rất hữu ích cho parser:

```text
HTML
 │
 │ href="/truyện/tiên-hiệp"
 ▼
yarl.URL
 │
 ▼
URL object
```

---

# 4. `str(url)` có thể khác `url.path`

Đây là điều bạn nên nhớ.

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/truyện/tiên-hiệp")

print("str(url):")
print(str(url))

print()

print("path:")
print(url.path)

print()

print("raw_path:")
print(url.raw_path)
```

Conceptually:

```text
str(url)
    ↓
URL representation phù hợp cho URL

url.path
    ↓
path ở dạng đã parse, dễ làm việc

url.raw_path
    ↓
raw/encoded representation của path
```

Đừng dùng `raw_path` làm dữ liệu domain chỉ vì nó có vẻ "đúng URL hơn".

---

# 5. Query Unicode

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/search").with_query({
    "keyword": "tiên hiệp",
    "author": "Nguyễn Nhật Ánh",
})

print(url)
```

Sau đó:

```python
print(url.query["keyword"])
print(url.query["author"])
```

Bạn làm việc với:

```text
tiên hiệp
Nguyễn Nhật Ánh
```

chứ không cần tự giải mã percent-encoding.

---

# 6. Unicode không chỉ là tiếng Việt

Ví dụ:

```python
queries = [
    "truyện",
    "日本語",
    "中文",
    "한국어",
    "Русский",
    "العربية",
]
```

`yarl` có thể xử lý URL chứa các giá trị Unicode.

Ví dụ:

```python
from yarl import URL

for text in [
    "truyện",
    "日本語",
    "中文",
    "한국어",
]:
    url = URL("https://example.com/search").with_query({
        "q": text
    })

    print(url)
    print(url.query["q"])
    print("---")
```

Điều quan trọng không phải là bạn nhớ từng mã `%XX`.

Điều quan trọng là hiểu:

> **Đưa Unicode vào `URL` ở dạng Python `str`, để `yarl` xử lý URL representation.**

---

# 7. Đừng tự percent-encode Unicode

Sai lầm:

```python
from urllib.parse import quote

keyword = quote("truyện kiếm hiệp")

url = URL("https://example.com/search").with_query({
    "q": keyword
})
```

Bạn đã biến:

```text
truyện kiếm hiệp
```

thành encoded string trước khi giao cho `yarl`.

Đây là nơi rất dễ xảy ra **double encoding**.

Nguyên tắc:

```text
❌ Python string
   ↓
   quote()
   ↓
   yarl

✅ Python string
   ↓
   yarl
```

---

# 8. Ví dụ double encoding

Giả sử:

```python
encoded = "truy%E1%BB%87n"
```

Nếu bạn đưa chuỗi này vào một API cần raw value:

```python
url = URL("https://example.com").with_query({
    "q": encoded
})
```

thì `%` trong dữ liệu có thể tiếp tục được xử lý như một ký tự cần encode.

Kết quả có thể xuất hiện dạng:

```text
%25
```

Ví dụ concept:

```text
%20
 ↓ encode tiếp
%2520
```

Đây là lý do không nên có pipeline:

```text
quote()
 ↓
yarl
 ↓
quote() lần nữa
```

---

# 9. Một nguyên tắc cực kỳ quan trọng cho crawler

Trong crawler:

```text
HTML
 ↓
href
 ↓
URL
 ↓
Fetcher
```

hãy cố gắng giữ URL ở dạng:

```python
yarl.URL
```

thay vì liên tục chuyển:

```text
URL
↓
str
↓
replace
↓
quote
↓
unquote
↓
str
```

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com") / "truyện" / "tiên-hiệp"

print(url)
```

Sau đó Fetcher nhận:

```python
def fetch(url: URL):
    ...
```

hoặc nếu HTTP client yêu cầu string:

```python
client.get(str(url))
```

---

# 10. Unicode trong Novel URL

Giả sử parser lấy được:

```html
<a href="/truyện/nhất-niệm-vĩnh-hằng">
    Nhất Niệm Vĩnh Hằng
</a>
```

Parser có thể:

```python
from yarl import URL

base_url = URL("https://truyen.example")

href = "/truyện/nhất-niệm-vĩnh-hằng"

url = base_url.join(URL(href))

print(url)
```

Ta giữ:

```python
url
```

là `URL`.

Sau đó:

```python
print(url.path)
```

có thể sử dụng path trong logic application.

---

# 11. Unicode và `URL.join()`

Đây là pattern sẽ cực kỳ quan trọng ở **Phần IV**.

Ví dụ HTML:

```html
<a href="/truyện/tiên-hiệp">Tiên Hiệp</a>
```

Ta có:

```python
from yarl import URL

base_url = URL("https://truyen.example/list")

href = "/truyện/tiên-hiệp"

chapter_url = base_url.join(URL(href))

print(chapter_url)
```

Tư duy:

```text
href từ HTML
      │
      ▼
    URL()
      │
      ▼
 base_url.join()
      │
      ▼
 absolute URL
```

Không cần tự:

```python
base_url + href
```

---

# 12. Unicode và query duplicate

Kết hợp với bài 28:

```python
from yarl import URL

url = (
    URL("https://example.com/search")
    .with_query([
        ("genre", "tiên hiệp"),
        ("genre", "kiếm hiệp"),
        ("genre", "huyền huyễn"),
    ])
)

print(url)
```

Sau đó:

```python
genres = url.query.getall("genre", [])

print(genres)
```

Kết quả logic:

```python
[
    "tiên hiệp",
    "kiếm hiệp",
    "huyền huyễn",
]
```

Đây là sự kết hợp của:

```text
Buổi 28
getall()
      +
Buổi 29
encoding
      +
Buổi 30
Unicode
```

---

# 13. Unicode normalization — vấn đề nâng cao

Đây là phần rất quan trọng khi làm crawler.

Hai chuỗi có thể **trông giống nhau** nhưng có representation Unicode khác nhau.

Ví dụ Unicode có thể biểu diễn một ký tự bằng:

```text
ký tự dựng sẵn
```

hoặc:

```text
ký tự cơ bản + combining mark
```

Ví dụ chữ:

```text
é
```

có thể được biểu diễn theo hai cách Unicode khác nhau.

Python có:

```python
import unicodedata
```

và:

```python
unicodedata.normalize()
```

Ví dụ:

```python
import unicodedata

a = "é"
b = "e\u0301"

print(a == b)
```

Có thể nhận:

```text
False
```

dù khi hiển thị chúng trông giống nhau.

---

# 14. Unicode normalization

Ta có thể normalize:

```python
import unicodedata

a = "é"
b = "e\u0301"

a = unicodedata.normalize("NFC", a)
b = unicodedata.normalize("NFC", b)

print(a == b)
```

Kết quả:

```text
True
```

Các dạng phổ biến:

```text
NFC
NFD
NFKC
NFKD
```

Đối với crawler, **NFC** thường là một lựa chọn hợp lý khi bạn muốn chuẩn hóa Unicode text.

Nhưng:

> Không nên mặc định normalize mọi URL một cách mù quáng.

Đặc biệt trong URL canonicalization, cần phân biệt:

```text
text normalization
```

và:

```text
URL normalization
```

Đây là hai vấn đề khác nhau.

---

# 15. Tại sao Unicode normalization quan trọng với crawler?

Giả sử crawler có:

```python
seen_urls = set()
```

Bạn nhận được hai URL:

```text
URL A
https://example.com/truyện/é

URL B
https://example.com/truyện/é
```

Nếu representation Unicode khác nhau, việc so sánh/deduplicate có thể không đơn giản.

Nhưng **không nên kết luận rằng hai URL chắc chắn tương đương trên server** chỉ vì chúng hiển thị giống nhau.

Đây là lý do canonicalization sẽ được học sau.

---

# 16. Domain model không nên chứa encoded URL

Ví dụ `Novel`:

```python
from dataclasses import dataclass
from yarl import URL


@dataclass
class Novel:
    title: str
    url: URL
```

Ta nên:

```python
novel = Novel(
    title="Nhất Niệm Vĩnh Hằng",
    url=URL("https://example.com/truyện/nhất-niệm-vĩnh-hằng"),
)
```

chứ không chủ động lưu:

```text
https://example.com/truy%E1%BB%87n/nh%E1%BA%A5t-ni%E1%BB%87m...
```

ở mọi tầng application chỉ vì URL representation có encoded form.

---

# 17. `str(URL)` ở boundary

Một pattern kiến trúc tốt:

```text
Domain
   │
   │ URL object
   ▼
Application
   │
   │ URL object
   ▼
Fetcher
   │
   │ str(url) nếu HTTP client cần
   ▼
httpx
```

Ví dụ:

```python
from yarl import URL
import httpx


def fetch(url: URL) -> str:
    with httpx.Client() as client:
        response = client.get(str(url))
        response.raise_for_status()
        return response.text
```

Điểm quan trọng:

**Chỉ chuyển sang `str` ở boundary cần string.**

Không nên:

```python
url = str(url)

# sau đó
url = URL(url)

# rồi lại
url = str(url)
```

liên tục trong toàn hệ thống.

---

# 18. Một ví dụ hoàn chỉnh cho Novel Crawler

```python
from dataclasses import dataclass
from yarl import URL


@dataclass
class Novel:
    title: str
    url: URL


def build_novel_url(slug: str) -> URL:
    base_url = URL("https://truyen.example")

    return base_url / "truyện" / slug


def main() -> None:
    title = "Nhất Niệm Vĩnh Hằng"
    slug = "nhất-niệm-vĩnh-hằng"

    url = build_novel_url(slug)

    novel = Novel(
        title=title,
        url=url,
    )

    print("Title:")
    print(novel.title)

    print("\nURL:")
    print(novel.url)

    print("\nPath:")
    print(novel.url.path)

    print("\nRaw path:")
    print(novel.url.raw_path)

    print("\nHuman representation:")
    print(novel.url.human_repr())


if __name__ == "__main__":
    main()
```

Kiến trúc:

```text
Novel
 ├── title: str
 └── url: URL
          │
          ├── path
          ├── raw_path
          └── human_repr()
```

Đây là kiểu thiết kế phù hợp với hướng **DDD + Clean Architecture** mà bạn đang xây dựng.

---

# 19. Một điều rất quan trọng: Unicode ≠ URL canonicalization

Đừng gộp hai vấn đề này.

### Unicode handling

Ví dụ:

```text
é
e + combining accent
```

là vấn đề về **Unicode representation**.

### URL canonicalization

Ví dụ:

```text
HTTP://example.com
http://example.com/
http://example.com:80/
```

có thể cần xem xét về **URL equivalence**.

Đây là vấn đề khác.

Chúng ta sẽ xử lý canonical URL ở:

```text
Buổi 36 — URL normalization
Buổi 37 — URL comparison
Buổi 38 — URL deduplication
Buổi 39 — Canonical URL
```

---

# 20. Những gì không nên làm

### ❌ Encode thủ công

```python
quote("truyện kiếm hiệp")
```

rồi đưa vào `with_query()`.

### ❌ `replace()` URL

```python
url.replace(" ", "%20")
```

### ❌ Decode thủ công mọi URL

```python
unquote(str(url))
```

rồi dùng kết quả đó làm URL mới.

### ❌ Xử lý URL bằng regex

```python
re.sub(...)
```

cho những việc mà `yarl` đã hỗ trợ.

### ❌ Normalize URL mù quáng

Không phải mọi khác biệt Unicode/URL representation đều có thể tự động coi là tương đương.

---

# 21. Quy tắc vàng cho bạn

Trong Novel Crawler, hãy cố giữ pipeline:

```text
                    RAW DATA
                       │
                       ▼
                 Parser / App
                       │
                       │ Unicode str
                       ▼
                    yarl.URL
                       │
                       │ URL object
                       ▼
                     Fetcher
                       │
                       │ str(url)
                       ▼
                     httpx
```

Và khi đọc:

```text
HTTP/HTML
   │
   ▼
href
   │
   ▼
URL
   │
   ├── path
   ├── query
   └── fragment
```

**Không đi vòng qua hàng loạt `quote()`, `unquote()`, `replace()` nếu không thực sự cần.**

---

# 22. Tổng kết Phần III

Chúng ta vừa hoàn thành:

```text
21  URL.with_query()
22  Dictionary → Query
23  List/Tuple → Query
24  Duplicate Query Parameters
25  URL.query
26  query_string
27  query.get()
28  query.getall()
29  Encoding / Decoding
30  Unicode trong URL
```

Bạn hiện đã có nền tảng khá đầy đủ để xử lý query:

```python
url.query.get("keyword")
```

```python
url.query.getall("genre", [])
```

```python
url.query.items()
```

và xây URL:

```python
URL(...).with_query(...)
```

mà không cần tự xử lý encoding.

---

# Bài tập Buổi 30

### Bài 1

Tạo URL:

```python
URL("https://example.com/search")
```

với:

```text
keyword = "truyện kiếm hiệp"
author = "Nguyễn Nhật Ánh"
```

Không dùng `quote()`.

---

### Bài 2

Tạo URL:

```text
/search?genre=tiên+hiệp&genre=kiếm+hiệp&genre=huyền+huyễn
```

bằng `yarl`.

Sau đó:

```python
url.query.getall("genre", [])
```

phải trả về danh sách Unicode tương ứng.

---

### Bài 3

Tạo:

```python
base_url = URL("https://truyen.example")

slug = "nhất-niệm-vĩnh-hằng"

url = ...
```

để tạo URL novel.

Không dùng nối chuỗi:

```python
base_url + ...
```

---

### Bài 4 — Bài quan trọng

Viết:

```python
@dataclass
class Novel:
    title: str
    url: URL
```

và tạo:

```python
Novel(
    title="Nhất Niệm Vĩnh Hằng",
    url=...
)
```

sao cho URL có Unicode trong path.

Sau đó in:

```python
novel.url
novel.url.path
novel.url.raw_path
novel.url.human_repr()
```

và quan sát sự khác nhau.

---

## Sau Buổi 30

**Phần III đã xong.**

Chúng ta chuyển sang phần rất thực chiến:

# Phần IV — `yarl` trong Web Crawler

```text
31. Relative URL → Absolute URL
32. <a href> → URL
33. Pagination
34. Chapter URL
35. Image URL
36. URL normalization
37. URL comparison
38. URL deduplication
39. Canonical URL
40. Xây URLBuilder cho Novel Crawler
```

Đặc biệt **Buổi 31 — Relative URL → Absolute URL** sẽ bắt đầu nối trực tiếp `yarl` với **Parser + selectolax + Fetcher**, đúng với kiến trúc Novel Crawler mà chúng ta đang xây dựng.
