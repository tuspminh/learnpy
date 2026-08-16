Để hiện thực hóa tính năng trích xuất truyện từ Database thành cấu trúc thư mục (Folder) chứa file thông tin và các file chương chữ, chúng ta sẽ viết thêm một module chuyên trách tại tầng **Logic Tier** [3] (hoặc tạo một Export Service chuyên biệt).

Tính năng này sẽ đọc dữ liệu thông qua các `Repository` đã có ở tầng Data Tier, sau đó ghi ra hệ thống tệp tin (File System).

* * *

📁 Cấu trúc thư mục đầu ra mong muốn

Khi chạy tính năng này, hệ thống sẽ tự động tạo ra một thư mục có cấu trúc như sau để người dùng dễ dàng lưu trữ hoặc sao chép vào máy đọc truyện:

text
    
    
    truyen_xuat_ban/
    └── [Tên Truyện] - [Tác giả]/
        ├── description.txt       # Chứa thông tin giới thiệu truyện, tác giả, nguồn
        ├── Chuong_0001.txt       # Nội dung chương 1
        ├── Chuong_0002.txt       # Nội dung chương 2
        └── ...
    

Hãy thận trọng khi sử dụng mã.

* * *

⚙️ 1. Triển khai Logic Tier: `ExporterEngine`

Chúng ta tạo một file mới có nhiệm vụ xử lý logic tạo folder, làm sạch tên thư mục (tránh ký tự đặc biệt của hệ điều hành như `\ / : * ? " < > |`) và ghi dữ liệu ra các file `.txt`.

**File:** `core/exporter_engine.py`

python
    
    
    import os
    import re
    from database.story_repository import StoryRepository
    from database.chapter_repository import ChapterRepository
    from database.models import StoryModel
    
    class ExporterEngine:
        def __init__(self, output_dir="truyen_xuat_ban"):
            self.story_repo = StoryRepository()
            self.chapter_repo = ChapterRepository()
            self.output_dir = output_dir
    
        def _sanitize_filename(self, filename: str) -> str:
            """Loại bỏ các ký tự không hợp lệ trong tên file/folder của Windows/Linux"""
            return re.sub(r'[\\/*?:"<>|]', "", filename).strip()
    
        def export_story(self, story_id: int) -> bool:
            """Đọc từ DB và xuất toàn bộ bộ truyện thành folder"""
            # 1. Lấy thông tin truyện từ DB thông qua StoryRepository
            # (Giả định bạn bổ sung hàm find_by_id hoặc dùng hàm thích hợp trong Repo)
            story = self.get_story_by_id_from_repo(story_id) 
            if not story:
                print("[-] Không tìm thấy truyện với ID này trong Database.")
                return False
    
            # 2. Tạo tên thư mục cha hợp lệ
            folder_name = f"{story.title} - {story.author}"
            safe_folder_name = self._sanitize_filename(folder_name)
            story_folder_path = os.path.join(self.output_dir, safe_folder_name)
    
            # Tạo folder (nếu chưa có)
            os.makedirs(story_folder_path, exist_ok=True)
    
            # 3. Tạo file description.txt
            desc_path = os.path.join(story_folder_path, "description.txt")
            with open(desc_path, "w", encoding="utf-8") as f:
                f.write(f"=========================================\n")
                f.write(f"THÔNG TIN TRUYỆN\n")
                f.write(f"=========================================\n")
                f.write(f"Tên truyện: {story.title}\n")
                f.write(f"Tác giả: {story.author}\n")
                f.write(f"Nguồn cào: {story.source}\n")
                f.write(f"Trạng thái: {story.status}\n")
                f.write(f"URL gốc: {story.url}\n")
                f.write(f"=========================================\n")
                f.write(f"\n[Mô tả/Giới thiệu truyện]:\n")
                f.write(f"(Bạn có thể cào thêm phần tóm tắt truyện từ website để lưu vào đây)\n")
    
            print(f"[+] Đã tạo file thông tin truyện: {desc_path}")
    
            # 4. Lấy danh sách chương từ DB thông qua ChapterRepository
            chapters = self.chapter_repo.get_chapters_by_story(story_id)
            if not chapters:
                print("[~] Truyện này hiện chưa có nội dung chương nào để xuất.")
                return True
    
            # 5. Xuất từng chương thành file .txt riêng biệt
            print(f"[*] Đang xuất {len(chapters)} chương ra file...")
            for ch in chapters:
                # Format số chương (ví dụ chương 1 thành Chuong_0001 để sắp xếp file theo thứ tự tốt hơn)
                # Định dạng hỗ trợ cả chương lẻ như 10.5 thành Chuong_0010.5
                ch_num_str = f"{ch.chapter_number:04.1f}" if ch.chapter_number % 1 != 0 else f"{int(ch.chapter_number):04d}"
                
                safe_ch_title = self._sanitize_filename(ch.title)
                file_name = f"Chuong_{ch_num_str} - {safe_ch_title}.txt"
                ch_file_path = os.path.join(story_folder_path, file_name)
    
                with open(ch_file_path, "w", encoding="utf-8") as f:
                    f.write(f"{ch.title.upper()}\n")
                    f.write("-" * 40 + "\n\n")
                    f.write(ch.content)
    
            print(f"[🌐] Xuất bản thành công! Thư mục lưu tại: {story_folder_path}")
            return True
    
        def get_story_by_id_from_repo(self, story_id: int) -> StoryModel:
            """Hàm bổ trợ để lấy truyện theo ID (bằng SQL thuần ẩn trong Repo)"""
            query = "SELECT id, title, url, author, source, status FROM stories WHERE id = ?"
            with self.story_repo._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (story_id,))
                row = cursor.fetchone()
                if row:
                    return StoryModel(id=row[0], title=row[1], url=row[2], author=row[3], source=row[4], status=row[5])
            return None
    

Hãy thận trọng khi sử dụng mã.

* * *

🎛️ 2. Cập nhật Presentation Tier: Thêm menu Xuất Bản

Chúng ta sẽ tích hợp tính năng này vào giao diện CLI bằng cách cho phép người dùng chọn một bộ truyện đang có trong Thư viện DB và ra lệnh trích xuất ra ổ đĩa máy tính.

**Cập nhật file:** `presentation/cli_viewer.py` (Bổ sung vào hàm `show_story_detail`)

Tìm đoạn menu hiển thị chi tiết của truyện trong file cũ của bạn, chỉnh sửa và thêm tính năng như sau:

python
    
    
        def show_story_detail(self, story):
            """Hiển thị danh sách chương của bộ truyện được chọn"""
            while True:
                self.clear_screen()
                print(f"=======================================")
                print(f"📖 TRUYỆN: {story.title.upper()}")
                print(f"✍️ Tác giả: {story.author}")
                print(f"=======================================")
                
                chapters = self.chapter_repo.get_chapters_by_story(story.id)
                print(f"[+] Trong DB đang lưu trữ: {len(chapters)} chương.")
                print("---------------------------------------")
                print("1. Đọc truyện trực tiếp trên màn hình (CLI)")
                print("2. TRÍCH XUẤT TRUYỆN RA FOLDER (.txt)") # Tính năng mới thêm vào
                print("0. Quay lại Thư viện")
                print("---------------------------------------")
                
                choice = input("\nNhập lựa chọn của bạn: ").strip()
                
                if choice == "0":
                    break
                    
                elif choice == "1":
                    # Nhảy vào luồng đọc chương cũ đã thiết kế
                    if not chapters:
                        input("[!] Chưa có chương nào để đọc. Nhấn Enter...")
                        continue
                    # Mặc định đọc từ chương đầu tiên (index 0)
                    self.read_chapter(chapters[0], chapters, 0)
                    
                elif choice == "2":
                    print("\n[*] Đang khởi tạo tiến trình trích xuất dữ liệu...")
                    from core.exporter_engine import ExporterEngine
                    exporter = ExporterEngine()
                    
                    # Gọi Logic Tier xử lý tác vụ ghi file
                    success = exporter.export_story(story.id)
                    if success:
                        input("\n[+] Trích xuất hoàn tất! Nhấn Enter để tiếp tục...")
                    else:
                        input("\n[-] Có lỗi xảy ra trong quá trình trích xuất. Nhấn Enter...")
                else:
                    input("[!] Lựa chọn không hợp lệ. Nhấn Enter để thử lại...")
    

Hãy thận trọng khi sử dụng mã.

* * *

💡 Đánh giá luồng dữ liệu 3-Tier sau tính năng này:

  1. **Tầng Presentation (`cli_viewer.py`):** Nhận lệnh xuất file từ phím bấm người dùng (`choice == "2"`), lấy ra ID truyện hiện tại rồi gửi xuống cho Tầng Logic. Giao diện hoàn toàn không làm việc với hàm `open()` hay tự ghi file.
  2. **Tầng Logic (`exporter_engine.py`):** Tiếp nhận ID từ Tầng 1, yêu cầu Tầng Data cung cấp thông tin thô (`StoryModel` & `ChapterModel`), tiến hành tính toán định dạng chuẩn hóa tên file, sau đó thực hiện ghi ra ổ cứng.
  3. **Tầng Data (`story_repository.py` / `chapter_repository.py`):** Đứng im thực thi câu lệnh SQL thuần để kéo dữ liệu từ file cơ sở dữ liệu lên nạp vào Model và trả ngược cho Tầng Logic.



Bây giờ framework của bạn đã có đủ: **Cào dữ liệu (Input) - > Lưu trữ và quản lý (Storage/DB) -> Hiển thị/Đọc (Viewer) -> Kết xuất dữ liệu (Output)**.

Để nâng cấp framework này lên mức phân tán chuyên nghiệp, bạn có muốn tìm hiểu cách chuyển đổi cơ sở dữ liệu từ **SQLite (File cục bộ) sang PostgreSQL (Server cơ sở dữ liệu độc lập)** mà không làm ảnh hưởng đến code của tầng Logic hay Presentation không?

