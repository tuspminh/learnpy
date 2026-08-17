Để tự động hóa việc nạp các lớp Infrastructure vào Use Case mà không cần phải khởi tạo thủ công bằng tay (hardcode) trong từng Worker, chúng ta sẽ áp dụng Dependency Injection (DI) thông qua một thư viện DI Container chuyên nghiệp rất phổ biến trong Python là `dependency-injector`.

DI Container đóng vai trò như một "nhà kho trung tâm". Khi Worker cần chạy một Use Case, nó chỉ cần yêu cầu Container cung cấp, Container sẽ tự động tìm kiếm, lắp ráp các thành phần liên quan (Database, Crawler, Repository) và trả về một Use Case hoàn chỉnh.

* * *

## 💡 Quy trình thiết kế DI cho Crawl Worker

Chúng ta sẽ tạo một file cấu hình tập trung để quản lý toàn bộ các thành phần (Dependencies). Sơ đồ lắp ráp sẽ như sau:  
`BeautifulSoupCrawler` \+ `SQLAlchemyRepository` ➡️ lắp vào ➡️ `CheckNewChaptersUseCase`.

* * *

## 🛠️ Triển khai mã nguồn từng bước

Trước tiên, bạn cần cài đặt thư viện hỗ trợ DI bằng lệnh:
    
    
    pip install dependency-injector
    

## 📌 Bước 1: Tạo file cấu hình Container (`src/infrastructure/container.py`)

File này định nghĩa cách khởi tạo và kết nối các đối tượng với nhau. Nó đọc cấu hình (như Database URL) và tự động "tiêm" (inject) các phụ thuộc vào đúng vị trí.
    
    
    from dependency_injector import containers, providers
    
    # Import các lớp từ tầng Domain và Use Cases
    from src.use_cases.check_new_chapters import CheckNewChaptersUseCase
    
    # Import các lớp triển khai thực tế từ tầng Infrastructure
    from src.infrastructure.repositories.sqlalchemy_repository import SQLAlchemyNovelRepository
    from src.infrastructure.crawlers.beautiful_soup_crawler import BeautifulSoupCrawler
    
    class AppContainer(containers.DeclarativeContainer):
        """Nơi quản lý và cấu hình tập trung tất cả các phụ thuộc trong hệ thống"""
        
        # 1. Cấu hình các tham số môi trường
        config = providers.Configuration()
    
        # 2. Khởi tạo các dịch vụ ở tầng Infrastructure (Chỉ khởi tạo một lần - Singleton)
        novel_repository = providers.Singleton(
            SQLAlchemyNovelRepository,
            db_url=config.database.url
        )
        
        novel_crawler = providers.Singleton(
            BeautifulSoupCrawler
        )
    
        # 3. Cấu hình và tự động 'tiêm' (Inject) Infrastructure vào Use Cases
        check_new_chapters_use_case = providers.Factory(
            CheckNewChaptersUseCase,
            novel_repo=novel_repository,  # Tự động truyền đối tượng novel_repository vào đây
            crawler=novel_crawler         # Tự động truyền đối tượng novel_crawler vào đây
        )
    

* * *

## 📌 Bước 2: Viết mã nguồn cho Worker sử dụng Container (`src/apps/worker_runner.py`)

Bây giờ, mã nguồn của Worker trở nên cực kỳ ngắn gọn và sạch sẽ. Worker không cần biết bên trong `CheckNewChaptersUseCase` cần những thư viện nào, nó chỉ cần gọi từ Container ra để sử dụng.
    
    
    import time
    import queue
    from multiprocessing.managers import BaseManager
    from src.infrastructure.container import AppContainer
    
    class QueueManager(BaseManager): 
        pass
    
    QueueManager.register('get_priority_queue')
    
    if __name__ == '__main__':
        # 1. Khởi tạo và cấu hình DI Container
        container = AppContainer()
        
        # Giả lập nạp cấu hình hệ thống (Thực tế bạn có thể đọc từ file .env hoặc yaml)
        container.config.database.url.from_value("postgresql://admin:password@localhost:5432/novel_db")
        
        # 2. Kết nối hệ thống Hàng đợi (Queue Server)
        address = ('127.0.0.1', 50000)
        manager = QueueManager(address=address, authkey=b'novel_crawl_secret')
        manager.connect()
        remote_queue = manager.get_priority_queue()
        print(" [Worker] Đã kết nối Queue thành công!")
        print(" [Worker] Đang lắng nghe tác vụ xử lý...")
    
        # 3. Vòng lặp nhận việc từ Queue và thực thi
        while True:
            try:
                priority, task_data = remote_queue.get(timeout=5)
                
                if task_data["action"] == "check_chapters":
                    novel_id = task_data["novel_id"]
                    
                    # CHÍNH XÁC TẠI ĐÂY: Lấy Use Case đã được Container lắp ráp hoàn chỉnh sẵn
                    use_case = container.check_new_chapters_use_case()
                    
                    # Thực thi nghiệp vụ
                    use_case.execute(novel_id)
                    
            except queue.Empty:
                time.sleep(2)
            except KeyboardInterrupt:
                print(" [Worker] Đã dừng tiến trình.")
                break
    

* * *

## 🌟 Lợi ích thực tế lớn nhất khi áp dụng DI kết hợp Clean/DDD

Để thấy rõ tại sao kiến trúc này lại mạnh mẽ, bạn hãy hình dung 2 kịch bản thay đổi yêu cầu dự án dưới đây:

## Kịch bản A: Thay đổi công nghệ (Ví dụ: Chuyển từ BeautifulSoup sang Playwright)

Khi trang web truyện nâng cấp bảo mật, bắt buộc phải dùng trình duyệt giả lập Playwright để cào dữ liệu thay vì Requests thuần.

  * Nếu không có DI: Bạn phải tìm tất cả các file Worker, file Use Case để sửa lại đoạn code khởi tạo crawler mới.
  * Khi có DI: Bạn viết một file mới là `src/infrastructure/crawlers/playwright_crawler.py`. Sau đó, bạn chỉ cần vào đúng 1 dòng duy nhất trong file `container.py` để đổi:
        
        # Từ thế này:
        novel_crawler = providers.Singleton(BeautifulSoupCrawler)
        # Đổi thành thế này:
        novel_crawler = providers.Singleton(PlaywrightCrawler)
        

Toàn bộ hệ thống Worker và Use Case tự động chạy trên nền tảng Playwright mới mà không cần chỉnh sửa một dòng code nghiệp vụ nào!



## Kịch bản B: Viết Unit Test cho Worker cực dễ (Mocking)

Khi viết kiểm thử tự động, bạn không muốn Worker chạy cào dữ liệu thật từ Internet (làm chậm test) hoặc ghi dữ liệu thật vào Database. Trong file kiểm thử, bạn chỉ cần tạo một `MockContainer` truyền các Repository giả lập (chỉ lưu dữ liệu vào RAM) là có thể test toàn bộ luồng xử lý của Use Case trong vòng chưa đầy 1 giây.

Để hệ thống hoàn chỉnh hơn, bạn có muốn tích hợp thêm cơ chế ghi log tập trung (Logging) theo từng tiến trình Worker để dễ dàng kiểm tra xem URL nào bị lỗi khi hệ thống chạy thực tế không?