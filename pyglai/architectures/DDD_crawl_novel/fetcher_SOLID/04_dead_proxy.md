Để tự động đổi proxy khác và thử lại khi gặp lỗi proxy chết (hoặc lỗi mạng), chúng ta sẽ áp dụng mẫu thiết kế Decorator hoặc nâng cấp trực tiếp trong `DynamicHttpxFetcher`.

Cách làm này tuân thủ nghiêm ngặt nguyên lý Single Responsibility (S) và Open/Closed (O): Logic thử lại và xử lý proxy chết nằm trọn trong bộ Fetcher, còn tầng nghiệp vụ `ComicFetcher` hoàn toàn không hề hay biết, nó chỉ cần gọi lệnh và nhận về dữ liệu sạch.

Dưới đây là mã nguồn nâng cấp hoàn chỉnh:

* * *

## 1\. Nâng cấp Interface cho Proxy Provider

Để xử lý proxy chết, lớp cung cấp proxy cần biết khi nào một proxy bị lỗi để loại bỏ hoặc đánh dấu lỗi nhằm tránh cấp lại proxy đó trong các request sau.
    
    
    from abc import ABC, abstractmethod
    
    class IUserAgentProvider(ABC):
        @abstractmethod
        def get_user_agent(self) -> str:
            pass
    
    class IProxyProvider(ABC):
        @abstractmethod
        def get_proxy(self) -> str:
            pass
    
        @abstractmethod
        def report_dead_proxy(self, proxy: str) -> None:
            """Đánh dấu proxy đã chết để không sử dụng lại."""
            pass
    

## 2\. Triển khai Proxy Provider có khả năng tự dọn dẹp
    
    
    class RotatingProxyProvider(IProxyProvider):
        """Bộ xoay vòng proxy có tính năng tự động loại bỏ proxy chết."""
        def __init__(self):
            # Ví dụ danh sách proxy danh bạ ban đầu
            self._proxies = [
                "http://example.com",
                "http://example.com",
                "http://example.com"
            ]
            self._index = 0
    
        def get_proxy(self) -> str:
            if not self._proxies:
                return ""  # Trả về chuỗi rỗng nếu hết sạch proxy (sẽ chạy IP mạng gốc)
            
            proxy = self._proxies[self._index]
            self._index = (self._index + 1) % len(self._proxies)
            return proxy
    
        def report_dead_proxy(self, proxy: str) -> None:
            if proxy in self._proxies:
                self._proxies.remove(proxy)
                print(f"[Proxy Service] ❌ Đã xóa proxy lỗi: {proxy}. Còn lại {len(self._proxies)} proxy.")
                # Reset lại index tránh lỗi chỉ mục vượt quá độ dài mảng mới
                if self._proxies:
                    self._index = self._index % len(self._proxies)
    

_(Bộ User-Agent giữ nguyên như cũ, không cần thay đổi)_
    
    
     import random
    
    class RandomUserAgentProvider(IUserAgentProvider):
        def __init__(self):
            self._ua_list = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
            ]
        def get_user_agent(self) -> str:
            return random.choice(self._ua_list)
    

## 3\. Khởi tạo Fetcher thông minh (Tự động đổi proxy & Retry)

Bộ Fetcher này sẽ bao bọc lệnh gọi mạng trong một vòng lặp `for` theo số lần cấu hình. Nếu gặp lỗi kết nối (thường do proxy sập), nó sẽ báo cáo proxy chết, lấy proxy mới, và tự động thử lại.
    
    
    import httpx
    
    class IFetcher(ABC):
        @abstractmethod
        def get(self, url: str, params: dict = None) -> str:
            pass
    
    class ResilientHttpxFetcher(IFetcher):
        """Fetcher thông minh: Tự động đổi UA/Proxy, phát hiện proxy chết và tự động cào lại."""
        def __init__(self, ua_provider: IUserAgentProvider, proxy_provider: IProxyProvider, max_retries: int = 3, timeout: float = 5.0):
            self.ua_provider = ua_provider
            self.proxy_provider = proxy_provider
            self.max_retries = max_retries
            self.timeout = timeout
    
        def get(self, url: str, params: dict = None) -> str:
            for attempt in range(1, self.max_retries + 1):
                current_ua = self.ua_provider.get_user_agent()
                current_proxy = self.proxy_provider.get_proxy()
                
                headers = {"User-Agent": current_ua}
                proxies = {"all://": current_proxy} if current_proxy else None
                
                print(f"[Fetcher] Thử lần {attempt}/{self.max_retries} | UA: {current_ua[:20]}... | Proxy: {current_proxy or 'IP Gốc'}")
                
                try:
                    # Thiết lập vòng đời client ngắn hạn cho từng request để đổi proxy triệt để
                    with httpx.Client(proxies=proxies, headers=headers, timeout=self.timeout) as client:
                        response = client.get(url, params=params)
                        response.raise_for_status()
                        return response.text  # Thành công -> Trả kết quả ngay lập tức
                        
                except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ProxyError) as net_err:
                    print(f"[Fetcher] ⚠️ Lỗi kết nối mạng/Proxy ở lần thử {attempt}: {type(net_err).__name__}")
                    if current_proxy:
                        # Báo cáo lên hệ thống quản lý để đào thải proxy lỗi này
                        self.proxy_provider.report_dead_proxy(current_proxy)
                        
                except httpx.HTTPStatusError as http_err:
                    # Lỗi HTTP như 403 Forbidden, 502 Bad Gateway cũng có thể do proxy bị block
                    print(f"[Fetcher] ⚠️ Lỗi HTTP {http_err.response.status_code} ở lần thử {attempt}")
                    if http_err.response.status_code in [403, 429, 502, 503, 504] and current_proxy:
                        self.proxy_provider.report_dead_proxy(current_proxy)
                
                except Exception as e:
                    print(f"[Fetcher] ⚠️ Gặp lỗi không xác định: {e}")
    
            # Nếu đi hết số lần vòng lặp mà không return được dữ liệu
            raise RuntimeError(f"❌ Thất bại hoàn toàn sau {self.max_retries} lần thử đổi proxy.")
    

## 4\. Kiểm nghiệm thực tế (Composition Root)

Tầng nghiệp vụ `ComicFetcher` của bạn được giữ nguyên vẹn 100%:
    
    
    class ComicFetcher:
        def __init__(self, fetcher: IFetcher):
            self.fetcher = fetcher
    
        def fetch_chapter(self, chapter_url: str) -> str:
            return self.fetcher.get(chapter_url)
    
    # --- CHẠY THỬ NGHIỆM GIẢ LẬP LỖI ---
    if __name__ == "__main__":
        ua_service = RandomUserAgentProvider()
        proxy_service = RotatingProxyProvider()
        
        # Khởi tạo Fetcher tự sửa lỗi với tối đa 3 lần thử lại
        smart_fetcher = ResilientHttpxFetcher(
            ua_provider=ua_service, 
            proxy_provider=proxy_service, 
            max_retries=3,
            timeout=3.0
        )
        
        comic_app = ComicFetcher(smart_fetcher)
        
        # Test thử với một link thực tế. 
        # Do danh sách proxy ở trên là "giả định" nên chắc chắn chúng sẽ lỗi.
        # Bạn sẽ thấy hệ thống tự động xóa từng proxy lỗi và thử lại cho đến khi hết lượt hoặc thành công.
        try:
            print("--- BẮT ĐẦU CÀO TRUYỆN ---")
            html_data = comic_app.fetch_chapter("https://httpbin.org")
            print("🎉 Kết quả: Cào thành công!")
        except Exception as e:
            print(f"\n⚡ Kết quả cuối cùng từ App: {e}")
    

* * *

## Kiến trúc này giúp ích gì cho dự án lớn?

  1. Dễ nâng cấp nguồn Proxy: Nếu sau này bạn không dùng danh sách Proxy cứng nữa mà mua Proxy từ các bên dịch vụ cung cấp API (họ bắt gọi URL để lấy proxy mới), bạn chỉ việc tạo lớp `ApiProxyProvider` kế thừa từ `IProxyProvider`. Toàn bộ cơ chế Retry và xóa proxy chết của bộ `ResilientHttpxFetcher` vẫn hoạt động hoàn hảo mà không cần viết lại.
  2. Tách biệt kiểm thử (Testability): Bạn có thể dễ dàng viết Unit Test để kiểm tra xem hệ thống có thực sự xóa proxy khi lỗi kết nối hay không bằng cách đưa vào một cấu hình giả lập (Mock), giúp kiểm soát chất lượng mã nguồn cực tốt.



Bạn có muốn tích hợp thêm bộ Giới hạn tốc độ (Rate Limiting / Delay ngẫu nhiên giữa các request) để tránh bị các web truyện cấu hình anti-bot khóa IP vĩnh viễn không?