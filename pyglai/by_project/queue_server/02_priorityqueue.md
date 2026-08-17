Để đáp ứng bài toán phân chia công việc theo độ ưu tiên (1 cho crawl truyện mới, 2 cho cập nhật danh sách cũ), chúng ta cần thay đổi cấu trúc dữ liệu từ hàng đợi thông thường (`queue.Queue`) sang Hàng đợi ưu tiên (`queue.PriorityQueue`).

Trong `PriorityQueue` của Python, các phần tử có số ưu tiên nhỏ hơn sẽ được lấy ra trước. Do đó, chúng ta sẽ quy ước:

  * Độ ưu tiên `1` (Crawl truyện mới): Cần ưu tiên xử lý ngay lập tức.
  * Độ ưu tiên `2` (Cập nhật danh sách cũ): Xử lý sau khi hàng đợi đã hết truyện mới.



Dưới đây là mã nguồn đã được nâng cấp toàn diện, sẵn sàng cho 3 Worker chạy song song.

* * *

## Bước 1: Nâng cấp Queue Server (`server.py`)

Chúng ta chuyển sang dùng `queue.PriorityQueue`. Định dạng dữ liệu đẩy vào hàng đợi từ nay sẽ là một Tuple: `(độ_ưu_tiên, url)`.
    
    
    import queue
    from multiprocessing.managers import BaseManager
    
    # 1. Sử dụng PriorityQueue để tự động sắp xếp theo độ ưu tiên (Số nhỏ ra trước)
    task_queue = queue.PriorityQueue()
    
    class QueueManager(BaseManager):
        pass
    
    def get_priority_queue():
        return task_queue
    
    if __name__ == '__main__':
        # Đăng ký hàng đợi ưu tiên với tên 'get_priority_queue'
        QueueManager.register('get_priority_queue', callable=get_priority_queue)
        
        address = ('127.0.0.1', 50000)
        manager = QueueManager(address=address, authkey=b'novel_crawl_secret')
        
        print(" [S] Priority Queue Server đang chạy tại cổng 50000...")
        
        server = manager.get_server()
        server.serve_forever()
    

* * *

## Bước 2: Nâng cấp Producer (`producer.py`)

Producer này sẽ giả lập việc đẩy xen kẽ cả URL crawl mới (Ưu tiên 1) và URL cập nhật chương mới (Ưu tiên 2).
    
    
    import time
    from multiprocessing.managers import BaseManager
    
    class QueueManager(BaseManager):
        pass
    
    QueueManager.register('get_priority_queue')
    
    if __name__ == '__main__':
        address = ('127.0.0.1', 50000)
        manager = QueueManager(address=address, authkey=b'novel_crawl_secret')
        
        print(" [P] Đang kết nối tới Queue Server...")
        manager.connect()
        remote_queue = manager.get_priority_queue()
        
        # 1. Đẩy 5 URL cập nhật truyện cũ (Độ ưu tiên = 2) vào trước
        print("\n [P] Đẩy danh sách cập nhật (Ưu tiên 2) vào trước...")
        for i in range(1, 6):
            url = f"https://truyen.com{i}"
            remote_queue.put((2, url)) # Đẩy một tuple (độ_ưu_tiên, dữ_liệu)
            print(f"  -> Đã xếp hàng [Ưu tiên 2]: {url}")
            time.sleep(0.1)
            
        # 2. Đẩy 3 URL crawl truyện mới (Độ ưu tiên = 1) vào sau
        print("\n [P] Đẩy danh sách crawl mới (Ưu tiên 1) vào sau...")
        for i in range(1, 4):
            url = f"https://truyen.com{i}"
            remote_queue.put((1, url))
            print(f"  -> Đã xếp hàng [Ưu tiên 1]: {url}")
            time.sleep(0.1)
    
        print("\n [P] Đã bơm xong việc vào hệ thống!")
    

* * *

## Bước 3: Mã nguồn cho Crawl Worker (`worker.py`)

Mã nguồn worker nhận diện độ ưu tiên và hiển thị log chi tiết để bạn dễ theo dõi hành vi phân phối việc.
    
    
    import time
    import queue
    import sys
    from multiprocessing.managers import BaseManager
    
    class QueueManager(BaseManager):
        pass
    
    QueueManager.register('get_priority_queue')
    
    def process_crawl(priority, url, worker_name):
        """Hàm xử lý logic crawl tùy thuộc vào độ ưu tiên"""
        type_str = "CRAWL TRUYỆN MỚI" if priority == 1 else "CHECK CHƯƠNG MỚI"
        print(f" [{worker_name}] Đang xử lý [{type_str}] -> {url}")
        
        # Giả lập thời gian cào dữ liệu (ví dụ: check chương cũ nhanh hơn crawl truyện mới)
        duration = 3 if priority == 1 else 1.5
        time.sleep(duration)
        
        print(f" [{worker_name}] Hoàn thành -> {url}")
    
    if __name__ == '__main__':
        # Lấy tên Worker từ tham số dòng lệnh (để phân biệt giữa 3 worker)
        worker_name = sys.argv[1] if len(sys.argv) > 1 else "Worker-X"
        
        address = ('127.0.0.1', 50000)
        manager = QueueManager(address=address, authkey=b'novel_crawl_secret')
        
        print(f" [{worker_name}] Đang kết nối tới Queue Server...")
        try:
            manager.connect()
            remote_queue = manager.get_priority_queue()
            print(f" [{worker_name}] Sẵn sàng nhận việc!")
        except Exception as e:
            print(f" Lỗi kết nối: {e}")
            sys.exit(1)
            
        while True:
            try:
                # Lấy tác vụ từ hàng đợi ưu tiên
                priority, url = remote_queue.get(timeout=5)
                
                # Tiến hành crawl
                process_crawl(priority, url, worker_name)
                
            except queue.Empty:
                print(f" [{worker_name}] Hàng đợi trống. Đang đợi task mới...")
                time.sleep(3)
            except KeyboardInterrupt:
                print(f" [{worker_name}] Đã dừng.")
                break
    

* * *

## Bước 4: Cách chạy thử nghiệm 3 Worker để thấy rõ "Độ ưu tiên"

Để thấy được sức mạnh của `PriorityQueue`, bạn hãy làm chính xác theo các bước sau để tích lũy việc trong hàng đợi trước khi cho worker chạy:

  1. Terminal 1: Khởi chạy Server.
         
         python server.py
         

  2. Terminal 2: Chạy Producer để bơm toàn bộ việc vào (Lúc này danh sách Ưu tiên 2 được đẩy vào trước, Ưu tiên 1 đẩy vào sau).
         
         python producer.py
         

  3. Mở đồng thời Terminal 3, 4, 5: Khởi chạy 3 Worker cùng lúc bằng cách truyền tên worker làm tham số:
         
         # Terminal 3
         python worker.py Worker-1
         
         # Terminal 4
         python worker.py Worker-2
         
         # Terminal 5
         python worker.py Worker-3
         




Kết quả bạn sẽ quan sát thấy: mặc dù các URL `Ưu tiên 2` (Cập nhật list cũ) được đẩy vào hàng đợi trước, nhưng ngay khi 3 Worker bật lên, chúng sẽ bốc toàn bộ các URL `Ưu tiên 1` (Crawl truyện mới) để xử lý trước sạch sẽ, sau đó mới quay sang xử lý các URL `Ưu tiên 2`. Các worker tự động chia việc mà không hề bị trùng lặp.

Để tối ưu hơn nữa cho ứng dụng crawl novel thực tế, bạn có muốn tích hợp thêm cơ chế Retry (Tự động crawl lại nếu lỗi mạng) hay giới hạn tốc độ (Rate Limit) để tránh bị các web truyện chặn IP không?