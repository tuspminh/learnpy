# 📘 Selectolax — Buổi 14: Testing Selectolax

Đây là buổi cuối của **Phần III — Selectolax nâng cao**.

Sau buổi này, chúng ta sẽ có tư duy:

```text
HTML
 ↓
Parser
 ↓
Extractor
 ↓
Article
 ↓
Test
```

Thay vì chỉ kiểm tra:

> "Scraper chạy được không?"

ta kiểm tra:

> **"Scraper có lấy đúng dữ liệu không?"**

---

# 1. Vì sao scraper rất cần test?

Scraper có một đặc điểm nguy hiểm:

Website có thể thay đổi HTML mà **không báo cho bạn**.

Hôm nay:

```html
<h1 class="article-title">
    Python
</h1>
```

Ngày mai:

```html
<h1 class="post-title">
    Python
</h1>
```

Code cũ:

```python
node = tree.css_first(
    ".article-title"
)
```

không crash.

Nhưng:

```python
node is None
```

và bạn có thể vô tình lưu:

```text
title = None
```

cho hàng nghìn bài.

Đây là lý do:

> **Regression test cực kỳ quan trọng đối với scraper.**

---

# 2. Chúng ta dùng pytest

Cài:

```bash
pip install pytest
```

Cấu trúc:

```text
selectolax_scraper/
│
├── app/
│   ├── model.py
│   ├── parser.py
│   ├── extractor.py
│   └── service.py
│
└── tests/
    ├── fixtures/
    │   └── article.html
    ├── test_parser.py
    ├── test_selector.py
    └── test_extractor.py
```

---

# 3. HTML Fixture

Fixture là HTML mẫu dùng trong test.

Tạo:

```text
tests/fixtures/article.html
```

Nội dung:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Test Article</title>
</head>

<body>

<header>
    Navigation
</header>

<article class="article">

    <h1 class="article-title">
        Python Selectolax
    </h1>

    <div class="author">
        Garden
    </div>

    <div class="article-content">
        <p>Selectolax is fast.</p>
        <p>It is useful for scraping.</p>
    </div>

    <img
        class="cover"
        src="/images/python.jpg"
    >

</article>

<footer>
    Footer
</footer>

</body>
</html>
```

---

# 4. Vì sao dùng fixture thay vì viết HTML trong test?

Không nên:

```python
def test_title():

    html = """
    <html>
        ...
    </html>
    """

    ...
```

Nếu HTML lớn:

```text
test_extractor.py
→ 500 dòng HTML
→ 20 dòng test
```

Rất khó đọc.

Tốt hơn:

```text
fixtures/
└── article.html
```

Test chỉ tập trung vào behavior.

---

# 5. Đọc fixture

```python
from pathlib import Path


FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> str:
    return (
        FIXTURES / name
    ).read_text(
        encoding="utf-8"
    )
```

Dùng:

```python
html = load_fixture(
    "article.html"
)
```

---

# 6. Test Parser

Giả sử:

```python
# app/parser.py

from selectolax.parser import HTMLParser


def parse(html: str) -> HTMLParser:
    return HTMLParser(html)
```

Test:

```python
# tests/test_parser.py

from app.parser import parse


def test_parse_html():

    html = """
    <html>
        <body>
            <h1>Hello</h1>
        </body>
    </html>
    """

    tree = parse(html)

    assert tree is not None
```

Chạy:

```bash
pytest
```

---

# 7. Test parser với fixture

```python
from app.parser import parse


def test_parse_article():

    html = load_fixture(
        "article.html"
    )

    tree = parse(html)

    assert tree.css_first(
        "article"
    ) is not None
```

Ta đang kiểm tra:

```text
HTML
 ↓
Selectolax
 ↓
DOM
 ↓
article tồn tại
```

---

# 8. Test CSS Selector

Đây là loại test rất hữu ích.

```python
def test_title_selector():

    html = load_fixture(
        "article.html"
    )

    tree = parse(html)

    node = tree.css_first(
        ".article-title"
    )

    assert node is not None
```

Sau đó kiểm tra text:

```python
assert node.text(
    strip=True
) == "Python Selectolax"
```

---

# 9. Test author

```python
def test_author_selector():

    html = load_fixture(
        "article.html"
    )

    tree = parse(html)

    node = tree.css_first(
        ".author"
    )

    assert node is not None

    assert node.text(
        strip=True
    ) == "Garden"
```

---

# 10. Test content

```python
def test_content_selector():

    html = load_fixture(
        "article.html"
    )

    tree = parse(html)

    node = tree.css_first(
        ".article-content"
    )

    assert node is not None

    text = node.text(
        separator="\n",
        strip=True,
    )

    assert (
        text
        == "Selectolax is fast.\n"
        "It is useful for scraping."
    )
```

---

# 11. Test image

```python
def test_cover_image():

    html = load_fixture(
        "article.html"
    )

    tree = parse(html)

    node = tree.css_first(
        "img.cover"
    )

    assert node is not None

    assert (
        node.attributes.get("src")
        == "/images/python.jpg"
    )
```

---

# 12. Nhưng test selector riêng chưa đủ

Ta có:

```text
test selector
```

nhưng application thực tế dùng:

```text
Extractor
```

Vì vậy quan trọng nhất là:

> **Test extractor.**

---

# 13. Model

Ví dụ:

```python
from dataclasses import dataclass


@dataclass
class Article:
    title: str
    content: str
    author: str | None = None
```

Extractor:

```python
class ArticleExtractor:

    def extract(self, tree):

        title_node = tree.css_first(
            ".article-title"
        )

        content_node = tree.css_first(
            ".article-content"
        )

        author_node = tree.css_first(
            ".author"
        )

        if not title_node:
            raise ValueError(
                "Missing title"
            )

        if not content_node:
            raise ValueError(
                "Missing content"
            )

        return Article(
            title=title_node.text(
                strip=True
            ),
            content=content_node.text(
                separator="\n",
                strip=True,
            ),
            author=(
                author_node.text(
                    strip=True
                )
                if author_node
                else None
            ),
        )
```

---

# 14. Test Extractor

```python
from app.parser import parse
from app.extractor import ArticleExtractor


def test_extract_article():

    html = load_fixture(
        "article.html"
    )

    tree = parse(html)

    extractor = ArticleExtractor()

    article = extractor.extract(
        tree
    )

    assert article.title == (
        "Python Selectolax"
    )

    assert article.author == (
        "Garden"
    )

    assert article.content == (
        "Selectolax is fast.\n"
        "It is useful for scraping."
    )
```

---

# 15. Test toàn bộ object

Có thể dùng:

```python
assert article == Article(
    title="Python Selectolax",
    content=(
        "Selectolax is fast.\n"
        "It is useful for scraping."
    ),
    author="Garden",
)
```

Đây là lợi thế của `dataclass`.

---

# 16. Test missing selector

Tạo fixture:

```text
tests/fixtures/
├── article.html
└── missing_title.html
```

`missing_title.html`:

```html
<html>
<body>

<article>

    <div class="article-content">
        Hello
    </div>

</article>

</body>
</html>
```

Test:

```python
import pytest


def test_missing_title():

    html = load_fixture(
        "missing_title.html"
    )

    tree = parse(html)

    extractor = ArticleExtractor()

    with pytest.raises(
        ValueError,
        match="Missing title",
    ):
        extractor.extract(tree)
```

---

# 17. Tại sao test exception?

Bởi vì:

```text
missing title
```

là behavior mà chúng ta **đã thiết kế**.

Ta muốn đảm bảo refactor sau này không biến thành:

```python
return Article(
    title=None,
    ...
)
```

một cách vô tình.

---

# 18. Test optional field

Tạo:

```text
missing_author.html
```

```html
<article>

    <h1 class="article-title">
        Python
    </h1>

    <div class="article-content">
        Hello
    </div>

</article>
```

Test:

```python
def test_missing_author():

    html = load_fixture(
        "missing_author.html"
    )

    tree = parse(html)

    article = (
        ArticleExtractor()
        .extract(tree)
    )

    assert article.title == "Python"

    assert article.author is None
```

Đây là distinction:

```text
required
→ exception

optional
→ None
```

---

# 19. Regression Test

Đây là phần quan trọng nhất.

Giả sử website thay đổi:

### Version cũ

```html
<h1 class="article-title">
```

### Version mới

```html
<h1 class="post-title">
```

Ta tạo fixture:

```text
tests/fixtures/
├── article.html
└── changed_layout.html
```

---

# 20. `changed_layout.html`

```html
<html>
<body>

<article>

    <h1 class="post-title">
        Python Selectolax
    </h1>

    <div class="post-content">
        Selectolax is fast.
    </div>

</article>

</body>
</html>
```

Nếu extractor hiện tại chỉ có:

```python
tree.css_first(
    ".article-title"
)
```

test sẽ fail.

Đây là **tốt**.

Test đang nói:

> Website đã thay đổi cấu trúc.

---

# 21. Thêm fallback

Ta sửa:

```python
title_node = first_match(
    tree,
    (
        ".article-title",
        ".post-title",
        "article h1",
    ),
)
```

Content:

```python
content_node = first_match(
    tree,
    (
        ".article-content",
        ".post-content",
        "article .content",
    ),
)
```

---

# 22. Test regression

```python
def test_changed_layout():

    html = load_fixture(
        "changed_layout.html"
    )

    tree = parse(html)

    article = (
        ArticleExtractor()
        .extract(tree)
    )

    assert article.title == (
        "Python Selectolax"
    )

    assert article.content == (
        "Selectolax is fast."
    )
```

Bây giờ extractor đã hỗ trợ cả:

```text
v1 HTML
v2 HTML
```

---

# 23. Regression test thực chất là gì?

Không chỉ:

```text
"test code"
```

mà là:

```text
HTML thực tế đã từng xuất hiện
             ↓
          lưu lại
             ↓
         fixture
             ↓
           test
```

Ví dụ bạn crawl một website.

Một ngày phát hiện:

```text
article.html
```

đã thay đổi.

Bạn lưu HTML mới:

```text
fixtures/site_a_2026_08.html
```

và viết test.

Từ đó về sau:

```text
Refactor
 ↓
pytest
 ↓
Nếu selector hỏng
 ↓
Test fail
```

---

# 24. Đây là "contract" của scraper

Ví dụ:

```text
ArticleExtractor contract
```

phải đảm bảo:

```text
title → không rỗng
content → không rỗng
author → optional
```

Test trở thành contract:

```python
assert article.title
assert article.content
```

---

# 25. Parametrize

Nếu có nhiều HTML structure:

```text
site_a
site_b
site_c
```

không cần viết:

```text
test_site_a
test_site_b
test_site_c
```

có thể dùng:

```python
import pytest


@pytest.mark.parametrize(
    "fixture_name,expected_title",
    [
        (
            "article.html",
            "Python Selectolax",
        ),
        (
            "changed_layout.html",
            "Python Selectolax",
        ),
    ],
)
def test_title_variants(
    fixture_name,
    expected_title,
):

    html = load_fixture(
        fixture_name
    )

    tree = parse(html)

    article = (
        ArticleExtractor()
        .extract(tree)
    )

    assert article.title == (
        expected_title
    )
```

Rất tiện khi scraper hỗ trợ nhiều layout.

---

# 26. Test helper `text_first`

Ở Buổi 12 chúng ta có:

```python
def text_first(
    root,
    selectors,
):
    for selector in selectors:

        node = root.css_first(
            selector
        )

        if node is None:
            continue

        value = node.text(
            strip=True
        )

        if value:
            return value

    return None
```

Đây cũng cần test.

---

# 27. Test selector fallback

```python
def test_text_first():

    html = """
    <article>
        <h1 class="post-title">
            Hello
        </h1>
    </article>
    """

    tree = parse(html)

    result = text_first(
        tree,
        (
            ".article-title",
            ".post-title",
            "h1",
        ),
    )

    assert result == "Hello"
```

---

# 28. Test tất cả selector đều fail

```python
def test_text_first_returns_none():

    html = """
    <article>
        <div>Hello</div>
    </article>
    """

    tree = parse(html)

    result = text_first(
        tree,
        (
            ".title",
            ".post-title",
            ".article-title",
        ),
    )

    assert result is None
```

---

# 29. Test empty text

HTML:

```html
<h1 class="title"></h1>
```

Test:

```python
def test_empty_text():

    html = """
    <h1 class="title"></h1>
    """

    tree = parse(html)

    result = text_first(
        tree,
        (".title",),
    )

    assert result is None
```

Đây là test rất tốt cho defensive extraction.

---

# 30. Test missing attribute

```python
def test_missing_attribute():

    html = """
    <img class="cover">
    """

    tree = parse(html)

    image = tree.css_first(
        "img.cover"
    )

    assert image is not None

    src = image.attributes.get(
        "src"
    )

    assert src is None
```

---

# 31. Test malformed HTML

Fixture:

```html
<article>
    <h1>Python
    <div class="content">
        Hello
</article>
```

Test:

```python
def test_malformed_html():

    html = load_fixture(
        "malformed.html"
    )

    tree = parse(html)

    assert tree is not None

    title = tree.css_first("h1")

    assert title is not None
```

Mục tiêu ở đây không phải chứng minh parser xử lý mọi HTML lỗi.

Mà là:

> HTML không hoàn hảo nhưng parser vẫn tạo được DOM usable cho case của chúng ta.

---

# 32. Test empty HTML

```python
def test_empty_html():

    html = ""

    with pytest.raises(
        ValueError,
        match="HTML cannot be empty",
    ):
        parse(html)
```

Nếu parser của bạn chưa có validation:

```python
def parse(html):

    if not html:
        raise ValueError(
            "HTML cannot be empty"
        )

    return HTMLParser(html)
```

---

# 33. Test whitespace HTML

```python
def test_whitespace_html():

    html = "   \n\t  "

    with pytest.raises(
        ValueError,
    ):
        parse(html)
```

Tốt hơn parser:

```python
def parse(html):

    if not html or not html.strip():
        raise ValueError(
            "HTML cannot be empty"
        )

    return HTMLParser(html)
```

---

# 34. Fixture càng thực tế càng tốt

Đừng tạo fixture quá đẹp:

```html
<h1>Hello</h1>
<div>Content</div>
```

Trong production:

```text
HTML
├── script
├── style
├── nav
├── ads
├── comments
├── tracking
├── article
│   ├── title
│   ├── author
│   └── content
└── footer
```

Fixture nên phản ánh HTML thật.

---

# 35. Fixture thực tế

Ví dụ:

```html
<body>

<script>
    console.log("tracking");
</script>

<nav>
    Home
    Books
</nav>

<div class="advertisement">
    BUY NOW
</div>

<article>

    <h1 class="article-title">
        Python Selectolax
    </h1>

    <div class="author">
        Garden
    </div>

    <div class="article-content">

        <p>
            Selectolax is fast.
        </p>

        <p>
            It is useful for scraping.
        </p>

    </div>

</article>

<footer>
    Footer
</footer>

</body>
```

Extractor phải lấy đúng:

```text
title
author
content
```

và không quan tâm:

```text
nav
advertisement
footer
script
```

---

# 36. Test content không chứa advertisement

Ví dụ:

```python
def test_content_does_not_include_ads():

    html = load_fixture(
        "article_with_ads.html"
    )

    tree = parse(html)

    article = (
        ArticleExtractor()
        .extract(tree)
    )

    assert "BUY NOW" not in (
        article.content
    )
```

Đây là test **behavior**, rất hữu ích.

---

# 37. Test thứ tự paragraph

Nếu article:

```html
<p>One</p>
<p>Two</p>
<p>Three</p>
```

thì:

```python
assert article.content == (
    "One\n"
    "Two\n"
    "Three"
)
```

Đừng chỉ test:

```python
assert "One" in content
```

vì thứ tự cũng có thể quan trọng.

---

# 38. Test image list

Nếu Article có:

```python
@dataclass
class Article:
    title: str
    content: str
    images: list[str]
```

test:

```python
assert article.images == [
    "/a.jpg",
    "/b.jpg",
]
```

Không nên chỉ:

```python
assert len(article.images) == 2
```

vì URL có thể sai nhưng test vẫn pass.

---

# 39. Test URL normalization

Nếu extractor chuyển:

```text
/images/a.jpg
```

thành:

```text
https://example.com/images/a.jpg
```

hãy test chính xác:

```python
assert article.images == [
    "https://example.com/images/a.jpg"
]
```

Những transformation này rất dễ regression.

---

# 40. Unit test vs Integration test

Đây là điểm quan trọng.

### Unit test

```text
HTML fixture
 ↓
Parser
 ↓
Extractor
 ↓
Article
```

Không có:

```text
Internet
Database
```

Nhanh.

---

### Integration test

```text
HTTPX
 ↓
Real website
 ↓
Selectolax
 ↓
Extractor
```

Chậm hơn và phụ thuộc network.

---

# 41. Không nên dùng website thật cho unit test

Sai:

```python
def test_article():

    response = httpx.get(
        "https://example.com/article"
    )

    ...
```

Test có thể fail vì:

```text
network down
website down
rate limit
Cloudflare
website changed
DNS
timeout
```

Trong khi code extractor hoàn toàn đúng.

---

# 42. Unit test phải deterministic

Tốt:

```text
fixture
 ↓
parse
 ↓
extract
 ↓
assert
```

Kết quả phải giống nhau:

```text
run 1 → pass
run 2 → pass
run 3 → pass
```

---

# 43. Integration test nên ít

Bạn có thể có:

```text
tests/
├── unit/
│   ├── test_parser.py
│   └── test_extractor.py
│
└── integration/
    └── test_site_a.py
```

Phần lớn test:

```text
unit
```

Một số ít:

```text
integration
```

---

# 44. Golden HTML

Một kỹ thuật rất hay cho scraper:

```text
Golden fixture
```

Bạn lưu HTML thực tế:

```text
fixtures/
├── site_a_article_v1.html
├── site_a_article_v2.html
└── site_b_article_v1.html
```

Sau đó:

```text
fixture
 ↓
extractor
 ↓
expected Article
```

Nếu website thay đổi:

```text
test fail
```

Bạn biết chính xác layout nào bị ảnh hưởng.

---

# 45. Snapshot tư duy

Bạn có thể xem:

```text
HTML
 ↓
Article
```

là một transformation.

Ví dụ expected:

```python
Article(
    title="Python",
    author="Garden",
    content="Hello",
)
```

Nếu sau refactor:

```python
Article(
    title="Python",
    author=None,
    content="",
)
```

test lập tức phát hiện.

---

# 46. Test parser và extractor nên tách

Không nên chỉ có:

```text
test_everything()
```

Tốt hơn:

```text
test_parser
test_selector
test_extractor
```

Khi fail:

```text
test_parser
→ parser lỗi

test_selector
→ selector lỗi

test_extractor
→ business extraction lỗi
```

Debug nhanh hơn.

---

# 47. Một bộ test hoàn chỉnh

```text
tests/
│
├── fixtures/
│   ├── article.html
│   ├── missing_title.html
│   ├── missing_author.html
│   ├── malformed.html
│   ├── changed_layout.html
│   └── article_with_ads.html
│
├── test_parser.py
├── test_selector.py
└── test_extractor.py
```

---

# 48. Test pyramid cho scraper

Tôi khuyên:

```text
                 /\
                /  \
               / E2E\
              /------\
             / Integr \
            /----------\
           / Unit Tests \
          /--------------\
```

Số lượng:

```text
Unit
████████████████████

Integration
████

E2E
█
```

Vì unit test:

```text
nhanh
ổn định
không cần internet
```

---

# 49. Test Extractor bằng dependency injection

Nếu:

```python
class ArticleExtractor:
    def extract(self, tree):
        ...
```

thì test cực đơn giản.

Bạn không cần:

```text
HTTPX
server
database
```

Chỉ:

```python
tree = parse(html)
article = extractor.extract(tree)
```

Đây chính là lợi ích của architecture Buổi 13.

---

# 50. Kiến trúc + Testing

Bây giờ nhìn lại:

```text
                  ArticleScraper
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Parser       Extractor    Repository
          │            │
          ▼            ▼
      Selectolax     Article
```

Test riêng:

```text
Parser
  ↓
test_parser.py
```

```text
Extractor
  ↓
test_extractor.py
```

```text
Repository
  ↓
test_repository.py
```

Đây chính là lý do separation of concerns quan trọng.

---

# 51. Một nguyên tắc cực kỳ quan trọng

Đừng test implementation.

Hãy test behavior.

Không nên quá phụ thuộc vào:

```python
assert extractor._title_selector == ...
```

Tốt hơn:

```python
assert article.title == "Python"
```

Nếu bạn thay:

```text
CSS selector
```

nhưng output vẫn đúng:

```text
test vẫn pass
```

Đó là test tốt.

---

# 52. Test selector trực tiếp khi nào?

Có.

Nếu selector là logic quan trọng:

```python
node = tree.css_first(
    ".article-title"
)
```

test trực tiếp giúp debug nhanh.

Nhưng test quan trọng nhất vẫn là:

```text
HTML
 ↓
Extractor
 ↓
Expected data
```

---

# 53. Regression test tốt nhất

Giả sử production gặp lỗi:

```text
Ngày 28/08:
title bị None
```

Bạn lấy HTML production về:

```text
production_bug.html
```

Sau đó:

```text
tests/fixtures/
└── production_bug.html
```

Viết test:

```python
def test_production_bug_2026_08_28():

    html = load_fixture(
        "production_bug.html"
    )

    tree = parse(html)

    article = (
        ArticleExtractor()
        .extract(tree)
    )

    assert article.title == (
        "Expected title"
    )
```

Sửa code.

Test pass.

Từ giờ lỗi này **không được phép quay trở lại**.

Đây chính là regression testing đúng nghĩa.

---

# 54. Workflow tôi khuyên dùng

Khi scraper gặp lỗi:

```text
Production bug
      ↓
Save HTML
      ↓
Create fixture
      ↓
Write failing test
      ↓
Fix extractor
      ↓
Test passes
      ↓
Deploy
```

Đừng chỉ:

```text
fix code
→ deploy
```

vì lỗi rất dễ quay lại.

---

# 55. Bài tập chính

Hãy xây bộ test:

```text
tests/
│
├── fixtures/
│   ├── article.html
│   ├── missing_title.html
│   ├── missing_author.html
│   ├── malformed.html
│   └── changed_layout.html
│
├── test_parser.py
├── test_selector.py
└── test_extractor.py
```

Phải có ít nhất:

```text
✓ parse HTML
✓ title selector
✓ author selector
✓ content selector
✓ image selector
✓ missing title
✓ missing author
✓ empty HTML
✓ malformed HTML
✓ fallback selector
✓ changed layout
```

---

# 56. Bài tập nâng cao

Viết:

```python
@pytest.mark.parametrize(...)
```

để test:

```text
article.html
changed_layout.html
```

đều phải trả:

```python
Article(
    title="Python Selectolax",
    content="...",
)
```

Sau đó thêm:

```text
article_v3.html
article_v4.html
```

mỗi file đại diện cho một layout mà scraper từng gặp.

Bạn sẽ bắt đầu có một **test suite cho nhiều phiên bản HTML**.

---

# 57. Bài tập Production

Đây là bài tôi đặc biệt khuyến khích bạn làm.

Tạo:

```text
fixtures/
└── real_site/
```

Mỗi khi scraper gặp một HTML lỗi:

```text
real_site/
├── article_001.html
├── article_002.html
├── article_003.html
```

Thêm test tương ứng.

Sau một thời gian:

```text
100 real HTML samples
```

Bạn đã có một dataset regression cực kỳ giá trị.

---

# 58. Tổng kết toàn bộ Phần III

Chúng ta đã đi:

### Buổi 9

```text
CSS Selector nâng cao
```

### Buổi 10

```text
DOM Traversal
```

### Buổi 11

```text
Performance
```

### Buổi 12

```text
Error Handling
```

### Buổi 13

```text
Scraper Architecture
```

### Buổi 14

```text
Testing
```

Và cuối cùng:

```text
               Scraper
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
      HTTP                Tests
        │                   │
        ▼                   ▼
      HTML               Fixtures
        │
        ▼
     Parser
        │
        ▼
    Selectolax
        │
        ▼
    Extractor
        │
        ▼
     Model
        │
        ▼
   Repository
```

---

# 🧠 6 nguyên tắc cần nhớ

### 1. HTML là external input

```text
HTML có thể thay đổi
```

### 2. Extractor phải defensive

```text
missing node
missing attribute
empty text
```

phải được xử lý.

### 3. Parser và Extractor tách biệt

```text
Parser
→ HTML → DOM

Extractor
→ DOM → Data
```

### 4. Test bằng fixture

```text
HTML thật
→ lưu lại
→ test
```

### 5. Regression test rất quan trọng

```text
Bug
 ↓
HTML fixture
 ↓
Failing test
 ↓
Fix
 ↓
Permanent protection
```

### 6. Test behavior, không test implementation

```python
assert article.title == "Python"
```

quan trọng hơn:

```python
assert selector == ".article-title"
```

---

# 🎓 Bạn đã hoàn thành Selectolax Advanced

Đến đây bạn đã đủ nền tảng để xây một scraper thực tế:

```text
HTTPX
   ↓
HTML
   ↓
Selectolax
   ↓
Parser
   ↓
Extractor
   ↓
Model
   ↓
Repository
   ↓
SQLite
```

Và quan trọng hơn, bạn đã có nền tảng để kết hợp Selectolax với những thứ bạn đang học như **HTTPX, asyncio, SQLite, Repository Pattern, Clean Architecture và crawler worker**.

### 🚀 Chặng tiếp theo tôi đề xuất

Nếu tiếp tục đào sâu Selectolax, phần hợp lý nhất là **Phần IV — Xây dựng một Scraper Framework thực tế**:

```text
Buổi 15 — Base Parser / Base Extractor
Buổi 16 — Multi-site Extractor
Buổi 17 — URL & Link Extractor
Buổi 18 — Pagination Engine
Buổi 19 — HTML Cleaner
Buổi 20 — Article Content Extractor
Buổi 21 — Image Extractor
Buổi 22 — Metadata / JSON-LD
Buổi 23 — Site Plugin Architecture
Buổi 24 — Scraper Pipeline
Buổi 25 — Selectolax + HTTPX + SQLite
Buổi 26 — Mini Project: Article Scraper Framework
```

Đây sẽ là bước chuyển rất tự nhiên từ **"học Selectolax" → "tự xây framework crawler/scraper bằng Python"**.
