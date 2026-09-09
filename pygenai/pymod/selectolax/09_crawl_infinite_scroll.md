> Hướng dẫn cách cào dữ liệu các trang web dùng Infinite Scroll (cuộn xuống tự tải thêm) hoặc phân trang qua API AJAX.

Khi cào dữ liệu từ các trang web sử dụng **Infinite Scroll** (cuộn vô tận) hoặc **Phân trang AJAX**, phương pháp cào HTML truyền thống sẽ không hoạt động vì dữ liệu mới được tải động bằng JavaScript.

Có **2 chiến lược chính** để giải quyết bài toán này, đi từ tối ưu tốc độ nhất đến phương án dự phòng khi gặp bảo mật cao.

---

## 💡 Tổng quan 2 chiến lược

```text
               ┌─────────────────────────────────────────┐
               │    Phân tích trang bằng F12 DevTools    │
               └────────────────────┬────────────────────┘
                                    │
                     Có bắt được API Request không?
                                    │
               ┌────────────────────┴────────────────────┐
               ▼                                         ▼
            [ CÓ ]                                    [ KHÔNG / BỊ ENCRYPT ]
┌──────────────────────────────┐          ┌──────────────────────────────┐
│  Chiến lược 1: Gọi trực tiếp │          │ Chiến lược 2: Dùng Playwright│
│  API Backend (Nhanh hơn 100x)│          │ Giả lập cuộn trang thật      │
└──────────────────────────────┘          └──────────────────────────────┘

```

---

## 🚀 Chiến lược 1: Bắt và gọi trực tiếp API Backend (Khuyên dùng - Siêu nhanh)

Trình duyệt không tự tạo ra dữ liệu, nó luôn phải gửi 1 request HTTP (AJAX/Fetch) đến máy chủ để lấy dữ liệu mới (thường ở dạng **JSON** hoặc chuỗi HTML). Nếu bạn bắt được API này, bạn không cần phải cuộn trang hay dùng trình duyệt thật!

### Bước 1: Tìm endpoint API bằng F12 DevTools

1. Mở trang web cần cào trên Chrome/Firefox.
2. Nhấn `F12` -> Chọn tab **Network** -> Lọc theo **Fetch/XHR**.
3. Thực hiện cuộn xuống (scroll down) hoặc bấm nút "Tải thêm".
4. Quan sát các request mới xuất hiện. Tìm request trả về dữ liệu danh sách sản phẩm/bài viết (xem tab *Preview* hoặc *Response*).

> **Chú ý các thông số:**
> * **URL Request**: VD: `[https://api.example.com/v1/products?page=2&limit=20](https://api.example.com/v1/products?page=2&limit=20)`
> * **Request Method**: GET hoặc POST.
> * **Headers**: Xem có cần `Authorization`, `X-CSRF-Token`, hoặc `User-Agent` đặc thù không.
> 
> 

### Bước 2: Code giả lập gọi API bằng `httpx` (JSON Response)

Khi API trả về JSON, bạn thậm chí **không cần dùng `selectolax**` vì dữ liệu đã nằm sẵn trong Python Dict!

```python
import asyncio
from typing import Any, Dict, List
import httpx


async def fetch_infinite_scroll_api() -> List[Dict[str, Any]]:
    # URL API bắt được từ DevTools
    api_url = "https://api.example.com/v1/items"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://example.com/products",
        # Thêm token hoặc header đặc thù nếu API yêu cầu
        # "X-Requested-With": "XMLHttpRequest",
    }

    all_products = []
    page = 1
    has_more = True

    async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
        while has_more and page <= 50:  # Giới hạn an toàn 50 trang
            print(f"🔄 Đang tải API trang {page}...")

            params = {
                "page": page,
                "limit": 20,
                # "cursor": next_cursor # Đôi khi API dùng cursor thay vì page
            }

            try:
                resp = await client.get(api_url, params=params)
                resp.raise_for_status()

                data = resp.json()

                # Giả sử JSON trả về dạng: {"data": [...], "has_next": true}
                items = data.get("data", [])
                if not items:
                    print("🛑 Hết dữ liệu.")
                    break

                all_products.extend(items)
                print(f"   ➔ Lấy được {len(items)} mục.")

                # Kiểm tra điều kiện dừng
                has_more = data.get("has_next", False)
                page += 1

                # Delay nhẹ để tránh bị chặn API
                await asyncio.sleep(0.5)

            except Exception as e:
                print(f"❌ Lỗi khi gọi API trang {page}: {e}")
                break

    return all_products


if __name__ == "__main__":
    products = asyncio.run(fetch_infinite_scroll_api())
    print(f"\n🎉 TỔNG CỘNG LẤY ĐƯỢC: {len(products)} sản phẩm.")

```

### Trường hợp API trả về đoạn HTML (HTML Fragment):

Nếu API trả về chuỗi HTML thay vì JSON, bạn kết hợp thêm `selectolax` để parse:

```python
from selectolax.lexbor import LexborHTMLParser

# Parse HTML trả về từ AJAX
tree = LexborHTMLParser(resp.text)
for card in tree.css("div.product-card"):
    # Bóc tách thông tin bình thường
    ...

```

---

## 🛠️ Chiến lược 2: Giả lập cuộn trang bằng Playwright kết hợp Selectolax

Dùng khi:

* API bị mã hóa parameters (Signatures, Hashing Token phức tạp).
* Website chặn bot cực mạnh (Cloudflare / Akamai).

Ta sẽ dùng **Playwright** để cuộn trang lấy toàn bộ DOM HTML, sau đó quăng HTML đó cho **Selectolax** parse với tốc độ cực nhanh.

### Cài đặt Playwright:

```bash
pip install playwright
playwright install chromium

```

### Python Script: Tự động cuộn trang (Auto Scroll)

```python
import asyncio
from playwright.async_api import async_playwright
from selectolax.lexbor import LexborHTMLParser


async def auto_scroll_page(page, max_scrolls: int = 10):
    """Hàm bổ trợ cuộn xuống cuối trang nhiều lần cho đến khi không còn content mới"""
    prev_height = -1

    for i in range(max_scrolls):
        # Cuộn xuống cuối trang
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        # Chờ 1.5 - 2 giây để JavaScript tải thêm content mới
        await page.wait_for_timeout(2000)

        # Tính chiều cao hiện tại của trang
        new_height = await page.evaluate("document.body.scrollHeight")

        print(f"📜 Lần cuộn {i+1}/{max_scrolls} - Chiều cao DOM: {new_height}px")

        # Nếu chiều cao không đổi -> Đã cuộn hết trang
        if new_height == prev_height:
            print("🛑 Đã cuộn tới cuối trang (Không còn dữ liệu mới).")
            break

        prev_height = new_height


async def main():
    target_url = "https://example.com/infinite-scroll-demo"

    async with async_playwright() as p:
        # Khởi tạo trình duyệt headless
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        print(f"🌐 Đang truy cập: {target_url}")
        await page.goto(target_url, wait_until="networkidle")

        # Thực hiện cuộn trang tự động
        await auto_scroll_page(page, max_scrolls=15)

        # ----------------------------------------------------------------------
        # CHUYỂN HTML TỪ PLAYWRIGHT SANG SELECTOLAX ĐỂ PARSE SIÊU NHANH
        # ----------------------------------------------------------------------
        full_html = await page.content()
        await browser.close()

        print("⚡ Đang phân tích HTML bằng Selectolax...")
        tree = LexborHTMLParser(full_html)

        items = []
        for card in tree.css("div.post-item"):
            title = card.css_first("h2")
            items.append(title.text(strip=True) if title else None)

        print(
            f"🎉 Thu thập được {len(items)} mục sau khi cuộn trang hoàn tất!"
        )


if __name__ == "__main__":
    asyncio.run(main())

```

---

## 📊 So sánh 2 phương pháp

| Tiêu chí | Chiến lược 1: Bắt API AJAX | Chiến lược 2: Playwright Scroll |
| --- | --- | --- |
| **Tốc độ** | 🚀 **Siêu nhanh** (Vài mili-giây/request) | 🐢 **Chậm** (Mất vài giây cho mỗi lần cuộn) |
| **Tài nguyên (RAM/CPU)** | 🟢 Cực kỳ nhẹ | 🔴 Tốn RAM (Do mở trình duyệt Chromium) |
| **Độ khó thiết lập** | Cần F12 soi Network API | Dễ hơn (chỉ cần viết script cuộn) |
| **Khả năng vượt WAF** | Trung bình (Dễ bị lộ nếu thiếu Header) | 🟢 Rất cao (Vì là trình duyệt thật) |