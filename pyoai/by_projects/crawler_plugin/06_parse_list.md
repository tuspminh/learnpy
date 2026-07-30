Rất hay. Từ bài này trở đi chúng ta sẽ **viết code thật**, không còn chỉ là kiến trúc nữa.

Đây là lúc plugin TruyenFull bắt đầu có thể crawl được dữ liệu.

---

# Bài 6 - Xây dựng `parse_list()`

## Mục tiêu

Sau bài này:

```text-x-trilium-auto
HTTP

↓

HTML

↓

parse_list()

↓

List[NovelSummaryModel]
```

Đây là hàm được gọi nhiều nhất trong toàn bộ crawler.

Ví dụ:

- Crawl truyện mới
- Crawl truyện hot
- Crawl thể loại
- Crawl tác giả
- Crawl truyện hoàn thành

Tất cả đều dùng `parse_list()`.

---

# 1. HTML của trang danh sách

Giả sử HTML có dạng:

```text-x-trilium-auto
<div class="row">

    <div class="col-xs-7">

        <h3>

            <a href="/than-dao-dan-ton/">
                Thần Đạo Đan Tôn
            </a>

        </h3>

    </div>

    <div class="col-xs-3">

        <span class="author">

            Cô Đơn Địa Phi

        </span>

    </div>

</div>
```

Có hàng chục block giống nhau.

---

# 2. Kết quả mong muốn

Parser không trả HTML.

Parser trả Model.

Ví dụ:

```text-x-trilium-auto
NovelSummaryModel(

    title="Thần Đạo Đan Tôn",

    author="Cô Đơn Địa Phi",

    slug="than-dao-dan-ton",

    url="https://truyenfull.vn/than-dao-dan-ton/"
)
```

Danh sách:

```text-x-trilium-auto
[
    NovelSummaryModel(...),

    NovelSummaryModel(...),

    NovelSummaryModel(...)
]
```

---

# 3. Thiết kế Model

Ví dụ:

```text-x-trilium-auto
from dataclasses import dataclass


@dataclass(slots=True)
class NovelSummaryModel:

    title: str

    slug: str

    url: str

    author: str
```

Tại sao chưa có:

- description
- status
- cover

?

Vì trang list thường không có đủ.

Đừng tạo object nửa đầy nửa rỗng.

---

# 4. Cấu trúc `parse_list()`

```text-x-trilium-auto
def parse_list(
    self,
    html: str
):
```

Đầu tiên:

```text-x-trilium-auto
soup = self.soup(html)
```

---

# 5. Lấy tất cả truyện

```text-x-trilium-auto
rows = self.select_all(

    soup,

    *ListSelectors.NOVELS
)
```

Ví dụ

```text-x-trilium-auto
rows

↓

40 item
```

---

# 6. Tạo kết quả

```text-x-trilium-auto
results = []
```

Rất đơn giản.

---

# 7. Duyệt từng item

```text-x-trilium-auto
for row in rows:

    ...
```

Trong mỗi row

ta parse

```text-x-trilium-auto
title

url

author
```

---

# 8. Parse title

```text-x-trilium-auto
title_node = self.select_first(

    row,

    *ListSelectors.TITLE
)
```

↓

```text-x-trilium-auto
title = self.safe_text(
    title_node
)
```

Ví dụ

```text-x-trilium-auto
Thần Đạo Đan Tôn
```

---

# 9. Parse URL

```text-x-trilium-auto
link_node = self.select_first(

    row,

    *ListSelectors.LINK
)
```

↓

```text-x-trilium-auto
url = self.safe_attr(
    link_node,
    "href"
)
```

Nhận

```text-x-trilium-auto
/than-dao-dan-ton/
```

---

# 10. URL tuyệt đối

Đây là lỗi mà người mới rất hay gặp.

Website thường trả

```text-x-trilium-auto
/than-dao-dan-ton/
```

Không phải

```text-x-trilium-auto
https://truyenfull.vn/than-dao-dan-ton/
```

Ta phải chuẩn hóa.

Trong `urls.py` đã có

```text-x-trilium-auto
TruyenFullUrls.full_url(
    path
)
```

↓

```text-x-trilium-auto
url = TruyenFullUrls.full_url(url)
```

↓

```text-x-trilium-auto
https://truyenfull.vn/than-dao-dan-ton/
```

---

# 11. Parse slug

Sai lầm phổ biến:

```text-x-trilium-auto
slug = url.split("/")[-1]
```

Nếu URL

```text-x-trilium-auto
https://....

/
```

↓

```text-x-trilium-auto
""
```

Sai.

---

Nên dùng

```text-x-trilium-auto
from urllib.parse import urlparse from pathlib import PurePosixPath
```

```text-x-trilium-auto
def extract_slug(url):

    path = urlparse(url).path

    return PurePosixPath(path).name
```

Ví dụ

```text-x-trilium-auto
https://truyenfull.vn/than-dao-dan-ton/
```

↓

```text-x-trilium-auto
than-dao-dan-ton
```

Ổn định hơn rất nhiều.

---

# 12. Parse author

```text-x-trilium-auto
author = self.safe_text(

    self.select_first(

        row,

        *ListSelectors.AUTHOR
    )
)
```

↓

```text-x-trilium-auto
Cô Đơn Địa Phi
```

---

# 13. Tạo Model

```text-x-trilium-auto
novel = NovelSummaryModel(

    title=title,

    slug=slug,

    url=url,

    author=author
)
```

↓

```text-x-trilium-auto
results.append(
    novel
)
```

---

# 14. Hoàn chỉnh

```text-x-trilium-auto
return results
```

↓

```text-x-trilium-auto
List[NovelSummaryModel]
```

---

# 15. Bỏ qua item lỗi

Website đôi khi có:

```text-x-trilium-auto
quảng cáo

banner

truyện VIP

...
```

Không nên crash.

Ví dụ

```text-x-trilium-auto
if not title:

    continue
```

---

Hoặc

```text-x-trilium-auto
if not slug:

    continue
```

---

# 16. Logger

Không nên

```text-x-trilium-auto
except:

    pass
```

Hãy

```text-x-trilium-auto
except Exception as ex:

    logger.exception(ex)
```

và tiếp tục.

Một item lỗi không nên làm hỏng cả trang.

---

# 17. Tách nhỏ parser

Đây là cách parser chuyên nghiệp thường làm.

Thay vì:

```text-x-trilium-auto
parse_list()
```

dài 200 dòng.

Ta tách:

```text-x-trilium-auto
parse_list()

↓

parse_list_item()

↓

NovelSummaryModel
```

Ví dụ

```text-x-trilium-auto
for row in rows:

    novel = self.parse_list_item(row)

    if novel:

        results.append(
            novel
        )
```

Ưu điểm:

- Dễ đọc.
- Dễ test.
- Có thể tái sử dụng.

---

# 18. Thiết kế cuối cùng

```text-x-trilium-auto
parse_list()

        │

        ▼

parse_list_item()

        │

        ▼

NovelSummaryModel
```

Đây là cách tổ chức mà mình khuyến nghị cho toàn bộ parser.

---

# Mã giả (Pseudo-code)

Đây là toàn bộ luồng xử lý:

```text-x-trilium-auto
def parse_list(html):

    soup = self.soup(html)

    rows = self.select_all(
        soup,
        *ListSelectors.NOVELS
    )

    results = []

    for row in rows:

        novel = self.parse_list_item(row)

        if novel:
            results.append(novel)

    return results
```

Trong đó:

```text-x-trilium-auto
def parse_list_item(row):

    # 1. Lấy title
    # 2. Lấy link
    # 3. Chuẩn hóa URL
    # 4. Trích slug
    # 5. Lấy author
    # 6. Tạo NovelSummaryModel
```

---

# Kiểm thử

Tạo một file HTML mẫu chứa 3 truyện và kiểm tra:

```text-x-trilium-auto
novels = parser.parse_list(html)

assert len(novels) == 3

assert novels[0].title == "Thần Đạo Đan Tôn"

assert novels[0].slug == "than-dao-dan-ton"

assert novels[0].author == "Cô Đơn Địa Phi"
```

Parser nên được kiểm thử bằng **HTML lưu sẵn**, không phụ thuộc vào mạng. Điều này giúp test chạy nhanh và ổn định.

---

# Tổng kết

Sau bài này bạn đã hiểu:

- Vai trò của `parse_list()` trong toàn bộ crawler.
- Thiết kế `NovelSummaryModel` chỉ chứa dữ liệu thực sự có ở trang danh sách.
- Chuẩn hóa URL và trích xuất slug đúng cách.
- Tách `parse_list_item()` để mã nguồn rõ ràng và dễ kiểm thử.
- Bỏ qua từng item lỗi thay vì làm hỏng cả quá trình crawl.

---

# Bài 7 sẽ rất quan trọng

Ở **Bài 7**, chúng ta sẽ xây dựng `**parse_novel()**`.

Đây là hàm đọc **trang chi tiết truyện** và tạo `NovelModel` đầy đủ, bao gồm:

- Tên truyện.
- Tác giả.
- Ảnh bìa.
- Mô tả.
- Thể loại.
- Trạng thái.
- Số chương (nếu có).
- Các metadata khác.

Sau bài 7, plugin của bạn sẽ có thể **crawl đầy đủ thông tin của một bộ truyện**, chỉ còn thiếu danh sách chương và nội dung chương để hoàn thiện toàn bộ quy trình.