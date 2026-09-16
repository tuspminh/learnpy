Dưới đây là mã nguồn mẫu cấu trúc một class `StoryFetcher` bất đồng bộ (async) bằng `curl_cffi`, được tối ưu chuyên dụng cho việc cào (crawl) truyện chữ từ các trang có Cloudflare/Anti-bot.

Mã nguồn này bao gồm: cấu hình giả mạo trình duyệt Chrome, tự động retry khi lỗi mạng, và xử lý decode lỗi font/nội dung nếu gặp trang dùng font-face hoặc mã hóa lạ.
    
    
    import asyncio
    import logging
    from curl_cffi.requests import AsyncSession, BrowserType, RequestsError
    
    # Cấu hình log để theo dõi quá trình crawl
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)
    
    class StoryFetcher:
        def __init__(self, max_retries: int = 3, delay: float = 1.5):
            self.max_retries = max_retries
            self.delay = delay
            # Khởi tạo session giả mạo trình duyệt Chrome (bản mới nhất được hỗ trợ)
            # Giữ nguyên session này suốt quá trình crawl để tận dụng Connection Pool và Cookie
            self.session = AsyncSession(browser=BrowserType.chrome120, impersonate="chrome120")
            
            # Cấu hình Header mặc định giống trình duyệt thật
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
    
        async def fetch_page(self, url: str) -> str:
            """Tải nội dung HTML của một trang (Danh sách chương hoặc nội dung chương)."""
            for attempt in range(1, self.max_retries + 1):
                try:
                    logger.info(f"Đang tải: {url} (Lần thử {attempt}/{self.max_retries})")
                    
                    # Gọi request (curl_cffi tự động xử lý JA3/JA4 fingerprint ngầm)
                    response = await self.session.get(url, timeout=15)
                    
                    # Kiểm tra HTTP Status
                    if response.status_code == 200:
                        # Tự động detect encoding nếu truyện bị lỗi font (UTF-8, TCVN3...)
                        return response.content.decode(response.apparent_encoding, errors='ignore')
                    
                    logger.warning(f"Lỗi HTTP {response.status_code} khi tải {url}")
                    
                except RequestsError as e:
                    logger.error(f"Lỗi kết nối curl_cffi: {e}")
                except Exception as e:
                    logger.error(f"Lỗi không xác định: {e}")
                    
                # Đợi một chút trước khi thử lại (Tránh bị dính Rate Limit)
                await asyncio.sleep(self.delay * attempt)
                
            logger.error(f"Thất bại hoàn toàn sau {self.max_retries} lần thử: {url}")
            return ""
    
        async def close(self):
            """Đóng session khi hoàn thành ứng dụng."""
            await self.session.close()
    
    # ==========================================
    # VÍ DỤ SỬ DỤNG THỰC TẾ (DEMO RUNNER)
    # ==========================================
    async def main():
        fetcher = StoryFetcher(max_retries=3, delay=2.0)
        
        # Danh sách các link chương truyện cần crawl song song
        urls = [
            "https://example-truyen.com",
            "https://example-truyen.com",
            "https://example-truyen.com",
        ]
        
        # Tạo các task chạy bất đồng bộ cùng lúc
        tasks = [fetcher.fetch_page(url) for url in urls]
        
        # Chạy đồng thời tất cả các task
        html_results = await asyncio.gather(*tasks)
        
        # Xử lý kết quả trả về
        for url, html in zip(urls, html_results):
            if html:
                print(f" Tải thành công {url} | Độ dài HTML: {len(html)} ký tự.")
                # Ở đây bạn có thể dùng BeautifulSoup hoặc Selectolax để parse HTML lấy text truyện
            else:
                print(f"❌ Tải thất bại {url}")
                
        # Giải phóng tài nguyên session
        await fetcher.close()
    
    if __name__ == "__main__":
        asyncio.run(main())
    

## Các điểm lưu ý khi viết App Crawl Truyện bằng `curl_cffi`:

  * Giữ nguyên 1 `AsyncSession`: Đừng tạo mới session ở mỗi chương. Việc dùng lại session giúp bạn giữ lại `Cookie` (nếu trang yêu cầu login/xác thực) và giữ kết nối TCP mở sẵn (keep-alive) giúp tốc độ crawl cực nhanh.
  * `apparent_encoding`: Truyện chữ ở Việt Nam đôi khi dùng các chuẩn mã hóa cũ hoặc bị lỗi header mã hóa. Sử dụng `response.apparent_encoding` giúp thư viện tự đoán chuẩn mã hóa của trang đó để không bị lỗi hiển thị dấu tiếng Việt (`đ`, `á`, `à`...).
  * Giới hạn số luồng (Semaphore): Nếu danh sách chương lên tới hàng nghìn, việc dùng `asyncio.gather` trực tiếp như trên sẽ gửi hàng nghìn request cùng lúc, làm sập IP của bạn. Bạn nên kết hợp `asyncio.Semaphore(5)` để giới hạn chỉ crawl tối đa 5 chương cùng một thời điểm.



Bạn muốn tích hợp thêm thư viện parse nội dung nào vào fetcher này (ví dụ: BeautifulSoup hay Selectolax để bóc tách thẻ chứa nội dung truyện)? Hoặc bạn có cần viết thêm cơ chế lưu truyện trực tiếp vào file Txt/Epub không?