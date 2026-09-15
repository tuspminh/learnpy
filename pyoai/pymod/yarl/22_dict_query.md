# Buổi 22 — Dictionary → Query với `yarl`

Ở Buổi 21, chúng ta đã biết:

```python
url.with_query(...)
```

Hôm nay tập trung vào một trường hợp rất quan trọng:

> **Biến một `dict` Python thành query string của URL.**

Đây là cách chúng ta sẽ thường xuyên xây URL cho **search, pagination, filter, sorting** trong Novel Crawler.

---

# 1. Dictionary cơ bản → Query

Ví dụ:

```python
from yarl import URL


params = {
    "keyword": "python",
    "page": 2,
    "sort": "newest",
}

url = URL("https://example.com/search").with_query(params)

print(url)
```

Kết quả:

```text
https://example.com/search?keyword=python&page=2&sort=newest
```

Mapping:

```text
Python dict
        ↓
{
    "keyword": "python",
    "page": 2,
    "sort": "newest",
}
        ↓
URL query
        ↓
?keyword=python&page=2&sort=newest
```

---

# 2. Dictionary key trở thành parameter name

Ví dụ:

```python
params = {
    "page": 3,
    "limit": 20,
    "category": "novel",
}
```

thì:

```python
url = URL(
    "https://example.com/novels"
).with_query(params)
```

tạo:

```text
https://example.com/novels?page=3&limit=20&category=novel
```

Có thể nhớ:

```text
dict key
   ↓
query parameter name

dict value
   ↓
query parameter value
```

---

# 3. Integer

```python
from yarl import URL

params = {
    "page": 10,
    "limit": 50,
}

url = URL(
    "https://example.com/novels"
).with_query(params)

print(url)
```

Kết quả:

```text
https://example.com/novels?page=10&limit=50
```

Trong Python:

```python
type(params["page"])
```

là:

```text
int
```

Nhưng trong URL:

```text
page=10
```

là textual representation.

---

# 4. Float

Bạn cũng có thể truyền số thực:

```python
from yarl import URL

params = {
    "rating": 4.5,
    "score": 9.25,
}

url = URL(
    "https://example.com/search"
).with_query(params)

print(url)
```

Kết quả dạng:

```text
https://example.com/search?rating=4.5&score=9.25
```

Tuy nhiên, với crawler, chỉ nên dùng kiểu này khi website thực sự nhận format đó.

---

# 5. String

Đây là trường hợp phổ biến nhất:

```python
params = {
    "keyword": "python",
    "author": "Guido",
}
```

```python
url = URL(
    "https://example.com/search"
).with_query(params)
```

Kết quả:

```text
https://example.com/search?keyword=python&author=Guido
```

---

# 6. Unicode

Đây là một lý do rất lớn để dùng `yarl`.

Ví dụ:

```python
from yarl import URL

params = {
    "keyword": "lập trình Python",
}

url = URL(
    "https://example.com/search"
).with_query(params)

print(url)
```

Bạn sẽ thấy URL được encode phù hợp.

Có thể dùng:

```python
print(url.human_repr())
```

để xem representation dễ đọc hơn.

Ví dụ về mặt logic:

```text
keyword = "lập trình Python"
```

vẫn là dữ liệu query ban đầu, dù URL cần encoding khi serialize.

---

# 7. Ký tự đặc biệt

Ví dụ:

```python
from yarl import URL

params = {
    "keyword": "python & sqlite",
}

url = URL(
    "https://example.com/search"
).with_query(params)

print(url)
```

Không nên tự làm:

```python
url = (
    "https://example.com/search"
    "?keyword=" + params["keyword"]
)
```

vì:

```text
&
?
=
space
unicode
%
```

đều có thể gây vấn đề khi tự xử lý.

Hãy để `yarl` đảm nhiệm việc serialize query.

---

# 8. Dictionary rỗng

```python
from yarl import URL

url = URL(
    "https://example.com/search"
).with_query({})

print(url)
```

Kết quả:

```text
https://example.com/search
```

Không có:

```text
?
```

---

# 9. `None` — không nên đưa trực tiếp một cách tùy tiện

Trong application, bạn thường có:

```python
params = {
    "keyword": "python",
    "author": None,
    "page": 2,
}
```

Ý nghĩa có thể là:

```text
keyword → có
author  → không filter
page    → có
```

Thường ta muốn:

```text
?keyword=python&page=2
```

chứ không muốn `author` xuất hiện.

Pattern nên dùng:

```python
params = {
    "keyword": "python",
    "author": None,
    "page": 2,
}

params = {
    key: value
    for key, value in params.items()
    if value is not None
}
```

Sau đó:

```python
url = URL(
    "https://example.com/search"
).with_query(params)

print(url)
```

---

# 10. Viết thành helper

Thay vì lặp lại:

```python
params = {
    key: value
    for key, value in params.items()
    if value is not None
}
```

ta có thể tạo:

```python
def remove_none(
    params: dict
) -> dict:
    return {
        key: value
        for key, value in params.items()
        if value is not None
    }
```

Dùng:

```python
from yarl import URL


def remove_none(params: dict) -> dict:
    return {
        key: value
        for key, value in params.items()
        if value is not None
    }


params = {
    "keyword": "python",
    "author": None,
    "page": 2,
}

params = remove_none(params)

url = URL(
    "https://example.com/search"
).with_query(params)

print(url)
```

Kết quả:

```text
https://example.com/search?keyword=python&page=2
```

---

# 11. Dictionary giữ thứ tự

Python hiện đại giữ insertion order của `dict`.

Ví dụ:

```python
params = {
    "keyword": "python",
    "page": 2,
    "sort": "newest",
}
```

thì khi serialize thường sẽ giữ thứ tự:

```text
keyword
page
sort
```

tạo:

```text
?keyword=python&page=2&sort=newest
```

Điều này rất tiện khi debug.

Tuy nhiên:

> Không nên xem thứ tự query parameter là một phần của semantic URL nếu server không yêu cầu.

Hai URL:

```text
?id=10&page=2
```

và:

```text
?page=2&id=10
```

thường mang cùng dữ liệu query.

---

# 12. Query dictionary không nên được dùng cho duplicate key

Đây là điểm chúng ta sẽ đào sâu ở Buổi 24.

Một `dict` thông thường:

```python
params = {
    "tag": "python",
    "tag": "sqlite",
}
```

không thể chứa hai key giống nhau.

Python thực chất chỉ còn:

```python
{
    "tag": "sqlite"
}
```

Do đó dictionary phù hợp với:

```text
page=2
keyword=python
sort=newest
```

nhưng không phù hợp để biểu diễn trực tiếp:

```text
tag=python&tag=sqlite
```

Khi cần duplicate parameters, chúng ta sẽ dùng cấu trúc khác.

---

# 13. Dictionary với list

Một trường hợp thú vị:

```python
from yarl import URL

params = {
    "tag": ["python", "sqlite"]
}

url = URL(
    "https://example.com/search"
).with_query(params)

print(url)
```

Tùy phiên bản/API serialization cụ thể, list value có thể được serialize thành nhiều giá trị của cùng parameter.

Đây chính là chủ đề chúng ta sẽ nghiên cứu kỹ ở:

```text
Buổi 23 — List/Tuple → query
Buổi 24 — Duplicate query parameters
```

Vì vậy ở Buổi 22, nguyên tắc đơn giản là:

> **Dictionary phù hợp nhất cho query dạng key → một value.**

---

# 14. Dictionary từ object

Trong ứng dụng thực tế, query thường không bắt đầu từ một `dict`.

Ví dụ ta có:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class SearchCriteria:
    keyword: str | None
    page: int
    sort: str | None
```

Sử dụng:

```python
criteria = SearchCriteria(
    keyword="python",
    page=2,
    sort="newest",
)
```

Ta có thể chuyển thành dictionary:

```python
params = {
    "keyword": criteria.keyword,
    "page": criteria.page,
    "sort": criteria.sort,
}
```

rồi:

```python
url = URL(
    "https://example.com/search"
).with_query(params)
```

---

# 15. Complete Search Builder

Đây là ví dụ nên ghi nhớ.

```python
from dataclasses import dataclass
from yarl import URL


@dataclass(frozen=True)
class SearchCriteria:
    keyword: str | None = None
    author: str | None = None
    page: int = 1
    sort: str | None = None


class SearchURLBuilder:

    def __init__(self, base_url: URL):
        self.base_url = base_url

    def build(
        self,
        criteria: SearchCriteria,
    ) -> URL:

        params = {
            "keyword": criteria.keyword,
            "author": criteria.author,
            "page": criteria.page,
            "sort": criteria.sort,
        }

        params = {
            key: value
            for key, value in params.items()
            if value is not None
        }

        return self.base_url.with_query(params)


def main():
    builder = SearchURLBuilder(
        URL("https://example.com/search")
    )

    criteria = SearchCriteria(
        keyword="python",
        author="Guido",
        page=2,
        sort="newest",
    )

    url = builder.build(criteria)

    print(url)


if __name__ == "__main__":
    main()
```

Kết quả:

```text
https://example.com/search?keyword=python&author=Guido&page=2&sort=newest
```

---

# 16. Khi không có `author`

```python
criteria = SearchCriteria(
    keyword="python",
    author=None,
    page=2,
    sort="newest",
)
```

Builder vẫn tạo:

```text
https://example.com/search?keyword=python&page=2&sort=newest
```

Đây là cách rất sạch.

Domain object:

```text
SearchCriteria
```

không cần biết:

```text
?
&
URL encoding
```

URL Builder chịu trách nhiệm chuyển đổi.

---

# 17. Dictionary → Query trong kiến trúc crawler

Có thể hình dung:

```text
┌──────────────────────┐
│ SearchCriteria       │
│                      │
│ keyword = python     │
│ page = 2             │
│ sort = newest        │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│ SearchURLBuilder     │
└──────────┬───────────┘
           │
           ↓
       dict params
           │
           ↓
┌──────────────────────┐
│ yarl.URL.with_query  │
└──────────┬───────────┘
           │
           ↓
https://example.com/search
?keyword=python
&page=2
&sort=newest
```

Đây là cách tách trách nhiệm tốt hơn việc:

```python
criteria.to_url()
```

trong Domain.

---

# 18. Đừng sửa dictionary gốc nếu không cần

Ví dụ:

```python
params = {
    "keyword": "python",
    "page": 2,
    "author": None,
}
```

Không nên vô tình mutate:

```python
for key in list(params):
    if params[key] is None:
        del params[key]
```

nếu dictionary còn được sử dụng ở nơi khác.

Tốt hơn:

```python
clean_params = {
    key: value
    for key, value in params.items()
    if value is not None
}
```

Ta có:

```text
params
   ↓
giữ nguyên

clean_params
   ↓
dictionary mới
```

Điều này phù hợp với tư duy immutable mà chúng ta đã học với `yarl.URL`.

---

# 19. Một helper hoàn chỉnh hơn

Có thể viết:

```python
from typing import Any


def build_query(
    params: dict[str, Any],
) -> dict[str, Any]:

    return {
        key: value
        for key, value in params.items()
        if value is not None
    }
```

Sau đó:

```python
from yarl import URL


def build_query(
    params: dict[str, object],
) -> dict[str, object]:

    return {
        key: value
        for key, value in params.items()
        if value is not None
    }


params = {
    "keyword": "python",
    "page": 2,
    "sort": None,
}

query = build_query(params)

url = URL(
    "https://example.com/search"
).with_query(query)

print(url)
```

Kết quả:

```text
https://example.com/search?keyword=python&page=2
```

---

# 20. Dictionary và `with_query()` — mental model

Hãy nhớ mô hình:

```text
dict
 │
 │ {
 │   "keyword": "python",
 │   "page": 2
 │ }
 ↓
with_query()
 ↓
URL
 │
 ↓
https://example.com/search?keyword=python&page=2
```

Không phải:

```text
dict
 ↓
tự nối string
```

---

# 21. Một ví dụ sát với Novel Crawler

Giả sử trang truyện có URL:

```text
https://example.com/truyen
```

API listing yêu cầu:

```text
?page=2
&sort=newest
&status=completed
```

Ta viết:

```python
from yarl import URL


params = {
    "page": 2,
    "sort": "newest",
    "status": "completed",
}

url = URL(
    "https://example.com/truyen"
).with_query(params)

print(url)
```

Kết quả:

```text
https://example.com/truyen?page=2&sort=newest&status=completed
```

Nếu người dùng không chọn status:

```python
params = {
    "page": 2,
    "sort": "newest",
    "status": None,
}
```

lọc:

```python
params = {
    key: value
    for key, value in params.items()
    if value is not None
}
```

thành:

```text
https://example.com/truyen?page=2&sort=newest
```

Đây chính là pattern chúng ta sẽ gặp khi xây:

```text
ListingParser
Novel Parser
Pagination
URL Builder
Fetcher
```

---

# 22. Một điều rất quan trọng: Query ≠ JSON

Đừng nhầm:

```python
params = {
    "page": 2,
    "limit": 20,
}
```

với JSON:

```json
{
    "page": 2,
    "limit": 20
}
```

Query URL:

```text
?page=2&limit=20
```

là một **serialization khác**.

Trong HTTP:

```text
URL Query
    ↓
?page=2&limit=20
```

khác với:

```text
JSON Body
    ↓
{"page": 2, "limit": 20}
```

Trong `httpx`:

```python
client.get(
    url,
    params=params,
)
```

là một cách rất tự nhiên để truyền query parameters.

---

# 23. `yarl` và `httpx`

Sau này trong Fetcher của Novel Crawler, bạn có thể có:

```python
from yarl import URL
import httpx


url = URL(
    "https://example.com/search"
)

params = {
    "keyword": "python",
    "page": 2,
}

with httpx.Client() as client:
    response = client.get(
        str(url),
        params=params,
    )
```

Ở đây có hai tầng:

```text
params
   ↓
httpx
   ↓
HTTP request
```

hoặc:

```text
params
   ↓
yarl.with_query()
   ↓
URL hoàn chỉnh
   ↓
httpx
```

Không nhất thiết phải luôn tạo query bằng `yarl` nếu HTTP client đã nhận `params`.

Chúng ta sẽ phân biệt rõ trách nhiệm này khi học:

```text
Buổi 43 — yarl + httpx
```

---

# 24. Quy tắc thiết kế nên nhớ

### Trường hợp đơn giản

```python
params = {
    "page": 2,
    "sort": "newest",
}

url = base_url.with_query(params)
```

### Có optional parameters

```python
params = {
    "keyword": keyword,
    "author": author,
    "page": page,
}

params = {
    k: v
    for k, v in params.items()
    if v is not None
}
```

### Có duplicate parameters

Không dùng `dict` đơn thuần.

Học:

```text
Buổi 23
Buổi 24
```

### Query cần encoding

Để `yarl` xử lý, không tự nối string.

---

# 25. Tổng kết Buổi 22

Điểm quan trọng nhất:

```python
params = {
    "keyword": "python",
    "page": 2,
}

url = URL(
    "https://example.com/search"
).with_query(params)
```

→

```text
https://example.com/search?keyword=python&page=2
```

### Mental model

```text
Python dict
    ↓
key → query parameter name
value → query parameter value
    ↓
URL.with_query()
    ↓
query string
```

Và:

```text
dict
```

phù hợp nhất khi mỗi parameter có **một value**.

---

# 🧪 Bài tập Buổi 22

### Bài 1

Tạo:

```python
params = {
    "keyword": "python",
    "page": 3,
    "sort": "newest",
}
```

và tạo:

```text
https://example.com/search?keyword=python&page=3&sort=newest
```

---

### Bài 2

Cho:

```python
params = {
    "keyword": "python",
    "author": None,
    "page": 2,
    "sort": None,
}
```

Viết code để tạo URL **không chứa `None`**.

Kết quả:

```text
https://example.com/search?keyword=python&page=2
```

---

### Bài 3

Cho:

```python
params = {
    "keyword": "lập trình Python",
    "page": 2,
}
```

Tạo URL và kiểm tra:

```python
print(url)
print(url.human_repr())
```

Quan sát sự khác nhau giữa URL serialized và URL dễ đọc.

---

### Bài 4 — Novel Crawler

Tạo:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ListingCriteria:
    page: int = 1
    sort: str | None = None
    status: str | None = None
```

và:

```python
class ListingURLBuilder:
    ...
```

Builder phải tạo được:

```text
https://example.com/truyen?page=2&sort=newest&status=completed
```

và nếu:

```python
ListingCriteria(
    page=2,
    sort=None,
    status=None,
)
```

thì:

```text
https://example.com/truyen?page=2
```

---

### Bài 5 — câu hỏi quan trọng

Giải thích tại sao cách này **không phù hợp** cho:

```text
?tag=python&tag=sqlite&tag=yarl
```

```python
params = {
    "tag": "python",
    "tag": "sqlite",
    "tag": "yarl",
}
```

Đây sẽ là cầu nối trực tiếp sang **Buổi 23 — List/Tuple → Query**, rồi **Buổi 24 — Duplicate Query Parameters**.
