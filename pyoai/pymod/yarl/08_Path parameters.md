# Buổi 8 — Path Parameters với `yarl`

Ở buổi này chúng ta học cách đưa **tham số động vào path URL**.

Đây là thứ xuất hiện liên tục trong crawler:

```text
/novel/{slug}
/chapter/{chapter_id}
/book/{book_id}
/page/{page_number}
```

Ví dụ:

```text
/novel/kiem-hiep
/chapter/123
```

Thay vì nối string thủ công, ta dùng `yarl.URL`.

---

## 1. Path parameter là gì?

Giả sử website có URL:

```text
https://example.com/novel/kiem-hiep
```

Trong đó:

```text
https://example.com
       │
       └── /novel/kiem-hiep
             │      │
             │      └── slug = "kiem-hiep"
             │
             └── resource = novel
```

Ta có thể coi:

```text
/novel/{slug}
```

là một URL template.

Với:

```python
slug = "kiem-hiep"
```

ta tạo:

```text
/novel/kiem-hiep
```

---

# 2. Cách đơn giản nhất với `yarl`

```python
from yarl import URL

base_url = URL("https://example.com")

slug = "kiem-hiep"

url = base_url / "novel" / slug

print(url)
```

Kết quả:

```text
https://example.com/novel/kiem-hiep
```

Đây chính là path parameter.

---

# 3. Parameter có thể là số

Ví dụ chapter:

```python
from yarl import URL

base_url = URL("https://example.com")

chapter_id = 123

url = (
    base_url
    / "chapter"
    / str(chapter_id)
)

print(url)
```

Kết quả:

```text
https://example.com/chapter/123
```

Lưu ý:

`yarl` xây path từ string-like segment, vì vậy khi dùng số nên chủ động:

```python
str(chapter_id)
```

---

# 4. Novel crawler: `novel_id`

Giả sử database lưu:

```python
novel_id = 12345
```

URL website:

```text
https://example.com/novel/12345
```

Ta viết:

```python
from yarl import URL

BASE_URL = URL("https://example.com")

novel_id = 12345

novel_url = (
    BASE_URL
    / "novel"
    / str(novel_id)
)

print(novel_url)
```

---

# 5. Novel crawler: `slug`

Nhiều website dùng slug:

```text
https://example.com/truyen/kiem-hiep
```

Code:

```python
from yarl import URL

BASE_URL = URL("https://example.com")

slug = "kiem-hiep"

url = BASE_URL / "truyen" / slug

print(url)
```

Kết quả:

```text
https://example.com/truyen/kiem-hiep
```

---

# 6. Chapter number

Ví dụ:

```text
https://example.com/truyen/kiem-hiep/chuong-100
```

Ta có:

```python
from yarl import URL

BASE_URL = URL("https://example.com")

novel_slug = "kiem-hiep"
chapter_no = 100

url = (
    BASE_URL
    / "truyen"
    / novel_slug
    / f"chuong-{chapter_no}"
)

print(url)
```

Kết quả:

```text
https://example.com/truyen/kiem-hiep/chuong-100
```

Ở đây:

```python
f"chuong-{chapter_no}"
```

tạo ra một **path segment hoàn chỉnh**.

Sau đó:

```python
base / "truyen" / novel_slug / segment
```

---

# 7. Không nên nối URL bằng string

Cách dễ thấy:

```python
url = (
    "https://example.com/"
    + "truyen/"
    + novel_slug
    + "/chuong-"
    + str(chapter_no)
)
```

Không nên.

Dùng:

```python
url = (
    URL("https://example.com")
    / "truyen"
    / novel_slug
    / f"chuong-{chapter_no}"
)
```

Code dễ đọc hơn rất nhiều.

---

# 8. Parameter chứa Unicode

Đây là lúc `yarl` thực sự hữu ích.

Ví dụ:

```python
from yarl import URL

BASE_URL = URL("https://example.com")

slug = "tiên-hiệp"

url = BASE_URL / "truyen" / slug

print(url)
```

`yarl` sẽ xử lý việc encode URL khi serialize.

Ta có thể xem:

```python
print(url.path)
```

và:

```python
print(url.raw_path)
```

`path` phù hợp khi muốn làm việc với giá trị path ở dạng dễ đọc.

`raw_path` cho ta representation đã encoded.

---

# 9. Parameter chứa khoảng trắng

Ví dụ:

```python
from yarl import URL

base = URL("https://example.com")

category = "truyện chữ"

url = base / "category" / category

print(url)
```

Không nên tự làm:

```python
category.replace(" ", "%20")
```

Hãy để `yarl` xử lý encoding.

---

# 10. Parameter chứa ký tự đặc biệt

Ví dụ:

```python
slug = "python&asyncio"
```

Ta có:

```python
from yarl import URL

url = (
    URL("https://example.com")
    / "search"
    / "python&asyncio"
)

print(url)
```

Ở đây `"python&asyncio"` là **một path segment**.

Điều này rất quan trọng.

`&` trong path không có cùng vai trò với `&` trong query.

Ví dụ:

```text
/path/python%26asyncio
```

khác với:

```text
/search?tag=python&tag=asyncio
```

---

# 11. Path parameter khác query parameter

Đây là điểm phải phân biệt rõ.

### Path parameter

```text
/novel/kiem-hiep
```

Code:

```python
url / "novel" / "kiem-hiep"
```

### Query parameter

```text
/novel?slug=kiem-hiep
```

Code:

```python
url.with_query(slug="kiem-hiep")
```

Hai URL có ý nghĩa khác nhau.

---

# 12. Ví dụ so sánh

```python
from yarl import URL

base = URL("https://example.com")

path_url = (
    base
    / "novel"
    / "kiem-hiep"
)

query_url = (
    base
    / "novel"
).with_query(
    slug="kiem-hiep"
)

print(path_url)
print(query_url)
```

Kết quả:

```text
https://example.com/novel/kiem-hiep
https://example.com/novel?slug=kiem-hiep
```

---

# 13. Nhiều path parameters

Website có thể có:

```text
/author/{author_id}/novel/{novel_id}/chapter/{chapter_id}
```

Ví dụ:

```text
/author/10/novel/200/chapter/300
```

Code:

```python
from yarl import URL

BASE_URL = URL("https://example.com")

author_id = 10
novel_id = 200
chapter_id = 300

url = (
    BASE_URL
    / "author"
    / str(author_id)
    / "novel"
    / str(novel_id)
    / "chapter"
    / str(chapter_id)
)

print(url)
```

---

# 14. Path parameter từ object

Giả sử:

```python
from dataclasses import dataclass


@dataclass
class Novel:
    id: int
    slug: str
```

Ta có:

```python
novel = Novel(
    id=123,
    slug="kiem-hiep",
)
```

Xây URL:

```python
from yarl import URL


BASE_URL = URL("https://example.com")

url = (
    BASE_URL
    / "novel"
    / novel.slug
)

print(url)
```

---

# 15. Chapter object

```python
from dataclasses import dataclass


@dataclass
class Chapter:
    number: int
    slug: str
```

Ví dụ:

```python
chapter = Chapter(
    number=100,
    slug="chuong-100",
)
```

URL:

```python
url = (
    BASE_URL
    / "novel"
    / novel.slug
    / chapter.slug
)
```

Kết quả:

```text
https://example.com/novel/kiem-hiep/chuong-100
```

---

# 16. Tạo function chuyên biệt

Thay vì rải logic khắp project:

```python
BASE_URL / "novel" / slug
```

ta có thể gom lại:

```python
from yarl import URL


BASE_URL = URL("https://example.com")


def build_novel_url(slug: str) -> URL:
    return BASE_URL / "novel" / slug


def build_chapter_url(
    novel_slug: str,
    chapter_slug: str,
) -> URL:
    return (
        BASE_URL
        / "novel"
        / novel_slug
        / chapter_slug
    )
```

Test:

```python
print(
    build_novel_url("kiem-hiep")
)

print(
    build_chapter_url(
        "kiem-hiep",
        "chuong-100",
    )
)
```

---

# 17. Parameter validation

Một URL builder tốt không nên nhận mọi thứ một cách mù quáng.

Ví dụ:

```python
def build_novel_url(slug: str) -> URL:
    if not slug:
        raise ValueError("slug cannot be empty")

    return BASE_URL / "novel" / slug
```

Test:

```python
print(
    build_novel_url("kiem-hiep")
)
```

nhưng:

```python
build_novel_url("")
```

sẽ báo:

```text
ValueError: slug cannot be empty
```

---

# 18. Kiểm tra chapter number

```python
def build_chapter_url(
    novel_slug: str,
    chapter_no: int,
) -> URL:

    if not novel_slug:
        raise ValueError(
            "novel_slug cannot be empty"
        )

    if chapter_no <= 0:
        raise ValueError(
            "chapter_no must be positive"
        )

    return (
        BASE_URL
        / "novel"
        / novel_slug
        / f"chuong-{chapter_no}"
    )
```

Test:

```python
print(
    build_chapter_url(
        "kiem-hiep",
        100,
    )
)
```

---

# 19. Một URL Builder thực tế hơn

```python
from yarl import URL


class NovelURLBuilder:

    def __init__(self, base_url: str):
        self.base_url = URL(base_url)

    def novel(
        self,
        slug: str,
    ) -> URL:

        if not slug:
            raise ValueError(
                "slug cannot be empty"
            )

        return (
            self.base_url
            / "novel"
            / slug
        )

    def chapter(
        self,
        novel_slug: str,
        chapter_slug: str,
    ) -> URL:

        if not novel_slug:
            raise ValueError(
                "novel_slug cannot be empty"
            )

        if not chapter_slug:
            raise ValueError(
                "chapter_slug cannot be empty"
            )

        return (
            self.base_url
            / "novel"
            / novel_slug
            / chapter_slug
        )


builder = NovelURLBuilder(
    "https://example.com"
)


novel_url = builder.novel(
    "kiem-hiep"
)

chapter_url = builder.chapter(
    "kiem-hiep",
    "chuong-100"
)

print(novel_url)
print(chapter_url)
```

Kết quả:

```text
https://example.com/novel/kiem-hiep
https://example.com/novel/kiem-hiep/chuong-100
```

---

# 20. Một vấn đề quan trọng: parameter chứa `/`

Giả sử:

```python
slug = "abc/def"
```

và:

```python
url = URL("https://example.com") / "novel" / slug
```

Bạn phải hiểu rằng `/` có ý nghĩa đặc biệt trong URL path.

Nếu dữ liệu của bạn **thực sự là một segment duy nhất** nhưng chứa `/`, bạn cần đặc biệt cẩn thận với cách encode dữ liệu đó.

Ví dụ ID:

```text
abc/def
```

có thể mang ý nghĩa:

```text
segment 1 = abc
segment 2 = def
```

chứ không còn đơn thuần là:

```text
segment = abc/def
```

Đây là một trong những lý do không nên tự xây URL bằng string.

---

# 21. Slug thường an toàn hơn ID tự do

Trong crawler, slug thường có dạng:

```text
kiem-hiep
tien-hiep
python-co-ban
truyen-1
```

Rất phù hợp:

```python
url = BASE_URL / "novel" / slug
```

Nhưng dữ liệu lấy trực tiếp từ database/user input cần được validation trước.

---

# 22. Path parameter + query

Một URL thực tế có thể chứa cả hai:

```text
https://example.com/novel/kiem-hiep?page=2
```

Ta xây:

```python
from yarl import URL

url = (
    URL("https://example.com")
    / "novel"
    / "kiem-hiep"
).with_query(
    page=2
)

print(url)
```

Kết quả:

```text
https://example.com/novel/kiem-hiep?page=2
```

Pattern:

```text
BASE
 │
 ├── / "novel"
 │
 └── / slug
       │
       ▼
     with_query()
```

---

# 23. Path parameter + fragment

Ví dụ:

```text
https://example.com/novel/abc#comments
```

Code:

```python
url = (
    URL("https://example.com")
    / "novel"
    / "abc"
).with_fragment(
    "comments"
)

print(url)
```

Kết quả:

```text
https://example.com/novel/abc#comments
```

Như vậy:

```text
/           → path
with_query  → query
with_fragment → fragment
```

---

# 24. Mapping vào Novel Crawler

Ta có thể thiết kế:

```text
Novel
│
├── id
├── slug
└── title

Chapter
│
├── id
├── novel_id
├── number
└── slug
```

URL:

```text
BASE_URL
   │
   └── /novel/{novel.slug}
             │
             └── /{chapter.slug}
```

Ví dụ:

```text
https://example.com
    /novel
    /kiem-hiep
    /chuong-100
```

Code:

```python
chapter_url = (
    BASE_URL
    / "novel"
    / novel.slug
    / chapter.slug
)
```

Rất rõ ràng.

---

# 25. Tách Domain khỏi yarl

Trong kiến trúc DDD/Clean Architecture, tôi **không khuyến khích** domain entity phải biết cách ghép URL:

```python
class Novel:

    def url(self):
        return URL(...) / ...
```

Thay vào đó:

```text
Domain
   │
   └── Novel
         │
         └── slug

Infrastructure/Application
   │
   └── NovelURLBuilder
         │
         └── yarl.URL
```

Ví dụ:

```python
@dataclass
class Novel:
    slug: str
    title: str
```

URL builder:

```python
class NovelURLBuilder:

    def __init__(self, base_url: URL):
        self.base_url = base_url

    def novel(self, novel: Novel) -> URL:
        return (
            self.base_url
            / "novel"
            / novel.slug
        )
```

Như vậy domain không bị phụ thuộc trực tiếp vào `yarl`.

Đây là cách rất phù hợp với kiến trúc crawler mà chúng ta đang hướng tới.

---

# 26. Mini Project cuối buổi

Hãy viết hoàn chỉnh:

```python
from dataclasses import dataclass
from yarl import URL


@dataclass
class Novel:
    slug: str
    title: str


@dataclass
class Chapter:
    slug: str
    number: int


class NovelURLBuilder:

    def __init__(self, base_url: str):
        self.base_url = URL(base_url)

    def novel(self, novel: Novel) -> URL:
        ...

    def chapter(
        self,
        novel: Novel,
        chapter: Chapter,
    ) -> URL:
        ...


novel = Novel(
    slug="kiem-hiep",
    title="Kiếm Hiệp",
)

chapter = Chapter(
    slug="chuong-100",
    number=100,
)

builder = NovelURLBuilder(
    "https://example.com"
)

print(builder.novel(novel))

print(
    builder.chapter(
        novel,
        chapter,
    )
)
```

Mục tiêu:

```text
https://example.com/novel/kiem-hiep

https://example.com/novel/kiem-hiep/chuong-100
```

---

# Tổng kết Buổi 8

Cốt lõi của bài này chỉ cần nhớ:

### Path parameter

```python
BASE_URL / "novel" / slug
```

### Numeric parameter

```python
BASE_URL / "chapter" / str(chapter_id)
```

### Dynamic segment

```python
BASE_URL / "novel" / slug / f"chuong-{chapter_no}"
```

### Path + query

```python
(
    BASE_URL
    / "novel"
    / slug
).with_query(page=2)
```

### Kiến trúc

```text
Domain
   │
   │ slug / id / chapter_no
   ▼
URL Builder
   │
   │ yarl
   ▼
URL
```

**Điểm đặc biệt quan trọng:** path parameter và query parameter là hai khái niệm khác nhau:

```text
/novel/kiem-hiep       ← PATH PARAMETER

/novel?slug=kiem-hiep  ← QUERY PARAMETER
```

Buổi tiếp theo **Buổi 9 — Query String cơ bản**, chúng ta sẽ đi sâu hơn vào việc tạo URL kiểu:

```text
/search?q=python&page=2
```

và cách `yarl` xử lý dictionary, keyword arguments và encoding của query.
