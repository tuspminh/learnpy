# Buổi 36 — URL Normalization

Trong crawler, sau khi chúng ta đã biết cách:

```text
HTML
 ↓
selectolax
 ↓
href / src
 ↓
yarl.URL
 ↓
absolute URL
```

thì bước tiếp theo rất quan trọng là **normalization — chuẩn hóa URL**.

Mục tiêu:

> Biến những URL có cách biểu diễn khác nhau về một dạng thống nhất, **nhưng không được tự ý làm thay đổi ý nghĩa của URL**.

---

# 1. Vì sao crawler cần normalize URL?

Ví dụ crawler gặp:

```text
https://example.com/chapter-1#top
https://example.com/chapter-1#content
https://example.com/chapter-1#bottom
```

Đối với crawler HTTP, fragment:

```text
#top
#content
#bottom
```

thường không được gửi lên server.

Vì vậy cả 3 có thể dẫn tới cùng resource:

```text
https://example.com/chapter-1
```

Nếu không normalize:

```python
visited = {
    URL("https://example.com/chapter-1#top"),
    URL("https://example.com/chapter-1#content"),
    URL("https://example.com/chapter-1#bottom"),
}
```

crawler có thể coi chúng là 3 URL khác nhau.

Sau normalization:

```text
https://example.com/chapter-1
```

→ dễ deduplicate hơn.

---

# 2. Normalization là gì?

Có thể hình dung:

```text
Raw URL
   ↓
Normalization
   ↓
Normalized URL
   ↓
Comparison / Deduplication
```

Ví dụ:

```text
https://example.com/chapter-1#top
                         ↓
https://example.com/chapter-1
```

Nhưng cần nhớ:

> **Normalization không có nghĩa là "sửa URL theo mọi cách có thể".**

Ví dụ:

```text
/novel
/novel/
```

không phải lúc nào cũng tương đương.

Server có thể xử lý chúng khác nhau.

Vì vậy crawler phải **conservative**.

---

# 3. Yarl không có một hàm "normalize everything"

Đây là điểm rất quan trọng.

Không nên kỳ vọng:

```python
url.normalize()
```

rồi mọi thứ được giải quyết.

Thay vào đó, ta xây normalization dựa trên **policy của crawler**.

Ví dụ:

```python
from yarl import URL


def normalize_url(url: URL) -> URL:
    return url.with_fragment(None)
```

Đây đã là một normalization hợp lệ.

---

# 4. Normalization cơ bản: bỏ fragment

Yarl cung cấp:

```python
with_fragment(None)
```

Ví dụ:

```python
from yarl import URL


url = URL("https://example.com/chapter-1#top")

normalized = url.with_fragment(None)

print(url)
print(normalized)
```

Kết quả:

```text
https://example.com/chapter-1#top
https://example.com/chapter-1
```

URL ban đầu không bị thay đổi.

Đây là vì `URL` immutable.

---

# 5. Viết hàm normalize đầu tiên

```python
from yarl import URL


def normalize_url(url: URL) -> URL:
    return url.with_fragment(None)


url = URL("https://example.com/chapter-1#content")

result = normalize_url(url)

print("Original :", url)
print("Normalized:", result)
```

Kết quả:

```text
Original : https://example.com/chapter-1#content
Normalized: https://example.com/chapter-1
```

Đây là implementation rất tốt cho crawler giai đoạn đầu.

Không cần class.

Không cần framework.

---

# 6. Tại sao nên bỏ fragment?

Ví dụ chapter page:

```text
https://truyen.example/chapter-100#content
https://truyen.example/chapter-100#comments
https://truyen.example/chapter-100#top
```

Fragment thường dùng cho navigation trong browser:

```html
<a href="#comments">
```

Nó chỉ di chuyển vị trí hiển thị trong document.

HTTP request thường chỉ quan tâm:

```text
https://truyen.example/chapter-100
```

Vì vậy crawler thường có policy:

```python
url = url.with_fragment(None)
```

---

# 7. Nhưng không phải normalization nào cũng an toàn

Đây là phần quan trọng nhất của bài.

Giả sử:

```text
https://example.com/novel
```

và:

```text
https://example.com/novel/
```

Bạn có thể nghĩ:

> "Hai cái giống nhau."

Nhưng server có thể xử lý:

```text
/novel
```

thành:

```text
200 OK
```

trong khi:

```text
/novel/
```

lại là resource khác.

Hoặc một URL redirect sang URL kia.

Do đó **không nên mặc định làm:**

```python
url = url.with_path(url.path.rstrip("/"))
```

Đặc biệt không nên làm với mọi crawler.

---

# 8. Trailing slash

Ví dụ:

```text
https://example.com/novel
https://example.com/novel/
```

Không nên tự động biến:

```text
/novel/
```

thành:

```text
/novel
```

trừ khi website/plugin của bạn đã xác định rõ policy.

Ví dụ một site có quy tắc:

```text
/truyen/abc/
/truyen/abc/
/truyen/abc/
```

thì trailing slash là một phần convention của site.

---

# 9. Default port

Có các URL:

```text
http://example.com:80/
http://example.com/
```

và:

```text
https://example.com:443/
https://example.com/
```

Về mặt URL semantics, default port thường không tạo ra một endpoint khác.

Nhưng đây là một normalization cần **cẩn thận**.

Không nên viết một hàm kiểu:

```python
url.with_port(None)
```

cho tất cả URL.

Ví dụ:

```text
http://example.com:8080
```

thì:

```text
8080
```

rõ ràng có ý nghĩa.

Vì vậy nếu muốn loại bỏ default port, phải có policy:

```python
HTTP_DEFAULT_PORT = 80
HTTPS_DEFAULT_PORT = 443
```

và chỉ xử lý đúng trường hợp.

---

# 10. Query string — không được tự tiện sửa

Ví dụ:

```text
https://example.com/search?q=python
```

và:

```text
https://example.com/search?q=python&page=2
```

rõ ràng khác nhau.

Không thể normalization kiểu:

```python
url.with_query({})
```

vì sẽ biến thành:

```text
https://example.com/search
```

và thay đổi resource.

---

# 11. Query parameter order

Ví dụ:

```text
https://example.com/search?a=1&b=2
```

và:

```text
https://example.com/search?b=2&a=1
```

Có thể có hệ thống coi chúng tương đương.

Nhưng crawler **không nên mặc định giả định điều đó**.

Đặc biệt:

```text
?tag=python&tag=sqlite
```

và:

```text
?tag=sqlite&tag=python
```

có thể có ý nghĩa thứ tự.

Ta đã học ở các bài trước:

```python
url.query.getall("tag")
```

có thể trả:

```python
["python", "sqlite"]
```

Do đó:

> Không tự động sort query parameters nếu chưa xác định rõ semantics của website.

---

# 12. Không tự decode/encode thủ công

Sai lầm phổ biến:

```python
from urllib.parse import unquote

value = unquote(url)
```

hoặc:

```python
url = str(url).replace("%20", " ")
```

hoặc:

```python
quote(str(url))
```

Đây rất dễ tạo ra:

```text
double encoding
```

Ví dụ:

```text
%20
```

có thể vô tình biến thành:

```text
%2520
```

Yarl đã chịu trách nhiệm phần encoding URL.

Do đó:

```python
url = URL(...)
```

và sử dụng các API của `yarl`.

---

# 13. `path` và `raw_path`

Ta đã học:

```python
url.path
```

và:

```python
url.raw_path
```

Ví dụ:

```python
from yarl import URL


url = URL(
    "https://example.com/"
    "truyện-python/chương 1"
)

print("path     :", url.path)
print("raw_path :", url.raw_path)
print("str      :", str(url))
print("human    :", url.human_repr())
```

Điểm cần nhớ:

```text
path
```

là representation phù hợp để làm việc ở mức logical/path value.

Trong khi:

```text
raw_path
```

liên quan tới representation đã encoded.

Không nên lấy `raw_path` rồi tự manipulate bằng string để "normalize".

---

# 14. Dot segments

URL có thể chứa:

```text
/a/b/../c
```

hoặc:

```text
/a/./b
```

Đây là một phần của URL resolution.

Ví dụ khi xử lý URL tương đối:

```python
from yarl import URL


base = URL("https://example.com/a/b/")
href = URL("../chapter-10")

result = base.join(href)

print(result)
```

Kết quả:

```text
https://example.com/a/chapter-10
```

Điều này cho thấy một nguyên tắc:

> **Hãy để URL resolution của yarl xử lý relative URL thay vì tự normalize bằng string.**

---

# 15. Một normalize function thực tế

Ở giai đoạn đầu của Novel Crawler, tôi khuyên dùng implementation đơn giản:

```python
from yarl import URL


def normalize_url(url: URL) -> URL:
    """
    Chuẩn hóa URL cho crawler.

    Policy hiện tại:
    - loại bỏ fragment
    - không tự thay đổi path
    - không tự thay đổi query
    - không tự thay đổi port
    """
    return url.with_fragment(None)
```

Test:

```python
from yarl import URL


urls = [
    URL("https://example.com/chapter-1#top"),
    URL("https://example.com/chapter-1#content"),
    URL("https://example.com/chapter-1#comments"),
]

for url in urls:
    print(
        f"{url} -> {normalize_url(url)}"
    )
```

Kết quả:

```text
https://example.com/chapter-1#top
    -> https://example.com/chapter-1

https://example.com/chapter-1#content
    -> https://example.com/chapter-1

https://example.com/chapter-1#comments
    -> https://example.com/chapter-1
```

---

# 16. Test normalization

Ta có thể viết test đơn giản:

```python
from yarl import URL


def normalize_url(url: URL) -> URL:
    return url.with_fragment(None)


def test_normalize_fragment():
    url = URL("https://example.com/chapter-1#top")

    result = normalize_url(url)

    assert result == URL(
        "https://example.com/chapter-1"
    )


def test_normalize_without_fragment():
    url = URL("https://example.com/chapter-1")

    result = normalize_url(url)

    assert result == url


def test_original_url_is_unchanged():
    url = URL("https://example.com/chapter-1#top")

    normalize_url(url)

    assert url.fragment == "top"
```

Chạy:

```bash
pytest
```

---

# 17. Normalization trong crawler architecture

Bây giờ pipeline của chúng ta bắt đầu rõ ràng hơn:

```text
                    HTML
                     │
                     ▼
                selectolax
                     │
                  href/src
                     │
                     ▼
                  yarl.URL
                     │
                     ▼
               URL Resolver
                     │
                     ▼
              URL Normalizer
                     │
                     ▼
                URL Policy
                     │
                     ▼
                  Queue
                     │
                     ▼
                  Fetcher
```

Ví dụ:

```python
raw_href = node.attributes["href"]

url = page_url.join(URL(raw_href))

url = normalize_url(url)

queue.add(url)
```

---

# 18. Parser không nên tự normalize quá nhiều

Đây là một điểm kiến trúc quan trọng với project của bạn.

Không nên:

```text
Parser
 ├── extract href
 ├── normalize
 ├── deduplicate
 ├── check domain
 ├── check robots
 ├── queue
 └── fetch
```

Parser nên tập trung vào:

```text
HTML
 ↓
extract URL
```

Sau đó:

```text
URL
 ↓
Resolver
 ↓
Normalizer
 ↓
Policy
 ↓
Queue
```

Như vậy plugin parser vẫn đơn giản.

---

# 19. Normalization ≠ Comparison

Đây là 4 khái niệm cần phân biệt rất rõ.

### Normalization

Biến:

```text
A
```

thành representation chuẩn:

```text
normalize(A) = B
```

Ví dụ:

```text
/chapter-1#top
        ↓
/chapter-1
```

---

### Comparison

Hỏi:

```text
A có tương đương B không?
```

Ví dụ:

```python
normalize(a) == normalize(b)
```

---

### Deduplication

Có một danh sách:

```text
A
B
A
C
B
```

và muốn:

```text
A
B
C
```

---

### Canonicalization

Chọn một URL được website coi là URL chuẩn.

Ví dụ HTML:

```html
<link
    rel="canonical"
    href="https://example.com/chapter-1"
/>
```

Đây là chủ đề **Buổi 39**.

---

# 20. Một ví dụ hoàn chỉnh cho Novel Crawler

Giả sử chapter page có:

```html
<a href="/chapter-1#top">Chapter 1</a>
<a href="/chapter-1#content">Chapter 1</a>
<a href="/chapter-2">Chapter 2</a>
```

Parser:

```python
from selectolax.parser import HTMLParser
from yarl import URL


def normalize_url(url: URL) -> URL:
    return url.with_fragment(None)


def extract_chapter_urls(
    page_url: URL,
    html: str,
) -> list[URL]:

    tree = HTMLParser(html)

    result = []

    for node in tree.css("a[href]"):
        href = node.attributes.get("href")

        if not href:
            continue

        href = href.strip()

        if not href:
            continue

        raw_url = URL(href)

        if raw_url.scheme not in {"", "http", "https"}:
            continue

        absolute_url = page_url.join(raw_url)

        normalized_url = normalize_url(
            absolute_url
        )

        result.append(normalized_url)

    return result
```

Test:

```python
page_url = URL(
    "https://example.com/novel/python"
)

html = """
<html>
<body>

<a href="/chapter-1#top">
    Chapter 1
</a>

<a href="/chapter-1#content">
    Chapter 1
</a>

<a href="/chapter-2">
    Chapter 2
</a>

</body>
</html>
"""

urls = extract_chapter_urls(
    page_url,
    html,
)

for url in urls:
    print(url)
```

Kết quả:

```text
https://example.com/chapter-1
https://example.com/chapter-1
https://example.com/chapter-2
```

Chú ý:

**Normalization chưa loại duplicate.**

Ta vẫn có:

```text
chapter-1
chapter-1
```

Đó là nhiệm vụ của **Buổi 38 — URL deduplication**.

---

# 21. Có nên normalize trailing slash không?

Có thể, nhưng nên để thành policy.

Ví dụ:

```python
def normalize_trailing_slash(url: URL) -> URL:
    if url.path != "/" and url.path.endswith("/"):
        return url.with_path(url.path.rstrip("/"))

    return url
```

Nhưng tôi **không khuyên đưa nó vào normalization mặc định**.

Nếu plugin của một website xác nhận:

```text
/truyen/foo
```

và:

```text
/truyen/foo/
```

luôn tương đương, khi đó mới bật policy:

```text
strip_trailing_slash = True
```

Đây chính là tư duy tốt khi xây crawler framework:

```text
Global normalization
        +
Site-specific URL policy
```

chứ không phải:

```text
Một hàm normalize cực kỳ mạnh
```

---

# 22. Thiết kế phù hợp với project của bạn

Hiện tại tôi đề xuất:

```text
URL Resolver
      │
      ▼
URL Normalizer
      │
      ▼
URL Policy
```

### Resolver

Chịu trách nhiệm:

```text
relative → absolute
```

### Normalizer

Chịu trách nhiệm:

```text
representation → normalized representation
```

Ví dụ:

```text
remove fragment
```

### Policy

Chịu trách nhiệm:

```text
Có được crawl URL này không?
```

Ví dụ:

```text
allowed scheme
allowed domain
allowed path
external CDN
trailing slash rule
```

### Deduplicator

Chịu trách nhiệm:

```text
URL đã xuất hiện chưa?
```

---

# 23. Phiên bản đầu tiên nên thật đơn giản

Đừng xây ngay:

```text
URLNormalizationEngine
URLNormalizationStrategy
URLNormalizationFactory
URLNormalizationRegistry
```

😄

Ở hiện tại chỉ cần:

```python
def normalize_url(url: URL) -> URL:
    return url.with_fragment(None)
```

Sau này khi crawler thực sự phát sinh requirements:

```text
default port
trailing slash
tracking parameters
site-specific query
canonical URL
```

thì mới mở rộng.

---

# 24. Quy tắc vàng của Buổi 36

Hãy nhớ 6 nguyên tắc:

```text
1. Normalize trước khi deduplicate.

2. Không normalize bằng string manipulation.

3. Fragment thường có thể bỏ trong crawler URL.

4. Không tự ý bỏ trailing slash.

5. Không tự ý sort hoặc xóa query parameters.

6. Normalization phải conservative.
```

Và kiến trúc:

```text
HTML
 ↓
selectolax
 ↓
href
 ↓
yarl.URL
 ↓
Resolver
 ↓
Normalizer
 ↓
Policy
 ↓
Deduplicator
 ↓
Queue
 ↓
Fetcher
```

**Buổi 37 — URL comparison** sẽ đi ngay sau bước này: chúng ta sẽ xây cách trả lời câu hỏi **"hai `yarl.URL` có thực sự được xem là cùng một URL hay không?"**, bao gồm `==`, normalized comparison, fragment, query, trailing slash và domain/origin.
