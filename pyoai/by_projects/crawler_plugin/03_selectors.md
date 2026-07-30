Rất tốt. Từ bài này trở đi chúng ta sẽ bắt đầu **xây dựng Parser**. Đây là phần quan trọng nhất của một plugin crawler.

> Theo kinh nghiệm thực tế, khoảng **70% công sức bảo trì crawler nằm ở Parser**, vì website thường thay đổi HTML chứ rất hiếm khi thay đổi URL.

Do đó, chúng ta sẽ thiết kế sao cho khi TruyenFull đổi giao diện, chỉ cần sửa một vài file.

---

# Bài 3 - Thiết kế `selectors.py`

## Mục tiêu

Sau bài này bạn sẽ hiểu:

- CSS Selector là gì
- Vì sao không nên viết selector trực tiếp trong parser
- Cách thiết kế `selectors.py`
- Cách dự phòng khi website thay đổi HTML
- Chuẩn bị cho `parser.py`

---

# 1. Parser hoạt động như thế nào?

Giả sử HttpClient đã tải HTML:

```text-x-trilium-auto
HttpClient

↓

HTML

↓

Parser

↓

NovelModel
```

Ví dụ:

```text-x-trilium-auto
<html>

    ...

</html>
```

Parser phải tìm được:

```text-x-trilium-auto
Tên truyện

Tác giả

Ảnh

Mô tả

Danh sách chương
```

Làm sao tìm?

→ CSS Selector.

---

# 2. CSS Selector là gì?

Ví dụ HTML

```text-x-trilium-auto
<div class="book">

    <h3 class="title">
        Thần Đạo Đan Tôn
    </h3>

</div>
```

Selector:

```text-x-trilium-auto
h3.title
```

sẽ lấy

```text-x-trilium-auto
Thần Đạo Đan Tôn
```

---

Ví dụ

```text-x-trilium-auto
<img class="cover"
     src="abc.jpg">
```

Selector

```text-x-trilium-auto
img.cover
```

lấy được

```text-x-trilium-auto
abc.jpg
```

---

Ví dụ

```text-x-trilium-auto
<div class="desc-text">

....

</div>
```

Selector

```text-x-trilium-auto
div.desc-text
```

---

Ví dụ

```text-x-trilium-auto
<ul class="list-chapter">

    <li>

        <a> 
```

Selector

```text-x-trilium-auto
ul.list-chapter li a
```

---

# 3. Sai lầm của người mới

Nhiều người viết như sau:

```text-x-trilium-auto
title = soup.select_one("h3.title")

cover = soup.select_one("img.cover")

desc = soup.select_one("div.desc-text")
```

Parser vài trăm dòng sẽ thành:

```text-x-trilium-auto
title = ...

cover = ...

author = ...

status = ...

category = ...

chapter = ...

...

...
```

Hàng chục selector nằm lẫn trong logic.

Nếu website đổi HTML thì phải sửa khắp nơi.

---

# 4. Ý tưởng

Ta gom toàn bộ selector.

```text-x-trilium-auto
Parser

↓

Selectors

↓

HTML
```

Parser không biết selector là gì.

Parser chỉ hỏi:

```text-x-trilium-auto
selector title

selector cover

selector chapter
```

---

# 5. Cấu trúc

```text-x-trilium-auto
plugins/

    truyenfull/

        selectors.py
```

---

# 6. Thiết kế class

```text-x-trilium-auto
class NovelSelectors:
    ...
```

Toàn bộ selector của trang truyện.

---

# 7. Selector tiêu đề

Ví dụ

```text-x-trilium-auto
<h3 class="title">

Thần Đạo Đan Tôn

</h3>
```

ta khai báo

```text-x-trilium-auto
class NovelSelectors:

    TITLE = "h3.title"
```

---

Parser dùng

```text-x-trilium-auto
soup.select_one(
    NovelSelectors.TITLE
)
```

---

# 8. Cover

```text-x-trilium-auto
class NovelSelectors:

    COVER = "img.cover"
```

---

# 9. Description

```text-x-trilium-auto
class NovelSelectors:

    DESCRIPTION = "div.desc-text"
```

---

# 10. Danh sách chapter

```text-x-trilium-auto
class NovelSelectors:

    CHAPTER_ITEMS = "ul.list-chapter li"
```

---

# 11. Link chapter

```text-x-trilium-auto
class NovelSelectors:

    CHAPTER_LINK = "a"
```

---

# 12. Selector cho trang list

Trang list khác.

Ta tạo class khác.

```text-x-trilium-auto
class ListSelectors:
```

Ví dụ

```text-x-trilium-auto
class ListSelectors:

    NOVELS = "div.row"
```

---

Tên

```text-x-trilium-auto
TITLE = "h3 a"
```

---

Tác giả

```text-x-trilium-auto
AUTHOR = ".author"
```

---

Link

```text-x-trilium-auto
LINK = "h3 a"
```

---

# 13. Selector của chapter

Ta lại tách.

```text-x-trilium-auto
class ChapterSelectors:
```

---

Tiêu đề

```text-x-trilium-auto
TITLE = ".chapter-title"
```

---

Nội dung

```text-x-trilium-auto
CONTENT = ".chapter-c"
```

---

Nút tiếp

```text-x-trilium-auto
NEXT = "#next_chap"
```

---

Nút trước

```text-x-trilium-auto
PREVIOUS = "#prev_chap"
```

---

# 14. File hoàn chỉnh

```text-x-trilium-auto
class ListSelectors:
    NOVELS = "div.row"

    TITLE = "h3 a"

    LINK = "h3 a"

    AUTHOR = ".author"


class NovelSelectors:
    TITLE = "h3.title"

    COVER = "img.cover"

    DESCRIPTION = ".desc-text"

    CHAPTER_ITEMS = ".list-chapter li"

    CHAPTER_LINK = "a"


class ChapterSelectors:
    TITLE = ".chapter-title"

    CONTENT = ".chapter-c"

    NEXT = "#next_chap"

    PREVIOUS = "#prev_chap"
```

---

# 15. Vì sao chia thành nhiều class?

Nếu viết

```text-x-trilium-auto
Selectors.TITLE
```

thì không biết

```text-x-trilium-auto
Title gì?

Title truyện?

Title chapter?

Title list?
```

Nhưng

```text-x-trilium-auto
NovelSelectors.TITLE
```

rõ ràng hơn.

---

# 16. Khi website thay đổi

Ví dụ

HTML cũ

```text-x-trilium-auto
<h3 class="title">
```

HTML mới

```text-x-trilium-auto
<h1 class="book-title">
```

Bạn chỉ sửa

```text-x-trilium-auto
TITLE = "h1.book-title"
```

Parser không cần sửa.

Đây là nguyên lý **Single Source of Truth**: mỗi thông tin chỉ nên được định nghĩa ở một nơi duy nhất.

---

# 17. Thiết kế nâng cao (Khuyến nghị)

Trong thực tế, website thường thay đổi giao diện. Một kỹ thuật hay là cho phép **nhiều selector dự phòng**.

Thay vì:

```text-x-trilium-auto
TITLE = "h3.title"
```

hãy dùng:

```text-x-trilium-auto
TITLE = (
    "h3.title",
    "h1.book-title",
    ".title"
)
```

Parser sẽ thử lần lượt đến khi tìm thấy kết quả.

Ví dụ:

```text-x-trilium-auto
def select_first(soup, *selectors):
    for selector in selectors:
        node = soup.select_one(selector)
        if node:
            return node
    return None
```

Sử dụng:

```text-x-trilium-auto
title_node = select_first(soup, *NovelSelectors.TITLE)
```

Nhờ đó, khi website thay đổi nhẹ, plugin vẫn có thể hoạt động mà chưa cần sửa ngay.

---

# 18. Cấu trúc plugin đến hiện tại

```text-x-trilium-auto
plugins/
└── truyenfull/
    ├── __init__.py
    ├── urls.py
    ├── selectors.py
    ├── parser.py      ← sẽ viết ở bài sau
    ├── source.py
    ├── normalizer.py
    └── tests/
```

---

# Bài tập

Hãy mở trang HTML của TruyenFull bằng trình duyệt (F12) và thử xác định thêm các selector cho:

1. Trạng thái truyện (Đang ra/Hoàn thành).
2. Danh sách thể loại.
3. Tên tác giả.
4. Tên nguồn dịch (nếu có).
5. Số chương.

Sau đó bổ sung chúng vào `NovelSelectors` theo cùng phong cách.

---

# Tổng kết

Sau bài này, bạn đã học được:

- CSS Selector là nền tảng của parser.
- Không nên viết selector trực tiếp trong mã phân tích.
- Tách `selectors.py` giúp mã nguồn dễ bảo trì và dễ mở rộng.
- Chia selector theo từng loại trang (`ListSelectors`, `NovelSelectors`, `ChapterSelectors`) giúp cấu trúc rõ ràng.
- Thiết kế selector dự phòng giúp crawler bền vững hơn khi website thay đổi.

---

## Bài 4 sẽ rất thú vị

Ở **Bài 4**, chúng ta sẽ bắt đầu viết `**parser.py**` thực sự.

Đây sẽ là một parser chuyên nghiệp với các thành phần:

- `BaseParser`
- `TruyenFullParser`
- Các hàm `parse_list()`, `parse_novel()`, `parse_chapter_list()`, `parse_chapter()`
- Các hàm tiện ích như `safe_text()`, `safe_attr()`, `select_first()`, `clean_html()`

Đến hết bài 4, plugin của bạn sẽ có thể **đọc HTML và chuyển thành các model Python** sẵn sàng để lưu vào SQLite. Đây là bước quan trọng nhất trong toàn bộ plugin.