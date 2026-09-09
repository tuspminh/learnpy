Trích xuất **JSON-LD (Structured Data)** và **Hình ảnh Lazy-load** là hai kỹ thuật kinh điển giúp bạn lấy dữ liệu siêu nhanh và chính xác.

Nhiều website hiện đại chứa sẵn cấu trúc dữ liệu JSON đầy đủ bên trong các thẻ `<script>`, giúp bạn cào dữ liệu mà không cần parse qua hàng trăm thẻ HTML lẻ tẻ.

---

## 1. Trích xuất dữ liệu Structured Data từ thẻ `<script type="application/ld+json">`

Website bán hàng, báo chí, bất động sản thường nhúng JSON-LD chứa sẵn thông tin giá, tên sản phẩm, đánh giá, tác giả...

### Cách thực hiện:

1. Dùng CSS Selector `script[type="application/ld+json"]` để tìm tất cả các thẻ JSON-LD.
2. Lấy chuỗi JSON bằng `.text()`.
3. Dùng thư viện `json` của Python để `loads()` thành **Dictionary/List** để khai thác.

```python
import json
from selectolax.lexbor import LexborHTMLParser

html_demo = """
<html>
<head>
    <script type="application/ld+json">
    {
      "@context": "https://schema.org/",
      "@type": "Product",
      "name": "Bàn phím cơ AKKO 3068B",
      "image": "https://example.com/keyboard.jpg",
      "description": "Bàn phím cơ không dây Bluetooth / 2.4Ghz",
      "offers": {
        "@type": "Offer",
        "priceCurrency": "VND",
        "price": "1690000",
        "availability": "https://schema.org/InStock"
      }
    }
    </script>
</head>
<body>
    <h1>Trang chi tiết sản phẩm</h1>
</body>
</html>
"""

tree = LexborHTMLParser(html_demo)

# 1. Tìm tất cả các thẻ script có type="application/ld+json"
script_nodes = tree.css('script[type="application/ld+json"]')

for node in script_nodes:
    raw_json = node.text(strip=True)
    if not raw_json:
        continue

    try:
        # 2. Parse chuỗi text thành Python Dictionary
        data = json.loads(raw_json)

        # 3. Lấy dữ liệu cực kỳ đơn giản qua dict key
        if data.get("@type") == "Product":
            print(f"Tên sản phẩm: {data.get('name')}")
            print(f"Mô tả: {data.get('description')}")

            offers = data.get("offers", {})
            print(f"Giá bán: {offers.get('price')} {offers.get('priceCurrency')}")
            print(f"Ảnh: {data.get('image')}")

    except json.JSONDecodeError:
        # Xử lý trường hợp chuỗi JSON bị lỗi syntax
        continue

```

> 💡 **Mẹo nâng cao:**
> Đôi khi một trang web có nhiều thẻ `ld+json` hoặc một thẻ chứa một **Danh sách JSON** `[{...}, {...}]`. Hãy luôn kiểm tra kiểu dữ liệu `isinstance(data, list)` hoặc `isinstance(data, dict)` trước khi truy cập key!

---

## 2. Trích xuất ảnh Lazy-load (Hình ảnh tải chậm)

Các trang web hiện đại dùng kỹ thuật **Lazy-loading** để tối ưu tốc độ trang. Thuộc tính `src` ban đầu của thẻ `<img>` thường chỉ chứa một file ảnh 1x1 rỗng hoặc loader gif (ví dụ: `placeholder.jpg`). Link ảnh thực sự sẽ được giấu trong các attribute khác.

### Các thuộc tính Lazy-load phổ biến trên Web:

* `data-src`
* `data-original`
* `data-lazy-src`
* `srcset` (Chứa danh sách ảnh theo độ phân giải)

### Kỹ thuật xử lý Fallback (Lấy ưu tiên) bằng Selectolax:

Dưới đây là hàm chuyên dụng giúp bạn cào ảnh bất chấp trang web dùng kiểu Lazy-load nào:

```python
from selectolax.lexbor import LexborHTMLParser


def extract_image_url(img_node) -> str | None:
    """Hàm bổ trợ lấy URL ảnh thực sự từ một Node thẻ img

    Thứ tự ưu tiên: data-original > data-src > data-lazy-src > src
    """
    # 1. Danh sách các thuộc tính lazy-load phổ biến nhất
    lazy_attrs = [
        "data-original",
        "data-src",
        "data-lazy-src",
        "data-actualsrc",
        "src",
    ]

    for attr in lazy_attrs:
        url = img_node.attributes.get(attr)
        # Bỏ qua nếu thuộc tính không tồn tại hoặc chỉ là ảnh placeholder rỗng
        if url and not url.startswith("data:image/") and "placeholder" not in url:
            return url.strip()

    # 2. Nếu không thấy trong attribute đơn, kiểm tra srcset (VD: "img-100w.jpg 100w, img-800w.jpg 800w")
    srcset = img_node.attributes.get("srcset")
    if srcset:
        # Lấy link ảnh đầu tiên trong danh sách srcset
        first_src = srcset.split(",")[0].strip().split(" ")[0]
        return first_src

    return None


# Demo HTML giả lập Lazy-load
html_images = """
<div class="gallery">
    <!-- Ảnh 1: Dùng data-src -->
    <img class="lazy" src="blank.gif" data-src="https://example.com/photo1-full.jpg" alt="Ảnh 1">
    
    <!-- Ảnh 2: Dùng data-original -->
    <img class="lazy" src="loading.png" data-original="https://example.com/photo2-full.jpg" alt="Ảnh 2">
    
    <!-- Ảnh 3: Dùng srcset -->
    <img class="responsive" srcset="https://example.com/photo3-large.jpg 1000w, https://example.com/photo3-small.jpg 500w">
    
    <!-- Ảnh 4: Ảnh thường không lazyload -->
    <img src="https://example.com/photo4.jpg" alt="Ảnh 4">
</div>
"""

tree = LexborHTMLParser(html_images)

# Lấy tất cả các thẻ img
for img in tree.css("img"):
    real_url = extract_image_url(img)
    alt_text = img.attributes.get("alt", "Không có Alt")
    print(f"[{alt_text}] -> {real_url}")

```

---

## 3. Tổng kết quy trình cào dữ liệu tối ưu

Khi bắt đầu bóc tách một trang web bằng `selectolax`, hãy ưu tiên kiểm tra theo thứ tự:

```
1. Thẻ <script type="application/ld+json"> (Nhanh nhất, dữ liệu chuẩn cấu trúc)
   └── 2. Tìm các thẻ <script> chứa biến Javascript dạng `window.__INITIAL_STATE__ = {...}`
       └── 3. Bóc tách HTML bằng CSS Selector + Xử lý Lazy-load (Xử lý ảnh & text lẻ)

```