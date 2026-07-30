# Khóa học Click Deep Dive

# Buổi 11: Command Lifecycle & Callback - Vòng đời của một ứng dụng Click

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu toàn bộ vòng đời (Lifecycle) của một ứng dụng Click. 
>   * Biết callback của `Group` được gọi khi nào. 
>   * Hiểu `invoke_without_command=True`. 
>   * Sử dụng `ctx.invoked_subcommand`. 
>   * Khởi tạo tài nguyên (Config, Logger, Database, HTTP Client...) đúng thời điểm. 
>   * Chuẩn bị nền tảng cho Resource Management ở các buổi sau. 
> 


* * *

# 1\. Vòng đời của một CLI

Khi người dùng gõ:
    
    
    story crawler start --threads 8

Nhiều người nghĩ Click sẽ chạy ngay:
    
    
    start()

Thực tế không phải.

Click trải qua nhiều bước.
    
    
    Người dùng
    
    ↓
    
    Phân tích argv
    
    ↓
    
    Tìm Root Group
    
    ↓
    
    Tạo Context
    
    ↓
    
    Gọi Callback của Root Group
    
    ↓
    
    Tìm Subcommand
    
    ↓
    
    Tạo Context mới
    
    ↓
    
    Gọi Callback của Sub Group
    
    ↓
    
    Thực thi Command
    
    ↓
    
    Kết thúc chương trình

Hiểu được vòng đời này là chìa khóa để thiết kế CLI chuyên nghiệp.

* * *

# 2\. Root Group Callback

Ví dụ:
    
    
    import click
    
    @click.group()
    def cli():
        click.echo("Root callback")
    
    @cli.command()
    def hello():
        click.echo("Hello")
    
    if __name__ == "__main__":
        cli()

Chạy:
    
    
    python app.py hello

Kết quả:
    
    
    Root callback
    Hello

Điều quan trọng:

> Callback của `Group` luôn chạy trước command.

* * *

# 3\. Có nhiều Group
    
    
    @click.group()
    def cli():
        click.echo("Root")
    
    @cli.group()
    def crawler():
        click.echo("Crawler")
    
    @crawler.command()
    def start():
        click.echo("Start")

CLI:
    
    
    python app.py crawler start

Kết quả:
    
    
    Root
    Crawler
    Start

Ta thấy:
    
    
    Root
    
    ↓
    
    Crawler
    
    ↓
    
    Command

Đây chính là vòng đời theo từng cấp của cây lệnh.

* * *

# 4\. Callback dùng để làm gì?

Đây là nơi thích hợp để:

  * Đọc file cấu hình. 
  * Tạo Logger. 
  * Mở Database. 
  * Khởi tạo HTTP Client. 
  * Tạo Cache. 
  * Khởi tạo Plugin Manager. 



Ví dụ:
    
    
    @click.group()
    @click.pass_context
    def cli(ctx):
    
        ctx.obj = AppContext()
    
        click.echo("Config loaded")
    
        click.echo("Database connected")

Sau đó mọi command đều dùng lại các đối tượng đã khởi tạo.

* * *

# 5\. Không nên khởi tạo trong Command

Sai:
    
    
    @cli.command()
    def backup():
    
        db = Database()
    
        db.connect()

Nếu có 20 command:

↓

20 lần tạo `Database`.

* * *

Đúng:
    
    
    @click.group()
    @click.pass_context
    def cli(ctx):
    
        ctx.obj = AppContext()
    
        ctx.obj.db = Database()

Command:
    
    
    @pass_app
    def backup(app):
    
        app.db.backup()

Database chỉ khởi tạo một lần.

* * *

# 6\. `invoke_without_command=True`

Thông thường:
    
    
    story

↓

Click chỉ hiện:
    
    
    Usage...

* * *

Có thể thay đổi:
    
    
    @click.group(
        invoke_without_command=True
    )

Ví dụ:
    
    
    @click.group(
        invoke_without_command=True
    )
    @click.pass_context
    def cli(ctx):
    
        if ctx.invoked_subcommand is None:
            click.echo("Welcome Story CLI")

CLI:
    
    
    story

↓
    
    
    Welcome Story CLI

Không cần viết command riêng.

* * *

# 7\. `ctx.invoked_subcommand`

Ví dụ:
    
    
    story crawler start

Trong Root Group:
    
    
    ctx.invoked_subcommand

↓
    
    
    crawler

Nếu:
    
    
    story db backup

↓
    
    
    db

Điều này rất hữu ích khi muốn thực hiện các hành động khác nhau tùy theo nhóm lệnh được gọi.

* * *

# 8\. Ví dụ thực tế
    
    
    @click.group(
        invoke_without_command=True
    )
    @click.pass_context
    def cli(ctx):
    
        if ctx.invoked_subcommand is None:
    
            click.echo("Dashboard")
    
        else:
    
            click.echo(
                f"Preparing {ctx.invoked_subcommand}"
            )

CLI:
    
    
    story crawler

↓
    
    
    Preparing crawler

CLI:
    
    
    story

↓
    
    
    Dashboard

* * *

# 9\. Thứ tự thực thi nhiều Group

Ví dụ:
    
    
    story
    
    ↓
    
    crawler
    
    ↓
    
    job
    
    ↓
    
    run

Thứ tự callback:
    
    
    Root
    
    ↓
    
    Crawler
    
    ↓
    
    Job
    
    ↓
    
    Run

Mỗi Group có thể chuẩn bị tài nguyên riêng.

* * *

# 10\. Lifecycle của Story CLI
    
    
    CLI
    
    ↓
    
    Root Callback
    │
    ├── Config
    ├── Logger
    ├── Database
    └── HttpClient
    
    ↓
    
    Crawler Callback
    │
    ├── Scheduler
    └── Queue
    
    ↓
    
    Start Command
    
    ↓
    
    CrawlerService.start()

Đây là kiến trúc thường thấy trong các ứng dụng CLI quy mô lớn.

* * *

# 11\. Dùng `ctx.obj` trong Callback
    
    
    @click.group()
    @click.pass_context
    def cli(ctx):
    
        ctx.obj = AppContext()
    
        ctx.obj.debug = True

Subcommand:
    
    
    @pass_app
    def info(app):
    
        click.echo(app.debug)

Mọi command đều dùng chung một đối tượng.

* * *

# 12\. Logging Lifecycle

Sai:
    
    
    @cli.command()
    def backup():
    
        logger = Logger()

Đúng:
    
    
    @click.group()
    @click.pass_context
    def cli(ctx):
    
        ctx.obj.logger = Logger()

Command:
    
    
    @pass_app
    def backup(app):
    
        app.logger.info("Backup")

Logger tồn tại suốt vòng đời của lần chạy CLI.

* * *

# 13\. Database Lifecycle
    
    
    Program Start
    
    ↓
    
    Database.connect()
    
    ↓
    
    Commands
    
    ↓
    
    Database.close()
    
    ↓
    
    Exit

Không nên:
    
    
    connect()
    
    backup()
    
    close()
    
    connect()
    
    restore()
    
    close()

Trong cùng một lần chạy.

* * *

# 14\. Cleanup tài nguyên

Click không tự động đóng mọi tài nguyên do bạn tạo.

Ví dụ:
    
    
    try:
        app.db.connect()
    
        ...
    
    finally:
        app.db.close()

Hoặc thiết kế `AppContext` có phương thức:
    
    
    class AppContext:
    
        def close(self):
    
            self.db.close()

Sau này chúng ta sẽ học các kỹ thuật quản lý tài nguyên nâng cao hơn.

* * *

# 15\. Mini Project

## app_context.py
    
    
    from dataclasses import dataclass
    
    @dataclass
    class AppContext:
    
        database: str = ""
    
        debug: bool = False

* * *

## app.py
    
    
    import click
    
    from app_context import AppContext
    
    pass_app = click.make_pass_decorator(AppContext)
    
    @click.group(
        invoke_without_command=True
    )
    @click.pass_context
    def cli(ctx):
    
        ctx.obj = AppContext(
            database="story.db",
            debug=True
        )
    
        if ctx.invoked_subcommand is None:
    
            click.echo("Welcome Story CLI")
    
        else:
    
            click.echo("Loading application...")

* * *
    
    
    @cli.command()
    @pass_app
    def info(app):
    
        click.echo(app.database)
    
        click.echo(app.debug)

CLI:
    
    
    python app.py info

↓
    
    
    Loading application...
    story.db
    True

* * *

CLI:
    
    
    python app.py

↓
    
    
    Welcome Story CLI

* * *

# 16\. Kiến trúc được khuyến nghị
    
    
    app.py
    │
    ├── Root Callback
    │      │
    │      ├── Load Config
    │      ├── Create Logger
    │      ├── Connect Database
    │      ├── Create HttpClient
    │      └── Create AppContext
    │
    ├── Commands
    │
    ├── Services
    │
    └── Repositories

Root Group chịu trách nhiệm **khởi tạo**.

Command chịu trách nhiệm **điều phối**.

Service chịu trách nhiệm **nghiệp vụ**.

* * *

# 17\. Những lỗi người mới thường gặp

## ❌ Callback chứa nghiệp vụ

Sai:
    
    
    @click.group()
    def cli():
    
        crawl_all()

Root Callback không nên thực hiện nghiệp vụ.

Nó chỉ nên chuẩn bị môi trường.

* * *

## ❌ Command khởi tạo tài nguyên

Sai:
    
    
    @cli.command()
    def export():
    
        logger = Logger()
    
        db = Database()

Điều này làm lặp mã và tăng chi phí khởi tạo.

* * *

## ❌ Không dùng `ctx.invoked_subcommand`

Khi bật:
    
    
    invoke_without_command=True

nhưng không kiểm tra:
    
    
    ctx.invoked_subcommand

bạn có thể vô tình hiển thị thông báo chào ngay cả khi người dùng đang chạy một command cụ thể.

* * *

# 18\. Tổng kết

Các API quan trọng:

API| Vai trò  
---|---  
`invoke_without_command=True`| Cho phép callback chạy khi không có command  
`ctx.invoked_subcommand`| Biết subcommand nào sẽ được thực thi  
Callback của Group| Khởi tạo tài nguyên  
`ctx.obj`| Chia sẻ tài nguyên  
`@click.pass_obj`| Nhận `AppContext` trực tiếp  
  
Vòng đời:
    
    
    CLI
    
    ↓
    
    Root Callback
    
    ↓
    
    Sub Group Callback
    
    ↓
    
    Command
    
    ↓
    
    Service
    
    ↓
    
    Repository
    
    ↓
    
    Database
    
    ↓
    
    Cleanup
    
    ↓
    
    Exit

* * *

# Bài tập thực hành

## Bài 1

Tạo Root Group với:
    
    
    invoke_without_command=True

Khi chạy:
    
    
    python app.py

hiển thị:
    
    
    Welcome to Story CLI

* * *

## Bài 2

In giá trị của:
    
    
    ctx.invoked_subcommand

để quan sát sự khác nhau giữa:
    
    
    python app.py
    python app.py info
    python app.py db

* * *

## Bài 3

Khởi tạo `AppContext` trong Root Callback với:

  * `database = "story.db"`
  * `debug = True`
  * `threads = 8`



Viết command `info` để đọc các giá trị đó.

* * *

## Bài 4

Tạo Group:
    
    
    story crawler start

In ra thứ tự callback:
    
    
    Root callback
    Crawler callback
    Start command

* * *

## Bài 5 (Mini Project)

Xây dựng vòng đời cho **Story CLI** :

  * Root Callback: 
    * Đọc cấu hình. 
    * Tạo `Logger`. 
    * Tạo `Database`. 
    * Tạo `HttpClient`. 
    * Tạo `AppContext`. 
  * Group `crawler`: 
    * Chuẩn bị hàng đợi (queue) và scheduler (mô phỏng). 
  * Command `start`: 
    * Gọi `CrawlerService.start()` (mô phỏng). 



Mỗi bước chỉ cần `click.echo()` để mô phỏng hoạt động.

* * *

# Chuẩn bị cho buổi 12

Ở **Buổi 12** , chúng ta sẽ đi sâu vào **Parameter System** của Click, một trong những phần mạnh mẽ nhất của thư viện:

  * `click.Parameter`
  * `click.Argument`
  * `click.Option`
  * `click.ParameterSource`
  * Giá trị mặc định động (dynamic defaults) 
  * Validation và callback cho tham số 
  * Thiết kế CLI thân thiện và dễ sử dụng 



Sau buổi này, bạn sẽ hiểu cách Click phân tích và xử lý tham số ở mức nội bộ, thay vì chỉ biết sử dụng các decorator cơ bản. Đây là nền tảng để xây dựng các CLI có khả năng kiểm tra đầu vào mạnh mẽ và linh hoạt.

