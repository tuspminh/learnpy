Dưới đây là một script Python hoàn chỉnh, chuẩn sản xuất (production-ready) kết hợp giữa `httpx` (để gửi yêu cầu HTTP) và `selectolax` (để phân tích & làm sạch DOM).

Script này giải quyết trọn vẹn 4 bài toán lớn khi cào báo chí:

1. **Trích xuất Metadata chuẩn xác**: Dùng Meta tags (`og:title`, `article:published_time`) làm fallback nếu thẻ HTML bị đổi class.
2. **Dọn rác DOM chuyên sâu**: Xóa sạch quảng cáo, iframe, script, các box bài viết liên quan...
3. **Định vị vùng nội dung linh hoạt**: Tự động thử nhiều CSS Selector phổ biến trên các trang báo Việt Nam (VnExpress, Dân Trí, Tuổi Trẻ, Thanh Niên...).
4. **Chuyển đổi sang Markdown**: Chuyển đổi các đoạn văn, tiêu đề, hình ảnh (bao gồm ảnh Lazy-load) và trích dẫn thành định dạng Markdown sạch đẹp.

---

### Cài đặt thư viện cần thiết

```bash
pip install selectolax httpx

```

---

### Python Script: `news_scraper.py`

```python
import json
import re
from typing import Any, Dict, Optional
import httpx
from selectolax.lexbor import LexborHTMLParser, Node

# ----------------------------------------------------------------------
# 1. CẤU HÌNH CÁC PHÂN TỬ RÁC VÀ PHÂN TỬ NỘI DUNG CHÍNH
# ----------------------------------------------------------------------

# Danh sách CSS Selector của các phần tử rác cần XÓA BỎ
GARBAGE_SELECTORS = [
    "script",
    "style",
    "iframe",
    "noscript",
    "svg",
    "header",
    "footer",
    "nav",
    "aside",
    # Class/ID quảng cáo và bài liên quan thường gặp
    ".ads",
    ".advertisement",
    ".banner",
    ".social-share",
    ".related-news",
    ".box-quantam",
    ".relate-news",
    ".author-info",
    ".comment",
    '[class*="ad-"]',
    '[class*="banner"]',
]

# Danh sách CSS Selector định vị vùng nội dung bài viết (Thử lần lượt từ trên xuống)
CONTENT_SELECTORS = [
    "article",
    "div.fck_detail",  # VnExpress
    "div.detail-content",  # Tuổi Trẻ, Thanh Niên
    "div.content-detail",  # Dân Trí
    "div.detail__content",  # VietnamNet
    "div.singular-content",
    "div.main-content",
]


# ----------------------------------------------------------------------
# 2. CÁC HÀM XỬ LÝ CHÍNH
# ----------------------------------------------------------------------


def clean_dom(tree: LexborHTMLParser) -> None:
    """Xóa bỏ hoàn toàn các thẻ rác khỏi cây DOM"""
    for selector in GARBAGE_SELECTORS:
        for node in tree.css(selector):
            node.decompose()


def extract_metadata(tree: LexborHTMLParser) -> Dict[str, Optional[str]]:
    """Trích xuất Tiêu đề và Ngày đăng từ Meta tag hoặc thẻ HTML fallback"""
    # 1. Trích xuất Tiêu đề
    title = None
    title_meta = (
        tree.css_first('meta[property="og:title"]')
        or tree.css_first('meta[name="twitter:title"]')
        or tree.css_first("h1")
        or tree.css_first("title")
    )
    if title_meta:
        title = title_meta.attributes.get("content") or title_meta.text(
            strip=True
        )

    # 2. Trích xuất Ngày đăng
    date = None
    date_meta = (
        tree.css_first('meta[property="article:published_time"]')
        or tree.css_first('meta[name="pubdate"]')
        or tree.css_first('meta[name="postdate"]')
        or tree.css_first("time")
    )
    if date_meta:
        date = (
            date_meta.attributes.get("content")
            or date_meta.attributes.get("datetime")
            or date_meta.text(strip=True)
        )

    return {"title": title, "published_date": date}


def get_image_url(img_node: Node) -> Optional[str]:
    """Bóc tách URL ảnh, tự động xử lý các loại Lazy-load"""
    lazy_attrs = ["data-src", "data-original", "data-lazy-src", "src"]
    for attr in lazy_attrs:
        url = img_node.attributes.get(attr)
        if url and not url.startswith("data:image/"):
            return url.strip()
    return None


def convert_node_to_markdown(content_node: Node) -> str:
    """Duyệt qua các thẻ khối trong nội dung và chuyển thành định dạng Markdown"""
    md_lines = []

    # Tìm tất cả các thẻ khối theo đúng thứ tự xuất hiện trong bài
    blocks = content_node.css("p, h1, h2, h3, h4, h5, h6, img, blockquote, ul, ol")

    for node in blocks:
        tag = node.tag

        # Thẻ tiêu đề nội dung
        if tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            level = int(tag[1])
            text = node.text(strip=True)
            if text:
                md_lines.append(f"\n\n{'#' * level} {text}\n")

        # Thẻ đoạn văn
        elif tag == "p":
            text = node.text(strip=True)
            if text:
                md_lines.append(f"\n\n{text}\n")

        # Thẻ trích dẫn
        elif tag == "blockquote":
            text = node.text(strip=True)
            if text:
                md_lines.append(f"\n\n> {text}\n")

        # Thẻ hình ảnh
        elif tag == "img":
            src = get_image_url(node)
            alt = node.attributes.get("alt", "Hình ảnh").strip()
            if src:
                md_lines.append(f"\n\n![{alt}]({src})\n")

        # Danh sách (Unordered / Ordered)
        elif tag in ["ul", "ol"]:
            for li in node.css("li"):
                li_text = li.text(strip=True)
                if li_text:
                    md_lines.append(f"\n* {li_text}")

    # Ghép chuỗi và làm sạch khoảng trắng thừa (\n\n\n -> \n\n)
    raw_md = "".join(md_lines)
    clean_md = re.sub(r"\n{3,}", "\n\n", raw_md).strip()
    return clean_md


def scrape_news_article(url: str) -> Dict[str, Any]:
    """Hàm chính: Tải trang, làm sạch và trích xuất dữ liệu bài viết"""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    # 1. Gửi HTTP Request lấy HTML
    with httpx.Client(timeout=10.0, follow_redirects=True) as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()

    # 2. Khởi tạo Parser bằng Lexbor
    tree = LexborHTMLParser(response.text)

    # 3. Trích xuất Metadata trước khi xóa DOM
    metadata = extract_metadata(tree)

    # 4. Làm sạch DOM (Xóa rác)
    clean_dom(tree)

    # 5. Định vị khung nội dung chính của bài viết
    content_node = None
    for selector in CONTENT_SELECTORS:
        content_node = tree.css_first(selector)
        if content_node:
            break

    # Fallback nếu không tìm thấy container khớp selector: Dùng <body>
    if not content_node:
        content_node = tree.body or tree.root

    # 6. Chuyển đổi nội dung sang Markdown
    markdown_text = convert_node_to_markdown(content_node)

    return {
        "url": url,
        "title": metadata["title"],
        "published_date": metadata["published_date"],
        "content_markdown": markdown_text,
    }


# ----------------------------------------------------------------------
# 3. CHẠY THỬ NGHIỆM (DEMO)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Thay đổi URL bài báo bạn muốn test tại đây
    test_url = "https://vnexpress.net/gia-vang-sjc-tang-vuot-80-trieu-dong-4718000.html"

    print(f"🔄 Đang cào dữ liệu từ: {test_url}...\n")

    try:
        result = scrape_news_article(test_url)

        print("=" * 60)
        print(f"📌 TIÊU ĐỀ    : {result['title']}")
        print(f"📅 NGÀY ĐĂNG  : {result['published_date']}")
        print("=" * 60)
        print("📝 NỘI DUNG (MARKDOWN):\n")
        print(result["content_markdown"][:1000] + "\n\n...[Đã cắt bớt]...")
        print("=" * 60)

        # Xuất ra file JSON nếu cần
        # with open("article.json", "w", encoding="utf-8") as f:
        #     json.dump(result, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"❌ Có lỗi xảy ra: {e}")

```

---

### Điểm nổi bật của Script này:

1. **Dùng `LexborHTMLParser**`: Đảm bảo tốc độ parse cao nhất và xử lý lỗi HTML cực tốt.
2. **Không làm rách Markdown**: Bằng cách quét danh sách các thẻ khối theo thứ tự xuất hiện (`content_node.css('p, h1, h2...')`), bài viết giữ nguyên thứ tự dòng, ảnh và trích dẫn.
3. **Cơ chế chống rò rỉ dữ liệu rác**: Hàm `clean_dom()` dọn dẹp triệt để `script`, `style`, `iframe`, giúp nội dung xuất ra không bị dính mã code hay quảng cáo chèn giữa bài.