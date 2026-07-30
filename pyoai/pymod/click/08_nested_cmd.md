# Khóa học Click Deep Dive

# Buổi 8: Nested Command trong Click - Thiết kế CLI nhiều tầng

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu rõ Nested Command là gì. 
>   * Xây dựng CLI có nhiều tầng lệnh. 
>   * Biết cách tổ chức command tree giống Git, Docker, Kubernetes. 
>   * Biết cách tách command thành module riêng. 
>   * Hiểu cách Click xử lý command hierarchy. 
>   * Xây dựng skeleton cho dự án CLI lớn. 
> 


* * *

# 1\. Nested Command là gì?

Ở buổi 7 chúng ta học:
    
    
    story crawler start

Cấu trúc:
    
    
    story
     |
     crawler
     |
     start

Đây là:

> Một cấp subcommand.

* * *

Nhưng dự án thực tế thường cần nhiều cấp hơn.

Ví dụ Docker:
    
    
    docker container run
    docker container stop
    docker image build
    docker image push

Cấu trúc:
    
    
    docker
    
    ├── container
    
    │      ├── run
    
    │      └── stop
    
    │
    
    └── image
    
           ├── build
    
           └── push

Đây gọi là:

# Nested Command

Command lồng trong command.

* * *

# 2\. Ví dụ đơn giản nhất

Ta xây dựng:
    
    
    app
    
    └── user
    
          └── add

CLI:
    
    
    python app.py user add

* * *

Code:
    
    
    import click
    
    
    @click.group()
    def cli():
        pass
    
    
    @cli.group()
    def user():
        pass
    
    
    @user.command()
    def add():
        click.echo("Add user")
    
    
    if __name__ == "__main__":
        cli()

* * *

Chạy:
    
    
    python app.py user add

Kết quả:
    
    
    Add user

* * *

# 3\. Hiểu cây command

Code:
    
    
    @click.group()
    def cli():

tạo:
    
    
    cli

* * *

Code:
    
    
    @cli.group()
    def user():

thêm:
    
    
    cli
    
    └── user

* * *

Code:
    
    
    @user.command()
    def add():

thêm:
    
    
    cli
    
    └── user
    
          └── add

* * *

# 4\. Thêm nhiều tầng hơn

Ví dụ:
    
    
    story
    
    └── crawler
    
           └── config
    
                  └── show

CLI:
    
    
    story crawler config show

* * *

Code:
    
    
    import click
    
    
    @click.group()
    def story():
        pass
    
    
    @story.group()
    def crawler():
        pass
    
    
    @crawler.group()
    def config():
        pass
    
    
    @config.command()
    def show():
        click.echo("Show crawler config")
    
    
    if __name__ == "__main__":
        story()

* * *

Chạy:
    
    
    python app.py crawler config show

Kết quả:
    
    
    Show crawler config

* * *

# 5\. Command tree thực tế

Click xây dựng cây:
    
    
    story
    
    |
    
    +-- crawler
    
    |      |
    
    |      +-- config
    
    |             |
    
    |             +-- show
    
    |
    
    +-- database
    
           |
    
           +-- backup

Khi chạy:
    
    
    story crawler config show

Click đi theo đường:
    
    
    story
     |
     crawler
     |
     config
     |
     show

* * *

# 6\. Nested Command giống Git

Git:
    
    
    git remote add origin url

Cấu trúc:
    
    
    git
    
    └── remote
    
           └── add

* * *

Click:
    
    
    @click.group()
    def git():
        pass
    
    
    @git.group()
    def remote():
        pass
    
    
    @remote.command()
    def add():
        pass

* * *

# 7\. Tổ chức code chuyên nghiệp

Không nên:
    
    
    app.py
    
    1000 dòng command

* * *

Nên:
    
    
    story_cli/
    
    │
    ├── app.py
    │
    └── commands/
        |
        ├── crawler.py
        |
        ├── database.py
        |
        └── plugin.py

* * *

# 8\. Tạo command module

## commands/crawler.py
    
    
    import click
    
    
    @click.group()
    def crawler():
        """
        Quản lý crawler.
        """
        pass
    
    
    @crawler.command()
    def start():
    
        click.echo(
            "Crawler started"
        )
    
    
    @crawler.command()
    def stop():
    
        click.echo(
            "Crawler stopped"
        )

* * *

## commands/database.py
    
    
    import click
    
    
    @click.group()
    def database():
        pass
    
    
    @database.command()
    def backup():
    
        click.echo(
            "Database backup"
        )

* * *

# 9\. Đăng ký command

## app.py
    
    
    import click
    
    from commands.crawler import crawler
    from commands.database import database
    
    
    @click.group()
    def cli():
        pass
    
    
    cli.add_command(crawler)
    
    cli.add_command(database)
    
    
    if __name__ == "__main__":
        cli()

* * *

Bây giờ:
    
    
    python app.py crawler start

hoạt động.

* * *
    
    
    python app.py database backup

hoạt động.

* * *

# 10\. Nested Command với nhiều module

Ví dụ:
    
    
    commands/
    
    crawler/
    
        __init__.py
    
        start.py
    
        config.py
    
    
    database/
    
        backup.py
    
        restore.py

Mục tiêu:
    
    
    story crawler start
    
    story crawler config show
    
    story database backup

* * *

# 11\. Tạo Group trong package

Ví dụ:
    
    
    commands/
    
    └── crawler
    
        ├── __init__.py
    
        ├── start.py
    
        └── config.py

* * *

## crawler/**init**.py
    
    
    import click
    
    
    @click.group()
    def crawler():
        pass

* * *

## start.py
    
    
    from . import crawler
    import click
    
    
    @crawler.command()
    def start():
    
        click.echo(
            "Start crawler"
        )

* * *

## config.py
    
    
    from . import crawler
    import click
    
    
    @crawler.group()
    def config():
        pass
    
    
    @config.command()
    def show():
    
        click.echo(
            "Config"
        )

* * *

# 12\. Import để đăng ký command

Một lỗi rất hay gặp:
    
    
    crawler
     |
     start

nhưng:
    
    
    story crawler start

báo:
    
    
    No such command 'start'

* * *

Nguyên nhân:

Bạn chưa import:
    
    
    import commands.crawler.start

Click chưa biết command tồn tại.

* * *

Ví dụ:
    
    
    # crawler/__init__.py
    
    from . import start
    from . import config

* * *

# 13\. Naming Convention

Không nên:
    
    
    commands.py

vì dễ xung đột.

Nên:
    
    
    commands/
    
        crawler.py
    
        database.py
    
        plugin.py

hoặc:
    
    
    commands/
    
        crawler/
    
        database/
    
        plugin/

* * *

# 14\. Group có callback riêng

Ví dụ:
    
    
    @click.group()
    def crawler():
    
        click.echo(
            "Crawler module"
        )

Chạy:
    
    
    story crawler start

Kết quả:
    
    
    Crawler module
    Crawler started

* * *

Mỗi tầng có thể chuẩn bị môi trường riêng.

* * *

# 15\. Thiết kế Story CLI

Ta xây dựng:
    
    
    story
    
    ├── crawler
    
    │      ├── start
    
    │      ├── stop
    
    │      ├── status
    
    │      └── config
    
    │              ├── show
    
    │              └── reset
    
    │
    
    ├── database
    
    │      ├── backup
    
    │      ├── restore
    
    │      └── migrate
    
    │
    
    ├── plugin
    
    │      ├── install
    
    │      ├── remove
    
    │      └── list
    
    │
    
    └── user
    
           ├── add
    
           └── remove

* * *

CLI:
    
    
    story crawler start
    
    story crawler config show
    
    story database backup
    
    story plugin list

* * *

Đây là cấu trúc của một CLI thực tế.

* * *

# 16\. Nested Command + Service Layer

Command không làm nghiệp vụ.

Sai:
    
    
    @crawler.command()
    def start():
    
        connect_database()
    
        crawl()
    
        save()

* * *

Đúng:
    
    
    @crawler.command()
    def start():
    
        crawler_service.start()

* * *

Kiến trúc:
    
    
    Click Command
    
    ↓
    
    Service
    
    ↓
    
    Repository
    
    ↓
    
    Database

* * *

# 17\. Khi nào dùng Nested Command?

Dùng khi:

  * Có nhiều nhóm chức năng. 
  * Command có quan hệ cha-con. 
  * Muốn CLI dễ khám phá. 



Ví dụ:

### Không tốt
    
    
    story-crawler-start
    story-db-backup
    story-plugin-list

* * *

Tốt:
    
    
    story crawler start
    
    story database backup
    
    story plugin list

* * *

# 18\. Bài tập thực hành

## Bài 1

Tạo:
    
    
    app
    
    └── user
    
          ├── add
    
          ├── remove
    
          └── list

CLI:
    
    
    python app.py user add
    python app.py user list

* * *

## Bài 2

Tạo:
    
    
    shop
    
    ├── product
    
    │      ├── add
    
    │      └── delete
    
    │
    
    └── order
    
           ├── create
    
           └── cancel

* * *

## Bài 3

Tách thành module:
    
    
    commands/
    
        product.py
    
        order.py

Không viết tất cả trong `app.py`.

* * *

## Bài 4

Xây dựng:
    
    
    story
    
    └── crawler
    
           └── config
    
                  ├── show
    
                  └── reset

CLI:
    
    
    story crawler config show
    
    story crawler config reset

* * *

## Bài 5 - Mini Project

Thiết kế skeleton:
    
    
    story_cli/
    
    ├── app.py
    
    └── commands/
    
        ├── crawler/
    
        │     ├── __init__.py
    
        │     ├── start.py
    
        │     └── config.py
    
        │
    
        ├── database/
    
        │     └── __init__.py
    
        │
    
        └── plugin/
    
              └── __init__.py

Mục tiêu:

Chạy được:
    
    
    story crawler start
    
    story crawler config show
    
    story database backup
    
    story plugin list

* * *

# Tổng kết Buổi 8

Bạn đã học:

Khái niệm| Ý nghĩa  
---|---  
Nested Command| Command nhiều tầng  
Group lồng nhau| Tạo cây lệnh  
`add_command()`| Đăng ký module  
Command package| Tổ chức dự án lớn  
Command tree| Mô hình CLI chuyên nghiệp  
  
Kiến trúc:
    
    
    CLI
    
    ↓
    
    Command Tree
    
    ↓
    
    Command
    
    ↓
    
    Service
    
    ↓
    
    Repository
    
    ↓
    
    Database

* * *

# Buổi tiếp theo: Buổi 9 - Context (`ctx`) trong Click

Sau khi đã có command tree, chúng ta mới học đúng thứ tự:

  * `click.Context`
  * `ctx.obj`
  * truyền dữ liệu giữa các tầng 
  * chia sẻ Config / Database / Logger 
  * `pass_context`
  * `pass_obj`
  * thiết kế AppContext cho Story CLI 



Đây sẽ là nền móng để xây dựng CLI lớn.

