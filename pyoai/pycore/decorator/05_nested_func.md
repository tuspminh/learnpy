# Decorator Deep Dive — Buổi 5

# Nested Function (Hàm lồng nhau) — Khung xương của Decorator

> **Mục tiêu buổi học**

Sau buổi này bạn sẽ hiểu:

  * Nested Function là gì. 
  * Tại sao Python hỗ trợ hàm lồng nhau. 
  * Khi nào nên dùng Nested Function. 
  * Nested Function khác Closure như thế nào. 
  * Các mẫu thiết kế (Pattern) sử dụng Nested Function. 
  * Vì sao mọi Decorator đều bắt đầu từ Nested Function. 



* * *

# Roadmap

Chúng ta đã học:

  * ✅ Buổi 1: Function là Object 
  * ✅ Buổi 2: First-Class Function 
  * ✅ Buổi 3: Closure 
  * ✅ Buổi 4: LEGB Scope 



Hôm nay:

> **Nested Function**

Buổi sau:

> **Decorator đầu tiên**

* * *

# 1\. Nested Function là gì?

Nested Function là:

> Một function được định nghĩa bên trong một function khác.

Ví dụ đơn giản nhất
    
    
    def outer():
    
        def inner():
            print("Hello")
    
        inner()
    
    outer()

Kết quả
    
    
    Hello

Cấu trúc
    
    
    outer
    
    │
    
    ├── inner

* * *

# 2\. Tại sao cần Nested Function?

Ví dụ không dùng Nested Function
    
    
    def validate_username(username):
        if len(username) < 3:
            raise ValueError("Username quá ngắn")
    
    
    def validate_password(password):
        if len(password) < 8:
            raise ValueError("Password quá ngắn")
    
    
    def create_user(username, password):
        validate_username(username)
        validate_password(password)
    
        print("User created")

Hai hàm validate chỉ dùng đúng một nơi.

Không cần public.

Ta có thể viết
    
    
    def create_user(username, password):
    
        def validate_username():
            if len(username) < 3:
                raise ValueError("Username quá ngắn")
    
        def validate_password():
            if len(password) < 8:
                raise ValueError("Password quá ngắn")
    
        validate_username()
        validate_password()
    
        print("User created")

Ưu điểm

  * Không làm bẩn namespace. 
  * Hàm helper không bị gọi từ nơi khác. 
  * Dễ đọc hơn. 



* * *

# 3\. Phạm vi của Nested Function
    
    
    def outer():
    
        def inner():
            print("Hello")
    
        inner()
    
    outer()

Nếu
    
    
    inner()

Python báo
    
    
    NameError

Vì
    
    
    inner

chỉ tồn tại bên trong
    
    
    outer

* * *

# 4\. Nested Function không phải Closure

Đây là điều rất nhiều người nhầm.

Ví dụ
    
    
    def outer():
    
        def inner():
            print("Hello")
    
        return inner

Đây là Nested Function.

Nhưng
    
    
    inner

không dùng biến của outer.

Cho nên
    
    
    f = outer()
    
    print(f.__closure__)

Kết quả
    
    
    None

Không phải Closure.

* * *

# 5\. Khi nào Nested Function trở thành Closure?

Ví dụ
    
    
    def outer():
    
        message = "Hello"
    
        def inner():
            print(message)
    
        return inner

Lúc này
    
    
    message

được dùng.

Cho nên
    
    
    Nested Function
    
    +
    
    Free Variable
    
    =
    
    Closure

Đây là công thức rất quan trọng.

* * *

# 6\. Nested Function để chia nhỏ bài toán

Ví dụ
    
    
    def process_file(path):
    
        def read():
            print(f"Reading {path}")
    
        def parse():
            print("Parsing")
    
        def save():
            print("Saving")
    
        read()
        parse()
        save()
    
    
    process_file("users.csv")

Kết quả
    
    
    Reading users.csv
    Parsing
    Saving

Toàn bộ helper đều được giấu trong `process_file()`.

* * *

# 7\. Factory Pattern

Nested Function thường dùng để tạo object mới.

Ví dụ
    
    
    def make_adder(n):
    
        def add(x):
            return x + n
    
        return add

Đây chính là Factory Function.
    
    
    make_adder
    
    ↓
    
    return add

* * *

# 8\. Chi tiết bộ nhớ

Ví dụ
    
    
    def outer():
    
        def inner():
            pass
    
        return inner

Mỗi lần gọi
    
    
    f1 = outer()
    
    f2 = outer()

Ta có
    
    
    f1
    
    ↓
    
    Function Object A
    
    
    f2
    
    ↓
    
    Function Object B

Kiểm tra
    
    
    print(f1 is f2)
    
    
    False

Hai function object khác nhau.

* * *

# 9\. Hàm lồng nhiều tầng

Python cho phép
    
    
    def level1():
    
        def level2():
    
            def level3():
                print("Hello")
    
            level3()
    
        level2()
    
    level1()
    
    
    level1
    
    ↓
    
    level2
    
    ↓
    
    level3

Framework lớn đôi khi có nhiều tầng như vậy.

* * *

# 10\. Nested Function làm Helper

Ví dụ
    
    
    def export_csv(rows):
    
        def write_header():
            print("id,name")
    
        def write_rows():
            for row in rows:
                print(f"{row['id']},{row['name']}")
    
        write_header()
        write_rows()

Sử dụng
    
    
    rows = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]
    
    export_csv(rows)

Kết quả
    
    
    id,name
    1,Alice
    2,Bob

* * *

# 11\. Nested Function để kiểm soát truy cập

Ví dụ
    
    
    def database():
    
        connection = "Connected"
    
        def execute(sql):
            print(connection)
            print(sql)
    
        return execute

Người dùng chỉ có
    
    
    db = database()

Không thể truy cập
    
    
    connection

Trực tiếp.

* * *

# 12\. Thực tế trong Flask

Sau này bạn sẽ thấy
    
    
    @app.route("/")
    def home():
        ...

Bên trong Flask thực chất có ý tưởng gần giống
    
    
    def route(url):
    
        def decorator(func):
    
            routes[url] = func
    
            return func
    
        return decorator

Có tới hai tầng Nested Function.

* * *

# 13\. Thực tế trong Retry

Ví dụ
    
    
    def retry(times):
    
        def decorator(func):
    
            def wrapper():
    
                for _ in range(times):
                    try:
                        return func()
                    except Exception:
                        pass
    
            return wrapper
    
        return decorator

Ta thấy
    
    
    retry
    
    ↓
    
    decorator
    
    ↓
    
    wrapper

Ba tầng hàm lồng nhau.

Đây là cấu trúc chuẩn của **Decorator Factory**.

* * *

# 14\. Ví dụ hoàn chỉnh — Mini Calculator
    
    
    def calculator():
    
        def add(a, b):
            return a + b
    
        def sub(a, b):
            return a - b
    
        def mul(a, b):
            return a * b
    
        def div(a, b):
            return a / b
    
        return {
            "+": add,
            "-": sub,
            "*": mul,
            "/": div,
        }
    
    
    calc = calculator()
    
    print(calc["+"](10, 5))
    print(calc["*"](10, 5))

Kết quả
    
    
    15
    50

Tất cả helper đều được đóng gói trong `calculator()`.

* * *

# 15\. Ví dụ hoàn chỉnh — Mini Command Dispatcher
    
    
    def create_dispatcher():
    
        commands = {}
    
        def register(name, func):
            commands[name] = func
    
        def dispatch(name, *args, **kwargs):
            if name not in commands:
                raise ValueError(f"Unknown command: {name}")
            return commands[name](*args, **kwargs)
    
        return register, dispatch
    
    
    register, dispatch = create_dispatcher()
    
    
    def greet(name):
        return f"Hello, {name}!"
    
    
    def square(x):
        return x * x
    
    
    register("greet", greet)
    register("square", square)
    
    print(dispatch("greet", "Alice"))
    print(dispatch("square", 8))

Kết quả
    
    
    Hello, Alice!
    64

Phân tích:

  * `commands` là dữ liệu nội bộ. 
  * `register()` và `dispatch()` là hai nested function cùng chia sẻ `commands`. 
  * Đây là một ví dụ điển hình về **encapsulation bằng closure** , rất giống cách các framework quản lý route, command hoặc event. 



* * *

# 16\. Ví dụ hoàn chỉnh — Mini Pipeline
    
    
    def build_pipeline():
    
        steps = []
    
        def add_step(func):
            steps.append(func)
    
        def run(data):
            result = data
            for step in steps:
                result = step(result)
            return result
    
        return add_step, run
    
    
    add_step, run = build_pipeline()
    
    
    def double(x):
        return x * 2
    
    
    def add_three(x):
        return x + 3
    
    
    def square(x):
        return x * x
    
    
    add_step(double)
    add_step(add_three)
    add_step(square)
    
    print(run(5))

Quá trình xử lý:
    
    
    5
    ↓
    
    double
    
    10
    ↓
    
    add_three
    
    13
    ↓
    
    square
    
    169

Kết quả
    
    
    169

Ý tưởng này được sử dụng trong:

  * Middleware của web framework. 
  * Data processing pipeline. 
  * ETL (Extract → Transform → Load). 
  * Chuỗi xử lý request/response. 



* * *

# 17\. Nested Function và Decorator

Một decorator tối giản có dạng:
    
    
    def decorator(func):
    
        def wrapper():
            print("Before")
            func()
            print("After")
    
        return wrapper

Phân tích:
    
    
    decorator
    │
    ├── wrapper
    │
    └── return wrapper

Nếu bỏ **Nested Function** , bạn sẽ **không thể tạo decorator theo cách chuẩn của Python**.

Nói cách khác:

> **Nested Function là khung xương.**

> **Closure là bộ nhớ.**

> **Decorator là ứng dụng của cả hai.**

* * *

# So sánh Nested Function và Closure

Nested Function| Closure  
---|---  
Chỉ cần hàm nằm trong hàm| Hàm lồng + sử dụng biến từ hàm cha  
Không nhất thiết lưu trạng thái| Có khả năng lưu trạng thái  
Có thể `__closure__` là `None`| `__closure__` chứa Cell Object  
Dùng để tổ chức mã| Dùng để duy trì dữ liệu giữa các lần gọi  
  
Mọi Closure đều là Nested Function, nhưng **không phải mọi Nested Function đều là Closure**.

* * *

# Best Practices

### Nên dùng Nested Function khi

  * Viết helper chỉ dùng trong một hàm. 
  * Muốn ẩn logic nội bộ. 
  * Tạo factory function. 
  * Viết callback. 
  * Chuẩn bị xây dựng decorator. 



### Không nên dùng khi

  * Hàm helper được tái sử dụng ở nhiều nơi. 
  * Hàm quá dài hoặc lồng quá nhiều tầng gây khó đọc. 
  * Logic nên được đóng gói thành class hoặc module riêng. 



* * *

# Tổng kết buổi 5

Bạn cần ghi nhớ:

  1. Nested Function là hàm được định nghĩa trong một hàm khác. 
  2. Nested Function giúp **đóng gói (encapsulation)** và tránh làm bẩn namespace. 
  3. Nested Function chỉ trở thành **Closure** khi sử dụng biến của hàm cha. 
  4. Các mẫu thiết kế như Factory, Dispatcher, Pipeline đều sử dụng Nested Function. 
  5. Decorator của Python luôn bắt đầu từ Nested Function. 



* * *

# Bài tập

## Bài 1

Viết `create_validator()` trả về hai nested function:

  * `validate_email(email)`
  * `validate_age(age)`



Hai hàm này được trả về dưới dạng một `dict`.

* * *

## Bài 2

Viết `build_pipeline()` hỗ trợ:
    
    
    add_step(...)
    remove_step(...)
    run(data)

Trong đó `steps` phải được ẩn hoàn toàn bên trong hàm ngoài.

* * *

## Bài 3

Viết một **Mini Event Bus** :
    
    
    register(event_name, listener)
    emit(event_name, data)

Yêu cầu:

  * Dùng nested function. 
  * Dữ liệu sự kiện được lưu kín bên trong hàm ngoài. 
  * Có thể đăng ký nhiều listener cho cùng một sự kiện. 



Đây là mô hình được sử dụng trong nhiều framework GUI (PySide6, Qt), web framework và hệ thống plugin.

* * *

## Chuẩn bị cho buổi 6

Từ buổi 6 trở đi, chúng ta sẽ bắt đầu viết **Decorator đầu tiên**. Bạn sẽ học cú pháp `@decorator`, hiểu chính xác Python biến đổi hàm như thế nào, tự xây dựng `wrapper`, và khám phá điều gì thực sự xảy ra khi Python gặp dòng:
    
    
    @my_decorator
    def hello():
        print("Hello")

Đây là bước chuyển từ nền tảng lý thuyết sang xây dựng decorator thực tế.

