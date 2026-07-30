Xây dựng hệ thống cào truyện gồm 3 tệp chính: tệp cấu hình tác vụ ngầm (**tasks.py**), tệp giao diện dòng lệnh gửi lệnh (**producer.py**), và tệp chạy cào dữ liệu qua **requests** kết hợp **BeautifulSoup**.

Cài đặt thư viện

  * Cài đặt các gói cần thiết bằng lệnh: `pip install dramatiq[redis] requests beautifulsoup4 click`

  * Khởi động một Message Broker (ví dụ Redis chạy ở `localhost:6379`). [[1](https://realpython.com/python-click/), [2](https://thejeshgn.com/2025/10/30/simple-and-easy-background-tasks-with-dramatiq/), [3](https://github.com/Bogdanp/dramatiq/issues/431)]




1\. Tệp định nghĩa tác vụ (tasks.py)

Tệp này cấu hình môi trường Dramatiq, sử dụng Redis làm broker, và viết hàm cào truyện với `requests`, `BeautifulSoup`. [[1](https://codelearn.io/sharing/python-crawl-du-lieu-tao-bai-bao-nhanh?srsltid=AfmBOoqJySAJQUZ5ipDSYYKY4jGN1E_-Wdh6CWwxte5HHzwf6qdn4pDL), [2](https://thejeshgn.com/2025/10/30/simple-and-easy-background-tasks-with-dramatiq/)]

python
    
    
    import dramatiq
    from dramatiq.brokers.redis import RedisBroker
    import requests
    from bs4 import BeautifulSoup
    
    # Kết nối broker Redis
    redis_broker = RedisBroker(url="redis://127.0.0.1:6379/0")
    dramatiq.set_broker(redis_broker)
    
    @dramatiq.actor(max_retries=3)
    def crawl_story_chapter(url: str):
        """Tác vụ ngầm cào nội dung chương truyện."""
        print(f"[Worker] Bắt đầu cào URL: {url}")
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Ví dụ tìm tiêu đề và nội dung (thay đổi selector theo trang thực tế)
            title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "No Title"
            content = soup.find("div", class_="chapter-content")
            content_text = content.get_text(separator="\n", strip=True) if content else "No Content"
            
            print(f"[Worker] Cào thành công: {title} ({len(content_text)} ký tự)")
            # Xử lý lưu database hoặc file ở đây tại worker
            
        except Exception as e:
            print(f"[Worker] Lỗi khi cào {url}: {e}")
            raise e
    

Hãy thận trọng khi sử dụng mã.

2\. Tệp điều khiển Producer CLI (producer.py)

Sử dụng thư viện `click` để tạo dòng lệnh đẩy tác vụ `crawl_story_chapter.send(url)` vào hàng đợi của Dramatiq. [[1](https://click.palletsprojects.com/en/stable/quickstart/), [2](https://thejeshgn.com/2025/10/30/simple-and-easy-background-tasks-with-dramatiq/)]

python
    
    
    import click
    from tasks import crawl_story_chapter
    
    @click.group()
    def cli():
        """Hệ thống Producer CLI điều khiển Worker cào truyện."""
        pass
    
    @cli.command()
    @click.option("--url", "-u", required=True, help="Đường dẫn URL của chương truyện cần cào.")
    def crawl(url):
        """Gửi lệnh yêu cầu worker cào một chương truyện."""
        click.echo(f"[Producer] Đang đưa URL vào hàng đợi: {url}")
        crawl_story_chapter.send(url)
        click.echo("[Producer] Đã gửi lệnh thành công vào Dramatiq!")
    
    if __name__ == "__main__":
        cli()
    

Hãy thận trọng khi sử dụng mã.

3\. Cách chạy hệ thống

  * **Khởi chạy Worker** xử lý hàng đợi bằng lệnh CLI của Dramatiq:  
`dramatiq tasks`

  * **Gửi lệnh cào** từ Producer CLI:  
`python producer.py crawl --url https://example.com` [[1](https://click.palletsprojects.com/en/stable/quickstart/), [2](https://dramatiq.io/guide.html), [3](https://thejeshgn.com/2025/10/30/simple-and-easy-background-tasks-with-dramatiq/), [4](https://medium.com/@rahulmadan_18191/why-not-click-for-cli-using-python-e70c41c4539a)]




Nếu bạn cần bổ sung **lưu dữ liệu vào Database** (như SQLite/PostgreSQL) hay **cơ chế cào đệ quy tự động lấy danh sách chương** , hãy cho tôi biết thêm chi tiết!

