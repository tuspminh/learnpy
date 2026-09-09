Khi làm Web Scraping ở quy mô lớn, hai rào cản lớn nhất bạn sẽ gặp phải là **IP bị khóa (Rate-limited / IP Ban)** và **Browser Fingerprinting** (phát hiện request từ script bằng User-Agent mặc định).

Để giải quyết vấn đề này, chúng ta sẽ nâng cấp script Async Scraper trước đó với 3 tính năng quan trọng:

1. **Random User-Agent:** Mỗi request gửi đi sẽ đóng vai một thiết bị/trình duyệt khác nhau (Chrome, Firefox, Safari, Edge trên Windows/Mac/Android).
2. **Proxy Rotation (Xoay vòng Proxy):** Mỗi request sẽ đi qua một địa chỉ IP Proxy ngẫu nhiên.
3. **Cơ chế Automatic Retry khi Proxy hỏng:** Vì proxy (đặc biệt là proxy miễn phí/giá rẻ) rất dễ bị die hoặc chập chờn, nếu request bị lỗi Proxy/Timeout, script sẽ tự động chọn một Proxy khác và thử lại.

---

## Script Async Scraper hoàn chỉnh (Proxy & User-Agent Rotation)

```python
import asyncio
import json
import logging
import random
from typing import List, Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup

# 1. Cấu hình Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

# Configuration Constants
BASE_URL = "https://quotes.toscrape.com/page/{page_num}/"
TOTAL_PAGES = 10
MAX_CONCURRENT_REQUESTS = 3
MAX_RETRIES = 3  # Số lần thử lại nếu Proxy bị lỗi
OUTPUT_FILE = "quotes_rotated.json"

# 2. Danh sách User-Agents đa dạng
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/122.0.0.0 Safari/537.36"
]

# 3. Danh sách Proxies (Thay thế bằng danh sách Proxy thật của bạn)
# Định dạng: "http://ip:port" hoặc "http://user:pass@ip:port" hoặc "socks5://ip:port"
PROXIES = [
    "http://103.152.112.162:80",
    "http://185.199.229.156:7492",
    "http://188.166.217.15:3128",
    # Thêm các IP proxy khác của bạn vào đây...
]

def get_random_headers() -> dict:
    """Tạo Headers ngẫu nhiên với User-Agent ngẫu nhiên cho mỗi Request"""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }

def get_random_proxy() -> Optional[str]:
    """Lấy ngẫu nhiên 1 Proxy từ danh sách (Trả về None nếu danh sách rỗng)"""
    return random.choice(PROXIES) if PROXIES else None

async def fetch_page_with_retry(
    semaphore: asyncio.Semaphore, 
    page_num: int
) -> List[Dict[str, Any]]:
    """
    Cào 1 trang với cơ chế Xoay vòng Proxy, Random User-Agent và Retry tự động
    """
    url = BASE_URL.format(page_num=page_num)
    
    async with semaphore:
        for attempt in range(1, MAX_RETRIES + 1):
            proxy = get_random_proxy()
            headers = get_random_headers()
            
            logging.info(
                f"🔄 Trang {page_num} (Lần thử {attempt}/{MAX_RETRIES}) "
                f"| Proxy: {proxy or 'Direct (Khong Proxy)'}"
            )

            try:
                # Tạo AsyncClient riêng cho từng request để đổi Proxy linh hoạt
                async with httpx.AsyncClient(
                    proxy=proxy,
                    headers=headers,
                    timeout=httpx.Timeout(10.0, connect=5.0),
                    follow_redirects=True
                ) as client:
                    
                    response = await client.get(url)
                    response.raise_for_status()

                    # Bóc tách HTML
                    soup = BeautifulSoup(response.text, "html.parser")
                    quotes_in_page = []

                    for elem in soup.select(".quote"):
                        text = elem.select_one(".text").get_text(strip=True)
                        author = elem.select_one(".author").get_text(strip=True)
                        tags = [tag.get_text(strip=True) for tag in elem.select(".tag")]
                        
                        quotes_in_page.append({
                            "page": page_num,
                            "quote": text,
                            "author": author,
                            "tags": tags
                        })

                    logging.info(f"✅ Thành công trang {page_num} với Proxy: {proxy}")
                    return quotes_in_page

            except (httpx.ProxyError, httpx.ConnectError, httpx.TimeoutException) as e:
                logging.warning(f"⚠️ Proxy lỗi/chậm khi cào trang {page_num} ({type(e).__name__}). Đang thử lại với Proxy khác...")
            except httpx.HTTPStatusError as e:
                logging.error(f"❌ Server trả về lỗi status {e.response.status_code} cho trang {page_num}")
                if e.response.status_code == 404:
                    break # Nếu 404 thì không cần retry nữa
            except Exception as e:
                logging.error(f"❌ Lỗi không xác định ở trang {page_num}: {e}")

            # Chờ một khoảng thời gian ngắn trước khi retry
            await asyncio.sleep(1)

        logging.error(f"💥 Thất bại hoàn toàn trang {page_num} sau {MAX_RETRIES} lần thử.")
        return []

async def main():
    start_time = asyncio.get_event_loop().time()
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    # Khởi tạo danh sách các Task
    tasks = [fetch_page_with_retry(semaphore, page_num) for page_num in range(1, TOTAL_PAGES + 1)]
    
    # Chạy song song tất cả các trang
    results = await asyncio.gather(*tasks)

    # Flatten danh sách kết quả
    all_quotes = [quote for page_quotes in results for quote in page_quotes]

    # Lưu ra file JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_quotes, f, ensure_ascii=False, indent=2)

    total_time = asyncio.get_event_loop().time() - start_time
    logging.info("=" * 60)
    logging.info(f"🎉 Hoàn thành! Thu thập được {len(all_quotes)} trích dẫn.")
    logging.info(f"⏱️ Tổng thời gian: {total_time:.2f} giây")

if __name__ == "__main__":
    asyncio.run(main())

```

---

## 🛠️ Những nâng cấp quan trọng cần lưu ý

1. **Khởi tạo `httpx.AsyncClient` linh hoạt từng Request:**
* Thay vì tạo 1 Client duy nhất cho toàn bộ chương trình như trước, chúng ta mở `async with httpx.AsyncClient(proxy=proxy, headers=headers)` bên trong hàm `fetch_page_with_retry`.
* Việc này giúp mỗi request có thể gán một địa chỉ **Proxy** và **User-Agent** riêng biệt.


2. **Cơ chế Bắt lỗi Proxy chuẩn xác:**
* Cụm `except (httpx.ProxyError, httpx.ConnectError, httpx.TimeoutException)` giúp bắt đúng các lỗi liên quan đến đường truyền Proxy. Khi gặp lỗi này, vòng lặp `for attempt in range(...)` sẽ tự nhảy sang lượt tiếp theo và chọn ngẫu nhiên một Proxy mới trong danh sách để thử lại.


3. **Mẹo dùng `fake-useragent` (Tùy chọn):**
* Nếu không muốn tự khai báo danh sách `USER_AGENTS` bằng tay, bạn có thể cài thêm thư viện:
```bash
pip install fake-useragent

```


* Sau đó thay hàm `get_random_headers()` bằng:
```python
from fake_useragent import UserAgent

ua = UserAgent()

def get_random_headers() -> dict:
    return {"User-Agent": ua.random}

```