Rất tốt.

Đây là **bài cuối cùng của Parser**.

Sau bài này, plugin TruyenFull sẽ hoàn thành tầng **Parser**, và từ bài 10 chúng ta sẽ chuyển sang **Source Layer** (điều phối toàn bộ quá trình crawl).

> Đây là bài mình sẽ dạy theo chuẩn production, không chỉ để crawl TruyenFull mà còn làm nền tảng cho các plugin khác.

---

# Bài 9 - Xây dựng `parse_chapter()`

## Mục tiêu

Sau bài này

```text-x-trilium-auto
URL Chapter

↓

HttpClient

↓

HTML

↓

parse_chapter()

↓

ChapterModel
```

Ví dụ

```text-x-trilium-auto
ChapterModel(
    source="truyenfull",
    novel_id="than-dao-dan-ton",
    slug="chuong-100",
    index=100,
    title="Chương 100: Thiên Kiêu",
    content="...."
)
```

Đây chính là dữ liệu sẽ lưu vào SQLite.

---

# 1. ChapterModel

Model này khác `ChapterSummaryModel`.

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass(slots=True)
class ChapterModel:

    source: str

    novel_id: str

    slug: str

    index: int

    title: str

    content: str

    url: str
```

Chỉ có **một thứ mới**:

```text-x-trilium-auto
content
```

Đó là nội dung chương.

---

# 2. HTML

Ví dụ

```text-x-trilium-auto
<h3 class="chapter-title">

Chương 100:
Thiên Kiêu

</h3>

<div class="chapter-c">

<p>

....

</p>

</div>
```

Parser cần lấy

```text-x-trilium-auto
title

content
```

---

# 3. Luồng parser

```text-x-trilium-auto
HTML

↓

BeautifulSoup

↓

parse_title()

↓

parse_content()

↓

extract_index()

↓

ChapterModel
```

---

# 4. parse_title()

Chính là helper đã quen.

```text-x-trilium-auto
def parse_chapter_title(
    self,
    soup
):
    node = self.select_first(
        soup,
        *ChapterSelectors.TITLE
    )

    return self.safe_text(node)
```

Không có gì mới.

---

# 5. parse_content()

Đây mới là phần khó.

Không nên

```text-x-trilium-auto
node.get_text()
```

Vì sẽ gặp

```text-x-trilium-auto
script

ads

style

comment

br

span
```

---

Ta lấy node.

```text-x-trilium-auto
node = self.select_first(
    soup,
    *ChapterSelectors.CONTENT
)
```

---

Sau đó

```text-x-trilium-auto
text = self.clean_html(
    node
)
```

Đây là lý do chúng ta đã xây dựng `clean_html()` từ bài trước.

---

# 6. clean_html()

Phiên bản ở bài 5 mới chỉ xử lý cơ bản.

Bây giờ ta nâng cấp.

Đầu tiên

```text-x-trilium-auto
for tag in node.select(
    "script,style"
):
    tag.decompose()
```

---

Tiếp theo

```text-x-trilium-auto
for tag in node.select(
    ".ads"
):
    tag.decompose()
```

Ví dụ

```text-x-trilium-auto
<div class="ads">

....

</div>
```

↓

bị xóa.

---

# 7. Xóa iframe

```text-x-trilium-auto
for tag in node.select(
    "iframe"
):
    tag.decompose()
```

---

# 8. Xóa quảng cáo

Một số website có

```text-x-trilium-auto
<div>

Mời bạn đọc tại....

</div>
```

Không có class.

Lúc này phải dùng text filter.

Ví dụ

```text-x-trilium-auto
for text in node.find_all(string=True):

    if "truyenfull.vn" in text.lower():

        text.extract()
```

Đây gọi là **content filter**.

---

# 9. Thay `<br>`

```text-x-trilium-auto
for br in node.find_all("br"):

    br.replace_with("\n")
```

Đây là bước cực kỳ quan trọng.

---

# 10. Paragraph

Ví dụ

```text-x-trilium-auto
<p>

Hello

</p>

<p>

World

</p>
```

Ta muốn

```text-x-trilium-auto
Hello

World
```

Không phải

```text-x-trilium-auto
HelloWorld
```

Do đó

```text-x-trilium-auto
text = node.get_text(
    separator="\n"
)
```

---

# 11. Chuẩn hóa

Không dùng

```text-x-trilium-auto
normalize_space()
```

Mà

```text-x-trilium-auto
normalize_content()
```

Ví dụ

```text-x-trilium-auto
Hello



World
```

↓

```text-x-trilium-auto
Hello

World
```

---

# 12. extract_index()

Đã có ở bài trước.

```text-x-trilium-auto
index = self.extract_index(
    title
)
```

↓

```text-x-trilium-auto
100
```

---

# 13. slug

Không nên

```text-x-trilium-auto
split("/")
```

Mà

```text-x-trilium-auto
slug = extract_slug(
    url
)
```

↓

```text-x-trilium-auto
chuong-100
```

---

# 14. parse_chapter()

Lúc này rất đẹp.

```text-x-trilium-auto
def parse_chapter(
    self,
    html,
    novel_id,
    url
):
```

↓

```text-x-trilium-auto
soup = self.soup(html)
```

↓

```text-x-trilium-auto
title = self.parse_chapter_title(
    soup
)
```

↓

```text-x-trilium-auto
content = self.parse_content(
    soup
)
```

↓

```text-x-trilium-auto
index = self.extract_index(
    title
)
```

↓

```text-x-trilium-auto
slug = extract_slug(
    url
)
```

↓

```text-x-trilium-auto
return ChapterModel(...)
```

---

# 15. Kiểm tra nội dung rỗng

Nếu

```text-x-trilium-auto
content=""
```

Không nên lưu.

Ta nên

```text-x-trilium-auto
if not content:

    raise ParseError(
        "Empty chapter"
    )
```

Đây là lỗi parser.

Không phải lỗi HTTP.

---

# 16. Logger

Ví dụ

```text-x-trilium-auto
except Exception:

    ...
```

Nên log

```text-x-trilium-auto
chapter parse failed

url=...

reason=...
```

Để dashboard sau này hiển thị.

---

# 17. Parser hoàn chỉnh

```text-x-trilium-auto
TruyenFullParser

│

├── parse_list()

├── parse_list_item()

│

├── parse_novel()

├── parse_title()

├── parse_author()

├── parse_cover()

├── parse_status()

├── parse_categories()

│

├── parse_chapter_list()

├── parse_chapter_item()

│

├── parse_chapter()

├── parse_chapter_title()

├── parse_content()

│

├── clean_html()

├── normalize_content()

│

├── extract_slug()

└── extract_index()
```

Đây là parser khá hoàn chỉnh.

---

# Nhưng vẫn còn một điểm cần cải thiện

Hiện tại `clean_html()` đang làm hai việc:

```text-x-trilium-auto
HTML

↓

xóa tag

↓

lấy text

↓

chuẩn hóa
```

Theo nguyên tắc **Single Responsibility Principle**, nên tách thành:

```text-x-trilium-auto
sanitize_html(node)
        │
        ▼
extract_text(node)
        │
        ▼
normalize_content(text)
```

Như vậy:

- `sanitize_html()` chỉ sửa cây HTML.
- `extract_text()` chỉ chuyển HTML thành chuỗi.
- `normalize_content()` chỉ chuẩn hóa văn bản.

Điều này giúp việc kiểm thử và tái sử dụng dễ hơn, đặc biệt khi sau này bạn crawl các website có cấu trúc khác.

---

# Kiểm thử

Một file HTML mẫu:

```text-x-trilium-auto
<div class="chapter-c"> <p>Dòng 1</p> <p>Dòng 2</p> <script>alert("x")</script> </div>
```

Kết quả mong muốn:

```text-x-trilium-auto
chapter = parser.parse_chapter(html, "than-dao-dan-ton", url)

assert chapter.title == "Chương 1"

assert chapter.content == "Dòng 1\n\nDòng 2"
```

Ngoài ra, hãy bổ sung các trường hợp:

- Có `<br>`.
- Có `iframe`.
- Có comment HTML.
- Có đoạn quảng cáo cần loại bỏ.

---

# Kết thúc giai đoạn Parser

Đến đây, **Parser Layer đã hoàn chỉnh**.

Chúng ta đã xây dựng được:

```text-x-trilium-auto
BaseParser
        │
        ▼
TruyenFullParser
        │
        ├── parse_list()
        ├── parse_novel()
        ├── parse_chapter_list()
        └── parse_chapter()
```

Đây là phần khó nhất của plugin.

---

# Giai đoạn tiếp theo: Source Layer

Từ **Bài 10**, chúng ta sẽ xây dựng `TruyenFullSource`.

Đây là lớp **điều phối (orchestrator)** của plugin.

Nó sẽ kết nối:

```text-x-trilium-auto
HttpClient
      │
      ▼
TruyenFullParser
      │
      ▼
Repository
```

và triển khai các API cấp cao như:

```text-x-trilium-auto
fetch_novel_list()
fetch_novel()
fetch_chapters()
fetch_chapter()
sync_novel()
```

Đây là bước biến parser thành một **plugin hoàn chỉnh** có thể được Dashboard hoặc Scheduler gọi trực tiếp để crawl dữ liệu.