Dưới đây là ví dụ code chi tiết và cách phân biệt hai loại descriptor.
------------------------------
## 1. Ví dụ code cụ thể về Data Descriptor
Data descriptor thường dùng để kiểm tra tính hợp lệ của dữ liệu trước khi gán.

class NonNegative:
    """Một data descriptor chỉ cho phép gán số lớn hơn hoặc bằng 0."""
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        # Nếu truy cập từ Class (ví dụ: Product.price), trả về chính descriptor
        if instance is None:
            return self
        # Trả về giá trị lưu trong __dict__ của đối tượng
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        # Kiểm tra điều kiện dữ liệu
        if value < 0:
            raise ValueError(f"{self.name} không được âm!")
        # Lưu giá trị vào __dict__ của đối tượng để tránh lặp vô hạn
        instance.__dict__[self.name] = value

class Product:
    # Nhúng descriptor vào class
    price = NonNegative("price")

    def __init__(self, name, price):
        self.name = name
        self.price = price  # Kích hoạt __set__

## Cách hoạt động:

p = Product("Laptop", 1000)
print(p.price)  # Kích hoạt __get__ -> Kết quả: 1000

p.price = -500  # Kích hoạt __set__ -> ValueError: price không được âm!

------------------------------
## 2. Phân biệt Data và Non-Data Descriptor
Sự khác biệt cốt lõi nằm ở phương thức được định nghĩa và độ ưu tiên tra cứu (Lookup Order) của Python.
## Định nghĩa

* Data Descriptor: Định nghĩa cả __get__ và __set__ (hoặc __delete__).
* Non-Data Descriptor: Chỉ định nghĩa duy nhất __get__.

## Độ ưu tiên tra cứu (Lookup Order)
Khi bạn gọi obj.attribute, Python sẽ tìm kiếm theo thứ tự nghiêm ngặt sau:

   1. Data Descriptor (Nếu có class attribute trùng tên).
   2. Instance Dictionary (obj.__dict__).
   3. Non-Data Descriptor (Nếu có class attribute trùng tên).
   4. Class Dictionary (Class.__dict__).

## Ví dụ minh họa sự khác biệt:

class DataDescriptor:
    def __get__(self, instance, owner): return "Từ Data Descriptor"
    def __set__(self, instance, value): pass
class NonDataDescriptor:
    def __get__(self, instance, owner): return "Từ Non-Data Descriptor"
class MyClass:
    x = DataDescriptor()
    y = NonDataDescriptor()
obj = MyClass()
# Thao túng ghi đè trực tiếp vào __dict__ của đối tượng
obj.__dict__['x'] = "Giá trị trong dict"
obj.__dict__['y'] = "Giá trị trong dict"

print(obj.x)  # Kết quả: "Từ Data Descriptor" (Descriptor thắng dict)
print(obj.y)  # Kết quả: "Giá trị trong dict" (Dict thắng Descriptor)

------------------------------
Nếu bạn muốn, tôi có thể tiếp tục giải thích về:

* Cách Python dùng Non-Data Descriptor để biến hàm (function) thành phương thức (bound method).
* Cách tự viết lại decorator @property bằng Descriptor.

Bạn muốn đi sâu vào cơ chế bên trong của hàm hay tự làm decorator property?

