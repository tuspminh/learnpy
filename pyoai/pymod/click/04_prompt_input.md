# Khóa học Click Deep Dive

# Buổi 4: Prompt, Confirmation và Input tương tác

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Biết khi nào nên dùng Prompt thay vì Argument hoặc Option. 
>   * Sử dụng `click.prompt()`, `click.confirm()`. 
>   * Hiểu `prompt=True`, `hide_input`, `confirmation_prompt`. 
>   * Xây dựng CLI tương tác giống `git`, `poetry`, `pip`, `docker login`. 
>   * Thiết kế trải nghiệm người dùng (UX) tốt cho ứng dụng CLI. 
> 


* * *

# 1\. CLI có hai kiểu làm việc

## Kiểu 1: Non-interactive (không tương tác)

Người dùng truyền đầy đủ tham số:
    
    
    story add "Harry Potter" --author "J.K. Rowling"

Ưu điểm:

  * Dễ dùng trong script. 
  * Dễ tự động hóa (automation). 
  * Phù hợp CI/CD. 



* * *

## Kiểu 2: Interactive (tương tác)

CLI sẽ hỏi từng bước:
    
    
    Tên truyện:
    > Harry Potter
    
    Tác giả:
    > J.K. Rowling
    
    Đã lưu.

Phù hợp khi:

  * Người dùng mới. 
  * Có nhiều thông tin cần nhập. 
  * Trình cài đặt (installer). 
  * Thiết lập ban đầu (wizard). 



* * *

# 2\. `click.prompt()`

Ví dụ:
    
    
    import click
    
    @click.command()
    def main():
        name = click.prompt("Tên của bạn")
        click.echo(f"Xin chào {name}")
    
    if __name__ == "__main__":
        main()

Chạy:
    
    
    Tên của bạn:

Người dùng nhập:
    
    
    Alice

Kết quả:
    
    
    Xin chào Alice

* * *

# 3\. Prompt có kiểu dữ liệu
    
    
    age = click.prompt(
        "Tuổi",
        type=int
    )

Nếu nhập:
    
    
    abc

Click sẽ tự báo:
    
    
    Error:
    'abc' is not a valid integer.

và hỏi lại.

Đây là điểm rất hay: **Click không kết thúc chương trình ngay** , mà cho phép nhập lại.

* * *

# 4\. Giá trị mặc định
    
    
    city = click.prompt(
        "Thành phố",
        default="Hồ Chí Minh"
    )

Hiển thị:
    
    
    Thành phố [Hồ Chí Minh]:

Nếu nhấn Enter:
    
    
    Hồ Chí Minh

được sử dụng.

* * *

# 5\. Prompt với Option

Không cần gọi `click.prompt()` thủ công.
    
    
    @click.command()
    @click.option(
        "--name",
        prompt=True
    )
    def hello(name):
        click.echo(name)

Nếu chạy:
    
    
    python app.py

Click tự hỏi:
    
    
    Name:

* * *

Nếu chạy:
    
    
    python app.py --name Alice

Click **không hỏi nữa**.

Đây là cách làm rất phổ biến.

* * *

# 6\. Prompt tùy chỉnh
    
    
    @click.option(
        "--name",
        prompt="Nhập tên của bạn"
    )

Kết quả:
    
    
    Nhập tên của bạn:

* * *

# 7\. Password

Ví dụ:
    
    
    password = click.prompt(
        "Password",
        hide_input=True
    )

Khi nhập:
    
    
    Password:

Các ký tự sẽ **không hiển thị**.

Giống:
    
    
    mysql
    
    docker login
    
    ssh

* * *

# 8\. Xác nhận mật khẩu
    
    
    password = click.prompt(
        "Password",
        hide_input=True,
        confirmation_prompt=True
    )

CLI:
    
    
    Password:
    ********
    
    Repeat for confirmation:
    ********

Nếu hai lần khác nhau:
    
    
    Error:
    The two entered values do not match.

Click sẽ yêu cầu nhập lại.

* * *

# 9\. `click.confirm()`

Ví dụ:
    
    
    import click
    
    @click.command()
    def delete():
        if click.confirm("Bạn có chắc muốn xóa?"):
            click.echo("Đã xóa")
        else:
            click.echo("Đã hủy")
    
    if __name__ == "__main__":
        delete()

Hiển thị:
    
    
    Bạn có chắc muốn xóa? [y/N]:

* * *

Nếu nhập:
    
    
    y

Kết quả:
    
    
    Đã xóa

* * *

Nếu nhập:
    
    
    n
    
    
    Đã hủy

* * *

# 10\. `abort=True`
    
    
    click.confirm(
        "Tiếp tục?",
        abort=True
    )

Nếu người dùng chọn:
    
    
    n

Click sẽ tự dừng:
    
    
    Aborted!

Không cần:
    
    
    if not confirm:
        exit()

* * *

# 11\. Prompt + Validation

Ví dụ:
    
    
    age = click.prompt(
        "Tuổi",
        type=click.IntRange(1, 120)
    )

Nếu nhập:
    
    
    500

Click:
    
    
    Error:
    500 is not in the valid range.

và hỏi lại.

* * *

# 12\. Prompt với Choice
    
    
    language = click.prompt(
        "Ngôn ngữ",
        type=click.Choice(
            ["vi", "en", "jp"]
        )
    )

Nếu nhập:
    
    
    fr

Click sẽ báo lỗi và yêu cầu nhập lại.

* * *

# 13\. Wizard nhiều bước

Ví dụ tạo cấu hình:
    
    
    import click
    
    @click.command()
    def init():
        host = click.prompt("Host")
        port = click.prompt(
            "Port",
            type=int,
            default=3306
        )
        username = click.prompt("Username")
        password = click.prompt(
            "Password",
            hide_input=True
        )
    
        click.echo()
        click.echo("Thông tin:")
        click.echo(f"Host: {host}")
        click.echo(f"Port: {port}")
        click.echo(f"User: {username}")
    
    if __name__ == "__main__":
        init()

Đây là nền tảng để xây dựng lệnh:
    
    
    story init

hoặc
    
    
    story config create

* * *

# 14\. Kết hợp Option và Prompt

Ví dụ:
    
    
    @click.command()
    @click.option(
        "--username",
        prompt=True
    )
    @click.option(
        "--password",
        prompt=True,
        hide_input=True
    )
    def login(username, password):
        click.echo("Đăng nhập thành công.")

Người dùng có hai cách:

### Cách 1
    
    
    python app.py

CLI sẽ hỏi.

* * *

### Cách 2
    
    
    python app.py \
        --username admin \
        --password 123456

Không cần hỏi.

Đây là thiết kế rất linh hoạt.

* * *

# 15\. Ví dụ thực tế: Story Crawler

Lệnh:
    
    
    story plugin install

Nếu thiếu thông tin:
    
    
    Tên plugin:
    > truyenfull
    
    URL:
    > https://...
    
    Có kích hoạt ngay không?
    [y/N]:

Nếu người dùng truyền:
    
    
    story plugin install \
        --name truyenfull \
        --url https://...

CLI sẽ không hỏi lại.

Đây là cách nhiều công cụ chuyên nghiệp hoạt động.

* * *

# 16\. Khi nào nên dùng Prompt?

Trường hợp| Prompt?  
---|---  
Script tự động| ❌  
CI/CD| ❌  
Lệnh hằng ngày| ❌  
Thiết lập ban đầu| ✅  
Wizard| ✅  
Nhập mật khẩu| ✅  
Xác nhận xóa dữ liệu| ✅  
  
* * *

# 17\. Những lỗi người mới thường gặp

### ❌ Luôn dùng Prompt
    
    
    name = click.prompt(...)

Ngay cả khi người dùng đã truyền `--name`.

Điều này làm CLI khó tự động hóa.

* * *

### ✅ Nên dùng
    
    
    @click.option(
        "--name",
        prompt=True
    )

* * *

### ❌ Dùng Prompt cho mọi thao tác xóa
    
    
    Delete?

Ngay cả khi chạy trong script.

* * *

### ✅ Nên có tùy chọn:
    
    
    story remove 15 --yes

để bỏ qua xác nhận khi cần tự động hóa.

* * *

# 18\. Tổng kết

Các hàm quan trọng:

Hàm| Mục đích  
---|---  
`click.prompt()`| Hỏi người dùng  
`prompt=True`| Tự hỏi nếu thiếu Option  
`click.confirm()`| Xác nhận Có/Không  
`hide_input=True`| Ẩn mật khẩu  
`confirmation_prompt=True`| Nhập lại để xác nhận  
`abort=True`| Dừng chương trình khi từ chối  
  
* * *

# Bài tập thực hành

## Bài 1

Viết chương trình hỏi:
    
    
    Tên:

và in lại tên.

* * *

## Bài 2

Hỏi:

  * Tên 
  * Tuổi 
  * Thành phố 



Trong đó:

  * Tuổi phải là số nguyên. 
  * Thành phố mặc định là `Hồ Chí Minh`. 



* * *

## Bài 3

Viết chương trình yêu cầu nhập mật khẩu hai lần bằng:

  * `hide_input=True`
  * `confirmation_prompt=True`



Sau khi nhập đúng, in:
    
    
    Thiết lập mật khẩu thành công.

* * *

## Bài 4

Viết chương trình:
    
    
    Bạn có chắc muốn xóa cơ sở dữ liệu?

Nếu người dùng chọn **No** , chương trình phải dừng ngay bằng `abort=True`.

* * *

## Bài 5 (Mini Project)

Tạo lệnh:
    
    
    story init

Quy trình:

  1. Hỏi đường dẫn cơ sở dữ liệu (mặc định: `story.db`). 
  2. Hỏi số luồng tải (`1–16`, mặc định `4`). 
  3. Hỏi định dạng xuất mặc định (`txt`, `html`, `epub`). 
  4. Hỏi có bật chế độ debug hay không (`click.confirm()`). 
  5. Hiển thị toàn bộ cấu hình vừa nhập và hỏi xác nhận lưu. 



* * *

## Chuẩn bị cho buổi 5

Ở **Buổi 5** , chúng ta sẽ học cách tạo **giao diện dòng lệnh đẹp và chuyên nghiệp** với Click:

  * `click.echo()`
  * `click.style()`
  * `click.secho()`
  * Màu sắc và định dạng văn bản 
  * `click.progressbar()`
  * `click.clear()`
  * `click.pause()`
  * Thông báo trạng thái, cảnh báo và lỗi 



Sau buổi này, CLI của chúng ta sẽ có trải nghiệm gần với các công cụ như `git`, `pip`, `poetry` và `docker`, đồng thời sẵn sàng tích hợp với thư viện **Rich** ở các buổi sau để xây dựng giao diện dòng lệnh hiện đại hơn.

