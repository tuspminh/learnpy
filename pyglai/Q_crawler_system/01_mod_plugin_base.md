Version:0.9 StartHTML:0000000105 EndHTML:0000037748 StartFragment:0000000141 EndFragment:0000037712 

Q:

tôi muốn làm module này
    
    
    plugins/
    	base/
    		├── http_client.py # API công khai
    		├── session_manager.py # Quản lý requests.Session
    		├── rate_limiter.py # Delay, tốc độ request
    		├── retry_policy.py # Chính sách retry
    		├── proxy_manager.py # Quản lý proxy
    		├── cookie_manager.py # Quản lý cookie
    		├── header_manager.py # User-Agent, Referer...
    		├── downloader.py # Streaming, tải file lớn
    		└── response.py # Wrapper cho Response

GLAI:

Để xây dựng module `plugins/base/` làm nền tảng HTTP Client mạnh mẽ, an toàn và chống bị chặn (anti-bot) cho crawler, chúng ta cần liên kết các thành phần lại với nhau một cách khoa học.

Dưới đây là kiến trúc chi tiết và code mẫu hoàn chỉnh cho từng file trong module của bạn.

* * *

**1\. Phân tích luồng hoạt động**

  * ` HTTPClient` (trong `http_client.py`) là điểm tiếp nhận duy nhất (Facade Pattern).
  * Khi gọi một request, `HTTPClient` sẽ:
    1. Lấy hoặc tạo `requests.Session` từ `SessionManager`.
    2. Áp dụng cấu hình tự động từ `HeaderManager`, `CookieManager`, và `ProxyManager`.
    3. Kiểm soát tần suất gọi qua `RateLimiter` để tránh bị ban IP.
    4. Thực thi request bên trong vòng lặp của `RetryPolicy`.
    5. Trả về một đối tượng `CustomResponse` (từ `response.py`) tiện dụng.



* * *

**2\. Triển khai chi tiết mã nguồn**

**📄 plugins/base/rate_limiter.py**

Kiểm soát khoảng cách giữa các request để không bị coi là tấn công DDOS.

python
    
    
    import time
    import random
    
    class RateLimiter:
        def __init__(self, delay_range: tuple[float, float] = (1.0, 3.0)):
            # Khoảng thời gian delay ngẫu nhiên (min, max) giây
            self.delay_range = delay_range
    
        def wait(self) -> None:
            delay = random.uniform(*self.delay_range)
            time.sleep(delay)
    

Hãy thận trọng khi sử dụng mã.

**📄 plugins/base/retry_policy.py**

Tự động thử lại khi gặp lỗi mạng hoặc lỗi Server (5xx).

python
    
    
    import time
    import logging
    from typing import Callable, Any
    import requests
    
    logger = logging.getLogger(__name__)
    
    class RetryPolicy:
        def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
            self.max_retries = max_retries
            self.backoff_factor = backoff_factor
    
        def execute(self, func: Callable[..., requests.Response], *args: Any, **kwargs: Any) -> requests.Response:
            retries = 0
            while retries <= self.max_retries:
                try:
                    response = func(*args, **kwargs)
                    # Nếu gặp lỗi phía Server, ném lỗi để nhảy vào nhánh except phục vụ retry
                    if 500 <= response.status_code < 600:
                        response.raise_for_status()
                    return response
                except (requests.RequestException, requests.HTTPError) as e:
                    retries += 1
                    if retries > self.max_retries:
                        logger.error(f"Đã thử lại tối đa {self.max_retries} lần nhưng vẫn thất bại: {e}")
                        raise e
                    
                    sleep_time = self.backoff_factor ** retries
                    logger.warning(f"Lỗi request ({e}). Đang thử lại lần {retries}/{self.max_retries} sau {sleep_time}s...")
                    time.sleep(sleep_time)
            raise requests.RequestException("Không thể thực hiện request.")
    

Hãy thận trọng khi sử dụng mã.

**📄 plugins/base/proxy_manager.py**

Xoay tua (rotate) proxy để bypass giới hạn IP.

python
    
    
    import random
    
    class ProxyManager:
        def __init__(self, proxies: list[str] | None = None):
            # Định dạng proxy chuẩn: ["http://user:pass@ip:port", ...]
            self.proxies = proxies or []
    
        def get_proxy_dict(self) -> dict[str, str] | None:
            if not self.proxies:
                return None
            proxy = random.choice(self.proxies)
            return {"http": proxy, "https": proxy}
    

Hãy thận trọng khi sử dụng mã.

**📄 plugins/base/cookie_manager.py**

Quản lý và đồng bộ Session Cookie.

python
    
    
    import requests
    
    class CookieManager:
        def __init__(self, initial_cookies: dict[str, str] | None = None):
            self.cookies = initial_cookies or {}
    
        def apply_to_session(self, session: requests.Session) -> None:
            if self.cookies:
                session.cookies.update(self.cookies)
    
        def extract_from_response(self, response: requests.Response) -> None:
            # Cập nhật ngược lại cookies mới nhận được từ server vào manager
            self.cookies.update(response.cookies.get_dict())
    

Hãy thận trọng khi sử dụng mã.

**📄 plugins/base/header_manager.py**

Giả lập trình duyệt bằng cách xoay tua User-Agent và cấu hình Header động.

python
    
    
    import random
    
    class HeaderManager:
        USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        ]
    
        def __init__(self, extra_headers: dict[str, str] | None = None):
            self.extra_headers = extra_headers or {}
    
        def generate(self, url: str | None = None) -> dict[str, str]:
            headers = {
                "User-Agent": random.choice(self.USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            }
            if url:
                headers["Referer"] = url
            headers.update(self.extra_headers)
            return headers
    

Hãy thận trọng khi sử dụng mã.

**📄 plugins/base/session_manager.py**

Tạo và cấu hình Pool cho các `requests.Session`.

python
    
    
    import requests
    
    class SessionManager:
        def __init__(self):
            self._session = requests.Session()
    
        def get_session(self) -> requests.Session:
            return self._session
    
        def close(self) -> None:
            self._session.close()
    

Hãy thận trọng khi sử dụng mã.

**📄 plugins/base/response.py**

Bọc lại (Wrapper) đối tượng `requests.Response` thô nhằm tích hợp sẵn các bộ Parser tiện dụng như BeautifulSoup hoặc JSON để mã nguồn tầng trên ngắn gọn hơn.

python
    
    
    import requests
    from bs4 import BeautifulSoup
    
    class CustomResponse:
        def __init__(self, raw_response: requests.Response):
            self.raw = raw_response
            self.status_code = raw_response.status_code
            self.text = raw_response.text
    
        @property
        def soup(self) -> BeautifulSoup:
            # Tự động parse HTML bằng BeautifulSoup khi gọi .soup
            return BeautifulSoup(self.text, "html.parser")
    
        def json(self) -> dict:
            return self.raw.json()
    

Hãy thận trọng khi sử dụng mã.

**📄 plugins/base/downloader.py**

Xử lý chuyên biệt cho tác vụ streaming và tải các file dung lượng lớn (ảnh truyện, file ebook).

python
    
    
    import requests
    from typing import Callable
    
    class Downloader:
        def __init__(self, session: requests.Session):
            self.session = session
    
        def download_file(self, url: str, save_path: str, chunk_size: int = 8192, callback: Callable[[int], None] | None = None) -> None:
            with self.session.get(url, stream=True) as r:
                r.raise_for_status()
                with open(save_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            if callback:
                                callback(len(chunk)) # Gọi callback để cập nhật thanh tiến trình (progress bar) nếu cần
    

Hãy thận trọng khi sử dụng mã.

**📄 plugins/base/http_client.py**

Bộ não trung tâm kết nối toàn bộ hệ thống lại với nhau.

python
    
    
    import requests
    from .session_manager import SessionManager
    from .rate_limiter import RateLimiter
    from .retry_policy import RetryPolicy
    from .proxy_manager import ProxyManager
    from .cookie_manager import CookieManager
    from .header_manager import HeaderManager
    from .response import CustomResponse
    from .downloader import Downloader
    
    class HTTPClient:
        def __init__(
            self,
            proxies: list[str] | None = None,
            delay_range: tuple[float, float] = (1.0, 2.5),
            max_retries: int = 3
        ):
            self.session_mgr = SessionManager()
            self.rate_limiter = RateLimiter(delay_range)
            self.retry_policy = RetryPolicy(max_retries)
            self.proxy_mgr = ProxyManager(proxies)
            self.cookie_mgr = CookieManager()
            self.header_mgr = HeaderManager()
            
            # Tiện ích tải file
            self.downloader = Downloader(self.session_mgr.get_session())
    
        def request(self, method: str, url: str, **kwargs) -> CustomResponse:
            session = self.session_mgr.get_session()
            
            # 1. Đắp thêm cấu hình tự động bảo mật chống chống bot
            kwargs["headers"] = self.header_mgr.generate(url=kwargs.get("headers", {}).get("Referer"))
            
            proxy_dict = self.proxy_mgr.get_proxy_dict()
            if proxy_dict:
                kwargs["proxies"] = proxy_dict
                
            self.cookie_mgr.apply_to_session(session)
    
            # 2. Thực thi giãn cách thời gian tránh bị ăn block
            self.rate_limiter.wait()
    
            # 3. Chạy hàm request bọc trong chính sách Retry phòng lỗi mạng
            raw_response = self.retry_policy.execute(session.request, method, url, **kwargs)
    
            # 4. Trích xuất đồng bộ ngược lại cookie
            self.cookie_mgr.extract_from_response(raw_response)
    
            return CustomResponse(raw_response)
    
        def get(self, url: str, **kwargs) -> CustomResponse:
            return self.request("GET", url, **kwargs)
    
        def post(self, url: str, **kwargs) -> CustomResponse:
            return self.request("POST", url, **kwargs)
    
        def close(self) -> None:
            self.session_mgr.close()
    

Hãy thận trọng khi sử dụng mã.

* * *

**3\. Hướng dẫn sử dụng thử nghiệm (Ở thư mục gốc dự án)**

Tạo một file test ngoài thư mục `plugins` để chạy thử nghiệm:

python
    
    
    # test_client.py
    from plugins.base.http_client import HTTPClient
    
    # Khởi tạo client 
    client = HTTPClient(delay_range=(1.0, 2.0), max_retries=2)
    
    try:
        # 1. Test request GET thông thường và dùng BeautifulSoup tích hợp sẵn
        print("--- Thử nghiệm truy cập TruyenFull ---")
        response = client.get("https://truyenfull.io") # Đổi thành domain truyện bạn cần cào
        print(f"Status Code: {response.status_code}")
        
        # Lấy thử thẻ tiêu đề của trang web bằng .soup cực kỳ tiện lợi
        title = response.soup.title.text if response.soup.title else "Không có title"
        print(f"Tiêu đề trang: {title}\n")
        
        # 2. Test Downloader tải file lớn / ảnh
        print("--- Thử nghiệm tải file ---")
        client.downloader.download_file(
            url="https://httpbin.org", 
            save_path="test_image.png"
        )
        print("Tải ảnh thành công thành file 'test_image.png'!")
    
    finally:
        # Đóng session khi hoàn tất
        client.close()
    

Hãy thận trọng khi sử dụng mã.

Để tiếp tục hoàn thiện, bạn có muốn tích hợp thêm bộ **giải mã Captcha** hoặc cấu hình **tự động Fake IP bằng Proxy dcom** vào hệ thống này không?

