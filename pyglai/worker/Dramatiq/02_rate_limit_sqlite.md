Để lưu truyện vào SQLite và thêm tính năng Rate Limit (giới hạn tần suất cào), chúng ta cần tích hợp thư viện `sqlite3` và middleware của Dramatiq để tránh bị trang web chặn IP.

Dưới đây là mã nguồn chi tiết sau khi nâng cấp hệ thống:

1\. File cấu hình và Worker (`tasks.py`)

Mã nguồn này bổ sung hàm khởi tạo cơ sở dữ liệu SQLite và sử dụng middleware `RateLimitingMiddleware` của Dramatiq để giới hạn tối đa **20 requests mỗi phút** (mỗi task cách nhau khoảng 3 giây).

python
    
    
    # tasks.py
    import sqlite3
    import time
    import dramatiq
    from dramatiq.brokers.redis import RedisBroker
    from dramatiq.middleware import RateLimitingMiddleware, TimeLimitMiddleware
    from dramatiq.rate_limits import ConcurrentRateLimiter
    import requests
    
    # 1. Cấu hình Broker với Rate Limiting Middleware
    # Giới hạn tối đa 20 task được xử lý trong 60 giây (60000 ms)
    rate_limiter = ConcurrentRateLimiter(host="localhost", port=6379)
    broker = RedisBroker(
        host="localhost", 
        port=6379,
        middleware=[
            RateLimitingMiddleware(rate_limiter),
            TimeLimitMiddleware(max_age=60000) # Task quá 60s không chạy sẽ bị hủy
        ]
    )
    dramatiq.set_broker(broker)
    
    # 2. Khởi tạo Database SQLite
    DB_NAME = "truyen.db"
    
    def init_db():
        """Tạo bảng lưu trữ truyện nếu chưa tồn tại"""
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
    
    # Chạy khởi tạo DB ngay khi worker load file này
    init_db()
    
    # 3. Định nghĩa Worker Task kèm Rate Limit
    # backend_mutations_limit giới hạn tần suất chạy của tác vụ này
    @dramatiq.actor(max_retries=3, rate_limits={"crawl_limit": (20, 60000)})
    def crawl_chapter(chapter_url: str):
        """Tác vụ cào truyện có giới hạn tần suất và lưu SQLite"""
        print(f"[{time.strftime('%H:%M:%S')}] Đang xử lý: {chapter_url}")
        
        try:
            # Giả lập tải trang (Thay bằng logic cào thực tế của bạn)
            response = requests.get(chapter_url, timeout=10)
            html_content = response.text
            
            # Giả lập bóc tách dữ liệu (Ví dụ tạm thời)
            title = f"Chương tự động từ URL"
            content = html_content[:500] # Lấy tạm 500 ký tự đầu làm nội dung
            
            # Lưu vào SQLite
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO chapters (url, title, content) VALUES (?, ?, ?)",
                    (chapter_url, title, content)
                )
                conn.commit()
                
            print(f"✔ Đã lưu thành công: {chapter_url}")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Lỗi mạng khi cào {chapter_url}: {e}")
            raise e  # Kích hoạt max_retries để Dramatiq thử lại sau
        except sqlite3.Error as e:
            print(f"❌ Lỗi SQLite: {e}")
    

Hãy thận trọng khi sử dụng mã.

2\. File Producer dùng Click CLI (`producer.py`)

Giữ nguyên giao diện CLI nhưng bổ sung thêm lệnh xem nhanh dữ liệu đã cào được trong SQLite để bạn tiện kiểm tra:

python
    
    
    # producer.py
    import click
    import sqlite3
    from tasks import crawl_chapter, DB_NAME
    
    @click.group()
    def cli():
        """Hệ thống CLI điều khiển Worker cào truyện (Hỗ trợ SQLite & Rate Limit)"""
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
        click.echo(click.style(f"Đã thêm {count} task vào hàng đợi. Kiểm tra worker để xem tốc độ rate limit.", fg="yellow"))
    
    @cli.command()
    @click.option('--limit', '-l', default=5, help='Số lượng dòng muốn xem.')
    def view_db(limit):
        """Xem nhanh dữ liệu đã lưu trong SQLite."""
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, url, title FROM chapters ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            
            if not rows:
                click.echo("Chưa có dữ liệu trong Database.")
                return
                
            click.echo(f"\n--- {limit} Chương mới nhất trong DB ---")
            for row in rows:
                click.echo(f"ID: {row[0]} | Title: {row[2]} | URL: {row[1]}")
    
    if __name__ == '__main__':
        cli()
    

Hãy thận trọng khi sử dụng mã.

3\. Kiểm tra tính năng Rate Limit

  1. Khởi động Worker: `dramatiq tasks`
  2. Tạo file `urls.txt` chứa khoảng 5-10 URL bất kỳ (mỗi URL 1 dòng).
  3. Đẩy hàng loạt task qua CLI: `python producer.py add-batch -f urls.txt`
  4. Quan sát Terminal của Worker: Bạn sẽ thấy các task không chạy ồ ạt cùng một lúc mà sẽ được **chia quãng nghỉ đều đặn** (khoảng ~3 giây một task) đúng theo cấu hình rate limit đã đặt.
  5. Kiểm tra kết quả lưu trữ: `python producer.py view-db`



Nếu bạn muốn tiếp tục tối ưu hệ thống, hãy phản hồi cho tôi biết:

  * Bạn có cần tích hợp thư viện **BeautifulSoup4** hoặc **Selectolax** để bóc tách chính xác thẻ HTML chứa tiêu đề/nội dung truyện không?
  * Bạn có cần cơ chế **tự động đổi Proxy hoặc User-Agent** cho từng request để tránh bị chặn triệt để hơn không?

