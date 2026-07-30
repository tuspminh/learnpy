# Decorator Deep Dive — Buổi 13

# Method Decorator (Decorator cho Method)

> Đây là một trong những chủ đề quan trọng nhất khi học Decorator.
> 
> Rất nhiều lập trình viên biết viết decorator cho function nhưng lại gặp lỗi ngay khi áp dụng cho method trong class.

Ví dụ:
    
    
    class User:
    
        @logger
        def login(self):
            ...

Nếu không hiểu cơ chế hoạt động của **method** , bạn sẽ rất dễ gặp lỗi như:
    
    
    TypeError:
    missing 1 required positional argument: 'self'

Sau buổi này, bạn sẽ hiểu **vì sao`self` không phải từ khóa đặc biệt**, cơ chế **bound method** , và cách viết decorator đúng cho mọi loại method.

* * *

# Mục tiêu

Sau buổi học bạn sẽ hiểu:

  * Function và Method khác nhau thế nào 
  * Bound Method 
  * Unbound Function 
  * Decorator cho Instance Method 
  * Decorator cho Class Method 
  * Decorator cho Static Method 
  * Descriptor Protocol (mức cơ bản) 
  * Best Practices 



* * *

# 1\. Function bình thường

Ví dụ
    
    
    def hello(name):
        print(name)

Đây là function.

Gọi
    
    
    hello("Alice")

Python truyền đúng một tham số.

* * *

# 2\. Method là gì?

Ví dụ
    
    
    class User:
    
        def login(self):
            print("Login")

Nhiều người nghĩ
    
    
    self

là từ khóa.

Không phải.

`self` chỉ là **tham số đầu tiên**.

Bạn có thể viết
    
    
    class User:
    
        def login(this):
            print("Login")

hoặc
    
    
    class User:
    
        def login(me):
            print("Login")

Đều chạy được.

* * *

# 3\. Python làm gì?
    
    
    u = User()
    
    u.login()

Python thực chất làm
    
    
    User.login(u)

Đây là điều cực kỳ quan trọng.

Method chỉ là function được "gắn" thêm instance.

* * *

# 4\. Chứng minh
    
    
    class User:
    
        def login(self):
            print(self)
    
    
    u = User()
    
    u.login()

Tương đương
    
    
    User.login(u)

Kết quả giống hệt.

* * *

# 5\. Method là Bound Method

Kiểm tra
    
    
    print(User.login)

Ví dụ
    
    
    <function User.login>

Đây là function.

* * *

Kiểm tra
    
    
    u = User()
    
    print(u.login)

Ví dụ
    
    
    <bound method User.login>

Khác hoàn toàn.

* * *

# 6\. Decorator đầu tiên
    
    
    from functools import wraps
    
    def logger(func):
    
        @wraps(func)
        def wrapper(*args, **kwargs):
    
            print("Before")
    
            result = func(*args, **kwargs)
    
            print("After")
    
            return result
    
        return wrapper

Áp dụng
    
    
    class User:
    
        @logger
        def login(self):
            print("Login")

* * *

# 7\. Chạy
    
    
    u = User()
    
    u.login()

Kết quả
    
    
    Before
    Login
    After

Không cần làm gì đặc biệt.

Vì
    
    
    args

chính là
    
    
    (self,)

* * *

# 8\. Quan sát args
    
    
    from functools import wraps
    
    def logger(func):
    
        @wraps(func)
        def wrapper(*args, **kwargs):
    
            print(args)
    
            return func(*args, **kwargs)
    
        return wrapper
    
    
    class User:
    
        @logger
        def login(self):
    
            print("Login")

Chạy
    
    
    User().login()

Kết quả
    
    
    (<User object>,)
    Login

`args[0]`

chính là
    
    
    self

* * *

# 9\. Ví dụ với nhiều tham số
    
    
    class Calculator:
    
        @logger
        def add(self, a, b):
    
            return a + b

Gọi
    
    
    c = Calculator()
    
    print(c.add(2, 3))

Trong wrapper
    
    
    args

sẽ là
    
    
    (
        self,
        2,
        3
    )

* * *

# 10\. Truy cập self

Decorator có thể lấy instance.
    
    
    from functools import wraps
    
    def logger(func):
    
        @wraps(func)
        def wrapper(*args, **kwargs):
    
            self = args[0]
    
            print(
                self.__class__.__name__
            )
    
            return func(*args, **kwargs)
    
        return wrapper

Ví dụ
    
    
    class User:
    
        @logger
        def login(self):
            print("Login")

Kết quả
    
    
    User
    Login

* * *

# 11\. Ví dụ kiểm tra quyền
    
    
    from functools import wraps
    
    def admin_only(func):
    
        @wraps(func)
        def wrapper(*args, **kwargs):
    
            self = args[0]
    
            if not self.is_admin:
                raise PermissionError
    
            return func(*args, **kwargs)
    
        return wrapper

Sử dụng
    
    
    class User:
    
        def __init__(self, admin):
    
            self.is_admin = admin
    
        @admin_only
        def delete(self):
    
            print("Deleted")

* * *

# 12\. Ví dụ Logging Object
    
    
    from functools import wraps
    
    def logger(func):
    
        @wraps(func)
        def wrapper(*args, **kwargs):
    
            self = args[0]
    
            print(
                "Object:",
                self
            )
    
            print(
                "Method:",
                func.__name__
            )
    
            return func(*args, **kwargs)
    
        return wrapper

* * *

# 13\. Class Method

Ôn lại
    
    
    class User:
    
        @classmethod
        def create(cls):
    
            print(cls)

Gọi
    
    
    User.create()

Python thực chất
    
    
    User.create.__func__(User)

hoặc có thể hình dung đơn giản là
    
    
    create(User)

Tham số đầu tiên là
    
    
    cls

* * *

# 14\. Decorator + classmethod

Đúng
    
    
    from functools import wraps
    
    def logger(func):
    
        @wraps(func)
        def wrapper(*args, **kwargs):
    
            print("Before")
    
            return func(*args, **kwargs)
    
        return wrapper
    
    
    class User:
    
        @classmethod
        @logger
        def create(cls):
    
            print(cls)

Python dịch
    
    
    create = classmethod(
        logger(create)
    )

* * *

# 15\. Đổi thứ tự

Sai
    
    
    class User:
    
        @logger
        @classmethod
        def create(cls):
            ...

Python dịch
    
    
    create = logger(
        classmethod(create)
    )

Lúc này
    
    
    func

không còn là function.

Nó là
    
    
    classmethod object

Khi wrapper gọi:
    
    
    func(*args)

sẽ gặp lỗi:
    
    
    TypeError:
    'classmethod' object is not callable

* * *

# 16\. Static Method
    
    
    class Math:
    
        @staticmethod
        def add(a, b):
    
            return a + b

Không có
    
    
    self

Không có
    
    
    cls

* * *

# 17\. Decorator + staticmethod

Đúng
    
    
    class Math:
    
        @staticmethod
        @logger
        def add(a, b):
    
            return a + b

Python
    
    
    add = staticmethod(
        logger(add)
    )

* * *

Sai
    
    
    @logger
    @staticmethod

Lý do giống
    
    
    classmethod

* * *

# 18\. Ví dụ hoàn chỉnh
    
    
    from functools import wraps
    
    
    def timer(func):
    
        @wraps(func)
        def wrapper(*args, **kwargs):
    
            print(
                "Calling",
                func.__name__
            )
    
            result = func(*args, **kwargs)
    
            print(
                "Finished"
            )
    
            return result
    
        return wrapper
    
    
    class Calculator:
    
        @timer
        def add(self, a, b):
    
            return a + b
    
    
    calc = Calculator()
    
    print(calc.add(4, 6))

Kết quả
    
    
    Calling add
    Finished
    10

* * *

# 19\. Ví dụ Class Method
    
    
    from functools import wraps
    
    
    def logger(func):
    
        @wraps(func)
        def wrapper(*args, **kwargs):
    
            print(args[0])
    
            return func(*args, **kwargs)
    
        return wrapper
    
    
    class User:
    
        @classmethod
        @logger
        def build(cls):
    
            return cls()
    
    
    User.build()

Kết quả
    
    
    <class '__main__.User'>

Ở đây:
    
    
    args[0]

chính là
    
    
    cls

* * *

# 20\. Ví dụ Static Method
    
    
    from functools import wraps
    
    
    def logger(func):
    
        @wraps(func)
        def wrapper(*args, **kwargs):
    
            print(args)
    
            return func(*args, **kwargs)
    
        return wrapper
    
    
    class Math:
    
        @staticmethod
        @logger
        def multiply(a, b):
    
            return a * b
    
    
    print(Math.multiply(3, 4))

Kết quả
    
    
    (3, 4)
    12

Không có
    
    
    self

Không có
    
    
    cls

* * *

# 21\. Một decorator dùng cho cả ba loại method

Đây là mẫu phổ biến trong framework:
    
    
    from functools import wraps
    
    def trace(func):
    
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"Calling {func.__qualname__}")
            print(f"args={args}")
            print(f"kwargs={kwargs}")
    
            result = func(*args, **kwargs)
    
            print(f"Returned {result!r}")
            return result
    
        return wrapper

Áp dụng được cho:

  * Function 
  * Instance method 
  * Class method (đặt dưới `@classmethod`) 
  * Static method (đặt dưới `@staticmethod`) 



Vì nó không giả định `args[0]` luôn là `self`.

* * *

# 22\. Descriptor Protocol (mức cơ bản)

Tại sao:
    
    
    u.login

lại tự động nhận
    
    
    self

Đó là nhờ **Descriptor Protocol**.

Function trong class có phương thức đặc biệt:
    
    
    __get__()

Khi bạn truy cập:
    
    
    u.login

Python thực hiện gần giống:
    
    
    User.login.__get__(u, User)

Kết quả trả về là **bound method**.

Ta sẽ học sâu về Descriptor trong một khóa học riêng, nhưng bạn nên nhớ:
    
    
    Function trong class
    
    ↓
    
    Descriptor
    
    ↓
    
    Bound Method
    
    ↓
    
    self được gắn tự động

* * *

# Best Practices

✅ Luôn viết decorator theo mẫu:
    
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

✅ Không giả định `args[0]` luôn là `self`, trừ khi decorator chỉ dành cho instance method.

✅ Với `@classmethod` và `@staticmethod`, **đặt decorator tự viết ở dưới** , tức là gần hàm hơn:
    
    
    @classmethod
    @logger
    def build(cls):
        ...

và
    
    
    @staticmethod
    @logger
    def add(a, b):
        ...

* * *

# Tổng kết buổi 13

Bạn cần ghi nhớ:

  1. Method thực chất là function được gắn với object. 
  2. `u.login()` tương đương `User.login(u)`. 
  3. Trong instance method, `args[0]` là `self`. 
  4. Trong class method, `args[0]` là `cls`. 
  5. Static method không có `self` và `cls`. 
  6. Với `@classmethod` và `@staticmethod`, decorator tự viết nên đặt **gần hàm hơn** để nhận function gốc thay vì object descriptor. 
  7. Cơ chế tự động gắn `self` được thực hiện thông qua **Descriptor Protocol**. 



* * *

# Bài tập

## Bài 1

Viết decorator `@count_calls` áp dụng cho instance method:
    
    
    class User:
    
        @count_calls
        def login(self):
            print("Login")

Yêu cầu:

  * Đếm số lần gọi của từng instance. 
  * Gợi ý: lưu bộ đếm trong `self`. 



* * *

## Bài 2

Viết decorator `@require_login`:
    
    
    class User:
    
        def __init__(self):
            self.logged_in = False
    
        @require_login
        def delete_account(self):
            print("Deleted")

Nếu `logged_in` là `False`, ném `PermissionError`.

* * *

## Bài 3

Tạo một lớp có đủ ba loại method:
    
    
    class Demo:
    
        @trace
        def instance(self):
            ...
    
        @classmethod
        @trace
        def cls_method(cls):
            ...
    
        @staticmethod
        @trace
        def static_method():
            ...

In `args` trong mỗi trường hợp và giải thích vì sao chúng khác nhau.

* * *

# Chuẩn bị cho buổi 14

Ở **buổi 14** , chúng ta sẽ học **Class Decorator** (decorator áp dụng cho **chính class** , không phải method). Bạn sẽ thấy cách các framework như `dataclasses`, ORM và nhiều thư viện khác dùng class decorator để:

  * Thêm thuộc tính vào class. 
  * Tự động đăng ký class vào registry. 
  * Sửa đổi hoặc thay thế class. 
  * Kết hợp với metaclass và descriptor. 



Đây là một chủ đề rất mạnh và là nền tảng để hiểu nhiều thư viện Python hiện đại.

