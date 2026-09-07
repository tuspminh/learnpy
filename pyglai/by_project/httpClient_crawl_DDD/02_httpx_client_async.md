Để nâng cấp hệ thống HTTP Client Manager/Session sang cơ chế bất đồng bộ (Asyncio) nhằm tăng tốc độ cào hàng loạt chương truyện cùng lúc, chúng ta sẽ chuyển đổi các Interface và Adapter từ đồng bộ sang `async/await` bằng cách sử dụng `httpx.AsyncClient`.

Dưới đây là mã nguồn chi tiết được cập nhật theo đúng cấu trúc Clean Architecture và DDD.

* * *

## 1\. Lớp Domain (`domain/crawler/gateways.py`)

Ta chuyển đổi các phương thức của Interface thành coroutine bằng từ khóa `async`.
    
    
    from abc import ABC, abstractmethod
    from typing import Dict, Optional
    
    class BaseAsyncHttpClient(ABC):
        """Port: Interface bất đồng bộ (Async) cho HTTP Client."""
        
        @abstractmethod
        async def fetch_html(self, url: str, headers: Optional[Dict[str, str]] = None) -> str:
            """Lấy mã nguồn HTML từ một URL (Async)."""
            pass
    
        @abstractmethod
        async def close(self) -> None:
            """Đóng session async khi hoàn thành."""
            pass
    

* * *

## 2\. Lớp Infrastructure (`infrastructure/http/client.py`)

Triển khai Adapter bằng `httpx.AsyncClient`. Chúng ta sẽ sử dụng thêm cơ chế giới hạn số lượng request đồng thời (Semaphore) để tránh việc gửi quá nhiều request cùng lúc làm sập server truyện hoặc bị chặn IP (Ban IP).
    
    
    import httpx
    import asyncio
    from typing import Dict, Optional
    from domain.crawler.gateways import BaseAsyncHttpClient
    from infrastructure.http.session_pool import SessionConfigPool  # Giữ nguyên cấu hình pool cũ
    
    class ManagedAsyncHttpClient(BaseAsyncHttpClient):
        """Adapter: Triển khai Async HTTP Client sử dụng httpx.AsyncClient."""
        
        def __init__(self, config_pool: SessionConfigPool, max_concurrent_requests: int = 10, timeout_seconds: int = 15):
            self.config_pool = config_pool
            
            # Giới hạn số lượng request chạy song song cùng một thời điểm
            self._semaphore = asyncio.Semaphore(max_concurrent_requests)
            
            # Cấu hình tự động retry 3 lần khi gặp lỗi mạng tạm thời
            transport = httpx.AsyncHTTPTransport(retries=3)
            proxy = self.config_pool.get_random_proxy()
            
            self._session = httpx.AsyncClient(
                transport=transport,
                proxy=proxy,
                timeout=httpx.Timeout(timeout_seconds),
                follow_redirects=True
            )
            
            # Cấu hình Headers mặc định cho Session
            self._session.headers.update({
                "User-Agent": self.config_pool.get_random_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8",
            })
    
        async def fetch_html(self, url: str, headers: Optional[Dict[str, str]] = None) -> str:
            """Thực thi request lấy HTML bất đồng bộ, có áp dụng Semaphore kiểm soát flow."""
            async with self._semaphore:  # Đảm bảo không vượt quá giới hạn kết nối đồng thời
                try:
                    req_headers = headers or {}
                    if "User-Agent" not in req_headers:
                        req_headers["User-Agent"] = self.config_pool.get_random_user_agent()
                    
                    # Gọi request async
                    response = await self._session.get(url, headers=req_headers)
                    response.raise_for_status()
                    return response.text
                    
                except httpx.HTTPStatusError as e:
                    print(f"[HTTP Error {e.response.status_code}] Lỗi từ server truyện tại: {url}")
                    raise e
                except httpx.RequestError as e:
                    print(f"[Network Error] Lỗi kết nối mạng khi tải: {url} - Chi tiết: {e}")
                    raise e
    
        async def close(self) -> None:
            """Đóng session async."""
            await self._session.aclose()
    
        async def __aenter__(self):
            return self
    
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await self.close()
    

* * *

## 3\. Cách Sử dụng với Asyncio (`main.py`)

Tại hàm chạy chính, chúng ta tận dụng `asyncio.gather` để tải song song hàng loạt chương truyện một cách tối ưu.
    
    
    import asyncio
    from infrastructure.http.session_pool import SessionConfigPool
    from infrastructure.http.client import ManagedAsyncHttpClient
    from domain.crawler.gateways import BaseAsyncHttpClient
    
    class AsyncChapterCrawlerService:
        """Domain Service: Xử lý logic nghiệp vụ cào dữ liệu chương truyện theo cụm."""
        
        def __init__(self, http_client: BaseAsyncHttpClient):
            self.http_client = http_client
    
        async def crawl_single_chapter(self, chapter_id: int, url: str) -> dict:
            """Cào một chương đơn lẻ."""
            print(f"[Bắt đầu] Tải chương {chapter_id}...")
            html_content = await self.http_client.fetch_html(url)
            
            # Giả lập parse HTML (Ví dụ: dùng BeautifulSoup trích xuất nội dung)
            # Tại đây bạn có thể thêm asyncio.sleep(random.uniform(0.5, 1.5)) nếu muốn làm chậm tiến trình tránh bot detect
            
            print(f"[Hoàn thành] Đã tải xong chương {chapter_id}")
            return {
                "chapter_id": chapter_id,
                "status": "Success",
                "size": len(html_content)
            }
    
        async def crawl_multiple_chapters(self, chapter_tasks: list[dict]) -> list[dict]:
            """Tạo hàng loạt task và kích hoạt chạy song song."""
            tasks = [
                self.crawl_single_chapter(item["id"], item["url"]) 
                for item in chapter_tasks
            ]
            # Chạy đồng thời tất cả các task
            return await asyncio.gather(*tasks, return_exceptions=True)
    
    
    async def main():
        # 1. Khởi tạo cấu hình (Xoay vòng User-Agent / Proxy)
        config_pool = SessionConfigPool(proxies=[])
        
        # 2. Khởi tạo Async Client với giới hạn tối đa 5 request chạy cùng lúc (Concurrency)
        async with ManagedAsyncHttpClient(config_pool=config_pool, max_concurrent_requests=5) as http_client:
            
            # Inject client vào Service của Domain
            crawler_service = AsyncChapterCrawlerService(http_client=http_client)
            
            # 3. Chuẩn bị danh sách URL truyện cần cào
            urls_to_crawl = [
                {"id": i, "url": f"https://example-truyen-chu.com{i}"} 
                for i in range(1, 11)  # Cào thử nghiệm từ chương 1 đến chương 10
            ]
            
            # 4. Kích hoạt tiến trình cào đồng thời
            print("--- BẮT ĐẦU CÀO TRUYỆN ĐỒNG THỜI ---")
            results = await crawler_service.crawl_multiple_chapters(urls_to_crawl)
            
            print("\n--- KẾT QUẢ THỐNG KÊ ---")
            for res in results:
                print(res)
    
    if __name__ == "__main__":
        # Chạy vòng lặp sự kiện Event Loop của Asyncio
        asyncio.run(main())
    

* * *

## 📊 Điểm vượt trội của kiến trúc Async kết hợp DDD này:

  1. Kiểm soát dòng chảy (Flow Control): Tham số `max_concurrent_requests=5` kết hợp với `asyncio.Semaphore` giúp ứng dụng của bạn tạo ra hàng trăm task nhưng tại một thời điểm chỉ có đúng 5 kết nối HTTP thực sự được gửi đi. Việc này giúp ứng dụng không bị sập vì quá tải tài nguyên RAM/Socket và bảo vệ hệ thống khỏi bị tường lửa của website truyện chặn IP.
  2. Tận dụng lại Connection Pool: Do sử dụng chung một thực thể `httpx.AsyncClient` xuyên suốt các task, cơ chế HTTP Keep-Alive được kích hoạt giúp tái sử dụng các kết nối TCP cũ, giảm thiểu thời gian bắt tay (TLS/TCP Handshake) đáng kể.



Để hoàn thiện pipeline thu thập dữ liệu này, bạn có muốn chúng ta cùng thiết kế tiếp phần:

  * Domain Models & Entities: Định nghĩa cấu trúc dữ liệu chặt chẽ cho `Novel` (Truyện) và `Chapter` (Chương) có khả năng tự dọn dẹp dữ liệu rác (Clean text)?
  * Repository Pattern: Interface và Adapter lưu trữ dữ liệu chương truyện sau khi cào vào Database (SQLite/MongoDB) hoặc xuất ra file TXT/EPUB?