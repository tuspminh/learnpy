# Khóa học Click Deep Dive

# Buổi 5: Output chuyên nghiệp - `echo`, `style`, `secho`, `progressbar`, `clear`, `pause`

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu cách Click hiển thị văn bản trên terminal một cách an toàn. 
>   * Sử dụng `click.echo()`, `click.secho()`, `click.style()`. 
>   * Tạo thông báo có màu sắc và định dạng. 
>   * Hiển thị thanh tiến trình (`progressbar`). 
>   * Xóa màn hình (`clear`) và tạm dừng (`pause`). 
>   * Thiết kế giao diện CLI dễ đọc và chuyên nghiệp. 
> 


* * *

# 1\. Vì sao không nên dùng `print()`?

Python:
    
    
    print("Hello")

Click:
    
    
    click.echo("Hello")

Thoạt nhìn giống nhau, nhưng `click.echo()` có nhiều ưu điểm:

  * Hỗ trợ Unicode tốt trên Windows. 
  * Tự xử lý mã hóa ký tự (encoding). 
  * Hỗ trợ ghi ra file (`stdout`, `stderr`). 
  * Dễ kiểm thử bằng `CliRunner`. 
  * Tích hợp màu sắc và định dạng. 



**Nguyên tắc:** Trong ứng dụng Click, hãy ưu tiên `click.echo()`.

* * *

# 2\. `click.echo()`
    
    
    import click
    
    @click.command()
    def hello():
        click.echo("Xin chào Click!")
    
    if __name__ == "__main__":
        hello()

* * *

## Xuống dòng
    
    
    click.echo("Dòng 1")
    click.echo("Dòng 2")

Kết quả:
    
    
    Dòng 1
    Dòng 2

* * *

## Không xuống dòng
    
    
    click.echo("Loading...", nl=False)
    click.echo("Done!")

Kết quả:
    
    
    Loading...Done!

* * *

# 3\. Ghi ra `stderr`

Thông báo lỗi nên đi ra `stderr` thay vì `stdout`.
    
    
    click.echo(
        "Không tìm thấy tệp!",
        err=True
    )

Điều này hữu ích khi:

  * Ghi log. 
  * Redirect kết quả. 
  * Viết script. 



* * *

# 4\. `click.style()`

`style()` tạo chuỗi có màu và định dạng.
    
    
    text = click.style(
        "Success",
        fg="green"
    )
    
    click.echo(text)

* * *

## Các màu cơ bản
    
    
    fg="black"
    fg="red"
    fg="green"
    fg="yellow"
    fg="blue"
    fg="magenta"
    fg="cyan"
    fg="white"

Ví dụ:
    
    
    click.echo(click.style("OK", fg="green"))
    click.echo(click.style("Warning", fg="yellow"))
    click.echo(click.style("Error", fg="red"))

* * *

# 5\. Màu nền
    
    
    click.style(
        "Python",
        fg="white",
        bg="blue"
    )

* * *

# 6\. Chữ đậm
    
    
    click.style(
        "Important",
        bold=True
    )

* * *

# 7\. Gạch chân
    
    
    click.style(
        "Website",
        underline=True
    )

* * *

# 8\. Đảo màu
    
    
    click.style(
        "Reverse",
        reverse=True
    )

* * *

# 9\. Nhấp nháy
    
    
    click.style(
        "Blink",
        blink=True
    )

> **Lưu ý:** Không phải terminal nào cũng hỗ trợ.

* * *

# 10\. `click.secho()`

Thay vì:
    
    
    click.echo(
        click.style(
            "Done",
            fg="green"
        )
    )

Có thể viết ngắn gọn:
    
    
    click.secho(
        "Done",
        fg="green"
    )

Đây là cách thường dùng trong các dự án Click.

* * *

# 11\. Tạo các hàm thông báo

Trong dự án lớn, bạn nên chuẩn hóa thông báo.
    
    
    import click
    
    def success(msg):
        click.secho(msg, fg="green")
    
    def warning(msg):
        click.secho(msg, fg="yellow")
    
    def error(msg):
        click.secho(msg, fg="red", err=True)

Sử dụng:
    
    
    success("Đã lưu dữ liệu.")
    warning("Bộ nhớ gần đầy.")
    error("Không thể kết nối cơ sở dữ liệu.")

Sau này, ta sẽ đặt các hàm này vào `utils/output.py`.

* * *

# 12\. `click.progressbar()`

Ví dụ:
    
    
    import click
    import time
    
    @click.command()
    def download():
        with click.progressbar(range(100)) as bar:
            for _ in bar:
                time.sleep(0.02)
    
    if __name__ == "__main__":
        download()

Click sẽ hiển thị thanh tiến trình tự động.

* * *

## Với danh sách
    
    
    files = [
        "a.txt",
        "b.txt",
        "c.txt"
    ]
    
    with click.progressbar(files) as bar:
        for file in bar:
            ...

* * *

## Có nhãn
    
    
    with click.progressbar(
        files,
        label="Đang sao chép"
    ) as bar:
        ...

Ví dụ:
    
    
    Đang sao chép  [#####---------]

* * *

# 13\. Ví dụ Story Crawler
    
    
    chapters = range(500)
    
    with click.progressbar(
        chapters,
        label="Đang tải chương"
    ) as bar:
        for chapter in bar:
            download(chapter)

Người dùng sẽ biết:

  * Đã tải bao nhiêu chương. 
  * Còn bao lâu. 



Trải nghiệm tốt hơn rất nhiều so với việc chỉ in:
    
    
    Downloading...
    Downloading...
    Downloading...

* * *

# 14\. `click.clear()`

Xóa màn hình terminal.
    
    
    click.clear()

Ví dụ:
    
    
    click.echo("Xin chào")
    click.pause()
    click.clear()
    click.echo("Màn hình đã được làm sạch.")

* * *

# 15\. `click.pause()`

Tạm dừng chương trình.
    
    
    click.pause()

Hiển thị:
    
    
    Press any key to continue...

Có thể đổi nội dung:
    
    
    click.pause("Nhấn Enter để tiếp tục...")

* * *

# 16\. Tạo giao diện CLI đẹp

Không nên:
    
    
    Name: Alice
    Age: 20
    City: HCM

Có thể trình bày:
    
    
    click.secho("Thông tin người dùng", fg="cyan", bold=True)
    click.echo("-" * 30)
    
    click.echo("Tên : Alice")
    click.echo("Tuổi: 20")
    click.echo("TP  : Hồ Chí Minh")

Kết quả:
    
    
    Thông tin người dùng
    ------------------------------
    Tên : Alice
    Tuổi: 20
    TP  : Hồ Chí Minh

* * *

# 17\. Thiết kế thông báo chuẩn

Một quy ước phổ biến:
    
    
    click.secho("[OK] Đã lưu", fg="green")
    click.secho("[WARN] Bộ nhớ thấp", fg="yellow")
    click.secho("[ERROR] Không kết nối được", fg="red")
    click.secho("[INFO] Đang tải...", fg="cyan")

Hoặc dùng biểu tượng Unicode:
    
    
    ✓ Thành công
    ⚠ Cảnh báo
    ✗ Lỗi
    ℹ Thông tin

Ví dụ:
    
    
    click.secho("✓ Đã hoàn tất", fg="green")
    click.secho("⚠ Kiểm tra cấu hình", fg="yellow")
    click.secho("✗ Kết nối thất bại", fg="red")

* * *

# 18\. Mini Project

Xây dựng CLI:
    
    
    story backup

Mô phỏng:
    
    
    import click
    import time
    
    @click.command()
    def backup():
        click.secho(
            "Bắt đầu sao lưu...",
            fg="cyan"
        )
    
        with click.progressbar(
            range(100),
            label="Đang sao lưu"
        ) as bar:
            for _ in bar:
                time.sleep(0.02)
    
        click.secho(
            "✓ Sao lưu hoàn tất",
            fg="green"
        )
    
    if __name__ == "__main__":
        backup()

Khi chạy, người dùng sẽ thấy:
    
    
    Bắt đầu sao lưu...
    
    Đang sao lưu  [##########......]
    
    ✓ Sao lưu hoàn tất

* * *

# 19\. Những lỗi thường gặp

### ❌ Dùng `print()` lẫn với `click.echo()`
    
    
    print("Loading")
    click.echo("Done")

Nên thống nhất:
    
    
    click.echo("Loading")
    click.echo("Done")

* * *

### ❌ Lạm dụng màu sắc

Không nên:
    
    
    click.secho(..., fg="red")
    click.secho(..., fg="green")
    click.secho(..., fg="yellow")
    click.secho(..., fg="blue")
    click.secho(..., fg="magenta")

quá nhiều trong cùng một màn hình.

Nên quy ước:

  * Xanh lá → Thành công 
  * Vàng → Cảnh báo 
  * Đỏ → Lỗi 
  * Xanh dương/Cyan → Thông tin 



* * *

# 20\. Tổng kết

Các API quan trọng:

Hàm| Công dụng  
---|---  
`click.echo()`| In văn bản  
`click.secho()`| In văn bản có màu  
`click.style()`| Tạo chuỗi có định dạng  
`click.progressbar()`| Thanh tiến trình  
`click.clear()`| Xóa màn hình  
`click.pause()`| Tạm dừng chương trình  
  
* * *

# Bài tập thực hành

## Bài 1

Viết chương trình in:

  * Thông báo thành công (màu xanh). 
  * Thông báo cảnh báo (màu vàng). 
  * Thông báo lỗi (màu đỏ). 



* * *

## Bài 2

Tạo hàm:
    
    
    info(msg)
    success(msg)
    warning(msg)
    error(msg)

sử dụng `click.secho()`.

* * *

## Bài 3

Mô phỏng tải 50 tệp bằng `click.progressbar()` với nhãn:
    
    
    Đang tải tệp

* * *

## Bài 4

Viết chương trình:

  1. Hiển thị thông báo chào mừng. 
  2. `click.pause()`. 
  3. `click.clear()`. 
  4. Hiển thị menu mới. 



* * *

## Bài 5 (Mini Project)

Xây dựng lệnh:
    
    
    story crawl

Mô phỏng quá trình thu thập **100 chương truyện** :

  * Hiển thị thông báo bắt đầu bằng màu `cyan`. 
  * Sử dụng `click.progressbar()` để mô phỏng quá trình tải. 
  * Sau khi hoàn tất, hiển thị: 
    * Tổng số chương đã tải. 
    * Thời gian thực hiện (có thể dùng `time.perf_counter()`). 
    * Thông báo thành công bằng màu xanh. 



* * *

# Chuẩn bị cho buổi 6

Từ buổi sau, chúng ta sẽ chuyển sang **giai đoạn quan trọng nhất của Click** : xây dựng **CLI nhiều lệnh (Multi-command CLI)**.

Bạn sẽ học:

  * `@click.group()`
  * Tổ chức nhiều command trong một ứng dụng. 
  * Cách hoạt động của `git`, `docker`, `kubectl`, `poetry`. 
  * Thiết kế CLI theo kiến trúc module. 



Đây là bước khởi đầu để xây dựng ứng dụng **Story Crawler CLI** với các lệnh như:
    
    
    story crawler start
    story crawler stop
    story db backup
    story plugin list
    story export epub

và cũng là nền tảng để đến các buổi sau tổ chức mã nguồn theo kiến trúc lớn, hỗ trợ plugin và mở rộng dễ dàng.

