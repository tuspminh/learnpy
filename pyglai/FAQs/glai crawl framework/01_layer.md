Để xây dựng một framework cào truyện từ nhiều nguồn (Crawl Framework) theo kiến trúc 3 tầng (3-Tier Architecture) bằng Python và SQL thuần, chúng ta cần tách biệt rõ ràng giữa dữ liệu, logic xử lý và giao diện điều khiển.

Dưới đây là hướng dẫn thiết kế chi tiết từng tầng và code mẫu triển khai.

* * *

🏛️ Tổng quan kiến trúc 3 Tầng (3-Tier Architecture)

  1. **Data Tier (Tầng dữ liệu):** Lưu trữ thông tin truyện, chương, và cấu hình các nguồn cào. Sử dụng SQLite hoặc PostgreSQL với SQL thuần (thư viện `sqlite3` hoặc `psycopg2`).
  2. **Logic Tier (Tầng xử lý):** Chứa các hàm cào dữ liệu (`requests`, `BeautifulSoup`), bóc tách dữ liệu theo từng nguồn (Strategy Pattern), và xử lý logic nghiệp vụ.
  3. **Presentation Tier (Tầng hiển thị/Điều khiển):** Giao diện dòng lệnh (CLI) hoặc Script điều hướng để người dùng chọn nguồn cào, nhập URL và kích hoạt hệ thống.



* * *

📁 Sơ đồ cấu trúc thư mục dự án

text
    
    
    comic_crawler/
    │
    ├── database/
    │   ├── __init__.py
    │   └── db_manager.py      # Tầng 1: Kết nối DB, chạy SQL thuần
    │
    ├── scrapers/
    │   ├── __init__.py
    │   ├── base_scraper.py    # Tầng 2: Lớp cơ sở (Abstract Class)
    │   ├── source_a.py        # Tầng 2: Cào nguồn A (Ví dụ: TruyenFull)
    │   └── source_b.py        # Tầng 2: Cào nguồn B (Ví dụ: Nettruyen)
    │
    ├── core/
    │   ├── __init__.py
    │   └── crawler_engine.py  # Tầng 2: Điều phối dòng chảy dữ liệu
    │
    ├── main.py                # Tầng 3: Giao diện CLI điều khiển
    └── requirements.txt
    

Hãy thận trọng khi sử dụng mã.

* * *

💻 Triển khai chi tiết từng tầng

1\. Data Tier (Tầng Dữ Liệu)

Tầng này chỉ làm việc với cơ sở dữ liệu qua SQL thuần, không chứa logic cào web.

**File:** `database/db_manager.py`

python
    
    
    import sqlite3
    
    class DBManager:
        def __init__(self, db_path="crawler.db"):
            self.db_path = db_path
            self.init_db()
    
        def get_connection(self):
            return sqlite3.connect(self.db_path)
    
        def init_db(self):
            """Khởi tạo các bảng bằng SQL thuần"""
            query_stories = """
            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                author TEXT,
                source TEXT
            );
            """
            query_chapters = """
            CREATE TABLE IF NOT EXISTS chapters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER,
                chapter_number REAL,
                title TEXT,
                content TEXT,
                FOREIGN KEY (story_id) REFERENCES stories (id)
            );
            """
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query_stories)
                cursor.execute(query_chapters)
                conn.commit()
    
        def save_story(self, title, url, author, source):
            """Chèn hoặc bỏ qua nếu truyện đã tồn tại, trả về story_id"""
            query = "INSERT OR IGNORE INTO stories (title, url, author, source) VALUES (?, ?, ?, ?)"
            select_query = "SELECT id FROM stories WHERE url = ?"
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (title, url, author, source))
                cursor.execute(select_query, (url,))
                row = cursor.fetchone()
                return row[0] if row else None
    
        def save_chapter(self, story_id, chapter_number, title, content):
            """Lưu chương truyện bằng SQL thuần"""
            query = "INSERT INTO chapters (story_id, chapter_number, title, content) VALUES (?, ?, ?, ?)"
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (story_id, chapter_number, title, content))
                conn.commit()
    

Hãy thận trọng khi sử dụng mã.

* * *

2\. Logic Tier (Tầng Xử Lý)

Tầng này chịu trách nhiệm gửi request, phân tích HTML. Để cào được **nhiều nguồn** , ta dùng kỹ thuật OOP để định nghĩa một khung chuẩn (`BaseScraper`), sau đó mỗi nguồn sẽ tự viết hàm bóc tách riêng.

**File:** `scrapers/base_scraper.py`

python
    
    
    from abc import ABC, abstractmethod
    import requests
    
    class BaseScraper(ABC):
        def __init__(self):
            self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
        def fetch_html(self, url):
            """Hàm tải HTML chung cho tất cả các nguồn"""
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    return response.text
            except Exception as e:
                print(f"Lỗi khi tải URL {url}: {e}")
            return None
    
        @abstractmethod
        def extract_story_info(self, html):
            """Mỗi nguồn phải tự định nghĩa cách lấy Tên, Tác giả"""
            pass
    
        @abstractmethod
        def extract_chapters_list(self, html):
            """Mỗi nguồn phải tự định nghĩa cách lấy danh sách Link chương"""
            pass
    
        @abstractmethod
        def extract_chapter_content(self, html):
            """Mỗi nguồn phải tự định nghĩa cách lấy nội dung chữ/ảnh của chương"""
            pass
    

Hãy thận trọng khi sử dụng mã.

**File:** `scrapers/source_a.py` (Ví dụ cụ thể cho nguồn truyện chữ)

python
    
    
    from bs4 import BeautifulSoup
    from scrapers.base_scraper import BaseScraper
    
    class SourceAScraper(BaseScraper):
        """Lớp cào cụ thể cho Nguồn A (Ví dụ: Bản mẫu dùng BeautifulSoup)"""
        
        def extract_story_info(self, html):
            soup = BeautifulSoup(html, 'html.parser')
            # Thay thế class/id tùy theo cấu trúc HTML thực tế của Nguồn A
            title = soup.find('h3', class_='title').text.strip()
            author = soup.find('span', class_='author').text.strip() if soup.find('span', class_='author') else "Unknown"
            return {"title": title, "author": author}
    
        def extract_chapters_list(self, html):
            soup = BeautifulSoup(html, 'html.parser')
            chapters = []
            # Lấy tất cả thẻ chứa link chương
            for a in soup.select('ul.list-chapter a'):
                chapters.append({
                    "title": a.text.strip(),
                    "url": a['href']
                })
            return chapters
    
        def extract_chapter_content(self, html):
            soup = BeautifulSoup(html, 'html.parser')
            # Lấy nội dung văn bản của chương truyện
            content_div = soup.find('div', class_='chapter-content')
            return content_div.text.strip() if content_div else ""
    

Hãy thận trọng khi sử dụng mã.

**File:** `core/crawler_engine.py` (Bộ điều phối kết nối Data Tier và Scraper)

python
    
    
    from database.db_manager import DBManager
    
    class CrawlerEngine:
        def __init__(self, scraper, source_name):
            self.scraper = scraper
            self.source_name = source_name
            self.db = DBManager()
    
        def execute(self, story_url):
            print(f"[*] Đang bắt đầu cào từ nguồn: {self.source_name}")
            
            # 1. Tải và bóc tách thông tin truyện chính
            story_html = self.scraper.fetch_html(story_url)
            if not story_html: return
            
            story_info = self.scraper.extract_story_info(story_html)
            
            # 2. Lưu thông tin truyện vào DB qua Data Tier
            story_id = self.db.save_story(
                title=story_info['title'],
                url=story_url,
                author=story_info['author'],
                source=self.source_name
            )
            print(f"[+] Đã lưu/Xác nhận truyện: {story_info['title']} (ID: {story_id})")
    
            # 3. Lấy danh sách chương
            chapters = self.scraper.extract_chapters_list(story_html)
            print(f"[+] Tìm thấy {len(chapters)} chương.")
    
            # 4. Vòng lặp cào từng chương truyện
            for idx, ch in enumerate(chapters, start=1):
                print(f" -> Đang cào chương {idx}: {ch['title']}")
                ch_html = self.scraper.fetch_html(ch['url'])
                if not ch_html: continue
                
                content = self.scraper.extract_chapter_content(ch_html)
                
                # Lưu chương vào DB bằng SQL thuần
                self.db.save_chapter(
                    story_id=story_id,
                    chapter_number=idx,
                    title=ch['title'],
                    content=content
                )
            print("[*] Hoàn thành tiến trình cào dữ liệu!")
    

Hãy thận trọng khi sử dụng mã.

* * *

3\. Presentation Tier (Tầng Điều Khiển / Giao Diện)

Giao diện dòng lệnh CLI đơn giản cho phép người dùng tương tác, chọn nguồn muốn cào và nhập link.

**File:** `main.py`

python
    
    
    from core.crawler_engine import CrawlerEngine
    from scrapers.source_a import SourceAScraper
    
    def main():
        print("=== HỆ THỐNG CÀO TRUYỆN ĐA NGUỒN 3-TIER ===")
        print("1. Cào từ Nguồn A (TruyenFull...)")
        print("2. Cào từ Nguồn B (Hiện chưa cấu hình...)")
        
        choice = input("Chọn nguồn cào (1-2): ")
        
        if choice == "1":
            scraper = SourceAScraper()
            source_name = "Nguon_A"
        else:
            print("Lựa chọn không hợp lệ hoặc chưa cấu hình nguồn này!")
            return
    
        story_url = input("Nhập URL của truyện cần cào: ").strip()
        
        if not story_url:
            print("URL không được để trống!")
            return
    
        # Kích hoạt Logic Tier xử lý tác vụ
        engine = CrawlerEngine(scraper, source_name)
        engine.execute(story_url)
    
    if __name__ == "__main__":
        main()
    

Hãy thận trọng khi sử dụng mã.

* * *

⚡ Các nâng cấp thực tế khuyến nghị cho Framework này

Để framework này vận hành thực tế mượt mà hơn, bạn nên nâng cấp thêm các phần sau:

  * **Xử lý đa luồng (Multi-threading):** Dùng `concurrent.futures.ThreadPoolExecutor` ở file `crawler_engine.py` khi cào danh sách chương để tải nhiều chương cùng lúc nhằm tăng tốc.
  * **Cơ chế chống chặn (Anti-Bot):** Tích hợp xoay tua **Proxy** và thay đổi ngẫu nhiên **User-Agent** vào hàm `fetch_html` trong `BaseScraper`.
  * **Hỗ trợ truyện tranh (Comic):** Hàm `extract_chapter_content` của nguồn truyện tranh sẽ trả về một _Danh sách URL ảnh_ thay vì dạng text, tầng Data Tier cần sửa bảng `chapters` để lưu danh sách chuỗi URL ảnh này (hoặc tải trực tiếp ảnh về máy).



Nếu bạn muốn mở rộng hệ thống, hãy cho tôi biết bạn định chọn **nguồn truyện cụ thể nào** (truyện chữ hay truyện tranh) hoặc cần tối ưu phần **cào đa luồng / chống chặn** , tôi sẽ bổ sung code chi tiết cho phần đó!

