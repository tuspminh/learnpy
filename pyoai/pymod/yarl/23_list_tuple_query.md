# Buổi 23 — List/Tuple → Query với `yarl`

Ở Buổi 22, chúng ta dùng:

```python
params = {
    "keyword": "python",
    "page": 2,
}
```

Cách này rất tốt khi mỗi parameter chỉ có **một giá trị**.

Nhưng trong crawler sẽ có những URL như:

```text
https://example.com/search?tag=python&tag=sqlite&tag=yarl
```

Ở đây:

```text
tag = python
tag = sqlite
tag = yarl
```

cùng một key xuất hiện nhiều lần.

Một `dict` thông thường không biểu diễn tốt trường hợp này.

Hôm nay chúng ta học cách dùng **List/Tuple làm query parameters**.

---

# 1. Vì sao cần List/Tuple?

Ta muốn biểu diễn:

```text
?tag=python&tag=sqlite&tag=yarl
```

Nhưng không thể viết:

```python
params = {
    "tag": "python",
    "tag": "sqlite",
    "tag": "yarl",
}
```

vì Python chỉ giữ key cuối cùng.

```python
print(params)
```

sẽ chỉ còn:

```python
{
    "tag": "yarl"
}
```

---

# 2. Cấu trúc List/Tuple

Thay vì dictionary:

```python
{
    "tag": "python"
}
```

ta có thể biểu diễn query dưới dạng các cặp:

```python
[
    ("tag", "python"),
    ("tag", "sqlite"),
    ("tag", "yarl"),
]
```

Mỗi phần tử là:

```text
(key, value)
```

Ví dụ:

```text
("tag", "python")
     │        │
     │        └── value
     └─────────── key
```

---

# 3. Dùng List of Tuples với `with_query()`

```python
from yarl import URL


params = [
    ("tag", "python"),
    ("tag", "sqlite"),
    ("tag", "yarl"),
]

url = URL(
    "https://example.com/search"
).with_query(params)

print(url)
```

Kết quả:

```text
https://example.com/search?tag=python&tag=sqlite&tag=yarl
```

Đây là một pattern cực kỳ quan trọng.

---

# 4. Dictionary vs List of Tuples

### Dictionary

```python
params = {
    "keyword": "python",
    "page": 2,
}
```

cho:

```text
?keyword=python&page=2
```

### List of tuples

```python
params = [
    ("tag", "python"),
    ("tag", "sqlite"),
]
```

cho:

```text
?tag=python&tag=sqlite
```

Có thể hình dung:

```text
dict
 │
 └── key → một value

list[tuple]
 │
 └── nhiều (key, value)
        │
        └── cho phép duplicate key
```

---

# 5. Một key có thể xuất hiện nhiều lần

Ví dụ:

```python
from yarl import URL


params = [
    ("category", "novel"),
    ("category", "fantasy"),
    ("category", "action"),
]

url = URL(
    "https://example.com/search"
).with_query(params)

print(url)
```

Kết quả:

```text
https://example.com/search?category=novel&category=fantasy&category=action
```

Đây là điều dictionary không thể biểu diễn trực tiếp.

---

# 6. Không chỉ duplicate key

List of tuples cũng cho phép bạn biểu diễn query một cách tuần tự:

```python
params = [
    ("keyword", "python"),
    ("tag", "programming"),
    ("tag", "sqlite"),
    ("page", 2),
]
```

Kết quả:

```text
?keyword=python&tag=programming&tag=sqlite&page=2
```

Điểm quan trọng:

> List giữ thứ tự các phần tử.

---

# 7. Tuple cũng được

Không nhất thiết phải dùng `list`.

Bạn có thể dùng:

```python
params = (
    ("tag", "python"),
    ("tag", "sqlite"),
    ("tag", "yarl"),
)
```

Sau đó:

```python
url = URL(
    "https://example.com/search"
).with_query(params)

print(url)
```

Kết quả:

```text
https://example.com/search?tag=python&tag=sqlite&tag=yarl
```

Về ý tưởng:

```text
list[tuple]
```

và:

```text
tuple[tuple]
```

đều có thể biểu diễn sequence các cặp key/value.

---

# 8. Mixed query

Một URL thực tế có thể vừa có parameter đơn vừa có duplicate parameters:

```text
?keyword=python
&page=2
&tag=programming
&tag=sqlite
```

Ta viết:

```python
from yarl import URL


params = [
    ("keyword", "python"),
    ("page", 2),
    ("tag", "programming"),
    ("tag", "sqlite"),
]

url = URL(
    "https://example.com/search"
).with_query(params)

print(url)
```

Kết quả:

```text
https://example.com/search?keyword=python&page=2&tag=programming&tag=sqlite
```

---

# 9. Query có nhiều value

Một use case phổ biến:

```text
?author=alice&author=bob
```

Code:

```python
from yarl import URL


params = [
    ("author", "alice"),
    ("author", "bob"),
]

url = URL(
    "https://example.com/novels"
).with_query(params)

print(url)
```

Kết quả:

```text
https://example.com/novels?author=alice&author=bob
```

---

# 10. Filter trong Novel Crawler

Giả sử website truyện hỗ trợ:

```text
genre=fantasy
genre=action
genre=romance
```

Ta có:

```python
from yarl import URL


params = [
    ("genre", "fantasy"),
    ("genre", "action"),
    ("genre", "romance"),
]

url = URL(
    "https://example.com/novels"
).with_query(params)

print(url)
```

Kết quả:

```text
https://example.com/novels?genre=fantasy&genre=action&genre=romance
```

Đây là trường hợp thực tế hơn rất nhiều so với ví dụ `tag`.

---

# 11. List value trong dictionary

Bạn cũng sẽ gặp kiểu:

```python
params = {
    "tag": [
        "python",
        "sqlite",
        "yarl",
    ]
}
```

Về mặt ý tưởng, nó biểu diễn:

```text
tag = python
tag = sqlite
tag = yarl
```

Tuy nhiên, khi xây crawler, tôi khuyên bạn **không nên dựa vào "magic" của một cấu trúc nested dict/list mà không kiểm tra format website yêu cầu**.

Cách rõ ràng nhất khi bạn thực sự cần duplicate parameters là:

```python
params = [
    ("tag", "python"),
    ("tag", "sqlite"),
    ("tag", "yarl"),
]
```

Nó thể hiện chính xác:

```text
3 query entries
3 lần tag
```

---

# 12. Tại sao List of Tuples rõ ràng hơn?

So sánh:

```python
params = {
    "tag": ["python", "sqlite", "yarl"]
}
```

với:

```python
params = [
    ("tag", "python"),
    ("tag", "sqlite"),
    ("tag", "yarl"),
]
```

Cái thứ hai nói rất rõ:

```text
query entry #1
query entry #2
query entry #3
```

và đặc biệt:

```text
thứ tự được giữ
duplicate key được phép
```

Đây là lý do kiểu:

```python
list[tuple[str, str]]
```

rất phù hợp để biểu diễn query có duplicate parameters.

---

# 13. Type hint

Ta có thể viết:

```python
from typing import TypeAlias


QueryParams: TypeAlias = list[
    tuple[str, str]
]
```

Ví dụ:

```python
params: QueryParams = [
    ("tag", "python"),
    ("tag", "sqlite"),
    ("page", "2"),
]
```

Sau đó:

```python
url = URL(
    "https://example.com/search"
).with_query(params)
```

---

# 14. Nhưng value không nhất thiết là `str`

Trong code application, bạn có thể muốn:

```python
params = [
    ("keyword", "python"),
    ("page", 2),
]
```

`yarl` sẽ serialize giá trị phù hợp khi tạo URL.

Vì vậy type alias trong application có thể rộng hơn:

```python
from typing import Any, TypeAlias


QueryParams: TypeAlias = list[
    tuple[str, Any]
]
```

Tuy nhiên, đừng vì vậy mà truyền mọi object tùy ý.

Query cuối cùng vẫn phải trở thành một representation mà server hiểu.

---

# 15. Boolean và số

Ví dụ:

```python
from yarl import URL


params = [
    ("page", 2),
    ("limit", 20),
    ("active", True),
]

url = URL(
    "https://example.com/search"
).with_query(params)

print(url)
```

Bạn nên kiểm tra URL thực tế mà website yêu cầu.

Đặc biệt có website yêu cầu:

```text
active=1
```

thay vì:

```text
active=true
```

Khi đó application nên chủ động chuyển đổi:

```python
active = 1 if is_active else 0
```

---

# 16. Unicode

List/Tuple cũng được `yarl` xử lý encoding.

```python
from yarl import URL


params = [
    ("keyword", "lập trình Python"),
    ("tag", "cơ sở dữ liệu"),
]

url = URL(
    "https://example.com/search"
).with_query(params)

print(url)
print(url.human_repr())
```

Ở đây:

```text
Python object
       ↓
yarl
       ↓
URL encoded representation
```

Bạn không cần tự biến:

```text
lập trình Python
```

thành chuỗi `%...`.

---

# 17. Ký tự `&`

Ví dụ:

```python
from yarl import URL


params = [
    ("keyword", "python & sqlite"),
    ("page", 2),
]

url = URL(
    "https://example.com/search"
).with_query(params)

print(url)
```

`&` trong value sẽ được encode để không bị hiểu nhầm là separator giữa các parameters.

Điều này rất quan trọng.

Nếu tự nối:

```python
url = (
    "?keyword=" +
    "python & sqlite"
)
```

thì bạn đang tự chịu trách nhiệm xử lý URL encoding.

---

# 18. Query order

List of tuples giữ thứ tự:

```python
params = [
    ("keyword", "python"),
    ("page", 2),
    ("sort", "newest"),
]
```

sẽ tạo representation theo thứ tự tương ứng:

```text
?keyword=python&page=2&sort=newest
```

Nếu:

```python
params = [
    ("sort", "newest"),
    ("page", 2),
    ("keyword", "python"),
]
```

thì thứ tự cũng thay đổi.

Điều này đôi khi hữu ích khi:

* debug request
* test URL
* tạo URL canonical theo quy tắc riêng
* làm cache key có format ổn định

Nhưng đừng mặc định rằng server coi thứ tự query là có ý nghĩa.

---

# 19. Duplicate parameters và URL equality

Ví dụ:

```text
?tag=python&tag=sqlite
```

và:

```text
?tag=sqlite&tag=python
```

có thể có ý nghĩa giống nhau đối với một website, nhưng không phải lúc nào application/server cũng xử lý chúng giống nhau.

Do đó khi xây crawler, bạn cần xác định:

```text
URL normalization policy
```

chứ không nên tự ý sort mọi query.

Phần này sẽ liên quan trực tiếp tới:

```text
Buổi 36 — URL normalization
Buổi 38 — URL deduplication
Buổi 39 — Canonical URL
```

---

# 20. Một ví dụ thực tế: Multi-tag Search

Ta xây một class nhỏ:

```python
from yarl import URL


class SearchURLBuilder:

    def __init__(self, base_url: URL):
        self.base_url = base_url

    def build(
        self,
        keyword: str,
        tags: list[str],
        page: int,
    ) -> URL:

        params = [
            ("keyword", keyword),
            ("page", page),
        ]

        for tag in tags:
            params.append(
                ("tag", tag)
            )

        return self.base_url.with_query(params)
```

Sử dụng:

```python
def main():
    builder = SearchURLBuilder(
        URL("https://example.com/search")
    )

    url = builder.build(
        keyword="python",
        tags=[
            "sqlite",
            "crawler",
            "yarl",
        ],
        page=2,
    )

    print(url)


if __name__ == "__main__":
    main()
```

Kết quả:

```text
https://example.com/search?keyword=python&page=2&tag=sqlite&tag=crawler&tag=yarl
```

---

# 21. Đây là một pattern rất đáng nhớ

Ta có:

```python
params = [
    ("keyword", "python"),
    ("page", 2),
]
```

Sau đó:

```python
for tag in tags:
    params.append(
        ("tag", tag)
    )
```

Nếu:

```python
tags = [
    "sqlite",
    "crawler",
    "yarl",
]
```

thì:

```python
params
```

trở thành:

```python
[
    ("keyword", "python"),
    ("page", 2),
    ("tag", "sqlite"),
    ("tag", "crawler"),
    ("tag", "yarl"),
]
```

và:

```python
url.with_query(params)
```

serialize thành:

```text
?keyword=python&page=2&tag=sqlite&tag=crawler&tag=yarl
```

---

# 22. Có thể dùng list comprehension

Ví dụ:

```python
tags = [
    "sqlite",
    "crawler",
    "yarl",
]

params = [
    ("keyword", "python"),
    ("page", 2),
    *[
        ("tag", tag)
        for tag in tags
    ],
]
```

Kết quả:

```python
[
    ("keyword", "python"),
    ("page", 2),
    ("tag", "sqlite"),
    ("tag", "crawler"),
    ("tag", "yarl"),
]
```

Sau đó:

```python
url = URL(
    "https://example.com/search"
).with_query(params)
```

---

# 23. Nhưng đừng abstraction quá sớm

Trong project crawler của bạn, không nên ngay lập tức xây:

```text
QueryManager
QueryFactory
QuerySerializer
QueryCollection
QueryParameterRegistry
...
```

chỉ để tạo:

```text
?page=2
```

Ban đầu:

```python
params = [
    ("keyword", keyword),
    ("page", page),
]
```

là đủ.

Chỉ khi requirement thực sự xuất hiện:

```text
duplicate parameters
optional parameters
query normalization
canonicalization
pagination
filters
```

thì mới tách abstraction.

Đây cũng phù hợp với nguyên tắc chúng ta đã học trong DDD/SOLID:

> **Abstraction nên xuất hiện từ complexity thực tế, không phải từ mong muốn abstraction hóa mọi thứ.**

---

# 24. List/Tuple phù hợp với Parser như thế nào?

Giả sử parser phát hiện URL:

```text
/search?tag=python&tag=sqlite
```

Ta đọc query thành các cặp:

```text
tag → python
tag → sqlite
```

Nếu sau đó cần tạo lại URL, cấu trúc:

```python
[
    ("tag", "python"),
    ("tag", "sqlite"),
]
```

sẽ bảo toàn duplicate entries tốt hơn dictionary.

Đây là lý do:

```text
URL
 ↓
Query
 ↓
list of pairs
 ↓
URL
```

là một workflow quan trọng.

---

# 25. Một ví dụ hoàn chỉnh

Hãy chạy nguyên chương trình:

```python
from yarl import URL


def build_search_url(
    keyword: str,
    tags: list[str],
    page: int,
) -> URL:

    params = [
        ("keyword", keyword),
        ("page", page),
    ]

    for tag in tags:
        params.append(
            ("tag", tag)
        )

    return URL(
        "https://example.com/search"
    ).with_query(params)


def main():
    url = build_search_url(
        keyword="python",
        tags=[
            "sqlite",
            "crawler",
            "yarl",
        ],
        page=2,
    )

    print("URL:")
    print(url)

    print("\nHuman representation:")
    print(url.human_repr())


if __name__ == "__main__":
    main()
```

Logic:

```text
keyword = python
page = 2
tag = sqlite
tag = crawler
tag = yarl
```

→

```text
https://example.com/search
    ?keyword=python
    &page=2
    &tag=sqlite
    &tag=crawler
    &tag=yarl
```

---

# 26. So sánh ba cách

| Cấu trúc       | Ví dụ                                  | Duplicate key |
| -------------- | -------------------------------------- | ------------- |
| `dict`         | `{"page": 2}`                          | ❌             |
| `list[tuple]`  | `[("tag","python"), ("tag","sqlite")]` | ✅             |
| `tuple[tuple]` | `(("tag","python"), ("tag","sqlite"))` | ✅             |

Mental model:

```text
dict
    ↓
one key → one value

list[tuple]
    ↓
many query entries
    ↓
duplicate keys possible
```

---

# 27. Khi nào dùng Dictionary?

Dùng:

```python
params = {
    "keyword": "python",
    "page": 2,
    "sort": "newest",
}
```

khi query có dạng:

```text
keyword = ...
page = ...
sort = ...
```

mỗi key một value.

---

# 28. Khi nào dùng List/Tuple?

Dùng:

```python
params = [
    ("tag", "python"),
    ("tag", "sqlite"),
    ("tag", "yarl"),
]
```

khi cần:

```text
duplicate key
```

hoặc muốn biểu diễn rõ ràng:

```text
sequence of query entries
```

---

# 29. Kiến trúc Novel Crawler

Ta có thể bắt đầu hình thành:

```text
SearchCriteria
       │
       ↓
SearchURLBuilder
       │
       ├── simple params
       │
       │     dict
       │
       └── repeated params
             │
             list[tuple]
       │
       ↓
    yarl.URL
       │
       ↓
     Fetcher
       │
       ↓
      httpx
```

Điều này sẽ rất hữu ích khi parser của bạn gặp các website có query phức tạp.

---

# 30. Tổng kết Buổi 23

Điểm quan trọng nhất hôm nay là:

```python
params = [
    ("tag", "python"),
    ("tag", "sqlite"),
    ("tag", "yarl"),
]

url = URL(
    "https://example.com/search"
).with_query(params)
```

→

```text
https://example.com/search?tag=python&tag=sqlite&tag=yarl
```

### Dictionary

```python
{
    "page": 2,
    "keyword": "python",
}
```

phù hợp:

```text
key → một value
```

### List/Tuple

```python
[
    ("tag", "python"),
    ("tag", "sqlite"),
]
```

phù hợp:

```text
key → nhiều value
```

---

# 🧪 Bài tập Buổi 23

### Bài 1

Tạo URL:

```text
https://example.com/search?tag=python&tag=sqlite&tag=yarl
```

bằng `list[tuple]`.

---

### Bài 2

Tạo:

```text
https://example.com/search?keyword=python&tag=sqlite&tag=crawler&page=2
```

bằng:

```python
params = [
    ...
]
```

---

### Bài 3

Viết function:

```python
def build_tag_url(
    tags: list[str],
) -> URL:
    ...
```

Sao cho:

```python
build_tag_url(
    ["python", "sqlite", "yarl"]
)
```

tạo:

```text
https://example.com/search?tag=python&tag=sqlite&tag=yarl
```

---

### Bài 4 — Novel Crawler

Viết:

```python
class NovelSearchURLBuilder:
    ...
```

hỗ trợ:

```python
keyword="python"

tags=[
    "crawler",
    "sqlite",
    "yarl",
]

page=2
```

và tạo URL tương ứng.

---

### Bài 5 — suy nghĩ kiến trúc

Giải thích tại sao cấu trúc:

```python
[
    ("tag", "python"),
    ("tag", "sqlite"),
]
```

phù hợp hơn:

```python
{
    "tag": ["python", "sqlite"]
}
```

khi mục tiêu của chúng ta là biểu diễn **chính xác từng query parameter entry**.

---

## Tiếp theo — Buổi 24

```text
### Buổi 24 — Duplicate Query Parameters
```

Buổi 23 mới chỉ tạo được duplicate query. Buổi 24 chúng ta sẽ đi sâu vào **đọc, giữ nguyên, sửa và xử lý duplicate parameters**, đặc biệt là:

```text
?tag=python&tag=sqlite&tag=yarl
```

và vì sao:

```python
dict(url.query)
```

có thể làm mất thông tin mà crawler cần bảo toàn.
