# Phần III — Query String chuyên sâu

# Buổi 26 — `query_string`

Ở Buổi 25, chúng ta đã học:

```python
url.query
```

và biết rằng nó là cấu trúc dữ liệu để **làm việc với query**.

Hôm nay chúng ta học:

```python
url.query_string
```

Điểm cốt lõi của bài này là phân biệt thật rõ:

```text
url.query
     ↓
dữ liệu query đã được parse

url.query_string
     ↓
chuỗi query đã được encode
```

Đây là kiến thức rất quan trọng khi bạn xây **URL parser, URL normalizer và crawler**.

---

# 1. Query string là gì?

Cho URL:

```text
https://example.com/search?keyword=python&page=2
```

Ta có:

```text
scheme
  ↓
https

host
  ↓
example.com

path
  ↓
/search

query string
  ↓
keyword=python&page=2
```

Phần query string là:

```text
keyword=python&page=2
```

Không bao gồm dấu:

```text
?
```

---

# 2. Lấy `query_string`

```python
from yarl import URL


url = URL(
    "https://example.com/search"
    "?keyword=python"
    "&page=2"
)

print(url.query_string)
```

Kết quả:

```text
keyword=python&page=2
```

Trong khi:

```python
print(url)
```

cho:

```text
https://example.com/search?keyword=python&page=2
```

Vì vậy:

```text
URL
 │
 ├── ?
 │
 └── query_string
```

---

# 3. `query` và `query_string` khác nhau thế nào?

Ví dụ:

```python
from yarl import URL


url = URL(
    "https://example.com/search"
    "?keyword=python"
    "&page=2"
)
```

### `query`

```python
print(url.query)
```

đại diện cho dữ liệu đã parse:

```text
keyword → python
page    → 2
```

### `query_string`

```python
print(url.query_string)
```

là:

```text
keyword=python&page=2
```

Mental model:

```text
                URL
                 │
          ┌──────┴──────┐
          ↓             ↓
       query       query_string
          │             │
          ↓             ↓
   structured data     string
```

---

# 4. Tại sao cần cả hai?

Bởi vì hai API phục vụ hai mục đích khác nhau.

Nếu bạn muốn:

> "Lấy giá trị `page`"

dùng:

```python
url.query.get("page")
```

Nếu bạn muốn:

> "Lấy toàn bộ query dưới dạng chuỗi"

dùng:

```python
url.query_string
```

Ví dụ:

```python
query = url.query.get("page")

print(query)
```

→ đọc dữ liệu.

Còn:

```python
print(url.query_string)
```

→ lấy representation của query.

---

# 5. Query có encoding

Đây là phần quan trọng.

Giả sử:

```python
from yarl import URL


url = URL(
    "https://example.com/search"
).with_query(
    {
        "q": "hello world",
    }
)

print(url)
print(url.query_string)
```

Bạn sẽ thấy query được encode phù hợp trong URL representation.

Trong URL, space không nên được xử lý bằng cách tự:

```python
url.replace(" ", "%20")
```

Hãy để `yarl` xử lý encoding.

---

# 6. Unicode

Ví dụ tiếng Việt:

```python
from yarl import URL


url = URL(
    "https://example.com/search"
).with_query(
    {
        "q": "lập trình Python",
    }
)

print("URL:")
print(url)

print("\nQuery string:")
print(url.query_string)

print("\nDecoded value:")
print(url.query["q"])
```

Điểm quan trọng:

```text
URL representation
        ↓
encoded

url.query
        ↓
decoded value
```

Tức là application có thể làm việc với:

```text
lập trình Python
```

mà không cần tự viết logic percent-decoding.

---

# 7. `query_string` không có `?`

Ví dụ:

```python
url = URL(
    "https://example.com/search?page=2"
)
```

thì:

```python
print(url.query_string)
```

là:

```text
page=2
```

không phải:

```text
?page=2
```

Nếu bạn cần toàn bộ URL:

```python
str(url)
```

Nếu cần phần query:

```python
url.query_string
```

---

# 8. URL không có query

```python
from yarl import URL


url = URL(
    "https://example.com/search"
)

print(url.query_string)
```

Kết quả là chuỗi rỗng:

```text
''
```

Bạn có thể kiểm tra:

```python
if not url.query_string:
    print("No query")
```

---

# 9. Query chỉ có một parameter

```python
url = URL(
    "https://example.com/search?page=2"
)

print(url.query_string)
```

Kết quả:

```text
page=2
```

---

# 10. Nhiều parameters

```python
url = URL(
    "https://example.com/search"
    "?keyword=python"
    "&page=2"
    "&sort=new"
)

print(url.query_string)
```

Kết quả:

```text
keyword=python&page=2&sort=new
```

Thứ tự query entries được phản ánh trong string representation.

---

# 11. Duplicate parameters

Đây là liên hệ trực tiếp với Buổi 24.

```python
url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=sqlite"
    "&tag=yarl"
)

print(url.query_string)
```

Kết quả:

```text
tag=python&tag=sqlite&tag=yarl
```

Không bị biến thành:

```text
tag=yarl
```

như khi bạn ép dữ liệu về `dict`.

Đồng thời:

```python
print(url.query.getall("tag"))
```

cho:

```text
['python', 'sqlite', 'yarl']
```

---

# 12. `query_string` là representation, không phải nơi để query dữ liệu

Đừng làm:

```python
query_string = url.query_string

# rồi tự split
parts = query_string.split("&")
```

rồi:

```python
key, value = part.split("=")
```

Cách này rất dễ sai.

Ví dụ value có thể chứa:

```text
&
=
%
Unicode
encoded characters
```

URL parser đã giải quyết những vấn đề này cho bạn.

Thay vì:

```python
query_string.split("&")
```

hãy dùng:

```python
url.query
```

---

# 13. Ví dụ dễ thấy lỗi

Giả sử:

```python
from yarl import URL


url = URL(
    "https://example.com/search"
).with_query(
    {
        "q": "python & sqlite",
    }
)

print(url)
```

Query cần được encode đúng.

Nếu bạn tự:

```python
query_string.split("&")
```

thì bạn đang giả định rằng mọi `&` đều là separator.

Đó là một giả định nguy hiểm nếu dữ liệu đã được encoded/decoded ở các bước khác nhau.

**Hãy để `yarl` parse URL.**

---

# 14. `query_string` rất hữu ích cho logging

Trong crawler, đôi khi log:

```python
print(url)
```

là quá dài.

Bạn có thể:

```python
print("Query:", url.query_string)
```

Ví dụ:

```text
Query: keyword=python&page=2&sort=new
```

Hoặc:

```python
print(
    f"Fetching: {url.origin()}"
    f"{url.path}"
    f"?{url.query_string}"
)
```

Nhưng nếu query rỗng thì cách nối `?` thủ công phải xử lý cẩn thận.

Tốt hơn thường là log:

```python
print(f"Fetching: {url}")
```

và chỉ dùng `query_string` khi thực sự cần query riêng.

---

# 15. `query_string` trong URL debugging

Ví dụ crawler gặp:

```text
https://example.com/novels?genre=fantasy&genre=action&page=3
```

Bạn có thể debug:

```python
from yarl import URL


url = URL(
    "https://example.com/novels"
    "?genre=fantasy"
    "&genre=action"
    "&page=3"
)

print("Path:")
print(url.path)

print("Query:")
print(url.query)

print("Query string:")
print(url.query_string)
```

Kết quả conceptually:

```text
Path:
/novels

Query:
MultiDictProxy(...)

Query string:
genre=fantasy&genre=action&page=3
```

---

# 16. `query_string` và `str(url)`

So sánh:

```python
from yarl import URL


url = URL(
    "https://example.com/search"
    "?keyword=python"
    "&page=2"
)

print("str(url):")
print(str(url))

print("\nquery_string:")
print(url.query_string)
```

Kết quả:

```text
str(url):
https://example.com/search?keyword=python&page=2

query_string:
keyword=python&page=2
```

Mental model:

```text
str(url)
    ↓
toàn bộ URL

query_string
    ↓
chỉ phần query
```

---

# 17. `query` và `query_string` trong crawler

Đây là cách tôi muốn bạn tư duy:

```text
                  URL
                   │
          ┌────────┴────────┐
          │                 │
          ▼                 ▼
       query          query_string
          │                 │
          │                 │
          ▼                 ▼
   application logic     representation
          │                 │
          │                 ├── logging
          │                 ├── debugging
          │                 └── URL output
          │
          ├── get()
          ├── getall()
          └── items()
```

---

# 18. Query → application data

Ví dụ:

```python
from yarl import URL


url = URL(
    "https://example.com/novels"
    "?genre=fantasy"
    "&genre=action"
    "&page=3"
)

genres = url.query.getall("genre")
page = int(url.query.get("page", "1"))

print(genres)
print(page)
```

Đây là **application-level usage**.

---

# 19. Query string → representation

Ngược lại:

```python
query_string = url.query_string

print(query_string)
```

Ta nhận:

```text
genre=fantasy&genre=action&page=3
```

Đây là **URL-level representation**.

---

# 20. Không nên tự encode query

Ví dụ không nên:

```python
keyword = "lập trình Python"

url = URL(
    "https://example.com/search"
    f"?q={keyword}"
)
```

Rồi tự xử lý:

```python
keyword.replace(" ", "%20")
```

hoặc:

```python
quote(...)
```

ở mọi chỗ.

Tốt hơn:

```python
url = URL(
    "https://example.com/search"
).with_query(
    {
        "q": keyword,
    }
)
```

`yarl` chịu trách nhiệm xây dựng URL hợp lệ.

---

# 21. Đặc biệt quan trọng với dấu `&`

Giả sử:

```python
query = "python & sqlite"
```

Bạn muốn:

```text
q=python & sqlite
```

là **một value duy nhất**.

Hãy để:

```python
URL(...).with_query(...)
```

xử lý.

Không tự ghép:

```python
"?q=" + query
```

rồi hy vọng parser sẽ hiểu đúng ý bạn.

---

# 22. `query_string` sau `with_query()`

Ví dụ:

```python
from yarl import URL


base = URL(
    "https://example.com/search"
)

url = base.with_query(
    {
        "keyword": "python",
        "page": 2,
    }
)

print(url.query_string)
```

Kết quả:

```text
keyword=python&page=2
```

---

# 23. `with_query(None)` và `query_string`

Ở Buổi 21 chúng ta đã học:

```python
url.with_query(None)
```

để xóa query.

Ví dụ:

```python
from yarl import URL


url = URL(
    "https://example.com/search"
    "?keyword=python"
    "&page=2"
)

print(url.query_string)

new_url = url.with_query(None)

print(new_url.query_string)
print(new_url)
```

Kết quả conceptually:

```text
keyword=python&page=2

''

https://example.com/search
```

Đây là một pattern rất hữu ích khi normalize URL.

---

# 24. Một utility nhỏ

Ta có thể viết:

```python
from yarl import URL


def get_query_string(url: URL) -> str:
    return url.query_string
```

Nhưng thực tế:

```python
url.query_string
```

đã đủ đơn giản.

Không nên tạo abstraction chỉ để bọc một property đơn giản.

---

# 25. Utility thực tế hơn

Nếu cần logging:

```python
from yarl import URL


def log_url(url: URL) -> None:
    print(f"Scheme : {url.scheme}")
    print(f"Host   : {url.host}")
    print(f"Path   : {url.path}")
    print(f"Query  : {url.query_string}")
    print(f"Full   : {url}")
```

Sử dụng:

```python
url = URL(
    "https://example.com/search"
    "?keyword=python"
    "&page=2"
)

log_url(url)
```

Output:

```text
Scheme : https
Host   : example.com
Path   : /search
Query  : keyword=python&page=2
Full   : https://example.com/search?keyword=python&page=2
```

---

# 26. Query string trong URL canonicalization

Đây là kiến thức sẽ rất hữu ích cho các bài sau.

Crawler có thể gặp:

```text
https://example.com/book?id=10
```

và:

```text
https://example.com/book?id=10&utm_source=google
```

Nếu website coi `utm_source` là tracking parameter, application có thể muốn loại bỏ nó.

Ta có:

```python
from yarl import URL


url = URL(
    "https://example.com/book"
    "?id=10"
    "&utm_source=google"
)
```

Ta có thể inspect:

```python
print(url.query_string)
```

→

```text
id=10&utm_source=google
```

Sau đó dùng `url.query` để phân tích và `with_query()` để tạo URL mới.

**Không nên dùng `query_string.replace()` để làm normalization.**

Đây là nền tảng cho:

```text
Buổi 36 — URL normalization
Buổi 37 — URL comparison
Buổi 38 — URL deduplication
Buổi 39 — Canonical URL
```

---

# 27. Complete example — Query Inspector

Hãy chạy nguyên chương trình này:

```python
from yarl import URL


def inspect_url(url: URL) -> None:
    print("=" * 50)

    print("FULL URL")
    print(url)

    print("\nPATH")
    print(url.path)

    print("\nQUERY")
    print(url.query)

    print("\nQUERY STRING")
    print(url.query_string)

    print("\nQUERY ITEMS")

    for key, value in url.query.items():
        print(f"{key} = {value}")


def main():
    url = URL(
        "https://example.com/novels"
        "?keyword=python"
        "&genre=fantasy"
        "&genre=action"
        "&page=2"
    )

    inspect_url(url)


if __name__ == "__main__":
    main()
```

Bạn sẽ thấy rõ ba tầng:

```text
URL
 │
 ├── path
 │     └── /novels
 │
 ├── query
 │     └── MultiDictProxy
 │
 └── query_string
       └── keyword=python&genre=fantasy&genre=action&page=2
```

---

# 28. Một ví dụ quan trọng hơn cho crawler

```python
from yarl import URL


def analyze_search_url(url: URL) -> None:
    print("URL:", url)

    print("\nRaw query representation:")
    print(url.query_string)

    print("\nSearch keyword:")
    print(url.query.get("keyword"))

    print("\nGenres:")
    print(url.query.getall("genre"))

    print("\nPage:")
    print(url.query.get("page"))


def main():
    url = URL(
        "https://example.com/novels"
        "?keyword=python"
        "&genre=fantasy"
        "&genre=action"
        "&page=3"
    )

    analyze_search_url(url)


if __name__ == "__main__":
    main()
```

Output:

```text
URL: https://example.com/novels?keyword=python&genre=fantasy&genre=action&page=3

Raw query representation:
keyword=python&genre=fantasy&genre=action&page=3

Search keyword:
python

Genres:
['fantasy', 'action']

Page:
3
```

Đây chính là kiểu xử lý URL mà sau này Parser/Fetcher của Novel Crawler sẽ cần.

---

# 29. 🧠 Phân biệt 4 thứ

Bạn nên thuộc lòng bảng này:

| API                       | Ý nghĩa                | Ví dụ                  |
| ------------------------- | ---------------------- | ---------------------- |
| `url.query`               | Query đã parse         | `MultiDictProxy(...)`  |
| `url.query_string`        | Query dưới dạng string | `"page=2&tag=python"`  |
| `url.query["page"]`       | Một value              | `"2"`                  |
| `url.query.getall("tag")` | Tất cả values          | `["python", "sqlite"]` |

Và:

```python
str(url)
```

là:

```text
toàn bộ URL
```

---

# 30. Quy tắc sử dụng

Khi bạn muốn:

### Đọc dữ liệu

```python
url.query
```

### Lấy một parameter

```python
url.query.get("page")
```

### Lấy duplicate values

```python
url.query.getall("tag")
```

### Duyệt toàn bộ entries

```python
url.query.items()
```

### Lấy query dưới dạng encoded string

```python
url.query_string
```

### Lấy toàn bộ URL

```python
str(url)
```

---

# 🧪 Bài tập Buổi 26

## Bài 1

Cho:

```python
url = URL(
    "https://example.com/search"
    "?keyword=python"
    "&page=2"
)
```

In:

```text
keyword=python&page=2
```

bằng `query_string`.

---

## Bài 2

Cho:

```text
https://example.com/search?tag=python&tag=sqlite&tag=yarl
```

In:

```text
tag=python&tag=sqlite&tag=yarl
```

bằng `query_string`.

---

## Bài 3

Cho:

```python
url = URL(
    "https://example.com/search"
    "?q=lập%20trình"
)
```

Hãy thử:

```python
print(url.query)
print(url.query_string)
print(url.query["q"])
```

và quan sát sự khác nhau giữa **encoded representation** và **decoded value**.

---

## Bài 4 — crawler

Cho:

```text
https://example.com/novels
?genre=fantasy
&genre=action
&page=3
```

Hãy in:

```text
Full URL:
...

Query string:
...

Genres:
...

Page:
...
```

---

## Bài 5 — tư duy

Giải thích tại sao đoạn code này không nên dùng để parse query:

```python
query_string = url.query_string

parts = query_string.split("&")

for part in parts:
    key, value = part.split("=")
```

và tại sao:

```python
url.query
```

an toàn/phù hợp hơn.

---

# 🎯 Tổng kết Buổi 26

Điểm quan trọng nhất:

```text
url.query
     ↓
structured query data
     ↓
dùng để đọc / phân tích

url.query_string
     ↓
encoded query string
     ↓
dùng khi cần representation
```

Đặc biệt:

```python
url.query
```

**không phải string**.

Còn:

```python
url.query_string
```

**là string**.

Và đừng biến việc xử lý URL thành:

```python
split("&")
split("=")
replace(...)
```

khi `yarl` đã cung cấp parser và encoder cho bạn.

### Bài tiếp theo

```text
Buổi 27 — query.get()
```

Chúng ta sẽ đi sâu vào:

```python
url.query.get("page")
url.query.get("page", "1")
url.query.get("missing")
```

đặc biệt là **default value, missing key, duplicate key và cách dùng `.get()` an toàn trong Parser của Novel Crawler**.
