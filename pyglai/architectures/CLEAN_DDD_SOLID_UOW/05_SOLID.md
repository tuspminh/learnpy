Dưới đây là cách áp dụng chi tiết từng nguyên lý trong bộ SOLID vào dự án Crawl & Đọc truyện bằng SQLite thuần đã thiết kế ở trên. Việc hiểu rõ từng nguyên lý giúp bạn kiểm soát mã nguồn tốt hơn khi dự án phình to.

* * *

## 1\. S - Single Responsibility Principle (Nguyên lý đơn nhiệm)

> _Một lớp (Class) chỉ nên giữ một trách nhiệm duy nhất và chỉ có một lý do duy nhất để thay đổi._

  * Sai thiết kế: Gộp logic tự động đánh số thứ tự chương và câu lệnh SQL `INSERT INTO chapters` vào chung một hàm trong class `Story`. Khi bạn đổi từ SQLite sang PostgreSQL hoặc đổi cách đánh số chương (v.v. Chương 1.1, 1.2), bạn đều phải sửa class này.
  * Đúng thiết kế (Đã áp dụng):

    * `Story` (Domain Model): Chỉ chịu trách nhiệm quản lý quy tắc nghiệp vụ của truyện (ví dụ: một chương mới thêm vào thì số thứ tự `order_index` tăng lên như thế nào). Nó không quan tâm dữ liệu được lưu vào đâu.
    * `SQLiteStoryRepository` (Infrastructure): Chỉ chịu trách nhiệm biên dịch đối tượng Domain thành các câu lệnh SQL thuần (`INSERT`, `SELECT`) để nói chuyện với SQLite.
    * `FakeWebCrawler` (Infrastructure): Chỉ chịu trách nhiệm bóc tách HTML từ internet.




* * *

## 2\. O - Open/Closed Principle (Nguyên lý Đóng/Mở)

> _Một thành phần phần mềm nên mở rộng cho việc phát triển (Open for extension) nhưng đóng lại với việc sửa đổi (Closed for modification)._

  * Tình huống: Hệ thống hiện tại đang cào truyện dạng chữ thuần (Text). Tương lai, bạn muốn mở rộng hệ thống để cào thêm Truyện tranh (Comic) (cần lưu danh sách link ảnh thay vì nội dung chữ).
  * Áp dụng trong code: Bạn không được vào sửa class `Story` hoặc sửa Use Case hiện tại (vì sẽ làm ảnh hưởng đến tính năng đọc truyện chữ đang chạy ổn định). Thay vào đó, bạn tạo ra một lớp mới kế thừa từ `Story`.


    
    
    # Mở rộng bằng cách tạo lớp mới, không sửa lớp cũ
    @dataclass
    class ComicStory(Story):
        image_urls: List[str] = field(default_factory=list)
        
        # Ghi đè hoặc bổ sung logic mới cho truyện tranh
        def add_page(self, url: str):
            self.image_urls.append(url)
    

* * *

## 3\. L - Liskov Substitution Principle (Nguyên lý thay thế Liskov)

> _Các đối tượng của lớp con phải có thể thay thế các đối tượng của lớp cha mà không làm thay đổi tính đúng đắn của chương trình._

  * Ý nghĩa: Khi bạn tạo ra một lớp triển khai mới (ví dụ: một Crawler mới), lớp đó phải tuân thủ đúng cam kết (Interface) của lớp cha. Nó không được phép ném ra những ngoại lệ (Exception) lạ lẫm khiến tầng ứng dụng bị sập, hoặc thay đổi kiểu dữ liệu trả về.
  * Áp dụng trong code: Tầng Use Case gọi `crawler.fetch_story_details(url)`. Hệ thống chạy chuẩn xác dù bạn truyền vào bất kỳ phiên bản Crawler nào dưới đây:


    
    
    # Cả 2 lớp con này đều trả về đúng kiểu dữ liệu `Story` giống như lớp cha cam kết
    class NetTruyenCrawler(CrawlService):
        def fetch_story_details(self, url: str) -> Story:
            # Code dùng BeautifulSoup cào trang NetTruyen
            return Story(...)
    
    class TruyenFullCrawler(CrawlService):
        def fetch_story_details(self, url: str) -> Story:
            # Code dùng Playwright cào trang TruyenFull
            return Story(...)
    

* * *

## 4\. I - Interface Segregation Principle (Nguyên lý phân tách Interface)

> _Thay vì sử dụng một Interface lớn chứa tất cả các phương thức, nên tách thành nhiều Interface nhỏ với các mục đích cụ thể. Client không nên bị ép buộc phụ thuộc vào các phương thức mà nó không sử dụng._

  * Sai thiết kế: Tạo ra một Interface `StoryService` khổng lồ chứa cả `crawl_from_web()`, `save_to_db()`, `read_chapter()`, `create_bookmark()`. Khi đó, lớp `FakeWebCrawler` chỉ muốn làm nhiệm vụ cào web cũng bị ép buộc phải viết code rỗng cho các hàm `read_chapter()` hay `save_to_db()`.
  * Đúng thiết kế (Đã áp dụng): Tách thành các Interface nhỏ gọn, độc lập tuyệt đối:

    * `CrawlService`: Chỉ chứa hàm phục vụ việc lấy dữ liệu từ Internet.
    * `StoryRepository`: Chỉ chứa các hàm tương tác CRUD với Database.




* * *

## 5\. D - Dependency Inversion Principle (Nguyên lý đảo ngược phụ thuộc)

> _Các mô-đun cấp cao không nên phụ thuộc vào các mô-đun cấp thấp. Cả hai nên phụ thuộc vào sự trừu tượng (Interface). Sự trừu tượng không nên phụ thuộc vào chi tiết, chi tiết phải phụ thuộc vào sự trừu tượng._

Đây là xương sống của Clean Architecture. Nó quyết định cách dòng phụ thuộc chạy từ ngoài vào trong.

  * Mô-đun cấp cao: `CrawlStoryUseCase` (Logic nghiệp vụ cào truyện).
  * Mô-đun cấp thấp: `SQLiteStoryRepository` (Chi tiết kết nối SQLite), `requests/BeautifulSoup` (Chi tiết cào web).
  * Sai thiết kế: Trong file `use_cases.py`, bạn viết `import sqlite3` hoặc `from src.infrastructure.repositories.sqlite_repo import SQLiteStoryRepository`. Lúc này, tầng nghiệp vụ bị dính chặt vào SQLite. Nếu muốn đổi sang lưu bằng file JSON hoặc MySQL, bạn phải đập đi viết lại Use Case.
  * Đúng thiết kế (Đã áp dụng): `CrawlStoryUseCase` chỉ import `StoryRepository` (là một Abstract Class - sự trừu tượng).

    * Use Case nói: _"Tôi chỉ cần một thực thể có hàm`.save()`. Tôi không quan tâm anh lưu vào SQLite hay Oracle"_.
    * Lớp cấp thấp `SQLiteStoryRepository` phải tự `import` cái Interface đó về và code tuân thủ theo nó (Đảo ngược sự phụ thuộc).




* * *

## 📊 Bảng tổng hợp sự liên kết trong dự án của bạn

Nguyên lý SOLID| Vị trí áp dụng trong code của bạn| Lợi ích trực tiếp  
---|---|---  
S (Đơn nhiệm)| Tách biệt `Story` (quy tắc), `SQLiteStoryRepository` (SQL), `FakeWebCrawler` (mạng).| Code ngắn, sửa chỗ này không sợ hỏng chỗ kia.  
O (Đóng/Mở)| Định nghĩa `Story` làm lớp cơ sở, sẵn sàng tạo `ComicStory` mà không sửa code cũ.| Thêm tính năng mới không sợ làm lỗi tính năng cũ.  
L (Thay thế)| `NetTruyenCrawler` và `TruyenFullCrawler` thay thế hoàn hảo cho `CrawlService`.| Hệ thống linh hoạt, đổi nguồn cào truyện trong 1 dòng code.  
I (Phân tách)| Tách biệt `CrawlService` riêng và `StoryRepository` riêng.| Các lớp không bị ép buộc viết những hàm không dùng tới.  
D (Đảo ngược)| Use Case chỉ gọi `AbstractUnitOfWork` và `CrawlService` (Dạng trừu tượng ABC).| Tách rời hoàn toàn khỏi SQLite và thư viện mạng. Dễ dàng viết Unit Test bằng Mock/Fake dữ liệu.  
  
Nếu bạn đã nắm rõ lý thuyết SOLID này, bước tiếp theo chúng ta có thể làm gì?

  * Bạn có muốn viết thử một file Unit Test (`pytest`) hoàn chỉnh cho `CrawlStoryUseCase` bằng cách áp dụng triệt để nguyên lý D (sử dụng một `FakeUnitOfWork` chạy trên RAM để không cần tạo file database thật khi test) không?
  * Hay bạn muốn triển khai thực tế mã nguồn cho lớp `WebCrawler` sử dụng thư viện BeautifulSoup để cào một trang truyện thật?