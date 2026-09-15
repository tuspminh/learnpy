# Phần III — Query String chuyên sâu

# Buổi 25 — `URL.query`

Ở Buổi 24, chúng ta đã biết query có thể chứa **duplicate parameters**:

```text
https://example.com/search?tag=python&tag=sqlite&tag=yarl
```

Hôm nay chúng ta đi sâu vào:

```python
url.query
```

Đây là một trong những thuộc tính quan trọng nhất của `yarl.URL` khi xây crawler.

---

# 1. `url.query` là gì?

Ví dụ:

```python
from yarl import URL


url = URL(
    "https://example.com/search"
    "?keyword=python"
    "&page=2"
)

print(url.query)
```

`url.query` đại diện cho **query string đã được parse thành cấu trúc dữ liệu**, thay vì để bạn phải tự xử lý:

```text
?keyword=python&page=2
```

bằng string.

Mental model:

```text
URL
 │
 ├── scheme
 ├── host
 ├── path
 ├── query  ← hôm nay
 └── fragment
```

---

# 2. Xem kiểu dữ liệu

Bạn có thể kiểm tra:

```python
from yarl import URL


url = URL(
    "https://example.com/search"
    "?keyword=python"
    "&page=2"
)

print(type(url.query))
```

Trong yarl, `url.query` là một **`MultiDictProxy`** từ thư viện `multidict`.

Điều này giải thích tại sao nó có thể biểu diễn:

```text
tag=python
tag=sqlite
tag=yarl
```

trong khi `dict` thông thường không thể giữ nhiều entry cùng key.

---

# 3. Vì sao yarl dùng `MultiDictProxy`?

Hãy so sánh.

## `dict`

```python
params = {
    "tag": "python",
}
```

Không thể có:

```python
{
    "tag": "python",
    "tag": "sqlite",
}
```

Key `tag` chỉ tồn tại một lần.

---

## MultiDict

Có thể biểu diễn:

```text
tag = python
tag = sqlite
tag = yarl
```

Đây chính là dạng query thực tế:

```text
?tag=python&tag=sqlite&tag=yarl
```

Vì URL có thể chứa duplicate parameters nên `MultiDict` phù hợp hơn.

---

# 4. Đọc một parameter

Ví dụ:

```python
from yarl import URL


url = URL(
    "https://example.com/search"
    "?keyword=python"
    "&page=2"
)

print(url.query["keyword"])
print(url.query["page"])
```

Kết quả:

```text
python
2
```

Lưu ý:

```python
url.query["page"]
```

trả về **string**:

```python
"2"
```

chứ không phải:

```python
2
```

Nếu cần số:

```python
page = int(url.query["page"])
```

---

# 5. Query values về cơ bản là string

Ví dụ URL:

```text
?page=2&limit=20&active=true
```

thì:

```python
print(url.query["page"])
print(type(url.query["page"]))
```

sẽ cho:

```text
2
<class 'str'>
```

Tương tự:

```text
20
```

vẫn là:

```python
"20"
```

và:

```text
true
```

là:

```python
"true"
```

Vì URL bản chất là text representation.

---

# 6. `query["key"]` và key không tồn tại

Ví dụ:

```python
from yarl import URL


url = URL(
    "https://example.com/search"
    "?keyword=python"
)

print(url.query["keyword"])
```

OK.

Nhưng:

```python
print(url.query["page"])
```

sẽ phát sinh lỗi nếu `page` không tồn tại.

Vì vậy khi parameter là optional, thường dùng:

```python
url.query.get("page")
```

Chúng ta sẽ học kỹ `.get()` ở Buổi 27.

---

# 7. Kiểm tra key tồn tại

Có thể dùng:

```python
if "page" in url.query:
    print("page exists")
```

Ví dụ:

```python
from yarl import URL


url = URL(
    "https://example.com/search"
    "?keyword=python"
    "&page=2"
)


if "page" in url.query:
    print("page exists")

if "author" not in url.query:
    print("author does not exist")
```

Output:

```text
page exists
author does not exist
```

Đây là pattern rất hữu ích trong Parser.

---

# 8. `keys()`

Lấy các query keys:

```python
from yarl import URL


url = URL(
    "https://example.com/search"
    "?keyword=python"
    "&page=2"
    "&sort=new"
)

print(list(url.query.keys()))
```

Kết quả:

```text
['keyword', 'page', 'sort']
```

---

# 9. `values()`

Lấy values:

```python
print(list(url.query.values()))
```

Kết quả:

```text
['python', '2', 'new']
```

Mental model:

```text
keys()
   ↓
keyword
page
sort

values()
   ↓
python
2
new
```

---

# 10. `items()`

Đây là API cực kỳ quan trọng.

```python
from yarl import URL


url = URL(
    "https://example.com/search"
    "?keyword=python"
    "&page=2"
    "&sort=new"
)

print(list(url.query.items()))
```

Kết quả:

```python
[
    ("keyword", "python"),
    ("page", "2"),
    ("sort", "new"),
]
```

Tức là:

```text
items()
   ↓
(key, value)
```

---

# 11. Duyệt query bằng `for`

Đây là cách tôi khuyên bạn dùng khi debug Parser:

```python
for key, value in url.query.items():
    print(f"{key} = {value}")
```

Output:

```text
keyword = python
page = 2
sort = new
```

Rất dễ đọc.

---

# 12. Duplicate parameter với `items()`

Đây là điểm liên quan trực tiếp Buổi 24.

```python
from yarl import URL


url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=sqlite"
    "&tag=yarl"
)

for key, value in url.query.items():
    print(key, "=", value)
```

Kết quả:

```text
tag = python
tag = sqlite
tag = yarl
```

Các query entries được giữ riêng.

Do đó:

```python
list(url.query.items())
```

cho:

```python
[
    ("tag", "python"),
    ("tag", "sqlite"),
    ("tag", "yarl"),
]
```

---

# 13. `query` không phải `dict`

Đây là một điểm bạn cần nhớ khi học yarl.

Không nên nghĩ:

```python
url.query
```

chính xác là:

```python
dict
```

Mà hãy nghĩ:

```text
url.query
    ↓
MultiDictProxy
    ↓
query có thể có duplicate keys
```

Ví dụ:

```text
?tag=python&tag=sqlite
```

vẫn giữ được:

```text
tag → python
tag → sqlite
```

---

# 14. So sánh với `dict`

```python
from yarl import URL


url = URL(
    "https://example.com/search"
    "?tag=python"
    "&tag=sqlite"
)

print("query:")
print(url.query)

print()

print("items:")
print(list(url.query.items()))

print()

print("dict:")
print(dict(url.query))
```

Điểm quan trọng là:

```text
url.query
```

có khả năng giữ duplicate.

Trong khi:

```python
dict(url.query)
```

ép dữ liệu về cấu trúc dictionary và **không còn phù hợp để bảo toàn duplicate keys**.

---

# 15. Query là read-only

Tên kiểu:

```text
MultiDictProxy
```

có chữ:

```text
Proxy
```

vì đây là view/proxy cho dữ liệu query.

Bạn không nên tư duy:

```python
url.query["page"] = "3"
```

để thay đổi URL.

Thay vào đó:

```python
url.with_query(...)
```

là cách đúng.

Điều này phù hợp với tính **immutable** của `yarl.URL`.

---

# 16. Muốn thay đổi query → tạo URL mới

Ví dụ:

```python
from yarl import URL


url = URL(
    "https://example.com/search"
    "?keyword=python"
    "&page=2"
)

new_url = url.with_query(
    {
        "keyword": "python",
        "page": 3,
    }
)

print("old:", url)
print("new:", new_url)
```

Kết quả:

```text
old: https://example.com/search?keyword=python&page=2

new: https://example.com/search?keyword=python&page=3
```

---

# 17. `query` giữ thứ tự query entries

Ví dụ:

```python
url = URL(
    "https://example.com/search"
    "?b=2"
    "&a=1"
    "&c=3"
)
```

Khi duyệt:

```python
for key, value in url.query.items():
    print(key, value)
```

ta có thể quan sát thứ tự:

```text
b 2
a 1
c 3
```

Điều này đặc biệt hữu ích khi bạn đang làm:

```text
URL
 ↓
parse
 ↓
modify
 ↓
rebuild
```

và muốn kiểm soát query entries thay vì biến chúng thành một `dict` một cách vô thức.

---

# 18. `query_string`

Đừng nhầm:

```python
url.query
```

với:

```python
url.query_string
```

Ví dụ:

```python
from yarl import URL


url = URL(
    "https://example.com/search"
    "?keyword=python"
    "&page=2"
)

print(url.query)
print(url.query_string)
```

Khái niệm:

```text
query
    ↓
cấu trúc dữ liệu đã parse

query_string
    ↓
chuỗi query đã encode
```

Ví dụ:

```text
url.query
```

giống như:

```text
keyword → python
page    → 2
```

còn:

```text
url.query_string
```

giống:

```text
keyword=python&page=2
```

Không có dấu:

```text
?
```

---

# 19. Khi nào dùng `query`?

Trong crawler, `query` phù hợp khi bạn muốn **phân tích URL**.

Ví dụ:

```python
page = url.query.get("page")
keyword = url.query.get("keyword")
tags = url.query.getall("tag")
```

Mental model:

```text
Parser / Application
       ↓
    URL.query
       ↓
    structured data
```

---

# 20. Khi nào dùng `query_string`?

Khi bạn cần **chuỗi query đã encode**.

Ví dụ:

```python
print(url.query_string)
```

có thể dùng để:

* logging
* debug
* canonicalization logic
* inspect URL
* so sánh representation

Nhưng nếu muốn lấy parameter cụ thể:

```python
url.query
```

phù hợp hơn.

---

# 21. Ví dụ Unicode

```python
from yarl import URL


url = URL(
    "https://example.com/search"
).with_query(
    {
        "q": "lập trình Python",
        "page": 2,
    }
)

print(url)
print(url.query)
print(url.query["q"])
print(url.query["page"])
```

URL khi stringify sẽ được encode phù hợp.

Nhưng khi đọc:

```python
url.query["q"]
```

bạn nhận được giá trị ở dạng decoded:

```text
lập trình Python
```

Đây là một trong những lý do nên để `yarl` xử lý URL encoding/decoding thay vì tự `replace()` string.

---

# 22. Ví dụ crawler thực tế

Giả sử Parser nhận:

```text
https://example.com/novels
?genre=fantasy
&genre=action
&status=completed
&page=3
```

Ta viết:

```python
from yarl import URL


url = URL(
    "https://example.com/novels"
    "?genre=fantasy"
    "&genre=action"
    "&status=completed"
    "&page=3"
)


genres = url.query.getall("genre")
status = url.query.get("status")
page = int(url.query.get("page", "1"))


print("Genres:", genres)
print("Status:", status)
print("Page:", page)
```

Kết quả:

```text
Genres: ['fantasy', 'action']
Status: completed
Page: 3
```

Đây chính là kiểu code bạn sẽ dùng trong Novel Parser.

---

# 23. Xây một Query Inspector

Một bài tập rất tốt để hiểu `url.query`:

```python
from yarl import URL


def inspect_query(url: URL) -> None:
    print("URL:")
    print(url)

    print("\nQuery type:")
    print(type(url.query))

    print("\nKeys:")
    print(list(url.query.keys()))

    print("\nValues:")
    print(list(url.query.values()))

    print("\nItems:")

    for key, value in url.query.items():
        print(f"  {key} = {value}")


def main():
    url = URL(
        "https://example.com/search"
        "?keyword=python"
        "&tag=sqlite"
        "&tag=yarl"
        "&page=2"
    )

    inspect_query(url)


if __name__ == "__main__":
    main()
```

Bạn sẽ thấy rõ:

```text
URL
 ↓
query
 ↓
MultiDictProxy
 ├── keys()
 ├── values()
 └── items()
```

---

# 24. Một pattern rất đáng nhớ

Trong Novel Crawler, bạn có thể gặp:

```python
url = URL(...)
```

Sau đó:

```python
query = url.query
```

rồi:

```python
keyword = query.get("keyword")
page = query.get("page")
genres = query.getall("genre")
```

Tức là:

```text
URL
 │
 └── query
      │
      ├── get()       → một value
      │
      ├── getall()    → nhiều value
      │
      ├── keys()      → keys
      │
      ├── values()    → values
      │
      └── items()     → key/value pairs
```

---

# 25. Đừng biến `query` thành dict quá sớm

Đây là nguyên tắc quan trọng cho crawler của bạn.

Không nên:

```python
params = dict(url.query)
```

ngay khi parse URL nếu bạn chưa biết query có duplicate hay không.

Tốt hơn:

```python
query = url.query
```

và chỉ chuyển sang cấu trúc khác khi domain/application thực sự yêu cầu.

Nếu cần bảo toàn toàn bộ entries:

```python
items = list(query.items())
```

Nếu cần tất cả value của một key:

```python
values = query.getall("tag")
```

---

# 26. Kiến trúc trong Novel Crawler

Ta có thể hình dung:

```text
                    yarl
                     │
                     ▼
                   URL
                     │
                     ▼
                URL.query
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
        get()     getall()    items()
          │          │          │
          ▼          ▼          ▼
       keyword      genres    raw pairs
          │          │          │
          └──────────┼──────────┘
                     ▼
                 Application
```

Điểm quan trọng:

> `yarl` chịu trách nhiệm URL representation/parsing; domain model của crawler không nên phụ thuộc trực tiếp vào mọi chi tiết của `MultiDictProxy`.

Ví dụ domain không nhất thiết phải biết:

```python
MultiDictProxy
```

Nó có thể nhận:

```python
SearchCriteria(
    keyword="python",
    genres=["fantasy", "action"],
    page=3,
)
```

Đây chính là ranh giới tốt giữa:

```text
Infrastructure / URL
```

và:

```text
Domain
```

---

# 27. Complete example

Chạy nguyên file này:

```python
from yarl import URL


def main():
    url = URL(
        "https://example.com/novels"
        "?keyword=python"
        "&genre=fantasy"
        "&genre=action"
        "&status=completed"
        "&page=3"
    )

    print("========== URL ==========")
    print(url)

    print("\n========== QUERY TYPE ==========")
    print(type(url.query))

    print("\n========== KEYS ==========")
    print(list(url.query.keys()))

    print("\n========== VALUES ==========")
    print(list(url.query.values()))

    print("\n========== ITEMS ==========")

    for key, value in url.query.items():
        print(f"{key} = {value}")

    print("\n========== SINGLE VALUE ==========")

    keyword = url.query["keyword"]

    print(keyword)
    print(type(keyword))

    print("\n========== OPTIONAL VALUE ==========")

    author = url.query.get("author")

    print(author)

    print("\n========== DUPLICATE VALUES ==========")

    genres = url.query.getall("genre")

    print(genres)

    print("\n========== PAGE ==========")

    page = int(
        url.query.get("page", "1")
    )

    print(page)
    print(type(page))


if __name__ == "__main__":
    main()
```

Output chính:

```text
========== URL ==========
https://example.com/novels?keyword=python&genre=fantasy&genre=action&status=completed&page=3

========== KEYS ==========
['keyword', 'genre', 'genre', 'status', 'page']

========== VALUES ==========
['python', 'fantasy', 'action', 'completed', '3']

========== ITEMS ==========
keyword = python
genre = fantasy
genre = action
status = completed
page = 3

========== SINGLE VALUE ==========
python

========== DUPLICATE VALUES ==========
['fantasy', 'action']

========== PAGE ==========
3
<class 'int'>
```

Lưu ý đặc biệt: với duplicate keys, danh sách `keys()`/`values()`/`items()` phản ánh các query entries; vì vậy `keys()` có thể chứa cùng một key nhiều lần.

---

# 28. 🧠 Tổng kết Buổi 25

### `url.query`

```python
url.query
```

là cấu trúc query của URL, dựa trên `MultiDictProxy`.

### Một value

```python
url.query["page"]
```

### Kiểm tra

```python
"page" in url.query
```

### Keys

```python
url.query.keys()
```

### Values

```python
url.query.values()
```

### Entries

```python
url.query.items()
```

### Duplicate values

```python
url.query.getall("tag")
```

### Query string

```python
url.query_string
```

### Không nên

```python
dict(url.query)
```

nếu bạn cần bảo toàn duplicate parameters.

---

## Roadmap tiếp theo

```text
Buổi 25 — query                    ← hôm nay
        ↓
Buổi 26 — query_string
        ↓
Buổi 27 — query.get()
        ↓
Buổi 28 — query.getall()
        ↓
Buổi 29 — Encoding / decoding
        ↓
Buổi 30 — Unicode trong URL
```

**Buổi 26** sẽ đi riêng vào `query_string`: khác `query` như thế nào, encoded string là gì, khi nào nên dùng `query_string`, và đặc biệt là cách `yarl` biểu diễn các ký tự đặc biệt trong query.
