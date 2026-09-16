# Phần III — Query String chuyên sâu

# Buổi 27 — `query.get()`

Ở Buổi 25, chúng ta đã biết:

```python
url.query
```

là `MultiDictProxy`.

Ở Buổi 26:

```python
url.query_string
```

là query dưới dạng chuỗi.

Hôm nay tập trung hoàn toàn vào:

```python
url.query.get()
```

Đây là API bạn sẽ dùng **rất thường xuyên trong Parser của Novel Crawler**, đặc biệt với các query parameter có thể có hoặc không.

---

# 1. `query.get()` dùng để làm gì?

Cho URL:

```python
from yarl import URL


url = URL(
    "https://example.com/novels"
    "?page=3"
    "&keyword=python"
)
```

Ta có:

```python
page = url.query.get("page")
keyword = url.query.get("keyword")

print(page)
print(keyword)
```

Kết quả:

```text
3
python
```

Về bản chất:

```text
query.get(key)
       ↓
tìm parameter
       ↓
trả về value
```

---

# 2. Tại sao dùng `get()` thay vì `[]`?

Có hai cách:

```python
url.query["page"]
```

và:

```python
url.query.get("page")
```

Nếu `page` chắc chắn tồn tại:

```python
page = url.query["page"]
```

có thể dùng được.

Nhưng nếu `page` là optional:

```python
page = url.query.get("page")
```

an toàn hơn.

Ví dụ URL:

```text
https://example.com/novels
```

không có query.

```python
url.query["page"]
```

sẽ phát sinh lỗi.

Trong khi:

```python
url.query.get("page")
```

trả về:

```python
None
```

Đây là lý do `.get()` rất hữu ích trong parser.

---

# 3. Ví dụ cơ bản

```python
from yarl import URL


url = URL(
    "https://example.com/search"
    "?keyword=python"
    "&page=2"
)


print(url.query.get("keyword"))
print(url.query.get("page"))
```

Output:

```text
python
2
```

Nhớ rằng `"2"` là string:

```python
page = url.query.get("page")

print(page)
print(type(page))
```

Kết quả:

```text
2
<class 'str'>
```

---

# 4. Key không tồn tại

```python
from yarl import URL


url = URL(
    "https://example.com/search"
    "?keyword=python"
)


print(url.query.get("page"))
```

Kết quả:

```text
None
```

Không có exception.

Mental model:

```text
query["page"]
    ↓
không có
    ↓
KeyError
```

Trong khi:

```text
query.get("page")
    ↓
không có
    ↓
None
```

---

# 5. Default value

Đây là tính năng cực kỳ hữu ích.

```python
page = url.query.get("page", "1")
```

Nếu `page` tồn tại:

```text
?page=3
```

→

```text
"3"
```

Nếu không tồn tại:

```text
(no page)
```

→

```text
"1"
```

Ví dụ:

```python
from yarl import URL


url = URL(
    "https://example.com/novels"
)

page = url.query.get("page", "1")

print(page)
```

Output:

```text
1
```

---

# 6. Tại sao `"1"` chứ không phải `1`?

Vì query values là string.

Do đó:

```python
page = url.query.get("page", "1")
```

cho:

```python
"1"
```

Nếu domain/application cần integer:

```python
page = int(
    url.query.get("page", "1")
)
```

Bây giờ:

```python
print(page)
print(type(page))
```

→

```text
1
<class 'int'>
```

Đây là pattern cực kỳ phổ biến:

```python
page = int(url.query.get("page", "1"))
```

---

# 7. Nhưng có một vấn đề

Đoạn này:

```python
page = int(
    url.query.get("page", "1")
)
```

chỉ an toàn nếu query chứa số hợp lệ.

Ví dụ:

```text
?page=abc
```

sẽ gây:

```text
ValueError
```

Do đó Parser thực tế nên validate.

---

# 8. Tạo helper parse integer

Ví dụ:

```python
from yarl import URL


def get_int_query(
    url: URL,
    key: str,
    default: int,
) -> int:
    value = url.query.get(key)

    if value is None:
        return default

    try:
        return int(value)
    except ValueError:
        return default
```

Sử dụng:

```python
url = URL(
    "https://example.com/novels"
    "?page=3"
)

page = get_int_query(
    url,
    "page",
    1,
)

print(page)
```

Output:

```text
3
```

Nếu:

```text
?page=abc
```

thì:

```text
1
```

---

# 9. `get()` không decode thành kiểu Python

Ví dụ:

```text
?page=3
```

```python
page = url.query.get("page")
```

→

```python
"3"
```

Không tự động:

```python
3
```

Tương tự:

```text
?active=true
```

cho:

```python
"true"
```

chứ không phải:

```python
True
```

Nếu domain cần boolean, application phải chuyển đổi.

---

# 10. Helper parse boolean

Ví dụ:

```python
from yarl import URL


def get_bool_query(
    url: URL,
    key: str,
    default: bool,
) -> bool:

    value = url.query.get(key)

    if value is None:
        return default

    value = value.lower()

    if value in {"true", "1", "yes"}:
        return True

    if value in {"false", "0", "no"}:
        return False

    return default
```

Sử dụng:

```python
url = URL(
    "https://example.com/search"
    "?active=true"
)

active = get_bool_query(
    url,
    "active",
    False,
)

print(active)
```

→

```text
True
```

Điểm kiến trúc quan trọng:

> `yarl` chỉ giúp bạn đọc URL/query. Việc biến `"true"` thành `True` thuộc application/domain logic.

---

# 11. `get()` với duplicate key

Đây là phần rất quan trọng.

URL:

```python
from yarl import URL


url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=sqlite"
    "&tag=yarl"
)
```

Nếu:

```python
print(url.query.get("tag"))
```

thì `.get()` chỉ lấy **một value**, không phải toàn bộ danh sách.

Với duplicate parameter, nếu bạn muốn tất cả:

```python
url.query.getall("tag")
```

Kết quả:

```python
[
    "python",
    "sqlite",
    "yarl",
]
```

Vì vậy:

```text
get()
    ↓
một value

getall()
    ↓
tất cả values
```

---

# 12. Khi nào `get()` là lựa chọn đúng?

Các parameter thường chỉ có một value:

```text
page=2
keyword=python
status=completed
sort=latest
slug=python-tutorial
```

Ví dụ:

```python
page = url.query.get("page")
status = url.query.get("status")
sort = url.query.get("sort")
```

---

# 13. Khi nào không nên dùng `get()`?

Nếu website dùng:

```text
?tag=python&tag=sqlite&tag=yarl
```

thì:

```python
tags = url.query.get("tag")
```

không thể biểu diễn đầy đủ:

```python
[
    "python",
    "sqlite",
    "yarl",
]
```

Phải dùng:

```python
tags = url.query.getall("tag")
```

Buổi 28 sẽ đi sâu riêng vào `getall()`.

---

# 14. Optional pagination

Đây là ví dụ rất sát Novel Crawler.

URL 1:

```text
https://example.com/novels
```

URL 2:

```text
https://example.com/novels?page=2
```

Parser:

```python
from yarl import URL


def get_page(url: URL) -> int:
    value = url.query.get("page")

    if value is None:
        return 1

    return int(value)
```

Test:

```python
url1 = URL(
    "https://example.com/novels"
)

url2 = URL(
    "https://example.com/novels?page=2"
)

print(get_page(url1))
print(get_page(url2))
```

Output:

```text
1
2
```

---

# 15. Viết ngắn hơn

Nếu website đảm bảo `page` luôn hợp lệ:

```python
def get_page(url: URL) -> int:
    return int(
        url.query.get("page", "1")
    )
```

Đây là cách rất phổ biến.

Nhưng nhớ:

```text
page=abc
```

vẫn có thể gây:

```text
ValueError
```

Nếu dữ liệu từ website không đáng tin, hãy validate.

---

# 16. Parser nên xử lý dữ liệu không hợp lệ

Ví dụ:

```python
from yarl import URL


def get_page(url: URL) -> int:
    raw_page = url.query.get("page")

    if raw_page is None:
        return 1

    try:
        page = int(raw_page)
    except ValueError:
        return 1

    if page < 1:
        return 1

    return page
```

Bây giờ:

```text
?page=2
```

→ `2`

```text
?page=abc
```

→ `1`

```text
?page=0
```

→ `1`

```text
(no page)
```

→ `1`

Đây mới gần với code production hơn.

---

# 17. `get()` với empty value

URL:

```text
https://example.com/search?q=
```

thì:

```python
value = url.query.get("q")
```

có thể cho:

```python
""
```

Không phải:

```python
None
```

Điều này rất quan trọng.

Phân biệt:

```text
key không tồn tại
        ↓
None
```

và:

```text
key tồn tại nhưng value rỗng
        ↓
""
```

Ví dụ:

```python
from yarl import URL


url = URL(
    "https://example.com/search?q="
)

value = url.query.get("q")

print(repr(value))
```

Kết quả:

```text
''
```

---

# 18. Vì vậy không nên viết tùy tiện

```python
value = url.query.get("q")

if value:
    ...
```

Vì:

```text
None
```

và:

```text
""
```

đều là falsy.

Nếu bạn cần phân biệt:

```python
value = url.query.get("q")

if value is None:
    print("parameter missing")
elif value == "":
    print("parameter exists but empty")
else:
    print("value:", value)
```

Đây là kỹ thuật rất hữu ích khi parse website không ổn định.

---

# 19. `get()` với default rỗng

Bạn có thể:

```python
value = url.query.get("q", "")
```

Nhưng lúc này:

```text
parameter missing
```

và:

```text
parameter exists but empty
```

đều có thể trở thành:

```text
""
```

Nếu application cần phân biệt hai trạng thái này thì **không nên dùng default `""`**.

---

# 20. Pattern Parser thực tế

Một parser query có thể viết:

```python
from yarl import URL


def parse_search_url(url: URL) -> dict:
    keyword = url.query.get("keyword")
    status = url.query.get("status")

    raw_page = url.query.get("page", "1")

    try:
        page = int(raw_page)
    except ValueError:
        page = 1

    return {
        "keyword": keyword,
        "status": status,
        "page": page,
    }
```

Test:

```python
url = URL(
    "https://example.com/novels"
    "?keyword=python"
    "&status=completed"
    "&page=3"
)

result = parse_search_url(url)

print(result)
```

Kết quả:

```python
{
    "keyword": "python",
    "status": "completed",
    "page": 3,
}
```

---

# 21. Nhưng Domain không nên phụ thuộc vào URL

Trong kiến trúc crawler của bạn, tốt hơn là:

```text
URL
 ↓
URL Parser
 ↓
SearchCriteria
 ↓
Application
 ↓
Use Case
```

Ví dụ:

```python
from dataclasses import dataclass


@dataclass
class SearchCriteria:
    keyword: str | None
    status: str | None
    page: int
```

Parser:

```python
from yarl import URL


def parse_search_url(
    url: URL,
) -> SearchCriteria:

    raw_page = url.query.get(
        "page",
        "1",
    )

    try:
        page = int(raw_page)
    except ValueError:
        page = 1

    return SearchCriteria(
        keyword=url.query.get("keyword"),
        status=url.query.get("status"),
        page=page,
    )
```

Đây là boundary rất đẹp:

```text
Infrastructure
     │
     │ yarl
     ▼
    URL
     │
     ▼
 Parser
     │
     ▼
SearchCriteria
     │
     ▼
 Domain/Application
```

Domain không cần biết:

```python
MultiDictProxy
```

là gì.

---

# 22. Một lỗi phổ biến

Đừng viết:

```python
page = url.query.get("page") or 1
```

rồi nghĩ rằng nó luôn cho integer đúng.

Ví dụ:

```python
page = "0"
```

là string `"0"`.

String `"0"` vẫn truthy:

```python
bool("0")
```

→ `True`.

Bạn vẫn nhận:

```python
"0"
```

chứ không phải:

```python
1
```

Do đó cần parse/validate rõ ràng:

```python
raw_page = url.query.get("page")

if raw_page is None:
    page = 1
else:
    page = int(raw_page)
```

---

# 23. Một lỗi khác

Không nên:

```python
page = int(
    url.query.get("page")
)
```

nếu `page` optional.

URL:

```text
https://example.com/novels
```

→:

```python
url.query.get("page")
```

là:

```python
None
```

và:

```python
int(None)
```

gây:

```text
TypeError
```

Tốt hơn:

```python
page = int(
    url.query.get("page", "1")
)
```

nếu bạn tin dữ liệu hợp lệ.

---

# 24. Complete example — Query Reader

Chạy nguyên file:

```python
from yarl import URL


def read_query(url: URL) -> None:
    print("URL:")
    print(url)

    print("\nKeyword:")
    print(repr(
        url.query.get("keyword")
    ))

    print("\nPage:")
    print(repr(
        url.query.get("page")
    ))

    print("\nPage with default:")
    print(
        url.query.get(
            "page",
            "1",
        )
    )

    print("\nMissing parameter:")
    print(repr(
        url.query.get("author")
    ))


def main():
    url = URL(
        "https://example.com/novels"
        "?keyword=python"
        "&page=3"
    )

    read_query(url)


if __name__ == "__main__":
    main()
```

Kết quả:

```text
URL:
https://example.com/novels?keyword=python&page=3

Keyword:
'python'

Page:
'3'

Page with default:
3

Missing parameter:
None
```

---

# 25. Complete example — Pagination Parser

Đây là ví dụ đáng nhớ nhất cho Novel Crawler:

```python
from yarl import URL


def parse_page(url: URL) -> int:
    raw_page = url.query.get("page")

    if raw_page is None:
        return 1

    try:
        page = int(raw_page)
    except ValueError:
        return 1

    if page < 1:
        return 1

    return page


def main():
    urls = [
        URL(
            "https://example.com/novels"
        ),
        URL(
            "https://example.com/novels?page=2"
        ),
        URL(
            "https://example.com/novels?page=10"
        ),
        URL(
            "https://example.com/novels?page=abc"
        ),
        URL(
            "https://example.com/novels?page=0"
        ),
    ]

    for url in urls:
        print(
            url,
            "→ page =",
            parse_page(url),
        )


if __name__ == "__main__":
    main()
```

Kết quả:

```text
https://example.com/novels → page = 1
https://example.com/novels?page=2 → page = 2
https://example.com/novels?page=10 → page = 10
https://example.com/novels?page=abc → page = 1
https://example.com/novels?page=0 → page = 1
```

Đây là một pattern có thể đưa thẳng vào Parser layer sau khi điều chỉnh theo domain.

---

# 26. `get()` và duplicate parameter — nhớ kỹ

Cho:

```text
?tag=python&tag=sqlite&tag=yarl
```

### Không dùng `get()` để lấy tất cả

```python
url.query.get("tag")
```

### Dùng:

```python
url.query.getall("tag")
```

Mental model:

```text
                 query
                   │
          ┌────────┴────────┐
          │                 │
        get()             getall()
          │                 │
          ▼                 ▼
     một value        tất cả values
```

---

# 27. 🧠 Tổng kết Buổi 27

## API cơ bản

```python
url.query.get("key")
```

→ lấy value.

---

## Key không tồn tại

```python
url.query.get("missing")
```

→ `None`.

---

## Default

```python
url.query.get("page", "1")
```

→ `"1"` nếu `page` không tồn tại.

---

## Query value luôn là string

```python
page = url.query.get("page")
```

→ `"3"`

Nếu cần:

```python
page = int(page)
```

---

## Empty value

```text
?q=
```

→ thường đọc thành:

```python
""
```

Trong khi:

```text
(no q)
```

→

```python
None
```

---

## Duplicate

```text
?tag=python&tag=sqlite
```

Không dùng:

```python
query.get("tag")
```

để lấy tất cả.

Dùng:

```python
query.getall("tag")
```

---

# 🎯 Pattern cần thuộc lòng cho Novel Crawler

```python
from yarl import URL


def parse_page(url: URL) -> int:
    raw = url.query.get("page", "1")

    try:
        page = int(raw)
    except ValueError:
        return 1

    return max(page, 1)
```

và:

```python
keyword = url.query.get("keyword")

status = url.query.get("status")

tags = url.query.getall("tag")
```

Đây là ba pattern sẽ xuất hiện rất nhiều khi bạn xây Parser:

```text
optional single value
        ↓
query.get()

optional numeric value
        ↓
query.get() + conversion + validation

duplicate values
        ↓
query.getall()
```

---

## Bài tiếp theo — Buổi 28

```text
### Buổi 28 — query.getall()
```

Chúng ta sẽ đi sâu vào **duplicate parameters**:

```text
?tag=python&tag=sqlite&tag=yarl
```

và học cách:

* lấy toàn bộ values;
* xử lý key không tồn tại;
* phân biệt `get()` và `getall()`;
* xử lý `MultiDictProxy`;
* chuyển query thành `list[str]`;
* xây `SearchCriteria` có `genres/tags`;
* và đặc biệt là **parse URL tìm kiếm truyện có nhiều thể loại** theo kiểu phù hợp với kiến trúc DDD của Novel Crawler.
