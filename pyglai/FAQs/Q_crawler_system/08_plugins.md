Version:0.9 StartHTML:0000000105 EndHTML:0000036398 StartFragment:0000000141 EndFragment:0000036362 

Q

plugins/├── plugin_manager.py├── base/│ ├── base_source.py│ ├── http_client.py│ ├── parser_utils.py│ └── exceptions.py└── truyenfull/ ├── manifest.json ├── source.py ├── parser.py ├── selectors.json └── config.py

GLAI

Để hoàn thiện cấu trúc hệ thống plugin linh hoạt và có khả năng mở rộng động (Dynamic Plugin Architecture), chúng ta sẽ tổ chức lại các thư mục. Mục tiêu là biến `plugins/` thành một hệ sinh thái, trong đó `PluginManager` tự động quét, nạp (load) và quản lý vòng đời của các nguồn cào truyện (như `truyenfull`, `tangthuvien`...) dựa trên file `manifest.json`.

Dưới đây là mã nguồn chi tiết, đồng bộ và hoàn chỉnh theo đúng cấu trúc bạn đã định ra.

* * *

**📦 1. TẦNG NỀN TẢNG (plugins/base/)**

**📄 plugins/base/exceptions.py**

Định nghĩa tập trung các ngoại lệ để dễ kiểm soát lỗi phát sinh từ các plugin con.

python
    
    
    class CrawlerException(Exception):
        """Ngoại lệ nền tảng cho hệ thống crawler."""
        pass
    
    class PluginLoadError(CrawlerException):
        """Lỗi xảy ra khi nạp hoặc đăng ký plugin không hợp lệ."""
        pass
    
    class HTTPClientError(CrawlerException):
        """Lỗi xảy ra trong quá trình thực hiện request mạng."""
        pass
    
    class ParserError(CrawlerException):
        """Lỗi bóc tách cú pháp HTML từ giao diện trang web."""
        pass
    

Hãy thận trọng khi sử dụng mã.

**📄 plugins/base/parser_utils.py**

Cung cấp các hàm tiện ích giúp làm sạch dữ liệu text chữ thô sơ, xóa quảng cáo rác chèn lồng trong truyện.

python
    
    
    import re
    from bs4 import BeautifulSoup
    
    class ParserUtils:
        @staticmethod
        def clean_html_content(soup_element: BeautifulSoup, reject_selectors: list[str] | None = None) -> str:
            """Loại bỏ các thẻ rác (script, ads) và lấy nội dung text sạch."""
            if not soup_element:
                return ""
                
            # Thừa kế các selector rác mặc định
            selectors = reject_selectors or ["script", "style", "iframe", ".ads-holder", ".ads-chapter"]
            
            # Tạo bản sao để tránh làm hỏng cấu trúc soup gốc
            element_copy = soup_element
            for selector in selectors:
                for tags in element_copy.select(selector):
                    tags.decompose()
                    
            # Trích xuất văn bản có ngắt dòng sạch sẽ
            text = element_copy.get_text(separator="\n")
            # Chuẩn hóa khoảng trắng và dòng trống liên tiếp
            text = re.sub(r'\n+', '\n', text)
            return text.strip()
    

Hãy thận trọng khi sử dụng mã.

**📄 plugins/base/base_source.py**

Lớp cha trừu tượng (Interface) bắt buộc mọi plugin con (như TruyenFull, TangThuVien) phải tuân thủ đúng thiết kế hàm.

python
    
    
    from abc import ABC, abstractmethod
    from .http_client import HTTPClient
    
    class BaseSource(ABC):
        def __init__(self, client: HTTPClient):
            self.client = client
    
        @abstractmethod
        def crawl_novel(self, novel_slug: str) -> dict:
            """Phương thức bắt buộc các plugin phải cài đặt để cào trọn vẹn thông tin truyện."""
            pass
    

Hãy thận trọng khi sử dụng mã.

_(Lưu ý: File_` _plugins/base/http_client.py_` _giữ nguyên code bọc_` _requests.Session_` _,_`_RateLimiter_` _và_` _RetryPolicy_` _giống như các lượt chat trước)._

* * *

**📦 2. MODULE TRUYỀN FULL (plugins/truyenfull/)**

**📄 plugins/truyenfull/manifest.json**

Khai báo meta-data giúp `PluginManager` nhận diện lớp xử lý chính.

json
    
    
    {
      "plugin_id": "truyenfull",
      "name": "TruyenFull Scraper",
      "version": "1.0.0",
      "entry_point": "source.TruyenFullSource",
      "enabled": true
    }
    

Hãy thận trọng khi sử dụng mã.

**📄 plugins/truyenfull/parser.py**

Sử dụng `ParserUtils` để làm sạch nội dung chương truyện.

python
    
    
    from bs4 import BeautifulSoup
    from plugins.base.parser_utils import ParserUtils
    from .config import SELECTORS
    
    class TruyenFullParser:
        @staticmethod
        def parse_novel_detail(soup: BeautifulSoup) -> dict:
            selectors = SELECTORS["novel_detail"]
            title_tag = soup.select_one(selectors["title"])
            author_tag = soup.select_one(selectors["author"])
            status_tag = soup.select_one(selectors["status"])
            desc_tag = soup.select_one(selectors["description"])
            
            genres = [g.text.strip() for g in soup.select(selectors["genres"])]
            chapters = [{"title": ch.text.strip(), "url": ch.get("href", "")} for ch in soup.select(selectors["chapter_item"])]
                
            return {
                "title": title_tag.text.strip() if title_tag else "Không rõ",
                "author": author_tag.text.strip() if author_tag else "Không rõ",
                "status": status_tag.text.strip() if status_tag else "Không rõ",
                "genres": genres,
                "description": desc_tag.text.strip() if desc_tag else "",
                "chapters": chapters
            }
    
        @staticmethod
        def parse_chapter_detail(soup: BeautifulSoup) -> dict:
            selectors = SELECTORS["chapter_detail"]
            title_tag = soup.select_one(selectors["title"])
            content_tag = soup.select_one(selectors["content"])
            
            # Gọi tiện ích dọn rác HTML ở base
            content_text = ParserUtils.clean_html_content(content_tag)
    
            return {
                "title": title_tag.text.strip() if title_tag else "Không rõ",
                "content": content_text
            }
    
        @staticmethod
        def parse_next_page(soup: BeautifulSoup) -> str | None:
            next_tag = soup.select_one(SELECTORS["pagination"]["next_page"])
            return next_tag.get("href") if next_tag else None
    

Hãy thận trọng khi sử dụng mã.

**📄 plugins/truyenfull/source.py**

Kế thừa `BaseSource` để định hình luồng chạy logic chính.

python
    
    
    from plugins.base.base_source import BaseSource
    from .config import BASE_URL
    from .parser import TruyenFullParser
    
    class TruyenFullSource(BaseSource):
        def crawl_novel(self, novel_slug: str) -> dict:
            if novel_slug.startswith("http"):
                novel_url = novel_slug
            else:
                novel_url = f"{BASE_URL}/{novel_slug.strip('/')}/"
    
            print(f"[TruyenFull] Bắt đầu xử lý: {novel_url}")
            main_response = self.client.get(novel_url)
            novel_data = TruyenFullParser.parse_novel_detail(main_response.soup)
            
            # Quét phân trang thu thập chương (Lược ngắn demo 2 chương)
            chapters_content = []
            for ch_info in novel_data["chapters"][:2]:
                ch_response = self.client.get(ch_info["url"])
                ch_data = TruyenFullParser.parse_chapter_detail(ch_response.soup)
                chapters_content.append({
                    "title": ch_data["title"],
                    "url": ch_info["url"],
                    "content": ch_data["content"]
                })
                
            novel_data["chapters_content"] = chapters_content
            return novel_data
    

Hãy thận trọng khi sử dụng mã.

_(Lưu ý: Các file_` _plugins/truyenfull/selectors.json_` _và_` _plugins/truyenfull/config.py_` _giữ cấu hình giống hệt lượt chat trước)._

* * *

**📦 3. BỘ QUẢN LÝ PLUGIN ĐỘNG (plugins/plugin_manager.py)**

**📄 plugins/plugin_manager.py**

Trái tim điều phối hệ thống. File này sẽ tự động tìm kiếm các thư mục con trong `plugins/`, đọc file `manifest.json`, nạp code động thông qua thư viện `importlib` của Python và đăng ký thực thể nguồn cào vào hệ thống mà không cần import cứng đầu file.

python
    
    
    import os
    import json
    import importlib
    import logging
    from typing import Dict, Type
    from plugins.base.base_source import BaseSource
    from plugins.base.http_client import HTTPClient
    from plugins.base.exceptions import PluginLoadError
    
    logger = logging.getLogger(__name__)
    
    class PluginManager:
        def __init__(self, client: HTTPClient):
            self.client = client
            # Lưu trữ các Class của Plugin đã nạp thành công: {plugin_id: PluginClass}
            self._plugins: Dict[str, Type[BaseSource]] = {}
            self.plugins_dir = os.path.dirname(os.path.abspath(__file__))
    
        def discover_and_load_plugins(self) -> None:
            """Quét toàn bộ thư mục để tìm kiếm và nạp các plugin hợp lệ."""
            logger.info("Bắt đầu quy trình tự động quét hệ thống plugin...")
            
            for item in os.listdir(self.plugins_dir):
                item_path = os.path.join(self.plugins_dir, item)
                
                # Chỉ kiểm tra các thư mục và bỏ qua thư mục cấu hình nền tảng 'base'
                if not os.path.isdir(item_path) or item == "base" or item.startswith("__"):
                    continue
                    
                manifest_path = os.path.join(item_path, "manifest.json")
                if not os.path.exists(manifest_path):
                    logger.warning(f"Bỏ qua thư mục '{item}': Thiếu file manifest.json")
                    continue
    
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        manifest = json.load(f)
    
                    # Kiểm tra trạng thái kích hoạt của plugin
                    if not manifest.get("enabled", True):
                        logger.info(f"Plugin '{manifest.get('name')}' đang ở trạng thái Tắt (disabled).")
                        continue
    
                    plugin_id = manifest["plugin_id"]
                    entry_point = manifest["entry_point"] # Ví dụ: "source.TruyenFullSource"
                    
                    # Tách module và class name từ entry_point
                    module_rel_path, class_name = entry_point.rsplit(".", 1)
                    
                    # Xây dựng đường dẫn import tuyệt đối: plugins.truyenfull.source
                    full_module_path = f"plugins.{plugin_id}.{module_rel_path}"
                    
                    # Nạp động module vào bộ nhớ Python
                    module = importlib.import_module(full_module_path)
                    plugin_class = getattr(module, class_name)
    
                    # Kiểm tra xem lớp nạp được có đúng là con của BaseSource hay không
                    if not issubclass(plugin_class, BaseSource):
                        raise PluginLoadError(f"Class '{class_name}' phải kế thừa từ lớp trừu tượng BaseSource.")
    
                    # Đăng ký thành công vào kho lưu trữ
                    self._plugins[plugin_id] = plugin_class
                    logger.info(f" Thống kê: Nạp thành công Plugin [{plugin_id}] v{manifest.get('version')}")
    
                except Exception as e:
                    logger.error(f"❌ Lỗi nghiêm trọng khi nạp plugin tại thư mục '{item}': {e}")
                    continue
    
        def get_source_instance(self, plugin_id: str) -> BaseSource:
            """Khởi tạo đối tượng xử lý cụ thể từ plugin_id được yêu cầu."""
            if plugin_id not in self._plugins:
                raise PluginLoadError(f"Không tìm thấy hoặc chưa nạp plugin có ID: '{plugin_id}'")
                
            plugin_class = self._plugins[plugin_id]
            # Khởi tạo instance và truyền trực tiếp HTTPClient dùng chung vào
            return plugin_class(client=self.client)
    
        @property
        def available_plugins(self) -> list[str]:
            """Trả về danh sách ID các plugin đang sẵn sàng phục vụ."""
            return list(self._plugins.keys())
    

Hãy thận trọng khi sử dụng mã.

* * *

**🔄 4. CẬP NHẬT TRONG FILE ĐẦU NÃO main.py**

Nhờ cấu trúc `PluginManager` mới, file `main.py` không còn cần import cứng lớp `TruyenFullSource` nữa. Thay vào đó, nó có thể gọi bất kỳ nguồn web nào bằng cấu hình mềm.

python
    
    
    # Cập nhật một phần trong file main.py
    
    from plugins.base.http_client import HTTPClient
    from plugins.plugin_manager import PluginManager
    
    class CrawlerCoordinator:
        def __init__(self):
            # 1. Tạo Client kết nối mạng dùng chung
            self.client = HTTPClient(delay_range=(1.5, 3.0))
            
            # 2. Khởi tạo bộ quản lý Plugin động và quét hệ thống
            self.plugin_manager = PluginManager(client=self.client)
            self.plugin_manager.discover_and_load_plugins()
            
            # Thử in ra màn hình các plugin quét được
            print(f"Các nguồn cào hiện có: {self.plugin_manager.available_plugins}")
    
        def process_task(self, target_website_id: str, slug: str):
            """Ví dụ xử lý tác vụ cào động dựa trên website_id."""
            # Tự động lấy bộ cào tương ứng (Ví dụ target_website_id = "truyenfull")
            scraper = self.plugin_manager.get_source_instance(target_website_id)
            
            # Thực thi tác vụ cào dữ liệu sạch sẽ
            novel_data = scraper.crawl_novel(slug)
            return novel_data
    

Hãy thận trọng khi sử dụng mã.

Hệ thống kiến trúc Plugin này giúp bạn phát triển độc lập cực tốt: Khi cần cào thêm một trang mới (ví dụ `tangthuvien`), bạn chỉ cần copy thư mục `truyenfull`, đổi tên thành `tangthuvien`, sửa lại CSS selector trong file JSON và sửa file `parser.py` mà không phải chỉnh sửa bất kỳ dòng code nào trong lỗi hệ thống (`base`, `database`, `main.py`).

Bạn có muốn tối ưu thêm phần **Đa luồng (Thread Pool)** để `PluginManager` có thể chạy song song nhiều plugin cào nhiều website cùng một lúc không?

