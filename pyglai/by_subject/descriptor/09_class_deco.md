Class Decorator (bộ trang trí lớp) trong Python là một hàm (hoặc một lớp) nhận đầu vào là một class, thực hiện chỉnh sửa hoặc bổ sung tính năng cho class đó, rồi trả về class đã thay đổi (hoặc một class hoàn toàn mới). [1, 2] 
Nó hoạt động tương tự như function decorator nhưng áp dụng ở cấp độ lớp. [3, 4] 
------------------------------
## 1. Cú pháp và Cách hoạt động cơ bản
Ký hiệu @ đặt phía trên class thực chất là một cách viết ngắn gọn (syntactic sugar) cho việc truyền class vào một hàm. [5, 6] 

# 1. Định nghĩa một decorator bằng hàm thông thườngdef them_mo_ta(cls):
    # Thêm một thuộc tính mới vào class nhận được
    cls.mo_ta = "Đây là một class đã được trang trí."
    return cls
# 2. Sử dụng decorator
@them_mo_taclass MayTinh:
    pass
# Cách hoạt động ngầm tương đương với: MayTinh = them_mo_ta(MayTinh)

print(MayTinh.mo_ta)  # Kết quả: Đây là một class đã được trang trí.

------------------------------
## 2. Các bài toán thực tế nên dùng Class Decorator
Class Decorator cực kỳ hữu dụng khi bạn muốn tái sử dụng code để thêm cùng một nhóm tính năng vào nhiều class độc lập mà không muốn dùng kế thừa. [7, 8, 9] 
## Bài toán 1: Tự động thêm log (ghi nhật ký) cho tất cả các hàm trong class
Nếu bạn muốn theo dõi xem người dùng đang gọi những hàm nào trong class, thay vì vào từng hàm viết lệnh print, bạn có thể bọc toàn bộ class bằng một decorator.

import functools
def log_all_methods(cls):
    """Decorator tự động log thời điểm gọi mọi hàm của class."""
    for name, attr in cls.__dict__.items():
        # Kiểm tra nếu thuộc tính đó là một hàm (callable) do người dùng viết
        if callable(attr) and not name.startswith("__"):
            # Bọc hàm đó bằng một hàm log
            def make_wrapper(func):
                @functools.wraps(func)
                def wrapper(*args, **kwargs):
                    print(f"[LOG] Đang chạy hàm: '{func.__name__}'")
                    return func(*args, **kwargs)
                return wrapper
            
            # Ghi đè hàm cũ bằng hàm đã bọc log
            setattr(cls, name, make_wrapper(attr))
    return cls

@log_all_methodsclass DichVu:
    def gui_email(self):
        return "Đã gửi email"
        
    def thanh_toan(self):
        return "Đã thanh toán"
# Chạy thử nghiệmdv = DichVu()
dv.gui_email()   # In ra: [LOG] Đang chạy hàm: 'gui_email'
dv.thanh_toan()  # In ra: [LOG] Đang chạy hàm: 'thanh_toan'

## Bài toán 2: Chuyển class thành dạng Singleton (Chỉ cho phép tạo duy nhất 1 instance)
Nếu bạn có một class quản lý kết nối Database hoặc cấu hình hệ thống và muốn đảm bảo dù có gọi hàm khởi tạo bao nhiêu lần thì vẫn chỉ có duy nhất một đối tượng được dùng chung trong toàn bộ ứng dụng.

def singleton(cls):
    instances = {}
    
    @functools.wraps(cls)
    def wrapper(*args, **kwargs):
        # Nếu class này chưa từng được tạo instance, tiến hành tạo và lưu lại
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return wrapper

@singletonclass DatabaseConnection:
    def __init__(self):
        print("Đang kết nối tới Database... (Chỉ chạy 1 lần duy nhất)")
# Thử tạo nhiều đối tượngdb1 = DatabaseConnection()db2 = DatabaseConnection()

print(db1 is db2)  # Kết quả: True (Cả hai biến đều trỏ chung về 1 đối tượng)

------------------------------
## 3. Class Decorator có truyền tham số
Đôi khi bạn muốn cấu hình cho decorator bằng cách truyền tham số vào cho nó (ví dụ: đặt tiền tố cho log, thêm các thuộc tính với giá trị động). Để làm được việc này, bạn cần viết 3 tầng hàm lồng nhau: [10] 

def add_metadata(author, version):
    """Decorator nhận tham số bên ngoài"""
    def decorator(cls):
        # Tác động lên class nhận được
        cls.__author__ = author
        cls.__version__ = version
        return cls
    return decorator

@add_metadata(author="Nguyen Van A", version="1.0.0")class WebApp:
    pass

print(WebApp.__author__)   # Kết quả: Nguyen Van A
print(WebApp.__version__)  # Kết quả: 1.0.0

------------------------------
## 4. Công cụ có sẵn trong Python: @dataclass
Một ví dụ kinh điển và phổ biến nhất của Class Decorator chính là @dataclass (có sẵn từ Python 3.7). Nó tự động quét các biến bạn khai báo để viết hộ bạn các hàm boilerplate nhàm chán như __init__, __repr__, __eq__. [11, 12, 13, 14, 15] 

from dataclasses import dataclass

@dataclassclass Book:
    title: str
    price: float
# @dataclass đã tự viết hàm __init__ ngầm cho bạn:b = Book("Lập trình Python", 150000)
print(b)  # Tự động có hàm __repr__ đẹp đẽ: Book(title='Lập trình Python', price=150000)

------------------------------
Bạn đã làm quen với cả 3 công cụ thay đổi hành vi class: Descriptor (quản lý thuộc tính), Metaclass (can thiệp lúc xây dựng class), và Class Decorator (bọc và chỉnh sửa class sau khi hoàn thiện). [16, 17, 18] 
Nếu bạn muốn, chúng ta có thể:

* Tìm hiểu sâu về cơ chế MRO (Method Resolution Order) của Python để biết cách hệ thống tìm kiếm hàm khi xảy ra đa kế thừa phức tạp.
* Hoặc làm một bài tập tổng hợp áp dụng cả 3 công cụ trên vào một chương trình cụ thể để bạn phân biệt rõ ràng. [19, 20] 

Bạn muốn tìm hiểu về MRO hay làm bài tập tổng hợp?

[1] [https://www.pythonmorsels.com](https://www.pythonmorsels.com/common-decorators-included-with-python/)
[2] [https://blog.stackademic.com](https://blog.stackademic.com/understanding-python-decorators-a-guide-to-using-class-decorators-7327c9b42916)
[3] [https://grahamdumpleton.me](https://grahamdumpleton.me/posts/2026/04/free-python-decorator-workshops/)
[4] [https://www.conf42.com](https://www.conf42.com/Python_2022_Andrew_Knight_how_decorators_function)
[5] [https://www.scaler.com](https://www.scaler.com/topics/python/python-decorators/)
[6] [https://www.theserverside.com](https://www.theserverside.com/tutorial/Understanding-the-TypeScript-method-decorator)
[7] [https://medium.com](https://medium.com/@nikitinsn6/advanced-typescript-techniques-generics-decorators-and-more-25a2d10d8029)
[8] [https://www.reddit.com](https://www.reddit.com/r/learnpython/comments/1dqe91i/im_frustrated_because_i_cant_understand_the_logic/)
[9] [https://medium.com](https://medium.com/@vedantdbhamare/demystifying-the-decorator-design-pattern-in-typescript-with-coffee-brewing-c9d97a508b4e)
[10] [https://blog.devgenius.io](https://blog.devgenius.io/design-pattern-adding-chocolate-and-whip-cream-to-our-coffee-with-the-decorator-pattern-899e61e45990)
[11] [https://realpython.com](https://realpython.com/primer-on-python-decorators/)
[12] [https://levelup.gitconnected.com](https://levelup.gitconnected.com/built-in-decorators-in-python-an-overview-of-the-commonly-used-decorators-provided-by-the-python-4e691415449f)
[13] [https://medium.com](https://medium.com/ai-ml-interview-playbook/top-10-python-decorators-to-make-you-a-10x-developer-4581ed6a094f)
[14] [https://www.kdnuggets.com](https://www.kdnuggets.com/how-to-use-pythons-dataclass-to-write-less-code)
[15] [https://thetechbuffet.substack.com](https://thetechbuffet.substack.com/p/python-decorators)
[16] [https://bas.codes](https://bas.codes/posts/python-decorators/)
[17] [https://dev.to](https://dev.to/theyashsawarkar/javascript-decorators-explained-like-magic-but-real-4dda)
[18] [https://medium.com](https://medium.com/@jonathanndambuki16/what-is-an-angular-component-is-it-a-class-d2f31750cd9a)
[19] [https://realpython.com](https://realpython.com/inheritance-composition-python/)
[20] [https://coddy.tech](https://coddy.tech/learn/python/object_oriented_programming/method_resolution_order)
