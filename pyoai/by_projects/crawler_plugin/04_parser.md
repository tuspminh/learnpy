Tuyệt vời. Từ bài này, chúng ta sẽ viết **trái tim của plugin**.

Nếu `HttpClient` là người đi lấy HTML thì **Parser là bộ não**, có nhiệm vụ hiểu HTML và chuyển nó thành các object Python.

Trong các hệ thống crawler lớn (Scrapy, Newspaper3k, Diffbot...), parser luôn là thành phần quan trọng nhất.

---

# Bài 4 - Xây dựng `parser.py`

## Mục tiêu

Sau bài này bạn sẽ xây dựng được:

```text-x-trilium-auto
HTML

↓

BeautifulSoup

↓

Parser

↓

NovelModel
ChapterModel
NovelSummaryModel
```

Đây chính là bước chuyển đổi dữ liệu.

---

# 1. Parser không nên biết HTTP

Đây là sai lầm phổ biến:

```text-x-trilium-auto
def parse(url):

    html = requests.get(url).text

    soup = BeautifulSoup(html)

    ...
```

Sai ở đâu?

Parser đang:

- tải HTML
- phân tích HTML

=> Vi phạm nguyên tắc **Single Responsibility Principle (SRP)**.

Đúng phải là:

```text-x-trilium-auto
HttpClient

↓

HTML

↓

Parser
```

Parser chỉ nhận HTML.

---

# 2. Thiết kế

```text-x-trilium-auto
HttpClient

↓

str (html)

↓

TruyenFullParser

↓

Model
```

Ví dụ:

```text-x-trilium-auto
html = client.get(url)

novel = parser.parse_novel(html)
```

Rất rõ ràng.

---

# 3. Tạo parser.py

```text-x-trilium-auto
plugins/

    truyenfull/

        parser.py
```

---

# 4. Import

```text-x-trilium-auto
from bs4 import BeautifulSoup
```

Parser chỉ cần BeautifulSoup.

---

# 5. Khởi tạo parser

```text-x-trilium-auto
class TruyenFullParser:

    def soup(self, html):

        return BeautifulSoup(
            html,
            "html.parser"
        )
```

Sau này:

```text-x-trilium-auto
soup = self.soup(html)
```

Không cần lặp lại.

---

# 6. Viết helper đầu tiên

Đây là helper được dùng rất nhiều.

```text-x-trilium-auto
def safe_text(node):

    if node is None:
        return ""

    return node.get_text(
        strip=True
    )
```

Ví dụ

HTML

```text-x-trilium-auto
<h3>

 Hello

</h3>
```

↓

```text-x-trilium-auto
Hello
```

---

Nếu

```text-x-trilium-auto
node=None
```

↓

```text-x-trilium-auto
""
```

Không bị crash.

---

# 7. Helper lấy attribute

Ví dụ

```text-x-trilium-auto
<img src="abc.jpg">
```

Ta viết

```text-x-trilium-auto
def safe_attr(node, attr):

    if node is None:
        return ""

    return node.attrs.get(attr, "")
```

Ví dụ

```text-x-trilium-auto
abc.jpg
```

---

# 8. Helper select_one

Nếu website thay đổi

```text-x-trilium-auto
h3.title

↓

h1.title
```

Ta muốn thử nhiều selector.

```text-x-trilium-auto
def select_first(
    soup,
    *selectors
):

    for selector in selectors:

        node = soup.select_one(selector)

        if node:
            return node

    return None
```

---

Ví dụ

```text-x-trilium-auto
select_first(

    soup,

    "h3.title",

    "h1.title",

    ".title"
)
```

---

# 9. Cấu trúc parser

```text-x-trilium-auto
class TruyenFullParser:

    parse_list()

    parse_novel()

    parse_chapter_list()

    parse_chapter()
```

Đây sẽ là 4 hàm chính.

---

# 10. parse_list()

Đầu tiên

```text-x-trilium-auto
def parse_list(
    self,
    html
):

    soup = self.soup(html)
```

---

Lấy danh sách

```text-x-trilium-auto
rows = soup.select(
    ListSelectors.NOVELS
)
```

Sau đó

```text-x-trilium-auto
results = []
```

---

Lặp

```text-x-trilium-auto
for row in rows:

    ...
```

Đây là cấu trúc chuẩn.

---

# 11. parse_novel()

```text-x-trilium-auto
def parse_novel(
    self,
    html
):
```

↓

```text-x-trilium-auto
soup=self.soup(html)
```

---

Lấy title

```text-x-trilium-auto
title = safe_text(

    select_first(

        soup,

        *NovelSelectors.TITLE
    )
)
```

---

Lấy cover

```text-x-trilium-auto
cover = safe_attr(

    select_first(

        soup,

        *NovelSelectors.COVER
    ),

    "src"
)
```

---

Description

```text-x-trilium-auto
description = safe_text(

    select_first(

        soup,

        *NovelSelectors.DESCRIPTION
    )
)
```

---

Sau đó

```text-x-trilium-auto
return NovelModel(...)
```

---

# 12. parse_chapter()

Tương tự

```text-x-trilium-auto
title = ...

content = ...
```

↓

```text-x-trilium-auto
return ChapterModel(...)
```

---

# 13. parse_chapter_list()

Đây là hàm được dùng nhiều nhất.

```text-x-trilium-auto
items = soup.select(

    NovelSelectors.CHAPTER_ITEMS
)
```

↓

```text-x-trilium-auto
100 item
```

---

Lặp

```text-x-trilium-auto
for item in items:
```

Lấy

```text-x-trilium-auto
chapter title

chapter url
```

↓

```text-x-trilium-auto
append
```

---

# 14. Đừng trả dict

Nhiều người viết

```text-x-trilium-auto
return {

"title":...

}
```

Sai.

Hãy trả

```text-x-trilium-auto
NovelModel(...)
```

Hoặc

```text-x-trilium-auto
ChapterModel(...)
```

Parser chỉ làm việc với model.

---

# 15. Thiết kế helper thành staticmethod

Các helper không cần trạng thái.

```text-x-trilium-auto
class TruyenFullParser:

    @staticmethod

    def safe_text(...):
```

Tương tự

```text-x-trilium-auto
safe_attr()
```

---

Ưu điểm

Không cần

```text-x-trilium-auto
self
```

---

# 16. Parser hoàn chỉnh

```text-x-trilium-auto
TruyenFullParser

    soup()

    safe_text()

    safe_attr()

    select_first()

    parse_list()

    parse_novel()

    parse_chapter_list()

    parse_chapter()
```

Đây là skeleton hoàn chỉnh.

---

# 17. Nhưng còn một vấn đề lớn...

Ví dụ HTML

```text-x-trilium-auto
<div>

<p>

Hello

</p>

<br>

<p>

World

</p>

</div>
```

Nếu dùng

```text-x-trilium-auto
get_text()
```

Ta nhận được

```text-x-trilium-auto
HelloWorld
```

Mất xuống dòng.

Hoặc có rất nhiều:

- quảng cáo
- script
- span ẩn
- comment
- khoảng trắng dư
- ký tự `&nbsp;`

Làm sao xử lý?

Đó là nhiệm vụ của **clean_html()**.

Đây là bước mà gần như mọi crawler chuyên nghiệp đều phải có.

---

# 18. Chúng ta sẽ cải tiến parser

Ở bài sau parser sẽ có thêm:

```text-x-trilium-auto
HTML

↓

BeautifulSoup

↓

clean_html()

↓

normalize()

↓

Model
```

Đây mới là parser chuyên nghiệp.

---

# Cấu trúc parser cuối cùng

```text-x-trilium-auto
TruyenFullParser
│
├── soup()
├── safe_text()
├── safe_attr()
├── select_first()
├── clean_html()
├── normalize()
├── parse_list()
├── parse_novel()
├── parse_chapter_list()
└── parse_chapter()
```

---

# Bài tập

Trước khi sang bài 5, hãy tự cài đặt và kiểm thử các hàm tiện ích sau bằng `pytest` hoặc một đoạn script nhỏ:

1. `safe_text(node)`:
  - `None` → `""`
  - `<h3> Hello </h3>` → `"Hello"`
2. `safe_attr(node, "src")`:
  - `<img src="cover.jpg">` → `"cover.jpg"`
  - Không có thuộc tính → `""`
3. `select_first(soup, *selectors)`:
  - Thử với nhiều selector, trong đó chỉ selector thứ hai tồn tại.
  - Kiểm tra khi không selector nào khớp thì trả về `None`.

---

## Một góp ý về thiết kế

Ở bài này chúng ta mới xây dựng **khung (skeleton)** của `TruyenFullParser`. Để code dễ kiểm thử và tái sử dụng hơn, mình khuyến nghị:

- Các helper chung (`safe_text`, `safe_attr`, `select_first`, `clean_html`) nên được đưa lên `BaseParser` trong thư mục `base/`.
- `TruyenFullParser` chỉ chứa logic đặc thù của TruyenFull.
- Mỗi phương thức `parse_*()` chỉ nên làm một việc: chuyển HTML thành model, không truy cập mạng, không ghi cơ sở dữ liệu, không xử lý luồng.

Đó cũng là cách các framework crawler lớn tổ chức mã nguồn.

---

## Bài 5 sẽ là bước ngoặt

Từ bài 5, chúng ta sẽ **viết parser hoàn chỉnh bằng code thật**, không còn là skeleton nữa.

Chúng ta sẽ lần lượt xây dựng:

- `BaseParser`
- `clean_html()`
- `normalize_text()`
- `parse_list()` hoàn chỉnh
- `parse_novel()` hoàn chỉnh
- `parse_chapter_list()` hoàn chỉnh
- `parse_chapter()` hoàn chỉnh

Đến hết bài 5, plugin TruyenFull của bạn sẽ **đọc được HTML thực tế và tạo ra các model Python đầy đủ**, sẵn sàng cho `Source` và `Repository` sử dụng. Đây là phần quan trọng nhất của toàn bộ hệ thống crawler.