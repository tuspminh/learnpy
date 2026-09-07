Dưới đây là kiến trúc và mã nguồn triển khai HTTP Client Manager / Session cho ứng dụng crawl truyện chữ bằng Python, được thiết kế chuẩn theo nguyên lý Clean Architecture và Domain-Driven Design (DDD).

Trong bối cảnh crawl truyện, "HTTP Session" đóng vai trò là một Infrastructure Service (hoặc Gateway) giúp Domain gửi yêu cầu tải nội dung trang web (chương truyện, danh sách truyện) mà không cần quan tâm đến chi tiết kỹ thuật bên dưới (Proxy, User-Agent, Rate-limiting, Retry).

* * *

## 1\. Cấu trúc thư mục (Clean & DDD)
    
    
    src/
    │
    ├── domain/                  # Lớp Domain (Chứa Nghiệp vụ lõi, Độc lập hoàn toàn)
    │   └── crawler/
    │       └── gateways.py      # Định nghĩa Interface (Port) cho HTTP Client
    │
    ├── infrastructure/          # Lớp Hạ tầng (Chi tiết công nghệ: HTTP, DB, Thư viện)
    │   └── http/
    │       ├── client.py        # Triển khai Interface bằng HTTPX/Requests (Adapter)
    │       └── session_pool.py  # Quản lý xoay vòng Session, Cookie, Proxy, User-Agent
    │
    └── main.py                  # Entry Point (DI / Khởi tạo và chạy ứng dụng)
    

* * *

## 2\. Triển khai Mã nguồn

Chúng ta sẽ sử dụng thư viện `httpx` (hoặc `requests`) cho phần hạ tầng. Ở đây ưu tiên `httpx` vì nó hỗ trợ cả đồng bộ và bất đồng bộ (async), rất phù hợp cho crawler hiệu năng cao.

## Lớp Domain (`domain/crawler/gateways.py`)

Lớp này định nghĩa hợp đồng (Interface). Domain chỉ biết "Tôi cần một thực thể có khả năng fetch HTML", hoàn toàn không phụ thuộc vào `httpx` hay `requests`.
    
    
    from abc import ABC, abstractmethod
    from typing import Dict, Optional
    
    class BaseHttpClient(ABC):
        """Port: Interface cho HTTP Client mà Domain Core sẽ tương tác."""
        
        @abstractmethod
        def fetch_html(self, url: str, headers: Optional[Dict[str, str]] = None) -> str:
            """Lấy mã nguồn HTML từ một URL."""
            pass
    
        @abstractmethod
        def close(self) -> None:
            """Đóng session khi hoàn thành."""
            pass
    

## Lớp Infrastructure (`infrastructure/http/session_pool.py`)

Thành phần bổ trợ quản lý cấu hình "sạch" cho HTTP Client: Xoay vòng User-Agent và quản lý Proxy để tránh bị chặn khi crawl truyện.
    
    
    import random
    from typing import List, Optional
    
    class SessionConfigPool:
        """Quản lý danh sách User-Agents và Proxies phục vụ chống chặn (Anti-bot)."""
        
        def __init__(self, proxies: Optional[List[str]] = None):
            self._user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
                "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
            ]
            self._proxies = proxies or []
    
        def get_random_user_agent(self) -> str:
            return random.choice(self._user_agents)
    
        def get_random_proxy(self) -> Optional[str]:
            if not self._proxies:
                return None
            return random.choice(self._proxies)
    

## Lớp Infrastructure (`infrastructure/http/client.py`)

Triển khai chi tiết Client sử dụng `httpx.Client`. Nó chịu trách nhiệm tự động gán Session Cookie, thiết lập Retry khi gặp lỗi mạng, và xử lý Timeout.
    
    
    import httpx
    from typing import Dict, Optional
    from domain.crawler.gateways import BaseHttpClient
    from infrastructure.http.session_pool import SessionConfigPool
    
    class ManagedHttpClient(BaseHttpClient):
        """Adapter: Triển khai cụ thể HTTP Client bằng thư viện HTTPX."""
        
        def __init__(self, config_pool: SessionConfigPool, timeout_seconds: int = 15):
            self.config_pool = config_pool
            
            # Khởi tạo HTTPX Session (giữ cookie, connection pool tự động)
            # Thiết lập các cơ chế transport như tự động retry khi gặp lỗi mạng (503, 502...)
            transport = httpx.HTTPTransport(retries=3) 
            
            proxy = self.config_pool.get_random_proxy()
            self._session = httpx.Client(
                transport=transport,
                proxy=proxy,
                timeout=httpx.Timeout(timeout_seconds),
                follow_redirects=True
            )
            
            # Thiết lập base headers mặc định cho session
            self._session.headers.update({
                "User-Agent": self.config_pool.get_random_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            })
    
        def fetch_html(self, url: str, headers: Optional[Dict[str, str]] = None) -> str:
            """Thực thi request lấy HTML, tự động handle lỗi cơ bản."""
            try:
                # Xoay vòng nhẹ User-Agent cho mỗi request cụ thể nếu cần tăng tính ngẫu nhiên
                req_headers = headers or {}
                if "User-Agent" not in req_headers:
                    req_headers["User-Agent"] = self.config_pool.get_random_user_agent()
                    
                response = self._session.get(url, headers=req_headers)
                
                # Kiểm tra lỗi HTTP (4xx, 5xx) và raise Exception tương ứng
                response.raise_for_status() 
                return response.text
                
            except httpx.HTTPStatusError as e:
                # Ở đây bạn có thể log lỗi hoặc chuyển đổi thành Domain Exception phù hợp
                print(f"[HTTP Error] Đã xảy ra lỗi mã nguồn từ trang truyện: {e.response.status_code} tại {url}")
                raise e
            except httpx.RequestError as e:
                print(f"[Network Error] Không thể kết nối tới server truyện: {e}")
                raise e
    
        def close(self) -> None:
            self._session.close()
            
        def __enter__(self):
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.close()
    

* * *

## 3\. Cách Sử dụng (Dependency Injection tại Main)

Tại tệp chạy chính, bạn thực hiện lắp ghép (Inject) Infrastructure Client vào UseCase hoặc Service của Domain để sử dụng.
    
    
    # main.py
    from infrastructure.http.session_pool import SessionConfigPool
    from infrastructure.http.client import ManagedHttpClient
    from domain.crawler.gateways import BaseHttpClient
    
    # Giả lập một Service thuộc Domain nhận Client để cào dữ liệu chương truyện
    class ChapterCrawlerService:
        def __init__(self, http_client: BaseHttpClient):
            self.http_client = http_client  # Nhận interface, không nhận class cụ thể
    
        def crawl_chapter_content(self, url: str) -> str:
            html_content = self.http_client.fetch_html(url)
            # Thực hiện bóc tách (parse) HTML bằng BeautifulSoup hoặc Selector tại đây...
            return f"Dữ liệu thô cào được từ {url} (Độ dài: {len(html_content)} ký tự)"
    
    
    if __name__ == "__main__":
        # 1. Khởi tạo cấu hình hạ tầng
        proxies_list = []  # Thêm proxy dạng 'http://user:pass@ip:port' nếu có
        config_pool = SessionConfigPool(proxies=proxies_list)
        
        # 2. Tạo Http Client Manager/Session chịu trách nhiệm kết nối
        # Sử dụng context manager (with) để đảm bảo session đóng chuẩn xác sau khi chạy xong
        with ManagedHttpClient(config_pool=config_pool) as http_client:
            
            # 3. Inject Client vào Domain Service
            crawler_service = ChapterCrawlerService(http_client=http_client)
            
            # 4. Chạy crawler
            target_url = "https://example-truyen-chu.com"
            try:
                result = crawler_service.crawl_chapter_content(target_url)
                print("[Thành công]", result)
            except Exception as e:
                print("[Thất bại] Lỗi tiến trình cào truyện:", e)
    

## 💡 Các điểm chuẩn DDD & Clean Architecture đạt được:

  1. Tính độc lập của Domain: Lớp `ChapterCrawlerService` chỉ tương tác với interface `BaseHttpClient`. Nếu sau này bạn muốn đổi sang dùng thư viện `requests`, `aiohttp` hoặc giả lập trình duyệt bằng `Selenium/Playwright`, bạn chỉ cần viết một Adapter mới ở lớp `infrastructure` mà không cần sửa đổi một dòng code nào trong logic xử lý truyện của `domain`.
  2. Quản lý Session thông minh (Manager): `ManagedHttpClient` bao gói (encapsulate) vòng đời của kết nối giúp tận dụng cơ chế _Connection Pooling_ của `httpx`, tự giữ lại Session Cookie của trang truyện qua các request liên tiếp, giả lập hành vi đọc truyện của người dùng thật một cách tự nhiên.



Để hoàn thiện hệ thống này, bạn có muốn thiết kế thêm:

  *   * Triển khai Client theo cơ chế Bất đồng bộ (Asyncio) để cào hàng loạt chương truyện cùng lúc?
  * Thiết kế Domain Model (Entities/Value Objects) chuẩn cho một `Truyện` và `Chương` không?
  *