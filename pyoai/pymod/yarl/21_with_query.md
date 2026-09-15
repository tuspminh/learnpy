# Phần III — Query String chuyên sâu

# Buổi 21 — `URL.with_query()`

Ở các buổi trước chúng ta đã **biết `with_query()` tồn tại**. Từ hôm nay, chúng ta sẽ đi sâu vào query string.

Mục tiêu của Buổi 21:

```text
URL
 │
 ├── đọc query
 │
 ├── thay thế query
 │
 ├── xóa query
 │
 └── hiểu chính xác with_query() hoạt động thế nào
```

Đây là phần rất quan trọng đối với **Novel Crawler**, vì pagination, search, filter, sorting... thường nằm trong query string.

---

# 1. Query string là gì?

Ví dụ:

```text
https://example.com/search?keyword=python&page=2
```

Phần:

```text
?keyword=python&page=2
```

là **query string**.

Có hai parameter:

```text
keyword = python
page    = 2
```

Trong `yarl`:

```python
from yarl import URL

url = URL(
    "https://example.com/search"
    "?keyword=python&page=2"
)

print(url.query)
print(url.query_string)
```

Ta sẽ học kỹ hai thuộc tính này ở Buổi 25–26.

Hôm nay tập trung vào:

```python
url.with_query(...)
```

---

# 2. `with_query()` dùng để làm gì?

Cú pháp:

```python
new_url = url.with_query(...)
```

Nó tạo ra **một URL mới với query mới**.

Ví dụ:

```python
from yarl import URL

url = URL(
    "https://example.com/search"
)

new_url = url.with_query(
    keyword="python",
    page=2,
)

print(new_url)
```

Kết quả:

```text
https://example.com/search?keyword=python&page=2
```

---

# 3. `URL` không bị thay đổi

Đây là điểm rất quan trọng.

```python
from yarl import URL

url = URL(
    "https://example.com/search"
)

new_url = url.with_query(
    keyword="python",
    page=2,
)

print("Original:", url)
print("New     :", new_url)
```

Kết quả:

```text
Original: https://example.com/search
New     : https://example.com/search?keyword=python&page=2
```

`url` vẫn giữ nguyên.

Có thể hình dung:

```text
url
 │
 │ with_query(...)
 ↓
new_url
```

Không phải:

```text
url ← bị sửa
```

---

# 4. `with_query()` thay thế query hiện tại

Đây là điều cần nhớ nhất của bài hôm nay.

Giả sử:

```python
from yarl import URL

url = URL(
    "https://example.com/search"
    "?keyword=python&page=1"
)

print(url)
```

Có query:

```text
keyword=python
page=1
```

Bây giờ:

```python
new_url = url.with_query(
    keyword="sqlite"
)

print(new_url)
```

Kết quả:

```text
https://example.com/search?keyword=sqlite
```

**Không phải:**

```text
https://example.com/search?keyword=python&page=1&keyword=sqlite
```

`with_query()` ở đây **thay thế toàn bộ query cũ**.

---

# 5. Ví dụ pagination

Đây là use case rất thực tế trong crawler.

```python
from yarl import URL

url = URL(
    "https://example.com/novels"
    "?page=1"
)

page_2 = url.with_query(
    page=2
)

page_3 = url.with_query(
    page=3
)

print(page_2)
print(page_3)
```

Kết quả:

```text
https://example.com/novels?page=2
https://example.com/novels?page=3
```

URL ban đầu:

```text
https://example.com/novels?page=1
```

không thay đổi.

---

# 6. Dictionary → query

Đây là cách rất phổ biến.

```python
from yarl import URL

params = {
    "keyword": "python",
    "page": 2,
    "sort": "newest",
}

url = URL(
    "https://example.com/search"
).with_query(params)

print(url)
```

Kết quả:

```text
https://example.com/search?keyword=python&page=2&sort=newest
```

Cách này rất phù hợp với crawler.

Ví dụ:

```python
params = {
    "keyword": keyword,
    "page": page,
}
```

sau đó:

```python
url = base_url.with_query(params)
```

---

# 7. Keyword arguments

Bạn cũng có thể truyền trực tiếp:

```python
from yarl import URL

url = URL(
    "https://example.com/search"
).with_query(
    keyword="python",
    page=2,
    sort="newest",
)

print(url)
```

Kết quả:

```text
https://example.com/search?keyword=python&page=2&sort=newest
```

Hai cách:

```python
url.with_query(
    {
        "keyword": "python",
        "page": 2,
    }
)
```

và:

```python
url.with_query(
    keyword="python",
    page=2,
)
```

đều rất hữu ích.

---

# 8. Giá trị số sẽ được chuyển thành chuỗi URL

Ví dụ:

```python
from yarl import URL

url = URL(
    "https://example.com/novels"
).with_query(
    page=10,
    limit=20,
)

print(url)
```

Kết quả:

```text
https://example.com/novels?page=10&limit=20
```

Bạn truyền:

```python
page=10
```

nhưng trên URL:

```text
page=10
```

là representation của query parameter.

Khi đọc query bằng `yarl`, bạn cần nhớ rằng query parameters về bản chất được biểu diễn dưới dạng text.

---

# 9. Boolean

Ví dụ:

```python
from yarl import URL

url = URL(
    "https://example.com/search"
).with_query(
    keyword="python",
    active=True,
)

print(url)
```

Bạn có thể thấy:

```text
https://example.com/search?keyword=python&active=true
```

Điểm quan trọng không phải là `True` trong Python mà là:

```text
URL representation
```

Do đó khi xây crawler, nếu website yêu cầu:

```text
active=1
```

thì đừng mặc định rằng:

```python
active=True
```

sẽ tạo đúng format mà website mong muốn.

Hãy chủ động chuyển đổi:

```python
active = 1 if is_active else 0
```

---

# 10. `None` — cần đặc biệt chú ý

Ví dụ:

```python
from yarl import URL

url = URL(
    "https://example.com/search"
).with_query(
    keyword="python",
    page=2,
    author=None,
)

print(url)
```

Trong thực tế xây URL builder, bạn thường **không muốn** các giá trị `None` xuất hiện như một parameter hợp lệ.

Một cách an toàn là lọc trước:

```python
from yarl import URL

params = {
    "keyword": "python",
    "page": 2,
    "author": None,
}

params = {
    key: value
    for key, value in params.items()
    if value is not None
}

url = URL(
    "https://example.com/search"
).with_query(params)

print(url)
```

Kết quả mong muốn:

```text
https://example.com/search?keyword=python&page=2
```

Đây là pattern rất hữu ích khi sau này chúng ta xây:

```text
NovelSearchURLBuilder
```

---

# 11. Xóa toàn bộ query bằng `None`

Đây là một tính năng quan trọng của:

```python
with_query(None)
```

Ví dụ:

```python
from yarl import URL

url = URL(
    "https://example.com/search"
    "?keyword=python&page=2"
)

clean_url = url.with_query(None)

print(url)
print(clean_url)
```

Kết quả:

```text
https://example.com/search?keyword=python&page=2
https://example.com/search
```

Như vậy:

```python
url.with_query(None)
```

có thể hiểu là:

```text
Remove query
```

---

# 12. Đây là một pattern rất hữu ích

Ví dụ URL:

```text
https://example.com/novel/python?page=2&sort=newest
```

Muốn lấy URL không có query:

```python
clean = url.with_query(None)
```

Kết quả:

```text
https://example.com/novel/python
```

Trong crawler có thể dùng cho:

```text
Canonical URL
Deduplication
URL normalization
Cache key
```

Nhưng **không phải lúc nào cũng được xóa query**.

Ví dụ:

```text
?page=2
?id=123
?chapter=10
```

có thể mang ý nghĩa thực sự của resource.

---

# 13. `with_query()` không thay đổi Path

Ví dụ:

```python
from yarl import URL

url = URL(
    "https://example.com/novels/python"
)

new_url = url.with_query(
    page=2
)

print(new_url.path)
print(new_url.query)
```

Kết quả:

```text
/novels/python
<QueryDict>
```

Path vẫn:

```text
/novels/python
```

Chỉ query thay đổi.

---

# 14. `with_query()` cũng giữ Fragment

Ví dụ:

```python
from yarl import URL

url = URL(
    "https://example.com/chapter/10"
    "#content"
)

new_url = url.with_query(
    page=2
)

print(new_url)
```

Kết quả:

```text
https://example.com/chapter/10?page=2#content
```

Ta có:

```text
Path     → giữ nguyên
Query    → thay đổi
Fragment → giữ nguyên
```

---

# 15. Complete example

Hãy chạy nguyên chương trình này:

```python
from yarl import URL


def main():
    url = URL(
        "https://example.com/novels"
        "?page=1"
        "#content"
    )

    print("Original:")
    print(url)

    print("\nChange query:")

    page_2 = url.with_query(
        page=2
    )

    print(page_2)

    print("\nMultiple parameters:")

    search_url = url.with_query(
        keyword="python",
        page=2,
        sort="newest",
    )

    print(search_url)

    print("\nRemove query:")

    clean_url = search_url.with_query(None)

    print(clean_url)

    print("\nOriginal remains unchanged:")

    print(url)


if __name__ == "__main__":
    main()
```

Kết quả gần như:

```text
Original:
https://example.com/novels?page=1#content

Change query:
https://example.com/novels?page=2#content

Multiple parameters:
https://example.com/novels?keyword=python&page=2&sort=newest#content

Remove query:
https://example.com/novels#content

Original remains unchanged:
https://example.com/novels?page=1#content
```

---

# 16. Một lỗi thiết kế thường gặp

Giả sử crawler có:

```python
base_url = URL(
    "https://example.com/search"
)
```

Một developer viết:

```python
url = base_url

for page in range(1, 6):
    url = url.with_query(page=page)
    print(url)
```

Code này vẫn chạy được.

Nhưng về mặt thiết kế, tốt hơn là:

```python
base_url = URL(
    "https://example.com/search"
)

for page in range(1, 6):
    page_url = base_url.with_query(
        page=page
    )

    print(page_url)
```

Bởi vì:

```text
base_url
    │
    ├── page 1
    ├── page 2
    ├── page 3
    ├── page 4
    └── page 5
```

Rõ ràng hơn.

---

# 17. Xây Pagination URL Builder

Đây là pattern chúng ta sẽ sử dụng nhiều trong Novel Crawler.

```python
from yarl import URL


class PaginationURLBuilder:

    def __init__(self, base_url: URL):
        self.base_url = base_url

    def build(self, page: int) -> URL:
        return self.base_url.with_query(
            page=page
        )


def main():
    base_url = URL(
        "https://example.com/novels"
    )

    builder = PaginationURLBuilder(
        base_url
    )

    for page in range(1, 6):
        url = builder.build(page)

        print(url)


if __name__ == "__main__":
    main()
```

Output:

```text
https://example.com/novels?page=1
https://example.com/novels?page=2
https://example.com/novels?page=3
https://example.com/novels?page=4
https://example.com/novels?page=5
```

---

# 18. Nhưng website có thể có query khác

Ví dụ website:

```text
/search?keyword=python&page=2&sort=newest
```

Ta không thể chỉ:

```python
base_url.with_query(page=2)
```

nếu `base_url` đã chứa:

```text
keyword
sort
```

vì `with_query()` **thay thế toàn bộ query**.

Ví dụ:

```python
from yarl import URL

url = URL(
    "https://example.com/search"
    "?keyword=python"
    "&sort=newest"
    "&page=1"
)

new_url = url.with_query(
    page=2
)

print(new_url)
```

Kết quả:

```text
https://example.com/search?page=2
```

`keyword` và `sort` đã biến mất.

---

# 19. Muốn thay đổi một parameter thì phải giữ các parameter khác

Ví dụ:

```text
https://example.com/search?keyword=python&sort=newest&page=1
```

Muốn:

```text
page=2
```

nhưng giữ:

```text
keyword=python
sort=newest
```

Ta có thể làm:

```python
from yarl import URL

url = URL(
    "https://example.com/search"
    "?keyword=python"
    "&sort=newest"
    "&page=1"
)

params = dict(url.query)

params["page"] = 2

new_url = url.with_query(params)

print(new_url)
```

Kết quả:

```text
https://example.com/search?keyword=python&sort=newest&page=2
```

Đây là một pattern cực kỳ quan trọng.

---

# 20. Nhưng `dict(url.query)` có một vấn đề

Chúng ta sẽ học rất kỹ ở Buổi 24.

Giả sử:

```text
https://example.com/search?tag=python&tag=sqlite
```

Có:

```text
tag=python
tag=sqlite
```

Nếu làm:

```python
params = dict(url.query)
```

thì duplicate parameter có thể không được biểu diễn theo cách bạn mong muốn.

Vì vậy:

> **Không nên dùng `dict(url.query)` một cách máy móc khi URL có duplicate query parameters.**

Đây chính là lý do roadmap có:

```text
24. Duplicate query parameters
```

---

# 21. Query builder cho Novel Crawler

Hãy xây một ví dụ thực tế hơn.

```python
from dataclasses import dataclass
from yarl import URL


@dataclass(frozen=True)
class SearchCriteria:
    keyword: str | None = None
    author: str | None = None
    page: int = 1
    sort: str | None = None


class NovelSearchURLBuilder:

    def __init__(self, base_url: URL):
        self.base_url = base_url

    def build(self, criteria: SearchCriteria) -> URL:
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
    builder = NovelSearchURLBuilder(
        URL("https://example.com/search")
    )

    criteria = SearchCriteria(
        keyword="python",
        author="Alice",
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
https://example.com/search?keyword=python&author=Alice&page=2&sort=newest
```

Đây là cách chúng ta bắt đầu đưa `yarl` vào kiến trúc crawler.

---

# 22. Tại sao không nối string?

Không nên:

```python
url = (
    "https://example.com/search"
    "?keyword=" + keyword
    "&page=" + str(page)
)
```

Vì sẽ nhanh chóng gặp vấn đề:

```text
Unicode
spaces
&
?
=
/
encoding
duplicate parameters
```

Ví dụ:

```python
keyword = "python & sqlite"
```

Nếu tự nối string, bạn phải tự xử lý encoding.

Với `yarl`:

```python
from yarl import URL

url = URL(
    "https://example.com/search"
).with_query(
    keyword="python & sqlite"
)

print(url)
```

`yarl` đảm nhiệm việc encode URL đúng cách.

---

# 23. Một nguyên tắc kiến trúc rất quan trọng

Trong Novel Crawler:

```text
Domain
    │
    │ SearchCriteria
    ↓
Application
    │
    │ query parameters
    ↓
URL Builder
    │
    │ yarl.URL
    ↓
Fetcher
    │
    ↓
httpx
```

Không nên để domain tự nối:

```python
"https://..."
```

Domain nên biểu diễn **ý nghĩa**:

```python
SearchCriteria(
    keyword="python",
    page=2,
)
```

URL Builder chịu trách nhiệm biến nó thành:

```text
https://example.com/search?keyword=python&page=2
```

---

# 24. Tóm tắt `with_query()`

### Thay query

```python
new_url = url.with_query(
    keyword="python",
    page=2,
)
```

### Dictionary

```python
params = {
    "keyword": "python",
    "page": 2,
}

new_url = url.with_query(params)
```

### Xóa query

```python
new_url = url.with_query(None)
```

### Immutable

```python
new_url = url.with_query(...)
```

không sửa `url`.

### Quan trọng nhất

```text
with_query()
        ↓
THAY THẾ toàn bộ query hiện tại
```

Không phải:

```text
append query
```

---

# 🧠 Bài tập Buổi 21

## Bài 1

Tạo:

```python
url = URL(
    "https://example.com/search"
)
```

dùng `with_query()` tạo:

```text
https://example.com/search?keyword=python&page=2
```

---

## Bài 2

Cho:

```python
url = URL(
    "https://example.com/search"
    "?keyword=python&page=1"
)
```

Dùng `with_query()` để tạo:

```text
https://example.com/search?keyword=sqlite
```

và quan sát `page=1` biến mất.

---

## Bài 3

Cho:

```text
https://example.com/search?keyword=python&page=1&sort=newest
```

Hãy tạo:

```text
https://example.com/search?keyword=python&page=2&sort=newest
```

mà không làm mất:

```text
keyword
sort
```

---

## Bài 4 — thực chiến crawler

Viết:

```python
class PaginationURLBuilder:
    ...
```

với:

```python
builder = PaginationURLBuilder(
    URL("https://example.com/novels")
)
```

và:

```python
builder.build(1)
builder.build(2)
builder.build(3)
```

phải tạo được URL pagination tương ứng.

---

## Bài 5 — Search URL Builder

Tạo:

```python
@dataclass(frozen=True)
class SearchCriteria:
    keyword: str | None
    page: int
    sort: str | None
```

sau đó:

```python
criteria = SearchCriteria(
    keyword="python",
    page=2,
    sort="newest",
)
```

và tạo URL:

```text
https://example.com/search?keyword=python&page=2&sort=newest
```

Đồng thời nếu:

```python
sort=None
```

thì **không đưa `sort` vào URL**.

---

### Tiếp theo — Buổi 22

```text
22. Dictionary → Query
```

Buổi 22 sẽ đi sâu riêng vào **Dictionary → query**, thứ tự parameter, giá trị `None`, kiểu dữ liệu, encoding và cách thiết kế một `QueryParams`/builder sạch cho Novel Crawler.
