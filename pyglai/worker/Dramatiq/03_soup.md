Để tích hợp **BeautifulSoup4** vào hệ thống, chúng ta sẽ viết thêm logic bóc tách phần tử HTML (như tên chương và nội dung văn bản) rồi mới lưu vào SQLite.

1\. Cài đặt thêm thư viện

Chạy lệnh sau để cài đặt BeautifulSoup4:

bash
    
    
    pip install beautifulsoup4
    

Hãy thận trọng khi sử dụng mã.

2\. Cập nhật file Worker (`tasks.py`)

Đoạn mã dưới đây sử dụng `BeautifulSoup` với parser mặc định `html.parser` để tìm chính xác thẻ chứa tiêu đề (ví dụ: `<h1>`) và nội dung truyện (ví dụ: `<div class="chapter-content">`).

_Lưu ý: Bạn cần thay đổi các class CSS (`.chapter-title`, `.chapter-content`) trong code sao cho khớp với cấu trúc thực tế của trang web bạn đang muốn cào._

python
    
    
    # tasks.py
    import sqlite3
    import time
    import dramatiq
    from dramatiq.brokers.redis import RedisBroker
    from dramatiq.middleware import RateLimitingMiddleware, TimeLimitMiddleware
    from dramatiq.rate_limits import ConcurrentRateLimiter
    import requests
    from bs4 import BeautifulSoup
    
    # 1. Cấu hình Broker với Rate Limiting (Giữ nguyên)
    rate_limiter = ConcurrentRateLimiter(host="localhost", port=6379)
    broker = RedisBroker(
        host="localhost", 
        port=6379,
        middleware=[
            RateLimitingMiddleware(rate_limiter),
            TimeLimitMiddleware(max_age=60000)
        ]
    )
    dramatiq.set_broker(broker)
    
    # 2. Khởi tạo Database SQLite (Giữ nguyên)
    DB_NAME = "truyen.db"
    
    def init_db():
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chapters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE,
                    title TEXT,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    init_db()
    
    # 3. Worker Task tích hợp BeautifulSoup4
    @dramatiq.actor(max_retries=3, rate_limits={"crawl_limit": (20, 60000)})
    def crawl_chapter(chapter_url: str):
        """Tác vụ cào truyện, bóc tách bằng BeautifulSoup và lưu SQLite"""
        print(f"[{time.strftime('%H:%M:%S')}] Đang cào: {chapter_url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        try:
            # Gửi request tải trang HTML
            response = requests.get(chapter_url, headers=headers, timeout=10)
            response.raise_for_status() # Báo lỗi nếu status code là 4xx hoặc 5xx
            
            # Ép kiểu dữ liệu html sang BeautifulSoup để phân tích
            soup = BeautifulSoup(response.text, "html.parser")
            
            # --- LOGIC BÓC TÁCH DỮ LIỆU (Thay đổi selector tùy theo trang truyện) ---
            # Tìm tiêu đề chương (Thường nằm trong thẻ h1 hoặc h2)
            title_node = soup.find("h1") or soup.find(class_="chapter-title")
            title = title_node.get_text(strip=True) if title_node else "Không tìm thấy tiêu đề"
            
            # Tìm nội dung chương (Thường nằm trong div có class cụ thể)
            content_node = soup.find(class_="chapter-content") or soup.find(id="chapter-c")
            
            if content_node:
                # Loại bỏ các thẻ không cần thiết nếu có (như quảng cáo, script tự chèn)
                for s in content_node(["script", "style", "iframe"]):
                    s.extract()
                # Lấy toàn bộ văn bản, giữ lại xuống dòng giữa các đoạn văn
                content = content_node.get_text(separator="\n", strip=True)
            else:
                content = "Không tìm thấy nội dung truyện"
            # ------------------------------------------------------------------------
    
            # Lưu dữ liệu sạch đã bóc tách vào SQLite
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO chapters (url, title, content) VALUES (?, ?, ?)",
                    (chapter_url, title, content)
                )
                conn.commit()
                
            print(f"✔ Đã cào & lưu: {title}")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Lỗi kết nối mạng: {e}")
            raise e
        except Exception as e:
            print(f"❌ Lỗi xử lý dữ liệu: {e}")
    

Hãy thận trọng khi sử dụng mã.

3\. Cập nhật file CLI (`producer.py`)

Cập nhật nhẹ hàm `view_db` để in ra terminal đẹp mắt và rõ ràng hơn khi có tiêu đề thực tế:

python
    
    
    # producer.py
    import click
    import sqlite3
    from tasks import crawl_chapter, DB_NAME
    
    @click.group()
    def cli():
        """Hệ thống CLI điều khiển Worker cào truyện (Sử dụng BeautifulSoup)"""
        pass
    
    @cli.command()
    @click.option('--url', '-u', required=True, help='URL của chapter truyện cần cào.')
    def add_task(url):
        """Đẩy 1 URL chapter vào hàng đợi."""
        crawl_chapter.send(url)
        click.echo(click.style(f"Đã thêm task cho URL: {url}", fg="green"))
    
    @cli.command()
    @click.option('--file', '-f', type=click.File('r'), required=True, help='File chứa danh sách URL.')
    def add_batch(file):
        """Đẩy hàng loạt URL từ file văn bản vào hàng đợi."""
        count = 0
        for line in file:
            url = line.strip()
            if url:
                crawl_chapter.send(url)
                count += 1
        click.echo(click.style(f"Đã thêm {count} task vào hàng đợi thành công.", fg="yellow"))
    
    @cli.command()
    @click.option('--limit', '-l', default=3, help='Số lượng dòng muốn xem.')
    def view_db(limit):
        """Xem dữ liệu chương đã bóc tách trong SQLite."""
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, SUBSTR(content, 1, 100), url FROM chapters ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            
            if not rows:
                click.echo("Chưa có dữ liệu trong Database.")
                return
                
            for row in rows:
                click.echo(click.style(f"\n[ID: {row[0]}] {row[1]}", fg="cyan", bold=True))
                click.echo(f"URL: {row[3]}")
                click.echo(f"Nội dung bản xem trước: {row[2]}...")
                click.echo("-" * 40)
    
    if __name__ == '__main__':
        cli()
    

Hãy thận trọng khi sử dụng mã.

4\. Cách vận hành

  1. Chạy Worker ở terminal 1: `dramatiq tasks`
  2. Thay các URL thật từ trang truyện bạn muốn cào vào file `urls.txt`.
  3. Đẩy hàng loạt task ở terminal 2: `python producer.py add-batch -f urls.txt`
  4. Kiểm tra dữ liệu văn bản sạch đã được lưu: `python producer.py view-db`



Bạn có muốn bổ sung thêm tính năng **tự động cào tiếp chương sau (Next Chapter)** bằng cách tìm link ở nút "Chương tiếp theo" ngay trong BeautifulSoup không?

