Sự kết hợp giữa **Requests + BeautifulSoup + Dramatiq** là bộ combo hoàn hảo (Lightweight Stack) cho app cào truyện: Requests/Soup lo phần bóc tách dữ liệu, còn Dramatiq quản lý việc cào song song và tự động xử lý khi gặp lỗi mạng.

Dưới đây là kiến trúc và mã nguồn hoàn chỉnh giúp bạn xây dựng hệ thống cào truyện tự động, chia làm 2 giai đoạn: Giai đoạn 1 lấy danh sách chương, Giai đoạn 2 cào đồng thời nội dung các chương.

1\. Kiến trúc phân tách tác vụ (Pipeline)

Đừng gộp chung việc "tìm danh sách chương" và "cào nội dung chương" vào một hàm. Hãy chia thành 2 Actor (tác vụ) độc lập:

  1. **Actor 1 (`discover_story`)**: Vào trang chính của truyện → Lấy danh sách tất cả các URL của các chương → Đẩy từng URL chương vào hàng đợi cho Actor 2.
  2. **Actor 2 (`crawl_chapter_content`)**: Nhận URL của một chương cụ thể → Tải nội dung → Bóc tách bằng Soup → Lưu vào Database. [[1](https://docs.apify.com/sdk/python/docs/guides/beautifulsoup-httpx)]



2\. Mã nguồn triển khai chi tiết

Bạn tạo một file `crawler.py`:

python
    
    
    import dramatiq
    from dramatiq.brokers.redis import RedisBroker
    import requests
    from bs4 import BeautifulSoup
    import time
    
    # 1. Cấu hình Broker kết nối tới Redis
    broker = RedisBroker(url="redis://localhost:6379/0")
    dramatiq.set_broker(broker)
    
    # Giả lập Database (Thay thế bằng code kết nối MySQL/MongoDB/PostgreSQL của bạn)
    def save_chapter_to_db(story_id, chapter_num, title, content):
        print(f"[DB LOG] Đã lưu vào DB: Truyện {story_id} - Chương {chapter_num}: {title}")
    
    # -------------------------------------------------------------------------
    # ACTOR 1: Quét thông tin truyện và tạo danh sách chương cần cào
    # -------------------------------------------------------------------------
    @dramatiq.actor
    def discover_story(story_id, story_url):
        print(f"Bắt đầu quét truyện ID: {story_id} tại {story_url}")
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(story_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"Không thể truy cập trang truyện: {story_url}")
            return
    
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Giả sử trang web có danh sách chương nằm trong thẻ <a class="chapter-link">
        # BẠN CẦN SỬA LẠI SELECTOR NÀY CHO ĐÚNG VỚI TRANG BẠN CÀO
        chapter_elements = soup.find_all('a', class_='chapter-link')
        
        print(f"Tìm thấy {len(chapter_elements)} chương. Đang đẩy vào hàng đợi...")
        
        for index, elem in enumerate(chapter_elements, start=1):
            chapter_url = elem['href']
            # Đẩy từng chương vào hàng đợi xử lý song song
            crawl_chapter_content.send(story_id, index, chapter_url)
    
    # -------------------------------------------------------------------------
    # ACTOR 2: Cào nội dung chi tiết của từng chương (Hỗ trợ tự động thử lại khi lỗi)
    # -------------------------------------------------------------------------
    @dramatiq.actor(
        max_retries=5,          # Nếu lỗi (mạng, sập nguồn cấp...), thử lại tối đa 5 lần
        min_backoff=60000,      # Chờ ít nhất 60 giây (60000ms) trước khi thử lại để tránh bị chặn IP
    )
    def crawl_chapter_content(story_id, chapter_num, chapter_url):
        print(f"Đang cào: Truyện {story_id} - Chương {chapter_num}")
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        
        # Thực hiện request
        response = requests.get(chapter_url, headers=headers, timeout=10)
        
        # Nếu gặp lỗi HTTP 429 (Too Many Requests), 502, 503... lệnh này sẽ raise lỗi.
        # Dramatiq sẽ bắt được lỗi này và tự động đưa chương này vào hàng đợi để cào lại sau.
        response.raise_for_status() 
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # BẠN CẦN SỬA LẠI SELECTOR NÀY THEO CẤU TRÚC WEB ĐÍCH
        title = soup.find('h2', class_='chapter-title').text.strip()
        content_div = soup.find('div', class_='chapter-content')
        
        # Xử lý xuống dòng cho text truyện đẹp hơn
        for br in content_div.find_all("br"):
            br.replace_with("\n")
        content = content_div.text.strip()
        
        # Lưu kết quả
        save_chapter_to_db(story_id, chapter_num, title, content)
        
        # Tạo độ trễ nhỏ giữa các request của cùng một worker để tránh bị block IP
        time.sleep(1) 
    

Hãy thận trọng khi sử dụng mã.

3\. Cách vận hành hệ thống cào này

**Bước 1: Khởi động Redis** (Nếu chưa có, chạy bằng Docker cho nhanh):

bash
    
    
    docker run -d -p 6379:6379 redis
    

Hãy thận trọng khi sử dụng mã.

**Bước 2: Khởi động Dramatiq Worker** để túc trực xử lý các tác vụ cào:

bash
    
    
    # Tham số --threads 10 giúp chạy 10 luồng cào đồng thời, cực kỳ tiết kiệm RAM
    dramatiq crawler --threads 10
    

Hãy thận trọng khi sử dụng mã.

**Bước 3: Kích hoạt cào một bộ truyện** (Chạy từ một file Python khác hoặc từ giao diện web/Django/FastAPI của bạn):

python
    
    
    from crawler import discover_story
    
    # Chỉ cần gọi hàm này một lần, hệ thống sẽ tự động bóc tách và cào 1000 chương song song
    discover_story.send(story_id=123, story_url="https://website-truyen.com")
    

Hãy thận trọng khi sử dụng mã.

4\. Mẹo nâng cao khi cào bằng Requests + Soup trên Dramatiq

  * **Tránh bị Block IP:** Khi bạn chạy `--threads 10`, 10 chương sẽ bị cào cùng một giây → Server nguồn rất dễ quét và khóa IP của bạn. Hãy tích hợp thêm thư viện `requests` kết hợp với Proxy xoay vòng (Rotating Proxy) bên trong `crawl_chapter_content`.
  * **Quản lý Task lỗi:** Khi một chương bị lỗi quá 5 lần (vượt `max_retries`), Dramatiq sẽ đưa nó vào `Dead Letter Queue`. Bạn có thể dùng lệnh `dramatiq-gui` (giao diện web quản lý của Dramatiq) để bấm nút "Chạy lại" (Retry) tất cả các chương lỗi này sau khi đã đổi Proxy hoặc sửa xong Selector của Soup.



Nếu bạn muốn biết cách tích hợp **Proxy xoay vòng** vào Dramatiq để cào không sợ bị chặn, hoặc cách kết nối trực tiếp vào **Database** nào (MySQL/MongoDB), hãy phản hồi để tôi bổ sung đoạn code mẫu nhé!

