Version:0.9 StartHTML:0000000105 EndHTML:0000034079 StartFragment:0000000141 EndFragment:0000034043 

### code: plugin_manager.py

Dưới đây là mã nguồn hoàn chỉnh cho file **plugins/plugin_manager.py**.

File này được thiết kế để tự động quét toàn bộ thư mục `plugins/`, đọc tệp `manifest.json` của từng plugin con (như `truyenfull`, `tangthuvien`), sau đó nạp động (dynamic import) các lớp mã nguồn vào hệ thống bằng thư viện `importlib`.

* * *

**📄 plugins/plugin_manager.py**

python
    
    
    import os
    import json
    import importlib
    import logging
    from typing import Dict, Type, List
    from plugins.base.base_source import BaseSource
    from plugins.base.http_client import HTTPClient
    from plugins.base.exceptions import PluginLoadError
    
    logger = logging.getLogger(__name__)
    
    class PluginManager:
        def __init__(self, client: HTTPClient):
            """Khởi tạo Bộ quản lý Plugin với một HTTPClient dùng chung."""
            self.client = client
            # Lưu trữ các Class của Plugin đã được nạp: {plugin_id: PluginClass}
            self._plugins: Dict[str, Type[BaseSource]] = {}
            # Lưu trữ metadata chi tiết của từng plugin phục vụ tra cứu
            self._manifests: Dict[str, dict] = {}
            # Định vị đường dẫn tuyệt đối đến thư mục chứa file này
            self.plugins_dir = os.path.dirname(os.path.abspath(__file__))
    
        def discover_and_load_plugins(self) -> None:
            """Quét tự động tất cả các thư mục con để nạp các plugin hợp lệ."""
            logger.info("Hệ thống: Bắt đầu quét và nạp động các mô-đun Plugin...")
            
            # Lặp qua tất cả thực thể trong thư mục plugins/
            for item in os.listdir(self.plugins_dir):
                item_path = os.path.join(self.plugins_dir, item)
                
                # Chỉ xử lý nếu là thư mục, bỏ qua thư mục cốt lõi 'base' và thư mục ẩn (__pycache__)
                if not os.path.isdir(item_path) or item == "base" or item.startswith("__"):
                    continue
                    
                manifest_path = os.path.join(item_path, "manifest.json")
                if not os.path.exists(manifest_path):
                    logger.warning(f"Bỏ qua thư mục '{item}': Không tìm thấy tệp manifest.json")
                    continue
    
                try:
                    # 1. Đọc nội dung tệp cấu hình manifest.json
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        manifest = json.load(f)
    
                    plugin_id = manifest.get("plugin_id", item)
                    plugin_name = manifest.get("name", item)
                    entry_point = manifest.get("entry_point") # Cấu trúc mẫu: "source.TruyenFullSource"
    
                    # 2. Kiểm tra trạng thái kích hoạt của plugin
                    if not manifest.get("enabled", True):
                        logger.info(f"Plugin '{plugin_name}' [{plugin_id}] đang TẮT. Bỏ qua.")
                        continue
    
                    if not entry_point:
                        raise PluginLoadError(f"Thiếu thuộc tính 'entry_point' trong cấu hình.")
    
                    # 3. Phân tách đường dẫn tệp mã nguồn và tên Class xử lý chính
                    # Ví dụ: "source.TruyenFullSource" -> module_rel_path="source", class_name="TruyenFullSource"
                    module_rel_path, class_name = entry_point.rsplit(".", 1)
                    
                    # Tạo đường dẫn import tuyệt đối cho Python: "plugins.truyenfull.source"
                    full_module_path = f"plugins.{plugin_id}.{module_rel_path}"
                    
                    # 4. Thực hiện nạp động Module vào bộ nhớ hệ thống
                    module = importlib.import_module(full_module_path)
                    plugin_class = getattr(module, class_name)
    
                    # 5. Ràng buộc bảo mật: Kiểm tra Class nạp lên có kế thừa từ BaseSource không
                    if not issubclass(plugin_class, BaseSource):
                        raise PluginLoadError(f"Lớp '{class_name}' bắt buộc phải kế thừa từ lớp trừu tượng 'BaseSource'.")
    
                    # 6. Đăng ký plugin thành công vào bộ nhớ lưu trữ
                    self._plugins[plugin_id] = plugin_class
                    self._manifests[plugin_id] = manifest
                    logger.info(f" Thống kê: Đã kích hoạt thành công Plugin [{plugin_id}] phiên bản v{manifest.get('version', '1.0.0')}")
    
                except Exception as e:
                    logger.error(f"❌ Thất bại khi nạp plugin tại thư mục '{item}': {e}")
                    continue
    
        def get_source_instance(self, plugin_id: str) -> BaseSource:
            """Khởi tạo và trả về một Instance (thực thể) chạy cụ thể của Plugin."""
            if plugin_id not in self._plugins:
                raise PluginLoadError(f"Không tìm thấy hoặc chưa kích hoạt plugin có mã ID: '{plugin_id}'")
                
            plugin_class = self._plugins[plugin_id]
            # Khởi tạo instance và truyền trực tiếp HTTPClient dùng chung vào hàm tạo
            return plugin_class(client=self.client)
    
        def get_manifest(self, plugin_id: str) -> dict | None:
            """Lấy thông tin cấu hình chi tiết của một plugin qua mã ID."""
            return self._manifests.get(plugin_id)
    
        @property
        def available_plugins(self) -> List[str]:
            """Trả về danh sách tất cả các ID Plugin đang sẵn sàng hoạt động."""
            return list(self._plugins.keys())
    

Hãy thận trọng khi sử dụng mã.

* * *

**💡 Ví dụ cấu hình manifest.json của tangthuvien để khớp luồng chạy**

Để `PluginManager` nhận diện đúng, file `plugins/tangthuvien/manifest.json` của bạn chỉ cần khai báo chuẩn định dạng tương tự như sau:

json
    
    
    {
      "plugin_id": "tangthuvien",
      "name": "Tàng Thư Viện Scraper",
      "version": "1.0.0",
      "entry_point": "source.TangThuVienSource",
      "enabled": true
    }
    

Hãy thận trọng khi sử dụng mã.

Nếu bạn cần viết tiếp khung xử lý logic cho file **plugins/tangthuvien/source.py** dựa trên kiến trúc nạp động này, hãy cho tôi biết nhé!

### code chạy thử

Dưới đây là mã nguồn file chạy thử nghiệm độc lập **test_plugins.py** đặt tại thư mục gốc của dự án.

Để bạn có thể chạy thử ngay cả khi chưa viết xong code thực tế cho trang Tàng Thư Viện, đoạn code này sẽ tự động **tạo nhanh một cấu trúc Plugin giả lập (Mock Plugin)** cho `tangthuvien` ngay trong bộ nhớ, giúp bạn kiểm tra tính đúng đắn của cơ chế quét và nạp động của `PluginManager`.

* * *

**📄 test_plugins.py (Đặt tại thư mục gốc)**

python
    
    
    import os
    import json
    import shutil
    import logging
    import sys
    from plugins.base.http_client import HTTPClient
    from plugins.plugin_manager import PluginManager
    
    # Cấu hình log để hiện thị chi tiết luồng quét plugin ra màn hình
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    logger = logging.getLogger(__name__)
    
    def create_mock_tangthuvien_plugin():
        """Tạo nhanh file manifest và code giả lập cho tangthuvien để phục vụ test."""
        plugin_dir = os.path.join("plugins", "tangthuvien")
        os.makedirs(plugin_dir, exist_ok=True)
        
        # 1. Tạo file manifest.json cho Tàng Thư Viện
        manifest = {
            "plugin_id": "tangthuvien",
            "name": "Tàng Thư Viện Mock Scraper",
            "version": "1.0.5",
            "entry_point": "source.TangThuVienSource",
            "enabled": True
        }
        with open(os.path.join(plugin_dir, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=4, ensure_ascii=False)
            
        # 2. Tạo file source.py chứa Class kế thừa đúng chuẩn BaseSource
        source_code = """from plugins.base.base_source import BaseSource
    
    class TangThuVienSource(BaseSource):
        def crawl_novel(self, novel_slug: str) -> dict:
            print(f"[TangThuVien] Đang cào dữ liệu giả lập cho slug: {novel_slug}")
            return {
                "title": "Truyện Giả Lập Tàng Thư Viện",
                "author": "Tác Giả Ẩn Danh",
                "genres": ["Tiên Hiệp", "Huyền Huyễn"],
                "description": "Nội dung cào thử nghiệm từ hệ thống nạp động."
            }
    """
        with open(os.path.join(plugin_dir, "source.py"), "w", encoding="utf-8") as f:
            f.write(source_code)
    
    def main():
        # Bước 1: Tạo môi trường test (Sinh dữ liệu giả lập cho tangthuvien)
        # LƯU Ý: Nếu bạn đã viết file thật trong thư mục này rồi, bạn có thể comment dòng dưới lại.
        create_mock_tangthuvien_plugin()
        
        # Bước 2: Khởi tạo HTTPClient dùng chung
        client = HTTPClient(delay_range=(1.0, 2.0))
        
        # Bước 3: Khởi tạo PluginManager và quét hệ thống
        manager = PluginManager(client=client)
        manager.discover_and_load_plugins()
        
        print("\n" + "="*50)
        print("🧪 KẾT QUẢ KIỂM TRA HỆ THỐNG PLUGIN DYNAMIC")
        print("="*50)
        
        # Kiểm tra danh sách các plugin quét được
        active_plugins = manager.available_plugins
        print(f"[+] Các mã Plugin được kích hoạt trong hệ thống: {active_plugins}")
        
        # Bước 4: Chạy thử nghiệm gọi động từng plugin
        for plugin_id in active_plugins:
            print(f"\n--- Thử nghiệm gọi máy cào: {plugin_id.upper()} ---")
            try:
                # Lấy thông tin cấu hình từ manifest
                manifest_info = manager.get_manifest(plugin_id)
                print(f"| Tên Plugin: {manifest_info.get('name')}")
                print(f"| Phiên bản: {manifest_info.get('version')}")
                
                # Khởi tạo thực thể chạy động mà KHÔNG CẦN import cứng đầu file
                scraper_instance = manager.get_source_instance(plugin_id)
                
                # Tiến hành gọi hàm cào thử nghiệm
                result = scraper_instance.crawl_novel("test-slug-truyen")
                
                print(f"| Kết quả trả về thành công:")
                print(f"|   -> Tiêu đề: {result.get('title')}")
                print(f"|   -> Tác giả: {result.get('author')}")
                
            except Exception as e:
                print(f"❌ Lỗi khi test plugin [{plugin_id}]: {e}")
                
        print("\n" + "="*50)
        
        # Đóng client giải phóng tài nguyên
        client.close()
    
    if __name__ == "__main__":
        main()
    

Hãy thận trọng khi sử dụng mã.

* * *

**🚀 Hướng dẫn chạy và kết quả mong đợi**

Bạn mở Terminal tại thư mục gốc của dự án và chạy câu lệnh:

bash
    
    
    python test_plugins.py
    

Hãy thận trọng khi sử dụng mã.

**Màn hình sẽ log ra luồng xử lý động cực kỳ đẹp mắt:**

text
    
    
    2026-07-14 15:25:00 [INFO] Hệ thống: Bắt đầu quét và nạp động các mô-đun Plugin...
    2026-07-14 15:25:00 [INFO]  Thống kê: Đã kích hoạt thành công Plugin [truyenfull] phiên bản v1.0.0
    2026-07-14 15:25:00 [INFO]  Thống kê: Đã kích hoạt thành công Plugin [tangthuvien] phiên bản v1.0.5
    
    ==================================================
    🧪 KẾT QUẢ KIỂM TRA HỆ THỐNG PLUGIN DYNAMIC
    ==================================================
    [+] Các mã Plugin được kích hoạt trong hệ thống: ['truyenfull', 'tangthuvien']
    
    --- Thử nghiệm gọi máy cào: TRUYENFULL ---
    | Tên Plugin: TruyenFull Scraper
    | Phiên bản: 1.0.0
    [TruyenFull] Bắt đầu xử lý: https://truyenfull.io
    ...
    
    --- Thử nghiệm gọi máy cào: TANGTHUVIEN ---
    | Tên Plugin: Tàng Thư Viện Mock Scraper
    | Phiên bản: 1.0.5
    [TangThuVien] Đang cào dữ liệu giả lập cho slug: test-slug-truyen
    | Kết quả trả về thành công:
    |   -> Tiêu đề: Truyện Giả Lập Tàng Thư Viện
    |   -> Tác giả: Tác Giả Ẩn Danh
    ==================================================
    

Hãy thận trọng khi sử dụng mã.

Tiếp theo, bạn có muốn tôi hỗ trợ viết tiếp cấu trúc file **plugins/tangthuvien/parser.py** thật để bóc tách các thẻ HTML đặc thù của trang Tàng Thư Viện không?

