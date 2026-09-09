Dưới đây là một script **Async Web Scraper hoàn chỉnh**, áp dụng đầy đủ các kỹ thuật nâng cao đã học: **`httpx.AsyncClient`**, **`asyncio.Semaphore`** (giới hạn tốc độ), xử lý lỗi, cùng thư viện **`BeautifulSoup`** để trích xuất dữ liệu.

Ví dụ này sẽ cào dữ liệu trích dẫn (Quotes), tác giả và thẻ tag từ trang web sandbox thực hành scraping nổi tiếng: `[https://quotes.toscrape.com](https://quotes.toscrape.com)`.

---

## 1. Cài đặt các thư viện cần thiết

Trước tiên, bạn cần cài đặt `httpx` và `beautifulsoup4` (dùng để đọc và bóc tách HTML):

```bash
pip install httpx beautifulsoup4

```

---

## 2. Mã nguồn Async Scraper hoàn chỉnh

```python
import asyncio
import json
import logging
from typing import List, Dict, Any
import httpx
from bs4 import BeautifulSoup

# 1. Cấu hình Logging để dễ theo dõi quá trình chạy
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

# Configuration Constants
BASE_URL = "https://quotes.toscrape.com/page/{page_num}/"
TOTAL_PAGES = 10                  # Tổng số trang cần cào
MAX_CONCURRENT_REQUESTS = 3       # Tối đa 3 request cùng một thời điểm (Tránh bị rate limit)
OUTPUT_FILE = "quotes_data.json"  # Tệp lưu kết quả

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

async def fetch_and_parse_page(
    client: httpx.AsyncClient, 
    semaphore: asyncio.Semaphore, 
    page_num: int
) -> List[Dict[str, Any]]:
    """
    Hàm xử lý cào 1 trang cụ thể: Gửi request -> Bóc tách HTML -> Trả về danh sách dữ liệu
    """
    url = BASE_URL.format(page_num=page_num)
    
    # Giới hạn số lượng request chạy song song bằng Semaphore
    async with semaphore:
        logging.info(f"🚀 Bắt đầu cào trang {page_num}: {url}")
        
        try:
            # Gửi HTTP GET Request
            response = await client.get(url)
            response.raise_for_status() # Bắt lỗi nếu mã trạng thái >= 400
            
            # Sử dụng BeautifulSoup để phân tích HTML
            soup = BeautifulSoup(response.text, "html.parser")
            quotes_in_page = []

            # Trích xuất dữ liệu dựa trên CSS Selector
            quote_elements = soup.select(".quote")
            for elem in quote_elements:
                text = elem.select_one(".text").get_text(strip=True)
                author = elem.select_one(".author").get_text(strip=True)
                tags = [tag.get_text(strip=True) for tag in elem.select(".tag")]
                
                quotes_in_page.append({
                    "page": page_num,
                    "quote": text,
                    "author": author,
                    "tags": tags
                })

            logging.info(f"✅ Hoàn thành trang {page_num} | Tìm thấy {len(quotes_in_page)} trích dẫn")
            return quotes_in_page

        except httpx.HTTPStatusError as e:
            logging.error(f"❌ Lỗi HTTP trang {page_num}: Status {e.response.status_code}")
        except httpx.RequestError as e:
            logging.error(f"❌ Lỗi đường truyền trang {page_num}: {e}")
        except Exception as e:
            logging.error(f"❌ Lỗi không xác định khi xử lý trang {page_num}: {e}")
        
        # Nếu có lỗi, trả về danh sách rỗng để không làm nghẽn toàn bộ ứng dụng
        return []

async def main():
    start_time = asyncio.get_event_loop().time()
    
    # Semaphore kiểm soát số request chạy đồng thời
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    # Cấu hình Client
    timeout = httpx.Timeout(10.0, connect=5.0)
    limits = httpx.Limits(max_connections=10, max_keepalive_connections=5)
    
    # Khởi tạo AsyncClient chung
    async with httpx.AsyncClient(headers=HEADERS, timeout=timeout, limits=limits) as client:
        # Tạo danh sách các task cào từ trang 1 đến TOTAL_PAGES
        tasks = [
            fetch_and_parse_page(client, semaphore, page_num) 
            for page_num in range(1, TOTAL_PAGES + 1)
        ]
        
        # Chạy song song tất cả các task
        results = await asyncio.gather(*tasks)

    # Gom tất cả danh sách con thành một danh sách phẳng (Flatten)
    all_quotes = [quote for page_quotes in results for quote in page_quotes]

    # Ghi dữ liệu thu thập được ra file JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_quotes, f, ensure_ascii=False, indent=2)

    total_time = asyncio.get_event_loop().time() - start_time
    logging.info("=" * 50)
    logging.info(f"🎉 TỔNG KẾT: Thu thập được {len(all_quotes)} trích dẫn từ {TOTAL_PAGES} trang.")
    logging.info(f"⏱️ Tổng thời gian thực thi: {total_time:.2f} giây")
    logging.info(f"💾 Dữ liệu đã lưu vào: {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())

```

---

## 3. Các điểm mấu chốt trong đoạn mã trên

1. **`asyncio.Semaphore(3)`**: Đảm bảo tại một thời điểm chỉ có tối đa 3 trang được gọi đồng thời, tránh việc Spam request khiến IP bị khóa.
2. **`httpx.AsyncClient` tái sử dụng**: Khởi tạo 1 lần duy nhất trong khối `async with` của hàm `main()`, tận dụng lại connection pool giúp tăng tốc độ mạng tối đa.
3. **Quản lý Exception an toàn**: Từng hàm `fetch_and_parse_page` đều có khối `try...except` riêng. Nếu trang số 5 bị lỗi mạng, các trang 1, 2, 3, 4, 6... vẫn chạy bình thường mà không dừng toàn bộ chương trình.
4. **Giả lập `User-Agent**`: Header `User-Agent` giúp request trông giống như gửi từ trình duyệt Chrome thật.

---

## 💡 Mẹo nâng cao khi đi Cào Web (Web Scraping) thực tế

* **Tăng tốc độ bóc tách HTML:** Nếu cần bóc tách dữ liệu dung lượng lớn (vài nghìn trang), thay vì dùng `beautifulsoup4`, bạn có thể dùng **`selectolax`** (thư viện C-based parser nhanh gấp 5-10 lần BeautifulSoup).
* **Xoay vòng Proxy (Proxy Rotation):** Khi cào quy mô lớn, hãy kết hợp truyền Proxy vào `AsyncClient` để tự động đổi IP sau mỗi lượt request.
* **Tự động lưu dạng CSV:** Bạn có thể dễ dàng chuyển `all_quotes` thành DataFrame và lưu file CSV thông qua thư viện `pandas`:
```python
import pandas as pd
df = pd.DataFrame(all_quotes)
df.to_csv("quotes.csv", index=False, encoding="utf-8-sig")

```