Version:0.9 StartHTML:0000000105 EndHTML:0000044666 StartFragment:0000000141 EndFragment:0000044630 

### v1

Để xây dựng một hệ thống có khả năng kiểm soát toàn diện như: xem trạng thái thời gian thực, nhấn nút Dừng (Stop), Chạy tiếp (Resume), hoặc Cào lại chương lỗi (Retry), chúng ta không thể dùng kịch bản script chạy một mạch từ đầu đến cuối như trước.

Giải pháp tối ưu nhất là xây dựng một **Giao diện Web Giám sát (Dashboard)** bằng **FastAPI** (cho backend bất đồng bộ) kết hợp với giao diện HTML/JS đơn giản sử dụng **WebSocket** để cập nhật trạng thái thời gian thực mà không làm chậm tiến trình cào.

**1\. Kiến trúc lưu trữ trạng thái (State Management)**

Chương trình cần một biến toàn cục quản lý danh sách chương và trạng thái của chúng:

  * `Pending`: Đang chờ cào.
  * `Running`: Đang tải dữ liệu.
  * `Success`: Đang lưu dữ liệu thành công.
  * `Failed`: Lỗi sau 3 lần thử.



**2\. Mã nguồn toàn diện cho Ứng dụng Giám sát (app.py)**

Hãy tạo một file tên là `app.py` và dán toàn bộ đoạn mã dưới đây vào.

Trước khi chạy, hãy cài đặt các thư viện cần thiết:

bash
    
    
    pip install fastapi uvicorn aiohttp fake-useragent selectolax
    

Hãy thận trọng khi sử dụng mã.

python
    
    
    import asyncio
    import json
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse
    import aiohttp
    from selectolax.parser import HTMLParser
    from fake_useragent import UserAgent
    
    app = FastAPI()
    ua = UserAgent()
    
    # --- CẤU HÌNH & QUẢN LÝ TRẠNG THÁI ---
    BASE_URL = "https://truyenfull.today"
    SEMAPHORE_LIMIT = 3
    
    # Quản lý luồng chạy của ứng dụng
    crawl_state = {
        "status": "STOPPED",  # RUNNING, STOPPED
        "chapters": {},       # {id_chuong: "Pending" | "Running" | "Success" | "Failed"}
        "results": {}         # {id_chuong: {data}}
    }
    
    # Quản lý các kết nối Giao diện để cập nhật Realtime
    active_connections: list[WebSocket] = []
    crawl_task = None  # Biến lưu trữ Task Async đang chạy chính
    
    async def broadcast_status():
        """Gửi trạng thái mới nhất tới tất cả các màn hình giám sát"""
        if active_connections:
            data = {
                "status": crawl_state["status"],
                "chapters": crawl_state["chapters"]
            }
            # Tạo bản sao danh sách để tránh xung đột luồng khi duyệt vòng lặp
            for connection in active_connections.copy():
                try:
                    await connection.send_text(json.dumps(data))
                except Exception:
                    active_connections.remove(connection)
    
    # --- CORE SCRAPING LOGIC ---
    async def cao_mot_chuong(session, semaphore, id_chuong):
        async with semaphore:
            # Nếu người dùng bấm STOP, dừng ngay lập tức khi chuẩn bị cào chương mới
            if crawl_state["status"] == "STOPPED":
                crawl_state["chapters"][id_chuong] = "Pending"
                return
    
            crawl_state["chapters"][id_chuong] = "Running"
            await broadcast_status()
    
            url = f"{BASE_URL}{id_chuong}/"
            SO_LAN_THU_LAI = 3
    
            for lan_thu in range(1, SO_LAN_THU_LAI + 1):
                if crawl_state["status"] == "STOPPED":
                    crawl_state["chapters"][id_chuong] = "Pending"
                    await broadcast_status()
                    return
    
                try:
                    headers = {"User-Agent": ua.random, "Referer": "https://truyenfull.today"}
                    async with session.get(url, headers=headers, timeout=8) as response:
                        if response.status == 200:
                            html = await response.text()
                            tree = HTMLParser(html)
                            
                            # Giả lập parse dữ liệu (Thay class selector thực tế ở đây)
                            tieu_de = f"Chương {id_chuong}" 
                            try: tieu_de = tree.css_first(".chapter-title").text(strip=True)
                            except: pass
                            
                            crawl_state["chapters"][id_chuong] = "Success"
                            crawl_state["results"][id_chuong] = {"title": tieu_de}
                            await broadcast_status()
                            return
                        elif response.status == 404:
                            break # Đầu truyện hết, không cần thử lại
                except Exception:
                    pass
                
                if lan_thu < SO_LAN_THU_LAI:
                    await asyncio.sleep(1)
    
            # Nếu chạy hết 3 lần vẫn lỗi
            crawl_state["chapters"][id_chuong] = "Failed"
            await broadcast_status()
    
    async def tiến_trình_cào_chính():
        """Vòng lặp chính quét các chương cần cào"""
        semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)
        async with aiohttp.ClientSession() as session:
            while crawl_state["status"] == "RUNNING":
                # Lấy danh sách các chương đang cần cào (Pending hoặc Failed muốn cào lại)
                cac_chuong_can_cao = [
                    id_ch for id_ch, trang_thai in crawl_state["chapters"].items()
                    if trang_thai in ["Pending", "Failed"]
                ]
    
                if not cac_chuong_can_cao:
                    crawl_state["status"] = "STOPPED"
                    await broadcast_status()
                    break
    
                # Chạy đồng thời các chương đang đợi
                tasks = [cao_mot_chuong(session, semaphore, id_ch) for id_ch in cac_chuong_can_cao]
                await asyncio.gather(*tasks)
                
                # Nghỉ ngắn giữa các đợt quét
                await asyncio.sleep(0.5)
    
    # --- CÁC ĐIỀU HƯỚNG ĐIỀU KHIỂN (API CONTROLS) ---
    @app.get("/start")
    async def start_crawl():
        global crawl_task
        # Khởi tạo dữ liệu mẫu nếu chưa có chương nào (Ví dụ cào từ chương 1 đến 30)
        if not crawl_state["chapters"]:
            crawl_state["chapters"] = {str(i): "Pending" for i in range(1, 31)}
    
        if crawl_state["status"] == "STOPPED":
            crawl_state["status"] = "RUNNING"
            await broadcast_status()
            # Chạy tác vụ cào dưới nền không gây nghẽn API
            crawl_task = asyncio.create_task(tiến_trình_cào_chính())
        return {"message": "Đã ra lệnh CÀO TRUYỆN"}
    
    @app.get("/stop")
    async def stop_crawl():
        crawl_state["status"] = "STOPPED"
        await broadcast_status()
        return {"message": "Đã dừng tiến trình cào thành công"}
    
    @app.get("/retry-failed")
    async def retry_failed():
        # Chuyển toàn bộ trạng thái lỗi về Pending để cào lại
        for id_ch, trang_thai in crawl_state["chapters"].items():
            if trang_thai == "Failed":
                crawl_state["chapters"][id_ch] = "Pending"
        await broadcast_status()
        return {"message": "Đã đặt lại các chương lỗi về trạng thái chờ"}
    
    # --- ĐƯỜNG DẪN GIAO DIỆN VÀ WEBSOCKET ---
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        active_connections.append(websocket)
        # Gửi dữ liệu ngay khi vừa kết nối màn hình
        await websocket.send_text(json.dumps({
            "status": crawl_state["status"],
            "chapters": crawl_state["chapters"]
        }))
        try:
            while True:
                await websocket.receive_text()  # Giữ kết nối mở
        except WebSocketDisconnect:
            active_connections.remove(websocket)
    
    @app.get("/", response_class=HTMLResponse)
    async def get_dashboard():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard Giám Sát Cào Truyện</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 30px; background: #f4f6f9; }
                .controls { margin-bottom: 20px; padding: 15px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                button { padding: 10px 20px; font-size: 15px; margin-right: 10px; cursor: pointer; border: none; border-radius: 4px; color: white;}
                .btn-start { background: #28a745; } .btn-stop { background: #dc3545; } .btn-retry { background: #ffc107; color: black; }
                .status-banner { font-size: 18px; font-weight: bold; margin-bottom: 10px; }
                .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 110px)); gap: 10px; }
                .chapter-card { padding: 12px; text-align: center; border-radius: 6px; font-weight: bold; color: white; transition: all 0.3s; }
                .Pending { background: #6c757d; }
                .Running { background: #007bff; animation: blink 1s infinite; }
                .Success { background: #28a745; }
                .Failed { background: #dc3545; }
                @keyframes blink { 0% {opacity: 1;} 50% {opacity: 0.5;} 100% {opacity: 1;} }
            </style>
        </head>
        <body>
            <h2> Hệ Thống Giám Sát Cào Truyện Tốc Độ Cao</h2>
            <div class="controls">
                <div class="status-banner">Trạng thái hệ thống: <span id="sys-status" style="color:#007bff">ĐANG TẢI...</span></div>
                <button class="btn-start" onclick="fetch('/start')">▶ CÀO / TIẾP TỤC</button>
                <button class="btn-stop" onclick="fetch('/stop')"> STOP DỪNG</button>
                <button class="btn-retry" onclick="fetch('/retry-failed')">🔄 ĐẶT LẠI CHƯƠNG LỖI</button>
            </div>
            <h3>Danh sách chương</h3>
            <div class="grid" id="chapters-grid"></div>
    
            <script>
                // Kết nối tới WebSocket để nhận cập nhật Realtime tự động
                const ws = new WebSocket(`ws://${window.location.host}/ws`);
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    
                    // Cập nhật trạng thái chữ hệ thống
                    document.getElementById("sys-status").innerText = data.status;
                    document.getElementById("sys-status").style.color = data.status === "RUNNING" ? "#28a745" : "#dc3545";
                    
                    // Vẽ lưới danh sách chương
                    const grid = document.getElementById("chapters-grid");
                    grid.innerHTML = "";
                    
                    // Sắp xếp ID theo thứ tự số tăng dần
                    const sortedKeys = Object.keys(data.chapters).sort((a,b) => Number(a) - Number(b));
                    
                    sortedKeys.forEach(id => {
                        const status = data.chapters[id];
                        const card = document.createElement("div");
                        card.className = `chapter-card ${status}`;
                        card.innerText = `Chương ${id}\\n(${status})`;
                        grid.appendChild(card);
                    });
                };
            </script>
        </body>
        </html>
        """
    

Hãy thận trọng khi sử dụng mã.

**3\. Cách vận hành ứng dụng**

  1. Khởi chạy ứng dụng bằng lệnh Terminal:

bash
         
         uvicorn app:app --reload
         

Hãy thận trọng khi sử dụng mã.

  2. Mở trình duyệt và truy cập: `http://127.0.0.1:8000`
  3. **Các tính năng đã được kích hoạt trên giao diện** :
     * Nhấn **CÀO / TIẾP TỤC** : Kích hoạt hệ thống gửi request cào đồng thời, các ô vuông chương chuyển sang màu xanh dương (Running) nhấp nháy, nếu xong sẽ hóa xanh lá (Success).
     * Nhấn **STOP DỪNG** : Tiến trình dừng an toàn ngay lập tức. Những chương đang cào dở hoặc chưa cào sẽ giữ nguyên trạng thái chờ (`Pending`). Nhấn lại nút Start hệ thống sẽ tự động **cào tiếp các chương còn lại**.
     * Nhấn **ĐẶT LẠI CHƯƠNG LỖI** : Tìm các ô màu đỏ (`Failed`), chuyển chúng về xám (`Pending`). Khi bạn bấm tiếp Start, hệ thống sẽ chỉ nhắm vào các chương lỗi này để **cào lại**.



Để hoàn thiện ứng dụng này phục vụ nhu cầu thực tế của bạn, hãy cho tôi biết:

  * Bạn có muốn thêm một ô **nhập số lượng chương tùy ý** (Ví dụ: Nhập cào từ chương X đến chương Y) ngay trên giao diện Web không?
  * Bạn muốn sau khi nhấn nút hoàn thành, ứng dụng sẽ **tự động đóng gói tất cả thành 1 file EPUB/MOBI** để đọc trên điện thoại không?



### v2

Để thêm tính năng nhập dải chương tùy ý (Ví dụ: Từ chương 1 đến chương 100), chúng ta sẽ thực hiện 2 thay đổi nhỏ:

  1. **Tại Frontend (HTML)** : Thêm 2 ô nhập liệu (`Từ chương` và `Đến chương`) và gửi giá trị này lên API khi bấm nút chạy.
  2. **Tại Backend (FastAPI)** : Thay đổi API `/start`

để tiếp nhận tham số này, sau đó khởi tạo danh sách chương tương ứng vào hệ thống.




Dưới đây là mã nguồn toàn diện đã được nâng cấp. Bạn chỉ cần thay thế toàn bộ file `app.py` cũ bằng đoạn mã mới này:

python
    
    
    import asyncio
    import json
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
    from fastapi.responses import HTMLResponse
    import aiohttp
    from selectolax.parser import HTMLParser
    from fake_useragent import UserAgent
    
    app = FastAPI()
    ua = UserAgent()
    
    # --- CẤU HÌNH & QUẢN LÝ TRẠNG THÁI ---
    BASE_URL = "https://truyenfull.today"
    SEMAPHORE_LIMIT = 3
    
    crawl_state = {
        "status": "STOPPED",  
        "chapters": {},       # {id_chuong: "Pending" | "Running" | "Success" | "Failed"}
        "results": {}         
    }
    
    active_connections: list[WebSocket] = []
    crawl_task = None  
    
    async def broadcast_status():
        """Gửi trạng thái mới nhất tới tất cả các màn hình giám sát"""
        if active_connections:
            data = {
                "status": crawl_state["status"],
                "chapters": crawl_state["chapters"]
            }
            for connection in active_connections.copy():
                try:
                    await connection.send_text(json.dumps(data))
                except Exception:
                    active_connections.remove(connection)
    
    # --- CORE SCRAPING LOGIC ---
    async def cao_mot_chuong(session, semaphore, id_chuong):
        async with semaphore:
            if crawl_state["status"] == "STOPPED":
                crawl_state["chapters"][id_chuong] = "Pending"
                return
    
            crawl_state["chapters"][id_chuong] = "Running"
            await broadcast_status()
    
            url = f"{BASE_URL}{id_chuong}/"
            SO_LAN_THU_LAI = 3
    
            for lan_thu in range(1, SO_LAN_THU_LAI + 1):
                if crawl_state["status"] == "STOPPED":
                    crawl_state["chapters"][id_chuong] = "Pending"
                    await broadcast_status()
                    return
    
                try:
                    headers = {"User-Agent": ua.random, "Referer": "https://truyenfull.today"}
                    async with session.get(url, headers=headers, timeout=8) as response:
                        if response.status == 200:
                            html = await response.text()
                            tree = HTMLParser(html)
                            
                            tieu_de = f"Chương {id_chuong}" 
                            try: tieu_de = tree.css_first(".chapter-title").text(strip=True)
                            except: pass
                            
                            crawl_state["chapters"][id_chuong] = "Success"
                            crawl_state["results"][id_chuong] = {"title": tieu_de}
                            await broadcast_status()
                            return
                        elif response.status == 404:
                            break 
                except Exception:
                    pass
                
                if lan_thu < SO_LAN_THU_LAI:
                    await asyncio.sleep(1)
    
            crawl_state["chapters"][id_chuong] = "Failed"
            await broadcast_status()
    
    async def tiến_trình_cào_chính():
        semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)
        async with aiohttp.ClientSession() as session:
            while crawl_state["status"] == "RUNNING":
                cac_chuong_can_cao = [
                    id_ch for id_ch, trang_thai in crawl_state["chapters"].items()
                    if trang_thai in ["Pending", "Failed"]
                ]
    
                if not cac_chuong_can_cao:
                    crawl_state["status"] = "STOPPED"
                    await broadcast_status()
                    break
    
                tasks = [cao_mot_chuong(session, semaphore, id_ch) for id_ch in cac_chuong_can_cao]
                await asyncio.gather(*tasks)
                await asyncio.sleep(0.5)
    
    # --- CÁC ĐIỀU HƯỚNG ĐIỀU KHIỂN (API CONTROLS) ---
    @app.get("/start")
    async def start_crawl(from_ch: int = Query(default=None), to_ch: int = Query(default=None)):
        global crawl_task
        
        # Nếu người dùng nhập khoảng chương mới, khởi tạo lại danh sách chương
        if from_ch is not None and to_ch is not None and from_ch <= to_ch:
            # Giữ lại kết quả cũ nếu trùng, hoặc ghi đè/tạo mới nếu chưa có
            for i in range(from_ch, to_ch + 1):
                ch_str = str(i)
                if ch_str not in crawl_state["chapters"] or crawl_state["chapters"][ch_str] == "Failed":
                    crawl_state["chapters"][ch_str] = "Pending"
    
        if crawl_state["status"] == "STOPPED":
            crawl_state["status"] = "RUNNING"
            await broadcast_status()
            crawl_task = asyncio.create_task(tiến_trình_cào_chính())
        return {"message": "Đã tiếp nhận cấu hình chương và kích hoạt cào"}
    
    @app.get("/stop")
    async def stop_crawl():
        crawl_state["status"] = "STOPPED"
        await broadcast_status()
        return {"message": "Đã dừng tiến trình cào thành công"}
    
    @app.get("/retry-failed")
    async def retry_failed():
        for id_ch, trang_thai in crawl_state["chapters"].items():
            if trang_thai == "Failed":
                crawl_state["chapters"][id_ch] = "Pending"
        await broadcast_status()
        return {"message": "Đã đặt lại các chương lỗi về trạng thái chờ"}
    
    # --- ĐƯỜNG DẪN GIAO DIỆN VÀ WEBSOCKET ---
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        active_connections.append(websocket)
        await websocket.send_text(json.dumps({
            "status": crawl_state["status"],
            "chapters": crawl_state["chapters"]
        }))
        try:
            while True:
                await websocket.receive_text()  
        except WebSocketDisconnect:
            active_connections.remove(websocket)
    
    @app.get("/", response_class=HTMLResponse)
    async def get_dashboard():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard Giám Sát Cào Truyện</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 30px; background: #f4f6f9; }
                .controls { margin-bottom: 20px; padding: 15px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .input-group { margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }
                .input-group input { padding: 8px; width: 80px; font-size: 14px; border: 1px solid #ccc; border-radius: 4px; }
                button { padding: 10px 20px; font-size: 15px; margin-right: 10px; cursor: pointer; border: none; border-radius: 4px; color: white; font-weight: bold;}
                .btn-start { background: #28a745; } .btn-stop { background: #dc3545; } .btn-retry { background: #ffc107; color: black; }
                .status-banner { font-size: 18px; font-weight: bold; margin-bottom: 15px; }
                .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 110px)); gap: 10px; }
                .chapter-card { padding: 12px; text-align: center; border-radius: 6px; font-weight: bold; color: white; transition: all 0.3s; font-size: 13px; }
                .Pending { background: #6c757d; }
                .Running { background: #007bff; animation: blink 1s infinite; }
                .Success { background: #28a745; }
                .Failed { background: #dc3545; }
                @keyframes blink { 0% {opacity: 1;} 50% {opacity: 0.5;} 100% {opacity: 1;} }
            </style>
        </head>
        <body>
            <h2> Hệ Thống Giám Sát Cào Truyện Tốc Độ Cao</h2>
            <div class="controls">
                <div class="status-banner">Trạng thái hệ thống: <span id="sys-status" style="color:#007bff font-weight: bold;">ĐANG TẢI...</span></div>
                
                <!-- Ô nhập dải chương tùy ý -->
                <div class="input-group">
                    <label><b>Cấu hình dải chương mới:</b></label>
                    <input type="number" id="from-ch" placeholder="Từ số" min="1">
                    <span>đến</span>
                    <input type="number" id="to-ch" placeholder="Đến số" min="1">
                </div>
    
                <button class="btn-start" onclick="startCrawling()">▶ CÀO / TIẾP TỤC</button>
                <button class="btn-stop" onclick="fetch('/stop')"> STOP DỪNG</button>
                <button class="btn-retry" onclick="fetch('/retry-failed')">🔄 ĐẶT LẠI CHƯƠNG LỖI</button>
            </div>
            <h3>Danh sách chương</h3>
            <div class="grid" id="chapters-grid"></div>
    
            <script>
                // Hàm xử lý nút Start kèm tham số dải chương
                function startCrawling() {
                    const fromCh = document.getElementById("from-ch").value;
                    const toCh = document.getElementById("to-ch").value;
                    
                    let url = "/start";
                    if(fromCh && toCh) {
                        url += `?from_ch=${fromCh}&to_ch=${toCh}`;
                    }
                    fetch(url);
                }
    
                const ws = new WebSocket(`ws://${window.location.host}/ws`);
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    
                    document.getElementById("sys-status").innerText = data.status;
                    document.getElementById("sys-status").style.color = data.status === "RUNNING" ? "#28a745" : "#dc3545";
                    
                    const grid = document.getElementById("chapters-grid");
                    grid.innerHTML = "";
                    
                    const sortedKeys = Object.keys(data.chapters).sort((a,b) => Number(a) - Number(b));
                    
                    sortedKeys.forEach(id => {
                        const status = data.chapters[id];
                        const card = document.createElement("div");
                        card.className = `chapter-card ${status}`;
                        card.innerText = `Chương ${id}\\n(${status})`;
                        grid.appendChild(card);
                    });
                };
            </script>
        </body>
        </html>
        """
    

Hãy thận trọng khi sử dụng mã.

**Cách hoạt động mới:**

  1. **Cào nối tiếp** : Nếu bạn bỏ trống 2 ô nhập liệu và bấm **▶ CÀO / TIẾP TỤC** , chương trình sẽ tiếp tục chạy các chương còn dang dở trước đó (`Pending`/`Failed`).
  2. **Thêm chương mới** : Nếu bạn nhập `Từ: 50` `Đến: 100` rồi bấm **▶ CÀO / TIẾP TỤC** , hệ thống sẽ tự động thêm các chương từ 50 đến 100 vào lưới hiển thị giám sát dưới trạng thái Chờ (`Pending`) và bắt đầu cào ngay lập tức.



Để hoàn thành bước cuối cùng, bạn có muốn:

  * Tích hợp tính năng tự động nhập **Tên truyện (Slug URL)** ngay trên giao diện để không phải sửa cứng link truyện trong mã nguồn `BASE_URL` không?
  * Thêm một nút bấm để **Xuất toàn bộ chương đã cào thành công ra file** văn bản lớn không?



