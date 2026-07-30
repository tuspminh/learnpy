Tuyệt vời.

Đây là **bài quan trọng nhất của toàn bộ plugin TruyenFull**.

Thực tế, trong các website truyện:

- `parse_list()` chỉ crawl vài chục truyện.
- `parse_novel()` chỉ chạy một lần cho mỗi truyện.
- `**parse_chapter_list()**` **sẽ chạy hàng triệu lần** trong suốt vòng đời của hệ thống.

Nếu thiết kế sai ở đây, sau này sẽ rất khó sửa.

---

# Bài 8 - Xây dựng `parse_chapter_list()`

## Mục tiêu

Sau bài này, chúng ta sẽ có luồng:

```text-x-trilium-auto
Novel URL
        │
        ▼
HttpClient
        │
        ▼
HTML
        │
        ▼
parse_chapter_list()
        │
        ▼
List[ChapterSummaryModel]
```

Ví dụ:

```text-x-trilium-auto
[
    ChapterSummaryModel(
        index=1,
        title="Chương 1: Trọng sinh",
        slug="chuong-1",
        url="https://..."
    ),
    ChapterSummaryModel(
        index=2,
        title="Chương 2: Bắt đầu",
        slug="chuong-2",
        url="https://..."
    )
]
```

---

# 1. Thiết kế Model

Đầu tiên tạo model.

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass(slots=True)
class ChapterSummaryModel:
    source: str

    novel_id: str

    index: int

    slug: str

    title: str

    url: str
```

Đây **không phải ChapterModel**.

Nó chỉ chứa metadata.

Vì lúc này ta chưa tải nội dung chương.

---

# 2. Vì sao phải có hai Model?

Nhiều người mới chỉ tạo:

```text-x-trilium-auto
ChapterModel
```

Sai.

Nên tách thành

```text-x-trilium-auto
ChapterSummaryModel

↓

ChapterModel
```

Giống như:

```text-x-trilium-auto
Danh bạ điện thoại

↓

Thông tin chi tiết
```

---

# 3. HTML

Ví dụ

```text-x-trilium-auto
<ul class="list-chapter">

<li>

<a href="/than-dao-dan-ton/chuong-1/">

Chương 1

</a>

</li>

<li>

<a href="/than-dao-dan-ton/chuong-2/">

Chương 2

</a>

</li>

</ul>
```

---

# 4. Luồng parser

```text-x-trilium-auto
HTML

↓

find chapter list

↓

for each li

↓

parse chapter

↓

append
```

---

# 5. parse_chapter_list()

Skeleton

```text-x-trilium-auto
def parse_chapter_list(
    self,
    html,
    novel_id
):
```

↓

```text-x-trilium-auto
soup = self.soup(html)
```

↓

```text-x-trilium-auto
items = self.select_all(
    soup,
    *NovelSelectors.CHAPTER_ITEMS
)
```

↓

```text-x-trilium-auto
results = []
```

↓

```text-x-trilium-auto
for item in items:

    ...
```

---

# 6. parse_chapter_item()

Đừng viết mọi thứ trong một hàm.

Hãy tách.

```text-x-trilium-auto
chapter = self.parse_chapter_item(
    item,
    novel_id
)
```

Nếu

```text-x-trilium-auto
chapter
```

khác None

↓

append.

---

# 7. parse_chapter_item()

Đầu tiên

```text-x-trilium-auto
link = self.select_first(
    item,
    *NovelSelectors.CHAPTER_LINK
)
```

---

Tiêu đề

```text-x-trilium-auto
title = self.safe_text(link)
```

Ví dụ

```text-x-trilium-auto
Chương 15:
Thần Bí
```

---

URL

```text-x-trilium-auto
url = self.safe_attr(
    link,
    "href"
)
```

↓

```text-x-trilium-auto
url = TruyenFullUrls.full_url(
    url
)
```

---

# 8. Slug

Không dùng

```text-x-trilium-auto
split("/")
```

Mà dùng helper.

```text-x-trilium-auto
slug = extract_slug(url)
```

↓

```text-x-trilium-auto
chuong-15
```

---

# 9. Index

Đây là phần khó.

Tiêu đề

```text-x-trilium-auto
Chương 15:
...
```

Ta cần

```text-x-trilium-auto
15
```

Không nên

```text-x-trilium-auto
split()
```

Nên dùng regex.

Ví dụ

```text-x-trilium-auto
import re
```

```text-x-trilium-auto
match = re.search(
    r"(\d+)",
    title
)
```

Nếu có

```text-x-trilium-auto
index = int(
    match.group(1)
)
```

Nếu không

```text-x-trilium-auto
index = 0
```

---

# 10. Không tin tiêu đề

Ví dụ website

```text-x-trilium-auto
Chương Một
```

Regex không được.

Hoặc

```text-x-trilium-auto
Extra 1
```

Hoặc

```text-x-trilium-auto
Phiên ngoại
```

Nên parser phải chấp nhận:

```text-x-trilium-auto
index=0
```

Không crash.

---

# 11. Tạo Model

```text-x-trilium-auto
return ChapterSummaryModel(

    source="truyenfull",

    novel_id=novel_id,

    index=index,

    slug=slug,

    title=title,

    url=url
)
```

---

# 12. Trùng lặp

Một số website

```text-x-trilium-auto
Trang 1

1

2

3

...
50
```

Trang 2

```text-x-trilium-auto
50

51

52
```

Có chương 50 hai lần.

Ta nên loại.

Ví dụ

```text-x-trilium-auto
seen = set()
```

---

```text-x-trilium-auto
if slug in seen:

    continue

seen.add(slug)
```

Rất quan trọng.

---

# 13. Sắp xếp

Website có thể trả

```text-x-trilium-auto
10

9

8

7
```

Ta nên

```text-x-trilium-auto
results.sort(
    key=lambda c: c.index
)
```

Nếu

```text-x-trilium-auto
index=0
```

thì đặt cuối.

Ví dụ

```text-x-trilium-auto
results.sort(
    key=lambda c: (
        c.index == 0,
        c.index
    )
)
```

---

# 14. Không bỏ chương đặc biệt

Ví dụ

```text-x-trilium-auto
Ngoại truyện

Phiên ngoại

Hậu ký
```

Đừng bỏ.

Chỉ để

```text-x-trilium-auto
index=0
```

Sau này người dùng vẫn đọc được.

---

# 15. Tách helper

Parser sẽ đẹp hơn nhiều.

```text-x-trilium-auto
parse_chapter_list()

        │

        ▼

parse_chapter_item()

        │

        ▼

extract_index()

        │

        ▼

extract_slug()
```

Mỗi hàm khoảng 10 dòng.

---

# 16. Kiểm thử

HTML

```text-x-trilium-auto
<li>

<a href="/abc/chuong-1/">

Chương 1

</a>

</li>
```

↓

```text-x-trilium-auto
chapter = parser.parse_chapter_item(...)
```

↓

```text-x-trilium-auto
assert chapter.index==1

assert chapter.slug=="chuong-1"

assert chapter.title=="Chương 1"
```

---

# 17. HTML mẫu

Nên lưu

```text-x-trilium-auto
tests/

    samples/

        novel.html

        chapter_list.html

        chapter.html
```

Parser test sẽ chạy cực nhanh.

Không cần Internet.

---

# 18. Kiến trúc hoàn chỉnh

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

├── extract_index()

└── extract_slug()
```

Đây là parser đủ chuẩn để sử dụng trong một dự án crawler thực tế.

---

# Tuy nhiên, chúng ta có thể làm tốt hơn

Đến đây, parser đã hoạt động được. Nhưng nếu nhìn dưới góc độ kiến trúc, vẫn còn một điểm có thể cải thiện.

Hiện tại `parse_chapter_item()` đang làm nhiều việc:

1. Đọc HTML.
2. Chuẩn hóa URL.
3. Trích xuất slug.
4. Phân tích số chương.
5. Tạo model.

Mình khuyến nghị tách thành các helper nhỏ hơn:

```text-x-trilium-auto
parse_chapter_item()
    │
    ├── parse_chapter_title()
    ├── parse_chapter_url()
    ├── parse_chapter_slug()
    └── parse_chapter_index()
```

Nhờ đó:

- Mỗi hàm chỉ có một trách nhiệm (SRP).
- Có thể kiểm thử từng phần độc lập.
- Nếu sau này TruyenFull đổi cách đặt tên chương, bạn chỉ cần sửa `parse_chapter_index()`.

---

# Bài 9 sẽ là bước cuối của Parser

Sau **Bài 9**, plugin TruyenFull sẽ hoàn chỉnh.

Chúng ta sẽ xây dựng:

- `parse_chapter()`
- Làm sạch nội dung chương.
- Loại bỏ quảng cáo, script, watermark.
- Giữ nguyên định dạng đoạn văn.
- Xử lý ảnh, chú thích, ký tự đặc biệt.
- Trả về `ChapterModel` hoàn chỉnh.

Kết thúc bài 9, plugin sẽ có thể:

```text-x-trilium-auto
Novel URL
    │
    ▼
Danh sách chương
    │
    ▼
Nội dung từng chương
    │
    ▼
Model Python
    │
    ▼
Repository lưu SQLite
```

Đó là lúc phần **Parser của plugin TruyenFull** được xem là hoàn chỉnh và chúng ta sẽ chuyển sang xây dựng `TruyenFullSource` để kết nối `HttpClient`, `Parser` và `Repository` thành một quy trình crawl hoàn chỉnh.