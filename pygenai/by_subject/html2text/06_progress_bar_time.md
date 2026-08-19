Khi cào hàng loạt, việc gửi hàng chục request liên tục trong vài giây rất dễ kích hoạt cơ chế chống Ddos / Bot detection của server (Cloudflare, Akamai...), dẫn đến việc IP bị khóa tạm thời (Lỗi `429 Too Many Requests` hoặc `403 Forbidden`).

Để giải quyết, chúng ta kết hợp **3 kỹ thuật**:

1. **`tqdm`**: Trực quan hóa tiến trình cào dữ liệu bằng thanh progress bar chuyên nghiệp.
2. **`time.sleep()` + `random**`: Tạo độ trễ ngẫu nhiên giữa các request (mô phỏng thao tác đọc bài của người thật).
3. **`tqdm.write()`**: Thay thế hàm `print()` tiêu chuẩn để thông báo không làm vỡ giao diện thanh tiến trình.

---

## 1. Cài đặt thư viện `tqdm`

Mở terminal và cài đặt thêm `tqdm`:

```bash
pip install tqdm

```

---

## 2. Script hoàn chỉnh nâng cấp

Dưới đây là script đã tích hợp `tqdm` và cơ chế chống bị chặn IP:

```python
import os
import random
import re
import sys
import time
import html2text
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# Ép console xuất chuẩn UTF-8
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def sanitize_filename(title: str) -> str:
    """Làm sạch tiêu đề để dùng làm tên file an toàn."""
    clean_title = re.sub(r'[\\/*?:"<>|]', "", title)
    clean_title = re.sub(r"\s+", " ", clean_title).strip()
    if len(clean_title) > 100:
        clean_title = clean_title[:100].rsplit(" ", 1)[0]
    return clean_title if clean_title else "bai_viet_khong_tieu_de"


def scrape_url_to_markdown(url: str, output_dir: str = "output_markdown") -> bool:
    """Tải một URL và lưu thành file .md."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = "utf-8"

        if response.status_code != 200:
            # Dùng tqdm.write thay cho print để không bị tràn thanh tiến trình
            tqdm.write(f"❌ [Lỗi {response.status_code}] Không thể tải: {url}")
            return False

        soup = BeautifulSoup(response.text, "html.parser")

        # Trích xuất tiêu đề
        h1_tag = soup.find("h1")
        if h1_tag and h1_tag.get_text().strip():
            raw_title = h1_tag.get_text().strip()
        elif soup.title and soup.title.get_text().strip():
            raw_title = soup.title.get_text().strip()
        else:
            raw_title = "Bai_viet"

        safe_filename = sanitize_filename(raw_title)

        # Lọc rác
        unwanted_tags = ["script", "style", "nav", "footer", "header", "aside", "form"]
        for tag in soup(unwanted_tags):
            tag.decompose()

        content_area = soup.find("article") or soup.find("main") or soup.body

        # Convert HTML sang Markdown
        h = html2text.HTML2Text()
        h.body_width = 0

        markdown_text = h.handle(str(content_area))

        # Lưu file
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{safe_filename}.md")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {raw_title}\n\n")
            f.write(f"> **Nguồn:** [{url}]({url})\n\n---\n\n")
            f.write(markdown_text)

        tqdm.write(f"✅ Đã lưu: {safe_filename}.md")
        return True

    except Exception as e:
        tqdm.write(f"❌ [Lỗi] {url}: {e}")
        return False


# ==========================================
# THỰC THI CHƯƠNG TRÌNH
# ==========================================
if __name__ == "__main__":
    urls = [
        "https://vi.wikipedia.org/wiki/Python_(ng%C3%B4n_ng%E1%BB%AF_l%E1%BA%ADp_tr%C3%ACnh)",
        "https://vi.wikipedia.org/wiki/Tr%C3%AD_tu%E1%BB%87_nh%C3%A2n_t%E1%BA%A1o",
        "https://vi.wikipedia.org/wiki/H%E1%BB%8Dc_m%C3%A1y",
        "https://vi.wikipedia.org/wiki/Khoa_h%E1%BB%8Dc_d%E1%BB%AF_li%E1%BB%87u",
    ]

    print("🚀 Bắt đầu quá trình cào dữ liệu...\n")

    # Bọc danh sách urls bằng tqdm() để tạo progress bar
    # unit="link" thể hiện đơn vị đếm trên thanh tiến trình
    for url in tqdm(urls, desc="Tiến độ cào web", unit="link"):
        
        # 1. Gọi hàm cào dữ liệu
        success = scrape_url_to_markdown(url)

        # 2. Tạo khoảng dừng ngẫu nhiên từ 1.5s đến 3.5s giữa mỗi request
        # (Chỉ dừng nếu chưa phải là link cuối cùng)
        if url != urls[-1]:
            delay = random.uniform(1.5, 3.5)
            time.sleep(delay)

    print("\n🎉 Hoàn tất toàn bộ công việc!")

```

---

## 3. Các điểm quan trọng cần lưu ý

1. **Tại sao dùng `random.uniform(1.5, 3.5)` thay vì `time.sleep(2)` cố định?**
* Nếu bạn gửi request với đúng chu kỳ 2 giây/lần, firewall của server dễ dàng phát hiện ra hành vi lập trình sẵn (bot). Việc thêm ngẫu nhiên số lẻ (ví dụ: `2.13s`, `1.87s`, `3.21s`) giúp mô phỏng chính xác hơn thao tác click của con người.


2. **Dùng `tqdm.write()` thay cho `print()**`:
* Chuỗi `print()` tiêu chuẩn sẽ đẩy dòng mới và ghi đè làm hỏng (vỡ) thanh tiến trình của `tqdm`. `tqdm.write()` sẽ khéo léo in log lên phía trên thanh tiến trình mà không làm ảnh hưởng đến hiệu ứng chạy phần trăm bên dưới.


3. **Cấu hình thanh tiến trình `tqdm**`:
* `desc`: Nhãn hiển thị đầu thanh tiến trình (ví dụ: `"Tiến độ cào web"`).
* `unit`: Đơn vị hiển thị trên tốc độ xử lý (ví dụ: `4/4 [00:08<00:00, 2.12s/link]`).