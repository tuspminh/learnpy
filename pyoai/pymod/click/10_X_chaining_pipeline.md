# Khóa học Click Deep Dive

# Buổi 10: Command Chaining & Pipeline - Thực thi nhiều lệnh trong một lần gọi

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu **Command Chaining** là gì. 
>   * Biết cách sử dụng `chain=True`. 
>   * Hiểu giới hạn của Command Chaining. 
>   * Thiết kế Pipeline xử lý dữ liệu. 
>   * Kết hợp với `Context` để chia sẻ dữ liệu giữa các command. 
>   * Hiểu sự khác nhau giữa Command Chaining và Subcommand. 
> 


* * *

# 1\. Tại sao cần Command Chaining?

Giả sử bạn có CLI:
    
    
    story
    
    ├── crawl
    ├── clean
    ├── export
    ├── backup
    └── upload

Thông thường bạn phải chạy:
    
    
    story crawl
    story clean
    story export
    story backup

Hoặc viết script:
    
    
    story crawl && \
    story clean && \
    story export && \
    story backup

Điều này khá bất tiện.

Click hỗ trợ:
    
    
    story crawl clean export backup

Chỉ với **một lần gọi**.

Đây gọi là **Command Chaining**.

* * *

# 2\. Chain hoạt động như thế nào?

Thông thường:
    
    
    CLI
    
    ↓
    
    crawl
    
    ↓
    
    Exit

Command Chain:
    
    
    CLI
    
    ↓
    
    crawl
    
    ↓
    
    clean
    
    ↓
    
    export
    
    ↓
    
    backup
    
    ↓
    
    Exit

Một tiến trình (process) duy nhất.

* * *

# 3\. Tạo Group Chain

Ví dụ:
    
    
    import click
    
    @click.group(chain=True)
    def cli():
        pass
    
    @cli.command()
    def hello():
        click.echo("Hello")
    
    @cli.command()
    def world():
        click.echo("World")
    
    if __name__ == "__main__":
        cli()

* * *

CLI
    
    
    python app.py hello world

↓
    
    
    Hello
    World

Không cần chạy hai lần.

* * *

# 4\. Không dùng Chain

Nếu bỏ:
    
    
    chain=True

CLI
    
    
    python app.py hello world

↓
    
    
    Error:
    Got unexpected extra argument (world)

Chỉ một command được phép chạy.

* * *

# 5\. Chain nhiều command
    
    
    @click.group(chain=True)
    def cli():
        pass
    
    @cli.command()
    def a():
        click.echo("A")
    
    @cli.command()
    def b():
        click.echo("B")
    
    @cli.command()
    def c():
        click.echo("C")

CLI
    
    
    python app.py a b c

↓
    
    
    A
    B
    C

Click thực thi theo đúng thứ tự người dùng nhập.

* * *

# 6\. Thêm Option
    
    
    @cli.command()
    @click.option("--name")
    def hello(name):
        click.echo(name)

CLI
    
    
    python app.py hello --name Alice world

↓
    
    
    Alice
    World

Option chỉ áp dụng cho command của nó.

* * *

# 7\. Ví dụ Story CLI
    
    
    story crawl export backup

Thực tế sẽ tương đương:
    
    
    crawl()
    
    export()
    
    backup()

Theo đúng thứ tự.

* * *

# 8\. Nhưng dữ liệu ở đâu?

Ví dụ:
    
    
    story crawl export

`crawl`

↓

tạo dữ liệu

↓

`export`

↓

xuất dữ liệu

Làm sao `export` biết dữ liệu?

* * *

Đó là lúc `ctx.obj` phát huy tác dụng.

* * *

# 9\. Chia sẻ dữ liệu bằng Context
    
    
    import click
    
    @click.group(chain=True)
    @click.pass_context
    def cli(ctx):
        ctx.ensure_object(dict)
        ctx.obj["stories"] = []

Command:
    
    
    @cli.command()
    @click.pass_context
    def crawl(ctx):
    
        ctx.obj["stories"].append("Story A")

Command tiếp theo:
    
    
    @cli.command()
    @click.pass_context
    def export(ctx):
    
        click.echo(ctx.obj["stories"])

CLI
    
    
    python app.py crawl export

↓
    
    
    ['Story A']

Dữ liệu được chia sẻ trong cùng một lần thực thi.

* * *

# 10\. Ví dụ hoàn chỉnh
    
    
    import click
    
    @click.group(chain=True)
    @click.pass_context
    def cli(ctx):
    
        ctx.ensure_object(dict)
    
        ctx.obj["numbers"] = []
    
    
    @cli.command()
    @click.pass_context
    def load(ctx):
    
        ctx.obj["numbers"] = [1,2,3]
    
    
    @cli.command()
    @click.pass_context
    def sum(ctx):
    
        click.echo(sum(ctx.obj["numbers"]))
    
    
    if __name__ == "__main__":
        cli()

CLI
    
    
    python app.py load sum

↓
    
    
    6

* * *

# 11\. Pipeline xử lý dữ liệu

Ví dụ:
    
    
    crawl
    
    ↓
    
    parse
    
    ↓
    
    clean
    
    ↓
    
    filter
    
    ↓
    
    export

Mỗi command làm **một việc duy nhất**.

Không làm nhiều việc.

* * *

# 12\. Thiết kế Service

Không nên:
    
    
    @cli.command()
    def export():
    
        crawl()
    
        parse()
    
        clean()
    
        export_epub()

Một command làm quá nhiều việc.

* * *

Nên:
    
    
    crawl
    
    ↓
    
    parse
    
    ↓
    
    clean
    
    ↓
    
    export

Mỗi bước độc lập.

Có thể kết hợp linh hoạt.

* * *

# 13\. Ví dụ xử lý văn bản
    
    
    @click.group(chain=True)

Command:
    
    
    load
    
    ↓
    
    uppercase
    
    ↓
    
    save

`load`

↓
    
    
    hello world

`uppercase`

↓
    
    
    HELLO WORLD

`save`

↓

ghi file.

Đây chính là Pipeline.

* * *

# 14\. Command Chaining có thay thế Subcommand không?

**Không.**

Subcommand:
    
    
    story db backup

Là **cấu trúc phân cấp**.

* * *

Chain:
    
    
    story backup upload

Là **thực hiện nhiều command liên tiếp**.

Hai khái niệm khác nhau.

Bạn có thể kết hợp cả hai trong một ứng dụng.

* * *

# 15\. Hạn chế của Chain

Không phải mọi CLI đều phù hợp.

Ví dụ:
    
    
    story crawler start stop

Không có nhiều ý nghĩa.

Nhưng:
    
    
    story clean export backup

lại rất hợp lý.

Hãy dùng Chain khi các command là các bước trong một quy trình.

* * *

# 16\. Mini Project
    
    
    import click
    
    @click.group(chain=True)
    @click.pass_context
    def cli(ctx):
    
        ctx.ensure_object(dict)
    
        ctx.obj["stories"] = []
    
    
    @cli.command()
    @click.pass_context
    def crawl(ctx):
    
        ctx.obj["stories"] = [
            "One Piece",
            "Naruto"
        ]
    
        click.echo("Đã crawl.")
    
    
    @cli.command()
    @click.pass_context
    def clean(ctx):
    
        ctx.obj["stories"] = [
            s.strip()
            for s in ctx.obj["stories"]
        ]
    
        click.echo("Đã clean.")
    
    
    @cli.command()
    @click.pass_context
    def export(ctx):
    
        click.echo("Export:")
    
        for story in ctx.obj["stories"]:
            click.echo(story)
    
    
    if __name__ == "__main__":
        cli()

CLI
    
    
    python app.py crawl clean export

↓
    
    
    Đã crawl.
    Đã clean.
    Export:
    One Piece
    Naruto

* * *

# 17\. Kết hợp với `AppContext`

Ở buổi 9 chúng ta đã có:
    
    
    @dataclass
    class AppContext:
    
        stories: list

Command:
    
    
    @pass_app
    def crawl(app):
    
        app.stories.append(...)

Command tiếp theo:
    
    
    @pass_app
    def export(app):
    
        ...

Đây là cách chuyên nghiệp hơn so với dùng `dict`.

* * *

# 18\. Kiến trúc hoàn chỉnh
    
    
    CLI
    
    ↓
    
    Group(chain=True)
    
    ↓
    
    AppContext
    
    ↓
    
    crawl
    
    ↓
    
    parse
    
    ↓
    
    clean
    
    ↓
    
    export
    
    ↓
    
    backup

Mỗi command chỉ chịu trách nhiệm cho **một bước** trong pipeline.

* * *

# 19\. Những lỗi người mới thường gặp

## ❌ Dùng Chain cho mọi thứ

Sai:
    
    
    story start stop pause

Các lệnh này loại trừ lẫn nhau.

Không nên chain.

* * *

## ❌ Không chia sẻ trạng thái
    
    
    @cli.command()
    def export():
    
        print(data)

`data` không tồn tại.

Hãy truyền qua `ctx.obj` hoặc `AppContext`.

* * *

## ❌ Một command làm quá nhiều việc
    
    
    crawl()
    
    parse()
    
    clean()
    
    backup()
    
    export()

Tất cả trong một command.

Khó tái sử dụng.

* * *

# 20\. Tổng kết

Các API quan trọng:

API| Mục đích  
---|---  
`@click.group(chain=True)`| Cho phép chạy nhiều command liên tiếp  
`ctx.obj`| Chia sẻ dữ liệu giữa các command  
`@click.pass_obj`| Truy cập `AppContext` trực tiếp  
`click.make_pass_decorator()`| Tạo decorator truyền đối tượng đúng kiểu  
  
Sơ đồ:
    
    
    Command 1
    
    ↓
    
    Command 2
    
    ↓
    
    Command 3
    
    ↓
    
    Command 4

Toàn bộ chạy trong **một Context**.

* * *

# Bài tập thực hành

## Bài 1

Tạo CLI:
    
    
    python app.py a b c

để in:
    
    
    A
    B
    C

sử dụng `chain=True`.

* * *

## Bài 2

Tạo pipeline:
    
    
    python app.py load uppercase print

  * `load` tạo chuỗi `"hello world"`. 
  * `uppercase` chuyển thành chữ hoa. 
  * `print` hiển thị kết quả. 



Dữ liệu phải được truyền qua `ctx.obj` hoặc `AppContext`.

* * *

## Bài 3

Tạo pipeline xử lý số:
    
    
    python app.py load double sum

  * `load` → `[1, 2, 3, 4]`
  * `double` → `[2, 4, 6, 8]`
  * `sum` → `20`



* * *

## Bài 4

Thiết kế `AppContext` với thuộc tính:
    
    
    @dataclass
    class AppContext:
        stories: list[str]

và cập nhật pipeline để sử dụng `@pass_app`.

* * *

## Bài 5 (Mini Project)

Xây dựng pipeline cho **Story Crawler** :
    
    
    story crawl parse clean export backup

Trong đó:

  * `crawl`: tạo danh sách chương truyện (giả lập). 
  * `parse`: chuyển dữ liệu thô thành cấu trúc chuẩn. 
  * `clean`: loại bỏ dữ liệu không hợp lệ. 
  * `export`: in danh sách đã xử lý. 
  * `backup`: mô phỏng sao lưu kết quả. 



Tất cả các bước dùng chung một `AppContext`, mỗi command chỉ thực hiện **một nhiệm vụ duy nhất**.

* * *

# Chuẩn bị cho buổi 11

Ở **Buổi 11** , chúng ta sẽ học về **Command Callback và Command Lifecycle** , bao gồm:

  * `invoke_without_command`
  * `ctx.invoked_subcommand`
  * Callback của `Group`
  * Khởi tạo tài nguyên (logger, config, database) đúng thời điểm 
  * Cleanup tài nguyên sau khi command kết thúc 
  * Thiết kế vòng đời (lifecycle) của một ứng dụng CLI chuyên nghiệp 



Đây là nền tảng để xây dựng các ứng dụng Click có khả năng khởi động nhanh, quản lý tài nguyên hiệu quả và dễ mở rộng.

