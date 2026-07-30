# Khóa học Click Deep Dive

# Buổi 3: Type System - Kiểu dữ liệu trong Click

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu cách Click tự động chuyển đổi kiểu dữ liệu. 
>   * Sử dụng các kiểu dữ liệu có sẵn như `INT`, `FLOAT`, `BOOL`, `STRING`, `Choice`, `Path`, `File`, `DateTime`, `UUID`. 
>   * Hiểu sự khác biệt giữa việc tự ép kiểu và để Click xử lý. 
>   * Biết cách thiết kế tham số an toàn và thân thiện với người dùng. 
> 


* * *

# 1\. Vì sao Click cần Type System?

Giả sử không dùng `type`:
    
    
    @click.command()
    @click.argument("age")
    def main(age):
        print(age)
        print(type(age))

Chạy:
    
    
    python app.py 25

Kết quả:
    
    
    25
    <class 'str'>

Mọi tham số dòng lệnh đều là **chuỗi (`str`)**.

Nếu muốn cộng số:
    
    
    result = age + 5

Bạn sẽ gặp lỗi:
    
    
    TypeError:
    can only concatenate str to str

* * *

## Cách cũ
    
    
    age = int(age)

Click cho phép làm việc này tự động.

* * *

# 2\. Kiểu `INT`
    
    
    import click
    
    @click.command()
    @click.argument("age", type=int)
    def main(age):
        click.echo(type(age))
        click.echo(age + 5)
    
    if __name__ == "__main__":
        main()

Chạy:
    
    
    python app.py 18

Kết quả:
    
    
    <class 'int'>
    23

* * *

Nếu nhập:
    
    
    python app.py abc

Click tự báo lỗi:
    
    
    Invalid value for 'AGE':
    'abc' is not a valid integer.

Không cần tự viết kiểm tra.

* * *

# 3\. `FLOAT`
    
    
    @click.argument("price", type=float)

Ví dụ:
    
    
    @click.command()
    @click.argument("price", type=float)
    @click.argument("quantity", type=int)
    def total(price, quantity):
        click.echo(price * quantity)

Chạy:
    
    
    python app.py 19.5 3

Kết quả:
    
    
    58.5

* * *

# 4\. `STRING`

Mặc định:
    
    
    type=str

Hai cách sau tương đương:
    
    
    @click.argument("name")

và
    
    
    @click.argument("name", type=str)

* * *

# 5\. `BOOL`

Lưu ý:

Thông thường **không dùng`type=bool`** cho Option.

Thay vào đó dùng:
    
    
    @click.option("--debug", is_flag=True)

Nếu bạn viết:
    
    
    @click.argument("enabled", type=bool)

thì Click sẽ chấp nhận các giá trị như:
    
    
    true
    false
    1
    0
    yes
    no

Tuy nhiên, với CLI thực tế, `is_flag=True` rõ ràng và phổ biến hơn.

* * *

# 6\. `Choice`

Một trong những kiểu được dùng nhiều nhất.

Ví dụ:
    
    
    @click.option(
        "--format",
        type=click.Choice(
            ["txt", "html", "epub"]
        )
    )

CLI:
    
    
    python app.py --format epub

OK.

* * *

Nếu:
    
    
    python app.py --format pdf

Click báo:
    
    
    Invalid value for '--format'

* * *

## `case_sensitive=False`
    
    
    type=click.Choice(
        ["txt", "html", "epub"],
        case_sensitive=False
    )

CLI:
    
    
    python app.py --format EPUB

vẫn hợp lệ.

* * *

# 7\. `IntRange`

Giới hạn số.
    
    
    @click.option(
        "--level",
        type=click.IntRange(1, 5)
    )

Chạy:
    
    
    python app.py --level 3

OK.

* * *
    
    
    python app.py --level 10

Báo lỗi.

Ứng dụng:

  * Mức log 
  * Độ ưu tiên 
  * Số luồng xử lý 



* * *

# 8\. `FloatRange`
    
    
    @click.option(
        "--score",
        type=click.FloatRange(0.0, 1.0)
    )

Ví dụ:
    
    
    python app.py --score 0.75

* * *

# 9\. `UUID`
    
    
    import uuid
    
    @click.argument(
        "id",
        type=click.UUID
    )

CLI:
    
    
    python app.py 550e8400-e29b-41d4-a716-446655440000

Kết quả trong Python là một đối tượng:
    
    
    uuid.UUID(...)

Không cần tự kiểm tra định dạng.

* * *

# 10\. `DateTime`
    
    
    @click.option(
        "--date",
        type=click.DateTime()
    )

CLI:
    
    
    python app.py --date "2026-07-23"

Kết quả:
    
    
    datetime.datetime(...)

Có thể chỉ định nhiều định dạng:
    
    
    click.DateTime(
        formats=[
            "%Y-%m-%d",
            "%d/%m/%Y"
        ]
    )

* * *

# 11\. `Path`

Đây là kiểu cực kỳ quan trọng.
    
    
    @click.argument(
        "path",
        type=click.Path()
    )

* * *

## Kiểm tra file có tồn tại
    
    
    @click.argument(
        "path",
        type=click.Path(exists=True)
    )

Nếu file không tồn tại:
    
    
    Invalid value for 'PATH'

* * *

## Chỉ cho phép file
    
    
    click.Path(
        file_okay=True,
        dir_okay=False
    )

* * *

## Chỉ cho phép thư mục
    
    
    click.Path(
        file_okay=False,
        dir_okay=True
    )

* * *

## Cho phép ghi
    
    
    click.Path(
        writable=True
    )

* * *

## Cho phép đọc
    
    
    click.Path(
        readable=True
    )

* * *

# 12\. `File`

Có thể mở file ngay.
    
    
    @click.argument(
        "file",
        type=click.File("r")
    )

Ví dụ:
    
    
    @click.command()
    @click.argument(
        "file",
        type=click.File("r")
    )
    def show(file):
        click.echo(file.read())

CLI:
    
    
    python app.py story.txt

Không cần:
    
    
    open(...)

* * *

## Ghi file
    
    
    type=click.File("w")

* * *

## Append
    
    
    type=click.File("a")

* * *

# 13\. `Tuple`

Ví dụ:
    
    
    @click.option(
        "--size",
        type=(int, int)
    )

CLI:
    
    
    python app.py --size 800 600

Kết quả:
    
    
    (800, 600)

Ứng dụng:

  * Width × Height 
  * X Y 
  * Row Column 



* * *

# 14\. Kết hợp nhiều kiểu

Ví dụ thực tế:
    
    
    import click
    
    @click.command()
    @click.argument(
        "database",
        type=click.Path(exists=True)
    )
    @click.option(
        "--format",
        type=click.Choice(
            ["txt", "epub", "html"],
            case_sensitive=False
        ),
        default="txt"
    )
    @click.option(
        "--threads",
        type=click.IntRange(1, 16),
        default=4
    )
    def export(database, format, threads):
        click.echo(f"DB      : {database}")
        click.echo(f"Format  : {format}")
        click.echo(f"Threads : {threads}")
    
    if __name__ == "__main__":
        export()

CLI:
    
    
    python app.py library.db --format epub --threads 8

Nếu:

  * File không tồn tại 
  * Threads = 100 
  * Format = pdf 



Click sẽ dừng ngay với thông báo lỗi rõ ràng.

* * *

# 15\. Thiết kế CLI thực tế

Giả sử dự án **Story Crawler**.

Không nên:
    
    
    story crawl website.txt

rồi tự kiểm tra.

Nên:
    
    
    @click.argument(
        "website",
        type=click.Path(exists=True)
    )

Hoặc:
    
    
    @click.option(
        "--format",
        type=click.Choice(
            ["epub", "html", "txt"]
        )
    )

Validation càng sớm, chương trình càng an toàn.

* * *

# 16\. Tổng kết Type System

Kiểu| Công dụng  
---|---  
`str`| Chuỗi  
`int`| Số nguyên  
`float`| Số thực  
`click.Choice`| Danh sách lựa chọn  
`click.IntRange`| Giới hạn số nguyên  
`click.FloatRange`| Giới hạn số thực  
`click.Path`| Kiểm tra đường dẫn  
`click.File`| Mở file trực tiếp  
`click.UUID`| Kiểm tra UUID  
`click.DateTime`| Chuyển thành `datetime`  
`tuple`| Nhận nhiều giá trị với nhiều kiểu  
  
* * *

# Bài tập thực hành

## Bài 1

Viết CLI:
    
    
    python app.py 15

Chỉ chấp nhận số nguyên.

* * *

## Bài 2

Viết:
    
    
    python app.py --format epub

Chỉ cho phép:

  * txt 
  * html 
  * epub 



* * *

## Bài 3

Viết:
    
    
    python app.py --threads 8

Chỉ chấp nhận từ **1 đến 16**.

* * *

## Bài 4

Viết:
    
    
    python app.py story.txt

Chỉ chấp nhận nếu file tồn tại và có thể đọc được.

* * *

## Bài 5 (Mini Project)

Tạo lệnh:
    
    
    story export library.db \
        --format epub \
        --threads 4 \
        --output exports/

Yêu cầu:

  * `library.db` phải tồn tại (`click.Path(exists=True)`). 
  * `--format` chỉ nhận `txt`, `html`, `epub`. 
  * `--threads` nằm trong khoảng `1–16`. 
  * `--output` phải là một thư mục (không phải tệp). 



* * *

## Chuẩn bị cho buổi 4

Ở **Buổi 4** , chúng ta sẽ học về **Prompt và Input tương tác** , bao gồm:

  * `click.prompt()`
  * `click.confirm()`
  * `hide_input`
  * `confirmation_prompt`
  * Giá trị mặc định và kiểm tra đầu vào 
  * Xây dựng các lệnh tương tác giống như `git`, `poetry`, hoặc trình cài đặt ứng dụng. 



Sau buổi đó, bạn sẽ có thể tạo các CLI vừa hỗ trợ tham số dòng lệnh, vừa tương tác trực tiếp với người dùng một cách chuyên nghiệp.

