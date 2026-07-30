Để hoàn thiện framework lên mức production, chúng ta sẽ xử lý hai bài toán thực tế quan trọng nhất khi vận hành hệ thống cào dữ liệu lớn: **Bảo mật thông tin cấu hình** và **Vượt cơ chế chặn IP (Anti-Bot)**.

Chúng ta sẽ tách biệt thông tin mật ra file `.env` và quản lý kho dữ liệu Proxy động hoàn toàn bằng SQL thuần.

* * *

🛠️ 1. Bảo mật thông tin bằng biến môi trường (File `.env`)

Để tránh việc lộ mật khẩu Database khi đẩy code lên GitHub, chúng ta cần cài đặt thư viện đọc biến môi trường:

bash
    
    
    pip install python-dotenv
    

Hãy thận trọng khi sử dụng mã.

Tạo file cấu hình `.env`

Tạo file `.env` nằm ở thư mục gốc của dự án:

env
    
    
    # Cấu hình Cơ sở dữ liệu PostgreSQL
    DB_NAME=comic_crawler_db
    DB_USER=postgres
    DB_PASSWORD=your_secure_password
    DB_HOST=localhost
    DB_PORT=5432
    
    # Cấu hình Trình cào dữ liệu
    MAX_CRAWL_THREADS=5
    REQUEST_TIMEOUT=10
    

Hãy thận trọng khi sử dụng mã.

Cập nhật Data Tier đọc file cấu hình

**Sửa đổi file:** `database/db_manager.py`

python
    
    
    import os
    import psycopg2
    from dotenv import load_dotenv
    
    # Tải các biến môi trường từ file .env vào bộ nhớ hệ thống
    load_dotenv()
    
    class DBManager:
        def __init__(self):
            # Đọc trực tiếp từ môi trường thay vì viết cứng (hardcode) dữ liệu mật
            self.config = {
                "dbname": os.getenv("DB_NAME"),
                "user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
                "host": os.getenv("DB_HOST"),
                "port": os.getenv("DB_PORT")
            }
            self.init_db()
            
        def get_connection(self):
            return psycopg2.connect(**self.config)
            
        def init_db(self):
            # ... (Giữ nguyên phần khởi tạo các bảng cũ) ...
            
            # Thêm bảng quản lý Proxy bằng SQL thuần
            query_proxies = """
            CREATE TABLE IF NOT EXISTS proxy_pool (
                id SERIAL PRIMARY KEY,
                proxy_address TEXT UNIQUE NOT NULL, -- Định dạng: http://ip:port hoặc http://user:pass@ip:port
                fail_count INTEGER DEFAULT 0,       # Đếm số lần lỗi để loại bỏ proxy chết
                is_active BOOLEAN DEFAULT TRUE
            );
            """
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query_proxies)
                conn.commit()
    

Hãy thận trọng khi sử dụng mã.

* * *

🌐 2. Quản lý xoay tua Proxy (Proxy Rotator) bằng SQL thuần

Khi cào hàng nghìn chương, TruyenFull hay Webnovel sẽ quét tần suất gửi request từ IP của bạn và khóa (Block IP). Giải pháp là mỗi luồng cào sẽ lấy ngẫu nhiên 1 Proxy hoạt động tốt trong DB để đổi danh tính mạng.

Tạo ProxyRepository (Data Tier)

**File:** `database/proxy_repository.py`

python
    
    
    import psycopg2
    from database.db_manager import DBManager
    
    class ProxyRepository:
        def __init__(self):
            self.db_manager = DBManager()
    
        def get_random_active_proxy(self) -> str:
            """Lấy ngẫu nhiên một proxy đang hoạt động tốt bằng SQL thuần"""
            query = """
            SELECT proxy_address FROM proxy_pool 
            WHERE is_active = TRUE 
            ORDER BY RANDOM() 
            LIMIT 1;
            """
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    row = cursor.fetchone()
                    return row[0] if row else None
    
        def log_proxy_failure(self, proxy_address: str):
            """Cộng dồn số lần lỗi, nếu lỗi quá 5 lần thì đánh dấu ngưng hoạt động"""
            query = """
            UPDATE proxy_pool 
            SET fail_count = fail_count + 1,
                is_active = CASE WHEN fail_count + 1 >= 5 THEN FALSE ELSE TRUE END
            WHERE proxy_address = %s;
            """
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (proxy_address,))
                conn.commit()
    

Hãy thận trọng khi sử dụng mã.

* * *

⚙️ 3. Tích hợp Proxy Xoay Tua vào Logic Tier

Chúng ta sẽ nâng cấp hàm tải dữ liệu mạng tại lớp cơ sở để tự động đính kèm cấu hình mạng ẩn danh.

**Sửa đổi file:** `scrapers/base_scraper.py`

python
    
    
    import os
    import requests
    from database.proxy_repository import ProxyRepository
    
    class BaseScraper:
        def __init__(self):
            self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            self.proxy_repo = ProxyRepository()
            self.timeout = int(os.getenv("REQUEST_TIMEOUT", 10))
    
        def fetch_html(self, url: str) -> str:
            """Tự động lấy proxy ngẫu nhiên từ DB để gửi request"""
            proxy_url = self.proxy_repo.get_random_active_proxy()
            proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
            
            try:
                # Gửi request kèm theo Proxy đại diện
                response = requests.get(
                    url, 
                    headers=self.headers, 
                    proxies=proxies, 
                    timeout=self.timeout
                )
                if response.status_code == 200:
                    return response.text
                    
                # Nếu website trả về mã lỗi chặn (403 Forbidden, 429 Too Many Requests)
                if response.status_code in [403, 429] and proxy_url:
                    self.proxy_repo.log_proxy_failure(proxy_url)
                    
            except requests.RequestException:
                # Nếu Proxy bị nghẽn, sập luồng mạng, báo lỗi về Tầng Data
                if proxy_url:
                    self.proxy_repo.log_proxy_failure(proxy_url)
                    
            return None
    

Hãy thận trọng khi sử dụng mã.

* * *

📊 Mô hình vận hành hoàn chỉnh của Framework

Hệ thống của bạn lúc này hoạt động khép kín và an toàn tuyệt đối:

  1. **Presentation Tier:** Tiếp nhận yêu cầu.
  2. **Logic Tier:** Chia danh sách chương thành các luồng chạy song song (`MAX_CRAWL_THREADS` lấy từ file `.env`). Mỗi luồng tự động yêu cầu một Proxy ngẫu nhiên để lướt web. Nếu lỗi, nó tự động cập nhật nhật ký lỗi (`Error Logs`) và loại trừ Proxy hỏng.
  3. **Data Tier:** Kết nối an toàn đến PostgreSQL thông qua thông tin mật bảo mật trong hệ thống, thực thi các truy vấn SQL thuần tốc độ cao.



Nếu bạn muốn tiếp tục tối ưu hóa hệ thống này, hãy cho tôi biết:

  * Bạn có muốn xây dựng **bộ công cụ kiểm tra độ sống/chết của Proxy (Proxy Checker)** chạy ngầm độc lập?
  * Hay bạn muốn tìm hiểu cách chuyển đổi toàn bộ thư viện `requests` đồng bộ sang **`httpx` kết hợp `asyncio` (Lập trình bất đồng bộ)** để đẩy hiệu năng cào lên gấp 10 lần so với đa luồng?

