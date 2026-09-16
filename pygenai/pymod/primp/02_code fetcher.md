Dưới đây là module `story_fetcher.py` hoàn chỉnh được thiết kế riêng cho việc crawl truyện chữ. Code sử dụng **`primp`** để vượt qua các tường lửa anti-bot (Cloudflare, Akamai) cùng **`BeautifulSoup`** để bóc tách nội dung chương và danh sách chương.

### 1. Cài đặt thư viện cần thiết

```bash
pip install primp beautifulsoup4 lxml

```

---

### 2. Source code `story_fetcher.py`

```python
import time
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import primp

class StoryFetcher:
    def __init__(self, impersonate: str = "chrome_126", proxy: Optional[str] = None):
        """
        Khởi tạo Fetcher giả lập trình duyệt để tránh bị chặn IP / TLS Fingerprint
        """
        self.client = primp.Client(
            impersonate=impersonate,
            os="windows",
            proxy=proxy,
            cookie_store=True,
            timeout=15,
            headers={
                "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://google.com"
            }
        )

    def _get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """Gửi request và trả về đối tượng BeautifulSoup"""
        try:
            response = self.client.get(url)
            if response.status_code == 200:
                return BeautifulSoup(response.text, "lxml")
            print(f"[ERROR] Request thất bại. Status Code: {response.status_code} - URL: {url}")
            return None
        except Exception as e:
            print(f"[EXCEPTION] Lỗi kết nối tới {url}: {e}")
            return None

    def fetch_story_info(self, story_url: str, selectors: Dict[str, str]) -> Dict[str, str]:
        """
        Crawl thông tin tổng quan của truyện (Tên, tác giả, mô tả, ảnh cover...)
        """
        soup = self._get_soup(story_url)
        if not soup:
            return {}

        title = soup.select_one(selectors.get("title", ""))
        author = soup.select_one(selectors.get("author", ""))
        description = soup.select_one(selectors.get("description", ""))
        cover_img = soup.select_one(selectors.get("cover", ""))

        return {
            "title": title.text.strip() if title else "N/A",
            "author": author.text.strip() if author else "N/A",
            "description": description.text.strip() if description else "N/A",
            "cover_url": cover_img.get("src", "") if cover_img else ""
        }

    def fetch_chapter_list(self, story_url: str, chapter_selector: str) -> List[Dict[str, str]]:
        """
        Lấy danh sách các chương (Tên chương và Link)
        """
        soup = self._get_soup(story_url)
        if not soup:
            return []

        chapters = []
        for a_tag in soup.select(chapter_selector):
            title = a_tag.text.strip()
            href = a_tag.get("href")
            
            # Xử lý URL tương đối (relative URL) nếu có
            if href and not href.startswith("http"):
                base_domain = "/".join(story_url.split("/")[:3])
                href = f"{base_domain}{href if href.startswith('/') else '/' + href}"

            chapters.append({
                "chapter_title": title,
                "url": href
            })
            
        return chapters

    def fetch_chapter_content(self, chapter_url: str, content_selector: str, remove_selectors: List[str] = None) -> Dict[str, str]:
        """
        Lấy nội dung văn bản của một chương và làm sạch quảng cáo/rác HTML
        """
        soup = self._get_soup(chapter_url)
        if not soup:
            return {}

        content_div = soup.select_one(content_selector)
        if not content_div:
            return {"url": chapter_url, "content": ""}

        # Xóa bớt các thẻ chứa quảng cáo hoặc link rác nằm trong nội dung
        if remove_selectors:
            for selector in remove_selectors:
                for tag in content_div.select(selector):
                    tag.decompose()

        # Thay thế các thẻ <br> hoặc <p> bằng dòng mới để giữ cấu hình đoạn văn
        for br in content_div.find_all(["br", "p"]):
            br.replace_with(f"\n{br.text.strip() if br.name == 'p' else ''}")

        raw_text = content_div.get_text()
        
        # Làm sạch khoảng trắng thừa
        clean_lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        clean_content = "\n\n".join(clean_lines)

        return {
            "url": chapter_url,
            "content": clean_content
        }

```

---

### 3. Ví dụ cách triển khai thực tế

```python
if __name__ == "__main__":
    fetcher = StoryFetcher(impersonate="chrome_126")

    # 1. Cấu hình CSS Selector theo trang web bạn muốn crawl (Ví dụ minh họa cấu trúc phổ biến)
    STORY_URL = "https://example-truyen-site.com/truyen-dem-trang"
    
    info_selectors = {
        "title": "h3.title",
        "author": ".info a[itemprop='author']",
        "description": ".desc-text",
        "cover": ".book-img img"
    }

    # 2. Lấy thông tin truyện
    print("--- Đang lấy thông tin truyện ---")
    info = fetcher.fetch_story_info(STORY_URL, info_selectors)
    print(info)

    # 3. Lấy danh sách chương
    print("\n--- Đang lấy danh sách chương ---")
    chapter_list_selector = "ul.list-chapter li a"
    chapters = fetcher.fetch_chapter_list(STORY_URL, chapter_list_selector)
    print(f"Tổng số chương tìm thấy: {len(chapters)}")

    # 4. Crawl thử nội dung chương đầu tiên
    if chapters:
        first_chap = chapters[0]
        print(f"\n--- Đang crawl: {first_chap['chapter_title']} ---")
        
        content_selector = "#chapter-content"
        # Xóa các thẻ quảng cáo ẩn bên trong nội dung nếu có
        ads_selectors = [".adsbox", "script", ".ads-holder"] 

        chapter_data = fetcher.fetch_chapter_content(
            chapter_url=first_chap["url"],
            content_selector=content_selector,
            remove_selectors=ads_selectors
        )
        
        print("Nội dung xem trước (200 ký tự đầu):")
        print(chapter_data["content"][:200] + "...")

```

---

### Các lưu ý quan trọng khi triển khai App Crawl

1. **Phân trang danh sách chương:** Một số trang web chia danh sách chương thành nhiều trang (`page=1`, `page=2`). Bạn cần viết thêm vòng lặp lướt trang nếu cần lấy toàn bộ chương.
2. **Delay giữa các request:** Luôn chèn `time.sleep(1)` đến `time.sleep(2)` giữa mỗi lần gọi chương mới để tránh bị khoá IP do gửi request quá nhanh.
3. **Trường hợp AJAX/Nội dung động:** Nếu trang web load chương bằng JavaScript API ẩn, bạn chỉ cần mở F12 (Tab Network) tìm API JSON đó và dùng `fetcher.client.get(api_url).json()` trực tiếp mà không cần dùng BeautifulSoup.