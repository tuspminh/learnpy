# Buổi 16 — Remove quảng cáo

Hôm nay chúng ta tập trung vào một bài toán rất thực tế khi xây crawler:

> **Làm sao phát hiện và loại bỏ quảng cáo khỏi HTML mà không xóa nhầm nội dung bài viết?**

Đây là bước quan trọng vì HTML thực tế thường không sạch như ví dụ:

```html
<div class="ads">Advertisement</div>
```

Mà có thể là:

```html
<div class="ad-container">
<div id="google_ads">
<div class="banner">
<div class="sponsor-box">
<div data-ad="true">
<aside class="sidebar-ad">
```

---

# 1. Mục tiêu của Buổi 16

Pipeline:

```text
HTML
 ↓
Selectolax
 ↓
Extract article
 ↓
Detect advertisements
 ↓
Remove advertisements
 ↓
Clean HTML
 ↓
html2text
 ↓
Markdown
```

Chúng ta sẽ xây:

```text
AdRemovalRule
       ↓
HTMLCleaner
```

và học nhiều chiến lược:

```text
1. CSS selector
2. class heuristic
3. id heuristic
4. attribute heuristic
5. text heuristic
6. kết hợp nhiều heuristic
7. tránh false positive
```

---

# 2. Tại sao remove quảng cáo khó?

Ví dụ:

```html
<div class="ads">
    Advertisement
</div>
```

rất dễ.

Nhưng website thực tế:

```html
<div class="box">
    <iframe ...>
        quảng cáo
    </iframe>
</div>
```

Tên class không nói gì về quảng cáo.

Hoặc:

```html
<div class="content">
    <p>Python is...</p>
</div>
```

Tên `content` lại là nội dung thật.

Vì vậy:

```text
class == "ads"
```

chỉ là một trường hợp đơn giản.

---

# 3. Chiến lược 1 — CSS selector

Đây là cách an toàn nhất nếu bạn biết cấu trúc website.

Ví dụ:

```python
AD_SELECTORS = [
    ".ads",
    ".ad",
    ".advertisement",
    ".advert",
    ".sponsor",
    ".sponsored",
]
```

Cleaner:

```python
class AdRemovalRule:

    SELECTORS = [
        ".ads",
        ".ad",
        ".advertisement",
        ".advert",
        ".sponsor",
        ".sponsored",
    ]

    def apply(self, root):
        for selector in self.SELECTORS:
            for node in root.css(selector):
                node.decompose()
```

---

# 4. Test

HTML:

```python
html = """
<article>

<h1>Python</h1>

<p>Hello Python.</p>

<div class="ads">
    Advertisement
</div>

<p>Python is powerful.</p>

</article>
"""
```

Parse:

```python
from selectolax.parser import HTMLParser

tree = HTMLParser(html)

article = tree.css_first("article")
```

Apply:

```python
rule = AdRemovalRule()

rule.apply(article)
```

Kiểm tra:

```python
print(article.html)
```

---

# 5. Kết quả

Trước:

```html
<article>
    <h1>Python</h1>

    <p>Hello Python.</p>

    <div class="ads">
        Advertisement
    </div>

    <p>Python is powerful.</p>
</article>
```

Sau:

```html
<article>
    <h1>Python</h1>

    <p>Hello Python.</p>

    <p>Python is powerful.</p>
</article>
```

Đây là rule rất đơn giản nhưng hữu ích.

---

# 6. Vấn đề selector `.ad`

Một selector nguy hiểm:

```python
".ad"
```

CSS:

```text
.ad
```

nghĩa là:

```text
class chứa token "ad"
```

Ví dụ:

```html
<div class="ad">
```

đúng.

Nhưng:

```html
<div class="address">
```

không match `.ad`.

Tuy nhiên những selector kiểu:

```python
"[class*='ad']"
```

lại nguy hiểm.

---

# 7. Không nên dùng `[class*='ad']` một cách ngây thơ

Ví dụ:

```python
"[class*='ad']"
```

có thể match:

```text
advertisement
ad-container
```

nhưng cũng có thể match các class không liên quan.

Ví dụ:

```html
<div class="reading">
```

hoặc:

```html
<div class="header">
```

Việc kiểm tra substring rất dễ tạo:

```text
false positive
```

---

# 8. False Positive

Hai khái niệm cực kỳ quan trọng:

### True Positive

Phát hiện đúng quảng cáo:

```text
quảng cáo
→ bị remove
```

### False Positive

Nội dung thật bị coi là quảng cáo:

```text
nội dung bài viết
→ bị remove
```

Với crawler:

> **False positive thường nguy hiểm hơn bỏ sót một quảng cáo.**

Bởi vì dữ liệu bài viết đã bị mất.

---

# 9. False Negative

Ngược lại:

```text
quảng cáo
→ không bị remove
```

đây là:

```text
False Negative
```

Ví dụ:

```text
Advertisement
```

vẫn xuất hiện trong Markdown.

Tốt nhất:

```text
False Positive ↓↓↓
False Negative ↓
```

Nhưng không được đánh đổi bằng việc xóa nội dung thật.

---

# 10. Strategy 2 — Class heuristic

Thay vì:

```python
".ads"
```

ta kiểm tra class.

Ví dụ:

```html
<div class="ad-container banner-top">
```

Node có:

```text
class = "ad-container banner-top"
```

Ta có thể lấy:

```python
node.attributes.get("class")
```

Ví dụ:

```python
classes = node.attributes.get("class", "")
```

---

# 11. Tokenize class

Không nên:

```python
if "ad" in classes:
```

Vì đây là substring matching.

Tốt hơn:

```python
tokens = classes.split()
```

Ví dụ:

```text
"ad-container banner-top"
```

thành:

```python
[
    "ad-container",
    "banner-top",
]
```

---

# 12. Kiểm tra token

Ví dụ:

```python
AD_CLASS_KEYWORDS = {
    "ad",
    "ads",
    "advert",
    "advertisement",
    "advertising",
    "sponsor",
    "sponsored",
}
```

Sau đó:

```python
def has_ad_class(node) -> bool:
    classes = node.attributes.get("class", "")

    tokens = classes.lower().split()

    return any(
        token in AD_CLASS_KEYWORDS
        for token in tokens
    )
```

---

# 13. Nhưng `ad-container` thì sao?

Nếu:

```text
class = "ad-container"
```

thì:

```python
token = "ad-container"
```

không bằng:

```text
ad
```

Ta có thể dùng prefix:

```python
token.startswith("ad-")
```

Ví dụ:

```python
def looks_like_ad_class(token: str) -> bool:
    token = token.lower()

    if token in AD_CLASS_KEYWORDS:
        return True

    if token.startswith("ad-"):
        return True

    if token.startswith("ads-"):
        return True

    if token.startswith("advert"):
        return True

    return False
```

---

# 14. Nhưng đừng quá aggressive

Ví dụ:

```text
advertising
```

khá rõ.

Nhưng:

```text
address
```

không phải quảng cáo.

Do đó:

```python
token.startswith("ad")
```

là quá nguy hiểm.

Không nên:

```python
if token.startswith("ad"):
    remove()
```

---

# 15. Strategy 3 — ID heuristic

HTML:

```html
<div id="google_ads">
```

Ta có:

```python
node.attributes.get("id")
```

Ví dụ:

```python
def has_ad_id(node) -> bool:
    node_id = node.attributes.get("id", "")

    value = node_id.lower()

    return (
        "ad-" in value
        or
        "ads-" in value
        or
        "advert" in value
    )
```

---

# 16. Nhưng ID cũng không tuyệt đối

Ví dụ:

```html
<div id="advertisement">
```

rất rõ.

Nhưng:

```html
<div id="header-adapter">
```

có thể không phải quảng cáo.

Vì vậy:

```text
heuristic
```

chỉ là tín hiệu.

Không nên coi nó là sự thật tuyệt đối.

---

# 17. Strategy 4 — Attributes

Một số ad network dùng attribute:

```html
<div data-ad="true">
```

hoặc:

```html
<div data-ad-slot="12345">
```

Ta có thể kiểm tra:

```python
attrs = node.attributes
```

Ví dụ:

```python
def has_ad_attribute(node) -> bool:
    attrs = node.attributes

    if attrs.get("data-ad") == "true":
        return True

    if "data-ad-slot" in attrs:
        return True

    return False
```

---

# 18. Một số attribute khác

Ví dụ:

```html
<div
    data-ad-client="..."
    data-ad-slot="..."
>
```

Ta có thể:

```python
def has_ad_data(node) -> bool:
    attrs = node.attributes

    return any(
        key.startswith("data-ad")
        for key in attrs
    )
```

---

# 19. Cẩn thận với iframe

Quảng cáo thường nằm trong:

```html
<iframe>
```

Có thể remove:

```python
for node in root.css("iframe"):
    node.decompose()
```

Nhưng:

> **Không phải iframe nào cũng là quảng cáo.**

Ví dụ:

```text
YouTube
Vimeo
Google Maps
embedded content
```

đều có thể dùng iframe.

Do đó:

```python
iframe → advertisement
```

là assumption nguy hiểm.

---

# 20. Khi nào remove iframe?

Có thể tạo rule riêng:

```python
class RemoveAdIframeRule:
    ...
```

và chỉ remove iframe có tín hiệu:

```text
data-ad
ad class
ad id
ad URL
```

Ví dụ:

```html
<iframe src="https://ads.example.com/...">
```

có nhiều tín hiệu hơn:

```html
<iframe src="https://youtube.com/...">
```

---

# 21. Strategy 5 — Text heuristic

Ví dụ:

```html
<div>
    Advertisement
</div>
```

Có thể phát hiện:

```python
text = node.text(strip=True)
```

và:

```python
if text.lower() == "advertisement":
    ...
```

Nhưng đây cũng không nên là rule duy nhất.

---

# 22. Không nên:

```python
if "advertisement" in node.text().lower():
    node.decompose()
```

Vì:

```html
<p>
This article discusses how online advertisements work.
</p>
```

cũng chứa:

```text
advertisement
```

và sẽ bị xóa nhầm.

---

# 23. Text phải là tín hiệu

Tốt hơn:

```python
def looks_like_ad_text(node) -> bool:
    text = node.text().strip().lower()

    return text in {
        "advertisement",
        "sponsored",
        "sponsored content",
    }
```

Nhưng ngay cả vậy vẫn nên kết hợp với:

```text
class
id
attribute
position
```

---

# 24. Multi-signal detection

Đây là bước quan trọng nhất hôm nay.

Thay vì:

```text
1 signal → remove
```

ta có:

```text
class signal
id signal
attribute signal
text signal
iframe signal
       ↓
    scoring
       ↓
   confidence
       ↓
    remove?
```

Ví dụ:

```text
class = ad-container       +2
id = google_ads            +2
data-ad-slot               +3
text = Advertisement       +1
iframe                     +1
```

Tổng:

```text
9
```

→ gần như chắc chắn là quảng cáo.

---

# 25. Tạo `AdDetector`

```python
class AdDetector:

    def score(self, node) -> int:
        score = 0

        if self.has_ad_class(node):
            score += 2

        if self.has_ad_id(node):
            score += 2

        if self.has_ad_attribute(node):
            score += 3

        return score
```

---

# 26. `has_ad_class`

```python
class AdDetector:

    AD_CLASS_KEYWORDS = {
        "ad",
        "ads",
        "advertisement",
        "advertising",
        "sponsor",
        "sponsored",
    }

    def has_ad_class(self, node) -> bool:
        classes = node.attributes.get("class", "")

        tokens = classes.lower().split()

        return any(
            token in self.AD_CLASS_KEYWORDS
            for token in tokens
        )
```

---

# 27. `has_ad_id`

```python
def has_ad_id(self, node) -> bool:
    node_id = node.attributes.get("id", "")

    value = node_id.lower()

    keywords = (
        "advert",
        "ads-",
        "ad-",
        "google_ads",
    )

    return any(
        keyword in value
        for keyword in keywords
    )
```

---

# 28. `has_ad_attribute`

```python
def has_ad_attribute(self, node) -> bool:
    attrs = node.attributes

    if attrs.get("data-ad") == "true":
        return True

    if "data-ad-slot" in attrs:
        return True

    if "data-ad-client" in attrs:
        return True

    return False
```

---

# 29. Detector hoàn chỉnh

```python
class AdDetector:

    AD_CLASS_KEYWORDS = {
        "ad",
        "ads",
        "advertisement",
        "advertising",
        "sponsor",
        "sponsored",
    }

    def has_ad_class(self, node) -> bool:
        classes = node.attributes.get("class", "")

        tokens = classes.lower().split()

        return any(
            token in self.AD_CLASS_KEYWORDS
            for token in tokens
        )

    def has_ad_id(self, node) -> bool:
        node_id = node.attributes.get("id", "")

        value = node_id.lower()

        keywords = (
            "advert",
            "ads-",
            "ad-",
            "google_ads",
        )

        return any(
            keyword in value
            for keyword in keywords
        )

    def has_ad_attribute(self, node) -> bool:
        attrs = node.attributes

        return (
            attrs.get("data-ad") == "true"
            or "data-ad-slot" in attrs
            or "data-ad-client" in attrs
        )

    def score(self, node) -> int:
        score = 0

        if self.has_ad_class(node):
            score += 2

        if self.has_ad_id(node):
            score += 2

        if self.has_ad_attribute(node):
            score += 3

        return score
```

---

# 30. `is_ad`

Thêm threshold:

```python
def is_ad(self, node) -> bool:
    return self.score(node) >= 2
```

Bây giờ:

```python
detector = AdDetector()

if detector.is_ad(node):
    node.decompose()
```

---

# 31. Nhưng có vấn đề

Nếu:

```html
<div class="sponsored">
    Important article content
</div>
```

thì:

```text
score = 2
```

và bị xóa.

Vì vậy threshold không phải phép màu.

Ta phải hiểu:

> **Heuristic chỉ giúp tăng confidence, không đảm bảo chính xác 100%.**

---

# 32. Hard rules vs heuristic rules

Đây là cách thiết kế tốt hơn.

### Hard rule

Ví dụ:

```html
<div data-ad-slot="123">
```

Nếu website/documentation cho biết đây chắc chắn là ad:

```text
confidence = 100%
```

Có thể remove.

### Heuristic rule

Ví dụ:

```text
class="banner"
```

Không chắc chắn.

```text
confidence thấp
```

Không nên tự động remove.

---

# 33. `AdRemovalRule`

Ta có:

```python
class AdRemovalRule:

    def __init__(self, detector):
        self.detector = detector

    def apply(self, root):
        for node in root.css("*"):
            if self.detector.is_ad(node):
                node.decompose()
```

Sau đó:

```python
detector = AdDetector()
rule = AdRemovalRule(detector)

rule.apply(article)
```

---

# 34. Nhưng `root.css("*")` cần cẩn thận

Ta đang duyệt:

```text
article
 ├── div
 │    └── p
 ├── aside
 └── div
```

Nếu remove parent:

```text
div.ad
```

thì những child node bên trong cũng biến mất.

Do đó DOM mutation trong lúc iteration cần được xử lý cẩn thận.

Một cách an toàn hơn trong thiết kế rule là:

```text
1. tìm candidate
2. đánh giá candidate
3. lưu candidate
4. remove sau
```

---

# 35. Collect trước, remove sau

```python
def find_ads(self, root):
    candidates = []

    for node in root.css("*"):
        if self.detector.is_ad(node):
            candidates.append(node)

    return candidates
```

Sau đó:

```python
for node in candidates:
    node.decompose()
```

Pattern:

```text
Traverse
   ↓
Collect
   ↓
Evaluate
   ↓
Mutate
```

Đây là pattern rất hữu ích khi thao tác DOM.

---

# 36. Cleaner

```python
class HTMLCleaner:

    def __init__(self, rules):
        self.rules = list(rules)

    def clean(self, root):
        for rule in self.rules:
            rule.apply(root)
```

Dùng:

```python
cleaner = HTMLCleaner([
    AdRemovalRule(AdDetector()),
])
```

---

# 37. Thêm selector rule

Ta có thể kết hợp:

```python
class RemoveSelectorRule:

    def __init__(self, selectors):
        self.selectors = list(selectors)

    def apply(self, root):
        for selector in self.selectors:
            for node in root.css(selector):
                node.decompose()
```

Cleaner:

```python
cleaner = HTMLCleaner([
    RemoveSelectorRule([
        ".ads",
        ".advertisement",
    ]),
    AdRemovalRule(AdDetector()),
])
```

---

# 38. Pipeline lúc này

```text
Article
   │
   ▼
HTMLCleaner
   │
   ├── RemoveSelectorRule
   │
   └── AdRemovalRule
          │
          ▼
      Clean Article
```

Đây là architecture tốt hơn nhiều so với:

```python
clean()
```

chứa 500 dòng `if`.

---

# 39. Site-specific rule

Đây mới là thứ rất hữu ích khi crawler nhiều website.

Ví dụ:

```python
source_a_cleaner = HTMLCleaner([
    RemoveSelectorRule([
        ".ads",
        ".share",
        ".related",
    ])
])
```

Source B:

```python
source_b_cleaner = HTMLCleaner([
    RemoveSelectorRule([
        "#google_ads",
        ".banner-ad",
    ])
])
```

Source C:

```python
source_c_cleaner = HTMLCleaner([
    AdRemovalRule(AdDetector())
])
```

---

# 40. Generic + site-specific

Một kiến trúc thực tế:

```text
                    HTMLCleaner
                        │
             ┌──────────┴──────────┐
             │                     │
        Generic Rules        Site Rules
             │                     │
      script/style/ads       source-specific
```

Ví dụ:

```python
common_rules = [
    RemoveSelectorRule([
        "script",
        "style",
    ])
]
```

Website A:

```python
rules = [
    *common_rules,
    RemoveSelectorRule([
        ".site-a-ad",
    ]),
]
```

---

# 41. Điều này rất quan trọng với crawler truyện

Bạn có thể có:

```text
sources/
├── source_a.py
├── source_b.py
├── source_c.py
```

Mỗi source có:

```text
extractor
cleaner rules
parser
```

Nhưng engine:

```text
HTMLCleaner
```

dùng chung.

---

# 42. Một ví dụ hoàn chỉnh

HTML:

```python
html = """
<article>

<h1>Python</h1>

<p>Python is powerful.</p>

<div class="ads">
    Advertisement
</div>

<div
    class="banner"
    data-ad="true"
>
    Buy now!
</div>

<div class="content">
    <p>This is real content.</p>
</div>

<p>Python is useful for crawling.</p>

</article>
"""
```

---

# 43. Parse

```python
tree = HTMLParser(html)

article = tree.css_first("article")
```

---

# 44. Cleaner

```python
cleaner = HTMLCleaner([
    RemoveSelectorRule([
        ".ads",
    ]),
    AdRemovalRule(
        AdDetector()
    ),
])

cleaner.clean(article)
```

---

# 45. Kết quả

```html
<article>

<h1>Python</h1>

<p>Python is powerful.</p>

<div class="content">
    <p>This is real content.</p>
</div>

<p>Python is useful for crawling.</p>

</article>
```

`content` vẫn còn.

Đây là điều quan trọng.

---

# 46. Sau đó html2text

```python
import html2text

converter = html2text.HTML2Text()
converter.body_width = 0

markdown = converter.handle(article.html)

print(markdown)
```

Kết quả gần như:

```markdown
# Python

Python is powerful.

This is real content.

Python is useful for crawling.
```

---

# 47. Đừng remove tất cả banner

Một lỗi phổ biến:

```python
RemoveSelectorRule([
    ".banner",
])
```

Có thể xóa:

```html
<div class="banner">
    Important story information
</div>
```

Trong website khác:

```text
banner = advertisement
```

Nhưng website khác:

```text
banner = article content
```

Vì vậy:

```text
selector meaning
```

phụ thuộc website.

---

# 48. Đừng remove `sponsor` một cách mù quáng

Ví dụ:

```html
<p>
Sponsored by...
</p>
```

có thể đúng là sponsored content.

Nhưng nếu crawler của bạn lưu:

```text
metadata
author
source
```

thì việc remove toàn bộ `sponsor` có thể làm mất metadata.

Cleaner phải có scope:

```text
Article content cleaning
```

không phải:

```text
Delete everything that looks suspicious
```

---

# 49. Một nguyên tắc rất quan trọng

Khi xây crawler:

> **Preserve content by default.**

Tức là:

```text
Không chắc?
→ Giữ lại.
```

thay vì:

```text
Không chắc?
→ Xóa.
```

Đặc biệt khi dữ liệu dùng để lưu trữ lâu dài.

---

# 50. Logging

Một AdRemovalRule tốt nên có khả năng debug.

Ví dụ:

```python
class AdRemovalRule:

    def apply(self, root):
        removed = 0

        for node in self.find_ads(root):
            node.decompose()
            removed += 1

        return removed
```

Sau đó:

```python
removed = rule.apply(article)

print(f"Removed {removed} ad nodes")
```

---

# 51. Tốt hơn nữa: lý do

Ta muốn biết:

```text
Node removed
Reason:
    data-ad-slot
```

hoặc:

```text
Reason:
    selector=.ads
```

hoặc:

```text
Reason:
    class=advertisement
```

Sau này rất hữu ích khi debug crawler.

---

# 52. Ad detection result

Có thể thiết kế:

```python
class DetectionResult:

    def __init__(self, is_ad, score, reasons):
        self.is_ad = is_ad
        self.score = score
        self.reasons = reasons
```

Ví dụ:

```text
is_ad = True
score = 5
reasons = [
    "ad_class",
    "data-ad-slot",
]
```

Nhưng ở Buổi 16 chưa cần triển khai phức tạp.

Chỉ cần hiểu hướng thiết kế.

---

# 53. Test cực kỳ quan trọng

Ta cần test cả:

### Advertisement

```html
<div class="ads">
```

→ remove.

### Real content

```html
<div class="content">
```

→ giữ.

### Ambiguous

```html
<div class="banner">
```

→ giữ nếu không đủ confidence.

### Strong signal

```html
<div data-ad-slot="123">
```

→ remove.

---

# 54. Test 1

```python
def test_remove_ads():
    html = """
    <article>
        <p>Hello</p>
        <div class="ads">Buy</div>
        <p>World</p>
    </article>
    """

    tree = HTMLParser(html)
    article = tree.css_first("article")

    rule = RemoveSelectorRule([".ads"])
    rule.apply(article)

    result = article.html

    assert "Buy" not in result
    assert "Hello" in result
    assert "World" in result
```

---

# 55. Test 2

```python
def test_keep_content():
    html = """
    <article>
        <div class="content">
            Important content
        </div>
    </article>
    """

    tree = HTMLParser(html)
    article = tree.css_first("article")

    detector = AdDetector()

    for node in article.css("*"):
        assert not detector.is_ad(node)
```

---

# 56. Test 3

```python
def test_data_ad():
    html = """
    <article>
        <div data-ad="true">
            Advertisement
        </div>
    </article>
    """

    tree = HTMLParser(html)
    article = tree.css_first("article")

    detector = AdDetector()

    node = article.css_first("[data-ad]")

    assert detector.is_ad(node)
```

---

# 57. Test 4 — False positive

```python
def test_do_not_remove_content():
    html = """
    <article>
        <div class="content">
            Python article
        </div>
    </article>
    """

    tree = HTMLParser(html)
    article = tree.css_first("article")

    detector = AdDetector()

    node = article.css_first(".content")

    assert not detector.is_ad(node)
```

Test này cực kỳ quan trọng.

---

# 58. Bài tập thực hành chính

Tạo:

```text
htmlcleaner/
├── __init__.py
├── cleaner.py
├── rules.py
├── detector.py
└── tests/
    ├── test_ads.py
    └── test_cleaner.py
```

Architecture:

```text
HTMLCleaner
    │
    └── Rule[]
          │
          ├── RemoveSelectorRule
          │
          └── AdRemovalRule
                         │
                         ▼
                     AdDetector
```

---

# 59. Bài tập 1

Implement:

```python
class RemoveSelectorRule:
    ...
```

API:

```python
rule = RemoveSelectorRule([
    ".ads",
    ".advertisement",
])
```

---

# 60. Bài tập 2

Implement:

```python
class AdDetector:
    ...
```

Hỗ trợ:

```text
class
id
data-ad
data-ad-slot
```

---

# 61. Bài tập 3

Implement:

```python
class AdRemovalRule:
    ...
```

Không được trực tiếp viết:

```python
if ".ads":
```

trong Cleaner.

Cleaner chỉ biết:

```python
rule.apply(root)
```

---

# 62. Bài tập 4

Tạo:

```python
HTMLCleaner([
    RemoveSelectorRule([
        "script",
        "style",
    ]),
    AdRemovalRule(
        AdDetector()
    ),
])
```

Sau đó:

```python
cleaner.clean(article)
```

---

# 63. Bài tập 5 — HTML thực tế

Hãy test HTML:

```html
<article>

<h1>Python</h1>

<p>Python is a programming language.</p>

<div class="top-banner">
    Advertisement
</div>

<div class="article-content">
    <p>Python is easy to learn.</p>
</div>

<div data-ad="true">
    Buy something
</div>

<div class="related">
    Related article
</div>

<p>Python is powerful.</p>

</article>
```

Yêu cầu:

```text
top-banner
data-ad
```

được xử lý theo rule của bạn.

Nhưng:

```text
article-content
```

phải giữ.

---

# 64. Bài tập 6 — Đừng xóa `.banner`

Thử:

```html
<div class="banner">
    Important information
</div>
```

Detector phải **không tự động coi nó là quảng cáo** nếu chỉ dựa vào class `banner`.

Đây là bài tập để hiểu:

```text
high precision
```

quan trọng thế nào.

---

# 65. Bài tập 7 — Scoring

Mở rộng:

```python
score(node)
```

Ví dụ:

```text
class ad-container       +2
id google_ads            +2
data-ad-slot             +3
```

Sau đó:

```python
score >= 3
```

→ remove.

Thử nghiệm các threshold:

```text
1
2
3
4
```

và quan sát false positive / false negative.

---

# 66. Kiến trúc cuối buổi

Chúng ta đã từ:

```text
Remove ".ads"
```

tiến tới:

```text
                    HTMLCleaner
                         │
                         ▼
                      Rules
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
   RemoveSelectorRule          AdRemovalRule
                                     │
                                     ▼
                                AdDetector
                                     │
                       ┌─────────────┼─────────────┐
                       ▼             ▼             ▼
                     class           id        attributes
                       │             │             │
                       └─────────────┼─────────────┘
                                     ▼
                                   score
                                     │
                                     ▼
                                remove / keep
```

---

# 67. Mental model quan trọng nhất

Hãy nhớ:

```text
Selector
    ↓
High precision
```

```text
Heuristic
    ↓
Flexible
```

```text
Scoring
    ↓
Combine multiple signals
```

và:

```text
Không chắc
    ↓
KEEP
```

Đây là nguyên tắc rất quan trọng khi làm data extraction.

---

# 68. Toàn bộ pipeline hiện tại

```text
                    HTTPX
                      ↓
                     HTML
                      ↓
                Selectolax
                      ↓
             ArticleExtractor
                      ↓
                  Article
                      ↓
               HTMLCleaner
                      ↓
        ┌─────────────┴─────────────┐
        │                           │
   Generic Rules              Site Rules
        │                           │
        └─────────────┬─────────────┘
                      ↓
                Clean Article
                      ↓
                 article.html
                      ↓
                  html2text
                      ↓
                  Markdown
```

---

## Tóm tắt Buổi 16

5 điều cần nhớ:

```text
1. Remove quảng cáo không đơn giản chỉ là ".ads".

2. CSS selector là cách chính xác nhất khi biết cấu trúc website.

3. Class/id/attribute có thể dùng làm heuristic.

4. Nên kết hợp nhiều signal thay vì dựa vào một heuristic duy nhất.

5. Khi không chắc một node là quảng cáo → ưu tiên GIỮ nội dung.
```

Buổi tiếp theo **Buổi 17 — Remove Navigation** sẽ giải quyết một vấn đề tương tự nhưng có một điểm khác rất quan trọng: navigation thường **không có dấu hiệu "ad"**, mà phải nhận diện qua cấu trúc như `nav`, `header`, `menu`, breadcrumb, sidebar, link density... Đây cũng là bước đầu để tiến tới **Article Extraction** ở Buổi 20.
