Để hoàn thiện kiến trúc 3 tầng (3-Tier Architecture), chúng ta sẽ triển khai **Presentation Tier (Tầng hiển thị)**. Tầng này đóng vai trò giao diện (định dạng dòng lệnh CLI trực quan, có menu điều hướng) để người dùng có thể **đọc truyện trực tiếp từ cơ sở dữ liệu** đã cào về, hoàn toàn không tương tác với các câu lệnh SQL hay file Scraper.

Chúng ta sẽ tạo một bộ quản lý hiển thị bằng cách gọi dữ liệu thông qua các `Repository` ở tầng Data Tier.

* * *

💻 Triển khai Presentation Tier

**File:** `presentation/cli_viewer.py`

python
    
    
    import os
    import sys
    # Đảm bảo Python tìm thấy các thư mục root nếu chạy script từ các thư mục con
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from database.story_repository import StoryRepository
    from database.chapter_repository import ChapterRepository
    
    class CLIViewer:
        def __init__(self):
            self.story_repo = StoryRepository()
            self.chapter_repo = ChapterRepository()
    
        def clear_screen(self):
            """Xóa màn hình console để trải nghiệm đọc mượt mà hơn"""
            os.system('cls' if os.name == 'nt' else 'clear')
    
        def show_main_menu(self):
            """Menu chính hiển thị danh sách truyện có trong máy"""
            while True:
                self.clear_screen()
                print("=======================================")
                print("       📚 THƯ VIỆN TRUYỆN OFFLINE      ")
                print("=======================================")
                
                # Lấy toàn bộ truyện từ Database qua Repository
                # (Giả định bạn đã thêm hàm get_all_stories vào StoryRepository)
                stories = self.story_repo.get_all_stories() 
                
                if not stories:
                    print("[!] Chưa có truyện nào trong cơ sở dữ liệu.")
                    print("[*] Hãy chạy tính năng cào truyện trước.")
                    print("---------------------------------------")
                    print("0. Thoát")
                    choice = input("\nNhập lựa chọn của bạn: ").strip()
                    if choice == "0": break
                    continue
    
                for idx, story in enumerate(stories, start=1):
                    print(f"{idx}. {story.title} [Tác giả: {story.author}] - Nguồn: {story.source}")
                
                print("---------------------------------------")
                print("0. Thoát ứng dụng")
                
                choice = input("\nChọn số để xem chi tiết truyện (hoặc 0 để thoát): ").strip()
                
                if choice == "0":
                    print("Cảm ơn bạn đã sử dụng hệ thống!")
                    break
                    
                if choice.isdigit() and 1 <= int(choice) <= len(stories):
                    selected_story = stories[int(choice) - 1]
                    self.show_story_detail(selected_story)
                else:
                    input("[!] Lựa chọn không hợp lệ. Nhấn Enter để thử lại...")
    
        def show_story_detail(self, story):
            """Hiển thị danh sách chương của bộ truyện được chọn"""
            while True:
                self.clear_screen()
                print(f"=======================================")
                print(f"📖 TRUYỆN: {story.title.upper()}")
                print(f"✍️ Tác giả: {story.author}")
                print(f"🌐 Nguồn cào: {story.source}")
                print(f"=======================================")
                
                # Gọi tầng Data Tier để lấy toàn bộ chương của truyện này
                chapters = self.chapter_repo.get_chapters_by_story(story.id)
                
                if not chapters:
                    print("[!] Bộ truyện này chưa có nội dung chương nào.")
                    input("\nNhấn Enter để quay lại menu chính...")
                    break
    
                print(f"[+] Tìm thấy {len(chapters)} chương trong máy:")
                for idx, ch in enumerate(chapters, start=1):
                    print(f"  {idx}. {ch.title}")
                    
                print("---------------------------------------")
                print("0. Quay lại Thư viện")
                
                choice = input("\nChọn số để ĐỌC CHƯƠNG (hoặc 0 để quay lại): ").strip()
                
                if choice == "0":
                    break
                    
                if choice.isdigit() and 1 <= int(choice) <= len(chapters):
                    selected_chapter = chapters[int(choice) - 1]
                    self.read_chapter(selected_chapter, chapters, int(choice) - 1)
                else:
                    input("[!] Lựa chọn không hợp lệ. Nhấn Enter để thử lại...")
    
        def read_chapter(self, current_chapter, chapters_list, current_index):
            """Giao diện đọc nội dung chương truyện kèm tính năng chuyển chương nhanh"""
            while True:
                self.clear_screen()
                print(f"--- {current_chapter.title.upper()} ---")
                print("-------------------------------------------------------------------\n")
                
                # Hiển thị nội dung chữ đã được làm sạch từ trước
                print(current_chapter.content)
                
                print("\n-------------------------------------------------------------------")
                
                # Xử lý điều hướng Trước / Sau
                has_prev = current_index > 0
                has_next = current_index < len(chapters_list) - 1
                
                nav_text = ""
                if has_prev: nav_text += "[P] Chương trước  |  "
                nav_text += "[B] Quay lại mục lục"
                if has_next: nav_text += "  |  [N] Chương sau"
                print(nav_text)
                
                action = input("\nNhập lệnh (P/B/N): ").strip().upper()
                
                if action == 'B':
                    break
                elif action == 'P' and has_prev:
                    current_index -= 1
                    current_chapter = chapters_list[current_index]
                elif action == 'N' and has_next:
                    current_index += 1
                    current_chapter = chapters_list[current_index]
    

Hãy thận trọng khi sử dụng mã.

* * *

⚙️ Cập nhật bổ sung cho StoryRepository (Data Tier)

Để Tầng hiển thị phía trên hoạt động được, bạn cần bổ sung hàm lấy toàn bộ danh sách truyện `get_all_stories` bằng SQL thuần vào file `database/story_repository.py` đã viết ở bước trước:

python
    
    
        def get_all_stories(self) -> List[StoryModel]:
            """Lấy toàn bộ danh sách truyện trong database để hiển thị lên Menu"""
            query = "SELECT id, title, url, author, source, status FROM stories ORDER BY id DESC"
            stories = []
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                for row in cursor.fetchall():
                    stories.append(StoryModel(
                        id=row[0],
                        title=row[1],
                        url=row[2],
                        author=row[3],
                        source=row[4],
                        status=row[5]
                    ))
            return stories
    

Hãy thận trọng khi sử dụng mã.

* * *

🎛️ Tích hợp toàn bộ hệ thống vào File chạy chính (`main.py`)

Bây giờ chúng ta sẽ cập nhật `main.py` đóng vai trò là bảng điều khiển tối cao (Presentation Tier), cho phép người dùng lựa chọn giữa việc **1\. Cào truyện mới** hoặc **2\. Đọc truyện sẵn có**.

python
    
    
    from scrapers.source_a import SourceAScraper
    from core.crawler_engine import CrawlerEngine
    from presentation.cli_viewer import CLIViewer
    
    def run_crawler_flow():
        """Luồng xử lý tác vụ cào truyện"""
        print("\n--- HỆ THỐNG CÀO TRUYỆN ĐA NGUỒN ---")
        print("1. Cào từ Nguồn A (TruyenFull)")
        print("2. Cào từ Nguồn B (Cấu hình sau)")
        source_choice = input("Chọn nguồn cào (1-2): ").strip()
        
        if source_choice == "1":
            scraper = SourceAScraper()
            source_name = "TruyenFull"
        else:
            print("[!] Nguồn chưa được hỗ trợ!")
            return
    
        story_url = input("Nhập URL truyện chữ cần cào: ").strip()
        if not story_url:
            print("[!] URL trống!")
            return
    
        # Kích hoạt Logic Tier
        engine = CrawlerEngine(scraper, source_name)
        engine.execute(story_url)
        input("\nBấm Enter để quay lại trang chủ...")
    
    def main():
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("=======================================")
            print("    CRAWLER FRAMEWORK 3-TIER SYSTEM    ")
            print("=======================================")
            print("1. Kích hoạt Trình cào truyện (Crawl truyện mới)")
            print("2. Vào Thư viện đọc truyện (Đọc từ Database)")
            print("0. Thoát chương trình")
            print("=======================================")
            
            choice = input("Nhập lựa chọn của bạn (0-2): ").strip()
            
            if choice == "1":
                run_crawler_flow()
            elif choice == "2":
                viewer = CLIViewer()
                viewer.show_main_menu()
            elif choice == "0":
                print("Hẹn gặp lại!")
                break
            else:
                input("[!] Lựa chọn sai. Nhấn Enter để chọn lại...")
    
    if __name__ == "__main__":
        import os
        main()
    

Hãy thận trọng khi sử dụng mã.

* * *

🎯 Điểm cốt lõi về kiến trúc sau khi hoàn thiện:

  1. **User** tương tác với giao diện CLI (`main.py` / `CLIViewer`).
  2. Nếu người dùng chọn **Đọc truyện** , `CLIViewer` yêu cầu dữ liệu từ `StoryRepository` / `ChapterRepository` mà **không hề biết** dữ liệu đó lấy từ file SQLite, PostgreSQL hay file Text (Tính đóng gói dữ liệu của Tầng 1).
  3. Nếu người dùng chọn **Cào truyện** , giao diện sẽ ra lệnh cho `CrawlerEngine` (Tầng 2) chạy. Engine tự đi cào, tự đổ dữ liệu ngược lại Tầng 1, giao diện chỉ nhận nhiệm vụ in thông báo hoàn thành ra màn hình.



Nếu bạn muốn nâng cấp hệ thống này lên một bước cao hơn, bạn có muốn tìm hiểu cách tích hợp **Tính năng xuất truyện thành file EPUB/PDF để đọc trên điện thoại** (thuộc Logic Tier), hay **Cơ chế Logs lưu lại lịch sử các chương bị lỗi khi cào** không?

