# Buổi 14 — `with_path()`

Hôm nay chúng ta học:

```python
URL.with_path()
```

Đây là một phương thức **rất quan trọng đối với crawler**, vì URL của truyện thường xuyên phải biến đổi giữa:

```text
/novel/...
/chapter/...
/truyen/...
/page/...
```

Điểm quan trọng nhất của buổi này:

> `with_path()` **thay thế toàn bộ path**, trong khi toán tử `/` của `yarl` dùng để **xây/nối path**.

---

# 1. Path là gì?

Ví dụ:

```text
https://example.com/novel/python/chapter-10?page=2
                  ^^^^^^^^^^^^^^^^^^^^^^^^^
                           path
```

Với:

```python
from yarl import URL

url = URL("https://example.com/novel/python/chapter-10?page=2")

print(url.path)
```

Kết quả:

```text
/novel/python/chapter-10
```

---

# 2. `with_path()` cơ bản

Cú pháp:

```python
new_url = url.with_path("/new/path")
```

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/novel/python")

new_url = url.with_path("/chapter/python-10")

print(url)
print(new_url)
```

Kết quả:

```text
https://example.com/novel/python
https://example.com/chapter/python-10
```

Chỉ path được thay đổi.

---

# 3. URL gốc không thay đổi

Giống:

```python
with_scheme()
with_host()
with_port()
```

`with_path()` cũng tạo URL mới.

```python
from yarl import URL

url = URL("https://example.com/novel/python")

url.with_path("/chapter/10")

print(url)
```

Vẫn là:

```text
https://example.com/novel/python
```

Muốn lấy URL mới:

```python
new_url = url.with_path("/chapter/10")
```

---

# 4. `with_path()` thay toàn bộ path

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/a/b/c")

new_url = url.with_path("/x/y")

print(new_url)
```

Kết quả:

```text
https://example.com/x/y
```

Không phải:

```text
https://example.com/a/b/c/x/y
```

Mà là:

```text
/a/b/c
    ↓
/x/y
```

---

# 5. Query không bị thay đổi

Đây là điểm rất hữu ích.

```python
from yarl import URL

url = URL("https://example.com/novel/python?page=2&sort=new")

new_url = url.with_path("/chapter/python-10")

print(new_url)
```

Kết quả:

```text
https://example.com/chapter/python-10?page=2&sort=new
```

Path thay đổi:

```text
/novel/python
        ↓
/chapter/python-10
```

Query giữ nguyên:

```text
page=2&sort=new
```

---

# 6. Fragment cũng giữ nguyên

```python
from yarl import URL

url = URL("https://example.com/novel/python?page=2#chapter-10")

new_url = url.with_path("/chapter/python-10")

print(new_url)
```

Kết quả:

```text
https://example.com/chapter/python-10?page=2#chapter-10
```

Ta có:

```text
scheme       giữ
host         giữ
port         giữ
path         thay
query        giữ
fragment     giữ
```

---

# 7. Ví dụ kiểm tra toàn bộ

```python
from yarl import URL


url = URL("https://example.com:8080/novel/python?page=2&sort=new#chapter-10")

new_url = url.with_path("/chapter/python-10")


print("Original:")
print(url)

print("\nNew:")
print(new_url)

print("\nComponents:")
print("scheme  :", new_url.scheme)
print("host    :", new_url.host)
print("port    :", new_url.port)
print("path    :", new_url.path)
print("query   :", new_url.query_string)
print("fragment:", new_url.fragment)
```

Kết quả:

```text
Original:
https://example.com:8080/novel/python?page=2&sort=new#chapter-10

New:
https://example.com:8080/chapter/python-10?page=2&sort=new#chapter-10

Components:
scheme  : https
host    : example.com
port    : 8080
path    : /chapter/python-10
query   : page=2&sort=new
fragment: chapter-10
```

---

# 8. `with_path()` và `/` khác nhau

Đây là phần quan trọng nhất của Buổi 14.

## `with_path()`

```python
url.with_path("/chapter/10")
```

Có nghĩa:

> **Thay toàn bộ path hiện tại bằng path mới.**

Ví dụ:

```text
https://example.com/novel/python
                     ↓
https://example.com/chapter/10
```

---

## Toán tử `/`

```python
url / "chapter" / "10"
```

Có nghĩa:

> **Xây/nối path.**

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com")

new_url = url / "chapter" / "10"

print(new_url)
```

Kết quả:

```text
https://example.com/chapter/10
```

---

# 9. Khi nào dùng `with_path()`?

Khi bạn **đã có URL và muốn thay toàn bộ path**.

Ví dụ:

```python
url = URL("https://example.com/novel/python")

chapter_url = url.with_path("/chapter/python-10")
```

---

# 10. Khi nào dùng `/`?

Khi bạn muốn **xây path từ các thành phần**.

Ví dụ:

```python
url = URL("https://example.com")

chapter_url = url / "novel" / "python" / "chapter-10"
```

Kết quả:

```text
https://example.com/novel/python/chapter-10
```

Tư duy:

```text
with_path()
    ↓
replace

/

    ↓
build / join
```

---

# 11. So sánh trực tiếp

```python
from yarl import URL


url = URL("https://example.com/novel/python")


a = url.with_path("/chapter/10")

b = url / "chapter" / "10"


print("A:", a)
print("B:", b)
```

Kết quả:

```text
A: https://example.com/chapter/10
B: https://example.com/novel/python/chapter/10
```

Đây là khác biệt rất lớn.

### `with_path()`

```text
/novel/python
      ↓
/chapter/10
```

### `/`

```text
/novel/python
      +
/chapter/10
      ↓
/novel/python/chapter/10
```

---

# 12. `with_path("")`

Ta có thể đặt path thành rỗng:

```python
from yarl import URL

url = URL("https://example.com/novel/python")

new_url = url.with_path("")

print(new_url)
```

URL trở về dạng host/root tương ứng.

Đây hữu ích khi muốn loại bỏ path hiện tại.

---

# 13. `with_path("/")`

Nếu muốn root path:

```python
from yarl import URL

url = URL("https://example.com/novel/python")

new_url = url.with_path("/")

print(new_url)
```

Kết quả:

```text
https://example.com/
```

Phân biệt:

```python
url.with_path("")
```

và:

```python
url.with_path("/")
```

Trong các URL có logic canonicalization, sự khác nhau giữa **empty path** và **root path `/`** có thể đáng quan tâm.

---

# 14. Path động trong Novel Crawler

Đây là use case quan trọng.

Giả sử ta có:

```python
novel_url = URL("https://truyen.example.com/novel/python")
```

Muốn tạo URL chapter:

```python
chapter_no = 10

chapter_url = novel_url.with_path(f"/chapter/{chapter_no}")

print(chapter_url)
```

Kết quả:

```text
https://truyen.example.com/chapter/10
```

---

# 15. Nhưng cẩn thận với URL structure của website

Không phải website nào cũng dùng:

```text
/chapter/10
```

Có website dùng:

```text
/novel/python/chuong-10
```

Có website:

```text
/doc-truyen/python/chuong-10
```

Có website:

```text
truyen-python/chuong-10.html
```

Vì vậy parser không nên giả định một format chung cho tất cả website.

Plugin của từng source nên quyết định URL structure.

Ví dụ:

```python
class TruyenExampleURLBuilder:
    def chapter_url(
        self,
        novel_url: URL,
        chapter_slug: str,
    ) -> URL:
        return novel_url.with_path(f"/novel/{chapter_slug}")
```

---

# 16. Path parameters

Một URL builder đơn giản:

```python
from yarl import URL


class NovelURLBuilder:
    def __init__(self, base_url: URL):
        self._base_url = base_url

    def novel(self, slug: str) -> URL:
        return self._base_url.with_path(f"/novel/{slug}")

    def chapter(
        self,
        novel_slug: str,
        chapter_slug: str,
    ) -> URL:
        return self._base_url.with_path(f"/novel/{novel_slug}/{chapter_slug}")
```

Sử dụng:

```python
builder = NovelURLBuilder(URL("https://example.com"))

novel_url = builder.novel("python")

chapter_url = builder.chapter(
    "python",
    "chapter-10",
)

print(novel_url)
print(chapter_url)
```

Kết quả:

```text
https://example.com/novel/python
https://example.com/novel/python/chapter-10
```

---

# 17. Nhưng khi path có nhiều segment, `/` thường đẹp hơn

Thay vì:

```python
return self._base_url.with_path(f"/novel/{novel_slug}/{chapter_slug}")
```

ta có thể:

```python
return self._base_url / "novel" / novel_slug / chapter_slug
```

Ví dụ:

```python
from yarl import URL


base_url = URL("https://example.com")

chapter_url = base_url / "novel" / "python" / "chapter-10"

print(chapter_url)
```

Kết quả:

```text
https://example.com/novel/python/chapter-10
```

Trong trường hợp **xây URL từ đầu**, tôi ưu tiên `/`.

---

# 18. `with_path()` phù hợp khi chuyển URL hiện có

Ví dụ parser nhận:

```text
https://example.com/old/path?page=2
```

Application muốn chuyển endpoint:

```text
https://example.com/api/novels?page=2
```

Ta làm:

```python
from yarl import URL

url = URL("https://example.com/old/path?page=2")

new_url = url.with_path("/api/novels")

print(new_url)
```

Kết quả:

```text
https://example.com/api/novels?page=2
```

---

# 19. `with_path()` + query

Một điểm rất hay:

```python
url = URL("https://example.com/search?q=python&page=2")

new_url = url.with_path("/novel/search")

print(new_url)
```

Kết quả:

```text
https://example.com/novel/search?q=python&page=2
```

Path thay đổi nhưng query được giữ lại.

Điều này rất tiện cho crawler pagination/filter.

---

# 20. Encoding path

URL có thể chứa Unicode.

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com")

new_url = url.with_path("/truyện/python")

print(new_url)
```

Khi in URL, yarl sẽ xử lý việc biểu diễn URL theo cơ chế encoding của nó.

Ta nên tránh tự:

```python
urllib.parse.quote(...)
```

rồi lại ghép string một cách thủ công nếu toàn bộ URL đã được quản lý bằng `yarl`.

Tư duy:

```text
Python string
       ↓
     yarl
       ↓
structured URL
       ↓
encoded representation
```

---

# 21. Path có dấu `/` bên trong

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com")

new_url = url.with_path("/novel/python/chapter-10")

print(new_url)
```

Kết quả:

```text
https://example.com/novel/python/chapter-10
```

`/` ở đây là delimiter của path.

Nếu bạn có dữ liệu động chứa ký tự đặc biệt, cần phân biệt:

```text
path segment
```

với:

```text
entire path
```

Đây là lý do xây URL bằng các segment:

```python
url / "novel" / slug / chapter
```

thường dễ kiểm soát hơn việc:

```python
url.with_path(f"/novel/{slug}/{chapter}")
```

---

# 22. Một lỗi thiết kế thường gặp

Không nên làm:

```python
def create_chapter_url(
    url: URL,
    chapter: str,
) -> URL:

    return url.with_path(f"/chapter/{chapter}")
```

nếu URL truyền vào có thể là:

```text
https://example.com/novel/python
```

và website thực tế yêu cầu:

```text
/novel/python/chapter-10
```

Vì `with_path()` sẽ **xóa path cũ**.

Nếu mục tiêu là thêm:

```text
/chapter-10
```

vào path hiện tại, hãy dùng:

```python
return url / chapter
```

Ví dụ:

```python
url = URL("https://example.com/novel/python")

chapter_url = url / "chapter-10"

print(chapter_url)
```

Kết quả:

```text
https://example.com/novel/python/chapter-10
```

---

# 23. Quy tắc rất dễ nhớ

Hãy nhớ câu này:

> **`with_path()` = thay path.**

> **`/` = nối path.**

Ví dụ:

```text
URL:
https://example.com/novel/python
```

### Thay

```python
url.with_path("/chapter/10")
```

→

```text
https://example.com/chapter/10
```

### Nối

```python
url / "chapter" / "10"
```

→

```text
https://example.com/novel/python/chapter/10
```

---

# 24. Kết hợp với những gì đã học

Đến thời điểm này chúng ta có:

```python
url.with_scheme("https")
url.with_host("mirror.example.com")
url.with_port(8443)
url.with_path("/novel/python")
```

Có thể chain:

```python
from yarl import URL


url = URL("http://example.com:8080/old/path?page=2")

new_url = (
    url.with_scheme("https")
    .with_host("mirror.example.com")
    .with_port(8443)
    .with_path("/novel/python")
)

print(new_url)
```

Kết quả:

```text
https://mirror.example.com:8443/novel/python?page=2
```

Query:

```text
page=2
```

vẫn được giữ.

---

# 25. Một `URLTransformer` nhỏ

Bây giờ ta đã đủ kiến thức để viết một abstraction nhỏ:

```python
from yarl import URL


class URLTransformer:
    @staticmethod
    def https(url: URL) -> URL:
        return url.with_scheme("https")

    @staticmethod
    def host(
        url: URL,
        host: str,
    ) -> URL:
        return url.with_host(host)

    @staticmethod
    def port(
        url: URL,
        port: int | None,
    ) -> URL:
        return url.with_port(port)

    @staticmethod
    def path(
        url: URL,
        path: str,
    ) -> URL:
        return url.with_path(path)
```

Sử dụng:

```python
url = URL("http://example.com:8080/old?page=2")

url = URLTransformer.https(url)
url = URLTransformer.host(
    url,
    "mirror.example.com",
)
url = URLTransformer.port(url, 8443)
url = URLTransformer.path(
    url,
    "/novel/python",
)

print(url)
```

Kết quả:

```text
https://mirror.example.com:8443/novel/python?page=2
```

Tuy nhiên, **chưa nên vội xây abstraction lớn**. Với `yarl`, API bản thân nó đã khá rõ ràng. Trong dự án thật, chỉ tạo lớp khi business logic thực sự cần.

---

# 26. Mini Project — Novel URL Builder

Tạo file:

```text
lesson_14.py
```

```python
from yarl import URL


class NovelURLBuilder:
    def __init__(self, base_url: URL):
        self._base_url = base_url

    def novel(self, slug: str) -> URL:
        return self._base_url / "novel" / slug

    def chapter(
        self,
        novel_slug: str,
        chapter_slug: str,
    ) -> URL:
        return self._base_url / "novel" / novel_slug / chapter_slug

    def replace_path(
        self,
        url: URL,
        path: str,
    ) -> URL:
        return url.with_path(path)


def main() -> None:

    base_url = URL("https://example.com")

    builder = NovelURLBuilder(base_url)

    novel_url = builder.novel("python")

    chapter_url = builder.chapter(
        "python",
        "chapter-10",
    )

    print("Novel:")
    print(novel_url)

    print("\nChapter:")
    print(chapter_url)

    print("\nReplace path:")
    print(builder.replace_path(novel_url, "/search"))


if __name__ == "__main__":
    main()
```

Kết quả:

```text
Novel:
https://example.com/novel/python

Chapter:
https://example.com/novel/python/chapter-10

Replace path:
https://example.com/search
```

---

# 27. Bài tập

### Bài 1 — Replace

Cho:

```python
url = URL("https://example.com/old/path?page=2")
```

Dùng `with_path()` tạo:

```text
https://example.com/new/path?page=2
```

---

### Bài 2 — So sánh

Cho:

```python
url = URL("https://example.com/novel/python")
```

Tạo hai URL:

```python
a = url.with_path("/chapter/10")
b = url / "chapter" / "10"
```

In cả hai và giải thích sự khác nhau.

---

### Bài 3 — Novel

Cho:

```python
novel_url = URL("https://example.com/novel/python")
```

Tạo:

```text
https://example.com/novel/python/chapter-15
```

bằng toán tử `/`.

---

### Bài 4 — Replace endpoint

Cho:

```text
https://example.com/novel/python?page=2#top
```

Dùng `with_path()` chuyển thành:

```text
https://example.com/search?page=2#top
```

Kiểm tra:

```python
query
fragment
```

vẫn giữ nguyên.

---

# Tổng kết Buổi 14

| Thao tác          | Phương thức     |
| ----------------- | --------------- |
| Thay scheme       | `with_scheme()` |
| Thay host         | `with_host()`   |
| Thay port         | `with_port()`   |
| Thay toàn bộ path | `with_path()`   |
| Nối path          | `/`             |
| Giữ URL gốc       | Có              |

Hai dòng quan trọng nhất:

```python
url.with_path("/new/path")
```

→ **thay toàn bộ path**

và:

```python
url / "new" / "path"
```

→ **nối thêm path**

Trong Novel Crawler, quy tắc thực tế là:

```text
ĐÃ CÓ URL
    │
    ├── muốn THAY path → with_path()
    │
    └── muốn THÊM segment → /
```

**Buổi 15 — `with_query()`** sẽ đi sâu vào việc thay đổi query string: thay toàn bộ query, thêm/đổi `page`, `sort`, `keyword`, filter, duplicate parameters và cách tránh mất các query parameter đang có.
