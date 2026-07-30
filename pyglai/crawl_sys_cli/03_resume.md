Để nâng cấp tính năng **tạm dừng (Pause)** và **cào tiếp (Resume)** một cách chính xác, chúng ta sẽ tích hợp một cơ sở dữ liệu **SQLite** nhỏ (có sẵn trong Python, không cần cài đặt thêm).

SQLite sẽ đóng vai trò là "bộ nhớ" lưu lại tiến độ: truyện nào đang cào, dừng ở chương mấy, và danh sách các chương còn lại để khi quay lại có thể cào tiếp ngay lập tức.

* * *

1\. Cấu trúc mã nguồn mới

Chúng ta sẽ cập nhật lại toàn bộ 2 file `tasks.py` và `cli.py`.

📝 File 1: `tasks.py` (Worker cập nhật tiến độ vào SQLite)

Cập nhật để worker đọc danh sách chương từ DB và cập nhật số chương đã cào thành công.

python
    
    
    import time
    import sqlite3
    from celery import Celery
    
    app = Celery('crawl_worker', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
    DB_NAME = "crawler_status.db"
    
    def get_db():
        conn = sqlite3.connect(DB_NAME)
        return conn, conn.cursor()
    
    @app.task(bind=True)
    def scrape_novel_task(self, novel_url):
        """Worker xử lý cào truyện dựa trên dữ liệu trong DB"""
        conn, cursor = get_db()
        
        # Lấy thông tin task từ DB dựa vào URL
        cursor.execute("SELECT id, current_chapter, total_chapters, status FROM tasks WHERE url = ?", (novel_url,))
        task_data = cursor.fetchone()
        
        if not task_data:
            print("[!] Không tìm thấy cấu hình task trong DB.")
            return "Error"
            
        task_id, current_chap, total_chaps, status = task_data
        print(f"[*] Khởi động cào truyện. Tiến độ hiện tại: {current_chap}/{total_chaps}")
    
        # Giả lập danh sách URL các chương (Thực tế bạn sẽ cào danh sách này từ novel_url)
        chapters = [f"{novel_url}/chap-{i}" for i in range(1, total_chaps + 1)]
    
        # Chạy vòng lặp từ chương chưa cào (current_chap) đến hết
        for index in range(current_chap, total_chaps):
            
            # 🚨 KIỂM TRA LỆNH DỪNG: Check trạng thái trong DB trước khi cào chương tiếp theo
            # Nếu CLI đã đổi trạng thái thành 'paused', worker sẽ tự thoát vòng lặp
            cursor.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
            current_status = cursor.fetchone()[0]
            if current_status == 'paused':
                print(f"[!] Nhận lệnh DỪNG từ CLI. Worker dừng ở chương {index}.")
                conn.close()
                return "Paused"
    
            # Giả lập hành động cào dữ liệu chương truyện
            chap_url = chapters[index]
            print(f"-> Đang cào: {chap_url}")
            time.sleep(3) # Giả lập cào mất 3 giây mỗi chương
    
            # Cào xong 1 chương -> Cập nhật ngay lập tức vào SQLite
            new_progress = index + 1
            cursor.execute(
                "UPDATE tasks SET current_chapter = ?, status = 'running' WHERE id = ?", 
                (new_progress, task_id)
            )
            conn.commit()
    
        # Sau khi chạy hết vòng lặp thành công
        cursor.execute("UPDATE tasks SET status = 'completed' WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        print("[+] Đã hoàn thành toàn bộ truyện!")
        return "Completed"
    

Hãy thận trọng khi sử dụng mã.

📝 File 2: `cli.py` (CLI điều khiển Pause / Resume)

CLI mới sẽ quản lý vòng đời của Task thông qua DB thay vì gọi lệnh `revoke` ép buộc của Celery. Điều này giúp tránh việc mất dữ liệu khi đang ghi dở dang.

python
    
    
    import click
    import sqlite3
    from tasks import scrape_novel_task
    
    DB_NAME = "crawler_status.db"
    
    def init_db():
        """Tạo bảng lưu trạng thái nếu chưa có"""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                current_chapter INTEGER DEFAULT 0,
                total_chapters INTEGER,
                status TEXT DEFAULT 'pending' -- pending, running, paused, completed
            )
        ''')
        conn.commit()
        conn.close()
    
    def get_db():
        conn = sqlite3.connect(DB_NAME)
        return conn, conn.cursor()
    
    @click.group()
    def cli():
        """Hệ thống CLI Crawler quản lý Trạng thái chạy ngầm (SQLite + Celery)"""
        init_db()
    
    @cli.command()
    @click.argument('url')
    @click.option('--chaps', default=10, help='Số lượng chương giả định cần cào')
    def scrape(url, chaps):
        """Bắt đầu tạo một tác vụ cào truyện mới"""
        conn, cursor = get_db()
        try:
            # Thêm truyện mới vào DB, mặc định có 10 chương, bắt đầu từ chương 0
            cursor.execute(
                "INSERT INTO tasks (url, total_chapters, status) VALUES (?, ?, 'running')", 
                (url, chaps)
            )
            conn.commit()
            
            # Kích hoạt worker ngầm xử lý
            scrape_novel_task.delay(url)
            click.secho(f"🚀 Đã thêm và kích hoạt cào truyện: {url}", fg="green")
        except sqlite3.IntegrityError:
            click.secho("❌ Truyện này đã tồn tại trong hệ thống. Hãy dùng lệnh 'resume' hoặc 'status'.", fg="yellow")
        finally:
            conn.close()
    
    @cli.command()
    @click.argument('url')
    def stop(url):
        """Tạm dừng một tác vụ cào đang chạy"""
        conn, cursor = get_db()
        cursor.execute("SELECT status FROM tasks WHERE url = ?", (url,))
        row = cursor.fetchone()
        
        if not row:
            click.echo("❌ Không tìm thấy truyện này.")
        elif row[0] != 'running':
            click.echo(f"❌ Truyện không ở trạng thái chạy (Trạng thái hiện tại: {row[0]})")
        else:
            # Đổi trạng thái thành paused. Worker chạy ngầm đọc được tín hiệu này sẽ tự dừng lại
            cursor.execute("UPDATE tasks SET status = 'paused' WHERE url = ?", (url,))
            conn.commit()
            click.secho(f"🛑 Đã phát lệnh TẠM DỪNG cào truyện: {url}", fg="red")
            click.echo("Worker sẽ dừng lại an toàn sau khi cào xong chương hiện tại.")
        conn.close()
    
    @cli.command()
    @click.argument('url')
    def resume(url):
        """Cào tiếp truyện đang bị tạm dừng"""
        conn, cursor = get_db()
        cursor.execute("SELECT current_chapter, total_chapters, status FROM tasks WHERE url = ?", (url,))
        row = cursor.fetchone()
        
        if not row:
            click.echo("❌ Không tìm thấy truyện này để cào tiếp.")
        elif row[2] == 'completed':
            click.echo("🎉 Truyện này đã cào xong toàn bộ trước đó rồi!")
        elif row[2] == 'running':
            click.echo("⚠️ Truyện này vẫn đang được cào ngầm, không cần resume.")
        else:
            # Đổi trạng thái từ paused quay lại running
            cursor.execute("UPDATE tasks SET status = 'running' WHERE url = ?", (url,))
            conn.commit()
            
            # Gọi lại worker ngầm chạy tiếp từ chương cũ
            scrape_novel_task.delay(url)
            click.secho(f"🔄 Đã kích hoạt CÀO TIẾP từ chương {row[0]} cho truyện: {url}", fg="cyan")
        conn.close()
    
    @cli.command()
    def status():
        """Xem danh sách các truyện và tiến độ cào chi tiết"""
        conn, cursor = get_db()
        cursor.execute("SELECT id, url, current_chapter, total_chapters, status FROM tasks")
        rows = cursor.fetchall()
        
        if not rows:
            click.echo("Chưa có tác vụ nào trong danh sách.")
            return
            
        click.secho(f"{'ID':<4} | {'Trạng thái':<10} | {'Tiến độ':<10} | {'URL truyện'}", bold=True)
        click.echo("-" * 60)
        for row in rows:
            progress = f"{row[2]}/{row[3]}"
            click.echo(f"{row[0]:<4} | {row[4]:<10} | {progress:<10} | {row[1]}")
        conn.close()
    
    if __name__ == '__main__':
        cli()
    

Hãy thận trọng khi sử dụng mã.

* * *

2\. Kịch bản chạy thử nghiệm thực tế

Bạn hãy khởi động Celery worker ở Terminal 1 trước:

bash
    
    
    celery -A tasks worker --loglevel=info
    

Hãy thận trọng khi sử dụng mã.

Sau đó qua Terminal 2 sử dụng CLI:

**Bước 1: Bắt đầu cào một truyện mới (Ví dụ giả định bộ này có 8 chương)**

bash
    
    
    python cli.py scrape http://truyen.com --chaps 8
    

Hãy thận trọng khi sử dụng mã.

_Bạn sẽ thấy Worker bắt đầu in: Đang cào chap-1, chap-2, chap-3..._

**Bước 2: Kiểm tra bảng tiến độ**

bash
    
    
    python cli.py status
    

Hãy thận trọng khi sử dụng mã.

_Kết quả sẽ hiển thị bảng tiến độ cập nhật liên tục theo thời gian thực (ví dụ`2/8`)._

**Bước 3: Ra lệnh tạm dừng khi worker đang cào**

bash
    
    
    python cli.py stop http://truyen.com
    

Hãy thận trọng khi sử dụng mã.

_Lúc này CLI đổi trạng thái DB thành`paused`. Worker cào nốt chương hiện tại rồi sẽ tự động thoát in ra dòng `[!] Nhận lệnh DỪNG từ CLI`._

**Bước 4: Ra lệnh CÀO TIẾP**

bash
    
    
    python cli.py resume http://truyen.com
    

Hãy thận trọng khi sử dụng mã.

_Worker nhận lệnh mới, kiểm tra DB thấy tiến độ đang dừng ở đâu (ví dụ chương 4), nó sẽ tự động cào tiếp từ`chap-5` trở đi mà không cần cào lại từ đầu._

* * *

Nếu bạn muốn đóng gói ứng dụng này thành một lệnh duy nhất toàn hệ thống (gõ `crawl scrape ...` thay vì `python cli.py scrape ...`), tôi có thể hướng dẫn bạn cấu hình file **`setup.py`** để cài đặt nó vào hệ thống. Bạn có cần bước này không?

