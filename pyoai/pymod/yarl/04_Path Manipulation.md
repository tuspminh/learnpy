# Buổi 4 — Path Manipulation trong `yarl`

Hôm nay tập trung vào **path** — phần cực kỳ quan trọng khi dùng `yarl` cho crawler.

Mục tiêu:

```text
URL
 │
 └── Path
      ├── /novels
      ├── /novels/python
      ├── /novels/python/chapter-1
      ├── parent
      ├── name
      └── suffix
```

Sau bài này bạn sẽ có thể xử lý các URL như:

```text
https://example.com/novel/python/chapter-10
https://example.com/images/cover.jpg
https://example.com/files/book.epub
```

mà không cần thao tác string thủ công.

---

# 1. Path là gì?

Cho URL:

```python
from yarl import URL

url = URL("https://example.com/novels/python/chapter-10")

print(url.path)
```

Kết quả:

```text
/novels/python/chapter-10
```

Ta có:

```text
https://example.com/novels/python/chapter-10
                    └───────────────┘
                           path
```

---

# 2. `parts`

`path` có thể được chia thành các phần:

```python
from yarl import URL

url = URL("https://example.com/novels/python/chapter-10")

print(url.parts)
```

Bạn sẽ nhận được dạng tuple tương tự:

```text
('/', 'novels', 'python', 'chapter-10')
```

Điểm quan trọng:

```python
url.parts
```

cho ta các **path component**, rất tiện khi cần phân tích cấu trúc URL.

Ví dụ:

```python
parts = url.parts

for part in parts:
    print(part)
```

---

# 3. Dùng `/` để xây dựng path

Đây là API mà bạn sẽ dùng rất thường xuyên.

```python
from yarl import URL

base = URL("https://example.com")

url = base / "novels" / "python" / "chapter-1"

print(url)
```

Kết quả:

```text
https://example.com/novels/python/chapter-1
```

Có thể xây từng bước:

```python
base = URL("https://example.com")

novels = base / "novels"
python = novels / "python"
chapter = python / "chapter-1"

print(novels)
print(python)
print(chapter)
```

---

# 4. Vì sao `/` tốt hơn nối string?

Không nên:

```python
url = "https://example.com" + "/novels/" + "python/" + "chapter-1"
```

Vì phải tự quản lý `/`.

Với `yarl`:

```python
url = URL("https://example.com") / "novels" / "python" / "chapter-1"
```

Code thể hiện đúng ý nghĩa:

```text
base
 ↓
novels
 ↓
python
 ↓
chapter-1
```

---

# 5. `parent`

Đây là API rất hữu ích khi xử lý URL.

Cho:

```python
from yarl import URL

url = URL("https://example.com/novels/python/chapter-10")

print(url.parent)
```

Kết quả tương tự:

```text
https://example.com/novels/python
```

Tức là:

```text
/novels/python/chapter-10
                  ↓
/novels/python
```

---

# 6. Đi lên nhiều cấp

```python
url = URL("https://example.com/a/b/c/d")

print(url)
print(url.parent)
print(url.parent.parent)
print(url.parent.parent.parent)
```

Ta có:

```text
https://example.com/a/b/c/d
https://example.com/a/b/c
https://example.com/a/b
https://example.com/a
```

Vì URL immutable nên không có gì bị thay đổi.

---

# 7. `name`

Lấy component cuối cùng của path:

```python
from yarl import URL

url = URL("https://example.com/novels/python/chapter-10")

print(url.name)
```

Kết quả:

```text
chapter-10
```

Có thể hiểu:

```text
/novels/python/chapter-10
                       ↑
                      name
```

---

# 8. Ví dụ với image

```python
from yarl import URL

url = URL("https://example.com/images/cover.jpg")

print(url.name)
```

Kết quả:

```text
cover.jpg
```

---

# 9. `suffix`

Với:

```python
url = URL("https://example.com/images/cover.jpg")

print(url.suffix)
```

Kết quả:

```text
.jpg
```

Đây rất hữu ích khi crawler tải file.

Ví dụ:

```python
suffix = url.suffix

if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
    print("Image")
```

---

# 10. `stem`

Ngoài `suffix`, path cuối còn có `stem`.

```python
from yarl import URL

url = URL("https://example.com/images/cover.jpg")

print("name  :", url.name)
print("stem  :", url.stem)
print("suffix:", url.suffix)
```

Kết quả:

```text
name  : cover.jpg
stem  : cover
suffix: .jpg
```

Mô hình:

```text
cover.jpg
└───┬──┘
    │
   name

cover
└──┘
stem

.jpg
 └─┘
suffix
```

---

# 11. `with_name()`

Thay tên file/path cuối:

```python
from yarl import URL

url = URL("https://example.com/images/cover.jpg")

new_url = url.with_name("cover.webp")

print(url)
print(new_url)
```

Kết quả:

```text
https://example.com/images/cover.jpg
https://example.com/images/cover.webp
```

URL cũ không thay đổi.

---

# 12. `with_name()` với chapter

Ví dụ:

```python
url = URL("https://example.com/novel/python/chapter-10")

new_url = url.with_name("chapter-11")

print(new_url)
```

Kết quả:

```text
https://example.com/novel/python/chapter-11
```

Điều này có thể dùng để xây chapter URL nếu website có cấu trúc ổn định.

---

# 13. `with_suffix()`

Thay extension:

```python
from yarl import URL

url = URL("https://example.com/images/cover.jpg")

new_url = url.with_suffix(".webp")

print(url)
print(new_url)
```

Kết quả:

```text
https://example.com/images/cover.jpg
https://example.com/images/cover.webp
```

---

# 14. `with_suffix()` khác `with_name()`

### `with_name()`

Thay **toàn bộ tên cuối**:

```python
url.with_name("cover.webp")
```

→

```text
/images/cover.webp
```

### `with_suffix()`

Chỉ thay **suffix**:

```python
url.with_suffix(".webp")
```

→

```text
/images/cover.webp
```

Ví dụ:

```python
url = URL("https://example.com/images/book-cover.jpg")

print(url.with_name("thumbnail.png"))
```

→

```text
/images/thumbnail.png
```

Còn:

```python
print(url.with_suffix(".webp"))
```

→

```text
/images/book-cover.webp
```

---

# 15. Path có query thì sao?

Đây là lý do nên dùng `yarl`.

```python
from yarl import URL

url = URL("https://example.com/images/cover.jpg?size=large")

print("path:", url.path)
print("name:", url.name)
print("suffix:", url.suffix)
print("query:", url.query)
```

Query được tách riêng:

```text
URL
 ├── path
 │    └── /images/cover.jpg
 │
 └── query
      └── size=large
```

Bạn không cần tự cắt string.

---

# 16. Path + query + fragment

Ví dụ:

```python
url = URL("https://example.com/images/cover.jpg?size=large#preview")

print("path     :", url.path)
print("name     :", url.name)
print("suffix   :", url.suffix)
print("query    :", url.query)
print("fragment :", url.fragment)
```

Các thành phần hoàn toàn độc lập.

Đây là một trong những lý do `URL` tốt hơn string.

---

# 17. Case study: Novel Crawler

Giả sử parser tìm được:

```text
https://example.com/novel/python/chapter-10
```

Ta có:

```python
from yarl import URL

chapter_url = URL("https://example.com/novel/python/chapter-10")

novel_url = chapter_url.parent

print(novel_url)
```

→

```text
https://example.com/novel/python
```

Đây là một pattern rất hữu ích:

```text
Chapter URL
     │
     │ .parent
     ↓
Novel URL
```

---

# 18. Lấy chapter name

```python
chapter_url = URL("https://example.com/novel/python/chapter-10")

chapter_slug = chapter_url.name

print(chapter_slug)
```

→

```text
chapter-10
```

Ta có thể đưa vào domain model:

```python
chapter_slug = chapter_url.name
```

---

# 19. Case study: image URL

Parser tìm thấy:

```text
https://cdn.example.com/images/python-cover.webp
```

Ta có:

```python
from yarl import URL

image_url = URL("https://cdn.example.com/images/python-cover.webp")

print("Filename:", image_url.name)
print("Stem    :", image_url.stem)
print("Suffix  :", image_url.suffix)
print("Parent  :", image_url.parent)
```

Kết quả:

```text
Filename: python-cover.webp
Stem    : python-cover
Suffix  : .webp
Parent  : https://cdn.example.com/images
```

---

# 20. Case study: đổi tên file download

Giả sử crawler muốn lưu:

```text
python-cover.webp
```

thành:

```text
python-cover-original.webp
```

Ta có:

```python
new_url = image_url.with_name("python-cover-original.webp")

print(new_url)
```

---

# 21. `joinpath()`

Ngoài `/`, `yarl` có:

```python
joinpath()
```

Ví dụ:

```python
from yarl import URL

base = URL("https://example.com")

url = base.joinpath(
    "novels",
    "python",
    "chapter-1",
)

print(url)
```

Kết quả:

```text
https://example.com/novels/python/chapter-1
```

Hai cách:

```python
base / "novels" / "python" / "chapter-1"
```

và:

```python
base.joinpath(
    "novels",
    "python",
    "chapter-1",
)
```

đều hữu ích.

Trong code crawler, tôi thường ưu tiên `/` khi path ngắn vì rất dễ đọc.

---

# 22. Relative URL

Đây là phần cực kỳ quan trọng đối với Parser.

Giả sử HTML có:

```html
<a href="chapter-2">
```

Ta lấy được:

```python
href = URL("chapter-2")
```

Đây là relative URL.

```python
print(href)
print(href.is_absolute())
```

Kết quả:

```text
chapter-2
False
```

---

# 23. URL tương đối và URL hiện tại

Giả sử trang hiện tại:

```python
current_url = URL("https://example.com/novel/python/chapter-1")
```

HTML:

```html
<a href="chapter-2">
```

Ta có:

```python
href = URL("chapter-2")
```

Nhưng:

```text
chapter-2
```

chưa phải URL mà Fetcher có thể request trực tiếp.

Ta cần resolve nó dựa trên URL hiện tại.

Đây là một chủ đề rất quan trọng và chúng ta sẽ dành riêng một bài cho **URL resolution**.

---

# 24. Đừng nhầm `parent` với URL resolution

Hai khái niệm khác nhau.

### `parent`

Đi lên một cấp:

```python
url.parent
```

Ví dụ:

```text
https://example.com/a/b/c
                         ↓
https://example.com/a/b
```

### Resolution

Biến:

```text
chapter-2
```

thành URL dựa trên:

```text
https://example.com/novel/python/chapter-1
```

Kết quả mong muốn:

```text
https://example.com/novel/python/chapter-2
```

Đây là **hai bài toán khác nhau**.

---

# 25. Một URL Path Helper

Để luyện tập, ta xây class nhỏ:

```python
from yarl import URL


class URLPathInspector:
    def __init__(self, url: URL):
        self.url = url

    def show(self) -> None:
        print("URL   :", self.url)
        print("Path  :", self.url.path)
        print("Parts :", self.url.parts)
        print("Parent:", self.url.parent)
        print("Name  :", self.url.name)
        print("Stem  :", self.url.stem)
        print("Suffix:", self.url.suffix)


def main() -> None:
    url = URL("https://example.com/novel/python/chapter-10.txt")

    inspector = URLPathInspector(url)
    inspector.show()


if __name__ == "__main__":
    main()
```

Đây là code hoàn chỉnh bạn có thể chạy ngay.

---

# 26. Xây Chapter URL

Một ví dụ rất gần với crawler:

```python
from yarl import URL


def make_chapter_url(
    novel_url: URL,
    chapter_slug: str,
) -> URL:
    return novel_url / chapter_slug


def main() -> None:
    novel_url = URL("https://example.com/novel/python")

    chapter_urls = [
        make_chapter_url(novel_url, "chapter-1"),
        make_chapter_url(novel_url, "chapter-2"),
        make_chapter_url(novel_url, "chapter-3"),
    ]

    for url in chapter_urls:
        print(url)


if __name__ == "__main__":
    main()
```

Kết quả:

```text
https://example.com/novel/python/chapter-1
https://example.com/novel/python/chapter-2
https://example.com/novel/python/chapter-3
```

---

# 27. Một điểm rất quan trọng: trailing slash

Hai URL:

```text
https://example.com/novel/python
```

và:

```text
https://example.com/novel/python/
```

không nhất thiết được coi là cùng một URL.

Ví dụ:

```python
from yarl import URL

a = URL("https://example.com/novel/python")
b = URL("https://example.com/novel/python/")

print(a == b)
```

Đừng tự giả định chúng giống nhau.

Đối với crawler, normalization policy phải được thiết kế **theo website**, không phải cứ xóa `/` cuối là đúng.

---

# 28. Pattern quan trọng cho crawler

Một pipeline URL có thể có dạng:

```text
HTML
 │
 │ href
 ↓
URL
 │
 ├── parse path
 │
 ├── validate
 │
 ├── resolve relative URL
 │
 ├── normalize
 │
 └── deduplicate
       │
       ↓
     Queue
       │
       ↓
    Fetcher
```

`yarl` sẽ đóng vai trò chủ yếu ở phần:

```text
href
 ↓
URL
 ↓
path/query/fragment
 ↓
URL manipulation
```

---

# 29. Những API hôm nay cần nhớ

```python
url.path
```

→ path

```python
url.parts
```

→ các path components

```python
url.parent
```

→ URL cha

```python
url.name
```

→ tên component cuối

```python
url.stem
```

→ tên không có suffix

```python
url.suffix
```

→ extension

```python
url.with_name(...)
```

→ thay tên cuối

```python
url.with_suffix(...)
```

→ thay extension

```python
url / "abc"
```

→ thêm path

```python
url.joinpath(...)
```

→ thêm nhiều path components

---

# 30. Sơ đồ ghi nhớ

```text
URL
│
├── path
│
├── parts
│
├── parent
│
├── name
│
├── stem
│
└── suffix
```

Thao tác:

```text
                  URL
                   │
       ┌───────────┼───────────┐
       ↓           ↓           ↓
      /         parent      with_path
   thêm path    đi lên       thay path
       │
       ├── with_name()
       │
       └── with_suffix()
```

---

# Bài tập Buổi 4

### Bài 1 — Path inspection

Cho:

```python
url = URL("https://example.com/novels/python/chapter-10.html")
```

In:

```text
path
parts
parent
name
stem
suffix
```

---

### Bài 2 — Xây chapter URL

Cho:

```python
base = URL("https://example.com")
```

Tạo:

```text
https://example.com/novels/python/chapter-1
https://example.com/novels/python/chapter-2
https://example.com/novels/python/chapter-3
```

chỉ sử dụng `yarl`.

---

### Bài 3 — Image

Cho:

```python
url = URL("https://cdn.example.com/images/book-cover.jpg")
```

Tạo URL mới:

```text
https://cdn.example.com/images/thumbnail.png
```

**Không dùng `replace()` của string.**

---

### Bài 4 — Novel Crawler

Cho:

```python
chapter_url = URL("https://example.com/novel/python/chapter-100")
```

Hãy lấy:

```text
Novel URL
Chapter slug
```

Kết quả mong muốn:

```text
Novel URL: https://example.com/novel/python
Chapter slug: chapter-100
```

---

### Bài 5 — Thử thách

Viết:

```python
def make_image_thumbnail(url: URL) -> URL: ...
```

Input:

```text
https://cdn.example.com/images/book-cover.jpg
```

Output:

```text
https://cdn.example.com/images/book-cover-thumb.jpg
```

Gợi ý: kết hợp:

```python
url.stem
url.suffix
url.with_name()
```

---

## Tiếp theo — Buổi 5

Buổi 5 sẽ đi vào **Query String**, một phần cực kỳ quan trọng của `yarl`:

```text
?page=2
?page=2&sort=new
?author=python&category=programming
```

Chúng ta sẽ học:

```python
url.query
url.query_string
url.with_query()
url.query.get()
url.query.getall()
```

và đặc biệt là **query có nhiều giá trị trùng key**, ví dụ:

```text
?tag=python&tag=asyncio&tag=crawler
```

Phần này rất hữu ích cho **pagination và filter trong Novel Crawler**.
