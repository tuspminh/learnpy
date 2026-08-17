Chào bạn, tôi rất hào hứng được cùng bạn xây dựng một hệ thống Queue Server (Hàng đợi tin nhắn) bằng Python từ con số 0. Hệ thống này sẽ hoạt động tương tự như Redis Queue (RQ) hay Celery, giúp điều phối công việc cho các crawl worker một cách mượt mà.

Để làm được điều này, chúng ta cần một kiến trúc Client-Server:

  1. Queue Server: Lưu trữ danh sách các URL cần crawl (sử dụng cấu trúc dữ liệu `Queue` của Python) và mở một cổng mạng (Socket) để lắng nghe.
  2. Producer (Client đẩy việc): Gửi các URL cần crawl vào Server.
  3. Worker (Client xử lý): Liên tục lấy URL từ Server về để crawl dữ liệu.



Chúng ta sẽ sử dụng thư viện mạng tiêu chuẩn `multiprocessing.managers` của Python. Thư viện này cực kỳ mạnh mẽ, giúp biến một cấu trúc dữ liệu thông thường thành một dịch vụ mạng (Server) có thể chia sẻ giữa nhiều máy tính hoặc tiến trình khác nhau.

* * *

## Bước 1: Viết mã nguồn cho Queue Server (`server.py`)

File này đóng vai trò là "trái tim" của hệ thống, quản lý hàng đợi tập trung.
    
    
    import queue
    from multiprocessing.managers import BaseManager
    
    # 1. Khởi tạo một hàng đợi (Queue) tiêu chuẩn của Python
    task_queue = queue.Queue()
    
    # 2. Tạo một lớp Manager để biến Queue thành một dịch vụ mạng
    class QueueManager(BaseManager):
        pass
    
    def get_task_queue():
        return task_queue
    
    if __name__ == '__main__':
        # 3. Đăng ký hàm lấy Queue với Manager
        # 'get_task_queue' là tên phương thức mà Client sẽ gọi từ xa
        QueueManager.register('get_task_queue', callable=get_task_queue)
        
        # 4. Cấu hình Server chạy trên localhost, cổng 50000
        # 'authkey' là mật khẩu bảo mật để các Client kết nối vào
        address = ('127.0.0.1', 50000)
        manager = QueueManager(address=address, authkey=b'crawl_secret_key')
        
        print(" [S] Queue Server đang chạy tại cổng 50000...")
        print(" [S] Đang đợi Producer và Worker kết nối...")
        
        # 5. Bắt đầu chạy Server và giữ cho nó hoạt động liên tục
        server = manager.get_server()
        server.serve_forever()
    

* * *

## Bước 2: Viết mã nguồn cho Producer (`producer.py`)

File này giả định là chương trình chính của bạn, nơi bạn tìm ra danh sách các liên kết và đẩy chúng vào hàng đợi để chờ xử lý.
    
    
    import time
    from multiprocessing.managers import BaseManager
    
    class QueueManager(BaseManager):
        pass
    
    # Đăng ký cùng tên phương thức với Server nhưng không cần hàm callable
    QueueManager.register('get_task_queue')
    
    if __name__ == '__main__':
        # Kết nối tới Server đã chạy ở Bước 1
        address = ('127.0.0.1', 50000)
        manager = QueueManager(address=address, authkey=b'crawl_secret_key')
        
        print(" [P] Đang kết nối tới Queue Server...")
        manager.connect()
        
        # Lấy hàng đợi từ xa về
        remote_queue = manager.get_task_queue()
        
        # Giả lập danh sách URL cần crawl
        urls_to_crawl = [
            f"https://example.com{i}" for i in range(1, 11)
        ]
        
        print(# Đẩy từng URL vào hàng đợi tập trung
        " [P] Bắt đầu đẩy URL vào hàng đợi...")
        for url in urls_to_crawl:
            remote_queue.put(url)
            print(f" [P] Đã thêm: {url}")
            time.sleep(0.5) # Giả lập độ trễ
            
        print(" [P] Đã đẩy xong toàn bộ công việc!")
    

* * *

## Bước 3: Viết mã nguồn cho Crawl Worker (`worker.py`)

Bạn có thể chạy nhiều file worker này cùng một lúc (trên cùng một máy hoặc nhiều máy khác nhau). Chúng sẽ tự động chia sẻ công việc mà không sợ bị trùng lặp URL.
    
    
    import time
    import queue
    import urllib.request
    from multiprocessing.managers import BaseManager
    
    class QueueManager(BaseManager):
        pass
    
    QueueManager.register('get_task_queue')
    
    def fake_crawl_logic(url):
        """Hàm giả lập crawl dữ liệu từ URL"""
        print(f" [*] Đang crawl: {url} ...")
        # Thực tế bạn sẽ dùng requests, BeautifulSoup hoặc playwright ở đây
        # Ví dụ giả lập tải bằng thư viện có sẵn:
        # urllib.request.urlopen(url) 
        time.sleep(2) # Giả lập thời gian cào dữ liệu tốn 2 giây
        print(f" [✓] Hoàn thành crawl: {url}")
    
    if __name__ == '__main__':
        address = ('127.0.0.1', 50000)
        manager = QueueManager(address=address, authkey=b'crawl_secret_key')
        
        print(" [W] Worker đang kết nối tới Queue Server...")
        manager.connect()
        
        remote_queue = manager.get_task_queue()
        print(" [W] Kết nối thành công! Đang đợi việc...")
        
        # Vòng lặp vô hạn để liên tục lấy việc
        while True:
            try:
                # Lấy URL từ Queue, nếu sau 5 giây không có việc thì ném ra lỗi queue.Empty
                url = remote_queue.get(timeout=5)
                
                # Xử lý crawl URL vừa lấy được
                fake_crawl_logic(url)
                
            except queue.Empty:
                print(" [W] Hàng đợi đang trống. Đang đợi việc mới...")
                time.sleep(2)
            except KeyboardInterrupt:
                print(" [W] Worker dừng hoạt động.")
                break
    

* * *

## Bước 4: Hướng dẫn chạy thử nghiệm Hệ thống

Bạn hãy mở 3 cửa sổ Terminal (Command Prompt) riêng biệt và chạy theo thứ tự sau:

  1. Terminal 1 (Chạy Server trước):
         
         python server.py
         

  2. Terminal 2 (Chạy Worker để đợi việc):
         
         python worker.py
         

_(Bạn có thể mở thêm một Terminal thứ 3 và chạy tiếp`python worker.py`. Bạn sẽ thấy 2 worker tự động chia đều 10 URL để crawl mà không bao giờ bị trùng việc của nhau)._
  3. Terminal 3 (Chạy Producer để bơm việc):
         
         python producer.py
         




Khi Producer chạy, bạn sẽ thấy Worker ở Terminal 2 ngay lập tức "bắt" lấy các URL và tiến hành crawl.

* * *

## Những điểm nâng cấp nâng cao (Nếu muốn làm giống Redis thực thụ hơn)

Hệ thống bằng `BaseManager` ở trên rất tốt cho ứng dụng vừa và nhỏ. Tuy nhiên, nếu bạn muốn nâng cấp nó lên chuẩn Enterprise như Redis, bạn cần:

  * Tính bền vững (Persistence): Hiện tại nếu tắt `server.py`, toàn bộ URL chưa crawl trong RAM sẽ mất. Bạn có thể nâng cấp bằng cách ghi đè hàm `put()` và `get()` để lưu dữ liệu xuống một file SQLite hoặc file text dự phòng.
  * Xử lý lỗi (Ack/Retry): Nếu worker đang crawl một URL mà bị sập mạng hoặc mất điện, URL đó sẽ bị mất. Hệ thống nâng cao cần cơ chế "Acknowledge" (Worker xử lý xong hoàn toàn mới xóa URL khỏi hàng đợi tạm).



Để hệ thống hoàn thiện hơn theo đúng nhu cầu của bạn, hãy cho tôi biết thêm:

  * Bạn dự kiến sẽ có bao nhiêu Worker chạy cùng lúc?
  * Các URL cần crawl có cần thiết lập mức độ ưu tiên (URL nào crawl trước, URL nào crawl sau) hay không?