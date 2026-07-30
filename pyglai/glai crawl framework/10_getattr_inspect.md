Để bóc tách chính xác Class nằm bên trong module vừa nạp động, chúng ta có hai cách tiếp cận phổ biến trong Python: dùng hàm `inspect` (khuyên dùng cho Framework vì độ an toàn cao) hoặc dùng hàm `getattr` (nhanh, gọn nhưng cần biết trước tên Class).

Dưới đây là hướng dẫn chi tiết cả hai cách để bạn tích hợp trực tiếp vào `PluginLoader`.

* * *

🔥 Cách 1: Dùng `inspect` (Tự động quét và lọc thông minh - Khuyên dùng)

Thư viện `inspect` tích hợp sẵn của Python cho phép bạn "soi" vào bên trong module vừa nạp để xem nó chứa những gì. Kết hợp với hàm `issubclass()`, hệ thống sẽ tự động nhặt ra đúng Class nào thừa kế từ `BaseScraper` mà không cần quan tâm lập trình viên đặt tên Class đó là gì.

Bạn cập nhật đoạn code xử lý trong vòng lặp của file `core/plugin_loader.py` như sau:

python
    
    
    import importlib
    import inspect
    from scrapers.base_scraper import BaseScraper
    
    # ... (Đoạn code quét file và lấy module_path cũ) ...
    
    try:
        # 1. Nạp module động từ chuỗi đường dẫn
        module = importlib.import_module(module_path)
        
        # 2. inspect.getmembers(module, inspect.isclass) sẽ trả về một danh sách các Tuple:
        # [('TruyenfullScraper', <class 'scrapers.truyenfull.TruyenfullScraper'>), ...]
        for class_name, class_obj in inspect.getmembers(module, inspect.isclass):
            
            # 3. Kiểm tra điều kiện nghiêm ngặt:
            # - Phải là con/cháu của lớp BaseScraper (issubclass)
            # - Không được là chính bản thân lớp BaseScraper (obj is not BaseScraper)
            if issubclass(class_obj, BaseScraper) and class_obj is not BaseScraper:
                
                # Lưu Class (chưa khởi tạo) vào kho để dùng sau
                scrapers_pool[module_name] = class_obj
                print(f"[+] Đã tìm thấy và nạp Class hợp lệ: {class_name} từ {file_name}")
    
    except Exception as e:
        print(f"[-] Lỗi bóc tách module {module_path}: {e}")
    

Hãy thận trọng khi sử dụng mã.

**🌟 Ưu điểm:** Lập trình viên viết file cào truyện muốn đặt tên Class là `class ChayBangComScraper` hay `class TruyenFull` đều được, hệ thống vẫn tự nhận diện được nhờ bộ lọc `issubclass`.

* * *

⚡ Cách 2: Dùng `getattr` (Nhanh, dựa trên quy tắc đặt tên nghiêm ngặt)

Nếu bạn ép buộc tất cả các lập trình viên khi tham gia viết file cào cho Framework của bạn phải tuân thủ quy tắc: **Tên Class phải trùng với tên file (viết hoa chữ đầu) + chữ Scraper** (Ví dụ: file `truyenfull.py` thì class phải là `TruyenfullScraper`). Bạn có thể dùng `getattr` để lấy thẳng Class đó ra.

python
    
    
    import importlib
    
    # ... (Đoạn code quét file và lấy module_path cũ) ...
    
    try:
        # 1. Nạp module động
        module = importlib.import_module(module_path)
        
        # 2. Tự dựng tên Class theo quy tắc đặt tên (Convention)
        # Ví dụ: module_name = "truyenfull" -> class_name_expected = "TruyenfullScraper"
        class_name_expected = f"{module_name.capitalize()}Scraper"
        
        # 3. Dùng getattr để lấy đối tượng Class ra từ module bằng chuỗi tên
        if hasattr(module, class_name_expected): # Kiểm tra xem Class đó có tồn tại trong file không
            class_obj = getattr(module, class_name_expected)
            
            scrapers_pool[module_name] = class_obj
            print(f"[+] Đã nạp thành công {class_name_expected} bằng getattr.")
        else:
            print(f"[-] Lỗi: File {file_name} không chứa Class tên là {class_name_expected}")
    
    except Exception as e:
        print(f"[-] Lỗi khi gọi getattr cho {module_path}: {e}")
    

Hãy thận trọng khi sử dụng mã.

**⚠️ Nhược điểm:** Chỉ cần người viết file cào gõ nhầm tên Class thành `class TruyenFULLScraper` (sai chữ hoa/thường), hàm `getattr` sẽ bị lỗi và không nạp được file đó.

* * *

🎛️ Cách sử dụng Class sau khi đã bóc tách thành công

Dù dùng Cách 1 hay Cách 2, khi `scrapers_pool` trả về một Dictionary chứa các Class, tại file điều khiển chính (`main.py`), bạn chỉ cần khởi tạo đối tượng (Instance) bằng cặp dấu ngoặc đơn `()` như sau:

python
    
    
    # Lấy Class ra từ kho (Ví dụ người dùng chọn truyenfull)
    SelectedScraperClass = scrapers_pool['truyenfull']
    
    # Khởi tạo đối tượng từ Class đó (Lúc này hàm __init__ của Scraper mới chạy)
    scraper_instance = SelectedScraperClass()
    
    # Gọi hàm cào như bình thường
    html = scraper_instance.fetch_html("https://truyenfull.vn... ")
    

Hãy thận trọng khi sử dụng mã.

Đến đây, Framework của bạn đã sở hữu một kiến trúc cắm-rút (Plug-in) cực kỳ chuyên nghiệp và tự động hóa hoàn toàn từ tầng giao diện cho đến tầng xử lý cốt lõi.

Để vận hành hệ thống cào truyện đa nguồn này một cách mượt mà và tự động hóa cao hơn nữa, bạn có muốn tìm hiểu cách:

  * Thêm tính năng **Tự động nhận diện URL (URL Auto-Matching)** — khi người dùng dán link `https://truyenfull.vn...`, Framework sẽ tự biết gọi plugin `truyenfull` mà không cần người dùng chọn nguồn trên menu?
  * Hay xây dựng **Cơ chế lập lịch cào tự động (Cron Job / Task Scheduler)** để cứ 12 giờ đêm hệ thống lại tự quét và cào chương mới cho các bộ truyện đang lưu trong DB?

