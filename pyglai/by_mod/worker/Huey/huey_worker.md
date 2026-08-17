Xây dựng hệ thống cào truyện gồm 3 tệp chính: cấu hình **Huey** kết nối Redis, **Worker** định nghĩa hàm cào bằng `requests` và `BeautifulSoup`, cùng **CLI Producer** dùng `click` để ra lệnh. [[1](https://huey.readthedocs.io/), [2](https://railway.com/deploy/huey), [3](https://pypi.org/project/huey/)]

Cấu trúc dự án

  * `config.py`: Khởi tạo đối tượng Huey.

  * `tasks.py`: Viết các tác vụ cào dữ liệu.

  * `cli.py`: Giao diện dòng lệnh bằng Click để đẩy job.




* * *

Cài đặt thư viện

bash
    
    
    pip install huey requests beautifulsoup4 click redis
    

Hãy thận trọng khi sử dụng mã.

* * *

1\. `config.py` \- Cấu hình Huey

python
    
    
    from huey import RedisHuey
    
    # Kết nối tới Redis chạy ở localhost port 6379
    huey = RedisHuey('story_crawler', host='localhost', port=6379)
    

Hãy thận trọng khi sử dụng mã.

* * *

2\. `tasks.py` \- Định nghĩa Worker Task cào truyện

python
    
    
    import requests
    from bs4 import BeautifulSoup
    from config import huey
    
    @huey.task()
    def crawl_chapter(url: str):
        """Task chạy ngầm dưới worker để cào nội dung chương truyện"""
        print(f"Đang cào URL: {url}")
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Tùy chỉnh Selector theo trang truyện thực tế
                title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No title"
                content = soup.find('div', class_='chapter-content').get_text('\n', strip=True) if soup.find('div', class_='chapter-content') else "No content"
                
                # Lưu trữ hoặc in ra kết quả mô phỏng
                print(f"Đã cào xong: {title} ({len(content)} ký tự)")
                return {"title": title, "url": url}
            else:
                print(f"Lỗi HTTP: {response.status_code}")
        except Exception as e:
            print(f"Lỗi khi cào {url}: {e}")
    

Hãy thận trọng khi sử dụng mã.

* * *

3\. `cli.py` \- Producer điều khiển bằng Click

python
    
    
    import click
    from tasks import crawl_chapter
    
    @click.group()
    def cli():
        """Hệ thống CLI điều khiển Crawler truyện"""
        pass
    
    @cli.command()
    @click.option('--url', prompt='Link chương truyện cần cào', help='URL của trang cần cào dữ liệu.')
    def add_task(url):
        """Gửi 1 link chương truyện vào hàng đợi Huey"""
        task = crawl_chapter(url)
        click.echo(f"Đã đưa task vào hàng đợi thành công! Task ID: {task.id}")
    
    if __name__ == '__main__':
        cli()
    

Hãy thận trọng khi sử dụng mã.

* * *

Cách vận hành hệ thống

  1. **Khởi động Redis** trên máy của bạn.

  2. **Chạy Worker (Consumer)** để lắng nghe và thực thi task:

bash
         
         huey_consumer tasks.huey
         

Hãy thận trọng khi sử dụng mã.

  3. **Dùng CLI (Producer)** để ra lệnh cào từ terminal:

bash
         
         python cli.py add-task --url "https://example.com"
         

Hãy thận trọng khi sử dụng mã.

[[1](https://www.untangled.dev/2020/07/01/huey-minimal-task-queue-django/), [2](https://www.reddit.com/r/django/comments/198imzv/need_huey_help/), [3](https://huey.readthedocs.io/en/latest/guide.html), [4](https://railway.com/deploy/huey), [5](https://pypi.org/project/huey/)]




Nếu bạn cần tính năng **cào tự động danh sách (pagination)** hoặc **lưu vào cơ sở dữ liệu (SQLite/MongoDB)** , hãy cho tôi biết để bổ sung chi tiết.

