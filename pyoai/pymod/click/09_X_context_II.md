# Khóa học Click Deep Dive

# Buổi 9: Context nâng cao - `pass_obj`, `make_pass_decorator()` và Dependency Injection

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu hạn chế của `ctx.obj`. 
>   * Sử dụng `@click.pass_obj`. 
>   * Tự tạo decorator bằng `click.make_pass_decorator()`. 
>   * Thiết kế `AppContext` theo kiểu Strongly Typed. 
>   * Áp dụng Dependency Injection (DI) trong ứng dụng CLI. 
>   * Chuẩn bị nền tảng cho Plugin Architecture và Dynamic Command. 
> 


* * *

# 1\. Nhìn lại buổi 8

Chúng ta đã học:
    
    
    @click.pass_context
    def start(ctx):
        app = ctx.obj

Mọi command đều phải viết:
    
    
    app = ctx.obj

hoặc
    
    
    db = ctx.obj.database
    logger = ctx.obj.logger
    config = ctx.obj.config

Điều này hoạt động tốt.

Nhưng với dự án lớn có **100 command** , việc lặp lại `ctx.obj` ở mọi nơi sẽ rất nhàm chán.

* * *

# 2\. Ý tưởng của `pass_obj`

Click cung cấp:
    
    
    @click.pass_obj

Nó lấy:
    
    
    ctx.obj

rồi truyền thẳng vào hàm.

Không cần:
    
    
    ctx.obj

nữa.

* * *

# 3\. Ví dụ đầu tiên
    
    
    import click
    
    class AppContext:
    
        def __init__(self):
            self.database = "story.db"
    
    
    @click.command()
    @click.pass_obj
    def hello(app):
        click.echo(app.database)
    
    
    if __name__ == "__main__":
        hello(obj=AppContext())

Ở ví dụ này:
    
    
    app

chính là
    
    
    ctx.obj

* * *

# 4\. Group thực tế
    
    
    import click
    
    class AppContext:
    
        def __init__(self):
            self.database = "story.db"
    
    
    @click.group()
    @click.pass_context
    def cli(ctx):
    
        ctx.obj = AppContext()
    
    
    @cli.command()
    @click.pass_obj
    def info(app):
    
        click.echo(app.database)
    
    
    if __name__ == "__main__":
        cli()

CLI
    
    
    python app.py info

↓
    
    
    story.db

Không còn thấy:
    
    
    ctx.obj

* * *

# 5\. `pass_context` hay `pass_obj`?

### pass_context
    
    
    @click.pass_context
    def backup(ctx):

Có thể dùng:

  * ctx.parent 
  * invoked_subcommand 
  * command 
  * params 
  * obj 



* * *

### pass_obj
    
    
    @click.pass_obj
    def backup(app):

Chỉ nhận:
    
    
    ctx.obj

Nếu command chỉ cần `AppContext`, hãy ưu tiên `pass_obj` vì code ngắn gọn hơn.

* * *

# 6\. Hạn chế của `pass_obj`

Giả sử:
    
    
    ctx.obj = Logger()

Command:
    
    
    @click.pass_obj
    def info(app):

Thực tế:
    
    
    app

lại là:
    
    
    Logger

Tên biến `app` gây hiểu nhầm.

Chúng ta cần một cách an toàn hơn.

* * *

# 7\. `make_pass_decorator()`

Đây là một trong những API mạnh nhất của Click.

Ví dụ:
    
    
    pass_app = click.make_pass_decorator(AppContext)

Sau đó:
    
    
    @pass_app
    def backup(app):

Click sẽ:

  * kiểm tra kiểu dữ liệu, 
  * tìm đúng `AppContext`, 
  * truyền vào. 



* * *

# 8\. Ví dụ hoàn chỉnh
    
    
    import click
    
    class AppContext:
    
        def __init__(self):
            self.database = "story.db"
    
    
    pass_app = click.make_pass_decorator(AppContext)
    
    
    @click.group()
    @click.pass_context
    def cli(ctx):
    
        ctx.obj = AppContext()
    
    
    @cli.command()
    @pass_app
    def info(app):
    
        click.echo(app.database)
    
    
    if __name__ == "__main__":
        cli()

Đây là cách rất nhiều dự án Click chuyên nghiệp sử dụng.

* * *

# 9\. Vì sao `make_pass_decorator()` tốt hơn?

Giả sử sau này có thêm:
    
    
    class Config:
        ...
    
    class Logger:
        ...
    
    class Database:
        ...

Bạn có thể tạo:
    
    
    pass_config = click.make_pass_decorator(Config)
    
    pass_logger = click.make_pass_decorator(Logger)
    
    pass_database = click.make_pass_decorator(Database)

Mỗi command chỉ nhận đúng đối tượng mà nó cần.

* * *

# 10\. Strongly Typed Context

Không nên:
    
    
    ctx.obj = {
    
        "database": "...",
    
        "logger": "...",
    
        "config": "..."
    }

IDE không biết:
    
    
    ctx.obj["database"]

là kiểu gì.

Không có gợi ý (autocomplete).

* * *

Nên:
    
    
    from dataclasses import dataclass
    
    @dataclass
    class AppContext:
    
        database: str
    
        debug: bool
    
        threads: int

Command:
    
    
    @click.pass_obj
    def info(app: AppContext):
    
        click.echo(app.database)

IDE sẽ gợi ý đầy đủ.

* * *

# 11\. Dependency Injection

Giả sử có:
    
    
    class Database:
    
        ...
    
    class Logger:
    
        ...

Tạo:
    
    
    @dataclass
    class AppContext:
    
        db: Database
    
        logger: Logger

Command:
    
    
    @pass_app
    def backup(app):
    
        app.logger.info(...)
    
        app.db.backup()

Command **không tạo** `Database`.

Nó chỉ **nhận** từ bên ngoài.

Đó chính là **Dependency Injection (DI)**.

* * *

# 12\. Sai và đúng

### Sai
    
    
    @cli.command()
    def backup():
    
        db = Database()
    
        db.backup()

Command phụ thuộc trực tiếp vào `Database`.

* * *

### Đúng
    
    
    @pass_app
    def backup(app):
    
        app.db.backup()

`Database` được tạo ở Root Group.

Command chỉ sử dụng.

* * *

# 13\. Tách AppContext

Cấu trúc:
    
    
    story/
    
    │
    
    ├── app.py
    
    ├── app_context.py
    
    ├── commands/
    
    ├── services/
    
    ├── repositories/

* * *

## app_context.py
    
    
    from dataclasses import dataclass
    
    @dataclass
    class AppContext:
    
        database: str
    
        threads: int
    
        debug: bool

* * *

## app.py
    
    
    ctx.obj = AppContext(
    
        database="story.db",
    
        threads=4,
    
        debug=False
    )

* * *

## commands/info.py
    
    
    @pass_app
    def info(app):
    
        click.echo(app.database)

Mỗi phần có trách nhiệm riêng.

* * *

# 14\. Kết hợp với Service

Giả sử:
    
    
    class BackupService:
    
        def backup(self):
            ...

AppContext:
    
    
    @dataclass
    class AppContext:
    
        backup_service: BackupService

Command:
    
    
    @pass_app
    def backup(app):
    
        app.backup_service.backup()

Command cực kỳ ngắn.

* * *

# 15\. Kiến trúc hoàn chỉnh
    
    
    CLI
    
    ↓
    
    Click
    
    ↓
    
    AppContext
    
    ↓
    
    Services
    
    ↓
    
    Repositories
    
    ↓
    
    Database

Command không biết:

  * SQLite 
  * MySQL 
  * Redis 



Nó chỉ gọi:
    
    
    app.backup_service.backup()

Đây chính là **Clean Architecture** ở tầng giao diện (Presentation Layer).

* * *

# 16\. Mini Project

## app_context.py
    
    
    from dataclasses import dataclass
    
    @dataclass
    class AppContext:
    
        database: str
    
        threads: int
    
        debug: bool

* * *

## decorators.py
    
    
    import click
    
    from app_context import AppContext
    
    pass_app = click.make_pass_decorator(AppContext)

* * *

## app.py
    
    
    import click
    
    from app_context import AppContext
    from decorators import pass_app
    
    
    @click.group()
    @click.pass_context
    def cli(ctx):
    
        ctx.obj = AppContext(
    
            database="story.db",
    
            threads=4,
    
            debug=True
        )
    
    
    @cli.command()
    @pass_app
    def info(app):
    
        click.echo(app.database)
    
        click.echo(app.threads)
    
        click.echo(app.debug)
    
    
    if __name__ == "__main__":
        cli()

CLI:
    
    
    python app.py info

↓
    
    
    story.db
    4
    True

* * *

# 17\. Những lỗi người mới thường gặp

## ❌ Lưu quá nhiều thứ trong `dict`
    
    
    ctx.obj = {
    
        "db": ...,
    
        "logger": ...,
    
        "cache": ...,
    
        "http": ...,
    
        "service": ...
    }

Sau vài tháng sẽ rất khó quản lý.

Hãy dùng một lớp hoặc `@dataclass`.

* * *

## ❌ Command tự tạo Service
    
    
    service = BackupService()

Nên để Root Group tạo và truyền qua `AppContext`.

* * *

## ❌ Command biết quá nhiều

Sai:
    
    
    sqlite.connect(...)
    
    cursor.execute(...)
    
    logger.info(...)

Đúng:
    
    
    app.backup_service.backup()

Command chỉ điều phối (orchestrate), không chứa nghiệp vụ.

* * *

# 18\. Tổng kết

Các API quan trọng:

API| Mục đích  
---|---  
`@click.pass_obj`| Truyền `ctx.obj` trực tiếp  
`click.make_pass_decorator()`| Tạo decorator truyền đúng kiểu đối tượng  
`@dataclass`| Tạo `AppContext` rõ ràng, dễ bảo trì  
Dependency Injection| Khởi tạo tài nguyên ở Root Group, sử dụng ở Command  
  
Luồng xử lý:
    
    
    CLI
    
    ↓
    
    Root Group
    
    ↓
    
    AppContext
    
    ↓
    
    Service
    
    ↓
    
    Repository
    
    ↓
    
    Database

* * *

# Bài tập thực hành

## Bài 1

Chuyển `ctx.obj` từ `dict` sang `@dataclass AppContext`.

* * *

## Bài 2

Tạo:
    
    
    pass_app = click.make_pass_decorator(AppContext)

và cập nhật các command để sử dụng `@pass_app`.

* * *

## Bài 3

Thêm lớp:
    
    
    class Logger:
        def info(self, message):
            print(message)

Lưu `Logger` vào `AppContext` và gọi `app.logger.info()` trong command.

* * *

## Bài 4

Tạo `BackupService` với phương thức:
    
    
    backup()

Lưu vào `AppContext` và viết lệnh:
    
    
    story db backup

để gọi `app.backup_service.backup()`.

* * *

## Bài 5 (Mini Project)

Thiết kế `AppContext` cho dự án **Story Crawler** :
    
    
    @dataclass
    class AppContext:
        config: Config
        logger: Logger
        database: Database
        http_client: HttpClient
        crawler_service: CrawlerService
        export_service: ExportService
        plugin_manager: PluginManager

Hiện tại các lớp có thể là mock hoặc đơn giản chỉ in thông báo. Mục tiêu là xây dựng **khung kiến trúc** để các buổi sau chúng ta chỉ việc thay thế bằng các triển khai thật.

* * *

# Chuẩn bị cho buổi 10

Ở **Buổi 10** , chúng ta sẽ học về **Command Chaining và Command Pipeline** :

  * `chain=True` trong `@click.group()`. 
  * Thực thi nhiều command trong một lần gọi. 
  * Xây dựng pipeline xử lý dữ liệu. 
  * Thiết kế các chuỗi lệnh như: 


    
    
    story crawl export backup

hoặc:
    
    
    backup compress upload

Đây là một tính năng ít người biết của Click nhưng rất hữu ích khi xây dựng các công cụ tự động hóa và xử lý dữ liệu theo nhiều bước.

