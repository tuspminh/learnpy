Version:0.9 StartHTML:00000097 EndHTML:00212454 StartFragment:00000131 EndFragment:00212418 

Để truyền dữ liệu theo thời gian thực từ Python server lên client dashboard, cách tối ưu nhất là sử dụng thư viện **WebSockets** (hoặc **Socket.IO**) kết hợp với một framework web như **FastAPI** hoặc **Flask**.

Dưới đây là hướng dẫn tạo một hệ thống đơn giản: Server Python gửi dữ liệu giả lập (như CPU, doanh thu) sau mỗi 1 giây, và Client Dashboard nhận dữ liệu để hiển thị.

* * *

Cách 1: Sử dụng FastAPI (Khuyên dùng - Nhanh, nhẹ, hỗ trợ sẵn WebSocket)

1\. Cài đặt thư viện trên Server

Chạy lệnh sau trong terminal:

bash
    
    
    pip install fastapi uvicorn
    

Hãy thận trọng khi sử dụng mã.

2\. Viết mã nguồn phía Server Python (`server.py`)

python
    
    
    import asyncio
    import random
    from fastapi import FastAPI, WebSocket
    from fastapi.responses import HTMLResponse
    
    app = FastAPI()
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        # Chấp nhận kết nối từ Client
        await websocket.accept()
        print("Client đã kết nối!")
        
        try:
            while True:
                # Giả lập dữ liệu dashboard (ví dụ: số liệu kinh doanh hoặc hiệu năng)
                dashboard_data = {
                    "users_online": random.randint(100, 500),
                    "revenue": random.randint(1000, 5000),
                    "cpu_usage": random.randint(10, 90)
                }
                
                # Gửi dữ liệu dưới dạng JSON lên Client
                await websocket.send_json(dashboard_data)
                
                # Chờ 1 giây trước khi gửi tiếp
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"Client ngắt kết nối: {e}")
    

Hãy thận trọng khi sử dụng mã.

_Để chạy server, dùng lệnh:_ `uvicorn server:app --reload`

3\. Viết mã nguồn phía Client Dashboard (`index.html`)

Tạo một file HTML để nhận dữ liệu và cập nhật giao diện:

html
    
    
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>Dashboard Thời Gian Thực</title>
        <style>
            .card { display: inline-block; padding: 20px; margin: 10px; border: 1px solid #ccc; border-radius: 8px; text-align: center; font-family: Arial; }
            .value { font-size: 24px; font-weight: bold; color: #007BFF; }
        </style>
    </head>
    <body>
        <h1>Hệ thống Giám sát Dashboard</h1>
        
        <div class="card">
            <h3>Người dùng Online</h3>
            <div id="users" class="value">0</div>
        </div>
        <div class="card">
            <h3>Doanh thu ($)</h3>
            <div id="revenue" class="value">0</div>
        </div>
        <div class="card">
            <h3>Sử dụng CPU</h3>
            <div id="cpu" class="value">0%</div>
        </div>
    
        <script>
            // Khởi tạo kết nối WebSocket tới Python Server
            const ws = new WebSocket("ws://localhost:8000/ws");
    
            // Lắng nghe dữ liệu từ Server gửi về
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                
                // Cập nhật giao diện Dashboard công khai
                document.getElementById("users").innerText = data.users_online;
                document.getElementById("revenue").innerText = data.revenue;
                document.getElementById("cpu").innerText = data.cpu_usage + "%";
            };
    
            ws.onopen = () => console.log("Đã kết nối với Server!");
            ws.onclose = () => console.log("Mất kết nối với Server!");
        </script>
    </body>
    </html>
    

Hãy thận trọng khi sử dụng mã.

* * *

Cách 2: Sử dụng Flask-SocketIO (Nếu bạn đã quen thuộc với Flask)

Nếu dashboard của bạn phức tạp hơn và cần cơ chế tự động kết nối lại khi mất mạng, hãy dùng **Socket.IO**.

1\. Cài đặt thư viện

bash
    
    
    pip install flask-socketio eventlet
    

Hãy thận trọng khi sử dụng mã.

2\. Mã nguồn Server (`app.py`)

python
    
    
    import time
    import random
    from flask import Flask
    from flask_socketio import SocketIO
    
    app = Flask(__name__)
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    def background_thread():
        """Hàm chạy ngầm liên tục gửi dữ liệu sau mỗi 2 giây"""
        while True:
            data = {"metric": random.randint(1, 100)}
            # Phát dữ liệu tới tất cả client đang kết nối thông qua event 'update_dashboard'
            socketio.emit('update_dashboard', data)
            socketio.sleep(2)
    
    @socketio.on('connect')
    def handle_connect():
        print("Client kết nối thành công qua Socket.IO")
    
    if __name__ == '__main__':
        # Chạy hàm gửi dữ liệu ngầm
        socketio.start_background_task(target=background_thread)
        socketio.run(app, port=5000, debug=True)
    

Hãy thận trọng khi sử dụng mã.

3\. Mã nguồn Client (`index.html`)

Khi dùng Socket.IO, phía Client cần nhúng thư viện JS của Socket.IO:

html
    
    
    <script src="https://socket.io"></script>
    <script>
        // Kết nối tới Flask server
        const socket = io("http://localhost:5000");
    
        // Lắng nghe sự kiện 'update_dashboard' từ server
        socket.on('update_dashboard', function(data) {
            console.log("Dữ liệu mới:", data.metric);
            // Tiến hành cập nhật biểu đồ hoặc text tại đây...
        });
    </script>
    

Hãy thận trọng khi sử dụng mã.

* * *

Để tôi có thể hỗ trợ bạn viết mã nguồn chuẩn xác nhất cho dự án, hãy cho biết:

  * Bạn định vẽ biểu đồ bằng thư viện nào ở frontend (**Chart.js** , **ApexCharts** , hay chỉ hiển thị số dạng bảng)?
  * Dữ liệu bạn muốn truyền lên lấy từ đâu (**Database** , **API bên thứ ba** , hay **cảm biến/hệ thống**)?

