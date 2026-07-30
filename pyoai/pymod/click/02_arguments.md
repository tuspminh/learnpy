# Khóa học Click Deep Dive

# Buổi 2: Arguments và Options - Nền tảng của mọi CLI

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu rõ sự khác nhau giữa **Argument** và **Option**. 
>   * Biết khi nào nên dùng mỗi loại. 
>   * Sử dụng được `@click.argument()` và `@click.option()`. 
>   * Hiểu các thuộc tính: `default`, `required`, `multiple`, `nargs`, `count`, `flag`. 
>   * Thiết kế giao diện dòng lệnh thân thiện và dễ sử dụng. 
> 


* * *

# 1\. Argument và Option khác nhau như thế nào?

Đây là kiến thức quan trọng nhất của buổi học.

Giả sử có lệnh:
    
    
    cp source.txt backup.txt

Ở đây:

  * `source.txt` là **Argument**
  * `backup.txt` là **Argument**



Không có tên.

* * *

Một ví dụ khác:
    
    
    python app.py story.txt

`story.txt`

là Argument.

* * *

Trong khi đó
    
    
    python app.py --output result.txt

`--output`

là Option.

* * *

## Quy tắc

Argument:

  * Không có tên 
  * Thường bắt buộc 
  * Có thứ tự 



Option:

  * Có tên 
  * Có thể không bắt buộc 
  * Có giá trị mặc định 



* * *

Ví dụ:
    
    
    story export novel.db --format epub --output books/

Thành phần| Loại  
---|---  
novel.db| Argument  
\--format| Option  
\--output| Option  
  
* * *

# 2\. Argument đầu tiên
    
    
    import click
    
    
    @click.command()
    @click.argument("name")
    def hello(name):
        click.echo(f"Hello {name}")
    
    
    if __name__ == "__main__":
        hello()

Chạy
    
    
    python app.py Alice

Kết quả
    
    
    Hello Alice

* * *

Nếu
    
    
    python app.py Bob
    
    
    Hello Bob

* * *

# 3\. Nếu không truyền Argument?
    
    
    python app.py

Click báo lỗi:
    
    
    Missing argument 'NAME'

Đây là validation tự động.

* * *

# 4\. Nhiều Argument
    
    
    @click.command()
    @click.argument("first")
    @click.argument("last")
    def hello(first, last):
        click.echo(f"{first} {last}")

Chạy
    
    
    python app.py Nguyen Van

Kết quả
    
    
    Nguyen Van

* * *

# 5\. Thứ tự rất quan trọng
    
    
    @click.argument("a")
    @click.argument("b")

CLI
    
    
    python app.py 5 10

Kết quả
    
    
    a = 5
    b = 10

Nếu đổi
    
    
    python app.py 10 5

thì
    
    
    a = 10
    b = 5

Argument phụ thuộc hoàn toàn vào vị trí.

* * *

# 6\. Option đầu tiên
    
    
    @click.command()
    @click.option("--name")
    def hello(name):
        click.echo(f"Hello {name}")

Chạy
    
    
    python app.py --name Alice

Kết quả
    
    
    Hello Alice

* * *

Không cần theo thứ tự.

Ví dụ sau vẫn đúng:
    
    
    python app.py --name Bob

* * *

# 7\. Option có default
    
    
    @click.option("--name", default="Guest")
    
    
    import click
    
    
    @click.command()
    @click.option("--name", default="Guest")
    def hello(name):
        click.echo(f"Hello {name}")
    
    
    if __name__ == "__main__":
        hello()

Chạy
    
    
    python app.py
    
    
    Hello Guest

* * *

Hoặc
    
    
    python app.py --name Alice
    
    
    Hello Alice

* * *

# 8\. Option bắt buộc
    
    
    @click.option("--name", required=True)

Ví dụ
    
    
    import click
    
    
    @click.command()
    @click.option("--name", required=True)
    def hello(name):
        click.echo(name)
    
    
    if __name__ == "__main__":
        hello()

Nếu
    
    
    python app.py

Click báo
    
    
    Missing option '--name'

* * *

# 9\. Default + Required?

Không hợp lý.
    
    
    @click.option(
        "--name",
        default="Guest",
        required=True
    )

Nếu đã có default thì không cần required.

* * *

# 10\. Short Option

Có thể viết
    
    
    @click.option("-n", "--name")

Chạy
    
    
    python app.py -n Alice

hoặc
    
    
    python app.py --name Alice

Đều đúng.

* * *

# 11\. Nhiều Option
    
    
    @click.command()
    @click.option("--name")
    @click.option("--age")
    def user(name, age):
        click.echo(name)
        click.echo(age)

CLI
    
    
    python app.py --name Alice --age 20

Hoặc
    
    
    python app.py --age 20 --name Alice

Option không phụ thuộc thứ tự.

* * *

# 12\. Flag

Flag là Option không có giá trị.

Ví dụ
    
    
    git status --short

`--short`

chỉ bật/tắt.

Click:
    
    
    @click.option("--debug", is_flag=True)

Ví dụ
    
    
    import click
    
    
    @click.command()
    @click.option("--debug", is_flag=True)
    def run(debug):
        click.echo(debug)
    
    
    if __name__ == "__main__":
        run()

Chạy
    
    
    python app.py
    
    
    False

* * *
    
    
    python app.py --debug
    
    
    True

* * *

# 13\. Count

Một số CLI hỗ trợ:
    
    
    -v
    -vv
    -vvv

Click:
    
    
    @click.option("-v", count=True)

Ví dụ
    
    
    import click
    
    
    @click.command()
    @click.option("-v", count=True)
    def cli(v):
        click.echo(v)
    
    
    if __name__ == "__main__":
        cli()
    
    
    python app.py
    
    
    0
    
    
    python app.py -v
    
    
    1
    
    
    python app.py -vvv
    
    
    3

Đây là cách phổ biến để điều khiển mức log.

* * *

# 14\. Multiple Option

Ví dụ
    
    
    story export --tag action --tag fantasy --tag magic

Click
    
    
    @click.option(
        "--tag",
        multiple=True
    )

Ví dụ
    
    
    import click
    
    
    @click.command()
    @click.option("--tag", multiple=True)
    def cli(tag):
        click.echo(tag)
    
    
    if __name__ == "__main__":
        cli()

Chạy
    
    
    python app.py --tag a --tag b --tag c

Kết quả
    
    
    ('a', 'b', 'c')

Lưu ý: Click trả về **tuple** , không phải list.

* * *

# 15\. nargs

Một Option nhận nhiều giá trị.
    
    
    @click.option(
        "--point",
        nargs=2,
        type=float
    )

CLI
    
    
    python app.py --point 10 20

Kết quả
    
    
    (10.0, 20.0)

Ứng dụng:

  * tọa độ 
  * kích thước 
  * vùng chọn 



* * *

# 16\. Kết hợp Argument và Option

Ví dụ tính diện tích hình chữ nhật:
    
    
    import click
    
    
    @click.command()
    @click.argument("width", type=float)
    @click.argument("height", type=float)
    @click.option("--unit", default="m²")
    def area(width, height, unit):
        """Tính diện tích hình chữ nhật."""
        result = width * height
        click.echo(f"Diện tích: {result} {unit}")
    
    
    if __name__ == "__main__":
        area()

Chạy:
    
    
    python app.py 5 3

Kết quả:
    
    
    Diện tích: 15.0 m²

Hoặc:
    
    
    python app.py 5 3 --unit cm²

Kết quả:
    
    
    Diện tích: 15.0 cm²

* * *

# 17\. Thiết kế CLI tốt

Không nên:
    
    
    story --input novel.txt

Nếu `novel.txt` luôn bắt buộc, hãy dùng **Argument** :
    
    
    story novel.txt

* * *

Không nên:
    
    
    story export output_folder

Nếu định dạng xuất là tùy chọn, hãy dùng:
    
    
    story export novel.db --format epub --output books/

Nguyên tắc:

  * Dữ liệu chính → **Argument**
  * Thiết lập, cấu hình → **Option**



* * *

# 18\. Tổng kết

Đặc điểm| Argument| Option  
---|---|---  
Có tên| ❌| ✅  
Có thứ tự| ✅| ❌  
Thường bắt buộc| ✅| ❌  
Có default| ❌| ✅  
Phù hợp cho| Dữ liệu chính| Thiết lập  
  
* * *

# Bài tập thực hành

## Bài 1

Viết CLI:
    
    
    python app.py Alice

Hiển thị:
    
    
    Xin chào Alice!

* * *

## Bài 2

Viết CLI:
    
    
    python app.py 8 6

Tính chu vi hình chữ nhật.

* * *

## Bài 3

Viết CLI:
    
    
    python app.py 8 6 --unit cm

Hiển thị:
    
    
    Chu vi: 28 cm

* * *

## Bài 4

Viết CLI nhận nhiều tag:
    
    
    python app.py --tag python --tag click --tag cli

In từng tag trên một dòng.

* * *

## Bài 5 (Mini Project)

Xây dựng lệnh:
    
    
    story add "Harry Potter"
    
    story remove 15
    
    story search "Magic"
    
    story export library.db --format epub --output exports/

Hiện tại bạn chỉ cần dùng `click.echo()` để in ra các tham số nhận được, chưa cần xử lý logic thật.

* * *

## Chuẩn bị cho buổi 3

Ở **Buổi 3** , chúng ta sẽ tìm hiểu **Type System của Click**. Đây là một trong những điểm mạnh nhất của Click, giúp tự động chuyển đổi và kiểm tra kiểu dữ liệu như:

  * `int`, `float`, `bool`
  * `Choice`
  * `Path`
  * `File`
  * `DateTime`
  * `UUID`
  * `Tuple`



Bạn cũng sẽ học cách tạo **kiểu dữ liệu tùy chỉnh (Custom Parameter Type)** , rất hữu ích khi xây dựng CLI lớn như dự án **Story Crawler** , ví dụ kiểm tra URL nguồn truyện, định dạng tệp, hoặc ID plugin ngay từ lúc phân tích tham số.

