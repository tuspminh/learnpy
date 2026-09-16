# Buổi 2 — GET Request & Query Parameters trong `primp`

Ở buổi 1, ta đã biết:

```python
client = primp.Client()

response = client.get(url)
```

Hôm nay tập trung vào **GET request**, đặc biệt là **query parameters** — thứ xuất hiện liên tục khi crawl listing, pagination, tìm kiếm truyện.

---

## 1. GET request là gì?

Ví dụ URL:

```text
https://example.com/search?q=python&page=2
```

Ta có:

```text
https://example.com/search
                       └─────────────── URL path

?q=python&page=2
└──────────────── Query String
```

Query gồm các cặp:

```text
q    = python
page = 2
```

Trong crawler:

```text
Listing
   │
   ├── /truyen-moi
   ├── /truyen-moi?page=2
   ├── /truyen-moi?page=3
   └── ...
```

Query parameters rất quan trọng.

---

# 2. Cách đơn giản nhất: viết trực tiếp URL

```python
import primp


def main():
    client = primp.Client()

    response = client.get(
        "https://httpbin.org/get?q=python&page=2"
    )

    print("Status:", response.status_code)
    print(response.text)


if __name__ == "__main__":
    main()
```

Server sẽ nhận:

```text
q=python
page=2
```

---

# 3. Dùng `params`

Thay vì tự nối URL:

```python
url = "https://httpbin.org/get?q=python&page=2"
```

ta truyền parameters riêng:

```python
import primp


def main():
    client = primp.Client()

    response = client.get(
        "https://httpbin.org/get",
        params={
            "q": "python",
            "page": 2,
        },
    )

    print(response.text)


if __name__ == "__main__":
    main()
```

Đây là cách nên ưu tiên.

Conceptually:

```text
URL
 +
params
 ↓
final URL
```

Tức:

```text
https://httpbin.org/get
+
?q=python&page=2
```

---

# 4. Kiểm tra URL cuối cùng

Sau request:

```python
print(response.url)
```

Ví dụ:

```python
import primp


def main():
    client = primp.Client()

    response = client.get(
        "https://httpbin.org/get",
        params={
            "q": "python",
            "page": 2,
        },
    )

    print("Final URL:")
    print(response.url)


if __name__ == "__main__":
    main()
```

Bạn sẽ thấy URL tương tự:

```text
https://httpbin.org/get?q=python&page=2
```

Đây là một kỹ năng rất quan trọng khi debug crawler.

---

# 5. Nhiều parameters

Ví dụ:

```python
params = {
    "keyword": "python",
    "page": 3,
    "limit": 20,
    "sort": "newest",
}
```

Request:

```python
response = client.get(
    "https://httpbin.org/get",
    params=params,
)
```

Tương đương:

```text
?keyword=python&page=3&limit=20&sort=newest
```

---

# 6. Parameter có tiếng Việt

Đây là trường hợp crawler thường gặp.

```python
params = {
    "q": "truyện tiên hiệp",
    "page": 2,
}

response = client.get(
    "https://httpbin.org/get",
    params=params,
)
```

Không nên tự làm:

```python
url = (
    "https://example.com/search"
    "?q=truyện tiên hiệp"
    "&page=2"
)
```

vì việc encode URL nên để HTTP client xử lý.

---

# 7. Giá trị `None`

Ví dụ:

```python
params = {
    "q": "python",
    "page": 2,
    "author": None,
}
```

Trong thực tế, cách thư viện xử lý tham số `None` là điều cần kiểm tra theo phiên bản/API cụ thể; vì vậy **đừng xây logic crawler dựa trên giả định rằng `None` luôn bị bỏ qua**.

Một pattern an toàn hơn là tự loại bỏ:

```python
params = {
    "q": "python",
    "page": 2,
    "author": None,
}

params = {
    key: value
    for key, value in params.items()
    if value is not None
}
```

Sau đó:

```python
response = client.get(
    url,
    params=params,
)
```

---

# 8. Query parameter dạng list

Một website có thể nhận:

```text
?tag=python&tag=crawler&tag=async
```

Tức một key xuất hiện nhiều lần.

Khi làm crawler, đây là trường hợp cần chú ý vì **không phải server nào cũng quy ước list giống nhau**.

Ví dụ dạng query string:

```text
tag=python
tag=crawler
tag=async
```

Ta sẽ học kỹ hơn vấn đề **duplicate query parameters** khi kết hợp `primp` với `yarl` — vì bạn vừa học `yarl`, và đây là chỗ hai thư viện phối hợp rất tốt:

```text
yarl.URL
    ↓
URL construction
    ↓
primp
    ↓
HTTP request
```

---

# 9. Pagination — ứng dụng trực tiếp vào Novel Crawler

Giả sử website có:

```text
https://example.com/truyen?page=1
https://example.com/truyen?page=2
https://example.com/truyen?page=3
```

Ta viết:

```python
import primp


def fetch_page(client: primp.Client, page: int) -> str:
    response = client.get(
        "https://example.com/truyen",
        params={
            "page": page,
        },
    )

    return response.text


def main():
    client = primp.Client()

    for page in range(1, 4):
        html = fetch_page(client, page)

        print(
            f"Fetched page {page}: "
            f"{len(html)} characters"
        )


if __name__ == "__main__":
    main()
```

Kiến trúc:

```text
page=1
   ↓
GET /truyen?page=1
   ↓
HTML
   ↓
Parser

page=2
   ↓
GET /truyen?page=2
   ↓
HTML
   ↓
Parser
```

Đây chính là phần Fetcher mà sau này chúng ta sẽ nâng cấp.

---

# 10. Đừng tạo Client cho từng request

❌ Không nên:

```python
for page in range(1, 100):
    client = primp.Client()

    response = client.get(
        url,
        params={"page": page},
    )
```

Thay vào đó:

```python
client = primp.Client()

for page in range(1, 100):
    response = client.get(
        url,
        params={"page": page},
    )
```

Tư duy:

```text
1 Client
   │
   ├── Request 1
   ├── Request 2
   ├── Request 3
   ├── ...
   └── Request 100
```

Thay vì:

```text
Client 1 → Request 1
Client 2 → Request 2
Client 3 → Request 3
...
```

Việc tái sử dụng client sẽ trở nên đặc biệt quan trọng khi chúng ta học **cookies, connection reuse, proxy, timeout và browser impersonation**.

---

# 11. GET request hoàn chỉnh

Hãy viết một mini utility:

```python
import primp


class HttpFetcher:

    def __init__(self):
        self.client = primp.Client()

    def get(
        self,
        url: str,
        params: dict | None = None,
    ):
        response = self.client.get(
            url,
            params=params,
        )

        return response


def main():
    fetcher = HttpFetcher()

    response = fetcher.get(
        "https://httpbin.org/get",
        params={
            "keyword": "python",
            "page": 2,
        },
    )

    print("Status:", response.status_code)
    print("URL:", response.url)
    print("Body:")
    print(response.text)


if __name__ == "__main__":
    main()
```

Đây chưa phải `PrimpFetcher` chuẩn DDD. Chúng ta chỉ đang làm quen API trước.

---

# 12. Một điểm rất quan trọng: URL Builder ≠ HTTP Client

Trong crawler lớn, nên phân biệt:

```text
URLBuilder
   │
   │ tạo URL
   ▼
https://example.com/truyen?page=2
   │
   ▼
Fetcher
   │
   │ HTTP GET
   ▼
Response
   │
   ▼
Parser
```

Không nên để parser tự xây URL:

```python
# ❌
parser.build_next_url(...)
```

Và cũng không nên để HTTP client chứa logic website:

```python
# ❌
client.get_novel_chapter(...)
```

Fetcher chỉ nên quan tâm:

```python
response = client.get(url)
```

Còn URL/domain logic thuộc tầng khác.

Điều này rất phù hợp với kiến trúc **DDD + SOLID** mà chúng ta sẽ áp dụng cho Novel Crawler.

---

# 13. Bài tập thực hành

### Bài 1

Gọi:

```text
https://httpbin.org/get
```

với:

```python
params={
    "keyword": "python",
    "page": 5,
}
```

In:

```text
status
final URL
response body
```

---

### Bài 2

Tạo:

```python
def fetch_search(
    client,
    keyword: str,
    page: int,
):
    ...
```

Sao cho:

```python
response = fetch_search(
    client,
    "python crawler",
    3,
)
```

tạo request tương đương:

```text
/search?keyword=python+crawler&page=3
```

---

### Bài 3 — crawler

Viết:

```python
def crawl_pages(
    client,
    url: str,
    start_page: int,
    end_page: int,
):
    ...
```

Ví dụ:

```python
crawl_pages(
    client,
    "https://httpbin.org/get",
    1,
    5,
)
```

Mỗi request phải có:

```text
page=1
page=2
page=3
page=4
page=5
```

---

## Những gì cần nhớ sau Buổi 2

```text
primp.Client()
       │
       ▼
client.get(url)
       │
       ├── params
       │
       ▼
   HTTP Request
       │
       ▼
   Response
       │
       ├── status_code
       ├── url
       ├── headers
       ├── text
       └── content
```

Và đối với crawler:

```text
Pagination
    ↓
params={"page": n}
    ↓
Fetcher
    ↓
Response
    ↓
Parser
```

**Buổi 3** chúng ta sẽ học **Headers trong `primp`**: `headers=`, default headers, `User-Agent`, `Accept`, `Referer`, cách header ảnh hưởng đến request, và đặc biệt sẽ bắt đầu nối sang **browser impersonation**.
