# Decorator Deep Dive — Buổi 2

# First-Class Function (Nền tảng thật sự của Decorator)

Ở buổi 1 chúng ta đã biết:

  * Function là object. 
  * Function có thể gán cho biến. 



Hôm nay chúng ta sẽ học **First-Class Function**.

Đây là khái niệm quan trọng nhất để hiểu Decorator, Closure, Callback, Event, Plugin Architecture, Flask, FastAPI...

* * *

# Mục tiêu buổi học

Sau buổi này bạn sẽ hiểu được:

  * First-Class Citizen là gì? 
  * Vì sao Function là First-Class Object 
  * Function khác Method như thế nào 
  * Function Object vs Function Call 
  * Callable Object 
  * Callback 
  * Higher Order Function (HOF) 
  * Thực hành nhiều ví dụ thực tế 



* * *

# 1\. First-Class Citizen là gì?

Trong khoa học máy tính có khái niệm:

> Một đối tượng được gọi là **First-Class Citizen** nếu nó có thể được đối xử như dữ liệu.

Ví dụ:

Nếu số nguyên có thể

  * gán cho biến 
  * truyền vào hàm 
  * trả về từ hàm 
  * lưu trong list 



thì số nguyên là First-Class.

Python còn tiến thêm một bước.

**Function cũng là First-Class.**

* * *

# 2\. Điều kiện của First-Class Function

Một function được gọi là First-Class nếu có đủ khả năng:

✓ Gán vào biến
    
    
    def hello():
        print("Hello")
    
    f = hello

* * *

✓ Lưu trong container
    
    
    funcs = [hello]

* * *

✓ Truyền làm tham số
    
    
    execute(hello)

* * *

✓ Trả về từ function khác
    
    
    def create():
        return hello

* * *

Nếu một ngôn ngữ hỗ trợ tất cả điều này thì function là First-Class.

Python hỗ trợ toàn bộ.

* * *

# 3\. Function Object và Function Call

Đây là lỗi phổ biến nhất.

Ví dụ
    
    
    def hello():
        print("Hello")

Có hai khái niệm hoàn toàn khác nhau.

## Function Object
    
    
    hello

Nó chỉ là object.
    
    
    hello
    
    ↓
    
    Function Object

Chưa chạy.

* * *

## Function Call
    
    
    hello()

Lúc này code mới chạy.
    
    
    hello()
    
    ↓
    
    print("Hello")

* * *

Ví dụ
    
    
    def hello():
        print("Hello")
    
    print(hello)

Kết quả
    
    
    <function hello at 0x...>

Không chạy.

* * *

Ví dụ
    
    
    print(hello())

Kết quả
    
    
    Hello
    None

Giải thích
    
    
    hello()
    
    ↓
    
    print("Hello")
    
    ↓
    
    return None

Sau đó
    
    
    print(None)

* * *

# 4\. Quan sát bằng id()
    
    
    def hello():
        pass
    
    print(id(hello))

Ví dụ
    
    
    4398129008

Gán
    
    
    f = hello
    
    print(id(f))

Kết quả
    
    
    4398129008

Cùng một object.
    
    
    hello ----+
    
               |
    
               +------ Function Object
    
               |
    
    f ---------+

* * *

# 5\. Function có thể đổi tên
    
    
    def hello():
        print("Hello")

Đổi tên
    
    
    say_hi = hello

Bây giờ
    
    
    say_hi()

Kết quả
    
    
    Hello

Nếu
    
    
    del hello

thì
    
    
    say_hi()

vẫn chạy.

Vì object vẫn còn.
    
    
    say_hi
    
    ↓
    
    Function Object

* * *

# 6\. Function có thể nằm trong List
    
    
    def add():
        print("Add")
    
    def remove():
        print("Remove")
    
    def update():
        print("Update")
    
    
    commands = [
        add,
        remove,
        update,
    ]

Thực thi
    
    
    for command in commands:
        command()

Kết quả
    
    
    Add
    Remove
    Update

* * *

# 7\. Function nằm trong Dictionary

Đây là kỹ thuật rất phổ biến.
    
    
    def add(a, b):
        return a + b
    
    def sub(a, b):
        return a - b
    
    def mul(a, b):
        return a * b
    
    
    operations = {
        "+": add,
        "-": sub,
        "*": mul,
    }

Gọi
    
    
    op = operations["*"]
    
    print(op(5, 4))
    
    
    20

Không cần
    
    
    if ...
    elif ...
    elif ...

Đây gọi là **Dispatch Table**.

* * *

# 8\. Function truyền làm tham số

Ví dụ
    
    
    def hello():
        print("Hello")
    
    
    def execute(func):
        print("Start")
        func()
        print("Done")

Gọi
    
    
    execute(hello)

Kết quả
    
    
    Start
    Hello
    Done

Ở đây
    
    
    hello
    
    ↓
    
    execute
    
    ↓
    
    func
    
    ↓
    
    hello()

Function được truyền giống hệt một biến.

* * *

# 9\. Callback là gì?

Callback là:

> Một function được truyền vào function khác để được gọi sau.

Ví dụ
    
    
    def notify():
        print("Finished!")
    
    
    def download(callback):
        print("Downloading...")
        callback()
    
    
    download(notify)

Kết quả
    
    
    Downloading...
    Finished!

Đây là callback.

* * *

Ví dụ thực tế
    
    
    def success():
        print("Save success.")
    
    def save_data(callback):
        print("Saving...")
        callback()
    
    save_data(success)

* * *

# 10\. Higher Order Function (HOF)

Higher Order Function là function:

  * nhận function làm tham số 
  * hoặc trả về function 



Ví dụ
    
    
    def hello():
        print("Hello")
    
    
    def execute(func):
        func()

`execute` là HOF.

* * *

Ví dụ
    
    
    def create():
        return hello

`create` cũng là HOF.

* * *

Decorator chính là một Higher Order Function.

* * *

# 11\. Function trả về Function

Ví dụ
    
    
    def english():
        def hello():
            print("Hello")
    
        return hello
    
    
    english()
    
    ↓
    
    return hello
    
    ↓
    
    Function Object

Gọi
    
    
    f = english()
    
    f()

Kết quả
    
    
    Hello

Đây là bước đầu của Closure.

* * *

# 12\. Callable Object

Không chỉ Function mới gọi được.

Ví dụ
    
    
    class Printer:
    
        def __call__(self):
            print("Printing...")
    
    
    p = Printer()
    
    p()

Kết quả
    
    
    Printing...

Điều này xảy ra vì Python sẽ gọi
    
    
    p.__call__()

* * *

Kiểm tra
    
    
    print(callable(p))
    
    
    True

* * *

Kiểm tra function
    
    
    print(callable(hello))
    
    
    True

* * *

Kiểm tra int
    
    
    print(callable(10))
    
    
    False

* * *

# 13\. Hàm là dữ liệu

Ví dụ
    
    
    def square(x):
        return x * x
    
    
    def cube(x):
        return x ** 3
    
    
    def calculate(func, number):
        return func(number)

Sử dụng
    
    
    print(calculate(square, 5))
    print(calculate(cube, 5))

Kết quả
    
    
    25
    125

Không cần sửa `calculate`.

* * *

# 14\. Ví dụ thực tế — Hệ thống Plugin
    
    
    plugins = []

Plugin A
    
    
    def plugin_a():
        print("Plugin A")

Plugin B
    
    
    def plugin_b():
        print("Plugin B")

Đăng ký
    
    
    plugins.append(plugin_a)
    plugins.append(plugin_b)

Thực thi
    
    
    for plugin in plugins:
        plugin()

Kết quả
    
    
    Plugin A
    Plugin B

Đây chính là nền tảng của Plugin Architecture.

* * *

# 15\. Ví dụ thực tế — Mini Event System
    
    
    listeners = []

Đăng ký
    
    
    def on_login(user):
        print(f"{user} logged in")
    
    def on_log(user):
        print(f"Write log: {user}")
    
    listeners.append(on_login)
    listeners.append(on_log)

Phát sự kiện
    
    
    def emit(user):
        for listener in listeners:
            listener(user)
    
    emit("Alice")

Kết quả
    
    
    Alice logged in
    Write log: Alice

Các framework GUI (PySide6, Tkinter), web và message queue đều hoạt động theo mô hình này.

* * *

# 16\. Ví dụ hoàn chỉnh — Mini Task Runner
    
    
    import time
    
    
    def timer(task):
        start = time.perf_counter()
        task()
        end = time.perf_counter()
        print(f"Execution time: {end - start:.6f} s")
    
    
    def backup():
        print("Backing up database...")
        time.sleep(1)
    
    
    def cleanup():
        print("Cleaning temporary files...")
        time.sleep(0.5)
    
    
    def report():
        print("Generating report...")
        time.sleep(0.2)
    
    
    tasks = [backup, cleanup, report]
    
    for task in tasks:
        print(f"\nRunning: {task.__name__}")
        timer(task)

**Kết quả (ví dụ):**
    
    
    Running: backup
    Backing up database...
    Execution time: 1.001234 s
    
    Running: cleanup
    Cleaning temporary files...
    Execution time: 0.500987 s
    
    Running: report
    Generating report...
    Execution time: 0.200431 s

Lưu ý rằng `timer` nhận một hàm làm tham số. Ở các buổi sau, chúng ta sẽ biến `timer(task)` thành cú pháp đẹp hơn:
    
    
    @timer
    def backup():
        ...

Đó chính là sức mạnh của decorator.

* * *

# Tóm tắt buổi 2

Bạn cần ghi nhớ các khái niệm sau:

Khái niệm| Ý nghĩa  
---|---  
First-Class Function| Hàm được đối xử như dữ liệu  
Function Object| Bản thân đối tượng hàm (`hello`)  
Function Call| Gọi thực thi hàm (`hello()`)  
Callback| Hàm được truyền vào để gọi sau  
Higher Order Function| Hàm nhận hoặc trả về hàm  
Callable| Bất kỳ đối tượng nào có `__call__()` và có thể gọi bằng `()`  
Dispatch Table| Dùng `dict` ánh xạ khóa → hàm thay cho nhiều `if/elif`  
  
* * *

# Bài tập

## Bài 1

Tạo một `dict` chứa 5 phép toán:

  * cộng 
  * trừ 
  * nhân 
  * chia 
  * lũy thừa 



Sau đó viết hàm:
    
    
    calculate(op, a, b)

để thực hiện phép toán bằng cách tra cứu trong `dict`.

* * *

## Bài 2

Viết một **Task Scheduler** :

  * Tạo 5 hàm (`backup`, `clean`, `compress`, `report`, `upload`). 
  * Lưu tất cả vào một `list`. 
  * Duyệt và thực thi từng hàm theo thứ tự. 



* * *

## Bài 3

Xây dựng một **Mini Event System** :

  * Có `register(listener)` để đăng ký hàm lắng nghe. 
  * Có `emit(data)` để phát sự kiện đến tất cả listener. 
  * Đăng ký ít nhất 3 listener khác nhau (ví dụ: ghi log, gửi email giả lập, hiển thị thông báo). 



Đây là mô hình nền tảng của các framework GUI, web server và hệ thống plugin.

* * *

Ở **buổi 3** , chúng ta sẽ học **Closure** — mảnh ghép quan trọng nhất trước khi bước vào xây dựng Decorator thực thụ. Sau buổi đó, bạn sẽ hiểu tại sao một hàm có thể "ghi nhớ" biến của hàm cha ngay cả khi hàm cha đã kết thúc. Đây là cơ chế cốt lõi mà hầu hết decorator trong Python đều dựa vào.

