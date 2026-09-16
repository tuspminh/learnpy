# Buổi 28 — `query.getall()`

Ở **Buổi 27**, chúng ta đã học:

```python
url.query.get("page")
```

Nó phù hợp khi một parameter chỉ có **một giá trị**.

Nhưng URL có thể chứa parameter lặp lại:

```text
https://example.com/search?tag=python&tag=sqlite&tag=yarl
```

Lúc này chúng ta cần:

```python
url.query.getall("tag")
```

---

# 1. `getall()` dùng để làm gì?

Cú pháp:

```python
url.query.getall(key)
```

Trả về **tất cả giá trị** của một query parameter.

Ví dụ:

```python
from yarl import URL

url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=sqlite"
    "&tag=yarl"
)

print(url.query.getall("tag"))
```

Kết quả:

```text
['python', 'sqlite', 'yarl']
```

Đây chính là điểm quan trọng nhất của bài hôm nay.

---

# 2. So sánh `get()` và `getall()`

Giả sử:

```python
from yarl import URL

url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=sqlite"
    "&tag=yarl"
)
```

### `get()`

```python
print(url.query.get("tag"))
```

Bạn chỉ lấy **một giá trị** đại diện cho key đó.

### `getall()`

```python
print(url.query.getall("tag"))
```

Bạn lấy toàn bộ:

```text
['python', 'sqlite', 'yarl']
```

Có thể nhớ đơn giản:

```text
get()
   ↓
một value

getall()
   ↓
tất cả value
```

---

# 3. Tại sao cần `getall()`?

Ví dụ website truyện có URL:

```text
/search?genre=fantasy&genre=action&genre=romance
```

Ý nghĩa:

```text
genre = fantasy
genre = action
genre = romance
```

Nếu dùng:

```python
url.query.get("genre")
```

thì bạn không lấy được danh sách đầy đủ.

Dùng:

```python
genres = url.query.getall("genre")
```

ta có:

```python
[
    "fantasy",
    "action",
    "romance",
]
```

Đây là trường hợp rất thực tế đối với **Novel Crawler** của bạn.

---

# 4. `getall()` khi key không tồn tại

Đây là điểm cần nhớ.

Nếu:

```python
url = URL("https://example.com/search")

print(url.query.getall("tag"))
```

thì khi key không tồn tại, `getall()` có thể phát sinh `KeyError`.

Trong code ứng dụng, thường nên truyền giá trị mặc định:

```python
tags = url.query.getall("tag", [])
```

Kết quả:

```python
[]
```

Do đó có một pattern rất hữu ích:

```python
tags = url.query.getall("tag", [])
```

---

# 5. `getall()` và parameter rỗng

Xét URL:

```text
https://example.com/search?tag=
```

Code:

```python
from yarl import URL

url = URL("https://example.com/search?tag=")

print(url.query.getall("tag", []))
```

Kết quả:

```python
['']
```

Điều này khác với:

```text
https://example.com/search
```

Trong trường hợp không có `tag`:

```python
url.query.getall("tag", [])
```

kết quả:

```python
[]
```

Ta có:

```text
?tag=
    ↓
[""]

không có tag
    ↓
[]
```

Đây là sự khác biệt giữa:

**parameter tồn tại nhưng giá trị rỗng**

và

**parameter hoàn toàn không tồn tại**.

---

# 6. `getall()` giữ thứ tự

Ví dụ:

```python
url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=sqlite"
    "&tag=yarl"
)
```

:

```python
tags = url.query.getall("tag")

print(tags)
```

Kết quả:

```python
['python', 'sqlite', 'yarl']
```

Thứ tự trong query được giữ lại.

Điều này hữu ích khi URL có:

```text
?sort=name&sort=date&sort=rating
```

hoặc:

```text
?genre=fantasy&genre=action&genre=romance
```

---

# 7. `getall()` với nhiều parameter khác nhau

Ví dụ:

```python
url = URL(
    "https://example.com/search"
    "?keyword=python"
    "&genre=fantasy"
    "&genre=action"
    "&page=2"
)
```

Ta có:

```python
keyword = url.query.get("keyword")
genres = url.query.getall("genre", [])
page = url.query.get("page", "1")
```

In ra:

```python
print(keyword)
print(genres)
print(page)
```

Kết quả:

```text
python
['fantasy', 'action']
2
```

Đây là cách sử dụng rất tự nhiên:

```text
parameter đơn
    ↓
get()

parameter nhiều giá trị
    ↓
getall()
```

---

# 8. Ví dụ với Novel Crawler

Giả sử URL tìm truyện:

```text
https://truyen.example/search
?keyword=python
&genre=programming
&genre=technology
&genre=tutorial
&page=2
```

Ta viết:

```python
from yarl import URL

url = URL(
    "https://truyen.example/search"
    "?keyword=python"
    "&genre=programming"
    "&genre=technology"
    "&genre=tutorial"
    "&page=2"
)

keyword = url.query.get("keyword")
genres = url.query.getall("genre", [])
page = url.query.get("page", "1")

print("Keyword:", keyword)
print("Genres:", genres)
print("Page:", page)
```

Kết quả:

```text
Keyword: python
Genres: ['programming', 'technology', 'tutorial']
Page: 2
```

---

# 9. Chuyển `page` sang `int`

Nhớ rằng query string về bản chất là text.

```python
page = url.query.get("page", "1")

print(type(page))
```

Kết quả:

```text
<class 'str'>
```

Nếu muốn `int`:

```python
page = int(url.query.get("page", "1"))
```

Sau đó:

```python
print(page)
print(type(page))
```

Kết quả:

```text
2
<class 'int'>
```

---

# 10. `getall()` với số

URL:

```text
https://example.com/books?id=10&id=20&id=30
```

Lấy:

```python
ids = url.query.getall("id", [])
```

Ta nhận:

```python
['10', '20', '30']
```

Nếu domain cần số:

```python
ids = [
    int(value)
    for value in url.query.getall("id", [])
]
```

Kết quả:

```python
[10, 20, 30]
```

Nhưng cần cẩn thận nếu URL bên ngoài có dữ liệu không hợp lệ:

```text
?id=10&id=abc&id=30
```

Khi đó `int("abc")` sẽ lỗi.

Có thể viết parser an toàn:

```python
from yarl import URL


def get_int_list(url: URL, key: str) -> list[int]:
    result = []

    for value in url.query.getall(key, []):
        try:
            result.append(int(value))
        except ValueError:
            continue

    return result


url = URL(
    "https://example.com/books"
    "?id=10"
    "&id=abc"
    "&id=30"
)

ids = get_int_list(url, "id")

print(ids)
```

Kết quả:

```python
[10, 30]
```

---

# 11. Làm sạch danh sách

Một URL thực tế có thể chứa:

```text
?tag=python&tag=sqlite&tag=&tag= yarl
```

Ta có thể làm sạch:

```python
tags = [
    value.strip()
    for value in url.query.getall("tag", [])
    if value.strip()
]
```

Ví dụ:

```python
from yarl import URL

url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=sqlite"
    "&tag="
    "&tag=%20yarl"
)

tags = [
    value.strip()
    for value in url.query.getall("tag", [])
    if value.strip()
]

print(tags)
```

Kết quả:

```python
['python', 'sqlite', 'yarl']
```

Đây là một pattern khá tốt ở tầng parser/application:

```text
URL
 ↓
getall()
 ↓
raw values
 ↓
validate / normalize
 ↓
domain data
```

---

# 12. `getall()` khác `.items()` thế nào?

Giả sử:

```python
url = URL(
    "https://example.com/search"
    "?keyword=python"
    "&tag=sqlite"
    "&tag=yarl"
    "&page=2"
)
```

### Chỉ muốn tất cả `tag`

Dùng:

```python
url.query.getall("tag", [])
```

Kết quả:

```python
['sqlite', 'yarl']
```

### Muốn toàn bộ query

Dùng:

```python
list(url.query.items())
```

Kết quả dạng:

```python
[
    ('keyword', 'python'),
    ('tag', 'sqlite'),
    ('tag', 'yarl'),
    ('page', '2'),
]
```

Vì vậy:

```text
getall("tag")
       ↓
lọc theo một key

items()
       ↓
toàn bộ query entries
```

---

# 13. Đừng chuyển `query` thành `dict` khi có duplicate

Đây là lỗi rất dễ mắc.

```python
url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=sqlite"
    "&tag=yarl"
)
```

Nếu:

```python
params = dict(url.query)
```

thì bạn đã biến cấu trúc nhiều giá trị thành cấu trúc một giá trị.

Không nên dùng cách này nếu duplicate key quan trọng.

Thay vào đó:

```python
tags = url.query.getall("tag", [])
```

hoặc:

```python
items = list(url.query.items())
```

---

# 14. `getall()` và Domain Model

Đây là phần quan trọng khi đưa vào kiến trúc Novel Crawler.

Domain có thể có:

```python
from dataclasses import dataclass


@dataclass
class SearchCriteria:
    keyword: str | None
    genres: list[str]
    page: int
```

URL parser:

```python
from yarl import URL


def parse_search_url(url: URL) -> SearchCriteria:
    keyword = url.query.get("keyword")

    genres = [
        genre.strip()
        for genre in url.query.getall("genre", [])
        if genre.strip()
    ]

    try:
        page = int(url.query.get("page", "1"))
    except ValueError:
        page = 1

    if page < 1:
        page = 1

    return SearchCriteria(
        keyword=keyword,
        genres=genres,
        page=page,
    )
```

Sử dụng:

```python
url = URL(
    "https://truyen.example/search"
    "?keyword=python"
    "&genre=programming"
    "&genre=technology"
    "&page=2"
)

criteria = parse_search_url(url)

print(criteria)
```

Kết quả:

```text
SearchCriteria(
    keyword='python',
    genres=['programming', 'technology'],
    page=2
)
```

Kiến trúc lúc này rất rõ:

```text
URL
 │
 ▼
yarl
 │
 ├── query.get()
 │
 └── query.getall()
 │
 ▼
Parser
 │
 ▼
SearchCriteria
 │
 ▼
Application
```

Domain không cần biết:

```python
MultiDictProxy
```

hay:

```python
yarl.URL
```

Đây chính là cách tách trách nhiệm tốt.

---

# 15. Tạo URL trở lại

Giả sử domain:

```python
genres = [
    "programming",
    "technology",
    "tutorial",
]
```

Khi tạo query có duplicate key, dùng list of tuples:

```python
params = [
    ("genre", genre)
    for genre in genres
]

url = URL("https://truyen.example/search").with_query(params)

print(url)
```

Kết quả:

```text
https://truyen.example/search?genre=programming&genre=technology&genre=tutorial
```

Có thể thêm keyword/page:

```python
params = [
    ("keyword", "python"),
    ("genre", "programming"),
    ("genre", "technology"),
    ("genre", "tutorial"),
    ("page", 2),
]

url = URL("https://truyen.example/search").with_query(params)

print(url)
```

---

# 16. Một ví dụ hoàn chỉnh có thể chạy ngay

```python
from dataclasses import dataclass

from yarl import URL


@dataclass
class SearchCriteria:
    keyword: str | None
    genres: list[str]
    page: int


def parse_search_url(url: URL) -> SearchCriteria:
    # Parameter đơn
    keyword = url.query.get("keyword")

    # Parameter nhiều giá trị
    genres = [
        genre.strip()
        for genre in url.query.getall("genre", [])
        if genre.strip()
    ]

    # Parameter đơn nhưng cần chuyển kiểu
    raw_page = url.query.get("page", "1")

    try:
        page = int(raw_page)
    except ValueError:
        page = 1

    if page < 1:
        page = 1

    return SearchCriteria(
        keyword=keyword,
        genres=genres,
        page=page,
    )


def main() -> None:
    url = URL(
        "https://truyen.example/search"
        "?keyword=python"
        "&genre=programming"
        "&genre=technology"
        "&genre=tutorial"
        "&page=2"
    )

    print("URL:")
    print(url)

    print("\nQuery:")
    print(url.query)

    print("\nAll genres:")
    print(url.query.getall("genre", []))

    criteria = parse_search_url(url)

    print("\nDomain object:")
    print(criteria)

    print("\nGenres:")
    for genre in criteria.genres:
        print("-", genre)


if __name__ == "__main__":
    main()
```

Kết quả:

```text
URL:
https://truyen.example/search?keyword=python&genre=programming&genre=technology&genre=tutorial&page=2

Query:
<MultiDictProxy(...)>

All genres:
['programming', 'technology', 'tutorial']

Domain object:
SearchCriteria(keyword='python', genres=['programming', 'technology', 'tutorial'], page=2)

Genres:
- programming
- technology
- tutorial
```

---

# 17. Pattern cần ghi nhớ

Sau bài này, bạn nên nhớ 4 pattern:

### Một giá trị

```python
value = url.query.get("keyword")
```

### Một giá trị có default

```python
page = url.query.get("page", "1")
```

### Nhiều giá trị

```python
genres = url.query.getall("genre", [])
```

### Toàn bộ query entries

```python
items = list(url.query.items())
```

Có thể hình dung:

```text
                    Query
                      │
          ┌───────────┴───────────┐
          │                       │
     một value               nhiều value
          │                       │
       get()                  getall()
          │                       │
   "python"             ["python", "sqlite", "yarl"]
```

---

# 18. Bài tập

## Bài 1

Cho:

```python
url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=sqlite"
    "&tag=yarl"
)
```

Viết code lấy toàn bộ `tag`.

Kết quả mong muốn:

```python
['python', 'sqlite', 'yarl']
```

---

## Bài 2

Cho:

```text
https://example.com/search?genre=fantasy&genre=action&page=3
```

Lấy:

```python
genres
page
```

Kết quả:

```python
['fantasy', 'action']
3
```

---

## Bài 3

Cho:

```text
https://example.com/books?id=10&id=20&id=30
```

Chuyển thành:

```python
[10, 20, 30]
```

---

## Bài 4 — Novel Crawler

Cho URL:

```text
https://truyen.example/search
?keyword=python
&genre=programming
&genre=tutorial
&genre=technology
&page=4
```

Hãy xây:

```python
SearchCriteria(
    keyword="python",
    genres=[
        "programming",
        "tutorial",
        "technology",
    ],
    page=4,
)
```

---

## Tóm tắt Buổi 28

Điểm quan trọng nhất:

```python
url.query.get("key")
```

→ lấy **một value**

Trong khi:

```python
url.query.getall("key", [])
```

→ lấy **toàn bộ values**

Đặc biệt:

```text
?genre=a&genre=b&genre=c
```

thì:

```python
url.query.getall("genre", [])
```

→

```python
["a", "b", "c"]
```

Đây là API rất quan trọng khi xử lý URL của crawler vì các website thường sử dụng **duplicate query parameters** cho filter, tag, genre, ID, category...

**Buổi 29 — Encoding / Decoding** sẽ đi sâu vào cách `yarl` xử lý `%20`, `%2F`, Unicode, ký tự đặc biệt và sự khác nhau giữa URL đã encode và URL ở dạng human-readable.
