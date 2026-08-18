# Buổi 5 — Semantic HTML Cleaner: phát hiện quảng cáo và HTML rác bằng Scoring

Ở Buổi 4 chúng ta đã có **structural cleaner**:

```text
script
style
iframe
svg
canvas
comment
hidden
```

Hôm nay xây tầng thứ hai:

```text
HTML
 │
 ▼
Structural Cleaner
 │
 ▼
Semantic Cleaner
 │
 ├── quảng cáo
 ├── banner
 ├── social share
 ├── newsletter
 ├── navigation
 ├── related content
 └── tracking/noise
 │
 ▼
Clean HTML
```

Điểm quan trọng của Buổi 5:

> **Không được xóa chỉ vì `class` chứa chữ `ad`.**

Chúng ta sẽ dùng **scoring system**.

---

# 1. Vì sao `if "ad" in class` là nguy hiểm?

Ví dụ:

```html
<div class="advertisement">
    Buy now!
</div>
```

rõ ràng là quảng cáo.

Nhưng:

```html
<div class="admin">
    Python tutorial
</div>
```

có:

```text
admin
```

Nếu làm:

```python
if "ad" in class_name:
```

thì:

```text
admin
  ↑
  ad
```

bị xóa nhầm.

Hoặc:

```html
<div id="advanced-python">
```

cũng có:

```text
ad
```

Vì vậy:

```text
contains "ad"
```

là một rule cực kỳ tệ.

---

# 2. Tư duy mới: Feature → Score

Thay vì:

```text
ad?
  │
 YES → DELETE
```

ta làm:

```text
class="advertisement"
       │
       ▼
     +5

id="ad-banner"
       │
       ▼
     +5

tag=<aside>
       │
       ▼
     +1

role="complementary"
       │
       ▼
     +1

score = 12
       │
       ▼
score >= 5
       │
       ▼
DELETE
```

Đây là **heuristic scoring**.

---

# 3. Tạo `NoiseDetector`

Cấu trúc:

```text
src/
└── clip2md/
    ├── cleaner.py
    └── detector.py
```

`detector.py`:

```python
from dataclasses import dataclass

from bs4 import Tag
```

---

# 4. `DetectionResult`

Ta không nên chỉ trả:

```python
True
```

mà nên trả thông tin:

```python
@dataclass(slots=True)
class DetectionResult:
    score: int
    reasons: list[str]
```

Ví dụ:

```python
DetectionResult(
    score=8,
    reasons=[
        "class:advertisement",
        "id:ad-banner",
    ],
)
```

Điều này cực kỳ hữu ích để debug.

---

# 5. Detector cơ bản

```python
class NoiseDetector:

    def detect(
        self,
        tag: Tag,
    ) -> DetectionResult:

        score = 0
        reasons = []

        return DetectionResult(
            score=score,
            reasons=reasons,
        )
```

---

# 6. Tokenize class và id

Giả sử:

```html
<div class="ad-banner top-ad">
```

Ta không muốn xử lý cả chuỗi:

```text
"ad-banner top-ad"
```

mà muốn:

```text
[
    "ad-banner",
    "top-ad",
]
```

Helper:

```python
def _tokens(value: str) -> list[str]:
    return value.lower().split()
```

---

# 7. Nhưng `split()` vẫn chưa đủ

Ví dụ:

```html
<div class="ad_banner">
```

hoặc:

```html
<div class="ad.banner">
```

hoặc:

```html
<div class="ad-banner">
```

Ta cần normalize.

Một cách đơn giản:

```python
import re


def _tokenize(value: str) -> list[str]:
    return [
        token
        for token in re.split(
            r"[^a-z0-9]+",
            value.lower(),
        )
        if token
    ]
```

Ví dụ:

```text
"ad-banner top_ad"
```

→

```python
[
    "ad",
    "banner",
    "top",
    "ad",
]
```

---

# 8. Nhưng `ad` vẫn quá generic

Ví dụ:

```text
"admin"
```

tokenize:

```text
admin
```

không phải:

```text
ad
min
```

Do đó token matching:

```python
token == "ad"
```

an toàn hơn:

```python
"ad" in value
```

---

# 9. Xây danh sách keyword

```python
AD_KEYWORDS = {
    "ad",
    "ads",
    "advert",
    "advertisement",
    "advertising",
    "banner",
    "sponsor",
    "sponsored",
}
```

Social:

```python
SOCIAL_KEYWORDS = {
    "social",
    "share",
    "sharing",
    "facebook",
    "twitter",
    "linkedin",
}
```

Newsletter:

```python
NEWSLETTER_KEYWORDS = {
    "newsletter",
    "subscribe",
    "subscription",
}
```

Related:

```python
RELATED_KEYWORDS = {
    "related",
    "recommendation",
    "recommended",
}
```

---

# 10. Không nên gộp tất cả thành một list

Ta cần phân biệt:

```text
Advertisement
Social
Newsletter
Navigation
Related
```

vì sau này policy có thể:

```text
remove_ads = True
remove_social = True
remove_related = False
```

Do đó:

```python
@dataclass(slots=True)
class DetectionResult:
    score: int
    reasons: list[str]
    category: str | None = None
```

Ví dụ:

```python
DetectionResult(
    score=7,
    reasons=["class:advertisement"],
    category="advertisement",
)
```

---

# 11. Scoring Rule đầu tiên

```python
class NoiseDetector:

    def detect(
        self,
        tag: Tag,
    ) -> DetectionResult:

        score = 0
        reasons = []
        category = None

        tokens = self._get_tokens(tag)

        if tokens & AD_KEYWORDS:
            score += 5
            reasons.append(
                "ad-keyword"
            )
            category = "advertisement"

        return DetectionResult(
            score=score,
            reasons=reasons,
            category=category,
        )
```

---

# 12. Lấy token từ `class`

BeautifulSoup:

```python
tag.get("class")
```

có thể trả:

```python
[
    "ad-banner",
    "top-ad",
]
```

Nhưng:

```python
tag.get("id")
```

là:

```python
"advertisement"
```

Ta cần xử lý cả hai.

---

# 13. `_get_tokens`

```python
def _get_tokens(
    self,
    tag: Tag,
) -> set[str]:

    tokens: set[str] = set()

    for class_name in tag.get(
        "class",
        [],
    ):
        tokens.update(
            self._tokenize(class_name)
        )

    tag_id = tag.get("id")

    if tag_id:
        tokens.update(
            self._tokenize(tag_id)
        )

    return tokens
```

---

# 14. Test

HTML:

```html
<div class="ad-banner">
    Advertisement
</div>
```

```python
result = detector.detect(tag)
```

Ta mong muốn:

```python
result.score
# 5
```

và:

```python
result.category
# "advertisement"
```

---

# 15. Nhưng `<div class="banner">` không phải lúc nào cũng quảng cáo

Ví dụ:

```html
<div class="banner">
    Python 3.14 Tutorial
</div>
```

Có thể là nội dung hợp lệ.

Vậy:

```text
banner
```

chỉ nên:

```text
+2
```

thay vì:

```text
+5
```

---

# 16. Thiết kế weight

```python
AD_WEIGHTS = {
    "ad": 5,
    "ads": 5,
    "advert": 5,
    "advertisement": 6,
    "advertising": 5,
    "sponsored": 5,
    "sponsor": 4,
    "banner": 2,
}
```

Sau đó:

```python
for token in tokens:
    weight = AD_WEIGHTS.get(token)

    if weight:
        score += weight
        reasons.append(
            f"keyword:{token}"
        )
```

---

# 17. Ví dụ scoring

```html
<div class="ad-banner">
```

tokens:

```text
ad
banner
```

score:

```text
ad       +5
banner   +2
---------
total     7
```

→ remove.

---

# 18. `id="banner"`

```html
<div id="banner">
```

score:

```text
banner = +2
```

Chưa đủ threshold.

Điều này tránh false positive.

---

# 19. Threshold

```python
NOISE_THRESHOLD = 5
```

Detector chỉ nói:

```text
score = 7
```

Cleaner quyết định:

```python
if result.score >= threshold:
    tag.decompose()
```

Đây là separation of responsibility:

```text
Detector
    ↓
đánh giá

Cleaner
    ↓
quyết định
```

---

# 20. Thêm `<aside>`

`aside` thường chứa:

* sidebar
* related article
* advertisement
* social
* recommendation

Nhưng không phải lúc nào cũng rác.

Cho:

```text
<aside>
```

score:

```text
+1
```

```python
if tag.name == "aside":
    score += 1
    reasons.append("tag:aside")
```

---

# 21. `role="complementary"`

Ví dụ:

```html
<div role="complementary">
```

thường là sidebar.

Cho:

```text
+1
```

```python
if tag.get("role") == "complementary":
    score += 1
    reasons.append(
        "role:complementary"
    )
```

---

# 22. `aria-label`

Ví dụ:

```html
<div aria-label="Advertisement">
```

Ta có thể kiểm tra:

```python
aria_label = tag.get(
    "aria-label",
    "",
)
```

Tokenize:

```python
tokens = self._tokenize(
    aria_label
)
```

Nếu:

```text
advertisement
```

→ +5.

---

# 23. Gom các nguồn metadata

Ta có:

```text
class
id
aria-label
```

Thay vì viết:

```python
tokens_class
tokens_id
tokens_aria
```

Ta có:

```python
def _metadata_tokens(
    self,
    tag: Tag,
) -> set[str]:

    values = []

    values.extend(
        tag.get("class", [])
    )

    tag_id = tag.get("id")

    if tag_id:
        values.append(tag_id)

    aria_label = tag.get(
        "aria-label"
    )

    if aria_label:
        values.append(
            aria_label
        )

    tokens = set()

    for value in values:
        tokens.update(
            self._tokenize(value)
        )

    return tokens
```

---

# 24. Detector phiên bản 1

```python
import re
from dataclasses import dataclass

from bs4 import Tag


AD_WEIGHTS = {
    "ad": 5,
    "ads": 5,
    "advert": 5,
    "advertisement": 6,
    "advertising": 5,
    "sponsored": 5,
    "sponsor": 4,
    "banner": 2,
}


@dataclass(slots=True)
class DetectionResult:
    score: int
    reasons: list[str]
    category: str | None = None


class NoiseDetector:

    def detect(
        self,
        tag: Tag,
    ) -> DetectionResult:

        score = 0
        reasons: list[str] = []

        tokens = self._metadata_tokens(tag)

        for token in tokens:
            weight = AD_WEIGHTS.get(token)

            if weight is None:
                continue

            score += weight

            reasons.append(
                f"keyword:{token}"
            )

        if tag.name == "aside":
            score += 1
            reasons.append(
                "tag:aside"
            )

        if (
            tag.get("role")
            == "complementary"
        ):
            score += 1
            reasons.append(
                "role:complementary"
            )

        category = (
            "advertisement"
            if score >= 5
            else None
        )

        return DetectionResult(
            score=score,
            reasons=reasons,
            category=category,
        )

    def _metadata_tokens(
        self,
        tag: Tag,
    ) -> set[str]:

        values: list[str] = []

        values.extend(
            tag.get("class", [])
        )

        tag_id = tag.get("id")

        if tag_id:
            values.append(tag_id)

        aria_label = tag.get(
            "aria-label"
        )

        if aria_label:
            values.append(
                aria_label
            )

        tokens: set[str] = set()

        for value in values:
            tokens.update(
                self._tokenize(value)
            )

        return tokens

    @staticmethod
    def _tokenize(
        value: str,
    ) -> list[str]:

        return [
            token
            for token in re.split(
                r"[^a-z0-9]+",
                value.lower(),
            )
            if token
        ]
```

---

# 25. Tại sao `category` không chỉ là bool?

Sau này:

```python
DetectionResult(
    score=8,
    reasons=[
        "keyword:advertisement"
    ],
    category="advertisement",
)
```

hoặc:

```python
DetectionResult(
    score=6,
    reasons=[
        "keyword:newsletter"
    ],
    category="newsletter",
)
```

hoặc:

```python
DetectionResult(
    score=4,
    reasons=[
        "tag:aside",
        "role:complementary",
    ],
    category="sidebar",
)
```

Cleaner có thể quyết định khác nhau.

---

# 26. Bảo vệ `pre` và `code`

Đây là requirement quan trọng nhất của project.

Trong detector:

```python
PROTECTED_TAGS = {
    "pre",
    "code",
}
```

Ngay đầu:

```python
def detect(
    self,
    tag: Tag,
) -> DetectionResult:

    if tag.name in PROTECTED_TAGS:
        return DetectionResult(
            score=0,
            reasons=["protected-tag"],
        )
```

Như vậy:

```html
<pre class="ad">
```

không bị detector xóa.

---

# 27. Tại sao cần bảo vệ?

Ví dụ website dùng:

```html
<pre class="ad">
```

nhưng bên trong:

```python
def add(a, b):
    return a + b
```

Nếu chỉ nhìn:

```text
class="ad"
```

thì detector sẽ xóa cả code.

Đối với Clip2MD:

> **Mất code là lỗi nghiêm trọng hơn giữ lại một ít noise.**

Đây là một product decision rất quan trọng.

---

# 28. Nhưng `<code>` có thể nằm trong quảng cáo

Ví dụ:

```html
<div class="advertisement">
    <code>coupon123</code>
</div>
```

Ta không muốn:

```text
<div>
```

bị xóa rồi code trở thành nội dung độc lập?

Đây là vấn đề hierarchy.

Khi xử lý parent:

```text
advertisement
    │
    └── code
```

Nếu xóa parent:

```python
tag.decompose()
```

thì code cũng biến mất.

Do đó protected tag không có nghĩa:

> mọi ancestor của nó đều được giữ.

Nó chỉ có nghĩa:

> detector không đánh dấu chính `<pre>`/`<code>` là noise.

Trong bài toán thực tế, đây là lý do scoring cần thêm context.

---

# 29. Semantic cleaner

Bây giờ tạo:

```python
class SemanticCleaner:

    def __init__(
        self,
        detector: NoiseDetector,
        threshold: int = 5,
    ):
        self.detector = detector
        self.threshold = threshold

    def clean(
        self,
        soup: BeautifulSoup,
    ) -> None:

        for tag in soup.find_all():

            if tag.name in {
                "pre",
                "code",
            }:
                continue

            result = self.detector.detect(tag)

            if result.score >= self.threshold:
                tag.decompose()
```

---

# 30. Nhưng `decompose()` trong lúc iterate có thể gây khó hiểu

Ta đang:

```python
for tag in soup.find_all():
```

rồi:

```python
tag.decompose()
```

Trong BeautifulSoup, `find_all()` trả về `ResultSet`, nên cách này thường hoạt động.

Nhưng architecture tốt hơn:

```python
candidates = []

for tag in soup.find_all():
    result = detector.detect(tag)

    if result.score >= threshold:
        candidates.append(tag)

for tag in candidates:
    if tag.parent is not None:
        tag.decompose()
```

Tách:

```text
Detection phase
       ↓
Mutation phase
```

Đây là pattern rất đáng học.

---

# 31. Vì sao tách 2 phase?

Nếu vừa:

```text
detect
delete
detect
delete
```

DOM thay đổi liên tục.

Điều này làm logic khó reasoning.

Tách:

```text
Phase 1
DOM
 ↓
detect
 ↓
candidates

Phase 2
candidates
 ↓
delete
```

dễ test hơn.

---

# 32. `SemanticCleaner` tốt hơn

```python
class SemanticCleaner:

    def __init__(
        self,
        detector: NoiseDetector,
        threshold: int = 5,
    ):
        self.detector = detector
        self.threshold = threshold

    def clean(
        self,
        soup: BeautifulSoup,
    ) -> None:

        candidates = []

        for tag in soup.find_all():

            if tag.name in {
                "pre",
                "code",
            }:
                continue

            result = self.detector.detect(tag)

            if result.score >= self.threshold:
                candidates.append(tag)

        for tag in candidates:
            if tag.parent is not None:
                tag.decompose()
```

---

# 33. Test

Input:

```html
<article>

<h1>Python</h1>

<p>Hello Python.</p>

<div class="advertisement">
    Buy now!
</div>

<div class="ad-banner">
    Banner
</div>

<aside class="sidebar">
    Related
</aside>

<pre class="language-python">
<code>
def hello():
    print("Hello")
</code>
</pre>

</article>
```

Detector:

```text
advertisement
    score = 6
    DELETE

ad-banner
    ad + banner
    score = 7
    DELETE

sidebar
    score = 0
    KEEP

pre
    protected
    KEEP
```

---

# 34. Vấn đề với `sidebar`

Hiện tại:

```html
<aside class="sidebar">
```

chỉ:

```text
aside +1
```

nên:

```text
score = 1
```

→ giữ.

Đây là chủ ý.

Chúng ta **không muốn xóa mọi sidebar** vì một số sidebar chứa:

```text
table of contents
documentation navigation
chapter navigation
```

có thể hữu ích.

---

# 35. Thêm social share

Ví dụ:

```html
<div class="social-share">
    Facebook
    X
    LinkedIn
</div>
```

Ta có:

```python
SOCIAL_WEIGHTS = {
    "social": 3,
    "share": 4,
    "sharing": 4,
    "facebook": 4,
    "twitter": 4,
    "linkedin": 4,
}
```

Nhưng category:

```text
social
```

không phải:

```text
advertisement
```

---

# 36. Tách scoring theo category

Một design tốt hơn:

```python
KEYWORD_RULES = {
    "advertisement": {
        "ad": 5,
        "ads": 5,
        "advertisement": 6,
        "sponsored": 5,
    },

    "social": {
        "social": 3,
        "share": 4,
        "facebook": 4,
        "twitter": 4,
        "linkedin": 4,
    },

    "newsletter": {
        "newsletter": 5,
        "subscribe": 4,
        "subscription": 4,
    },
}
```

Sau này detector có thể tính:

```text
advertisement = 7
social = 4
newsletter = 5
```

và chọn category có score cao nhất.

---

# 37. Detector v2

Ý tưởng:

```python
@dataclass(slots=True)
class DetectionResult:
    score: int
    category: str | None
    reasons: list[str]
```

Detector:

```text
              metadata
                 │
        ┌────────┼─────────┐
        ▼        ▼         ▼
       AD      SOCIAL   NEWSLETTER
        │        │         │
        ▼        ▼         ▼
      score    score      score
        └────────┼─────────┘
                 ▼
          highest score
                 │
                 ▼
        DetectionResult
```

Đây là architecture tốt hơn rất nhiều so với:

```python
if "ad" in class:
    delete()
```

---

# 38. Một nguyên tắc quan trọng: conservative cleaning

App của chúng ta dùng để:

```text
Browser
  ↓
Copy
  ↓
Markdown
```

Mục tiêu là:

> **Giữ nội dung hữu ích**, không phải tạo HTML hoàn hảo.

Vì vậy khi không chắc:

```text
KEEP
```

thay vì:

```text
DELETE
```

Ví dụ:

```text
score = 3
threshold = 5
```

→ giữ.

Điều này giảm false positive.

---

# 39. Pipeline hoàn chỉnh hiện tại

Bây giờ project bắt đầu có hình dạng:

```text
┌─────────────────────┐
│      Browser        │
└──────────┬──────────┘
           │ Ctrl+C
           ▼
┌─────────────────────┐
│ ClipboardMonitor    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ ClipboardReader     │
└──────────┬──────────┘
           │ CF_HTML
           ▼
┌─────────────────────┐
│ CFHTMLParser        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ StructuralCleaner   │
│                     │
│ script/style/...    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ SemanticCleaner     │
│                     │
│ ad/social/...       │
└──────────┬──────────┘
           │
           ▼
        Clean HTML
```

---

# 40. Cấu trúc project

Đến đây tôi khuyên chuyển thành:

```text
clip2md/
│
├── pyproject.toml
│
├── src/
│   └── clip2md/
│       │
│       ├── __init__.py
│       │
│       ├── clipboard/
│       │   ├── __init__.py
│       │   ├── reader.py
│       │   ├── writer.py
│       │   ├── cf_html.py
│       │   └── monitor.py
│       │
│       ├── html/
│       │   ├── __init__.py
│       │   ├── policy.py
│       │   ├── cleaner.py
│       │   ├── detector.py
│       │   └── semantic.py
│       │
│       └── markdown/
│           └── converter.py
│
└── tests/
    ├── test_cf_html.py
    ├── test_cleaner.py
    ├── test_detector.py
    └── test_monitor.py
```

Đây là thời điểm tốt để tách package theo **responsibility**.

---

# 41. Bài tập Buổi 5

### Bài 1

Implement:

```python
DetectionResult
NoiseDetector
```

---

### Bài 2

Implement scoring:

```text
advertisement
social
newsletter
```

---

### Bài 3

Test:

```html
<div class="advertisement">
```

phải bị phát hiện.

---

### Bài 4

Test:

```html
<div class="admin">
```

**không được** bị phát hiện chỉ vì có `"ad"`.

---

### Bài 5

Test:

```html
<pre class="ad-banner">
```

phải được bảo vệ.

---

### Bài 6

Test:

```html
<div class="ad-banner">
```

phải có score cao hơn:

```html
<div class="banner">
```

---

# 42. Bài tập quan trọng nhất

Hãy tạo một file:

```text
tests/fixtures/article.html
```

mô phỏng một bài viết:

```html
<article>

    <h1>Python Async Programming</h1>

    <p>
        Python hỗ trợ lập trình bất đồng bộ.
    </p>

    <div class="advertisement">
        BUY NOW
    </div>

    <p>
        Ví dụ:
    </p>

    <pre class="language-python"><code>
async def main():
    await do_work()
    </code></pre>

    <div class="social-share">
        Facebook Twitter
    </div>

    <div class="newsletter">
        Subscribe to newsletter
    </div>

    <p>
        Nội dung tiếp theo.
    </p>

</article>
```

Mục tiêu:

```text
KEEP
 ├── h1
 ├── p
 ├── pre
 ├── code
 └── p

REMOVE
 ├── advertisement
 ├── social-share
 └── newsletter
```

---

## Kết quả cuối Buổi 5

Bạn đã có hai tầng làm sạch:

```text
             HTML
               │
               ▼
     ┌───────────────────┐
     │ Structural Cleaner │
     └─────────┬─────────┘
               │
               ▼
     ┌───────────────────┐
     │ Semantic Cleaner   │
     │                   │
     │ Detector          │
     │   ↓               │
     │ Scoring           │
     │   ↓               │
     │ Threshold         │
     └─────────┬─────────┘
               │
               ▼
          Clean HTML
```

**Buổi 6** chúng ta sẽ chuyển sang phần rất quan trọng: **HTML normalization trước khi đưa vào `html2text`** — xử lý `<br>`, `<p>`, heading, whitespace, links, images, `<pre><code>`, class `language-*`, và đặc biệt thiết kế pipeline để **không phá code block/inline code**.
