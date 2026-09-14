Dưới đây là boilerplate code hoàn chỉnh sử dụng `httpx` (Async) để fetch dữ liệu truyện chữ. Code tích hợp sẵn cơ chế xoay vòng Proxy (Rotator), tự động loại bỏ Proxy chết (Valid Alive Check), và xoay vòng User-Agent.
    
    
    import asyncio
    import random
    import httpx
    from typing import List, Optional
    
    # Danh sách User-Agents phổ biến để tránh bị chặn
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1"
    ]
    
    class StoryFetcher:
        def __init__(self, proxy_list: List[str]):
            """
            proxy_list format: [
                "http://username:password@ip:port",
                "http://ip:port"
            ]
            """
            self.raw_proxies = proxy_list
            self.active_proxies = proxy_list.copy() # Danh sách proxy đang hoạt động
    
        def _get_headers(self) -> dict:
            """Tạo ngẫu nhiên Headers và User-Agent cho mỗi request"""
            return {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://google.com",
            }
    
        async def check_proxy_alive(self, proxy: str) -> bool:
            """Kiểm tra nhanh xem proxy có hoạt động tốt hay không"""
            try:
                async with httpx.AsyncClient(proxies=proxy, timeout=5.0) as client:
                    # Sử dụng httpbin hoặc chính trang truyện để check
                    resp = await client.get("https://httpbin.org")
                    return resp.status_code == 200
            except Exception:
                return False
    
        async def fetch_page(self, url: str, max_retries: int = 5) -> Optional[str]:
            """Fetch nội dung HTML của trang truyện chữ kèm cơ chế xoay vòng và retry"""
            for attempt in range(max_retries):
                # Nếu hết sạch proxy hoạt động, nạp lại danh sách gốc để thử lại
                if not self.active_proxies:
                    print("⚠️ Tất cả proxy trong list đã die. Nạp lại danh sách gốc...")
                    self.active_proxies = self.raw_proxies.copy()
                    if not self.active_proxies:
                        print("❌ Không có proxy nào khả dụng.")
                        return None
    
                # 1. Rotator: Lấy ngẫu nhiên 1 proxy từ danh sách active
                proxy = random.choice(self.active_proxies)
                
                try:
                    # Cấu hình Client với proxy và headers riêng biệt cho từng request
                    async with httpx.AsyncClient(
                        proxies=proxy, 
                        headers=self._get_headers(), 
                        timeout=10.0,
                        follow_redirects=True
                    ) as client:
                        
                        response = await client.get(url)
                        
                        if response.status_code == 200:
                            return response.text
                        elif response.status_code in:
                            print(f"🚫 Proxy {proxy} bị block (HTTP {response.status_code}). Loại bỏ...")
                            self.active_proxies.remove(proxy)
                        else:
                            print(f"⚠️ Lỗi HTTP {response.status_code} với proxy {proxy}")
                            
                except (httpx.ProxyError, httpx.NetworkError, httpx.TimeoutException) as e:
                    print(f"❌ Proxy {proxy} gặp lỗi kết nối ({type(e).__name__}). Đang loại bỏ...")
                    if proxy in self.active_proxies:
                        self.active_proxies.remove(proxy)
                
                # Delay ngắn trước khi thử lại với proxy khác (tránh spam)
                await asyncio.sleep(1)
                
            print(f"❌ Thất bại sau {max_retries} lần thử cho URL: {url}")
            return None
    
    # ==================== HƯỚNG DẪN SỬ DỤNG ====================
    async def main():
        # Thay thế bằng list proxy thật của bạn
        my_proxies = [
            "http://123.45.67.89:8080",
            "http://98.76.54",
        ]
        
        fetcher = StoryFetcher(proxy_list=my_proxies)
        
        target_url = "https://truyenfull.io" # Ví dụ url
        
        print("🚀 Bắt đầu fetch trang truyện...")
        html_content = await fetcher.fetch_page(target_url)
        
        if html_content:
            print("✅ Tải trang thành công! Độ dài HTML:", len(html_content))
            # Tiến hành dùng BeautifulSoup hoặc Selectolax để parse nội dung chữ ở đây...
        else:
            print("❌ Không thể lấy dữ liệu.")
    
    if __name__ == "__main__":
        asyncio.run(main())
    

## Các điểm tối ưu cho Crawl Truyện Chữ trong code trên:

  * `httpx.AsyncClient` cục bộ: Khởi tạo client riêng biệt theo từng request bên trong vòng lặp để đảm bảo mỗi khi đổi proxy, connection pool cũ của proxy chết sẽ được giải phóng hoàn toàn.
  * Xử lý Error-Driven Removal: Thay vì check trước toàn bộ proxy (tốn thời gian), code sử dụng chiến lược chạy thực tế. Nếu proxy lỗi mạng hoặc dính `403/429` (Cloudflare/Anti-bot chặn), nó sẽ tự động bị xóa khỏi `active_proxies` để không gọi lại nữa.
  * `follow_redirects=True`: Rất quan trọng với web truyện vì các trang này thường chuyển hướng URL khi sang chương mới hoặc thay đổi cấu trúc domain.



Để hoàn thiện app crawl, bạn có muốn tích hợp thêm:

  1. Bộ thư viện parse nội dung tốc độ cao như `selectolax` (nhanh hơn BeautifulSoup)?
  2. Cơ chế bypass Cloudflare (nếu trang truyện bạn crawl sử dụng Cloudflare bảo mật cao)?
  3. Lưu dữ liệu vào SQLite hay file Text/Markdown?