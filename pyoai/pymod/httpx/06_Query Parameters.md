# Buổi 6 — Query Parameters Deep Dive

Ở Buổi 5, chúng ta đã học Timeout. Hôm nay đi sâu vào `params=`.

Đây là phần tưởng đơn giản nhưng cực kỳ quan trọng khi làm:

* REST API
* Web crawler
* Search engine
* Pagination
* Filtering
* Sorting
* API client

Mục tiêu cuối buổi:

```text
Python data
    ↓
params=
    ↓
Query String
    ↓
URL
```

---

# 1. Query Parameter là gì?

Ví dụ URL:

```text
https://example.com/search?q=python&page=2
```

Phần:

```text
?q=python&page=2
```

là **query string**.

Trong đó:

```text
q=python
page=2
```

là các query parameters.

Mô hình:

```text
https://example.com/search?q=python&page=2
        │             │
        │             └── Query
        │
        └── Path
```

---

# 2. HTTPX dùng `params=`

Thay vì tự nối URL:

```python
url = (
    "https://example.com/search"
    "?q=python&page=2"
)
```

hãy dùng:

```python
import httpx

response = httpx.get(
    "https://example.com/search",
    params={
        "q": "python",
        "page": 2,
    },
)
```

HTTPX sẽ xây dựng URL.

Kiểm tra:

```python
print(response.url)
```

---

# 3. Vì sao không nên tự nối URL?

Cách này:

```python
url = f"https://example.com/search?q={keyword}"
```

có nhiều vấn đề.

Ví dụ:

```python
keyword = "python httpx"
```

URL cần encode thành dạng phù hợp.

Hoặc:

```python
keyword = "python&httpx"
```

`&` có ý nghĩa đặc biệt trong query string.

HTTPX xử lý việc encoding cho bạn:

```python
params = {
    "q": keyword,
}
```

Đây là cách an toàn và rõ ràng hơn.

---

# 4. Một parameter

```python
response = httpx.get(
    url,
    params={
        "page": 1,
    },
)
```

URL:

```text
?page=1
```

---

# 5. Nhiều parameters

```python
params = {
    "q": "python",
    "page": 2,
    "limit": 20,
}
```

Request:

```python
response = httpx.get(
    url,
    params=params,
)
```

URL sẽ có dạng:

```text
?q=python&page=2&limit=20
```

---

# 6. Giá trị số

Bạn không cần tự chuyển:

```python
page = str(2)
```

HTTPX có thể xử lý:

```python
params = {
    "page": 2,
    "limit": 20,
}
```

Tư duy:

```text
Python
int
 ↓
HTTPX
 ↓
URL encoding
 ↓
query string
```

---

# 7. Boolean

Ví dụ:

```python
params = {
    "active": True,
}
```

HTTPX sẽ encode giá trị theo quy tắc của query parameter.

Tuy nhiên, **đừng mặc định rằng mọi API đều muốn boolean theo cùng một format**.

API A có thể muốn:

```text
active=true
```

API B có thể muốn:

```text
active=1
```

API C có thể muốn:

```text
active=yes
```

Nếu API yêu cầu format đặc biệt, bạn phải chuẩn hóa trước khi truyền vào HTTPX.

Ví dụ:

```python
params = {
    "active": "1",
}
```

---

# 8. `None`

Một pattern thường gặp:

```python
params = {
    "q": "python",
    "page": 1,
    "category": None,
}
```

Nếu một parameter không có giá trị, HTTPX có cách xử lý phù hợp thay vì bạn phải tự nối URL.

Điều này đặc biệt hữu ích khi xây API client:

```python
def search(
    q: str,
    page: int = 1,
    category: str | None = None,
):
    params = {
        "q": q,
        "page": page,
        "category": category,
    }
```

---

# 9. Query Parameters trong `Client`

Bạn có thể cấu hình params mặc định:

```python
with httpx.Client(
    base_url="https://api.example.com",
    params={
        "api_key": "abc123",
    },
) as client:

    response = client.get("/users")
```

Request sẽ có:

```text
/users?api_key=abc123
```

---

# 10. Client Params + Request Params

Ví dụ:

```python
with httpx.Client(
    base_url="https://api.example.com",
    params={
        "api_key": "abc123",
    },
) as client:

    response = client.get(
        "/users",
        params={
            "page": 2,
        },
    )
```

Concept:

```text
Client params
    +
Request params
    ↓
Final URL
```

Bạn cần chú ý cách HTTPX kết hợp các parameter trong trường hợp thực tế, đặc biệt khi cùng một key xuất hiện ở cả hai cấp.

---

# 11. Query Parameter lặp lại

Đây là phần rất quan trọng.

Một URL hợp lệ có thể là:

```text
?tag=python&tag=httpx&tag=asyncio
```

Tức là:

```text
tag
tag
tag
```

cùng một key xuất hiện nhiều lần.

Một API có thể yêu cầu format này.

---

# 12. Dùng list cho multiple values

Bạn có thể viết:

```python
params = {
    "tag": [
        "python",
        "httpx",
        "asyncio",
    ]
}
```

HTTPX có thể encode thành nhiều giá trị của cùng một parameter.

Concept:

```text
tag=python
tag=httpx
tag=asyncio
```

Đây là pattern thường gặp trong API filtering.

---

# 13. Tại sao multiple values quan trọng?

Giả sử API:

```text
GET /articles
```

muốn:

```text
tag=python
tag=httpx
```

Bạn có thể biểu diễn:

```python
params = {
    "tag": ["python", "httpx"]
}
```

Thay vì tự xây:

```python
url = (
    "/articles"
    "?tag=python"
    "&tag=httpx"
)
```

---

# 14. `httpx.QueryParams`

HTTPX có object:

```python
httpx.QueryParams
```

Ví dụ:

```python
params = httpx.QueryParams(
    {
        "q": "python",
        "page": 2,
    }
)

print(params)
```

Bạn có thể truyền nó:

```python
response = httpx.get(
    url,
    params=params,
)
```

---

# 15. Tại sao cần `QueryParams`?

Trong code đơn giản:

```python
params = {
    "q": "python",
}
```

là đủ.

Nhưng khi xây HTTP client lớn, `QueryParams` giúp bạn làm việc rõ ràng hơn với query data.

Ví dụ:

```python
params = httpx.QueryParams()

params = params.set(
    "page",
    "2",
)
```

Sau đó:

```python
print(params)
```

---

# 16. Immutable mindset

Một điểm đáng chú ý là `QueryParams` có API theo hướng immutable.

Ví dụ, thay vì nghĩ:

```text
object bị sửa trực tiếp
```

hãy nghĩ:

```text
old params
   ↓
new params
```

Điều này hữu ích khi bạn muốn xây request một cách predictable.

---

# 17. URL Object

HTTPX cũng có:

```python
httpx.URL
```

Ví dụ:

```python
url = httpx.URL(
    "https://example.com/search"
)

print(url)
```

Sau đó bạn có thể làm việc với URL ở dạng object thay vì chỉ là string.

Điều này hữu ích khi xây crawler/API client có logic URL phức tạp.

---

# 18. Query + Path

Ví dụ API:

```text
/users/10/posts?page=2&limit=20
```

Ta có:

```python
user_id = 10

params = {
    "page": 2,
    "limit": 20,
}

response = client.get(
    f"/users/{user_id}/posts",
    params=params,
)
```

Đây là pattern cực kỳ phổ biến.

---

# 19. Pagination

Query params đặc biệt quan trọng với pagination.

API có thể:

```text
GET /articles?page=1&limit=20
GET /articles?page=2&limit=20
GET /articles?page=3&limit=20
```

Code:

```python
for page in range(1, 4):
    response = client.get(
        "/articles",
        params={
            "page": page,
            "limit": 20,
        },
    )

    response.raise_for_status()

    data = response.json()

    print(data)
```

Đây chính là nền tảng của crawler phân trang.

---

# 20. Pagination theo offset

Một số API không dùng `page`.

Ví dụ:

```text
?offset=0&limit=20
?offset=20&limit=20
?offset=40&limit=20
```

Code:

```python
for offset in range(0, 100, 20):
    response = client.get(
        "/articles",
        params={
            "offset": offset,
            "limit": 20,
        },
    )
```

---

# 21. Pagination theo cursor

API hiện đại đôi khi dùng:

```text
?cursor=abc123
```

Ví dụ:

```python
cursor = None

while True:
    params = {
        "limit": 100,
    }

    if cursor is not None:
        params["cursor"] = cursor

    response = client.get(
        "/articles",
        params=params,
    )

    response.raise_for_status()

    data = response.json()

    # process data

    cursor = data.get("next_cursor")

    if not cursor:
        break
```

Đây là pattern bạn sẽ gặp nhiều khi crawl API lớn.

---

# 22. Filtering

Ví dụ:

```text
/articles?category=python&status=published
```

HTTPX:

```python
params = {
    "category": "python",
    "status": "published",
}

response = client.get(
    "/articles",
    params=params,
)
```

---

# 23. Sorting

API:

```text
/articles?sort=created_at&order=desc
```

Code:

```python
params = {
    "sort": "created_at",
    "order": "desc",
}

response = client.get(
    "/articles",
    params=params,
)
```

---

# 24. Search API

Ví dụ:

```python
def search(
    client: httpx.Client,
    keyword: str,
    page: int = 1,
):
    response = client.get(
        "/search",
        params={
            "q": keyword,
            "page": page,
        },
    )

    response.raise_for_status()

    return response.json()
```

Sử dụng:

```python
results = search(
    client,
    "python httpx",
    page=2,
)
```

HTTPX xử lý việc tạo query string.

---

# 25. URL Encoding

Đây là một trong những lý do quan trọng nhất để sử dụng `params=`.

Ví dụ:

```python
params = {
    "q": "python httpx & asyncio",
}
```

Không nên tự làm:

```python
url = f"/search?q={keyword}"
```

vì dữ liệu:

```text
python httpx & asyncio
```

có các ký tự đặc biệt.

HTTPX sẽ thực hiện URL encoding phù hợp.

---

# 26. Unicode

Ví dụ:

```python
params = {
    "q": "lập trình Python",
}
```

HTTPX sẽ encode query string phù hợp với URL.

Điều này rất hữu ích khi crawler/search engine làm việc với:

```text
Tiếng Việt
中文
日本語
한국어
```

Bạn không cần tự biến text thành percent-encoding.

---

# 27. Không nên encode hai lần

Một lỗi phổ biến:

```python
from urllib.parse import quote

keyword = quote("python httpx")

params = {
    "q": keyword,
}
```

rồi HTTPX lại xử lý encoding.

Có thể dẫn đến **double encoding** tùy cách bạn xây dữ liệu.

Thông thường:

```python
params = {
    "q": "python httpx",
}
```

là đủ.

Hãy để HTTPX xử lý URL encoding.

---

# 28. Query Params trong API Client

Đây là cách thiết kế tốt:

```python
class ArticleClient:

    def __init__(self, client: httpx.Client):
        self.client = client

    def search(
        self,
        keyword: str,
        page: int = 1,
        limit: int = 20,
    ):
        response = self.client.get(
            "/articles",
            params={
                "q": keyword,
                "page": page,
                "limit": limit,
            },
        )

        response.raise_for_status()

        return response.json()
```

Application không cần biết URL query string được tạo như thế nào.

---

# 29. Đây chính là Separation of Concerns

Application:

```python
articles = client.search(
    "python",
    page=2,
)
```

API Client:

```text
search()
   ↓
params={}
   ↓
HTTPX
   ↓
URL
```

Application không phải viết:

```python
"?q=python&page=2"
```

Đây là một design principle rất tốt.

---

# 30. Debug Query Params

Khi debug, hãy kiểm tra:

```python
response.url
```

Ví dụ:

```python
response = client.get(
    "/search",
    params={
        "q": "python",
        "page": 2,
    },
)

print(response.url)
```

Đây là một trong những kỹ thuật debug HTTP đơn giản nhưng cực kỳ hữu ích.

---

# 31. Một ví dụ thực tế — Crawler

Giả sử website có:

```text
/articles?page=1
/articles?page=2
/articles?page=3
```

Ta có:

```python
import httpx


with httpx.Client(
    base_url="https://example.com",
    timeout=10.0,
) as client:

    for page in range(1, 4):

        response = client.get(
            "/articles",
            params={
                "page": page,
            },
        )

        response.raise_for_status()

        print(
            response.url,
            response.status_code,
        )
```

Rất sạch:

```text
Client
 │
 ├── GET /articles?page=1
 ├── GET /articles?page=2
 └── GET /articles?page=3
```

---

# 32. Một crawler pagination tốt hơn

Ta có thể tạo generator:

```python
def iter_pages(
    client: httpx.Client,
    max_pages: int,
):
    for page in range(1, max_pages + 1):

        response = client.get(
            "/articles",
            params={
                "page": page,
            },
        )

        response.raise_for_status()

        yield response
```

Sử dụng:

```python
with httpx.Client(
    base_url="https://example.com"
) as client:

    for response in iter_pages(client, 10):
        data = response.json()

        print(data)
```

Bạn sẽ thấy kiến thức từ các khóa Iterator trước đây bắt đầu kết nối rất tự nhiên với HTTPX.

---

# 33. Bài tập 1 — Query cơ bản

Viết:

```python
params = {
    "q": "python",
    "page": 2,
    "limit": 20,
}
```

Gửi request và in:

```python
response.url
```

---

# 34. Bài tập 2 — Multiple values

Tạo query:

```text
tag=python&tag=httpx&tag=asyncio
```

bằng `params=`.

**Không được tự nối URL.**

Sau đó kiểm tra:

```python
print(response.url)
```

---

# 35. Bài tập 3 — Search Client

Viết:

```python
class SearchClient:
    def search(
        self,
        keyword: str,
        page: int = 1,
        limit: int = 20,
    ):
        ...
```

Yêu cầu sử dụng:

```python
params={
    "q": keyword,
    "page": page,
    "limit": limit,
}
```

---

# 36. Bài tập 4 — Pagination

Viết:

```python
def iter_articles(
    client: httpx.Client,
    max_pages: int,
):
    ...
```

Yêu cầu:

```text
page=1
page=2
page=3
...
```

và sử dụng `yield`.

---

# 37. Bài tập 5 — Cursor Pagination

Viết function:

```python
def iter_articles(client):
    ...
```

API giả định trả:

```python
{
    "items": [...],
    "next_cursor": "abc123",
}
```

Yêu cầu:

```text
Request
   ↓
items
   ↓
next_cursor
   ↓
Request tiếp
   ↓
...
```

Dừng khi:

```python
next_cursor is None
```

---

# 38. Bài tập 6 — API Client thực tế

Nâng cấp:

```text
ArticleClient
│
├── list(page, limit)
├── search(keyword, page)
├── filter(category, status)
└── iter_all()
```

Kiến trúc:

```text
Application
     │
     ▼
ArticleClient
     │
     ├── params={}
     │
     ▼
httpx.Client
     │
     ▼
HTTP Server
```

---

# Tổng kết Buổi 6

Bạn cần nhớ 5 điểm:

### 1. Query params

```python
params={
    "page": 2,
}
```

### 2. Không tự nối query string

```python
# Không nên
url = f"/search?q={keyword}"

# Nên
params={"q": keyword}
```

### 3. Multiple values

```python
params={
    "tag": ["python", "httpx"]
}
```

### 4. Pagination

```python
params={
    "page": page,
    "limit": limit,
}
```

### 5. Debug

```python
print(response.url)
```

---

## Roadmap

```text
Buổi 1  HTTPX Foundation
   ↓
Buổi 2  Request / Response
   ↓
Buổi 3  HTTP Methods
   ↓
Buổi 4  Client
   ↓
Buổi 5  Timeout
   ↓
Buổi 6  Query Parameters ← hiện tại
   ↓
Buổi 7  Headers Deep Dive
   ↓
Buổi 8  Cookies
   ↓
Buổi 9  Form Data
   ↓
Buổi 10 Multipart / File Upload
```

**Buổi 7** chúng ta sẽ học `Headers` thật sâu: `User-Agent`, `Accept`, `Authorization`, `Referer`, `Content-Type`, header inheritance giữa `Client` và `Request`, cách xây default headers cho crawler/API Client, và cách debug chính xác **headers thực sự được HTTPX gửi đi**.
