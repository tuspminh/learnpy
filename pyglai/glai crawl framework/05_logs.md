Để xây dựng cơ chế lưu log lỗi khi cào truyện đa luồng, chúng ta cần giải quyết hai vấn đề cốt lõi:

  1. **Ghi log không nghẽn luồng:** Khi chạy đa luồng (`ThreadPoolExecutor`), nếu nhiều luồng cùng ghi vào một file log một lúc sẽ gây ra hiện tượng xung đột (Race Condition) hoặc khóa file.

  2. **SQL thuần để lưu log:** Lưu nhật ký lỗi vào ngay một bảng trong Database để sau này có thể viết tính năng "Cào lại các chương lỗi" (Retry Mechanism) một cách tự động.



Dưới đây là cách tích hợp hệ thống Logging chuyên nghiệp vào Framework 3-tier hiện tại.

* * *

🏛️ 1. Cập nhật Data Tier: Tạo bảng Error Logs

Chúng ta cần một bảng để lưu: ID truyện, Số chương, URL bị lỗi, Lý do lỗi (Timeout, lỗi bóc tách HTML, hay lỗi DB) và Thời gian bị lỗi.

**Bổ sung vào file:** `database/db_manager.py` (Hàm `init_db`)

python
    
    
            query_logs = """
            CREATE TABLE IF NOT EXISTS crawler_error_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER,
                chapter_number REAL,
                chapter_url TEXT,
                error_message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'PENDING' -- PENDING: Chưa sửa, FIXED: Đã cào lại thành công
            );
            """
            # Thêm câu lệnh thực thi query_logs vào hàm init_db() của bạn
    

Hãy thận trọng khi sử dụng mã.

Tạo Log Repository riêng biệt

**File:** `database/log_repository.py`

python
    
    
    import sqlite3
    from typing import List
    
    class LogRepository:
        def __init__(self, db_path="crawler.db"):
            self.db_path = db_path
    
        def _get_conn(self):
            return sqlite3.connect(self.db_path, timeout=30)
    
        def insert_error_log(self, story_id: int, chapter_number: float, url: str, error_msg: str):
            """Ghi nhận lỗi vào DB bằng SQL thuần"""
            query = """
            INSERT INTO crawler_error_logs (story_id, chapter_number, chapter_url, error_message)
            VALUES (?, ?, ?, ?)
            """
            try:
                with self._get_conn() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, (story_id, chapter_number, url, error_msg))
                    conn.commit()
            except sqlite3.Error as e:
                print(f"[-] Không thể ghi log vào DB: {e}")
    
        def get_pending_errors(self) -> List[dict]:
            """Lấy danh sách các chương đang bị lỗi để chuẩn bị cào lại"""
            query = "SELECT id, story_id, chapter_number, chapter_url FROM crawler_error_logs WHERE status = 'PENDING'"
            with self._get_conn() as conn:
                conn.row_factory = sqlite3.Row # Để lấy dữ liệu dạng dict cho dễ đọc
                cursor = conn.cursor()
                cursor.execute(query)
                return [dict(row) for row in cursor.fetchall()]
    
        def update_log_status(self, log_id: int, status: str = 'FIXED'):
            """Cập nhật trạng thái sau khi đã cào lại thành công"""
            query = "UPDATE crawler_error_logs SET status = ? WHERE id = ?"
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (status, log_id))
                conn.commit()
    

Hãy thận trọng khi sử dụng mã.

* * *

⚙️ 2. Cập nhật Logic Tier: Sử dụng thư viện `logging` chuẩn kết hợp Repo

Trong môi trường đa luồng, thư viện `logging` tích hợp sẵn của Python là **Thread-safe** (an toàn cho đa luồng) khi ghi ra file văn bản. Chúng ta sẽ kết hợp ghi file `.log` và lưu vào DB.

**File:** `core/crawler_engine.py` (Phiên bản tích hợp cơ chế bắt lỗi)

python
    
    
    import logging
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from database.story_repository import StoryRepository
    from database.chapter_repository import ChapterRepository
    from database.log_repository import LogRepository
    from database.models import ChapterModel
    
    # Cấu hình ghi log ra file văn bản (Dùng chung cho toàn bộ luồng)
    logging.basicConfig(
        filename='crawler_errors.log',
        level=logging.ERROR,
        format='%(asctime)s - [%(levelname)s] - %(message)s',
        encoding='utf-8'
    )
    
    class CrawlerEngine:
        def __init__(self, scraper, source_name):
            self.scraper = scraper
            self.source_name = source_name
            self.story_repo = StoryRepository()
            self.chapter_repo = ChapterRepository()
            self.log_repo = LogRepository() # Tích hợp Repo Log
    
        def _crawl_single_chapter(self, story_id: int, chapter_idx: float, chapter_info: dict):
            if self.chapter_repo.check_chapter_exists(story_id, chapter_idx):
                return
    
            try:
                # Tình huống lỗi 1: Lỗi kết nối mạng / Timeout
                html = self.scraper.fetch_html(chapter_info['url'])
                if not html:
                    raise Exception("Không thể tải HTML (Có thể bị chặn IP hoặc URL chết)")
    
                # Tình huống lỗi 2: Lỗi bóc tách cấu hình (Website đổi cấu trúc HTML giữa chừng)
                raw_content = self.scraper.extract_chapter_content(html)
                if not raw_content or len(raw_content) < 100: # Truyện chữ mà quá ngắn là bất thường
                    raise Exception("Nội dung bóc tách quá ngắn hoặc trống (Lỗi HTML Parser)")
    
                chapter_model = ChapterModel(
                    id=None, story_id=story_id, chapter_number=chapter_idx,
                    title=chapter_info['title'], content=raw_content
                )
                
                # Tình huống lỗi 3: Lỗi ghi vào Cơ sở dữ liệu
                if not self.chapter_repo.insert_chapter(chapter_model):
                    raise Exception("Lỗi SQL thuần khi chèn dữ liệu vào bảng chapters")
                    
                print(f"[+] Thành công: Chương {chapter_idx}")
    
            except Exception as e:
                error_msg = str(e)
                print(f"[-] THẤT BẠI: Chương {chapter_idx}. Lý do: {error_msg}")
                
                # 1. Ghi vào file crawler_errors.log (An toàn đa luồng)
                logging.error(f"StoryID {story_id} | Chương {chapter_idx} | URL: {chapter_info['url']} | Lỗi: {error_msg}")
                
                # 2. Ghi vào Database để kích hoạt tính năng tự động cào lại sau này
                self.log_repo.insert_error_log(
                    story_id=story_id,
                    chapter_number=chapter_idx,
                    url=chapter_info['url'],
                    error_msg=error_msg
                )
    
        def execute(self, story_url):
            # ... (Giữ nguyên phần lấy story_info và danh sách chương như cũ) ...
            chapters_list = self.scraper.extract_chapters_list(story_html)
            story_id = self.story_repo.insert_story(story_model)
    
            max_workers = 5
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(self._crawl_single_chapter, story_id, float(idx), ch_info)
                    for idx, ch_info in enumerate(chapters_list, start=1)
                ]
                for future in as_completed(futures):
                    pass # Chờ các luồng chạy xong
                    
            print("\n[*] Tiến trình hoàn tất. Vui lòng kiểm tra file 'crawler_errors.log' hoặc menu hệ thống nếu có lỗi.")
    

Hãy thận trọng khi sử dụng mã.

* * *

🔄 3. Bonus: Tính năng tự động cào lại chương lỗi (Auto-Retry Logic)

Nhờ lưu log vào DB, chúng ta có thể dễ dàng viết thêm một hàm trong `CrawlerEngine` để quét các chương bị lỗi trước đó và cào lại, giúp người dùng không phải cào lại cả bộ truyện từ đầu.

python
    
    
        def retry_failed_chapters(self):
            """Quét và cào lại các chương nằm trong danh sách lỗi"""
            failed_list = self.log_repo.get_pending_errors()
            if not failed_list:
                print("[*] Tuyệt vời! Không có chương nào bị lỗi cần cào lại.")
                return
    
            print(f"[*] Tìm thấy {len(failed_list)} chương từng bị lỗi. Bắt đầu cào lại...")
            
            for item in failed_list:
                print(f" -> Thử lại Chương {item['chapter_number']} (URL: {item['chapter_url']})")
                
                html = self.scraper.fetch_html(item['chapter_url'])
                if html:
                    content = self.scraper.extract_chapter_content(html)
                    if content and len(content) > 100:
                        # Giả định lấy tạm tiêu đề cũ
                        chapter_model = ChapterModel(
                            id=None, story_id=item['story_id'], 
                            chapter_number=item['chapter_number'],
                            title=f"Chương {item['chapter_number']} (Cào lại)", content=content
                        )
                        if self.chapter_repo.insert_chapter(chapter_model):
                            print(f" [!] Sửa lỗi thành công chương {item['chapter_number']}!")
                            # Đổi trạng thái log thành FIXED để không quét lại nữa
                            self.log_repo.update_log_status(item['id'], 'FIXED')
                            continue
                print(f" [-] Thử lại chương {item['chapter_number']} vẫn thất bại.")
    

Hãy thận trọng khi sử dụng mã.

* * *

🎛️ 4. Cập nhật Presentation Tier (Giao diện CLI chính)

Bạn chỉ cần thêm một nút bấm ở menu chính tại file `main.py` để người dùng kích hoạt tính năng kiểm tra / cào lại lỗi này:

python
    
    
            print("=======================================")
            print("1. Kích hoạt Trình cào truyện")
            print("2. Vào Thư viện đọc truyện")
            print("3. Sửa lỗi & Cào lại các chương lỗi (Retry Logs)") # Thêm tính năng này
            print("0. Thoát chương trình")
            print("=======================================")
    

Hãy thận trọng khi sử dụng mã.

Khi người dùng chọn `3`, bạn chỉ cần gọi hàm `engine.retry_failed_chapters()` là xong.

Ý tưởng tiếp theo để hoàn thiện triệt để framework này là gì? Bạn có muốn cấu trúc **Cơ chế xoay tua Proxy (Proxy Rotator)** ở tầng Logic để xử lý triệt để nguyên nhân gây lỗi lớn nhất là **Bị website chặn IP / Bắt xác minh Cloudflare** không?

