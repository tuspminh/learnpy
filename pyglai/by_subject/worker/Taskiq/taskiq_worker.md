Xây dựng hệ thống cào truyện gồm 3 file chính sử dụng [Taskiq](https://github.com/taskiq-python/taskiq) làm hàng đợi tác vụ, [Click](https://click.palletsprojects.com/) làm giao diện dòng lệnh (CLI), kết hợp với `requests` và `BeautifulSoup4` để lấy dữ liệu.

Cài đặt thư viện

Chạy lệnh sau để cài đặt các gói cần thiết:

bash
    
    
    pip install taskiq taskiq-redis click requests beautifulsoup4
    

Hãy thận trọng khi sử dụng mã.

1\. File cấu hình Broker (`broker.py`)

Khởi tạo broker sử dụng Redis để truyền thông điệp giữa CLI producer và worker. [[1](https://github.com/taskiq-python/taskiq-redis)]

python
    
    
    # broker.py
    from taskiq_redis import ListQueueBroker
    
    # Khởi tạo broker kết nối tới Redis local
    broker = ListQueueBroker(url="redis://localhost:6379")
    

Hãy thận trọng khi sử dụng mã.

2\. File định nghĩa Task cào truyện (`tasks.py`)

Viết logic dùng `requests` và `BeautifulSoup4` để phân tích trang web truyện. [[1](https://codelearn.io/sharing/python-crawl-du-lieu-tao-bai-bao-nhanh?srsltid=AfmBOoopJdM9BwvM-4YKGfZ8F1x5RX_oHZS-40yBQkfoazUg5jx5DlV7)]

python
    
    
    # tasks.py
    import requests
    from bs4 import BeautifulSoup
    from broker import broker
    
    @broker.task
    def crawl_chapter(url: str) -> str:
        """Task cào nội dung một chương truyện từ URL chỉ định."""
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Thay thế '.chapter-title' và '.chapter-content' bằng Selector thực tế của trang web
            title = soup.select_one(".chapter-title").get_text(strip=True) if soup.select_one(".chapter-title") else "No Title"
            content = soup.select_one(".chapter-content").get_text(separator="\n", strip=True) if soup.select_one(".chapter-content") else "No Content"
            
            print(f"Đã cào xong: {title}")
            # Lưu file hoặc xử lý tiếp dữ liệu ở đây tùy ý
            return f"Success: {title}"
        except Exception as e:
            print(f"Lỗi khi cào {url}: {e}")
            return f"Error: {str(e)}"
    

Hãy thận trọng khi sử dụng mã.

3\. File Producer CLI (`cli.py`)

Sử dụng `click` để tạo lệnh điều khiển đẩy task vào hàng đợi. [[1](https://github.com/taskiq-python/taskiq)]

python
    
    
    # cli.py
    import click
    import asyncio
    from tasks import crawl_chapter
    
    @click.group()
    def cli():
        """CLI quản lý hệ thống cào truyện."""
        pass
    
    @cli.command()
    @click.option("--url", prompt="URL chương truyện cần cào", help="Đường dẫn đến chương truyện.")
    def add_task(url: str):
        """Gửi lệnh cào 1 chương truyện xuống worker qua Taskiq."""
        async def send():
            # Đẩy task bất đồng bộ vào hàng đợi
            task = await crawl_chapter.kiq(url=url)
            click.echo(f"Đã gửi task {task.task_id} cho URL: {url}")
    
        asyncio.run(send())
    
    if __name__ == "__main__":
        cli()
    

Hãy thận trọng khi sử dụng mã.

Cách chạy hệ thống

  1. **Khởi động Redis server** trên máy tính của bạn.

  2. **Chạy Worker** để lắng nghe và thực hiện task:

bash
         
         taskiq worker broker:broker -fsd
         

Hãy thận trọng khi sử dụng mã.

  3. **Dùng CLI Producer** để ra lệnh cào truyện:

bash
         
         python cli.py add-task --url "https://example.com"
         

Hãy thận trọng khi sử dụng mã.

[[1](https://taskiq-python.github.io/guide/getting-started.html)]




Bạn có muốn tôi bổ sung thêm **chức năng cào danh sách (pagination)** hay **lưu nội dung truyện vào cơ sở dữ liệu SQLite** không?

