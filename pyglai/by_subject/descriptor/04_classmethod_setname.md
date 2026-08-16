Dưới đây là cách hoạt động nâng cao của descriptor thông qua việc tự chế @classmethod, @staticmethod và cách tối ưu hóa code bằng __set_name__.
------------------------------
## 1. Tự viết lại @classmethod và @staticmethod
Cả hai decorator này đều là Non-Data Descriptor. Nhiệm vụ của chúng là thay đổi đối số đầu tiên được truyền vào hàm khi bạn gọi nó.
## Code giả lập @classmethod và @staticmethod:

class BảnSaoClassMethod:
    """Descriptor giả lập @classmethod: Luôn truyền 'cls' vào đối số đầu tiên."""
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        # owner chính là Class chứa descriptor này
        # Trả về một hàm mới đã được nạp sẵn class (owner) vào vị trí của 'cls'
        def wrapper(*args, **kwargs):
            return self.func(owner, *args, **kwargs)
        return wrapper

class BảnSaoStaticMethod:
    """Descriptor giả lập @staticmethod: Không truyền 'self' hay 'cls' gì cả."""
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        # Trả về chính hàm gốc ban đầu, giống hệt một hàm tự do ngoài class
        return self.func

## Cách sử dụng:

class MayTinh:
    @BảnSaoClassMethod
    def thong_tin(cls):
        return f"Đây là class {cls.__name__}"

    @BảnSaoStaticMethod
    def cong(a, b):
        return a + b
# Kiểm tra
print(MayTinh.thong_tin())  # Kết quả: Đây là class MayTinh
print(MayTinh.cong(5, 10))  # Kết quả: 15

------------------------------
## 2. Mẹo rút gọn code với phương thức đặc biệt __set_name__
Trong các ví dụ trước, khi tạo descriptor, chúng ta phải truyền thủ công tên biến vào hàm khởi tạo, ví dụ: price = NonNegative("price"). Điều này rất dễ gây lỗi nếu tên biến bên trái và chuỗi bên phải không khớp nhau.
Từ Python 3.6, bạn có thể dùng __set_name__. Phương thức này sẽ tự động kích hoạt ngay khi class được khởi tạo để truyền chính xác tên biến vào descriptor.
## Code tối ưu hóa với __set_name__:

class AutoNameDescriptor:
    """Descriptor tự động nhận diện tên thuộc tính được gán."""
    def __set_name__(self, owner, name):
        # owner: Class chứa descriptor (ví dụ: User)
        # name: Tên biến được gán ở bên trái dấu "=" (ví dụ: "email")
        self.name = name
        print(f"Đã tự động nhận diện tên biến: {self.name}")

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value

class User:
    # Không cần truyền chuỗi vào __init__ nữa!
    email = AutoNameDescriptor()
    username = AutoNameDescriptor()
# Khi chạy file, Python tự động in ra:# > Đã tự động nhận diện tên biến: email# > Đã tự động nhận diện tên biến: username

------------------------------
Đến đây, bạn đã nắm trọn vẹn từ cơ bản đến những kỹ thuật nâng cao nhất của Python Descriptor bao gồm: Giao thức __get__/__set__, độ ưu tiên tra cứu, cơ chế bound method, cách tự viết các decorator hệ thống (@property, @classmethod), và tối ưu bằng __set_name__.
Nếu bạn muốn, chúng ta có thể:

* Thực hành giải quyết một bài toán thực tế cụ thể sử dụng descriptor (ví dụ: Viết một thư viện ORM mini để map dữ liệu xuống database).
* Hoặc chuyển sang tìm hiểu các khái niệm nâng cao liên quan khác của Python như Metaclass hoặc MRO (Method Resolution Order).

Bạn muốn làm bài tập thực tế hay chuyển sang khám phá chủ đề nâng cao mới?

