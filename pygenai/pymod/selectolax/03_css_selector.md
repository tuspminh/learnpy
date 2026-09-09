Vì `selectolax` dựa trên engine **Lexbor / Modest** viết bằng C, nó hỗ trợ rất tốt **CSS3 Selectors**. Tuy nhiên, do `selectolax` **không hỗ trợ XPath** và không có sẵn các pseudo-class phi chuẩn như `:contains()`, việc nắm vững các cú pháp CSS nâng cao kết hợp với kỹ thuật xử lý trong Python sẽ giúp bạn cào dữ liệu từ những trang web khó nhất.

---

## 1. Bảng tra cứu CSS Selector từ nâng cao đến chuyên sâu

### A. Attribute Selectors (Khớp thuộc tính linh hoạt)

Rất hữu ích khi các trang web dùng class ngẫu nhiên (React/Next.js, Tailwind, CSS Modules) hoặc muốn lọc thẻ theo URL/Data attribute.

| Cú pháp | Ý nghĩa | Ví dụ thực tế |
| --- | --- | --- |
| `[attr]` | Có chứa thuộc tính `attr` | `[data-sku]` (Lấy các thẻ có chứa attribute data-sku) |
| `[attr="val"]` | Khớp chính xác 100% | `[type="submit"]` |
| `[attr*="val"]` | Giá trị chứa chuỗi `val` (**Phổ biến nhất**) | `[class*="price-"]` (Khớp `price-old`, `main-price-val`) |
| `[attr^="val"]` | Giá trị **bắt đầu** bằng `val` | `a[href^="https://"]` (Chỉ lấy link tuyệt đối) |
| `[attr$="val"]` | Giá trị **kết thúc** bằng `val` | `a[href$=".pdf"]` (Chỉ lấy link tải file PDF) |
| `[attr~="val"]` | Chứa từ `val` trong danh sách cách nhau bởi khoảng trắng | `[class~="active"]` (Tương đương `.active`) |
| `[attr|="val"]` | Bắt đầu bằng `val` hoặc `val-` | `[lang|="en"]` (Khớp `en`, `en-US`, `en-GB`) |

---

### B. Combinators & Structural Pseudo-classes (Định vị vị trí & Cấu trúc)

| Cú pháp | Ý nghĩa | Ví dụ |
| --- | --- | --- |
| `A > B` | B là con trực tiếp của A | `ul.menu > li` |
| `A + B` | B là phần tử **kế tiếp ngay sau** A (Cùng cấp) | `h2 + p` (Lấy đoạn văn ngay dưới tiêu đề H2) |
| `A ~ B` | B là phần tử **bất kỳ phía sau** A (Cùng cấp) | `h2 ~ div.comment` (Lấy các div comment đứng sau H2) |
| `:first-child` / `:last-child` | Phần tử đầu tiên / cuối cùng | `li:first-child` |
| `:nth-child(n)` | Phần tử thứ `n` (bắt đầu từ 1) | `tr:nth-child(2)` (Lấy dòng thứ 2 của bảng) |
| `:nth-child(odd)` / `(even)` | Dòng lẻ / Dòng chẵn | `tr:nth-child(even)` |
| `:nth-of-type(n)` | Phần tử thứ `n` **cùng kiểu thẻ** | `article > p:nth-of-type(1)` |
| `:not(selector)` | Loại trừ phần tử thỏa mãn selector | `div.card:not(.promoted)` (Lấy thẻ card trừ thẻ quảng cáo) |
| `:empty` | Phần tử rỗng (không có con lẫn text) | `div:empty` |

---

## 2. Các mẹo xử lý "Ca khó" trong Selectolax

### Mẹo 1: Tìm phần tử theo NỘI DUNG TEXT (Thay thế `:contains()`)

`selectolax` không hỗ trợ `:contains("text")` của XPath/jQuery. Cách tối ưu nhất là dùng CSS Selector gom vùng hẹp rồi lọc bằng Python List Comprehension:

```python
from selectolax.lexbor import LexborHTMLParser

html = """
<button class="btn">Thêm vào giỏ</button>
<button class="btn primary">Mua ngay</button>
<button class="btn">Hủy bỏ</button>
"""
tree = LexborHTMLParser(html)

# Lấy tất cả button, sau đó lọc theo text bằng Python
buy_buttons = [
    btn
    for btn in tree.css("button.btn")
    if "Mua ngay" in btn.text(strip=True)
]

target_btn = buy_buttons[0] if buy_buttons else None
print(target_btn.attributes)  # {'class': 'btn primary'}

```

---

### Mẹo 2: Xử lý Class bị mã hóa / Dynamic Class (Styled-Components, React, Tailwind)

Các trang như Shopee, Tiki, Facebook thường sinh class ngẫu nhiên dạng `ProductTitle__sc-1a2b3-0` hoặc class dài ngoằn của Tailwind.

* **Cách giải quyết:** Kết hợp nhiều Attribute Matcher hoặc bám vào các thuộc tính cố định khác (`data-*`, `aria-*`, `name`, `type`).

```python
# Giả sử HTML: <h1 class="Title_sc-1x89a-0 dynamic-a12">Sản phẩm A</h1>

# Cách 1: Tìm theo phần chuỗi cố định của class
title = tree.css_first('[class*="Title_sc-"]')

# Cách 2: Kết hợp thuộc tính role hoặc aria (rất phổ biến trên giao diện React/Vue)
button = tree.css_first('button[aria-label="Đóng"], [role="button"]')

# Cách 3: Kết hợp tìm theo thẻ cha cố định + thẻ con
price = tree.css_first("div#product-detail-wrapper [class*='price']")

```

---

### Mẹo 3: Kỹ thuật "Thợ săn mỏ neo" (Anchor & Traverse)

Khi phần tử cần lấy không có Class hay ID riêng biệt, hãy **tìm một phần tử mốc (Anchor)** gần nó nhất (ví dụ: nhãn "Giá bán:", "Tình trạng:"), sau đó di chuyển qua cây DOM.

```python
html = """
<div class="specs">
    <span class="label">Mã sản phẩm:</span>
    <span class="value">SKU-9988</span>
    
    <span class="label">Giá bán:</span>
    <span class="value highlight">1.500.000đ</span>
</div>
"""
tree = LexborHTMLParser(html)

# Mục tiêu: Lấy giá bán dựa vào nhãn "Giá bán:"
# Step 1: Tìm thẻ span.label chứa chữ "Giá bán:"
price_label = next(
    (
        node
        for node in tree.css("span.label")
        if "Giá bán" in node.text(strip=True)
    ),
    None,
)

# Step 2: Dùng .next để lấy thẻ span.value đứng ngay sau nó
if price_label:
    price_val_node = price_label.next
    print("Giá tìm được:", price_val_node.text(strip=True))  # 1.500.000đ

```

---

### Mẹo 4: Làm sạch tài liệu trước khi Parse (Dọn rác DOM)

Đôi khi text thu được bị dính các đoạn Script, Style hoặc Quảng cáo ẩn. Hãy dùng `.decompose()` để xóa sạch chúng trước khi lấy dữ liệu:

```python
tree = LexborHTMLParser(html)

# Xóa toàn bộ script, style, iframe và các thẻ ẩn
for garbage in tree.css(
    'script, style, iframe, .ads, [style*="display: none"]'
):
    garbage.decompose()

# Bây giờ bóc tách dữ liệu mà không sợ dính text rác
clean_text = tree.body.text(separator="\n", strip=True)

```

---

### Mẹo 5: Gom nhiều Selector trong một lượt truy vấn

Bạn có thể kết hợp nhiều điều kiện CSS phân cách bằng dấu phẩy `,` (phép OR trong CSS) để tìm nhiều loại thẻ cùng lúc:

```python
# Lấy tất cả các tiêu đề từ H1 đến H3 và các đoạn văn quan trọng
headings_and_intro = tree.css("h1, h2, h3, p.intro")

# Lấy tất cả ảnh có thuộc tính data-src (lazyload) HOẶC src thông thường
images = tree.css("img[data-src], img[src]")

for img in images:
    # Lấy data-src trước, nếu không có thì lấy src
    src = img.attrs.get("data-src") or img.attrs.get("src")
    print(src)

```