Khi cào dữ liệu web, `html2text` sẽ chuyển đổi **toàn bộ** HTML nó nhận được — bao gồm cả thanh điều hướng (navbar), chân trang (footer), quảng cáo và các đoạn mã Javascript.

Việc kết hợp **BeautifulSoup** đóng vai trò như một "màng lọc", giúp bạn loại bỏ rác và chỉ trích xuất vùng nội dung chính trước khi đưa sang `html2text`.

---

1. **Trích xuất HTML bằng BeautifulSoup:** Parse cấu trúc trang web thành DOM tree.
Sử dụng BeautifulSoup để đọc và phân tích cú pháp HTML của trang web.


2. **Xóa các thẻ rác hệ thống:** Sử dụng phương thức .decompose().
Loại bỏ hoàn toàn các thẻ không chứa văn bản hữu ích như `<script>`, `<style>`, `<nav>`, `<footer>`, `<header>`, `<aside>`.


3. **Khoanh vùng nội dung chính:** Tìm thẻ chứa bài viết.
Sử dụng `soup.find()` hoặc `soup.select()` để chỉ giữ lại vùng chứa bài viết chính (thường nằm trong thẻ `<article>`, `<main>` hoặc một `<div class="content">`).


4. **Chuyển đổi sang Markdown:** Đưa chuỗi HTML sạch vào html2text.
Ép kiểu phần HTML đã lọc thành chuỗi (`str`) và đưa qua `html2text.handle()`.


---

## Code minh họa hoàn chỉnh

```python
from bs4 import BeautifulSoup
import html2text

# 1. HTML giả lập (chứa nhiều rác như menu, quảng cáo, footer)
raw_html = """
<html>
  <head><title>Trang tin tức</title></head>
  <body>
    <header><h1>Website Logo & Navigation</h1></header>
    <nav>
      <ul><li><a href="#">Trang chủ</a></li><li><a href="#">Liên hệ</a></li></ul>
    </nav>
    
    <!-- Vùng bài viết chính -->
    <article class="post-body">
      <h2>Cách nấu phở bò truyền thống</h2>
      <p>Phở bò là món ăn đặc trưng của Việt Nam...</p>
      <div class="ad-banner">Mua nồi áp suất giảm giá 50%!</div>
      <p>Nước dùng cần ninh từ xương ống trong 8 tiếng.</p>
      <script>console.log("Mã theo dõi người dùng");</script>
    </article>

    <aside class="sidebar">Bài viết liên quan...</aside>
    <footer>Copyright 2026 - All rights reserved</footer>
  </body>
</html>
"""

# 2. Khởi tạo BeautifulSoup
soup = BeautifulSoup(raw_html, "html.parser")

# --- BƯỚC LỌC 1: Xóa toàn bộ các thẻ rác định sẵn ---
unwanted_tags = ["script", "style", "nav", "footer", "header", "aside"]
for tag in soup(unwanted_tags):
    tag.decompose()  # decompose() sẽ xóa hẳn thẻ đó khỏi DOM tree

# --- BƯỚC LỌC 2: Xóa bớt khung quảng cáo/bình luận theo Class/ID ---
for ad in soup.find_all("div", class_="ad-banner"):
    ad.decompose()

# --- BƯỚC LỌC 3: Chọn đúng vùng bài viết chính ---
main_article = soup.find("article", class_="post-body")

# Chuyển đối tượng BeautifulSoup thành chuỗi HTML sạch
clean_html = str(main_article) if main_article else str(soup.body)

# 3. Tiến hành chuyển sang Markdown bằng html2text
h = html2text.HTML2Text()
h.body_width = 0  # Không tự ngắt dòng

markdown_result = h.handle(clean_html)

print("--- KẾT QUẢ MARKDOWN SAU KHU LỌC RÁC ---")
print(markdown_result)

```

---

## Mẹo lọc rác hiệu quả khi Cào Web (Web Scraping)

* **Ưu tiên `.decompose()` hơn `.extract()**`: `.decompose()` xóa sạch thẻ và giải phóng bộ nhớ, trong khi `.extract()` chỉ tách thẻ ra nhưng vẫn giữ trong RAM.
* **Xác định Main Content**: Hầu hết các trang báo/blog hiện đại đều đặt bài viết trong thẻ `<article>`, `<main>` hoặc `<div class="entry-content">`. Luôn dùng `soup.find()` tới các khung này trước.
* **Xóa class rác bằng Regex**: Bạn có thể xóa tất cả `div` chứa chữ "ad", "banner", "social" bằng Regex:
```python
import re
for ad in soup.find_all(class_=re.compile(r'(ad|banner|social|comment)', re.I)):
    ad.decompose()

```