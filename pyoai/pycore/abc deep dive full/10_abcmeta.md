# ABC Deep Dive - Buổi 10

# ABCMeta Deep Dive - Bên trong `abc`

Chào mừng bạn đến với **buổi quan trọng nhất** của khóa học ABC.

Cho đến nay, chúng ta đã **sử dụng** `ABC`, `@abstractmethod`, `register()`, `__subclasshook__()`, Generic, Property,...

Hôm nay chúng ta sẽ trả lời câu hỏi:

> **Python đã làm điều đó bằng cách nào?**

Đây là kiến thức giúp bạn đọc được source code của CPython và hiểu cách nhiều framework hoạt động.

* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * `type`
  * Metaclass 
  * `ABCMeta`
  * Quá trình Python tạo class 
  * `__new__()` của metaclass 
  * `__call__()`
  * `__abstractmethods__`
  * `__isabstractmethod__`
  * `update_abstractmethods()`
  * Cách tự viết một metaclass đơn giản 



* * *

# 1\. Mọi thứ trong Python đều là object

Ví dụ:
    
    
    class Dog:
        pass

Hỏi:
    
    
    type(Dog)

Kết quả:
    
    
    <class 'type'>

Điều này có nghĩa:
    
    
    Dog
    
    ↓
    
    object
    
    ↓
    
    được tạo bởi
    
    ↓
    
    type

Sơ đồ:
    
    
              type
                │
                ▼
            tạo class
                │
                ▼
              Dog
                │
                ▼
            tạo object
                │
                ▼
            dog = Dog()

* * *

# 2\. Class cũng là object

Ví dụ
    
    
    class Cat:
        pass

Bạn có thể:
    
    
    print(type(Cat))
    
    
    print(id(Cat))
    
    
    print(Cat.__dict__)
    
    
    print(dir(Cat))

Tất cả đều hợp lệ vì class là object.

* * *

# 3\. `type` tạo class

Khi viết
    
    
    class Dog:
        pass

Python thực chất làm gần giống:
    
    
    Dog = type(
        "Dog",
        (),
        {},
    )

Trong đó
    
    
    Tên lớp
    
    ↓
    
    Danh sách lớp cha
    
    ↓
    
    Namespace (__dict__)

Ví dụ:
    
    
    Dog = type(
        "Dog",
        (),
        {
            "x": 10
        }
    )
    
    print(Dog.x)

Kết quả
    
    
    10

* * *

# 4\. Metaclass

Metaclass là:
    
    
    Class của Class

Hay:
    
    
    Object
    
    ↓
    
    Class
    
    ↓
    
    Metaclass

Thông thường:
    
    
    type

là metaclass mặc định.

* * *

# 5\. `ABCMeta`

Nếu viết
    
    
    from abc import ABC
    
    class Animal(ABC):
        pass

thì:
    
    
    print(type(Animal))

Kết quả:
    
    
    <class 'abc.ABCMeta'>

Không còn là:
    
    
    type

mà là:
    
    
    ABCMeta

* * *

# 6\. Quan hệ kế thừa
    
    
    ABCMeta
    
    ↓
    
    type

Có nghĩa:
    
    
    issubclass(ABCMeta, type)

Kết quả
    
    
    True

`ABCMeta` chỉ là một metaclass đặc biệt được xây dựng trên `type`.

* * *

# 7\. Khi tạo class

Ví dụ:
    
    
    class Animal(ABC):
    
        @abstractmethod
        def speak(self):
            ...

Python không chỉ tạo class.

Nó còn:

  * tìm abstract method 
  * lưu metadata 
  * chuẩn bị kiểm tra khi khởi tạo object 



Ai làm việc đó?
    
    
    ABCMeta

* * *

# 8\. `__new__()` của Metaclass

Quá trình tạo class:
    
    
    class Animal
    
    ↓
    
    ABCMeta.__new__()
    
    ↓
    
    Class được tạo

Không phải:
    
    
    Animal.__new__()

Đây là điểm rất nhiều người nhầm.

* * *

# 9\. `__abstractmethods__`

Ví dụ
    
    
    from abc import ABC
    from abc import abstractmethod
    
    
    class Animal(ABC):
    
        @abstractmethod
        def speak(self):
            ...
    
        @abstractmethod
        def walk(self):
            ...

Kiểm tra
    
    
    print(Animal.__abstractmethods__)

Kết quả
    
    
    frozenset({
        "speak",
        "walk",
    })

Đây là tập hợp mà `ABCMeta` tự xây dựng.

* * *

# 10\. Tại sao dùng `frozenset`?

Không phải:
    
    
    set

mà:
    
    
    frozenset

Lý do:

  * immutable 
  * hashable 
  * tránh bị sửa ngoài ý muốn 
  * tối ưu cache 



* * *

# 11\. `__isabstractmethod__`

Một abstract method thực chất chỉ là:
    
    
    function

được gắn thêm:
    
    
    __isabstractmethod__ = True

Ví dụ
    
    
    class Animal(ABC):
    
        @abstractmethod
        def speak(self):
            ...

Kiểm tra
    
    
    print(
        Animal.speak.__isabstractmethod__
    )

Kết quả
    
    
    True

* * *

# 12\. Decorator làm gì?

`@abstractmethod`

gần giống:
    
    
    def abstractmethod(func):
    
        func.__isabstractmethod__ = True
    
        return func

Thực tế source code phức tạp hơn một chút, nhưng ý tưởng chính là như vậy.

* * *

# 13\. ABCMeta tìm abstract method

Giả sử
    
    
    class Animal(ABC):
    
        @abstractmethod
        def a(self):
            ...
    
        def b(self):
            ...
    
        @abstractmethod
        def c(self):
            ...

ABCMeta duyệt namespace:
    
    
    a
    
    ↓
    
    b
    
    ↓
    
    c

Nếu:
    
    
    obj.__isabstractmethod__

là:
    
    
    True

thì thêm vào:
    
    
    __abstractmethods__

* * *

# 14\. Tại sao không tạo được object?

Ví dụ
    
    
    class Dog(Animal):
        pass

Khi:
    
    
    Dog()

Python kiểm tra:
    
    
    Dog.__abstractmethods__

Nếu khác:
    
    
    frozenset()

thì:
    
    
    TypeError

* * *

# 15\. Nếu implement đủ
    
    
    class Dog(Animal):
    
        def speak(self):
            ...
    
        def walk(self):
            ...

Kiểm tra:
    
    
    print(Dog.__abstractmethods__)

Kết quả
    
    
    frozenset()

Lúc này:
    
    
    Dog()

được phép.

* * *

# 16\. `update_abstractmethods()`

Python có hàm:
    
    
    from abc import update_abstractmethods

Ví dụ:
    
    
    class Animal(ABC):
    
        @abstractmethod
        def speak(self):
            ...

Sau đó:
    
    
    Animal.speak = lambda self: print("Hi")

Thông tin trong `__abstractmethods__` chưa tự cập nhật.

Gọi:
    
    
    update_abstractmethods(Animal)

để Python tính toán lại tập abstract methods.

Trong thực tế, bạn hiếm khi cần dùng hàm này, nhưng nó hữu ích nếu framework của bạn **thay đổi class động**.

* * *

# 17\. Viết Metaclass đơn giản

Ví dụ:
    
    
    class MyMeta(type):
    
        def __new__(cls, name, bases, namespace):
    
            print(f"Creating {name}")
    
            return super().__new__(
                cls,
                name,
                bases,
                namespace,
            )

Sử dụng
    
    
    class Dog(
        metaclass=MyMeta
    ):
        pass

Kết quả
    
    
    Creating Dog

Metaclass đã can thiệp vào quá trình tạo lớp.

* * *

# 18\. Metaclass kiểm tra quy tắc

Ví dụ:
    
    
    class InterfaceMeta(type):
    
        def __new__(
            cls,
            name,
            bases,
            namespace,
        ):
    
            if "run" not in namespace:
                raise TypeError(
                    "Missing run()"
                )
    
            return super().__new__(
                cls,
                name,
                bases,
                namespace,
            )

Thử:
    
    
    class Task(
        metaclass=InterfaceMeta
    ):
        pass

Kết quả:
    
    
    TypeError

Đây chính là ý tưởng mà nhiều framework sử dụng để áp đặt quy ước.

* * *

# 19\. So sánh `type` và `ABCMeta`

`type`| `ABCMeta`  
---|---  
Tạo class| Tạo abstract class  
Không quan tâm abstract method| Quản lý abstract method  
Không có `register()`| Có `register()`  
Không có `__subclasshook__()`| Hỗ trợ `__subclasshook__()`  
Không tạo `__abstractmethods__`| Tự xây dựng `__abstractmethods__`  
  
* * *

# 20\. Áp dụng vào dự án crawler

Giả sử:
    
    
    class BaseSource(ABC):
    
        @abstractmethod
        def search(self):
            ...
    
        @abstractmethod
        def get_detail(self):
            ...

Khi Python import plugin:
    
    
    class TruyenFull(
        BaseSource
    ):
        ...

`ABCMeta` sẽ ngay lập tức xác định:

  * Plugin còn thiếu phương thức nào? 
  * Có thể khởi tạo hay chưa? 
  * `__abstractmethods__` có rỗng không? 



Nhờ đó, lỗi được phát hiện **ngay khi bạn cố gắng tạo instance** , thay vì đến lúc chương trình chạy sâu mới gặp.

* * *

# 21\. Một góc nhìn tổng thể

Sơ đồ hoạt động:
    
    
    @abstractmethod
            │
            ▼
    __isabstractmethod__ = True
            │
            ▼
    ABCMeta.__new__()
            │
            ▼
    Thu thập __abstractmethods__
            │
            ▼
    Lưu vào frozenset
            │
            ▼
    Khi gọi Class()
            │
            ▼
    Kiểm tra __abstractmethods__
            │
            ▼
    Rỗng? ───► Có → Cho phép tạo object
       │
       └── Không → TypeError

* * *

# Tổng kết

Trong buổi này bạn đã học:

  * `type`
  * Metaclass 
  * `ABCMeta`
  * `__new__()` của metaclass 
  * `__abstractmethods__`
  * `__isabstractmethod__`
  * `frozenset`
  * `update_abstractmethods()`
  * Tự viết metaclass đơn giản 
  * Cách `ABCMeta` hoạt động bên trong 



Đến đây, bạn đã hiểu phần lớn cơ chế cốt lõi của module `abc`.

* * *

# Bài tập

## Bài 1

Viết một metaclass:
    
    
    class PrintMeta(type):
        ...

Mỗi khi tạo class, in ra:
    
    
    Creating class: <Tên lớp>

* * *

## Bài 2

Viết metaclass:
    
    
    RequireRunMeta(type)

Yêu cầu mọi class sử dụng metaclass này phải định nghĩa phương thức:
    
    
    run()

Nếu thiếu, ném `TypeError`.

* * *

## Bài 3

Tạo một abstract class có:

  * 3 abstract method 
  * 2 concrete method 



Sau đó:

  * In `__abstractmethods__`
  * In `__isabstractmethod__` của từng phương thức 
  * Hoàn thành lớp con và kiểm tra `__abstractmethods__` sau khi implement đầy đủ. 



* * *

## Bài 4 (Áp dụng dự án crawler)

Hãy thiết kế một `PluginMeta` (kế thừa `ABCMeta`) có thể kiểm tra khi tạo lớp:

  * Plugin phải có thuộc tính `plugin_name`. 
  * Plugin phải có `plugin_version`. 
  * Plugin phải triển khai các abstract method của `BaseSource`. 



Gợi ý: Trong `__new__()`, bạn có thể kiểm tra `namespace` đối với lớp plugin cụ thể trước khi gọi `super().__new__()`. Tuy nhiên, hãy cẩn thận để không áp dụng quy tắc này lên chính `BaseSource` (lớp cơ sở), nếu không bạn sẽ không thể định nghĩa nó.

* * *

# Buổi 11

Ở **Buổi 11** , chúng ta sẽ bước vào phần nâng cao nhất của khóa học:

> **Xây dựng một mini-framework plugin hoàn chỉnh bằng`ABC`**

Chúng ta sẽ kết hợp tất cả kiến thức đã học:

  * `ABC`
  * `ABCMeta`
  * `Generic`
  * `Template Method`
  * `Mixins`
  * `__subclasshook__()`
  * `register()`
  * `typing`



để xây dựng một hệ thống plugin có kiến trúc gần với các framework Python chuyên nghiệp như Scrapy hoặc pytest.

