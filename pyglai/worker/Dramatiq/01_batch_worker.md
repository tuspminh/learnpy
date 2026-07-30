Xây dựng hệ thống cào truyện bằng [Dramatiq](https://github.com/bogdanp/dramatiq) và [Click](https://github.com/pallets/click) gồm các bước: cài đặt thư viện, định nghĩa tác vụ cào (actor) xử lý ngầm, và thiết lập giao diện dòng lệnh (CLI) để đẩy việc vào hàng đợi. [[1](https://github.com/bogdanp/dramatiq), [2](https://click.palletsprojects.com/)]

Cài đặt thư viện

Chạy lệnh sau để cài đặt Dramatiq (dùng Redis làm broker) và Click: [[1](https://realpython.com/python-click/), [2](https://github.com/bogdanp/dramatiq)]

bash
    
    
    pip install "dramatiq[redis,watch]" click requests
    

Hãy thận trọng khi sử dụng mã.

1\. File định nghĩa Worker (`tasks.py`)

File này cấu hình kết nối Redis và định nghĩa tác vụ (`actor`) cào dữ liệu từ trang truyện: [[1](https://oneuptime.com/blog/post/2026-01-24-python-task-queues-dramatiq/view), [2](https://github.com/bogdanp/dramatiq)]

python
    
    
    # tasks.py
    import dramatiq
    from dramatiq.brokers.redis import RedisBroker
    import requests
    
    # Kết nối tới Redis Broker chạy ở localhost port 6379
    redis_broker = RedisBroker(host="localhost", port=6379)
    dramatiq.set_broker(redis_broker)
    
    @dramatiq.actor
    def crawl_chapter(chapter_url: str):
        """Tác vụ cào một chapter truyện chạy ngầm"""
        print(f"Bắt đầu cào URL: {chapter_url}")
        try:
            response = requests.get(chapter_url, timeout=10)
            # Xử lý nội dung HTML cào được ở đây (ví dụ: lưu vào database)
            print(f"Cào thành công: {chapter_url} (Độ dài: {len(response.text)} ký tự)")
        except Exception as e:
            print(f"Lỗi khi cào {chapter_url}: {e}")
            raise e
    

Hãy thận trọng khi sử dụng mã.

2\. File Producer dùng Click CLI (`producer.py`)

File này dùng thư viện `click` để tạo lệnh trên terminal, giúp ra lệnh cho worker bằng cách đẩy (`send`) URL cần cào vào hàng đợi: [[1](https://click.palletsprojects.com/), [2](https://github.com/bogdanp/dramatiq)]

python
    
    
    # producer.py
    import click
    from tasks import crawl_chapter
    
    @click.group()
    def cli():
        """Hệ thống CLI điều khiển Worker cào truyện"""
        pass
    
    @cli.command()
    @click.option('--url', '-u', required=True, help='Đường dẫn (URL) của chapter truyện cần cào.')
    def add_task(url):
        """Đẩy 1 URL chapter vào hàng đợi cào truyện."""
        crawl_chapter.send(url)
        click.echo(click.style(f"Đã thêm task cào cho URL: {url}", fg="green"))
    
    @cli.command()
    @click.option('--file', '-f', type=click.File('r'), required=True, help='File chứa danh sách URL, mỗi dòng 1 URL.')
    def add_batch(file):
        """Đẩy hàng loạt URL từ file văn bản vào hàng đợi."""
        count = 0
        for line in file:
            url = line.strip()
            if url:
                crawl_chapter.send(url)
                count += 1
        click.echo(click.style(f"Đã thêm {count} task vào hàng đợi từ file.", fg="green"))
    
    if __name__ == '__main__':
        cli()
    

Hãy thận trọng khi sử dụng mã.

3\. Cách chạy hệ thống

Mở 2 cửa sổ terminal riêng biệt:

  * **Terminal 1 (Khởi động Worker để chạy ngầm)** :

bash
        
        dramatiq tasks
        

Hãy thận trọng khi sử dụng mã.

[[1](https://github.com/bogdanp/dramatiq)]
  * **Terminal 2 (Dùng CLI do Click cung cấp để ra lệnh cào)** :
    * Cào một truyện đơn lẻ:

bash
          
          python producer.py add-task --url https://example.com
          

Hãy thận trọng khi sử dụng mã.

    * Cào hàng loạt từ file danh sách (`urls.txt`):

bash
          
          python producer.py add-batch --file urls.txt
          

Hãy thận trọng khi sử dụng mã.

[[1](https://github.com/bogdanp/dramatiq), [2](https://click.palletsprojects.com/)]



Để hiểu rõ hơn về cách cấu hình các actor và cơ chế chạy ngầm của Dramatiq:

