Unit test cho lớp Scraper trong Infrastructure Layer nhằm đảm bảo logic bóc tách HTML (parsing) hoạt động đúng mà **không thực hiện HTTP Request thực tế hay mở trình duyệt thật ra internet**.

---

### 1. Unit Test cho BeautifulSoup Scraper (Dùng HTML Fixture + `respx`)

Khi test BeautifulSoup, bạn mock phản hồi HTTP bằng thư viện `respx` (dành cho `httpx`) hoặc `unittest.mock`, sau đó nạp HTML mẫu để kiểm tra tính chính xác của CSS Selector.

#### Code Scraper (`infrastructure/scrapers/bs4_scraper.py`)

```python
from bs4 import BeautifulSoup
import httpx
from application.interfaces.scraper import ExternalStoryScraper, ScrapedChapterDTO

class BeautifulSoupStoryScraper(ExternalStoryScraper):
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def fetch_chapter(self, source_url: str) -> ScrapedChapterDTO:
        response = await self.client.get(source_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        
        title_el = soup.select_one("h1.chapter-title")
        content_el = soup.select_one("div.chapter-content")

        if not title_el or not content_el:
            raise ValueError("Không thể bóc tách cấu trúc HTML của trang")

        return ScrapedChapterDTO(
            title=title_el.get_text(strip=True),
            content_raw=content_el.get_text(strip=True),
            chapter_number=1
        )

```

#### Code Test (`tests/unit/infrastructure/test_bs4_scraper.py`)

```python
import httpx
import pytest
import respx
from infrastructure.scrapers.bs4_scraper import BeautifulSoupStoryScraper

# HTML Giả lập đại diện cho DOM thực tế của website
MOCK_HTML_PAGE = """
<html>
    <body>
        <h1 class="chapter-title">Chương 10: Quy Y</h1>
        <div class="chapter-content">
            <p>Nội dung đoạn 1...</p>
            <p>Nội dung đoạn 2...</p>
        </div>
    </body>
</html>
"""

@pytest.mark.asyncio
@respx.mock
async def test_bs4_scraper_parse_html_success():
    # 1. Arrange: Mock URL trả về HTML mẫu
    target_url = "https://truyen.example/chuong-10"
    respx.get(target_url).mock(
        return_value=httpx.Response(200, html=MOCK_HTML_PAGE)
    )

    async with httpx.AsyncClient() as client:
        scraper = BeautifulSoupStoryScraper(client=client)

        # 2. Act
        result = await scraper.fetch_chapter(target_url)

        # 3. Assert
        assert result.title == "Chương 10: Quy Y"
        assert "Nội dung đoạn 1..." in result.content_raw
        assert "Nội dung đoạn 2..." in result.content_raw


@pytest.mark.asyncio
@respx.mock
async def test_bs4_scraper_raises_error_on_invalid_html():
    # Mock trang web bị thay đổi cấu trúc (thiếu class .chapter-title)
    target_url = "https://truyen.example/broken-page"
    respx.get(target_url).mock(
        return_value=httpx.Response(200, html="<html><body>Bad DOM</body></html>")
    )

    async with httpx.AsyncClient() as client:
        scraper = BeautifulSoupStoryScraper(client=client)

        with pytest.raises(ValueError, match="Không thể bóc tách cấu trúc HTML"):
            await scraper.fetch_chapter(target_url)

```

---

### 2. Unit Test cho Playwright Scraper (Dùng `data:` URI hoặc Intercept)

Đối với các trang render bằng JavaScript, bạn có thể truyền thẳng chuỗi HTML dưới dạng `data:text/html` vào Playwright hoặc chặn request (`page.route`) để nạp HTML giả lập nhanh chóng mà không cần kết nối mạng.

#### Code Scraper (`infrastructure/scrapers/playwright_scraper.py`)

```python
from playwright.async_api import Page
from application.interfaces.scraper import ExternalStoryScraper, ScrapedChapterDTO

class PlaywrightStoryScraper(ExternalStoryScraper):
    def __init__(self, page: Page):
        self.page = page

    async def fetch_chapter(self, source_url: str) -> ScrapedChapterDTO:
        await self.page.goto(source_url)
        
        # Đợi element render qua JS
        await self.page.wait_for_selector("h1.chapter-title")

        title = await self.page.inner_text("h1.chapter-title")
        content = await self.page.inner_text("div.chapter-content")

        return ScrapedChapterDTO(
            title=title.strip(),
            content_raw=content.strip(),
            chapter_number=1
        )

```

#### Code Test (`tests/unit/infrastructure/test_playwright_scraper.py`)

Thư viện `pytest-playwright` cung cấp sẵn fixture `page` khởi chạy Headless Browser hoàn toàn tự động.

```python
import pytest
from playwright.async_api import Page
from infrastructure.scrapers.playwright_scraper import PlaywrightStoryScraper

@pytest.mark.asyncio
async def test_playwright_scraper_extracts_data(page: Page):
    # 1. Arrange: Intercept mọi request đến domain và trả về HTML giả lập
    target_url = "https://spa-truyen.example/chuong-1"
    
    mock_html = """
    <!DOCTYPE html>
    <html>
        <body>
            <script>
                // Giả lập JavaScript render nội dung sau 100ms
                setTimeout(() => {
                    document.body.innerHTML = `
                        <h1 class="chapter-title">Chương 1: Trùng Sinh</h1>
                        <div class="chapter-content">Nội dung render từ JS...</div>
                    `;
                }, 100);
            </script>
        </body>
    </html>
    """
    
    # Chặn request mạng thực tế
    await page.route(target_url, lambda route: route.fulfill(
        status=200, 
        content_type="text/html", 
        body=mock_html
    ))

    scraper = PlaywrightStoryScraper(page=page)

    # 2. Act
    result = await scraper.fetch_chapter(target_url)

    # 3. Assert
    assert result.title == "Chương 1: Trùng Sinh"
    assert result.content_raw == "Nội dung render từ JS..."

```

---

### Quy tắc vàng khi Test Scraper

* **Lưu HTML Fixture ra file `.html**`: Tạo thư mục `tests/fixtures/sample_chapter.html` lưu mã nguồn trang web thực tế thu thập được để dùng lại trong nhiều bài test.
* **Tách biệt Parser và Network**: Nếu muốn tối ưu tốc độ hơn nữa, bạn có thể tách class Scraper thành 2 phần: 1 hàm chuyên tải HTML (Network) và 1 hàm pure-function chuyên parse HTML (`parse(html_str) -> DTO`). Lúc này bạn chỉ cần Unit Test hàm `parse()`.