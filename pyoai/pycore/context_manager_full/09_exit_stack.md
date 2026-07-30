# Context Manager Deep Dive – Buổi 9

# `contextlib.ExitStack` — Quản lý Context Manager động như một lập trình viên chuyên nghiệp

> **ExitStack** là một trong những module mạnh nhất nhưng cũng ít được biết đến trong Python.

Nó xuất hiện rất nhiều trong:

  * pytest 
  * unittest 
  * pathlib 
  * SQLAlchemy 
  * các framework lớn 
  * hệ thống plugin 
  * crawler 
  * automation 



Nếu phải chọn **một chủ đề nâng cao quan trọng nhất** của Context Manager thì đó chính là **ExitStack**.

* * *

# Mục tiêu

Sau buổi này bạn sẽ biết:

  * ExitStack giải quyết vấn đề gì 
  * enter_context() 
  * callback() 
  * push() 
  * pop_all() 
  * Resource Stack 
  * Dynamic Context Manager 
  * Best Practices 



* * *

# 1\. Vấn đề của Nested Context

Giả sử bạn cần mở:

  * 3 file 


    
    
    with open("a.txt") as a:
    
        with open("b.txt") as b:
    
            with open("c.txt") as c:
    
                ...

Nếu là

20 file?
    
    
    with open(...):
    
        with open(...):
    
            with open(...):
    
                with open(...):
    
                    ...

Code bắt đầu rất xấu.

* * *

# 2\. Nếu số lượng file không biết trước?

Ví dụ
    
    
    files = [
        "a.txt",
        "b.txt",
        "c.txt",
        "d.txt",
    ]

Không thể viết
    
    
    with open(a):
    
        with open(b):
    
            ...

vì số lượng thay đổi.

* * *

# 3\. ExitStack ra đời
    
    
    from contextlib import ExitStack

Ví dụ
    
    
    from contextlib import ExitStack
    
    with ExitStack() as stack:
    
        files = []
    
        for name in filenames:
    
            f = stack.enter_context(open(name))
    
            files.append(f)
    
        ...

Python sẽ tự:
    
    
    Open
    
    a
    
    ↓
    
    b
    
    ↓
    
    c
    
    ↓
    
    ...
    
    ↓
    
    Close
    
    ...
    
    ↓
    
    c
    
    ↓
    
    b
    
    ↓
    
    a

* * *

# 4\. `enter_context()`

Đây là hàm quan trọng nhất.
    
    
    stack.enter_context(...)

Nó tương đương
    
    
    with something as x:

Ví dụ
    
    
    with ExitStack() as stack:
    
        f = stack.enter_context(
            open("data.txt")
        )
    
        print(f.read())

* * *

# 5\. Mở nhiều file
    
    
    from contextlib import ExitStack
    
    names = [
        "a.txt",
        "b.txt",
        "c.txt"
    ]
    
    with ExitStack() as stack:
    
        files = [
            stack.enter_context(open(name))
            for name in names
        ]
    
        for f in files:
    
            print(f.read())

Không cần biết có bao nhiêu file.

* * *

# 6\. Hoạt động như Stack

Giả sử
    
    
    stack.enter_context(A())
    
    stack.enter_context(B())
    
    stack.enter_context(C())

Exit
    
    
    Exit C
    
    ↓
    
    Exit B
    
    ↓
    
    Exit A

LIFO.

* * *

# 7\. Có Exception
    
    
    with ExitStack() as stack:
    
        stack.enter_context(A())
    
        stack.enter_context(B())
    
        raise RuntimeError()

Python
    
    
    Enter A
    
    ↓
    
    Enter B
    
    ↓
    
    RuntimeError
    
    ↓
    
    Exit B
    
    ↓
    
    Exit A

Giống Nested Context.

* * *

# 8\. Context Manager động

Ví dụ
    
    
    if use_database:
    
        stack.enter_context(Database())
    
    if use_http:
    
        stack.enter_context(Http())

Không cần
    
    
    if ...
    
        with ...
    
    else ...
    

Rất gọn.

* * *

# 9\. `callback()`

Đây là tính năng cực kỳ mạnh.
    
    
    with ExitStack() as stack:
    
        stack.callback(print, "Cleaning")

Khi kết thúc

↓

Python gọi
    
    
    print("Cleaning")

Không cần Context Manager.

* * *

Ví dụ
    
    
    from contextlib import ExitStack
    
    with ExitStack() as stack:
    
        print("Working")
    
        stack.callback(
            print,
            "Finished"
        )

Output
    
    
    Working
    
    Finished

* * *

# 10\. Callback nhiều lần
    
    
    with ExitStack() as stack:
    
        stack.callback(print, "A")
    
        stack.callback(print, "B")
    
        stack.callback(print, "C")

Output
    
    
    C
    
    B
    
    A

LIFO.

* * *

# 11\. `push()`

`push()` dùng để đăng ký trực tiếp một hàm có giao diện giống `__exit__`.

Ví dụ đơn giản:
    
    
    from contextlib import ExitStack
    
    def cleanup(exc_type, exc, tb):
        print("Cleanup")
        return False
    
    with ExitStack() as stack:
        stack.push(cleanup)
        print("Working")

Output:
    
    
    Working
    Cleanup

Khác với `callback()`, hàm được truyền vào `push()` sẽ nhận ba tham số của `__exit__` và có thể quyết định có chặn ngoại lệ hay không.

* * *

# 12\. `pop_all()`

Đây là chức năng cực kỳ hay.

Ví dụ
    
    
    stack = ExitStack()
    
    with stack:
    
        ...

Sau đó
    
    
    new_stack = stack.pop_all()

Tất cả cleanup được chuyển sang stack mới.

Stack cũ không cleanup nữa.

Điều này hữu ích khi bạn muốn **chuyển quyền sở hữu tài nguyên** sang một thành phần khác.

* * *

# 13\. Kết hợp Context Manager và Callback
    
    
    from contextlib import ExitStack
    
    with ExitStack() as stack:
    
        conn = stack.enter_context(Database())
    
        stack.callback(
            print,
            "Send log"
        )
    
        print("Working")

Cleanup
    
    
    Send log
    
    ↓
    
    Close Database

Do callback được đăng ký sau `Database`, nên nó được gọi trước khi `Database` đóng.

* * *

# 14\. Resource Manager

Ví dụ
    
    
    class ResourceManager:
    
        def load(self):
    
            with ExitStack() as stack:
    
                db = stack.enter_context(Database())
    
                http = stack.enter_context(Http())
    
                log = stack.enter_context(Logger())
    
                ...

Đây là kiến trúc rất phổ biến.

* * *

# 15\. Story Crawler

Ví dụ
    
    
    with ExitStack() as stack:
    
        db = stack.enter_context(Database())
    
        session = stack.enter_context(HttpSession())
    
        logger = stack.enter_context(Logger())
    
        parser = Parser()
    
        parser.parse(...)

Sau này

Bạn muốn thêm
    
    
    Redis
    
    RabbitMQ
    
    Cache
    
    Metrics
    
    Plugin

Chỉ cần
    
    
    stack.enter_context(...)

Không phải sửa cấu trúc `with`.

* * *

# 16\. Ví dụ Plugin
    
    
    plugins = [
        PluginA(),
        PluginB(),
        PluginC(),
    ]
    
    
    with ExitStack() as stack:
    
        active = []
    
        for plugin in plugins:
    
            active.append(
                stack.enter_context(plugin)
            )
    
        print("Running")

Không cần biết có bao nhiêu plugin.

* * *

# 17\. So sánh

Nested
    
    
    with A():
    
        with B():
    
            with C():

ExitStack
    
    
    with ExitStack() as stack:
    
        stack.enter_context(A())
    
        stack.enter_context(B())
    
        stack.enter_context(C())

* * *

# 18\. Khi nào nên dùng ExitStack?

Không nên
    
    
    with A(), B():

nếu
    
    
    A
    
    ↓
    
    B
    
    ↓
    
    C
    
    ↓
    
    D
    
    ↓
    
    E
    
    ↓
    
    ...
    
    ↓
    
    Plugin N

Đặc biệt khi số lượng được quyết định lúc chạy.

* * *

# 19\. Khi nào KHÔNG nên dùng?

Nếu chỉ có
    
    
    with open():
    
        ...

hoặc
    
    
    with Database():

Không cần ExitStack.

Nested đơn giản hơn.

* * *

# 20\. Best Practices

## Dùng khi số lượng Context Manager thay đổi
    
    
    for item:
    
        stack.enter_context(...)

* * *

## Dùng callback cho cleanup đơn giản
    
    
    stack.callback(...)

* * *

## Không lạm dụng

Nếu chỉ có
    
    
    with open():

thì dùng `with` bình thường sẽ rõ ràng hơn.

* * *

# Ví dụ hoàn chỉnh
    
    
    from contextlib import ExitStack
    import tempfile
    
    files = []
    
    with ExitStack() as stack:
    
        for _ in range(3):
    
            f = stack.enter_context(
                tempfile.NamedTemporaryFile(
                    mode="w+",
                    encoding="utf-8"
                )
            )
    
            f.write("Hello\n")
    
            f.seek(0)
    
            files.append(f)
    
        for f in files:
    
            print(f.read().strip())

Python sẽ tự đóng và dọn dẹp cả ba file theo đúng thứ tự.

* * *

# So sánh Nested vs ExitStack

Nested| ExitStack  
---|---  
Ít Context Manager| ✅  
Nhiều Context Manager| ❌  
Số lượng động| ❌  
Plugin| ❌  
Resource Pool| ❌  
Đọc dễ (ít tài nguyên)| ✅  
Mở rộng tốt| ⭐⭐  
  
* * *

# Bài tập

## Bài 1

Viết chương trình:

  * mở 10 file bằng `ExitStack`, 
  * đọc nội dung, 
  * tự động đóng tất cả. 



* * *

## Bài 2

Viết:
    
    
    plugins = [
        PluginA(),
        PluginB(),
        PluginC(),
    ]

Dùng `ExitStack` để kích hoạt tất cả plugin.

* * *

## Bài 3

Thiết kế `ResourceManager`.

Quản lý:

  * Database 
  * HTTP Session 
  * Logger 
  * Cache 



Tất cả đều được thêm bằng:
    
    
    stack.enter_context(...)

* * *

## Bài 4 (Áp dụng cho dự án Story Crawler)

Thiết kế hàm:
    
    
    def crawl_story(source_name):
        ...

Trong đó:

  * Luôn mở `Database`. 
  * Luôn mở `Logger`. 
  * Chỉ mở `HttpSession` nếu source là nguồn trực tuyến. 
  * Chỉ mở `Cache` nếu chế độ cache được bật. 
  * Nếu có plugin tiền xử lý (`PreProcessor`) hoặc hậu xử lý (`PostProcessor`), thêm chúng vào `ExitStack` theo cấu hình. 



Hãy thử triển khai bằng `ExitStack` thay vì nhiều khối `if ... with ...`.

* * *

# Tổng kết buổi 9

Đến đây, bạn đã làm chủ ba phong cách quản lý Context Manager:

  1. **Class-based** (`__enter__` / `__exit__`) – phù hợp với đối tượng có trạng thái và API phong phú. 
  2. **Generator-based** (`@contextmanager`) – ngắn gọn cho các tiện ích acquire/release. 
  3. **`ExitStack`** – mạnh mẽ khi số lượng Context Manager chỉ được biết tại runtime hoặc cần kết hợp nhiều loại cleanup. 



Đây là ba công cụ nền tảng để quản lý tài nguyên trong Python.

* * *

# Chuẩn bị cho buổi 10 – Async Context Manager

Buổi tiếp theo sẽ đưa chúng ta sang thế giới **bất đồng bộ (`asyncio`)**, nơi Context Manager có hai phương thức mới:

  * `__aenter__()`
  * `__aexit__()`



và cú pháp:
    
    
    async with ...

Bạn sẽ học cách quản lý:

  * `aiohttp.ClientSession`
  * `aiosqlite.Connection`
  * Semaphore bất đồng bộ 
  * Lock bất đồng bộ 
  * Connection pool 



Đây là kiến thức cần thiết nếu bạn muốn xây dựng các crawler, web service hoặc ứng dụng I/O hiệu năng cao bằng Python.

