# Khóa học Click Deep Dive

# Buổi 6: Multi-Command CLI với `@click.group()` \- Xây dựng CLI giống Git, Docker và Poetry

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu vì sao `@click.command()` không đủ cho ứng dụng lớn. 
>   * Hiểu cơ chế hoạt động của `@click.group()`. 
>   * Xây dựng CLI có nhiều lệnh như `git`, `docker`, `uv`, `poetry`. 
>   * Biết cách tổ chức dự án CLI theo module. 
>   * Chuẩn bị nền tảng cho các buổi về Context, Plugin và Dynamic Command. 
> 


* * *

# 1\. Một ứng dụng lớn không thể chỉ có một command

Cho đến buổi trước, chúng ta đều viết:
    
    
    @click.command()
    def cli():
        ...

Ví dụ:
    
    
    story

Điều này chỉ phù hợp với ứng dụng rất nhỏ.

* * *

Giả sử dự án Story Crawler.

Bạn muốn có:
    
    
    story crawl

rồi sau này thêm:
    
    
    story export
    story backup
    story config
    story plugin
    story database
    story search
    story remove

Nếu dùng `@click.command()`, bạn **không thể** làm điều này.

* * *

## Đây chính là lý do `Group` ra đời.

* * *

# 2\. Multi Command là gì?

Nhìn vào Git:
    
    
    git add
    git commit
    git push
    git pull
    git status
    git clone

Ở đây:
    
    
    git

không phải command.

Nó là **Group**.

Các command thật sự là:
    
    
    add
    commit
    push
    pull
    status
    clone

* * *

Docker cũng vậy.
    
    
    docker run
    
    docker ps
    
    docker image
    
    docker volume
    
    docker network

`docker`

↓

Group

* * *

Poetry
    
    
    poetry install
    
    poetry update
    
    poetry add
    
    poetry remove
    
    poetry build

* * *

Chúng ta cũng sẽ xây dựng
    
    
    story add
    
    story remove
    
    story search
    
    story export

* * *

# 3\. Group đầu tiên
    
    
    import click
    
    
    @click.group()
    def cli():
        """Story CLI"""
        pass
    
    
    @cli.command()
    def hello():
        click.echo("Hello")
    
    
    if __name__ == "__main__":
        cli()

Chạy
    
    
    python app.py hello

Kết quả
    
    
    Hello

* * *

Nếu chạy
    
    
    python app.py

Kết quả
    
    
    Usage:
    ...

vì Group đang chờ command.

* * *

# 4\. Group hoạt động thế nào?

Trước đây
    
    
    OS
    
    ↓
    
    Click
    
    ↓
    
    Command
    
    ↓
    
    Execute

Bây giờ
    
    
    OS
    
    ↓
    
    Group
    
    ↓
    
    Parser
    
    ↓
    
    Find Command
    
    ↓
    
    Execute

Ví dụ
    
    
    story export

Parser sẽ:
    
    
    story
    
    ↓
    
    Group
    
    ↓
    
    export
    
    ↓
    
    Execute export()

* * *

# 5\. Thêm nhiều command
    
    
    import click
    
    
    @click.group()
    def cli():
        pass
    
    
    @cli.command()
    def add():
        click.echo("Add")
    
    
    @cli.command()
    def remove():
        click.echo("Remove")
    
    
    @cli.command()
    def search():
        click.echo("Search")
    
    
    if __name__ == "__main__":
        cli()

* * *

CLI
    
    
    python app.py add

↓
    
    
    Add

* * *
    
    
    python app.py remove

↓
    
    
    Remove

* * *
    
    
    python app.py search

↓
    
    
    Search

* * *

# 6\. Help của Group

Chạy
    
    
    python app.py --help

Click sinh:
    
    
    Usage:
    
    app.py [OPTIONS] COMMAND [ARGS]...
    
    Commands:
    
    add
    
    remove
    
    search

Toàn bộ command đều xuất hiện.

Bạn không cần viết.

* * *

# 7\. Đặt tên command
    
    
    @cli.command("delete")
    def remove():
        pass

CLI
    
    
    python app.py delete

thay vì
    
    
    python app.py remove

Tên hàm Python và tên command không nhất thiết phải giống nhau.

* * *

# 8\. Thêm mô tả cho command
    
    
    @cli.command()
    def add():
        """Thêm truyện."""

Help
    
    
    Commands:
    
    add       Thêm truyện.
    
    remove    Xóa truyện.
    
    search    Tìm truyện.

Docstring chính là mô tả.

* * *

# 9\. Command có Argument
    
    
    @click.group()
    def cli():
        pass
    
    
    @cli.command()
    @click.argument("title")
    def add(title):
        click.echo(title)

CLI
    
    
    python app.py add "Harry Potter"

↓
    
    
    Harry Potter

* * *

# 10\. Command có Option
    
    
    @cli.command()
    @click.option("--format")
    def export(format):
        click.echo(format)

CLI
    
    
    python app.py export --format epub

↓
    
    
    epub

* * *

# 11\. Group giống một thư mục

Hãy tưởng tượng
    
    
    story
    
    ├── add
    
    ├── remove
    
    ├── export
    
    ├── backup
    
    ├── config

Group giống như một thư mục.

Command giống như các file bên trong.

* * *

# 12\. Chia command thành module

Đây mới là cách làm chuyên nghiệp.

Không nên:
    
    
    app.py
    
    1500 dòng

* * *

Nên
    
    
    project/
    
    │
    
    ├── app.py
    
    │
    
    ├── commands/
    
    │      add.py
    
    │      remove.py
    
    │      export.py
    
    │      backup.py

Ví dụ

**commands/add.py**
    
    
    import click
    
    
    @click.command()
    @click.argument("title")
    def add(title):
        click.echo(f"Add: {title}")

* * *

**commands/remove.py**
    
    
    import click
    
    
    @click.command()
    @click.argument("id")
    def remove(id):
        click.echo(f"Remove: {id}")

* * *

**app.py**
    
    
    import click
    
    from commands.add import add
    from commands.remove import remove
    
    
    @click.group()
    def cli():
        pass
    
    
    cli.add_command(add)
    cli.add_command(remove)
    
    
    if __name__ == "__main__":
        cli()

CLI
    
    
    python app.py add Novel

↓
    
    
    Add: Novel

* * *

# 13\. `add_command()`

Có hai cách.

Cách 1

Decorator
    
    
    @cli.command()

* * *

Cách 2
    
    
    cli.add_command(add)

Đây là cách sẽ dùng nhiều trong các dự án lớn vì:

  * Có thể nạp động (dynamic loading). 
  * Hỗ trợ plugin. 
  * Dễ quản lý. 



* * *

# 14\. Tổ chức Story CLI

Từ buổi này, chúng ta sẽ hướng tới cấu trúc như sau:
    
    
    story/
    
    │
    
    ├── app.py
    
    │
    
    ├── commands/
    
    │      crawler.py
    
    │      export.py
    
    │      backup.py
    
    │      config.py
    
    │      plugin.py
    
    │      database.py

Trong tương lai:
    
    
    story crawler
    
    story export
    
    story backup
    
    story plugin
    
    story config

Mỗi file sẽ chịu trách nhiệm cho một nhóm chức năng.

* * *

# 15\. Mini Project

**Cấu trúc**
    
    
    story_cli/
    
    │
    
    ├── app.py
    
    │
    
    └── commands/
    
           add.py
    
           remove.py
    
           search.py

* * *

**commands/add.py**
    
    
    import click
    
    @click.command()
    @click.argument("title")
    def add(title):
        """Thêm truyện."""
        click.echo(f"Đã thêm: {title}")

* * *

**commands/remove.py**
    
    
    import click
    
    @click.command()
    @click.argument("story_id", type=int)
    def remove(story_id):
        """Xóa truyện."""
        click.echo(f"Đã xóa ID: {story_id}")

* * *

**commands/search.py**
    
    
    import click
    
    @click.command()
    @click.argument("keyword")
    def search(keyword):
        """Tìm truyện."""
        click.echo(f"Tìm: {keyword}")

* * *

**app.py**
    
    
    import click
    
    from commands.add import add
    from commands.remove import remove
    from commands.search import search
    
    
    @click.group()
    def cli():
        """Story CLI."""
        pass
    
    
    cli.add_command(add)
    cli.add_command(remove)
    cli.add_command(search)
    
    
    if __name__ == "__main__":
        cli()

Thử chạy:
    
    
    python app.py add "Harry Potter"
    python app.py remove 15
    python app.py search "Magic"
    python app.py --help

* * *

# 16\. Những lỗi người mới thường gặp

## ❌ Viết tất cả command trong một file
    
    
    app.py
    
    2500 dòng

Rất khó bảo trì.

* * *

## ❌ Mỗi command tự chạy
    
    
    if __name__ == "__main__":
        add()

Khi command được import vào `app.py`, **không** nên tự chạy.

Chỉ `app.py` mới chứa:
    
    
    if __name__ == "__main__":
        cli()

* * *

## ❌ Đặt logic xử lý ngay trong command

Không nên:
    
    
    @cli.command()
    def backup():
        # 300 dòng xử lý

Nên:
    
    
    @cli.command()
    def backup():
        backup_service.run()

Command chỉ nên:

  * Nhận tham số. 
  * Kiểm tra đầu vào. 
  * Gọi service. 
  * Hiển thị kết quả. 



Điều này sẽ giúp mã nguồn dễ kiểm thử và tái sử dụng.

* * *

# 17\. Tổng kết

Các khái niệm quan trọng:

Khái niệm| Vai trò  
---|---  
`@click.group()`| Tạo CLI nhiều lệnh  
`@cli.command()`| Đăng ký command  
`cli.add_command()`| Thêm command từ module khác  
`--help`| Tự sinh danh sách command  
Docstring| Mô tả command  
  
Luồng xử lý:
    
    
    CLI
    
    ↓
    
    Group
    
    ↓
    
    Command
    
    ↓
    
    Service
    
    ↓
    
    Repository
    
    ↓
    
    Database

Đây là kiến trúc mà chúng ta sẽ theo đuổi trong toàn bộ khóa học.

* * *

# Bài tập thực hành

## Bài 1

Tạo CLI gồm ba lệnh:
    
    
    python app.py hello
    python app.py goodbye
    python app.py version

* * *

## Bài 2

Tách mỗi lệnh thành một file riêng trong thư mục `commands/` và đăng ký bằng `cli.add_command()`.

* * *

## Bài 3

Viết lệnh:
    
    
    python app.py add "One Piece"

In ra:
    
    
    Đã thêm truyện: One Piece

* * *

## Bài 4

Viết lệnh:
    
    
    python app.py remove 101

với `story_id` là `int`.

* * *

## Bài 5 (Mini Project)

Xây dựng CLI quản lý truyện với các lệnh:
    
    
    story add "Harry Potter"
    
    story remove 10
    
    story search "Magic"
    
    story list

Hiện tại các lệnh chỉ cần `click.echo()` để mô phỏng. Từ **buổi 7** , chúng ta sẽ bắt đầu xây dựng **Subcommand** để có cấu trúc nhiều cấp như:
    
    
    story crawler start
    
    story crawler stop
    
    story db backup
    
    story plugin install

Đây là bước tiến giúp CLI của bạn có kiến trúc tương tự các công cụ chuyên nghiệp như `git`, `docker` và `kubectl`.

