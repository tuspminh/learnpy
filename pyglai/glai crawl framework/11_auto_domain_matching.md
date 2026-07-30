Để hệ thống tự động nhận diện URL người dùng nhập vào thuộc về website nào và tự kích hoạt plugin tương ứng (không bắt người dùng chọn nguồn thủ công), chúng ta sẽ bổ sung một thuộc tính định danh URL vào lớp cơ sở `BaseScraper`.

Khi người dùng dán một link bất kỳ, **Logic Tier** sẽ duyệt qua tất cả các plugin đã nạp động để tìm ra plugin phù hợp nhất.

* * *

🛠️ 1. Cập nhật Scraper (Plug-in) để tự nhận diện domain

Chúng ta cần thêm một thuộc tính là **`ALLOWED_DOMAINS`** (Danh sách các tên miền được phép cào) hoặc một hàm kiểm tra URL vào cấu trúc của Scraper.

Bước A: Cập nhật file cơ sở `scrapers/base_scraper.py`

python
    
    
    from abc import ABC, abstractmethod
    
    class BaseScraper(ABC):
        # Thuộc tính bắt buộc các file con phải định nghĩa (Ví dụ: ['truyenfull.vn', 'truyenfull.com'])
        ALLOWED_DOMAINS = []
    
        def __init__(self):
            self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
        def is_match_url(self, url: str) -> bool:
            """Kiểm tra xem URL người dùng nhập vào có thuộc về Scraper này không"""
            url_lower = url.lower()
            for domain in self.ALLOWED_DOMAINS:
                if domain.lower() in url_lower:
                    return True
            return False
    
        @abstractmethod
        def extract_story_info(self, html, url): pass
    
        @abstractmethod
        def extract_chapters_list(self, html): pass
    
        @abstractmethod
        def extract_chapter_content(self, html): pass
    

Hãy thận trọng khi sử dụng mã.

Bước B: Định nghĩa danh mục domain trong file con (Ví dụ: `scrapers/truyenfull.py`)

python
    
    
    from scrapers.base_scraper import BaseScraper
    
    class TruyenfullScraper(BaseScraper):
        # Khai báo các domain mà plugin này có thể xử lý
        ALLOWED_DOMAINS = ["truyenfull.vn", "truyenfull.io", "truyenfull.com"]
    
        def extract_story_info(self, html, url):
            return {"title": "Truyện cào từ TruyenFull", "author": "Tác giả"}
    
        def extract_chapters_list(self, html):
            return []
    
        def extract_chapter_content(self, html):
            return "Nội dung..."
    

Hãy thận trọng khi sử dụng mã.

* * *

⚙️ 2. Nâng cấp bộ điều phối Logic Tier (`core/crawler_engine.py`)

Chúng ta sẽ tạo ra một hàm điều phối thông minh. Hàm này nhận vào URL thô từ người dùng, gọi `PluginLoader` để lấy tất cả các plugin đang có, sau đó tìm ra plugin có `ALLOWED_DOMAINS` khớp với URL đó.

python
    
    
    from core.plugin_loader import PluginLoader
    
    class CrawlerEngine:
        def __init__(self):
            # Nạp động toàn bộ các Class plugin đang có trong thư mục scrapers/
            loader = PluginLoader()
            self.scrapers_pool = loader.discover_scrapers()
    
        def get_scraper_for_url(self, url: str):
            """Quét toàn bộ kho plugin để tìm ra Scraper phù hợp với URL"""
            for source_name, ScraperClass in self.scrapers_pool.items():
                # Khởi tạo thử đối tượng để chạy hàm kiểm tra
                scraper_instance = ScraperClass()
                
                if scraper_instance.is_match_url(url):
                    return scraper_instance, source_name
                    
            return None, None
    
        def execute_by_url(self, story_url: str):
            """Hàm thực thi tự động nhận diện thông minh"""
            print(f"[*] Đang phân tích hệ thống phân phối cho URL: {story_url}")
            
            # 1. Tự động tìm kiếm Scraper phù hợp
            scraper, source_name = self.get_scraper_for_url(story_url)
            
            if not scraper:
                print("[-] Thất bại: Không tìm thấy Plugin Scraper nào hỗ trợ tên miền này!")
                print("[*] Vui lòng viết thêm file plugin mới trong thư mục scrapers/ để mở rộng.")
                return
    
            print(f"[+] Nhận diện thành công! Hệ thống chọn Plugin: [{source_name.upper()}]")
            
            # 2. Tiến hành các bước cào truyện như cũ (Đã triển khai ở các phần trước)
            # story_html = scraper.fetch_html(story_url)
            # ... logic lưu DB, đa luồng ...
    

Hãy thận trọng khi sử dụng mã.

* * *

🎛️ 3. Cập nhật Presentation Tier (`main.py`) để tối giản giao diện

Nhờ có tính năng tự động nhận diện URL, giao diện dòng lệnh của bạn sẽ cực kỳ tinh gọn. Người dùng không cần phải chọn số 1 cho TruyenFull, số 2 cho Webnovel nữa. Họ chỉ cần dán link vào và hệ thống tự lo phần còn lại.

python
    
    
    from core.crawler_engine import CrawlerEngine
    
    def run_smart_crawler():
        print("\n--- TRÌNH CÀO TRUYỆN TỰ ĐỘNG NHẬN DIỆN ---")
        story_url = input("Dán URL truyện cần cào vào đây: ").strip()
        
        if not story_url:
            print("[!] URL không được để trống.")
            return
    
        # Khởi động Engine thông minh
        engine = CrawlerEngine()
        engine.execute_by_url(story_url)
        
        input("\nNhấn Enter để quay lại trang chủ...")
    

Hãy thận trọng khi sử dụng mã.

* * *

💎 Điểm mấu chốt của tính năng này:

Bây giờ, Framework của bạn đã đạt đến độ tự động hóa rất cao. Nếu tuần sau bạn thêm một file plug-in mới là `scrapers/webnovel.py` và khai báo `ALLOWED_DOMAINS = ["webnovel.com"]`:

  * Bạn **không cần** sửa menu giao diện.
  * Bạn **không cần** cấu hình định tuyến (Routing).
  * Người dùng chỉ cần mở phần mềm lên, dán link `https://webnovel.com...`, hệ thống dùng `importlib` nạp file lên, chạy hàm quét chuỗi và tự biết phải dùng file `webnovel.py` để xử lý văn bản.



Nếu bạn muốn tiếp tục nâng cấp hệ thống này, cho tôi biết bạn có muốn tìm hiểu về **Cơ chế lập lịch tự động (Task Scheduler)** — cứ đúng giờ hẹn phần mềm sẽ tự quét Database, lấy các URL truyện ra kiểm tra xem website gốc có chương mới chưa để tự động cào nối tiếp không?

