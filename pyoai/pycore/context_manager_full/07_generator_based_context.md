# Context Manager Deep Dive – Buổi 7

# `contextlib` và `@contextmanager` (Generator-based Context Manager)

> Đây là một trong những tính năng "đậm chất Python" nhất.

Sau buổi này, bạn sẽ hiểu vì sao chỉ với **một generator có một lệnh`yield`**, Python có thể tạo ra một Context Manager hoàn chỉnh.

Đây cũng là lúc kiến thức về **Generator Deep Dive** mà bạn đã học bắt đầu kết nối với Context Manager.

* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * `contextlib` là gì 
  * `@contextmanager`
  * Tại sao chỉ cần một `yield`
  * Cơ chế hoạt động bên trong 
  * Khi nào nên dùng class, khi nào nên dùng generator 
  * Best Practices 



* * *

# 1\. Trước đây chúng ta viết thế này
    
    
    class Timer:
    
        def __enter__(self):
            print("Start")
            return self
    
        def __exit__(self, exc_type, exc, tb):
            print("Stop")

Sử dụng
    
    
    with Timer():
        print("Working")

Hoàn toàn đúng.

Nhưng hơi dài.

* * *

# 2\. Python cung cấp `contextlib`
    
    
    from contextlib import contextmanager

Decorator này giúp biến **generator** thành Context Manager.

* * *

# 3\. Context Manager đầu tiên
    
    
    from contextlib import contextmanager
    
    
    @contextmanager
    def timer():
    
        print("Start")
    
        yield
    
        print("Stop")

Sử dụng
    
    
    with timer():
        print("Working")

Output
    
    
    Start
    Working
    Stop

Chỉ 5 dòng.

* * *

# 4\. Điều kỳ diệu nằm ở `yield`

Hãy nhớ lại Generator.
    
    
    def demo():
    
        print("A")
    
        yield
    
        print("B")

Lần đầu
    
    
    next(gen)

Output
    
    
    A

Generator dừng tại `yield`.

* * *

Lần sau
    
    
    next(gen)

Output
    
    
    B

Generator tiếp tục.

* * *

`contextmanager` lợi dụng đúng cơ chế này.

* * *

# 5\. Python làm gì?

Đoạn
    
    
    with timer():
        print("Hello")

Thực tế tương đương
    
    
    gen = timer()
    
    next(gen)
    
    try:
    
        print("Hello")
    
    finally:
    
        next(gen)

Đây chính là ý tưởng cốt lõi.

* * *

# 6\. `yield` tương đương `__enter__`

Ví dụ
    
    
    @contextmanager
    def demo():
    
        print("ENTER")
    
        yield
    
        print("EXIT")

Thứ tự
    
    
    ENTER
    
    ↓
    
    yield
    
    ↓
    
    block with
    
    ↓
    
    EXIT

* * *

# 7\. Giá trị sau `as`

Ví dụ
    
    
    @contextmanager
    def numbers():
    
        yield 100
    
    
    with numbers() as x:
    
        print(x)

Output
    
    
    100

Giống hệt
    
    
    def __enter__(self):
    
        return 100

* * *

# 8\. Ví dụ Database
    
    
    @contextmanager
    def database():
    
        print("Connect")
    
        yield "connection"
    
        print("Disconnect")
    
    
    with database() as conn:
    
        print(conn)

Output
    
    
    Connect
    
    connection
    
    Disconnect

* * *

# 9\. Đo thời gian
    
    
    import time
    
    from contextlib import contextmanager
    
    
    @contextmanager
    def timer():
    
        start = time.perf_counter()
    
        yield
    
        elapsed = time.perf_counter() - start
    
        print(elapsed)

Sử dụng
    
    
    with timer():
    
        total = sum(range(5_000_000))

Ví dụ
    
    
    0.132

* * *

# 10\. Mở file
    
    
    from contextlib import contextmanager
    
    
    @contextmanager
    def my_open(filename):
    
        f = open(filename)
    
        try:
    
            yield f
    
        finally:
    
            f.close()

Sử dụng
    
    
    with my_open("data.txt") as f:
    
        print(f.read())

Hoạt động giống `open()`.

* * *

# 11\. Tại sao phải có `try...finally`?

Sai
    
    
    @contextmanager
    def bad():
    
        print("Open")
    
        yield
    
        print("Close")

Nếu
    
    
    with bad():
    
        1 / 0

Dòng `"Close"` sẽ **không được thực thi** , vì ngoại lệ làm generator thoát trước khi chạy tiếp.

Đúng
    
    
    @contextmanager
    def good():
    
        print("Open")
    
        try:
    
            yield
    
        finally:
    
            print("Close")

Luôn cleanup.

Đây là mẫu chuẩn.

* * *

# 12\. Bắt Exception
    
    
    from contextlib import contextmanager
    
    
    @contextmanager
    def logger():
    
        try:
    
            yield
    
        except Exception as e:
    
            print("Caught:", e)
    
            raise

Sử dụng
    
    
    with logger():
    
        int("abc")

Output
    
    
    Caught: invalid literal...
    
    ValueError

`raise` giúp ngoại lệ tiếp tục lan truyền sau khi ghi log.

* * *

# 13\. Có thể chặn Exception
    
    
    @contextmanager
    def ignore():
    
        try:
    
            yield
    
        except ZeroDivisionError:
    
            print("Ignored")
    
    
    with ignore():
    
        1 / 0
    
    print("Continue")

Output
    
    
    Ignored
    
    Continue

Lưu ý: trong generator-based Context Manager, **nếu bạn bắt ngoại lệ và không`raise` lại**, ngoại lệ được xem là đã được xử lý.

* * *

# 14\. Nhiều Resource
    
    
    @contextmanager
    def resources():
    
        print("Open DB")
    
        print("Open File")
    
        try:
    
            yield
    
        finally:
    
            print("Close File")
    
            print("Close DB")

Output
    
    
    Open DB
    
    Open File
    
    ...
    
    Close File
    
    Close DB

LIFO.

* * *

# 15\. Truyền tham số
    
    
    @contextmanager
    def connect(host):
    
        print("Connect", host)
    
        yield host
    
        print("Disconnect")
    
    
    with connect("localhost") as db:
    
        print(db)

Output
    
    
    Connect localhost
    
    localhost
    
    Disconnect

* * *

# 16\. Điều gì xảy ra nếu có nhiều `yield`?

Sai
    
    
    @contextmanager
    def bad():
    
        yield 1
    
        yield 2

Sử dụng
    
    
    with bad():
        pass

Kết quả
    
    
    RuntimeError:
    generator didn't stop

**Quy tắc vàng:**

> Một Context Manager tạo bằng `@contextmanager` phải có **chính xác một`yield`**.

* * *

# 17\. Bên trong `contextmanager`

Đây là phiên bản mô phỏng đơn giản:
    
    
    class GeneratorContextManager:
    
        def __init__(self, gen):
            self.gen = gen
    
        def __enter__(self):
            return next(self.gen)
    
        def __exit__(self, exc_type, exc, tb):
    
            if exc_type is None:
                try:
                    next(self.gen)
                except StopIteration:
                    return False
            else:
                try:
                    self.gen.throw(exc_type, exc, tb)
                except StopIteration:
                    return True
    
            raise RuntimeError("generator didn't stop")

Đây **không phải** mã nguồn thật của `contextlib`, nhưng giúp bạn hình dung cơ chế hoạt động.

* * *

# 18\. Khi nào dùng Class?

Nên dùng khi:

  * Có nhiều trạng thái 
  * Có nhiều phương thức 
  * Quản lý resource lớn 
  * Có lifecycle phức tạp 



Ví dụ
    
    
    class Database:
    
        connect()
    
        disconnect()
    
        execute()
    
        rollback()
    
        commit()

* * *

# 19\. Khi nào dùng `@contextmanager`?

Rất phù hợp khi:

  * Logic đơn giản 
  * Chỉ cần acquire → release 
  * Không cần nhiều phương thức 
  * Viết tiện ích nhỏ 



Ví dụ
    
    
    @contextmanager
    def timer():
    
    
    @contextmanager
    def suppress_log():
    
    
    @contextmanager
    def change_directory():

* * *

# So sánh

Class| `@contextmanager`  
---|---  
Có trạng thái phức tạp| ❌ Không phù hợp  
Có nhiều phương thức| ❌ Không phù hợp  
Ngắn gọn| ❌  
Dễ đọc| ⭐⭐⭐  
Dễ mở rộng| ⭐⭐⭐⭐⭐  
  
* * *

# Best Practices

Luôn dùng:
    
    
    try:
    
        yield resource
    
    finally:
    
        cleanup()

Không viết:
    
    
    yield
    
    cleanup()

vì cleanup có thể bị bỏ qua nếu có ngoại lệ.

* * *

# Ví dụ hoàn chỉnh
    
    
    from contextlib import contextmanager
    import sqlite3
    
    
    @contextmanager
    def sqlite_transaction(path):
    
        conn = sqlite3.connect(path)
    
        try:
    
            yield conn
    
            conn.commit()
    
        except Exception:
    
            conn.rollback()
    
            raise
    
        finally:
    
            conn.close()

Sử dụng
    
    
    with sqlite_transaction("school.db") as conn:
    
        conn.execute(
            "INSERT INTO student(name) VALUES (?)",
            ("Alice",)
        )

Đây là một Context Manager rất gần với những gì bạn có thể dùng trong dự án thực tế.

* * *

# Bài tập

## Bài 1

Viết `timer()` bằng `@contextmanager`.

Yêu cầu:

  * đo thời gian, 
  * in thời gian khi kết thúc. 



* * *

## Bài 2

Viết `change_directory(path)`.

Yêu cầu:

  * lưu thư mục hiện tại, 
  * chuyển sang thư mục mới, 
  * sau khi thoát `with`, quay về thư mục cũ. 



* * *

## Bài 3

Viết `transaction()`.

Yêu cầu:

  * in `BEGIN`, 
  * `yield`, 
  * nếu thành công → `COMMIT`, 
  * nếu lỗi → `ROLLBACK`. 



* * *

## Bài 4

Viết `log_context(name)`.

Ví dụ:
    
    
    with log_context("Import Stories"):
        ...

Output:
    
    
    [START] Import Stories
    ...
    [END] Import Stories
    Elapsed: 0.456 s

Nếu có lỗi, ghi thêm thông tin ngoại lệ rồi để ngoại lệ tiếp tục lan truyền.

* * *

# Tổng kết buổi 7

Đến đây, bạn đã làm chủ **hai cách xây dựng Context Manager** :

  1. **Class-based Context Manager** (`__enter__` / `__exit__`): mạnh mẽ, phù hợp cho các đối tượng có trạng thái và API phong phú. 
  2. **Generator-based Context Manager** (`@contextmanager`): ngắn gọn, rất phù hợp cho các tiện ích và logic acquire/release đơn giản. 



Việc lựa chọn cách nào phụ thuộc vào độ phức tạp của bài toán.

* * *

# Chuẩn bị cho buổi 8

Ở buổi tiếp theo, chúng ta sẽ học **Nested Context Manager** và cách tổ chức nhiều Context Manager cùng lúc:

  * Cơ chế vào/ra theo nguyên tắc **LIFO**. 
  * Quản lý nhiều tài nguyên phụ thuộc nhau. 
  * Kết hợp Context Manager dạng class và dạng generator. 
  * Thiết kế các khối `with` lồng nhau rõ ràng, dễ bảo trì trong các dự án lớn như hệ thống **Story Crawler** hoặc các ứng dụng sử dụng SQLite, HTTP Session và Logging đồng thời.

