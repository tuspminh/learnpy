# Context Manager Deep Dive – Buổi 8

# Nested Context Manager (Quản lý nhiều Context Manager cùng lúc)

> Đây là buổi học cực kỳ quan trọng.

Trong các dự án thực tế, gần như **không bao giờ** bạn chỉ có một Context Manager.

Ví dụ trong dự án **Story Crawler** của bạn:
    
    
    SQLite Connection
            ↓
    Transaction
            ↓
    HTTP Session
            ↓
    Log Session
            ↓
    Download Story

Hoặc:
    
    
    Database
        ↓
    Lock
        ↓
    Temporary File
        ↓
    Open Image

Làm sao Python quản lý tất cả những tài nguyên này?

Đó chính là **Nested Context Manager**.

* * *

# Mục tiêu

Sau buổi này bạn sẽ:

  * Hiểu Nested Context Manager 
  * Hiểu nguyên lý LIFO 
  * Biết thứ tự Enter/Exit 
  * Thiết kế nhiều Context Manager cùng lúc 
  * Biết các lỗi thường gặp 
  * Chuẩn bị cho `ExitStack` (buổi 9) 



* * *

# 1\. Nested Context Manager là gì?

Ví dụ:
    
    
    with Database():
        with Transaction():
            with Logger():
                print("Working")

Có ba Context Manager:
    
    
    Database
    
    ↓
    
    Transaction
    
    ↓
    
    Logger

Python sẽ quản lý tất cả.

* * *

# 2\. Thứ tự Enter

Ví dụ
    
    
    class A:
    
        def __enter__(self):
            print("Enter A")
    
        def __exit__(self, *args):
            print("Exit A")
    
    
    class B:
    
        def __enter__(self):
            print("Enter B")
    
        def __exit__(self, *args):
            print("Exit B")
    
    
    with A():
        with B():
            print("Work")

Output
    
    
    Enter A
    
    Enter B
    
    Work
    
    Exit B
    
    Exit A

* * *

## Quy luật
    
    
    Enter
    
    A
    
    ↓
    
    B
    
    ↓
    
    Work
    
    ↓
    
    Exit
    
    B
    
    ↓
    
    A

Đây là:

# LIFO

Last In

↓

First Out

* * *

# 3\. Ví dụ thực tế
    
    
    with open("a.txt") as f:
    
        with sqlite3.connect("db.sqlite") as conn:
    
            print("Processing...")

Thứ tự
    
    
    Open File
    
    ↓
    
    Open DB
    
    ↓
    
    Processing
    
    ↓
    
    Close DB
    
    ↓
    
    Close File

Điều này rất hợp lý:

Tài nguyên được mở **sau** thì đóng **trước**.

* * *

# 4\. Viết gọn

Python cho phép
    
    
    with A(), B():
        print("Hello")

Tương đương
    
    
    with A():
    
        with B():
    
            print("Hello")

* * *

Thử
    
    
    class A:
    
        def __enter__(self):
            print("Enter A")
    
        def __exit__(self, *args):
            print("Exit A")
    
    
    class B:
    
        def __enter__(self):
            print("Enter B")
    
        def __exit__(self, *args):
            print("Exit B")
    
    
    with A(), B():
        print("Working")

Output
    
    
    Enter A
    
    Enter B
    
    Working
    
    Exit B
    
    Exit A

Hoàn toàn giống.

* * *

# 5\. Python 3.10+

Có thể viết
    
    
    with (
        A(),
        B(),
        C(),
    ):
        ...

Ưu điểm:

  * dễ đọc 
  * không cần dấu `\`
  * thêm/xóa Context Manager dễ dàng 



* * *

# 6\. Có Exception

Ví dụ
    
    
    class A:
    
        def __enter__(self):
            print("Enter A")
    
        def __exit__(self, *args):
            print("Exit A")
    
    
    class B:
    
        def __enter__(self):
            print("Enter B")
    
        def __exit__(self, *args):
            print("Exit B")
    
    
    with A():
    
        with B():
    
            raise RuntimeError()

Output
    
    
    Enter A
    
    Enter B
    
    Exit B
    
    Exit A
    
    RuntimeError

Quan sát:

Dù có lỗi

↓

mọi Context Manager đều cleanup.

* * *

# 7\. Nếu `__enter__` của B thất bại
    
    
    class B:
    
        def __enter__(self):
    
            print("Enter B")
    
            raise RuntimeError()
    
        def __exit__(self, *args):
    
            print("Exit B")
    
    
    with A():
    
        with B():
    
            pass

Output
    
    
    Enter A
    
    Enter B
    
    Exit A
    
    RuntimeError

Điều gì xảy ra?
    
    
    A
    
    ↓
    
    đã enter
    
    ↓
    
    B enter lỗi
    
    ↓
    
    Exit A
    
    ↓
    
    Exception

`Exit B` **không chạy** , vì B chưa enter thành công.

* * *

# 8\. Nếu `__exit__` của B lỗi
    
    
    class B:
    
        def __enter__(self):
    
            print("Enter")
    
        def __exit__(self, *args):
    
            print("Exit")
    
            raise RuntimeError("Exit failed")
    
    
    with A():
    
        with B():
    
            print("Hello")

Output
    
    
    Enter A
    
    Enter
    
    Hello
    
    Exit
    
    Exit A
    
    RuntimeError

Quan sát:

Python **vẫn gọi`Exit A`**.

Đây là điểm rất hay.

* * *

# 9\. Context Manager phụ thuộc nhau

Ví dụ
    
    
    Database
    
    ↓
    
    Transaction
    
    ↓
    
    Repository

Không nên
    
    
    with Repository():
    
        with Database():

Vì:

Repository cần Database.

Đúng
    
    
    with Database() as db:
    
        with Transaction(db):
    
            with Repository(db):
                ...

Thứ tự mở và đóng phản ánh đúng sự phụ thuộc.

* * *

# 10\. Story Crawler

Ví dụ thực tế
    
    
    with Database() as db:
    
        with HttpSession() as session:
    
            with Logger():
    
                crawl()

Lifecycle
    
    
    Connect DB
    
    ↓
    
    Open HTTP
    
    ↓
    
    Start Logger
    
    ↓
    
    Crawl
    
    ↓
    
    Stop Logger
    
    ↓
    
    Close HTTP
    
    ↓
    
    Close DB

Đây là kiến trúc rất phổ biến.

* * *

# 11\. Kết hợp class và `@contextmanager`

Không có vấn đề gì.
    
    
    @contextmanager
    def logger():
    
        print("Start")
    
        try:
    
            yield
    
        finally:
    
            print("End")
    
    
    with Database():
    
        with logger():
    
            print("Working")

Output
    
    
    Connect
    
    Start
    
    Working
    
    End
    
    Disconnect

Python xử lý cả hai loại Context Manager giống nhau.

* * *

# 12\. Context Manager động

Giả sử
    
    
    use_db = True

Nhiều người viết
    
    
    if use_db:
    
        with Database():
    
            work()
    
    else:
    
        work()

Điều này ổn nhưng sẽ trở nên rối khi có nhiều điều kiện.

Đây chính là lý do `contextlib.ExitStack` ra đời.

Chúng ta sẽ học ở buổi 9.

* * *

# 13\. Thứ tự Cleanup

Ví dụ
    
    
    with Database():
    
        with Transaction():
    
            with File():
    
                with Lock():
    
                    ...

Cleanup
    
    
    Release Lock
    
    ↓
    
    Close File
    
    ↓
    
    Commit Transaction
    
    ↓
    
    Close Database

Đây chính là Stack.

* * *

# 14\. Minh họa Stack
    
    
    Enter
    
    Database
    
    ↓
    
    Transaction
    
    ↓
    
    File
    
    ↓
    
    Lock
    
    ----------------
    
    Exit
    
    Lock
    
    ↓
    
    File
    
    ↓
    
    Transaction
    
    ↓
    
    Database

* * *

# 15\. Ví dụ hoàn chỉnh
    
    
    class Database:
    
        def __enter__(self):
            print("Connect DB")
            return self
    
        def __exit__(self, *args):
            print("Disconnect DB")
    
    
    class Http:
    
        def __enter__(self):
            print("Open HTTP")
            return self
    
        def __exit__(self, *args):
            print("Close HTTP")
    
    
    class Logger:
    
        def __enter__(self):
            print("Logger Start")
            return self
    
        def __exit__(self, *args):
            print("Logger Stop")
    
    
    with (
        Database(),
        Http(),
        Logger(),
    ):
        print("Download Story")

Output
    
    
    Connect DB
    
    Open HTTP
    
    Logger Start
    
    Download Story
    
    Logger Stop
    
    Close HTTP
    
    Disconnect DB

* * *

# 16\. Lỗi thường gặp

## Sai 1

Cleanup thủ công.
    
    
    db = Database()
    
    db.connect()
    
    ...

Dễ quên đóng.

* * *

## Sai 2

Lồng quá sâu.
    
    
    with A():
    
        with B():
    
            with C():
    
                with D():
    
                    with E():

Nếu có nhiều Context Manager động, hãy cân nhắc dùng `ExitStack`.

* * *

## Sai 3

Phụ thuộc sai thứ tự.
    
    
    Repository
    
    ↓
    
    Database

Repository không thể hoạt động nếu Database chưa được mở.

* * *

# Best Practices

## Mở theo thứ tự phụ thuộc
    
    
    Database
    
    ↓
    
    Transaction
    
    ↓
    
    Repository
    
    ↓
    
    Logger

* * *

## Đóng theo LIFO
    
    
    Logger
    
    ↓
    
    Repository
    
    ↓
    
    Transaction
    
    ↓
    
    Database

* * *

## Dùng cú pháp nhiều Context Manager
    
    
    with (
        Database() as db,
        Http() as session,
        Logger(),
    ):
        ...

Thay vì lồng nhiều `with` khi điều đó giúp mã rõ ràng hơn.

* * *

# Bài tập

## Bài 1

Tạo ba Context Manager:

  * `Database`
  * `Logger`
  * `Timer`



Mỗi lớp in:
    
    
    Enter ...
    Exit ...

Sử dụng:
    
    
    with (
        Database(),
        Logger(),
        Timer(),
    ):
        print("Working")

Quan sát thứ tự.

* * *

## Bài 2

Cho `Database` và `Transaction`.

Thiết kế sao cho:
    
    
    BEGIN
    
    ↓
    
    UPDATE
    
    ↓
    
    COMMIT
    
    ↓
    
    DISCONNECT

Nếu lỗi
    
    
    BEGIN
    
    ↓
    
    ROLLBACK
    
    ↓
    
    DISCONNECT

* * *

## Bài 3

Trong dự án **Story Crawler** , hãy thiết kế chuỗi Context Manager:
    
    
    Config
    
    ↓
    
    SQLite
    
    ↓
    
    HTTP Session
    
    ↓
    
    Download
    
    ↓
    
    Parser
    
    ↓
    
    Repository
    
    ↓
    
    Logger

Với mỗi Context Manager, hãy trả lời:

  * Nó quản lý tài nguyên gì? 
  * Khi nào nên mở? 
  * Khi nào nên đóng? 
  * Nếu `Parser` gặp lỗi, Context Manager nào cần rollback hoặc cleanup? 



* * *

# Tổng kết buổi 8

Bạn đã hiểu một nguyên lý rất quan trọng:

> **Context Manager hoạt động như một Stack.**

  * Mở theo thứ tự từ ngoài vào trong. 
  * Đóng theo thứ tự ngược lại (LIFO). 
  * Dù có ngoại lệ, các Context Manager đã `__enter__` thành công vẫn được `__exit__`. 



Đây là nền tảng để hiểu **`contextlib.ExitStack`**.

* * *

# Chuẩn bị cho buổi 9 – `ExitStack`

Ở buổi sau, chúng ta sẽ học một trong những công cụ mạnh nhất của `contextlib`:

  * Thêm Context Manager **động** tại runtime. 
  * Quản lý số lượng Context Manager không cố định. 
  * Đăng ký các hàm cleanup tùy ý. 
  * Xây dựng các hệ thống như plugin loader, scraper, hoặc resource manager mà không cần lồng hàng chục khối `with`. 



Đây là kỹ thuật được nhiều framework và thư viện Python sử dụng để quản lý tài nguyên một cách linh hoạt và an toàn.

