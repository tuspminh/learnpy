# Buổi 29 — Encoding / Decoding trong `yarl`

Đây là bài rất quan trọng trước khi chúng ta đi sang **Unicode trong URL** và sau đó áp dụng `yarl` vào **Novel Crawler**.

Mục tiêu hôm nay:

```text
URL
 │
 ├── encoding
 │      ↓
 │   URL an toàn để truyền qua HTTP
 │
 └── decoding
        ↓
     dữ liệu dễ đọc trong Python
```

---

# 1. Encoding URL là gì?

URL không thể tùy ý chứa mọi ký tự.

Ví dụ ta muốn tìm:

```text
python sqlite
```

Nếu viết trực tiếp:

```text
https://example.com/search?q=python sqlite
```

thì khoảng trắng cần được biểu diễn dưới dạng encoded URL.

Ví dụ:

```text
https://example.com/search?q=python+sqlite
```

hoặc trong nhiều ngữ cảnh URL encoding:

```text
https://example.com/search?q=python%20sqlite
```

`yarl` giúp chúng ta xử lý việc này thay vì tự:

```python
url.replace(" ", "%20")
```

**Không nên tự encode URL bằng `replace()`.**

---

# 2. Ví dụ cơ bản với `with_query()`

```python
from yarl import URL

url = URL("https://example.com/search").with_query({
    "q": "python sqlite"
})

print(url)
```

Bạn sẽ thấy URL được encode phù hợp.

Ví dụ dạng:

```text
https://example.com/search?q=python+sqlite
```

Nhưng khi lấy giá trị:

```python
print(url.query["q"])
```

ta nhận lại:

```text
python sqlite
```

Đây chính là ý tưởng:

```text
Python value
    │
    ▼
yarl
    │
    ▼
Encoded URL
    │
    ▼
HTTP
```

và ngược lại:

```text
Encoded URL
    │
    ▼
yarl
    │
    ▼
Python value
```

---

# 3. Encoding và decoding diễn ra ở đâu?

Ví dụ:

```python
from yarl import URL

url = URL(
    "https://example.com/search?q=python%20sqlite"
)

print(url)
print(url.query["q"])
```

Kết quả về mặt giá trị:

```text
https://example.com/search?q=python%20sqlite
python sqlite
```

Ta có:

```text
URL representation:
python%20sqlite

Decoded query value:
python sqlite
```

Không nên nhầm:

```python
str(url)
```

với:

```python
url.query["q"]
```

Một cái là **URL representation**, một cái là **giá trị đã được parse**.

---

# 4. `query_string`

Ta có:

```python
from yarl import URL

url = URL(
    "https://example.com/search?q=python%20sqlite"
)

print(url.query_string)
```

Kết quả:

```text
q=python sqlite
```

Điểm cần chú ý:

`query_string` là representation của query theo API của `yarl`, không nên coi nó là nơi để tự viết bộ encode/decode.

Khi cần dữ liệu có cấu trúc:

```python
url.query
```

Khi cần giá trị query dạng string:

```python
url.query_string
```

Khi cần toàn URL:

```python
str(url)
```

---

# 5. Ký tự đặc biệt

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/search").with_query({
    "q": "C++ & Python"
})

print(url)
```

`yarl` sẽ xử lý các ký tự đặc biệt cần thiết trong URL.

Bạn không nên làm:

```python
query = "C++ & Python"
query = query.replace("+", "%2B")
query = query.replace("&", "%26")
```

Đây là việc thư viện URL nên đảm nhận.

---

# 6. Tại sao tự `replace()` rất nguy hiểm?

Ví dụ:

```python
keyword = "C++"
```

Bạn tự:

```python
keyword.replace("+", "%2B")
```

có vẻ đơn giản.

Nhưng khi dữ liệu phức tạp hơn:

```text
C++ & Python / SQLite? beginner
```

bạn sẽ phải xử lý:

```text
+
&
/
?
space
Unicode
%
#
...
```

Chưa kể encoding phụ thuộc vào **vị trí của dữ liệu trong URL**.

Ví dụ:

```text
path
query
fragment
username
password
```

không nên xử lý bằng một chuỗi `replace()` chung.

---

# 7. Query parameter chứa `%`

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/search").with_query({
    "q": "100%"
})

print(url)
```

`%` là một ký tự có ý nghĩa đặc biệt trong percent-encoding, nên việc tự xử lý nó rất dễ sai.

`yarl` đảm nhiệm việc tạo representation phù hợp.

Sau đó:

```python
print(url.query["q"])
```

vẫn lấy được:

```text
100%
```

---

# 8. Query chứa `/` và `?`

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/search").with_query({
    "q": "python/sqlite?beginner"
})

print(url)
print(url.query["q"])
```

Điều quan trọng là `/` và `?` ở **query value** không nên được hiểu nhầm thành cấu trúc của URL.

Ta muốn:

```text
query value
    ↓
python/sqlite?beginner
```

chứ không phải:

```text
path
    ↓
python/sqlite

query
    ↓
beginner
```

Khi xây URL bằng:

```python
with_query()
```

`yarl` biết rằng dữ liệu đó đang nằm trong **query**.

---

# 9. Path cũng có encoding

Encoding không chỉ xảy ra ở query.

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com") / "truyện python"

print(url)
```

URL cần representation phù hợp cho path.

Nhưng:

```python
print(url.path)
```

cho bạn giá trị path ở dạng dễ làm việc hơn trong Python.

Có thể hình dung:

```text
URL representation
        │
        │ encoded representation
        ▼
https://example.com/truy%E1%BB%87n%20python

        ▲
        │
        │ parsed value
        │
Python
        │
        ▼
/truyện python
```

---

# 10. `raw_path` vs `path`

Đây là một API rất đáng nhớ của `yarl`.

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/truyện python")

print("path     =", url.path)
print("raw_path =", url.raw_path)
```

Ý tưởng:

```text
path
    ↓
giá trị path đã được decode / dễ đọc

raw_path
    ↓
representation encoded của path
```

Đối với URL có Unicode hoặc ký tự cần encoding, sự khác nhau này trở nên rõ ràng.

---

# 11. `human_repr()`

`yarl` còn có:

```python
url.human_repr()
```

Mục đích là tạo representation **dễ đọc cho con người**.

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/truyện-python?q=xin chào")

print("str         :", str(url))
print("human_repr  :", url.human_repr())
```

Bạn có thể xem:

```text
str(url)
    ↓
URL representation phù hợp để truyền/biểu diễn

human_repr()
    ↓
representation dễ đọc hơn cho developer
```

---

# 12. `str(url)` và `human_repr()` không nên nhầm với dữ liệu domain

Ví dụ:

```python
url = URL(
    "https://example.com/search?q=xin%20chào"
)
```

Bạn có:

```python
str(url)
```

để lấy URL.

Còn:

```python
url.query["q"]
```

để lấy:

```text
xin chào
```

Domain application của crawler thường quan tâm:

```python
keyword = url.query.get("q")
```

chứ không nên lấy:

```python
url.query_string
```

rồi tự parse.

---

# 13. Unicode

Ví dụ thực tế hơn:

```python
from yarl import URL

url = URL("https://example.com/search").with_query({
    "q": "truyện kiếm hiệp"
})

print("URL:")
print(url)

print("\nQuery:")
print(url.query["q"])

print("\nHuman:")
print(url.human_repr())
```

Bạn sẽ thấy sự khác biệt giữa:

```text
URL representation
```

và:

```text
giá trị Unicode
```

Đây là nền tảng cho **Buổi 30 — Unicode trong URL**.

---

# 14. Một lỗi rất phổ biến: encode hai lần

Đây là lỗi quan trọng trong crawler.

Giả sử bạn có:

```python
keyword = "truyện kiếm hiệp"
```

Bạn tự encode trước:

```python
keyword = "truy%E1%BB%87n%20ki%E1%BA%BFm%20hi%E1%BB%87p"
```

rồi lại:

```python
url = URL("https://example.com/search").with_query({
    "q": keyword
})
```

Bạn đang đưa **encoded data** vào API đang chờ **raw value**.

Có nguy cơ tạo ra:

```text
%25
```

vì `%` có thể bị encode thành `%25`.

Ví dụ conceptually:

```text
%20
 ↓ encode lần nữa
%2520
```

Đây gọi là:

> **double encoding**

---

# 15. Quy tắc cực kỳ quan trọng

Khi sử dụng `yarl`, hãy giữ dữ liệu của application ở dạng bình thường:

```python
keyword = "truyện kiếm hiệp"
```

Sau đó:

```python
url = URL(
    "https://example.com/search"
).with_query({
    "q": keyword
})
```

**Không làm:**

```python
keyword = urllib.parse.quote(keyword)

url = URL(...).with_query({"q": keyword})
```

nếu mục đích chỉ là truyền query value bình thường.

Hãy để `yarl` xử lý URL encoding.

---

# 16. Encoding trong Novel Crawler

Giả sử người dùng nhập:

```text
Tìm truyện: Tiên hiệp Việt Nam
```

Application có:

```python
keyword = "Tiên hiệp Việt Nam"
```

URL Builder:

```python
from yarl import URL


class SearchURLBuilder:

    def __init__(self, base_url: URL):
        self.base_url = base_url

    def build(self, keyword: str, page: int = 1) -> URL:
        return (
            self.base_url
            .with_query({
                "keyword": keyword,
                "page": page,
            })
        )


builder = SearchURLBuilder(
    URL("https://truyen.example/search")
)

url = builder.build(
    keyword="Tiên hiệp Việt Nam",
    page=2,
)

print(url)
```

Application không cần biết:

```text
Unicode encoding
percent encoding
space encoding
special-character escaping
```

Nó chỉ cần:

```python
keyword = "Tiên hiệp Việt Nam"
```

Đây chính là separation of concerns:

```text
Application
    │
    │ raw values
    ▼
URL Builder
    │
    ▼
yarl
    │
    │ encoding
    ▼
URL
    │
    ▼
httpx
```

---

# 17. Đặc biệt quan trọng với `httpx`

Sau này Fetcher của bạn sẽ có kiểu:

```python
import httpx
from yarl import URL

url = (
    URL("https://example.com/search")
    .with_query({
        "keyword": "truyện kiếm hiệp",
        "page": 2,
    })
)

with httpx.Client() as client:
    response = client.get(str(url))
```

Ở đây:

```text
yarl
 ↓
tạo URL đúng
 ↓
httpx
 ↓
HTTP request
```

Không cần:

```python
urllib.parse.quote(...)
```

rồi lại đưa chuỗi đã encode vào `yarl`.

---

# 18. Encoding không có nghĩa là mã hóa bảo mật

Một nhầm lẫn rất phổ biến:

```text
URL encoding ≠ encryption
```

Ví dụ:

```text
python
```

có thể thành representation encoded:

```text
python
```

hoặc:

```text
python%20sqlite
```

Nhưng bất kỳ ai cũng có thể decode.

URL encoding chỉ nhằm:

* biểu diễn ký tự đặc biệt
* đảm bảo URL hợp lệ
* truyền dữ liệu qua URL

Nó **không bảo mật dữ liệu**.

---

# 19. Một ví dụ tổng hợp

Chạy nguyên chương trình này:

```python
from yarl import URL


def main() -> None:
    url = (
        URL("https://example.com/search")
        .with_query({
            "keyword": "truyện kiếm hiệp",
            "category": "tiên hiệp / huyền huyễn",
            "page": 2,
        })
    )

    print("=" * 60)

    print("URL")
    print(url)

    print("\nSTR")
    print(str(url))

    print("\nQUERY")
    print(url.query)

    print("\nQUERY VALUES")

    print("keyword =", url.query.get("keyword"))
    print("category =", url.query.get("category"))
    print("page =", url.query.get("page"))

    print("\nHUMAN REPRESENTATION")
    print(url.human_repr())

    print("=" * 60)


if __name__ == "__main__":
    main()
```

Điểm cần quan sát:

```text
Python value
     │
     ▼
with_query()
     │
     ▼
yarl encoding
     │
     ▼
str(url)
```

nhưng khi đọc:

```python
url.query.get("keyword")
```

thì ta lại làm việc với **giá trị query**, không phải tự decode `%XX`.

---

# 20. Sai lầm cần tránh

### ❌ Tự replace

```python
url = url.replace(" ", "%20")
```

Không nên.

### ❌ Tự encode trước

```python
keyword = quote(keyword)
url = URL(...).with_query({"q": keyword})
```

Dễ dẫn tới double encoding.

### ❌ Tự parse query

```python
query.split("&")
```

Không nên.

Dùng:

```python
url.query
```

### ❌ Dùng encoded string làm domain value

Domain nên giữ:

```python
"Tiên hiệp Việt Nam"
```

không phải:

```python
"Ti%C3%AAn%20hi%E1%BB%87p%20Vi%E1%BB%87t%20Nam"
```

---

# 21. Mô hình tư duy cần nhớ

Hãy nhớ nguyên tắc này:

```text
                    yarl
                      │
       ┌──────────────┴──────────────┐
       │                             │
  Python values                URL representation
       │                             │
       │  with_query()               │ str()
       ▼                             ▼
"truyện kiếm hiệp"      ...%20...
       ▲
       │
       │ query["keyword"]
       │
       └──────── parsing
```

**Application làm việc với giá trị.**

**`yarl` làm việc với URL representation.**

Đừng trộn hai tầng này với nhau.

---

# 22. Bài tập thực hành

### Bài 1

Tạo:

```python
URL("https://example.com/search")
```

với query:

```text
keyword = "python sqlite"
page = 2
```

Không được tự encode.

---

### Bài 2

Tạo URL với:

```text
keyword = "C++ & Python"
```

Sau đó lấy lại bằng:

```python
url.query["keyword"]
```

và kiểm tra rằng giá trị vẫn là:

```text
C++ & Python
```

---

### Bài 3

Tạo URL:

```text
https://example.com/search?q=truyện%20kiếm%20hiệp
```

Sau đó lấy:

```python
url.query["q"]
```

Quan sát sự khác nhau giữa:

```python
str(url)
url.query["q"]
url.human_repr()
```

---

### Bài 4 — Novel Crawler

Viết:

```python
class SearchURLBuilder:
    ...
```

nhận:

```python
keyword: str
genres: list[str]
page: int
```

và tạo:

```text
/search?keyword=...&genre=...&genre=...&page=...
```

**Không được tự encode bất kỳ giá trị nào.**

---

## Tóm tắt Buổi 29

Ba điều quan trọng nhất:

### 1. Đừng tự encode URL

```python
url.with_query({
    "q": "truyện kiếm hiệp"
})
```

### 2. Đừng double-encode

```text
raw value
   ↓
yarl
   ↓
encoded URL
```

Không:

```text
raw value
   ↓
encode thủ công
   ↓
yarl encode tiếp
```

### 3. Phân biệt dữ liệu và representation

```python
url.query["q"]
```

→ giá trị để application sử dụng.

```python
str(url)
```

→ URL representation.

```python
url.raw_path
```

→ raw/encoded path representation.

```python
url.human_repr()
```

→ representation thân thiện với con người.

**Buổi 30 — Unicode trong URL** sẽ đi sâu hơn vào tiếng Việt, Unicode normalization, `%XX`, Unicode trong path/query và những vấn đề rất dễ gặp khi crawler các website truyện Việt Nam.
