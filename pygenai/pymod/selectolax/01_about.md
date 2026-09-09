Chào bạn! Với vai trò là một lập trình viên Python chuyên sâu về bóc tách dữ liệu (Web Scraping), tôi rất hào hứng khi giới thiệu cho bạn **`selectolax`**.

Nếu bạn đã từng dùng `BeautifulSoup4` và cảm thấy nó chạy quá chậm khi xử lý hàng ngàn trang web, thì `selectolax` chính là "vũ khí tối tân" giúp bạn tăng tốc độ xử lý lên **từ 5 đến 30 lần**.

---

## 1. Selectolax là gì? Tại sao lại nhanh đến vậy?

`selectolax` là một thư viện Python wrapper xung quanh hai engine C siêu nhẹ và siêu nhanh:

1. **Modest** (Default): Engine phân tích HTML bằng C.
2. **Lexbor**: Engine phân tích HTML5 hiện đại hơn, xử lý HTML lỗi/méo cực kỳ hiệu quả.

### So sánh nhanh các thư viện Parsing Python:

| Thư viện | Tốc độ | Engine bên dưới | Cú pháp chính | Độ phổ biến |
| --- | --- | --- | --- | --- |
| **`selectolax`** | 🚀 **Siêu nhanh** | C (Modest / Lexbor) | CSS Selector | Đang tăng nhanh |
| **`lxml`** | ⚡ Nhanh | C (libxml2) | XPath / CSS | Rất cao |
| **`BeautifulSoup4`** | 🐢 Chậm | Python pure / lxml | Custom API | Cực kỳ cao |

---

## 2. Cài đặt

Cài đặt cực kỳ đơn giản qua `pip`:

```bash
pip install selectolax

```

---

## 3. Khởi tạo Parser: Modest vs Lexbor

`selectolax` hỗ trợ 2 parser. Trong 90% trường hợp, bạn nên dùng **`LexborHTMLParser`** vì nó hỗ trợ chuẩn HTML5 tốt hơn và xử lý các thẻ đóng thiếu chính xác hơn.

```python
# Cách 1: Sử dụng Modest (Mặc định)
from selectolax.parser import HTMLParser

# Cách 2: Sử dụng Lexbor (Khuyên dùng)
from selectolax.lexbor import LexborHTMLParser

html_code = """
<html>
    <body>
        <h1 id="title">Chào mừng đến với Selectolax</h1>
        <div class="content">
            <p class="text">Bài viết 1</p>
            <p class="text highlight">Bài viết 2</p>
        </div>
    </body>
</html>
"""

# Khởi tạo tree
tree = LexborHTMLParser(html_code)

```

---

## 4. Tìm kiếm phần tử (Querying DOM)

`selectolax` tập trung vào **CSS Selectors** (không hỗ trợ XPath). Bạn có 2 phương thức cốt lõi:

* `css(query)`: Trả về một **danh sách** các `Node` khớp với điều kiện.
* `css_first(query, default=None)`: Trả về **Node đầu tiên** tìm thấy, hoặc giá trị `default` nếu không thấy.

```python
# 1. Tìm phần tử đầu tiên
title_node = tree.css_first("h1#title")
print(title_node.text())  # Thẻ h1: "Chào mừng đến với Selectolax"

# 2. Tìm tất cả các phần tử thỏa mãn
p_nodes = tree.css("p.text")
for p in p_nodes:
    print(p.text())

# 3. Sử dụng CSS Selector nâng cao
highlight_p = tree.css_first("div.content > p.highlight")

```

---

## 5. Bóc tách thông tin từ Node (Data Extraction)

Sau khi lấy được một `Node`, bạn có thể khai thác các thuộc tính sau:

### A. Lấy văn bản (`.text()`)

```python
node = tree.css_first("h1")

# Lấy text nguyên bản
raw_text = node.text()

# Lấy text đã loại bỏ khoảng trắng thừa ở 2 đầu (strip=True)
clean_text = node.text(strip=True)

```

### B. Lấy thuộc tính (`.attributes` / `.attrs`)

```python
html = '<a href="https://example.com" id="main-link" data-id="123">Link</a>'
node = LexborHTMLParser(html).css_first("a")

# Lấy tất cả thuộc tính dạng dictionary
print(node.attributes)
# Output: {'href': 'https://example.com', 'id': 'main-link', 'data-id': '123'}

# Lấy giá trị của 1 thuộc tính cụ thể
link_url = node.attributes.get("href")
data_id = node.attrs.get("data-id")  # .attrs là viết tắt của .attributes

```

### C. Duyệt cây DOM (Navigation)

```python
node = tree.css_first("p.highlight")

parent_node = node.parent  # Thẻ cha (div.content)
next_sibling = node.next  # Phần tử kế tiếp
prev_sibling = node.prev  # Phần tử phía trước
child_nodes = parent_node.children  # Danh sách con

```

---

## 6. Chỉnh sửa & Làm sạch DOM (DOM Manipulation)

Một tính năng cực mạnh của `selectolax` là xóa bỏ các thẻ không cần thiết (như quảng cáo, `<script>`, `<style>`) trước khi trích xuất văn bản.

### A. Xóa node (`.decompose()`)

```python
html = """
<article>
    <h1>Tiêu đề bài viết</h1>
    <script>console.log("Xóa tôi đi!");</script>
    <p>Nội dung chính của bài viết...</p>
</article>
"""

tree = LexborHTMLParser(html)

# Xóa tất cả các thẻ <script> và <style>
for tag in tree.css("script, style"):
    tag.decompose()

# Bây giờ lấy text toàn bộ bài viết sẽ sạch sẽ hoàn toàn
print(tree.css_first("article").text(strip=True))
# Output: "Tiêu đề bài viếtNội dung chính của bài viết..."

```

### B. Thay thế phần tử (`.replace_with()`)

```python
node = tree.css_first("h1")
node.replace_with("<h2>Tiêu đề mới</h2>")

```

---

## 7. Ví dụ thực chiến: Cào danh sách sản phẩm

Dưới đây là đoạn mã thực tế phân tích một danh sách sản phẩm e-commerce:

```python
from selectolax.lexbor import LexborHTMLParser

html_data = """
<div class="product-grid">
    <div class="product-card" data-sku="SKU-001">
        <h2 class="title"><a href="/item/1">Bàn phím cơ AKKO</a></h2>
        <span class="price">1.250.000đ</span>
        <span class="stock out-of-stock">Hết hàng</span>
    </div>
    <div class="product-card" data-sku="SKU-002">
        <h2 class="title"><a href="/item/2">Chuột Logitech MX Master 3S</a></h2>
        <span class="price">2.490.000đ</span>
        <span class="stock in-stock">Còn hàng</span>
    </div>
</div>
"""

tree = LexborHTMLParser(html_data)
products = []

for card in tree.css("div.product-card"):
    sku = card.attributes.get("data-sku")

    # Lấy link và title
    title_node = card.css_first("h2.title a")
    title = title_node.text(strip=True) if title_node else None
    url = title_node.attributes.get("href") if title_node else None

    # Lấy giá
    price_node = card.css_first("span.price")
    price = price_node.text(strip=True) if price_node else None

    # Kiểm tra trạng thái hàng
    is_in_stock = card.css_first("span.in-stock") is not None

    products.append(
        {
            "sku": sku,
            "title": title,
            "url": url,
            "price": price,
            "in_stock": is_in_stock,
        }
    )

import pprint

pprint.pprint(products)

```

---

## 8. Tóm tắt các bí kíp làm việc với Selectolax

1. **Luôn ưu tiên `LexborHTMLParser**`: `from selectolax.lexbor import LexborHTMLParser`.
2. **Kiểm tra `None` khi dùng `css_first**`: Nếu CSS Selector không khớp, `css_first()` trả về `None`. Truy cập `.text()` trực tiếp trên `None` sẽ gây ra `AttributeError`.
3. **Dùng `.strip_tags()**`: Nếu muốn xóa các tag HTML nội hàm giữ lại text đơn thuần.
4. **Kết hợp `httpx` hoặc `requests**`:
```python
import httpx
from selectolax.lexbor import LexborHTMLParser

resp = httpx.get("https://example.com")
tree = LexborHTMLParser(resp.text)

```



```

<ElicitationsGroup message="Bạn muốn đi sâu hơn vào phần nào tiếp theo?">
  <Elicitation label="Xây dựng Crawler bất đồng bộ kết hợp HTTPX và Selectolax" query="Hãy hướng dẫn tôi viết một script cào dữ liệu bất đồng bộ (asyncio) sử dụng httpx và selectolax để đạt tốc độ tối đa."/>
  <Elicitation label="So sánh benchmark chi tiết Tốc độ & Bộ nhớ với BeautifulSoup" query="Hãy viết một đoạn script benchmark so sánh tốc độ thực tế giữa BeautifulSoup4, lxml và selectolax trên cùng một tệp HTML lớn."/>
</ElicitationsGroup>

```