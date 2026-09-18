Với bài toán cào hàng loạt (Bulk) một lần, tích hợp 2 - 3 nguồn truyện và không cần render Javascript, hệ thống của bạn sẽ thiên về tối ưu băng thông mạng (I/O) và tốc độ ghi dữ liệu (Throughput).

Dưới đây là thiết kế chi tiết tinh chỉnh lại từ mô hình DDD ban đầu để tối ưu hóa hiệu năng cho bài toán Bulk Crawl của bạn.

* * *

## 1\. Kiến trúc Bounded Context Tối ưu cho Bulk Crawl

Vì cào hàng loạt, chúng ta không cần hệ thống Event-Driven quá phức tạp theo kiểu Pub/Sub thời gian thực (như Kafka). Thay vào đó, kiến trúc sẽ đi theo mô hình Pipeline (Đường ống xử lý tuần tự) kết hợp Hàng đợi bộ nhớ (In-memory Queue) như Redis hoặc chính `asyncio.Queue` của Python.
    
    
    [Crawler] -> Sinh danh sách URL -> Đẩy vào URL Queue (Redis/Memory)
                                           │
                                           ▼
    [Fetcher] -> Lấy URL -> Download HTML -> Đẩy vào Raw HTML Queue
                                           │
                                           ▼
    [Parser]  -> Lấy HTML -> Bóc tách text -> Trả về Clean Data
                                           │
                                           ▼
    [Storage] -> Ghi hàng loạt (Bulk Insert) vào Database
    

* * *

## 2\. Thiết kế Chiến lược xử lý cho 2 - 3 nguồn không JS

Vì không có JS, bạn chỉ cần dùng các thư viện request thuần túy. Để cào bulk nhanh nhất bằng Python, bộ công cụ tối ưu nhất là: `httpx` (hoặc `aiohttp`) kết hợp với `selectolax` (nhanh gấp 10-20 lần `BeautifulSoup`).

## A. Kiến trúc của Fetcher (Tải thô)

Đối với cào bulk, Fetcher là "cổ chai" nếu bị chặn IP. Do đó, tầng Infrastructure của `Data Ingestion Context` cần triển khai:

  * Connection Pooling: Giữ tối đa số lượng connection đồng thời kết nối tới nguồn để tránh overhead bắt tay SSL/TLS liên tục.
  * Rate Limiting & Semaphore: Giới hạn số lượng request đồng thời (ví dụ: tối đa 10-20 request/giây trên một domain) để tránh bị ăn gậy `429 Too Many Requests`.
  * Proxy Rotator: Sử dụng một list proxy để xoay tua sau mỗi `N` request.



## B. Kiến trúc của Parser (Phân tách cấu trúc)

Vì bạn chỉ có 2-3 nguồn, việc áp dụng Strategy Pattern là cực kỳ gọn nhẹ và sạch sẽ.

  * Bạn tạo một lớp trừu tượng `BaseParser`.
  * Viết 3 class con cụ thể: `Nguon1Parser`, `Nguon2Parser`, `Nguon3Parser`.
  * Dùng một `ParserFactory` để lấy ra đúng Parser dựa trên domain của URL đang cào.



## C. Kiến trúc của Storage (Lưu trữ)

  * Tuyệt đối tránh: Cào xong 1 chương -> Lưu luôn vào DB 1 bản ghi. Việc này sẽ làm nghẽn Database do số lượng kết nối I/O quá nhiều.
  * Giải pháp: Sử dụng Batching (Gom hàng loạt). Khi tầng Parser trả về dữ liệu sạch, gom đủ 50 hoặc 100 chương rồi mới thực hiện một lệnh `Bulk Insert` duy nhất vào Database.



* * *

## 3\. Triển khai Code Concept Tối ưu cho Bulk Crawl (Python Asyncio)

Dưới đây là bản thiết kế code mẫu bằng Python, tận dụng `asyncio` để xử lý Bulk và áp dụng đúng tư tưởng phân tách trách nhiệm (DDD) cho 2-3 nguồn:
    
    
    import asyncio
    from abc import ABC, abstractmethod
    from dataclasses import dataclass
    from typing import List
    import httpx
    from selectolax.parser import HTMLParser
    
    # ==========================================
    # 1. DOMAIN LAYER (Parsing Context)
    # ==========================================
    @dataclass(frozen=True)
    class ChapterVO:
        novel_id: str
        chapter_num: int
        title: str
        content: str
    
    class BaseParser(ABC):
        @abstractmethod
        def parse(self, html: str, novel_id: str) -> ChapterVO:
            pass
    
    # Triển khai cụ thể cho Nguồn 1
    class Nguon1Parser(BaseParser):
        def parse(self, html: str, novel_id: str) -> ChapterVO:
            tree = HTMLParser(html)
            title = tree.css_first("h2.chapter-title").text(strip=True)
            # Gom các đoạn văn lại thành 1 đoạn text lớn hoặc giữ nguyên list tùy nhu cầu
            content = "\n".join([p.text(strip=True) for p in tree.css("div.chapter-content p")])
            return ChapterVO(novel_id, 1, title, content)
    
    # Triển khai cụ thể cho Nguồn 2
    class Nguon2Parser(BaseParser):
        def parse(self, html: str, novel_id: str) -> ChapterVO:
            tree = HTMLParser(html)
            title = tree.css_first(".title-ch").text(strip=True)
            content = tree.css_first("#content-txt").text(strip=True)
            return ChapterVO(novel_id, 1, title, content)
    
    class ParserFactory:
        @staticmethod
        def get_parser(source_type: str) -> BaseParser:
            parsers = {
                "nguon1": Nguon1Parser(),
                "nguon2": Nguon2Parser()
            }
            return parsers.get(source_type)
    
    # ==========================================
    # 2. INFRASTRUCTURE LAYER (Ingestion Context)
    # ==========================================
    class BulkFetcher:
        def __init__(self, max_concurrent: int = 10):
            # Giới hạn số lượng request chạy đồng thời để tránh bị block IP
            self.semaphore = asyncio.Semaphore(max_concurrent)
            self.client = httpx.AsyncClient(timeout=10.0)
    
        async def fetch(self, url: str) -> str:
            async with self.semaphore:
                try:
                    response = await self.client.get(url, headers={"User-Agent": "Mozilla/5.0..."})
                    if response.status_code == 200:
                        return response.text
                except Exception as e:
                    print(f"Lỗi khi tải URL {url}: {e}")
                return ""
    
    # ==========================================
    # 3. APPLICATION LAYER (Pipeline / Coordinator)
    # ==========================================
    class BulkScraperPipeline:
        def __init__(self, fetcher: BulkFetcher):
            self.fetcher = fetcher
            self.batch_buffer = []
            self.batch_size = 50  # Cứ 50 chương thì insert DB một lần
    
        async def worker(self, url_queue: asyncio.Queue, source_type: str, novel_id: str):
            """Worker chạy ngầm lấy URL từ hàng đợi để xử lý"""
            parser = ParserFactory.get_parser(source_type)
            
            while not url_queue.empty():
                url = await url_queue.get()
                
                # Fetch
                html = await self.fetcher.fetch(url)
                if html:
                    # Parse
                    chapter_data = parser.parse(html, novel_id)
                    
                    # Gom cụm dữ liệu sạch để chuẩn bị Bulk Insert
                    self.batch_buffer.append(chapter_data)
                    if len(self.batch_buffer) >= self.batch_size:
                        await self._flush_to_db()
                        
                url_queue.task_done()
    
        async def _flush_to_db(self):
            """Mô phỏng hàm Bulk Insert vào DB ở Storage Context"""
            if not self.batch_buffer:
                return
            print(f"[Database] Đang Bulk Insert {len(self.batch_buffer)} chương vào DB...")
            # Thực hiện logic ghi DB (Ví dụ: await db.insert_many(self.batch_buffer))
            self.batch_buffer.clear()
    
        async def run(self, urls: List[str], source_type: str, novel_id: str):
            # 1. Khởi tạo hàng đợi công việc
            queue = asyncio.Queue()
            for url in urls:
                await queue.put(url)
    
            # 2. Kích hoạt đồng thời 5 workers để cào bulk song song
            fetch_workers = [
                asyncio.create_task(self.worker(queue, source_type, novel_id))
                for _ in range(5)
            ]
            
            await queue.join()
            
            # 3. Đảm bảo những chương cuối cùng còn sót lại trong buffer được lưu hết
            await self._flush_to_db()
    

## 4\. Ưu điểm của kiến trúc này khi Cào Bulk

  * Tốc độ tối đa: Nhờ cơ chế `asyncio.Queue` và `Semaphore`, hệ thống có thể tải hàng trăm chương truyện cùng lúc mà không cần chờ đợi tuần tự, đồng thời vẫn kiểm soát được tốc độ để không làm sập web nguồn.
  * Tiết kiệm tài nguyên: Việc bóc tách bằng `selectolax` diễn ra trực tiếp trên luồng I/O mà không sinh ra quá nhiều overhead về CPU. Dữ liệu được giải phóng ngay sau khi parse xong và đưa vào mảng lưu trữ tạm thời.



Để hoàn thiện hệ thống, bạn có muốn trao đổi sâu hơn về:

  * Phương án xử lý khi cào bulk bị đứt gánh giữa chừng (lưu lại trạng thái checkpoint để cào tiếp)?
  * Lựa chọn loại Database phù hợp nhất để lưu và tối ưu hóa câu lệnh tìm kiếm/đọc truyện sau này?