Dưới đây là một script Python hoàn chỉnh, được tối ưu hóa để cào danh sách nhiều URL tiếng Việt, tự động chuẩn hóa tiêu đề thành tên file an toàn (xóa ký tự cấm của hệ điều hành), lọc rác và lưu thành file `.md` với mã hóa **UTF-8**.

---

### Script Python hoàn chỉnh

```python
import os
import re
import sys
import requests
from bs4 import BeautifulSoup
import html2text

# Ép console xuất chuẩn UTF-8 (tránh lỗi hiển thị trên Windows)
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def sanitize_filename(title: str) -> str:
    """Làm sạch tiêu đề để dùng làm tên file an toàn trên Windows/Linux/macOS."""
    # 1. Bỏ các ký tự cấm trong tên file: \ / * ? : " < > |
    clean_title = re.sub(r'[\\/*?:"<>|]', "", title)

    # 2. Thay thế nhiều dấu khoảng trắng hoặc xuống dòng thành 1 khoảng trắng
    clean_title = re.sub(r"\s+", " ", clean_title).strip()

    # 3. Giới hạn độ dài tên file (tối đa 100 ký tự) để tránh lỗi quá dài đường dẫn
    if len(clean_title) > 100:
        clean_title = clean_title[:100].rsplit(" ", 1)[0]

    # Nếu tiêu đề rỗng sau khi lọc, đặt tên mặc định
    return clean_title if clean_title else "bai_viet_khong_tieu_de"


def scrape_url_to_markdown(url: str, output_dir: str = "output_markdown"):
    """Tải một URL, lọc nội dung và lưu thành file .md."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        # 1. Tải trang web
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = "utf-8"  # Đảm bảo UTF-8

        if response.status_code != 200:
            print(f"❌ [Lỗi {response.status_code}] Không thể tải: {url}")
            return

        # 2. Phân tích HTML bằng BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # 3. Trích xuất tiêu đề bài viết
        # Ưu tiên thẻ <h1>, nếu không có thì lấy thẻ <title>
        h1_tag = soup.find("h1")
        if h1_tag and h1_tag.get_text().strip():
            raw_title = h1_tag.get_text().strip()
        elif soup.title and soup.title.get_text().strip():
            raw_title = soup.title.get_text().strip()
        else:
            raw_title = "Bai_viet"

        safe_filename = sanitize_filename(raw_title)

        # 4. Lọc bỏ các thẻ rác không dùng đến
        unwanted_tags = ["script", "style", "nav", "footer", "header", "aside", "form"]
        for tag in soup(unwanted_tags):
            tag.decompose()

        # Tìm vùng bài viết chính (nếu có article/main thì lấy, không thì lấy body)
        content_area = soup.find("article") or soup.find("main") or soup.body

        # 5. Chuyển đổi sang Markdown
        h = html2text.HTML2Text()
        h.body_width = 0  # Không ngắt dòng tự động
        h.ignore_images = False  # Giữ lại ảnh (đổi thành True nếu muốn bỏ)

        markdown_text = h.handle(str(content_area))

        # 6. Lưu file với mã hóa UTF-8
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{safe_filename}.md")

        with open(filepath, "w", encoding="utf-8") as f:
            # Thêm tiêu đề ở đầu file Markdown
            f.write(f"# {raw_title}\n\n")
            f.write(f"> **Nguồn:** [{url}]({url})\n\n---\n\n")
            f.write(markdown_text)

        print(f"✅ Đã lưu: {filepath}")

    except Exception as e:
        print(f"❌ [Lỗi ngoại lệ] {url}: {e}")


# ==========================================
# THỰC THI SCRIPT
# ==========================================
if __name__ == "__main__":
    # Danh sách các URL cần cào
    urls = [
        "https://vi.wikipedia.org/wiki/Python_(ng%C3%B4n_ng%E1%BB%AF_l%E1%BA%ADp_tr%C3%ACnh)",
        "https://vi.wikipedia.org/wiki/Tr%C3%AD_tu%E1%BB%87_nh%C3%A2n_t%E1%BA%A1o",
    ]

    print("🚀 Bắt đầu cào dữ liệu...\n")
    for url in urls:
        scrape_url_to_markdown(url)

    print("\nHoàn tất! Các file .md được lưu trong thư mục 'output_markdown'.")

```

---

### Điểm nổi bật của Script này:

1. **`sanitize_filename()`**: Xử lý triệt để ký tự tiếng Việt có dấu và tự động loại bỏ các ký tự cấm của hệ điều hành (`/ \ : * ? " < > |`) để không bị văng lỗi khi tạo file.
2. **Xử lý UTF-8 toàn diện**: Đảm bảo từ lúc `requests` nhận dữ liệu đến lúc ghi file `open(..., encoding="utf-8")` đều đồng bộ chuẩn UTF-8.
3. **Trích xuất thông minh**: Lấy tiêu đề thực tế từ `<h1>` thay vì chỉ dùng thẻ `<title>` (vốn thường chứa thêm tên thương hiệu website như `| Báo VNExpress`).
4. **Tránh nghẽn/Sập chương trình**: Dùng khối `try...except` để nếu 1 URL bị lỗi link chết, script vẫn sẽ tiếp tục cào các URL còn lại trong danh sách.