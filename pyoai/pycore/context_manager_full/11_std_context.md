# Context Manager Deep Dive – Buổi 11

# Những Context Manager quan trọng trong Thư viện chuẩn (Standard Library)

> Đây là buổi học mang tính **thực chiến**.

Ở 10 buổi trước, chúng ta đã học cách **tự xây dựng Context Manager**.

Hôm nay chúng ta sẽ học cách **sử dụng những Context Manager mà Python đã cung cấp sẵn**.

Đây là những thứ bạn sẽ gặp hàng ngày khi đọc source code của:

  * CPython 
  * Django 
  * Flask 
  * SQLAlchemy 
  * FastAPI 
  * aiohttp 
  * pytest 
  * pip 
  * requests 
  * pandas 



* * *

# Mục tiêu

Sau buổi này bạn sẽ thành thạo:

  * `contextlib.closing`
  * `contextlib.suppress`
  * `contextlib.nullcontext`
  * `contextlib.redirect_stdout`
  * `contextlib.redirect_stderr`
  * `contextlib.chdir` (Python 3.11+) 
  * `decimal.localcontext`
  * `tempfile`
  * `warnings.catch_warnings`
  * `unittest.mock.patch`
  * Best Practices 



* * *

# 1\. `contextlib.closing`

Có nhiều object có
    
    
    close()

nhưng **không phải Context Manager**.

Ví dụ
    
    
    sock = socket.socket(...)

Nếu object không hỗ trợ `with`, bạn có thể dùng:
    
    
    from contextlib import closing
    import socket
    
    with closing(socket.socket()) as sock:
        ...

`closing()` sẽ gọi:
    
    
    sock.close()

khi thoát.

* * *

## Bên trong `closing`

Ý tưởng rất đơn giản:
    
    
    @contextmanager
    def closing(obj):
    
        try:
            yield obj
    
        finally:
            obj.close()

* * *

# 2\. `contextlib.suppress`

Một trong những Context Manager được dùng nhiều nhất.

Ví dụ
    
    
    try:
    
        os.remove("abc.txt")
    
    except FileNotFoundError:
    
        pass

Có thể viết
    
    
    from contextlib import suppress
    import os
    
    with suppress(FileNotFoundError):
    
        os.remove("abc.txt")

Rất gọn.

* * *

## Nhiều Exception
    
    
    with suppress(
        FileNotFoundError,
        PermissionError,
    ):
        ...

* * *

## Khi nào nên dùng?

✔ Cleanup

✔ Xóa file tạm

✔ Đóng socket

✔ Rollback nhẹ

* * *

## Không nên
    
    
    with suppress(Exception):

Điều này che giấu mọi lỗi.

Chỉ suppress những exception mà bạn **thực sự mong đợi**.

* * *

# 3\. `contextlib.nullcontext`

Ví dụ
    
    
    if debug:
    
        with Logger():
    
            work()
    
    else:
    
        work()

Có thể viết
    
    
    from contextlib import nullcontext
    
    ctx = Logger() if debug else nullcontext()
    
    with ctx:
    
        work()

Code sạch hơn rất nhiều.

* * *

## Giá trị trả về
    
    
    with nullcontext(100) as x:
    
        print(x)

Output
    
    
    100

* * *

## Rất hữu ích

Ví dụ
    
    
    session = (
        aiohttp.ClientSession()
        if own_session
        else nullcontext(existing_session)
    )

Bạn sẽ thấy mẫu này trong nhiều thư viện.

* * *

# 4\. `redirect_stdout`

Ví dụ
    
    
    print("Hello")

Muốn ghi ra file
    
    
    from contextlib import redirect_stdout
    
    with open("log.txt", "w") as f:
    
        with redirect_stdout(f):
    
            print("Hello")

Kết quả
    
    
    Hello

được ghi vào
    
    
    log.txt

* * *

## Redirect sang StringIO
    
    
    import io
    
    buffer = io.StringIO()
    
    with redirect_stdout(buffer):
    
        print("ABC")
    
    print(buffer.getvalue())

Output
    
    
    ABC

Rất hữu ích trong:

  * unittest 
  * pytest 
  * benchmark 



* * *

# 5\. `redirect_stderr`

Giống hệt
    
    
    redirect_stdout

nhưng áp dụng cho
    
    
    sys.stderr

Ví dụ
    
    
    from contextlib import redirect_stderr
    import io
    import sys
    
    err = io.StringIO()
    
    with redirect_stderr(err):
    
        print("ERROR", file=sys.stderr)
    
    print(err.getvalue())

* * *

# 6\. `contextlib.chdir` (Python 3.11+)

Ngày xưa
    
    
    cwd = os.getcwd()
    
    os.chdir("project")
    
    try:
    
        ...
    
    finally:
    
        os.chdir(cwd)

Bây giờ
    
    
    from contextlib import chdir
    
    with chdir("project"):
    
        ...

Tự động quay về thư mục cũ.

* * *

# 7\. `decimal.localcontext`

Ví dụ
    
    
    from decimal import Decimal
    from decimal import localcontext
    
    with localcontext() as ctx:
    
        ctx.prec = 50
    
        print(
            Decimal(1) / Decimal(7)
        )

Sau khi thoát

↓

Precision trở về như cũ.

Đây là Context Manager thay đổi **tạm thời** trạng thái toàn cục.

* * *

# 8\. `tempfile.TemporaryDirectory`

Một Context Manager cực kỳ hữu ích.
    
    
    import tempfile
    
    with tempfile.TemporaryDirectory() as path:
    
        print(path)

Python
    
    
    Create Folder
    
    ↓
    
    Use
    
    ↓
    
    Delete Folder

Không cần tự xóa.

* * *

# 9\. `NamedTemporaryFile`
    
    
    import tempfile
    
    with tempfile.NamedTemporaryFile(
        mode="w+",
        delete=True
    ) as f:
    
        f.write("Hello")
    
        f.seek(0)
    
        print(f.read())

Thoát

↓

File biến mất.

* * *

# 10\. `warnings.catch_warnings`

Ví dụ
    
    
    import warnings
    
    with warnings.catch_warnings():
    
        warnings.simplefilter("ignore")
    
        ...

Chỉ block bên trong bị ảnh hưởng.

Ra ngoài

↓

Warning trở lại bình thường.

* * *

# 11\. `unittest.mock.patch`

Context Manager nổi tiếng.
    
    
    from unittest.mock import patch
    
    with patch("os.getcwd") as mock:
    
        mock.return_value = "/tmp"
    
        print(os.getcwd())

Output
    
    
    /tmp

Thoát

↓

`os.getcwd`

quay về bình thường.

* * *

# 12\. Kết hợp nhiều Context Manager
    
    
    with (
        tempfile.TemporaryDirectory() as tmp,
        redirect_stdout(open("log.txt", "w")),
    ):
        ...

Hoặc nếu số lượng thay đổi:
    
    
    from contextlib import ExitStack
    
    with ExitStack() as stack:
        ...

* * *

# 13\. `closing` \+ `suppress`

Ví dụ
    
    
    from contextlib import (
        closing,
        suppress,
    )
    import socket
    
    with closing(socket.socket()) as sock:
    
        with suppress(ConnectionResetError):
    
            sock.recv(1024)

Đây là mẫu rất phổ biến.

* * *

# 14\. `nullcontext` trong API

Ví dụ
    
    
    from contextlib import nullcontext
    
    def process(file_or_path):
    
        if isinstance(file_or_path, str):
    
            ctx = open(file_or_path)
    
        else:
    
            ctx = nullcontext(file_or_path)
    
        with ctx as f:
    
            return f.read()

Hàm này chấp nhận:

  * đường dẫn 
  * hoặc file đã mở 



Đây là một kỹ thuật thiết kế API rất hay.

* * *

# 15\. Tổng hợp các Context Manager quan trọng

Context Manager| Công dụng  
---|---  
`open()`| Quản lý file  
`closing()`| Đóng object có `close()`  
`suppress()`| Bỏ qua exception mong đợi  
`nullcontext()`| Context Manager rỗng  
`redirect_stdout()`| Chuyển hướng `stdout`  
`redirect_stderr()`| Chuyển hướng `stderr`  
`chdir()`| Đổi thư mục tạm thời  
`TemporaryDirectory()`| Thư mục tạm  
`NamedTemporaryFile()`| File tạm  
`localcontext()`| Thay đổi tạm thời context của `decimal`  
`catch_warnings()`| Quản lý cảnh báo  
`patch()`| Mock trong kiểm thử  
  
* * *

# Story Crawler – Ứng dụng thực tế

Giả sử bạn cần:

  * Tạo thư mục tạm để lưu HTML. 
  * Ghi log quá trình crawl vào file. 
  * Bỏ qua lỗi khi xóa file cache đã không còn. 
  * Chấp nhận cả đường dẫn hoặc file object. 



Bạn có thể kết hợp:
    
    
    from contextlib import (
        suppress,
        redirect_stdout,
    )
    import tempfile
    
    with (
        tempfile.TemporaryDirectory() as tmp,
        open("crawl.log", "w", encoding="utf-8") as log_file,
        redirect_stdout(log_file),
    ):
        print(f"Downloading to {tmp}")
    
        with suppress(FileNotFoundError):
            # Xóa cache cũ nếu có
            ...

Mã nguồn vừa ngắn gọn vừa đảm bảo mọi tài nguyên được dọn dẹp đúng cách.

* * *

# Best Practices

## Dùng `suppress` có chọn lọc

✔
    
    
    with suppress(FileNotFoundError):
        ...

✘
    
    
    with suppress(Exception):
        ...

* * *

## Dùng `nullcontext`

Khi muốn bỏ `if...else` chỉ để có hoặc không có `with`.

* * *

## Dùng `TemporaryDirectory`

Thay vì tự tạo:
    
    
    os.mkdir(...)

rồi quên xóa.

* * *

## Dùng `redirect_stdout`

Để:

  * benchmark 
  * test 
  * capture output 



Không dùng để thay thế hệ thống logging trong ứng dụng production.

* * *

# Bài tập

## Bài 1

Viết chương trình:

  * tạo `TemporaryDirectory()`, 
  * tạo 5 file bên trong, 
  * ghi dữ liệu, 
  * sau khi thoát `with`, xác minh thư mục đã được xóa. 



* * *

## Bài 2

Viết hàm:
    
    
    def read_text(source):
        ...

Yêu cầu:

  * Nếu `source` là `str` hoặc `Path`, tự mở file. 
  * Nếu `source` là file object, sử dụng luôn. 
  * Dùng `nullcontext()` để tránh lặp mã. 



* * *

## Bài 3

Dùng `redirect_stdout()` để:

  * chuyển toàn bộ `print()` của một hàm sang `io.StringIO`, 
  * trả về chuỗi kết quả thay vì in ra màn hình. 



* * *

## Bài 4 (Áp dụng cho Story Crawler)

Thiết kế quy trình tải và phân tích HTML:

  * Tạo `TemporaryDirectory()` để lưu HTML tạm. 
  * Dùng `redirect_stdout()` để ghi log vào file trong thư mục tạm. 
  * Dùng `suppress(FileNotFoundError)` khi dọn dẹp cache cũ. 
  * Nếu người gọi truyền vào một file HTML đã mở sẵn, dùng `nullcontext()` để không mở lại file. 



* * *

# Tổng kết buổi 11

Sau buổi này, bạn đã làm quen với hầu hết các **Context Manager quan trọng trong thư viện chuẩn** và biết khi nào nên sử dụng chúng trong các dự án thực tế.

Bạn không chỉ biết cách **tự viết Context Manager** , mà còn biết tận dụng các công cụ có sẵn của Python để:

  * quản lý file và thư mục tạm, 
  * xử lý ngoại lệ có chủ đích, 
  * thay đổi trạng thái tạm thời, 
  * chuyển hướng luồng xuất, 
  * viết API linh hoạt và dễ bảo trì. 



* * *

# Chuẩn bị cho buổi 12 – Project Production

Buổi cuối cùng sẽ là **Project Production**.

Chúng ta sẽ tổng hợp toàn bộ kiến thức đã học để xây dựng một **Resource Manager Framework** theo phong cách production, kết hợp:

  * Class-based Context Manager. 
  * `@contextmanager`. 
  * `ExitStack`. 
  * `AsyncExitStack`. 
  * Logging. 
  * Database. 
  * HTTP Session. 
  * Transaction. 
  * Plugin. 



Đây sẽ là một kiến trúc có thể áp dụng trực tiếp vào các dự án lớn như **Story Crawler** , nơi nhiều tài nguyên cần được quản lý an toàn, rõ ràng và dễ mở rộng.

