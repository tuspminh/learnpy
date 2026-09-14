Dưới đây là boilerplate code sử dụng `httpx` (Synchronous) được thiết kế đúng theo các yêu cầu của bạn: Xoay vòng Proxy/User-Agent, tự động loại bỏ proxy lỗi, xử lý logic retry hoàn toàn ở tầng Application (vòng lặp code) mà không can thiệp vào tầng `HTTPTransport`.
    
    
    import time
    import random
    import httpx
    from typing import List, Optional
    
    # Danh sách User-Agents để xoay vòng tránh bị detect
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1"
    ]
    
    class SyncStoryFetcher:
        def __init__(self, proxy_list: List[str]):
            """
            proxy_list format: [
                "http://username:password@ip:port",
                "http://ip:port"
            ]
            """
            self.raw_proxies = proxy_list
            self.active_proxies = proxy_list.copy()  # Danh sách proxy sống, sẽ bị loại bỏ dần nếu lỗi
    
        def _get_headers(self) -> dict:
            """Tạo ngẫu nhiên Headers và User-Agent cho mỗi request riêng biệt"""
            return {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://google.com",
            }
    
        def fetch_page(self, url: str, max_retries: int = 5) -> Optional[str]:
            """
            Fetch nội dung trang truyện chữ.
            Retry tầng Application: Sử dụng vòng lặp để đổi proxy và gập lỗi kết nối.
            """
            for attempt in range(1, max_retries + 1):
                # Nếu danh sách active trống, nạp lại từ danh sách gốc để duy trì mạch chạy
                if not self.active_proxies:
                    print("⚠️ Tất cả proxy trong list đã cạn. Nạp lại danh sách gốc...")
                    self.active_proxies = self.raw_proxies.copy()
                    if not self.active_proxies:
                        print("❌ Danh sách cấu hình ban đầu trống. Không thể crawl.")
                        return None
    
                # 1. Rotator: Chọn ngẫu nhiên một proxy từ các proxy còn sống
                current_proxy = random.choice(self.active_proxies)
                
                print(f"🔄 [Lần thử {attempt}/{max_retries}] Đang fetch bằng proxy: {current_proxy}")
    
                try:
                    # Khởi tạo Client đồng bộ với proxy và headers mới cho từng request
                    # Không cấu hình retry ở Transport để kiểm soát lỗi hoàn toàn ở đây
                    with httpx.Client(
                        proxies=current_proxy,
                        headers=self._get_headers(),
                        timeout=10.0,
                        follow_redirects=True
                    ) as client:
                        
                        response = client.get(url)
                        
                        # Kiểm tra HTTP Status Code (Application-level check)
                        if response.status_code == 200:
                            return response.text
                        
                        # Trường hợp bị chặn bởi Anti-bot (Cloudflare 403, Rate Limit 429)
                        elif response.status_code in:
                            print(f"🚫 Proxy bị chặn (HTTP {response.status_code}). Tiến hành loại bỏ proxy này.")
                            if current_proxy in self.active_proxies:
                                self.active_proxies.remove(current_proxy)
                        else:
                            print(f"⚠️ Nhận HTTP {response.status_code}. Thử lại với proxy khác.")
    
                except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ProxyError) as e:
                    # Bắt toàn bộ lỗi kết nối mạng/proxy tại tầng ứng dụng
                    print(f"❌ Lỗi mạng/Proxy ({type(e).__name__}). Tiến hành loại bỏ khỏi danh sách active.")
                    if current_proxy in self.active_proxies:
                        self.active_proxies.remove(current_proxy)
                
                # Delay ngắn giữa các lần retry ở ứng dụng để tránh dồn dập
                time.sleep(1)
    
            print(f"❌ Thất bại hoàn toàn sau {max_retries} lần thử tại URL: {url}")
            return None
    
    # ==================== HƯỚNG DẪN SỬ DỤNG ====================
    if __name__ == "__main__":
        # Cấu hình danh sách proxy của bạn
        my_proxies = [
            "http://123.45.67.89:8080",
            "http://98.76.54",
            "http://111.222.33.44:80"
        ]
        
        fetcher = SyncStoryFetcher(proxy_list=my_proxies)
        target_url = "https://example-truyen-chu.com"
        
        html_content = fetcher.fetch_page(target_url, max_retries=5)
        
        if html_content:
            print("✅ Thành công! Độ dài trang tải được:", len(html_content))
            # Thực hiện bóc tách DOM chữ truyện bằng selectolax/beautifulsoup ở đây
        else:
            print("❌ Không lấy được dữ liệu.")
    

## Cách hoạt động chi tiết của mã nguồn:

  * Retry tầng Application: Toàn bộ logic `try-except` bọc ngoài `with httpx.Client()` đóng vai trò là tầng Application Retry. Mọi lỗi mạng hay timeout phát sinh từ request của `httpx` sẽ văng ra ngoài, được bắt lại, ghi nhận proxy hỏng và chuyển sang vòng lặp kế tiếp để thử lại.
  * Xoay vòng (Rotator) thực thụ: Mỗi lượt retry hoặc lượt gọi trang mới, `random.choice()` sẽ chọn ra một proxy ngẫu nhiên khác từ pool nhằm phân tán request.
  * Valid Proxy Alive (Loại bỏ proxy chết): Thay vì tốn thời gian kiểm tra trước (check alive) toàn bộ proxy làm chậm app, code sử dụng chiến lược "Fail-and-Drop". Nếu proxy phát sinh lỗi mạng hoặc trả về mã chặn `403`/`429`, nó sẽ lập tức bị `.remove()` khỏi `active_proxies`, đảm bảo các request sau không gọi trúng nó nữa.
  * Tách biệt Connection Pool: Mỗi vòng lặp tạo mới một instance `httpx.Client()`. Điều này rất quan trọng khi đổi proxy đồng bộ, giúp `httpx` không dùng lại socket/connection cũ đã map với proxy hỏng trước đó.



Để xử lý tiếp dữ liệu sau khi fetch thành công, bạn muốn:

  * Tích hợp công cụ parse HTML siêu nhanh `selectolax` để lọc thẻ chứa nội dung chương truyện?
  * Tạo cấu trúc thư mục tự động lưu truyện thành các file `.txt` hay `.md` theo từng chương?