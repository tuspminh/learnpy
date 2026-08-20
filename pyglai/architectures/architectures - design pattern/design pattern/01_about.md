Chào bạn, việc chuyển từ tư duy Kiến trúc thượng tầng (Architectural Patterns) xuống Mẫu thiết kế chi tiết (Design Patterns) là bước đi cực kỳ quan trọng. Kiến trúc giúp bạn phân chia thư mục và ranh giới hệ thống, còn Design Patterns giúp bạn giải quyết các bài toán lập trình cụ thể trong từng file code sao cho tối ưu, dễ đọc và dễ mở rộng.

Do Python là một ngôn ngữ Dynamic Programming có các tính năng cực kỳ mạnh mẽ như _First-class functions_ , _Decorators_ , và _Dynamic Typing_ , việc triển khai Design Patterns trong Python thường gọn gàng và linh hoạt hơn nhiều so với các ngôn ngữ thuần OOP tĩnh như Java hay C#.

Dưới đây là tổng hợp chi tiết các mẫu thiết kế chia theo 3 nhóm cốt lõi: Creational (Khởi tạo), Structural (Cấu trúc), và Behavioral (Hành vi) kèm mã nguồn thực tế bằng Python.

* * *

## 🏗️ 1. Creational Patterns (Mẫu Khởi Tạo)

_Nhóm này tập trung vào các cơ chế khởi tạo đối tượng, giúp che giấu logic tạo đối tượng phức tạp và kiểm soát số lượng instance._

## Singleton Pattern

  * Mục đích: Đảm bảo một lớp (Class) chỉ có duy nhất một thể hiện (Instance) trong suốt vòng đời của ứng dụng và cung cấp một điểm truy cập toàn cục tới nó.
  * Ứng dụng thực tế: Thường dùng cho các kết nối Database (Database Connection Pool), Logger hệ thống, hoặc bộ quản lý Cấu hình (Configuration Manager).
  * Cách triển khai tối ưu trong Python: Sử dụng phương thức `__new__`.


    
    
    class DatabaseConnection:
        _instance = None
    
        def __new__(cls, *args, **kwargs):
            # Nếu chưa có instance nào được tạo, tiến hành tạo mới
            if not cls._instance:
                cls._instance = super().__new__(cls)
                # Giả lập khởi tạo kết nối nặng
                cls._instance.connection_string = "postgresql://user:secret@localhost:5432/db"
                print("[DB] Khởi tạo kết nối vật lý lần đầu tiên.")
            return cls._instance
    
    # Kiểm thử Singleton
    conn1 = DatabaseConnection()
    conn2 = DatabaseConnection()
    
    print("conn1 là conn2?", conn1 is conn2)  # Trả về True (Cùng chung 1 ô nhớ)
    

## Factory Method Pattern

  * Mục đích: Định nghĩa một interface (hoặc base class) để tạo đối tượng, nhưng để các lớp con quyết định xem lớp nào sẽ được khởi tạo.
  * Ứng dụng thực tế: Khi ứng dụng Crawl của bạn cần hỗ trợ cào từ nhiều nguồn khác nhau (SlideShare, Docco, Pinterest) dựa trên URL đầu vào.


    
    
    from abc import ABC, abstractmethod
    
    # Sản phẩm trừu tượng (Abstract Product)
    class BaseCrawler(ABC):
        @abstractmethod
        def extract(self, url: str) -> list: pass
    
    # Các sản phẩm cụ thể (Concrete Products)
    class SlideShareCrawler(BaseCrawler):
        def extract(self, url: str): return ["slide1.jpg", "slide2.jpg"]
    
    class PinterestCrawler(BaseCrawler):
        def extract(self, url: str): return ["pin1.png", "pin2.png"]
    
    # Nhà máy sản xuất (Factory)
    class CrawlerFactory:
        @staticmethod
        def get_crawler(url: str) -> BaseCrawler:
            if "slideshare.net" in url:
                return SlideShareCrawler()
            elif "pinterest.com" in url:
                return PinterestCrawler()
            raise ValueError("Hệ thống chưa hỗ trợ nguồn này!")
    
    # Sử dụng Factory
    crawler = CrawlerFactory.get_crawler("https://slideshare.net")
    print(type(crawler).__name__)  # Đầu ra: SlideShareCrawler
    

* * *

## 📐 2. Structural Patterns (Mẫu Cấu Trúc)

_Nhóm này tập trung vào cách kết hợp các lớp và đối tượng lại với nhau để tạo thành các cấu trúc lớn hơn, linh hoạt hơn._

## Decorator Pattern

  * Mục đích: Cho phép người dùng thêm tính năng mới vào một đối tượng hiện có mà không làm thay đổi cấu trúc của nó.
  * Ứng dụng thực tế: Ghi log (Logging), đo thời gian chạy hàm (Benchmarking), kiểm tra quyền truy cập (Authentication).
  * Đặc quyền của Python: Python hỗ trợ sẵn cú pháp `@decorator` cực kỳ thanh lịch mà không cần viết nhiều lớp hướng đối tượng phức tạp như Java.


    
    
    import time
    from functools import wraps
    
    def timing_decorator(func):
        """Decorator dùng để đo thời gian thực thi của bất kỳ hàm nào"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)  # Thực thi hàm gốc
            end_time = time.time()
            print(f"⏱️ Hàm '{func.__name__}' mất {end_time - start_time:.4f} giây để chạy.")
            return result
        return wrapper
    
    # Áp dụng Decorator
    @timing_decorator
    def download_heavy_file():
        print("Đang tải file nặng...")
        time.sleep(1.5)  # Giả lập độ trễ mạng
    
    download_heavy_file()
    

## Adapter Pattern

  * Mục đích: Đóng vai trò là bộ chuyển đổi giữa hai interface không tương thích, giúp chúng có thể làm việc cùng nhau.
  * Ứng dụng thực tế: Bạn có một thư viện ghi log cũ chỉ nhận định dạng XML, nhưng ứng dụng hiện tại của bạn xuất ra JSON. Bạn viết một Adapter ở giữa để dịch JSON sang XML.


    
    
    # Hệ thống cũ (Legacy System) yêu cầu format XML
    class OldXmlLogger:
        def log_xml(self, xml_data: str):
            print(f"<log>{xml_data}</log>")
    
    # Hệ thống mới phát ra JSON
    class ModernApp:
        def generate_json_log(self) -> dict:
            return {"status": "success", "message": "Ứng dụng vận hành tốt"}
    
    # Bộ chuyển đổi (Adapter)
    class LoggerAdapter:
        def __init__(self, old_logger: OldXmlLogger):
            self.old_logger = old_logger
    
        def log(self, json_data: dict):
            # Chuyển đổi dữ liệu JSON thô thành chuỗi dạng XML giả lập
            xml_equivalent = f"status='{json_data['status']}' msg='{json_data['message']}'"
            # Gọi hệ thống cũ xử lý
            self.old_logger.log_xml(xml_equivalent)
    
    # Chạy thử Adapter
    app = ModernApp()
    legacy_logger = OldXmlLogger()
    adapter = LoggerAdapter(legacy_logger)
    
    # Ứng dụng mới tương tác mượt mà với logger cũ thông qua Adapter
    json_log = app.generate_json_log()
    adapter.log(json_log)  # Đầu ra: <log>status='success' msg='Ứng dụng vận hành tốt'</log>
    

* * *

## 🎯 3. Behavioral Patterns (Mẫu Hành Vi)

_Nhóm này tập trung vào việc phân chia trách nhiệm và cách thức giao tiếp, tương tác giữa các đối tượng với nhau._

## Strategy Pattern

  * Mục đích: Định nghĩa một tập hợp các thuật toán, đóng gói từng thuật toán lại và làm cho chúng có thể thay thế lẫn nhau lúc chạy (Runtime) tùy theo ngữ cảnh.
  * Ứng dụng thực tế: Hệ thống thanh toán (chọn Momo, Thẻ tín dụng, hoặc Paypal), hoặc thuật toán nén file (ZIP, RAR, TAR).


    
    
    from abc import ABC, abstractmethod
    
    # Chiến lược trừu tượng (Abstract Strategy)
    class CompressionStrategy(ABC):
        @abstractmethod
        def compress(self, file_path: str): pass
    
    # Các chiến lược cụ thể (Concrete Strategies)
    class ZipCompression(CompressionStrategy):
        def compress(self, file_path: str): print(f"Nén file {file_path} bằng thuật toán ZIP (.zip)")
    
    class RarCompression(CompressionStrategy):
        def compress(self, file_path: str): print(f"Nén file {file_path} bằng thuật toán RAR (.rar)")
    
    # Lớp ngữ cảnh sử dụng (Context)
    class FileArchiver:
        def __init__(self, strategy: CompressionStrategy):
            self.strategy = strategy  # Cài đặt chiến lược ban đầu
    
        def set_strategy(self, strategy: CompressionStrategy):
            self.strategy = strategy  # Thay đổi chiến lược linh hoạt lúc chạy
    
        def create_archive(self, file_path: str):
            self.strategy.compress(file_path)
    
    # Sử dụng Strategy linh hoạt
    archiver = FileArchiver(ZipCompression())
    archiver.create_archive("document.pdf")  # Đầu ra: Nén bằng ZIP
    
    # Người dùng đổi ý, chuyển sang nén RAR tại thời điểm chạy runtime
    archiver.set_strategy(RarCompression())
    archiver.create_archive("document.pdf")  # Đầu ra: Nén bằng RAR
    

## Observer Pattern (Publish/Subscribe)

  * Mục đích: Định nghĩa mối quan hệ phụ thuộc một-nhiều giữa các đối tượng. Khi một đối tượng thay đổi trạng thái, tất cả các đối tượng phụ thuộc của nó sẽ tự động nhận được thông báo và cập nhật.
  * Ứng dụng thực tế: Đây chính là nền tảng cốt lõi để xây dựng Event-Driven Architecture (EDA) mà chúng ta đã làm ở các bước trước!


    
    
    # Người quan sát (Observer Interface)
    class Subscriber(ABC):
        @abstractmethod
        def update(self, message: str): pass
    
    # Các Subscriber cụ thể
    class EmailNotificationSubscriber(Subscriber):
        def update(self, message: str): print(f"[Email] Đang gửi mail thông báo: {message}")
    
    class SmsNotificationSubscriber(Subscriber):
        def update(self, message: str): print(f"[SMS] Đang gửi tin nhắn SMS: {message}")
    
    # Đối tượng bị quan sát (Subject / Publisher)
    class VideoChannel:
        def __init__(self):
            self._subscribers = []
    
        def attach(self, subscriber: Subscriber):
            self._subscribers.append(subscriber)
    
        def notify(self, video_title: str):
            for sub in self._subscribers:
                sub.update(f"Kênh vừa đăng video mới: '{video_title}'")
    
    # Vận hành hệ thống Pub/Sub
    channel = VideoChannel()
    channel.attach(EmailNotificationSubscriber())
    channel.attach(SmsNotificationSubscriber())
    
    # Kênh phát hành video mới, tất cả các subscriber tự động nhận thông báo hành vi
    channel.notify("Hướng dẫn Design Patterns trong Python")
    

* * *

## 💡 Tổng kết nhanh cách lựa chọn mẫu thiết kế thích hợp:

  1. Bạn muốn quản lý việc kết nối Database, bộ nhớ Cache dùng chung duy nhất? ➡️ Chọn Singleton.
  2. Bạn muốn tạo ra các công cụ tính toán, bò cào khác nhau dựa trên tham số đầu vào của người dùng? ➡️ Chọn Factory Method.
  3. Bạn muốn viết tính năng ghi log, đo lường tốc độ, kiểm tra quyền truy cập cho hàng chục hàm khác nhau mà không muốn copy-paste code? ➡️ Chọn Decorator.
  4. Bạn muốn tích hợp một thư viện nguồn mở cũ hoặc API bên thứ ba có cấu trúc hàm không khớp với dự án hiện tại? ➡️ Chọn Adapter.
  5. Bạn muốn viết một hệ thống xử lý logic (ví dụ: xuất báo cáo ra Excel, PDF, CSV) cho phép người dùng bấm chọn định dạng trên giao diện? ➡️ Chọn Strategy.



Nếu bạn muốn tiếp tục hành trình tối ưu hóa mã nguồn, chúng ta còn một phần rất thú vị ở danh sách ban đầu là: Các Mô hình Dữ liệu hiện đại trong Python (Pydantic Models, `@dataclass`, và cơ chế Async/Await). Bạn có muốn phân tích sâu vào phần này để biết cách tối ưu hóa cấu trúc dữ liệu cho dự án của mình không?