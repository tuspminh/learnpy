Sử dụng thư viện tích hợp sẵn `importlib` là một giải pháp **cực kỳ xuất sắc** để nâng cấp Framework này lên mức **Dynamic Plug-in Architecture (Kiến trúc cắm-rút động)**.

Thay vì phải vào file `main.py` khai báo cứng `from scrapers.source_a import SourceAScraper` bằng tay, `importlib` cho phép hệ thống tự động quét thư mục `scrapers/`, phát hiện ra các file scraper mới và tự động nạp (load) chúng vào hệ thống khi ứng dụng đang chạy.

Dưới đây là cách tái cấu trúc lại **Presentation Tier** và **Logic Tier** để biến các file cào nguồn truyện thành các Plug-in hoàn toàn độc lập.

* * *

🏛️ 1. Nguyên lý hoạt động với 3-Tier Architecture

Khi áp dụng `importlib`, cấu trúc 3 tầng vẫn được giữ vững nhưng linh hoạt hơn:

  * **Data Tier & Logic Engine:** Giữ nguyên 100%.
  * **Scrapers (Plug-ins):** Mỗi website cần cào chỉ cần vứt một file `.py` vào thư mục `scrapers/`.
  * **Presentation Tier / Main Entry:** Tự quét thư mục, tự nhận diện nguồn truyện và hiển thị lên Menu cho người dùng chọn.



* * *

💻 2. Cấu trúc lại mã nguồn

Bước A: Chuẩn hóa quy tắc đặt tên (Convention)

Để `importlib` tự động tìm và ánh xạ đúng lớp (Class) bên trong file, chúng ta cần đặt ra một quy chuẩn đặt tên.

  * _Quy tắc:_ Tên file viết thường (`truyenfull.py`), tên Class bên trong viết theo dạng CamelCase và kết thúc bằng chữ Scraper (`class TruyenfullScraper`).



**Ví dụ file plug-in mới:** `scrapers/truyenfull.py`

python
    
    
    from scrapers.base_scraper import BaseScraper
    
    # Tên class bắt buộc tuân theo quy tắc: [Tên_file_viết_hoa_chữ_đầu]Scraper
    class TruyenfullScraper(BaseScraper):
        def extract_story_info(self, html, url):
            return {"title": "Truyện Demo TruyenFull", "author": "Tác Giả A"}
    
        def extract_chapters_list(self, html):
            return [{"title": "Chương 1", "url": "https://example.com"}]
    
        def extract_chapter_content(self, html):
            return "Nội dung chữ truyện chữ demo..."
    

Hãy thận trọng khi sử dụng mã.

* * *

Bước B: Tạo module quản lý Plug-in bằng `importlib` (Logic Tier)

Chúng ta tạo một file `core/plugin_loader.py` để quét thư mục và nạp động các Class Scraper.

**File:** `core/plugin_loader.py`

python
    
    
    import os
    import importlib
    import inspect
    from scrapers.base_scraper import BaseScraper
    
    class PluginLoader:
        def __init__(self, plugin_dir="scrapers"):
            self.plugin_dir = plugin_dir
    
        def discover_scrapers(self) -> dict:
            """
            Tự động quét thư mục scrapers/ và nạp động các Class
            Trả về một Dictionary dạng: {'truyenfull': Class_TruyenfullScraper, 'webnovel': Class_WebnovelScraper}
            """
            scrapers_pool = {}
            
            # 1. Liệt kê các file trong thư mục scrapers
            if not os.path.exists(self.plugin_dir):
                return scrapers_pool
    
            for file_name in os.listdir(self.plugin_dir):
                # Chỉ lấy các file .py và bỏ qua các file hệ thống, file base
                if file_name.endswith(".py") and file_name not in ["__init__.py", "base_scraper.py"]:
                    module_name = file_name[:-3] # Bỏ đuôi .txt -> 'truyenfull'
                    
                    try:
                        # 2. Nạp động module bằng importlib
                        # Tương đương câu lệnh: import scrapers.truyenfull
                        module_path = f"{self.plugin_dir}.{module_name}"
                        module = importlib.import_module(module_path) [1]
                        
                        # 3. Tìm Class hợp lệ bên trong module vừa nạp [1]
                        # Quy tắc: Class phải là con của BaseScraper và không phải bản thân BaseScraper
                        for name, obj in inspect.getmembers(module, inspect.isclass): [1]
                            if issubclass(obj, BaseScraper) and obj is not BaseScraper:
                                scrapers_pool[module_name] = obj
                                
                    except Exception as e:
                        print(f"[-] Lỗi khi nạp plug-in {file_name}: {e}")
                        
            return scrapers_pool
    

Hãy thận trọng khi sử dụng mã.

* * *

Bước C: Cập nhật Presentation Tier (`main.py`)

Bây giờ, file giao diện chính hoàn toàn sạch bóng các câu lệnh `import` cứng tên nguồn truyện. Nó sẽ gọi `PluginLoader` để tự dựng menu tùy biến.

**File:** `main.py` (Phiên bản tối ưu với `importlib`)

python
    
    
    import os
    from core.plugin_loader import PluginLoader
    from core.crawler_engine import CrawlerEngine
    from presentation.cli_viewer import CLIViewer
    
    def run_dynamic_crawler():
        """Luồng cào truyện tự động nhận diện tất cả các nguồn bằng importlib"""
        print("\n--- HỆ THỐNG CÀO TRUYỆN ĐA NGUỒN (PLUG-IN ARCHITECTURE) ---")
        
        # 1. Quét và nạp danh sách các nguồn cào đang có trong thư mục scrapers/
        loader = PluginLoader()
        scrapers_pool = loader.discover_scrapers()
        
        if not scrapers_pool:
            print("[!] Không tìm thấy bất kỳ file Scraper plug-in nào trong thư mục scrapers/.")
            input("\nNhấn Enter để quay lại...")
            return
    
        # 2. Hiển thị danh sách nguồn động lên menu
        sources_list = list(scrapers_pool.keys())
        for idx, source in enumerate(sources_list, start=1):
            print(f"{idx}. Cào từ nguồn: {source.upper()}")
            
        print("0. Quay lại mục lục")
        print("---------------------------------------------------------")
        
        choice = input("Chọn nguồn muốn cào: ").strip()
        if choice == "0" or not choice.isdigit() or int(choice) > len(sources_list):
            return
    
        selected_source_name = sources_list[int(choice) - 1]
        
        # 3. Khởi tạo đối tượng (Instance) từ Class được nạp động [1]
        ScraperClass = scrapers_pool[selected_source_name]
        scraper_instance = ScraperClass() # Tự động tạo đối tượng cào tương ứng
    
        story_url = input(f"Nhập URL truyện của {selected_source_name.upper()}: ").strip()
        if not story_url:
            return
    
        # 4. Truyền đối tượng nạp động vào Logic Engine chạy như bình thường
        engine = CrawlerEngine(scraper_instance, selected_source_name)
        engine.execute(story_url)
        input("\nBấm Enter để quay lại trang chủ...")
    
    def main():
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("=======================================")
            print("    CRAWLER FRAMEWORK PLUG-IN SYSTEM   ")
            print("=======================================")
            print("1. Kích hoạt Trình cào truyện (Tự động nhận diện nguồn)")
            print("2. Vào Thư viện đọc truyện (Đọc từ Database)")
            print("0. Thoát chương trình")
            print("=======================================")
            
            choice = input("Nhập lựa chọn của bạn (0-2): ").strip()
            if choice == "1":
                run_dynamic_crawler()
            elif choice == "2":
                viewer = CLIViewer()
                viewer.show_main_menu()
            elif choice == "0":
                break
    
    if __name__ == "__main__":
        main()
    

Hãy thận trọng khi sử dụng mã.

* * *

💎 3. Lợi ích tối thượng của nâng cấp này

  1. **Mở rộng không giới hạn (Zero-configuration):** Từ nay về sau, nếu bạn muốn cào thêm trang `webnovel.com`, `tangthuvien.net`, `nettruyen`, bạn chỉ cần code 1 file parser và **ném file đó vào thư mục`scrapers/`**. Hệ thống tự nhận diện và tự thêm vào menu mà không bắt bạn sửa đổi một dòng code nào ở file `main.py`.
  2. **Đóng gói độc lập (Hot-swapping):** Bạn có thể sửa code bóc tách HTML của file `truyenfull.py` khi website này đổi giao diện ngay cả khi ứng dụng đang chạy. Trong lần bấm nút cào tiếp theo, `importlib` sẽ nạp lại phiên bản code mới nhất mà không cần khởi động lại ứng dụng.



Nếu bạn muốn hoàn thiện trọn vẹn mô hình Plug-in nâng cao này, hãy cho tôi biết:

  * Bạn có muốn thêm **hàm kiểm tra tính hợp lệ của URL (URL Validation)** vào mỗi Plug-in để hệ thống tự động nhận diện URL người dùng nhập vào thuộc về nguồn nào (không cần người dùng chọn nguồn bằng tay) không?
  * Hay bạn muốn tìm hiểu cách xử lý **tải bất đồng bộ các Plug-in** để tăng tốc độ khởi động framework?

