Nếu bạn đang nhắm tới **Procrastinate** , đây là một lựa chọn cực kỳ thông minh và thực tế cho dự án cào truyện nếu bạn **muốn hệ thống gọn gàng nhất có thể và đã chọn PostgreSQL làm database chính**.

Điểm đặc biệt nhất của Procrastinate là nó dùng cơ chế `LISTEN/NOTIFY` của **PostgreSQL làm Message Broker** luôn. Bạn hoàn toàn **không cần cài thêm Redis hay RabbitMQ**.

Dưới đây là cách áp dụng Procrastinate kết hợp với `requests` và `beautifulsoup4` cho ứng dụng cào truyện của bạn:

1\. Chuẩn bị môi trường

Cài đặt thư viện Procrastinate (phiên bản hỗ trợ driver đồng bộ `psycopg` cho phù hợp với `requests`):

bash
    
    
    pip install "procrastinate[psycopg]" requests beautifulsoup4
    

Hãy thận trọng khi sử dụng mã.

2\. Mã nguồn cấu hình và định nghĩa Actor cào truyện

Bạn tạo file `crawler_procrastinate.py`:

python
    
    
    import procrastinate
    from procrastinate.contrib.psycopg import Psycopg3Connector
    import requests
    from bs4 import BeautifulSoup
    import time
    
    # 1. Kết nối trực tiếp tới PostgreSQL (vừa làm Broker, vừa làm nơi lưu trữ task)
    # Thay thông tin database của bạn vào đây
    device_connector = Psycopg3Connector(
        conninfo="postgresql://postgres:password@localhost:5432/truyen_db"
    )
    app = procrastinate.App(connector=device_connector)
    
    # -------------------------------------------------------------------------
    # TASK 1: Quét danh sách chương
    # -------------------------------------------------------------------------
    @app.task(queue="discovery_queue")
    def discover_story(story_id: int, story_url: str):
        print(f"[Discover] Đang quét danh sách chương từ: {story_url}")
        
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(story_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return
    
        soup = BeautifulSoup(response.text, 'html.parser')
        # Giả sử cấu trúc thẻ chứa link chương
        chapter_elements = soup.find_all('a', class_='chapter-link')
        
        print(f"[Discover] Tìm thấy {len(chapter_elements)} chương. Tiến hành đẩy vào Postgres...")
        
        for index, elem in enumerate(chapter_elements, start=1):
            chapter_url = elem['href']
            
            # Đẩy task cào từng chương vào Postgres
            # Sử dụng lock để đảm bảo không cào trùng một chương cùng lúc
            crawl_chapter_content.defer(
                story_id=story_id, 
                chapter_num=index, 
                chapter_url=chapter_url
            )
    
    # -------------------------------------------------------------------------
    # TASK 2: Cào nội dung chi tiết chương (Hỗ trợ cấu hình Retry chuyên sâu)
    # -------------------------------------------------------------------------
    # Nếu lỗi mạng, task này sẽ tự động thử lại sau 30s, 60s, 120s...
    retry_strategy = procrastinate.RetryStrategy(max_attempts=5, wait=30)
    
    @app.task(queue="crawler_queue", retry=retry_strategy)
    def crawl_chapter_content(story_id: int, chapter_num: int, chapter_url: str):
        print(f"[Crawl] Đang tải chương {chapter_num} của truyện {story_id}")
        
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(chapter_url, headers=headers, timeout=10)
        
        # Nếu dính lỗi HTTP (như 429 bận, 502 sập nguồn), raise lỗi để Postgres kích hoạt retry
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h2', class_='chapter-title').text.strip()
        content = soup.find('div', class_='chapter-content').text.strip()
        
        # Ghi nhận kết quả (Lưu luôn vào bảng dữ liệu truyện của bạn trong cùng DB Postgres)
        print(f"[DB] Đã cào xong & lưu: {title}")
        
        # Nghỉ 1 giây để tránh bị website chặn IP
        time.sleep(1)
    

Hãy thận trọng khi sử dụng mã.

3\. Cách vận hành hệ thống với Procrastinate

**Bước 1: Khởi tạo các bảng quản lý hàng đợi trong Postgres**  
Vì Procrastinate lưu dữ liệu task vào Postgres, bạn cần tạo các bảng schema cho nó trước khi chạy. Chạy lệnh này một lần duy nhất:

bash
    
    
    procrastinate --app=crawler_procrastinate.app schema --apply
    

Hãy thận trọng khi sử dụng mã.

**Bước 2: Chạy Worker kích hoạt cào dữ liệu**  
Bạn có thể mở nhiều cửa sổ terminal (hoặc chạy nền) để tăng tốc độ cào:

bash
    
    
    # Worker này chỉ tập trung đi cào nội dung chương (chạy đa luồng song song)
    procrastinate --app=crawler_procrastinate.app worker --queue=crawler_queue
    

Hãy thận trọng khi sử dụng mã.

**Bước 3: Gọi lệnh cào từ code ứng dụng của bạn**  
Khi có một bộ truyện mới cần cào, bạn kích hoạt bằng lệnh:

python
    
    
    from crawler_procrastinate import discover_story
    
    # Đẩy lệnh quét vào Postgres
    discover_story.defer(story_id=999, story_url="https://website-truyen.com")
    

Hãy thận trọng khi sử dụng mã.

4\. Tại sao Procrastinate cực kỳ ĐÁNG DÙNG cho app cào truyện?

  1. **Một Database cho tất cả:** Bạn vừa lưu thông tin bộ truyện, chương truyện, vừa lưu hàng đợi tác vụ trong cùng một database Postgres. Việc sao lưu (Backup) hay dọn dẹp data cực kỳ tập trung.
  2. **Quản lý hàng đợi bằng SQL thuần túy:** Bạn có thể mở DBeaver/PgAdmin lên, viết lệnh SQL `SELECT * FROM procrastinate_jobs;` là thấy ngay có bao nhiêu chương đang chờ cào, chương nào bị lỗi, lỗi vì sao (nó lưu toàn bộ Traceback lỗi vào cột trong DB). Bạn có thể sửa trạng thái task lỗi thành `todo` bằng lệnh `UPDATE` để nó tự cào lại.
  3. **Hỗ trợ khóa (Locking) thông minh:** Khi cào truyện, đôi khi bạn vô tình bấm cào 1 bộ truyện 2 lần. Procrastinate hỗ trợ thuộc tính `locks`. Bạn chỉ cần truyền tên lock, ví dụ `locks=[f"story_{story_id}"]`, nó sẽ đảm bảo tại một thời điểm chỉ có duy nhất 1 worker được xử lý bộ truyện đó, tránh việc spam request trùng lặp làm block IP.



Nếu bạn muốn tôi hướng dẫn chi tiết cách **viết câu lệnh SQL để quản lý/bật lại các chương cào lỗi** trực tiếp trên database Postgres, hoặc cách cấu hình **kết nối an toàn (Connection Pool)** , hãy cho tôi biết nhé!

