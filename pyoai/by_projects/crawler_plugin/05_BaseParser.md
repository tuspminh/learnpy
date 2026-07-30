Rất tốt. Từ bài này chúng ta sẽ **không còn viết skeleton nữa**, mà bắt đầu viết **code production-ready**.

Mục tiêu của chúng ta không chỉ là "crawl được", mà là xây dựng một parser **dễ test, dễ bảo trì, dễ mở rộng**.

---

# Bài 5 - Xây dựng `BaseParser`

## Tại sao phải có `BaseParser`?

Giả sử sau này bạn có:

```text-x-trilium-auto
plugins/
    truyenfull/
    tangthuvien/
    metruyen/
    bachngocsach/
```

Nếu mỗi plugin đều tự viết:

```text-x-trilium-auto
safe_text()

safe_attr()

clean_html()

normalize_space()

select_first()
```

thì sẽ có rất nhiều đoạn code giống nhau.

Giải pháp là:

```text-x-trilium-auto
BaseParser

        ↑

TruyenFullParser

TangThuVienParser

MeTruyenParser
```

Mọi parser đều kế thừa `BaseParser`.

---

# Bước 1. Tạo cấu trúc

```text-x-trilium-auto
crawler/

    base/

        parser.py
```

Đây là parser dùng chung.

---

# Bước 2. Khởi tạo BeautifulSoup

```text-x-trilium-auto
from bs4 import BeautifulSoup


class BaseParser:

    PARSER = "html.parser"

    def soup(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, self.PARSER)
```

Sau này tất cả parser chỉ cần:

```text-x-trilium-auto
soup = self.soup(html)
```

---

# Bước 3. `safe_text()`

Đây là hàm được gọi hàng nghìn lần.

```text-x-trilium-auto
@staticmethod def safe_text(node) -> str:

    if node is None:
        return ""

    return node.get_text(strip=True)
```

Ví dụ

HTML

```text-x-trilium-auto
<h3>

   Hello World

</h3>
```

↓

```text-x-trilium-auto
Hello World
```

---

# Nhưng vẫn chưa đủ

Ví dụ

```text-x-trilium-auto
<h3>

Hello


World

</h3>
```

`get_text(strip=True)` trả về

```text-x-trilium-auto
Hello
World
```

hoặc nhiều khoảng trắng.

Ta cần chuẩn hóa.

---

# Bước 4. normalize_space()

```text-x-trilium-auto
import re
```

```text-x-trilium-auto
@staticmethod def normalize_space(text: str) -> str:

    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()
```

Ví dụ

```text-x-trilium-auto
Hello


World
```

↓

```text-x-trilium-auto
Hello World
```

---

Sau đó sửa

```text-x-trilium-auto
@staticmethod def safe_text(node):

    if node is None:
        return ""

    return BaseParser.normalize_space(
        node.get_text()
    )
```

---

# Bước 5. `safe_attr()`

```text-x-trilium-auto
@staticmethod def safe_attr(node, attr):

    if node is None:
        return ""

    return node.attrs.get(attr, "")
```

Ví dụ

```text-x-trilium-auto
<img src="cover.jpg">
```

↓

```text-x-trilium-auto
cover.jpg
```

---

# Bước 6. `select_first()`

Đây là helper rất quan trọng.

```text-x-trilium-auto
@staticmethod def select_first(soup, *selectors):

    for selector in selectors:

        node = soup.select_one(selector)

        if node:
            return node

    return None
```

Ví dụ

```text-x-trilium-auto
node = BaseParser.select_first(
    soup,
    ".book-title",
    "h3.title",
    ".title"
)
```

Nếu website thay đổi selector đầu tiên, parser vẫn hoạt động.

---

# Bước 7. `select_all()`

Ta cũng nên có helper.

```text-x-trilium-auto
@staticmethod def select_all(soup, *selectors):

    for selector in selectors:

        nodes = soup.select(selector)

        if nodes:
            return nodes

    return []
```

Ví dụ

```text-x-trilium-auto
items = self.select_all(
    soup,
    ".chapter-list li",
    ".list-chapter li"
)
```

---

# Bước 8. Làm sạch HTML

Đây là phần mà crawler chuyên nghiệp luôn làm.

Ví dụ

```text-x-trilium-auto
<div>

<script>

....

</script>

<p>Hello</p>

<style>

...

</style>

</div>
```

Ta không muốn:

```text-x-trilium-auto
script

style

comment
```

---

Viết

```text-x-trilium-auto
def clean_html(self, node):
```

Đầu tiên

```text-x-trilium-auto
for tag in node.select(
    "script,style"
):
    tag.decompose()
```

`decompose()` nghĩa là xóa khỏi cây HTML.

---

# Bước 9. Xóa comment

```text-x-trilium-auto
from bs4 import Comment
```

```text-x-trilium-auto
for text in node.find_all(
    string=lambda t:
        isinstance(t, Comment)
):
    text.extract()
```

---

Ví dụ

```text-x-trilium-auto
<!-- ads -->
```

↓

bị xóa.

---

# Bước 10. Chuyển `<br>` thành xuống dòng

Đây là lỗi phổ biến.

HTML

```text-x-trilium-auto
Hello

<br>

World
```

Nếu dùng

```text-x-trilium-auto
get_text()
```

↓

```text-x-trilium-auto
HelloWorld
```

Ta sửa

```text-x-trilium-auto
for br in node.find_all("br"):
    br.replace_with("\n")
```

---

# Bước 11. Lấy text

```text-x-trilium-auto
text = node.get_text(
    separator="\n"
)
```

Ví dụ

```text-x-trilium-auto
Hello

World
```

vẫn giữ nguyên.

---

# Bước 12. Chuẩn hóa

```text-x-trilium-auto
return self.normalize_space(
    text
)
```

Nhưng còn một vấn đề...

---

# Vấn đề

Nếu dùng

```text-x-trilium-auto
normalize_space()
```

thì

```text-x-trilium-auto
Hello

World
```

↓

```text-x-trilium-auto
Hello World
```

Mất xuống dòng.

Đối với **nội dung chương**, điều này là không chấp nhận được.

---

# Bước 13. Tách hai loại normalize

## Cho tiêu đề

```text-x-trilium-auto
Hello


World
```

↓

```text-x-trilium-auto
Hello World
```

---

## Cho nội dung

```text-x-trilium-auto
Hello

World
```

↓

```text-x-trilium-auto
Hello

World
```

Giữ nguyên dòng.

Ta tạo:

```text-x-trilium-auto
normalize_text()
```

và

```text-x-trilium-auto
normalize_content()
```

---

Ví dụ

```text-x-trilium-auto
@staticmethod def normalize_content(text):

    text = text.replace("\r", "")

    lines = []

    for line in text.split("\n"):

        line = line.strip()

        if line:
            lines.append(line)

    return "\n".join(lines)
```

---

Kết quả

```text-x-trilium-auto
Hello


World



Python
```

↓

```text-x-trilium-auto
Hello

World

Python
```

Đẹp hơn rất nhiều.

---

# Bước 14. Cấu trúc `BaseParser`

```text-x-trilium-auto
BaseParser
│
├── soup()
├── safe_text()
├── safe_attr()
├── select_first()
├── select_all()
├── normalize_space()
├── normalize_content()
├── clean_html()
```

Đây là nền tảng cho mọi plugin.

---

# Bước 15. `TruyenFullParser`

Bây giờ parser rất đơn giản.

```text-x-trilium-auto
class TruyenFullParser(BaseParser):

    ...
```

Không cần viết lại helper.

Chỉ còn

```text-x-trilium-auto
parse_list()

parse_novel()

parse_chapter()

parse_chapter_list()
```

---

# Kiểm thử từng helper

Đừng đợi đến khi hoàn thành parser mới kiểm thử. Hãy kiểm tra từng hàm nhỏ:

```text-x-trilium-auto
assert BaseParser.normalize_space("  Hello   World  ") == "Hello World"

assert BaseParser.normalize_content(
    "Hello\n\n\nWorld\n"
) == "Hello\nWorld"
```

Việc này giúp phát hiện lỗi sớm và đảm bảo các plugin khác cũng dùng được các helper này.

---

# Cấu trúc hiện tại của plugin

```text-x-trilium-auto
crawler/
├── base/
│   ├── parser.py          ← BaseParser
│   ├── http_client.py
│   └── ...
└── plugins/
    └── truyenfull/
        ├── parser.py       ← TruyenFullParser(BaseParser)
        ├── selectors.py
        ├── urls.py
        └── source.py
```

Đến thời điểm này, kiến trúc đã khá giống với các hệ thống crawler chuyên nghiệp.

---

# Tổng kết

Sau bài này bạn đã có một `BaseParser` có thể tái sử dụng cho mọi website, bao gồm:

- Tạo `BeautifulSoup`.
- Đọc text và attribute an toàn.
- Hỗ trợ nhiều selector dự phòng.
- Làm sạch HTML.
- Chuẩn hóa văn bản thông thường và nội dung chương theo hai cách khác nhau.

Đây là nền móng quan trọng để các parser cụ thể chỉ tập trung vào **logic trích xuất dữ liệu**, không phải xử lý các vấn đề chung.

---

# Bài 6 sẽ bắt đầu crawl dữ liệu thật

Từ **Bài 6**, chúng ta sẽ viết `**parse_list()**` **hoàn chỉnh**.

Bạn sẽ học cách:

- Phân tích HTML thật của trang danh sách truyện.
- Trích xuất từng truyện thành `NovelSummaryModel`.
- Chuẩn hóa URL, ảnh bìa, tên tác giả.
- Xử lý các trường hợp dữ liệu thiếu hoặc HTML thay đổi.
- Viết test với HTML mẫu để đảm bảo parser hoạt động ổn định.

Đến hết bài 6, plugin TruyenFull sẽ **đọc được một trang danh sách truyện và trả về danh sách model Python**, sẵn sàng cho `Source` tiếp tục xử lý.