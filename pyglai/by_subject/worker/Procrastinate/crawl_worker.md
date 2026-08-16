Xây dựng hệ thống cào truyện bằng Python sử dụng **Procrastinate** (lưu queue qua PostgreSQL), **Click** làm CLI điều phối, cùng **Requests** và **BeautifulSoup4** để xử lý HTML. [[1](https://click.palletsprojects.com/), [2](https://www.linkedin.com/pulse/why-i-use-procrastinate-postgres-background-tasks-raman-sapezhka-bhowf), [3](https://codelearn.io/sharing/web-crawling-voi-beautifulsoup4-python?srsltid=AfmBOorbKGjxrc01Ujwg5FDM4v1X0HbQpQzo0p_d96tmJFFkM7wEAf_x), [4](https://codelearn.io/sharing/python-crawl-du-lieu-tao-bai-bao-nhanh?srsltid=AfmBOoqC6tRYxvG9peTXL3gq6WmEEsVBNjDXcEsO48p2UaOK87CvI55M)]

* * *

1\. Cài đặt thư viện

Chạy lệnh sau để cài đặt các gói cần thiết:

bash
    
    
    pip install procrastinate[psycopg] click requests beautifulsoup4
    

Hãy thận trọng khi sử dụng mã.

2\. File cấu hình ứng dụng (`app.py`)

Khởi tạo kết nối PostgreSQL cho [Procrastinate](https://procrastinate.readthedocs.io/): [[1](https://procrastinate.readthedocs.io/en/stable/quickstart.html), [2](https://www.linkedin.com/pulse/why-i-use-procrastinate-postgres-background-tasks-raman-sapezhka-bhowf)]

python
    
    
    # app.py
    import procrastinate
    
    # Thay đổi thông số kết nối DB của bạn
    connector = procrastinate.PsycopgConnector(
        conninfo="postgres://postgres:password@localhost:5432/crawldb"
    )
    
    app = procrastinate.App(connector=connector)
    

Hãy thận trọng khi sử dụng mã.

_Khởi tạo schema DB lần đầu bằng lệnh:_ `procrastinate --app=app.app schema --apply` [[1](https://procrastinate.readthedocs.io/en/stable/quickstart.html)]

3\. File định nghĩa tác vụ cào dữ liệu (`tasks.py`)

Sử dụng `requests` và `beautifulsoup4` để phân tích nội dung truyện: [[1](https://codelearn.io/sharing/python-crawl-du-lieu-tao-bai-bao-nhanh?srsltid=AfmBOoqC6tRYxvG9peTXL3gq6WmEEsVBNjDXcEsO48p2UaOK87CvI55M), [2](https://codelearn.io/sharing/web-crawling-voi-beautifulsoup4-python?srsltid=AfmBOorbKGjxrc01Ujwg5FDM4v1X0HbQpQzo0p_d96tmJFFkM7wEAf_x)]

python
    
    
    # tasks.py
    from .app import app
    import requests
    from bs4 import BeautifulSoup
    
    @app.task(queue="story_queue")
    def crawl_chapter(url: str):
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Ví dụ cấu trúc HTML (Cần thay đổi selector theo web thực tế)
            title = soup.find("h1").get_text(strip=True)
            content = soup.find("div", class_="chapter-content").get_text("\n", strip=True)
            
            print(f"Đã cào xong: {title}")
            # Lưu kết quả vào Database ở đây tùy theo nhu cầu dự án
        else:
            print(f"Lỗi tải trang: {url}")
    

Hãy thận trọng khi sử dụng mã.

4\. File điều phối Producer CLI (`cli.py`)

Dùng thư viện [Click](https://click.palletsprojects.com/) để tạo lệnh đẩy tác vụ vào hàng đợi: [[1](https://click.palletsprojects.com/), [2](https://www.geeksforgeeks.org/python/click-module-in-python-making-awesome-command-line-utilities/)]

python
    
    
    # cli.py
    import click
    from .tasks import crawl_chapter
    from .app import app
    
    @click.group()
    def cli():
        """Hệ thống CLI điều phối cào truyện."""
        pass
    
    @cli.command()
    @click.option("--url", prompt="Link chương truyện cần cào", help="URL của trang web cần lấy dữ liệu.")
    def add_job(url):
        """Đẩy một link chương truyện vào hàng đợi cho worker xử lý."""
        with app.open():
            job_id = crawl_chapter.defer(url=url)
            click.echo(f"Đã thêm job #{job_id} cho URL: {url}")
    
    if __name__ == "__main__":
        cli()
    

Hãy thận trọng khi sử dụng mã.

5\. Cách vận hành hệ thống

  * **Khởi chạy Worker** (lắng nghe hàng đợi từ PostgreSQL):

bash
        
        procrastinate --app=app.app worker -q story_queue
        

Hãy thận trọng khi sử dụng mã.

  * **Ra lệnh từ Producer CLI** :

bash
        
        python cli.py add-job --url "https://example.com"
        

Hãy thận trọng khi sử dụng mã.

[[1](https://www.linkedin.com/pulse/why-i-use-procrastinate-postgres-background-tasks-raman-sapezhka-bhowf), [2](https://procrastinate.readthedocs.io/en/stable/howto/basics/worker.html)]




Nếu bạn cần thêm tính năng **tự động cào danh sách chương (pagination)** hay **lưu nội dung trực tiếp vào bảng PostgreSQL** , hãy cho tôi biết cấu trúc HTML trang web mẫu hoặc yêu cầu cụ thể của bạn!

