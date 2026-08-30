# 📘 Selectolax — Buổi 11: Performance

Hôm nay chúng ta chuyển từ:

```text
"Biết dùng Selectolax"
```

sang:

```text
"Biết dùng Selectolax để scrape hàng nghìn trang"
```

Mục tiêu:

* Vì sao Selectolax nhanh?
* Parse nhiều HTML hiệu quả
* Tách **network time** khỏi **parsing time**
* Benchmark Selectolax với BeautifulSoup
* Tránh những bottleneck thường gặp
* Thiết kế scraper có performance tốt

---

# 1. Trước hết: Selectolax không làm HTTP nhanh hơn

Một scraper thường có pipeline:

```text
URL
 ↓
HTTP request
 ↓
Download HTML
 ↓
Parse HTML
 ↓
CSS Selector
 ↓
Extract data
 ↓
Save database
```

Ví dụ một request:

```text
HTTP       450 ms
Parse       2 ms
Selector    1 ms
Extract     1 ms
SQLite      3 ms
----------------
Total      457 ms
```

Trong trường hợp này:

> Tối ưu Selectolax từ 2 ms xuống 1 ms gần như không đáng kể.

Đây là nguyên tắc đầu tiên của performance:

> **Đo bottleneck trước khi tối ưu.**

---

# 2. Ba loại bottleneck

Scraper thường bị giới hạn bởi:

```text
Network
   ↓
HTTP request / server response

CPU
   ↓
HTML parsing / extraction

I/O
   ↓
Database / file / disk
```

Ví dụ:

```text
HTTP       ████████████████████  90%
Parsing    █                     4%
Database   ██                    6%
```

Lúc này tối ưu Selectolax không giúp nhiều.

Ngược lại:

```text
HTTP       ███████               35%
Parsing    ████████              40%
Database   █████                 25%
```

thì parser performance bắt đầu quan trọng.

---

# 3. Vì sao Selectolax nhanh?

Selectolax được thiết kế để parse HTML rất nhanh và có backend native.

Ý tưởng tổng quát:

```text
Python code
     ↓
Selectolax API
     ↓
native HTML parser
     ↓
DOM
```

Trong khi một parser thuần Python thường phải thực hiện nhiều công việc ở tầng Python.

Điểm quan trọng không phải:

> "Selectolax nhanh vì CSS selector."

Mà chủ yếu:

> **HTML parsing được thực hiện rất hiệu quả ở tầng native.**

---

# 4. Nhưng đừng hiểu sai

Selectolax nhanh không có nghĩa:

```text
Selectolax
>
mọi parser
>
mọi trường hợp
```

Performance phụ thuộc:

```text
HTML size
+
parser backend
+
selector complexity
+
number of nodes
+
number of pages
+
Python processing
```

Vì vậy phải benchmark workload thực tế.

---

# 5. Benchmark đơn giản

Cài:

```bash
pip install selectolax beautifulsoup4
```

Tạo HTML:

```python
HTML = """
<html>
<body>

<article class="post">

<h1>Python Selectolax</h1>

<div class="content">
    <p>Hello</p>
    <p>World</p>
    <p>Python</p>
</div>

</article>

</body>
</html>
"""
```

---

# 6. Benchmark Selectolax

```python
from timeit import timeit
from selectolax.parser import HTMLParser


def parse_selectolax():
    tree = HTMLParser(HTML)

    title = tree.css_first("h1")

    return title.text(strip=True)
```

Benchmark:

```python
elapsed = timeit(
    parse_selectolax,
    number=10_000,
)

print(elapsed)
```

---

# 7. Benchmark BeautifulSoup

```python
from bs4 import BeautifulSoup


def parse_bs4():
    soup = BeautifulSoup(
        HTML,
        "html.parser",
    )

    title = soup.select_one("h1")

    return title.get_text(
        strip=True
    )
```

Benchmark:

```python
elapsed = timeit(
    parse_bs4,
    number=10_000,
)

print(elapsed)
```

---

# 8. So sánh

Có thể:

```text
Selectolax      0.xxx s
BeautifulSoup   x.xxx s
```

Nhưng **đừng ghi nhớ một con số cố định**.

Kết quả phụ thuộc:

* CPU
* Python version
* HTML size
* parser backend
* selector
* phiên bản thư viện

Điều bạn cần nhớ là **cách benchmark**, không phải một con số trên máy người khác.

---

# 9. Benchmark đúng cách

Không nên:

```python
start = time.perf_counter()

# request
# parse
# database
# print

end = time.perf_counter()
```

rồi kết luận:

> Selectolax chậm.

Bạn cần đo riêng:

```text
HTTP
 ↓
Parse
 ↓
Extract
 ↓
Database
```

---

# 10. Đo parse time

```python
import time
from selectolax.parser import HTMLParser


start = time.perf_counter()

tree = HTMLParser(html)

elapsed = time.perf_counter() - start

print(
    f"Parse: {elapsed:.6f}s"
)
```

---

# 11. Đo selector time

```python
start = time.perf_counter()

nodes = tree.css(
    ".article-content p"
)

elapsed = time.perf_counter() - start

print(
    f"Selector: {elapsed:.6f}s"
)
```

---

# 12. Đo extraction time

```python
start = time.perf_counter()

texts = [
    node.text(strip=True)
    for node in nodes
]

elapsed = time.perf_counter() - start

print(
    f"Extraction: {elapsed:.6f}s"
)
```

Bây giờ bạn có:

```text
Parse
Selector
Extraction
```

---

# 13. Network phải đo riêng

Với HTTPX:

```python
import httpx
import time


start = time.perf_counter()

response = httpx.get(url)

network_time = (
    time.perf_counter() - start
)
```

Sau đó:

```python
start = time.perf_counter()

tree = HTMLParser(response.text)

parse_time = (
    time.perf_counter() - start
)
```

Bạn sẽ thấy:

```text
Network:    0.400s
Parse:      0.001s
```

---

# 14. Đây là lý do HTTPX + Selectolax rất hợp nhau

Pipeline:

```text
HTTPX
  │
  │ download
  ▼
HTML string
  │
  ▼
Selectolax
  │
  │ parse
  ▼
DOM
```

Mỗi thư viện có nhiệm vụ rõ:

```text
HTTPX
→ Network

Selectolax
→ HTML parsing

Your code
→ Extraction
```

---

# 15. Parse hàng nghìn trang

Giả sử:

```text
10,000 pages
```

Mỗi HTML:

```text
200 KB
```

Tổng:

```text
2 GB HTML
```

Đây đã là workload đáng quan tâm.

Nếu parser mất:

```text
5 ms/page
```

thì:

```text
10,000 × 5 ms
= 50 seconds
```

Nếu:

```text
50 ms/page
```

thì:

```text
500 seconds
≈ 8.3 phút
```

---

# 16. Parse sequential

Cách đơn giản:

```python
for html in pages:

    tree = HTMLParser(html)

    title = tree.css_first("h1")

    ...
```

Ưu điểm:

* đơn giản
* dễ debug
* ít memory
* dễ kiểm soát

Nhược điểm:

* tổng thời gian tăng tuyến tính.

---

# 17. Network và CPU là hai chuyện khác nhau

Đây là điểm cực kỳ quan trọng.

Nếu scraper:

```text
HTTP request
 ↓
wait 500 ms
 ↓
parse 3 ms
```

thì concurrency giúp rất nhiều.

Nhưng nếu:

```text
HTTP
 ↓
parse 300 ms
 ↓
heavy extraction
```

thì vấn đề đã chuyển sang CPU.

---

# 18. Async không làm Selectolax parse nhanh hơn

Ví dụ:

```python
async def scrape(url):
    response = await client.get(url)

    tree = HTMLParser(
        response.text
    )
```

`await` giúp:

```text
HTTP I/O
```

nhưng không tự động biến:

```text
HTML parsing
```

thành async.

Đây là hai vấn đề khác nhau.

---

# 19. Pipeline thực tế

Ví dụ 1000 URL:

```text
                 ┌── HTTP ──┐
URL 1 ──────────►│          │
URL 2 ──────────►│ HTTPX    │
URL 3 ──────────►│          │
...              └────┬─────┘
                      │
                      ▼
                HTML strings
                      │
                      ▼
                 Selectolax
                      │
                      ▼
                  Extract
                      │
                      ▼
                   SQLite
```

Ở đây:

```text
HTTPX
```

có thể concurrent.

Parser:

```text
Selectolax
```

chạy theo workload CPU.

---

# 20. Không parse HTML nhiều lần

Sai:

```python
title = HTMLParser(html).css_first("h1")

content = HTMLParser(html).css_first(
    ".content"
)

author = HTMLParser(html).css_first(
    ".author"
)
```

Bạn parse 3 lần.

Nên:

```python
tree = HTMLParser(html)

title = tree.css_first("h1")

content = tree.css_first(".content")

author = tree.css_first(".author")
```

Pipeline:

```text
HTML
 ↓
Parse ONE time
 ↓
Reuse DOM
```

---

# 21. Đây là optimization rất quan trọng

Giả sử:

```text
10,000 pages
```

Bạn vô tình parse mỗi trang:

```text
3 times
```

thì:

```text
30,000 parse operations
```

Trong khi:

```python
tree = HTMLParser(html)
```

mỗi page chỉ cần một lần.

---

# 22. Không dùng selector toàn document nếu không cần

Ví dụ:

```python
tree.css(
    ".article-content p"
)
```

Nếu trang cực lớn, tốt hơn:

```python
article = tree.css_first(
    "article"
)

content = article.css_first(
    ".article-content"
)
```

Sau đó:

```python
paragraphs = content.css("p")
```

Tư duy:

```text
Document
 ↓
Root
 ↓
Subtree
 ↓
Nodes
```

---

# 23. Scoped parsing

Ví dụ:

```python
article = tree.css_first(
    "article"
)

if article is None:
    return

content = article.css_first(
    ".content"
)
```

Không chỉ giúp correctness.

Nó còn giúp code:

* rõ hơn
* dễ maintain hơn
* tránh query toàn document không cần thiết.

Performance improvement thực tế phụ thuộc DOM và selector; đừng giả định mọi scoped selector luôn nhanh hơn nếu chưa benchmark.

---

# 24. Đừng extract mọi thứ

Sai:

```python
for node in tree.iter():
    print(node.text())
```

Một trang có:

```text
50,000 nodes
```

Bạn đang xử lý tất cả.

Nếu chỉ cần:

```text
title
author
content
```

thì:

```python
title = tree.css_first(
    "h1"
)

author = tree.css_first(
    ".author"
)

content = tree.css_first(
    ".content"
)
```

---

# 25. `text()` có thể là bottleneck

Ví dụ:

```python
text = node.text()
```

Nếu content rất lớn:

```text
500 KB
1 MB
5 MB
```

thì việc chuyển cả DOM subtree thành string cũng tốn CPU/memory.

Không nên:

```python
whole_page_text = tree.body.text()
```

nếu chỉ cần article.

Nên:

```python
content = tree.css_first(
    ".article-content"
)

text = content.text(
    separator="\n",
    strip=True,
)
```

---

# 26. HTML và text là hai representation khác nhau

Ví dụ:

```python
html = content.html
```

và:

```python
text = content.text()
```

Nếu bạn chỉ cần lưu HTML:

```text
không cần convert toàn bộ sang text
```

Nếu cần text:

```text
chỉ convert subtree cần thiết
```

---

# 27. Memory

Giả sử:

```text
10,000 HTML pages
```

mỗi page:

```text
500 KB
```

Nếu giữ tất cả:

```text
≈ 5 GB raw HTML
```

Chưa tính DOM.

Sai:

```python
pages = []

for response in responses:
    pages.append(
        HTMLParser(response.text)
    )
```

Bạn đang giữ hàng nghìn DOM trees.

---

# 28. Stream pipeline tốt hơn

Nên:

```text
download
   ↓
parse
   ↓
extract
   ↓
save
   ↓
discard DOM
```

Ví dụ:

```python
for url in urls:

    response = client.get(url)

    tree = HTMLParser(
        response.text
    )

    article = extract(tree)

    save(article)

    del tree
```

Thông thường Python sẽ tự quản lý lifetime object; không nhất thiết phải `del`, nhưng điều quan trọng là **không giữ references không cần thiết**.

---

# 29. Đừng lưu DOM vào model

Sai:

```python
@dataclass
class Article:
    title: str
    content: str
    dom: object
```

Nếu scrape hàng nghìn trang:

```text
Article
 └── DOM
     └── thousands of nodes
```

Memory sẽ tăng mạnh.

Model nên giữ:

```python
@dataclass
class Article:
    title: str
    content: str
    author: str | None
```

---

# 30. Selector performance

Không phải selector nào cũng có cùng cost.

Ví dụ đơn giản:

```css
h1
```

hoặc:

```css
.article-title
```

thường dễ xử lý.

Selector phức tạp:

```css
article > div.wrapper > div.content > p:nth-child(2)
```

có thể khó maintain hơn và cần benchmark nếu nó nằm trong hot path.

Nhưng:

> Đừng tối ưu selector chỉ vì nó "trông phức tạp".

Hãy đo.

---

# 31. Microbenchmark

Dùng:

```python
from timeit import timeit
```

Ví dụ:

```python
time = timeit(
    lambda: tree.css(
        ".article-content p"
    ),
    number=10_000,
)

print(time)
```

So sánh:

```python
time1 = timeit(
    lambda: tree.css(
        ".article-content p"
    ),
    number=10_000,
)

time2 = timeit(
    lambda: tree.css(
        "article p"
    ),
    number=10_000,
)

print(time1)
print(time2)
```

---

# 32. Nhưng microbenchmark có bẫy

Ví dụ:

```python
tree = HTMLParser(html)
```

được tạo **ngoài benchmark**.

Nếu bạn muốn benchmark parsing:

```python
timeit(
    lambda: HTMLParser(html),
    number=1000,
)
```

Nếu muốn benchmark selector:

```python
tree = HTMLParser(html)

timeit(
    lambda: tree.css(".content"),
    number=10000,
)
```

Không trộn hai benchmark.

---

# 33. Benchmark parser

```python
def parse():
    HTMLParser(html)


elapsed = timeit(
    parse,
    number=1000,
)

print(
    f"{elapsed:.4f}s"
)
```

---

# 34. Benchmark extraction

```python
tree = HTMLParser(html)


def extract():
    node = tree.css_first(
        ".article-title"
    )

    if node:
        return node.text(
            strip=True
        )

    return None
```

Sau đó:

```python
elapsed = timeit(
    extract,
    number=10_000,
)
```

---

# 35. Benchmark thực tế hơn

Tạo một workload:

```python
def scrape_html(html):

    tree = HTMLParser(html)

    title = tree.css_first(
        "h1"
    )

    content = tree.css_first(
        ".content"
    )

    author = tree.css_first(
        ".author"
    )

    return {
        "title": (
            title.text(strip=True)
            if title
            else None
        ),
        "content": (
            content.text(strip=True)
            if content
            else None
        ),
        "author": (
            author.text(strip=True)
            if author
            else None
        ),
    }
```

Benchmark toàn bộ parsing + extraction:

```python
elapsed = timeit(
    lambda: scrape_html(HTML),
    number=10_000,
)
```

Đây là benchmark gần với workload thật hơn.

---

# 36. BeautifulSoup benchmark công bằng

Nếu so:

```text
Selectolax
vs
BeautifulSoup
```

hãy dùng cùng:

```text
HTML
↓
parse
↓
find title
↓
find content
↓
extract text
```

Không nên:

```text
Selectolax
→ chỉ parse

BeautifulSoup
→ parse + extract + serialize
```

Đó là benchmark không công bằng.

---

# 37. BeautifulSoup có nhiều parser backend

Điểm này rất quan trọng.

BeautifulSoup có thể dùng:

```python
BeautifulSoup(
    html,
    "html.parser",
)
```

hoặc backend khác.

Vì vậy:

```text
BeautifulSoup
```

không phải lúc nào cũng đồng nghĩa với một tốc độ cố định.

Benchmark phải ghi rõ:

```text
Python version
BeautifulSoup version
parser backend
Selectolax version
machine
HTML workload
```

---

# 38. Benchmark bằng `pytest-benchmark`

Nếu project lớn, có thể dùng plugin:

```bash
pip install pytest-benchmark
```

Ví dụ:

```python
def test_selectolax_benchmark(
    benchmark,
):

    result = benchmark(
        parse_selectolax
    )

    assert result == "Python"
```

Bạn có thể theo dõi performance qua nhiều lần refactor.

---

# 39. Performance regression

Ví dụ hôm nay:

```text
1000 pages
→ 8 seconds
```

Sau refactor:

```text
1000 pages
→ 15 seconds
```

Bạn vừa tạo:

```text
Performance regression
```

Benchmark có thể giúp phát hiện điều này.

Đây là lý do testing performance có giá trị trong scraper lớn.

---

# 40. Đừng tối ưu sai tầng

Một scraper:

```text
HTTP        10 sec
Parsing      0.2 sec
DB           1 sec
```

Bạn tối ưu Selectolax:

```text
0.2 sec → 0.15 sec
```

Total:

```text
11.2 sec
→
11.15 sec
```

Gần như không có ý nghĩa.

Nhưng nếu tối ưu HTTP concurrency:

```text
10 sec
→
2 sec
```

thì khác hoàn toàn.

---

# 41. Amdahl's Law

Một nguyên tắc rất hữu ích:

Nếu một phần chương trình chiếm:

```text
90%
```

thời gian.

Bạn làm nó nhanh gấp đôi:

```text
90% → 45%
```

Tổng chương trình chỉ giảm từ:

```text
100%
→
55%
```

Không phải:

```text
100%
→
50%
```

Vì 10% còn lại vẫn tồn tại.

Trong scraper:

```text
Network = 90%
Parser  = 10%
```

Parser nhanh gấp đôi:

```text
90 + 5 = 95
```

Không đáng bằng giảm network.

---

# 42. Architecture tốt cho performance

Một scraper production có thể:

```text
                 URLs
                   │
                   ▼
              HTTPX Client
                   │
          concurrent requests
                   │
                   ▼
                HTML
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

Mỗi tầng có bottleneck riêng.

---

# 43. Connection pooling

Vì chúng ta sẽ học HTTPX + Selectolax, hãy nhớ:

Không nên:

```python
for url in urls:
    response = httpx.get(url)
```

Tốt hơn:

```python
with httpx.Client() as client:

    for url in urls:
        response = client.get(url)
```

Client có connection pooling và giúp giảm overhead kết nối lặp lại.

---

# 44. Parsing function nên stateless

Tốt:

```python
def parse_article(
    html: str,
) -> Article:

    tree = HTMLParser(html)

    ...
```

Không nên giữ:

```python
class Parser:

    def __init__(self):
        self.trees = []
```

nếu không cần.

Stateless parser:

```text
HTML
 ↓
parse
 ↓
result
 ↓
DOM có thể giải phóng
```

Dễ scale hơn.

---

# 45. Một parser tốt

```python
from dataclasses import dataclass
from selectolax.parser import HTMLParser


@dataclass
class Article:
    title: str | None
    content: str | None


def parse_article(
    html: str,
) -> Article:

    tree = HTMLParser(html)

    title_node = tree.css_first(
        "h1"
    )

    content_node = tree.css_first(
        ".content"
    )

    return Article(
        title=(
            title_node.text(
                strip=True
            )
            if title_node
            else None
        ),
        content=(
            content_node.text(
                strip=True
            )
            if content_node
            else None
        ),
    )
```

Đây là:

```text
input
 ↓
parse
 ↓
extract
 ↓
model
```

Không giữ DOM.

---

# 46. Checklist Performance

Khi scraper chậm, kiểm tra theo thứ tự:

### 1.

```text
HTTP có chậm không?
```

### 2.

```text
Database có chậm không?
```

### 3.

```text
Parse có chậm không?
```

### 4.

```text
Extraction có chậm không?
```

### 5.

```text
Có parse HTML nhiều lần không?
```

### 6.

```text
Có giữ quá nhiều DOM trong memory không?
```

### 7.

```text
Có xử lý node không cần thiết không?
```

### 8.

```text
Có benchmark trước/sau refactor không?
```

---

# 47. Một nguyên tắc tôi muốn bạn nhớ

> **Không tối ưu theo cảm giác.**

Sai:

> "Selector này dài, chắc chậm."

Sai:

> "BeautifulSoup chậm."

Sai:

> "Async chắc chắn nhanh hơn."

Đúng:

```text
Measure
   ↓
Profile
   ↓
Identify bottleneck
   ↓
Optimize
   ↓
Benchmark again
```

---

# 48. Bài tập thực hành chính

Hãy tạo file:

```text
benchmark_parser.py
```

Với cùng một HTML lớn.

Viết hai function:

```python
def parse_selectolax(html):
    ...


def parse_bs4(html):
    ...
```

Cả hai phải trả:

```python
{
    "title": ...,
    "author": ...,
    "content": ...,
}
```

Sau đó benchmark:

```python
from timeit import timeit


selectolax_time = timeit(
    lambda: parse_selectolax(html),
    number=1000,
)

bs4_time = timeit(
    lambda: parse_bs4(html),
    number=1000,
)

print(
    "Selectolax:",
    selectolax_time,
)

print(
    "BeautifulSoup:",
    bs4_time,
)
```

Cuối cùng tính:

```python
speedup = (
    bs4_time /
    selectolax_time
)

print(
    f"Speedup: {speedup:.2f}x"
)
```

**Đừng quan tâm nếu kết quả máy bạn khác máy tôi.** Quan trọng là bạn hiểu benchmark đang đo cái gì.

---

# 49. Bài tập nâng cao — 10.000 articles

Tạo HTML giả lập:

```python
HTML = """
<article class="article">
    <h1>Title</h1>

    <div class="author">
        Author
    </div>

    <div class="content">
        <p>Paragraph 1</p>
        <p>Paragraph 2</p>
        <p>Paragraph 3</p>
    </div>
</article>
"""
```

Tạo:

```python
pages = [
    HTML
    for _ in range(10_000)
]
```

Đo:

```text
1. Tổng thời gian parse
2. Tổng thời gian extraction
3. Memory
4. Selectolax vs BeautifulSoup
```

Sau đó thử:

```text
A. parse mỗi page 1 lần
B. parse mỗi page 3 lần
```

So sánh.

Bạn sẽ thấy rất rõ tại sao:

```python
tree = HTMLParser(html)
```

nên được tạo **một lần cho mỗi document**.

---

# 50. Bài tập kiến trúc

Cuối cùng hãy xây:

```text
scraper/
│
├── parser.py
├── extractor.py
├── model.py
└── benchmark.py
```

### `parser.py`

```python
def parse(html: str):
    ...
```

### `extractor.py`

```python
def extract_article(tree):
    ...
```

### `model.py`

```python
@dataclass
class Article:
    ...
```

### `benchmark.py`

```text
Selectolax benchmark
BeautifulSoup benchmark
```

Đây chính là bước chuyển từ:

```text
học thư viện
```

sang:

```text
thiết kế scraper
```

---

# 🧠 Tổng kết Buổi 11

Bạn cần nắm 6 ý chính:

```text
1. Selectolax nhanh chủ yếu nhờ parsing native hiệu quả.

2. Network thường lớn hơn parsing rất nhiều.

3. Parse mỗi HTML một lần rồi reuse DOM.

4. Không giữ hàng nghìn DOM trong memory nếu không cần.

5. Scoped extraction giúp code rõ ràng và có thể giảm work không cần thiết.

6. Performance phải đo bằng benchmark/profile, không đoán.
```

Pipeline production nên hướng tới:

```text
                URL
                 │
                 ▼
          HTTPX Client
                 │
          connection pool
                 │
                 ▼
               HTML
                 │
                 ▼
           Selectolax
          parse 1 lần
                 │
                 ▼
           Article Root
                 │
                 ▼
             Extract
                 │
                 ▼
              Model
                 │
                 ▼
             Database
```

## 🔜 Buổi 12 — Error Handling

Chúng ta sẽ xử lý những thứ **chắc chắn xảy ra trong scraper thực tế**:

```text
HTML
 │
 ├── selector không tồn tại
 ├── HTML lỗi
 ├── response rỗng
 ├── encoding sai
 ├── attribute thiếu
 ├── content thiếu
 └── website thay đổi DOM
          ↓
     Defensive Extraction
```

Đặc biệt chúng ta sẽ xây một `SafeExtractor` để thay vì scraper chết ở:

```python
node.attributes["href"]
```

nó xử lý an toàn:

```python
node.attributes.get("href")
```

và tạo chiến lược fallback khi website thay đổi HTML.
