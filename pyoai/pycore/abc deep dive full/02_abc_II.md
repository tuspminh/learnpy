Version:0.9 StartHTML:00000097 EndHTML:00112873 StartFragment:00000131 EndFragment:00112837 

# ABC Deep Dive - Buổi 2

# Module `abc` từ A-Z

Ở buổi trước chúng ta đã hiểu:

  * Duck Typing 
  * Interface 
  * Vì sao ABC ra đời 



Hôm nay chúng ta sẽ đi vào **module`abc`**.

Đây là một module rất nhỏ (chỉ vài trăm dòng code) nhưng lại được sử dụng trong hầu hết thư viện chuẩn Python.

Ví dụ:
    
    
    collections.abc
    numbers
    io
    asyncio
    typing
    pathlib
    importlib
    concurrent.futures

Tất cả đều xây dựng trên nền tảng ABC.

* * *

# Mục tiêu buổi học

Sau buổi này bạn sẽ hiểu:

  * abc module là gì 
  * ABCMeta 
  * ABC 
  * abstractmethod 
  * abstractproperty 
  * abstractclassmethod 
  * abstractstaticmethod 
  * Vì sao Python vẫn cho phép viết code trong abstract method 
  * Cơ chế đánh dấu abstract method 



* * *

# 1\. Module abc

Import
    
    
    import abc

hoặc
    
    
    from abc import ABC
    from abc import ABCMeta
    from abc import abstractmethod

Đây là 3 thành phần được dùng nhiều nhất.

* * *

# 2\. ABC là gì?

Thực tế:
    
    
    from abc import ABC

chỉ là cách viết tắt của
    
    
    class ABC(metaclass=ABCMeta):
        pass

Nghĩa là
    
    
    ABC
         ↓
    ABCMeta
         ↓
    type

Hay nói cách khác
    
    
    ABC
       chỉ là helper class

Còn **ABCMeta mới là nhân vật chính**.

* * *

# Ví dụ
    
    
    from abc import ABC
    
    
    class Animal(ABC):
        pass

tương đương
    
    
    from abc import ABCMeta
    
    
    class Animal(metaclass=ABCMeta):
        pass

Hai cách hoàn toàn giống nhau.

Thông thường nên dùng `ABC` vì ngắn gọn và dễ đọc.

* * *

# 3\. ABCMeta là gì?

Trong Python

mọi class đều được tạo bởi metaclass.

Ví dụ
    
    
    class Dog:
        pass

thực tế Python làm
    
    
    Dog = type(
        "Dog",
        (),
        {}
    )

Ở đây
    
    
    type

chính là metaclass.

* * *

ABC cũng vậy.

Chỉ khác
    
    
    Dog
    
    ↓
    
    type

còn
    
    
    Animal
    
    ↓
    
    ABCMeta
    
    ↓
    
    type

* * *

# 4\. Kiểm tra metaclass
    
    
    from abc import ABC
    
    
    class Animal(ABC):
        pass
    
    
    print(type(Animal))

Kết quả
    
    
    <class 'abc.ABCMeta'>

Trong khi
    
    
    class Dog:
        pass
    
    
    print(type(Dog))

cho
    
    
    <class 'type'>

* * *

# 5\. abstractmethod

Đây là decorator quan trọng nhất.

Ví dụ
    
    
    from abc import ABC
    from abc import abstractmethod
    
    
    class Animal(ABC):
    
        @abstractmethod
        def speak(self):
            pass

Lúc này
    
    
    Animal

không thể tạo object.
    
    
    Animal()

Lỗi
    
    
    TypeError:
    Can't instantiate abstract class Animal

* * *

# 6\. Class con
    
    
    class Dog(Animal):
    
        def speak(self):
            print("Woof")

Bây giờ
    
    
    Dog()

được phép.

* * *

# 7\. Nếu quên implement
    
    
    class Cat(Animal):
        pass

thì
    
    
    Cat()

Lỗi
    
    
    TypeError

* * *

# 8\. Một abstract class có nhiều abstract method
    
    
    from abc import ABC
    from abc import abstractmethod
    
    
    class Animal(ABC):
    
        @abstractmethod
        def speak(self):
            pass
    
        @abstractmethod
        def run(self):
            pass

Subclass
    
    
    class Dog(Animal):
    
        def speak(self):
            print("Woof")

sẽ vẫn lỗi
    
    
    run()

chưa implement.

Phải đủ
    
    
    class Dog(Animal):
    
        def speak(self):
            print("Woof")
    
        def run(self):
            print("Running")

* * *

# 9\. Abstract method vẫn có body

Điều này rất nhiều người mới học ngạc nhiên.

Ví dụ
    
    
    class Animal(ABC):
    
        @abstractmethod
        def speak(self):
            print("Animal speaking...")

Điều này hợp lệ.

* * *

Subclass
    
    
    class Dog(Animal):
    
        def speak(self):
            super().speak()
            print("Woof")

Kết quả
    
    
    Animal speaking...
    
    Woof

* * *

Đây là khác biệt lớn với Java.

Trong Java
    
    
    abstract method

không có body.

Trong Python

được phép.

Điều này rất hữu ích trong **Template Method Pattern** , nơi lớp cơ sở cung cấp một phần logic dùng chung.

* * *

# 10\. Abstract class cũng có method bình thường
    
    
    class Animal(ABC):
    
        @abstractmethod
        def speak(self):
            pass
    
        def sleep(self):
            print("Sleeping")

Subclass
    
    
    class Dog(Animal):
    
        def speak(self):
            print("Woof")

Sử dụng
    
    
    dog = Dog()
    
    dog.sleep()
    
    
    Sleeping

* * *

# 11\. Abstract Property

Python có decorator
    
    
    @property

Có thể kết hợp
    
    
    @abstractmethod

Ví dụ
    
    
    from abc import ABC
    from abc import abstractmethod
    
    
    class Animal(ABC):
    
        @property
        @abstractmethod
        def name(self):
            pass

Subclass
    
    
    class Dog(Animal):
    
        @property
        def name(self):
            return "Dog"

* * *

Lưu ý thứ tự decorator rất quan trọng:
    
    
    @property
    @abstractmethod

Không phải ngược lại.

* * *

# 12\. abstractproperty

Ngày xưa

Python có
    
    
    from abc import abstractproperty

Ví dụ
    
    
    @abstractproperty
    def name(self):
        ...

Hiện nay **đã bị deprecate**.

Nên dùng
    
    
    @property
    @abstractmethod

* * *

# 13\. abstractclassmethod

Ví dụ
    
    
    from abc import ABC
    from abc import abstractmethod
    
    
    class Animal(ABC):
    
        @classmethod
        @abstractmethod
        def create(cls):
            pass

Subclass
    
    
    class Dog(Animal):
    
        @classmethod
        def create(cls):
            return cls()

* * *

Tương tự,

`abstractclassmethod` cũ cũng đã bị deprecate.

Nên dùng
    
    
    @classmethod
    @abstractmethod

* * *

# 14\. abstractstaticmethod
    
    
    class Animal(ABC):
    
        @staticmethod
        @abstractmethod
        def info():
            pass

Subclass
    
    
    class Dog(Animal):
    
        @staticmethod
        def info():
            print("Dog")

* * *

`abstractstaticmethod`

cũng đã bị deprecate.

* * *

# 15\. Vì sao decorator phải theo đúng thứ tự?

Ví dụ đúng
    
    
    @property
    @abstractmethod
    def name(self):
        ...

Thứ tự thực thi decorator là từ dưới lên:

  1. `@abstractmethod` đánh dấu hàm bằng thuộc tính `__isabstractmethod__ = True`. 
  2. `@property` tạo đối tượng `property` từ hàm đã được đánh dấu. 



Khi `ABCMeta` quét lớp, nó thấy property này chứa getter có cờ `__isabstractmethod__`, nên coi đó là abstract property.

Nếu đảo ngược:
    
    
    @abstractmethod
    @property
    def name(self):
        ...

thì `@abstractmethod` sẽ cố gắng đánh dấu trực tiếp đối tượng `property`. Điều này không hoạt động như mong muốn và trên các phiên bản Python hiện đại thường dẫn đến lỗi hoặc không được hỗ trợ.

Quy tắc tương tự áp dụng cho `@classmethod` và `@staticmethod`: đặt `@abstractmethod` ở **trong cùng** (gần định nghĩa hàm nhất).

* * *

# 16\. ABCMeta phát hiện abstract method như thế nào?

Thử xem:
    
    
    from abc import abstractmethod
    
    
    def f():
        pass
    
    
    print(hasattr(f, "__isabstractmethod__"))
    
    
    False

Sau khi dùng decorator:
    
    
    from abc import abstractmethod
    
    
    @abstractmethod
    def f():
        pass
    
    
    print(f.__isabstractmethod__)
    
    
    True

Thực chất `@abstractmethod` chỉ đánh dấu đối tượng hàm bằng thuộc tính `__isabstractmethod__ = True`. Khi tạo lớp, `ABCMeta` sẽ quét các thuộc tính và thu thập tất cả các phương thức có cờ này vào tập `__abstractmethods__`.

* * *

# 17\. Thuộc tính `__abstractmethods__`

Ví dụ:
    
    
    from abc import ABC, abstractmethod
    
    
    class Animal(ABC):
    
        @abstractmethod
        def speak(self):
            pass
    
        @abstractmethod
        def run(self):
            pass
    
    
    print(Animal.__abstractmethods__)

Kết quả:
    
    
    frozenset({'run', 'speak'})

Khi `Dog` cài đặt đầy đủ cả hai phương thức, `Dog.__abstractmethods__` sẽ là:
    
    
    frozenset()

Đó là lý do `Dog()` có thể được khởi tạo.

* * *

# 18\. Tổng kết

Trong buổi học này, bạn đã nắm được:

  * `ABC` chỉ là lớp tiện ích; **`ABCMeta` mới là metaclass thực hiện toàn bộ cơ chế abstract**. 
  * `@abstractmethod` đánh dấu phương thức bằng `__isabstractmethod__`. 
  * `ABCMeta` thu thập các phương thức abstract vào `__abstractmethods__`. 
  * Một abstract method **có thể có phần thân (body)** và được gọi qua `super()`. 
  * Các decorator `abstractproperty`, `abstractclassmethod`, `abstractstaticmethod` là API cũ và đã được thay thế bằng cách kết hợp `@property`, `@classmethod`, `@staticmethod` với `@abstractmethod`. 
  * Thứ tự decorator là: 
    * `@property` → `@abstractmethod`
    * `@classmethod` → `@abstractmethod`
    * `@staticmethod` → `@abstractmethod`



* * *

# Bài tập

  1. Tạo lớp `Shape(ABC)` với ba abstract method: 
     * `area()`
     * `perimeter()`
     * `draw()`
  2. Cài đặt hai lớp `Rectangle` và `Circle` kế thừa `Shape`. 
  3. Thêm một abstract property `name` vào `Shape` và triển khai ở các lớp con. 
  4. In ra:
         
         print(Shape.__abstractmethods__)
         print(Rectangle.__abstractmethods__)

rồi giải thích vì sao kết quả khác nhau.

  5. Trong dự án crawler truyện của bạn, thiết kế một lớp:
         
         class BaseSource(ABC):
             ...

với:

     * abstract property: `site_name`
     * abstract classmethod: `create()`
     * abstract staticmethod: `validate_url(url)`
     * abstract method: `search()`, `get_detail()`, `get_chapters()`, `download_chapter()`

Đây sẽ là nền tảng rất tốt để chuẩn hóa các plugin như `TruyenFull`, `TangThuVien`, `Wattpad`,...




Ở **Buổi 3** , chúng ta sẽ đi sâu vào **`ABCMeta` internals**: cách metaclass chặn việc khởi tạo đối tượng, vai trò của `__call__`, `__new__`, `__instancecheck__`, `__subclasscheck__`, và cách Python quyết định một lớp có còn là abstract hay không. Đây là phần giúp bạn hiểu cơ chế hoạt động của ABC ở mức gần với mã nguồn CPython.

