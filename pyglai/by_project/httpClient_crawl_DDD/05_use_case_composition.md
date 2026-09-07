Dưới đây là cách kết hợp cả 3 thành phần: Async HTTP Client, Domain Models/Entities, và Sync SQLite Repository thành một Application Service (Use Case) hoàn chỉnh.

Vì tầng lưu trữ SQLite chạy đồng bộ (Sync), chúng ta sẽ sử dụng kỹ thuật phân tách luồng xử lý: Cào dữ liệu song song bằng `asyncio`, sau đó gom kết quả và lưu tuần tự vào Database nhằm đảm bảo tính toàn vẹn dữ liệu (Transaction) và tránh xung đột khóa (Lock) của SQLite.

* * *

## 1\. Tạo Kiến trúc Thư mục Ứng dụng
    
    
    src/
    ├── domain/
    │   └── story/
    │       ├── value_objects.py
    │       ├── entities.py
    │       └── repositories.py
    ├── infrastructure/
    │   ├── http/
    │   │   ├── session_pool.py
    │   │   └── client.py
    │   └── persistence/
    │       └── sqlite_repository.py
    ├── application/
    │   └── crawl_novel_usecase.py  # <-- Thành phần mới: Điều hướng dòng chảy nghiệp vụ
    └── main.py
    

* * *

## 2\. Triển khai Lớp Application Service (`application/crawl_novel_usecase.py`)

Lớp này đóng vai trò Orchestrator (Nhạc trưởng). Nó nhận vào các Interface (`BaseAsyncHttpClient`, `BaseNovelRepository`), tải danh sách chương, kích hoạt cào dữ liệu, ra lệnh cho Domain xử lý và lưu kết quả cuối cùng.
    
    
    import asyncio
    from typing import List, Dict
    from domain.story.entities import Novel, Chapter
    from domain.story.repositories import BaseNovelRepository
    from domain.crawler.gateways import BaseAsyncHttpClient
    
    class CrawlNovelUseCase:
        """Application Service: Quản lý quy trình (Workflow) cào truyện và lưu trữ."""
    
        def __init__(self, http_client: BaseAsyncHttpClient, novel_repository: BaseNovelRepository):
            self.http_client = http_client
            self.novel_repository = novel_repository
    
        async def execute(self, novel: Novel, chapter_tasks: List[Dict[str, any]]) -> None:
            """Kích hoạt tiến trình cào đồng thời nhiều chương và cập nhật vào DB."""
            print(f"\n[UseCase] Bắt đầu tiến trình cào dữ liệu cho bộ truyện: '{novel.title}'")
            
            # 1. Tạo danh sách các tác vụ Async để cào song song
            async_tasks = [
                self._crawl_and_populate_chapter(novel, task["id"], task["number"], task["title"], task["url"])
                for task in chapter_tasks
            ]
            
            # 2. Thực thi cào đồng thời (Concurrent Request)
            # return_exceptions=True giúp một chương bị lỗi mạng không làm chết cả hệ thống
            await asyncio.gather(*async_tasks, return_exceptions=True)
    
            # 3. Đồng bộ (Sync) dữ liệu từ bộ nhớ RAM xuống SQLite Database sau khi cào xong
            print(f"[UseCase] Đang chuẩn bị đồng bộ {novel.get_total_chapters()} chương vào Database...")
            try:
                self.novel_repository.save(novel)
                print(f"[UseCase] Thành công! Bộ truyện '{novel.title}' đã được cập nhật dữ liệu sạch.")
            except Exception as e:
                print(f"[UseCase] Thất bại khi ghi dữ liệu vào ổ cứng: {e}")
    
        async def _crawl_and_populate_chapter(
            self, novel: Novel, ch_id: str, ch_number: float, ch_title: str, url: str
        ) -> None:
            """Tác vụ con: Tải HTML thô và nạp vào thực thể Chapter tương ứng."""
            try:
                # Gọi hạ tầng mạng để lấy HTML thô
                raw_html = await self.http_client.fetch_html(url)
                
                # Khởi tạo thực thể Chương của Domain
                chapter = Chapter(chapter_id=ch_id, number=ch_number, title=ch_title)
                
                # Ra lệnh cho Domain tự làm sạch text rác/quảng cáo
                chapter.update_content(raw_html)
                
                # Thêm chương vào gốc tổng hợp (Aggregate Root) của truyện
                novel.add_chapter(chapter)
                print(f" -> Đã tải và dọn sạch: {ch_title}")
                
            except Exception as e:
                print(f" -> Lỗi khi tải chương '{ch_title}' từ URL {url}: {e}")
    

* * *

## 3\. Entry Point Kết hợp Hệ thống (`main.py`)

Tệp này thực hiện thiết lập cấu hình, khởi tạo Database, Inject (gài) hạ tầng vào UseCase và chạy ứng dụng thông qua Vòng lặp sự kiện (Event Loop).
    
    
    import sqlite3
    import asyncio
    from domain.story.value_objects import StoryUrl
    from domain.story.entities import Novel
    from infrastructure.http.session_pool import SessionConfigPool
    from infrastructure.http.client import ManagedAsyncHttpClient
    from infrastructure.persistence.sqlite_repository import SqliteNovelRepository
    from application.crawl_novel_usecase import CrawlNovelUseCase
    
    async def run_pipeline():
        # ==========================================
        # 1. KHỞI TẠO TẦNG HẠ TẦNG (INFRASTRUCTURE)
        # ==========================================
        # Cấu hình Mạng (Xoay vòng User-Agent, giới hạn tối đa 3 kết nối đồng thời)
        config_pool = SessionConfigPool(proxies=[])
        async_http_client = ManagedAsyncHttpClient(config_pool=config_pool, max_concurrent_requests=3)
        
        # Cấu hình Cơ sở dữ liệu SQLite
        db_conn = sqlite3.connect("app_crawler_clean_ddd.db")
        db_conn.pragma("foreign_keys = ON") # Kích hoạt ràng buộc khóa ngoại
        sqlite_repo = SqliteNovelRepository(connection=db_conn)
    
        # ==========================================
        # 2. KHỞI TẠO TẦNG ỨNG DỤNG (APPLICATION)
        # ==========================================
        # Inject các thực thể hạ tầng vào UseCase (Dependency Injection)
        crawl_usecase = CrawlNovelUseCase(
            http_client=async_http_client, 
            novel_repository=sqlite_repo
        )
    
        # ==========================================
        # 3. CHUẨN BỊ DỮ LIỆU ĐẦU VÀO (DOMAIN INPUT)
        # ==========================================
        # Giả lập Aggregate Root khởi tạo ban đầu từ Domain
        novel_domain_obj = Novel(
            novel_id="novel_001",
            title="Tru Tiên",
            author="Tiêu Đỉnh",
            url=StoryUrl("https://truyen-tien-hiep.com")
        )
    
        # Giả lập danh sách link chương thu thập được từ trang mục lục (Index page)
        # Thử nghiệm với các đoạn mã HTML dính quảng cáo rác để test bộ lọc của Domain
        simulated_chapter_tasks = [
            {
                "id": "ch_tt_01", "number": 1.0, "title": "Chương 1: Thanh Vân Môn",
                "url": "https://truyen-tien-hiep.com/chuong-1"
            },
            {
                "id": "ch_tt_02", "number": 2.0, "title": "Chương 2: Thảo Miếu Thôn",
                "url": "https://truyen-tien-hiep.com/chuong-2"
            }
        ]
    
        # Giả lập dữ liệu trả về từ Server truyện khi Client gửi Request
        # (Để mã chạy độc lập không phụ thuộc mạng, chúng ta mock nhẹ hàm fetch_html của client)
        async def mock_fetch_html(url: str, headers=None) -> str:
            if "chuong-1" in url:
                return "<div><p>Trương Tiểu Phàm là một thiếu niên bình thường...</p><span>Nguồn: truyenfull</span></div>"
            return "<div><p>Phổ Trí thần tăng đang bị trọng thương...</p><p>Đọc tại truyen-tien-hiep để cập nhật chương mới.</p></div>"
        
        async_http_client.fetch_html = mock_fetch_html # Mock dữ liệu kiểm thử nhanh
    
        # ==========================================
        # 4. KÍCH HOẠT VẬN HÀNH TOÀN BỘ PIPELINE
        # ==========================================
        try:
            # Chạy quy trình đóng gói qua UseCase
            await crawl_usecase.execute(novel=novel_domain_obj, chapter_tasks=simulated_chapter_tasks)
            
            # Kiểm tra thử dữ liệu sau khi lưu vào DB xem đã sạch chưa
            print("\n--- KIỂM TRA DỮ LIỆU SẠCH TRONG SQLITE DATABASE ---")
            saved_novel = sqlite_repo.find_by_id("novel_001")
            if saved_novel:
                for ch in saved_novel.chapters:
                    print(f"\n👉 Dữ liệu trong DB của [{ch.title}]:")
                    print(ch.content.clean_text if ch.content else "Trống")
                    
        finally:
            # Giải phóng tài nguyên hệ thống chuẩn xác
            await async_http_client.close()
            db_conn.close()
    
    if __name__ == "__main__":
        # Khởi chạy ứng dụng
        asyncio.run(run_pipeline())
    

## 🎯 Ưu điểm kiến trúc tổng thể này đem lại:

  1. Phân tách luồng (Concurrency Control): Luồng IO Mạng (I/O Bound) chạy bất đồng bộ đa luồng cực nhanh để gom dữ liệu thô, trong khi luồng ghi ổ cứng (Disk I/O) chạy tuần tự đồng bộ để bảo vệ SQLite khỏi lỗi `database is locked`.
  2. Quy trình đóng gói biệt lập: Bạn có thể dễ dàng viết Unit Test để kiểm tra toàn bộ luồng đi này bằng cách gán một Repository ảo (`MockRepository` lưu vào biến mảng thay vì SQLite) mà không cần chỉnh sửa bất kỳ logic nào trong file `crawl_novel_usecase.py`.



Hệ thống lõi (Core Crawler Engine) hiện tại đã rất vững chắc. Bạn có muốn mở rộng thêm tính năng nào sau đây để hoàn thiện app không:

  * Thiết kế cơ chế Retry/Backoff thông minh (Nếu cào lỗi do bị chặn IP, tự động đổi Proxy hoặc ngủ 5 giây rồi thử lại)?
  * Thêm tầng Interface Adapter / Controller (Ví dụ tích hợp CLI command hoặc làm API FastAPI để người dùng bấm nút ra lệnh cào)?