Mô hình Producer-Consumer (Người sản xuất - Người tiêu dùng) kết hợp với `asyncio.Queue` là giải pháp hoàn hảo cho các hệ thống cào dữ liệu lớn.

Thay vì phải đợi tìm hết 1000 link rồi mới cào, mô hình này chia làm hai nhóm công nhân làm việc song song:

  * Producer (Người sản xuất): Đi vào trang mục lục, tìm thấy link chương nào mới là ném ngay vào hàng đợi (Queue).
  * Consumer (Người tiêu dùng): Ngồi chực chờ ở hàng đợi, thấy có link mới xuất hiện là lập tức bốc ra để tải và xử lý ngay theo kiểu cuốn chiếu.



* * *

## Kịch bản triển khai bằng Code Python

Dưới đây là mã nguồn hoàn chỉnh áp dụng SOLID và mô hình Queue để vừa tìm link vừa cào truyện liên tục.
    
    
    import asyncio
    import aiohttp
    from abc import ABC, abstractmethod
    from bs4 import BeautifulSoup
    from dataclasses import dataclass
    
    @dataclass
    class NovelChapter:
        title: str
        content: str
    
    # ==========================================
    # 1. PORTS / INTERFACES (Theo nguyên lý SOLID)
    # ==========================================
    class NovelParser(ABC):
        @abstractmethod
        def parse_chapter(self, html: str) -> NovelChapter:
            """Bóc tách nội dung một chương"""
            pass
    
        @abstractmethod
        def extract_links_from_toc(self, html: str) -> list[str]:
            """Bóc tách danh sách link chương từ trang mục lục (Table of Contents)"""
            pass
    
    class AsyncStorage(ABC):
        @abstractmethod
        async def save(self, chapter: NovelChapter) -> None:
            pass
    
    # ==========================================
    # 2. ADAPTERS (Triển khai chi tiết kỹ thuật)
    # ==========================================
    class DemoNovelParser(NovelParser):
        def parse_chapter(self, html: str) -> NovelChapter:
            # Giả lập bóc tách HTML chương
            soup = BeautifulSoup(html, 'html.parser')
            return NovelChapter(title="Chương Demo", content="Nội dung truyện...")
    
        def extract_links_from_toc(self, html: str) -> list[str]:
            # Giả lập tìm thấy 5 link chương từ trang mục lục
            return [f"https://truyen.demo{i}/" for i in range(1, 11)]
    
    class ConsoleStorage(AsyncStorage):
        async def save(self, chapter: NovelChapter) -> None:
            await asyncio.sleep(0.5)  # Giả lập thời gian ghi DB/File
            print(f" Saved: {chapter.title} thành công.")
    
    # ==========================================
    # 3. CORE ENGINE (Mô hình Producer - Consumer)
    # ==========================================
    class AdvancedNovelCrawler:
        def __init__(self, parser: NovelParser, storage: AsyncStorage, session: aiohttp.ClientSession):
            self.parser = parser
            self.storage = storage
            self.session = session
            # Tạo hàng đợi asyncio để luân chuyển link giữa Producer và Consumer
            self.queue = asyncio.Queue()
    
        # --- PRODUCER ---
        async def producer_discover_links(self, toc_url: str):
            """Nhiệm vụ: Quét trang mục lục để tìm link và ném vào Queue"""
            print(f"[Producer] Đang quét trang mục lục: {toc_url}")
            
            # Giả lập tải trang mục lục (Trong thực tế dùng self.session.get)
            await asyncio.sleep(1) 
            mock_html = "<html>Mục lục</html>"
            
            # Trích xuất link
            urls = self.parser.extract_links_from_toc(mock_html)
            
            for url in urls:
                print(f"[Producer] ➕ Đã tìm thấy và thêm vào hàng đợi: {url}")
                # Đẩy link vào hàng đợi (Bất đồng bộ)
                await self.queue.put(url)
                await asyncio.sleep(0.1) # Nghỉ ngắn giữa các lần tìm
                
            print("[Producer] Đã tìm hết link ở trang mục lục. Hoàn thành nhiệm vụ!")
    
        # --- CONSUMER ---
        async def consumer_crawl_worker(self, worker_id: int):
            """Nhiệm vụ: Lấy link từ Queue ra để cào cuốn chiếu"""
            print(f"   [Consumer {worker_id}] Đã kích hoạt, sẵn sàng chờ link...")
            
            while True:
                # Chờ cho đến khi có link trong hàng đợi để bốc ra xử lý
                url = await self.queue.get()
                
                try:
                    print(f"   [Consumer {worker_id}] 🚀 Bắt đầu cào: {url}")
                    
                    # Giả lập tải và parse chương truyện
                    await asyncio.sleep(0.8) # Giả lập tải trang
                    mock_chapter_html = "<html>Nội dung chương</html>"
                    chapter_data = self.parser.parse_chapter(mock_chapter_html)
                    chapter_data.title = f"Chương {url.split('-')[-1].replace('/', '')}"
                    
                    # Lưu dữ liệu
                    await self.storage.save(chapter_data)
                    
                except Exception as e:
                    print(f"   [Consumer {worker_id}] ❌ Lỗi khi cào {url}: {e}")
                finally:
                    # BẮT BUỘC: Báo cáo với Queue là tác vụ của link này đã xử lý xong
                    self.queue.task_done()
    
    # ==========================================
    # 4. ĐIỀU PHỐI HỆ THỐNG RUNTIME
    # ==========================================
    async def main():
        async with aiohttp.ClientSession() as session:
            # Khởi tạo hệ thống (Dependency Injection)
            crawler = AdvancedNovelCrawler(
                parser=DemoNovelParser(),
                storage=ConsoleStorage(),
                session=session
            )
    
            # Số lượng công nhân Consumer muốn chạy song song (Tùy thuộc vào giới hạn IP của web)
            NUM_CONSUMERS = 3
    
            # 1. Kích hoạt các công nhân Consumer chạy ngầm (Background Tasks)
            consumer_tasks = []
            for i in range(NUM_CONSUMERS):
                task = asyncio.create_task(crawler.consumer_crawl_worker(worker_id=i+1))
                consumer_tasks.append(task)
    
            # 2. Kích hoạt Producer đi tìm link (Đợi cho đến khi Producer quét xong)
            toc_url = "https://truyen.demo"
            await crawler.producer_discover_links(toc_url)
    
            # 3. Chờ cho đến khi các Consumer xử lý sạch sẽ toàn bộ link trong Queue
            await crawler.queue.join()
            print("\n🎉 Tất cả truyện trong hàng đợi đã được cào cuốn chiếu xong!")
    
            # 4. Hủy các tác vụ Consumer ngầm vì hàng đợi đã trống hoàn toàn
            for task in consumer_tasks:
                task.cancel()
    
    if __name__ == "__main__":
        asyncio.run(main())
    

* * *

## Giải thích luồng vận hành

  1. Khởi tạo ngầm (Consumers): 3 "công nhân" Consumer được tạo ra và rơi vào trạng thái treo máy tại dòng `await self.queue.get()`. Chúng không làm gì cả cho đến khi có dữ liệu.
  2. Sản xuất (Producer): Producer bắt đầu chạy, đọc trang mục lục và tìm thấy `chuong-1`, `chuong-2`... Khi dùng lệnh `await self.queue.put(url)`, ngay lập tức các Consumer đang chờ sẽ "thức giấc" để bốc link đó đi xử lý luôn.
  3. Cuốn chiếu: Bạn sẽ thấy trên màn hình console hiển thị đan xen: Producer vừa báo tìm thấy `chuong-5`, thì cùng lúc đó Consumer 1 đang xử lý `chuong-2`, Consumer 2 xử lý `chuong-3`. Quá trình diễn ra liên tục, không lãng phí một mili-giây thời gian chết nào.
  4. `queue.join()` và `task_done()`: Đây là cơ chế đồng bộ. Mỗi khi Consumer xử lý xong 1 link, nó gọi `task_done()`. Hàm `queue.join()` ở luồng chính sẽ chặn chương trình lại cho đến khi số lượng `task_done()` bằng đúng số lượng link đã `put` vào. Khi tất cả bằng nhau, chương trình kết thúc an toàn.



Nếu bạn muốn tiếp tục nâng cấp hệ thống này lên mức tối thượng, hãy cho tôi biết:

  * Bạn có muốn biến Producer thành quét đa trang (vừa cào vừa lật trang mục lục 1, trang 2, trang 3) không?
  * Hay bạn muốn tìm hiểu cách xử lý Hàng đợi ưu tiên (`asyncio.PriorityQueue`) để luôn ưu tiên cào những chương VIP hoặc chương mới cập nhật trước?