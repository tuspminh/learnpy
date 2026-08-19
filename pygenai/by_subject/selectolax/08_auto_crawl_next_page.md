Thay vì phải khai báo trước danh sách số trang `range(1, 4)`, cơ chế **Phân trang Tự động (Auto-Pagination)** sẽ tìm thẻ chứa liên kết đến trang kế tiếp (thường là nút **Next** hoặc **›**) trong HTML.

Chương trình sẽ tự động chuyển sang trang mới trong vòng lặp `while`, và dừng lại ngay khi không còn tìm thấy nút Next nữa.

---

## 1. Cơ chế hoạt động của Auto-Pagination

1. **Bắt đầu**: Khởi tạo với `current_url = START_URL`.
2. **Trích xuất kép**: Mỗi khi parse trang danh sách, thư viện `selectolax` thực hiện **2 nhiệm vụ**:
* Trích xuất các URL bài viết/sản phẩm chi tiết.
* Tìm thẻ nút Next (`li.next > a`, `a[rel="next"]`, v.v.) để lấy `href`.


3. **Chuyển tiếp**: Dùng `urllib.parse.urljoin` biến URL tương đối (`page-2.html`) thành URL tuyệt đối.
4. **Điều kiện dừng**:
* Khi `next_page_url` trả về `None` (đã tới trang cuối cùng).
* Hoặc khi chạm ngưỡng an toàn `MAX_PAGES` (tránh vòng lặp vô tận nếu website bị lỗi lặp link).



---

## 2. Script Python hoàn chỉnh (`auto_pagination_crawler.py`)

```python
import asyncio
from typing import Any, Dict, Optional, Set, Tuple
from urllib.parse import urljoin
import httpx
from selectolax.lexbor import LexborHTMLParser

START_URL = "https://books.toscrape.com/catalogue/page-1.html"
MAX_PAGES_SAFETY_LIMIT = 100  # Giới hạn an toàn tránh lặp vô tận


# ==============================================================================
# 1. BÓC TÁCH DỮ LIỆU & TÌM NÚT NEXT PAGE
# ==============================================================================


def parse_list_page_with_next(
    html: str, current_url: str
) -> Tuple[Set[str], Optional[str]]:
    """Phân tích trang danh sách:

    Trả về tuple (Danh sách URL chi tiết, URL trang tiếp theo nếu có)
    """
    tree = LexborHTMLParser(html)
    detail_urls = set()

    # 1. Trích xuất danh sách link chi tiết trên trang hiện tại
    for a_tag in tree.css("h3 > a"):
        href = a_tag.attributes.get("href")
        if href:
            detail_urls.add(urljoin(current_url, href))

    # 2. Tìm nút Next Page (Điều chỉnh Selector tùy theo giao diện từng website)
    # Các selector phổ biến: 'li.next > a', 'a.next', 'a[rel="next"]', '.pagination-next'
    next_node = (
        tree.css_first("li.next > a")
        or tree.css_first('a[rel="next"]')
        or tree.css_first("a.next")
    )

    next_page_url = None
    if next_node:
        next_href = next_node.attributes.get("href")
        if next_href:
            # Chuyển link tương đối thành link tuyệt đối
            next_page_url = urljoin(current_url, next_href)

    return detail_urls, next_page_url


def parse_detail_page(html: str, url: str) -> Dict[str, Any]:
    """Phân tích nội dung trang chi tiết sách"""
    tree = LexborHTMLParser(html)
    title_node = tree.css_first("h1")
    price_node = tree.css_first("p.price_color")

    return {
        "url": url,
        "title": title_node.text(strip=True) if title_node else None,
        "price": price_node.text(strip=True) if price_node else None,
    }


# ==============================================================================
# 2. VÒNG LẬP TỰ ĐỘNG PHÂN TRANG (PAGINATION LOOP)
# ==============================================================================


async def discover_all_detail_urls(
    client: httpx.AsyncClient, start_url: str, max_pages: int = 100
) -> Set[str]:
    """Cào tuần tự các trang danh sách bằng cách lần theo nút Next"""
    current_url = start_url
    all_detail_urls = set()
    page_count = 0

    while current_url and page_count < max_pages:
        page_count += 1
        print(f"📖 [{page_count}] Đang cào trang danh sách: {current_url}")

        try:
            resp = await client.get(current_url)
            resp.raise_for_status()

            # Trích xuất URL chi tiết và URL trang kế tiếp
            detail_urls, next_url = parse_list_page_with_next(
                resp.text, current_url
            )
            all_detail_urls.update(detail_urls)

            print(
                f"   ➔ Lấy được {len(detail_urls)} sản phẩm. ",
                end="",
            )

            # Cập nhật URL cho vòng lặp tiếp theo
            if next_url:
                print(f"Phát hiện trang kế tiếp...")
                current_url = next_url
            else:
                print("HẾT DANH SÁCH (Không tìm thấy nút Next).")
                current_url = None  # Dừng vòng lặp while

        except Exception as e:
            print(f"\n❌ Lỗi tại trang {current_url}: {e}")
            break

    print(
        f"\n🏁 Đã duyệt xong {page_count} trang danh sách. Tổng cộng thu được {len(all_detail_urls)} URL chi tiết.\n"
    )
    return all_detail_urls


# ==============================================================================
# 3. ĐIỀU PHỐI CHÍNH
# ==============================================================================


async def fetch_detail_page(
    client: httpx.AsyncClient, semaphore: asyncio.Semaphore, url: str
) -> Optional[Dict[str, Any]]:
    """Gửi request lấy trang chi tiết song song"""
    async with semaphore:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            return parse_detail_page(resp.text, url)
        except Exception:
            return None


async def main():
    CONCURRENCY_LIMIT = 10
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    async with httpx.AsyncClient(
        headers=headers, timeout=10.0, follow_redirects=True
    ) as client:

        # ----------------------------------------------------------------------
        # BƯỚC 1: TỰ ĐỘNG LẦN THEO NÚT NEXT ĐỂ GOM TẤT CẢ LINK CHI TIẾT
        # ----------------------------------------------------------------------
        all_detail_urls = await discover_all_detail_urls(
            client, START_URL, max_pages=MAX_PAGES_SAFETY_LIMIT
        )

        # ----------------------------------------------------------------------
        # BƯỚC 2: CÀO SONG SONG HÀNG LOẠT TRANG CHI TIẾT THU ĐƯỢC
        # ----------------------------------------------------------------------
        print(
            f"🚀 BẮT ĐẦU CÀO CHI TIẾT: Đang xử lý {len(all_detail_urls)} trang song song..."
        )

        detail_tasks = [
            fetch_detail_page(client, semaphore, url)
            for url in all_detail_urls
        ]
        results = await asyncio.gather(*detail_tasks)

        # Lọc bỏ bản ghi rỗng
        final_data = [item for item in results if item is not None]

        print(
            f"\n🎉 HOÀN THÀNH TẤT CẢ! Đã thu thập thành công {len(final_data)} sản phẩm."
        )


if __name__ == "__main__":
    asyncio.run(main())

```

---

## 3. Các mẹo nâng cao cho nút Phân trang (Pagination Selector)

Tùy vào từng trang web, nút Next Page có thể xuất hiện dưới nhiều dạng HTML khác nhau:

| Dạng nút Next trên giao diện | Cú pháp CSS Selector thích hợp trong Selectolax |
| --- | --- |
| **Thẻ chứa thẻ con** (`<li class="next"><a href="...">Next</a></li>`) | `li.next > a` |
| **Dùng thuộc tính rel** (`<a rel="next" href="...">Next</a>`) | `a[rel="next"]` |
| **Class trực tiếp** (`<a class="pagination-next" href="...">`) | `a.pagination-next` |
| **Dùng icon mũi tên** (`<a class="next_page"><i class="fa fa-angle-right"></i></a>`) | `a.next_page` hoặc `a[aria-label="Next"]` |