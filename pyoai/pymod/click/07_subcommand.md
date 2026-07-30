# Khóa học Click Deep Dive

# Buổi 7: Subcommand - CLI nhiều cấp (Lệnh lồng nhau)

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu sự khác biệt giữa **Command** và **Subcommand**. 
>   * Biết cách tạo **Group lồng nhau**. 
>   * Xây dựng CLI nhiều cấp giống `git`, `docker`, `kubectl`, `aws`. 
>   * Thiết kế cấu trúc CLI dễ mở rộng cho các dự án lớn. 
>   * Chuẩn bị nền tảng cho **Context (`ctx`)** ở buổi 8. 
> 


* * *

# 1\. Từ Command đến Subcommand

Ở buổi 6 chúng ta có:
    
    
    story
    
    ├── add
    ├── remove
    ├── search
    └── export

CLI:
    
    
    story add
    story remove
    story search
    story export

Điều này ổn với ứng dụng nhỏ.

* * *

Nhưng nếu dự án phát triển:
    
    
    story crawler start
    story crawler stop
    story crawler pause
    story crawler resume
    story crawler status
    
    story db backup
    story db restore
    story db vacuum
    
    story plugin list
    story plugin install
    story plugin remove
    
    story config show
    story config edit
    story config reset

Nếu tất cả đều nằm cùng một cấp:
    
    
    story start
    story stop
    story pause
    storyresume
    storystatus
    storybackup
    storyrestore
    storyvacuum
    storyinstall
    storyremove
    ...

CLI sẽ rất lộn xộn.

Đó là lý do **Subcommand** tồn tại.

* * *

# 2\. Cấu trúc Tree

Click cho phép tạo cây lệnh.
    
    
    story
    │
    ├── crawler
    │      ├── start
    │      ├── stop
    │      ├── pause
    │      └── status
    │
    ├── db
    │      ├── backup
    │      ├── restore
    │      └── vacuum
    │
    ├── plugin
    │      ├── install
    │      ├── remove
    │      └── list
    │
    └── config
           ├── show
           ├── edit
           └── reset

Đây chính là cách Git, Docker và Kubernetes tổ chức CLI.

* * *

# 3\. Group bên trong Group

Trong Click:
    
    
    @click.group()
    def cli():
        pass
    
    
    @cli.group()
    def crawler():
        pass

Lưu ý:
    
    
    @cli.group()

không phải
    
    
    @click.group()

Nó có nghĩa:

> Tạo **Group con** bên trong `cli`.

* * *

# 4\. Ví dụ đầu tiên
    
    
    import click
    
    
    @click.group()
    def cli():
        pass
    
    
    @cli.group()
    def crawler():
        """Quản lý crawler."""
        pass
    
    
    @crawler.command()
    def start():
        click.echo("Crawler started.")
    
    
    @crawler.command()
    def stop():
        click.echo("Crawler stopped.")
    
    
    if __name__ == "__main__":
        cli()

* * *

CLI
    
    
    python app.py crawler start

↓
    
    
    Crawler started.

* * *
    
    
    python app.py crawler stop

↓
    
    
    Crawler stopped.

* * *

# 5\. Help của Subcommand
    
    
    python app.py --help

↓
    
    
    Commands:
    
    crawler

* * *

Tiếp theo:
    
    
    python app.py crawler --help

↓
    
    
    Commands:
    
    start
    
    stop

Mỗi Group có `--help` riêng.

* * *

# 6\. Thêm Argument
    
    
    @crawler.command()
    @click.argument("url")
    def crawl(url):
        click.echo(url)

CLI
    
    
    python app.py crawler crawl https://example.com

↓
    
    
    https://example.com

* * *

# 7\. Thêm Option
    
    
    @crawler.command()
    @click.option("--threads", default=4)
    def start(threads):
        click.echo(f"Threads: {threads}")

CLI
    
    
    python app.py crawler start --threads 8

↓
    
    
    Threads: 8

* * *

# 8\. Nhiều Group
    
    
    @click.group()
    def cli():
        pass
    
    
    @cli.group()
    def crawler():
        pass
    
    
    @cli.group()
    def db():
        pass
    
    
    @cli.group()
    def plugin():
        pass

CLI
    
    
    story crawler ...
    
    story db ...
    
    story plugin ...

* * *

# 9\. Mỗi Group có nhiều Command
    
    
    @db.command()
    def backup():
        ...
    
    
    @db.command()
    def restore():
        ...
    
    
    @db.command()
    def vacuum():
        ...

CLI
    
    
    story db backup
    
    story db restore
    
    story db vacuum

* * *

# 10\. Sơ đồ hoạt động

Ví dụ:
    
    
    story db backup

Click xử lý:
    
    
    OS
    
    ↓
    
    cli
    
    ↓
    
    db
    
    ↓
    
    backup
    
    ↓
    
    Execute

* * *

Ví dụ:
    
    
    story crawler start

↓
    
    
    OS
    
    ↓
    
    cli
    
    ↓
    
    crawler
    
    ↓
    
    start
    
    ↓
    
    Execute

* * *

# 11\. Tổ chức theo module

Không nên:
    
    
    app.py
    
    1000 dòng

* * *

Nên:
    
    
    story/
    
    │
    
    ├── app.py
    
    │
    
    ├── commands/
    
    │      crawler.py
    
    │      db.py
    
    │      plugin.py
    
    │      config.py

* * *

## crawler.py
    
    
    import click
    
    
    @click.group()
    def crawler():
        """Crawler commands."""
        pass
    
    
    @crawler.command()
    def start():
        click.echo("Crawler started.")
    
    
    @crawler.command()
    def stop():
        click.echo("Crawler stopped.")

* * *

## db.py
    
    
    import click
    
    
    @click.group()
    def db():
        """Database commands."""
        pass
    
    
    @db.command()
    def backup():
        click.echo("Backup completed.")

* * *

## app.py
    
    
    import click
    
    from commands.crawler import crawler
    from commands.db import db
    
    
    @click.group()
    def cli():
        """Story CLI."""
        pass
    
    
    cli.add_command(crawler)
    cli.add_command(db)
    
    
    if __name__ == "__main__":
        cli()

* * *

# 12\. Group không nhất thiết phải có logic

Thông thường:
    
    
    @click.group()
    def crawler():
        pass

Không làm gì cả.

Nó chỉ đóng vai trò **thư mục**.

* * *

# 13\. Thiết kế Story CLI

Đây là cấu trúc chúng ta sẽ hướng tới:
    
    
    story
    
    │
    
    ├── crawler
    
    │      start
    
    │      stop
    
    │      pause
    
    │      resume
    
    │      status
    
    │
    
    ├── db
    
    │      backup
    
    │      restore
    
    │      optimize
    
    │
    
    ├── plugin
    
    │      install
    
    │      uninstall
    
    │      enable
    
    │      disable
    
    │      list
    
    │
    
    ├── export
    
    │      epub
    
    │      html
    
    │      txt
    
    │
    
    └── config
    
           show
    
           edit
    
           reset

Đây là kiến trúc phổ biến trong các CLI chuyên nghiệp.

* * *

# 14\. Mini Project

Cấu trúc:
    
    
    story_cli/
    
    │
    
    ├── app.py
    
    │
    
    └── commands/
    
           crawler.py
    
           db.py

* * *

**crawler.py**
    
    
    import click
    
    
    @click.group()
    def crawler():
        pass
    
    
    @crawler.command()
    def start():
        click.echo("Crawler started.")
    
    
    @crawler.command()
    def stop():
        click.echo("Crawler stopped.")
    
    
    @crawler.command()
    def status():
        click.echo("Crawler is running.")

* * *

**db.py**
    
    
    import click
    
    
    @click.group()
    def db():
        pass
    
    
    @db.command()
    def backup():
        click.echo("Backup done.")
    
    
    @db.command()
    def restore():
        click.echo("Restore done.")

* * *

**app.py**
    
    
    import click
    
    from commands.crawler import crawler
    from commands.db import db
    
    
    @click.group()
    def cli():
        pass
    
    
    cli.add_command(crawler)
    cli.add_command(db)
    
    
    if __name__ == "__main__":
        cli()

Chạy thử:
    
    
    python app.py crawler start
    python app.py crawler status
    python app.py db backup
    python app.py db restore
    python app.py --help
    python app.py crawler --help
    python app.py db --help

Quan sát cách Click sinh tài liệu trợ giúp theo từng cấp.

* * *

# 15\. Những lỗi người mới thường gặp

### ❌ Đăng ký sai cấp

Sai:
    
    
    @cli.command()
    def start():
        ...

Trong khi mong muốn là:
    
    
    story crawler start

Đúng:
    
    
    @crawler.command()
    def start():
        ...

* * *

### ❌ Group làm quá nhiều việc

Sai:
    
    
    @click.group()
    def db():
        connect_database()

`Group` nên đóng vai trò điều hướng.

Việc khởi tạo tài nguyên sẽ được học ở **buổi 8 với`Context (ctx)`**.

* * *

### ❌ Đặt quá nhiều command ở root

Không nên:
    
    
    story backup
    story restore
    story vacuum
    story optimize
    story migrate
    story init

Nên:
    
    
    story db backup
    story db restore
    story db vacuum
    story db optimize
    story db migrate
    story db init

CLI sẽ trực quan và dễ khám phá hơn.

* * *

# 16\. Tổng kết

Các khái niệm quan trọng:

Thành phần| Vai trò  
---|---  
`@click.group()`| Tạo nhóm lệnh  
`@cli.group()`| Tạo nhóm lệnh con  
`@group.command()`| Thêm command vào group  
`add_command()`| Đăng ký group hoặc command từ module khác  
  
Cấu trúc xử lý:
    
    
    CLI
    
    ↓
    
    Root Group
    
    ↓
    
    Sub Group
    
    ↓
    
    Command
    
    ↓
    
    Service
    
    ↓
    
    Repository

* * *

# Bài tập thực hành

## Bài 1

Tạo CLI:
    
    
    python app.py user add
    python app.py user remove
    python app.py user list

* * *

## Bài 2

Tạo CLI:
    
    
    python app.py book add
    python app.py book search
    python app.py book export

* * *

## Bài 3

Tạo hai nhóm:
    
    
    python app.py crawler start
    python app.py crawler stop
    
    python app.py db backup
    python app.py db restore

Mỗi nhóm nằm trong một file riêng.

* * *

## Bài 4

Thêm Option:
    
    
    python app.py crawler start --threads 8

In ra:
    
    
    Crawler started with 8 threads.

* * *

## Bài 5 (Mini Project)

Xây dựng cấu trúc CLI cho dự án **Story Crawler** :
    
    
    story
    
    ├── crawler
    │   ├── start
    │   ├── stop
    │   ├── status
    │
    ├── db
    │   ├── backup
    │   ├── restore
    │
    ├── plugin
    │   ├── install
    │   ├── list
    │
    └── config
        ├── show
        ├── reset

Hiện tại mỗi lệnh chỉ cần `click.echo()` mô phỏng chức năng.

* * *

# Chuẩn bị cho buổi 8

Ở **Buổi 8** , chúng ta sẽ học một trong những cơ chế quan trọng nhất của Click: **Context (`click.Context`)**.

Bạn sẽ hiểu:

  * `ctx` là gì và vì sao hầu hết các CLI lớn đều sử dụng nó. 
  * `@click.pass_context`. 
  * `ctx.obj` để chia sẻ cấu hình, logger, kết nối cơ sở dữ liệu và các service giữa các command. 
  * Cách xây dựng nền tảng cho Dependency Injection trong CLI. 



Đây là bước chuyển từ "biết dùng Click" sang "thiết kế CLI quy mô lớn", và sẽ là nền móng cho các buổi về Plugin Architecture, Dynamic Command Loading và dự án **Story Crawler CLI** sau này.

