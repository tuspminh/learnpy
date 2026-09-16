Dưới đây là mã nguồn `StoryFetcher` phiên bản đồng bộ (Synchronous) sử dụng `curl_cffi.requests`. Phiên bản này phù hợp nếu cấu trúc app của bạn viết theo dạng tuần tự (Crawl từng chương một) hoặc dùng kết hợp với `ThreadPoolExecutor`.

Tôi đã thêm sẵn `requests.Session` đồng bộ, cơ chế tự động cấu hình `impersonate`, tự sửa lỗi font tiếng Việt, và giới hạn thời gian chờ (`timeout`).
    
    
    import time
    import logging
    from curl_cffi import requests
    from curl_cffi.requests import Session, BrowserType, RequestsError
    
    # Cấu hình log để theo dõi quá trình crawl
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)
    
    class StoryFetcherSync:
        def __init__(self, max_retries: int = 3, delay: float = 1.5):
            self.max_retries = max_retries
            self.delay = delay
            
            # Khởi tạo Session đồng bộ, giả mạo Chrome 120
            self.session = Session(browser=BrowserType.chrome120, impersonate="chrome120")
            
            # Cấu hình Header giống trình duyệt thật
            self.session.headers.update({
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "accept-language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
            })
    
        def fetch_page(self, url: str) -> str:
            """Tải nội dung HTML của một trang (Đồng bộ)."""
            for attempt in range(1, self.max_retries + 1):
                try:
                    logger.info(f"Đang tải: {url} (Lần thử {attempt}/{self.max_retries})")
                    
                    # Gọi request đồng bộ (Chặn luồng cho đến khi có kết quả hoặc timeout)
                    response = self.session.get(url, timeout=15)
                    
                    if response.status_code == 200:
                        # Tự động giải mã đúng font tiếng Việt tránh lỗi hiển thị
                        return response.content.decode(response.apparent_encoding, errors='ignore')
                    
                    logger.warning(f"Lỗi HTTP {response.status_code} khi tải {url}")
                    
                except RequestsError as e:
                    logger.error(f"Lỗi kết nối curl_cffi: {e}")
                except Exception as e:
                    logger.error(f"Lỗi không xác định: {e}")
                    
                # Đợi tăng dần trước khi retry để tránh bị dính block block IP / Rate Limit
                time.sleep(self.delay * attempt)
                
            logger.error(f"Thất bại hoàn toàn sau {self.max_retries} lần thử: {url}")
            return ""
    
        def close(self):
            """Đóng session để giải phóng bộ nhớ."""
            self.session.close()
    
    # ==========================================
    # VÍ DỤ SỬ DỤNG THỰC TẾ (CHẠY TUẦN TỰ)
    # ==========================================
    if __name__ == "__main__":
        # Khởi tạo fetcher
        fetcher = StoryFetcherSync(max_retries=3, delay=1.5)
        
        # Danh sách chương truyện cần crawl tuần tự
        chapters = [
            "https://example-truyen.com",
            "https://example-truyen.com",
            "https://example-truyen.com",
        ]
        
        for url in chapters:
            html_content = fetcher.fetch_page(url)
            
            if html_content:
                print(f" Tải thành công {url} | Độ dài HTML: {len(html_content)} ký tự.")
                # Xử lý bóc tách nội dung chương ở đây (BeautifulSoup/Selectolax)
            else:
                print(f"❌ Tải thất bại {url}")
                
            # Giãn cách nhẹ giữa các chương để ứng xử như người dùng thật đọc truyện
            time.sleep(1.0)
            
        # Luôn đóng session khi hoàn thành tác vụ
        fetcher.close()
    

## Điểm khác biệt so với bản Async:

  1. Không dùng từ khóa `async/await`: Bạn gọi trực tiếp `fetcher.fetch_page(url)` như thư viện `requests` truyền thống.
  2. `time.sleep()` thay cho `asyncio.sleep()`: Chặn hoàn toàn tiến trình hiện tại trong thời gian nghỉ.
  3. Phù hợp đa luồng cũ (`threading`): Nếu bạn muốn tăng tốc bản sync này mà không muốn dùng `asyncio`, bạn có thể ném class này vào `concurrent.futures.ThreadPoolExecutor`.