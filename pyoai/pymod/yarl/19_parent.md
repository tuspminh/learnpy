# Buổi 19 — `parent` trong `yarl`

Hôm nay chúng ta học cách **đi ngược lên URL cha** bằng:

```python
url.parent
```

Đây là một thao tác rất hữu ích khi làm **URL resolution, crawler, parser và xây URL tương đối**.

---

# 1. `parent` là gì?

Giả sử:

```text
https://example.com/novel/python/chapter/10
```

Path là:

```text
/novel/python/chapter/10
```

URL cha của nó là:

```text
https://example.com/novel/python/chapter
```

Tiếp tục:

```text
https://example.com/novel/python/chapter
                       ↓ parent

https://example.com/novel/python
```

Tiếp:

```text
https://example.com/novel/python
                       ↓ parent

https://example.com/novel
```

---

# 2. Sử dụng `parent`

```python
from yarl import URL

url = URL("https://example.com/novel/python/chapter/10")

print(url.parent)
```

Kết quả:

```text
https://example.com/novel/python/chapter
```

Rất đơn giản:

```python
url.parent
```

---

# 3. Có thể gọi nhiều lần

```python
from yarl import URL

url = URL("https://example.com/novel/python/chapter/10")

print(url)
print(url.parent)
print(url.parent.parent)
print(url.parent.parent.parent)
```

Kết quả:

```text
https://example.com/novel/python/chapter/10
https://example.com/novel/python/chapter
https://example.com/novel/python
https://example.com/novel
```

Có thể hình dung:

```text
/novel/python/chapter/10
        ↑
/novel/python/chapter
        ↑
/novel/python
        ↑
/novel
```

---

# 4. `parent` chỉ thay đổi Path

Ví dụ URL đầy đủ:

```python
from yarl import URL

url = URL("https://example.com:8080/novel/python/chapter/10?page=2#content")

parent = url.parent

print(parent)
```

Kết quả:

```text
https://example.com:8080/novel/python/chapter?page=2#content
```

Ta thấy:

```text
scheme    giữ nguyên
host      giữ nguyên
port      giữ nguyên
query     giữ nguyên
fragment  giữ nguyên
path      đi lên một cấp
```

---

# 5. Kiểm tra từng thành phần

```python
from yarl import URL

url = URL("https://example.com:8080/novel/python/chapter/10?page=2#content")

parent = url.parent

print("Original")
print("scheme  :", url.scheme)
print("host    :", url.host)
print("port    :", url.port)
print("path    :", url.path)
print("query   :", url.query_string)
print("fragment:", url.fragment)

print("\nParent")
print("scheme  :", parent.scheme)
print("host    :", parent.host)
print("port    :", parent.port)
print("path    :", parent.path)
print("query   :", parent.query_string)
print("fragment:", parent.fragment)
```

Điểm cần nhớ:

> `parent` là một URL mới; URL gốc không bị thay đổi.

---

# 6. `parent` và `path`

Đây là cách tư duy rất quan trọng:

```text
URL
 │
 └── Path
      │
      ├── novel
      ├── python
      ├── chapter
      └── 10
```

Khi gọi:

```python
url.parent
```

ta bỏ segment cuối:

```text
10
```

còn:

```text
novel/python/chapter
```

---

# 7. `parent` khác `/`

Hai thao tác này ngược hướng nhau.

### `/` đi xuống

```python
url / "chapter" / "10"
```

Ví dụ:

```text
/novel/python
      ↓
/novel/python/chapter
      ↓
/novel/python/chapter/10
```

### `parent` đi lên

```python
url.parent
```

Ví dụ:

```text
/novel/python/chapter/10
      ↓
/novel/python/chapter
      ↓
/novel/python
```

Có thể nhớ:

```text
       /
       ↓
     child
       ↑
    parent
```

---

# 8. `parent` + `/`

Hai thao tác này có thể kết hợp.

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/novel/python/chapter/10")

parent = url.parent

new_url = parent / "11"

print(new_url)
```

Kết quả:

```text
https://example.com/novel/python/chapter/11
```

Đây là pattern khá hữu ích:

```text
chapter/10
   ↓ parent
chapter/
   ↓ / "11"
chapter/11
```

---

# 9. Use case: lấy thư mục chapter

Giả sử:

```text
https://example.com/novel/python/chapter/100
```

Ta muốn URL chứa danh sách chapter:

```text
https://example.com/novel/python/chapter
```

Có thể:

```python
from yarl import URL

chapter_url = URL("https://example.com/novel/python/chapter/100")

chapter_list_url = chapter_url.parent

print(chapter_list_url)
```

Kết quả:

```text
https://example.com/novel/python/chapter
```

---

# 10. Use case: crawl cấu trúc website

Giả sử parser gặp:

```html
<a href="../chapter-10">Chapter 10</a>
```

và page hiện tại:

```text
https://example.com/novel/python/chapter/20
```

Ta cần biết base URL phù hợp.

URL hiện tại:

```text
https://example.com/novel/python/chapter/20
```

Parent:

```text
https://example.com/novel/python/chapter
```

Từ đó có thể kết hợp với URL resolution.

Đây là lý do `parent` rất hữu ích trong crawler.

---

# 11. Nhưng đừng nhầm `parent` với `join`

Đây là điểm quan trọng.

Giả sử:

```python
url = URL("https://example.com/novel/python/chapter/10")
```

Bạn muốn resolve:

```text
../chapter-20
```

Không nên tự làm:

```python
url.parent / "../chapter-20"
```

rồi giả định đó là URL cuối cùng.

Trong URL processing, tốt hơn là sử dụng cơ chế URL resolution phù hợp.

Ví dụ với `join`:

```python
from yarl import URL

base = URL("https://example.com/novel/python/chapter/10")

result = base.join(URL("../chapter-20"))

print(result)
```

Mục đích:

```text
base URL
   +
relative URL
   ↓
absolute URL
```

`parent` là một công cụ để **truy cập cấp cha**, không phải replacement cho URL resolver.

---

# 12. `parent` trong Novel Parser

Giả sử parser đang xử lý:

```text
https://example.com/truyen/python-lap-trinh/chuong-10
```

Ta có:

```python
from yarl import URL

chapter_url = URL("https://example.com/truyen/python-lap-trinh/chuong-10")

novel_url = chapter_url.parent

print(novel_url)
```

Kết quả:

```text
https://example.com/truyen/python-lap-trinh
```

Trong **một số website**, cấu trúc URL có thể như vậy:

```text
Novel
  ↓
/truyen/python-lap-trinh

Chapter
  ↓
/truyen/python-lap-trinh/chuong-10
```

Khi đó:

```python
chapter_url.parent
```

có thể giúp tìm URL novel.

Nhưng nhớ:

> Đây chỉ đúng nếu website thực sự có cấu trúc URL như vậy.

Không được giả định mọi website đều tổ chức URL theo cấu trúc này.

---

# 13. Đây là lý do Plugin Parser phải có policy riêng

Trong kiến trúc crawler của bạn:

```text
Generic Parser
      ↓
Plugin
      ↓
Website-specific URL rules
```

Ví dụ:

```python
class NovelURLResolver:
    def novel_from_chapter(self, chapter_url: URL) -> URL:
        return chapter_url.parent
```

Cách này chỉ phù hợp với website có:

```text
/novel-slug/chapter
```

Nếu website khác:

```text
/read?id=12345
```

thì:

```python
chapter_url.parent
```

không thể suy ra novel URL.

Đây là một ví dụ rất hay về:

> **Không nên biến một quy luật của website thành quy luật của framework.**

---

# 14. `parent` nhiều cấp

Có thể viết:

```python
url.parent.parent
```

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/a/b/c/d")

print(url)
print(url.parent)
print(url.parent.parent)
print(url.parent.parent.parent)
```

Kết quả:

```text
https://example.com/a/b/c/d
https://example.com/a/b/c
https://example.com/a/b
https://example.com/a
```

---

# 15. Không nên chain quá dài

Đoạn này:

```python
url.parent.parent.parent.parent
```

có thể khó đọc.

Tốt hơn:

```python
parent = url.parent
grandparent = parent.parent
```

hoặc tạo helper:

```python
def parent_url(url: URL, levels: int = 1) -> URL:
    result = url

    for _ in range(levels):
        result = result.parent

    return result
```

Sử dụng:

```python
from yarl import URL

url = URL("https://example.com/a/b/c/d")

print(parent_url(url, 1))
print(parent_url(url, 2))
print(parent_url(url, 3))
```

Kết quả:

```text
https://example.com/a/b/c
https://example.com/a/b
https://example.com/a
```

---

# 16. Complete example: `parent_url()`

```python
from yarl import URL


def parent_url(url: URL, levels: int = 1) -> URL:
    if levels < 0:
        raise ValueError("levels must be >= 0")

    result = url

    for _ in range(levels):
        result = result.parent

    return result


def main():
    url = URL("https://example.com/novel/python/chapter/10?page=2#content")

    print("Original:")
    print(url)

    print("\n1 level:")
    print(parent_url(url, 1))

    print("\n2 levels:")
    print(parent_url(url, 2))

    print("\n3 levels:")
    print(parent_url(url, 3))


if __name__ == "__main__":
    main()
```

Kết quả:

```text
Original:
https://example.com/novel/python/chapter/10?page=2#content

1 level:
https://example.com/novel/python/chapter?page=2#content

2 levels:
https://example.com/novel/python?page=2#content

3 levels:
https://example.com/novel?page=2#content
```

---

# 17. Một điều cần chú ý: query và fragment

Bạn có thể thấy ví dụ trên cho rằng:

```text
? page=2
# content
```

vẫn xuất hiện khi đi lên `parent`.

Điều này rất đáng lưu ý khi xây URL normalization.

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/a/b/c?page=2#content")

parent = url.parent

print(parent)
```

Nếu mục đích của bạn là **network URL**, có thể cần policy riêng:

```python
network_url = url.parent.with_fragment(None)
```

Nếu query cũng không còn ý nghĩa sau khi thay đổi path, bạn phải quyết định rõ ràng có xóa nó hay không.

Không nên để việc này xảy ra một cách ngẫu nhiên.

---

# 18. `parent` không phải filesystem `Path.parent`

Bạn sẽ thấy API khá giống `pathlib`:

```python
from pathlib import Path

path = Path("data/novel/python/chapter/10.html")

print(path.parent)
```

và:

```python
from yarl import URL

url = URL("https://example.com/novel/python/chapter/10")

print(url.parent)
```

Ý tưởng tương tự:

```text
pathlib.Path
    ↓
filesystem hierarchy

yarl.URL
    ↓
URL path hierarchy
```

Nhưng chúng thuộc **hai domain khác nhau**.

---

# 19. Complete crawler example

Giả sử ta có một chapter URL:

```python
from yarl import URL


def get_novel_url_from_chapter(chapter_url: URL) -> URL:
    """
    Chỉ phù hợp với website có cấu trúc:

    /novel-slug/chapter-slug
    """
    return chapter_url.parent


def main():
    chapter_url = URL("https://example.com/novel/python/chapter-10")

    novel_url = get_novel_url_from_chapter(chapter_url)

    print("Chapter URL:")
    print(chapter_url)

    print("\nNovel URL:")
    print(novel_url)


if __name__ == "__main__":
    main()
```

Kết quả:

```text
Chapter URL:
https://example.com/novel/python/chapter-10

Novel URL:
https://example.com/novel/python
```

---

# 20. Kết hợp với các kiến thức trước

Bây giờ chúng ta đã có một nhóm URL manipulation khá mạnh:

```text
with_scheme()
with_host()
with_port()
with_path()
with_query()
with_fragment()
with_name()
with_suffix()
parent
```

Ví dụ:

```python
from yarl import URL

url = URL("http://old.example.com:8000/old/chapter-10.html?page=2#content")

result = (
    url.with_scheme("https")
    .with_host("example.com")
    .with_port(443)
    .with_name("chapter-20.html")
    .with_fragment(None)
)

print(result)
```

Kết quả:

```text
https://example.com:443/old/chapter-20.html?page=2
```

Sau đó:

```python
parent = result.parent
```

ta có:

```text
https://example.com:443/old?page=2
```

---

# 21. Một helper thực tế hơn

Trong crawler, ta có thể viết:

```python
from yarl import URL


def get_directory_url(url: URL) -> URL:
    """
    Lấy URL directory/parent của resource.
    """
    return url.parent


def get_network_url(url: URL) -> URL:
    """
    Chuẩn bị URL cho network request.
    Fragment không cần thiết.
    """
    return url.with_fragment(None)


def get_parent_network_url(url: URL) -> URL:
    return url.parent.with_fragment(None)
```

Ví dụ:

```python
url = URL("https://example.com/novel/python/chapter/10#content")

print(get_directory_url(url))
print(get_network_url(url))
print(get_parent_network_url(url))
```

---

# 22. Những điều cần nhớ

### `parent`

```python
url.parent
```

→ đi lên một cấp Path.

---

### `/`

```python
url / "chapter"
```

→ đi xuống / thêm Path segment.

---

### `with_path()`

```python
url.with_path("/new/path")
```

→ thay toàn bộ Path.

---

### `with_name()`

```python
url.with_name("chapter-20.html")
```

→ thay tên cuối cùng.

---

### `with_suffix()`

```python
url.with_suffix(".json")
```

→ thay extension.

---

# 23. Mô hình tư duy

Hãy nhớ URL như một cây:

```text
https://example.com
│
└── novel
    │
    └── python
        │
        └── chapter
            │
            ├── 1
            ├── 2
            ├── 3
            └── 10
```

Từ:

```text
chapter/10
```

đi lên:

```python
url.parent
```

→

```text
chapter
```

Thêm:

```python
url.parent / "11"
```

→

```text
chapter/11
```

Đây là tư duy rất hữu ích khi làm crawler.

---

# 24. Bài tập Buổi 19

Cho:

```python
from yarl import URL

url = URL("https://example.com/novel/python/chapter/10?page=2#content")
```

### Bài 1

Lấy URL cha:

```text
https://example.com/novel/python/chapter?page=2#content
```

---

### Bài 2

Lấy URL cha **2 cấp**:

```text
https://example.com/novel/python?page=2#content
```

---

### Bài 3

Từ URL chapter 10:

```text
https://example.com/novel/python/chapter/10
```

tạo URL chapter 11 bằng:

```python
url.parent / "11"
```

---

### Bài 4

Viết:

```python
def get_novel_url(chapter_url: URL) -> URL: ...
```

với input:

```text
https://example.com/novel/python/chapter/10
```

output:

```text
https://example.com/novel/python/chapter
```

---

### Bài 5 — crawler

Viết:

```python
def prepare_parent_request_url(url: URL) -> URL: ...
```

sao cho:

```text
input:
https://example.com/novel/python/chapter/10?page=2#content
```

output:

```text
https://example.com/novel/python/chapter?page=2
```

Tức là:

```text
parent
   ↓
strip fragment
```

---

## Tóm tắt

```python
url.parent
```

là API để **đi lên một cấp trong URL path**.

Ví dụ:

```text
/a/b/c
 ↓ parent
/a/b
 ↓ parent
/a
```

Trong Novel Crawler, nó hữu ích cho:

* tìm URL cha;
* phân tích cấu trúc website;
* xây URL từ hierarchy;
* xử lý chapter/novel URL;
* kết hợp với `/`;
* hỗ trợ URL resolver.

Nhưng cần nhớ:

> `parent` chỉ phản ánh **cấu trúc Path**. Nó không đảm bảo URL cha thực sự là một resource hợp lệ trên website.

**Buổi 20 — `origin()`** sẽ kết thúc Phần II. Chúng ta sẽ học cách lấy phần **scheme + host + port** của URL, rất hữu ích cho việc xác định **domain/origin, proxy policy, same-origin, crawler scope và URL security policy**.
