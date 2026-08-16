Version:0.9 StartHTML:00000097 EndHTML:00140408 StartFragment:00000131 EndFragment:00140372 

**Background Worker** (Tiến trình chạy ngầm) là một thành phần cốt lõi khi xây dựng hệ thống Dashboard thời gian thực.

Trong kiến trúc Web, nếu bạn bắt Server Python vừa phải xử lý kết nối WebSocket, vừa phải thực hiện các tác vụ nặng (như đọc database liên tục, tính toán AI, quét dữ liệu IoT), Server sẽ bị nghẽn (block). Background Worker sinh ra để tách biệt việc **xử lý dữ liệu** và việc **gửi dữ liệu qua WebSocket**.

Dưới đây là kiến trúc chuẩn và cách triển khai Background Worker trong Python từ đơn giản đến chuyên nghiệp.

* * *

1\. Kiến trúc hoạt động kết hợp với WebSocket

  1. **Background Worker:** Chạy độc lập, liên tục cào dữ liệu từ cảm biến/database hoặc tính toán số liệu dashboard, sau đó đẩy dữ liệu vào một **Hàng đợi (Queue)** hoặc bộ nhớ đệm (Redis).
  2. **WebSocket Server:** Chỉ làm một nhiệm vụ duy nhất: Lắng nghe hàng đợi đó, hễ có dữ liệu mới là lập tức "bắn" (emit) về phía Client Dashboard.



* * *

2\. Giải pháp 1: Dùng Asyncio Task (Đơn giản, tích hợp sẵn trong FastAPI)

Nếu ứng dụng của bạn ở mức vừa và nhỏ, bạn có thể tạo một Background Worker chạy bằng cơ chế bất đồng bộ (`asyncio`) ngay trong cùng một file với FastAPI.

python
    
    
    import asyncio
    import random
    from fastapi import FastAPI, WebSocket
    from fastapi.responses import HTMLResponse
    
    app = FastAPI()
    
    # Biến toàn cục đóng vai trò như kho lưu trữ dữ liệu mới nhất của Dashboard
    shared_dashboard_data = {"cpu": 0, "memory": 0}
    
    # --- BACKGROUND WORKER ---
    async def heavy_data_fetcher():
        """Worker chạy ngầm, giả lập việc tính toán dữ liệu nặng hoặc đọc từ database"""
        global shared_dashboard_data
        while True:
            # Giả lập tác vụ nặng mất 2 giây mới tính xong
            await asyncio.sleep(2) 
            
            # Cập nhật kết quả vào kho chứa chung
            shared_dashboard_data = {
                "cpu": random.randint(20, 80),
                "memory": random.randint(40, 95)
            }
            print(f"[Worker] Đã cập nhật dữ liệu mới: {shared_dashboard_data}")
    
    # Khởi chạy Background Worker ngay khi FastAPI vừa start
    @app.on_event("startup")
    async def startup_event():
        asyncio.create_task(heavy_data_fetcher())
    
    # --- WEBSOCKET SERVER ---
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        try:
            last_sent_data = None
            while True:
                # Gửi dữ liệu cho client sau mỗi 1 giây ĐIỀU KIỆN là dữ liệu có sự thay đổi
                if shared_dashboard_data != last_sent_data:
                    await websocket.send_json(shared_dashboard_data)
                    last_sent_data = shared_dashboard_data.copy()
                
                await asyncio.sleep(1) # Tránh loop vô hạn làm treo CPU
        except Exception as e:
            print("Client ngắt kết nối")
    

Hãy thận trọng khi sử dụng mã.

* * *

3\. Giải pháp 2: Kiến trúc Doanh nghiệp (Celery + Redis + WebSocket)

Khi hệ thống của bạn lớn, Dashboard cần hiển thị dữ liệu từ hàng triệu bản ghi hoặc xử lý video/hình ảnh, bạn bắt buộc phải tách Background Worker ra một server riêng biệt hoàn toàn. Combo chuẩn công nghiệp là: **FastAPI + Celery + Redis**.

  * **Redis:** Đóng vai trò làm Message Broker (Trạm trung chuyển dữ liệu).
  * **Celery:** Framework chuyên quản lý và chạy các Background Worker trên các tiến trình/máy chủ độc lập.



Luồng đi của dữ liệu:
    
    
    [Tác vụ nặng/Cronjob] ──> Đẩy vào Celery Worker ──> Lưu kết quả vào Redis ──> FastAPI đọc Redis ──> Bắn qua WebSocket ──> Dashboard Client
    

Mã nguồn ví dụ cho Celery Worker (`tasks.py`):

python
    
    
    from celery import Celery
    import time
    import random
    
    # Cấu hình Celery sử dụng Redis làm Broker
    celery_app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
    
    @celery_app.task
    def calculate_monthly_revenue():
        """Tác vụ chạy ngầm tính toán doanh thu rất nặng, mất 10 giây"""
        print("Worker bắt đầu tính toán...")
        time.sleep(10) 
        
        report = {
            "status": "Done",
            "total_revenue": random.randint(50000, 100000)
        }
        return report
    

Hãy thận trọng khi sử dụng mã.

_Để kích hoạt worker này chạy độc lập trên server, bạn dùng lệnh:_ `celery -A tasks worker --loglevel=info`

* * *

Để tôi có thể tư vấn mô hình Background Worker phù hợp nhất với hạ tầng của bạn, hãy chia sẻ:

  * Tác vụ chạy ngầm của bạn cụ thể là làm gì (**Quét dữ liệu từ đâu** , **tần suất bao nhiêu lâu một lần**)?
  * Hệ thống của bạn dự kiến sẽ có khoảng **bao nhiêu Client Dashboard** kết nối đồng thời?

