Version:0.9 StartHTML:00000097 EndHTML:00092009 StartFragment:00000131 EndFragment:00091973 

# ABC Deep Dive - Buổi 3

# ABCMeta Internals - Bên trong cơ chế hoạt động của ABC

Đến buổi này chúng ta bắt đầu đi vào **Python Internals**.

Đây là kiến thức mà đa số lập trình viên Python chưa từng đọc, nhưng nếu muốn thiết kế framework, plugin hoặc hiểu vì sao `ABC` hoạt động như vậy thì đây là phần rất quan trọng.

* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * ABCMeta hoạt động như thế nào 
  * Quá trình tạo class trong Python 
  * `__new__()`
  * `__init__()`
  * `__call__()`
  * Vì sao abstract class không tạo được object 
  * `__instancecheck__()`
  * `__subclasscheck__()`
  * `isinstance()` và `issubclass()` hoạt động ra sao 



* * *

# Phần 1. Mọi thứ trong Python đều là object

Ví dụ:
    
    
    class Dog:
        pass

Nhiều người nghĩ đây chỉ là định nghĩa một lớp.

Thực tế, Python thực hiện gần tương đương:
    
    
    Dog = type(
        "Dog",
        (),
        {}
    )

Ở đây:

  * `"Dog"`: tên lớp 
  * `()`: các lớp cha 
  * `{}`: namespace chứa thuộc tính và phương thức 



Nghĩa là:

> **Class cũng là một object.**

Kiểm tra:
    
    
    class Dog:
        pass
    
    print(type(Dog))

Kết quả:
    
    
    <class 'type'>

Điều này có nghĩa:

  * `Dog` là một object. 
  * Object `Dog` được tạo bởi `type`. 



* * *

# Phần 2. Metaclass là "class của class"

Ví dụ:
    
    
    class Cat:
        pass

Ta có:
    
    
    Cat instance
          ↑
        Cat class
          ↑
        type

Hay:
    
    
    meo = Cat()
    
    type(meo)
    ↓
    
    Cat
    
    type(Cat)
    ↓
    
    type

* * *

# Phần 3. ABCMeta thay thế type

Lớp thông thường:
    
    
    class Animal:
        pass

Metaclass:
    
    
    Animal
        ↓
    type

Nhưng:
    
    
    from abc import ABC
    
    class Animal(ABC):
        pass

thì:
    
    
    Animal
          ↓
    ABCMeta
          ↓
    type

Kiểm tra:
    
    
    from abc import ABC
    
    class Animal(ABC):
        pass
    
    print(type(Animal))

Kết quả:
    
    
    <class 'abc.ABCMeta'>

* * *

# Phần 4. ABC chỉ là helper

Trong thư viện chuẩn:
    
    
    from abc import ABC

gần tương đương với:
    
    
    class ABC(metaclass=ABCMeta):
        pass

Nghĩa là:
    
    
    ABC
    ↓
    
    ABCMeta

* * *

# Phần 5. Quá trình tạo object

Khi viết:
    
    
    dog = Dog()

Python **không** gọi `Dog.__init__()` ngay.

Thứ tự thực tế là:
    
    
    Dog()
    
    ↓
    
    Dog.__call__()
    
    ↓
    
    Dog.__new__()
    
    ↓
    
    Dog.__init__()

Điểm quan trọng là:

> **Việc gọi lớp (`Dog()`) thực chất là gọi phương thức `__call__` của metaclass.**

Với lớp thông thường, `__call__` là của `type`.

Với lớp ABC, `__call__` là của `ABCMeta`.

* * *

# Phần 6. Vai trò của `ABCMeta.__call__`

Đây chính là nơi Python kiểm tra abstract class.

Ta có:
    
    
    from abc import ABC, abstractmethod
    
    class Animal(ABC):
    
        @abstractmethod
        def speak(self):
            pass

Khi gọi:
    
    
    Animal()

Python đi theo luồng:
    
    
    Animal()
    
    ↓
    
    ABCMeta.__call__()
    
    ↓
    
    Kiểm tra __abstractmethods__
    
    ↓
    
    Có abstract?
    
    ↓
    
    Có
    
    ↓
    
    TypeError

Do đó, lỗi xảy ra **trước khi** `__new__()` hay `__init__()` được thực thi.

* * *

# Phần 7. `__abstractmethods__`

Xem trực tiếp:
    
    
    from abc import ABC, abstractmethod
    
    class Animal(ABC):
    
        @abstractmethod
        def speak(self):
            pass
    
    print(Animal.__abstractmethods__)

Kết quả:
    
    
    frozenset({'speak'})

Nếu:
    
    
    class Dog(Animal):
    
        def speak(self):
            print("Woof")

thì:
    
    
    print(Dog.__abstractmethods__)

Kết quả:
    
    
    frozenset()

Đây là lý do:
    
    
    Dog()

được phép.

* * *

# Phần 8. `__new__()` và `__init__()`

Ví dụ:
    
    
    class Dog:
    
        def __new__(cls):
            print("__new__")
            return super().__new__(cls)
    
        def __init__(self):
            print("__init__")
    
    Dog()

Kết quả:
    
    
    __new__
    __init__

Thứ tự luôn là:
    
    
    __call__
    
    ↓
    
    __new__
    
    ↓
    
    __init__

* * *

# Phần 9. Chứng minh `ABCMeta` chặn trước `__new__`
    
    
    from abc import ABC, abstractmethod
    
    class Animal(ABC):
    
        def __new__(cls):
            print("__new__")
            return super().__new__(cls)
    
        def __init__(self):
            print("__init__")
    
        @abstractmethod
        def speak(self):
            pass
    
    Animal()

Kết quả:
    
    
    TypeError

Không có:
    
    
    __new__

Không có:
    
    
    __init__

Nghĩa là `ABCMeta` đã dừng quá trình trước khi tạo đối tượng.

* * *

# Phần 10. `isinstance()`

Ví dụ:
    
    
    class Animal:
        pass
    
    class Dog(Animal):
        pass
    
    dog = Dog()
    
    print(isinstance(dog, Animal))

Kết quả:
    
    
    True

Nhiều người nghĩ:
    
    
    isinstance()

là hàm đặc biệt.

Thực tế:
    
    
    isinstance()
    
    ↓
    
    Animal.__instancecheck__()

Nếu lớp dùng metaclass `type`, thì `type.__instancecheck__()` xử lý.

Nếu dùng `ABCMeta`, thì `ABCMeta.__instancecheck__()` có thể bổ sung logic riêng (ví dụ hỗ trợ virtual subclass).

* * *

# Phần 11. `issubclass()`

Ví dụ:
    
    
    class Animal:
        pass
    
    class Dog(Animal):
        pass
    
    print(issubclass(Dog, Animal))

Thực chất:
    
    
    issubclass()
    
    ↓
    
    Animal.__subclasscheck__()

Với ABC, `ABCMeta.__subclasscheck__()` còn xét thêm các lớp đã được đăng ký bằng `register()` hoặc do `__subclasshook__()` quyết định.

* * *

# Phần 12. Toàn bộ quá trình

Ví dụ:
    
    
    dog = Dog()

Sơ đồ:
    
    
    Dog()
    
    ↓
    
    ABCMeta.__call__()
    
    ↓
    
    Kiểm tra __abstractmethods__
    
    ↓
    
    Không còn abstract?
    
    ↓
    
    Dog.__new__()
    
    ↓
    
    Dog.__init__()
    
    ↓
    
    Trả object

Nếu còn abstract:
    
    
    Dog()
    
    ↓
    
    ABCMeta.__call__()
    
    ↓
    
    Có abstract
    
    ↓
    
    TypeError
    
    ↓
    
    Kết thúc

* * *

# Phần 13. Vì sao `__abstractmethods__` là `frozenset`?

Thay vì:
    
    
    set(...)

Python dùng:
    
    
    frozenset(...)

Lý do:

  * Không thể sửa đổi ngoài ý muốn. 
  * Có thể dùng làm khóa trong từ điển hoặc cache. 
  * Giảm nguy cơ thay đổi trạng thái của lớp sau khi đã tạo. 



Ví dụ:
    
    
    print(type(Animal.__abstractmethods__))

Kết quả:
    
    
    <class 'frozenset'>

* * *

# Phần 14. ABCMeta không kiểm tra chữ ký (signature)

ABC chỉ kiểm tra **tên phương thức** đã được cài đặt hay chưa.

Ví dụ:
    
    
    from abc import ABC, abstractmethod
    
    class Animal(ABC):
    
        @abstractmethod
        def speak(self, volume):
            pass
    
    
    class Dog(Animal):
    
        def speak(self):   # Thiếu tham số
            print("Woof")

`Dog()` **vẫn tạo được** , vì `ABCMeta` chỉ thấy rằng phương thức `speak` đã tồn tại. Sai khác về tham số chỉ bộc lộ khi gọi:
    
    
    dog = Dog()
    dog.speak(5)

sẽ gây:
    
    
    TypeError: speak() takes 1 positional argument but 2 were given

Đây là một hạn chế của ABC và là một trong những lý do `typing.Protocol` kết hợp với các trình kiểm tra kiểu (như `mypy`) trở nên hữu ích trong các dự án lớn.

* * *

# Tổng kết

Hôm nay chúng ta đã đi sâu vào internals của `ABCMeta`:

  * Class trong Python cũng là object. 
  * `type` là metaclass mặc định. 
  * `ABCMeta` thay thế `type` để thêm cơ chế kiểm tra abstract. 
  * Khi gọi `Dog()`, Python đi qua `ABCMeta.__call__()` trước. 
  * `ABCMeta.__call__()` kiểm tra `__abstractmethods__` và chặn việc tạo đối tượng nếu còn phương thức abstract. 
  * `isinstance()` và `issubclass()` hoạt động thông qua `__instancecheck__()` và `__subclasscheck__()` của metaclass. 
  * `ABCMeta` chỉ kiểm tra sự tồn tại của phương thức, **không kiểm tra chữ ký**. 



* * *

# Bài tập

  1. Tạo lớp `Shape(ABC)` với hai abstract method và in `Shape.__abstractmethods__`. 
  2. Tạo `Rectangle` chỉ cài đặt một phương thức, quan sát `Rectangle.__abstractmethods__`. 
  3. Thêm `__new__()` và `__init__()` vào `Shape`, thử khởi tạo `Shape()` để xác nhận rằng hai phương thức này không được gọi. 
  4. Tạo `Circle` cài đặt đầy đủ các abstract method, sau đó in:
         
         print(type(Circle))
         print(Circle.__abstractmethods__)

  5. Thử thay đổi chữ ký (signature) của một abstract method trong lớp con và quan sát rằng `ABCMeta` vẫn cho phép khởi tạo, nhưng lỗi chỉ xuất hiện khi gọi phương thức. 



* * *

## Buổi 4 (rất quan trọng)

Ở **Buổi 4** , chúng ta sẽ học **Virtual Subclass** và `register()`.

Đây là một cơ chế đặc biệt của `ABCMeta` cho phép:
    
    
    issubclass(MyClass, MyABC) == True

**mà không cần kế thừa** `MyABC`.

Đây là kỹ thuật được sử dụng rộng rãi trong `collections.abc`, `io`, `pathlib` và nhiều framework lớn để hỗ trợ các lớp bên ngoài mà không ép chúng phải thay đổi cây kế thừa.

