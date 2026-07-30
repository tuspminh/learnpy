# Context Manager Deep Dive – Buổi 2

# Context Manager Protocol (`__enter__` và `__exit__`)

Ở buổi 1, chúng ta đã biết cách sử dụng:
    
    
    with open("data.txt") as f:
        print(f.read())

Nhưng câu hỏi quan trọng là:

> **`with` hoạt động như thế nào?**

Đến cuối buổi học này, bạn sẽ hiểu chính xác Python làm gì khi gặp câu lệnh `with`.

* * *

# Mục tiêu

Sau buổi này bạn sẽ:

  * Hiểu Context Manager Protocol 
  * Hiểu `__enter__()`
  * Hiểu `__exit__()`
  * Tự viết Context Manager đầu tiên 
  * Hiểu vì sao `with` có thể xử lý exception 
  * Hiểu thứ tự gọi các hàm 



* * *

# 1\. Context Manager Protocol

Một object trở thành Context Manager nếu nó có hai phương thức:
    
    
    __enter__()
    
    __exit__()

Ví dụ
    
    
    class MyContext:
    
        def __enter__(self):
            ...
    
        def __exit__(self, exc_type, exc_value, traceback):
            ...

Đơn giản vậy thôi.

Không cần kế thừa class nào.

Không cần interface.

Python chỉ kiểm tra:

> Có `__enter__` và `__exit__` hay không.

Đây gọi là **Duck Typing**.

* * *

# 2\. Context Manager đầu tiên
    
    
    class MyContext:
    
        def __enter__(self):
            print("Enter")
    
        def __exit__(self, exc_type, exc_value, traceback):
            print("Exit")

Sử dụng
    
    
    with MyContext():
        print("Working...")

Kết quả
    
    
    Enter
    Working...
    Exit

* * *

## Thứ tự
    
    
    Tạo object
    
    ↓
    
    __enter__()
    
    ↓
    
    Code trong with
    
    ↓
    
    __exit__()

* * *

# 3\. Python thực hiện gì?

Đoạn
    
    
    with MyContext():
        print("Hello")

Python gần tương đương
    
    
    ctx = MyContext()
    
    ctx.__enter__()
    
    try:
        print("Hello")
    finally:
        ctx.__exit__(None, None, None)

Đó là lý do Context Manager luôn cleanup.

* * *

# 4\. Giá trị trả về của `__enter__`

Ví dụ
    
    
    class MyContext:
    
        def __enter__(self):
            print("Enter")
            return 100
    
        def __exit__(self, exc_type, exc_value, traceback):
            print("Exit")
    
    
    with MyContext() as x:
        print(x)

Kết quả
    
    
    Enter
    100
    Exit

* * *

## Điều gì xảy ra?
    
    
    return của __enter__()
    
    ↓
    
    gán vào biến sau chữ as

Ví dụ
    
    
    with open("a.txt") as f:

thực chất
    
    
    f = open(...).__enter__()

* * *

# 5\. Trả về chính object

Đây là kiểu phổ biến nhất.
    
    
    class Database:
    
        def __enter__(self):
            print("Open DB")
            return self
    
        def __exit__(self, exc_type, exc_value, traceback):
            print("Close DB")
    
        def query(self):
            print("SELECT ...")

Sử dụng
    
    
    with Database() as db:
        db.query()

Kết quả
    
    
    Open DB
    SELECT ...
    Close DB

Đây là cách hầu hết thư viện hoạt động.

* * *

# 6\. `__exit__` nhận gì?

Định nghĩa
    
    
    def __exit__(self,
                 exc_type,
                 exc_value,
                 traceback):

Ba tham số này chứa thông tin về ngoại lệ.

Nếu không có lỗi
    
    
    exc_type = None
    
    exc_value = None
    
    traceback = None

* * *

Ví dụ
    
    
    class Demo:
    
        def __enter__(self):
            print("Enter")
            return self
    
        def __exit__(self, exc_type, exc_value, tb):
    
            print(exc_type)
            print(exc_value)
    
    
    with Demo():
        pass

Kết quả
    
    
    Enter
    None
    None

* * *

# 7\. Nếu có Exception
    
    
    class Demo:
    
        def __enter__(self):
            print("Enter")
            return self
    
        def __exit__(self, exc_type, exc_value, tb):
    
            print(exc_type)
            print(exc_value)
    
    
    with Demo():
        1 / 0

Kết quả
    
    
    Enter
    
    <class 'ZeroDivisionError'>
    
    division by zero
    
    Traceback...

Python truyền toàn bộ exception vào `__exit__`.

* * *

# 8\. `__exit__` luôn được gọi

Ví dụ
    
    
    class Demo:
    
        def __enter__(self):
            print("Open")
    
        def __exit__(self, *args):
            print("Cleanup")
    
    
    with Demo():
        raise RuntimeError()

Output
    
    
    Open
    
    Cleanup
    
    RuntimeError

Cleanup luôn chạy.

Đây chính là điểm mạnh của Context Manager.

* * *

# 9\. Thử mô phỏng open()
    
    
    class FakeFile:
    
        def __enter__(self):
            print("Open file")
            return self
    
        def __exit__(self, *args):
            print("Close file")
    
        def read(self):
            print("Reading...")
    
    
    with FakeFile() as f:
        f.read()

Output
    
    
    Open file
    
    Reading...
    
    Close file

* * *

# 10\. Context Manager Database
    
    
    class Database:
    
        def __enter__(self):
    
            print("Connect")
    
            return self
    
        def execute(self, sql):
    
            print(sql)
    
        def __exit__(self, *args):
    
            print("Disconnect")
    
    
    with Database() as db:
    
        db.execute("SELECT * FROM users")

Output
    
    
    Connect
    
    SELECT * FROM users
    
    Disconnect

* * *

# 11\. Quan sát thứ tự thực thi
    
    
    class Demo:
    
        def __init__(self):
            print("Init")
    
        def __enter__(self):
            print("Enter")
            return self
    
        def __exit__(self, *args):
            print("Exit")
    
    
    with Demo():
        print("Inside")

Output
    
    
    Init
    
    Enter
    
    Inside
    
    Exit

Sơ đồ
    
    
    __init__
    
    ↓
    
    __enter__
    
    ↓
    
    Block with
    
    ↓
    
    __exit__

* * *

# 12\. Có thể dùng lại object
    
    
    ctx = Demo()
    
    with ctx:
        print("One")
    
    with ctx:
        print("Two")

Output
    
    
    Init
    
    Enter
    One
    Exit
    
    Enter
    Two
    Exit

`__init__` chỉ chạy một lần khi tạo đối tượng. Mỗi lần vào khối `with`, Python sẽ gọi `__enter__` và khi thoát sẽ gọi `__exit__`.

> **Lưu ý:** Không phải mọi Context Manager đều an toàn để tái sử dụng. Ví dụ, một đối tượng quản lý transaction hoặc file có thể chỉ được thiết kế để dùng một lần.

* * *

# 13\. Có thể dùng `with` mà không có `as`
    
    
    with Demo():
        print("Hello")

Điều này hoàn toàn hợp lệ.

`as` chỉ dùng khi cần lấy giá trị trả về từ `__enter__`.

* * *

# 14\. Điều gì xảy ra nếu thiếu một phương thức?

Thiếu `__enter__`
    
    
    class A:
    
        def __exit__(self, *args):
            pass
    
    
    with A():
        pass

Kết quả
    
    
    TypeError:
    '__enter__' missing

Thiếu `__exit__`
    
    
    class B:
    
        def __enter__(self):
            return self
    
    
    with B():
        pass

Kết quả
    
    
    TypeError:
    '__exit__' missing

Để trở thành Context Manager hợp lệ, đối tượng phải có **cả hai** phương thức.

* * *

# Tổng kết
    
    
    with Context() as obj:
    
    ↓
    
    obj = Context().__enter__()
    
    ↓
    
    Thực hiện code
    
    ↓
    
    Context().__exit__(...)

Bảng tóm tắt:

Thành phần| Vai trò  
---|---  
`__enter__()`| Khởi tạo tài nguyên và trả về đối tượng sẽ gán sau `as`  
`__exit__()`| Dọn dẹp tài nguyên khi rời khối `with`  
`exc_type`| Kiểu ngoại lệ nếu có  
`exc_value`| Đối tượng ngoại lệ  
`traceback`| Thông tin traceback của ngoại lệ  
`as obj`| Nhận giá trị trả về từ `__enter__()`  
  
* * *

# Bài tập thực hành

## Bài 1

Viết lớp:
    
    
    class Timer:
        ...

Yêu cầu:

  * `__enter__` in `"Start"`
  * `__exit__` in `"Stop"`



Sử dụng:
    
    
    with Timer():
        print("Doing something")

* * *

## Bài 2

Viết lớp:
    
    
    class Printer:

Trong `__enter__`:
    
    
    return "Hello Python"

Kiểm tra:
    
    
    with Printer() as msg:
        print(msg)

Kết quả mong đợi:
    
    
    Hello Python

* * *

## Bài 3

Viết lớp:
    
    
    class Logger:

Trong `__exit__`, in ra:

  * `exc_type`
  * `exc_value`



Sau đó thử:
    
    
    with Logger():
        print("Before error")
        raise ValueError("Invalid input")

Quan sát giá trị của `exc_type` và `exc_value`.

* * *

## Bài 4

Viết `FakeDatabase` với các yêu cầu:

  * `__enter__` in `"Connecting..."`
  * `__exit__` in `"Disconnecting..."`
  * Có phương thức: 


    
    
    query(sql)

để in ra câu lệnh SQL.

Sử dụng:
    
    
    with FakeDatabase() as db:
        db.query("SELECT * FROM users")

* * *

# Chuẩn bị cho buổi 3

Ở buổi tiếp theo, chúng ta sẽ đi sâu vào **cơ chế thực thi của câu lệnh`with`**:

  * Python biên dịch `with` thành bytecode như thế nào. 
  * Luồng điều khiển khi có `return`, `break`, `continue` hoặc ngoại lệ trong khối `with`. 
  * Vai trò đặc biệt của giá trị trả về từ `__exit__` (`True` hoặc `False`) trong việc **chặn hoặc cho phép ngoại lệ lan truyền**. 



Đây là phần giúp bạn hiểu Context Manager ở mức ngôn ngữ, thay vì chỉ biết cách sử dụng.

