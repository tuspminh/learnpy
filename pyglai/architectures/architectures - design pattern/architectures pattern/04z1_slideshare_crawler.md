Để thiết kế ứng dụng cào sách SlideShare theo kiến trúc Microservices (Vi dịch vụ), chúng ta sẽ chia hệ thống lớn thành 3 dịch vụ độc lập chạy bằng FastAPI. Các dịch vụ này sẽ sở hữu cơ sở dữ liệu riêng và giao tiếp bất đồng bộ qua Message Broker (RabbitMQ) nhằm tăng tính chịu lỗi và khả năng mở rộng tối đa.

* * *

## 🌟 Sơ đồ Kiến trúc Microservices của Ứng dụng
    
    
                    +-------------------------------------------+
    
                    |         Client (Giao diện CLI / Web)      |
                    +-------------------------------------------+
                                          | (HTTP POST /crawl)
                                          v
                    +-------------------------------------------+
    
                    |               API Gateway                 |
                    +-------------------------------------------+
                                          | (Định tuyến Request)
                                          v
                    +-------------------------------------------+
    
                    |             1. Crawler Service            | ---> [ SQLite DB 1 ]
                    +-------------------------------------------+
                                          | 
                             (Phát sự kiện: "book_metadata_fetched")
                                          v
                    +-------------------------------------------+
    
                    |    Message Broker (RabbitMQ / Kombu)      |
                    +-------------------------------------------+
                            /                           \
    (Nhận event: "book_metadata_fetched")     (Nhận event: "slides_downloaded")
                          /                               \
                         v                                 v
        +---------------------------------+     +---------------------------------+
    
        |       2. Downloader Service     |     |        3. PDF Export Service    |
        +---------------------------------+     +---------------------------------+
    
        | Tải ảnh slide bất đồng bộ       |     | Gộp file ảnh sang PDF qua Fitz  |
        | Lưu vào: output/book-name/      |     | Lưu vào: output/book-name/.pdf  |
        +---------------------------------+     +---------------------------------+
    

* * *

## 📂 Cấu trúc thư mục tổng thể (Monorepo)
    
    
    slideshare_microservices/
    │
    ├── shared/                      # Mã nguồn, cấu hình DTO dùng chung cho các service
    │   ├── __init__.py
    │   └── events.py                # Định nghĩa cấu trúc tin nhắn sự kiện (Event Schemas)
    │
    ├── crawler_service/             # Service 1: Cào HTML SlideShare lấy metadata
    │   ├── main.py                  # FastAPI + Endpoint tiếp nhận URL từ Client
    │   ├── Dockerfile
    │   └── requirements.txt
    │
    ├── downloader_service/          # Service 2: Worker tải ảnh slide bất đồng bộ (Aiohttp)
    │   ├── worker.py                # Lắng nghe RabbitMQ -> Tải ảnh -> Lưu vào ổ đĩa chung
    │   ├── Dockerfile
    │   └── requirements.txt
    │
    ├── pdf_service/                 # Service 3: Worker đóng gói ảnh thành file PDF bằng Fitz
    │   ├── worker.py                # Lắng nghe RabbitMQ -> Xuất file PDF bằng PyMuPDF
    │   ├── Dockerfile
    │   └── requirements.txt
    │
    ├── output/                      # Ổ đĩa dùng chung (Shared Volume) giữa các Container
    │   └── [book-name]/
    │
    └── docker-compose.yml           # Khởi chạy RabbitMQ và toàn bộ 3 Services cùng lúc
    

Để truyền nhận tin nhắn mượt mà trong Python, chúng ta sử dụng thư viện Kombu (bộ thư viện messaging mã nguồn mở làm nền tảng cho Celery) để kết nối với RabbitMQ.

* * *

## 💻 Mã nguồn chi tiết của từng Microservice

## 0\. Các Sự kiện dùng chung (`shared/events.py`)
    
    
    # shared/events.py
    from pydantic import BaseModel
    from typing import List
    
    class BookMetadataEvent(BaseModel):
        title: str
        safe_title: str
        slide_urls: List[str]
    
    class SlidesDownloadedEvent(BaseModel):
        safe_title: str
        image_paths: List[str]
    

## 1\. Crawler Service (`crawler_service/main.py`)

Tiếp nhận yêu cầu HTTP từ người dùng, sử dụng `BeautifulSoup` cào nhanh danh sách URL ảnh, sau đó bắn sự kiện lên RabbitMQ rồi lập tức trả về phản hồi cho Client (không bắt người dùng ngồi chờ tải ảnh).
    
    
    # crawler_service/main.py
    import re
    import json
    import requests
    from bs4 import BeautifulSoup
    from fastapi import FastAPI, HTTPException
    from kombu import Connection, Exchange, Queue
    
    app = FastAPI(title="SlideShare Crawler Service")
    
    # Cấu hình kết nối RabbitMQ
    RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672//"
    exchange = Exchange("slideshare_events", type="direct")
    
    @app.post("/crawl")
    def start_crawl(slideshare_url: str):
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(slideshare_url, headers=headers)
        if res.status_code != 200:
            raise HTTPException(status_code=400, detail="Không thể truy cập đường dẫn SlideShare")
    
        soup = BeautifulSoup(res.text, 'html.parser')
        title_tag = soup.find('h1') or soup.find('meta', {'property': 'og:title'})
        title = title_tag.text.strip() if title_tag else "Untitled_Book"
        safe_title = re.sub(r'[\\/*?:"<>| ]', '_', title).strip('_')
    
        slide_urls = []
        for img in soup.find_all('img'):
            src = img.get('data-full') or img.get('data-normal') or img.get('src')
            if src and "slide-" in src:
                clean_url = src.split('?')[0]
                if clean_url not in slide_urls:
                    slide_urls.append(clean_url)
    
        if not slide_urls:
            raise HTTPException(status_code=422, detail="Không tìm thấy ảnh slide nào.")
    
        # Đóng gói dữ liệu sự kiện
        payload = {
            "title": title,
            "safe_title": safe_title,
            "slide_urls": slide_urls
        }
    
        # Phát sự kiện sang RabbitMQ để Downloader Service xử lý
        with Connection(RABBITMQ_URL) as conn:
            producer = conn.Producer(serializer="json")
            producer.publish(
                payload,
                exchange=exchange,
                routing_key="book_metadata_fetched",
                declare=[exchange]
            )
    
        return {"status": "Đang xử lý", "message": f"Sách '{title}' đã được đưa vào hàng đợi tải xuống."}
    

## 2\. Downloader Service (`downloader_service/worker.py`)

Là một tiến trình worker chạy ngầm liên tục. Khi nhận được sự kiện `book_metadata_fetched`, nó kích hoạt cơ chế [Async/Await Model] (`aiohttp`) để kéo toàn bộ ảnh về ổ đĩa chung với tốc độ cao nhất, rồi phát tiếp sự kiện thông báo đã tải xong.
    
    
    # downloader_service/worker.py
    import os
    import asyncio
    import aiohttp
    from kombu import Connection, Exchange, Queue
    from kombu.mixins import ConsumerMixin
    
    RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672//"
    exchange = Exchange("slideshare_events", type="direct")
    queue = Queue("download_queue", exchange, routing_key="book_metadata_fetched")
    
    async def download_slide(session, url, path):
        async with session.get(url) as res:
            if res.status == 200:
                content = await res.read()
                with open(path, "wb") as f:
                    f.write(content)
                return path
    
    async def download_all(slide_urls, safe_title):
        output_dir = os.path.join("/output", safe_title) # Lưu vào thư mục /output chung
        os.makedirs(output_dir, exist_ok=True)
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for index, url in enumerate(slide_urls, start=1):
                path = os.path.join(output_dir, f"slide_{index:03d}.jpg")
                tasks.append(download_slide(session, url, path))
            return await asyncio.gather(*tasks)
    
    class DownloaderWorker(ConsumerMixin):
        def __init__(self, connection):
            self.connection = connection
    
        def get_consumers(self, Consumer, channel):
            return [Consumer(queues=[queue], callbacks=[self.process_task])]
    
        def process_task(self, body, message):
            safe_title = body['safe_title']
            slide_urls = body['slide_urls']
            print(f"[*] Tiến hành tải bất đồng bộ {len(slide_urls)} slides cho: {safe_title}")
    
            # Chạy coroutine async trong môi trường worker đồng bộ
            image_paths = asyncio.run(download_all(slide_urls, safe_title))
            
            # Gửi sự kiện tiếp theo sang PDF Service
            producer = self.connection.Producer(serializer="json")
            producer.publish(
                {"safe_title": safe_title, "image_paths": image_paths},
                exchange=exchange,
                routing_key="slides_downloaded"
            )
            message.ack() # Xác nhận đã xử lý xong tin nhắn
    
    if __name__ == "__main__":
        with Connection(RABBITMQ_URL) as conn:
            print("[*] Downloader Service Worker đang lắng nghe...")
            DownloaderWorker(conn).run()
    

## 3\. PDF Export Service (`pdf_service/worker.py`)

Chịu trách nhiệm duy nhất là xử lý file và tính toán nặng: Đọc danh sách ảnh từ ổ đĩa chung, dùng thư viện PyMuPDF (Fitz) nén gộp lại thành file PDF đích và lưu ngay tại thư mục của cuốn sách.
    
    
    # pdf_service/worker.py
    import os
    import fitz # PyMuPDF
    from kombu import Connection, Exchange, Queue
    from kombu.mixins import ConsumerMixin
    
    RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672//"
    exchange = Exchange("slideshare_events", type="direct")
    queue = Queue("pdf_queue", exchange, routing_key="slides_downloaded")
    
    class PdfExportWorker(ConsumerMixin):
        def __init__(self, connection):
            self.connection = connection
    
        def get_consumers(self, Consumer, channel):
            return [Consumer(queues=[queue], callbacks=[self.process_task])]
    
        def process_task(self, body, message):
            safe_title = body['safe_title']
            image_paths = body['image_paths']
            
            pdf_path = os.path.join("/output", safe_title, f"{safe_title}.pdf")
            print(f"[*] Đang đóng gói file PDF bằng Fitz cho: {safe_title}")
    
            doc = fitz.open()
            for img_path in image_paths:
                if os.path.exists(img_path):
                    img_doc = fitz.open(img_path)
                    pdf_bytes = img_doc.convert_to_pdf()
                    img_doc.close()
                    
                    page_doc = fitz.open("pdf", pdf_bytes)
                    doc.insert_pdf(page_doc)
                    page_doc.close()
            
            doc.save(pdf_path)
            doc.close()
            print(f"[🎉] XUẤT PDF THÀNH CÔNG: {pdf_path}")
            message.ack()
    
    if __name__ == "__main__":
        with Connection(RABBITMQ_URL) as conn:
            print("[*] PDF Export Service Worker đang lắng nghe...")
            PdfExportWorker(conn).run()
    

* * *

## 🐳 Cấu hình Đóng gói và Vận hành (`docker-compose.yml`)

Để hệ thống Microservices hoạt động trên máy tính của bạn, file Compose này sẽ đứng ra dựng cụm máy chủ ảo, tạo mạng nội bộ và ánh xạ chung một ổ đĩa cứng `/output` (Shared Volume) để các Service cùng ghi đọc file ảnh.
    
    
    version: '3.8'
    
    services:
      rabbitmq:
        image: rabbitmq:3-management
        ports:
          - "5672:5672"
          - "15672:15672" # Giao diện quản lý hàng đợi trực quan
    
      crawler_service:
        build: ./crawler_service
        command: uvicorn main:app --host 0.0.0.0 --port 8000
        ports:
          - "8000:8000"
        depends_on:
          - rabbitmq
    
      downloader_service:
        build: ./downloader_service
        command: python worker.py
        volumes:
          - shared_output:/output
        depends_on:
          - rabbitmq
    
      pdf_service:
        build: ./pdf_service
        command: python worker.py
        volumes:
          - shared_output:/output
        depends_on:
          - rabbitmq
    
    volumes:
      shared_output:
        driver: local
        driver_opts:
          type: none
          o: bind
          device: ./output # Ánh xạ thẳng ra thư mục output trên máy thật của bạn
    

* * *

## 📊 Điểm mạnh vượt trội của Thiết kế Microservices này:

  * Khả năng chịu tải cực hạn (Asynchronous Scaling): Giả sử người dùng gửi liên tục 100 URL sách cùng lúc. `Crawler Service` chỉ mất 0.5 giây để cào HTML và đẩy sự kiện vào hàng đợi rồi báo "Nhận lệnh thành công". Hệ thống không bao giờ bị sập hay nghẽn mạng (Timeout).
  * Mở rộng luồng tải độc lập: Nếu tốc độ tải ảnh từ SlideShare bị chậm, bạn chỉ cần gõ lệnh `docker-compose up --scale downloader_service=5` để nhân bản lên 5 Worker cùng chia nhau tải ảnh song song từ hàng đợi, trong khi code của các service khác giữ nguyên.
  * Cô lập lỗi hoàn toàn: Nếu thư viện PyMuPDF (`fitz`) bị lỗi bộ nhớ (Segmentation Fault) làm sập `pdf_service`, các file ảnh slide đã tải về vẫn nằm nguyên vẹn an toàn tại thư mục `output/`. Khi bạn sửa lỗi và bật lại `pdf_service`, nó tự động nhặt các tin nhắn tồn đọng trong hàng đợi RabbitMQ để xuất tiếp PDF mà không cần cào lại từ đầu.



Chúng ta đã đi qua toàn bộ các mô hình kiến trúc lớn của phần mềm. Bạn có muốn chuyển tiếp sang tìm hiểu các mẫu thiết kế cấu trúc chi tiết cấp thấp hơn là Design Patterns (Creational, Structural, Behavioral) trong Python không?