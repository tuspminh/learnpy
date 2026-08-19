Nếu bạn đã từng cào dữ liệu ở quy mô lớn (hàng chục ngàn trang HTML), bạn sẽ nhận ra **BeautifulSoup4 (BS4)** chính là "nút thắt cổ chai" (bottleneck) về hiệu năng CPU. BS4 rất linh hoạt nhưng lại tạo ra cây DOM khá nặng trong bộ nhớ Python.

**`selectolax`** là thư viện bóc tách HTML siêu tốc nhờ viết bằng C (sử dụng engine **Modest** hoặc **Lexbor**). Khi kết hợp tốc độ tải mạng của **`httpx`** với tốc độ parse C-based của **`selectolax`**, bạn sẽ có một pipeline cào web đạt tốc độ tối đa của phần cứng.

---

## 🚀 So sánh hiệu năng nhanh

| Tiêu chí | BeautifulSoup4 (`lxml`) | `selectolax` |
| --- | --- | --- |
| **Engine bên dưới** | Python wrapper over C | Pure C engine (Modest/Lexbor) |
| **Tốc độ Parse** | Trung bình (~50-100 ms/trang) | **Siêu nhanh (~2-5 ms/trang - Nhanh gấp 10-20x)** |
| **Tiêu tốn RAM** | Cao (Tạo nhiều Python objects) | **Rất thấp (Bộ nhớ C tối ưu)** |
| **Cú pháp** | CSS Selector / Find | CSS Selector (Cú pháp tương tự) |

---

## 1. Cài đặt

```bash
pip install httpx selectolax

```

---

## 2. Bảng quy đổi cú pháp (BS4 vs Selectolax)

Cú pháp của `selectolax` rất gần gũi nếu bạn đã quen dùng CSS Selectors trong BeautifulSoup:

```python
# --- BEAUTIFULSOUP4 ---
from bs4 import BeautifulSoup
soup = BeautifulSoup(html_text, "html.parser")

elem = soup.select_one(".title")         # Lấy 1 phần tử
text = elem.get_text(strip=True)         # Lấy text
link = elem.get("href")                  # Lấy attribute

# --- SELECTOLAX ---
from selectolax.parser import HTMLParser
tree = HTMLParser(html_text)

elem = tree.css_first(".title")          # Lấy 1 phần tử
text = elem.text(strip=True)             # Lấy text
link = elem.attributes.get("href")       # Lấy attribute

```

---

## 3. Script Scraper Hoàn chỉnh (`httpx` + `selectolax`)

Dưới đây là đoạn mã Async Scraper tốc độ cao kết hợp `httpx` và `selectolax`:

```python
import asyncio
import json
import logging
import time
import httpx
from selectolax.parser import HTMLParser

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

BASE_URL = "https://quotes.toscrape.com/page/{page_num}/"
TOTAL_PAGES = 10
MAX_CONCURRENT = 5

async def parse_page(client: httpx.AsyncClient, semaphore: asyncio.Semaphore, page_num: int):
    url = BASE_URL.format(page_num=page_num)
    
    async with semaphore:
        try:
            response = await client.get(url)
            response.raise_for_status()

            # -------------------------------------------------------------
            # ⚡ SELECTOLAX PARSING (Nhanh gấp 10 lần BeautifulSoup)
            # -------------------------------------------------------------
            start_parse = time.perf_counter()
            tree = HTMLParser(response.text)
            
            quotes_in_page = []

            # .css() trả về một danh sách các Node
            for node in tree.css(".quote"):
                # .css_first() lấy phần tử đầu tiên khớp với CSS selector
                text_node = node.css_first(".text")
                author_node = node.css_first(".author")
                
                # Lấy danh sách các thẻ tag
                tag_nodes = node.css(".tag")

                quotes_in_page.append({
                    "page": page_num,
                    "quote": text_node.text(strip=True) if text_node else "",
                    "author": author_node.text(strip=True) if author_node else "",
                    "tags": [t.text(strip=True) for t in tag_nodes]
                })

            parse_time = (time.perf_counter() - start_parse) * 1000
            logging.info(f"✅ Trang {page_num}: Parse xong {len(quotes_in_page)} items trong {parse_time:.2f} ms")
            return quotes_in_page

        except Exception as e:
            logging.error(f"❌ Lỗi trang {page_num}: {e}")
            return []

async def main():
    start_total = time.perf_counter()
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = [parse_page(client, semaphore, page) for page in range(1, TOTAL_PAGES + 1)]
        results = await asyncio.gather(*tasks)

    # Flatten danh sách
    all_quotes = [item for page_data in results for item in page_data]

    total_time = time.perf_counter() - start_total
    logging.info(f"🎉 Tổng cộng: {len(all_quotes)} trích dẫn | Thời gian chạy: {total_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())

```

---

## 4. Cheat Sheet thao tác Node thường dùng trong `selectolax`

### A. Lấy thuộc tính (Attributes)

```python
node = tree.css_first("a.login-btn")

# Lấy trực tiếp từ dict .attributes
link = node.attributes.get("href", "#")
class_name = node.attributes.get("class")

```

### B. Duyệt qua danh sách các Node

```python
# .css() trả về Generator/List các Node
for product in tree.css("div.product-card"):
    title = product.css_first("h2.title").text(strip=True)
    price = product.css_first("span.price").text(strip=True)

```

### C. Lấy HTML thô (Outer/Inner HTML)

```python
node = tree.css_first("div.container")

outer_html = node.html             # Bao gồm cả thẻ div.container
inner_html = node.child.html if node.child else "" # Chỉ chứa nội dung bên trong

```

### D. Bỏ qua bớt các thẻ không cần thiết (Unwrap / Strip)

Ví dụ bạn muốn lấy toàn bộ text trong bài viết nhưng muốn xóa các thẻ `<script>`, `<style>` hay `<iframe>` quảng cáo trước:

```python
# Xóa toàn bộ thẻ script và style khỏi cây DOM
for tag in tree.css("script, style, iframe"):
    tag.decompose()

# Bây giờ lấy text bài viết sẽ rất sạch
clean_text = tree.css_first("article").text(strip=True)

```

---

## 💡 Khi nào nên dùng gì?

* **Dùng BeautifulSoup4 khi:** Cần cào dữ liệu nhỏ, script đơn giản, hoặc cần tính năng tìm kiếm linh hoạt theo Regex / Function phức tạp của BS4.
* **Dùng `selectolax` khi:** Cào **dữ liệu lớn (Big Data/Massive Scraping)**, cần tối ưu CPU/RAM, chạy async với hàng nghìn request/phút.