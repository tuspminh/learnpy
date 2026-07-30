# Khóa học Click Deep Dive

# Buổi 10: Command Chaining & Pipeline trong Click

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu Command Chaining là gì. 
>   * Biết khi nào nên dùng `chain=True`. 
>   * Xây dựng pipeline CLI nhiều bước. 
>   * Truyền dữ liệu giữa các command. 
>   * Kết hợp Context + Nested Command + Pipeline. 
>   * Thiết kế workflow CLI giống các công cụ thực tế. 
> 


* * *

# 1\. Command Chaining là gì?

Thông thường Click chạy **một command duy nhất** :
    
    
    story crawl

Luồng:
    
    
    CLI
     |
     crawl
     |
     END

* * *

Nhưng có những tác vụ cần nhiều bước liên tiếp:

Ví dụ xử lý truyện:
    
    
    story process \
    crawl \
    parse \
    clean \
    export

Luồng:
    
    
    crawl
    
    ↓
    
    parse
    
    ↓
    
    clean
    
    ↓
    
    export

Đây gọi là:

# Command Chaining

* * *

# 2\. Ví dụ đơn giản

Ta tạo CLI:
    
    
    tool
    
    ├── hello
    
    ├── world

Muốn chạy:
    
    
    tool hello world

* * *

Code:
    
    
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

Chạy:
    
    
    python app.py hello world

Kết quả:
    
    
    Hello
    World

* * *

# 3\. `chain=True` hoạt động thế nào?

Bình thường:
    
    
    @click.group()

Click:
    
    
    group
     |
     command
     |
     stop

* * *

Có chain:
    
    
    @click.group(chain=True)

Click:
    
    
    group
    
     |
     +-- command 1
    
     |
     +-- command 2
    
     |
     +-- command 3

* * *

# 4\. Giới hạn của Command Chaining

Không phải mọi thứ đều dùng chain.

Ví dụ:

Không nên:
    
    
    story user add delete list

Vì:

  * không có pipeline logic. 



* * *

Nên dùng:
    
    
    story process crawl parse export

Vì:

  * kết quả bước trước là input bước sau. 



* * *

# 5\. Pipeline xử lý dữ liệu

Ví dụ:

Ta có dữ liệu:
    
    
    [
     "hello",
     "world"
    ]

Pipeline:
    
    
    load
    
    ↓
    
    uppercase
    
    ↓
    
    save

* * *

CLI:
    
    
    tool load uppercase save

* * *

# 6\. Truyền dữ liệu giữa các command

Click hỗ trợ bằng:
    
    
    ctx.obj

hoặc:
    
    
    return value

* * *

Cách đơn giản:
    
    
    import click
    
    
    @click.group(chain=True)
    @click.pass_context
    def cli(ctx):
    
        ctx.obj = {}
    
    
    @cli.command()
    @click.pass_context
    def load(ctx):
    
        ctx.obj["data"] = [
            "hello",
            "world"
        ]
    
    
    @cli.command()
    @click.pass_context
    def upper(ctx):
    
        data = ctx.obj["data"]
    
        ctx.obj["data"] = [
            x.upper()
            for x in data
        ]
    
    
    @cli.command()
    @click.pass_context
    def show(ctx):
    
        click.echo(
            ctx.obj["data"]
        )
    
    
    if __name__ == "__main__":
        cli()

* * *

Chạy:
    
    
    python app.py load upper show

Kết quả:
    
    
    ['HELLO', 'WORLD']

* * *

# 7\. Pipeline trong Story CLI

Ứng dụng đọc truyện:
    
    
    story pipeline \
    crawl \
    parse \
    download \
    save

* * *

Luồng:
    
    
    crawl
    
    ↓
    
    HTML
    
    ↓
    
    parse
    
    ↓
    
    Chapter Object
    
    ↓
    
    download
    
    ↓
    
    Images
    
    ↓
    
    save
    
    ↓
    
    Database

* * *

# 8\. Chain với Group Nested

Ví dụ:
    
    
    story
    
    └── pipeline
    
           ├── crawl
    
           ├── parse
    
           └── export

CLI:
    
    
    story pipeline crawl parse export

* * *

Code:
    
    
    @click.group()
    def story():
        pass
    
    
    @story.group(chain=True)
    def pipeline():
        pass

* * *

# 9\. Kết hợp Context

Kiến trúc:
    
    
    Root Context
    
        |
        |
     AppContext
    
        |
        |
    Pipeline Context
    
        |
        |
    Command

* * *

Ví dụ:
    
    
    class AppContext:
    
        def __init__(self):
    
            self.data = []

* * *

Root:
    
    
    ctx.obj = AppContext()

* * *

Pipeline:
    
    
    @click.pass_obj
    def crawl(app):
    
        app.data.append(
            "chapter1"
        )

* * *

# 10\. Return value trong Chain

Click hỗ trợ:
    
    
    return

Ví dụ:
    
    
    @click.command()
    def step1():
    
        return "data"

* * *

Nhưng:

Trong chain, Click thu thập kết quả:
    
    
    [
     result1,
     result2,
     result3
    ]

* * *

Ví dụ:
    
    
    @click.group(chain=True)
    def cli():
        pass
    
    
    @cli.command()
    def one():
    
        return 1
    
    
    @cli.command()
    def two():
    
        return 2

* * *

Kết quả nội bộ:
    
    
    [
    1,
    2
    ]

* * *

# 11\. Result Callback

Đây là phần quan trọng.

Ví dụ:
    
    
    @click.group(chain=True)
    def cli():
        pass
    
    
    @cli.result_callback()
    def process(results):
    
        print(results)

* * *

Command:
    
    
    @cli.command()
    def a():
    
        return "A"
    
    
    @cli.command()
    def b():
    
        return "B"

* * *

Chạy:
    
    
    tool a b

Result:
    
    
    [
    'A',
    'B'
    ]

* * *

# 12\. Ví dụ thực tế

Pipeline:
    
    
    story process crawl parse save

* * *

Command:
    
    
    @click.command()
    def crawl():
    
        html = "<html>"
    
        return html

* * *

Parse:
    
    
    @click.command()
    def parse(html):
    
        return chapter

* * *

Save:
    
    
    @click.command()
    def save(chapter):
    
        database.save(chapter)

* * *

# 13\. Pipeline Function Pattern

Một cách chuyên nghiệp hơn:

Mỗi bước trả về function.

Ví dụ:
    
    
    def crawl():
    
        def processor(data):
    
            return "HTML"
    
        return processor

* * *

Chain:
    
    
    Command
    
    ↓
    
    Processor
    
    ↓
    
    Data
    
    ↓
    
    Processor
    
    ↓
    
    Data

* * *

Đây là pattern:

# Unix Pipe Style

Giống:
    
    
    cat file | grep text | sort

* * *

# 14\. CLI kiểu Unix

Ví dụ:
    
    
    cat story.txt \
    | clean \
    | convert \
    | export

Mỗi bước:
    
    
    input
    
    ↓
    
    transform
    
    ↓
    
    output

* * *

Click có thể mô phỏng.

* * *

# 15\. Khi nào dùng Command Chaining?

Nên dùng:

Trường hợp| Ví dụ  
---|---  
Data pipeline| crawl → parse → save  
Build pipeline| clean → compile → package  
Migration| export → transform → import  
ETL| extract → transform → load  
  
* * *

Không nên dùng:

Trường hợp  
---  
CRUD command  
Admin command  
Config command  
  
* * *

# 16\. So sánh Nested Command và Chain

## Nested Command

Cấu trúc:
    
    
    story database backup

Ý nghĩa:
    
    
    chọn chức năng

* * *

## Chain

Cấu trúc:
    
    
    story process crawl parse save

Ý nghĩa:
    
    
    chuỗi xử lý

* * *

# 17\. Thiết kế Story CLI hoàn chỉnh

Sau 10 buổi:
    
    
    story
    
    ├── crawler
    
    │     ├── start
    
    │     ├── stop
    
    │     └── status
    
    
    ├── database
    
    │     ├── backup
    
    │     └── restore
    
    
    ├── pipeline
    
    │     ├── crawl
    
    │     ├── parse
    
    │     └── export
    
    
    └── plugin
    
          ├── install
    
          └── list

* * *

Ví dụ:

Quản lý:
    
    
    story crawler start

Pipeline:
    
    
    story pipeline crawl parse export

* * *

# 18\. Bài tập thực hành

## Bài 1

Tạo:
    
    
    tool hello world test

với:
    
    
    chain=True

* * *

## Bài 2

Tạo pipeline:
    
    
    text upper reverse show

Input:
    
    
    hello

Output:
    
    
    OLLEH

* * *

## Bài 3

Tạo:
    
    
    story pipeline crawl parse save

Mỗi bước trả về dữ liệu.

* * *

## Bài 4

Dùng:
    
    
    @result_callback()

để nhận toàn bộ kết quả.

* * *

## Bài 5 - Mini Project

Xây dựng:
    
    
    Story Pipeline
    
    crawl
     |
    parse
     |
    clean
     |
    save

Yêu cầu:

Chạy:
    
    
    story pipeline crawl parse clean save

Kết quả:
    
    
    Crawler running...
    Parsing chapters...
    Cleaning content...
    Saving database...
    Done

* * *

# Tổng kết Buổi 10

Bạn đã học:

Thành phần| Ý nghĩa  
---|---  
`chain=True`| Chạy nhiều command liên tiếp  
Pipeline| Luồng xử lý dữ liệu  
`ctx.obj`| Chia sẻ trạng thái  
return value| Trả kết quả command  
`result_callback`| Nhận toàn bộ pipeline  
  
Kiến trúc:
    
    
    Command Tree
    
    +
    
    Context
    
    +
    
    Pipeline
    
    =
    
    CLI Framework chuyên nghiệp

* * *

# Buổi 11 tiếp theo (theo roadmap)

**Config Management trong Click**

Nội dung:

  * Quản lý cấu hình CLI. 
  * File config. 
  * Environment variables. 
  * Override thứ tự: 
    * Default 
    * Config file 
    * Environment 
    * Command line 
  * Xây dựng `ConfigManager`. 
  * Kết hợp với `AppContext`. 



Đây là bước cần thiết trước khi xây dựng CLI thực tế.

