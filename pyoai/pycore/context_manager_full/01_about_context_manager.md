# Buổi 1

# Context Manager là gì?

## Một vấn đề rất phổ biến

Ví dụ mở file.
    
    
    f = open("data.txt")
    
    data = f.read()
    
    f.close()

Có vẻ bình thường.

Nhưng...

Nếu xảy ra lỗi?
    
    
    f = open("data.txt")
    
    x = 1 / 0
    
    f.close()

Kết quả
    
    
    ZeroDivisionError

File không bao giờ được đóng.

Đây gọi là

> Resource Leak

Resource gồm

  * file 
  * socket 
  * database connection 
  * lock 
  * thread 
  * process 
  * memory mapping 
  * GPU handle 



* * *

## Cách giải quyết cũ
    
    
    f = open("data.txt")
    
    try:
        data = f.read()
    finally:
        f.close()

Lúc này dù lỗi
    
    
    1 / 0

thì
    
    
    f.close()

vẫn chạy.

Đây là cách Python làm trước khi có `with`.

* * *

# Cách Python hiện đại
    
    
    with open("data.txt") as f:
        data = f.read()

Không cần
    
    
    close()

Python tự làm.

Đây chính là

> Context Manager

* * *

# Ý tưởng của Context Manager

Có thể tưởng tượng như sau:
    
    
    Vào phòng
    
    ↓
    
    Làm việc
    
    ↓
    
    Ra khỏi phòng
    
    ↓
    
    Dọn dẹp

Python cũng vậy
    
    
    Bắt đầu Context
    
    ↓
    
    Thực hiện code
    
    ↓
    
    Kết thúc Context
    
    ↓
    
    Cleanup

* * *

# Ví dụ đời thực

## Ví dụ 1

Mượn chìa khóa
    
    
    Nhận chìa khóa
    
    ↓
    
    Mở cửa
    
    ↓
    
    Làm việc
    
    ↓
    
    Trả chìa khóa

Nếu quên trả?

Có vấn đề.

Context Manager đảm bảo luôn trả chìa khóa.

* * *

## Ví dụ 2

Kết nối Database
    
    
    Open Connection
    
    ↓
    
    Query
    
    ↓
    
    Commit/Rollback
    
    ↓
    
    Close Connection

Không đóng connection

↓

Memory Leak

↓

Too many connections

↓

Server chết.

* * *

## Ví dụ 3

Mutex Lock
    
    
    Acquire Lock
    
    ↓
    
    Do something
    
    ↓
    
    Release Lock

Nếu exception xảy ra?

Lock vẫn giữ.

Các thread khác đứng chờ mãi.

Context Manager giải quyết điều này.

* * *

# Cú pháp
    
    
    with something as obj:
        ...

Python sẽ gọi
    
    
    something.__enter__()
    
    ↓
    
    obj
    
    ↓
    
    code
    
    ↓
    
    something.__exit__()

Đây chính là protocol của Context Manager.

* * *

# Ví dụ với file
    
    
    with open("hello.txt") as f:
        print(f.read())

Python thực hiện gần như
    
    
    f = open("hello.txt")
    
    try:
        print(f.read())
    finally:
        f.close()

* * *

# Nhiều Context Manager
    
    
    with open("a.txt") as fa, open("b.txt") as fb:
        ...

Python sẽ
    
    
    Open a
    
    Open b
    
    ...
    
    Close b
    
    Close a

Đóng theo thứ tự ngược lại (LIFO).

* * *

# Context không chỉ cho file

Ví dụ lock
    
    
    lock.acquire()
    
    try:
        ...
    finally:
        lock.release()

Viết đẹp hơn
    
    
    with lock:
        ...

* * *

Ví dụ sqlite
    
    
    with sqlite3.connect("db.sqlite") as conn:
        conn.execute(...)

Kết thúc

  * commit 
  * rollback nếu lỗi 
  * đóng connection (nếu bạn quản lý vòng đời kết nối theo context) 



* * *

# Một số Context Manager có sẵn

Đối tượng| Ý nghĩa  
---|---  
`open()`| Đóng file tự động  
`threading.Lock()`| Release lock  
`sqlite3.Connection`| Quản lý transaction  
`decimal.localcontext()`| Thiết lập ngữ cảnh tính toán tạm thời  
`tempfile.TemporaryDirectory()`| Xóa thư mục tạm  
`contextlib.redirect_stdout()`| Chuyển hướng `stdout` tạm thời  
`contextlib.suppress()`| Bỏ qua ngoại lệ được chỉ định  
  
* * *

# Điều quan trọng

Context Manager **không phải** để đóng file.

Mục đích thực sự là:

> **Quản lý vòng đời (lifecycle) của một tài nguyên (resource).**

Mọi resource đều có:
    
    
    Khởi tạo
    
    ↓
    
    Sử dụng
    
    ↓
    
    Cleanup

Context Manager chuẩn hóa quy trình này.

* * *

# Tư duy của lập trình viên chuyên nghiệp

Thay vì nghĩ:

> "Tôi đang mở file."

Hãy nghĩ:

> "Tôi đang mượn một resource."

Resource có thể là:

  * File 
  * Database 
  * HTTP Session 
  * Socket 
  * Redis connection 
  * Kafka producer 
  * GPU Memory 
  * Mutex Lock 
  * Transaction 
  * Temporary directory 
  * Logging scope 



Mọi resource đều có thể được quản lý bằng Context Manager.

* * *

# Bài tập thực hành

## Bài 1

Tạo file:
    
    
    hello.txt

Nội dung:
    
    
    Hello Python
    Context Manager

Đọc file bằng:
    
    
    with open(...) as f:
        ...

và in ra nội dung.

* * *

## Bài 2

Viết hai phiên bản:

**Phiên bản 1**
    
    
    f = open(...)
    try:
        ...
    finally:
        ...

**Phiên bản 2**
    
    
    with open(...) as f:
        ...

So sánh:

  * Độ dài mã nguồn. 
  * Mức độ dễ đọc. 
  * Khả năng tự động dọn dẹp tài nguyên khi có ngoại lệ. 



* * *

## Bài 3

Viết chương trình đọc đồng thời hai file:
    
    
    a.txt
    b.txt

Sử dụng:
    
    
    with open(...) as fa, open(...) as fb:
        ...

và in nội dung của cả hai file.

* * *

## Bài 4

Tạo một lỗi có chủ đích:
    
    
    with open("hello.txt") as f:
        raise RuntimeError("Something went wrong")

Quan sát rằng chương trình ném ngoại lệ, nhưng file vẫn được đóng tự động khi thoát khỏi khối `with`. (Trong buổi sau, chúng ta sẽ tìm hiểu cơ chế `__exit__` đã làm điều này như thế nào.)

* * *

## Kiến thức đạt được sau buổi 1

Sau buổi học này, bạn sẽ:

  * Hiểu được vấn đề mà Context Manager giải quyết. 
  * Biết vì sao `with` an toàn hơn `try...finally` trong nhiều trường hợp. 
  * Sử dụng thành thạo `with` với các Context Manager có sẵn như `open()`. 
  * Có tư duy xem Context Manager là công cụ quản lý vòng đời tài nguyên, không chỉ là cú pháp để đóng file. 



Ở **buổi 2** , chúng ta sẽ đi sâu vào **Context Manager Protocol** (`__enter__` và `__exit__`), tự xây dựng một Context Manager đầu tiên và hiểu chính xác Python làm gì khi thực thi câu lệnh `with`. Đây là nền tảng để bạn có thể tự thiết kế các Context Manager cho file, database, transaction, lock hay bất kỳ tài nguyên nào trong các dự án Python chuyên nghiệp.

