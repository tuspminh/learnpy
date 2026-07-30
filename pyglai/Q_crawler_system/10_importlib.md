Version:0.9 StartHTML:0000000105 EndHTML:0000018569 StartFragment:0000000141 EndFragment:0000018533 

Thư viện **importlib** là một thư viện tích hợp sẵn (built-in) của Python, cung cấp toàn bộ cơ chế và các hàm tiện ích liên quan đến hệ thống nạp mô-đun (`import`).

Trong dự án crawler của bạn, `importlib` đóng vai trò là "chìa khóa" cốt lõi để hiện thực hóa kiến trúc **Dynamic Plugin**. Thay vì viết mã cứng (hardcode) dòng chữ `import plugins.truyenfull.source`, `importlib` cho phép bạn truyền vào một chuỗi text (string) lấy từ file cấu hình JSON và nạp code đó lên bộ nhớ khi chương trình đang chạy (Runtime).

Dưới đây là các hàm quan trọng nhất của `importlib` và cách áp dụng cụ thể vào hệ thống Plugin Manager:

* * *

**1\. Hàm quan trọng nhất: importlib.import_module()**

Hàm này nhận vào một chuỗi ký tự đại diện cho đường dẫn tuyệt đối hoặc tương đối của mô-đun và trả về đối tượng module đó.

**Cú pháp:**

python
    
    
    import importlib
    
    # Tương đương với dòng code: import plugins.truyenfull.source as module
    module = importlib.import_module("plugins.truyenfull.source")
    

Hãy thận trọng khi sử dụng mã.

**2\. Cách kết hợp importlib và getattr để khởi tạo Class động**

Khi `import_module` nạp xong file code (file `.py`), bạn cần lấy ra một Lớp (Class) hoặc Hàm cụ thể nằm trong file đó. Lúc này ta kết hợp với hàm `getattr()` toàn năng của Python.

**Ví dụ thực tế:**  
Giả sử file `plugins/tangthuvien/source.py` của bạn có nội dung:

python
    
    
    class TangThuVienSource:
        def __init__(self, client):
            self.client = client
    

Hãy thận trọng khi sử dụng mã.

Hệ thống điều phối của bạn sẽ nạp lớp này hoàn toàn bằng chuỗi chữ như sau:

python
    
    
    import importlib
    
    module_path = "plugins.tangthuvien.source"
    class_name = "TangThuVienSource"
    
    # Bước 1: Nạp file source.py động
    module = importlib.import_module(module_path)
    
    # Bước 2: Bốc lấy Class TangThuVienSource ra khỏi file vừa nạp
    PluginClass = getattr(module, class_name)
    
    # Bước 3: Khởi tạo thực thể (Instance) và truyền tham số bình thường
    scraper = PluginClass(client=my_client)
    

Hãy thận trọng khi sử dụng mã.

* * *

**3\. Hàm nâng cao: importlib.reload()**

Trong quá trình vận hành Crawler (đặc biệt là khi bạn treo máy chạy 24/7), có thể bạn sẽ vào sửa lại file `selectors.json` hoặc vá lỗi file `parser.py` của một plugin mà không muốn tắt tiến trình `main.py` đang chạy.

`importlib.reload(module)` giúp bạn **nạp lại** phiên bản mới nhất của file code đó ngay lập tức mà không cần khởi động lại toàn bộ hệ thống.

**Ví dụ:**

python
    
    
    import importlib
    import plugins.truyenfull.parser
    
    # Bạn vừa sửa code file parser.py ngoài ổ đĩa...
    # Dòng lệnh này sẽ cập nhật code mới vào bộ nhớ ngay lập tức:
    importlib.reload(plugins.truyenfull.parser)
    

Hãy thận trọng khi sử dụng mã.

* * *

**💡 Tại sao importlib giúp kiến trúc Crawler của bạn đạt điểm 10?**

  * **Loose Coupling (Giảm sự phụ thuộc):** File `main.py` hoặc `PluginManager` hoàn toàn không biết trước hệ thống có bao nhiêu plugin. Nó chỉ việc quét thư mục, thấy thư mục nào có `manifest.json` hợp lệ là nạp lên.
  * **Hot-Plugging (Cắm rút nóng):** Bạn có thể thả thêm thư mục `plugins/truyenviettienganh/` vào hệ thống ngay khi chương trình đang chạy, hệ thống vẫn tự nhận diện cấu trúc mới ở chu kỳ quét tiếp theo.



Bạn đã nắm vững cách hoạt động của `importlib` chưa, hay bạn muốn tôi tối ưu thêm cơ chế **tự động nạp lại plugin khi file code thay đổi (Auto-reload)** cho `PluginManager`?

