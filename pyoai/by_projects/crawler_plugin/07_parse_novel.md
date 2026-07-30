Rất tốt. Từ bài này trở đi, chúng ta sẽ bắt đầu xây dựng **plugin theo chuẩn production**, tức là mỗi hàm đều đủ chất lượng để sau này dùng trong hệ thống lớn.

Đây là bài cực kỳ quan trọng.

---

# Bài 7 - Xây dựng `parse_novel()`

## Mục tiêu

Sau bài này:

```text-x-trilium-auto
Novel URL

↓

HttpClient

↓

HTML

↓

parse_novel()

↓

NovelModel
```

Ví dụ:

```text-x-trilium-auto
https://truyenfull.vn/than-dao-dan-ton/
```

↓

```text-x-trilium-auto
NovelModel(
    source="truyenfull",
    source_id="than-dao-dan-ton",
    title="Thần Đạo Đan Tôn",
    author="Cô Đơn Địa Phi",
    cover="https://....jpg",
    description="...",
    categories=["Tiên Hiệp","Huyền Huyễn"],
    status="completed",
)
```

Đây là model sẽ được lưu vào SQLite.

---

# 1. Không trả về dict

Sai:

```text-x-trilium-auto
return {
    "title": title,
    "author": author,
    ...
}
```

Đúng:

```text-x-trilium-auto
return NovelModel(...)
```

Parser luôn làm việc với Model.

---

# 2. Thiết kế NovelModel

Khác với `NovelSummaryModel`, model này chứa đầy đủ thông tin.

Ví dụ:

```text-x-trilium-auto
from dataclasses import dataclass, field

@dataclass(slots=True)
class NovelModel:
    source: str

    source_id: str

    url: str

    title: str

    author: str

    cover: str

    description: str

    status: str

    categories: list[str] = field(default_factory=list)
```

Tại sao có `source_id`?

Ví dụ

```text-x-trilium-auto
than-dao-dan-ton
```

Đây là ID duy nhất của truyện trong TruyenFull.

Sau này khi đồng bộ dữ liệu, ta không cần tìm theo URL.

---

# 3. Luồng xử lý

```text-x-trilium-auto
HTML

↓

BeautifulSoup

↓

parse_title()

↓

parse_author()

↓

parse_cover()

↓

parse_description()

↓

parse_status()

↓

parse_categories()

↓

NovelModel
```

Không nên để mọi thứ trong một hàm dài 300 dòng.

---

# 4. `parse_title()`

Ví dụ HTML

```text-x-trilium-auto
<h3 class="title">
Thần Đạo Đan Tôn
</h3>
```

Code:

```text-x-trilium-auto
def parse_title(self, soup):

    node = self.select_first(
        soup,
        *NovelSelectors.TITLE
    )

    return self.safe_text(node)
```

Rất đơn giản.

---

# 5. `parse_author()`

Ví dụ HTML

```text-x-trilium-auto
<a href="/tac-gia/co-doc-dia-phi/">

Cô Đơn Địa Phi

</a>
```

Code:

```text-x-trilium-auto
def parse_author(self, soup):

    node = self.select_first(
        soup,
        *NovelSelectors.AUTHOR
    )

    return self.safe_text(node)
```

---

# 6. `parse_cover()`

HTML

```text-x-trilium-auto
<img
    class="cover"
    src="/images/abc.jpg" >
```

Không nên chỉ lấy `src`.

```text-x-trilium-auto
cover = self.safe_attr(node, "src")
```

Sau đó:

```text-x-trilium-auto
cover = TruyenFullUrls.full_url(
    cover
)
```

Để luôn có URL tuyệt đối.

---

# 7. `parse_description()`

Đây là phần khó nhất.

HTML

```text-x-trilium-auto
<div class="desc-text">

<p>Hello</p>

<p>World</p>

</div>
```

Không nên:

```text-x-trilium-auto
node.get_text()
```

Mà dùng:

```text-x-trilium-auto
self.clean_html(node)
```

Sau đó:

```text-x-trilium-auto
return self.normalize_content(text)
```

Giữ nguyên xuống dòng.

---

# 8. `parse_status()`

HTML thường hiển thị:

```text-x-trilium-auto
Tình trạng:
Hoàn
```

hoặc

```text-x-trilium-auto
Đang ra
```

Nhưng trong Database **không nên lưu tiếng Việt**.

Ta chuẩn hóa:

```text-x-trilium-auto
STATUS_MAP = {
    "Hoàn": "completed",
    "Đang ra": "ongoing",
}
```

Code:

```text-x-trilium-auto
text = self.safe_text(node)

status = STATUS_MAP.get(
    text,
    "unknown"
)
```

Sau này dashboard sẽ dễ lọc hơn.

---

# 9. `parse_categories()`

HTML

```text-x-trilium-auto
<a>Tiên Hiệp</a>

<a>Huyền Huyễn</a>

<a>Xuyên Không</a>
```

Không nên trả:

```text-x-trilium-auto
"Tiên Hiệp,Huyền Huyễn"
```

Đúng:

```text-x-trilium-auto
[
    "Tiên Hiệp",
    "Huyền Huyễn",
    "Xuyên Không"
]
```

Code:

```text-x-trilium-auto
categories = []

for node in nodes:

    categories.append(
        self.safe_text(node)
    )
```

---

# 10. Chuẩn hóa Category

Sau này nhiều website sẽ có:

```text-x-trilium-auto
Tiên hiệp

Tiên Hiệp

TIÊN HIỆP
```

Ta chuẩn hóa trong `normalizer.py`

Ví dụ:

```text-x-trilium-auto
CATEGORY_MAP = {
    "Tiên hiệp": "Tiên Hiệp",
    "TIÊN HIỆP": "Tiên Hiệp",
}
```

Parser gọi:

```text-x-trilium-auto
normalize_category(name)
```

Không tự xử lý.

---

# 11. `parse_novel()`

Lúc này rất đẹp.

```text-x-trilium-auto
def parse_novel(
    self,
    html,
    url
):
```

↓

```text-x-trilium-auto
soup = self.soup(html)
```

↓

```text-x-trilium-auto
title = self.parse_title(soup)
```

↓

```text-x-trilium-auto
author = self.parse_author(soup)
```

↓

```text-x-trilium-auto
cover = self.parse_cover(soup)
```

↓

```text-x-trilium-auto
description = self.parse_description(soup)
```

↓

```text-x-trilium-auto
status = self.parse_status(soup)
```

↓

```text-x-trilium-auto
categories = self.parse_categories(soup)
```

↓

```text-x-trilium-auto
return NovelModel(...)
```

---

# 12. Không để parser biết slug

Đừng viết:

```text-x-trilium-auto
slug = ...
```

bên trong parser.

Slug đến từ URL.

Nên:

```text-x-trilium-auto
parse_novel(
    html,
    url
)
```

Parser chỉ:

```text-x-trilium-auto
source_id = extract_slug(url)
```

Đây là một phép biến đổi dữ liệu đơn giản, không phải logic mạng.

---

# 13. Logger

Nếu một trường bị thiếu:

```text-x-trilium-auto
cover=""
```

không nên crash.

Chỉ log:

```text-x-trilium-auto
Missing cover:
https://....
```

và vẫn tạo `NovelModel`.

Crawler cần **chịu lỗi tốt (fault tolerant)**.

---

# 14. Kiểm thử

Lưu HTML thật vào:

```text-x-trilium-auto
tests/
    samples/

        novel.html
```

Sau đó:

```text-x-trilium-auto
novel = parser.parse_novel(
    html,
    url
)

assert novel.title == ...

assert novel.author == ...

assert novel.status == ...

assert len(
    novel.categories
) == 5
```

Không cần Internet.

---

# 15. Parser chuyên nghiệp

Cuối cùng parser sẽ như sau:

```text-x-trilium-auto
parse_novel()

│

├── parse_title()

├── parse_author()

├── parse_cover()

├── parse_description()

├── parse_status()

├── parse_categories()

└── NovelModel()
```

Mỗi hàm khoảng 10–20 dòng.

Đây là cấu trúc rất dễ đọc và dễ bảo trì.

---

# 16. Chuẩn bị cho bài sau

Sau khi có `NovelModel`, chúng ta vẫn chưa biết truyện có bao nhiêu chương.

Trang truyện chỉ hiển thị:

```text-x-trilium-auto
Chương 1

...

Chương 50
```

hoặc

```text-x-trilium-auto
Trang 1

Trang 2

Trang 3

...
```

Làm sao parser lấy toàn bộ danh sách chương?

Đó là nhiệm vụ của:

```text-x-trilium-auto
parse_chapter_list()
```

Đây là hàm được gọi nhiều nhất trong toàn bộ hệ thống vì một truyện có thể có từ vài chục đến hàng chục nghìn chương.

---

# Kiến thức rút ra

Qua bài này, bạn đã học được các nguyên tắc quan trọng:

- Mỗi loại dữ liệu có một hàm `parse_*()` riêng.
- `parse_novel()` chỉ đóng vai trò điều phối.
- Chuẩn hóa dữ liệu (trạng thái, thể loại...) trước khi lưu vào model.
- Parser luôn trả về `NovelModel`, không trả `dict`.
- Xử lý thiếu dữ liệu theo hướng chịu lỗi, không làm dừng toàn bộ quá trình crawl.
- Kiểm thử parser bằng HTML mẫu thay vì phụ thuộc vào website thật.

---

## Bài 8 sẽ là phần khó nhất của parser

Ở **Bài 8**, chúng ta sẽ xây dựng `parse_chapter_list()` theo chuẩn production.

Chúng ta sẽ học:

- Thiết kế `ChapterSummaryModel`.
- Phân tích HTML danh sách chương.
- Xử lý truyện có nhiều trang chương.
- Trích xuất số thứ tự chương, tiêu đề, URL.
- Loại bỏ chương trùng lặp.
- Sắp xếp đúng thứ tự chương.
- Chuẩn bị dữ liệu cho bước tải nội dung chương.

Sau bài 8, plugin TruyenFull sẽ gần như hoàn chỉnh về mặt **thu thập metadata**, chỉ còn thiếu bước đọc nội dung từng chương ở bài tiếp theo.