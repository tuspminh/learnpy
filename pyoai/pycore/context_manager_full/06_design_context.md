# Context Manager Deep Dive – Buổi 6

# Thiết kế Context Manager chuyên nghiệp (Design & Best Practices)

> Đây là buổi đánh dấu sự chuyển đổi từ **người biết dùng Context Manager** sang **người có thể tự thiết kế Context Manager chất lượng thư viện (library-quality)**.

Ở các buổi trước, chúng ta viết những ví dụ đơn giản như:
    
    
    class Timer:
        ...

Hôm nay, chúng ta sẽ học cách thiết kế Context Manager giống như các thư viện lớn:

  * SQLAlchemy 
  * requests 
  * asyncio 
  * tempfile 
  * threading 
  * pathlib 



* * *

# Mục tiêu

Sau buổi này bạn sẽ biết:

  * Thiết kế Context Manager theo SOLID 
  * Quản lý nhiều resource 
  * Xử lý lỗi trong `__enter__`
  * Xử lý lỗi trong `__exit__`
  * Thiết kế Context Manager có trạng thái (stateful) 
  * Viết Context Manager có thể tái sử dụng 



* * *

# 1\. Context Manager cũng là một Object

Nhiều người nghĩ Context Manager chỉ có:
    
    
    __enter__()
    
    __exit__()

Thực tế, nó chỉ là một object bình thường.

Ví dụ:
    
    
    class Database:
    
        def __init__(self, db_path):
    
            self.db_path = db_path
    
            self.conn = None
    
        def connect(self):
            ...
    
        def close(self):
            ...
    
        def __enter__(self):
            ...
    
        def __exit__(self, ...):
            ...

Nó có:

  * thuộc tính 
  * phương thức 
  * trạng thái 
  * vòng đời 



* * *

# 2\. Tách trách nhiệm

Sai:
    
    
    class Database:
    
        def __enter__(self):
    
            connect()
    
            authenticate()
    
            create_tables()
    
            load_cache()
    
            check_version()
    
            ...
    
        def __exit__(...):
            ...

`__enter__()` làm quá nhiều việc.

* * *

Đúng:
    
    
    class Database:
    
        def connect(self):
            ...
    
        def authenticate(self):
            ...
    
        def check_version(self):
            ...
    
        def __enter__(self):
    
            self.connect()
    
            self.authenticate()
    
            self.check_version()
    
            return self

`__enter__()` chỉ điều phối (orchestrate).

* * *

# 3\. Có trạng thái

Ví dụ
    
    
    class FileManager:
    
        def __init__(self, filename):
    
            self.filename = filename
    
            self.file = None

Sau khi
    
    
    with FileManager("a.txt") as fm:

Object thay đổi
    
    
    filename
    
    ↓
    
    file=None
    
    ↓
    
    __enter__()
    
    ↓
    
    file=<TextIOWrapper>

Sau `__exit__`
    
    
    file.close()
    
    ↓
    
    file=None

Đây gọi là **state transition**.

* * *

# 4\. Context Manager nên có trạng thái rõ ràng

Ví dụ
    
    
    class Connection:
    
        CLOSED = 0
        OPEN = 1
    
        def __init__(self):
    
            self.state = self.CLOSED

Trong `__enter__`
    
    
    self.state = self.OPEN

Trong `__exit__`
    
    
    self.state = self.CLOSED

Ưu điểm

  * debug dễ 
  * test dễ 
  * tránh gọi sai API 



* * *

# 5\. Không nên để object ở trạng thái nửa vời

Ví dụ
    
    
    class DB:
    
        def __enter__(self):
    
            self.conn = connect()
    
            authenticate()
    
            load_cache()
    
            raise RuntimeError()

Điều gì xảy ra?
    
    
    conn
    
    ↓
    
    đã mở
    
    ↓
    
    exception
    
    ↓
    
    __exit__()
    
    KHÔNG chạy

Connection bị rò rỉ.

* * *

# Cách đúng
    
    
    class DB:
    
        def __enter__(self):
    
            try:
    
                self.conn = connect()
    
                authenticate()
    
                load_cache()
    
                return self
    
            except:
    
                if self.conn:
    
                    self.conn.close()
    
                raise

Đây là nguyên tắc rất quan trọng:

> Nếu `__enter__` thất bại, chính `__enter__` phải tự dọn dẹp các tài nguyên đã cấp phát.

* * *

# 6\. `__exit__` không nên ném exception mới

Sai
    
    
    def __exit__(...):
    
        self.conn.close()
    
        raise RuntimeError()

Nếu block cũng có lỗi

↓

Bạn mất exception gốc.

* * *

Đúng
    
    
    def __exit__(...):
    
        try:
    
            self.conn.close()
    
        except Exception:
    
            logging.exception("Close failed")

Hoặc chỉ ném ngoại lệ mới nếu đó là chủ đích rõ ràng.

* * *

# 7\. Quản lý nhiều Resource

Ví dụ
    
    
    Database
    
    ↓
    
    Socket
    
    ↓
    
    File
    
    ↓
    
    Lock

Không nên
    
    
    def __exit__(...):
    
        file.close()
    
        socket.close()
    
        db.close()

Nếu
    
    
    file.close()
    
    ↓
    
    Exception

Các resource còn lại không được đóng.

* * *

Đúng
    
    
    errors = []
    
    for closer in [
        self.file.close,
        self.socket.close,
        self.db.close,
    ]:
        try:
            closer()
        except Exception as e:
            errors.append(e)

Đảm bảo mọi resource đều được giải phóng.

> Ở **buổi 9** , chúng ta sẽ học `contextlib.ExitStack`, một công cụ của Python giúp quản lý nhiều Context Manager theo cách này một cách an toàn và gọn gàng.

* * *

# 8\. Thiết kế API đẹp

Không nên
    
    
    with Database("db.sqlite") as x:

Tên biến không có ý nghĩa.

Nên
    
    
    with Database("db.sqlite") as db:

Hoặc
    
    
    with Transaction() as tx:

API nên tự mô tả.

* * *

# 9\. Context Manager không nhất thiết trả về `self`

Ví dụ
    
    
    class Config:
    
        def __enter__(self):
    
            return {
                "host": "localhost",
                "port": 3306,
            }
    
        def __exit__(...):
    
            pass

Sử dụng
    
    
    with Config() as cfg:
    
        print(cfg["host"])

`__enter__()` có thể trả về bất kỳ đối tượng nào.

* * *

# 10\. Có thể lồng nhiều tầng
    
    
    with Database() as db:
    
        with Transaction(db):
    
            with Logger():
    
                ...

Hoặc
    
    
    with (
        Database() as db,
        Transaction(db),
        Logger(),
    ):
        ...

Từ Python 3.10+, cách viết trong ngoặc giúp mã dễ đọc hơn khi có nhiều Context Manager.

* * *

# 11\. Context Manager có thể tái sử dụng?

Ví dụ
    
    
    ctx = Timer()
    
    with ctx:
        ...
    
    with ctx:
        ...

Điều này **có thể** đúng.

Nhưng
    
    
    ctx = open("a.txt")
    
    
    with ctx:
        ...

Sau khi thoát

↓

File đã đóng.

Lần sau

↓

Lỗi.

Không phải Context Manager nào cũng reusable.

* * *

# 12\. Thiết kế Resource Lifecycle

Đây là mô hình chuẩn.
    
    
    NEW
    
    ↓
    
    OPENING
    
    ↓
    
    OPEN
    
    ↓
    
    WORKING
    
    ↓
    
    CLOSING
    
    ↓
    
    CLOSED

Không nên
    
    
    NEW
    
    ↓
    
    OPEN
    
    ↓
    
    CLOSED

Quản lý trạng thái rõ ràng sẽ giúp hệ thống lớn ổn định hơn.

* * *

# 13\. Ví dụ hoàn chỉnh
    
    
    from enum import Enum
    
    
    class State(Enum):
        CLOSED = 0
        OPEN = 1
    
    
    class Resource:
    
        def __init__(self):
    
            self.state = State.CLOSED
    
        def open(self):
    
            print("Opening")
    
        def close(self):
    
            print("Closing")
    
        def __enter__(self):
    
            self.open()
    
            self.state = State.OPEN
    
            return self
    
        def __exit__(self, exc_type, exc, tb):
    
            try:
    
                self.close()
    
            finally:
    
                self.state = State.CLOSED

Sử dụng
    
    
    with Resource() as r:
    
        print(r.state)

Output
    
    
    Opening
    
    State.OPEN
    
    Closing

Sau khi thoát
    
    
    State.CLOSED

* * *

# 14\. Ví dụ thực tế: HTTP Client
    
    
    class HttpClient:
    
        def __init__(self):
    
            self.session = None
    
        def __enter__(self):
    
            self.session = requests.Session()
    
            return self.session
    
        def __exit__(self, *args):
    
            self.session.close()

Sử dụng
    
    
    with HttpClient() as session:
    
        session.get(...)

Người dùng không cần nhớ gọi `close()`.

* * *

# 15\. Ví dụ thực tế: Repository

Đây là ví dụ gần với dự án **Story Crawler** mà chúng ta đã trao đổi.
    
    
    class StoryRepository:
    
        def __init__(self, connection):
    
            self.connection = connection
    
        def __enter__(self):
    
            self.connection.begin()
    
            return self
    
        def __exit__(self, exc_type, exc, tb):
    
            if exc_type:
    
                self.connection.rollback()
    
            else:
    
                self.connection.commit()

Sử dụng
    
    
    with StoryRepository(conn) as repo:
    
        repo.add_story(...)
        repo.add_chapter(...)

Đây là cách rất nhiều Repository trong các ứng dụng thực tế quản lý transaction.

* * *

# Best Practices

## `__enter__`

✅ Chỉ khởi tạo tài nguyên.

✅ Nếu thất bại, tự dọn dẹp những gì đã tạo.

✅ Trả về đối tượng có ý nghĩa.

* * *

## `__exit__`

✅ Luôn giải phóng tài nguyên.

✅ Hạn chế ném ngoại lệ mới.

✅ Không che giấu lỗi nếu không có chủ đích.

* * *

## Thiết kế

✅ Có trạng thái rõ ràng.

✅ Tách nhỏ các phương thức.

✅ API dễ đọc.

* * *

# Bài tập

## Bài 1

Viết `FileManager`

Yêu cầu:

  * Có trạng thái `OPEN` và `CLOSED`. 
  * `__enter__` mở file. 
  * `__exit__` đóng file và cập nhật trạng thái. 



* * *

## Bài 2

Viết `DatabaseConnection`

Yêu cầu:

  * `connect()`
  * `disconnect()`
  * `__enter__`
  * `__exit__`



Nếu `connect()` lỗi sau khi đã mở một phần tài nguyên, hãy tự dọn dẹp trước khi ném ngoại lệ.

* * *

## Bài 3

Viết `MultiResource`

Quản lý:

  * một file, 
  * một socket giả (mock), 
  * một logger. 



Trong `__exit__`, đảm bảo tất cả đều được đóng, ngay cả khi một thao tác đóng thất bại.

* * *

## Bài 4

Trong dự án **Story Crawler** , hãy thiết kế một Context Manager tên `ScrapeSession` với vòng đời:
    
    
    NEW
      ↓
    CONNECT_DATABASE
      ↓
    OPEN_HTTP_SESSION
      ↓
    SCRAPING
      ↓
    SAVE_TO_DATABASE
      ↓
    CLOSE_HTTP_SESSION
      ↓
    DISCONNECT_DATABASE

Hãy suy nghĩ:

  * `__enter__` nên làm gì? 
  * `__exit__` nên commit hay rollback khi có lỗi? 
  * Tài nguyên nào cần được giải phóng theo thứ tự nào? 



* * *

# Tổng kết buổi 6

Đến đây, bạn đã nắm vững cách **thiết kế Context Manager dạng class** theo tiêu chuẩn của các thư viện Python chuyên nghiệp.

Từ **buổi 7** , chúng ta sẽ chuyển sang một phong cách hoàn toàn khác nhưng rất phổ biến trong Python:

  * `contextlib`
  * `@contextmanager`
  * Context Manager dựa trên **generator**



Đây là cách mà rất nhiều thư viện trong hệ sinh thái Python triển khai các Context Manager ngắn gọn, dễ đọc và vẫn đảm bảo đầy đủ cơ chế `__enter__`/`__exit__`. Nó cũng là cầu nối để bạn hiểu sâu hơn về mối liên hệ giữa **generator** và **Context Manager** , hai chủ đề rất đặc trưng của Python.

