# Khóa học Click Deep Dive

# Buổi 8: `click.Context (ctx)` \- Trái tim của ứng dụng Click

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu `click.Context` là gì. 
>   * Biết vì sao gần như mọi ứng dụng Click lớn đều dùng `ctx`. 
>   * Sử dụng `@click.pass_context`. 
>   * Truyền dữ liệu giữa Root Group, Sub Group và Command. 
>   * Sử dụng `ctx.obj` để chia sẻ Config, Logger, Database, Service. 
>   * Chuẩn bị nền tảng cho Dependency Injection và Plugin Architecture. 
> 


* * *

# 1\. Vì sao cần Context?

Giả sử bạn có CLI:
    
    
    story
    
    ├── crawler
    │      start
    │      stop
    │
    ├── db
    │      backup
    │      restore
    │
    └── config

Mỗi command đều cần:

  * Config 
  * Logger 
  * Database 
  * HTTP Client 
  * Cache 



Ví dụ:
    
    
    db = Database(...)
    logger = Logger(...)
    config = Config(...)

Bạn sẽ làm thế nào?

* * *

## Cách 1 (Sai)
    
    
    @crawler.command()
    def start():
        config = load_config()
        logger = Logger()
        db = Database()

Command khác:
    
    
    @db.command()
    def backup():
        config = load_config()
        logger = Logger()
        db = Database()

Mỗi command đều tạo lại.

Đây là thiết kế rất tệ.

* * *

# 2\. Ý tưởng của Context

Click tạo ra một **Context Object**.

Bạn có thể hình dung:
    
    
    CLI
    
    ↓
    
    Context
    
    ↓
    
    Config
    
    ↓
    
    Logger
    
    ↓
    
    Database
    
    ↓
    
    Services
    
    ↓
    
    Commands

Context giống như một **chiếc ba lô**.

Bạn bỏ mọi thứ vào.

Command nào cũng lấy được.

* * *

# 3\. Context là gì?

Khi Click chạy:
    
    
    story crawler start

Nó tạo:
    
    
    ctx = click.Context(...)

Object này chứa:

  * Command hiện tại 
  * Parent 
  * Tham số 
  * Dữ liệu người dùng (`ctx.obj`) 
  * Metadata 



* * *

# 4\. Lấy Context
    
    
    import click
    
    @click.command()
    @click.pass_context
    def hello(ctx):
        click.echo(ctx)

Chạy:
    
    
    python app.py

Kết quả:
    
    
    <click.core.Context object at ...>

* * *

# 5\. `@click.pass_context`

Decorator này yêu cầu Click truyền `Context` vào hàm.
    
    
    @click.pass_context
    def hello(ctx):

Nếu không có:
    
    
    def hello():

Bạn sẽ không truy cập được Context.

* * *

# 6\. `ctx.info_name`
    
    
    @click.command()
    @click.pass_context
    def hello(ctx):
        click.echo(ctx.info_name)

Kết quả:
    
    
    hello

Đây là tên command đang chạy.

* * *

# 7\. `ctx.command`
    
    
    @click.pass_context
    def hello(ctx):
        click.echo(ctx.command.name)

↓
    
    
    hello

* * *

# 8\. `ctx.parent`

Ví dụ:
    
    
    story
    
    ↓
    
    crawler
    
    ↓
    
    start

Trong command `start`:
    
    
    ctx.parent

chính là Context của:
    
    
    crawler

Còn:
    
    
    ctx.parent.parent

là:
    
    
    story

Context tạo thành một cây giống CLI.

* * *

# 9\. `ctx.obj`

Đây là thứ quan trọng nhất.

Click dành riêng:
    
    
    ctx.obj

để lưu dữ liệu của bạn.

Ví dụ:
    
    
    ctx.obj = {}

* * *

# 10\. Ví dụ đầu tiên
    
    
    import click
    
    @click.group()
    @click.pass_context
    def cli(ctx):
        ctx.obj = {
            "username": "admin"
        }
    
    @cli.command()
    @click.pass_context
    def whoami(ctx):
        click.echo(ctx.obj["username"])
    
    if __name__ == "__main__":
        cli()

Chạy:
    
    
    python app.py whoami

↓
    
    
    admin

* * *

# 11\. Truyền Config

Thay vì:
    
    
    config = load_config()

làm một lần:
    
    
    @click.group()
    @click.pass_context
    def cli(ctx):
    
        ctx.obj = {
            "config": load_config()
        }

Command:
    
    
    @click.pass_context
    def backup(ctx):
    
        config = ctx.obj["config"]

Không cần đọc file cấu hình nhiều lần.

* * *

# 12\. Truyền Logger
    
    
    ctx.obj = {
    
        "logger": logger
    }

Command:
    
    
    logger = ctx.obj["logger"]
    
    logger.info(...)

* * *

# 13\. Truyền Database
    
    
    ctx.obj = {
    
        "database": db
    }

Command:
    
    
    db = ctx.obj["database"]

Không cần:
    
    
    Database(...)

ở mọi command.

* * *

# 14\. Truyền nhiều đối tượng
    
    
    ctx.obj = {
    
        "config": config,
    
        "logger": logger,
    
        "database": database,
    
        "cache": cache
    }

Command:
    
    
    cfg = ctx.obj["config"]
    
    db = ctx.obj["database"]
    
    logger = ctx.obj["logger"]

* * *

# 15\. Ví dụ Story CLI
    
    
    import click
    
    @click.group()
    @click.pass_context
    def cli(ctx):
    
        ctx.obj = {
    
            "database": "story.db",
    
            "threads": 4
        }
    
    @cli.group()
    def crawler():
        pass
    
    @crawler.command()
    @click.pass_context
    def start(ctx):
    
        click.echo(ctx.obj["database"])
    
        click.echo(ctx.obj["threads"])
    
    if __name__ == "__main__":
        cli()

CLI
    
    
    python app.py crawler start

↓
    
    
    story.db
    
    4

* * *

# 16\. `ctx.ensure_object()`

Thay vì
    
    
    ctx.obj = {}

nên dùng
    
    
    ctx.ensure_object(dict)

Ví dụ:
    
    
    @click.group()
    @click.pass_context
    def cli(ctx):
    
        ctx.ensure_object(dict)
    
        ctx.obj["debug"] = True

Ưu điểm:

Nếu `obj` chưa tồn tại

↓

Click tự tạo.

* * *

# 17\. `invoke_without_command`

Nếu chạy
    
    
    story

Group mặc định chỉ hiện Help.

Có thể đổi:
    
    
    @click.group(
        invoke_without_command=True
    )

Ví dụ
    
    
    @click.group(
        invoke_without_command=True
    )
    @click.pass_context
    def cli(ctx):
    
        if ctx.invoked_subcommand is None:
            click.echo("Welcome Story CLI")

CLI
    
    
    story

↓
    
    
    Welcome Story CLI

* * *

# 18\. `ctx.invoked_subcommand`

Cho biết command nào được gọi.

Ví dụ
    
    
    story crawler

Trong Root:
    
    
    ctx.invoked_subcommand

↓
    
    
    crawler

Nếu
    
    
    story db backup

Root thấy:
    
    
    db

Group `db` sẽ thấy:
    
    
    backup

* * *

# 19\. Thiết kế chuyên nghiệp

Thay vì:
    
    
    ctx.obj = {
    
        "config": config,
    
        "database": database,
    
        "logger": logger,
    
        "cache": cache,
    
        "http": client,
    
        "plugin": plugin_manager
    }

nên tạo một lớp.
    
    
    class AppContext:
    
        def __init__(self):
    
            self.config = ...
    
            self.logger = ...
    
            self.database = ...

Sau đó:
    
    
    ctx.obj = AppContext()

Command:
    
    
    app = ctx.obj
    
    app.logger.info(...)
    
    app.database.connect()

Đây là cách mà các dự án lớn thường sử dụng vì có kiểu dữ liệu rõ ràng, dễ mở rộng và dễ kiểm tra hơn việc lưu nhiều khóa trong một `dict`.

* * *

# 20\. Mini Project

## app_context.py
    
    
    class AppContext:
    
        def __init__(self):
    
            self.database = "story.db"
    
            self.threads = 4
    
            self.debug = True

* * *

## app.py
    
    
    import click
    
    from app_context import AppContext
    
    @click.group()
    @click.pass_context
    def cli(ctx):
    
        ctx.obj = AppContext()
    
    @cli.group()
    def crawler():
        pass
    
    @crawler.command()
    @click.pass_context
    def start(ctx):
    
        app = ctx.obj
    
        click.echo(app.database)
    
        click.echo(app.threads)
    
        click.echo(app.debug)
    
    if __name__ == "__main__":
        cli()

CLI
    
    
    python app.py crawler start

↓
    
    
    story.db
    
    4
    
    True

* * *

# 21\. Những lỗi người mới thường gặp

### ❌ Dùng biến toàn cục
    
    
    config = {}
    logger = None
    database = None

Sau đó mọi nơi đều truy cập biến toàn cục.

Điều này làm ứng dụng khó kiểm thử và khó chạy nhiều phiên bản khác nhau.

Hãy truyền dữ liệu qua `ctx.obj`.

* * *

### ❌ Mỗi command tự tạo Database
    
    
    @cli.command()
    def backup():
    
        db = Database(...)

Nên:
    
    
    db = ctx.obj.database

Khởi tạo một lần ở Root Group và tái sử dụng.

* * *

### ❌ Dùng `dict` quá lâu

Khi dự án còn nhỏ:
    
    
    ctx.obj = {}

là đủ.

Khi số lượng dữ liệu tăng lên, nên chuyển sang:
    
    
    ctx.obj = AppContext()

để có cấu trúc rõ ràng và được IDE hỗ trợ tự động hoàn thành (autocomplete).

* * *

# 22\. Tổng kết

Các API quan trọng:

API| Mục đích  
---|---  
`@click.pass_context`| Truyền `Context` vào command  
`ctx.obj`| Chia sẻ dữ liệu  
`ctx.ensure_object(dict)`| Đảm bảo `obj` tồn tại  
`ctx.parent`| Context cha  
`ctx.command`| Command hiện tại  
`ctx.invoked_subcommand`| Subcommand đang được gọi  
  
Kiến trúc chuẩn:
    
    
    CLI
    
    ↓
    
    Root Group
    
    ↓
    
    AppContext
    
    ├── Config
    ├── Logger
    ├── Database
    ├── Cache
    ├── HTTP Client
    └── Plugin Manager
    
    ↓
    
    Commands
    
    ↓
    
    Services
    
    ↓
    
    Repositories

* * *

# Bài tập thực hành

## Bài 1

Tạo `ctx.obj` là một `dict` chứa:

  * `username`
  * `database`
  * `debug`



Viết lệnh:
    
    
    python app.py info

để in ba giá trị này.

* * *

## Bài 2

Thay `dict` bằng lớp:
    
    
    class AppContext:
        ...

và cập nhật command `info` để truy cập thuộc tính của lớp.

* * *

## Bài 3

Tạo CLI:
    
    
    story crawler start

Trong `start`, in ra:

  * Đường dẫn cơ sở dữ liệu. 
  * Số luồng (`threads`). 



Lấy tất cả từ `ctx.obj`.

* * *

## Bài 4

Sử dụng:
    
    
    @click.group(invoke_without_command=True)

để khi chạy:
    
    
    story

chương trình hiển thị:
    
    
    Welcome to Story CLI

Nếu có subcommand thì không in thông báo này.

* * *

## Bài 5 (Mini Project)

Xây dựng lớp:
    
    
    class AppContext:
        config
        logger
        database
        http_client
        plugin_manager

Hiện tại các thuộc tính có thể là chuỗi hoặc đối tượng giả lập (mock). Khởi tạo `AppContext` ở Root Group, lưu vào `ctx.obj` và viết các lệnh:
    
    
    story config show
    story db info
    story plugin list

để lấy dữ liệu từ cùng một `AppContext`.

* * *

# Chuẩn bị cho buổi 9

Ở **Buổi 9** , chúng ta sẽ tìm hiểu **Context nâng cao** :

  * `@click.pass_obj`
  * `click.make_pass_decorator()`
  * Tạo `AppContext` có kiểu dữ liệu mạnh (strongly typed). 
  * Chia sẻ service giữa các module. 
  * Thiết kế theo **Dependency Injection** thay vì truy cập trực tiếp `ctx`. 



Đây là kỹ thuật được nhiều dự án Click quy mô lớn sử dụng để giữ cho command ngắn gọn, dễ kiểm thử và dễ bảo trì.

