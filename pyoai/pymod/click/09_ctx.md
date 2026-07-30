# Khóa học Click Deep Dive

# Buổi 9: Context (`ctx`) trong Click - Truyền dữ liệu xuyên suốt Command Tree

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu bản chất `click.Context`. 
>   * Biết Context được tạo như thế nào trong Nested Command. 
>   * Sử dụng `@click.pass_context`. 
>   * Hiểu `ctx.parent`. 
>   * Sử dụng `ctx.obj` để chia sẻ trạng thái. 
>   * Thiết kế `AppContext` cho CLI lớn. 
>   * Chuẩn bị nền tảng cho Config, Database, Plugin Architecture. 
> 


* * *

# 1\. Vấn đề của Nested Command

Buổi trước chúng ta có:
    
    
    story
    
    └── crawler
    
           └── start

Chạy:
    
    
    story crawler start

Bây giờ giả sử:

`story` cần:

  * config file 
  * logger 
  * database 



`crawler` cần:

  * crawler config 
  * http client 



`start` cần:

  * crawler service 



Câu hỏi:

Làm sao truyền dữ liệu từ:
    
    
    story

xuống:
    
    
    crawler

và:
    
    
    start

?

* * *

# 2\. Context giải quyết vấn đề này

Click tạo ra một Context cho mỗi command.

Ví dụ:
    
    
    story crawler start

Click tạo:
    
    
    Context Root
    
    story
     |
     |
    Context Crawler
    
    crawler
     |
     |
    Context Command
    
    start

Mỗi Context biết:

  * command hiện tại 
  * command cha 
  * tham số 
  * dữ liệu dùng chung 



* * *

# 3\. Context Tree

Ví dụ:
    
    
    ctx_story
    
    
        |
        |
        v
    
    
    ctx_crawler
    
    
        |
        |
        v
    
    
    ctx_start

Quan hệ:
    
    
    ctx_start.parent
    
            ↓
    
    ctx_crawler.parent
    
            ↓
    
    ctx_story

* * *

# 4\. Lấy Context bằng `pass_context`

Ví dụ:
    
    
    import click
    
    
    @click.command()
    @click.pass_context
    def hello(ctx):
    
        click.echo(ctx)
    
    
    if __name__ == "__main__":
        hello()

Kết quả:
    
    
    <click.core.Context object>

* * *

`ctx` chính là:
    
    
    click.Context

* * *

# 5\. Xem thông tin Context

Ví dụ:
    
    
    @click.command()
    @click.pass_context
    def hello(ctx):
    
        print(ctx.command)
    
        print(ctx.info_name)

Kết quả:
    
    
    <Command hello>
    hello

* * *

# 6\. Context trong Nested Command

Ví dụ:
    
    
    import click
    
    
    @click.group()
    @click.pass_context
    def cli(ctx):
    
        print("ROOT")
    
    
    @cli.group()
    @click.pass_context
    def crawler(ctx):
    
        print("CRAWLER")
    
    
    @crawler.command()
    @click.pass_context
    def start(ctx):
    
        print("START")
    
    
    if __name__ == "__main__":
        cli()

Chạy:
    
    
    python app.py crawler start

Kết quả:
    
    
    ROOT
    CRAWLER
    START

* * *

Click đi qua từng Context.

* * *

# 7\. `ctx.parent`

Trong command `start`:
    
    
    @crawler.command()
    @click.pass_context
    def start(ctx):
    
        print(ctx.parent)

`ctx.parent` chính là:
    
    
    crawler Context

* * *

Ví dụ:
    
    
    @start
    def start(ctx):
    
        parent = ctx.parent
    
        print(parent.info_name)

Kết quả:
    
    
    crawler

* * *

# 8\. `ctx.obj` là gì?

`ctx.obj` là nơi chúng ta lưu dữ liệu ứng dụng.

Ví dụ:
    
    
    ctx.obj = {
        "name": "Story CLI"
    }

Sau đó command con lấy ra.

* * *

# 9\. Chia sẻ dữ liệu từ Root

Ví dụ:
    
    
    import click
    
    
    @click.group()
    @click.pass_context
    def cli(ctx):
    
        ctx.obj = {
            "version": "1.0"
        }
    
    
    @cli.command()
    @click.pass_context
    def info(ctx):
    
        print(ctx.obj["version"])
    
    
    if __name__ == "__main__":
        cli()

Chạy:
    
    
    python app.py info

Kết quả:
    
    
    1.0

* * *

# 10\. Context trong Nested Command

Ví dụ:
    
    
    @click.group()
    @click.pass_context
    def cli(ctx):
    
        ctx.obj = {
            "app": "Story"
        }
    
    
    @cli.group()
    @click.pass_context
    def crawler(ctx):
    
        print(ctx.obj)
    
    
    @crawler.command()
    @click.pass_context
    def start(ctx):
    
        print(ctx.obj)

Chạy:
    
    
    story crawler start

Kết quả:
    
    
    {'app':'Story'}
    
    {'app':'Story'}

Dữ liệu đi xuyên suốt cây.

* * *

# 11\. AppContext thay vì dict

Không nên:
    
    
    ctx.obj = {
        "database": db,
        "logger": logger
    }

Vì:

  * khó đọc 
  * dễ sai key 
  * IDE không hỗ trợ tốt 



Nên:
    
    
    class AppContext:
    
        def __init__(self):
    
            self.database = None
    
            self.logger = None

* * *

# 12\. Tạo AppContext

File:
    
    
    context.py

* * *
    
    
    class AppContext:
    
        def __init__(self):
    
            self.config = {}
    
            self.database = None
    
            self.logger = None

* * *

# 13\. Khởi tạo ở Root

app.py
    
    
    import click
    
    from context import AppContext
    
    
    @click.group()
    @click.pass_context
    def cli(ctx):
    
        ctx.obj = AppContext()
    
    
    if __name__ == "__main__":
        cli()

* * *

Bây giờ mọi command đều có:
    
    
    ctx.obj

là:
    
    
    AppContext

* * *

# 14\. Command sử dụng AppContext
    
    
    @cli.command()
    @click.pass_context
    def info(ctx):
    
        app = ctx.obj
    
        print(app.config)

* * *

# 15\. Với Nested Command

Cấu trúc:
    
    
    story
    
    └── crawler
    
           └── start

* * *

Root:
    
    
    ctx.obj = AppContext()

* * *

Crawler:
    
    
    @cli.group()
    def crawler():
        pass

* * *

Start:
    
    
    @crawler.command()
    @click.pass_context
    def start(ctx):
    
        app = ctx.obj
    
        print(app)

* * *

Tất cả dùng chung:
    
    
    AppContext

* * *

# 16\. `ensure_object()`

Một cách an toàn:
    
    
    @click.group()
    @click.pass_context
    def cli(ctx):
    
        ctx.ensure_object(dict)

Nếu:
    
    
    ctx.obj

chưa có:

Click tạo:
    
    
    {}

* * *

Ví dụ:
    
    
    ctx.ensure_object(dict)
    
    ctx.obj["debug"] = True

* * *

# 17\. `pass_obj`

Nếu chỉ cần `obj`:

Thay vì:
    
    
    @click.pass_context
    def start(ctx):
    
        app = ctx.obj

Dùng:
    
    
    @click.pass_obj
    def start(app):
    
        print(app)

Ngắn hơn.

* * *

# 18\. `make_pass_decorator`

Với dự án lớn:
    
    
    class AppContext:
        pass

Tạo:
    
    
    pass_app = click.make_pass_decorator(
        AppContext
    )

Dùng:
    
    
    @pass_app
    def start(app):
    
        print(app.database)

* * *

Ưu điểm:

  * Có kiểm tra kiểu. 
  * IDE autocomplete. 
  * Code sạch hơn. 



* * *

# 19\. Thiết kế Story CLI

Sau buổi này kiến trúc:
    
    
    story
    
    |
    
    AppContext
    
    |
    
    +----------------+
    
    |                |
    
    crawler          database
    
    |                |
    
    start            backup

* * *

AppContext:
    
    
    class AppContext:
    
        config
    
        logger
    
        database
    
        http_client
    
        plugin_manager

* * *

Command:
    
    
    def start(app):
    
        app.crawler_service.start()

Không tự tạo:
    
    
    Database()
    Logger()

* * *

# 20\. Ví dụ hoàn chỉnh

Cấu trúc:
    
    
    story/
    
    ├── app.py
    
    ├── context.py
    
    └── commands/
    
           crawler.py

* * *

## context.py
    
    
    class AppContext:
    
        def __init__(self):
    
            self.name = "Story CLI"
    
            self.database = "story.db"

* * *

## app.py
    
    
    import click
    
    from context import AppContext
    
    
    @click.group()
    @click.pass_context
    def cli(ctx):
    
        ctx.obj = AppContext()
    
    
    from commands.crawler import crawler
    
    cli.add_command(crawler)
    
    
    if __name__ == "__main__":
        cli()

* * *

## crawler.py
    
    
    import click
    
    
    @click.group()
    def crawler():
        pass
    
    
    @crawler.command()
    @click.pass_context
    def start(ctx):
    
        app = ctx.obj
    
        click.echo(app.name)
    
        click.echo(app.database)

* * *

Chạy:
    
    
    python app.py crawler start

* * *

Kết quả:
    
    
    Story CLI
    story.db

* * *

# 21\. Những lỗi thường gặp

## Lỗi 1: Tạo object ở command

Sai:
    
    
    def backup():
    
        db = Database()

Đúng:
    
    
    Root tạo
    
    ↓
    
    ctx.obj
    
    ↓
    
    command sử dụng

* * *

## Lỗi 2: Dùng biến global

Sai:
    
    
    DATABASE = Database()

Vấn đề:

  * khó test 
  * khó thay đổi config 



* * *

## Lỗi 3: Lạm dụng ctx.obj

Không nên:
    
    
    ctx.obj["a"]
    ctx.obj["b"]
    ctx.obj["c"]

Khi lớn nên chuyển:
    
    
    AppContext

* * *

# Bài tập thực hành

## Bài 1

Tạo:
    
    
    story
    
    └── crawler
    
           └── start

Root tạo:
    
    
    ctx.obj = {
        "name":"Story CLI"
    }

Command `start` in ra.

* * *

## Bài 2

Tạo class:
    
    
    class AppContext:
    
        config
    
        database
    
        logger

Truyền qua `ctx.obj`.

* * *

## Bài 3

Tạo:
    
    
    story database backup

và:
    
    
    story crawler start

Cả hai cùng sử dụng:
    
    
    AppContext.database

* * *

## Bài 4

Tạo:
    
    
    pass_app =
    click.make_pass_decorator(AppContext)

Thay toàn bộ:
    
    
    ctx.obj

bằng:
    
    
    app

* * *

## Bài 5 - Mini Project

Xây dựng skeleton:
    
    
    story_cli
    
    ├── app.py
    
    ├── context.py
    
    └── commands
    
        ├── crawler.py
    
        ├── database.py
    
        └── plugin.py

Yêu cầu chạy được:
    
    
    story crawler start
    
    story database backup
    
    story plugin list

Tất cả command nhận chung:
    
    
    AppContext

* * *

# Tổng kết Buổi 9

Bạn đã học:

Thành phần| Vai trò  
---|---  
`click.Context`| Trạng thái của command  
`ctx.parent`| Context cha  
`ctx.obj`| Chia sẻ dữ liệu  
`pass_context`| Nhận Context  
`pass_obj`| Nhận obj trực tiếp  
`make_pass_decorator`| Inject AppContext  
  
Kiến trúc sau buổi 9:
    
    
    CLI
    
    ↓
    
    Nested Command Tree
    
    ↓
    
    Context
    
    ↓
    
    AppContext
    
    ↓
    
    Service
    
    ↓
    
    Repository
    
    ↓
    
    Database

* * *

# Buổi 10 tiếp theo (đúng roadmap)

**Command Chaining & Pipeline**

Chúng ta sẽ học:
    
    
    story crawl parse clean export

  * `chain=True`
  * Pipeline command 
  * Truyền dữ liệu giữa các bước 
  * Thiết kế workflow CLI 
  * Kết hợp Nested Command + Context 



Đây là bước tiếp theo sau khi đã có Command Tree và Context.

