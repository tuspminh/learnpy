
# Buổi 35 — Image URL

Ở Buổi 34 chúng ta đã xử lý:

```text
Novel Detail HTML
        ↓
Chapter <a href>
        ↓
yarl.URL
        ↓
ChapterLink
```

Hôm nay xử lý **URL của ảnh**.

Trong Novel Crawler, ảnh có thể xuất hiện ở:

* ảnh bìa truyện
* ảnh minh họa trong chapter
* ảnh lazy-loading
* ảnh CDN
* ảnh dùng URL tương đối
* ảnh dùng URL tuyệt đối

Pipeline:

```text
HTML
 ↓
<img ...>
 ↓
image href/src
 ↓
yarl.URL
 ↓
absolute Image URL
 ↓
Fetcher
 ↓
Image Storage
```

---

# 1. `<img src>` chính là nguồn URL

Ví dụ:

```html
<img
    src="/uploads/cover/python.jpg"
    alt="Python"
/>
```

Trang:

```text
https://example.com/truyen/python
```

Ta cần tạo:

```text
https://example.com/uploads/cover/python.jpg
```

Dùng:

```python
from yarl import URL

page_url = URL(
    "https://example.com/truyen/python"
)

image_url = page_url.join(
    URL("/uploads/cover/python.jpg")
)

print(image_url)
```

Kết quả:

```text
https://example.com/uploads/cover/python.jpg
```

---

# 2. `<img>` khác `<a>`

Chapter:

```html
<a href="/chapter-1">
    Chương 1
</a>
```

Ảnh:

```html
<img src="/images/cover.jpg">
```

Vì vậy:

```text
<a href>
```

→ `href`

còn:

```text
<img src>
```

→ `src`

Selectolax:

```python
node.attributes.get("src")
```

---

# 3. Ví dụ cơ bản với selectolax

```python
from selectolax.parser import HTMLParser


html = """
<div class="content">

    <img src="/images/chapter-1-01.jpg">
    <img src="/images/chapter-1-02.jpg">
    <img src="/images/chapter-1-03.jpg">

</div>
"""

tree = HTMLParser(html)

for node in tree.css("img[src]"):
    src = node.attributes.get("src")

    print(src)
```

Kết quả:

```text
/images/chapter-1-01.jpg
/images/chapter-1-02.jpg
/images/chapter-1-03.jpg
```

---

# 4. Resolve bằng yarl

```python
from selectolax.parser import HTMLParser
from yarl import URL


page_url = URL(
    "https://example.com/truyen/python/chuong-1"
)

html = """
<div class="content">

    <img src="/images/chapter-1-01.jpg">
    <img src="/images/chapter-1-02.jpg">

</div>
"""

tree = HTMLParser(html)

for node in tree.css("img[src]"):

    src = node.attributes.get("src")

    if not src:
        continue

    image_url = page_url.join(
        URL(src.strip())
    )

    print(image_url)
```

Kết quả:

```text
https://example.com/images/chapter-1-01.jpg
https://example.com/images/chapter-1-02.jpg
```

---

# 5. Relative image URL

HTML:

```html
<img src="images/chapter-1.jpg">
```

Trang:

```text
https://example.com/truyen/python/chuong-1/
```

Ta dùng:

```python
page_url.join(
    URL("images/chapter-1.jpg")
)
```

→

```text
https://example.com/truyen/python/chuong-1/images/chapter-1.jpg
```

Yarl tự xử lý relative URL theo URL của document.

---

# 6. Root-relative

```html
<img src="/images/chapter-1.jpg">
```

→

```text
https://example.com/images/chapter-1.jpg
```

---

# 7. Absolute

```html
<img
    src="https://cdn.example.com/images/chapter-1.jpg"
>
```

Yarl:

```python
page_url.join(
    URL(
        "https://cdn.example.com/images/chapter-1.jpg"
    )
)
```

→

```text
https://cdn.example.com/images/chapter-1.jpg
```

---

# 8. CDN là trường hợp rất phổ biến

Novel website thường:

```text
Website
    ↓
https://truyen.example
```

nhưng ảnh:

```text
https://cdn.example.com/
```

Ví dụ:

```html
<img
    src="https://cdn.example.com/book/123/chapter-1.webp"
>
```

**Không được mặc định loại bỏ external URL.**

Vì image CDN hoàn toàn có thể là nguồn ảnh hợp lệ.

Đây là khác biệt với crawl page:

```text
Page URL
    → có thể giới hạn same-origin

Image URL
    → có thể cho phép CDN
```

Crawl policy quyết định việc này.

---

# 9. Image URL không nhất thiết nằm trong `src`

Đây là vấn đề thực tế rất quan trọng.

Lazy loading thường dùng:

```html
<img
    data-src="/images/chapter-1.jpg"
>
```

hoặc:

```html
<img
    data-original="/images/chapter-1.jpg"
>
```

hoặc:

```html
<img
    data-lazy-src="/images/chapter-1.jpg"
>
```

Nếu chúng ta chỉ:

```python
tree.css("img[src]")
```

thì có thể **không lấy được ảnh thật**.

---

# 10. Lazy loading

Ví dụ:

```html
<div class="chapter-content">

    <img
        src="placeholder.gif"
        data-src="/images/chapter-1-01.jpg"
    >

</div>
```

Ảnh thực:

```text
data-src
```

không phải:

```text
src
```

Có thể xử lý:

```python
src = (
    node.attributes.get("data-src")
    or node.attributes.get("src")
)
```

Nhưng cần cẩn thận.

Nếu:

```html
<img
    src="placeholder.gif"
    data-src="/real-image.jpg"
>
```

thì phải ưu tiên:

```text
data-src
```

---

# 11. Hàm lấy image source

Ta có thể viết:

```python
def get_image_source(node) -> str | None:

    for attribute in (
        "data-src",
        "data-original",
        "data-lazy-src",
        "src",
    ):
        value = node.attributes.get(attribute)

        if value:
            value = value.strip()

            if value:
                return value

    return None
```

Thứ tự:

```text
data-src
data-original
data-lazy-src
src
```

Tùy website mà thứ tự thực tế có thể cần điều chỉnh.

---

# 12. Nhưng chưa nên over-engineer

Không phải website nào cũng cần:

```text
data-src
data-original
data-lazy-src
data-lazy
data-url
data-image
...
```

Với một plugin cụ thể, tốt hơn là biết HTML của website đó rồi cấu hình:

```text
TruyenFull
    image source = data-src

Website B
    image source = src

Website C
    image source = data-original
```

Đây là lý do **Plugin Architecture** rất hữu ích.

---

# 13. Tạo `ImageLink`

Giống Buổi 34, ta không nhất thiết chỉ trả `URL`.

Có thể:

```python
from dataclasses import dataclass
from yarl import URL


@dataclass(frozen=True)
class ImageLink:
    url: URL
```

Sau này có thể mở rộng:

```text
ImageLink
├── url
├── alt
├── index
└── ...
```

---

# 14. Parser Image Link

Implementation đơn giản:

```python
from dataclasses import dataclass

from selectolax.parser import HTMLParser
from yarl import URL


@dataclass(frozen=True)
class ImageLink:
    url: URL


def parse_image_links(
    page_url: URL,
    html: str,
) -> list[ImageLink]:

    tree = HTMLParser(html)

    result: list[ImageLink] = []

    for node in tree.css("img"):

        src = node.attributes.get("src")

        if not src:
            continue

        src = src.strip()

        if not src:
            continue

        src_url = URL(src)

        if src_url.scheme not in {
            "",
            "http",
            "https",
        }:
            continue

        image_url = page_url.join(src_url)

        if image_url.scheme not in {
            "http",
            "https",
        }:
            continue

        result.append(
            ImageLink(
                url=image_url
            )
        )

    return result
```

---

# 15. Test hoàn chỉnh

```python
from dataclasses import dataclass

from selectolax.parser import HTMLParser
from yarl import URL


@dataclass(frozen=True)
class ImageLink:
    url: URL


def parse_image_links(
    page_url: URL,
    html: str,
) -> list[ImageLink]:

    tree = HTMLParser(html)

    result: list[ImageLink] = []

    for node in tree.css("img"):

        src = node.attributes.get("src")

        if not src:
            continue

        src = src.strip()

        if not src:
            continue

        src_url = URL(src)

        if src_url.scheme not in {
            "",
            "http",
            "https",
        }:
            continue

        image_url = page_url.join(src_url)

        if image_url.scheme not in {
            "http",
            "https",
        }:
            continue

        result.append(
            ImageLink(
                url=image_url
            )
        )

    return result


def main():

    page_url = URL(
        "https://example.com/truyen/python/chuong-1/"
    )

    html = """
    <div class="chapter-content">

        <img src="images/001.jpg">

        <img src="/uploads/002.jpg">

        <img
            src="https://cdn.example.com/003.webp"
        >

        <img src="">

    </div>
    """

    images = parse_image_links(
        page_url,
        html,
    )

    for image in images:
        print(image.url)


if __name__ == "__main__":
    main()
```

Kết quả:

```text
https://example.com/truyen/python/chuong-1/images/001.jpg
https://example.com/uploads/002.jpg
https://cdn.example.com/003.webp
```

---

# 16. Thêm lazy loading

Bây giờ nâng cấp:

```python
def get_image_source(node) -> str | None:

    for attribute in (
        "data-src",
        "data-original",
        "data-lazy-src",
        "src",
    ):
        value = node.attributes.get(attribute)

        if value:
            value = value.strip()

            if value:
                return value

    return None
```

Sau đó:

```python
def parse_image_links(
    page_url: URL,
    html: str,
) -> list[ImageLink]:

    tree = HTMLParser(html)

    result: list[ImageLink] = []

    for node in tree.css("img"):

        src = get_image_source(node)

        if src is None:
            continue

        src_url = URL(src)

        if src_url.scheme not in {
            "",
            "http",
            "https",
        }:
            continue

        image_url = page_url.join(src_url)

        result.append(
            ImageLink(
                url=image_url
            )
        )

    return result
```

---

# 17. Test lazy loading

```python
html = """
<div class="chapter-content">

    <img
        src="placeholder.gif"
        data-src="/images/001.jpg"
    >

    <img
        data-original="/images/002.jpg"
    >

    <img
        data-lazy-src="/images/003.jpg"
    >

    <img
        src="/images/004.jpg"
    >

</div>
"""
```

Kết quả:

```text
https://example.com/images/001.jpg
https://example.com/images/002.jpg
https://example.com/images/003.jpg
https://example.com/images/004.jpg
```

---

# 18. `srcset`

Một HTML hiện đại có thể có:

```html
<img
    src="/images/chapter.jpg"
    srcset="
        /images/chapter-small.jpg 480w,
        /images/chapter-medium.jpg 800w,
        /images/chapter-large.jpg 1200w
    "
>
```

`srcset` không phải một URL đơn.

Nó là:

```text
URL + descriptor
```

Ví dụ:

```text
/images/chapter-small.jpg 480w
/images/chapter-medium.jpg 800w
/images/chapter-large.jpg 1200w
```

Không nên lấy nguyên:

```python
node.attributes["srcset"]
```

rồi đưa vào:

```python
URL(srcset)
```

vì sai.

`srcset` sẽ cần parser riêng nếu crawler cần hỗ trợ nó.

---

# 19. Background image

Một số website dùng:

```html
<div
    style="
        background-image:
        url('/images/chapter-1.jpg')
    "
>
</div>
```

Đây không phải:

```html
<img>
```

Vì vậy:

```python
tree.css("img")
```

không tìm thấy.

Đừng vội đưa CSS parser vào image extractor chung.

Có thể thiết kế:

```text
ImageSourceExtractor
├── IMG_SRC
├── DATA_SRC
├── SRCSET
└── CSS_BACKGROUND
```

**chỉ khi website thực sự cần.**

---

# 20. Image URL và fragment

Ví dụ:

```html
<img src="/image.jpg#something">
```

Yarl sẽ giữ:

```text
https://example.com/image.jpg#something
```

Nhưng khi download ảnh qua HTTP, fragment thường không được gửi tới server.

Do đó, về sau URL normalization có thể xử lý:

```python
image_url = image_url.with_fragment(None)
```

Nhưng giống các bài trước:

> **Đừng trộn normalization vào extraction nếu chưa cần.**

---

# 21. Image URL và query string

CDN thường có:

```text
https://cdn.example.com/image.jpg?w=800&q=90
```

Không được tự ý bỏ query:

```python
image_url = image_url.with_query(None)
```

vì:

```text
?w=800
```

có thể quyết định kích thước ảnh.

Hoặc:

```text
?token=abc123
```

có thể là signed URL.

Do đó:

```text
Extraction
    ↓
giữ nguyên URL
    ↓
Normalization
    ↓
Canonicalization
```

chỉ bỏ thành phần nào khi policy xác định rõ.

---

# 22. Image URL có thể có token

Ví dụ:

```text
https://cdn.example.com/image.jpg?token=abc123
```

Nếu crawler làm:

```python
URL(...).with_query(None)
```

thì có thể biến URL hợp lệ thành:

```text
https://cdn.example.com/image.jpg
```

và server trả:

```text
403 Forbidden
```

Vì vậy:

> **Không tự ý canonicalize image URL trước khi download.**

Đặc biệt với CDN.

---

# 23. Image URL ≠ Image file

Điều này cũng cần phân biệt:

```text
Image URL
```

là:

```text
https://cdn.example.com/001.webp
```

Còn:

```text
Image
```

là bytes:

```text
b'\x89PNG...'
```

Pipeline:

```text
HTML
 ↓
Image URL
 ↓
Fetcher
 ↓
HTTP response
 ↓
bytes
 ↓
Image Storage
```

`yarl` chỉ giải quyết phần:

```text
href/src → URL
```

không download ảnh.

---

# 24. Đặt vào kiến trúc Novel Crawler

Chapter Parser có thể trả:

```text
Chapter
├── title
├── number
├── content
└── images
```

Ví dụ:

```python
from dataclasses import dataclass
from yarl import URL


@dataclass(frozen=True)
class ChapterImage:
    url: URL
    index: int
```

Parser:

```text
Chapter HTML
     │
     ▼
Selectolax
     │
     ├── title
     ├── number
     ├── content
     │
     └── image src
              │
              ▼
           yarl.URL
              │
              ▼
         ChapterImage
```

---

# 25. Một kiến trúc rất đáng giữ

Không nên:

```text
ImageParser
    ↓
httpx.get(image_url)
    ↓
save image
```

Parser chỉ:

```text
HTML
 ↓
Image URL
```

Fetcher:

```text
Image URL
 ↓
HTTP
 ↓
bytes
```

Storage:

```text
bytes
 ↓
file/database/object storage
```

Tách như vậy sẽ giúp chúng ta dễ:

* retry
* proxy
* timeout
* rate limit
* download song song
* resume
* checksum

sau này.

---

# 26. Một phiên bản thực tế cho crawler

Tôi đề xuất ở giai đoạn hiện tại:

```python
from dataclasses import dataclass

from selectolax.parser import HTMLParser
from yarl import URL


@dataclass(frozen=True)
class ImageLink:
    url: URL


def get_image_source(node) -> str | None:

    for attribute in (
        "data-src",
        "data-original",
        "data-lazy-src",
        "src",
    ):
        value = node.attributes.get(attribute)

        if value:
            value = value.strip()

            if value:
                return value

    return None


def parse_image_links(
    page_url: URL,
    html: str,
) -> list[ImageLink]:

    tree = HTMLParser(html)

    result: list[ImageLink] = []

    for node in tree.css("img"):

        src = get_image_source(node)

        if src is None:
            continue

        src_url = URL(src)

        if src_url.scheme not in {
            "",
            "http",
            "https",
        }:
            continue

        image_url = page_url.join(src_url)

        if image_url.scheme not in {
            "http",
            "https",
        }:
            continue

        result.append(
            ImageLink(url=image_url)
        )

    return result
```

Đây là mức abstraction vừa đủ cho hiện tại.

---

# 27. Một điểm cần lưu ý cho plugin

Không phải website nào cũng có:

```css
.chapter-content img
```

Có thể là:

```css
.reading-content img
```

hoặc:

```css
#chapter-c
```

Do đó phần selector nên thuộc **plugin/source configuration**.

Ví dụ:

```python
class TruyenFullConfig:
    chapter_content_selector = ".chapter-content"
    image_selector = ".chapter-content img"
```

Parser:

```python
tree.css(
    config.image_selector
)
```

Khi đó:

```text
Core Parser
     ↑
     │
Plugin Config
     │
     ├── chapter selector
     ├── image selector
     └── image source attribute
```

Đây là hướng rất phù hợp với Plugin Architecture mà bạn đang xây dựng.

---

# 28. So sánh ba loại URL đã học

Đến đây chúng ta có:

### Link

```html
<a href="chapter-1">
```

→

```python
URL(href)
```

### Pagination

```html
<a href="?page=2">
```

→

```python
page_url.join(URL(href))
```

### Image

```html
<img src="/images/001.jpg">
```

→

```python
page_url.join(URL(src))
```

Cốt lõi vẫn là:

```text
                  HTML
                   │
         ┌─────────┼─────────┐
         ▼         ▼         ▼
       href      href       src
       link      next       image
         │         │         │
         └─────────┼─────────┘
                   ▼
                URL(...)
                   │
                   ▼
          page_url.join(...)
                   │
                   ▼
             Absolute URL
```

---

# 29. Những gì cần nhớ sau Buổi 35

```text
✓ <img src> là nguồn Image URL
✓ dùng selectolax để lấy img
✓ dùng yarl để resolve relative URL
✓ src có thể relative/root-relative/absolute
✓ CDN có thể là external URL hợp lệ
✓ lazy loading có thể dùng data-src
✓ không nên mặc định chỉ đọc src
✓ srcset là một vấn đề riêng
✓ CSS background image là một vấn đề riêng
✓ không tự ý bỏ query của CDN
✓ không tự ý bỏ fragment khi extraction
✓ parser không download ảnh
✓ parser trả URL/ImageLink
```

Pipeline hiện tại:

```text
                  Novel Detail
                       │
                       ▼
                 Chapter Links
                       │
                       ▼
                    yarl.URL
                       │
                       ▼
                     Queue
                       │
                       ▼
                 Chapter Fetch
                       │
                       ▼
                 Chapter HTML
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
          Content             <img>
                                 │
                                 ▼
                              src
                                 │
                                 ▼
                            yarl.URL
                                 │
                                 ▼
                           ImageLink
                                 │
                                 ▼
                              Queue
                                 │
                                 ▼
                           Image Fetch
```

Và roadmap tiếp theo:

```text
31 Relative URL → Absolute URL
32 <a href> → URL
33 Pagination
34 Chapter URL
👉 35 Image URL
36 URL Normalization
37 URL Comparison
38 URL Deduplication
39 Canonical URL
40 URLBuilder cho Novel Crawler
```

**Điểm mấu chốt:** từ bây giờ, trong crawler của chúng ta, `href`, `src` chỉ là **raw URL reference**. Sau khi đi qua `yarl.URL` + `page_url.join(...)`, ta mới có một `URL` object có thể truyền tiếp sang **policy, queue hoặc fetcher**.
