Kết hợp **`httpx` (Async)** + **`asyncio`** + **`selectolax`** tạo nên bộ ba (stack) cào dữ liệu web (scraping) có hiệu năng thuộc hàng cao nhất hiện nay trong Python:

* **`httpx.AsyncClient` + `asyncio**`: Xử lý hàng trăm yêu cầu mạng (Network I/O) cùng lúc mà không bị nghẽn (non-blocking).
* **`selectolax`**: Phân tích cú pháp DOM (CPU-bound) bằng C với tốc độ gần như tức thì, không làm trễ Event Loop của asyncio.

---

## 1. Mẫu Code Chuẩn (Production Template)

Dưới đây là một script hoàn chỉnh cào danh sách trang web bất đồng bộ, sử dụng **`asyncio.Semaphore`** để kiểm soát số lượng request đồng thời (tránh bị server đích chặn IP).

### Cài đặt thư viện:

```bash
pip install httpx selectolax

```

### Python Script: `async_crawler.py`

```python
import asyncio
from typing import Any, Dict, List
import httpx
from selectolax.lexbor import LexborHTMLParser

# Danh sách URL mẫu cần cào (Ví dụ 20 trang)
URLS = [f"https://quotes.toscrape.com/page/{i}/" for i in range(1, 21)]


# 1. HÀM PARSE HTML (Chạy đồng bộ vì Selectolax siêu nhanh)
def parse_quotes_page(html: str, url: str) -> List[Dict[str, Any]]:
    """Phân tích HTML bằng Selectolax và bóc tách dữ liệu"""
    tree = LexborHTMLParser(html)
    page_data = []

    for quote_node in tree.css("div.quote"):
        text_node = quote_node.css_first("span.text")
        author_node = quote_node.css_first("small.author")
        tags = [tag.text(strip=True) for tag in quote_node.css("a.tag")]

        page_data.append(
            {
                "quote": text_node.text(strip=True) if text_node else None,
                "author": author_node.text(strip=True) if author_node else None,
                "tags": tags,
                "source_url": url,
            }
        )

    return page_data


# 2. HÀM FETCH BẤT ĐỒNG BỘ CHO MỖI URL
async def fetch_and_parse(
    client: httpx.AsyncClient, semaphore: asyncio.Semaphore, url: str
) -> List[Dict[str, Any]]:
    """Gửi request và gọi parser với cơ chế giới hạn luồng (Semaphore)"""
    async with semaphore:
        try:
            # Gửi HTTP Request bất đồng bộ
            response = await client.get(url)
            response.raise_for_status()

            # Parse dữ liệu (Do Selectolax chạy bằng C mất ~1ms nên gọi trực tiếp)
            return parse_quotes_page(response.text, url)

        except httpx.HTTPStatusError as e:
            print(f"❌ Lỗi HTTP {e.response.status_code} tại {url}")
        except httpx.RequestError as e:
            print(f"❌ Lỗi kết nối ({e}) tại {url}")
        except Exception as e:
            print(f"❌ Lỗi không xác định tại {url}: {e}")

        return []


# 3. HÀM ĐIỀU PHỐI CHÍNH (MAIN ASYNC LOOP)
async def main():
    # GIỚI HẠN: Chỉ cho phép tối đa 5 request chạy song song cùng một thời điểm
    CONCURRENCY_LIMIT = 5
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    # Cấu hình Pool kết nối cho HTTPX
    limits = httpx.Limits(
        max_keepalive_connections=10, max_connections=CONCURRENCY_LIMIT
    )

    # Khởi tạo AsyncClient tái sử dụng connection
    async with httpx.AsyncClient(
        headers=headers, timeout=10.0, limits=limits, follow_redirects=True
    ) as client:
        # Tạo danh sách các task
        tasks = [fetch_and_parse(client, semaphore, url) for url in URLS]

        print(
            f"🚀 Bắt đầu cào {len(URLS)} trang (Tối đa {CONCURRENCY_LIMIT} luồng đồng thời)..."
        )

        # Chạy tất cả các task song song
        results = await asyncio.gather(*tasks)

        # Gom gộp kết quả từ các trang
        all_data = [item for sublist in results for item in sublist]

        print(
            f"✅ Hoàn tất! Thu thập được tổng cộng {len(all_data)} mục dữ liệu."
        )


if __name__ == "__main__":
    asyncio.run(main())

```

---

## 2. Những lưu ý kỹ thuật quan trọng (Best Practices)

### A. Tốc độ Selectolax & Event Loop

Khác với `BeautifulSoup4` (có thể làm nghẽn Event Loop khi parse HTML lớn), `selectolax` được viết bằng C nên thời gian parse 1 file HTML thường chỉ mất **1-2 milliseconds**. Do đó, bạn có thể gọi trực tiếp `LexborHTMLParser(html)` inside async function mà **không cần** chuyển sang ThreadPool/ProcessPool executor.

### B. Luôn dùng `asyncio.Semaphore`

Nếu cào hàng nghìn trang mà không dùng `Semaphore`, script sẽ bắn hàng nghìn request **cùng một microsecond**. Điều này sẽ gây ra:

* Bị Server đố phương chặn IP ngay lập tức (Status code 429 hoặc 403).
* Tràn bộ nhớ RAM hoặc lỗi `Too many open files` của Hệ điều hành.

### C. Tối ưu HTTPX với `httpx.Limits` và `HTTP/2`

Nếu trang web hỗ trợ HTTP/2, bạn có thể tăng tốc thêm bằng cách bật HTTP/2 (yêu cầu cài `pip install httpx[http2]`):

```python
async with httpx.AsyncClient(
    http2=True,  # Bật HTTP/2 multiplexing
    limits=httpx.Limits(
        max_connections=20, max_keepalive_connections=10
    ),  # Giữ kết quả socket mở để tái sử dụng
) as client:
    ...

```

### D. Xử lý Retry tự động khi gặp lỗi mạng

Có thể kết hợp thêm thư viện **`tenacity`** để tự động thử lại khi request bị timeout hoặc gặp lỗi server:

```python
from tenacity import retry, stop_after_attempt, wait_exponential


@retry(
    stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def fetch_with_retry(client, url):
    response = await client.get(url)
    response.raise_for_status()
    return response.text

```