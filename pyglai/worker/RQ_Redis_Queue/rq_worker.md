Xây dựng hệ thống cào truyện bằng **Python** , sử dụng **requests** và **BeautifulSoup4** để xử lý dữ liệu, **RQ (Redis Queue)** làm hàng đợi tác vụ ngầm, và **Click** làm công cụ dòng lệnh (CLI) để đẩy lệnh cào vào queue. [[1](https://click.palletsprojects.com/), [2](https://codelearn.io/sharing/python-crawl-du-lieu-tao-bai-bao-nhanh?srsltid=AfmBOopwau7Bk2re18x8QBRAPJtTCOzf_3LoDm_EkBhsgMKIE8mgLAHD), [3](https://translate.google.com/translate?u=https://python-rq.org/&hl=vi&sl=en&tl=vi&client=sge), [4](https://python-rq.org/docs/)]

* * *

1\. Cài đặt thư viện

Chạy lệnh sau để cài đặt các gói cần thiết:

bash
    
    
    pip install redis rq requests beautifulsoup4 click
    

Hãy thận trọng khi sử dụng mã.

_Lưu ý: Bạn cần chạy sẵn một server Redis trên máy hoặc qua Docker._ [[1](https://www.twilio.com/en-us/blog/developers/tutorials/building-blocks/first-task-rq-redis-python)]

* * *

2\. Hàm cào truyện (`tasks.py`)

File này chứa logic dùng `requests` và `BeautifulSoup4` để cào nội dung truyện từ một URL cụ thể và chạy ngầm bởi RQ worker. [[1](https://redis.io/glossary/redis-queue/)]

python
    
    
    # tasks.py
    import requests
    from bs4 import BeautifulSoup
    
    def scrape_chapter(url):
        print(f"Bắt đầu cào URL: {url}")
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Thay đổi selector tùy thuộc vào cấu trúc website truyện thực tế
            title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "Không có tiêu đề"
            content = soup.find('div', class_='chapter-content').get_text(strip=True) if soup.find('div', class_='chapter-content') else "Không có nội dung"
            
            print(f"Đã cào xong: {title} (Độ dài nội dung: {len(content)} ký tự)")
            # Ở đây bạn có thể lưu vào Database (MongoDB, PostgreSQL, v.v.)
            
            return {"title": title, "status": "success"}
        except Exception as e:
            print(f"Lỗi khi cào {url}: {str(e)}")
            return {"url": url, "status": "error", "message": str(e)}
    

Hãy thận trọng khi sử dụng mã.

* * *

3\. Chạy Worker

Khởi động worker để lắng nghe hàng đợi `default` từ Redis: [[1](https://www.cybrosys.com/blog/how-to-use-rq-redis-queue-worker-to-queue-your-task-in-python)]

bash
    
    
    rq worker default
    

Hãy thận trọng khi sử dụng mã.

* * *

4\. Producer CLI bằng Click (`producer.py`)

File này tạo giao diện dòng lệnh (CLI) bằng `click`, nhận lệnh từ người dùng và đẩy tác vụ `scrape_chapter` vào hàng đợi Redis Queue. [[1](https://click.palletsprojects.com/), [2](https://python-rq.org/docs/)]

python
    
    
    # producer.py
    import click
    from redis import Redis
    from rq import Queue
    from tasks import scrape_chapter
    
    # Kết nối Redis và khởi tạo Queue
    redis_conn = Redis(host='localhost', port=6379, db=0)
    q = Queue(connection=redis_conn)
    
    @click.group()
    def cli():
        """Hệ thống CLI điều khiển Worker cào truyện"""
        pass
    
    @cli.command()
    @click.option('--url', '-u', required=True, help='Đường dẫn URL của chương truyện cần cào.')
    def add_job(url):
        """Đẩy một task cào truyện vào hàng đợi Redis."""
        job = q.enqueue(scrape_chapter, url)
        click.echo(f"Đã thêm task thành công! Job ID: {job.id}")
    
    if __name__ == '__main__':
        cli()
    

Hãy thận trọng khi sử dụng mã.

* * *

5\. Cách sử dụng

  1. Cào một chương truyện mới thông qua CLI bằng cách truyền URL:

bash
         
         python producer.py add_job --url "https://example.com"
         

Hãy thận trọng khi sử dụng mã.

  2. Xem trợ giúp của lệnh CLI:

bash
         
         python producer.py --help
         

Hãy thận trọng khi sử dụng mã.




Nếu bạn muốn mở rộng, bạn có thể cho tôi biết:

  * Bạn có cần tính năng **cào tự động danh sách chương** (dùng một URL mục lục rồi tự tách ra nhiều task nhỏ) không?
  * Hay bạn muốn **lưu trực tiếp dữ liệu vào Database** loại nào (MongoDB, SQLite, MySQL)?



