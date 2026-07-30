Để xây dựng hệ thống này bằng **Python** , giải pháp tối ưu và nhanh nhất là kết hợp **Click** (làm CLI) và **Celery** (làm Worker chạy ngầm) trên nền **Redis**. [[1](https://realpython.com/python-click/), [2](https://www.guvi.in/blog/important-python-backend-technologies/), [3](https://dbader.org/blog/installing-python-and-pip-on-windows-10)]

Dưới đây là hướng dẫn chi tiết và mã nguồn mẫu hoàn chỉnh để bạn triển khai hệ thống quản lý cào dữ liệu truyện (novel/chapter).

* * *

1\. Chuẩn bị môi trường

Cài đặt Redis trên máy của bạn (hoặc chạy qua Docker). Sau đó cài các thư viện Python sau: [[1](https://eugeneyan.com/writing/setting-up-python-project-for-automation-and-collaboration/), [2](https://docs.threatconnect.com/en/latest/tcex/building_apps_quickstart.html)]

bash
    
    
    pip install click celery redis requests beautifulsoup4
    

Hãy thận trọng khi sử dụng mã.

* * *

2\. Cấu trúc mã nguồn

Tạo một thư mục dự án với 2 file chính:

  * `tasks.py`: Chứa mã nguồn của Worker chạy ngầm và các hàm cào dữ liệu.
  * `cli.py`: Chứa mã nguồn giao diện dòng lệnh CLI. [[1](https://medium.com/stinopys/running-your-first-cython-code-b223297fe61b)]



📝 File 1: `tasks.py` (Worker chạy ngầm)

File này định nghĩa các tác vụ cào dữ liệu và quản lý trạng thái qua Redis. [[1](https://pypi.org/project/tasks-py/)]

python
    
    
    import time
    from celery import Celery
    import requests
    from bs4 import BeautifulSoup
    
    # Khởi tạo Celery kết nối tới Redis
    app = Celery('crawl_worker', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
    
    @app.task(bind=True)
    def scrape_novel(self, novel_url):
        """Tác vụ cào toàn bộ truyện"""
        print(f"[*] Bắt đầu cào truyện từ: {novel_url}")
        
        # Giả lập danh sách 5 chương cần cào
        chapters = [f"{novel_url}/chap-1", f"{novel_url}/chap-2", f"{novel_url}/chap-3", f"{novel_url}/chap-4", f"{novel_url}/chap-5"]
        
        for index, chap_url in enumerate(chapters):
            # 🚨 KIỂM TRA TRẠNG THÁI: Trước khi cào chương mới, check xem có lệnh dừng không
            # Celery cho phép kiểm tra trạng thái của chính task đó qua Redis
            state = self.app.AsyncResult(self.request.id).state
            if state == 'REVOKED':
                print(f"[!] Tác vụ đã bị dừng bởi người dùng tại chương {index}")
                return "Paused"
                
            print(f"-> Đang cào: {chap_url}")
            # Giả lập thời gian cào dữ liệu bằng requests & bs4
            time.sleep(3) 
            
            # Cập nhật tiến độ vào metadata của Celery để CLI có thể check
            self.update_state(state='PROGRESS', meta={'current': index + 1, 'total': len(chapters)})
    
        print("[+] Hoàn thành cào truyện!")
        return "Completed"
    
    @app.task
    def scrape_chapter(chapter_url):
        """Tác vụ cào nhanh 1 chương đơn lẻ"""
        print(f"[*] Đang cào đơn lẻ chương: {chapter_url}")
        time.sleep(2)
        print("[+] Đã cào xong chương.")
        return "Done"
    

Hãy thận trọng khi sử dụng mã.

📝 File 2: `cli.py` (Ứng dụng CLI điều khiển) [[1](https://dev.to/alexmercedcoder/an-introduction-to-python-6l4)]

File này định nghĩa các lệnh CLI để tương tác với Worker.

python
    
    
    import click
    from celery.result import AsyncResult
    from tasks import app as celery_app, scrape_novel, scrape_chapter
    import redis
    import json
    
    # Kết nối Redis để lưu trữ ID của các task đang chạy ngầm
    r = redis.Redis(host='localhost', port=6379, db=1)
    TASK_KEY = "current_crawl_task"
    
    @click.group()
    def cli():
        """Hệ thống CLI quản lý Crawler Worker chạy ngầm."""
        pass
    
    @cli.command()
    def run():
        """Khởi động Worker chạy ngầm (Hướng dẫn user)"""
        click.echo("Để chạy worker ngầm, hãy mở một Terminal mới và chạy lệnh:")
        click.secho("celery -A tasks worker --loglevel=info", fg="green", bold=True)
    
    @cli.command()
    @click.argument('url')
    def scrape(url):
        """Bắt đầu cào một truyện từ URL.
        Ví dụ: crawl scrape http://example.com
        """
        if "/chapter" in url or "/chap" in url:
            # Cào 1 chương
            task = scrape_chapter.delay(url)
            click.echo(f"🚀 Đã gửi lệnh cào chương ngầm. Task ID: {task.id}")
        else:
            # Cào cả bộ truyện
            task = scrape_novel.delay(url)
            # Lưu lại Task ID vào Redis để các lệnh stop, status sau này biết đường điều khiển
            r.set(TASK_KEY, task.id)
            click.echo(f"🚀 Đã gửi lệnh cào truyện ngầm. Task ID: {task.id}")
    
    @cli.command()
    def stop():
        """Dừng tác vụ cào hiện tại ngay lập tức"""
        task_id = r.get(TASK_KEY)
        if not task_id:
            click.echo("❌ Không có tác vụ cào nào đang chạy.")
            return
            
        task_id = task_id.decode('utf-8')
        # Gửi lệnh revoke (hủy) tới Celery Worker ngầm
        celery_app.control.revoke(task_id, terminate=True)
        click.secho(f"🛑 Đã phát lệnh DỪNG tác vụ cào truyện (ID: {task_id}).", fg="red")
    
    @cli.command()
    def status():
        """Kiểm tra tiến độ cào hiện tại"""
        task_id = r.get(TASK_KEY)
        if not task_id:
            click.echo("Không có thông tin tác vụ.")
            return
            
        task_id = task_id.decode('utf-8')
        res = AsyncResult(task_id, app=celery_app)
        
        click.echo(f"Trạng thái Task: {res.state}")
        if res.state == 'PROGRESS':
            click.echo(f"Tiến độ: {res.info.get('current')}/{res.info.get('total')} chương.")
        elif res.state == 'SUCCESS':
            click.echo("🎉 Tác vụ trước đó đã hoàn thành thành công!")
    
    if __name__ == '__main__':
        cli()
    

Hãy thận trọng khi sử dụng mã.

* * *

3\. Cách vận hành hệ thống

Bạn mở **2 cửa sổ Terminal** song song:

**Terminal 1: Khởi động Worker chạy ngầm**  
Để worker luôn luôn trực chiến nhận lệnh, bạn chạy lệnh sau (đúng như lệnh trong `crawl run` gợi ý):

bash
    
    
    celery -A tasks worker --loglevel=info
    

Hãy thận trọng khi sử dụng mã.

_(Worker này sẽ chạy liên tục dưới nền để chờ lệnh)._

**Terminal 2: Dùng CLI để ra lệnh**  
Bây giờ bạn có thể dùng CLI để điều khiển thoải mái:

  1. **Ra lệnh cào bộ truyện:**

bash
         
         python cli.py scrape http://example.com
         

Hãy thận trọng khi sử dụng mã.

_Kết quả:_ Bạn sẽ thấy bên Terminal 1 của Worker bắt đầu in ra dòng chữ cào từng chương.
  2. **Kiểm tra tiến độ bằng CLI:**

bash
         
         python cli.py status
         

Hãy thận trọng khi sử dụng mã.

  3. **Ra lệnh DỪNG cào ngay lập tức:**

bash
         
         python cli.py stop
         

Hãy thận trọng khi sử dụng mã.

_Kết quả:_ Worker bên Terminal 1 sẽ dừng vòng lặp cào truyện lại ngay lập tức.



* * *

💡 Cách nâng cấp lên "Cào tiếp" (Resume)

Để làm được tính năng **Cào tiếp** , thay vì dựa hoàn toàn vào Celery, bạn nên tạo một cơ sở dữ liệu nhỏ (ví dụ dùng thư viện `sqlite3` có sẵn trong Python).

  * Khi nhấn `stop`, lưu lại URL truyện và `chương hiện tại` (ví dụ: Chương 15) vào SQLite.
  * Khi gõ `python cli.py resume`, CLI sẽ đọc từ SQLite xem truyện này đang dừng ở chương 15, sau đó gọi hàm `scrape_novel.delay(url, start_chapter=16)`.



Bạn có cần tôi viết thêm phần **tích hợp SQLite** để lưu trạng thái đóng/mở và tính năng **resume (cào tiếp)** này không?

