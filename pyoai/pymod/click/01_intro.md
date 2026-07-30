# Khóa học Click Deep Dive

# Buổi 1: Giới thiệu Click và xây dựng CLI đầu tiên

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ hiểu:
> 
>   * CLI là gì. 
>   * Tại sao Click lại phổ biến. 
>   * Click hoạt động như thế nào. 
>   * Viết được ứng dụng CLI đầu tiên. 
>   * Hiểu decorator `@click.command()`. 
>   * Hiểu cơ chế parse command line. 
>   * Biết cách tổ chức project CLI nhỏ. 
> 


* * *

# 1\. CLI là gì?

CLI (Command Line Interface) là chương trình được điều khiển bằng dòng lệnh.

Ví dụ:
    
    
    git status
    
    docker ps
    
    pip install requests
    
    python main.py
    
    uv sync

Thay vì bấm nút như GUI, người dùng gõ lệnh.

Ví dụ:
    
    
    story crawl
    
    story export
    
    story backup

CLI đặc biệt phù hợp để:

  * Automation 
  * DevOps 
  * Quản trị server 
  * Data Engineering 
  * AI Tool 
  * Build Tool 
  * Internal Tool 



* * *

# 2\. Click là gì?

Click là framework giúp xây dựng CLI rất nhanh.

Tên đầy đủ:

> **Command Line Interface Creation Kit**

Được tạo bởi:

**Armin Ronacher**

(cũng là tác giả Flask)

* * *

Không dùng Click, Python có:
    
    
    sys.argv

hoặc
    
    
    argparse

Ví dụ:
    
    
    import sys
    
    print(sys.argv)

Chạy
    
    
    python app.py hello world

Kết quả
    
    
    [
     "app.py",
     "hello",
     "world"
    ]

Tự parse rất cực.

* * *

argparse khá dài:
    
    
    import argparse
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--name")
    
    args = parser.parse_args()
    
    print(args.name)

Click đơn giản hơn nhiều.

* * *

# 3\. Cài đặt Click
    
    
    pip install click

Kiểm tra
    
    
    python -c "import click;print(click.__version__)"

* * *

# 4\. Hello Click

Tạo file
    
    
    hello.py
    
    
    import click
    
    
    @click.command()
    def hello():
        print("Hello Click!")

Chạy
    
    
    python hello.py

Không có gì xảy ra!

Đây là lỗi mà người mới học gần như ai cũng gặp.

Tại sao?

* * *

## Vì decorator chỉ đăng ký command.

Nó chưa được gọi.

Phải thêm
    
    
    hello()

đầy đủ
    
    
    import click
    
    
    @click.command()
    def hello():
        print("Hello Click!")
    
    
    if __name__ == "__main__":
        hello()

Bây giờ chạy
    
    
    python hello.py

Kết quả
    
    
    Hello Click!

* * *

# 5\. Điều gì xảy ra bên trong?

Decorator
    
    
    @click.command()

không chỉ đơn giản là gọi hàm.

Nó biến hàm thành một object Command.

Trước:
    
    
    hello
    
    ↓
    
    function

Sau decorator
    
    
    hello
    
    ↓
    
    Click Command

Có thể kiểm tra
    
    
    import click
    
    
    @click.command()
    def hello():
        pass
    
    
    print(type(hello))

Kết quả
    
    
    <class 'click.core.Command'>

Đây là điểm rất quan trọng.

Sau decorator:
    
    
    Function
    
    ↓
    
    Command Object
    
    ↓
    
    Click Runtime
    
    ↓
    
    Parser
    
    ↓
    
    Execute

* * *

# 6\. Click Runtime hoạt động thế nào?

Giả sử
    
    
    python hello.py

Click làm các bước sau:
    
    
    OS
    
    ↓
    
    sys.argv
    
    ↓
    
    Click
    
    ↓
    
    Parse
    
    ↓
    
    Validate
    
    ↓
    
    Convert Type
    
    ↓
    
    Execute Function

Nếu có
    
    
    python hello.py --help

Click không gọi hàm.

Nó tự hiển thị help.

* * *

# 7\. Help miễn phí

Đổi chương trình thành
    
    
    import click
    
    
    @click.command()
    def hello():
        """My first click app."""
        print("Hello")

Chạy
    
    
    python hello.py --help

Kết quả
    
    
    Usage:
    
    hello.py [OPTIONS]
    
    My first click app.
    
    Options:
    
    --help

Bạn không cần viết.

Click sinh tự động.

* * *

# 8\. Click thay thế print()

Thay vì
    
    
    print("Hello")

nên dùng
    
    
    click.echo("Hello")

Ví dụ
    
    
    import click
    
    
    @click.command()
    def hello():
        click.echo("Hello Click")

Tại sao?

Vì

`click.echo()`

hỗ trợ:

  * Unicode 
  * Windows Console 
  * UTF-8 
  * Redirect 
  * Color 
  * Testing 



Trong các bài sau, chúng ta sẽ luôn ưu tiên `click.echo()`.

* * *

# 9\. Command Name

Mặc định
    
    
    @click.command()
    def hello():
        ...

Tên command là
    
    
    hello

Có thể đổi
    
    
    @click.command("hi")
    def hello():
        click.echo("Hello")

Help sẽ hiển thị
    
    
    hi

* * *

# 10\. Docstring

Docstring sẽ trở thành phần mô tả.
    
    
    @click.command()
    def hello():
        """
        Đây là chương trình đầu tiên.
        """

Khi chạy
    
    
    --help

sẽ hiển thị
    
    
    Đây là chương trình đầu tiên.

* * *

# 11\. Tổ chức project nhỏ

Thay vì
    
    
    hello.py

nên tạo
    
    
    mycli/
    
    │
    ├── app.py
    │
    └── requirements.txt

**app.py**
    
    
    import click
    
    
    @click.command()
    def cli():
        """My CLI"""
        click.echo("Hello Click")
    
    
    if __name__ == "__main__":
        cli()

Chạy
    
    
    python app.py

* * *

# 12\. Ví dụ thực tế

Một CLI tính diện tích hình chữ nhật:
    
    
    import click
    
    
    @click.command()
    @click.option("--width", type=float, required=True)
    @click.option("--height", type=float, required=True)
    def area(width, height):
        """Tính diện tích hình chữ nhật."""
        click.echo(f"Diện tích: {width * height}")
    
    
    if __name__ == "__main__":
        area()

Chạy:
    
    
    python app.py --width 5 --height 3

Kết quả:
    
    
    Diện tích: 15.0

Bạn chưa cần hiểu `@click.option` ngay; chúng ta sẽ học chi tiết ở buổi 2. Mục đích ở đây là thấy Click giúp định nghĩa CLI rất ngắn gọn.

* * *

# 13\. So sánh `sys.argv`, `argparse` và Click

Tiêu chí| sys.argv| argparse| Click  
---|---|---|---  
Có sẵn trong Python| ✅| ✅| ❌  
Tự parse tham số| ❌| ✅| ✅  
Tự sinh `--help`| ❌| ✅| ✅  
Hỗ trợ nhiều command| ❌| Có nhưng khá dài| ✅  
Dễ mở rộng| ❌| Trung bình| ✅  
Trải nghiệm lập trình| Thấp| Khá| Rất tốt  
  
* * *

# 14\. Những điều cần ghi nhớ

  * `@click.command()` biến một hàm Python thành một **Command Object**. 
  * Hàm decorated phải được gọi (`cli()` hoặc `hello()`) để Click xử lý dòng lệnh. 
  * `click.echo()` là lựa chọn tốt hơn `print()` trong ứng dụng CLI. 
  * `--help` được Click tạo tự động từ tên hàm và docstring. 
  * Click đọc `sys.argv`, phân tích tham số, kiểm tra kiểu dữ liệu rồi mới gọi hàm của bạn. 



* * *

# Bài tập thực hành

## Bài 1

Viết chương trình:
    
    
    python app.py

Hiển thị:
    
    
    Welcome to Click

* * *

## Bài 2

Đổi tên command thành:
    
    
    welcome

và kiểm tra:
    
    
    python app.py --help

Quan sát sự thay đổi trong phần `Usage`.

* * *

## Bài 3

Thêm docstring:
    
    
    """
    Ứng dụng CLI đầu tiên của tôi.
    """

Sau đó chạy:
    
    
    python app.py --help

và xem mô tả có được hiển thị hay không.

* * *

## Bài 4

Thay `print()` bằng `click.echo()` và so sánh kết quả.

* * *

## Chuẩn bị cho buổi 2

Ở buổi tiếp theo, chúng ta sẽ đi sâu vào **Arguments** và **Options** — nền tảng của mọi CLI. Bạn sẽ học cách xây dựng các lệnh như:
    
    
    story add "Truyện mới"
    
    story remove 12
    
    story search "Harry Potter"
    
    story export --format epub --output books/

Đây là bước đầu để xây dựng CLI chuyên nghiệp giống `git`, `docker` hay `uv`, và cũng sẽ là nền tảng cho dự án **Story Crawler CLI** mà chúng ta sẽ phát triển xuyên suốt khóa học.

