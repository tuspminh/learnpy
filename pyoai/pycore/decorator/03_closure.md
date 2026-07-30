# Decorator Deep Dive — Buổi 3

# Closure — Trái tim của Decorator

> **Mục tiêu buổi học**

Sau buổi này, bạn sẽ hiểu:

  * Closure là gì. 
  * Biến tự do (_free variable_) là gì. 
  * Tại sao biến của hàm cha vẫn tồn tại sau khi hàm cha kết thúc. 
  * `__closure__`, `co_freevars`, `cell_contents`. 
  * Closure hoạt động như thế nào trong bộ nhớ. 
  * Vì sao hầu hết decorator đều dựa trên Closure. 



* * *

# 1\. Ôn lại buổi trước

Buổi trước chúng ta đã học:
    
    
    def create():
        def hello():
            print("Hello")
    
        return hello
    
    
    f = create()
    
    f()

Kết quả
    
    
    Hello

Câu hỏi là:

> Hàm `hello()` đã được tạo trong `create()`. Vậy tại sao sau khi `create()` kết thúc, `hello()` vẫn còn tồn tại?

Đó chính là **Closure**.

* * *

# 2\. Không phải Closure

Ví dụ:
    
    
    def outer():
        x = 10
    
        def inner():
            print("Hello")
    
        return inner

Ở đây:
    
    
    inner

không sử dụng biến `x`.

Do đó **không tạo Closure**.

Kiểm tra:
    
    
    f = outer()
    
    print(f.__closure__)

Kết quả
    
    
    None

Không có Closure.

* * *

# 3\. Closure đầu tiên

Ví dụ
    
    
    def outer():
        x = 10
    
        def inner():
            print(x)
    
        return inner

Gọi
    
    
    f = outer()
    
    f()

Kết quả
    
    
    10

Lúc này `outer()` đã kết thúc từ lâu.

Nhưng `x` vẫn còn.

Đây chính là Closure.

* * *

# 4\. Bộ nhớ hoạt động ra sao?

Khi gọi
    
    
    outer()

Python tạo
    
    
    Stack
    
    outer()
    
    x = 10

Thông thường

sau khi kết thúc
    
    
    outer()
    
    ↓
    
    Stack bị hủy

Nếu không có Closure

thì
    
    
    x

cũng biến mất.

Nhưng ở đây
    
    
    inner()

đang sử dụng
    
    
    x

Python phát hiện điều đó.

Nó chuyển
    
    
    x

vào một vùng nhớ đặc biệt gọi là
    
    
    Cell Object

Sơ đồ:
    
    
    inner
    
    ↓
    
    Closure
    
    ↓
    
    Cell
    
    ↓
    
    10

Cho nên
    
    
    outer()

đã kết thúc

nhưng
    
    
    10

vẫn còn.

* * *

# 5\. Quan sát **closure**
    
    
    def outer():
        x = 100
    
        def inner():
            print(x)
    
        return inner
    
    
    f = outer()
    
    print(f.__closure__)

Ví dụ
    
    
    (<cell at 0x000001A4..., int object at ...>,)

Có một Cell.

* * *

Lấy giá trị
    
    
    cell = f.__closure__[0]
    
    print(cell.cell_contents)

Kết quả
    
    
    100

Cell chính là nơi Python lưu biến.

* * *

# 6\. Có nhiều biến
    
    
    def outer():
        a = 1
        b = 2
    
        def inner():
            print(a, b)
    
        return inner
    
    
    f = outer()
    
    print(f.__closure__)

Có hai Cell.
    
    
    for cell in f.__closure__:
        print(cell.cell_contents)

Kết quả
    
    
    1
    2

* * *

# 7\. Free Variable

Ví dụ
    
    
    def outer():
        x = 5
    
        def inner():
            return x
    
        return inner

Trong `inner`
    
    
    x

không được tạo.

Nó đến từ
    
    
    outer

Cho nên
    
    
    x

được gọi là

> **Free Variable**

Kiểm tra
    
    
    print(f.__code__.co_freevars)

Kết quả
    
    
    ('x',)

* * *

# 8\. Local Variable
    
    
    def outer():
        x = 5
    
        def inner():
            y = 10
            return x + y
    
        return inner

Ở đây
    
    
    y

không phải Free Variable.

Nó là
    
    
    Local Variable

Kiểm tra
    
    
    print(f.__code__.co_varnames)
    
    
    ('y',)

* * *

# 9\. Closure ghi nhớ giá trị

Ví dụ
    
    
    def make_multiplier(n):
    
        def multiply(x):
            return x * n
    
        return multiply

Tạo
    
    
    double = make_multiplier(2)
    
    triple = make_multiplier(3)

Gọi
    
    
    print(double(10))
    print(triple(10))

Kết quả
    
    
    20
    30

Tại sao?

Vì mỗi Closure có Cell riêng.
    
    
    double
    
    ↓
    
    Cell
    
    ↓
    
    2
    
    
    triple
    
    ↓
    
    Cell
    
    ↓
    
    3

* * *

# 10\. Hai Closure độc lập
    
    
    def counter():
    
        value = 0
    
        def show():
            print(value)
    
        return show
    
    
    a = counter()
    b = counter()

Hai object khác nhau.
    
    
    a
    
    ↓
    
    Cell
    
    ↓
    
    0
    
    
    b
    
    ↓
    
    Cell
    
    ↓
    
    0

Không dùng chung.

* * *

# 11\. Thay đổi biến Closure bằng nonlocal

Ví dụ
    
    
    def counter():
    
        value = 0
    
        def increment():
            nonlocal value
            value += 1
            print(value)
    
        return increment

Gọi
    
    
    c = counter()
    
    c()
    c()
    c()

Kết quả
    
    
    1
    2
    3

Không có `nonlocal`
    
    
    value += 1

sẽ báo lỗi
    
    
    UnboundLocalError

Vì Python nghĩ bạn đang tạo một biến cục bộ mới.

* * *

# 12\. Ví dụ hoàn chỉnh — Counter
    
    
    def make_counter():
    
        count = 0
    
        def increment():
            nonlocal count
    
            count += 1
            return count
    
        return increment
    
    
    counter1 = make_counter()
    
    print(counter1())
    print(counter1())
    print(counter1())
    
    counter2 = make_counter()
    
    print(counter2())
    print(counter2())

Kết quả
    
    
    1
    2
    3
    1
    2

Mỗi Counter có trạng thái riêng.

* * *

# 13\. Ví dụ hoàn chỉnh — Logger
    
    
    def logger(prefix):
    
        def log(message):
            print(f"[{prefix}] {message}")
    
        return log
    
    
    info = logger("INFO")
    error = logger("ERROR")
    
    info("Application started")
    info("Connected to database")
    
    error("Database connection failed")
    error("Timeout")

Kết quả
    
    
    [INFO] Application started
    [INFO] Connected to database
    [ERROR] Database connection failed
    [ERROR] Timeout

`prefix` được Closure ghi nhớ.

* * *

# 14\. Ví dụ hoàn chỉnh — Discount Calculator
    
    
    def create_discount(percent):
    
        def calculate(price):
            return price * (100 - percent) / 100
    
        return calculate
    
    
    discount10 = create_discount(10)
    discount20 = create_discount(20)
    
    print(discount10(500))
    print(discount20(500))

Kết quả
    
    
    450.0
    400.0

Mỗi hàm đều nhớ phần trăm giảm giá của mình.

* * *

# 15\. Closure chính là nền tảng của Decorator

Một decorator đơn giản thực chất có dạng:
    
    
    def decorator(func):
    
        def wrapper(*args, **kwargs):
            print("Before")
    
            result = func(*args, **kwargs)
    
            print("After")
    
            return result
    
        return wrapper

Ở đây
    
    
    wrapper

là Closure.

Nó ghi nhớ
    
    
    func

để sau này vẫn có thể gọi:
    
    
    func(*args, **kwargs)

mặc dù
    
    
    decorator()

đã kết thúc từ lâu.

Đây là lý do Decorator hoạt động được.

* * *

# 16\. So sánh Closure và Class

Closure:
    
    
    def counter():
    
        count = 0
    
        def increment():
            nonlocal count
            count += 1
            return count
    
        return increment

Class:
    
    
    class Counter:
    
        def __init__(self):
            self.count = 0
    
        def increment(self):
            self.count += 1
            return self.count

Hai cách đều lưu trạng thái.

Khác biệt:

Closure| Class  
---|---  
Trạng thái nằm trong Cell| Trạng thái nằm trong thuộc tính (`self`)  
Thường gọn, phù hợp hàm nhỏ| Dễ mở rộng, nhiều hành vi  
Không lộ trực tiếp dữ liệu| Có thể truy cập qua `self`  
  
* * *

# 17\. Quan sát sâu hơn với `inspect`
    
    
    import inspect
    
    def outer():
        x = 42
    
        def inner():
            return x
    
        return inner
    
    
    f = outer()
    
    print(inspect.getclosurevars(f))

Kết quả (ví dụ):
    
    
    ClosureVars(
        nonlocals={'x': 42},
        globals={},
        builtins={...},
        unbound=set()
    )

Đây là cách rất hữu ích khi debug các decorator hoặc callback phức tạp.

* * *

# Tổng kết buổi 3

Bạn cần nắm chắc các khái niệm sau:

  1. **Closure** xuất hiện khi một hàm bên trong sử dụng biến của hàm bên ngoài. 
  2. Python lưu các biến đó trong **Cell Object** thay vì để chúng mất đi khi hàm cha kết thúc. 
  3. `__closure__` chứa các Cell, `cell_contents` cho biết giá trị trong từng Cell. 
  4. `co_freevars` liệt kê các **Free Variable** mà hàm đang "đóng gói". 
  5. `nonlocal` cho phép thay đổi giá trị của biến nằm trong Closure. 
  6. Mỗi lần gọi hàm tạo Closure sẽ sinh ra **một môi trường độc lập** , vì vậy mỗi Closure có trạng thái riêng. 
  7. **Decorator thực chất là một Closure** : hàm `wrapper` ghi nhớ `func` thông qua cơ chế Closure. 



* * *

# Bài tập

## Bài 1

Viết hàm:
    
    
    def make_power(n):
        ...

Trả về một hàm tính:
    
    
    x^n

Ví dụ:
    
    
    square = make_power(2)
    cube = make_power(3)
    
    print(square(5))  # 25
    print(cube(5))    # 125

* * *

## Bài 2

Viết `make_accumulator()`:
    
    
    acc = make_accumulator()
    
    print(acc(5))
    print(acc(10))
    print(acc(-3))

Kết quả:
    
    
    5
    15
    12

Gợi ý: sử dụng `nonlocal`.

* * *

## Bài 3

Viết `make_formatter(prefix, suffix)`:
    
    
    fmt = make_formatter("[", "]")
    
    print(fmt("Python"))

Kết quả:
    
    
    [Python]

Tạo thêm nhiều formatter khác nhau như:

  * `<Python>`
  * `(Python)`
  * `**Python**`



để thấy mỗi Closure ghi nhớ cấu hình riêng của nó.

* * *

Ở **buổi 4** , chúng ta sẽ học **LEGB Scope và Name Resolution**. Đây là mảnh ghép cuối cùng trước khi xây dựng decorator hoàn chỉnh, giúp bạn hiểu chính xác Python tìm kiếm biến theo thứ tự nào, vì sao `global` và `nonlocal` hoạt động, và cách tránh những lỗi phạm vi biến rất phổ biến khi viết decorator và callback phức tạp.

