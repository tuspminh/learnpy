Version:0.9 StartHTML:00000097 EndHTML:00119981 StartFragment:00000131 EndFragment:00119945 

# ABC Deep Dive - Buổi 4

# Virtual Subclass và `register()` \- Bí mật của `collections.abc`

Đây là một trong những tính năng **độc đáo nhất của ABC**.

Đa số lập trình viên Python chưa bao giờ sử dụng, nhưng thư viện chuẩn Python lại sử dụng rất nhiều.

Ví dụ:

  * `collections.abc`
  * `io`
  * `numbers`
  * `pathlib`



đều dựa trên cơ chế này.

* * *

# Mục tiêu

Sau buổi học bạn sẽ hiểu:

  * Virtual Subclass là gì 
  * `register()`
  * Vì sao không cần kế thừa vẫn là subclass 
  * `issubclass()`
  * `isinstance()`
  * Ưu điểm 
  * Nhược điểm 
  * Khi nào nên dùng 
  * Ứng dụng trong Plugin Architecture 



* * *

# 1\. Kế thừa thông thường

Ví dụ
    
    
    from abc import ABC
    
    class Animal(ABC):
        pass
    
    
    class Dog(Animal):
        pass

Ta có
    
    
    print(issubclass(Dog, Animal))
    
    
    True

và
    
    
    dog = Dog()
    
    print(isinstance(dog, Animal))
    
    
    True

Đây là kế thừa bình thường.

Sơ đồ:
    
    
    Animal
       ▲
       │
     Dog

* * *

# 2\. Nếu không kế thừa
    
    
    class Fish:
        pass
    
    
    print(issubclass(Fish, Animal))
    
    
    False

* * *

# 3\. Nhưng...

ABCMeta có một tính năng rất đặc biệt.

Ta có thể nói với Python rằng

> "Hãy coi Fish là Animal."

Mặc dù Fish không kế thừa Animal.

* * *

# 4\. register()

Ví dụ
    
    
    from abc import ABC
    
    
    class Animal(ABC):
        pass
    
    
    class Fish:
        pass
    
    
    Animal.register(Fish)

Bây giờ
    
    
    print(issubclass(Fish, Animal))
    
    
    True

Điều đáng ngạc nhiên là:
    
    
    fish = Fish()
    
    print(isinstance(fish, Animal))
    
    
    True

* * *

# 5\. Nhưng Fish có kế thừa không?

Kiểm tra
    
    
    print(Fish.__bases__)
    
    
    (<class 'object'>,)

Không hề có
    
    
    Animal

Kiểm tra tiếp
    
    
    print(Fish.mro())
    
    
    [
     Fish,
     object
    ]

Không có
    
    
    Animal

Điều này rất quan trọng.

`register()` **không thay đổi cây kế thừa (inheritance tree)**.

* * *

# 6\. Virtual Subclass là gì?

Ta gọi Fish là
    
    
    Virtual Subclass

Nghĩa là

> "Subclass trên danh nghĩa"

không phải subclass thật.

Sơ đồ
    
    
    Animal
    
    Fish

Không có mũi tên kế thừa.

Nhưng
    
    
    issubclass(Fish, Animal)

vẫn trả về
    
    
    True

* * *

# 7\. register() làm gì?

Nó không sửa class.

Nó chỉ lưu
    
    
    Fish

vào một registry nội bộ của `ABCMeta`.

Có thể hình dung:
    
    
    ABCMeta
    
    registered_classes = {
        Fish
    }

Sau này
    
    
    issubclass(Fish, Animal)

ABCMeta sẽ kiểm tra:
    
    
    Fish
    
    ↓
    
    Có trong registry?
    
    ↓
    
    Có
    
    ↓
    
    True

* * *

# 8\. Thử nhiều class
    
    
    class Dog:
        pass
    
    
    class Cat:
        pass
    
    
    Animal.register(Dog)
    Animal.register(Cat)
    
    
    print(issubclass(Dog, Animal))
    print(issubclass(Cat, Animal))
    
    
    True
    True

* * *

# 9\. register() không thêm method

Ví dụ
    
    
    from abc import ABC
    
    class Animal(ABC):
    
        def sleep(self):
            print("Sleeping")
    
    
    class Fish:
        pass
    
    Animal.register(Fish)
    
    
    fish = Fish()
    
    fish.sleep()

Kết quả
    
    
    AttributeError

Đây là điều rất nhiều người hiểu nhầm.

`register()` **không copy method**.

* * *

# 10\. register() không ép implement

Ví dụ
    
    
    from abc import ABC
    from abc import abstractmethod
    
    
    class Animal(ABC):
    
        @abstractmethod
        def speak(self):
            pass
    
    
    class Fish:
        pass
    
    
    Animal.register(Fish)
    
    
    fish = Fish()

Có lỗi không?

**Không.**

Fish vẫn tạo object bình thường.

* * *

Tại sao?

Bởi vì

Fish

không kế thừa

Animal.

Nó chỉ được đăng ký.

Cho nên
    
    
    abstractmethod

không có tác dụng.

* * *

# 11\. register() chỉ ảnh hưởng
    
    
    issubclass()
    
    isinstance()

Không ảnh hưởng
    
    
    MRO
    
    Inheritance
    
    super()
    
    method resolution

* * *

# 12\. Ví dụ trực quan
    
    
    from abc import ABC
    
    
    class Animal(ABC):
        pass
    
    
    class Fish:
        pass
    
    
    Animal.register(Fish)
    
    print(isinstance(Fish(), Animal))
    
    print(issubclass(Fish, Animal))
    
    print(Fish.__bases__)
    
    print(Fish.mro())

Kết quả
    
    
    True
    
    True
    
    (<class 'object'>,)
    
    [Fish, object]

Đây là ví dụ kinh điển.

* * *

# 13\. Vì sao cần register()?

Giả sử bạn viết framework.

Framework định nghĩa
    
    
    class Storage(ABC):
        pass

Người khác viết
    
    
    class MyStorage:
        ...

Họ không muốn sửa
    
    
    class MyStorage(Storage)

vì:

  * thư viện cũ 
  * package bên thứ ba 
  * không được phép chỉnh sửa 



Lúc này

Framework có thể làm
    
    
    Storage.register(MyStorage)

Thế là
    
    
    issubclass(MyStorage, Storage)
    
    
    True

* * *

# 14\. collections.abc dùng thế nào?

Ví dụ
    
    
    from collections.abc import Iterable
    
    print(isinstance([], Iterable))
    
    
    True

List được xem là Iterable.

Một số kiểu dữ liệu trong Python được công nhận là triển khai giao diện tương ứng thông qua cơ chế của `ABCMeta` (kết hợp kế thừa, đăng ký hoặc các hook nội bộ), giúp `isinstance` và `issubclass` hoạt động nhất quán.

* * *

# 15\. Ứng dụng vào Plugin

Đây chính là điều liên quan đến dự án crawler của bạn.

Framework
    
    
    class SourcePlugin(ABC):
        pass

Plugin cũ
    
    
    class OldPlugin:
        ...

Không muốn sửa.

Framework
    
    
    SourcePlugin.register(OldPlugin)

Thế là
    
    
    plugin = OldPlugin()
    
    isinstance(plugin, SourcePlugin)
    
    
    True

Framework có thể chấp nhận plugin này mà không buộc tác giả plugin thay đổi mã nguồn.

* * *

# 16\. Ưu điểm

✅ Không cần sửa source code

✅ Không cần kế thừa

✅ Không phá MRO

✅ Hỗ trợ backward compatibility

✅ Framework rất linh hoạt

* * *

# 17\. Nhược điểm

Đây cũng là lý do nhiều người không dùng.

Ví dụ
    
    
    class Bird:
        pass
    
    Animal.register(Bird)

Python sẽ tin rằng

Bird

là Animal.

Dù

Bird

không có
    
    
    speak()

Không có
    
    
    eat()

Không có gì cả.

Điều này có nghĩa:

**`register()` dựa trên sự tin tưởng**. Nó **không xác minh** rằng lớp được đăng ký thực sự đáp ứng "hợp đồng" của ABC.

* * *

# 18\. register() và Duck Typing

Thực ra

register()

là sự kết hợp của
    
    
    Duck Typing
    
    +
    
    ABC

Nó nói rằng

> "Tôi biết lớp này phù hợp."

ABCMeta sẽ tin bạn.

* * *

# 19\. Khi nào nên dùng?

Nên dùng khi:

  * Framework 
  * Plugin 
  * Adapter 
  * Legacy Code 
  * Third-party Library 
  * Không sửa được source 



Không nên dùng khi:

  * Bạn kiểm soát toàn bộ code. 
  * Có thể kế thừa trực tiếp. 
  * Muốn bắt buộc triển khai abstract method. 



Trong các trường hợp đó, kế thừa từ `ABC` thường rõ ràng và an toàn hơn.

* * *

# Tổng kết

Hôm nay chúng ta đã học:

  * `register()`
  * Virtual Subclass 
  * Registry của `ABCMeta`
  * `issubclass()`
  * `isinstance()`
  * Vì sao không thay đổi MRO 
  * Vì sao không ép implement abstract method 
  * Ứng dụng trong framework và plugin 



* * *

# Bài tập

## Bài 1

Viết
    
    
    class Vehicle(ABC)

và
    
    
    class Bicycle

Dùng
    
    
    Vehicle.register(Bicycle)

Kiểm tra
    
    
    issubclass()
    isinstance()

* * *

## Bài 2

In
    
    
    Bicycle.__bases__
    
    Bicycle.mro()

Quan sát rằng

Vehicle

không xuất hiện.

* * *

## Bài 3

Thêm
    
    
    @abstractmethod
    def move(self):
        ...

vào

Vehicle.

Đăng ký
    
    
    Vehicle.register(Bicycle)

Kiểm tra xem
    
    
    Bicycle()

có lỗi không.

Giải thích vì sao.

* * *

## Bài 4 (Áp dụng vào dự án crawler)

Thiết kế:
    
    
    class BaseSource(ABC):
        @abstractmethod
        def search(self, keyword):
            ...
    
        @abstractmethod
        def get_detail(self, url):
            ...

Sau đó tạo:
    
    
    class LegacySource:
        def search(self, keyword):
            ...
    
        def get_detail(self, url):
            ...

Đăng ký:
    
    
    BaseSource.register(LegacySource)

và kiểm tra:
    
    
    issubclass(LegacySource, BaseSource)
    isinstance(LegacySource(), BaseSource)

Điều này mô phỏng chính xác cách một framework có thể hỗ trợ các plugin cũ mà không yêu cầu tác giả plugin thay đổi cây kế thừa.

* * *

## Buổi 5 (rất thú vị)

Ở **Buổi 5** , chúng ta sẽ học **`__subclasshook__()`** — cơ chế còn mạnh hơn `register()`.

Với `__subclasshook__()`, bạn có thể khiến:
    
    
    issubclass(MyClass, MyABC)

trả về `True` **mà không cần** :

  * kế thừa `MyABC`, 
  * gọi `register()`, 
  * sửa mã nguồn của `MyClass`. 



Đây là nền tảng giúp nhiều ABC trong `collections.abc` hoạt động theo đúng tinh thần "duck typing" của Python, nhưng vẫn tận dụng được `isinstance()` và `issubclass()`.

