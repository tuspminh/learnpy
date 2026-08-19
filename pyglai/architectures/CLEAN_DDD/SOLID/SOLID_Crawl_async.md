Để nâng cấp `NovelCrawlerEngine` thành bất đồng bộ (`asyncio`), chúng ta cần chuyển đổi các tác vụ tốn thời gian chờ đợi (I/O Bound) như tải trang qua mạng (Network requests) và ghi file (Disk I/O) sang dạng `async/await`.

Thay vì dùng thư viện `requests` (vốn là đồng bộ và gây nghẽn mạch), chúng ta sẽ dùng thư viện mã nguồn mở phổ biến `aiohttp` để tải trang bất đồng bộ.

Dưới đây là hướng dẫn từng bước để chuyển đổi hệ thống cào truyện của bạn sang siêu tốc độ với `asyncio`.

* * *

## Bước 1: Khai báo lại các Interface (Ports) dạng Async

Các phương thức lưu trữ cần được thêm từ khóa `async` để có thể tận dụng cơ chế non-blocking khi ghi dữ liệu.
    
    
    import asyncio
    from abc import ABC, abstractmethod
    from dataclasses import dataclass
    from bs4 import BeautifulSoup
    import aiohttp  # Thư viện HTTP Client bất đồng bộ
    
    @dataclass
    class NovelChapter:
        title: str
        content: str
    
    # LƯU Ý: Phân tách HTML (Parser) là tác vụ tốn CPU (CPU Bound) chứ không tốn I/O,
    # nên hàm parse() giữ nguyên là hàm đồng bộ (sync) thông thường.
    class NovelParser(ABC):
        @abstractmethod
        def parse(self, html_content: str) -> NovelChapter:
            pass
    
    class TruyenFullParser(NovelParser):
        def parse(self, html_content: str) -> NovelChapter:
            soup = BeautifulSoup(html_content, 'html.parser')
            title = soup.find('a', class_='chapter-title').text.strip()
            content = soup.find('div', class_='chapter-c').text.strip()
            return NovelChapter(title=title, content=content)
    
    # Interface lưu trữ dạng Async
    class AsyncTextStorage(ABC):
        @abstractmethod
        async def save_text(self, chapter: NovelChapter) -> None:
            pass
    
    # Triển khai lưu file cục bộ (Giả lập async hoặc dùng thư viện aiofiles)
    class AsyncLocalFileSaver(AsyncTextStorage):
        async def save_text(self, chapter: NovelChapter) -> None:
            # Trong thực tế dự án lớn, bạn nên dùng thư viện 'aiofiles' để ghi file async thực sự.
            # Ở đây ta giả lập một tác vụ chờ ngắn để minh họa luồng async.
            await asyncio.sleep(0.01) 
            with open(f"{chapter.title}.txt", "w", encoding="utf-8") as f:
                f.write(chapter.content)
            print(f"✅ Đã lưu xong: {chapter.title}")
    

* * *

## Bước 2: Nâng cấp lớp `NovelCrawlerEngine` thành Async

Chúng ta sẽ truyền vào lớp Engine này một `session` của `aiohttp` để tái sử dụng kết nối (Connection Pooling), giúp tăng tốc độ tải file và tiết kiệm tài nguyên hệ thống.
    
    
    class AsyncNovelCrawlerEngine:
        def __init__(self, parser: NovelParser, storage: AsyncTextStorage, session: aiohttp.ClientSession):
            self.parser = parser
            self.storage = storage
            self.session = session  # DI: Bơm aiohttp session từ ngoài vào
    
        # Nâng cấp thành hàm async
        async def crawl_single_chapter(self, url: str) -> None:
            try:
                # Tải HTML bất đồng bộ không gây nghẽn hệ thống
                async with self.session.get(url, timeout=10) as response:
                    if response.status != 200:
                        print(f"❌ Lỗi tải trang {url}: Mã lỗi {response.status}")
                        return
                    html_content = await response.text()
    
                # Phân tách HTML (Tác vụ đồng bộ nhanh)
                chapter_data = self.parser.parse(html_content)
    
                # Lưu trữ dữ liệu bất đồng bộ
                await self.storage.save_text(chapter_data)
                
            except Exception as e:
                print(f"💥 Lỗi khi xử lý link {url}: {e}")
    

* * *

## Bước 3: Ráp nối và Kích hoạt cào hàng loạt (Concurrent Crawling)

Thay vì cào từng chương theo thứ tự (Chương 1 xong mới đến Chương 2), chúng ta sẽ tạo ra danh sách các tác vụ (`tasks`) và dùng hàm `asyncio.gather` để phát lệnh tải tất cả các chương cùng một lúc.
    
    
    async def main():
        # Danh sách các link chương truyện cần cào
        urls = [
            "https://truyenfull.vn",
            "https://truyenfull.vn",
            "https://truyenfull.vn",
            "https://truyenfull.vn",
            "https://truyenfull.vn",
        ]
    
        # Khởi tạo các phần phụ thuộc (DI)
        parser = TruyenFullParser()
        storage = AsyncLocalFileSaver()
    
        # Tạo một Session quản lý kết nối mạng tập trung
        async with aiohttp.ClientSession() as session:
            # Khởi tạo Engine
            engine = AsyncNovelCrawlerEngine(parser=parser, storage=storage, session=session)
            
            print(f"🚀 Bắt đầu cào đồng thời {len(urls)} chương truyện...")
            
            # Tạo danh sách các task bất đồng bộ
            tasks = [engine.crawl_single_chapter(url) for url in urls]
            
            # Kích hoạt chạy đồng thời toàn bộ các task và chờ kết quả
            await asyncio.gather(*tasks)
            
            print("🎉 Hoàn thành toàn bộ tiến trình cào truyện!")
    
    if __name__ == "__main__":
        # Kích hoạt vòng lặp sự kiện (Event Loop) của Asyncio
        asyncio.run(main())
    

* * *

## 🛡️ Kỹ thuật nâng cao: Giới hạn số lượng Request đồng thời (Rate Limiting)

Nếu danh sách của bạn có 1000 chương và bạn dùng `asyncio.gather` trực tiếp như trên, Python sẽ gửi 1000 request cùng một thời điểm lên máy chủ của trang truyện. Hành động này sẽ ngay lập tức khiến IP của bạn bị Block (Chặn) vì hệ thống chống DDoS của họ phát hiện.

Để áp dụng chuẩn SOLID, bạn có thể bọc thêm một cơ chế kiểm soát số lượng request đồng thời bằng `asyncio.Semaphore` mà không cần sửa đổi logic cốt lõi của Engine:
    
    
    class ControlledAsyncNovelCrawlerEngine(AsyncNovelCrawlerEngine):
        def __init__(self, parser: NovelParser, storage: AsyncTextStorage, session: aiohttp.ClientSession, max_concurrent: int):
            super().__init__(parser, storage, session)
            # Giới hạn số lượng tác vụ chạy song song tối đa (ví dụ: chỉ cho phép 3 request cùng lúc)
            self.semaphore = asyncio.Semaphore(max_concurrent)
    
        async def crawl_single_chapter(self, url: str) -> None:
            # Chỉ khi nào có "vé" từ semaphore thì request mới được thực thi, còn lại phải xếp hàng chờ
            async with self.semaphore:
                await super().crawl_single_chapter(url)
    

Khi chạy trong hàm `main()`, bạn chỉ cần đổi tên lớp khởi tạo thành `ControlledAsyncNovelCrawlerEngine(..., max_concurrent=3)` là hệ thống sẽ tự động xếp hàng và cào tối đa 3 chương cùng lúc, vừa nhanh vừa an toàn!

* * *

Nếu bạn muốn nâng cấp hệ thống cào truyện này lên mức độ "sản xuất" (Production-ready), hãy cho tôi biết:

  * Bạn có muốn tích hợp Cơ chế tự động thử lại (Retry Mechanism) khi mạng lỗi hoặc bị timeout không?
  * Hay bạn muốn tìm hiểu cách sử dụng Queue (`asyncio.Queue`) để tạo mô hình Người sản xuất - Người tiêu dùng (Producer-Consumer), giúp vừa tìm link chương mới vừa cào cuốn chiếu liên tục?