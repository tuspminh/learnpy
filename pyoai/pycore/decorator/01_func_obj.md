# Buổi 1 — Function là Object

Muốn hiểu decorator thì phải hiểu một sự thật:

> Trong Python, **function là object**.

Nó không phải chỉ là "đoạn code".

Ví dụ:
    
    
    def hello():
        print("Hello")

Ta tưởng tượng:
    
    
    RAM
    
    +------------------+
    | object Function  |
    | code             |
    | globals          |
    | defaults         |
    | closure          |
    +------------------+
    
    ^
    
    |
    
    hello

Biến `hello` chỉ là một **reference**.

Nó giống hệt:
    
    
    a = 10

`a` trỏ tới object int.

Còn
    
    
    hello

trỏ tới object function.

* * *

# Kiểm tra
    
    
    def hello():
        print("Hello")

In ra:
    
    
    print(hello)

Kết quả
    
    
    <function hello at 0x10a4f1120>

Đây không phải chuỗi.

Nó là object.

* * *

Kiểm tra kiểu
    
    
    print(type(hello))
    
    
    <class 'function'>

Function cũng có type.

* * *

# Có id()
    
    
    print(id(hello))

Ví dụ
    
    
    4361920000

Nghĩa là object tồn tại trong RAM.

* * *

# Có thể gán sang biến khác
    
    
    def hello():
        print("Hello")
    
    
    f = hello

Bây giờ
    
    
    hello
    
    ↓
    
    Function Object
    
    ↑
    
    f

Có hai biến cùng trỏ.

* * *

Thử:
    
    
    f()
    
    
    Hello

Không khác gì
    
    
    hello()

* * *

# Không có dấu ()

Nhiều người mới học nhầm.

Sai:
    
    
    f = hello()

Lúc này
    
    
    hello()

được thực thi.

Nếu
    
    
    def hello():
        print("Hello")

thì
    
    
    Hello

được in ra.

Sau đó
    
    
    f = None

vì hàm không return.

* * *

Đúng phải là
    
    
    f = hello

Không có dấu ngoặc.

* * *

# Hàm có thể nằm trong List
    
    
    def a():
        print("A")
    
    def b():
        print("B")
    
    funcs = [a, b]

Duyệt
    
    
    for func in funcs:
        func()

Kết quả
    
    
    A
    B

* * *

# Hàm nằm trong Dictionary
    
    
    def add(x, y):
        return x + y
    
    def sub(x, y):
        return x - y
    
    operations = {
        "+": add,
        "-": sub,
    }

Gọi
    
    
    print(operations["+"](5, 3))
    
    
    8

Hoặc
    
    
    op = operations["-"]
    
    print(op(5, 3))
    
    
    2

Đây là kỹ thuật thay thế nhiều câu lệnh `if...elif` hoặc `match`.

* * *

# Hàm là tham số
    
    
    def hello():
        print("Hello")
    
    
    def execute(func):
        func()

Gọi
    
    
    execute(hello)

Kết quả
    
    
    Hello

Lưu ý
    
    
    execute(hello)

không phải
    
    
    execute(hello())

* * *

# Hàm trả về Function

Ví dụ
    
    
    def create():
        def hello():
            print("Hello")
    
        return hello
    
    
    create
    
    ↓
    
    Function
    
    ↓
    
    return hello

Gọi
    
    
    f = create()
    
    f()
    
    
    Hello

Đây chính là nền móng của decorator.

* * *

# Function có Attribute

Nhiều người không biết.
    
    
    def hello():
        pass
    
    
    print(hello.__name__)
    
    
    hello

* * *
    
    
    print(hello.__module__)
    
    
    __main__

* * *
    
    
    print(hello.__doc__)

Nếu
    
    
    def hello():
        """Greeting"""

thì
    
    
    Greeting

* * *

Có thể tự thêm
    
    
    hello.version = "1.0"
    
    print(hello.version)
    
    
    1.0

Vì function là object.

* * *

# Function truyền qua nhiều tầng
    
    
    def hello():
        print("Hello")
    
    
    def layer1(func):
        layer2(func)
    
    def layer2(func):
        layer3(func)
    
    def layer3(func):
        func()
    
    
    layer1
    
    ↓
    
    layer2
    
    ↓
    
    layer3
    
    ↓
    
    hello()

Gọi
    
    
    layer1(hello)
    
    
    Hello

Decorator thực chất cũng chỉ truyền function qua nhiều lớp như vậy.

* * *

# Ví dụ hoàn chỉnh — Bộ thực thi tác vụ
    
    
    def backup():
        print("Backup database...")
    
    
    def clean():
        print("Cleaning temp files...")
    
    
    def report():
        print("Generating report...")
    
    
    def execute(tasks):
        for task in tasks:
            print(f"Running {task.__name__}")
            task()
            print("-" * 30)
    
    
    tasks = [
        backup,
        clean,
        report,
    ]
    
    execute(tasks)

Kết quả:
    
    
    Running backup
    Backup database...
    ------------------------------
    Running clean
    Cleaning temp files...
    ------------------------------
    Running report
    Generating report...
    ------------------------------

Qua ví dụ này, bạn đã thấy:

  * Hàm được lưu trong danh sách. 
  * Hàm được truyền như dữ liệu. 
  * Có thể đọc thuộc tính `__name__`. 
  * Có thể gọi động bằng `task()`. 



Đây là nền tảng của rất nhiều framework Python.

* * *

# Ví dụ hoàn chỉnh — Bộ định tuyến (Router) đơn giản
    
    
    def home():
        print("Home Page")
    
    
    def about():
        print("About Page")
    
    
    def contact():
        print("Contact Page")
    
    
    routes = {
        "/": home,
        "/about": about,
        "/contact": contact,
    }
    
    
    def handle_request(path):
        handler = routes.get(path)
    
        if handler:
            print(f"Handling {path}")
            handler()
        else:
            print("404 Not Found")
    
    
    handle_request("/")
    handle_request("/about")
    handle_request("/contact")
    handle_request("/missing")

Kết quả:
    
    
    Handling /
    Home Page
    Handling /about
    About Page
    Handling /contact
    Contact Page
    404 Not Found

Đây chính là ý tưởng cốt lõi mà các framework web sử dụng. Sau này, decorator như `@app.route("/")` sẽ tự động đăng ký hàm vào bảng `routes` thay vì bạn phải thêm thủ công.

* * *

# Tổng kết buổi 1

Bạn cần nắm vững các ý sau trước khi học decorator:

  1. Function là một object. 
  2. Biến chỉ giữ tham chiếu đến object function. 
  3. Có thể gán hàm cho biến khác. 
  4. Có thể lưu hàm trong list, tuple, dict. 
  5. Có thể truyền hàm làm tham số. 
  6. Có thể trả về một hàm từ hàm khác. 
  7. Function có thuộc tính (`__name__`, `__doc__`, `__module__`, …) và có thể gắn thêm thuộc tính tùy ý. 
  8. Decorator chỉ hoạt động được vì Python xem hàm như dữ liệu (first-class object). 



Ở **buổi 2** , chúng ta sẽ đi sâu vào khái niệm **First-Class Function** và phân biệt rõ **function object** , **function call** , **callable** , cùng các kỹ thuật truyền và trả về hàm trong các tình huống thực tế. Đây là bước chuyển tiếp quan trọng trước khi học **Closure** và bắt đầu tự xây dựng decorator.

