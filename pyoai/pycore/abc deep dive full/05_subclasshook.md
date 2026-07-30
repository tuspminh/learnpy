Version:0.9 StartHTML:00000097 EndHTML:00111206 StartFragment:00000131 EndFragment:00111170 

# ABC Deep Dive - Buổi 5

# `__subclasshook__()` \- Bí mật lớn nhất của ABCMeta

Đây là một trong những tính năng **nâng cao nhất** của `abc`.

Nếu `register()` là:

> "Tôi nói lớp này là subclass."

thì `__subclasshook__()` là:

> "Hãy tự động quyết định xem lớp này có phải subclass hay không."

Đây là cơ chế được sử dụng trong rất nhiều ABC của thư viện chuẩn như `collections.abc`.

* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * `__subclasshook__()`
  * Khi nào Python gọi nó 
  * Vì sao không cần `register()`
  * Vì sao không cần kế thừa 
  * Quan hệ với Duck Typing 
  * Cách `collections.abc` hoạt động 
  * Cách tự xây dựng Interface thông minh 



* * *

# 1\. Ôn lại `issubclass()`

Ví dụ:
    
    
    class Animal:
        pass
    
    
    class Dog(Animal):
        pass
    
    
    print(issubclass(Dog, Animal))

Kết quả:
    
    
    True

Thông thường Python kiểm tra cây kế thừa (MRO).

* * *

# 2\. Nhưng với ABC

Khi lớp có metaclass là `ABCMeta`, luồng xử lý của `issubclass()` được mở rộng:
    
    
    issubclass(Dog, Animal)
    
    ↓
    
    ABCMeta.__subclasscheck__()
    
    ↓
    
    1. Kiểm tra cache
    2. Kiểm tra kế thừa thật
    3. Kiểm tra register()
    4. Gọi __subclasshook__()

`__subclasshook__()` là "cơ hội cuối cùng" để ABC quyết định kết quả.

* * *

# 3\. `__subclasshook__()`

Ví dụ đơn giản:
    
    
    from abc import ABC
    
    
    class Animal(ABC):
    
        @classmethod
        def __subclasshook__(cls, C):
            return True

Bây giờ:
    
    
    class Car:
        pass
    
    
    print(issubclass(Car, Animal))

Kết quả:
    
    
    True

Car không hề kế thừa Animal.

Không hề register.

Nhưng vẫn là subclass.

* * *

# 4\. Hook nhận gì?
    
    
    @classmethod
    def __subclasshook__(cls, C):

Trong đó:

  * `cls` là chính lớp ABC (`Animal`) 
  * `C` là lớp đang được kiểm tra (`Car`) 



Ví dụ:
    
    
    print(cls)
    print(C)

Kết quả:
    
    
    <class '__main__.Animal'>
    
    <class '__main__.Car'>

* * *

# 5\. Hook trả về gì?

Có **3 khả năng**.

## True
    
    
    return True

Python kết luận:
    
    
    Đây là subclass.

* * *

## False
    
    
    return False

Python kết luận:
    
    
    Không phải subclass.

* * *

## NotImplemented
    
    
    return NotImplemented

Python quay lại cách kiểm tra thông thường:

  * kế thừa 
  * register() 
  * ... 



Đây là giá trị nên dùng khi hook không thể tự quyết định.

* * *

# 6\. Ví dụ thực tế

Giả sử Interface:
    
    
    class Flyable(ABC):
        ...

Ta không quan tâm đối tượng kế thừa ai.

Ta chỉ cần nó có:
    
    
    fly()

Viết:
    
    
    from abc import ABC
    
    
    class Flyable(ABC):
    
        @classmethod
        def __subclasshook__(cls, C):
    
            if any("fly" in B.__dict__ for B in C.__mro__):
                return True
    
            return NotImplemented

* * *

# 7\. Thử nghiệm
    
    
    class Bird:
    
        def fly(self):
            print("Flying")

Kiểm tra:
    
    
    print(issubclass(Bird, Flyable))

Kết quả:
    
    
    True

Bird không kế thừa.

Không register.

* * *

# 8\. Vì sao dùng `__mro__`?

Giả sử:
    
    
    class A:
    
        def fly(self):
            pass
    
    
    class Bird(A):
        pass

Nếu chỉ kiểm tra:
    
    
    Bird.__dict__

ta sẽ không thấy `fly`.

Nhưng:
    
    
    Bird.__mro__

là:
    
    
    Bird
    
    ↓
    
    A
    
    ↓
    
    object

Cho nên:
    
    
    for B in Bird.__mro__:

sẽ tìm thấy.

* * *

# 9\. `any()`

Đoạn này:
    
    
    any("fly" in B.__dict__ for B in C.__mro__)

nghĩa là:
    
    
    Có bất kỳ class nào trong MRO
    chứa fly không?

Ví dụ:
    
    
    Bird
    
    ↓
    
    Animal
    
    ↓
    
    FlyingAnimal
    
    ↓
    
    object

Nếu:
    
    
    FlyingAnimal.fly()

thì kết quả vẫn là:
    
    
    True

* * *

# 10\. Tại sao dùng `__dict__`?

Nhiều người sẽ viết:
    
    
    hasattr(C, "fly")

Điều này có thể cho kết quả đúng trong nhiều trường hợp, nhưng `__dict__` kết hợp với `__mro__` cho phép bạn **kiểm tra nơi phương thức được định nghĩa** và tránh một số trường hợp `hasattr` bị ảnh hưởng bởi cơ chế truy cập thuộc tính động.

Đây cũng là cách mà tài liệu Python thường minh họa khi viết `__subclasshook__()`.

* * *

# 11\. Interface thông minh

Ví dụ
    
    
    class JsonSerializable(ABC):
    
        @classmethod
        def __subclasshook__(cls, C):
    
            if any("to_json" in B.__dict__ for B in C.__mro__):
                return True
    
            return NotImplemented

Sau đó
    
    
    class User:
    
        def to_json(self):
            pass
    
    
    issubclass(User, JsonSerializable)
    
    
    True

* * *

# 12\. collections.abc hoạt động tương tự

Ví dụ:
    
    
    from collections.abc import Iterable

Bạn có thể thấy nhiều kiểu dữ liệu được xem là `Iterable` nếu chúng đáp ứng giao diện mong đợi (ví dụ có khả năng lặp), chứ không nhất thiết phải trực tiếp kế thừa `Iterable`.

Ý tưởng này rất gần với `__subclasshook__()`:

> Quan tâm **hành vi** hơn là cây kế thừa.

* * *

# 13\. register() vs hook()

register()
    
    
    Animal.register(Dog)

Nghĩa là
    
    
    Lập trình viên tự khai báo.

* * *

Hook
    
    
    __subclasshook__()

Nghĩa là
    
    
    Framework tự quyết định.

* * *

# 14\. Kết hợp cả hai

ABCMeta sẽ lần lượt xét:
    
    
    issubclass()
    
    ↓
    
    Cache
    
    ↓
    
    Inheritance
    
    ↓
    
    Register
    
    ↓
    
    Hook

Nếu hook trả:
    
    
    True

xong.

Nếu:
    
    
    False

xong.

Nếu:
    
    
    NotImplemented

Python tiếp tục theo quy trình mặc định nếu còn cần thiết.

* * *

# 15\. Ứng dụng vào dự án crawler

Bạn có:
    
    
    class BaseSource(ABC):

Muốn mọi plugin có:
    
    
    search()
    
    get_detail()
    
    get_chapters()

Ta có thể viết:
    
    
    from abc import ABC
    
    
    class BaseSource(ABC):
    
        @classmethod
        def __subclasshook__(cls, C):
    
            required = (
                "search",
                "get_detail",
                "get_chapters",
            )
    
            if all(
                any(name in B.__dict__ for B in C.__mro__)
                for name in required
            ):
                return True
    
            return NotImplemented

* * *

Sau đó
    
    
    class LegacyPlugin:
    
        def search(self):
            ...
    
        def get_detail(self):
            ...
    
        def get_chapters(self):
            ...
    
    
    print(issubclass(LegacyPlugin, BaseSource))
    
    
    True

Không cần:
    
    
    register()

Không cần:
    
    
    class LegacyPlugin(BaseSource)

Đây là cách rất phù hợp khi muốn tích hợp các plugin cũ mà vẫn giữ tinh thần "duck typing".

* * *

# 16\. Hạn chế

`__subclasshook__()` chỉ ảnh hưởng đến:
    
    
    issubclass()
    
    isinstance()

Nó **không** :

  * thêm phương thức, 
  * thay đổi MRO, 
  * khiến `super()` hoạt động, 
  * ép lớp phải cài đặt `@abstractmethod`. 



Nó chỉ thay đổi cách **ABCMeta đánh giá mối quan hệ kiểu**.

* * *

# 17\. `__subclasshook__()` không kiểm tra chất lượng

Ví dụ:
    
    
    class Fake:
    
        def fly(self):
            return 123

Hook:
    
    
    if "fly" in ...

sẽ vẫn:
    
    
    True

Cho nên hook chỉ kiểm tra:
    
    
    Có method

không kiểm tra:

  * đúng logic 
  * đúng signature 
  * đúng kiểu dữ liệu trả về 



Nếu cần kiểm tra những điều này, bạn nên kết hợp với kiểm thử, `typing.Protocol`, hoặc các công cụ kiểm tra kiểu như `mypy`.

* * *

# So sánh ba cơ chế

Cơ chế| Cần kế thừa| Cần register| Tự động| Thay đổi MRO  
---|---|---|---|---  
Kế thừa| ✅| ❌| ❌| ✅  
`register()`| ❌| ✅| ❌| ❌  
`__subclasshook__()`| ❌| ❌| ✅| ❌  
  
* * *

# Tổng kết

Hôm nay bạn đã học:

  * `__subclasshook__()`
  * Khi `ABCMeta` gọi hook 
  * Ba giá trị trả về: `True`, `False`, `NotImplemented`
  * Cách xây dựng một "interface thông minh" dựa trên hành vi 
  * Sự khác nhau giữa kế thừa, `register()` và `__subclasshook__()`
  * Cách áp dụng cơ chế này vào hệ thống plugin crawler truyện 



Đến đây, bạn đã nắm gần như toàn bộ các cơ chế cốt lõi của `abc`.

* * *

# Bài tập

### Bài 1

Viết `Serializable(ABC)`.

Nếu class có:
    
    
    to_dict()

thì:
    
    
    issubclass(...)

phải trả:
    
    
    True

* * *

### Bài 2

Viết `DatabaseDriver(ABC)`.

Yêu cầu:
    
    
    connect()
    
    close()
    
    execute()

Sử dụng `__subclasshook__()` để nhận diện các driver phù hợp.

* * *

### Bài 3

Viết `PaymentGateway(ABC)`.

Một lớp được coi là gateway nếu có:

  * `pay()`
  * `refund()`



Thử với các lớp:
    
    
    Stripe
    Paypal
    VNPay

mà không kế thừa `PaymentGateway`.

* * *

### Bài 4 (Áp dụng dự án crawler)

Viết `BaseSource` sao cho bất kỳ lớp nào có đầy đủ:

  * `search()`
  * `get_detail()`
  * `get_chapters()`
  * `download_chapter()`



đều được:
    
    
    issubclass(MyPlugin, BaseSource)

trả về `True` mà **không cần kế thừa** và **không cần`register()`**.

* * *

## Buổi 6

Ở **Buổi 6** , chúng ta sẽ chuyển sang một chủ đề cực kỳ quan trọng trong thiết kế framework:

> **Abstract Class + Concrete Method + Template Method Pattern**

Đây là cách mà rất nhiều framework lớn (Django, `pathlib`, `unittest`, `asyncio`, `io`,...) sử dụng: lớp cơ sở cung cấp **logic chung** , còn lớp con chỉ cần điền vào những "điểm mở rộng" (hook) thông qua các abstract method. Đây cũng là mô hình rất phù hợp để xây dựng hệ thống crawler nhiều nguồn của bạn.

