Version:0.9 StartHTML:00000097 EndHTML:00438119 StartFragment:00000131 EndFragment:00438083 

Đây là một bài toán kinh điển và rất thực tế khi xây dựng hệ thống cào dữ liệu (Web Scraper) ở quy mô công nghiệp. Để quản lý trạng thái của hàng triệu URL mà không làm nghẽn hệ thống, chúng ta sẽ kết hợp sức mạnh xử lý ngầm của **Celery** , trạm trung chuyển dữ liệu **Redis** , và khả năng truyền tải dữ liệu thời gian thực của **FastAPI WebSocket**.

Dưới đây là kiến trúc toàn diện và mã nguồn chi tiết cho hệ thống của bạn.

* * *

🔥 Kiến Trúc Hệ Thống (Architecture)

  1. **Cơ sở dữ liệu (Redis/Database):** Lưu trữ danh sách URL và trạng thái của chúng (`pending`, `scraping`, `completed`, `failed`).
  2. **FastAPI Dashboard:**
     * Cung cấp API để thêm link mới (phân phối link).
     * Mở kết nối **WebSocket** để đẩy trạng thái cào (đang cào, lỗi, hoàn thành) lên giao diện Front-end theo thời gian thực.
  3. **Celery Worker:** Nhận link từ FastAPI qua Redis Broker, tiến hành cào dữ liệu, tải nội dung truyện và cập nhật trạng thái ngược lại cho FastAPI/Redis.



* * *

📦 Bước 1: Cấu hình Celery Worker (`tasks.py`)

File này định nghĩa tác vụ cào một link truyện cụ thể. Worker sẽ chạy độc lập.

python
    
    
    import time
    import random
    import requests
    from celery import Celery
    
    # Cấu hình Celery với Redis
    celery_app = Celery('scraper_tasks', 
                        broker='redis://localhost:6379/0', 
                        backend='redis://localhost:6379/0')
    
    @celery_app.task(bind=True)
    def crawl_story_page(self, url: str):
        """Tác vụ cào một trang truyện ngầm"""
        task_id = self.request.id
        print(f"[Worker] Bắt đầu cào: {url}")
        
        # 1. Thông báo cho hệ thống biết link này ĐANG ĐƯỢC CÀO
        self.update_state(state='PROGRESS', meta={'url': url, 'status': 'scraping'})
        
        try:
            # Giả lập thời gian cào web (từ 2 đến 5 giây) và tải nội dung
            time.sleep(random.randint(2, 5))
            
            # Giả lập tỷ lệ lỗi 15% để test tính năng link lỗi
            if random.random() < 0.15:
                raise Exception("Lỗi kết nối Cloudflare hoặc Selector CSS đã thay đổi!")
                
            # Giả lập cào thành công
            print(f"[Worker] Thành công: {url}")
            return {'url': url, 'status': 'completed', 'result': 'Đã lưu chương thành công'}
            
        except Exception as e:
            print(f"[Worker] Thất bại: {url} - Lỗi: {str(e)}")
            # Trả về trạng thái lỗi để lưu vào Result Backend
            return {'url': url, 'status': 'failed', 'error': str(e)}
    

Hãy thận trọng khi sử dụng mã.

* * *

🚀 Bước 2: Xây dựng FastAPI Server & WebSockets (`main.py`)

FastAPI đóng vai trò nhận link mới, đẩy vào Celery và giám sát tiến độ thông qua một Background Task để "bắn" dữ liệu qua WebSocket.

python
    
    
    import asyncio
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
    from pydantic import BaseModel
    from tasks import crawl_story_page, celery_app
    from celery.result import AsyncResult
    
    app = FastAPI()
    
    # Lưu trữ danh sách các task đang được theo dõi
    # Trong thực tế, bạn nên lưu thông tin này vào Redis hoặc Database (Postgres/MySQL)
    MONITORED_TASKS = {} 
    
    class LinkModel(BaseModel):
        url: str
    
    @app.post("/api/v1/crawl")
    def add_new_link(payload: LinkModel):
        """API tiếp nhận link mới và phân phối ngay cho Celery"""
        url = payload.url
        
        # Đẩy tác vụ vào hàng đợi Celery
        task = crawl_story_page.delay(url)
        
        # Lưu vết trạng thái ban đầu
        MONITORED_TASKS[task.id] = {
            "url": url,
            "status": "pending",
            "error": None
        }
        
        return {"message": "Đã xếp hàng link cào", "task_id": task.id}
    
    async def monitor_celery_status():
        """Hàm chạy ngầm cập nhật trạng thái liên tục từ Celery Result Backend"""
        while True:
            for task_id, info in list(MONITORED_TASKS.items()):
                # Kiểm tra trạng thái thực tế từ Celery
                result = AsyncResult(task_id, app=celery_app)
                
                if result.state == 'PROGRESS':
                    MONITORED_TASKS[task_id]['status'] = 'scraping'
                elif result.state == 'SUCCESS':
                    res_data = result.result
                    MONITORED_TASKS[task_id]['status'] = res_data.get('status', 'completed')
                    if res_data.get('status') == 'failed':
                        MONITORED_TASKS[task_id]['error'] = res_data.get('error')
                elif result.state == 'FAILURE':
                    MONITORED_TASKS[task_id]['status'] = 'failed'
                    MONITORED_TASKS[task_id]['error'] = str(result.info)
                    
            await asyncio.sleep(1) # Cập nhật mỗi giây một lần
    
    @app.on_event("startup")
    async def startup_event():
        # Kích hoạt vòng lặp theo dõi trạng thái ngay khi khởi động FastAPI
        asyncio.create_task(monitor_celery_status())
    
    @app.websocket("/ws/dashboard")
    async def websocket_dashboard(websocket: WebSocket):
        """Mở kết nối WebSocket để Dashboard kéo thông tin thời gian thực"""
        await websocket.accept()
        print("Dashboard đã kết nối WebSocket!")
        try:
            while True:
                # Phân loại danh sách link để đẩy lên Dashboard giao diện công khai
                dashboard_snapshot = {
                    "pending": [v for k, v in MONITORED_TASKS.items() if v['status'] == 'pending'],
                    "scraping": [v for k, v in MONITORED_TASKS.items() if v['status'] == 'scraping'],
                    "completed": [v for k, v in MONITORED_TASKS.items() if v['status'] == 'completed'],
                    "failed": [v for k, v in MONITORED_TASKS.items() if v['status'] == 'failed']
                }
                
                # Gửi toàn bộ trạng thái hiện tại về Front-end Dashboard
                await websocket.send_json(dashboard_snapshot)
                await asyncio.sleep(1) # Gửi cập nhật sau mỗi 1 giây
        except WebSocketDisconnect:
            print("Dashboard đã ngắt kết nối WebSocket")
    

Hãy thận trọng khi sử dụng mã.

* * *

📊 Bước 3: Giao diện Front-end Dashboard (`dashboard.html`)

Tạo một file HTML đơn giản để hiển thị số lượng và danh sách các link theo từng trạng thái: _Chờ cào, Đang cào, Đã xong, Bị lỗi_. Bạn cũng có thể bấm "Cào lại" đối với các link lỗi.

html
    
    
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>Scraper Monitor Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f4f6f9; }
            .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-top: 20px; }
            .column { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); min-height: 400px; }
            h3 { border-bottom: 2px solid #eee; padding-bottom: 10px; margin-top: 0; }
            .pending h3 { color: #f39c12; } .scraping h3 { color: #3498db; }
            .completed h3 { color: #2ecc71; } .failed h3 { color: #e74c3c; }
            .link-item { background: #f8f9fa; padding: 8px; margin-bottom: 8px; border-radius: 4px; font-size: 13px; word-break: break-all; border-left: 4px solid #ccc; }
            .failed .link-item { border-left-color: #e74c3c; }
            .scraping .link-item { border-left-color: #3498db; animation: pulse 1.5s infinite; }
            .btn-retry { background: #e74c3c; color: white; border: none; padding: 3px 8px; border-radius: 3px; cursor: pointer; margin-top: 5px; font-size: 11px; }
            @keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }
        </style>
    </head>
    <body>
    
        <h2>🕷️ Hệ Thống Giám Sát Cào Truyện Thời Gian Thực</h2>
        
        <div>
            <input type="text" id="urlInput" placeholder="Nhập link truyện mới cần cào..." style="width: 400px; padding: 8px;">
            <button onclick="submitLink()" style="padding: 8px 15px; background: #2ecc71; color:white; border:none; cursor:pointer;">Phân phối Link</button>
        </div>
    
        <div class="grid">
            <div class="column pending">
                <h3>Chờ xử lý (<span id="count-pending">0</span>)</h3>
                <div id="list-pending"></div>
            </div>
            <div class="column scraping">
                <h3>Đang cào (<span id="count-scraping">0</span>)</h3>
                <div id="list-scraping"></div>
            </div>
            <div class="column completed">
                <h3>Đã hoàn thành (<span id="count-completed">0</span>)</h3>
                <div id="list-completed"></div>
            </div>
            <div class="column failed">
                <h3>Cào bị lỗi (<span id="count-failed">0</span>)</h3>
                <div id="list-failed"></div>
            </div>
        </div>
    
        <script>
            // Connect WebSocket to FastAPI
            const ws = new WebSocket("ws://localhost:8000/ws/dashboard");
    
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                
                // Cập nhật số lượng đếm trên các cột
                document.getElementById("count-pending").innerText = data.pending.length;
                document.getElementById("count-scraping").innerText = data.scraping.length;
                document.getElementById("count-completed").innerText = data.completed.length;
                document.getElementById("count-failed").innerText = data.failed.length;
    
                // Render danh sách link chi tiết vào từng cột
                renderList("list-pending", data.pending);
                renderList("list-scraping", data.scraping);
                renderList("list-completed", data.completed);
                renderList("list-failed", data.failed, true);
            };
    
            function renderList(elementId, items, isFailedColumn = false) {
                const container = document.getElementById(elementId);
                container.innerHTML = "";
                items.forEach(item => {
                    let html = `<div class="link-item"><b>URL:</b> ${item.url}`;
                    if (isFailedColumn) {
                        html += `<br><span style="color:red;">⚠️ ${item.error || 'Lỗi không xác định'}</span>`;
                        html += `<br><button class="btn-retry" onclick="retryLink('${item.url}')">Cào lại ↻</button>`;
                    }
                    html += `</div>`;
                    container.innerHTML += html;
                });
            }
    
            // Gửi link mới qua API của FastAPI
            function submitLink() {
                const urlInput = document.getElementById("urlInput");
                if (!urlInput.value) return;
                
                fetch("http://localhost:8000/api/v1/crawl", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ url: urlInput.value })
                });
                urlInput.value = "";
            }
    
            // Cơ chế cào lại link lỗi (thực chất là đẩy lại link đó vào hàng đợi mới)
            function retryLink(url) {
                fetch("http://localhost:8000/api/v1/crawl", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ url: url })
                });
            }
        </script>
    </body>
    </html>
    

Hãy thận trọng khi sử dụng mã.

* * *

🛠️ Hướng dẫn chạy thử nghiệm hệ thống

  1. **Khởi động Redis Server** (Bằng Docker cho nhanh):

bash
         
         docker run -d -p 6379:6379 redis
         

Hãy thận trọng khi sử dụng mã.

  2. **Khởi chạy Celery Worker** để làm nhiệm vụ cào ngầm:

bash
         
         celery -A tasks worker --loglevel=info
         

Hãy thận trọng khi sử dụng mã.

  3. **Khởi chạy FastAPI Server** :

bash
         
         uvicorn main:app --reload --port 8000
         

Hãy thận trọng khi sử dụng mã.

  4. **Mở Dashboard:** Bật file `dashboard.html` bằng trình duyệt web. Nhập thử một vài URL truyện bất kỳ rồi bấm **Phân phối Link**. Bạn sẽ thấy các hộp dịch chuyển trạng thái thời gian thực từ _Chờ_ ➔ _Đang cào_ ➔ _Xong_ hoặc _Lỗi_ một cách mượt mà.



* * *

Nếu bạn muốn mở rộng dự án này, hãy phản hồi cho tôi biết:

  * Bạn có cần cấu hình **Celery Beat** để tự động quét lại các bộ truyện cũ tìm chương mới theo chu kỳ (ví dụ: 2 tiếng một lần) không?
  * Bạn muốn sử dụng thư viện cào dữ liệu nào bên trong Celery (**BeautifulSoup** , **Playwright** để né chặn, hay chỉ cần **httpx/requests**)?

