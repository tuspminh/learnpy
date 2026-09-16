Dưới đây là mã nguồn mẫu hoàn chỉnh cho một `Fetcher` truyện chữ bằng thư viện `primp`, bao gồm cả hai phiên bản: Đồng bộ (Sync) dành cho các tác vụ tuần tự/đơn giản và Bất đồng bộ (Async) giúp tăng tốc độ cào dữ liệu hàng loạt khi tải danh sách chương.

## 1\. Phiên bản Đồng bộ (Sync Fetcher)

Thích hợp khi bạn cần lấy thông tin cấu trúc truyện, danh sách chương, hoặc khi trang web có hệ thống chặn tần suất (rate-limit) gắt gao buộc phải tải chậm.
    
    
    import primp
    import time
    from typing import Optional
    
    class ComicSyncFetcher:
        def __init__(self, impersonate: str = "chrome_146", proxy: Optional[str] = None):
            # Khởi tạo client dùng chung để giữ session và cookie (nếu có)
            self.client = primp.Client(
                impersonate=impersonate,
                proxy=proxy,
                timeout=15, # Giới hạn thời gian chờ 15 giây
                follow_redirects=True
            )
            # Cập nhật các header chuẩn cho việc cào truyện
            self.client.headers.update({
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://google.com"
            })
    
        def fetch_page(self, url: str, retries: int = 3) -> Optional[str]:
            """Tải nội dung HTML của một trang (Trang chủ truyện hoặc Trang nội dung chương)"""
            for attempt in range(retries):
                try:
                    response = self.client.get(url)
                    if response.status_code == 200:
                        return response.text
                    print(f"[Sync] Lỗi HTTP {response.status_code} khi tải: {url}")
                except Exception as e:
                    print(f"[Sync] Lỗi kết nối (Lần thử {attempt + 1}/{retries}): {e}")
                    time.sleep(2) # Đợi 2 giây trước khi thử lại
            return None
    
    # --- VÍ DỤ SỬ DỤNG ---
    if __name__ == "__main__":
        # Khởi tạo fetcher giả lập Chrome mới nhất
        fetcher = ComicSyncFetcher(impersonate="chrome_146")
        
        # Giả định URL một trang truyện chữ (Ví dụ: TangThuVien, TruyenFull...)
        url_truyen = "https://httpbin.org" # Thay bằng URL thật
        
        print("Đang tải dữ liệu truyện...")
        html_content = fetcher.fetch_page(url_truyen)
        if html_content:
            print("Tải thành công! Độ dài HTML:", len(html_content))
    

* * *

## 2\. Phiên bản Bất đồng bộ (Async Fetcher)

Thích hợp nhất khi bạn đã có danh sách 50 - 100 chương truyện và muốn tải song song tất cả các chương này về máy để lưu trữ (như xuất file EPUB/TXT) nhằm tiết kiệm thời gian tối đa.
    
    
    import asyncio
    import primp
    from typing import List, Dict, Optional
    
    class ComicAsyncFetcher:
        def __init__(self, impersonate: str = "chrome_146", proxy: Optional[str] = None, max_connections: int = 5):
            # Giới hạn số lượng request chạy song song cùng lúc để tránh bị block IP
            self.semaphore = asyncio.Semaphore(max_connections)
            self.client_kwargs = {
                "impersonate": impersonate,
                "proxy": proxy,
                "timeout": 20,
                "follow_redirects": True
            }
            self.headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            }
    
        async def fetch_chapter(self, client: primp.AsyncClient, chapter_id: int, url: str, retries: int = 3) -> Dict:
            """Tải một chương truyện cụ thể"""
            async with self.semaphore: # Giới hạn concurrency tại đây
                for attempt in range(retries):
                    try:
                        response = await client.get(url)
                        if response.status_code == 200:
                            return {"chapter_id": chapter_id, "status": "success", "html": response.text}
                        
                        print(f"[Async] Chương {chapter_id} lỗi HTTP {response.status_code}")
                    except Exception as e:
                        print(f"[Async] Chương {chapter_id} lỗi (Lần {attempt+1}): {e}")
                        await asyncio.sleep(1.5)
                
                return {"chapter_id": chapter_id, "status": "failed", "html": None}
    
        async def fetch_all_chapters(self, chapter_list: List[Dict[str, str]]) -> List[Dict]:
            """Nhận vào danh sách gồm nhiều chương [{'id': 1, 'url': '...'}, ...] và tải song song"""
            async with primp.AsyncClient(**self.client_kwargs) as client:
                client.headers.update(self.headers)
                
                # Tạo danh sách các task cần chạy
                tasks = [
                    self.fetch_chapter(client, ch["id"], ch["url"]) 
                    for ch in chapter_list
                ]
                
                # Kích hoạt chạy song song và đợi gom kết quả
                results = await asyncio.gather(*tasks)
                return results
    
    # --- VÍ DỤ SỬ DỤNG ---
    async def main():
        # Giả lập danh sách chương cần cào hàng loạt
        chapters_to_download = [
            {"id": 1, "url": "https://httpbin.org"},
            {"id": 2, "url": "https://httpbin.org"},
            {"id": 3, "url": "https://httpbin.org"},
            {"id": 4, "url": "https://httpbin.org"},
        ]
        
        # Khởi tạo fetcher bất đồng bộ, tối đa 3 request chạy đồng thời
        async_fetcher = ComicAsyncFetcher(impersonate="chrome_146", max_connections=3)
        
        print("Đang cào song song các chương...")
        results = await async_fetcher.fetch_all_chapters(chapters_to_download)
        
        for res in results:
            print(f"Chương {res['chapter_id']}: Trạng thái tải -> {res['status']}")
    
    if __name__ == "__main__":
        asyncio.run(main())
    

Để hoàn thiện ứng dụng cào truyện chữ, bạn muốn tôi hỗ trợ thêm phần nào:

  * Viết tiếp đoạn mã bóc tách nội dung HTML (Parse nội dung chương) bằng thư viện `BeautifulSoup` hoặc `selectolax`?
  * Cách xử lý gom các kết quả tải về để xuất thành file truyện (.txt hoặc .epub)?
  * Bạn có cần cấu hình cơ chế xoay vòng Proxy (Rotated Proxies) nếu trang truyện cấu hình chặn IP gắt gao không?