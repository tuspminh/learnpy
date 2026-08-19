Dưới đây là tài liệu tra cứu đầy đủ và chi tiết nhất về **thư viện `html2text**` trong Python, bao gồm hàm cấp module, lớp chính (`HTML2Text`), tất cả các phương thức, thuộc tính cấu hình và ví dụ minh họa trực quan.

---

## 1. Hàm cấp Module (Module-Level Function)

Nếu bạn không cần tùy chỉnh nâng cao, `html2text` cung cấp một hàm tiện ích nhanh:

### `html2text.html2text(html, baseurl="")`

* **Cú pháp:**
```python
import html2text

result = html2text.html2text(html_string, baseurl="https://example.com")

```


* **Tham số:**
* `html` (*str*): Chuỗi HTML cần chuyển đổi.
* `baseurl` (*str*, tùy chọn): URL gốc để nối các đường dẫn tương đối (relative links).


* **Trả về:** Chuỗi văn bản định dạng Markdown.

---

## 2. Lớp chính: `html2text.HTML2Text`

Để tùy chỉnh các quy tắc chuyển đổi, bạn sẽ khởi tạo một đối tượng từ lớp `HTML2Text`.

```python
import html2text

h = html2text.HTML2Text(baseurl="", bodywidth=None)

```

### Các phương thức (Methods) chính

| Phương thức | Cú pháp | Mô tả |
| --- | --- | --- |
| **`__init__()`** | `HTML2Text(baseurl="", bodywidth=None)` | Khởi tạo đối tượng parser. |
| **`handle()`** | `h.handle(html_string)` | **Phương thức chính:** Nhận vào chuỗi HTML và trả về chuỗi Markdown. |
| **`feed()`** | `h.feed(data)` | *(Kế thừa từ HTMLParser)* Đưa từng phần dữ liệu HTML vào parser. |
| **`close()`** | `h.close()` | *(Kế thừa từ HTMLParser)* Đóng parser và xử lý nốt phần dữ liệu còn đọng lại. |

---

## 3. Chi tiết tất cả các Thuộc tính Cấu hình (Attributes)

Bạn có thể thay đổi các thuộc tính này trên đối tượng `h` trước khi gọi hàm `.handle()`.

### A. Quản lý Dòng & Văn bản (Line & Text Wrapping)

| Thuộc tính | Kiểu dữ liệu | Mặc định | Ý nghĩa & Cú pháp |
| --- | --- | --- | --- |
| **`body_width`** | `int` | `78` | Số ký tự tối đa trên 1 dòng. Đặt `= 0` hoặc `None` để **tắt tự động xuống dòng**. <br>

<br>`h.body_width = 0` |
| **`single_line_break`** | `bool` | `False` | Nếu `True`, một ký tự xuống dòng `\n` trong HTML sẽ được coi như thẻ `<br>`. <br>

<br>`h.single_line_break = True` |
| **`unicode_snob`** | `bool` | `True` | Nếu `True`, giữ nguyên các ký tự Unicode (như tiếng Việt, emoji, ngoặc kép thông minh). <br>

<br>`h.unicode_snob = True` |

---

### B. Bỏ qua / Bật tắt các Thẻ HTML (Element Filtering)

| Thuộc tính | Kiểu dữ liệu | Mặc định | Ý nghĩa & Cú pháp |
| --- | --- | --- | --- |
| **`ignore_links`** | `bool` | `False` | Nếu `True`, loại bỏ các đường dẫn (`<a>`), chỉ giữ lại văn bản hiển thị. <br>

<br>`h.ignore_links = True` |
| **`ignore_images`** | `bool` | `False` | Nếu `True`, loại bỏ hoàn toàn các thẻ hình ảnh (`<img>`). <br>

<br>`h.ignore_images = True` |
| **`ignore_emphasis`** | `bool` | `False` | Nếu `True`, loại bỏ định dạng in đậm/in nghiêng (`<b>`, `<i>`, `<em>`, `<strong>`). <br>

<br>`h.ignore_emphasis = True` |
| **`ignore_tables`** | `bool` | `False` | Nếu `True`, bỏ qua bảng (`<table>`) không chuyển thành Markdown table. <br>

<br>`h.ignore_tables = True` |
| **`hide_strikethrough`** | `bool` | `False` | Nếu `True`, bỏ qua định dạng gạch ngang (`<s>`, `<strike>`, `<del>`). <br>

<br>`h.hide_strikethrough = True` |

---

### C. Xử lý Đường dẫn & Hình ảnh (Links & Images)

| Thuộc tính | Kiểu dữ liệu | Mặc định | Ý nghĩa & Cú pháp |
| --- | --- | --- | --- |
| **`baseurl`** | `str` | `""` | URL gốc để chuyển đổi link tương đối (`/about`) thành tuyệt đối (`[https://site.com/about](https://site.com/about)`). <br>

<br>`h.baseurl = "[https://example.com](https://example.com)"` |
| **`use_automatic_links`** | `bool` | `True` | Nếu `True`, tự động chuyển link dạng text thành `[http://link.com](http://link.com)`. <br>

<br>`h.use_automatic_links = False` |
| **`protect_links`** | `bool` | `False` | Nếu `True`, bảo vệ URL không bị chèn ngắt dòng giữa chừng khi dòng quá dài. <br>

<br>`h.protect_links = True` |
| **`images_to_alt`** | `bool` | `False` | Nếu `True`, thay thế thẻ ảnh `<img>` bằng đoạn văn bản Alt Text thay vì dạng `![alt](url)`. <br>

<br>`h.images_to_alt = True` |
| **`default_image_alt`** | `str` | `""` | Văn bản hiển thị mặc định nếu ảnh không có thuộc tính `alt=""`. <br>

<br>`h.default_image_alt = "Hình ảnh"` |
| **`images_as_html`** | `bool` | `False` | Nếu `True`, giữ nguyên thẻ `<img>` dưới dạng HTML gốc thay vì Markdown. <br>

<br>`h.images_as_html = True` |
| **`images_with_size`** | `bool` | `False` | Nếu `True`, giữ lại thông số chiều rộng/chiều cao của ảnh nếu có. <br>

<br>`h.images_with_size = True` |

---

### D. Tùy biến Ký tự Định dạng Markdown (Markdown Styling)

| Thuộc tính | Kiểu dữ liệu | Mặc định | Ý nghĩa & Cú pháp |
| --- | --- | --- | --- |
| **`ul_item_mark`** | `str` | `"*"` | Ký tự đại diện cho danh sách không thứ tự (`*`, `-`, hoặc `+`). <br>

<br>`h.ul_item_mark = "-"` |
| **`emphasis_mark`** | `str` | `"_"` hoặc `"*"` | Ký tự dùng cho in nghiêng (`_` hoặc `*`). <br>

<br>`h.emphasis_mark = "_"` |
| **`strong_mark`** | `str` | `"**"` | Ký tự dùng cho in đậm (`**` hoặc `__`). <br>

<br>`h.strong_mark = "**"` |
| **`mark_code`** | `bool` | `False` | Nếu `True`, bao bọc các khối `<code>` hoặc `<pre>` bằng ký hiệu code block `````. <br>

<br>`h.mark_code = True` |

---

### E. Xử lý Bảng & Công cụ khác (Tables & Integrations)

| Thuộc tính | Kiểu dữ liệu | Mặc định | Ý nghĩa & Cú pháp |
| --- | --- | --- | --- |
| **`bypass_tables`** | `bool` | `False` | Nếu `True`, giữ nguyên thẻ `<table>` dạng HTML gốc thay vì cố biến nó thành Markdown. <br>

<br>`h.bypass_tables = True` |
| **`pad_tables`** | `bool` | `False` | Nếu `True`, thêm khoảng trắng vào các ô trong bảng để bảng Markdown thẳng hàng và đẹp mắt hơn. <br>

<br>`h.pad_tables = True` |
| **`google_doc`** | `bool` | `False` | Bật chế độ tối ưu hóa đặc biệt khi xử lý HTML xuất ra từ Google Docs. <br>

<br>`h.google_doc = True` |

---

## 4. Ví dụ Tổng hợp Sử dụng Tất cả Cấu hình

Đoạn mã bên dưới minh họa cách kết hợp hầu hết các thuộc tính cấu hình quan trọng của `html2text`:

```python
import html2text

# HTML đầu vào phức tạp
html_input = """
<html>
<body>
    <h1>Hướng dẫn Lập trình</h1>
    <p>Chào mừng bạn đến với <b>Python</b>! Ghé thăm <a href="/docs">Tài liệu</a>.</p>
    
    <p>Danh sách tính năng:</p>
    <ul>
        <li>Dễ đọc</li>
        <li>Mạnh mẽ</li>
    </ul>

    <p>Ảnh minh họa: <img src="/images/logo.png" alt="Python Logo"></p>
    
    <pre><code>print("Hello World")</code></pre>

    <table border="1">
        <tr><th>Ngôn ngữ</th><th>Độ khó</th></tr>
        <tr><td>Python</td><td>Dễ</td></tr>
    </table>
</body>
</html>
"""

# Khởi tạo đối tượng
h = html2text.HTML2Text()

# --- BỘ CẤU HÌNH TÙY CHỈNH ---
# 1. Cấu hình Dòng & Mã hóa
h.body_width = 0                  # Tắt tự động ngắt dòng
h.unicode_snob = True             # Giữ nguyên ký tự UTF-8

# 2. Xử lý Link & Ảnh
h.baseurl = "[https://python.org](https://python.org)"  # Nối URL tuyệt đối cho các link/ảnh tương đối
h.default_image_alt = "Ảnh minh họa"

# 3. Định dạng Markdown
h.ul_item_mark = "-"              # Dùng dấu "-" cho danh sách tròn
h.strong_mark = "**"              # Dùng "**" cho in đậm
h.mark_code = True                # Đánh dấu khối <code> dạng markdown block

# 4. Xử lý Bảng
h.pad_tables = True               # Căn đệm ô trong bảng cho thẳng hàng

# --- THỰC THI CHUYỂN ĐỔI ---
markdown_output = h.handle(html_input)

print(markdown_output)

```

**Kết quả đầu ra (Markdown):**

```markdown
# Hướng dẫn Lập trình

Chào mừng bạn đến với **Python**! Ghé thăm [Tài liệu](https://python.org/docs).

Danh sách tính năng:

- Dễ đọc
- Mạnh mẽ

Ảnh minh họa: ![Python Logo](https://python.org/images/logo.png)

`print("Hello World")`

| Ngôn ngữ | Độ khó |
| --- | --- |
| Python | Dễ |

```