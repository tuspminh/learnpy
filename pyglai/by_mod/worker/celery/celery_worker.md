Xây dựng hệ thống cào truyện phân tán gồm 3 thành phần chính: **Celery Worker** xử lý cào ngầm, **Click CLI Producer** ra lệnh điều phối, và **Redis** làm Message Broker. [[1](https://cybersoft.edu.vn/xu-ly-tac-vu-nen-voi-celery-trong-python-huong-dan-cho-back-end/), [2](https://viblo.asia/p/tim-hieu-ve-celery-1VgZv4dr5Aw)]

1\. Cài đặt thư viện

Chạy lệnh cài đặt các gói cần thiết qua pip: [[1](https://scrapeops.io/web-scraping-playbook/celery-rabbitmq-scraper-scheduling/), [2](https://scrapfly.io/blog/posts/web-scraping-with-python-beautifulsoup)]

bash
    
    
    pip install celery redis requests beautifulsoup4 click
    

Hãy thận trọng khi sử dụng mã.

2\. File cấu hình Celery (`celery_app.py`)

Khởi tạo ứng dụng Celery kết nối với Redis: [[1](https://cybersoft.edu.vn/xu-ly-tac-vu-nen-voi-celery-trong-python-huong-dan-cho-back-end/), [2](https://scrapeops.io/web-scraping-playbook/celery-rabbitmq-scraper-scheduling/)]

python
    
    
    from celery import Celery
    
    app = Celery(
        'comic_scraper',
        broker='redis://localhost:6379/0',
        backend='redis://localhost:6379/0'
    )
    

Hãy thận trọng khi sử dụng mã.

3\. File định nghĩa Task Cào Truyện (`tasks.py`)

Sử dụng `requests` và `beautifulsoup4` để phân tích HTML cào tiêu đề và nội dung truyện: [[1](https://realpython.com/beautiful-soup-web-scraper-python/), [2](https://www.geeksforgeeks.org/python/implementing-web-scraping-python-beautiful-soup/)]

python
    
    
    import requests
    from bs4 import BeautifulSoup
    from celery_app import app
    
    @app.task(name='tasks.scrape_chapter')
    def scrape_chapter(url: str):
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Thay đổi selector tùy thuộc vào website cấu trúc truyện thực tế
                title = soup.find('h1').get_text(strip=True) if soup.find('h1') else 'No Title'
                content = soup.find('div', class_='chapter-content').get_text() if soup.find('div', class_='chapter-content') else 'No Content'
                
                print(f"Đã cào xong: {title}")
                return {'url': url, 'title': title, 'length': len(content)}
            return {'error': f"Status code: {response.status_code}"}
        except Exception as e:
            return {'error': str(e)}
    

Hãy thận trọng khi sử dụng mã.

4\. File điều khiển CLI Producer (`cli.py`)

Dùng thư viện `click` để tạo lệnh điều hướng đẩy task vào hàng đợi của Celery:

python
    
    
    import click
    from tasks import scrape_chapter
    
    @click.group()
    def cli():
        """CLI quản lý worker cào truyện"""
        pass
    
    @cli.command()
    @click.option('--url', prompt='Link chương truyện cần cào', help='URL trang chi tiết chương truyện.')
    def crawl(url):
        """Gửi task cào một URL đơn lẻ xuống Worker."""
        click.echo(f"Đang gửi URL {url} vào hàng đợi Celery...")
        result = scrape_chapter.delay(url)
        click.echo(f"Task ID: {result.id} đã được khởi tạo.")
    
    if __name__ == '__main__':
        cli()
    

Hãy thận trọng khi sử dụng mã.

5\. Hướng dẫn chạy hệ thống

  * **Khởi động Celery Worker:**

bash
        
        celery -A tasks worker --loglevel=INFO
        

Hãy thận trọng khi sử dụng mã.

  * **Sử dụng CLI Producer ra lệnh:**

bash
        
        python cli.py crawl --url https://example.com
        

Hãy thận trọng khi sử dụng mã.

[[1](https://docs.celeryq.dev/en/stable/userguide/workers.html)]




Xem video hướng dẫn chi tiết cách kết hợp Celery và BeautifulSoup để tối ưu hiệu suất xử lý tác vụ cào dữ liệu:

