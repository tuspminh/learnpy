Version:0.9 StartHTML:0000000105 EndHTML:0000034385 StartFragment:0000000141 EndFragment:0000034349 

_Q_

 _plugins/├── base/│ ├── base_source.py # Lớp trừu tượng│ ├── http_client.py # HTTP client dùng chung│ ├── parser_utils.py # Hàm tiện ích│ └── exceptions.py│├── truyenfull/│ ├── manifest.json # Thông tin plugin│ ├── source.py # TruyenFullSource│ ├── parser.py # Phân tích HTML│ ├── selectors.json # CSS/XPath selector│ └── config.py│viết từng file cho tôi_

GLAI:

Dưới đây là mã nguồn chi tiết, hoàn chỉnh và sẵn sàng sử dụng cho từng file trong cấu trúc thư mục hệ thống plugin cào truyện (crawler) của bạn.

Hệ thống được thiết kế theo hướng **hướng đối tượng (OOP)** , sử dụng thư viện `httpx` để cào dữ liệu bất đồng bộ (`asyncio`) hiệu quả và `BeautifulSoup` để phân tích cú pháp HTML.

* * *

**I. Thư mục base/ (Cốt lõi chung)**

**1\. plugins/base/exceptions.py**

Định nghĩa các lỗi chuyên biệt để dễ dàng quản lý và bắt lỗi trong quá trình cào dữ liệu.

python
    
    
    class PluginError(Exception):
        """Lỗi cơ bản của hệ thống plugin."""
        pass
    
    class NetworkError(PluginError):
        """Lỗi liên quan đến kết nối mạng hoặc HTTP."""
        pass
    
    class ParseError(PluginError):
        """Lỗi xảy ra khi phân tích cú pháp HTML (DOM thay đổi, v.v.)."""
        pass
    
    class ConfigError(PluginError):
        """Lỗi cấu hình plugin thiếu hoặc sai định dạng."""
        pass
    

Hãy thận trọng khi sử dụng mã.

**2\. plugins/base/parser_utils.py**

Các hàm tiện ích tĩnh giúp xử lý văn bản và tối ưu hóa việc phân tích DOM.

python
    
    
    import re
    from bs4 import BeautifulSoup
    
    def clean_text(text: str) -> str:
        """Xóa khoảng trắng thừa và chuẩn hóa văn bản."""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def clean_html_content(soup_element) -> str:
        """Xóa các thẻ quảng cáo, script và giữ lại định dạng văn bản truyện."""
        if not soup_element:
            return ""
        
        # Xóa các thành phần không mong muốn
        for tag in soup_element(["script", "style", "iframe", "ins", "div.ads"]):
            tag.decompose()
            
        # Chuyển đổi các thẻ ngắt dòng thành xuống dòng chuẩn
        for br in soup_element.find_all("br"):
            br.replace_with("\n")
            
        return soup_element.get_text().strip()
    
    def extract_number(text: str) -> float:
        """Trích xuất số đầu tiên tìm thấy trong chuỗi (ví dụ: 'Chương 123' -> 123)."""
        match = re.search(r'\d+(\.\d+)?', text)
        return float(match.group()) if match else 0.0
    

Hãy thận trọng khi sử dụng mã.

**3\. plugins/base/http_client.py**

Client HTTP bất đồng bộ dùng chung, tích hợp sẵn cơ chế chống chặn (User-Agent giả lập).

python
    
    
    import httpx
    from typing import Dict, Any, Optional
    from plugins.base.exceptions import NetworkError
    
    class HTTPClient:
        def __init__(self, default_headers: Optional[Dict[str, str]] = None):
            self.headers = default_headers or {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7"
            }
    
        async def fetch(self, url: str, params: Optional[Dict[str, Any]] = None) -> str:
            """Gửi yêu cầu GET và trả về nội dung HTML dạng chuỗi."""
            try:
                async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=15.0) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    return response.text
            except httpx.HTTPStatusError as e:
                raise NetworkError(f"HTTP lỗi {e.response.status_code} khi truy cập: {url}")
            except httpx.RequestError as e:
                raise NetworkError(f"Lỗi kết nối mạng mạng: {str(e)}")
    

Hãy thận trọng khi sử dụng mã.

**4\. plugins/base/base_source.py**

Lớp trừu tượng bắt buộc mọi plugin nguồn truyện phải tuân thủ để hệ thống core có thể gọi đồng bộ.

python
    
    
    from abc import ABC, abstractmethod
    from typing import List, Dict, Any
    
    class BaseSource(ABC):
        def __init__(self, manifest: Dict[str, Any], selectors: Dict[str, Any], config: Any):
            self.manifest = manifest
            self.selectors = selectors
            self.config = config
    
        @abstractmethod
        async def search_novels(self, keyword: str, page: int = 1) -> List[Dict[str, Any]]:
            """Tìm kiếm truyện theo từ khóa."""
            pass
    
        @abstractmethod
        async def get_novel_details(self, novel_url: str) -> Dict[str, Any]:
            """Lấy thông tin chi tiết truyện (Tên, tác giả, trạng thái, danh sách chương)."""
            pass
    
        @abstractmethod
        async def get_chapter_content(self, chapter_url: str) -> Dict[str, Any]:
            """Lấy nội dung chi tiết của một chương."""
            pass
    

Hãy thận trọng khi sử dụng mã.

* * *

**II. Thư mục truyenfull/ (Plugin cụ thể)**

**1\. plugins/truyenfull/manifest.json**

File cấu hình khai báo siêu dữ liệu của plugin.

json
    
    
    {
      "id": "vn.truyenfull",
      "name": "TruyenFull",
      "version": "1.0.0",
      "author": "Developer",
      "description": "Plugin cào dữ liệu từ website TruyenFull",
      "base_url": "https://truyenfull.io"
    }
    

Hãy thận trọng khi sử dụng mã.

**2\. plugins/truyenfull/selectors.json**

Tách rời các Selector CSS để nếu website TruyenFull đổi giao diện, bạn chỉ cần sửa file JSON này mà không cần sửa code Python.

json
    
    
    {
      "search": {
        "item": "div.list-truyen div.row",
        "title": "h3.truyen-title a",
        "url": "h3.truyen-title a",
        "author": "span.author",
        "poster": "div.lazyimg"
      },
      "detail": {
        "title": "h3.title",
        "author": "a[itemprop='author']",
        "status": "span.text-success, span.text-primary",
        "description": "div.desc-text",
        "chapter_item": "ul.list-chapter li a"
      },
      "chapter": {
        "title": "a.chapter-title",
        "content": "div.chapter-c"
      }
    }
    

Hãy thận trọng khi sử dụng mã.

**3\. plugins/truyenfull/config.py**

Cấu hình riêng cho môi trường chạy của TruyenFull.

python
    
    
    import os
    from plugins.truyenfull import manifest
    
    class TruyenFullConfig:
        BASE_URL = manifest.get("base_url", "https://truyenfull.io")
        SEARCH_ENDPOINT = f"{BASE_URL}/tim-kiem/"
        
        # Định cấu hình số luồng hoặc độ trễ nếu cần để tránh bị chặn IP
        RATE_LIMIT_DELAY = 1.0 
    

Hãy thận trọng khi sử dụng mã.

**4\. plugins/truyenfull/parser.py**

Nơi bóc tách dữ liệu HTML thô thành dữ liệu cấu trúc sạch bằng BeautifulSoup.

python
    
    
    from bs4 import BeautifulSoup
    from typing import List, Dict, Any
    from plugins.base import parser_utils
    from plugins.base.exceptions import ParseError
    
    class TruyenFullParser:
        def __init__(self, selectors: Dict[str, Any]):
            self.selectors = selectors
    
        def parse_search_results(self, html: str) -> List[Dict[str, Any]]:
            soup = BeautifulSoup(html, "html.parser")
            results = []
            items = soup.select(self.selectors["search"]["item"])
            
            for item in items:
                try:
                    title_el = item.select_one(self.selectors["search"]["title"])
                    if not title_el:
                        continue
                        
                    author_el = item.select_one(self.selectors["search"]["author"])
                    
                    results.append({
                        "title": parser_utils.clean_text(title_el.text),
                        "url": title_el.get("href", ""),
                        "author": parser_utils.clean_text(author_el.text) if author_el else "Ẩn danh"
                    })
                except Exception as e:
                    raise ParseError(f"Lỗi phân tích mục tìm kiếm: {str(e)}")
            return results
    
        def parse_novel_details(self, html: str) -> Dict[str, Any]:
            soup = BeautifulSoup(html, "html.parser")
            try:
                title_el = soup.select_one(self.selectors["detail"]["title"])
                author_el = soup.select_one(self.selectors["detail"]["author"])
                status_el = soup.select_one(self.selectors["detail"]["status"])
                desc_el = soup.select_one(self.selectors["detail"]["description"])
                
                # Lấy danh sách chương xuất hiện trên trang hiện tại
                chapters = []
                chapter_els = soup.select(self.selectors["detail"]["chapter_item"])
                for ch in chapter_els:
                    chapters.append({
                        "chapter_title": parser_utils.clean_text(ch.text),
                        "chapter_url": ch.get("href", "")
                    })
    
                return {
                    "title": parser_utils.clean_text(title_el.text) if title_el else "Không rõ",
                    "author": parser_utils.clean_text(author_el.text) if author_el else "Không rõ",
                    "status": parser_utils.clean_text(status_el.text) if status_el else "Không rõ",
                    "description": parser_utils.clean_html_content(desc_el) if desc_el else "",
                    "chapters": chapters
                }
            except Exception as e:
                raise ParseError(f"Lỗi phân tích chi tiết truyện: {str(e)}")
    
        def parse_chapter_content(self, html: str) -> Dict[str, Any]:
            soup = BeautifulSoup(html, "html.parser")
            try:
                title_el = soup.select_one(self.selectors["chapter"]["title"])
                content_el = soup.select_one(self.selectors["chapter"]["content"])
                
                return {
                    "chapter_title": parser_utils.clean_text(title_el.text) if title_el else "Không có tiêu đề",
                    "content": parser_utils.clean_html_content(content_el) if content_el else "Nội dung trống"
                }
            except Exception as e:
                raise ParseError(f"Lỗi phân tích nội dung chương: {str(e)}")
    

Hãy thận trọng khi sử dụng mã.

**5\. plugins/truyenfull/source.py**

File kết nối mọi thành phần lại với nhau. Nó kế thừa `BaseSource` và điều phối việc tải HTML (qua HTTPClient) và phân tích (qua Parser).

python
    
    
    import json
    import os
    from typing import List, Dict, Any
    from plugins.base.base_source import BaseSource
    from plugins.base.http_client import HTTPClient
    from plugins.truyenfull.parser import TruyenFullParser
    from plugins.truyenfull.config import TruyenFullConfig
    
    class TruyenFullSource(BaseSource):
        def __init__(self):
            # Đọc dữ liệu từ manifest.json và selectors.json nằm cùng thư mục
            current_dir = os.path.dirname(__file__)
            
            with open(os.path.join(current_dir, "manifest.json"), "r", encoding="utf-8") as f:
                manifest = json.load(f)
                
            with open(os.path.join(current_dir, "selectors.json"), "r", encoding="utf-8") as f:
                selectors = json.load(f)
                
            super().__init__(manifest=manifest, selectors=selectors, config=TruyenFullConfig)
            
            self.http_client = HTTPClient()
            self.parser = TruyenFullParser(self.selectors)
    
        async def search_novels(self, keyword: str, page: int = 1) -> List[Dict[str, Any]]:
            params = {"tukhoa": keyword, "page": page}
            html = await self.http_client.fetch(self.config.SEARCH_ENDPOINT, params=params)
            return self.parser.parse_search_results(html)
    
        async def get_novel_details(self, novel_url: str) -> Dict[str, Any]:
            html = await self.http_client.fetch(novel_url)
            return self.parser.parse_novel_details(html)
    
        async def get_chapter_content(self, chapter_url: str) -> Dict[str, Any]:
            html = await self.http_client.fetch(chapter_url)
            return self.parser.parse_chapter_content(html)
    

Hãy thận trọng khi sử dụng mã.

* * *

**💡 Hướng dẫn kiểm tra chạy thử (Ví dụ mẫu)**

Để chạy kiểm tra hệ thống plugin này, bạn tạo một file `main.py` ở **thư mục cha bên ngoài thư mục plugins/** và thực thi đoạn mã sau:

python
    
    
    import asyncio
    from plugins.truyenfull.source import TruyenFullSource
    
    async def test():
        # 1. Khởi tạo plugin
        source = TruyenFullSource()
        print(f"--- Đã nạp thành công Plugin: {source.manifest['name']} ---")
    
        # 2. Thử nghiệm tìm kiếm truyện
        print("\n[Hành động] Đang tìm kiếm truyện 'Đấu Phá Thương Khung'...")
        search_results = await source.search_novels("đấu phá thương khung")
        
        if search_results:
            first_novel = search_results[0]
            print(f"Tìm thấy: {first_novel['title']} | Link: {first_novel['url']}")
            
            # 3. Thử nghiệm lấy chi tiết truyện từ link đầu tiên
            print(f"\n[Hành động] Đang lấy chi tiết truyện từ: {first_novel['url']}...")
            detail = await source.get_novel_details(first_novel['url'])
            print(f"Tên truyện: {detail['title']}")
            print(f"Tác giả: {detail['author']}")
            print(f"Số lượng chương lấy được ở trang 1: {len(detail['chapters'])}")
            
            # 4. Thử nghiệm lấy nội dung chương đầu tiên
            if detail['chapters']:
                first_chapter_url = detail['chapters'][0]['chapter_url']
                print(f"\n[Hành động] Đang lấy nội dung chương từ: {first_chapter_url}...")
                chapter_data = await source.get_chapter_content(first_chapter_url)
                print(f"Tiêu đề chương: {chapter_data['chapter_title']}")
                print(f"Nội dung (50 ký tự đầu): {chapter_data['content'][:50]}...")
        else:
            print("Không tìm thấy kết quả phù hợp.")
    
    if __name__ == "__main__":
        asyncio.run(test())
    

Hãy thận trọng khi sử dụng mã.

Nếu bạn cần mở rộng thêm các tính năng như **tự động chuyển trang danh sách chương (pagination)** hay xử lý bypass nâng cao, hãy cho tôi biết nhé!

