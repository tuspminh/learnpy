# Buổi 32 — `<a href>` → URL

Ở **Buổi 31**, chúng ta đã học cách biến một URL tương đối thành URL tuyệt đối:

```python
page_url.join(URL(href))
```

Bây giờ đưa kiến thức đó vào đúng ngữ cảnh crawler:

```text
HTML
 ↓
<a href="...">
 ↓
extract href
 ↓
yarl.URL
 ↓
resolve relative URL
 ↓
URL tuyệt đối
```

Đây là một bước rất quan trọng trong **Novel Crawler**, vì parser thực tế sẽ gặp hàng trăm `<a href>` trên mỗi trang.

---

# 1. HTML `<a href>` không phải URL hoàn chỉnh

Ví dụ trang:

```text
https://example.com/novel/python/
```

HTML:

```html
<a href="/novel/python">Python</a>

<a href="chapter-1">Chương 1</a>

<a href="../">Trang chủ</a>

<a href="https://example.com/about">About</a>
```

Các `href` này có thể là:

```text
/novel/python
chapter-1
../
https://example.com/about
```

Chúng **chưa đồng nhất về dạng**.

Crawler cần biến tất cả thành:

```text
https://example.com/novel/python
https://example.com/novel/python/chapter-1
https://example.com/
https://example.com/about
```

Do đó:

```text
HTML href
    ↓
href string
    ↓
URL(href)
    ↓
page_url.join(...)
    ↓
absolute URL
```

---

# 2. Lấy `<a href>` bằng selectolax

Cài thư viện nếu chưa có:

```bash
pip install yarl selectolax
```

HTML:

```python
from selectolax.parser import HTMLParser


html = """
<html>
<body>

<a href="/novel/python">Python</a>
<a href="chapter-1">Chương 1</a>
<a href="../">Trang chủ</a>

</body>
</html>
"""

tree = HTMLParser(html)

for node in tree.css("a[href]"):
    print(node.attributes.get("href"))
```

Kết quả:

```text
/novel/python
chapter-1
../
```

---

# 3. `a[href]` có ý nghĩa gì?

Selector:

```css
a[href]
```

nghĩa là:

> Chọn các thẻ `<a>` có thuộc tính `href`.

Ví dụ:

```html
<a href="/novel/python">Python</a>

<a href="chapter-1">Chapter 1</a>

<a>Không có href</a>
```

Selector:

```python
tree.css("a[href]")
```

chỉ lấy 2 thẻ đầu.

Trong crawler, đây thường là selector phù hợp hơn:

```python
tree.css("a")
```

vì:

```python
a
```

có thể lấy cả những anchor không phải link thực sự.

---

# 4. Lấy `href`

Cách an toàn:

```python
href = node.attributes.get("href")
```

Không nên mặc định:

```python
href = node.attributes["href"]
```

vì có thể xảy ra:

```text
KeyError
```

nếu HTML không có thuộc tính đó.

Nhưng với:

```python
tree.css("a[href]")
```

thì thông thường `href` đã tồn tại.

Dù vậy:

```python
.get()
```

vẫn là cách xử lý an toàn và dễ mở rộng.

---

# 5. Kết hợp selectolax + yarl

Đây chính là phần quan trọng.

```python
from selectolax.parser import HTMLParser
from yarl import URL


page_url = URL("https://example.com/novel/python/")

html = """
<a href="/novel/python">Python</a>
<a href="chapter-1">Chapter 1</a>
<a href="../">Home</a>
<a href="https://example.com/about">About</a>
"""

tree = HTMLParser(html)

for node in tree.css("a[href]"):
    href = node.attributes.get("href")

    if not href:
        continue

    url = page_url.join(URL(href))

    print(url)
```

Kết quả:

```text
https://example.com/novel/python
https://example.com/novel/python/chapter-1
https://example.com/
https://example.com/about
```

Đây chính là pattern mà crawler của chúng ta sẽ sử dụng rất nhiều.

---

# 6. Tại sao không dùng string?

Một cách dễ nghĩ:

```python
url = str(page_url) + href
```

Nhưng:

```python
page_url = "https://example.com/novel/python/"
href = "../"
```

sẽ tạo:

```text
https://example.com/novel/python/../
```

Trong khi URL đúng phải là:

```text
https://example.com/
```

Hoặc:

```python
href = "chapter-1"
```

cần hiểu nó tương đối với:

```text
https://example.com/novel/python/
```

Yarl hiểu được quy tắc URL:

```python
page_url.join(URL(href))
```

Vì vậy:

> **Không nối URL bằng string.**

---

# 7. `href` có thể chứa khoảng trắng

HTML thực tế không phải lúc nào cũng sạch.

Ví dụ:

```html
<a href="  /novel/python  ">
    Python
</a>
```

Nên:

```python
href = href.strip()
```

Sau đó mới:

```python
URL(href)
```

Pattern:

```python
href = node.attributes.get("href")

if href is None:
    continue

href = href.strip()

if not href:
    continue

url = page_url.join(URL(href))
```

---

# 8. Không phải `href` nào cũng nên crawl

Đây là vấn đề rất quan trọng.

HTML có thể chứa:

```html
<a href="/novel/python">Python</a>

<a href="chapter-1">Chapter 1</a>

<a href="https://example.com/about">About</a>

<a href="javascript:void(0)">Click</a>

<a href="mailto:test@example.com">Email</a>

<a href="tel:0123456789">Call</a>

<a href="data:text/plain,hello">Data</a>
```

Crawler của chúng ta chỉ muốn:

```text
http://...
https://...
```

Không muốn:

```text
javascript:
mailto:
tel:
data:
blob:
```

---

# 9. Kiểm tra scheme

Yarl:

```python
url = URL("javascript:void(0)")

print(url.scheme)
```

Kết quả:

```text
javascript
```

URL:

```python
URL("mailto:test@example.com")
```

có:

```text
mailto
```

URL tương đối:

```python
URL("chapter-1")
```

có:

```text
""
```

Do đó có thể định nghĩa:

```python
ALLOWED_SCHEMES = {"http", "https"}
```

và:

```python
href_url = URL(href)

if href_url.scheme and href_url.scheme not in ALLOWED_SCHEMES:
    continue
```

Ý nghĩa:

```text
scheme == ""
    → relative URL → cho phép

http
https
    → cho phép

javascript
mailto
tel
data
blob
    → bỏ
```

---

# 10. Viết hàm `extract_links()`

Bây giờ chúng ta gom logic lại.

```python
from selectolax.parser import HTMLParser
from yarl import URL


ALLOWED_SCHEMES = {"http", "https"}


def extract_links(page_url: URL, html: str) -> list[URL]:
    tree = HTMLParser(html)

    result: list[URL] = []

    for node in tree.css("a[href]"):
        href = node.attributes.get("href")

        if href is None:
            continue

        href = href.strip()

        if not href:
            continue

        href_url = URL(href)

        # Reject javascript:, mailto:, tel:, ...
        if href_url.scheme and href_url.scheme not in ALLOWED_SCHEMES:
            continue

        url = page_url.join(href_url)

        # Đảm bảo kết quả cuối cùng là HTTP/HTTPS
        if url.scheme not in ALLOWED_SCHEMES:
            continue

        result.append(url)

    return result
```

---

# 11. Test hoàn chỉnh

Đây là ví dụ bạn có thể copy chạy ngay:

```python
from selectolax.parser import HTMLParser
from yarl import URL


ALLOWED_SCHEMES = {"http", "https"}


def extract_links(page_url: URL, html: str) -> list[URL]:
    tree = HTMLParser(html)

    result: list[URL] = []

    for node in tree.css("a[href]"):
        href = node.attributes.get("href")

        if href is None:
            continue

        href = href.strip()

        if not href:
            continue

        href_url = URL(href)

        if href_url.scheme and href_url.scheme not in ALLOWED_SCHEMES:
            continue

        url = page_url.join(href_url)

        if url.scheme not in ALLOWED_SCHEMES:
            continue

        result.append(url)

    return result


def main():
    page_url = URL(
        "https://truyen.example/novels/python/"
    )

    html = """
    <html>
    <body>

        <a href="/novels/python">
            Python
        </a>

        <a href="chapter-1">
            Chương 1
        </a>

        <a href="../">
            Trang chủ
        </a>

        <a href="https://truyen.example/about">
            About
        </a>

        <a href="javascript:void(0)">
            JavaScript
        </a>

        <a href="mailto:test@example.com">
            Email
        </a>

        <a href="tel:0123456789">
            Phone
        </a>

        <a href="">
            Empty
        </a>

        <a>
            No href
        </a>

        <a href="#chapter-10">
            Chapter 10
        </a>

    </body>
    </html>
    """

    links = extract_links(page_url, html)

    for url in links:
        print(url)


if __name__ == "__main__":
    main()
```

Kết quả:

```text
https://truyen.example/novels/python
https://truyen.example/novels/python/chapter-1
https://truyen.example/
https://truyen.example/about
https://truyen.example/novels/python/#chapter-10
```

---

# 12. Một điểm rất quan trọng: Fragment

Có:

```html
<a href="#chapter-10">
    Chương 10
</a>
```

Yarl resolve thành:

```text
https://truyen.example/novels/python/#chapter-10
```

Nhưng crawler HTTP thường **không cần fragment**.

Ví dụ:

```python
url = URL(
    "https://truyen.example/novels/python/#chapter-10"
)

print(url.with_fragment(None))
```

Kết quả:

```text
https://truyen.example/novels/python/
```

Tuy nhiên, **chưa nên đưa việc này vào `extract_links()`**.

Tại sao?

Vì chúng ta đang cố gắng tách:

```text
Extraction
    ↓
URL Resolution
    ↓
URL Policy
    ↓
Fetcher
```

Fragment thuộc về **URL policy/canonicalization** hơn là HTML extraction.

Chúng ta sẽ xử lý sâu hơn ở các bài:

```text
36 URL normalization
37 URL comparison
38 URL deduplication
39 Canonical URL
```

---

# 13. External URL có nên loại bỏ không?

Ví dụ:

```html
<a href="https://google.com">
    Google
</a>
```

Hàm hiện tại sẽ trả:

```text
https://google.com
```

Điều này **không có nghĩa crawler phải crawl nó**.

Đây là hai vấn đề khác nhau:

### Link extraction

```text
HTML
 ↓
https://google.com
```

### Crawl policy

```text
https://google.com
 ↓
Có được phép crawl không?
```

Ví dụ Novel Crawler chỉ crawl:

```text
https://truyen.example/*
```

thì policy có thể nói:

```python
if url.origin() != page_url.origin():
    reject
```

Nhưng **không nên nhét rule này vào extractor**.

Đây là một nguyên tắc kiến trúc quan trọng.

---

# 14. Extraction ≠ Crawl Policy

Nên phân biệt:

```text
HTML
 │
 ▼
LinkExtractor
 │
 │  lấy tất cả HTTP/HTTPS links hợp lệ
 ▼
URL
 │
 ▼
URL Policy
 │
 ├── same-origin?
 ├── allowed path?
 ├── chapter URL?
 ├── novel URL?
 └── blacklist?
 │
 ▼
Fetcher
```

Ví dụ:

```python
extract_links(...)
```

chỉ quan tâm:

> "Trong HTML có những URL nào?"

Còn:

```python
CrawlPolicy
```

quan tâm:

> "URL nào crawler được phép lấy?"

Đây là cách thiết kế rất phù hợp với DDD/SOLID mà chúng ta đang xây dựng.

---

# 15. Lấy cả text của link

Trong parser truyện, đôi khi chúng ta không chỉ cần URL mà còn cần:

```text
title
href
```

Ví dụ:

```html
<a href="/novel/python">
    Lập trình Python
</a>
```

Có thể lấy:

```python
for node in tree.css("a[href]"):
    href = node.attributes.get("href")
    text = node.text(strip=True)

    print(text)
    print(href)
```

Kết quả:

```text
Lập trình Python
/novel/python
```

Nhưng lúc này output không còn đơn giản là:

```python
list[URL]
```

mà có thể là:

```text
Link
 ├── text
 └── url
```

Đây là nơi sau này chúng ta có thể dùng Domain Model/DTO nếu cần.

---

# 16. Có nên tạo `LinkExtractor` class ngay không?

Có thể:

```python
class LinkExtractor:
    def extract(self, page_url: URL, html: str) -> list[URL]:
        ...
```

Nhưng với logic hiện tại, tôi **chưa khuyên tạo class chỉ để bọc một function**.

Function:

```python
extract_links(...)
```

đã đủ rõ.

Khi logic tăng lên:

```text
extract links
    ↓
resolve URL
    ↓
normalize
    ↓
canonicalize
    ↓
crawl policy
    ↓
deduplicate
```

lúc đó mới có lý do tách component.

Đây chính là **balanced abstraction** thay vì:

```text
HrefExtractor
URLExtractor
SchemeExtractor
FragmentExtractor
...
```

cho những logic rất nhỏ.

---

# 17. Kiến trúc sau Buổi 32

Crawler của chúng ta hiện có luồng:

```text
                HTTPX
                  │
                  │ page_source
                  ▼
             Selectolax
                  │
                  │ <a href>
                  ▼
             href string
                  │
                  ▼
              yarl.URL
                  │
                  ▼
          URL Resolution
                  │
                  ▼
          absolute URL
                  │
                  ▼
            URL Policy
                  │
                  ▼
              Fetcher
```

Trong code có thể hình dung:

```python
page_url = URL("https://example.com/novels/python/")

links = extract_links(
    page_url=page_url,
    html=page_source,
)

for url in links:
    print(url)
```

Điểm rất quan trọng:

```python
page_url
```

phải đi cùng:

```python
page_source
```

Bởi vì:

```html
<a href="chapter-1">
```

không thể tự xác định URL tuyệt đối nếu không biết trang HTML nằm ở đâu.

---

# 18. Phiên bản nên dùng trong Novel Crawler

Tại thời điểm hiện tại, tôi đề xuất giữ component đơn giản:

```python
from selectolax.parser import HTMLParser
from yarl import URL


ALLOWED_SCHEMES = {"http", "https"}


def extract_links(
    page_url: URL,
    html: str,
) -> list[URL]:

    tree = HTMLParser(html)

    links: list[URL] = []

    for node in tree.css("a[href]"):
        href = node.attributes.get("href")

        if not href:
            continue

        href = href.strip()

        if not href:
            continue

        href_url = URL(href)

        if (
            href_url.scheme
            and href_url.scheme not in ALLOWED_SCHEMES
        ):
            continue

        url = page_url.join(href_url)

        if url.scheme not in ALLOWED_SCHEMES:
            continue

        links.append(url)

    return links
```

Đây là một abstraction vừa đủ.

---

# 19. Những gì cần nhớ sau Buổi 32

### ① CSS selector

```python
tree.css("a[href]")
```

### ② Lấy href

```python
href = node.attributes.get("href")
```

### ③ Làm sạch

```python
href = href.strip()
```

### ④ Chuyển thành yarl URL

```python
href_url = URL(href)
```

### ⑤ Resolve

```python
url = page_url.join(href_url)
```

### ⑥ Kiểm tra scheme

```python
if href_url.scheme not in {"", "http", "https"}:
    continue
```

### ⑦ Output

```python
list[URL]
```

thay vì:

```python
list[str]
```

---

## Pipeline chúng ta đang xây

```text
Buổi 31
Relative URL → Absolute URL
          ↓
Buổi 32
<a href> → URL
          ↓
Buổi 33
Pagination
          ↓
Buổi 34
Chapter URL
          ↓
Buổi 35
Image URL
          ↓
Buổi 36
URL normalization
          ↓
Buổi 37
URL comparison
          ↓
Buổi 38
URL deduplication
          ↓
Buổi 39
Canonical URL
          ↓
Buổi 40
URLBuilder cho Novel Crawler
```

**Bài tập thực hành:** hãy lấy một `page_source` thật của trang listing truyện, dùng `selectolax` lấy toàn bộ `a[href]`, sau đó chuyển thành `list[URL]`. Ở **Buổi 33**, chúng ta sẽ dùng chính pipeline này để xử lý **pagination (`trang-2`, `?page=2`, `next`)** một cách chắc chắn.
