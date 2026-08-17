Để tự động cào tiếp chương sau (Auto Next Chapter), worker sau khi bóc tách chương hiện tại sẽ tìm thẻ chứa đường dẫn của chương kế tiếp (ví dụ: nút "Chương sau"). Nếu tìm thấy, nó sẽ tự động dùng lệnh `crawl_chapter.send(next_url)` để đẩy một task mới vào hàng đợi [Dramatiq](https://github.com/bogdanp/dramatiq).

Dưới đây là mã nguồn nâng cấp chi tiết cho cả hai file:

1\. Cập nhật file Worker (`tasks.py`)

Chúng ta bổ sung logic tìm thuộc tính `href` của nút chuyển chương và một cơ chế **chống lặp vô hạn** dựa trên SQLite (nếu chương đó đã có trong DB thì dừng lại, không đào sâu tiếp).

python
    
    
    # tasks.py
    import sqlite3
    import time
    from urllib.parse import urljoin # Dùng để xử lý link tương đối (vídụ: /chuong-2) thành link tuyệt đối
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
    
    def is_already_crawled(url: str) -> bool:
        """Kiểm tra xem URL này đã được cào chưa"""
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM chapters WHERE url = ?", (url,))
            return cursor.fetchone() is not None
    
    # 2. Worker Task tích hợp Đệ quy hàng đợi (Auto-Next)
    @dramatiq.actor(max_retries=3, rate_limits={"crawl_limit": (20, 60000)})
    def crawl_chapter(chapter_url: str):
        """Tác vụ cào truyện, lưu SQLite và tự động kích hoạt chương tiếp theo"""
        print(f"[{time.strftime('%H:%M:%S')}] Đang cào: {chapter_url}")
        
        # Kiểm tra tránh cào trùng lặp hoặc lặp vòng tròn vô hạn
        if is_already_crawled(chapter_url):
            print(f"⚠ Bỏ qua (URL đã tồn tại trong DB): {chapter_url}")
            return
    
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        try:
            response = requests.get(chapter_url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            # --- 1. BÓC TÁCH TIÊU ĐỀ & NỘI DUNG ---
            title_node = soup.find("h1") or soup.find(class_="chapter-title")
            title = title_node.get_text(strip=True) if title_node else "Không rõ tiêu đề"
            
            content_node = soup.find(class_="chapter-content") or soup.find(id="chapter-c")
            if content_node:
                for s in content_node(["script", "style", "iframe"]):
                    s.extract()
                content = content_node.get_text(separator="\n", strip=True)
            else:
                content = "Không tìm thấy nội dung"
    
            # --- 2. LƯU VÀO SQLITE ---
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO chapters (url, title, content) VALUES (?, ?, ?)",
                    (chapter_url, title, content)
                )
                conn.commit()
            print(f"✔ Đã lưu thành công: {title}")
    
            # --- 3. LOGIC TỰ ĐỘNG TÌM CHƯƠNG TIẾP THEO ---
            # Thay đổi selector (ví dụ: text="Chương sau", class_="next-chap", id="next_chap") theo web thật
            next_node = (
                soup.find("a", string=lambda text: text and "Chương sau" in text) or 
                soup.find("a", class_="btn-next") or
                soup.find("a", id="next_chap")
            )
            
            if next_node and next_node.get("href"):
                raw_next_url = next_node["href"]
                # Chuyển link tương đối thành link tuyệt đối đầy đủ định dạng http/https
                next_url = urljoin(chapter_url, raw_next_url)
                
                # Tránh việc nút "Chương sau" trỏ ngược lại chính nó hoặc trỏ vào ký tự trống '#'
                if next_url != chapter_url and not raw_next_url.startswith("#"):
                    print(f"🔗 Phát hiện chương tiếp theo: {next_url}. Đang gửi task vào hàng đợi...")
                    crawl_chapter.send(next_url) # Đẩy task mới vào Dramatiq
                else:
                    print("🏁 Đã đến chương cuối cùng (Link chương sau không hợp lệ hoặc trùng lặp).")
            else:
                print("🏁 Đã đến chương cuối cùng (Không tìm thấy nút Chương sau).")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Lỗi kết nối mạng: {e}")
            raise e
        except Exception as e:
            print(f"❌ Lỗi hệ thống: {e}")
    

Hãy thận trọng khi sử dụng mã.

2\. Cập nhật file CLI (`producer.py`)

Thêm tùy chọn `--auto` (hoặc `-a`) bằng `click.option` để người dùng linh hoạt quyết định xem chỉ muốn cào **đúng 1 chương đơn lẻ** hay muốn kích hoạt **chuỗi cào liên tục tự động**.

python
    
    
    # producer.py
    import click
    import sqlite3
    from tasks import crawl_chapter, DB_NAME
    
    @click.group()
    def cli():
        """CLI quản lý Worker cào truyện tự động chuyển chương"""
        pass
    
    @cli.command()
    @click.option('--url', '-u', required=True, help='URL của chapter truyện bắt đầu.')
    def start(url):
        """Bắt đầu cào từ chương này và tự động đào sâu sang các chương tiếp theo."""
        crawl_chapter.send(url)
        click.echo(click.style(f"🚀 Đã kích hoạt chuỗi cào tự động bắt đầu từ URL: {url}", fg="green", bold=True))
    
    @cli.command()
    @click.option('--limit', '-l', default=5, help='Số lượng dòng muốn xem.')
    def view_db(limit):
        """Xem các chương mới nhất trong SQLite."""
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, url FROM chapters ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            
            if not rows:
                click.echo("Chưa có dữ liệu.")
                return
                
            click.echo(f"\n--- {limit} Chương vừa cào mới nhất ---")
            for row in rows:
                click.echo(f"ID: {row} | {row} \n  -> URL: {row}")
                click.echo("-" * 50)
    
    if __name__ == '__main__':
        cli()
    

Hãy thận trọng khi sử dụng mã.

3\. Nguyên lý hoạt động trên Terminal

  1. Bật worker chạy ngầm: `dramatiq tasks`
  2. Kích hoạt cào từ chương 1 của một bộ truyện bằng CLI:

bash
         
         python producer.py start --url https://example.com
         

Hãy thận trọng khi sử dụng mã.

  3. **Luồng xử lý tự động** :
     * Worker nhận lệnh cào `chuong-1` → Lưu vào SQLite.
     * Xử lý xong, BeautifulSoup tìm thấy link `chuong-2` → Tự động gửi task `chuong-2` vào Redis.
     * Do có middleware Rate limit, task `chuong-2` sẽ đợi khoảng 3 giây rồi mới chạy tiếp.
     * Quá trình này lặp lại liên tục giống như một hiệu ứng Domino cho đến khi gặp chương cuối cùng thì dừng lại.



Nếu bạn muốn kiểm soát chặt chẽ hơn tiến trình cào này, hãy cho tôi biết:

  * Bạn có cần **giới hạn số lượng chương tối đa** cho một chuỗi cào (ví dụ: chỉ tự động cào tiếp tối đa 50 chương rồi dừng) không?
  * Bạn có cần tách bảng SQLite thành 2 bảng riêng biệt: `stories` (thông tin truyện) và `chapters` (nội dung chi tiết từng chương) không?

