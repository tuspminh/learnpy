
# Buổi 1 — Giới thiệu `yarl`

## 1. `yarl` là gì?

`yarl` là thư viện Python dùng để làm việc với **URL một cách có cấu trúc**.

Thay vì:

```python
url = "https://example.com/books?page=2"
```

ta có:

```python
from yarl import URL

url = URL("https://example.com/books?page=2")
```

Lúc này `url` không còn đơn thuần là `str`.

Nó là một object có thể truy cập từng thành phần:

```python
print(url.scheme)
print(url.host)
print(url.path)
print(url.query)
```

---

# 2. Cài đặt

```bash
pip install yarl
```

Kiểm tra:

```python
import yarl

print(yarl.__version__)
```

---

# 3. Ví dụ đầu tiên

Tạo file:

```text
lesson_01.py
```

Code hoàn chỉnh:

```python
from yarl import URL


url = URL("https://example.com/books?page=2")


print("URL:", url)
print("Type:", type(url))

print("Scheme:", url.scheme)
print("Host:", url.host)
print("Path:", url.path)
print("Query:", url.query)
```

Kết quả tương tự:

```text
URL: https://example.com/books?page=2
Type: <class 'yarl.URL'>

Scheme: https
Host: example.com
Path: /books
Query: <MultiDictProxy('page': '2')>
```

Điểm quan trọng:

```python
url = URL(...)
```

không phải:

```python
url = "..."
```

---

# 4. URL được chia thành những phần nào?

Ví dụ:

```text
https://example.com:8080/novels/chapter-1?page=2&sort=new#content
```

Có thể hình dung:

```text
https://example.com:8080/novels/chapter-1?page=2&sort=new#content
│      │           │                       │                │
│      │           │                       │                └── fragment
│      │           │                       └── query
│      │           └── path
│      └── host + port
└── scheme
```

Trong `yarl`:

```python
from yarl import URL


url = URL("https://example.com:8080/novels/chapter-1?page=2&sort=new#content")


print("scheme   =", url.scheme)
print("host     =", url.host)
print("port     =", url.port)
print("path     =", url.path)
print("query    =", url.query)
print("fragment =", url.fragment)
```

---

# 5. `yarl.URL` không chỉ là một string

Đây là điểm quan trọng nhất của bài hôm nay.

Với string:

```python
url = "https://example.com/books?page=2"
```

muốn lấy host rất bất tiện.

Bạn phải tự parse:

```python
# Không nên tự làm
```

Trong `yarl`:

```python
url = URL("https://example.com/books?page=2")

print(url.host)
```

Kết quả:

```text
example.com
```

---

# 6. Các thuộc tính quan trọng

Một `URL` có rất nhiều property.

Những cái chúng ta sẽ dùng thường xuyên:

```python
url.scheme
url.host
url.port
url.path
url.query
url.fragment
```

Ngoài ra còn có:

```python
url.user
url.password
url.raw_path
url.raw_query_string
url.query_string
url.origin()
```

Ví dụ:

```python
from yarl import URL


url = URL("https://user:secret@example.com:8080/books/page-2?page=2#chapter")


print("scheme:", url.scheme)
print("user:", url.user)
print("password:", url.password)
print("host:", url.host)
print("port:", url.port)
print("path:", url.path)
print("query:", url.query)
print("fragment:", url.fragment)
```

---

# 7. `URL` là immutable

Đây là một đặc điểm cực kỳ quan trọng.

Ví dụ:

```python
from yarl import URL


url = URL("https://example.com/books")


new_url = url.with_query(page=2)


print(url)
print(new_url)
```

Kết quả:

```text
https://example.com/books
https://example.com/books?page=2
```

`url` **không thay đổi**.

Thay vào đó:

```python
new_url = url.with_query(page=2)
```

tạo ra một URL mới.

---

# 8. Tại sao immutable rất hữu ích cho crawler?

Giả sử crawler có:

```python
base_url = URL("https://example.com")
```

Ta có thể tạo:

```python
novel_url = base_url / "novel" / "abc"

chapter_url = novel_url / "chapter-1"

image_url = novel_url / "images" / "cover.jpg"
```

Mỗi object độc lập.

```text
base_url
   │
   ├── novel_url
   │      │
   │      ├── chapter_url
   │      │
   │      └── image_url
```

Không cần sửa chuỗi URL bằng tay.

---

# 9. Một ví dụ rất sát với Novel Crawler

Giả sử website:

```text
https://example.com
```

Novel:

```text
https://example.com/novel/dau-pha-thuong-khung
```

Chapter:

```text
https://example.com/novel/dau-pha-thuong-khung/chuong-1
```

Ta viết:

```python
from yarl import URL


BASE_URL = URL("https://example.com")


novel_url = BASE_URL / "novel" / "dau-pha-thuong-khung"

chapter_url = novel_url / "chuong-1"


print("Base:", BASE_URL)
print("Novel:", novel_url)
print("Chapter:", chapter_url)
```

Kết quả:

```text
Base: https://example.com
Novel: https://example.com/novel/dau-pha-thuong-khung
Chapter: https://example.com/novel/dau-pha-thuong-khung/chuong-1
```

Đây sẽ là một trong những thao tác chúng ta sử dụng rất nhiều khi xây crawler.

---

# 10. `/` — một tính năng cực kỳ hay

`yarl` cho phép dùng `/` để nối path:

```python
url = URL("https://example.com")

url = url / "novels"
url = url / "python"
url = url / "chapter-1"

print(url)
```

Kết quả:

```text
https://example.com/novels/python/chapter-1
```

Thay vì:

```python
url = "https://example.com/" + "novels/" + "python/" + "chapter-1"
```

---

# 11. So sánh string với `yarl`

### String

```python
base = "https://example.com"

url = base + "/novels/" + "python"
```

Dễ phát sinh:

```text
https://example.com//novels/python
```

hoặc:

```text
https://example.comnovels/python
```

nếu xử lý slash không cẩn thận.

### `yarl`

```python
base = URL("https://example.com")

url = base / "novels" / "python"
```

Rõ ràng hơn:

```text
https://example.com/novels/python
```

---

# 12. Một lỗi người mới thường gặp

Không nên làm:

```python
url = URL("https://example.com")
url += "/novels"
```

Vì `URL` immutable.

Hãy làm:

```python
url = url / "novels"
```

hoặc:

```python
new_url = url / "novels"
```

---

# 13. `str(URL)`

Khi cần đưa URL cho thư viện khác, thường chỉ cần:

```python
url = URL("https://example.com/books?page=2")

print(str(url))
```

Kết quả:

```text
https://example.com/books?page=2
```

Ví dụ với `httpx`:

```python
import httpx
from yarl import URL


url = URL("https://example.com")


response = httpx.get(str(url))

print(response.status_code)
```

Trong crawler của bạn, ta có thể giữ:

```python
URL
```

ở tầng domain/application và chỉ chuyển thành string tại boundary nếu thư viện bên ngoài cần string.

---

# 14. Mini project Buổi 1

Tạo:

```text
lesson_01/
└── main.py
```

Code:

```python
from yarl import URL


def main() -> None:
    base_url = URL("https://example.com")

    novel_url = base_url / "novel" / "dau-pha-thuong-khung"

    chapter_url = novel_url / "chuong-1"

    print("=" * 50)
    print("BASE URL")
    print("=" * 50)
    print(base_url)

    print()

    print("=" * 50)
    print("NOVEL URL")
    print("=" * 50)
    print(novel_url)

    print()

    print("=" * 50)
    print("CHAPTER URL")
    print("=" * 50)
    print(chapter_url)

    print()

    print("=" * 50)
    print("CHAPTER COMPONENTS")
    print("=" * 50)

    print("scheme  :", chapter_url.scheme)
    print("host    :", chapter_url.host)
    print("path    :", chapter_url.path)
    print("query   :", chapter_url.query)
    print("fragment:", chapter_url.fragment)


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python main.py
```

---

# 15. Bài tập

### Bài 1

Tạo:

```python
URL("https://example.com")
```

sau đó xây dựng:

```text
https://example.com/novels
https://example.com/novels/python
https://example.com/novels/python/chapter-10
```

chỉ bằng `/`.

---

### Bài 2

Cho URL:

```text
https://example.com:8080/novels/python?page=2#content
```

hãy in:

```text
scheme
host
port
path
query
fragment
```

---

### Bài 3 — crawler

Cho:

```python
BASE_URL = URL("https://example.com")
```

hãy tạo:

```text
https://example.com/truyen
https://example.com/truyen/python
https://example.com/truyen/python/chuong-1
https://example.com/truyen/python/chuong-2
https://example.com/truyen/python/chuong-3
```

**Không được nối URL bằng `+`.**

---

## Những gì cần nhớ sau Buổi 1

```text
yarl
 │
 └── URL
      │
      ├── scheme
      ├── host
      ├── port
      ├── path
      ├── query
      └── fragment
```

Và 3 nguyên tắc quan trọng:

```python
URL("https://example.com")
```

→ URL là **object**, không chỉ là string.

```python
url / "novel" / "chapter-1"
```

→ dùng `/` để xây dựng path.

```python
url.with_query(...)
```

→ URL **immutable**, thao tác tạo URL mới thay vì sửa URL cũ.

**Buổi 2** chúng ta sẽ đi sâu vào **`URL()` và toàn bộ cấu trúc URL**, bao gồm `scheme`, `host`, `port`, `path`, `query`, `fragment`, `user/password`, `origin`, `raw_path` và đặc biệt là cách `yarl` xử lý **URL encoding** — phần rất quan trọng đối với crawler.
