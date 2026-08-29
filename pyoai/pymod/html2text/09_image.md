# Buổi 9 — Image Configuration Deep Dive

Hôm nay chúng ta học `<img>` trong `html2text`. Đây là phần rất quan trọng nếu bạn dùng `html2text` cho **crawler → Markdown → reader/TTS**, vì ảnh trên website thực tế thường không đơn giản là:

```html
<img src="image.jpg" alt="Python">
```

Mà có thể là:

```html
<img data-src="..." loading="lazy">
<img srcset="...">
<img class="lazyload" data-original="...">
```

---

# 1. Mục tiêu buổi học

Sau buổi này bạn cần hiểu:

```text
<img>
 │
 ├── ignore_images
 ├── images_to_alt
 ├── images_as_html
 ├── images_with_size
 ├── default_image_alt
 │
 ├── src
 ├── alt
 ├── title
 ├── width / height
 │
 └── lazy loading
       ├── data-src
       ├── data-original
       └── srcset
```

Và đặc biệt:

> `html2text` xử lý HTML image → Markdown image, nhưng việc **tìm đúng URL ảnh thực tế** thường nên được xử lý ở tầng parser/cleaner.

---

# 2. `<img>` cơ bản

HTML:

```html
<img src="python.png" alt="Python logo">
```

Markdown:

```markdown
![Python logo](python.png)
```

Mental model:

```text
<img>
 │
 ├── src → URL
 │
 └── alt → description
 │
 ▼
![alt](src)
```

Code:

```python
import html2text

html = """
<img src="python.png" alt="Python logo">
"""

converter = html2text.HTML2Text()

print(converter.handle(html))
```

---

# 3. `alt` cực kỳ quan trọng

HTML:

```html
<img
    src="python.png"
    alt="Python programming language logo"
>
```

Markdown:

```markdown
![Python programming language logo](python.png)
```

`alt` không phải URL.

Nó là:

```text
alternative text
```

Có giá trị cho:

* accessibility
* screen reader
* fallback khi ảnh không tải
* semantic information
* AI/document processing

---

# 4. Không có `alt`

HTML:

```html
<img src="python.png">
```

Khi đó:

```text
alt = ""
```

Output có thể dạng:

```markdown
![](python.png)
```

Đây không phải output lý tưởng cho document processing.

---

# 5. `default_image_alt`

Khi ảnh không có alt, có thể cấu hình default alt:

```python
converter.default_image_alt = "image"
```

Ví dụ:

```html
<img src="python.png">
```

có thể trở thành:

```markdown
![image](python.png)
```

Mental model:

```text
alt tồn tại?
 │
 ├── yes → dùng alt
 │
 └── no
      │
      ▼
default_image_alt
```

---

# 6. `ignore_images`

Option rất quan trọng:

```python
converter.ignore_images = True
```

HTML:

```html
<p>
Python là ngôn ngữ lập trình.
<img src="python.png" alt="Python">
</p>
```

Khi bật:

```python
converter.ignore_images = True
```

ảnh sẽ bị bỏ khỏi output.

Ta thu được nội dung text thay vì:

```markdown
![Python](python.png)
```

---

# 7. Khi nào dùng `ignore_images`?

Đây là option rất hữu ích cho **TTS**.

Pipeline:

```text
HTML
 ↓
Cleaner
 ↓
html2text
 ↓
Markdown
 ↓
TTS
```

Nếu TTS chỉ đọc text:

```python
converter.ignore_images = True
```

thường hợp lý.

Đối với app đọc truyện:

```text
Chapter
 │
 ├── text
 ├── images
 └── formatting
```

thì tùy mục tiêu.

Nếu reader có hỗ trợ ảnh:

```text
ignore_images = False
```

Nếu chỉ tạo audiobook:

```text
ignore_images = True
```

---

# 8. `images_to_alt`

Một behavior hữu ích là chuyển image thành chính `alt` text thay vì Markdown image.

Ví dụ:

```html
<img src="python.png" alt="Python logo">
```

thay vì:

```markdown
![Python logo](python.png)
```

có thể output text:

```text
Python logo
```

Configuration:

```python
converter.images_to_alt = True
```

Mental model:

```text
<img>
 │
 ▼
alt
```

thay vì:

```text
<img>
 │
 ▼
![alt](src)
```

---

# 9. `images_to_alt` rất hữu ích cho TTS

Ví dụ article:

```html
<p>
Python là ngôn ngữ phổ biến.
</p>

<img
    src="diagram.png"
    alt="Sơ đồ kiến trúc Python"
>
```

Nếu:

```python
converter.images_to_alt = True
```

TTS có thể đọc:

```text
Python là ngôn ngữ phổ biến.

Sơ đồ kiến trúc Python
```

Thay vì đọc:

```text
![Sơ đồ kiến trúc Python](diagram.png)
```

---

# 10. `images_as_html`

Markdown thông thường:

```markdown
![Python](python.png)
```

Nhưng đôi khi bạn muốn giữ image dưới dạng HTML:

```html
<img src="python.png" alt="Python">
```

Có thể dùng:

```python
converter.images_as_html = True
```

Điều này hữu ích khi Markdown renderer của bạn cần giữ thêm HTML attributes.

---

# 11. Markdown image vs HTML image

### Markdown

```markdown
![Python](python.png)
```

Ưu:

* đơn giản
* portable
* dễ đọc
* tương thích Markdown tốt

### HTML

```html
<img src="python.png" alt="Python" width="400">
```

Ưu:

* giữ được attributes
* kiểm soát width/height tốt hơn

Mental model:

```text
Markdown image
      ↓
simple


HTML image
      ↓
more control
```

---

# 12. `images_with_size`

HTML:

```html
<img
    src="python.png"
    alt="Python"
    width="400"
    height="200"
>
```

Nếu:

```python
converter.images_with_size = True
```

converter có thể giữ thông tin kích thước trong output.

Đây là option bạn nên test cùng:

```python
images_as_html
```

vì behavior cuối cùng phụ thuộc cách `html2text` biểu diễn image trong phiên bản bạn đang dùng.

---

# 13. Width và height

Có ba trường hợp:

### HTML

```html
<img width="400">
```

### HTML

```html
<img height="200">
```

### HTML

```html
<img width="400" height="200">
```

Khi crawl website thực tế, attributes này có thể được dùng cho:

* layout
* responsive image
* placeholder
* lazy loading
* CSS

Không nên mặc định coi `width`/`height` là kích thước file ảnh thực tế.

---

# 14. Lazy loading

Đây là phần **rất quan trọng**.

Website hiện đại thường không:

```html
<img src="real-image.jpg">
```

mà:

```html
<img
    src="placeholder.jpg"
    data-src="real-image.jpg"
>
```

Nếu converter chỉ nhìn:

```text
src
```

thì nó có thể lấy:

```text
placeholder.jpg
```

thay vì:

```text
real-image.jpg
```

---

# 15. Các dạng lazy loading phổ biến

Bạn có thể gặp:

```html
<img data-src="real.jpg">
```

hoặc:

```html
<img data-original="real.jpg">
```

hoặc:

```html
<img data-lazy-src="real.jpg">
```

hoặc:

```html
<img
    src="placeholder.jpg"
    data-src="real.jpg"
>
```

hoặc:

```html
<img
    src="placeholder.jpg"
    data-srcset="image-800.jpg 800w"
>
```

---

# 16. `html2text` không phải image downloader

Đây là nguyên tắc architecture:

```text
html2text
```

không có nhiệm vụ:

```text
download image
```

Nó chỉ chuyển:

```text
HTML
 ↓
Markdown
```

Nếu bạn cần download ảnh:

```text
ImageDownloader
```

nên là component riêng.

---

# 17. Kiến trúc crawler tốt

```text
                 HTML
                   │
                   ▼
               Selectolax
                   │
          ┌────────┴────────┐
          │                 │
      LinkParser       ImageParser
          │                 │
          ▼                 ▼
   URLNormalizer      ImageNormalizer
          │                 │
          └────────┬────────┘
                   ▼
                Cleaner
                   │
                   ▼
               html2text
                   │
                   ▼
                Markdown
```

Đây là architecture rất phù hợp cho project crawler của bạn.

---

# 18. Image URL normalization

Giả sử:

```text
base_url =
https://example.com/articles/python
```

HTML:

```html
<img src="/images/python.png">
```

`src` là relative URL.

Dùng:

```python
from urllib.parse import urljoin

base_url = "https://example.com/articles/python"

src = "/images/python.png"

absolute_url = urljoin(base_url, src)

print(absolute_url)
```

Kết quả:

```text
https://example.com/images/python.png
```

---

# 19. Vì sao cần normalize ảnh?

Nếu lưu Markdown:

```markdown
![Python](/images/python.png)
```

thì Markdown reader phải biết base URL.

Nhưng:

```markdown
![Python](https://example.com/images/python.png)
```

thì document có URL độc lập.

Với crawler, thường tốt hơn:

```text
relative
   ↓
absolute
   ↓
Markdown
```

---

# 20. `srcset`

Một website responsive có thể:

```html
<img
    src="small.jpg"
    srcset="
        small.jpg 400w,
        medium.jpg 800w,
        large.jpg 1200w
    "
>
```

`srcset` chứa nhiều candidate:

```text
small.jpg    400w
medium.jpg   800w
large.jpg    1200w
```

Đây là logic của browser.

Không nên đơn giản:

```python
src = element.attributes["srcset"]
```

rồi coi nó là một URL.

---

# 21. `srcset` parser

Bạn có thể bắt đầu bằng parser đơn giản:

```python
def parse_srcset(srcset: str) -> list[str]:
    result = []

    for item in srcset.split(","):
        item = item.strip()

        if not item:
            continue

        url = item.split()[0]

        result.append(url)

    return result
```

Ví dụ:

```python
srcset = """
small.jpg 400w,
medium.jpg 800w,
large.jpg 1200w
"""

print(parse_srcset(srcset))
```

Kết quả:

```python
[
    "small.jpg",
    "medium.jpg",
    "large.jpg",
]
```

Đây mới chỉ là parser cơ bản.

---

# 22. Chọn image từ `srcset`

Nếu crawler chỉ cần một image:

```text
small.jpg
medium.jpg
large.jpg
```

có thể chọn:

```text
largest available
```

Ví dụ:

```python
def choose_largest(srcset: str) -> str | None:
    candidates = []

    for item in srcset.split(","):
        parts = item.strip().split()

        if not parts:
            continue

        url = parts[0]

        width = 0

        if len(parts) > 1 and parts[1].endswith("w"):
            width = int(parts[1][:-1])

        candidates.append((width, url))

    if not candidates:
        return None

    return max(candidates)[1]
```

---

# 23. Nhưng đừng quá phụ thuộc vào `srcset`

Một crawler thực tế nên ưu tiên:

```text
data-src
    ↓
data-lazy-src
    ↓
data-original
    ↓
src
    ↓
srcset
```

**nhưng thứ tự này không phải universal rule.**

Mỗi website có thể dùng convention khác nhau.

Do đó nên xây:

```text
ImagePolicy
```

thay vì hard-code logic vào `html2text`.

---

# 24. Xây `ImagePolicy`

Ví dụ:

```python
from dataclasses import dataclass


@dataclass
class ImagePolicy:
    ignore_images: bool = False
    use_alt_only: bool = False
    prefer_lazy_src: bool = True
    normalize_url: bool = True
```

Sau này có thể mở rộng:

```text
download_images
save_local
max_width
prefer_srcset
```

---

# 25. `ImageNormalizer`

Ví dụ đơn giản:

```python
from urllib.parse import urljoin


class ImageNormalizer:

    LAZY_ATTRIBUTES = (
        "data-src",
        "data-lazy-src",
        "data-original",
    )

    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_src(self, attrs: dict[str, str]) -> str | None:

        for name in self.LAZY_ATTRIBUTES:
            value = attrs.get(name)

            if value:
                return urljoin(self.base_url, value)

        src = attrs.get("src")

        if src:
            return urljoin(self.base_url, src)

        return None
```

Đây là component rất hữu ích cho crawler.

---

# 26. Test `ImageNormalizer`

```python
normalizer = ImageNormalizer(
    "https://example.com/article"
)

attrs = {
    "src": "placeholder.gif",
    "data-src": "/images/python.jpg",
}

print(normalizer.get_src(attrs))
```

Kết quả mong muốn:

```text
https://example.com/images/python.jpg
```

thay vì:

```text
https://example.com/placeholder.gif
```

---

# 27. Một lỗi rất phổ biến

Sai:

```python
img_url = element.attributes.get("src")
```

Website:

```html
<img
    src="loading.gif"
    data-src="/images/chapter-1.jpg"
>
```

Bạn sẽ lấy:

```text
loading.gif
```

Đúng hơn:

```text
data-src
   ↓
real image
```

---

# 28. `alt` cũng cần cleaning

Ví dụ:

```html
<img
    src="python.jpg"
    alt="  Python   programming   "
>
```

Có thể normalize:

```python
alt = " ".join(alt.split())
```

Kết quả:

```text
Python programming
```

Đây là một ví dụ nhỏ nhưng rất hữu ích khi làm document processing.

---

# 29. Image trong `<a>`

HTML:

```html
<a href="https://python.org">
    <img
        src="python.png"
        alt="Python"
    >
</a>
```

Semantic:

```text
a
└── img
```

Markdown thường có dạng:

```markdown
[![Python](python.png)](https://python.org)
```

Đây là combination:

```text
Link configuration
        +
Image configuration
```

---

# 30. Image không có alt

Ví dụ:

```html
<img src="ad-banner.jpg">
```

Trong crawler article, đây có thể là:

```text
advertisement
```

Nếu:

```text
alt = ""
```

thì đây là tín hiệu để xem xét loại bỏ image.

Ví dụ policy:

```python
def should_keep_image(src: str | None, alt: str | None) -> bool:
    if not src:
        return False

    return bool(alt)
```

Tuy nhiên đây chỉ là heuristic.

Không nên áp dụng mù quáng vì ảnh nội dung cũng có thể không có alt.

---

# 31. Image quảng cáo

Crawler thực tế thường gặp:

```html
<img
    class="advertisement"
    src="banner.jpg"
>
```

`html2text` không nên chịu trách nhiệm quyết định:

```text
advertisement?
```

Tầng cleaner nên xử lý:

```text
BeautifulSoup / Selectolax
        ↓
remove ads
        ↓
html2text
```

Đúng architecture:

```text
Cleaner
   ↓
remove unwanted <img>
   ↓
html2text
```

---

# 32. Image và TTS

Nếu mục tiêu là TTS:

```text
HTML
 ↓
Cleaner
 ↓
ImageNormalizer
 ↓
html2text
 ↓
Markdown
 ↓
Text extraction
 ↓
TTS
```

Có ba chiến lược:

### Strategy A

```python
ignore_images = True
```

→ bỏ hoàn toàn.

### Strategy B

```python
images_to_alt = True
```

→ giữ mô tả.

### Strategy C

```text
Markdown image
```

→ giữ ảnh để reader hiển thị.

---

# 33. Chọn strategy theo application

| Application     | Strategy                |
| --------------- | ----------------------- |
| TTS             | `ignore_images=True`    |
| Plain text      | `images_to_alt=True`    |
| Markdown reader | giữ image               |
| Knowledge base  | giữ image               |
| Search index    | thường bỏ hoặc dùng alt |
| Web archive     | giữ image + URL         |

Không có configuration "đúng" cho mọi ứng dụng.

---

# 34. Converter cho TTS

Ví dụ:

```python
import html2text


def create_tts_converter() -> html2text.HTML2Text:
    converter = html2text.HTML2Text()

    converter.ignore_links = True
    converter.ignore_images = True
    converter.body_width = 0

    return converter
```

Pipeline:

```text
HTML
 ↓
Markdown
 ↓
TTS
```

---

# 35. Converter cho Markdown Reader

```python
import html2text


def create_reader_converter() -> html2text.HTML2Text:
    converter = html2text.HTML2Text()

    converter.ignore_links = False
    converter.ignore_images = False
    converter.inline_links = True
    converter.body_width = 0

    return converter
```

Đây là configuration hợp lý cho reader.

---

# 36. Bài tập 1 — Image cơ bản

Chạy:

```python
html = """
<img src="python.png" alt="Python">
"""
```

và quan sát:

```python
converter = html2text.HTML2Text()
```

---

# 37. Bài tập 2 — `ignore_images`

Test:

```python
converter.ignore_images = False
```

sau đó:

```python
converter.ignore_images = True
```

So sánh output.

---

# 38. Bài tập 3 — `images_to_alt`

Test:

```html
<img
    src="python.png"
    alt="Python programming language"
>
```

với:

```python
converter.images_to_alt = True
```

Quan sát sự khác biệt.

---

# 39. Bài tập 4 — Default alt

Test:

```html
<img src="python.png">
```

với:

```python
converter.default_image_alt = "Image"
```

Quan sát output.

---

# 40. Bài tập 5 — Lazy loading

Test:

```html
<img
    src="placeholder.jpg"
    data-src="real-image.jpg"
    alt="Python"
>
```

Hãy suy nghĩ:

> Nếu chỉ lấy `src`, crawler sẽ lấy ảnh nào?

Đáp án:

```text
placeholder.jpg
```

Đây là lỗi crawler rất phổ biến.

---

# 41. Bài tập 6 — Relative image URL

Base:

```python
base_url = "https://example.com/article/1"
```

HTML:

```html
<img
    src="/images/python.jpg"
    alt="Python"
>
```

Dùng:

```python
from urllib.parse import urljoin
```

để biến thành:

```text
https://example.com/images/python.jpg
```

---

# 42. Bài tập 7 — `srcset`

Test:

```html
<img
    src="small.jpg"
    srcset="
        small.jpg 400w,
        medium.jpg 800w,
        large.jpg 1200w
    "
    alt="Python"
>
```

Viết hàm:

```python
def parse_srcset(srcset: str) -> list[str]:
    ...
```

để lấy:

```python
[
    "small.jpg",
    "medium.jpg",
    "large.jpg",
]
```

---

# 43. Bài tập 8 — Xây ImageNormalizer

Hoàn thiện:

```python
class ImageNormalizer:

    def __init__(self, base_url: str):
        ...

    def get_src(self, attrs: dict[str, str]) -> str | None:
        ...
```

Input:

```python
{
    "src": "placeholder.jpg",
    "data-src": "/images/python.jpg",
}
```

Output:

```text
https://example.com/images/python.jpg
```

---

# 44. Bài tập 9 — Production case

Xử lý HTML:

```html
<article>

<h1>Python</h1>

<p>Python là ngôn ngữ lập trình.</p>

<img
    src="loading.gif"
    data-src="/images/python.png"
    alt="Python logo"
    loading="lazy"
>

<img
    src="/ads/banner.jpg"
    class="advertisement"
    alt="Advertisement"
>

<p>
<a href="#comments">Comments</a>
</p>

</article>
```

Pipeline mong muốn:

```text
HTML
 ↓
remove advertisement
 ↓
resolve lazy image
 ↓
resolve relative URL
 ↓
skip internal link
 ↓
html2text
 ↓
Markdown
```

Đây chính là bài tập kết hợp:

```text
Buổi 6
Buổi 7
Buổi 8
Buổi 9
```

---

# 45. Kiến trúc nên hướng tới

Đừng xây một class khổng lồ:

```python
class Crawler:
    # 1000 lines
```

Thay vào đó:

```text
                    Crawler
                       │
              ┌────────┴────────┐
              │                 │
           LinkParser       ImageParser
              │                 │
        LinkNormalizer     ImageNormalizer
              │                 │
              └────────┬────────┘
                       │
                    Cleaner
                       │
                       ▼
                  html2text
                       │
                       ▼
                    Markdown
```

Đây là cách bạn có thể dễ dàng test từng thành phần.

---

# 46. Mental model Buổi 9

Hãy nhớ:

```text
<img>
 │
 ├── src
 │
 ├── alt
 │
 ├── width
 │
 ├── height
 │
 ├── data-src
 │
 └── srcset
```

`html2text`:

```text
HTML image
    ↓
Markdown image
```

Còn crawler:

```text
ImageParser
    ↓
find real image URL
    ↓
normalize URL
    ↓
clean/filter
    ↓
html2text
```

**Điểm quan trọng nhất của Buổi 9:**

> Đừng chỉ lấy `img["src"]`. Khi crawl website hiện đại, hãy nghĩ đến `data-src`, `data-lazy-src`, `data-original`, `srcset` và URL tương đối.

**Buổi 10 — Unicode & HTML Entities** sẽ đi sâu vào:

```text
&nbsp;
&amp;
&lt;
&gt;
&quot;

&#39;
&#x27;

é
→
&amp;#...
```

và đặc biệt là vấn đề **HTML entity → Unicode → Markdown → TTS**, rất đáng chú ý khi bạn xử lý nội dung tiếng Việt.
