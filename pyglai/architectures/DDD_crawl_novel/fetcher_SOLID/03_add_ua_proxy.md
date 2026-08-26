Để tự động thay đổi User-Agent và Proxy cho ứng dụng cào truyện theo chuẩn SOLID, chúng ta áp dụng nguyên lý Open/Closed và Dependency Inversion. Thay vì viết cứng logic đổi proxy/user-agent vào trong HTTP Client, ta sẽ tách chúng thành các service độc lập rồi "tiêm" (inject) vào Fetcher.

Dưới đây là giải pháp hoàn chỉnh sử dụng thư viện `httpx` (hoặc `requests` tương tự).

* * *

## 1\. Thiết kế Interface cho Proxy và User-Agent Providers

Mỗi lớp chỉ làm một nhiệm vụ (Single Responsibility): một lớp chuyên cấp User-Agent, một lớp chuyên cấp Proxy.
    
    
    import random
    from abc import ABC, abstractmethod
    
    class IUserAgentProvider(ABC):
        """Giao thức cấp User-Agent xoay vòng."""
        @abstractmethod
        def get_user_agent(self) -> str:
            pass
    
    class IProxyProvider(ABC):
        """Giao thức cấp Proxy xoay vòng."""
        @abstractmethod
        def get_proxy(self) -> str:
            pass
    

## 2\. Triển khai các bộ xoay vòng dữ liệu (Providers)

Bạn có thể dễ dàng thay đổi danh sách này hoặc nâng cấp lên lấy từ API, database sau này mà không ảnh hưởng đến phần fetcher.
    
    
    class RandomUserAgentProvider(IUserAgentProvider):
        """Tự động xoay vòng ngẫu nhiên User-Agent từ danh sách có sẵn."""
        def __init__(self):
            self._ua_list = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            ]
    
        def get_user_agent(self) -> str:
            return random.choice(self._ua_list)
    
    
    class RotatingProxyProvider(IProxyProvider):
        """Tự động xoay vòng Proxy theo thứ tự (Round Robin)."""
        def __init__(self):
            # Ví dụ danh sách proxy (thay bằng proxy thật của bạn)
            self._proxies = [
                "http://example.com",
                "http://example.com",
                "http://example.com"
            ]
            self._index = 0
    
        def get_proxy(self) -> str:
            if not self._proxies:
                return ""
            proxy = self._proxies[self._index]
            # Xoay vòng chỉ số index
            self._index = (self._index + 1) % len(self._proxies)
            return proxy
    

## 3\. Triển khai Dynamic Fetcher (Thay đổi theo từng Request)

Đối với việc cào truyện, nếu cấu hình Proxy/UA cố định vào `httpx.Client(...)` thì suốt vòng đời của Client đó sẽ không đổi. Để tự động thay đổi trên từng request, ta sẽ gọi các provider ngay bên trong hàm `get`.
    
    
    import httpx
    
    class IFetcher(ABC):
        @abstractmethod
        def get(self, url: str, params: dict = None) -> str:
            pass
    
    class DynamicHttpxFetcher(IFetcher):
        """Fetcher sử dụng HTTPX, tự động đổi UA và Proxy mỗi lần gọi hàm get."""
        def __init__(self, ua_provider: IUserAgentProvider, proxy_provider: IProxyProvider, timeout: float = 10.0):
            self.ua_provider = ua_provider
            self.proxy_provider = proxy_provider
            self.timeout = timeout
    
        def get(self, url: str, params: dict = None) -> str:
            # 1. Lấy UA và Proxy mới cho request này
            current_ua = self.ua_provider.get_user_agent()
            current_proxy = self.proxy_provider.get_proxy()
            
            headers = {"User-Agent": current_ua}
            
            # 2. Khởi tạo mount proxy động cho request hiện tại (HTTPX hỗ trợ truyền proxy qua transport)
            # Sử dụng ngữ cảnh 'with' để đóng client ngay sau khi request xong, tránh rò rỉ kết nối
            proxies = {"all://": current_proxy} if current_proxy else None
            
            print(f"[Fetcher] Requesting with UA: {current_ua[:30]}... | Proxy: {current_proxy}")
            
            with httpx.Client(proxies=proxies, headers=headers, timeout=self.timeout) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                return response.text
    

## 4\. Tầng logic cào truyện và Khởi tạo (Composition Root)

Tầng `ComicFetcher` nhận nhiệm vụ bóc tách dữ liệu hoàn toàn không quan tâm việc hệ thống đang đổi Proxy hay User-Agent như thế nào.
    
    
    class ComicFetcher:
        """Tầng nghiệp vụ cào truyện (Giữ nguyên không đổi)."""
        def __init__(self, fetcher: IFetcher):
            self.fetcher = fetcher
    
        def fetch_chapter(self, chapter_url: str) -> str:
            return self.fetcher.get(chapter_url)
    
    # --- CHẠY THỬ NGHIỆM ---
    if __name__ == "__main__":
        # Khởi tạo các thành phần độc lập
        ua_service = RandomUserAgentProvider()
        proxy_service = RotatingProxyProvider()
        
        # Tiêm các service vào bộ Fetcher động
        dynamic_fetcher = DynamicHttpxFetcher(ua_provider=ua_service, proxy_provider=proxy_service)
        
        # Tiêm Fetcher vào App cào truyện
        comic_app = ComicFetcher(dynamic_fetcher)
        
        # Giả lập cào liên tiếp 3 chương để thấy sự thay đổi Proxy/UA
        urls = [
            "https://httpbin.org",  # Website test trả về thông tin request của bạn
            "https://httpbin.org",
            "https://httpbin.org"
        ]
        
        for i, url in enumerate(urls, 1):
            try:
                print(f"\n--- Đang cào chương {i} ---")
                html = comic_app.fetch_chapter(url)
                # Bạn có thể in html ra để check xem "user-agent" và "origin" (IP proxy) có đổi không
            except Exception as e:
                print(f"Lỗi khi cào chương {i}: {e} (Có thể do proxy giả định không hoạt động)")
    

* * *

## Lợi ích về mặt SOLID của cách làm này:

  * Tính tái sử dụng lớn: Nếu bạn muốn đổi sang lấy proxy từ một API trả phí (như Tinsoft, ProxyFb...), bạn chỉ cần tạo lớp `ApiProxyProvider(IProxyProvider)` và thay vào hàm main. Toàn bộ code `DynamicHttpxFetcher` và `ComicFetcher` không cần sửa một chữ nào.
  * Dễ bảo trì: Logic xử lý lỗi proxy chết, kiểm tra proxy sống/chết sẽ được gom gọn hoàn toàn vào trong lớp `ProxyProvider`.



Nếu bạn muốn, tôi có thể hướng dẫn tiếp cách bắt lỗi Proxy chết (Tự động đổi proxy khác và thử lại) ngay trong Fetcher mà không làm gián đoạn tiến trình cào truyện. Bạn có cần bổ sung phần này không?