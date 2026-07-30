# Decorator Deep Dive — Buổi 6

# Decorator đầu tiên — Python thực sự làm gì khi gặp `@`

Đến đây chúng ta đã có đầy đủ nền tảng:

  * ✅ Function là Object 
  * ✅ First-Class Function 
  * ✅ Closure 
  * ✅ LEGB 
  * ✅ Nested Function 



Hôm nay chúng ta sẽ ghép tất cả lại để tạo ra **Decorator đầu tiên**.

> Đây là buổi quan trọng nhất của toàn bộ khóa học.

* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * Decorator là gì? 
  * Python xử lý `@` như thế nào? 
  * Không dùng `@` có viết decorator được không? 
  * Wrapper là gì? 
  * Decorator thay thế Function như thế nào? 
  * Luồng thực thi của Decorator. 
  * Tự viết nhiều Decorator hoàn chỉnh. 



* * *

# 1\. Decorator là gì?

Định nghĩa đơn giản nhất:

> Decorator là một hàm nhận vào một hàm khác, thêm hành vi mới và trả về một hàm mới.

Nói ngắn gọn:
    
    
    Function
    
    ↓
    
    Decorator
    
    ↓
    
    New Function

Decorator **không sửa mã nguồn của hàm gốc**.

Nó chỉ bọc (wrap) bên ngoài.

* * *

# 2\. Ví dụ đầu tiên

Ta có
    
    
    def hello():
        print("Hello")

Muốn khi gọi
    
    
    hello()

ta được
    
    
    Before
    Hello
    After

Nếu không dùng decorator
    
    
    def hello():
        print("Hello")
    
    
    print("Before")
    hello()
    print("After")

Không tiện.

Nếu có 200 hàm?

Ta sẽ phải copy rất nhiều.

Decorator giải quyết việc này.

* * *

# 3\. Decorator đầu tiên
    
    
    def decorator(func):
    
        def wrapper():
            print("Before")
    
            func()
    
            print("After")
    
        return wrapper

Quan sát thật kỹ.

Có ba thành phần.
    
    
    decorator
    
    ↓
    
    wrapper
    
    ↓
    
    func()

* * *

# 4\. Sử dụng không cần `@`

Ta có
    
    
    def hello():
        print("Hello")

Bọc
    
    
    hello = decorator(hello)

Sau đó
    
    
    hello()

Kết quả
    
    
    Before
    Hello
    After

* * *

# 5\. Python làm gì?

Ban đầu
    
    
    hello
    
    ↓
    
    Function A

Sau dòng
    
    
    hello = decorator(hello)

Python tạo
    
    
    decorator
    
    ↓
    
    wrapper
    
    ↓
    
    func
    
    ↓
    
    Function A

Sau đó
    
    
    hello
    
    ↓
    
    wrapper

Lưu ý

Biến
    
    
    hello

không còn trỏ tới Function A nữa.

Nó trỏ sang wrapper.

* * *

# 6\. Chứng minh
    
    
    def hello():
        print("Hello")

In ra
    
    
    print(hello)

Ví dụ
    
    
    <function hello at 0x...>

Sau
    
    
    hello = decorator(hello)
    
    print(hello)

Ví dụ
    
    
    <function decorator.<locals>.wrapper at 0x...>

Đã đổi object.

* * *

# 7\. Wrapper là gì?

Wrapper là một hàm mới.

Nó bao quanh hàm cũ.
    
    
    wrapper()
    
    ↓
    
    Before
    
    ↓
    
    func()
    
    ↓
    
    After

Hầu hết mọi decorator đều có một wrapper.

* * *

# 8\. Luồng thực thi
    
    
    def decorator(func):
    
        def wrapper():
            print("Before")
            func()
            print("After")
    
        return wrapper
    
    
    def hello():
        print("Hello")
    
    
    hello = decorator(hello)

Khi gọi
    
    
    hello()

Luồng
    
    
    hello
    
    ↓
    
    wrapper
    
    ↓
    
    print("Before")
    
    ↓
    
    func()
    
    ↓
    
    hello gốc
    
    ↓
    
    print("Hello")
    
    ↓
    
    print("After")

* * *

# 9\. Cú pháp @

Python cho phép viết
    
    
    @decorator
    def hello():
        print("Hello")

Thực ra Python biến thành
    
    
    def hello():
        print("Hello")
    
    hello = decorator(hello)

Hai đoạn này **100% giống nhau**.

Không có khác biệt.

* * *

# 10\. Chứng minh

Ví dụ
    
    
    def decorator(func):
    
        def wrapper():
            print("Decorator")
    
            func()
    
        return wrapper
    
    
    @decorator
    def hello():
        print("Hello")
    
    
    hello()

Kết quả
    
    
    Decorator
    Hello

Viết lại
    
    
    def decorator(func):
    
        def wrapper():
            print("Decorator")
    
            func()
    
        return wrapper
    
    
    def hello():
        print("Hello")
    
    
    hello = decorator(hello)
    
    hello()

Kết quả giống hệt.

* * *

# 11\. Decorator thay thế Function

Quan sát
    
    
    @decorator
    def hello():
        print("Hello")

Sau khi chạy
    
    
    hello
    
    ↓
    
    wrapper

Function cũ vẫn tồn tại.

Nhưng biến
    
    
    hello

đã đổi.

* * *

# 12\. Decorator nhiều hàm
    
    
    def logger(func):
    
        def wrapper():
            print("Running")
    
            func()
    
        return wrapper
    
    
    @logger
    def backup():
        print("Backup")
    
    
    @logger
    def clean():
        print("Clean")
    
    
    backup()
    clean()

Kết quả
    
    
    Running
    Backup
    
    Running
    Clean

Một decorator có thể dùng cho rất nhiều hàm.

* * *

# 13\. Ví dụ thực tế — Logging
    
    
    def logging(func):
    
        def wrapper():
            print(f"Start: {func.__name__}")
    
            func()
    
            print(f"Finish: {func.__name__}")
    
        return wrapper
    
    
    @logging
    def backup():
        print("Backing up...")
    
    
    @logging
    def upload():
        print("Uploading...")
    
    
    backup()
    upload()

Kết quả
    
    
    Start: backup
    Backing up...
    Finish: backup
    
    Start: upload
    Uploading...
    Finish: upload

* * *

# 14\. Ví dụ thực tế — Timer (phiên bản đầu)
    
    
    import time
    
    
    def timer(func):
    
        def wrapper():
            start = time.perf_counter()
    
            func()
    
            end = time.perf_counter()
    
            print(f"Execution: {end-start:.4f}s")
    
        return wrapper
    
    
    @timer
    def task():
        time.sleep(1)
    
    
    task()

Ví dụ
    
    
    Execution: 1.0002s

Đây là tiền thân của `@timer`.

* * *

# 15\. Ví dụ thực tế — Authorization
    
    
    LOGGED_IN = False
    
    
    def login_required(func):
    
        def wrapper():
    
            if not LOGGED_IN:
                print("Permission denied")
                return
    
            func()
    
        return wrapper
    
    
    @login_required
    def dashboard():
        print("Dashboard")
    
    
    dashboard()

Kết quả
    
    
    Permission denied

Nếu
    
    
    LOGGED_IN = True

thì
    
    
    Dashboard

Đây là ý tưởng mà Django, Flask, FastAPI sử dụng.

* * *

# 16\. Decorator có thể bọc Decorator
    
    
    def A(func):
    
        def wrapper():
            print("A Before")
    
            func()
    
            print("A After")
    
        return wrapper
    
    
    def B(func):
    
        def wrapper():
            print("B Before")
    
            func()
    
            print("B After")
    
        return wrapper
    
    
    @A
    @B
    def hello():
        print("Hello")

Python biến thành
    
    
    hello = A(B(hello))

Luồng
    
    
    A Before
    
    ↓
    
    B Before
    
    ↓
    
    Hello
    
    ↓
    
    B After
    
    ↓
    
    A After

Đây gọi là **Decorator Stacking**. Chúng ta sẽ học rất sâu ở các buổi sau.

* * *

# 17\. Minh họa bằng sơ đồ

Trước decorator
    
    
    hello
    
    ↓
    
    Function

Sau decorator
    
    
    hello
    
    ↓
    
    wrapper
    
    ↓
    
    func
    
    ↓
    
    Function

Nếu có hai decorator
    
    
    hello
    
    ↓
    
    wrapper A
    
    ↓
    
    wrapper B
    
    ↓
    
    Function

* * *

# 18\. Ví dụ hoàn chỉnh — Mini Debug Decorator
    
    
    def debug(func):
    
        def wrapper():
            print("=" * 30)
            print(f"Function: {func.__name__}")
            print("Calling...")
    
            func()
    
            print("Done")
            print("=" * 30)
    
        return wrapper
    
    
    @debug
    def backup():
        print("Backup database")
    
    
    @debug
    def report():
        print("Generate report")
    
    
    backup()
    report()

Kết quả
    
    
    ==============================
    Function: backup
    Calling...
    Backup database
    Done
    ==============================
    
    ==============================
    Function: report
    Calling...
    Generate report
    Done
    ==============================

* * *

# 19\. Ví dụ hoàn chỉnh — Mini Transaction
    
    
    def transaction(func):
    
        def wrapper():
            print("BEGIN TRANSACTION")
    
            try:
                func()
                print("COMMIT")
            except Exception:
                print("ROLLBACK")
    
        return wrapper
    
    
    @transaction
    def save_user():
        print("Insert into database")
    
    
    @transaction
    def broken():
        print("Insert...")
        raise RuntimeError("Database error")
    
    
    save_user()
    
    print()
    
    broken()

Kết quả
    
    
    BEGIN TRANSACTION
    Insert into database
    COMMIT
    
    BEGIN TRANSACTION
    Insert...
    ROLLBACK

Đây là ý tưởng được dùng trong nhiều ORM và hệ thống quản lý giao dịch.

* * *

# Decorator hoạt động dựa trên những gì?

Toàn bộ decorator mà chúng ta đã viết đều dựa trên các kiến thức của 5 buổi trước:

Kiến thức| Vai trò  
---|---  
Function Object| Truyền hàm như dữ liệu  
First-Class Function| Nhận và trả về hàm  
Nested Function| Tạo `wrapper` bên trong decorator  
Closure| `wrapper` ghi nhớ `func` sau khi `decorator()` kết thúc  
LEGB| `wrapper` truy cập `func` từ Enclosing Scope  
  
Thiếu **bất kỳ** mảnh ghép nào ở trên thì decorator sẽ không hoạt động.

* * *

# Những hạn chế của decorator hiện tại

Decorator của chúng ta vẫn còn nhiều nhược điểm:
    
    
    def wrapper():
        ...

Nó chỉ hoạt động với các hàm **không có tham số**.

Ví dụ:
    
    
    @debug
    def add(a, b):
        return a + b

Khi gọi:
    
    
    add(1, 2)

sẽ nhận lỗi:
    
    
    TypeError:
    wrapper() takes 0 positional arguments but 2 were given

Đây là vấn đề mà chúng ta sẽ giải quyết ở **buổi 7** bằng cách sử dụng:
    
    
    *args
    **kwargs

để tạo decorator có thể bọc **mọi hàm** , bất kể số lượng tham số hay kiểu tham số.

* * *

# Tổng kết buổi 6

Bạn cần nắm chắc:

  1. Decorator là hàm nhận một hàm và trả về một hàm mới. 
  2. `@decorator` chỉ là cú pháp rút gọn của: 


    
    
    hello = decorator(hello)

  3. `wrapper` là hàm thay thế hàm gốc. 
  4. `wrapper` sử dụng **Closure** để ghi nhớ `func`. 
  5. Có thể xếp chồng nhiều decorator. 
  6. Decorator hiện tại chỉ hoạt động với hàm không có tham số. 



* * *

# Bài tập

## Bài 1

Viết decorator `@announce`:
    
    
    @announce
    def deploy():
        print("Deploy application")

Kết quả:
    
    
    === START ===
    Deploy application
    === END ===

* * *

## Bài 2

Viết decorator `@repeat_twice`:
    
    
    @repeat_twice
    def hello():
        print("Hello")

Kết quả:
    
    
    Hello
    Hello

* * *

## Bài 3

Viết hai decorator:

  * `@logger`
  * `@timer` (không cần hỗ trợ tham số) 



Áp dụng đồng thời:
    
    
    @logger
    @timer
    def backup():
        ...

Quan sát và giải thích **thứ tự thực thi** của hai decorator.

* * *

# Chuẩn bị cho buổi 7

Ở **buổi 7** , chúng ta sẽ nâng cấp decorator để hoạt động với **mọi loại hàm** bằng cách sử dụng `*args` và `**kwargs`. Bạn cũng sẽ học cách **trả về giá trị (`return`)** từ hàm gốc mà không làm thay đổi hành vi của nó. Đây là mẫu decorator mà hầu hết các thư viện và framework Python sử dụng trong thực tế.

