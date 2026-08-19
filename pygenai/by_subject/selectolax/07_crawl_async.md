Mô hình **Cào dữ liệu 2 tầng (2-Tier Crawler)** là bài toán phổ biến nhất trong Web Scraping:

* **Tầng 1 (List Phase):** Cào trang danh sách để thu thập toàn bộ đường dẫn (URL) của trang chi tiết.
* **Tầng 2 (Detail Phase):** Gửi các request bất đồng bộ song song để cào thông tin chi tiết từng sản phẩm/bài viết từ danh sách URL thu được.

Dưới đây là hướng dẫn chi tiết kèm script Python hoàn chỉnh sử dụng `httpx` (Async), `asyncio` và `selectolax` chạy trên trang mẫu [Books to Scrape](https://books.toscrape.com/).

---

## 1. Kiến trúc luồng xử lý (Data Flow)

```text
[ Danh sách URL Trang List ] 
          │
          ▼ (HTTPX Async)
   [ Fetch & Parse List ] ────► [ Trích xuất List URL Chi tiết ]
                                             │
                                             ▼ (Khử trùng lặp: set)
                                   [ Set URL Chi tiết ]
                                             │
                                             ▼ (Asyncio Semaphore - Max N Concurrent)
                                  [ Fetch & Parse Detail ]
                                             │
                                             ▼
                                  [ Kết quả JSON/Dict ]

```

---

## 2. Script Python hoàn chỉnh (`multi_tier_crawler.py`)

Cài đặt thư viện nếu chưa có:

```bash
pip install httpx selectolax

```

```python
import asyncio
from typing import Any, Dict, List, Set
from urllib.parse import urljoin
import httpx
from selectolax.lexbor import LexborHTMLParser

# Cấu hình chung
BASE_URL = "https://books.toscrape.com/"
LIST_URLS = [
    f"https://books.toscrape.com/catalogue/page-{i}.html" for i in range(1, 4)
]  # Cào 3 trang danh sách mẫu


# ==============================================================================
# 1. BÓC TÁCH DỮ LIỆU (PARSERS)
# ==============================================================================


def parse_list_page(html: str, current_url: str) -> Set[str]:
    """Phân tích trang danh sách và trích xuất tất cả URL trang chi tiết"""
    tree = LexborHTMLParser(html)
    detail_urls = set()

    # Mối sách nằm trong thẻ h3 > a
    for a_tag in tree.css("h3 > a"):
        href = a_tag.attributes.get("href")
        if href:
            # Chuyển URL tương đối (../book.html) thành URL tuyệt đối
            full_url = urljoin(current_url, href)
            detail_urls.add(full_url)

    return detail_urls


def parse_detail_page(html: str, url: str) -> Dict[str, Any]:
    """Phân tích nội dung trang chi tiết sách"""
    tree = LexborHTMLParser(html)

    title_node = tree.css_first("h1")
    price_node = tree.css_first("p.price_color")
    stock_node = tree.css_first("p.instock.availability")
    upc_node = tree.css_first("table.table-striped td")

    return {
        "url": url,
        "title": title_node.text(strip=True) if title_node else None,
        "price": price_node.text(strip=True) if price_node else None,
        "stock": stock_node.text(strip=True) if stock_node else None,
        "upc": upc_node.text(strip=True) if upc_node else None,
    }


# ==============================================================================
# 2. BẤT ĐỒNG BỘ FETCHERS
# ==============================================================================


async def fetch_list_page(
    client: httpx.AsyncClient, semaphore: asyncio.Semaphore, url: str
) -> Set[str]:
    """Gửi request lấy trang danh sách"""
    async with semaphore:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            return parse_list_page(resp.text, url)
        except Exception as e:
            print(f"❌ Lỗi khi cào trang danh sách {url}: {e}")
            return set()


async def fetch_detail_page(
    client: httpx.AsyncClient, semaphore: asyncio.Semaphore, url: str
) -> Dict[str, Any] | None:
    """Gửi request lấy trang chi tiết"""
    async with semaphore:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            return parse_detail_page(resp.text, url)
        except Exception as e:
            print(f"❌ Lỗi khi cào trang chi tiết {url}: {e}")
            return None


# ==============================================================================
# 3. ĐIỀU PHỐI CHÍNH (MAIN WORKFLOW)
# ==============================================================================


async def main():
    # Khống chế tối đa 10 request đồng thời để tránh crash IP
    CONCURRENCY_LIMIT = 10
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    async with httpx.AsyncClient(
        headers=headers, timeout=10.0, follow_redirects=True
    ) as client:

        # ----------------------------------------------------------------------
        # BƯỚC 1: CÀO TẤT CẢ TRANG DANH SÁCH ĐỂ LẤY URL CHI TIẾT
        # ----------------------------------------------------------------------
        print(f"🚀 BẮT ĐẦU TẦNG 1: Cào {len(LIST_URLS)} trang danh sách...")

        list_tasks = [
            fetch_list_page(client, semaphore, url) for url in LIST_URLS
        ]
        list_results = await asyncio.gather(*list_tasks)

        # Gom tất cả các URL chi tiết tìm được và khử trùng lặp bằng set()
        all_detail_urls: Set[str] = set().union(*list_results)
        print(
            f"✅ TẦNG 1 HOÀN TẤT: Tìm thấy {len(all_detail_urls)} URL trang chi tiết độc bản.\n"
        )

        # ----------------------------------------------------------------------
        # BƯỚC 2: CÀO TẤT CẢ TRANG CHI TIẾT SONG SONG
        # ----------------------------------------------------------------------
        print(
            f"🚀 BẮT ĐẦU TẦNG 2: Đang cào {len(all_detail_urls)} trang chi tiết..."
        )

        detail_tasks = [
            fetch_detail_page(client, semaphore, url)
            for url in all_detail_urls
        ]
        detail_results = await asyncio.gather(*detail_tasks)

        # Lọc bỏ các kết quả None (do lỗi request)
        final_data = [item for item in detail_results if item is not None]

        print(
            f"\n🎉 THÀNH CÔNG! Đã thu thập hoàn chỉnh {len(final_data)} item."
        )

        # In mẫu 3 kết quả đầu tiên
        print("\n--- MẪU DỮ LIỆU THU ĐƯỢC ---")
        for item in final_data[:3]:
            print(item)


if __name__ == "__main__":
    asyncio.run(main())

```

---

## 3. Các điểm mấu chốt trong mã nguồn

1. **Chuẩn hóa URL tương đối bằng `urljoin**`:
Trang danh sách thường chứa link tương đối như `../../../a-light-in-the-attic_1000/index.html`. Sử dụng `urllib.parse.urljoin(current_url, href)` giúp biến các link này thành link đầy đủ chính xác.
2. **Quản lý giới hạn tải với `asyncio.Semaphore**`:
Dù ở Tầng 1 hay Tầng 2, tất cả hàm `fetch_*` đều bọc trong `async with semaphore:`. Việc này giữ cho số lượng kết nối đồng thời không bao giờ vượt quá `CONCURRENCY_LIMIT` (ví dụ: 10), bảo vệ bạn khỏi bị server chặn IP (rate limit).
3. **Giai đoạn gộp URL (Deduplication)**:
Thao tác `set().union(*list_results)` loại bỏ các link trùng lặp nếu cùng một sản phẩm xuất hiện ở nhiều trang danh sách khác nhau.
4. **Quản lý phiên với `httpx.AsyncClient**`:
Sử dụng duy nhất một ngữ cảnh `async with httpx.AsyncClient()` xuyên suốt từ Tầng 1 đến Tầng 2 giúp tái sử dụng lại các kết nối TCP (Connection Pooling), tiết kiệm băng thông và tăng tốc đáng kể.