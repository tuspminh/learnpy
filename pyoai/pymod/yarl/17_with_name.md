# Buổi 17 — `with_name()` trong `yarl`

Hôm nay chúng ta học cách **thay đổi tên cuối cùng của Path** bằng:

```python
url.with_name(...)
```

Đây là phần nối trực tiếp với các kiến thức `path`, `name`, `suffix`, `stem`, `parent` mà chúng ta đã học.

---

# 1. `name` của URL là gì?

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/novels/python/chapter-10.html")

print(url.path)
print(url.name)
print(url.stem)
print(url.suffix)
```

Kết quả:

```text
/novels/python/chapter-10.html
chapter-10.html
chapter-10
.html
```

Có thể hình dung:

```text
https://example.com/novels/python/chapter-10.html
                                      │
                                      └── name
                                          chapter-10.html
```

`name` chính là **segment cuối cùng của Path**.

---

# 2. `with_name()` dùng để làm gì?

Cú pháp:

```python
new_url = url.with_name("new-name")
```

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/novels/python/chapter-10.html")

new_url = url.with_name("chapter-20.html")

print(new_url)
```

Kết quả:

```text
https://example.com/novels/python/chapter-20.html
```

Chỉ phần cuối:

```text
chapter-10.html
```

được thay bằng:

```text
chapter-20.html
```

---

# 3. So sánh với `with_path()`

Đây là điểm rất quan trọng.

### `with_path()`

Thay **toàn bộ Path**:

```python
url.with_path("/books/python/chapter-20.html")
```

### `with_name()`

Chỉ thay **name cuối cùng**:

```python
url.with_name("chapter-20.html")
```

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/novels/python/chapter-10.html")

a = url.with_path("/books/python/chapter-20.html")

b = url.with_name("chapter-20.html")

print("Original:", url)
print("with_path:", a)
print("with_name:", b)
```

Kết quả:

```text
Original:
https://example.com/novels/python/chapter-10.html

with_path:
https://example.com/books/python/chapter-20.html

with_name:
https://example.com/novels/python/chapter-20.html
```

Như vậy:

```text
with_path()
    ↓
thay cả đường dẫn

with_name()
    ↓
chỉ thay phần cuối
```

---

# 4. `with_name()` là immutable

Giống toàn bộ nhóm `with_*()` chúng ta đã học.

```python
from yarl import URL

url = URL("https://example.com/novels/python/chapter-10.html")

new_url = url.with_name("chapter-20.html")

print(url)
print(new_url)
```

Kết quả:

```text
https://example.com/novels/python/chapter-10.html
https://example.com/novels/python/chapter-20.html
```

URL gốc không thay đổi.

---

# 5. `name` sau khi thay đổi

```python
from yarl import URL

url = URL("https://example.com/novels/python/chapter-10.html")

new_url = url.with_name("chapter-20.html")

print("old name:", url.name)
print("new name:", new_url.name)
```

Kết quả:

```text
old name: chapter-10.html
new name: chapter-20.html
```

---

# 6. `with_name()` giữ nguyên Parent

Đây là đặc điểm quan trọng nhất.

```python
from yarl import URL

url = URL("https://example.com/novels/python/chapter-10.html")

print("parent:", url.parent)

new_url = url.with_name("chapter-20.html")

print("new parent:", new_url.parent)
```

Cả hai đều:

```text
https://example.com/novels/python
```

Nói cách khác:

```text
Original:

/novels/python/chapter-10.html
^^^^^^^^^^^^^^^^
     parent
             ^^^^^^^^^^^^^^^
                  name


with_name():

/novels/python/chapter-20.html
^^^^^^^^^^^^^^^^
     parent
             ^^^^^^^^^^^^^^^
                  name mới
```

---

# 7. `with_name()` và `stem`

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/chapter-10.html")

print("name  :", url.name)
print("stem  :", url.stem)
print("suffix:", url.suffix)
```

Kết quả:

```text
name  : chapter-10.html
stem  : chapter-10
suffix: .html
```

Nếu:

```python
new_url = url.with_name("chapter-20.txt")
```

thì:

```python
print(new_url.name)
print(new_url.stem)
print(new_url.suffix)
```

Kết quả:

```text
chapter-20.txt
chapter-20
.txt
```

---

# 8. `with_name()` không chỉ dành cho `.html`

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/files/data.json")

print(url.with_name("result.json"))
print(url.with_name("backup.json"))
print(url.with_name("image.jpg"))
print(url.with_name("chapter-100.txt"))
```

Kết quả:

```text
https://example.com/files/result.json
https://example.com/files/backup.json
https://example.com/files/image.jpg
https://example.com/files/chapter-100.txt
```

---

# 9. Thay đổi extension nên dùng `with_suffix()`

Nếu mục tiêu của bạn chỉ là:

```text
.html
   ↓
.txt
```

thì không nên dùng:

```python
url.with_name("chapter-10.txt")
```

Mà dùng:

```python
url.with_suffix(".txt")
```

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/chapter-10.html")

new_url = url.with_suffix(".txt")

print(new_url)
```

Kết quả:

```text
https://example.com/chapter-10.txt
```

---

# 10. `with_name()` vs `with_suffix()`

Rất dễ nhầm:

| Method          | Mục đích              |
| --------------- | --------------------- |
| `with_name()`   | Thay toàn bộ filename |
| `with_suffix()` | Thay extension        |
| `with_path()`   | Thay toàn bộ path     |
| `/`             | Thêm path segment     |

Ví dụ URL ban đầu:

```text
https://example.com/book/chapter-10.html
```

### `with_name()`

```python
url.with_name("chapter-20.html")
```

→

```text
https://example.com/book/chapter-20.html
```

---

### `with_suffix()`

```python
url.with_suffix(".txt")
```

→

```text
https://example.com/book/chapter-10.txt
```

---

### `with_path()`

```python
url.with_path("/new/path/file.html")
```

→

```text
https://example.com/new/path/file.html
```

---

# 11. Query và Fragment vẫn được giữ

Đây là điều rất hay của `with_name()`.

```python
from yarl import URL

url = URL("https://example.com/book/chapter-10.html?page=2#content")

new_url = url.with_name("chapter-20.html")

print(new_url)
```

Kết quả:

```text
https://example.com/book/chapter-20.html?page=2#content
```

Chúng ta chỉ thay:

```text
chapter-10.html
```

thành:

```text
chapter-20.html
```

Còn:

```text
?page=2
#content
```

vẫn giữ nguyên.

---

# 12. Chain với các method đã học

Có thể kết hợp:

```python
from yarl import URL

url = URL("http://old.example.com:8000/old/chapter-10.html?page=2#content")

new_url = (
    url.with_scheme("https")
    .with_host("example.com")
    .with_port(443)
    .with_name("chapter-20.html")
    .with_fragment(None)
)

print(new_url)
```

Kết quả:

```text
https://example.com/old/chapter-20.html?page=2
```

Ta có:

```text
with_scheme()
      ↓
with_host()
      ↓
with_port()
      ↓
with_name()
      ↓
with_fragment()
```

Đây chính là sức mạnh của immutable URL transformation.

---

# 13. Use case trong Novel Crawler

Giả sử crawler lưu HTML:

```text
chapters/
    chapter-001.html
    chapter-002.html
    chapter-003.html
```

URL:

```text
https://example.com/novel/python/chapter-001
```

Ta có thể tạo URL cho chapter tiếp theo:

```python
from yarl import URL

url = URL("https://example.com/novel/python/chapter-001")

next_url = url.with_name("chapter-002")

print(next_url)
```

Kết quả:

```text
https://example.com/novel/python/chapter-002
```

---

# 14. Nhưng cần phân biệt URL thật và tên file

Trong crawler thực tế, đây là một điểm kiến trúc quan trọng.

Giả sử:

```text
https://example.com/truyen/python-lap-trinh/chuong-10
```

`name` là:

```text
chuong-10
```

Ta có thể:

```python
url.with_name("chuong-11")
```

thành:

```text
https://example.com/truyen/python-lap-trinh/chuong-11
```

Nhưng **không phải website nào cũng thiết kế URL chapter tuần tự theo tên cuối**.

Ví dụ:

```text
/chuong-10
/chuong-10-abc123
/chapter?id=12345
```

Vì vậy:

```python
with_name()
```

là công cụ URL manipulation, **không phải thuật toán tìm chapter kế tiếp**.

Chapter parser vẫn phải xác định URL thực tế.

---

# 15. Một use case tốt hơn: đổi tên resource

Ví dụ server có:

```text
https://example.com/book/index.html
```

Bạn muốn URL:

```text
https://example.com/book/reader.html
```

Dùng:

```python
from yarl import URL

url = URL("https://example.com/book/index.html")

reader_url = url.with_name("reader.html")

print(reader_url)
```

Kết quả:

```text
https://example.com/book/reader.html
```

Đây là use case rất tự nhiên của `with_name()`.

---

# 16. URL không có filename truyền thống

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/novel/python/")

print("path:", url.path)
print("name:", url.name)
```

Trong trường hợp path kết thúc bằng `/`, URL có trailing slash và không nên suy nghĩ đơn giản rằng nó có một filename như:

```text
python.html
```

Đây là lý do chúng ta cần phân biệt:

```text
Path
Directory-like URL
Filename-like URL
```

`with_name()` phù hợp nhất khi URL có **path segment cuối cùng mà bạn muốn thay thế**.

---

# 17. Xây `ChapterURLBuilder`

Hãy áp dụng vào crawler.

```python
from yarl import URL


class ChapterURLBuilder:
    def __init__(self, base_url: URL):
        self.base_url = base_url

    def chapter(self, chapter_name: str) -> URL:
        return self.base_url.with_name(chapter_name)


def main():
    base_url = URL("https://example.com/novel/python/chapter-001")

    builder = ChapterURLBuilder(base_url)

    chapter_2 = builder.chapter("chapter-002")
    chapter_3 = builder.chapter("chapter-003")
    chapter_4 = builder.chapter("chapter-004")

    print(chapter_2)
    print(chapter_3)
    print(chapter_4)


if __name__ == "__main__":
    main()
```

Kết quả:

```text
https://example.com/novel/python/chapter-002
https://example.com/novel/python/chapter-003
https://example.com/novel/python/chapter-004
```

---

# 18. Nhưng có một vấn đề kiến trúc

Đừng biến:

```python
ChapterURLBuilder
```

thành nơi chứa mọi logic crawler.

Ví dụ **không nên**:

```python
class ChapterURLBuilder:
    def next_chapter(self):
        # parse HTML
        # tìm chapter
        # kiểm tra HTTP
        # database
        # retry
        # ...
        pass
```

Builder chỉ nên chịu trách nhiệm:

```text
input
  ↓
URL transformation
  ↓
URL
```

Ví dụ:

```python
class ChapterURLBuilder:
    def chapter(self, chapter_name: str) -> URL:
        return self.base_url.with_name(chapter_name)
```

Đúng tinh thần SOLID/DDD mà chúng ta đang theo đuổi.

---

# 19. Complete runnable example

Bạn có thể copy nguyên đoạn này chạy:

```python
from yarl import URL


def main():
    url = URL("https://example.com/novel/python/chapter-10.html?page=2#content")

    print("=" * 60)
    print("ORIGINAL")
    print("=" * 60)

    print("URL      :", url)
    print("path     :", url.path)
    print("parent   :", url.parent)
    print("name     :", url.name)
    print("stem     :", url.stem)
    print("suffix   :", url.suffix)
    print("query    :", url.query_string)
    print("fragment :", url.fragment)

    # --------------------------------------------------

    new_url = url.with_name("chapter-20.html")

    print("\n" + "=" * 60)
    print("WITH_NAME")
    print("=" * 60)

    print("Original :", url)
    print("New      :", new_url)

    print("\nComponents:")
    print("path     :", new_url.path)
    print("parent   :", new_url.parent)
    print("name     :", new_url.name)
    print("stem     :", new_url.stem)
    print("suffix   :", new_url.suffix)
    print("query    :", new_url.query_string)
    print("fragment :", new_url.fragment)

    # --------------------------------------------------

    txt_url = url.with_suffix(".txt")

    print("\n" + "=" * 60)
    print("WITH_SUFFIX")
    print("=" * 60)

    print(txt_url)

    # --------------------------------------------------

    clean_url = url.with_name("chapter-30.html").with_fragment(None)

    print("\n" + "=" * 60)
    print("CHAIN")
    print("=" * 60)

    print(clean_url)


if __name__ == "__main__":
    main()
```

Kết quả chính:

```text
ORIGINAL
https://example.com/novel/python/chapter-10.html?page=2#content

WITH_NAME
https://example.com/novel/python/chapter-20.html?page=2#content

WITH_SUFFIX
https://example.com/novel/python/chapter-10.txt?page=2#content

CHAIN
https://example.com/novel/python/chapter-30.html?page=2
```

---

# 20. Tổng kết Buổi 17

Nhớ 4 method liên quan đến Path:

```python
url.path
url.name
url.stem
url.suffix
```

và:

```python
url.with_path(...)
url.with_name(...)
url.with_suffix(...)
url.parent
```

Trong đó:

```text
with_path()
    → thay toàn bộ path

with_name()
    → thay path segment cuối

with_suffix()
    → thay extension

parent
    → lấy URL cha
```

Ví dụ:

```python
url = URL("https://example.com/book/chapter-10.html")
```

thì:

```python
url.with_path("/new/a.html")
```

→

```text
https://example.com/new/a.html
```

```python
url.with_name("chapter-20.html")
```

→

```text
https://example.com/book/chapter-20.html
```

```python
url.with_suffix(".txt")
```

→

```text
https://example.com/book/chapter-10.txt
```

---

## Bài tập Buổi 17

Cho:

```python
url = URL("https://example.com/novel/python/chapter-10.html?page=2#content")
```

Hãy viết code tạo ra:

### 1.

```text
https://example.com/novel/python/chapter-20.html?page=2#content
```

### 2.

```text
https://example.com/novel/python/chapter-10.txt?page=2#content
```

### 3.

```text
https://example.com/novel/python/chapter-20.txt?page=2
```

### 4.

Viết:

```python
def rename_chapter(url: URL, name: str) -> URL: ...
```

sao cho:

```python
rename_chapter(url, "chapter-99.html")
```

trả về:

```text
https://example.com/novel/python/chapter-99.html?page=2#content
```

---

**Buổi 18 — `with_suffix()`** sẽ đi sâu riêng vào việc thay đổi extension, xử lý `.html`, `.txt`, `.json`, `.jpg`, trường hợp file không có suffix và cách ứng dụng vào **lưu HTML/chapter/image trong Novel Crawler**.
