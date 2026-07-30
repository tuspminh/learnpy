# Khóa học Click Deep Dive

# Buổi 12: Parameter System - Làm chủ Argument, Option và Validation

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu hệ thống Parameter bên trong Click. 
>   * Phân biệt `Argument` và `Option`. 
>   * Hiểu cách Click parse command line. 
>   * Biết cách validate dữ liệu đầu vào. 
>   * Sử dụng `callback` của parameter. 
>   * Tạo CLI có trải nghiệm người dùng chuyên nghiệp. 
> 


* * *

# 1\. Parameter trong Click là gì?

Khi người dùng chạy:
    
    
    story crawler start --threads 8 --url https://example.com

Click phải phân tích:
    
    
    crawler
    start
    --threads
    8
    --url
    https://example.com

Các thành phần này gọi chung là:
    
    
    Parameter

Trong Click:
    
    
    Parameter
    
    ├── Argument
    │
    └── Option

* * *

# 2\. Kiến trúc Parameter
    
    
    click.Parameter
    
            |
            |
      ----------------
    
      |              |
    
    Argument       Option

* * *

# 3\. Argument là gì?

Argument là giá trị bắt buộc theo vị trí.

Ví dụ:
    
    
    story add book.txt

`book.txt` là argument.

* * *

Code:
    
    
    import click
    
    
    @click.command()
    @click.argument("filename")
    def add(filename):
    
        click.echo(filename)
    
    
    if __name__ == "__main__":
        add()

* * *

Chạy:
    
    
    python app.py hello.txt

Kết quả:
    
    
    hello.txt

* * *

# 4\. Argument bắt buộc

Mặc định:
    
    
    @click.argument("filename")

là:
    
    
    required=True

* * *

Nếu chạy:
    
    
    python app.py

Click báo:
    
    
    Missing argument 'FILENAME'

* * *

# 5\. Argument tùy chọn

Có thể:
    
    
    @click.argument(
        "filename",
        required=False
    )

Ví dụ:
    
    
    @click.command()
    @click.argument(
        "name",
        required=False
    )
    def hello(name):
    
        click.echo(name)

* * *

Chạy:
    
    
    python app.py

Kết quả:
    
    
    None

* * *

# 6\. Nhiều Argument

Ví dụ:
    
    
    story copy a.txt b.txt

Code:
    
    
    @click.command()
    @click.argument(
        "files",
        nargs=2
    )
    def copy(files):
    
        click.echo(files)

* * *

Kết quả:
    
    
    ('a.txt', 'b.txt')

* * *

# 7\. Variadic Argument

Nhận nhiều giá trị:
    
    
    @click.argument(
        "files",
        nargs=-1
    )

Ví dụ:
    
    
    story delete a b c d

Nhận:
    
    
    (
    'a',
    'b',
    'c',
    'd'
    )

* * *

# 8\. Option là gì?

Option có dấu:
    
    
    -
    --

Ví dụ:
    
    
    --threads 8

* * *

Code:
    
    
    @click.command()
    @click.option(
        "--threads"
    )
    def start(threads):
    
        click.echo(threads)

* * *

Chạy:
    
    
    python app.py --threads 8

↓
    
    
    8

* * *

# 9\. Short Option

Có thể tạo:
    
    
    @click.option(
        "-t",
        "--threads"
    )

CLI:
    
    
    story start -t 8

hoặc:
    
    
    story start --threads 8

* * *

# 10\. Default Value
    
    
    @click.option(
        "--threads",
        default=4
    )

* * *

Nếu:
    
    
    story start

↓
    
    
    4

* * *

Nếu:
    
    
    story start --threads 10

↓
    
    
    10

* * *

# 11\. Type System

Click tự chuyển kiểu:
    
    
    @click.option(
        "--threads",
        type=int
    )

* * *

CLI:
    
    
    --threads 8

Python nhận:
    
    
    8

không phải:
    
    
    "8"

* * *

Các type thường dùng:

Type| Ý nghĩa  
---|---  
`str`| Chuỗi  
`int`| Số nguyên  
`float`| Số thực  
`bool`| Boolean  
`File`| File object  
`Path`| Đường dẫn  
`Choice`| Danh sách lựa chọn  
  
* * *

# 12\. Choice

Ví dụ:

Chỉ cho phép:
    
    
    json
    xml
    csv

Code:
    
    
    @click.option(
        "--format",
        type=click.Choice(
            [
                "json",
                "xml",
                "csv"
            ]
        )
    )
    def export(format):
    
        click.echo(format)

* * *

CLI:
    
    
    --format json

OK.

* * *

Nhưng:
    
    
    --format pdf

Lỗi:
    
    
    Invalid choice

* * *

# 13\. Path Type

Ví dụ:
    
    
    @click.option(
        "--output",
        type=click.Path()
    )

CLI:
    
    
    --output data.txt

* * *

Click kiểm tra đường dẫn.

* * *

## Kiểm tra file tồn tại
    
    
    @click.option(
        "--input",
        type=click.Path(
            exists=True
        )
    )

* * *

Nếu file không tồn tại:
    
    
    Path does not exist

* * *

# 14\. Boolean Flag

Ví dụ:
    
    
    story crawl --verbose

* * *

Code:
    
    
    @click.option(
        "--verbose",
        is_flag=True
    )
    def crawl(verbose):
    
        if verbose:
            click.echo("Debug mode")

* * *

Không truyền:
    
    
    False

Có truyền:
    
    
    True

* * *

# 15\. Dual Flag

Ví dụ:
    
    
    --color / --no-color

Code:
    
    
    @click.option(
        "--color/--no-color",
        default=True
    )

* * *

CLI:
    
    
    --no-color

↓
    
    
    False

* * *

# 16\. Callback Validation

Đây là phần rất quan trọng.

Ví dụ:

Không cho phép:
    
    
    threads <= 0

* * *

Code:
    
    
    def validate_threads(
        ctx,
        param,
        value
    ):
    
        if value <= 0:
    
            raise click.BadParameter(
                "threads must > 0"
            )
    
        return value

* * *

Gắn vào:
    
    
    @click.option(
        "--threads",
        type=int,
        callback=validate_threads
    )

* * *

CLI:
    
    
    --threads 0

↓
    
    
    Invalid value:
    threads must > 0

* * *

# 17\. Callback Parameter hoạt động thế nào?

Luồng:
    
    
    CLI input
    
    ↓
    
    Convert Type
    
    ↓
    
    Callback
    
    ↓
    
    Command Function

Ví dụ:
    
    
    "--threads 8"
    
    ↓
    
    int(8)
    
    ↓
    
    validate_threads()
    
    ↓
    
    start(threads=8)

* * *

# 18\. Dynamic Default

Đôi khi default không cố định.

Ví dụ:
    
    
    def get_threads():
    
        return 8

* * *

Dùng:
    
    
    @click.option(
        "--threads",
        default=get_threads
    )

* * *

Mỗi lần chạy Click sẽ gọi:
    
    
    get_threads()

* * *

# 19\. Lấy giá trị từ Environment Variable

Ví dụ:
    
    
    @click.option(
        "--database",
        envvar="STORY_DB"
    )

* * *

Windows:
    
    
    set STORY_DB=data.db

Linux:
    
    
    export STORY_DB=data.db

Chạy:
    
    
    story db backup

Click tự lấy:
    
    
    data.db

* * *

# 20\. ParameterSource

Click có thể biết giá trị đến từ đâu.

Ví dụ:
    
    
    ctx.get_parameter_source("threads")

Nguồn có thể:
    
    
    COMMANDLINE
    DEFAULT
    ENVIRONMENT
    DEFAULT_MAP

* * *

Ví dụ:
    
    
    @click.pass_context
    def start(ctx, threads):
    
        source = ctx.get_parameter_source(
            "threads"
        )
    
        click.echo(source)

* * *

CLI:
    
    
    --threads 8

↓
    
    
    COMMANDLINE

* * *

Không truyền:

↓
    
    
    DEFAULT

* * *

# 21\. Thiết kế Story CLI thực tế

Ví dụ:
    
    
    story crawler start \
    --url https://example.com \
    --threads 8 \
    --format json \
    --verbose

* * *

Code:
    
    
    @click.command()
    @click.option(
        "--url",
        required=True
    )
    @click.option(
        "--threads",
        default=4,
        type=int
    )
    @click.option(
        "--format",
        type=click.Choice(
            [
                "json",
                "xml"
            ]
        )
    )
    @click.option(
        "--verbose",
        is_flag=True
    )
    def start(
        url,
        threads,
        format,
        verbose
    ):
    
        ...

* * *

# 22\. Argument hay Option?

Quy tắc:

## Argument

Dữ liệu chính:
    
    
    story open book.txt

`book.txt`

* * *

## Option

Cấu hình:
    
    
    --threads 8
    --verbose
    --format json

* * *

Ví dụ:
    
    
    story convert input.txt --format pdf

Đúng.

Không nên:
    
    
    story convert --input input.txt

trừ khi input là tùy chọn.

* * *

# 23\. Kiến trúc Parameter chuyên nghiệp
    
    
    Command
    
    |
    
    Parameters
    
    |
    
    Validation
    
    |
    
    Service
    
    |
    
    Business Logic

Command không nên tự kiểm tra:
    
    
    if threads < 0:

Hãy để Parameter xử lý.

* * *

# 24\. Mini Project

Xây dựng:
    
    
    story crawler start

với:
    
    
    --url
    --threads
    --format
    --verbose

Yêu cầu:

* * *

## URL

Bắt buộc:
    
    
    required=True

* * *

## threads

Mặc định:
    
    
    4

Không được:
    
    
    <=0

* * *

## format

Chỉ nhận:
    
    
    json
    xml

* * *

## verbose

Flag:
    
    
    --verbose

* * *

Kết quả:
    
    
    python app.py crawler start \
    --url https://example.com \
    --threads 8 \
    --format json \
    --verbose

In:
    
    
    URL: https://example.com
    Threads: 8
    Format: json
    Verbose: True

* * *

# Tổng kết Buổi 12

Bạn đã học:

Thành phần| Mục đích  
---|---  
`Argument`| Giá trị theo vị trí  
`Option`| Tham số cấu hình  
`type`| Ép kiểu  
`Choice`| Giới hạn lựa chọn  
`Path`| Kiểm tra đường dẫn  
`is_flag`| Boolean flag  
`callback`| Validation  
`envvar`| Environment config  
`ParameterSource`| Biết nguồn giá trị  
  
* * *

# Bài tập nâng cao

Thiết kế command:
    
    
    story export novel.epub \
    --format epub \
    --quality high \
    --compress \
    --output ./dist

Yêu cầu:

  1. `novel.epub` là Argument. 
  2. `format` chỉ nhận: 
     * epub 
     * pdf 
     * mobi 
  3. `quality`: 
     * low 
     * medium 
     * high 
  4. `compress` là flag. 
  5. `output` phải là thư mục tồn tại. 



* * *

# Chuẩn bị Buổi 13

**Buổi 13: Advanced Option Design**

Chúng ta sẽ học:

  * Option class. 
  * Custom Option. 
  * Multi-value option. 
  * Tuple option. 
  * Password option. 
  * Prompt nhập liệu. 
  * Confirmation. 
  * Hidden input. 
  * Thiết kế CLI tương tác (interactive CLI). 



Đây là bước để xây dựng các công cụ CLI chuyên nghiệp giống:

  * GitHub CLI 
  * AWS CLI 
  * Docker CLI 
  * Poetry CLI 
  * Terraform CLI.

