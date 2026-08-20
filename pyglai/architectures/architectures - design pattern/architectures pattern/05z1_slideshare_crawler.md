Dưới đây là thiết kế chi tiết cho ứng dụng Crawl Book từ SlideShare theo kiến trúc Event-Driven Architecture (EDA - Kiến trúc hướng sự kiện).

Trong thiết kế này, thay vì các thành phần gọi trực tiếp lẫn nhau (như trong MVC hay Clean Architecture), hệ thống vận hành hoàn toàn bằng cách phát (Publish) và lắng nghe (Consume) các sự kiện thông qua một Event Broker. Để đơn giản, gọn nhẹ và không cần cài đặt các hệ thống cồng kềnh như Kafka hay RabbitMQ, chúng ta sẽ sử dụng Redis Pub/Sub làm Event Broker tốc độ cao.

* * *

## 🌟 Sơ đồ Luồng Sự kiện của Ứng dụng (EDA)
    
    
    +------------------------------------------------------------------------+
    
    |                          Event Broker (Redis)                          |
    +------------------------------------------------------------------------+
         ^                                ^                            ^
    
         | (Publish)                      | (Publish)                  | (Publish)
    [1. Request Cào]               [2. Ảnh Đã Tải]              [3. PDF Hoàn Thành]
    
         |                                |                            |
         v                                v                            v
    +------------------+         +------------------+         +------------------+
    
    | Crawler Executor |         | Downloader Worker|         |   PDF Worker     |
    | (Lắng nghe:      |         | (Lắng nghe:      |         | (Lắng nghe:      |
    |  "CrawlRequested")         | "MetadataFetched")         | "SlidesDownloaded")
    +------------------+         +------------------+         +------------------+
    

  1. Sự kiện `CrawlRequested`: Được kích hoạt khi người dùng gõ lệnh CLI. `Crawler Executor` sẽ nhận sự kiện này để cào HTML và lấy danh sách link ảnh.
  2. Sự kiện `MetadataFetched`: Được phát ra sau khi cào xong HTML. `Downloader Worker` nhận sự kiện này và tải toàn bộ ảnh slide bất đồng bộ, lưu vào thư mục `output/<book-name>/`.
  3. Sự kiện `SlidesDownloaded`: Được phát ra khi ảnh tải xong. `PDF Worker` nhận sự kiện này, đọc các ảnh từ thư mục và đóng gói thành file PDF bằng Fitz (PyMuPDF).



* * *

## 📂 Cấu trúc thư mục ứng dụng EDA
    
    
    slideshare_eda/
    │
    ├── broker/                      # Cấu hình kết nối hạ tầng truyền tin
    │   ├── __init__.py
    │   └── redis_client.py          # Kết nối và định nghĩa hàm Pub/Sub với Redis
    │
    ├── events/                      # Định nghĩa cấu trúc (Schema) các sự kiện
    │   ├── __init__.py
    │   └── schemas.py               # Các sự kiện: CrawlRequested, MetadataFetched, SlidesDownloaded
    │
    ├── workers/                     # Các bộ xử lý sự kiện độc lập (Event Handlers)
    │   ├── __init__.py
    │   ├── crawler_worker.py        # Xử lý cào HTML lấy danh sách slide
    │   ├── downloader_worker.py     # Xử lý tải ảnh slide bất đồng bộ (Aiohttp)
    │   └── pdf_worker.py            # Xử lý gộp ảnh thành PDF bằng PyMuPDF (Fitz)
    │
    ├── output/                      # Thư mục chứa kết quả (Tự động sinh ra)
    │   └── [book-name]/
    │
    ├── main.py                      # Giao diện CLI (Click) dùng để phát sự kiện mở đầu
    └── event_hub.py                 # Tiến trình trung tâm quản lý và điều phối các Worker
    

Để chạy ứng dụng này, hãy cài đặt các thư viện sau:
    
    
    pip install beautifulsoup4 requests pymupdf aiohttp click redis
    

_Lưu ý: Bạn cần có một máy chủ Redis đang chạy (mặc định tại`localhost:6379`)._

* * *

## 💻 Mã nguồn chi tiết theo kiến trúc EDA

## 1\. Định nghĩa các Sự kiện (`events/schemas.py`)

Mọi sự kiện trong hệ thống được định nghĩa tường minh để đảm bảo dữ liệu truyền qua Broker luôn nhất quán.
    
    
    # events/schemas.py
    import json
    
    class Event:
        def to_json(self) -> str:
            return json.dumps(self.__dict__)
    
    class CrawlRequestedEvent(Event):
        def __init__(self, url: str):
            self.url = url
    
    class MetadataFetchedEvent(Event):
        def __init__(self, title: str, safe_title: str, slide_urls: list):
            self.title = title
            self.safe_title = safe_title
            self.slide_urls = slide_urls
    
    class SlidesDownloadedEvent(Event):
        def __init__(self, safe_title: str, image_paths: list):
            self.safe_title = safe_title
            self.image_paths = image_paths
    

## 2\. Cấu hình Kết nối Broker (`broker/redis_client.py`)
    
    
    # broker/redis_client.py
    import redis
    
    class RedisEventBroker:
        def __init__(self, host='localhost', port=6379):
            # Kết nối tới Redis Server
            self.client = redis.Redis(host=host, port=port, decode_responses=True)
    
        def publish(self, channel: str, event_data: str):
            """Phát sự kiện lên một kênh cụ thể"""
            self.client.publish(channel, event_data)
    

## 3\. Các Worker xử lý sự kiện độc lập (`workers/`)

  * Crawler Worker (`workers/crawler_worker.py`): Lắng nghe kênh `CrawlRequested`. Xử lý xong thì phát sự kiện lên kênh `MetadataFetched`.


    
    
    # workers/crawler_worker.py
    import re
    import json
    import requests
    from bs4 import BeautifulSoup
    from events.schemas import MetadataFetchedEvent
    
    class CrawlerWorker:
        def __init__(self, broker):
            self.broker = broker
    
        def handle(self, message_data: str):
            data = json.loads(message_data)
            url = data['url']
            print(f"[*] [Crawler] Nhận sự kiện cào URL: {url}")
    
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(url, headers=headers)
            if res.status_code != 200:
                print(f"[❌] [Crawler] Không thể truy cập SlideShare: {res.status_code}")
                return
    
            soup = BeautifulSoup(res.text, 'html.parser')
            title_tag = soup.find('h1') or soup.find('meta', {'property': 'og:title'})
            title = title_tag.text.strip() if title_tag else "Untitled"
            safe_title = re.sub(r'[\\/*?:"<>| ]', '_', title).strip('_')
    
            slide_urls = []
            for img in soup.find_all('img'):
                src = img.get('data-full') or img.get('data-normal') or img.get('src')
                if src and "slide-" in src:
                    clean_url = src.split('?')[0]
                    if clean_url not in slide_urls:
                        slide_urls.append(clean_url)
    
            if not slide_urls:
                print("[❌] [Crawler] Không tìm thấy ảnh slide.")
                return
    
            # Phát sự kiện tiếp theo vào hệ thống
            next_event = MetadataFetchedEvent(title, safe_title, slide_urls)
            self.broker.publish("MetadataFetched", next_event.to_json())
            print(f"[+] [Crawler] Hoàn thành. Đã phát sự kiện 'MetadataFetched' cho: {title}")
    

  * Downloader Worker (`workers/downloader_worker.py`): Lắng nghe kênh `MetadataFetched`. Sử dụng cơ chế `Async/Await` tải ảnh song song, ghi file xong thì phát sự kiện lên kênh `SlidesDownloaded`.


    
    
    # workers/downloader_worker.py
    import os
    import json
    import asyncio
    import aiohttp
    from events.schemas import SlidesDownloadedEvent
    
    class DownloaderWorker:
        def __init__(self, broker):
            self.broker = broker
    
        async def _download_slide(self, session, url, save_path):
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    with open(save_path, "wb") as f:
                        f.write(content)
                    return save_path
    
        async def _download_all(self, urls, safe_title):
            output_dir = os.path.join("output", safe_title)
            os.makedirs(output_dir, exist_ok=True)
            
            async with aiohttp.ClientSession() as session:
                tasks = []
                for index, url in enumerate(urls, start=1):
                    path = os.path.join(output_dir, f"slide_{index:03d}.jpg")
                    tasks.append(self._download_slide(session, url, path))
                return await asyncio.gather(*tasks)
    
        def handle(self, message_data: str):
            data = json.loads(message_data)
            safe_title = data['safe_title']
            slide_urls = data['slide_urls']
            print(f"[*] [Downloader] Nhận sự kiện tải {len(slide_urls)} slides cho: {safe_title}")
    
            # Chạy bất đồng bộ tiến trình tải ảnh
            image_paths = asyncio.run(self._download_all(slide_urls, safe_title))
            print("[+] [Downloader] Đã lưu toàn bộ ảnh slide xuống ổ đĩa.")
    
            # Phát sự kiện thông báo tải xong ảnh
            next_event = SlidesDownloadedEvent(safe_title, image_paths)
            self.broker.publish("SlidesDownloaded", next_event.to_json())
    

  * PDF Worker (`workers/pdf_worker.py`): Lắng nghe kênh `SlidesDownloaded`. Chịu trách nhiệm gộp ảnh thành file PDF bằng Fitz (PyMuPDF).


    
    
    # workers/pdf_worker.py
    import os
    import json
    import fitz  # PyMuPDF
    
    class PdfWorker:
        def __init__(self, broker):
            self.broker = broker
    
        def handle(self, message_data: str):
            data = json.loads(message_data)
            safe_title = data['safe_title']
            image_paths = data['image_paths']
            print(f"[*] [PDF Worker] Nhận sự kiện đóng gói PDF cho: {safe_title}")
    
            output_pdf = os.path.join("output", safe_title, f"{safe_title}.pdf")
            doc = fitz.open()
            
            for img_path in image_paths:
                if os.path.exists(img_path):
                    img_doc = fitz.open(img_path)
                    pdf_bytes = img_doc.convert_to_pdf()
                    img_doc.close()
                    
                    page_doc = fitz.open("pdf", pdf_bytes)
                    doc.insert_pdf(page_doc)
                    page_doc.close()
    
            doc.save(output_pdf)
            doc.close()
            print(f"[🎉] [PDF Worker] XUẤT FILE PDF THÀNH CÔNG: {output_pdf}")
    

* * *

## 🎛️ Tiến trình Điều phối Trung tâm (`event_hub.py`)

File này chạy như một dịch vụ nền (Daemon) liên tục giữ kết nối với Redis Pub/Sub, lắng nghe mọi kênh sự kiện và phân phối tin nhắn đến đúng Worker phụ trách.
    
    
    # event_hub.py
    from broker.redis_client import RedisEventBroker
    from workers.crawler_worker import CrawlerWorker
    from workers.downloader_worker import DownloaderWorker
    from workers.pdf_worker import PdfWorker
    
    def start_event_hub():
        broker = RedisEventBroker()
        pubsub = broker.client.pubsub()
    
        # Khởi tạo các Worker xử lý
        crawler = CrawlerWorker(broker)
        downloader = DownloaderWorker(broker)
        pdf_processor = PdfWorker(broker)
    
        # Đăng ký các kênh sự kiện tương ứng
        pubsub.subscribe(**{
            'CrawlRequested': lambda msg: crawler.handle(msg['data']),
            'MetadataFetched': lambda msg: downloader.handle(msg['data']),
            'SlidesDownloaded': lambda msg: pdf_processor.handle(msg['data'])
        })
    
        print("[🚀] Event Hub đang chạy ngầm và lắng nghe các sự kiện hệ thống...")
        pubsub.run_in_thread(sleep_time=0.01) # Chạy ngầm trong một luồng riêng biệt
    
    if __name__ == "__main__":
        import time
        start_event_hub()
        while True:
            time.sleep(1) # Giữ cho tiến trình chính không bị tắt
    

* * *

## 🚀 Giao diện CLI gửi lệnh Kích hoạt (`main.py`)

Khi người dùng gõ lệnh, file `main.py` không thực hiện cào dữ liệu ngay. Nó chỉ làm đúng một việc: Bắn sự kiện mở màn `CrawlRequested` vào hệ thống rồi kết thúc công việc.
    
    
    # main.py
    import click
    from broker.redis_client import RedisEventBroker
    from events.schemas import CrawlRequestedEvent
    
    @click.command()
    @click.argument('url', type=str)
    def trigger_crawl(url):
        """Crawl sách SlideShare theo mô hình Kiến trúc hướng sự kiện (EDA)."""
        broker = RedisEventBroker()
        
        # Tạo sự kiện mở đầu kịch bản
        event = CrawlRequestedEvent(url=url)
        
        # Bắn sự kiện lên Broker
        broker.publish("CrawlRequested", event.to_json())
        click.secho("[+] Đã phát sự kiện 'CrawlRequested' vào hệ thống thành công!", fg="green")
    
    if __name__ == "__main__":
        trigger_crawl()
    

* * *

## 🛠️ Hướng dẫn Vận hành Hệ thống EDA

Do hệ thống hoạt động dựa trên các tiến trình độc lập và truyền tin qua sự kiện, bạn cần vận hành theo các bước sau:

  1. Bước 1: Bật máy chủ Redis trên máy tính của bạn.
  2. Bước 2: Khởi động trung tâm xử lý sự kiện ngầm (để mở các cổng lắng nghe):
         
         python event_hub.py
         

  3. Bước 3: Mở một Terminal mới và gõ lệnh CLI để ném URL vào hệ thống:
         
         python main.py https://slideshare.net
         




## 🎯 Ưu điểm lớn nhất của EDA áp dụng vào bài toán này:

  * Tính bất đồng bộ tuyệt đối (Non-blocking): CLI (`main.py`) chạy xong ngay lập tức trong 0.1 giây. Người dùng không cần treo Terminal để đợi tải ảnh hay xuất PDF.
  * Tách biệt hoàn toàn (Decoupling): `CrawlerWorker` hoàn toàn không biết đến sự tồn tại của `PdfWorker`. Nó chỉ cần biết: "Tôi làm xong việc của tôi, tôi quăng sự kiện lên tổng đài Redis, ai muốn làm gì tiếp theo thì làm".
  * Dễ dàng mở rộng: Nếu sau này bạn muốn thêm tính năng _"Khi tải sách xong thì tự động gửi tin nhắn Telegram báo cáo"_ , bạn chỉ cần viết thêm một `TelegramWorker` mới và cấu hình cho nó lắng nghe kênh `SlidesDownloaded` là xong, tuyệt đối không cần sửa một dòng code nào của 3 worker cũ.



Chúng ta đã hoàn thành xuất sắc việc thiết kế cùng một ứng dụng bò cào SlideShare qua cả 5 mô hình kiến trúc phổ biến nhất: Clean, Onion, Microservices, MVC, MVT, và Event-Driven. Bạn có câu hỏi nào về sự khác biệt giữa các mô hình này hoặc muốn chuyển sang phần tiếp theo của danh sách tổng hợp ban đầu không?