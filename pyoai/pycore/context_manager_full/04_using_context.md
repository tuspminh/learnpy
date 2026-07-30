# Context Manager Deep Dive – Buổi 4

# Ứng dụng thực tế: File, Database, Socket, Lock, Resource Management

> Từ buổi này trở đi, chúng ta sẽ chuyển từ **"hiểu Context Manager"** sang **"sử dụng Context Manager như một lập trình viên Python chuyên nghiệp"**.

Trong các framework như:

  * Django 
  * SQLAlchemy 
  * FastAPI 
  * Requests 
  * asyncio 
  * sqlite3 
  * threading 
  * tempfile 



Context Manager xuất hiện ở khắp mọi nơi.

* * *

# Mục tiêu

Sau buổi này bạn sẽ biết cách dùng Context Manager với:

  * File 
  * SQLite 
  * Lock 
  * Temporary Directory 
  * Socket 
  * HTTP Session 
  * Logging 
  * Transaction 



Đồng thời hiểu **vì sao** mỗi trường hợp đều cần Context Manager.

* * *

# 1\. File Context Manager

Đây là ví dụ phổ biến nhất.
    
    
    with open("data.txt", encoding="utf-8") as f:
        text = f.read()
    
    print(text)

Python đảm bảo:
    
    
    Open File
    
    ↓
    
    Read
    
    ↓
    
    Close File

Cho dù:

  * return 
  * break 
  * continue 
  * raise exception 



file vẫn luôn được đóng.

* * *

## Sai lầm phổ biến
    
    
    f = open("data.txt")
    
    data = f.read()
    
    # quên close()

Nếu chương trình mở hàng nghìn file:
    
    
    for filename in many_files:
        f = open(filename)

Sau một lúc:
    
    
    OSError:
    Too many open files

Đây là lỗi rất phổ biến trên Linux.

* * *

# 2\. Ghi file
    
    
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write("Hello\n")

Không cần
    
    
    f.flush()
    
    f.close()

* * *

# 3\. Đọc nhiều file
    
    
    files = [
        "a.txt",
        "b.txt",
        "c.txt"
    ]
    
    for file in files:
    
        with open(file, encoding="utf-8") as f:
    
            print(f.read())

Mỗi file được mở rồi đóng ngay.

Đây là cách tiết kiệm tài nguyên.

* * *

# 4\. SQLite Transaction

Ví dụ
    
    
    import sqlite3
    
    with sqlite3.connect("school.db") as conn:
    
        conn.execute(
            "INSERT INTO student(name) VALUES(?)",
            ("Alice",)
        )

Nhiều người nghĩ:
    
    
    with
    
    ↓
    
    đóng connection

Không hẳn.

Điều quan trọng hơn là:
    
    
    BEGIN
    
    ↓
    
    SQL
    
    ↓
    
    COMMIT
    
    ↓
    
    ROLLBACK nếu lỗi

`sqlite3.Connection` hoạt động như một Context Manager cho **transaction**.

Ví dụ:
    
    
    import sqlite3
    
    try:
        with sqlite3.connect(":memory:") as conn:
            conn.execute("CREATE TABLE t(x INTEGER)")
            conn.execute("INSERT INTO t VALUES (1)")
            raise RuntimeError("Oops")
    except RuntimeError:
        pass

Trong ví dụ này, transaction đang mở sẽ bị **rollback** khi ngoại lệ xảy ra. Nếu bạn muốn đóng kết nối ngay sau đó, hãy dùng thêm:
    
    
    conn.close()

hoặc bọc việc tạo kết nối trong một Context Manager của riêng bạn.

> **Lưu ý quan trọng:** Context Manager của `sqlite3.Connection` **không tự động đóng kết nối** khi kết thúc `with`. Nó quản lý transaction (commit/rollback). Bạn vẫn nên đóng kết nối khi không còn sử dụng.

* * *

# 5\. Lock

Đây là ví dụ cực kỳ quan trọng.

Không nên
    
    
    lock.acquire()
    
    try:
    
        update_database()
    
    finally:
    
        lock.release()

Mà hãy dùng
    
    
    from threading import Lock
    
    lock = Lock()
    
    with lock:
    
        update_database()

Python sẽ tự:
    
    
    Acquire
    
    ↓
    
    Work
    
    ↓
    
    Release

Không bao giờ quên release.

* * *

# 6\. Temporary Directory
    
    
    import tempfile
    
    with tempfile.TemporaryDirectory() as folder:
    
        print(folder)

Python tạo
    
    
    /tmp/abcd1234

Khi ra khỏi `with`

↓

Python tự xóa.

Không cần:
    
    
    shutil.rmtree(...)

* * *

# 7\. Temporary File
    
    
    import tempfile
    
    with tempfile.NamedTemporaryFile() as f:
    
        f.write(b"Hello")
    
        f.seek(0)
    
        print(f.read())

Ra khỏi `with`

↓

File bị xóa (mặc định trên nhiều hệ điều hành, có thể thay đổi bằng tham số `delete`).

* * *

# 8\. Socket

Thông thường
    
    
    import socket
    
    sock = socket.socket()
    
    sock.connect(...)
    
    sock.send(...)
    
    sock.close()

Nếu exception

↓

Không close.

Tốt hơn
    
    
    import socket
    
    with socket.socket() as sock:
    
        sock.connect(("example.com", 80))
    
        sock.send(b"GET / HTTP/1.0\r\n\r\n")

Socket luôn được đóng.

* * *

# 9\. HTTP Session (`requests`)

Ví dụ
    
    
    import requests
    
    with requests.Session() as session:
    
        response = session.get(
            "https://example.com"
        )
    
        print(response.status_code)

Ra khỏi `with`

↓

Session đóng.

Connection Pool được giải phóng.

Đây là cách viết chuyên nghiệp khi gửi nhiều request.

* * *

# 10\. Logging Context

Ví dụ tự viết
    
    
    class Logger:
    
        def __enter__(self):
    
            print("Start")
    
            return self
    
        def __exit__(self, *args):
    
            print("End")
    
    
    with Logger():
    
        print("Doing job")

Output
    
    
    Start
    
    Doing job
    
    End

Thực tế có thể mở rộng để:

  * ghi thời gian bắt đầu/kết thúc, 
  * ghi log khi có ngoại lệ, 
  * đo hiệu năng. 



* * *

# 11\. Timer Context Manager

Đây là ứng dụng cực kỳ phổ biến.
    
    
    import time
    
    
    class Timer:
    
        def __enter__(self):
    
            self.start = time.perf_counter()
    
            return self
    
        def __exit__(self, *args):
    
            elapsed = time.perf_counter() - self.start
    
            print(f"{elapsed:.3f} s")

Sử dụng
    
    
    with Timer():
    
        total = sum(range(5_000_000))

Ví dụ kết quả:
    
    
    0.124 s

* * *

# 12\. Redirect Output
    
    
    from contextlib import redirect_stdout
    
    with open("output.txt", "w", encoding="utf-8") as f:
        with redirect_stdout(f):
            print("Hello")
            print("Python")

Kết quả
    
    
    output.txt
    
    
    Hello
    Python

* * *

# 13\. Decimal Context
    
    
    from decimal import Decimal
    from decimal import localcontext
    
    with localcontext() as ctx:
    
        ctx.prec = 50
    
        print(Decimal(1) / Decimal(7))

Ra ngoài

↓

Precision trở lại như cũ.

* * *

# 14\. Suppress Exception
    
    
    from contextlib import suppress
    
    with suppress(FileNotFoundError):
    
        open("abc.txt")

Nếu file không tồn tại

↓

Không crash.

Đây là một Context Manager có sẵn trong `contextlib`.

* * *

# 15\. Chuyển thư mục làm việc tạm thời

Ta có thể tự viết:
    
    
    from pathlib import Path
    import os
    
    
    class ChangeDirectory:
    
        def __init__(self, path):
            self.path = Path(path)
    
        def __enter__(self):
            self.old = Path.cwd()
            os.chdir(self.path)
    
        def __exit__(self, *args):
            os.chdir(self.old)

Sử dụng
    
    
    with ChangeDirectory("/tmp"):
        print(Path.cwd())
    
    print(Path.cwd())

Thư mục luôn được khôi phục sau khi rời khỏi `with`.

* * *

# 16\. Transaction Manager tự viết
    
    
    class Transaction:
    
        def __enter__(self):
    
            print("BEGIN")
    
            return self
    
        def commit(self):
    
            print("COMMIT")
    
        def rollback(self):
    
            print("ROLLBACK")
    
        def __exit__(self, exc_type, exc, tb):
    
            if exc_type:
    
                self.rollback()
    
            else:
    
                self.commit()
    
    
    with Transaction():
    
        print("Update user")

Output
    
    
    BEGIN
    
    Update user
    
    COMMIT

Nếu
    
    
    with Transaction():
    
        raise RuntimeError()

Output
    
    
    BEGIN
    
    ROLLBACK

Đây chính là ý tưởng mà rất nhiều ORM và thư viện cơ sở dữ liệu áp dụng.

* * *

# Những tình huống nên dùng Context Manager

Resource| Có nên dùng `with`?| Lý do  
---|---|---  
File| ✅| Đóng file tự động  
SQLite Transaction| ✅| Commit/Rollback an toàn  
Lock| ✅| Luôn release  
Socket| ✅| Đóng socket  
HTTP Session| ✅| Giải phóng connection pool  
Temporary Directory| ✅| Xóa tài nguyên tạm  
Timer| ✅| Đo thời gian  
Logging Scope| ✅| Ghi log khi vào/ra  
  
* * *

# Bài tập thực hành

## Bài 1

Viết `Timer`:

  * đo thời gian thực thi, 
  * in kết quả sau khi kết thúc khối `with`. 



* * *

## Bài 2

Viết `ChangeDirectory`.

Yêu cầu:
    
    
    with ChangeDirectory("C:/Temp"):
    
        print(Path.cwd())

Sau khi ra khỏi `with`

↓

thư mục cũ phải được khôi phục.

* * *

## Bài 3

Viết `Transaction`.

Nếu:

  * không lỗi → `COMMIT`
  * có lỗi → `ROLLBACK`



* * *

## Bài 4

Viết `Logger`.

Yêu cầu:
    
    
    [12:00:01] START
    
    ...
    
    [12:00:03] END

Có thể dùng `datetime.now()` để ghi thời gian.

* * *

# Tổng kết buổi 4

Sau buổi này, bạn đã thấy Context Manager không chỉ dùng cho `open()` mà là một **mẫu thiết kế (design pattern)** để quản lý vòng đời tài nguyên:
    
    
    Acquire Resource
            │
            ▼
        __enter__()
            │
            ▼
        Use Resource
            │
            ▼
        __exit__()
            │
            ▼
     Release/Cleanup

Các thư viện lớn trong hệ sinh thái Python đều dựa trên ý tưởng này.

* * *

# Chuẩn bị cho buổi 5

Ở buổi tiếp theo, chúng ta sẽ đi sâu vào **Exception Handling trong Context Manager** , bao gồm:

  * Phân tích chi tiết ba tham số `exc_type`, `exc_value`, `traceback`. 
  * Cách ghi log đầy đủ khi có lỗi. 
  * Chỉ chặn một số loại ngoại lệ và để các ngoại lệ khác tiếp tục lan truyền. 
  * Thiết kế Context Manager an toàn, tránh che giấu lỗi ngoài ý muốn. 



Đây là bước giúp bạn viết các Context Manager đáng tin cậy cho các dự án thực tế.

