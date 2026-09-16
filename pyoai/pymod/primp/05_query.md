# Buổi 5 — Query Parameters trong `primp`

Theo roadmap bạn đưa, hôm nay là:

```text
05. Query Parameters
```

Ta sẽ học kỹ hơn phần `params=`. Ở Buổi 2 chúng ta đã dùng nó, nhưng hôm nay sẽ đi sâu vào cách query string hoạt động, nhiều tham số, tham số lặp, encoding và cách ứng dụng vào **pagination của Novel Crawler**.

---

## 1. Query Parameters là gì?

Ví dụ:

```text
https://example.com/search?q=python&page=2
```

Tách URL:

```text
https://example.com/search
                       │
                       └── Query String
                           ?q=python&page=2
```

Trong đó:

```text
q    = python
page = 2
```

Ta gọi mỗi cặp:

```text
key=value
```

là một **query parameter**.

---

# 2. `params=` trong `primp`

Cách nên dùng:

```python
import primp


client = primp.Client()

response = client.get(
    "https://httpbin.org/get",
    params={
        "q": "python",
        "page": 2,
    },
)

print(response.url)
```

Thay vì tự ghép:

```python
# Không nên làm thủ công nếu không cần
url = "https://httpbin.org/get?q=python&page=2"
```

Hãy để HTTP client xử lý query encoding.

---

# 3. Một parameter

```python
response = client.get(
    "https://httpbin.org/get",
    params={
        "page": 2,
    },
)
```

URL tương ứng:

```text
https://httpbin.org/get?page=2
```

---

# 4. Nhiều parameters

```python
params = {
    "keyword": "python",
    "page": 2,
    "limit": 20,
    "sort": "newest",
}

response = client.get(
    "https://httpbin.org/get",
    params=params,
)
```

Conceptually:

```text
?keyword=python
&page=2
&limit=20
&sort=newest
```

---

# 5. Query parameter có khoảng trắng

Ví dụ:

```python
params = {
    "keyword": "python crawler",
}
```

Không cần tự biến:

```text
python crawler
```

thành:

```text
python+crawler
```

Client sẽ thực hiện encoding cần thiết.

```python
response = client.get(
    "https://httpbin.org/get",
    params=params,
)
```

Kiểm tra:

```python
print(response.url)
```

---

# 6. Unicode / tiếng Việt

Đây là trường hợp rất thực tế với crawler truyện:

```python
params = {
    "keyword": "tiên hiệp",
    "page": 2,
}
```

Request:

```python
response = client.get(
    "https://httpbin.org/get",
    params=params,
)

print(response.url)
```

Bạn sẽ thấy URL được percent-encode phù hợp.

Điểm quan trọng:

```text
Python string
      ↓
params
      ↓
URL encoding
      ↓
HTTP request
```

Không cần tự:

```python
urllib.parse.quote(...)
```

trong trường hợp thông thường.

---

# 7. Query parameter boolean

Ví dụ:

```python
params = {
    "active": True,
}
```

hoặc:

```python
params = {
    "active": False,
}
```

Ở đây cần nhớ một điều:

> Query string cuối cùng vẫn là dữ liệu dạng text.

Server có thể nhận:

```text
active=true
```

hoặc:

```text
active=True
```

tùy cách client serialize và quy ước API.

Vì vậy khi làm API thực tế, phải kiểm tra **API contract** thay vì giả định server luôn hiểu boolean giống Python.

---

# 8. Query parameter dạng số

```python
params = {
    "page": 10,
    "limit": 50,
}
```

Python:

```text
int
```

HTTP URL:

```text
page=10&limit=50
```

Không cần:

```python
str(page)
```

trước khi truyền.

---

# 9. Query parameter bị trùng

Đây là phần quan trọng.

Một URL hợp lệ có thể có:

```text
?tag=python&tag=http&tag=crawler
```

Tức:

```text
tag = python
tag = http
tag = crawler
```

Đây gọi là **duplicate query parameters**.

Điều này rất phổ biến trong API:

```text
?id=1&id=2&id=3
```

hoặc:

```text
?tag=python&tag=crawler
```

---

# 10. Tại sao dictionary không phù hợp cho duplicate key?

Không thể biểu diễn trực tiếp:

```python
{
    "tag": "python",
    "tag": "crawler",
}
```

vì Python dictionary chỉ giữ một key:

```text
tag
```

Do đó:

```python
{
    "tag": "crawler"
}
```

sẽ ghi đè giá trị trước.

Khi cần duplicate query parameters, ta cần một cấu trúc khác, chẳng hạn sequence các cặp:

```text
[
    ("tag", "python"),
    ("tag", "crawler"),
    ("tag", "async"),
]
```

Việc serialize sequence này thành duplicate query keys phụ thuộc vào API của client/version; đây là một điểm chúng ta sẽ kiểm tra khi thực hành trực tiếp với phiên bản `primp` bạn đang dùng.

---

# 11. Query Parameters và `yarl`

Điểm này rất đáng chú ý vì bạn vừa học `yarl`.

Ta có thể phân chia trách nhiệm:

```text
yarl
 │
 └── URL construction / manipulation
          │
          ▼
       URL object
          │
          ▼
primp
 │
 └── HTTP transport
          │
          ▼
        Server
```

Ví dụ về mặt tư duy:

```python
from yarl import URL

url = URL("https://example.com/search")

url = url.with_query(
    keyword="python",
    page=2,
)
```

Sau đó URL được đưa cho HTTP client.

Đây là cách rất đẹp khi crawler của bạn có nhiều logic URL.

---

# 12. Pagination

Đây là ứng dụng quan trọng nhất.

Website:

```text
/truyen?page=1
/truyen?page=2
/truyen?page=3
```

Ta viết:

```python
import primp


def fetch_listing(
    client: primp.Client,
    page: int,
):
    response = client.get(
        "https://example.com/truyen",
        params={
            "page": page,
        },
    )

    return response


def main():
    client = primp.Client()

    for page in range(1, 6):
        response = fetch_listing(
            client,
            page,
        )

        print(
            response.status_code,
            response.url,
        )


if __name__ == "__main__":
    main()
```

Luồng:

```text
page=1
   ↓
GET
   ↓
HTML
   ↓
Parser
   ↓
next page

page=2
   ↓
GET
   ↓
HTML
   ↓
Parser
```

---

# 13. Pagination không phải lúc nào cũng là `?page=`

Đây là điểm đặc biệt quan trọng đối với Novel Crawler của bạn.

Có website:

```text
/truyen?page=2
```

Website khác:

```text
/truyen/trang-2
```

Website khác:

```text
/truyen?page=2&sort=new
```

Hoặc:

```text
/truyen?start=20
```

Do đó:

```text
Query Parameters
```

chỉ là **một kiểu pagination**.

Parser của bạn phải phát hiện URL `next` thực tế từ HTML:

```text
<a href="/truyen?page=2">Next</a>
```

rồi:

```text
relative URL
      ↓
absolute URL
      ↓
Fetcher
```

Đây chính là nội dung chúng ta đã học trong `yarl`.

---

# 14. Query Parameters + Parser

Giả sử parser tìm được:

```html
<a href="/truyen?page=2">Trang sau</a>
```

Parser không nên tự request.

❌:

```python
html = client.get(next_url).text
```

Đúng:

```text
Parser
  ↓
next_url
  ↓
Application
  ↓
Fetcher
  ↓
primp
```

Kiến trúc:

```text
              ListingParser
                   │
                   │ next_url
                   ▼
              Crawl UseCase
                   │
                   ▼
                Fetcher
                   │
                   ▼
             PrimpFetcher
                   │
                   ▼
                 primp
```

---

# 15. Query Parameters + Filter

Giả sử website hỗ trợ:

```text
/truyen
    ?category=tien-hiep
    &status=completed
    &page=2
```

Ta có:

```python
params = {
    "category": "tien-hiep",
    "status": "completed",
    "page": 2,
}
```

Request:

```python
response = client.get(
    "https://example.com/truyen",
    params=params,
)
```

Đây chính là kiểu request mà một crawler listing thường xuyên gặp.

---

# 16. Query Parameters + Search

Ví dụ:

```python
def search_novels(
    client: primp.Client,
    keyword: str,
    page: int = 1,
):
    return client.get(
        "https://example.com/search",
        params={
            "keyword": keyword,
            "page": page,
        },
    )
```

Sử dụng:

```python
response = search_novels(
    client,
    keyword="tiên hiệp",
    page=3,
)
```

---

# 17. Đừng trộn URL building với HTTP request

Một thiết kế tốt:

```python
def build_search_url(
    keyword: str,
    page: int,
):
    ...
```

và:

```python
def fetch(
    url: str,
):
    ...
```

Hai trách nhiệm khác nhau:

```text
URL Builder
    ↓
URL

Fetcher
    ↓
HTTP request
```

Điều này đặc biệt hữu ích khi crawler của bạn có nhiều source:

```text
TruyenFull
NovelSourceA
NovelSourceB
NovelSourceC
```

Mỗi plugin biết cách xây URL.

`PrimpFetcher` chỉ biết:

```python
fetch(url)
```

---

# 18. Một `PrimpFetcher` nhỏ

Sau khi học đến đây, ta có thể viết:

```python
import primp


class PrimpFetcher:

    def __init__(self):
        self.client = primp.Client()

    def get(
        self,
        url: str,
        params: dict | None = None,
    ):
        return self.client.get(
            url,
            params=params,
        )
```

Sử dụng:

```python
def main():
    fetcher = PrimpFetcher()

    response = fetcher.get(
        "https://httpbin.org/get",
        params={
            "keyword": "python",
            "page": 2,
        },
    )

    print(response.status_code)
    print(response.url)
    print(response.text)


if __name__ == "__main__":
    main()
```

Đây mới chỉ là **adapter đơn giản**.

Chúng ta chưa thêm:

```text
timeout
retry
proxy
exception mapping
logging
browser profile
```

---

# 19. Một lỗi rất hay gặp

❌ Tự nối query:

```python
url = (
    "https://example.com/search"
    f"?keyword={keyword}"
    f"&page={page}"
)
```

Với:

```python
keyword = "tiên hiệp & huyền huyễn"
```

bạn rất dễ tạo URL sai nếu tự xử lý encoding không cẩn thận.

Ưu tiên:

```python
response = client.get(
    "https://example.com/search",
    params={
        "keyword": keyword,
        "page": page,
    },
)
```

---

# 20. Bài tập thực hành

## Bài 1

Gửi:

```python
params={
    "keyword": "python",
    "page": 3,
}
```

tới:

```text
https://httpbin.org/get
```

và in:

```text
response.url
```

---

## Bài 2

Thử Unicode:

```python
params={
    "keyword": "truyện tiên hiệp",
    "page": 5,
}
```

Quan sát URL cuối cùng.

---

## Bài 3

Viết:

```python
def fetch_listing(
    client,
    page: int,
):
    ...
```

sao cho:

```python
fetch_listing(client, 1)
fetch_listing(client, 2)
fetch_listing(client, 3)
```

tương ứng với:

```text
?page=1
?page=2
?page=3
```

---

## Bài 4 — rất quan trọng

Tạo:

```python
params = {
    "keyword": "tiên hiệp",
    "category": "fantasy",
    "status": "completed",
    "page": 2,
    "limit": 20,
}
```

Gửi tới:

```text
https://httpbin.org/get
```

Sau đó dùng:

```python
data = response.json()
```

và kiểm tra:

```python
data["args"]
```

Bạn sẽ thấy cách server parse query parameters.

---

# Tổng kết Buổi 5

Ta có:

```text
params=
   │
   ▼
Query Parameters
   │
   ▼
URL
```

Ví dụ:

```python
client.get(
    url,
    params={
        "keyword": "python",
        "page": 2,
    },
)
```

Tạo conceptually:

```text
/search?keyword=python&page=2
```

Các trường hợp cần nhớ:

```text
dict
 │
 ├── string
 ├── int
 ├── bool
 ├── Unicode
 └── ...
```

Và:

```text
Query Parameters
       ≠
POST JSON
       ≠
Form Data
```

### Roadmap

```text
01. Cài đặt + Client      ✓
02. GET request           ✓
03. Response              ✓
04. Headers               ✓
05. Query Parameters      ← hôm nay
06. POST
07. JSON
08. Form Data
09. Cookies
10. Redirect
```

**Buổi 6** theo roadmap của bạn sẽ là **POST request**; chúng ta sẽ đi sâu vào `POST`, request body, `data=`, `json=`, và cách phân biệt POST form với POST JSON trong `primp`.
