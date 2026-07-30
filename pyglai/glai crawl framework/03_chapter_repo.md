Để xử lý nội dung chương của truyện chữ từ các nguồn như TruyenFull hay Webnovel, thách thức lớn nhất chính là **dung lượng văn bản lớn** , **ký tự đặc biệt (emoji, font lạ)** , và **lỗi xuống dòng (`\n`, `\r\n`, `<p>`, `<br>`)**.

Dưới đây là cách thiết kế chi tiết **ChapterModel** , **ChapterRepository** sử dụng SQL thuần và giải pháp làm sạch dữ liệu trước khi lưu vào DB.

* * *

1\. Nâng cấp Model cho Chương (Chapter Model)

Chúng ta bổ sung thêm một hàm xử lý chuỗi trực tiếp trong Model để tự động làm sạch văn bản (loại bỏ quảng cáo rác, chuẩn hóa dấu xuống dòng) trước khi lưu vào cơ sở dữ liệu.

**File:** `database/models.py`

python
    
    
    import re
    from dataclasses import dataclass
    from typing import Optional
    
    @dataclass
    class ChapterModel:
        id: Optional[int]
        story_id: int
        chapter_number: float  # Để float đề phòng chương 10.5, 100.1
        title: str
        content: str
    
        def clean_content(self) -> str:
            """Làm sạch nội dung truyện chữ trước khi lưu vào DB"""
            if not self.content:
                return ""
                
            text = self.content
            # 1. Khử các đoạn text rác/quảng cáo thường chèn giữa truyện
            trash_words = [
                r"Bạn đang đọc truyện tại TruyenFull.*",
                r"Chúc bạn đọc truyện vui vẻ.*",
                r"Truy cập.*để đọc chương mới nhất.*"
            ]
            for pattern in trash_words:
                text = re.sub(pattern, "", text, flags=re.IGNORECASE)
                
            # 2. Chuẩn hóa xuống dòng (thay thế nhiều dấu xuống dòng liên tiếp bằng 2 dấu)
            text = re.sub(r'[\r\n]+', '\n\n', text)
            
            return text.strip()
    

Hãy thận trọng khi sử dụng mã.

* * *

2\. Thiết kế ChapterRepository (SQL thuần)

Khi lưu nội dung văn bản lớn (Text/LongText), chúng ta cần dùng cơ chế **Parameterized Query** (`?` trong SQLite hoặc `%s` trong PostgreSQL) để tránh lỗi cú pháp do ký tự đặc biệt (như dấu nháy đơn `'`, nháy kép `"`) và chặn hoàn toàn lỗi bảo mật SQL Injection.

**File:** `database/chapter_repository.py`

python
    
    
    import sqlite3
    from typing import List, Optional
    from database.models import ChapterModel
    
    class ChapterRepository:
        def __init__(self, db_path="crawler.db"):
            self.db_path = db_path
    
        def _get_conn(self):
            # Thiết kế thực tế: Thêm timeout đề phòng ghi đa luồng bị khóa DB (Database Locked)
            return sqlite3.connect(self.db_path, timeout=30)
    
        def insert_chapter(self, chapter: ChapterModel) -> bool:
            """Lưu một chương truyện bằng SQL thuần (đã làm sạch nội dung)"""
            query = """
            INSERT INTO chapters (story_id, chapter_number, title, content)
            VALUES (?, ?, ?, ?)
            """
            # Gọi hàm làm sạch nội dung từ Model
            cleaned_text = chapter.clean_content()
            
            try:
                with self._get_conn() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, (
                        chapter.story_id, 
                        chapter.chapter_number, 
                        chapter.title, 
                        cleaned_text
                    ))
                    conn.commit()
                    return True
            except sqlite3.Error as e:
                print(f"[-] Lỗi SQL khi lưu chương {chapter.chapter_number}: {e}")
                return False
    
        def check_chapter_exists(self, story_id: int, chapter_number: float) -> bool:
            """Kiểm tra chương đã được cào chưa (để bỏ qua nếu cào lại/cào nối tiếp)"""
            query = "SELECT 1 FROM chapters WHERE story_id = ? AND chapter_number = ? LIMIT 1"
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (story_id, chapter_number))
                return cursor.fetchone() is not None
    
        def get_chapters_by_story(self, story_id: int) -> List[ChapterModel]:
            """Lấy toàn bộ danh sách chương của 1 bộ truyện (dùng cho tầng hiển thị)"""
            query = "SELECT id, story_id, chapter_number, title, content FROM chapters WHERE story_id = ? ORDER BY chapter_number ASC"
            chapters = []
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (story_id,))
                for row in cursor.fetchall():
                    chapters.append(ChapterModel(
                        id=row[0],
                        story_id=row[1],
                        chapter_number=row[2],
                        title=row[3],
                        content=row[4]
                    ))
            return chapters
    

Hãy thận trọng khi sử dụng mã.

* * *

3\. Tích hợp Đa luồng (Multi-threading) vào Tầng Logic

Đối với truyện chữ có hàng nghìn chương, nếu cào tuần tự từng chương sẽ rất chậm. Chúng ta sẽ sử dụng `ThreadPoolExecutor` tại tầng **Logic** để cào song song nhiều chương.

Khi dùng đa luồng với SQL thuần, hãy lưu ý: **Mỗi luồng phải tự tạo một kết nối DB riêng** (đó là lý do hàm `_get_conn()` luôn trả về một kết nối mới thay vì dùng chung một biến `self.conn`).

**File:** `core/crawler_engine.py` (Phiên bản nâng cấp)

python
    
    
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from database.story_repository import StoryRepository
    from database.chapter_repository import ChapterRepository
    from database.models import ChapterModel
    
    class CrawlerEngine:
        def __init__(self, scraper, source_name):
            self.scraper = scraper
            self.source_name = source_name
            self.story_repo = StoryRepository()
            self.chapter_repo = ChapterRepository()
    
        def _crawl_single_chapter(self, story_id: int, chapter_idx: float, chapter_info: dict):
            """Hàm xử lý cho một luồng (Thread) đơn lẻ"""
            # Kiểm tra trùng lặp trước khi cào để tiết kiệm băng thông
            if self.chapter_repo.check_chapter_exists(story_id, chapter_idx):
                print(f"[~] Chương {chapter_idx} đã tồn tại trong DB. Bỏ qua.")
                return
    
            html = self.scraper.fetch_html(chapter_info['url'])
            if not html:
                return
    
            raw_content = self.scraper.extract_chapter_content(html)
            
            # Đóng gói vào Model
            chapter_model = ChapterModel(
                id=None,
                story_id=story_id,
                chapter_number=chapter_idx,
                title=chapter_info['title'],
                content=raw_content
            )
            
            # Đẩy qua Repo lưu vào DB
            if self.chapter_repo.insert_chapter(chapter_model):
                print(f"[+] Đã cào xong & lưu: Chương {chapter_idx}")
    
        def execute(self, story_url):
            print(f"[*] Khởi động engine cào đa luồng từ: {self.source_name}")
            
            # 1. Cào thông tin truyện gốc
            story_html = self.scraper.fetch_html(story_url)
            if not story_html: return
            
            story_model = self.scraper.extract_story_info(story_html, story_url)
            story_id = self.story_repo.insert_story(story_model)
            
            # 2. Lấy danh sách chương
            chapters_list = self.scraper.extract_chapters_list(story_html)
            print(f"[+] Tìm thấy {len(chapters_list)} chương cần xử lý.")
    
            # 3. Kích hoạt Đa luồng (Ví dụ: chạy tối đa 5 luồng cùng lúc để tránh bị block IP)
            max_workers = 5
            print(f"[*] Đang cào với {max_workers} luồng song song...")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for idx, ch_info in enumerate(chapters_list, start=1):
                    # Gửi tác vụ vào hồ bơi luồng (thread pool)
                    f = executor.submit(self._crawl_single_chapter, story_id, float(idx), ch_info)
                    futures.append(f)
                
                # Chờ tất cả các luồng hoàn thành
                for future in as_completed(futures):
                    pass
                    
            print("[*] Quá trình cào đa luồng hoàn tất thành công!")
    

Hãy thận trọng khi sử dụng mã.

* * *

💡 Đánh giá mô hình sau khi nâng cấp:

  * **Tầng 1 (Data):** Độc lập tuyệt đối. `ChapterRepository` chỉ quan tâm nhận đúng Object và thực thi câu lệnh SQL một cách an toàn.
  * **Tầng 2 (Logic):** Tập trung tối đa vào tốc độ nhờ đa luồng (`ThreadPoolExecutor`) và độ chính xác nhờ hàm `clean_content()`.
  * **Tính mở rộng:** Nếu mai này TruyenFull đổi giao diện hay bạn muốn thêm Webnovel, bạn **chỉ cần viết thêm 1 file Scraper mới** thừa kế từ `BaseScraper`. Toàn bộ hệ thống Model, Repo, Engine giữ nguyên 100%.



Tiếp theo, bạn có muốn tối ưu thêm phần **vượt Cloudflare / Chống chặn IP** (vì Webnovel và TruyenFull chặn bot rất gắt), hay bạn muốn triển khai thử phần **giao diện hiển thị truyện (Presentation Tier) đọc trực tiếp từ DB** ra không?

